---
date: 2026-01-09T20:51:22-08:00
researcher: Claude
topic: "Required Changes to sysml-codegen for Cost Modeling Support"
tags: [research, cost-modeling, sysml-codegen, tooling-gap, nested-calcs]
status: complete
last_updated: 2026-01-09
---

# Research: Required Changes to sysml-codegen for Cost Modeling Support

**Date**: 2026-01-09 20:51 PST
**Researcher**: Claude
**Research Type**: Architecture Gap Analysis (Usage Requirements → Library Capabilities)

## Research Question

Given the cost modeling requirements identified in fusion-tea's research reports, what changes are needed to the sysml-codegen library to support:
1. Nested cost models where parts "know" their own cost (calc usages in PartDefinitions)
2. Template instantiation (multiple PartUsages of same PartDefinition with embedded calcs)
3. Binding resolution through redefinition chains
4. Hierarchical cost rollup patterns
5. Full LCOE visibility with 20+ output channels

## Summary

- **Major Tooling Gap**: sysml-codegen extracts calc usages in PartDefinitions but does NOT instantiate them per PartUsage - this is the PRIMARY change required
- **Extraction Phase**: Must detect whether calc usage owner is PartDefinition vs PartUsage, then find all PartUsages instantiating that definition
- **Analysis Phase**: Must resolve bindings through redefinition chains (`:>> attribute = value`)
- **Resolution Phase**: Minor updates to handle virtual calc usages with resolved paths
- **Generation Phase**: No changes required - already supports multi-output, multi-module pipelines
- **Estimated Scope**: ~400-500 lines of new code in extraction + analysis phases

---

## Detailed Findings

### 1. Mapping Usage Needs to Library Capabilities

#### From fusion-tea Research Reports:

| Requirement | Current sysml-codegen Support | Gap |
|-------------|-------------------------------|-----|
| Calc usages inside PartDefinitions | Extracted as templates | NOT instantiated per PartUsage |
| Binding resolution through redefinition | NOT supported | Must resolve `:>> attr = value` |
| Hierarchical cost rollup | Multi-output supported | Pattern works if calcs are explicit |
| LCOE with 20+ outputs | Fully supported | No change needed |
| Cross-concept comparison | Exit points capture all outputs | No change needed |
| Nested part hierarchies | Parent path extraction exists | Must handle PartDef→PartUsage chain |

#### Key Insight

The "nested cost model" pattern where parts contain their own cost calculations is semantically correct in SysMLv2. The gap is purely in tooling:

```sysml
// This is VALID SysML and SHOULD work:
part def 'Magnet System' :> 'Costed Component' {
    attribute field_strength : Real;

    calc cost_model : MagnetSystemCostCalc {
        in field = field_strength;  // Binds to parent attribute
    }

    :>> capital_cost = cost_model.total;
}

// When instantiated:
part magnets : 'Magnet System' {
    :>> field_strength = 12.0;  // Redefinition
}
// magnets.capital_cost SHOULD work (inherits cost_model result)
```

**Current Behavior**: sysml-codegen finds `cost_model` calc usage owned by PartDefinition `'Magnet System'`, but generates only ONE module for the template - not per-instantiation modules.

**Required Behavior**: When `magnets : 'Magnet System'` is instantiated, create `magnets__cost_model` module with bindings resolved through redefinitions.

---

### 2. Current Architecture Analysis

#### 2.1 Extraction Phase (`extraction/usage_extractor.py`)

**Current Flow:**
1. `extract_calculation_usages()` iterates all `CalculationUsage` elements
2. `_extract_single_usage()` extracts data for each
3. `_get_parent_part_path()` builds parent path (lines 407-421)
4. Returns `CalcUsageData` with `parent_part_path` and `qualified_name`

**Gap at Line 417:**
```python
# Current: Only checks PartUsage
if SysideAdapter.is_instance(owning_elem, "PartUsage"):
    parts.insert(0, owning_elem.name)
# Missing: Does NOT check PartDefinition
```

**Key Data Structures:**
- `CalcUsageData.parent_part_path`: Dot-separated path (e.g., "blanket.heating")
- `CalcUsageData.qualified_name`: EQN with `__` separator
- `CalcUsageData.bindings`: List of `BindingInfo` with type and source

#### 2.2 Analysis Phase (`analysis/dependency_backtracker.py`)

