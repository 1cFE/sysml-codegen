"""Conformance tests for extraction snapshot round-trip.

Validates that extraction snapshots:
1. Exist and load without error
2. Reconstruct typed dataclass instances
3. Have expected fields populated
4. Preserve enum values, path types, and set types correctly

REQ-SNAP-01: Snapshot files exist and deserialize without error.
REQ-SNAP-02: CalculationDefinitionData fields populated.
REQ-SNAP-03: CalcUsageData bindings have typed BindingType.
REQ-SNAP-04: HierarchyExtractionResult round-trips with tuple keys.
REQ-SNAP-05: AST fields are None (not serialized Java objects).
REQ-SNAP-06: Path fields are Path instances, not strings.
REQ-SNAP-07: Enum fields are typed enum instances, not raw strings.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from sysml_codegen.snapshot import load_extraction_snapshot
from tests.conftest import snapshot_fixture

from agentic_mbse.sysml.types import BindingType
from sysml_codegen.extraction.data_models import (
    AggregationExpressionData,
    CalculationDefinitionData,
    ComputedAttributeClassification,
    ComputedAttributeData,
    HierarchyExtractionResult,
    RedefinitionData,
    RedefinitionType,
    ScopedAggregationData,
)
from sysml_codegen.extraction.expression_compiler import Compilability
from sysml_codegen.extraction.usage_extractor import BindingInfo, CalcUsageData
from sysml_codegen.core.models import ChannelAlias

MODELS = [
    "sample_model",
    "solar_battery_model",
    "catf_mfe_model",
    "attr_expr_probe",
    "chain_spike_model",
    "issue22_model",
    "return_styles",
]


@pytest.mark.parametrize("model_name", MODELS)
class TestExtractionSnapshotRoundTrip:
    """Round-trip tests for extraction snapshots."""

    @pytest.mark.req(id="REQ-SNAP-01")
    def test_snapshot_loads(self, model_name: str) -> None:
        """Snapshot file exists and deserializes without error."""
        snapshot = load_extraction_snapshot(snapshot_fixture(model_name))
        assert snapshot is not None
        assert snapshot["model_name"] == model_name

    @pytest.mark.req(id="REQ-SNAP-02")
    def test_calc_defs_have_fields(self, model_name: str) -> None:
        """Every CalculationDefinitionData has required fields populated."""
        snapshot = load_extraction_snapshot(snapshot_fixture(model_name))
        for cd in snapshot["calc_defs"]:
            assert isinstance(cd, CalculationDefinitionData)
            assert cd.name
            assert cd.qualified_name
            assert cd.source_file
            assert isinstance(cd.input_attributes, list)
            assert isinstance(cd.output_attributes, list)

    @pytest.mark.req(id="REQ-SNAP-03")
    def test_calc_usages_have_bindings(self, model_name: str) -> None:
        """Every CalcUsageData has typed bindings."""
        snapshot = load_extraction_snapshot(snapshot_fixture(model_name))
        for cu in snapshot["calc_usages"]:
            assert isinstance(cu, CalcUsageData)
            assert cu.instance_name
            assert cu.calc_def_name
            for b in cu.bindings:
                assert isinstance(b, BindingInfo)
                assert isinstance(b.binding_type, BindingType)

    @pytest.mark.req(id="REQ-SNAP-04")
    def test_hierarchy_data_round_trips(self, model_name: str) -> None:
        """HierarchyExtractionResult round-trips with correct types."""
        snapshot = load_extraction_snapshot(snapshot_fixture(model_name))
        hd = snapshot["hierarchy_data"]
        assert isinstance(hd, HierarchyExtractionResult)

        for r in hd.redefinitions:
            assert isinstance(r, RedefinitionData)
            assert isinstance(r.redefinition_type, RedefinitionType)

        # usage_type_map keys are tuples
        for key in hd.usage_type_map:
            assert isinstance(key, tuple), f"Expected tuple key, got {type(key)}: {key}"
            assert len(key) == 2

        # part_usage_names values are sets
        for value in hd.part_usage_names.values():
            assert isinstance(value, set), f"Expected set, got {type(value)}"

    @pytest.mark.req(id="REQ-SNAP-05")
    def test_ast_fields_are_none(self, model_name: str) -> None:
        """AST fields are None (not serialized Java objects)."""
        snapshot = load_extraction_snapshot(snapshot_fixture(model_name))

        for cd in snapshot["calc_defs"]:
            assert cd.output_expression_asts == {}, \
                f"output_expression_asts should be empty dict, got {cd.output_expression_asts}"
            assert cd.member_expressions == {}, \
                f"member_expressions should be empty dict, got {cd.member_expressions}"

        for cu in snapshot["calc_usages"]:
            for b in cu.bindings:
                assert b.source_instance_elem is None
                assert b.source_attribute_elem is None
                assert b.expression_ast is None

        for ca in snapshot["computed_attributes"]:
            assert ca.expression_ast is None

    @pytest.mark.req(id="REQ-SNAP-06")
    def test_path_fields_are_paths(self, model_name: str) -> None:
        """Path fields are Path instances, not strings."""
        snapshot = load_extraction_snapshot(snapshot_fixture(model_name))

        for cd in snapshot["calc_defs"]:
            assert isinstance(cd.source_file, Path), \
                f"source_file should be Path, got {type(cd.source_file)}"

        for cu in snapshot["calc_usages"]:
            assert isinstance(cu.source_file, Path)

    @pytest.mark.req(id="REQ-SNAP-07")
    def test_enum_fields_are_typed(self, model_name: str) -> None:
        """Enum fields are typed enum instances, not raw strings."""
        snapshot = load_extraction_snapshot(snapshot_fixture(model_name))

        for cu in snapshot["calc_usages"]:
            for b in cu.bindings:
                assert isinstance(b.binding_type, BindingType), \
                    f"binding_type should be BindingType, got {type(b.binding_type)}: {b.binding_type}"

        for r in snapshot["hierarchy_data"].redefinitions:
            assert isinstance(r.redefinition_type, RedefinitionType)

        for ca in snapshot["computed_attributes"]:
            assert isinstance(ca.classification, ComputedAttributeClassification)
            assert isinstance(ca.compilability, Compilability)

    @pytest.mark.req(id="REQ-SNAP-02")
    def test_aggregation_expressions_round_trip(self, model_name: str) -> None:
        """ScopedAggregationData round-trips with correct types."""
        snapshot = load_extraction_snapshot(snapshot_fixture(model_name))
        for sa in snapshot["aggregation_expressions"]:
            assert isinstance(sa, ScopedAggregationData)
            assert isinstance(sa.expression, AggregationExpressionData)
            assert sa.instance_path  # non-empty

    @pytest.mark.req(id="REQ-SNAP-01")
    def test_channel_aliases_round_trip(self, model_name: str) -> None:
        """ChannelAlias round-trips through Pydantic validation."""
        snapshot = load_extraction_snapshot(snapshot_fixture(model_name))
        for ca in snapshot["channel_aliases"]:
            assert isinstance(ca, ChannelAlias)
            assert ca.alias_name
            assert ca.canonical_name
            assert ca.source in ("redefinition", "expose_pure", "design_override")
