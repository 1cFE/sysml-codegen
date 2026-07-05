# Phase 3 Checkpoint Audit — Action Items

**Audit date**: 2026-02-17
**Auditor**: Claude Opus 4.6 (Phase 3 checkpoint review)
**Scope**: All Phase 3 components (C11a, C11b, C12, C13, X02) + design doc consistency + forward-looking Phase 4 impact

---

## A. Bookkeeping — Complete Before Starting Phase 4

> These are documentation/status accuracy fixes. No code changes.

- [x] **A1** — Update CURRENT_WORK.md to reflect Phase 3 completion (was stuck on Phase 2). *(done 2026-02-17)*
- [x] **A2** — Check the Checkpoint 3 box in IMPLEMENTATION_PLAN.md (already marked `[x]`; test counts verified: 1349 passed, 5 xfailed). *(verified 2026-02-17)*
- [x] **A3** — Verify all Phase 3 component plan.md files have status `DONE` in their §7 Commit sections (all 5 confirmed: C11a, C11b, C12, C13, X02). *(verified 2026-02-17)*

---

## B. Design Doc Amendments — Tier 1 (Apply Before Phase 4)

> These directly affect Phase 4 component understanding. Mismatches between design docs
> and implementation will confuse C14–C18 conformance test design.

- [x] **B1** — `04-input-resolver.md`: Corrected REQ-IR-05 strategy name "DirectRegistryLookup" → "SysMLQNLookup". Also fixed position number (2 → 1, 0-indexed). *(done 2026-02-17)*
  - **Source**: C12 plan Issue #2

- [x] **B2** — `04-input-resolver.md`: Removed `= STANDARD_STRATEGIES` default from `resolve_input()` signature. Updated description to note callers must pass explicitly; no non-aggregation caller identified. *(done 2026-02-17)*
  - **Source**: C12 spike — no non-aggregation caller identified

- [x] **B3** — `04-input-resolver.md`: Added coverage notes to Strategy B (zero exercise for aggregation, backtracker Step 2 more capable) and Strategy D (zero exercise, no-op for current fixtures). *(done 2026-02-17)*
  - **Source**: C12 spike findings (94% hit rate for Strategy A)

- [x] **B4** — `11-analysis-backtracker.md`: Added EXPRESSION binding handling to DFS Tracing Algorithm §3 — creates ENTRY_POINT with warning, no registry lookup. Notes zero natural coverage and expression_binding_probe. *(done 2026-02-17)*
  - **Source**: C11 conformance finding

- [x] **B5** — `11-analysis-backtracker.md`: Added "Compat-Only Resolution Migration" section documenting all 14 resolutions (12 catf_mfe Key_A alias, 2 solar_battery Key_F/Key_E_stripped) and their typed migration fixes. *(done 2026-02-17)*
  - **Source**: C11 conformance + C11b migration

- [x] **B6** — `24-dual-resolution-architecture.md`: Added "Known Asymmetry: REFERENCE Step 2" subsection to Strategy Overlap section. Documents backtracker Step 2 capability gap vs Strategy B normalization. Notes this is not a consistency violation — zero `::` refs in aggregation scope. *(done 2026-02-17)*
  - **Source**: X02 conformance finding #1

---

## C. Design Doc Amendments — Tier 2 (Apply on Next Doc Pass)

> Coverage notes and terminology corrections. No Phase 4 impact.

- [x] **C1** — `01-extraction.md`: Note EXPRESSION binding type has zero coverage in fixture models *(done 2026-02-17)*
  - **Source**: C03 conformance (2026-02-17)

- [x] **C2** — `COMPONENT_CHECKLIST.md`: C03 AC8 — clarify "all binding types" means 4 of 5 (EXPRESSION absent from natural fixtures; covered by expression_binding_probe) *(done 2026-02-17)*
  - **Source**: C03 conformance (2026-02-17)

- [x] **C3** — `16-computed-attributes.md`: Note UNRESOLVABLE has zero coverage in fixture models *(done 2026-02-17)*
  - **Source**: C05 conformance (2026-02-17)

- [x] **C4** — `COMPONENT_CHECKLIST.md`: Consider adding REQ-CA-08 (FORMULA-to-FORMULA limitation) to AC list *(done 2026-02-17 — added REQ-CA-08 to C05 ACs and updated REQ range to REQ-CA-01 through REQ-CA-08)*
  - **Source**: C05 conformance — present in design doc but absent from checklist

