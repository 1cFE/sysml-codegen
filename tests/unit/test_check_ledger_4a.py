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
    """One row, reset to `proposed` so a test states the state it is exercising.

    Gate 4B writes real states into the committed ledger, and a negative test that
    inherited one would pass or fail for a reason it never named.
    """
    row = next(row for row in ledger["rows"] if row["id"] == row_id)
    for field in ("state", "executed_commit", "remaining"):
        row.pop(field, None)
    return row


def test_the_committed_row_states_agree_with_the_tree(ledger: dict) -> None:
    """Every state claim in the committed ledger is checked against Git, not believed."""
    assert checker.check_states(ledger["rows"]) == []


def test_a_row_with_no_state_is_proposed_and_passes(ledger: dict) -> None:
    """Gate 4A's rows carry no state field; adding the check must not invalidate them."""
    for row in ledger["rows"]:
        for field in ("state", "executed_commit", "remaining"):
            row.pop(field, None)
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


def test_a_partially_executed_row_must_say_what_is_left(ledger: dict) -> None:
    """Several G0 rows move one thing now and retire the rest in G3.

    A row that says only "executed" would claim the whole disposition is spent, which is
    how the original run lost track of what it had actually done.
    """
    row = _row(ledger, "L-018")
    row["state"] = "partially-executed"
    row["executed_commit"] = "0" * 40
    problems = checker.check_states(ledger["rows"])
    assert any("does not say what is left" in problem for problem in problems)

    row["remaining"] = "the PipelineContext class itself retires with pipeline_builder in G3"
    assert checker.check_states(ledger["rows"]) == []  # and the rest of the ledger stays clean


def test_a_partially_executed_row_whose_file_is_gone_fails(ledger: dict) -> None:
    row = _row(ledger, "L-018")
    row["path"] = "src/sysml_codegen/orchestration/vanished.py"
    row["state"] = "partially-executed"
    row["executed_commit"] = "0" * 40
    row["remaining"] = "G3"
    problems = checker.check_states(ledger["rows"])
    assert any("partially-executed but" in problem for problem in problems)


# --- Gate 4C part 3: surface coverage and group readiness --------------------
#
# The path check proves every path the candidate *touched* has a row. It cannot see a file
# the candidate never touched that a future deletion group will break at import time, which
# is how Gate 4B-G2 met two live conformance files with no row at all. These pin the check
# that closes that class, and the readiness check that says whether a group may run.


def _fake_repo(tmp_path: Path, relpath: str, source: str) -> Path:
    target = tmp_path / relpath
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(source)
    return tmp_path


DELETE_ROW = {
    "id": "L-900",
    "path": "src/sysml_codegen/legacy/reader.py",
    "repo": "sysml-codegen",
    "class": "production",
    "disposition": "delete",
    "origin": "forensic-diff",
    "group": "4B-G9",
    "reason": "a legacy reader",
}


def test_the_committed_ledger_has_no_unrowed_module_level_breakage(ledger: dict) -> None:
    assert checker.check_surface_coverage(ledger) == []


def test_a_file_with_no_row_that_imports_a_delete_row_at_module_level_fails(
    tmp_path: Path,
) -> None:
    repo = _fake_repo(
        tmp_path,
        "tests/test_unrowed.py",
        "from sysml_codegen.legacy.reader import read\n",
    )
    problems = checker.check_surface_coverage({"rows": [DELETE_ROW]}, repo)
    assert len(problems) == 1
    assert "tests/test_unrowed.py" in problems[0]
    assert "L-900" in problems[0] and "4B-G9" in problems[0]


def test_a_file_that_has_a_row_is_not_reported_as_unrowed(tmp_path: Path) -> None:
    repo = _fake_repo(
        tmp_path,
        "tests/test_rowed.py",
        "from sysml_codegen.legacy.reader import read\n",
    )
    rowed = {"id": "L-901", "path": "tests/test_rowed.py", "repo": "sysml-codegen",
             "class": "test", "disposition": "retain", "origin": "derived-blast-radius",
             "group": None, "reason": "has a row"}
    assert checker.check_surface_coverage({"rows": [DELETE_ROW, rowed]}, repo) == []


def test_a_function_local_import_is_not_an_unrowed_breakage(tmp_path: Path) -> None:
    """It breaks nodes, not collection, so the reviewer sees it as a test failure."""
    repo = _fake_repo(
        tmp_path,
        "tests/test_local.py",
        "def test_x():\n    from sysml_codegen.legacy.reader import read\n",
    )
    assert checker.check_surface_coverage({"rows": [DELETE_ROW]}, repo) == []


