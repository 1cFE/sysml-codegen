"""Load extraction snapshots from JSON and reconstruct typed dataclass instances.

Reverses the serialization performed by snapshot_serializer.py:
- str → Path for source_file fields
- str → Enum for binding_type, redefinition_type, classification, compilability
- None AST fields remain None (documented as "not available from snapshot")
- tuple-encoded dict keys → tuple
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agentic_mbse.sysml.types import BindingType, ExpressionRef

from sysml_codegen.core.models import ChannelAlias
from sysml_codegen.extraction.data_models import (
    AggregationExpressionData,
    AttributeInfo,
    CalculationDefinitionData,
    ComputedAttributeClassification,
    ComputedAttributeData,
    ConstraintInfo,
    HierarchyExtractionResult,
    LocalTerm,
    MultiplicityData,
    RedefinitionData,
    RedefinitionType,
    ScopedAggregationData,
    SingletonTerm,
    SumTerm,
)
from sysml_codegen.extraction.expression_compiler import Compilability
from sysml_codegen.extraction.usage_extractor import BindingInfo, CalcUsageData
from sysml_codegen.analysis.parameter_groups import DesignAttributeData

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


def load_extraction_snapshot(model_name: str) -> dict[str, Any]:
    """Load a model's extraction snapshot and reconstruct typed instances.

    Args:
        model_name: Name of the fixture model (e.g., "solar_battery_model").

    Returns:
        Dict with typed instances:
            calc_defs: list[CalculationDefinitionData]
            calc_usages: list[CalcUsageData]
            design_attributes: dict[str, list[DesignAttributeData]]
            hierarchy_data: HierarchyExtractionResult
            aggregation_expressions: list[ScopedAggregationData]
            computed_attributes: list[ComputedAttributeData]
            channel_aliases: list[ChannelAlias]
    """
    snapshot_path = FIXTURES_DIR / model_name / "extraction_snapshot.json"
    raw = json.loads(snapshot_path.read_text())

    return {
        "model_name": raw["model_name"],
        "captured_at": raw["captured_at"],
        "calc_defs": [_deserialize_calc_def(d) for d in raw["calc_defs"]],
        "calc_usages": [_deserialize_calc_usage(d) for d in raw["calc_usages"]],
        "design_attributes": {
            k: [_deserialize_design_attribute(da) for da in v]
            for k, v in raw["design_attributes"].items()
        },
        "hierarchy_data": _deserialize_hierarchy_result(raw["hierarchy_data"]),
        "aggregation_expressions": [
            _deserialize_scoped_aggregation(d) for d in raw["aggregation_expressions"]
        ],
        "computed_attributes": [
            _deserialize_computed_attribute(d) for d in raw["computed_attributes"]
        ],
        "channel_aliases": [
            ChannelAlias.model_validate(d) for d in raw["channel_aliases"]
        ],
    }


# --- Individual deserializers ---


def _deserialize_attribute_info(d: dict) -> AttributeInfo:
    """Reconstruct an AttributeInfo from a serialized dict."""
    return AttributeInfo(
        name=d["name"],
        sysml_type=d.get("sysml_type"),
        default_value=d.get("default_value"),
        binding_type=BindingType(d["binding_type"]) if d.get("binding_type") else BindingType.UNBOUND,
        is_input=d.get("is_input", False),
        is_output=d.get("is_output", False),
        python_type=d.get("python_type", "Any"),
        description=d.get("description", ""),
        unit=d.get("unit"),
        source_line=d.get("source_line", 0),
        is_optional=d.get("is_optional", False),
    )


def _deserialize_constraint_info(d: dict) -> ConstraintInfo:
    """Reconstruct a ConstraintInfo from a serialized dict."""
    return ConstraintInfo(
        expression=d["expression"],
        description=d["description"],
        affected_attributes=d["affected_attributes"],
        constraint_type=d["constraint_type"],
        source_line=d.get("source_line", 0),
    )


def _deserialize_calc_def(d: dict) -> CalculationDefinitionData:
    """Reconstruct a CalculationDefinitionData from a serialized dict."""
    return CalculationDefinitionData(
        name=d["name"],
        qualified_name=d["qualified_name"],
        doc_comment=d["doc_comment"],
        calc_expressions=d["calc_expressions"],
        input_attributes=[_deserialize_attribute_info(a) for a in d["input_attributes"]],
        output_attributes=[_deserialize_attribute_info(a) for a in d["output_attributes"]],
        references=d["references"],
        source_file=Path(d["source_file"]),
        source_line=d.get("source_line", 0),
        source_hash=d.get("source_hash", ""),
        output_expression_asts={},  # AST not available from snapshot
        all_member_names=set(d.get("all_member_names", [])),
        member_expressions={},  # AST not available from snapshot
    )


def _deserialize_binding_info(d: dict) -> BindingInfo:
    """Reconstruct a BindingInfo from a serialized dict."""
    return BindingInfo(
        param_name=d["param_name"],
        source_path=d.get("source_path"),
        binding_type=BindingType(d["binding_type"]),
        is_cross_file=d.get("is_cross_file", False),
        raw_expression=d.get("raw_expression", ""),
        source_instance_elem=None,  # AST not available from snapshot
        source_attribute_elem=None,  # AST not available from snapshot
        literal_value=d.get("literal_value"),
        expression_ast=None,  # AST not available from snapshot
    )


def _deserialize_calc_usage(d: dict) -> CalcUsageData:
    """Reconstruct a CalcUsageData from a serialized dict."""
    return CalcUsageData(
        instance_name=d["instance_name"],
        calc_def_name=d["calc_def_name"],
        calc_def_qualified_name=d["calc_def_qualified_name"],
        module_type=d["module_type"],
        bindings=[_deserialize_binding_info(b) for b in d["bindings"]],
        unbound_params=d.get("unbound_params", []),
        source_file=Path(d["source_file"]),
        source_line=d.get("source_line", 0),
        parent_part_path=d.get("parent_part_path", ""),
        qualified_name=d.get("qualified_name", ""),
        is_template=d.get("is_template", False),
        owning_part_def_qn=d.get("owning_part_def_qn"),
    )


def _deserialize_design_attribute(d: dict) -> DesignAttributeData:
    """Reconstruct a DesignAttributeData from a serialized dict."""
    return DesignAttributeData(
        name=d["name"],
        sysml_type=d["sysml_type"],
        default_value=d.get("default_value"),
        unit=d.get("unit"),
        source_file=Path(d["source_file"]),
        source_line=d.get("source_line", 0),
        parent_part=d["parent_part"],
        qualified_name=d.get("qualified_name", ""),
    )


def _deserialize_redefinition_data(d: dict) -> RedefinitionData:
    """Reconstruct a RedefinitionData from a serialized dict."""
    return RedefinitionData(
        owning_part_qn=d["owning_part_qn"],
        attribute_name=d["attribute_name"],
        redefinition_type=RedefinitionType(d["redefinition_type"]),
        literal_value=d.get("literal_value"),
        source_path=d.get("source_path"),
        expression_ast=None,  # AST not available from snapshot
        expression_text=d.get("expression_text", ""),
        target_path=d.get("target_path", []),
        is_deep_path=d.get("is_deep_path", False),
        source_file=Path(d.get("source_file", "unknown")),
        source_line=d.get("source_line", 0),
    )


def _deserialize_multiplicity_data(d: dict) -> MultiplicityData:
    """Reconstruct a MultiplicityData from a serialized dict."""
    return MultiplicityData(
        part_usage_name=d["part_usage_name"],
        owning_part_def_qn=d["owning_part_def_qn"],
        count=d.get("count"),
        count_attribute_name=d.get("count_attribute_name"),
        default_value=d.get("default_value"),
    )


def _deserialize_sum_term(d: dict) -> SumTerm:
    return SumTerm(
        part_usage_name=d["part_usage_name"],
        attribute_name=d["attribute_name"],
        multiplicity_attr=d.get("multiplicity_attr"),
        multiplicity_count=d.get("multiplicity_count"),
    )


def _deserialize_singleton_term(d: dict) -> SingletonTerm:
    return SingletonTerm(source_path=d["source_path"])


def _deserialize_local_term(d: dict) -> LocalTerm:
    return LocalTerm(attribute_name=d["attribute_name"])


def _deserialize_aggregation_expression(d: dict) -> AggregationExpressionData:
    """Reconstruct an AggregationExpressionData from a serialized dict."""
    return AggregationExpressionData(
        owning_part_qn=d["owning_part_qn"],
        owning_part_name=d["owning_part_name"],
        attribute_name=d["attribute_name"],
        raw_expression_text=d["raw_expression_text"],
        transformed_expression=d["transformed_expression"],
        sum_terms=[_deserialize_sum_term(t) for t in d["sum_terms"]],
        singleton_terms=[_deserialize_singleton_term(t) for t in d["singleton_terms"]],
        local_terms=[_deserialize_local_term(t) for t in d["local_terms"]],
        input_channels=d["input_channels"],
        entry_points=d["entry_points"],
        compilability=Compilability(d["compilability"]) if d.get("compilability") else Compilability.UNKNOWN,
        has_unsupported_nodes=d.get("has_unsupported_nodes", False),
        aliases=d.get("aliases", []),
        source_file=Path(d.get("source_file", "unknown")),
        source_line=d.get("source_line", 0),
    )


def _deserialize_hierarchy_result(d: dict) -> HierarchyExtractionResult:
    """Reconstruct a HierarchyExtractionResult from a serialized dict."""
    # usage_type_map has tuple keys serialized as JSON arrays
    usage_type_map: dict[tuple[str, str], str] = {}
    for key_str, value in d.get("usage_type_map", {}).items():
        try:
            parts = json.loads(key_str)
            usage_type_map[(parts[0], parts[1])] = value
        except (json.JSONDecodeError, IndexError):
            pass

    # part_usage_names has set values serialized as sorted lists
    part_usage_names: dict[str, set[str]] = {
        k: set(v) for k, v in d.get("part_usage_names", {}).items()
    }

    return HierarchyExtractionResult(
        redefinitions=[_deserialize_redefinition_data(r) for r in d["redefinitions"]],
        design_overrides=[_deserialize_redefinition_data(r) for r in d["design_overrides"]],
        multiplicities=[_deserialize_multiplicity_data(m) for m in d["multiplicities"]],
        aggregation_expressions=[
            _deserialize_aggregation_expression(a) for a in d["aggregation_expressions"]
        ],
        warnings=d["warnings"],
        part_usage_names=part_usage_names,
        usage_type_map=usage_type_map,
    )


def _deserialize_expression_ref(d: dict) -> ExpressionRef:
    """Reconstruct an ExpressionRef from a serialized dict."""
    return ExpressionRef(
        name=d["name"],
        qualified_name=d.get("qualified_name", ""),
        document_path=d.get("document_path"),
        element=None,  # AST not available from snapshot
    )


def _deserialize_scoped_aggregation(d: dict) -> ScopedAggregationData:
    """Reconstruct a ScopedAggregationData from a serialized dict."""
    return ScopedAggregationData(
        expression=_deserialize_aggregation_expression(d["expression"]),
        instance_path=d["instance_path"],
    )


def _deserialize_computed_attribute(d: dict) -> ComputedAttributeData:
    """Reconstruct a ComputedAttributeData from a serialized dict."""
    return ComputedAttributeData(
        name=d["name"],
        python_name=d["python_name"],
        owning_part_name=d["owning_part_name"],
        owning_part_qualified_name=d["owning_part_qualified_name"],
        expression_ast=None,  # AST not available from snapshot
        expression_text=d["expression_text"],
        references=[_deserialize_expression_ref(r) for r in d["references"]],
        classification=ComputedAttributeClassification(d["classification"]),
        compilability=Compilability(d["compilability"]) if d.get("compilability") else Compilability.UNKNOWN,
        compiled_expression=d.get("compiled_expression"),
        is_on_part_definition=d.get("is_on_part_definition", False),
        source_file=Path(d.get("source_file", "unknown")),
        source_line=d.get("source_line", 0),
    )
