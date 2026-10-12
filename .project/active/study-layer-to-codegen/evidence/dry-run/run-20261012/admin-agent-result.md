session 444180b4-8e7b-467f-934a-864af600a111  result success  cost $0.95  turns 17

I wrote `studies/20261012-pump-fit-response-b/synthesis.md`, and no other file changed. Opening the two result databases read-only left four empty helper files beside them; I deleted those. Both databases still match the digests in `snapshot.json`, and `git status` now shows only the new file.

I read only `record.md`, `snapshot.json`, `indicators.json` and `results/`. I didn't open `axes.json`: it's in the record directory but wasn't on your list, and the per-axis details I needed are also in `indicators.json`. Every file's digest matches what `snapshot.json` records, and so does the snapshot's own digest (`e08b077f…e594`).

**What the study found:**
- **Result:** the pump-fit constraint (installed capacity ≥ required flow) is satisfied at 7 of the 12 grid points and violated at 5. The stored results, the oracle scan and the 12 per-case files agree point for point, and verification matched exactly.
- **Basin area:** a larger basin lowers the required flow, which makes the constraint easier to meet. At capacity 0.25 the verdict flips between area 8 and area 12. The boundary is only known to within one grid cell.
- **Installed capacity:** at every area the verdict goes from violated to satisfied as capacity rises. It flips between 0.25 and 0.30 at areas 4 and 8, and between 0.20 and 0.25 at areas 12 and 16.
- **Energy price:** it was never swept. The only answer is the structural check, which found no path from price to the constraint. One sentence in `results/report.md` words this more absolutely than that check supports, and the synthesis points this out.
- **Framing:** I agree with the record's framing of all three axes. The record's six findings are carried forward as recorded.

**Missing from the record** (listed as missing in the synthesis, not looked up elsewhere):
- The stored inputs for each grid point hold only area and capacity. The values held fixed, including energy price at 0.10, appear only as a statement in `snapshot.json`.
- The grid's source in the route code, the reason it was chosen, and the claim that it was fixed before the oracle scan are not in the directory.
- The operator's later rulings appear only as the executor's restatement, not in the operator's own words.
- Things the record points to but doesn't contain: the earlier stopped record, the annex, the study policy, the discovery-log rows and the oracle's source code.
- The teax version used is recorded in `snapshot.json` but marked "unrecorded" in the verification output.
- The baseline run's per-case evidence file wasn't kept.
- Every review in the record is the executor's own check; there was no independent review.

**Gaps in the record format (A–E in the synthesis)**, which I haven't added to the discovery log; whoever acts on the synthesis should file them:
- The verification output lists nothing as "not independently verified", yet the capacity side of the constraint is identical on both sides by construction.
- The format doesn't require keeping the grid's source in the record.
- It doesn't require operator rulings made after intake to be kept verbatim.
- A continuation record cites the record it continues without carrying any of its content.
- The values held fixed at each point aren't stored.
