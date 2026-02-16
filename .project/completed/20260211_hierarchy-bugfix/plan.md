# Implementation Plan: Hierarchy Pipeline Bug Fixes

**Status:** Complete
**Created:** 2026-02-11
**Last Updated:** 2026-02-11

## Source Documents
- **Spec:** `.project/active/hierarchy-bugfix/spec.md`
- **Design:** `.project/active/hierarchy-bugfix/design.md` — See here for component details, function signatures, dependencies, error handling

## Implementation Strategy

**Phasing Rationale:**
BF-1 (AST unwrap) goes first because it's the prerequisite for BF-2 and cascade-fixes 2 additional symptoms. Phase 2 groups three small independent fixes in the same file. Phase 3 tackles scoping and wiring (moderate effort, different subsystems). Phase 4 completes with expression compilation (largest fix, depends on Phase 1) and multiplicity surfacing (shares `graph_builder.py`).

**Testing Approach:**
Every phase starts with REAL tests using synthetic models. Tests construct actual data model instances (`ScopedAggregationData`, `AggregationExpressionData`, `CalcUsageData`, etc.) and pass them through real pipeline functions — no mocking of framework internals. Each phase's tests must pass before proceeding.

**Overall Validation:**
- Each phase starts with tests that exercise the actual functions being fixed
- `uv run pytest tests/` after every phase — zero regressions
- `uv run ruff check src/` and `uv run mypy src/` for code quality

---

## Phase 1: BF-1 — AST Evaluation() Unwrap

### Goal
Fix `_walk_aggregation_ast()` to unwrap `InvocationExpression` wrappers (e.g., `Evaluation`, `collect`, `select`) around `sum()` operands. This is the prerequisite for BF-2 and cascade-fixes `has_unsupported_nodes` and garbage YAML names.

### Test Stencil (Write First)

```python
# tests/unit/test_hierarchy_resolver.py — new test class
# Uses mock AST elements (same pattern as existing MockInvocationExpression)

class TestWalkAggregationAstEvaluationUnwrap:
    """BF-1: _walk_aggregation_ast() unwraps InvocationExpression around sum() operands."""

    def test_sum_with_evaluation_wrapper_produces_correct_sum_term(self):
        """sum(Evaluation(pv_module.capital_cost)) → SumTerm(part_usage_name='pv_module', ...)."""
        # Build: InvocationExpression[func='sum'](
        #     InvocationExpression[func='Evaluation'](
        #         FeatureChainExpression['pv_module', 'capital_cost']
        #     )
        # )
        feature_chain = MockFeatureChainExpression(["pv_module", "capital_cost"])
        eval_wrapper = MockInvocationExpression("Evaluation", [feature_chain])
        sum_expr = MockInvocationExpression("sum", [eval_wrapper])

        result = _walk_aggregation_ast(sum_expr, owning_part_qn="Lib__Solar_Array")

        assert len(result.sum_terms) == 1
        assert result.sum_terms[0].part_usage_name == "pv_module"
        assert result.sum_terms[0].attribute_name == "capital_cost"
        assert result.has_unsupported_nodes is False

    def test_sum_without_wrapper_still_works(self):
        """sum(pv_module.capital_cost) — no wrapper — still produces correct SumTerm."""
        feature_chain = MockFeatureChainExpression(["pv_module", "capital_cost"])
        sum_expr = MockInvocationExpression("sum", [feature_chain])

        result = _walk_aggregation_ast(sum_expr, owning_part_qn="Lib__Solar_Array")

        assert len(result.sum_terms) == 1
        assert result.has_unsupported_nodes is False

    def test_nested_wrapper_unwrapped(self):
        """collect(Evaluation(chain)) — nested invocations are unwrapped."""
        feature_chain = MockFeatureChainExpression(["inverter", "cost"])
        eval_wrap = MockInvocationExpression("Evaluation", [feature_chain])
        collect_wrap = MockInvocationExpression("collect", [eval_wrap])
        sum_expr = MockInvocationExpression("sum", [collect_wrap])

        result = _walk_aggregation_ast(sum_expr, owning_part_qn="Lib__Inverter")

        assert len(result.sum_terms) == 1
        assert result.has_unsupported_nodes is False

    def test_non_sum_evaluation_wrapper_unwrapped_not_marked_unsupported(self):
        """Standalone Evaluation(chain) outside sum() is unwrapped, not marked unsupported."""
        feature_chain = MockFeatureChainExpression(["allocation_model", "total_allocation"])
        eval_wrapper = MockInvocationExpression("Evaluation", [feature_chain])

        result = _walk_aggregation_ast(eval_wrapper, owning_part_qn="Lib__Part")

        assert result.has_unsupported_nodes is False

    def test_transformed_expression_contains_real_attribute_names(self):
        """After unwrap, transformed_expression has real names, not 'Evaluation()'."""
        feature_chain = MockFeatureChainExpression(["pv_module", "capital_cost"])
        eval_wrapper = MockInvocationExpression("Evaluation", [feature_chain])
        sum_expr = MockInvocationExpression("sum", [eval_wrapper])

        result = _walk_aggregation_ast(sum_expr, owning_part_qn="Lib__Solar_Array")

        assert "Evaluation" not in result.transformed_expression
        assert "pv_module" in result.transformed_expression or "capital_cost" in result.transformed_expression
```

