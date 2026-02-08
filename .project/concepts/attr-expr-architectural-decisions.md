# Concept: Attribute Expression Architectural Decisions

**Status**: Draft (pre-ADR)
**Date**: 2026-02-08
**Authors**: Reid + Claude
**Epic**: ATTR-EXPR (Phase 2)
**Prerequisite**: EXPR-CODEGEN (Phase 1) complete; ATTR-EXPR Item 1 spike complete (GO)
**Related**: `expression-aware-codegen.md` (Phase 1 concept), ADR-001, ADR-002, ADR-003

---

## 1. Context

Phase 1 (EXPR-CODEGEN) built an expression compiler that auto-implements CalcDef
outputs as Python code. Results: 15/15 solar_battery CalcDefs, 19/21 CATF CalcDefs
auto-implemented. The `_impl.py` bottleneck is largely eliminated.

Phase 2 (ATTR-EXPR) addresses the remaining overhead: the CalcDef *ceremony* itself.
For a formula like `volume = pi * r^2 * h`, modelers must still write a CalcDef in
library.sysml, a CalcUsage in design.sysml, and codegen generates a module wrapper
and pipeline YAML entry. That's ~100 lines of infrastructure for 1 line of math.

The ATTR-EXPR spike (Item 1, v1 + v2) proved:
- SysIDE populates `feature_value_expression` on all PartDef/PartUsage attributes
- 14/14 FORMULA patterns compile with the Phase 1 compiler, zero changes needed
- Chains (computed attrs referencing other computed attrs) work trivially
- EXPOSE patterns (pure FeatureChainExpression) fail compilation as expected

This document captures the architectural decisions for Items 2-4 of the ATTR-EXPR
epic. These decisions will be formalized as ADRs before the PR is merged.

---

## 2. Decision 1: Integration Architecture -- Option C (Direct Graph Integration)

### Decision

Computed attributes are modeled as a **first-class entity** (`ComputedAttributeData`)
that the graph builder processes directly alongside CalcUsages. We do NOT synthesize
phantom CalcDef+CalcUsage objects.

### Options Considered

| Option | Description | Pros | Cons |
|--------|-------------|------|------|
| **A: Synthetic CalcDef+CalcUsage** | Transform computed attributes into phantom CalcDef and CalcUsage data, inject into existing pipeline | Reuses all existing backtracker, graph builder, and generation infrastructure unchanged | Creates phantom SysML entities that don't exist in any model file; pollutes logs, YAML, and backlog with objects that have no source location; poor fit for EXPOSE patterns (an alias is not a CalcDef) |
| **B: Synthetic CalcUsage only** | Create synthetic CalcUsages referencing a shared "computed attribute CalcDef" | Lighter than A, still reuses module generation | Still creates phantom entities; CalcDef is a meaningless placeholder |
| **C: Direct graph integration** | `ComputedAttributeData` is first-class; graph builder generates `PipelineModule` from computed attributes directly | Clean provenance (every module traces to a real SysML element); FORMULA and EXPOSE get different treatment naturally; no phantom entities | Requires extending graph builder to understand a new entity type |
| **D: Inline @computed_field** | Computed attributes become `@computed_field` on Pydantic parameter schemas, no separate modules | Simplest for trivial formulas | Cannot handle cross-module dependencies; doesn't participate in pipeline YAML; limited to single-part scope |

### Rationale

1. **FORMULA and EXPOSE need fundamentally different pipeline treatment.** FORMULA
   attributes become synthetic modules. EXPOSE_PURE attributes become channel aliases
   (no module). Option A forces both through the same CalcDef-shaped hole, requiring
   awkward special cases inside the existing CalcUsage pipeline.

2. **Provenance matters.** Every `PipelineModule` in the current system traces back
   to a specific `calc` usage in a specific `.sysml` file. Phantom CalcDefs break
   this invariant. With Option C, computed attribute modules trace to the `attribute`
   declaration on the PartDef -- a real SysML element with a real source location.

3. **The graph builder extension is moderate and well-scoped.** The change is:
   alongside the existing loop over CalcUsage modules, add a second loop over
   FORMULA computed attributes. Each produces a `PipelineModule` with inputs and
   outputs. The rest of generation (templates, YAML, backlog) is unchanged.

