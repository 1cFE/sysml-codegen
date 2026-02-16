# Implementation Plan: Template CalcUsage Detection & Virtual Instantiation

**Status:** Complete
**Created:** 2026-02-10
**Last Updated:** 2026-02-10

## Source Documents
- **Spec:** `.project/active/template-detection/spec.md`
- **Design:** `.project/active/template-detection/design.md` ← See here for component details, dependencies, architecture

## Implementation Strategy

**Phasing Rationale:**
Phase 1 is purely additive (new fields with defaults + detection logic) — zero regression risk and foundation for everything else. Phase 2 tackles the riskiest algorithm (recursive path resolution) in isolation with mock-based tests, de-risking before integration. Phase 3 assembles the pieces — with Phases 1-2 proven, this is straightforward data assembly and list filtering.

**Overall Validation Approach:**
- Each phase starts with tests
- Each phase runs full regression suite (`uv run pytest tests/`)
- Each phase runs `mypy` and `ruff` checks
- Continuous verification ensures no regressions against 313+ baseline

---

## Phase 1: Data Model + Template Detection

### Goal
Add the 3 new fields to `CalcUsageData` and implement template detection in `_extract_single_usage()`. This is purely additive with defaults on all new fields, so it has zero regression risk. Every subsequent phase depends on `is_template` being correctly set.

### Test Stencil (Write This First)
```python
# tests/unit/test_template_detection.py — Phase 1 tests

class TestTemplateDetection:
    """Test Suite 1: Template detection in _extract_single_usage()."""

    def test_calc_in_part_def_is_template(self):
        """CalcUsage owned by PartDefinition → is_template=True."""
        elem = make_calc_usage_elem(owning_type_class="PartDefinition")
        usage = _extract_single_usage(elem, ...)
        assert usage.is_template is True

    def test_calc_in_part_usage_is_concrete(self):
        """CalcUsage owned by PartUsage → is_template=False."""
        elem = make_calc_usage_elem(owning_type_class="PartUsage")
        usage = _extract_single_usage(elem, ...)
        assert usage.is_template is False

    def test_owning_part_def_qn_set_for_template(self):
        """Template CalcUsage has owning_part_def_qn set."""
        # Verify QN matches build_element_qualified_name(owning_type)

    def test_raw_element_stored(self):
        """raw_element stores the original AST element."""
```

### Changes Required

**See `design.md` for:**
- Field definitions → `design.md#component-1-data-model-extensions`
- Detection logic → `design.md#component-2-template-detection`
- Rationale for `SysideAdapter.is_instance()` vs `type().__name__` → `design.md#component-2-template-detection`

**Specific file changes:**

#### 1. Test File
**File:** `tests/unit/test_template_detection.py` (NEW — write first)
- [ ] Create test file with mock helpers for AST elements
- [ ] Implement Test Suite 1 (5 tests): template detection, concrete detection, no owning_type, owning_part_def_qn, raw_element
- [ ] Run tests — expect failures (no implementation yet)

#### 2. Data Model
**File:** `src/sysml_codegen/extraction/usage_extractor.py:87` (CalcUsageData class)
- [ ] Add `is_template: bool = False` after `qualified_name`
- [ ] Add `owning_part_def_qn: str | None = None`
- [ ] Add `raw_element: object | None = None`

#### 3. Template Detection Logic
**File:** `src/sysml_codegen/extraction/usage_extractor.py:174` (_extract_single_usage)
- [ ] Add `owning_type` check via `SysideAdapter.is_instance(owning_type, "PartDefinition")` before return statement
- [ ] Set `is_template` and `owning_part_def_qn` fields
- [ ] Pass `raw_element=elem` to CalcUsageData constructor

### Validation

**Automated:**
- [ ] `uv run pytest tests/unit/test_template_detection.py` → All Phase 1 tests pass
- [ ] `uv run pytest tests/` → All 313+ existing tests pass (zero regressions)
- [ ] `uv run mypy src/sysml_codegen/extraction/usage_extractor.py` → passes
- [ ] `uv run ruff check src/sysml_codegen/extraction/usage_extractor.py` → passes

