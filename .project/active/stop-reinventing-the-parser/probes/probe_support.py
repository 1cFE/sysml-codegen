"""Shared immutable-input checks for the stop-parser retained probes."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from agentic_mbse.sysml.syside_adapter import SysideAdapter

BATCH_SHA256 = "bd7bf245e3ca3923b9b5d41db97861c9fcdf64435e768d48a2d7027eb52d9288"


def canonical_json_bytes(value: Any) -> bytes:
    """Encode one probe result in the stable representation used by verdicts."""
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        allow_nan=False,
    ).encode()


def write_canonical_json(path: Path, value: Any) -> None:
    """Write one newline-terminated canonical JSON document."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(canonical_json_bytes(value) + b"\n")


def sha256_file(path: Path) -> str:
    """Return the SHA-256 digest of one required file."""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    """Load a JSON object and reject any other root type."""
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected a JSON object")
    return value


def load_model(root: Path) -> Any:
    """Load one real fixture and reject parser errors."""
    model, diagnostics = SysideAdapter.load_model([root])
    errors = [
        item for item in diagnostics.all if str(getattr(item, "severity", "")).endswith("Error")
    ]
    if errors:
        raise RuntimeError(f"{root}: parser errors: {errors!r}")
    return model


def validate_lock(
    repository: Path,
    *,
    lock_path: Path,
    expected_probe_commit: str | None = None,
) -> dict[str, Any]:
    """Recompute every probe/fixture-lock digest before a retained probe runs."""
    lock = load_json(lock_path)
    probe_commit = lock.get("probe_fixture_commit")
    if not isinstance(probe_commit, str) or len(probe_commit) != 40:
        raise ValueError("probe_fixture_commit must be one full SHA")
    if expected_probe_commit is not None and probe_commit != expected_probe_commit:
        raise ValueError(
            f"probe commit mismatch: lock={probe_commit} expected={expected_probe_commit}"
        )
    for item in lock.get("files", []):
        relative = item.get("path")
        digest = item.get("sha256")
        if not isinstance(relative, str) or not isinstance(digest, str):
            raise ValueError("lock file rows require path and sha256 strings")
        path = repository / relative
        if not path.is_file() or sha256_file(path) != digest:
            raise ValueError(f"locked input changed: {relative}")
    batch = repository / "tests/fixtures/v6_recapture_batch/batch.json"
    if sha256_file(batch) != BATCH_SHA256:
        raise ValueError("canonical v6 batch manifest digest changed")
    return lock
