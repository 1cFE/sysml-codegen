# Current Work

**Last Updated**: 2026-07-20 (post-merge close-out)

---

## Active Work

### Post-merge state — CONSTRAINT-LIFECYCLE epic MERGED and CLOSED (2026-07-20)

The constraint-execution lifecycle wave is merged, in the load-bearing order:

- agentic-mbse PR #11 → main `f4ebdce` (merged FIRST)
- sysml-codegen PR #9 → main `936315c`
- teax PR #3 → main `fa0e06a`

All three repos are back on `main` and pulled. Post-merge smoke on codegen main:
**3115 passed / 47 skipped, zero `no live syside license` skip lines** (the skip-line check is
the only valid license proof; pass/skip counts do not discriminate).

Epic archived: `.project/completed/20260720_epic_constraint_execution_lifecycle_remediation.md`
plus all 15 item folders (`20260720_constraint-lifecycle-*`, `20260720_constraint-execution-lifecycle-contract`).
The superseded PR-wave epic is archived alongside
(`20260720_epic_constraint_pr_wave_remediation.md`). Key records, post-archive:

- Release record: `.project/completed/20260720_constraint-lifecycle-composed-proof/release-readiness.md`
- 41/41 register: `.project/completed/20260720_constraint-lifecycle-composed-proof/evidence-coordinate-register.md`
- Ratified authority (unchanged home): `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md`

### docs-lifecycle-sync — IMPLEMENTED + AUDITED on branch `docs-lifecycle-sync` (2026-07-24)

All 5 phases done in an orchestrated run (Opus stages, briefs committed); final audit **Pass
with notes → N1 closed by orchestrator** (no open findings) — see
`.project/active/docs-lifecycle-sync/audit.md` + `inventory.md` (the full claim register).
Highlights: `04-input-resolver.md` → `04-producer-resolution.md` (unified-ladder reference),
doc 24 rewritten, new `30-diagnostic-severity.md` (three stacked fail-closed guards),
REQ-SNAP-21/22 added (matrix 274→276, index reconciled + pre-existing DM/RES drift fixed),
module_kind sweep, R5 honesty note, EXPLAINER_PROMPT re-anchored to merged main. Three
matrix-row candidates filed (producer resolution, catalog 2.0.0, trust manifest) — owner
decision. **Branch awaits owner review/merge; `/_my_close` after.** The original owed-items
list (kept for the record):

1. **Item 4 severity system has ZERO public doc coverage** (Item 6 gap G1 — no stale claim
   existed to amend, so nothing was written). The diagnostics severity contract
   (constraint-facts/v2, fail-closed skew both directions, BLOCK/warning ordering) needs a home
   in `docs/architecture/reference/` near docs 27/28.
2. **Item 5 portability has no verification-matrix row** (Item 6 gap G2; changes index counts —
   recount discipline in memory `verification-matrix-drift-modes`).
3. **Full `docs/architecture/` sweep vs merged main** — the epic landed large late changes
   (v5 snapshot format, written-qualifier fields, catalog schema 2.0.0, producer completeness,
   trust manifest/anchor) after docs 27/28 were last re-projected. Reuse the three-sweep
   inventory METHOD from `completed/20260720_constraint-lifecycle-docs-f1/spec.md`.
4. **`EXPLAINER_PROMPT.md` re-anchoring** (`.project/active/EXPLAINER_PROMPT.md`) — last touched
   pre-epic; Gen-1 banner may be stale vs merged state. Feeds `[V2-HTML-BUILD]` (owner-assigned
   elsewhere).
5. If docs describe override capture, state the def-relative limitation honestly
   (`[NESTED-OCCURRENCE-OVERRIDE]`, probe fixture `tests/fixtures/nested_occurrence_override_probe/`).

### Open decisions — owner rulings recorded 2026-07-24

1. **fusion-tea + stellarator local branches — HOLD [OWNER 2026-07-24].** Stay local until
   the owner says otherwise. Epic evidence pinned at immutable `342cc799`/`c2f10960`; the
   stellarator tip moves from EXTERNAL processes — check `git log origin/<branch>..HEAD`
   before touching.
2. **Local `constraint-exec-epic` branches — DELETED [OWNER 2026-07-24]** in all three merged
   repos (teax needed `-D`: PR #3 was squash-merged; tree verified byte-identical to main
   before deletion).
3. **Stale-baseline class — LEAVE FILED [OWNER 2026-07-24]**, now a proper backlog entry:
   `[STALE-BASELINE-CLASS]` (P3, no assignee).
4. **`[NESTED-OCCURRENCE-OVERRIDE]`** (BACKLOG P2) — still open: schedule the
   occurrence-materialization fix or leave filed. Note the asymmetric defensiveness: the
   constraint path fails loud (strict INV-2 halt), the calc path loses the value silently
   (falls to a manual-required entry point).