**Current Flow:**
1. `DependencyBacktracker` builds lookup tables for usages
2. `find_required_modules()` does DFS to trace dependencies
3. `_trace_dependencies()` builds `binding_resolutions` dict
4. For each binding: resolve to MODULE_OUTPUT or ENTRY_POINT

**Critical: binding_resolutions Dict (Lines 179-188, 305-484)**
- Key: `"{usage_qualified_name}|{param_name}"`
- Value: `BindingResolution` with type + qualified target
- This is THE SINGLE SOURCE OF TRUTH for all wiring

**Gap**: No handling of redefinition chain resolution. When calc binding targets `'Magnet System'::field_strength` and PartUsage has `:>> field_strength = 12.0`, the binding should resolve to LITERAL 12.0.

#### 2.3 Resolution Phase (`resolution/graph_builder.py`)

**Current Flow:**
1. `build_computation_graph()` takes BacktrackingResult
2. `_build_pipeline_module()` uses `binding_resolutions` as single truth
3. Creates `PipelineModule` with `ModuleInput` sources

**Status**: Will work correctly IF extraction/analysis produce proper virtual usages.

#### 2.4 Generation Phase

**Current Flow:**
1. `generate_pipeline_yaml()` renders ComputationGraph
2. `generate_teax_module()` creates wrapper classes
3. Multi-output schemas generated automatically

**Status**: No changes needed. Already supports arbitrary module counts and multi-output patterns.

---

### 3. Required Changes

#### Change Set 1: Template Detection in Extraction

**File**: `src/sysml_codegen/extraction/usage_extractor.py`

**Change 1.1: Add owner type detection function**

```python
def _get_owning_type_info(elem: Any) -> tuple[str | None, Any | None]:
    """Get the owning type (PartDefinition or PartUsage) of an element.

    Returns:
        Tuple of (owner_type, owner_element) where owner_type is
        "PartDefinition", "PartUsage", or None.
    """
    current = elem
    while hasattr(current, "owner") and current.owner:
        owner = current.owner
        if hasattr(owner, "owning_related_element"):
            owning_elem = owner.owning_related_element
            if owning_elem:
                if SysideAdapter.is_instance(owning_elem, "PartDefinition"):
                    return ("PartDefinition", owning_elem)
                elif SysideAdapter.is_instance(owning_elem, "PartUsage"):
                    return ("PartUsage", owning_elem)
        current = owner
    return (None, None)
```

**Change 1.2: Add function to find PartUsages of a PartDefinition**

```python
def _find_part_usages_of_definition(
    model: Any,
    part_def: Any,
) -> list[tuple[Any, str]]:
    """Find all PartUsages that instantiate a given PartDefinition.

    Args:
        model: The parsed SysML model
        part_def: The PartDefinition element

    Returns:
        List of (PartUsage element, full qualified path) tuples
    """
    usages = []
    part_def_qn = SysideAdapter.get_qualified_name(part_def)

    for elem in SysideAdapter.elements_of_type(model, "PartUsage"):
        if _usage_instantiates_definition(elem, part_def, part_def_qn):
            path = _build_full_part_path(elem)
            usages.append((elem, path))

    return usages


def _usage_instantiates_definition(
    usage: Any,
    part_def: Any,
    part_def_qn: str,
) -> bool:
    """Check if a PartUsage instantiates a given PartDefinition."""
    if not hasattr(usage, "type") or not usage.type:
        return False

    for type_ref in usage.type:
        # Direct match
        if type_ref == part_def:
            return True
        # Qualified name match
        type_qn = SysideAdapter.get_qualified_name(type_ref)
        if type_qn == part_def_qn:
            return True
        # Check specialization chain
        if _is_specialization_of(type_ref, part_def_qn):
            return True

    return False


def _is_specialization_of(elem: Any, target_qn: str) -> bool:
    """Check if elem specializes a type with the given qualified name."""
    if not hasattr(elem, "owned_specializations"):
        return False
    for spec in elem.owned_specializations:
        if hasattr(spec, "general"):
            for general in spec.general:
                if SysideAdapter.get_qualified_name(general) == target_qn:
                    return True
                # Recursive check
                if _is_specialization_of(general, target_qn):
                    return True
    return False


def _build_full_part_path(elem: Any) -> str:
    """Build full dot-separated path from root to this element."""
    parts = []
    current = elem

    while current:
        if hasattr(current, "name") and current.name:
            if SysideAdapter.is_instance(current, "PartUsage"):
                parts.insert(0, current.name)

        # Navigate up
        if hasattr(current, "owner") and current.owner:
            owner = current.owner
            if hasattr(owner, "owning_related_element"):
                current = owner.owning_related_element
            else:
                break
        else:
            break

    return ".".join(parts)
```

