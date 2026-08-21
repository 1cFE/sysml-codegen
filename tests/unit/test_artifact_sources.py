"""The retained verification tools consume only explicit immutable artifact roots."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import pytest

from verification import artifact_sources


def _git(repository: Path, *arguments: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repository), *arguments],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _artifact_inputs(tmp_path: Path) -> tuple[Path, Path, Path]:
    agentic = tmp_path / "extracted/agentic/agentic-mbse-0.1.3"
    for relative in (
        "src/agentic_mbse",
        "claude",
        ".claude",
        "docs",
        "project_templates",
    ):
        (agentic / relative).mkdir(parents=True)
    codegen = tmp_path / "extracted/codegen/sysml-codegen-0.1.1"
    codegen.mkdir(parents=True)

    history = tmp_path / "history-extracted/codegen"
    history.mkdir(parents=True)
    _git(history, "init", "--quiet")
    (history / "tracked.txt").write_text("history\n")
    _git(history, "add", "tracked.txt")
    _git(
        history,
        "-c",
        "user.name=Artifact Source Test",
        "-c",
        "user.email=artifact-source@example.invalid",
        "commit",
        "--quiet",
        "-m",
        "history",
    )
    commit = _git(history, "rev-parse", "HEAD")

    sources = tmp_path / "sources"
    sources.mkdir()
    agentic_archive = sources / "agentic.tar"
    codegen_archive = sources / "codegen.tar"
    agentic_archive.write_bytes(b"agentic-source-archive\n")
    codegen_archive.write_bytes(b"codegen-source-archive\n")
    bundle_dir = tmp_path / "history"
    bundle_dir.mkdir()
    bundle = bundle_dir / "codegen.bundle"
    _git(history, "bundle", "create", str(bundle), "HEAD")

    payload = {
        "schema_version": artifact_sources.SCHEMA_VERSION,
        "agentic_source": {
            "root": "extracted/agentic/agentic-mbse-0.1.3",
            "commit": "a" * 40,
            "archive": "sources/agentic.tar",
            "archive_sha256": hashlib.sha256(agentic_archive.read_bytes()).hexdigest(),
        },
        "codegen_source": {
            "root": "extracted/codegen/sysml-codegen-0.1.1",
            "commit": commit,
            "archive": "sources/codegen.tar",
            "archive_sha256": hashlib.sha256(codegen_archive.read_bytes()).hexdigest(),
        },
        "codegen_history": {
            "root": "history-extracted/codegen",
            "commit": commit,
            "bundle": "history/codegen.bundle",
            "bundle_sha256": hashlib.sha256(bundle.read_bytes()).hexdigest(),
            "required_commits": {"c_prod": commit},
        },
    }
    manifest = tmp_path / "artifact-source-inputs.json"
    manifest.write_text(json.dumps(payload, sort_keys=True) + "\n")
    return manifest, agentic, codegen


def test_missing_artifact_source_manifest_is_refused() -> None:
    with pytest.raises(
        artifact_sources.ArtifactSourceInputError,
        match=artifact_sources.ARTIFACT_SOURCE_INPUTS,
    ):
        artifact_sources.load_artifact_source_inputs({})


def test_wrong_hash_identified_artifact_root_is_refused(tmp_path: Path) -> None:
    manifest, _agentic, _codegen = _artifact_inputs(tmp_path)
    payload = json.loads(manifest.read_text())
    payload["agentic_source"]["archive_sha256"] = "0" * 64
    manifest.write_text(json.dumps(payload, sort_keys=True) + "\n")

    with pytest.raises(artifact_sources.ArtifactSourceInputError, match="hash mismatch"):
        artifact_sources.load_artifact_source_inputs(
            {artifact_sources.ARTIFACT_SOURCE_INPUTS: str(manifest)}
        )


def test_correct_roots_are_admitted_and_wrong_codegen_root_fails_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    manifest, agentic, codegen = _artifact_inputs(tmp_path)
    monkeypatch.setenv(artifact_sources.ARTIFACT_SOURCE_INPUTS, str(manifest))

    inputs = artifact_sources.load_artifact_source_inputs()

    assert inputs.manifest == manifest
    assert inputs.agentic_source == agentic
    assert artifact_sources.agentic_source_root(codegen) == agentic
    assert artifact_sources.codegen_history_root(codegen) == tmp_path / "history-extracted/codegen"
    with pytest.raises(
        artifact_sources.ArtifactSourceInputError, match="differs from"
    ):
        artifact_sources.require_codegen_source(tmp_path / "editable-codegen")
