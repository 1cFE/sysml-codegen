# Phase 5+6 Checkpoint Audit — Action Items

**Audit date**: 2026-02-19
**Auditor**: Claude Opus 4.6 (Phase 5+6 checkpoint review)
**Scope**: Phase 5 (C19, 5.2) + Phase 6 (C20-C25, X01) + forward-looking Phase 7 impact

---

## Executive Summary

Phases 5 and 6 are functionally complete. Phase 5 is conformance-only (zero production
code changes). Phase 6 applied 4 bug fixes (Bugs 8a, 8b, 9, 10), confirmed 1 deferred
bug (Bug 11), consolidated type mapping (X01), and added 206 conformance tests.

**Overall status**: 1753 tests passing, 6 xfailed (5 inherited attr + 1 Bug 11), 0 failures.

**Key findings**: 7 bookkeeping gaps, 2 unapplied design doc amendments, 1 missing test
count entry, 3 test quality concerns, and 4 items that affect Phase 7 planning.

---

## A. Bookkeeping — Incomplete Documentation Updates

> These are status accuracy and documentation fixes. No code changes.

- [x] **A1** — Checkpoint 6 checkbox NOT checked in IMPLEMENTATION_PLAN.md (line 552).
  Currently reads `[ ]`. Should be `[x]` with completion note.
  **Done 2026-02-19**: Checked and updated with full completion details (combined with A6).

- [x] **A2** — Checkpoint 5 and 6 rows in Summary table (lines 665-666) still show
  estimate counts (`~20`, `~40`). Should be updated to actuals:
  - Checkpoint 5: `~20` → `55 (actual: C19: 39, 5.2: 16)`
  - Checkpoint 6: `~40` → `167 (actual: C20: 27, C21: 19, C22: 21, C23: 30, C24: 22, C25: 28, X01: 20)`
  **Done 2026-02-19**: Both rows updated with actual counts.

- [x] **A3** — C24 Module Registry Generator is MISSING from Test Count Tracking table
  (between C23 line 1289 and C25 line 1290). Should add:
  `| C24 Module Registry Generator | 1705 | 22 | 1727 (+6 xfail) | 2026-02-18 |`
  And adjust C25 row: existing count 1733 = 1727 + 6 (gap corrected or documented).
  **Done 2026-02-19**: Inserted C24 row between C22 and C23 (matches actual execution
  order: C24 was step 6.4, C23 was step 6.5). Numbers: 1653 + 22 = 1675, matching
  C23's "Existing" of 1675. C25 row unchanged (1705 + 28 = 1733 remains correct).

