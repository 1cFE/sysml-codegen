# Non-Mocked Test Strategy for Hierarchy Pipeline

**Date**: 2026-02-12
**Author**: Claude (Opus 4.6)
**Status**: Draft

## Problem Statement

All existing unit tests for the hierarchy pipeline (hierarchy_resolver, graph_builder_aggregation, backtracker_aggregation) use mock AST elements that don't accurately represent the real SysIDE AST structure. This caused 4 E2E failures where the code works correctly against mocks but fails against real data.

### The Mock Problem

Current mocks construct AST nodes like:
```python
class MockInvocationExpression:
    def __init__(self, func_name, operands):
        self.function = type("Function", (), {"name": func_name})()
        self.operands = operands

# Test constructs: sum(FeatureChainExpression("pv_module.capital_cost"))
mock_sum = MockInvocationExpression("sum", [MockFeatureChainExpression(["pv_module", "capital_cost"])])
```

But SysIDE produces:
```
InvocationExpression [func='sum']
  └─ InvocationExpression [func='Evaluation']     ← NOT in our mocks!
       └─ FeatureChainExpression [pv_module.capital_cost]
```

The `Evaluation()` wrapper is an internal SysML collect/select semantic that our mocks completely omit.

---

## Strategy: Three-Tier Testing

### Tier 1: AST Assumption Tests (NEW - highest priority)

**Purpose**: Validate our assumptions about the SysIDE AST structure by loading real models and asserting specific AST properties.

**Fixture**: `tests/fixtures/solar_battery_model/` (already exists)

**Test file**: `tests/integration/test_ast_assumptions.py`

These tests load the real model once per class via `build_pipeline_context()` and then probe the intermediate data structures. They are NOT end-to-end tests — they validate specific assumptions at the extraction layer.

#### Test Class 1: `TestSumExpressionAST`
Tests that validate what `sum()` looks like in the real AST.

| Test | Assertion | Why |
|------|-----------|-----|
| `test_sum_is_invocation_expression` | `sum()` nodes have `function.name == 'sum'` | Basic sanity |
| `test_sum_operand_is_wrapped` | `sum()` operand may be another `InvocationExpression`, not directly `FeatureChainExpression` | THE critical assumption that failed |
| `test_unwrap_reveals_feature_chain` | After unwrapping, the inner node is `FeatureChainExpression` | Validates `_unwrap_invocation()` |
| `test_feature_chain_has_parts` | The unwrapped chain produces `"part_name.attr_name"` format | Validates `extract_feature_chain_name()` |
| `test_no_evaluation_in_chain_name` | `extract_feature_chain_name()` never returns "Evaluation" | Regression guard |

**Implementation pattern**:
```python
class TestSumExpressionAST:
    @pytest.fixture(scope="class")
    def model_and_adapter(self):
        extractor = SysMLDataExtractor([FIXTURES_DIR / "solar_battery_model"])
        extractor.load_models()
        return extractor.model, extractor.adapter

    def test_sum_operand_structure(self, model_and_adapter):
        model, adapter = model_and_adapter
        # Find a PartDef with aggregation (Solar Array has sum())
        solar_array = _find_part_def(model, adapter, "Solar Array")
        # Find :>> capital_cost (ReferenceUsage with EXPRESSION type)
        capital_cost_redef = _find_redef(solar_array, "capital_cost")
        expr = capital_cost_redef.feature_value_expression
        # Walk the expression tree to find sum() nodes
        sum_nodes = _find_invocations(expr, "sum")
        assert len(sum_nodes) > 0
        for sum_node in sum_nodes:
            operand = sum_node.operands[0]
            # THIS is the critical assertion: is operand wrapped?
            if hasattr(operand, 'function'):
                # Wrapped in Evaluation - unwrap
                inner = _unwrap(operand)
                assert adapter.is_instance(inner, "FeatureChainExpression")
                chain_name = extract_feature_chain_name(inner)
                assert "Evaluation" not in chain_name
            else:
                # Direct FeatureChainExpression (mocks assumed this)
                assert adapter.is_instance(operand, "FeatureChainExpression")
```

