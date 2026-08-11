"""Phase 3: Step 9 wiring, `seal` subcommand, emitted-verbatim verifier.

Offline — sealing needs no license; from-snapshot generation is license-free (Item 8).
Proves the seal joins `run_codegen` as its final step (D1), the emitted verifier is
byte-identical to the in-repo source (INV-8), and re-seal recomputes only the
`PackageContract` (D2).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import runpy
from pathlib import Path

from sysml_codegen.cli import GenerationConfig, cmd_seal
from sysml_codegen.contracts.verify import verify_package
from tests.helpers.legacy_route import generate_via_legacy_route

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
    assert generate_via_legacy_route(_snapshot_config(output))

    contracts = output / "contracts"
    assert (contracts / "model_contract.json").exists()
    assert (contracts / "verify.py").exists()
    assert (contracts / "package_contract.json").exists()
    assert verify_package(output, "chain_spike").ok


def test_emitted_verifier_is_verbatim(tmp_path):
    """INV-8 drift guard: the emitted copy is byte-identical to the canonical source."""
    output = tmp_path / "out"
    assert generate_via_legacy_route(_snapshot_config(output))

    emitted = (output / "contracts" / "verify.py").read_bytes()
    canonical = SRC_VERIFY.read_bytes()
    assert emitted == canonical
    seal = json.loads((output / "contracts/package_contract.json").read_text())
    assert seal["artifact_hashes"]["contracts/verify.py"] == hashlib.sha256(canonical).hexdigest()


def test_trusted_verifier_hash_matches_canonical(tmp_path):
    """INV-B (codegen half): the published ``TRUSTED_VERIFIER_SHA256`` equals the sha256 of
    the canonical verifier. Combined with the verbatim-emit guard, this is what lets a runtime
    authenticate a package-local verifier against the vendored constant. A verify.py edit that
    forgets to re-publish (and re-vendor in TEAx) trips this test."""
    from sysml_codegen.contracts.versions import TRUSTED_VERIFIER_SHA256

    canonical = SRC_VERIFY.read_bytes()
    assert TRUSTED_VERIFIER_SHA256 == hashlib.sha256(canonical).hexdigest()


def test_emitted_verifier_rejects_internal_directory_symlink(tmp_path):
    output = tmp_path / "out"
    assert generate_via_legacy_route(_snapshot_config(output))
    (output / "alias_modules").symlink_to(output / "modules", target_is_directory=True)

    emitted_namespace = runpy.run_path(str(output / "contracts" / "verify.py"))
    result = emitted_namespace["verify_package"](output, "chain_spike")

    assert result.ok is False
    assert any(
        diagnostic.kind == "INVALID_PATH" and diagnostic.path == "alias_modules"
        for diagnostic in result.diagnostics
    )


def test_emitted_verifier_rejects_dangling_file_symlink(tmp_path):
    output = tmp_path / "out"
    assert generate_via_legacy_route(_snapshot_config(output))
    (output / "dangling.py").symlink_to(tmp_path / "missing.py")

    emitted_namespace = runpy.run_path(str(output / "contracts" / "verify.py"))
    result = emitted_namespace["verify_package"](output, "chain_spike")

    assert [(item.kind, item.path, item.message) for item in result.diagnostics] == [
        (
            "INVALID_PATH",
            "dangling.py",
            "symlinks are forbidden beneath the package root",
        )
    ]


def test_seal_ordering_excludes_itself_from_coverage(tmp_path):
    """INV-3: package_contract.json is written last and never in its own coverage set."""
    import json

    output = tmp_path / "out"
    assert generate_via_legacy_route(_snapshot_config(output))

    seal = json.loads((output / "contracts" / "package_contract.json").read_text())
    assert "contracts/package_contract.json" not in seal["artifact_hashes"]
    assert "contracts/model_contract.json" in seal["artifact_hashes"]
    assert "contracts/verify.py" in seal["artifact_hashes"]


def test_reseal_after_stencil_edit(tmp_path):
    """D1/D2 re-seal workflow: seal -> edit -> invalid -> `seal` -> valid; MC unchanged."""
    output = tmp_path / "out"
    assert generate_via_legacy_route(_snapshot_config(output))

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


def test_reseal_rejects_linked_contracts_before_model_contract_check(tmp_path):
    package = tmp_path / "pkg"
    package.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "model_contract.json").write_text("{}\n")
    prior_seal = outside / "package_contract.json"
    prior_seal.write_bytes(b"prior seal bytes\n")
    (package / "contracts").symlink_to(outside, target_is_directory=True)

    assert cmd_seal(_seal_args(package, "chain_spike")) == 1
    assert prior_seal.read_bytes() == b"prior seal bytes\n"


def test_step9_rejects_linked_contracts_without_writing_contract(tmp_path):
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
    config = _snapshot_config(output, package_name="chain_spike")
    context = type(
        "Context",
        (),
        {
            "computation_graph": ComputationGraph(
                modules=[], entry_point_groups=[], execution_order=[]
            )
        },
    )()

    try:
        _seal_package(context.computation_graph, config)
    except PackageSealError as error:
        assert error.path == "contracts"
    else:
        raise AssertionError("Step 9 accepted linked contracts directory")
    assert marker.read_text() == "unchanged\n"
    assert not (outside / "package_contract.json").exists()


def test_reseal_rejects_foreign_file_as_codegen_provenance(tmp_path):
    """Attack (b), RED-first: a foreign file dropped under a codegen region must not be
    laundered into the seal as covered provenance.

    The generation manifest (Item 7) records the codegen-produced set as
    tree-minus-``handwritten/**``-minus-runtime-globs at first seal. ``modules/evil.py`` is not
    in that enumerated set and not under a non-codegen glob, so re-seal hard-fails and never
    admits it. RED against pre-fix ``cmd_seal``, which hashed it into ``artifact_hashes``
    (``cli/__init__.py:762``) and returned 0.
    """
    output = tmp_path / "out"
    assert generate_via_legacy_route(_snapshot_config(output))

    foreign = output / "modules" / "evil.py"
    foreign.write_text("# injected\nPWNED = True\n")

    assert cmd_seal(_seal_args(output, "chain_spike")) == 1

    seal = json.loads((output / "contracts" / "package_contract.json").read_text())
    assert "modules/evil.py" not in seal["artifact_hashes"]


def test_reseal_rejects_edit_to_codegen_produced_file(tmp_path):
    """Attack (b) sibling: a codegen-produced file is byte-frozen across re-seal (INV-F). An
    edit to a generated module is laundering just as a foreign file is, so re-seal hard-fails
    rather than recording the edited bytes. Only ``handwritten/**`` files may change.
    """
    output = tmp_path / "out"
    assert generate_via_legacy_route(_snapshot_config(output))

    modules = sorted((output / "modules").glob("*.py"))
    assert modules, "expected at least one generated module"
    modules[0].write_text(modules[0].read_text() + "\n# tampered generated file\n")

    assert cmd_seal(_seal_args(output, "chain_spike")) == 1


def test_generate_emits_generation_manifest(tmp_path):
    """The manifest is a covered artifact enumerating the codegen-produced set (tree minus
    ``handwritten/**`` minus runtime globs); it carries no ``runtime_contract_version`` (the
    seal owns that)."""
    output = tmp_path / "out"
    assert generate_via_legacy_route(_snapshot_config(output))

    manifest_path = output / "contracts" / "generation_manifest.json"
    assert manifest_path.exists()
    manifest = json.loads(manifest_path.read_text())
    assert "contracts/verify.py" in manifest["codegen_produced"]
    assert "contracts/generation_manifest.json" in manifest["codegen_produced"]
    assert "handwritten/**" in manifest["handwritten_globs"]
    assert "runtime_contract_version" not in manifest
    # No handwritten file leaks into the codegen-produced set.
    assert not any(p.startswith("handwritten/") for p in manifest["codegen_produced"])

    seal = json.loads((output / "contracts" / "package_contract.json").read_text())
    assert "contracts/generation_manifest.json" in seal["artifact_hashes"]