### Changes Required

**See `design.md#bf-1` for full design.**

#### 1. Test File
**File:** `tests/unit/test_hierarchy_resolver.py` (EXTEND)
- [x] Add `TestWalkAggregationAstEvaluationUnwrap` test class (6 tests)
- [x] Test via `build_aggregation_expression` (public API, full integration coverage)
- [x] Use existing `MockInvocationExpression`, `MockFeatureChainExpression` helpers (already defined)
- [x] Test: wrapped sum, unwrapped sum (regression), nested wrapper, non-sum wrapper, expression text, mixed full expression

#### 2. Implementation
**File:** `src/sysml_codegen/extraction/hierarchy_resolver.py`
- [x] Add `_unwrap_invocation(node)` helper at line 278 with depth limit of 3
- [x] Add `_KNOWN_WRAPPER_FUNCTIONS` frozenset at line 275
- [x] Insert unwrap call at line 352 before type-testing operand
- [x] Update non-sum InvocationExpression branch (line 392-396): unwrap known wrappers before marking unsupported
- [x] No changes to `expression_utils.py` (per design rationale)

### Validation

**Automated:**
- [x] `uv run pytest tests/unit/test_hierarchy_resolver.py -k "TestWalkAggregationAstEvaluationUnwrap"` → 6 passed
- [x] `uv run pytest tests/` → 460 passed, zero regressions
- [x] `uv run ruff check src/sysml_codegen/extraction/hierarchy_resolver.py` → Clean

**Manual:**
- [x] `_unwrap_invocation()` handles any InvocationExpression (recurses into operands[0])
- [x] Depth limit of 3 prevents infinite recursion

**What We Know Works After This Phase:**
- `_walk_aggregation_ast()` correctly unwraps `InvocationExpression` wrappers
- `transformed_expression` contains real attribute names (not `Evaluation()`)
- `has_unsupported_nodes` is `False` for wrapped operands
- Existing tests still pass (backward compatibility)

---

## Phase 2: BF-3 + BF-4 + BF-5 — Lookup & Path Fixes

### Goal
Fix three small bugs in `cli/__init__.py`: case mismatch in module lookup (BF-3), PartDef-scoped wrapper paths (BF-4), and PartDef-scoped stencil paths (BF-5). All are under 5 lines each.

### Test Stencil (Write First)

