# Stage brief — narrow-correction step 1: record the ratified dispositions

You are executing step 1 of the 2026-08-12 narrow correction proposal for Item 7.
The proposal is agent-authored and the owner forwarded it with the instruction to execute.
Every decision from that proposal must therefore be recorded as:

`[AGENT] (ratified for execution by owner, 2026-08-12)`

Never upgrade it to `[OWNER]`. This is an amendment pass: replace stale pending or blocked
statements rather than appending a contradictory status.

Work synchronously. Never pause for background agents. Finish this bounded record-only stage or
stop with a concrete premise conflict.

## Authority and required reading

- `/tmp/handoff-20260812-074345.md`, especially "Focus" and completion-sequence step 1.
- `.project/active/cutover-recovery/owner-disposition-20260811.md`.
- `.project/active/cutover-recovery/plan.md`, especially Progress, Owner gate, and REVISE step 7.
- `.project/CURRENT_WORK.md`, whose headline still says the owner disposition is the open gate.
- The repository `AGENTS.md` instructions supplied by the caller, especially provenance,
  correction, and surfacing.

## Objective

Amend the persistent execution authority so a fresh session can execute correction steps 2–10
without relying on the handoff or chat. Record the proposal's dispositions question by question,
with their correct agent-grade provenance. Replace the old "awaiting owner" / "blocked" state.

## Required dispositions

Record every item below in `owner-disposition-20260811.md` and carry the executable sequence into
the recovery plan. Preserve the substance and conditions exactly.

1. R8: **fix first**. Preserve qualified identity through rendering. Fall back to a shipping gate
   only if measurement shows a substantially larger naming-contract change. Item 10 is not an
   Item 7 dependency when R8 is fixed here; it becomes an explicit dependency only under that
   fallback.
2. Ruff: amend spec requirement R12 to a zero-new baseline. Recorded canonical baselines are
   sysml-codegen `src` **14** and agentic-mbse `src` **1**. No new findings; changed files clean
   unless a recorded pre-existing finding is unchanged; totals no worse.
3. Final audit: a fresh, narrow audit covering compiler convergence and symbol removal,
   replacement coverage for deleted tests, R8, portable provenance, final gate semantics, and
   evidence consistency. It is not a re-review of all 195 deletions.
4. audit-F4: make provenance referents portable and amend invariant 35 to semantic equality plus
   generated-byte equality after defined normalization of permitted provenance metadata.
5. REQ-CL-03: amend the requirement only after one public-behavior check proves that a model with
   constraint usages but zero eligible assertions still emits the `not_assessed` report and that
   no instance-reaching constraint usage is silently dropped. A failed check is a product defect
   to surface, not authority to amend.
6. The two non-shipping extraction modules: nonblocking cleanup. Delete them or fold them into test
   helpers; they are not a certification dependency.
7. Nine UNTESTED matrix rows: add coverage for REQ-GEN-03 and REQ-OSR-02/03/05; for smart-regen
   rows, add vertical behavioral tests if they remain product behavior, otherwise retire or amend
   the requirements; retain REQ-GA-05 only if its field set is an intentional public or serialized
   contract.
8. Three PARTIAL rows: add focused assertions for REQ-CL-04 total swept-usage mapping,
   REQ-EPC-01 exactly-one classification, and REQ-GA-03 rejection of an unresolved producer
   channel.
9. Missing elaborator REQ families: backlog, not an Item 7 certification dependency.
10. D3 and R2 amendments: ratified.

Also record the correction proposal's verdict: the recovered implementation stays in place; no
rollback and no second rebuild. Item 7 remains open because compiler convergence was falsely
recorded as executed, replacement proof is incomplete, and record-integrity corrections remain.

## Plan amendment

Add one persistent narrow-correction section to `plan.md` with checkboxes for the handoff's ten-step
completion sequence:

1. dispositions;
2. real L-033/L-034 compiler convergence plus checker hardening;
3. R8 fix-first;
4. replacement/matrix tests plus the `gain = 100` three-route proof;
5. portable provenance and invariant 35;
6. ruff R12 amendment;
7. three complete final batteries at the final paired OIDs;
8. candidate-record regeneration;
9. fresh narrow audit;
10. return to the owner for final acceptance.

Mark only step 1 complete in this stage. State that final acceptance remains owner-grade and that
the proposal authorizes no push, tag, promotion, close, or archive.

Amend the Phase 5 / Gate 2 wording so it no longer claims the regenerated `b987d9a` record is
waiting on unanswered questions. It is a superseded checkpoint under active correction. Preserve
Gate 1 as settled history. Update `.project/CURRENT_WORK.md` to make this correction path the active
work and name compiler convergence as the next blocker.

## Declared path set

This stage may change only:

- `.project/active/cutover-recovery/owner-disposition-20260811.md`
- `.project/active/cutover-recovery/plan.md`
- `.project/CURRENT_WORK.md`

The already-committed brief is not part of the stage diff. If any product, test, evidence,
candidate, matrix, spec, design, or companion-repository path changes, stop before commit.

## Validation and commit

- Re-read all amended status sentences and confirm there is no stale `R8 — BLOCKED`, `owner input
  pending`, or equivalent claim that the correction proposal resolved.
- Verify all ten dispositions appear and carry the exact agent-ratified provenance.
- Verify the plan has one executable correction sequence and only step 1 is checked.
- `git diff --check`.
- Confirm the changed path set is exactly the three declared files.
- Commit the record amendments as one focused commit. Do not amend or squash earlier history.

Report the commit OID, changed paths, and any premise conflict.

`ARTIFACT:` `.project/active/cutover-recovery/owner-disposition-20260811.md`
