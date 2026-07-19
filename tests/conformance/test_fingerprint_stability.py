"""Phase 4: SC-4 fingerprint stability + parity, the canary this item cannot prove alone.

Offline leg (cross-session): two independent from-snapshot generations of the same
fixture produce byte-identical fingerprints. License leg (live-vs-snapshot): the
fingerprints are the only pipeline-dependent surface (B1) — if Item 8's byte-identity
regresses, this fails loudly rather than the divergence surfacing later at the study
layer (design.md:382-385).
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from sysml_codegen.cli import GenerationConfig, run_codegen
from tests.conftest import FIXTURES_DIR, requires_license

CHAIN_SNAPSHOT = FIXTURES_DIR / "chain_spike_model" / "extraction_snapshot.json"
REPO_ROOT = Path(__file__).resolve().parents[2]
REVIEWED_REVISION = "512786c7dfab44fba7a0185d09e845b7494c702d"
REVIEWED_VERIFY_SHA256 = "24eb3565b0a7a682cf8a2510c871d7af9baa938fdaac6b5e826f88045a400276"


def _exec_fp(package_dir: Path) -> str:
    seal = json.loads((package_dir / "contracts" / "package_contract.json").read_text())
    return seal["executable_fingerprint"]


def _sem_fp(package_dir: Path) -> str:
    mc = json.loads((package_dir / "contracts" / "model_contract.json").read_text())
    return mc["semantic_fingerprint"]


def _seal(package_dir: Path) -> dict:
    return json.loads((package_dir / "contracts/package_contract.json").read_text())


def test_fingerprints_stable_across_independent_generation(tmp_path):
    out_a = tmp_path / "a"
    out_b = tmp_path / "b"
    for out in (out_a, out_b):
        config = GenerationConfig(
            output_path=out,
            from_snapshot=CHAIN_SNAPSHOT,
            package_name="chain_spike",
            overwrite=True,
        )
        assert run_codegen(config)

    assert _exec_fp(out_a) == _exec_fp(out_b)
    assert _sem_fp(out_a) == _sem_fp(out_b)
    first = _seal(out_a)
    second = _seal(out_b)
    assert first["artifact_hashes"] == second["artifact_hashes"]
    fingerprint_input = "\n".join(
        f"{path}:{digest}" for path, digest in sorted(first["artifact_hashes"].items())
    ).encode()
    assert first["executable_fingerprint"] == hashlib.sha256(fingerprint_input).hexdigest()


def _generate_with_source(source_root: Path, output: Path) -> None:
    script = """
import sys
from pathlib import Path
from sysml_codegen.cli import GenerationConfig, run_codegen

output = Path(sys.argv[1])
snapshot = Path(sys.argv[2])
config = GenerationConfig(
    output_path=output,
    from_snapshot=snapshot,
    package_name="chain_spike",
    overwrite=True,
)
if not run_codegen(config):
    raise SystemExit(1)
"""
    environment = os.environ.copy()
    environment.update(
        {
            "PYTHONNOUSERSITE": "1",
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONPATH": str(source_root / "src"),
        }
    )
    subprocess.run(
        [sys.executable, "-c", script, str(output), str(CHAIN_SNAPSHOT)],
        check=True,
        cwd=REPO_ROOT,
        env=environment,
    )


def test_policy_update_changes_only_verifier_hash_and_derived_fingerprint(tmp_path):
    archive = tmp_path / "reviewed.tar"
    reviewed_source = tmp_path / "reviewed"
    reviewed_source.mkdir()
    subprocess.run(
        ["git", "archive", "--format=tar", f"--output={archive}", REVIEWED_REVISION],
        check=True,
        cwd=REPO_ROOT,
    )
    subprocess.run(["tar", "-xf", archive, "-C", reviewed_source], check=True)

    reviewed_output = tmp_path / "reviewed-output"
    candidate_output = tmp_path / "candidate-output"
    _generate_with_source(reviewed_source, reviewed_output)
    _generate_with_source(REPO_ROOT, candidate_output)

    reviewed_seal = _seal(reviewed_output)
    candidate_seal = _seal(candidate_output)
    reviewed_hashes = dict(reviewed_seal["artifact_hashes"])
    candidate_hashes = dict(candidate_seal["artifact_hashes"])
    reviewed_verifier_hash = reviewed_hashes.pop("contracts/verify.py")
    candidate_verifier_hash = candidate_hashes.pop("contracts/verify.py")

    assert reviewed_hashes == candidate_hashes
    assert reviewed_verifier_hash == REVIEWED_VERIFY_SHA256
    canonical_candidate = (REPO_ROOT / "src/sysml_codegen/contracts/verify.py").read_bytes()
    emitted_candidate = (candidate_output / "contracts/verify.py").read_bytes()
    assert emitted_candidate == canonical_candidate
    assert candidate_verifier_hash == hashlib.sha256(canonical_candidate).hexdigest()
    assert candidate_verifier_hash != reviewed_verifier_hash

    for seal in (reviewed_seal, candidate_seal):
        fingerprint_input = "\n".join(
            f"{path}:{digest}" for path, digest in sorted(seal["artifact_hashes"].items())
        ).encode()
        assert seal["executable_fingerprint"] == hashlib.sha256(fingerprint_input).hexdigest()
    assert reviewed_seal["executable_fingerprint"] != candidate_seal["executable_fingerprint"]


@requires_license
@pytest.mark.parametrize("fixture", ["wi014_toy", "constraint_multi_instance"])
def test_fingerprints_stable_live_vs_snapshot(fixture, tmp_path):
    live_out = tmp_path / "live"
    snap_out = tmp_path / "snap"

    live_config = GenerationConfig(
        output_path=live_out,
        models_path=FIXTURES_DIR / fixture,
        package_name=fixture,
        overwrite=True,
    )
    assert run_codegen(live_config)

    snap_config = GenerationConfig(
        output_path=snap_out,
        from_snapshot=FIXTURES_DIR / fixture / "extraction_snapshot.json",
        package_name=fixture,
        overwrite=True,
    )
    assert run_codegen(snap_config)

    assert _exec_fp(live_out) == _exec_fp(snap_out)
    assert _sem_fp(live_out) == _sem_fp(snap_out)
