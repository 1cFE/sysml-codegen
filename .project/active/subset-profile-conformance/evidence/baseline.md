# Baseline: both repositories before any Item 2a change (P1.1–1.2)

Recorded 2026-10-18 before any 2a code change. Every later phase gate and the P7 final checks compare with this file by test ID.

## Revisions and identity

- sysml-codegen: `d256845de832cd199ac57b5e5f99b85fd6d486f3` (branch `subset-conformance`). `src/` is identical to the spec base `b5663c07` (`git diff --stat b5663c07 HEAD -- src/` is empty).
- agentic-mbse: `882edc6a034fa792dd750423c9823e50806a2a53` (branch `subset-conformance`; `ccd57d83` plus two epic-planning commits, neither touching `src/` or `tests/`).
- `main` has no commits beyond `subset-conformance` in either repository (`git log --oneline subset-conformance..main` is empty in both).
- SysIDE 0.8.4, `agentic_mbse.__version__` 0.1.3, Python 3.12.3 (system build dated 2026-08-31), `SYSIDE_LICENSE_KEY` set from each worktree's `.env` (value not recorded).

## Commands

- codegen: `uv run --extra dev pytest tests/ -q -rfEs -p no:cacheprovider --junitxml=/tmp/subset-2a/baseline-codegen.xml`, after `set -a; source ../agentic-mbse/.env; set +a`.
- agentic-mbse: `uv run pytest tests/ -q -rfEs --junitxml=/tmp/subset-2a/baseline-agentic.xml`, after sourcing its `.env`. Default marker set (PD15), so 14 tests are deselected.
- Static checks: codegen `uv run --extra dev mypy src/` and `uv run --extra dev ruff check src/ tests/`; agentic-mbse `uv run mypy src/` and `uv run ruff check src/ tests/`.