def test_a_migrate_row_removing_a_re_export_is_surface_too(tmp_path: Path) -> None:
    repo = _fake_repo(
        tmp_path,
        "tests/test_reexport.py",
        "from sysml_codegen.snapshot import load_extraction_snapshot\n",
    )
    migrate = {"id": "L-902", "path": "src/sysml_codegen/snapshot/__init__.py",
               "repo": "sysml-codegen", "class": "production", "disposition": "migrate",
               "origin": "phase3-carried", "group": "4B-G9", "reason": "drops re-exports",
               "removes": [{"group": "4B-G9", "symbols": ["load_extraction_snapshot"]}]}
    problems = checker.check_surface_coverage({"rows": [migrate]}, repo)
    assert len(problems) == 1
    assert "L-902" in problems[0]


def test_a_removes_block_is_scoped_to_the_group_that_spends_it() -> None:
    """One row can split across groups: G9 drops the reader, the writer waits."""
    migrate = {"id": "L-903", "path": "src/sysml_codegen/snapshot/__init__.py",
               "repo": "sysml-codegen", "class": "production", "disposition": "migrate",
               "origin": "phase3-carried", "group": "4B-G9", "reason": "split",
               "removes": [{"group": "4B-G9", "symbols": ["read_it"]},
                           {"group": "4B-later", "symbols": ["write_it"]}]}
    now = checker.removal_surface({"rows": [migrate]}, frozenset({"4B-G9"}))
    assert now.symbols["sysml_codegen.snapshot"] == frozenset({"read_it"})
    later = checker.removal_surface({"rows": [migrate]}, frozenset({"4B-later"}))
    assert later.symbols["sysml_codegen.snapshot"] == frozenset({"write_it"})


def test_an_executed_row_no_longer_contributes_surface() -> None:
    spent = dict(DELETE_ROW, state="executed", executed_commit="deadbee")
    assert checker.removal_surface({"rows": [spent]}).modules == frozenset()


def test_a_group_is_blocked_while_a_deferred_file_still_needs_its_surface(
    tmp_path: Path,
) -> None:
    repo = _fake_repo(
        tmp_path, "tests/test_defers.py", "from sysml_codegen.legacy.reader import read\n"
    )
    deferred = {"id": "L-904", "path": "tests/test_defers.py", "repo": "sysml-codegen",
                "class": "test", "disposition": "retain", "origin": "derived-blast-radius",
                "group": None, "reason": "still live", "disposition_4c": "defer-to-v5-family"}
    readiness = checker.group_readiness({"rows": [DELETE_ROW, deferred]}, "4B-G9", repo)
    assert not readiness.is_ready
    assert readiness.blockers == ("L-904 tests/test_defers.py",)


def test_a_group_is_ready_once_every_affected_file_retires_or_repoints(
    tmp_path: Path,
) -> None:
    repo = _fake_repo(
        tmp_path, "tests/test_retires.py", "from sysml_codegen.legacy.reader import read\n"
    )
    retiring = {"id": "L-905", "path": "tests/test_retires.py", "repo": "sysml-codegen",
                "class": "test", "disposition": "retain", "origin": "derived-blast-radius",
                "group": None, "reason": "green cover", "disposition_4c": "retire-with-owner"}
    readiness = checker.group_readiness({"rows": [DELETE_ROW, retiring]}, "4B-G9", repo)
    assert readiness.is_ready
    assert readiness.affected == 1


def test_every_affected_row_carries_its_own_gate_4c_part_3_disposition(
    ledger: dict,
) -> None:
    """Rule 6, mechanically: no file is disposed of by a bulk rule with no statement."""
    surface = checker.removal_surface(ledger)
    rows = {row["path"]: row for row in ledger["rows"]}
    for path in checker.surface_hits(checker.REPO_ROOT, surface):
        row = rows.get(path)
        assert row is not None, f"{path} has no ledger row"
        assert row.get("disposition_4c") in {
            "retire-with-owner", "rewrite", "repoint", "defer-to-v5-family",
            "defer-to-part-6",
        }, f"{path} has no Gate 4C part 3 disposition"
        assert row.get("responsibility"), f"{path} states no responsibility"
        assert row.get("disposition_4c_note"), f"{path} gives no reason for its disposition"


def test_a_retire_with_owner_row_names_the_green_replacement_that_covers_it(
    ledger: dict,
) -> None:
    """The whole point of the disposition: a retirement must name what replaces it."""
    for row in ledger["rows"]:
        if row.get("disposition_4c") != "retire-with-owner":
            continue
        assert row.get("replacement_proof_node"), (
            f"{row['id']} retires with its owner but names no replacement node"
        )


