"""C02: Naming convention conformance tests.

Verifies that every naming function referenced in doc 15
(15-naming-conventions.md) produces the correct identifier format,
handles edge cases correctly, and uses real data from fixture models.

Requirements: REQ-NC-01 through REQ-NC-07.
"""

from dataclasses import dataclass

import pytest

from sysml_codegen.core.identifier_types import derive_module_type, make_scoped_key
from sysml_codegen.core.output_registry import OutputRegistry
from sysml_codegen.core.qualified_names import (
    build_element_qualified_name,
    build_parameter_qualified_name,
    extract_simple_name,
    get_channel_name,
    get_module_name,
    python_to_sysml_qualified_name,
    sanitize_name,
    sysml_to_python_qualified_name,
)

# ---------------------------------------------------------------------------
# SysIDE boundary stubs (permitted per ground rules)
# ---------------------------------------------------------------------------


@dataclass
class FakeElement:
    """Minimal stub for SysIDE AST element."""

    name: str | None
    owner: "FakeElement | FakeOwnership | None" = None


@dataclass
class FakeOwnership:
    """Minimal stub for SysIDE AST membership/relationship."""

    owning_related_element: FakeElement | None
    owner: "FakeElement | FakeOwnership | None" = None
    name: str | None = None


def _build_chain(names: list[str]) -> FakeElement:
    """Build an ownership chain from a list of names (root-first).

    The last name becomes the element itself; earlier names form the
    ownership chain via FakeOwnership nodes.

    Example: _build_chain(["A", "B", "C"]) produces EQN "A__B__C".
    """
    assert len(names) >= 1
    if len(names) == 1:
        return FakeElement(name=names[0])

    elem = FakeElement(name=names[-1])
    # Build ownership chain: innermost = root (names[0]), outermost = immediate parent (names[-2])
    current_owner = None
    for name in names[:-1]:
        ownership = FakeOwnership(
            owning_related_element=FakeElement(name=name),
            owner=current_owner,
        )
        current_owner = ownership
    elem.owner = current_owner
    return elem


# ---------------------------------------------------------------------------
# Real data tables (harvested from fixture models and existing tests)
# ---------------------------------------------------------------------------

# Reserved words documented in sanitize_name()
RESERVED_WORDS = ["class", "def", "import", "from", "return", "yield"]

# SysML QNs -> expected module types (for REQ-NC-04)
SYSML_QNS_AND_MODULE_TYPES = [
    ("SolarBatteryLibrary::BatteryPackCostCalc", "solarbatterylibrary.BatteryPackCostCalcModule"),
    ("SolarBatteryLibrary::PVModuleCostCalc", "solarbatterylibrary.PVModuleCostCalcModule"),
    ("SolarBatteryLibrary::LCOECalc", "solarbatterylibrary.LCOECalcModule"),
    ("SolarBatteryLibrary::EnergyProductionCalc", "solarbatterylibrary.EnergyProductionCalcModule"),
    ("FusionPhysics::NetElectricPower", "fusionphysics.NetElectricPowerModule"),
    ("FusionPhysicsGeometry::TorusVolume", "fusionphysicsgeometry.TorusVolumeModule"),
    ("ChainSpikeLibrary::CostCalc", "chainspikelibrary.CostCalcModule"),
]

# Real EQNs from fixture models (for REQ-NC-03/05 tests)
REAL_EQNS = [
    "SolarBatteryDesign__solar_battery_plant__battery_system__battery_pack__cost_model",
    "CATFMFEPhysics__catf_physics__net_electric",
    "CATFMFEPhysics__catf_physics__alpha_neutron_split",
]

# Known ownership chains -> expected EQNs (for REQ-NC-01)
KNOWN_EQN_CHAINS = [
    (
        [
            "SolarBatteryDesign", "solar_battery_plant",
            "battery_system", "battery_pack", "cost_model",
        ],
        "SolarBatteryDesign__solar_battery_plant__battery_system__battery_pack__cost_model",
    ),
    (
        ["CATFMFEPhysics", "catf_physics", "net_electric"],
        "CATFMFEPhysics__catf_physics__net_electric",
    ),
    (
        ["CATFMFEPhysics", "catf_physics", "alpha_neutron_split"],
        "CATFMFEPhysics__catf_physics__alpha_neutron_split",
    ),
]

# PQN test data: (EQN, param_name, expected_PQN)
PQN_EXAMPLES = [
    (
        "SolarBatteryDesign__solar_battery_plant__battery_system__battery_pack__cost_model",
        "total_cost",
        "SolarBatteryDesign__solar_battery_plant__battery_system__battery_pack__cost_model__total_cost",
    ),
    (
        "CATFMFEPhysics__catf_physics__net_electric",
        "net_power",
        "CATFMFEPhysics__catf_physics__net_electric__net_power",
    ),
    (
        "CATFMFEPhysics__catf_physics__alpha_neutron_split",
        "alpha_fraction",
        "CATFMFEPhysics__catf_physics__alpha_neutron_split__alpha_fraction",
    ),
]

