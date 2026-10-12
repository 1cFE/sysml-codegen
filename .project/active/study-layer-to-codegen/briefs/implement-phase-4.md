# Brief: implement Phase 4 — study-layer-to-codegen

Sent by the orchestrator (2026-10-12) to `/_my_implement`. Implement **Phase 4** of `.project/active/study-layer-to-codegen/plan.md`: SC12 parity and the fusion-tea code drafts. Only Phase 4. Read Phases 1–3's Implementation Notes first, especially Phase 3's "decision needed" note on receipts.

## Decisions [AGENT, orchestrator, 2026-10-12]

- **The parity environment uses `/usr/bin/python3.12`** (Q2, already in the plan).
- **Receipt comparison rule** (spec, B13 consequence, now committed):
  - Parity excludes, from read-coverage receipt comparison, the original-only `runtime-observed` `.pyc` reads of standard-library modules that the moved observer preloads. Those are the modules imported because of `roots` (with `subprocess`) and `zoneinfo`.
  - Exclude exactly that set and nothing else. Measure it in the parity environment as the `sys.modules` difference, the way Phase 3 did. Record the measured list in evidence. Assert that every excluded module is in the transitive import closure of `sysml_codegen.study.roots` or `zoneinfo`.
  - Any other receipt difference is `DIFFERENT`.
- **Normalisation is by declared token pattern** (design Appendix G, as revised for review S3): mask the noisy parts, never whole fields. A changed blocker message must show as a difference.
- **An unlisted difference stops the phase.** Report it rather than masking it or adding a rule. The orchestrator decides whether it is a closed-list item or a defect.

## As before

- **The contract** is `design.md` (`5ef62d6`) and `spec.md` (latest commit). The closed list is B1–B13. Use `uv run --no-sync` in this worktree's venv.
- **The fusion-tea code drafts** (wrappers, `routes.sed`, test patches) go in this item folder as the plan says. The orchestrator applies them on a fusion-tea copy. Smoke-test them in the parity layout as the plan describes.
- **Quality bar:** the parity script is evidence the owner and the audit will read. Keep it small, deterministic and explicit about every rule it applies.
- **Commit** each coherent step with explicit paths (`git commit -- <paths>`), after checking the index is otherwise empty. Each subject leads with what changed. End each message with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Do not push.
- **Before you finish,** tick Phase 4's checkboxes and add Implementation Notes: the parity result per case, the measured exclusion list, and anything Phase 5 must know.

Do not start background tasks. Finish with a short report and `ARTIFACT: .project/active/study-layer-to-codegen/plan.md`.
