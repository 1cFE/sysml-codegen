# Brief: plan stage — CONSTRAINT-SEMANTICS Item 4 (Predicate Defect Hardening)

Orchestrated run (owner-invoked `/_my_orchestrate`, check-ins waived). You are the plan stage.
Work synchronously: never pause for background agents; finish the artifact this turn and end
with `ARTIFACT: <path>`.

## Input

- Design (mechanism authority, revised after review — read in full):
  `.project/active/constraint-predicate-hardening/design.md`
- Spec (requirements + success criteria): `.project/active/constraint-predicate-hardening/spec.md`
- Review + resolutions: `.project/active/constraint-predicate-hardening/design-review.md`
- Orchestrator-verified companion evidence (incl. P4 verdict and the verbatim REASON_CODES
  list for the M3 reconciliation):
  `.project/active/constraint-predicate-hardening/probes/companion-evidence.md`

## What the plan must encode

- **Phases with checkboxes** sized for one implement session (this is a 0.5–1 day item), each
  phase ending in a committed, green state in BOTH trees (editable-install coupling: the
  codegen licensed suite imports the companion worktree live).
- **Red-first**: characterizations land as `xfail(strict=True)` with the red demonstrated by
  a marker-removed run whose output is captured into the item folder (design D8 + review A3),
  BEFORE the fixes. Then fixes land and the markers come off (strict xfail forces this).
- **The designed landing order** across codegen + companion — take it from the design's
  Landing Order section, do not invent one.
- **Probes P1/P3 at their designed points** (P3 before/at the D2 step, P1 at the fixture
  step; P2 is a regression guard, not a gate). Each probe's discriminating outcome and the
  branch it selects are in the design.
- **Verification phase**: focused tests; full licensed codegen suite
  (`/home/reid/1cfe/item7-rebuild-venv/bin/python -m pytest`, after
  `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a`; zero license-skip lines or the
  run is not full); full companion suite (default selection — NEVER `-m ""`, the corpus trap);
  `ruff check src` = 12; `mypy src` = 55; `git diff --check` both repos; exact counts recorded
  in `verification.md`. Also the M3 reconciliation into the close record.
- **Environment facts** from the spec's Cross-cutting section restated where the implementer
  will trip on them (interpreter, license, TEAx stays on `constraint-semantics-item3`, frozen
  twins untouched, new fixtures only).
- Commit discipline: one commit per phase minimum, subjects leading with the decision;
  companion commits in the companion worktree (`git -C`), never mixed.

## Deliverable

`.project/active/constraint-predicate-hardening/plan.md` with phase checkboxes and a
per-phase "how to verify" line. End with `ARTIFACT: <path>`.
