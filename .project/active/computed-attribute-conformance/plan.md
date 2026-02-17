# Component: Computed Attribute Classification Conformance (C05)

**Status**: DONE
**Created**: 2026-02-17
**Last updated**: 2026-02-17
**Updated by**: Build agent

## Source Documents

- **Checklist entry**: `COMPONENT_CHECKLIST.md` -- C05
- **Design intent**: [16-computed-attributes.md](../../concepts/refactor-design-intent/16-computed-attributes.md)
- **Requirements**: REQ-CA-01 through REQ-CA-07
- **Depends on**: C01 (data models -- complete), C03 (extractor -- complete), C04 (expression compiler -- complete), Phase 0 (snapshots -- complete)

---

## 1. Assessment

### What This Component Does

The computed attribute extractor (`extraction/computed_attribute_extractor.py`) classifies
PartDef/PartUsage attribute expressions into one of 5 categories (FORMULA, EXPOSE_PURE,
EXPOSE_COMPUTED, LITERAL, UNRESOLVABLE) and compiles FORMULA patterns to Python. It consumes
raw SysIDE AST nodes + ExpressionRef data and produces `ComputedAttributeData` + `ChannelAlias`
objects. Downstream, `_build_attribute_resolution_map()` in `graph_builder.py` maps each FORMULA
input to an `AttributeResolutionKind` for wiring.

### Current State
- **Exists?** Yes, fully implemented:
  - `extraction/computed_attribute_extractor.py` (276 LOC) -- classifier + compiler orchestration
  - `extraction/data_models.py` lines 164-218 -- `ComputedAttributeClassification` enum + `ComputedAttributeData` dataclass
  - `resolution/graph_builder.py` lines 526-638 -- `AttributeResolutionKind`, `AttributeResolution`, `_build_attribute_resolution_map()`
- **Needs extraction/refactoring?** No. Code is stable. Conformance tests only.
- **Current test coverage**:
  - `tests/unit/test_computed_attribute_extraction.py` (716 LOC): 10 tests using mock SysIDE objects for classification + compilation
  - `tests/unit/test_computed_attr_generation.py`: generation-level tests
  - `tests/integration/test_computed_attributes_e2e.py`: E2E tests
  - `tests/integration/test_computed_attribute_pipeline.py`: pipeline integration
  - No conformance tests against real snapshot data yet

### Design Consistency Check

- [x] All acceptance criteria from COMPONENT_CHECKLIST are testable with real data (no mocks)
- [x] AC are consistent with the requirements in the design intent doc (16-computed-attributes.md)
- [x] No contradictions with other component specs
- [x] Input/output interfaces match what upstream/downstream components expect
- [x] Any ambiguities or gaps identified and resolved (documented below)

**Issues found during review:**

