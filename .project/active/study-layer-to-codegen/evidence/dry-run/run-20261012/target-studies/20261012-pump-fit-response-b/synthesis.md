# Synthesis — `20261012-pump-fit-response-b`

- **Administrator:** Claude (Opus 5.5), Claude Code session, run-study skill, administer mode. This was a fresh session with no conversation inherited from the executor. The brief limited reading to this record directory.
- **Date:** 2026-10-12
- **`snapshot.json` read:** sha256 `e08b077f495eef6d8e82113423837e8f99917dbcd8df24cec46fc2f82581e594`, which matches `record.md` § 16.
- **Read set:** `record.md`, `snapshot.json`, `indicators.json`, and everything under `results/`, including the two stores (opened read-only) and the 12 case artifacts. `axes.json` sits in this directory but was outside the brief's read set, so it was not opened. The per-key provenance below comes from `indicators.json` `groups[].declared_keys`.
- **Integrity:** every artifact digest under `snapshot.json` `arms[0].artifacts` was recomputed and matches. `indicators.json` matches `snapshot.json` `indicators.sha256`. `results/verification_summary.json` matches `arms[0].verification.summary_sha256`.

Labels used below: **[recorded]** means the record states it and a cited artifact carries it. **[record says]** means only `record.md` prose carries it, with no artifact in this directory behind it. **[administrator's reading]** is my own interpretation, drawn from the cited evidence and not attributed to the executor.

---

## What the study set out to do

[recorded] The owner's intake, verbatim in `record.md` § 2: *"Study how the pump-fit constraint responds to basin area and installed pump capacity, and whether the energy price matters to it. The package is pkg/station_study."*

[recorded] The executor resolved "the pump-fit constraint" to `PumpStation__station__pump_fit__aa8dd6c31b6b238a` (`PumpStation::CapacityCoversDemand`, local identity `pump_fit`, operator `>=`, operands `capacity` (bound to `PumpStation__station__installed_capacity`) and `demand_flow` (computed, `PumpStation__station__demand__required_flow`)). Sources are `indicators.json` `groups[].bounds` and `record.md` § 2. It is the only constraint in the indicator output. Every case artifact reports `authored_usage_total: 1` and `applicable_gate_total: 1` (`results/_work/artifacts/*.json`).

[recorded] This record continues `20261012-pump-fit-response`, which stopped at step 7 on an operator question. Steps 1–7 were re-run here (`record.md` § 1). The study ran one arm, `arm-main`.

## What it found

**Pump-fit verdict over the 12-point grid** [recorded]. Source: `results/grid_cases.json`, cross-checked against `results/oracle_scan.json` and the 12 case artifacts, which agree case for case. Each cell gives the verdict and then the margin from `oracle_scan.json`.

| basin_area \ installed_capacity | 0.20 | 0.25 | 0.30 |
|---|---|---|---|
| 4.0 | violated (−0.08) | violated (−0.03) | satisfied (+0.02) |
| 8.0 | violated (−0.06) | violated (−0.01) | satisfied (+0.04) |
| 12.0 | violated (−0.04) | satisfied (+0.01) | satisfied (+0.06) |
| 16.0 | violated (−0.02) | satisfied (+0.03) | satisfied (+0.08) |

- 7 points are satisfied and 5 are violated. All 12 cases are `completed`, with coverage `complete`, under executable fingerprint `75c3cc58…8c00`.
- `required_flow` takes the values 0.28, 0.26, 0.24 and 0.22 at areas 4, 8, 12 and 16, at every capacity. `annual_cost` takes the values 224.0, 208.0, 192.0 and 176.0 at the same areas, at every capacity. It is unit-less in the model (`record.md` § 3).
- No point sits on the boundary. The smallest |margin| is 0.01 (`results/oracle_scan.json`).

**Baseline** [recorded]. The pinned point (area 12.0, capacity 0.25, energy_price 0.1, design_inflow 0.3, allowed_rise_rate 0.005, pump_head 8.0) reproduced `annual_cost` 192.0 with `pump_fit` satisfied (`results/baseline_result.json`). Every preflight gate passed (`results/preflight_results.json`), and the post-run package-clean check passed (`results/postrun_clean.json`).

**Verification** [recorded]. All 12 cases were sampled across 2 verdict strata. Both channels show a worst relative deviation of 0.0 against tolerance 1e-9. Verdicts were re-derived from oracle operands, with no mismatches (`results/verification_summary.json`).

**Energy price** [recorded]. `indicators.json` reports `no_constraint_response: true` for `energy_price`. Neither `pump_fit` operand is reached, and `annual_pumping_cost` is the only objective reached. The axis was not swept, by operator ruling (`record.md` § 8).

**Optimum.** None was sought. [record says] The objective policy is empty (`record.md` § 3). The route code is not in this directory.

## Framing verdict per axis

| Axis | Indicator (`indicators.json`) | Proposed | Judged | Administrator's verdict |
|---|---|---|---|---|
| `basin_area` | `constraints_reachable` via `demand_flow` (computed) | search | search | **Upheld.** The verdict flips with area at capacity 0.25, between 8.0 (margin −0.01) and 12.0 (+0.01). Area produces no flip at 0.20 (all violated) or at 0.30 (all satisfied). The boundary is located only to the grid cell. |
| `installed_capacity` | `constraints_reachable` via `capacity` (bound, the input itself) | search | search | **Upheld.** At every area the verdict goes from violated to satisfied as capacity rises. The flip lies in 0.25–0.30 at areas 4 and 8 and in 0.20–0.25 at areas 12 and 16. Capacity reaches no objective, and on the grid it changes neither channel. |
| `energy_price` | `no_constraint_response` | sensitivity, then declined | not swept | **Upheld as an indicator-only answer.** No run evidence exists for this axis. The answer to "does energy price matter to pump-fit" is the structural sound negative, and nothing more. |

[administrator's reading] For basin_area, the data show a larger basin lowering required_flow and so loosening the constraint. Both indicator and verdict structure are consistent with the search framing. The record correctly confines its "falls as area rises" claim to the four grid points. Monotonicity is not derivable from indicators (`indicators.json` `not_derivable`), and four points do not establish it off-grid.

[administrator's reading] `results/report.md` says *"In this model, energy price cannot change the pump-fit verdict."* That claim is only as strong as the indicator's module-level trace. It is a structural sound negative, and no observation stands behind it. The report does label it structural. The sentence itself, though, is worded more absolutely than "no path in the module graph reaches either operand".

## Constraint structure

[recorded] There is one executing constraint, `pump_fit`: `capacity >= demand_flow`, where `demand_flow = required_flow`.

- `capacity` is the swept input `installed_capacity` (`indicators.json`, operand class `bound`). Each case artifact's `observed.capacity` equals the case's input.
- [recorded] `snapshot.json` `manifest.content_used.objective_catalog[].note` gives `required_flow = inflow − rise_rate * area`. At the held values (inflow 0.3, rise_rate 0.005) that is 0.3 − 0.005·area, which reproduces 0.28/0.26/0.24/0.22. That note is the manifest's description of the model text and is not the model text itself.
- [administrator's reading] The feasible region on the grid is capacity ≥ 0.3 − 0.005·area. Every recorded margin equals capacity − required_flow. The 12 verdicts are therefore one linear boundary sampled on a 4×3 lattice. The record claims the boundary only to the grid cell, and this synthesis does not extend it.
- [recorded] `annual_cost` sits outside the constraint. Per the catalog note it is `flow_rate * head * price * 1000.0`, and energy_price reaches only this channel (`indicators.json`). Nothing bounds it, which is finding #1.

## Findings carried forward

These are taken from `record.md` § 15 as recorded. Their discovery-log rows are outside this directory and were not read.

| Id | Kind | Finding (abridged) | Disposition / Home (as recorded) |
|---|---|---|---|
| `#1` | model | energy_price reaches no constraint, and nothing bounds operating cost | open; unrouted |
| `#2` | model | required_flow goes negative above area = design_inflow / allowed_rise_rate (60.0), and no constraint catches it | open, outside this window; unrouted |
| `#3` | process | annex and manifest drafted by the executor, not ratified by the owner | open; `studies/ANNEX.md` |
| `#4` | process | study policy is an unratified template; its § 1 current-state line is unfilled | open; `modeling_project/STUDY_POLICY.md` |
| `#5` | process | no resume path for a record stopped on an operator question | open; runbook step 15 |
| `#6` | process | window fixed in route code before the step-7 oracle scan | accepted by operator ruling 2026-10-12 |

[administrator's reading] The record directory partly supports #2. The catalog note gives `required_flow = inflow − rise_rate * area`, so 0.3 / 0.005 = 60.0. `pump_fit` is the only constraint, and with `>=` it would pass a negative demand. The "validity mask in the annex" lives outside this directory.

Process observations from this reading. They are filed here and not in the discovery log; whoever acts on this synthesis files them.

- **A.** `results/verification_summary.json` has `not_independently_verified: []`. Yet `record.md` § 13 correctly states that the `capacity` operand is identical by construction on both sides, and the oracle binds it to the input. The tool's output omits a limitation the record has to argue in prose. That is a contract or tool gap: the verify output should list operands bound to swept inputs.
- **B.** The record contract does not require the window's source, the route's `GRID` and its docstring rationale, to be snapshotted into the record. This record's window provenance (§ 11, "fixed in the route before the oracle scan") therefore rests on prose and on `oracle_scan.json`'s `grid_source` string.
- **C.** The contract does not require operator rulings made after intake to be kept verbatim. § 8's later rulings read as the executor's restatement.
- **D.** A continuation record cites its predecessor (indicator content "identical", findings "re-sighting") without carrying the predecessor's relevant content or digest.
- **E.** Per-case held-fixed inputs are not stored. Store `inputs_json` and `grid_cases.json` carry only the two swept keys.

## What the record does not support

Facts I could not recover from this directory are listed as missing. Claims the directory's evidence does not carry follow after them.

**Missing facts**

1. **The held-fixed values actually in force at each grid point.** `results/_work/station-grid-v1.db` `cases.inputs_json` and `results/grid_cases.json` hold only basin_area and installed_capacity. The only source for energy_price = 0.10, design_inflow 0.3, allowed_rise_rate 0.005 and pump_head 8.0 is the `snapshot.json` `arms[0].window.held_fixed` statement. [administrator's reading] The values are consistent with it: cost and flow at area 12 equal the baseline's at energy_price 0.1. That consistency is not a record of the inputs.
2. **The window's origin.** The route `GRID`, its docstring (the "chosen so both verdicts occur" rationale in § 11), and the claim that it was fixed before the scan are all absent. Only `record.md` prose and `oracle_scan.json` `grid_source` back them.
3. **The operator's later rulings in their own words**, and their timing relative to execution. § 8 gives the date 2026-10-12 and "before any study point ran". No artifact timestamps the ruling against the runs.
4. **The predecessor record `20261012-pump-fit-response`.** The claims that its indicator content is identical, that findings #1 and #2 are re-sightings, and that it carries an addendum all point outside this directory.
5. **The annex.** That covers § Declared ties ("no ties"), § Validity masks (the area ≤ 60.0 bound) and § Oracle coverage. The manifest's `ties: []` in `snapshot.json` is the only in-directory support for "no ties".
6. **The study policy's § 6 / § Execution routes naming this route.** This is asserted in § 10 only.
7. **The objective policy being empty** (`ObjectivePolicy((), {})`). This is asserted in § 3 only, and no route code or artifact carries it.
8. **The oracle's independence and content.** Only its source digest (`snapshot.json` `manifest.content_used.oracle.source_digest`) and its outputs are here. Whether it is a separate recomputation from the model text cannot be checked from this directory.
9. **The teax revision.** `snapshot.json` `teax.revision` is `8d877460…3397`, while `results/verification_summary.json` records `"unrecorded"`. The § 17 account of how the snapshot value was read (`git rev-parse` on `TEAX_SIMKIT_PATH`) is prose only.
10. **The discovery-log rows** and the step-14 check's printed `[]`. `DISCOVERY_LOG.md` is outside this directory.
11. **The coordinator check of the annex and manifest** ("every fact was cross-checked against the model, pipeline and contracts", § 14). No artifact records that check.
12. **The baseline case's evidence artifact.** `results/baseline_result.json` names case `station-baseline-v1:c0000`. All 12 retained artifacts under `results/_work/artifacts/` are grid cases, and the baseline store's evidence artifact is not retained. Its channels and verdict are present in `baseline_result.json` itself.
13. **The commit that froze this record.** `snapshot.json` `package.repo_commit` (`5eb5dbb…`) is the package's commit at execution. The commit containing this record cannot be recovered from the directory.

**Claims the evidence does not carry**

- No location of the pump-fit boundary finer than the grid cell, and no claim between grid points or outside area 4–16 × capacity 0.20–0.30.
- No monotonicity of required_flow or annual_cost in basin_area beyond the four observed points (`indicators.json` `not_derivable`).
- No observed response to energy_price, of any kind. The only energy-price evidence is the structural indicator.
- No constrained optimum, because none was sought.
- No independent verification of the `capacity` operand. It is identical by construction (`record.md` § 13), even though `verification_summary.json` lists nothing as not independently verified.
- No check of the model's physics. Per § 13, the oracle and package share the same model text.
- No owner ratification of the annex, the manifest or the study policy (findings #3 and #4).
- No `sysml-codegen study integrate` result (§ 17).
- No independent review. Every § 14 verdict is a coordinator check by the executor.
