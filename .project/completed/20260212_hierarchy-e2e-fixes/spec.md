# Spec: Hierarchy E2E Fixes — Probe-Validated AST Dispatch Corrections

**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-02-12 06:04 UTC
**Complexity:** MEDIUM
**Branch:** cost-pattern
**Epic:** COST-PATTERN (Item 5 — E2E validation failures against real SysIDE AST)
**Supersedes:** Portions of `.project/active/hierarchy-bugfix/spec.md` BF-1, BF-6, BF-7 (now probe-validated with revised fixes)

---

## Business Goals

### Why This Matters

Items 1-4 of the COST-PATTERN epic built the hierarchy-aware pipeline with 69 unit tests on synthetic (mock) data. Item 5 E2E validation created `test_hierarchy_e2e.py` with 10 tests across 3 test classes running against the real solar_battery model via SysIDE. 6 tests pass; **4 tests fail**, exposing real gaps where the mock-based bugfixes don't work against the actual SysIDE AST.

Probe scripts run against the live AST revealed a single root architectural flaw: `FeatureReferenceExpression` and `FeatureChainExpression` nodes both carry a `function` attribute with a `.name` property (`"Evaluation"` and `"."` respectively). All code that uses `hasattr(node, "function")` as a proxy for InvocationExpression produces false positives on these types. This affects 3 files across the extraction layer, causing **all 20 aggregation expressions** to be broken (`has_unsupported_nodes=True`, `sum_terms=[]`, `singleton_terms=[]`, `aliases=[]`).

Two additional root causes (singleton assembly scoping and alias detection from CalcUsage bindings) compound the AST dispatch failures. Without these 5 fixes, the COST-PATTERN epic cannot close.

### Success Criteria

- [ ] All 10 tests in `tests/integration/test_hierarchy_e2e.py` pass (currently 6 pass, 4 fail)
- [ ] All 20 aggregation expressions have `has_unsupported_nodes=False`
- [ ] All existing tests pass with zero regressions (`uv run pytest tests/`)
- [ ] No `"Evaluation"` string artifacts in any `transformed_expression` or pipeline YAML output

### Priority

P0. Blocks COST-PATTERN epic closure. All 5 root causes are production code defects validated by probe scripts against the real SysIDE AST.

---

## Problem Statement

### Current State

Running `test_hierarchy_e2e.py` against the solar_battery model via SysIDE produces:

| Test | Status | Root Cause |
|------|--------|------------|
| `test_aggregation_expressions_extracted` | PASS | Baseline |
| `test_bf1_no_unsupported_nodes` | **FAIL** | RC2, RC3 |
| `test_bf1_sum_terms_have_real_names` | **FAIL** | RC1 |
| `test_bf6_all_assemblies_scoped` | PASS | — |
| `test_bf7_aliases_extracted` | **FAIL** | RC5 (+RC4) |
| `test_aggregation_modules_in_graph` | PASS | — |
| `test_bf3_aggregation_wrappers_have_inputs` | PASS | — |
| `test_bf4_bf5_instance_scoped_paths` | PASS | — |
| `test_bf7_total_capex_wired_to_module_output` | **FAIL** | RC4, RC5 |
| `test_aggregation_yaml_no_evaluation_artifacts` | PASS | — |

All 20 aggregation expressions have `has_unsupported_nodes=True`, `sum_terms=[]`, `singleton_terms=[]`, and `aliases=[]`.

### Desired Outcome

All 10 E2E tests pass. Aggregation expressions are correctly decomposed into `SumTerm`, `SingletonTerm`, and `LocalTerm` classifications. Solar Battery Plant's `capital_cost` aggregation has `total_capex` in aliases. `annualized_financial.total_capex` wires to `MODULE_OUTPUT` from the aggregation chain.

---

## Scope

### In Scope

5 bug fixes across 4 source files, all probe-validated against the real SysIDE AST:

1. **RC1** — `_unwrap_invocation()` type guards (`hierarchy_resolver.py`)
2. **RC2** — `reconstruct_expression()` check reorder (`expression_utils.py`)
3. **RC3** — `_walk_aggregation_ast()` block relocation (`hierarchy_resolver.py`)
4. **RC4** — Singleton child extraction for all-singleton assemblies (`data_models.py`, `hierarchy_resolver.py`, `initialization.py`)
5. **RC5** — Alias enrichment from CalcUsage bindings (`initialization.py`)

### Out of Scope

- New feature work (this is purely corrective)
- BF-2 (expression compilation) — already working, not affected by these AST dispatch fixes
- BF-3 (case mismatch lookup) — already fixed, test passes
- BF-4/BF-5 (path fixes) — already fixed, test passes
- BF-8 (multiplicity entry points in parameter groups) — separate concern
- Non-uniform array support
- TEAx runtime validation
- Probe script maintenance

### Edge Cases & Considerations

