"""Validate execution imports against the immutable artifact provenance file."""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

CODEGEN_EXECUTION_PROVENANCE = "CODEGEN_EXECUTION_PROVENANCE"
SCHEMA_VERSION = "stop-parser-execution-provenance/v1"
_FULL_COMMIT = re.compile(r"[0-9a-f]{40}")
_SHA256 = re.compile(r"[0-9a-f]{64}")


class ExecutionProvenanceError(RuntimeError):
    """The execution lane was not bound to a complete immutable artifact set."""


@dataclass(frozen=True)
class ExecutionProvenance:
    """The four exact roots and interpreter admitted by the execution lane."""

    manifest_path: Path
    manifest_sha256: str
    python_executable: Path
    codegen_source_root: Path
    agentic_install_root: Path
    teax_source_root: Path
    teax_simkit_root: Path


def _object(value: object, *, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ExecutionProvenanceError(f"{label} must be an object")
    return value


def _identity_root(
    roots: dict[str, Any],
    name: str,
    *,
    artifact_root: Path,
    hash_field: str,
    package: str | None = None,
) -> tuple[Path, str, str]:
    row = _object(roots.get(name), label=f"roots.{name}")
    commit = row.get("commit")
    digest = row.get(hash_field)
    if not isinstance(commit, str) or _FULL_COMMIT.fullmatch(commit) is None:
        raise ExecutionProvenanceError(f"roots.{name}.commit must be a full commit SHA")
    if not isinstance(digest, str) or _SHA256.fullmatch(digest) is None:
        raise ExecutionProvenanceError(f"roots.{name}.{hash_field} must be a SHA-256")
    raw_artifact = row.get("artifact_path")
    if not isinstance(raw_artifact, str) or not raw_artifact:
        raise ExecutionProvenanceError(
            f"roots.{name}.artifact_path must be a non-empty path"
        )
    artifact = Path(raw_artifact).expanduser().resolve()
    if not artifact.is_relative_to(artifact_root) or not artifact.is_file():
        raise ExecutionProvenanceError(
            f"roots.{name}.artifact_path is outside the artifact root: {artifact}"
        )
    actual_digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
    if actual_digest != digest:
        raise ExecutionProvenanceError(
            f"roots.{name} artifact hash mismatch: expected {digest}, found {actual_digest}"
        )
    raw_path = row.get("path")
    if not isinstance(raw_path, str) or not raw_path:
        raise ExecutionProvenanceError(f"roots.{name}.path must be a non-empty path")
    root = Path(raw_path).expanduser().resolve()
    if not root.is_dir():
        raise ExecutionProvenanceError(f"roots.{name}.path is not a directory: {root}")
    if package is not None and not (root / package / "__init__.py").is_file():
        raise ExecutionProvenanceError(
            f"roots.{name}.path does not contain {package}/__init__.py: {root}"
        )
    return root, commit, digest


def load_execution_provenance(
    environment: Mapping[str, str],
) -> ExecutionProvenance:
    """Load and close the one manifest named by the execution environment."""
    raw_manifest = environment.get(CODEGEN_EXECUTION_PROVENANCE)
    if not raw_manifest:
        raise ExecutionProvenanceError(
            f"{CODEGEN_EXECUTION_PROVENANCE} must name the artifact provenance file"
        )
    manifest = Path(raw_manifest).expanduser().resolve()
    try:
        payload_bytes = manifest.read_bytes()
        payload = json.loads(payload_bytes)
    except (OSError, json.JSONDecodeError) as error:
        raise ExecutionProvenanceError(f"cannot read provenance {manifest}: {error}") from error
    record = _object(payload, label="execution provenance")
    if record.get("schema_version") != SCHEMA_VERSION:
        raise ExecutionProvenanceError(
            f"execution provenance schema must be {SCHEMA_VERSION}"
        )
    raw_artifact_root = record.get("artifact_root")
    if not isinstance(raw_artifact_root, str) or not raw_artifact_root:
        raise ExecutionProvenanceError("artifact_root must be a non-empty path")
    artifact_root = Path(raw_artifact_root).expanduser().resolve()
    if not artifact_root.is_dir():
        raise ExecutionProvenanceError(
            f"artifact_root is not a directory: {artifact_root}"
        )
    python = _object(record.get("python"), label="python")
    executable = python.get("executable")
    version = python.get("version")
    if not isinstance(executable, str) or not executable:
        raise ExecutionProvenanceError("python.executable must be a non-empty path")
    if not isinstance(version, str) or not version:
        raise ExecutionProvenanceError("python.version must be recorded")

    roots = _object(record.get("roots"), label="roots")
    if set(roots) != {
        "codegen_source",
        "agentic_install",
        "teax_source",
        "teax_simkit",
    }:
        raise ExecutionProvenanceError("roots must contain the four closed artifact roots")
    codegen, _codegen_commit, _codegen_hash = _identity_root(
        roots,
        "codegen_source",
        artifact_root=artifact_root,
        hash_field="archive_sha256",
        package="sysml_codegen",
    )
    agentic, _agentic_commit, _agentic_hash = _identity_root(
        roots,
        "agentic_install",
        artifact_root=artifact_root,
        hash_field="wheel_sha256",
        package="agentic_mbse",
    )
    teax, teax_commit, teax_hash = _identity_root(
        roots,
        "teax_source",
        artifact_root=artifact_root,
        hash_field="archive_sha256",
    )
    simkit, simkit_commit, simkit_hash = _identity_root(
        roots,
        "teax_simkit",
        artifact_root=artifact_root,
        hash_field="archive_sha256",
        package="simkit",
    )
    if not simkit.is_relative_to(teax):
        raise ExecutionProvenanceError("the simkit root is outside the recorded TEAx source")
    if (simkit_commit, simkit_hash) != (teax_commit, teax_hash):
        raise ExecutionProvenanceError("the simkit and TEAx identities differ")
    return ExecutionProvenance(
        manifest_path=manifest,
        manifest_sha256=hashlib.sha256(payload_bytes).hexdigest(),
        python_executable=Path(executable).expanduser().resolve(),
        codegen_source_root=codegen,
        agentic_install_root=agentic,
        teax_source_root=teax,
        teax_simkit_root=simkit,
    )


def environment_pin_problems(
    resolved: Mapping[str, str], provenance: ExecutionProvenance
) -> list[str]:
    """Return one problem for every interpreter or import outside its recorded root."""
    expected = {
        "sysml_codegen": provenance.codegen_source_root,
        "agentic_mbse": provenance.agentic_install_root,
        "simkit": provenance.teax_simkit_root,
    }
    problems: list[str] = []
    python = resolved.get("python")
    if python is None or Path(python).resolve() != provenance.python_executable:
        problems.append(
            f"python resolved outside the recorded executable: {python!r}"
        )
    for name, root in expected.items():
        imported = resolved.get(name)
        if imported is None or not Path(imported).resolve().is_relative_to(root):
            problems.append(f"{name} resolved outside {root}: {imported!r}")
    return problems
