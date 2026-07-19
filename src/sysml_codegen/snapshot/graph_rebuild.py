"""Rebuild a ComputationGraph from a loaded extraction snapshot.

Promoted from ``tests/conformance/test_entry_point_classifier.py`` (the proven
graph-rebuild body exercised by the conformance suite). Runs the snapshot path —
output registry, backtracker, classifier, graph builder — without ever invoking
the syside adapter/parser. Transitive imports of syside modules are license-free;
the constraint is behavioral (never invoke), not import-graph.
"""

from __future__ import annotations

import logging
from pathlib import Path

from sysml_codegen.analysis.constraint_lowering import (
    collect_bare_actual_demand,
    extend_graph_with_constraints,
    lower_constraints,
)
from sysml_codegen.analysis.dependency_backtracker import DependencyBacktracker
from sysml_codegen.analysis.parameter_groups import ParameterGroupDeriver
from sysml_codegen.analysis.part_instance_index import FrozenOccurrenceIndex
from sysml_codegen.orchestration.output_registry_builder import build_output_registry
from sysml_codegen.resolution.graph_builder import (
    _classify_entry_points,
    build_computation_graph,
)
from sysml_codegen.resolution.models import ComputationGraph
from sysml_codegen.resolution.supplied_values import materialize_supplied_values
from sysml_codegen.snapshot import (
    CONSTRAINT_LOWERING_MODE_APPLIED,
    CONSTRAINT_LOWERING_MODE_GRANDFATHERED_OFF,
)
from sysml_codegen.snapshot.loader import load_extraction_snapshot

logger = logging.getLogger(__name__)


def build_classifier_inputs_from_snapshot(snapshot_path: Path) -> dict:
    """Build all inputs needed to verify _classify_entry_points() from a snapshot.

    Exposes intermediate data structures:
    - design_attr_by_qname: for verifying DESIGN_ATTRIBUTE classification
    - unbound_lookup: for verifying LIBRARY_DEFAULT classification
    - entry_point_sources: for verifying USAGE_LITERAL classification
    - group_deriver: for verifying param_group assignment

    Returns dict with all components.
    """
    snap = load_extraction_snapshot(snapshot_path)

    # Build registry
    registry = build_output_registry(
        calc_usages=snap["calc_usages"],
        calc_defs=snap["calc_defs"],
        aggregation_data=snap["aggregation_expressions"],
        computed_attributes=snap["computed_attributes"],
        channel_aliases=snap.get("channel_aliases", []),
        design_attributes=snap.get("design_attributes", {}),
    )

    # Item 10 #4: populate the structured _scoped_alias namespace the same way the
    # live path does (pipeline_builder Step 5.55), so a part-def EXPOSE resolves
    # offline too. Local import avoids a pipeline_builder import cycle.
    from sysml_codegen.orchestration.pipeline_builder import (
        _register_partdef_expose_scoped_aliases,
        _rescue_self_named_bindings,
    )

    _register_partdef_expose_scoped_aliases(
        registry,
        snap["computed_attributes"],
        snap["calc_usages"],
        snap.get("hierarchy_data"),
    )

    # Item 10 stage (b), mechanism D: rescue self-named bindings to their upstream
    # EXPOSE channel (pipeline_builder Step 5.56), so the offline path wires them the
    # same as the live path. Runs after the scoped aliases exist, before the backtracker.
    _rescue_self_named_bindings(registry, snap["calc_usages"])

    # Item 2 (REQ-SVM-01..04): materialize supplied subsystem-attr values into
    # design_attributes BEFORE the backtracker, so its Step-3 design-attribute
    # resolution carries them to the consumer and collapses fan-out by source QN.
    # The backtracker (below) is the real seam — it, not build_computation_graph,
    # runs `_resolve_to_design_attribute`.
    hierarchy_data = snap["hierarchy_data"]
    # D2 (Item 14): widen the demand set to a constraint actual with no calc-usage
    # binding of its own — mirrors pipeline_builder.py's live Step 5.65 so the
    # offline rebuild stays in parity (a snapshot captured `applied` already ran
    # this widened materializer live; re-deriving it identically here is what
    # makes from-snapshot regeneration byte-identical, not merely non-crashing).
    constraint_actual_demand = (
        collect_bare_actual_demand(
            snap["constraint_facts"],
            FrozenOccurrenceIndex(snap["part_occurrences"]),
            snap["calc_usages"],
        )
        if snap["constraint_lowering_mode"] == CONSTRAINT_LOWERING_MODE_APPLIED
        and snap["constraint_facts"].usages
        else []
    )
    synth_attrs = materialize_supplied_values(
        snap["calc_usages"],
        hierarchy_data.redefinitions,
        hierarchy_data.design_overrides,
        hierarchy_data.usage_type_map,
        snap["design_attributes"],
        constraint_actual_demand=constraint_actual_demand,
    )
    for attr in synth_attrs:
        # Bucket by the attribute's own source file (the consuming usage's file) so it
        # groups into a valid, existing parameter group, not a sentinel-named one.
        snap["design_attributes"].setdefault(str(attr.source_file), []).append(attr)

    # Run backtracker
    backtracker = DependencyBacktracker(
        all_usages=snap["calc_usages"],
        calc_defs=snap["calc_defs"],
        design_attributes=snap.get("design_attributes", {}),
        output_registry=registry,
    )
    result = backtracker.find_required_modules([], include_all=True)

    # Build calc_def_map
    calc_def_map = {cd.name: cd for cd in snap["calc_defs"]}

    # Build design_attrs with Path keys
    design_attrs = {Path(k): v for k, v in snap["design_attributes"].items()}

    # Build ParameterGroupDeriver
    group_deriver = ParameterGroupDeriver(
        design_attrs, snap["calc_usages"], snap["calc_defs"]
    )

    # Classify entry points
    entry_points = _classify_entry_points(
        result.entry_points,
        result.entry_point_sources,
        design_attrs,
        result.required_usages,
        calc_def_map,
        group_deriver,
    )

    # Build the intermediate lookup indexes (same logic as _classify_entry_points)
    design_attr_by_qname: dict[str, object] = {}
    for attrs in design_attrs.values():
        for attr in attrs:
            if attr.qualified_name:
                design_attr_by_qname[attr.qualified_name] = attr

    unbound_lookup: dict[str, tuple] = {}
    for usage in result.required_usages:
        for param_name in usage.unbound_params:
            qname = f"{usage.qualified_name}__{param_name}"
            unbound_lookup[qname] = (usage, param_name)

    return {
        "snap": snap,
        "result": result,
        "entry_points": entry_points,
        "calc_def_map": calc_def_map,
        "design_attrs": design_attrs,
        "design_attr_by_qname": design_attr_by_qname,
        "unbound_lookup": unbound_lookup,
        "entry_point_sources": result.entry_point_sources,
        "group_deriver": group_deriver,
        "registry": registry,
    }


