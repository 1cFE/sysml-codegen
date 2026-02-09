# Implementation Plan: Pipeline Integration -- Computed Attribute Modules

**Status:** Complete
**Created:** 2026-02-09
**Last Updated:** 2026-02-09

## Source Documents
- **Spec:** `.project/active/attr-expr-pipeline/spec.md`
- **Design:** `.project/active/attr-expr-pipeline/design.md` -- See here for component details, function signatures, data structures, architecture

## Implementation Strategy

**Phasing Rationale:**
Phases follow the data flow through the pipeline: extraction (Phase 1) feeds the backtracker (Phase 2), which feeds the graph builder (Phase 3), which feeds code generation (Phase 4). Each phase produces testable output independent of downstream phases. The heaviest risk (graph builder, ~150 lines) is Phase 3 -- by then, the inputs it depends on are proven correct. Integration tests (Phase 5) run last as a holistic validation.

**Overall Validation Approach:**
- Each phase starts with tests
- `uv run pytest tests/` after every phase (182+ baseline must hold)
- `uv run mypy src/` and `uv run ruff check src/` after each phase
- Manual verification after Phase 4 using `attr_expr_probe` fixture

---

## Phase 1: Foundation -- Data Model + Step 4.5 Extraction & Filtering

### Goal
Get computed attributes into the pipeline and FORMULA attributes removed from `design_attrs`. Every downstream component depends on this. Satisfies FR-1 through FR-5, FR-15.

### Test Stencil (Write This First)
```python
# tests/unit/test_step_4_5.py

class TestFormulaRemovalFromDesignAttrs:
    """Test that FORMULA attributes are removed from design_attrs dict."""

    def test_formula_removed_expose_preserved(self):
        """FORMULA attrs removed, EXPOSE_PURE and plain design attrs kept."""
        design_attrs = {Path("test.sysml"): [
            DesignAttributeData(qualified_name="Part__area", name="area", ...),
            DesignAttributeData(qualified_name="Part__length", name="length", ...),
        ]}
        computed_attrs = [make_formula_ca("area", "Part"), make_expose_ca("eta", "Part")]
        _extract_and_filter_computed_attributes(...)
        # "area" removed (FORMULA), "length" preserved (not computed)
        remaining = design_attrs[Path("test.sysml")]
        assert len(remaining) == 1
        assert remaining[0].name == "length"

    def test_empty_computed_attrs_no_op(self):
        """No computed attrs -> design_attrs unchanged."""

    def test_formula_qn_format_matches_design_attr_qn(self):
        """Verify the QN format built from ComputedAttributeData matches DesignAttributeData.qualified_name."""
```

### Changes Required

**See `design.md` for:**
- `PipelineModule.is_computed_attribute` field -> `design.md#component-1`
- `PipelineContext.computed_attributes` field -> `design.md#component-2`
- Step 4.5 algorithm and integration -> `design.md#component-3`

**Specific file changes:**

#### 1. Test File
**File:** `tests/unit/test_step_4_5.py` (NEW - write first)
- [x] Create test file with mock helpers
- [x] Test FORMULA removal from design_attrs (QN format matching)
- [x] Test empty computed attrs is no-op
- [x] Test EXPOSE_PURE and EXPOSE_COMPUTED preserved in design_attrs

#### 2. Data Model Extension
**File:** `src/sysml_codegen/resolution/models.py:167`
- [x] Add `is_computed_attribute: bool = False` to `PipelineModule`

#### 3. PipelineContext Extension
**File:** `src/sysml_codegen/generation/initialization.py:60-91`
- [x] Add import for `ComputedAttributeData`
- [x] Add `computed_attributes: list[ComputedAttributeData] = field(default_factory=list)` field

#### 4. Step 4.5 Implementation
**File:** `src/sysml_codegen/generation/initialization.py`
- [x] Add `_extract_and_filter_computed_attributes()` function per `design.md#component-3`
- [x] Integrate into `build_pipeline_context()` between Step 4 and Step 5
- [x] Pass `computed_attrs` to `DependencyBacktracker` constructor (new kwarg, ignored until Phase 2)
- [x] Pass `computed_attrs` to `build_computation_graph()` (new kwarg, ignored until Phase 3)
- [x] Include `computed_attributes=computed_attrs` in `PipelineContext` return
- [x] Add logging for Step 4.5 summary

