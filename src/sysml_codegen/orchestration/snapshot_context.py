"""Assemble a PipelineContext from a snapshot instead of live extraction.

This is the read-path convergence point for ``generate --from-snapshot``: it
rebuilds the same ``PipelineContext`` the live 7-step sequence produces, but from
a versioned JSON snapshot. The two syside-only fields — ``extractor`` and
``backtracker`` — are ``None`` (INV-4), safe because no generation path reads
them. The snapshot path never invokes the parser (INV-1).

Kept in its own module so the dependency edge is one-directional
(``orchestration → snapshot``, never back — D2).
"""

from __future__ import annotations

import logging
from pathlib import Path

from sysml_codegen.extraction.constraint_report import render_constraint_report
from sysml_codegen.orchestration.pipeline_context import PipelineContext
from sysml_codegen.snapshot import build_full_graph_from_snapshot

logger = logging.getLogger(__name__)

# The from-snapshot report must render through the SAME logger as the live path
# (Item 4, INV-B) so byte output and caplog filtering match across paths.
_extractor_logger = logging.getLogger("sysml_codegen.extraction.extractor")


def build_pipeline_context_from_snapshot(snapshot_path: Path) -> PipelineContext:
    """Build a full PipelineContext from a snapshot (no syside license, INV-1).

    Rebuilds the ComputationGraph via the promoted helper, threads the
    deserialized ``compilation_results`` (SC-10) into it, and wraps everything in
    a ``PipelineContext`` with ``extractor`` / ``backtracker`` set to ``None``
    (INV-4). Logs the provenance banner once (V5) and, if the loader flagged
    stale sources, one end-of-run freshness summary (V3/M6).
    """
    graph, inputs = build_full_graph_from_snapshot(snapshot_path)
    snap = inputs["snap"]

    # Replay the constraint drop report from the serialized manifest (Item 4).
    # Same renderer, same logger as the live path — the report the live run
    # emitted is now emitted offline too (INV-B).
    constraint_manifest = snap["constraint_manifest"]
    render_constraint_report(constraint_manifest, _extractor_logger)

    # Provenance banner (V5) — goes to the log only, never into an artifact (INV-6).
    logger.info(
        "Generating from snapshot %s (model %s, captured %s). "
        "This run did NOT use live extraction.",
        snapshot_path,
        snap["model_name"],
        snap["captured_at"],
    )

    # One end-of-run freshness summary (V3/M6) in addition to the loader's
    # per-file warnings.
    stale = snap.get("stale_sources", [])
    if stale:
        total = len({
            str(cd.source_file)
            for cd in snap["calc_defs"]
            if str(cd.source_file) not in ("unknown", "hierarchy")
        })
        logger.warning(
            "%d of %d snapshot source files no longer match on-disk source; "
            "recapture to refresh.",
            len(stale),
            total,
        )

    return PipelineContext(
        extractor=None,
        calc_defs=snap["calc_defs"],
        calc_usages=snap["calc_usages"],
        design_attributes=inputs["design_attrs"],
        group_deriver=inputs["group_deriver"],
        backtracker=None,  # type: ignore[arg-type]  # INV-4: no generation path reads it
        backtracking_result=inputs["result"],
        computation_graph=graph,
        compilation_results=snap["compilation_results"],
        computed_attributes=snap["computed_attributes"],
        hierarchy_data=snap["hierarchy_data"],
        aggregation_expressions=snap["aggregation_expressions"],
        channel_aliases=snap["channel_aliases"],
        constraint_manifest=constraint_manifest,
        output_registry=inputs["registry"],
    )
