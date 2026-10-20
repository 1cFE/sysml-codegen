# Churn lists for Phases 2-8 (Phase 0, at `556cbedf`)

Found by grepping `tests/` and `scripts/` for every name D1 moves out of `cli/__init__.py`: `_ensure_package_init_files`, `_clear_output_directory`, `_setup_output_directories`, `_generate_primitives`, `_get_template_env`, `_get_python_path`, `_raw_source_name`, `_module_source`, `_check_duplicate_output_paths`, the six `_preflight_*` functions, the eight `_generate_*` writers, `_seal_package` and `_generate_package_from_graph`. Comments and docstrings that only mention a name are listed last; they need a wording check, not an import change.

## 1. Import lines naming a moved name

Multi-line imports in full:

- `tests/conformance/test_constraint_generation_integration.py:28-40`: `from sysml_codegen.cli import (GenerationConfig, _generate_backlog, _generate_entry_points, _generate_modules, _generate_pipeline, _generate_registry, _generate_schemas, _generate_stencils, _generate_tests, _get_template_env, _setup_output_directories)`
- `tests/conformance/test_coverage_preflight.py:20-24`: `from sysml_codegen.cli import (GenerationConfig, _generate_package_from_graph, _preflight_coverage_account)`
- `tests/conformance/test_exact_route_generated_package.py:23-33`: `from sysml_codegen.cli import (GenerationConfig, _generate_entry_points, _generate_modules, _generate_pipeline, _generate_registry, _generate_schemas, _generate_stencils, _get_template_env, _setup_output_directories)`
- `tests/conformance/test_zero_entry_package_golden.py:52-62`: the same nine names as `test_exact_route_generated_package.py`.
- `tests/unit/test_cli_generation.py:16-30`: `from sysml_codegen.cli import (GenerationConfig, _generate_backlog, _generate_entry_points, _generate_modules, _generate_package_from_graph, _generate_pipeline, _generate_registry, _generate_schemas, _generate_stencils, _generate_tests, _get_template_env, _seal_package, run_codegen)`

Single-line imports:

- `tests/conformance/test_constraint_catalog_totality.py:20`: `GenerationConfig, _generate_package_from_graph`
- `tests/conformance/test_coverage_preflight.py:39`, `:162` (function-local): `_get_template_env`
- `tests/conformance/test_diagnostic_provenance_sites.py:285` (local): `_check_duplicate_output_paths`
- `tests/conformance/test_entry_point_generation.py:7`: `_get_template_env`
- `tests/conformance/test_exact_route_seal_step9.py:152` (local): `_seal_package`
- `tests/conformance/test_module_kind_faildloud.py:298` (local): `_check_duplicate_output_paths`; `:331` (local): `GenerationConfig, _generate_stencils, _get_template_env`
- `tests/unit/test_cli_generation.py:59, 68, 76, 83` (local): `_ensure_package_init_files`; `:94, 111, 124` (local): `GenerationConfig, _setup_output_directories`
- `tests/unit/test_duplicate_path_failfast.py:13`: `_check_duplicate_output_paths`
- `tests/unit/test_stencils.py:553` (local): `GenerationConfig, _generate_stencils`
- `scripts/assess_v6_snapshot_churn.py:21`: `_get_template_env`

Not churn: `tests/unit/test_stencils.py:41`, `tests/unit/test_aggregation_generation.py:94` and `tests/unit/test_computed_attr_generation.py:200` define their own local `_get_template_env`.

## 2. Monkeypatches of a moved name

The design listed four. There is a fifth.

- `tests/unit/test_cli_generation.py:466`: `monkeypatch.setattr("sysml_codegen.cli._generate_package_from_graph", _unclassified_failure)` (the function is removed in Phase 3)
- `tests/unit/test_cli_generation.py:507`: `monkeypatch.setattr("sysml_codegen.cli._clear_output_directory", record_clear)`
- `tests/conformance/test_public_package_oracle.py:55` and `:66`: reads `cli._get_template_env`, then `monkeypatch.setattr(cli, '_get_template_env', changed_environment)`
- `tests/conformance/test_public_diagnostic_totality.py:471-473`: `monkeypatch.setattr(cli_module, "_generate_package_from_graph", …)` (removed in Phase 3)
- **Not in the design:** `tests/conformance/test_public_authority_switch.py:483`: `monkeypatch.setattr(cli, "_check_duplicate_output_paths", refuse)`

## 3. Callers of `_generate_package_from_graph` (R2-4)

- `tests/unit/test_cli_generation.py:348, 366, 381, 475, 490` (direct calls) and `:466` (patch)
- `tests/conformance/test_constraint_catalog_totality.py:110, 140, 269`
- `tests/conformance/test_coverage_preflight.py:67`
- `tests/conformance/test_public_diagnostic_totality.py:471-473` (patch)