#### Test Class 2: `TestRedefinitionStructure`
Tests that validate :>> redefinition AST patterns.

| Test | Assertion | Why |
|------|-----------|-----|
| `test_redef_is_reference_usage` | `:>>` members are `ReferenceUsage` not `AttributeUsage` | Spike Q2 finding |
| `test_redef_has_owned_redefinitions` | `owned_redefinitions` is non-empty | Distinguishes :>> from new attributes |
| `test_literal_redef_has_value` | `:>> wattage = 400.0` has `feature_value_expression.value == 400.0` | Literal extraction |
| `test_chain_redef_has_feature_chain` | `:>> capital_cost = cost_model.total_cost` produces `FeatureChainExpression` | Chain extraction |
| `test_expression_redef_has_operator` | `:>> capital_cost = sum(...) + ...` produces `OperatorExpression` | Aggregation detection |
| `test_deep_path_chaining_features` | `:>> pv_module.wattage = 400.0` has `chaining_features == [pv_module, wattage]` | Deep-path resolution |

#### Test Class 3: `TestAliasDetection`
Tests that validate the alias discovery logic.

| Test | Assertion | Why |
|------|-----------|-----|
| `test_chain_redef_creates_alias` | When PartDef has both `:>> capital_cost = sum(...)` AND `:>> total_capex = capital_cost`, the CHAIN redef is found as sibling | Alias population |
| `test_alias_source_path_ends_with_attribute` | The CHAIN redef's `source_path` ends with the EXPRESSION redef's `attribute_name` | Matching logic |
| `test_aliases_populated_in_aggregation_data` | `AggregationExpressionData.aliases` contains the alias name | E2E alias flow |

#### Test Class 4: `TestMultiplicityAST`
Tests that validate multiplicity representation.

| Test | Assertion | Why |
|------|-----------|-----|
| `test_arrayed_part_has_multiplicity` | `pv_module` PartUsage has non-None `multiplicity` | Multiplicity detection |
| `test_cached_lower_bound_correct` | `cached_lower_bound` matches expected count (e.g., 20) | Spike Q5 |
| `test_cached_upper_bound_is_n_plus_1` | `cached_upper_bound` is N+1 (exclusive convention) | Guard against using wrong bound |
| `test_count_attribute_name_extracted` | `upper_bound.referent.name` gives attribute name (e.g., "module_count") | Multiplicity attr name |

### Tier 2: Algorithm Integration Tests (ENHANCE existing)

**Purpose**: Test algorithms with real AST data flowing through, not just mocks.

**Test file**: `tests/integration/test_hierarchy_algorithms.py`

These tests run specific algorithms (hierarchy_resolver functions) against the real model and verify the output data structures.

| Test | Tests What | Validates |
|------|-----------|-----------|
| `test_extract_redefinitions_solar_array` | `extract_redefinitions()` on Solar Array PartDef | Correct redef count, types, values |
| `test_extract_multiplicities_solar_array` | `extract_multiplicities()` on Solar Array PartDef | pv_module count=20, inverter count=4 |
| `test_build_aggregation_solar_array_capital_cost` | `build_aggregation_expression()` for capital_cost | sum_terms populated, no Evaluation, correct part names |
| `test_extract_hierarchy_data_completeness` | `extract_hierarchy_data()` on full model | All PartDefs scanned, all aggregations found |
| `test_walk_aggregation_ast_real_expression` | `_walk_aggregation_ast()` on real capital_cost expr | Correct sum_terms, singleton_terms, local_terms classification |
| `test_unwrap_invocation_real_sum` | `_unwrap_invocation()` on real sum() operand | Returns FeatureChainExpression |
| `test_scope_aggregation_all_assemblies` | `_scope_aggregation_expressions()` finds all 4 assemblies | Including site_infra (BF-6 regression test) |

