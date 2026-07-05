# Current Work

**Last Updated**: 2026-02-17

---

## Active Work

### UPSTREAM-FINDINGS Item 1: Baseline Repair & Silent-Failure Diagnostics

**Status**: **Audited CONDITIONAL** (2026-07-05, commit 3c42dd1) — implementation certifiable; clears
to PASS on a 3-item fix list (see `audit.md`). All five phases complete and committed.
**Epic**: `.project/backlog/epic_upstream_findings.md`
**Audit**: `.project/active/baseline-diagnostics/audit.md`
**Plan**: `.project/active/baseline-diagnostics/plan.md`

Done: D1 sort (`entry_point_groups` name-sorted) + I1 test; D2 constraint-drop diagnostic
(`report_dropped_constraints`, REQ-EXT-09); D3 zero-output fail-fast (REQ-EXT-08); D4 EXPOSE_PURE
wording reword (REQ-CA-09 test deferred to Item 8 — shape-A fires malformed-refs, not the reworded
warnings); dead-code deletion; Phase 3 re-capture (solar_battery ×3 + catf_mfe ×2, ordering-only) +
two stale-registry corrections; Phase 4 docs + verification matrix.

**To clear CONDITIONAL → PASS:** (1) reconfirm suite/ruff/mypy green on 3c42dd1 — auditor was
harness-blocked from running them; (2) flip verification-matrix REQ-BASE-05 from "PENDING RE-CAPTURE"
to PASS (the re-capture is already committed); (3) optional — the Item-2 `snapshot-generation/design-review.md`
was bundled into the Item-1 commit (harmless doc, scope-hygiene note).

### UPSTREAM-FINDINGS Item 2: Snapshot-Driven Generation (SC-9 + SC-10)

**Status**: **Audited CONDITIONAL** (2026-07-05, commit b9f9b82) — substance certified;
clears to PASS on one item: re-run suite/mypy/ruff (auditor was harness-blocked from `uv run`).
**Epic**: `.project/backlog/epic_upstream_findings.md`
**Spec / Design / Plan**: `.project/active/snapshot-generation/{spec,design,plan}.md`
**Audit**: `.project/active/snapshot-generation/audit.md`

Supported `--from-snapshot` generation path + `snapshot` capture command, so
generation/debug/CI decouple from the syside license (expires 2026-08-06).
Delivered: promoted `sysml_codegen.snapshot` package; format versioning +
provenance/freshness guards; `compilation_results` serialized (SC-10 — CalcUsage
auto-impl survives); `source_file` relativize-at-capture / lexical-re-absolutize-at-load.
**SC-1 proven live**: `generate --from-snapshot` byte-identical to
`generate --models` incl. a symlinked run (empty tree diff). **SC-10 proven**:
chain_spike stencils auto-implement from the committed snapshot. Reference doc:
`docs/architecture/reference/27-snapshot-generation.md` (REQ-SNAP-08..19).
One deviation: completed Item 1's deterministic entry-point sort by also sorting
parameters within each group (`graph_builder.py:375`) — required for SC-1 byte-identity.
Suite 1837 passed; mypy 109 / ruff 21 (== baseline, recorded — not re-run by auditor).
**Audit findings (all low-severity, non-blocking):** deviation #2 undercount (4 new
`# type: ignore`, not two — all scoped/sound); dead `out` var in a test; plan Phase 3/4/5
checkboxes unfilled though deliverables landed. See `audit.md`.

### UPSTREAM-FINDINGS Item 3: Return-Style & Bare-Parameter Extraction (SC-2)

**Status**: **Implemented** (2026-07-05, uncommitted — orchestrator commits). All 4
plan phases complete; ready for `/_my_audit`.
**Epic**: `.project/backlog/epic_upstream_findings.md`
**Spec / Design / Plan**: `.project/active/return-style-extraction/{spec,design,plan}.md`

