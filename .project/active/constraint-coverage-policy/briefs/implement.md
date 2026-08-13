# Stage brief: implement — CONSTRAINT-SEMANTICS Item 3 (Coverage Report and TEAx Policy)

Repos: codegen `/home/reid/1cfe/sysml-codegen-item7-rebuild` (branch `item7-rebuild`); TEAx
`/home/reid/1cfe/teax` — **create a branch off `fa0e06a` before touching anything; never commit
to TEAx main; never push** (remote is SSH, no key — pushes would fail anyway). Companion
(`agentic-mbse-item7-rebuild`) is expected untouched; verify at the end, don't assume.

**Execute the plan:** `.project/active/constraint-coverage-policy/plan.md` — phase by phase,
checking off items and writing per-phase completion notes. Design rev 2 (`design.md`) is the
architecture authority; spec carries success criteria. Deviations recorded with reasons;
premise contradictions surfaced, not absorbed.

## Non-negotiables

- **Phase gates are real.** The red window opens at Phase 3 and closes at Phase 6, gated by the
  enumerated failing set that MAY NOT GROW — track it exactly as the plan states.
- **Hand-written expectations before confirmation tests** (owner-directed): the
  `expected-coverage.md` ledger and the four `all_satisfied` site updates (incl. the
  hand-derived fusion whole-dump coverage block from Phase 0) land before the tests that
  confirm them. Accounts are derived from each fixture's SysML source, never transcribed from a
  catalog dump (design DR-6).
- **PD5 ruling (orchestrator, recorded in the plan commit): replace-and-regenerate stands.**
  Phase 6 probes ONE TEAx fixture package first. If the probe shows regeneration infeasible —
  especially `f1_arithmetic`'s stale-SHA script — STOP at that phase boundary, record the
  evidence in the plan notes, and end your turn with the situation stated; do not quietly
  extend the accepted version sets, and do not sink hours into forcing one package.
- **Fail-closed everywhere the design says:** both policy dispatch tables, unknown tokens both
  vocabularies, `expects_report` single-authority (both former derivations), D9's
  eligible+inapplicable refusal.
- **One authority:** coverage derived from the sealed catalog once at generation; no per-usage
  recomputation; no second inventory.
- **Codegen gates:** `/home/reid/1cfe/item7-rebuild-venv/bin/python -m pytest` (NEVER `uv
  run`). License: `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a`; licensed proof =
  zero `no live syside license` skip lines. TEAx suite from `/home/reid/1cfe/teax`.
- **Zero-new ruff/mypy in both repos**; fixtures/baselines format-exempt; frozen twins
  untouched; Item 2's usage-tier schema gains no field.

## Commit discipline

Commit per phase (or tighter) in the repo the phase touches, subject leading with the phase and
decision. TEAx commits go on its item branch only.

## Deliverable

`.project/active/constraint-coverage-policy/verification.md` — exact counts: codegen full
licensed suite (zero-skip), TEAx full suite (on the branch, with the five-package outcome
explicit), focused modules, cross-repo compatibility tests, ruff/mypy both repos, generated-
artifact review, `git diff --check` all repos, companion-untouched check, the six-state matrix
evidence, and anything left open honestly.

If you run out of time or context, stop at a phase boundary with checkboxes and notes current.
Finish with `ARTIFACT: <path>` as the last line.
