"""Concrete constraint lowering (Item 5).

Expands each extracted ``assert constraint`` into concrete graph structure: one
:class:`~sysml_codegen.resolution.models.ConcreteConstraint` per concrete owner
instance, every formal strictly resolved to a real producer channel, a real
design attribute, or an overridable modeled default — never synthesized. See
``.project/active/constraint-lowering/design.md`` for the full design.
"""

from __future__ import annotations

import hashlib
import json

from sysml_codegen.orchestration.pipeline_context import CodeGenerationError
from sysml_codegen.resolution.models import (
    ConcreteConstraint,
    ConcreteConstraintInput,
    ConstraintInputResolution,
)


def mint_constraint_id(*, instance_path: str, source_local: str, tuple_: tuple) -> str:
    """Mint a deterministic, collision-checkable ``constraint_id`` (D3/N1).

    ``{instance_path}__{source_local}__{sha256[:16] of the canonical tuple}``.
    The prefix is human-scannable; the suffix folds source-local identity,
    owner-instance identity, membership kind, and polarity into a 64-bit
    collision-visible fingerprint (a hard duplicate is a generation error,
    checked post-expansion by :func:`assert_unique_constraint_ids`).
    """
    canonical = json.dumps(list(tuple_), sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    suffix = hashlib.sha256(canonical.encode()).hexdigest()[:16]
    return f"{instance_path}__{source_local}__{suffix}"


def assert_unique_constraint_ids(concrete: list[ConcreteConstraint]) -> None:
    """Raise if any two concrete constraints share a ``constraint_id`` (D3, INV-4).

    A collision under a 64-bit hash on a valid model means something upstream is
    broken (e.g. two owner instances sharing an identity) — never silently kept.
    """
    seen: dict[str, ConcreteConstraint] = {}
    for c in concrete:
        prior = seen.get(c.constraint_id)
        if prior is not None:
            raise CodeGenerationError(
                f"constraint_id collision: '{c.constraint_id}' minted for both "
                f"'{prior.owner_instance_path}' and '{c.owner_instance_path}' "
                "(generation error, never silently kept — D3/INV-4)"
            )
        seen[c.constraint_id] = c


__all__ = [
    "ConcreteConstraint",
    "ConcreteConstraintInput",
    "ConstraintInputResolution",
    "assert_unique_constraint_ids",
    "mint_constraint_id",
]
