# Design: Template CalcUsage Detection & Virtual Instantiation

**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-02-10 06:53 UTC
**Branch:** cost-pattern
**Commit:** 93f0a55
**Epic:** COST-PATTERN Item 2

## Overview

Extend `extract_calculation_usages()` to detect CalcUsages owned by PartDefinitions (templates), find all PartUsages that instantiate those PartDefs, and generate virtual `CalcUsageData` instances per instantiation — with hierarchy-aware qualified names and bindings copied from the template.

## Related Artifacts

- **Spec:** `.project/active/template-detection/spec.md`
- **Spike report:** `.project/active/hierarchy-spike/report.md`
- **Epic:** `.project/backlog/epic_costed_component_pattern.md` (Item 2)
- **Research:** `.project/research/20260109-205122_cost-modeling-codegen-changes.md`

---

## Research Findings

### 1. Current Extraction Pipeline (usage_extractor.py)

The extraction pipeline is a single file at `src/sysml_codegen/extraction/usage_extractor.py` (451 lines). Key components:

- **`extract_calculation_usages()`** (line 136): Iterates `SysideAdapter.elements_of_type(model, "CalculationUsage")`, calls `_extract_single_usage()` for each, returns `list[CalcUsageData]` + `ExtractionReport`.
- **`_extract_single_usage()`** (line 174): Extracts instance name, calc def info, bindings, parent path, qualified name. Returns `CalcUsageData`. Does NOT check whether the owning type is PartDefinition vs PartUsage.
- **`_get_parent_part_path()`** (line 419): Walks the AST ownership chain via `current.owner → owner.owning_related_element`, collecting only `PartUsage` names. Skips PartDefinitions silently.
- **`_extract_bindings()`** (line 240): Extracts CHAIN, REFERENCE, LITERAL, EXPRESSION, UNBOUND bindings from calc usage `owned_members`.

### 2. CalcUsageData Model (usage_extractor.py:87-123)

Currently has 10 fields: `instance_name`, `calc_def_name`, `calc_def_qualified_name`, `module_type`, `bindings`, `unbound_params`, `source_file`, `source_line`, `parent_part_path`, `qualified_name`. No template detection fields.

### 3. Qualified Name Construction (core/qualified_names.py)

- **`build_element_qualified_name()`** (line 39): Walks AST ownership chain, collects sanitized names, joins with `__`. For a library PartUsage like `pv_module` (owned by `Solar Array` PartDef), produces `SolarBatteryLibrary__Solar_Array__pv_module` — this is the **library-relative** path, NOT the design-relative path needed for virtual instances.
- **`sanitize_name()`** (line 13): Strips quotes, replaces spaces/special chars, collapses underscores. The canonical implementation (duplicate in extractor.py was removed in Bug 6 fix).

### 4. AST Access Patterns (validated by spike Q1, Q7)

- **Template detection:** `type(elem.owning_type).__name__` returns `'PartDefinition'` (template) or `'PartUsage'` (concrete). Direct attribute access on the element — no adapter call needed. Spike Q1 validated on `PV Module.cost_model`, `Solar Array.allocation_model`, `solar_battery_plant.energy_production`.
- **Type resolution:** `for t in usage.types: ...` gets the PartDefinition for a PartUsage. Spike Q7 validated full 8-step chain traversal. The codebase does NOT currently use `.types` on AST elements anywhere.
- **`owning_type` vs `owner` chain:** The codebase's `_get_parent_part_path()` walks `owner → owning_related_element` (a KerML membership indirection). The spike accesses `owning_type` directly — a cleaner API that returns the immediate owning Type element. Both work; `owning_type` is more direct for our needs.
- **`owned_members`:** Used throughout the codebase (8 call sites). Standard pattern: `for member in elem.owned_members:` with `SysideAdapter.is_instance()` type checks.
- **`owned_redefinitions`:** Present on `part redefines` PartUsages (non-empty), absent on plain `part` PartUsages (empty). Spike Q3 validated this distinguisher.

### 5. Critical Design-Phase Verification (from spec acceptance criteria)

**Verification 1: `owning_type` access pattern**
The spike accessed `elem.owning_type` directly (spike_hierarchy_ast.py:266). The codebase's `_get_parent_part_path()` uses `owner.owning_related_element` — a different traversal. Both access the AST, but `owning_type` is the KerML/SysML standard attribute that returns the containing Type. Since the spike validated it works on the solar_battery model, the design uses `owning_type` directly.

