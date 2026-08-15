# Stage brief — Close the Phase 4 audit findings (runbook to genuinely mechanical)

**You are closing the eight findings** in
`.project/active/cutover-recovery/evidence/audit-4.md` (committed at `ee8fc40` — read it in
full first, including the machinery-ceiling notes and the not-verified list) against the plan
`/home/reid/1cfe/sysml-codegen-item7-rebuild/.project/active/cutover-recovery/plan.md`.
Environment discipline binding (assert import paths; license; measured gates only).

## The bar

The acceptance packet may only call the retirement mechanical if a fresh agent could execute it
from the runbook alone, with the audit's simulation method proving each step's post-state in
advance. The audit showed that is not yet true. Make it true — by measurement, not assertion.

## Required

1. **F1+F2 (high):** rebuild the runbook so every one of the 66+131+34 rows is named by exactly
   one step (or the owner-gated fifth entry), each step has a complete edit table, and each
   step's post-state is PROVEN by the audit's own method — execute the step in a scratch
   worktree, run the full battery there, record the numbers in the runbook, discard the
   worktree. That includes the transitive-breakage class the checker cannot see: the scratch
   run IS the detector; fold every discovered edit back into the table until the scratch run
   is green. Fix L-298's false note and the missed `test_d5_variants.py:116` assertion; the
   v5-refusal pins must survive step 1 in the simulated run. If a step cannot be made green
   without a decision that is not yours, name it and put it in the fifth entry — do not soften.
2. **F3 (medium):** correct CLAUDE.md's closure sentence to the measured 10-of-11 (and re-check
   the four-module pin statement stays true).
3. **F4 (medium):** add the batch-revision cost to the Phase 5 packet section: revising the
   PROPOSED batch costs 38 failed + 57 errors of dependent evidence until recaptured —
   Git-reversible, not free. State it plainly.
4. **F5–F8 (low):** fix the two additional stale docstrings if they are in files the retirement
   doesn't rewrite anyway (else note them in the relevant step's edit table); give
   `check_proof_integrity.py` the failure path + tests the audit found missing (it must be able
   to fail); record the four machinery ceilings in the checker's own docs; delete the dead
   alias.

## Rules

Batteries per commit; scratch-worktree simulations never touch the real tree; nothing retires
for real (the acceptance gate stands); rule-10 stops as established.

## Report back

Per-finding closure with the simulation numbers per runbook step, the final runbook state, OIDs.
`ARTIFACT:` the updated plan.
