# Current Work

**Updated:** 2026-10-20

## Active Work

EXEC-SUBSET-CONTRACT Item 2b (`subset-profile-screen`, epic in agentic-mbse): implementation in progress on branch `subset-profile-screen`, plan `.project/active/subset-profile-screen/plan.md`. Phases 0-3 done (baselines and probes, then the three pure moves: shared load, module split, `prepare` → `emit_package`) Phase 4 (every model refusal before the destination) and Phase 5 (writers' re-checks dropped, reachability test) done; Phase 6 is next; Phase 10 (readiness rule D8) waits on the owner.

The backlog holds separately scoped capabilities, diagnostics, model work, and assurance limits.

## Shipped State and Historical Authority

EXEC-SUBSET-CONTRACT Item 2a (`subset-profile-conformance`) closed 2026-10-20, certified (final-audit re-check 2026-10-19), then integrated with the merged epic Item 3 (agentic-mbse PR #32). It is not merged yet: branch `subset-conformance` here and in agentic-mbse, for a coordinated merge. sysml-codegen now checks the shared subset contract (`subset-profile/v2`) against what the generator actually does: 246 conformance cases with stored answers (154 of them packaged in agentic-mbse), a per-site account of every refusal, detector-disable mutations, and the occurrence-parity test. A change to the generator's accept/refuse behaviour fails a test here. Spec, design, plan, audit, evidence and the owner-gate drafts are retained at `c381fb00eb8e51248f68701e00ac997ebf2cd413:.project/active/subset-profile-conformance/`. The agentic-mbse gate receipt names codegen `ceb6796e`; the close touches only `.project/` and `docs/`.

Still with the owner, not decided at close:

- **RG-1**: 12 candidate changes to what the generator accepts or refuses (`rg1-recommendations.md` in the retained folder). Backlog rows `[CALC-USAGE-BINDING-LOST-WITH-RESULT-EXPRESSION]`, `[CALC-DEF-KEYWORD-MEMBER-STUB]` and `[ITEM-OWNED-PART-REFUSED]` depend on it.
- **RG-2**: the String metadata policy (`rg2-string-policy.md` in the retained folder).
- **RG-3**: the coordinated merge, and filing the staged amendments to ADR 0001, ADR 0012, ADR 0016 and P-0001 and the fact-placement ADR draft (all in the retained folder). Check the owner's `adr-0012-occurrence-summary-amendment` branch first: at `8396cb23` it already adds ADR 0018, which amends ADR 0012 for the shared occurrence summary. Whether that covers the staged ADR 0012 amendment was not checked.

The integration changes two things L6 users see, compared with what Item 3 shipped: the verdict line names `subset-profile/v2, subset-coverage/v2`, and the coverage line says 70 follow-up sites instead of 85.

WRAP-SPLIT Item 3 (`study-layer-to-codegen`) closed 2026-10-12, certified with follow-ups, in [PR #20](https://github.com/1cFE/sysml-codegen/pull/20). The study layer ships from this repo: `install-commands` installs `run-study`, and `sysml-codegen study` runs the tools in `sysml_codegen.study` (P-007; ADRs 0015–0017). Its spec, design, plan, audit and evidence are retained at `4dfe275f9d90aa2f07824f48349f373df151ef03:.project/active/study-layer-to-codegen/`. fusion-tea's adoption runbook and its kit moved to agentic-mbse `.project/completed/20261012_study-layer-to-codegen/`. Follow-ups are in the backlog's "Study Layer" section.

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

## Research Register Harvest — 2026-10-12

[OWNER] Review the remaining research reports deeply and move consequential information into ADR/product. All 39 reports were read and individually classified. New builder ADRs 0011–0014 capture exact graph identity/projection, exclusive semantic-evidence ownership, the owner-directed removal of unit guessing, and constraint-evaluation semantics. Existing product entries already capture the relevant implemented promises; no duplicate promises were filed. Original authority grades and current assurance limits remain intact.

The reports are archived at Git `aa35f06fb6b3bacfd42c7763a07a4ee4fdaafa57:.project/research/<filename>`; the exact backup, per-file review notes, and validation receipt are under `/tmp/sysml-codegen-research-review-20261012/`. Surviving citations name their immutable archive. Backlog anonymous-key/profile-parity claims now describe current verification questions rather than retired defects; CATF manual-acceptance tracking and the named C19 authoring guidance were corrected.

Verification: 321 focused tests passed with the license loaded; ledger path/surface and Markdown checks passed. Three independent source reviews found no material fidelity issues in the captures. Original mental-alignment drafts and Git index remain unchanged.
