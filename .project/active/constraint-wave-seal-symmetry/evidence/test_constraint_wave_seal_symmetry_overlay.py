"""Frozen Item 6 RED/GREEN overlay for seal/verify symlink symmetry.

This file is intentionally self-contained. Historical runs put an archived source tree
first on PYTHONPATH; candidate runs use the same bytes and select only one node per
fresh pytest process.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import runpy
from pathlib import Path

import pytest

from sysml_codegen.cli import GenerationConfig, cmd_seal, run_codegen
from sysml_codegen.contracts import seal as seal_module
from sysml_codegen.contracts.serialize import write_contract_json
from sysml_codegen.contracts.verify import ARTIFACT_UNREADABLE, INVALID_PATH, verify_package
from sysml_codegen.resolution.models import ComputationGraph


FORBIDDEN_MESSAGE = "symlinks are forbidden beneath the package root"
REPO_ROOT = Path(__file__).resolve().parents[4]
CHAIN_SNAPSHOT = REPO_ROOT / "tests/fixtures/chain_spike_model/extraction_snapshot.json"


def _regular_package(root: Path) -> Path:
    (root / "modules").mkdir(parents=True)
    (root / "modules" / "calc.py").write_text("def run():\n    return 1\n")
    (root / "contracts").mkdir()
    return root


def _sealed(root: Path) -> Path:
    package = _regular_package(root)
    contract = seal_module.seal_package(package, "pkg")
    write_contract_json(package / "contracts/package_contract.json", contract)
    return package


def _assert_seal_invalid(package: Path, expected_path: str) -> None:
    error_type = getattr(seal_module, "PackageSealError", ValueError)
    with pytest.raises(error_type) as caught:
        seal_module.seal_package(package, "pkg")
    error = caught.value
    assert getattr(error, "kind", None) == INVALID_PATH
    assert getattr(error, "path", None) == expected_path
    assert getattr(error, "message", None) == FORBIDDEN_MESSAGE
    assert str(error) == f"INVALID_PATH({expected_path}): {FORBIDDEN_MESSAGE}"


def _assert_verify_invalid(package: Path, expected_path: str) -> None:
    result = verify_package(package, "pkg")
    assert result.ok is False
    assert [(item.kind, item.path, item.message) for item in result.diagnostics] == [
        (INVALID_PATH, expected_path, FORBIDDEN_MESSAGE)
    ]


def _link_target(tmp_path: Path, package: Path, target_kind: str, entry_kind: str) -> Path:
    if target_kind == "internal":
        if entry_kind == "file":
            target = package / "modules/calc.py"
        else:
            target = package / "modules"
    elif target_kind == "escaping":
        target = tmp_path / f"outside-{entry_kind}"
        if entry_kind == "file":
            target.write_text("outside\n")
        else:
            target.mkdir()
            (target / "payload.py").write_text("outside = True\n")
    else:
        target = tmp_path / f"missing-{entry_kind}"
    return target


def _add_link(
    tmp_path: Path,
    package: Path,
    target_kind: str,
    entry_kind: str,
    rel_path: str = "alias",
) -> Path:
    link = package / rel_path
    link.parent.mkdir(parents=True, exist_ok=True)
    link.symlink_to(
        _link_target(tmp_path, package, target_kind, entry_kind),
        target_is_directory=entry_kind == "directory",
    )
    return link


def _snapshot_config(output: Path) -> GenerationConfig:
    return GenerationConfig(
        output_path=output,
        from_snapshot=CHAIN_SNAPSHOT,
        package_name="chain_spike",
        overwrite=True,
    )


def test_regular_file_and_directory_controls(tmp_path):
    package = _regular_package(tmp_path / "pkg")
    first = seal_module.seal_package(package, "pkg")
    second = seal_module.seal_package(package, "pkg")
    assert first.artifact_hashes == second.artifact_hashes
    assert first.executable_fingerprint == second.executable_fingerprint


def test_r10_seal_hashes_escaping_file_link_reviewed(tmp_path):
    package = _regular_package(tmp_path / "pkg")
    link = _add_link(tmp_path, package, "escaping", "file", "escape.py")
    if hasattr(seal_module, "PackageSealError"):
        _assert_seal_invalid(package, "escape.py")
    else:
        contract = seal_module.seal_package(package, "pkg")
        assert contract.artifact_hashes["escape.py"] == hashlib.sha256(link.read_bytes()).hexdigest()


def test_r10_seal_skips_directory_link_reviewed(tmp_path):
    package = _regular_package(tmp_path / "pkg")
    _add_link(tmp_path, package, "escaping", "directory", "escape_dir")
    if hasattr(seal_module, "PackageSealError"):
        _assert_seal_invalid(package, "escape_dir")
    else:
        assert "escape_dir" not in seal_module.seal_package(package, "pkg").artifact_hashes


def test_r10_verify_accepts_dangling_link_reviewed(tmp_path):
    package = _sealed(tmp_path / "pkg")
    _add_link(tmp_path, package, "dangling", "file", "dangling.py")
    result = verify_package(package, "pkg")
    if hasattr(seal_module, "PackageSealError"):
        _assert_verify_invalid(package, "dangling.py")
    else:
        assert result.ok is True and result.diagnostics == []


@pytest.mark.parametrize("target_kind", ["internal", "escaping"])
def _f9_control(tmp_path: Path, target_kind: str) -> None:
    package = _sealed(tmp_path / "pkg")
    _add_link(tmp_path, package, target_kind, "directory", "alias_modules")
    result = verify_package(package, "pkg")
    assert result.ok is False
    assert any(item.kind == INVALID_PATH and item.path == "alias_modules" for item in result.diagnostics)


def test_f9_verify_rejects_internal_directory_link_control(tmp_path):
    _f9_control(tmp_path, "internal")


def test_f9_verify_rejects_escaping_directory_link_control(tmp_path):
    _f9_control(tmp_path, "escaping")


def test_direct_seal_rejects_root_link_without_following(tmp_path):
    target = _regular_package(tmp_path / "target")
    root = tmp_path / "root"
    root.symlink_to(target, target_is_directory=True)
    _assert_seal_invalid(root, ".")


@pytest.mark.parametrize(
    ("target_kind", "entry_kind"),
    [
        ("internal", "file"),
        ("escaping", "file"),
        ("dangling", "file"),
        ("internal", "directory"),
        ("escaping", "directory"),
        ("dangling", "directory"),
    ],
)
def _direct_matrix(tmp_path: Path, target_kind: str, entry_kind: str) -> None:
    package = _regular_package(tmp_path / "pkg")
    _add_link(tmp_path, package, target_kind, entry_kind)
    _assert_seal_invalid(package, "alias")


def test_direct_seal_rejects_internal_file_link_without_following(tmp_path):
    _direct_matrix(tmp_path, "internal", "file")


def test_direct_seal_rejects_escaping_file_link_without_following(tmp_path):
    _direct_matrix(tmp_path, "escaping", "file")


def test_direct_seal_rejects_dangling_file_link_without_following(tmp_path):
    _direct_matrix(tmp_path, "dangling", "file")


def test_direct_seal_rejects_internal_directory_link_without_following(tmp_path):
    _direct_matrix(tmp_path, "internal", "directory")


def test_direct_seal_rejects_escaping_directory_link_without_following(tmp_path):
    _direct_matrix(tmp_path, "escaping", "directory")


def test_direct_seal_rejects_dangling_directory_link_without_following(tmp_path):
    _direct_matrix(tmp_path, "dangling", "directory")


def test_direct_seal_rejects_excluded_link_before_coverage(tmp_path):
    package = _regular_package(tmp_path / "pkg")
    _add_link(tmp_path, package, "dangling", "file", "contracts/package_contract.json")
    _assert_seal_invalid(package, "contracts/package_contract.json")


def test_verify_rejects_root_link_before_seal_load(tmp_path):
    target = _sealed(tmp_path / "target")
    root = tmp_path / "root"
    root.symlink_to(target, target_is_directory=True)
    _assert_verify_invalid(root, ".")


def test_verify_rejects_contracts_link_before_seal_load(tmp_path):
    package = _sealed(tmp_path / "pkg")
    outside = tmp_path / "outside-contracts"
    (outside).mkdir()
    for child in (package / "contracts").iterdir():
        (outside / child.name).write_bytes(child.read_bytes())
    for child in (package / "contracts").iterdir():
        child.unlink()
    (package / "contracts").rmdir()
    (package / "contracts").symlink_to(outside, target_is_directory=True)
    _assert_verify_invalid(package, "contracts")


def test_verify_rejects_linked_seal_file_before_seal_load(tmp_path):
    package = _sealed(tmp_path / "pkg")
    seal_path = package / "contracts/package_contract.json"
    outside = tmp_path / "outside-seal.json"
    outside.write_bytes(seal_path.read_bytes())
    seal_path.unlink()
    seal_path.symlink_to(outside)
    _assert_verify_invalid(package, "contracts/package_contract.json")


@pytest.mark.parametrize(
    ("target_kind", "entry_kind"),
    [
        ("internal", "file"),
        ("escaping", "file"),
        ("dangling", "file"),
        ("dangling", "directory"),
    ],
)
def _verify_matrix(tmp_path: Path, target_kind: str, entry_kind: str) -> None:
    package = _sealed(tmp_path / "pkg")
    _add_link(tmp_path, package, target_kind, entry_kind)
    _assert_verify_invalid(package, "alias")


def test_verify_rejects_internal_file_link_without_following(tmp_path):
    _verify_matrix(tmp_path, "internal", "file")


def test_verify_rejects_escaping_file_link_without_following(tmp_path):
    _verify_matrix(tmp_path, "escaping", "file")


def test_verify_rejects_dangling_file_link_without_following(tmp_path):
    _verify_matrix(tmp_path, "dangling", "file")


def test_verify_rejects_dangling_directory_link_without_following(tmp_path):
    _verify_matrix(tmp_path, "dangling", "directory")


def test_verify_rejects_excluded_link_before_coverage(tmp_path):
    package = _sealed(tmp_path / "pkg")
    _add_link(tmp_path, package, "dangling", "file", "runtime/ignored.py")
    _assert_verify_invalid(package, "runtime/ignored.py")


def test_verify_reports_only_lexical_first_link(tmp_path):
    package = _sealed(tmp_path / "pkg")
    _add_link(tmp_path, package, "dangling", "file", "z-link")
    _add_link(tmp_path, package, "dangling", "file", "a-link")
    _assert_verify_invalid(package, "a-link")


def test_verify_link_precedes_missing_extra_and_tamper(tmp_path):
    package = _sealed(tmp_path / "pkg")
    (package / "modules/calc.py").write_text("tampered\n")
    (package / "pipelines").mkdir()
    (package / "pipelines/extra.yaml").write_text("extra\n")
    _add_link(tmp_path, package, "dangling", "file", "a-link")
    _assert_verify_invalid(package, "a-link")


def test_preflight_walk_error_precedes_descendant_claim(tmp_path, monkeypatch):
    package = _sealed(tmp_path / "pkg")
    original = Path.rglob

    def fail_walk(path, pattern):
        if path == package:
            raise PermissionError("walk denied")
        return original(path, pattern)

    monkeypatch.setattr(Path, "rglob", fail_walk)
    result = verify_package(package, "pkg")
    assert [(item.kind, item.path) for item in result.diagnostics] == [(ARTIFACT_UNREADABLE, None)]
    assert result.diagnostics[0].message.startswith("package artifact preflight failed: walk denied")


def test_generation_rejects_existing_root_link_before_output_mutation(tmp_path, monkeypatch):
    target = tmp_path / "target"
    target.mkdir()
    marker = target / "marker.txt"
    marker.write_text("unchanged\n")
    output = tmp_path / "out"
    output.symlink_to(target, target_is_directory=True)

    clear_reached = False

    def record_clear(config):
        nonlocal clear_reached
        clear_reached = True

    monkeypatch.setattr("sysml_codegen.cli._clear_output_directory", record_clear)
    assert run_codegen(_snapshot_config(output)) is False
    assert clear_reached is False
    assert marker.read_text() == "unchanged\n"


def test_step9_link_failure_writes_no_partial_contract(tmp_path):
    from sysml_codegen.cli import _seal_package

    output = tmp_path / "out"
    output.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    marker = outside / "marker.txt"
    marker.write_text("unchanged\n")
    (output / "contracts").symlink_to(outside, target_is_directory=True)
    config = GenerationConfig(output_path=output, from_snapshot=CHAIN_SNAPSHOT, package_name="pkg")
    ctx = type("Ctx", (), {"computation_graph": ComputationGraph(modules=[], entry_point_groups=[], execution_order=[])})()
    error_type = getattr(seal_module, "PackageSealError", ValueError)
    with pytest.raises(error_type):
        _seal_package(ctx, config)
    assert marker.read_text() == "unchanged\n"
    assert not (outside / "package_contract.json").exists()


def test_reseal_rejects_contracts_link_before_model_contract_check(tmp_path):
    package = tmp_path / "pkg"
    package.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "model_contract.json").write_text("{}\n")
    marker = outside / "marker.txt"
    marker.write_text("unchanged\n")
    (package / "contracts").symlink_to(outside, target_is_directory=True)
    args = argparse.Namespace(package_dir=package, package_name="pkg", verbose=False)
    assert cmd_seal(args) == 1
    assert marker.read_text() == "unchanged\n"
    assert not (outside / "package_contract.json").exists()


def test_emitted_verifier_matches_canonical_link_policy(tmp_path):
    output = tmp_path / "out"
    assert run_codegen(_snapshot_config(output))
    canonical = Path(seal_module.__file__).with_name("verify.py").read_bytes()
    emitted = output / "contracts/verify.py"
    assert emitted.read_bytes() == canonical
    (output / "dangling.py").symlink_to(tmp_path / "missing.py")
    namespace = runpy.run_path(str(emitted))
    result = namespace["verify_package"](output, "chain_spike")
    assert [(item.kind, item.path, item.message) for item in result.diagnostics] == [
        (INVALID_PATH, "dangling.py", FORBIDDEN_MESSAGE)
    ]
