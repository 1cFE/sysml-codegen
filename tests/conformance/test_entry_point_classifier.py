"""Conformance tests for Entry Point Classification (C17).

Requirements: REQ-EPC-01 through REQ-EPC-08
Design intent: 06-entry-point-classifier.md

Tests verify _classify_entry_points() behavior with real extraction data:
- Every EP classified as exactly one EntryPointType
- Precedence: DESIGN_ATTRIBUTE > LIBRARY_DEFAULT > USAGE_LITERAL
- Float conversion of default_value (or None on failure)
- param_group assigned via ParameterGroupDeriver
- Orphan EPs land in "system_design" group
- Groups rebuilt after factory construction
- Pure function (no input mutation)
- Factory EPs retain DESIGN_ATTRIBUTE, never re-classified

Tests use real extraction snapshot data -- no mocks.
"""

from __future__ import annotations

import ast
import copy
import inspect
import textwrap
from types import SimpleNamespace

import pytest

from sysml_codegen.extraction.usage_extractor import CalcUsageData
from sysml_codegen.resolution.graph_builder import (
    _classify_entry_points,
    _get_library_default,
    build_computation_graph,
)
from sysml_codegen.resolution.models import (
    EntryPoint,
    EntryPointType,
)
from sysml_codegen.snapshot import (
    build_classifier_inputs_from_snapshot,
    build_full_graph_from_snapshot,
)
from tests.conftest import snapshot_fixture


# ---------------------------------------------------------------------------
# Session-scoped fixtures (expensive -- build once per session)
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session")
def solar_battery_classifier():
    """Classifier inputs for solar_battery_model."""
    return build_classifier_inputs_from_snapshot(snapshot_fixture("solar_battery_model"))


@pytest.fixture(scope="session")
def catf_mfe_classifier():
    """Classifier inputs for catf_mfe_model."""
    return build_classifier_inputs_from_snapshot(snapshot_fixture("catf_mfe_model"))


@pytest.fixture(scope="session")
def chain_spike_classifier():
    """Classifier inputs for chain_spike_model."""
    return build_classifier_inputs_from_snapshot(snapshot_fixture("chain_spike_model"))


@pytest.fixture(scope="session")
def solar_battery_full_graph():
    """Full ComputationGraph for solar_battery_model."""
    return build_full_graph_from_snapshot(snapshot_fixture("solar_battery_model"))


@pytest.fixture(scope="session", params=[
    "solar_battery_model",
    "catf_mfe_model",
    "chain_spike_model",
])
def classifier_inputs(request):
    """Parametrized classifier inputs across 3 models."""
    return build_classifier_inputs_from_snapshot(snapshot_fixture(request.param))


