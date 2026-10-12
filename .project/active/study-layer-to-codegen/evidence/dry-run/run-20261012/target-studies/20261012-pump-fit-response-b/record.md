# Study record — `20261012-pump-fit-response-b`

Written from the run-study `record-template.md`. The values live in `snapshot.json` and the arguments live here. Once committed, this file is corrected only by an appended `## Addendum` section.

---

## 1. Study header

- **Study id:** `20261012-pump-fit-response-b`
- **Package:** `pkg/station_study`
- **Date executed:** `2026-10-12`
- **Executor:** Claude (Opus 5.5) Claude Code session, run-study skill, execute mode
- **Mode:** execute
- **Arms:** `arm-main` (single arm)

This record continues `20261012-pump-fit-response`, which stopped at runbook step 7 on an operator question and is committed unchanged apart from an addendum. That record's snapshot cannot change, so this continuation has its own study id. Steps 1–7 were re-run here so that this directory stands alone, and steps 8–15 follow.

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

The operator's later rulings on the stopped record's question are in § 8.

**Executor's additions (not the owner's words).**
- Three candidate axes, one per named attribute: `basin_area`, `installed_capacity`, `energy_price` (`PumpStation::station::*`).
- "The pump-fit constraint" is `PumpStation__station__pump_fit__aa8dd6c31b6b238a` (`PumpStation::CapacityCoversDemand`, local identity `pump_fit`), the model's only executing constraint.
- `studies/ANNEX.md` and `studies/manifest.json` were drafted by the executor of the stopped record from `models/station.sysml`, the package's pipeline and contracts, and `studies/oracle_entry.py`. They are not owner-ratified (finding #3).

## 3. Objective and result

- **Objective channel(s):** `PumpStation__station__pumping__annual_cost` (catalog name `annual_pumping_cost`), and `PumpStation__station__demand__required_flow` (catalog name `required_flow`, the pump-fit `demand_flow` operand)
- **Objective result:** over the 12-point grid, annual_cost ranges from 176.0 at basin_area 16.0 to 224.0 at basin_area 4.0, at every installed_capacity. It is unit-less in the model. Source: `results/grid_cases.json`.

On the grid, both channels depend on basin_area alone. required_flow is 0.28, 0.26, 0.24 and 0.22, and annual_cost is 224.0, 208.0, 192.0 and 176.0, at areas 4, 8, 12 and 16. installed_capacity changes neither. No optimum is sought: the objective policy is empty (`ObjectivePolicy((), {})` on the route).

## 4. Constraint outcomes

Every executing constraint, by qualified identity, with its status.

| `constraint_id` | `source_local_identity` | Status | Note |
|---|---|---|---|
| `PumpStation__station__pump_fit__aa8dd6c31b6b238a` | `pump_fit` (`PumpStation::CapacityCoversDemand`, usage `PumpStation::station::pump_fit`) | satisfied at 7 of 12 points, violated at 5 | Violated at every area at capacity 0.20, and at areas 4 and 8 at capacity 0.25. Satisfied elsewhere. Every case completed with constraint coverage `complete` (`results/grid_cases.json`, store `results/_work/station-grid-v1.db`). |

## 5. Framing

**As proposed at intake.**

| Axis | Framing proposed | Why |
|---|---|---|
| `basin_area` | search | `constraints_reachable`: reaches `pump_fit` through its computed `demand_flow` operand. A verdict boundary is expected. |
| `installed_capacity` | search | `constraints_reachable`: is `pump_fit`'s bound `capacity` operand directly. A verdict boundary is expected. |
| `energy_price` | sensitivity (proposed); declined from sweeping by operator ruling | `no_constraint_response`. The initial ruling was "proceed as sensitivity-only". The later ruling (§ 8) answers the axis by its indicator alone and does not sweep it. |

**As judged after the run.**

| Axis | Framing judged | Changed? | Why |
|---|---|---|---|
| `basin_area` | search | no | The verdict flips with area at capacity 0.25 (violated at 4 and 8, satisfied at 12 and 16). There is verdict structure, not full feasibility. |
| `installed_capacity` | search | no | The verdict flips with capacity at every area. The flip location shifts with area. |
| `energy_price` | not swept | not applicable | Declined by the operator's ruling. No run result exists to judge it against. The indicator answer stands (§ 6). |

## 6. Per-axis account

#### `basin_area` — feasible structure (search framing)
**Applies:** yes

`pump_fit` is the active constraint, through its `demand_flow` operand (required_flow, which falls as area rises on the grid: 0.28 → 0.22).
- At capacity 0.25, the boundary lies between area 8.0 (violated, margin −0.01) and 12.0 (satisfied, margin +0.01).
- At capacity 0.20, the whole area range is violated, and at 0.30 the whole range is satisfied, so there is no flip inside the window at those capacities.
- No constrained optimum is claimed, because no objective policy was set.

