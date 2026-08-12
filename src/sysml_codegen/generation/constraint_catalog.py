"""The same-IR generation guard and the compile-once grouping key (Item 7 / D6, INV-2).

**One catalog authority.** The projector assembles the catalog and sets it on the graph it
mints (`elaboration/project.py`, `_build_constraint_catalog`); every seam that needs catalog
data reads `graph.constraint_catalog`, never `ctx` (Appendix A: "generation reads only the
graph"). This module no longer assembles anything. The legacy route's assembler lived here
until Revise step 6d and now sits in `tests/helpers/retired_catalog_assembly.py`, where it
reads as the fixture builder it had become rather than as a second authority.

The same-IR guard re-reads the catalog at generation time (`assert_same_ir`, called from the
module-wrapper seam before the single per-definition compile), so a post-assembly mutation of
a catalog entry is caught where it matters — at the point the shared predicate is about to be
compiled — not baked into a stale assembly-time check.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from agentic_mbse.sysml.expression_ir import parse_expression, serialize_expression

if TYPE_CHECKING:
    from sysml_codegen.core.errors import CodeGenerationError
    from sysml_codegen.resolution.models import ConcreteConstraint, ConstraintCatalogEntry

__all__ = [
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