**Verification 2: `build_element_qualified_name()` for virtual instances**
`build_element_qualified_name()` walks the AST ownership chain. For a library PartUsage like `pv_module`, it produces `SolarBatteryLibrary__Solar_Array__pv_module` — the library-relative path. Virtual instances need the **design-relative** path: `SolarBatteryDesign__solar_battery_plant__solar_array__pv_module__cost_model`. **Conclusion: We CANNOT use `build_element_qualified_name()` on library PartUsages.** The virtual qualified name must be constructed manually via the recursive instantiation path algorithm described below.

**Verification 3: PartUsage finder via `.types`**
The spike Q7 demonstrated `for t in sa_usage.types: sa_def = t; break` to get the PartDef from a PartUsage. This works. The design uses this pattern for type matching in the part usage index.

### 6. `part redefines` Deduplication Concern

The design file has `part redefines solar_array : 'Solar Array' { ... }` inside `solar_battery_plant`. This creates a second PartUsage of `Solar Array` alongside the library's plain `part solar_array : 'Solar Array'`. Both type `Solar Array` and would both be returned by `elements_of_type("PartUsage")`. Without deduplication, the recursive path builder would produce duplicate virtual CalcUsages with identical qualified names. **Solution:** Deduplicate virtual CalcUsages by `qualified_name` after expansion.

### 7. Pipeline Integration Point (initialization.py)

`build_pipeline_context()` (initialization.py:199) calls `extract_calculation_usages()` at Step 3 (line 252). The returned CalcUsageData list flows through Steps 4-7 (design attrs, parameter groups, backtracker, graph builder). Adding `expand_templates=True` to the Step 3 call is the integration point — virtual CalcUsages replace templates transparently.

### 8. Model Structure (solar_battery_model)

The solar_battery model has 9 leaf PartDefs with embedded `cost_model` CalcUsages, 1 allocation CalcUsage (`Solar Array.allocation_model`), and 5 system-level CalcUsages (in `solar_battery_plant` PartUsage). The hierarchy is 4 levels deep:
- SolarBatteryDesign → solar_battery_plant → solar_array → pv_module → cost_model
- SolarBatteryDesign → solar_battery_plant → battery_system → battery_pack → cost_model
- etc.

---

## Proposed Design

### Component 1: Data Model Extensions

**File:** `src/sysml_codegen/extraction/usage_extractor.py`
**Location:** `CalcUsageData` class (line 87)

Add three fields after `qualified_name`:

```python
# Template detection fields
is_template: bool = False
owning_part_def_qn: str | None = None
raw_element: object | None = None
```

- `is_template`: `True` when CalcUsage is owned by a PartDefinition (detected via `owning_type`)
- `owning_part_def_qn`: The `__`-separated qualified name of the owning PartDef (from `build_element_qualified_name(owning_type)`). Used as lookup key in the part usage index.
- `raw_element`: The original SysIDE AST element, stored for potential re-inspection during instantiation. Uses `object | None` to match the codebase convention for AST element storage (see `BindingInfo.source_instance_elem`, `BindingInfo.source_attribute_elem`).

All three fields have defaults, preserving backward compatibility with existing CalcUsageData construction.

### Component 2: Template Detection

**File:** `src/sysml_codegen/extraction/usage_extractor.py`
**Location:** Inside `_extract_single_usage()` (line 174), before the `return CalcUsageData(...)` at line 226

**Logic:**
```python
# Template detection: check if owning type is PartDefinition
# Uses SysideAdapter.is_instance() for consistency with codebase convention
# (see constraint_extractor.py:162 for precedent)
owning_type = getattr(elem, "owning_type", None)
is_template = False
owning_part_def_qn = None

if owning_type is not None and SysideAdapter.is_instance(owning_type, "PartDefinition"):
    is_template = True
    owning_part_def_qn = build_element_qualified_name(owning_type)
```

Pass these fields plus `raw_element=elem` to the `CalcUsageData()` constructor.

**Rationale:** Uses `SysideAdapter.is_instance()` rather than `type().__name__` to maintain adapter abstraction consistency. The spike Q1 validated `type(elem.owning_type).__name__` works, but `is_instance()` is the standard pattern in this codebase (38 call sites across 7 files, including `is_instance(current, "PartDefinition")` at `constraint_extractor.py:162`). `owning_type` is a standard KerML attribute accessed directly on the element. `build_element_qualified_name()` is appropriate here because we're getting the PartDef's own QN (its library path), which we need as a consistent key for the part usage index.