**Implementation pattern**:
```python
class TestHierarchyAlgorithms:
    @pytest.fixture(scope="class")
    def hierarchy_data(self):
        extractor = SysMLDataExtractor([FIXTURES_DIR / "solar_battery_model"])
        extractor.load_models()
        return extract_hierarchy_data(extractor.model)

    def test_solar_array_sum_terms(self, hierarchy_data):
        solar_array_aggs = [
            a for a in hierarchy_data.aggregation_expressions
            if "Solar_Array" in a.owning_part_qn and a.attribute_name == "capital_cost"
        ]
        assert len(solar_array_aggs) == 1
        agg = solar_array_aggs[0]

        # Critical: sum_terms should have real part names, not Evaluation artifacts
        assert len(agg.sum_terms) >= 2  # pv_module and inverter at minimum
        sum_part_names = {t.part_usage_name for t in agg.sum_terms}
        assert "pv_module" in sum_part_names
        assert "inverter" in sum_part_names

        # No Evaluation artifacts
        assert not agg.has_unsupported_nodes
        assert "Evaluation" not in agg.transformed_expression

    def test_alias_populated(self, hierarchy_data):
        plant_aggs = [
            a for a in hierarchy_data.aggregation_expressions
            if "Solar_Battery_Plant" in a.owning_part_qn and a.attribute_name == "capital_cost"
        ]
        assert len(plant_aggs) == 1
        assert "total_capex" in plant_aggs[0].aliases
```

### Tier 3: Pipeline Wiring Tests (ENHANCE existing E2E)

**Purpose**: Test the full pipeline context creation and verify wiring correctness.

**Test file**: `tests/integration/test_hierarchy_wiring.py`

| Test | Tests What | Validates |
|------|-----------|-----------|
| `test_aggregation_modules_created` | Aggregation modules exist in computation graph | Module count and names |
| `test_aggregation_modules_have_inputs` | Each aggregation module has non-empty inputs | No empty Input classes |
| `test_aggregation_inputs_are_module_output` | SumTerm inputs wire to module_output, not entry_point | Correct source_type |
| `test_total_capex_wires_to_aggregation` | annualized_financial.total_capex → module_output | BF-7 regression |
| `test_multiplicity_entry_points_exist` | module_count, inverter_count in entry_points | Entry point creation |
| `test_site_infra_scoped` | Site Infrastructure gets scoped aggregation modules | BF-6 regression |
| `test_no_evaluation_in_yaml` | Pipeline YAML has no Evaluation artifacts | BF-1 regression |
| `test_aggregation_compiled_expressions` | compiled_expression uses inputs.X form | Expression compilation |

---

## What Makes These Tests "Non-Mocked"

1. **Real SysIDE AST**: All tests load `solar_battery_model` via `SysMLDataExtractor`, producing real syside AST nodes
2. **Real algorithm execution**: Tests call the actual extraction/resolution/generation functions, not mocked versions
3. **Structural assertions**: Tests assert properties of intermediate data structures (SumTerm, AggregationExpressionData, ModuleInput) that were produced from real AST
4. **No type mocking**: No `MockFeatureChainExpression` or `MockInvocationExpression` — the code processes actual syside objects

## Fixture Design

### Shared fixture: `solar_battery_context`

```python
@pytest.fixture(scope="module")
def solar_battery_context():
    """Load solar_battery model and build full pipeline context.

    Scope=module to avoid repeated model loading (expensive).
    """
    model_path = Path(__file__).parent.parent / "fixtures" / "solar_battery_model"
    return build_pipeline_context([model_path])
```

### Shared fixture: `solar_battery_hierarchy`

