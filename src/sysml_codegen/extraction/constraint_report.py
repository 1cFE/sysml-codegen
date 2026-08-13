"""Constraint usage sweep + kind classification (PIPELINE-TRUTH Item 4; Item 14 W2).

``collect_constraint_manifest`` (on the extractor) sweeps the model for
``ConstraintUsage`` and its subtypes and produces a typed
:class:`ConstraintManifestEntry` list — the manifest side of the manifest->catalog
no-silent-drop mapping. The test that proved that mapping retired with the legacy
stack; CONSTRAINT-SEMANTICS Item 2 re-anchors the proof. The report/render/
snapshot-replay half this manifest used to feed (the drop-manifest era: a blanket
not-executable warning) retired with Item 14 — the catalog is now the single source
of truth for what happens to a constraint usage, so this module keeps only the sweep
and its kind vocabulary, both load-bearing for the mapping.

The manifest holds the *whole* swept subtree, including the requirement-side usages
that are not dropped (``REQUIREMENT`` / ``SATISFY``), tagged by kind (INV-C) — the
mapping's justified carrier-free category.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ConstraintKind(str, Enum):
    """What a swept ``ConstraintUsage`` is, finest-grained for the report.

    ``ASSERT`` and ``PLAIN`` are dropped executable predicates (see
    :data:`DROPPABLE_KINDS`); ``REQUIREMENT`` and ``SATISFY`` are requirement-side
    and excluded. ``require``/``assume`` constraints fold into ``PLAIN`` — they
    are plain ``ConstraintUsage``s and the require/assume flag lives on the
    membership, not a distinct usage type (a documented v2 limitation).
    """

    ASSERT = "assert"  # assert constraint -> AssertConstraintUsage
    PLAIN = "plain"  # constraint / require constraint -> ConstraintUsage
    REQUIREMENT = "requirement"  # RequirementUsage (excluded)
    SATISFY = "satisfy"  # satisfy requirement -> SatisfyRequirementUsage (excluded)


class OwnerKind(str, Enum):
    """The kind of element that owns a constraint, for the diagnostic wording."""

    CALC_DEF = "calc_def"
    PART_DEF = "part_def"
    PART_USAGE = "part_usage"
    ELEMENT = "element"
    MODEL = "model"


# The kinds that count as dropped executable predicates. Requirement-side kinds
# (REQUIREMENT, SATISFY) are excluded — the mirror of the adapter's
# EXCLUDED_CONSTRAINT_TYPES policy, pinned equal to is_droppable_constraint by
# the INV-D cross-repo consistency test.
DROPPABLE_KINDS = frozenset({ConstraintKind.ASSERT, ConstraintKind.PLAIN})


@dataclass(frozen=True)
class ConstraintManifestEntry:
    """One swept ``ConstraintUsage`` (subtypes included), tagged by kind.

    Frozen so the manifest is a stable record set; serialized by stable enum
    tokens (D8) so a diagnostic reword never changes snapshot bytes.
    """

    owner_kind: OwnerKind
    owner_name: str
    owner_qualified_name: str
    constraint_name: str
    constraint_kind: ConstraintKind
    source_line: int