### Component 3: Part Usage Index Builder

**File:** `src/sysml_codegen/extraction/usage_extractor.py`
**New function**

```python
def _build_part_usage_index(model: Any) -> dict[str, list[Any]]:
    """Build index mapping PartDef qualified names to their PartUsage elements.

    Iterates all PartUsage elements in the model. For each, resolves its
    typed PartDefinition via `usage.types` (spike Q7 pattern), computes
    the PartDef's qualified name, and indexes the PartUsage under that key.

    Args:
        model: Parsed SysIDE model.

    Returns:
        Dict mapping PartDef QN (e.g., "SolarBatteryLibrary__PV_Module")
        to list of PartUsage AST elements that type that PartDef.
    """
```

**Logic:**
1. Iterate `SysideAdapter.elements_of_type(model, "PartUsage")`
2. For each PartUsage, get the typed PartDef via `next(iter(usage.types))` (with try/except)
3. Compute PartDef QN via `build_element_qualified_name(part_def)`
4. Store: `index[part_def_qn].append(usage_element)`

**Note on `.types`:** The `.types` attribute returns an iterable of Type elements. We take the first (primary type). The spike Q7 validated this pattern works for PartUsage → PartDef resolution. The try/except handles edge cases where `.types` is empty or inaccessible.

**FR-10 (Specialization chains):** The index matches by **direct type** only. If a PartUsage types a specialized PartDef (e.g., `part x : SpecializedWidget` where `SpecializedWidget :> Widget`), CalcUsages from the parent `Widget` PartDef would not be found via this index. This is acceptable for Item 2 because:
- The solar_battery model uses direct typing exclusively (no specialization indirection in PartUsage→PartDef type relationships)
- Item 3 already handles specialization chains as part of `:>>` redefinition resolution, which is the broader context where this matters
- Adding specialization traversal here would require iterating `owned_specializations` recursively, which introduces complexity better addressed alongside the other hierarchy-resolution work in Item 3

If specialization chain support is needed earlier, the index builder can be extended to also index a PartUsage under its type's supertype QNs by walking `part_def.owned_specializations[*].general`.

### Component 4: Recursive Instantiation Path Resolver

**File:** `src/sysml_codegen/extraction/usage_extractor.py`
**New function**

This is the core algorithm that computes design-relative paths for library PartUsages.

```python
def _find_instantiation_paths(
    target_part_def_qn: str,
    part_usage_index: dict[str, list[Any]],
) -> list[str]:
    """Find all design-relative qualified paths to PartUsages of a target PartDef.

    Recursively resolves the instantiation chain from design root through
    intermediate PartDefs to the target. Returns fully qualified paths using
    the __ separator per ADR-003.

    Args:
        target_part_def_qn: QN of the PartDef to find instantiation paths for.
        part_usage_index: Prebuilt index from _build_part_usage_index().

    Returns:
        List of design-relative qualified name prefixes. For PV Module in
        the solar_battery model, returns:
        ["SolarBatteryDesign__solar_battery_plant__solar_array__pv_module"]
    """
```

**Algorithm:**

1. Look up `part_usage_index[target_part_def_qn]` → list of PartUsage elements
2. If empty, return `[]` (no instantiations)
3. For each PartUsage:
   a. Get `owning_type = getattr(usage, "owning_type", None)`
   b. If `owning_type is not None and SysideAdapter.is_instance(owning_type, "PartDefinition")`:
      - This PartUsage is inside another PartDef (e.g., `pv_module` in `Solar Array`)
      - Get parent PartDef QN: `build_element_qualified_name(owning_type)`
      - **Recurse:** `parent_paths = _find_instantiation_paths(parent_part_def_qn, index)`
      - For each parent path, append `__{sanitize_name(usage.name)}`
   c. Else (owned by Package, PartUsage, or other non-PartDef):
      - This is a terminal node (concrete design context)
      - Path = `build_element_qualified_name(usage)` (this IS the design-relative path for top-level PartUsages)
      - Add to results
4. Return deduplicated list of paths

**Walk-through for `PV Module` in solar_battery:**