**Manual:**
- [ ] Verify `CalcUsageData` fields have defaults (existing construction sites unaffected)

**What We Know Works After This Phase:**
Template vs concrete classification is correct. The `is_template` flag and `owning_part_def_qn` are set for PartDefinition-owned CalcUsages. All existing code is unaffected by the additive changes.

---

## Phase 2: Part Usage Index + Instantiation Path Resolver

### Goal
Implement `_build_part_usage_index()` and `_find_instantiation_paths()` — the recursive path resolution algorithm. This is the most complex component, so we de-risk it with focused mock-based tests before wiring it into the expansion pipeline.

### Test Stencil (Write This First)
```python
# Add to tests/unit/test_template_detection.py — Phase 2 tests

class TestPartUsageIndex:
    """Test Suite 2: Part usage index builder."""

    def test_index_maps_part_def_to_usages(self):
        """Two PartUsages typing same PartDef → both in index."""
        model = make_model_with_usages([("mod_a", "WidgetDef"), ("mod_b", "WidgetDef")])
        index = _build_part_usage_index(model)
        assert len(index["Pkg__WidgetDef"]) == 2

    def test_index_empty_types_skipped(self):
        """PartUsage with empty .types → not indexed."""

class TestInstantiationPaths:
    """Test Suite 3: Recursive path resolution."""

    def test_single_level_path(self):
        """PartUsage in Package → direct path."""

    def test_two_level_path(self):
        """PartUsage in PartDef → composed path through parent."""

    def test_three_level_path(self):
        """Full solar_battery-style 3-level chain."""

    def test_deduplication(self):
        """Library + part redefines → single deduplicated path."""

    def test_no_instantiations_returns_empty(self):
        """PartDef with no PartUsages → empty list."""
```

### Changes Required

**See `design.md` for:**
- Index builder spec → `design.md#component-3-part-usage-index-builder`
- Recursive algorithm + walk-through → `design.md#component-4-recursive-instantiation-path-resolver`
- FR-10 specialization chain deferral rationale → `design.md#component-3-part-usage-index-builder`
- Deduplication strategy → `design.md#component-4-recursive-instantiation-path-resolver`

**Specific file changes:**

#### 1. Tests
**File:** `tests/unit/test_template_detection.py` (extend)
- [ ] Add mock helpers for PartUsage/PartDef elements with `.types`, `.name`, `owning_type`
- [ ] Implement Test Suite 2 (3 tests): index mapping, quoted names, empty types
- [ ] Implement Test Suite 3 (5 tests): single/two/three level paths, deduplication, empty
- [ ] Run tests — expect failures

#### 2. Part Usage Index Builder
**File:** `src/sysml_codegen/extraction/usage_extractor.py` (new function)
- [ ] Implement `_build_part_usage_index(model)` per design Component 3
- [ ] Use `SysideAdapter.elements_of_type(model, "PartUsage")` + `next(iter(usage.types))`
- [ ] Handle empty `.types` with try/except

#### 3. Recursive Path Resolver
**File:** `src/sysml_codegen/extraction/usage_extractor.py` (new function)
- [ ] Implement `_find_instantiation_paths(target_part_def_qn, part_usage_index)` per design Component 4
- [ ] Add `_visited` set for recursion guard
- [ ] Deduplicate paths at each recursion level

### Validation

**Automated:**
- [ ] `uv run pytest tests/unit/test_template_detection.py` → All Phase 1+2 tests pass
- [ ] `uv run pytest tests/` → All 313+ tests pass
- [ ] `uv run mypy src/sysml_codegen/extraction/usage_extractor.py` → passes
- [ ] `uv run ruff check src/sysml_codegen/extraction/usage_extractor.py` → passes

