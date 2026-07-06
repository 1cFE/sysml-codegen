"""Conformance tests for ParameterGroupDeriver (C13).

Tests REQ-PGD-01 through REQ-PGD-07 using real extraction snapshot data.
No mocks — all tests use real Pydantic models and real SysML fixture output.

Design intent doc: 17-parameter-group-deriver.md
"""

from __future__ import annotations

from pathlib import Path

import pytest

from sysml_codegen.analysis.dependency_backtracker import (
    BacktrackingResult,
    _ensure_backtracking_result_rebuilt,
)
from sysml_codegen.analysis.parameter_groups import (
    DerivedParameterGroup,
    ParameterGroupDeriver,
)
from sysml_codegen.analysis.phantom_detector import PhantomDetectionReport
from sysml_codegen.snapshot import load_extraction_snapshot  # noqa: I001
from tests.conftest import snapshot_fixture

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def build_deriver_from_snapshot(snap: dict) -> ParameterGroupDeriver:
    """Build ParameterGroupDeriver from extraction snapshot data.

    Converts design_attributes dict keys from str to Path (snapshot loader
    returns string keys; deriver expects Path keys for .stem/.name access).
    """
    design_attrs = {Path(k): v for k, v in snap["design_attributes"].items()}
    return ParameterGroupDeriver(design_attrs, snap["calc_usages"], snap["calc_defs"])


def _collect_all_index_keys(deriver: ParameterGroupDeriver) -> dict[str, set[str]]:
    """Collect all qualified names from all 4 indexes."""
    return {
        "attr": set(deriver._attr_index.keys()),
        "binding": set(deriver._binding_index.keys()),
        "unbound": set(deriver._unbound_index.keys()),
        "literal": set(deriver._literal_index.keys()),
    }


# ---------------------------------------------------------------------------
# Session-scoped fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def solar_battery_deriver():
    snap = load_extraction_snapshot(snapshot_fixture("solar_battery_model"))
    return build_deriver_from_snapshot(snap), snap


@pytest.fixture(scope="session")
def catf_mfe_deriver():
    snap = load_extraction_snapshot(snapshot_fixture("catf_mfe_model"))
    return build_deriver_from_snapshot(snap), snap


@pytest.fixture(scope="session")
def chain_spike_deriver():
    snap = load_extraction_snapshot(snapshot_fixture("chain_spike_model"))
    return build_deriver_from_snapshot(snap), snap


# ===========================================================================
# REQ-PGD-01: Unique Assignment — each parameter claimed by exactly one index
# ===========================================================================


class TestReqPgd01UniqueAssignment:

    @pytest.mark.req("REQ-PGD-01")
    def test_req_pgd_01_unique_assignment_solar_battery(self, solar_battery_deriver):
        """No qname appears in more than one index (solar_battery)."""
        deriver, _ = solar_battery_deriver
        indexes = _collect_all_index_keys(deriver)

        all_keys = []
        for name, keys in indexes.items():
            all_keys.extend(keys)

        # No duplicates across indexes
        assert len(all_keys) == len(set(all_keys)), (
            "Some qnames appear in multiple indexes"
        )

    @pytest.mark.req("REQ-PGD-01")
    def test_req_pgd_01_unique_assignment_catf_mfe(self, catf_mfe_deriver):
        """No qname appears in more than one index (catf_mfe — 530 attrs, 17 files)."""
        deriver, _ = catf_mfe_deriver
        indexes = _collect_all_index_keys(deriver)

        all_keys = []
        for keys in indexes.values():
            all_keys.extend(keys)

        assert len(all_keys) == len(set(all_keys)), (
            "Some qnames appear in multiple indexes"
        )

    @pytest.mark.req("REQ-PGD-01")
    def test_req_pgd_01_every_group_param_unique(self, solar_battery_deriver):
        """derive_groups() produces no duplicate param.name across all groups."""
        deriver, _ = solar_battery_deriver
        groups = deriver.derive_groups()

        all_param_names = []
        for group in groups:
            for param in group.parameters:
                all_param_names.append(param.name)

        assert len(all_param_names) == len(set(all_param_names)), (
            f"Duplicate param names found: "
            f"{[n for n in all_param_names if all_param_names.count(n) > 1]}"
        )


# ===========================================================================
# REQ-PGD-02: Four Index Precedence
# ===========================================================================


