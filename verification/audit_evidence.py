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

from verification import artifact_sources, build_artifacts, run_independent_green

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
        unprefixed_hash = archive.get("unprefixed_git_archive_sha256")
        if unprefixed_hash is not None and re.fullmatch(
            r"[0-9a-f]{64}", str(unprefixed_hash)
        ) is None:
            raise EvidenceAuditError(f"{name} unprefixed source hash is malformed")
        excluded_links = build_artifacts._excluded_unsafe_links(
            archive_path, str(archive.get("prefix"))
        )
        if archive.get("excluded_unsafe_links") != excluded_links:
            raise EvidenceAuditError(f"{name} excluded unsafe-link inventory mismatch")
        history = row.get("history")
        if name == "codegen":
            if not isinstance(history, dict):
                raise EvidenceAuditError("codegen dependency row omits its history input")
            if history.get("commit") != commit:
                raise EvidenceAuditError("codegen history does not name C_prod")
            required_commits = history.get("required_commits")
            if (
                not isinstance(required_commits, dict)
                or required_commits.get("c_prod") != commit
            ):
                raise EvidenceAuditError("codegen history omits its closed commit inventory")
            bundle = _artifact_path(
                artifact_root,
                history.get("filename"),
                label="codegen history bundle",
            )
            if _sha256(bundle) != history.get("sha256"):
                raise EvidenceAuditError("codegen history bundle hash mismatch")
        elif history is not None:
            raise EvidenceAuditError(f"{name} dependency row has an unexpected history input")
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
    source_manifest = artifact_root / "artifact-source-inputs.json"
    try:
        source_inputs = artifact_sources.load_artifact_source_inputs(
            {artifact_sources.ARTIFACT_SOURCE_INPUTS: str(source_manifest)}
        )
    except artifact_sources.ArtifactSourceInputError as error:
        raise EvidenceAuditError(f"artifact source inputs are invalid: {error}") from error
    if source_inputs.codegen_commit != c_prod:
        raise EvidenceAuditError("artifact source inputs do not name C_prod")
    if source_inputs.agentic_commit != inputs["agentic"].get("commit"):
        raise EvidenceAuditError("artifact source inputs do not name A_final")
    source_payload = _load_json(source_manifest)
    expected_source_payload = {
        "schema_version": artifact_sources.SCHEMA_VERSION,
        "agentic_source": {
            "root": inputs["agentic"]["extracted_root"],
            "commit": inputs["agentic"]["commit"],
            "archive": inputs["agentic"]["archive"]["filename"],
            "archive_sha256": inputs["agentic"]["archive"]["sha256"],
        },
        "codegen_source": {
            "root": inputs["codegen"]["extracted_root"],
            "commit": inputs["codegen"]["commit"],
            "archive": inputs["codegen"]["archive"]["filename"],
            "archive_sha256": inputs["codegen"]["archive"]["sha256"],
        },
        "codegen_history": {
            "root": inputs["codegen"]["history"]["extracted_root"],
            "commit": inputs["codegen"]["history"]["commit"],
            "bundle": inputs["codegen"]["history"]["filename"],
            "bundle_sha256": inputs["codegen"]["history"]["sha256"],
            "required_commits": inputs["codegen"]["history"]["required_commits"],
        },
    }
    if source_payload != expected_source_payload:
        raise EvidenceAuditError("artifact source inputs differ from dependencies.json")
    expected_roots = {
        "agentic source": artifact_root / str(inputs["agentic"].get("extracted_root")),
        "codegen source": artifact_root / str(inputs["codegen"].get("extracted_root")),
        "codegen history": artifact_root
        / str(inputs["codegen"]["history"].get("extracted_root")),
    }
    actual_roots = {
        "agentic source": source_inputs.agentic_source,
        "codegen source": source_inputs.codegen_source,
        "codegen history": source_inputs.codegen_history,
    }
    for label, expected in expected_roots.items():
        if actual_roots[label] != expected.resolve():
            raise EvidenceAuditError(
                f"artifact source manifest {label} differs from dependencies.json"
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
        history_record = codegen.get("history")
        if not isinstance(history_record, dict):
            raise EvidenceAuditError("C_prod dependency row has no history input")
        rebuilt_bundle = root / Path(str(history_record["filename"])).name
        required_commits = history_record.get("required_commits")
        if not isinstance(required_commits, dict):
            raise EvidenceAuditError("C_prod history has no required commit inventory")
        try:
            rebuilt_history = build_artifacts._deterministic_history_bundle(
                repository, required_commits, rebuilt_bundle
            )
            build_artifacts._extract_history_bundle(
                rebuilt_bundle, root / "history-extracted", required_commits
            )
        except build_artifacts.ArtifactContractError as error:
            raise EvidenceAuditError(f"C_prod history rebuild failed: {error}") from error
        if (
            rebuilt_history["filename"] != history_record["filename"]
            or rebuilt_history["sha256"] != history_record["sha256"]
        ):
            raise EvidenceAuditError("rebuilt C_prod history identity/hash mismatch")
        recorded_bundle = _artifact_path(
            artifact_root,
            history_record["filename"],
            label="certified C_prod history bundle",
        )
        if _sha256(recorded_bundle) != rebuilt_history["sha256"]:
            raise EvidenceAuditError("certified C_prod history differs from reconstruction")
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


def verify_retained_run_artifacts(artifact_root: Path, record: dict[str, Any]) -> None:
    """Recompute the three retained subprocess/probe files for one run."""
    run_id = record.get("id", "<unnamed>")
    retained_paths: dict[str, Path] = {}
    for field in ("stdout", "stderr", "import_probe"):
        retained = record.get(field)
        if not isinstance(retained, dict):
            raise EvidenceAuditError(f"{run_id}: retained {field} record is missing")
        path = _artifact_path(
            artifact_root,
            retained.get("path"),
            label=f"{run_id} retained {field}",
        )
        if _sha256(path) != retained.get("sha256"):
            raise EvidenceAuditError(f"{run_id}: retained {field} hash mismatch")
        retained_paths[field] = path
    junit_record = record.get("junit")
    junit: Path | None = None
    if junit_record is not None:
        if not isinstance(junit_record, dict):
            raise EvidenceAuditError(f"{run_id}: retained JUnit record is malformed")
        junit = _artifact_path(
            artifact_root,
            junit_record.get("path"),
            label=f"{run_id} retained JUnit",
        )
        if _sha256(junit) != junit_record.get("sha256"):
            raise EvidenceAuditError(f"{run_id}: JUnit hash mismatch")
    output_hash = run_independent_green._output_hash(
        artifact_root=artifact_root,
        stdout=retained_paths["stdout"].read_text(),
        stderr=retained_paths["stderr"].read_text(),
        junit=junit,
    )
    if output_hash != record.get("output_sha256"):
        raise EvidenceAuditError(f"{run_id}: normalized output hash mismatch")


def _verify_wheelhouse(
    repository: Path, artifact_root: Path, dependencies: dict[str, Any]
) -> None:
    wheelhouse = dependencies.get("wheelhouse")
    if not isinstance(wheelhouse, dict):
        raise EvidenceAuditError("dependencies.json omits the wheelhouse")
    relative = Path(str(wheelhouse.get("directory", "")))
    if relative.is_absolute() or ".." in relative.parts:
        raise EvidenceAuditError("wheelhouse directory must be artifact-root-relative")
    root = artifact_root / relative
    files = wheelhouse.get("files")
    if not isinstance(files, dict) or not files:
        raise EvidenceAuditError("wheelhouse inventory is empty")
    actual = {path.name: _sha256(path) for path in root.glob("*.whl")}
    if actual != files:
        raise EvidenceAuditError("wheelhouse file inventory/hash mismatch")
    requirements = repository / "verification/wheelhouse-requirements.txt"
    for filename, digest in files.items():
        name = filename.partition("-")[0].replace("_", "-")
        text = requirements.read_text()
        if name not in text or f"--hash=sha256:{digest}" not in text:
            raise EvidenceAuditError(
                f"wheelhouse requirements omit {filename} and its exact hash"
            )


def _verify_lock_and_runs(repository: Path, artifact_root: Path) -> None:
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
    if report.get("artifact_build_sha256") != _sha256(
        artifact_root / "artifact-build.json"
    ):
        raise EvidenceAuditError("independent-green artifact-build hash mismatch")
    runner = report.get("committed_runner")
    if not isinstance(runner, dict):
        raise EvidenceAuditError("independent-green omits its committed runner")
    runner_path = _artifact_path(
        artifact_root, runner.get("path"), label="committed runner"
    )
    if _sha256(runner_path) != runner.get("sha256"):
        raise EvidenceAuditError("committed runner hash mismatch")
    runs = report.get("runs")
    if not isinstance(runs, list) or not runs:
        raise EvidenceAuditError("independent-green.json contains no runs")
    for record in runs:
        try:
            run_independent_green.validate_run_record(record)
        except run_independent_green.IndependentRunError as error:
            raise EvidenceAuditError(str(error)) from error
        verify_retained_run_artifacts(artifact_root, record)
    dependencies = _load_json(repository / "verification/dependencies.json")
    _verify_wheelhouse(repository, artifact_root, dependencies)
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

    _verify_lock_and_runs(root, artifact_root)
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
