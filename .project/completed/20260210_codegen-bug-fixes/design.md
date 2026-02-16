# Design: Codegen Bug Fixes (E2E Validation Findings)

**Status:** Reviewed
**Owner:** Reid Westwood
**Created:** 2026-02-10 04:34 UTC
**Complexity:** MEDIUM
**Branch:** cost-pattern
**Commit:** 7625088

---

## Overview

Design for fixing all 7 codegen bugs found during fusion-tea E2E validation. Each proposed fix from the root cause analysis reports has been validated against the actual codebase. All research claims are confirmed accurate with minor line number drift.

## Related Artifacts

- **Spec:** `.project/active/codegen-bug-fixes/spec.md`
- **Research (Bugs 1-4):** `.project/research/20260210-040346_e2e-codegen-bug-root-cause-analysis.md`
- **Research (Bugs 5-7):** `.project/research/20260210-042253_phase4-additional-bugs-root-cause-analysis.md`
- **Epic (downstream):** `.project/backlog/epic_costed_component_pattern.md`

---

## Research Findings

### Codebase Validation of Research Report Claims

Every proposed fix from both research reports was validated against the actual source code. Summary:

| Bug | Report Claim | Validated? | Line Drift | Notes |
|-----|-------------|-----------|------------|-------|
| 1 | param_groups frozen before FORMULA EPs created | **Yes** | ~1 line | Steps 4-5 at lines 112-128, Step 6.5 at 156-167 |
| 2 | Index uses dotted/bare keys, lookup gets `::` paths | **Yes** | Exact | Index at 138-145, lookup at 397-400 |
| 2b | EXPOSE_PURE excluded from index | **Yes** | Exact | Lines 140-141 |
| 3 | `"Float"` hardcoded for FORMULA input type_hint | **Yes** | Exact | cli/__init__.py:265 |
| 4 | `_build_exit_points()` uses bare `float` for multi-output | **Yes** | Exact | pipeline.py:221-224 |
| 4 | `_collect_exit_point_primitive_types()` only collects single-output | **Yes** | Exact | registry.py:57 (`if out.field_name == "root"`) |
| 5 | Preserve branch ignores compilation_result | **Yes** | Exact | cli/__init__.py:459-461 |
| 6 | `sanitize_name()` missing special char handling | **Yes** | Exact | qualified_names.py:12-27 |
| 6b | Duplicate `_sanitize_name()` in extractor.py | **Yes** | Exact | extractor.py:616-624, 7 call sites |
| 7 | All 4 functions only write `__init__.py` to deepest dir | **Yes** | ~2 lines | Lines 181-189, 239-244, 347-352, 429-437 |

### Key Architectural Finding: param_groups Not Used During Module Building

For Bug 1, investigation revealed that `param_groups` (the `list[ParameterGroup]`) is **not used during module building** (Steps 6 and 6.5). Both `_build_pipeline_module()` and `_build_computed_attr_module()` use `entry_points` dict and `group_deriver.classify()` directly. `param_groups` is only consumed in the final `ComputationGraph(entry_point_groups=param_groups)`.

This means param_groups can be **safely rebuilt from scratch after Step 6.5** without affecting any module wiring. This is cleaner than the research report's proposed "Step 6.6 reconciliation."

### Key Finding: No run_pipeline.py Template Exists (Bug 4)

Codegen does NOT generate `run_pipeline.py`. It is hand-crafted per project. For Bug 4, this means primitive write handlers must be provided through a different mechanism than the research report suggested. See Bug 4 design section for the approach.

### Key Finding: `derive_for_entry_points()` Exists (Bug 1)

`ParameterGroupDeriver` has both:
- `derive_groups_filtered(backtracking_result, ...)` - filters by `backtracking_result.entry_points` (excludes FORMULA EPs)
- `derive_for_entry_points(entry_points: set[str])` - filters by arbitrary EP set (can include FORMULA EPs)

However, `derive_for_entry_points` filters groups but not individual parameters within groups. `derive_groups_filtered` filters both. The Bug 1 fix needs parameter-level filtering with the full EP set.

---

## Inter-Bug Dependencies