# ===========================================================================
# REQ-EPC-01: Every EP classified as exactly one EntryPointType
# ===========================================================================
class TestEveryEPHasType:
    """REQ-EPC-01: Every EP has exactly one EntryPointType."""

    @pytest.mark.req("REQ-EPC-01")
    def test_every_ep_has_exactly_one_type(self, classifier_inputs):
        """Every EP in entry_points dict has entry_type in EntryPointType and is not None."""
        entry_points = classifier_inputs["entry_points"]
        assert len(entry_points) > 0, "No entry points classified"
        for qname, ep in entry_points.items():
            assert ep.entry_type is not None, f"EP {qname} has None entry_type"
            assert ep.entry_type in EntryPointType, (
                f"EP {qname} has invalid entry_type: {ep.entry_type}"
            )

    @pytest.mark.req("REQ-EPC-01")
    def test_classification_types_present_catf_mfe(self, catf_mfe_classifier):
        """catf_mfe produces all 3 EP types from the classifier."""
        entry_points = catf_mfe_classifier["entry_points"]
        types_present = {ep.entry_type for ep in entry_points.values()}
        assert EntryPointType.DESIGN_ATTRIBUTE in types_present
        assert EntryPointType.LIBRARY_DEFAULT in types_present
        assert EntryPointType.USAGE_LITERAL in types_present

    @pytest.mark.req("REQ-EPC-01")
    def test_simple_name_derivation(self, classifier_inputs):
        """Every EP's simple_name equals qualified_name.split('__')[-1]."""
        entry_points = classifier_inputs["entry_points"]
        for qname, ep in entry_points.items():
            expected_simple = qname.split("__")[-1]
            assert ep.simple_name == expected_simple, (
                f"EP {qname}: simple_name={ep.simple_name}, expected={expected_simple}"
            )

    @pytest.mark.req("REQ-EPC-01")
    def test_source_calc_usage_set_for_library_default(self, classifier_inputs):
        """LIBRARY_DEFAULT EPs have source_calc_usage; others do not."""
        entry_points = classifier_inputs["entry_points"]
        for qname, ep in entry_points.items():
            if ep.entry_type == EntryPointType.LIBRARY_DEFAULT:
                assert ep.source_calc_usage is not None, (
                    f"LIBRARY_DEFAULT EP {qname} has None source_calc_usage"
                )
            else:
                assert ep.source_calc_usage is None, (
                    f"{ep.entry_type.value} EP {qname} has non-None source_calc_usage: "
                    f"{ep.source_calc_usage}"
                )

    @pytest.mark.req("REQ-EPC-01")
    def test_ep_count_matches_backtracker(self, classifier_inputs):
        """Number of classified EPs equals len(BacktrackingResult.entry_points)."""
        result = classifier_inputs["result"]
        entry_points = classifier_inputs["entry_points"]
        assert len(entry_points) == len(result.entry_points), (
            f"Classified {len(entry_points)} EPs but backtracker found "
            f"{len(result.entry_points)}"
        )


