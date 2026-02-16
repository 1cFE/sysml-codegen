# Implementation Plan: Codegen Bug Fixes

**Status:** Complete
**Created:** 2026-02-10
**Last Updated:** 2026-02-10

## Source Documents
- **Spec:** `.project/active/codegen-bug-fixes/spec.md`
- **Design:** `.project/active/codegen-bug-fixes/design.md` — See here for component details, code snippets, risk analysis

## Implementation Strategy

**Phasing Rationale:**
The design identifies three implementation phases with a clear dependency: Bug 2 must precede Bug 1. The plan follows this ordering, grouping independent bugs for parallelism within phases. Each phase is a single commit with tests written first.

Phase 1 tackles the three independent, low-risk bugs (6, 7, 3) to build confidence and get quick wins. Phase 2 handles the riskiest, most interconnected work (Bugs 2 + 1 — backtracker wiring and param_groups rebuild). Phase 3 covers Bug 5 (smart-regen), which is independent but touches generation logic that benefits from Phases 1-2 being stable. Bug 4 is a TEAx fix (out of scope — file task only).

**Overall Validation Approach:**
- Each phase starts with tests
- `uv run pytest tests/ -v` after each phase (285+ baseline, 0 failures)
- `uv run mypy src/` and `uv run ruff check src/` after each phase

---

## Phase 1: Independent Fixes (Bugs 6, 7, 3)

### Goal
Fix three independent, low-risk bugs that have no inter-dependencies. This builds a stable foundation and catches any unexpected regression before touching the core backtracker/graph builder in Phase 2.

### Test Stencil (Write First)

```python
# tests/unit/test_qualified_names.py (NEW)
import pytest
from sysml_codegen.core.qualified_names import sanitize_name

class TestSanitizeNameSpecialChars:
    """Bug 6: Special character sanitization."""

    @pytest.mark.parametrize("input_name, expected", [
        ("Racking_&_Mounting", "Racking_Mounting"),
        ("foo$bar", "foo_bar"),
        ("hello-world", "hello_world"),
        ("a@b#c", "a_b_c"),
        ("  normal  ", "normal"),
        ("'Quoted Name'", "Quoted_Name"),
        ("class", "class_"),   # reserved word still works
        ("", ""),              # empty still works
        (None, ""),            # None still works
    ])
    def test_sanitize_name(self, input_name, expected):
        assert sanitize_name(input_name) == expected
```

```python
# tests/unit/test_cli_generation.py (NEW)
import pytest
from pathlib import Path

class TestEnsurePackageInitFiles:
    """Bug 7: Intermediate __init__.py creation."""

    def test_creates_init_files_in_all_intermediate_dirs(self, tmp_path):
        from sysml_codegen.cli import _ensure_package_init_files
        (tmp_path / "a" / "b" / "c").mkdir(parents=True)
        _ensure_package_init_files(tmp_path, "a/b/c")
        assert (tmp_path / "a" / "__init__.py").exists()
        assert (tmp_path / "a" / "b" / "__init__.py").exists()
        assert (tmp_path / "a" / "b" / "c" / "__init__.py").exists()

    def test_does_not_overwrite_existing_init(self, tmp_path):
        (tmp_path / "a").mkdir()
        (tmp_path / "a" / "__init__.py").write_text("# custom\n")
        _ensure_package_init_files(tmp_path, "a")
        assert (tmp_path / "a" / "__init__.py").read_text() == "# custom\n"
```

```python
# tests/unit/test_computed_attr_generation.py (ADD to existing)
class TestFormulaModuleInputType:
    """Bug 3: FORMULA input type must be 'float', not 'Float'."""

    def test_formula_module_inputs_use_float_primitive(self):
        # Build a FORMULA PipelineModule and verify input python_type
        # See existing _make_formula_module() pattern in this file
        ...
        for inp in module.inputs:
            assert inp.python_type == "float"
```

### Changes Required

**See `design.md#bug-6-special-character-sanitization` for:** code snippets, call site list, underscore collapsing rationale.

**Specific file changes:**