5. **Item-10 completeness-check MODULE_OUTPUT exemption — MOOT: already closed in code.**
   Surfaced at the 2026-07-24 ruling pass: audit Major 1 (`b987869`, pre-merge) removed the
   exemption — the check flags name-based key forms regardless of outcome
   (`producer_completeness.py:141`, pinned by
   `test_qualified_channel_tier_leaf_guess_is_flagged`). The "ruling pending" note in the
   archived epic lessons/handoff was stale. The check remains a diagnostic, not a hard
   generation gate — that part is unchanged and by design.
6. **teax remote is SSH** (`git@github.com:rwestwood89/teax.git`) but sessions have no SSH key —
   pulls/pushes need explicit HTTPS URLs. Consider switching the remote to HTTPS. (Still open.)
7. **Archive stragglers in `active/`** — item dirs from already-closed epics remain; need a
   mapping pass first (several are referenced by live BACKLOG entries, e.g.
   `matrix-truth/probes/`, `hygiene-tail/probes/`). (Still open.)

Also ticketed 2026-07-24: `[MATRIX-EPIC-SURFACE-ROWS]` (P3) — the three uncovered lifecycle
surfaces as matrix-row candidates.

### Pre-existing accepted baselines (unchanged)

- `ruff format --check src` fails on 22 files and `mypy src` has 72 errors — accepted baselines;
  the maintained gates are `ruff check` clean + mypy-zero-new.
- Two `-O` failures in `test_expression_compiler` are pre-existing (assert-stripped).

---

## Recently Completed

### 2026-07-20: CONSTRAINT-LIFECYCLE Epic — Constraint Execution Lifecycle Remediation
- All 14 items (0–13) done; composed public proof 41/41 at the pinned set (rerun 22 / compose 19;
  16 negative mutations at boundary; 6/6 byte checks). Sealed artifact thread
  (generate→seal→trusted-load→evaluate→persist→resume/query) demonstrated end-to-end; IFE
  2,301-point + stellarator five-constraint acceptances pass.
- Merged 2026-07-20: agentic-mbse #11 first (enforced by `test_upstream_pins`), then codegen #9,
  then teax #3. Post-merge smoke green on main.
- Epic + 15 item folders archived to `completed/20260720_*`; release-readiness and the 41/41
  evidence-coordinate register live in `20260720_constraint-lifecycle-composed-proof/`.

### 2026-07-19: CONSTRAINT-WAVE epic — superseded
- Items 1 (profile semantics) and 2 (name safety) complete; Items 4 (snapshot portability) and
  6 (seal symlink symmetry) certified. All unfinished work mapped into CONSTRAINT-LIFECYCLE.
- Epic doc archived to `completed/20260720_epic_constraint_pr_wave_remediation.md`.

### 2026-07-18: GAP-CLOSE epic — local scope certified
- Items 2/3/4 certified; Item 1 codegen leg complete. External TEAx leg
  `[GAP-CLOSE-F1-TEAX-NORMALIZATION]` remains open in BACKLOG; epic doc still in `backlog/`.
- Same day: numerical-constraint-profile certified + committed; CONSTRAINT-EXEC code-quality
  remediation cures committed (D5 discharged by the v3 item).

### 2026-07-13: CONSTRAINT-EXEC Epic — Constraint Execution and Design-Space Studies
- All 15 items (0–14) implemented, adversarially reviewed, and audit-certified across four
  repos in one orchestrated run; independent findings audit reproduced every sampled claim
  exactly (`completed/20260713_epic_constraint_execution_audit_independent.md`).
- Modeled `assert constraint` now lowers to Kleene-compiled graph modules + exact-schema report
  aggregator; snapshots carry constraint facts (v3); packages seal with verified-on-load
  contracts; crash-safe study layer (evaluator → store/runner → policy/query/CLI); IFE
  acceptance 2294/2301 + 7 model-favoring boundary rows ([OWNER] ratified); hand viability rule
  deleted. CE-F3 fixed post-run (teax `0d606a4`); CE-F1/F2 registered follow-ons.
- Gates at close: sysml-codegen 2330/23, mypy 76 baseline, ruff clean; agentic-mbse 1401/1;
  teax fully green 262 (pre-existing path bug also fixed, `1b63272`).
- Also 2026-07-13: docs-explainer-refresh audited Certify and pushed to the open PRs.

