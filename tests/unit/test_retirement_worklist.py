"""The retirement runbook's step lists must be derived, not hand-copied.

Audit 4 (F1) measured the hand-copied version: the four steps named 66 rows and left 131
`retire-with-owner` and all 34 `repoint` rows named by no step at all. These cases pin the
derivation that replaced it — the placement rule itself, and the property the runbook rests
on, that every actionable row is named by exactly one step.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))

_spec = importlib.util.spec_from_file_location(
    "retirement_worklist", SCRIPTS / "retirement_worklist.py"
)
assert _spec is not None and _spec.loader is not None
worklist = importlib.util.module_from_spec(_spec)
# dataclasses resolve their annotations through sys.modules
sys.modules["retirement_worklist"] = worklist
_spec.loader.exec_module(worklist)


def test_every_actionable_row_is_named_by_exactly_one_step() -> None:
    """The F1 property. `check` returns 0 only when the placement is total."""
    assert worklist.check(worklist.load_items()) == 0


def test_a_deletion_group_places_its_own_rows() -> None:
    item = worklist.place(
        {
            "id": "L-900",
            "path": "src/pkg/legacy.py",
            "group": "4B-G4",
            "disposition": "delete",
        }
    )
    assert item is not None
    assert (item.step, item.action) == (4, "delete")


def test_a_dispositioned_row_lands_on_the_earliest_step_that_breaks_it() -> None:
    """`breaks_on` may name two groups; the file goes red at the first one."""
    item = worklist.place(
        {
            "id": "L-901",
            "path": "tests/unit/test_thing.py",
            "disposition": "retain",
            "disposition_4c": "retire-with-owner",
            "breaks_on": "pkg.a (L-010, 4B-G4); pkg.b (L-028, 4B-v5-family)",
        }
    )
    assert item is not None
    assert item.step == 2  # the v5 family, not G4' — the earliest step that breaks it


def test_an_archive_row_is_moved_not_deleted() -> None:
    """Plan rule 7: a probe carrying a finding is preserved."""
    item = worklist.place(
        {
            "id": "L-902",
            "path": "scripts/probes/probe_x.py",
            "disposition": "retain",
            "disposition_4c": "archive-with-findings",
            "breaks_on": "pkg.a (L-029, 4B-v5-family)",
        }
    )
    assert item is not None
    assert item.action == "archive"


def test_an_executed_row_is_placed_nowhere() -> None:
    assert (
        worklist.place(
            {
                "id": "L-006",
                "path": "src/pkg/gone.py",
                "group": "4B-G1",
                "disposition": "delete",
                "state": "executed",
            }
        )
        is None
    )


def test_the_owner_gated_duals_are_in_no_step() -> None:
    """The two agentic duals are in no step — and after retirement step 6, in no list.

    The owner ruled them in (disposition 2026-08-11, step 2 items 1-2), revise step 2
    migrated their consumers, and revise step 6 deleted the members and closed both rows at
    the agentic commit. An executed row is placed nowhere, so the ledger half of this node
    is now that absence.

    The mechanism it was written to pin is still live and still worth a claim, so it is
    stated over a constructed row instead of over a spent one: a *proposed* row in
    ``OWNER_GATED`` is held out of every step rather than falling into one.
    """
    rows = {row["id"]: row for row in json.loads(worklist.LEDGER.read_text())["rows"]}
    placed = {item.row for item in worklist.load_items()}
    for rid in ("L-036", "L-037"):
        assert rows[rid]["state"] == "executed"
        assert rid not in placed

    held_out = worklist.place(dict(rows["L-036"], state="proposed"))
    assert held_out is not None
    assert held_out.step is None
    assert held_out.action == "owner-gated"


def test_a_dispositioned_row_that_cannot_be_placed_refuses_rather_than_defaults() -> None:
    """A new data-axis row with no placement is a stop, not a silent step-1 assignment."""
    try:
        worklist.place(
            {
                "id": "L-999",
                "path": "tests/unit/test_new.py",
                "disposition": "retain",
                "disposition_4c": "repoint",
                "breaks_on": "",
            }
        )
    except SystemExit as exc:
        assert "L-999" in str(exc)
    else:  # pragma: no cover - the failure this test exists to prevent
        raise AssertionError("an unplaceable row was placed silently")


def test_the_v5_family_step_names_the_thirty_seven_fixtures() -> None:
    """The 37 committed v5 fixtures are the v5-family step's, one row each.

    Read from the ledger rather than from ``load_items()``: placement skips rows that are
    already executed, so a version of this that asked the work-list would go red the moment
    the step it describes actually ran, which is the opposite of what it means to check a
    placement rule. The rule itself is checked on the same rows, one by one, below.
    """
    rows = json.loads(worklist.LEDGER.read_text())["rows"]
    fixtures = [
        row for row in rows if row["path"].endswith("/extraction_snapshot.json")
    ]
    assert len(fixtures) == 37
    assert {row["group"] for row in fixtures} == {"4B-v5-family"}
    for row in fixtures:
        placed = worklist.place({**row, "state": "proposed"})
        assert placed is not None and placed.step == 2, row["id"]
