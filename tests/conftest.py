"""Shared pytest fixtures for sysml-codegen tests.

Provides:
- Sample SysML model loading
- Temporary directory management
- Test configuration
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from sysml_codegen.extraction.extractor import SysMLDataExtractor

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def snapshot_fixture(model_name: str) -> Path:
    """Return the committed extraction-snapshot path for a fixture model.

    The promoted loader takes a snapshot path (not a fixtures-relative model
    name); this resolves ``model_name`` to
    ``tests/fixtures/<model_name>/extraction_snapshot.json`` for test call sites.
    """
    return FIXTURES_DIR / model_name / "extraction_snapshot.json"


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