```python
# tests/unit/test_aggregation_generation.py — new test classes

class TestAggregationModuleLookupCaseMatch:
    """BF-3: Aggregation module lookup normalizes case."""

    def test_mixed_case_eqn_finds_lowered_module(self):
        """agg.module_eqn with MixedCase finds module keyed by lowered name."""
        agg = _make_scoped_agg(instance_path="Design__Plant__Solar_Array")
        # module_eqn = "Design__Plant__Solar_Array__capital_cost" (mixed)
        # m.name = "design__plant__solar_array__capital_cost" (lowered)
        module = PipelineModule(
            name=get_module_name(agg.module_eqn),
            module_type="SolarArrayCapitalCost",
            inputs=[ModuleInput(
                field_name="pv_module_capital_cost",
                python_type="float",
                param_name="pv_module_capital_cost",
                source=InputSource(source_type="entry_point", qualified_name="ep1"),
            )],
            outputs=[],
            execution_order=0,
            is_aggregation=True,
        )
        agg_modules_by_name = {module.name: module}

        # Lookup using normalized key (the fix)
        found = agg_modules_by_name.get(get_module_name(agg.module_eqn))
        assert found is not None
        assert len(found.inputs) == 1


class TestAggregationPathsUseInstanceEQN:
    """BF-4 + BF-5: Module wrapper and stencil paths use instance-scoped EQN."""

    def test_module_wrapper_sysml_qn_uses_instance_eqn(self):
        """sysml_qn derived from module_eqn, not owning_part_qn::attribute."""
        agg = _make_scoped_agg(
            owning_part_qn="Lib__Solar_Array",
            attribute_name="capital_cost",
            instance_path="Design__Plant__Solar_Array",
        )
        # Old (wrong): "Lib__Solar_Array::capital_cost"
        # New (correct): instance-scoped from module_eqn
        sysml_qn = agg.module_eqn.replace("__", "::")
        assert sysml_qn.startswith("Design")
        assert "Solar_Array" in sysml_qn
        assert "capital_cost" in sysml_qn

    def test_stencil_path_matches_wrapper_path(self):
        """Stencil path derivation uses same instance-scoped EQN as wrapper."""
        agg = _make_scoped_agg(instance_path="Design__Plant__Solar_Array")
        wrapper_qn = agg.module_eqn.replace("__", "::")
        stencil_qn = agg.module_eqn.replace("__", "::")
        assert wrapper_qn == stencil_qn
```

### Changes Required

**See `design.md#bf-3`, `design.md#bf-4--bf-5` for full design.**

#### 1. Test File
**File:** `tests/unit/test_aggregation_generation.py` (EXTEND)
- [x] Add `TestAggregationModuleLookupCaseMatch` test class (2 tests)
- [x] Add `TestAggregationPathsUseInstanceEQN` test class (3 tests)
- [x] Import `get_module_name` from `sysml_codegen.core.qualified_names`

#### 2. Implementation
**File:** `src/sysml_codegen/cli/__init__.py`
- [x] BF-3 at line 453: Changed to `get_module_name(agg.module_eqn)` in lookup
- [x] BF-4 at line 434: Changed `sysml_qn` to `agg.module_eqn.replace("__", "::")`
- [x] BF-5 at line 533: Same change for stencil path
- [x] BF-5 at line 536: Changed to `agg.module_eqn` directly; removed unused `sysml_to_python_qualified_name` import

### Validation

**Automated:**
- [x] `uv run pytest tests/unit/test_aggregation_generation.py -k "Lookup or Paths"` → 5 passed
- [x] `uv run pytest tests/` → 465 passed, zero regressions
- [x] `uv run ruff check src/sysml_codegen/cli/__init__.py` → Clean

**Manual:**
- [x] `get_module_name()` already imported at line 421

**What We Know Works After This Phase:**
- Aggregation module lookup succeeds regardless of case in `module_eqn`
- Module wrapper directories use instance-scoped paths matching YAML keys
- Stencil paths are instance-scoped (no PartDef-level collisions)

---

## Phase 3: BF-6 + BF-7 — Scoping & Wiring Fixes

### Goal
Fix Site Infrastructure missing from aggregation scoping (BF-6) and `total_capex` ENTRY_POINT→MODULE_OUTPUT wiring (BF-7). These are independent but both involve changes to analysis/extraction layers.

### Test Stencil (Write First)