#### 1. Tests (Write First)
- [x] Create `tests/unit/test_qualified_names.py` with parametrized `sanitize_name` tests
- [x] Create `tests/unit/test_cli_generation.py` with `_ensure_package_init_files` tests
- [x] Add Bug 3 test to `tests/unit/test_computed_attr_generation.py`

#### 2. Bug 6: `sanitize_name()` Enhancement
**File:** `src/sysml_codegen/core/qualified_names.py:12-27`
- [x] Add `import re` at top
- [x] Add `re.sub(r"[^a-zA-Z0-9_]", "_", name)` after space replacement
- [x] Add underscore collapsing and strip (see `design.md#bug-6`)

**File:** `src/sysml_codegen/extraction/extractor.py`
- [x] Add `from sysml_codegen.core.qualified_names import sanitize_name` import
- [x] Replace 6 `self._sanitize_name(...)` calls with `sanitize_name(...)` (lines 93, 132, 155, 191, 258, 341)
- [x] Delete `_sanitize_name()` method (lines 616-624)

#### 3. Bug 7: Intermediate `__init__.py`
**File:** `src/sysml_codegen/cli/__init__.py`
- [x] Add `_ensure_package_init_files()` helper (see `design.md#bug-7`)
- [x] Refactor `_generate_modules()` (~line 181): replace `created_namespaces` + single `__init__.py` write with helper call
- [x] Refactor `_generate_computed_attr_modules()` (~line 239): same pattern
- [x] Refactor `_generate_computed_attr_stencils()` (~line 347): same pattern
- [x] Refactor `_generate_stencils()` (~line 429): same pattern, remove `created_namespaces` set

#### 4. Bug 3: FORMULA Input Type
**File:** `src/sysml_codegen/cli/__init__.py:265`
- [x] Change `"Float"` to `"float"` in input_attributes list comprehension

### Validation

**Automated:**
- [x] `uv run pytest tests/unit/test_qualified_names.py -v` — 13 passed
- [x] `uv run pytest tests/unit/test_cli_generation.py -v` — 4 passed
- [x] `uv run pytest tests/unit/test_computed_attr_generation.py -v` — 15 passed
- [x] `uv run pytest tests/ -v` — 303 tests, 0 failures (full regression)
- [x] `uv run mypy src/` — 76 pre-existing errors, 0 new
- [x] `uv run ruff check src/` — 17 pre-existing errors, 0 new

**What We Know Works After This Phase:**
- `sanitize_name()` handles all special characters and produces valid Python identifiers
- Duplicate `_sanitize_name()` eliminated from extractor
- All intermediate directories get `__init__.py` files
- FORMULA module inputs use `float` (not `Float`)

---

## Phase 2: Core Backtracker/Graph Builder (Bugs 2, 1)

### Goal
Fix the core backtracker wiring (Bug 2) so FORMULA and EXPOSE_PURE bindings resolve as MODULE_OUTPUT, then fix the param_groups rebuild (Bug 1) so FORMULA entry points appear in DesignParams. This is the highest-risk phase — it touches the dependency resolution engine.

Bug 2 must be implemented first: without correct MODULE_OUTPUT resolution, Bug 1's entry point additions would be partially redundant.

### Test Stencil (Write First)

```python
# tests/unit/test_backtracker_computed_attrs.py (ADD to existing)

class TestFormulaIndexSysmlQualifiedName:
    """Bug 2 Change A: _computed_attr_index includes :: key."""

    def test_sysml_qn_key_in_index(self):
        ca = _make_computed_attr("power_mw", "e2e_plant", "E2EDesign::e2e_plant")
        bt = DependencyBacktracker(
            calc_usages=[], calc_defs=[], design_attributes=[],
            computed_attributes=[ca],
        )
        assert "E2EDesign::e2e_plant::power_mw" in bt._computed_attr_index

class TestBindingResolutionWithColonColon:
    """Bug 2 Changes B+C: :: source_path resolves to FORMULA MODULE_OUTPUT."""

    def test_colon_colon_binding_resolves_to_module_output(self):
        # CalcUsage with binding source_path = "E2EDesign::e2e_plant::power_mw"
        # Backtracker should resolve as MODULE_OUTPUT, not ENTRY_POINT
        ...
        resolution = result.binding_resolutions[mapping_key]
        assert resolution.resolution_type == BindingResolutionType.MODULE_OUTPUT
```

