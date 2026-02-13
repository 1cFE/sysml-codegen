# Research: SysIDE AST Assumption Spike Results

**Date:** 2026-02-13
**Models tested:** solar_battery, chain_spike, e2e_attr_expr, catf_mfe
**Scripts:** `scripts/spikes/spike_template_binding_format.py`, `spike_virtual_instance_keys.py`, `spike_expose_pure_chain.py`, `spike_bare_name_collisions.py`
**Purpose:** Empirically verify SysIDE parser assumptions that block OutputRegistry design finalization

---

## Spike 1 Findings: Template Binding source_path Format

**Question:** What `source_path` format does SysIDE produce for CalcUsage bindings?

### Data

| Model | Total bindings | BARE | DOTTED | SYSML_QN | LITERAL | EXPRESSION |
|-------|---------------|------|--------|----------|---------|------------|
| solar_battery | 62 | **0** | 8 | 50 | 4 | 0 |
| chain_spike | 12 | **0** | 6 | 6 | 0 | 0 |
| e2e_attr_expr | 20 | **0** | 4 | 16 | 0 | 0 |

### Format Rules (100% consistent across all models)

| BindingType | source_path format | Example |
|-------------|-------------------|---------|
| REFERENCE | **SYSML_QN** | `SolarBatteryLibrary::'PV Module'::cost_model::wattage` |
| CHAIN | **DOTTED** | `annualized_financial.annualized_capital_cost` |
| LITERAL | N/A (literal_value used) | `25.0` |

- **BARE format was never observed.** Zero instances across 94 bindings in 3 models.
- Template bindings (expand_templates=False) use the same SYSML_QN format as concrete bindings.
- Virtual CalcUsages (expand_templates=True) inherit the original source_path unchanged.

### Design Implication

The virtual binding rewrite mechanism in Step 3.5E that handles bare-name source_paths
is likely dead code. SysIDE always produces SYSML_QN for REFERENCE and DOTTED for CHAIN.
The OutputRegistry needs to handle exactly two source_path formats:

1. **SYSML_QN** (`Namespace::Part::usage::param`) -- for REFERENCE bindings (entry points)
2. **DOTTED** (`instance.output`) -- for CHAIN bindings (module-to-module wiring)

---

## Spike 2 Findings: Virtual Instance Names and Output Keys

**Question:** For virtual CalcUsages, what lookup keys do downstream bindings use?

### Data

| Model | CHAIN bindings | Match type | Mismatches |
|-------|---------------|------------|------------|
| solar_battery | 4 | All SHORT_KEY (concrete producers) | **0** |
| e2e_attr_expr | 2 | All SHORT_KEY (concrete producers) | **0** |

### Key Observations

1. **All CHAIN bindings use short instance names** in source_path (e.g., `annualized_financial.annualized_capital_cost`, not the qualified form).

2. **No CHAIN binding targets a virtual CalcUsage output.** Virtual CalcUsages (the `cost_model` instances from template expansion) are leaf nodes -- their outputs are consumed by aggregation expressions (`:>>` aliases), not by direct CHAIN bindings from other CalcUsages.

3. **Short keys collide massively for virtual CalcUsages.** In solar_battery, 9 virtual CalcUsages all produce `cost_model.total_cost` as their short key. Only the full qualified key (`SolarBatteryDesign__solar_battery_plant__solar_array__pv_module__cost_model.total_cost`) is unique.

### Design Implication

The OutputRegistry must register both short and full keys for virtual CalcUsages, but the
short-key collision is irrelevant for CHAIN resolution because no CHAIN binding references
virtual CalcUsage outputs. Virtual outputs flow through aggregation, which uses a different
resolution path (`:>>` redefinitions, not CHAIN source_paths).

The concern in Issue 1 about virtual instance_name format is real but narrower than feared:
it affects aggregation scoping and EXPOSE_PURE alias resolution, not direct CHAIN wiring.

---

## Spike 3 Findings: EXPOSE_PURE Resolution Chain

**Question:** Can we trace the Bug 2 resolution chain with actual data?

### e2e_attr_expr: financial.total_capex Chain

```
Step A: source_path = "E2EAttrExprDesign::e2e_plant::financial::total_capex" (SYSML_QN)
Step B: computed_attr_index -> FOUND via bare name "total_capex"
        classification: EXPOSE_PURE
        expression_text: ".(component_cost)"        <-- NOT a dotted path!
        references[0]: name="total_cost"  qn="E2EAttrExprLibrary::ComponentCostCalc::total_cost"
        references[1]: name="component_cost"  qn="E2EAttrExprDesign::e2e_plant::component_cost"
Step C: EXPOSE_PURE target from expression_text: ".(component_cost)" -- UNPARSEABLE
Step D: design_attr_binding_index["e2e_plant.total_capex"] = "component_cost.total_cost"
Step E: output_catalog["component_cost.total_cost"] = "component_cost__total_cost" -- FOUND
Step F: Direct registry.resolve("financial.total_capex") = None -- FAILS
```

### Critical Discovery: expression_text is NOT a dotted path

The design assumed `expression_text = "component_cost.total_cost"` for EXPOSE_PURE attributes.
SysIDE actually produces `expression_text = ".(component_cost)"` -- the raw FeatureChainExpression
AST text reconstruction, which is not a parseable dotted key.

**The actual target information is in the `references` field:**
- `references[0].name = "total_cost"` (the output attribute name)
- `references[1].name = "component_cost"` (the CalcUsage instance name)
- Combined: `component_cost.total_cost` -- which IS in the output catalog

### Resolution Paths That Work

