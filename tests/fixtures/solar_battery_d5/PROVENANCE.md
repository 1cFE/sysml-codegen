# Provenance — `solar_battery_d5`

Authored 2026-08-11 for recovery plan **Gate 4C part 6**
(`.project/active/cutover-recovery/plan.md`), as the migrated variant of
`solar_battery_model` — corpus row 33, a ratified `expected-collapse` refused with
24× `SI_SELF_BINDING`.

**Not a corpus fixture.** It joins no ledger and no 37-path corpus run. `solar_battery_model`
is untouched and still carries its refused shape.

**The exact route accepts this model**: 77 modules, 199 entry points, 221 output aliases —
the full twelve-assembly costing hierarchy. This is the scale-shaped evidence the recovery
was missing.

## Stage 1 — the D-5 rename

21 formals renamed to `<name>_in` inside their `calc def`s and on the left side of every
binding, across `design.sysml` and `library.sysml`: `capacity_kwh`, `chemistry_factor`,
`circuit_count`, `discount_rate`, `efficiency`, `fuel_consumption`, `fuel_unit_cost`,
`n_mod`, `om_rate_per_kw_year`, `p_net_kw`, `p_net_mw`, `pack_count`, `panel_count`,
`plant_availability`, `plant_lifetime`, `power_rating`, `string_count`,
`system_capacity_kw`, `tilt_angle`, `wattage`, `yearly_inflation`.

## Stage 2 — the aggregation split, and why it is enumerated

With the self-bindings gone, projection refused with `SI_RENDERING_COLLISION`. That refusal
is **ratified correct behaviour (S4 ruling, 2026-08-11)**: the exact route names an
expression parameter after the last member of a reference and drops the qualifier, so
`sum(pv_module.raw_material_cost) + sum(inverter.raw_material_cost)` renders both terms
`raw_material_cost`. The modelling requirement — one named term per aggregation — is carried
to the **Gate 4D documentation subject list**, and `tests/fixtures/costed_cart_d5` is the
worked example.

A shape change cannot be proved by the strip check that proves stage 1: no suffix removal
recovers an original from a model with different attributes. **What replaces byte-identity is
an enumerated difference.** Every added attribute below is derived from the original by one
deterministic rule in `scripts/make_d5_variant.py` — a term that names a reference path gets
an attribute called after that path, flattened — and `strip_check` undoes exactly this list
before comparing bytes. An edit the list does not name survives the undo and fails.

**16 rollups rewritten, 49 named intermediates added.**

| # | metric | named intermediates (each `= ` its original term) |
|---:|---|---|
| 1 | `capital_cost` | `pv_module_capital_cost`, `inverter_capital_cost`, `array_bos_capital_cost` |
| 2 | `raw_material_cost` | `pv_module_raw_material_cost`, `inverter_raw_material_cost`, `array_bos_raw_material_cost`, `allocation_model_material_portion` |
| 3 | `fabrication_cost` | `pv_module_fabrication_cost`, `inverter_fabrication_cost`, `array_bos_fabrication_cost` |
| 4 | `installation_cost` | `pv_module_installation_cost`, `inverter_installation_cost`, `array_bos_installation_cost` |
| 5 | `capital_cost` | `battery_pack_capital_cost`, `hybrid_inverter_capital_cost`, `battery_bos_capital_cost` |
| 6 | `raw_material_cost` | `battery_pack_raw_material_cost`, `hybrid_inverter_raw_material_cost`, `battery_bos_raw_material_cost` |
| 7 | `fabrication_cost` | `battery_pack_fabrication_cost`, `hybrid_inverter_fabrication_cost`, `battery_bos_fabrication_cost` |
| 8 | `installation_cost` | `battery_pack_installation_cost`, `hybrid_inverter_installation_cost`, `battery_bos_installation_cost` |
| 9 | `capital_cost` | `racking_capital_cost`, `electrical_panel_capital_cost`, `permitting_capital_cost` |
| 10 | `raw_material_cost` | `racking_raw_material_cost`, `electrical_panel_raw_material_cost`, `permitting_raw_material_cost` |
| 11 | `fabrication_cost` | `racking_fabrication_cost`, `electrical_panel_fabrication_cost`, `permitting_fabrication_cost` |
| 12 | `installation_cost` | `racking_installation_cost`, `electrical_panel_installation_cost`, `permitting_installation_cost` |
| 13 | `capital_cost` | `solar_array_capital_cost`, `battery_system_capital_cost`, `site_infra_capital_cost` |
| 14 | `raw_material_cost` | `solar_array_raw_material_cost`, `battery_system_raw_material_cost`, `site_infra_raw_material_cost` |
| 15 | `fabrication_cost` | `solar_array_fabrication_cost`, `battery_system_fabrication_cost`, `site_infra_fabrication_cost` |
| 16 | `installation_cost` | `solar_array_installation_cost`, `battery_system_installation_cost`, `site_infra_installation_cost` |

## The disease is still pinned

Curing a refusal must not hide it.
`test_d5_variants.py::test_the_rename_alone_still_collides_so_the_cure_is_not_hiding_the_disease`
builds the stage-1-only text and asserts the exact route still refuses it with
`SI_RENDERING_COLLISION`. If the collision ever stops firing, that test fails here rather
than passing silently in a variant that no longer needs the cure.

## Hand arithmetic — Site Infrastructure

Checked by hand from the model, not copied from any route's output. Design values:
`racking.panel_count = 20.0`, `electrical_panel.circuit_count = 4.0`,
`permitting.system_capacity_kw = 8.0`; library defaults `cost_per_panel_rack = 57.0`,
`base_cost = 150.0`, `cost_per_circuit = 34.0`, `cost_per_kw = 187.5`,
`fab_factor = 0.45`, `install_factor = 0.30`.

| Child | material | fabrication | installation | total |
|---|---:|---:|---:|---:|
| Racking & Mounting | 20 × 57 = **1140.0** | ×0.45 = **513.0** | ×0.30 = **342.0** | **1995.0** |
| Electrical Panel | 150 + 4×34 = **286.0** | ×0.45 = **128.7** | ×0.30 = **85.8** | **500.5** |
| Permitting & Interconnect | **0.0** | **0.0** | **0.0** | 8 × 187.5 = **1500.0** |

| Site Infrastructure rollup | value |
|---|---:|
| `capital_cost` | 1995.0 + 500.5 + 1500.0 = **3995.5** |
| `raw_material_cost` | 1140.0 + 286.0 + 0.0 = **1426.0** |
| `fabrication_cost` | 513.0 + 128.7 + 0.0 = **641.7** |
| `installation_cost` | 342.0 + 85.8 + 0.0 = **427.8** |
| `idiot_index` | 3995.5 / 1426.0 = **2.8018934081346423** |

`test_d5_variants.py` asserts these against the projected graph: each rollup's inputs are
exactly the three named intermediates, each wired to the child channel the table names, and
the leaf `calc_expressions` evaluate to the leaf values above.
