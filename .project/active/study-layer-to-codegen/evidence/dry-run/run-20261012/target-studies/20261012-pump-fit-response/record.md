# Study record — `20261012-pump-fit-response`

Written from the run-study `record-template.md`. The values live in `snapshot.json` and the arguments live here. Once committed, this file is corrected only by an appended `## Addendum` section.

---

## 1. Study header

- **Study id:** `20261012-pump-fit-response`
- **Package:** `pkg/station_study`
- **Date executed:** `2026-10-12`
- **Executor:** Claude (Opus 5.5) Claude Code session, run-study skill, execute mode
- **Mode:** execute
- **Arms:** single arm (planned as `arm-main`; not executed: the study stopped at runbook step 7, see § 17)

**Status: STOPPED before any study point ran.** Runbook steps 1–6 completed. Step 7 stopped on a question only the operator can answer (§ 17). Steps 8–13 did not run. Step 14 (findings) and step 15 (snapshot and commit) were done for what exists.

## 2. Intake

The owner's goal and scope, in their own words, verbatim.

> Study how the pump-fit constraint responds to basin area and installed pump capacity, and whether the energy price matters to it. The package is pkg/station_study.

Operator answers given with the intake, verbatim:

> - The studies directory is `studies/`. Write that into the policy's § Locations.
> - The execution route is `execute_baseline` and `run_grid` in `studies/study_route.py`.
> - The oracle is `oracle_entry`, in `studies/`.
> - If an axis reports `no_constraint_response`, the ruling is: proceed with it as sensitivity-only.
> - A coordinator review check suffices for the review steps.
> - Commit the record.

**Executor's additions (not the owner's words).**
- Three candidate axes, one per named attribute: `basin_area`, `installed_capacity`, `energy_price` (`PumpStation::station::*`).
- "The pump-fit constraint" is `PumpStation__station__pump_fit__aa8dd6c31b6b238a` (`PumpStation::CapacityCoversDemand`, local identity `pump_fit`), the model's only executing constraint.
- The project supplied no `studies/ANNEX.md` and no `studies/manifest.json`. The executor drafted both from `models/station.sysml`, the package's pipeline and contracts, and `studies/oracle_entry.py`. Both are labeled executor-drafted and are not owner-ratified (finding #4).
- The executor filled the study policy's § 6 Execution routes with the route the operator named, as `station_study_route`, alongside § 10 Locations.

## 3. Objective and result

- **Objective channel(s):** `PumpStation__station__pumping__annual_cost` (catalog name `annual_pumping_cost`); also cataloged: `PumpStation__station__demand__required_flow`
- **Objective result:** no study result. Only the pinned baseline point ran: annual_cost = 192.0 (unit-less in the model) and required_flow = 0.24 at the baseline design point (`results/baseline_result.json`).

The study stopped before step 9, so the objective was not evaluated over any studied space.

## 4. Constraint outcomes

Every executing constraint, by qualified identity, with its status.

| `constraint_id` | `source_local_identity` | Status | Note |
|---|---|---|---|
| `PumpStation__station__pump_fit__aa8dd6c31b6b238a` | `pump_fit` (`PumpStation::CapacityCoversDemand`, usage `PumpStation::station::pump_fit`) | satisfied, at the baseline point only | 0.25 ≥ 0.24 at the baseline (`results/baseline_result.json`). No study point ran, so there is no outcome over the studied space. |

## 5. Framing

**As proposed at intake.**

| Axis | Framing proposed | Why |
|---|---|---|
| `basin_area` | search | `constraints_reachable`: reaches `pump_fit` through its computed `demand_flow` operand (required_flow). A pump-fit verdict boundary is expected. |
| `installed_capacity` | search | `constraints_reachable`: is `pump_fit`'s bound `capacity` operand directly. A verdict boundary is expected. |
| `energy_price` | sensitivity | `no_constraint_response`: reaches only `annual_pumping_cost`. The owner ruled it proceeds as sensitivity-only. |

