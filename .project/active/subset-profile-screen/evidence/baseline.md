# Baseline: both repositories before any Item 2b code change (Phase 0)

Recorded 2026-10-20 at sysml-codegen `556cbedf` (branch `subset-profile-screen`; `src/` is unchanged since the design base `18714833`) and agentic-mbse `e268357f` (clean, not edited). Every later phase exit compares with this file by test ID.

## Environment

- SysIDE license from the worktree's `.env` (value not recorded). Python 3.12.3. Every licensed run below had the key set; no test skipped for a missing license.
- Suites run with `--all-extras` as the plan asks. sysml-codegen has one extra (`dev`), so this is the same environment 2a's `--extra dev` gave.

## Commands

- codegen: `set -a; source .env; set +a; uv run --all-extras pytest tests/ -q -rfEs -p no:cacheprovider --durations=50 --junitxml=/tmp/subset-2b/base-codegen.xml`
- agentic-mbse (in its worktree): `set -a; source .env; set +a; uv run --all-extras pytest tests/ -q -rfEs -p no:cacheprovider --junitxml=/tmp/subset-2b/base-agentic.xml`
- Static checks: `uv run --extra dev mypy src/`, `uv run --extra dev ruff check src/`, `uv run --extra dev ruff check src/ tests/`.
- Phase exit comparison: read the new JUnit XML into the same `{test id: passed|failed|skipped}` form as `codegen-outcomes-base.json` and require (a) every failing ID is in `codegen-failing-base.txt`, (b) no ID that passed here is now skipped or missing.

## sysml-codegen

7170 passed, 9 failed, 9 skipped, 124 deselected, in 180.3 s (wall clock 3:02 under `/usr/bin/time`, peak RSS 0.9 GB). Outcomes by ID: `codegen-outcomes-base.json`. Failing IDs: `codegen-failing-base.txt`. The 50 slowest tests: `durations-base.txt`.

The 9 failures are 2a's environment failures: 8 in `tests/unit/test_check_ledger_4a.py` (a commit the clone lacks) and `tests/study/test_study_cli.py::test_a_missing_or_unknown_tool_is_a_usage_error[argv1-…]` (the system argparse quotes choices).

**The 2a "10 versus 9" gap, settled by ID.** 2a's baseline had 10 failures. The tenth, `tests/conformance/test_self_binding_guidance_contract.py::test_zero_unmarked_self_named_examples_across_all_trees`, now passes. Both its input and the test changed after 2a's base: agentic-mbse `60c75af3` edited `project_templates/MODELING_PROCESS.md.template`, and codegen `f904953c` pointed the test at relocated guidance sources. Which of the two made it pass is not checked. The current set is exactly 2a's set minus that test.

The 9 skips are the same 9 `test_calc_compat_parity.py:91` "historical parity golden absent" skips as 2a. None is a license skip.

Static checks: mypy "Success: no issues found in 87 source files"; ruff `src/` passes; ruff `src/ tests/` reports 94 errors, all under `tests/`, the same count as 2a. Files Appendix A touches have no mypy or ruff error under `src/`.

## agentic-mbse (all extras)

4447 passed, 5 failed, 8 skipped, 1 xfailed, 17 deselected, in 130.2 s. Outcomes: `agentic-outcomes-base.json` (the xfail shows as `skipped`). The 5 failures are 2a's 5 all-extras IDs exactly (`agentic-failing-base.txt`): three Pandoc tests in `tests/test_check.py` and two `tests/test_index.py::TestScriptBackwardCompat` tests with the hard-coded `/home/reid/1cfe` path. `git status --porcelain` in the worktree was empty after the run.

## Execution lane: not run

`tests/execution` needs `CODEGEN_EXECUTION_PROVENANCE`, a manifest naming hashed artifact archives for the codegen, agentic-mbse and teax roots (`tests/execution/environment_pins.py`). No such manifest exists on this machine and nothing in either repository builds one. Phases 1-3 do not depend on it; Phase 9 (D15) needs it before close, so the owner or the orchestrator has to supply the provenance manifest by then.

## Timings (B3)

`sysml-codegen generate --models <dir> --output <tmp>` wall time, one run each, license set: `catf_mfe_d5` (sources from `spike-snapshot/regen/catf_mfe_d5`) 4.19 s; `catf_mfe_gated` 3.84 s. Both include `uv run` startup.

