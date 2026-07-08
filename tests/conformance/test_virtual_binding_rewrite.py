"""Conformance tests for Virtual Binding Rewrite (C09).

Tests REQ-VBR-01 through REQ-VBR-07 from design intent doc 12-virtual-binding-rewrite.md.

Testing strategy:
- Snapshot data is POST-rewrite (captured via build_pipeline_context which calls
  _rewrite_virtual_bindings at Step 3.5). Tests that need pre-rewrite state use
  the reconstruct_pre_rewrite_bindings() helper to restore REFERENCE bindings.
- CHAIN overrides, template-skip, flat overrides, and EXPRESSION-skip tests use
  constructed CalcUsageData with real qualified names from the solar_battery snapshot.
- No mocks. All data comes from real extraction snapshots or is constructed from
  real field values.
"""

from __future__ import annotations

import ast
import copy
import inspect
from pathlib import Path

import pytest

from sysml_codegen.extraction.data_models import (
    HierarchyExtractionResult,
    RedefinitionData,
    RedefinitionType,
)
from sysml_codegen.extraction.usage_extractor import (
    BindingInfo,
    BindingType,
    CalcUsageData,
)
from sysml_codegen.orchestration.pipeline_builder import _rewrite_virtual_bindings

# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------

def _build_override_index(
    design_overrides: list[RedefinitionData],
) -> dict[tuple[str, str], RedefinitionData]:
    """Reproduce Phase 1 of _rewrite_virtual_bindings(): build the override index.

    Extracted so REQ-VBR-01 and REQ-VBR-02 can test index construction directly.
    """
    index: dict[tuple[str, str], RedefinitionData] = {}
    for override in design_overrides:
        if override.is_deep_path and len(override.target_path) >= 2:
            intermediate = "__".join(override.target_path[:-1])
            full_parent = f"{override.owning_part_qn}__{intermediate}"
            leaf_attr = override.target_path[-1]
            index[(full_parent, leaf_attr)] = override
        elif not override.is_deep_path:
            full_parent = override.owning_part_qn
            index[(full_parent, override.attribute_name)] = override
    return index


def _reconstruct_pre_rewrite_bindings(
    calc_usages: list[CalcUsageData],
    design_overrides: list[RedefinitionData],
) -> list[tuple[CalcUsageData, BindingInfo, RedefinitionData]]:
    """Restore post-rewrite LITERAL bindings to pre-rewrite REFERENCE state.

    For each design_override, finds the matching CalcUsage binding and sets it
    back to REFERENCE with source_path derived from the usage's owning_part_def_qn.

    Returns list of (usage, binding, override) triples that were restored.
    """
    index = _build_override_index(design_overrides)
    restored = []

    for key, override in index.items():
        full_parent, leaf = key
        for usage in calc_usages:
            if usage.is_template:
                continue
            parts = usage.qualified_name.rsplit("__", 1)
            if len(parts) < 2:
                continue
            parent_path = parts[0]
            if parent_path != full_parent:
                continue

            for binding in usage.bindings:
                if binding.param_name == leaf:
                    owning_def_sysml = (
                        usage.owning_part_def_qn.replace("__", "::")
                        if usage.owning_part_def_qn
                        else "UNKNOWN"
                    )
                    binding.binding_type = BindingType.REFERENCE
                    binding.source_path = f"{owning_def_sysml}::{leaf}"
                    binding.literal_value = None
                    restored.append((usage, binding, override))
                    break

    return restored


def _make_binding(
    param_name: str,
    source_path: str | None = None,
    binding_type: BindingType = BindingType.REFERENCE,
    literal_value: float | int | str | bool | None = None,
) -> BindingInfo:
    """Create a BindingInfo with sensible defaults for test construction."""
    return BindingInfo(
        param_name=param_name,
        source_path=source_path,
        binding_type=binding_type,
        is_cross_file=False,
        raw_expression=param_name,
        source_instance_elem=None,
        source_attribute_elem=None,
        literal_value=literal_value,
        expression_ast=None,
    )


def _make_calc_usage(
    qualified_name: str,
    bindings: list[BindingInfo],
    is_template: bool = False,
    owning_part_def_qn: str | None = None,
) -> CalcUsageData:
    """Create a CalcUsageData with sensible defaults for test construction."""
    return CalcUsageData(
        instance_name=(
            qualified_name.rsplit("__", 1)[-1]
            if "__" in qualified_name
            else qualified_name
        ),
        calc_def_name="TestCalc",
        calc_def_qualified_name="TestLib::TestCalc",
        module_type="testlib.TestCalcModule",
        bindings=bindings,
        unbound_params=[],
        source_file=Path("unknown"),
        source_line=0,
        parent_part_path=qualified_name.replace("__", "."),
        qualified_name=qualified_name,
        is_template=is_template,
        owning_part_def_qn=owning_part_def_qn,
        raw_element=None,
    )


