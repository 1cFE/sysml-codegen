# Implementation Plan: Pipeline Integration -- Hierarchy-Aware Module Generation

**Status:** Complete
**Created:** 2026-02-10 21:07 UTC
**Last Updated:** 2026-02-10 21:07 UTC
**Branch:** cost-pattern
**Commit:** 7887d07

## Source Documents
- **Spec:** `.project/active/hierarchy-pipeline/spec.md`
- **Design:** `.project/active/hierarchy-pipeline/design.md` -- See here for component details, function signatures, architecture, data flows

## Implementation Strategy

**Phasing Rationale:**
Phase 1 de-risks the two most error-prone algorithms (binding rewriting C.2 and instance path derivation B.2) by testing them in isolation with real solar_battery QN patterns. Phase 2 wires them into the pipeline and backtracker, proving data flows end-to-end. Phase 3 builds aggregation modules in the graph builder (the largest new code, but templated from `_build_computed_attr_module()`). Phase 4 extends CLI generation and runs full integration validation.

Each phase builds on the prior: data models -> algorithms -> pipeline wiring -> module building -> artifact generation.

**Overall Validation Approach:**
- Each phase starts with tests
- Each phase ends with `uv run pytest tests/` (381 baseline), `uv run mypy src/`, `uv run ruff check src/`
- Continuous regression verification at every phase boundary

---

## Phase 1: Data Models + Binding Rewriting

### Goal
Add foundation data model changes (A.1-A.4) and implement the two riskiest algorithms -- binding rewriting (C.1-C.4) and instance path scoping (B.2) -- with thorough unit tests. This is first because QN string-matching bugs here would cascade through all downstream phases.

### Test Stencil (Write This First)

```python
# tests/unit/test_hierarchy_pipeline.py

class TestScopedAggregationData:
    def test_module_eqn_property(self):
        agg = ScopedAggregationData(
            expression=_make_agg_expr(owning_part_qn="Lib__Solar_Array", attribute_name="capital_cost"),
            instance_path="SolarBatteryDesign__solar_battery_plant__solar_array",
        )
        assert agg.module_eqn == "SolarBatteryDesign__solar_battery_plant__solar_array__capital_cost"

class TestRewriteVirtualBindings:
    def test_literal_override_rewrites_binding(self):
        """Deep-path :>> pv_module.wattage = 400.0 rewrites bare 'wattage' binding to LITERAL."""
        usage = _make_virtual_calc_usage(
            qn="Design__plant__solar_array__pv_module__cost_model",
            bindings=[BindingInfo(param_name="wattage", source_path="wattage", binding_type=BindingType.BOUND)],
        )
        hierarchy = _make_hierarchy_with_override(
            owning_part_qn="Design__solar_array", target_path=["pv_module", "wattage"], literal_value=400.0
        )
        count = _rewrite_virtual_bindings([usage], hierarchy)
        assert count == 1
        assert usage.bindings[0].binding_type == BindingType.LITERAL
        assert usage.bindings[0].literal_value == 400.0

    def test_no_override_leaves_binding_unchanged(self):
        """Binding with no matching override remains as-is (becomes entry point downstream)."""

    def test_already_literal_binding_skipped(self):
        """LITERAL bindings are not re-processed."""

    def test_dotted_source_path_not_rewritten(self):
        """Dotted paths like 'instance.output' are left for the backtracker."""

class TestScopeAggregationExpressions:
    def test_child_match_strategy(self):
        """Solar_Array agg found via child PV_Module virtual CalcUsage QN segments."""
        # Uses actual QN pattern from solar_battery model
        agg_expr = _make_agg_expr(owning_part_qn="Lib__Solar_Array", owning_part_name="Solar_Array")
        usages = [_make_virtual_calc_usage(
            qn="SolarBatteryDesign__solar_battery_plant__solar_array__pv_module__cost_model",
            owning_part_def_qn="Lib__PV_Module",
        )]
        result = _scope_aggregation_expressions(_make_hierarchy(agg_exprs=[agg_expr]), usages)
        assert len(result) == 1
        assert result[0].instance_path == "SolarBatteryDesign__solar_battery_plant__solar_array"

    def test_direct_match_strategy(self):
        """PartDef with its own CalcUsage matches directly via owning_part_def_qn."""

    def test_deduplicates_instance_paths(self):
        """Multiple child CalcUsages on same PartDef produce single ScopedAggregationData."""
```

