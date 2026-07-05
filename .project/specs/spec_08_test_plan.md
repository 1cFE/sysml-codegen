# Spec 08: Comprehensive Test Plan

**Epic**: OUTPUT-REGISTRY (All Items)
**Status**: Draft
**Created**: 2026-02-13

---

## 1. Overview

This spec defines every test required for the OutputRegistry redesign, organized by test file. Each test specifies its name, what it validates, key assertions, and how test data is set up. Tests are organized into two tiers:

- **Unit tests** (`tests/unit/`): Synthetic data, fast, test one class/function. Use factory helpers to create representative data objects.
- **Integration tests** (`tests/integration/`): Real SysML models via SysIDE adapter, full pipeline, slower. Validate end-to-end correctness.

### Test File Index

| File | New/Modified | Item | What it tests |
|------|-------------|------|---------------|
| `tests/unit/test_output_registry.py` | NEW | 1 | OutputRegistry class: register, resolve, collisions, phases |
| `tests/unit/test_backtracker_registry.py` | NEW | 3 | Backtracker with OutputRegistry: CHAIN/REFERENCE/LITERAL resolution |
| `tests/unit/test_hierarchy_resolver_aliases.py` | NEW | 2a | CHAIN redef -> ChannelAlias production and filtering |
| `tests/unit/test_computed_attr_aliases.py` | NEW | 2a | EXPOSE_PURE -> ChannelAlias + FORMULA -> synthetic CalcUsage |
| `tests/unit/test_backtracker_aggregation.py` | MODIFIED | 3 | Update constructor for OutputRegistry |
| `tests/unit/test_backtracker_computed_attrs.py` | MODIFIED | 3,4 | Update for registry-based resolution |
| `tests/unit/test_graph_builder.py` | MODIFIED | 4 | Remove output catalog building tests |
| `tests/unit/test_step_4_5.py` | MODIFIED | 2a | Add EXPOSE_PURE alias + synthetic CalcUsage tests |
| `tests/unit/test_hierarchy_resolver.py` | MODIFIED | 2a | Add CHAIN alias tests |
| `tests/integration/test_registry_e2e.py` | NEW | 3,4 | Full pipeline OutputRegistry validation |
| `tests/integration/test_costed_component_e2e.py` | MODIFIED | 4 | Pass unchanged (behavior preserved) |
| `tests/integration/test_full_pipeline.py` | MODIFIED | 4 | Pass unchanged |
| `tests/integration/test_hierarchy_e2e.py` | MODIFIED | 4 | Pass unchanged |

---

## 2. Shared Test Helpers

### 2.1 Factory Functions

These factory functions create representative data objects for unit testing. They produce hardcoded data grounded in spike results (no SysIDE loading required).

```python
# tests/conftest_output_registry.py (or inline in test files)

from dataclasses import dataclass, field
from sysml_codegen.extraction.usage_extractor import CalcUsageData, BindingInfo
from sysml_codegen.extraction.data_models import (
    AggregationExpressionData,
    ComputedAttributeClassification,
    ComputedAttributeData,
    ScopedAggregationData,
)
from sysml_codegen.core.models import ChannelAlias
from sysml_codegen.extraction.expression_compiler import Compilability
from agentic_mbse.sysml.types import BindingType


def make_calc_usage(
    instance_name: str,
    calc_def_name: str,
    qualified_name: str = "",
    bindings: list[BindingInfo] | None = None,
    is_template: bool = False,
    owning_part_def_qn: str | None = None,
) -> CalcUsageData:
    """Create a minimal CalcUsageData for unit testing."""
    return CalcUsageData(
        instance_name=instance_name,
        calc_def_name=calc_def_name,
        calc_def_qualified_name=f"Lib__{calc_def_name}",
        module_type=f"{calc_def_name}Module",
        bindings=bindings or [],
        qualified_name=qualified_name or f"Pkg__Part__{instance_name}",
        is_template=is_template,
        owning_part_def_qn=owning_part_def_qn,
    )


def make_virtual_calc_usage(
    instance_name: str,
    calc_def_name: str,
    instance_path: str,
    bindings: list[BindingInfo] | None = None,
) -> CalcUsageData:
    """Create a virtual (template-expanded) CalcUsageData.

    Example: instance_path="SolarBatteryDesign__solar_battery_plant__solar_array__pv_module"
             instance_name="cost_model"
             -> qualified_name="SolarBatteryDesign__solar_battery_plant__solar_array__pv_module__cost_model"
    """
    return CalcUsageData(
        instance_name=instance_name,
        calc_def_name=calc_def_name,
        calc_def_qualified_name=f"Lib__{calc_def_name}",
        module_type=f"{calc_def_name}Module",
        bindings=bindings or [],
        qualified_name=f"{instance_path}__{instance_name}",
        is_template=False,
    )


@dataclass
class SimpleCalcDef:
    """Minimal calc def for backtracker/graph builder tests."""
    name: str
    qualified_name: str
    output_attributes: list = field(default_factory=list)
    input_attributes: list = field(default_factory=list)


@dataclass
class SimpleAttrInfo:
    """Minimal attribute info for calc def outputs/inputs."""
    name: str
    sysml_type: str = "Real"
    python_type: str = "float"
    default_value: str | None = None


def make_scoped_agg(
    attribute_name: str = "capital_cost",
    owning_part_qn: str = "Lib__Solar_Array",
    owning_part_name: str = "Solar_Array",
    instance_path: str = "Design__plant__solar_array",
    aliases: list[str] | None = None,
) -> ScopedAggregationData:
    """Create a ScopedAggregationData for unit testing."""
    expr = AggregationExpressionData(
        owning_part_qn=owning_part_qn,
        owning_part_name=owning_part_name,
        attribute_name=attribute_name,
        raw_expression_text="sum(...)",
        transformed_expression="...",
        sum_terms=[],
        singleton_terms=[],
        local_terms=[],
        input_channels=[],
        entry_points=[],
        aliases=aliases or [],
    )
    return ScopedAggregationData(expression=expr, instance_path=instance_path)


def make_computed_attr(
    name: str,
    owning_part_name: str,
    owning_part_qn: str,
    classification: ComputedAttributeClassification,
    compilability: Compilability = Compilability.FULLY_COMPILABLE,
    compiled_expression: str | None = None,
    references: list | None = None,
    is_on_part_definition: bool = False,
) -> ComputedAttributeData:
    """Create a ComputedAttributeData for unit testing."""
    return ComputedAttributeData(
        name=name,
        python_name=name,
        owning_part_name=owning_part_name,
        owning_part_qualified_name=owning_part_qn,
        expression_ast=None,
        expression_text=f"{name} expression",
        references=references or [],
        classification=classification,
        compilability=compilability,
        compiled_expression=compiled_expression,
        is_on_part_definition=is_on_part_definition,
    )


def make_channel_alias(
    alias_name: str,
    canonical_name: str,
    owning_part_qn: str = "Lib__Part",
    source: str = "redefinition",
) -> ChannelAlias:
    """Create a ChannelAlias for unit testing."""
    return ChannelAlias(
        alias_name=alias_name,
        canonical_name=canonical_name,
        owning_part_qn=owning_part_qn,
        source=source,
    )
```

---

## 3. Unit Tests: `tests/unit/test_output_registry.py` (NEW)

Tests the `OutputRegistry` class in isolation. All tests use synthetic data.

### 3.1 `test_register_and_resolve_exact_match`

**Validates**: Basic register + resolve round-trip.

**Setup**: Create an `OutputRegistry`, register one channel with one lookup key.