def _make_override(
    owning_part_qn: str,
    attribute_name: str,
    redefinition_type: RedefinitionType = RedefinitionType.LITERAL,
    literal_value: float | int | str | bool | None = None,
    source_path: str | None = None,
    target_path: list[str] | None = None,
    is_deep_path: bool = True,
) -> RedefinitionData:
    """Create a RedefinitionData with sensible defaults for test construction."""
    return RedefinitionData(
        owning_part_qn=owning_part_qn,
        attribute_name=attribute_name,
        redefinition_type=redefinition_type,
        literal_value=literal_value,
        source_path=source_path,
        expression_ast=None,
        expression_text=str(literal_value) if literal_value else (source_path or ""),
        target_path=target_path or [attribute_name],
        is_deep_path=is_deep_path,
        source_file=Path("unknown"),
        source_line=0,
    )


def _make_hierarchy_data(
    design_overrides: list[RedefinitionData],
) -> HierarchyExtractionResult:
    """Create a minimal HierarchyExtractionResult with only design_overrides populated."""
    return HierarchyExtractionResult(
        redefinitions=[],
        design_overrides=design_overrides,
        multiplicities=[],
        aggregation_expressions=[],
        warnings=[],
        part_usage_names={},
        usage_type_map={},
    )


# ---------------------------------------------------------------------------
# REQ-VBR-01: Override index keyed by (full_parent_path, leaf_attribute_name)
# ---------------------------------------------------------------------------


@pytest.mark.req("REQ-VBR-01")
class TestOverrideIndexKey:
    """REQ-VBR-01: Override index SHALL be keyed by (full_parent_path, leaf_attribute_name)."""

    def test_override_index_structure(self, solar_battery_snapshot):
        """All 13 design_overrides produce (full_parent, leaf) tuple keys."""
        hierarchy = solar_battery_snapshot["hierarchy_data"]
        index = _build_override_index(hierarchy.design_overrides)

        assert len(index) == 13
        for key in index:
            assert isinstance(key, tuple), f"Key should be tuple, got {type(key)}"
            assert len(key) == 2, f"Key should have 2 elements, got {len(key)}"
            full_parent, leaf = key
            assert isinstance(full_parent, str)
            assert isinstance(leaf, str)
            assert "__" in full_parent, f"full_parent should contain '__': {full_parent}"
            assert "__" not in leaf, f"leaf should be a simple name: {leaf}"

    def test_specific_override_keys(self, solar_battery_snapshot):
        """Spot-check specific override index keys for known overrides."""
        hierarchy = solar_battery_snapshot["hierarchy_data"]
        index = _build_override_index(hierarchy.design_overrides)

        # fmt: off
        sa = "SolarBatteryDesign__solar_battery_plant__solar_array"
        bs = "SolarBatteryDesign__solar_battery_plant__battery_system"
        si = "SolarBatteryDesign__solar_battery_plant__site_infra"
        expected_keys = [
            (f"{sa}__pv_module", "wattage"),
            (f"{sa}__pv_module", "efficiency"),
            (f"{sa}__inverter", "power_rating"),
            (f"{sa}__array_bos", "string_count"),
            (f"{sa}__array_bos", "panel_count"),
            (f"{bs}__battery_pack", "capacity_kwh"),
            (f"{bs}__battery_pack", "chemistry_factor"),
            (f"{bs}__hybrid_inverter", "power_rating"),
            (f"{bs}__battery_bos", "pack_count"),
            (f"{si}__racking", "panel_count"),
            (f"{si}__racking", "tilt_angle"),
            (f"{si}__electrical_panel", "circuit_count"),
            (f"{si}__permitting", "system_capacity_kw"),
        ]
        # fmt: on
        for key in expected_keys:
            assert key in index, f"Expected key {key} not in override index"

    def test_empty_overrides_returns_zero(self):
        """Empty design_overrides causes _rewrite_virtual_bindings to return 0 immediately."""
        hierarchy = _make_hierarchy_data(design_overrides=[])
        usage = _make_calc_usage(
            qualified_name="Design__part__calc",
            bindings=[_make_binding("x", source_path="Lib::Part::x")],
            owning_part_def_qn="Lib__Part",
        )
        count = _rewrite_virtual_bindings([usage], hierarchy)
        assert count == 0


# ---------------------------------------------------------------------------
# REQ-VBR-02: Deep-path joins intermediate segments with __
# ---------------------------------------------------------------------------


