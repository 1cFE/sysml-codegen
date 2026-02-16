# Spec: Cut-over, Cleanup, and E2E Validation

**Status:** Complete
**Owner:** Reid Westwood
**Created:** 2026-02-14 20:45 UTC
**Complexity:** HIGH
**Branch:** cost-pattern
**Epic:** `.project/backlog/epic_output_registry_backtracker_redesign.md` (Item 4)

---

## Business Goals

### Why This Matters

Items 1-3 built and validated the OutputRegistry as a drop-in replacement for the backtracker's 5 ad-hoc indexes and 7-strategy cascade. Parallel validation on all 4 test models (215+ bindings) achieved zero divergences -- the new single-lookup resolution produces identical results to the old cascade. But the old code is still the authoritative path: both paths run on every binding, the old indexes still exist in the constructor, and Bug 2 remains unfixed in production pipeline output.

Item 4 completes the cut-over. The new registry path becomes sole, the old code is removed, 39 tests are migrated to test the new API, the graph builder stops building its own parallel output catalog, and E2E validation confirms Bug 2 is fixed and all models generate correct pipeline YAML. This is the final deliverable of the OutputRegistry epic.

### Success Criteria

- [ ] Old backtracker indexes completely removed (zero references to `_computed_attr_index`, `_aggregation_output_index`, `_output_catalog`, `_design_attr_binding_index`)
- [ ] `_resolve_binding_to_usage()` 7-strategy cascade removed
- [ ] Graph builder's three output catalog functions replaced with OutputRegistry-backed validation
- [ ] All 39 migrated tests pass against OutputRegistry-based resolution
- [ ] E2E: Pipeline YAML matches baselines for all 4 models (only Bug 2 / Issue 22 improvements)
- [ ] E2E: Bug 2 fixed -- `financial.total_capex` in e2e_attr_expr wired to MODULE_OUTPUT
- [ ] E2E: Issue 22 REFERENCE->aggregation same-scope resolves to MODULE_OUTPUT
- [ ] `uv run pytest tests/` passes (zero regressions)
- [ ] `uv run mypy src/` passes
- [ ] `uv run ruff check src/` passes

### Priority

P0 -- final deliverable of the OutputRegistry Backtracker Redesign epic. Items 1, 2a, 2b, 3 are complete with all gates passed. Parallel validation achieved zero divergences on all 4 models.

---

## Problem Statement

### Current State

- The backtracker runs **dual-path resolution**: both the old cascade (authoritative) and the new registry path (shadow/validation) execute for every binding. Parallel validation logs divergences but old results are used. This architecture was correct for Item 3 validation but is now overhead.
- Five old indexes remain in the backtracker constructor (lines 144-254), each marked `TODO(Item-4)`:
  - `_computed_attr_index` (lines 144-162): FORMULA computed attrs, 3 key patterns each
  - `_aggregation_output_index` (lines 163-205): aggregation outputs + BF-7 aliases, 3+ key patterns
  - `_output_catalog` (lines 232-248): "instance.output" -> CalcUsageData, 2 key patterns
  - `_design_attr_binding_index` (lines 250-254): transitive design attribute resolution
  - `_usage_by_name` (lines 214-230): retained for `find_required_modules()`, only cascade usages removed
- `_resolve_binding_to_usage()` (lines 924-1019): 7-strategy cascade with 12+ lookup attempts
- Inline computed_attr/aggregation checks in `_trace_dependencies()` (lines 459-513): duplicate resolution logic
- `_compare_with_registry()` (lines 755-776) + 3 insertion points (lines 481, 512, 619): parallel validation scaffolding
- `_build_computed_attr_channel()` (lines 642-646): private helper only used by old inline resolution
- Graph builder builds its own output catalog via 3 functions (`_build_output_catalog()`, `_extend_output_catalog_with_computed_attrs()`, `_extend_output_catalog_with_aggregation()`) -- redundant with OutputRegistry
- Bug 2 xfail test (`test_bug2_regression.py`) exists but is still marked `xfail` because old path is authoritative
- 39 tests in `test_backtracker_computed_attrs.py` (19) and `test_backtracker_aggregation.py` (20) access internal indexes that will be removed
- Step 3.6 (`_enrich_aliases_from_bindings()`) is retained but may be dead code -- diagnostic deferred from Item 2b