4. **Option A was the original concept doc recommendation** (Section 3.2, "generate
   synthetic CalcUsages"). The spike findings provide new information that makes
   Option C more attractive: the strong FORMULA/EXPOSE split, the alias strategy
   for EXPOSE, and the discovery that chains are purely a graph-ordering concern.

### Consequences

- `ComputedAttributeData` becomes a new data model in `extraction/data_models.py`
- `build_computation_graph()` in `resolution/graph_builder.py` accepts computed
  attributes as an additional input
- `PipelineModule.is_computed_attribute` flag distinguishes provenance
- The concept doc's Step 3.5 ("generate synthetic CalcUsages, merge into usages
  list") is replaced with a direct computed attribute extraction step

---

## 3. Decision 2: Computed Attribute Classification Scheme

### Decision

Replace the original 5-way classification (FORMULA, EXPOSE, MIXED, LITERAL,
UNRESOLVABLE) with a more precise 5-way scheme that splits EXPOSE and drops MIXED.

### Classification Definitions and Examples

Each classification is illustrated with concrete SysML from the spike probe fixture
and real CATF/solar_battery models.

---

#### 3a. FORMULA -- Arithmetic on sibling attributes

**Definition**: An attribute expression where ALL feature references resolve to
sibling attributes on the same PartDef/PartUsage. No FeatureChainExpression nodes
(no dotted paths to calc outputs or other parts).

**Pipeline treatment**: Generate a synthetic `PipelineModule` with auto-implementation.

**Examples from spike probe**:

```sysml
part probe_design {
    attribute length : Real = 10.0;      // LITERAL input
    attribute width : Real = 5.0;        // LITERAL input
    attribute height : Real = 3.0;       // LITERAL input
    attribute rate : Real = 12.0;        // LITERAL input

    // FORMULA: simple binary
    attribute area : Real = length * width;

    // FORMULA: 3-term product
    attribute volume : Real = length * width * height;

    // FORMULA: chain -- references another computed attr
    attribute cost : Real = area * rate;

    // FORMULA: multi-hop chain
    attribute marked_up_cost : Real = cost * 1.15;

    // FORMULA: fan-in from two computed attrs
    attribute cost_density : Real = cost / volume;

    // FORMULA: deeply nested, 7 refs
    attribute p_blanket_thermal : Real =
        m_neutron * p_fusion + p_input
        + eta_thermal * (f_pump * eta_pump + f_subsystem)
          * (m_neutron * p_fusion);
}
```

**Compiled output** (from probe, all verified correct):
```python
area         = (inputs.length * inputs.width)
volume       = ((inputs.length * inputs.width) * inputs.height)
cost         = (inputs.area * inputs.rate)
cost_density = (inputs.cost / inputs.volume)
```

**Real model example** (solar_battery `design.sysml:60`):
```sysml
part solar_battery_plant {
    attribute p_net_mw : Real = 0.008;
    attribute p_net_kw : Real = p_net_mw * 1000.0;   // FORMULA
}
```

**Modeling practice impact**: This is the **primary new capability**. Modelers can
write `attribute volume = pi * r^2 * h` directly on a PartDef instead of creating
a CalcDef + CalcUsage. This eliminates the biggest remaining source of SysML
modeling overhead identified in the research report.

**Key finding from spike**: The compiler treats computed attributes identically to
literal attributes. `cost = area * rate` compiles to `(inputs.area * inputs.rate)`
regardless of whether `area` is a literal or itself a computed attribute. Chain
resolution is entirely a graph-builder concern (topological ordering), not a
compiler concern.

---

#### 3b. EXPOSE_PURE -- Single reference to a calc output, no operators

**Definition**: An attribute expression that is a single `FeatureChainExpression`
with no surrounding operators. The attribute's value IS the calc output -- pure
value forwarding.

**Pipeline treatment**: Channel alias. No synthetic module generated. When
something references this attribute, the graph builder resolves through the alias
to the upstream calc output channel.

**Examples from spike probe**:

```sysml
part probe_design {
    // CalcUsage -- the real computation
    calc scale_calc : ScaleCalc { in value = area; }
    calc split : SplitCalc { in value = volume; }

    // EXPOSE_PURE: surface a single calc output as a part-level attribute
    attribute scale_result : Real = scale_calc.result;
    attribute half_vol : Real = split.half;
    attribute quarter_vol : Real = split.quarter;
}
```

**Real model examples** (CATF `physics.sysml:114-122`):
```sysml
part def FusionPlasmaPhysics {
    calc alpha_neutron_split : AlphaNeutronSplitCalc {
        in p_fusion = p_fusion;
    }

    // EXPOSE_PURE: surface calc outputs for downstream wiring
    attribute p_alpha_out : Real = alpha_neutron_split.p_alpha;
    attribute p_neutron_out : Real = alpha_neutron_split.p_neutron;
}
```

And (CATF `system.sysml:204`):
```sysml
part def PowerConversionSystem {
    calc auxiliary_load : AuxiliaryLoadCalc { ... }

    attribute auxiliary_power : Real = auxiliary_load.auxiliary_power;  // EXPOSE_PURE
}
```

**Modeling practice impact**: **No change.** This IS the existing EXPOSE pattern
that modelers already use today. It was introduced as a wiring convenience so that
other parts can reference `physics.p_alpha_out` instead of the deeper path
`physics.alpha_neutron_split.p_alpha`.

The only question is whether the current backtracker already handles EXPOSE
transitively (when a CalcUsage binds to an EXPOSE attribute, does the backtracker
chase through to the calc output?). This is an Item 3 investigation, not a modeling
practice change. If the backtracker already handles it, EXPOSE_PURE requires zero
code changes. If not, the graph builder adds alias resolution.

**Why this classification matters even if "deferred"**: FORMULA modules may
reference EXPOSE attributes as inputs. If `cost_density = cost / volume` and
`cost` is a FORMULA but `volume` happens to be an EXPOSE alias for
`volume_calc.result`, the graph builder must resolve `volume` through the alias
to the upstream calc output channel. So the classifier must identify EXPOSE
attributes to provide wiring context, even though EXPOSE itself generates no
module.

---

#### 3c. EXPOSE_COMPUTED -- Calc output reference wrapped in arithmetic

**Definition**: An attribute expression containing BOTH a `FeatureChainExpression`
(calc output reference) AND arithmetic operators. This is "EXPOSE + math."

**Pipeline treatment**: Decompose into two parts: (1) resolve the
FeatureChainExpression to the upstream calc output channel, (2) generate a FORMULA
module that takes the resolved channel as an input and applies the remaining
arithmetic.

**Example from spike probe**:

```sysml
part probe_design {
    calc scale_calc : ScaleCalc { in value = area; }

    // EXPOSE_COMPUTED: takes a calc output AND does math on it
    attribute scaled_area : Real = scale_calc.result * 2.0;
}
```

The spike found this compiles with error `unsupported operator: .` because the
FeatureChainExpression (`scale_calc.result`) hits the compiler's unsupported-node
path.

**Hypothetical real-model example** (not in any current model):
```sysml
part def PowerPlant {
    calc cost_calc : TotalCostCalc { ... }

    // EXPOSE_COMPUTED: scale the calc output by inflation factor
    attribute adjusted_cost : Real = cost_calc.total_cost * inflation_factor;
}
```

**Modeling practice impact**: This is a **new capability that does not yet exist**
in any model. It would allow modelers to take a calc output and apply lightweight
arithmetic without creating a separate CalcDef for the scaling/adjustment.

**Status: DEFERRED.** No current model uses this pattern. When modelers need post-
calc arithmetic today, they create another CalcDef (which Phase 1 auto-implements).
The decomposition strategy is well-understood but adds implementation complexity
(FeatureChainExpression resolution inside the compiler or a pre-processing
decomposition step). We defer this until a concrete modeling need arises.

---

#### 3d. LITERAL -- No expression or pure constants

**Definition**: An attribute with either no expression (just a type declaration) or
a pure constant expression (`LiteralRational`, `LiteralInteger`, etc.) with no
feature references.

**Pipeline treatment**: Not a computed attribute. Handled by existing extraction as
`DesignAttributeData` with `default_value`. May become an entry point via the
existing `ParameterGroupDeriver`.

**Examples**:
```sysml
part probe_design {
    attribute length : Real = 10.0;      // LITERAL (constant)
    attribute width : Real = 5.0;        // LITERAL (constant)
    attribute name : String;             // LITERAL (no expression)
}
```

**Modeling practice impact**: None. This is the existing behavior.

---

#### 3e. UNRESOLVABLE -- References that can't be resolved

**Definition**: An attribute expression with feature references that don't match
any sibling attribute or known calc usage on the same part.

**Pipeline treatment**: Log a warning, skip. Do not generate a module.

**Example** (hypothetical):
```sysml
part probe_design {
    // UNRESOLVABLE: 'mystery_value' is not a sibling attribute or calc usage
    attribute broken : Real = length * mystery_value;
}
```

**Modeling practice impact**: None. This is an error condition. The classifier
catches it and provides a clear diagnostic rather than silently dropping the
expression.

---

### Classification Summary

| Classification | Generates Module? | Exists in Current Models? | Modeling Practice Change? |
|---------------|-------------------|--------------------------|--------------------------|
| FORMULA | Yes (synthetic, auto-implemented) | Rare (1 instance in solar_battery) | **New option**: write formulas without CalcDefs |
| EXPOSE_PURE | No (channel alias) | Common (19+ in CATF) | **No change**: existing EXPOSE pattern continues |
| EXPOSE_COMPUTED | Deferred | None | **Deferred**: new option for post-calc arithmetic |
| LITERAL | No (existing handling) | Very common | **No change** |
| UNRESOLVABLE | No (warning) | None | **No change** |

### Why MIXED Was Dropped

The original classification had MIXED defined as "references both sibling attributes
and calc outputs." The spike probe found:

1. **Zero MIXED patterns in any real model** across 540 attributes
2. **The D2 pattern** (`scale_calc.result * 2.0`) was predicted to be MIXED but
   classified as EXPOSE because the `2.0` is a literal (no feature ref), not a
   sibling attribute reference
3. **The MIXED concept conflated two distinct concerns**: "what do the references
   point to?" and "what operations wrap them?" The EXPOSE_PURE / EXPOSE_COMPUTED
   split captures the meaningful distinction more precisely

If a true MIXED pattern appears in a future model (`attr = sibling_a + calc.output`),
it would be classified as EXPOSE_COMPUTED (because it contains a
FeatureChainExpression + operators) and handled by the same decomposition strategy.

---

## 4. Decision 3: EXPOSE Handling Strategy

### Decision

- **EXPOSE_PURE**: Classify and record, but do not generate a module. Provide alias
  resolution context to the graph builder so that FORMULA modules referencing EXPOSE
  attributes wire correctly.
- **EXPOSE_COMPUTED**: Classify and record, but defer implementation. Log as
  "not yet supported" if encountered in a real model.

### Rationale: Why EXPOSE_PURE Doesn't Need a Module

An EXPOSE_PURE attribute like `attribute p_alpha_out = alpha_neutron_split.p_alpha`
carries no computation. It's a name alias: "when someone says `p_alpha_out`, they
mean `alpha_neutron_split.p_alpha`." Generating a passthrough module for this would
create pipeline overhead (module wrapper, YAML entry, schema) for zero computational
value.

Instead, the graph builder maintains an alias map:
```
p_alpha_out → alpha_neutron_split::p_alpha (module output channel)
```

When building a FORMULA module that references `p_alpha_out` as an input, the graph
builder resolves the alias to the upstream calc output channel and wires directly.

### Interaction with Existing Backtracker

The current backtracker may already handle EXPOSE transitively. When a CalcUsage
has a binding like `in x = p_alpha_out`, the backtracker traces `p_alpha_out` and
(potentially) discovers it's an attribute with a value expression pointing to
`alpha_neutron_split.p_alpha`. This is the "transitive resolution" path at lines
567-624 of `dependency_backtracker.py`.

**Item 3 must verify this.** If confirmed:
- EXPOSE_PURE for CalcUsage bindings requires zero code changes
- EXPOSE_PURE for FORMULA module inputs requires graph builder alias resolution
  (new, but lightweight)

If not confirmed:
- The graph builder adds alias resolution for both cases
- The backtracker may need a small extension for the CalcUsage binding case

### What Doesn't Change About Modeling Practice

The EXPOSE pattern was introduced as part of Approach E (modeling discipline) to
solve a specific wiring problem:

```
BEFORE EXPOSE (verbose wiring):
  part system {
      part physics { calc alpha_split : AlphaNeutronSplit { ... } }
      part blanket {
          calc thermal : BlanketThermal {
              in p_alpha = physics.alpha_split.p_alpha;  // deep path
          }
      }
  }

AFTER EXPOSE (cleaner wiring):
  part system {
      part physics {
          calc alpha_split : AlphaNeutronSplit { ... }
          attribute p_alpha_out = alpha_split.p_alpha;     // EXPOSE
      }
      part blanket {
          calc thermal : BlanketThermal {
              in p_alpha = physics.p_alpha_out;            // shallow path
          }
      }
  }
```

This modeling practice **does not change at all** with ATTR-EXPR. Modelers continue
to use EXPOSE for wiring convenience. The only thing that changes is codegen's
internal handling: it now classifies the EXPOSE attribute and uses it for alias
resolution when building FORMULA modules.

---

## 5. Decision 4: Pipeline Placement

### Decision

Computed attribute extraction runs as **Step 4.5**, after design attribute extraction
(Step 4) and before parameter group derivation (Step 5).

### Updated Pipeline Flow

```
Step 1:   Load SysML models via SysideAdapter
Step 2:   extract_calculation_definitions()        → list[CalculationDefinitionData]
Step 3:   extract_calculation_usages()              → list[CalcUsageData]
Step 4:   extract_design_attributes()               → dict[Path, list[DesignAttributeData]]
Step 4.5: extract_computed_attributes()              → list[ComputedAttributeData]     ← NEW
            + removes FORMULA attributes from Step 4's design_attributes dict
Step 5:   ParameterGroupDeriver                      → list[ParameterGroup]
Step 6:   DependencyBacktracker.find_required_modules() → BacktrackingResult
            + NEW: accepts computed_attributes (from Step 4.5) for resolution
Step 6.5: classify_compilability()                   → dict[str, CalcDefCompilationResult]
Step 7:   build_computation_graph()                  → ComputationGraph
            + NEW: accepts computed_attributes as additional input
            + generates PipelineModule for each FORMULA computed attribute
            + resolves EXPOSE_PURE aliases for input wiring
Step 8:   Generation (modules, stencils, YAML, schemas, backlog)
```

### Why Step 4.5?

Step 4.5 needs:
- PartDef/PartUsage element data (from Step 3, available on the loaded model)
- CalcUsage names on each part (from Step 3, needed for EXPOSE classification)
- Sibling attribute names on each part (from the model, needed for FORMULA
  reference resolution)

Step 4.5 feeds:
- `ComputedAttributeData` list into Step 6 (backtracker, for resolution) and
  Step 7 (`build_computation_graph`, for module generation)
- EXPOSE alias map into Step 7 (for input wiring resolution)
- Potentially new entry points into Step 5 (FORMULA inputs that aren't upstream
  outputs become entry points)

### Step 4 / Step 4.5 Overlap: Preventing Double-Handling

A FORMULA attribute like `p_net_kw = p_net_mw * 1000.0` will be processed by both
Step 4 (as a `DesignAttributeData` with `default_value=None`, since the expression
isn't a pure literal) and Step 4.5 (as a `ComputedAttributeData` with classification
FORMULA).

This creates a risk: the ParameterGroupDeriver in Step 5 sees `p_net_kw` as a design
attribute with no default and may incorrectly derive an entry point for it. But
`p_net_kw` is computed — it should NOT be an entry point.

**Resolution**: After Step 4.5 classifies FORMULA attributes, it **removes them from
the design attributes dict** before the dict is passed to Step 5. This is a simple
set subtraction keyed on `(owning_part_qualified_name, attribute_name)`. The
`DesignAttributeData` for `p_net_kw` is dropped; only the `ComputedAttributeData`
survives.

EXPOSE_PURE attributes are NOT removed from the design attributes dict, because they
don't generate modules — they're aliases. The ParameterGroupDeriver continues to
see them as design attributes, which is correct (they derive their value from an
upstream calc output, which the backtracker resolves).

LITERAL attributes are unaffected — they remain in the design attributes dict and
may become entry points as today.

### Difference from Concept Doc

The original concept doc (Section 3.2) placed computed attribute extraction at
Step 3.5 and generated synthetic CalcUsages that merged into the CalcUsage list.
With Option C, we instead place it at Step 4.5 (after design attribute extraction,
which it logically extends) and pass the results directly to the graph builder
without synthesizing CalcUsages.

---

## 6. Decision 5: Module Naming for Computed Attributes

### Decision

Synthetic modules for FORMULA computed attributes follow ADR-003 naming:
`{part_name}__{attr_name}` using lowercase EQN (execution qualified name).

### Examples

| PartDef | Attribute | Module Name | Module Type (PascalCase) |
|---------|-----------|-------------|-------------------------|
| `probe_design` | `area` | `probe_design__area` | `ProbeDesignArea` |
| `probe_design` | `volume` | `probe_design__volume` | `ProbeDesignVolume` |
| `probe_design` | `cost_density` | `probe_design__cost_density` | `ProbeDesignCostDensity` |
| `solar_battery_plant` | `p_net_kw` | `solar_battery_plant__p_net_kw` | `SolarBatteryPlantPNetKw` |

### Output Channel Names

Each FORMULA module has exactly one output, named after the attribute:
`{module_name}__{attr_name}` (PQN format, per ADR-003).

Example: Module `probe_design__area` produces output channel
`probe_design__area__area`.

### Assumption: No Member Name Collisions

This naming convention assumes SysML prevents a CalcUsage and an AttributeUsage
from sharing the same name on the same part. If `part plant` has both
`calc area : AreaCalc { ... }` and `attribute area : Real = l * w`, both would
produce module name `plant__area` — a collision.

SysML v2 treats owned members as a flat namespace within a definition/usage, so
duplicate names should be rejected by the parser. If this assumption proves wrong
(e.g., SysIDE allows overloading across meta-types), the naming convention would
need a type prefix (e.g., `plant__attr__area` vs `plant__calc__area`). For now we
rely on SysML's namespace rules.

### Provenance Marking

`PipelineModule.is_computed_attribute = True` distinguishes computed attribute
modules from CalcUsage modules. This flag is used by:
- Pipeline YAML generator (optional: add `# computed attribute` comment)
- `IMPLEMENTATION_BACKLOG.md` generator (show "auto-implemented" status)
- Module registry `__init__.py` (include in imports)

---

## 7. Decision 6: Qualified Name Resolution in Classification

### Decision

The computed attribute classifier MUST use `ref.qualified_name` to determine
reference targets. Simple `ref.name` matching is insufficient and produces
incorrect classifications.

### The Problem

The v1 spike found 19 CATF attributes misclassified as MIXED because CalcDef
output names collided with sibling attribute names:

```sysml
part def FusionPlasmaPhysics {
    attribute p_alpha : Real = 2600.0 * 3.52 / 17.58;  // sibling attr named "p_alpha"

    calc alpha_neutron_split : AlphaNeutronSplitCalc {
        out p_alpha : Real = ...;                        // calc output also named "p_alpha"
    }

    attribute p_alpha_out : Real = alpha_neutron_split.p_alpha;  // EXPOSE
}
```

When classifying `p_alpha_out`, `extract_feature_refs()` returns two refs:
- `ref.name = "p_alpha"`, `ref.qualified_name = "CATFLibrary::AlphaNeutronSplitCalc::p_alpha"`
- `ref.name = "alpha_neutron_split"`, `ref.qualified_name = "CATFDesign::physics::alpha_neutron_split"`

Using simple name matching, `p_alpha` matches the sibling attribute AND is part of
a calc output reference. The classifier incorrectly produces MIXED.

Using qualified name matching, `CATFLibrary::AlphaNeutronSplitCalc::p_alpha` is
clearly a CalcDef output (different namespace), not a sibling attribute. The
classifier correctly produces EXPOSE_PURE.

### Rule

For each ref returned by `extract_feature_refs()`:
1. Check if `ref.qualified_name` shares the same parent namespace as the owning
   part's qualified name → **sibling attribute reference**
2. Check if `ref.qualified_name` matches a CalcDef output namespace → **calc
   output reference** (EXPOSE indicator)
3. Check if `ref.name` matches a CalcUsage name on the owning part → **calc usage
   instance** (part of a FeatureChainExpression, EXPOSE indicator)
4. Otherwise → **unresolvable**

---

## 8. Decision 7: Backtracker Must Consume Computed Attributes

### Decision

The backtracker (Step 6) receives `list[ComputedAttributeData]` as a new input
alongside calc defs and calc usages. It uses this to correctly resolve CalcUsage
bindings that target FORMULA computed attributes.

### The Problem

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

At Step 6, the backtracker traces `annualized_om`'s binding `in p_net_kw = p_net_kw`.
Today, it finds a design attribute with no literal default and likely classifies it
as ENTRY_POINT (or UNBOUND). After ATTR-EXPR, it must recognize that `p_net_kw` is
a FORMULA computed attribute and resolve it as **MODULE_OUTPUT** from the synthetic
module `solar_battery_plant__p_net_kw`.

This is not just a graph builder concern -- it's a first-order change to the
backtracker's resolution logic.

### Resolution Rules

When the backtracker encounters a binding target that matches an attribute name on
the owning part:

1. **Check computed attributes first.** If the attribute name matches a FORMULA
   `ComputedAttributeData`, resolve as `MODULE_OUTPUT` from the synthetic module.
2. **Check EXPOSE aliases.** If the attribute name matches an EXPOSE_PURE
   `ComputedAttributeData`, follow the alias to the upstream calc output and
   resolve as `MODULE_OUTPUT` from that calc's module.
3. **Fall through to existing logic.** If neither, proceed with current behavior
   (literal design attribute → ENTRY_POINT, etc.).

### Interface Change

```python
# Current:
def find_required_modules(
    self,
    calc_usages: list[CalcUsageData],
    calc_defs: list[CalculationDefinitionData],
    ...
) -> BacktrackingResult:

# After ATTR-EXPR:
def find_required_modules(
    self,
    calc_usages: list[CalcUsageData],
    calc_defs: list[CalculationDefinitionData],
    computed_attributes: list[ComputedAttributeData],  # NEW
    ...
) -> BacktrackingResult:
```

The backtracker builds a lookup dict from computed attributes keyed by
`(owning_part_qualified_name, attribute_name)` for O(1) resolution during
dependency tracing.

---

## 9. Modeling Practice Summary

### What Changes for Modelers

| Capability | Before ATTR-EXPR | After ATTR-EXPR |
|-----------|-----------------|-----------------|
| Simple formula (`volume = l * w * h`) | Must create CalcDef + CalcUsage | Write `attribute volume = l * w * h` on PartDef |
| Aggregation (`total = a + b + c`) | Must create aggregation CalcDef (Approach E Rule 3) | Write `attribute total = a + b + c` on PartDef |
| EXPOSE pattern (`p_out = calc.output`) | Already works as modeling convention | **No change** -- continues to work; codegen now classifies it internally |
| EXPOSE + arithmetic (`adj = calc.output * 1.15`) | Must create a separate CalcDef for the arithmetic | **Deferred** -- still requires a CalcDef for now (see UX gap note below) |
| Complex calculations (physics, costs) | CalcDef + auto-implemented `_impl.py` (Phase 1) | **No change** -- complex calcs stay as CalcDefs |

### What Doesn't Change

1. **CalcDefs remain the right tool for reusable, complex computations.** A CalcDef
   like `TorusVolumeCalc` that's used across multiple parts should stay a CalcDef.
   Computed attributes are for one-off formulas tied to a specific design part.

2. **The EXPOSE pattern is unaffected.** Modelers continue to write
   `attribute p_alpha_out = alpha_split.p_alpha` for wiring convenience. Codegen
   now understands this pattern internally but requires no modeling changes.

3. **Approach E modeling discipline still applies for patterns not yet supported.**
   Hierarchy, multiplicity, and aggregation-across-parts (Phase 3) still require
   the Approach E rules.

4. **All existing models continue to work without modification.** ATTR-EXPR is
   purely additive. No model changes are required to benefit from it.

### Known UX Gap: EXPOSE_COMPUTED Deferral

After ATTR-EXPR, this works:
```sysml
attribute area : Real = length * width;                    // FORMULA -- works!
```

But this does not:
```sysml
attribute adjusted_cost : Real = cost_calc.total * 1.15;   // EXPOSE_COMPUTED -- deferred
```

From a modeler's perspective, these look similar — both are "attribute equals
expression." The distinction (sibling attribute refs vs. calc output refs) is an
implementation detail of how SysIDE represents dotted paths. Modelers may find this
surprising.

**Workaround**: The modeler creates a CalcDef for the adjustment. Phase 1 auto-
implements it, so no handwritten `_impl.py` is needed. The overhead is the CalcDef
ceremony (~20 lines), not manual implementation.

**Future resolution**: The decomposition strategy (resolve FeatureChainExpression to
upstream channel name, then compile remaining expression as FORMULA) is technically
tractable. It would be a pre-processing step that transforms the AST before handing
it to the existing compiler — the compiler itself wouldn't change. This could be
added in a follow-up if modelers hit this gap frequently. The trigger would be
multiple modelers independently writing `attribute x = calc.output * factor` and
being surprised it doesn't work.

**Modeler guidance**: Until EXPOSE_COMPUTED is supported, document the rule clearly:
"Attribute expressions can reference sibling attributes on the same part. To
reference a calc output, use the EXPOSE pattern (pure alias, no arithmetic) or
create a CalcDef."

### Approach E Rule Relaxation

| Approach E Rule | Current Status | After ATTR-EXPR |
|----------------|---------------|-----------------|
| Rule 1: Multiplicity is a parameter | Required | Required (Phase 3) |
| Rule 2: `:>>` redefinition creates CalcUsage | Required | Required (Phase 3) |
| Rule 3: Aggregation is an explicit CalcDef | Required | **Optional** -- can use `attribute total = a + b + c` |
| Rule 4: Context is a flat parameter | Required | Required (Phase 3) |
| Rule 5: Every formula is a CalcDef | Required | **Optional** for simple formulas -- can use `attribute x = expr` |

---

## 9. Chain Handling: A Non-Decision

### Finding

The spike's most important discovery was that chains (computed attributes
referencing other computed attributes) require **zero special handling** in the
extraction or compilation layer.

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