@pytest.mark.req("REQ-VBR-02")
class TestDeepPathJoin:
    """REQ-VBR-02: Deep-path overrides SHALL join intermediate target_path segments with __."""

    def test_deep_path_join_all_overrides(self, solar_battery_snapshot):
        """Every deep-path override produces full_parent with intermediate segments joined by __."""
        hierarchy = solar_battery_snapshot["hierarchy_data"]
        index = _build_override_index(hierarchy.design_overrides)

        for override in hierarchy.design_overrides:
            assert override.is_deep_path, "All solar_battery overrides are deep-path"
            assert len(override.target_path) >= 2, (
                f"Deep-path needs >= 2 segments: {override.target_path}"
            )

            intermediate = "__".join(override.target_path[:-1])
            expected_parent = f"{override.owning_part_qn}__{intermediate}"
            leaf = override.target_path[-1]

            assert (expected_parent, leaf) in index, (
                f"Key ({expected_parent}, {leaf}) not in index"
            )

    @pytest.mark.parametrize(
        "target_path, owning_part_qn, expected_parent, expected_leaf",
        [
            (
                ["pv_module", "wattage"],
                "SolarBatteryDesign__solar_battery_plant__solar_array",
                "SolarBatteryDesign__solar_battery_plant__solar_array__pv_module",
                "wattage",
            ),
            (
                ["battery_pack", "capacity_kwh"],
                "SolarBatteryDesign__solar_battery_plant__battery_system",
                "SolarBatteryDesign__solar_battery_plant__battery_system__battery_pack",
                "capacity_kwh",
            ),
            (
                ["racking", "panel_count"],
                "SolarBatteryDesign__solar_battery_plant__site_infra",
                "SolarBatteryDesign__solar_battery_plant__site_infra__racking",
                "panel_count",
            ),
        ],
        ids=["pv_module.wattage", "battery_pack.capacity_kwh", "racking.panel_count"],
    )
    def test_deep_path_specific_cases(
        self, target_path, owning_part_qn, expected_parent, expected_leaf,
    ):
        """Specific deep-path override produces correct (full_parent, leaf) key."""
        override = _make_override(
            owning_part_qn=owning_part_qn,
            attribute_name=target_path[-1],
            literal_value=1.0,
            target_path=target_path,
            is_deep_path=True,
        )
        index = _build_override_index([override])
        assert (expected_parent, expected_leaf) in index

    def test_flat_override_key_format(self):
        """Flat (non-deep-path) override uses owning_part_qn directly as full_parent."""
        # Use a real owning_part_qn from the solar_battery fixture
        override = _make_override(
            owning_part_qn="SolarBatteryDesign__solar_battery_plant__solar_array",
            attribute_name="efficiency",
            literal_value=0.22,
            target_path=["efficiency"],
            is_deep_path=False,
        )
        index = _build_override_index([override])
        expected_key = ("SolarBatteryDesign__solar_battery_plant__solar_array", "efficiency")
        assert expected_key in index
        # Verify no intermediate segment was joined
        full_parent = expected_key[0]
        assert full_parent == override.owning_part_qn


# ---------------------------------------------------------------------------
# REQ-VBR-03: LITERAL override mutations
# ---------------------------------------------------------------------------


