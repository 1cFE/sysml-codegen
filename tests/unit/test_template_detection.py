"""Unit tests for raw template CalcUsage detection.

Tests use mock AST elements — no real SysML models required. Mock class names
include the SysML type name so SysideAdapter.is_instance() fallback works
(type_name in type(elem).__name__).

The exact elaborator owns effective occurrence expansion. These tests retain only
the route-neutral extraction fact that a declaration is owned by a PartDefinition.
"""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from sysml_codegen.extraction.usage_extractor import (
    CalcUsageData,
    _extract_single_usage,
)

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