The compiler treats `area` as just another input name. It doesn't know or care
that `area` is itself a computed attribute. This is correct -- each computed
attribute becomes its own module, and the module's input named `area` will be
wired to the upstream `probe_design__area` module's output by the graph builder.

### Consequence

- **Item 2 (extraction/data models)**: No chain-awareness needed. The extraction
  logic classifies each attribute independently.
- **Item 3 (pipeline integration)**: Chain handling is purely topological ordering
  in the graph builder. The graph builder must place `probe_design__area` before
  `probe_design__cost` before `probe_design__marked_up_cost` in the execution
  order. This is the same topological sort already used for CalcUsage modules.

### Edge Case: FORMULA-as-Passthrough

An attribute like `attribute b : Real = a` (single `FeatureReferenceExpression`, no
operators) classifies as FORMULA — all refs are sibling attributes. It compiles to
`inputs.a` and generates a passthrough module that does nothing but forward a value.

This is functionally correct but wasteful. In practice this pattern is unlikely to
occur (modelers would just reference `a` directly). If encountered during Item 3
testing, note it but don't special-case it — a trivial passthrough module is
harmless.

---

## 10. EXPOSE Within FORMULA: The Interaction Case

### Scenario

A FORMULA attribute may reference an EXPOSE attribute as one of its inputs:

