# 08: Desired-State Algorithm Design

**Date:** 2026-02-13
**Purpose:** How the codegen pipeline SHOULD work. Each section describes the
target architecture, with `DELTA` callouts where it differs from the current
implementation. See `07_open_issues.md` for precise current-state problems.

**Reading guide:** Sections 3-9 follow the pipeline in order, top-to-bottom.
Section 10 (naming) is a cross-cutting concern referenced throughout.
Section 11 (Output Registry) is the central architectural change.

---

## Table of Contents

1. [The Big Picture](#1-the-big-picture)
2. [Pipeline Overview Diagram](#2-pipeline-overview-diagram)
3. [Steps 1-3: Extraction](#3-steps-1-3-extraction)
4. [Step 3.5: Hierarchy Processing](#4-step-35-hierarchy)
5. [Steps 4-4.5: Design Attributes and Computed Attributes](#5-steps-4-45-attributes)
6. [Step 5: Build the Output Registry](#6-step-5-output-registry)
7. [Step 6: Dependency Backtracking](#7-step-6-backtracking)
8. [Step 6.5: Expression Compilation](#8-step-65-compilation)
9. [Step 7: Build the Computation Graph](#9-step-7-graph)
10. [Generation](#10-generation)
11. [Cross-Cutting: The Naming System](#11-naming-system)
12. [Cross-Cutting: The Output Registry](#12-output-registry)
13. [Cross-Cutting: AST Dispatch Rules](#13-ast-dispatch)

---

## 1. The Big Picture

sysml-codegen reads SysML v2 model files and produces a complete, runnable Python pipeline.
The pipeline is a DAG (directed acyclic graph) of calculation modules wired together
by named channels.

**The core question the pipeline answers:**

> For every calculation input, where does its value come from?
> Either (a) it's an **entry point** (user provides it), or
> (b) it's a **module output** from an upstream calculation.

That's it. The entire pipeline is about answering that question for every input
on every calculation, then generating code that wires them together.

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

---

## 2. Pipeline Overview Diagram

```
 SysML Files
     |
     |  Step 1: Load Models                                   -.
     |  Step 2: Extract CalcDefs                               |  --> Section 3
     |  Step 3: Extract CalcUsages (+ template expansion)     -'
     v
 CalcDefs + CalcUsages (with bindings)
     |
     |  Step 3.5: Hierarchy extraction & override application     --> Section 4
     v
 + HierarchyExtractionResult + ChannelAliases
     |
     |  Step 4:   Extract design attributes                   -.
     |  Step 4.5: Extract & classify computed attributes       -'  --> Section 5
     v
 + DesignAttrs + ComputedAttrs (producing more ChannelAliases)
     |
     |  Step 5: Build OutputRegistry (SINGLE LOOKUP)              --> Section 6
     v
 OutputRegistry (every output channel, every alias, one index)
     |
     |  Step 6: Dependency backtracking                           --> Section 7
     v
 BacktrackingResult (binding_resolutions for EVERY input)
     |
     |  Step 6.5: Expression compilation                          --> Section 8
     v
 + CalcDefCompilationResults
     |
     |  Step 7: Build ComputationGraph                            --> Section 9
     v
 ComputationGraph (modules + entry_point_groups + execution_order)
     |
     |  Generation: Jinja2 templates                              --> Section 10
     v
 Generated Python Package
```

> **DELTA vs. current:** Steps 3.6, 4.7 are eliminated as separate steps.
> Alias enrichment (was 3.6) is replaced by explicit `ChannelAlias` production
> in Steps 3.5 and 4.5. Aggregation scoping (was 4.7) moves into Step 3.5
> (producing `ScopedAggregationData`); Step 5 only registers the results.
> The OutputRegistry (Step 5) replaces the five ad-hoc indexes currently built
> inside the backtracker constructor. Registry uses a 4-phase registration
> protocol and resolves via **exact match only** (no bare names, no SYSML_QN
> normalization -- Spike 5 showed `::` -> `__` normalization is broken).
> REFERENCE bindings that target computed attributes are resolved by the
> backtracker's secondary resolution path, not by the OutputRegistry directly.

---

## 3. Steps 1-3: Extraction -- What Exists in the Model? {#3-steps-1-3-extraction}

### Step 1: Load Models

Parse `.sysml` files via the SysIDE adapter into an in-memory AST. Just I/O.

### Step 2: Extract Calculation Definitions (CalcDefs)

**Question answered:** "What formulas exist in the library?"

Each `CalculationDefinitionData` has:
- `name`, `qualified_name` (SysML `::` format -- raw from parser, not yet converted)
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
- `qualified_name` (globally unique EQN -- see [Section 11](#11-naming-system))
- `bindings` (list of `BindingInfo` -- the wiring)
- `unbound_params` (inputs with no binding)

#### The four kinds of bindings

When a CalcUsage instantiates a CalcDef, each input parameter is bound in one of
four ways:

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

**Important (empirically verified -- Spike 1):** The `source_path` on each binding
arrives in exactly one of two formats depending on binding type:
- CHAIN: dotted path (`"alpha_split.p_alpha"`)
- REFERENCE: SysML qualified name (`"FusionPhysics::GrossEfficiency::eta_gross"`)
- LITERAL/UNBOUND: no source_path

Bare names were **never observed** (94 bindings, 3 models, all confirmed DOTTED or
SYSML_QN). These source_path formats are **not normalized at extraction time**. They
stay in their original format. The OutputRegistry (Step 5) resolves DOTTED via exact
match. SYSML_QN source_paths are handled by the backtracker's secondary resolution
path (leaf-name extraction + parent-scoped lookup). See [Section 7](#7-step-6-backtracking)
and [Section 12](#12-output-registry).

#### Template detection (COST-PATTERN)

Step 3 also detects CalcUsages that live on **PartDefinitions** (templates) rather
than **PartUsages** (concrete design instances):

```
 For each CalcUsage found:
   Is its owning_type a PartDefinition?
     YES -> flag is_template=True, record owning_part_def_qn
     NO  -> normal CalcUsage (keep as-is)
```

Template CalcUsages get **virtually expanded**: one copy per design instance that
uses that PartDefinition:

```
 Template: cost_model on PartDef Solar_Array
 Design instances of Solar_Array: [pv_module, inverter, frame]

 Virtual expansion:
   solar_battery_plant__solar_array__pv_module__cost_model
   solar_battery_plant__solar_array__inverter__cost_model
   solar_battery_plant__solar_array__frame__cost_model
```

Each virtual CalcUsage gets a hierarchy-scoped EQN (see [Section 11](#11-naming-system))
and inherits the template's bindings. Those bindings get rewritten in Step 3.5.

### Step 3 output

A flat list of CalcUsages -- both "real" ones from the design and "virtual" ones
from template expansion. The rest of the pipeline treats them identically.

---

## 4. Step 3.5: Hierarchy Processing {#4-step-35-hierarchy}

**Question answered:** "How does the design hierarchy customize template parameters, create aliases, and define cost rollups?"

This step extracts metadata from the part hierarchy and applies overrides to
virtual CalcUsage bindings.

### (A) Extract `:>>` redefinitions

Scans PartDefinition members for `:>>` (redefine) statements. Each is classified
by its RHS:

```
 :>> wattage = 400              -> LITERAL    (direct value override)
 :>> capital_cost = cost.total  -> CHAIN      (alias to another attribute)
 :>> cost = sum(child.cost)     -> EXPRESSION (aggregation formula)
```

### (B) Extract multiplicities

Finds array sizes on child PartUsages:

```
 pv_module [20]    -> MultiplicityData(count=20, count_attribute_name="module_count")
 inverter [2]      -> MultiplicityData(count=2, count_attribute_name="inverter_count")
 frame [1]         -> (singleton, no multiplicity extracted)
```

### (C) Build aggregation expressions from EXPRESSION-type redefinitions

When a `:>>` has an aggregation function call, it gets decomposed into typed terms.

> **DELTA vs. current:** The current code only handles `sum()`. The target
> design keeps direct `sum()` handling code -- no Protocol/registry abstraction.
> Per project guidelines: "Don't create abstractions for one-time operations."
> There is exactly one aggregation function. Add the registry later if a second
> decomposer is needed.

```python
# Direct sum() handling (no Protocol):
def decompose_sum_aggregation(
    operands: list[AST],
    mult_lookup: dict[str, MultiplicityData],
) -> DecompositionResult:
    """Decompose sum(child.attr, ...) into parametric multiply terms.

    Precondition (uniform-array assumption): All instances in a PartUsage
    array are identical. sum(child.attr) becomes count * child.attr.
    This assumption is documented here, not buried in an ADR.
    """
    ...

@dataclass
class DecompositionResult:
    sum_terms: list[SumTerm]
    singleton_terms: list[SingletonTerm]
    local_terms: list[LocalTerm]
    transformed_expression: str
    has_unsupported_nodes: bool
```

The aggregation walker:

```python
if func_name == "sum":
    result = decompose_sum_aggregation(operands, mult_lookup)
elif func_name in _KNOWN_WRAPPER_FUNCTIONS:
    # unwrap Evaluation/collect/select wrappers
else:
    ctx.has_unsupported = True
    logger.warning("Unknown aggregation function '%s' -- marking unsupported", func_name)
```

**Validation rule:** `decompose_sum_aggregation()` MUST verify that each operand
is a `FeatureChainExpression` referencing a child part attribute (i.e., the first
segment of the dotted path matches a child PartUsage name). If the operand
is a bare name or a non-child reference, it should be classified as a
`LocalTerm` or flagged as unsupported -- not silently treated as a `SumTerm`.

> **NOTE:** `sum()` in a `:>>` EXPRESSION on a PartDefinition goes through this
> aggregation decomposer. `sum()` inside a CalcDef expression body goes through
> the expression compiler (Step 6.5) which reconstructs it as literal Python
> `sum(...)` with no multiplicity awareness. These are two distinct code paths
> and the distinction is: `:>>` redefinitions are assembly-level rollups with
> hierarchy semantics. CalcDef expressions are formula-level math.

### (D) Extract `:>>` CHAIN aliases

`:>>` CHAIN redefinitions create named aliases for attributes:

```
 :>> total_capex = cost_model.total_cost

 This means: "total_capex" aliases "cost_model.total_cost" on this PartDef.
```

> **Empirically verified (Spike 6):** CHAIN redefinition source_paths come in
> exactly two formats:
> - **DOTTED (76%):** PartDef-local paths like `cost_model.total_cost`
> - **BARE (24%):** CAS category codes like `CAS220101` -- string literal values,
>   NOT channel references. These are filtered out before alias construction.
>
> `expression_text` is empty and `expression_ast` is None for all CHAIN redefs.
> `source_path` is the only reliable field.

These produce `ChannelAlias` objects, but only for DOTTED source_paths:

```python
@dataclass
class ChannelAlias:
    """An explicit alias for a pipeline output channel."""
    alias_name: str          # "solar_array.total_capex" (scoped)
    canonical_name: str      # "solar_array.cost_model.total_cost" (scoped)
    owning_part_qn: str      # PartDef where the :>> lives
    source: str              # "redefinition" | "expose_pure" | "design_override"

# Construction at Step 3.5(D):
for redef in chain_redefinitions:
    # Filter: skip BARE non-reference values (CAS codes, enums, etc.)
    if "." not in redef.source_path:
        continue

    # Scope with design instance path (available from aggregation scoping)
    ChannelAlias(
        alias_name=f"{instance_path}.{redef.attribute_name}",
        canonical_name=f"{instance_path}.{redef.source_path}",
        owning_part_qn=redef.owning_part_qn,
        source="redefinition",
    )
```

> **DELTA vs. current:** Currently, alias detection happens in two places
> (hierarchy extractor and Step 3.6 param_name heuristic). In the target design,
> Step 3.6 is eliminated entirely. Aliases are produced ONLY from authoritative
> sources: `:>>` CHAIN redefinitions (here in Step 3.5) and EXPOSE_PURE
> classification (Step 4.5). The `ChannelAlias` is a first-class data model,
> not a `list[str]` bolted onto `AggregationExpressionData`.

### (E) Apply overrides to virtual CalcUsage bindings

After extracting hierarchy metadata, this step rewrites virtual CalcUsage bindings
using design overrides.

> **Verified (Spike 1):** SysIDE produces exactly two source_path formats:
> - **REFERENCE bindings** (e.g., to sibling PartDef attributes): SYSML_QN format
>   (`SolarBatteryLibrary::'PV Module'::cost_model::wattage`)
> - **CHAIN bindings** (e.g., to CalcUsage outputs): DOTTED format
>   (`annualized_financial.annualized_capital_cost`)
>
> **Bare names were never observed** (94 bindings, 3 models). Template bindings
> use the same SYSML_QN format as concrete bindings. Virtual CalcUsages inherit
> source_path unchanged.

```python
def _rewrite_virtual_bindings(calc_usages, hierarchy_data) -> int:
    """Rewrite virtual CalcUsage bindings using design overrides.

    For each non-template CalcUsage, check each binding against the
    override index. Match by normalizing the binding's source_path
    to a (parent_path, attribute_name) key.
    """
    for usage in calc_usages:
        if usage.is_template:
            continue

        parent_path = usage.qualified_name.rsplit("__", 1)[0]

        for binding in usage.bindings:
            if binding.binding_type == BindingType.LITERAL:
                continue
            if not binding.source_path:
                continue

            # Extract leaf attribute name from source_path.
            # Spike 1 confirmed: REFERENCE bindings use SYSML_QN ("Ns::Part::attr"),
            # CHAIN bindings use DOTTED ("instance.output"). No bare names exist.
            if "::" in binding.source_path:
                attr_name = binding.source_path.rsplit("::", 1)[-1]
            elif "." in binding.source_path:
                attr_name = binding.source_path.rsplit(".", 1)[-1]
            else:
                attr_name = binding.source_path  # defensive fallback

            key = (parent_path, attr_name)
            matched = override_index.get(key)

            if matched is None:
                continue

            if matched.redefinition_type == RedefinitionType.LITERAL:
                binding.binding_type = BindingType.LITERAL
                binding.literal_value = matched.literal_value
                binding.source_path = None
                rewrite_count += 1

            elif matched.redefinition_type == RedefinitionType.CHAIN:
                # CHAIN override: rewrite source_path to point to the override target
                binding.source_path = matched.source_path
                rewrite_count += 1

            # EXPRESSION overrides are aggregation formulas -- don't rewrite
            # the binding; the aggregation module will be created in Step 7.
```

> **DELTA vs. current:** The current code only handles LITERAL overrides and only
> matches bare-name source_paths. The target handles LITERAL and CHAIN overrides,
> and extracts leaf names from SYSML_QN and DOTTED formats.

### Step 3.5 output

- `HierarchyExtractionResult` with redefinitions, multiplicities, aggregation expressions
- `list[ScopedAggregationData]` -- aggregation expressions scoped to design instance paths
  (scoping runs here as sub-step, not deferred to Step 5)
- `list[ChannelAlias]` from `:>>` CHAIN redefinitions
- CalcUsage bindings mutated (LITERAL and CHAIN overrides applied)

---

## 5. Steps 4-4.5: Design Attributes and Computed Attributes {#5-steps-4-45-attributes}

### Step 4: Extract Design Attributes

**Question answered:** "What literal parameter values does the design file specify?"

Scans all `AttributeUsage` elements with values. Produces `DesignAttributeData`:
- `name`, `qualified_name`, `default_value`, `parent_part`, `sysml_type`

These are the "user-editable knobs" -- parameter values like `efficiency = 0.92`.

### Step 4.5: Extract and Classify Computed Attributes

**Question answered:** "Which attributes are formulas (need pipeline modules) vs. aliases (need channel aliases)?"

Uses a 5-way classification:

```
 attribute p_net_kw = p_net_mw * 1000.0         -> FORMULA
   "Arithmetic on sibling attributes. Gets its own pipeline module."

 attribute total_capex = component_cost.total    -> EXPOSE_PURE
   "Alias for a CalcUsage output. Produces a ChannelAlias, NOT a module."

 attribute adjusted = component_cost.total * 1.1 -> EXPOSE_COMPUTED
   "CalcUsage output + arithmetic. Deferred (not yet implemented)."

 attribute name = "solar plant"                  -> LITERAL
   "No computation. Stays in design_attrs."

 attribute unknown = ??? -> UNRESOLVABLE
   "Can't figure this out. Warning + skip."
```

**FORMULA handling:** FORMULA attributes are REMOVED from `design_attrs` after
extraction, preventing false entry points.

**EXPOSE_PURE handling:**

> **DELTA vs. current:** Currently, EXPOSE_PURE attrs are stored in
> `_computed_attr_index` alongside FORMULA attrs, and the backtracker treats them
> identically -- building a channel name for a module that doesn't exist (Bug 2).
>
> In the target design, EXPOSE_PURE attrs produce `ChannelAlias` objects:

```python
for ca in computed_attrs:
    if ca.classification == ComputedAttributeClassification.EXPOSE_PURE:
        # IMPORTANT: Do NOT use ca.expression_text -- SysIDE produces raw AST text
        # like ".(component_cost)" which is not a parseable dotted key.
        # Instead, reconstruct the dotted target from the references field:
        #   references[0].name = "total_cost"     (output attribute)
        #   references[1].name = "component_cost" (CalcUsage instance)
        #
        # Spike 3 confirmed this is the only reliable path.
        if len(ca.references) >= 2:
            instance_name = ca.references[1].name   # CalcUsage instance
            output_name = ca.references[0].name      # output attribute
            canonical_target = f"{instance_name}.{output_name}"
        else:
            logger.warning(
                "EXPOSE_PURE '%s' has %d references (expected >= 2), skipping",
                ca.python_name, len(ca.references),
            )
            continue

        aliases.append(ChannelAlias(
            alias_name=ca.python_name,           # "total_capex"
            canonical_name=canonical_target,      # "component_cost.total_cost"
            owning_part_qn=ca.owning_part_qualified_name,
            source="expose_pure",
        ))
```

EXPOSE_PURE attrs are NOT added to any computed attribute index. They are NOT
available for direct resolution. They exist ONLY as aliases in the OutputRegistry,
which resolves them transitively.

### Steps 4-4.5 output

- `DesignAttributeData` dict (with FORMULAs removed)
- `ComputedAttributeData` list (FORMULA only -- these become modules in Step 7)
- `list[ChannelAlias]` from EXPOSE_PURE classifications (appended to aliases from Step 3.5)

---

## 6. Step 5: Build the Output Registry {#6-step-5-output-registry}

> **DELTA vs. current:** This step does not exist in the current pipeline. Currently,
> the backtracker constructor builds 5 separate indexes with incompatible key formats.
> The OutputRegistry replaces all of them with a single data structure.
> See [Section 12](#12-output-registry) for the full design.

**Question answered:** "Given any source_path from a binding, what channel does it resolve to?"

The OutputRegistry is built from three sources:

```
 Step 3 output (CalcUsages)         -> register CalcUsage output channels
 Step 3.5 output (hierarchy)        -> register aggregation output channels + aliases
 Step 4.5 output (computed attrs)   -> register FORMULA output channels + EXPOSE_PURE aliases
```

After construction, the registry can resolve any **dotted** binding source_path
to a canonical channel name -- or return `None` if the source_path doesn't
match any known output. SYSML_QN source_paths (from REFERENCE bindings) are
handled by the backtracker's secondary resolution path (see Section 7), not
by the OutputRegistry directly.

```python
registry = OutputRegistry()

# ── Phase 1: Register canonical channels ──────────────────────
# All CalcUsage, aggregation, and FORMULA outputs.

# CalcUsage outputs
for usage in calc_usages:
    for output_attr in calc_def.output_attributes:
        channel = get_channel_name(usage.qualified_name, output_attr.name)
        registry.register(channel, [
            f"{usage.instance_name}.{output_attr.name}",  # dotted (short)
            f"{usage.qualified_name}__{output_attr.name}", # EQN (full)
        ])
        # NOTE: No bare-name registration (Spike 4: zero bare-name references).

# Aggregation outputs (scoped to design instances)
for agg in scoped_aggregation_data:
    channel = get_channel_name(agg.module_eqn, agg.expression.attribute_name)
    registry.register(channel, [
        f"{instance_part}.{agg.expression.attribute_name}",         # dotted
        ".".join(instance_parts + [agg.expression.attribute_name]), # full dotted path
    ])
    # NOTE: No bare-name registration.

# FORMULA computed attribute outputs
for ca in computed_attrs_formula_only:
    channel = get_channel_name(module_eqn, ca.python_name)
    registry.register(channel, [
        f"{ca.owning_part_name}.{ca.python_name}",  # dotted
    ])
    # NOTE: No bare-name registration.

# ── Phase 2: Register :>> CHAIN aliases ───────────────────────
# These alias canonical channels from Phase 1.
for alias in chain_aliases:  # filtered from all_channel_aliases where source == "redefinition"
    canonical_channel = registry.resolve(alias.canonical_name)
    if canonical_channel:
        registry.register_alias(alias.alias_name, canonical_channel)
    else:
        logger.warning(
            "CHAIN alias '%s' -> '%s' could not resolve (Phase 2)",
            alias.alias_name, alias.canonical_name,
        )

# ── Phase 3: Register EXPOSE_PURE aliases ────────────────────
# These may alias CHAIN aliases from Phase 2.
# IMPORTANT: canonical_name is built from references field, NOT expression_text.
# (Spike 3: expression_text is ".(component_cost)", not a parseable dotted key.)
# Aliases are registered with SCOPED dotted keys (parent_part.attr_name).
for alias in expose_pure_aliases:  # filtered where source == "expose_pure"
    canonical_channel = registry.resolve(alias.canonical_name)
    if canonical_channel:
        # Register scoped alias: "e2e_plant.total_capex" -> channel
        scoped_alias = f"{alias.owning_part_short_name}.{alias.alias_name}"
        registry.register_alias(scoped_alias, canonical_channel)
    else:
        logger.warning(
            "EXPOSE_PURE alias '%s' -> '%s' could not resolve (Phase 3)",
            alias.alias_name, alias.canonical_name,
        )

# ── Phase 4: Register design-attribute transitive aliases ────
# Design attributes whose default_value is a dotted path pointing to a
# module output. These collapse the two-hop resolution problem.
for attr in design_attrs_with_transitive_defaults:
    canonical_channel = registry.resolve(attr.default_value)
    if canonical_channel:
        registry.register_alias(
            f"{attr.parent_part}.{attr.name}",  # "e2e_plant.total_capex"
            canonical_channel,
        )
```

> **Registration phase contract:** Each phase may only reference names registered in
> prior phases. If a Phase N alias can't resolve, log a warning -- don't silently drop it.
> Phase ordering is: (1) canonical channels, (2) `:>>` CHAIN, (3) EXPOSE_PURE,
> (4) design-attribute transitive. This ordering was empirically validated by Spike 3.

> **NOTE on aggregation scoping:** Scoping logic (mapping PartDef-level aggregation
> expressions to design instance paths, producing `ScopedAggregationData`) runs in
> **Step 3.5** as a sub-step of hierarchy extraction. Step 5 only **registers** the
> already-scoped results into the OutputRegistry. This separation is important because
> scoping depends on hierarchy extraction results, not on the OutputRegistry.
> (Spike 2 confirmed: virtual CalcUsage outputs are consumed via aggregation, not
> CHAIN, so scoping must complete before registration.)

### Step 5 output

- `OutputRegistry` -- the single lookup for CHAIN binding resolution and alias lookups
- `list[ScopedAggregationData]` -- scoped aggregation expressions (for Step 7 module building)

---

## 7. Step 6: Dependency Backtracking {#7-step-6-backtracking}

**Question answered:** "For every input on every CalcUsage, does the value come from an upstream module or from the user?"

The `DependencyBacktracker` does a DFS trace across all CalcUsages and resolves
every binding to one of two outcomes:

```
 For each CalcUsage:
   For each input binding:
     Resolve to exactly ONE of:
       MODULE_OUTPUT  -> "this value comes from upstream module X, channel Y"
       ENTRY_POINT    -> "this value comes from the user (via JSON input)"
```

Results are stored in a dict keyed by `"{usage_qn}|{param_name}"`.

### How LITERAL and UNBOUND bindings resolve

Simple:

- **LITERAL** (`p_recirculating = 50.0`) -> Always `ENTRY_POINT`. Literal value is the default.
- **UNBOUND** (parameter not mentioned) -> Always `ENTRY_POINT`. CalcDef default (if any) is the default.

### How CHAIN bindings resolve

> **DELTA vs. current:** The current code uses a 7-strategy cascade with 12+ lookup
> attempts across 5 indexes. In the target design, CHAIN bindings resolve via
> the OutputRegistry with exact dotted-key match:

```python
# For each CHAIN binding (source_path is always DOTTED, e.g. "alpha_split.p_alpha"):
channel = self._output_registry.resolve(binding.source_path)

if channel is not None:
    self._binding_resolutions[mapping_key] = BindingResolution(
        resolution_type=BindingResolutionType.MODULE_OUTPUT,
        qualified_name=channel,
        source_path=binding.source_path,
    )
else:
    # CHAIN target not found -- likely a design attribute entry point
    design_attr = self._resolve_to_design_attribute(binding.source_path)
    if design_attr:
        # ENTRY_POINT with design attribute default
        ...
    else:
        logger.warning(
            "CHAIN binding '%s' on '%s' could not be resolved. "
            "Treating as entry point.",
            binding.source_path, usage.qualified_name,
        )
        ...
```

### How REFERENCE bindings resolve

> **Empirically verified (Spike 5):** REFERENCE bindings use SYSML_QN source_paths
> (e.g., `SolarBatteryLibrary::'PV Module'::cost_model::wattage`). 119/123
> resolve to ENTRY_POINT. 4/123 resolve to MODULE_OUTPUT (all computed attributes).
>
> The OutputRegistry does NOT do SYSML_QN normalization (`::` -> `__` is broken --
> Spike 5 showed the consuming path differs from the producing path in all 4 cases).
> Instead, the backtracker has a structured resolution path:

```python
# For each REFERENCE binding (source_path is always SYSML_QN):

# Step 1: Try OutputRegistry exact match (rare, but handles any dotted aliases)
channel = self._output_registry.resolve(binding.source_path)

if channel is None:
    # Step 2: Secondary resolution for computed attributes.
    # Extract leaf name from SYSML_QN, try parent-scoped dotted lookup.
    # This handles the 4 REFERENCE -> MODULE_OUTPUT cases (Spike 5).
    leaf_name = binding.source_path.rsplit("::", 1)[-1].strip("'")
    parent_part = self._get_parent_part_for_usage(usage)
    if parent_part:
        channel = self._output_registry.resolve(f"{parent_part}.{leaf_name}")

if channel is not None:
    self._binding_resolutions[mapping_key] = BindingResolution(
        resolution_type=BindingResolutionType.MODULE_OUTPUT,
        qualified_name=channel,
        source_path=binding.source_path,
    )
else:
    # Step 3: Design attribute fallback (the 119 ENTRY_POINT cases)
    design_attr = self._resolve_to_design_attribute(binding.source_path)
    if design_attr:
        # ENTRY_POINT with design attribute default
        ...
    else:
        logger.warning(
            "REFERENCE binding '%s' on '%s' could not be resolved. "
            "Treating as entry point.",
            binding.source_path, usage.qualified_name,
        )
        ...
```

### `_resolve_to_design_attribute()` specification

> **Added in iteration 2** (was previously unspecified).

```python
def _resolve_to_design_attribute(self, source_path: str) -> DesignAttributeData | None:
    """Resolve source_path to a literal-valued design attribute (ENTRY_POINT).

    This is the fallback after OutputRegistry resolution fails. It handles
    the 119 REFERENCE -> ENTRY_POINT cases (Spike 5).

    Transitive design attrs (whose default_value is a dotted path pointing
    to a module output) are handled by Phase 4 OutputRegistry aliases and
    never reach this method.

    Resolution:
    1. Extract leaf name from source_path:
       - SYSML_QN ("Ns::Part::attr") -> last segment after "::", strip quotes
       - DOTTED ("instance.output") -> last segment after "."
    2. Search design_attrs by (parent_path, leaf_name) match
    3. If match with literal or None default_value -> return it
    4. If no match -> return None
    """
```

> **Key change:** The fallback to ENTRY_POINT now emits a **warning**, not silent
> acceptance. This makes it visible when the pipeline creates a false entry point
> because resolution failed, rather than burying it in the pipeline YAML.

### The guarantee

> After backtracking, **every** input on **every** CalcUsage has exactly one
> `BindingResolution` stored in `binding_resolutions["{usage_qn}|{param_name}"]`.
> Each resolution is either `ENTRY_POINT` or `MODULE_OUTPUT`.
> There are no unresolved bindings. If resolution fails, it falls back to
> `ENTRY_POINT` with a logged warning.

### Entry point classification (happens later in Step 7)

When a binding resolves to `ENTRY_POINT`, Step 7 classifies it into one of three types:

| Type | Source of Default Value | Example |
|---|---|---|
| `DESIGN_ATTRIBUTE` | Design file literal | `efficiency = 0.92` in design |
| `LIBRARY_DEFAULT` | CalcDef input default | `input eta = 0.9` in library |
| `USAGE_LITERAL` | Literal binding in CalcUsage | `eta = 0.8` in usage |

Entry points are grouped by source file into `ParameterGroup` objects.

### Step 6 output

- `BacktrackingResult` with `binding_resolutions` (the authoritative wiring map)
- `required_usages` (topologically sorted)
- `entry_points` (set of qualified names)

---

## 8. Step 6.5: Expression Compilation {#8-step-65-compilation}

**Question answered:** "Can we auto-generate the Python implementation, or does a human need to write it?"

For each CalcDef with output expression ASTs, the compiler walks the SysIDE AST tree
and converts it to a Python expression string:

```
 SysML AST tree
     |
     v
 reconstruct_expression()
     |  Dispatches on node type (see Section 13 for dispatch rules):
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

### Step 6.5 output

- `dict[str, CalcDefCompilationResult]` mapping CalcDef names to compilation results

---

## 9. Step 7: Build the Computation Graph (THE SINGLE SOURCE OF TRUTH) {#9-step-7-graph}

**Question answered:** "What is the complete, validated pipeline structure?"

`build_computation_graph()` is the **funnel**. It takes ALL prior results and
produces the single `ComputationGraph` that generation reads from.

```
 INPUTS (everything from steps 1-6.5):         OUTPUT (one structure):

 CalcDefs                 \                     ComputationGraph
 CalcUsages                \                      .modules[]
 DesignAttrs                \                     .entry_point_groups[]
 ComputedAttrs (FORMULA)     +-->                 .execution_order[]
 ScopedAggregationData      /
 BacktrackingResult        /
 CompilationResults       /
```

Nothing downstream of `ComputationGraph` looks at raw extraction data.
This is the **single source of truth** contract (ADR-003).

### What Step 7 builds: the three module families

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
 |  | Mechanism: synthetic          |                                        |
 |  |   CalcUsageData created in   |  Inputs resolve through the            |
 |  |   Step 4.5, flows through    |  standard backtracker pipeline.        |
 |  |   normal backtracking        |                                        |
 |  | Flag: is_computed_attribute   |                                        |
 |  +-------------------------------+                                        |
 |  | NOTE: EXPOSE_PURE does NOT    |                                        |
 |  |   produce a module. It is a  |                                        |
 |  |   ChannelAlias only.         |                                        |
 |  +-------------------------------+                                        |
 |                                                                           |
 |  Family 3: Aggregation Modules                    (from Step 3.5)        |
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
silently generating broken code.

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
      v  (resolved via alias)            Family 1: CalcUsage Module
 [annualized_financial]           |      (alias: total_capex -> capital_cost)
      |                           |
      | output: lcoe              |      Family 2: Computed Attribute Module
      v                           '--->[p_net_kw] (p_net_mw * 1000)
 [Pipeline Exit]
```

### Sub-steps within Step 7

1. **Build CalcUsage modules** (Family 1) from `binding_resolutions`
2. **Build FORMULA computed attribute modules** (Family 2) from `binding_resolutions`
   (FORMULA attrs produce synthetic CalcUsages in Step 4.5 that flow through
   normal backtracking in Step 6. Their inputs resolve through the OutputRegistry
   like any other CalcUsage binding.)
3. **Build aggregation modules** (Family 3) directly from `ScopedAggregationData`
   (NOT through the OutputRegistry -- aggregation modules construct their input
   channels from pre-scoped data. The OutputRegistry is for *binding* resolution
   in Step 6, not for all channel construction.)
4. **Classify entry points** into the 3 types
5. **Group entry points** via ParameterGroupDeriver
6. **Collect orphan entry points** not in any group -> "system_design" group
7. **Unified topological sort** across ALL module families
8. **Validate channel references** -- early check before generation

### Step 7 output

- `ComputationGraph` with `modules`, `entry_point_groups`, `execution_order`

---

## 10. Generation: Templates Produce the Output Package {#10-generation}

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

## 11. Cross-Cutting: The Naming System (Global Uniqueness Guarantee) {#11-naming-system}

### When does `::` become `__`?

SysML uses `::` as a namespace separator. Python identifiers cannot contain `::`.
The conversion happens at a **single well-defined point**: `build_element_qualified_name()`
in `core/qualified_names.py`, which is called during extraction (Steps 2-3).

```
 SysML world (raw parser output):       Python world (our data models):
 "FusionPhysics::AlphaNeutronSplit"     "FusionPhysics__AlphaNeutronSplit"
         ::                                      __
```

**Rule:** After `build_element_qualified_name()` runs, names stored on our data
models (`CalcUsageData.qualified_name`, `CalculationDefinitionData.qualified_name`)
use `__`. But binding `source_path` values may still contain `::` because they
come from a different parser code path (`referent.qualified_name` on AST nodes).

> **DELTA vs. current:** This is NOT a change -- the current conversion point is
> correct. The problem was never WHEN conversion happens, but that binding
> source_paths arrive in multiple formats and the lookup code didn't handle all of
> them consistently. The OutputRegistry (Section 12) handles DOTTED format via
> exact match. SYSML_QN format is handled by the backtracker's secondary
> resolution path (Section 7): extract leaf name, scope with parent, then
> resolve the resulting dotted key through the OutputRegistry.

### The naming hierarchy

```
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
| **Channels can always be found** | Given a channel name, find the producer | OutputRegistry maps all aliases to canonical PQN |
| **No collisions across files** | Modules from different SysML files don't clash | Package prefix is part of EQN |

### The `__` separator convention

All internal names use `__` (double underscore). Given an EQN:
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
```

---

## 12. Cross-Cutting: The Output Registry {#12-output-registry}

> **DELTA vs. current:** The OutputRegistry does not exist today. It replaces the
> five ad-hoc indexes in the backtracker constructor (`_computed_attr_index`,
> `_aggregation_output_index`, `_output_catalog`, `_design_attr_binding_index`,
> `_usage_by_name`).

### The problem it solves

Bindings arrive in two formats (Spike 1, empirically verified):
- `"alpha_split.p_alpha"` (dotted, from CHAIN bindings)
- `"FusionPhysics::GrossEfficiency::eta"` (SysML QN, from REFERENCE bindings)

> Bare names (e.g., `"wattage"`) were never observed in any tested model
> (94 bindings, 3 models). The OutputRegistry does not register or resolve bare names.

Module outputs are registered with one canonical channel name (PQN format):
- `"catfmfephysics__catf_physics__alpha_split__p_alpha"`

The registry handles **dotted format resolution** (exact match). SYSML_QN
source_paths from REFERENCE bindings are handled by the **backtracker's
secondary resolution path** (leaf-name extraction + parent-scoped lookup),
not by the OutputRegistry. This is because SYSML_QN normalization (`::` -> `__`)
is broken: the consuming path differs from the producing path (Spike 5).

> **Scope clarification:** The OutputRegistry is the single mechanism for
> *binding* resolution from CHAIN source_paths and alias lookups. It is NOT
> the universal channel construction mechanism. Aggregation modules construct
> their input channels directly from `ScopedAggregationData` (Step 7).
> REFERENCE bindings use the backtracker's secondary resolution + design
> attribute fallback (Step 6).

### Design

```python
class OutputRegistry:
    """Single lookup for resolving any binding source_path to a channel name.

    Every pipeline output (CalcUsage output, FORMULA computed attribute output,
    aggregation module output) is registered with a canonical channel name and
    a set of lookup keys (aliases). Resolution tries exact match, then
    normalized forms.
    """

    def __init__(self) -> None:
        self._index: dict[str, str] = {}        # alias -> canonical channel
        self._canonical: set[str] = set()        # set of canonical channels

    def register(self, canonical_channel: str, lookup_keys: list[str]) -> None:
        """Register a channel with all its lookup keys.

        Lookup keys are dotted and EQN formats only -- bare names are NOT
        registered (Spike 4: zero bare-name references in any tested model).
        """
        self._canonical.add(canonical_channel)
        self._index[canonical_channel] = canonical_channel
        for key in lookup_keys:
            if key in self._index and self._index[key] != canonical_channel:
                logger.warning(
                    "OutputRegistry key collision: '%s' already maps to '%s', "
                    "refusing to overwrite with '%s'",
                    key, self._index[key], canonical_channel,
                )
                continue
            self._index[key] = canonical_channel

    def register_alias(self, alias: str, canonical_channel: str) -> None:
        """Register an alias that maps to an existing canonical channel."""
        assert canonical_channel in self._canonical, (
            f"Cannot alias to unregistered channel: {canonical_channel}"
        )
        self._index[alias] = canonical_channel

    def resolve(self, source_path: str) -> str | None:
        """Resolve a dotted source_path to a canonical channel name.

        Exact match only. No normalization.

        Empirically verified:
        - Spike 1: CHAIN bindings always use DOTTED format ("instance.output")
        - Spike 5: SYSML_QN normalization (:: -> __) is broken -- the consuming
          path differs from the producing path. REFERENCE bindings are handled
          by the backtracker's secondary resolution, not here.
        - Spike 4: Bare names are never produced by the parser.

        Returns canonical channel name or None.
        """
        return self._index.get(source_path)
```

### What gets registered and when

| Source | Phase | Canonical Channel Format | Lookup Keys |
|--------|-------|--------------------------|-------------|
| CalcUsage outputs | 1 | `{usage_eqn}__{output_name}` | dotted (`instance.output`), EQN |
| FORMULA computed attr outputs | 1 | `{part_eqn}__{attr_name}__{attr_name}` | dotted (`part.attr`) |
| Aggregation module outputs | 1 | `{scoped_eqn}__{attr_name}` | dotted, full instance path |
| `:>>` CHAIN aliases | 2 | (resolved against Phase 1) | scoped dotted (`instance_path.attr`) |
| EXPOSE_PURE aliases | 3 | (resolved against Phase 1+2) | scoped dotted (`parent_part.attr`, from `references` field) |
| Design-attr transitive aliases | 4 | (resolved against Phase 1-3) | `parent_part.attr_name` |

> **All keys are dotted format.** No bare-name registration (Spike 4). No SYSML_QN
> keys (Spike 5: `::` normalization is broken). CHAIN and EXPOSE_PURE aliases
> are scoped with instance/parent paths at construction time (Spike 6).

### The guarantee

> `OutputRegistry.resolve(source_path)` is a **pure function**: exact match only,
> returns `None` or a canonical channel name. No cascade, no normalization,
> no silent fallback. The phase ordering is an explicit contract: each phase
> only references names from prior phases.
>
> The **backtracker** owns the full resolution strategy:
> - CHAIN bindings: `resolve(source_path)` directly (DOTTED -> exact match)
> - REFERENCE bindings: extract leaf name + parent-scoped `resolve()` (secondary)
> - Fallback: `_resolve_to_design_attribute()` for entry points
> - Final fallback: ENTRY_POINT with warning

---

## 13. Cross-Cutting: AST Dispatch Rules {#13-ast-dispatch}

SysIDE AST nodes have a surprising property: `FeatureReferenceExpression` and
`FeatureChainExpression` both carry a `function` attribute. This means
`hasattr(node, "function")` matches all three node types.

**Mandatory dispatch order for ALL AST-walking code:**

```python
# CORRECT -- always check specific types first:
if SysideAdapter.is_instance(node, "FeatureReferenceExpression"):
    ...
elif SysideAdapter.is_instance(node, "FeatureChainExpression"):
    ...
elif SysideAdapter.is_instance(node, "OperatorExpression"):
    ...
elif hasattr(node, "function"):   # InvocationExpression (generic, LAST)
    ...
```

```python
# WRONG -- generic check catches all three:
if hasattr(node, "function"):     # matches FeatureRef and FeatureChain too!
    ...
```

This rule applies in:
- `expression_utils.py` / `reconstruct_expression()`
- `hierarchy_resolver.py` / `_walk_aggregation_ast()`
- `hierarchy_resolver.py` / `_unwrap_invocation()`
- Any future code that walks SysIDE AST nodes

> **Ideal future state:** Extract this pattern into a shared `dispatch_ast_node()`
> helper that enforces the correct order, so individual call sites can't get it wrong.

---

## Appendix A: Desired-State Step Index

| Step | What | Source File | Differs from Current? |
|------|------|-------------|----------------------|
| 1 | Load models | extraction/extractor.py | No |
| 2 | Extract CalcDefs | extraction/extractor.py | No |
| 3 | Extract CalcUsages + template expansion | extraction/usage_extractor.py | No |
| 3.5 | Hierarchy extraction + override application + aggregation scoping | hierarchy_resolver.py, initialization.py | **Yes:** handles CHAIN overrides, SYSML_QN/DOTTED normalization, produces scoped ChannelAlias (filtered, instance-path-prefixed) + ScopedAggregationData. Direct sum() code (no Protocol). |
| ~~3.6~~ | ~~Alias enrichment~~ | ~~initialization.py~~ | **Eliminated.** Aliases come from 3.5 and 4.5 |
| 4 | Extract design attributes | analysis/parameter_groups.py | No |
| 4.5 | Extract & classify computed attributes | computed_attribute_extractor.py | **Yes:** EXPOSE_PURE produces scoped ChannelAlias (using `references` field, not `expression_text`). FORMULA produces synthetic CalcUsageData. |
| ~~4.7~~ | ~~Scope aggregation expressions~~ | ~~initialization.py~~ | **Moved** into Step 3.5 (scoping) + Step 5 (registration only) |
| 5 | **Build OutputRegistry** | **NEW: core/output_registry.py** | **New step.** Replaces 5 backtracker indexes. Exact-match resolve only (no SYSML_QN normalization). |
| 6 | Dependency backtracking | analysis/dependency_backtracker.py | **Yes:** CHAIN via OutputRegistry.resolve(). REFERENCE via leaf-name extraction + parent-scoped resolve + design_attr fallback. Warns on unresolved. |
| 6.5 | Expression compilation | extraction/expression_compiler.py | No |
| 7 | Build ComputationGraph | resolution/graph_builder.py | **Yes:** no longer builds output catalog (registry does it) |

## Appendix B: Desired-State File Map

```
src/sysml_codegen/
  core/
    models.py               BindingResolution, BindingResolutionType, ChannelAlias
    qualified_names.py       EQN/PQN/module name functions
    identifier_types.py      SysMLQualifiedName, PythonModulePath, ModuleType
    output_registry.py       NEW: OutputRegistry (Section 12)
  extraction/
    extractor.py             Steps 1-2: SysMLDataExtractor, CalcDefs
    usage_extractor.py       Step 3: CalcUsages, template detection, virtual expansion
    hierarchy_resolver.py    Step 3.5: redefinitions, multiplicities, aggregation + scoping
                             CHANGED: direct sum() decomposition (no Protocol),
                             scoped ChannelAlias production (filtered, instance-path-prefixed),
                             ScopedAggregationData output
    computed_attribute_extractor.py   Step 4.5: 5-way classification
                             CHANGED: EXPOSE_PURE -> ChannelAlias (via references field)
    expression_compiler.py   Step 6.5: compile_calc_def(), Compilability
    expression_utils.py      Step 6.5: reconstruct_expression(), AST walking
    data_models.py           Shared data models (AttributeInfo, etc.)
  analysis/
    dependency_backtracker.py  Step 6: CHANGED: uses OutputRegistry, no internal indexes
    parameter_groups.py        Steps 4-5: design attrs, ParameterGroupDeriver
  resolution/
    graph_builder.py         Step 7: build_computation_graph()
    models.py                PipelineModule, ModuleInput, ModuleOutput, ComputationGraph
  generation/
    initialization.py        build_pipeline_context(): Steps 1-7 orchestration
                             CHANGED: Step 3.6 removed, Step 5 added (OutputRegistry)
    ...
```

## Appendix C: Migration Path

The changes can be implemented incrementally. All spikes are complete
(iterations 1+2, 7 spikes total). Design is empirically grounded.

1. **Add `ChannelAlias` data model** to `core/models.py`. Zero risk -- additive only.
2. **Add `OutputRegistry`** to `core/output_registry.py`. Zero risk -- new file.
   Exact-match `resolve()` only (Spike 5: no SYSML_QN normalization).
   No bare-name registration (Spike 4).
3. **Produce scoped `ChannelAlias` from EXPOSE_PURE** in computed_attribute_extractor.
   Low risk -- additive. Must use `references` field, not `expression_text` (Spike 3).
   Alias keys scoped with parent part name (Spike 5: enables REFERENCE resolution).
4. **Produce scoped `ChannelAlias` from `:>>` CHAIN** in hierarchy_resolver.
   Low risk -- additive. Filter BARE non-references (Spike 6: CAS codes).
   Scope DOTTED canonical_names with instance_path prefix (Spike 6).
5. **Build `OutputRegistry` in initialization.py** (new Step 5). Medium risk -- must
   register all current output formats with explicit 4-phase ordering.
6. **Wire backtracker to use `OutputRegistry.resolve()`**. High risk -- replaces 5 indexes.
   CHAIN: direct resolve(). REFERENCE: leaf-name extraction + parent-scoped resolve.
   Add `_resolve_to_design_attribute()` per spec. Gate behind feature flag.
   Run both paths in parallel and assert same results.
7. **Remove old indexes** from backtracker after parallel validation passes.
8. **Add CHAIN override support** to `_rewrite_virtual_bindings()`. Normalize SYSML_QN
   and DOTTED formats only (Spike 1 -- no bare names exist).
9. **Wrap existing `sum()` logic** in hierarchy_resolver with validation. No Protocol.
   Aggregation scoping produces `ScopedAggregationData` in Step 3.5 before Step 5
   registration. Aggregation modules built directly from scoped data in Step 7
   (not through OutputRegistry).
