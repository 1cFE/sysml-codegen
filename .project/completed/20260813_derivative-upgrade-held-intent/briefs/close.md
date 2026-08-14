# Orchestrator brief — close stage, CONSTRAINT-SEMANTICS Item 9

Close Item 9 (derivative upgrade under held intent), item home
`.project/active/derivative-upgrade-held-intent/`. Audit verdict: **Certify-with-residuals**
(none blocking; R1 cured in place at `d713f21` — stencil-count record error, named correction).
Owner authorized close at Align (2026-08-13); `pre_pr` and any push remain with the owner.

## Close actions

1. Archive the item folder to `.project/completed/20260813_derivative-upgrade-held-intent/`
   (git mv, epic conventions). Check first that no test or script reads the `active/` path —
   the F5 lesson; Item 9's own artifacts should be records only, but verify
   (`grep -rn "active/derivative-upgrade-held-intent" src/ tests/ scripts/`).
2. Epic bookkeeping (`.project/backlog/epic_constraint_semantics_contract.md`, Item 9 section +
   status lines + Next Action): tick criteria 1 and 2 with the audit evidence; SC-3 stays
   UNTICKED with a dated note — not-fired conditional by owner ruling, recorded two-sided
   (fixture `PROVENANCE.md` §3b + the `[INLINE-PREDICATE-MARKER-DROP]` BACKLOG line). Add a
   short close block: three executing gates (A2, A3, A9), identity restated 65 = 56 + 9 and
   machine-proved, blocked-by-defect retired on the live surface, archive frozen, licensed
   2070/34/0. Record the D3 `tf_coil.thickness` ratification, the A9 def-shape NOTE →
   `[CONSTRAINT-FORM-PER-DIMENSION-COST]`, the float-drift surfacing, and the orchestrator's
   Item 8 archive-path cure (`4155b4d`, F5 family) as a rider that belongs to Item 8's record,
   not Item 9's scope.
3. Update `.project/CURRENT_WORK.md`: Item 9 closed; **Item 7 is now unblocked and is the last
   item** before epic close/pre_pr (it documents the final state, including the §8
   unit-on-binding rewrite and the B1–B5 marker mechanism; the epic-level verification-matrix
   reconciliation rides it). Move the Item 9 entry to Recently Completed per house style.
4. `.project/completed/CHANGELOG.md`: one entry, house style.
5. Residual homes: R2 (substituted-and-disclosed freeze measure) and R3 (SC-3 epic checkbox
   open by ruling) need no future owner — record as disposed. R4/R5 (`_LAYERS` list, A1/A4
   `None` exemptions) are forward-looking observations — record them in the close block so the
   next fixture-touching item sees them; no backlog entry (they are fail-closed and inherited).
6. Nothing pushed, no `main`, TEAx untouched on `constraint-semantics-item3` @ `5b70ae9`.

## Concurrency

Another agent closed Items 6/8 earlier today; CURRENT_WORK.md/BACKLOG.md/CHANGELOG.md may have
fresh commits. Rebase-read before editing; commit only files this close touches.

Commit the close yourself (subject leading with the decision, epic convention:
`close(Item 9): archived to completed/20260813_derivative-upgrade-held-intent — ...`).
Reply with the commit SHA and ARTIFACT: the archived folder path.
