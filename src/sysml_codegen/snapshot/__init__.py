"""Supported snapshot machinery: capture, load, and rebuild a ComputationGraph
from a versioned JSON extraction snapshot — without a syside license at runtime.

A snapshot is a versioned JSON capture of the extraction boundary (the typed
dataclasses live extraction produces, with live syside ASTs nullified and the
lowered ``compilation_results`` strings preserved). Loading and rebuilding never
invoke the parser; only ``capture_snapshot`` needs a live license.
"""

from __future__ import annotations

from pathlib import Path

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


class GrandfatheredSnapshotError(Exception):
    """A ``grandfathered_off`` snapshot was routed to the certifying product path.

    A snapshot captured without constraint lowering carries no lowered
    constraints; generating a package from it would seal a certifying artifact
    with its constraint assertions silently absent. Normal product generation
    fails closed here (Item 12) — the snapshot must be recaptured with lowering
    enabled (the default) first. Loading such a snapshot for inspection is
    unaffected; only certifying generation is refused.
    """


def assert_snapshot_certifiable(constraint_lowering_mode: str, snapshot_path: Path) -> None:
    """Fail closed if a snapshot cannot produce a certifying package (Item 12).

    Called on the product generation path, before any output is written, so a
    grandfathered snapshot can never seal. ``grandfathered_off`` is non-certifying
    by construction: it was captured without lowering, so its constraint
    assertions were never lowered into generatable form.
    """
    if constraint_lowering_mode == CONSTRAINT_LOWERING_MODE_GRANDFATHERED_OFF:
        raise GrandfatheredSnapshotError(
            f"Snapshot {snapshot_path} was captured with constraint lowering "
            f"disabled (grandfathered_off) and cannot produce a certifying "
            f"package: its constraint assertions were never lowered. Recapture "
            f"with lowering enabled (the default) before generating from it."
        )


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
    "GrandfatheredSnapshotError",
    "assert_snapshot_certifiable",
    "build_classifier_inputs_from_snapshot",
    "build_full_graph_from_snapshot",
    "capture_snapshot",
    "load_extraction_snapshot",
    "serialize_extraction_snapshot",
    "snapshot_to_json",
]
