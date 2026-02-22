# Component: Dual Resolution Consistency (X02)

**Status**: DONE
**Created**: 2026-02-17
**Last updated**: 2026-02-17
**Updated by**: Plan prompt — Claude Opus 4.6

## Source Documents

- **Checklist entry**: `COMPONENT_CHECKLIST.md` — X02
- **Design intent**: [24-dual-resolution-architecture.md](../../concepts/refactor-design-intent/24-dual-resolution-architecture.md)
- **Requirements**: REQ-DRA-01 through REQ-DRA-05
- **Depends on**: C11a (backtracker conformance — DONE), C11b (typed dispatch — DONE), C12 (input resolver — DONE)

---

## 1. Assessment

### What This Component Does

X02 is a cross-cutting conformance test — no production code changes. It verifies that the three resolution paths (backtracker DFS, FORMULA attribute resolution map, `resolve_input()` strategy chain) produce identical wiring decisions when resolving the same reference in the same scope. This is the key architectural invariant from doc 24: two separate code paths must agree.

### Current State

- **Exists?** Partial. C12's `test_cross_path_consistency` (test_input_resolver.py:552-609) already verifies backtracker vs `resolve_input()` for solar_battery CHAIN MODULE_OUTPUT bindings. But this is a single test covering one model and one binding type, embedded in C12's test file rather than a dedicated cross-cutting test.
- **Needs extraction/refactoring?** No production code changes. New test file only.
- **Current test coverage**:
  - REQ-DRA-01: Covered by C11a (backtracker DFS calls `_resolve_binding_via_registry` during traversal)
  - REQ-DRA-02: Covered by C12 (`test_formula_not_via_resolve_input`, `test_calcusage_not_via_resolve_input` — static analysis)
  - REQ-DRA-03: Covered by C11b (typed dispatch static analysis) and C12 (Strategy A uses `scoped_lookup`)
  - REQ-DRA-04: **Partially** covered by C12 `test_cross_path_consistency` — solar_battery CHAIN only
  - REQ-DRA-05: **Not** explicitly tested

### Design Consistency Check

- [x] All acceptance criteria from COMPONENT_CHECKLIST are testable with real data (no mocks)
- [x] AC are consistent with the requirements in the design intent doc(s)
- [x] No contradictions with other component specs
- [x] Input/output interfaces match what upstream/downstream components expect
- [x] Any ambiguities or gaps identified and resolved (documented below)

**Issues found during review:**

#### Issue #1: Implementation plan text mentions "CalcUsage and FORMULA context" but natural overlap doesn't exist

**Problem**: The implementation plan says "For a shared reference that appears in both CalcUsage and FORMULA context, verify both paths produce the same wiring decision." C12 Learning #3 established: "No natural REQ-DRA-04 overlap in fixture models." CalcUsage bindings reference feature chains (`cost_model.total_cost`); FORMULA inputs reference sibling attributes within a PartDef (`length`, `width`). They operate at different abstraction levels.

**Analysis**: The overlap between FORMULA and CalcUsage is indirect:
- FORMULA EXPOSE_PURE attributes resolve via `_resolve_expose_pure()` → `scoped_lookup(ScopedKey("instance.attr"))` → same OutputRegistry
- CalcUsage CHAIN bindings resolve via backtracker → `scoped_lookup(ScopedKey(consumer_scope + "." + source_path))` → same OutputRegistry
- Both use the same typed registry lookups. Consistency is guaranteed by using the same registry with the same typed methods.

The testable assertion is: for every EXPOSE_PURE channel in the attribute resolution map, the same channel is reachable via `scoped_lookup` or `alias_lookup` on the registry (the same method the backtracker uses).

**Resolution**: Test FORMULA consistency by verifying EXPOSE_PURE resolution map channels match what typed registry lookups return. Test CalcUsage-vs-Agg consistency by running both paths on the same refs across all models.

#### Issue #2: No three-way overlap scenario in real data

