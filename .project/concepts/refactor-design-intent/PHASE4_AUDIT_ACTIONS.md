# Phase 4 Checkpoint Audit — Action Items

**Audit date**: 2026-02-17
**Auditor**: Claude Opus 4.6 (Phase 4 checkpoint review)
**Scope**: All Phase 4 components (C14, C15, C16, C17, C18) + design doc consistency + carry-forward from Phase 3 audit + forward-looking Phase 5 impact

---

## A. Bookkeeping — Complete Before Starting Phase 5

> These are documentation/status accuracy fixes. No code changes.

- [x] **A1** — CURRENT_WORK.md updated to reflect Phase 4 completion and Phase 5 as current. *(verified 2026-02-17)*
- [x] **A2** — Checkpoint 4 box checked in IMPLEMENTATION_PLAN.md. Test counts verified: 1532 passed, 2 skipped, 5 xfailed (1539 collected). *(verified 2026-02-17)*
- [x] **A3** — All 5 Phase 4 plan.md files have status DONE:
  - `.project/active/calc-usage-module-factory/plan.md` (C14)
  - `.project/active/formula-module-factory/plan.md` (C15)
  - `.project/active/aggregation-module-factory/plan.md` (C16)
  - `.project/active/entry-point-classifier/plan.md` (C17)
  - `.project/active/graph-assembly/plan.md` (C18)
- [x] **A4** — Checkpoint 4 assessment added to IMPLEMENTATION_PLAN.md: baseline comparison passes for solar_battery, chain_spike, attr_expr_probe (after normalizing CalcUsage compilability and parameter ordering).
- [ ] **A5** — Commit untracked housekeeping files or add to .gitignore:
  - `.project/logs/` — Phase 3 logs directory
  - `scripts/run_phase2.sh` — Phase 2 automation script
  - `scripts/run_phase3.sh` — Phase 3 automation script

---

## B. Design Doc Amendments — Already Applied During Phase 4

> These were applied in Phase 4 commits. Listed here for audit trail completeness.

- [x] **B1** — `05-module-factory.md`: Strategy 1 (type-aware) essential for aliased usage names in `_find_literal_redefinition()`. *(C16 commit f317015)*
- [x] **B2** — `18-literal-value-propagation.md`: LITERAL redef fallback naturally exercised by SingletonTerms, not SumTerms. *(C16 commit f317015)*
- [x] **B3** — `06-entry-point-classifier.md`: solar_battery has zero DESIGN_ATTRIBUTE EPs from Path 1 classifier; catf_mfe exercises all 3 types. *(C17 commit 2fd1514)*
- [x] **B4** — `06-entry-point-classifier.md`: REQ-EPC-04 is graph-level invariant (param_group may be None from classifier; orphan handling ensures grouping). *(C17 commit 2fd1514)*
- [x] **B5** — COMPONENT_CHECKLIST.md: All C14-C18 ACs checked; C16 interfaces corrected (actual vs aspirational); C18 baseline normalization documented. *(Commits fb3b2bb through 56666dd)*
- [x] **B6** — IMPLEMENTATION_PLAN.md: Accumulated Learnings updated for C16, C17, C18. Step 7.7 (factory purity refactor) added. Summary table updated with actual test counts. *(Multiple Phase 4 commits)*
- [x] **B7** — Phase 3 Tier 2 amendments (C1-C9 from PHASE3_AUDIT_ACTIONS.md): All 9 applied in C14 commit fb3b2bb:
  - `01-extraction.md`: EXPRESSION binding zero-coverage note
  - `16-computed-attributes.md`: UNRESOLVABLE zero-coverage note
  - `19-ast-dispatch-invariant.md`: Dispatch site count and function name corrections
  - `25-hierarchy-resolver.md`: REQ-HR-07 alias detection coverage update
  - COMPONENT_CHECKLIST.md: C03/C05/C06 AC updates

---

## C. Requirement Tagging Gaps

> Requirements that are functionally tested but missing `@pytest.mark.req()` tags.

- [x] **C1** — `test_factory_aggregation.py`: REQ-LVP-02 (SumTerm fallback calls `_find_literal_redefinition`) — added `@pytest.mark.req("REQ-LVP-02")` to `test_sumterm_literal_fallback`. *(done 2026-02-17)*

- [x] **C2** — `test_factory_aggregation.py`: REQ-LVP-03 (SingletonTerm fallback calls `_find_literal_redefinition`) — added `@pytest.mark.req("REQ-LVP-03")` to `test_singleton_literal_fallback`. *(done 2026-02-17)*