Relaxed the calc-def member filter to a shared `_is_parameter_member` predicate at
both passes (`extractor.py`): named `return` and bare `in` (direction-carrying
ReferenceUsage) now extract; named inline `return` auto-implements. Anonymous
`return` raises the new V8 diagnostic before V7 (V7 reworded — no more "not yet
extracted (Item 3)"). New `return_styles` fixture (4 styles + design part) +
committed snapshot + `anonymous_return` live fixture; `test_return_style_extraction.py`
(11 tests, live + offline). Docs lockstep: REQ-EXT-10/11/12 in 01-extraction +
verification-matrix, V7/V8 rows in modeling-assumptions. Body-assignment capture
deferred (BACKLOG.md, P3). **A-2 stencil fix applied in `~/1cfe/agentic-mbse`
(uncommitted — report to orchestrator).**

**Phase 0 deviation (key finding):** the design's primary V8 rule ("direction-Out +
empty `sanitize_name`") was REFUTED live — an anonymous `return` gets a
syside-synthesized name `result` (non-empty), so V8 keys off the probe-evidenced B4
fallback instead: an owned `ReturnParameterMembership` whose `declared_name` is empty.
Plain `out attribute` calc defs carry no such membership → existing fixtures safe.

**I1 gate:** re-capture diff was `captured_at`-timestamp-only across all 10 existing
snapshots (zero semantic change); baselines byte-identical. Reverted the
timestamp-only rewrites — only `return_styles` + `anonymous_return` added.
Suite 1857 passed / 4 skipped / 5 xfailed; mypy 109, ruff 21 (== baseline).

### UPSTREAM-FINDINGS Item 4: Part-Usage Type Indexing (SC-3)

**Status**: Spec in progress
**Epic**: `.project/backlog/epic_upstream_findings.md`
**Spec**: `.project/active/type-indexing/spec.md`

Retyped part usages (`part :>> x : Subtype`) instantiate their subtype's template
calcs instead of silently dropping them. Fix the first-type bug in two places
(`usage_extractor.py` `_build_part_usage_index`, `hierarchy_resolver.py`
`usage_type_map`): index/resolve by owned FeatureTyping target plus every
user-model PartDef in `usage.types`, never by list position. Virtual-QN collision
tiebreak/warning; retyping fixture + snapshot + conformance tests; 4 pipeline
baselines byte-identical.

### REFACTOR: Incremental Pipeline Refactor

**Status**: In Progress (Phases 0–4 complete)
**Plan**: `.project/concepts/refactor-design-intent/IMPLEMENTATION_PLAN.md`
**Checklist**: `.project/concepts/refactor-design-intent/COMPONENT_CHECKLIST.md`
**Branch**: `cost-pattern-refactor`

**Objective**: Bottom-up, test-first refactor of the pipeline. Lock down every component with conformance tests using real data, then restructure the codebase to match target architecture.

**Completed Phases**:
- [x] Phase 0: Test Infrastructure & Baselines (70 tests, 6 extraction snapshots, 4 pipeline baselines)
- [x] Phase 1: Foundation & Extraction Components (C01-C07, 311 conformance tests)
- [x] Phase TRR: Typed Registry Refactor design doc updates (8 docs updated)
- [x] Phase 2: Core Infrastructure Spikes (C08-C10, 117 conformance tests)
- [x] Phase 3: Analysis Components (C11a/b, C12, C13, X02, 136 conformance tests)
- [x] Phase 4: Module Factory + Graph Assembly (C14-C18, 183 conformance tests, Checkpoint 4 passed)
- [x] Phase 5: Orchestrator Integration (C19 + 5.2, 55 conformance tests, Checkpoint 5 passed)

**Current Phase**: Phase 6 — Generation Layer Validation (C20-C25, X01)

**Test Suite**: 1587 tests passing (920 conformance + 667 existing), 5 xfailed

**Key Decisions**:
- Typed Registry Refactor complete — 3 typed registries, zero `_compat`, zero `resolve()`
- Backtracker typed dispatch (C11b) migrated all 14 compat-only resolutions to typed lookups
- Input Resolver (C12) proven equivalent to old function; graph_builder integration deferred to C16

**Blockers**: None

**Audit**: Phase 3 audit complete — see `.project/concepts/refactor-design-intent/PHASE3_AUDIT_ACTIONS.md`

---

## Recently Completed

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

1. Phase 6: Generation Layer Validation (C20-C25, X01)
2. Phase 7: Structural Refactoring & Dead Code Removal

---
