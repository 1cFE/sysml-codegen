"""The production/evidence split is executable, not an honor-system convention.

These tests keep the Phase 6 verification entry points honest before final cross-repository
evidence exists.  They use temporary repositories and artifact records so the checks exercise
Git identity, wheel metadata, import roots, and skip accounting without reading a sibling checkout.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

from verification import audit_evidence, build_artifacts, run_independent_green

EVIDENCE_PATHS = (
    "verification/dependencies.json",
    "verification/wheelhouse-requirements.txt",
    "verification/execution-provenance.json",
    "verification/independent-green.json",
    "verification/reconciliation-ledger.md",
    "verification/evidence-lock.json",
)


def _git(repository: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repository), *arguments],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def _commit(repository: Path, message: str) -> str:
    _git(repository, "add", "--all")
    _git(
        repository,
        "-c",
        "user.name=Evidence Test",
        "-c",
        "user.email=evidence@example.invalid",
        "commit",
        "-m",
        message,
    )
    return _git(repository, "rev-parse", "HEAD")


@pytest.fixture
def production_repository(tmp_path: Path) -> tuple[Path, str]:
    repository = tmp_path / "codegen"
    repository.mkdir()
    _git(repository, "init", "--quiet")
    (repository / "pyproject.toml").write_text(
        '[project]\nname = "sysml-codegen"\nversion = "0.1.1"\n'
    )
    (repository / "src").mkdir()
    (repository / "src/sysml_codegen.py").write_text('__version__ = "0.1.1"\n')
    return repository, _commit(repository, "production")


def _write_evidence(repository: Path, *, self_reference: str | None = None) -> None:
    payloads = {
        EVIDENCE_PATHS[0]: '{"schema_version":"stop-parser-dependencies/v1"}\n',
        EVIDENCE_PATHS[1]: "example==1.0 --hash=sha256:" + "0" * 64 + "\n",
        EVIDENCE_PATHS[2]: '{"schema_version":"stop-parser-execution-provenance/v1"}\n',
        EVIDENCE_PATHS[3]: '{"schema_version":"stop-parser-independent-green/v1"}\n',
        EVIDENCE_PATHS[4]: "# Reconciliation ledger\n",
        EVIDENCE_PATHS[5]: '{"schema_version":"stop-parser-evidence-lock/v1"}\n',
    }
    if self_reference is not None:
        payloads[EVIDENCE_PATHS[4]] += self_reference + "\n"
    for relative, text in payloads.items():
        path = repository / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)


def _wheel(path: Path, *, version: str) -> str:
    dist_info = f"sysml_codegen-{version}.dist-info"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(
            f"{dist_info}/METADATA",
            f"Metadata-Version: 2.3\nName: sysml-codegen\nVersion: {version}\n",
        )
        archive.writestr(
            f"{dist_info}/WHEEL",
            "Wheel-Version: 1.0\nGenerator: evidence-test\nRoot-Is-Purelib: true\n"
            "Tag: py3-none-any\n",
        )
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_builder_refuses_dirty_source(production_repository: tuple[Path, str]) -> None:
    repository, commit = production_repository
    (repository / "dirty.txt").write_text("not committed\n")

    with pytest.raises(build_artifacts.ArtifactContractError, match="dirty source"):
        build_artifacts.require_clean_commit(repository, commit)


def test_builder_refuses_wrong_full_identity(production_repository: tuple[Path, str]) -> None:
    repository, _commit_sha = production_repository

    with pytest.raises(build_artifacts.ArtifactContractError, match="40 lowercase"):
        build_artifacts.require_clean_commit(repository, "abc123")


def test_evidence_boundary_accepts_exact_direct_child(
    production_repository: tuple[Path, str],
) -> None:
    repository, c_prod = production_repository
    _write_evidence(repository)
    c_evidence = _commit(repository, "evidence")

    result = audit_evidence.verify_commit_boundary(repository, c_prod, c_evidence)

    assert result == {
        "parent": c_prod,
        "changed_paths": sorted(EVIDENCE_PATHS),
    }


def test_evidence_boundary_refuses_wrong_parent(
    production_repository: tuple[Path, str],
) -> None:
    repository, c_prod = production_repository
    (repository / "intervening.txt").write_text("production drift\n")
    _commit(repository, "intervening")
    _write_evidence(repository)
    c_evidence = _commit(repository, "evidence")

    with pytest.raises(audit_evidence.EvidenceAuditError, match="parent"):
        audit_evidence.verify_commit_boundary(repository, c_prod, c_evidence)


def test_evidence_boundary_refuses_seventh_changed_path(
    production_repository: tuple[Path, str],
) -> None:
    repository, c_prod = production_repository
    _write_evidence(repository)
    (repository / "verification/extra.json").write_text("{}\n")
    c_evidence = _commit(repository, "evidence plus production drift")

    with pytest.raises(audit_evidence.EvidenceAuditError, match="changed-path"):
        audit_evidence.verify_commit_boundary(repository, c_prod, c_evidence)


def test_evidence_files_refuse_self_reference(
    production_repository: tuple[Path, str],
) -> None:
    repository, _c_prod = production_repository
    candidate = "f" * 40
    _write_evidence(repository, self_reference=candidate)

    with pytest.raises(audit_evidence.EvidenceAuditError, match="self-reference"):
        audit_evidence.verify_no_evidence_self_reference(repository, candidate)


@pytest.mark.parametrize(
    ("expected_version", "expected_hash", "message"),
    [
        ("0.1.1", "f" * 64, "hash"),
        ("0.1.1", None, "version"),
    ],
)
def test_wheel_identity_refuses_wrong_version_or_hash(
    tmp_path: Path,
    expected_version: str,
    expected_hash: str | None,
    message: str,
) -> None:
    actual_version = "0.1.2" if expected_hash is None else "0.1.1"
    wheel = tmp_path / f"sysml_codegen-{actual_version}-py3-none-any.whl"
    actual_hash = _wheel(wheel, version=actual_version)

    with pytest.raises(audit_evidence.EvidenceAuditError, match=message):
        audit_evidence.verify_wheel(
            wheel,
            distribution="sysml-codegen",
            version=expected_version,
            sha256=expected_hash or actual_hash,
        )


def test_run_record_refuses_sibling_import(tmp_path: Path) -> None:
    extracted = tmp_path / "extracted/codegen"
    sibling = tmp_path / "sibling/sysml_codegen/__init__.py"
    extracted.mkdir(parents=True)
    sibling.parent.mkdir(parents=True)
    sibling.write_text("")
    record = {
        "id": "codegen-default",
        "command": [sys.executable, "-m", "pytest", "tests"],
        "executed_command": [sys.executable, "-m", "pytest", "tests", "-ra"],
        "status": 0,
        "expected_status": 0,
        "counts": {
            "collected": 1,
            "selected": 1,
            "passed": 1,
            "failed": 0,
            "skipped": 0,
            "xfailed": 0,
            "deselected": 0,
        },
        "expected_counts": {
            "collected": 1,
            "selected": 1,
            "passed": 1,
            "failed": 0,
            "skipped": 0,
            "xfailed": 0,
            "deselected": 0,
        },
        "output_sha256": "0" * 64,
        "expected_output_sha256": None,
        "allowed_skips": [],
        "observed_skips": [],
        "unexpected_skips": [],
        "import_roots": [str(extracted)],
        "import_files": [str(sibling)],
    }

    with pytest.raises(run_independent_green.IndependentRunError, match="import root"):
        run_independent_green.validate_run_record(record)


def test_run_record_refuses_unexpected_skip(tmp_path: Path) -> None:
    extracted = tmp_path / "extracted/codegen"
    imported = extracted / "src/sysml_codegen/__init__.py"
    imported.parent.mkdir(parents=True)
    imported.write_text("")
    record = {
        "id": "codegen-default",
        "command": [sys.executable, "-m", "pytest", "tests"],
        "executed_command": [sys.executable, "-m", "pytest", "tests", "-ra"],
        "status": 0,
        "expected_status": 0,
        "counts": {
            "collected": 2,
            "selected": 2,
            "passed": 1,
            "failed": 0,
            "skipped": 1,
            "xfailed": 0,
            "deselected": 0,
        },
        "expected_counts": {
            "collected": 2,
            "selected": 2,
            "passed": 1,
            "failed": 0,
            "skipped": 1,
            "xfailed": 0,
            "deselected": 0,
        },
        "output_sha256": "0" * 64,
        "expected_output_sha256": None,
        "allowed_skips": [],
        "observed_skips": [{"node_id": "tests/test_x.py::test_x", "reason": "missing"}],
        "unexpected_skips": [{"node_id": "tests/test_x.py::test_x", "reason": "missing"}],
        "import_roots": [str(extracted)],
        "import_files": [str(imported)],
    }

    with pytest.raises(run_independent_green.IndependentRunError, match="unexpected skip"):
        run_independent_green.validate_run_record(record)


def test_run_record_accepts_closed_counts_and_imports(tmp_path: Path) -> None:
    extracted = tmp_path / "extracted/codegen"
    imported = extracted / "src/sysml_codegen/__init__.py"
    imported.parent.mkdir(parents=True)
    imported.write_text("")
    record = {
        "id": "codegen-default",
        "command": [sys.executable, "-m", "pytest", "tests"],
        "executed_command": [sys.executable, "-m", "pytest", "tests", "-ra"],
        "status": 0,
        "expected_status": 0,
        "counts": {
            "collected": 2,
            "selected": 2,
            "passed": 1,
            "failed": 0,
            "skipped": 1,
            "xfailed": 0,
            "deselected": 0,
        },
        "expected_counts": {
            "collected": 2,
            "selected": 2,
            "passed": 1,
            "failed": 0,
            "skipped": 1,
            "xfailed": 0,
            "deselected": 0,
        },
        "output_sha256": "0" * 64,
        "expected_output_sha256": None,
        "allowed_skips": [
            {"node_id": "tests/test_x.py::test_x", "reason": "declared dependency absent"}
        ],
        "observed_skips": [
            {"node_id": "tests/test_x.py::test_x", "reason": "declared dependency absent"}
        ],
        "unexpected_skips": [],
        "import_roots": [str(extracted)],
        "import_files": [str(imported)],
    }

    run_independent_green.validate_run_record(record)


def test_nonzero_baseline_requires_its_exact_output_hash(tmp_path: Path) -> None:
    root = tmp_path / "artifact"
    root.mkdir()
    zero_counts = {field: 0 for field in run_independent_green.COUNT_FIELDS}
    record = {
        "id": "baseline-delta",
        "command": ["mypy", "src"],
        "executed_command": ["mypy", "src"],
        "status": 1,
        "expected_status": 1,
        "counts": zero_counts,
        "expected_counts": zero_counts,
        "output_sha256": "0" * 64,
        "expected_output_sha256": "f" * 64,
        "allowed_skips": [],
        "observed_skips": [],
        "unexpected_skips": [],
        "import_roots": [str(root)],
        "import_files": [],
    }

    with pytest.raises(run_independent_green.IndependentRunError, match="baseline output"):
        run_independent_green.validate_run_record(record)


def test_lock_covers_five_siblings_and_two_production_files(tmp_path: Path) -> None:
    repository = tmp_path / "repository"
    staging = tmp_path / "staging"
    repository.mkdir()
    staging.mkdir()
    for relative in (
        "verification/probe-fixture-lock.json",
        "verification/expected-transitions.md",
    ):
        path = repository / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(relative + "\n")
    for name in (
        "dependencies.json",
        "wheelhouse-requirements.txt",
        "execution-provenance.json",
        "independent-green.json",
        "reconciliation-ledger.md",
    ):
        (staging / name).write_text(name + "\n")

    lock = run_independent_green.build_evidence_lock(repository, staging)

    assert set(lock["files"]) == {
        "verification/dependencies.json",
        "verification/wheelhouse-requirements.txt",
        "verification/execution-provenance.json",
        "verification/independent-green.json",
        "verification/reconciliation-ledger.md",
        "verification/probe-fixture-lock.json",
        "verification/expected-transitions.md",
    }
    assert "verification/evidence-lock.json" not in lock["files"]


def test_cli_contracts_keep_the_fixed_required_options() -> None:
    assert build_artifacts.build_parser().parse_args(
        [
            "--c-prod",
            "1" * 40,
            "--agentic",
            "2" * 40,
            "--teax",
            "3" * 40,
            "--costingfe",
            "4" * 40,
            "--fusion",
            "5" * 40,
            "--output",
            "/tmp/artifacts",
        ]
    ).c_prod == "1" * 40
    assert run_independent_green.build_parser().parse_args(
        ["--artifact-root", "/tmp/artifacts", "--evidence-output", "/tmp/evidence"]
    ).artifact_root == Path("/tmp/artifacts")
    assert audit_evidence.build_parser().parse_args(
        [
            "--repository",
            "/tmp/codegen",
            "--c-prod",
            "1" * 40,
            "--f-final",
            "2" * 40,
            "--c-evidence",
            "3" * 40,
            "--artifact-root",
            "/tmp/artifacts",
        ]
    ).c_evidence == "3" * 40


def test_source_manifest_is_closed_and_absolute(tmp_path: Path) -> None:
    manifest = tmp_path / "sources.json"
    rows = {
        name: {
            "path": str((tmp_path / name).resolve()),
            "url": f"https://example.invalid/{name}.git",
            "version": "0.1.0",
            "wheel_distribution": None,
        }
        for name in build_artifacts.REPOSITORY_NAMES
    }
    manifest.write_text(
        json.dumps({"schema_version": "stop-parser-source-roots/v1", "repositories": rows})
    )

    assert set(build_artifacts.load_source_manifest(manifest)) == set(
        build_artifacts.REPOSITORY_NAMES
    )

    rows["fusion"]["path"] = "../fusion-tea"
    manifest.write_text(
        json.dumps({"schema_version": "stop-parser-source-roots/v1", "repositories": rows})
    )
    with pytest.raises(build_artifacts.ArtifactContractError, match="absolute"):
        build_artifacts.load_source_manifest(manifest)


def test_builder_cli_creates_five_closed_source_artifacts(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    identities: dict[str, str] = {}
    rows: dict[str, dict[str, object]] = {}
    for name in build_artifacts.REPOSITORY_NAMES:
        repository = tmp_path / name
        repository.mkdir()
        _git(repository, "init", "--quiet")
        (repository / "pyproject.toml").write_text(
            f'[project]\nname = "{name}"\nversion = "0.1.0"\n'
        )
        (repository / "source.txt").write_text(f"{name}\n")
        if name == "agentic":
            (repository / "source-link.txt").symlink_to("source.txt")
            (repository / "workspace-only-link").symlink_to(
                "/private/workspace/agentic-only"
            )
        identities[name] = _commit(repository, f"freeze {name}")
        rows[name] = {
            "path": str(repository.resolve()),
            "url": f"https://example.invalid/{name}.git",
            "version": "0.1.0",
            "wheel_distribution": None,
        }
    source_manifest = tmp_path / "source-manifest.json"
    source_manifest.write_text(
        json.dumps(
            {
                "schema_version": build_artifacts.SOURCE_SCHEMA_VERSION,
                "repositories": rows,
            }
        )
    )
    output = tmp_path / "artifacts"
    monkeypatch.setenv("STOP_PARSER_SOURCE_MANIFEST", str(source_manifest))

    assert (
        build_artifacts.main(
            [
                "--c-prod",
                identities["codegen"],
                "--agentic",
                identities["agentic"],
                "--teax",
                identities["teax"],
                "--costingfe",
                identities["costingfe"],
                "--fusion",
                identities["fusion"],
                "--output",
                str(output),
            ]
        )
        == 0
    )
    manifest = json.loads((output / "artifact-build.json").read_text())
    assert {
        name: row["commit"] for name, row in manifest["inputs"].items()
    } == identities
    assert len(list((output / "sources").glob("*.tar"))) == 5
    assert manifest["inputs"]["agentic"]["archive"]["excluded_unsafe_links"] == [
        {
            "kind": "symlink",
            "path": "agentic-0.1.0/workspace-only-link",
            "target": "/private/workspace/agentic-only",
        }
    ]
    assert not (
        output / "extracted/agentic/agentic-0.1.0/workspace-only-link"
    ).is_symlink()
    extracted_internal_link = (
        output / "extracted/agentic/agentic-0.1.0/source-link.txt"
    )
    assert extracted_internal_link.is_symlink()
    assert extracted_internal_link.read_text() == "agentic\n"


def test_independent_green_cli_stages_exact_six_files(tmp_path: Path) -> None:
    artifact_root = tmp_path / "artifacts"
    codegen_root = artifact_root / "codegen-source"
    verification = codegen_root / "verification"
    verification.mkdir(parents=True)
    (verification / "probe-fixture-lock.json").write_text("{}\n")
    (verification / "expected-transitions.md").write_text("# transitions\n")
    (codegen_root / "test_green.py").write_text("def test_green():\n    assert True\n")
    (artifact_root / "requirements.txt").write_text(
        "example==1.0 --hash=sha256:" + "0" * 64 + "\n"
    )
    (artifact_root / "ledger.md").write_text("# staged reconciliation\n")
    inputs = {
        name: {"commit": str(index) * 40}
        for index, name in enumerate(build_artifacts.REPOSITORY_NAMES, start=1)
    }
    (artifact_root / "artifact-build.json").write_text(
        json.dumps(
            {
                "schema_version": build_artifacts.SCHEMA_VERSION,
                "inputs": inputs,
            }
        )
    )
    (artifact_root / "run-contract.json").write_text(
        json.dumps(
            {
                "schema_version": run_independent_green.CONTRACT_SCHEMA_VERSION,
                "runs": [
                    {
                        "id": "green",
                        "command": [sys.executable, "-m", "pytest", "test_green.py"],
                        "cwd": "codegen-source",
                        "environment": {},
                        "expected_status": 0,
                        "expected_counts": {
                            "collected": 1,
                            "selected": 1,
                            "passed": 1,
                            "failed": 0,
                            "skipped": 0,
                            "xfailed": 0,
                            "deselected": 0,
                        },
                        "allowed_skips": [],
                        "import_roots": [str(codegen_root.resolve())],
                        "import_files": [],
                    }
                ],
                "python": {"version": sys.version.split()[0]},
                "syside": {"version": "test"},
                "wheelhouse": {"status": "fixture"},
                "wheelhouse_requirements": "requirements.txt",
                "execution_provenance": {"installed_artifacts": {}},
                "reconciliation_ledger": "ledger.md",
                "codegen_source_root": "codegen-source",
            }
        )
    )
    evidence = tmp_path / "evidence"

    assert (
        run_independent_green.main(
            ["--artifact-root", str(artifact_root), "--evidence-output", str(evidence)]
        )
        == 0
    )
    assert {path.name for path in evidence.iterdir()} == {
        *run_independent_green.EVIDENCE_SIBLINGS,
        "evidence-lock.json",
    }
    report = json.loads((evidence / "independent-green.json").read_text())
    assert report["runs"][0]["command"] == [
        sys.executable,
        "-m",
        "pytest",
        "test_green.py",
    ]
    assert "-ra" in report["runs"][0]["executed_command"]
    assert any(
        item.startswith("--junitxml=") for item in report["runs"][0]["executed_command"]
    )
    assert report["runs"][0]["counts"] == {
        "collected": 1,
        "selected": 1,
        "passed": 1,
        "failed": 0,
        "skipped": 0,
        "xfailed": 0,
        "deselected": 0,
    }