```
_find_instantiation_paths("SolarBatteryLibrary__PV_Module", index)
  → usages: [pv_module (in Solar Array PartDef)]
  → pv_module.owning_type = Solar Array (PartDefinition) → recurse
    _find_instantiation_paths("SolarBatteryLibrary__Solar_Array", index)
      → usages: [solar_array (in Solar Battery Plant PartDef), solar_array redefines (in solar_battery_plant PartUsage)]
      → library solar_array.owning_type = Solar Battery Plant (PartDef) → recurse
        _find_instantiation_paths("SolarBatteryLibrary__Solar_Battery_Plant", index)
          → usages: [solar_battery_plant (in SolarBatteryDesign Package)]
          → solar_battery_plant.owning_type = SolarBatteryDesign (Package) → terminal
          → path = build_element_qualified_name(solar_battery_plant) = "SolarBatteryDesign__solar_battery_plant"
        → return ["SolarBatteryDesign__solar_battery_plant"]
      → append "__solar_array" → "SolarBatteryDesign__solar_battery_plant__solar_array"
      → design solar_array redefines.owning_type = solar_battery_plant (PartUsage) → terminal
      → path = build_element_qualified_name(redefines_solar_array) = "SolarBatteryDesign__solar_battery_plant__solar_array"
    → deduplicate → ["SolarBatteryDesign__solar_battery_plant__solar_array"]
  → append "__pv_module" → "SolarBatteryDesign__solar_battery_plant__solar_array__pv_module"
→ return ["SolarBatteryDesign__solar_battery_plant__solar_array__pv_module"]
```

**Deduplication:** Both the library `solar_array` and design `part redefines solar_array` resolve to the same qualified path. Deduplication by set membership avoids duplicate virtual CalcUsages. Performed at each recursion level.

**Recursion guard:** Add a `_visited` set parameter to prevent infinite loops from circular specialization chains (defensive — not expected in well-formed models). Maximum depth of ~10 is sufficient for any practical hierarchy.

### Component 5: Virtual CalcUsage Generator

**File:** `src/sysml_codegen/extraction/usage_extractor.py`
**New function**

```python
def _expand_template_calc_usages(
    model: Any,
    calc_usages: list[CalcUsageData],
    warnings: list[str],
) -> list[CalcUsageData]:
    """Replace template CalcUsages with virtual per-instance CalcUsages.

    Args:
        model: Parsed SysIDE model.
        calc_usages: Extracted CalcUsages (may include templates).
        warnings: List to append warnings to.

    Returns:
        Expanded list: concrete CalcUsages unchanged, templates replaced
        by virtual instances (one per PartUsage instantiation).
    """
```

**Logic:**

1. Build part usage index via `_build_part_usage_index(model)`
2. Separate CalcUsages into concrete (pass through) and templates (to expand)
3. For each template CalcUsage:
   a. Call `_find_instantiation_paths(template.owning_part_def_qn, index)`
   b. If no paths found, emit warning and drop the template (FR-23)
   c. For each path, create a virtual `CalcUsageData`:

```python
def _create_virtual_calc_usage(
    template: CalcUsageData,
    instantiation_path: str,
) -> CalcUsageData:
    """Create a virtual CalcUsage for a specific instantiation path.

    Args:
        template: The template CalcUsageData from the PartDefinition.
        instantiation_path: Full design-relative path to the PartUsage
            (e.g., "SolarBatteryDesign__solar_battery_plant__solar_array__pv_module").

    Returns:
        New CalcUsageData with design-relative qualified name and
        bindings copied from the template.
    """
    calc_name = sanitize_name(template.instance_name)
    qualified_name = f"{instantiation_path}__{calc_name}"

    # FR-14: instance_name derived from qualified_name (flattened with __).
    # Must be unique across all CalcUsages because the backtracker uses
    # _usage_by_name[instance_name] as a lookup key (dependency_backtracker.py:166).
    instance_name = qualified_name

    # Build dot-separated parent_part_path from the instantiation path
    # Strip the leading package segment(s) and join remaining with dots
    path_segments = instantiation_path.split("__")
    # Skip the first segment (package name) for parent_part_path
    part_segments = path_segments[1:] if len(path_segments) > 1 else path_segments
    parent_part_path = ".".join(part_segments)

    # Shallow copy of bindings list — the BindingInfo objects are shared with
    # the template. This is safe because downstream code (backtracker, graph
    # builder) reads bindings but does not mutate BindingInfo fields.
    # If mutation becomes necessary in the future, switch to copy.deepcopy().
    return CalcUsageData(
        instance_name=instance_name,
        calc_def_name=template.calc_def_name,
        calc_def_qualified_name=template.calc_def_qualified_name,
        module_type=template.module_type,
        bindings=list(template.bindings),      # Shallow copy; BindingInfo shared (FR-16)
        unbound_params=list(template.unbound_params),  # Copy as-is (FR-17)
        source_file=template.source_file,
        source_line=template.source_line,
        parent_part_path=parent_part_path,
        qualified_name=qualified_name,
        is_template=False,                     # Now concrete (FR-18)
        owning_part_def_qn=None,
        raw_element=template.raw_element,
    )
```