### Desired Outcome

- `_resolve_binding_via_registry()` (lines 691-753) is the sole resolution path
- All 5 old indexes removed (except `_usage_by_name` retained for `find_required_modules()`)
- Graph builder delegates channel existence checks to OutputRegistry
- 39 tests migrated to test OutputRegistry-based registration and resolution
- Bug 2 xfail removed -- test passes green
- E2E pipeline YAML validated against baselines with only expected improvements
- Step 3.6 status resolved by diagnostic (remove if dead, retain with documentation if live)
- No dead code from old cascade, parallel validation, or Steps 3.6/4.7

---

## Scope

### In Scope

1. **Step 3.6 diagnostic** (~30 min, before any removal work):
   - Build OutputRegistry without Step 3.6 aliases (skip `_enrich_aliases_from_bindings()`)
   - Run parallel validation on all 4 models
   - If zero divergences: Step 3.6 is dead code, remove it
   - If divergences: Step 3.6 covers a real resolution path, retain it with documentation

2. **Remove old backtracker indexes and cascade** (Change 9 completion):
   - Remove `_computed_attr_index` construction (lines 144-162)
   - Remove `_aggregation_output_index` construction (lines 163-205)
   - Remove `_output_catalog` construction (lines 232-248)
   - Remove `_design_attr_binding_index` construction (lines 250-254)
   - Keep `_usage_by_name` (lines 214-230) for `find_required_modules()` (line 330), remove cascade usages only (Strategies 2a, 3)
   - Remove `_resolve_binding_to_usage()` cascade (lines 924-1019)
   - Remove inline computed_attr/aggregation checks in `_trace_dependencies()` (lines 459-513)
   - Remove `_build_computed_attr_channel()` (lines 642-646)
   - Remove `_compare_with_registry()` and 3 insertion points (parallel validation)
   - Make `_resolve_binding_via_registry()` the sole resolution path
   - Make `output_registry` a required parameter (no longer optional)

3. **Migrate 39 tests** (following test_migration_audit.md plan):
   - **24 category (a) registration tests**: Rewrite to use `build_output_registry()` + `registry.resolve()`. Move to `test_output_registry_construction.py` where appropriate.
   - **10 category (b) resolution tests**: Add `output_registry` parameter to backtracker construction. Assertions on `_binding_resolutions` stay the same. Update `is_transitive` expectation in test #19 (`test_colon_colon_binding_to_expose_pure_resolves_transitively`: True -> False).
   - **5 category (c) integration tests**: Add `output_registry` parameter if required. Update trace log expected strings if log labels changed.

4. **Graph builder simplification** (Change 10):
   - Replace `_build_output_catalog()` (line 255), `_extend_output_catalog_with_computed_attrs()` (line 583), and `_extend_output_catalog_with_aggregation()` (line 830) with OutputRegistry-backed channel validation
   - Graph builder receives `OutputRegistry` as a parameter
   - Channel existence checks use `registry.resolve()` instead of catalog lookups
   - Downstream consumers updated: `_build_pipeline_module()`, `_build_attribute_resolution_map()`, `_resolve_aggregation_input_channel()`, `_build_computed_attr_module()`

5. **Bug 2 xfail removal**:
   - Remove `@pytest.mark.xfail(strict=True)` from `test_bug2_regression.py`
   - Test passes green: EXPOSE_PURE `total_capex` resolves to MODULE_OUTPUT via Phase 3 alias

6. **E2E validation**:
   - Full codegen on all 4 models (solar_battery, attr_expr_probe, chain_spike, sample_model)
   - YAML diff against baselines in `tests/fixtures/baseline_yaml/` -- only expected changes (Bug 2 fix, Issue 22 fix)
   - New integration test on Issue 22 fixture (`tests/fixtures/issue22_model/`): REFERENCE->aggregation same-scope resolves to MODULE_OUTPUT
   - Verify no false entry points for values that should be module outputs