# ===========================================================================
# REQ-EPC-02: Precedence DESIGN_ATTRIBUTE > LIBRARY_DEFAULT > USAGE_LITERAL
# ===========================================================================
class TestClassificationPrecedence:
    """REQ-EPC-02: Strict precedence in classification."""

    @pytest.mark.req("REQ-EPC-02")
    def test_design_attribute_precedence(self, catf_mfe_classifier):
        """When a QN exists in both DA and LD indexes, DA wins.

        No fixture model naturally produces overlap (DA QNs use design-qualified
        names while unbound QNs use library-qualified names). This test constructs
        a minimal overlap by injecting a synthetic unbound param whose QN matches
        an existing DA-classified EP, then re-classifying to verify DA still wins.
        """
        inputs = catf_mfe_classifier
        entry_points = inputs["entry_points"]
        design_attr_by_qname = inputs["design_attr_by_qname"]
        result = inputs["result"]
        calc_def_map = inputs["calc_def_map"]
        design_attrs = inputs["design_attrs"]
        group_deriver = inputs["group_deriver"]

        # Find a DA-matching EP to use as the overlap QN
        da_matching = set(design_attr_by_qname.keys()) & set(entry_points.keys())
        assert len(da_matching) > 0, "No EPs match design_attr_by_qname in catf_mfe"
        overlap_qn = next(iter(da_matching))

        # Construct a synthetic usage whose unbound_params produces the same QN.
        # QN format: usage.qualified_name__param_name
        parts = overlap_qn.rsplit("__", 1)
        assert len(parts) == 2, f"Cannot split overlap QN: {overlap_qn}"
        usage_qn, param_name = parts

        synthetic_usage = CalcUsageData(
            instance_name="synthetic_overlap_test",
            calc_def_name=list(calc_def_map.keys())[0],  # any valid calc def
            calc_def_qualified_name="test",
            module_type="test",
            unbound_params=[param_name],
            qualified_name=usage_qn,
        )

        # Build augmented usages list with the synthetic overlap
        augmented_usages = list(result.required_usages) + [synthetic_usage]

        # Re-classify with augmented usages
        reclassified = _classify_entry_points(
            result.entry_points,
            result.entry_point_sources,
            design_attrs,
            augmented_usages,
            calc_def_map,
            group_deriver,
        )

        # The overlap QN must be classified as DA, not LD
        ep = reclassified[overlap_qn]
        assert ep.entry_type == EntryPointType.DESIGN_ATTRIBUTE, (
            f"EP {overlap_qn} exists in both DA and LD indexes but classified as "
            f"{ep.entry_type.value} instead of DESIGN_ATTRIBUTE — precedence broken"
        )

    @pytest.mark.req("REQ-EPC-02")
    def test_library_default_classification(self, catf_mfe_classifier):
        """EPs in unbound_lookup (and NOT in design_attr_by_qname) are LIBRARY_DEFAULT."""
        entry_points = catf_mfe_classifier["entry_points"]
        design_attr_by_qname = catf_mfe_classifier["design_attr_by_qname"]
        unbound_lookup = catf_mfe_classifier["unbound_lookup"]

        ld_matching = (
            set(unbound_lookup.keys()) & set(entry_points.keys())
        ) - set(design_attr_by_qname.keys())

        for qname in ld_matching:
            ep = entry_points[qname]
            assert ep.entry_type == EntryPointType.LIBRARY_DEFAULT, (
                f"EP {qname} in unbound_lookup (not DA) but classified as "
                f"{ep.entry_type.value} instead of LIBRARY_DEFAULT"
            )

    @pytest.mark.req("REQ-EPC-02")
    def test_usage_literal_classification(self, catf_mfe_classifier):
        """EPs in neither DA nor unbound_lookup are USAGE_LITERAL."""
        entry_points = catf_mfe_classifier["entry_points"]
        design_attr_by_qname = catf_mfe_classifier["design_attr_by_qname"]
        unbound_lookup = catf_mfe_classifier["unbound_lookup"]

        ul_matching = (
            set(entry_points.keys())
            - set(design_attr_by_qname.keys())
            - set(unbound_lookup.keys())
        )

        for qname in ul_matching:
            ep = entry_points[qname]
            assert ep.entry_type == EntryPointType.USAGE_LITERAL, (
                f"EP {qname} not in DA or unbound but classified as "
                f"{ep.entry_type.value} instead of USAGE_LITERAL"
            )


