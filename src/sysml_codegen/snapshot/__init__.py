"""Public v6 instance-graph snapshot API."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from sysml_codegen.snapshot.capture import capture_snapshot
    from sysml_codegen.snapshot.envelope import (
        SnapshotCertifiabilityError,
        SnapshotCompatibilityError,
        SnapshotFormatError,
        SnapshotIntegrityError,
        SnapshotStaleSourceError,
        load_snapshot,
    )
SNAPSHOT_FORMAT_VERSION = 6


def __getattr__(name: str) -> Any:
    """Resolve snapshot exports lazily so the source owner has no import cycle."""
    if name == "capture_snapshot":
        from sysml_codegen.snapshot.capture import capture_snapshot

        return capture_snapshot
    if name in {
        "SnapshotCertifiabilityError",
        "SnapshotCompatibilityError",
        "SnapshotFormatError",
        "SnapshotIntegrityError",
        "SnapshotStaleSourceError",
        "load_snapshot",
    }:
        from sysml_codegen.snapshot import envelope

        return getattr(envelope, name)
    raise AttributeError(name)

__all__ = [
    "SNAPSHOT_FORMAT_VERSION",
    "SnapshotCertifiabilityError",
    "SnapshotCompatibilityError",
    "SnapshotFormatError",
    "SnapshotIntegrityError",
    "SnapshotStaleSourceError",
    "capture_snapshot",
    "load_snapshot",
]
