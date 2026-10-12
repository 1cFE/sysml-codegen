# Brief: audit — study-layer-to-codegen (WRAP-SPLIT Item 3)

Sent by the orchestrator (2026-10-12) to `/_my_audit`, in a fresh session that authored none of the work. Certify the item against its spec, design and plan. Write the audit where `/_my_audit` puts it, at `.project/active/study-layer-to-codegen/audit.md`.

## What to audit

- **The contract.**
  - `spec.md`: SC1–SC12, the closed list B1–B13 with B13's receipt consequence, the decisions, the Non-Goals, and the amendments.
  - `design.md`, with its 2026-10-12 amendment.
  - `plan.md`, with Phases A and 1–6 and their Implementation Notes.
- **The sysml-codegen branch** `study-layer-to-codegen`, from base `aa35f06` to HEAD, in this worktree. `git log aa35f06..HEAD` and `git diff aa35f06..HEAD` are yours to read.
- **The agentic-mbse branch** (installer API, tracking, ledger). It is staged read-only at `.orchestrate-logs/src/audit/agentic-mbse-branch.{log,diff}`, from base `ac5fb1a`.
- **The fusion-tea branch** `study-layer-adoption` (the SC10 text homes, commit `699b0a74d`, base `c42ed1d8a`). It is staged at `.orchestrate-logs/src/audit/fusion-tea-branch.{log,diff}`.
- **Evidence** in `.project/active/study-layer-to-codegen/evidence/`:
  - the SC1 install transcript (`install-transcript.md`, 25 of 25);
  - SC4's dry run (`dry-run/run-20261012/RESULT.md` and its records);
  - SC12 parity (`parity/`, 28 of 28);
  - the read-through and the ledger rows (SC5, SC10).
- **SC9's rehearsal** is still running. The orchestrator will resume this session with its results. Until then, mark SC9 pending and audit everything else.

The staged fusion-tea and agentic-mbse sources are in `.orchestrate-logs/src/`, as before.

## What the orchestrator wants from the audit

- **Certify by checking, not by reading claims.**
  - Re-run the default suite: `uv run --no-sync --env-file /home/reid/1cfe/sysml-codegen/.env pytest tests/`.
  - Re-run `ruff check src/` and `mypy src/`.
  - Re-run the teax lane, using the command the plan names.
  - Spot-check at least three evidence claims by re-running them, for example the parity report from stored runs, the record checker on the dry-run record, and the wheel's asset list.
  - Use `uv run --no-sync` throughout. Plain `uv run` silently tests the wrong agentic-mbse.
- **Engineering quality.** Is `sysml_codegen.study` a clean, well-bounded package that sysml-codegen can own? Look at:
  - `roots.py`;
  - `declarations.py`;
  - `cli/install.py` and `cli/study.py`;
  - the edit map against the closed list. Is any edit outside B1–B13, with its consequences?
  - the mypy overrides on the ported modules: which strict checks are switched off, and whether any of them hides a real defect. Name each one.
- **The owner's bar** on the shipped text (`src/sysml_codegen/assets/`):
  - It reads as general rules.
  - Fusion vocabulary appears only in labelled examples.
  - No fusion-tea or sysml-codegen internals are cited as authority.
  - No machine paths or consumer requirement numbers.
  - The owner's shape holds: a lightweight skill, a runbook, a policy rulebook and tools; indicators never gate; collaborative intake; one skill for both roles.
- **No loss for fusion-tea (SC10).** Every moved read-through row has a ledger row and a home on the fusion-tea branch.
- **The dry run's three findings (F-DR1..3).** Agree or disagree with their disposition. F-DR1 is filed as a follow-up, not fixed.
- **Hazards the owner faces at adoption.** Say which runbook steps are risky and whether the runbook guards them.

Give a verdict (Certify, Certify with follow-ups, or Needs Work) with numbered findings, each graded by severity and each with evidence. Do not fix code. Do not commit. Do not start background tasks. Finish with `ARTIFACT: <path>`.
