"""Conformance test configuration and fixtures.

Provides:
- Marker registration (req, baseline)
- Session-scoped extraction snapshot fixtures
- Per-model convenience fixtures
"""

from __future__ import annotations

import pytest

from tests.helpers.snapshot_loader import load_extraction_snapshot

# All models with extraction snapshots
SNAPSHOT_MODELS = [
    "sample_model",
    "solar_battery_model",
    "catf_mfe_model",
    "attr_expr_probe",
    "chain_spike_model",
    "issue22_model",
]


def pytest_configure(config):
    config.addinivalue_line("markers", "req(id): map test to requirement ID")
    config.addinivalue_line("markers", "baseline: pipeline baseline comparison test")


@pytest.fixture(scope="session")
def extraction_snapshots():
    """Load all extraction snapshots once per session."""
    return {
        name: load_extraction_snapshot(name)
        for name in SNAPSHOT_MODELS
    }


@pytest.fixture
def solar_battery_snapshot(extraction_snapshots):
    """Convenience fixture for solar_battery_model snapshot."""
    return extraction_snapshots["solar_battery_model"]


@pytest.fixture
def catf_mfe_snapshot(extraction_snapshots):
    """Convenience fixture for catf_mfe_model snapshot."""
    return extraction_snapshots["catf_mfe_model"]


@pytest.fixture
def sample_model_snapshot(extraction_snapshots):
    """Convenience fixture for sample_model snapshot."""
    return extraction_snapshots["sample_model"]


@pytest.fixture
def attr_expr_probe_snapshot(extraction_snapshots):
    """Convenience fixture for attr_expr_probe snapshot."""
    return extraction_snapshots["attr_expr_probe"]


@pytest.fixture
def chain_spike_snapshot(extraction_snapshots):
    """Convenience fixture for chain_spike_model snapshot."""
    return extraction_snapshots["chain_spike_model"]


@pytest.fixture
def issue22_snapshot(extraction_snapshots):
    """Convenience fixture for issue22_model snapshot."""
    return extraction_snapshots["issue22_model"]
