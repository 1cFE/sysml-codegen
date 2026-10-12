# Brief: plan — study-layer-to-codegen (WRAP-SPLIT Item 3)

Sent by the orchestrator (agentic-mbse `/_my_orchestrate` run, 2026-10-12) to `/_my_plan`. Write the plan at `.project/active/study-layer-to-codegen/plan.md`.

## Input

- `design.md` (approved for planning at `5ef62d6`). This is the contract. Do not redesign.
- `spec.md` (amended at `4960d6b`), for the criteria SC1–SC12, the closed list B1–B12, the estimate and the cut order.
- The staged sources in `.orchestrate-logs/src/` (read-only), as listed in `briefs/design.md`.

## The owner wants speed

The owner said this run is moving slowly. Keep the plan lean:
- **Few, large phases.** Each phase is one implementing session that ends green: tests pass, ruff is clean and mypy is clean, apart from the known baseline failure. Aim for 5–7 phases. Don't split for its own sake.
- **Make parallelism explicit.** The agentic-mbse change (design Appendix B) is its own phase, run by a separate implementer in the agentic-mbse worktree. Order the sysml-codegen phases so that everything not needing that API runs first, in parallel with it: the package port, roots, declarations, the fixture and the text port. Mark each phase's dependencies.
- **Test-first where it carries weight.** Write the invariant, parity and contract tests before or with the code they pin. Skip ceremony.
- **Checkboxes and a verification command per phase.** No prose beyond what an implementer needs.

## Environment facts [AGENT, verified by orchestrator 2026-10-12]

Put these in the plan so implementers don't rediscover them:
- **sysml-codegen worktree.** `/home/reid/1cfe/sysml-codegen-study-layer`, branch `study-layer-to-codegen`.
- **Its environment.** Its `.venv` has agentic-mbse installed editable from the agentic-mbse worktree `/home/reid/1cfe/agentic-mbse-study-layer` (branch `study-layer-to-codegen`, base `ac5fb1a`), not from the `../agentic-mbse` path source. So every test command uses `uv run --no-sync`. A plain `uv run` re-syncs to `../agentic-mbse` and silently tests the wrong agentic-mbse.
  - Suite command: `uv run --no-sync --env-file /home/reid/1cfe/sysml-codegen/.env pytest tests/`.
  - Baseline: 2206 passed, 9 skipped, 1 failed (`tests/conformance/test_self_binding_guidance_contract.py::test_zero_unmarked_self_named_examples_across_all_trees`, pre-existing, not this item's).
- **agentic-mbse worktree.** Suite: `uv run pytest tests/` from `/home/reid/1cfe/agentic-mbse-study-layer`. It has its own environment, so it needs `uv sync` once. Lint: `uv run ruff check src/ tests/` and `uv run mypy src/`. Record its baseline in that phase before changing anything.
- **teax.** The checkout is at `/home/reid/1cfe/teax`, HEAD `8d87746`, with simkit at `packages/teax-simkit`. This repo's execution lane needs `TEAX_SIMKIT_PATH` and `CODEGEN_EXECUTION_PROVENANCE` (see `tests/execution/conftest.py`, `tests/helpers/teax_discovery.py` and `tests/execution/environment_pins.py`). The plan states the exact command for the teax lane.
- **Committing.** An implementer started with `run` can commit. One continued with `resume` cannot: it runs with acceptEdits, and git commit is blocked. Design phases so that each one is a fresh `run`. Commit with explicit paths (`git commit -- <paths>`) after checking the index is otherwise empty.

## Orchestrator-run evidence

Stage agents cannot reach fusion-tea, and can't run nested `claude -p` sessions reliably. So the orchestrator runs the evidence steps:
- SC4's fresh-target dry run (two agents);
- SC9's fusion-tea rehearsal (design Appendix H);
- the SC1 install from a built wheel into a scratch target;
- applying ledger rows and fusion-tea text on a fusion-tea branch (SC10).

The plan still owns them:
- name each one as a phase or step marked **orchestrator**;
- say what the implementing phases must produce first: scripts, the runbook draft, the read-through record, the fusion-tea patches drafted in this item folder;
- give each one's expected observations.

SC12's parity script is implementer-run if it needs only the staged copy in a scratch layout. If it needs teax, the implementer can use the checkout above.

## Scope

- No cuts applied up front. Keep the cut order from the spec, and mark which phase or step each cut removes, so the orchestrator can apply one mid-run without replanning.
- Give the per-phase estimate and the total.

Do not commit. Do not start background tasks. Finish with `ARTIFACT: <path>`.
