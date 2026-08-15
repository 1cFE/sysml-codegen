# 05 -- Module Factory: Building the 3 Types of Pipeline Modules

> **Status: historical.** The three factory functions this document describes lived in
> `resolution/graph_builder.py`, **deleted** by the Item 7 retirement (2026-08-12, `19072ad` /
> `82c7951` / `882fc8d` / `3071fba`).
>
> **The subject survives; the owner does not.** The shipped route still produces `CALCULATION`,
> `FORMULA`, and `AGGREGATION` modules, and still returns them as pure data — projection builds
> them from the instance graph (`elaboration/project.py`, `_build_calculation_modules` and the
> computed-input path). What is gone is the resolution work these factories did while building:
> projection classifies sources elaboration has already resolved.
>
> Everything below is retained as the record of the deleted design. It is accurate about the
> code that was removed and is **not a description of what the product does**. For that, read
> [00-pipeline-overview](00-pipeline-overview.md).

Module construction is decoupled from ad-hoc inline resolution. CalcUsage
factories receive pre-resolved data (from the
[backtracker](11-analysis-backtracker.md)). FORMULA factories use the
pre-computed [attribute resolution map](16-computed-attributes.md); Aggregation
factories resolve SumTerm/SingletonTerm inputs through the shared
[`resolve_producer()`](04-producer-resolution.md) table, via the
`_build_agg_input_source()` choke point. All three produce a
[PipelineModule](09-data-models.md#resolution-models)
+ new [entry points](06-entry-point-classifier.md#two-entry-point-creation-paths).

## Requirements

| ID | Requirement | Verified by |
|----|-------------|-------------|
| REQ-MF-01 | All three factory functions SHALL be pure data transformers: return `(PipelineModule, dict[str, EntryPoint])`, no mutation of shared state. | Type signatures return tuples; no `entry_points[k] = v` inside factory bodies |
| REQ-MF-02 | CalcUsage factory SHALL fail-fast (`ValueError`) on missing `binding_resolutions` key -- no fallback resolution. | `if mapping_key not in binding_resolutions: raise ValueError(...)` in `_build_pipeline_module()` |
| REQ-MF-03 | FORMULA factory SHALL set `module_kind=ModuleKind.FORMULA` and `compilability=FULLY_COMPILABLE`. | `assert module.module_kind == ModuleKind.FORMULA and module.compilability == FULLY_COMPILABLE` |
| REQ-MF-04 | Aggregation factory SHALL handle all three [extraction term types](01-extraction.md#aggregation-data-sumterm-singletonterm-localterm): SumTerm, SingletonTerm, LocalTerm. | Code paths exist for each; missing term type = `AttributeError` |
| REQ-MF-05 | Every [ModuleInput](09-data-models.md#resolution-models) SHALL have exactly one [InputSource](04-producer-resolution.md#inputsource-output-model) with `source_type` in {`module_output`, `entry_point`}. | `all(mi.source.source_type in {"module_output","entry_point"} for mi in module.inputs)` |
| REQ-MF-06 | SumTerm and SingletonTerm LITERAL fallback SHALL use `_find_literal_redefinition()` to propagate `:>>` default values. See [18](18-literal-value-propagation.md). | Entry point `default_value` matches `RedefinitionData.literal_value` when LITERAL redef exists |
| REQ-MF-07 | LocalTerm resolution SHALL try: (1) sibling aggregation output, (2) [EXPOSE_PURE alias](16-computed-attributes.md), (3) entry point fallback -- in that order. | Three `if/elif/else` branches in LocalTerm loop; order-dependent (Strategy 1 checked first) |
| REQ-MF-08 | Single-output modules SHALL use `field_name="root"`; multi-output SHALL use attribute names. | `len(outputs)==1 => outputs[0].field_name=="root"`; `len(outputs)>1 => field_name==attr.name` |
| REQ-MF-09 | The aggregation compile step SHALL substitute each symbolic ref with its `inputs.X` form on **whole-token** boundaries (`re.sub(r"\bref\b", …)`), never a plain substring `.replace()`. | A ref that is a substring of another (`cost` / `cost_total`) SHALL NOT corrupt (`inputs.inputs.cost_total`); disjoint refs SHALL compile byte-identically. TRUTH-DEBT Item 6, Site 2; conformance: `test_hygiene_tail_agg_compile.py` |

## 1. The PipelineModule Data Model

See [09-data-models](09-data-models.md#resolution-models) for full field definitions.

```python
class PipelineModule(BaseModel):
    name: str                       # Lowercase EQN (15-naming-conventions)
    module_type: str                # PascalCase from calc def QN
    inputs: list[ModuleInput]       # What the module consumes
    outputs: list[ModuleOutput]     # What the module produces
    execution_order: int            # Position in topological sort (07-graph-assembly)
    compilability: Compilability    # FULLY_COMPILABLE | MANUAL_REQUIRED | UNKNOWN
    compiled_expression: str | None # Inlined expression for auto-gen modules
    module_kind: ModuleKind         # CALCULATION | FORMULA | AGGREGATION | CONSTRAINT | REPORT_AGGREGATOR (resolution/models.py)

class ModuleInput(BaseModel):
    param_name: str      # e.g., "capacity"
    python_type: str     # Always "float" for now
    source: InputSource  # WHERE the value comes from (04-producer-resolution)

class ModuleOutput(BaseModel):
    field_name: str    # "root" for single-output (REQ-MF-08), attr name for multi
    python_type: str   # Always "float" for now
    channel_name: str  # PQN format (15-naming-conventions)
```

Every input is wired to exactly one source (REQ-MF-05): an upstream module's
output channel, or a user-provided [entry point](06-entry-point-classifier.md).

## 2. CalcUsage Modules -- `_build_pipeline_module()`

**Source**: [CalcUsageData](09-data-models.md#extraction-models) + its
[CalculationDefinitionData](09-data-models.md#extraction-models). A named invocation
of a calculation definition. The function receives `binding_resolutions` mapping
`"{usage_qn}|{param_name}"` to a [BindingResolution](09-data-models.md#core-models) --
single source of truth ([REQ-RES-06](03-resolution-overview.md#requirements)).
Missing mapping = immediate raise (REQ-MF-02, fail-fast, no fallback).

**Inputs**: Look up each calc def input_attribute in binding_resolutions.
`MODULE_OUTPUT` -> wire to upstream channel. `ENTRY_POINT` -> wire to entry point.

**Outputs**: [PQN](15-naming-conventions.md) channel per output_attribute.
Single output: `field_name="root"` (REQ-MF-08); multi-output: attribute name.

```
_build_pipeline_module(
    usage=CalcUsageData(qualified_name="Design__plant__battery_cost_calc"),
    calc_def=CalcDef(inputs=[capacity, unit_cost], outputs=[battery_cost]),
    binding_resolutions={
        "...|capacity":  MODULE_OUTPUT -> "design__plant__size_calc__capacity",
        "...|unit_cost": ENTRY_POINT  -> "design__plant__unit_cost",
    },
)
-->
PipelineModule(
    name="design__plant__battery_cost_calc",
    module_type="BatteryCostCalcModule",
    inputs=[
        ModuleInput("capacity",  source=module_output("design__plant__size_calc__capacity")),
        ModuleInput("unit_cost", source=entry_point("design__plant__unit_cost")),
    ],
    outputs=[ModuleOutput("root", channel="design__plant__battery_cost_calc__battery_cost")],
    execution_order=3,
)
```

## 3. FORMULA Modules -- `_build_computed_attr_module()`

**Source**: [ComputedAttributeData](16-computed-attributes.md) with classification
FORMULA -- a PartDef attribute with an inline expression. Synthetic module; no
SysML calc usage. The [expression compiler](14-expression-compiler.md) already
produced `compiled_expression` with `inputs.X` refs.

**Input resolution**: (1) Parse input names from `compiled_expression` via
`inputs\.(\w+)` regex. (2) Look up each name in the pre-computed
[attribute resolution map](16-computed-attributes.md) (`_build_attribute_resolution_map()`).
Inputs with kind `FORMULA`/`EXPOSE_ALIAS` + channel → `module_output`.
All others → `entry_point`. This is PRE-RESOLUTION: channels are known at
classification time, so no registry lookup is needed.

**Outputs**: Single output, `field_name="root"` (REQ-MF-08).
**Kind**: `module_kind=ModuleKind.FORMULA`, `FULLY_COMPILABLE` (REQ-MF-03).

```
_build_computed_attr_module(
    ca=ComputedAttributeData(
        name="total_cost", owning_part_name="SolarPlant",
        compiled_expression="inputs.material_cost + inputs.labor_cost",
    ),
)
-->
PipelineModule(
    name="solarplant__total_cost",
    module_type="SolarPlantTotalCostModule",
    inputs=[
        ModuleInput("material_cost", source=module_output("solarplant__material_cost__...")),
        ModuleInput("labor_cost",    source=entry_point("solarplant__labor_cost")),
    ],
    outputs=[ModuleOutput("root", channel="solarplant__total_cost__total_cost")],
    module_kind=ModuleKind.FORMULA, compilability=FULLY_COMPILABLE,
)
```

## 4. Aggregation Modules -- `_build_aggregation_module()`

**Source**: [ScopedAggregationData](09-data-models.md#extraction-models) -- a PartDef
`:>>` expression with `sum()` calls, scoped to a design instance path by
[aggregation scoping](13-aggregation-scoping.md). Rollup across child part usages.
Additional inputs: `expose_aliases` ([EXPOSE_PURE](16-computed-attributes.md) alias map
for LocalTerms), `usage_type_map` (type-aware PartDef QN resolution -- see [doc 18](18-literal-value-propagation.md)).

> **Note**: The `usage_type_map` (Strategy 1 in `_find_literal_redefinition()`)
> is **essential** when the PartUsage name differs from the PartDef name. For
> example, the usage `permitting` types to PartDef `Permitting_Interconnect`.
> Name-based Strategy 2 fails because
> `sanitize_name("Permitting_Interconnect").lower()` != `"permitting"`.
> Strategy 1 resolves this via `usage_type_map[("Site_Infrastructure",
> "permitting")]` → `"Permitting_Interconnect"`.

Expression is decomposed into three term types (REQ-MF-04):

### 4a. SumTerm -- `sum(child.attr * count)`

```python
SumTerm(part_usage_name="pv_module", attribute_name="capital_cost",
        multiplicity_attr="module_count", multiplicity_count=20)
```

Resolution chain (live path: `_build_agg_input_source()` → `resolve_producer(request,
context)` with `policy=LENIENT`, see [producer resolution](04-producer-resolution.md)):
1. `resolve_producer()` runs the shared `KEY_FORMS` table -- tier-1 channel forms (scoped/alias/`chain_redefinition_follow`/`direct_channel`) then tier-2 design attributes + [registry](10-output-registry.md) lookup. A `module_output` result wires directly.
2. **LITERAL fallback** (REQ-MF-06) -- on a terminal-miss `entry_point` result, `_build_agg_input_source()` calls `_find_literal_redefinition()` for `:>> attr = value`
   on the child PartDef. If found, the value becomes the entry point's `default_value`
   and the module stays `FULLY_COMPILABLE` (see [doc 18](18-literal-value-propagation.md)).
3. Entry point (no default) + `MANUAL_REQUIRED` compilability.

When `multiplicity_attr` is present, adds a second input for the count
(entry point, default = `multiplicity_count`, `python_type="float"`).

### 4b. SingletonTerm -- `child.attr` (no multiplication)

```python
SingletonTerm(source_path="allocation_model.total_allocation")
```

Resolution chain (same live path: `_build_agg_input_source()` → `resolve_producer()`, `policy=LENIENT`):
1. `resolve_producer()` -- CHAIN redefinition tracing (`chain_redefinition_follow`) + scoped/alias registry forms
2. Direct channel construction -- `instance_path__prefix__output_name` (the `direct_channel` key form, inside the shared table)
3. **LITERAL fallback** (REQ-MF-06) -- same as SumTerm, found value becomes EP default
4. Entry point (no default) + `MANUAL_REQUIRED` compilability.

### 4c. LocalTerm -- same-PartDef attribute

```python
LocalTerm(attribute_name="misc_hardware_cost")
```

Tries three strategies in order (REQ-MF-07):
1. **Sibling aggregation output** -- another aggregation module at the same scope
   produces a channel with the double-attr format `{ip}__{attr}__{attr}`.
2. **EXPOSE_PURE alias** -- the `expose_aliases` map (built in Step 6.6b from
   [EXPOSE_PURE ComputedAttributes](16-computed-attributes.md)) provides a dotted
   expression path (e.g., `"allocation_model.total_allocation"`). That path is
   then resolved through `resolve_producer()`, but the channel is taken
   **only when the outcome is a `module_output`** (the D5 guard). Any other
   outcome is discarded here and falls through to strategy 3, because the
   resolver keys its terminal-miss entry point on the alias target, not
   `attribute_name` — the LocalTerm fallback below keeps the
   `{module_eqn}__{attribute_name}` key.
3. **Entry point fallback** -- user-provided value. LocalTerm keeps its own simpler
   inline entry-point fallback for this leg (it did not move into `_build_agg_input_source()`).

After all terms are processed, symbolic references (`pv_module.capital_cost`)
are replaced with input references (`inputs.pv_module_capital_cost`) to produce
`compiled_expression`. The substitution is **whole-token** (`re.sub(r"\bref\b", …)`),
not a plain substring `.replace()`: a length-sorted `.replace()` still corrupts when
one ref is a substring of another (`cost` matches inside an already-substituted
`inputs.cost_total` → `inputs.inputs.cost_total`); the `\b` boundary blocks that
(REQ-MF-09). **Kind**: `module_kind=ModuleKind.AGGREGATION`.

### Concrete example

SysML: `total_cost :>> sum(pv_module.capital_cost * module_count) + inverter.install_cost + misc_cost`
Scope: `Design__plant__solar_array` (from [aggregation scoping](13-aggregation-scoping.md))

```
Input:  sum_terms=[SumTerm("pv_module", "capital_cost", "module_count", 20)]
        singleton_terms=[SingletonTerm("inverter.install_cost")]
        local_terms=[LocalTerm("misc_cost")]
-->
PipelineModule(
    name="design__plant__solar_array__total_cost",
    module_type="SolarArrayTotalCostModule",
    inputs=[
        ModuleInput("pv_module_capital_cost",  source=module_output("...pv_module__cost_calc__capital_cost")),
        ModuleInput("module_count",            source=entry_point("...solar_array__module_count", default=20)),
        ModuleInput("inverter_install_cost",   source=module_output("...inverter__install_calc__install_cost")),
        ModuleInput("misc_cost",               source=entry_point("...total_cost__misc_cost")),
    ],
    outputs=[ModuleOutput("root", channel="...solar_array__total_cost__total_cost")],
    module_kind=ModuleKind.AGGREGATION,
    compiled_expression="inputs.pv_module_capital_cost * inputs.module_count
                       + inputs.inverter_install_cost + inputs.misc_cost",
)
```

## 5. The Key Insight: Structured Resolution

All three factory functions follow the same output contract (REQ-MF-01):

    inputs + context  -->  (PipelineModule, new_entry_points)

No mutation of shared state. Entry points are **returned**, not injected into
a shared dict. But the three types differ in HOW they resolve:

| Type | Resolution source | Who resolves |
|------|-------------------|-------------|
| CalcUsage | `binding_resolutions` dict (pre-computed by [backtracker](11-analysis-backtracker.md)) | Backtracker (during DFS) |
| FORMULA | Pre-computed [attribute resolution map](16-computed-attributes.md) | Factory uses map (no resolver call) |
| Aggregation | [`resolve_producer()`](04-producer-resolution.md) shared table, via `_build_agg_input_source()` | Factory calls resolve_producer |

CalcUsage factories are truly pure data transformers -- lookup only, no
resolution logic. FORMULA factories read the pre-computed map; Aggregation
factories resolve SumTerm/SingletonTerm inputs through `resolve_producer()`
via the `_build_agg_input_source()` choke point. Entry points
created by FORMULA/Aggregation factories are hardcoded to DESIGN_ATTRIBUTE;
CalcUsage entry points receive full 3-strategy classification. See
[06-entry-point-classifier](06-entry-point-classifier.md#two-entry-point-creation-paths).

## Related Documents

- **Upstream**: [03-resolution-overview](03-resolution-overview.md) -- orchestrator that calls factory functions, [04-producer-resolution](04-producer-resolution.md) -- `resolve_producer()`, the shared resolution authority
- **Downstream**: [07-graph-assembly](07-graph-assembly.md) -- topological sort of produced modules, [06-entry-point-classifier](06-entry-point-classifier.md) -- classifies returned entry points
- **Aggregation**: [13-aggregation-scoping](13-aggregation-scoping.md) -- produces ScopedAggregationData, [18-literal-value-propagation](18-literal-value-propagation.md) -- LITERAL fallback defaults
- **Computed attrs**: [16-computed-attributes](16-computed-attributes.md) -- FORMULA/EXPOSE_PURE classification
- **Data models**: [09-data-models](09-data-models.md) -- PipelineModule, ModuleInput, ModuleOutput, InputSource
- **Naming**: [15-naming-conventions](15-naming-conventions.md) -- EQN, PQN, channel name formats
