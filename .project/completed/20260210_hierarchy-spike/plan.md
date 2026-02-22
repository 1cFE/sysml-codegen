# Implementation Plan: SysIDE AST Discovery for Hierarchy Patterns

**Status:** Complete
**Created:** 2026-02-10
**Last Updated:** 2026-02-10

## Source Documents
- **Spec:** `.project/active/hierarchy-spike/spec.md`
- **Design:** `.project/active/hierarchy-spike/design.md` ← See here for component details, syside API table, probe strategies, output format

## Implementation Strategy

**Phasing Rationale:**
Phase 1 de-risks model loading and element lookup (the foundation everything depends on) by implementing the scaffold + Q1 as a smoke test. Phase 2 iterates through the remaining 9 probes now that the pattern is proven. Phase 3 adds the assessment/reporting sections that require all probe findings as input.

**Overall Validation Approach:**
- Each phase validated by running the script and checking output
- No test files (this is a research script, not production code)
- Regression safety verified by `uv run pytest tests/` at the end

---

## Phase 1: Script Scaffold + Q1 Smoke Test

### Goal
Get the script running: model loading, utilities, CLI pattern, and Q1 (template ownership) as proof that we can find elements, walk ownership chains, and produce structured output with code examples. If this phase fails, we know immediately.

### Test Stencil (Manual Validation)
```bash
# Run the script -- should load model and print Q1 output
uv run python scripts/spike_hierarchy_ast.py

# Expected: model loads without error, Q1 section prints with:
# - 3 test targets (PV Module.cost_model, Solar Array.allocation_model, solar_battery_plant.energy_production)
# - Owner chain for each showing type(owning_elem).__name__
# - Code example: block with # => annotations
# - Status line (✓/✗/⚠)
```

### Changes Required

**See `design.md` for:**
- Architecture → `design.md#architecture-single-script-10-probe-functions`
- Loading pattern → `design.md#component-1-model-loading-and-utilities`
- Utility signatures → `design.md#component-1-model-loading-and-utilities`
- Q1 strategy & attributes → `design.md#q1-template-calcusage-ownership`
- Output format → `design.md#component-2-probe-functions-q1-q10` (per-question output format example)

**Specific file changes:**

#### 1. Script File
**File:** `scripts/spike_hierarchy_ast.py` (NEW)
- [x] Add docstring, imports (`SysMLDataExtractor`, `Path`, `sys`)
- [x] Add `DEFAULT_SUITES` + CLI arg pattern (see `design.md#component-4-report-generation`)
- [x] Implement `sanitize_name()` -- strip `'` and `"`, replace spaces with `_`
- [x] Implement `safe_attr(obj, attr, default)` -- `getattr` with try/except
- [x] Implement `type_name(obj)` -- `type(obj).__name__`
- [x] Implement `find_element_by_name(model, adapter, type_str, name)` -- iterate `elements_of_type`, match against both `elem.name` and `sanitize_name(elem.name)`
- [x] Implement `dump_owned_members(elem, indent, max_depth)` -- recursive owned_members dump
- [x] Implement `dump_redefinitions(elem)` -- list `owned_redefinitions` with `redefined_feature` info
- [x] Implement `probe_q1_template_ownership(model, adapter)` per design Q1 strategy
- [x] Implement `main()` -- load model, run Q1, print header/output
- [x] Add `if __name__ == "__main__": main()`

### Validation

**Automated:**
- [x] `uv run python scripts/spike_hierarchy_ast.py` → exits 0, prints Q1 output
- [x] `uv run pytest tests/` → all existing tests pass (no production code touched)

**Manual:**
- [ ] Q1 output shows 3 test targets with owner chain details
- [ ] `PV Module.cost_model` shows PartDefinition in owner chain
- [ ] `solar_battery_plant.energy_production` shows PartUsage in owner chain
- [ ] `Code example:` block present with `# =>` annotations
- [ ] Quoted name `'PV Module'` found correctly by `find_element_by_name()`

**What We Know Works After This Phase:**
Model loading via SysideAdapter, element lookup with quoted name normalization, ownership chain traversal, structured output format with code examples.

---

## Phase 2: Core Probes (Q2-Q10)

### Goal
Implement the remaining 9 probe functions. Each follows the same pattern proven in Phase 1: find target element(s), inspect documented syside attributes, print structured output with code examples.

### Test Stencil (Manual Validation)
```bash
# Run full script -- all 10 questions should produce output
uv run python scripts/spike_hierarchy_ast.py

# Expected: 10 sections (Q1-Q10), each with:
# - Target identification
# - Attribute inspection results
# - Code example: block
# - Status: line
# No crashes, no empty sections (⚠ with explanation is OK for gaps)
```

### Changes Required