```python
# tests/unit/test_graph_builder_computed_attrs.py (ADD to existing)

class TestParamGroupsRebuild:
    """Bug 1: FORMULA entry points appear in param_groups after Step 6.6."""

    def test_formula_entry_points_in_param_groups(self):
        # Build computation graph with FORMULA computed attrs
        # Verify entry_point_groups contains FORMULA module inputs
        graph = build_computation_graph(...)
        all_ep_names = {
            ep.qualified_name
            for pg in graph.entry_point_groups
            for ep in pg.parameters
        }
        # FORMULA module inputs must appear
        assert "e2edesign__e2e_plant__quantity" in all_ep_names
```

### Changes Required

**See `design.md#bug-2-formulaexpose-backtracker-wiring` for:** index extension code, normalization code, EXPOSE_PURE resolution strategy.
**See `design.md#bug-1-formula-entry-point-omission` for:** Step 6.6 code, prerequisite refactoring, `_convert_derived_groups()` extraction.

**Specific file changes:**

#### 1. Tests (Write First)
- [x] Add `::` index key test to `tests/unit/test_backtracker_computed_attrs.py`
- [x] Add `::` binding resolution test to `tests/unit/test_backtracker_computed_attrs.py`
- [x] Add EXPOSE_PURE transitive resolution test (dotted path via `_design_attr_binding_index`)
- [x] Add param_groups rebuild test to `tests/unit/test_graph_builder_computed_attrs.py`

#### 2. Bug 2, Change A: Extend `_computed_attr_index` Keys
**File:** `src/sysml_codegen/analysis/dependency_backtracker.py:138-145`
- [x] Add SysML `::` qualified name as third key per FORMULA attribute

#### 3. Bug 2, Change B: Normalize `_trace_dependencies` Lookup
**File:** `src/sysml_codegen/analysis/dependency_backtracker.py:397-400`
- [x] Add `::` fallback after existing dotted-name fallback

#### 4. Bug 2, Change C: Generalize `::` Normalization in `_resolve_binding_to_usage`
**File:** `src/sysml_codegen/analysis/dependency_backtracker.py` (~line 700)
- [x] Add `::` -> dotted normalization as **fallback** (Strategy 5, after all existing strategies)
- [x] This fixes EXPOSE_PURE transitive resolution for `::` source paths

#### 4b. Bug 2, Additional: Normalize `::` in `_build_channel_name_for_binding`
**File:** `src/sysml_codegen/analysis/dependency_backtracker.py` (~line 640)
- [x] Add `::` -> dotted normalization at top of `_build_channel_name_for_binding()`
- [x] Required because resolved `::` source paths need dotted format for channel name construction

#### 5. Bug 1, Prerequisite: Extract `_convert_derived_groups()`
**File:** `src/sysml_codegen/resolution/graph_builder.py:371-413`
- [x] Extract conversion logic from `_group_entry_points_via_deriver()` into `_convert_derived_groups(entry_points, derived_groups)` helper
- [x] Refactor `_group_entry_points_via_deriver()` to call helper

#### 6. Bug 1, Prerequisite: Remove Unused `param_groups` Parameter
**File:** `src/sysml_codegen/resolution/graph_builder.py`
- [x] Remove `param_groups` from `_build_pipeline_module()` signature (line 821) and call site (line 145)
- [x] Remove `param_groups` from `_build_computed_attr_module()` signature (line 627) and call site (line 165)
- [x] Update all test call sites in `test_graph_builder_computed_attrs.py`