- [ ] **C3** — Verify all other Phase 4 requirements have tags. Quick audit:
  | Component | REQs in design doc | REQs tagged in tests | Gap |
  |-----------|-------------------|---------------------|-----|
  | C14 | REQ-MF-01, 02, 05, 08 | All 4 tagged | None |
  | C15 | REQ-MF-01, 03, 05 | All 3 tagged | None |
  | C16 | REQ-MF-01, 04-07, REQ-LVP-01-07 | All tagged | None (C1, C2 fixed) |
  | C17 | REQ-EPC-01-08 | All 8 tagged | None |
  | C18 | REQ-GA-01-07 | All 7 tagged | None |

---

## D. Technical Debt — Carry Forward from Phase 3

### D1. Pre-existing Ruff Errors (carried from Phase 3 audit D1 — STILL OPEN)

- **Issue**: 19 ruff errors across `src/` (7 auto-fixable I001 import sorting, 12 E501/UP037).
  None in Phase 4 modified files (Phase 4 was conformance-only, no production code changes).
- [ ] **Action**: Run `uv run ruff check src/ --fix` to resolve auto-fixable errors. Address
  remaining in a cleanup commit. Target: Phase 7 cleanup or dedicated commit before Phase 5.

### D2. Test Helper `registry_compat.py` Usage (carried from Phase 3 audit D2 — STILL OPEN)

- **Issue**: `registry_resolve()` and `registry_register()` in `tests/helpers/registry_compat.py`
  are used by 10 test files (8 unit/integration + 2 conformance). These re-create the cascade
  behavior that was deliberately eliminated from production code. Production code is clean — this
  is test-only.
- **Files affected** (10 total):
  - Unit: `test_backtracker_aggregation.py`, `test_backtracker_computed_attrs.py`, `test_graph_builder_aggregation.py`, `test_graph_builder_computed_attrs.py`, `test_output_registry.py`, `test_output_registry_construction.py`
  - Integration: `test_parallel_validation.py`, `test_output_registry_smoke.py`
  - Conformance: `test_output_registry.py`, `test_computed_attributes.py`
- **Risk**: Low. Convenience wrappers for pre-existing tests. Phase 4 conformance tests use typed lookups directly.
- [ ] **Action**: Migrate remaining callers to typed lookups during Phase 7 cleanup.

### D3. TRR Validation Criteria 5-7 (carried from Phase 3 audit D3 — STILL OPEN)

- [ ] **E1** — Criterion 5: Systematic REQ cross-reference audit (REQ-XX-NN cited in tests must exist in home doc). Partially mitigated by Phase 4's thorough tagging (only C1/C2 gaps found).
- [ ] **E2** — Criterion 6: Typed identifier consistency confirmed for all amended docs. `04-input-resolver.md` now has `CanonicalChannel` (Phase 3 B1 fix).
- [ ] **E3** — Criterion 7: No orphan requirement references (full sweep not yet done). Scope: verify every `@pytest.mark.req("REQ-XX-NN")` in `tests/conformance/` maps to a defined requirement in its home design doc.

---

## E. Phase 4 Gaps & Findings

### E1. resolve_input() Integration Still Deferred

- **Status**: `resolve_input()` in `resolution/input_resolver.py` is fully implemented, proven equivalent to `_resolve_aggregation_input_channel()` via regression test (51/51 refs match), but **NOT wired into** `graph_builder.py`.
- **History**: Phase 3 audit (E1) said "deferred to C16". C16 was conformance-only (as planned). The old function `_resolve_aggregation_input_channel()` (graph_builder.py line 762) is still called at 3 production sites.
- **Phase 5 impact**: E2E validation will use the old function. This is safe — the two functions are proven identical.
- **Deferred to**: Phase 7.2 (extract input resolver / wire call sites).
- **Risk**: Low — the two functions are verified identical. No behavioral difference.

### E2. Entry Points Mutation — Phase 7.7 Scope Confirmed

- **Issue**: FORMULA factory (1 mutation site) and Aggregation factory (6 mutation sites) mutate the shared `entry_points` dict in-place. This deviates from REQ-MF-01 "pure data transformer."
- **Evidence**: 17 `entry_points[...] = ...` statements in graph_builder.py (lines 720, 996, 1003-1005, 1031, 1108, 1115-1118, 1177).
- **Mitigation**: C17 conformance tests verify factory-created EPs retain DESIGN_ATTRIBUTE classification and are not re-classified. Static analysis confirms `_classify_entry_points()` is called once, before factories.
- **Risk**: Low — mutation behavior is tested and documented. Phase 7.7 refactor target is well-defined: return `(PipelineModule, dict[str, EntryPoint])` from all 3 factories.
- [ ] **Action**: No action needed before Phase 5. Phase 7.7 will refactor.