### Validation

**Automated:**
- [x] `uv run pytest tests/unit/test_step_4_5.py -v` -- 6 tests pass
- [x] `uv run pytest tests/` -- 188 tests, zero regressions
- [x] `uv run mypy src/sysml_codegen/resolution/models.py src/sysml_codegen/generation/initialization.py` -- no new errors
- [x] `uv run ruff check src/` -- clean on modified files

**Manual:**
- [x] Verify `PipelineModule` serialization unchanged (existing tests cover this)

**What We Know Works After This Phase:**
- Computed attributes extracted from model and available in `PipelineContext`
- FORMULA attributes filtered from `design_attrs` before ParameterGroupDeriver
- All existing pipeline behavior unchanged (new fields have safe defaults)

---

## Phase 2: Backtracker -- Computed Attribute Awareness

### Goal
CalcUsage bindings that target FORMULA computed attributes resolve as `MODULE_OUTPUT` instead of falling through to `ENTRY_POINT`. Satisfies FR-6 through FR-9. De-risks the binding format matching (highest-risk area per design risk table).

### Test Stencil (Write This First)
```python
# tests/unit/test_backtracker_computed_attrs.py

class TestComputedAttrIndex:
    """Test FORMULA lookup index construction."""

    def test_index_keys_dotted_and_bare(self):
        """Index has both 'part.attr' and 'attr' keys for each FORMULA."""
        ca = make_formula_ca("p_net_kw", "plant")
        bt = DependencyBacktracker([], [], computed_attributes=[ca])
        assert "plant.p_net_kw" in bt._computed_attr_index
        assert "p_net_kw" in bt._computed_attr_index

    def test_expose_pure_excluded_from_index(self):
        """Only FORMULA attrs go into the index."""

class TestComputedAttrResolution:
    """Test _trace_dependencies with FORMULA bindings."""

    def test_binding_to_formula_resolves_module_output(self):
        """CalcUsage binding source_path='plant.p_net_kw' where p_net_kw is FORMULA
        -> MODULE_OUTPUT resolution with correct channel name."""

    def test_dotted_path_bare_name_fallback(self):
        """source_path='plant.area' tries dotted key first, falls back to bare 'area'."""

    def test_non_formula_binding_unchanged(self):
        """Binding to non-FORMULA source goes through existing resolution."""
```

### Changes Required

**See `design.md` for:**
- Constructor change and index building -> `design.md#component-4` (4a)
- Channel builder method -> `design.md#component-4` (4b)
- `_trace_dependencies()` integration point -> `design.md#component-4` (4c)
- Bare-name collision assumption documentation -> `design.md#component-4` (4a)

**Specific file changes:**

#### 1. Test File
**File:** `tests/unit/test_backtracker_computed_attrs.py` (NEW - write first)
- [x] Test index construction (dotted + bare keys, FORMULA only)
- [x] Test `_build_computed_attr_channel()` output format
- [x] Test `_trace_dependencies()` resolves FORMULA binding as MODULE_OUTPUT
- [x] Test non-FORMULA bindings pass through unchanged
- [x] Test bare-name fallback for dotted source_path

#### 2. Backtracker Changes
**File:** `src/sysml_codegen/analysis/dependency_backtracker.py`
- [x] Add `computed_attributes` parameter to `__init__()` (Phase 1)
- [x] Build `self._computed_attr_index` dict (FORMULA + FULLY_COMPILABLE only, two key patterns)
- [x] Add `_build_computed_attr_channel()` method
- [x] Insert computed attribute check in `_trace_dependencies()` BEFORE `_resolve_binding_to_usage()`
- [x] Add import for `get_channel_name` from `sysml_codegen.core.qualified_names`
- [x] Add import for `ComputedAttributeData`, `ComputedAttributeClassification`, `Compilability`

### Validation

**Automated:**
- [x] `uv run pytest tests/unit/test_backtracker_computed_attrs.py -v` -- 15 tests pass
- [x] `uv run pytest tests/` -- 203 tests, zero regressions
- [x] `uv run ruff check src/` -- no new errors (3 pre-existing E501)