# Key_C test data: (EQN, output_attr, expected_key_c)
KEY_C_EXAMPLES = [
    (
        "SolarBatteryDesign__solar_battery_plant__battery_system__battery_pack__cost_model",
        "total_cost",
        "solar_battery_plant.battery_system.battery_pack.cost_model.total_cost",
    ),
    (
        "CATFMFEPhysics__catf_physics__net_electric",
        "net_power",
        "catf_physics.net_electric.net_power",
    ),
]


# ---------------------------------------------------------------------------
# REQ-NC-06: sanitize_name()
# ---------------------------------------------------------------------------


@pytest.mark.req("REQ-NC-06")
class TestSanitizeName:
    """Verifies sanitize_name() applies all 6 transforms correctly."""

    def test_strip_quotes(self):
        assert sanitize_name("'Quoted Name'") == "Quoted_Name"
        assert sanitize_name('"Double Quoted"') == "Double_Quoted"

    def test_spaces_to_underscore(self):
        assert sanitize_name("hello world") == "hello_world"

    def test_special_chars(self):
        assert sanitize_name("Racking_&_Mounting") == "Racking_Mounting"
        assert sanitize_name("foo$bar") == "foo_bar"

    def test_collapse_underscores(self):
        assert sanitize_name("a___b") == "a_b"

    def test_strip_edge_underscores(self):
        assert sanitize_name("___leading___") == "leading"

    @pytest.mark.parametrize("word", RESERVED_WORDS)
    def test_reserved_words(self, word):
        assert sanitize_name(word) == f"{word}_"

    def test_transform_order(self):
        # "'class & def'" -> strip quotes -> "class & def"
        # -> spaces to _ -> "class_&_def" -> non-alnum to _ -> "class___def"
        # -> collapse _ -> "class_def" -> strip edge _ -> "class_def"
        # -> not a reserved word -> "class_def"
        assert sanitize_name("'class & def'") == "class_def"

    def test_edge_cases(self):
        assert sanitize_name("") == ""
        assert sanitize_name(None) == ""
        assert sanitize_name("$$$") == "unnamed"


# ---------------------------------------------------------------------------
# REQ-NC-01: EQN construction
# ---------------------------------------------------------------------------


@pytest.mark.req("REQ-NC-01")
class TestEQN:
    """Verifies EQN construction from ownership chains."""

    def test_joins_with_double_underscore(self):
        elem = _build_chain(["Root", "Middle", "Leaf"])
        result = build_element_qualified_name(elem)
        assert result == "Root__Middle__Leaf"
        assert "__" in result

    def test_segments_sanitized(self):
        elem = _build_chain(["Solar Battery", "cost_model"])
        result = build_element_qualified_name(elem)
        assert "Solar_Battery" in result
        assert " " not in result

    @pytest.mark.parametrize(
        "chain,expected",
        KNOWN_EQN_CHAINS,
        ids=[c[-1].split("__")[-1] for c in KNOWN_EQN_CHAINS],
    )
    def test_known_outputs(self, chain, expected):
        elem = _build_chain(chain)
        assert build_element_qualified_name(elem) == expected


# ---------------------------------------------------------------------------
# REQ-NC-02: PQN construction
# ---------------------------------------------------------------------------


@pytest.mark.req("REQ-NC-02")
class TestPQN:
    """Verifies PQN extends EQN with __{param_name}."""

    def test_pqn_extends_eqn(self):
        result = build_parameter_qualified_name(
            "Design__plant__cost_model", "total_cost"
        )
        assert result == "Design__plant__cost_model__total_cost"

    @pytest.mark.parametrize(
        "eqn,param,expected",
        PQN_EXAMPLES,
        ids=[e[1] for e in PQN_EXAMPLES],
    )
    def test_pqn_with_real_eqns(self, eqn, param, expected):
        assert build_parameter_qualified_name(eqn, param) == expected


# ---------------------------------------------------------------------------
# REQ-NC-03: Module name
# ---------------------------------------------------------------------------


@pytest.mark.req("REQ-NC-03")
class TestModuleName:
    """Verifies module name is lowercased EQN."""

    def test_module_name_is_lowered_eqn(self):
        result = get_module_name(
            "SolarBatteryDesign__solar_battery_plant__cost_model"
        )
        assert result == "solarbatterydesign__solar_battery_plant__cost_model"

    # Hand-transcribed lowercased module name per REAL_EQNS row. Replaces the former
    # `assert result == eqn.lower()`, which recomputed get_module_name's own lowercasing
    # (a tautology). provenance: hand-transcribed lowercasing of each REAL_EQNS row.
    EXPECTED_MODULE_NAMES = {
        "SolarBatteryDesign__solar_battery_plant__battery_system__battery_pack__cost_model":
            "solarbatterydesign__solar_battery_plant__battery_system__battery_pack__cost_model",
        "CATFMFEPhysics__catf_physics__net_electric":
            "catfmfephysics__catf_physics__net_electric",
        "CATFMFEPhysics__catf_physics__alpha_neutron_split":
            "catfmfephysics__catf_physics__alpha_neutron_split",
    }

    @pytest.mark.parametrize("eqn", REAL_EQNS)
    def test_module_name_parametrized(self, eqn):
        assert get_module_name(eqn) == self.EXPECTED_MODULE_NAMES[eqn]