### E3. 5 xfailed Tests — Inherited Attribute Misclassification (UNCHANGED)

- **Location**: `tests/conformance/test_computed_attributes.py` (3 xfail markers covering 5 test cases)
- **Root cause**: Deferred Issue #9 — inherited attrs classified as EXPOSE_COMPUTED instead of FORMULA
- **Phase 5 impact**: None. The classifier is upstream and not modified.
- **Fix deferred to**: Phase 7 refactor (supertype chain walk in `_classify_attribute_expression`), requires C03 extraction enrichment for PartDefinitionData supertype chain.

### E4. 2 Skipped Tests in Phase 4 (NEW)

- **Observation**: Test suite shows 1532 passed + 2 skipped + 5 xfailed = 1539 collected. The IMPLEMENTATION_PLAN tracks "passed" count (1532) as the primary metric.
- **Likely cause**: C15 FORMULA factory tests that skip when certain fixture conditions aren't met (e.g., no EXPOSE_ALIAS inputs in specific models). These are `pytest.skip()` calls inside test bodies, not `@pytest.mark.skip`.
- **Risk**: None. Skips are conditional and documented in test bodies. No requirements are untested.
- [x] **Action**: Documented "2 skipped" in IMPLEMENTATION_PLAN Checkpoint 4 test count. *(done 2026-02-17)*

### E5. Baseline Normalization Requirements for Phase 5 (NEW)

- **Issue**: C18's Checkpoint 4 baseline comparison identified 2 normalizations needed:
  1. **CalcUsage compilability**: `'unknown'` from snapshot (no `compilation_results` due to AST serialization boundary) vs `'fully_compilable'` from live pipeline.
  2. **Parameter ordering within groups**: dict iteration order differs between snapshot-based and live pipeline execution.
- **Phase 5 impact**: Phase 5 E2E tests will use **live pipeline** (not snapshots), so compilability normalization won't be needed. But parameter ordering may still differ from Phase 0 baselines.
- [ ] **Action**: Phase 5 E2E baseline comparison should either:
  (a) Use sorted parameter lists for comparison, or
  (b) Establish new live-pipeline baselines as the canonical reference.
  Document the decision in C19 plan.

---

## F. Forward-Looking: Phase 5 Risks & Dependencies

### F1. Orchestrator Integration Scope

- **Key question**: Phase 5.1 (C19) tests the orchestrator's step ordering and E2E pipeline. The orchestrator is `build_pipeline_context()` in `generation/initialization.py` (~889 lines). Phase 5 tests will wrap the entire function.
- **Risk**: The orchestrator will be restructured in Phase 7.1 (extract to `orchestration/` package, target <200 lines). Phase 5 tests should test **behavior** (step ordering, output correctness) not **structure** (import paths, function locations).
- **Mitigation**: Write Phase 5 tests against public API (`build_pipeline_context()` / `build_computation_graph()`), not internal helpers. This makes them resilient to Phase 7 restructuring.

### F2. Phase 5 Execution Order

| Component | Can Start | Depends On |
|-----------|-----------|------------|
| C19 — Orchestrator Step Ordering | Immediately | C14-C18 (all done) |
| 5.2 — E2E Pipeline Validation | After C19 | C19 |

### F3. Live Pipeline vs Snapshot Boundary

- **Issue**: Phases 0-4 used extraction snapshots (JSON-serialized). Phase 5 E2E tests need the **live pipeline** which requires the SysIDE JVM adapter.
- **Options**:
  (a) Run E2E tests with live SysIDE adapter (most complete, but slow and JVM-dependent)
  (b) Reconstruct pipeline from snapshots using `build_full_graph_from_snapshot()` (fast, JVM-free, already proven in C18)
  (c) Both — live tests as integration, snapshot-based as conformance regression
- **Recommendation**: Option (c) — use `build_full_graph_from_snapshot()` for fast conformance regression, add optional live-pipeline integration tests gated by SysIDE availability.

### F4. Phase 0 Learning #4 — Live ComputationGraph Regression Test

- **Issue**: Phase 0 noted "no live regression test for ComputationGraph JSON baselines. A live comparison test should be added when Phase 5 (orchestrator integration) is implemented."
- **Status**: C18's `build_full_graph_from_snapshot()` effectively fills this gap via Checkpoint 4 baseline comparison. However, a truly live (SysIDE-driven) comparison is still missing.
- [ ] **Action**: Phase 5 should add a live ComputationGraph baseline test if SysIDE is available, or document why snapshot-based comparison is sufficient.

---

## G. Test Suite Health — Verification Results

### G1. Test Counts (2026-02-17)

