"""Shared pytest fixtures for sysml-codegen tests.

Provides:
- Sample SysML model loading
- Temporary directory management
- Test configuration
"""

from __future__ import annotations

import functools
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from sysml_codegen.extraction.extractor import SysMLDataExtractor

FIXTURES_DIR = Path(__file__).parent / "fixtures"
REPO_ROOT = Path(__file__).resolve().parent.parent


@functools.lru_cache(maxsize=1)
def _license_available() -> bool:
    """True if a live syside license can load a model (else license-gated tests skip).

    Cached so the probe runs one live ``load_models()`` per session. Shared by every
    ``@requires_license`` test — do not copy it, a second copy runs a second probe.
    """
    from sysml_codegen.extraction.extractor import SysMLDataExtractor

    try:
        extractor = SysMLDataExtractor([REPO_ROOT / "tests/fixtures/chain_spike_model"])
        return bool(extractor.load_models())
    except ImportError:
        return False


requires_license = pytest.mark.skipif(
    not _license_available(), reason="no live syside license"
)


def snapshot_fixture(model_name: str) -> Path:
    """Return the committed extraction-snapshot path for a fixture model.

    The promoted loader takes a snapshot path (not a fixtures-relative model
    name); this resolves ``model_name`` to
    ``tests/fixtures/<model_name>/extraction_snapshot.json`` for test call sites.
    """
    return FIXTURES_DIR / model_name / "extraction_snapshot.json"


def instance_graph_fixture(model_name: str) -> Path:
    """Return the committed v6 instance-graph snapshot path for a fixture model.

    The v6 counterpart of ``snapshot_fixture``. Both spellings live here through the
    transition so a test can be repointed one at a time: the v5 helper resolves the
    extraction snapshot the legacy route reads, this one the sealed instance graph the
    exact route reads. Reading a committed v6 snapshot needs no licence, which is what
    keeps a repointed conformance test in the license-free lane it was already in.
    """
    return FIXTURES_DIR / model_name / "instance_graph_snapshot.json"


def exact_graph_from_fixture(model_name: str):
    """The projected ComputationGraph of a fixture, read from its sealed v6 snapshot.

    The exact-route replacement for ``build_full_graph_from_snapshot(snapshot_fixture(...))``.
    That call returned ``(graph, classifier_inputs)`` because the legacy rebuild exposed its
    intermediate; the exact route has no such intermediate, so this returns the graph alone
    and a caller that wanted the second element has to say what it actually needs.
    """
    from sysml_codegen.elaboration import project
    from sysml_codegen.snapshot.envelope import load_instance_graph_snapshot

    return project(load_instance_graph_snapshot(instance_graph_fixture(model_name)))


@pytest.fixture
def fixtures_path() -> Path:
    """Return path to test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_model_path(fixtures_path: Path) -> Path:
    """Return path to sample SysML model directory."""
    return fixtures_path / "sample_model"


@pytest.fixture
def chain_spike_model_path(fixtures_path: Path) -> Path:
    """Return path to chain spike SysML model directory."""
    return fixtures_path / "chain_spike_model"


@pytest.fixture
def solar_battery_model_path(fixtures_path: Path) -> Path:
    """Return path to solar battery SysML model directory."""
    return fixtures_path / "solar_battery_model"


@pytest.fixture
def catf_mfe_model_path(fixtures_path: Path) -> Path:
    """Return path to CATF MFE SysML model directory."""
    return fixtures_path / "catf_mfe_model"


@pytest.fixture
def expected_outputs_path(fixtures_path: Path) -> Path:
    """Return path to expected outputs directory."""
    return fixtures_path / "expected_outputs"


@pytest.fixture
def simple_calc_sysml(sample_model_path: Path) -> Path:
    """Return path to simple_calc.sysml test fixture."""
    return sample_model_path / "simple_calc.sysml"


@pytest.fixture
def multi_output_sysml(sample_model_path: Path) -> Path:
    """Return path to multi_output.sysml test fixture."""
    return sample_model_path / "multi_output.sysml"


@pytest.fixture
def dependencies_sysml(sample_model_path: Path) -> Path:
    """Return path to dependencies.sysml test fixture."""
    return sample_model_path / "dependencies.sysml"


@pytest.fixture
def temp_output_dir(tmp_path: Path) -> Path:
    """Create and return a temporary output directory."""
    output_dir = tmp_path / "generated"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


@pytest.fixture
def sample_extractor(sample_model_path: Path) -> SysMLDataExtractor:
    """Create an extractor loaded with sample models."""
    from sysml_codegen.extraction.extractor import SysMLDataExtractor

    extractor = SysMLDataExtractor([sample_model_path])
    if not extractor.load_models():
        pytest.skip("Could not load sample SysML models")
    return extractor


@pytest.fixture
def generation_config(sample_model_path: Path, temp_output_dir: Path):
    """Create a GenerationConfig for testing."""
    from sysml_codegen.cli import GenerationConfig

    return GenerationConfig(
        models_path=sample_model_path,
        output_path=temp_output_dir,
        package_name="test_package",
        schema_class_name="TestParams",
        pipeline_name="test_pipeline",
        overwrite=True,
    )