class TestReqPgd02FourIndexPrecedence:

    @pytest.mark.req("REQ-PGD-02")
    def test_req_pgd_02_four_indexes_populated(self, solar_battery_deriver):
        """All 4 indexes are non-empty for solar_battery."""
        deriver, _ = solar_battery_deriver
        indexes = _collect_all_index_keys(deriver)

        assert len(indexes["attr"]) > 0, "_attr_index is empty"
        assert len(indexes["binding"]) > 0, "_binding_index is empty"
        assert len(indexes["unbound"]) > 0, "_unbound_index is empty"
        assert len(indexes["literal"]) > 0, "_literal_index is empty"

    @pytest.mark.req("REQ-PGD-02")
    def test_req_pgd_02_attr_index_has_design_attrs(self, solar_battery_deriver):
        """_attr_index keys match expected solar_battery design attribute qnames."""
        deriver, _ = solar_battery_deriver

        # Known design attributes from solar_battery snapshot
        expected_qnames = {
            "SolarBatteryDesign__solar_battery_plant__p_net_mw",
            "SolarBatteryDesign__solar_battery_plant__discount_rate",
            "SolarBatteryDesign__solar_battery_plant__plant_lifetime",
        }

        attr_keys = set(deriver._attr_index.keys())
        assert expected_qnames.issubset(attr_keys), (
            f"Missing expected design attrs: {expected_qnames - attr_keys}"
        )

    @pytest.mark.req("REQ-PGD-02")
    def test_req_pgd_02_binding_excludes_attr_names(self, solar_battery_deriver):
        """_binding_index keys do not overlap with _attr_index keys."""
        deriver, _ = solar_battery_deriver
        overlap = set(deriver._binding_index.keys()) & set(deriver._attr_index.keys())
        assert overlap == set(), f"Binding/attr overlap: {overlap}"

    @pytest.mark.req("REQ-PGD-02")
    def test_req_pgd_02_unbound_excludes_higher_precedence(self, solar_battery_deriver):
        """_unbound_index keys do not appear in _attr_index or _binding_index."""
        deriver, _ = solar_battery_deriver
        unbound_keys = set(deriver._unbound_index.keys())
        higher = set(deriver._attr_index.keys()) | set(deriver._binding_index.keys())
        overlap = unbound_keys & higher
        assert overlap == set(), f"Unbound/higher overlap: {overlap}"

    @pytest.mark.req("REQ-PGD-02")
    def test_req_pgd_02_literal_excludes_all_higher(self, solar_battery_deriver):
        """_literal_index keys do not appear in any higher-precedence index."""
        deriver, _ = solar_battery_deriver
        literal_keys = set(deriver._literal_index.keys())
        higher = (
            set(deriver._attr_index.keys())
            | set(deriver._binding_index.keys())
            | set(deriver._unbound_index.keys())
        )
        overlap = literal_keys & higher
        assert overlap == set(), f"Literal/higher overlap: {overlap}"


# ===========================================================================
# REQ-PGD-03: File-Based Grouping
# ===========================================================================


class TestReqPgd03FileBasedGrouping:

    @pytest.mark.req("REQ-PGD-03")
    def test_req_pgd_03_group_count_solar_battery(self, solar_battery_deriver):
        """solar_battery has 2 source files -> at least 2 groups."""
        deriver, _ = solar_battery_deriver
        groups = deriver.derive_groups()

        assert len(groups) >= 2, (
            f"Expected at least 2 groups, got {len(groups)}"
        )
        # Every group name should be unique
        group_names = [g.name for g in groups]
        assert len(group_names) == len(set(group_names))

    @pytest.mark.req("REQ-PGD-03")
    def test_req_pgd_03_group_count_chain_spike(self, chain_spike_deriver):
        """chain_spike has 1 source file -> exactly 1 group."""
        deriver, _ = chain_spike_deriver
        groups = deriver.derive_groups()

        assert len(groups) >= 1, (
            f"Expected at least 1 group, got {len(groups)}"
        )
        group_names = [g.name for g in groups]
        assert len(group_names) == len(set(group_names))

    @pytest.mark.req("REQ-PGD-03")
    def test_req_pgd_03_source_identifier_is_sysml_filename(
        self, solar_battery_deriver
    ):
        """Every group's source_identifier ends with .sysml."""
        deriver, _ = solar_battery_deriver
        groups = deriver.derive_groups()

        for group in groups:
            assert group.source_identifier.endswith(".sysml"), (
                f"Group '{group.name}' source_identifier "
                f"'{group.source_identifier}' doesn't end with .sysml"
            )

    @pytest.mark.req("REQ-PGD-03")
    def test_req_pgd_03_catf_mfe_many_groups(self, catf_mfe_deriver):
        """catf_mfe has 17 source files. Verify group count >= 10."""
        deriver, _ = catf_mfe_deriver
        groups = deriver.derive_groups()

        assert len(groups) >= 10, (
            f"Expected at least 10 groups for catf_mfe, got {len(groups)}"
        )