**As judged after the run.**

| Axis | Framing judged | Changed? | Why |
|---|---|---|---|
| `basin_area` | not judged | not applicable | No study point ran (§ 17). |
| `installed_capacity` | not judged | not applicable | No study point ran (§ 17). |
| `energy_price` | not judged | not applicable | No study point ran (§ 17). |

## 6. Per-axis account

No study point ran, so every account below is discharged by the stop (§ 17). The oracle scan at step 7 is recorded in § 11. It is pre-execution evidence, not a run result.

#### `basin_area` — feasible structure (search framing)
**Applies:** yes, but not delivered: the study stopped before execution.

Not run.

#### `basin_area` — observed response (sensitivity framing)
**Applies:** not applicable — this axis is search-framed

#### `installed_capacity` — feasible structure (search framing)
**Applies:** yes, but not delivered: the study stopped before execution.

Not run.

#### `installed_capacity` — observed response (sensitivity framing)
**Applies:** not applicable — this axis is search-framed

#### `energy_price` — feasible structure (search framing)
**Applies:** not applicable — this axis is sensitivity-framed

#### `energy_price` — observed response (sensitivity framing)
**Applies:** yes, but not delivered: the study stopped before execution.

Not run. No boundary claim is made. The structural fact that does stand is the indicator: `energy_price` has `no_constraint_response`, so no path in the module graph reaches `pump_fit` from it (§ 8).

## 7. Axis groups

Every declared qualified entry key, with its per-key provenance. Declaration file: `axes.json`.

| Axis | Entry key | Provenance | Note |
|---|---|---|---|
| `basin_area` | `PumpStation__station__basin_area` | fan_out | the attribute's only entry key in `pipelines/pipeline.yaml` (feeds `pumpstation__station__demand.area`) |
| `installed_capacity` | `PumpStation__station__installed_capacity` | fan_out | the attribute's only entry key (feeds `pump_fit.capacity`) |
| `energy_price` | `PumpStation__station__energy_price` | fan_out | the attribute's only entry key (feeds `pumpstation__station__pumping.price`) |

No ties are declared (annex § Declared ties).

## 8. Indicators and rulings

Per proposed axis. All three were proposed, and none was declined. Source: `indicators.json`, `subset: false`, no warnings.

| Axis | Indicator | Ruling | Note |
|---|---|---|---|
| `basin_area` | `constraints_reachable` | none needed | Reaches `pump_fit` via `demand_flow` (computed, required_flow). Reaches both objectives. 4 modules fired. To be swept; not yet run. |
| `installed_capacity` | `constraints_reachable` | none needed | Reaches `pump_fit` via `capacity` (bound, the design attribute itself). Reaches no objective. 2 modules fired. To be swept; not yet run. |
| `energy_price` | `no_constraint_response` | Owner, given before execution: "proceed with it as sensitivity-only" | Reaches `annual_pumping_cost` only. `pump_fit` is unreachable (neither operand reached). 1 module fired. To be swept as sensitivity-only, but no named route callable can execute it (§ 17). |

**Not derivable, disclosed in every record.** These are not decidable from the indicator run and no indicator output claims them: monotonicity of any channel in any axis; identity of the same physical quantity across differing key names; intra-module operand dependency. `constraints_reachable` is a *possible* path and never a statement that a constraint responds. `unresisted` is the agent's recorded judgment, never a tool output.

**Model-development findings.** Every `no_constraint_response` axis carries one, in addition to the user's ruling. The ruling does not discharge it.

| Axis | What should push back and is not modeled | Finding id |
|---|---|---|
| `energy_price` | Nothing in the model limits operating cost. No constraint bounds `annual_cost` (for example, a sourced operating budget), and energy price does not feed the capacity or sizing decision. So the price can move cost without limit and no verdict changes. | `20261012-pump-fit-response#1` |

## 9. Preflight results

