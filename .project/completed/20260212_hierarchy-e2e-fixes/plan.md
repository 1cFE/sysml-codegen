# Implementation Plan: Hierarchy E2E Fixes

**Status:** Complete
**Created:** 2026-02-12 06:15 UTC
**Last Updated:** 2026-02-12 06:15 UTC

## Source Documents
- **Spec:** `.project/active/hierarchy-e2e-fixes/spec.md`
- **Design:** `.project/active/hierarchy-e2e-fixes/design.md` — See here for component details, code snippets, integration analysis

## Implementation Strategy

**Phasing Rationale:**
Three phases, ordered by dependency chain and impact. Phase 1 fixes the core AST dispatch bug affecting all 20 aggregation expressions (3 functions, 2 files). Phase 2 adds the data-flow field needed for all-singleton assembly scoping. Phase 3 adds alias enrichment, which only matters once scoped aggregation modules exist.

All 5 fixes are pure corrections — no new features, no API changes. The existing E2E tests in `test_hierarchy_e2e.py` serve as acceptance criteria. No new test files needed; existing 69 unit tests catch regressions.

**Overall Validation Approach:**
- Unit tests after each phase to catch regressions immediately
- E2E tests after Phase 1 and Phase 3 to verify acceptance criteria
- Full suite at the end

---

## Phase 1: AST Dispatch Fixes (FR-2, FR-1, FR-3)

### Goal
Fix type dispatch ordering in `reconstruct_expression()`, `_unwrap_invocation()`, and `_walk_aggregation_ast()` so that `FeatureChainExpression` and `FeatureReferenceExpression` nodes are handled before the generic `hasattr(node, "function")` check. This is the highest-impact change — it fixes all 20 aggregation expressions and unblocks 2 of the 4 failing E2E tests.

### Changes Required

**See `design.md#fix-1-fr-2`, `design.md#fix-2-fr-1`, `design.md#fix-3-fr-3` for full code and rationale.**

#### 1. FR-2: Reorder checks in `reconstruct_expression()`
**File:** `src/sysml_codegen/extraction/expression_utils.py:44-58`
- [x] Move `FeatureReferenceExpression` check (line 54-55) to after the `OperatorExpression` check (line 44-45)
- [x] Move `FeatureChainExpression` check (line 57-58) to after the new `FeatureReferenceExpression` position
- [x] `hasattr(expr_node, "function")` block (line 47-52) is now 4th instead of 2nd
- [x] No logic changes inside any block

#### 2. FR-1: Add type guards to `_unwrap_invocation()`
**File:** `src/sysml_codegen/extraction/hierarchy_resolver.py:278-298`
- [x] Add `if SysideAdapter.is_instance(node, "FeatureChainExpression"): return node` after depth check
- [x] Add `if SysideAdapter.is_instance(node, "FeatureReferenceExpression"): return node` after FeatureChain check
- [x] Existing `hasattr(node, "function")` block stays below the new guards

#### 3. FR-3: Relocate handlers in `_walk_aggregation_ast()`
**File:** `src/sysml_codegen/extraction/hierarchy_resolver.py:301-429`
- [x] Move FeatureChainExpression handler (lines 406-411) to between OperatorExpression block (ends line 344) and `hasattr(node, "function")` block (line 347)
- [x] Move FeatureReferenceExpression handler (lines 413-417) to after the relocated FeatureChainExpression block
- [x] Delete the original blocks at their old positions (now dead code)
- [x] Preserve all handler logic exactly as-is — only position changes

### Validation

**Automated:**
- [x] `uv run pytest tests/unit/test_hierarchy_resolver.py -v` — all existing tests pass (including `TestReconstructExpressionInvocation`, `TestWalkAggregationAstEvaluationUnwrap`)
- [x] `uv run pytest tests/unit/ -v` — full unit suite, no regressions
- [x] `uv run pytest tests/integration/test_hierarchy_e2e.py -k "no_unsupported or sum_terms" -v` — both BF-1 tests pass

