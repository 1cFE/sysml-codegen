# 06: How sysml-codegen Works (Algorithm Overview)

**Date:** 2026-02-13
**Purpose:** Plain-language walkthrough of the full codegen pipeline with visual diagrams.
Explains what each stage does, what guarantees it makes, and how data flows end-to-end.

---

## Table of Contents

1. [The Big Picture](#1-the-big-picture)
2. [Pipeline Overview Diagram](#2-pipeline-overview-diagram)
3. [Steps 1-3: Extraction -- What Exists in the Model?](#3-steps-1-3-extraction)
4. [Steps 3.5-3.6: Hierarchy Processing -- Templates, Overrides, and Aggregation](#4-steps-35-36-hierarchy)
5. [Steps 4-4.7: Design Attributes and Computed Attributes](#5-steps-4-47-attributes)
6. [Steps 5-6: Analysis -- Backtracking and Parameter Groups](#6-steps-5-6-analysis)
7. [Step 6.5: Expression Compilation](#7-step-65-compilation)
8. [Step 7: Build the Computation Graph](#8-step-7-graph)
9. [Generation: Templates Produce the Output Package](#9-generation)
10. [Cross-Cutting: The Naming System](#10-naming-system)
11. [Known Fragilities and Open Issues](#11-known-fragilities)

---

## 1. The Big Picture

sysml-codegen reads SysML v2 model files and produces a complete, runnable Python pipeline.
The pipeline is a DAG (directed acyclic graph) of calculation modules wired together by named channels.

```
 SysML v2 Model Files (.sysml)
         |
         v
 +-----------------------------------------------+
 |          sysml-codegen Pipeline                |
 |                                                |
 |  [Extract] -> [Analyze] -> [Resolve] -> [Gen] |
 +-----------------------------------------------+
         |
         v
 Generated Python Package:
   modules/          TEAx module wrappers
   handwritten/      Implementation stencils (or auto-impls)
   pipelines/        Pipeline YAML (the DAG wiring)
   schemas/          Pydantic data models
   inputs/           JSON templates for user parameters
   __init__.py       Module registry
```

**The core question the pipeline answers:**

> For every calculation input, where does its value come from?
> Either (a) it's an **entry point** (user provides it), or
> (b) it's a **module output** from an upstream calculation.

That's it. The entire pipeline is about answering that question for every input
on every calculation, then generating code that wires them together.

---

## 2. Pipeline Overview Diagram

The initialization builds a `PipelineContext` in ~10 numbered steps.
Each step is explained in detail in the section indicated by `-->`.

```
 SysML Files
     |
     |  Step 1: Load Models                                   -.
     |  Step 2: Extract CalcDefs                               |  --> Section 3
     |  Step 3: Extract CalcUsages (+ template expansion)     -'
     v
 CalcDefs + CalcUsages (with bindings)
     |
     |  Step 3.5: Hierarchy extraction & binding rewrite      -.
     |  Step 3.6: Alias enrichment                            -'  --> Section 4
     v
 + HierarchyExtractionResult (redefinitions, multiplicities, aggregations)
     |
     |  Step 4:   Extract design attributes                   -.
     |  Step 4.5: Extract & classify computed attributes       |  --> Section 5
     |  Step 4.7: Scope aggregation expressions               -'
     v
 + DesignAttrs + ComputedAttrs + ScopedAggregationData
     |
     |  Step 5: Build ParameterGroupDeriver (indexes)         -.
     |  Step 6: Dependency backtracking (THE CORE ALGORITHM)  -'  --> Section 6
     v
 BacktrackingResult (binding_resolutions for EVERY input)
     |
     |  Step 6.5: Expression compilation                          --> Section 7
     v
 + CalcDefCompilationResults
     |
     |  Step 7: Build ComputationGraph (THE SINGLE SOURCE OF TRUTH)  --> Section 8
     v
 ComputationGraph (modules + entry_point_groups + execution_order)
     |
     |  Generation: Jinja2 templates                              --> Section 9
     v
 Generated Python Package
```

### How to read the rest of this document

Sections 3-9 follow the pipeline in order. Read them top-to-bottom and you're reading
the algorithm top-to-bottom. Section 10 (naming) is a cross-cutting concern referenced
throughout.

---

## 3. Steps 1-3: Extraction -- What Exists in the Model? {#3-steps-1-3-extraction}

### Step 1: Load Models

Parse `.sysml` files via the SysIDE adapter into an in-memory AST.
Nothing interesting happens here -- it's just I/O.

### Step 2: Extract Calculation Definitions (CalcDefs)

**Question answered:** "What formulas exist in the library?"

Each `CalculationDefinitionData` has:
- `name`, `qualified_name` (SysML `::` format)
- `input_attributes`, `output_attributes` (lists of `AttributeInfo`)
- `output_expression_asts` (raw SysIDE AST nodes -- used later in Step 6.5)

```
 Example CalcDef:
 +-----------------------------------------+
 | calc def NetElectricPower               |
 |   input p_fusion : Real                 |
 |   input p_recirculating : Real          |
 |   input eta_gross : Real                |
 |   input eta_aux : Real                  |
 |   output p_net : Real                   |
 |   p_net = p_fusion * eta_gross          |
 |           - p_recirculating             |
 +-----------------------------------------+
```

### Step 3: Extract Calculation Usages (CalcUsages)

**Question answered:** "Where are those formulas instantiated in the design, and how are their inputs wired?"

Each `CalcUsageData` has:
- `instance_name` (e.g., `"net_electric"`)
- `calc_def_name` (which CalcDef it instantiates)
- `qualified_name` (globally unique EQN -- see [Section 10](#10-naming-system))
- `bindings` (list of `BindingInfo` -- the wiring)
- `unbound_params` (inputs with no binding)

#### The four kinds of bindings

This is the most fundamental concept in the whole system. When a CalcUsage instantiates
a CalcDef, each input parameter can be bound in one of four ways:

```
 CalcDef "NetElectricPower":         CalcUsage "net_electric":
   input p_fusion : Real               p_fusion = alpha_split.p_alpha   <-- CHAIN
   input p_recirculating : Real         p_recirculating = 50.0          <-- LITERAL
   input eta_gross : Real               eta_gross = GrossEff            <-- REFERENCE
   input eta_aux : Real                 (not mentioned)                 <-- UNBOUND
```

| Binding Type | What It Looks Like | Meaning |
|---|---|---|
| **CHAIN** | `p_fusion = alpha_split.p_alpha` | "Wire to output `p_alpha` from CalcUsage `alpha_split`" |
| **REFERENCE** | `eta_gross = GrossEff` | "Wire to something named `GrossEff` (a qualified SysML name)" |
| **LITERAL** | `p_recirculating = 50.0` | "This input is a constant value" |
| **UNBOUND** | (parameter not mentioned) | "No binding; use the CalcDef's default if it has one" |

These bindings are the **raw wiring instructions**. Step 6 (backtracking) is where they
get resolved into concrete `MODULE_OUTPUT` or `ENTRY_POINT` decisions.

#### Template detection (COST-PATTERN)

Step 3 also detects CalcUsages that live on **PartDefinitions** (templates) rather than
**PartUsages** (concrete design instances):

```
 For each CalcUsage found:
   Is its owning_type a PartDefinition?
     YES -> flag is_template=True, record owning_part_def_qn
     NO  -> normal CalcUsage (keep as-is)
```

Template CalcUsages get **virtually expanded**: one copy per design instance that
uses that PartDefinition. For example, `cost_model` on PartDef `Solar_Array` expands
into separate CalcUsages for `pv_module__cost_model`, `inverter__cost_model`, etc.

```
 Template: cost_model on PartDef Solar_Array
 Design instances of Solar_Array: [pv_module, inverter, frame]

 Virtual expansion:
   solar_battery_plant__solar_array__pv_module__cost_model
   solar_battery_plant__solar_array__inverter__cost_model
   solar_battery_plant__solar_array__frame__cost_model
```

Each virtual CalcUsage gets a hierarchy-scoped EQN (see [Section 10](#10-naming-system))
and inherits the template's bindings. Those bindings get rewritten in Step 3.5.

### Step 3 output

After Step 3, we have a flat list of CalcUsages -- both "real" ones from the design
and "virtual" ones from template expansion. The rest of the pipeline treats them identically.

---

## 4. Steps 3.5-3.6: Hierarchy Processing {#4-steps-35-36-hierarchy}

These steps extract metadata from the part hierarchy that the flat CalcUsage list doesn't capture:
override values, array multiplicities, and aggregation expressions.

### Step 3.5: Hierarchy Extraction and Virtual Binding Rewrite

**Question answered:** "How does the design hierarchy customize template parameters and roll up costs?"

This step does THREE things:

#### (A) Extract `:>>` redefinitions

Scans PartDefinition members for `:>>` (redefine) statements. Each is classified by its RHS:

```
 :>> wattage = 400              -> LITERAL  (direct value override)
 :>> capital_cost = cost.total  -> CHAIN    (alias to another attribute)
 :>> cost = sum(child.cost)     -> EXPRESSION (aggregation formula)
```

#### (B) Extract multiplicities

Finds array sizes on child PartUsages:

```
 pv_module [20]    -> multiplicity = 20
 inverter [2]      -> multiplicity = 2
 frame [1]         -> (singleton, no multiplicity)
```

#### (C) Build aggregation expressions from EXPRESSION-type redefinitions

When a `:>>` has a `sum()`, it gets decomposed into typed terms:

```
 :>> capital_cost = sum(pv_module.cost, inverter.cost) + frame.cost

 Decomposed into:
   SumTerm:       module_count * pv_module.cost     (array child, multiplied)
   SumTerm:       inverter_count * inverter.cost    (array child, multiplied)
   SingletonTerm: frame.cost                        (no multiplicity)
   LocalTerm:     module_count                      (becomes an entry point)
   LocalTerm:     inverter_count                    (becomes an entry point)
```

The `sum()` -> parametric multiply transformation is the key insight:
`sum(pv_module.cost)` over 20 identical modules becomes `20 * pv_module.cost`.

#### (D) Rewrite virtual CalcUsage bindings with design overrides

After extracting the hierarchy metadata, this step mutates virtual CalcUsage bindings
in-place using LITERAL `:>>` overrides:

```
 BEFORE rewrite:
   Virtual CalcUsage: pv_module__cost_model
     binding: wattage -> (UNBOUND)

 Design has: :>> wattage = 400 (on pv_module path)

 AFTER rewrite:
   Virtual CalcUsage: pv_module__cost_model
     binding: wattage -> (LITERAL, value=400)
```

After this step, the virtual CalcUsage looks as if `wattage = 400` was written
directly in the calc usage. The rest of the pipeline never knows it was a `:>>` override.

### Step 3.6: Alias Enrichment

**Question answered:** "When a CalcUsage binding creates an implicit alias, does the aggregation system know about it?"

Scans CalcUsage bindings for parameters whose names differ from the aggregation attributes
they reference. For example, if a CalcUsage binds `total_capex` to `capital_cost`,
that creates an alias: `total_capex` -> `capital_cost`.

These aliases are added to `AggregationExpressionData` so that downstream modules
can wire to aggregation outputs using either name.

### Step 3.5-3.6 output

- `HierarchyExtractionResult` with redefinitions, multiplicities, aggregation expressions
- CalcUsage bindings mutated in-place (LITERAL overrides applied)
- Aliases added to aggregation data

---

## 5. Steps 4-4.7: Design Attributes and Computed Attributes {#5-steps-4-47-attributes}

### Step 4: Extract Design Attributes

**Question answered:** "What literal parameter values does the design file specify?"

Scans all `AttributeUsage` elements with values. Produces `DesignAttributeData`:
- `name`, `qualified_name`, `default_value`, `parent_part`, `sysml_type`

These are the "user-editable knobs" -- parameter values like `efficiency = 0.92`.

### Step 4.5: Extract and Classify Computed Attributes

**Question answered:** "Which attributes are formulas (need pipeline modules) vs. aliases (just rename a channel)?"

Uses a 5-way classification:

```
 attribute p_net_kw = p_net_mw * 1000.0         -> FORMULA
   "Arithmetic on sibling attributes. Gets its own pipeline module."

 attribute total_capex = component_cost.total    -> EXPOSE_PURE
   "Just an alias for a CalcUsage output. No module; becomes a channel rename."

 attribute adjusted = component_cost.total * 1.1 -> EXPOSE_COMPUTED
   "CalcUsage output + arithmetic. Deferred (not yet implemented)."

 attribute name = "solar plant"                  -> LITERAL
   "No computation. Stays in design_attrs."

 attribute unknown = ??? -> UNRESOLVABLE
   "Can't figure this out. Warning + skip."
```

**Critical side effect:** FORMULA attributes are REMOVED from `design_attrs` after
extraction. This prevents them from showing up as false entry points later --
a FORMULA attribute's value comes from its expression, not from user input.

### Step 4.7: Scope Aggregation Expressions

**Question answered:** "Each PartDef can have aggregation expressions, but which design instance(s) do they apply to?"

Maps each PartDef-level `AggregationExpressionData` to one or more concrete design
instance paths by matching against virtual CalcUsage parent paths:

```
 PartDef "Solar_Array" has aggregation for capital_cost
 Virtual CalcUsages show solar_array is at path: solar_battery_plant.solar_array

 Result: ScopedAggregationData
   module_eqn = "solar_battery_plant__solar_array__capital_cost"
```

This `module_eqn` becomes the aggregation module's name in Step 7.

### Steps 4-4.7 output

- `DesignAttributeData` dict (with FORMULAs removed)
- `ComputedAttributeData` list (classified)
- `ScopedAggregationData` list (aggregation expressions mapped to design instances)

---

## 6. Steps 5-6: Analysis -- Backtracking and Parameter Groups {#6-steps-5-6-analysis}

### Step 5: Build ParameterGroupDeriver

Pre-indexes all design attributes, bindings, and unbound params for fast lookup.
Used in Step 7 to classify entry points into groups for JSON input files.

### Step 6: Dependency Backtracking (THE CORE ALGORITHM)

**Question answered:** "For every input on every CalcUsage, does the value come from an upstream module or from the user?"

This is the heart of the pipeline. The `DependencyBacktracker` does a DFS trace
across all CalcUsages and resolves every binding to one of two outcomes:

```
 For each CalcUsage:
   For each input binding:
     Resolve to exactly ONE of:
       MODULE_OUTPUT  -> "this value comes from upstream module X, channel Y"
       ENTRY_POINT    -> "this value comes from the user (via JSON input)"
```

Results are stored in a dict keyed by `"{usage_qn}|{param_name}"`.

#### How LITERAL and UNBOUND bindings resolve

These are simple:

- **LITERAL** (`p_recirculating = 50.0`) -> Always `ENTRY_POINT`. The literal value becomes the default.
- **UNBOUND** (parameter not mentioned) -> Always `ENTRY_POINT`. The CalcDef default (if any) becomes the default.

#### How CHAIN and REFERENCE bindings resolve (the strategy cascade)

CHAIN and REFERENCE bindings are where the complexity lives. The backtracker tries a
cascade of strategies **in order**, stopping at the first match:

```
 Input binding: p_fusion = alpha_split.p_alpha
                                |
                                v
 +------------------------------------------------------+
 | Strategy 0: Computed attribute output?                |
 | Check _computed_attr_index for FORMULA module outputs |
 +------------------------------------------------------+
                |  miss
                v
 +------------------------------------------------------+
 | Strategy 0b: Aggregation module output?               |
 | Check _aggregation_output_index (+ aliases)           |
 +------------------------------------------------------+
                |  miss
                v
 +------------------------------------------------------+
 | Strategy 1: Exact output catalog match                |
 | Check _output_catalog for "alpha_split.p_alpha"       |
 | This is the HAPPY PATH for most CHAIN bindings        |
 +------------------------------------------------------+
                |  miss
                v
 +------------------------------------------------------+
 | Strategy 2: Direct instance name match                |
 | Look up CalcUsage by instance_name "alpha_split"      |
 | Check if "p_alpha" is one of its CalcDef outputs      |
 +------------------------------------------------------+
                |  miss
                v
 +------------------------------------------------------+
 | Strategy 3: Transitive design attribute resolution    |
 | Maybe "alpha_split.p_alpha" is a design attribute     |
 | that itself points to a CalcUsage output              |
 +------------------------------------------------------+
                |  miss
                v
 +------------------------------------------------------+
 | Strategy 4: Cross-file bare attribute match           |
 | Search design_attrs by bare name across all files     |
 +------------------------------------------------------+
                |  miss
                v
 +------------------------------------------------------+
 | Strategy 5: Bare instance name lookup                 |
 | Just the first segment as a CalcUsage name            |
 +------------------------------------------------------+
                |  miss
                v
 +------------------------------------------------------+
 | Strategy 6: Normalize :: qualified names and retry    |
 | Convert SysML :: format to __ format                  |
 +------------------------------------------------------+
                |  miss
                v
 +------------------------------------------------------+
 | Fallback: Create ENTRY_POINT                          |
 | "We don't know where this comes from.                 |
 |  The user will need to supply it."                    |
 +------------------------------------------------------+
```

#### The guarantee

> After backtracking, **every** input on **every** CalcUsage has exactly one
> `BindingResolution` stored in `binding_resolutions["{usage_qn}|{param_name}"]`.
> Each resolution is either `ENTRY_POINT` or `MODULE_OUTPUT`.
> There are no unresolved bindings. If the cascade can't figure it out,
> the fallback conservatively creates an `ENTRY_POINT`.

#### Entry point classification (happens later in Step 7, but derives from Step 6)

When a binding resolves to `ENTRY_POINT`, Step 7 classifies it into one of three types:

```
 Entry point qualified name
              |
    Does it match a DesignAttributeData?
           /             \
         yes              no
          |                |
   DESIGN_ATTRIBUTE   Is it an unbound param with a CalcDef default?
                           /          \
                         yes            no
                          |              |
                   LIBRARY_DEFAULT   USAGE_LITERAL
```

| Type | Source of Default Value | Example |
|---|---|---|
| `DESIGN_ATTRIBUTE` | Design file literal | `efficiency = 0.92` in design |
| `LIBRARY_DEFAULT` | CalcDef input default | `input eta = 0.9` in library |
| `USAGE_LITERAL` | Literal binding in CalcUsage | `eta = 0.8` in usage |

Entry points are grouped by source file into `ParameterGroup` objects.
Each group becomes one JSON input file + one Pydantic schema.

### Step 6 output

- `BacktrackingResult` with `binding_resolutions` (the authoritative wiring map)
- `required_usages` (topologically sorted)
- `entry_points` (set of qualified names)

---

## 7. Step 6.5: Expression Compilation {#7-step-65-compilation}

**Question answered:** "Can we auto-generate the Python implementation, or does a human need to write it?"

For each CalcDef with output expression ASTs, the compiler walks the SysIDE AST tree
and converts it to a Python expression string:

```
 SysML AST tree
     |
     v
 reconstruct_expression()
     |  Dispatches on node type:
     |    OperatorExpression            -> "left op right"
     |    LiteralInteger / LiteralReal  -> "42" / "3.14"
     |    FeatureReferenceExpression    -> "param_name"
     |    FeatureChainExpression        -> "obj.attr"
     |    InvocationExpression          -> "func(args)"
     v
 Python expression string: "p_fusion * eta_gross - p_recirculating"
     |
     v
 Compilability verdict:
     FULLY_COMPILABLE     -> auto-implement (no human needed)
     PARTIALLY_COMPILABLE -> some outputs auto, some manual
     MANUAL_REQUIRED      -> human writes the _impl.py
     UNKNOWN              -> no AST available
```

### The AST type dispatch gotcha

A critical lesson learned (BF-1, BF-2, commit 3318da7): in SysIDE's AST,
`FeatureReferenceExpression` and `FeatureChainExpression` **both** have a `function`
attribute. This means `hasattr(node, "function")` matches ALL THREE types:

```
 hasattr(node, "function") is True for:
   InvocationExpression        function.name = "some_func"
   FeatureReferenceExpression  function.name = "Evaluation"  <-- SURPRISE
   FeatureChainExpression      function.name = "."           <-- SURPRISE
```

The fix: always check specific types BEFORE generic attribute checks:

```python
 # CORRECT order:
 if is_instance(node, "FeatureReferenceExpression"):  # specific first
     ...
 elif is_instance(node, "FeatureChainExpression"):     # specific second
     ...
 elif hasattr(node, "function"):                       # generic last
     ...
```

Any new code that walks SysIDE ASTs **must** follow this pattern.

### Step 6.5 output

- `dict[str, CalcDefCompilationResult]` mapping CalcDef names to compilation results

---

## 8. Step 7: Build the Computation Graph (THE SINGLE SOURCE OF TRUTH) {#8-step-7-graph}

**Question answered:** "What is the complete, validated pipeline structure?"

`build_computation_graph()` is the **funnel**. It takes ALL prior results and
produces the single `ComputationGraph` that generation reads from.

```
 INPUTS (everything from steps 1-6.5):         OUTPUT (one structure):

 CalcDefs                 \                     ComputationGraph
 CalcUsages                \                      .modules[]
 DesignAttrs                \                     .entry_point_groups[]
 ComputedAttrs               +-->                 .execution_order[]
 ScopedAggregationData      /
 BacktrackingResult        /
 CompilationResults       /
```

Nothing downstream of `ComputationGraph` looks at raw extraction data.
This is the **single source of truth** contract (ADR-003).

### What Step 7 builds: the three module families

Step 7 creates `PipelineModule` objects from three different sources:

```
 +===========================================================================+
 |                        ComputationGraph.modules                           |
 |                                                                           |
 |  Family 1: CalcUsage Modules                     (from Step 3/6)         |
 |  +-------------------------------+                                        |
 |  | Source: CalcDef + CalcUsage   |  "A SysML calculation instantiated    |
 |  | Built by: main loop over     |   in the design"                       |
 |  |   BacktrackingResult         |                                        |
 |  | Example: net_electric_power   |                                        |
 |  +-------------------------------+                                        |
 |                                                                           |
 |  Family 2: Computed Attribute Modules             (from Step 4.5)        |
 |  +-------------------------------+                                        |
 |  | Source: FORMULA-classified    |  "A formula attribute like             |
 |  |   ComputedAttributeData      |   p_net_kw = p_net_mw * 1000"         |
 |  | Flag: is_computed_attribute   |                                        |
 |  +-------------------------------+                                        |
 |                                                                           |
 |  Family 3: Aggregation Modules                    (from Step 4.7)        |
 |  +-------------------------------+                                        |
 |  | Source: ScopedAggregationData |  "An assembly cost rollup like         |
 |  |   with SumTerms/Singletons   |   capital_cost = sum(child.cost)"     |
 |  | Flag: is_aggregation          |                                        |
 |  +-------------------------------+                                        |
 +===========================================================================+
```

### How modules get wired (the PipelineModule structure)

Each `PipelineModule` has inputs and outputs:

```
 PipelineModule: "net_electric_power"
   inputs:
     p_fusion:
       source_type: "module_output"
       producer_channel: "...alpha_split__p_alpha"    <-- from binding_resolutions
     p_recirculating:
       source_type: "entry_point"
       param_group: "catf_physics"
       qualified_name: "...net_electric__p_recirculating"
   outputs:
     p_net:
       channel_name: "...net_electric__p_net"         <-- globally unique PQN
```

For CalcUsage modules, the wiring comes directly from `binding_resolutions` (the
backtracker output). This is **not re-derived** -- the graph builder uses the
backtracker's decision as the single source of truth.

### The fail-fast contract

```python
 resolution = binding_resolutions.get(mapping_key)
 if resolution is None:
     raise ValueError(f"ADR-003 VIOLATION: no resolution for {mapping_key}")
```

If the backtracker missed a binding, the graph builder **crashes** instead of
silently generating broken code. Better to fail loudly during codegen than to
produce a pipeline that fails at runtime.

### How the three families wire together

```
 [JSON Inputs]
      |
      v  (entry_point)                   Family 1: CalcUsage Module
 [pv_module__cost_model]  -------.
      |                           |
      | output: total_cost        |
      v  (module_output)          |      Family 3: Aggregation Module
 [solar_array__capital_cost]      |
      |                           |
      | output: capital_cost      |
      v  (module_output)          |      Family 3: Aggregation (higher level)
 [solar_battery_plant__capital_cost]
      |                           |
      | output: capital_cost      |
      v  (module_output, via alias)      Family 1: CalcUsage Module
 [annualized_financial]           |
      |                           |
      | output: lcoe              |      Family 2: Computed Attribute Module
      v                           '--->[p_net_kw] (p_net_mw * 1000)
 [Pipeline Exit]
```

### Sub-steps within Step 7

1. **Build output catalog** -- maps `"instance.output"` to `(module_type, channel_name)`
2. **Extend catalog** with computed attribute and aggregation outputs
3. **Classify entry points** into the 3 types (see [Section 6](#6-steps-5-6-analysis))
4. **Build CalcUsage modules** (Family 1) from `binding_resolutions`
5. **Build computed attribute modules** (Family 2) for FORMULA-classified attrs
6. **Build aggregation modules** (Family 3) from `ScopedAggregationData`
7. **Rebuild param groups** to capture entry points added by sub-steps 5-6
8. **Collect orphan entry points** not in any group -> "system_design" group
9. **Unified topological sort** across ALL module families
10. **Validate channel references** -- early check before generation

### Step 7 output

- `ComputationGraph` with `modules`, `entry_point_groups`, `execution_order`

---

## 9. Generation: Templates Produce the Output Package {#9-generation}

Generation is straightforward: Jinja2 templates iterate over `ComputationGraph` fields.

| Template | Reads | Produces |
|----------|-------|----------|
| `teax_module.py.jinja2` | `PipelineModule` inputs/outputs | TEAx module wrapper class |
| `auto_implementation.py.jinja2` | `compiled_expression` | Auto-generated `_impl.py` |
| `implementation_stencil.py.jinja2` | `PipelineModule` signature | `NotImplementedError` stub |
| `pipeline_yaml.jinja2` | All modules + execution_order | Pipeline YAML (the DAG) |
| `parameter_group_schema.py.jinja2` | `ParameterGroup` | Pydantic schema + JSON template |
| `registry_function.py.jinja2` | All module types | `__init__.py` registry |

### Pipeline YAML wiring format

In the generated YAML, input sources are formatted as:
- Entry point: `group.qualified_name` (e.g., `catf_physics.p_recirculating`)
- Module output (single): `channel.root` (e.g., `alpha_split__p_alpha.root`)
- Module output (multi): `channel` (e.g., `alpha_split__p_alpha`)

### Smart regeneration (preservation.py)

When re-running codegen, the preservation system:
1. Detects if an existing `_impl.py` is a stub (`raise NotImplementedError`)
2. If the CalcDef is now `FULLY_COMPILABLE`, upgrades the stub to an auto-impl
3. If the user has modified the file, leaves it alone (signature hash comparison)

---

## 10. Cross-Cutting: The Naming System (Global Uniqueness Guarantee) {#10-naming-system}

The naming system (ADR-003) is referenced throughout the pipeline. Every module and
channel has a **globally unique** name derived from its position in the SysML hierarchy.

### The naming hierarchy

```
 SysML Qualified Name (raw):    FusionPhysics::AlphaNeutronSplit
                                     |
                                     v  (converted at extraction, :: -> __)
 Element Qualified Name (EQN):  CATFMFEPhysics__catf_physics__alpha_split
                                     |
          +--------------------------+----------------------------+
          |                          |                            |
          v                          v                            v
 Module Name:               Channel Name (PQN):          Module Type:
 catfmfephysics__           catfmfephysics__              fusionphysics.
 catf_physics__             catf_physics__                AlphaNeutronSplit
 alpha_split                alpha_split__p_alpha          Module
 (lowercase EQN)            (EQN + "__" + output)        (namespace.ClassModule)
```

### Uniqueness guarantees

| Property | Guarantee | How |
|---|---|---|
| **Module names are unique** | No two modules share a name | EQN encodes full hierarchy path |
| **Channel names are unique** | No two outputs share a channel | PQN = EQN + output name |
| **Channels can always be found** | Given a channel name, find the producer | Output catalog is built from PQNs |
| **No collisions across files** | Modules from different SysML files don't clash | Package prefix is part of EQN |

### The `__` separator convention

All internal names use `__` (double underscore). SysML uses `::` but we convert
at extraction time and **never convert back**. Given an EQN:
- Lowercase it -> module name
- Append `__output_name` -> channel name (PQN)
- Split on `__` -> hierarchy segments

### Hierarchy naming example

```
 PartDef: Solar_Array (template)
   CalcUsage: cost_model

 PartUsage in design: solar_battery_plant.solar_array.pv_module

 Virtual CalcUsage EQN:
   SolarBatteryDesign__solar_battery_plant__solar_array__pv_module__cost_model
   ^^^^^^^^^^^^^^^^   ^^^^^^^^^^^^^^^^^^^^  ^^^^^^^^^^^  ^^^^^^^^^  ^^^^^^^^^^
   design part        level 1              level 2      level 3    calc usage

 Module name: solarbatterydesign__solar_battery_plant__solar_array__pv_module__cost_model
 Channel:     ...pv_module__cost_model__total_cost
```

Two `cost_model` usages on different PartUsages get different EQNs.
You can always trace back from an EQN to the exact location in the model.

---

## 11. Known Fragilities and Open Issues {#11-known-fragilities}

### Currently open bug

**Bug 2: EXPOSE_PURE two-hop transitive resolution**
(`.project/research/20260213-152845_bug2-expose-calcusage-wiring-persistent-failure.md`)

```
 total_capex (EXPOSE_PURE alias for capital_cost)
     |
     v  Strategy 4 resolves hop 1: total_capex -> capital_cost (bare name)
     |
     v  Hop 2 needs to find: component_cost.total_cost (CalcUsage output)
     |
     X  FAILS: bare "capital_cost" doesn't match EQN-format index keys
```

The backtracker resolves the first hop but can't resolve the second because
the index keys use EQN format and the bare name doesn't match.

### Architectural fragilities

1. **Strategy cascade silent fallback.** If no strategy matches a CHAIN/REFERENCE binding,
   it silently becomes an entry point. There's no warning that resolution "gave up."
   A binding that *should* be MODULE_OUTPUT appears as ENTRY_POINT with no diagnostic.

2. **In-place mutation in Step 3.5.** Virtual binding rewrite mutates CalcUsage objects
   in-place. The CalcUsage list is different after Step 3.5 than after Step 3.
   Any code that caches CalcUsage state before Step 3.5 will be stale.

3. **AST type dispatch is fragile.** SysIDE AST nodes have unexpected properties
   (FeatureRef and FeatureChain both have `function`). Any new AST-walking code that
   does `hasattr(node, "function")` will hit the same bug. The fix is always:
   check specific `is_instance()` types before generic attribute presence.

4. **Aggregation scoping heuristics.** Step 4.7 matches PartDef aggregations to
   design instances using name-based and structural strategies. All-singleton assemblies
   required a special Strategy 3 (child-walk matching). New assembly patterns may
   need new strategies.

5. **Alias enrichment is post-hoc.** Aliases (Step 3.6) are discovered after hierarchy
   extraction. If aggregation resolution in Step 3.5 itself needs aliases, they
   won't be available yet.

### What "healthy" looks like

If the pipeline is working correctly:
- `IMPLEMENTATION_BACKLOG.md` shows "0 functions to implement"
- All generated `_impl.py` files pass `ast.parse()` (valid Python)
- Pipeline YAML has no entry points for values that should be module outputs
- Every module's inputs trace back to either a JSON entry point or an upstream output

---

## Appendix A: Complete Step Index

| Step | Function | Source File | Input | Output |
|------|----------|-------------|-------|--------|
| 1 | `SysMLDataExtractor.load_models()` | extraction/extractor.py | .sysml files | In-memory AST |
| 2 | `extract_calculation_definitions()` | extraction/extractor.py | AST | list[CalculationDefinitionData] |
| 3 | `extract_calculation_usages()` | extraction/usage_extractor.py | AST + CalcDefs | list[CalcUsageData] |
| 3.5 | `_extract_hierarchy_and_rewrite_bindings()` | generation/initialization.py | AST + CalcUsages | HierarchyExtractionResult |
| 3.6 | `_enrich_aliases_from_bindings()` | generation/initialization.py | HierarchyData + CalcUsages | (mutates aliases) |
| 4 | `extract_design_attributes()` | analysis/parameter_groups.py | AST | dict[Path, list[DesignAttributeData]] |
| 4.5 | `_extract_and_filter_computed_attributes()` | generation/initialization.py | AST + CalcUsages + DesignAttrs | list[ComputedAttributeData] |
| 4.7 | `_scope_aggregation_expressions()` | generation/initialization.py | HierarchyData + CalcUsages | list[ScopedAggregationData] |
| 5 | `ParameterGroupDeriver()` | analysis/parameter_groups.py | DesignAttrs + CalcUsages + CalcDefs | Grouping indexes |
| 6 | `DependencyBacktracker.find_required_modules()` | analysis/dependency_backtracker.py | All of the above | BacktrackingResult |
| 6.5 | `compile_calc_def()` | extraction/expression_compiler.py | CalcDef ASTs | dict[str, CalcDefCompilationResult] |
| 7 | `build_computation_graph()` | resolution/graph_builder.py | BacktrackingResult + everything | ComputationGraph |

## Appendix B: File Map

```
src/sysml_codegen/
  core/
    models.py               BindingResolution, BindingResolutionType
    qualified_names.py       EQN/PQN/module name functions (Section 10)
    identifier_types.py      SysMLQualifiedName, PythonModulePath, ModuleType
  extraction/
    extractor.py             Steps 1-2: SysMLDataExtractor, CalcDefs
    usage_extractor.py       Step 3: CalcUsages, template detection, virtual expansion
    hierarchy_resolver.py    Step 3.5: redefinitions, multiplicities, aggregation
    computed_attribute_extractor.py   Step 4.5: 5-way classification
    expression_compiler.py   Step 6.5: compile_calc_def(), Compilability
    expression_utils.py      Step 6.5: reconstruct_expression(), AST walking
    data_models.py           Shared data models (AttributeInfo, etc.)
  analysis/
    dependency_backtracker.py  Step 6: 7-strategy resolution cascade
    parameter_groups.py        Steps 4-5: design attrs, ParameterGroupDeriver
  resolution/
    graph_builder.py         Step 7: build_computation_graph(), THE funnel
    models.py                PipelineModule, ModuleInput, ModuleOutput, ComputationGraph
  generation/
    initialization.py        build_pipeline_context(): Steps 1-7 orchestration
    pipeline.py              Generation: Pipeline YAML
    modules.py               Generation: TEAx module wrappers
    stencils.py              Generation: Implementation stencils
    entry_point.py           Generation: Parameter group schemas + JSON
    registry.py              Generation: __init__.py registry
    preservation.py          Generation: Smart-regen (stub -> auto-impl upgrade)
  cli/
    __init__.py              run_codegen(): all _generate_*() functions
  templates/
    *.jinja2                 All Jinja2 templates
```
