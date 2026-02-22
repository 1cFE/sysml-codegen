"""Unit tests for template CalcUsage detection and virtual instantiation.

Tests use mock AST elements — no real SysML models required. Mock class names
include the SysML type name so SysideAdapter.is_instance() fallback works
(type_name in type(elem).__name__).

Test Suites:
1. Template Detection — is_template classification in _extract_single_usage()
2. Part Usage Index — _build_part_usage_index() mapping
3. Instantiation Paths — _find_instantiation_paths() recursive resolution
4. Virtual CalcUsage Generation — _create_virtual_calc_usage() field assembly
5. Integration — expand_templates flag in extract_calculation_usages()
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from sysml_codegen.extraction.usage_extractor import (
    BindingInfo,
    CalcUsageData,
    _extract_single_usage,
    _build_part_usage_index,
    _find_instantiation_paths,
    _create_virtual_calc_usage,
    _expand_template_calc_usages,
    extract_calculation_usages,
)
from sysml_codegen.core.qualified_names import build_element_qualified_name
from agentic_mbse.sysml.types import BindingType


# ---------------------------------------------------------------------------
# Mock AST Elements
# ---------------------------------------------------------------------------


class MockPartDefinition:
    """Mock PartDefinition — is_instance(x, "PartDefinition") matches."""

    def __init__(self, name: str = "TestPartDef", owner=None):
        self.name = name
        self.owner = owner


class MockPartUsage:
    """Mock PartUsage — is_instance(x, "PartUsage") matches."""

    def __init__(
        self,
        name: str = "test_usage",
        owning_type=None,
        types=None,
        owner=None,
    ):
        self.name = name
        self.owning_type = owning_type
        self.types = types or []
        self.owner = owner


class MockOwnerMembership:
    """Mock ownership membership node (owner → owning_related_element)."""

    def __init__(self, owning_related_element=None, owner=None, name=None):
        self.owning_related_element = owning_related_element
        self.owner = owner
        self.name = name


class MockPackage:
    """Mock Package element — neither PartDefinition nor PartUsage."""

    def __init__(self, name: str = "TestPkg", owner=None):
        self.name = name
        self.owner = owner


class MockCalculationUsage:
    """Mock CalculationUsage element for _extract_single_usage()."""

    def __init__(
        self,
        name: str = "cost_model",
        owning_type=None,
        calc_def_name: str = "CostCalc",
        owned_members=None,
        owner=None,
        direction=None,
    ):
        self.name = name
        self.owning_type = owning_type
        self.owned_members = owned_members or []
        self.owner = owner
        # For get_calc_def_name() resolution
        self._calc_def_name = calc_def_name


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_calc_def_stub(name: str, qualified_name: str | None = None):
    """Create a minimal calc def object for calc_def_map."""

    class _Stub:
        pass

    s = _Stub()
    s.name = name
    s.qualified_name = qualified_name or name
    s.input_attributes = []
    return s


def _make_calc_usage_elem(
    name: str = "cost_model",
    owning_type_class: str = "PartDefinition",
    owning_type_name: str = "PV_Module",
    calc_def_name: str = "CostCalc",
) -> MockCalculationUsage:
    """Build a MockCalculationUsage with the specified owning type.

    The owning_type is set as the element's owning_type attribute AND wired
    into the ownership chain so build_element_qualified_name() can traverse it.
    """
    if owning_type_class == "PartDefinition":
        owning = MockPartDefinition(name=owning_type_name)
    elif owning_type_class == "PartUsage":
        owning = MockPartUsage(name=owning_type_name)
    else:
        owning = MockPackage(name=owning_type_name)

    # Wire ownership chain: elem.owner.owning_related_element = owning_type
    membership = MockOwnerMembership(owning_related_element=owning)
    elem = MockCalculationUsage(
        name=name,
        owning_type=owning,
        calc_def_name=calc_def_name,
        owner=membership,
    )
    return elem


# ---------------------------------------------------------------------------
# Test Suite 1: Template Detection
# ---------------------------------------------------------------------------


class TestTemplateDetection:
    """Template detection in _extract_single_usage()."""

    @pytest.fixture(autouse=True)
    def _patch_helpers(self):
        """Patch external helpers so _extract_single_usage() works with mocks."""
        with (
            patch(
                "sysml_codegen.extraction.usage_extractor.get_calc_def_name",
                side_effect=lambda elem: getattr(elem, "_calc_def_name", "UnknownCalc"),
            ),
            patch(
                "sysml_codegen.extraction.usage_extractor.get_source_location",
                return_value=(Path("test.sysml"), 1),
            ),
        ):
            yield

    def _extract(self, elem, calc_def_name: str = "CostCalc") -> CalcUsageData | None:
        """Call _extract_single_usage with standard test scaffolding."""
        calc_def = _make_calc_def_stub(calc_def_name)
        warnings: list[str] = []
        return _extract_single_usage(
            elem,
            known_calc_defs={calc_def_name},
            warnings=warnings,
            calc_def_map={calc_def_name: calc_def},
        )

    def test_calc_in_part_def_is_template(self):
        """CalcUsage owned by PartDefinition → is_template=True."""
        elem = _make_calc_usage_elem(owning_type_class="PartDefinition")
        usage = self._extract(elem)
        assert usage is not None
        assert usage.is_template is True

    def test_calc_in_part_usage_is_concrete(self):
        """CalcUsage owned by PartUsage → is_template=False."""
        elem = _make_calc_usage_elem(owning_type_class="PartUsage")
        usage = self._extract(elem)
        assert usage is not None
        assert usage.is_template is False

    def test_calc_with_no_owning_type_is_concrete(self):
        """CalcUsage without owning_type → is_template=False."""
        elem = _make_calc_usage_elem(owning_type_class="Package")
        # Remove owning_type entirely
        elem.owning_type = None
        usage = self._extract(elem)
        assert usage is not None
        assert usage.is_template is False

    def test_owning_part_def_qn_set_for_template(self):
        """Template CalcUsage has owning_part_def_qn matching the PartDef QN."""
        elem = _make_calc_usage_elem(
            owning_type_class="PartDefinition",
            owning_type_name="PV_Module",
        )
        usage = self._extract(elem)
        assert usage is not None
        assert usage.owning_part_def_qn is not None
        # build_element_qualified_name on the MockPartDefinition will produce
        # the sanitized name. The exact value depends on the mock's ownership
        # chain, but it must contain "PV_Module".
        assert "PV_Module" in usage.owning_part_def_qn

    def test_raw_element_stored(self):
        """raw_element stores the original AST element."""
        elem = _make_calc_usage_elem(owning_type_class="PartDefinition")
        usage = self._extract(elem)
        assert usage is not None
        assert usage.raw_element is elem

    def test_concrete_usage_has_none_owning_part_def_qn(self):
        """Concrete CalcUsage has owning_part_def_qn=None."""
        elem = _make_calc_usage_elem(owning_type_class="PartUsage")
        usage = self._extract(elem)
        assert usage is not None
        assert usage.owning_part_def_qn is None


# ---------------------------------------------------------------------------
# Mock hierarchy builders for Phase 2-3 tests
# ---------------------------------------------------------------------------


def _wire_ownership(child, parent):
    """Wire child.owner → MockOwnerMembership → parent (standard AST chain)."""
    membership = MockOwnerMembership(owning_related_element=parent)
    child.owner = membership
    return child


def _build_mock_hierarchy():
    """Build a solar_battery-style mock hierarchy for index/path tests.

    Hierarchy (3 levels):
        Package "SolarBatteryDesign"
          └─ PartUsage "solar_battery_plant" types PartDef "Solar_Battery_Plant"
               └─ (in PartDef "Solar_Battery_Plant"):
                    PartUsage "solar_array" types PartDef "Solar_Array"
                      └─ (in PartDef "Solar_Array"):
                           PartUsage "pv_module" types PartDef "PV_Module"

    Returns (part_defs, part_usages, package) for building mock model.
    """
    # Package (top-level)
    pkg = MockPackage(name="SolarBatteryDesign")

    # PartDefinitions
    pv_module_def = MockPartDefinition(name="PV_Module")
    solar_array_def = MockPartDefinition(name="Solar_Array")
    plant_def = MockPartDefinition(name="Solar_Battery_Plant")

    # PartUsages — wire types and ownership
    # pv_module lives inside Solar_Array PartDef
    pv_module_usage = MockPartUsage(
        name="pv_module",
        owning_type=solar_array_def,
        types=[pv_module_def],
    )
    _wire_ownership(pv_module_usage, solar_array_def)

    # solar_array lives inside Solar_Battery_Plant PartDef
    solar_array_usage = MockPartUsage(
        name="solar_array",
        owning_type=plant_def,
        types=[solar_array_def],
    )
    _wire_ownership(solar_array_usage, plant_def)

    # solar_battery_plant lives inside Package (top-level concrete usage)
    plant_usage = MockPartUsage(
        name="solar_battery_plant",
        owning_type=pkg,
        types=[plant_def],
    )
    _wire_ownership(plant_usage, pkg)

    return {
        "part_defs": {
            "PV_Module": pv_module_def,
            "Solar_Array": solar_array_def,
            "Solar_Battery_Plant": plant_def,
        },
        "part_usages": [pv_module_usage, solar_array_usage, plant_usage],
        "package": pkg,
    }


def _mock_elements_of_type(part_usages):
    """Create a mock for SysideAdapter.elements_of_type that returns PartUsages."""

    def _elements(model, type_name):
        if type_name == "PartUsage":
            return part_usages
        return []

    return _elements


# ---------------------------------------------------------------------------
# Test Suite 2: Part Usage Index
# ---------------------------------------------------------------------------


class TestPartUsageIndex:
    """Part usage index builder tests."""

    def test_index_maps_part_def_to_usages(self):
        """PartUsages typing same PartDef → both indexed under that QN."""
        hierarchy = _build_mock_hierarchy()
        with patch(
            "sysml_codegen.extraction.usage_extractor.SysideAdapter.elements_of_type",
            side_effect=_mock_elements_of_type(hierarchy["part_usages"]),
        ):
            index = _build_part_usage_index("mock_model")
        # Each PartDef should have exactly one PartUsage in our mock
        pv_qn = build_element_qualified_name(hierarchy["part_defs"]["PV_Module"])
        assert pv_qn in index
        assert len(index[pv_qn]) == 1

    def test_index_maps_multiple_usages_of_same_def(self):
        """Two PartUsages typing same PartDef → both in index list."""
        part_def = MockPartDefinition(name="Widget")
        usage_a = MockPartUsage(name="widget_a", types=[part_def])
        _wire_ownership(usage_a, MockPackage(name="Pkg"))
        usage_b = MockPartUsage(name="widget_b", types=[part_def])
        _wire_ownership(usage_b, MockPackage(name="Pkg"))

        with patch(
            "sysml_codegen.extraction.usage_extractor.SysideAdapter.elements_of_type",
            side_effect=_mock_elements_of_type([usage_a, usage_b]),
        ):
            index = _build_part_usage_index("mock_model")
        widget_qn = build_element_qualified_name(part_def)
        assert len(index[widget_qn]) == 2

    def test_index_empty_types_skipped(self):
        """PartUsage with empty .types → not indexed."""
        usage = MockPartUsage(name="orphan", types=[])
        _wire_ownership(usage, MockPackage(name="Pkg"))

        with patch(
            "sysml_codegen.extraction.usage_extractor.SysideAdapter.elements_of_type",
            side_effect=_mock_elements_of_type([usage]),
        ):
            index = _build_part_usage_index("mock_model")
        assert len(index) == 0


# ---------------------------------------------------------------------------
# Test Suite 3: Instantiation Path Resolution
# ---------------------------------------------------------------------------


class TestInstantiationPaths:
    """Recursive path resolution tests."""

    def test_single_level_path(self):
        """PartUsage directly in Package → path from build_element_qualified_name."""
        hierarchy = _build_mock_hierarchy()
        with patch(
            "sysml_codegen.extraction.usage_extractor.SysideAdapter.elements_of_type",
            side_effect=_mock_elements_of_type(hierarchy["part_usages"]),
        ):
            index = _build_part_usage_index("mock_model")

        plant_def_qn = build_element_qualified_name(
            hierarchy["part_defs"]["Solar_Battery_Plant"]
        )
        paths = _find_instantiation_paths(plant_def_qn, index)
        assert len(paths) == 1
        assert paths[0] == "SolarBatteryDesign__solar_battery_plant"

    def test_two_level_path(self):
        """PartUsage in PartDef → composed path through parent."""
        hierarchy = _build_mock_hierarchy()
        with patch(
            "sysml_codegen.extraction.usage_extractor.SysideAdapter.elements_of_type",
            side_effect=_mock_elements_of_type(hierarchy["part_usages"]),
        ):
            index = _build_part_usage_index("mock_model")

        array_def_qn = build_element_qualified_name(
            hierarchy["part_defs"]["Solar_Array"]
        )
        paths = _find_instantiation_paths(array_def_qn, index)
        assert len(paths) == 1
        assert paths[0] == "SolarBatteryDesign__solar_battery_plant__solar_array"

    def test_three_level_path(self):
        """Full 3-level chain: Pkg → plant → array → module."""
        hierarchy = _build_mock_hierarchy()
        with patch(
            "sysml_codegen.extraction.usage_extractor.SysideAdapter.elements_of_type",
            side_effect=_mock_elements_of_type(hierarchy["part_usages"]),
        ):
            index = _build_part_usage_index("mock_model")

        pv_def_qn = build_element_qualified_name(
            hierarchy["part_defs"]["PV_Module"]
        )
        paths = _find_instantiation_paths(pv_def_qn, index)
        assert len(paths) == 1
        assert (
            paths[0]
            == "SolarBatteryDesign__solar_battery_plant__solar_array__pv_module"
        )

    def test_deduplication(self):
        """Library + design PartUsages resolving to same path → deduplicated."""
        pkg = MockPackage(name="Pkg")
        part_def = MockPartDefinition(name="Widget")

        # Two PartUsages that will produce the same qualified path
        # (simulates library + part redefines scenario)
        usage_lib = MockPartUsage(name="widget", types=[part_def])
        _wire_ownership(usage_lib, pkg)
        usage_design = MockPartUsage(name="widget", types=[part_def])
        _wire_ownership(usage_design, pkg)

        with patch(
            "sysml_codegen.extraction.usage_extractor.SysideAdapter.elements_of_type",
            side_effect=_mock_elements_of_type([usage_lib, usage_design]),
        ):
            index = _build_part_usage_index("mock_model")

        widget_qn = build_element_qualified_name(part_def)
        paths = _find_instantiation_paths(widget_qn, index)
        # Both resolve to "Pkg__widget" — should be deduplicated to 1
        assert len(paths) == 1
        assert paths[0] == "Pkg__widget"

    def test_no_instantiations_returns_empty(self):
        """PartDef with no PartUsages → empty list."""
        paths = _find_instantiation_paths("NonExistent__Def", {})
        assert paths == []


# ---------------------------------------------------------------------------
# Test Suite 4: Virtual CalcUsage Generation
# ---------------------------------------------------------------------------


class TestVirtualCalcUsageGeneration:
    """Virtual CalcUsage creation tests."""

    def _make_template(self, **kwargs) -> CalcUsageData:
        """Create a template CalcUsageData for testing."""
        defaults = dict(
            instance_name="cost_model",
            calc_def_name="CostCalc",
            calc_def_qualified_name="Lib__CostCalc",
            module_type="CostCalcModule",
            bindings=[
                BindingInfo(
                    param_name="wattage",
                    source_path="wattage",
                    binding_type=BindingType.REFERENCE,
                )
            ],
            unbound_params=["cost_per_watt"],
            source_file=Path("test.sysml"),
            source_line=42,
            parent_part_path="PV_Module",
            qualified_name="Lib__PV_Module__cost_model",
            is_template=True,
            owning_part_def_qn="Lib__PV_Module",
        )
        defaults.update(kwargs)
        return CalcUsageData(**defaults)

    def test_virtual_calc_qualified_name(self):
        """Virtual QN = instantiation_path__calc_name."""
        template = self._make_template()
        virtual = _create_virtual_calc_usage(
            template, "Pkg__plant__array__module"
        )
        assert virtual.qualified_name == "Pkg__plant__array__module__cost_model"

    def test_virtual_calc_instance_name_equals_qualified_name(self):
        """instance_name = qualified_name for uniqueness."""
        template = self._make_template()
        virtual = _create_virtual_calc_usage(
            template, "Pkg__plant__array__module"
        )
        assert virtual.instance_name == virtual.qualified_name

    def test_virtual_calc_bindings_copied(self):
        """Bindings from template are present in virtual."""
        template = self._make_template()
        virtual = _create_virtual_calc_usage(
            template, "Pkg__plant__array__module"
        )
        assert len(virtual.bindings) == 1
        assert virtual.bindings[0].param_name == "wattage"

    def test_virtual_calc_unbound_params_copied(self):
        """Unbound params from template are copied."""
        template = self._make_template()
        virtual = _create_virtual_calc_usage(
            template, "Pkg__plant__array__module"
        )
        assert virtual.unbound_params == ["cost_per_watt"]

    def test_virtual_calc_is_not_template(self):
        """Virtual instance has is_template=False but preserves owning_part_def_qn."""
        template = self._make_template()
        virtual = _create_virtual_calc_usage(
            template, "Pkg__plant__array__module"
        )
        assert virtual.is_template is False
        assert virtual.owning_part_def_qn == template.owning_part_def_qn

    def test_virtual_calc_parent_part_path(self):
        """parent_part_path is dot-separated from instantiation path segments."""
        template = self._make_template()
        virtual = _create_virtual_calc_usage(
            template, "Pkg__plant__array__module"
        )
        # Skip first segment (package name), join remaining with dots
        assert virtual.parent_part_path == "plant.array.module"

    def test_virtual_preserves_source_info(self):
        """source_file and source_line copied from template."""
        template = self._make_template()
        virtual = _create_virtual_calc_usage(
            template, "Pkg__plant__array__module"
        )
        assert virtual.source_file == Path("test.sysml")
        assert virtual.source_line == 42
        assert virtual.calc_def_name == "CostCalc"
        assert virtual.module_type == "CostCalcModule"

    def test_multiple_usages_produce_multiple_virtuals(self):
        """Two instantiation paths → two distinct virtual CalcUsages."""
        template = self._make_template()
        v1 = _create_virtual_calc_usage(template, "Pkg__plant__array_a__module")
        v2 = _create_virtual_calc_usage(template, "Pkg__plant__array_b__module")
        assert v1.qualified_name != v2.qualified_name
        assert "array_a" in v1.qualified_name
        assert "array_b" in v2.qualified_name


# ---------------------------------------------------------------------------
# Test Suite 5: Integration (expand_templates)
# ---------------------------------------------------------------------------


class TestTemplateExpansionIntegration:
    """End-to-end expand_templates tests."""

    def test_expand_replaces_templates_with_virtuals(self):
        """Templates removed, virtuals added when expanding."""
        hierarchy = _build_mock_hierarchy()

        # Template CalcUsage in PV_Module PartDef
        template = CalcUsageData(
            instance_name="cost_model",
            calc_def_name="CostCalc",
            calc_def_qualified_name="Lib__CostCalc",
            module_type="CostCalcModule",
            bindings=[],
            unbound_params=[],
            source_file=Path("test.sysml"),
            source_line=1,
            parent_part_path="PV_Module",
            qualified_name="Lib__PV_Module__cost_model",
            is_template=True,
            owning_part_def_qn=build_element_qualified_name(
                hierarchy["part_defs"]["PV_Module"]
            ),
        )
        # Concrete CalcUsage (should pass through)
        concrete = CalcUsageData(
            instance_name="energy_production",
            calc_def_name="EnergyCalc",
            calc_def_qualified_name="Lib__EnergyCalc",
            module_type="EnergyCalcModule",
            bindings=[],
            unbound_params=[],
            source_file=Path("test.sysml"),
            source_line=10,
            parent_part_path="solar_battery_plant",
            qualified_name="Design__solar_battery_plant__energy_production",
            is_template=False,
        )

        warnings: list[str] = []
        with patch(
            "sysml_codegen.extraction.usage_extractor.SysideAdapter.elements_of_type",
            side_effect=_mock_elements_of_type(hierarchy["part_usages"]),
        ):
            result = _expand_template_calc_usages(
                "mock_model", [template, concrete], warnings
            )

        # Concrete passes through
        concrete_results = [u for u in result if u.instance_name == "energy_production"]
        assert len(concrete_results) == 1

        # Template replaced by virtual
        template_results = [u for u in result if u.is_template]
        assert len(template_results) == 0

        virtual_results = [
            u for u in result if "cost_model" in u.qualified_name and not u.is_template
        ]
        assert len(virtual_results) == 1
        assert "pv_module__cost_model" in virtual_results[0].qualified_name

    def test_expand_false_preserves_templates(self):
        """expand_templates=False keeps templates — _expand is NOT called."""
        template = CalcUsageData(
            instance_name="cost_model",
            calc_def_name="CostCalc",
            calc_def_qualified_name="Lib__CostCalc",
            module_type="CostCalcModule",
            is_template=True,
            owning_part_def_qn="Lib__PV_Module",
        )
        mock_elem = MockCalculationUsage(name="cost_model")
        with (
            patch(
                "sysml_codegen.extraction.usage_extractor.SysideAdapter.elements_of_type",
                return_value=[mock_elem],
            ),
            patch(
                "sysml_codegen.extraction.usage_extractor._extract_single_usage",
                return_value=template,
            ),
            patch(
                "sysml_codegen.extraction.usage_extractor._expand_template_calc_usages",
            ) as mock_expand,
        ):
            usages, report = extract_calculation_usages(
                "mock_model", expand_templates=False
            )
        mock_expand.assert_not_called()
        assert len(usages) == 1
        assert usages[0].is_template is True
        assert usages[0].instance_name == "cost_model"

    def test_concrete_usages_unchanged(self):
        """Non-template CalcUsages pass through unmodified."""
        concrete = CalcUsageData(
            instance_name="energy_production",
            calc_def_name="EnergyCalc",
            calc_def_qualified_name="Lib__EnergyCalc",
            module_type="EnergyCalcModule",
            is_template=False,
        )
        warnings: list[str] = []
        with patch(
            "sysml_codegen.extraction.usage_extractor.SysideAdapter.elements_of_type",
            side_effect=_mock_elements_of_type([]),
        ):
            result = _expand_template_calc_usages(
                "mock_model", [concrete], warnings
            )
        assert len(result) == 1
        assert result[0] is concrete

    def test_warning_on_no_instantiations(self):
        """Template with no PartUsages emits warning and is dropped."""
        template = CalcUsageData(
            instance_name="orphan_calc",
            calc_def_name="OrphanCalc",
            calc_def_qualified_name="Lib__OrphanCalc",
            module_type="OrphanCalcModule",
            is_template=True,
            owning_part_def_qn="Lib__NonExistentPartDef",
        )
        warnings: list[str] = []
        with patch(
            "sysml_codegen.extraction.usage_extractor.SysideAdapter.elements_of_type",
            side_effect=_mock_elements_of_type([]),
        ):
            result = _expand_template_calc_usages(
                "mock_model", [template], warnings
            )
        assert len(result) == 0
        assert len(warnings) == 1
        assert "orphan_calc" in warnings[0]