@pytest.mark.req("REQ-VBR-03")
class TestLiteralOverrideMutation:
    """REQ-VBR-03: LITERAL override sets binding_type, copies literal_value, clears source_path."""

    def test_literal_override_single(self, solar_battery_snapshot):
        """Reconstruct one pre-rewrite binding and verify LITERAL mutation."""
        hierarchy = solar_battery_snapshot["hierarchy_data"]
        calc_usages = copy.deepcopy(solar_battery_snapshot["calc_usages"])

        # Reconstruct only the wattage override for pv_module
        restored = _reconstruct_pre_rewrite_bindings(calc_usages, hierarchy.design_overrides)
        assert len(restored) == 13

        # Find the wattage binding
        wattage_entry = None
        for usage, binding, override in restored:
            if override.attribute_name == "wattage" and "pv_module" in usage.qualified_name:
                wattage_entry = (usage, binding, override)
                break
        assert wattage_entry is not None, "Should find wattage override for pv_module"

        usage, binding, override = wattage_entry
        # Verify pre-rewrite state
        assert binding.binding_type == BindingType.REFERENCE
        assert binding.source_path == "SolarBatteryLibrary::PV_Module::wattage"
        assert binding.literal_value is None

        # Apply rewrite
        count = _rewrite_virtual_bindings(calc_usages, hierarchy)
        assert count == 13

        # Verify post-rewrite state
        assert binding.binding_type == BindingType.LITERAL
        assert binding.literal_value == 400.0
        assert binding.source_path is None

    def test_literal_override_all_13(self, solar_battery_snapshot):
        """Reconstruct all 13 overrides, apply rewrite, verify all become LITERAL."""
        hierarchy = solar_battery_snapshot["hierarchy_data"]
        calc_usages = copy.deepcopy(solar_battery_snapshot["calc_usages"])

        restored = _reconstruct_pre_rewrite_bindings(calc_usages, hierarchy.design_overrides)
        assert len(restored) == 13

        count = _rewrite_virtual_bindings(calc_usages, hierarchy)
        assert count == 13

        for usage, binding, override in restored:
            assert binding.binding_type == BindingType.LITERAL, (
                f"Binding {binding.param_name} on {usage.qualified_name} should be LITERAL"
            )
            assert binding.literal_value == override.literal_value, (
                f"Binding {binding.param_name}: "
                f"expected {override.literal_value}, got {binding.literal_value}"
            )
            assert binding.source_path is None, (
                f"Binding {binding.param_name} should have source_path=None"
            )

    @pytest.mark.parametrize(
        "override_idx, expected_value",
        [
            (0, 400.0),    # pv_module.wattage
            (1, 0.21),     # pv_module.efficiency
            (2, 2000.0),   # inverter.power_rating
            (3, 4.0),      # array_bos.string_count
            (4, 20.0),     # array_bos.panel_count
            (5, 5.0),      # battery_pack.capacity_kwh
            (6, 1.0),      # battery_pack.chemistry_factor
            (7, 10000.0),  # hybrid_inverter.power_rating
            (8, 8.0),      # battery_bos.pack_count
            (9, 20.0),     # racking.panel_count
            (10, 30.0),    # racking.tilt_angle
            (11, 4.0),     # electrical_panel.circuit_count
            (12, 8.0),     # permitting.system_capacity_kw
        ],
        ids=[
            "pv_module.wattage=400",
            "pv_module.efficiency=0.21",
            "inverter.power_rating=2000",
            "array_bos.string_count=4",
            "array_bos.panel_count=20",
            "battery_pack.capacity_kwh=5",
            "battery_pack.chemistry_factor=1",
            "hybrid_inverter.power_rating=10000",
            "battery_bos.pack_count=8",
            "racking.panel_count=20",
            "racking.tilt_angle=30",
            "electrical_panel.circuit_count=4",
            "permitting.system_capacity_kw=8",
        ],
    )
    def test_literal_override_parametrized(
        self, solar_battery_snapshot, override_idx, expected_value,
    ):
        """Each of the 13 overrides produces the correct literal_value after rewrite."""
        hierarchy = solar_battery_snapshot["hierarchy_data"]
        calc_usages = copy.deepcopy(solar_battery_snapshot["calc_usages"])

        restored = _reconstruct_pre_rewrite_bindings(calc_usages, hierarchy.design_overrides)
        override = hierarchy.design_overrides[override_idx]

        _rewrite_virtual_bindings(calc_usages, hierarchy)

        # Find the binding that was restored for this override
        for _usage, binding, ov in restored:
            if ov is override:
                assert binding.binding_type == BindingType.LITERAL
                assert binding.literal_value == expected_value
                assert binding.source_path is None
                return

        pytest.fail(
            f"Override index {override_idx} ({override.attribute_name}) "
            "not found in restored bindings"
        )


# ---------------------------------------------------------------------------
# REQ-VBR-04: CHAIN override replaces source_path
# ---------------------------------------------------------------------------


@pytest.mark.req("REQ-VBR-04")
class TestChainOverride:
    """REQ-VBR-04: CHAIN override SHALL replace source_path with redefinition's source_path."""

    def test_chain_override_replaces_source_path(self):
        """CHAIN override replaces source_path, binding_type stays REFERENCE."""
        # Construct using real names from solar_battery
        chain_override = _make_override(
            owning_part_qn="SolarBatteryDesign__solar_battery_plant__solar_array",
            attribute_name="efficiency",
            redefinition_type=RedefinitionType.CHAIN,
            source_path="tracker.eta",
            target_path=["pv_module", "efficiency"],
            is_deep_path=True,
        )
        hierarchy = _make_hierarchy_data([chain_override])

        binding = _make_binding(
            param_name="efficiency",
            source_path="SolarBatteryLibrary::PV_Module::efficiency",
            binding_type=BindingType.REFERENCE,
        )
        usage = _make_calc_usage(
            qualified_name="SolarBatteryDesign__solar_battery_plant__solar_array__pv_module__cost_model",
            bindings=[binding],
            owning_part_def_qn="SolarBatteryLibrary__PV_Module",
        )

        count = _rewrite_virtual_bindings([usage], hierarchy)

        assert count == 1
        assert binding.source_path == "tracker.eta"
        assert binding.binding_type == BindingType.REFERENCE  # unchanged
        assert binding.literal_value is None  # unchanged

    def test_chain_override_dotted_source_path(self):
        """CHAIN override with dotted source_path (e.g., 'cost_model.total_cost')."""
        chain_override = _make_override(
            owning_part_qn="SolarBatteryDesign__solar_battery_plant__solar_array",
            attribute_name="total_cost",
            redefinition_type=RedefinitionType.CHAIN,
            source_path="cost_model.total_cost",
            target_path=["pv_module", "total_cost"],
            is_deep_path=True,
        )
        hierarchy = _make_hierarchy_data([chain_override])

        binding = _make_binding(
            param_name="total_cost",
            source_path="SolarBatteryLibrary::PV_Module::total_cost",
        )
        usage = _make_calc_usage(
            qualified_name="SolarBatteryDesign__solar_battery_plant__solar_array__pv_module__some_calc",
            bindings=[binding],
            owning_part_def_qn="SolarBatteryLibrary__PV_Module",
        )

        count = _rewrite_virtual_bindings([usage], hierarchy)

        assert count == 1
        assert binding.source_path == "cost_model.total_cost"