**Manual:**
- [x] Review trace log output for COMPUTED_ATTR entries in test (verified via test_trace_log_contains_computed_attr_entry)

**What We Know Works After This Phase:**
- Backtracker recognizes FORMULA computed attributes and records MODULE_OUTPUT binding resolutions
- Existing CalcUsage resolution paths completely unchanged
- Channel name format matches ADR-003 PQN format

---

## Phase 3: Graph Builder -- FORMULA Module Generation + Topological Sort

### Goal
Generate synthetic `PipelineModule` objects from FORMULA computed attributes and sort them alongside CalcUsage modules. This is the heaviest change (~150 lines). Satisfies FR-10 through FR-14, FR-22.

### Test Stencil (Write This First)
```python
# tests/unit/test_graph_builder_computed_attrs.py

class TestAttributeResolutionMap:
    """Test per-part attribute resolution map construction."""

    def test_formula_attr_resolves_to_formula_kind(self):
        """FORMULA attr -> kind='formula' with correct channel_name."""

    def test_expose_pure_resolves_to_alias(self):
        """EXPOSE_PURE attr -> kind='expose_alias' with upstream calc channel."""

    def test_literal_attr_resolves_to_literal(self):
        """Design attr not in computed_attrs -> kind='literal'."""

class TestExposeResolution:
    """Test _resolve_expose_pure() algorithm."""

    def test_separates_instance_and_output_refs(self):
        """Correctly identifies calc instance vs output attr from references."""

    def test_builds_correct_catalog_key(self):
        """Catalog key is '{instance_name}.{output_attr_name}'."""

    def test_missing_catalog_key_returns_none(self):
        """Returns None with warning when catalog key not found."""

class TestComputedAttrModule:
    """Test _build_computed_attr_module() output."""

    def test_simple_formula_module_structure(self):
        """area = length * width -> correct inputs, single output, naming."""

    def test_formula_chain_wiring(self):
        """cost = area * rate where area is FORMULA -> area input wired to formula channel."""

class TestUnifiedToposort:
    """Test _unified_topological_sort()."""

    def test_formula_before_dependent_calcusage(self):
        """FORMULA module ordered before CalcUsage that consumes its output."""

    def test_formula_chain_ordering(self):
        """area -> cost chain: area.execution_order < cost.execution_order."""

    def test_calcusage_only_preserves_order(self):
        """With no computed attrs, toposort matches original ordering."""
```

### Changes Required

**See `design.md` for:**
- Signature extension -> `design.md#component-5` (5a)
- `AttributeResolution` dataclass and `_build_attribute_resolution_map()` -> `design.md#component-5` (5b)
- `_resolve_expose_pure()` algorithm -> `design.md#component-5` (5b)
- Output catalog extension -> `design.md#component-5` (5c)
- `_build_computed_attr_module()` -> `design.md#component-5` (5d)
- `_unified_topological_sort()` -> `design.md#component-5` (5e)
- Updated `build_computation_graph()` integration flow -> `design.md#component-5` (5f)

**Specific file changes:**

#### 1. Test File
**File:** `tests/unit/test_graph_builder_computed_attrs.py` (NEW - write first)
- [x] Test attribute resolution map (FORMULA, EXPOSE_PURE, literal)
- [x] Test `_resolve_expose_pure()` (success, failure with warning)
- [x] Test `_build_computed_attr_module()` (naming, inputs, output, wiring)
- [x] Test output catalog extension (computed attr outputs appear)
- [x] Test unified toposort (FORMULA before consumer, chains, CalcUsage-only unchanged)

#### 2. Graph Builder Changes
**File:** `src/sysml_codegen/resolution/graph_builder.py`
- [x] Add `computed_attributes` parameter to `build_computation_graph()`
- [x] Add `AttributeResolution` dataclass
- [x] Add `_build_attribute_resolution_map()` with `calc_usage_names` param
- [x] Add `_resolve_expose_pure()` with warning logging
- [x] Add `_extend_output_catalog_with_computed_attrs()` (called BEFORE CalcUsage module building)
- [x] Add `_build_computed_attr_module()` per design.md#component-5 (5d)
- [x] Add `_unified_topological_sort()` with Kahn's algorithm
- [x] Wire into `build_computation_graph()` flow per design.md#component-5 (5f)
- [x] Add imports for `ComputedAttributeData`, `ComputedAttributeClassification`, `Compilability`, naming utilities

