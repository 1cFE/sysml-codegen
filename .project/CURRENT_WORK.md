# Current Work

**Updated:** 2026-10-12

## Active Work

- **study-layer-to-codegen** (agentic-mbse epic WRAP-SPLIT, Item 3): move fusion-tea's `run-study` skill, study tools and `integrate.py` into sysml-codegen with an ownership-aware `install-commands`. Implementing on branch `study-layer-to-codegen`: Phase A (agentic-mbse `0843fe2`), Phase 1 (KB4 holds; package port and root split) and Phase 2 (station fixture; indicators, preflight and verify complete and fail closed; SC6; SC7) are done. Phase 3 is done: integrate is target-neutral with SC8 green, B13 covers the interpreter's platform data (entropy devices and `zoneinfo.TZPATH`), and the station returns `CANDIDATE` with all ten gates. Phase 4 is done. SC12's parity passes: all 28 cases are equal outside the closed list, under three receipt rules the orchestrator ratified. A B1 refinement pins the project root before read coverage observes a route. The fusion-tea code drafts (wrappers, a nine-route `routes.sed`, the step-5 test patch, rehearsal helpers) are written and smoke-tested. Phase 5 (the shipped text) is running in a parallel worktree. See the [plan](active/study-layer-to-codegen/plan.md).

The backlog holds separately scoped capabilities, diagnostics, model work, and assurance limits.

## Shipped State and Historical Authority

ELABORATE-FIRST closed 2026-10-10 by owner direction after final independent certification of the bounded delivered architecture and downstream scope. The final epic, audit, and aggregate product-lens are retained at `0e43cc76179e21473c36f2b30d473a3cf9626c4a:.project/backlog/epic_elaborate_first_architecture.md` and `0e43cc76179e21473c36f2b30d473a3cf9626c4a:.project/backlog/epic_elaborate_first_architecture_audit.md`. Fresh audit checks: 195 licensed passes and 53 stock-runtime passes; 21 acceptance artifact hashes matched. Four broader evidence/process criteria and Item 1's historical-clean-base conjunct remain unchecked in the Git record. Full 35-coordinate lifecycle assurance and LC-SI-23 remain PARTIAL in the [source-identity map](reference/source-identity-reconciliation.md); diagnostic, deep-override, and array bounds retain their existing dispositions.

ELABORATE-FIRST Item 8 (`elaborator-downstream`) closed 2026-10-09 after independent bounded certification. Its spec, original owner review, product-lens resolutions, and audit are retained at `33405e81b1695cd90b302dc575742458ccad5310:.project/active/elaborator-downstream/`. Fixture/customer/guidance/documentation/reconciliation outcomes are complete at the recorded bounds; full 35-coordinate lifecycle assurance and LC-SI-23 remain PARTIAL. The final epic close is recorded above.

PR-readiness cleanup closed 2026-10-09 after independent certification. C1–C10 and scoped customer compatibility are complete; audit, owner rulings, and receipts are retained at `540826abd4cb55759fd80a731a65376e25ee8afa:.project/active/pr-readiness-cleanup/`. Archived default: 2,207 passed, nine historical parity gaps; stock TEAx: 96 passed. The local `pr-readiness-cleanup` branch carries implementation; companion/customer repair branches remain separately preserved. The post-close pre-PR gate (`a082db22a120f5fa420312f96881a59b71166cd5:.project/reports/20261009-pr-readiness-pre-pr.md`) passes; merged [codegen PR #16](https://github.com/1cFE/sysml-codegen/pull/16), and [companion guidance PR #17](https://github.com/1cFE/agentic-mbse/pull/17).

REPO-CLEANUP merged through PR #15 at `6872977541eae935d4be2789f48f723ffea7101b`. Its deletion rulings and replacement evidence remain in the decision/product registers and ledger; Git retains the removed working-state artifacts.

**stop-reinventing-the-parser CLOSED by owner direction** on 2026-08-19; PR #13 shipped it. The historical rev-3 audit remains `Needs Work`, rather than being rewritten as a passing verdict. Production identity is `8a758e9240707b58fe32a509c3b509941ca4fa01`; direct evidence child is `924eadfd12f39401a6ea8e578b405d4ba8833b51`. The later owner close ruling and final product-lens dispositions are historical authority, recorded in Git's parser-close/shipment records. Internal-defect diagnostic totality remains separately filed as `[DIAGNOSTIC-PROVENANCE-BY-CONSTRUCTION]`. The predecessor dependency is satisfied.

Numeric study evidence acceptance shipped in PR #14: real multi-output numbers, dependent single-output arithmetic, and reopened-study evidence use TEAx schema v3. That runtime repair changes no codegen production representation; current candidate execution must still name its immutable artifacts.

## Context and Follow-ons

[Backlog](backlog/BACKLOG.md) lists current capabilities, model debt, and diagnostic/assurance bounds. [Product promises](product/INDEX.md) and [builder decisions](adr/INDEX.md) retain their own authority grades. Historical logs and counts are recoverable from Git and linked research, not current acceptance claims.

The mental-alignment drafts remain uncommitted owner review material.

## Project Artifact Cleanup — 2026-10-11

[OWNER] Archive closed/deprecated work and delete completed artifacts no longer needed. [AGENT] Removed historical refactor plans, completed decision-harvest intermediates, obsolete January/February investigations and probes, copied reference sources, empty memory captures, closed epic files, and completed reports. Current contracts, decisions, product promises, live ledgers, later research, and outstanding backlog scopes remain. GAP-CLOSE's historical evidence gap remains recorded in the backlog.

The permanent pre-cleanup archive is Git `a082db22a120f5fa420312f96881a59b71166cd5`; retrieve a removed tracked file with `git show a082db22a120f5fa420312f96881a59b71166cd5:.project/<path>`. An exact temporary archive, including uncommitted updates to removed records, is `/tmp/sysml-codegen-project-cleanup-20261011/removed-artifacts.tar.gz`; its manifest and checksum are in the adjacent `receipt.json`. Original mental-alignment contents and the Git index are preserved.

Verification: 73 relevant tests passed; ledger path/surface checks passed; removed-file Git citations resolve and Markdown diff checks pass.
