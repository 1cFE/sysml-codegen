"""Supported snapshot machinery: capture, load, and rebuild a ComputationGraph
from a versioned JSON extraction snapshot — without a syside license at runtime.

A snapshot is a versioned JSON capture of the extraction boundary (the typed
dataclasses live extraction produces, with live syside ASTs nullified and the
lowered ``compilation_results`` strings preserved). Loading and rebuilding never
invoke the parser; only ``capture_snapshot`` needs a live license.
"""

from __future__ import annotations

# v2 (PIPELINE-TRUTH Item 4): adds the top-level ``dropped_constraints`` manifest.
# The loader hard-gates on this version (INV-E) — there is no v1/v2 coexistence, so
# every committed snapshot is re-captured at v2 in the same change.
SNAPSHOT_FORMAT_VERSION = 2


class SnapshotFormatError(Exception):
    """Raised when a snapshot's ``snapshot_format_version`` is missing or does
    not match ``SNAPSHOT_FORMAT_VERSION`` — the snapshot must be recaptured."""


from sysml_codegen.snapshot.capture import capture_snapshot  # noqa: E402
from sysml_codegen.snapshot.graph_rebuild import (  # noqa: E402
    build_classifier_inputs_from_snapshot,
    build_full_graph_from_snapshot,
)
from sysml_codegen.snapshot.loader import load_extraction_snapshot  # noqa: E402
from sysml_codegen.snapshot.serializer import (  # noqa: E402
    serialize_extraction_snapshot,
    snapshot_to_json,
)

__all__ = [
    "SNAPSHOT_FORMAT_VERSION",
    "SnapshotFormatError",
    "build_classifier_inputs_from_snapshot",
    "build_full_graph_from_snapshot",
    "capture_snapshot",
    "load_extraction_snapshot",
    "serialize_extraction_snapshot",
    "snapshot_to_json",
]