# ===========================================================================
# REQ-PGD-04: Filtered Groups
# ===========================================================================


class TestReqPgd04FilteredGroups:

    @pytest.mark.req("REQ-PGD-04")
    def test_req_pgd_04_filtered_retains_only_entry_points(
        self, solar_battery_deriver
    ):
        """derive_groups_filtered() retains only params in entry_points set."""
        deriver, snap = solar_battery_deriver

        # Use a subset of known deriver index names as entry points
        all_indexes = _collect_all_index_keys(deriver)
        all_qnames = set()
        for keys in all_indexes.values():
            all_qnames.update(keys)

        # Pick a subset (first 5 from each index that has entries)
        entry_points: set[str] = set()
        for keys in all_indexes.values():
            entry_points.update(list(keys)[:5])

        _ensure_backtracking_result_rebuilt()
        bt_result = BacktrackingResult(
            required_usages=[],
            dependency_graph={},
            entry_points=entry_points,
            entry_point_sources={},
            phantom_report=PhantomDetectionReport(),
        )

        filtered = deriver.derive_groups_filtered(bt_result, snap["calc_defs"])

        # Every surviving param.name must be in entry_points
        for group in filtered:
            for param in group.parameters:
                assert param.name in entry_points, (
                    f"Param '{param.name}' in group '{group.name}' "
                    f"is not in entry_points"
                )

    @pytest.mark.req("REQ-PGD-04")
    def test_req_pgd_04_filtered_drops_empty_groups(self, solar_battery_deriver):
        """Groups with no surviving params are dropped."""
        deriver, snap = solar_battery_deriver

        # Use entry_points from only _attr_index (design.sysml attrs)
        attr_keys = set(deriver._attr_index.keys())
        # Pick just 2 to ensure some groups are empty
        entry_points = set(list(attr_keys)[:2])

        _ensure_backtracking_result_rebuilt()
        bt_result = BacktrackingResult(
            required_usages=[],
            dependency_graph={},
            entry_points=entry_points,
            entry_point_sources={},
            phantom_report=PhantomDetectionReport(),
        )

        filtered = deriver.derive_groups_filtered(bt_result, snap["calc_defs"])

        # Every surviving group must have at least one parameter
        for group in filtered:
            assert len(group.parameters) > 0, (
                f"Group '{group.name}' has no parameters but wasn't dropped"
            )

        # Fewer groups than unfiltered
        all_groups = deriver.derive_groups()
        assert len(filtered) <= len(all_groups)

    @pytest.mark.req("REQ-PGD-04")
    def test_req_pgd_04_filtered_preserves_group_structure(
        self, solar_battery_deriver
    ):
        """Surviving groups retain correct name, class_name, source_type, source_identifier."""
        deriver, snap = solar_battery_deriver

        # Use all index keys as entry points (everything survives)
        all_indexes = _collect_all_index_keys(deriver)
        entry_points: set[str] = set()
        for keys in all_indexes.values():
            entry_points.update(keys)

        _ensure_backtracking_result_rebuilt()
        bt_result = BacktrackingResult(
            required_usages=[],
            dependency_graph={},
            entry_points=entry_points,
            entry_point_sources={},
            phantom_report=PhantomDetectionReport(),
        )

        filtered = deriver.derive_groups_filtered(bt_result, snap["calc_defs"])

        for group in filtered:
            assert isinstance(group, DerivedParameterGroup)
            assert group.name, "Group name is empty"
            assert group.class_name, "Group class_name is empty"
            assert group.source_type in ("design", "library")
            assert group.source_identifier, "Group source_identifier is empty"


# ===========================================================================
# REQ-PGD-05: Classify
# ===========================================================================


