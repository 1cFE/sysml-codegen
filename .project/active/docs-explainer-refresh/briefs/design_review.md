# Brief: design_review — docs-explainer-refresh

Review `.project/active/docs-explainer-refresh/design.md` against the spec
(`spec.md`, revised 2026-07-13 post spec_review) and the evidence base
(`staleness-survey.md`, verified at HEAD twice).

## Context

- Four-repo docs truth-up + explainer-brief rewrite after the CONSTRAINT-EXEC epic. Intent:
  every touched teaching surface tells one story (current HEAD); `EXPLAINER_PROMPT.md`
  becomes a truthful, buildable v2 brief for another agent.
- Work rides the open PR branches (`constraint-exec-epic` in sysml-codegen/agentic-mbse/teax;
  fusion-tea local `main`) as appended commits. [OWNER-confirmed at Align.]
- Settled, do not relitigate: brief-only explainer deliverable ([OWNER]); fusion-tea
  walkthrough pointer-only ([OWNER]); alias default = drop (orchestration decision, recorded
  in spec SC-7); targeted sweep not a scrub.
- The design was asked to decide five calls (matrix family shape, contracts doc home,
  agentic-mbse doc depth, Gen-1 banner, retired-symbol row handling) — decisions with
  rejected alternatives are expected in the artifact. Challenge their reasoning if it's
  weak, but absence of an owner gate is not a defect: the owner delegated them.
- The orchestrator verified the design's two claimed test anchors exist:
  `tests/unit/test_contract_models.py`, `tests/conformance/test_seal_step9.py`.

## Review hardest

1. Auditability: can each spec success criterion be discharged by following this design, and
   would an auditor know where to look? Especially the new inherited-history criterion
   (INV-1/2/3) and the matrix-recount trap (INV-4).
2. The CON family rows: are they anchored to tests that actually exercise the claimed
   behavior (not placeholder rows that would land UNTESTED)?
3. The explainer-brief redesign: does it keep the brief BUILDABLE (concrete slot map, data
   sources, reuse guidance) rather than just truthful? The v2 HTML agent is the reader.
4. Cross-repo edits designed from survey cites under a sandbox boundary: is the "re-grep
   before editing" instruction concrete enough that the implementer can't silently edit the
   wrong lines?
5. Scope discipline: nothing in the design should quietly grow into a docs scrub or redo
   what Item 14 already flipped (survey §sysml-codegen lists it).

End with a verdict and, if not Approved, an ordered must-fix list.