| Dependency | Description |
|-----------|-------------|
| Bug 2 before Bug 1 | Bug 2 fix (backtracker wiring) ensures CalcUsage bindings to FORMULA attrs resolve as MODULE_OUTPUT. Without this, Bug 1's entry point additions would be partially redundant (some would be incorrectly created as entry points instead of wired). |
| Bug 6 independent | Name sanitization is orthogonal to all other bugs. Can be fixed first as a safety improvement. |
| Bug 7 independent | `__init__.py` creation is orthogonal. Can be fixed in any order. |
| Bug 3 independent | Type mismatch fix is isolated to one line. |
| Bug 5 independent | Smart-regen logic is separate from all other bugs. |
| Bug 4 is a TEAx fix | No sysml-codegen changes needed. Pipeline YAML generation is already correct. TEAx ExitPoint needs native primitive type support. |

### Implementation Order

1. **Bug 6** (sanitize_name) - Independent, trivial, broad safety improvement
2. **Bug 7** (intermediate __init__.py) - Independent, low effort
3. **Bug 3** (FORMULA input type) - Independent, one-line fix
4. **Bug 2** (backtracker wiring) - Core fix, enables proper FORMULA/EXPOSE resolution
5. **Bug 1** (entry point groups) - Depends on Bug 2 being correct
6. **Bug 5** (smart-regen upgrade) - Independent
7. **Bug 4** (exit_point primitives) - **TEAx fix, not sysml-codegen** — file task in fusion-tea

---

## Proposed Design

### Bug 6: Special Character Sanitization

**File:** `src/sysml_codegen/core/qualified_names.py`
**Function:** `sanitize_name()` (lines 12-27)

**Change:** Add regex replacement for non-identifier characters after existing space replacement.

```python
import re

def sanitize_name(name: str | None) -> str:
    if not name:
        return ""
    name = name.strip("'\"")
    name = name.replace(" ", "_")
    # NEW: Replace non-alphanumeric, non-underscore chars with underscore
    name = re.sub(r"[^a-zA-Z0-9_]", "_", name)
    # NEW: Collapse runs of underscores (but NOT across segment boundaries)
    name = re.sub(r"_+", "_", name)
    # NEW: Strip leading/trailing underscores
    name = name.strip("_") or "unnamed"
    if name in {"class", "def", "import", "from", "return", "yield"}:
        name = f"{name}_"
    return name
```

**Result:** `Racking_&_Mounting` -> `Racking_Mounting` (valid Python identifier).

**Note on underscore collapsing:** `_+` (not `__+`) is used because `sanitize_name()` operates on individual name segments. The `__` ADR-003 separator is applied later in `build_element_qualified_name()` / `get_channel_name()` by joining segments. Collapsing within segments is safe.

**File:** `src/sysml_codegen/extraction/extractor.py`
**Function:** `_sanitize_name()` (lines 616-624) and 7 call sites (lines 93, 132, 155, 191, 258, 341, 616)

**Change:** Remove the method entirely. Replace all `self._sanitize_name(...)` calls with `sanitize_name(...)` imported from `core.qualified_names`.

Add import at top of file:
```python
from sysml_codegen.core.qualified_names import sanitize_name
```

Replace calls:
- Line 93: `self._sanitize_name(elem.name)` -> `sanitize_name(elem.name)`
- Line 132: same pattern
- Line 155: same pattern
- Line 191: same pattern
- Line 258: same pattern
- Line 341: same pattern
- Lines 616-624: Delete method

**Testing:**
- Unit test: `sanitize_name("Racking_&_Mounting")` -> `"Racking_Mounting"`
- Unit test: `sanitize_name("foo$bar")` -> `"foo_bar"`
- Unit test: `sanitize_name("hello-world")` -> `"hello_world"`
- Unit test: `sanitize_name("a@b#c")` -> `"a_b_c"`
- Unit test: `sanitize_name("  normal  ")` -> `"normal"` (strip still works)
- Unit test: `sanitize_name("'Quoted Name'")` -> `"Quoted_Name"` (quote strip still works)
- Existing tests must still pass (regression)

---

### Bug 7: Missing Intermediate `__init__.py`

**File:** `src/sysml_codegen/cli/__init__.py`

**New helper function** (add near top of file, after imports):

```python
def _ensure_package_init_files(
    base_dir: Path, relative_path: str, docstring: str = '"""Namespace package."""\n'
) -> None:
    """Ensure __init__.py exists in all directories along relative_path."""
    parts = Path(relative_path).parts
    current = base_dir
    for part in parts:
        current = current / part
        init_file = current / "__init__.py"
        if not init_file.exists():
            init_file.write_text(docstring)
```