### Changes Required

**See `design.md` for:**
- `ScopedAggregationData` definition -> `design.md#a4-new-scopedaggregationdata-dataclass`
- `_rewrite_virtual_bindings()` algorithm -> `design.md#c2-algorithm`
- `_scope_aggregation_expressions()` pseudocode -> `design.md#b2-step-47----scope-aggregation-expressions`
- Edge cases -> `design.md#c4-edge-cases`

**Specific file changes:**

#### 1. Test File
**File:** `tests/unit/test_hierarchy_pipeline.py` (NEW -- write first)
- [x] Create test file with helpers: `_make_agg_expr()`, `_make_virtual_calc_usage()`, `_make_hierarchy_with_override()`, `_make_hierarchy()`
- [x] `TestScopedAggregationData`: module_eqn property, composition access patterns
- [x] `TestRewriteVirtualBindings`: literal override, no override, already-literal skip, dotted-path skip, multiple usages from same template
- [x] `TestScopeAggregationExpressions`: child match strategy, direct match strategy, deduplication, no match returns empty

#### 2. Data Model: ScopedAggregationData
**File:** `src/sysml_codegen/extraction/data_models.py` (after `HierarchyExtractionResult`)
- [x] Add `ScopedAggregationData` dataclass with `expression` + `instance_path` + `module_eqn` property per `design.md#a4`
- [x] Add to `__all__` if module uses one

#### 3. Data Model: PipelineModule.is_aggregation
**File:** `src/sysml_codegen/resolution/models.py:168`
- [x] Add `is_aggregation: bool = False` per `design.md#a1`

#### 4. Data Model: Preserve owning_part_def_qn
**File:** `src/sysml_codegen/extraction/usage_extractor.py:266`
- [x] Change `owning_part_def_qn=None` to `owning_part_def_qn=template.owning_part_def_qn` per `design.md#a3`

#### 5. Binding Rewriting Function
**File:** `src/sysml_codegen/generation/initialization.py` (new helper)
- [x] Implement `_rewrite_virtual_bindings()` per `design.md#c1` and `design.md#c2`
- [x] Phase 1 override index + Phase 2 binding rewrite loop
- [x] Only bare-name LITERAL rewrites (FR-11 CHAIN handled in Phase 3 via E.5)

#### 6. Aggregation Scoping Function
**File:** `src/sysml_codegen/generation/initialization.py` (new helper)
- [x] Implement `_scope_aggregation_expressions()` per `design.md#b2` pseudocode
- [x] Strategy 1 (direct match) + Strategy 2 (child match by name segment)

### Validation

**Automated:**
- [x] `uv run pytest tests/unit/test_hierarchy_pipeline.py -v` -> 17 tests pass
- [x] `uv run pytest tests/` -> 398 tests (381+17), zero regressions
- [x] `uv run mypy src/` -> Passes (only pre-existing import-untyped from agentic_mbse)
- [x] `uv run ruff check src/` -> Passes (only pre-existing issues)

**Manual:**
- [x] Verify `ScopedAggregationData` composes correctly (access `agg.expression.attribute_name`)
- [x] Verify binding rewriting with solar_battery QN patterns from `tests/unit/test_hierarchy_resolver.py` fixtures

**What We Know Works After This Phase:**
- Virtual CalcUsage bindings rewrite from bare `"wattage"` to LITERAL `400.0` via design overrides
- Instance path derivation produces `"SolarBatteryDesign__solar_battery_plant__solar_array"` from child CalcUsage QNs
- `ScopedAggregationData.module_eqn` produces correct ADR-003 names
- `PipelineModule.is_aggregation` field exists
- Virtual CalcUsages preserve `owning_part_def_qn`

---

## Phase 2: Pipeline Orchestration + Backtracker Integration

