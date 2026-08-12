"""The deleted route's constraint-catalog assembler, kept as a test fixture builder.

**This is not the product's catalog.** The shipped catalog is assembled by the projector
(`elaboration/project.py`, `_build_constraint_catalog`) directly from the elaborated
`InstanceGraph`, and `generation/` reads it off `graph.constraint_catalog`. The function
below was the *legacy* route's assembler; its only call site was
`orchestration/pipeline_builder.py`, deleted by the Item 7 retirement (`19072ad`). It moved
out of `src/` in Revise step 6d so the product surface carries one catalog authority.

Three unit modules — `test_constraint_emission.py`, `test_catalog_usage_tier.py`,
`test_cli_generation.py` — use it to build a `ConstraintCatalog` from a hand-written
`ConcreteConstraint` list without standing up an `InstanceGraph`. That is what it is now: a
fixture builder. Read nothing here as a statement about shipped behaviour.

**The two assemblers do not agree, and the difference is recorded, not reconciled.** This
one derives `source_records` from `facts.definitions` — every `ConstraintDefinition` in the
model, visible even when zero of its usages are eligible. The projector derives them from
the constraints it actually projected, so a definition with no eligible entry produces no
source record. Exclusion records differ the same way (`c.exclusion` here; eligibility-derived
in the projector). Whether the shipped catalog should carry the total-inventory guarantee is
an open product question with no recorded authority — surfaced in the Revise step 6d stage
note, not answered here.
"""

from __future__ import annotations

import hashlib
import json
from typing import TYPE_CHECKING, Any

from sysml_codegen.resolution.models import (
    ConstraintCatalog,
    ConstraintCatalogEntry,
    ConstraintCatalogExcludedRecord,
    ConstraintCatalogSourceRecord,
    ConstraintCatalogUsageRecord,
)

if TYPE_CHECKING:
    from agentic_mbse.sysml.constraint_facts import ConstraintFacts

    from sysml_codegen.resolution.models import ConcreteConstraint

__all__ = ["assemble_constraint_catalog"]


