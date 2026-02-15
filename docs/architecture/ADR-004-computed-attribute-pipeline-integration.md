# ADR-004: Computed Attribute Pipeline Integration

## Status
**Accepted** - 2026-02-09

## Context

Phase 1 (EXPR-CODEGEN) built an expression compiler that auto-implements CalcDef output expressions as Python code (15/15 solar_battery CalcDefs, 19/21 CATF CalcDefs). Phase 2 (ATTR-EXPR) extends codegen to capture attribute-level expressions on PartDefs -- expressions like `attribute area = length * width` -- and generate synthetic pipeline modules for them.

The ATTR-EXPR spike (Item 1) confirmed:
- SysIDE populates `feature_value_expression` on all PartDef/PartUsage attributes (35/35 in probe fixture, confirmed on solar_battery and CATF)
- 14/14 FORMULA patterns compile with the Phase 1 compiler, zero changes needed
- Chain handling (computed attributes referencing other computed attributes) requires zero special handling in the compiler
- EXPOSE patterns (pure `FeatureChainExpression`) fail compilation as expected -- they are aliases, not computations

This ADR captures how computed attributes are integrated into the extraction-resolution-generation pipeline: which architecture option was chosen, where computed attribute processing runs in the pipeline, how synthetic modules are named, and how the backtracker resolves bindings to computed attributes.

See ADR-005 for the classification scheme that determines which attributes receive which pipeline treatment.

## Decision

### Decision 1: Integration Architecture -- Option C (Direct Graph Integration)

Computed attributes are modeled as a **first-class entity** (`ComputedAttributeData`) that the graph builder processes directly alongside CalcUsages. Phantom CalcDef+CalcUsage objects are NOT synthesized.

#### Options Considered

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| **A: Synthetic CalcDef+CalcUsage** | Transform computed attributes into phantom CalcDef and CalcUsage data, inject into existing pipeline | Reuses all existing backtracker, graph builder, and generation infrastructure unchanged | Creates phantom SysML entities that don't exist in any model file; pollutes logs, YAML, and backlog with objects that have no source location; poor fit for EXPOSE patterns (an alias is not a CalcDef) |
| **B: Synthetic CalcUsage only** | Create synthetic CalcUsages referencing a shared "computed attribute CalcDef" | Lighter than A, still reuses module generation | Still creates phantom entities; CalcDef is a meaningless placeholder |
| **C: Direct graph integration** | `ComputedAttributeData` is first-class; graph builder generates `PipelineModule` from computed attributes directly | Clean provenance (every module traces to a real SysML element); FORMULA and EXPOSE get different treatment naturally; no phantom entities | Requires extending graph builder to understand a new entity type |
| **D: Inline @computed_field** | Computed attributes become `@computed_field` on Pydantic parameter schemas, no separate modules | Simplest for trivial formulas | Cannot handle cross-module dependencies; doesn't participate in pipeline YAML; limited to single-part scope |

#### Rationale

1. **FORMULA and EXPOSE need fundamentally different pipeline treatment.** FORMULA attributes become synthetic modules. EXPOSE_PURE attributes become channel aliases (no module). Option A forces both through the same CalcDef-shaped hole, requiring awkward special cases inside the existing CalcUsage pipeline.

2. **Provenance matters.** Every `PipelineModule` in the current system traces back to a specific `calc` usage in a specific `.sysml` file. Phantom CalcDefs break this invariant. With Option C, computed attribute modules trace to the `attribute` declaration on the PartDef -- a real SysML element with a real source location.

3. **The graph builder extension is moderate and well-scoped.** The change is: alongside the existing loop over CalcUsage modules, add a second loop over FORMULA computed attributes. Each produces a `PipelineModule` with inputs and outputs. The rest of generation (templates, YAML, backlog) is unchanged.

4. **Option A was the original concept doc recommendation.** The spike findings provided new information that makes Option C more attractive: the strong FORMULA/EXPOSE split, the alias strategy for EXPOSE, and the discovery that chains are purely a graph-ordering concern.

### Decision 2: Pipeline Placement -- Step 4.5

Computed attribute extraction runs as **Step 4.5**, after design attribute extraction (Step 4) and before parameter group derivation (Step 5).

#### Updated Pipeline Flow