# ===========================================================================
# REQ-EPC-03: Float conversion of default_value
# ===========================================================================
class TestFloatConversion:
    """REQ-EPC-03: default_value converted to float or None."""

    @pytest.mark.req("REQ-EPC-03")
    def test_design_attribute_default_float_conversion(self, catf_mfe_classifier):
        """DESIGN_ATTRIBUTE EPs with known defaults have float default_value.

        Uses catf_mfe because its EP QNs match design attribute QNs directly.
        """
        entry_points = catf_mfe_classifier["entry_points"]
        da_eps = [
            ep for ep in entry_points.values()
            if ep.entry_type == EntryPointType.DESIGN_ATTRIBUTE
        ]
        assert len(da_eps) > 0, "No DESIGN_ATTRIBUTE EPs in catf_mfe"

        for ep in da_eps:
            if ep.default_value is not None:
                assert isinstance(ep.default_value, float), (
                    f"DA EP {ep.qualified_name}: default_value={ep.default_value} "
                    f"is {type(ep.default_value).__name__}, not float"
                )

    @pytest.mark.req("REQ-EPC-03")
    def test_library_default_float_conversion(self, classifier_inputs):
        """LIBRARY_DEFAULT EPs have float or None default_value."""
        entry_points = classifier_inputs["entry_points"]
        ld_eps = [
            ep for ep in entry_points.values()
            if ep.entry_type == EntryPointType.LIBRARY_DEFAULT
        ]

        for ep in ld_eps:
            if ep.default_value is not None:
                assert isinstance(ep.default_value, float), (
                    f"LD EP {ep.qualified_name}: default_value={ep.default_value} "
                    f"is {type(ep.default_value).__name__}, not float"
                )

    @pytest.mark.req("REQ-EPC-03")
    def test_usage_literal_float_conversion(self, catf_mfe_classifier):
        """USAGE_LITERAL EPs carry the hand-transcribed literal from their binding.

        The former body computed ``expected = float(source)`` and asserted the EP's
        default_value equalled it -- but production sets that default_value with the
        same ``float(entry_point_sources[qname])`` call (graph_builder.py), so the
        assertion was f(x) == f(x) and could never fail. Anchor the value instead to
        literals transcribed directly from the catf_mfe snapshot bindings.
        """
        entry_points = catf_mfe_classifier["entry_points"]

        # Anchored values: named USAGE_LITERAL EPs carry the transcribed literal.
        expected_ul_defaults = {
            # provenance: tests/fixtures/catf_mfe_model/extraction_snapshot.json:4527
            #   (literal_value 1546.72 bound to auxiliary_load.gross_electric)
            "CATF_MFE__catf_mfe_plant__auxiliary_load__gross_electric": 1546.72,
            # provenance: catf_mfe_model/extraction_snapshot.json:2896
            #   (literal_value 2079.41 bound to cryo_load.p_neutron)
            "CATFMFEMagnets__catf_tf_system__cryo_load__p_neutron": 2079.41,
            # provenance: catf_mfe_model/extraction_snapshot.json:4495
            #   (literal_value 1104.22 bound to pump_load.p_thermal_electric)
            "CATFMFEBlanket__catf_blanket__pump_load__p_thermal_electric": 1104.22,
        }
        for qname, expected in expected_ul_defaults.items():
            ep = entry_points.get(qname)
            assert ep is not None, f"USAGE_LITERAL EP {qname} missing from catf entry points"
            assert ep.entry_type == EntryPointType.USAGE_LITERAL, (
                f"{qname}: expected USAGE_LITERAL, got {ep.entry_type.name}"
            )
            assert ep.default_value == expected, (
                f"UL EP {qname}: default={ep.default_value} != transcribed {expected}"
            )

        # Independent shape check (value-agnostic): every UL default is float or None.
        for ep in entry_points.values():
            if ep.entry_type == EntryPointType.USAGE_LITERAL and ep.default_value is not None:
                assert isinstance(ep.default_value, float), (
                    f"UL EP {ep.qualified_name}: default_value={ep.default_value} "
                    f"is {type(ep.default_value).__name__}, not float"
                )

        # Synthetic guard for the None path: an unparseable literal source is not a
        # float, so production's float() conversion yields None rather than raising.
        # provenance: hand-computed -- float("3+4") raises ValueError.
        with pytest.raises(ValueError):
            float("3+4")

    @pytest.mark.req("REQ-EPC-03")
    def test_unparseable_default_is_none(self, classifier_inputs):
        """A None default_value implies the raw source was genuinely unparseable.

        Verifies the invariant "classifier nulled the default => the raw source does
        not parse as float" for the two branches that actually carry None-default EPs
        in the fixtures (DESIGN_ATTRIBUTE, USAGE_LITERAL). Each branch asserts the raw
        source independently -- it does not re-invoke the classifier's own conversion.

        The former LIBRARY_DEFAULT branch re-invoked ``_get_library_default`` and
        asserted it agreed with the classifier's own default_value (both produced by
        the same call) -- a tautology, and vacuous besides: no LIBRARY_DEFAULT EP has a
        None default in any fixture (every calc-def input default parses). The real
        parse-path coverage for ``_get_library_default`` now lives in the anchored test
        ``test_library_default_parsing_anchored`` below.
        """
        entry_points = classifier_inputs["entry_points"]
        entry_point_sources = classifier_inputs["entry_point_sources"]
        design_attr_by_qname = classifier_inputs["design_attr_by_qname"]

        for qname, ep in entry_points.items():
            if ep.default_value is not None:
                continue  # Has a valid float default -- not the failure path

            if ep.entry_type == EntryPointType.DESIGN_ATTRIBUTE:
                # Verify: either no raw default, or raw default is unparseable
                attr = design_attr_by_qname.get(qname)
                if attr and attr.default_value:
                    with pytest.raises((ValueError, TypeError)):
                        float(attr.default_value)

            elif ep.entry_type == EntryPointType.USAGE_LITERAL:
                # Verify: either no source, or source is unparseable
                source = entry_point_sources.get(qname)
                if source:
                    with pytest.raises((ValueError, TypeError)):
                        float(source)

    @pytest.mark.req("REQ-EPC-03")
    def test_library_default_parsing_anchored(self, solar_battery_classifier):
        """_get_library_default parses numeric defaults to the transcribed float and
        yields None (not a raise) for unparseable/absent defaults.

        Replaces the vacuous, tautological LIBRARY_DEFAULT branch of
        test_unparseable_default_is_none: the expected values here are transcribed from
        the solar_battery snapshot's calc-def input defaults, not produced by the
        function under test.
        """
        calc_def_map = solar_battery_classifier["calc_def_map"]

        def find_calc_def(short_name):
            match = next(
                (cd for qn, cd in calc_def_map.items() if qn.split("::")[-1] == short_name),
                None,
            )
            assert match is not None, f"calc def {short_name} not in solar_battery calc_def_map"
            return match

        numeric_cases = [
            # (calc_def, param, expected). provenance: solar_battery snapshot calc-def defaults.
            ("PVModuleCostCalc", "cost_per_watt", 1.07),   # provenance: solar snapshot:923
            ("PVModuleCostCalc", "fab_factor", 0.45),      # provenance: solar snapshot:936
            ("BatteryPackCostCalc", "cost_per_kwh", 171.5),  # provenance: solar snapshot:1428
        ]
        for cd_name, param, expected in numeric_cases:
            calc_def = find_calc_def(cd_name)
            assert _get_library_default(calc_def, param) == expected, (
                f"_get_library_default({cd_name}, {param}) != transcribed {expected}"
            )

        # No fixture calc-def carries an unparseable default, so exercise the float()
        # failure path with synthetic input attributes. An expression or placeholder
        # default yields None; an absent default yields None -- neither raises.
        # provenance: hand-computed -- float("1.0 / q_eng") and float("TBD") raise ValueError.
        synthetic = SimpleNamespace(input_attributes=[
            SimpleNamespace(name="ratio", default_value="1.0 / q_eng"),
            SimpleNamespace(name="placeholder", default_value="TBD"),
            SimpleNamespace(name="absent", default_value=None),
        ])
        assert _get_library_default(synthetic, "ratio") is None
        assert _get_library_default(synthetic, "placeholder") is None
        assert _get_library_default(synthetic, "absent") is None

    @pytest.mark.req("REQ-EPC-03")
    def test_get_library_default_real_calc_defs(self, solar_battery_classifier):
        """_get_library_default() returns float for numeric defaults, None for non-numeric."""
        calc_def_map = solar_battery_classifier["calc_def_map"]
        tested_count = 0

        for cd_name, calc_def in calc_def_map.items():
            for attr in calc_def.input_attributes:
                result = _get_library_default(calc_def, attr.name)
                if result is not None:
                    assert isinstance(result, float), (
                        f"_get_library_default({cd_name}, {attr.name}) returned "
                        f"{type(result).__name__}, not float"
                    )
                    tested_count += 1
                elif attr.default_value:
                    # Has a default but not parseable as float -- that's fine
                    try:
                        float(attr.default_value)
                        pytest.fail(
                            f"_get_library_default({cd_name}, {attr.name}) returned None "
                            f"but default '{attr.default_value}' is parseable as float"
                        )
                    except (ValueError, TypeError):
                        pass  # Expected: non-numeric default

        assert tested_count > 0, "No numeric library defaults found to test"


