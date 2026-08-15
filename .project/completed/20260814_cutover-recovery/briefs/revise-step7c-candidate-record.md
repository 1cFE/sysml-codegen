# Stage brief — REVISE step 7c: regenerate ONE internally consistent candidate record

**You are executing the tail of owner step 7**: regenerate `evidence/candidate.{md,json}`
from scratch at the final paired OIDs, fixing the record-integrity discrepancies the owner
named. Plan: `/home/reid/1cfe/sysml-codegen-item7-rebuild/.project/active/cutover-recovery/plan.md`.
Read first: `owner-disposition-20260811.md` (step 7 + "Also in scope"), the current
`evidence/candidate.md` (the stale record you replace), `evidence/phase5-runs/build_candidate.py`
and the `revise-runs/` artifacts + `comparison.md`, the step-7 stage note (7a/7b/dispositions),
and `evidence/audit-7-retired.md`'s certification clause.

Work synchronously. Never pause for background agents; finish or stop with questions.

## The content OIDs

- codegen `item7-rebuild` **`6c35aa0`** (product + record content; the 7a runs measured
  `c0ceb24` and the only product change since is the audited-and-dispositioned F3 CLI
  handler + its two pinned nodes — state exactly that, with the +2 suite delta:
  1707 / 34 / 65 at `6c35aa0` vs 1705 / 34 / 65 in the three runs)
- agentic-mbse `item7-rebuild` **`3fbda2f`**
- TEAx pinned **`fa0e06a9`**
The record commit lands ON TOP of these (a commit cannot contain its own OID); the record
names the content OIDs.

## The discrepancies the owner named (fix ALL, from the handoff's "Record integrity")

1. `candidate.md`'s "audit has not run" line and every `c4e9b76` reference — the record must
   describe the retired tree, the 7a three-run table, the audit-7 verdict + probe addendum,
   and the F1–F3 dispositions.
2. The commit count: recount mechanically at the final OIDs (`git rev-list --count` over the
   relevant range, stated with its range definition; the old record's 108-vs-112 ambiguity
   must not recur — one number, one definition).
3. The owner-gate OID in the plan's owner gate section: currently names `800ec84` as the
   candidate; amend to record BOTH gates — the 2026-08-11 REVISE disposition at `800ec84`,
   and the post-revise candidate at the new content OIDs awaiting the owner's final
   disposition.
4. The plan's progress checkboxes (~line 156 area and the Phase 4/5 sections): Phase 4's
   postponed-retirement boxes and the phase table must reflect the executed retirement
   (cite the step-6 commits); Phase 5/audit boxes reflect audit-7.
5. Any remaining internal inconsistency you find while regenerating — the standard is ONE
   internally consistent record; verify every OID, count, and gate value in the finished
   record against the tree or a committed log, and say in the record how each was derived.

## Mechanics

- Extend/adapt `build_candidate.py` (or a sibling builder under `evidence/phase5-runs/`) so
  the numbers come from the committed `revise-runs/` logs and the tree — no hand-typed
  numbers. Where a value has no log (commit counts, OIDs), derive it with a git command
  embedded in the builder.
- The record states plainly: what the candidate is (the retired tree), the gate results
  (33/33 identical), the audit verdict and its clause, the parked owner questions (R8,
  ruff-14, audit-F4, and the question-6 list in the disposition record), and what remains
  for the owner (final disposition; R8 resolution or shipping-gate before close).
- Update `.project/CURRENT_WORK.md`: the revise path is executed through step 7; owner
  disposition on the new candidate is the open gate.
- Two commits max: the record (+ builder), then any OID-record commit if needed.

## Battery

The record work changes no product or test file: `git diff --check`, distinctness if docs
touched, and re-assert `check_ledger_4a.py paths` still 304/0. If you find yourself editing
a product or test file, STOP — that is not this stage.

## Report back

The regenerated record's headline numbers; each of the five discrepancy fixes (before →
after); the commit OIDs; anything found inconsistent and how it was resolved.
`ARTIFACT:` `evidence/candidate.md`.
