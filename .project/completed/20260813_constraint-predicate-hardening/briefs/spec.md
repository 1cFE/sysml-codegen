# Brief: spec stage — CONSTRAINT-SEMANTICS Item 4 (Predicate Defect Hardening)

Orchestrated run (owner-invoked `/_my_orchestrate`, check-ins waived). You are the spec stage.

## Work item

Epic: `.project/backlog/epic_constraint_semantics_contract.md`, **Item 4: Predicate Defect
Hardening** (read that section in full — it is the item's scope authority). Item location:
`.project/active/constraint-predicate-hardening/`.

Objective: remove the two reproduced predicate-boundary defects that block or obscure correct
asserted-constraint authoring:

1. **`[m]`-literal elaboration defect.** A unit-annotated literal in an asserted predicate
   (e.g. `bioshield.outer_radius == 8.55 [m]`) triggers `SI_OCCURRENCE_MISSING: leaf declaration
   … has no feature slot` even though the literal is not a missing feature occurrence; dropping
   `[m]` removes the error. Reproduced and isolated in research §6.
2. **Tautological chain-block diagnostic.** When the profile blocks a feature chain inside a
   predicate, the message is literally `feature_chain: block_feature_chain` — no offending
   reference, no location; `LayerContinuity` emits 13 identical copies. The fix must name the
   exact written reference and state the supported rewrite (bind the chain to a formal, use the
   formal in the predicate body). Multi-chain predicates must identify each distinct offending
   reference deterministically.

## Provenance you must preserve

- The must-fix disposition of both defects is **[INHERITED: rulings-20260812.md Q8]**.
- Boundary/slicing authority is **[AGENT] (ratified by owner, 2026-08-12)**.
- Behavioral requirements inherit from `.project/active/constraint-semantics-contract/spec.md`
  ("Migration, fixtures, and defects" + Non-Goals) unless separately marked.
- Nothing in this item is owner-originated-settled beyond the Q8 must-fix disposition; do not
  upgrade grades.

## Required reading

- `.project/backlog/epic_constraint_semantics_contract.md` — Item 4 section (scope, success
  criteria, out-of-scope).
- `.project/active/constraint-semantics-contract/spec.md` — Migration/fixtures/defects section
  and Non-Goals.
- `.project/research/20260812-101200_constraint-semantics-end-to-end.md` §6 (defect
  reproductions) and Code References section.
- `.project/active/constraint-semantics-contract/rulings-20260812.md` Q4 and Q8.

## Hard boundaries (umbrella spec Non-Goals — restate in your Out of Scope)

- Do NOT admit feature chains inside predicate bodies (filed as a future capability; Q4 ruling
  is bindings-only now). The chain fix is a *diagnostic* fix, not an admission.
- Do NOT build first-class tolerance semantics for `==` or expand the executable profile.
- The frozen twins `catf_mfe_model` / `catf_mfe_d5` keep their constraint syntax unchanged.

## Context the item builds on (landed, on these worktrees)

- Items 1–3 have landed on codegen branch `item7-rebuild` (tip `546ac20`) and companion worktree
  `/home/reid/1cfe/agentic-mbse-item7-rebuild` (tip `bc69f04`). Item 2 gave every authored
  constraint usage a catalog carrier with one disposition; severity follows cause. Your spec
  must not contradict the landed Item 2 disposition/severity contract — a blocked chain in a
  *plain* constraint still generates and catalogs unassessed; an asserted one halts (BLOCK).
- The elaboration route is the only route (exact route; `elaboration/` in codegen). The profile
  (form gate / predicate admission) partly lives in the companion (agentic-mbse).

## Environment facts (record in the spec so later stages inherit them)

- Test interpreter: `/home/reid/1cfe/item7-rebuild-venv/bin/python -m pytest` — NOT `uv run`
  (uv resolves the companion to the wrong checkout).
- License: `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a` before licensed runs;
  a green run with license-skip lines is not a full run.
- Lint baselines: `ruff check src` = 12, `mypy src` = 55 (zero-new gates).
- TEAx is untouched by this item and its checkout must stay on `constraint-semantics-item3`.

## Success criteria to carry (from the epic, verbatim in substance)

- An asserted predicate containing a compatible unit-annotated literal elaborates without
  `SI_OCCURRENCE_MISSING`; incompatible-unit behavior remains governed by the profile.
- A blocked feature chain names the exact offending written reference and the bindings rewrite;
  a multi-chain predicate identifies each distinct offending reference deterministically.
- Kept failing characterizations are added BEFORE the fixes (the epic's de-risking posture).
- Existing quantity, occurrence, profile, and diagnostic tests do not regress.
- Focused companion/codegen tests, full maintained suites, ruff/mypy zero-new, and
  `git diff --check` pass with exact counts recorded.

## Your deliverable

`.project/active/constraint-predicate-hardening/spec.md`. Investigate the two defects in the
code far enough to state precise, testable requirements (including where each defect lives —
codegen vs companion — and the reproduction shapes), but do not design the fix. End with
`ARTIFACT: <path>`.