The boundary is located only to the grid cell. No point sits on it, and nothing is claimed between grid points or outside the window.

#### `basin_area` — observed response (sensitivity framing)
**Applies:** not applicable — this axis is search-framed

#### `installed_capacity` — feasible structure (search framing)
**Applies:** yes

`pump_fit` is active through its `capacity` operand. At every area the verdict goes from violated to satisfied as capacity rises across the grid. The flip lies between 0.25 and 0.30 at areas 4.0 and 8.0, and between 0.20 and 0.25 at areas 12.0 and 16.0. A larger basin lowers the capacity needed to fit. No constrained optimum is claimed. As with basin area, the boundary is located only to the grid cell.

#### `installed_capacity` — observed response (sensitivity framing)
**Applies:** not applicable — this axis is search-framed

#### `energy_price` — feasible structure (search framing)
**Applies:** not applicable — this axis is not search-framed. It was declined from sweeping by operator ruling (§ 8).

#### `energy_price` — observed response (sensitivity framing)
**Applies:** not applicable — energy_price was not swept, by operator ruling (§ 8). There is no observed response.

What answers "whether the energy price matters to it" is the indicator. `energy_price` has `no_constraint_response`: neither `pump_fit` operand is reachable from `PumpStation__station__energy_price`, and only `annual_pumping_cost` is (`indicators.json`). No boundary claim is made, and no run-derived claim about energy_price is made at all.

## 7. Axis groups

Every declared qualified entry key, with its per-key provenance. Declaration file: `axes.json`.

| Axis | Entry key | Provenance | Note |
|---|---|---|---|
| `basin_area` | `PumpStation__station__basin_area` | fan_out | the attribute's only entry key in `pipelines/pipeline.yaml` (feeds `pumpstation__station__demand.area`) |
| `installed_capacity` | `PumpStation__station__installed_capacity` | fan_out | the attribute's only entry key (feeds `pump_fit.capacity`) |
| `energy_price` | `PumpStation__station__energy_price` | fan_out | the attribute's only entry key (feeds `pumpstation__station__pumping.price`). Declared and traced, then declined from sweeping. |

No ties are declared (annex § Declared ties).

## 8. Indicators and rulings

Per proposed axis, including axes proposed and declined. Source: `indicators.json`, `subset: false`, no warnings. Its content is identical to the stopped record's indicator run apart from the axis-declaration path.

| Axis | Indicator | Ruling | Note |
|---|---|---|---|
| `basin_area` | `constraints_reachable` | none needed | Reaches `pump_fit` via `demand_flow` (computed). Reaches both objectives. Swept. |
| `installed_capacity` | `constraints_reachable` | none needed | Reaches `pump_fit` via `capacity` (bound, the design attribute itself). Reaches no objective. Swept. |
| `energy_price` | `no_constraint_response` | Operator, before execution: first "proceed with it as sensitivity-only", then superseded by the ruling below | Reaches `annual_pumping_cost` only. **Declined, not swept**, by the operator's ruling. |