```
Step 1:   Load SysML models via SysideAdapter
Step 2:   extract_calculation_definitions()        -> list[CalculationDefinitionData]
Step 3:   extract_calculation_usages()              -> list[CalcUsageData]
Step 4:   extract_design_attributes()               -> dict[Path, list[DesignAttributeData]]
Step 4.5: extract_computed_attributes()              -> list[ComputedAttributeData]     <- NEW
            + removes FORMULA attributes from Step 4's design_attributes dict
Step 5:   ParameterGroupDeriver                      -> list[ParameterGroup]
Step 5.5: Build OutputRegistry                       -> OutputRegistry                   <- NEW
            + registers FORMULA computed attributes as FORMULA channels
Step 6:   DependencyBacktracker.find_required_modules() -> BacktrackingResult
            + receives OutputRegistry (pre-built with FORMULA channels in Step 5.5)
Step 6.5: classify_compilability()                   -> dict[str, CalcDefCompilationResult]
Step 7:   build_computation_graph()                  -> ComputationGraph
            + accepts computed_attributes + output_registry
            + generates PipelineModule for each FORMULA computed attribute
            + resolves EXPOSE_PURE aliases for input wiring
Step 8:   Generation (modules, stencils, YAML, schemas, backlog)
```

#### Why Step 4.5?

Step 4.5 **needs**:
- PartDef/PartUsage element data (from the loaded model)
- CalcUsage names on each part (from Step 3, needed for EXPOSE classification)
- Sibling attribute names on each part (from the model, needed for FORMULA reference resolution)

