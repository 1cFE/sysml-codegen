"""Capture a versioned extraction snapshot from live models.

This is the only license-requiring code in the snapshot package: it runs the live
``build_pipeline_context`` once, then serializes the extraction boundary with
``compilation_results`` (SC-10) and ``source_file`` relativized to the snapshot's
own directory (D1). Lifted from
``scripts/capture_extraction_snapshots.py:_capture_full_pipeline``.
"""

from __future__ import annotations

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

    ctx = build_pipeline_context(model_paths, design_path_filter=design_path_filter)

    snapshot = serialize_extraction_snapshot(
        model_name=model_paths[0].name,
        calc_defs=ctx.calc_defs,
        calc_usages=ctx.calc_usages,
        design_attributes=ctx.design_attributes,
        hierarchy_data=ctx.hierarchy_data,
        aggregation_expressions=ctx.aggregation_expressions,
        computed_attributes=ctx.computed_attributes,
        channel_aliases=ctx.channel_aliases,
        compilation_results=ctx.compilation_results,
        constraint_manifest=ctx.constraint_manifest,
        output_dir=output_path.parent,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(snapshot_to_json(snapshot))
    return output_path
