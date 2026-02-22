# Component: Virtual Binding Rewrite (C09)

**Status**: DONE
**Created**: 2026-02-17
**Last updated**: 2026-02-17
**Updated by**: PROMPT-plan agent — C09 Virtual Binding Rewrite Spike

## Source Documents

- **Checklist entry**: `COMPONENT_CHECKLIST.md` — C09
- **Design intent**: [12-virtual-binding-rewrite.md](../../concepts/refactor-design-intent/12-virtual-binding-rewrite.md)
- **Requirements**: REQ-VBR-01 through REQ-VBR-07
- **Depends on**: C01 (Data Models), C08 (Output Registry) — both complete

---

## 1. Assessment

### What This Component Does

`_rewrite_virtual_bindings()` patches virtual CalcUsage bindings in-place using `:>>` design
overrides from the hierarchy extraction. It builds an override index keyed by
`(full_parent_path, leaf_attribute_name)`, then iterates non-template CalcUsage bindings,
matching each binding's leaf name against the index. LITERAL matches flip the binding to
`BindingType.LITERAL` with the override value. CHAIN matches replace `source_path`. This
ensures downstream steps (backtracker, registry) see design-intent values instead of
template-level references.

### Current State

- **Exists?** Yes — `src/sysml_codegen/generation/initialization.py:266-333`
- **Needs extraction/refactoring?** No structural changes needed for C09. The function exists
  as a standalone helper `_rewrite_virtual_bindings()` with a clean interface
  (`calc_usages, hierarchy_data -> int`). Future Phase 7.1 will extract it to
  `orchestration/`, but C09 validates behavior in-place.
- **Current test coverage**: No dedicated tests. The function is exercised indirectly through
  `build_pipeline_context()` integration tests and the pipeline baseline tests (Phase 0.2),
  but no conformance test isolates and verifies the rewrite behavior against each REQ.

### Design Consistency Check

- [x] All acceptance criteria from COMPONENT_CHECKLIST are testable with real data (no mocks)
- [x] AC are consistent with the requirements in the design intent doc(s)
- [x] No contradictions with other component specs
- [x] Input/output interfaces match what upstream/downstream components expect
- [x] Any ambiguities or gaps identified and resolved (documented below)

**Issues found during review:**

1. **Snapshot data is post-rewrite (CRITICAL for test design).**
   The extraction snapshots are captured via `build_pipeline_context()`, which calls
   `_rewrite_virtual_bindings()` at Step 3.5. This means `calc_usages` in the snapshot
   already have rewritten bindings. Testing the rewrite function directly on snapshot data
   would show 0 rewrites (already LITERAL, already has no source_path for overridden bindings).

   **Resolution**: The spike must determine the testing strategy. Three options:
   - (A) **Reconstruct pre-rewrite state**: Use the `design_overrides` from the snapshot to
     reverse-engineer what the bindings looked like before rewrite (set `binding_type` back to
     REFERENCE, reconstruct `source_path` from the template pattern). Then apply
     `_rewrite_virtual_bindings()` and verify the expected mutations.
   - (B) **Test structural properties post-rewrite**: Verify that after rewrite, every
     design_override is reflected in the corresponding binding (binding_type matches override
     type, literal_value matches override value). This tests "the rewrite happened correctly"
     without needing pre-rewrite state.
   - (C) **Construct synthetic CalcUsageData from real components**: Build `CalcUsageData`
     objects with REFERENCE bindings using real qualified names and source_paths derived from
     the template patterns in the snapshot, then run the rewrite.