```python
@pytest.fixture(scope="module")
def solar_battery_hierarchy():
    """Load solar_battery model and extract hierarchy data only.

    Lighter than full pipeline context — for Tier 1 and Tier 2 tests.
    """
    model_path = Path(__file__).parent.parent / "fixtures" / "solar_battery_model"
    extractor = SysMLDataExtractor([model_path])
    extractor.load_models()
    return extract_hierarchy_data(extractor.model), extractor.model, extractor.adapter
```

### Shared fixture: `solar_battery_raw_elements`

```python
@pytest.fixture(scope="module")
def solar_battery_raw_elements():
    """Load solar_battery model and provide raw model + adapter for AST probing.

    For Tier 1 tests that need to inspect raw AST nodes.
    """
    model_path = Path(__file__).parent.parent / "fixtures" / "solar_battery_model"
    extractor = SysMLDataExtractor([model_path])
    extractor.load_models()
    return extractor.model, extractor.adapter
```

---

## Implementation Priority

### Phase 1: Tier 1 AST Assumption Tests (HIGHEST PRIORITY)
These tests validate our understanding of the AST. If they fail, it means our mental model is wrong and the algorithms need fundamental redesign.

**Estimated**: 4-6 tests, ~150 lines
**File**: `tests/integration/test_ast_assumptions.py`

### Phase 2: Tier 2 Algorithm Integration Tests
These tests validate that our algorithms produce correct output from real input. They will catch all 4 current failures.

**Estimated**: 7-10 tests, ~250 lines
**File**: `tests/integration/test_hierarchy_algorithms.py`

### Phase 3: Tier 3 Pipeline Wiring Tests
These tests validate the full pipeline end-to-end. They're the most comprehensive but also the slowest.

**Estimated**: 8-10 tests, ~300 lines
**File**: `tests/integration/test_hierarchy_wiring.py`

---

## Relationship to Existing Tests

| Existing File | Nature | What It Misses |
|--------------|--------|----------------|
| `test_hierarchy_resolver.py` (42 tests) | Mock-based unit | Real AST node types and nesting |
| `test_graph_builder_aggregation.py` | Mock-based unit | Real channel names and resolution |
| `test_backtracker_aggregation.py` | Mock-based unit | Real binding source_path formats |
| `test_hierarchy_pipeline.py` | Mock-based unit | Real pipeline step interactions |
| `test_hierarchy_e2e.py` (10 tests) | Real E2E (current) | 4 of 10 failing |

The new tests fill the gap between mock-based unit tests (fast but unrealistic) and the E2E tests (realistic but coarse-grained). The new Tier 1-2 tests are the "missing middle" — they use real data but test specific algorithm functions, making failures easy to diagnose.

---

## Test Data Ground Truth

For the solar_battery model, these are the expected values that tests should validate:

### Aggregation Expressions
| Assembly | Attribute | Expected Sum Terms | Expected Singletons | Expected Local |
|----------|-----------|-------------------|--------------------|----|
| Solar Array | capital_cost | pv_module, inverter | array_bos | misc_hardware_cost |
| Battery System | capital_cost | battery_pack | hybrid_inverter, battery_bos | — |
| Site Infrastructure | capital_cost | — (all singletons) | racking, electrical_panel, permitting | — |
| Solar Battery Plant | capital_cost | solar_array, battery_system, site_infra | — | — |

### Multiplicities
| Assembly | Child Part | Count | Count Attribute |
|----------|-----------|-------|----------------|
| Solar Array | pv_module | 20 | module_count |
| Solar Array | inverter | 4 | inverter_count |
| Battery System | battery_pack | 8 | pack_count |

### Aliases
| Assembly | Attribute | Alias |
|----------|-----------|-------|
| Solar Battery Plant | capital_cost | total_capex |

### Wiring
| CalcUsage | Input | Expected Source |
|-----------|-------|----------------|
| annualized_financial | total_capex | module_output (from plant capital_cost aggregation) |
| annualized_om | p_net_kw | module_output (from p_net_kw computed attribute) |