**Change 1.3: Add raw_element to CalcUsageData**

```python
@dataclass
class CalcUsageData:
    # ... existing fields ...

    # NEW: Store raw AST element for template detection
    raw_element: Any = field(default=None, repr=False)

    # NEW: Flag indicating this is a template (owned by PartDefinition)
    is_template: bool = False

    # NEW: If template, the PartDefinition that owns this calc
    owning_part_def_qn: str | None = None
```

**Change 1.4: Update _extract_single_usage() to track owner info**

```python
def _extract_single_usage(...) -> CalcUsageData | None:
    # ... existing extraction ...

    # NEW: Detect owner type
    owner_type, owner_elem = _get_owning_type_info(elem)
    is_template = (owner_type == "PartDefinition")
    owning_part_def_qn = None
    if is_template and owner_elem:
        owning_part_def_qn = SysideAdapter.get_qualified_name(owner_elem)

    return CalcUsageData(
        # ... existing fields ...
        raw_element=elem,
        is_template=is_template,
        owning_part_def_qn=owning_part_def_qn,
    )
```

**Change 1.5: Add template instantiation expansion**

```python
def _instantiate_template_calc_usages(
    model: Any,
    calc_usages: list[CalcUsageData],
    warnings: list[str],
) -> list[CalcUsageData]:
    """Expand calc usages in PartDefinitions to per-PartUsage instances.

    Args:
        model: The parsed SysML model
        calc_usages: List of extracted calc usages (may include templates)
        warnings: List to append warnings to

    Returns:
        Expanded list with template usages replaced by concrete instances
    """
    expanded = []

    for usage in calc_usages:
        if not usage.is_template:
            # Concrete usage - keep as-is
            expanded.append(usage)
            continue

        # This is a template - find all instantiations
        part_def = _find_part_def_by_qn(model, usage.owning_part_def_qn)
        if not part_def:
            warnings.append(
                f"Could not find PartDefinition for template calc usage: {usage.instance_name}"
            )
            continue

        part_usages = _find_part_usages_of_definition(model, part_def)

        if not part_usages:
            warnings.append(
                f"Calc usage '{usage.instance_name}' in PartDefinition "
                f"'{usage.owning_part_def_qn}' has no instantiations"
            )
            continue

        for part_usage_elem, part_path in part_usages:
            # Create virtual calc usage for this instantiation
            virtual = _create_virtual_calc_usage(
                template=usage,
                part_usage=part_usage_elem,
                part_def=part_def,
                part_path=part_path,
                model=model,
            )
            expanded.append(virtual)

    return expanded
```

**Change 1.6: Add virtual calc usage creation with binding resolution**

