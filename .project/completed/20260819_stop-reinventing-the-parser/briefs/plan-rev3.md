# Brief — Plan Revision 3: consume the corrected design Revision 7

You are revising `.project/active/stop-reinventing-the-parser/plan.md` from Revision 2 to
Revision 3. This is a **targeted revision**: the phase structure (1-5), the Global Execution
Contract's worktree/checkout discipline, the owner-directed PDF exclusion, and everything not named
below stay as they are. Read first:

1. `.project/active/stop-reinventing-the-parser/design.md` — Revision 7 (targeted amendment of the
   approved Revision 6; review must-fix set applied and orchestrator-verified). Its
   `## Next-stage handoff` names exactly what Plan Revision 3 must carry.
2. `.project/active/stop-reinventing-the-parser/run-records/phase1-stop-report.md` — why Revision 2
   tripped: its lock-recompute clause executed a rule Revision 6 stated wrongly, and its Phase 1
   stencil targeted a shape that goes red for the wrong reason. Rulings 1-7 are owner-ratified.
3. `plan.md` Revision 2 — your base text.

Provenance: design rev 7 and the ratified rulings are binding. Operational details in this brief
marked [AGENT] are orchestrator choices; the design wins on any conflict, surfaced not silently
resolved.

## What Revision 3 must change

1. **Global Execution Contract — lock verification clause.** Replace "Their parent chain and every
   locked probe/fixture hash must recompute before Phase 1" with the design's three-leg rule
   (design.md `#### What the lock is verified against`): leg 1 fixture inputs against the tree the
   lock itself names (`probe_fixture_commit == 20f9e60a…`, read from the lock file — never
   hard-code `43edf9bd`); leg 2 current outputs through the committed transition-ledger validators;
   leg 3 the six locked verification/probe code rows pinned at current bytes, differences
   ledger-owned. Keep "a mismatch returns the item to design; never re-derive the lock." Carry the
   firing-form D10 rerun trigger.
2. **Phase 1 test stencil and red set.** Replace the single `cells#(2).mass` stencil with the two
   required kept cases from design.md `### The indexed red set`: Case 1 `Cell[1]` bare chain, index
   out of range → recorded red is a zero-diagnostic graph silently binding occurrence zero; Case 2
   `Cell[3]` bare chain → recorded red pins `SI_OCCURRENCE_AMBIGUOUS` and requires it to become
   `SI_INDEXED_SOURCE_UNSUPPORTED`. State each case's exact expected-red reason; a different
   failure is not the proof point. Operator-wrapped forms are positive regression coverage, not
   red-set members.
3. **Phase 1 changes/validation.** Add the committed historical-tree lock check as a Phase-1 kept
   test (design.md `#### The missing committed check`), with its five bullet obligations. Update the
   base-verification checklist item to run the three legs. The "first proof point" section must
   describe Case 1's zero-diagnostic collapse (and name Case 2's wrong-name refusal as the paired
   red), not the old ambiguous-shape stencil.
4. **Phase 4 reconciliation expectations.** Add the A5a/A5b ledger rows and the expected
   `SI_OCCURRENCE_AMBIGUOUS → SI_INDEXED_SOURCE_UNSUPPORTED` transition so the reconciliation gate
   expects it rather than flagging it.
5. **`deep_cross_scope_probe` obligations.** Carry the never-restore stop condition (a change
   returning it to a captured graph fails the item), the fixture-comment fix at
   `tests/fixtures/deep_cross_scope_probe/design.sysml:75`, and the `[DEEP-QUALIFIED-OUTPUT-WIRING]`
   backlog row into the phases that own them (comment fix and backlog row belong with Phase 4's
   documentation/filing work; the stop condition is global).
6. **Source-document header and status.** Reference design Revision 7 and the rev-7 review
   disposition; bump plan revision to 3 with a one-paragraph revision note naming the stop report
   as cause. Reset nothing in the Implementation Notes sections — they are still empty and stay so.
7. **Counts and states.** Anywhere the plan quotes batch counts or the `bd7bf245…` hash, label
   frozen (`P_seed`, 15/22) vs current (`C_base`, 14/23) per the design's two-state table.

## Constraints

- [AGENT] The run scaffolding stands: implementation worktrees at
  `/tmp/stop-parser-rev2/worktrees/{sysml-codegen,agentic-mbse}` on branches
  `stop-parser-impl-r2`/`stop-parser-evidence-r2` at the unchanged `C_base`/`A_base`. The plan's
  "exact starting trees" section is unchanged except the lock-verification language.
- Do not weaken any Phase 2-5 gate. Do not touch the owner-verbatim PDF exclusion.
- Edit plan.md in place in this checkout. Do not commit.

## Deliverable

Final message: prose summary of each change, any deviation surfaced, ending with
`ARTIFACT: .project/active/stop-reinventing-the-parser/plan.md`.