1. **No UNRESOLVABLE attribute in any fixture model.** All 6 fixture models have zero
   UNRESOLVABLE computed attributes. REQ-CA-05 cannot be tested with snapshot data directly.
   **Resolution**: Test the _absence_ of UNRESOLVABLE from all snapshots (confirming real
   models don't produce it) plus test the negative invariant: no alias exists for any
   non-EXPOSE_PURE classification. The existing unit test (`test_unresolvable` in
   `test_computed_attribute_extraction.py`) covers the algorithm with mock data. Document
   as a coverage gap like C03's EXPRESSION binding type gap.

2. **Only solar_battery has `is_on_part_definition: true` EXPOSE_PURE.** This is the sole
   test of REQ-CA-03 (PartDef guard). attr_expr_probe's `probe_design` is a PartUsage.
   **Resolution**: Use solar_battery snapshot for PartDef guard test. Verify that
   `is_on_part_definition=true` EXPOSE_PURE attributes have NO corresponding ChannelAlias.

3. **REQ-CA-06 (AttributeResolutionKind) lives in graph_builder.py, not extractor.** This
   tests `_build_attribute_resolution_map()` which is in the resolution layer, not extraction.
   The function requires an OutputRegistry which involves infrastructure not yet conformance-tested
   (C08). **Resolution**: Build a minimal OutputRegistry from snapshot data for this test.
   This is valid because we're testing the classification logic, not the registry itself.
   Alternatively, scope REQ-CA-06 to verify the map is constructable with real data and
   produces the correct kind for each attribute. This is a lightweight spike-free approach.

4. **REQ-CA-08 in design doc not in COMPONENT_CHECKLIST.** Doc 16 has REQ-CA-08
   (FORMULA-to-FORMULA limitation: `output_names=set()`). It's not in the checklist REQ list
   (CA-01 through CA-07) but is in the design doc. **Resolution**: Test this as a bonus
   (not required for conformance sign-off). Verify that FORMULA chain attrs (like `cost`
   referencing computed `area`) compile `area` as `inputs.area` (an input ref, not an output
   ref), confirming the `output_names=set()` behavior.

### Risks & Unknowns

- **Low risk**: The extractor is stable and well-tested with unit tests. Conformance tests
  are additive validation, not discovery.
- **AST serialization boundary**: `expression_ast` is null in all snapshots. Tests cannot
  re-run `_classify_attribute_expression()` from snapshot data alone (the function needs
  real AST for EXPOSE_PURE detection). Tests validate the _output_ of classification, not
  the algorithm's internal AST checks.

---

## 2. Spike

**Decision**: SKIP
**Rationale**: The extractor is fully implemented and stable. All 6 fixture model snapshots
contain computed attribute data. The snapshot data structure is well-understood from Phase 0
and C03. No unknowns about the data format or test approach. The only limitation (no
UNRESOLVABLE fixture data) is a known gap from the design review, not a blocker.

---

## 3. Test Plan

**Test file**: `tests/conformance/test_computed_attributes.py`
**Fixture data**: attr_expr_probe (primary), solar_battery_model (PartDef guard), catf_mfe_model (cross-model validation)

### Test Cases

> Every requirement (REQ-CA-NN) must have at least one test case.
> Every test uses real snapshot data -- no mocks. The computed_attributes list and
> channel_aliases list in each snapshot are the real extraction output.

| Test | Requirement | What it verifies |
|------|-------------|------------------|
| `test_req_ca_01_classification_exhaustive` | REQ-CA-01 | Every `ComputedAttributeData` in attr_expr_probe has a classification value that is a valid `ComputedAttributeClassification` enum member |
| `test_req_ca_01_classification_exclusive` | REQ-CA-01 | Each attribute has exactly one classification (enum, not multi-valued); verify all 18 attrs in attr_expr_probe each have one value |
| `test_req_ca_01_all_five_values_defined` | REQ-CA-01 | The `ComputedAttributeClassification` enum has exactly 5 members: FORMULA, EXPOSE_PURE, EXPOSE_COMPUTED, LITERAL, UNRESOLVABLE |
| `test_req_ca_01_fixture_coverage` | REQ-CA-01 | attr_expr_probe exercises 3 of 5 classifications (FORMULA, EXPOSE_PURE, EXPOSE_COMPUTED); LITERAL is excluded by design (not in list); UNRESOLVABLE absent (coverage gap) |
| `test_req_ca_02_formula_compiles_to_python` | REQ-CA-02 | Every FORMULA attribute in attr_expr_probe has a non-None `compiled_expression` and `compilability == FULLY_COMPILABLE` |
| `test_req_ca_02_formula_ast_parse` | REQ-CA-02 | Every FORMULA `compiled_expression` from attr_expr_probe passes `ast.parse()` -- produces valid Python |
| `test_req_ca_02_formula_compilation_cross_model[solar_battery]` | REQ-CA-02 | Every FORMULA in solar_battery_model has valid compiled_expression that passes ast.parse() |
| `test_req_ca_02_formula_inputs_prefix` | REQ-CA-02 | Every variable reference in FORMULA compiled_expressions uses `inputs.` prefix (no bare names) |
| `test_req_ca_03_expose_pure_partusage_only` | REQ-CA-03 | solar_battery has EXPOSE_PURE with `is_on_part_definition=true` -- verify no ChannelAlias exists for that attribute; attr_expr_probe EXPOSE_PURE attrs (all PartUsage-level) DO have aliases |
| `test_req_ca_03_expose_pure_alias_count` | REQ-CA-03 | Number of channel_aliases with `source="expose_pure"` equals number of EXPOSE_PURE attrs with `is_on_part_definition=false` in attr_expr_probe |
| `test_req_ca_04_literal_excluded` | REQ-CA-04 | No `ComputedAttributeData` in any fixture model has `classification == LITERAL`; LITERAL attributes stay in `design_attributes`, not `computed_attributes` |
| `test_req_ca_04_literal_attr_not_in_aliases` | REQ-CA-04 | Known literal attribute names (length, width, height, rate, markup) from attr_expr_probe do NOT appear as alias_name in channel_aliases |
| `test_req_ca_05_unresolvable_no_alias` | REQ-CA-05 | No ChannelAlias in any fixture model has a classification-correlated entry for UNRESOLVABLE or EXPOSE_COMPUTED attrs; only EXPOSE_PURE produces aliases |
| `test_req_ca_05_unresolvable_coverage_gap` | REQ-CA-05 | Document: no UNRESOLVABLE attrs in any fixture model; zero computed_attributes with classification=="unresolvable" across all 6 models |
| `test_req_ca_06_resolution_kind_enum` | REQ-CA-06 | `AttributeResolutionKind` has exactly 3 values: FORMULA, EXPOSE_ALIAS, LITERAL |
| `test_req_ca_06_resolution_map_from_real_data` | REQ-CA-06 | Build `_build_attribute_resolution_map()` with attr_expr_probe computed_attributes + design_attrs; verify FORMULA attrs produce FORMULA kind, EXPOSE_PURE attrs produce EXPOSE_ALIAS kind, remaining attrs produce LITERAL kind |
| `test_req_ca_07_self_reference_excluded` | REQ-CA-07 | For every FORMULA in attr_expr_probe, `compiled_expression` does not contain `inputs.{self_python_name}` (e.g., `area`'s expression doesn't contain `inputs.area`) |
| `test_req_ca_07_self_reference_chain_attrs` | REQ-CA-07 | Chain attrs (cost, marked_up_cost, cost_density) reference computed siblings but NOT themselves in compiled_expression |
| `test_classification_counts_attr_expr_probe` | -- | Exact counts: 14 FORMULA, 1 EXPOSE_COMPUTED, 3 EXPOSE_PURE in attr_expr_probe snapshot |
| `test_expose_pure_alias_canonical_name` | REQ-CA-03 | Each EXPOSE_PURE alias has canonical_name format `"{instance}.{output}"` (e.g., `scale_calc.result`, `split.half`) |
| `test_formula_compiled_expressions_known_good` | REQ-CA-02 | Parametrize over all 14 FORMULA attrs in attr_expr_probe; verify compiled_expression matches expected values from snapshot (regression guard) |
| `test_expose_computed_no_compilation` | REQ-CA-01 | EXPOSE_COMPUTED attrs have `compiled_expression is None` and `compilability == MANUAL_REQUIRED` |
| `test_expose_pure_no_compilation` | REQ-CA-01 | EXPOSE_PURE attrs have `compiled_expression is None` and `compilability == MANUAL_REQUIRED` |
| `test_cross_model_catf_mfe` | -- | catf_mfe_model computed_attributes all have valid classification, EXPOSE_PURE attrs all on PartUsage (is_on_part_definition=false) |

### Test Infrastructure Needed

- `attr_expr_probe_snapshot` fixture from conftest.py (already exists)
- `solar_battery_snapshot` fixture from conftest.py (already exists)
- `catf_mfe_snapshot` fixture from conftest.py (already exists)
- For REQ-CA-06: need to import `_build_attribute_resolution_map`, `AttributeResolutionKind`,
  `AttributeResolution` from `resolution.graph_builder` and `OutputRegistry` from `core.output_registry`.
  Build a minimal registry by registering FORMULA output channels from snapshot data.
- No new fixtures or helpers needed.

### Gate: Ready for BUILD
- [x] Test file exists with all test cases written
- [x] Tests run (37 passed in 0.09s)
- [x] No test uses mocking (verified by grep for `mock`, `patch`, `MagicMock`)

---

## 4. Build Plan

### Files to Modify
| File | Change | Why |
|------|--------|-----|
| (none) | No production code changes | C05 is conformance-only |

### Files to Create
| File | Purpose |
|------|---------|
| `tests/conformance/test_computed_attributes.py` | Conformance tests for REQ-CA-01 through REQ-CA-07 |

### Implementation Notes

1. **Snapshot-first approach**: All tests read from deserialized extraction snapshots.
   The `ComputedAttributeData` objects have `expression_ast=None` (serialization boundary)
   but all other fields are fully populated including `classification`, `compiled_expression`,
   `compilability`, `references`, `is_on_part_definition`.

2. **No algorithm re-testing**: The conformance tests validate OUTPUTS of classification,
   not the classification algorithm itself. The algorithm is tested in the existing unit tests
   with mock SysIDE objects. Conformance tests verify that real models produce expected results.

3. **ast.parse() validation**: Import Python `ast` module and call `ast.parse(compiled_expression)`
   on every FORMULA result. This confirms the expression compiler produced syntactically valid
   Python, complementing the C04 conformance tests.

4. **REQ-CA-06 build approach**: Import `_build_attribute_resolution_map` and build a minimal
   `OutputRegistry`. Register FORMULA output channels using the naming convention:
   `{owning_part}__attr_name__attr_name` (PQN format). Register EXPOSE_PURE aliases.
   Then verify the map assigns correct `AttributeResolutionKind` per attribute.

5. **Self-reference test approach**: For each FORMULA attr, check that `f"inputs.{attr.python_name}"`
   does NOT appear in `attr.compiled_expression`. This validates REQ-CA-07 at the output level.

6. **Parametrize over known-good values**: Use `@pytest.mark.parametrize` with the 14 FORMULA
   attrs from attr_expr_probe to create individual regression tests for each compiled expression.

### Gate: Ready for VALIDATE
- [x] All test cases pass (37/37)
- [x] No regressions in full test suite (991 passed, 2 pre-existing spike failures)
- [x] Lint clean (no C05-related issues; 20 pre-existing warnings in other files)

---

## 5. Validation

- [x] Every acceptance criterion from COMPONENT_CHECKLIST is satisfied
- [x] Every REQ-CA-NN has at least one passing test
- [x] Full test suite passes (record count: 993 tests, 2 pre-existing spike failures)
- [x] Cross-check: re-read design intent doc, verify implementation matches
- [x] No unresolved TODOs or FIXMEs in new/modified code

### Baseline Impact
No baseline changes expected. C05 is conformance-only; no production code modified.

---

## 6. Commit

**Branch**: `cost-pattern-refactor` (current branch)
**Commit convention**: one commit per component, message references component code

- [x] All validation checks above are green
- [x] `git add` only the files listed in Build Plan + test file (no unrelated changes)
- [x] Commit message format:
  ```
  refactor(C05): Computed Attribute Classification conformance tests

  - Tests: 37 new conformance tests in tests/conformance/test_computed_attributes.py
  - Refs: REQ-CA-01 through REQ-CA-07
  - Design intent: 16-computed-attributes.md
  ```
- [ ] Committed successfully

---

## 7. Learnings

### Findings

1. **UNRESOLVABLE confirmed absent from all 6 fixture models.** Same pattern as C03's
   EXPRESSION binding type gap. The code path is exercised by existing unit tests with
   mock data, but no real SysML model triggers it. Zero-coverage gap documented.

2. **All 14 FORMULA compiled expressions are valid Python.** `ast.parse()` succeeds on
   every compiled expression from attr_expr_probe. The parametrized regression tests
   lock down exact expression strings.

3. **REQ-CA-06 resolution map test succeeded with minimal OutputRegistry.** Building a
   lightweight registry from snapshot data (registering FORMULA channels + calc usage
   outputs) was sufficient to test `_build_attribute_resolution_map()`. No need for full
   pipeline infrastructure.

4. **Test file was written in a prior planning session.** The 37-test file was already
   present as an untracked file when this build session started. All tests passed
   immediately, confirming the plan's assessment that C05 is conformance validation
   of stable, existing behavior.

### Design Doc Updates Needed
| Doc | What to update | Why |
|-----|---------------|-----|
| 16-computed-attributes.md | Note UNRESOLVABLE has zero coverage in fixture models | Same pattern as C03 EXPRESSION binding type gap |
| COMPONENT_CHECKLIST.md | Consider adding REQ-CA-08 (FORMULA-to-FORMULA limitation) to AC list | Present in design doc but absent from checklist |

### Cross-Component Impact
| Component | Impact | Action needed |
|-----------|--------|---------------|
| C06 (Hierarchy Resolver) | None | -- |
| C07 (AST Dispatch Invariant) | C05 confirms FCE detection path works for EXPOSE_PURE | Informational only |

### Deviations from Plan

None. All 23 planned test cases implemented (expanding to 37 collected tests via parametrization).
No production code changes needed (conformance-only, as planned).

---

## Progress Log

### Session: 2026-02-17 -- Plan creation
**Phase**: PLANNING
**Work done**:
- Read all context: IMPLEMENTATION_PLAN.md, COMPONENT_CHECKLIST.md, 16-computed-attributes.md
- Read source: computed_attribute_extractor.py, data_models.py, graph_builder.py
- Analyzed all 6 fixture snapshots for computed_attributes content
- Identified 4 design consistency issues, all resolved
- Designed 23 test cases covering REQ-CA-01 through REQ-CA-07
**Stopped at**: Plan complete, ready for review
**Next step**: Build -- write tests/conformance/test_computed_attributes.py
**Blockers**: None

### Session: 2026-02-17 -- Build, validate, and commit
**Phase**: PLANNING → DONE
**Work done**:
- Found test file already written (37 tests, untracked)
- Ran C05 tests: 37/37 passed in 0.09s
- Verified no mocks (grep clean)
- Ran full suite: 991 passed, 2 pre-existing spike failures (tests/spikes/)
- Verified lint: no C05-related issues
- Cross-checked all 7 REQs against design intent doc 16-computed-attributes.md
- Cross-checked all 7 ACs against COMPONENT_CHECKLIST.md
- Updated IMPLEMENTATION_PLAN.md: marked C05 complete, added learnings, updated test count
- Committed
**Stopped at**: DONE
**Next step**: C06 (Hierarchy Resolver) or C07 (AST Dispatch Invariant)
**Blockers**: None
