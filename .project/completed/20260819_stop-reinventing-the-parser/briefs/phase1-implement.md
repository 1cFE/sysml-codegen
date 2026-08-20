# Brief — Phase 1 implement: verify the base and establish the red closure harness

You are executing **Phase 1 only** of an approved implementation plan. Read these first, in order:

1. `.project/active/stop-reinventing-the-parser/plan.md` — your contract. Execute the section
   "Phase 1: Verify the base and establish the red closure harness" exactly, including its Global
   Execution Contract.
2. `design.md` sections the phase links: `#revision-6-implementation-base`, `#current-code-facts`,
   `#load-bearing-bets`, `#test-design`, `#checked-consumer-and-ownership-manifests`,
   `#occurrence-and-producer-matrix`.
3. `.project/active/stop-reinventing-the-parser/run-records/entry-status.md` — the run scaffolding.

Provenance: plan.md (rev 2) and design.md (rev 6, review verdict Approve) are owner-ratified
artifacts — treat their requirements as binding. Everything in this brief marked [AGENT] is
orchestrator operationalization, not owner intent; if it conflicts with plan/design, the plan wins
and you surface the conflict in your final message instead of resolving it silently.

## The intent you serve

A reference the toolchain cannot honor must be refused by name before any graph, snapshot, package,
or output mutation escapes — never silently rewritten into another expression. Phase 1 proves the
implementation starts from the audited trees and reproduces the known escape
(`cells#(2).mass` reaching the computed-attribute route with **zero diagnostics**, aliased to
`cells[0].mass`) as a **kept, recorded red test set** before any production edit. Phase 1 ends red
on purpose. Phases 2–4 will turn these exact tests green; do not soften them to make them pass.

## Where you work [AGENT]

- Codegen implementation worktree: `/tmp/stop-parser-rev2/worktrees/sysml-codegen`
  (branch `stop-parser-impl-r2`, rooted at `C_base` = `78a9beb9…`). Codegen test/manifest commits go here.
- Agentic implementation worktree: `/tmp/stop-parser-rev2/worktrees/agentic-mbse`
  (branch `stop-parser-evidence-r2`, rooted at `A_base` = `2171016d…`). Agentic test commits go here.
- Docs checkout: `/home/reid/1cfe/sysml-codegen` (branch `stop-reinventing-the-parser`). Only the
  plan.md "Phase 1 completion" section update is committed here, as your final act. Never run
  implementation commands from it and never import production code from it.
- Touch NOTHING else: no other checkout, no `/tmp/stop-parser.QVJIIP/*` worktree (historical
  evidence of the failed candidate — read-forbidden for code; you derive everything from the
  worktrees above), no stash/reset/switch anywhere.

## Hard constraints (from the plan — binding)

- **No production source changes in Phase 1.** Tests, manifests, and phase records only.
  `git diff C_base -- src/sysml_codegen/elaboration/occurrence.py` must be empty at phase end.
- The two retained commits (`20f9e60a…` probe, `43edf9bd…` lock) must be proven ancestors of
  `C_base`, and every locked probe/fixture hash must recompute before and after the phase. On any
  mismatch: STOP and report — do not recreate probes from baseline `7b29d8b`.
- The proof point is exact: the licensed computed-attribute test must fail because the model reaches
  a zero-diagnostic graph. A fixture, license, import, or harness failure is NOT the proof point —
  if you cannot reproduce the exact red, STOP and report it as a stop-rule trip.
- D1-D4 occurrence and mutation tests must stay green; any regression is a stop-rule trip.
- **[OWNER-VERBATIM, 2026-08-17]** "do not rerun the PDF suite anymore." Never invoke the Agentic
  slow PDF/HTML corpus suite or the 15 paid/network cases; never report them in any status.
- Record the exact expected-red node IDs in the phase record.

## Environment notes [AGENT]

- SysIDE license: `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a` before licensed tests.
  Never copy `.env`, its value, or any secret into an artifact, commit, or report.
- Codegen commands run with `uv run --extra dev …`; Agentic with `uv run …` (plan's validation
  contract). First `uv run` in each worktree will sync; that is expected.
- Do not install or update unrelated dependencies.

## Deliverables

1. Commits on the two implementation branches: new/extended test files and manifests exactly as the
   Phase 1 checklist names them, plus nothing else.
2. Every Phase 1 validation box executed, with commands and results recorded.
3. plan.md "Phase 1 completion" section filled (completed items, commit SHAs on both branches,
   actual changes and test results including the recorded red node ID list, issues/deviations,
   rollback point) and committed in the docs checkout.
4. Final message: a prose summary — base verification results, the recorded red set, D1-D4 status,
   any deviation — ending with `ARTIFACT: .project/active/stop-reinventing-the-parser/plan.md`.
   If a stop rule tripped, say so plainly at the top and do not proceed.