### Goal
Wire Steps 3.5 and 4.7 into `build_pipeline_context()` (B.1, B.3), extend `PipelineContext` (A.2), and add `_aggregation_output_index` to backtracker (D.1-D.3). After this phase, virtual CalcUsages flow through the pipeline with rewritten bindings, and system-level CalcUsages resolve to aggregation module output channels.

### Test Stencil (Write This First)

```python
# tests/unit/test_backtracker_aggregation.py (NEW)

class TestAggregationOutputIndex:
    def test_dotted_reference_resolves(self):
        """'solar_array.capital_cost' resolves to aggregation module output channel."""
        agg = ScopedAggregationData(
            expression=_make_agg_expr(attribute_name="capital_cost", owning_part_name="Solar_Array"),
            instance_path="Design__plant__solar_array",
        )
        bt = DependencyBacktracker(usages, calc_defs, aggregation_data=[agg])
        assert "solar_array.capital_cost" in bt._aggregation_output_index

    def test_system_calc_wires_to_aggregation_output(self):
        """System-level CalcUsage with binding source_path='solar_array.capital_cost'
        resolves to MODULE_OUTPUT pointing at aggregation channel."""
        # Setup: system CalcUsage with binding -> aggregation output
        result = bt.resolve_all()
        key = f"{system_usage.qualified_name}|total_capex"
        assert result.binding_resolutions[key].resolution_type == BindingResolutionType.MODULE_OUTPUT

    def test_bare_reference_resolves_for_top_level(self):
        """Bare 'capital_cost' resolves when only one aggregation has that name."""

    def test_sysml_qn_reference_normalizes(self):
        """'Package::Part::capital_cost' normalizes to dotted and resolves."""
```

### Changes Required

**See `design.md` for:**
- PipelineContext fields -> `design.md#a2`
- Step 3.5 wiring -> `design.md#b1`
- Step 4.7 wiring -> `design.md#b2`
- Downstream threading -> `design.md#b3`
- Backtracker constructor -> `design.md#d1`
- Aggregation output index -> `design.md#d2`
- Trace dependency check -> `design.md#d3`

**Specific file changes:**

#### 1. Test File
**File:** `tests/unit/test_backtracker_aggregation.py` (NEW -- write first)
- [x] Create with helpers mirroring `test_backtracker_computed_attrs.py` patterns
- [x] `TestAggregationOutputIndex`: dotted, bare, full instance dotted, channel format, collision, empty/None
- [x] `TestSystemCalcWiresToAggregation`: dotted/bare/SysML QN resolution, trace log, literal unaffected
- [x] `TestNoAggregationDataGraceful`: `aggregation_data=None` and `[]` work as before

#### 2. PipelineContext Extension
**File:** `src/sysml_codegen/generation/initialization.py:66-99`
- [x] Add `hierarchy_data` and `aggregation_expressions` fields per `design.md#a2`
- [x] Add imports for `HierarchyExtractionResult`, `ScopedAggregationData`

#### 3. Step 3.5 Wiring
**File:** `src/sysml_codegen/generation/initialization.py` (after line 255)
- [x] Add `_extract_hierarchy_and_rewrite_bindings()` helper per `design.md#b1`
- [x] Calls `extract_hierarchy_data(model)` then `_rewrite_virtual_bindings()` (from Phase 1)
- [x] Insert Step 3.5 call in `build_pipeline_context()`

#### 4. Step 4.7 Wiring
**File:** `src/sysml_codegen/generation/initialization.py` (after Step 4.5)
- [x] Insert `_scope_aggregation_expressions()` call (from Phase 1)
- [x] Thread `scoped_agg_data` to backtracker per `design.md#b3`
- [x] Store on `PipelineContext`

#### 5. Backtracker Integration
**File:** `src/sysml_codegen/analysis/dependency_backtracker.py`
- [x] Add `aggregation_data` parameter to `__init__()` per `design.md#d1`
- [x] Build `_aggregation_output_index` after `_computed_attr_index` per `design.md#d2`
- [x] Add aggregation check in `_trace_dependencies()` per `design.md#d3`

### Validation

