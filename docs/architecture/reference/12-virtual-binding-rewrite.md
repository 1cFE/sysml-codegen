# 12 - Virtual Binding Rewriting

> **Status: historical.** Template expansion and `_rewrite_virtual_bindings()` lived in
> `orchestration/pipeline_builder.py`, **deleted** by the Item 7 retirement (2026-08-12,
> `19072ad` / `82c7951` / `882fc8d` / `3071fba`).
>
> **The shipped route has no virtual copies to rewrite.** A calc declared on a part def is
> instantiated per occurrence by the elaborator, and each occurrence's values come from its own
> value site. There is no template binding carrying a generic reference that a later pass has
> to redirect, so there is no in-place mutation step and no ordering constraint around it.
>
> Everything below is retained as the record of the deleted design. It is accurate about the
> code that was removed and is **not a description of what the product does**. For that, read
> [00-pipeline-overview](00-pipeline-overview.md).

## What Are "Virtual" Calc Usages?

A SysML library PartDef (e.g., `Solar_Array`) owns calculation usages that reference
template-level attributes. When a design PartDef (e.g., `SolarBatteryDesign`) instantiates
that library part via a PartUsage, the pipeline creates **virtual** copies of those calc
usages scoped to the design instance. Each virtual [`CalcUsageData`](09-data-models.md#extraction-models)
carries:

- `is_template = False` (the original library copy has `is_template = True`)
- `owning_part_def_qn` pointing back to the library PartDef
- `qualified_name` scoped to the design instance
  (e.g., `SolarBatteryDesign__solar_array__calc_cost`)

Template copies (`is_template = True`) are excluded from the pipeline entirely. Only
virtual (non-template) copies become pipeline modules.

## Requirements

| ID | Requirement | Verified by |
|----|-------------|-------------|
| REQ-VBR-01 | Override index SHALL be keyed by `(full_parent_path, leaf_attribute_name)` | `override_index: dict[tuple[str, str], RedefinitionData]` in `_rewrite_virtual_bindings` (Phase 1a) |
| REQ-VBR-02 | Deep-path overrides SHALL join intermediate `target_path` segments with `__` to form `full_parent` | `f"{override.owning_part_qn}__{intermediate}"` in the deep-path branch of `_rewrite_virtual_bindings` Phase 1a |
| REQ-VBR-03 | LITERAL override SHALL set `binding_type=LITERAL`, copy `literal_value`, clear `source_path=None` | Three mutations in the tier-1 LITERAL branch of `_rewrite_virtual_bindings` |
| REQ-VBR-04 | CHAIN override SHALL replace `source_path` with the redefinition's `source_path` | `binding.source_path = matched.source_path` in the tier-1 CHAIN branch of `_rewrite_virtual_bindings` |
| REQ-VBR-05 | Template copies (`is_template=True`) SHALL be skipped during rewriting | `if usage.is_template: continue` in `_rewrite_virtual_bindings` Phase 2 |
| REQ-VBR-06 | Bindings already LITERAL or with no `source_path` SHALL be skipped (no double-rewrite) | The LITERAL / empty-`source_path` guards at the top of the `_rewrite_virtual_bindings` binding loop |
| REQ-VBR-07 | Rewriting SHALL complete BEFORE any downstream processing (Step 3.5 ordering) | Called from `_extract_hierarchy_and_rewrite_bindings` (Step 3.5) in `build_pipeline_context()`, before Steps 4-7 |
| REQ-VBR-08 | `_create_virtual_calc_usage` SHALL shallow-copy each `BindingInfo` (`[copy.copy(b) for b in template.bindings]`) so no two virtual instances share a binding object; the rewrite mutates only scalar fields, so a shallow copy suffices | `test_virtual_binding_rewrite.py::test_rewrite_respects_instance_boundary_for_divergent_siblings` — two instances given different overrides read 50.0 and 100.0 independently |
| REQ-VBR-09 | `_rewrite_virtual_bindings` SHALL NOT raise on a bare-name `source_path` (no `::`, no `.`); it logs DEBUG and skips the override match | `test_virtual_binding_rewrite.py::test_rewrite_skips_bare_name_source_path_without_raising` — non-empty index, bare-name binding, no raise, DEBUG logged, binding unchanged |
| REQ-VBR-10 | A `part_usage.attr` CHAIN binding whose retyped part usage's specialized def carries a `:>> attr = calc.output` redefinition SHALL be rewritten through it (tier 2 of the three-tier merge, `_rewrite_specialized_chain`). A self-named binding (`in x = x`, resolved to a full-QN self-reference) whose outer same-named EXPOSE resolves to a real channel SHALL be rewritten to that upstream channel (mechanism D, `_rescue_self_named_bindings`, a separate step); no resolvable upstream → left as-is | Specialized-def resolver: `test_spec_chain_channel.py::test_cost_per_joule_wired_to_gamma`; self-named rescue: `test_self_named_rescue.py::test_self_named_binding_rescued_to_upstream` |
| REQ-VBR-11 | The specialized-def type-select SHALL try the consumer INSTANCE's path key (`usage.qualified_name.rsplit("__",1)[0]`) before the declaring-def key, so a two-level specialization (retype on a part usage, consumer calc on the base def) resolves against the instance's own retype | `test_spec_chain_twolevel.py::test_cost_per_joule_wired_to_gamma` |

## Why Binding Rewriting Is Needed

Template bindings reference template-level attributes using SysML qualified names:

```
source_path = "Lib::Solar_Array::wattage"
```

But at the design level, a `:>>` redefinition may override that attribute:

```sysml
part redefines solar_array : Solar_Array {
    :>> wattage = 400.0;              // LITERAL override
    :>> efficiency = tracker.eta;     // CHAIN override
}
```

(On a *plain* typed usage — `part solar_array : Solar_Array { ... }` — only the LITERAL
member override would be captured; a plain-usage CHAIN/EXPRESSION override is filtered
out at extraction, REQ-HR-08. The `part redefines` shape keeps all RHS types.)

Without rewriting, the virtual CalcUsage would still look up `Lib::Solar_Array::wattage`,
missing the design-specific value `400.0`. The rewrite step patches each virtual
CalcUsage's [`BindingInfo`](09-data-models.md#extraction-models) objects **in place** so
downstream steps ([backtracking](11-analysis-backtracker.md),
[graph building](07-graph-assembly.md)) see the design-intent values.

## Implementation: `_rewrite_virtual_bindings()`

**File:** `src/sysml_codegen/orchestration/pipeline_builder.py`.

### Phase 1 -- Build the Override Index

The function iterates `hierarchy_data.design_overrides` (a `list[`[`RedefinitionData`](09-data-models.md#extraction-models)`]`)
and builds a lookup dict:

```python
override_index: dict[tuple[str, str], RedefinitionData]
```

The key is `(full_target_parent_path, leaf_attribute_name)`.

**Deep-path overrides** (`redef.is_deep_path = True`, e.g., `:>> pv_module.wattage = 400`):
- `target_path = ["pv_module", "wattage"]`
- Intermediate segments joined: `"pv_module"` (all but last)
- `full_parent = f"{owning_part_qn}__pv_module"`
- `leaf_attr = "wattage"`

**Flat overrides** (`is_deep_path = False`, e.g., `:>> efficiency = 0.22`):
- `full_parent = owning_part_qn`
- `leaf_attr = attribute_name`

This is Phase 1a (tier 1). Phase 1b builds a second index over
`hierarchy_data.redefinitions` for the tier-2 specialized-chain rewrite (see the
three-tier merge section below). If **both** indexes are empty, the function returns
`0` immediately.

### Phase 2 -- Match and Rewrite Bindings

For each `CalcUsageData` where `is_template = False`:

1. Extract `parent_path` from `usage.qualified_name.rsplit("__", 1)[0]`
2. Skip bindings that are already `LITERAL` or have no `source_path`
3. Extract the leaf name from `binding.source_path`:
   - SysML QN (`"::"` separator): `"Lib::Solar_Array::wattage"` -> leaf `"wattage"`
   - Dotted path (`"."` separator): `"tracker.eta"` -> leaf `"eta"`
   - Bare name (no `::`, no `.`): a self-named binding like `in availability = availability`.
     The binding is **skipped with a DEBUG log** (REQ-VBR-09) — no deep-path key can
     match a bare leaf, so skipping loses no rewrite, and resolving it to the outer
     attribute is Item 10's per-instance rewrite. Before REQ-VBR-09 this raised
     `ValueError`; that raise was unreachable only while the index was empty for these
     models. The relaxed capture guard (REQ-HR-08) can now make the index non-empty, so
     the branch is reachable and is made crash-safe. No committed fixture reaches it —
     the reachable bindings in `unresolvable_attr_probe` / ife_plant are all
     `::`-qualified (they take the `::` branch), and `self_named_binding_trap`'s
     self-named binding arrives as a full `::`-QN (mechanism D, below), so it takes
     the `::` branch too — the guarantee holds by branch, not by empty index; the
     constructed unit test is the coverage.
4. Lookup `(parent_path, leaf)` in the override index

### The Three Mutation Cases

| Case | Condition | Mutations | Downstream effect |
|------|-----------|-----------|-------------------|
| **LITERAL override** | `matched.redefinition_type == RedefinitionType.LITERAL` | `binding_type = LITERAL`, `literal_value = matched.literal_value`, `source_path = None` | Becomes [DESIGN_ATTRIBUTE entry point](06-entry-point-classifier.md) |
| **CHAIN override** | `matched.redefinition_type == RedefinitionType.CHAIN` | `source_path = matched.source_path` (e.g., `"tracker.eta"`) | Resolved via [OutputRegistry](10-output-registry.md) as MODULE_OUTPUT |
| **No match** | Key not in override index | Falls to tier 2 (`_rewrite_specialized_chain`, next section); if that also declines, binding unchanged | Tier-2 rewrite, or original template binding used |

## Three-Tier Merge: Specialized-Def `:>>` Precedence (REQ-VBR-10, REQ-VBR-11)

The usage-override cases above are tier 1. When no usage override matches, a second
tier resolves a `part_usage.attr` binding through the *type* the part usage was retyped
to. The full precedence is:

**usage override (tier 1) > specialized-def `:>>` (tier 2) > base def (fall-through).**

Tier 2 lives in `_rewrite_specialized_chain`. Its two inputs come from the hierarchy
resolver ([25-hierarchy-resolver](25-hierarchy-resolver.md)):

- A **second index** over `hierarchy_data.redefinitions` keyed by the *specializing*
  def QN (`(owning_part_qn, attribute_name) → RedefinitionData`), distinct from the
  tier-1 `override_index`.
- `usage_type_map`, which says what type a part usage resolves to per scope.

**The rewrite.** For a binding `driver.cost_per_joule`, split into part usage `driver`
and attribute `cost_per_joule`. Type-select `driver` to its retyped def (`'HIF Driver'`).
If that def redefines `cost_per_joule :>> meier_cost.gamma`, rewrite the binding to
`driver.meier_cost.gamma`. The chain dispatch then wires it to the gamma channel (the
gamma → lcoe edge, SC-2). A base def whose attribute carries no redefinition falls
through unchanged — tier 3. The hop is single and non-recursive.

**Instance-first type-select (REQ-VBR-11).** The type-select tries two keys, in order:

```python
instance_path = usage.qualified_name.rsplit("__", 1)[0]
target_def = usage_type_map.get((instance_path, part_usage)) \
    or usage_type_map.get((owning_def, part_usage))
```

The **instance-path key first** handles two-level specialization: the fusion-tea shape
retypes `driver` on a part *usage* (`part hif_plant : 'IFE Power Plant' { part :>>
driver : 'HIF Driver' }`) while the consumer `lcoe_calc` is declared on the *base* def.
Keying only on the consumer's declaring def would see the base type and miss the retype.
The instance-path key (`TwoLevelDesign__hif_plant`) reaches the usage-level retype that
`_index_usage_level_retypes` indexed (REQ-LVP-09,
[25-hierarchy-resolver](25-hierarchy-resolver.md)). The **declaring-def key** is the
fall-through for the single-level shape (`spec_chain_channel`), where consumer and retype
sit on the same def.

## Self-Named Binding Rescue — Mechanism D (REQ-VBR-10)

A self-named binding `in throughput = throughput` does **not** reach `_rewrite_virtual_bindings`
as a bare name. Extraction resolves it to a full REFERENCE QN pointing at the consuming
calc's own parameter (e.g. `RescueLib::'Rescue Plant'::sink_calc::throughput`) — the same
shape `self_named_binding_trap` pins. So the rescue is a **separate step**,
`_rescue_self_named_bindings`, not a branch of the rewrite (D-E deviation, faithful to the
design's "may land as a pre-resolution rewrite").

It runs at **Step 5.56**, after the scoped-alias registry is populated (so "resolves to a
real channel" is a real lookup) and before the backtracker reads bindings. It detects the
self-reference — the binding QN's parent segment equals the consuming usage's own short
name — and, when an outer same-named EXPOSE resolves to a real channel (a `_scoped_alias`
hit), rewrites the binding to the instance-scoped `{instance}.{leaf}` CHAIN. The chain
dispatch (Step 1c) then wires it to the upstream `source_calc` channel. No resolvable
outer EXPOSE → the binding is left as-is: that is the genuine modeling error
`self_named_binding_trap` pins. This keeps REQ-VBR-10 as mechanism D's sole home; only the
implementation site is a dedicated function.

## Concrete Before/After Example

**Setup:** Library PartDef `Lib__Solar_Array` owns `calc_cost` with two inputs.
Design PartDef `SolarBatteryDesign` instantiates it as `solar_array` with overrides:

```sysml
part redefines solar_array : Solar_Array {
    :>> wattage = 400.0;
    :>> efficiency = tracker.eta;
}
```

This produces two `design_overrides` — flat member overrides owned by the
`solar_array` usage (a `part redefines` usage, so both RHS types are kept,
REQ-HR-08):
- `RedefinitionData(owning_part_qn="SolarBatteryDesign__solar_array", attribute_name="wattage", is_deep_path=False, redefinition_type=LITERAL, literal_value=400.0)`
- `RedefinitionData(owning_part_qn="SolarBatteryDesign__solar_array", attribute_name="efficiency", is_deep_path=False, redefinition_type=CHAIN, source_path="tracker.eta")`

**Override index after Phase 1** (flat key: `(owning_part_qn, attribute_name)`):
```
("SolarBatteryDesign__solar_array", "wattage")   -> LITERAL(400.0)
("SolarBatteryDesign__solar_array", "efficiency") -> CHAIN("tracker.eta")
```

**Virtual CalcUsage before rewrite:**
```python
CalcUsageData(
    qualified_name="SolarBatteryDesign__solar_array__calc_cost",
    is_template=False,
    owning_part_def_qn="Lib__Solar_Array",
    bindings=[
        BindingInfo(param_name="wattage",   source_path="Lib::Solar_Array::wattage",
                    binding_type=BindingType.REFERENCE, literal_value=None),
        BindingInfo(param_name="efficiency", source_path="Lib::Solar_Array::efficiency",
                    binding_type=BindingType.REFERENCE, literal_value=None),
    ],
)
```

**After rewrite (in-place mutation):**
```python
CalcUsageData(
    qualified_name="SolarBatteryDesign__solar_array__calc_cost",
    is_template=False,
    owning_part_def_qn="Lib__Solar_Array",
    bindings=[
        BindingInfo(param_name="wattage",   source_path=None,
                    binding_type=BindingType.LITERAL, literal_value=400.0),
        BindingInfo(param_name="efficiency", source_path="tracker.eta",
                    binding_type=BindingType.REFERENCE, literal_value=None),
    ],
)
```

The `wattage` binding flipped from REFERENCE to LITERAL with value `400.0`.
The `efficiency` binding kept its type but `source_path` was rewritten to `"tracker.eta"`.

## Ordering Constraint: In-Place Mutation Before Downstream Steps

`_rewrite_virtual_bindings()` is called inside `_extract_hierarchy_and_rewrite_bindings()`
at **Step 3.5** of [`build_pipeline_context()`](00-pipeline-overview.md), which runs **before**:

- Step 4 -- `extract_design_attributes()` ([parameter group derivation](17-parameter-group-deriver.md))
- Step 5.5 -- [`build_output_registry()`](10-output-registry.md) (channel registration, including the Phase 3b confirm pass)
- Step 5.7 -- `ParameterGroupDeriver` construction (moved after the registry's confirm pass, INV-G)
- Step 6 -- [`DependencyBacktracker.find_required_modules()`](11-analysis-backtracker.md) (dependency analysis)
- Step 7 -- [`build_computation_graph()`](07-graph-assembly.md) (graph assembly)

The mutations are in-place on the shared `calc_usages` list, so every downstream
consumer automatically sees the rewritten bindings. No return value carries the
modified list -- the same list object is passed through the entire pipeline.

### Per-Instance Binding Isolation (REQ-VBR-08)

Because the rewrite mutates `BindingInfo` **in place**, sibling virtual instances
minted from one template must not share the same `BindingInfo` objects. When a
multiplicity part like `widget [3]` produces multiple virtual instances and their
deep-path overrides diverge, a shared object would let the first instance's rewrite
(to LITERAL) make the rewrite skip the second (already-LITERAL), so the second reads
the first's value. `_create_virtual_calc_usage` (`extraction/usage_extractor.py`)
therefore mints each instance's bindings as `[copy.copy(b) for b in template.bindings]`
— a **shallow** copy per binding. The rewrite reassigns only scalar fields
(`binding_type`, `literal_value`, `source_path`), so each instance gets independent
scalars while the read-only raw AST-node references (`source_instance_elem`,
`expression_ast`) stay shared. `copy.deepcopy` is deliberately avoided — it would
recurse into the SysIDE parse subgraph (slow, possibly cyclic).

## Key Data Model References

All models fully defined in [09-data-models](09-data-models.md).

| Model | Key Fields Used Here |
|-------|---------------------|
| [`CalcUsageData`](09-data-models.md#extraction-models) | `.is_template`, `.owning_part_def_qn`, `.qualified_name`, `.bindings` |
| [`BindingInfo`](09-data-models.md#extraction-models) | `.param_name`, `.source_path`, `.binding_type`, `.literal_value` |
| [`RedefinitionData`](09-data-models.md#extraction-models) | `.owning_part_qn`, `.attribute_name`, `.redefinition_type`, `.target_path`, `.is_deep_path`, `.literal_value`, `.source_path` |
| [`RedefinitionType`](09-data-models.md#extraction-models) | `LITERAL`, `CHAIN`, `EXPRESSION` |
| [`BindingType`](09-data-models.md#extraction-models) | `CHAIN`, `REFERENCE`, `LITERAL`, `EXPRESSION`, `UNBOUND` |
| [`HierarchyExtractionResult`](09-data-models.md#extraction-models) | `.design_overrides` (list of `RedefinitionData`) |

## Related Documents

- **Upstream**: [01-extraction](01-extraction.md) — produces `CalcUsageData` and `RedefinitionData`, [02-orchestration](02-orchestration.md) — calls rewriting at Step 3.5
- **Architecture**: [00-pipeline-overview](00-pipeline-overview.md) — Step 3.5 placement in pipeline, [24-dual-resolution-architecture](24-dual-resolution-architecture.md) — why rewriting feeds both resolution paths
- **Downstream**: [11-analysis-backtracker](11-analysis-backtracker.md) — DFS sees rewritten bindings, [10-output-registry](10-output-registry.md) — CHAIN rewrites become registry lookups, [13-aggregation-scoping](13-aggregation-scoping.md) — scoped aggregations also use rewritten data
- **Cross-cutting**: [06-entry-point-classifier](06-entry-point-classifier.md) — LITERAL rewrites become entry points, [18-literal-value-propagation](18-literal-value-propagation.md) — literal defaults for entry points
- **Sibling (Item 2)**: [25-hierarchy-resolver §Supplied-Value Materializer](25-hierarchy-resolver.md#supplied-value-materializer-req-svm-01-04) — REQ-SVM carries plain subsystem-attr literals to plant-calc inputs. Distinct from REQ-VBR-03: VBR-03 rewrites a design-override literal per consumer (`usage_qn__param`); the materializer keys by source QN and collapses across differently-named consumers
- **Data models**: [09-data-models](09-data-models.md) — `CalcUsageData`, `BindingInfo`, `RedefinitionData`