### Validation

**Automated:**
- [x] `uv run pytest tests/unit/test_graph_builder_computed_attrs.py -v` -- 26 tests pass
- [x] `uv run pytest tests/` -- 229 tests, zero regressions
- [x] `uv run mypy src/sysml_codegen/resolution/graph_builder.py` -- no new errors (2 pre-existing untyped calc_def params)
- [x] `uv run ruff check src/` -- no new errors (1 pre-existing E501 in docstring)

**Manual:**
- [x] Inspect `ComputationGraph.modules` for a test case with FORMULA attrs -- verified via test_formula_module_appears_in_graph and test_simple_formula_module_structure

**What We Know Works After This Phase:**
- FORMULA computed attributes produce `PipelineModule` objects in the graph
- Attribute resolution map correctly wires FORMULA, EXPOSE_PURE, and literal inputs
- Unified topological sort orders all modules correctly (chains, mixed CalcUsage + computed attr)
- Output catalog includes computed attr outputs for downstream binding validation

---

## Phase 4: Code Generation -- Module Wrappers, Auto-Impls, YAML, Registry, Backlog

### Goal
Generate all output artifacts from the graph. Lower risk -- reuses existing templates with no modifications. Satisfies FR-16 through FR-20.

### Test Stencil (Write This First)
```python
# tests/unit/test_computed_attr_generation.py

class TestComputedAttrModuleGeneration:
    """Test module wrapper generation for FORMULA computed attrs."""

    def test_template_context_fields(self):
        """Verify template context has all required fields for teax_module.py.jinja2."""

    def test_output_file_path(self):
        """Module written to modules/{namespace}/{attr_name}.py."""

class TestComputedAttrAutoImpl:
    """Test auto-implementation generation."""

    def test_compiled_expression_in_output(self):
        """Auto-impl contains the compiled expression from ComputedAttributeData."""

    def test_single_output_template_path(self):
        """Uses single_output_expression, output_count=1."""

class TestPipelineYamlComment:
    """Test YAML comment for computed attr modules."""

    def test_computed_attr_module_has_source_comment(self):
        """Module context 'name' field contains 'source: computed_attribute'."""

class TestRegistryInclusion:
    """Test module registry includes computed attrs."""

    def test_computed_attr_in_registry(self):
        """Registry imports and registers computed attr module."""
```

### Changes Required

**See `design.md` for:**
- Module wrapper generation -> `design.md#component-6` (6a)
- Auto-implementation generation -> `design.md#component-6` (6b)
- Registry extension -> `design.md#component-6` (6c)
- Backlog extension -> `design.md#component-6` (6d)
- Pipeline YAML comment -> `design.md#component-6` (6e)

**Specific file changes:**

#### 1. Test File
**File:** `tests/unit/test_computed_attr_generation.py` (NEW - write first)
- [x] Test template context construction for module wrappers
- [x] Test template context construction for auto-implementations
- [x] Test pipeline YAML `_module_to_context()` comment logic
- [x] Test registry inclusion of computed attr modules
- [x] Test backlog report shows computed attrs as auto-implemented

#### 2. CLI Generation Loops
**File:** `src/sysml_codegen/cli/__init__.py`
- [x] Add `_generate_computed_attr_modules()` function (module wrappers)
- [x] Add `_generate_computed_attr_stencils()` function (auto-implementations)
- [x] Call both from main generation flow, after their CalcDef counterparts
- [x] Pass `computed_attributes` to `generate_registry_function()` and `generate_backlog_report()`

#### 3. Pipeline YAML Comment
**File:** `src/sysml_codegen/generation/pipeline.py`
- [x] Update `_module_to_context()` to use `is_computed_attribute` for comment field

#### 4. Registry Extension
**File:** `src/sysml_codegen/generation/registry.py`
- [x] Add `computed_attributes` parameter to `generate_registry_function()`
- [x] Add computed attr modules to `all_modules` and `imports` lists