# ---------------------------------------------------------------------------
# REQ-VBR-05: Template copies skipped
# ---------------------------------------------------------------------------


@pytest.mark.req("REQ-VBR-05")
class TestTemplateSkip:
    """REQ-VBR-05: Template copies (is_template=True) SHALL be skipped during rewriting."""

    def test_template_usage_not_rewritten(self):
        """Template CalcUsage with matching override is NOT mutated."""
        override = _make_override(
            owning_part_qn="SolarBatteryDesign__solar_battery_plant__solar_array",
            attribute_name="wattage",
            literal_value=400.0,
            target_path=["pv_module", "wattage"],
            is_deep_path=True,
        )
        hierarchy = _make_hierarchy_data([override])

        binding = _make_binding(
            param_name="wattage",
            source_path="SolarBatteryLibrary::PV_Module::wattage",
        )
        template_usage = _make_calc_usage(
            qualified_name="SolarBatteryDesign__solar_battery_plant__solar_array__pv_module__cost_model",
            bindings=[binding],
            is_template=True,
            owning_part_def_qn="SolarBatteryLibrary__PV_Module",
        )

        count = _rewrite_virtual_bindings([template_usage], hierarchy)

        assert count == 0
        assert binding.binding_type == BindingType.REFERENCE
        assert binding.source_path == "SolarBatteryLibrary::PV_Module::wattage"
        assert binding.literal_value is None

    def test_template_excluded_non_template_included(self):
        """Only non-template usages are rewritten when both exist."""
        override = _make_override(
            owning_part_qn="SolarBatteryDesign__solar_battery_plant__solar_array",
            attribute_name="wattage",
            literal_value=400.0,
            target_path=["pv_module", "wattage"],
            is_deep_path=True,
        )
        hierarchy = _make_hierarchy_data([override])

        template_binding = _make_binding(
            param_name="wattage",
            source_path="SolarBatteryLibrary::PV_Module::wattage",
        )
        template_usage = _make_calc_usage(
            qualified_name="SolarBatteryDesign__solar_battery_plant__solar_array__pv_module__cost_model",
            bindings=[template_binding],
            is_template=True,
            owning_part_def_qn="SolarBatteryLibrary__PV_Module",
        )

        virtual_binding = _make_binding(
            param_name="wattage",
            source_path="SolarBatteryLibrary::PV_Module::wattage",
        )
        virtual_usage = _make_calc_usage(
            qualified_name="SolarBatteryDesign__solar_battery_plant__solar_array__pv_module__cost_model",
            bindings=[virtual_binding],
            is_template=False,
            owning_part_def_qn="SolarBatteryLibrary__PV_Module",
        )

        count = _rewrite_virtual_bindings([template_usage, virtual_usage], hierarchy)

        assert count == 1
        # Template unchanged
        assert template_binding.binding_type == BindingType.REFERENCE
        assert template_binding.source_path == "SolarBatteryLibrary::PV_Module::wattage"
        # Virtual rewritten
        assert virtual_binding.binding_type == BindingType.LITERAL
        assert virtual_binding.literal_value == 400.0


# ---------------------------------------------------------------------------
# REQ-VBR-06: Already-LITERAL or no source_path skipped
# ---------------------------------------------------------------------------


@pytest.mark.req("REQ-VBR-06")
class TestSkipGuards:
    """REQ-VBR-06: Bindings already LITERAL or with no source_path SHALL be skipped."""

    def test_already_literal_skipped(self):
        """Binding already LITERAL is not double-rewritten."""
        override = _make_override(
            owning_part_qn="SolarBatteryDesign__solar_battery_plant__solar_array",
            attribute_name="wattage",
            literal_value=400.0,
            target_path=["pv_module", "wattage"],
            is_deep_path=True,
        )
        hierarchy = _make_hierarchy_data([override])

        binding = _make_binding(
            param_name="wattage",
            binding_type=BindingType.LITERAL,
            literal_value=999.0,  # Different value — should NOT be overwritten
            source_path=None,
        )
        usage = _make_calc_usage(
            qualified_name="SolarBatteryDesign__solar_battery_plant__solar_array__pv_module__cost_model",
            bindings=[binding],
            owning_part_def_qn="SolarBatteryLibrary__PV_Module",
        )

        count = _rewrite_virtual_bindings([usage], hierarchy)

        assert count == 0
        assert binding.binding_type == BindingType.LITERAL
        assert binding.literal_value == 999.0  # Unchanged

    def test_no_source_path_skipped(self):
        """Binding with source_path=None is skipped even if not LITERAL."""
        override = _make_override(
            owning_part_qn="SolarBatteryDesign__solar_battery_plant__solar_array",
            attribute_name="wattage",
            literal_value=400.0,
            target_path=["pv_module", "wattage"],
            is_deep_path=True,
        )
        hierarchy = _make_hierarchy_data([override])

        binding = _make_binding(
            param_name="wattage",
            binding_type=BindingType.UNBOUND,
            source_path=None,
        )
        usage = _make_calc_usage(
            qualified_name="SolarBatteryDesign__solar_battery_plant__solar_array__pv_module__cost_model",
            bindings=[binding],
            owning_part_def_qn="SolarBatteryLibrary__PV_Module",
        )

        count = _rewrite_virtual_bindings([usage], hierarchy)

        assert count == 0
        assert binding.binding_type == BindingType.UNBOUND

    def test_idempotency(self, solar_battery_snapshot):
        """Calling on already-rewritten snapshot data returns 0 (no rewrites)."""
        hierarchy = solar_battery_snapshot["hierarchy_data"]
        calc_usages = copy.deepcopy(solar_battery_snapshot["calc_usages"])

        count = _rewrite_virtual_bindings(calc_usages, hierarchy)
        assert count == 0