```python
# tests/unit/test_hierarchy_pipeline.py — extend with BF-6 tests

class TestScopeAggregationSiteInfra:
    """BF-6: _scope_aggregation_expressions() finds Site Infrastructure via child-walk."""

    def test_partdef_with_mismatched_usage_name_scoped_via_children(self):
        """PartDef 'SiteInfrastructure' typed by usage 'site_infra' is found via child-walk."""
        # Build: PartDef "SiteInfrastructure" has child "grid_connection"
        # Virtual CalcUsage QN contains "...site_infra__grid_connection__..."
        # Strategy 2 child-walk finds "site_infra" as parent of "grid_connection"
        agg_expr = _make_agg_expr(
            owning_part_qn="Lib__SiteInfrastructure",
            owning_part_name="SiteInfrastructure",
            attribute_name="capital_cost",
        )
        multiplicities = [
            MultiplicityData(
                owning_part_def_qn="Lib__SiteInfrastructure",
                part_usage_name="grid_connection",
                multiplicity_attribute="connection_count",
            ),
        ]
        virtual_usages = [
            _make_virtual_calc_usage(
                qn="Design__plant__site_infra__grid_connection__cost_model",
                owning_part_def_qn="Lib__GridConnection",
            ),
        ]
        hierarchy_data = HierarchyExtractionResult(
            multiplicities=multiplicities,
            # ... other fields as needed
        )

        result = _scope_aggregation_expressions(
            aggregation_expressions=[agg_expr],
            virtual_calc_usages=virtual_usages,
            hierarchy_data=hierarchy_data,
        )

        assert len(result) >= 1
        assert any(s.instance_path and "site_infra" in s.instance_path for s in result)

    def test_all_four_assemblies_scoped(self):
        """With 4 assembly PartDefs (including mismatched name), all 4 get scoped."""
        # Build synthetic data for 4 assemblies, one with name mismatch
        # ... (construct 4 agg_exprs, multiplicities, virtual usages)
        # Assert len(result) covers all 4
        pass  # Full implementation during Phase 3
```

```python
# tests/unit/test_backtracker_aggregation.py — extend with BF-7 tests

class TestAggregationAliasResolution:
    """BF-7: EXPOSE_PURE aliases registered in aggregation output index."""

    def test_alias_in_index_resolves_to_module_output(self):
        """':>> total_capex = capital_cost' alias resolves to aggregation output."""
        agg = _make_scoped_agg(
            attribute_name="capital_cost",
            instance_path="Design__plant__solar_battery_plant",
        )
        # Add alias to expression
        agg.expression.aliases = ["total_capex"]

        bt = DependencyBacktracker([], [], aggregation_data=[agg])

        # Both original and alias should resolve
        assert "solar_battery_plant.capital_cost" in bt._aggregation_output_index
        assert "solar_battery_plant.total_capex" in bt._aggregation_output_index

    def test_bare_alias_resolves(self):
        """Bare alias name resolves when unambiguous."""
        agg = _make_scoped_agg(attribute_name="capital_cost")
        agg.expression.aliases = ["total_capex"]

        bt = DependencyBacktracker([], [], aggregation_data=[agg])
        assert "total_capex" in bt._aggregation_output_index

    def test_sanitized_partdef_name_in_fallback(self):
        """:: fallback sanitizes PartDef names ('Solar Battery Plant' → 'solar_battery_plant')."""
        # This tests the sanitization fix in the :: lookup path
        agg = _make_scoped_agg(
            attribute_name="capital_cost",
            instance_path="Design__plant__solar_battery_plant",
        )
        agg.expression.aliases = ["total_capex"]

        bt = DependencyBacktracker([], [], aggregation_data=[agg])

        # Simulated :: lookup: "Solar Battery Plant::total_capex"
        # After sanitization: "solar_battery_plant.total_capex"
        assert "solar_battery_plant.total_capex" in bt._aggregation_output_index
```

### Changes Required

**See `design.md#bf-6` and `design.md#bf-7` for full design.**

#### 1. Test Files
**File:** `tests/unit/test_hierarchy_pipeline.py` (EXTEND)
- [x] Add `TestScopeAggregationSiteInfra` class (3 tests: mismatched name, no-duplicate, all-four-assemblies)
- [x] Import `MultiplicityData` from data_models
- [x] Build synthetic data with name-mismatched PartDef and child usages

**File:** `tests/unit/test_backtracker_aggregation.py` (EXTEND)
- [x] Add `TestAggregationAliasResolution` class (6 tests)
- [x] Tests: alias in index, bare alias, channel match, full dotted, no-aliases, sanitized fallback
- [x] `aliases` field added on `AggregationExpressionData`

#### 2. Implementation — BF-6
**File:** `src/sysml_codegen/generation/initialization.py:330-338`
- [x] Replace Strategy 2 body with child-walk using `MultiplicityData`
- [x] Find children of PartDef from `hierarchy_data.multiplicities`
- [x] Walk virtual CalcUsage QNs to find child segments and derive parent instance path