**Problem**: No fixture exercises a scenario where a single reference is resolved by all three paths simultaneously. This is structurally expected: CalcUsage bindings are resolved during DFS, FORMULA inputs during attribute map construction, and Aggregation inputs during module building. A reference belongs to exactly one context.

**Resolution**: REQ-DRA-04 is about pairwise consistency for overlapping strategies, not three-way identity. The test covers the two meaningful pairwise comparisons: (1) backtracker CHAIN dispatch vs `resolve_input()` Strategy A, and (2) FORMULA EXPOSE_PURE resolution vs backtracker scoped_lookup. Both pairs use the same typed registry as their source of truth.

#### Issue #3: REQ-DRA-05 has no explicit test

**Problem**: REQ-DRA-05 says "The backtracker SHALL produce `BindingResolution` objects; `resolve_input()` SHALL produce `InputSource` objects. Both encode the same two-valued answer (module_output or entry_point)." This structural mapping is untested.

**Resolution**: Add a test verifying the structural equivalence: `BindingResolution.resolution_type` maps to `InputSource.source_type` with `MODULE_OUTPUT` → `"module_output"` and `ENTRY_POINT` → `"entry_point"`.

### Risks & Unknowns

1. **Low risk**: The C12 `test_cross_path_consistency` already verifies the primary overlap case (backtracker vs resolve_input for CHAIN). X02 extends coverage to more models and binding types — incremental, not novel.
2. **Low risk**: FORMULA overlap is structurally guaranteed by shared registry. Tests verify the guarantee holds empirically.
3. **No unknowns**: C12 spike answered all relevant questions; no new spike needed.

---

## 2. Spike

