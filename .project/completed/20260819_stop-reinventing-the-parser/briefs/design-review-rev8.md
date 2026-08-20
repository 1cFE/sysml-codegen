# Brief — targeted design review: Revision 8 amendment

Review `design.md` **Revision 8** of `.project/active/stop-reinventing-the-parser/` — a targeted
amendment of approved Revision 7, written after Phase 3 halted on a falsified premise. This is a
**targeted** review: judge the amendment and its integration, not the whole design (Revision 6
was approved in full; Revision 7's amendment was reviewed and closed).

Read: `design.md` (rev 8, focus on its revision-history entry and the four changed areas),
`run-records/phase3-stop-report.md` (the cause), the owner rulings in
`briefs/design-rev8-amendment.md` (the input contract — rulings are [OWNER]/[OWNER-VERBATIM]),
`run-records/phase2-audit.md` m2/m3 (context), plan.md Phase 1 completion deviations item 3.

You may read the implementation worktrees read-only for factual verification
(`/tmp/stop-parser-rev2/worktrees/{sysml-codegen,agentic-mbse}`); modify nothing anywhere.

## Review obligations

1. **Fidelity to the rulings.** Each of the four owner rulings must land with its meaning and
   provenance intact — verbatim blocks quoted, no silent weakening or strengthening. Flag any
   place the amendment adds requirements the owner did not state or drops ones they did.
   Ruling 1's distinction ("does not validate unit grammar at all" ≠ "any shape passes
   validation") must survive; check the test-coverage list matches the owner's four cases.
2. **Internal consistency.** The new opaque-unit contract, the shared primitive, and the Codegen
   value-site policy must not contradict each other or surviving rev-7 text (e.g. does any
   remaining sentence still imply unit-shape validation or an exact-referent requirement on the
   unit operand? does `annotated_ast_value`'s deletion clause square with the primitive
   delegation?).
3. **The manifest rules.** The Codegen-gate subsection must be implementable as written: is
   "field owner or receiver contract" defined well enough that an implementer and an auditor
   would agree whether a row qualifies? Is the adapter-free evasion mutant specified so it must
   be discovered by the repository-wide scan? Does the text keep the Agentic gate's audited
   scoping untouched?
4. **The behavior-matrix row.** Check the lenient row against the measured record (plan.md
   Phase 1 completion, deviations item 3, and the Phase-1 audit Minor 9): graph returned carrying
   `SI_OCCURRENCE_AMBIGUOUS` + `SI_OCCURRENCE_MISSING`, three `cells[i]__mass` attributes,
   `picked` unresolved. The A5b ledger-row text must expect both starting states so Phase 4
   reconciliation does not flag the transition as unlisted drift.
5. **Amendment discipline.** Only the rulings' reach changed; D1-D9 unrenumbered; cited anchors
   stable (spot-check the anchors plan.md rev 3 links); cause and changed-section list at top.
6. **Downstream coherence.** The next-stage handoff block must give the plan revision what it
   needs — especially the phase-boundary consequence (ruling 2 lands in Agentic, which Phase 3
   treated as read-only, under the same `0.1.3` / `semantic-evidence/v2` contract). Say if
   anything the plan revision will need is missing.

## Deliverable

Append your review to `design-review.md` as a new dated "Revision 8 targeted review" section (do
not commit): verdict `Approve` / `Revise` with must-fix and should-fix lists, each finding with
exact location. Final message: prose summary ending with
`ARTIFACT: .project/active/stop-reinventing-the-parser/design-review.md`.
