# Spec: Codegen Runtime Gap Fixes

**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-02-01T21:57:00Z
**Complexity:** MEDIUM
**Branch:** 1cfe_dev

---

## Business Goals

### Why This Matters

Generated codegen output MUST be directly executable by TEAx without manual workarounds. The codegen-chain-spike (Item 2 of the end-to-end pipeline derisking epic) revealed three gaps that prevent `execute_pipeline()` from running on generated output. Each gap requires hand-editing generated files, which:

1. Defeats the purpose of automated code generation
2. Will recur for every model run through codegen (including the solar+battery pipeline)
3. Blocks Items 4-5 of the derisking epic (codegen pipeline run + TEAx end-to-end execution)

### Success Criteria

- [ ] `sysml-codegen generate` on the chain spike model produces output that executes via `execute_pipeline()` without manual intervention
- [ ] `design_params.json` is populated with correct default values from the SysML model
- [ ] Exit point types (`RootModel[float]`) are registered in `CUSTOM_SCHEMA_TYPES`
- [ ] No static `FusionParams` schema is copied into generated packages
- [ ] All existing tests continue to pass
- [ ] New tests verify each fix and the end-to-end flow

### Priority

P0 — blocking Items 4-5 of the end-to-end pipeline derisking epic (`epic-end-to-end-pipeline-derisking.md`).

---

## Problem Statement

### Current State

The codegen pipeline (`sysml-codegen generate`) produces structurally correct output (right files, right wiring), but the output cannot be executed by TEAx without three manual workarounds:

1. **Empty JSON**: `design_params.json` is generated as `{}` because design attribute extraction filters out all models not under `models/designs/`
2. **Missing handler**: TEAx's output router has no handler for `RootModel[float]` because exit point types are never registered in `CUSTOM_SCHEMA_TYPES`
3. **Stale template**: A hardcoded `FusionParams` schema is copied into every package regardless of the model domain

### Desired Outcome

Running `sysml-codegen generate` on any valid SysML model produces output that TEAx can execute directly. The generated `design_params.json` contains correct defaults, the registry includes all necessary type registrations, and no domain-specific artifacts leak into unrelated packages.

---

## Scope

### In Scope

- Fix default value extraction path filter (Gap 1 primary)
- Add crash guard for OperatorExpression evaluation (Gap 1 secondary)
- Register exit point types in CUSTOM_SCHEMA_TYPES (Gap 2)
- Remove static FusionParams template (Gap 3)
- Unit tests for each fix
- Integration test verifying end-to-end codegen correctness
- Copy chain spike SysML model into `tests/fixtures/` as self-contained test fixture

### Out of Scope

- Changes to `agentic-mbse` repo (validation improvements, Level 8 extractability check)
- Strategy 1 qualified name matching fix in `graph_builder.py` (safety net works correctly)
- TEAx framework changes
- Solar+battery model codegen (Items 4-5 — unblocked by this work)
- CLI flag `--design-path-filter` is in scope (see FR-4)

### Edge Cases & Considerations

- Models with OperatorExpressions in design attributes (e.g., `attribute x : Real = a * 2`) — the crash guard MUST return `None` gracefully, not propagate the error
- Multi-output modules use bare type names (not `RootModel[T]`) for exit points — the fix MUST handle both single-output and multi-output exit point types
- The `_group_entry_points_via_deriver()` safety net at `graph_builder.py:326-336` is the actual mechanism that populates defaults (not Strategy 1 direct matching) — the path filter fix enables this safety net to work by ensuring design attributes are extracted in the first place

---

## Requirements

### Functional Requirements

> Requirements below are from the gap analysis reports and fix plan unless marked [INFERRED].

#### Gap 1: Empty design_params.json

1. **FR-1**: `extract_design_attributes()` in `parameter_groups.py` MUST default to `design_path_filter=""` (accept all files) instead of `"models/designs"`.

2. **FR-2**: `build_pipeline_context()` in `initialization.py` MUST accept an optional `design_path_filter` parameter and pass it through to `extract_design_attributes()`.

3. **FR-3**: `_extract_default_value()` in `parameter_groups.py` MUST NOT crash when `evaluate_true_static_expression()` encounters an OperatorExpression with feature references. It MUST catch `ValueError` and `TypeError` and return `None`.

4. **FR-4**: `GenerationConfig` in `cli/__init__.py` MUST accept a `design_path_filter` field (default `""`). The CLI MUST expose a `--design-path-filter` flag that maps to this field, wired through to `build_pipeline_context()`.

#### Gap 2: Missing RootModel[float] Handler

5. **FR-5**: `generate_registry_function()` in `registry.py` MUST accept exit point type information and include exit point types in the generated `CUSTOM_SCHEMA_TYPES` list.

6. **FR-6**: The `registry_function.py.jinja2` template MUST render exit point types (e.g., the `Float` alias from `primitives.py`) alongside entry point schema types in `CUSTOM_SCHEMA_TYPES`.

