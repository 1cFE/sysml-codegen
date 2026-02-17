# Current Work

**Last Updated**: 2026-02-17

---

## Active Work

### REFACTOR: Incremental Pipeline Refactor

**Status**: In Progress (Phases 0–3 complete)
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

**Current Phase**: Phase 4 — Module Factory + Graph Assembly (C14-C18)

**Next Component**: C14 — CalcUsage Module Factory. Builds PipelineModules from BacktrackingResult + real calc defs. Design specified in doc 05.

**Test Suite**: 1349 tests passing (682 conformance + 667 existing), 5 xfailed

**Key Decisions**:
- Typed Registry Refactor complete — 3 typed registries, zero `_compat`, zero `resolve()`
- Backtracker typed dispatch (C11b) migrated all 14 compat-only resolutions to typed lookups
- Input Resolver (C12) proven equivalent to old function; graph_builder integration deferred to C16

**Blockers**: None

**Audit**: Phase 3 audit complete — see `.project/concepts/refactor-design-intent/PHASE3_AUDIT_ACTIONS.md`

---

## Recently Completed

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

1. Phase 4: C14 CalcUsage Module Factory — build modules from BacktrackingResult
2. Phase 4: C15 FORMULA Module Factory — build FORMULA modules from ComputedAttributeData
3. Phase 4: C16 Aggregation Module Factory — wire resolve_input() into graph_builder
4. Phase 4: C17 Entry Point Classification, C18 Graph Assembly
5. Apply Tier 1 design doc amendments (6 items — see PHASE3_AUDIT_ACTIONS.md §B)

---
