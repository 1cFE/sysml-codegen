"""Capture a snapshot from live models — the only license-requiring code here.

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