## Byte-identity manifest (D15)

`scripts/package_manifest.py record` runs `run_codegen(GenerationConfig(...))` with default options on 123 subjects: the 77 2a builds cases live, the 23 committed v6 snapshots replayed, and those 23 snapshots' sources live (all present in this checkout, including the untracked `catf_mfe_d5` regen folder). 117 generate; the 6 that refuse are `constraint_inline`, `constraint_non_numerical` and `unresolvable_attr_probe`, live and replayed (their refusals are the fixtures' point). 3418 files in all. Saved as `package-manifest-base.json`.

Determinism: a second run into a different temporary folder (`compare`) gave 0 differences. **Nothing was normalized.**

## Refusal-record oracle

`scripts/refusal_records.py record` wrote `tests/expectations/subset_profile/refusal_records.json`: 173 entries, each exactly one refusal-carrying record.

- 169 refused 2a cases (`case:<id>`), each into an empty destination.
- `destination_link:output-naming__param_field_collision`: D4's coincidence case. At the base it logs `Package sealing failed: INVALID_PATH(elsewhere): symlinks are forbidden beneath the package root` with `PACKAGE_WRITE`, as the design says.
- `writer_failure:CodeGenerationError|OSError|RuntimeError`: D18, with `_generate_pipeline` patched on the builds case `anonymous-declaration__attribute_usage`. Messages: "Code generation failed: …" (`GENERATION`), "Writing the generated package failed: …" (`PACKAGE_WRITE`), "Code generation failed: SI_INTERNAL_DEFECT: …" (`DIAGNOSTIC`).

Placeholders replace the output folder, this checkout and the installed agentic-mbse path (`tests/helpers/refusal_records.py`); no record holds a code location, so moving code cannot change a record. `compare` against itself: 0 of 173 differ.

## Probe 1: what the writers can reach (D14, "de-risk first")

`call_closure` (added to `tests/helpers/subset_profile/site_scan.py`, unit-tested in `tests/conformance/subset_profile/test_call_closure.py`) from today's writer roots (`_ensure_package_init_files`, `_clear_output_directory`, `_setup_output_directories`, `_generate_primitives`, the eight `_generate_*` writers, `_seal_package`) reaches 105 functions. Joined with the site account, the covered sites (`public_capability`, `malformed_input`, `unknown`, `relay_plumbing`) in that closure are exactly three:

| account line | site | reached through |
|---|---|---|
| 337 | `generation/entry_point.py::_refuse_colliding_field_names` (`PARAM_FIELD_COLLISION`) | `generate_all_derived_schemas`, the schema writer |
| 338 | `generation/errors.py::validate_constraint_graph_or_raise` | `_preflight_constraint_names`, `generate_pipeline_yaml`, `generate_registry`, `build_model_contract` |
| 341 | `generation/modules.py::assert_unique_predicate_function_names` | `_preflight_constraint_names` only |

**This matches the design's prediction** (site 337, site 338 through the three renderer guards, and the sites behind the nine `_preflight_constraint_names` calls, which are 338 and 341). After Phase 5 drops the re-checks, 341 leaves the closure and 338 stays through the three renderer guards, as D14 allows.

Closure rules, refined while running the probe because a naive name match reached all of elaboration: a dunder call (`super().__init__`) is left to construction; a nested function is visible only from its enclosing function (Jinja's `template.render()` had matched a nested `render` in projection); a method is reached only through an attribute; annotations are not followed; a module-level `alias = name` is followed across modules (`generate_all_derived_schemas_from_graph = generate_all_derived_schemas` hid site 337 at first).

## Probe 2: the String-default fact (D8 option 2)

Case `candidate-es-010-refusal__string_library_default__unbound_input` builds (stored outcome `generated`, loss `rg2_pending`). Its entry points:

| key | entry_type | python_type | default_value | unresolved_default_kind |
|---|---|---|---|---|
| `fx__gen__rate` | `DESIGN_ATTRIBUTE` | `float` | `2.0` | `None` |
| `fx__gen__t__u` | `LIBRARY_DEFAULT` | `str` | `None` | `"literal"` |

**The review's inference holds.** The String default is a `LIBRARY_DEFAULT`, `str` entry point with no default value and `unresolved_default_kind == "literal"` (set where `float()` fails in `extraction/modeled_defaults.py:47-51`).