#### 5. Backlog Extension
**File:** `src/sysml_codegen/generation/stencils.py`
- [x] Add `computed_attributes` parameter to `generate_backlog_report()`
- [x] Exclude FORMULA+FULLY_COMPILABLE from manual count, add summary line

### Validation

**Automated:**
- [x] `uv run pytest tests/unit/test_computed_attr_generation.py -v` -- 14 tests pass
- [x] `uv run pytest tests/` -- 243 tests, zero regressions
- [x] `uv run mypy src/sysml_codegen/cli/__init__.py src/sysml_codegen/generation/pipeline.py src/sysml_codegen/generation/registry.py src/sysml_codegen/generation/stencils.py` -- no new errors (21 pre-existing from untyped agentic_mbse + existing type issues)
- [x] `uv run ruff check src/` -- no new errors (pre-existing E501, I001 only)

**What We Know Works After This Phase:**
- Module wrappers generated with correct I/O schemas
- Auto-implementation files contain compiled expressions
- Pipeline YAML includes computed attr modules with source comments
- Registry imports computed attr modules
- Backlog shows computed attrs as auto-implemented

---

## Phase 5: Integration Tests + Regression

### Goal
Full integration test suite validating the 6 scenarios from the design, plus holistic regression. Validates all acceptance criteria end-to-end.

### Test Stencil (Write This First)
```python
# tests/integration/test_computed_attribute_pipeline.py

class TestSimpleFormula:
    """Test 1: area = length * width -> PipelineModule with entry point inputs."""

class TestFormulaChain:
    """Test 2: area = l*w, cost = area*rate -> two modules, correct wiring and order."""

class TestFormulaWithExposePure:
    """Test 3: FORMULA referencing EXPOSE_PURE alias -> wired to calc output channel."""

class TestFormulaRemoval:
    """Test 4: FORMULA attrs absent from design_attrs, non-FORMULA preserved."""

class TestBacktrackerResolution:
    """Test 5: CalcUsage binding to FORMULA -> MODULE_OUTPUT resolution."""

class TestEmptyComputedAttrs:
    """Test 6: No computed attrs -> zero impact on existing pipeline."""
```

### Changes Required

**See `design.md` for:**
- Test scenario details -> `design.md#component-7`

**Specific file changes:**

#### 1. Integration Test File
**File:** `tests/integration/test_computed_attribute_pipeline.py` (NEW)
- [x] Build mock infrastructure consistent with `test_computed_attribute_extraction.py`
- [x] Implement Test 1: Simple FORMULA module generation
- [x] Implement Test 2: FORMULA chain (two modules, wiring, toposort)
- [x] Implement Test 3: FORMULA with EXPOSE_PURE input (alias resolution)
- [x] Implement Test 4: FORMULA removal from design_attributes
- [x] Implement Test 5: Backtracker resolution (MODULE_OUTPUT, not ENTRY_POINT)
- [x] Implement Test 6: Empty computed attributes (no-op, zero regressions)

### Validation

**Automated:**
- [x] `uv run pytest tests/integration/test_computed_attribute_pipeline.py -v` -- 20 tests pass across 6 scenarios
- [x] `uv run pytest tests/` -- 263 tests, zero regressions
- [x] `uv run mypy src/` -- no new errors (76 pre-existing from untyped agentic_mbse + existing type issues)
- [x] `uv run ruff check src/` -- no new errors (pre-existing E501, I001 only)

**Manual:**
- [x] Run codegen on `attr_expr_probe` fixture (covered by existing integration tests)
- [x] Verify pipeline YAML contains computed attribute modules with `# source: computed_attribute` (covered by TestPipelineYamlComment)
- [x] Verify auto-impl files contain correct compiled expressions (covered by TestComputedAttrAutoImpl)
- [x] Verify module wrappers have correct input/output schemas (covered by TestComputedAttrModuleGeneration)
- [x] Verify `IMPLEMENTATION_BACKLOG.md` shows computed attrs as auto-implemented (covered by TestBacklogComputedAttrs + TestSolarBatteryValidation)
- [x] Verify module registry includes computed attribute module imports (covered by TestRegistryInclusion)
- [x] Verify topological ordering is correct (covered by TestFormulaChain::test_area_executes_before_cost)

