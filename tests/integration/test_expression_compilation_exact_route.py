"""Gate 4C, row L-201: expression compilation and its stub fallback, exact route.

The responsibility this replaces belonged to
``tests/integration/test_expression_compilation_e2e.py``: a calc def whose
expressions compile becomes an auto-implementation, one whose expressions cannot
be compiled becomes a ``NotImplementedError`` stub, the backlog lists exactly the
second kind, and the compiled arithmetic is right. Its specimens were
``solar_battery_model``, ``catf_mfe_model`` and ``chain_spike_model``, all
ratified ``expected-collapse`` rows the exact route refuses.

The fixture is ``expr_compile_d5``, authored because **no fixture the exact route
accepts emits a stub** — every accepted one auto-implements completely, so the
classification claim had no specimen at any authority. ``OpaqueCalc``'s output
carries no expression, which is the smallest honest way to have nothing to
compile.

Expected values are hand-derived from the model
(``tests/fixtures/expr_compile_d5/PROVENANCE.md``), never read back.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from sysml_codegen.cli import GenerationConfig, run_codegen
from tests.conftest import FIXTURES_DIR, requires_license
from tests.helpers.impl_execution import (
    assert_outputs_match,
    execute_impl_body,
    extract_function_body,
    find_impl_files,
    is_auto_implemented,
)

pytestmark = requires_license

FIXTURE = FIXTURES_DIR / "expr_compile_d5"
PACKAGE = "expr_compile"

COMPILABLE = ["productcalc", "ratiocalc", "powercalc"]
NON_COMPILABLE = "opaquecalc"


@pytest.fixture(scope="module")
def package(tmp_path_factory) -> Path:
    output = tmp_path_factory.mktemp("expr-compile") / "out"
    assert run_codegen(
        GenerationConfig(
            models_path=FIXTURE,
            output_path=output,
            package_name=PACKAGE,
            pipeline_name="pipeline",
        )
    )
    return output


def _impl(package: Path, calc: str) -> Path:
    target = f"{calc}_impl.py"
    matches = [path for path in find_impl_files(package) if path.name == target]
    assert len(matches) == 1, f"expected exactly one {target}, found {matches}"
    return matches[0]


def test_the_classification_partitions_the_four_calc_defs(package: Path) -> None:
    """Named on both sides: three compile, one does not, and nothing else exists."""
    emitted = sorted(path.name.removesuffix("_impl.py") for path in find_impl_files(package))
    assert emitted == sorted([*COMPILABLE, NON_COMPILABLE])

    for calc in COMPILABLE:
        assert is_auto_implemented(_impl(package, calc)), f"{calc} should have compiled"
    assert not is_auto_implemented(_impl(package, NON_COMPILABLE))


def test_the_non_compilable_calc_falls_back_to_a_loud_stub(package: Path) -> None:
    """A stub raises. It does not return a plausible default."""
    text = _impl(package, NON_COMPILABLE).read_text()
    assert "raise NotImplementedError" in text
    assert "AUTO_IMPLEMENTED = True" not in text
    assert extract_function_body(_impl(package, NON_COMPILABLE)) is None


def test_the_backlog_lists_exactly_the_non_compilable_calc(package: Path) -> None:
    backlog = (package / "IMPLEMENTATION_BACKLOG.md").read_text()
    assert "**Total**: 1 functions to implement" in backlog
    assert "OpaqueCalc" in backlog
    assert "run_opaquecalc" in backlog
    for calc in ("ProductCalc", "RatioCalc", "PowerCalc"):
        assert f"| {calc} |" not in backlog, f"{calc} compiled but is in the backlog"


def test_product_arithmetic_matches_the_model(package: Path) -> None:
    """6.0 x 2.5 = 15.0 area; + 4.0 margin = 19.0 padded."""
    body = extract_function_body(_impl(package, "productcalc"))
    assert body is not None
    result = execute_impl_body(
        body,
        {"width_in": 6.0, "height_in": 2.5, "margin_in": 4.0},
        ["area", "padded_area"],
    )
    assert_outputs_match(result, {"area": 15.0, "padded_area": 19.0})


def test_ratio_arithmetic_respects_the_parenthesised_numerator(package: Path) -> None:
    """(19.0 + 5.0) / 4.0 = 6.0. Dropping the parentheses would give 20.25."""
    body = extract_function_body(_impl(package, "ratiocalc"))
    assert body is not None
    result = execute_impl_body(
        body,
        {"numerator_in": 19.0, "offset_in": 5.0, "divisor_in": 4.0},
        ["ratio"],
    )
    assert_outputs_match(result, {"ratio": 6.0})


def test_power_arithmetic_respects_operator_precedence(package: Path) -> None:
    """0.5 * 3.0 ** 2.0 = 4.5. Binding the product first would give 2.25."""
    body = extract_function_body(_impl(package, "powercalc"))
    assert body is not None
    result = execute_impl_body(
        body,
        {"scale_in": 0.5, "base_in": 3.0, "exponent_in": 2.0},
        ["scaled_power"],
    )
    assert_outputs_match(result, {"scaled_power": 4.5})


def test_the_stub_calc_still_reaches_the_pipeline(package: Path) -> None:
    """A stub is a missing body, not a missing module: the wiring must survive."""
    import yaml

    pipeline = yaml.safe_load((package / "pipelines" / "pipeline.yaml").read_text())
    opaque = pipeline["modules"]["exprcompiled5__rig__opaque"]
    assert "measurement" in opaque["inputs"]["measurement_in"]
    assert opaque["outputs"], "the stub module publishes no output channel"