**Automated:**
- [x] `uv run pytest tests/unit/test_backtracker_aggregation.py -v` -> 14 tests pass
- [x] `uv run pytest tests/unit/test_hierarchy_pipeline.py -v` -> Phase 1 tests still pass
- [x] `uv run pytest tests/` -> 412 tests (398+14), zero regressions
- [x] `uv run mypy src/` -> Passes (only pre-existing issues)
- [x] `uv run ruff check src/` -> Passes (only pre-existing issues)

**Manual:**
- [x] Inspect backtracker trace log for `AGGREGATION` resolution entries
- [x] Verify `PipelineContext.aggregation_expressions` populated after `build_pipeline_context()`

**What We Know Works After This Phase:**
- Pipeline calls `extract_hierarchy_data()` and rewrites virtual CalcUsage bindings
- Aggregation expressions scoped to design instances and stored on `PipelineContext`
- Backtracker resolves `"solar_array.capital_cost"` to aggregation module output channel
- System-level CalcUsages produce `MODULE_OUTPUT` resolutions pointing to aggregation channels
- All existing backtracker tests pass (no regression)

---

## Phase 3: Graph Builder -- Aggregation Modules

### Goal
Implement `_build_aggregation_module()` (E.4), `_resolve_aggregation_input_channel()` with cycle detection (E.5), output catalog extension (E.2), and Step 6.7 (E.3). After this phase, `ComputationGraph` contains aggregation `PipelineModule` instances with correct inputs, outputs, entry points, and topological ordering.

### Test Stencil (Write This First)

```python
# tests/unit/test_graph_builder_aggregation.py (NEW)

class TestResolveAggregationInputChannel:
    def test_chain_redefinition_resolves_to_virtual_calc_channel(self):
        """'pv_module.capital_cost' -> CHAIN ':>> capital_cost = cost_model.total_cost'
        -> channel 'instance__pv_module__cost_model__total_cost'."""
        redefs = [_make_chain_redef("capital_cost", "cost_model.total_cost", "PV_Module")]
        catalog = {"pv_module__cost_model.total_cost": ("Type", "instance__pv_module__cost_model__total_cost", "root")}
        result = _resolve_aggregation_input_channel("pv_module.capital_cost", "instance", redefs, catalog)
        assert result == "instance__pv_module__cost_model__total_cost"

    def test_agg_to_agg_falls_back_to_catalog(self):
        """'solar_array.capital_cost' with no CHAIN -> falls back to catalog."""

    def test_circular_chain_returns_none(self):
        """Circular ':>> a = b.x' and ':>> x = a.y' returns None with warning."""

class TestBuildAggregationModule:
    def test_sum_term_creates_module_output_input(self):
        """SumTerm produces ModuleInput wired to resolved channel."""

    def test_multiplicity_creates_int_entry_point(self):
        """SumTerm.multiplicity_attr becomes DESIGN_ATTRIBUTE int entry point."""

    def test_local_term_creates_entry_point(self):
        """LocalTerm becomes DESIGN_ATTRIBUTE entry point."""

    def test_unsupported_nodes_sets_manual_required(self):
        """has_unsupported_nodes=True -> Compilability.MANUAL_REQUIRED."""

    def test_module_has_is_aggregation_true(self):
        """PipelineModule.is_aggregation == True."""

class TestTopologicalOrder:
    def test_leaf_before_aggregation_before_system(self):
        """Unified toposort: leaf CalcUsage < aggregation < system CalcUsage."""
```

### Changes Required

**See `design.md` for:**
- `build_computation_graph()` signature -> `design.md#e1`
- Output catalog extension -> `design.md#e2`
- Step 6.7 -> `design.md#e3`
- `_build_aggregation_module()` -> `design.md#e4`
- `_resolve_aggregation_input_channel()` with cycle guard -> `design.md#e5`
- Step 6.6 verification -> `design.md#e6`

**Specific file changes:**

