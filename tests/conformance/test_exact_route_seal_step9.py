"""Gate 4C, row L-169: seal step 9 on a package the exact route generated.

The responsibility this replaces belonged to
``tests/conformance/test_seal_step9.py``: generation's final step emits three
contract files plus a generation manifest, the emitted verifier is byte-identical
to the in-repo source, the seal never covers itself, and re-seal refuses a
foreign file, a tampered generated file, and a symlinked contracts directory.
Its specimen was a **v5** extraction snapshot of ``chain_spike_model``; the
shipped ``--from-snapshot`` is v6 and the exact route refuses that model live.

The specimen here is the committed v6 instance-graph snapshot of ``fusion_tea``,
driven through ``run_codegen``. That keeps the original's most useful property:
sealing needs no license, so these nodes run in any environment.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import runpy
from pathlib import Path

import pytest

from sysml_codegen.cli import GenerationConfig, cmd_seal, run_codegen
from sysml_codegen.contracts.verify import verify_package
from tests.conftest import FIXTURES_DIR

REPO_ROOT = Path(__file__).resolve().parents[2]
V6_SNAPSHOT = FIXTURES_DIR / "fusion_tea" / "instance_graph_snapshot.json"
SRC_VERIFY = REPO_ROOT / "src" / "sysml_codegen" / "contracts" / "verify.py"
PACKAGE = "fusion_tea"


def _generate(output: Path) -> Path:
    assert run_codegen(
        GenerationConfig(
            output_path=output,
            from_snapshot=V6_SNAPSHOT,
            package_name=PACKAGE,
            overwrite=True,
        )
    ), "the v6 snapshot route must generate fusion_tea"
    return output


def _seal_args(package_dir: Path) -> argparse.Namespace:
    return argparse.Namespace(package_dir=package_dir, package_name=PACKAGE, verbose=False)


@pytest.fixture
def package(tmp_path: Path) -> Path:
    return _generate(tmp_path / "out")


def test_generation_emits_three_contract_files_and_they_verify(package: Path) -> None:
    contracts = package / "contracts"
    assert (contracts / "model_contract.json").exists()
    assert (contracts / "verify.py").exists()
    assert (contracts / "package_contract.json").exists()
    assert verify_package(package, PACKAGE).ok


def test_the_emitted_verifier_is_byte_identical_to_the_source(package: Path) -> None:
    canonical = SRC_VERIFY.read_bytes()
    assert (package / "contracts" / "verify.py").read_bytes() == canonical

    seal = json.loads((package / "contracts/package_contract.json").read_text())
    assert seal["artifact_hashes"]["contracts/verify.py"] == hashlib.sha256(canonical).hexdigest()


def test_the_published_trusted_verifier_hash_matches_the_canonical_source() -> None:
    """A verifier edit that forgets to re-publish the constant trips here."""
    from sysml_codegen.contracts.versions import TRUSTED_VERIFIER_SHA256

    assert TRUSTED_VERIFIER_SHA256 == hashlib.sha256(SRC_VERIFY.read_bytes()).hexdigest()


def test_the_emitted_verifier_rejects_an_internal_directory_symlink(package: Path) -> None:
    (package / "alias_modules").symlink_to(package / "modules", target_is_directory=True)

    emitted = runpy.run_path(str(package / "contracts" / "verify.py"))
    result = emitted["verify_package"](package, PACKAGE)

    assert result.ok is False
    assert any(
        diagnostic.kind == "INVALID_PATH" and diagnostic.path == "alias_modules"
        for diagnostic in result.diagnostics
    )


def test_the_emitted_verifier_rejects_a_dangling_file_symlink(package: Path) -> None:
    (package / "dangling.py").symlink_to(package.parent / "missing.py")

    emitted = runpy.run_path(str(package / "contracts" / "verify.py"))
    result = emitted["verify_package"](package, PACKAGE)

    assert [(item.kind, item.path, item.message) for item in result.diagnostics] == [
        (
            "INVALID_PATH",
            "dangling.py",
            "symlinks are forbidden beneath the package root",
        )
    ]


def test_the_seal_is_written_last_and_excludes_itself(package: Path) -> None:
    seal = json.loads((package / "contracts" / "package_contract.json").read_text())
    assert "contracts/package_contract.json" not in seal["artifact_hashes"]
    assert "contracts/model_contract.json" in seal["artifact_hashes"]
    assert "contracts/verify.py" in seal["artifact_hashes"]


def test_reseal_after_a_stencil_edit_restores_validity_without_touching_the_model(
    package: Path,
) -> None:
    model_contract_before = (package / "contracts" / "model_contract.json").read_bytes()

    stencils = sorted((package / "handwritten").rglob("*_impl.py"))
    assert stencils, "expected at least one generated stencil"
    stencils[0].write_text(stencils[0].read_text() + "\n# human edit\n")

    assert not verify_package(package, PACKAGE).ok
    assert cmd_seal(_seal_args(package)) == 0
    assert verify_package(package, PACKAGE).ok
    assert (package / "contracts" / "model_contract.json").read_bytes() == model_contract_before


def test_reseal_refuses_a_foreign_file_dropped_into_a_codegen_region(package: Path) -> None:
    """A file the manifest never enumerated must not be laundered into the seal."""
    foreign = package / "modules" / "evil.py"
    foreign.write_text("# injected\nPWNED = True\n")

    assert cmd_seal(_seal_args(package)) == 1
    seal = json.loads((package / "contracts" / "package_contract.json").read_text())
    assert "modules/evil.py" not in seal["artifact_hashes"]


def test_reseal_refuses_an_edit_to_a_codegen_produced_file(package: Path) -> None:
    """Only ``handwritten/**`` may change across a re-seal."""
    modules = sorted((package / "modules").rglob("*.py"))
    assert modules
    modules[0].write_text(modules[0].read_text() + "\n# tampered generated file\n")

    assert cmd_seal(_seal_args(package)) == 1


def test_the_seal_step_refuses_a_symlinked_contracts_directory_before_writing(
    tmp_path: Path,
) -> None:
    from sysml_codegen.cli import _seal_package
    from sysml_codegen.contracts.seal import PackageSealError
    from sysml_codegen.resolution.models import ComputationGraph

    output = tmp_path / "out"
    output.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    marker = outside / "marker.txt"
    marker.write_text("unchanged\n")
    (output / "contracts").symlink_to(outside, target_is_directory=True)

    config = GenerationConfig(
        output_path=output, from_snapshot=V6_SNAPSHOT, package_name=PACKAGE, overwrite=True
    )
    with pytest.raises(PackageSealError) as refusal:
        _seal_package(
            ComputationGraph(modules=[], entry_point_groups=[], execution_order=[]), config
        )
    assert refusal.value.path == "contracts"
    assert marker.read_text() == "unchanged\n"
    assert not (outside / "package_contract.json").exists()


def test_the_seal_subcommand_refuses_a_directory_that_was_never_generated(
    tmp_path: Path,
) -> None:
    empty = tmp_path / "not_a_package"
    empty.mkdir()
    assert cmd_seal(_seal_args(empty)) == 1


def test_generation_emits_a_manifest_that_excludes_handwritten_files(package: Path) -> None:
    manifest_path = package / "contracts" / "generation_manifest.json"
    assert manifest_path.exists()
    manifest = json.loads(manifest_path.read_text())

    assert "contracts/verify.py" in manifest["codegen_produced"]
    assert "contracts/generation_manifest.json" in manifest["codegen_produced"]
    assert "handwritten/**" in manifest["handwritten_globs"]
    assert "runtime_contract_version" not in manifest
    assert not any(path.startswith("handwritten/") for path in manifest["codegen_produced"])

    seal = json.loads((package / "contracts" / "package_contract.json").read_text())
    assert "contracts/generation_manifest.json" in seal["artifact_hashes"]