**What We Know Works After This Phase:**
- All 20 aggregation expressions have `has_unsupported_nodes=False`
- `sum_terms` contain real part names (`pv_module`, `inverter`, `battery_pack`)
- `singleton_terms` and `local_terms` correctly classified
- No `"Evaluation"` artifacts in `transformed_expression`
- `test_bf1_no_unsupported_nodes` — PASS
- `test_bf1_sum_terms_have_real_names` — PASS

---

## Phase 2: Singleton Scoping (FR-4)

### Goal
Add `part_usage_names` field to `HierarchyExtractionResult` so that `_scope_aggregation_expressions()` Strategy 2 can discover all-singleton assemblies (Site Infrastructure, Solar Battery Plant) that have zero multiplicity children.

### Changes Required

**See `design.md#fix-4-fr-4` for full code, field definition, and before/after comparisons.**

#### 1. Add field to data model
**File:** `src/sysml_codegen/extraction/data_models.py:331-338`
- [x] Add `part_usage_names: dict[str, set[str]] = field(default_factory=dict)` to `HierarchyExtractionResult`

#### 2. Populate field during extraction
**File:** `src/sysml_codegen/extraction/hierarchy_resolver.py:483-541`
- [x] In `extract_hierarchy_data()`, add `part_usage_names` dict before the main loop
- [x] Inside the `for part_def in ...` loop body, scan `owned_members` for PartUsage elements and collect names into the dict
- [x] Pass `part_usage_names` to the `HierarchyExtractionResult` constructor

#### 3. Widen Strategy 2 data source
**File:** `src/sysml_codegen/generation/initialization.py:332-337`
- [x] Replace `hierarchy_data.multiplicities` filter with `hierarchy_data.part_usage_names.get(agg_expr.owning_part_qn, set())`
- [x] Rest of Strategy 2 logic (child-walk matching) unchanged

### Validation

**Automated:**
- [x] `uv run pytest tests/unit/test_hierarchy_pipeline.py -v` — all scoping tests pass (including `TestScopeAggregationSiteInfra`)
- [x] `uv run pytest tests/unit/test_hierarchy_resolver.py -k "extraction_result" -v` — construction test passes with new field
- [x] `uv run pytest tests/unit/ -v` — full unit suite, no regressions

**What We Know Works After This Phase:**
- `_scope_aggregation_expressions()` produces ScopedAggregationData for Site Infrastructure and Solar Battery Plant
- All assemblies (Solar Array, Battery System, Site Infrastructure, Solar Battery Plant) appear in scoped aggregation data
- `test_bf6_all_assemblies_scoped` remains PASS (was already passing but now covers more assemblies)

---

## Phase 3: Alias Enrichment (FR-5) + Full Validation

### Goal
Add `_enrich_aliases_from_bindings()` to populate aggregation aliases from CalcUsage binding parameter names. Run full E2E and regression validation.

### Changes Required

**See `design.md#fix-5-fr-5` for full function implementation and call site placement.**

#### 1. Add enrichment function
**File:** `src/sysml_codegen/generation/initialization.py`
- [x] Add `_enrich_aliases_from_bindings(hierarchy_data, calc_usages)` function (see design.md for implementation)
- [x] Key detail: extract leaf name from `source_path` using `rsplit("::", 1)[-1]` for REFERENCE bindings and `rsplit(".", 1)[-1]` for CHAIN bindings

#### 2. Wire into pipeline orchestration
**File:** `src/sysml_codegen/generation/initialization.py:416-420`
- [x] Add call to `_enrich_aliases_from_bindings()` between Step 3.5 (line 419) and Step 4 (line 422)
- [x] Add logging: `logger.info("Step 3.6: Enriched %d aggregation alias(es)...", alias_count)`

### Validation

**Automated — targeted:**
- [x] `uv run pytest tests/unit/test_hierarchy_pipeline.py -v` — no regressions in pipeline tests
- [x] `uv run pytest tests/integration/test_hierarchy_e2e.py -v` — **all 10 tests pass**

**Automated — full regression:**
- [x] `uv run pytest tests/ -v` — entire test suite passes with zero regressions