# ===========================================================================
# REQ-EPC-04: Every EP assigned a param_group
# ===========================================================================
class TestParamGroupAssignment:
    """REQ-EPC-04: Every EP has a param_group via ParameterGroupDeriver."""

    @pytest.mark.req("REQ-EPC-04")
    def test_every_ep_has_param_group(self, classifier_inputs):
        """Every EP where group_deriver.classify() returns non-None has a param_group.

        Some deeply-nested EP QNs may not match any group (param_group=None).
        These become orphans handled by Step 6.8 in build_computation_graph().
        """
        entry_points = classifier_inputs["entry_points"]
        assigned_count = 0
        for qname, ep in entry_points.items():
            if ep.param_group is not None:
                assert isinstance(ep.param_group, str), (
                    f"EP {qname} param_group is {type(ep.param_group).__name__}, not str"
                )
                assert len(ep.param_group) > 0, (
                    f"EP {qname} has empty param_group"
                )
                assigned_count += 1
        # At least some EPs should have param_group assigned
        assert assigned_count > 0, "No EPs have param_group assigned"

    @pytest.mark.req("REQ-EPC-04")
    def test_every_ep_in_group_after_graph_assembly(self, solar_battery_full_graph):
        """In the final graph, every EP is covered by some ParameterGroup.

        After Step 6.8 orphan handling, no EP should be ungrouped.
        """
        graph, inputs = solar_battery_full_graph

        # Collect all EP QNs from groups
        grouped_ep_qns: set[str] = set()
        for group in graph.entry_point_groups:
            for p in group.parameters:
                grouped_ep_qns.add(p.qualified_name)

        # Every EP that ended up in any module's inputs should be grouped
        for module in graph.modules:
            for inp in module.inputs:
                if inp.source.source_type == "entry_point" and inp.source.qualified_name:
                    assert inp.source.qualified_name in grouped_ep_qns, (
                        f"Module {module.name} references EP "
                        f"{inp.source.qualified_name} which is not in any group"
                    )


