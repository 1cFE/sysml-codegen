"""Pure, license-free constraint drop report (PIPELINE-TRUTH Item 4).

The constraint drop report has two halves that must not share a syside
dependency:

* **collect** (live, on the extractor) sweeps the model for ``ConstraintUsage``
  and its subtypes and produces a typed :class:`ConstraintManifestEntry` list.
* **render** (here, pure) turns that manifest into log lines.

Keeping render syside-free lets the ``generate --from-snapshot`` path replay the
exact same report from a deserialized manifest, with no license. Both paths call
the one :func:`render_constraint_report`, so render identity is by construction
(INV-B guards the serialize/deserialize step between them).

The manifest holds the *whole* swept subtree, including the requirement-side
usages that are not dropped (``REQUIREMENT`` / ``SATISFY``), tagged by kind
(INV-C). Render derives the droppable set from the kind, so the scanned /
reported / excluded breakdown reproduces offline and an excluded ``satisfy``
stays observable rather than silent.
"""

from __future__ import annotations

import logging
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


# Owner token -> diagnostic wording. Render owns display strings (D8); the
# serialized token is the enum value, decoupled from this wording.
_OWNER_DISPLAY = {
    OwnerKind.CALC_DEF: "calc def",
    OwnerKind.PART_DEF: "part def",
    OwnerKind.PART_USAGE: "part usage",
    OwnerKind.ELEMENT: "element",
    OwnerKind.MODEL: "model",
}


def render_constraint_report(
    manifest: list[ConstraintManifestEntry], logger: logging.Logger
) -> None:
    """Render the constraint drop report from a manifest (pure, no syside).

    Emits, in order:

    1. One always-present sentinel INFO with the scanned / reported / excluded
       breakdown — so an empty result is distinguishable from a blind query and
       an excluded ``satisfy`` is observable (row-1 zero-found sentinel).
    2. One INFO per dropped predicate, naming its owner.
    3. One summary WARN, only if at least one predicate was dropped.

    Called identically on the live and from-snapshot paths (INV-B). The caller
    passes the ``sysml_codegen.extraction.extractor`` logger so byte output and
    caplog filtering match across paths.
    """
    droppable = [e for e in manifest if e.constraint_kind in DROPPABLE_KINDS]
    scanned = len(manifest)
    reported = len(droppable)
    asserts = sum(1 for e in droppable if e.constraint_kind is ConstraintKind.ASSERT)
    plains = sum(1 for e in droppable if e.constraint_kind is ConstraintKind.PLAIN)
    excluded = scanned - reported

    logger.info(
        "Constraint drop report: scanned %d ConstraintUsage (incl. subtypes), "
        "reported %d droppable (%d assert, %d require/plain), excluded %d "
        "requirement/satisfy.",
        scanned,
        reported,
        asserts,
        plains,
        excluded,
    )

    for entry in droppable:
        logger.info(
            "Constraint '%s' on %s '%s' is not executable and was dropped "
            "(constraints are not compiled to pipeline modules; see "
            "modeling-assumptions.md).",
            entry.constraint_name or "<anonymous>",
            _OWNER_DISPLAY[entry.owner_kind],
            entry.owner_name or "<unknown>",
        )

    if reported:
        logger.warning(
            "Dropped %d constraint usage(s) across the model; constraint "
            "predicates are not executable and do not appear in generated "
            "output. See the 'Constraints are not executable' section of "
            "modeling-assumptions.md.",
            reported,
        )


def manifest_to_records(manifest: list[ConstraintManifestEntry]) -> list[dict]:
    """Serialize a manifest to JSON-safe records with stable enum tokens (D8).

    The kind/owner enums serialize by their fixed token (``.value``), decoupled
    from render's display wording, so a diagnostic reword never changes snapshot
    bytes. Order is preserved (INV-G).
    """
    return [
        {
            "owner_kind": e.owner_kind.value,
            "owner_name": e.owner_name,
            "owner_qualified_name": e.owner_qualified_name,
            "constraint_name": e.constraint_name,
            "constraint_kind": e.constraint_kind.value,
            "source_line": e.source_line,
        }
        for e in manifest
    ]


def manifest_from_records(records: list[dict]) -> list[ConstraintManifestEntry]:
    """Rebuild a manifest from serialized records (stable tokens -> enums)."""
    return [
        ConstraintManifestEntry(
            owner_kind=OwnerKind(r["owner_kind"]),
            owner_name=r["owner_name"],
            owner_qualified_name=r["owner_qualified_name"],
            constraint_name=r["constraint_name"],
            constraint_kind=ConstraintKind(r["constraint_kind"]),
            source_line=r["source_line"],
        )
        for r in records
    ]
