# ADR-003: Signal Identifier Architecture

## Status
**Accepted** - 2025-12-23

**Resolved**: Module Type uniqueness is now guaranteed via namespaced module types. See `project/active/adr003-opens/design_proposal.md` for the design that enables same-named calc defs in different packages (e.g., `Magnets::Capex`, `Blanket::Capex`).

## Context

The codegen pipeline uses various identifiers to uniquely reference elements throughout the transformation from SysML models to executable pipelines. Recent bugs (e.g., the channel mismatch bug documented in `project/research/20251223-000000_e2e-test-channel-mismatch.md`) stem from **multiple places independently constructing identifiers** using ad-hoc string formatting, leading to lookup mismatches at runtime.

This ADR establishes the definitive specification for:
1. The taxonomy of all identifier types in the system
2. The single source of truth for each identifier type
3. Construction, derivation, and resolution rules
4. Lookup and validation mechanisms

### Background

ADR-001 established the namespace format for input parameters using `__` (double underscore) as the hierarchy separator. ADR-002 established where calculations belong (library vs design). This ADR completes the picture by defining ALL signal identifiers used throughout the pipeline.

### The Problem

An audit of the codebase revealed **7 locations** that construct or derive identifiers:

| File | Lines | What It Constructs | Method |
|------|-------|-------------------|--------|
| `usage_extractor.py` | 636-662 | Calc usage qualified names | `_build_qualified_name()` |
| `parameter_group_derivation.py` | 444-470 | Design attr qualified names | `_build_qualified_name()` (duplicate) |
| `dependency_backtracker.py` | 224, 333, 341, 346 | Entry point qualified names | Inline f-string |
| `graph_builder.py` | 323, 543, 559 | Entry point lookups | Inline f-string |
| `graph_builder.py` | 45-84 | Module names | `_derive_unique_module_name()` |
| `graph_builder.py` | 275 | Channel names | Inline f-string |
| `graph_builder.py` | 269 | Output catalog keys | Inline f-string |

**Root Cause**: No single source of truth. Downstream code re-derives identifiers instead of looking up authoritative values computed upstream.

**Specific Bug**: When a calc input is bound to a design attribute at a different scope (e.g., `wall_plug::delivered_power` bound to `catf_heating::delivered_power`), `graph_builder.py` constructs `{usage.qualified_name}__{param_name}` which produces the wrong key for entry point lookup.

## Decision

### Core Principle

> **Identifiers are computed ONCE at extraction time and LOOKED UP thereafter. Downstream code SHALL NOT re-derive or reconstruct identifiers.**

### Simplification Principle

> **Use existing qualified names directly. Do not derive shortened forms that require collision detection.**

The previous approach used "last 2 segments" for module names as a readability optimization. This introduced:
- Collision detection code (`_assert_module_names_unique()`)
- Fallback logic when collisions occur
- Risk of unexpected failures with nested parts

The new approach uses EQN/PQN directly, which:
- Is guaranteed unique by SysML specification
- Requires no collision detection
- Works correctly regardless of nesting depth
- Trades YAML readability for architectural simplicity

### Identifier Taxonomy

The pipeline uses five distinct identifier types:

#### 1. Element Qualified Name (EQN)
**Purpose**: Globally unique identifier for any SysML element.
**Format**: `Package__Part__SubPart__...Element`
**Separator**: `__` (double underscore)
**Source of Truth**: AST traversal via `_build_qualified_name()`
**Scope**: Computed at extraction time; stored in data models

**Examples**:
- Calc usage: `CATFMFEPhysics__catf_physics__alpha_neutron_split`
- Design attr: `CATFMFEPhysics__catf_physics__p_fusion`
- Nested part: `CATFMFERadialBuild__catf_radial_build__plasma_region__minor_radius`

**Data Models**:
- `CalcUsageData.qualified_name`
- `DesignAttributeData.qualified_name`

**Uniqueness**: Guaranteed by SysML v2 specification (full ownership chain).

#### 2. Parameter Qualified Name (PQN)
**Purpose**: Globally unique identifier for a calc input/output parameter.
**Format**: `{EQN}__{param_name}` (extends element EQN with parameter)
**Separator**: `__` (double underscore)
**Source of Truth**: `DependencyBacktracker` (computed once, stored in mapping)
**Scope**: Entry points, pipeline module inputs, channel names

