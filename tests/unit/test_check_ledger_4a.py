"""The Gate 4A ledger checker must fail on the defects that produced the incident.

Two families. The path check must see *deletions* — the original census scanned a worktree,
where a deleted file simply is not there, and 118 changed paths went unrecorded. The
replacement check must resolve a real pytest node and watch it pass — the original accepted
absence as proof, so a deleted responsibility with no replacement scored the same as a
migrated one.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

import check_ledger_4a as checker  # noqa: E402

DESELECTED_NODE = "tests/execution/test_fusion_tea_real_teax.py"


@pytest.fixture
def ledger() -> dict:
    return checker.load_ledger()


def test_the_committed_ledger_covers_the_git_derived_set_exactly(ledger: dict) -> None:
    assert checker.check_paths(ledger) == []


def test_the_candidate_set_is_read_from_the_diff_so_deletions_are_visible(
    ledger: dict,
) -> None:
    """The defect that made the original census blind: deletions.

    A worktree scan of the rebuild finds these files present and would report nothing to
    disposition. Reading the diff finds them deleted by the candidate, which is the set the
    ledger owes rows for.
    """
    source = ledger["git_derived_from"]
    derived = checker.git_candidate_set(source["base"], source["candidate"])
    deleted_but_present = {
        path for path in derived if checker.path_at_head(path)
    }
    assert len(deleted_but_present) > 200
    assert "src/sysml_codegen/orchestration/pipeline_builder.py" not in derived
    assert "src/sysml_codegen/resolution/producer_resolution.py" in derived


def test_an_uncovered_path_fails(ledger: dict) -> None:
    dropped = next(
        row for row in ledger["rows"] if row["origin"] == "forensic-diff"
    )
    ledger["rows"] = [row for row in ledger["rows"] if row is not dropped]
    problems = checker.check_paths(ledger)
    assert any(
        problem.startswith("uncovered path") and dropped["path"] in problem
        for problem in problems
    )


def test_an_orphan_row_fails(ledger: dict) -> None:
    ledger["rows"].append(
        {
            "id": "L-999",
            "path": "src/sysml_codegen/not_in_the_diff.py",
            "repo": "sysml-codegen",
            "class": "production",
            "disposition": "delete",
            "origin": "forensic-diff",
            "group": "4B-G1",
            "authority": "invented",
            "unreachability": None,
            "replacement_proof_node": None,
            "blocked_by": [],
            "reason": "invented",
        }
    )
    problems = checker.check_paths(ledger)
    assert any("orphan row" in problem for problem in problems)


def test_a_carried_row_that_does_not_exist_at_head_fails(ledger: dict) -> None:
    ledger["rows"].append(
        {
            "id": "L-998",
            "path": "src/sysml_codegen/gone.py",
            "repo": "sysml-codegen",
            "class": "production",
            "disposition": "delete",
            "origin": "phase3-carried",
            "group": "4B-G1",
            "authority": "invented",
            "unreachability": None,
            "replacement_proof_node": None,
            "blocked_by": [],
            "reason": "invented",
        }
    )
    problems = checker.check_paths(ledger)
    assert any("does not exist at HEAD" in problem for problem in problems)


def test_a_row_with_no_reason_fails(ledger: dict) -> None:
    ledger["rows"][0]["reason"] = ""
    assert any("no reason recorded" in problem for problem in checker.check_paths(ledger))


def _write_node(tmp_path: Path, body: str) -> str:
    module = tmp_path / "test_replacement_probe.py"
    module.write_text(body)
    return f"{module}::test_probe"


def test_replacement_is_green_on_a_node_that_collects_and_passes(tmp_path: Path) -> None:
    node = _write_node(tmp_path, "def test_probe() -> None:\n    assert True\n")
    proof = checker.replacement_is_green(node, sys.executable)
    assert proof.verdict is checker.Verdict.GREEN
    assert proof.is_green


def test_replacement_is_not_green_when_the_node_is_missing(tmp_path: Path) -> None:
    node = _write_node(tmp_path, "def test_other() -> None:\n    assert True\n")
    proof = checker.replacement_is_green(node, sys.executable)
    assert proof.verdict is checker.Verdict.MISSING
    assert not proof.is_green


def test_replacement_is_not_green_when_the_node_is_deselected() -> None:
    """A node the required suite never runs is not a replacement.

    ``tests/execution`` is deselected by the default marker expression, so this module
    exists and passes when its lane is selected — and still cannot prove a replacement in
    the suite the gate runs.
    """
    proof = checker.replacement_is_green(DESELECTED_NODE, sys.executable)
    assert proof.verdict is checker.Verdict.DESELECTED
    assert not proof.is_green


def test_replacement_is_not_green_when_the_node_fails(tmp_path: Path) -> None:
    node = _write_node(tmp_path, "def test_probe() -> None:\n    assert False\n")
    proof = checker.replacement_is_green(node, sys.executable)
    assert proof.verdict is checker.Verdict.FAILED
    assert not proof.is_green


def test_a_row_may_name_the_lane_its_replacement_runs_in() -> None:
    """Deselection is judged inside the suite the row declares, not one global suite.

    ``tests/runtime/test_pipeline_runner.py``'s responsibility was superseded by the real-TEAx
    mutation lane, which the default marker expression excludes. Without a declared lane the
    row reads as deselected; with one it is checked where it actually runs.
    """
    assert checker.SUITES["execution"] == ("-m", "execution")
    row = next(
        row
        for row in checker.load_ledger()["rows"]
        if row["path"] == "tests/runtime/test_pipeline_runner.py"
    )
    assert row["required_suite"] == "execution"
    assert checker.replacement_is_green(
        DESELECTED_NODE, sys.executable, "not-a-suite"
    ).verdict is checker.Verdict.MISSING


def test_a_pending_replacement_is_never_green() -> None:
    proof = checker.replacement_is_green("PENDING-4C: an exact-route fixture", sys.executable)
    assert proof.verdict is checker.Verdict.PENDING
    assert not proof.is_green


def test_every_row_that_deletes_or_migrates_names_a_replacement_or_a_pending_owner(
    ledger: dict,
) -> None:
    """No silent deletion: a row that removes something owes a named node.

    The three exceptions are stated by path, not by class, so a new one cannot slip in.
    """
    allowed_without_node = {
        "src/sysml_codegen/elaboration/diff.py",  # recovery-only comparator
        "tests/helpers/legacy_route.py",  # the adapter itself
    }
    missing = [
        row["path"]
        for row in ledger["rows"]
        if row["disposition"] in {"delete", "migrate"}
        and not row["replacement_proof_node"]
        and row["path"] not in allowed_without_node
    ]
    assert missing == []


def test_every_conflict_row_states_what_the_orchestrator_must_rule_on(ledger: dict) -> None:
    conflicts = [row for row in ledger["rows"] if row.get("conflict")]
    assert conflicts, "the ledger records at least the two derived conflicts"
    for row in conflicts:
        assert len(row["conflict"]) > 80, row["id"]


# ---------------------------------------------------------------------------
# Row state: Gate 4B marks a row executed, and the checker verifies the claim
# ---------------------------------------------------------------------------


def _row(ledger: dict, row_id: str) -> dict:
    return next(row for row in ledger["rows"] if row["id"] == row_id)


def test_a_row_with_no_state_is_proposed_and_passes(ledger: dict) -> None:
    """Gate 4A's rows carry no state field; adding the check must not invalidate them."""
    assert checker.check_states(ledger["rows"]) == []