#### 7. Bug 1: Add Step 6.6 — Rebuild param_groups
**File:** `src/sysml_codegen/resolution/graph_builder.py` (after Step 6.5, ~line 167)
- [x] Add Step 6.6: `derive_groups()` -> filter by `entry_points.keys()` -> `_convert_derived_groups()`
- [x] Assign result to `param_groups` (overwrites Step 5 result)

#### 8. RESOLVED: `::` normalization regression fixed
- [x] Fixed circular dependency regression in chain_spike, solar_battery, CATF MFE integration tests

### Validation

**Automated:**
- [x] `uv run pytest tests/unit/test_backtracker_computed_attrs.py -v` — 19 passed (including 4 new)
- [x] `uv run pytest tests/unit/test_graph_builder_computed_attrs.py -v` — 29 passed (including 2 new)
- [x] `uv run pytest tests/ -v` — 309 passed, 0 failures (regression resolved)
- [x] `uv run mypy src/` — 76 pre-existing errors, 0 new
- [x] `uv run ruff check src/` — 17 pre-existing errors, 0 new

**What We Know Works After This Phase:**
- CalcUsage bindings to FORMULA attrs resolve as MODULE_OUTPUT regardless of `::`, dotted, or bare source_path format
- EXPOSE_PURE transitive resolution works for `::` source paths
- FORMULA entry points appear in `entry_point_groups` (and will appear in generated DesignParams schema)
- Unused `param_groups` parameter cleaned up from module builder signatures

---

## Phase 3: Smart-Regen Stub Upgrade (Bug 5) + Wrap-Up

### Goal
Fix the `--smart-regen` preserve branch to detect stubs and upgrade them to auto-implementations when FULLY_COMPILABLE. File the Bug 4 TEAx task. Run final E2E validation.

### Test Stencil (Write First)

```python
# tests/unit/test_stencils.py (ADD to existing or new test class)

class TestSmartRegenStubUpgrade:
    """Bug 5: --smart-regen upgrades stubs when auto-impl available."""

    def test_stub_upgraded_when_fully_compilable(self, tmp_path):
        stub_content = 'def calculate(inputs):\n    raise NotImplementedError("TODO")\n'
        stencil = tmp_path / "calc_impl.py"
        stencil.write_text(stub_content)
        # Mock compilation_result with FULLY_COMPILABLE
        # Run _generate_stencils with smart_regen=True
        # Assert file was overwritten (no longer contains NotImplementedError)
        assert "raise NotImplementedError" not in stencil.read_text()

    def test_handwritten_preserved_when_fully_compilable(self, tmp_path):
        handwritten = 'def calculate(inputs):\n    return inputs.x * 2\n'
        stencil = tmp_path / "calc_impl.py"
        stencil.write_text(handwritten)
        # Same FULLY_COMPILABLE mock, smart_regen=True
        # Assert file was NOT overwritten
        assert stencil.read_text() == handwritten

    def test_stub_preserved_when_not_compilable(self, tmp_path):
        stub_content = 'def calculate(inputs):\n    raise NotImplementedError("TODO")\n'
        stencil = tmp_path / "calc_impl.py"
        stencil.write_text(stub_content)
        # compilation_result = None (no AST)
        # Assert file was preserved (still contains NotImplementedError)
        assert "raise NotImplementedError" in stencil.read_text()
```

### Changes Required

**See `design.md#bug-5-smart-regen-stub-upgrade` for:** stub-detection code, safety analysis, import needed.

**Specific file changes:**

#### 1. Tests (Write First)
- [x] Add `TestSmartRegenStubUpgrade` to `tests/unit/test_stencils.py`
- [x] Cover 4 cases: stub+compilable (upgrade), handwritten+compilable (preserve), auto-impl+compilable (preserve), stub+no-compilation (preserve)

#### 2. Bug 5: Stub-to-Auto-Impl Upgrade
**File:** `src/sysml_codegen/cli/__init__.py:459-461`
- [x] Add `Compilability` import (from `sysml_codegen.extraction.expression_compiler`)
- [x] Replace unconditional preserve with stub-detection check (see `design.md#bug-5`)
- [x] Stub detected by `"raise NotImplementedError" in existing_content`
- [x] Auto-impl available when `compilation_result.overall_compilability == Compilability.FULLY_COMPILABLE`