7. **Dead code removal**:
   - Step 3.6 `_enrich_aliases_from_bindings()` if diagnostic confirms dead
   - Parallel validation code (`_compare_with_registry()` + insertion points)
   - Any remaining Step 4.7 code (aggregation scoping was consolidated into Step 3.5 in Item 2b)

8. **Quality gates**:
   - `uv run pytest tests/` -- zero regressions
   - `uv run mypy src/` -- no type errors
   - `uv run ruff check src/` -- no lint errors
   - YAML diff against baselines -- only expected changes

### Out of Scope

- New features (expression compiler improvements, Phase 2/3 from expression-aware-codegen concept)
- Performance optimization (OutputRegistry is already O(1) lookup)
- `find_required_modules()` refactoring to use `_usage_by_qualified` instead of `_usage_by_name` (future cleanup, outside this epic's scope)
- Step 3.6 removal if diagnostic finds it covers a real resolution path (retain with documentation)

### Edge Cases & Considerations

- **`_usage_by_name` retention**: Only cascade usages (Strategies 2a, 3 in `_resolve_binding_to_usage()`) are removed. The index itself, its population loop (lines 214-230), and its use in `find_required_modules()` (line 330) are all retained. The existing `TODO(Item-4)` annotation at line 214 SHOULD be updated to indicate cascade usage removed, `find_required_modules()` usage retained, mark for future cleanup.

- **`is_transitive` behavioral change**: After cut-over, `is_transitive` on `BindingResolution` will always be `False`. Phase 4 transitive aliases resolve within the registry, making the chain invisible to the backtracker. This field is not consumed by downstream logic (graph builder, generation) -- only trace logging. Test #19 in computed attrs (`test_colon_colon_binding_to_expose_pure_resolves_transitively`) MUST update its assertion from `True` to `False`.

- **Graph builder `output_catalog` downstream consumers**: The output catalog is consumed by 4 methods in the graph builder: `_build_pipeline_module()`, `_build_attribute_resolution_map()`, `_resolve_aggregation_input_channel()`, and `_build_computed_attr_module()`. Each performs channel existence/lookup via `catalog.get(key)` returning `(module_type, channel_name, field_name)` tuples. The migration needs to:
  - Provide `module_type` via the `calc_def_map` (already available in graph builder)
  - Provide `channel_name` via `registry.resolve(key)` (exact match)
  - Derive `field_name` from channel structure (last `__`-separated segment, or `"root"` for single-output modules)
  - This is the most architecturally significant change in Item 4 -- the catalog tuple `(module_type, channel_name, field_name)` carries three pieces of information while `registry.resolve()` returns only the channel name. Design MUST address how module_type and field_name are provided.

- **Trace log changes**: The old inline resolution produces trace log entries with labels like `COMPUTED_ATTR` and `AGGREGATION`. After cut-over, these specific labels may not exist if the new path uses different logging. The 2 trace log tests (test #14 computed attrs, test #11 aggregation) need updated expected strings or removal.

- **Step 3.6 diagnostic false negative risk**: The diagnostic builds the registry without Step 3.6 aliases and checks for divergences. A false negative (zero divergences despite Step 3.6 being live) could occur if Step 3.6 aliases are redundant with other registration phases. This is acceptable -- if redundant, they're safe to remove. The risk is a false positive (divergence from a non-Step-3.6 cause), which is mitigated by the fact that parallel validation already passes with Step 3.6 present.

- **Bug 2 xfail test**: The xfail is `strict=True`, meaning if the test unexpectedly passes, pytest reports it as a failure. Once the old path is removed and the registry path becomes authoritative, the xfail must be removed in the same commit that completes the cut-over, or the test suite will fail.

---

## Requirements

### Functional Requirements

> Requirements below are from the epic Item 4 definition and user's Q&A responses unless marked [INFERRED].

1. **FR-1**: A Step 3.6 diagnostic MUST be run before any dead code removal. The diagnostic MUST build the OutputRegistry without Step 3.6 aliases and run parallel validation on all 4 models. If zero divergences, Step 3.6 is dead code and MUST be removed. If divergences, Step 3.6 MUST be retained with documentation explaining which resolution paths it covers.

2. **FR-2**: The backtracker's `_computed_attr_index`, `_aggregation_output_index`, `_output_catalog`, and `_design_attr_binding_index` MUST be removed along with their construction code. The `_usage_by_name` index MUST be retained for `find_required_modules()`.

3. **FR-3**: The `_resolve_binding_to_usage()` 7-strategy cascade (lines 924-1019) MUST be removed entirely.

4. **FR-4**: The inline computed_attr/aggregation checks in `_trace_dependencies()` (lines 459-513) MUST be removed. `_resolve_binding_via_registry()` becomes the sole resolution path for CHAIN and REFERENCE bindings.

5. **FR-5**: The parallel validation code (`_compare_with_registry()` and its 3 insertion points) MUST be removed. The `output_registry` parameter on `DependencyBacktracker` MUST become required (not optional).

6. **FR-6**: The `_build_computed_attr_channel()` private method MUST be removed.

7. **FR-7**: All 39 tests accessing internal indexes MUST be migrated following the test_migration_audit.md plan:
   - 24 category (a) tests rewritten to use `build_output_registry()` + `registry.resolve()`
   - 10 category (b) tests updated with `output_registry` parameter, same `_binding_resolutions` assertions
   - 5 category (c) tests updated with `output_registry` parameter and adjusted trace log expectations

8. **FR-8**: The graph builder MUST receive an `OutputRegistry` parameter. The three output catalog functions (`_build_output_catalog()`, `_extend_output_catalog_with_computed_attrs()`, `_extend_output_catalog_with_aggregation()`) MUST be replaced with OutputRegistry-backed channel validation.

9. **FR-9**: [INFERRED] The graph builder's downstream consumers (`_build_pipeline_module()`, `_build_attribute_resolution_map()`, `_resolve_aggregation_input_channel()`, `_build_computed_attr_module()`) MUST be updated to derive `module_type`, `channel_name`, and `field_name` from the OutputRegistry and calc_def_map instead of the removed output catalog.

10. **FR-10**: The `@pytest.mark.xfail(strict=True)` on `test_bug2_regression.py` MUST be removed. The test MUST pass green.

11. **FR-11**: E2E validation MUST run full codegen on all 4 models and diff generated pipeline YAML against baselines in `tests/fixtures/baseline_yaml/`. Only expected changes (Bug 2 fix, Issue 22 fix) SHOULD appear.

12. **FR-12**: A new integration test MUST be created for the Issue 22 fixture (`tests/fixtures/issue22_model/`). The test MUST run full codegen and assert the REFERENCE->aggregation same-scope binding resolves to MODULE_OUTPUT.

13. **FR-13**: [INFERRED] After all removals, `uv run mypy src/` and `uv run ruff check src/` MUST pass with no new errors.

---

## Acceptance Criteria

### Step 3.6 Diagnostic
- [ ] Diagnostic builds registry without Step 3.6 aliases
- [ ] Parallel validation run on all 4 models with Step-3.6-free registry
- [ ] Decision documented: remove (zero divergences) or retain (divergences found)
- [ ] If removed: `_enrich_aliases_from_bindings()` deleted, call site in `build_pipeline_context()` removed
- [ ] If retained: documented which bindings depend on Step 3.6 aliases

### Backtracker Cleanup
- [ ] Zero references to `_computed_attr_index` in production code
- [ ] Zero references to `_aggregation_output_index` in production code
- [ ] Zero references to `_output_catalog` in production code
- [ ] Zero references to `_design_attr_binding_index` in production code
- [ ] `_usage_by_name` retained for `find_required_modules()` only, TODO annotation updated
- [ ] `_resolve_binding_to_usage()` removed
- [ ] `_build_computed_attr_channel()` removed
- [ ] Inline computed_attr/aggregation checks in `_trace_dependencies()` removed
- [ ] `_compare_with_registry()` and 3 insertion points removed
- [ ] `_resolve_binding_via_registry()` is the sole resolution path
- [ ] `output_registry` is a required parameter (not optional)

### Test Migration
- [ ] 24 category (a) registration tests rewritten with `registry.resolve()` assertions
- [ ] 10 category (b) resolution tests updated with `output_registry` parameter
- [ ] 5 category (c) integration tests updated (trace log strings, `output_registry` param)
- [ ] `is_transitive` assertion updated in `test_colon_colon_binding_to_expose_pure_resolves_transitively` (True -> False)
- [ ] All 39 migrated tests pass

### Graph Builder Simplification
- [ ] `_build_output_catalog()` removed
- [ ] `_extend_output_catalog_with_computed_attrs()` removed
- [ ] `_extend_output_catalog_with_aggregation()` removed
- [ ] `build_computation_graph()` accepts `OutputRegistry` parameter
- [ ] Downstream consumers derive module_type, channel_name, field_name from registry + calc_def_map
- [ ] Graph builder tests pass (zero regressions)

### Bug 2 Fix
- [ ] `@pytest.mark.xfail(strict=True)` removed from `test_bug2_regression.py`
- [ ] Test passes green: EXPOSE_PURE `total_capex` resolves to MODULE_OUTPUT

### E2E Validation
- [ ] Full codegen on solar_battery produces pipeline YAML matching baseline (or improved)
- [ ] Full codegen on attr_expr_probe: `financial.total_capex` wired to MODULE_OUTPUT (Bug 2 fix)
- [ ] Full codegen on chain_spike produces pipeline YAML matching baseline
- [ ] Full codegen on sample_model produces pipeline YAML matching baseline
- [ ] Issue 22 integration test: REFERENCE->aggregation same-scope resolves to MODULE_OUTPUT
- [ ] YAML diff against baselines shows only expected changes
- [ ] No false entry points for values that should be module outputs

### Quality & Integration
- [ ] `uv run pytest tests/` passes (zero regressions across full test suite)
- [ ] `uv run mypy src/` passes (no new type errors)
- [ ] `uv run ruff check src/` passes (no lint errors)
- [ ] No dead code from old cascade, parallel validation, Steps 3.6/4.7

---

## Implementation Notes

### Recommended Sub-task Ordering

The following ordering minimizes risk by validating each change before proceeding:

1. **Step 3.6 diagnostic** -- resolve the open question first (~30 min)
2. **Test migration: category (a)** -- rewrite 24 registration tests to use `registry.resolve()`. This validates that the registry covers all key patterns the old indexes covered. Run `pytest` to confirm.
3. **Test migration: category (b)** -- update 10 resolution tests with `output_registry` param. Same `_binding_resolutions` outcomes. Run `pytest`.
4. **Test migration: category (c)** -- update 5 integration tests. Run `pytest`.
5. **Backtracker cut-over** -- remove old indexes, cascade, inline checks, parallel validation. Make `_resolve_binding_via_registry()` sole path. Make `output_registry` required. Run `pytest`.
6. **Bug 2 xfail removal** -- must happen in same commit as or after backtracker cut-over. Run `pytest`.
7. **Graph builder simplification** -- replace 3 output catalog functions with OutputRegistry. Run `pytest`.
8. **E2E validation** -- full codegen on all 4 models + Issue 22, YAML diff against baselines.
9. **Dead code cleanup** -- remove Step 3.6 if diagnostic passed, remove any remaining parallel validation artifacts, Step 4.7 remnants.
10. **Quality gate** -- `pytest`, `mypy`, `ruff check`.

### Graph Builder Migration: The `(module_type, channel_name, field_name)` Problem

The current output catalog returns `(module_type, channel_name, field_name)` tuples. The OutputRegistry's `resolve()` returns only a channel name string. The graph builder needs all three values.

**Recommended approach**: Create a thin adapter or helper that, given a key:
- Gets `channel_name` from `registry.resolve(key)`
- Derives `module_type` from `calc_def_map` (lookup the producing CalcDef's qualified name, derive PascalCase type)
- Derives `field_name` from the channel name structure: for single-output modules it's `"root"`, for multi-output it's the last `__`-separated segment of the channel name (matching the output attribute name)

This keeps the OutputRegistry clean (single-responsibility: key -> channel resolution) while providing the graph builder with the richer information it needs. The exact design should be worked out in the design phase.

### Backtracker `_trace_dependencies()` Simplification

After removing inline computed_attr/aggregation checks (lines 459-513) and the cascade call, `_trace_dependencies()` simplifies to:

1. LITERAL/UNBOUND -> ENTRY_POINT (fast path, unchanged)
2. CHAIN/REFERENCE with source_path -> `_resolve_binding_via_registry()` (sole path)
3. Self-reference guard (adapted for channel-name-based resolution, already implemented in Item 3)
4. If resolved: MODULE_OUTPUT with channel name
5. If not resolved: `_resolve_to_design_attribute()` -> ENTRY_POINT

The ~55 lines of inline computed_attr/aggregation checks and ~95 lines of cascade are replaced by a single call to `_resolve_binding_via_registry()`.

### Files Affected

| File | Change Type | Description |
|------|------------|-------------|
| `src/sysml_codegen/analysis/dependency_backtracker.py` | Major modification | Remove 4 indexes, cascade, inline checks, parallel validation; sole registry path |
| `src/sysml_codegen/resolution/graph_builder.py` | Major modification | Remove 3 output catalog functions, accept OutputRegistry, update 4 downstream consumers |
| `src/sysml_codegen/generation/initialization.py` | Minor modification | Remove Step 3.6 if diagnostic passes; `output_registry` required in backtracker call |
| `tests/unit/test_backtracker_computed_attrs.py` | Major modification | Migrate 19 tests (11 registration, 6 resolution, 2 integration) |
| `tests/unit/test_backtracker_aggregation.py` | Major modification | Migrate 20 tests (13 registration, 4 resolution, 3 integration) |
| `tests/unit/test_output_registry_construction.py` | Minor modification | Receive relocated category (a) tests if appropriate |
| `tests/integration/test_bug2_regression.py` | Minor modification | Remove xfail marker |
| `tests/integration/test_e2e_output_registry.py` | New | E2E validation tests (4 models + Issue 22, YAML diff) |

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_output_registry_backtracker_redesign.md`
- **Item 3 spec:** `.project/active/backtracker-integration/spec.md`
- **Item 3 design:** `.project/active/backtracker-integration/design.md`
- **Test migration audit:** `.project/active/backtracker-integration/test_migration_audit.md`
- **Design basis:** `.project/reports/08_algorithm_revised.md` (Sections 12, 14)
- **Item 1 code:** `src/sysml_codegen/core/output_registry.py`, `src/sysml_codegen/core/models.py`
- **Item 3 code:** `src/sysml_codegen/generation/initialization.py` (`build_output_registry()`), `src/sysml_codegen/analysis/dependency_backtracker.py` (`_resolve_binding_via_registry()`)
- **Baseline YAML:** `tests/fixtures/baseline_yaml/` (4 models)
- **Bug 2 xfail:** `tests/integration/test_bug2_regression.py`
- **Issue 22 fixture:** `tests/fixtures/issue22_model/`
- **Parallel validation:** `tests/integration/test_parallel_validation.py` (8 tests, zero divergences)

---

## Deliverables

| File | Type | Description |
|------|------|-------------|
| `src/sysml_codegen/analysis/dependency_backtracker.py` | Modified | Old indexes removed, sole registry path |
| `src/sysml_codegen/resolution/graph_builder.py` | Modified | OutputRegistry-backed channel validation |
| `src/sysml_codegen/generation/initialization.py` | Modified | Step 3.6 removed (if diagnostic passes), required registry |
| `tests/unit/test_backtracker_computed_attrs.py` | Modified | 19 tests migrated |
| `tests/unit/test_backtracker_aggregation.py` | Modified | 20 tests migrated |
| `tests/integration/test_bug2_regression.py` | Modified | xfail removed |
| `tests/integration/test_e2e_output_registry.py` | New | E2E validation (4 models + Issue 22, YAML diff) |

---

**Next Steps:** After approval, proceed to `/_my_design`