```sysml
part def PowerPlant {
    calc efficiency_calc : EfficiencyCalc { ... }

    // EXPOSE_PURE: surface calc output
    attribute thermal_efficiency : Real = efficiency_calc.eta_thermal;

    // FORMULA: references an EXPOSE attribute
    attribute useful_power : Real = p_fusion * thermal_efficiency;
}
```

When building the FORMULA module for `useful_power`, the graph builder encounters
input `thermal_efficiency`. It must determine that this is an EXPOSE alias for
`efficiency_calc.eta_thermal` (a module output channel) rather than a literal
entry point.

### Resolution Strategy

The graph builder maintains a per-part attribute resolution map built from the
classification results:

```python
resolution_map = {
    "p_fusion": AttributeResolution(kind="literal", entry_point=True),
    "thermal_efficiency": AttributeResolution(
        kind="expose_alias",
        upstream_module="efficiency_calc",
        upstream_output="eta_thermal",
    ),
}
```

When wiring FORMULA module inputs:
1. Look up each input name in the resolution map
2. If `kind == "literal"` → wire to entry point (existing behavior)
3. If `kind == "expose_alias"` → wire to upstream module output channel
4. If `kind == "formula"` → wire to the computed attribute's synthetic module output
5. If not found → wire to entry point as default (conservative behavior)