Source: `results/preflight_results.json` (`sysml-codegen study preflight gates`, outcome `pass`). The gates read `results/package_identity.json` and `results/baseline_result.json`, which `execute_baseline` deposited at step 5.

| Gate | Outcome | Detail |
|---|---|---|
| Declared-group key validation | pass | 3 declared keys across 3 groups, all package inputs |
| Suffix-sibling scan (warnings only) | pass | no siblings found |
| Baseline gate against the pinned headline | pass | `PumpStation__station__pumping__annual_cost` expected 192.0, observed 192.0 (relative deviation 0.0); 1/1 pinned verdicts match (`pump_fit` satisfied) |
| Manifest / package fingerprint match | pass | both recorded package fingerprints match the package on disk; identity gate: sealed digest `75c3cc58…8c00` recomputed, every sealed artifact matches |
| Package cleanliness | pass | package tree byte-untouched (git clean) |

## 10. Execution route and why

- **Route:** `station_study_route`: `studies/study_route.py` `execute_baseline` (exercised at step 5) and `run_grid` (not exercised).
- **Why this route:** it is the only route the study policy's § 6 names, and the operator named it. Step 8's rationale is incomplete: the route loaded and gated cleanly for the baseline, but `run_grid` runs only the fixed `GRID` (basin_area × installed_capacity, 4 × 3 points at the design energy_price). No named callable can execute the `energy_price` axis that the owner ruled should proceed. That question stopped the study (§ 17).

**Glue disclosure.** Glue ledger: none for the route as exercised. `execute_baseline` loads the sealed package through teax's own loader, with no adapter and no injected values. The preflight identity gate recomputed the sealed digest from 0 allowed-modified files. No arm ran, so `snapshot.json` carries no arm-scoped `glue_ledger`.

## 11. Study definition and window provenance

The window was not fixed. What was scanned: the route's fixed `GRID`, evaluated through the oracle (`oracle_entry.evaluate`). Pump-fit margin = installed_capacity − required_flow, with required_flow = 0.30 − 0.005 × basin_area:

- At basin_area 4.0 and 8.0, only capacity 0.30 is satisfied (margins +0.02, +0.04).
- At 12.0 and 16.0, capacities 0.25 and 0.30 are satisfied, and 0.20 is violated.
- Both verdicts occur, and no grid point sits on the boundary (smallest |margin| is 0.01).

The scan therefore shows the grid would catch the pump-fit boundary on both axes. Within the grid, the boundary lies between capacity 0.20 and 0.30 at every area.

A wider oracle scan of basin_area 0–60 at capacity 0.25 put the verdict flip between area 8 and 12, which agrees with the analytic boundary at area = 10. At area 60, required_flow reaches 0.0, which is the annex § Validity masks bound (area ≤ design_inflow / allowed_rise_rate = 60.0 at the held-fixed design values).

An oracle scan of energy_price 0.05–0.20 at baseline gave annual_cost from 96 to 384, linear in price, with required_flow and the pump-fit verdict unchanged.

If the route's grid were used, the window would be **engineered**. It is fixed in the route's source, and the route's docstring says it was chosen so "both verdicts occur" and no point sits on the boundary. The window was not fixed from this scan, and no bounds are recorded in `snapshot.json` (`arms` is empty).

## 12. Cross-fingerprint correlation and what it means

Single fingerprint — no cross-arm correlation needed. No arm executed. The baseline ran under the sealed executable fingerprint `75c3cc58959e064834c27f0babce156dc042d099bba4b286fe8fefb385b78c00`, which is the manifest's recorded value.

## 13. Verification

Not run. Runbook step 10 was not reached because the study stopped at step 7. `sysml-codegen study verify` was not invoked and `results/verification_summary.json` does not exist.

Nothing was independently verified against the oracle in a sampled sense. The baseline headline agreed with the manifest pin (preflight), and the pin is the model file's own stated arithmetic. That agreement checks the package against the model text at one point only.

## 14. Review outcomes