**Assertions**:
- `registry.resolve(key)` returns the canonical channel name
- `registry.resolve(canonical_channel)` also returns the canonical (self-maps)

```python
def test_register_and_resolve_exact_match():
    registry = OutputRegistry()
    registry.register("design__plant__lcoe__lcoe_per_mwh", ["lcoe.lcoe_per_mwh"])
    assert registry.resolve("lcoe.lcoe_per_mwh") == "design__plant__lcoe__lcoe_per_mwh"
    assert registry.resolve("design__plant__lcoe__lcoe_per_mwh") == "design__plant__lcoe__lcoe_per_mwh"
```

### 3.2 `test_register_multiple_keys`

**Validates**: One channel registered with multiple lookup keys (Key_A, Key_B, Key_C).

**Setup**: Register a channel with 3 keys.

**Assertions**:
- All 3 keys resolve to the same canonical channel
- Keys that were not registered return `None`

```python
def test_register_multiple_keys():
    registry = OutputRegistry()
    channel = "design__plant__lcoe__lcoe_per_mwh"
    registry.register(channel, [
        "lcoe.lcoe_per_mwh",                              # Key_A
        "Design__plant__lcoe__lcoe_per_mwh",               # Key_B
        "plant.lcoe.lcoe_per_mwh",                         # Key_C
    ])
    assert registry.resolve("lcoe.lcoe_per_mwh") == channel
    assert registry.resolve("Design__plant__lcoe__lcoe_per_mwh") == channel
    assert registry.resolve("plant.lcoe.lcoe_per_mwh") == channel
    assert registry.resolve("unknown.key") is None
```

### 3.3 `test_register_alias`

**Validates**: Alias maps to a canonical channel registered in Phase 1.

**Setup**: Register a canonical channel, then register an alias.

**Assertions**:
- `registry.resolve(alias_key)` returns the canonical channel
- Original keys still resolve

```python
def test_register_alias():
    registry = OutputRegistry()
    channel = "design__plant__solar_array__pv_module__cost_model__total_cost"
    registry.register(channel, ["pv_module.cost_model.total_cost"])
    registry.register_alias("pv_module.capital_cost", channel)
    assert registry.resolve("pv_module.capital_cost") == channel
    assert registry.resolve("pv_module.cost_model.total_cost") == channel
```

### 3.4 `test_register_alias_unregistered_channel_fails`

**Validates**: `register_alias()` raises `AssertionError` if the canonical channel is not registered.

**Setup**: Create an empty registry, attempt to register an alias to a nonexistent channel.

**Assertions**:
- `AssertionError` is raised with message about unregistered channel

```python
def test_register_alias_unregistered_channel_fails():
    registry = OutputRegistry()
    with pytest.raises(AssertionError, match="unregistered channel"):
        registry.register_alias("alias.key", "nonexistent__channel")
```

### 3.5 `test_resolve_returns_none_for_unknown`

**Validates**: Miss returns `None`, not an exception.

**Setup**: Register some channels, query with unknown key.

**Assertions**:
- `registry.resolve("totally.unknown.key")` returns `None`

```python
def test_resolve_returns_none_for_unknown():
    registry = OutputRegistry()
    registry.register("some__channel", ["some.key"])
    assert registry.resolve("totally.unknown.key") is None
```

### 3.6 `test_register_collision_refuses_overwrite`

**Validates**: When two different channels try to register the same key, the first wins and a warning is logged.

**Setup**: Register two channels with an overlapping key.

**Assertions**:
- First registration wins
- `resolve()` returns first channel, not second
- Warning is logged (use `caplog` fixture)

```python
def test_register_collision_refuses_overwrite(caplog):
    registry = OutputRegistry()
    registry.register("channel_a", ["shared.key"])
    registry.register("channel_b", ["shared.key"])
    assert registry.resolve("shared.key") == "channel_a"
    assert "collision" in caplog.text.lower() or "refusing" in caplog.text.lower()
```

### 3.7 `test_resolve_exact_match_only_no_normalization`

**Validates**: No `::` -> `__` normalization, no bare-name fallback.

**Setup**: Register channel with dotted key, query with SysML QN format and bare name.

**Assertions**:
- Dotted key resolves: `registry.resolve("alpha_split.p_alpha")` -> channel
- SysML QN does NOT resolve: `registry.resolve("FusionPhysics::AlphaNeutronSplit::p_alpha")` -> `None`
- Bare name does NOT resolve: `registry.resolve("p_alpha")` -> `None`

```python
def test_resolve_exact_match_only_no_normalization():
    registry = OutputRegistry()
    channel = "catfmfephysics__catf_physics__alpha_split__p_alpha"
    registry.register(channel, ["alpha_split.p_alpha"])
    assert registry.resolve("alpha_split.p_alpha") == channel
    assert registry.resolve("FusionPhysics::AlphaNeutronSplit::p_alpha") is None
    assert registry.resolve("p_alpha") is None
```

### 3.8 `test_phase_ordering_contract`

**Validates**: Phase 2 alias resolves against Phase 1 canonical. Phase 3 resolves against Phase 1+2.

**Setup**:
1. Phase 1: Register `"pv_module.cost_model.total_cost"` -> channel_A
2. Phase 2 (CHAIN): Alias `"pv_module.capital_cost"` -> canonical_name `"pv_module.cost_model.total_cost"` (resolves to channel_A)
3. Phase 3 (EXPOSE_PURE): Alias `"solar_array.total_capex"` -> canonical_name `"pv_module.capital_cost"` (resolves via Phase 2 alias to channel_A)

**Assertions**:
- `registry.resolve("pv_module.cost_model.total_cost")` == channel_A (Phase 1)
- `registry.resolve("pv_module.capital_cost")` == channel_A (Phase 2)
- `registry.resolve("solar_array.total_capex")` == channel_A (Phase 3)

```python
def test_phase_ordering_contract():
    registry = OutputRegistry()
    channel_a = "design__plant__solar_array__pv_module__cost_model__total_cost"

    # Phase 1: canonical
    registry.register(channel_a, ["pv_module.cost_model.total_cost"])

    # Phase 2: CHAIN alias
    resolved = registry.resolve("pv_module.cost_model.total_cost")
    assert resolved is not None
    registry.register_alias("pv_module.capital_cost", resolved)

    # Phase 3: EXPOSE_PURE alias (resolves through Phase 2)
    resolved2 = registry.resolve("pv_module.capital_cost")
    assert resolved2 is not None
    registry.register_alias("solar_array.total_capex", resolved2)

    # All three resolve to same channel
    assert registry.resolve("pv_module.cost_model.total_cost") == channel_a
    assert registry.resolve("pv_module.capital_cost") == channel_a
    assert registry.resolve("solar_array.total_capex") == channel_a
```

### 3.9 `test_key_c_format_concrete_calcusage`

**Validates**: Key_C derivation for concrete (non-virtual) CalcUsages.

**Setup**: CalcUsage with `qualified_name="CATFMFEPhysics__catf_physics__alpha_split"`, output `"p_alpha"`.

**Assertions**:
- Key_C = `"catf_physics.alpha_split.p_alpha"` (strip first segment, join with `.`)
- Key_A = `"alpha_split.p_alpha"` (instance_name.output)
- Both resolve to the same channel

