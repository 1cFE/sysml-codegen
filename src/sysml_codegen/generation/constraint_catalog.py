"""ConstraintCatalog assembly + the same-IR generation guard (Item 7 / D6, INV-2).

Assembly runs once, early (`orchestration/pipeline_builder.py`, right after
`extend_graph_with_constraints`) and sets the result on the graph — every seam that needs
catalog data reads `graph.constraint_catalog`, never `ctx` (Appendix A: "generation reads only
the graph"). The same-IR guard re-reads the catalog at generation time (`assert_same_ir`,
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
    ConstraintCatalogSourceRecord,
)

if TYPE_CHECKING:
    from agentic_mbse.sysml.constraint_facts import ConstraintFacts

    from sysml_codegen.orchestration.pipeline_context import CodeGenerationError
    from sysml_codegen.resolution.models import ConcreteConstraint

__all__ = [
    "assemble_constraint_catalog",
    "assert_same_ir",
    "predicate_definition_key",
]


def _generation_error(message: str) -> CodeGenerationError:
    from sysml_codegen.orchestration.pipeline_context import CodeGenerationError

    return CodeGenerationError(message)


def predicate_definition_key(entry: ConcreteConstraint | ConstraintCatalogEntry) -> str:
    """The compile-once grouping key (D3): the source assertion's identity.

    Every concrete entry expanded from one ``ConstraintUsageFact`` shares this — one
    ``part_def`` owner with N occurrences mints N distinct ``constraint_id``s but keeps one
    ``usage_qualified_name``, which is exactly the "one definition" D3's compile-once emission
    keys on.
    """
    return entry.usage_qualified_name


def _canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def assemble_constraint_catalog(
    concrete: list[ConcreteConstraint], facts: ConstraintFacts
) -> ConstraintCatalog:
    """Build the catalog from eligible concrete entries + source definitions.

    Called only when ``concrete`` is non-empty (the ``pipeline_builder.py`` call site guards
    on it), i.e. exactly when the constraint pathway is active and
    ``extend_graph_with_constraints`` also runs — so the aggregator's ``CATALOG_FINGERPRINT``
    always has a catalog to read, even with zero eligible entries (D11: a model whose
    assertions are all unassessed still gets a ``not_assessed`` report surface, needing
    the fingerprint but no ``concrete_entries``). A model with zero constraint facts at all
    never reaches this function — ``graph.constraint_catalog`` stays ``None``, preserving
    INV-7. Ordering follows ``concrete`` (already sorted by ``constraint_id``, Item 5 /
    INV-4), so the fingerprint is deterministic across repeated live loads with identical
    input (INV-8).
    """
    eligible = [c for c in concrete if c.eligible]
    source_records = [
        ConstraintCatalogSourceRecord(
            definition_qualified_name=d.identity.qualified_name or "<anonymous>",
            formal_names=[f.name for f in d.formals if f.name],
        )
        for d in facts.definitions
    ]
    concrete_entries = []
    for c in eligible:
        if c.evaluation_channel is None:  # enforced by ConcreteConstraint's validator
            raise RuntimeError(
                f"eligible constraint {c.constraint_id!r} has no evaluation_channel"
            )
        concrete_entries.append(
            ConstraintCatalogEntry(
                constraint_id=c.constraint_id,
                usage_qualified_name=c.usage_qualified_name,
                owner_instance_path=c.owner_instance_path,
                membership_kind=c.membership_kind,
                is_negated=c.is_negated,
                expected_value=c.expected_value,
                predicate_ir=c.predicate_ir,
                evaluation_channel=c.evaluation_channel,
            )
        )
    payload = {
        "source_records": [r.model_dump(mode="json") for r in source_records],
        "concrete_entries": [e.model_dump(mode="json") for e in concrete_entries],
    }
    fingerprint = hashlib.sha256(_canonical_json(payload).encode()).hexdigest()
    return ConstraintCatalog(
        source_records=source_records,
        concrete_entries=concrete_entries,
        fingerprint=fingerprint,
    )


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
