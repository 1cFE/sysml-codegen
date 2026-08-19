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

from verification import artifact_sources, audit_evidence, build_artifacts, run_independent_green

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


def test_wheelhouse_uses_own_metadata_when_wheel_vendors_a_distribution(
    tmp_path: Path,
) -> None:
    wheel = tmp_path / "example-1.0.0-py3-none-any.whl"
    with zipfile.ZipFile(wheel, "w") as archive:
        archive.writestr(
            "example-1.0.0.dist-info/METADATA",
            "Metadata-Version: 2.3\nName: example\nVersion: 1.0.0\n",
        )
        archive.writestr(
            "example/_vendor/vendored-2.0.0.dist-info/METADATA",
            "Metadata-Version: 2.3\nName: vendored\nVersion: 2.0.0\n",
        )

    assert run_independent_green._wheel_identity(wheel) == ("example", "1.0.0")


def test_teax_runtime_wheel_comes_from_its_frozen_lock(tmp_path: Path) -> None:
    teax = tmp_path / "teax"
    teax.mkdir()
    digest = "a" * 64
    url = (
        "https://files.example.invalid/pyarrow-22.0.0-"
        "cp312-cp312-manylinux_2_28_x86_64.whl"
    )
    (teax / "uv.lock").write_text(
        'version = 1\n[[package]]\nname = "pyarrow"\nversion = "22.0.0"\n'
        f'wheels = [{{ url = "{url}", hash = "sha256:{digest}" }}]\n'
    )

    assert run_independent_green._teax_pyarrow_requirement(teax) == (
        f"pyarrow @ {url}#sha256={digest}"
    )


def test_teax_runtime_wheel_refuses_an_unhashed_candidate(tmp_path: Path) -> None:
    teax = tmp_path / "teax"
    teax.mkdir()
    (teax / "uv.lock").write_text(
        'version = 1\n[[package]]\nname = "pyarrow"\nversion = "22.0.0"\n'
        'wheels = [{ url = "https://example.invalid/pyarrow-22.0.0-'
        'cp312-cp312-manylinux_2_28_x86_64.whl", hash = "sha256:wrong" }]\n'
    )

    with pytest.raises(run_independent_green.IndependentRunError, match="0 CPython"):
        run_independent_green._teax_pyarrow_requirement(teax)


def test_deterministic_wheel_creates_its_missing_output_directory(tmp_path: Path) -> None:
    source = tmp_path / "source"
    package = source / "src/audit_wheel_probe"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text('__version__ = "1.0.0"\n')
    (source / "pyproject.toml").write_text(
        "[build-system]\n"
        'requires = ["hatchling"]\n'
        'build-backend = "hatchling.build"\n'
        "\n"
        "[project]\n"
        'name = "audit-wheel-probe"\n'
        'version = "1.0.0"\n'
        "\n"
        "[tool.hatch.build.targets.wheel]\n"
        'packages = ["src/audit_wheel_probe"]\n'
    )
    output = tmp_path / "wheels"

    result = build_artifacts._deterministic_wheel(
        source,
        output,
        distribution="audit-wheel-probe",
        version="1.0.0",
        source_date_epoch="1700000000",
    )

    wheel = output / result["filename"]
    assert output.is_dir()
    assert wheel.is_file()
    audit_evidence.verify_wheel(
        wheel,
        distribution="audit-wheel-probe",
        version="1.0.0",
        sha256=result["sha256"],
    )


