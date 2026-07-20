"""Supported snapshot machinery: capture, load, and rebuild a ComputationGraph
from a versioned JSON extraction snapshot — without a syside license at runtime.

A snapshot is a versioned JSON capture of the extraction boundary (the typed
dataclasses live extraction produces, with live syside ASTs nullified and the
lowered ``compilation_results`` strings preserved). Loading and rebuilding never
invoke the parser; only ``capture_snapshot`` needs a live license.
"""

from __future__ import annotations

# v3 (CONSTRAINT-EXEC Item 8): adds the top-level ``constraint_facts``,
# ``part_occurrences``, and ``constraint_lowering_mode`` sections — the neutral
# constraint facts, the resolved per-owner occurrence table (the transcript of
# the capture-time ``lower_constraints`` call), and the lowering-mode marker.
# The loader hard-gates on this version (INV-6) — there is no v2/v3
# coexistence, so every committed snapshot is re-captured at v3 in the same
# change.
#
# v5 (constraint-lifecycle Item 5): every ``source_file`` is stored as the
# certified portable ``root-N/<relpath>`` referent instead of a snapshot-dir-
# relative path that the loader re-absolutized on load. The loader validates the
# referent shape at load (``_validate_source_referents``) and no longer
# reconstructs any absolute path, so generated output is checkout-root-portable.
# A real version bump with a load-time shape gate — not an in-place v4 edit —
# closes Item 4 note N1: a field-less or absolute ``source_file`` is rejected
# loudly rather than silently loading and reintroducing the leak.
SNAPSHOT_FORMAT_VERSION = 5

# constraint_lowering_mode values (D3): "applied" means offline re-lowering
# should run; "grandfathered_off" means the snapshot was captured with lowering
# disabled (the plant_values/fusion_tea carve-out) and the offline path must
# skip lowering, loudly, rather than silently inferring it from an empty
# section. No other mode string is ever valid (MF2).
CONSTRAINT_LOWERING_MODE_APPLIED = "applied"
CONSTRAINT_LOWERING_MODE_GRANDFATHERED_OFF = "grandfathered_off"
VALID_CONSTRAINT_LOWERING_MODES = frozenset(
    {CONSTRAINT_LOWERING_MODE_APPLIED, CONSTRAINT_LOWERING_MODE_GRANDFATHERED_OFF}
)


class SnapshotFormatError(Exception):
    """Raised when a snapshot version or load-bearing v3 shape is invalid.

    The snapshot must be recaptured before generation can continue.
    """


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
    "CONSTRAINT_LOWERING_MODE_APPLIED",
    "CONSTRAINT_LOWERING_MODE_GRANDFATHERED_OFF",
    "SNAPSHOT_FORMAT_VERSION",
    "VALID_CONSTRAINT_LOWERING_MODES",
    "SnapshotFormatError",
    "build_classifier_inputs_from_snapshot",
    "build_full_graph_from_snapshot",
    "capture_snapshot",
    "load_extraction_snapshot",
    "serialize_extraction_snapshot",
    "snapshot_to_json",
]