7. **FR-7**: The CLI orchestrator (`_generate_registry()` in `cli/__init__.py`) MUST collect unique exit point types from `ComputationGraph` and pass them to `generate_registry_function()`.

8. **FR-8**: [INFERRED] For single-output modules using `RootModel[float]`, the generated code SHOULD import and register the `Float` alias from `primitives.py` rather than trying to register the string `"RootModel[float]"` directly.

#### Gap 3: Static FusionParams Template

9. **FR-9**: The static template file `templates/schemas_ref.py` MUST be deleted.

10. **FR-10**: The `_generate_schemas()` function in `cli/__init__.py` MUST NOT unconditionally copy any static schema template. The copy operation (lines ~138-143) MUST be removed.

#### Test Coverage

11. **FR-11**: Unit tests MUST verify that `extract_design_attributes()` returns attributes with non-None defaults when called with default parameters on a model containing design attributes.

12. **FR-12**: Unit tests MUST verify that `_extract_default_value()` returns `None` (not an exception) for OperatorExpressions containing feature references.

13. **FR-13**: Unit tests MUST verify that generated `CUSTOM_SCHEMA_TYPES` includes exit point type registrations.

14. **FR-14**: Integration tests MUST verify end-to-end codegen produces:
    - Populated `design_params.json` with correct numeric values
    - `CUSTOM_SCHEMA_TYPES` including exit point types
    - No `{package}_schemas.py` file containing `FusionParams`

15. **FR-15**: A chain spike SysML model fixture MUST be added to `tests/fixtures/` so integration tests are self-contained within the sysml-codegen repo (copied from `fusion-tea`).

16. **FR-16**: The existing `test_generates_schemas()` integration test MUST be updated to assert that no static `FusionParams` schema file is generated (rather than checking for its presence).

---

## Acceptance Criteria

### Core Functionality

- [ ] **AC-1 (Gap 1):** Running codegen on the chain spike model produces `design_params.json` with 3 entries: `length=10.0`, `width=5.0`, `rate=12.0`
- [ ] **AC-2 (Gap 1):** Running codegen on a model with OperatorExpression design attributes does not crash; non-extractable values are `None`
- [ ] **AC-3 (Gap 2):** Generated `__init__.py` includes `Float` (or equivalent `RootModel[float]` alias) in `CUSTOM_SCHEMA_TYPES`
- [ ] **AC-4 (Gap 2):** `execute_pipeline()` on generated output does not fail with "ExitPoint output type has no registered write handler"
- [ ] **AC-5 (Gap 3):** No file named `{package}_schemas.py` containing `FusionParams` exists in generated output
- [ ] **AC-6 (Gap 3):** `templates/schemas_ref.py` does not exist in the repo

### Quality & Integration

- [ ] **AC-7:** All existing tests in `tests/` continue to pass (`uv run pytest tests/`)
- [ ] **AC-8:** New unit tests cover each of the three gaps
- [ ] **AC-9:** Integration test runs full codegen and verifies output correctness
- [ ] **AC-10:** `uv run mypy src/` passes
- [ ] **AC-11:** `uv run ruff check src/` passes

---

## Files Affected

| File | Change Type | Gap |
|------|------------|-----|
| `src/sysml_codegen/analysis/parameter_groups.py` | Edit (default filter + crash guard) | 1 |
| `src/sysml_codegen/generation/initialization.py` | Edit (add design_path_filter param) | 1 |
| `src/sysml_codegen/cli/__init__.py` | Edit (GenerationConfig field + wire through + remove schema copy) | 1, 3 |
| `src/sysml_codegen/generation/registry.py` | Edit (accept + pass exit point types) | 2 |
| `src/sysml_codegen/templates/registry_function.py.jinja2` | Edit (render exit point types) | 2 |
| `src/sysml_codegen/templates/schemas_ref.py` | **Delete** | 3 |
| `tests/fixtures/chain_spike_model/` | **New** (test fixture) | Testing |
| `tests/unit/test_parameter_groups.py` | **New** (unit tests for Gap 1) | Testing |
| `tests/unit/test_registry_generation.py` | **New** (unit tests for Gap 2) | Testing |
| `tests/integration/test_full_pipeline.py` | Edit (update schema assertion + add E2E tests) | Testing |

---

## Related Artifacts

- **Research:** `/home/reid/1cfe/fusion-tea/.project/reports/codegen-runtime-gaps-2026-02-01-2047.md`
- **Root Cause:** `/home/reid/1cfe/fusion-tea/.project/research/20260201-210000_codegen-runtime-gaps-root-cause.md`
- **Gap 1 Findings:** `/home/reid/1cfe/fusion-tea/.project/active/gap1-default-value-debug/findings.md`
- **Gap 1 Fix Plan:** `/home/reid/1cfe/fusion-tea/.project/active/gap1-default-value-debug/fix-plan.md`
- **Epic:** `/home/reid/1cfe/fusion-tea/.project/backlog/epic-end-to-end-pipeline-derisking.md` (Item 2)
- **Design:** `.project/active/codegen-runtime-gap-fixes/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_design`
