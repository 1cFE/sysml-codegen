# Spec: Redefinition Literal Value Propagation to JSON Templates

**Status:** Implemented
**Owner:** Reid Westwood
**Created:** 2026-02-16 20:08 UTC
**Complexity:** LOW
**Branch:** cost-pattern
**Commit:** 20b720e

---

## Business Goals

### Why This Matters

The COST-PATTERN epic's hierarchy-aware codegen correctly extracts `:>>` redefinition literals (e.g., `wattage :>> 400.0`) and rewrites virtual CalcUsage bindings to carry those values. But the literal values are dropped during entry point classification, so generated JSON input templates are empty for these parameters. Users must manually populate 13 design override fields before running the solar_battery pipeline — defeating the zero-workaround goal of V3 codegen.

### Success Criteria

- [ ] Generated `system_design.json` contains all 13 `:>>` literal values (wattage=400, efficiency=0.21, etc.) alongside the 3 multiplicity counts
- [ ] Zero manual JSON editing required to execute the solar_battery pipeline
- [ ] e2e_attr_expr codegen is unaffected (no hierarchy redefinitions in that model)

### Priority

High — blocks Phase 5 of the E2E post-codegen validation plan (`fusion-tea/.project/active/e2e-post-codegen-validation/plan.md`), which is the gate for COST-PATTERN Item 5.

---

## Problem Statement

### Current State

The data flow has a gap at a single point. The upstream and downstream both work correctly:

1. **Extraction** (works): `extract_design_overrides()` produces `RedefinitionData` with `literal_value=400.0` for each `:>>` override.

2. **Binding rewrite** (works): `_rewrite_virtual_bindings()` mutates the virtual CalcUsage binding from `REFERENCE` to `LITERAL`, setting `BindingInfo.literal_value=400.0` and `source_path=None`.

3. **Backtracker** (value dropped): `_trace_dependencies()` creates `BindingResolution(source_path=None)` for LITERAL bindings. Because `source_path` is None, the entry point is NOT added to `entry_point_sources`. The literal value on `BindingInfo.literal_value` is not carried forward.

4. **Classification** (receives nothing): `_classify_entry_points()` Strategy 3 looks up `entry_point_sources.get(qname)` — gets `None` — sets `default_value=None`.

5. **JSON generation** (works): `generate_all_derived_jsons_from_graph()` correctly skips entries where `ep.default_value is None`. Since the 13 parameters have `None`, they're omitted from the JSON.

**Contrast with multiplicity counts** (which work): Multiplicity values bypass `_classify_entry_points()` entirely. They flow through `MultiplicityData.count` -> `SumTerm.multiplicity_count` -> `EntryPoint(default_value=float(count))` directly in `_build_aggregation_module()`.

### Desired Outcome

Literal values from rewritten `:>>` LITERAL bindings MUST reach `EntryPoint.default_value` so that JSON templates are populated.

---

## Scope

### In Scope

- Propagating `BindingInfo.literal_value` through the backtracker -> graph builder -> `EntryPoint.default_value` path for LITERAL bindings created by `_rewrite_virtual_bindings()`

### Out of Scope

- Changes to `_rewrite_virtual_bindings()` — already correct
- Changes to `RedefinitionData` extraction — already correct
- Changes to `generate_all_derived_jsons_from_graph()` — already correct
- The AST dispatch & resolution cleanup work item (separate scope, no dependency)
- Entry point type reclassification (USAGE_LITERAL is acceptable for these; the issue is the missing value, not the classification label)

### Edge Cases & Considerations

- **Non-numeric literals**: Some `:>>` overrides could be boolean or string values. The current `float()` parsing in Strategy 3 would fail on these. The fix SHOULD handle non-float literal types gracefully (store as-is or convert where possible).
- **CHAIN redefinitions**: `_rewrite_virtual_bindings()` also rewrites CHAIN redefinitions (`:>> capital_cost = cost_model.total_cost`). These are NOT literal entry points — they resolve to MODULE_OUTPUT wiring. The fix MUST NOT affect CHAIN resolution.
- **Existing LITERAL bindings**: Some CalcUsage bindings are natively LITERAL (not from `:>>` rewrite). The fix SHOULD work for both native and rewritten LITERAL bindings consistently.
- **e2e_attr_expr model**: Has no hierarchy redefinitions. The fix MUST NOT regress this model's codegen output.

---

## Requirements

### Functional Requirements

1. **FR-1**: When a LITERAL binding (native or rewritten from `:>>`) creates an entry point, the literal value from `BindingInfo.literal_value` MUST be propagated to `EntryPoint.default_value`.

2. **FR-2**: The propagation MUST work for all numeric literal types (`int`, `float`). Non-numeric types (bool, string) SHOULD be stored if the `EntryPoint.default_value` field supports them, or MAY be skipped with a log warning.

3. **FR-3**: CHAIN redefinition bindings (which resolve to MODULE_OUTPUT wiring) MUST NOT be affected by this change.

4. **FR-4**: The fix MUST NOT change behavior for entry points that already have `default_value` populated via Strategy 1 (DESIGN_ATTRIBUTE) or Strategy 2 (LIBRARY_DEFAULT).

---

## Acceptance Criteria

### Core Functionality

- [ ] After regenerating solar_battery_v3, `system_design.json` contains all 13 `:>>` literal values with correct numeric values (wattage=400, efficiency=0.21, power_rating=5000, string_count=5, panel_count=20, capacity_kwh=13.5, chemistry_factor=1.1, pack_count=8, tilt_angle=25, circuit_count=6, system_capacity_kw=10, plus any others)
- [ ] `system_design.json` retains all 3 multiplicity counts (module_count=20, inverter_count=4, pack_count=8) — no regression
- [ ] e2e_attr_expr_v3 codegen output is byte-identical or functionally equivalent to pre-fix output

### Quality & Integration

- [ ] All existing sysml-codegen tests pass (currently 647+)
- [ ] New unit test(s) verify that a LITERAL binding entry point gets `default_value` populated
- [ ] No changes to JSON generation code (`entry_point.py`) — the fix is upstream of generation

---

## Affected Code Paths

| File | Function | Role in Fix |
|------|----------|-------------|
| `analysis/dependency_backtracker.py` | `_trace_dependencies()` LITERAL case (~line 338-353) | Where the literal value is currently dropped |
| `resolution/graph_builder.py` | `_classify_entry_points()` Strategy 3 (~line 322-333) | Where `default_value` is set from `entry_point_sources` |
| `resolution/graph_builder.py` | `build_computation_graph()` (~line 116-123) | Call site that could pass additional data |

---

## Related Artifacts

- **Validation plan:** `~/1cfe/fusion-tea/.project/active/e2e-post-codegen-validation/plan.md` (Phase 4.3 finding, Phase 5 blocked)
- **Cleanup design:** `.project/active/ast-dispatch-resolution-cleanup/design.md` (independent work item)
- **Epic:** `.project/backlog/epic_costed_component_pattern.md`
- **Design:** `.project/active/redefinition-literal-propagation/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_design`
