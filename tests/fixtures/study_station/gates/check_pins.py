"""The station's pinned-packages gate: the toolchain the station is studied with imports.

Written for study-layer-to-codegen. ``integrate`` runs this file as gate 1a, because the
station's ``pyproject.toml`` declares it under
``[tool.sysml-codegen.integrate.gates.pinned-packages]``. A project with pinned revisions
would compare them here. The station pins nothing, so it checks only what it declares it
checked: the generator, its model layer and teax's simkit all import.
"""

import importlib

import pytest


@pytest.mark.parametrize("module", ["sysml_codegen", "agentic_mbse", "simkit"])
def test_a_toolchain_package_imports(module):
    importlib.import_module(module)