- **RC1 + RC3 interaction:** RC1 fixes `_unwrap_invocation()` which is called from INSIDE the sum handler in `_walk_aggregation_ast()`. RC3 fixes the top-level dispatch in the same function. Both are needed — RC3 alone does not fix the sum operand unwrapping path.
- **RC2 → RC3 dependency:** `extract_feature_chain_name()` calls `reconstruct_expression()` internally. RC2 MUST be applied before RC3 can produce correct chain names.
- **RC4 data boundary:** `_scope_aggregation_expressions()` is in the generation layer and has NO access to AST elements. The fix MUST extract singleton child names in the extraction layer and pass them via `HierarchyExtractionResult`.
- **RC5 test target:** `test_bf7_aliases_extracted` asserts `"total_capex" in agg.aliases` on extraction-layer `AggregationExpressionData`, NOT on the backtracker index. The fix MUST populate `agg.aliases` on the data model, not just the backtracker's `_aggregation_output_index`.
- **Existing BF-7 backtracker code:** Lines 189-197 of `dependency_backtracker.py` already propagate `agg.expression.aliases` into `_aggregation_output_index`. If RC5 correctly populates `aliases` on the data model, no backtracker changes are needed.

---

## Requirements

### Functional Requirements

> All requirements derived from probe-validated root cause analysis in `.project/reports/05_synthesis_and_fixes.md` and design review UPDATE markers.

#### FR-1: `_unwrap_invocation()` MUST NOT unwrap FeatureChainExpression or FeatureReferenceExpression

**Root Cause:** RC1
**File:** `src/sysml_codegen/extraction/hierarchy_resolver.py:278-298`

`_unwrap_invocation()` MUST use explicit `SysideAdapter.is_instance()` type guards to return early for `FeatureChainExpression` and `FeatureReferenceExpression` nodes, preventing them from being mistaken for InvocationExpression wrappers.

The fix MUST NOT use the `_KNOWN_WRAPPER_FUNCTIONS` name-set filter. `"Evaluation"` is in that set AND is the `function.name` on `FeatureReferenceExpression` — using it creates a fragile name collision where FeatureReferenceExpression nodes with operands would be incorrectly unwrapped.

**Acceptance test:** `test_bf1_sum_terms_have_real_names` — sum terms contain real part names (`pv_module`, `inverter`, `battery_pack`), not AST artifacts.

#### FR-2: `reconstruct_expression()` MUST check specific SysML types BEFORE generic `function.name` check

**Root Cause:** RC2
**File:** `src/sysml_codegen/extraction/expression_utils.py:34-75`

The `FeatureReferenceExpression` and `FeatureChainExpression` type checks (currently at lines 54-58) MUST be relocated before the `hasattr(expr_node, "function")` check (currently at line 47). The generic `function.name` check MUST only fire for genuine `InvocationExpression` nodes (sum, sqrt, etc.).

No logic changes to the individual handlers — only position change.

**Acceptance test:** `test_bf1_no_unsupported_nodes` — no `"Evaluation"` artifacts in any `transformed_expression`.

#### FR-3: `_walk_aggregation_ast()` MUST check FeatureChainExpression/FeatureReferenceExpression before `hasattr(function)` dispatch

**Root Cause:** RC3
**File:** `src/sysml_codegen/extraction/hierarchy_resolver.py:301-429`

The existing `FeatureChainExpression` handler (lines 407-411) and `FeatureReferenceExpression` handler (lines 414-417) MUST be relocated before the `hasattr(node, "function")` check at line 347. The existing handler logic MUST be preserved as-is — no rewrite, only position change.

**Depends on:** FR-2 (because `extract_feature_chain_name()` calls `reconstruct_expression()` internally).

**Acceptance test:** `test_bf1_no_unsupported_nodes` — singleton and local terms correctly classified.

#### FR-4: `HierarchyExtractionResult` MUST include all child PartUsage names (not just multiplicities)

**Root Cause:** RC4
**Files:** `src/sysml_codegen/extraction/data_models.py`, `src/sysml_codegen/extraction/hierarchy_resolver.py`, `src/sysml_codegen/generation/initialization.py`

Three changes:

1. `HierarchyExtractionResult` MUST have a new field `part_usage_names: dict[str, set[str]]` mapping `owning_part_def_qn` to the set of ALL child PartUsage names on that PartDef (both multiplicity and singleton children).

2. `extract_hierarchy_data()` MUST populate `part_usage_names` by scanning `owned_members` for `PartUsage` elements on each `PartDefinition` (alongside existing `extract_multiplicities()` call). This keeps AST iteration in the extraction layer where it belongs.

3. `_scope_aggregation_expressions()` Strategy 2 MUST use `hierarchy_data.part_usage_names.get(agg_expr.owning_part_qn, set())` instead of filtering `hierarchy_data.multiplicities`. This naturally handles assemblies with only singleton children (Site Infrastructure, Solar Battery Plant).

The fix MUST NOT add AST iteration to `_scope_aggregation_expressions()` — that function is in the generation layer and MUST only consume pre-extracted data.

