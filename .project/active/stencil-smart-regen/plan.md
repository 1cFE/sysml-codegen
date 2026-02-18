# Component: Stencil Generator + Smart Regen (C23)

**Status**: DONE
**Created**: 2026-02-18
**Last updated**: 2026-02-18
**Updated by**: Build agent (Phase 6, step 6.5)

## Source Documents

- **Checklist entry**: `COMPONENT_CHECKLIST.md` — C23
- **Design intent**: [08-generation.md](../../concepts/refactor-design-intent/08-generation.md) (REQ-GEN-04), [23-smart-regen-preservation.md](../../concepts/refactor-design-intent/23-smart-regen-preservation.md) (REQ-SR-01 through REQ-SR-07)
- **Requirements**: REQ-GEN-04, REQ-SR-01 through REQ-SR-07
- **Depends on**: C20, C21, C22 (all complete); C24 (complete)

---

## 1. Assessment

### What This Component Does

The stencil generator produces `handwritten/*_impl.py` files for each CalcDef: auto-implemented code for FULLY_COMPILABLE defs, NotImplementedError stubs for all others. Smart regen (preservation.py) compares function signatures to preserve handwritten implementations when the interface hasn't changed, upgrades stubs to auto-impl when conditions are met, and creates backups before any regeneration. Aggregation and FORMULA modules are always regenerated (bypass smart regen).

### Current State

- **Exists?** Yes:
  - `generation/stencils.py` (578 lines) — `generate_implementation()`, `generate_implementation_stencil()`, `_build_stencil_context()`, `_build_auto_impl_context()`, `_map_input_type()`, `generate_backlog_report()`
  - `generation/preservation.py` (99 lines) — `should_regenerate_stencil()`, `backup_implementation()`
  - `analysis/signature_extractor.py` (247 lines) — `FunctionSignature`, `extract_signature_from_impl()`, `generate_expected_signature()`
  - `cli/__init__.py` lines 617-711 — `_generate_implementation_stencils()` with smart regen logic
  - `cli/__init__.py` lines 331-400 — `_generate_computed_attr_stencils()` (always regenerated)
  - `cli/__init__.py` lines 517-600 — `_generate_aggregation_stencils()` (always regenerated)
  - Templates: `implementation_stencil.py.jinja2`, `auto_implementation.py.jinja2`
- **Needs extraction/refactoring?** No — conformance tests only.
- **Current test coverage**: `tests/unit/test_stencils.py` — unit tests with synthetic CalculationDefinitionData. No conformance tests with real fixture data yet.

### Design Consistency Check

- [x] All acceptance criteria from COMPONENT_CHECKLIST are testable with real data (no mocks)
- [x] AC are consistent with the requirements in the design intent doc(s)
- [x] No contradictions with other component specs
- [x] Input/output interfaces match what upstream/downstream components expect
- [x] Any ambiguities or gaps identified and resolved (documented below)

**Issues found during review:**

