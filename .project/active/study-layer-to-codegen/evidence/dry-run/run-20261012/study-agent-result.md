session 26d32721-0b1b-46ee-95ef-078347c59ecf  result success  cost $1.91  turns 34

I stopped the study at runbook step 7 on a question only you can answer, and committed the record so far (`5eb5dbb`) at `studies/20261012-pump-fit-response/`. No study points ran, so there is no result yet for how pump-fit responds to basin area or capacity.

**The question (record § 17).** You ruled that energy price goes ahead as sensitivity-only. But the only route you named, `run_grid`, runs a fixed grid: basin area 4, 8, 12, 16 × installed capacity 0.20, 0.25, 0.30, with energy price held at 0.10. Nothing in the named route can run an energy-price point. Using the module's unnamed `run_points`, or editing the grid, would mean I picked the route myself. So: should I
- (a) extend the named route,
- (b) admit `run_points` as a route callable, or
- (c) run only basin area × capacity and let energy price be answered by its indicator alone?

Also: is the route's pre-set grid acceptable as the study window? The runbook says the window should be fixed after the oracle scan, and this one was fixed in the route code beforehand.

**What ran:**
- **Indicators (step 3):** basin area reaches `pump_fit` through the required-flow side, and installed capacity is its capacity side. Energy price reports `no_constraint_response`: no path reaches `pump_fit`, only the annual cost. So structurally, energy price does not matter to the pump-fit constraint. I recorded your ruling and the required model-development finding (#1): nothing in the model limits operating cost.
- **Baseline and preflight (steps 5–6):** the baseline reproduced the pinned 192.0 annual cost, with `pump_fit` satisfied. All six preflight gates passed.
- **Oracle scan (step 7):** the route's grid would produce both verdicts, with no point on the boundary (required flow = 0.30 − 0.005 × area). Basin areas above 60 give a negative required flow that no constraint catches. That is finding #2, applied as a validity mask.
- **Checks:** the step 14 and 15 checks are recorded in § 14. They printed `[]`, `0`, `[]`, `[]`, `[]`. The last two are vacuous, because no study arm exists yet; the record says so.

**Things I added that you should check:**
- **Annex and manifest:** the project had no `studies/ANNEX.md` or `studies/manifest.json`. I wrote both from the model file, and they are marked as mine and not yet approved by you (finding #4). The baseline pin comes from the arithmetic in the model file's header comment.
- **Study policy:** I filled § 10 Locations with `studies/` as you asked. I also filled § 6 Execution routes with the route you named. The policy itself is still marked as an unratified template (finding #5).
- **`sysml-codegen study integrate` was not run:** it requires an audited work item, an integrate declaration in `pyproject.toml` and a tracked census, and the project has none of these.
- **Snapshot shape:** because no arm ran, `snapshot.json` has `arms: []` and three extra top-level fields that say so (`status`, `arms_none_reason` and `pre_execution_artifacts`). § 17 lists these departures from the template.