**What We Know Works After This Phase:**
- `test_bf7_aliases_extracted` — PASS: `"total_capex"` in `agg.aliases` for Solar Battery Plant's `capital_cost`
- `test_bf7_total_capex_wired_to_module_output` — PASS: `annualized_financial.total_capex` wires to `module_output`
- All 10 E2E tests pass (4 previously failing now pass, 6 previously passing remain)
- All existing unit tests pass (zero regressions)
- No `"Evaluation"` string artifacts in pipeline output

---

## Risk Management

**See `design.md#potential-risks` for detailed risk analysis.**

**Phase-Specific Mitigations:**
- **Phase 1**: Run `test_hierarchy_resolver.py` immediately after edits — the mock-based `TestReconstructExpressionInvocation` and `TestWalkAggregationAstEvaluationUnwrap` classes validate the dispatch logic with synthetic mocks. If any fail, the reorder broke mock expectations and needs investigation before proceeding.
- **Phase 2**: The `field(default_factory=dict)` default on `part_usage_names` ensures backward compatibility. Existing tests that construct `HierarchyExtractionResult` without the new field will continue to work.
- **Phase 3**: The leaf extraction logic (`rsplit("::", 1)[-1]`) is the only new algorithmic code. If it produces false-positive aliases, the E2E tests will catch it via incorrect wiring.

## Implementation Notes

### Phase 1 Completion
**Completed:** 2026-02-12
**Actual Changes:**
- Modified `expression_utils.py:44-58`: Moved FeatureReferenceExpression and FeatureChainExpression checks before hasattr(function) check
- Modified `hierarchy_resolver.py:278-302`: Added SysideAdapter.is_instance() guards for FeatureChainExpression and FeatureReferenceExpression in _unwrap_invocation()
- Modified `hierarchy_resolver.py:305-433`: Relocated FeatureChainExpression and FeatureReferenceExpression handlers before hasattr(function) block, removed original dead code

**Issues:** None
**Deviations:** None. All 407 unit tests pass after Phase 1.

### Phase 2 Completion
**Completed:** 2026-02-12
**Actual Changes:**
- Modified `data_models.py:330-339`: Added `part_usage_names: dict[str, set[str]] = field(default_factory=dict)` to HierarchyExtractionResult
- Modified `hierarchy_resolver.py:500-555`: Added part_usage_names collection in extract_hierarchy_data() main loop, passed to constructor
- Modified `initialization.py:332-337`: Replaced multiplicities filter with part_usage_names.get() in Strategy 2
- Modified `tests/unit/test_hierarchy_pipeline.py`: Updated _make_hierarchy() helper to accept part_usage_names; updated 5 tests to supply part_usage_names matching their multiplicity fixtures

**Issues:** 5 unit tests failed initially because they constructed HierarchyExtractionResult with multiplicities but no part_usage_names. Strategy 2 now uses part_usage_names, so the test fixtures needed updating.
**Deviations:** Test fixture updates needed (expected per design risk table).

### Phase 3 Completion
**Completed:** 2026-02-12
**Actual Changes:**
- Modified `initialization.py`: Added AggregationExpressionData import, added _enrich_aliases_from_bindings() function (44 lines), wired Step 3.6 call between Step 3.5 and Step 4
- Modified `tests/integration/test_computed_attributes_e2e.py:241`: Updated impl count from 16 to 36 (20 new aggregation module impls)
- Modified `tests/integration/test_expression_compilation_e2e.py:148`: Updated impl count from 16 to 36

**Issues:** 2 integration tests (test_impl_count_includes_computed_attr, test_auto_implementation_count) expected 16 impl files but pipeline now correctly generates 36 (15 CalcDefs + 1 computed attr + 20 aggregation modules for 4 assemblies x 5 cost attributes). Updated counts.
**Deviations:** None from the fix design. Count updates are a natural consequence of correct aggregation module generation.

### Final Validation
- 407 unit tests pass
- 10/10 E2E hierarchy tests pass (4 previously failing now pass)
- 495 total tests pass, 0 failures

---

**Status**: Complete