This is the primary reason EXPOSE classification is needed in Item 2 even though
EXPOSE itself generates no module.

---

## 11. Deferred Decisions (Phase 3 or Later)

These decisions are explicitly deferred. They are recorded here for context but
are out of scope for the ATTR-EXPR epic.

| Decision | Trigger for Revisiting |
|----------|----------------------|
| EXPOSE_COMPUTED implementation (FeatureChain + arithmetic decomposition) | A real model uses this pattern |
| Cross-part attribute references (`reactor.power * 1.5`) | Hierarchy extraction (Phase 3) |
| `InvocationExpression` support (`sqrt(x)`, `min(a, b)`) | A real model uses function calls in attribute expressions |
| `SelectExpression` support (`if condition then a else b`) | A real model uses conditional attribute expressions |
| Part hierarchy with multiplicity | Phase 3 epic |
| `:>>` redefinition chain resolution | Phase 3 epic |

---

## 12. Refined Epic Item Scoping

### Item 2: Computed Attribute Extraction & Data Models (~1 day)

**Scope (narrowed from original)**:
- `ComputedAttributeClassification` enum: FORMULA, EXPOSE_PURE, EXPOSE_COMPUTED,
  LITERAL, UNRESOLVABLE
- `ComputedAttributeData` dataclass with all fields
- `extract_computed_attributes()` function: scan PartDef attributes, classify,
  compile FORMULA patterns
