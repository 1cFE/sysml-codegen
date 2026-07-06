"""Unit tests for the pure constraint-drop render (PIPELINE-TRUTH Item 4).

License-free: render operates on a typed manifest with no syside dependency, so
these run in CI without a license and pin the render contract directly (the same
function both the live and from-snapshot paths call — INV-B).
"""

from __future__ import annotations

import logging

from sysml_codegen.extraction.constraint_report import (
    ConstraintKind,
    ConstraintManifestEntry,
    OwnerKind,
    render_constraint_report,
)

_LOGGER_NAME = "sysml_codegen.extraction.extractor"


def _entry(kind: ConstraintKind, name: str, owner: OwnerKind = OwnerKind.PART_DEF):
    return ConstraintManifestEntry(
        owner_kind=owner,
        owner_name="Owner",
        owner_qualified_name="Pkg::Owner",
        constraint_name=name,
        constraint_kind=kind,
        source_line=1,
    )


def _records(caplog):
    return caplog.records


def test_empty_manifest_emits_zero_sentinel_and_stays_silent(caplog):
    # silent-on-clean (R1): no droppable predicates -> the sentinel reports all
    # zeros, and there is NO summary WARN and NO per-constraint INFO.
    with caplog.at_level(logging.INFO, logger=_LOGGER_NAME):
        render_constraint_report([], logging.getLogger(_LOGGER_NAME))

    infos = [r for r in _records(caplog) if r.levelno == logging.INFO]
    warns = [r for r in _records(caplog) if r.levelno == logging.WARNING]
    assert len(infos) == 1, "only the sentinel INFO is emitted on an empty manifest"
    assert not warns, "no summary WARN when nothing is droppable"
    msg = infos[0].getMessage()
    assert "scanned 0" in msg
    assert "reported 0" in msg
    assert "excluded 0" in msg


def test_mixed_manifest_breakdown_and_warn(caplog):
    # fires-on-shape: 1 assert + 1 plain droppable; 1 requirement + 1 satisfy
    # excluded. Sentinel: scanned 4, reported 2 (1 assert, 1 require/plain),
    # excluded 2. One WARN, two per-droppable INFO lines.
    manifest = [
        _entry(ConstraintKind.ASSERT, "a"),
        _entry(ConstraintKind.PLAIN, "p"),
        _entry(ConstraintKind.REQUIREMENT, "r"),
        _entry(ConstraintKind.SATISFY, "s"),
    ]
    with caplog.at_level(logging.INFO, logger=_LOGGER_NAME):
        render_constraint_report(manifest, logging.getLogger(_LOGGER_NAME))

    sentinels = [r for r in _records(caplog) if "scanned" in r.getMessage()]
    drop_infos = [
        r for r in _records(caplog)
        if r.levelno == logging.INFO and "is not executable" in r.getMessage()
    ]
    warns = [r for r in _records(caplog) if r.levelno == logging.WARNING]

    assert len(sentinels) == 1
    smsg = sentinels[0].getMessage()
    assert "scanned 4" in smsg
    assert "reported 2" in smsg
    assert "1 assert" in smsg
    assert "1 require/plain" in smsg
    assert "excluded 2" in smsg

    assert len(drop_infos) == 2, "one INFO per droppable predicate (assert + plain)"
    assert len(warns) == 1, "one summary WARN when droppable > 0"
    # excluded entries are NOT rendered as dropped predicates
    dropped_names = " ".join(r.getMessage() for r in drop_infos)
    assert "'a'" in dropped_names and "'p'" in dropped_names
    assert "'r'" not in dropped_names and "'s'" not in dropped_names


def test_owner_kind_display_wording(caplog):
    with caplog.at_level(logging.INFO, logger=_LOGGER_NAME):
        render_constraint_report(
            [_entry(ConstraintKind.PLAIN, "c", OwnerKind.PART_USAGE)],
            logging.getLogger(_LOGGER_NAME),
        )
    drop_infos = [r for r in caplog.records if "is not executable" in r.getMessage()]
    assert len(drop_infos) == 1
    assert "part usage" in drop_infos[0].getMessage()