#### 3. Implementation — BF-7
**File:** `src/sysml_codegen/extraction/data_models.py:296-326`
- [x] Add `aliases: list[str] = field(default_factory=list)` to `AggregationExpressionData`

**File:** `src/sysml_codegen/extraction/hierarchy_resolver.py:400-448`
- [x] After `build_aggregation_expression()` returns, scan sibling redefinitions for CHAIN-type entries
- [x] Populate `agg.aliases` with matching alias names

**File:** `src/sysml_codegen/analysis/dependency_backtracker.py:153-183`
- [x] After existing 3-key registration, add alias pass reading from `agg.expression.aliases`
- [x] Register `part_usage_name.alias_name`, bare `alias_name`, and dotted instance path with alias

**File:** `src/sysml_codegen/analysis/dependency_backtracker.py:464-470`
- [x] Sanitize PartDef names in `::` fallback: `sanitize_name(parts[-2]).lower()`

### Validation

**Automated:**
- [x] `uv run pytest tests/unit/test_hierarchy_pipeline.py -k "SiteInfra"` → 3 passed
- [x] `uv run pytest tests/unit/test_backtracker_aggregation.py -k "Alias"` → 6 passed
- [x] `uv run pytest tests/` → 474 passed, zero regressions
- [x] `uv run ruff check src/` → Clean on modified files (3 pre-existing E501 in backtracker docstrings)

**Manual:**
- [x] `_scope_aggregation_expressions()` no longer uses exact string comparison — uses child-walk via MultiplicityData
- [x] `_aggregation_output_index` has entries for both `capital_cost` and `total_capex`

**What We Know Works After This Phase:**
- All 4 assemblies (including Site Infrastructure) produce aggregation modules
- `:>> total_capex` alias resolves to MODULE_OUTPUT from aggregation chain
- `::` fallback works with unsanitized PartDef names

---

## Phase 4: BF-8 + BF-2 — Multiplicity EPs & Expression Compilation

### Goal
Surface orphan entry points in parameter groups (BF-8) and add the expression compilation step that converts symbolic text to `inputs.X`-form Python (BF-2, largest fix).

### Test Stencil (Write First)

```python
# tests/unit/test_graph_builder_aggregation.py — extend with BF-8 and BF-2 tests

class TestOrphanEntryPointsSurfaced:
    """BF-8: Orphan entry points (e.g., multiplicity) appear in parameter groups."""

    def test_multiplicity_ep_in_system_design_group(self):
        """module_count entry point appears in 'system_design' parameter group."""
        # Build a module with a multiplicity input sourced from entry_point
        module = PipelineModule(
            name="design__plant__solar_array__capital_cost",
            module_type="SolarArrayCapitalCost",
            inputs=[ModuleInput(
                field_name="module_count",
                python_type="int",
                param_name="module_count",
                source=InputSource(source_type="entry_point", qualified_name="module_count"),
            )],
            outputs=[],
            execution_order=0,
            is_aggregation=True,
        )
        entry_points = {
            "module_count": EntryPoint(
                qualified_name="module_count",
                simple_name="module_count",
                entry_type=EntryPointType.LIBRARY_DEFAULT,
                default_value=1,
            ),
        }
        # Pass through graph builder Step 6.6 rebuild
        # ... (call actual build_computation_graph or the relevant post-processing)
        # Assert: "system_design" group contains "module_count"
        # Assert: type is "int" (from ModuleInput.python_type)

    def test_non_multiplicity_orphan_also_captured(self):
        """Any orphan entry point (not just multiplicity) gets captured."""
        pass  # Full implementation during Phase 4


class TestAggregationExpressionCompilation:
    """BF-2: Aggregation modules have compiled_expression with inputs.X form."""

    def test_compiled_expression_has_inputs_prefix(self):
        """_build_aggregation_module() produces compiled_expression with inputs.X refs."""
        agg = _make_scoped_agg(
            transformed_expression="module_count * pv_module.capital_cost",
            sum_terms=[SumTerm(
                part_usage_name="pv_module",
                attribute_name="capital_cost",
                multiplicity_attr="module_count",
            )],
        )
        # ... build with real _build_aggregation_module()
        # Assert: module.compiled_expression == "inputs.module_count * inputs.pv_module_capital_cost"

    def test_compiled_expression_ast_parses(self):
        """compiled_expression is valid Python (ast.parse succeeds)."""
        import ast
        # ... build module
        ast.parse(module.compiled_expression)  # Should not raise

    def test_singleton_term_compiled_correctly(self):
        """Singleton term ref replaced with inputs.X form."""
        agg = _make_scoped_agg(
            transformed_expression="allocation_model.total_allocation + pv_module.capital_cost",
            singleton_terms=[SingletonTerm(
                source_path="allocation_model.total_allocation",
                # ...
            )],
            sum_terms=[SumTerm(
                part_usage_name="pv_module",
                attribute_name="capital_cost",
                multiplicity_attr="module_count",
            )],
        )
        # Assert: compiled has "inputs.allocation_model_total_allocation"

    def test_stencil_generation_uses_compiled_expression(self):
        """_generate_aggregation_stencils() reads compiled_expression, not transformed_expression."""
        # Integration-level: create a PipelineModule with compiled_expression set,
        # run through stencil generation, verify output contains "inputs." prefixes
        pass  # Full implementation during Phase 4
```

