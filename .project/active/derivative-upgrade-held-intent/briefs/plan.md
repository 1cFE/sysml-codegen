# Orchestrator brief — plan stage, CONSTRAINT-SEMANTICS Item 9

## Input

Design (rev 2, review-accepted): `.project/active/derivative-upgrade-held-intent/design.md`.
Spec: `spec.md` beside it. Both committed. The design's change list, expectation table, and
PROVENANCE edit list are the material; the plan turns them into phased, checkboxed execution
that a single implement session (or two) can walk without re-deriving anything.

## Ordering constraints the plan must honor

1. **Snapshot capture/re-seal de-risk FIRST** — it is the one lane the design probe did not
   exercise. Before any expectation is committed, prove the edited fixture captures and
   re-seals (v6 snapshot) cleanly.
2. **SC-6 discipline**: source edits → read A9's new `source_line` from source → write and
   commit ALL expectations (manifest JSON, population JSON, expected-coverage.md,
   test literals, PROVENANCE) in a commit that precedes the first confirmation run.
3. Prover extension (`check_gated_manifest.py` per-occurrence DERIVATIONS + three anchor-failure
   cases as reported problems) and its occurrence-scoped falsification tests.
4. The BACKLOG edits: SC-3 side 2 one-liner on `[INLINE-PREDICATE-MARKER-DROP]` and the new
   `ProductWithinBand` per-dimension-cost entry (decision-record phrasing, design change-list
   row 9).
5. Final gates: focused tests; full licensed suite via
   `/home/reid/1cfe/item7-rebuild-venv/bin/python -m pytest` with
   `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a` (zero license-skip lines is the
   only licensed proof); ruff zero-new (baseline 12); mypy zero-new (baseline 52);
   `git diff --check`; byte-untouched verification for the frozen twins
   (`catf_mfe_model`, `catf_mfe_d5`) AND the archived
   `.project/completed/20260813_catf-constraint-policy-acceptance/`; exact counts recorded in
   `verification.md`.

## Constraints

- No re-disposition, no TEAx change, no schema change, nothing pushed, no `main`.
- Known baseline failure that is NOT this item's: `tests/execution/...::test_the_lane_runs_the_real_simkit`
  fails on whole-set runs, passes in isolation (collection-order artifact, pre-existing,
  unowned). Do not chase it; record it if hit.
- Commit discipline: the plan should name its commit points (expectations-before-confirmation
  is one of them). The orchestrator or the implement stage commits per plan phase; keep other
  agents' files out of every commit.

## Deliverable

`plan.md` in the item folder: phases with checkboxes, per-phase verification, commit points,
and a rollback note for the fixture edits. Keep it tight — the design already carries the
detail; the plan sequences it. Do not commit — the orchestrator commits.