class TestReqPgd05Classify:

    @pytest.mark.req("REQ-PGD-05")
    def test_req_pgd_05_classify_returns_group_for_attr_index(
        self, solar_battery_deriver
    ):
        """A design-attribute qname classifies to design_params.

        Former body drew qname = next(iter(_attr_index)) and asserted only non-None --
        it never pinned which group. Anchor a named qname to a named group.
        """
        deriver, _ = solar_battery_deriver
        # provenance: design.sysml:53 -- p_net_mw is a design attribute.
        qname = "SolarBatteryDesign__solar_battery_plant__p_net_mw"
        assert deriver.classify(qname) == "design_params"

    @pytest.mark.req("REQ-PGD-05")
    def test_req_pgd_05_classify_returns_group_for_binding_index(
        self, solar_battery_deriver
    ):
        """A binding-traced qname classifies to design_params (traces to a design attr)."""
        deriver, _ = solar_battery_deriver
        # provenance: energy_production.p_net_mw binds to the design attr p_net_mw
        #   (design.sysml:69), so it groups with design_params.
        qname = "SolarBatteryDesign__solar_battery_plant__energy_production__p_net_mw"
        assert deriver.classify(qname) == "design_params"

    @pytest.mark.req("REQ-PGD-05")
    def test_req_pgd_05_classify_returns_group_for_unbound_index(
        self, solar_battery_deriver
    ):
        """An unbound library-default qname classifies to library_params."""
        deriver, _ = solar_battery_deriver
        # provenance: cost_per_watt is a library calc-def input default (library.sysml).
        qname = (
            "SolarBatteryDesign__solar_battery_plant__solar_array__pv_module"
            "__cost_model__cost_per_watt"
        )
        assert deriver.classify(qname) == "library_params"

    @pytest.mark.req("REQ-PGD-05")
    def test_req_pgd_05_classify_returns_group_for_literal_index(
        self, solar_battery_deriver
    ):
        """A usage-literal qname classifies to library_params."""
        deriver, _ = solar_battery_deriver
        # provenance: child_count = 25.0 usage literal (library.sysml:608).
        qname = (
            "SolarBatteryDesign__solar_battery_plant__solar_array__allocation_model"
            "__child_count"
        )
        assert deriver.classify(qname) == "library_params"

    @pytest.mark.req("REQ-PGD-05")
    def test_req_pgd_05_classify_unknown_returns_none(self, solar_battery_deriver):
        """classify() returns None for an unknown qname."""
        deriver, _ = solar_battery_deriver
        result = deriver.classify("nonexistent__param__name")
        assert result is None

    @pytest.mark.req("REQ-PGD-05")
    def test_req_pgd_05_classify_precedence_matches_index(
        self, solar_battery_deriver
    ):
        """classify() returns the transcribed group for a named design-param qname.

        Former body computed expected_group = deriver._generate_group_names(file.stem) --
        the same method classify() calls internally -- so it could never fail. Anchor to
        a literal group name.
        """
        deriver, _ = solar_battery_deriver
        # provenance: design.sysml:53 -- p_net_mw is a design attribute -> design_params.
        assert deriver.classify(
            "SolarBatteryDesign__solar_battery_plant__p_net_mw"
        ) == "design_params"


# ===========================================================================
# REQ-PGD-06: Default Value Resolution
# ===========================================================================


