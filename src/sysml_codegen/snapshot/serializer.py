"""Serialize extraction output to JSON-safe dicts.

Handles the serialization boundary between live SysIDE objects (py4j Java bridges)
and JSON-safe Python types. Non-serializable AST fields are nullified; computed
property values are preserved as explicit fields.

Serialization rules:
- dataclass fields → recursive dict conversion
- Pydantic BaseModel → .model_dump()
- Path → str (relative to fixtures dir when possible)
- Enum → .value
- set → sorted list
- AST objects (Any-typed Java bridges) → None
- BindingInfo.source_instance_elem/source_attribute_elem → None,
  but source_instance_name/source_attribute_name preserved as explicit keys
"""

from __future__ import annotations

import dataclasses
import datetime
import json
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from sysml_codegen.extraction.constraint_report import (
    ConstraintManifestEntry,
    manifest_to_records,
)
from sysml_codegen.snapshot import SNAPSHOT_FORMAT_VERSION

# Fields that hold live SysIDE Java objects — always nullify.
_AST_FIELDS = frozenset({
    "output_expression_asts",
    "member_expressions",
    "expression_ast",
    "source_instance_elem",
    "source_attribute_elem",
    "raw_element",
})


def serialize_extraction_snapshot(
    *,
    model_name: str,
    calc_defs: list[Any],
    calc_usages: list[Any],
    design_attributes: dict[Path, list[Any]],
    hierarchy_data: Any,
    aggregation_expressions: list[Any],
    computed_attributes: list[Any],
    channel_aliases: list[Any],
    compilation_results: dict[str, Any] | None = None,
    constraint_manifest: list[ConstraintManifestEntry] | None = None,
    output_dir: Path | None = None,
) -> dict[str, Any]:
    """Serialize full extraction output to a versioned JSON-safe dict.

    Args:
        model_name: Name of the fixture model.
        calc_defs: List of CalculationDefinitionData.
        calc_usages: List of CalcUsageData.
        design_attributes: Design attributes by source file path.
        hierarchy_data: HierarchyExtractionResult.
        aggregation_expressions: List of ScopedAggregationData.
        computed_attributes: List of ComputedAttributeData.
        channel_aliases: List of ChannelAlias.
        compilation_results: dict[str, CalcDefCompilationResult] keyed by
            calc_def.name (SC-10). Absent/None → empty block; loader degrades.
        constraint_manifest: model-wide dropped-constraint manifest (Item 4).
            Absent/None → empty ``dropped_constraints`` array.
        output_dir: If provided, Path fields (and Path dict keys) are made
            relative to this dir — the snapshot's own directory (D1). The loader
            re-absolutizes against the same anchor, so the round-trip is exact.

    Returns:
        JSON-safe dict suitable for json.dumps(). The top-level
        ``snapshot_format_version`` gates loading (INV-2).
    """
    return {
        "snapshot_format_version": SNAPSHOT_FORMAT_VERSION,
        "model_name": model_name,
        "captured_at": datetime.datetime.now(datetime.UTC).isoformat(),
        "compilation_results": {
            str(name): _serialize_value(cr, output_dir)
            for name, cr in (compilation_results or {}).items()
        },
        "calc_defs": [_serialize_value(cd, output_dir) for cd in calc_defs],
        "calc_usages": [_serialize_value(cu, output_dir) for cu in calc_usages],
        "design_attributes": {
            str(k): [_serialize_value(da, output_dir) for da in v]
            for k, v in design_attributes.items()
        },
        "hierarchy_data": _serialize_value(hierarchy_data, output_dir),
        "aggregation_expressions": [
            _serialize_value(sa, output_dir) for sa in aggregation_expressions
        ],
        "computed_attributes": [
            _serialize_value(ca, output_dir) for ca in computed_attributes
        ],
        "channel_aliases": [_serialize_value(ca, output_dir) for ca in channel_aliases],
        # Model-wide dropped-constraint manifest, stable enum tokens, order
        # preserved (D2/D8/INV-G). The from-snapshot path replays the drop report
        # from this. Empty list for constraint-free models.
        "dropped_constraints": manifest_to_records(constraint_manifest or []),
    }


def _serialize_value(obj: Any, output_dir: Path | None) -> Any:
    """Recursively serialize a value to a JSON-safe type."""
    if obj is None:
        return None

    # Primitives
    if isinstance(obj, (str, int, float, bool)):
        return obj

    # Enum → .value
    if isinstance(obj, Enum):
        return obj.value

    # Path → str (relative if possible)
    if isinstance(obj, Path):
        if output_dir and obj.is_absolute():
            try:
                return str(obj.relative_to(output_dir))
            except ValueError:
                pass
        return str(obj)

    # set → sorted list
    if isinstance(obj, set):
        return sorted(obj)

    # Pydantic BaseModel → .model_dump() then recurse
    if isinstance(obj, BaseModel):
        return _serialize_value(obj.model_dump(), output_dir)

    # tuple → list (for dict keys that are tuples, handled in dict branch)
    if isinstance(obj, tuple):
        return [_serialize_value(item, output_dir) for item in obj]

    # dataclass → dict with special handling
    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        return _serialize_dataclass(obj, output_dir)

    # dict
    if isinstance(obj, dict):
        result = {}
        for k, v in obj.items():
            # Tuple keys (e.g., usage_type_map) → JSON string key
            if isinstance(k, tuple):
                key = json.dumps([str(part) for part in k])
            elif isinstance(k, Path):
                if output_dir and k.is_absolute():
                    try:
                        key = str(k.relative_to(output_dir))
                    except ValueError:
                        key = str(k)
                else:
                    key = str(k)
            else:
                key = str(k)
            result[key] = _serialize_value(v, output_dir)
        return result

    # list
    if isinstance(obj, (list,)):
        return [_serialize_value(item, output_dir) for item in obj]

    # Unrecognized object (likely a Java bridge) → None
    return None


def _serialize_dataclass(obj: Any, output_dir: Path | None) -> dict[str, Any]:
    """Serialize a dataclass instance, handling AST fields and computed properties."""
    result: dict[str, Any] = {}

    for f in dataclasses.fields(obj):
        if f.name in _AST_FIELDS:
            result[f.name] = None
            continue
        value = getattr(obj, f.name)
        result[f.name] = _serialize_value(value, output_dir)

    # Preserve computed property values from BindingInfo
    if hasattr(obj, "source_instance_name") and hasattr(obj, "source_instance_elem"):
        result["source_instance_name"] = obj.source_instance_name
    if hasattr(obj, "source_attribute_name") and hasattr(obj, "source_attribute_elem"):
        result["source_attribute_name"] = obj.source_attribute_name

    return result


def snapshot_to_json(snapshot: dict[str, Any], indent: int = 2) -> str:
    """Convert a snapshot dict to a JSON string."""
    return json.dumps(snapshot, indent=indent, ensure_ascii=False)
