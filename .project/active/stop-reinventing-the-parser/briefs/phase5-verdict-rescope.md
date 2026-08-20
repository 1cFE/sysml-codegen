# Brief — verdict re-scope pass: sort the rev-3 findings against the owner's ruled boundary

You are the independent auditor issuing the **re-scoped verdict** for this item. Do not re-run
the chain verification or the attack batteries — rev 3 (`audit.md`, rev-3 section) already did,
and its measurements stand. Your single job: apply the owner's scope ruling to the rev-3
findings, honestly, and issue the verdict that follows.

Read: `audit.md` rev-3 section (the four blocking findings and their reproductions); plan.md's
"Owner scope ruling after the rev-3 audit (2026-08-19)" (the binding boundary);
`.project/backlog/BACKLOG.md` `[DIAGNOSTIC-PROVENANCE-BY-CONSTRUCTION]` (where out-of-scope
findings transfer); design.md rev 8 D8 (code ownership — what counts as model-facing).

**The ruled boundary [OWNER, 2026-08-19]:** in scope — authored-model-caused refusals on the
natural routes must refuse by name, pre-mutation, with true provenance. Out of scope
(transferred) — the quality of internal-defect reporting (`SI_INTERNAL_DEFECT` class) and the
totality-guard mechanism.

## Obligations

1. **Sort each of the four rev-3 findings** by what actually causes the failure the finding
   describes, measured, not by which code it currently carries:
   - *Collision provenance discarded before both CLI outputs* — is a rendering collision a
     model-caused refusal? If a model author's naming causes it and they get no location, it is
     in scope and blocks.
   - *`generate_registry` fabricating `unknown:0`* — same question: on what inputs does it
     fire, model-caused or internal?
   - *Incorrect attribution with overlapping model roots* — whose failure gets misattributed:
     a model-caused diagnostic (in scope) or an internal wrap (transferred)?
   - *Totality guard limited to three hard-coded files* — the guard mechanism itself; ruled
     out of scope unless you find it currently masks an in-scope defect.
   Where a finding straddles (one shape in scope, another out), split it and say so.
2. **For any finding you rule in-scope:** it blocks; state exactly what must change, and note
   whether it is production (invalidates the r3 chain again) or test/record only.
3. **For findings you rule transferred:** verify the backlog row's seed list names them
   faithfully — no finding may vanish in the transfer.
4. **Issue the verdict** against the ruled scope: Pass / Pass with findings / Needs Work, with
   the sorting table as its core. If Pass-grade: state plainly what the certification covers
   and what it explicitly does not (the transferred class), so `close` and the merge plan
   inherit an honest boundary.

Same rules as always: worktrees read-only (verify Codegen still at `875ba01`, Agentic at
`4433888`), your own probes only if a sorting question genuinely needs a measurement, license
via the `.env` source line, no PDF/paid suites, modify nothing, commit nothing.

## Deliverable

Append a dated "Re-scoped verdict" section to `audit.md` (do not commit): the four-row sorting
table with measured justification per row, transferred-findings check, and the verdict with its
explicit coverage statement. Final message: prose summary ending with
`ARTIFACT: .project/active/stop-reinventing-the-parser/audit.md`.
