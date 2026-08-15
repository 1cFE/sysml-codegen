"""Gate 4C, row L-202: the ``run_codegen`` phase sequence on the exact route.

The responsibility this replaces is the tail of
``tests/integration/test_full_pipeline.py``: one call to ``run_codegen``
produces the whole directory structure, the design-parameter JSON carries the
modelled defaults as numbers, the package's ``CUSTOM_SCHEMA_TYPES`` names the
exit-point primitive, and no static ``FusionParams`` schema survives anywhere.
Its specimen was ``chain_spike_model``, corpus row 7, a ratified
``expected-collapse`` the exact route refuses with 3x ``SI_SELF_BINDING``.

``costed_cart_d5`` replaces it: it is the only new fixture that emits both a
design-parameter group and a library-parameter group, which is what makes the
JSON claim non-trivial.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from sysml_codegen.cli import GenerationConfig, run_codegen
from tests.conftest import FIXTURES_DIR, requires_license

pytestmark = requires_license

FIXTURE = FIXTURES_DIR / "costed_cart_d5"
PACKAGE = "costed_cart"

# Read out of tests/fixtures/costed_cart_d5/design.sysml, not out of the output.
EXPECTED_DESIGN_PARAMS = {
    "CostedCartDesign__cart_plant__recovery_factor": 0.1,
    "CostedCartDesign__cart_plant__shift_count": 3.0,
    "CostedCartDesign__cart_plant__units_per_shift": 250.0,
    "CostedCartDesign__cart_plant__handling_cost_per_unit": 0.4,
}


@pytest.fixture(scope="module")
def package(tmp_path_factory) -> Path:
    output = tmp_path_factory.mktemp("full-pipeline") / "generated"
    assert run_codegen(
        GenerationConfig(
            models_path=FIXTURE,
            output_path=output,
            package_name=PACKAGE,
            pipeline_name="pipeline",
        )
    )
    return output


def test_one_call_creates_the_whole_package_structure(package: Path) -> None:
    for directory in ("schemas", "modules", "handwritten", "pipelines", "inputs", "tests"):
        assert (package / directory).is_dir(), f"{directory}/ missing from the package"

    primitives = package / "primitives.py"
    assert primitives.exists()
    assert "Float = RootModel[float]" in primitives.read_text()


def test_the_design_parameter_json_carries_the_modelled_defaults(package: Path) -> None:
    """Every design attribute reaches the JSON as a number, at its modelled value."""
    payload = json.loads((package / "inputs" / "design_params.json").read_text())
    assert payload == EXPECTED_DESIGN_PARAMS

    library = json.loads((package / "inputs" / "library_params.json").read_text())
    assert all(isinstance(value, (int, float)) for value in library.values())
    # One value traced by hand: design.sysml binds the rail length.
    assert library["CostedCartDesign__cart_plant__frame_assembly__frame_rail__length"] == 4.0


def test_the_registry_names_the_exit_point_primitive(package: Path) -> None:
    init = (package / "__init__.py").read_text()
    assert "CUSTOM_SCHEMA_TYPES" in init
    assert "Float" in init
    assert f"from {PACKAGE}.primitives import" in init


def test_no_static_fusion_params_schema_survives(package: Path) -> None:
    assert not (package / f"{PACKAGE}_schemas.py").exists()
    offenders = [
        str(path.relative_to(package))
        for path in package.rglob("*.py")
        if "FusionParams" in path.read_text()
    ]
    assert offenders == []


def test_the_phase_sequence_leaves_a_sealed_package(package: Path) -> None:
    """The last phase is the seal, so a complete run ends with three contracts."""
    contracts = package / "contracts"
    for name in ("model_contract.json", "verify.py", "package_contract.json"):
        assert (contracts / name).exists(), f"contracts/{name} missing"

    from sysml_codegen.contracts.verify import verify_package

    assert verify_package(package, PACKAGE).ok