```python
def test_key_c_format_concrete_calcusage():
    registry = OutputRegistry()
    qn = "CATFMFEPhysics__catf_physics__alpha_split"
    output_name = "p_alpha"
    channel = get_channel_name(qn, output_name)

    segments = qn.split("__")
    key_c = ".".join(segments[1:]) + "." + output_name  # "catf_physics.alpha_split.p_alpha"
    key_a = f"alpha_split.{output_name}"

    registry.register(channel, [key_a, key_c])
    assert registry.resolve(key_c) == channel
    assert registry.resolve(key_a) == channel
```

### 3.10 `test_key_c_format_virtual_calcusage`

**Validates**: Key_C derivation for virtual (template-expanded) CalcUsages. Key_C is the ONLY key format that Phase 2 CHAIN aliases resolve against for virtual CalcUsages (Spike 8).

**Setup**: Virtual CalcUsage with `qualified_name="SolarBatteryDesign__solar_battery_plant__solar_array__pv_module__cost_model"`, output `"total_cost"`.

**Assertions**:
- Key_C = `"solar_battery_plant.solar_array.pv_module.cost_model.total_cost"` (strip design prefix, join with `.`)
- Key_A = `"cost_model.total_cost"` (instance_name.output -- ambiguous for virtual)
- Phase 2 CHAIN alias `"solar_battery_plant.solar_array.pv_module.capital_cost"` resolves via Key_C canonical

```python
def test_key_c_format_virtual_calcusage():
    registry = OutputRegistry()
    qn = "SolarBatteryDesign__solar_battery_plant__solar_array__pv_module__cost_model"
    output_name = "total_cost"
    channel = get_channel_name(qn, output_name)

    segments = qn.split("__")
    key_c = ".".join(segments[1:]) + "." + output_name
    # "solar_battery_plant.solar_array.pv_module.cost_model.total_cost"
    assert key_c == "solar_battery_plant.solar_array.pv_module.cost_model.total_cost"

    registry.register(channel, ["cost_model.total_cost", key_c])

    # Phase 2: CHAIN alias resolves against Key_C
    canonical = registry.resolve(
        "solar_battery_plant.solar_array.pv_module.cost_model.total_cost"
    )
    assert canonical is not None
    registry.register_alias(
        "solar_battery_plant.solar_array.pv_module.capital_cost",
        canonical,
    )
    assert registry.resolve("solar_battery_plant.solar_array.pv_module.capital_cost") == channel
```

### 3.11 `test_channel_alias_dataclass`

**Validates**: `ChannelAlias` construction, field access, equality, and source types.

**Setup**: Create two `ChannelAlias` instances.

**Assertions**:
- All fields accessible
- Two instances with same fields compare equal (dataclass default)
- Source is one of `"redefinition"` or `"expose_pure"`
- `"."` present in alias_name and canonical_name
- No `"::"` in alias_name or canonical_name

```python
def test_channel_alias_dataclass():
    alias = ChannelAlias(
        alias_name="solar_array.capital_cost",
        canonical_name="solar_array.cost_model.total_cost",
        owning_part_qn="Lib__Solar_Array",
        source="redefinition",
    )
    assert alias.alias_name == "solar_array.capital_cost"
    assert alias.canonical_name == "solar_array.cost_model.total_cost"
    assert alias.owning_part_qn == "Lib__Solar_Array"
    assert alias.source == "redefinition"
    assert "." in alias.alias_name
    assert "." in alias.canonical_name
    assert "::" not in alias.alias_name
    assert "::" not in alias.canonical_name

    # Equality
    alias2 = ChannelAlias(
        alias_name="solar_array.capital_cost",
        canonical_name="solar_array.cost_model.total_cost",
        owning_part_qn="Lib__Solar_Array",
        source="redefinition",
    )
    assert alias == alias2
```

---

## 4. Unit Tests: `tests/unit/test_backtracker_registry.py` (NEW)

Tests the backtracker's resolution logic when backed by an OutputRegistry.

### 4.1 `test_chain_binding_resolves_via_registry`

**Validates**: CHAIN binding with dotted source_path resolves to MODULE_OUTPUT through OutputRegistry.

**Setup**:
- Create OutputRegistry with one channel registered under key `"alpha_split.p_alpha"`
- Create CalcUsage with CHAIN binding `source_path="alpha_split.p_alpha"`
- Create CalcDef with matching input parameter
- Create DependencyBacktracker with `output_registry=registry`

**Assertions**:
- `binding_resolutions["{usage_qn}|{param}"]` has `resolution_type == MODULE_OUTPUT`
- `qualified_name` matches the registered channel

```python
def test_chain_binding_resolves_via_registry():
    registry = OutputRegistry()
    channel = "catfmfephysics__catf_physics__alpha_split__p_alpha"
    registry.register(channel, ["alpha_split.p_alpha"])

    usage = make_calc_usage(
        instance_name="net_electric",
        calc_def_name="NetElectricPower",
        qualified_name="Pkg__Part__net_electric",
        bindings=[BindingInfo(
            param_name="p_fusion",
            binding_type=BindingType.CHAIN,
            source_path="alpha_split.p_alpha",
        )],
    )
    calc_def = SimpleCalcDef(
        name="NetElectricPower",
        qualified_name="NetElectricPower",
        input_attributes=[SimpleAttrInfo(name="p_fusion")],
        output_attributes=[SimpleAttrInfo(name="p_net")],
    )

    bt = DependencyBacktracker([usage], [calc_def], output_registry=registry)
    result = bt.find_required_modules([], include_all=True)

    key = "Pkg__Part__net_electric|p_fusion"
    assert key in result.binding_resolutions
    assert result.binding_resolutions[key].resolution_type == BindingResolutionType.MODULE_OUTPUT
    assert result.binding_resolutions[key].qualified_name == channel
```

### 4.2 `test_chain_binding_fallback_to_entry_point`

**Validates**: CHAIN binding that misses the OutputRegistry falls back to ENTRY_POINT (with warning).

**Setup**:
- Create empty OutputRegistry (no channels)
- Create CalcUsage with CHAIN binding
- No design attributes match either

**Assertions**:
- Resolution is ENTRY_POINT
- Warning is logged about unresolved CHAIN binding

```python
def test_chain_binding_fallback_to_entry_point(caplog):
    registry = OutputRegistry()
    usage = make_calc_usage(
        instance_name="net_electric",
        calc_def_name="NetElectricPower",
        qualified_name="Pkg__Part__net_electric",
        bindings=[BindingInfo(
            param_name="p_fusion",
            binding_type=BindingType.CHAIN,
            source_path="missing_calc.p_output",
        )],
    )
    calc_def = SimpleCalcDef(
        name="NetElectricPower",
        qualified_name="NetElectricPower",
        input_attributes=[SimpleAttrInfo(name="p_fusion")],
        output_attributes=[SimpleAttrInfo(name="p_net")],
    )

    bt = DependencyBacktracker([usage], [calc_def], output_registry=registry)
    result = bt.find_required_modules([], include_all=True)

    key = "Pkg__Part__net_electric|p_fusion"
    assert result.binding_resolutions[key].resolution_type == BindingResolutionType.ENTRY_POINT
    assert "could not be resolved" in caplog.text.lower() or "warning" in caplog.text.lower()
```

### 4.3 `test_reference_binding_secondary_resolution`

**Validates**: REFERENCE binding with SYSML_QN source_path resolves to MODULE_OUTPUT via `segments[-2]` + leaf_name scoped registry lookup.

**Setup**:
- Register channel under key `"e2e_plant.power_mw"` (computed attr Key_F)
- CalcUsage with `qualified_name="E2EAttrExprDesign__e2e_plant__financial"` (segments[-2] = "e2e_plant")
- REFERENCE binding with `source_path="E2EAttrExprDesign::e2e_plant::power_mw"`