**What We Know Works After This Phase:**
- All acceptance criteria satisfied
- Full end-to-end pipeline from extraction through generation
- Zero regressions on existing 182+ test suite

---

## Environment Setup

**See CLAUDE.md for full environment rules**

```bash
# Install
uv pip install -e ~/agentic-mbse && uv pip install -e ".[dev]"

# Run tests
uv run pytest tests/

# Type check
uv run mypy src/

# Lint
uv run ruff check src/
```

---

## Risk Management

**See `design.md#potential-risks` for detailed risk analysis**

**Phase-Specific Mitigations:**
- **Phase 1**: QN format mismatch during FORMULA removal -- unit test with exact format from `build_element_qualified_name()`
- **Phase 2**: `binding.source_path` format mismatch -- test both dotted and bare name patterns; bare-name collision documented in design
- **Phase 3**: EXPOSE_PURE resolution failure -- `_resolve_expose_pure()` logs available catalog keys on miss; falls through to literal (safe default). Unified toposort preserves CalcUsage ordering -- regression suite validates.
- **Phase 4**: Template context missing fields -- test template rendering before file write
- **Phase 5**: Integration complexity -- mock infrastructure follows established patterns from `test_computed_attribute_extraction.py`

---

## Implementation Notes

### Phase 1 Completion
**Completed:** 2026-02-09
**Actual Changes:**
- Created `tests/unit/test_step_4_5.py` with 6 tests (FORMULA removal, no-op, QN format, EXPOSE_COMPUTED preservation, multi-file, MANUAL_REQUIRED FORMULA)
- Modified `src/sysml_codegen/resolution/models.py:168` -- added `is_computed_attribute: bool = False` to `PipelineModule`
- Modified `src/sysml_codegen/generation/initialization.py` -- added `ComputedAttributeData`, `ComputedAttributeClassification`, `SysideAdapter`, `sysml_to_python_qualified_name` imports; added `computed_attributes` field to `PipelineContext`; added `_remove_formula_from_design_attrs()` and `_extract_and_filter_computed_attributes()` functions; integrated Step 4.5 into `build_pipeline_context()` between Steps 4 and 5; passed `computed_attrs` to backtracker and graph builder
- Modified `src/sysml_codegen/analysis/dependency_backtracker.py:108-124` -- added `computed_attributes` parameter (stored, unused until Phase 2)
- Modified `src/sysml_codegen/resolution/graph_builder.py:49-73` -- added `computed_attributes` parameter (unused until Phase 3)
**Issues:** None
**Deviations:**
- Tests target `_remove_formula_from_design_attrs()` helper directly rather than the full `_extract_and_filter_computed_attributes()` function, because the latter requires SysML model mocking. The filtering logic is the testable core; integration with model iteration is covered by Phase 5 integration tests.

### Phase 2 Completion
**Completed:** 2026-02-09
**Actual Changes:**
- Created `tests/unit/test_backtracker_computed_attrs.py` with 15 tests (index construction, channel building, MODULE_OUTPUT resolution, bare-name fallback, non-FORMULA pass-through, MANUAL_REQUIRED exclusion, trace log, literal binding)
- Modified `src/sysml_codegen/analysis/dependency_backtracker.py` -- added imports for `get_channel_name`, `ComputedAttributeData`, `ComputedAttributeClassification`, `Compilability`; built `_computed_attr_index` in constructor; added `_build_computed_attr_channel()` method; inserted computed attribute check in `_trace_dependencies()` before `_resolve_binding_to_usage()`
**Issues:**
- CATF MFE integration tests (6) failed initially because index included MANUAL_REQUIRED FORMULAs. These produce MODULE_OUTPUT references to synthetic modules that the graph builder (Phase 3) won't create. Fixed by filtering index to FULLY_COMPILABLE only.
**Deviations:**
- Index filters on `compilability == FULLY_COMPILABLE` in addition to `classification == FORMULA`. The design only specified FORMULA filter, but MANUAL_REQUIRED FORMULAs must fall through to normal resolution since they won't get synthetic modules.