# ---------------------------------------------------------------------------
# REQ-VBR-07: Rewrite before downstream processing
# ---------------------------------------------------------------------------


@pytest.mark.req("REQ-VBR-07")
class TestRewriteOrdering:
    """REQ-VBR-07: Rewriting SHALL complete BEFORE any downstream processing."""

    def test_rewrite_called_before_downstream_in_build_pipeline_context(self):
        """Static analysis: _rewrite_virtual_bindings called before downstream steps."""
        from sysml_codegen.orchestration import pipeline_builder

        source = inspect.getsource(pipeline_builder)
        tree = ast.parse(source)

        # Find build_pipeline_context and extract call line numbers
        call_lines: dict[str, int] = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "build_pipeline_context":
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        if isinstance(child.func, ast.Name):
                            name = child.func.id
                            if name in (
                                "_extract_hierarchy_and_rewrite_bindings",
                                "extract_design_attributes",
                                "build_output_registry",
                                "build_computation_graph",
                            ):
                                call_lines[name] = child.lineno
                        elif isinstance(child.func, ast.Attribute):
                            if child.func.attr == "find_required_modules":
                                call_lines["find_required_modules"] = child.lineno

        assert "_extract_hierarchy_and_rewrite_bindings" in call_lines, (
            "_extract_hierarchy_and_rewrite_bindings not found in build_pipeline_context"
        )

        rewrite_line = call_lines["_extract_hierarchy_and_rewrite_bindings"]

        # Verify rewrite is before all downstream steps
        for step_name in ["extract_design_attributes", "build_output_registry",
                          "find_required_modules", "build_computation_graph"]:
            if step_name in call_lines:
                assert rewrite_line < call_lines[step_name], (
                    f"_extract_hierarchy_and_rewrite_bindings (line {rewrite_line}) "
                    f"should be before {step_name} (line {call_lines[step_name]})"
                )

    def test_rewrite_called_inside_hierarchy_extraction(self):
        """_rewrite_virtual_bindings called within _extract_hierarchy_and_rewrite_bindings."""
        from sysml_codegen.orchestration import pipeline_builder

        source = inspect.getsource(pipeline_builder)
        tree = ast.parse(source)

        target_fn = "_extract_hierarchy_and_rewrite_bindings"
        found = False
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == target_fn:
                for child in ast.walk(node):
                    if not isinstance(child, ast.Call):
                        continue
                    func = child.func
                    if (
                        isinstance(func, ast.Name)
                        and func.id == "_rewrite_virtual_bindings"
                    ):
                        found = True
                        break

        assert found, (
            f"_rewrite_virtual_bindings not called inside {target_fn}"
        )


# ---------------------------------------------------------------------------
# Leaf extraction tests (source_path parsing)
# ---------------------------------------------------------------------------


@pytest.mark.req("REQ-VBR-03")
class TestLeafExtraction:
    """Verify leaf name extraction from different source_path formats."""

    def test_sysml_qn_leaf_extraction(self):
        """SysML QN (:: separator): 'Lib::Solar_Array::wattage' → leaf 'wattage'."""
        override = _make_override(
            owning_part_qn="Design__part",
            attribute_name="wattage",
            literal_value=400.0,
            target_path=["sub", "wattage"],
            is_deep_path=True,
        )
        hierarchy = _make_hierarchy_data([override])

        binding = _make_binding(
            param_name="wattage",
            source_path="Lib::Solar_Array::wattage",
        )
        usage = _make_calc_usage(
            qualified_name="Design__part__sub__cost_model",
            bindings=[binding],
            owning_part_def_qn="Lib__Solar_Array",
        )

        count = _rewrite_virtual_bindings([usage], hierarchy)
        assert count == 1
        assert binding.binding_type == BindingType.LITERAL
        assert binding.literal_value == 400.0

    def test_dotted_leaf_extraction(self):
        """Dotted path (. separator): 'tracker.eta' → leaf 'eta'."""
        override = _make_override(
            owning_part_qn="Design__part",
            attribute_name="eta",
            literal_value=0.95,
            target_path=["sub", "eta"],
            is_deep_path=True,
        )
        hierarchy = _make_hierarchy_data([override])

        binding = _make_binding(
            param_name="eta",
            source_path="tracker.eta",
        )
        usage = _make_calc_usage(
            qualified_name="Design__part__sub__cost_model",
            bindings=[binding],
            owning_part_def_qn="Lib__Tracker",
        )

        count = _rewrite_virtual_bindings([usage], hierarchy)
        assert count == 1
        assert binding.binding_type == BindingType.LITERAL
        assert binding.literal_value == 0.95

    # test_bare_name_leaf_extraction removed — bare-name source_paths are dead code (7.4)


