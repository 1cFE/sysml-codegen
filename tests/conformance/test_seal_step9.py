"""Phase 3: Step 9 wiring, `seal` subcommand, emitted-verbatim verifier.

Offline — sealing needs no license; from-snapshot generation is license-free (Item 8).
Proves the seal joins `run_codegen` as its final step (D1), the emitted verifier is
byte-identical to the in-repo source (INV-8), and re-seal recomputes only the
`PackageContract` (D2).
"""

from __future__ import annotations

import argparse
import runpy
from pathlib import Path

from sysml_codegen.cli import GenerationConfig, cmd_seal, run_codegen
from sysml_codegen.contracts.verify import verify_package

REPO_ROOT = Path(__file__).resolve().parents[2]
CHAIN_SNAPSHOT = REPO_ROOT / "tests/fixtures/chain_spike_model/extraction_snapshot.json"
SRC_VERIFY = REPO_ROOT / "src" / "sysml_codegen" / "contracts" / "verify.py"


def _snapshot_config(output_path: Path, package_name: str = "chain_spike") -> GenerationConfig:
    return GenerationConfig(
        output_path=output_path,
        from_snapshot=CHAIN_SNAPSHOT,
        package_name=package_name,
        overwrite=True,
    )


def _seal_args(package_dir: Path, package_name: str) -> argparse.Namespace:
    return argparse.Namespace(package_dir=package_dir, package_name=package_name, verbose=False)


def test_generate_emits_three_contract_files(tmp_path):
    output = tmp_path / "out"
    assert run_codegen(_snapshot_config(output))

    contracts = output / "contracts"
    assert (contracts / "model_contract.json").exists()
    assert (contracts / "verify.py").exists()
    assert (contracts / "package_contract.json").exists()
    assert verify_package(output, "chain_spike").ok


def test_emitted_verifier_is_verbatim(tmp_path):
    """INV-8 drift guard: the emitted copy is byte-identical to the canonical source."""
    output = tmp_path / "out"
    assert run_codegen(_snapshot_config(output))

    emitted = (output / "contracts" / "verify.py").read_bytes()
    canonical = SRC_VERIFY.read_bytes()
    assert emitted == canonical


def test_emitted_verifier_rejects_internal_directory_symlink(tmp_path):
    output = tmp_path / "out"
    assert run_codegen(_snapshot_config(output))
    (output / "alias_modules").symlink_to(output / "modules", target_is_directory=True)

    emitted_namespace = runpy.run_path(str(output / "contracts" / "verify.py"))
    result = emitted_namespace["verify_package"](output, "chain_spike")

    assert result.ok is False
    assert any(
        diagnostic.kind == "INVALID_PATH" and diagnostic.path == "alias_modules"
        for diagnostic in result.diagnostics
    )


def test_seal_ordering_excludes_itself_from_coverage(tmp_path):
    """INV-3: package_contract.json is written last and never in its own coverage set."""
    import json

    output = tmp_path / "out"
    assert run_codegen(_snapshot_config(output))

    seal = json.loads((output / "contracts" / "package_contract.json").read_text())
    assert "contracts/package_contract.json" not in seal["artifact_hashes"]
    assert "contracts/model_contract.json" in seal["artifact_hashes"]
    assert "contracts/verify.py" in seal["artifact_hashes"]


def test_reseal_after_stencil_edit(tmp_path):
    """D1/D2 re-seal workflow: seal -> edit -> invalid -> `seal` -> valid; MC unchanged."""
    output = tmp_path / "out"
    assert run_codegen(_snapshot_config(output))

    mc_before = (output / "contracts" / "model_contract.json").read_bytes()

    handwritten_files = list((output / "handwritten").glob("*.py"))
    assert handwritten_files, "expected at least one generated stencil"
    edited = handwritten_files[0]
    edited.write_text(edited.read_text() + "\n# human edit\n")

    assert not verify_package(output, "chain_spike").ok

    assert cmd_seal(_seal_args(output, "chain_spike")) == 0
    assert verify_package(output, "chain_spike").ok

    mc_after = (output / "contracts" / "model_contract.json").read_bytes()
    assert mc_after == mc_before


def test_seal_subcommand_requires_existing_model_contract(tmp_path):
    """D2: `seal` re-seals a package `generate` already sealed once — it never builds a
    ModelContract from scratch."""
    empty_dir = tmp_path / "not_a_package"
    empty_dir.mkdir()
    assert cmd_seal(_seal_args(empty_dir, "chain_spike")) == 1