def test_run_record_refuses_sibling_import(tmp_path: Path) -> None:
    extracted = tmp_path / "extracted/codegen"
    sibling = tmp_path / "sibling/sysml_codegen/__init__.py"
    extracted.mkdir(parents=True)
    sibling.parent.mkdir(parents=True)
    sibling.write_text("")
    record = {
        "id": "fixture-run",
        "command": [sys.executable, "-m", "pytest", "tests"],
        "executed_command": [sys.executable, "-m", "pytest", "tests", "-ra"],
        "status": 0,
        "expected_status": 0,
        "counts": {
            "collected": 1,
            "selected": 1,
            "passed": 1,
            "failed": 0,
            "errors": 0,
            "skipped": 0,
            "xfailed": 0,
            "deselected": 0,
        },
        "expected_counts": {
            "collected": 1,
            "selected": 1,
            "passed": 1,
            "failed": 0,
            "errors": 0,
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
            "errors": 0,
            "skipped": 1,
            "xfailed": 0,
            "deselected": 0,
        },
        "expected_counts": {
            "collected": 2,
            "selected": 2,
            "passed": 1,
            "failed": 0,
            "errors": 0,
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
        "id": "fixture-run",
        "command": [sys.executable, "-m", "pytest", "tests"],
        "executed_command": [sys.executable, "-m", "pytest", "tests", "-ra"],
        "status": 0,
        "expected_status": 0,
        "counts": {
            "collected": 2,
            "selected": 2,
            "passed": 1,
            "failed": 0,
            "errors": 0,
            "skipped": 1,
            "xfailed": 0,
            "deselected": 0,
        },
        "expected_counts": {
            "collected": 2,
            "selected": 2,
            "passed": 1,
            "failed": 0,
            "errors": 0,
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


def test_required_run_refuses_relaxed_skip_policy(tmp_path: Path) -> None:
    root = tmp_path / "artifact"
    root.mkdir()
    counts = {
        "collected": 1,
        "selected": 1,
        "passed": 1,
        "failed": 0,
        "errors": 0,
        "skipped": 0,
        "xfailed": 0,
        "deselected": 0,
    }
    record = {
        "id": "agentic-focused",
        "command": [sys.executable, "-m", "pytest", "tests"],
        "executed_command": [sys.executable, "-m", "pytest", "tests", "-ra"],
        "status": 0,
        "expected_status": 0,
        "counts": counts,
        "expected_counts": counts,
        "output_sha256": "0" * 64,
        "expected_output_sha256": None,
        "skip_policies": [],
        "allowed_skips": [],
        "observed_skips": [],
        "unexpected_skips": [],
        "import_roots": [str(root)],
        "import_files": [],
    }

    with pytest.raises(run_independent_green.IndependentRunError, match="committed contract"):
        run_independent_green.validate_run_record(record)


def test_run_one_puts_its_isolated_python_on_subprocess_path(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    reports = tmp_path / "reports"
    reports.mkdir()
    monkeypatch.setenv("PATH", "")
    counts = {field: 0 for field in run_independent_green.COUNT_FIELDS}
    record = run_independent_green._run_one(
        {
            "id": "subprocess-python",
            "command": [
                sys.executable,
                "-c",
                "import subprocess; subprocess.run(['python', '-V'], check=True)",
            ],
            "cwd": ".",
            "python": sys.executable,
            "environment": {},
            "expected_status": 0,
            "expected_counts": counts,
            "expected_output_sha256": None,
            "skip_policies": [],
            "import_roots": [str(tmp_path)],
            "import_files": [],
        },
        artifact_root=tmp_path,
        report_root=reports,
    )

    assert record["status"] == 0


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


def test_a_retained_run_output_mutation_is_rejected(tmp_path: Path) -> None:
    stdout = tmp_path / "run-reports/example.stdout"
    stderr = tmp_path / "run-reports/example.stderr"
    probe = tmp_path / "run-reports/example.imports.json"
    stdout.parent.mkdir()
    stdout.write_text("green\n")
    stderr.write_text("")
    probe.write_text("[]\n")
    record = {
        "id": "example",
        "output_sha256": hashlib.sha256(b"green\n\n").hexdigest(),
        "stdout": {
            "path": str(stdout.relative_to(tmp_path)),
            "sha256": hashlib.sha256(stdout.read_bytes()).hexdigest(),
        },
        "stderr": {
            "path": str(stderr.relative_to(tmp_path)),
            "sha256": hashlib.sha256(stderr.read_bytes()).hexdigest(),
        },
        "import_probe": {
            "path": str(probe.relative_to(tmp_path)),
            "sha256": hashlib.sha256(probe.read_bytes()).hexdigest(),
        },
    }

    audit_evidence.verify_retained_run_artifacts(tmp_path, record)
    stdout.write_text("mutated\n")
    with pytest.raises(audit_evidence.EvidenceAuditError, match="stdout hash mismatch"):
        audit_evidence.verify_retained_run_artifacts(tmp_path, record)


def test_run_record_counts_pytest_errors_separately_from_failures(tmp_path: Path) -> None:
    root = tmp_path / "artifact"
    root.mkdir()
    counts = {
        "collected": 1,
        "selected": 1,
        "passed": 0,
        "failed": 0,
        "errors": 1,
        "skipped": 0,
        "xfailed": 0,
        "deselected": 0,
    }
    record = {
        "id": "collection-error",
        "command": [sys.executable, "-m", "pytest", "tests"],
        "executed_command": [sys.executable, "-m", "pytest", "tests", "-ra"],
        "status": 1,
        "expected_status": 1,
        "counts": counts,
        "expected_counts": counts,
        "output_sha256": "0" * 64,
        "expected_output_sha256": "0" * 64,
        "allowed_skips": [],
        "observed_skips": [],
        "unexpected_skips": [],
        "import_roots": [str(root)],
        "import_files": [],
    }

    run_independent_green.validate_run_record(record)
    record["counts"] = counts | {"errors": 0, "failed": 1}
    with pytest.raises(run_independent_green.IndependentRunError, match="measured counts"):
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
    rows["codegen"]["history_commits"] = {
        name: "f" * 40 for name in build_artifacts.CODEGEN_HISTORY_INPUT_NAMES
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
            for relative in (
                "src/agentic_mbse",
                "claude",
                ".claude",
                "docs",
                "project_templates",
            ):
                directory = repository / relative
                directory.mkdir(parents=True)
                (directory / "artifact-contract.txt").write_text(relative + "\n")
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
    rows["codegen"]["history_commits"] = {
        name: identities["codegen"]
        for name in build_artifacts.CODEGEN_HISTORY_INPUT_NAMES
    }
    raw_teax = tmp_path / "raw-teax.tar"
    build_artifacts._git_archive(
        Path(rows["teax"]["path"]), identities["teax"], "", raw_teax
    )
    rows["teax"]["expected_archive_sha256"] = hashlib.sha256(
        raw_teax.read_bytes()
    ).hexdigest()
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
    assert manifest["inputs"]["teax"]["archive"][
        "unprefixed_git_archive_sha256"
    ] == rows["teax"]["expected_archive_sha256"]
    assert manifest["inputs"]["teax"]["archive"]["sha256"] != rows["teax"][
        "expected_archive_sha256"
    ]
    history = manifest["inputs"]["codegen"]["history"]
    assert history["commit"] == identities["codegen"]
    assert history["required_commits"] == {
        "c_prod": identities["codegen"],
        **rows["codegen"]["history_commits"],
    }
    assert hashlib.sha256((output / history["filename"]).read_bytes()).hexdigest() == history[
        "sha256"
    ]
    source_inputs = artifact_sources.load_artifact_source_inputs(
        {
            artifact_sources.ARTIFACT_SOURCE_INPUTS: str(
                output / "artifact-source-inputs.json"
            )
        }
    )
    assert source_inputs.codegen_commit == identities["codegen"]
    assert source_inputs.agentic_commit == identities["agentic"]
    assert source_inputs.codegen_history == output / "history-extracted/codegen"
    assert manifest["inputs"]["agentic"]["archive"]["excluded_unsafe_links"] == [
        {
            "kind": "symlink",
            "path": "agentic-0.1.0/workspace-only-link",
            "target_kind": "absolute",
            "target_sha256": hashlib.sha256(
                b"/private/workspace/agentic-only"
            ).hexdigest(),
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


def test_independent_green_refuses_external_run_staging(tmp_path: Path) -> None:
    artifact_root = tmp_path / "artifacts"
    artifact_root.mkdir()
    (artifact_root / "run-contract.json").write_text(
        json.dumps({"runs": [{"status": 0, "output_sha256": "0" * 64}]})
    )
    evidence = tmp_path / "evidence"

    with pytest.raises(run_independent_green.IndependentRunError, match="external run staging"):
        run_independent_green.run_battery(artifact_root, evidence)


def test_committed_runner_stages_exactly_six_evidence_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    artifact_root = tmp_path / "artifacts"
    artifact_root.mkdir()
    inputs: dict[str, dict[str, object]] = {}
    for index, name in enumerate(build_artifacts.REPOSITORY_NAMES, start=1):
        root = artifact_root / f"extracted/{name}/tree"
        root.mkdir(parents=True)
        inputs[name] = {
            "commit": str(index) * 40,
            "extracted_root": str(root.relative_to(artifact_root)),
            "archive": {"sha256": str(index) * 64},
            "wheel": {"sha256": str(index) * 64},
        }
    codegen = artifact_root / str(inputs["codegen"]["extracted_root"])
    verification = codegen / "verification"
    verification.mkdir()
    (verification / "probe-fixture-lock.json").write_text("{}\n")
    (verification / "expected-transitions.md").write_text("# transitions\n")
    (verification / "run_independent_green.py").write_text("# committed runner\n")
    (artifact_root / "artifact-build.json").write_text(
        json.dumps(
            {
                "schema_version": build_artifacts.SCHEMA_VERSION,
                "inputs": inputs,
            }
        )
    )
    evidence = tmp_path / "evidence"
    wheelhouse = artifact_root / "fixture-wheelhouse"
    wheelhouse.mkdir()

    def prepare(_root: Path, output: Path, _inputs):
        (output / "wheelhouse-requirements.txt").write_text(
            "example==1.0 --hash=sha256:" + "0" * 64 + "\n"
        )
        return {
            "python": Path(sys.executable),
            "versions": {"python": "3.12", "syside": "0.8.4"},
            "wheelhouse": wheelhouse,
            "wheelhouse_inventory": {"example.whl": "0" * 64},
            "freeze": ["example==1.0"],
        }

    monkeypatch.setattr(run_independent_green, "_prepare_environment", prepare)
    monkeypatch.setattr(
        run_independent_green,
        "_execution_provenance",
        lambda *_args: {"schema_version": "stop-parser-execution-provenance/v1"},
    )
    monkeypatch.setattr(
        run_independent_green,
        "_committed_runs",
        lambda *_args: [{"id": "green"}],
    )
    counts = {
        "collected": 1,
        "selected": 1,
        "passed": 1,
        "failed": 0,
        "errors": 0,
        "skipped": 0,
        "xfailed": 0,
        "deselected": 0,
    }
    monkeypatch.setattr(
        run_independent_green,
        "_run_one",
        lambda *_args, **_kwargs: {
            "id": "green",
            "command": [sys.executable, "-m", "pytest", "test_green.py"],
            "executed_command": [
                sys.executable,
                "-m",
                "pytest",
                "test_green.py",
                "-ra",
            ],
            "status": 0,
            "expected_status": 0,
            "counts": counts,
            "expected_counts": counts,
            "output_sha256": "0" * 64,
            "expected_output_sha256": None,
            "skip_policies": [],
            "allowed_skips": [],
            "observed_skips": [],
            "unexpected_skips": [],
            "import_roots": [str(codegen)],
            "import_files": [],
        },
    )

    run_independent_green.run_battery(artifact_root, evidence)

    assert {path.name for path in evidence.iterdir()} == {
        *run_independent_green.EVIDENCE_SIBLINGS,
        "evidence-lock.json",
    }


def test_committed_runner_inventory_covers_every_required_lane() -> None:
    assert set(run_independent_green.REQUIRED_RUN_IDS) == {
        "agentic-focused",
        "agentic-fast",
        "agentic-strict",
        "agentic-mypy-baseline",
        "agentic-ruff-baseline",
        "costingfe-pytest",
        "costingfe-ruff",
        "teax-pytest",
        "codegen-strict",
        "codegen-mypy-baseline",
        "codegen-default",
        "codegen-live-snapshot",
        "codegen-generated-package",
        "codegen-execution",
        "fusion-lock-check",
        "fusion-pytest",
        "fusion-models-primary",
        "fusion-models-exploration",
        "fusion-generated-execution",
        "fusion-ruff",
        "fusion-mypy",
    }
