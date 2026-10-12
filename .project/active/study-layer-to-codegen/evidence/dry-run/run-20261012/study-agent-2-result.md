session 26d32721-0b1b-46ee-95ef-078347c59ecf  result success  cost $3.07  turns 17

The study is finished and committed (`ec99f16`). Basin area and installed capacity both flip the pump-fit verdict within the grid, and energy price cannot affect it. One departure from your instructions: the results are in a new record, `studies/20261012-pump-fit-response-b/`, not the stopped one.

**Why a new record.** The first record was already committed, and the runbook makes a committed record immutable. Its text can only be corrected by an appended addendum, and a changed snapshot value counts as a different study with a new id. So I couldn't move the question out of its § 17 or add the run to its snapshot. What I did instead:
- **Stopped record:** I appended an addendum that records your two rulings and points to the new record. Nothing in it was edited.
- **New record:** your question and both rulings are in § 8, where the runbook records operator rulings. Steps 1–7 were re-run there so it stands on its own; the indicators and baseline came out identical. Steps 8–15 then ran in full.

If you'd rather I had edited the committed record in place, that would override the runbook's immutability rule, so it's your call. I logged the missing resume path as finding #5.

**Results** (12-point grid; energy price held at 0.10):
- **Pump fit** is satisfied at 7 points and violated at 5.
- **Basin area:** a larger basin lowers the required flow, from 0.28 at area 4 to 0.22 at area 16. At capacity 0.25 the verdict flips between area 8 and area 12. At capacity 0.20 every area fails; at 0.30 every area passes.
- **Installed capacity:** at every area, raising capacity moves the verdict from violated to satisfied. The flip is between 0.25 and 0.30 at areas 4 and 8, and between 0.20 and 0.25 at areas 12 and 16.
- **Limits:** boundaries are located only to within a grid cell, and nothing is claimed outside the grid.
- **Energy price** was not swept, per your ruling. Its indicator shows no path from energy price to either side of the pump-fit constraint; it only affects annual cost. So in this model it cannot change the verdict.
- **Verification:** all 12 points agree with the independent oracle at 0.0 deviation, and the verdicts re-derive with no mismatches. One caveat in § 13: the capacity side of the constraint is the swept input itself, so only the required-flow side is independently checked.
- **Checks:** the step-14 and step-15 checks are recorded in § 14 and printed `[]`, `0`, `[]`, `[]`, `[]`.

**Still open, none of them blocking:**
- The annex and manifest are mine, drafted from the model, and not yet approved by you (#3).
- The study policy is still an unratified template (#4).
- Two gaps in the model: nothing limits operating cost (#1), and required flow goes negative above basin area 60 (#2).
- `sysml-codegen study integrate` was not run, because the project has no audited work item, integrate declaration or census.