def _canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def assemble_constraint_catalog(
    concrete: list[ConcreteConstraint], facts: ConstraintFacts
) -> ConstraintCatalog:
    """Build the catalog from eligible concrete entries + source definitions.

    **No shipped route calls this.** Its call site was ``pipeline_builder.py``, deleted by
    the Item 7 retirement; on the exact route projection assembles the catalog itself
    (``elaboration/project.py:_build_constraint_catalog``) and sets it on the graph. What
    keeps the function in the tree is its unit coverage: ``tests/unit/test_constraint_emission.py``,
    ``test_catalog_usage_tier.py`` and ``test_cli_generation.py`` build catalogs through it
    to pin the same eligibility, ordering and fingerprint rules the projector implements.
    Whether that second assembler earns its place, or the tests should read the projector's,
    is an open disposition (Revise step 6c, rule-10 surfacing).

    The guarantees below are the ones both assemblers keep. Callers pass ``concrete``
    non-empty, i.e. exactly when the constraint pathway is active and
    ``extend_graph_with_constraints`` also runs — so the aggregator's ``CATALOG_FINGERPRINT``
    always has a catalog to read, even with zero eligible entries (D11: a model whose
    assertions are all unassessed still gets a ``not_assessed`` report surface, needing
    the fingerprint but no ``concrete_entries``). A model with zero constraint facts at all
    yields no catalog — ``graph.constraint_catalog`` stays ``None``, preserving
    INV-7. Ordering follows ``concrete`` (already sorted by ``constraint_id``, Item 5 /
    INV-4), so the fingerprint is deterministic across repeated live loads with identical
    input (INV-8).
    """
    validated_concrete = [
        type(item).model_validate(item.model_dump(mode="python")) for item in concrete
    ]
    eligible = [c for c in validated_concrete if c.eligible]
    source_records = [
        ConstraintCatalogSourceRecord(
            definition_qualified_name=d.identity.qualified_name or "<anonymous>",
            formal_names=[f.name for f in d.formals if f.name],
        )
        for d in facts.definitions
    ]
    concrete_entries = []
    for c in eligible:
        missing_fields = [
            field_name
            for field_name in (
                "is_negated",
                "expected_value",
                "predicate_ir",
                "evaluation_channel",
            )
            if getattr(c, field_name) is None
        ]
        if missing_fields:  # enforced by ConcreteConstraint; guards mutated models
            raise RuntimeError(
                f"eligible constraint {c.constraint_id!r} has missing executable fields: "
                + ", ".join(missing_fields)
            )
        assert c.is_negated is not None
        assert c.expected_value is not None
        assert c.predicate_ir is not None
        assert c.evaluation_channel is not None
        concrete_entries.append(
            ConstraintCatalogEntry(
                constraint_id=c.constraint_id,
                usage_qualified_name=c.usage_qualified_name,
                source_local_identity=c.source_local_identity,
                source_form=c.source_form,
                owner_qualified_name=c.owner_qualified_name,
                definition_qualified_name=c.definition_qualified_name,
                owner_instance_path=c.owner_instance_path,
                membership_kind=c.membership_kind,
                predicate_source_key=c.predicate_source_key,
                is_negated=c.is_negated,
                expected_value=c.expected_value,
                predicate_ir=c.predicate_ir,
                evaluation_channel=c.evaluation_channel,
            )
        )
    usage_records = _assemble_usage_records(eligible)
    excluded_records = [
        ConstraintCatalogExcludedRecord(
            constraint_id=c.constraint_id,
            usage_qualified_name=c.usage_qualified_name,
            source_form=c.source_form,
            membership_kind=c.membership_kind,
            exclusion=c.exclusion,
        )
        for c in sorted(validated_concrete, key=lambda item: item.constraint_id)
        if not c.eligible and c.exclusion is not None
    ]
    payload = {
        "source_records": [r.model_dump(mode="json") for r in source_records],
        "usage_records": [r.model_dump(mode="json") for r in usage_records],
        "concrete_entries": [e.model_dump(mode="json") for e in concrete_entries],
        "excluded_records": [r.model_dump(mode="json") for r in excluded_records],
    }
    fingerprint = hashlib.sha256(_canonical_json(payload).encode()).hexdigest()
    return ConstraintCatalog(
        source_records=source_records,
        usage_records=usage_records,
        concrete_entries=concrete_entries,
        excluded_records=excluded_records,
        fingerprint=fingerprint,
    )


def _assemble_usage_records(
    eligible: list[ConcreteConstraint],
) -> list[ConstraintCatalogUsageRecord]:
    """One admitted-usage row per distinct ``(usage_qualified_name, source_local_identity)``.

    Deduplicated across the usage's concrete occurrences (Item 8, INV-2). The identity key
    folds in ``source_local_identity`` so two distinct *anonymous* eligible usages (both
    ``usage_qualified_name == "<anonymous>"``) yield two rows, never one (F2). Ordering follows
    first appearance in ``eligible`` (already ``constraint_id``-sorted upstream), so the tier is
    deterministic. Usage-tier identity fields are invariant across occurrences (B2), so the
    first occurrence's values are authoritative.
    """
    records: dict[tuple[str, str], ConstraintCatalogUsageRecord] = {}
    for c in eligible:
        key = (c.usage_qualified_name, c.source_local_identity)
        if key in records:
            continue
        assert c.is_negated is not None and c.expected_value is not None  # eligible-guarded
        records[key] = ConstraintCatalogUsageRecord(
            usage_qualified_name=c.usage_qualified_name,
            source_local_identity=c.source_local_identity,
            source_form=c.source_form,
            owner_kind=c.owner_kind,
            owner_qualified_name=c.owner_qualified_name,
            definition_qualified_name=c.definition_qualified_name,
            membership_kind=c.membership_kind,
            is_negated=c.is_negated,
            expected_value=c.expected_value,
        )
    return list(records.values())