- Qualified name resolution in classifier (mandatory)
- `expression_text` field is display-only (populated via `reconstruct_expression()`)
- No chain-awareness in extraction logic
- Unit tests for all 5 classification categories

**Explicitly excluded from Item 2**:
- Pipeline integration (Item 3)
- Backtracker changes (Item 3)
- EXPOSE_COMPUTED compilation (deferred)
- Graph builder changes (Item 3)

### Item 3: Pipeline Integration (~2-2.5 days)

**Primary deliverable**: FORMULA computed attributes generate synthetic pipeline
modules with auto-implementations.

**Secondary investigation**: Does the backtracker already handle EXPOSE_PURE
transitively for CalcUsage bindings? Document findings. Implement alias resolution
in graph builder for FORMULA→EXPOSE input wiring.

**Key sub-tasks**:
1. Add Step 4.5 to `build_pipeline_context()` in `initialization.py`
2. Extend `build_computation_graph()` to accept and process FORMULA computed attrs
3. Build attribute resolution map (literal / expose_alias / formula) per part
4. Wire FORMULA module inputs using the resolution map
5. Topological ordering of computed attribute modules (chains)
6. Verify EXPOSE_PURE backtracker behavior for CalcUsage bindings
7. Reuse Phase 1 `auto_implementation.py.jinja2` template for computed attr modules
8. Include computed attr modules in pipeline YAML, backlog, registry