**Examples**:
- Unbound param: `CATFMFEPhysics__catf_physics__wall_plug__heating_efficiency`
- Bound to design attr: `CATFMFEPhysics__catf_physics__p_fusion` (inherits design attr's EQN)
- Output channel: `CATFMFEPhysics__catf_physics__alpha_neutron_split__p_neutron`

**Key Insight**: When a calc input binds to a design attribute, the PQN is the **design attribute's EQN**, NOT `{usage.qualified_name}__{param_name}`.

**Data Model**: `EntryPoint.qualified_name`, `ModuleOutput.channel_name`

**Uniqueness**: Guaranteed (extends already-unique EQN).

#### 3. Module Name
**Purpose**: YAML key for pipeline module instances.
**Format**: Usage EQN, lowercased
**Source of Truth**: `CalcUsageData.qualified_name` (direct use, no derivation)
**Scope**: Pipeline YAML keys

**Example**:
```
EQN: CATFMFEPhysics__catf_physics__alpha_neutron_split
Module Name: catfmfephysics__catf_physics__alpha_neutron_split
```

**Data Model**: `PipelineModule.name`

**Uniqueness**: Guaranteed (uses full EQN).

**Rationale**: Previous approach used "last 2 segments" for readability but required collision detection. Using the full EQN (lowercased) eliminates this complexity. YAML keys are machine-consumed; human readability is a minor concern compared to architectural simplicity.

#### 4. Module Type
**Purpose**: Identifier for module implementation in YAML and TEAx registry.
**Format**: `{namespace}.{CalcDefName}Module`
**Source of Truth**: Calc definition's `qualified_name` from SysIDE
**Scope**: Python imports, YAML module_type field, TEAx registry key

**Derivation**:
1. Extract qualified_name from SysIDE (e.g., `FusionPhysics_PowerBalance::AlphaNeutronSplit`)
2. Split on `::` separator
3. Join package segments with `.` (lowercased) to form namespace
4. Append `Module` suffix to element name (preserving case)

**Examples**:
| SysML Qualified Name | Module Type |
|---------------------|-------------|
| `FusionPhysics_PowerBalance::AlphaNeutronSplit` | `fusionphysics_powerbalance.AlphaNeutronSplitModule` |
| `Magnets::Capex` | `magnets.CapexModule` |
| `Blanket::Capex` | `blanket.CapexModule` |
| `Standalone` (no package) | `StandaloneModule` |

**Data Model**: `PipelineModule.module_type`

**Uniqueness**: Guaranteed by SysML package namespace. Same-named calc defs in different packages produce unique module types.

**Python Path**: Derived from same segments with `/` separator instead of `.`:
- `fusionphysics_powerbalance.AlphaNeutronSplitModule` → `fusionphysics_powerbalance/alphaneutronsplit.py`
- `magnets.CapexModule` → `magnets/capex.py`

#### 5. Channel Name
**Purpose**: Wiring identifier for module outputs.
**Format**: PQN of the output (usage EQN + output attribute name)
**Source of Truth**: Computed from `CalcUsageData.qualified_name` + output attribute
**Scope**: Pipeline YAML outputs, downstream input references

**Examples**:
- `CATFMFEPhysics__catf_physics__alpha_neutron_split__p_alpha`
- `CATFMFEPhysics__catf_physics__alpha_neutron_split__p_neutron`

**Data Model**: `ModuleOutput.channel_name`, `InputSource.producer_channel`

**Uniqueness**: Guaranteed (is a PQN).

**Rationale**: Using PQN for channels means the channel name IS the output's qualified name. This eliminates the need for a separate "channel name" concept—channels are just PQNs.

### Identifier Resolution Flow

```
SysML Model
    │
    ▼
┌──────────────────────────────────────────────────────────────┐
│ EXTRACTION PHASE                                              │
│                                                               │
│ usage_extractor.py      → CalcUsageData.qualified_name (EQN) │
│ parameter_group_derivation.py → DesignAttributeData.qualified_name (EQN) │
└──────────────────────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────────────────────┐
│ BACKTRACKING PHASE                                           │
│                                                               │
│ dependency_backtracker.py:                                   │
│   - Receives OutputRegistry (pre-built, Step 5)              │
│   - CHAIN bindings: registry.resolve(source_path) →          │
│       MODULE_OUTPUT or design attr fallback → ENTRY_POINT    │
│   - REFERENCE bindings: leaf-name extraction +               │
│       parent-scoped registry.resolve() → MODULE_OUTPUT       │
│       or design attr fallback                                │
│   - LITERAL/UNBOUND: → ENTRY_POINT directly                 │
│   - Stores results in binding_resolutions dict               │
│   - See ADR-008 for the full OutputRegistry architectural    │
│     decision.                                                │
└──────────────────────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────────────────────┐
│ GRAPH BUILDING PHASE                                         │
│                                                               │
│ graph_builder.py:                                            │
│   - build_computation_graph() takes output_registry param    │
│   - Module name = usage.qualified_name.lower()               │
│   - Channel existence uses registry.resolve() and            │
│     registry.canonical_channels                              │
│   - _build_pipeline_module() uses binding_resolutions        │
│     (no output_catalog parameter)                            │
│   - Wires inputs to entry points or upstream channels        │
└──────────────────────────────────────────────────────────────┘
    │
    ▼
┌──────────────────────────────────────────────────────────────┐
│ GENERATION PHASE                                             │
│                                                               │
│ pipeline_generator.py:                                       │
│   - Uses only values from ComputationGraph                   │
│   - No identifier construction                               │
└──────────────────────────────────────────────────────────────┘
```

### Single Source of Truth: `binding_resolutions` Mapping

**The Fix**: The backtracker resolves every binding via the `OutputRegistry` and stores a `BindingResolution` for each. The graph builder looks up this mapping instead of constructing identifiers. The older `binding_to_entry_point` mapping is deprecated; `binding_resolutions` is the authoritative source.

**Data Structure**:
```python
class BindingResolution(BaseModel):
    resolution_type: BindingResolutionType  # MODULE_OUTPUT or ENTRY_POINT
    qualified_name: str                      # channel PQN or entry point PQN
    source_path: str | None                  # original SysML source path
    is_transitive: bool

class BacktrackingResult(BaseModel):
    # Existing fields...
    entry_points: set[str]
    execution_order: list[CalcUsageData]

    # AUTHORITATIVE: Unified binding resolutions via OutputRegistry
    binding_resolutions: dict[str, BindingResolution]
    # Maps "{usage_qn}|{param_name}" → BindingResolution

    # DEPRECATED: Kept for backward compatibility
    binding_to_entry_point: dict[str, str]
```

**Construction in Backtracker** (via OutputRegistry):
```python
def _trace_dependencies(self, usage, visited, path):
    for binding in usage.bindings:
        mapping_key = f"{usage.qualified_name}|{param_name}"

        if binding is LITERAL or UNBOUND:
            # -> ENTRY_POINT directly
            entry_point_qn = f"{usage.qualified_name}__{param_name}"
            self._binding_resolutions[mapping_key] = BindingResolution(
                resolution_type=BindingResolutionType.ENTRY_POINT,
                qualified_name=entry_point_qn,
            )

        elif binding has source_path:
            # Sole resolution path via OutputRegistry
            resolution = self._resolve_binding_via_registry(binding, usage)
            self._binding_resolutions[mapping_key] = resolution

            if resolution.resolution_type == MODULE_OUTPUT:
                # DFS into producing usage
                producing_usage = self._find_usage_for_channel(resolution.qualified_name)
                if producing_usage and producing_usage not in visited:
                    self._trace_dependencies(producing_usage, visited, path)
            else:
                # ENTRY_POINT (design attribute fallback)
                self._entry_point_context[resolution.qualified_name] = usage

    for param in usage.unbound_params:
        mapping_key = f"{usage.qualified_name}|{param}"
        self._binding_resolutions[mapping_key] = BindingResolution(
            resolution_type=BindingResolutionType.ENTRY_POINT,
            qualified_name=f"{usage.qualified_name}__{param}",
        )
```

The `_resolve_binding_via_registry()` method implements the resolution cascade:
1. `registry.resolve(source_path)` -- direct channel lookup
2. Normalize `::` SysML QN to dotted format and retry
3. REFERENCE secondary: leaf-name extraction + parent-scoped `registry.resolve()`
4. Design attribute fallback -- `ENTRY_POINT`
5. Fallback -- `ENTRY_POINT` with warning

See ADR-008 for the full OutputRegistry architectural decision.

**Lookup in Graph Builder**:
```python
def build_computation_graph(result, calc_defs, design_attrs,
                            group_deriver, output_registry, ...):
    # output_registry: OutputRegistry passed in (no output_catalog construction)
    # Channel existence checks use registry.resolve() and
    # registry.canonical_channels
    ...

def _build_pipeline_module(usage, calc_def, entry_points,
                           execution_order, binding_resolutions):
    # Module name is just the EQN lowercased
    module_name = usage.qualified_name.lower()

    for input_attr in calc_def.input_attributes:
        param_name = input_attr.name

        # LOOKUP via binding_resolutions (sole source of truth)
        lookup_key = f"{usage.qualified_name}|{param_name}"
        resolution = binding_resolutions.get(lookup_key)
        if resolution is None:
            raise ValueError(f"No binding resolution for {lookup_key}")

        if resolution.resolution_type == MODULE_OUTPUT:
            # Wire to upstream producer channel
            ...
        else:
            # Wire to entry point
            ep = entry_points.get(resolution.qualified_name)

    # Channel names are PQNs
    for output_attr in calc_def.output_attributes:
        channel_name = f"{usage.qualified_name}__{output_attr.name}"
```

See ADR-008 for the full OutputRegistry architectural decision.

### Shared Utility: `qualified_names.py`

The duplicate `_build_qualified_name()` functions SHALL be consolidated into a shared module:

**File**: `scripts/codegen/qualified_names.py`

```python
"""Single source of truth for qualified name construction.

All identifier construction MUST use these functions.
Do NOT construct qualified names via inline f-strings.
"""

def build_element_qualified_name(elem: object, separator: str = "__") -> str:
    """Build qualified name for any SysML element.

    Traverses AST ownership hierarchy to build full path.
    Used for CalcUsageData.qualified_name and DesignAttributeData.qualified_name.
    """
    chain = _build_owner_chain(elem)
    name = _sanitize_name(getattr(elem, "name", ""))
    if chain:
        return separator.join(chain + [name])
    return name

def build_parameter_qualified_name(usage_qualified_name: str, param_name: str) -> str:
    """Build qualified name for a parameter scoped to a usage.

    ONLY for unbound params and literal bindings.
    For bindings to design attributes, use the design attribute's qualified_name instead.
    """
    return f"{usage_qualified_name}__{param_name}"

def get_module_name(usage_qualified_name: str) -> str:
    """Get YAML module name from usage qualified name.

    Simply lowercases the EQN. No derivation or shortening.
    """
    return usage_qualified_name.lower()

def get_channel_name(usage_qualified_name: str, output_attr_name: str) -> str:
    """Get output channel name (which is just the output's PQN)."""
    return f"{usage_qualified_name}__{output_attr_name}"
```

### Validation Rules

| Rule | Location | Validation |
|------|----------|------------|
| V1 | Extraction | Element qualified names must be non-empty |
| V2 | Backtracking | All bindings must resolve via OutputRegistry (MODULE_OUTPUT) or design attribute fallback (ENTRY_POINT). See ADR-008. |
| V3 | Graph Building | All entry point lookups must succeed |
| V4 | Pipeline Generation | All channel references must resolve to declared outputs |

**Removed**: Module name collision detection (V3 in previous draft). No longer needed since module names are full EQNs.

### Naming Convention Summary

| Identifier Type | Format | Example | Uniqueness |
|-----------------|--------|---------|------------|
| Element Qualified Name (EQN) | `Pkg__Part__Element` | `CATFMFEPhysics__catf_physics__alpha_neutron_split` | Guaranteed by SysML |
| Parameter Qualified Name (PQN) | `{EQN}__{param}` | `CATFMFEPhysics__catf_physics__alpha_neutron_split__p_fusion` | Guaranteed (extends EQN) |
| Module Name | `{EQN}.lower()` | `catfmfephysics__catf_physics__alpha_neutron_split` | Guaranteed (is EQN) |
| Module Type | `{namespace}.{CalcDefName}Module` | `fusionphysics_powerbalance.AlphaNeutronSplitModule` | Guaranteed (namespaced) |
| Channel Name | PQN of output | `CATFMFEPhysics__catf_physics__alpha_neutron_split__p_neutron` | Guaranteed (is PQN) |

## Consequences

### Positive

1. **Single source of truth**: Each identifier type has exactly one construction point
2. **No lookup mismatches**: Graph builder looks up instead of re-deriving
3. **No collision detection**: Using full EQN eliminates collision risk entirely
4. **Simpler code**: Remove `_derive_unique_module_name()` and `_assert_module_names_unique()`
5. **Works with arbitrary nesting**: Full EQN handles any part hierarchy depth
6. **Explicit mappings**: The `binding_resolutions` mapping makes resolution transparent
7. **Fail-fast validation**: Lookup failures are explicit errors, not silent bugs
8. **Consolidated code**: Shared `qualified_names.py` eliminates duplicate functions
9. **Supports same-named calc defs**: Multiple packages can have `Capex` calc def without collision (e.g., `magnets.CapexModule`, `blanket.CapexModule`)
10. **Scalable namespacing**: Works with flat packages (current) and nested packages (future) using the same derivation logic

### Negative

1. **Longer YAML keys**: Module names like `catfmfephysics__catf_physics__alpha_neutron_split` are verbose
2. **Data structure change**: `BacktrackingResult` grows with new mapping field
3. **Migration required**: Graph builder must be refactored to use lookups

### Tradeoff Analysis

| Aspect | Previous (Last-2) | New (Full EQN) |
|--------|-------------------|----------------|
| YAML readability | Better | Worse (verbose) |
| Code complexity | Higher (derivation + validation) | Lower (direct use) |
| Collision risk | Requires detection | None |
| Nesting support | Breaks with deep nesting | Works always |
| Debugging | Harder (which module?) | Easier (full path visible) |

**Verdict**: The verbosity cost is acceptable. YAML is machine-consumed; human readers benefit from seeing the full path anyway.

### Implementation Requirements

#### Phase 0: Fix Qualified Name Extraction
0. Fix `scripts/sysml_to_teax.py:356` to extract `elem.qualified_name` from SysIDE (currently just uses element name)

#### Phase 1: Consolidate Qualified Name Functions
1. Create `scripts/codegen/qualified_names.py` with shared functions
2. Create `scripts/codegen/identifier_types.py` with data classes (`SysMLQualifiedName`, `ModuleType`, `PythonModulePath`)
3. Refactor `usage_extractor.py` to import from shared module
4. Refactor `parameter_group_derivation.py` to import from shared module
5. Verify all tests pass

#### Phase 2: Add Binding-to-Entry-Point Mapping
5. Add `binding_to_entry_point: dict[tuple[str, str], str]` to `BacktrackingResult`
6. Populate mapping in `DependencyBacktracker._trace_dependencies()`
7. Populate mapping for unbound params in `DependencyBacktracker.find_required_modules()`
8. Add tests for mapping correctness

#### Phase 3: Simplify Graph Builder
9. Remove `_derive_unique_module_name()` function
10. Remove `_assert_module_names_unique()` function
11. Remove `ModuleNameCollisionError` class
12. Change module name to `usage.qualified_name.lower()`
13. Change channel name to PQN format
14. Pass `binding_to_entry_point` to `_build_pipeline_module()`
15. Replace inline f-string construction with mapping lookup
16. Verify E2E tests pass (especially the channel mismatch scenario)

#### Phase 4: Update Tests and Documentation
17. Update tests that check for short module names
18. Add explicit tests for the channel mismatch scenario
19. Update FOUNDATION.md with new identifier format
20. Update glossary documents

## Examples

### Example 1: Bound to Design Attribute at Different Scope

**SysML Model**:
```sysml
part catf_heating {
    attribute delivered_power : Real = 50.0;  // Design attribute

    calc wall_plug : HeatingWallPlugPower {
        in delivered_power = catf_heating::delivered_power;  // Bound to parent
    }
}
```

**Identifier Resolution**:
- Design attr EQN: `CATFMFEHeating__catf_heating__delivered_power`
- Calc usage EQN: `CATFMFEHeating__catf_heating__wall_plug`
- Binding resolves to: `CATFMFEHeating__catf_heating__delivered_power` (uses design attr's EQN)

**Previous (Broken)**:
```python
# Graph builder constructed:
qualified_name = f"{usage.qualified_name}__{param_name}"
# = "CATFMFEHeating__catf_heating__wall_plug__delivered_power"  # WRONG!
```

**Fixed (Lookup)**:
```python
# Graph builder looks up:
qualified_name = binding_to_entry_point[(usage.qualified_name, "delivered_power")]
# = "CATFMFEHeating__catf_heating__delivered_power"  # CORRECT!
```

### Example 2: Unbound Parameter (Library Default)

**SysML Model**:
```sysml
calc wall_plug : HeatingWallPlugPower {
    // heating_efficiency NOT bound → uses library default 0.5
}
```

**Identifier Resolution**:
- Calc usage EQN: `CATFMFEHeating__catf_heating__wall_plug`
- Unbound param PQN: `CATFMFEHeating__catf_heating__wall_plug__heating_efficiency`

**Mapping**: `("CATFMFEHeating__catf_heating__wall_plug", "heating_efficiency")` → `"CATFMFEHeating__catf_heating__wall_plug__heating_efficiency"`

### Example 3: Module and Channel Names (New Format)

**Calc Usage**:
- Instance: `alpha_neutron_split`
- EQN: `CATFMFEPhysics__catf_physics__alpha_neutron_split`
- Calc def qualified name: `FusionPhysics_PowerBalance::AlphaNeutronSplit`

**Identifiers**:
- Module name: `catfmfephysics__catf_physics__alpha_neutron_split` (EQN lowercased)
- Module type: `fusionphysics_powerbalance.AlphaNeutronSplitModule` (namespaced from calc def)
- Channel names (PQNs):
  - `CATFMFEPhysics__catf_physics__alpha_neutron_split__p_alpha`
  - `CATFMFEPhysics__catf_physics__alpha_neutron_split__p_neutron`

**YAML Output**:
```yaml
catfmfephysics__catf_physics__alpha_neutron_split:
  module_type: fusionphysics_powerbalance.AlphaNeutronSplitModule
  inputs:
    p_fusion: float physics_params.CATFMFEPhysics__catf_physics__p_fusion
  outputs:
    p_alpha: float CATFMFEPhysics__catf_physics__alpha_neutron_split__p_alpha
    p_neutron: float CATFMFEPhysics__catf_physics__alpha_neutron_split__p_neutron
```

### Example 4: Downstream Wiring

**SysML Model**:
```sysml
calc blanket_thermal : BlanketThermalPower {
    in p_neutron = alpha_neutron_split.p_neutron;
}
```

**YAML Output**:
```yaml
catfmfephysics__catf_physics__blanket_thermal:
  module_type: fusionphysics_powerbalance.BlanketThermalPowerModule
  inputs:
    # Wired to upstream channel (which is a PQN)
    p_neutron: float CATFMFEPhysics__catf_physics__alpha_neutron_split__p_neutron
```

## References

- **ADR-001**: `docs/architecture/ADR-001-input-parameter-definition.md` - Namespace format
- **ADR-002**: `docs/architecture/ADR-002-calculation-architecture.md` - Calculation location
- **ADR-008**: `docs/architecture/ADR-008-output-registry.md` - OutputRegistry architectural decision
- **SysML Glossary**: `docs/glossary/sysml.md` - Formal SysML v2 terms
- **Codegen Glossary**: `docs/glossary/codegen.md` - Project-specific terminology
- **Bug Analysis**: `project/research/20251223-000000_e2e-test-channel-mismatch.md`
- **Fix Spec**: `project/active/pipeline-refactor/identifier-consolidation-spec.md`
- **Tech Debt**: `project/active/pipeline-refactor/tech-debt-spec.md`
- **Models**: `scripts/codegen/models.py` - Data model definitions
- **Module Type Design**: `project/active/adr003-opens/design_proposal.md` - Namespaced module type transformation
- **Critical Assessment**: `project/agent_debug_scripts/adr003_critical_assessment.md` - Validation of namespaced approach

## Changelog

| Date | Change |
|------|--------|
| 2026-02-15 | **OutputRegistry cutover**: Updated backtracker and graph builder sections to reflect OutputRegistry-based resolution. `binding_resolutions` is now the authoritative mapping (replaces deprecated `binding_to_entry_point`). Updated V2 validation rule, pseudocode, and identifier resolution flow. Added cross-references to ADR-008. |
| 2025-12-23 | **Module Type namespacing**: Changed Module Type format from `{CalcDefName}Module` to `{namespace}.{CalcDefName}Module`. Enables same-named calc defs in different packages. Changed status from Draft to Accepted. |
| 2025-12-23 | **Simplified module/channel naming**: Changed Module Name from "last 2 segments" to full EQN (lowercased). Changed Channel Name from derived format to PQN. Removed collision detection requirement. |
| 2025-12-23 | Initial draft - comprehensive identifier architecture |