| Lens | Verdict | Disposition |
|---|---|---|
| Step 4 pre-execution framing check (coordinator check, per the operator's "a coordinator review check suffices") | Framing follows the indicators: two search axes reaching `pump_fit`, one `no_constraint_response` axis with an owner ruling and a model-development finding (#1). No new or reinterpreted source or math needs an independent check: the oracle, model and baseline arithmetic are the project's own, unchanged. | Accepted. No independent critique was triggered (single model family, no coupled architecture, no failed coverage). |
| Coordinator check of executor-drafted annex and manifest | Every annex and manifest fact was cross-checked against `models/station.sysml`, `pipelines/pipeline.yaml` and the contracts. Indicators and preflight validated the manifest mechanically (schema, fingerprints, baseline pin). | Owner ratification is still outstanding (finding #4). |
| Step 12 review outcomes | Not run: the study stopped at step 7. | (§ 17) |

**Runbook step 14 check**, run from the record directory:

```bash
python3 -c "import sys; sid = sys.argv[1] + '#'; bar = chr(124); ids = lambda path, col: {c for line in open(path) if line.startswith(bar) for c in [line.split(bar)[col].strip().strip(chr(96))] if c.startswith(sid)}; print(sorted(ids('record.md', 1) ^ ids('../DISCOVERY_LOG.md', 3)))" 20261012-pump-fit-response
```

Printed: `[]`

**Runbook step 15 checks**, run from the record directory:

```bash
# 0: no unreplaced placeholder (chr(60) is the opening angle bracket)
python3 -c "print(open('record.md').read().count(chr(60)))"
```

Printed: `0`

```bash
# []: every fingerprint name has a key under fingerprints
python3 -c "import json; s = json.load(open('snapshot.json')); print(sorted(set(s['manifest']['content_used']['fingerprint_names']) - set(s['fingerprints'])))"
```

Printed: `[]`

```bash
# []: every arm's store id resolves into stores[]
python3 -c "import json; s = json.load(open('snapshot.json')); print(sorted({a['store_id'] for a in s['arms']} - {t['store_id'] for t in s['stores']}))"
```

Printed: `[]`. This is vacuous: `arms` is empty because no arm ran.

```bash
# []: every result artifact has a digest
python3 -c "import json; s = json.load(open('snapshot.json')); print([f['path'] for a in s['arms'] for f in a['artifacts'] if not f.get('sha256')])"
```

Printed: `[]`. This is vacuous for the same reason. The pre-execution artifacts that do exist are digested under `snapshot.json` `pre_execution_artifacts`, which this check does not read.

## 15. Findings

Each finding gets an id used verbatim in `DISCOVERY_LOG.md`.

| Id | Kind | Finding | Disposition | Home |
|---|---|---|---|---|
| `20261012-pump-fit-response#1` | model | energy_price reaches no constraint: nothing in the model pushes back on operating cost (§ 8) | open; owner ruled the axis proceeds as sensitivity-only, which does not discharge this | unrouted |
| `20261012-pump-fit-response#2` | model | required_flow goes negative for basin_area above design_inflow / allowed_rise_rate (60.0 at the design values), and no constraint catches it | open; applied as a validity mask in the annex | unrouted |
| `20261012-pump-fit-response#3` | process | the named route cannot execute the energy_price axis: `run_grid` runs a fixed area-by-capacity grid only, and its window is fixed in route code before any scan | open; study stopped at step 7 pending operator ruling (§ 17) | unrouted |
| `20261012-pump-fit-response#4` | process | the project supplied no annex or manifest; the executor drafted both from the model text | open; awaiting owner ratification | `studies/ANNEX.md` |
| `20261012-pump-fit-response#5` | process | the study policy is an unratified template and its § 1 current-state line is unfilled | open | `modeling_project/STUDY_POLICY.md` |

**Homes a finding may route to:** tool, runbook step, policy rule, skill, modeling item, research round, documented seam. `unrouted` is a stated state, not a blank.

## 16. Snapshot

- **File:** `snapshot.json`
- **sha256:** `450cb1ed26fb5ca1f37ff355c5705d8a9bc09e51268886173ee8e6890cf03352`
- **Schema version:** `1`

No snapshot content is restated here. Departures from the template shape are disclosed in § 17.

## 17. What this record does not contain

**The open question for the operator (why the study stopped).** The owner ruled that `energy_price`, which reports `no_constraint_response`, should "proceed … as sensitivity-only". The only route the operator named is `execute_baseline` and `run_grid` in `studies/study_route.py`. `run_grid` takes no points: it runs the module's fixed `GRID`, which is basin_area {4, 8, 12, 16} × installed_capacity {0.20, 0.25, 0.30} with energy_price held at 0.10. So no named route callable can execute an energy_price point. The policy says "nothing else is a route". Calling the module's unnamed `run_points` helper, or editing `GRID` or the route, would each be the executor choosing an execution route. The question:

> **How should the energy_price axis be executed?** (a) Extend the named route, for example a `run_grid` that accepts the study's points or a grid that includes energy_price, and name it in policy § 6. (b) Admit `study_route.run_points` as a named route callable. (c) Execute only basin_area × installed_capacity through `run_grid` and leave energy_price answered by its indicator alone, which revises the "proceed" ruling. And relatedly: is the route's pre-fixed `GRID` acceptable as the study window (engineered), given runbook step 7 fixes the window after the scan?

**Gaps in this record:**
- No study point ran. There is no objective result over a studied space, and no constraint outcome beyond the baseline point (§§ 3, 4).
- No judged framing (§ 5) and no per-axis account (§ 6).
- No fixed window. `snapshot.json` has no `arms[].window`.
- No verification (§ 13): `results/verification_summary.json` does not exist. No step-12 review and no report (step 13).
- `snapshot.json` has `arms: []` and `stores[]` holds only the baseline store. Fields the template scopes to arms are absent: `effective_executable_fingerprint`, `entry_models`, `strategy`, `window`, `verification`, `glue_ledger`, `artifacts`. Two top-level fields outside the template shape were added to say so: `arms_none_reason`, and `pre_execution_artifacts`, which digests the step 5–6 results. A `status` field states the stop.
- The annex (`studies/ANNEX.md`) and manifest (`studies/manifest.json`) are executor-drafted and not owner-ratified. The baseline pin's provenance is the model file's own comment.
- `sysml-codegen study integrate` was not run. The project has no audited work item, no `[tool.sysml-codegen.integrate]` declaration and no tracked census, so its gates 1a, 4 and 5 could not judge.
- Route scratch from step 5 was removed before digesting: `results/_work/link/`, an absolute symlink to the package, and an empty `results/_work/staging/` directory. The store and its artifact are kept.
- The study policy is still marked "Template, not ratified by this project". This record cites it as it stands.

---

**END OF RECORD**

## Addendum 2026-10-12

The § 17 operator question was answered on 2026-10-12. The operator's rulings:

1. Option (c): run basin_area × installed_capacity only, on the named route's grid. energy_price is answered by its indicator alone, because its structural `no_constraint_response` is the finding for "whether the energy price matters to it". energy_price is not swept.
2. The route's pre-set `GRID` is accepted as the study window. It was fixed in the route before the oracle scan; the scan then confirmed that both verdicts appear and that no point sits on the boundary.

The operator asked for the question to be moved from § 17 to where the runbook records operator rulings. This record was already committed, so its prior text is left as written, per its immutability rule. The question and the rulings are recorded in § 8 of the continuation record. Continuing would change snapshot values (arms, window, verification), and a changed snapshot value is a different study. So the study continues as `20261012-pump-fit-response-b` (`studies/20261012-pump-fit-response-b/record.md`), which re-runs steps 1–7 so that it stands alone, and then runs steps 8–15. Finding `20261012-pump-fit-response#3` carries a joined disposition row in `DISCOVERY_LOG.md`.
