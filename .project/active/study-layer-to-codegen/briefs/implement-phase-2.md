# Brief: implement Phase 2 — study-layer-to-codegen

Sent by the orchestrator (2026-10-12) to `/_my_implement`. Implement **Phase 2** of `.project/active/study-layer-to-codegen/plan.md`: the neutral fixture, and three tools that complete and fail closed. Only Phase 2. Later phases get their own sessions.

- **The contract** is `design.md` (`5ef62d6`) and `spec.md` (`4960d6b`). The plan's "Ground rules for every phase" apply.
- **Phase A is done** as agentic-mbse `0843fe2`. This worktree's `.venv` already imports `installer/v1` from it. Use `uv run --no-sync` everywhere.
- **Phase 1 is done** (`03b61f8`..`f041d0b`). KB4 holds. Read its Implementation Notes in the plan first.
- **Orchestrator decisions on Phase 1's proposals [AGENT, 2026-10-12]:**
  - **Git's own message.** The "in no git work tree" refusal carries git's own message when `rev-parse` fails for a reason other than "not a git repository", for example dubious ownership. Do it in this phase. It is a B1 refinement, so record it in the notes.
  - **Ported docstrings.** Their fusion-tea design labels ("Invariant 6", "D5", "M3", "design S1") are left for Phase 5's read-through. Do not touch them here.
- **Quality bar.** This is sysml-codegen's supported study package, not a lift-and-shift:
  - Every former `__file__` question goes through `study/roots.py`.
  - Edits stay inside the closed list B1–B12 plus what mypy and SC5 need. Anything else you would like to change goes in Implementation Notes as a proposal, not into the code.
  - Typed and lint-clean, under this repo's strict mypy.
- **If the plan or design is wrong** against the real code, adapt only where the intent is unambiguous, and record the deviation in the plan's Implementation Notes. Otherwise stop and report.
- **Commit** each coherent step with explicit paths (`git commit -- <paths>`), after checking the index is otherwise empty. Each subject leads with what changed. End each message with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Do not push.
- **Before you finish,** tick Phase 2's checkboxes and add Implementation Notes: test counts against the baseline, deviations, and anything Phase 3 must know.

Do not start background tasks. Finish with a short report and `ARTIFACT: .project/active/study-layer-to-codegen/plan.md`.