**Changes to 4 functions:**

1. **`_generate_modules()`** (lines 181-189): After `namespace_dir.mkdir(...)`, replace single `__init__.py` write with:
   ```python
   _ensure_package_init_files(modules_dir, python_path.directory,
       '"""Namespace package for generated modules."""\n')
   ```
   Remove the `created_namespaces` set and its check (the helper is idempotent via `if not init_file.exists()`).

2. **`_generate_computed_attr_modules()`** (lines 239-244): Same pattern, replace single `__init__.py` write.

3. **`_generate_computed_attr_stencils()`** (lines 347-352): Same pattern, replace with:
   ```python
   _ensure_package_init_files(handwritten_dir, python_path.directory,
       '"""Handwritten implementations."""\n')
   ```

4. **`_generate_stencils()`** (lines 429-437): Same pattern, remove `created_namespaces` set.

**Testing:**
- Unit test: Create a path `a/b/c`, verify `__init__.py` exists in `a/`, `a/b/`, and `a/b/c/`
- Integration: Regenerate solar_battery, verify `modules/solarbatterydesign/__init__.py` exists
- Existing tests must still pass

---

### Bug 3: FORMULA Module Input Type Mismatch

**File:** `src/sysml_codegen/cli/__init__.py`
**Function:** `_generate_computed_attr_modules()` (line 265)

**Change:** One line:

```python
# Before (line 265):
{"name": n, "type_hint": "Float", "description": f"Input {n}"}
# After:
{"name": n, "type_hint": "float", "description": f"Input {n}"}
```