```python
def _create_virtual_calc_usage(
    template: CalcUsageData,
    part_usage: Any,
    part_def: Any,
    part_path: str,
    model: Any,
) -> CalcUsageData:
    """Create a virtual calc usage for a specific PartUsage instantiation.

    Args:
        template: The template CalcUsageData from the PartDefinition
        part_usage: The PartUsage instantiating the PartDefinition
        part_def: The PartDefinition containing the template
        part_path: Full dot-separated path to the PartUsage
        model: The parsed SysML model

    Returns:
        New CalcUsageData with resolved bindings and updated paths
    """
    # Resolve bindings through redefinition chain
    resolved_bindings = []
    resolved_unbound = []

    for binding in template.bindings:
        resolved = _resolve_binding_through_redefinition(
            original_binding=binding,
            part_usage=part_usage,
            part_def=part_def,
        )
        if resolved.binding_type == BindingType.UNBOUND:
            resolved_unbound.append(resolved.param_name)
        else:
            resolved_bindings.append(resolved)

    # Also check template's unbound params - may now be bound via redefinition
    for param_name in template.unbound_params:
        binding = _check_redefinition_provides_value(
            param_name=param_name,
            part_usage=part_usage,
            part_def=part_def,
        )
        if binding:
            resolved_bindings.append(binding)
        else:
            resolved_unbound.append(param_name)

    # Build qualified name: part_path.calc_name with __ separator
    qualified_name = f"{sysml_to_python_qualified_name(part_path)}__{template.instance_name}"

    # Build instance name: flatten path with __
    instance_name = qualified_name.replace(".", "__")

    return CalcUsageData(
        instance_name=instance_name,
        calc_def_name=template.calc_def_name,
        calc_def_qualified_name=template.calc_def_qualified_name,
        module_type=template.module_type,
        bindings=resolved_bindings,
        unbound_params=resolved_unbound,
        source_file=template.source_file,
        source_line=template.source_line,
        parent_part_path=part_path,
        qualified_name=qualified_name,
        raw_element=template.raw_element,
        is_template=False,  # This is now a concrete instance
        owning_part_def_qn=None,
    )


def _resolve_binding_through_redefinition(
    original_binding: BindingInfo,
    part_usage: Any,
    part_def: Any,
) -> BindingInfo:
    """Resolve a binding through a PartUsage's redefinitions.

    Args:
        original_binding: The binding from the template calc usage
        part_usage: The PartUsage that may redefine attributes
        part_def: The PartDefinition containing the original attribute

    Returns:
        New BindingInfo with resolved source path
    """
    # Find the target attribute in the binding source
    target_attr_name = _extract_attribute_name_from_binding(original_binding)
    if not target_attr_name:
        return original_binding

    # Check if part_usage redefines this attribute
    for member in getattr(part_usage, "ownedMember", []):
        if not SysideAdapter.is_instance(member, "AttributeUsage"):
            continue

        # Check if this member redefines the target attribute
        if _member_redefines_attribute(member, target_attr_name, part_def):
            # Extract the new value from the redefinition
            new_value = _extract_redefinition_value(member)
            if new_value is not None:
                return BindingInfo(
                    param_name=original_binding.param_name,
                    source_path=None,
                    binding_type=BindingType.LITERAL,
                    literal_value=new_value,
                    raw_expression=f"Redefined to: {new_value}",
                )

            # Check if redefinition has a chain expression
            new_chain = _extract_redefinition_chain(member)
            if new_chain:
                return BindingInfo(
                    param_name=original_binding.param_name,
                    source_path=new_chain,
                    binding_type=BindingType.CHAIN,
                    raw_expression=f"Redefined via chain: {new_chain}",
                )

    # No redefinition found - binding remains as-is (may become entry point)
    return original_binding


def _member_redefines_attribute(
    member: Any,
    attr_name: str,
    part_def: Any,
) -> bool:
    """Check if a member redefines a specific attribute by name."""
    # Check explicit redefinitions
    if hasattr(member, "ownedRedefinition"):
        for redef in member.ownedRedefinition:
            if hasattr(redef, "redefinedFeature"):
                redefined = redef.redefinedFeature
                if getattr(redefined, "name", None) == attr_name:
                    return True

    # Check implicit redefinition by name match
    if getattr(member, "name", None) == attr_name:
        return True

    return False
```

**Change 1.7: Update main extraction function**

```python
def extract_calculation_usages(
    model: Any,
    known_calc_defs: set[str] | None = None,
    calc_defs: list | None = None,
    expand_templates: bool = True,  # NEW PARAMETER
) -> tuple[list[CalcUsageData], ExtractionReport]:
    """Extract all calculation usages from a SysML model.

    Args:
        model: Parsed SysIDE model
        known_calc_defs: Set of known calc def names for validation (optional)
        calc_defs: List of CalculationDefinitionData for detecting algorithm params
        expand_templates: If True, expand calc usages in PartDefinitions to
                         per-PartUsage instances (default True)

    Returns:
        Tuple of (list of CalcUsageData, ExtractionReport with statistics)
    """
    usages: list[CalcUsageData] = []
    warnings: list[str] = []

    # ... existing extraction code ...

    # NEW: Expand template calc usages
    if expand_templates:
        usages = _instantiate_template_calc_usages(model, usages, warnings)

    # ... rest of function ...
```

---

#### Change Set 2: Analysis Phase Updates

**File**: `src/sysml_codegen/analysis/dependency_backtracker.py`

The analysis phase requires minimal changes because:
1. Virtual calc usages from extraction have resolved bindings
2. `binding_resolutions` dict already handles LITERAL bindings as ENTRY_POINTs
3. `_resolve_binding_to_usage()` works with any CalcUsageData

**Change 2.1: Handle transitive bindings from redefinitions**

The virtual usages created in extraction will have bindings that may reference parent part attributes. The existing transitive resolution logic should handle this, but we need to ensure design attribute indexing includes attributes from PartDefinitions.