#### 3. Bug 4: File TEAx Task
- [x] TEAx ExitPoint primitive type support spec filed: `~/1cfe/teax/.project/active/exitpoint-primitive-types/spec.md`

### Validation

**Automated:**
- [x] `uv run pytest tests/unit/test_stencils.py -v` — 20 passed (including 4 new)
- [x] `uv run pytest tests/ -v` — 313 passed, 0 failures (full regression)
- [x] `uv run mypy src/` — 76 pre-existing errors, 0 new
- [x] `uv run ruff check src/` — 17 pre-existing errors, 0 new

**What We Know Works After This Phase:**
- `--smart-regen` upgrades stubs when auto-implementation available
- Hand-written and auto-implemented files preserved correctly
- All 6 sysml-codegen bugs fixed (Bug 4 is TEAx-side)

---

## Phase 4: E2E Validation (Zero Manual Workarounds)

### Goal
Run codegen on both test models and verify zero manual workarounds needed. This is the final acceptance gate before closing the epic items.

### Changes Required

No code changes. Validation only.

#### 1. e2e_attr_expr Model
- [x] Run: `uv run sysml-codegen generate --models /home/reid/1cfe/fusion-tea/models/tests/e2e_attr_expr/ --output /tmp/e2e_attr_expr --package-name e2e_attr_expr --overwrite`
- [x] Verify: No errors during generation
- [x] Verify: `design_params.py` contains all 7 FORMULA input parameters (FR-1, FR-2) — confirmed: quantity, unit_cost, om_rate, length, width, height, cost_per_sqm all present with defaults
- [x] Verify: `pipeline.yaml` wires FORMULA/EXPOSE bindings to module outputs (FR-3, FR-4, FR-5) — confirmed: `energy.power_mw` wired to `E2EAttrExprDesign__e2e_plant__power_mw__power_mw.root`, `lcoe.annual_om` wired to `annual_om__annual_om.root`, `financial.total_capex` present as entry point (EXPOSE_PURE resolved)
- [x] Verify: FORMULA module inputs use `float` type (FR-6, FR-7) — confirmed: `quantity: float`, `unit_cost: float` in power_mw module; output still `Float` (RootModel[float])

#### 2. solar_battery Model
- [x] Run: `uv run sysml-codegen generate --models /home/reid/1cfe/fusion-tea/models/tests/solar_battery/ --output /tmp/solar_battery --package-name solar_battery --overwrite`
- [x] Verify: No SyntaxError in generated code (Bug 6 — `Racking_&_Mounting`) — confirmed: all .py files parse via `ast.parse()`
- [x] Verify: `modules/solarbatterydesign/__init__.py` exists (Bug 7) — confirmed: all intermediate dirs have `__init__.py`
- [x] Verify: FORMULA module inputs use `float` (Bug 3) — confirmed: `p_net_kw` module uses `float` for inputs

#### 3. Final Regression
- [x] `uv run pytest tests/ -v` — 313 passed, 0 failures
- [x] `uv run mypy src/` — 76 pre-existing errors, 0 new
- [x] `uv run ruff check src/` — 17 pre-existing errors, 0 new

**What We Know Works After This Phase:**
All spec acceptance criteria met. Ready to close bug fixes and unblock COST-PATTERN epic.

---

## Risk Management

**See `design.md#potential-risks` for detailed risk analysis.**

**Phase-Specific Mitigations:**
- **Phase 1**: Low risk. All fixes are isolated. Full regression suite catches any unexpected name changes from Bug 6 underscore collapsing.
- **Phase 2**: Highest risk. Bug 2's `::` normalization in `_resolve_binding_to_usage()` uses recursive calls — ensure `visited` set prevents infinite loops. Bug 1's `param_groups` rebuild uses the same deriver — test that groupings match expectations.
- **Phase 3**: Low risk. `raise NotImplementedError` detection is a safe, conservative heuristic. No false positives possible for hand-written code (the whole point of implementing is to remove the raise).

