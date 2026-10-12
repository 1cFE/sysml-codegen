# Package annex — `station_study`

Package fact, not rule. The run-study runbook cites a section here at each step that needs something only true of this package. Nothing in this file is an instruction, and nothing in it is inlined into the runbook.

**Authorship.** Drafted 2026-10-12 by the executor of study `20261012-pump-fit-response` (Claude, Opus 5.5), because the project supplied no annex. Every fact below is read from `models/station.sysml`, the generated package's `pipelines/pipeline.yaml` and contracts, and `studies/oracle_entry.py`. The package owner has not reviewed or ratified it.

---

## Package-owned pieces

| Piece | Where it is |
|---|---|
| Package | `pkg/station_study` |
| Manifest | `studies/manifest.json` (executor-drafted, same authorship as this annex) |
| Axis declaration | per study, in the record directory: `studies/<study-id>/axes.json` |
| Route | `studies/study_route.py`: `execute_baseline`, and `run_grid` (runs the module's fixed `GRID`). It is the route the study policy's § Execution routes names. |
| Oracle | `studies/oracle_entry.evaluate` and its `operand_bindings()`, as the manifest's `oracle` block names them |
| Snapshot | `station.snapshot.json` |
| Census | none tracked |

**The snapshot rule.** `sysml-codegen study integrate` recaptures the snapshot at its gate 4, so it needs exactly one `*.snapshot.json` beside the models root, in the models root's parent directory. `station.snapshot.json` sits beside `models/`.

---

## § Declared ties

No ties; every axis key fans out from one attribute. In `pipelines/pipeline.yaml` each of the six `station` design attributes reaches the package as exactly one entry key, `PumpStation__station__<attribute>`, consumed by exactly one module.

---

## § Baseline pin

The baseline point is the six `station` design values as `models/station.sysml` declares them (also `inputs/station_params.json`): design_inflow 0.30, basin_area 12.0, allowed_rise_rate 0.005, installed_capacity 0.25, pump_head 8.0, energy_price 0.10.

Headline: `PumpStation__station__pumping__annual_cost` = 192.0. Expected verdict: `pump_fit` satisfied. Source: the arithmetic in the model file's own header comment — required_flow = 0.30 − 0.005 × 12.0 = 0.24; annual_cost = 0.24 × 8.0 × 0.10 × 1000.0 = 192.0; pump_fit holds because 0.25 ≥ 0.24.

The baseline establishes that the package reproduces the model's stated arithmetic at one point. It says nothing about the design's margin beyond that point, and the model carries no units, so 192.0 is unit-less.

---

## § Oracle

`studies/oracle_entry.py` recomputes the model's two calcs from the model text, independently of the generated package: `required_flow = design_inflow − allowed_rise_rate × basin_area`, and `annual_cost = required_flow × pump_head × energy_price × 1000.0`. It returns both channels by qualified name.

Covers: both calculated channels, and the one constraint `pump_fit` (`PumpStation__station__pump_fit__aa8dd6c31b6b238a`). `operand_bindings()` maps its `capacity` operand to the input `PumpStation__station__installed_capacity` and its `demand_flow` operand to the channel `PumpStation__station__demand__required_flow`.

Does not cover: the constraint report aggregator, or anything not among the six design inputs. It refuses (raises `ValueError`) any input key it does not model.

---

## § Validity masks

One derived bound. `required_flow` is the flow the pumps must remove; it is non-negative only while `basin_area ≤ design_inflow / allowed_rise_rate`. With the held-fixed design_inflow 0.30 and allowed_rise_rate 0.005, that bound is basin_area ≤ 60.0. Beyond it the model computes a negative required flow and a negative annual cost, which no modeled constraint catches. All swept inputs are also held non-negative (an area, a capacity and a price cannot be negative).
