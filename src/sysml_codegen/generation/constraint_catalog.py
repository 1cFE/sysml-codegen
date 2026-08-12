"""ConstraintCatalog assembly + the same-IR generation guard (Item 7 / D6, INV-2).

Assembly runs once, early. On the exact route projection builds the catalog and sets it on the
graph it mints (`elaboration/project.py:266`, `_build_constraint_catalog`) — every seam that
needs catalog data reads `graph.constraint_catalog`, never `ctx` (Appendix A: "generation reads
only the graph"). The same-IR guard re-reads the catalog at generation time (`assert_same_ir`,
called from the module-wrapper seam before the single per-definition compile), so a
post-assembly mutation of a catalog entry is caught where it matters — at the point the shared
predicate is about to be compiled — not baked into a stale assembly-time check.
"""

from __future__ import annotations

import hashlib
import json
from typing import TYPE_CHECKING, Any

from agentic_mbse.sysml.expression_ir import parse_expression, serialize_expression

from sysml_codegen.resolution.models import (
    ConstraintCatalog,
    ConstraintCatalogEntry,
    ConstraintCatalogExcludedRecord,
    ConstraintCatalogSourceRecord,
    ConstraintCatalogUsageRecord,
)

if TYPE_CHECKING:
    from agentic_mbse.sysml.constraint_facts import ConstraintFacts

    from sysml_codegen.core.errors import CodeGenerationError
    from sysml_codegen.resolution.models import ConcreteConstraint

__all__ = [
    "assemble_constraint_catalog",
    "assert_same_ir",
    "predicate_definition_key",
]


def _generation_error(message: str) -> CodeGenerationError:
    from sysml_codegen.core.errors import CodeGenerationError

    return CodeGenerationError(message)


def predicate_definition_key(entry: ConcreteConstraint | ConstraintCatalogEntry) -> str:
    """Return the true positive-predicate source identity used for compile-once grouping."""
    if entry.predicate_source_key is None:
        raise _generation_error(f"constraint {entry.constraint_id!r} has no predicate_source_key")
    return entry.predicate_source_key


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


def assert_same_ir(entries: list[ConstraintCatalogEntry]) -> None:
    """INV-2, two arms, both run before the single per-definition compile.

    (a) Round-trip stability per entry: ``serialize(parse(entry.predicate_ir)) ==
    entry.predicate_ir`` (B3) — a serializer-noise divergence trips here.
    (b) Byte-agreement: every entry sharing ``predicate_definition_key`` carries the
    identical ``predicate_ir`` string — a real post-lowering mutation trips here.

    Both arms raise a loud ``CodeGenerationError`` naming the offending ``constraint_id``,
    never a silent skip or a stale-cached compile.
    """
    for entry in entries:
        if entry.predicate_ir is None:
            raise _generation_error(
                f"same-IR violation (INV-2) for '{entry.constraint_id}': eligible catalog "
                "entry has no predicate_ir"
            )
        if serialize_expression(parse_expression(entry.predicate_ir)) != entry.predicate_ir:
            raise _generation_error(
                f"same-IR violation (INV-2 arm a) for '{entry.constraint_id}': predicate_ir "
                "does not round-trip stably through parse_expression/serialize_expression"
            )

    by_definition: dict[str, tuple[str, str]] = {}
    for entry in entries:
        key = predicate_definition_key(entry)
        prior = by_definition.get(key)
        assert entry.predicate_ir is not None  # guarded by arm (a) above
        if prior is not None and prior[1] != entry.predicate_ir:
            raise _generation_error(
                f"same-IR violation (INV-2 arm b) for '{entry.constraint_id}': predicate_ir "
                f"diverges from '{prior[0]}', another concrete entry sharing definition "
                f"'{key}'"
            )
        by_definition[key] = (entry.constraint_id, entry.predicate_ir)