**Deferred from Item 3**:
- EXPOSE_COMPUTED decomposition
- Cross-part references
- Inline module optimization (expression in module wrapper, no separate file)

### Item 4: E2E Validation (~1 day)

**Primary fixture**: Reuse `tests/fixtures/attr_expr_probe/` (14 FORMULA + 3 chain
+ 4 EXPOSE + 2 CalcUsages). Extend with numerical ground truth values.

**Real-model validation**: solar_battery `p_net_kw = p_net_mw * 1000.0`.

**Regression gate**: All 167+ existing tests pass with zero failures.

---

## 13. ADR Candidates

After the epic is implemented and validated, these decisions should be formalized:

| ADR | Captures |
|-----|----------|
| ADR-004: Computed Attribute Pipeline Integration | Decision 1 (Option C), Decision 4 (pipeline placement), Decision 5 (module naming), Decision 7 (backtracker awareness) |
| ADR-002 Amendment: Relaxation of Rule 3 and Rule 5 | Section 9 (modeling practice changes), allowing `attribute x = expr` |
| ADR-005: Computed Attribute Classification | Decision 2 (5-way scheme), Decision 3 (EXPOSE strategy), Decision 6 (qualified name resolution) |

These ADRs should be drafted as part of the PR, referencing this concept document
and the spike findings for empirical grounding.

---

## Changelog

| Date | Change |
|------|--------|
| 2026-02-08 | Initial draft capturing 6 architectural decisions from Item 1 spike findings |
| 2026-02-08 | Rev 2: Added Decision 7 (backtracker computed attribute awareness). Addressed Step 4/4.5 overlap with FORMULA attribute removal from design_attributes. Flagged EXPOSE_COMPUTED UX gap with workaround guidance. Added passthrough edge case note, member name collision assumption. Updated pipeline flow to show backtracker consuming computed attributes. |
