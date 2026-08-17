#!/usr/bin/env python3
"""Audit the direct-child evidence commit and reconstruct its immutable artifact claims."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
import tomllib
import zipfile
from pathlib import Path
from typing import Any

from verification import build_artifacts, run_independent_green

EXACT_EVIDENCE_PATHS = frozenset(
    {
        "verification/dependencies.json",
        "verification/wheelhouse-requirements.txt",
        "verification/execution-provenance.json",
        "verification/independent-green.json",
        "verification/reconciliation-ledger.md",
        "verification/evidence-lock.json",
    }
)
_FULL_SHA = re.compile(r"[0-9a-f]{40}")


class EvidenceAuditError(RuntimeError):
    """Final evidence is not an acyclic, reconstructable child of production."""


def _run(*command: str) -> str:
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as error:
        detail = (error.stderr or error.stdout or "").strip()
        raise EvidenceAuditError(
            f"command failed ({' '.join(command)}): {detail or error.returncode}"
        ) from error
    return result.stdout.strip()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise EvidenceAuditError(f"cannot read JSON evidence {path}: {error}") from error
    if not isinstance(value, dict):
        raise EvidenceAuditError(f"JSON evidence must be an object: {path}")
    return value


def _full_sha(value: str, *, label: str) -> str:
    if _FULL_SHA.fullmatch(value) is None:
        raise EvidenceAuditError(f"{label} must be a full 40 lowercase hexadecimal commit SHA")
    return value


def verify_commit_boundary(repository: Path, c_prod: str, c_evidence: str) -> dict[str, object]:
    """Prove exact parenthood and the closed six-path production/evidence boundary."""
    production = _full_sha(c_prod, label="C_prod")
    evidence = _full_sha(c_evidence, label="C_evidence")
    root = repository.resolve()
    parent = _run("git", "-C", str(root), "rev-parse", f"{evidence}^")
    if parent != production:
        raise EvidenceAuditError(
            f"evidence parent mismatch: expected C_prod {production}, found {parent}"
        )
    changed = {
        line
        for line in _run(
            "git", "-C", str(root), "diff", "--name-only", production, evidence
        ).splitlines()
        if line
    }
    if changed != EXACT_EVIDENCE_PATHS:
        raise EvidenceAuditError(
            "evidence changed-path set mismatch: "
            f"expected {sorted(EXACT_EVIDENCE_PATHS)}, found {sorted(changed)}"
        )
    return {"parent": parent, "changed_paths": sorted(changed)}


def verify_no_evidence_self_reference(repository: Path, c_evidence: str) -> None:
    """Reject the evidence commit identity from every file it contains."""
    candidate = _full_sha(c_evidence, label="C_evidence")
    for relative in sorted(EXACT_EVIDENCE_PATHS):
        path = repository / relative
        if not path.is_file():
            raise EvidenceAuditError(f"evidence path is missing: {relative}")
        if candidate.encode() in path.read_bytes():
            raise EvidenceAuditError(f"evidence self-reference found in {relative}")


def _wheel_metadata(path: Path) -> tuple[str, str]:
    try:
        with zipfile.ZipFile(path) as archive:
            names = [name for name in archive.namelist() if name.endswith(".dist-info/METADATA")]
            if len(names) != 1:
                raise EvidenceAuditError(f"wheel has {len(names)} METADATA files: {path}")
            lines = archive.read(names[0]).decode().splitlines()
    except (OSError, UnicodeDecodeError, zipfile.BadZipFile) as error:
        raise EvidenceAuditError(f"invalid wheel {path}: {error}") from error
    fields: dict[str, str] = {}
    for line in lines:
        if ": " in line:
            key, value = line.split(": ", 1)
            fields.setdefault(key, value)
    if "Name" not in fields or "Version" not in fields:
        raise EvidenceAuditError(f"wheel metadata omits Name or Version: {path}")
    return fields["Name"], fields["Version"]


def _normalized_distribution(value: str) -> str:
    return re.sub(r"[-_.]+", "-", value).lower()


def verify_wheel(
    path: Path,
    *,
    distribution: str,
    version: str,
    sha256: str,
) -> None:
    """Require file hash and embedded distribution/version identity together."""
    actual_hash = _sha256(path)
    if actual_hash != sha256:
        raise EvidenceAuditError(
            f"wheel hash mismatch for {path.name}: expected {sha256}, found {actual_hash}"
        )
    actual_distribution, actual_version = _wheel_metadata(path)
    if _normalized_distribution(actual_distribution) != _normalized_distribution(distribution):
        raise EvidenceAuditError(
            f"wheel distribution mismatch: expected {distribution}, found {actual_distribution}"
        )
    if actual_version != version:
        raise EvidenceAuditError(
            f"wheel version mismatch: expected {version}, found {actual_version}"
        )


def _artifact_path(root: Path, value: object, *, label: str) -> Path:
    relative = Path(str(value))
    if relative.is_absolute() or ".." in relative.parts:
        raise EvidenceAuditError(f"{label} must be artifact-root-relative")
    result = root / relative
    if not result.is_file():
        raise EvidenceAuditError(f"{label} is missing: {result}")
    return result


def _verify_dependencies(
    repository: Path, artifact_root: Path, c_prod: str, f_final: str
) -> dict[str, Any]:
    dependencies = _load_json(repository / "verification/dependencies.json")
    if dependencies.get("schema_version") != "stop-parser-dependencies/v1":
        raise EvidenceAuditError("dependencies.json has the wrong schema")
    inputs = dependencies.get("inputs")
    if not isinstance(inputs, dict) or set(inputs) != set(build_artifacts.REPOSITORY_NAMES):
        raise EvidenceAuditError("dependencies.json must contain exactly five repository inputs")
    if inputs["codegen"].get("commit") != c_prod:
        raise EvidenceAuditError("dependencies.json codegen row does not name C_prod")
    if inputs["fusion"].get("commit") != f_final:
        raise EvidenceAuditError("dependencies.json Fusion row does not name F_final")
    for name in build_artifacts.REPOSITORY_NAMES:
        row = inputs[name]
        commit = row.get("commit")
        _full_sha(str(commit), label=f"{name} dependency commit")
        archive = row.get("archive")
        if not isinstance(archive, dict):
            raise EvidenceAuditError(f"{name} dependency row omits its archive")
        archive_path = _artifact_path(
            artifact_root, archive.get("filename"), label=f"{name} source archive"
        )
        if _sha256(archive_path) != archive.get("sha256"):
            raise EvidenceAuditError(f"{name} source archive hash mismatch")
        wheel = row.get("wheel")
        if wheel is not None:
            if not isinstance(wheel, dict):
                raise EvidenceAuditError(f"{name} wheel record must be an object or null")
            wheel_path = _artifact_path(
                artifact_root,
                f"wheels/{wheel.get('filename')}",
                label=f"{name} wheel",
            )
            verify_wheel(
                wheel_path,
                distribution=str(wheel.get("distribution")),
                version=str(wheel.get("version")),
                sha256=str(wheel.get("sha256")),
            )
    return inputs


def _rebuild_codegen(
    repository: Path,
    artifact_root: Path,
    codegen: dict[str, Any],
    c_prod: str,
) -> None:
    archive_record = codegen["archive"]
    with tempfile.TemporaryDirectory(prefix="stop-parser-audit-codegen-") as temporary:
        root = Path(temporary)
        rebuilt_archive = root / Path(archive_record["filename"]).name
        build_artifacts._git_archive(
            repository,
            c_prod,
            str(archive_record["prefix"]),
            rebuilt_archive,
        )
        if _sha256(rebuilt_archive) != archive_record["sha256"]:
            raise EvidenceAuditError("rebuilt C_prod source archive hash mismatch")
        extracted = build_artifacts._extract_archive(
            rebuilt_archive,
            root / "extracted",
            str(archive_record["prefix"]),
        )
        wheel = codegen.get("wheel")
        if wheel is None:
            raise EvidenceAuditError("C_prod dependency row has no certified wheel")
        timestamp = _run(
            "git", "-C", str(repository), "show", "-s", "--format=%ct", c_prod
        )
        try:
            rebuilt = build_artifacts._deterministic_wheel(
                extracted,
                root / "wheels",
                distribution=str(wheel["distribution"]),
                version=str(wheel["version"]),
                source_date_epoch=timestamp,
            )
        except build_artifacts.ArtifactContractError as error:
            raise EvidenceAuditError(f"C_prod wheel rebuild failed: {error}") from error
        if rebuilt["filename"] != wheel["filename"] or rebuilt["sha256"] != wheel["sha256"]:
            raise EvidenceAuditError("rebuilt C_prod wheel identity/hash mismatch")
        recorded = _artifact_path(
            artifact_root,
            f"wheels/{wheel['filename']}",
            label="certified C_prod wheel",
        )
        if _sha256(recorded) != rebuilt["sha256"]:
            raise EvidenceAuditError("certified C_prod wheel differs from reconstruction")


def _read_fusion_sources(artifact_root: Path, fusion: dict[str, Any]) -> tuple[str, str]:
    relative = Path(str(fusion.get("extracted_root", "")))
    if relative.is_absolute() or ".." in relative.parts:
        raise EvidenceAuditError("Fusion extracted root must be artifact-root-relative")
    root = artifact_root / relative
    pyproject = root / "pyproject.toml"
    lock = root / "uv.lock"
    if not pyproject.is_file() or not lock.is_file():
        raise EvidenceAuditError("Fusion artifact omits pyproject.toml or uv.lock")
    return pyproject.read_text(), lock.read_text()


def _verify_fusion_pins(
    repository: Path,
    artifact_root: Path,
    inputs: dict[str, Any],
    c_prod: str,
    c_evidence: str,
) -> None:
    pyproject_text, lock_text = _read_fusion_sources(artifact_root, inputs["fusion"])
    try:
        pyproject = tomllib.loads(pyproject_text)
    except tomllib.TOMLDecodeError as error:
        raise EvidenceAuditError(f"Fusion pyproject is invalid: {error}") from error
    sources = pyproject.get("tool", {}).get("uv", {}).get("sources", {})
    expected = {
        "agentic-mbse": inputs["agentic"]["commit"],
        "sysml-codegen": c_prod,
        "1costingfe": inputs["costingfe"]["commit"],
    }
    for package, commit in expected.items():
        row = sources.get(package)
        if not isinstance(row, dict) or row.get("rev") != commit or not row.get("git"):
            raise EvidenceAuditError(f"Fusion source pin for {package} does not name {commit}")
        if "path" in row or row.get("editable"):
            raise EvidenceAuditError(f"Fusion source pin for {package} is editable or path-based")
        if commit not in lock_text:
            raise EvidenceAuditError(f"Fusion lock omits full {package} commit {commit}")
    joined = pyproject_text + "\n" + lock_text
    if c_evidence in joined:
        raise EvidenceAuditError("Fusion project or lock pins C_evidence")
    if "editable =" in lock_text:
        raise EvidenceAuditError("Fusion lock contains an editable source")
    provenance = _load_json(repository / "verification/execution-provenance.json")
    installed = provenance.get("installed_artifacts", {})
    codegen_wheel = inputs["codegen"].get("wheel")
    if not isinstance(installed, dict) or not isinstance(codegen_wheel, dict):
        raise EvidenceAuditError("execution provenance omits installed codegen wheel")
    if installed.get("sysml-codegen", {}).get("sha256") != codegen_wheel.get("sha256"):
        raise EvidenceAuditError("Fusion run used a different codegen wheel hash")


def _verify_lock_and_runs(repository: Path) -> None:
    lock = _load_json(repository / "verification/evidence-lock.json")
    if lock.get("schema_version") != "stop-parser-evidence-lock/v1":
        raise EvidenceAuditError("evidence-lock.json has the wrong schema")
    files = lock.get("files")
    if not isinstance(files, dict):
        raise EvidenceAuditError("evidence-lock.json omits its files map")
    expected = {
        *(f"verification/{name}" for name in run_independent_green.EVIDENCE_SIBLINGS),
        *run_independent_green.PRODUCTION_LOCK_INPUTS,
    }
    if set(files) != expected or "verification/evidence-lock.json" in files:
        raise EvidenceAuditError(
            "evidence lock coverage is not exactly five siblings plus two inputs"
        )
    for relative, expected_hash in files.items():
        if _sha256(repository / relative) != expected_hash:
            raise EvidenceAuditError(f"evidence lock hash mismatch: {relative}")
    report = _load_json(repository / "verification/independent-green.json")
    if report.get("schema_version") != run_independent_green.RUN_SCHEMA_VERSION:
        raise EvidenceAuditError("independent-green.json has the wrong schema")
    if set(report.get("input_repositories", [])) != set(build_artifacts.REPOSITORY_NAMES):
        raise EvidenceAuditError("independent-green.json does not cover five inputs")
    runs = report.get("runs")
    if not isinstance(runs, list) or not runs:
        raise EvidenceAuditError("independent-green.json contains no runs")
    for record in runs:
        try:
            run_independent_green.validate_run_record(record)
        except run_independent_green.IndependentRunError as error:
            raise EvidenceAuditError(str(error)) from error
    ledger = (repository / "verification/reconciliation-ledger.md").read_text()
    required = {*(f"L-{number:02d}" for number in range(1, 15)), "U-1", "U-2"}
    missing = sorted(row for row in required if row not in ledger)
    if missing:
        raise EvidenceAuditError(f"reconciliation ledger omits rows: {missing}")


def audit(
    *,
    repository: Path,
    c_prod: str,
    f_final: str,
    c_evidence: str,
    artifact_root: Path,
) -> dict[str, str]:
    production = _full_sha(c_prod, label="C_prod")
    fusion = _full_sha(f_final, label="F_final")
    evidence = _full_sha(c_evidence, label="C_evidence")
    root = repository.resolve()
    actual = _run("git", "-C", str(root), "rev-parse", "HEAD")
    if actual != evidence:
        raise EvidenceAuditError(f"audit repository HEAD is {actual}, not C_evidence {evidence}")
    status = _run(
        "git", "-C", str(root), "status", "--porcelain=v1", "--untracked-files=all"
    )
    if status:
        raise EvidenceAuditError(f"audit repository is dirty:\n{status}")

    verify_commit_boundary(root, production, evidence)
    verify_no_evidence_self_reference(root, evidence)
    boundary = "PASS"

    inputs = _verify_dependencies(root, artifact_root, production, fusion)
    _rebuild_codegen(root, artifact_root, inputs["codegen"], production)
    reconstruction = "PASS"

    _verify_fusion_pins(root, artifact_root, inputs, production, evidence)
    fusion_pin = "PASS"

    _verify_lock_and_runs(root)
    artifacts_and_lock = "PASS"
    return {
        "parent_and_paths": boundary,
        "codegen_reconstruction": reconstruction,
        "fusion_pin": fusion_pin,
        "artifacts_and_lock": artifacts_and_lock,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", required=True, type=Path)
    parser.add_argument("--c-prod", required=True)
    parser.add_argument("--f-final", required=True)
    parser.add_argument("--c-evidence", required=True)
    parser.add_argument("--artifact-root", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    results = audit(
        repository=arguments.repository,
        c_prod=arguments.c_prod,
        f_final=arguments.f_final,
        c_evidence=arguments.c_evidence,
        artifact_root=arguments.artifact_root.resolve(),
    )
    for name, status in results.items():
        print(f"{name}: {status}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except EvidenceAuditError as error:
        print(f"EVIDENCE AUDIT REFUSED: {error}", file=sys.stderr)
        raise SystemExit(2) from error
