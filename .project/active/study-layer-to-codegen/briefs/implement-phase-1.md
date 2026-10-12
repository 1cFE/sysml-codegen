# Brief: implement Phase 1 — study-layer-to-codegen

Sent by the orchestrator (2026-10-12) to `/_my_implement`. Implement **Phase 1** of `.project/active/study-layer-to-codegen/plan.md`: the KB4 proof, then the package port and the root split. Only Phase 1. Later phases get their own sessions.

- **The contract** is `design.md` (`5ef62d6`) and `spec.md` (`4960d6b`). The plan's "Ground rules for every phase" apply.
- **Phase A is done** as agentic-mbse `0843fe2`. This worktree's `.venv` already imports `installer/v1` from it. Use `uv run --no-sync` everywhere.
- **The KB4 proof comes first.** If the neutral model does not run on stock teax, stop before committing any port work. Report what failed and what cut 2 would mean. The orchestrator decides.
- **Quality bar.** This is sysml-codegen's supported study package, not a lift-and-shift:
  - Every former `__file__` question goes through `study/roots.py`.
  - Edits stay inside the closed list B1–B12 plus what mypy and SC5 need. Anything else you would like to change goes in Implementation Notes as a proposal, not into the code.
  - Typed and lint-clean, under this repo's strict mypy.
- **If the plan or design is wrong** against the real code, adapt only where the intent is unambiguous, and record the deviation in the plan's Implementation Notes. Otherwise stop and report.
- **Commit** each coherent step with explicit paths (`git commit -- <paths>`), after checking the index is otherwise empty. Each subject leads with what changed. End each message with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Do not push.
- **Before you finish,** tick Phase 1's checkboxes and add Implementation Notes: the KB4 result, test counts against the baseline, deviations, and anything Phase 2 must know.

Do not start background tasks. Finish with a short report and `ARTIFACT: .project/active/study-layer-to-codegen/plan.md`.