**Manual:**
- [ ] Trace through the solar_battery walk-through from `design.md#component-4` mentally against the implementation

**What We Know Works After This Phase:**
The part usage index correctly maps PartDef QNs to their PartUsage elements. The recursive path resolver correctly computes design-relative paths through multi-level hierarchies, with deduplication handling `part redefines` correctly.

---

## Phase 3: Virtual CalcUsage Generation + Integration

### Goal
Implement `_expand_template_calc_usages()`, `_create_virtual_calc_usage()`, wire the `expand_templates` parameter into `extract_calculation_usages()`, and add logging. With Phases 1-2 proven, this is straightforward data assembly and list filtering.

### Test Stencil (Write This First)
```python
# Add to tests/unit/test_template_detection.py — Phase 3 tests

class TestVirtualCalcUsageGeneration:
    """Test Suite 4: Virtual CalcUsage creation."""

    def test_virtual_calc_qualified_name(self):
        """Virtual QN = instantiation_path__calc_name."""
        template = make_template_calc_usage(instance_name="cost_model")
        virtual = _create_virtual_calc_usage(template, "Pkg__plant__array__module")
        assert virtual.qualified_name == "Pkg__plant__array__module__cost_model"

    def test_virtual_calc_bindings_copied(self):
        """Bindings from template are present in virtual."""

    def test_virtual_calc_is_not_template(self):
        """Virtual instance has is_template=False."""

    def test_virtual_calc_parent_part_path(self):
        """parent_part_path is dot-separated design-relative path."""

class TestTemplateExpansionIntegration:
    """Test Suite 5: End-to-end expansion."""

    def test_expand_templates_true_replaces_templates(self):
        """Templates removed, virtuals added."""

    def test_expand_templates_false_preserves_templates(self):
        """Templates kept with is_template=True."""

    def test_concrete_usages_unchanged(self):
        """Non-template CalcUsages pass through unmodified."""

    def test_warning_on_no_instantiations(self):
        """Template with no PartUsages emits warning."""
```

### Changes Required

**See `design.md` for:**
- Virtual creation logic → `design.md#component-5-virtual-calcusage-generator`
- `_create_virtual_calc_usage()` full implementation → `design.md#component-5-virtual-calcusage-generator`
- Integration point → `design.md#component-6-integration-into-extract_calculation_usages`
- Logging strategy → `design.md#component-7-logging-and-warning-routing`
- Key decisions (instance_name, shallow copy, parent_part_path) → `design.md#component-5-virtual-calcusage-generator`

**Specific file changes:**

#### 1. Tests
**File:** `tests/unit/test_template_detection.py` (extend)
- [ ] Add helper to create template CalcUsageData with mock bindings
- [ ] Implement Test Suite 4 (5 tests): qualified name, bindings, is_template, parent_part_path, multiple usages
- [ ] Implement Test Suite 5 (4 tests): expand true/false, concrete unchanged, warning
- [ ] Run tests — expect failures

#### 2. Virtual CalcUsage Creator
**File:** `src/sysml_codegen/extraction/usage_extractor.py` (new function)
- [ ] Implement `_create_virtual_calc_usage(template, instantiation_path)` per design Component 5
- [ ] Qualified name: `f"{instantiation_path}__{sanitize_name(template.instance_name)}"`
- [ ] Shallow copy bindings and unbound_params
- [ ] Build dot-separated parent_part_path from path segments

#### 3. Template Expansion Orchestrator
**File:** `src/sysml_codegen/extraction/usage_extractor.py` (new function)
- [ ] Implement `_expand_template_calc_usages(model, calc_usages, warnings)` per design Component 5
- [ ] Build index, separate concrete/template, expand templates via path resolver
- [ ] Emit warning + drop when template has zero instantiations (FR-23)
- [ ] Deduplicate virtual CalcUsages by qualified_name

