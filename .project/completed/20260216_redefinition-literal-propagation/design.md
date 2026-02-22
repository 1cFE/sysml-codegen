# Design: Redefinition Literal Value Propagation

**Status:** Implemented
**Owner:** Reid Westwood
**Created:** 2026-02-16 20:13 UTC
**Branch:** cost-pattern
**Commit:** 20b720e

## Overview

Populate `entry_point_sources` for LITERAL bindings in the backtracker so that
`_classify_entry_points()` Strategy 3 can set `EntryPoint.default_value`. This
is a 2-line fix in one function.

## Related Artifacts

- **Spec:** `.project/active/redefinition-literal-propagation/spec.md`
- **Validation plan:** `~/1cfe/fusion-tea/.project/active/e2e-post-codegen-validation/plan.md`
- **Epic:** `.project/backlog/epic_costed_component_pattern.md`

---

## Research Findings

### The Exact Gap

The LITERAL binding case in `_trace_dependencies()` (dependency_backtracker.py:338-353)
creates a `BindingResolution(source_path=None)` and then `continue`s past the
`entry_point_sources` population code at line 375-376. The literal value exists
on `binding.literal_value` but is never transferred to any output dict.

Meanwhile, `_classify_entry_points()` Strategy 3 (graph_builder.py:328-333) is
already designed to consume literal values from `entry_point_sources`:

```python
source_path = entry_point_sources.get(qname)
if source_path:
    try:
        default_value = float(source_path)
    except (ValueError, TypeError):
        pass
```

The producer doesn't write; the consumer already reads. The fix connects them.

### `entry_point_sources` Has One Consumer

Grepping the entire `src/` tree confirms `entry_point_sources` is only consumed
by `_classify_entry_points()` Strategy 3 (graph_builder.py:328). Strategies 1
and 2 don't use it. No other code reads it. So adding entries for LITERAL
bindings cannot interfere with any other logic.

### Native vs Rewritten LITERAL Bindings

Two paths create LITERAL bindings:

| Origin | `binding.source_path` | `binding.literal_value` |
|--------|-----------------------|-------------------------|
| Native (usage_extractor.py:548-554) | `str(literal_value)` | `literal_value` |
| `:>>` rewrite (initialization.py:318-321) | `None` | `matched.literal_value` |

Both paths populate `binding.literal_value`. The fix uses this field, so it
handles both native and rewritten LITERAL bindings consistently.

### Round-Trip Safety

`str()` → `float()` round-trip for expected types:

| Input | `str()` | `float()` | Result |
|-------|---------|-----------|--------|
| `400.0` | `"400.0"` | `400.0` | correct |
| `0.21` | `"0.21"` | `0.21` | correct |
| `400` (int) | `"400"` | `400.0` | correct (int→float acceptable; `EntryPoint.default_value` is `float \| None`) |
| `True` (bool) | `"True"` | `ValueError` | skipped — acceptable per FR-2 MAY |
| `"text"` (str) | `"text"` | `ValueError` | skipped — acceptable per FR-2 MAY |

### Existing Test Pattern

`test_graph_builder.py` tests `build_computation_graph()` via helper
`_make_minimal_graph_inputs()` which builds a `BacktrackingResult` with
synthetic data. The same pattern can construct a result with a LITERAL entry
point in `entry_point_sources` and verify the graph's `EntryPoint.default_value`.

---

## Proposed Design

### Change 1: Backtracker LITERAL Case

**File:** `src/sysml_codegen/analysis/dependency_backtracker.py`
**Function:** `_trace_dependencies()`, LITERAL case (lines 338-353)

Add 2 lines after the existing `self._entry_point_context` assignment:

