# Brief: implement Phase 5 — study-layer-to-codegen

Sent by the orchestrator (2026-10-12) to `/_my_implement`. Implement **Phase 5** of `.project/active/study-layer-to-codegen/plan.md`: the shipped text, the read-through, and the fusion-tea text drafts. Only Phase 5. Read Phases 1–3's Implementation Notes first.

## You are running in parallel with Phase 4

- **Your worktree** is `/home/reid/1cfe/sysml-codegen-study-layer-text`, branch `study-layer-text`. It was cut from `study-layer-to-codegen` at `24cce2c`, after Phase 3 and before Phase 4.
- **Phase 4** (SC12 parity and the fusion-tea code drafts) runs at the same time in the main worktree. The orchestrator merges your branch back afterwards.
- **Your environment** is this worktree's own `.venv`, with agentic-mbse installed editable from `/home/reid/1cfe/agentic-mbse-study-layer`. Use `uv run --no-sync` everywhere. The staged sources are in `.orchestrate-logs/src/` as before.
- **To keep the merge clean:**
  - Edit only Phase 5's section of `plan.md`, plus your own Implementation Notes.
  - Do not touch the parity script, Phase 4's evidence paths, or `CURRENT_WORK.md`. The orchestrator updates `CURRENT_WORK.md`.
- **The runbook draft's dependency on Phase 4.** It cites Phase 4's step-5 drafts (wrappers, `routes.sed`, test patches). Cite them by the paths the plan names. Write the runbook draft last. Add one line to your notes saying the citations were written against the plan, not against the files.

## Decisions carried in [AGENT, orchestrator, 2026-10-12]

- **The closed list is B1–B13**, from `spec.md` at its latest commit. Read B13 and its receipt consequence.
- **The ported docstrings' fusion-tea design labels** ("Invariant 6", "D5", "M3", "design S1" and the like, listed in Phase 1's notes with file and line) are in scope for your read-through. For each one, either state the meaning inline or drop the label. Record a verdict per label. These are comment and docstring edits that SC5 requires, which the closed list allows.
- **The bar** for the text is the owner's:
  - It reads as a general rule or practice.
  - Fusion vocabulary is fine in labelled examples.
  - What goes: pointers into fusion-tea or sysml-codegen internals as authority, machine paths, consumer requirement numbers, and single-project instructions.
  - Every removed line gets a fusion-tea home and a ledger row. That is the owner's no-loss rule.
- **Keep the owner's shape.** A lightweight skill plus a runbook plus a policy rulebook plus tools. Indicators inform and never gate. Intake is collaborative. One skill serves both the executing and the administrator role. Don't let the port bloat the skill.

## As before

- **The contract** is `design.md` (`5ef62d6`) and `spec.md`.
- **Commit** each coherent step with explicit paths (`git commit -- <paths>`), after checking the index is otherwise empty. Each subject leads with what changed. End each message with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`. Do not push.
- **Validation:** the full suite in this worktree, plus ruff and mypy, as the plan's ground rules say.
- **Before you finish,** tick Phase 5's checkboxes and add Implementation Notes: test counts, the read-through totals, the ledger row count, and anything Phase 6 must know.

Do not start background tasks. Finish with a short report and `ARTIFACT: .project/active/study-layer-to-codegen/plan.md`.