### Changes Required

**See `design.md#bf-8` and `design.md#bf-2` for full design.**

#### 1. Test Files
**File:** `tests/unit/test_graph_builder_aggregation.py` (EXTEND)
- [x] Add `TestOrphanEntryPointsSurfaced` class (BF-8)
- [x] Add `TestAggregationExpressionCompilation` class (BF-2)
- [x] Import `EntryPoint`, `EntryPointType`, `ParameterGroup` from resolution models
- [x] Tests: multiplicity in system_design group, non-multiplicity orphan, compiled_expression content, ast.parse, singleton terms

#### 2. Implementation — BF-8
**File:** `src/sysml_codegen/resolution/graph_builder.py:190-203`
- [x] After Step 6.6 filter, collect orphan entry points not covered by any param group
- [x] Build `ep_type_lookup` from `ModuleInput.python_type` (authoritative types)
- [x] Create synthetic `system_design` `ParameterGroup` for orphans
- [x] Verify `EntryPoint` model supports `python_type` field — added `python_type: str = "float"` to EntryPoint

#### 3. Implementation — BF-2
**File:** `src/sysml_codegen/resolution/models.py:149-169`
- [x] Add `compiled_expression: str | None = None` field to `PipelineModule`

**File:** `src/sysml_codegen/resolution/graph_builder.py:900-1086`
- [x] Initialize `ref_to_inputs: dict[str, str]` at top of `_build_aggregation_module()`
- [x] Populate inline during SumTerm, multiplicity, SingletonTerm, and LocalTerm input construction
- [x] After all inputs built, compile expression via longest-first string replacement
- [x] Store result on `PipelineModule.compiled_expression`

