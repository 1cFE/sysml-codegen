"""Conformance tests for the snapshot generation surface (Item 2, SC-9).

Covers the context builder and CLI wiring:
- INV-4/B1: a snapshot PipelineContext has null extractor/backtracker and still generates.
- INV-1: `generate --from-snapshot` completes with no license at runtime.
- INV-6: no provenance/version text reaches a generated artifact.
- INV-7/V6: the CLI accepts exactly one extraction input, and rejects
  `--from-snapshot` + `--design-path-filter`.
- Dead-template: the lone generation timestamp has zero render sites.

Requirements: REQ-SNAP-13 through REQ-SNAP-18.
"""

from __future__ import annotations

import functools
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from tests.conftest import snapshot_fixture

REPO_ROOT = Path(__file__).resolve().parents[2]
CLI = str(Path(sys.executable).parent / "sysml-codegen")
CHAIN_SNAPSHOT = "tests/fixtures/chain_spike_model/extraction_snapshot.json"

_LICENSE_VARS = ("SYSIDE_LICENSE_KEY", "SYSIDE_LICENSE", "SYSIDE_LICENSE_FILE")


@functools.lru_cache(maxsize=1)
def _license_available() -> bool:
    """True if a live syside license can load a model (else the test skips)."""
    from sysml_codegen.extraction.extractor import SysMLDataExtractor

    try:
        extractor = SysMLDataExtractor([REPO_ROOT / "tests/fixtures/chain_spike_model"])
        return bool(extractor.load_models())
    except ImportError:
        return False


requires_license = pytest.mark.skipif(
    not _license_available(), reason="no live syside license"
)


def _tree_diff(a: Path, b: Path) -> list[str]:
    """Recursive byte-level diff of two output trees; empty list == identical."""
    a_files = {p.relative_to(a) for p in a.rglob("*") if p.is_file()}
    b_files = {p.relative_to(b) for p in b.rglob("*") if p.is_file()}
    diffs = [f"only in one tree: {rel}" for rel in sorted(a_files ^ b_files)]
    diffs += [
        f"differs: {rel}"
        for rel in sorted(a_files & b_files)
        if (a / rel).read_bytes() != (b / rel).read_bytes()
    ]
    return diffs


def _run_cli(*args: str, scrub_license: bool = False) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    if scrub_license:
        for var in _LICENSE_VARS:
            env.pop(var, None)
    return subprocess.run(
        [CLI, *args], cwd=REPO_ROOT, capture_output=True, text=True, env=env
    )


# ===========================================================================
# REQ-SNAP-13 (INV-4/B1): snapshot context has null extractor/backtracker and generates.
# ===========================================================================
@pytest.mark.req("REQ-SNAP-13")
def test_snapshot_context_has_null_extractor_and_generates(tmp_path):
    from sysml_codegen.cli import GenerationConfig, run_codegen
    from sysml_codegen.orchestration.snapshot_context import (
        build_pipeline_context_from_snapshot,
    )

    ctx = build_pipeline_context_from_snapshot(snapshot_fixture("solar_battery_model"))
    assert ctx.extractor is None
    assert ctx.backtracker is None  # INV-4

    # B1: no generation path dereferences the null fields.
    config = GenerationConfig(
        output_path=tmp_path / "out",
        from_snapshot=snapshot_fixture("solar_battery_model"),
        package_name="solar_battery",
        overwrite=True,
    )
    assert run_codegen(config) is True


# ===========================================================================
# REQ-SNAP-14 (INV-1): license-free runtime generation from a snapshot.
# ===========================================================================
@pytest.mark.req("REQ-SNAP-14")
def test_generate_from_snapshot_no_license(tmp_path):
    result = _run_cli(
        "generate", "--from-snapshot", CHAIN_SNAPSHOT,
        "--output", str(tmp_path / "out"), "--package-name", "chain_spike",
        "--overwrite",
        scrub_license=True,
    )
    assert result.returncode == 0, result.stderr
    assert (tmp_path / "out" / "__init__.py").exists()


# ===========================================================================
# REQ-SNAP-15 (INV-6): provenance/version text never reaches a generated artifact.
# ===========================================================================
@pytest.mark.req("REQ-SNAP-15")
def test_provenance_never_in_output(tmp_path):
    out = tmp_path / "out"
    result = _run_cli(
        "generate", "--from-snapshot", CHAIN_SNAPSHOT,
        "--output", str(out), "--package-name", "chain_spike", "--overwrite",
    )
    assert result.returncode == 0, result.stderr
    needles = ("This run did NOT use live extraction", "snapshot_format_version", "captured ")
    for path in out.rglob("*"):
        if path.is_file():
            text = path.read_text(errors="ignore")
            for needle in needles:
                assert needle not in text, f"{needle!r} leaked into {path}"


# ===========================================================================
# REQ-SNAP-16 (INV-7/V6): CLI accepts exactly one extraction input.
# ===========================================================================
@pytest.mark.req("REQ-SNAP-16")
def test_generate_neither_input_is_error(tmp_path):
    result = _run_cli("generate", "--output", str(tmp_path / "out"))
    assert result.returncode == 2  # argparse required-group error
    assert "one of the arguments" in result.stderr


