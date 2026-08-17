"""Validate explicit, hash-identified source inputs used by artifact verification."""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from collections.abc import Mapping
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

ARTIFACT_SOURCE_INPUTS = "STOP_PARSER_ARTIFACT_SOURCE_INPUTS"
SCHEMA_VERSION = "stop-parser-artifact-source-inputs/v1"
_COMMIT = re.compile(r"[0-9a-f]{40}")
_DIGEST = re.compile(r"[0-9a-f]{64}")


class ArtifactSourceInputError(RuntimeError):
    """An external source/history input was absent, mutable, or misidentified."""


@dataclass(frozen=True)
class ArtifactSourceInputs:
    """The three roots admitted by one immutable artifact-source manifest."""

    manifest: Path
    agentic_source: Path
    agentic_commit: str
    codegen_source: Path
    codegen_commit: str
    codegen_history: Path
    codegen_history_commits: tuple[tuple[str, str], ...]


def _object(value: object, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ArtifactSourceInputError(f"{label} must be an object")
    return value


def _artifact_member(root: Path, value: object, label: str, *, directory: bool) -> Path:
    if not isinstance(value, str) or not value:
        raise ArtifactSourceInputError(f"{label} must be a non-empty relative path")
    relative = Path(value)
    if relative.is_absolute() or ".." in relative.parts:
        raise ArtifactSourceInputError(f"{label} must be artifact-root-relative")
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ArtifactSourceInputError(f"{label} escapes the artifact root")
    exists = path.is_dir() if directory else path.is_file()
    if not exists:
        kind = "directory" if directory else "file"
        raise ArtifactSourceInputError(f"{label} is not a {kind}: {path}")
    return path


def _commit(value: object, label: str) -> str:
    if not isinstance(value, str) or _COMMIT.fullmatch(value) is None:
        raise ArtifactSourceInputError(f"{label} must be a full commit SHA")
    return value


def _digest(value: object, label: str) -> str:
    if not isinstance(value, str) or _DIGEST.fullmatch(value) is None:
        raise ArtifactSourceInputError(f"{label} must be a SHA-256")
    return value


def _require_layout(value: object, expected: tuple[str, ...], label: str) -> None:
    if not isinstance(value, str):
        raise ArtifactSourceInputError(f"{label} must be a relative path")
    parts = Path(value).parts
    if parts[: len(expected)] != expected:
        raise ArtifactSourceInputError(
            f"{label} must be under {'/'.join(expected)}, found {value!r}"
        )


def _source_row(root: Path, payload: dict[str, Any], name: str) -> tuple[Path, str]:
    row = _object(payload.get(name), name)
    if set(row) != {"root", "commit", "archive", "archive_sha256"}:
        raise ArtifactSourceInputError(f"{name} must contain the closed source fields")
    commit = _commit(row.get("commit"), f"{name}.commit")
    digest = _digest(row.get("archive_sha256"), f"{name}.archive_sha256")
    role = name.removesuffix("_source")
    _require_layout(row.get("root"), ("extracted", role), f"{name}.root")
    if len(Path(str(row.get("root"))).parts) != 3:
        raise ArtifactSourceInputError(f"{name}.root must name one extracted archive root")
    _require_layout(row.get("archive"), ("sources",), f"{name}.archive")
    if len(Path(str(row.get("archive"))).parts) != 2:
        raise ArtifactSourceInputError(f"{name}.archive must name one source archive")
    archive = _artifact_member(root, row.get("archive"), f"{name}.archive", directory=False)
    actual = hashlib.sha256(archive.read_bytes()).hexdigest()
    if actual != digest:
        raise ArtifactSourceInputError(
            f"{name}.archive hash mismatch: expected {digest}, found {actual}"
        )
    source = _artifact_member(root, row.get("root"), f"{name}.root", directory=True)
    return source, commit


def _history_row(
    root: Path, payload: dict[str, Any]
) -> tuple[Path, str, tuple[tuple[str, str], ...]]:
    row = _object(payload.get("codegen_history"), "codegen_history")
    if set(row) != {
        "root",
        "commit",
        "bundle",
        "bundle_sha256",
        "required_commits",
    }:
        raise ArtifactSourceInputError(
            "codegen_history must contain the closed history fields"
        )
    commit = _commit(row.get("commit"), "codegen_history.commit")
    digest = _digest(row.get("bundle_sha256"), "codegen_history.bundle_sha256")
    if row.get("root") != "history-extracted/codegen":
        raise ArtifactSourceInputError(
            "codegen_history.root must be history-extracted/codegen"
        )
    _require_layout(row.get("bundle"), ("history",), "codegen_history.bundle")
    if len(Path(str(row.get("bundle"))).parts) != 2:
        raise ArtifactSourceInputError("codegen_history.bundle must name one history bundle")
    bundle = _artifact_member(
        root, row.get("bundle"), "codegen_history.bundle", directory=False
    )
    actual = hashlib.sha256(bundle.read_bytes()).hexdigest()
    if actual != digest:
        raise ArtifactSourceInputError(
            f"codegen_history.bundle hash mismatch: expected {digest}, found {actual}"
        )
    history = _artifact_member(
        root, row.get("root"), "codegen_history.root", directory=True
    )
    try:
        head = subprocess.run(
            ["git", "-C", str(history), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except subprocess.CalledProcessError as error:
        raise ArtifactSourceInputError(
            f"codegen_history.root is not a readable Git history: {history}"
        ) from error
    if head != commit:
        raise ArtifactSourceInputError(
            f"codegen_history.root is {head}, expected exact commit {commit}"
        )
    required = _object(row.get("required_commits"), "codegen_history.required_commits")
    if not required or required.get("c_prod") != commit:
        raise ArtifactSourceInputError(
            "codegen_history.required_commits must bind c_prod to the source commit"
        )
    commits = tuple(
        (name, _commit(value, f"codegen_history.required_commits.{name}"))
        for name, value in sorted(required.items())
    )
    for name, required_commit in commits:
        try:
            subprocess.run(
                ["git", "-C", str(history), "cat-file", "-e", f"{required_commit}^{{commit}}"],
                check=True,
                capture_output=True,
            )
        except subprocess.CalledProcessError as error:
            raise ArtifactSourceInputError(
                f"codegen history omits required commit {name}={required_commit}"
            ) from error
    return history, commit, commits


@lru_cache(maxsize=4)
def _load(manifest: Path) -> ArtifactSourceInputs:
    try:
        payload = json.loads(manifest.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise ArtifactSourceInputError(f"cannot read artifact source inputs: {error}") from error
    record = _object(payload, "artifact source inputs")
    if record.get("schema_version") != SCHEMA_VERSION:
        raise ArtifactSourceInputError(f"artifact source schema must be {SCHEMA_VERSION}")
    if set(record) != {
        "schema_version",
        "agentic_source",
        "codegen_source",
        "codegen_history",
    }:
        raise ArtifactSourceInputError("artifact source inputs must contain the closed three rows")
    root = manifest.parent.resolve()
    agentic, agentic_commit = _source_row(root, record, "agentic_source")
    codegen, codegen_commit = _source_row(root, record, "codegen_source")
    history, history_commit, history_commits = _history_row(root, record)
    if history_commit != codegen_commit:
        raise ArtifactSourceInputError("codegen source and history commits differ")
    required = ("src/agentic_mbse", "claude", ".claude", "docs", "project_templates")
    missing = [relative for relative in required if not (agentic / relative).is_dir()]
    if missing:
        raise ArtifactSourceInputError(f"agentic_source.root omits {missing}")
    return ArtifactSourceInputs(
        manifest=manifest,
        agentic_source=agentic,
        agentic_commit=agentic_commit,
        codegen_source=codegen,
        codegen_commit=codegen_commit,
        codegen_history=history,
        codegen_history_commits=history_commits,
    )


def load_artifact_source_inputs(
    environment: Mapping[str, str] = os.environ,
) -> ArtifactSourceInputs:
    """Load the one explicit manifest; there is no checkout or sibling fallback."""
    raw = environment.get(ARTIFACT_SOURCE_INPUTS)
    if not raw:
        raise ArtifactSourceInputError(
            f"{ARTIFACT_SOURCE_INPUTS} must name the hash-identified source manifest"
        )
    return _load(Path(raw).expanduser().resolve())


def require_codegen_source(codegen_root: Path) -> ArtifactSourceInputs:
    """Admit inputs only when the running codegen tree is the declared extraction."""
    inputs = load_artifact_source_inputs()
    actual = codegen_root.resolve()
    if actual != inputs.codegen_source:
        raise ArtifactSourceInputError(
            f"codegen source root {actual} differs from {inputs.codegen_source}"
        )
    return inputs


def agentic_source_root(codegen_root: Path) -> Path:
    """Return the exact agentic source paired with a declared codegen extraction."""
    return require_codegen_source(codegen_root).agentic_source


def codegen_history_root(codegen_root: Path) -> Path:
    """Return the exact history paired with a declared codegen extraction."""
    return require_codegen_source(codegen_root).codegen_history