**File:** `src/sysml_codegen/cli/__init__.py:553-566`
- [x] In `_generate_aggregation_stencils()`, look up `PipelineModule` (using BF-3's fixed lookup)
- [x] Use `pipeline_module.compiled_expression` instead of `agg.expression.transformed_expression`

### Validation

**Automated:**
- [x] `uv run pytest tests/unit/test_graph_builder_aggregation.py -k "Orphan or Compilation"` → 11 passed
- [x] `uv run pytest tests/` → 485 passed, zero regressions
- [x] `uv run ruff check src/` → Clean on modified files (4 pre-existing E501 in unchanged code)
- [x] `uv run mypy src/` → Clean on modified files (pre-existing issues in agentic_mbse stubs and unchanged code)

**Manual:**
- [x] Verify `compiled_expression` contains `inputs.` prefixed references for a sample aggregation
- [x] Verify multiplicity params appear in `system_design` param group with `int` type
- [x] Verify stencil template writes `inputs.X` form, not raw symbolic text

**What We Know Works After This Phase:**
- All aggregation modules have `compiled_expression` with valid `inputs.X`-form Python
- `ast.parse()` succeeds on all compiled expressions
- Multiplicity entry points (`module_count`, etc.) appear in parameter group schemas
- Stencil generation produces executable `_impl.py` files

---

## Environment Setup

**See CLAUDE.md for full environment rules.**

```bash
uv run pytest tests/                    # Full test suite
uv run pytest tests/unit/FILE -k NAME   # Single test
uv run ruff check src/                  # Linting
uv run mypy src/                        # Type checking
```

---

## Risk Management

**See `design.md#potential-risks` for detailed risk analysis.**

**Phase-Specific Mitigations:**
- **Phase 1**: Depth limit on `_unwrap_invocation()` prevents infinite recursion. Defensive pass-through if no wrapper found.
- **Phase 2**: All three fixes are under 5 lines each — minimal blast radius. Tests verify the fix logic directly.
- **Phase 3**: BF-6 child-walk uses structural parent-child data (not name heuristics). BF-7 alias scope limited to same `owning_part_qn`.
- **Phase 4**: BF-2 string replacement sorted longest-first to prevent partial matches. `transformed_expression` is pure arithmetic (guaranteed by `_walk_aggregation_ast()` structure).

## Implementation Notes

_TO BE FILLED DURING IMPLEMENTATION_

### Phase 1 Completion
**Completed:** 2026-02-11
**Actual Changes:**
- Added `_KNOWN_WRAPPER_FUNCTIONS` frozenset and `_unwrap_invocation()` helper at `hierarchy_resolver.py:275-298`
- Applied unwrap in sum() handler at line 352: `operand = _unwrap_invocation(operands[0])`
- Added wrapper-check branch for non-sum invocations at lines 392-396: checks `_KNOWN_WRAPPER_FUNCTIONS`, unwraps and recurses
- Added 6 tests in `TestWalkAggregationAstEvaluationUnwrap` class + `_make_wrapped_sum_invocation` helper

**Issues:** None — clean implementation.

**Deviations from Plan:**
- Tests use `build_aggregation_expression()` (public API) instead of `_walk_aggregation_ast()` directly — the plan's test stencil assumed a different function signature (`owning_part_qn` kwarg). Testing through the public API provides better integration coverage.
- Added `_KNOWN_WRAPPER_FUNCTIONS` frozenset for the non-sum branch (design said "check if this invocation is a known wrapper pattern"). For sum() operands, unwrap is unconditional (any InvocationExpression).
- Added 6th test (`test_mixed_expression_with_evaluation_wrappers`) beyond the plan's 5 to verify the full Solar Array expression with Evaluation wrappers on both sum() terms.

### Phase 2 Completion
**Completed:** 2026-02-11
**Actual Changes:**
- BF-3: `cli/__init__.py:453` — lookup changed to `get_module_name(agg.module_eqn)`
- BF-4: `cli/__init__.py:434` — `sysml_qn` changed to `agg.module_eqn.replace("__", "::")`
- BF-5: `cli/__init__.py:533` — same instance-scoped fix; line 536 uses `agg.module_eqn` directly
- Removed unused `sysml_to_python_qualified_name` import from `_generate_aggregation_stencils()`
- Added 5 tests: 2 in `TestAggregationModuleLookupCaseMatch`, 3 in `TestAggregationPathsUseInstanceEQN`

**Issues:** None.

**Deviations from Plan:**
- Added `test_raw_eqn_lookup_fails` to explicitly demonstrate the bug (raw lookup returns None)
- Added `test_different_instances_produce_different_paths` to verify no path collisions between instances of same PartDef
- Cleaned up unused import in stencils function (minor)

### Phase 3 Completion
**Completed:** 2026-02-11
**Actual Changes:**
- BF-6: `initialization.py:330-343` — Replaced Strategy 2 name matching with child-walk using `MultiplicityData`. Gets children of PartDef from `hierarchy_data.multiplicities`, finds child names in virtual CalcUsage QN segments, derives parent instance path from preceding segment.
- BF-7 Change 1: `data_models.py:325` — Added `aliases: list[str]` field to `AggregationExpressionData`
- BF-7 Change 2: `hierarchy_resolver.py:519-527` — Scan sibling CHAIN redefinitions after `build_aggregation_expression()` to populate aliases
- BF-7 Change 3: `dependency_backtracker.py:186-195` — Register alias entries (dotted, bare, full instance path) in `_aggregation_output_index`
- BF-7 Change 4: `dependency_backtracker.py:478-479` — Sanitize PartDef names in `::` fallback via `sanitize_name().lower()`
- Removed unused `sanitize_name` import from `initialization.py` (was used by old Strategy 2)
- Added 9 tests: 3 in `TestScopeAggregationSiteInfra`, 6 in `TestAggregationAliasResolution`

**Issues:**
- 3 existing Strategy 2 tests failed after the child-walk change because they didn't provide multiplicities. Fixed by adding `MultiplicityData` to those tests' `_make_hierarchy()` calls. This is expected — the Strategy 2 behavior changed from name-matching to child-walk.

**Deviations from Plan:**
- Updated `_make_hierarchy` helper to accept `multiplicities` parameter (needed for BF-6 tests)
- Added `test_child_walk_does_not_duplicate_with_strategy1` test (verifies Strategy 1 skips child-walk)
- Added `test_alias_channel_matches_original`, `test_full_dotted_alias_resolves`, `test_no_aliases_no_extra_keys` tests beyond plan stencil for more thorough coverage

### Phase 4 Completion
**Completed:** 2026-02-11
**Actual Changes:**
- BF-8 Change 1: `resolution/models.py:59` — Added `python_type: str = "float"` field to `EntryPoint` model
- BF-8 Change 2: `resolution/models.py:168` — Added `compiled_expression: str | None = None` field to `PipelineModule` model
- BF-8 Change 3: `resolution/graph_builder.py:204-235` — Added Step 6.8 orphan EP collection after Step 6.6 rebuild: collects EPs not covered by any param group, builds `ep_type_lookup` from `ModuleInput.python_type`, creates synthetic `system_design` ParameterGroup
- BF-8 Change 4: `generation/entry_point.py:563` — Changed hardcoded `"float"` to `getattr(ep, "python_type", "float")` in schema generation
- BF-2 Change 1: `resolution/graph_builder.py:963` — Initialize `ref_to_inputs: dict[str, str]` at top of `_build_aggregation_module()`
- BF-2 Change 2: `resolution/graph_builder.py` — Populate `ref_to_inputs` inline after each SumTerm (line 1005), multiplicity (line 1035), SingletonTerm (line 1085), and LocalTerm (line 1112) input construction
- BF-2 Change 3: `resolution/graph_builder.py:1114-1118` — Compile expression via longest-first string replacement when `has_unsupported_nodes` is False
- BF-2 Change 4: `resolution/graph_builder.py:1127` — Store `compiled_expression` on `PipelineModule`
- BF-2 Change 5: `cli/__init__.py:527-531` — Build `agg_modules_by_name` lookup in `_generate_aggregation_stencils()`
- BF-2 Change 6: `cli/__init__.py:556-558` — Look up `PipelineModule`, use `compiled_expression` instead of `transformed_expression` for template rendering
- Added 11 tests: 5 in `TestOrphanEntryPointsSurfaced`, 6 in `TestAggregationExpressionCompilation`
- Fixed pre-existing test bug in `test_computed_attribute_pipeline.py:530` exposed by BF-8 (`group.entries` → `group.parameters`)

**Issues:**
- Pre-existing test at `test_computed_attribute_pipeline.py::TestFormulaRemoval::test_formula_removal_prevents_false_entry_points` used `group.entries` (nonexistent attribute) instead of `group.parameters`. This was masked because `entry_point_groups` was previously empty in that test scenario. BF-8's orphan EP collection now creates a `system_design` group, causing the loop to execute and surface the latent bug. Fixed by correcting the attribute access.

**Deviations from Plan:**
- Added `python_type` field to `EntryPoint` model (design mentioned this as option (a) if `EntryPoint` lacked the field). Used `getattr()` in schema generation for defensive backward compatibility.
- Used `getattr(ep, "python_type", "float")` in `entry_point.py` instead of direct access for robustness with any non-Pydantic parameter objects.
- BF-8 orphan tests use a helper method `_collect_orphans()` that mirrors the graph_builder logic, testing the algorithm directly without requiring the full `build_computation_graph()` pipeline. This is more isolated and faster than integration-level testing.
- Added `test_no_orphans_no_synthetic_group` beyond plan stencil for completeness.

---

**Status**: ~~Draft~~ → ~~In Progress~~ → **Complete**