- [x] **C5** — `19-ast-dispatch-invariant.md`: Correct "8 files" → "8 multi-type dispatch functions across 5 files" *(done 2026-02-17)*
  - **Source**: C07 conformance (2026-02-17)

- [x] **C6** — `19-ast-dispatch-invariant.md`: Note 5 additional single-type helper functions exist (13 total with `is_instance` on expression types) *(done 2026-02-17)*
  - **Source**: C07 conformance (2026-02-17)

- [x] **C7** — `25-hierarchy-resolver.md`: Update REQ-HR-07 note — alias_agg_probe now exercises positive case. Note `endswith()` false-positive edge case for dotted source_paths *(done 2026-02-17)*
  - **Source**: C5 probe (Phase 2 audit) + C06 conformance

- [x] **C8** — `COMPONENT_CHECKLIST.md`: C06 — update REQ-HR-07 note from "zero positive-case coverage" to "alias_agg_probe exercises positive case" *(already applied — line 131 of checklist has updated language)*
  - **Source**: C5 probe (Phase 2 audit)

- [x] **C9** — `19-ast-dispatch-invariant.md`: Note `_extract_single_binding` is the actual function name (not `extract_binding_info` as listed in plan) *(done 2026-02-17 — corrected function name in dispatch site table)*
  - **Source**: C07 conformance — plan had wrong function name for dispatch site #4

---

## D. Technical Debt — Carry Forward

### D1. Pre-existing Ruff Errors (carried from Phase 2 audit)

- **Issue**: 19 ruff errors across `src/` (7 auto-fixable I001 import sorting, 12 E501/UP037).
  None in Phase 3 modified files.
- [ ] **Action**: Run `uv run ruff check src/ --fix` to resolve auto-fixable errors. Address
  remaining in a cleanup commit.

### D2. Test Helper `registry_compat.py` Usage (NEW)

- **Issue**: `registry_resolve()` and `registry_register()` in `tests/helpers/registry_compat.py`
  are used by 10 test files (unit + integration + 2 conformance). These re-create the cascade
  behavior that was deliberately eliminated from production code. Production code is clean — this
  is test-only.
- **Risk**: Low. Convenience wrappers for pre-existing unit tests. Conformance tests use typed
  lookups directly.
- **Files affected**: `test_backtracker_aggregation.py`, `test_output_registry_construction.py`,
  `test_backtracker_computed_attrs.py`, `test_output_registry.py`, `test_parallel_validation.py`,
  `test_graph_builder_aggregation.py`, `test_graph_builder_computed_attrs.py`,
  `test_output_registry_smoke.py`, `test_output_registry.py` (conformance),
  `test_computed_attributes.py` (conformance)
- [ ] **Action**: Migrate remaining unit tests to typed lookups during Phase 7 cleanup.
  Consider removing `registry_compat.py` once all callers migrated.

### D3. TRR Validation Criteria 5–7 (carried from Phase 2 audit)

- [ ] **E1** — Criterion 5: Systematic REQ cross-reference audit (REQ-XX-NN cited in tests must exist in home doc)
- [ ] **E2** — Criterion 6: Typed identifier consistency fully confirmed for `04-input-resolver.md` (was missing `CanonicalChannel`; B1 addresses this)
- [ ] **E3** — Criterion 7: No orphan requirement references (full sweep not yet done)

---

## E. Phase 4 Risks & Dependencies

### E1. C12 → C16 Integration (graph_builder.py wiring)

- **Status**: `resolve_input()` is proven equivalent to `_resolve_aggregation_input_channel()`
  via regression test (51/51 refs match). However, it is **not yet wired** into `graph_builder.py`.
  The old function (lines 762–873) is still used at 4 call sites.
- **Deferred to**: C16 (Aggregation Module Factory, Phase 4.3)
- **Risk**: Low — the two functions are verified identical. C16 integration is a call-site swap.
- **Dependency**: C14 and C15 can proceed independently. C16 must wire `resolve_input()` before
  the old function can be removed.

### E2. Phase 4 Execution Order

| Component | Can Start | Depends On |
|-----------|-----------|------------|
| C14 — CalcUsage Module Factory | Immediately | C11a/b (done) |
| C15 — FORMULA Module Factory | Immediately | C05 (done), C08 (done) |
| C16 — Aggregation Module Factory | Immediately (but wiring blocked on C12 understanding) | C12 (done), C10 (done) |
| C17 — Entry Point Classification | After C14 (needs factory output) | C14 |
| C18 — Graph Assembly | After C14, C15, C16 (needs all module types) | C14, C15, C16 |