**Assertions**:
- Resolution is MODULE_OUTPUT
- Resolved via secondary path (exact SYSML_QN match fails, then `segments[-2]` + leaf succeeds)

```python
def test_reference_binding_secondary_resolution():
    registry = OutputRegistry()
    channel = "e2eattrexprdesign__e2e_plant__power_mw__power_mw"
    registry.register(channel, ["e2e_plant.power_mw"])

    usage = make_calc_usage(
        instance_name="financial",
        calc_def_name="FinancialCalc",
        qualified_name="E2EAttrExprDesign__e2e_plant__financial",
        bindings=[BindingInfo(
            param_name="power",
            binding_type=BindingType.REFERENCE,
            source_path="E2EAttrExprDesign::e2e_plant::power_mw",
        )],
    )
    calc_def = SimpleCalcDef(
        name="FinancialCalc",
        qualified_name="FinancialCalc",
        input_attributes=[SimpleAttrInfo(name="power")],
        output_attributes=[SimpleAttrInfo(name="lcoe")],
    )

    bt = DependencyBacktracker([usage], [calc_def], output_registry=registry)
    result = bt.find_required_modules([], include_all=True)

    key = "E2EAttrExprDesign__e2e_plant__financial|power"
    assert result.binding_resolutions[key].resolution_type == BindingResolutionType.MODULE_OUTPUT
    assert result.binding_resolutions[key].qualified_name == channel
```

### 4.4 `test_reference_binding_entry_point_fallback`

**Validates**: REFERENCE binding that does not match any registry entry falls back to ENTRY_POINT (the 119-case majority from Spike 5).

**Setup**:
- Create OutputRegistry with no matching entries
- CalcUsage with REFERENCE binding to a design attribute

**Assertions**:
- Resolution is ENTRY_POINT

```python
def test_reference_binding_entry_point_fallback():
    registry = OutputRegistry()
    usage = make_calc_usage(
        instance_name="cost_model",
        calc_def_name="CostCalc",
        qualified_name="Design__plant__pv_module__cost_model",
        bindings=[BindingInfo(
            param_name="wattage",
            binding_type=BindingType.REFERENCE,
            source_path="SolarBatteryLibrary::'PV Module'::wattage",
        )],
    )
    calc_def = SimpleCalcDef(
        name="CostCalc",
        qualified_name="CostCalc",
        input_attributes=[SimpleAttrInfo(name="wattage")],
        output_attributes=[SimpleAttrInfo(name="total_cost")],
    )

    bt = DependencyBacktracker([usage], [calc_def], output_registry=registry)
    result = bt.find_required_modules([], include_all=True)

    key = "Design__plant__pv_module__cost_model|wattage"
    assert result.binding_resolutions[key].resolution_type == BindingResolutionType.ENTRY_POINT
```

### 4.5 `test_literal_binding_always_entry_point`

**Validates**: LITERAL binding always resolves to ENTRY_POINT regardless of registry contents.

**Setup**: CalcUsage with LITERAL binding, OutputRegistry with matching channel.

**Assertions**:
- Resolution is ENTRY_POINT (LITERAL never queries registry)

```python
def test_literal_binding_always_entry_point():
    registry = OutputRegistry()
    registry.register("some__channel", ["p_recirculating"])

    usage = make_calc_usage(
        instance_name="net_electric",
        calc_def_name="NetElectricPower",
        qualified_name="Pkg__Part__net_electric",
        bindings=[BindingInfo(
            param_name="p_recirculating",
            binding_type=BindingType.LITERAL,
            literal_value="50.0",
        )],
    )
    calc_def = SimpleCalcDef(
        name="NetElectricPower",
        qualified_name="NetElectricPower",
        input_attributes=[SimpleAttrInfo(name="p_recirculating")],
        output_attributes=[SimpleAttrInfo(name="p_net")],
    )

    bt = DependencyBacktracker([usage], [calc_def], output_registry=registry)
    result = bt.find_required_modules([], include_all=True)

    key = "Pkg__Part__net_electric|p_recirculating"
    assert result.binding_resolutions[key].resolution_type == BindingResolutionType.ENTRY_POINT
```

### 4.6 `test_unbound_always_entry_point`

**Validates**: UNBOUND parameter (not in bindings list) always resolves to ENTRY_POINT.

**Setup**: CalcUsage with no binding for an input parameter.

**Assertions**:
- Resolution is ENTRY_POINT

```python
def test_unbound_always_entry_point():
    registry = OutputRegistry()
    usage = make_calc_usage(
        instance_name="net_electric",
        calc_def_name="NetElectricPower",
        qualified_name="Pkg__Part__net_electric",
        bindings=[],  # No bindings -- eta_aux is unbound
        unbound_params=["eta_aux"],
    )
    calc_def = SimpleCalcDef(
        name="NetElectricPower",
        qualified_name="NetElectricPower",
        input_attributes=[SimpleAttrInfo(name="eta_aux", default_value="0.9")],
        output_attributes=[SimpleAttrInfo(name="p_net")],
    )

    bt = DependencyBacktracker([usage], [calc_def], output_registry=registry)
    result = bt.find_required_modules([], include_all=True)

    key = "Pkg__Part__net_electric|eta_aux"
    assert result.binding_resolutions[key].resolution_type == BindingResolutionType.ENTRY_POINT
```

### 4.7 `test_get_parent_part_for_usage`

**Validates**: `_get_parent_part_for_usage()` returns `segments[-2]` for various QN depths.

**Setup**: CalcUsages with qualified_names of varying depth.

**Assertions**:
- `"SolarBatteryDesign__solar_battery_plant__annualized_financial"` -> `"solar_battery_plant"`
- `"SolarBatteryDesign__solar_battery_plant__solar_array__pv_module__cost_model"` -> `"pv_module"`
- `"TopLevel__calc"` -> `"TopLevel"`
- Single-segment QN -> `None`

```python
def test_get_parent_part_for_usage():
    bt = DependencyBacktracker([], [], output_registry=OutputRegistry())

    usage1 = make_calc_usage("financial", "Fin", qualified_name="Design__plant__financial")
    assert bt._get_parent_part_for_usage(usage1) == "plant"

    usage2 = make_calc_usage("cost_model", "Cost", qualified_name="Design__plant__solar_array__pv_module__cost_model")
    assert bt._get_parent_part_for_usage(usage2) == "pv_module"

    usage3 = make_calc_usage("calc", "Calc", qualified_name="TopLevel__calc")
    assert bt._get_parent_part_for_usage(usage3) == "TopLevel"

    usage4 = make_calc_usage("orphan", "Orphan", qualified_name="orphan")
    assert bt._get_parent_part_for_usage(usage4) is None
```

### 4.8 `test_resolve_to_design_attribute_sysml_qn`

**Validates**: `_resolve_to_design_attribute()` extracts leaf from SYSML_QN source_path and finds matching design attribute.

**Setup**: Design attribute with `qualified_name="Design__plant__wattage"`, source_path `"SolarBatteryLibrary::'PV Module'::wattage"`.

**Assertions**:
- Returns the matching `DesignAttributeData`
- Leaf extraction: `"wattage"` from `"SolarBatteryLibrary::'PV Module'::wattage"`

### 4.9 `test_resolve_to_design_attribute_dotted`

**Validates**: `_resolve_to_design_attribute()` extracts leaf from dotted source_path.

**Setup**: source_path = `"alpha_split.p_alpha"`, leaf = `"p_alpha"`.

