"""The proof-integrity check must be able to fail.

Audit 4 (F6) measured that the live tree can no longer exercise this check: every group has
been READY since Gate 4C part 7 chunk 19, so `blocked_paths` is empty and the problem loop
never runs. A check that cannot fail on the tree it runs against proves nothing about the tree
*or* about itself, so its failure path is proven here instead, on constructed rows.
"""

from __future__ import annotations

import importlib.util
import sys
from dataclasses import dataclass
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"
sys.path.insert(0, str(SCRIPTS))

_spec = importlib.util.spec_from_file_location(
    "check_proof_integrity", SCRIPTS / "check_proof_integrity.py"
)
assert _spec is not None and _spec.loader is not None
integrity = importlib.util.module_from_spec(_spec)
# dataclasses resolve their annotations through sys.modules
sys.modules["check_proof_integrity"] = integrity
_spec.loader.exec_module(integrity)


@dataclass
class FakeReadiness:
    blockers: list[str]


def readiness_for(blockers_by_group: dict[str, list[str]]):
    """A stand-in for the Gate 4A checker's `group_readiness`, over constructed blockers."""

    def readiness(_ledger: dict, group: str) -> FakeReadiness:
        return FakeReadiness(blockers_by_group.get(group, []))

    return readiness


def test_a_proof_in_a_blocking_file_is_reported() -> None:
    """The defect the check exists for: the proof dies with the deletion it authorises."""
    rows = [
        {
            "id": "L-900",
            "path": "src/pkg/legacy.py",
            "replacement_proof_node": "tests/unit/test_thing.py::test_it",
        }
    ]
    blocked = integrity.blocked_paths(
        {}, readiness_for({"4B-G2": ["L-901 tests/unit/test_thing.py"]})
    )
    assert blocked == {"tests/unit/test_thing.py": "L-901"}

    problems = integrity.find_problems(rows, blocked)
    assert len(problems) == 1
    assert "L-900" in problems[0] and "L-901" in problems[0]
    assert integrity.report(problems, len(blocked)) == 1


def test_a_proof_in_a_surviving_file_is_not_reported() -> None:
    rows = [
        {
            "id": "L-900",
            "path": "src/pkg/legacy.py",
            "replacement_proof_node": "tests/unit/test_survivor.py::test_it",
        }
    ]
    blocked = {"tests/unit/test_thing.py": "L-901"}
    assert integrity.find_problems(rows, blocked) == []
    assert integrity.report([], len(blocked)) == 0


def test_every_node_of_a_multi_node_proof_is_checked() -> None:
    """A row may name a list of proof nodes; one bad node is enough to fail the row."""
    rows = [
        {
            "id": "L-900",
            "path": "src/pkg/legacy.py",
            "replacement_proof_node": [
                "tests/unit/test_survivor.py::test_a",
                "tests/unit/test_thing.py::test_b",
            ],
        }
    ]
    problems = integrity.find_problems(rows, {"tests/unit/test_thing.py": "L-901"})
    assert len(problems) == 1
    assert "test_b" in problems[0]


def test_a_row_with_no_proof_node_is_skipped_not_crashed() -> None:
    rows = [{"id": "L-900", "path": "docs/x.md", "replacement_proof_node": None}]
    assert integrity.find_problems(rows, {"docs/x.md": "L-901"}) == []


def test_blockers_are_collected_across_every_deletion_group() -> None:
    """Transitivity: a file that only blocks G4' still kills a proof that runs at step 1."""
    blocked = integrity.blocked_paths(
        {},
        readiness_for(
            {
                "4B-v5-family": ["L-901 tests/a.py"],
                "4B-G4": ["L-902 tests/b.py"],
            }
        ),
    )
    assert blocked == {"tests/a.py": "L-901", "tests/b.py": "L-902"}


def test_the_live_ledger_reports_zero_problems() -> None:
    """The reading audit 4 recorded, kept as a tripwire rather than as evidence."""
    checker = integrity._checker()
    ledger = checker["load_ledger"]()
    blocked = integrity.blocked_paths(ledger, checker["group_readiness"])
    assert integrity.find_problems(ledger["rows"], blocked) == []