#### 4. Integration
**File:** `src/sysml_codegen/extraction/usage_extractor.py:136` (extract_calculation_usages)
- [ ] Add `expand_templates: bool = True` parameter
- [ ] Call `_expand_template_calc_usages()` after extraction loop, before report construction
- [ ] Add logging per design Component 7

### Validation

**Automated:**
- [ ] `uv run pytest tests/unit/test_template_detection.py` → All Phase 1+2+3 tests pass
- [ ] `uv run pytest tests/` → All 313+ tests pass (zero regressions)
- [ ] `uv run mypy src/sysml_codegen/extraction/usage_extractor.py` → passes
- [ ] `uv run ruff check src/sysml_codegen/extraction/usage_extractor.py` → passes

**Manual:**
- [ ] Verify `extract_calculation_usages(model, expand_templates=False)` returns templates with `is_template=True`
- [ ] Verify `extract_calculation_usages(model, expand_templates=True)` returns only concrete + virtual (no templates)

**What We Know Works After This Phase:**
Full template detection and virtual instantiation pipeline. Templates are correctly replaced by per-instance virtual CalcUsages with hierarchy-aware qualified names and copied bindings. The `expand_templates` flag works for testing/debugging. All existing pipeline code receives virtual CalcUsages transparently.

---

## Environment Setup

**See CLAUDE.md for full environment rules**

---

## Risk Management

**See `design.md#potential-risks` for detailed risk analysis**

**Phase-Specific Mitigations:**
- **Phase 1**: Low risk — all new fields have defaults. Existing CalcUsageData construction unaffected.
- **Phase 2**: Highest risk — recursive algorithm. Mitigated by `_visited` set, mock-based tests covering the exact solar_battery walk-through, and deduplication at each recursion level.
- **Phase 3**: Medium risk — assembly of proven components. Main risk is wiring bugs. Mitigated by integration tests covering expand_templates=True/False and concrete passthrough.

## Implementation Notes

### Phase 1 Completion
**Completed:** 2026-02-10
**Actual Changes:**
- Modified `src/sysml_codegen/extraction/usage_extractor.py`: Added `is_template`, `owning_part_def_qn`, `raw_element` fields to `CalcUsageData`. Added template detection logic in `_extract_single_usage()` using `SysideAdapter.is_instance(owning_type, "PartDefinition")`.
- Created `tests/unit/test_template_detection.py` with 6 tests (TestTemplateDetection suite).
**Issues:** None
**Deviations:** Added a 6th test (`test_concrete_usage_has_none_owning_part_def_qn`) beyond the 5 in the plan stencil for completeness.

### Phase 2 Completion
**Completed:** 2026-02-10
**Actual Changes:**
- Added `_build_part_usage_index()` and `_find_instantiation_paths()` to `usage_extractor.py`.
- Added TestPartUsageIndex (3 tests) and TestInstantiationPaths (5 tests) to test file.
**Issues:** None
**Deviations:** None — implemented exactly per design Components 3 and 4.

### Phase 3 Completion
**Completed:** 2026-02-10
**Actual Changes:**
- Added `_create_virtual_calc_usage()` and `_expand_template_calc_usages()` to `usage_extractor.py`.
- Added `expand_templates: bool = True` parameter to `extract_calculation_usages()`.
- Added logging per design Component 7.
- Added TestVirtualCalcUsageGeneration (8 tests) and TestTemplateExpansionIntegration (4 tests) to test file.
**Issues:** None
**Deviations:** Added 3 extra tests beyond plan stencil (instance_name_equals_qualified_name, unbound_params_copied, preserves_source_info) for coverage.

### Validation Results
- **26 new tests pass** (all 5 suites)
- **339 total tests pass** (313 baseline + 26 new, zero regressions)
- **mypy:** Pre-existing errors only (agentic_mbse lacking py.typed marker, existing `Any` returns on lines 75/82/625/655/666). No new errors.
- **ruff:** Pre-existing I001 import sort issue only. No new lint errors.

---

**Status**: Complete