2. **No CHAIN overrides in solar_battery design_overrides.**
   All 13 `design_overrides` in solar_battery are `redefinition_type: "literal"` with
   `is_deep_path: true`. Zero CHAIN overrides. REQ-VBR-04 (CHAIN override) has no fixture
   coverage in solar_battery. The CHAIN redefinitions that exist in the `redefinitions` list
   (e.g., `source_path: "cost_model.total_cost"`) are not in `design_overrides` — they're
   flat redefinitions on PartDefs, not design-level deep-path overrides.

   **Resolution**: REQ-VBR-04 must be tested with constructed data using real component names
   from the fixture. Alternatively, check other fixture models. Issue22_model and catf_mfe
   have empty design_overrides. Only solar_battery has non-empty design_overrides, and all are
   LITERAL. This is a genuine fixture gap — no model exercises CHAIN design overrides.

3. **No template CalcUsages in snapshots.**
   The snapshot only contains non-template usages (`is_template: false`). Template usages
   (`is_template: true`) are filtered out during extraction or not captured. REQ-VBR-05
   (template skip) can be tested by constructing a CalcUsageData with `is_template=True` and
   verifying it's skipped — but this uses real field values from the snapshot, not a mock.

4. **EXPRESSION override type exists but is not handled by the rewrite.**
   The `RedefinitionType` enum has three values: `LITERAL`, `CHAIN`, `EXPRESSION`. The
   rewrite function only handles LITERAL and CHAIN. EXPRESSION overrides are silently
   skipped (no match in the `if/elif` chain at lines 324-331). The design intent doc 12
   only specifies LITERAL and CHAIN mutation cases, so this is correct behavior — but
   the omission should be documented.

5. **No flat (non-deep-path) overrides in solar_battery design_overrides.**
   All 13 are `is_deep_path: true`. The REQ-VBR-01/02 distinction between flat and deep-path
   index key construction is only exercised for the deep-path case with real data. Flat
   override key construction needs constructed test data.

### Risks & Unknowns

1. **Testing strategy for in-place mutation on post-rewrite data** — spike question.
2. **No CHAIN override fixture coverage** — must decide whether to construct data or accept
   partial coverage and document the gap.
3. **Idempotency**: Is the function safe to call twice? The post-rewrite snapshot test
   implicitly checks this (calling on already-rewritten data should return 0), but this isn't
   an explicit requirement.

---

## 2. Spike