- [x] **A4** — COMPONENT_CHECKLIST.md: C20 marked `*(completed 2026-02-18)*` but C21
  AC checkboxes reference `C21` inline. Verify all C20-C25 ACs are checked in the
  checklist (audit found all checked, but cross-verify).
  **Done 2026-02-19**: Cross-verified. All C20-C25 ACs are checked. Only unchecked
  items are C01 (typed names), C03/C05 (Deferred Issue #9), and C26 (Phase 7).

- [x] **A5** — COMPONENT_CHECKLIST.md C26 (PipelineModule Migration) still shows all
  ACs unchecked `[ ]`. This is correct (Phase 7), but should be annotated with
  "Phase 7 target" for clarity, consistent with how C19 notes "Phase 7.6".
  **Done 2026-02-19**: Added "*(Phase 7 target)*" to heading and "*(Phase 7 — not yet started)*" to AC section.

- [x] **A6** — Checkpoint 6 text (line 552) is missing the completion date and test
  count summary that other checkpoints have. Update to match the pattern:
  `**Checkpoint 6**: [x] Full generation validated. 167 new conformance tests (C20: 27, C21: 19, C22: 21, C23: 30, C24: 22, C25: 28, X01: 20). 1753 total tests, 2 skipped, 6 xfailed, 0 failures. *(2026-02-19)*`
  **Done 2026-02-19**: Combined with A1. Full checkpoint text matches pattern.

- [x] **A7** — Update all Phase 5 and 6 plan.md files' status to `DONE` if not already.
  (Audit found all are marked DONE, but the type-mapping-consolidation plan.md
  may still be in BUILD/VALIDATE state since X01 is today's work.)
  **Done 2026-02-19**: Verified — all plan.md files already show `**Status**: DONE`
  (orchestrator-step-ordering, pipeline-e2e-validation, pipeline-yaml-generator,
  module-wrapper-generator, schema-generator, module-registry-generator,
  stencil-smart-regen, json-template-generator, type-mapping-consolidation).

---

## B. Design Doc Amendments — Not Yet Applied

> Two entries in the Design Doc Amendments table (lines 1249-1250) have empty
> "Applied?" columns.

- [x] **B1** — `22-output-schema-rules.md`: Note Bug 11 confirmed —
  Permitting_Interconnect has `default=0.0` on 4 output fields (`material_cost`,
  `fab_cost`, `install_cost`, `idiot_index`). Add note to relevant section
  explaining the REQ-OSR-05 violation, its root cause (schema generator doesn't
  strip defaults from outputs), and its tracking status (xfailed test in C22).
  **Done 2026-02-19**: Added "Bug 11: Confirmed REQ-OSR-05 Violation" subsection
  with root cause, affected fields, and xfail tracking reference.

- [x] **B2** — `08-generation.md`: Update REQ-GEN-06 "Verified by" note. Remove
  "Currently VIOLATED" language and add reference to `generation/type_mapping.py`
  as the consolidated module. Note the 20 X01 conformance tests.
  **Done 2026-02-19**: REQ-GEN-06 table row updated with verification details.
  "Current Gap" section retitled (REQ-GEN-06 removed from heading), added resolved
  callout block, and trimmed duplicated-logic description.

---

## C. Bug Tracking Summary — Phases 5+6

### Bugs Fixed

| Bug | Phase | Component | File | Fix Description |
|-----|-------|-----------|------|-----------------|
| Bug 8a | 6 | C24 | `registry.py:126` | Aggregation import paths: `owning_part_qn` → `module_eqn.replace("__", "::")` for design-scoped paths |
| Bug 8b | 6 | C24 | `registry.py:93-137` | Added `_resolve_class_name_collisions()` (~70 lines) for duplicate aggregation class names |
| Bug 9 | 6 | C20 | `graph_builder.py` (Step 6.9) | Added param_group propagation after Step 6.8 orphan handling (~9 lines). Fixed 28 entry point InputSources in solar_battery |
| Bug 10 | 6 | C20 | `graph_builder.py:1045` | Multiplicity input type `"int"` → `"float"` (1 line). Updated 6 test assertions across C16/unit tests |

### Bugs Deferred

| Bug | Phase | Component | Status | Description |
|-----|-------|-----------|--------|-------------|
| ~~Bug 8a remainder~~ | 6→7 | C24→7.5a | **FIXED 2026-02-19** | `graph_builder.py:970` now uses `agg.module_eqn.replace("__", "::")`. Graph and registry module_types consistent. Baselines regenerated. |
| Bug 11 | 6→7 | C22 | xfail test | `Permitting_Interconnect` output fields render `Field(default=0.0, ...)`. REQ-OSR-05 violation. Schema generator should strip defaults from outputs |

---

## D. Learnings That Affect Phase 7

### D1. ~~graph_builder module_type mismatch (Bug 8a remainder)~~ RESOLVED 2026-02-19

- **Was**: `PipelineModule.module_type` for aggregation modules used `owning_part_qn`
  (library-scoped, e.g., `solarbatterylibrary__solar_array.capital_costModule`), but
  registry.py generated design-scoped module_types (e.g.,
  `solarbatterydesign.solar_battery_plant.solar_array.capital_costModule`).
- **Fix applied**: `graph_builder.py:970` now uses `agg.module_eqn.replace("__", "::")`
  — identical to registry.py:131. All 20 solar_battery aggregation module_types verified
  consistent between graph JSON and registry `__init__.py`.
- **Actual cascade** (narrower than predicted):
  - ComputationGraph JSON baselines: regenerated (solar_battery, attr_expr_probe, chain_spike)
  - Pipeline YAML baselines: regenerated (same 3 models)
  - C14-C18 conformance tests: **zero assertion failures** (tests compare within-model
    consistency, not hardcoded strings)
  - C20-C25 conformance tests: **zero assertion failures**
  - 1 unit test assertion updated (`test_graph_builder_aggregation.py::test_module_naming`)
  - 1 static analysis test inverted (`test_gen_registry.py` — now asserts fix present)

### D2. Dead code identified for 7.4 removal

- **`teax_module_stub.py.jinja2`** — confirmed dead (C21 finding). Zero references in
  any Python source file. Safe to delete.
- **Extraction imports in generation files** — C19 documented 9 generation files that
  import from `extraction/` or `analysis/`. This is the baseline for 7.6. The C19 test
  `test_generation_extraction_import_count` asserts violations > 0; Phase 7.6 must
  invert this when it achieves zero violations.

### D3. Baseline comparison helper duplication

- `_compare_graph_to_baseline()` exists in both `test_graph_assembly.py` (C18) and
  `test_pipeline_e2e.py` (5.2). Plan notes: extract to shared helper if 3rd consumer
  appears. Phase 7 is unlikely to create a 3rd consumer, so this is acceptable debt.

### D4. Registry alias format differs from design doc examples

- C24 learning: Real output uses lowercase element names (e.g.,
  `SolarArray_capital_costModule`), not the PascalCase shown in
  `20-module-registry-generation.md` examples. Cosmetic-only; no functional impact.
  Consider updating doc examples if editing that doc during Phase 7.

---

## E. Test Quality Concerns

### E1. Partial Model Parametrization

Several Phase 6 tests parametrize over 4 models but only assert detailed properties
on the first 1-2 models:

- `test_gen_pipeline_yaml.py`: REQ-PY-04/05/06/07 only tested on solar_battery +
  catf_mfe (chain_spike, attr_expr_probe excluded from detailed assertions)
- `test_gen_module_wrappers.py`: `TestInputNamesMatchCalcDef` only tests first model
- `test_gen_schemas.py`: `TestFieldNamesMatchOutputAttributes` only tests first model;
  REQ-OSR-06 only tested on first model for aggregation/FORMULA
- `test_gen_registry.py`: `TestAggregationPathsDesignScoped` has hard-coded
  `len(agg_imports) == 20` for solar_battery

**Risk**: Low — solar_battery is the most complex model (all 3 module types) and
exercises the most code paths. chain_spike and attr_expr_probe are simpler models
that don't exercise generation edge cases.

**Recommendation**: No action needed before Phase 7. If a future model is added that
exercises generation differently, extend the parametrized assertions.

### E2. Fragile String Parsing in Assertions

- `test_gen_pipeline_yaml.py:379`: `rsplit(" ", 1)` for type parsing — could fail if
  exit point type contains spaces
- `test_gen_module_wrappers.py:415`: regex `ModuleBase[...]` search doesn't handle
  line breaks
- `test_gen_stencils.py:849`: String search for `"stats[\"preserved\"]"` for branch
  detection

**Risk**: Low — these parse known template outputs with predictable formats. The
assertions work today and are protected by the session-scoped graph fixtures.

**Recommendation**: No action needed. If a template change breaks these, the error
messages are clear enough to diagnose.

### E3. Session-Scoped Fixture Staleness

All Phase 6 tests use session-scoped `build_full_graph_from_snapshot()` fixtures.
If extraction pipeline code changes during a test session, the graph fixtures are
NOT refreshed. This is by design (performance), but could mask regressions if
someone modifies graph_builder.py and runs only Phase 6 tests.

**Risk**: Low — the full test suite runs all phases in order, and Phase 0-4 tests
catch extraction/resolution regressions before Phase 6 tests execute.

**Recommendation**: No action needed. The test ordering provides implicit protection.

---

## F. Gaps in Implementation

### F1. X01 Type Mapping — FORMULA and Aggregation Not Verified

`test_type_mapping_consolidation.py::TestCrossGeneratorConsistency` only checks
CalcUsage modules. FORMULA and aggregation modules derive types differently
(hardcoded `python_type="float"` in graph_builder), so cross-generator consistency
is not verified for those paths.

**Risk**: Low — FORMULA and aggregation modules are always single-output with
`field_name="root"` and `python_type="float"`. The type mapping is irrelevant for
these because the graph builder sets the type directly.

**Recommendation**: No action needed. The FORMULA/aggregation type path is
fundamentally different (graph-builder-determined, not SysML-type-mapped).

### F2. No Error Path Testing in Generation Layer

Phase 6 tests only verify the happy path (valid ComputationGraph → correct output).
No tests cover:
- Malformed PipelineModule inputs
- Missing attributes or type mismatches
- Generators receiving empty module lists

**Risk**: Low — the ComputationGraph contract is enforced by Phase 4-5 tests.
Generators receive validated data by construction.

**Recommendation**: No action needed for Phase 7 (structural refactoring).
Consider adding defensive tests if the generation layer is later exposed as a
public API.

---

## G. Phase 7 Planning Impact

### G1. Recommended Execution Order for Phase 7

Based on Phase 5+6 findings, the following ordering minimizes cascade:

1. ~~**7.5a** (Bug 8a remainder)~~ **DONE 2026-02-19.** Fixed `graph_builder.py:970-972`:
   `derive_module_type(agg.module_eqn.replace("__", "::"))` replaces
   `derive_module_type(f"{agg.expression.owning_part_qn}::{agg.expression.attribute_name}")`.
   All 20 solar_battery aggregation module_types now design-scoped and consistent with
   registry.py. Cascade resolved: 3 baselines regenerated (ComputationGraph JSON + YAML
   for solar_battery, attr_expr_probe, chain_spike), 1 unit test assertion updated
   (`test_graph_builder_aggregation.py::test_module_naming`), 1 static analysis test
   inverted (`test_gen_registry.py::TestGraphBuilderModuleTypeConsistency` — now asserts
   fix is present, not that bug exists). 1753 tests pass, 0 failures, 6 xfailed (unchanged).
2. **7.5** (C26 PipelineModule Field Expansion) — Next, since it also touches
   PipelineModule construction in graph_builder.
3. **7.4** (Dead code removal) — Delete `teax_module_stub.py.jinja2`, bare-name
   handling, Strategy B dead path, Step 3.6 alias heuristic.
4. **7.1** (Extract orchestration/) — Move `build_pipeline_context()` and friends.
5. **7.3** (Consolidate naming utilities) — Merge qualified_names, identifier_types.
6. **7.6** (Generation only consumes ComputationGraph) — The big one: migrate all 9
   violating generation files to consume PipelineModule fields instead of extraction
   models. This is where C26 field expansion pays off.
7. **7.7** (Factory purity) — Refactor C15/C16 to return EPs instead of mutating.
8. **7.2** (Extract input_resolver) — Already done (C12 created
   `resolution/input_resolver.py`). Verify no remaining inline code in graph_builder.

### G2. Bug 11 Fix Timing

Bug 11 (output field defaults) is tracked as xfail in C22 but not listed in any
Phase 7 sub-item. Options:
- Fix as part of 7.6 (when migrating schemas.py to consume ComputationGraph)
- Fix as standalone pre-7 bug fix (simpler, low risk)
- Add as explicit 7.x item

**Recommendation**: Fix as standalone item before 7.6. The fix is small (strip
defaults before rendering) and enables the xfail test, reducing noise.

### G3. Ruff Lint Debt (Carried from Phase 2 Audit D2)

Still open from Phase 2 audit: 19 ruff errors across `src/` (7 auto-fixable I001,
12 E501/UP037). None in Phase 5-6 modified files. Consider addressing as a
pre-Phase-7 cleanup commit.

### G4. TRR Validation Criteria E1-E3 (Carried from Phase 2 Audit)

Still open from Phase 2 audit:
- **E1**: Systematic REQ cross-reference audit (spot-check only done)
- **E2**: Typed identifier consistency across all docs
- **E3**: No orphan requirement references

These are documentation quality checks, not blockers. Consider addressing during
Phase 7 documentation cleanup.

---

## H. Accumulated xfail Inventory

| Test | xfail Reason | Component | Fix Target |
|------|-------------|-----------|------------|
| `test_computed_attributes::TestInheritedAttrClassification` (5 tests) | Inherited attr misclassification — FORMULA→EXPOSE_COMPUTED | C05 | Deferred Issue #9 |
| `test_gen_schemas::test_output_fields_have_no_defaults` (1 test) | Bug 11 — Permitting_Interconnect defaults on outputs | C22 | Phase 7 or pre-7 fix |

**Total**: 6 xfailed tests. All documented with clear root causes and fix targets.

---

## I. Production Code Changes Summary (Phase 5+6)

### Phase 5: Zero production code changes (conformance-only)

### Phase 6: Changes to 7 production files

| File | Change Type | Lines Changed | Triggered By |
|------|------------|---------------|--------------|
| `resolution/graph_builder.py` | Bug fix | +9 (Step 6.9), 1 modified (int→float) | C20 (Bug 9, 10) |
| `generation/registry.py` | Bug fix + refactor | +70 (collision detection), 1 modified (owning_part_qn→module_eqn) + import removal | C24 (Bug 8a, 8b) + X01 |
| `generation/type_mapping.py` | New file | +83 lines | X01 |
| `generation/entry_point.py` | Refactor | -27 lines (removed `_map_input_type`), +1 import, 3 call sites updated | X01 |
| `generation/modules.py` | Refactor | -28 lines (removed `_map_input_type`), +1 import, 1 call site updated | X01 |
| `generation/schemas.py` | Refactor | -44 lines (removed both `_map_*` functions), +1 import, 2 call sites updated | X01 |
| `generation/stencils.py` | Refactor | -23 lines (removed `_map_input_type`), +1 import, 1 call site updated | X01 |

**Net**: +83 new, -122 removed from duplicated functions = **-39 net lines** of
production code (ignoring bug fix additions). Clean consolidation.

---

## Progress Tracking

| Date | Items Completed | By |
|------|----------------|----|
| 2026-02-19 | Audit performed, action items written | Phase 5+6 checkpoint review |
| 2026-02-19 | A1-A7, B1-B2 all completed | Post-audit action session |
