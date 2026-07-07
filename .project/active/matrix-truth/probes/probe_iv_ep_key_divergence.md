# Probe (iv) — EP-key divergence: `resolve_input` fallback vs the live aggregation path

**Purpose:** capture, as a reviewable artifact, the baseline evidence that a naive
`resolve_input` drop-in would churn params-JSON keys. This is the concrete backing for design
bet **B2** and the reason the F4 cutover is filed as `[ITEM7-F4-CUTOVER]` rather than done in
Item 7. (Added per design-review M4.)

## The divergence

For the SumTerm `permitting.raw_material_cost` in the aggregation module
`SolarBatteryDesign__solar_battery_plant__site_infra__raw_material_cost`:

- **Live path** (`_build_aggregation_module`, graph_builder.py:1460) builds the entry-point QN
  as `{module_eqn}__{part_usage}_{attr}` → `…site_infra__raw_material_cost__permitting_raw_material_cost`.
- **`resolve_input` fallback** (input_resolver.py:270) builds it as `{module_eqn}__{leaf}` →
  `…site_infra__raw_material_cost__raw_material_cost`.

## Baseline evidence — both strings coexist in one file

`tests/fixtures/baseline_outputs/solar_battery/computation_graph.json`:

```
# The live-path SumTerm ENTRY-POINT qualified_name (input param, part_usage-prefixed):
2472:  "qualified_name": "SolarBatteryDesign__solar_battery_plant__site_infra__raw_material_cost__permitting_raw_material_cost",
4311:  "qualified_name": "SolarBatteryDesign__solar_battery_plant__site_infra__raw_material_cost__permitting_raw_material_cost",

# The aggregation module's own OUTPUT channel_name (leaf-only) — what resolve_input's
# leaf-only fallback would ALSO emit, but as an ENTRY POINT:
2483:  "channel_name": "SolarBatteryDesign__solar_battery_plant__site_infra__raw_material_cost__raw_material_cost",
3270:  "producer_channel": "SolarBatteryDesign__solar_battery_plant__site_infra__raw_material_cost__raw_material_cost",
3486:  "producer_channel": "SolarBatteryDesign__solar_battery_plant__site_infra__raw_material_cost__raw_material_cost",
```

## Why a drop-in churns the baseline

The leaf-only fallback format (`…__raw_material_cost`) is already live in the graph as the
module's **output channel** (line 2483, consumed as a `producer_channel` at 3270/3486). A
naive cutover would make the module's SumTerm **input entry point** take that same string —
colliding an input EP with an existing output-channel name in the same graph, and dropping the
`permitting_` disambiguator that keeps sibling part-usage inputs distinct. Either reading —
collapse of the part-usage prefix, or input/output name collision — rewrites the baseline.

## Consequence for the cutover item

`[ITEM7-F4-CUTOVER]` must reconcile `resolve_input`'s fallback to the live path's richer EP
construction (part_usage-prefixed QN, `_find_literal_redefinition` defaults, param-groups,
multiplicity EPs, SingletonTerm Try-2) **before** rewiring the 3 call sites, then re-capture
baselines byte-identically or as a reviewed capture diff. Its safety-net parity suite must
compare against `_resolve_aggregation_input_channel` (the replaced function), not only the
backtracker DFS.