**See `design.md` for:** probe strategies and attributes for each question:
- Q2: `design.md#q2-redefinition-ast-representation`
- Q3: `design.md#q3-part-redefines-vs-plain-part`
- Q4: `design.md#q4-deep-path-redefinition`
- Q5: `design.md#q5-multiplicity-representation`
- Q6: `design.md#q6-sum-invocationexpression-structure`
- Q7: `design.md#q7-specialization-chain-traversal`
- Q8: `design.md#q8-new-attribute-vs-redefined-attribute-distinction`
- Q9: `design.md#q9-default-representation`
- Q10: `design.md#q10-binding-to-inherited-redefined-attribute`

**Specific file changes:**

#### 1. Probe Functions
**File:** `scripts/spike_hierarchy_ast.py` (MODIFY)

Implement in this order (grouped by risk/dependency):

**Redefinition cluster (Q2, Q3, Q8 -- highest risk, core to epic):**
- [x] `probe_q2_redefinition_ast()` -- test all 4 `:>>` patterns on `PV Module` and `Solar Array`; probes `owned_redefinitions`, `redefined_feature`, `feature_value_expression`
- [x] `probe_q3_part_redefines()` -- compare `part redefines solar_array` (design:25) vs `part solar_array` (library:738); probes `owned_redefinitions`, `types`, `owned_specializations`
- [x] `probe_q8_new_vs_redefined_attr()` -- compare `misc_hardware_cost` vs `:>> capital_cost` on `Solar Array`; probes `owned_redefinitions` presence as differentiator

**Deep path + multiplicity cluster (Q4, Q5 -- needed for hierarchy traversal):**
- [x] `probe_q4_deep_path_redefinition()` -- inspect `:>> pv_module.wattage = 400.0`; probes `owned_feature_chainings`, `chaining_features`, `first_chaining_feature`
- [x] `probe_q5_multiplicity()` -- inspect `pv_module [module_count]` on `Solar Array`; probes `multiplicity`, `MultiplicityRange` bounds, resolve to default literal

**Expression cluster (Q6 -- sum() is critical for aggregation):**
- [x] `probe_q6_sum_invocation()` -- inspect `sum(pv_module.capital_cost)` expression tree; probes for `InvocationExpression` nodes, operand structure, function reference

**Traversal (Q7 -- end-to-end validation):**
- [x] `probe_q7_specialization_chain()` -- walk full chain from `solar_battery_plant` to `PVModuleCostCalc`; probes `types`, `owned_features`, `owned_specializations` at each level

**Remaining (Q9, Q10 -- lower risk):**
- [x] `probe_q9_default_value()` -- compare `default :=` on CalcDef param vs part attribute; probes `feature_value`, `feature_value_expression`
- [x] `probe_q10_binding_to_redefined()` -- inspect `in total_capex = capital_cost` binding; probes whether reference resolves to redefined or abstract attribute

#### 2. Update main()
**File:** `scripts/spike_hierarchy_ast.py` (MODIFY)
- [x] Wire all 9 new probe functions into `main()` execution flow
- [x] Collect results from all probes for summary (Phase 3)

### Validation

**Automated:**
- [x] `uv run python scripts/spike_hierarchy_ast.py` → exits 0, prints Q1-Q10 output
- [x] No Python tracebacks (all attribute access guarded by `safe_attr` / try-except)

**Manual:**
- [ ] All 10 Q sections produce output (no empty sections)
- [ ] Q2: at least one `:>>` pattern shows `owned_redefinitions` with `redefined_feature`
- [ ] Q4: deep-path element structure documented (chained feature or other)
- [ ] Q5: multiplicity attribute found on PartUsage element
- [ ] Q6: `sum()` expression tree nodes identified by type name
- [ ] Q7: full chain traversable from design to CalcDef
- [ ] Each section has `Code example:` block and `Status:` line

**What We Know Works After This Phase:**
All 10 AST patterns probed with concrete findings. We know which syside attributes work, which are populated, and which are gaps.

---

## Phase 3: Assessment, Summary & Report

### Goal
Add FR-11 reuse assessment (per agentic-mbse module), NFR-3 metamodel type population table, summary table, go/no-go recommendation, and capture the full output as the spike report.

### Test Stencil (Manual Validation)
```bash
# Run script, capture output to report
uv run python scripts/spike_hierarchy_ast.py 2>&1 | tee /tmp/spike_output.txt

# Expected additions beyond Phase 2:
# - "agentic-mbse Reuse Assessment (FR-11)" section with 5 module assessments
# - "Metamodel Type Population (NFR-3)" table
# - "Summary" table with Q1-Q10 one-line findings
# - "Go/No-Go Recommendation" section
```

### Changes Required

**See `design.md` for:**
- FR-11 module checklist → `design.md#component-3-agentic-mbse-reuse-assessment-fr-11`
- NFR-3 type table → `design.md#component-4-report-generation`
- Output structure → `design.md#component-4-report-generation`

