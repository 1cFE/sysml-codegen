# Brief — Phase 2 implement: close the Agentic evidence contract

You are executing **Phase 2 only** of an approved implementation plan. Phase 1 is complete,
audited (Pass with findings; all four Majors closed), and owner-closed — do not reopen, rerun, or
modify any Phase 1 artifact except as this phase's checklist directs. Read in order:

1. `.project/active/stop-reinventing-the-parser/plan.md` — **Revision 3**, your contract. Execute
   "Phase 2: Close the Agentic evidence contract" exactly, including the Global Execution
   Contract. The "Phase 1 completion" section records what already exists, including the 10
   Agentic red test nodes your work must turn green.
2. `design.md` — **Revision 7** — sections the phase links, especially
   `#d5-public-agentic-evidence-contract`, `#d6-documenttier-owns-b5`,
   `#agentic-semantic-contract`, `#closed-reference-use-values`,
   `#one-total-inspection-operation`, `#delete-the-permissive-production-surface`,
   `#documentation-and-backlog-obligations`.
3. `run-records/phase1-audit.md` — the Phase 1 audit. Its Minors 5 and 11 are **assigned to this
   phase** (details below). Rulings and Majors are closed; do not re-litigate.
4. `run-records/entry-status.md` — run scaffolding.

Provenance: plan rev 3 and design rev 7 are the binding contracts. This brief's operational notes
are orchestrator [AGENT] material; on any conflict the plan/design win and you surface the
conflict in your final message instead of resolving it silently.

## The intent you serve

A reference the toolchain cannot honor must be refused by name — never silently rewritten into
another expression. Phase 2 makes exact parser evidence the only representable form on the Agentic
side: one provenance-complete inspector (`inspect_reference_uses`) serves expression traversal,
aggregation, binding, ADR002, and math reconstruction, and the permissive fact/helper surface is
deleted atomically with no deprecation path. Codegen does not consume the new artifact until
Agentic is independently green — that boundary is Phase 3's, not yours.

The 10 Phase-1 Agentic red nodes (listed in plan.md's Phase 1 completion section, on
`stop-parser-evidence-r2` at `8d27fb3`) are the green contract: your implementation must turn
exactly those tests green for their stated reasons, not replace them with easier tests.

## Where you work [AGENT]

- Agentic worktree: `/tmp/stop-parser-rev2/worktrees/agentic-mbse` (branch
  `stop-parser-evidence-r2` at `8d27fb3`, verified clean). ALL implementation commits go here.
- Docs checkout: `/home/reid/1cfe/sysml-codegen` (branch `stop-reinventing-the-parser`). Only the
  plan.md "Phase 2 completion" section update is committed here, as your final act. Never run
  implementation commands from it.
- The Codegen worktree `/tmp/stop-parser-rev2/worktrees/sysml-codegen` is **not yours this
  phase** — read-only if you need to consult the Phase 1 tests; commit nothing there.
- Touch NOTHING else — no user checkout (`/home/reid/1cfe/agentic-mbse` included), no
  `/tmp/stop-parser.QVJIIP/*` worktree (read-forbidden for code), no stash/reset/switch anywhere.
  Re-verify the worktree is clean at `8d27fb3` before starting.

## Hard constraints (from plan rev 3 — binding)

- **Tests first.** Complete `tests/test_sysml/test_reference_use.py` and the consumer/boundary
  test extensions before production edits.
- **Atomic deletion, no compatibility path.** `extract_feature_refs`,
  `feature_reference_facts`, `feature_chain_facts`, `ResolvedSemanticReferenceFact`,
  `has_index_segment`, `ExpressionRef`, `BindingInfo.references` — removed from production,
  exports, lazy aliases, tests, and docs. No wrapper, alias, or manifest exemption. A consumer
  that cannot migrate without reconstructing the weak route is a **design conflict: STOP** and
  report; do not work around it.
- **Scoped strict gate:** `uv run mypy --strict src/agentic_mbse/errors.py
  src/agentic_mbse/sysml/reference_use.py` must return zero errors.
- **Version/package contract:** bump Agentic to `0.1.3`; update `pyproject.toml`, package
  version, `uv.lock`, public API assertions, `docs/patterns/plant-idiom.md` per the design's
  documentation obligations.
- **Artifact-isolated validation:** build a clean Agentic source archive and wheel from the phase
  commit; rerun the focused and fast gates from the extracted archive and verify installed
  version/API markers.
- **[OWNER-VERBATIM, 2026-08-17]** "do not rerun the PDF suite anymore." Never invoke the Agentic
  slow PDF/HTML corpus suite or the 15 paid/network cases; never report them in any status.
- `IndexExpression` dispatch must come from the mapped SysIDE metatype, never a runtime
  class-name comparison.
- Baseline discipline: repository-wide mypy/Ruff are comparisons against `A_base`; item-caused
  diagnostics are forbidden, and a nonzero baseline must not be described as green.

## Audit findings assigned to this phase (close them; cite the closure in the phase record)

- **Minor 5:** `PERMISSIVE_SYMBOLS` in `tests/test_sysml/test_semantic_selector_ownership.py`
  omits four of the seven ordered deletions — `extract_feature_refs`,
  `ResolvedSemanticReferenceFact`, `ExpressionRef`, `BindingInfo.references`. Extend the
  symbol-absence gate to cover all seven before/with the deletion so the gate actually proves it.
- **Minor 11:** `tests/test_sysml/test_reference_use.py:80-88` passes the
  `IndexedReferenceUse` **class** (not an instance) to `build_aggregation_term` and catches broad
  `Exception`. Tighten to `pytest.raises(SemanticEvidenceError)` over a constructed instance, and
  make the test actually prove refusal happens before term construction.

## Environment notes [AGENT]

- SysIDE license: `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a` before licensed
  tests. Never copy `.env`, its value, or any secret into an artifact, commit, or report.
- Agentic commands: `uv run …` from the worktree. First run syncs; expected.
- **Known `A_base` baseline (not yours):** the fast suite has 18 pre-existing failures — 17 in
  `tests/test_web_backend.py`, 1 in `tests/test_equations.py`, all `ModuleNotFoundError` for
  optional deps (`PIL`, web backend). Do not install those deps and do not count these against
  your work; do not describe them as green either.
- One baseline test asserts the checkout path contains the string `agentic-mbse` — when you build
  the clean-extraction validation root under `/tmp/stop-parser-rev2/`, keep that string in the
  directory name.
- Do not install or update unrelated dependencies.

## Deliverables

1. Commits on `stop-parser-evidence-r2`: the Phase 2 checklist's tests and production changes,
   committed in reviewable units (tests-first commit(s), then implementation).
2. Every Phase 2 validation box executed with commands and results recorded: all 10 Phase-1 red
   nodes green, scoped strict zero, fast suite with the declared skip/baseline set, symbol-absence
   searches, clean-archive/wheel gates, and the two manual inspections.
3. plan.md "Phase 2 completion" section filled (completed date, commit SHAs, actual changes and
   test results, issues/deviations, rollback point) and committed in the docs checkout.
4. Final message: prose summary — what landed, the red-to-green account, deletion closure, static
   gates, deviations — ending with
   `ARTIFACT: .project/active/stop-reinventing-the-parser/plan.md`. If any stop rule tripped, say
   so plainly at the top and stop.

Phase 2 is the end of your scope. Do not begin Phase 3 work of any kind.