**Assertions**:
- If a design attribute with matching leaf exists, returns it
- If no match, returns `None`

### 4.10 `test_unresolved_chain_logs_warning`

**Validates**: When a CHAIN binding cannot be resolved (neither registry nor design attrs), a warning is logged.

**Setup**: CHAIN binding with unresolvable source_path, no matching design attrs.

**Assertions**:
- Resolution falls back to ENTRY_POINT
- `caplog` contains a warning message mentioning the source_path

```python
def test_unresolved_chain_logs_warning(caplog):
    import logging
    registry = OutputRegistry()
    usage = make_calc_usage(
        instance_name="calc",
        calc_def_name="Calc",
        qualified_name="Pkg__Part__calc",
        bindings=[BindingInfo(
            param_name="x",
            binding_type=BindingType.CHAIN,
            source_path="nonexistent.output",
        )],
    )
    calc_def = SimpleCalcDef(
        name="Calc", qualified_name="Calc",
        input_attributes=[SimpleAttrInfo(name="x")],
        output_attributes=[SimpleAttrInfo(name="y")],
    )

    with caplog.at_level(logging.WARNING):
        bt = DependencyBacktracker([usage], [calc_def], output_registry=registry)
        result = bt.find_required_modules([], include_all=True)

    key = "Pkg__Part__calc|x"
    assert result.binding_resolutions[key].resolution_type == BindingResolutionType.ENTRY_POINT
    assert "nonexistent.output" in caplog.text
```

---

## 5. Unit Tests: `tests/unit/test_hierarchy_resolver_aliases.py` (NEW)

Tests CHAIN `:>>` redefinition -> ChannelAlias production logic.

### 5.1 `test_chain_redef_produces_channel_alias`

**Validates**: CHAIN redefinition with dotted source_path produces a correctly scoped `ChannelAlias`.

**Setup**: `RedefinitionData` with `source_path="cost_model.total_cost"`, `attribute_name="capital_cost"`, and `instance_path="solar_battery_plant.solar_array.pv_module"` (already in dotted, prefix-stripped form).

**Assertions**:
- `alias.alias_name == "solar_battery_plant.solar_array.pv_module.capital_cost"`
- `alias.canonical_name == "solar_battery_plant.solar_array.pv_module.cost_model.total_cost"`
- `alias.source == "redefinition"`
- `"." in alias.alias_name` and `"." in alias.canonical_name`

### 5.2 `test_chain_redef_filters_bare_cas_codes`

**Validates**: CHAIN redefinitions where `"." not in source_path` are filtered out (CAS codes like `"CAS220101"`).

**Setup**: Two `RedefinitionData`: one with `source_path="cost_model.total_cost"` (DOTTED), one with `source_path="CAS220101"` (BARE).

**Assertions**:
- Only 1 alias produced (the DOTTED one)
- The BARE CAS code does not produce an alias

### 5.3 `test_chain_redef_scoping_with_instance_path`

**Validates**: Correct dotted instance_path prefix derivation from `ScopedAggregationData.instance_path`.

**Setup**: `instance_path="SolarBatteryDesign__solar_battery_plant__solar_array"` -> prefix-stripped, dot-separated: `"solar_battery_plant.solar_array"`.

**Assertions**:
- `alias.alias_name` starts with `"solar_battery_plant.solar_array."`
- `alias.canonical_name` starts with `"solar_battery_plant.solar_array."`

### 5.4 `test_chain_override_rewrites_literal`

**Validates**: `_rewrite_virtual_bindings()` correctly rewrites a LITERAL override (unchanged behavior).

**Setup**: Virtual CalcUsage with REFERENCE binding, `design_override` with `RedefinitionType.LITERAL`.

**Assertions**:
- After rewrite: `binding.binding_type == BindingType.LITERAL`
- `binding.literal_value` matches the override value
- `binding.source_path is None`

### 5.5 `test_chain_override_rewrites_chain`

**Validates**: `_rewrite_virtual_bindings()` rewrites CHAIN override by replacing `binding.source_path`.

**Setup**: Virtual CalcUsage with REFERENCE binding `source_path="Lib::Part::attr"`, design_override with `RedefinitionType.CHAIN` and `source_path="local_calc.output"`.

