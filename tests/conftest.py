"""Shared pytest fixtures for sysml-codegen tests.

Provides:
- Sample SysML model loading
- Temporary directory management
- Test configuration
"""

from __future__ import annotations

import functools
from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"
REPO_ROOT = Path(__file__).resolve().parent.parent


@functools.lru_cache(maxsize=1)
def _license_available() -> bool:
    """Probe licensed syside independently of whether a particular model is valid."""
    from agentic_mbse.sysml.syside_adapter import get_syside

    try:
        get_syside()
    except ImportError:
        return False
    return True


requires_license = pytest.mark.skipif(
    not _license_available(), reason="no live syside license"
)


def instance_graph_fixture(model_name: str) -> Path:
    """Return the committed v6 instance-graph snapshot path for a fixture model.

    The v5 counterpart, ``snapshot_fixture``, resolved a committed
    ``extraction_snapshot.json``; both spellings lived here through the transition so tests
    could be repointed one at a time, and the v5 one retired with the family (retirement
    step 2). Reading a committed v6 snapshot needs no licence, which is what keeps a
    repointed conformance test in the license-free lane it was already in.
    """
    return FIXTURES_DIR / model_name / "instance_graph_snapshot.json"


def exact_graph_from_fixture(model_name: str):
    """The projected ComputationGraph of a fixture, read from its sealed v6 snapshot.

    The exact-route replacement for the retired ``build_full_graph_from_snapshot`` call.
    That call returned ``(graph, classifier_inputs)`` because the legacy rebuild exposed its
    intermediate; the exact route has no such intermediate, so this returns the graph alone
    and a caller that wanted the second element has to say what it actually needs.
    """
    from sysml_codegen.elaboration import project
    from sysml_codegen.snapshot.envelope import load_instance_graph_snapshot

    return project(load_instance_graph_snapshot(instance_graph_fixture(model_name)))