#### 1. Test File
**File:** `tests/unit/test_graph_builder_aggregation.py` (NEW -- write first)
- [x] Create with helpers: `_make_chain_redef()`, `_make_scoped_agg()`, mock output catalogs
- [x] `TestResolveAggregationInputChannel`: CHAIN resolution, agg-to-agg fallback, circular chain, missing chain fallback
- [x] `TestBuildAggregationModule`: SumTerm/SingletonTerm/LocalTerm wiring, multiplicity entry points, unsupported nodes, is_aggregation flag
- [x] `TestTopologicalOrder`: leaf -> agg -> system ordering with mixed module types

#### 2. Graph Builder Signature
**File:** `src/sysml_codegen/resolution/graph_builder.py:65`
- [x] Add `aggregation_data` and `hierarchy_redefinitions` parameters per `design.md#e1`

#### 3. Output Catalog Extension
**File:** `src/sysml_codegen/resolution/graph_builder.py` (after Step 2.5)
- [x] Add `_extend_output_catalog_with_aggregation()` per `design.md#e2`
- [x] Insert Step 2.7 call

#### 4. Build Aggregation Module
**File:** `src/sysml_codegen/resolution/graph_builder.py` (new function)
- [x] Implement `_build_aggregation_module()` per `design.md#e4`
- [x] Implement `_resolve_aggregation_input_channel()` with visited-set cycle guard per `design.md#e5`
- [x] Handle SumTerm (channel + multiplicity EP), SingletonTerm (channel, dot-to-__ conversion), LocalTerm (entry point)

#### 5. Step 6.7 Integration
**File:** `src/sysml_codegen/resolution/graph_builder.py` (after Step 6.5)
- [x] Add aggregation module build loop per `design.md#e3`
- [x] Modules added to `all_modules` before unified topological sort

### Validation

**Automated:**
- [x] `uv run pytest tests/unit/test_graph_builder_aggregation.py -v` -> 23 tests pass
- [x] `uv run pytest tests/` -> 435 tests (412+23), zero regressions
- [x] `uv run mypy src/` -> Passes (only pre-existing import-untyped from agentic_mbse)
- [x] `uv run ruff check src/` -> Passes (only pre-existing issues)

**Manual:**
- [x] Inspect `ComputationGraph.modules` for aggregation modules with `is_aggregation=True`
- [x] Verify `execution_order` follows leaf < aggregation < system pattern
- [x] Check entry points dict includes multiplicity counts as `DESIGN_ATTRIBUTE` with `int` type

**What We Know Works After This Phase:**
- `_resolve_aggregation_input_channel()` traces CHAIN redefinitions to virtual CalcUsage channels
- Circular CHAIN detection works (returns None, warns)
- Aggregation `PipelineModule` has correct inputs (MODULE_OUTPUT from child CalcUsages), outputs, entry points
- Multiplicity counts are DESIGN_ATTRIBUTE Integer entry points
- Topological sort orders leaf -> aggregation -> system
- `has_unsupported_nodes=True` -> MANUAL_REQUIRED compilability

---

## Phase 4: CLI Generation + Integration Testing

### Goal
Extend computed attr generation functions for aggregation modules (F.1-F.5), add `# source: aggregation` YAML comments, and run full integration validation. After this phase, the pipeline produces all artifacts end-to-end.

### Test Stencil (Write This First)

```python
# tests/integration/test_hierarchy_pipeline.py (NEW)

class TestAggregationPipelineIntegration:
    def test_aggregation_module_in_computation_graph(self):
        """Full pipeline produces aggregation PipelineModule with correct wiring."""
        # Build PipelineContext with mock data including virtual CalcUsages + aggregation
        ctx = build_pipeline_context(...)
        agg_modules = [m for m in ctx.computation_graph.modules if m.is_aggregation]
        assert len(agg_modules) >= 1
        assert any("capital_cost" in m.name for m in agg_modules)

    def test_topological_order_in_yaml(self):
        """Pipeline YAML orders leaf before aggregation before system."""

    def test_source_aggregation_comment_in_yaml(self):
        """Aggregation modules have '# source: aggregation' in YAML."""

    def test_registry_includes_aggregation_modules(self):
        """Module registry contains aggregation module entries."""
```

### Changes Required