# ---------------------------------------------------------------------------
# EXPRESSION override not applied
# ---------------------------------------------------------------------------


@pytest.mark.req("REQ-VBR-03")
class TestExpressionOverrideSkipped:
    """EXPRESSION-type overrides are silently skipped (not handled by rewrite)."""

    def test_expression_override_not_applied(self):
        """EXPRESSION override in index does not mutate the binding."""
        expression_override = _make_override(
            owning_part_qn="Design__part",
            attribute_name="cost",
            redefinition_type=RedefinitionType.EXPRESSION,
            target_path=["sub", "cost"],
            is_deep_path=True,
        )
        hierarchy = _make_hierarchy_data([expression_override])

        binding = _make_binding(
            param_name="cost",
            source_path="Lib::Part::cost",
        )
        usage = _make_calc_usage(
            qualified_name="Design__part__sub__cost_model",
            bindings=[binding],
            owning_part_def_qn="Lib__Part",
        )

        count = _rewrite_virtual_bindings([usage], hierarchy)

        assert count == 0
        assert binding.binding_type == BindingType.REFERENCE
        assert binding.source_path == "Lib::Part::cost"


# ---------------------------------------------------------------------------
# Rewrite count validation
# ---------------------------------------------------------------------------


@pytest.mark.req("REQ-VBR-03")
class TestRewriteCount:
    """Verify return value matches the number of mutations performed."""

    def test_rewrite_count_matches_mutations(self, solar_battery_snapshot):
        """Reconstruct all 13 overrides; verify return value == 13."""
        hierarchy = solar_battery_snapshot["hierarchy_data"]
        calc_usages = copy.deepcopy(solar_battery_snapshot["calc_usages"])

        restored = _reconstruct_pre_rewrite_bindings(calc_usages, hierarchy.design_overrides)
        assert len(restored) == 13

        count = _rewrite_virtual_bindings(calc_usages, hierarchy)
        assert count == 13

    def test_mixed_literal_and_chain_count(self):
        """Count includes both LITERAL and CHAIN rewrites."""
        literal_override = _make_override(
            owning_part_qn="Design__part",
            attribute_name="wattage",
            redefinition_type=RedefinitionType.LITERAL,
            literal_value=400.0,
            target_path=["sub", "wattage"],
            is_deep_path=True,
        )
        chain_override = _make_override(
            owning_part_qn="Design__part",
            attribute_name="eta",
            redefinition_type=RedefinitionType.CHAIN,
            source_path="tracker.eta",
            target_path=["sub", "eta"],
            is_deep_path=True,
        )
        hierarchy = _make_hierarchy_data([literal_override, chain_override])

        binding1 = _make_binding(param_name="wattage", source_path="Lib::Part::wattage")
        binding2 = _make_binding(param_name="eta", source_path="Lib::Part::eta")
        usage = _make_calc_usage(
            qualified_name="Design__part__sub__cost_model",
            bindings=[binding1, binding2],
            owning_part_def_qn="Lib__Part",
        )

        count = _rewrite_virtual_bindings([usage], hierarchy)

        assert count == 2
        assert binding1.binding_type == BindingType.LITERAL
        assert binding2.source_path == "tracker.eta"


# ---------------------------------------------------------------------------
# CHAIN override fixture coverage (C2 gap closure)
# Uses chain_override_probe fixture — real SysML data with CHAIN design override.
# ---------------------------------------------------------------------------