def test_an_executed_row_must_name_its_commit(ledger: dict) -> None:
    row = _row(ledger, "L-025")
    row["state"] = "executed"
    problems = checker.check_states(ledger["rows"])
    assert any("L-025: executed row names no commit" == problem for problem in problems)


def test_a_proposed_row_may_not_claim_a_commit(ledger: dict) -> None:
    row = _row(ledger, "L-025")
    row["executed_commit"] = "0" * 40
    problems = checker.check_states(ledger["rows"])
    assert any("proposed row names an executed_commit" in problem for problem in problems)


def test_an_executed_delete_whose_file_is_still_there_fails(ledger: dict) -> None:
    """The claim is checked against Git, exactly as the candidate set is."""
    row = _row(ledger, "L-001")  # constraint_lowering.py, still at HEAD
    row["state"] = "executed"
    row["executed_commit"] = "0" * 40
    problems = checker.check_states(ledger["rows"])
    assert any("still at HEAD" in problem for problem in problems)


def test_an_executed_migrate_whose_file_vanished_fails(ledger: dict) -> None:
    row = _row(ledger, "L-025")
    row["path"] = "src/sysml_codegen/never_existed.py"
    row["state"] = "executed"
    row["executed_commit"] = "0" * 40
    problems = checker.check_states(ledger["rows"])
    assert any("is gone from HEAD" in problem for problem in problems)


def test_an_unknown_state_fails(ledger: dict) -> None:
    _row(ledger, "L-025")["state"] = "half-done"
    problems = checker.check_states(ledger["rows"])
    assert any("unknown state" in problem for problem in problems)


def test_an_executed_carried_delete_is_not_reported_as_a_missing_carried_row(
    ledger: dict,
) -> None:
    """The two halves must not contradict each other at G2/G3.

    ``check_paths`` requires a carried row to exist at HEAD. A carried row whose
    disposition is ``delete`` stops existing the moment its group runs, and that is the
    ledger working, not a defect — so the existence rule yields to the state rule.
    """
    row = _row(ledger, "L-029")  # pipeline_builder.py: phase3-carried, delete
    row["path"] = "src/sysml_codegen/orchestration/already_deleted.py"
    row["state"] = "executed"
    row["executed_commit"] = "0" * 40
    problems = checker.check_paths(ledger)
    assert not any("does not exist at HEAD" in problem for problem in problems)


def test_a_multi_node_replacement_is_green_only_when_every_node_is(tmp_path: Path) -> None:
    """C1's ruling names three modules for one responsibility; all three must pass."""
    green = [
        "tests/conformance/test_gen_stencils.py",
        "tests/unit/test_stencils.py",
    ]
    assert checker.replacement_is_green(green).is_green

    missing = checker.replacement_is_green([*green, "tests/unit/test_does_not_exist.py"])
    assert missing.verdict is checker.Verdict.MISSING
    assert not checker.replacement_is_green([]).is_green