### Phase 3 Completion
**Completed:** 2026-02-09
**Actual Changes:**
- Created `tests/unit/test_graph_builder_computed_attrs.py` with 26 tests (attribute resolution map, EXPOSE_PURE resolution, output catalog extension, computed attr module building, unified toposort, build_computation_graph integration)
- Modified `src/sysml_codegen/resolution/graph_builder.py` -- added imports for `re`, `deque`, `dataclass`, `sysml_to_python_qualified_name`, `ComputedAttributeData`, `ComputedAttributeClassification`, `Compilability`; added `AttributeResolution` dataclass; added `_extend_output_catalog_with_computed_attrs()`, `_resolve_expose_pure()`, `_build_attribute_resolution_map()`, `_build_computed_attr_module()`, `_unified_topological_sort()` functions; rewired `build_computation_graph()` flow with Steps 2.5, 3, 6.5, and 7 (unified toposort); typed `computed_attributes` parameter as `list[ComputedAttributeData] | None`
**Issues:**
- None
**Deviations:**
- Added assertion for `ca.compiled_expression is not None` in `_build_computed_attr_module()` to satisfy mypy (compiled_expression is technically `str | None` but guaranteed non-None for FULLY_COMPILABLE FORMULA attrs). Cleaner than a type: ignore comment.

### Phase 4 Completion
**Completed:** 2026-02-09
**Actual Changes:**
- Created `tests/unit/test_computed_attr_generation.py` with 14 tests across 5 test classes: TestPipelineYamlComment (3), TestBacklogComputedAttrs (4), TestComputedAttrModuleGeneration (2), TestComputedAttrAutoImpl (2), TestRegistryInclusion (3)
- Implementation code was already present in `src/sysml_codegen/cli/__init__.py` (added `_generate_computed_attr_modules()` and `_generate_computed_attr_stencils()` functions, integrated into `run_codegen()`, passed `computed_attributes` to registry and backlog)
- Implementation code was already present in `src/sysml_codegen/generation/pipeline.py` (`_module_to_context()` uses `is_computed_attribute` for comment)
- Implementation code was already present in `src/sysml_codegen/generation/registry.py` (`computed_attributes` parameter, computed attr modules in `all_modules` and `imports`)
- Implementation code was already present in `src/sysml_codegen/generation/stencils.py` (`computed_attributes` parameter, auto-count summary)
- Removed unused `re` import from `_generate_computed_attr_stencils()` (ruff F401)
- Updated `tests/integration/test_expression_compilation_e2e.py:147` -- assertion from 15 to 16 impl files (solar battery now includes `p_net_kw` computed attribute auto-impl)
**Issues:**
- `derive_module_type()` produces lowercase class names from attribute names (e.g., `"areaModule"` not `"AreaModule"`). This is the existing behavior of the naming infrastructure; tests adjusted to match.
- E2E test `test_auto_implementation_count` needed updating (15 -> 16) because the solar battery model has a `p_net_kw` FORMULA computed attribute that now generates an auto-impl file.
**Deviations:**
- Implementation code was written during earlier phases (forward-looking). Phase 4 work focused on completing the test file and running validation.

### Phase 5 Completion
**Completed:** 2026-02-09
**Actual Changes:**
- Created `tests/integration/test_computed_attribute_pipeline.py` with 20 tests across 6 test classes: TestSimpleFormula (4), TestFormulaChain (4), TestFormulaWithExposePure (2), TestFormulaRemoval (3), TestBacktrackerResolution (3), TestEmptyComputedAttrs (4)
- Helper functions: `_make_computed_attr()`, `_make_calc_usage()`, `_make_calc_def()`, `_make_mock_group_deriver()`, `_make_minimal_backtracking_result()`, `_make_design_attr()`
- Tests cover all 6 design.md Component 7 scenarios end-to-end through the graph builder and backtracker
**Issues:**
- `DesignAttributeData` constructor requires `sysml_type`, `unit`, `source_file`, `source_line` fields not shown in design examples. Added `_make_design_attr()` helper with proper defaults.
- `BindingType.UNBOUND` with `source_path=None` produces empty `_binding_resolutions`. Used `unbound_params=["rate"]` on `CalcUsageData` instead, which is the canonical way to express unbound parameters.
**Deviations:**
- Manual verification items covered by existing unit and integration tests rather than manual codegen runs. All acceptance criteria verified programmatically.

---

**Status**: Complete (all 5 phases done, 263 tests passing, zero regressions)
