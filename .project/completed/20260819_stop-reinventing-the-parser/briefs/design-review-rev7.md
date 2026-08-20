# Brief — Targeted design review: Revision 7 amendment only

Review `.project/active/stop-reinventing-the-parser/design.md` Revision 7. **Scope: the amendment
only.** Revision 6 was reviewed and approved (`design-review.md`, "Approve (Revision 6)"); do not
re-litigate what that review already approved. Your job is to confirm the five amended areas are
correct, complete against the ratified rulings, and change no approved mechanism.

Read in order:

1. The Revision 7 diff: `git show f53ae94` in this checkout — that is the exact amendment.
2. `.project/active/stop-reinventing-the-parser/run-records/phase1-stop-report.md` — the evidence
   record (revision 3). The seven rulings at its end are **owner-ratified 2026-08-17** and binding;
   the amendment must implement them faithfully.
3. `design-review.md` — for what the Revision-6 verdict already covers.
4. `plan.md` rev 2 — to check the amendment leaves every anchor the plan links to intact and gives
   Plan Revision 3 what the handoff promises.

For fact-checking there is a clean read-only worktree at `C_base`:
`/tmp/stop-parser-rev2/worktrees/sysml-codegen` (`78a9beb9…`). Key files:
`verification/capture_baseline.py`, `verification/expected-transitions.md`,
`verification/probe-fixture-lock.json`, `src/sysml_codegen/extraction/source_evidence.py`,
`tests/fixtures/deep_cross_scope_probe/`. Probe models: `/tmp/stop-parser-rev2/scratch/`. Do not
modify anything outside design-review.md.

## What to verify

1. **Faithfulness to the rulings.** Each of rulings 1-7 must be implemented exactly — especially:
   lock preserved and never re-derived (a mismatch returns to design, never authorizes a re-lock);
   the two-leg verification stated correctly against the implemented contract in
   `capture_baseline.py`; both indexed red cases required as kept tests with their recorded
   `C_base` diagnostics; `deep_cross_scope` never-restore as a stop condition.
2. **Factual accuracy.** Every hash, commit, count, code citation, and behavior claim in the
   amendment must match the stop report's [verified] record and, where cheap, the `C_base` tree
   itself. A wrong SHA or line number in a design that governs byte-level gates is a finding.
3. **No weakened obligation.** The amendment claims every Revision-6 closure requirement stays as
   strong or stronger. Check for accidental loosening — e.g., does replacing the byte-identity rule
   leave any file class unverified by either leg? Does any reworded gate drop an assertion?
4. **No mechanism change.** D1-D10, closed variants, artifact chain, topology, manifests untouched.
   Judge whether new D11 truly adds no mechanism (it claims to restate D7's ordering plus a
   diagnostic/test obligation). If it smuggles in behavior D7 does not already require, say so.
5. **Internal consistency.** New A5a/A5b rows vs the pre-existing A5 row; the frozen/current table
   vs the anti-vacuity counts; the handoff's Plan-Revision-3 obligations vs what the amended
   sections actually require; anchor integrity for every `design.md#…` link in plan.md.

## Deliverable

Append a clearly-delimited "Targeted review — Revision 7 amendment" section to
`.project/active/stop-reinventing-the-parser/design-review.md` (do not rewrite prior review
content; do not commit). Findings ranked; each with severity (Critical / Major / Minor), the exact
design.md location, and what correct looks like. End with a verdict for the amendment:
`Approve` or `Revise`, and if Revise, the minimal must-fix set. Final message: prose summary of
verdict and findings, ending with
`ARTIFACT: .project/active/stop-reinventing-the-parser/design-review.md`.