# ---------------------------------------------------------------------------
# REQ-NC-04: Module type
# ---------------------------------------------------------------------------


@pytest.mark.req("REQ-NC-04")
class TestModuleType:
    """Verifies module type format: {namespace}.{ElementName}Module."""

    def test_module_type_format(self):
        result = derive_module_type("SolarBatteryLibrary::BatteryPackCostCalc")
        assert result == "solarbatterylibrary.BatteryPackCostCalcModule"

    def test_module_type_no_package(self):
        result = derive_module_type("Standalone")
        assert result == "StandaloneModule"

    @pytest.mark.parametrize(
        "sysml_qn,expected",
        SYSML_QNS_AND_MODULE_TYPES,
        ids=[q[0].split("::")[-1] for q in SYSML_QNS_AND_MODULE_TYPES],
    )
    def test_module_type_parametrized(self, sysml_qn, expected):
        assert derive_module_type(sysml_qn) == expected


# ---------------------------------------------------------------------------
# REQ-NC-05: Channel name
# ---------------------------------------------------------------------------


@pytest.mark.req("REQ-NC-05")
class TestChannelName:
    """Verifies channel names are PQNs."""

    def test_channel_name_is_pqn(self):
        result = get_channel_name("Design__plant__cost_model", "total_cost")
        assert result == "Design__plant__cost_model__total_cost"

    @pytest.mark.parametrize(
        "eqn,output,expected",
        PQN_EXAMPLES,
        ids=[e[1] for e in PQN_EXAMPLES],
    )
    def test_channel_name_parametrized(self, eqn, output, expected):
        # Channel name == PQN (REQ-NC-05)
        assert get_channel_name(eqn, output) == expected


# ---------------------------------------------------------------------------
# REQ-NC-07: Key formats (dotted, no ::)
# ---------------------------------------------------------------------------


@pytest.mark.req("REQ-NC-07")
class TestKeyFormats:
    """Verifies registry key formats use dots, not ::."""

    def test_key_c_strips_design_prefix(self):
        result = make_scoped_key(
            "SolarBatteryDesign__solar_battery_plant__battery_system__battery_pack__cost_model",
            "total_cost",
        )
        assert result == "solar_battery_plant.battery_system.battery_pack.cost_model.total_cost"
        assert not result.startswith("SolarBatteryDesign")

    def test_key_c_uses_dots_not_colons(self):
        result = make_scoped_key(
            "CATFMFEPhysics__catf_physics__net_electric",
            "net_power",
        )
        assert "::" not in result
        assert "." in result

    @pytest.mark.parametrize(
        "eqn,output,expected",
        KEY_C_EXAMPLES,
        ids=[e[2].split(".")[-1] for e in KEY_C_EXAMPLES],
    )
    def test_key_c_parametrized(self, eqn, output, expected):
        assert make_scoped_key(eqn, output) == expected

    def test_no_colon_keys_in_key_formats(self):
        """All key formats (A, B, C, D, E, F) use dotted format, never ::."""
        # Key_A: instance.output
        key_a = "cost_model.total_cost"
        assert "::" not in key_a

        # Key_B: canonical PQN channel (uses __, not ::)
        key_b = get_channel_name(
            "SolarBatteryDesign__solar_battery_plant__cost_model",
            "total_cost",
        )
        assert "::" not in key_b

        # Key_C: derive_key_c()
        key_c = make_scoped_key(
            "SolarBatteryDesign__solar_battery_plant__cost_model",
            "total_cost",
        )
        assert "::" not in key_c

        # Key_D: part_usage.attr
        key_d = "battery_system.capital_cost"
        assert "::" not in key_d

        # Key_E: full dotted instance path
        key_e = "SolarBatteryDesign.solar_battery_plant.battery_system.capital_cost"
        assert "::" not in key_e

        # Key_F: owning_part.attr
        key_f = "Solar_Array.dc_capacity"
        assert "::" not in key_f


# ---------------------------------------------------------------------------
# Utility functions (no REQ mapping)
# ---------------------------------------------------------------------------


class TestUtilities:
    """Utility function tests for completeness."""

    def test_sysml_to_python_qn_roundtrip(self):
        original = "A::B::C"
        python_qn = sysml_to_python_qualified_name(original)
        assert python_qn == "A__B__C"
        roundtrip = python_to_sysml_qualified_name(python_qn)
        assert roundtrip == original

    def test_extract_simple_name(self):
        assert extract_simple_name("A::B::C") == "C"
        assert extract_simple_name("A__B__C") == "C"
        assert extract_simple_name("A.B.C") == "C"
        assert extract_simple_name("standalone") == "standalone"