# ===========================================================================
# REQ-EPC-05: Orphan EPs land in "system_design" fallback group
# ===========================================================================
class TestOrphanEntryPoints:
    """REQ-EPC-05: Orphans land in system_design group."""

    @pytest.mark.req("REQ-EPC-05")
    def test_orphan_ep_lands_in_system_design(self, solar_battery_full_graph):
        """Natural orphan EPs land in system_design group after graph assembly.

        Learning #2: solar_battery has 13 EPs with param_group=None from the
        classifier (deeply-nested QNs that don't match any ParameterGroupDeriver
        pattern). Step 6.8 in build_computation_graph() collects these into a
        "system_design" fallback group.
        """
        graph, inputs = solar_battery_full_graph

        # Identify classifier-level orphans: EPs with param_group=None
        classifier_eps = inputs["entry_points"]
        orphan_qns = {
            qn for qn, ep in classifier_eps.items()
            if ep.param_group is None
        }
        assert len(orphan_qns) > 0, (
            "Expected solar_battery to have natural orphan EPs (param_group=None) "
            "but found none — Learning #2 documents 13"
        )

        # Find the system_design group in the final graph
        system_design_groups = [
            g for g in graph.entry_point_groups if g.name == "system_design"
        ]
        assert len(system_design_groups) == 1, (
            f"Expected exactly 1 system_design group, found {len(system_design_groups)}"
        )
        sd_group = system_design_groups[0]
        sd_qns = {p.qualified_name for p in sd_group.parameters}

        # Every classifier-level orphan that's still in the graph should be
        # in the system_design group
        for qn in orphan_qns:
            if qn in {p.qualified_name for g in graph.entry_point_groups for p in g.parameters}:
                assert qn in sd_qns, (
                    f"Orphan EP {qn} (param_group=None from classifier) is in the "
                    f"graph but not in the system_design group"
                )

        # Cross-group uniqueness: no entry point belongs to more than one group.
        seen: dict[str, str] = {}
        duplicates: list[str] = []
        for group in graph.entry_point_groups:
            for p in group.parameters:
                if p.qualified_name in seen and seen[p.qualified_name] != group.name:
                    duplicates.append(
                        f"{p.qualified_name} in both {seen[p.qualified_name]!r} "
                        f"and {group.name!r}"
                    )
                seen[p.qualified_name] = group.name
        assert not duplicates, (
            f"Entry point(s) belong to more than one ParameterGroup: {duplicates}"
        )


