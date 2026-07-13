"""Phase 4: SC-4 fingerprint stability + parity, the canary this item cannot prove alone.

Offline leg (cross-session): two independent from-snapshot generations of the same
fixture produce byte-identical fingerprints. License leg (live-vs-snapshot): the
fingerprints are the only pipeline-dependent surface (B1) — if Item 8's byte-identity
regresses, this fails loudly rather than the divergence surfacing later at the study
layer (design.md:382-385).
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from sysml_codegen.cli import GenerationConfig, run_codegen
from tests.conftest import FIXTURES_DIR, requires_license

CHAIN_SNAPSHOT = FIXTURES_DIR / "chain_spike_model" / "extraction_snapshot.json"


def _exec_fp(package_dir: Path) -> str:
    seal = json.loads((package_dir / "contracts" / "package_contract.json").read_text())
    return seal["executable_fingerprint"]


def _sem_fp(package_dir: Path) -> str:
    mc = json.loads((package_dir / "contracts" / "model_contract.json").read_text())
    return mc["semantic_fingerprint"]


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