**Acceptance test:** `test_bf7_total_capex_wired_to_module_output` — Solar Battery Plant aggregation modules exist in the graph (prerequisite for wiring).

#### FR-5: Aliases MUST be enriched from CalcUsage bindings before scoping

**Root Cause:** RC5
**File:** `src/sysml_codegen/generation/initialization.py`

A new function `_enrich_aliases_from_bindings(hierarchy_data, calc_usages)` MUST be added and called in `build_pipeline_context()` between Step 3.5 (hierarchy extraction) and Step 4.7 (scoping).

The function MUST:
1. Build a lookup from aggregation `attribute_name` → `AggregationExpressionData` across all `hierarchy_data.aggregation_expressions`
2. Scan `calc_usages` for bindings where `binding.source_path` (bare name, no dots/colons) matches an aggregation `attribute_name`
3. For each match where `binding.param_name != attribute_name`, append `binding.param_name` to the matching aggregation's `.aliases` list
4. Deduplicate aliases (no duplicates if multiple CalcUsages bind the same alias)

The fix MUST NOT modify the extraction layer (`hierarchy_resolver.py`) — it doesn't have CalcUsage data. The fix MUST NOT modify the backtracker — the existing BF-7 code at lines 189-197 already propagates populated aliases into `_aggregation_output_index`.

**Acceptance tests:**
- `test_bf7_aliases_extracted` — `"total_capex"` in `agg.aliases` for Solar Battery Plant's `capital_cost`
- `test_bf7_total_capex_wired_to_module_output` — `annualized_financial.total_capex` wires to `MODULE_OUTPUT`

### Non-Functional Requirements

- All fixes MUST maintain backward compatibility with existing CalcDef-based pipeline
- Fixes MUST NOT change any public API signatures
- Fix ordering MUST respect the dependency chain: FR-2 → FR-1 → FR-3 → FR-4 → FR-5

---

## Acceptance Criteria

### Per-Fix Verification

- [ ] **FR-1 (RC1):** `_unwrap_invocation()` has `SysideAdapter.is_instance()` guards for FeatureChainExpression and FeatureReferenceExpression. No reference to `_KNOWN_WRAPPER_FUNCTIONS` in the function.
- [ ] **FR-2 (RC2):** In `reconstruct_expression()`, the `FeatureReferenceExpression` and `FeatureChainExpression` checks appear BEFORE the `hasattr(function)` check.
- [ ] **FR-3 (RC3):** In `_walk_aggregation_ast()`, the FeatureChainExpression and FeatureReferenceExpression handlers appear BEFORE the `hasattr(function)` check. Handler logic is unchanged from current lines 407-417.
- [ ] **FR-4 (RC4):** `HierarchyExtractionResult` has `part_usage_names` field. `extract_hierarchy_data()` populates it. `_scope_aggregation_expressions()` uses it in Strategy 2.
- [ ] **FR-5 (RC5):** `_enrich_aliases_from_bindings()` exists in `initialization.py`. Called between Step 3.5 and Step 4.7. Populates `agg.aliases` from CalcUsage binding matches.

### E2E Test Results

- [ ] `test_bf1_no_unsupported_nodes` — PASS
- [ ] `test_bf1_sum_terms_have_real_names` — PASS
- [ ] `test_bf7_aliases_extracted` — PASS
- [ ] `test_bf7_total_capex_wired_to_module_output` — PASS
- [ ] All 6 currently-passing tests remain PASS (zero regressions)

### Integration

- [ ] `uv run pytest tests/` — full suite passes with zero regressions
- [ ] No `"Evaluation"` string in any pipeline YAML output for solar_battery model

---

## Implementation Order

| Step | Fix | File(s) | Depends On |
|------|-----|---------|------------|
| 1 | FR-2 (RC2) | `expression_utils.py` | — |
| 2 | FR-1 (RC1) | `hierarchy_resolver.py` | — |
| 3 | FR-3 (RC3) | `hierarchy_resolver.py` | FR-2 |
| 4 | FR-4 (RC4) | `data_models.py`, `hierarchy_resolver.py`, `initialization.py` | — |
| 5 | FR-5 (RC5) | `initialization.py` | FR-4 (aliases need scoped aggs to be useful) |

---

## Related Artifacts

- **Synthesis Report:** `.project/reports/05_synthesis_and_fixes.md` (with design review UPDATE markers)
- **Prior Spec:** `.project/active/hierarchy-bugfix/spec.md` (BF-1 through BF-8; partially superseded)
- **E2E Tests:** `tests/integration/test_hierarchy_e2e.py`
- **Probe Scripts:** `scripts/probes/probe_sum_ast_structure.py`, `probe_redefinition_structure.py`, `probe_alias_resolution.py`
- **Epic:** `.project/backlog/epic_costed_component_pattern.md`
- **Design:** `.project/active/hierarchy-e2e-fixes/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_design`