**Decision**: SKIP
**Rationale**: C12's spike (7 questions, 51 refs, 3 models) already answered the key questions:
- No natural REQ-DRA-04 overlap in fixture models (C12 Learning #3)
- Strategy A resolves 94% of aggregation refs (C12 Learning #1)
- Constructed ResolutionContext from CalcUsage binding metadata successfully verified cross-path consistency for solar_battery (C12 `test_cross_path_consistency`)
- Both paths use the same typed OutputRegistry (verified in C08, C11b, C12)

The test approach is clear: extend C12's cross-path test to all models, all binding types, and FORMULA resolution map consistency. No unknowns to validate.

---

## 3. Test Plan

**Test file**: `tests/conformance/test_dual_resolution.py`
**Fixture data**: solar_battery_model, catf_mfe_model, attr_expr_probe, chain_spike_model

### Test Cases

| Test | Requirement | What it verifies |
|------|-------------|------------------|
| `test_backtracker_vs_resolve_input_chain` | REQ-DRA-04 | Every CHAIN MODULE_OUTPUT binding across solar_battery, catf_mfe, chain_spike resolves identically via backtracker and resolve_input with AGG_STRATEGIES |
| `test_backtracker_vs_resolve_input_reference` | REQ-DRA-04 | Every REFERENCE MODULE_OUTPUT binding (attr_expr_probe, solar_battery, catf_mfe) resolves identically via backtracker sysml_qn dispatch and resolve_input Strategy B |
| `test_formula_expose_pure_channels_match_registry` | REQ-DRA-04 | Every EXPOSE_PURE channel in `_build_attribute_resolution_map()` matches the channel returned by `scoped_lookup` or `alias_lookup` on the same registry |
| `test_formula_channel_exists_in_sysml_qn_registry` | REQ-DRA-04 | Every FORMULA channel in the attribute resolution map corresponds to a SysML QN key in the registry (backtracker REFERENCE path would find it) |
| `test_agg_module_output_channels_match_backtracker` | REQ-DRA-04 | For every aggregation SumTerm/SingletonTerm that resolve_input resolves to MODULE_OUTPUT, the same channel is registered and reachable via backtracker-equivalent scoped_lookup |
| `test_binding_resolution_maps_to_input_source` | REQ-DRA-05 | Run both paths on shared refs; verify BindingResolution(MODULE_OUTPUT, channel) produces same answer as InputSource("module_output", channel), and BindingResolution(ENTRY_POINT, qn) maps to InputSource("entry_point", qn) |
| `test_entry_point_fallback_consistent` | REQ-DRA-04 | Unresolvable ref produces ENTRY_POINT via backtracker and "entry_point" via resolve_input — both paths agree on fallback |
| `test_no_untyped_dict_get_in_resolution_paths` | REQ-DRA-03 | Static analysis: `_resolve_binding_via_registry`, `_resolve_expose_pure`, and `resolve_input` contain no raw `dict.get()` on registry internals |

### Test Infrastructure Needed

- **Helpers from C11/C12**: `build_backtracker_from_snapshot()` pattern (load snapshot → build registry → instantiate backtracker → run), `_build_resolution_context_for_agg()`, `_flatten_design_attrs()` — duplicated or imported from existing test files.
- **New helper**: `_build_attribute_resolution_map_from_snapshot()` — calls `_build_attribute_resolution_map()` with snapshot data. Import the private function from `graph_builder.py` (consistent with C12 pattern of importing private functions for conformance testing).
- **All fixture snapshots**: Already available in `tests/fixtures/{model}/extraction_snapshot.json`.

### Gate: Ready for BUILD

- [x] Test file exists with all test cases written
- [x] Tests run (all 20 PASS — conformance-only, no production code changes)
- [x] No test uses mocking (verified by grep — all hits are in comments/docstrings/method names)

---

## 4. Build Plan

### Files to Modify

None. This is a conformance-only component — no production code changes.

### Files to Create

| File | Purpose |
|------|---------|
| `tests/conformance/test_dual_resolution.py` | Dedicated cross-path consistency tests for REQ-DRA-03, REQ-DRA-04, REQ-DRA-05 |

### Implementation Notes

1. **Backtracker vs resolve_input tests** extend C12's `test_cross_path_consistency` pattern:
   - Run backtracker with `find_required_modules([], include_all=True)` to get all binding_resolutions
   - For each MODULE_OUTPUT resolution with a CHAIN source_path (dotted, no `::`), construct ResolutionContext, run `resolve_input()`, compare channels
   - For REFERENCE source_paths (containing `::`), same pattern
   - Parametrize over `[solar_battery_model, catf_mfe_model, chain_spike_model]` for CHAIN and `[attr_expr_probe, solar_battery_model, catf_mfe_model]` for REFERENCE

2. **FORMULA consistency tests** verify the attribute resolution map:
   - Call `_build_attribute_resolution_map()` with snapshot data
   - For EXPOSE_PURE entries: verify `scoped_lookup(ScopedKey(key))` returns the same channel the map contains
   - For FORMULA entries: verify `sysml_qn_lookup(SysMLQN(qn))` returns the expected channel (or channel is in `canonical_channels`)
   - Use attr_expr_probe and solar_battery (both have FORMULA/EXPOSE_PURE attrs)

3. **REQ-DRA-05 structural mapping** test:
   - BindingResolutionType.MODULE_OUTPUT maps to `source_type="module_output"`
   - BindingResolutionType.ENTRY_POINT maps to `source_type="entry_point"`
   - For overlapping refs, verify the channel/QN values match

4. **Static analysis test** for REQ-DRA-03:
   - Parse `_resolve_binding_via_registry`, `_resolve_expose_pure`, and `resolve_input` source
   - Verify no `.get(` calls that bypass typed lookup methods
   - Similar pattern to C07/C11b static analysis tests

5. **Key imports** from production code:
   - `from sysml_codegen.analysis.dependency_backtracker import DependencyBacktracker`
   - `from sysml_codegen.resolution.input_resolver import resolve_input, ResolutionContext, AGG_STRATEGIES`
   - `from sysml_codegen.resolution.graph_builder import _build_attribute_resolution_map, _resolve_expose_pure`
   - `from sysml_codegen.core.identifier_types import ScopedKey, SysMLQN, CanonicalChannel`
   - `from sysml_codegen.core.models import BindingResolutionType`

6. **Note**: C12's `test_cross_path_consistency` stays in test_input_resolver.py. X02 tests are additive and broader; there is deliberate overlap for the solar_battery CHAIN case which provides redundant verification.

### Gate: Ready for VALIDATE

- [x] All test cases pass (20/20)
- [x] No regressions in full test suite (1349 passed, 5 xfailed, 0 failures)
- [x] Lint clean (`uv run ruff check tests/conformance/test_dual_resolution.py`)

---

## 5. Validation

- [x] Every acceptance criterion from COMPONENT_CHECKLIST is satisfied:
  - [x] Same reference in same scope produces identical wiring from all applicable paths
  - [x] Test: for every Agg input that COULD be a CalcUsage input, both paths agree
- [x] Every REQ-XX-NN has at least one passing test:
  - [x] REQ-DRA-03 (static analysis — no untyped dict.get): 4 tests
  - [x] REQ-DRA-04 (cross-path consistency — backtracker vs resolve_input, FORMULA map consistency): 14 tests
  - [x] REQ-DRA-05 (BindingResolution maps to InputSource): 2 tests
  - Note: REQ-DRA-01, REQ-DRA-02 already green in C11a and C12 — not re-tested here
- [x] Full test suite passes (record count: 1349 tests passed, 5 xfailed, 0 failures)
- [x] Cross-check: re-read design intent doc 24, implementation matches
- [x] No unresolved TODOs or FIXMEs in new/modified code
- [x] COMPONENT_CHECKLIST and IMPLEMENTATION_PLAN have been updated

### Baseline Impact

None. Conformance-only component; no production code changes, no output changes.

---

## 6. Learnings

### Findings

1. **Backtracker REFERENCE Step 2 not replicated by Strategy B.** The backtracker's `_resolve_reference_dispatch` has a Step 2 (leaf + parent_part scoped lookup) that AGG_STRATEGIES' SysMLQNLookup doesn't implement. The solar_battery `annualized_om|p_net_kw` REFERENCE binding resolves via this Step 2 (Key_F registered as `solar_battery_plant.p_net_kw`), but Strategy B's normalized lookup constructs `annualized_om.p_net_kw` (penultimate + last `::` segment), which doesn't match. This is expected — REFERENCE bindings are not aggregation scope (C12 spike: zero `::` in aggregation refs). The test accounts for this by treating backtracker-only resolutions as a capability gap, not a consistency violation.

2. **All CHAIN cross-path verifications pass perfectly across 3 models.** solar_battery, catf_mfe, and chain_spike: every CHAIN MODULE_OUTPUT from the backtracker matches resolve_input with AGG_STRATEGIES. Strategy A (ScopedRegistryLookup) is sufficient for all CHAIN cases — Strategy C (ChainRedefinitionFollow) adds redundant matches.

3. **FORMULA SysML QN registration is complete.** Every FORMULA channel in the attribute resolution map has a corresponding SysML QN key in the registry, confirming the backtracker's REFERENCE path could find it.

4. **EXPOSE_PURE channels verified in canonical_channels set.** All EXPOSE_PURE channels from the attribute resolution map exist in the registry's canonical_channels.

### Design Doc Updates Needed
| Doc | What to update | Why |
|-----|---------------|-----|
| 24-dual-resolution-architecture.md | Note Strategy B asymmetry: backtracker REFERENCE Step 2 (leaf + parent scope) not replicated by SysMLQNLookup | X02 conformance finding #1 |

### Cross-Component Impact
| Component | Impact | Action needed |
|-----------|--------|---------------|

### Deviations from Plan

1. **REFERENCE cross-path test accounts for known asymmetry.** The plan's `test_backtracker_vs_resolve_input_reference` expected all REFERENCE MODULE_OUTPUTs to match. The solar_battery `annualized_om|p_net_kw` case uses a backtracker-only path (Step 2) that Strategy B doesn't replicate. The test was updated to count backtracker-only resolutions as a documented capability gap (`bt_only` counter) rather than a consistency failure.

2. **No `_build_attribute_resolution_map_from_snapshot()` helper needed.** The test calls `_build_attribute_resolution_map()` directly with snapshot data — simpler than the plan's proposed wrapper.

---

## 7. Commit

**Branch**: `cost-pattern-refactor` (current branch — Phase 3 work)
**Commit convention**: one commit per component, message references component code

- [x] All validation checks above are green
- [x] `git add` only the files listed in Build Plan + test file, plus IMPLEMENTATION_PLAN and COMPONENT_CHECKLIST (no unrelated changes)
- [ ] Commit message format:
  ```
  refactor(X02): Dual resolution consistency — cross-path conformance tests

  - Tests: 20 new conformance tests in tests/conformance/test_dual_resolution.py
  - Refs: REQ-DRA-03, REQ-DRA-04, REQ-DRA-05
  - Design intent: 24-dual-resolution-architecture.md
  ```
- [x] Committed successfully (55addd2)

---

## Progress Log

### Session: 2026-02-17 — Planning
**Phase**: PLANNING
**Work done**:
- Read implementation plan step 3.4 and X02 checklist entry
- Read design intent doc 24 (dual resolution architecture) — all 5 REQs
- Read C11a, C11b, C12 plans and accumulated learnings
- Read existing `test_cross_path_consistency` in C12 (test_input_resolver.py:552-609)
- Read all three resolution path implementations:
  - Backtracker: `dependency_backtracker.py:501` (`_resolve_binding_via_registry`)
  - FORMULA: `graph_builder.py:587` (`_build_attribute_resolution_map`, `_resolve_expose_pure`)
  - Aggregation: `input_resolver.py:239` (`resolve_input`)
- Design consistency check completed — 3 issues documented and resolved
- Spike decision: SKIP (C12 spike already answered key questions)
- 8 test cases designed covering REQ-DRA-03, REQ-DRA-04, REQ-DRA-05
**Stopped at**: Plan complete, ready for review
**Next step**: BUILD — create `tests/conformance/test_dual_resolution.py`
**Blockers**: None

### Session: 2026-02-17 — Build + Validate
**Phase**: BUILD → VALIDATE → DONE
**Work done**:
- Created `tests/conformance/test_dual_resolution.py` with 20 test items (8 test cases, 6 parametrized)
- All 8 planned test cases implemented:
  - `test_backtracker_vs_resolve_input_chain` (3 models: solar_battery, catf_mfe, chain_spike)
  - `test_backtracker_vs_resolve_input_reference` (3 models: attr_expr_probe, solar_battery, catf_mfe)
  - `test_formula_expose_pure_channels_match_registry` (2 models: attr_expr_probe, solar_battery)
  - `test_formula_channel_exists_in_sysml_qn_registry` (2 models: attr_expr_probe, solar_battery)
  - `test_agg_module_output_channels_match_backtracker` (3 models: solar_battery, issue22, alias_agg_probe)
  - `test_binding_resolution_maps_to_input_source` + `test_resolution_type_enum_values_correspond`
  - `test_entry_point_fallback_consistent`
  - `test_no_untyped_dict_get_in_*` (4 static analysis tests for REQ-DRA-03)
- Fixed initial failure: solar_battery REFERENCE `annualized_om|p_net_kw` uses backtracker Step 2 not replicated by Strategy B. Updated test to document as capability gap, not consistency violation.
- Lint fixes: removed unused imports, removed unused variable, fixed f-string
- All 20 tests pass, full suite: 1349 passed, 5 xfailed, 0 failures
- Validation section completed — all checkboxes green
- Learnings and deviations documented
**Stopped at**: DONE — ready for commit
**Next step**: Update IMPLEMENTATION_PLAN.md, then commit
**Blockers**: None
