# Brief: spec_review — docs-explainer-refresh

Review the spec at `.project/active/docs-explainer-refresh/spec.md`.

## Context you need

- This is a post-CONSTRAINT-EXEC docs + explainer-brief refresh spanning FOUR repos:
  sysml-codegen (home, this repo), agentic-mbse (`/home/reid/1cfe/agentic-mbse`), teax
  (`/home/reid/1cfe/teax`), fusion-tea (`/home/reid/1cfe/fusion-tea`). All but fusion-tea sit
  on branch `constraint-exec-epic` with open PRs (sysml-codegen #9, agentic-mbse #11, teax #3);
  the work lands as appended commits on those branches. [OWNER 2026-07-13: confirmed at Align.]
- Primary evidence is the spec-time staleness survey alongside the spec
  (`staleness-survey.md`). Its instruction: trust-but-spot-check, do not re-survey.
- Owner-graded decisions already settled ([OWNER] 2026-07-13, do not relitigate):
  the explainer deliverable is the refreshed `EXPLAINER_PROMPT.md` brief only — the v2 HTML
  build is a separate follow-on item another agent picks up; fusion-tea's
  `pipeline-walkthrough.html` gets a pointer/retirement note only.
- No reserved gates: the owner delegated the spec's Open Questions to the design stage
  (matrix family shape, contracts doc numbering, agentic-mbse doc depth, Gen-1 HTML banner).
  Do not fail the spec for leaving those open — they are deliberately deferred to design.
- [INHERITED] cautions the spec carries (check they are stated clearly enough for an
  implementer to not get them wrong): the `lower_constraints_enabled` flag story is history
  not current behavior; `collect_constraint_manifest` survives deliberately; CE-F1/CE-F2 are
  open follow-ons — docs must describe current embedded-catalog / single-channel-bridge
  reality.

## What to review hardest

- Is every success criterion checkable by an auditor against the survey + HEAD?
- Does the scope boundary (targeted survey-driven sweep, NOT a full docs scrub) hold up
  everywhere, or do any criteria quietly imply a scrub?
- Cross-repo coherence: are the per-repo deliverables individually well-defined and is
  nothing falling between repos?
- The "no claim contradicted by HEAD" bar for EXPLAINER_PROMPT.md: is it operationalized
  enough to audit?

End with a verdict and, if not Approved, an ordered must-fix list.
