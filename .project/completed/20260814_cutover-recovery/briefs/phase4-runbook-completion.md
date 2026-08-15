# Stage brief — Runbook completion: prove steps 2–4 by the scratch method

**You are completing the retirement runbook** of the recovery plan:
`/home/reid/1cfe/sysml-codegen-item7-rebuild/.project/active/cutover-recovery/plan.md`.
Read first: the runbook as rebuilt at `5b682c1` (step 1 proven; step 2's production table
complete but its per-node test table unwritten — 86 failed + 58 errors across 33 surviving
files; steps 3–4 unreached), `evidence/audit-4.md`, the six owner-gated items, and the
part-6/part-7 re-derivation records (the bar and the mechanism citations). Environment
discipline binding.

## The form of the work

The retirement executes post-acceptance, so prepared work lives as REVIEWABLE PATCHES, proven
in scratch, applied for real only after the owner accepts:

- `.project/active/cutover-recovery/runbook-patches/step2/*.patch` (and step3/, step4/ as
  needed): the per-file test edits for the 33 surviving files — re-derivations at the part-6
  bar (independent expectations, mechanism citations, no thinning; per-node dispositions where
  a node's subject genuinely ends with the v5 family, each recorded on its row).
- The runbook's step 2 gains its per-node test table referencing the patches; same for 3–4 if
  they need edits beyond deletions.
- **Proof:** execute each step IN ORDER in a scratch worktree (1 → 2 → 3 → 4, since later
  steps assume earlier post-states), applying deletions + patches, running the full battery at
  each step boundary. Record the measured post-state per step in the runbook. Green at every
  boundary = the runbook may say MECHANICAL. Anything that cannot go green without an ungiven
  decision moves to the owner-gated fifth entry with its measurement — the entry may grow,
  never silently.

## Constraints

- The L-033 dual and the other five owner-gated items stay out of the steps; if step 2's
  simulation needs a provisional trim around them, mark the trim in the runbook exactly as the
  prior session did.
- Patches must apply cleanly on the real tree at HEAD and carry no unrelated hunks; a checker
  test asserts `git apply --check` for every patch so drift fails the suite.
- Real tree: only the runbook, patches, plan, ledger-state notes, and the patch-check test
  change. Batteries per commit on the REAL tree remain the unchanged-numbers check
  (3854/47/53 etc.).
- Rule-10 stops as established. Honest remainder if budget ends — a partially proven runbook
  that says so beats a complete-looking one.

## Report back

Per-step simulated post-states (full battery numbers), patch inventory with node accounting,
the final owner-gated entry contents, runbook state (MECHANICAL or the honest remainder), OIDs.
`ARTIFACT:` the updated plan.