**Specific file changes:**

#### 1. Assessment and Summary Functions
**File:** `scripts/spike_hierarchy_ast.py` (MODIFY)
- [x] Implement `assess_agentic_mbse_reuse(model, adapter)` -- review all 5 modules per design FR-11 table: `syside_adapter.py` (type map), `binding.py` (classify_binding), `expression.py` (traverse_expression + InvocationExpression), `helpers.py` (get_parent_part_name), `types.py` (data models)
- [x] Implement `print_metamodel_type_population(probe_results)` -- collect which syside types were accessed and whether they were populated; output the NFR-3 table (Redefinition, Specialization, Multiplicity, MultiplicityRange, InvocationExpression, FeatureChainExpression, FeatureValue)
- [x] Implement `print_summary(probe_results)` -- Q1-Q10 one-line status table
- [x] Implement `print_go_no_go(probe_results)` -- analyze results, recommend go/no-go with rationale

#### 2. Update main()
**File:** `scripts/spike_hierarchy_ast.py` (MODIFY)
- [x] Wire assessment, NFR-3 table, summary, and go/no-go into output flow
- [x] Track `type_population` dict across all probes (type name → {available: bool, populated: bool, count: int})

#### 3. Capture Report
**File:** `.project/active/hierarchy-spike/report.md` (NEW)
- [x] Run script, capture output
- [x] Format into markdown report with header (status, date, branch, epic ref)
- [x] Add "Related Artifacts" section linking back to spec and design
- [x] Organize findings by question number for easy reference during Items 2-4
- [x] Ensure all acceptance criteria from spec are addressed

### Validation

**Automated:**
- [x] `uv run python scripts/spike_hierarchy_ast.py` → exits 0, full output
- [x] `uv run pytest tests/` → all existing tests pass (final regression check)

**Manual:**
- [ ] FR-11 section lists all 5 agentic-mbse modules with assessments
- [ ] NFR-3 table shows all 7 syside types with available/populated status
- [ ] Summary table has Q1-Q10 one-line findings
- [ ] Go/no-go recommendation present with rationale
- [ ] `report.md` exists and covers all spec acceptance criteria
- [ ] No production code was modified (verify with `git diff --name-only src/`)

**What We Know Works After This Phase:**
Complete spike deliverable: reusable probe script + structured report answering all 10 questions with code examples, agentic-mbse reuse assessment, metamodel type population data, and go/no-go decision. Ready to feed into Item 2 spec.

---

## Environment Setup

**See CLAUDE.md for full environment rules**

```bash
# Ensure dependencies installed (should already be from prior work)
uv pip install -e ~/agentic-mbse && uv pip install -e ".[dev]"

# Verify model fixture exists
ls tests/fixtures/solar_battery_model/
```

---

## Risk Management

**See `design.md#potential-risks` for detailed risk analysis**

**Phase-Specific Mitigations:**
- **Phase 1**: If model loading fails, check that `agentic-mbse` is installed and syside is available. If `find_element_by_name()` can't find quoted names, try matching against `elem.declared_name` in addition to `elem.name`.
- **Phase 2**: If `owned_redefinitions` is empty (Q2), probe `owned_relationships` and filter by `type(rel).__name__` containing "Redefinition". If `InvocationExpression` isn't found (Q6), dump the full expression tree node types to see what syside uses. Document gaps rather than building workarounds (per spec: out of scope).
- **Phase 3**: Assessment is based on empirical findings from Phase 2. If a type is missing/unpopulated, document it as a gap -- don't speculate about workarounds.

## Implementation Notes

[TO BE FILLED DURING IMPLEMENTATION]

### Phase 1 Completion
**Completed:** 2026-02-10
**Actual Changes:**
- Created `scripts/spike_hierarchy_ast.py` with utilities, model loading, Q1 probe, and main()
- Utilities: `sanitize_name`, `safe_attr`, `type_name`, `find_element_by_name`, `find_member_by_name`, `dump_owned_members`, `dump_owned_relationships`, `dump_redefinitions`
- Q1 successfully probed all 3 targets: `PV Module.cost_model` (PartDefinition), `Solar Array.allocation_model` (PartDefinition), `solar_battery_plant.energy_production` (PartUsage)
- All 285 existing tests pass (no production code touched)

**Issues:** None. All targets found, all ownership chains correct.
**Deviations:**
- Added `find_member_by_name()` helper (not in design) for targeted member lookup on a specific parent element. Cleaner than iterating all CalcUsages and filtering by owner.
- `dump_owned_relationships()` included for completeness (will be useful in Phase 2)

**Key Finding:** `owning_type` cleanly distinguishes PartDefinition (template) from PartUsage (concrete). The owner chain traversal works: CalcUsage → Part → Package → Namespace.