**The operator question and its rulings (moved here from the stopped record's § 17).** The question was: the named route's `run_grid` runs a fixed `GRID` (basin_area {4, 8, 12, 16} × installed_capacity {0.20, 0.25, 0.30}, energy_price held at 0.10), so no named route callable can execute energy_price, which was ruled to proceed. How should energy_price be executed: (a) extend the route, (b) admit `run_points`, or (c) sweep area × capacity only and answer energy_price by its indicator? And is the route's pre-fixed `GRID` acceptable as the window? The operator ruled on 2026-10-12, before any study point ran:

1. Option (c). Run basin_area × installed_capacity only, on the named route's grid. energy_price is answered by its indicator alone: the structural `no_constraint_response` is the finding for "whether the energy price matters to it". energy_price was not swept.
2. The route's pre-set `GRID` is accepted as the study window. It was fixed in the route before the oracle scan; the scan then confirmed both verdicts appear and no point sits on the boundary; the operator accepted it (see § 11).

**Not derivable, disclosed in every record.** These are not decidable from the indicator run and no indicator output claims them: monotonicity of any channel in any axis; identity of the same physical quantity across differing key names; intra-module operand dependency. `constraints_reachable` is a *possible* path and never a statement that a constraint responds. `unresisted` is the agent's recorded judgment, never a tool output.

**Model-development findings.** Every `no_constraint_response` axis carries one, in addition to the user's ruling. The ruling does not discharge it.

| Axis | What should push back and is not modeled | Finding id |
|---|---|---|
| `energy_price` | Nothing in the model limits operating cost. No constraint bounds `annual_cost` (for example, a sourced operating budget), and energy price does not feed the capacity or sizing decision. So the price can move cost without limit and no verdict changes. | `20261012-pump-fit-response-b#1` |

## 9. Preflight results

Source: `results/preflight_results.json` (`sysml-codegen study preflight gates`, outcome `pass`). The gates read `results/package_identity.json` and `results/baseline_result.json`, which `execute_baseline` deposited at step 5. A post-run package-cleanliness check is in `results/postrun_clean.json` (pass).

| Gate | Outcome | Detail |
|---|---|---|
| Declared-group key validation | pass | 3 declared keys across 3 groups, all package inputs |
| Suffix-sibling scan (warnings only) | pass | no siblings found |
| Baseline gate against the pinned headline | pass | `PumpStation__station__pumping__annual_cost` expected 192.0, observed 192.0 (relative deviation 0.0); 1/1 pinned verdicts match (`pump_fit` satisfied) |
| Manifest / package fingerprint match | pass | both recorded package fingerprints match the package on disk; identity gate: sealed digest `75c3cc58…8c00` recomputed, every sealed artifact matches |
| Package cleanliness | pass | git clean before the run (preflight) and after it (`results/postrun_clean.json`) |

## 10. Execution route and why

- **Route:** `station_study_route`: `studies/study_route.py`, using `execute_baseline` for the baseline (step 5) and `run_grid` for the study's points (step 9).
- **Why this route:** it is the only route the study policy's § 6 names, and the operator named it. Its `run_grid` runs exactly the window the operator accepted. By the operator's ruling the study sweeps only basin_area × installed_capacity, so the route's fixed grid covers the whole study. Before step 9 it had already loaded the sealed package and passed every preflight gate.

**Glue disclosure.** Glue ledger: none. Nothing on this route is harness-supplied. The route loads the sealed package through teax's own seal-checking loader and runs points through `StudyRunner`, with no adapter and no injected values. The preflight identity gate recomputed the sealed digest from 0 allowed-modified files.

## 11. Study definition and window provenance

The window was **fixed in the route before the oracle scan**: it is the `GRID` constant in `studies/study_route.py`. The step-7 oracle scan (`results/oracle_scan.json`, `oracle_entry.evaluate` over every grid point) then confirmed that both pump-fit verdicts appear and that no point sits on the boundary (smallest |margin| 0.01). The operator accepted this grid as the study window on 2026-10-12 (§ 8).

The window is **engineered**. The route's docstring says it was chosen so that both verdicts occur and no point sits on the boundary. That costs the following:
- the grid makes no claim about where the design range is physically meaningful;
- the boundary is located only to the grid cell;
- nothing is claimed outside area 4–16 or capacity 0.20–0.30.

The window stays inside the annex § Validity masks bound (area ≤ 60.0 at the held-fixed design_inflow and allowed_rise_rate).

## 12. Cross-fingerprint correlation and what it means

Single fingerprint — no cross-arm correlation needed. One arm. The baseline and grid stores both ran under the sealed executable fingerprint `75c3cc58959e064834c27f0babce156dc042d099bba4b286fe8fefb385b78c00` and model-contract fingerprint `e2240e55…cf6f`.

## 13. Verification

Pass. All 12 grid cases were sampled across the 2 observed verdict strata. Both calculated channels (required_flow, annual_cost) agree with the independent oracle at a worst relative deviation of 0.0. The `pump_fit` verdict was re-derived from the oracle's operands at every sampled case with no mismatches. This licenses the statement that the package's channels and verdicts on this grid match an independent recomputation from the model text (`results/verification_summary.json`).

What verification did not cover:
- The `capacity` operand is bound to the swept input itself, so it is identical by construction on both sides and not independently verified. Only the `demand_flow` side (required_flow) is an independent recomputation.
- The oracle and the package derive from the same model text, so verification checks code generation and execution, not the model's physics.
- Points off the grid, the energy_price axis and the constraint report aggregator were not verified.
- `verify` records the teax revision as "unrecorded". The run's teax revision is in `snapshot.json` `teax`.

## 14. Review outcomes

| Lens | Verdict | Disposition |
|---|---|---|
| Step 4 pre-execution framing check (coordinator check, per the operator's "a coordinator review check suffices") | Framing follows the indicators: two search axes reaching `pump_fit`, and one `no_constraint_response` axis with operator rulings and a model-development finding (#1). No new or reinterpreted source or math needs an independent check. | Accepted. No independent critique was triggered (single model family, no coupled architecture, no failed coverage). |
| Step 12 correctness (coordinator check) | Store results equal the step-7 oracle scan at all 12 points, and `verify` passed at 0.0 deviation. Verdict counts (7 satisfied, 5 violated) were checked against `results/grid_cases.json`. | No finding. |
| Step 12 claim limits (coordinator check) | Boundary claims are limited to the grid cell. No monotonicity claim is drawn from the indicators. The energy_price claim is structural only. The engineered window is disclosed. | No finding. |
| Step 12 readability (coordinator check) | The operator rulings sit in § 8. The continuation relationship to the stopped record is stated in § 1 and in that record's addendum. | No finding. |
| Coordinator check of executor-drafted annex and manifest | Every fact was cross-checked against the model, pipeline and contracts, and validated mechanically by indicators and preflight. | Owner ratification is still outstanding (finding #3). |

**Runbook step 14 check**, run from the record directory:

```bash
python3 -c "import sys; sid = sys.argv[1] + '#'; bar = chr(124); ids = lambda path, col: {c for line in open(path) if line.startswith(bar) for c in [line.split(bar)[col].strip().strip(chr(96))] if c.startswith(sid)}; print(sorted(ids('record.md', 1) ^ ids('../DISCOVERY_LOG.md', 3)))" 20261012-pump-fit-response-b
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

Printed: `[]`

```bash
# []: every result artifact has a digest
python3 -c "import json; s = json.load(open('snapshot.json')); print([f['path'] for a in s['arms'] for f in a['artifacts'] if not f.get('sha256')])"
```

Printed: `[]`

## 15. Findings

Each finding gets an id used verbatim in `DISCOVERY_LOG.md`.

| Id | Kind | Finding | Disposition | Home |
|---|---|---|---|---|
| `20261012-pump-fit-response-b#1` | model | energy_price reaches no constraint: nothing in the model pushes back on operating cost (re-sighting of the stopped record's #1) | open; operator ruled the axis answered by its indicator and not swept, which does not discharge this | unrouted |
| `20261012-pump-fit-response-b#2` | model | required_flow goes negative for basin_area above design_inflow / allowed_rise_rate (60.0 at the design values), and no constraint catches it (re-sighting of the stopped record's #2) | open; outside this study's window, applied as a validity mask in the annex | unrouted |
| `20261012-pump-fit-response-b#3` | process | the annex and manifest are executor-drafted from the model text and not owner-ratified | open; awaiting owner ratification | `studies/ANNEX.md` |
| `20261012-pump-fit-response-b#4` | process | the study policy is an unratified template and its § 1 current-state line is unfilled | open | `modeling_project/STUDY_POLICY.md` |
| `20261012-pump-fit-response-b#5` | process | the runbook has no resume path for a record committed while stopped on an operator question: immutability forced a new study id, and steps 1-7 were re-run | open | runbook step 15 |
| `20261012-pump-fit-response-b#6` | process | the study window is the route's GRID, fixed in route code before the step-7 oracle scan rather than after it | accepted by operator ruling 2026-10-12; scan confirmed both verdicts and no on-boundary point | `studies/study_route.py` |

**Homes a finding may route to:** tool, runbook step, policy rule, skill, modeling item, research round, documented seam. `unrouted` is a stated state, not a blank.

## 16. Snapshot

- **File:** `snapshot.json`
- **sha256:** `e08b077f495eef6d8e82113423837e8f99917dbcd8df24cec46fc2f82581e594`
- **Schema version:** `1`

No snapshot content is restated here.

## 17. What this record does not contain

- **No swept energy_price result.** energy_price was not swept, by operator ruling (§ 8). Its only evidence is the indicator.
- **No boundary location finer than the grid cell**, and no result outside basin_area 4–16 or installed_capacity 0.20–0.30.
- **No constrained optimum.** The route's objective policy is empty.
- **`sysml-codegen study integrate` was not run.** The project has no audited work item, no `[tool.sysml-codegen.integrate]` declaration and no tracked census, so its gates 1a, 4 and 5 could not judge.
- **Route scratch was removed before digesting:** `results/_work/link/`, an absolute symlink to the package, and empty `results/_work/staging/` directories. The stores and their artifacts are kept.
- **Snapshot additions and gaps:**
  - `stores[]` also lists the step-5 baseline store, labeled as not an arm store.
  - `arms[].strategy` names the strategy identity and config digest but not the point list. The 12 points are in `results/grid_cases.json` and `arms[].window`.
  - The verify tool records the teax revision as "unrecorded". The revision in `snapshot.json` `teax` was read from `TEAX_SIMKIT_PATH` by `git rev-parse`.
- **No owner ratification** of the annex, the manifest or the study policy (findings #3 and #4).

---

**END OF RECORD**