**Key decisions:**
- **`instance_name` = `qualified_name` (FR-14):** The backtracker indexes CalcUsages by `instance_name` in `_usage_by_name` (dependency_backtracker.py:166-167) and logs collision warnings on duplicates. Using the full `__`-separated qualified name ensures uniqueness across all virtual instances. This differs from concrete CalcUsages which use short names (e.g., `energy_production`), but those are already unique within the model.
- **Bindings shallow-copied (FR-16):** `list(template.bindings)` creates a new list but shares the `BindingInfo` objects. Internal bindings like `in wattage = wattage` reference the parent PartDef's attribute and are left unresolved — the backtracker in Item 4 will resolve them through the `:>>` redefinition chain. Downstream code reads bindings but does not mutate `BindingInfo` fields, so sharing is safe.
- **Unbound params copied as-is (FR-17):** Algorithm parameters with defaults (e.g., `cost_per_watt`) remain unbound. The backtracker handles default resolution.
- **`parent_part_path`** reflects the design instantiation path (FR-19), not the template's original library path.

### Component 6: Integration into `extract_calculation_usages()`

**File:** `src/sysml_codegen/extraction/usage_extractor.py`
**Location:** `extract_calculation_usages()` (line 136)

**Changes:**

1. Add `expand_templates: bool = True` parameter (FR-20)
2. After the extraction loop (line 161), add template expansion:

```python
# Expand template CalcUsages to per-instance virtuals
if expand_templates:
    usages = _expand_template_calc_usages(model, usages, warnings)
```

3. The `ExtractionReport` (line 163) is built AFTER expansion, so `total_usages` reflects the expanded count.

**No changes needed to `initialization.py`** — it already calls `extract_calculation_usages()` without keyword args, so the default `expand_templates=True` activates automatically.

### Component 7: Logging and Warning Routing

Add structured logging at key points:

```python
logger.info("Template detection: %d templates, %d concrete CalcUsages", template_count, concrete_count)
logger.info("Template expansion: %d templates → %d virtual instances", template_count, virtual_count)
```

**FR-23 warning routing:** When a template CalcUsage has zero PartUsage instantiations, the warning goes to **both** channels:
1. `logger.warning(...)` — for runtime log output
2. `warnings.append(...)` — for the `ExtractionReport.warnings` list returned to callers

This dual routing matches the existing pattern in `_extract_single_usage()` (line 187, 192) where warnings are appended to the `warnings` list AND the report is built from that list at line 163-168.

---

## Potential Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| `owning_type` not populated on some AST elements | Low | High | Spike validated on all 3 test targets. Use `getattr(elem, "owning_type", None)` with graceful fallback. |
| `.types` returns empty iterator for some PartUsages | Low | Medium | Use try/except with logging. Skip PartUsages without resolvable types. |
| Circular specialization chains cause infinite recursion | Very Low | High | Add `_visited` set parameter and max depth guard (10 levels). |
| `build_element_qualified_name()` produces inconsistent QNs across library/design elements | Low | High | Tested in walk-through above. QN consistency comes from AST structure, not file location. Both library and design elements for the same PartDef produce the same QN. |
| `part redefines` produces duplicate virtual CalcUsages | Medium | Low | Deduplication by `qualified_name` at each recursion level handles this cleanly. |
| Specialization chain PartUsages missed (FR-10) | Low | Medium | Deferred to Item 3. Solar_battery model uses direct typing exclusively. Index builder is extensible. |
| Performance with large models | Low | Low | Index built once per model, O(n) where n = PartUsage count. Recursion bounded by hierarchy depth. Solar_battery: ~15 PartUsages, depth 4. |

---

## Integration Strategy