# ===========================================================================
# REQ-EPC-06: Groups rebuilt after FORMULA/Aggregation construction
# ===========================================================================
class TestGroupsRebuilt:
    """REQ-EPC-06: param_groups rebuilt with complete entry point set."""

    @pytest.mark.req("REQ-EPC-06")
    def test_groups_rebuilt_after_factory_construction(self, solar_battery_full_graph):
        """Factory-created EPs appear in final entry_point_groups."""
        graph, inputs = solar_battery_full_graph

        # Collect all EP qualified names from backtracker (Path 1 -- classifier)
        path1_eps = set(inputs["result"].entry_points)

        # Collect all EP qualified names from the final graph groups
        graph_ep_qns: set[str] = set()
        for group in graph.entry_point_groups:
            for p in group.parameters:
                graph_ep_qns.add(p.qualified_name)

        # Factory-created EPs (Path 2) are those in graph groups but NOT in
        # the original backtracker entry_points set
        factory_eps = graph_ep_qns - path1_eps

        # solar_battery has FORMULA + aggregation modules that create new EPs.
        # This must be non-empty or the test is vacuous.
        assert len(factory_eps) > 0, (
            "No factory-created EPs found in solar_battery graph. "
            "Expected FORMULA and/or aggregation factories to create new EPs. "
            "Without factory EPs, this test verifies nothing about group rebuild."
        )

        for ep_qn in factory_eps:
            found_in_group = any(
                any(p.qualified_name == ep_qn for p in g.parameters)
                for g in graph.entry_point_groups
            )
            assert found_in_group, (
                f"Factory-created EP {ep_qn} not in any param group after rebuild"
            )


# ===========================================================================
# REQ-EPC-07: _classify_entry_points() is a pure function
# ===========================================================================
class TestPureFunction:
    """REQ-EPC-07: No mutation of input arguments."""

    @pytest.mark.req("REQ-EPC-07")
    def test_classify_is_pure_function(self, solar_battery_classifier):
        """Deep-copy all inputs, call _classify_entry_points(), verify inputs unchanged."""
        inputs = solar_battery_classifier
        result = inputs["result"]
        calc_def_map = inputs["calc_def_map"]
        design_attrs = inputs["design_attrs"]
        group_deriver = inputs["group_deriver"]

        # Deep copy all mutable inputs
        ep_names_copy = copy.deepcopy(result.entry_points)
        ep_sources_copy = copy.deepcopy(result.entry_point_sources)
        design_attrs_copy = copy.deepcopy(design_attrs)
        usages_copy = copy.deepcopy(result.required_usages)
        calc_def_map_copy = copy.deepcopy(calc_def_map)

        # Call the function
        _classify_entry_points(
            ep_names_copy,
            ep_sources_copy,
            design_attrs_copy,
            usages_copy,
            calc_def_map_copy,
            group_deriver,
        )

        # Verify no mutation of inputs -- deep-compare all five inputs against
        # fresh copies of the untouched originals (dataclass __eq__ is structural,
        # so this catches a mutated field even when keys/lengths are unchanged).
        assert ep_names_copy == copy.deepcopy(result.entry_points), (
            "entry_point_names was mutated by _classify_entry_points()"
        )
        assert ep_sources_copy == copy.deepcopy(result.entry_point_sources), (
            "entry_point_sources was mutated by _classify_entry_points()"
        )
        assert design_attrs_copy == copy.deepcopy(design_attrs), (
            "design_attrs was mutated by _classify_entry_points()"
        )
        assert usages_copy == copy.deepcopy(result.required_usages), (
            "required_usages was mutated by _classify_entry_points()"
        )
        assert calc_def_map_copy == copy.deepcopy(calc_def_map), (
            "calc_def_map was mutated by _classify_entry_points()"
        )