The outcome of every test, by ID, is in `baseline/codegen-outcomes.json` and `baseline/agentic-outcomes.json` (read from the JUnit XML; JUnit reports agentic-mbse's one xfail as `skipped`).

## sysml-codegen

2735 passed, 10 failed, 9 skipped, 124 deselected, in 113.5 s. This matches spike S1's counts.

Failed:
- `tests/conformance/test_self_binding_guidance_contract.py::test_zero_unmarked_self_named_examples_across_all_trees`
- `tests/study/test_study_cli.py::test_a_missing_or_unknown_tool_is_a_usage_error[argv1-invalid choice: 'bogus' (choose from indicators, preflight, verify, integrate)]`
- `tests/unit/test_check_ledger_4a.py::test_the_committed_ledger_covers_the_git_derived_set_exactly`
- `tests/unit/test_check_ledger_4a.py::test_the_candidate_set_is_read_from_the_diff_so_deletions_are_visible`
- `tests/unit/test_check_ledger_4a.py::test_an_uncovered_path_fails`
- `tests/unit/test_check_ledger_4a.py::test_an_orphan_row_fails`
- `tests/unit/test_check_ledger_4a.py::test_a_carried_row_that_does_not_exist_at_head_fails`
- `tests/unit/test_check_ledger_4a.py::test_a_row_with_no_reason_fails`
- `tests/unit/test_check_ledger_4a.py::test_an_executed_carried_delete_is_not_reported_as_a_missing_carried_row`
- `tests/unit/test_check_ledger_4a.py::test_the_paths_check_now_fails_on_either_axis`

S1 described the set as one self-binding failure plus nine in `test_check_ledger_4a.py`. The run shows eight there and one in `test_study_cli.py`; the total is the same. S1 did not list the failures by ID, so which reading S1 had is not checked.

Skipped (all 9 in `tests/conformance/test_calc_compat_parity.py:91`, each "historical parity golden absent" with the test that covers the fixture instead): `agg_literal_probe`, `agg_localterm_probe`, `constraint_non_numerical`, `crosspart_rollup_twolevel`, `gate_a`, `gate_a_package_owner`, `modeled_default_fidelity`, `shadowed_reference`, `shared_producer`. None is a license skip.

Static checks: mypy "Success: no issues found in 85 source files". ruff over `src/` passes; ruff over `src/ tests/` reports 94 errors, all under `tests/` (largest: `tests/study/test_read_coverage.py` 11, `tests/conformance/test_calc_compat_parity.py` 11, the `tests/fixtures/study_station/` generated package 22). Full list: `/tmp/subset-2a/baseline-codegen-ruff.txt` at the time of the run; the count is the comparison point.

## agentic-mbse

**The phase-gate baseline is the all-extras run below (§ agentic-mbse with all extras, P2).** The run described in this section had only the default extras installed. It is kept as history: its 129 failing IDs are not the comparison set any more.

3524 passed, 94 failed, 35 errors, 8 skipped, 1 xfailed, 14 deselected, in 35.5 s.

All 129 failures and errors are outside `src/agentic_mbse/sysml/` and its tests, and every one is an environment failure:
- 123 in `tests/test_research/` (93), `tests/test_web_backend.py` (29) and `tests/test_extract_cli.py::TestFigureWarningsThroughCli::test_web_route`: the `web` extra is not installed. The direct errors are `ModuleNotFoundError: No module named 'trafilatura'` and the registration precondition "URL capture needs the web extra"; the rest of `test_research/` fails on assertions downstream of that precondition (`precondition_failed` where `registered`, `duplicate` or `holdout_hit` was expected).
- 3 in `tests/test_check.py` (`TestProbePandoc` ×2, `TestRunCheck::test_capability_predicts_whether_extract_substitutes[identified-with-html]`): Pandoc is not installed.
- `tests/test_equations.py::TestDetectEquations::test_returns_detected_equations`: `No module named 'PIL'`.
- 2 in `tests/test_index.py::TestScriptBackwardCompat`: hardcoded `cwd="/home/reid/1cfe/agentic-mbse"`, which does not exist.

Skipped: 7 "needs Pandoc" (`tests/test_arxiv_html.py:262, :678, :689`, `tests/test_pipeline.py:401, :515`, `tests/test_web_backend.py:450, :471`); `tests/test_sysml/test_adr002.py:281` "Requires fusion_modeling CATF models not in this repo". None is a license skip.

Static checks: mypy 98 errors in 20 files (5 in `src/agentic_mbse/sysml/`: `helpers.py` 3, `binding.py` 2); ruff 118 errors, none under `scripts/subset_profile/`.

## Pre-existing failures (PD11)

**Method.** codegen's suite was rerun at the 2a bases with the P1.2 gate script, from agentic-mbse `c39b4cda`: `uv run python scripts/subset_profile/codegen_suite.py run --agentic-rev ccd57d83 --codegen-rev b5663c07 --label baseline-2a --select tests/ --out /tmp/subset-2a/preexisting --tmp-root /tmp/subset-2a/trees`. The run's identity: codegen `b5663c07e987…`, agentic-mbse `ccd57d831aa8…`, `uv.lock` sha256 `a17e9fa1…a4d4`, sysml-codegen 0.1.1, agentic-mbse 0.1.3, SysIDE 0.8.4, all three packages resolved inside the exported tree, license key present. Result: 2685 passed, 53 failed, 7 errors, 9 skipped, 124 deselected; the outcomes are in `baseline/codegen-at-bases.json`. The test ID sets at HEAD and at the bases are identical.

Because agentic-mbse's HEAD baseline had failures, its suite also ran at `ccd57d83`, exported with `git archive` into `/tmp/subset-2a/agentic-ccd57d83` and synced with `uv sync --frozen`: 94 failed and 35 errors, the same 129 test IDs as at HEAD, with no test ID present in only one run.

| Test ID | Fails at the bases | Cause |
|---|---|---|
| `tests/conformance/test_self_binding_guidance_contract.py::test_zero_unmarked_self_named_examples_across_all_trees` | yes | Flags agentic-mbse `project_templates/MODELING_PROCESS.md.template`, which is identical at `ccd57d83` and HEAD (`git diff ccd57d83 HEAD -- project_templates/MODELING_PROCESS.md.template` is empty). Predates 2a. |
| `tests/study/test_study_cli.py::test_a_missing_or_unknown_tool_is_a_usage_error[argv1-…]` | yes | The system Python's argparse quotes the choices (`choose from 'indicators', …`); the test expects them unquoted. Environment. |
| `tests/unit/test_check_ledger_4a.py`, the 8 tests above | yes | `git diff 1672c57 07531e64` exits 128: `1672c57` exists in this clone, `07531e64` does not (`git cat-file -e`). Environment. |
| 129 agentic-mbse failures and errors | yes, all | Missing `web` extra, Pandoc and PIL, and a hardcoded `/home/reid/1cfe` path. Environment. |

**Failures at the bases only, from the export.** 50 codegen tests fail at the bases and pass at HEAD. They are an artifact of the method, not a difference between the revisions: `git archive` exports carry no `.git`, so 43 study-layer tests refuse with "no git work tree" or "not a git repository", 3 more `test_check_ledger_4a.py` tests cannot run `git diff`, and `test_v6_snapshot_inventory.py` (3) and `test_exact_route_fingerprint_stability.py` (1) read git state. Files: `tests/study/test_output_contract.py` 12, `test_read_coverage.py` 10, `test_preflight_gates.py` 8, `test_common.py` 4, `test_study_cli.py` 3, `test_integrate_refusals.py` 2, `test_tool_identity.py` 2, `test_study_fixture_current.py` 1, `test_census.py` 1. **Consequence for P7:** the gate run (`codegen_suite.py`) runs `tests/conformance/subset_profile` by default, which must not depend on git state, or the receipt run would fail for the same reason.

## agentic-mbse with all extras (re-recorded 2026-10-18, before P2)

The orchestrator ran `uv sync --all-extras` in the agentic-mbse worktree, which installs the `web` extra and PIL. Without those, 124 of the 129 failures above were missing-dependency failures, which hid any real failure in those files. The run was repeated with all extras, at HEAD and at the base.

- **Command:** `uv run --all-extras pytest tests/ -q -rfEs -p no:cacheprovider --junitxml=…`, after sourcing `.env`. The `--all-extras` flag is now part of the gate command: plain `uv run` does not remove extras that are installed, but a fresh `uv sync` would, and the 5-ID set holds only with all extras.
- **HEAD** `8be21e045a50` (P1 complete): 3597 passed, 5 failed, 8 skipped, 1 xfailed, 14 deselected, in 116.6 s. Outcomes by ID: `baseline/agentic-outcomes-allextras.json` (the xfail is reported as `skipped`, so the file shows 9 skipped).
- **Base** `ccd57d83`, exported with `git archive` into `/tmp/subset-2a/agentic-ccd57d83-allextras` and synced with `uv sync --frozen --all-extras`: 3648 passed, 5 failed, 8 skipped, 1 xfailed, 14 deselected. The 51 extra tests at the base are the ones P1.5 retired (the parity test) less those P1.2 and P1.4 added.
- **The same 5 IDs fail at both revisions:**
  - `tests/test_check.py::TestProbePandoc::test_reports_length_of_converted_markdown` (no Pandoc binary)
  - `tests/test_check.py::TestProbePandoc::test_conversion_error` (no Pandoc binary)
  - `tests/test_check.py::TestRunCheck::test_capability_predicts_whether_extract_substitutes[identified-with-html]` (no Pandoc binary)
  - `tests/test_index.py::TestScriptBackwardCompat::test_generate_index_script_runs` (hardcoded `cwd="/home/reid/1cfe/agentic-mbse"`)
  - `tests/test_index.py::TestScriptBackwardCompat::test_read_section_script_runs` (same path)
- Static checks with all extras, at HEAD `8be21e045a50` (taken in step 2.1): mypy `src/` reports 88 errors in 18 files, down from 98 because the extras' packages resolve imports mypy could not see before; ruff `src/ tests/` still reports 118. These are the agentic-mbse static-check baselines from P2 on.
- The 8 skips are the same as before: 7 "needs Pandoc" and the `test_adr002.py:281` CATF skip. None is a license skip.

From P2 onward, every phase gate and the P7 final checks compare agentic-mbse against these 5 IDs. The 129-ID record above stays as history.

**Conclusion.** No baseline failure is caused by this branch. The P7 comparison treats exactly the 10 codegen test IDs above and the 5 agentic-mbse test IDs from the all-extras run as pre-existing.