### Upstream Dependencies
- No changes to `agentic-mbse`. The `SysideAdapter` API is used as-is.
- No changes to `core/qualified_names.py`. Existing `build_element_qualified_name()` and `sanitize_name()` are reused.

### Downstream Compatibility
- Virtual CalcUsages are standard `CalcUsageData` objects with `is_template=False`. The existing pipeline (backtracker, graph builder, generation) processes them identically to concrete CalcUsages.
- The three new fields (`is_template`, `owning_part_def_qn`, `raw_element`) have defaults, so existing code constructing `CalcUsageData` is unaffected.
- `expand_templates=True` by default means the integration is transparent — `build_pipeline_context()` needs no changes.

### What Changes
- **Modified:** `src/sysml_codegen/extraction/usage_extractor.py`
  - `CalcUsageData`: 3 new fields
  - `_extract_single_usage()`: template detection logic
  - `extract_calculation_usages()`: `expand_templates` parameter + expansion call
  - New functions: `_build_part_usage_index()`, `_find_instantiation_paths()`, `_expand_template_calc_usages()`, `_create_virtual_calc_usage()`
- **New:** `tests/unit/test_template_detection.py`

### What Does NOT Change
- `initialization.py` — uses default `expand_templates=True` automatically
- `dependency_backtracker.py` — virtual CalcUsages are regular CalcUsageData
- `graph_builder.py` — processes CalcUsageData generically
- `generation/` — no template awareness needed

---

## Validation Approach

### Unit Tests (`tests/unit/test_template_detection.py`)

Tests use mock AST elements (no real SysML models required). Mock objects simulate `owning_type`, `.types`, `owned_members`, and `name` attributes.

**Test Suite 1: Template Detection**
- `test_calc_in_part_def_is_template`: CalcUsage with `owning_type` = PartDefinition mock → `is_template=True`
- `test_calc_in_part_usage_is_concrete`: CalcUsage with `owning_type` = PartUsage mock → `is_template=False`
- `test_calc_with_no_owning_type_is_concrete`: CalcUsage without `owning_type` → `is_template=False`
- `test_owning_part_def_qn_set_for_template`: Verify `owning_part_def_qn` matches `build_element_qualified_name(owning_type)`
- `test_raw_element_stored`: Verify `raw_element` is the original AST element

**Test Suite 2: Part Usage Index**
- `test_index_maps_part_def_to_usages`: 2 PartUsages typing same PartDef → both in index
- `test_index_handles_quoted_names`: `part pv_module : 'PV Module'` → QN uses sanitized name
- `test_index_empty_types_skipped`: PartUsage with empty `.types` → not in index

**Test Suite 3: Instantiation Path Resolution**
- `test_single_level_path`: PartUsage in Package → direct path from `build_element_qualified_name`
- `test_two_level_path`: PartUsage in PartDef, PartDef instantiated by PartUsage in Package → composed path
- `test_three_level_path`: Full solar_battery-style chain → `Pkg__plant__array__module`
- `test_deduplication`: Library + `part redefines` both resolve to same path → single result
- `test_no_instantiations`: PartDef with no PartUsages → empty list + warning

**Test Suite 4: Virtual CalcUsage Generation**
- `test_virtual_calc_qualified_name`: `path__calc_name` format per ADR-003
- `test_virtual_calc_bindings_copied`: Bindings from template are copied to virtual
- `test_virtual_calc_is_not_template`: `is_template=False` on virtual instances
- `test_virtual_calc_parent_part_path`: Design-relative dot-separated path
- `test_multiple_usages_produce_multiple_virtuals`: 2 PartUsages → 2 virtual CalcUsages

**Test Suite 5: Integration**
- `test_expand_templates_true_replaces_templates`: Templates removed, virtuals added
- `test_expand_templates_false_preserves_templates`: Templates kept with `is_template=True`
- `test_concrete_usages_unchanged`: Non-template CalcUsages pass through unmodified
- `test_warning_on_no_instantiations`: Template with no PartUsages emits warning

### Mypy & Ruff
- `uv run mypy src/sysml_codegen/extraction/usage_extractor.py` — verify type annotations
- `uv run ruff check src/sysml_codegen/extraction/usage_extractor.py` — verify lint

### Regression
- `uv run pytest tests/` — all 313+ existing tests pass

---

Next Step: After approval → `/_my_implement` or `/_my_plan`