class TestReqPgd06DefaultValueResolution:

    @pytest.mark.req("REQ-PGD-06")
    def test_req_pgd_06_default_value_direct_attr(self, solar_battery_deriver):
        """get_default_value() for a known design attr qname returns correct float."""
        deriver, _ = solar_battery_deriver
        # SolarBatteryDesign__solar_battery_plant__p_net_mw has default "0.008"
        qname = "SolarBatteryDesign__solar_battery_plant__p_net_mw"
        result = deriver.get_default_value(qname)
        assert result == pytest.approx(0.008), f"Expected 0.008, got {result}"

    @pytest.mark.req("REQ-PGD-06")
    def test_req_pgd_06_default_value_binding_resolution(
        self, solar_battery_deriver
    ):
        """get_default_value() resolves a binding-traced qname to its design-attr value.

        Former body drew a binding qname and asserted only ``None or isinstance float``
        (no value pinned, and it skipped when the index was empty). Anchor a named
        binding qname to the transcribed design-attr default it traces to.
        """
        deriver, _ = solar_battery_deriver
        # provenance: energy_production.p_net_mw binds to design attr p_net_mw = 0.008
        #   (design.sysml:53, bound at design.sysml:69).
        qname = "SolarBatteryDesign__solar_battery_plant__energy_production__p_net_mw"
        assert deriver.get_default_value(qname) == pytest.approx(0.008)

    @pytest.mark.req("REQ-PGD-06")
    def test_req_pgd_06_default_value_literal(self, solar_battery_deriver):
        """get_default_value() returns the transcribed literal for literal-indexed qnames.

        Former body read ``_, expected = _literal_index[qname]`` then asserted
        get_default_value(qname) equalled that same dict value -- a tautology. Anchor to
        hand-transcribed literals.
        """
        deriver, _ = solar_battery_deriver
        # provenance: library.sysml:608 (child_count = 25.0), :609 (total_child_mass = 50.0).
        child_count = (
            "SolarBatteryDesign__solar_battery_plant__solar_array__allocation_model"
            "__child_count"
        )
        total_child_mass = (
            "SolarBatteryDesign__solar_battery_plant__solar_array__allocation_model"
            "__total_child_mass"
        )
        assert deriver.get_default_value(child_count) == pytest.approx(25.0)
        assert deriver.get_default_value(total_child_mass) == pytest.approx(50.0)

    @pytest.mark.req("REQ-PGD-06")
    def test_req_pgd_06_default_value_unbound_returns_none(
        self, solar_battery_deriver
    ):
        """get_default_value() for an unbound-indexed qname returns None."""
        deriver, _ = solar_battery_deriver

        if not deriver._unbound_index:
            pytest.skip("No unbound index entries")

        qname = next(iter(deriver._unbound_index.keys()))
        result = deriver.get_default_value(qname)
        assert result is None

    @pytest.mark.req("REQ-PGD-06")
    def test_req_pgd_06_default_value_unknown_returns_none(
        self, solar_battery_deriver
    ):
        """get_default_value() for unknown qname returns None."""
        deriver, _ = solar_battery_deriver
        result = deriver.get_default_value("nonexistent__qname__here")
        assert result is None


# ===========================================================================
# REQ-PGD-07: Group Naming Convention
# ===========================================================================


class TestReqPgd07GroupNamingConvention:

    @pytest.mark.req("REQ-PGD-07")
    def test_req_pgd_07_snake_case_params_suffix(self, solar_battery_deriver):
        """_generate_group_names('SolarBatteryDesign') produces expected names."""
        deriver, _ = solar_battery_deriver
        group_name, class_name = deriver._generate_group_names("SolarBatteryDesign")
        assert group_name == "solar_battery_design_params"
        assert class_name == "SolarBatteryDesignParams"

    @pytest.mark.req("REQ-PGD-07")
    def test_req_pgd_07_already_suffixed_input(self, solar_battery_deriver):
        """_generate_group_names('design_params') avoids double _params suffix."""
        deriver, _ = solar_battery_deriver
        group_name, class_name = deriver._generate_group_names("design_params")
        assert group_name == "design_params", f"Got {group_name}"
        assert class_name == "DesignParams", f"Got {class_name}"

    @pytest.mark.req("REQ-PGD-07")
    def test_req_pgd_07_real_group_names_from_fixture(self, solar_battery_deriver):
        """derive_groups() groups: name ends with _params, class_name ends with Params."""
        deriver, _ = solar_battery_deriver
        groups = deriver.derive_groups()

        assert len(groups) > 0, "No groups derived"
        for group in groups:
            assert group.name.endswith("_params"), (
                f"Group name '{group.name}' doesn't end with _params"
            )
            assert group.class_name.endswith("Params"), (
                f"Class name '{group.class_name}' doesn't end with Params"
            )

    @pytest.mark.req("REQ-PGD-07")
    def test_req_pgd_07_class_name_matches_group_name(self, solar_battery_deriver):
        """class_name is PascalCase equivalent of group name."""
        deriver, _ = solar_battery_deriver
        groups = deriver.derive_groups()

        for group in groups:
            # Strip _params, PascalCase, re-append Params
            base = group.name
            assert base.endswith("_params")
            base = base[: -len("_params")]
            expected_class = (
                "".join(word.capitalize() for word in base.split("_")) + "Params"
            )
            assert group.class_name == expected_class, (
                f"Group '{group.name}': expected class_name '{expected_class}', "
                f"got '{group.class_name}'"
            )