### 2026-07-10: PUSH-DOWN epic — independently audited and certified
- Expression reconstruction, qualified-name split, hierarchy primitives/models, aggregation
  decomposition moved to agentic-mbse (PRs #8 codegen / #10 agentic-mbse merged).

### 2026-07-08: TRUTH-DEBT Epic
- Archived all six audited items plus the epic ledger to `.project/completed/`.
- Retired the F4 aggregation cutover, resolved multi-hop chain support, matrix test gaps,
  inherited-attr classifier fix, matrix sweep residue, and D3 hygiene tail.
- Pre-PR gates: 2120 passed / 4 skipped / 0 xfailed; ruff src clean; mypy src 97;
  matrix 259 = 258 PASS + 1 UNTESTED.

### 2026-07-06: PIPELINE-TRUTH epic complete; UPSTREAM-FINDINGS + docs-scrub merged
- PIPELINE-TRUTH: all 10 items landed and audited PASS. UPSTREAM-FINDINGS merged (PR #3);
  docs-scrub certified and merged (PR #4).

### 2026-02-17: Phase 5 — E2E Pipeline Validation (5.2) — Checkpoint 5
- 16 conformance tests in `tests/conformance/test_pipeline_e2e.py`
- catf_mfe baseline generated: 42 modules (all CalcUsage), 8 EP groups
- Baseline comparison for all 4 models (solar_battery, catf_mfe, chain_spike, attr_expr_probe)
- REQ-PIPE-01 through REQ-PIPE-06 validated end-to-end
- Checkpoint 5: All 4 models match baselines — refactored pipeline composes correctly
- No production code changes — conformance-only

### 2026-02-17: Phase 5 (partial) — Orchestrator Step Ordering (C19)
- 39 conformance tests in `tests/conformance/test_orchestrator.py`
- Static analysis: `build_pipeline_context()` 10-step DAG ordering verified
- FORMULA removal safety net verified (zero natural overlap in fixtures; constructed overlap exercises logic)
- Registry 4-phase ordering: all aliases target Phase 1 canonical channels (solar_battery + catf_mfe)
- Pipeline invariants (PIPE-01–06) verified across 4 models (solar_battery, catf_mfe, chain_spike, attr_expr_probe)
- REQ-PIPE-07 baseline: 9 generation/ files import from extraction/analysis (Phase 7.6 target)
- No production code changes — conformance-only

### 2026-02-17: Phase 4 — Module Factory + Graph Assembly
- C14 CalcUsage Factory (48 tests), C15 FORMULA Factory (34 tests), C16 Aggregation Factory (32 tests)
- C17 Entry Point Classification (35 tests), C18 Graph Assembly (34 tests)
- Checkpoint 4 baseline comparison: solar_battery, chain_spike, attr_expr_probe match Phase 0 baselines
- All 3 module types verified (CalcUsage + FORMULA + Aggregation)
- Baseline normalization documented: CalcUsage compilability (snapshot serialization boundary), parameter ordering (dict iteration order)
- All design doc amendments applied (06-entry-point-classifier.md, 11-analysis-backtracker.md)

### 2026-02-17: Phase 3 — Analysis Components
- C11a Backtracker Conformance (43 tests), C11b Typed Dispatch Migration (17 tests)
- C12 Input Resolver (26 tests), C13 ParameterGroupDeriver (30 tests), X02 Dual Resolution (20 tests)
- Backtracker fully migrated to typed dispatch: scoped_lookup/sysml_qn_lookup/alias_lookup
- `_compat` dict, `resolve()`, `register()` removed from OutputRegistry
- 14 previously compat-only resolutions (12 catf_mfe + 2 solar_battery) now typed
- D3: Static analysis helpers extracted to `tests/helpers/static_analysis.py`

### 2026-02-17: Phase 2 — Core Infrastructure Spikes
- C08 Output Registry (32 tests), C09 Virtual Binding Rewrite (38 tests), C10 Aggregation Scoping (47 tests)
- 5 NewType wrappers + 3 typed registries implemented
- Phase 2 audit: 6 fixture coverage gaps investigated (C1-C6), 4 closed, 1 partially closed, 1 pending

### 2026-02-17: Phase TRR — Typed Registry Refactor (Design Docs)
- All 8 TRR design doc updates applied (docs 03, 04, 09, 10, 11, 15, 24, 27)
- New design intent doc: `27-typed-registry-refactor.md`

### 2026-02-17: Phase 1 — Foundation & Extraction Components
- C01-C07, all 49 requirement IDs verified

### 2026-02-17: Phase 0 — Test Infrastructure & Baselines
- Extraction snapshots for 6 models, pipeline baselines for 4 models

### 2026-02-10: COST-PATTERN Items 1-4
- Hierarchy-aware codegen: templates, redefinitions, aggregation, pipeline integration

---

## Up Next

1. **Documentation update pass** (see Documentation debt above): severity-system doc home,
   portability matrix row, `docs/architecture/` sweep vs merged main, EXPLAINER_PROMPT
   re-anchoring. Reuse the Item 6 three-sweep inventory method.
2. **CE-F1/F2 follow-ons** (BACKLOG): direct TEAx consumption of codegen's embedded catalog with
   the alternate catalog schema/materializer removed, plus multi-channel CandidateBridge (teax).
3. **pipeline_explainer_v2.html build** (`[V2-HTML-BUILD]`, P2, owner-assigned elsewhere) — after
   EXPLAINER_PROMPT re-anchoring.
4. **Owner decisions** listed under Open decisions (branch delivery/deletion, stale-baseline
   owner, nested-occurrence-override scheduling, Item-10 completeness ruling).

---
