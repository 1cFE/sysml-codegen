"""Capture a snapshot from live models — the only license-requiring code here.

Two captures live side by side while the cutover runs:

``capture_snapshot`` writes the v5 extraction snapshot: it runs the live
``build_pipeline_context`` once, then serializes the extraction boundary with
``compilation_results`` (SC-10) and ``source_file`` relativized to the snapshot's
own directory (D1).

``capture_instance_graph_snapshot`` writes the v6 instance-graph snapshot: it
admits the sources, elaborates them once, and seals the resulting graph into the
envelope. Capture is the only place that can establish that the sealed graph came
from the sealed sources, so it elaborates and seals in one step, and writes
atomically — a snapshot file is complete and loadable or it does not exist.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

from sysml_codegen.snapshot.serializer import (
    serialize_extraction_snapshot,
    snapshot_to_json,
)


def capture_snapshot(
    model_paths: list[Path],
    output_path: Path,
    design_path_filter: str = "",
) -> Path:
    """Capture a versioned snapshot from live models and write it to output_path.

    Always captures with constraint lowering applied: a captured snapshot must be
    able to produce a certifying package, so ``constraint_lowering_mode`` is always
    ``"applied"`` (Item 12 closed the capture-time opt-out — the only honest
    ``grandfathered_off`` producer left is the extraction-only path, for models
    that cannot build a pipeline at all).

    Args:
        model_paths: SysML model directories/files to extract.
        output_path: Where to write the snapshot JSON. ``source_file`` fields are
            relativized against ``output_path.parent`` so the loader reproduces
            the parser's absolute paths exactly (D1).
        design_path_filter: Substring filter applied at capture time; its effect
            is baked into the snapshot (so re-applying it at generation is a hard
            CLI error, V6).

    Returns:
        The output path written.
    """
    # Local import: build_pipeline_context is the syside-invoking entry point.
    from sysml_codegen.orchestration.pipeline_builder import build_pipeline_context

    ctx = build_pipeline_context(
        model_paths,
        design_path_filter=design_path_filter,
    )
    if ctx.constraint_facts is None:  # build_pipeline_context always populates it
        raise RuntimeError("build_pipeline_context returned no constraint_facts")

    snapshot = serialize_extraction_snapshot(
        model_name=model_paths[0].name,
        calc_defs=ctx.calc_defs,
        calc_usages=ctx.calc_usages,
        design_attributes=ctx.design_attributes,
        hierarchy_data=ctx.hierarchy_data,
        aggregation_expressions=ctx.aggregation_expressions,
        computed_attributes=ctx.computed_attributes,
        channel_aliases=ctx.channel_aliases,
        constraint_facts=ctx.constraint_facts,
        part_occurrences=ctx.part_occurrences,
        constraint_lowering_mode=ctx.constraint_lowering_mode,
        model_paths=model_paths,
        compilation_results=ctx.compilation_results,
        output_dir=output_path.parent,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(snapshot_to_json(snapshot))
    return output_path


def capture_instance_graph_snapshot(model_paths: list[Path], output_path: Path) -> Path:
    """Elaborate the admitted sources once and atomically seal one v6 snapshot.

    Returns the written path. On any refusal — an unadmissible source tree, a
    model that does not elaborate cleanly, a graph that is not projectable —
    nothing is written and an existing file at ``output_path`` is left untouched.
    """
    # Local import: the elaboration route is the syside-invoking entry point.
    from sysml_codegen.extraction.source_manifest import admit_sources
    from sysml_codegen.orchestration.elaborated_pipeline import elaborate_admitted_sources
    from sysml_codegen.snapshot.envelope import build_envelope, encode_envelope

    with admit_sources(model_paths) as admission:
        graph = elaborate_admitted_sources(admission)
        payload = encode_envelope(build_envelope(graph, admission))

    _write_atomically(output_path, payload)
    return output_path


def _write_atomically(output_path: Path, payload: bytes) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{output_path.name}.", suffix=".tmp", dir=output_path.parent
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        temporary_path.chmod(0o644)
        os.replace(temporary_path, output_path)
    except BaseException:
        temporary_path.unlink(missing_ok=True)
        raise