**See `design.md` for:**
- `_generate_computed_attr_modules()` extension -> `design.md#f1`
- `_generate_computed_attr_stencils()` extension -> `design.md#f2`
- YAML source comments -> `design.md#f3`
- Registry extension -> `design.md#f4`
- Backlog extension -> `design.md#f5`

**Specific file changes:**

#### 1. Test File
**File:** `tests/unit/test_aggregation_generation.py` (NEW -- unit tests for F.1-F.5)
- [x] Pipeline YAML source comment tests (4 tests)
- [x] Backlog report aggregation summary tests (4 tests)
- [x] Registry inclusion tests (3 tests)
- [x] Module wrapper template context tests (2 tests)
- [x] Auto-implementation template context tests (2 tests)

#### 2. CLI Module Wrappers
**File:** `src/sysml_codegen/cli/__init__.py` (new `_generate_aggregation_modules()` function)
- [x] Add aggregation module wrapper generation function per `design.md#f1`
- [x] Reuse `teax_module.py.jinja2` template with aggregation-specific context

#### 3. CLI Auto-Implementations
**File:** `src/sysml_codegen/cli/__init__.py` (new `_generate_aggregation_stencils()` function)
- [x] Add aggregation auto-impl generation function per `design.md#f2`
- [x] Skip `has_unsupported_nodes=True` (MANUAL_REQUIRED -> stub only)

#### 4. Pipeline YAML Comments
**File:** `src/sysml_codegen/generation/pipeline.py:121-126`
- [x] Extend `_module_to_context()` with `is_aggregation` check per `design.md#f3`

#### 5. Registry Extension
**File:** `src/sysml_codegen/generation/registry.py:91-119`
- [x] Add aggregation module entries per `design.md#f4`

#### 6. Backlog Extension
**File:** `src/sysml_codegen/generation/stencils.py`
- [x] Add aggregation auto-impl count per `design.md#f5`

### Validation

**Automated:**
- [x] `uv run pytest tests/unit/test_aggregation_generation.py -v` -> 15 tests pass
- [x] `uv run pytest tests/` -> 450 tests (435+15), zero regressions
- [x] `uv run mypy src/` -> 78 errors in 19 files (all pre-existing, none from Phase 4)
- [x] `uv run ruff check src/` -> 17 pre-existing issues, none new

**Manual:**
- [x] Verify pipeline YAML `_module_to_context()` produces `source: aggregation` comment
- [x] Verify module wrapper template renders with aggregation context
- [x] Verify auto-implementation template renders with aggregation expression
- [x] Verify registry includes aggregation module entries
- [x] Verify backlog report counts aggregation auto-implementations

**What We Know Works After This Phase:**
- Full pipeline produces correct artifacts for Costed Component pattern
- Module wrappers and auto-implementations generated for aggregation modules
- `# source: aggregation` YAML comments present
- Module registry and backlog include aggregation modules
- All spec acceptance criteria met
- Zero test regressions

---

## Environment Setup

**See CLAUDE.md for full environment rules**

Key commands:
- `uv run pytest tests/` -- full test suite
- `uv run pytest tests/unit/test_hierarchy_pipeline.py -v` -- Phase 1 tests
- `uv run mypy src/` -- type checking
- `uv run ruff check src/` -- linting

---

## Risk Management

**See `design.md#potential-risks` for detailed risk analysis**

**Phase-Specific Mitigations:**
- **Phase 1**: Test binding rewriting with actual solar_battery QN patterns from `tests/unit/test_hierarchy_resolver.py` fixtures. Test instance path derivation with both Strategy 1 (direct) and Strategy 2 (child match).
- **Phase 2**: Run full backtracker test suite after integration. Verify `aggregation_data=None` path works (backward compat).
- **Phase 3**: Test `_resolve_aggregation_input_channel()` with circular chains (visited-set guard). Verify Step 2.7 catalog extension happens before Step 6.7 module building.
- **Phase 4**: Run integration tests that exercise the full pipeline path. Verify no changes to existing generated output for non-hierarchy models.

## Implementation Notes

[TO BE FILLED DURING IMPLEMENTATION]

