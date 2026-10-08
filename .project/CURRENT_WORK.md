# Current Work

**Updated:** 2026-10-08

## Active Work

### PR-readiness cleanup — audited; ready for close

[OWNER] Authorized `$my-orchestrate` through implementation and independent audit, using best judgment and keeping the work simple. [Spec](active/pr-readiness-cleanup/spec.md), [design](active/pr-readiness-cleanup/design.md), [plan](active/pr-readiness-cleanup/plan.md), and [evidence](active/pr-readiness-cleanup/evidence.md) carry the current contract and progress.

[AGENT] Work is isolated in `/tmp/pr-readiness-cleanup-run` on `pr-readiness-cleanup`; its companion guidance branch is `/tmp/pr-readiness-agentic-mbse`. The original checkout's index and mental-alignment drafts are preserved. The pre-change oracle covers all 22 committed snapshots. Licensed freshness identified two pre-existing metadata/order recaptures in addition to the owner-directed unit/driver changes; exact dispositions live in the evidence record.

[AGENT] C1–C10 are implemented. Archived final codegen `0046fa1535ec0f3581b08ab8436fd47825965b51` passes 2,207 default tests with nine named historical parity-golden gaps and 96 separately executed runtime tests. All 18 current customer generation units are compared; principal-family runtime, mutations, and handwritten preservation pass after two reproduced consumer-test defects were repaired in isolated customer commit `455c1ede893816e6ffabddff69f90d14aed8ee19`. The full replacement-evidence checker passes after bounded stale-reference repairs; the independent [audit](active/pr-readiness-cleanup/audit.md) certifies this cleanup with no unresolved material findings. The October customer cleanup reports supply failure context rather than a numerical acceptance threshold.

### ELABORATE-FIRST Item 8 — retained assurance reconciliation

The elaborator implementation shipped in PR #10, parser/identity follow-through in PR #13, and repository retirement in PR #15. The [downstream spec](active/elaborator-downstream/spec.md) retains one Item 8 completion authority; this cleanup supplies its remaining fixture/documentation/evidence reconciliation. Final [source-identity mapping](reference/source-identity-reconciliation.md) must preserve unsupported shapes, diagnostic debt, and partial evidence bounds. Item 8 and the epic remain open for audit/close; no new proof is manufactured for owner-descoped scope.

## Shipped State and Historical Authority

REPO-CLEANUP merged through PR #15 at `6872977541eae935d4be2789f48f723ffea7101b`. Its deletion rulings and replacement evidence remain in the decision/product registers and ledger; Git retains the removed working-state artifacts.

**stop-reinventing-the-parser CLOSED by owner direction** on 2026-08-19; PR #13 shipped it. The historical rev-3 audit remains `Needs Work`, rather than being rewritten as a passing verdict. Production identity is `8a758e9240707b58fe32a509c3b509941ca4fa01`; direct evidence child is `924eadfd12f39401a6ea8e578b405d4ba8833b51`. The later owner close ruling and final product-lens dispositions are historical authority, recorded in Git's parser-close/shipment records. Internal-defect diagnostic totality remains separately filed as `[DIAGNOSTIC-PROVENANCE-BY-CONSTRUCTION]`. The predecessor dependency is satisfied.

Numeric study evidence acceptance shipped in PR #14: real multi-output numbers, dependent single-output arithmetic, and reopened-study evidence use TEAx schema v3. That runtime repair changes no codegen production representation; current candidate execution must still name its immutable artifacts.

## Context and Follow-ons

[Backlog](backlog/BACKLOG.md) lists current capabilities, model debt, and diagnostic/assurance bounds. [Product promises](product/INDEX.md) and [builder decisions](adr/INDEX.md) retain their own authority grades. Historical logs and counts are recoverable from Git and linked research, not current acceptance claims.

The mental-alignment drafts remain owner review material; this cleanup neither includes them in its branch nor changes their original staged/unstaged contents. Close and the post-close pre-PR gate remain the next human-controlled boundary after independent audit.
