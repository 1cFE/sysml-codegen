# Provenance — `solar_battery_d5`

Authored 2026-08-11 for recovery plan **Gate 4C part 6**
(`.project/active/cutover-recovery/plan.md`), as the migrated variant of
`solar_battery_model` — corpus row 33, a ratified `expected-collapse` refused with
24× `SI_SELF_BINDING`.

**Not a corpus fixture.** It joins no ledger and no 37-path corpus run. `solar_battery_model`
is untouched.

**INCOMPLETE — the exact route does not yet accept this model.** It is committed at the
rename stage because that stage is finished and proved, not because it is usable coverage.

## What was done — the D-5 rename, complete and proved

21 formals renamed to `<name>_in` inside their `calc def`s and on the left side of every
binding, across `design.sysml` and `library.sysml`: `capacity_kwh`, `chemistry_factor`,
`circuit_count`, `discount_rate`, `efficiency`, `fuel_consumption`, `fuel_unit_cost`,
`n_mod`, `om_rate_per_kw_year`, `p_net_kw`, `p_net_mw`, `pack_count`, `panel_count`,
`plant_availability`, `plant_lifetime`, `power_rating`, `string_count`,
`system_capacity_kw`, `tilt_angle`, `wattage`, `yearly_inflation`.

**Strip check: 0 problems.** Removing the `_in` suffix reproduces `solar_battery_model` byte
for byte, file for file. Pinned by `tests/conformance/test_d5_variants.py`.

## What blocks it — the ratified aggregation requirement, at scale

With the self-bindings gone, projection refuses the model with `SI_RENDERING_COLLISION`:

```
distinct expression sources on
'SolarBatteryDesign__solar_battery_plant__solar_array__raw_material_cost'
render as parameter 'raw_material_cost_0'
```

This is the behaviour the **S4 ruling** confirmed as correct and the `costed_cart_d5` fixture
already demonstrates the cure for: an assembly cannot write
`sum(pv_module.raw_material_cost) + sum(inverter.raw_material_cost) + …`, because the exact
route names an expression parameter after the last member of the reference and drops the
qualifier, so every term renders the same name. Each child's contribution needs its own named
attribute and the rollup adds those names.

**Measured scope: 16 colliding rollups over 50 terms**, across `capital_cost`,
`raw_material_cost`, `fabrication_cost` and `installation_cost` in every assembly. The cure
adds ~50 named intermediate attributes and rewrites all 16 rollups.

That is a shape change, not a rename, so **the strip-check proof the gate requires cannot
cover it** — stripping cannot recover the original from a model with different attributes.
Surfaced to the orchestrator rather than applied on the rename gate's authority.