```python
# In _build_design_attr_binding_index(), ensure we also index
# attributes from PartDefinitions that are redefined in PartUsages
```

**Change 2.2: Update design attribute extraction to include inherited attributes**

Currently design attributes are extracted only from explicit definitions in design files. For the nested cost pattern, we need to recognize that `magnets.capital_cost` comes from the inherited calc model.

This may require coordination with `parameter_groups.py` to ensure:
1. Attributes exposed via redefinition (`:>> capital_cost = cost_model.total`) are indexed
2. Binding resolution finds these inherited attributes

---

#### Change Set 3: Resolution Phase Updates

**File**: `src/sysml_codegen/resolution/graph_builder.py`

Minimal changes needed since resolution consumes CalcUsageData generically.

**Change 3.1: Handle expanded qualified names**

Virtual usages have longer qualified names (e.g., `catf_plant__magnets__cost_model`). Ensure:
- `get_module_name()` handles deeply nested names correctly
- `get_channel_name()` produces unique channel names

---

#### Change Set 4: No Generation Phase Changes

The generation phase operates on `ComputationGraph` which is produced by resolution. Since resolution will produce proper `PipelineModule` objects for virtual usages, generation will work unchanged.

---

### 4. Test Cases Required

#### Test 1: Calc in PartDef with single usage

```sysml
part def 'Component' {
    attribute input_value : Real;
    calc embedded : SimpleCalc { in x = input_value; }
    attribute output_value : Real = embedded.y;
}

part my_component : 'Component' { :>> input_value = 5.0; }
```

**Expected**: One module `my_component__embedded` with input resolved to LITERAL 5.0.

#### Test 2: Calc in PartDef with multiple usages

```sysml
part def 'Wheel' {
    attribute diameter : Real;
    calc cost_calc : WheelCostCalc { in d = diameter; }
}

part front_wheel : 'Wheel' { :>> diameter = 60.0; }
part rear_wheel : 'Wheel' { :>> diameter = 65.0; }
```

**Expected**: Two modules:
- `front_wheel__cost_calc` with diameter = 60.0
- `rear_wheel__cost_calc` with diameter = 65.0

#### Test 3: Nested part hierarchy

```sysml
part plant {
    part reactor {
        part magnets : 'Magnet System' { :>> field_strength = 12.0; }
    }
}
```

**Expected**: Module `plant__reactor__magnets__cost_model` with field_strength = 12.0.

#### Test 4: Redefinition with chain binding

```sysml
part my_component : 'Component' {
    :>> input_value = power_balance.p_net;  // Chain, not literal
}
```

**Expected**: Module binding resolved to MODULE_OUTPUT referencing power_balance's output.

#### Test 5: Hierarchical cost rollup

```sysml
part bike : 'Bike' {
    :>> frame_length = 1.5;
    :>> wheel_hub_mass = 0.3;
}
```

**Expected**:
- `bike__frame__cost_calc` module
- `bike__front_wheel__cost_calc` module
- `bike__rear_wheel__cost_calc` module
- `bike__rollup_calc` module (if exists)
- All properly wired for rollup

---

### 5. Implementation Order

#### Phase 1: Extraction Foundation (BR-1, BR-2)

1. Add `_get_owning_type_info()` function
2. Add `_find_part_usages_of_definition()` and helpers
3. Add `_build_full_part_path()`
4. Add `is_template`, `owning_part_def_qn`, `raw_element` to CalcUsageData
5. Update `_extract_single_usage()` to detect templates
6. Add unit tests for detection

#### Phase 2: Binding Resolution (BR-4)

7. Add `_resolve_binding_through_redefinition()`
8. Add `_member_redefines_attribute()`
9. Add `_extract_redefinition_value()` and `_extract_redefinition_chain()`
10. Add unit tests for literal and chain resolution

#### Phase 3: Instantiation (BR-3)

11. Add `_instantiate_template_calc_usages()`
12. Add `_create_virtual_calc_usage()`
13. Update `extract_calculation_usages()` with `expand_templates` param
14. Add integration tests

#### Phase 4: Hierarchy Support (BR-5, BR-6)

15. Enhance path building for deep hierarchies
16. Handle recursive definition nesting
17. Add end-to-end tests

#### Phase 5: Verification

18. End-to-end test with cost model example
19. Verify generated pipeline YAML is correct
20. Verify teax-simkit executes correctly

