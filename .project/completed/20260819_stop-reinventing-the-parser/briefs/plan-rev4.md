# Brief — plan Revision 4: consume design Revision 8, restructure the remaining run

Item: `.project/active/stop-reinventing-the-parser/`. Revise `plan.md` **Revision 3 →
Revision 4**. Phase 3 halted on a falsified design premise; the owner ruled; design Revision 8
encodes the rulings and its review is closed. Your revision consumes that amendment and
restructures Phases 3-5 to match reality. Phases 1-2 are complete and closed — their contract
text and completion records are **history: do not rewrite them** (a Revision 4 note may say what
superseded them, as the Revision 3 note did for Revision 2).

Read first: `design.md` Revision 8 — especially its revision-history entry, the "Review
incorporation" note, and the next-stage handoff block (it lists what this revision must carry
and the two consequences it must act on); `run-records/phase3-stop-report.md`;
`design-review.md`'s "Revision 8 targeted review" + orchestrator verification note;
`run-records/phase2-audit.md` (the m3 closure being re-based); plan.md itself.

Provenance: the owner's rulings are already encoded in design rev 8 with their grades — cite
design anchors rather than re-deriving. The owner's sequence directive for the run
**[OWNER, 2026-08-18]**: reopen Agentic tests-first and land the shared unit primitive with a
Phase 2 audit addendum; resume Phase 3 from `b4e97dd` — **no rollback**; finish the
responsibility migration; end with a dedicated adversarial Phase 3 audit. The owner's
conditional acceptance of the tests-after deviation **[OWNER, 2026-08-18]**: no history rewrite;
the missing constructor/inventory/deep-path/manifest kept tests must be added before Phase 3
closes; important boundaries mutation-tested; the auditor must try weak variants (skipped
inventory, indexed-to-exact conversion, shortened deep paths, adapter-free selector reads,
malformed unit arity, missing diagnostic provenance); the audit does not substitute for missing
kept tests. The owner's disposition ruling **[OWNER, 2026-08-18]**:
`tests/conformance/test_source_identity_extraction.py` may be removed only with a **14-row
disposition table** (replacement test ID or precise retirement reason per row, against the
responsibilities in `ledger-4a.md:628`), with replacements landing in the same commit that
deletes the file.

## What Revision 4 must contain

1. **A Revision 4 note** naming the cause (Phase 3 stop, rulings, design rev 8) and what
   changed, in the style of the Revision 3 note.
2. **A new phase — "Phase 2b: land the shared unit primitive" (or fold it cleanly as a
   pre-Phase-3 gate; your structural call, but it must be separately gated):** reopen the
   Agentic worktree (`stop-parser-evidence-r2` at `68bca37`) **tests first**; retire the two
   superseded shape assertions the design names; add `unit_annotation_value` per the design
   contract (wrong arity raises the named refusal; `None` strictly means not-an-annotation);
   make `inspect_reference_uses` call it; keep the never-emit rule; the owner's four coverage
   cases (`[m]`, compound forms `[kg/m^3]` and `[W/(m·K)]` elaborating, wrong-arity synthetic,
   value-operand references still visited). Re-apply the Phase-2 audited obligations to this
   landing (scoped strict zero, focused suites, fast-suite baseline, wheel check at the same
   `0.1.3` / `semantic-evidence/v2` contract — design rev 8 rules whether a version distinct
   from the audited `68bca37` bytes is required; follow it). Close with a **Phase 2 audit
   addendum** re-establishing m3 on non-emission. Codegen's pin then targets this landing.
3. **Phase 3 rewritten to resume from `b4e97dd`** (no rollback), with:
   - the falsified "removes the ~26 unowned reads" checklist item restated per design rev 8's
     Codegen-gate subsection: repository-wide discovery, collision-aware rows with the defined
     proof artifact, adapter-free evasion mutant failing the equality gate, genuine raw reads
     (e.g. `usage_extractor`) migrated or mechanically excluded against the 20-row measurement;
   - the Codegen value-site policy re-implemented over the shared primitive (delegating all
     structural interpretation), replacing the ratified-in-substance interim helper;
   - the missing kept tests (constructor/exhaustiveness, inventory missing/duplicate,
     per-consumer bypass, deep-path totality) as explicit checklist items with the
     mutation-testing obligation;
   - the 14-row disposition table item for `test_source_identity_extraction.py` (file currently
     blocks collection — Phase 3 cannot close while it stands unchanged);
   - the carried Phase-1 audit Minors 6, 7, 8 and Informational 12 (already in the Phase 3
     brief; keep them);
   - unchanged surviving obligations (occurrence.py byte-identity, dependency pins, scoped
     strict, deep_cross_scope never-restore, extraction-lane suite numbers).
4. **Phase 3's validation** updated to include the compound-unit elaboration proof (the models
   that refused at the stop — e.g. the `catf_mfe_*` fixtures — must elaborate again) and the
   owner's adversarial-audit weak-variant list recorded as the audit's obligations.
5. **Phases 4-5 touched only where rev 8 reaches:** A5b's dual starting states are already in
   the design; reconcile the plan's A5a/A5b text with it; everything else stays.
6. **Global Execution Contract:** add the Agentic reopening to the tree table/discipline (the
   read-only rule for the Agentic worktree is superseded by the gated Phase 2b landing; state
   it), and nothing else.

Keep every count state-labeled as Revision 3 does. Do not invent new gates the design does not
require. Implementation notes sections for completed phases stay as they are; add empty
completion sections for any new phase.

## Deliverable

`plan.md` updated in place to Revision 4 (do not commit; the orchestrator commits). Final
message: prose summary of the structural changes and any place you had to interpret a ruling,
ending with `ARTIFACT: .project/active/stop-reinventing-the-parser/plan.md`.
