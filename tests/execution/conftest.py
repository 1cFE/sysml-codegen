"""Bind the selected real-TEAx lane to its immutable execution provenance."""

from __future__ import annotations

import os
import sys

import pytest

from tests.execution.environment_pins import load_execution_provenance
from tests.helpers.teax_discovery import discover_teax_simkit


@pytest.fixture(scope="session", autouse=True)
def execution_provenance():
    """Load the manifest only when an execution test is actually selected."""
    provenance = load_execution_provenance(os.environ)
    simkit = discover_teax_simkit(
        os.environ, expected_root=provenance.teax_simkit_root
    )
    for root in (provenance.codegen_source_root, simkit):
        if str(root) not in sys.path:
            sys.path.insert(0, str(root))
    return provenance