Step 4.5 **feeds**:
- `ComputedAttributeData` list into Step 6 (backtracker) and Step 7 (graph builder)
- EXPOSE alias map into Step 7 (for input wiring resolution)
- New entry points into Step 5 (FORMULA inputs that aren't upstream outputs become entry points)

#### Step 4 / Step 4.5 Overlap: Preventing Double-Handling

A FORMULA attribute like `p_net_kw = p_net_mw * 1000.0` is processed by both Step 4 (as a `DesignAttributeData` with `default_value=None`, since the expression isn't a pure literal) and Step 4.5 (as a `ComputedAttributeData` with classification FORMULA).

This creates a risk: the ParameterGroupDeriver in Step 5 sees `p_net_kw` as a design attribute with no default and may incorrectly derive an entry point for it. But `p_net_kw` is computed -- it should NOT be an entry point.

**Resolution**: After Step 4.5 classifies FORMULA attributes, it **removes them from the design attributes dict** before the dict is passed to Step 5. This is a simple set subtraction keyed on `(owning_part_qualified_name, attribute_name)`. The `DesignAttributeData` for `p_net_kw` is dropped; only the `ComputedAttributeData` survives.

EXPOSE_PURE attributes are NOT removed from the design attributes dict, because they don't generate modules -- they're aliases. The ParameterGroupDeriver continues to see them as design attributes, which is correct (they derive their value from an upstream calc output, which the backtracker resolves).

### Decision 3: Module Naming -- `{part_name}__{attr_name}` per ADR-003

Synthetic modules for FORMULA computed attributes follow ADR-003 naming conventions.

#### Examples

| PartDef | Attribute | Module Name | Module Type (PascalCase) |
|---------|-----------|-------------|-------------------------|
| `probe_design` | `area` | `probe_design__area` | `ProbeDesignArea` |
| `probe_design` | `volume` | `probe_design__volume` | `ProbeDesignVolume` |
| `probe_design` | `cost_density` | `probe_design__cost_density` | `ProbeDesignCostDensity` |
| `solar_battery_plant` | `p_net_kw` | `solar_battery_plant__p_net_kw` | `SolarBatteryPlantPNetKw` |

#### Output Channel Names

Each FORMULA module has exactly one output, named after the attribute: `{module_name}__{attr_name}` (PQN format, per ADR-003).

Example: Module `probe_design__area` produces output channel `probe_design__area__area`.

#### Assumption: No Member Name Collisions

This naming convention assumes SysML prevents a CalcUsage and an AttributeUsage from sharing the same name on the same part. SysML v2 treats owned members as a flat namespace within a definition/usage, so duplicate names should be rejected by the parser. If this assumption proves wrong, the naming convention would need a type prefix (e.g., `plant__attr__area` vs `plant__calc__area`).

#### Provenance Marking

`PipelineModule.is_computed_attribute = True` distinguishes computed attribute modules from CalcUsage modules. This flag is used by:
- Pipeline YAML generator: adds `# source: computed_attribute` comment
- `IMPLEMENTATION_BACKLOG.md` generator: shows "auto-implemented" status
- Module registry `__init__.py`: includes in imports

### Decision 4: Backtracker Must Consume Computed Attributes

The backtracker (Step 6) receives `list[ComputedAttributeData]` as a new input alongside calc defs and calc usages. It uses this to correctly resolve CalcUsage bindings that target FORMULA computed attributes.

#### The Problem

Consider solar_battery's downstream flow:

```sysml
part solar_battery_plant {
    attribute p_net_mw : Real = 0.008;
    attribute p_net_kw : Real = p_net_mw * 1000.0;   // FORMULA

    calc annualized_om : AnnualizedOMCalc {
        in p_net_kw = p_net_kw;   // CalcUsage binds to computed attribute
    }
}
```

At Step 6, the backtracker traces `annualized_om`'s binding `in p_net_kw = p_net_kw`. Without computed attribute awareness, it finds a design attribute with no literal default and classifies it as ENTRY_POINT (or UNBOUND). After ATTR-EXPR, it must recognize that `p_net_kw` is a FORMULA computed attribute and resolve it as **MODULE_OUTPUT** from the synthetic module `solar_battery_plant__p_net_kw`.

#### Resolution Rules

When the backtracker encounters a binding target that matches an attribute name on the owning part:

1. **Check computed attributes first.** If the attribute name matches a FORMULA `ComputedAttributeData`, resolve as `MODULE_OUTPUT` from the synthetic module `{part_name}__{attr_name}`.
2. **Check EXPOSE aliases.** If the attribute name matches an EXPOSE_PURE `ComputedAttributeData`, follow the alias to the upstream calc output and resolve as `MODULE_OUTPUT` from that calc's module.
3. **Fall through to existing logic.** If neither, proceed with current behavior (literal design attribute -> ENTRY_POINT, etc.).

#### Interface Change

```python
# Before ATTR-EXPR:
def find_required_modules(
    self,
    calc_usages: list[CalcUsageData],
    calc_defs: list[CalculationDefinitionData],
    ...
) -> BacktrackingResult:

# After ATTR-EXPR:
class DependencyBacktracker:
    def __init__(
        self,
        all_usages: list[CalcUsageData],
        calc_defs: list[CalculationDefinitionData],
        ...,
        *,
        output_registry: OutputRegistry,  # NEW — sole resolution path
    ):
```

FORMULA computed attributes are registered in the OutputRegistry (Step 5.5, Phase 1) with dotted keys (e.g., `parent_part.attr_name`). The backtracker resolves CHAIN bindings to these via `registry.resolve(source_path)`. No internal computed attribute index is built -- the OutputRegistry is the single lookup.

### Chain Handling: A Non-Decision

The spike's most important discovery was that chains (computed attributes referencing other computed attributes) require **zero special handling** in the extraction or compilation layer.

```sysml
attribute area : Real = length * width;        // FORMULA
attribute cost : Real = area * rate;           // FORMULA (chain: references 'area')
attribute marked_up_cost : Real = cost * 1.15; // FORMULA (2-hop chain)
```

The compiler produces:
```python
area           = (inputs.length * inputs.width)
cost           = (inputs.area * inputs.rate)
marked_up_cost = (inputs.cost * 1.15)
```

The compiler treats `area` as just another input name. It doesn't know or care that `area` is itself a computed attribute. This is correct -- each computed attribute becomes its own module, and the module's input named `area` is wired to the upstream `probe_design__area` module's output by the graph builder.

Chain handling is purely topological ordering in the graph builder. The graph builder must place `probe_design__area` before `probe_design__cost` before `probe_design__marked_up_cost` in the execution order. This is the same topological sort already used for CalcUsage modules.

## Consequences

### Positive

1. **Clean provenance**: Every module traces to a real SysML element with a real source location. No phantom entities.
2. **Natural FORMULA/EXPOSE split**: FORMULA -> module, EXPOSE_PURE -> alias. No awkward special cases.
3. **Phase 1 compiler reused with zero changes**: The expression compiler is CalcDef-agnostic and works identically on attribute expression ASTs.
4. **Chain handling is free**: Topological sort in the graph builder handles all chain patterns without dedicated chain logic.
5. **Moderate implementation scope**: Graph builder extension is well-contained alongside the existing CalcUsage processing loop.
6. **Step 4/4.5 overlap cleanly resolved**: FORMULA removal from design_attributes prevents false entry points.

### Negative

1. **Graph builder complexity increases**: It now processes two entity types (CalcUsage and ComputedAttributeData) instead of one.
2. **Backtracker interface changes**: New parameter and resolution logic must be maintained.
3. **EXPOSE alias resolution is new code**: The attribute resolution map in the graph builder adds complexity that didn't exist before.

## Examples

### Example 1: Probe Fixture Chain (area -> cost -> cost_density)

**SysML**:
```sysml
part probe_design {
    attribute length : Real = 10.0;
    attribute width : Real = 5.0;
    attribute height : Real = 3.0;
    attribute rate : Real = 12.0;

    attribute area : Real = length * width;
    attribute cost : Real = area * rate;
    attribute volume : Real = length * width * height;
    attribute cost_density : Real = cost / volume;
}
```

**Generated Pipeline Modules** (in topological order):
1. `probe_design__area` (inputs: `length`, `width`)
2. `probe_design__volume` (inputs: `length`, `width`, `height`)
3. `probe_design__cost` (inputs: `area` from module 1, `rate`)
4. `probe_design__cost_density` (inputs: `cost` from module 3, `volume` from module 2)

**Generated Implementation** (auto-implemented, `probe_design__area`):
```python
def run(self, inputs):
    area = (inputs.length * inputs.width)
    return {"area": area}
```

### Example 2: Solar Battery p_net_kw with Downstream CalcUsage

**SysML**:
```sysml
part solar_battery_plant {
    attribute p_net_mw : Real = 0.008;
    attribute p_net_kw : Real = p_net_mw * 1000.0;

    calc annualized_om : AnnualizedOMCalc {
        in p_net_kw = p_net_kw;
    }
}
```

**Pipeline Flow**:
1. `solar_battery_plant__p_net_kw` module runs first (input: `p_net_mw = 0.008` as entry point)
2. Produces output: `p_net_kw = 8.0`
3. `annualized_om` module receives `p_net_kw = 8.0` via MODULE_OUTPUT wiring (not as entry point)

**Backtracker resolution**: When tracing `annualized_om`'s binding `in p_net_kw = p_net_kw`, the backtracker finds `p_net_kw` in its computed attribute lookup dict, classifies it as FORMULA, and resolves the binding source as MODULE_OUTPUT from `solar_battery_plant__p_net_kw`. The entry point for `p_net_mw = 0.008` is correctly derived as DESIGN_ATTRIBUTE.

### Example 3: Pipeline YAML Output

```yaml
# Computed attribute modules
solar_battery_plant__p_net_kw:  # source: computed_attribute
  module_type: SolarBatteryPlantPNetKw
  inputs:
    p_net_mw: float solar_battery_params.SolarBatteryDesign__solar_battery_plant__p_net_mw
  outputs:
    p_net_kw: float solar_battery_plant__p_net_kw__p_net_kw

# CalcUsage modules (downstream)
solarbatterydesign__solar_battery_plant__annualized_om:
  module_type: solarbatteryanalyses.AnnualizedOMModule
  inputs:
    p_net_kw: float solar_battery_plant__p_net_kw__p_net_kw  # wired from computed attr
  outputs:
    annual_om_cost: float SolarBatteryDesign__solar_battery_plant__annualized_om__annual_om_cost
```

## References

- **Concept document**: `.project/concepts/attr-expr-architectural-decisions.md` -- Sections 2, 5, 8, 9-10 (source material for this ADR)
- **Spike report v1**: `.project/active/attr-expr-spike/report.md` -- Architecture evaluation, chain handling discovery
- **Spike report v2**: `.project/active/attr-expr-spike/findings_v2.md` -- Probe fixture compilation results
- **E2E validation report**: `.project/active/attr-expr-e2e/report.md` -- 21 tests, solar_battery `p_net_kw` validated
- **ADR-003**: `docs/architecture/ADR-003-signal-identifiers.md` -- Module naming conventions (`{part}__{attr}`, PQN format)
- **ADR-005**: `docs/architecture/ADR-005-computed-attribute-classification.md` -- Classification scheme determining pipeline treatment

## Changelog

| Date | Change |
|------|--------|
| 2026-02-09 | Initial version -- formalized integration architecture (Option C), pipeline placement (Step 4.5), module naming, and backtracker awareness from ATTR-EXPR concept document and implementation findings |
