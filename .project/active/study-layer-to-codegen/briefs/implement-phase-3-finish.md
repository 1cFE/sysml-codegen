# Brief: implement Phase 3 (finish) — study-layer-to-codegen

Sent by the orchestrator (2026-10-12) to `/_my_implement`. Finish **Phase 3** of `.project/active/study-layer-to-codegen/plan.md`. The previous session paused at gate 7 (`09e9625`); read its notes in the plan first. Only Phase 3; Phase 4 gets its own session.

## Decisions on the pause [AGENT, orchestrator, 2026-10-12]

- **Q1: option (a), worded on `zoneinfo.TZPATH`.**
  - B13 is amended in `spec.md` (`4ca8cb3`) to cover "interpreter platform data": `/dev/urandom` and `/dev/random`, plus files under the interpreter's own `zoneinfo.TZPATH`.
  - Implement it in `read_coverage`. Read `zoneinfo.TZPATH` at observer construction; do not hard-code the paths.
  - Add a test that reproduces the zone-read refusal before the change and passes after it.
  - Then finish the `CANDIDATE` test and the gate-8 refusal test the plan names.
- **Q2: the parity environment uses `/usr/bin/python3.12`,** fusion-tea's own interpreter, so neither allowance fires on either side. Write that into Phase 4's steps in the plan as a recorded change. Phase 4 implements it.

## As before

- **The contract** is `design.md` (`5ef62d6`) and `spec.md` (now `4ca8cb3`). The closed list is B1–B13. Use `uv run --no-sync` everywhere.
- **Quality bar:** edits stay inside the closed list plus what mypy and SC5 need. Typed and lint-clean.
- **Commit** each coherent step with explicit paths (`git commit -- <paths>`), after checking the index is otherwise empty. Each subject leads with what changed. End each message with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Do not push.
- **Before you finish,** tick Phase 3's remaining checkboxes and add Implementation Notes: test counts against the baseline, and anything Phase 4 must know.

Do not start background tasks. Finish with a short report and `ARTIFACT: .project/active/study-layer-to-codegen/plan.md`.
