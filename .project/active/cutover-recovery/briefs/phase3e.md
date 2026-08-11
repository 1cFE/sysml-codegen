# Stage brief — Phase 3, Slice 3E: Public authority switch

**You are executing exactly one slice** of the owner-approved recovery plan:
`/home/reid/1cfe/sysml-codegen-item7-rebuild/.project/active/cutover-recovery/plan.md`.
Read first: rules, Slice 3E, per-slice validation, "Overall validation" (real TEAx before the
switch, after the switch), completion notes 3A–3D, `evidence/audit-3{a,b,c,d}.md`.

## Intent

Every supported public caller — CLI and public API — constructs through the exact route. The
legacy implementation becomes unreachable from public surfaces but is NOT deleted (Phase 4's
job, against its ledger). No public flag, env var, or config may select between two authorities.
This is the slice where shipped artifacts change; every change must be explained, classified,
and pinned before commit.

## State you inherit

- Heads: codegen `0a812af`, agentic `cc6c7a7`, both clean. Suites: codegen 3539/47/38 licensed
  (38 = execution lane, runs green, no skips); agentic 1825/1/5. mypy 71/17 measured; ruff 16.
- Venv + license + PYTHONPATH-for-old-commits discipline as recorded (F2 trap, 3C process note).
- Real-TEAx evidence exists at `0a812af` (pre-switch): 11 channels, LCOE `270.1211779380445`,
  live=relocated. That is your "before" anchor; re-run it after the switch.

## Orchestrator rulings you carry in (recorded, not yours to relitigate)

1. **d38_caret** and **unresolvable_attr_probe** exact-vs-legacy divergences: classified
   **expected-fix** at the switch. Rationale: the epic's ratified premise is that string-era
   attribution is the defect home; the exact behaviors are pinned as correct by Item 6 tests
   (three-concrete-instances scoping) and by declaration-site semantics. At 3E: amend the
   dual-run ledger rows with measured before/after cells (old cells retained), update the two
   defect-to-disposition pins to expected-state pins, and flag both in the plan for the Phase 5
   owner packet. Both are fixture-internal; NO customer-model group naming changes (3B measured
   stem-case equality; re-verify for fusion_tea in the package diff).
2. **Provenance-comment fingerprint residual** (SysML Source lines → differing
   `executable_fingerprint` between live and relocated): carried as a named residual to the
   Phase 5 packet, not fixed in 3E unless the switch itself requires it.
3. **Checklist reconciliation** (3D audit process note): the "Validation for every Phase 3
   slice" checklist is unchecked for 3A–3D. Reconcile it once in this slice: per slice, mark
   each item with its evidence pointer (audit record section or commit), honestly marking
   anything not done.

## Requirements

1. **Tests first:** public import/CLI tests proving (a) `generate --models` and
   `generate --from-snapshot` construct through the exact route (assert by behavior/receipt, not
   by symbol identity alone); (b) no public flag exposes two authorities (enumerate the CLI
   surface and public API exports; a test must fail if a dual-authority escape hatch appears);
   (c) a v5 snapshot fed to `--from-snapshot` produces a TYPED refusal naming the v6
   requirement — not a silent legacy fallback, not a stack trace. Red at `0a812af` where
   applicable.
2. **Switch the callers.** Minimal production diff: route the public builders/CLI through
   `exact_pipeline_context` / v6 capture-load. Do not delete or gut `pipeline_builder.py`,
   `snapshot_context.py`, the v5 loader, or any legacy module — unreachable is the goal,
   absence is Phase 4's.
3. **Generated-package comparison, legacy vs exact, fusion_tea + representative fixtures:**
   diff the full trees. Classify EVERY difference: provenance-only / expected-fix (cite the
   ledger row or pin) / unexplained → rule-10 STOP. Expect and explain the `system_design`
   hierarchy-group difference if it appears in fusion_tea; hand-checked modeled values must be
   unchanged.
4. **Repeat the full battery after the switch:** 37-path corpus vs the amended ledger (15/22,
   both error classes, exact multisets); both full suites from paired worktrees; real TEAx on
   live and relocated v6 through the SWITCHED public surface (the same hand values must hold);
   legacy-route tests that pin shipped-CLI behavior may need reclassification — any test whose
   subject is "the CLI uses the legacy builder" gets a recorded disposition (rewrite to the
   exact expectation with evidence, never silent deletion; the count delta must be explained
   row by row).
5. **Gates:** ruff byte-identical; mypy measured (71/17 or better, stated as measured);
   `git diff --check`; declared path sets; one switch commit + OID record, separate from
   everything deletion-shaped; agentic `N/A if unchanged`.

## Hard rules

Unchanged. Rule-10 stops: any unexplained package diff, any corpus row moving beyond the two
ruled expected-fixes, any hand-value change, any surviving public path to the legacy authority,
any test deletion.

## Report back

What switched and how it's proven single-authority; the package-diff classification table; the
after-switch real-TEAx and corpus results; test reclassification rows; checklist reconciliation
summary; gates; OIDs. `ARTIFACT:` the updated plan.