**Also update** the `primitive_types` collection (lines 270-274) to not add `"Float"` from input types (since inputs are now `"float"`, they won't match the `in ("Float", "Int", ...)` check). The `primitive_types.add("Float")` at line 274 already ensures `Float` is imported for the output type.

Actually, since `"float"` is NOT in the set `("Float", "Int", "String", "Bool")`, the loop at lines 271-273 simply won't add anything for inputs. Line 274 adds `Float` for output. So **no additional changes** are needed to the primitive_types logic.

**Testing:**
- Unit test: Verify generated FORMULA module Input class fields use `float` type
- Verify FORMULA module output is still `Float` (RootModel[float])
- Existing FORMULA module tests must pass

---

### Bug 2: FORMULA/EXPOSE Backtracker Wiring

**File:** `src/sysml_codegen/analysis/dependency_backtracker.py`

**Change A: Extend `_computed_attr_index` keys** (in `__init__`, lines 138-145)

Add SysML qualified name key as a third lookup format per FORMULA attribute:

```python
self._computed_attr_index: dict[str, ComputedAttributeData] = {}
for ca in self._computed_attributes:
    if ca.classification != ComputedAttributeClassification.FORMULA:
        continue
    if ca.compilability != Compilability.FULLY_COMPILABLE:
        continue
    # Existing keys
    self._computed_attr_index[f"{ca.owning_part_name}.{ca.python_name}"] = ca
    self._computed_attr_index[ca.python_name] = ca
    # NEW: SysML qualified name key (what FeatureReferenceExpression produces)
    if ca.owning_part_qualified_name:
        sysml_qn = f"{ca.owning_part_qualified_name}::{ca.name}"
        self._computed_attr_index[sysml_qn] = ca
```

**Change B: Normalize lookup path** (in `_trace_dependencies`, lines 397-400)

Extend the fallback to handle `::` separator:

```python
ca = self._computed_attr_index.get(binding.source_path)
if ca is None and "." in binding.source_path:
    bare = binding.source_path.split(".")[-1]
    ca = self._computed_attr_index.get(bare)
# NEW: Handle SysML qualified names with :: separator
if ca is None and "::" in binding.source_path:
    bare = binding.source_path.split("::")[-1]
    ca = self._computed_attr_index.get(bare)
```

**Change C: Generalize `::` normalization to `_resolve_binding_to_usage()`** (in `_resolve_binding_to_usage`, around line 700)

**Resolution (from design review investigation):** The backtracker's existing transitive resolution path already handles EXPOSE_PURE correctly — `_design_attr_binding_index` (Strategy 4 in `_resolve_binding_to_usage`) maps EXPOSE_PURE attributes like `e2e_plant.total_capex` -> `component_cost.total_cost` and recursively resolves to the CalcUsage output. No separate EXPOSE_PURE index is needed.

The transitive path fails only when `source_path` is in `::` qualified name format (e.g., `"E2EAttrExprDesign::e2e_plant::total_capex"`), because `_design_attr_binding_index` keys use dotted format. This is the **same root cause** as the FORMULA lookup failure in Change B.

Rather than adding `::` normalization piecemeal to individual lookup sites, add a single normalization step at the top of `_resolve_binding_to_usage()` to convert `::` paths to dotted format before applying existing resolution strategies:

```python
def _resolve_binding_to_usage(self, binding_source: str, visited=None):
    # NEW: Normalize :: qualified names to dotted format for index lookups
    if "::" in binding_source:
        parts = binding_source.split("::")
        # Try "parent.attr" format (last two segments)
        if len(parts) >= 2:
            dotted = f"{parts[-2]}.{parts[-1]}"
            result = self._resolve_binding_to_usage(dotted, visited)
            if result is not None:
                return result
            # Also try bare name (last segment only)
            result = self._resolve_binding_to_usage(parts[-1], visited)
            if result is not None:
                return result
    # ... existing resolution strategies unchanged ...
```

This fixes EXPOSE_PURE resolution (via Strategy 4 transitive path) and any other binding format that uses `::` separators, without requiring a separate index.

**Note on collision risk for bare-name keys (Change A):** The bare-name key in `_computed_attr_index` (e.g., `"power_mw"`) creates a many-to-one mapping. If two parts have FORMULA attributes with the same bare name, the last indexed wins. This is acceptable in practice because: (1) the bare-name lookup is a fallback after dotted and `::` lookups fail, and (2) FORMULA attributes are rare and unlikely to collide across parts in current models. If this becomes an issue, the bare-name fallback can be removed — the `::` normalization in Change C provides a more reliable resolution path.

**Testing:**
- Unit test: Binding with source_path `"E2EAttrExprDesign::e2e_plant::power_mw"` resolves to FORMULA computed attr
- Unit test: Binding with source_path `"e2e_plant.power_mw"` still resolves (existing format)
- Unit test: Binding with source_path `"power_mw"` still resolves (bare name)
- Unit test: EXPOSE_PURE attribute `total_capex` resolves to MODULE_OUTPUT (not ENTRY_POINT)
- Integration: e2e_attr_expr backtracking produces MODULE_OUTPUT resolutions for patterns 10-12

---

### Bug 1: FORMULA Entry Point Omission

**File:** `src/sysml_codegen/resolution/graph_builder.py`
**Function:** `build_computation_graph()` (lines 65-180)

**Change:** Add Step 6.6 after Step 6.5 to rebuild param_groups with the full entry_points set.

Since `param_groups` is NOT used during module building (Steps 6 and 6.5 use `entry_points` dict and `group_deriver.classify()` directly), it is safe to rebuild it after all entry points have been created.

**Prerequisite refactoring:** Before adding Step 6.6:

1. **Extract `_convert_derived_groups()`** from the conversion logic in `_group_entry_points_via_deriver()` (lines 371-413). This shared helper converts `list[DerivedParameterGroup]` + `entry_points` dict -> `list[ParameterGroup]`. Both Step 5 and Step 6.6 will use it.

2. **Remove unused `param_groups` parameter** from `_build_pipeline_module()` (line 821) and `_build_computed_attr_module()` (line 627). Neither function references `param_groups` in its body — the parameter is vestigial. Remove it from the signatures and from the call sites at lines 145 and 165. This makes the data flow honest: `param_groups` is built at Step 5, rebuilt at Step 6.6, and consumed only by `ComputationGraph(entry_point_groups=param_groups)`.

```python
    # Step 6.5: Build computed attribute modules
    if computed_attributes:
        for ca in computed_attributes:
            ...
            modules.append(module)

    # Step 6.6: Rebuild param_groups with ALL entry points
    # FORMULA modules (Step 6.5) may have added new entry points to the
    # entry_points dict. Rebuild param_groups to include them.
    all_ep_names = set(entry_points.keys())
    raw_groups = group_deriver.derive_groups()
    for group in raw_groups:
        group.parameters = [
            p for p in group.parameters
            if p.name in all_ep_names
        ]
    filtered_groups = [g for g in raw_groups if g.parameters]

    # Convert DerivedParameterGroup -> ParameterGroup (Pydantic)
    # Reuse same conversion logic as _group_entry_points_via_deriver
    param_groups = []
    for dg in filtered_groups:
        params = []
        for ps in dg.parameters:
            if ps.name in entry_points:
                ep = entry_points[ps.name]
                if ep.default_value is None and ps.default_value is not None:
                    ep = EntryPoint(
                        qualified_name=ep.qualified_name,
                        simple_name=ep.simple_name,
                        entry_type=ep.entry_type,
                        default_value=ps.default_value,
                        source_calc_usage=ep.source_calc_usage,
                        param_group=ep.param_group,
                    )
                params.append(ep)
        source_file = (
            Path(dg.source_identifier) if dg.source_identifier else Path("unknown.sysml")
        )
        param_groups.append(
            ParameterGroup(
                name=dg.name,
                class_name=dg.class_name,
                source_file=source_file,
                parameters=params,
            )
        )
```

**Refactoring note:** The `_convert_derived_groups()` extraction is listed as a prerequisite above. Step 6.6 calls the shared helper rather than duplicating the conversion inline. `_group_entry_points_via_deriver()` at Step 5 is also refactored to use the same helper.

**Testing:**
- Unit test: After `build_computation_graph()`, verify all FORMULA module entry points appear in `entry_point_groups`
- Unit test: Verify e2e_attr_expr param_groups contain the 7 FORMULA input parameters
- Integration: e2e_attr_expr codegen produces `design_params.py` with all FORMULA fields
- Integration: e2e_attr_expr codegen produces `design_params.json` with all FORMULA defaults

---

### Bug 5: Smart-Regen Stub Upgrade

**File:** `src/sysml_codegen/cli/__init__.py`
**Function:** `_generate_stencils()` (lines 459-461)

**Change:** Replace the unconditional preserve with a stub-detection check:

```python
            else:
                # Smart-regen: signature unchanged. Check if stub can be upgraded.
                existing_content = output_path.read_text()
                is_stub = "raise NotImplementedError" in existing_content
                has_auto_impl = (
                    compilation_result is not None
                    and compilation_result.overall_compilability == Compilability.FULLY_COMPILABLE
                )
                if is_stub and has_auto_impl:
                    # Upgrade stub to auto-implementation
                    backup_implementation(output_path, backup_dir)
                    code = generate_implementation(
                        calc_def, template_env, output_path, config.package_name,
                        compilation_result=compilation_result,
                    )
                    if code:
                        output_path.write_text(code)
                    stats["regenerated"] += 1
                    logger.debug(f"Upgraded stub to auto-impl: {output_path.name}")
                else:
                    stats["preserved"] += 1
                    logger.debug(f"Preserved stencil ({reason}): {output_path.name}")
```

**Import needed:** Add `Compilability` import at top of function (or at file level):
```python
from sysml_codegen.extraction.expression_compiler import Compilability
```

**Safety analysis:**
- Files with `raise NotImplementedError` are stubs (from `implementation_stencil.py.jinja2` template)
- Hand-written implementations NEVER contain `raise NotImplementedError` (the whole point of implementing is to replace it)
- Auto-implemented files contain `AUTO_IMPLEMENTED = True` sentinel AND don't contain `raise NotImplementedError`
- This logic correctly distinguishes: stub -> upgradeable, hand-written -> preserved, auto-impl -> preserved

**Testing:**
- Unit test: Stub file with FULLY_COMPILABLE result -> upgraded
- Unit test: Hand-written file (no NotImplementedError) with FULLY_COMPILABLE -> preserved
- Unit test: Auto-implemented file (AUTO_IMPLEMENTED = True) -> preserved
- Unit test: Stub file without compilation result -> preserved
- Integration: solar_battery `--smart-regen` upgrades 10 stubs, preserves 5 hand-written

---

### Bug 4: ExitPoint Float Write Handler

**Problem:** Multi-output CalcUsage modules produce bare `float` values on channels. The pipeline YAML exit_point declares type `float` for these channels. TEAx ExitPoint has no handler for serializing bare `float` to JSON files.

**Prior art:** The fusion_modeling project (2024-12-24) established that the type asymmetry (single-output = RootModel, multi-output = bare primitive) is correct TEAx architecture.

**Root cause:** TEAx's ExitPoint only handles Pydantic model serialization (`.model_dump_json()`). It has no handler for bare Python primitives (`float`, `int`, etc.).

**Fix location:** TEAx, not sysml-codegen. The sysml-codegen pipeline YAML generation is already correct:
- `pipeline.py:_build_exit_points()` correctly declares `float` for multi-output channels (line 224)
- `pipeline.py:_output_to_context()` correctly declares `RootModel[float]` for single-output channels (line 189)
- No changes needed in sysml-codegen.

**TEAx fix needed:** ExitPoint should natively handle bare primitive types (`float`, `int`, `str`, `bool`) by serializing them to JSON using `json.dump()`. This is a small, well-scoped addition to TEAx's output router — add a primitive write handler alongside the existing Pydantic model handler.

**sysml-codegen action:** None. File a task in fusion-tea for TEAx ExitPoint primitive support.

**Testing:**
- E2E: After TEAx fix, e2e_attr_expr pipeline executes with all multi-output channels serialized to JSON
- E2E: Solar battery pipeline executes with all channels serialized

---

## Potential Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Bug 2 EXPOSE_PURE transitive resolution doesn't work for e2e_attr_expr | Medium | Medium | Test transitive path first. If it fails, implement EXPOSE_PURE index. |
| Bug 6 underscore collapsing changes existing qualified names | Low | Medium | Only collapses within `sanitize_name()` (individual segments). Qualified names use `__` join externally. Run full test suite. |
| Bug 1 param_group rebuild produces different groupings | Low | Low | Same deriver, same data. Only difference is including FORMULA EPs. |
| Bug 5 false positive on `raise NotImplementedError` in hand-written code | Very Low | Medium | Hand-written implementations replace the raise. Checked: template-generated stubs always have this pattern. |
| Bug 4 TEAx ExitPoint fix delayed | Low | Medium | Bug 4 is a TEAx fix, not sysml-codegen. File task in fusion-tea. E2E validation for multi-output serialization blocked until TEAx fix lands. |

---

## Integration Strategy

### Implementation Phases

**Phase 1 (Independent fixes):** Bugs 6, 7, 3
- No dependencies between them or on other code
- Can be implemented and tested independently
- Each has unit tests that verify the fix in isolation

**Phase 2 (Core backtracker/graph builder):** Bugs 2, 1
- Bug 2 first (backtracker wiring), then Bug 1 (param_groups)
- These interact but the implementation order ensures Bug 2 provides correct resolutions before Bug 1 rebuilds groups

**Phase 3 (Generation enhancements):** Bug 5
- Bug 5 (smart-regen) is independent
- Bug 4 (exit_point) is a TEAx fix — file task in fusion-tea, no sysml-codegen changes

### Files Modified (Summary)

| File | Bugs | Changes |
|------|------|---------|
| `core/qualified_names.py` | 6 | Add `re.sub` to `sanitize_name()` |
| `extraction/extractor.py` | 6 | Remove `_sanitize_name()`, use canonical import |
| `cli/__init__.py` | 3, 5, 7 | Fix type hint, add `_ensure_package_init_files()`, upgrade stub check |
| `analysis/dependency_backtracker.py` | 2 | Extend index keys, normalize lookup |
| `resolution/graph_builder.py` | 1 | Add Step 6.6 param_groups rebuild |

---

## Validation Approach

### Per-Bug Unit Tests

Each bug gets targeted unit tests (described in each section above). Tests are placed in existing test files or new test files as appropriate.

### E2E Validation

After all 7 fixes:

1. **e2e_attr_expr model:** `uv run sysml-codegen generate --models models/tests/e2e_attr_expr/ --output generated/e2e_attr_expr --package-name e2e_attr_expr --overwrite`
   - Verify: No errors
   - Verify: All 16 ground truth values pass via `verify_pipeline.py`
   - Verify: Zero manual file modifications needed

2. **solar_battery model:** `uv run sysml-codegen generate --models models/tests/solar_battery/ --output generated/solar_battery --package-name solar_battery --overwrite`
   - Verify: No SyntaxError in generated schema (Bug 6)
   - Verify: `modules/solarbatterydesign/__init__.py` exists (Bug 7)
   - Verify: FORMULA module inputs use `float` (Bug 3)

3. **Regression:** `uv run pytest tests/ -v` -> 285+ tests, 0 failures

---

**Next Step:** After approval -> `/_my_plan` for implementation planning