---

## Implementation Notes

*(To be filled during implementation)*

### Phase 1 Completion
**Completed:** 2026-02-10
**Actual Changes:**
- Modified `src/sysml_codegen/core/qualified_names.py:12-27` — Added `import re`, enhanced `sanitize_name()` with `re.sub` for special char replacement, underscore collapsing, leading/trailing strip, "unnamed" fallback
- Modified `src/sysml_codegen/extraction/extractor.py` — Added `from sysml_codegen.core.qualified_names import sanitize_name`, replaced 6 `self._sanitize_name()` calls, deleted `_sanitize_name()` method (lines 616-624)
- Modified `src/sysml_codegen/extraction/expression_compiler.py:166-179` — Added `import re`, updated `_sanitize_name()` body with same regex logic (without reserved word check, by design)
- Modified `src/sysml_codegen/extraction/computed_attribute_extractor.py:179` — Sanitized `input_names` set via `{_sanitize_name(n) for n in sibling_attr_names}` for consistency with expression compiler
- Modified `src/sysml_codegen/cli/__init__.py` — Added `_ensure_package_init_files()` helper after `logger`; refactored `_generate_modules()`, `_generate_computed_attr_modules()`, `_generate_computed_attr_stencils()`, `_generate_stencils()` to use helper; removed `created_namespaces` sets
- Modified `src/sysml_codegen/cli/__init__.py:265` — Changed `"Float"` to `"float"` for FORMULA module input type_hint
- Created `tests/unit/test_qualified_names.py` — 13 parametrized tests for `sanitize_name()`
- Created `tests/unit/test_cli_generation.py` — 4 tests for `_ensure_package_init_files()`
- Modified `tests/unit/test_computed_attr_generation.py` — Added `TestFormulaModuleInputType` with 1 test

**Issues:** None

**Deviations:**
- **expression_compiler.py and computed_attribute_extractor.py changes (not in plan):** Design only specified removing the extractor's duplicate `_sanitize_name()`. However, `expression_compiler.py` has a THIRD copy of `_sanitize_name()` (without special char handling) that would become inconsistent after the extractor fix. Without updating it, CalcDef expression compilation would produce mismatched names for attributes with special characters (e.g., expression compiler produces `"Racking_&_Mounting"` but extractor produces `"Racking_Mounting"`). Fixed by: (1) adding same regex logic to expression_compiler's `_sanitize_name`, (2) sanitizing `input_names` in computed_attribute_extractor's FORMULA path so names match.

**Validation:**
- 303 tests passed, 0 failures (was 285+ baseline — grew from previous phases)
- mypy: 76 pre-existing errors, 0 new from Phase 1
- ruff: 17 pre-existing errors, 0 new from Phase 1

### Phase 2 Completion
**Completed:** 2026-02-10
**Actual Changes:**
- Modified `src/sysml_codegen/analysis/dependency_backtracker.py`:
  - **Change A:** Added SysML `::` qualified name as third key per FORMULA attr in `_computed_attr_index` (line ~145)
  - **Change B:** Added `::` bare-name fallback in `_trace_dependencies` computed attr check (line ~406)
  - **Change C (Strategy 5 — narrowed):** `::` normalization in `_resolve_binding_to_usage` now ONLY tries `_design_attr_binding_index` lookup with the normalized dotted path. Does NOT recurse through all resolution strategies, which previously allowed Strategy 2a (instance name match) to create self-dependencies.
  - **Self-reference guard:** Added check in `_trace_dependencies` after `_resolve_binding_to_usage`: if resolved usage has same `qualified_name` as current usage, treat as entry point (prevents self-loops from any resolution path).
  - **Self-edge guard:** Added `source_usage.qualified_name != usage.qualified_name` check in `_build_dependency_graph` to prevent self-edges in the dependency graph.
  - **`::` channel name normalization:** Added `::` -> dotted normalization in `_build_channel_name_for_binding` (line ~640) for `::` source paths that resolve via design attr transitive path.
