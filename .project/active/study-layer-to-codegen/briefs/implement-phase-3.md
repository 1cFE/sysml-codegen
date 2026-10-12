# Brief: implement Phase 3 — study-layer-to-codegen

Sent by the orchestrator (2026-10-12) to `/_my_implement`. Implement **Phase 3** of `.project/active/study-layer-to-codegen/plan.md`: integrate judges any target. Only Phase 3. Later phases get their own sessions.

- **The contract** is `design.md` (`5ef62d6`) and `spec.md` (`4960d6b`). The plan's "Ground rules for every phase" apply.
- **Phase A is done** as agentic-mbse `0843fe2`. This worktree's `.venv` already imports `installer/v1` from it. Use `uv run --no-sync` everywhere.
- **Phases 1 and 2 are done** (through `863135c`). Read their Implementation Notes in the plan first, especially "For Phase 3".
- **Orchestrator decision on gate 7 and `/dev/urandom` [AGENT, 2026-10-12]:** new closed-list item **B13**, now in `spec.md` (`c34ae2d`). `read_coverage` classifies a read of `/dev/urandom` or `/dev/random`, exactly those two paths, as a runtime read, the same as reads under `sys.prefix`. Implement it in this phase, with a test that reproduces the station refusal before the change and passes after it. Then pursue `CANDIDATE` on the station as the plan says. Keep the edit to those two paths.
- **Closed list is now B1–B13.**
- **Quality bar.** This is sysml-codegen's supported study package, not a lift-and-shift:
  - Every former `__file__` question goes through `study/roots.py`.
  - Edits stay inside the closed list B1–B12 plus what mypy and SC5 need. Anything else you would like to change goes in Implementation Notes as a proposal, not into the code.
  - Typed and lint-clean, under this repo's strict mypy.
- **If the plan or design is wrong** against the real code, adapt only where the intent is unambiguous, and record the deviation in the plan's Implementation Notes. Otherwise stop and report.
- **Commit** each coherent step with explicit paths (`git commit -- <paths>`), after checking the index is otherwise empty. Each subject leads with what changed. End each message with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Do not push.
- **Before you finish,** tick Phase 3's checkboxes and add Implementation Notes: test counts against the baseline, deviations, and anything Phase 4 must know.

Do not start background tasks. Finish with a short report and `ARTIFACT: .project/active/study-layer-to-codegen/plan.md`.