| Path | Key used | Result |
|------|----------|--------|
| design_attr_binding_index | `e2e_plant.total_capex` -> `component_cost.total_cost` | Resolves to `component_cost__total_cost` |
| EXPOSE_PURE references | `component_cost` + `total_cost` -> `component_cost.total_cost` | Resolves to `component_cost__total_cost` |
| Direct output catalog | `component_cost.total_cost` | Resolves to `component_cost__total_cost` |

### solar_battery: annualized_financial.total_capex Chain

This binding's source_path is `SolarBatteryLibrary::'Solar Battery Plant'::capital_cost`
-- a SYSML_QN pointing to a PartDef attribute. This resolves through aggregation (`:>>`
aliases), not EXPOSE_PURE. The EXPOSE_PURE in solar_battery is `misc_hardware_cost` on
`Solar_Array`, which points to `allocation_model.total_allocation`.

### Design Implications

1. **OutputRegistry MUST NOT use `expression_text` for EXPOSE_PURE canonical targets.**
   Must use the `references` field to reconstruct `{instance_name}.{output_name}`.

2. **Two viable resolution strategies for EXPOSE_PURE:**
   - **Option A (references-based):** At alias registration time, extract instance and output
     names from `ComputedAttributeData.references` and register as alias.
   - **Option B (design_attr_binding_index):** The existing two-hop path works when the
     index key format matches. The key is `parent_part.attr_name`, and the target is the
     dotted path from `default_value`.

3. **Option A is more reliable** because it doesn't depend on `DesignAttributeData`
   having the correct `parent_part` (solar_battery showed a broken key with empty parent).

---

## Spike 4 Findings: Bare-Name Collisions

**Question:** How many output names collide across CalcUsages?

### Data

| Model | N (total outputs) | M (unique names) | K (ambiguous) | Bare-name refs |
|-------|-------------------|-------------------|---------------|----------------|
| solar_battery | 56 | 16 | **5** | **0** |
| catf_mfe | 46 | 19 | **5** | **0** |

### Ambiguous Names

**solar_battery:** `total_cost`, `material_cost`, `fab_cost`, `install_cost`, `idiot_index` -- each produced by 9 virtual CalcUsages (all `cost_model` template instances).

**catf_mfe:** `volume` (13 producers), `a` (13 producers), `area` (2), `p_net` (2), `pump_power` (2).

### Critical Finding: Zero Bare-Name References

**No binding source_path in any tested model uses a bare output name.** All 94 bindings
across 4 models use either DOTTED (`instance.output`) or SYSML_QN (`Namespace::part::attr`)
format. The bare-name collision problem is entirely theoretical.

### Design Implication

**Skip bare-name registration entirely.** It adds complexity (collision detection, removal
logic) to solve a problem that doesn't exist in practice. The OutputRegistry only needs:
- Dotted keys: `instance_name.output_name`
- Full qualified keys: `qualified_name.output_name` (for virtual CalcUsages)
- SysML QN normalization: `Namespace::Part::attr` -> dotted lookup

---

## Design Comment Resolutions

| Comment Issue | Spike | Finding | Resolution |
|---|---|---|---|
| **Issue 1** (virtual instance_name) | Spike 2 | No CHAIN binding targets virtual outputs. Virtual outputs flow through aggregation. Short-key collisions exist but are irrelevant for CHAIN resolution. | Register both short and full keys. Collision doesn't affect CHAIN wiring. Aggregation scoping handles virtual outputs separately. |
| **Issue 2** (bare-name ambiguity) | Spike 4 | K=5 ambiguous names per model, but **0 bare-name references** in any binding. | **Skip bare-name registration.** No collision handling needed. All bindings use dotted or SysML QN format. |
| **Issue 3** (design attr two-hop) | Spike 3 | design_attr_binding_index works when keys match. EXPOSE_PURE expression_text is NOT a dotted path -- must use `references` field. | Use `references` field to build EXPOSE_PURE aliases. Register as OutputRegistry alias at Phase 3, after CalcUsage outputs are registered. |
| **Issue 7** (probe first) | Spike 1 | SysIDE always produces SYSML_QN for REFERENCE, DOTTED for CHAIN. Zero bare names. | Virtual binding rewrite for bare names is dead code. OutputRegistry handles two formats: SYSML_QN (normalize to dotted) and DOTTED (direct lookup). |

### Issues NOT directly addressed by spikes (but informed by results)

| Comment Issue | Informed by | Note |
|---|---|---|
| **Issue 4** (alias registration order) | Spike 3 | Confirmed: EXPOSE_PURE aliases must resolve against already-registered CalcUsage outputs. Phase ordering: (1) CalcUsage outputs, (2) `:>>` CHAIN aliases, (3) EXPOSE_PURE aliases. |
| **Issue 5** (aggregation scoping hidden) | Spike 2 | Confirmed: virtual CalcUsage outputs are consumed via aggregation, not CHAIN. Scoping must run before OutputRegistry construction. |
| **Issue 6** (AggregationDecomposer) | N/A | No new data. Recommendation stands: drop the Protocol, keep direct sum() code. |
| **Issue 8** (no spike/test plan) | All | These spikes ARE the test plan. Results provide the empirical ground truth for design finalization. |

---

## Key Takeaways for 08_algorithm_revised.md Update

1. **OutputRegistry key formats:** Only DOTTED and SysML QN. No bare names.
2. **SysML QN normalization:** Extract `parts[-2].parts[-1]` to produce dotted key.
3. **EXPOSE_PURE alias source:** Use `ComputedAttributeData.references`, not `expression_text`.
4. **Virtual CalcUsage outputs:** Consumed via aggregation, not CHAIN. Short-key collision is a non-issue for direct wiring.
5. **Registration phases:** (1) CalcUsage + aggregation + FORMULA outputs, (2) `:>>` aliases, (3) EXPOSE_PURE aliases built from `references`.
6. **Bare-name registration:** Skip entirely.
