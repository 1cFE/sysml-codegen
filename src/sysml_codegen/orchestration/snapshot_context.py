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

from sysml_codegen.analysis.diagnostic_screen import screen_extraction_diagnostics
from sysml_codegen.orchestration.pipeline_context import PipelineContext
from sysml_codegen.snapshot import build_full_graph_from_snapshot
from sysml_codegen.snapshot.loader import load_extraction_snapshot

logger = logging.getLogger(__name__)


def build_pipeline_context_from_snapshot(snapshot_path: Path) -> PipelineContext:
    """Build a full PipelineContext from a snapshot (no syside license, INV-1).

    Rebuilds the ComputationGraph via the promoted helper, threads the
    deserialized ``compilation_results`` (SC-10) into it, and wraps everything in
    a ``PipelineContext`` with ``extractor`` / ``backtracker`` set to ``None``
    (INV-4). Logs the provenance banner once (V5) and, if the loader flagged
    stale sources, one end-of-run freshness summary (V3/M6).
    """
    # Snapshot route's diagnostic sink (DD-R08/R09) — the same function the live route
    # calls, at the matching boundary, and it must run **before** lowering to be that.
    #
    # It sits here rather than inside the loader on purpose: loading is deserialization,
    # and a snapshot carrying a blocking diagnostic must stay inspectable by tooling that
    # is not generating from it. Generation is what a blocking diagnostic stops (PC-4).
    #
    # It sits *above* `build_full_graph_from_snapshot` rather than below because that
    # call lowers constraints (`snapshot/graph_rebuild.py`). Screening after it let
    # lowering consume a non-finite literal first, so a user got an obscure lowering
    # failure instead of the actionable diagnostic — exactly the failure DD-R09 exists
    # to prevent (audit F1). The extra load is the honest price of the ordering; the
    # graph build that follows dominates it.
    screen_extraction_diagnostics(load_extraction_snapshot(snapshot_path)["constraint_facts"])

    graph, inputs = build_full_graph_from_snapshot(snapshot_path)
    snap = inputs["snap"]

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
        output_registry=inputs["registry"],
        # Carry the snapshot's real lowering mode (Item 12): without this the
        # context inherits the dataclass default "grandfathered_off" and every
        # from-snapshot context mis-reports, even an "applied" one. The product
        # generate gate reads this field, so it must be honest before the gate exists.
        constraint_lowering_mode=snap["constraint_lowering_mode"],
    )