C14 and C15 are independent and can run in parallel. C16 is independent but is the integration
point for `resolve_input()`. C17 depends on C14. C18 depends on all three factories.

### E3. 5 xfailed Tests (inherited attribute misclassification)

- **Location**: `tests/conformance/test_computed_attributes.py`
- **Root cause**: Inherited attrs classified as EXPOSE_COMPUTED instead of FORMULA (Deferred Issue #9)
- **Phase 4 impact**: None. The classifier is upstream and not modified by Phase 4.
- **Fix deferred to**: Phase 7 refactor (supertype chain walk in `_classify_attribute_expression`)

### E4. Old `_resolve_aggregation_input_channel()` Still Exported

- **Location**: `src/sysml_codegen/resolution/graph_builder.py` lines 762–873
- **Status**: Still in `__all__` (line 1420), called at 4 sites within `_build_aggregation_module()`
- **Risk**: None until C16 — the function works correctly. C16 will replace call sites with
  `resolve_input()` and remove the old function.

---

## F. Verification Results

### Test Suite Health (2026-02-17)

| Metric | Value |
|--------|-------|
| Total tests | **1349 passed**, 5 xfailed, 0 failures |
| Conformance tests | 682 passed, 5 xfailed |
| Requirement-tagged (`-m req`) | 651 passed |
| Phase 3 new conformance tests | 136 (C11a: 43, C11b: 17, C12: 26, C13: 30, X02: 20) |

### Production Code Cleanliness

| Check | Result |
|-------|--------|
| `resolve()` in `src/` | Only `Path.resolve()` in CLI — **clean** |
| `_compat` in `src/` | **Zero hits** — fully removed |
| `_key_a_keys` in `src/` | **Zero hits** |
| `register()` convenience on OutputRegistry | **Removed** |
| `derive_key_c()` on OutputRegistry | **Removed** — replaced by `make_scoped_key()` |
| D3 static analysis helpers | **Extracted** to `tests/helpers/static_analysis.py` |

### TRR Design Doc Validation

| Criterion | Result |
|-----------|--------|
| Key_A zero hits outside doc 27 rationale | **PASS** |
| `dict[str, str]` zero OutputRegistry API hits | **PASS** |
| `UnscopedResolutionError` zero active references | **PASS** |
| `resolve()` zero OutputRegistry API hits | **PASS** |
| ScopedKey/CanonicalChannel/SysMLQN consistency (8 docs) | **PASS** |

### Component Verification

| Component | Tests | REQs Verified | Status |
|-----------|-------|---------------|--------|
| C11a — Backtracker Conformance | 43 | REQ-BT-01–08, REQ-DRA-01 | **PASS** |
| C11b — Typed Dispatch Migration | 17 | Static analysis + registry cleanup + dispatch mechanism | **PASS** |
| C12 — Input Resolver | 26 | REQ-IR-01–07, REQ-DRA-02, REQ-DRA-04 | **PASS** |
| C13 — ParameterGroupDeriver | 30 | REQ-PGD-01–07 | **PASS** |
| X02 — Dual Resolution Consistency | 20 | REQ-DRA-03–05 | **PASS** |

---

## Progress Tracking

| Date | Items Completed | By |
|------|----------------|----|
| 2026-02-17 | Audit performed, action items written | Phase 3 checkpoint review |
| 2026-02-17 | A1 — CURRENT_WORK.md updated to Phase 3 complete | Phase 3 checkpoint review |
| 2026-02-17 | A2, A3 — Checkpoint 3 verified, all 5 plan.md files confirmed DONE | Phase 3 checkpoint review |
| 2026-02-17 | B1–B3 — `04-input-resolver.md`: REQ-IR-05 strategy name fix, STANDARD_STRATEGIES default removed, Strategy B/D coverage notes added | Phase 3 checkpoint review |
| 2026-02-17 | B4–B5 — `11-analysis-backtracker.md`: EXPRESSION binding handling documented, compat-only migration section added | Phase 3 checkpoint review |
| 2026-02-17 | B6 — `24-dual-resolution-architecture.md`: REFERENCE Step 2 asymmetry documented | Phase 3 checkpoint review |
| 2026-02-17 | C1–C9 — Tier 2 doc amendments applied: EXPRESSION zero-coverage note (01), binding type clarification (checklist), UNRESOLVABLE zero-coverage note (16), REQ-CA-08 added (checklist), dispatch site count corrected (19), single-type helpers noted (19), alias detection coverage+edge case (25), C06 REQ-HR-07 verified (checklist), function name corrected (19) | Tier 2 doc pass |