# --- Gate 4C part 5: the second axis -----------------------------------------
#
# Part 3 measured imports of src/ modules. Part B step 1 walked into the two axes it
# missed: a file can depend on a delete row by reading its bytes, or by importing a
# *script* that is itself a row. Neither is a package import, so neither was visible, and
# six live files were found breaking with no row at all.


FIXTURE_ROW = {
    "id": "L-910",
    "path": "tests/fixtures/toy/extraction_snapshot.json",
    "repo": "sysml-codegen",
    "class": "snapshot",
    "disposition": "delete",
    "origin": "forensic-diff",
    "group": "4B-G9",
    "reason": "a v5 fixture",
}
SCRIPT_ROW = {
    "id": "L-911",
    "path": "scripts/capture_legacy.py",
    "repo": "sysml-codegen",
    "class": "script",
    "disposition": "delete",
    "origin": "forensic-diff",
    "group": "4B-G9",
    "reason": "the v5 capture driver",
}


def test_the_committed_ledger_has_no_unrowed_data_breakage(ledger: dict) -> None:
    assert checker.check_data_surface_coverage(ledger) == []


def test_reading_a_deleted_fixture_by_path_is_surface(tmp_path: Path) -> None:
    repo = _fake_repo(
        tmp_path,
        "tests/test_reads.py",
        'PATH = "tests/fixtures/toy/extraction_snapshot.json"\n',
    )
    problems = checker.check_data_surface_coverage({"rows": [FIXTURE_ROW]}, repo)
    assert len(problems) == 1
    assert "L-910" in problems[0] and "tests/test_reads.py" in problems[0]


def test_globbing_deleted_fixtures_is_surface(tmp_path: Path) -> None:
    """A glob names no single path, which is exactly why a path-set check cannot see it."""
    repo = _fake_repo(
        tmp_path, "tests/test_globs.py", 'FIXTURES.glob("*/extraction_snapshot.json")\n'
    )
    assert len(checker.check_data_surface_coverage({"rows": [FIXTURE_ROW]}, repo)) == 1


def test_importing_a_deleted_script_is_surface(tmp_path: Path) -> None:
    repo = _fake_repo(
        tmp_path, "tests/test_imports.py", "from scripts.capture_legacy import MODELS\n"
    )
    problems = checker.check_data_surface_coverage({"rows": [SCRIPT_ROW]}, repo)
    assert len(problems) == 1
    assert "L-911" in problems[0]


def test_running_a_deleted_script_by_path_is_surface(tmp_path: Path) -> None:
    """A subprocess argument is a dependency the import graph cannot see at all."""
    repo = _fake_repo(
        tmp_path,
        "tests/test_subprocess.py",
        'run([sys.executable, "scripts/capture_legacy.py", "--fixture", "toy"])\n',
    )
    assert len(checker.check_data_surface_coverage({"rows": [SCRIPT_ROW]}, repo)) == 1


def test_a_file_with_a_row_is_not_reported_on_the_data_axis(tmp_path: Path) -> None:
    repo = _fake_repo(
        tmp_path, "tests/test_rowed.py", 'open("tests/fixtures/toy/extraction_snapshot.json")\n'
    )
    rowed = {"id": "L-912", "path": "tests/test_rowed.py", "repo": "sysml-codegen",
             "class": "test", "disposition": "retain", "origin": "derived-blast-radius",
             "group": None, "reason": "has a row"}
    assert checker.check_data_surface_coverage({"rows": [FIXTURE_ROW, rowed]}, repo) == []


def test_a_retained_fixture_contributes_no_data_surface(tmp_path: Path) -> None:
    """Only a *delete* row removes anything. A retained fixture breaks nobody."""
    repo = _fake_repo(
        tmp_path, "tests/test_reads.py", 'open("tests/fixtures/toy/extraction_snapshot.json")\n'
    )
    retained = dict(FIXTURE_ROW, disposition="retain")
    assert checker.check_data_surface_coverage({"rows": [retained]}, repo) == []


def test_a_deleted_script_does_not_report_itself(tmp_path: Path) -> None:
    repo = _fake_repo(tmp_path, "scripts/capture_legacy.py", "MODELS = {}\n")
    assert checker.check_data_surface_coverage({"rows": [SCRIPT_ROW]}, repo) == []


def test_the_paths_check_now_fails_on_either_axis(ledger: dict) -> None:
    """Both surface checks are wired into `paths`, so neither can be forgotten."""
    problems = checker.check_paths(ledger)
    assert problems == []
    # Drop the row that covers a real data-axis dependent and the wiring must notice.
    without = dict(
        ledger,
        rows=[row for row in ledger["rows"] if row["path"] != "tests/conftest.py"],
    )
    problems = checker.check_paths(without)
    assert any(
        "unrowed data breakage" in problem and "tests/conftest.py" in problem
        for problem in problems
    )