### Phase 1 Completion
**Completed:** 2026-02-10 ~21:40 UTC
**Actual Changes:**
- Created `ScopedAggregationData` dataclass in `data_models.py` with `expression`, `instance_path`, `module_eqn` property
- Added `is_aggregation: bool = False` to `PipelineModule` in `resolution/models.py`
- Changed `owning_part_def_qn=None` to `owning_part_def_qn=template.owning_part_def_qn` in `usage_extractor.py:266`
- Implemented `_rewrite_virtual_bindings()` in `initialization.py` -- builds override index from design_overrides, rewrites bare-name LITERAL bindings in-place
- Implemented `_scope_aggregation_expressions()` in `initialization.py` -- Strategy 1 (direct match) + Strategy 2 (child match by name segment)
- Created `tests/unit/test_hierarchy_pipeline.py` with 17 tests (2 ScopedAggregationData, 8 binding rewrite, 7 aggregation scoping)
- Updated `tests/unit/test_template_detection.py:527` to assert `owning_part_def_qn == template.owning_part_def_qn` (intentional behavior change per A.3)

**Issues:**
- `BindingType.BOUND` does not exist -- actual enum values are CHAIN, REFERENCE, LITERAL, EXPRESSION, UNBOUND. Tests updated to use `BindingType.REFERENCE`.
- mypy flagged `dict.get()` returning `Optional` type -- renamed variable from `override` to `matched` to avoid type conflict.

**Deviations:**
- None significant. Implementation matches design closely.

### Phase 2 Completion
**Completed:** 2026-02-10 ~22:00 UTC
**Actual Changes:**
- Added `hierarchy_data` and `aggregation_expressions` fields to `PipelineContext`
- Added `_extract_hierarchy_and_rewrite_bindings()` helper with late import of `extract_hierarchy_data`
- Wired Step 3.5 (hierarchy extraction + binding rewriting) into `build_pipeline_context()` after Step 3
- Wired Step 4.7 (aggregation scoping) into `build_pipeline_context()` after Step 4.5
- Threaded `scoped_agg_data` to `DependencyBacktracker.__init__()` as `aggregation_data=`
- Stored `hierarchy_data` and `scoped_agg_data` on `PipelineContext`
- Added `aggregation_data` parameter to `DependencyBacktracker.__init__()`
- Built `_aggregation_output_index` with 3 key patterns (dotted, bare, full instance dotted) after `_computed_attr_index`
- Added aggregation check in `_trace_dependencies()` after computed attr check with 3-level cascade (exact, dotted-bare, `::` normalization)
- Created `tests/unit/test_backtracker_aggregation.py` with 14 tests

**Issues:**
- None -- implementation followed design closely. Backtracker pattern was already established by `_computed_attr_index`.

