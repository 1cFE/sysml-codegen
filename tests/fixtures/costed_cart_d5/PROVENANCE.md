# Provenance — `costed_cart_d5`

Authored 2026-08-11 for recovery plan **Gate 4C** (`.project/active/cutover-recovery/plan.md`),
as the exact-route replacement specimen for rows **L-199** (costed component end to end),
**L-203** (hierarchy aggregation wrappers), and as a second source for **L-198**
(computed attributes) and **L-201** (expression compilation).

**Not a corpus fixture.** It joins no ledger and no 37-path corpus run. The 37 ratified
corpus fixtures are untouched by the gate that authored this one.

## Why it exists

`solar_battery_model` carried the Costed Component pattern's only end-to-end proof. It is
corpus row 33, a ratified `expected-collapse`: the exact route refuses it with 24×
`SI_SELF_BINDING`. This fixture carries the same pattern in the form the exact route accepts.

## The two differences against `solar_battery_model`

1. **D-5 binding form.** Every calc-usage binding renames the formal
   (`in area_in = area`) rather than binding a formal to an attribute of its own name.

2. **Named aggregation terms.** The fixture gives each child's contribution its own named
   attribute and adds those names. This remains useful for readable rollups and independently
   inspectable per-role modules. It is no longer required to avoid `SI_RENDERING_COLLISION`:
   when distinct resolved chains in one expression share a leaf name, the exact route retains
   the shortest resolved qualifier that distinguishes them. The direct two-term form and its
   `panel_capital_cost_{0,1}` / `caster_capital_cost_{0,1}` inputs are pinned by
   `tests/integration/test_costed_component_exact_route.py::test_a_two_term_same_name_rollup_keeps_both_resolved_source_families`.

## Hand-derived values

Every factor is binary-exact, so the expected values in the specimens are exact.

| Leaf | driver | material | fab | total | idiot index |
|---|---|---:|---:|---:|---:|
| deck panel (×4) | area 2.5 × 12.0 | 30.0 | 15.0 | 45.0 | 1.5 |
| caster (×4) | load 80.0 × 0.75 | 60.0 | 30.0 | 90.0 | 1.5 |
| frame rail | length 4.0 × 25.0 | 100.0 | 50.0 | 150.0 | 1.5 |
| cross brace set | 6.0 × 5.0 | 30.0 | 15.0 | 45.0 | 1.5 |

Allocation: `fastener_cost = 20.0 × 0.5 = 10.0`, `wiring_cost = 50.0 × 2.0 = 100.0`,
`total_allocation = 110.0`, `material_portion = 110.0 × 0.8 = 88.0`.

| Rollup | capital | raw material | fabrication |
|---|---:|---:|---:|
| deck assembly | 4×45 + 4×90 + 110 = **650.0** | 4×30 + 4×60 + 88 = **448.0** | 4×15 + 4×30 = **180.0** |
| frame assembly | 150 + 45 = **195.0** | 100 + 30 = **130.0** | 50 + 15 = **65.0** |
| cart plant | 650 + 195 = **845.0** | 448 + 130 = **578.0** | 180 + 65 = **245.0** |

System level: `throughput_units = 3.0 × 250.0 = 750.0`,
`annual_handling_cost = 750.0 × 0.4 = 300.0`,
`annualized_capital_cost = 845.0 × 0.1 = 84.5`.