---

### 6. Coordination with agentic-mbse Changes

The agentic-mbse research report (`20260109-202300_cost-modeling-library-changes.md`) identifies:

1. **Level 9 Validation Rules** - These validate the PATTERNS we're adding support for
2. **SysideAdapter Extensions** - We may need these for specialization chain detection
3. **MODELING_GUIDE Updates** - Documents the patterns that sysml-codegen will support

**Dependency Order:**

1. **agentic-mbse first** - Add SysideAdapter helper functions if needed
2. **sysml-codegen second** - Implement template instantiation using helpers
3. **Validation third** - Level 9 rules verify correct usage of supported patterns

**Shared Needs:**

| Function | agentic-mbse | sysml-codegen |
|----------|--------------|---------------|
| `specializes(elem, name)` | Level 9 Rule 1 | `_usage_instantiates_definition()` |
| `get_specialization_chain(elem)` | Level 9 Rule 1 | Hierarchy traversal |
| `get_parent_part_name(elem)` | Already exists | Can reuse |

**Recommendation**: Add shared helpers to agentic-mbse's SysideAdapter, then use them in sysml-codegen.

---

### 7. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| syside doesn't expose redefinition info | Medium | High | Test early with real models |
| Specialization chain complex to traverse | Low | Medium | Use iterative approach |
| Qualified names become very long | Low | Low | Already using `__` which handles nesting |
| Performance with many instantiations | Low | Low | Template detection is O(n) |
| Binding resolution ambiguity | Medium | Medium | Log warnings, fail gracefully |

---

### 8. Scope Summary

| Component | Estimated Lines | Complexity |
|-----------|-----------------|------------|
| Extraction: Owner detection | ~60 lines | Low |
| Extraction: PartUsage finding | ~80 lines | Medium |
| Extraction: Binding resolution | ~150 lines | High |
| Extraction: Instantiation | ~100 lines | Medium |
| Analysis: Minor updates | ~30 lines | Low |
| Resolution: Minor updates | ~20 lines | Low |
| Tests | ~300 lines | Medium |
| **Total** | **~740 lines** | Medium-High |

---

## Recommendations

1. **Implement in phases** - Start with detection, then resolution, then instantiation
2. **Test with real models** - Use fusion-tea's test models for validation
3. **Coordinate with agentic-mbse** - Share helper functions for specialization detection
4. **Log extensively** - Template instantiation is complex; good logging aids debugging
5. **Add `expand_templates` flag** - Allow disabling for backward compatibility
6. **Document the pattern** - MODELING_GUIDE should explain nested cost model pattern

---

## Open Questions

1. **syside redefinition API**: What's the exact API for accessing redefinition information? Need to verify `ownedRedefinition` and `redefinedFeature` attributes.

2. **Implicit vs explicit redefinition**: Does SysMLv2 distinguish `:>> attr = value` from `attribute attr = value`? Both may need handling.

3. **Default value inheritance**: If part def attribute has default and part usage doesn't redefine, how is that exposed in AST?

4. **Cross-file instantiations**: When PartDefinition and PartUsage are in different files, does syside resolve the type reference correctly?

5. **Recursive instantiation depth**: How deep can nesting go? (e.g., PartDef containing PartUsage containing another PartDef with calc)

---

## Code References

**Current Implementation:**
- `src/sysml_codegen/extraction/usage_extractor.py:407-421` - `_get_parent_part_path()`
- `src/sysml_codegen/extraction/usage_extractor.py:133-168` - `extract_calculation_usages()`
- `src/sysml_codegen/extraction/usage_extractor.py:171-234` - `_extract_single_usage()`
- `src/sysml_codegen/analysis/dependency_backtracker.py:305-484` - `_trace_dependencies()`
- `src/sysml_codegen/resolution/graph_builder.py:423-539` - `_build_pipeline_module()`

**fusion-tea Research:**
- `~/1cfe/fusion-tea/project/research/20260106-050051_cost-modeling-lcoe-strategy.md`
- `~/1cfe/fusion-tea/project/research/20260106-065431_cost-architecture-patterns.md`
- `~/1cfe/fusion-tea/project/research/20260107-final-cost-architecture.md`

**agentic-mbse Planned Changes:**
- `~/1cfe/agentic-mbse/.project/research/20260109-202300_cost-modeling-library-changes.md`

---

**Last Updated**: 2026-01-09