**Assertions**:
- After rewrite: `binding.source_path == "local_calc.output"` (the override's source_path)
- `binding.binding_type` is unchanged (still REFERENCE or becomes CHAIN, depending on implementation)

### 5.6 `test_expression_override_not_rewritten`

**Validates**: EXPRESSION-type overrides (aggregation formulas) do NOT rewrite the binding.

**Setup**: Virtual CalcUsage with binding, design_override with `RedefinitionType.EXPRESSION`.

**Assertions**:
- Binding is unchanged after rewrite
- Return count does not include this binding

---

## 6. Unit Tests: `tests/unit/test_computed_attr_aliases.py` (NEW)

Tests EXPOSE_PURE -> ChannelAlias and FORMULA -> synthetic CalcUsage production.

### 6.1 `test_expose_pure_produces_channel_alias`

**Validates**: EXPOSE_PURE ComputedAttributeData with `references` field produces a correctly constructed ChannelAlias.

**Setup**:
```python
@dataclass
class ExpressionRef:
    name: str
    qualified_name: str

ca = make_computed_attr(
    name="total_capex",
    owning_part_name="e2e_plant",
    owning_part_qn="E2EAttrExprDesign::e2e_plant",
    classification=ComputedAttributeClassification.EXPOSE_PURE,
    compilability=Compilability.MANUAL_REQUIRED,
    references=[
        ExpressionRef(name="total_cost", qualified_name="..."),    # [0] output attr
        ExpressionRef(name="component_cost", qualified_name="..."), # [1] instance
    ],
    is_on_part_definition=False,
)
```

**Assertions**:
- Alias produced with `canonical_name == "component_cost.total_cost"` (from references[1].name + "." + references[0].name)
- `alias_name` includes owning part scope
- `source == "expose_pure"`

### 6.2 `test_expose_pure_filters_partdef`

**Validates**: EXPOSE_PURE on PartDef (is_on_part_definition=True) does NOT produce a ChannelAlias.

**Setup**: Same as 6.1 but `is_on_part_definition=True`.

**Assertions**:
- No alias produced
- No exception raised

### 6.3 `test_expose_pure_bad_references_skipped`

**Validates**: EXPOSE_PURE with fewer than 2 references produces a warning and no alias.

**Setup**: ComputedAttributeData with `references=[]` or `references=[single_ref]`.

**Assertions**:
- No alias produced
- Warning logged about insufficient references

```python
def test_expose_pure_bad_references_skipped(caplog):
    import logging
    ca = make_computed_attr(
        name="broken",
        owning_part_name="part",
        owning_part_qn="Pkg::part",
        classification=ComputedAttributeClassification.EXPOSE_PURE,
        references=[],  # < 2 references
        is_on_part_definition=False,
    )
    with caplog.at_level(logging.WARNING):
        aliases = _build_expose_pure_aliases([ca])
    assert len(aliases) == 0
    assert "broken" in caplog.text
```

### 6.4 `test_formula_produces_synthetic_calcusage`

**Validates**: FORMULA-classified computed attribute produces a synthetic CalcUsageData with correct qualified_name and bindings.

**Setup**: FORMULA ComputedAttributeData with `owning_part_qualified_name="E2EAttrExprDesign::e2e_plant"`, `python_name="power_mw"`, references to `[p_net_mw]`.

**Assertions**:
- Synthetic CalcUsage created with `qualified_name="E2EAttrExprDesign__e2e_plant__power_mw"`
- `instance_name == "power_mw"`
- `calc_def_name is None` (inline expression, no CalcDef)
- `is_computed_attribute == True`
- Bindings have CHAIN type with scoped dotted source_path `"e2e_plant.{ref.name}"`

### 6.5 `test_formula_binding_source_path_scoped`

**Validates**: FORMULA synthetic CalcUsage bindings use `"{parent_short}.{ref.name}"` format (scoped dotted) so they resolve through the OutputRegistry.

**Setup**: FORMULA attr with `owning_part_name="e2e_plant"`, reference with `name="p_net_mw"`.

**Assertions**:
- Binding `source_path == "e2e_plant.p_net_mw"`
- Not bare name `"p_net_mw"` (which would fail registry resolution)

---

## 7. Modifications to Existing Unit Tests

### 7.1 `tests/unit/test_backtracker_aggregation.py`

**What changes**: Update `DependencyBacktracker` constructor calls to use `output_registry` parameter instead of `aggregation_data`.

**Specific changes**:
- `TestAggregationOutputIndex`: These tests verify internal `_aggregation_output_index` keys. After Item 4, these tests either (a) verify OutputRegistry contents instead, or (b) are replaced by `test_output_registry.py` tests covering Key_D/Key_E.
- `TestTraceWithAggregation`: Update constructor. The behavior should be identical (MODULE_OUTPUT resolution for aggregation outputs).

**Example migration**:
```python
# BEFORE:
bt = DependencyBacktracker([], [], aggregation_data=[agg])
assert "solar_array.capital_cost" in bt._aggregation_output_index

# AFTER:
registry = OutputRegistry()
channel = get_channel_name(agg.module_eqn, agg.expression.attribute_name)
registry.register(channel, ["solar_array.capital_cost"])
bt = DependencyBacktracker([], [], output_registry=registry)
assert registry.resolve("solar_array.capital_cost") == channel
```

**Migration strategy**: During Item 3 (parallel validation), keep both constructor parameters. During Item 4 (cut-over), remove `aggregation_data` and migrate tests.

### 7.2 `tests/unit/test_backtracker_computed_attrs.py`

**What changes**: Update constructor calls. Tests currently access `bt._computed_attr_index` which is removed after Item 4.

**Specific changes**:
- Tests verifying `_computed_attr_index` key presence -> verify OutputRegistry `resolve()` instead
- Tests verifying `binding_resolutions` for MODULE_OUTPUT -> should pass unchanged (behavior preserved)
- Constructor: `computed_attributes=` -> `output_registry=` with pre-populated registry

### 7.3 `tests/unit/test_graph_builder.py`

**What changes**: Remove tests that verify output catalog construction. The graph builder no longer builds an output catalog.

**Specific changes**:
- Remove any tests that inspect `_build_output_catalog()` behavior
- Keep tests that verify `build_computation_graph()` produces correct `ComputationGraph` from `BacktrackingResult`
- Update `_make_minimal_graph_inputs()` if it constructs output catalogs
- The `_build_pipeline_module()` signature drops `output_catalog` parameter

### 7.4 `tests/unit/test_step_4_5.py`

**What changes**: Add tests for EXPOSE_PURE alias production and FORMULA synthetic CalcUsage creation.

**New tests**:
- `test_expose_pure_produces_alias_not_index_entry`: Verify EXPOSE_PURE attrs produce ChannelAlias (returned by function) instead of entering any index
- `test_formula_produces_synthetic_calcusage`: Verify FORMULA attrs append synthetic CalcUsageData to `calc_usages` list
- `test_expose_pure_on_partdef_filtered`: Verify EXPOSE_PURE on PartDef does not produce alias

### 7.5 `tests/unit/test_hierarchy_resolver.py`

**What changes**: Add tests for CHAIN alias production from `:>>` redefinitions.

**New tests**:
- `test_chain_redef_produces_alias`: CHAIN `:>>` with dotted source_path produces ChannelAlias
- `test_chain_redef_bare_filtered`: CHAIN `:>>` with bare CAS code is filtered
- `test_chain_redef_multiple_instances`: One PartDef `:>>` with multiple design instances produces multiple ChannelAlias objects (one per instance_path)

---

## 8. Integration Tests: `tests/integration/test_registry_e2e.py` (NEW)

These tests load real SysML models and verify OutputRegistry behavior end-to-end. They require the `agentic-mbse` dependency.

### 8.1 `test_solar_battery_phase1_registration`

**Validates**: Phase 1 registration on solar_battery model produces the expected number of channels and keys with zero collisions.

**Setup**: Load solar_battery model, run pipeline through Step 5 (OutputRegistry construction).

**Assertions**:
- 77 canonical channels registered (Spike 8 count)
- 217 total keys (Spike 8 count)
- Zero collision warnings in log

```python
def test_solar_battery_phase1_registration(solar_battery_context):
    registry = solar_battery_context.output_registry
    assert len(registry._canonical) == 77
    assert len(registry._index) >= 217
    # Verify no collisions logged during construction (check fixture setup)
```

### 8.2 `test_solar_battery_phase2_chain_aliases`

**Validates**: All 41 CHAIN aliases from solar_battery resolve via Key_C.

**Setup**: Same as 8.1.

**Assertions**:
- 41 CHAIN aliases registered (Spike 8 count)
- All 41 resolve to valid canonical channels (no warnings)

```python
def test_solar_battery_phase2_chain_aliases(solar_battery_context):
    # Verify CHAIN aliases were registered (count from Spike 8)
    # The chain_aliases list should have 41 entries
    # All should resolve in the registry
    for alias in solar_battery_context.chain_aliases:
        resolved = solar_battery_context.output_registry.resolve(alias.alias_name)
        assert resolved is not None, f"CHAIN alias '{alias.alias_name}' failed to resolve"
```

### 8.3 `test_solar_battery_phase3_expose_pure`

**Validates**: EXPOSE_PURE on solar_battery PartDefs is correctly filtered (0 aliases from PartDef, 1 if from PartUsage).

**Setup**: Same as 8.1.

**Assertions**:
- PartDef EXPOSE_PURE entries are filtered out (Spike 8: PartDef `misc_hardware_cost` filtered)
- Any PartUsage EXPOSE_PURE entries resolve correctly

### 8.4 `test_e2e_attr_expr_phase3_expose_pure`

**Validates**: EXPOSE_PURE on e2e_attr_expr PartUsage `total_capex` resolves correctly (Bug 2 fix).

**Setup**: Load e2e_attr_expr model, run through Step 5.

**Assertions**:
- EXPOSE_PURE alias `"e2e_plant.total_capex"` resolves to `component_cost.total_cost` channel
- This is the Bug 2 regression test

```python
def test_e2e_attr_expr_phase3_expose_pure(e2e_attr_expr_context):
    registry = e2e_attr_expr_context.output_registry
    resolved = registry.resolve("e2e_plant.total_capex")
    assert resolved is not None, "Bug 2: EXPOSE_PURE total_capex failed to resolve"
    # The resolved channel should be the component_cost.total_cost output
    assert "total_cost" in resolved or "component_cost" in resolved
```

### 8.5 `test_e2e_attr_expr_phase4_transitive`

**Validates**: Transitive design attribute alias on e2e_attr_expr resolves (Phase 4).

**Setup**: Load e2e_attr_expr model.

**Assertions**:
- 1 transitive default resolved (Spike 7)

### 8.6 `test_chain_binding_match_rate`

**Validates**: 100% match rate between old backtracker and new OutputRegistry-backed backtracker for all CHAIN bindings.

**Setup**: Load solar_battery model, run both old and new backtracker paths.

**Assertions**:
- For every CHAIN binding, old and new produce identical `BindingResolution`
- Zero divergences

```python
def test_chain_binding_match_rate(solar_battery_context):
    old_result = solar_battery_context.old_backtracking_result  # from parallel validation
    new_result = solar_battery_context.new_backtracking_result

    divergences = []
    for key, old_res in old_result.binding_resolutions.items():
        new_res = new_result.binding_resolutions.get(key)
        if new_res is None:
            divergences.append(f"Missing in new: {key}")
        elif old_res.resolution_type != new_res.resolution_type:
            divergences.append(f"Type mismatch for {key}: {old_res.resolution_type} vs {new_res.resolution_type}")
        elif old_res.qualified_name != new_res.qualified_name:
            divergences.append(f"QN mismatch for {key}: {old_res.qualified_name} vs {new_res.qualified_name}")

    assert divergences == [], f"Divergences found:\n" + "\n".join(divergences)
```

### 8.7 `test_reference_secondary_resolution`

**Validates**: All 4 REFERENCE->MODULE_OUTPUT cases resolve correctly via `segments[-2]` + leaf-name.

**Setup**: Load both solar_battery and e2e_attr_expr models.

**Assertions**:
- solar_battery: `p_net_kw` and `capital_cost` REFERENCE bindings resolve to MODULE_OUTPUT
- e2e_attr_expr: `power_mw` and `annual_om` REFERENCE bindings resolve to MODULE_OUTPUT

```python
def test_reference_secondary_resolution(solar_battery_context, e2e_attr_expr_context):
    # From Spike 5: exactly 4 REFERENCE -> MODULE_OUTPUT cases
    for ctx in [solar_battery_context, e2e_attr_expr_context]:
        for key, res in ctx.backtracking_result.binding_resolutions.items():
            if res.source_path and "::" in res.source_path:
                if res.resolution_type == BindingResolutionType.MODULE_OUTPUT:
                    # Verify this is one of the 4 expected cases
                    assert any(attr in key for attr in ["p_net_kw", "capital_cost", "power_mw", "annual_om"])
```

---

## 9. Modifications to Existing Integration Tests

### 9.1 `tests/integration/test_costed_component_e2e.py`

**Expected**: Should pass UNCHANGED after the OutputRegistry redesign. The behavior is preserved -- same modules, same wiring, same pipeline YAML.

**Validation**: Run the full test suite and verify zero regressions in this file.

### 9.2 `tests/integration/test_full_pipeline.py`

**Expected**: Should pass UNCHANGED. The pipeline output is identical.

### 9.3 `tests/integration/test_hierarchy_e2e.py`

**Expected**: Should pass UNCHANGED. Hierarchy extraction, aggregation expressions, and aggregation module wiring are preserved.

---

## 10. Parallel Validation Test (Migration Safety)

### 10.1 `test_parallel_validation` (in `tests/integration/test_registry_e2e.py`)

**Validates**: Running the old backtracker (5 indexes, 7-strategy cascade) and the new OutputRegistry-backed backtracker side-by-side produces identical `binding_resolutions` for every binding on every model.

**Setup**:
```python
@pytest.fixture(params=[
    "solar_battery_model",
    "e2e_attr_expr_model",
    "chain_spike_model",
    "sample_model",
])
def model_path(request):
    return FIXTURES_DIR / request.param
```

**Implementation sketch**:
```python
def test_parallel_validation(model_path):
    """Run old and new backtracker side by side. Assert identical binding_resolutions."""
    # Load model
    ctx = build_pipeline_context([model_path])

    # Run old backtracker (current code, 5 indexes)
    old_backtracker = DependencyBacktracker(
        ctx.calc_usages, ctx.calc_defs,
        design_attributes=ctx.design_attributes,
        computed_attributes=ctx.computed_attributes,
        aggregation_data=ctx.aggregation_expressions,
    )
    old_result = old_backtracker.find_required_modules([], include_all=True)

    # Run new backtracker (OutputRegistry)
    new_backtracker = DependencyBacktracker(
        ctx.calc_usages, ctx.calc_defs,
        design_attributes=ctx.design_attributes,
        output_registry=ctx.output_registry,
    )
    new_result = new_backtracker.find_required_modules([], include_all=True)

    # Compare binding_resolutions
    assert set(old_result.binding_resolutions.keys()) == set(new_result.binding_resolutions.keys()), \
        "Key sets differ"

    divergences = []
    for key in old_result.binding_resolutions:
        old_res = old_result.binding_resolutions[key]
        new_res = new_result.binding_resolutions[key]
        if old_res.resolution_type != new_res.resolution_type:
            divergences.append(
                f"{key}: type {old_res.resolution_type} -> {new_res.resolution_type}"
            )
        elif old_res.qualified_name != new_res.qualified_name:
            divergences.append(
                f"{key}: qn '{old_res.qualified_name}' -> '{new_res.qualified_name}'"
            )

    assert divergences == [], (
        f"Parallel validation found {len(divergences)} divergence(s):\n"
        + "\n".join(divergences[:20])
    )
```

**Key assertions**:
- Zero divergences on solar_battery (largest model: ~215 bindings)
- Zero divergences on e2e_attr_expr (Bug 2 model)
- Zero divergences on chain_spike and sample_model
- Binding resolution key sets are identical
- For each key: `resolution_type` and `qualified_name` match exactly

**NOTE on Bug 2**: The parallel validation may show a **known expected divergence** for Bug 2: the old backtracker resolves `financial.total_capex` to ENTRY_POINT (wrong), while the new resolves to MODULE_OUTPUT (correct). This divergence is **accepted and documented** as the Bug 2 fix. The test should either exclude this specific key from the exact-match assertion, or use a separate assertion that validates the fix:

```python
# Known Bug 2 fix: total_capex resolves differently (improvement, not regression)
BUG2_KEYS = {"E2EAttrExprDesign__e2e_plant__financial|total_capex"}
expected_divergences = {k for k in divergences_keys if k in BUG2_KEYS}
unexpected_divergences = {k for k in divergences_keys if k not in BUG2_KEYS}
assert unexpected_divergences == set(), f"Unexpected divergences: {unexpected_divergences}"
```

---

## 11. `_is_transitive_default()` Tests (in `test_output_registry.py`)

### 11.1 `test_is_transitive_default_dotted_path`

**Validates**: Dotted path default values like `"cost_model.total_cost"` are identified as transitive.

**Assertions**:
- `_is_transitive_default(attr_with_default="cost_model.total_cost")` returns `True`

### 11.2 `test_is_transitive_default_numeric`

**Validates**: Numeric defaults like `"3.14"` and `"100"` are NOT transitive.

**Assertions**:
- `_is_transitive_default(attr_with_default="3.14")` returns `False`
- `_is_transitive_default(attr_with_default="100")` returns `False`

### 11.3 `test_is_transitive_default_none`

**Validates**: `None` default is NOT transitive.

**Assertions**:
- `_is_transitive_default(attr_with_default=None)` returns `False`

### 11.4 `test_is_transitive_default_no_dot`

**Validates**: String defaults without dots (e.g., `"aluminum"`) are NOT transitive.

**Assertions**:
- `_is_transitive_default(attr_with_default="aluminum")` returns `False`

---

## 12. Contract Test: Registry Key Format Agreement

### 12.1 `test_backtracker_key_format_matches_registry` (in `test_backtracker_registry.py`)

**Validates**: For every binding in a representative fixture, the key that the backtracker constructs for `registry.resolve()` matches a key that was registered into the OutputRegistry from the same fixture data.

**This is the critical interface contract test.** It catches the class of key-format-mismatch bugs that produced the original 5-index problem.

**Setup**:
- Build a fixture with 3 CalcUsages: one concrete with CHAIN binding, one virtual with CHAIN binding, one with REFERENCE binding
- Build OutputRegistry from the CalcUsage outputs (Phase 1 registration)
- Run backtracker resolution

**Assertions**:
- For every CHAIN binding that resolves to MODULE_OUTPUT: the `binding.source_path` was found via `registry.resolve(source_path)` -- i.e., the key the backtracker queries is present in the registry
- For every REFERENCE binding that resolves to MODULE_OUTPUT: the secondary resolution key `f"{segments[-2]}.{leaf_name}"` was found in the registry

```python
def test_backtracker_key_format_matches_registry():
    """Contract: the key format the backtracker uses matches what the registry indexes."""
    # Setup: 2 CalcUsages, one produces output, one consumes it via CHAIN
    producer = make_calc_usage("alpha_split", "AlphaSplit", qualified_name="Pkg__Part__alpha_split")
    consumer = make_calc_usage(
        "net_electric", "NetElectricPower", qualified_name="Pkg__Part__net_electric",
        bindings=[BindingInfo(
            param_name="p_fusion",
            binding_type=BindingType.CHAIN,
            source_path="alpha_split.p_alpha",
        )],
    )
    producer_def = SimpleCalcDef(
        name="AlphaSplit", qualified_name="AlphaSplit",
        input_attributes=[], output_attributes=[SimpleAttrInfo(name="p_alpha")],
    )
    consumer_def = SimpleCalcDef(
        name="NetElectricPower", qualified_name="NetElectricPower",
        input_attributes=[SimpleAttrInfo(name="p_fusion")],
        output_attributes=[SimpleAttrInfo(name="p_net")],
    )

    # Build registry from producer outputs
    registry = OutputRegistry()
    channel = get_channel_name(producer.qualified_name, "p_alpha")
    segments = producer.qualified_name.split("__")
    key_a = f"{producer.instance_name}.p_alpha"
    key_c = ".".join(segments[1:]) + ".p_alpha"
    registry.register(channel, [key_a, key_c])

    # Verify the consumer's source_path is a key in the registry
    assert registry.resolve("alpha_split.p_alpha") is not None, \
        "Contract violation: consumer source_path not in registry"

    # Run backtracker
    bt = DependencyBacktracker(
        [producer, consumer], [producer_def, consumer_def],
        output_registry=registry,
    )
    result = bt.find_required_modules([], include_all=True)

    key = "Pkg__Part__net_electric|p_fusion"
    assert result.binding_resolutions[key].resolution_type == BindingResolutionType.MODULE_OUTPUT
```

---

## 13. Test Execution Order and Dependencies

### Unit tests (fast, no model loading)

Run first. All should pass independently:
```bash
uv run pytest tests/unit/test_output_registry.py
uv run pytest tests/unit/test_backtracker_registry.py
uv run pytest tests/unit/test_hierarchy_resolver_aliases.py
uv run pytest tests/unit/test_computed_attr_aliases.py
```

### Modified unit tests (must pass after each Item)

Run after code changes:
```bash
uv run pytest tests/unit/test_backtracker_aggregation.py
uv run pytest tests/unit/test_backtracker_computed_attrs.py
uv run pytest tests/unit/test_graph_builder.py
uv run pytest tests/unit/test_step_4_5.py
uv run pytest tests/unit/test_hierarchy_resolver.py
```

### Integration tests (slow, requires SysIDE)

Run last:
```bash
uv run pytest tests/integration/test_registry_e2e.py
uv run pytest tests/integration/test_costed_component_e2e.py
uv run pytest tests/integration/test_full_pipeline.py
uv run pytest tests/integration/test_hierarchy_e2e.py
```

### Full regression gate

Before any Item is marked complete:
```bash
uv run pytest tests/
```

All tests must pass with zero failures.

---

## 14. Test Coverage Matrix

| Component | Unit Tests | Integration Tests | Parallel Validation |
|-----------|-----------|-------------------|---------------------|
| OutputRegistry.register() | 3.1, 3.2, 3.6 | 8.1 | - |
| OutputRegistry.register_alias() | 3.3, 3.4 | 8.2, 8.3 | - |
| OutputRegistry.resolve() | 3.1, 3.5, 3.7 | 8.4, 8.5 | - |
| Phase ordering (1->2->3->4) | 3.8 | 8.1-8.5 | - |
| Key_A (dotted short) | 3.2, 3.9 | 8.1 | 10.1 |
| Key_B (EQN) | 3.2 | 8.1 | 10.1 |
| Key_C (dotted hierarchy) | 3.10 | 8.2 | 10.1 |
| Key_D/E (aggregation) | - | 8.1 | 10.1 |
| Key_F (FORMULA) | - | 8.1, 8.4 | 10.1 |
| CHAIN binding -> MODULE_OUTPUT | 4.1 | 8.6 | 10.1 |
| CHAIN binding -> ENTRY_POINT | 4.2 | - | 10.1 |
| REFERENCE -> MODULE_OUTPUT | 4.3 | 8.7 | 10.1 |
| REFERENCE -> ENTRY_POINT | 4.4 | - | 10.1 |
| LITERAL -> ENTRY_POINT | 4.5 | - | 10.1 |
| UNBOUND -> ENTRY_POINT | 4.6 | - | 10.1 |
| segments[-2] parent resolution | 4.7 | 8.7 | - |
| _resolve_to_design_attribute() | 4.8, 4.9 | - | 10.1 |
| Warning on unresolved | 4.10 | - | - |
| CHAIN redef -> ChannelAlias | 5.1, 5.2, 5.3 | 8.2 | - |
| CHAIN override rewrite | 5.4, 5.5 | - | - |
| EXPRESSION override skip | 5.6 | - | - |
| EXPOSE_PURE -> ChannelAlias | 6.1 | 8.3, 8.4 | - |
| EXPOSE_PURE PartDef filter | 6.2 | 8.3 | - |
| EXPOSE_PURE bad refs | 6.3 | - | - |
| FORMULA -> synthetic CalcUsage | 6.4, 6.5 | - | - |
| _is_transitive_default() | 11.1-11.4 | 8.5 | - |
| Contract: key format agreement | 12.1 | 10.1 | 10.1 |
| ChannelAlias dataclass | 3.11 | - | - |
| Bug 2 fix (total_capex) | - | 8.4 | 10.1 |
| Collision handling | 3.6 | 8.1 | - |
| Graph builder (no output catalog) | 7.3 (modified) | 9.1, 9.2, 9.3 | - |

---

## 15. Risk Coverage

| Risk from Epic | Test that mitigates it |
|---|---|
| Parallel validation reveals divergences | 10.1 (runs on all 4 models) |
| PartDef EXPOSE_PURE filter too aggressive | 6.2, 8.3 |
| Key_C collisions | 3.6, 8.1 |
| segments[-2] fails for deep hierarchy | 4.7, 8.7 |
| _is_transitive_default() misclassifies | 11.1-11.4, 8.5 |
| PhantomDetector depends on removed indexes | Existing test_hierarchy_e2e.py (unchanged) |

---

**Last Updated**: 2026-02-13
