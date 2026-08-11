"""Strict atomic capture of a complete v6 exact instance-graph envelope."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

from sysml_codegen.snapshot.envelope import (
    build_snapshot_envelope,
    encode_snapshot_envelope,
)
from sysml_codegen.snapshot.source_manifest import admit_sources


def capture_snapshot(
    model_paths: list[Path],
    output_path: Path,
    design_path_filter: str = "",
) -> Path:
    """Elaborate admitted source bytes once and atomically write one v6 snapshot."""
    from sysml_codegen.orchestration.pipeline_builder import _load_and_elaborate

    with admit_sources(model_paths) as admission:
        graph = _load_and_elaborate(admission, design_path_filter)
        document = build_snapshot_envelope(
            graph,
            admission,
            model_name=model_paths[0].name,
            design_path_filter=design_path_filter,
        )
        payload = encode_snapshot_envelope(document)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{output_path.name}.",
        suffix=".tmp",
        dir=output_path.parent,
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_path, output_path)
    except BaseException:
        temporary_path.unlink(missing_ok=True)
        raise
    return output_path