**Decision**: SPIKE
**Rationale**: The primary unknown is how to test an in-place mutation function when the
snapshot data is already post-mutation. Three candidate strategies exist (see Assessment
Issue #1) and the spike must determine which produces reliable, maintainable tests using
real data. The function itself is well-understood (68 lines, clear logic), but the test
design requires experimentation.

### Spike Questions

1. **Can we reconstruct pre-rewrite CalcUsageData from snapshot data + design_overrides?**
   Given a post-rewrite binding (LITERAL, value=400.0) and a matching design_override
   (owning_part_qn, target_path, literal_value=400.0), can we reliably reconstruct the
   original REFERENCE binding (binding_type=REFERENCE, source_path="Lib::Solar_Array::wattage")?
   What is the template source_path pattern?

2. **Does calling `_rewrite_virtual_bindings()` on already-rewritten data return 0?**
   If yes, this confirms idempotency and gives us a "no-change" baseline test.

3. **Can we construct a CHAIN design override test case using real names from the fixture?**
   We need a CalcUsageData with a binding that would be matched by a CHAIN override. Can we
   use real qualified_names and attribute_names from the solar_battery snapshot to build this?

### Spike Approach

1. Load solar_battery snapshot. Inspect `design_overrides` and the corresponding virtual
   CalcUsage bindings. Map each override to the binding it affected.
2. Call `_rewrite_virtual_bindings()` on the snapshot calc_usages + hierarchy_data.
   Verify it returns 0 (idempotency check).
3. For one known LITERAL override (e.g., `wattage=400.0`), manually set the corresponding
   binding back to `REFERENCE` with `source_path="SolarBatteryLibrary::PV_Module::wattage"`.
   Call `_rewrite_virtual_bindings()` and verify it rewrites correctly.
4. Construct a CHAIN override test case: create a `RedefinitionData` with `redefinition_type=CHAIN`
   and a CalcUsageData binding with a REFERENCE source_path. Verify the rewrite replaces
   source_path.

### Spike Findings

**Q1: Can we reconstruct pre-rewrite CalcUsageData from snapshot data + design_overrides?**
YES. Strategy proven:
- For each design_override, locate the matching virtual CalcUsage by matching the override index
  key `(full_parent_path, leaf)` to `(usage.qualified_name.rsplit("__",1)[0], binding.param_name)`.
- Reconstruct the original REFERENCE binding:
  - `binding.binding_type = BindingType.REFERENCE`
  - `binding.source_path = f"{owning_part_def_qn.replace('__', '::')}::{param_name}"`
  - `binding.literal_value = None`
- All 13 overrides successfully reconstructed and rewritten. Return value = 13. All post-rewrite
  states match the original snapshot (LITERAL, correct literal_value, source_path=None).

**Q2: Does calling `_rewrite_virtual_bindings()` on already-rewritten data return 0?**
YES. Confirmed idempotency: calling on post-rewrite snapshot data returns 0. All LITERAL bindings
have `source_path=None`, which triggers the `if not binding.source_path: continue` guard (line 308).

**Q3: Can we construct a CHAIN design override test case using real names from the fixture?**
YES. Verified that `RedefinitionData`, `BindingInfo`, and `CalcUsageData` constructors accept
all required fields. Can use real qualified_names from the snapshot (e.g.,
`SolarBatteryDesign__solar_battery_plant__solar_array__pv_module__cost_model`) with
`RedefinitionType.CHAIN` and `source_path="tracker.eta"` to test the CHAIN rewrite path.

**Additional findings:**
- 15 non-template CalcUsages in solar_battery; 10 have `owning_part_def_qn` (virtual copies).
  5 are top-level usages without owning_part_def_qn (energy_production, annualized_om, etc.)
- Call ordering confirmed via AST inspection: `_extract_hierarchy_and_rewrite_bindings` at line 763,
  `extract_design_attributes` at line 768, `build_output_registry` at line 782,
  `.find_required_modules` at line 798, `build_computation_graph` at line 846.
- The allocation_model CalcUsage (solar_array) has LITERAL bindings with `source_path` set to
  the literal value string (e.g., `src=25.0`). These don't have matching design_overrides.

### Spike Impact on Plan

No changes to the test plan needed. All three candidate testing strategies validated:
- **Strategy A (reconstruct pre-rewrite)**: Primary strategy for REQ-VBR-03 tests. Works perfectly.
- **Strategy B (post-rewrite structural verification)**: Used for idempotency test.
- **Strategy C (constructed data)**: Used for CHAIN (REQ-VBR-04), template skip (REQ-VBR-05),
  flat override (REQ-VBR-02), and EXPRESSION skip tests.

The test plan as written is correct. Proceed to TEST phase.

---

## 3. Test Plan

**Test file**: `tests/conformance/test_virtual_binding_rewrite.py`
**Fixture data**: solar_battery_model extraction snapshot (primary — only model with
non-empty design_overrides). Supplemented with constructed CalcUsageData using real names
from snapshots for CHAIN override and template-skip coverage.

### Test Cases

> Every requirement (REQ-VBR-NN) must have at least one test case.
> Every test uses real data — no mocks. Stubs only at SysIDE adapter boundary.

| Test | Requirement | What it verifies |
|------|-------------|------------------|
| `test_req_vbr_01_override_index_keyed_by_parent_leaf[solar_battery]` | REQ-VBR-01 | Build override index from solar_battery `design_overrides`; verify every key is `(full_parent_path, leaf_attribute_name)` tuple; verify 13 entries; verify specific keys like `("SolarBatteryDesign__solar_battery_plant__solar_array__pv_module", "wattage")` |
| `test_req_vbr_02_deep_path_join[solar_battery]` | REQ-VBR-02 | For each deep-path override in solar_battery, verify intermediate segments joined with `__` (e.g., `target_path=["pv_module","wattage"]` → `full_parent="SolarBatteryDesign__solar_battery_plant__solar_array__pv_module"`) |
| `test_req_vbr_02_flat_override_key_format` | REQ-VBR-02 | Construct flat (non-deep-path) RedefinitionData with real owning_part_qn from solar_battery; verify override index key is `(owning_part_qn, attribute_name)` with no `__` appended |
| `test_req_vbr_03_literal_override_mutations` | REQ-VBR-03 | Reconstruct pre-rewrite CalcUsageData with REFERENCE binding for `wattage` on `pv_module__cost_model`; apply `_rewrite_virtual_bindings()`; verify binding_type changed to LITERAL, literal_value set to 400.0, source_path set to None |
| `test_req_vbr_03_literal_override_all_13_overrides[solar_battery]` | REQ-VBR-03 | For all 13 design_overrides, reconstruct pre-rewrite bindings, apply rewrite, verify all 13 are LITERAL with correct values; parametrized over all overrides |
| `test_req_vbr_04_chain_override_replaces_source_path` | REQ-VBR-04 | Construct a CHAIN RedefinitionData override with real names from solar_battery (e.g., `source_path="tracker.eta"`); construct CalcUsageData with REFERENCE binding; apply rewrite; verify source_path replaced, binding_type unchanged |
| `test_req_vbr_05_template_copies_skipped` | REQ-VBR-05 | Construct CalcUsageData with `is_template=True` using real qualified_name from solar_battery template pattern; include matching design_override; apply rewrite; verify binding NOT mutated; verify rewrite_count excludes template |
| `test_req_vbr_06_already_literal_skipped` | REQ-VBR-06 | Construct CalcUsageData with binding already `LITERAL` and matching override in index; apply rewrite; verify binding unchanged; verify rewrite_count = 0 |
| `test_req_vbr_06_no_source_path_skipped` | REQ-VBR-06 | Construct CalcUsageData with binding having `source_path=None` and non-LITERAL type; apply rewrite; verify binding unchanged |
| `test_req_vbr_07_rewrite_before_downstream[solar_battery]` | REQ-VBR-07 | Static analysis test: verify `_rewrite_virtual_bindings()` is called at line 243 in `_extract_hierarchy_and_rewrite_bindings()`, which is called at line 763 in `build_pipeline_context()` BEFORE Steps 4-7. Read source with `ast.parse()` or line inspection to verify call ordering. |
| `test_idempotency[solar_battery]` | REQ-VBR-03, REQ-VBR-06 | Call `_rewrite_virtual_bindings()` on post-rewrite snapshot data; verify returns 0 (no rewrites — all bindings already LITERAL or no source_path) |
| `test_empty_override_index_returns_zero` | REQ-VBR-01 | Pass CalcUsages with hierarchy_data having empty `design_overrides`; verify returns 0 immediately |
| `test_sysml_qn_leaf_extraction` | REQ-VBR-03 | Binding with `source_path="Lib::Solar_Array::wattage"` → leaf = `"wattage"`; verify `"::"` separator handled |
| `test_dotted_leaf_extraction` | REQ-VBR-04 | Binding with `source_path="tracker.eta"` → leaf = `"eta"`; verify `"."` separator handled |
| `test_bare_name_leaf_extraction` | REQ-VBR-06 | Binding with `source_path="wattage"` → leaf = `"wattage"`; verify bare name fallback |
| `test_expression_override_not_applied` | REQ-VBR-03 | Construct EXPRESSION-type RedefinitionData; verify no mutation (function only handles LITERAL and CHAIN) |
| `test_rewrite_count_matches_mutations[solar_battery]` | REQ-VBR-03 | Reconstruct pre-rewrite state for all 13 overrides; apply rewrite; verify return value == 13 |

### Test Infrastructure Needed

1. **Helper function**: `reconstruct_pre_rewrite_binding(binding, design_override)` — given a
   post-rewrite LITERAL binding and its matching design_override, reconstruct the original
   REFERENCE binding by setting `binding_type=BindingType.REFERENCE` and
   `source_path` to the SysML QN pattern (`{lib_qn}::{attr_name}` using
   `owning_part_def_qn` from the CalcUsageData).

2. **Helper function**: `build_override_index(design_overrides)` — extract Phase 1 of
   `_rewrite_virtual_bindings()` for direct testing of the index construction.

3. No new conftest fixtures needed — `solar_battery_snapshot` already available.

### Gate: Ready for BUILD
- [x] Test file exists with all test cases written
- [x] Tests run (all 38 PASS — function already implemented correctly)
- [x] No test uses mocking (verified by grep for `mock`, `patch`, `MagicMock`)

---

## 4. Build Plan

### Files to Modify

| File | Change | Why |
|------|--------|-----|
| (none) | No production code changes needed for C09 | The function at `generation/initialization.py:266-333` is already implemented and working. C09 is a conformance testing effort — the spike validates the existing implementation, and the tests lock it down for future refactoring (Phase 7.1 extraction to `orchestration/`). |

### Files to Create

| File | Purpose |
|------|---------|
| `tests/conformance/test_virtual_binding_rewrite.py` | Conformance tests for REQ-VBR-01 through REQ-VBR-07 |

### Implementation Notes

1. **The function already exists and works.** C09 is a "spike + conformance test" step, not
   a build-from-scratch step. The implementation plan says "Extract
   `_rewrite_virtual_bindings()` from `generation/initialization.py` into a standalone
   function" but also says "or keep in-place with clean interface." The function already
   has a clean interface. Extraction to `orchestration/` is Phase 7.1 scope.

2. **Import the function directly for testing.** The function is `_rewrite_virtual_bindings()`
   (underscore-prefixed). It's already in `__all__` indirectly through module-level availability.
   Import via `from sysml_codegen.generation.initialization import _rewrite_virtual_bindings`.

3. **Pre-rewrite state reconstruction strategy** (contingent on spike results):
   - For each design_override with `is_deep_path=True`:
     - Find the virtual CalcUsageData whose `parent_path` matches the deep-path full_parent
     - The binding's `param_name` matches the override's `leaf_attr` (last element of target_path)
     - Set `binding.binding_type = BindingType.REFERENCE`
     - Set `binding.source_path` to `f"{owning_part_def_qn.replace('__', '::')}::{param_name}"`
       (reverse the Python→SysML QN conversion)
     - Set `binding.literal_value = None`
   - This produces CalcUsageData objects in their pre-rewrite state using ONLY data from the
     snapshot (real qualified names, real attribute names, real override values).

4. **CHAIN override test case construction** (no fixture coverage):
   - Use a real virtual CalcUsage qualified_name (e.g., `SolarBatteryDesign__solar_battery_plant__solar_array__pv_module__cost_model`)
   - Construct a `RedefinitionData` with `redefinition_type=CHAIN`, `source_path="tracker.eta"`,
     `owning_part_qn="SolarBatteryDesign__solar_battery_plant__solar_array"`,
     `target_path=["pv_module", "wattage"]`, `is_deep_path=True`
   - Add a REFERENCE binding with `source_path="SolarBatteryLibrary::PV_Module::wattage"`
   - Verify rewrite replaces `source_path` to `"tracker.eta"`

5. **Deepcopy CalcUsageData before mutation.** Since `_rewrite_virtual_bindings()` mutates
   in-place, tests that reconstruct pre-rewrite state must deepcopy the snapshot data first
   to avoid polluting the session-scoped fixture.

### Gate: Ready for VALIDATE
- [x] All test cases pass (38/38)
- [x] No regressions in full test suite (1118 passed)
- [x] Lint clean (`ruff check` passes on test file)

---

## 5. Validation

- [x] Override index keyed by `(full_parent_path, leaf_attribute_name)` — REQ-VBR-01 (3 tests)
- [x] Deep-path joins intermediate segments with `__` — REQ-VBR-02 (5 tests)
- [x] LITERAL override: sets binding_type=LITERAL, copies literal_value — REQ-VBR-03 (20 tests)
- [x] CHAIN override: replaces source_path — REQ-VBR-04 (2 tests)
- [x] Template copies (is_template=True) skipped — REQ-VBR-05 (2 tests)
- [x] Already-LITERAL or no source_path skipped — REQ-VBR-06 (3 tests)
- [x] Rewrite completes before downstream (backtracker, registry build) — REQ-VBR-07 (2 tests)
- [x] Test: extract solar_battery, apply rewrite, verify binding changes — C09 AC final item
- [x] Every REQ-VBR-NN has at least one passing test
- [x] Full test suite passes (record count: 1118 tests, 0 failures)
- [x] Cross-check: re-read design intent doc 12, verify tests cover all specified behavior
- [x] No unresolved TODOs or FIXMEs in new/modified code
- [x] COMPONENT_CHECKLIST and IMPLEMENTATION_PLAN have been updated

### Baseline Impact

No baseline impact — C09 adds conformance tests only. No production code changes.

---

## 6. Learnings

### Findings

1. **Pre-rewrite reconstruction from post-rewrite snapshots works reliably.** The approach of
   reversing `owning_part_def_qn` from `__` to `::` format to reconstruct `source_path` and
   setting `binding_type=REFERENCE` is deterministic and correct for all 13 solar_battery overrides.
   This pattern is reusable for C10 (aggregation scoping) which faces the same snapshot issue.

2. **The function is idempotent.** Calling `_rewrite_virtual_bindings()` on already-rewritten data
   returns 0 with no side effects. This is because LITERAL bindings have `source_path=None`, which
   triggers the `if not binding.source_path: continue` guard before any leaf extraction.

3. **All 38 tests passed immediately — no production code changes needed.** C09 is purely a
   conformance-testing component. The existing implementation at `initialization.py:266-333` is
   correct and handles all documented cases.

4. **CHAIN override path tested only with constructed data.** Zero CHAIN overrides exist in
   design_overrides across all 6 fixture models. Two tests verify CHAIN behavior using constructed
   data with real qualified names from solar_battery.

5. **EXPRESSION override path verified as no-op.** The function's `if/elif` chain at lines 324-331
   only handles LITERAL and CHAIN. EXPRESSION overrides match in the index but fall through without
   mutation. This is correct per the design intent doc but undocumented.

### Design Doc Updates Needed
| Doc | What to update | Why |
|-----|---------------|-----|
| 12-virtual-binding-rewrite.md | Note that EXPRESSION-type overrides are silently skipped (not an error) | Code handles only LITERAL and CHAIN; EXPRESSION falls through with no mutation |
| 12-virtual-binding-rewrite.md | Note zero CHAIN override coverage in design_overrides across all 6 fixture models | Coverage gap — CHAIN override path tested only with constructed data |
| COMPONENT_CHECKLIST.md | Add note about snapshot post-rewrite state affecting test strategy | Testing methodology finding |

### Cross-Component Impact
| Component | Impact | Action needed |
|-----------|--------|---------------|
| C10 (Aggregation Scoping) | Same snapshot-is-post-mutation issue applies to `_scope_aggregation_expressions()` | C10 plan should address the same testing challenge |
| Phase 7.1 | C09 conformance tests will validate behavior before extraction to `orchestration/` | Tests serve as safety net for the structural refactoring |

### Deviations from Plan

1. **Test naming convention differs from plan.** The plan listed test names like
   `test_req_vbr_01_override_index_keyed_by_parent_leaf[solar_battery]` but the actual
   test file uses class-based organization (e.g., `TestOverrideIndexKey::test_override_index_structure`).
   This is consistent with other conformance test files in the project (C03-C08 all use class-based).

2. **TEST and BUILD phases collapsed.** Since C09 requires no production code changes, all 38
   tests passed on the first run. The plan anticipated most tests would FAIL during TEST phase,
   but the existing implementation was already correct.

---

## 7. Commit

**Branch**: `cost-pattern-refactor` (current branch)
**Commit convention**: one commit per component, message references component code

- [x] All validation checks above are green
- [x] Committed as part of Phase 2 batch commit (C08 + C09 + C10 + TRR + audit)
- [x] Committed successfully *(2026-02-17)*

---

## Progress Log

> Each agent context that does work on this component adds an entry here.
> This is how the next context knows where to pick up.

### Session: 2026-02-17 — Initial plan creation
**Phase**: PLANNING
**Work done**:
- Read all design docs: IMPLEMENTATION_PLAN (Step 2.2), COMPONENT_CHECKLIST (C09),
  12-virtual-binding-rewrite.md, 09-data-models.md
- Read current source: `generation/initialization.py:266-333` (_rewrite_virtual_bindings, 68 lines)
- Read snapshot capture script: snapshots are captured via `build_pipeline_context()` which
  includes the rewrite step — snapshots contain POST-rewrite data
- Analyzed solar_battery fixture data:
  - 13 design_overrides, ALL LITERAL, ALL deep-path
  - 10 virtual CalcUsages (is_template=false, owning_part_def_qn != null)
  - 0 CHAIN overrides in design_overrides (coverage gap)
  - 0 flat (non-deep-path) overrides in design_overrides
  - 0 template usages in snapshot (is_template=true not present)
  - 0 EXPRESSION overrides in design_overrides
  - Other models (catf_mfe, sample, attr_expr_probe, chain_spike, issue22) have empty
    design_overrides — solar_battery is the only model with override data
- Read C08 (Output Registry) learnings: _compat bridge for dead keys, backtracker coupling
- Design consistency review: 5 issues found, all with resolutions
- Spike decision: SPIKE needed — testing strategy for in-place mutation on post-rewrite data
- Plan template filled, self-review checklist partially completed
**Stopped at**: Plan complete, spike not yet executed
**Next step**: Execute spike (verify idempotency, test pre-rewrite reconstruction, verify
CHAIN override construction approach)
**Blockers**: None — all prerequisites (C01, C08, Phase 0, Checkpoint 1) are complete

### Session: 2026-02-17 — Spike + Test + Build + Validate
**Phase**: PLANNING → DONE (all phases completed in one session)
**Work done**:
- Executed spike: inspected solar_battery snapshot data, confirmed 13 LITERAL deep-path overrides,
  0 CHAIN/EXPRESSION/flat overrides across all 6 fixture models
- Spike Q1: Pre-rewrite reconstruction validated — all 13 bindings restored and correctly rewritten
- Spike Q2: Idempotency confirmed — `_rewrite_virtual_bindings()` returns 0 on post-rewrite data
- Spike Q3: CHAIN override construction approach validated with real names from fixture
- Wrote 38 conformance tests in `tests/conformance/test_virtual_binding_rewrite.py`:
  - REQ-VBR-01: 3 tests (index structure, specific keys, empty overrides)
  - REQ-VBR-02: 5 tests (deep-path join all overrides, 3 parametrized cases, flat override)
  - REQ-VBR-03: 20 tests (single, all-13, 13 parametrized, leaf extraction x3, expression skip,
    count validation x2)
  - REQ-VBR-04: 2 tests (CHAIN replaces source_path, dotted source_path)
  - REQ-VBR-05: 2 tests (template not rewritten, template excluded + non-template included)
  - REQ-VBR-06: 3 tests (already LITERAL, no source_path, idempotency)
  - REQ-VBR-07: 2 tests (call ordering static analysis, nested call verification)
- All 38 tests pass on first run (no production code changes needed)
- Full suite: 1118 tests, 0 failures
- Lint clean on test file
- All validation checkboxes completed
**Stopped at**: Component DONE — ready for commit
**Next step**: Commit C09 and update IMPLEMENTATION_PLAN / COMPONENT_CHECKLIST
**Blockers**: None
