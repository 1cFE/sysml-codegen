# Brief — Phase 1 implement (relaunch): verify the base and establish the red closure harness

You are executing **Phase 1 only** of an approved implementation plan. A prior Phase 1 attempt
correctly tripped a stop rule before writing anything; the design and plan have since been amended
and the blocking questions owner-ruled. You start clean. Read in order:

1. `.project/active/stop-reinventing-the-parser/plan.md` — **Revision 3**, your contract. Execute
   "Phase 1: Verify the base and establish the red closure harness" exactly, including the Global
   Execution Contract (three-leg lock verification; two-case indexed red set; the committed
   historical-tree lock check as a kept test; `deep_cross_scope_probe` never-restore stop
   condition).
2. `design.md` — **Revision 7** — sections the phase links, especially
   `#what-the-lock-is-verified-against`, `#the-missing-committed-check--phase-1-adds-it`,
   `#current-code-facts`, `#the-indexed-red-set--both-cases-are-required-kept-tests`,
   `#inventory-refusal-precedes-occurrence-resolution`, `#occurrence-and-producer-matrix`,
   `#checked-consumer-and-ownership-manifests`.
3. `run-records/phase1-stop-report.md` — why the first attempt stopped; its rulings are
   owner-ratified and already folded into the documents above. Do not re-litigate them.
4. `run-records/entry-status.md` — run scaffolding.

Provenance: plan rev 3 and design rev 7 are the binding contracts. This brief's operational notes
are orchestrator [AGENT] material; on any conflict the plan/design win and you surface the
conflict in your final message instead of resolving it silently.

## The intent you serve

A reference the toolchain cannot honor must be refused by name before any graph, snapshot,
package, or output mutation escapes — never silently rewritten. Phase 1 proves the implementation
starts from the audited trees and records the failure class as kept red tests before any
production edit. The red set is **two cases, each red for its exact stated reason**:

- **Case 1** — `picked = cells#(2).mass` with `cells : Cell[1]` (index out of range): at `C_base`
  this must produce a **zero-diagnostic graph** silently binding occurrence zero. That collapse is
  the escape.
- **Case 2** — `picked = cells#(2).mass` with `cells : Cell[3]`: at `C_base` this must refuse as
  `SI_OCCURRENCE_AMBIGUOUS` (the wrong name); the kept test pins that starting diagnostic and
  requires it to become `SI_INDEXED_SOURCE_UNSUPPORTED`.

A different failure than each case's stated red is not the proof point — a `C_base` result that
differs from the design's behavior matrix is a design conflict: STOP and report.

## Where you work [AGENT]

- Codegen worktree: `/tmp/stop-parser-rev2/worktrees/sysml-codegen` (branch `stop-parser-impl-r2`
  at `C_base` = `78a9beb9…`, verified clean). Codegen test/manifest commits go here.
- Agentic worktree: `/tmp/stop-parser-rev2/worktrees/agentic-mbse` (branch
  `stop-parser-evidence-r2` at `A_base` = `2171016d…`, verified clean). Agentic test commits go
  here.
- Docs checkout: `/home/reid/1cfe/sysml-codegen` (branch `stop-reinventing-the-parser`). Only the
  plan.md "Phase 1 completion" section update is committed here, as your final act. Never run
  implementation commands from it; never import production code from it.
- Touch NOTHING else — no other checkout, no `/tmp/stop-parser.QVJIIP/*` worktree (read-forbidden
  for code), no stash/reset/switch anywhere. Re-verify both worktrees are clean before starting.
- Read-only probe models from the stop investigation exist at `/tmp/stop-parser-rev2/scratch/`;
  you may consult them, but your kept test fixtures are authored fresh in the worktrees.

## Hard constraints (from plan rev 3 — binding)

- **No production source changes in Phase 1.** Tests, manifests, and phase records only.
  `git diff C_base -- src/sysml_codegen/elaboration/occurrence.py` must be empty at phase end.
- **Lock verification runs on the three legs** — leg 1 against the tree the lock itself names
  (assert `probe_fixture_commit == 20f9e60a…` read from the lock file; never hard-code
  `43edf9bd`), leg 2 through the committed `capture_baseline.py` validators, leg 3 the six
  verification/probe rows at current bytes with the one known `capture_baseline.py` difference
  ledger-owned. Any leg failing: STOP. Never re-derive the lock.
- **Add the committed historical-tree lock check as a kept test** per the design's five bullet
  obligations (read the field from the lock file; recompute all 118 from Git at that tree;
  anti-vacuity on the count; leg-3 current-byte assertions; never read the working tree for
  historical bytes, never rewrite the lock).
- Leg 3's ledger row for `capture_baseline.py` (citing `da4aa78` and `46694e2`) is part of this
  phase's manifest/ledger work if the plan places it here — follow the plan's checklist placement.
- D1-D4 occurrence and mutation tests must stay green; any regression is a stop-rule trip.
- `deep_cross_scope_probe` must read as a typed refusal; any change restoring its captured graph
  is a global stop condition.
- **[OWNER-VERBATIM, 2026-08-17]** "do not rerun the PDF suite anymore." Never invoke the Agentic
  slow PDF/HTML corpus suite or the 15 paid/network cases; never report them in any status.
- Record the exact expected-red node IDs in the phase record.

## Environment notes [AGENT]

- SysIDE license: `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a` before licensed
  tests. Never copy `.env`, its value, or any secret into an artifact, commit, or report.
- Codegen commands: `uv run --extra dev …`. Agentic commands: `uv run …`. First run in each
  worktree syncs; expected.
- Do not install or update unrelated dependencies.

## Deliverables

1. Commits on the two implementation branches: exactly the Phase 1 checklist's tests/manifests and
   nothing else.
2. Every Phase 1 validation box executed with commands and results recorded, including the
   three-leg lock verification results and both red cases failing for their exact stated reasons.
3. plan.md "Phase 1 completion" section filled (completed items, commit SHAs on both branches,
   actual changes and test results including the recorded red node IDs, issues/deviations,
   rollback point) and committed in the docs checkout.
4. Final message: prose summary — base verification, the recorded red set with each case's reason,
   D1-D4 status, deviations — ending with
   `ARTIFACT: .project/active/stop-reinventing-the-parser/plan.md`. If any stop rule tripped, say
   so plainly at the top and stop.

Phase 1 is the end of your scope. The run pauses for the owner after this phase; do not begin
Phase 2 work of any kind.
