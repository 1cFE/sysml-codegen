# Brief: implement — docs-explainer-refresh

Execute `.project/active/docs-explainer-refresh/plan.md`, phases 1→7 in order. Read first:
`plan.md`, then `design.md` and `spec.md` (same folder) for the decisions and success
criteria the phases discharge. The staleness survey (`staleness-survey.md`) is the verified
evidence base — trust it, re-grep each cite immediately before editing (line numbers can
drift; on a miss, STOP that edit and record the discrepancy in the plan's notes rather than
guessing).

Work synchronously; never pause for, schedule, or spawn background agents. If a phase's
verification command is blocked by permissions, record it as "gate deferred to orchestrator"
in the plan notes and continue — do not stall.

## Discipline

- Check off plan checkboxes as you complete them; add implementation notes (deviations,
  discoveries) per phase.
- One commit per phase, subject leading with the decision, pathspec-limited
  (`git add <paths> && git commit -- <paths>`); use `git -C <repo>` for the cross-repo
  phases (agentic-mbse, teax at `constraint-exec-epic`; fusion-tea at `main`). NEVER push,
  NEVER rebase, NEVER touch uv.lock, NEVER commit files you did not edit (other repos have
  pre-existing untracked files — leave them).
- agentic-mbse: never run `pytest tests/ -m ""`; no full suites are needed for this item.
- Do not redo what CONSTRAINT-EXEC Item 14 already flipped (survey §sysml-codegen lists it).

## Quality bar (why this item exists)

A reader anywhere in the four repos gets ONE story — current HEAD. Write docs in the voice
and structure of their sibling docs (match the existing reference-doc conventions, heading
style, REQ-row format). The explainer brief (Phase 3) is the biggest deliverable: it must be
BUILDABLE by the v2 HTML agent from the brief alone (design INV-6 — responsibility-map rows,
reading-list data sources, reuse-guidance delta, corrected counts), truthful to HEAD, and
must keep the inherited history straight (design INV-1/2/3: flag = landed history; the
manifest collector survives; CE-F1/F2 are open follow-ons, not landed behavior).

End with: phases completed, commits made (hash + repo each), any deferred gates or recorded
discrepancies. ARTIFACT: .project/active/docs-explainer-refresh/plan.md
