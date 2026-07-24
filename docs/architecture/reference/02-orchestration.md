# 02 -- Orchestration: The Pipeline Builder

## What orchestration does

Orchestration is the conductor of the sysml-codegen pipeline. It does not
extract SysML data, resolve dependencies, or render templates. It calls
those layers in the right order and threads data between them:

```
  extraction  -->  orchestration  -->  resolution  -->  generation
                   (this layer)
```

This logic lives in `orchestration/pipeline_builder.py`. It is coordination
code (not generation) that produces the [PipelineContext](#pipelinecontext)
that [generation](08-generation.md) consumes.

## Requirements

| ID | Requirement | Verified by |
|----|-------------|-------------|
| REQ-ORCH-01 | `build_pipeline_context()` SHALL execute steps in strict dependency order: 3.5 before 4, 4.5 before 5, 5.5 before 6, all before 7. | Step ordering in `build_pipeline_context()` matches DAG; reorder causes `AttributeError` or silent wiring bugs |
| REQ-ORCH-02 | Step 3.5 SHALL [rewrite virtual bindings](#virtual-binding-rewriting) in-place before any downstream step reads `calc_usages`. | `_rewrite_virtual_bindings()` called before Steps 4-7; binding_type mutations visible to backtracker |
| REQ-ORCH-03 | Step 4.5 SHALL remove FORMULA-classified [computed attributes](16-computed-attributes.md) from `design_attrs` before [ParameterGroupDeriver](17-parameter-group-deriver.md) construction. | After Step 4.5: `all(ca.name not in design_attrs for ca in computed_attrs if ca.classification == FORMULA)` |
| REQ-ORCH-04 | [OutputRegistry](10-output-registry.md) SHALL register outputs in strict phase order: 1a/1b/1c (canonical) then 2/3/4 (aliases). | Phase 2-4 `register_alias()` calls reject unknown canonical channels |
| REQ-ORCH-05 | Each [aggregation expression](01-extraction.md#aggregation-data-sumterm-singletonterm-localterm) SHALL be scoped to its concrete design instance path(s) via virtual CalcUsage matching. | `len(scoped_agg_data) >= len(hierarchy_data.aggregation_expressions)` (one per instance) |
| REQ-ORCH-06 | `build_pipeline_context()` SHALL return a [PipelineContext](#pipelinecontext) where `computation_graph` is the single source of truth -- [generation](08-generation.md) SHALL NOT access extraction models directly. | All [templates](08-generation.md) receive only `ComputationGraph` fields |
| REQ-ORCH-07 | CHAIN alias canonical names SHALL resolve to Phase 1 channels. Unresolvable aliases produce a warning, not an error. | Phase 2 logs warning for unresolved; does not raise |

## build_pipeline_context() -- the 7-step sequence

Everything the orchestrator builds ends up in a [PipelineContext](#pipelinecontext).
[Generation](08-generation.md) templates primarily need `computation_graph`, but the
context carries all intermediate data for debugging and future generation modes.

| Step | What it does | Produces | Detail |
|------|-------------|----------|--------|
| 1 | Load SysML models via `SysMLDataExtractor` | `extractor` | [01-extraction](01-extraction.md) |
| 2 | Extract calc definitions from the model | `calc_defs` | [01-extraction](01-extraction.md) |
| 2.6 | Extract neutral constraint facts (`ConstraintFacts`) — always populated, may carry empty `usages` | `constraint_facts` | [28-constraint-lowering-and-catalog](28-constraint-lowering-and-catalog.md), REQ-EXT-09 |
| 3 | Extract calc usages with binding info | `calc_usages` | [01-extraction](01-extraction.md) |
| 3.5 | Hierarchy extraction + [binding rewrite](#virtual-binding-rewriting) + [aggregation scoping](#aggregation-scoping) + CHAIN aliases | `hierarchy_data`, `scoped_agg_data`, `chain_aliases` | [12](12-virtual-binding-rewrite.md), [13](13-aggregation-scoping.md) |
| 4 | Extract design attributes (literal values from PartDefs) | `design_attrs` | [17](17-parameter-group-deriver.md) |
| 4.5 | Extract [computed attributes](16-computed-attributes.md), remove FORMULAs from design attrs | `computed_attrs`, `expose_aliases` | [16](16-computed-attributes.md) |
| 5.5 | Build [OutputRegistry](10-output-registry.md) (4-phase lookup table, incl. the [Phase 3b](#phase-3b-confirm-multi-hop-expose-tentatives) confirm pass) | `output_registry` | [10](10-output-registry.md) |
| 5.55 | Expand part-def EXPOSE aliases per design instance into the registry's structured `_scoped_alias` namespace | registry mutation | [10](10-output-registry.md), [16](16-computed-attributes.md) |
| 5.56 | Rescue self-named bindings (`in x = x`) to their resolvable outer EXPOSE channel; the trap case is left as-is | `calc_usages` mutation | [12](12-virtual-binding-rewrite.md) |
| 5.6 | Re-run FORMULA removal: a Phase-3b tentative that reverted to FORMULA is removed from `design_attrs` (INV-G) | `design_attrs` mutation | [16](16-computed-attributes.md) |
| 5.65 | Materialize supplied subsystem-attr values (`graph_design_attrs`), widened to a constraint actual's bare-name demand with no calc-usage binding of its own | `graph_design_attrs` | [28-constraint-lowering-and-catalog](28-constraint-lowering-and-catalog.md) |
| 5.7 | Create [ParameterGroupDeriver](17-parameter-group-deriver.md), now that `design_attrs` reflects final classifications | `group_deriver` | [17](17-parameter-group-deriver.md) |
| [P1 RESOLVE] | Lower every admitted constraint usage to concrete graph structure (profile preflight halts loudly on BLOCK) | `concrete_constraints`, `part_occurrences` | [28-constraint-lowering-and-catalog](28-constraint-lowering-and-catalog.md) |
| 6 | Run [DependencyBacktracker](11-analysis-backtracker.md) | `backtracking_result` | [11](11-analysis-backtracker.md) |
| 6.5 | Compile SysML expressions to Python strings | `compilation_results` | [14](14-expression-compiler.md) |
| 7 | Build [ComputationGraph](09-data-models.md#resolution-models); [P4 CATALOG] assembles `constraint_catalog` from eligible entries | `computation_graph` | [07](07-graph-assembly.md), [28-constraint-lowering-and-catalog](28-constraint-lowering-and-catalog.md) |

Key ordering constraints (REQ-ORCH-01):

- **Step 3.5 before Step 4**: binding rewriting mutates `calc_usages` in place (REQ-ORCH-02);
  later steps must see rewritten bindings.
- **Step 4.5 before the group deriver (Step 5.7)**: removes FORMULA attributes from
  `design_attrs` (REQ-ORCH-03), preventing false entry points in the
  [parameter group deriver](17-parameter-group-deriver.md). The removal re-runs at
  Step 5.6 because the registry's Phase 3b confirm pass can revert a tentative EXPOSE
  back to FORMULA after the Step-4.5 pass already ran (INV-G) -- the deriver must see
  final classifications.
- **Steps 5.55/5.56 after 5.5, before 6**: the scoped aliases and rescued bindings must
  exist before the backtracker reads them.
- **Step 5.5 before Step 6**: the [backtracker](11-analysis-backtracker.md) uses the
  [OutputRegistry](10-output-registry.md) as its sole resolution path.

## build_output_registry() -- the 4-phase lookup table

The [OutputRegistry](10-output-registry.md) uses four [typed registries](10-output-registry.md)
mapping binding references to canonical channel names (`CanonicalChannel`): scoped keys,
SysML QNs, flat aliases, and the structured `_scoped_alias` namespace (keyed by
`ScopedAliasKey`, a `(scope, leaf)` tuple) for part-def EXPOSE aliases.
**Why multiple registries?** Extraction produces `source_path` strings in different
formats depending on AST node type -- a `FeatureChainExpression` produces a scope-relative
dotted path (queried via `ScopedKey`), while a `REFERENCE` binding uses a SysML QN
(queried via `SysMLQN`). Type-directed dispatch selects the correct registry. See
[The Scope Problem](03-resolution-overview.md#the-scope-problem) for why `ScopedKey`
(the hierarchy-scoped key) is the critical one. Phase ordering is enforced (REQ-ORCH-04).

### Phase 1: Canonical channels

Registers the actual outputs that pipeline modules produce.

**Phase 1a -- CalcUsage outputs.** Two typed keys per output ([15-naming-conventions](15-naming-conventions.md), [10-output-registry](10-output-registry.md)):

```
Calc usage: SolarBatteryDesign__solar_battery_plant__solar_array__cost_model
Output:     total_cost

Canonical (CanonicalChannel): solar_battery_plant__solar_array__cost_model__total_cost
Scoped    (ScopedKey):        solar_battery_plant.solar_array.cost_model.total_cost
```

**ScopedKey is the critical key** -- the [resolver](04-producer-resolution.md#c-scopedregistrylookup)
constructs `ScopedKey` lookups by prepending the consumer's scope to the bare `source_path`.

**Phase 1b -- Aggregation outputs.** Registered with `ScopedKey` (stripped
dotted hierarchy path) in the scoped registry.

**Phase 1c -- FORMULA outputs.** [Computed attributes](16-computed-attributes.md)
classified as FORMULA with `FULLY_COMPILABLE` compilability generate synthetic
modules. Registered with `SysMLQN` key in the SysML QN registry.

### Phase 2: CHAIN aliases (REQ-ORCH-07)

For each `:>>` CHAIN [redefinition](01-extraction.md#redefinitions-redefinitiondata),
look up the canonical channel that the chain target resolves to, then register
the alias name pointing to the same canonical. Unresolvable aliases log a warning.

```
Redefinition:  total_capex :>> cost_model.total_cost
Alias name:    solar_battery_plant.solar_array.total_capex
Resolves to:   solar_battery_plant__solar_array__cost_model__total_cost
```

### Phase 3: EXPOSE_PURE aliases

Similar to Phase 2, but for [EXPOSE_PURE computed attributes](16-computed-attributes.md)
that expose another calculation's output through a PartUsage. Scoped to the
owning part name (e.g., `SolarArray.total_allocation`).

### Phase 3b: Confirm multi-hop EXPOSE tentatives

A derived attribute that exposes another EXPOSE (a multi-hop chain) arrives from
extraction classified `EXPOSE_CHAIN_TENTATIVE`. Phase 3b (in
`output_registry_builder.py`, part of registry build -- not a backtracker phase)
walks each tentative to a real Phase 1 channel: on success it is reclassified
`EXPOSE_PURE` and the transitive channel is registered; on failure it reverts to
FORMULA (the old behavior). No tentative may survive registry build to a reader
(INV-F raises). Because a revert can re-introduce a FORMULA after the Step-4.5
removal already ran, FORMULA removal re-runs at Step 5.6 (INV-G).

### Phase 4: Transitive design attribute aliases

Some design attributes have default values that reference other outputs
(e.g., `p_net = net_electric.p_net`). Phase 4 registers `DesignPart.p_net`
as an alias for whatever `net_electric.p_net` already resolved to.

### After construction

```python
registry.scoped_lookup(ScopedKey("solar_battery_plant.solar_array.cost_model.total_cost"))
# => CanonicalChannel("solar_battery_plant__solar_array__cost_model__total_cost")

registry.alias_lookup(ScopedKey("solar_battery_plant.solar_array.total_capex"))
# => CanonicalChannel("solar_battery_plant__solar_array__cost_model__total_cost")  (via Phase 2 alias)
```

Both lookups resolve to the same canonical channel via type-directed dispatch.
See [10-output-registry](10-output-registry.md) for the full type system.

## Virtual binding rewriting

A calc usage is "virtual" when it was instantiated by [template expansion](12-virtual-binding-rewrite.md).
A PartDef acts as the template; each PartUsage creates a virtual copy.
The problem: virtual copies carry the template's generic bindings, which
reference template-level attributes. These must be rewritten for the
design instance. See [12-virtual-binding-rewrite](12-virtual-binding-rewrite.md) for full detail.

`_rewrite_virtual_bindings()` builds an override index from
`hierarchy_data.design_overrides`, keyed by `(parent_path, leaf_attribute)`.
Then for each non-template calc usage, it matches bindings against the index:

```
BEFORE (template binding):
  binding.source_path = "SolarBatteryLibrary::Solar_Array::panel_cost"
  binding.binding_type = REFERENCE

AFTER (LITERAL override -- design sets a concrete value):
  binding.binding_type = LITERAL
  binding.literal_value = 250.0

AFTER (CHAIN override -- design redirects to another output):
  binding.source_path = "cost_model.adjusted_cost"
```

A `part_usage.attr` CHAIN binding with no direct override can also be rewritten
through a retyped part usage's specialized-def `:>>` chain
(`_rewrite_specialized_chain` in `pipeline_builder.py`, REQ-VBR-10). Precedence:
usage override > specialized-def `:>>` > base def. See
[12-virtual-binding-rewrite](12-virtual-binding-rewrite.md).

This mutation happens in place (REQ-ORCH-02), which is why Step 3.5
must run before any downstream step that reads bindings.

## Aggregation scoping

SysML models define aggregation expressions at the PartDef level (see
[01-extraction](01-extraction.md#aggregation-data-sumterm-singletonterm-localterm)):

```sysml
part def Solar_Array {
    attribute total_capex = sum(cost_model.total_cost);
}
```

But the pipeline operates on concrete design instances, not abstract
PartDefs. `_scope_aggregation_expressions()` maps each PartDef-level
aggregation to its design instances (REQ-ORCH-05) by scanning virtual
calc usages: if a usage's `owning_part_def_qn` matches the aggregation's
owning PartDef, its parent path is an instance.

```
PartDef:   SolarBatteryLibrary__Solar_Array
Instance:  SolarBatteryDesign__solar_battery_plant__solar_array

=> ScopedAggregationData(expression=<sum>, instance_path="...solar_array")
```

CHAIN alias construction (`_build_chain_aliases()`) uses the same
instance-discovery mechanism: for each `:>>` CHAIN [redefinition](01-extraction.md#redefinitions-redefinitiondata)
on a PartDef, it finds the instance paths and produces scoped `ChannelAlias`
objects that Phase 2 of the [registry builder](#build_output_registry----the-4-phase-lookup-table) consumes.
See [13-aggregation-scoping](13-aggregation-scoping.md) for full detail.

## PipelineContext

> A `PipelineContext` can also be rebuilt from a captured JSON snapshot instead of
> live extraction (`build_pipeline_context_from_snapshot`), enabling license-free
> `generate --from-snapshot`. See [27-snapshot-generation](27-snapshot-generation.md).

The `PipelineContext` dataclass carries all pipeline state. Key fields:

| Field | Type | Source step |
|-------|------|-------------|
| `calc_defs` | `list[CalculationDefinitionData]` | Step 2 |
| `calc_usages` | `list[CalcUsageData]` | Step 3 (mutated by 3.5 and 5.56) |
| `design_attributes` | `dict[Path, list[DesignAttributeData]]` | Step 4 (mutated by 4.5 and 5.6) |
| `computed_attributes` | `list[ComputedAttributeData]` | Step 4.5 |
| `output_registry` | `OutputRegistry` | Step 5.5 |
| `backtracking_result` | `BacktrackingResult` | Step 6 |
| `compilation_results` | `dict[str, CalcDefCompilationResult]` | Step 6.5 |
| `computation_graph` | [ComputationGraph](09-data-models.md#resolution-models) | Step 7 |

See [09-data-models](09-data-models.md) for full field definitions.

## Package structure

```
orchestration/
    pipeline_builder.py          -- build_pipeline_context() + helpers
                                    Steps 1-7 coordination, no business logic
    output_registry_builder.py   -- build_output_registry()
                                    4-phase registration protocol
    pipeline_context.py          -- PipelineContext dataclass
    snapshot_context.py          -- build_pipeline_context_from_snapshot()
                                    same PipelineContext, rebuilt from a
                                    captured snapshot (no live extraction)
```

Supporting functions (`_rewrite_virtual_bindings`, `_scope_aggregation_expressions`,
`_build_chain_aliases`, `find_instance_paths_for_partdef`) live in
`pipeline_builder.py` as data-preparation helpers called exclusively by
the pipeline builder.

## Related Documents

- **Upstream**: [00-pipeline-overview](00-pipeline-overview.md) -- Steps 1-7 overview, [01-extraction](01-extraction.md) -- provides calc defs, usages, hierarchy data
- **Downstream**: [03-resolution-overview](03-resolution-overview.md) (consumes PipelineContext), [08-generation](08-generation.md) (consumes ComputationGraph)
- **Registry**: [10-output-registry](10-output-registry.md) -- 4-phase protocol detail, [15-naming-conventions](15-naming-conventions.md) -- key formats
- **Sub-processes**: [12-virtual-binding-rewrite](12-virtual-binding-rewrite.md), [13-aggregation-scoping](13-aggregation-scoping.md), [16-computed-attributes](16-computed-attributes.md), [17-parameter-group-deriver](17-parameter-group-deriver.md)
- **Data models**: [09-data-models](09-data-models.md) -- PipelineContext, ComputationGraph, all extraction types