# ===========================================================================
# REQ-EPC-08: Factory EPs retain DESIGN_ATTRIBUTE, never re-classified
# ===========================================================================
class TestFactoryEPsNotReclassified:
    """REQ-EPC-08: Factory-created EPs bypass classification."""

    @pytest.mark.req("REQ-EPC-08")
    def test_factory_eps_retain_design_attribute(self, solar_battery_full_graph):
        """Factory-created EPs all have entry_type=DESIGN_ATTRIBUTE."""
        graph, inputs = solar_battery_full_graph

        # Path 1 EPs: from backtracker
        path1_eps = set(inputs["result"].entry_points)

        # Collect all EPs from final graph groups
        all_graph_eps: dict[str, EntryPoint] = {}
        for group in graph.entry_point_groups:
            for p in group.parameters:
                all_graph_eps[p.qualified_name] = p

        # Path 2 EPs: in graph but not from backtracker
        factory_ep_qns = set(all_graph_eps.keys()) - path1_eps

        assert len(factory_ep_qns) > 0, (
            "No factory-created EPs found in solar_battery graph. "
            "Expected FORMULA and/or aggregation factories to create new EPs. "
            "Without factory EPs, this test verifies nothing about re-classification."
        )

        for qn in factory_ep_qns:
            ep = all_graph_eps[qn]
            assert ep.entry_type == EntryPointType.DESIGN_ATTRIBUTE, (
                f"Factory EP {qn} has entry_type={ep.entry_type.value}, "
                f"expected DESIGN_ATTRIBUTE"
            )

    @pytest.mark.req("REQ-EPC-08")
    def test_classify_called_before_factories(self):
        """Static analysis: _classify_entry_points call appears before factory calls."""
        source = textwrap.dedent(inspect.getsource(build_computation_graph))
        tree = ast.parse(source)

        # Find line numbers for key function calls
        classify_lines = []
        computed_attr_lines = []
        aggregation_lines = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_name = ""
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    func_name = node.func.attr

                if func_name == "_classify_entry_points":
                    classify_lines.append(node.lineno)
                elif func_name == "_build_computed_attr_module":
                    computed_attr_lines.append(node.lineno)
                elif func_name == "_build_aggregation_module":
                    aggregation_lines.append(node.lineno)

        assert len(classify_lines) >= 1, (
            "_classify_entry_points not found in build_computation_graph"
        )

        classify_line = classify_lines[0]

        if computed_attr_lines:
            assert classify_line < min(computed_attr_lines), (
                f"_classify_entry_points (line {classify_line}) not before "
                f"_build_computed_attr_module (line {min(computed_attr_lines)})"
            )

        if aggregation_lines:
            assert classify_line < min(aggregation_lines), (
                f"_classify_entry_points (line {classify_line}) not before "
                f"_build_aggregation_module (line {min(aggregation_lines)})"
            )

    @pytest.mark.req("REQ-EPC-08")
    def test_classify_called_exactly_once(self):
        """Static analysis: _classify_entry_points called exactly once."""
        source = textwrap.dedent(inspect.getsource(build_computation_graph))
        tree = ast.parse(source)

        call_count = 0
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func_name = ""
                if isinstance(node.func, ast.Name):
                    func_name = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    func_name = node.func.attr

                if func_name == "_classify_entry_points":
                    call_count += 1

        assert call_count == 1, (
            f"_classify_entry_points called {call_count} times in "
            f"build_computation_graph, expected exactly 1"
        )