- Modified `src/sysml_codegen/resolution/graph_builder.py`:
  - Extracted `_convert_derived_groups()` helper from `_group_entry_points_via_deriver()` (shared by Step 5 and Step 6.6)
  - Removed vestigial `param_groups` parameter from `_build_pipeline_module()` and `_build_computed_attr_module()` signatures and call sites
  - Added Step 6.6: Rebuild `param_groups` with ALL entry points (including FORMULA module inputs) after Step 6.5
- Modified `tests/unit/test_backtracker_computed_attrs.py`: Added `TestSysmlQualifiedNameIndex` (2 tests) and `TestColonColonBindingResolution` (2 tests)
- Modified `tests/unit/test_graph_builder_computed_attrs.py`: Added `TestParamGroupsRebuild` (2 tests); updated all `_build_computed_attr_module` call sites to remove `param_groups` arg

**Issues:** RESOLVED.

**Root Cause Analysis of :: Self-Dependency Regression:**
- SysIDE binding extraction produces self-referential `::` source_paths for REFERENCE bindings: `"Package::Part::CalcUsage::Param"` — the qualified name of the parameter itself, not the upstream source.
- Strategy 5 (original design) normalized ALL `::` paths to dotted format (`parts[-2].parts[-1]`), which for 4-segment self-referential paths produced `"CalcUsage.Param"`. Strategy 2a then matched `CalcUsage` as a usage instance name, creating a self-loop.
- Verified across all 4 test models: chain_spike (3 self-ref bindings), solar_battery (25 self-ref bindings), CATF MFE (1 self-ref binding), attr_expr_probe (0 self-ref bindings, all 3-segment cross-refs handled by Change A).
- Fix: Three-layer defense: (1) narrow Strategy 5 to only try `_design_attr_binding_index`, (2) self-reference guard in `_trace_dependencies`, (3) self-edge prevention in `_build_dependency_graph`.

**Deviations:**
- **Change C (Strategy 5) narrowed vs design's "top of method" placement:** Design specified normalizing ALL `::` paths to dotted and recursing through all strategies. Actual implementation narrows to only checking `_design_attr_binding_index` with the normalized path. Full recursion is unsafe because self-referential 4-segment `::` paths match calc usage instance names via Strategy 2a.
- **`_build_channel_name_for_binding` normalization (not in design):** Required for `::` source paths that resolve via design attr transitive path.
- **Self-reference guard (not in design):** Added as safety net — if ANY resolution path accidentally returns the same usage, treat as entry point.
- **Self-edge guard in `_build_dependency_graph` (not in design):** Defensive; `_build_dependency_graph` re-runs `_resolve_binding_to_usage` independently and could create self-edges without this guard.

### Phase 3 Completion
**Completed:** 2026-02-10
**Actual Changes:**
- Modified `src/sysml_codegen/cli/__init__.py` — Added `Compilability` import inside `_generate_stencils()`; replaced unconditional preserve in smart-regen else branch with stub-detection check: reads existing file, checks for `"raise NotImplementedError"` (stub marker) and `compilation_result.overall_compilability == Compilability.FULLY_COMPILABLE` (auto-impl available); if both true, backs up and upgrades stub; otherwise preserves as before.
- Modified `tests/unit/test_stencils.py` — Added `TestSmartRegenStubUpgrade` class with 4 tests: stub+compilable (upgrade), handwritten+compilable (preserve), auto-impl+compilable (preserve), stub+no-compilation (preserve). Tests use `unittest.mock.patch` to control `should_regenerate_stencil` return value, exercising only the preserve branch logic.
**Issues:** None
**Deviations:** None — implementation matches design exactly.

### Phase 4 Completion
**Completed:** 2026-02-10
**Actual Changes:** None (validation only)
**Issues:** None — both models generate cleanly with zero errors.
**Deviations:** Model paths are in fusion-tea (`/home/reid/1cfe/fusion-tea/models/tests/`) not sysml-codegen (no local `models/tests/` directory exists). Adjusted paths accordingly.

---

**Status**: ~~Draft~~ → ~~In Progress~~ → **Complete**
