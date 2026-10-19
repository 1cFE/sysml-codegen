# Final repository checks (Item 2a P7, 2026-10-19)

**Result: both repositories match the baseline.** No test fails that did not fail in `baseline.md`'s pre-existing set, the skips are the baseline's skips by ID, and the static checks report the baseline's counts. The gate run's 3861 codegen subset tests passed with no skip, so the receipt is from a licensed run.

## Revisions

- sysml-codegen: `fdc1f7849e8356850832a8c30f9194444eef885c` for the code under test. The P7 commit after it touches only `.project/`.
- agentic-mbse: `2b2cbb810e557785ce64b15d7d212c4bf0671cf8` (the receipt commit). Its covered files are the same as at `db25490c`, the revision the gate ran on.
- SysIDE 0.8.4, Python 3.12.3, `SYSIDE_LICENSE_KEY` sourced from agentic-mbse's `.env` (value not recorded).
- `main` has no commits beyond `subset-conformance` in either repository: local `main` and the last-fetched `origin/main` are `b5663c07` (codegen) and `ebb3d467` (agentic-mbse), both ancestors of the branch. Nothing was fetched, so a merge to the remotes after the last fetch would not show here.

## sysml-codegen

- **Command:** `uv run --extra dev pytest tests/ -q -rfEs -p no:cacheprovider --junitxml=…`, license sourced. **Result:** 6644 passed, 9 failed, 9 skipped, 124 deselected, in 322.9 s. Outcomes by ID: `final/codegen-outcomes.json`.
- **Failures:** the 9 baseline IDs (`test_study_cli.py` bogus-tool, and the 8 `test_check_ledger_4a.py` tests), each an environment failure (`baseline.md` § Pre-existing). None new.
- **A baseline failure that now passes:** `test_self_binding_guidance_contract.py::test_zero_unmarked_self_named_examples_across_all_trees`. It reads agentic-mbse guidance that Item 4 changed (noted at the Phase 2 gate).
- **Tests:** 3908 added, 0 removed against the baseline's IDs.
- **Skips:** the baseline's 9, by ID: `test_calc_compat_parity.py:91` for `agg_literal_probe`, `agg_localterm_probe`, `constraint_non_numerical`, `crosspart_rollup_twolevel`, `gate_a`, `gate_a_package_owner`, `modeled_default_fidelity`, `shadowed_reference` and `shared_producer`, each "historical parity golden absent" with the test that covers it. None is a license skip.
- **Deselected:** 124, the `execution` lane, excluded by `addopts`. It needs TEAx (`TEAX_SIMKIT_PATH`) and was **not run**.
- **mypy** `src/`: "Success: no issues found in 87 source files" (baseline: clean, 85 files; 2a added two modules).
- **ruff** `src/ tests/`: 94 errors, the baseline count; `src/` alone is clean. Not compared error by error.
- **Phase-gate invariants:** the 22 committed `instance_graph_snapshot.json` files are byte-identical to `d73a4fc5`; `tests/expectations/public_package_oracle/baseline.json` and `tests/fixtures/v6_recapture_batch/batch.json` are unchanged since `d73a4fc5`, and their tests pass in the run above.

## agentic-mbse

- **Command:** `uv run --all-extras pytest tests/ -q -rfEs -p no:cacheprovider --junitxml=…`, `.env` sourced. **Result:** 3960 passed, 5 failed, 8 skipped, 1 xfailed, 17 deselected, in 119 s. Outcomes by ID: `final/agentic-outcomes-allextras.json` (JUnit reports the xfail as `skipped`).
- **Failures:** the 5 all-extras baseline IDs (3 Pandoc, 2 hardcoded `/home/reid/1cfe` path). None new.
- **Skips:** the baseline's 8, by ID: 7 "needs Pandoc" and `test_adr002.py` "Requires fusion_modeling CATF models not in this repo". The xfail is `test_packaged_guidance_contract.py::test_built_wheel_carries_every_packaged_file_unchanged[docs]`, as at baseline. None is a license skip.
- **Deselected:** 17 (baseline 14), by the repository's default marker set (PD15). Not run. Which 3 tests are newly deselected was not traced.
- **Tests:** 820 added, 457 removed. Removed: the retired probe tests (`test_subset_probe_evidence.py` 281, `test_subset_probe_judge.py` 46) and parametrized IDs that changed when probes became cases or rules changed (rule replays 81, `test_subset_matrix.py` 35, records 6, scripts 8; each module also gained IDs). Added: the case-citation, rule-replay, matrix, records, conformance-case and receipt tests, and Item 4's positional-binding tests brought in by the Phase 2 rebase.
- **mypy** `src/` (with all extras): 88 errors in 18 files, the baseline count.
- **ruff** `src/ tests/`: 118, the baseline count. `scripts/subset_profile/` is clean. ruff over all of `scripts/` reports errors in `scripts/sync_stdlib.py`, which 2a did not touch and the baseline did not cover.

## The gate run (receipt)

- `uv run python scripts/subset_profile/codegen_suite.py run --agentic-rev HEAD --codegen-rev fdc1f784… --label gate --out /tmp/subset-2a/gate`, at agentic-mbse `db25490c`: 3861 passed in 202.7 s, nothing else. Per-test report: `gate/gate.json`.
- The first attempt stopped with `IsolationBreachError` before writing anything: this worktree was edited while the run was going (evidence files, not code). The guard worked as designed; the rerun was made with the worktree untouched.
- Receipt `tests/fixtures/subset_profile/codegen_gate.json` (agentic-mbse `2b2cbb81`): `codegen_rev` `fdc1f7849e8356850832a8c30f9194444eef885c`, `agentic_rev` `db25490c0460416a24adba072fb1e96d36cb7810`, 154 case IDs, which is every packaged case. `tests/test_subset_gate_receipt.py` passes on it.

## Checks not run

- The codegen `execution` lane (124 tests, needs TEAx) and agentic-mbse's 17 deselected tests.
- ruff over agentic-mbse `scripts/` outside `subset_profile/`, and any error-by-error ruff comparison.
- `uv build --wheel` in agentic-mbse at the final revision (last checked at P2.1). The receipt test reads the working tree, not the wheel.
- No remote was fetched, so whether either remote `main` moved after the last fetch is not known.