## 4. Tests that drive a writer directly with a graph a preflight would refuse (D14, move to `prepare_graph` in Phase 5)

- `tests/unit/test_cli_generation.py::test_unsafe_graph_rejected_before_writer_io` (`:283-307`): each of the nine `GRAPH_AWARE_WRITERS` (`:270-281`) with an unsafe constraint-name graph; asserts the writer raises `CodeGenerationError` with a name-safety violation and the tree is unchanged. This is exactly the re-check D14 drops.
- `tests/unit/test_cli_generation.py::test_missing_catalog_rejected_before_writer_io` (`:310-…`): the same nine writers on a graph whose catalog was removed.

The other direct writer drivers pass graphs every preflight accepts and are only import churn: `test_constraint_generation_integration.py:176-190`, `test_exact_route_generated_package.py:52-60`, `test_zero_entry_package_golden.py:90-98`, `test_module_kind_faildloud.py:339` (a constraint-module graph the stencil loop skips), `test_stencils.py:578`, `test_exact_route_seal_step9.py:168`, `test_entry_point_generation.py:46-48`.

## 5. Tests that assert on the count or level of log records (risk table, Phase 8)

None asserts `len(caplog.records)` over every record. These read every message, so new INFO or WARNING report lines could change what they see:

- `tests/conformance/test_generation_exit_type_preflight.py:250-251`: `message.count("EXIT_POINT_TYPE_UNSUPPORTED") == 1` over every record. A report line that names the refusal code (a disagreement line) would make the count 2.
- `tests/unit/test_warning_reconciliation_exact_route.py:44` and `tests/unit/test_hygiene_tail_registry.py:26`: collect every message at WARNING or above and compare. A screen line at WARNING would join them; screen lines are INFO by D5, but the D17 guard's WARNING line is not.
- `tests/unit/test_cli_generation.py:350-351, 368-369`: filter by text ("name-safety violation") and require exactly one record.
- `tests/conformance/test_public_diagnostic_totality.py` (21 `caplog.text` reads), `test_public_authority_switch.py` (6), `test_extraction_diagnostic_screen.py` (6), `test_finite_generation_boundary.py` (4), `test_constraint_catalog_totality.py` (2), `test_public_handwritten_preservation.py` (2), `test_snapshot_v5_gate.py` (1): substring checks over `caplog.text`; they break only if a report line contains text a test says must be absent.
- The 2a harness's one-refusal-record rule (`tests/helpers/subset_profile/observe.py:238-241`) counts only records carrying a `refusal` extra.

## 6. Site account rows whose IDs change in Phase 2

The 16 `sysml_codegen/cli/__init__.py::…` rows (account file lines 15-30), in `_get_python_path`, `_raw_source_name`, `_check_duplicate_output_paths` (2), `_preflight_generation_metadata` (2), `_preflight_registry_class_names`, `_preflight_constraint_totality` (6) and `_preflight_coverage_account` (3). IDs are also cited in `tests/expectations/subset_profile/mutations.json`, `tests/conformance/subset_profile/test_mutator.py:244` and three case files (`output-naming__module_path_collision.json`, `output-naming__schema_path_collision.json`, `output-naming__registry_class_collision.json`).

## 7. Mentions in comments and docstrings

`tests/runtime/pipeline_runner.py:117`, `tests/conformance/test_smart_regen_behavior.py:23`, `tests/conformance/test_constraint_generation_integration.py:3, 5`, `tests/conformance/test_coverage_preflight.py:4, 62`, `tests/conformance/test_constraint_catalog_totality.py:252`, `tests/conformance/test_public_authority_switch.py:469-470`, `tests/conformance/test_module_kind_faildloud.py:328`, `tests/unit/test_stencils.py:550, 635`, `tests/unit/test_aggregation_generation.py:418`.

## 8. Tests that read `cli/__init__.py` as source text

Neither is in the design's lists. Both keep passing after a move without checking anything, so each must be pointed at the module that now holds the code.

- `tests/conformance/test_generation_boundary.py:175-200` (`test_cli_generates_without_extraction_in_generation`): parses `cli/__init__.py` and checks that no `_generate*` function imports from `extraction` or `analysis`. After Phase 2 the writers live in `cli/emit.py`, so the test must parse that file (it would find no `_generate*` function in `__init__.py` and pass vacuously).
- `tests/unit/test_elaboration_import_boundaries.py:322-328`: requires `cli/__init__.py`'s text to name `build_exact_pipeline_context` and `build_exact_pipeline_context_from_snapshot`. Phase 3 moves construction into `cli/prepare.py`; the test must read the file where the CLI now constructs.