```python
if binding.binding_type == BindingType.LITERAL:
    # Case 2: Literal binding -> entry point
    entry_point_qn = f"{usage.qualified_name}__{param_name}"

    # Unified resolution
    self._binding_resolutions[mapping_key] = BindingResolution(
        resolution_type=BindingResolutionType.ENTRY_POINT,
        qualified_name=entry_point_qn,
        source_path=None,
        is_transitive=False,
    )

    # DEPRECATED: Keep for backward compat
    self._binding_to_entry_point[mapping_key] = entry_point_qn
    self._entry_point_context[entry_point_qn] = usage

    # NEW: Carry literal value for entry point classification (FR-1)
    if binding.literal_value is not None:
        self._entry_point_sources[entry_point_qn] = str(binding.literal_value)

    continue
```

**Why this works:** Strategy 3 in `_classify_entry_points()` already does
`float(entry_point_sources.get(qname))`. No changes needed downstream.

**What doesn't change:**
- `BindingResolution.source_path` stays `None` — it's semantically a binding
  *path*, not a value. The resolution model is unchanged.
- Strategy 1 (DESIGN_ATTRIBUTE) and Strategy 2 (LIBRARY_DEFAULT) don't read
  `entry_point_sources`, so they're unaffected (FR-4).
- CHAIN bindings don't enter the LITERAL case, so they're unaffected (FR-3).

### Change 2: None

No changes to `_classify_entry_points()`, `build_computation_graph()`,
`BacktrackingResult`, `EntryPoint`, or `generate_all_derived_jsons_from_graph()`.

### Test: LITERAL Entry Point Default Value

**File:** `tests/unit/test_graph_builder.py` (extend existing file)

Add one test function that:

1. Creates a `CalcUsageData` with one input parameter
2. Creates a `BacktrackingResult` with:
   - That usage's parameter as an entry point in `entry_points`
   - The literal value string in `entry_point_sources` (e.g., `{"UsageA__param": "42.5"}`)
3. Calls `build_computation_graph()`
4. Asserts the resulting `EntryPoint` has `default_value == 42.5` and
   `entry_type == EntryPointType.USAGE_LITERAL`

This tests the Strategy 3 path end-to-end without needing the backtracker
(the backtracker change is tested implicitly by the integration test below).

### Integration Validation

After the fix, regenerate solar_battery_v3 in fusion-tea and verify:

```bash
# Check that system_design.json has more than 3 entries
python3 -c "import json; d=json.load(open('generated/solar_battery_v3/inputs/system_design.json')); print(len(d), 'entries'); assert len(d) >= 16"
```

Expected: 16+ entries (13 `:>>` literals + 3 multiplicity counts).

---

## Potential Risks

| Risk | Impact | Mitigation |
|------|--------|-----------|
| `str(literal_value)` produces unparseable string for exotic types | `default_value` stays `None` for that entry point | Acceptable per FR-2 MAY. Only affects non-numeric literals, which are rare in cost models. |
| Existing native LITERAL bindings now also get values in JSON | Behavioral change for non-hierarchy models | Checked: e2e_attr_expr model has no native LITERAL bindings that create entry points (its literals are CalcDef defaults → LIBRARY_DEFAULT). No regression expected. |
| `entry_point_sources` docstring says "binding source path" | Semantic drift | Update the docstring comment (line 56, 159) to note it also carries literal value strings for LITERAL bindings. |

---

## Integration Strategy

This is a standalone fix with no dependencies on the AST dispatch cleanup.
It should land before Phase 5 of the E2E validation plan so the solar_battery
pipeline can execute without manual JSON editing.

The fix touches one function in one file (plus one test). It can be reviewed
and validated in isolation.

---

## Validation Approach

1. **Unit test**: New test in `test_graph_builder.py` verifying LITERAL entry
   point gets `default_value` populated via Strategy 3
2. **Existing tests**: All 647+ tests pass (`uv run pytest tests/`)
3. **E2E validation**: Regenerate solar_battery_v3 in fusion-tea, confirm
   `system_design.json` contains 16+ entries with correct literal values
4. **Regression check**: Regenerate e2e_attr_expr_v3, confirm output is
   unchanged (no native LITERAL entry points affected)

---

**Next Steps:** After approval → `/_my_implement`
