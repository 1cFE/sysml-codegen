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
from copy import deepcopy
from enum import Enum
from pathlib import Path
from typing import TYPE_CHECKING, Any

from agentic_mbse.sysml.constraint_facts import serialize as serialize_constraint_facts
from pydantic import BaseModel

from sysml_codegen.analysis.constraint_lowering import (
    associate_usage_decisions,
    is_excluded_usage,
)
from sysml_codegen.analysis.source_referent import map_live_source_referent
from sysml_codegen.snapshot import SNAPSHOT_FORMAT_VERSION

if TYPE_CHECKING:
    from agentic_mbse.sysml.constraint_facts import ConstraintFacts

    from sysml_codegen.analysis.part_instance_index import InstanceOccurrence

# Fields that hold live SysIDE Java objects — always nullify.
_AST_FIELDS = frozenset(
    {
        "output_expression_asts",
        "member_expressions",
        "expression_ast",
        "source_instance_elem",
        "source_attribute_elem",
        "raw_element",
    }
)


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
    constraint_facts: ConstraintFacts,
    part_occurrences: dict[str, list[InstanceOccurrence]],
    constraint_lowering_mode: str,
    model_paths: list[Path],
    compilation_results: dict[str, Any] | None = None,
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
        constraint_facts: the neutral ``ConstraintFacts`` (Item 1) — always
            present, embedded via its own canonical ``serialize()`` (bytes
            preserved, not re-derived). May carry empty ``usages``.
        part_occurrences: the resolved per-owner occurrence table (Item 8, MF3)
            — the transcript of the capture-time ``lower_constraints`` call's
            ``occurrences_of`` queries. ``{}`` when lowering did not run.
        constraint_lowering_mode: ``"applied"`` or ``"grandfathered_off"`` (Item
            8, D3) — always present.
        compilation_results: dict[str, CalcDefCompilationResult] keyed by
            calc_def.name (SC-10). Absent/None → empty block; loader degrades.
        output_dir: If provided, Path fields (and Path dict keys) are made
            relative to this dir — the snapshot's own directory (D1). The loader
            re-absolutizes against the same anchor, so the round-trip is exact.

    Returns:
        JSON-safe dict suitable for json.dumps(). The top-level
        ``snapshot_format_version`` gates loading (INV-6).
    """
    return {
        "snapshot_format_version": SNAPSHOT_FORMAT_VERSION,
        "model_name": model_name,
        "captured_at": datetime.datetime.now(datetime.UTC).isoformat(),
        "constraint_lowering_mode": constraint_lowering_mode,
        "constraint_facts": json.loads(
            serialize_constraint_facts(
                _constraint_facts_for_snapshot(
                    constraint_facts,
                    constraint_lowering_mode=constraint_lowering_mode,
                    model_paths=model_paths,
                )
            )
        ),
        # Owner keys emitted sorted (INV-7/MF4) — snapshot_to_json does not
        # sort_keys, so an unsorted dict would churn this section every capture.
        "part_occurrences": {
            owner_eqn: _serialize_value(occurrences, output_dir)
            for owner_eqn, occurrences in sorted(part_occurrences.items())
        },
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
        "computed_attributes": [_serialize_value(ca, output_dir) for ca in computed_attributes],
        "channel_aliases": [_serialize_value(ca, output_dir) for ca in channel_aliases],
    }


def _constraint_facts_for_snapshot(
    facts: ConstraintFacts,
    *,
    constraint_lowering_mode: str,
    model_paths: list[Path],
) -> ConstraintFacts:
    """Copy and canonicalize every located usage selected for exclusion."""
    copied = deepcopy(facts)
    if constraint_lowering_mode != "applied" or not copied.usages:
        return copied
    # A second, purely associative evaluation (D10): it selects excluded usages and
    # canonicalizes their copied locations. It emits no warning, aggregates no BLOCK,
    # expands no owner, and mutates only the deep copy.
    for index, (usage, decision) in enumerate(associate_usage_decisions(facts)):
        if not is_excluded_usage(usage, decision):
            continue
        original = facts.usages[index]
        if original.location is None:
            if original.identity.name is None:
                raise ValueError("anonymous excluded constraint has no LocationFact")
            continue
        copied_location = copied.usages[index].location
        if copied_location is None:
            raise RuntimeError("copied exclusion lost its LocationFact")
        copied_location.file = map_live_source_referent(original.location.file, model_paths)
    return copied


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
        # Fields whose value is reconstructed on load, never written. Unlike
        # _AST_FIELDS these emit no key at all, so adding one cannot change the
        # wire form of an already-committed snapshot.
        if f.metadata.get("snapshot_exclude"):
            continue
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
    if hasattr(obj, "source_written_qualifier"):
        result["source_written_qualifier"] = obj.source_written_qualifier

    return result


def snapshot_to_json(snapshot: dict[str, Any], indent: int = 2) -> str:
    """Convert a snapshot dict to a JSON string."""
    return json.dumps(snapshot, indent=indent, ensure_ascii=False)
