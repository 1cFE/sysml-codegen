"""The execution lane accepts only roots named by the artifact provenance file."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from tests.execution.environment_pins import (
    CODEGEN_EXECUTION_PROVENANCE,
    ExecutionProvenanceError,
    environment_pin_problems,
    load_execution_provenance,
)


def _package(root: Path, name: str) -> Path:
    package = root / name
    package.mkdir(parents=True)
    init = package / "__init__.py"
    init.write_text("")
    return init


def _manifest(tmp_path: Path) -> tuple[Path, dict[str, str]]:
    codegen = tmp_path / "extracted/codegen/src"
    agentic = tmp_path / "installed/site-packages"
    teax = tmp_path / "extracted/teax"
    simkit = teax / "packages/teax-simkit"
    resolved = {
        "python": str(tmp_path / "venv/bin/python"),
        "sysml_codegen": str(_package(codegen, "sysml_codegen")),
        "agentic_mbse": str(_package(agentic, "agentic_mbse")),
        "simkit": str(_package(simkit, "simkit")),
    }
    artifacts = {
        "codegen": tmp_path / "artifacts/codegen.tar",
        "agentic": tmp_path / "artifacts/agentic.whl",
        "teax": tmp_path / "artifacts/teax.tar",
    }
    for name, path in artifacts.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(name.encode())
    digests = {
        name: hashlib.sha256(path.read_bytes()).hexdigest()
        for name, path in artifacts.items()
    }
    manifest = tmp_path / "execution-provenance.json"
    manifest.write_text(
        json.dumps(
            {
                "schema_version": "stop-parser-execution-provenance/v1",
                "artifact_root": str((tmp_path / "artifacts").resolve()),
                "python": {
                    "executable": resolved["python"],
                    "version": "3.12.3",
                },
                "roots": {
                    "codegen_source": {
                        "path": str(codegen),
                        "commit": "a" * 40,
                        "artifact_path": str(artifacts["codegen"]),
                        "archive_sha256": digests["codegen"],
                    },
                    "agentic_install": {
                        "path": str(agentic),
                        "commit": "b" * 40,
                        "artifact_path": str(artifacts["agentic"]),
                        "wheel_sha256": digests["agentic"],
                    },
                    "teax_source": {
                        "path": str(teax),
                        "commit": "c" * 40,
                        "artifact_path": str(artifacts["teax"]),
                        "archive_sha256": digests["teax"],
                    },
                    "teax_simkit": {
                        "path": str(simkit),
                        "commit": "c" * 40,
                        "artifact_path": str(artifacts["teax"]),
                        "archive_sha256": digests["teax"],
                    },
                },
            },
            sort_keys=True,
        )
        + "\n"
    )
    return manifest, resolved


def test_the_recorded_artifact_roots_pass(tmp_path: Path) -> None:
    manifest, resolved = _manifest(tmp_path)
    provenance = load_execution_provenance(
        {CODEGEN_EXECUTION_PROVENANCE: str(manifest)}
    )

    assert environment_pin_problems(resolved, provenance) == []
    assert provenance.manifest_path == manifest.resolve()
    assert len(provenance.manifest_sha256) == 64


def test_manifest_is_required(tmp_path: Path) -> None:
    with pytest.raises(ExecutionProvenanceError, match=CODEGEN_EXECUTION_PROVENANCE):
        load_execution_provenance({})


def test_wrong_schema_is_refused(tmp_path: Path) -> None:
    manifest, _resolved = _manifest(tmp_path)
    payload = json.loads(manifest.read_text())
    payload["schema_version"] = "wrong"
    manifest.write_text(json.dumps(payload))

    with pytest.raises(ExecutionProvenanceError, match="schema"):
        load_execution_provenance({CODEGEN_EXECUTION_PROVENANCE: str(manifest)})


@pytest.mark.parametrize(
    ("name", "wrong"),
    [
        ("python", "/other/bin/python"),
        ("simkit", "/other/simkit/__init__.py"),
        ("sysml_codegen", "/other/sysml_codegen/__init__.py"),
        ("agentic_mbse", "/other/agentic_mbse/__init__.py"),
    ],
)
def test_every_wrong_resolution_is_rejected(
    tmp_path: Path, name: str, wrong: str
) -> None:
    manifest, resolved = _manifest(tmp_path)
    provenance = load_execution_provenance(
        {CODEGEN_EXECUTION_PROVENANCE: str(manifest)}
    )

    problems = environment_pin_problems(resolved | {name: wrong}, provenance)

    assert len(problems) == 1
    assert name in problems[0]


def test_old_checkout_relative_shape_is_rejected(tmp_path: Path) -> None:
    manifest, resolved = _manifest(tmp_path)
    provenance = load_execution_provenance(
        {CODEGEN_EXECUTION_PROVENANCE: str(manifest)}
    )
    old_sibling = tmp_path / "agentic-mbse/src/agentic_mbse/__init__.py"
    old_sibling.parent.mkdir(parents=True)
    old_sibling.write_text("")

    problems = environment_pin_problems(
        resolved | {"agentic_mbse": str(old_sibling)}, provenance
    )

    assert len(problems) == 1
    assert "agentic_mbse" in problems[0]


def test_manifest_rejects_non_hash_artifact_identity(tmp_path: Path) -> None:
    manifest, _resolved = _manifest(tmp_path)
    payload = json.loads(manifest.read_text())
    payload["roots"]["codegen_source"]["archive_sha256"] = "short"
    manifest.write_text(json.dumps(payload))

    with pytest.raises(ExecutionProvenanceError, match="archive_sha256"):
        load_execution_provenance({CODEGEN_EXECUTION_PROVENANCE: str(manifest)})


def test_manifest_rejects_a_well_formed_but_wrong_artifact_hash(tmp_path: Path) -> None:
    manifest, _resolved = _manifest(tmp_path)
    payload = json.loads(manifest.read_text())
    payload["roots"]["agentic_install"]["wheel_sha256"] = "f" * 64
    manifest.write_text(json.dumps(payload))

    with pytest.raises(ExecutionProvenanceError, match="artifact hash mismatch"):
        load_execution_provenance({CODEGEN_EXECUTION_PROVENANCE: str(manifest)})


def test_manifest_rejects_an_artifact_outside_the_manifest_directory(tmp_path: Path) -> None:
    manifest, _resolved = _manifest(tmp_path)
    payload = json.loads(manifest.read_text())
    outside = tmp_path.parent / "unowned-codegen.tar"
    outside.write_bytes(b"codegen")
    payload["roots"]["codegen_source"]["artifact_path"] = str(outside)
    manifest.write_text(json.dumps(payload))

    with pytest.raises(ExecutionProvenanceError, match="artifact root"):
        load_execution_provenance({CODEGEN_EXECUTION_PROVENANCE: str(manifest)})