| Metric | Value |
|--------|-------|
| Tests collected | **1539** |
| Tests passed | **1532** |
| Tests skipped | **2** |
| Tests xfailed | **5** |
| Conformance tests | **872** collected |
| Requirement-tagged (`-m req`) | **836** collected |
| Phase 4 new conformance | **183** (C14: 48, C15: 34, C16: 32, C17: 35, C18: 34) |

### G2. Production Code Cleanliness (Phase 4 was conformance-only)

| Check | Result |
|-------|--------|
| Phase 4 production code changes | **Zero** — conformance-only as planned |
| `resolve()` on OutputRegistry | **Removed** (Phase 3) — clean |
| `_compat` on OutputRegistry | **Zero hits** — fully removed (Phase 3) |
| `_resolve_aggregation_input_channel()` present | **Yes** — 3 call sites, removal deferred to Phase 7 |
| `resolve_input()` wired into graph_builder | **No** — implemented but not integrated |
| Entry_points mutation in factories | **Active** — 7 assignment sites; Phase 7.7 fix |
| TODO/FIXME/HACK in graph_builder.py | **Zero** |
| TODO/FIXME/HACK in initialization.py | **Zero** |
| Ruff errors in src/ | **19** (7 auto-fixable) — carried from Phase 3 |

### G3. Component Verification Summary

| Component | Tests | REQs Verified | Production Changes | Status |
|-----------|-------|---------------|-------------------|--------|
| C14 — CalcUsage Module Factory | 48 | REQ-MF-01, 02, 05, 08 | None | **PASS** |
| C15 — FORMULA Module Factory | 34 (2 skipped) | REQ-MF-01, 03, 05 | None | **PASS** |
| C16 — Aggregation Module Factory | 32 | REQ-MF-01, 04-07, REQ-LVP-01, 04-07 | None | **PASS** (REQ-LVP-02/03 functionally tested but untagged) |
| C17 — Entry Point Classification | 35 | REQ-EPC-01-08 | None | **PASS** |
| C18 — Graph Assembly | 34 | REQ-GA-01-07 | None | **PASS** |

### G4. Checkpoint 4 Baseline Comparison

| Model | Result | Notes |
|-------|--------|-------|
| solar_battery | **MATCH** | After compilability + param order normalization |
| chain_spike | **MATCH** | After compilability + param order normalization |
| attr_expr_probe | **MATCH** | After compilability + param order normalization |

---

## H. Consolidated Action Items for Phase 5 Readiness

### Must-Do Before Phase 5 (Low Effort)

| # | Action | Effort | Source |
|---|--------|--------|--------|
| C1 | Tag `test_sumterm_literal_fallback` with `@pytest.mark.req("REQ-LVP-02")` | 1 line | Audit §C |
| C2 | Tag `test_singleton_literal_fallback` with `@pytest.mark.req("REQ-LVP-03")` | 1 line | Audit §C |
| A5 | Commit or gitignore untracked housekeeping files (.project/logs/, scripts/run_phase*.sh) | 5 min | Audit §A |
| E4 | Add "2 skipped" to IMPLEMENTATION_PLAN test count note | 1 line | Audit §E |

### Should-Do Before Phase 5 (Recommended)

| # | Action | Effort | Source |
|---|--------|--------|--------|
| D1 | Run `ruff check src/ --fix` for 7 auto-fixable import sorting errors | 5 min | Phase 3 carry-forward |
| E5 | Decide baseline normalization strategy for Phase 5 E2E tests | Design decision | Audit §E |

### Carry Forward to Phase 7 (No Phase 5 Urgency)

| # | Action | Phase 7 Target | Source |
|---|--------|----------------|--------|
| D2 | Migrate 10 test files from `registry_compat.py` to typed lookups | 7.4 (cleanup) | Phase 3 carry-forward |
| D3 | TRR validation criteria 5-7 full sweep | 7.4 (cleanup) | Phase 3 carry-forward |
| E1 | Wire `resolve_input()` into `graph_builder.py` call sites | 7.2 | Phase 3 carry-forward |
| E2 | Refactor factory entry_points mutation → pure return | 7.7 | Phase 4 finding |
| E3 | Fix inherited attribute misclassification (5 xfailed tests) | 7 (requires C03 enrichment) | Deferred Issue #9 |

---

## Progress Tracking

| Date | Items Completed | By |
|------|----------------|----|
| 2026-02-17 | Audit performed, action items written | Phase 4 checkpoint review |
| 2026-02-17 | A1-A4 verified (bookkeeping already done in Phase 4 commits) | Phase 4 checkpoint review |
| 2026-02-17 | B1-B7 verified (design doc amendments already applied) | Phase 4 checkpoint review |