@pytest.mark.req("REQ-VBR-04")
@pytest.mark.req("REQ-HR-08")
class TestChainOverrideFixtureCoverage:
    """CHAIN design override with real SysML fixture data (closes C2 gap).

    Also pins REQ-HR-08's "`part redefines` keeps all RHS types" leg: this
    fixture's CHAIN override (RHS type CHAIN, not LITERAL) is scanned and kept
    on a `part redefines` usage, unlike the plain-usage LITERAL-only gate.

    The chain_override_probe fixture has:
    - 1 LITERAL override: :>> base_cost = 100.0
    - 1 CHAIN override: :>> sensitivity = calibration.calibrated_factor
    Both are flat (not deep-path) overrides on the sensor PartUsage.
    """

    def test_chain_override_present_in_fixture(self, chain_override_snapshot):
        """chain_override_probe has at least one CHAIN design override."""
        overrides = chain_override_snapshot["hierarchy_data"].design_overrides
        chain_overrides = [
            o for o in overrides
            if o.redefinition_type == RedefinitionType.CHAIN
        ]
        assert len(chain_overrides) >= 1, (
            f"Expected at least 1 CHAIN override, found {len(chain_overrides)}"
        )

    def test_chain_override_has_source_path(self, chain_override_snapshot):
        """CHAIN override has non-None source_path (calibration.calibrated_factor)."""
        overrides = chain_override_snapshot["hierarchy_data"].design_overrides
        chain_overrides = [
            o for o in overrides
            if o.redefinition_type == RedefinitionType.CHAIN
        ]
        for o in chain_overrides:
            assert o.source_path is not None and o.source_path != "", (
                f"CHAIN override {o.attribute_name} has empty source_path"
            )

    def test_chain_override_sensitivity_redirected(self, chain_override_snapshot):
        """sensitivity binding source_path is redirected to calibration.calibrated_factor."""
        overrides = chain_override_snapshot["hierarchy_data"].design_overrides
        sensitivity_override = next(
            (o for o in overrides if o.attribute_name == "sensitivity"), None
        )
        assert sensitivity_override is not None, "sensitivity override not found"
        assert sensitivity_override.redefinition_type == RedefinitionType.CHAIN
        assert sensitivity_override.source_path == "calibration.calibrated_factor"

    def test_literal_override_also_present(self, chain_override_snapshot):
        """chain_override_probe has both LITERAL and CHAIN overrides."""
        overrides = chain_override_snapshot["hierarchy_data"].design_overrides
        types = {o.redefinition_type for o in overrides}
        assert RedefinitionType.LITERAL in types, "Missing LITERAL override"
        assert RedefinitionType.CHAIN in types, "Missing CHAIN override"

    def test_override_count(self, chain_override_snapshot):
        """chain_override_probe has exactly 2 design overrides (1 LITERAL + 1 CHAIN)."""
        overrides = chain_override_snapshot["hierarchy_data"].design_overrides
        assert len(overrides) == 2, (
            f"Expected 2 design overrides, got {len(overrides)}"
        )

    def test_vbr_applies_chain_override_to_real_binding(self, chain_override_snapshot):
        """VBR applies CHAIN override on real fixture data, changing source_path."""
        hierarchy = chain_override_snapshot["hierarchy_data"]
        calc_usages = copy.deepcopy(chain_override_snapshot["calc_usages"])

        # Find the sensor cost_model CalcUsage
        cost_model = next(
            (u for u in calc_usages if "cost_model" in u.instance_name),
            None,
        )
        assert cost_model is not None, "cost_model CalcUsage not found"

        # Snapshot is post-rewrite. The sensitivity binding should already be redirected.
        sensitivity = next(
            (b for b in cost_model.bindings if b.param_name == "sensitivity"), None
        )
        assert sensitivity is not None, "sensitivity binding not found"

        # Post-rewrite: source_path should be the CHAIN target
        assert sensitivity.source_path == "calibration.calibrated_factor", (
            f"Expected source_path='calibration.calibrated_factor', "
            f"got {sensitivity.source_path!r}"
        )

    def test_vbr_applies_literal_override_to_real_binding(self, chain_override_snapshot):
        """VBR applies LITERAL override on real fixture data, setting literal_value."""
        calc_usages = chain_override_snapshot["calc_usages"]

        cost_model = next(
            (u for u in calc_usages if "cost_model" in u.instance_name), None
        )
        assert cost_model is not None

        base_cost = next(
            (b for b in cost_model.bindings if b.param_name == "base_cost"), None
        )
        assert base_cost is not None, "base_cost binding not found"
        assert base_cost.binding_type == BindingType.LITERAL
        assert base_cost.literal_value == 100.0
        assert base_cost.source_path is None

    def test_chain_override_is_flat_not_deep(self, chain_override_snapshot):
        """chain_override_probe overrides are flat (not deep-path)."""
        overrides = chain_override_snapshot["hierarchy_data"].design_overrides
        for o in overrides:
            assert o.is_deep_path is False, (
                f"Override {o.attribute_name} is_deep_path={o.is_deep_path}, "
                f"expected False"
            )

    def test_chain_override_across_all_models(self, extraction_snapshots):
        """With chain_override_probe, CHAIN design overrides now have fixture coverage."""
        has_chain_override = False
        for model_name, snapshot in extraction_snapshots.items():
            for o in snapshot["hierarchy_data"].design_overrides:
                if o.redefinition_type == RedefinitionType.CHAIN:
                    has_chain_override = True
                    break
            if has_chain_override:
                break
        assert has_chain_override, (
            "No CHAIN design override found across any fixture model"
        )