### Phase 2 Completion
**Completed:** 2026-02-10
**Actual Changes:**
- Implemented all 9 probe functions (Q2-Q10) in `scripts/spike_hierarchy_ast.py`
- Added utilities: `walk_expression_tree()`, `get_redefinition_info()`, `find_any_member_by_name()`, `_q_result()`, `_probe_default_attr()`
- Added import: `from agentic_mbse.sysml.expression import traverse_expression`
- Wired all 10 probes into `main()`, all producing structured output with Code example blocks
- All 10 probes pass (✓) on solar_battery model
- All 285 existing tests pass

**Issues:**
- **CRITICAL DISCOVERY: `:>>` redefinitions create `ReferenceUsage` elements, not `AttributeUsage`**. Initial probes for Q2, Q6, Q8 failed because they searched for `AttributeUsage`. Fixed by searching ReferenceUsage then falling back to `find_any_member_by_name()`. This is a key finding for Items 2-4: code that processes `:>>` must check ReferenceUsage, not just AttributeUsage.
- Q4 deep-path elements are unnamed `ReferenceUsage` with `name=None`. The `owned_feature_chainings` list is empty (0 found), but `chaining_features` returns a `LazyIterator`. The redefined_feature also has `name=None`. Element identified by matching `feature_value_expression` literal value (400.0). This encoding is less structured than expected.
- Q5 `cached_lower_bound=20, cached_upper_bound=21` -- the upper bound is 21, not 20. This needs investigation (may be an off-by-one or exclusive bound).
- Q10 `total_capex` binding parameter is `ReferenceUsage` (not AttributeUsage) with `direction=FeatureDirectionKind.In`.

**Deviations:**
- Added `find_any_member_by_name()` (not in design) -- needed because `:>>` elements are ReferenceUsage, not predictable as AttributeUsage
- Added `_q_result()` helper for consistent early-return result dicts
- Q4 identification strategy changed: instead of searching by name/chainings, identified deep-path element by matching literal value (400.0) since elements are unnamed
- Q6 uses both `walk_expression_tree()` (our own) and `traverse_expression()` (agentic_mbse) for comparison -- both successfully find InvocationExpression nodes

**Key Findings:**
- Q2: All 4 `:>>` patterns (enum, EXPOSE, aggregation, FORMULA) produce `ReferenceUsage` with `owned_redefinitions[0].redefined_feature` pointing to `Costed Component` abstract attributes
- Q3: `part redefines` adds explicit `Redefinition` in `owned_specializations`; plain `part` has `FeatureTyping + Subsetting` instead
- Q4: Deep-path overrides are unnamed ReferenceUsages with literal values; chaining resolution needs more investigation
- Q5: `MultiplicityRange` with `cached_lower_bound/cached_upper_bound` and `upper_bound` as `FeatureReferenceExpression` referencing sibling attribute
- Q6: `InvocationExpression` with `.function.name='sum'` -- traverse_expression handles it; 2 sum() calls found (pv_module + inverter aggregation)
- Q7: Full 8-step chain traversal works via alternating `.types` and `owned_members`
- Q8: `owned_redefinitions` cleanly distinguishes new (AttributeUsage, empty) from redefined (ReferenceUsage, non-empty)
- Q9: `feature_value.is_default=True` uniformly marks `default :=` in both CalcDef params and part attributes
- Q10: `capital_cost` binding resolves to `ReferenceUsage` on `Solar Battery Plant` PartDef (the redefined attribute), not the abstract `Costed Component`

### Phase 3 Completion
**Completed:** 2026-02-10
**Actual Changes:**
- Added `assess_agentic_mbse_reuse(adapter, probe_results)` -- programmatically checks adapter type map, reviews all 5 agentic-mbse modules against probe findings
- Added `build_type_population(results)` -- derives NFR-3 type availability/population from probe result status
- Added `print_metamodel_type_population(type_pop)` -- formatted table of 7 syside types
- Added `print_summary(results)` -- Q1-Q10 one-line status table
- Added `print_go_no_go(results, type_pop)` -- quantitative analysis + recommendation
- Updated `main()` to wire Phase 3 functions, replacing partial summary
- Created `.project/active/hierarchy-spike/report.md` with full formatted findings
- Script exits 0, all 10 probes pass (✓), 285 existing tests pass

**Issues:** None. All sections render correctly, assessment is data-driven from probe results.
**Deviations:**
- `assess_agentic_mbse_reuse` takes `(adapter, probe_results)` instead of `(model, adapter)` from plan -- probe results needed to inform assessment (e.g., Q6 InvocationExpression finding)
- `build_type_population` added as separate function (not in original plan) -- cleaner separation between data collection and rendering
- Go/no-go includes hardcoded critical findings list based on empirical Phase 2 results -- these are known truths, not dynamic calculations

---

**Status**: ~~Draft~~ → ~~In Progress~~ → **Complete**
