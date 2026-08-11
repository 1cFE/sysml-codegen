"""The retirement runbook's step lists must be derived, not hand-copied.

Audit 4 (F1) measured the hand-copied version: the four steps named 66 rows and left 131
`retire-with-owner` and all 34 `repoint` rows named by no step at all. These cases pin the
derivation that replaced it — the placement rule itself, and the property the runbook rests
on, that every actionable row is named by exactly one step.
"""

from __future__ import annotations

import importlib.util
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
            "group": "4B-G2",
            "disposition": "delete",
        }
    )
    assert item is not None
    assert (item.step, item.action) == (2, "delete")


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
    assert item.step == 1


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
    items = {item.row: item for item in worklist.load_items()}
    for row in ("L-036", "L-037"):
        assert items[row].step is None
        assert items[row].action == "owner-gated"


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
    step1 = {item.path for item in worklist.load_items() if item.step == 1}
    fixtures = {p for p in step1 if p.endswith("/extraction_snapshot.json")}
    assert len(fixtures) == 37