@pytest.mark.req("REQ-SNAP-16")
def test_generate_both_inputs_is_error(tmp_path):
    result = _run_cli(
        "generate", "--models", "tests/fixtures/chain_spike_model",
        "--from-snapshot", CHAIN_SNAPSHOT, "--output", str(tmp_path / "out"),
    )
    assert result.returncode == 2  # mutually exclusive
    assert "not allowed with argument" in result.stderr


@pytest.mark.req("REQ-SNAP-16")
def test_from_snapshot_rejects_design_path_filter(tmp_path):
    result = _run_cli(
        "generate", "--from-snapshot", CHAIN_SNAPSHOT,
        "--output", str(tmp_path / "out"), "--design-path-filter", "designs/",
    )
    assert result.returncode == 1  # cmd_generate hard error (V6)
    assert "design-path-filter cannot be combined with --from-snapshot" in result.stderr


# ===========================================================================
# REQ-SNAP-17 (INV-5/SC-10): chain_spike CalcUsage auto-implements from a snapshot.
# ===========================================================================
@pytest.mark.req("REQ-SNAP-17")
def test_chain_spike_autoimpl_from_snapshot(tmp_path):
    out = tmp_path / "out"
    result = _run_cli(
        "generate", "--from-snapshot", CHAIN_SNAPSHOT,
        "--output", str(out), "--package-name", "chain_spike", "--overwrite",
    )
    assert result.returncode == 0, result.stderr
    stencils = list((out / "handwritten").rglob("*_impl.py"))
    assert stencils, "no CalcUsage stencils generated"
    for stencil in stencils:
        text = stencil.read_text()
        assert "NotImplementedError" not in text, f"{stencil} regressed to a stub"
        assert "AUTO_IMPLEMENTED = True" in text


# ===========================================================================
# REQ-SNAP-19 (SC-1): live generation is byte-identical to snapshot generation.
# License-gated; skips cleanly with no license.
# ===========================================================================
@requires_license
@pytest.mark.req("REQ-SNAP-19")
def test_live_vs_snapshot_byte_identical(tmp_path):
    """generate --models <abs> == generate --from-snapshot, byte-for-byte."""
    # Feed live an ABSOLUTE --models path so the parser emits the absolute
    # source_file the loader re-absolutizes against the committed snapshot's dir.
    abs_models = REPO_ROOT / "tests/fixtures/solar_battery_model"
    live_out, snap_out = tmp_path / "live", tmp_path / "snap"

    live = _run_cli(
        "generate", "--models", str(abs_models),
        "--output", str(live_out), "--package-name", "solar_battery", "--overwrite",
    )
    assert live.returncode == 0, live.stderr

    snap = _run_cli(
        "generate", "--from-snapshot", str(abs_models / "extraction_snapshot.json"),
        "--output", str(snap_out), "--package-name", "solar_battery", "--overwrite",
    )
    assert snap.returncode == 0, snap.stderr

    assert _tree_diff(live_out, snap_out) == []


@requires_license
@pytest.mark.req("REQ-SNAP-19")
def test_live_vs_snapshot_byte_identical_symlinked(tmp_path):
    """SC-1 on a SYMLINKED source path (D8/B2 at integration scale).

    Copy the sources so the snapshot can be written beside them, symlink the copy,
    and drive both live and snapshot generation through the symlink — the parser
    preserves the symlink name and the lexical re-absolutization reproduces it.
    """
    real = tmp_path / "real"
    shutil.copytree(REPO_ROOT / "tests/fixtures/solar_battery_model", real)
    (real / "extraction_snapshot.json").unlink(missing_ok=True)
    link = tmp_path / "link"
    link.symlink_to(real)

    # Capture a snapshot through the symlink (writes into real via the link).
    cap = _run_cli(
        "snapshot", "--models", str(link),
        "--output", str(link / "extraction_snapshot.json"),
    )
    assert cap.returncode == 0, cap.stderr

    live_out, snap_out = tmp_path / "live", tmp_path / "snap"
    live = _run_cli(
        "generate", "--models", str(link),
        "--output", str(live_out), "--package-name", "solar_battery", "--overwrite",
    )
    assert live.returncode == 0, live.stderr
    snap = _run_cli(
        "generate", "--from-snapshot", str(link / "extraction_snapshot.json"),
        "--output", str(snap_out), "--package-name", "solar_battery", "--overwrite",
    )
    assert snap.returncode == 0, snap.stderr

    assert _tree_diff(live_out, snap_out) == []


# ===========================================================================
# REQ-SNAP-18 (dead template): the lone generation timestamp has zero render sites.
# ===========================================================================
@pytest.mark.req("REQ-SNAP-18")
def test_generation_timestamp_has_no_render_site():
    """generation_timestamp is a latent byte-identity trap — must stay unwired."""
    out = subprocess.run(
        ["grep", "-rn", "generation_timestamp", "src"],
        cwd=REPO_ROOT, capture_output=True, text=True,
    )
    # The only permitted mention is the template variable itself (never rendered
    # from Python): no .py passes it into a render() call.
    py_render = subprocess.run(
        ["grep", "-rn", "generation_timestamp", "src/sysml_codegen"],
        cwd=REPO_ROOT, capture_output=True, text=True,
    )
    offenders = [
        line for line in py_render.stdout.splitlines() if line.split(":", 1)[0].endswith(".py")
    ]
    assert offenders == [], f"generation_timestamp is wired from Python: {offenders}"