def build_full_graph_from_snapshot(
    snapshot_path: Path,
) -> tuple[ComputationGraph, dict]:
    """Build a full ComputationGraph from snapshot, including FORMULA + aggregation.

    Returns (ComputationGraph, classifier_inputs_dict) so callers can inspect both
    the final graph and the intermediate data.
    """
    inputs = build_classifier_inputs_from_snapshot(snapshot_path)
    snap = inputs["snap"]
    result = inputs["result"]

    hierarchy_data = snap["hierarchy_data"]

    graph = build_computation_graph(
        result=result,
        calc_defs=snap["calc_defs"],
        design_attrs=inputs["design_attrs"],
        group_deriver=inputs["group_deriver"],
        output_registry=inputs["registry"],
        compilation_results=snap.get("compilation_results"),
        computed_attributes=snap["computed_attributes"],
        aggregation_data=snap["aggregation_expressions"],
        hierarchy_redefinitions=hierarchy_data.redefinitions,
        usage_type_map=hierarchy_data.usage_type_map,
        # Item 11 (F-A): the snapshot path is the one the 7 graph baselines are
        # captured through — thread the expose_pure ChannelAliases so shape-B
        # output_aliases are populated (not silently empty) in committed artifacts.
        # A snapshot rebuild is always a full graph (include_all=True below).
        channel_aliases=snap.get("channel_aliases", []),
        include_all=True,
    )

    # [P1 RESOLVE + P3 EXTEND] (Item 8): offline re-lowering, dispatched on the
    # load-validated mode enum (total — no third branch, the loader already
    # rejected any other value). P2 (roots-before-pruning) is inert offline:
    # include_all=True above already put every calc usage's producer channel in
    # the graph, so a constraint's bound_channel never dangles (design.md#key-bets B3).
    facts = snap["constraint_facts"]
    mode = snap["constraint_lowering_mode"]
    if mode == CONSTRAINT_LOWERING_MODE_APPLIED and facts.usages:
        occ_index = FrozenOccurrenceIndex(snap["part_occurrences"])
        concrete = lower_constraints(
            facts,
            occ_index=occ_index,
            registry=inputs["registry"],
            design_attrs=inputs["design_attrs"],
            calc_usages=snap["calc_usages"],
            source_location_mode="snapshot",
            source_roots=[],
        )
        if concrete:
            graph = extend_graph_with_constraints(graph, concrete, inputs["group_deriver"])
            # [P4 CATALOG] (Item 7 / D6): mirrors pipeline_builder.py's live P4 —
            # every generation seam reads the catalog from the graph, never from
            # a context, so live and from-snapshot artifacts stay byte-identical
            # only if both assemble it the same way.
            from sysml_codegen.generation.constraint_catalog import assemble_constraint_catalog

            graph.constraint_catalog = assemble_constraint_catalog(concrete, facts)
    elif mode == CONSTRAINT_LOWERING_MODE_GRANDFATHERED_OFF and facts.usages:
        logger.warning(
            "Snapshot %s was captured with constraint lowering disabled "
            "(grandfathered) but carries %d constraint assertion(s) — these "
            "assertions are NOT generated into this graph. Recapture with "
            "lowering enabled to include them.",
            snapshot_path,
            len(facts.usages),
        )

    return graph, inputs