1. **Snapshot limitation for compilation_results**: Extraction snapshots have `compilation_results=None` (AST fields nullified — Phase 0 Learning #2). `generate_implementation()` with `compilation_result=None` always produces stubs. To test FULLY_COMPILABLE auto-impl with real data, we need either (a) live extraction (like C04), or (b) construct `CalcDefCompilationResult` objects from snapshot calc_def metadata. **Resolution**: Use approach (b) — construct minimal `CalcDefCompilationResult` from real calc_def output_attributes to get valid auto-impl output. The existing `test_stencils.py` unit tests already do this with synthetic data; we'll do the same with real calc_def metadata from snapshots.

2. **Smart regen requires filesystem interaction**: `should_regenerate_stencil()` reads from `impl_path` and `backup_implementation()` copies files. These test the preservation logic, not the generation logic. **Resolution**: Use `tmp_path` fixture to create real impl files on disk, then call `should_regenerate_stencil()` and `backup_implementation()` against them. This is real filesystem interaction, not mocking.

3. **`--preserve-handwritten` is a CLI config flag, not a function parameter**: The blanket skip logic lives in `_generate_implementation_stencils()` in `cli/__init__.py` (line 692), gated by `config.preserve_handwritten`. **Resolution**: Test this at the config/flag level — verify the control flow logic via static analysis (the flag gates a simple `continue` branch).

4. **Aggregation/FORMULA bypass (REQ-SR-06)**: `_generate_aggregation_stencils()` and `_generate_computed_attr_stencils()` in cli/__init__.py never reference `smart_regen` or `should_regenerate_stencil`. **Resolution**: Static analysis test verifying these functions don't call smart-regen APIs. Same pattern as C07/C19.

5. **REQ-SR-04 (stub upgrade) logic lives in cli/__init__.py, not preservation.py**: The 3-condition check is inline at lines 672-688. **Resolution**: Test the conditions directly with real calc_def data + constructed compilation_result + real stencil output on disk.

### Risks & Unknowns

- **Low risk**: The stencil generator is well-tested at the unit level. Conformance tests add real-data coverage.
- **No unknowns requiring spike**: The design is clear, the code matches the design doc, and the testing approach is straightforward.

---

## 2. Spike

**Decision**: SKIP
**Rationale**: The stencil generator and smart regen code closely match the design doc descriptions. The code paths are well-understood from unit tests. The snapshot limitation for compilation_results has a clear workaround (construct from real calc_def metadata). No unknowns to resolve.

---

## 3. Test Plan

**Test file**: `tests/conformance/test_gen_stencils.py`
**Fixture data**: solar_battery_model (8 CalcUsage, mixed compilability), catf_mfe_model (42 CalcUsage, all CalcUsage)

### Test Cases

> Every requirement (REQ-XX-NN) must have at least one test case.
> Every test uses real data — no mocks. Stubs only at SysIDE adapter boundary.

| Test | Requirement | What it verifies |
|------|-------------|------------------|
| `test_req_gen_04_fully_compilable_produces_auto_impl[solar_battery]` | REQ-GEN-04 | generate_implementation() with FULLY_COMPILABLE compilation_result produces code containing `AUTO_IMPLEMENTED = True` sentinel and no `NotImplementedError` |
| `test_req_gen_04_non_compilable_produces_stub[solar_battery]` | REQ-GEN-04 | generate_implementation() with compilation_result=None produces `raise NotImplementedError(...)` |
| `test_req_gen_04_stencil_valid_python[solar_battery]` | REQ-GEN-04 | Both auto-impl and stub output pass `ast.parse()` |
| `test_req_gen_04_stencil_function_signature[solar_battery]` | REQ-GEN-04 | Generated function has `run_{name}(inputs: {Name}Input) -> {return_type}` matching calc_def |
| `test_req_gen_04_multi_output_return_type[solar_battery]` | REQ-GEN-04 | CalcDefs with 2+ outputs produce `tuple[float, ...]` return type in generated code |
| `test_req_sr_01_two_level_signature_matching` | REQ-SR-01 | FunctionSignature.matches() uses type-level (function_name, input_type, return_type) as required, field-level (input_fields sorted) as optional |
| `test_req_sr_02_field_comparison_order_independent` | REQ-SR-02 | Two signatures with same fields in different order return matches()=True |
| `test_req_sr_03_decision_tree_case1_new_file` | REQ-SR-03 | should_regenerate_stencil() returns (True, "New module...") for non-existent path |
| `test_req_sr_03_decision_tree_case2_unparseable` | REQ-SR-03 | should_regenerate_stencil() returns (True, "Could not parse...") for file with syntax errors |
| `test_req_sr_03_decision_tree_case3_unchanged` | REQ-SR-03 | should_regenerate_stencil() returns (False, "Signature unchanged") for file matching expected signature |
| `test_req_sr_03_decision_tree_case4_changed` | REQ-SR-03 | should_regenerate_stencil() returns (True, "Signature changed...") for file with different return type |
| `test_req_sr_04_stub_upgrade_three_conditions[solar_battery]` | REQ-SR-04 | With real calc_def: (1) generate stub → (2) construct FULLY_COMPILABLE result → (3) verify stub content has NotImplementedError → upgrade to auto-impl. All 3 conditions exercised with real data. |
| `test_req_sr_04_handwritten_not_upgraded[solar_battery]` | REQ-SR-04 | Handwritten impl (no NotImplementedError) is NOT upgraded even if FULLY_COMPILABLE |
| `test_req_sr_05_backup_before_regen` | REQ-SR-05 | backup_implementation() creates timestamped file in backup_dir preserving original content |
| `test_req_sr_05_backup_preserves_content` | REQ-SR-05 | Backup file content matches original exactly (shutil.copy2) |
| `test_req_sr_06_aggregation_no_smart_regen` | REQ-SR-06 | Static analysis: `_generate_aggregation_stencils()` source does not reference `should_regenerate_stencil`, `smart_regen`, or `backup_implementation` |
| `test_req_sr_06_computed_attr_no_smart_regen` | REQ-SR-06 | Static analysis: `_generate_computed_attr_stencils()` source does not reference `should_regenerate_stencil`, `smart_regen`, or `backup_implementation` |
| `test_req_sr_07_preserve_handwritten_flag` | REQ-SR-07 | Static analysis: `_generate_implementation_stencils()` has `config.preserve_handwritten and output_path.exists()` branch that skips without calling `should_regenerate_stencil` |
| `test_generate_expected_signature_matches_stencil[solar_battery]` | REQ-SR-01 | For each CalcUsage calc_def, `generate_expected_signature(calc_def)` produces a FunctionSignature whose function_name, input_type, return_type match what `generate_implementation()` produces |
| `test_stencil_import_path_consistency[solar_battery]` | REQ-GEN-04 | Generated stencil imports from `{package_name}.modules.{import_path}` where import_path matches PythonModulePath.from_sysml() |

### Test Infrastructure Needed

1. **Session-scoped fixtures**: Reuse `build_full_graph_from_snapshot()` from `test_entry_point_classifier.py` and `_build_calcusage_module_to_calcdef_map()` from `test_gen_module_wrappers.py` to get real calc_defs.
2. **Template env fixture**: Same pattern as C20/C21/C22 — `jinja2.Environment(loader=FileSystemLoader(TEMPLATE_DIR))`.
3. **Compilation result construction helper**: `_make_fully_compilable_result(calc_def)` that builds a minimal `CalcDefCompilationResult` with `overall_compilability=FULLY_COMPILABLE` and `output_results` from real calc_def output_attributes. This is NOT a mock — it's constructing a real Pydantic model with data derived from real extraction snapshots.
4. **tmp_path usage**: For smart regen tests (REQ-SR-03, REQ-SR-04, REQ-SR-05), write generated stencils to `tmp_path` then test decision logic against them.

### Gate: Ready for BUILD
- [x] Test file exists with all test cases written
- [x] Tests run (all 30 PASS — conformance-only component)
- [x] No test uses mocking (verified by grep for `mock`, `patch`, `MagicMock`)

---

## 4. Build Plan

### Files to Modify
| File | Change | Why |
|------|--------|-----|
| (none) | No production code changes | Conformance-only component |

### Files to Create
| File | Purpose |
|------|---------|
| `tests/conformance/test_gen_stencils.py` | C23 conformance tests (~20 test cases) |

### Implementation Notes

1. **Parametrization**: Use `solar_battery_model` as primary fixture (has mixed module types). `catf_mfe_model` as secondary (42 CalcUsage, 100% coverage by stencil generator). Tests parametrized with `@pytest.mark.parametrize("model_name", PARAMETRIZED_MODELS, ...)`.

2. **Compilation result construction**: For `test_req_gen_04_fully_compilable_produces_auto_impl`, construct a `CalcDefCompilationResult` with:
   - `overall_compilability = Compilability.FULLY_COMPILABLE`
   - `output_results` = one `CompilationResult` per output_attribute with `python_expression = f"inputs.{input_attrs[0].name} * 1.0"` (valid but synthetic expression derived from real attribute names)
   - `execution_order` = list of output attribute names
   This exercises the auto-impl template code path with a structurally valid compilation result.

3. **Smart regen filesystem tests**: Use `tmp_path` to write a generated stub, then:
   - Call `should_regenerate_stencil(calc_def, tmp_path / "impl.py")` — should return (False, "Signature unchanged")
   - Modify the file to change the return type — should return (True, "Signature changed")
   - Delete the file — should return (True, "New module")
   - Write invalid Python — should return (True, "Could not parse")

4. **Static analysis pattern**: Same approach as C07, C19 — `inspect.getsource()` + search for string patterns. Verify:
   - `_generate_aggregation_stencils` doesn't contain `should_regenerate_stencil` or `smart_regen`
   - `_generate_computed_attr_stencils` doesn't contain `should_regenerate_stencil` or `smart_regen`
   - `_generate_implementation_stencils` DOES contain `preserve_handwritten` branch

5. **No baseline changes**: This is conformance-only — no production code modifications expected.

### Gate: Ready for VALIDATE
- [x] All test cases pass (30 passed)
- [x] No regressions in full test suite (1705 passed, 2 skipped, 6 xfailed)
- [x] Lint clean (test file clean; src/ has 19 pre-existing errors)

---

## 5. Validation

- [x] Every acceptance criterion from COMPONENT_CHECKLIST is satisfied
  - [x] FULLY_COMPILABLE gets auto-impl; others get stubs (REQ-GEN-04)
  - [x] Two-level signature matching: type-level required, field-level order-independent (REQ-SR-01, REQ-SR-02)
  - [x] 4-case decision tree for should_regenerate_stencil (REQ-SR-03)
  - [x] Stub-to-auto-impl upgrade requires 3 conditions (REQ-SR-04)
  - [x] Backup before every regen/upgrade (REQ-SR-05)
  - [x] Aggregation/FORMULA modules always regenerated (REQ-SR-06)
  - [x] --preserve-handwritten skips without comparison (REQ-SR-07)
- [x] Every REQ has at least one passing test
- [x] Full test suite passes (record count: 1705 tests, 0 failures)
- [x] Cross-check: re-read design intent doc, verify implementation matches
- [x] No unresolved TODOs or FIXMEs in new/modified code
- [x] COMPONENT_CHECKLIST and IMPLEMENTATION_PLAN have been updated

### Baseline Impact
No baseline changes expected — conformance tests only.

---

## 6. Learnings

### Findings

1. **All 30 tests pass on first run.** Conformance-only component — no production code changes needed. The stencil generator, smart regen logic, and signature comparison all behave as documented in design intent docs 08-generation.md and 23-smart-regen-preservation.md.

2. **catf_mfe exercises multi-output CalcDef stencils.** Both solar_battery and catf_mfe have multi-output calc_defs that exercise the `tuple[float, ...]` return type path.

3. **`_make_fully_compilable_result()` helper reuses the C04/unit test pattern.** Constructs real `CalcDefCompilationResult` from real calc_def metadata (attribute names, output counts). The same approach as `test_stencils.py` but with real calc_def data instead of synthetic.

4. **CLI function renamed from `_generate_implementation_stencils` to `_generate_stencils`.** The plan referenced the old name; the actual function is `_generate_stencils` in cli/__init__.py (line 612). Tests updated accordingly.

### Design Doc Updates Needed
| Doc | What to update | Why |
|-----|---------------|-----|
| (none) | No updates needed | All design docs accurate |

### Cross-Component Impact
| Component | Impact | Action needed |
|-----------|--------|---------------|
| (none) | No impact | Conformance-only |

### Deviations from Plan

1. **Plan listed 20 test cases; actual is 30.** The plan counted unique test names but each parametrized test runs once per model (solar_battery + catf_mfe). 20 unique test functions × parametrization = 30 collected test items. This matches the C20-C22 pattern.

2. **REQ-SR-02 has an extra test.** Added `test_req_sr_02_field_mismatch_returns_false` to verify the negative case (different fields → matches()=False). Not listed in plan but strengthens coverage.

---

## 7. Commit

**Branch**: `cost-pattern-refactor` (continuing)
**Commit convention**: one commit per component, message references component code

- [x] All validation checks above are green
- [ ] `git add` only the files listed in Build Plan + test file, plus IMPLEMENTATION_PLAN and COMPONENT_CHECKLIST (no unrelated changes)
- [ ] Commit message format:
  ```
  refactor(C23): Stencil Generator + Smart Regen conformance tests

  - Tests: 30 new conformance tests in tests/conformance/test_gen_stencils.py
  - Refs: REQ-GEN-04, REQ-SR-01 through REQ-SR-07
  - Design intent: 08-generation.md, 23-smart-regen-preservation.md
  ```
- [ ] Committed successfully

---

## Progress Log

### Session: 2026-02-18 — Planning
**Phase**: PLANNING
**Work done**:
- Read design intent docs (08-generation.md REQ-GEN-04, 23-smart-regen-preservation.md REQ-SR-01 through REQ-SR-07)
- Read component checklist C23 (7 AC)
- Read implementation plan step 6.5
- Read current source: `generation/stencils.py` (578 lines), `generation/preservation.py` (99 lines), `analysis/signature_extractor.py` (247 lines)
- Read CLI generation functions: `_generate_implementation_stencils()` (lines 617-711), `_generate_computed_attr_stencils()` (lines 331-400), `_generate_aggregation_stencils()` (lines 517-600)
- Read templates: `implementation_stencil.py.jinja2`, `auto_implementation.py.jinja2`
- Read existing unit tests: `tests/unit/test_stencils.py`
- Reviewed C20, C21, C22 learnings and test patterns
- Identified 5 design consistency issues and documented resolutions
- Design consistency check: all 5 items pass
**Stopped at**: Plan complete, ready for build
**Next step**: Build the conformance test file
**Blockers**: None

### Session: 2026-02-18 — Build + Validate
**Phase**: PLANNING → DONE (all phases in one session)
**Work done**:
- Wrote `tests/conformance/test_gen_stencils.py` (30 test cases)
- All 30 tests pass on first run (conformance-only — no production code changes)
- Full suite: 1705 passed, 2 skipped, 6 xfailed
- Lint clean (test file)
- Verified no mocks (grep for mock/patch/MagicMock)
- Verified no TODOs/FIXMEs
- All 8 requirements covered: REQ-GEN-04, REQ-SR-01 through REQ-SR-07
- All 7 acceptance criteria satisfied
- Cross-checked against design intent docs
- Updated COMPONENT_CHECKLIST.md and IMPLEMENTATION_PLAN.md
**Stopped at**: DONE — ready for commit
**Next step**: Commit
**Blockers**: None
