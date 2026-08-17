#!/usr/bin/env python3
"""Build deterministic source archives and wheels from five explicit Git inputs.

The fixed command line carries immutable identities.  Source locations are supplied separately by
``STOP_PARSER_SOURCE_MANIFEST`` so this tool never guesses a branch or an adjacent checkout.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import tomllib
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any

SCHEMA_VERSION = "stop-parser-artifact-build/v1"
SOURCE_SCHEMA_VERSION = "stop-parser-source-roots/v1"
ARTIFACT_SOURCE_INPUT_SCHEMA_VERSION = "stop-parser-artifact-source-inputs/v1"
REPOSITORY_NAMES = ("agentic", "codegen", "teax", "costingfe", "fusion")
CODEGEN_HISTORY_INPUT_NAMES = frozenset(
    {
        "fingerprint_policy",
        "ledger_base",
        "ledger_candidate",
        "phase1_seed",
        "phase4a_boundary",
    }
)
_FULL_SHA = re.compile(r"[0-9a-f]{40}")


class ArtifactContractError(RuntimeError):
    """An immutable artifact input or output violated the approved contract."""


def _run(*command: str, cwd: Path | None = None, env: dict[str, str] | None = None) -> str:
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            env=env,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as error:
        detail = (error.stderr or error.stdout or "").strip()
        raise ArtifactContractError(
            f"command failed ({' '.join(command)}): {detail or error.returncode}"
        ) from error
    return result.stdout.strip()


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True) + "\n"


def _full_sha(value: str, *, label: str) -> str:
    if _FULL_SHA.fullmatch(value) is None:
        raise ArtifactContractError(f"{label} must be a full 40 lowercase hexadecimal commit SHA")
    return value


def require_clean_commit(repository: Path, commit: str) -> None:
    """Require one explicit clean Git source at exactly ``commit``."""
    expected = _full_sha(commit, label="commit")
    root = repository.resolve()
    if not root.is_dir():
        raise ArtifactContractError(f"source repository does not exist: {root}")
    actual = _run("git", "-C", str(root), "rev-parse", "HEAD")
    if actual != expected:
        raise ArtifactContractError(
            f"source identity mismatch: expected {expected}, found {actual}"
        )
    resolved = _run("git", "-C", str(root), "rev-parse", f"{expected}^{{commit}}")
    if resolved != expected:
        raise ArtifactContractError(f"source commit does not resolve exactly: {expected}")
    status = _run(
        "git",
        "-C",
        str(root),
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
    )
    if status:
        raise ArtifactContractError(f"dirty source repository refused: {root}\n{status}")


def load_source_manifest(path: Path) -> dict[str, dict[str, Any]]:
    """Load the closed, explicit map from repository role to local immutable source."""
    try:
        payload = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise ArtifactContractError(f"cannot read source manifest {path}: {error}") from error
    if payload.get("schema_version") != SOURCE_SCHEMA_VERSION:
        raise ArtifactContractError(
            f"source manifest schema must be {SOURCE_SCHEMA_VERSION!r}"
        )
    rows = payload.get("repositories")
    if not isinstance(rows, dict) or set(rows) != set(REPOSITORY_NAMES):
        raise ArtifactContractError(
            f"source manifest repositories must be exactly {list(REPOSITORY_NAMES)}"
        )
    result: dict[str, dict[str, Any]] = {}
    for name in REPOSITORY_NAMES:
        raw = rows[name]
        if not isinstance(raw, dict):
            raise ArtifactContractError(f"source manifest row {name!r} must be an object")
        source = Path(str(raw.get("path", "")))
        if not source.is_absolute():
            raise ArtifactContractError(f"source manifest path for {name} must be absolute")
        url = raw.get("url")
        version = raw.get("version")
        if not isinstance(url, str) or not url:
            raise ArtifactContractError(f"source manifest row {name!r} has no repository URL")
        if not isinstance(version, str) or not version:
            raise ArtifactContractError(f"source manifest row {name!r} has no declared version")
        wheel_distribution = raw.get("wheel_distribution")
        if wheel_distribution is not None and not isinstance(wheel_distribution, str):
            raise ArtifactContractError(
                f"source manifest wheel_distribution for {name!r} must be a string or null"
            )
        if name == "codegen":
            history_commits = raw.get("history_commits")
            if not isinstance(history_commits, dict) or set(history_commits) != set(
                CODEGEN_HISTORY_INPUT_NAMES
            ):
                raise ArtifactContractError(
                    "codegen source row history_commits must contain the closed retained inputs"
                )
            for label, value in history_commits.items():
                _full_sha(str(value), label=f"codegen history commit {label}")
        elif "history_commits" in raw:
            raise ArtifactContractError(
                f"source manifest row {name!r} cannot declare codegen history"
            )
        result[name] = dict(raw, path=str(source.resolve()))
    return result


def _archive_prefix(name: str, row: dict[str, Any]) -> str:
    prefix = str(row.get("archive_prefix") or f"{name}-{row['version']}")
    candidate = Path(prefix)
    if candidate.is_absolute() or ".." in candidate.parts or len(candidate.parts) != 1:
        raise ArtifactContractError(f"non-portable archive prefix for {name}: {prefix!r}")
    return prefix


def _git_archive(repository: Path, commit: str, prefix: str, output: Path) -> None:
    _run(
        "git",
        "-C",
        str(repository),
        "archive",
        "--format=tar",
        f"--prefix={prefix}/",
        f"--output={output}",
        commit,
    )


def _git_history_bundle(
    repository: Path, commits: dict[str, str], output: Path
) -> None:
    """Write a deterministic v2 bundle for the closed retained commit inventory."""
    header_rows = ["# v2 git bundle"]
    for name, commit in sorted(commits.items()):
        reference = "refs/heads/artifact" if name == "c_prod" else f"refs/heads/retained/{name}"
        header_rows.append(f"{commit} {reference}")
    header = ("\n".join(header_rows) + "\n\n").encode()
    try:
        with output.open("wb") as stream:
            stream.write(header)
            stream.flush()
            result = subprocess.run(
                [
                    "git",
                    "-c",
                    "pack.threads=1",
                    "-C",
                    str(repository),
                    "pack-objects",
                    "--stdout",
                    "--revs",
                ],
                input=("\n".join(sorted(set(commits.values()))) + "\n").encode(),
                stdout=stream,
                stderr=subprocess.PIPE,
                check=False,
            )
    except OSError as error:
        raise ArtifactContractError(f"cannot write codegen history bundle: {error}") from error
    if result.returncode != 0:
        detail = result.stderr.decode(errors="replace").strip()
        raise ArtifactContractError(
            f"codegen history pack failed: {detail or result.returncode}"
        )


def _deterministic_history_bundle(
    repository: Path, commits: dict[str, str], output: Path
) -> dict[str, Any]:
    """Build the codegen history input twice and retain only byte-identical output."""
    with tempfile.TemporaryDirectory(prefix="stop-parser-history-repeat-") as temporary:
        repeated = Path(temporary) / output.name
        _git_history_bundle(repository, commits, output)
        _git_history_bundle(repository, commits, repeated)
        if output.read_bytes() != repeated.read_bytes():
            raise ArtifactContractError("codegen history bundle is not deterministic")
    return {
        "filename": f"history/{output.name}",
        "sha256": _sha256(output),
        "required_commits": dict(sorted(commits.items())),
    }


def _extract_history_bundle(
    bundle: Path, destination: Path, commits: dict[str, str]
) -> Path:
    """Create a no-checkout history root that cannot expose workspace link targets."""
    _run("git", "init", "--quiet", str(destination))
    _run("git", "-C", str(destination), "bundle", "unbundle", str(bundle))
    commit = commits["c_prod"]
    for name, retained_commit in sorted(commits.items()):
        reference = "refs/heads/artifact" if name == "c_prod" else f"refs/heads/retained/{name}"
        _run("git", "-C", str(destination), "update-ref", reference, retained_commit)
    _run(
        "git",
        "-C",
        str(destination),
        "symbolic-ref",
        "HEAD",
        "refs/heads/artifact",
    )
    actual = _run("git", "-C", str(destination), "rev-parse", "HEAD")
    if actual != commit:
        raise ArtifactContractError(
            f"history bundle resolved {actual}, expected exact commit {commit}"
        )
    _run("git", "-C", str(destination), "read-tree", commit)
    for name, retained_commit in sorted(commits.items()):
        actual_retained = _run(
            "git", "-C", str(destination), "rev-parse", f"{retained_commit}^{{commit}}"
        )
        if actual_retained != retained_commit:
            raise ArtifactContractError(
                f"history bundle omitted {name}={retained_commit}"
            )
    return destination


def _normalized_archive_path(path: PurePosixPath) -> PurePosixPath | None:
    parts: list[str] = []
    for part in path.parts:
        if part in ("", "."):
            continue
        if part == "..":
            if not parts:
                return None
            parts.pop()
            continue
        parts.append(part)
    return PurePosixPath(*parts)


def _excluded_unsafe_links(archive: Path, prefix: str) -> list[dict[str, str]]:
    """Describe links that cannot be materialized inside the extracted source root."""
    excluded: list[dict[str, str]] = []
    with tarfile.open(archive, "r:") as bundle:
        for member in bundle.getmembers():
            if not (member.issym() or member.islnk()):
                continue
            target = PurePosixPath(member.linkname)
            if target.is_absolute():
                safe = False
            else:
                base = PurePosixPath(member.name).parent if member.issym() else PurePosixPath()
                normalized = _normalized_archive_path(base / target)
                safe = normalized is not None and normalized.parts[:1] == (prefix,)
            if not safe:
                excluded.append(
                    {
                        "kind": "symlink" if member.issym() else "hardlink",
                        "path": member.name,
                        "target_kind": "absolute" if target.is_absolute() else "escape",
                        "target_sha256": hashlib.sha256(member.linkname.encode()).hexdigest(),
                    }
                )
    return sorted(excluded, key=lambda row: row["path"])


def _extract_archive(
    archive: Path,
    destination: Path,
    prefix: str,
    excluded_unsafe_links: list[dict[str, str]] | None = None,
) -> Path:
    destination.mkdir(parents=True, exist_ok=False)
    excluded = excluded_unsafe_links
    if excluded is None:
        excluded = _excluded_unsafe_links(archive, prefix)
    excluded_paths = {row["path"] for row in excluded}

    def safe_member(member: tarfile.TarInfo, destination_path: str) -> tarfile.TarInfo | None:
        if member.name in excluded_paths:
            return None
        return tarfile.data_filter(member, destination_path)

    with tarfile.open(archive, "r:") as bundle:
        names = bundle.getnames()
        if not names or any(
            Path(name).is_absolute()
            or ".." in Path(name).parts
            or Path(name).parts[0] != prefix
            for name in names
        ):
            raise ArtifactContractError(f"source archive has an unsafe or wrong prefix: {archive}")
        bundle.extractall(destination, filter=safe_member)
    root = destination / prefix
    if not root.is_dir():
        raise ArtifactContractError(f"source archive did not create {prefix}/")
    if any(path.name == ".env" for path in root.rglob(".env")):
        raise ArtifactContractError(f"source archive contains forbidden .env bytes: {archive}")
    return root


def _declared_project_version(root: Path) -> str | None:
    pyproject = root / "pyproject.toml"
    if not pyproject.is_file():
        return None
    with pyproject.open("rb") as stream:
        payload = tomllib.load(stream)
    value = payload.get("project", {}).get("version")
    return str(value) if value is not None else None


def _wheel_metadata(path: Path) -> tuple[str, str]:
    try:
        with zipfile.ZipFile(path) as archive:
            metadata_names = [
                name for name in archive.namelist() if name.endswith(".dist-info/METADATA")
            ]
            if len(metadata_names) != 1:
                raise ArtifactContractError(
                    f"wheel has {len(metadata_names)} METADATA files: {path}"
                )
            lines = archive.read(metadata_names[0]).decode("utf-8").splitlines()
    except (OSError, UnicodeDecodeError, zipfile.BadZipFile) as error:
        raise ArtifactContractError(f"invalid wheel {path}: {error}") from error
    fields: dict[str, str] = {}
    for line in lines:
        if ": " in line:
            key, value = line.split(": ", 1)
            fields.setdefault(key, value)
    try:
        return fields["Name"], fields["Version"]
    except KeyError as error:
        raise ArtifactContractError(f"wheel metadata omits {error.args[0]}: {path}") from error


def _normalized_distribution(value: str) -> str:
    return re.sub(r"[-_.]+", "-", value).lower()


def _build_wheel_once(
    source: Path,
    destination: Path,
    *,
    source_date_epoch: str,
) -> Path:
    uv = shutil.which("uv")
    if uv is None:
        raise ArtifactContractError("uv executable is required for offline wheel builds")
    destination.mkdir(parents=True, exist_ok=False)
    environment = os.environ.copy()
    environment.update(
        {
            "PYTHONPATH": "",
            "SOURCE_DATE_EPOCH": source_date_epoch,
            "UV_OFFLINE": "1",
            "UV_NO_SYNC": "1",
        }
    )
    _run(
        uv,
        "build",
        "--wheel",
        "--offline",
        "--no-sources",
        "--out-dir",
        str(destination),
        str(source),
        env=environment,
    )
    wheels = sorted(destination.glob("*.whl"))
    if len(wheels) != 1:
        raise ArtifactContractError(
            f"wheel build produced {len(wheels)} wheels under {destination}"
        )
    return wheels[0]


def _deterministic_wheel(
    source: Path,
    output: Path,
    *,
    distribution: str,
    version: str,
    source_date_epoch: str,
) -> dict[str, str]:
    with tempfile.TemporaryDirectory(prefix="stop-parser-wheel-") as temporary:
        root = Path(temporary)
        first = _build_wheel_once(source, root / "first", source_date_epoch=source_date_epoch)
        second = _build_wheel_once(source, root / "second", source_date_epoch=source_date_epoch)
        first_hash = _sha256(first)
        second_hash = _sha256(second)
        if first.name != second.name or first_hash != second_hash:
            raise ArtifactContractError(
                "wheel build is not deterministic: "
                f"{first.name} {first_hash} != {second.name} {second_hash}"
            )
        actual_distribution, actual_version = _wheel_metadata(first)
        if _normalized_distribution(actual_distribution) != _normalized_distribution(distribution):
            raise ArtifactContractError(
                f"wheel distribution mismatch: expected {distribution}, found {actual_distribution}"
            )
        if actual_version != version:
            raise ArtifactContractError(
                f"wheel version mismatch: expected {version}, found {actual_version}"
            )
        destination = output / first.name
        shutil.copyfile(first, destination)
    return {
        "filename": destination.name,
        "sha256": _sha256(destination),
        "distribution": actual_distribution,
        "version": actual_version,
    }


def build_artifacts(
    *,
    identities: dict[str, str],
    sources: dict[str, dict[str, Any]],
    output: Path,
) -> dict[str, object]:
    """Create the deterministic private artifact set and return its closed manifest."""
    if set(identities) != set(REPOSITORY_NAMES):
        raise ArtifactContractError("artifact identities do not cover the five repositories")
    if output.exists() and any(output.iterdir()):
        raise ArtifactContractError(f"artifact output must be new and empty: {output}")
    output.mkdir(parents=True, exist_ok=True)
    archives = output / "sources"
    extracts = output / "extracted"
    history = output / "history"
    history_extracts = output / "history-extracted"
    wheels = output / "wheels"
    archives.mkdir()
    extracts.mkdir()
    history.mkdir()
    history_extracts.mkdir()
    wheels.mkdir()

    records: dict[str, dict[str, Any]] = {}
    for name in REPOSITORY_NAMES:
        commit = _full_sha(identities[name], label=name)
        row = sources[name]
        repository = Path(row["path"])
        require_clean_commit(repository, commit)
        prefix = _archive_prefix(name, row)
        archive_name = f"{name}-{commit}.tar"
        archive = archives / archive_name
        with tempfile.TemporaryDirectory(prefix=f"stop-parser-{name}-archive-") as temporary:
            repeated = Path(temporary) / archive_name
            _git_archive(repository, commit, prefix, archive)
            _git_archive(repository, commit, prefix, repeated)
            if archive.read_bytes() != repeated.read_bytes():
                raise ArtifactContractError(f"source archive is not deterministic for {name}")
        archive_hash = _sha256(archive)
        pinned_archive_hash = row.get("expected_archive_sha256")
        if pinned_archive_hash is not None and archive_hash != pinned_archive_hash:
            raise ArtifactContractError(
                f"source archive hash mismatch for {name}: "
                f"expected {pinned_archive_hash}, found {archive_hash}"
            )
        extracted_parent = extracts / name
        excluded_unsafe_links = _excluded_unsafe_links(archive, prefix)
        extracted = _extract_archive(
            archive,
            extracted_parent,
            prefix,
            excluded_unsafe_links,
        )
        declared = _declared_project_version(extracted)
        if declared is not None and declared != row["version"]:
            raise ArtifactContractError(
                f"declared version mismatch for {name}: expected {row['version']}, found {declared}"
            )
        timestamp = _run("git", "-C", str(repository), "show", "-s", "--format=%ct", commit)
        wheel_record: dict[str, str] | None = None
        distribution = row.get("wheel_distribution")
        if distribution:
            wheel_record = _deterministic_wheel(
                extracted,
                wheels,
                distribution=distribution,
                version=row["version"],
                source_date_epoch=timestamp,
            )
        history_record: dict[str, Any] | None = None
        if name == "codegen":
            history_commits = {"c_prod": commit, **row["history_commits"]}
            history_bundle = history / f"codegen-{commit}.bundle"
            history_record = _deterministic_history_bundle(
                repository, history_commits, history_bundle
            )
            history_root = _extract_history_bundle(
                history_bundle, history_extracts / "codegen", history_commits
            )
            history_record.update(
                {
                    "commit": commit,
                    "extracted_root": str(history_root.relative_to(output)),
                }
            )
        records[name] = {
            "repository_url": row["url"],
            "commit": commit,
            "version": row["version"],
            "archive": {
                "filename": f"sources/{archive.name}",
                "prefix": prefix,
                "sha256": archive_hash,
                "excluded_unsafe_links": excluded_unsafe_links,
            },
            "extracted_root": f"extracted/{name}/{prefix}",
            "wheel": wheel_record,
        }
        if history_record is not None:
            records[name]["history"] = history_record

    manifest: dict[str, object] = {
        "schema_version": SCHEMA_VERSION,
        "inputs": records,
        "artifact_source_inputs": "artifact-source-inputs.json",
    }
    (output / "artifact-build.json").write_text(_canonical_json(manifest))
    agentic = records["agentic"]
    codegen = records["codegen"]
    source_inputs = {
        "schema_version": ARTIFACT_SOURCE_INPUT_SCHEMA_VERSION,
        "agentic_source": {
            "root": agentic["extracted_root"],
            "commit": agentic["commit"],
            "archive": agentic["archive"]["filename"],
            "archive_sha256": agentic["archive"]["sha256"],
        },
        "codegen_source": {
            "root": codegen["extracted_root"],
            "commit": codegen["commit"],
            "archive": codegen["archive"]["filename"],
            "archive_sha256": codegen["archive"]["sha256"],
        },
        "codegen_history": {
            "root": codegen["history"]["extracted_root"],
            "commit": codegen["history"]["commit"],
            "bundle": codegen["history"]["filename"],
            "bundle_sha256": codegen["history"]["sha256"],
            "required_commits": codegen["history"]["required_commits"],
        },
    }
    (output / "artifact-source-inputs.json").write_text(_canonical_json(source_inputs))
    return manifest


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--c-prod", required=True)
    parser.add_argument("--agentic", required=True)
    parser.add_argument("--teax", required=True)
    parser.add_argument("--costingfe", required=True)
    parser.add_argument("--fusion", required=True)
    parser.add_argument("--output", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    source_manifest = os.environ.get("STOP_PARSER_SOURCE_MANIFEST")
    if not source_manifest:
        raise ArtifactContractError(
            "STOP_PARSER_SOURCE_MANIFEST must name the explicit five-repository source map"
        )
    sources = load_source_manifest(Path(source_manifest))
    build_artifacts(
        identities={
            "agentic": arguments.agentic,
            "codegen": arguments.c_prod,
            "teax": arguments.teax,
            "costingfe": arguments.costingfe,
            "fusion": arguments.fusion,
        },
        sources=sources,
        output=arguments.output,
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ArtifactContractError as error:
        print(f"ARTIFACT REFUSED: {error}", file=sys.stderr)
        raise SystemExit(2) from error
