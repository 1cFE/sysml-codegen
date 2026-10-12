# Discovery log — `station_study`

Append-only index, newest row last. One row per finding sighting, joined to its record by `<study-id>#<n>`; the record's § 15 holds the account. Format: the run-study runbook, § `DISCOVERY_LOG.md`.

| Date | Kind | Record | Finding | Disposition | Home |
|---|---|---|---|---|---|
| 2026-10-12 | `model` | `20261012-pump-fit-response#1` | energy_price reaches no constraint: nothing in the model pushes back on operating cost | open; owner ruled the axis proceeds as sensitivity-only, which does not discharge this | unrouted |
| 2026-10-12 | `model` | `20261012-pump-fit-response#2` | required_flow goes negative for basin_area above design_inflow / allowed_rise_rate (60.0 at the design values) and no constraint catches it | open; applied as a validity mask in the annex | unrouted |
| 2026-10-12 | `process` | `20261012-pump-fit-response#3` | the named route cannot execute the energy_price axis: run_grid runs a fixed area-by-capacity grid only | open; study stopped at step 7 pending operator ruling | unrouted |
| 2026-10-12 | `process` | `20261012-pump-fit-response#4` | the project supplied no annex or manifest; the executor drafted both from the model text | open; awaiting owner ratification | `studies/ANNEX.md` |
| 2026-10-12 | `process` | `20261012-pump-fit-response#5` | the study policy is an unratified template and its § 1 current-state line is unfilled | open | `modeling_project/STUDY_POLICY.md` |
| 2026-10-12 | `process` | `20261012-pump-fit-response#3` | the named route cannot execute the energy_price axis: run_grid runs a fixed area-by-capacity grid only | resolved by operator ruling 2026-10-12: option (c), sweep basin_area by installed_capacity only and answer energy_price by its indicator; continued as 20261012-pump-fit-response-b | `studies/20261012-pump-fit-response-b/record.md` |
| 2026-10-12 | `model` | `20261012-pump-fit-response-b#1` | energy_price reaches no constraint: nothing in the model pushes back on operating cost (re-sighting of 20261012-pump-fit-response#1) | open; operator ruled the axis answered by its indicator and not swept, which does not discharge this | unrouted |
| 2026-10-12 | `model` | `20261012-pump-fit-response-b#2` | required_flow goes negative for basin_area above design_inflow / allowed_rise_rate (60.0 at the design values) and no constraint catches it (re-sighting of 20261012-pump-fit-response#2) | open; outside this study's window, applied as a validity mask in the annex | unrouted |
| 2026-10-12 | `process` | `20261012-pump-fit-response-b#3` | the annex and manifest are executor-drafted from the model text and not owner-ratified | open; awaiting owner ratification | `studies/ANNEX.md` |
| 2026-10-12 | `process` | `20261012-pump-fit-response-b#4` | the study policy is an unratified template and its § 1 current-state line is unfilled | open | `modeling_project/STUDY_POLICY.md` |
| 2026-10-12 | `process` | `20261012-pump-fit-response-b#5` | the runbook has no resume path for a record committed while stopped on an operator question: immutability forced a new study id, and steps 1-7 were re-run | open | runbook step 15 |
| 2026-10-12 | `process` | `20261012-pump-fit-response-b#6` | the study window is the route's GRID, fixed in route code before the step-7 oracle scan rather than after it | accepted by operator ruling 2026-10-12; scan confirmed both verdicts and no on-boundary point | `studies/study_route.py` |
