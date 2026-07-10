"""Load extraction snapshots from JSON and reconstruct typed dataclass instances.

Reverses the serialization performed by snapshot_serializer.py:
- str → Path for source_file fields
- str → Enum for binding_type, redefinition_type, classification, compilability
- None AST fields remain None (documented as "not available from snapshot")
- tuple-encoded dict keys → tuple
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
from pathlib import Path
from typing import Any

from agentic_mbse.sysml.types import BindingType, ExpressionRef

from sysml_codegen.analysis.parameter_groups import DesignAttributeData
from sysml_codegen.core.models import ChannelAlias
from sysml_codegen.extraction.constraint_report import manifest_from_records
from sysml_codegen.extraction.data_models import (
    AggregationExpressionData,
    AttributeInfo,
    CalculationDefinitionData,
    ComputedAttributeClassification,
    ComputedAttributeData,
    HierarchyExtractionResult,
    LocalTerm,
    MultiplicityData,
    RedefinitionData,
    RedefinitionType,
    ScopedAggregationData,
    SingletonTerm,
    SumTerm,
)
from sysml_codegen.extraction.expression_compiler import (
    CalcDefCompilationResult,
    Compilability,
    CompilationResult,
)
from sysml_codegen.extraction.usage_extractor import BindingInfo, CalcUsageData
from sysml_codegen.snapshot import SNAPSHOT_FORMAT_VERSION, SnapshotFormatError

logger = logging.getLogger(__name__)

# source_file values that are not real paths — passed through untouched.
_SOURCE_SENTINELS = frozenset({"unknown", "hierarchy"})


def _require(
    d: dict, field: str, default: Any, context: str, *, raise_on_missing: bool = False
) -> Any:
    """Return ``d[field]``, or the degraded default when the field is missing.

    A handful of snapshot fields are load-bearing: defaulting them silently
    masks a corrupt/missing value that changes wiring, keying, or type. This
    fires a diagnostic instead of defaulting quietly. Keying fields (whose
    default would mis-key the output registry) raise; the rest warn and
    degrade.
    """
    if field in d:
        return d[field]
    if raise_on_missing:
        raise SnapshotFormatError(
            f"{context}: snapshot is missing load-bearing field {field!r} — "
            f"this field keys the output registry, and a silent default would "
            f"mis-key it. Recapture the snapshot."
        )
    logger.warning(
        "%s: snapshot is missing load-bearing field %r — falling back to %r; "
        "downstream wiring/typing is degraded.",
        context,
        field,
        default,
    )
    return default


def _require_binding_type(d: dict, context: str) -> BindingType:
    """Return the deserialized ``binding_type``, warning if missing/empty.

    A missing or falsy ``binding_type`` silently drops the binding to
    ``UNBOUND`` today; that is load-bearing (it changes wiring), so it warns.
    """
    raw = d.get("binding_type")
    if raw:
        return BindingType(raw)
    logger.warning(
        "%s: snapshot has no binding_type (missing or empty) — the binding "
        "is dropped to UNBOUND.",
        context,
    )
    return BindingType.UNBOUND


def load_extraction_snapshot(snapshot_path: Path) -> dict[str, Any]:
    """Load an extraction snapshot from a path and reconstruct typed instances.

    Args:
        snapshot_path: Path to the ``extraction_snapshot.json`` file.

    Raises:
        SnapshotFormatError: if ``snapshot_format_version`` is missing or does
            not match ``SNAPSHOT_FORMAT_VERSION`` (INV-2) — checked before any
            field deserialization.

    Returns:
        Dict with typed instances:
            calc_defs: list[CalculationDefinitionData]
            calc_usages: list[CalcUsageData]
            design_attributes: dict[str, list[DesignAttributeData]]
            hierarchy_data: HierarchyExtractionResult
            aggregation_expressions: list[ScopedAggregationData]
            computed_attributes: list[ComputedAttributeData]
            channel_aliases: list[ChannelAlias]
            compilation_results: dict[str, CalcDefCompilationResult] (SC-10;
                empty if the snapshot predates the section — degrades with a warning)
            stale_sources: list[str] of re-absolutized source files whose on-disk
                hash no longer matches the snapshot (freshness, V3)
    """
    raw = json.loads(snapshot_path.read_text())

    # Version guard runs first (INV-2, V1/V2) — before any field deserialization.
    version = raw.get("snapshot_format_version")
    if version is None:
        raise SnapshotFormatError(
            f"Snapshot {snapshot_path} has no snapshot_format_version — it "
            "predates versioned snapshots. Recapture with "
            "`scripts/capture_extraction_snapshots.py` (current tooling writes "
            f"version {SNAPSHOT_FORMAT_VERSION})."
        )
    if version != SNAPSHOT_FORMAT_VERSION:
        raise SnapshotFormatError(
            f"Snapshot {snapshot_path} is format version {version}, tool expects "
            f"{SNAPSHOT_FORMAT_VERSION}. Recapture with "
            "`scripts/capture_extraction_snapshots.py`."
        )

    snapshot_dir = snapshot_path.parent
    snap: dict[str, Any] = {
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
        "compilation_results": _load_compilation_results(raw, snapshot_path),
        # Model-wide dropped-constraint manifest (Item 4). Additive: a snapshot
        # captured before this field just yields an empty manifest.
        "constraint_manifest": manifest_from_records(
            raw.get("dropped_constraints", [])
        ),
    }

    # source_file re-absolutization (D1/D8): lexical absolute join against the
    # snapshot's own directory, no symlink resolution. Sentinels pass through.
    _reabsolutize_source_files(snap, snapshot_dir)

    # Source freshness (V3): warn per stale file, record the set for a one-line
    # end-of-run summary the caller logs.
    snap["stale_sources"] = _check_source_freshness(snap, snapshot_path)

    return snap


# --- Format-contract helpers (version / compilation_results / source_file) ---


def _load_compilation_results(
    raw: dict, snapshot_path: Path
) -> dict[str, CalcDefCompilationResult]:
    """Deserialize the compilation_results block, or degrade with a warning (V4)."""
    block = raw.get("compilation_results")
    if not block:
        # Absent or empty. A version-current snapshot may legitimately lack it
        # (captured before SC-10) — degrade to today's behavior with a warning.
        if "compilation_results" not in raw:
            logger.warning(
                "Snapshot %s has no compilation_results section (captured before "
                "SC-10). CalcUsage auto-implementation will be lost; stencils fall "
                "back to NotImplementedError. Recapture to restore.",
                snapshot_path,
            )
        return {}
    return {
        name: _deserialize_calc_def_compilation_result(cr)
        for name, cr in block.items()
    }


def _deserialize_compilation_result(d: dict) -> CompilationResult:
    """Reconstruct a CompilationResult (one output's lowered expression)."""
    return CompilationResult(
        output_name=d["output_name"],
        compilability=Compilability(d["compilability"]),
        python_expression=d.get("python_expression"),
        input_refs=d.get("input_refs", []),
        intermediate_refs=d.get("intermediate_refs", []),
        unsupported_reason=d.get("unsupported_reason"),
        is_undeclared_intermediate=d.get("is_undeclared_intermediate", False),
    )


def _deserialize_calc_def_compilation_result(d: dict) -> CalcDefCompilationResult:
    """Reconstruct a CalcDefCompilationResult from a serialized dict."""
    return CalcDefCompilationResult(
        calc_def_name=d["calc_def_name"],
        overall_compilability=Compilability(d["overall_compilability"]),
        output_results=[_deserialize_compilation_result(r) for r in d["output_results"]],
        execution_order=d["execution_order"],
    )


def _reabsolutize_source_file(source_file: Path, snapshot_dir: Path) -> Path:
    """Rebuild an absolute source_file by a lexical join against snapshot_dir (D8).

    Uses ``os.path.abspath`` (no ``.resolve()``) so a symlinked source path is
    reproduced exactly as the parser reports it (B2). Sentinels pass through.
    """
    stored = str(source_file)
    if stored in _SOURCE_SENTINELS:
        return source_file
    return Path(os.path.abspath(snapshot_dir / stored))


def _reabsolutize_source_files(snap: dict[str, Any], snapshot_dir: Path) -> None:
    """Re-absolutize every real source_file field in place against snapshot_dir."""

    def fix(obj: Any) -> None:
        sf = getattr(obj, "source_file", None)
        if isinstance(sf, Path):
            obj.source_file = _reabsolutize_source_file(sf, snapshot_dir)

    for cd in snap["calc_defs"]:
        fix(cd)
    for cu in snap["calc_usages"]:
        fix(cu)
    for attrs in snap["design_attributes"].values():
        for da in attrs:
            fix(da)
    hierarchy = snap["hierarchy_data"]
    for redef in hierarchy.redefinitions:
        fix(redef)
    for override in hierarchy.design_overrides:
        fix(override)
    for agg in hierarchy.aggregation_expressions:
        fix(agg)
    for scoped in snap["aggregation_expressions"]:
        fix(scoped.expression)
    for ca in snap["computed_attributes"]:
        fix(ca)


def _compute_source_hash(file_path: Path) -> str:
    """SHA256 of file contents — matches SysMLDataExtractor._compute_file_hash."""
    if not file_path.exists() or file_path.is_dir():
        return ""
    sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            sha256.update(chunk)
    return sha256.hexdigest()


def _check_source_freshness(snap: dict[str, Any], snapshot_path: Path) -> list[str]:
    """Warn per calc_def whose on-disk source hash no longer matches (V3).

    Returns the sorted list of stale source files so the caller can log one
    end-of-run summary. calc_defs are the only objects carrying source_hash.
    """
    stale: set[str] = set()
    for cd in snap["calc_defs"]:
        stored_hash = getattr(cd, "source_hash", "")
        source_file = getattr(cd, "source_file", None)
        if not stored_hash or not isinstance(source_file, Path):
            continue
        if str(source_file) in _SOURCE_SENTINELS or not source_file.exists():
            continue
        if _compute_source_hash(source_file) != stored_hash:
            stale.add(str(source_file))
            logger.warning(
                "Snapshot %s source hash for %s no longer matches on-disk source "
                "— snapshot may be stale. Continuing; recapture to refresh.",
                snapshot_path,
                source_file,
            )
    return sorted(stale)


# --- Individual deserializers ---


def _deserialize_attribute_info(d: dict) -> AttributeInfo:
    """Reconstruct an AttributeInfo from a serialized dict."""
    context = f"attribute {d.get('name', '?')!r}"
    return AttributeInfo(
        name=d["name"],
        sysml_type=d.get("sysml_type"),
        default_value=d.get("default_value"),
        binding_type=_require_binding_type(d, context),
        is_input=d.get("is_input", False),
        is_output=d.get("is_output", False),
        python_type=_require(d, "python_type", "Any", context),
        description=d.get("description", ""),
        unit=d.get("unit"),
        source_line=d.get("source_line", 0),
        is_optional=d.get("is_optional", False),
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
    context = f"calc usage {d.get('instance_name', '?')!r}"
    return CalcUsageData(
        instance_name=d["instance_name"],
        calc_def_name=d["calc_def_name"],
        calc_def_qualified_name=d["calc_def_qualified_name"],
        module_type=d["module_type"],
        bindings=[_deserialize_binding_info(b) for b in d["bindings"]],
        unbound_params=d.get("unbound_params", []),
        source_file=Path(d["source_file"]),
        source_line=d.get("source_line", 0),
        parent_part_path=_require(d, "parent_part_path", "", context),
        qualified_name=_require(d, "qualified_name", "", context, raise_on_missing=True),
        is_template=d.get("is_template", False),
        owning_part_def_qn=_require(d, "owning_part_def_qn", None, context),
    )


def _deserialize_design_attribute(d: dict) -> DesignAttributeData:
    """Reconstruct a DesignAttributeData from a serialized dict."""
    context = f"design attribute {d.get('name', '?')!r}"
    return DesignAttributeData(
        name=d["name"],
        sysml_type=d["sysml_type"],
        default_value=d.get("default_value"),
        unit=d.get("unit"),
        source_file=Path(d["source_file"]),
        source_line=d.get("source_line", 0),
        parent_part=d["parent_part"],
        qualified_name=_require(d, "qualified_name", "", context, raise_on_missing=True),
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
        compilability=(
            Compilability(d["compilability"]) if d.get("compilability") else Compilability.UNKNOWN
        ),
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
            # D3-6 (offline-parity guard): a malformed usage_type_map key drops a
            # retype mapping, so the from-snapshot path silently mis-wires (falls
            # to the base def) where the live path wired correctly. The except is
            # already narrow; log the drop instead of a bare pass so the offline
            # divergence is visible.
            logger.warning(
                "Snapshot usage_type_map: dropping malformed key %r — the "
                "retype it carried will fall to the base def (offline-only "
                "mis-wire).",
                key_str,
            )

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
        compilability=(
            Compilability(d["compilability"]) if d.get("compilability") else Compilability.UNKNOWN
        ),
        compiled_expression=d.get("compiled_expression"),
        is_on_part_definition=d.get("is_on_part_definition", False),
        source_file=Path(d.get("source_file", "unknown")),
        source_line=d.get("source_line", 0),
        # Additive-optional (Item 10, D9): old snapshots lack it → None. No
        # SNAPSHOT_FORMAT_VERSION bump; absent chain leaves classification at
        # today's FORMULA behavior.
        reference_chain=d.get("reference_chain"),
    )