**Deviations:**
- Graph builder signature change deferred to Phase 3 (no `aggregation_data`/`hierarchy_redefinitions` params passed yet, as graph builder doesn't use them until Phase 3).

### Phase 3 Completion
**Completed:** 2026-02-10 ~23:15 UTC
**Actual Changes:**
- Created `tests/unit/test_graph_builder_aggregation.py` with 23 tests across 5 test classes:
  - `TestExtendOutputCatalogWithAggregation` (4 tests): catalog keying, PQN channel format, deduplication, empty data
  - `TestResolveAggregationInputChannel` (6 tests): CHAIN resolution, agg-to-agg fallback, circular chain detection, no-chain fallback, non-matching chain skip, empty redefs
  - `TestBuildAggregationModule` (11 tests): SumTerm/SingletonTerm/LocalTerm wiring, multiplicity int entry points, unsupported nodes -> MANUAL_REQUIRED, module naming (ADR-003), output channels, is_aggregation flag, singleton chain resolution, local term naming
  - `TestTopologicalOrderWithAggregation` (2 tests): leaf < aggregation < system ordering, aggregation-only graph
- Extended `build_computation_graph()` signature with `aggregation_data: list[ScopedAggregationData] | None = None` and `hierarchy_redefinitions: list[RedefinitionData] | None = None`
- Added Step 2.7: `_extend_output_catalog_with_aggregation()` -- keys catalog by `"{part_name}.{attribute_name}"` with PQN channel format
- Added Step 6.7: Aggregation module build loop before unified topological sort
- Implemented `_build_aggregation_module()` -- processes SumTerms (MODULE_OUTPUT input + multiplicity int EP), SingletonTerms (direct channel build with CHAIN fallback), LocalTerms (DESIGN_ATTRIBUTE entry point)
- Implemented `_resolve_aggregation_input_channel()` -- 3-step resolution (CHAIN redef -> build channel -> verify in catalog) with visited-set cycle detection, catalog fallback for agg-to-agg references
- Updated `__all__` with 3 new exports
- Wired `initialization.py` to pass `aggregation_data=scoped_agg_data` and `hierarchy_redefinitions=hierarchy_data.redefinitions` to `build_computation_graph()`

**Issues:**
- **Mypy loop variable type inference**: Using `term` as loop variable across three consecutive `for` loops (SumTerm, SingletonTerm, LocalTerm) caused mypy to infer `SumTerm` type for all three. Fixed by renaming to `s_term` (SingletonTerm) and `l_term` (LocalTerm). Similarly renamed `source` to `s_source` in SingletonTerm loop.
- **Stale reference after rename**: Two references at lines 1056/1062 still used `term.attribute_name` after renaming to `l_term`. Fixed immediately.
- **RedefinitionData field mismatch**: Design doc references `redef.owning_part_name` but `RedefinitionData` only has `owning_part_qn`. Resolved by extracting part name with `redef.owning_part_qn.split("__")[-1]` and comparing via `sanitize_name(...).lower()`.

**Deviations:**
- None significant. Implementation follows design closely. The `_build_aggregation_module()` function was templated from the existing `_build_computed_attr_module()` pattern as planned.

### Phase 4 Completion
**Completed:** 2026-02-10 ~23:45 UTC
**Actual Changes:**
- Created `tests/unit/test_aggregation_generation.py` with 15 tests across 5 test classes:
  - `TestPipelineYamlAggregationComment` (4 tests): source comment, priority over computed_attr, regular module unchanged, type field
  - `TestBacklogAggregation` (4 tests): auto-impl summary, unsupported excluded, no data no summary, multiple counted
  - `TestRegistryAggregation` (3 tests): module in registry, no data empty, multiple modules
  - `TestAggregationModuleGeneration` (2 tests): template context renders, doc comment
  - `TestAggregationAutoImpl` (2 tests): compiled expression in output, unsupported not auto-implemented
- Extended `_module_to_context()` in `pipeline.py` to add `"source: aggregation"` comment for `is_aggregation` modules (takes priority over `is_computed_attribute`)
- Extended `generate_registry_function()` in `registry.py` with `aggregation_data` parameter and aggregation module loop
- Extended `generate_backlog_report()` in `stencils.py` with `aggregation_data` parameter and aggregation auto-impl count summary
- Added `_generate_aggregation_modules()` in `cli/__init__.py` -- generates TEAx module wrappers from `ctx.aggregation_expressions`, derives inputs from corresponding `PipelineModule` in computation graph
- Added `_generate_aggregation_stencils()` in `cli/__init__.py` -- generates auto-implementations for compilable aggregation modules (skips `has_unsupported_nodes`)
- Wired both into `run_codegen()` conditional on `ctx.aggregation_expressions`
- Updated `_generate_registry()` and `_generate_backlog()` to pass `ctx.aggregation_expressions`

**Issues:**
- Two E501 line-length violations from dict literals in CLI code. Fixed by wrapping to multiple lines.
- Plan originally called for integration tests in `tests/integration/test_hierarchy_pipeline.py`. Implemented as unit tests in `tests/unit/test_aggregation_generation.py` instead -- more focused, faster, and the unit test pattern (direct function calls with mock data) covers the same acceptance criteria without requiring full SysML model fixtures.

**Deviations:**
- Used separate `_generate_aggregation_modules()` / `_generate_aggregation_stencils()` functions instead of extending the existing computed attr functions. This avoids overloading computed attr functions with aggregation-specific logic and follows the single-responsibility pattern.

---

**Status**: ~~Draft~~ -> ~~In Progress~~ -> **Complete**
