"""Gate 4C, row L-198: FORMULA computed attributes on the exact route.

The responsibility this replaces belonged to
``tests/integration/test_computed_attributes_e2e.py``: a FORMULA computed
attribute becomes its own auto-implemented module, an EXPOSE attribute becomes
none, and a downstream consumer wires to the computed attribute's channel rather
than to an entry point. Its repointed nodes drove ``solar_battery_model``,
``catf_mfe_model`` and ``chain_spike_model``, all of which the exact route
refuses.

Two fixtures carry it here. ``attr_expr_probe`` is a ratified corpus fixture the
exact route *accepts* (row 4, ``expected-fix``), and it owns the FORMULA and
EXPOSE classification cases. ``costed_cart_d5`` owns the downstream-wiring case,
which is what ``solar_battery_model``'s ``p_net_kw`` proved.

Every expected value is hand-derived from the model source, and each impl is
executed in isolation with its upstream value supplied, exactly as the original
did.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

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

PROBE = FIXTURES_DIR / "attr_expr_probe"
CART = FIXTURES_DIR / "costed_cart_d5"

# Hand-computed from tests/fixtures/attr_expr_probe. Chained attributes take
# their upstream value as an input, so each impl is checked on its own.
PROBE_GROUND_TRUTH = [
    ("area", {"length": 10.0, "width": 5.0}, 50.0),
    ("volume", {"length": 10.0, "width": 5.0, "height": 3.0}, 150.0),
    ("cost", {"area": 50.0, "rate": 12.0}, 600.0),
    ("marked_up_cost", {"cost": 600.0, "markup": 1.15}, 690.0),
    ("cost_density", {"cost": 600.0, "volume": 150.0}, 4.0),
    ("q_scientific", {"p_fusion": 2600.0, "p_input": 50.0}, 52.0),
    ("perimeter", {"length": 10.0, "width": 5.0}, 30.0),
    ("minor_radius", {"r_inner": 4.2, "r_outer": 4.4, "r_major": 3.0}, 1.3),
    ("p_alpha", {"p_fusion": 2600.0}, 2600.0 * 3.52 / 17.58),
]

# Pure aliases of another value (``= scale_calc.result``): no module of their own.
EXPOSE_PURE_ATTRS = ["scale_result", "half_vol", "quarter_vol"]

# A computation *over* a calc output (``= scale_calc.result * 2.0``). The legacy
# route dropped it; the exact route mints it, which is the ratified expected-fix
# on corpus row 4 (.project/completed/20260809_elaborator-breadth/diff-ledger.md).
EXPOSE_COMPUTED_ATTR = "scaled_area"


def _generate(models: Path, output: Path, package: str) -> Path:
    assert run_codegen(
        GenerationConfig(
            models_path=models,
            output_path=output,
            package_name=package,
            pipeline_name="pipeline",
        )
    ), f"the exact route must generate {models.name}"
    return output


@pytest.fixture(scope="module")
def probe_package(tmp_path_factory) -> Path:
    return _generate(PROBE, tmp_path_factory.mktemp("attr-expr") / "out", "attr_expr_probe")


@pytest.fixture(scope="module")
def cart_package(tmp_path_factory) -> Path:
    return _generate(CART, tmp_path_factory.mktemp("cart-computed") / "out", "costed_cart")


def _impl(package: Path, attribute: str) -> Path:
    target = f"{attribute}_impl.py"
    matches = [path for path in find_impl_files(package) if path.name == target]
    assert len(matches) == 1, f"expected exactly one {target}, found {matches}"
    return matches[0]


def test_every_formula_computed_attribute_becomes_an_auto_implemented_module(
    probe_package: Path,
) -> None:
    """Named, not counted: each FORMULA attribute has its own module and impl."""
    for attribute, _inputs, _expected in PROBE_GROUND_TRUTH:
        impl = _impl(probe_package, attribute)
        assert is_auto_implemented(impl), f"{attribute} fell back to a stub"
        modules = [
            path
            for path in (probe_package / "modules").rglob("*.py")
            if path.stem == attribute
        ]
        assert modules, f"{attribute} has an impl but no module wrapper"


@pytest.mark.parametrize(
    "attribute,inputs,expected",
    PROBE_GROUND_TRUTH,
    ids=[case[0] for case in PROBE_GROUND_TRUTH],
)
def test_computed_attribute_arithmetic_matches_the_model(
    probe_package: Path, attribute: str, inputs: dict, expected: float
) -> None:
    body = extract_function_body(_impl(probe_package, attribute))
    assert body is not None, f"{attribute} has no executable body"
    assert_outputs_match(execute_impl_body(body, inputs, [attribute]), {attribute: expected})


def test_a_pure_expose_attribute_mints_no_module_of_its_own(probe_package: Path) -> None:
    names = {path.name for path in find_impl_files(probe_package)}
    leaked = [attr for attr in EXPOSE_PURE_ATTRS if f"{attr}_impl.py" in names]
    assert leaked == [], f"pure EXPOSE attributes minted modules: {leaked}"


def test_a_computation_over_a_calc_output_does_mint_a_module(probe_package: Path) -> None:
    """The corpus row-4 expected-fix: ``scale_calc.result * 2.0`` is runtime behaviour.

    The legacy route dropped this attribute; keeping the drop would have been
    the regression. The arithmetic is checked too, so "a module exists" cannot
    pass on an empty stub.
    """
    impl = _impl(probe_package, EXPOSE_COMPUTED_ATTR)
    assert is_auto_implemented(impl)
    body = extract_function_body(impl)
    assert body is not None
    assert_outputs_match(
        execute_impl_body(body, {"result": 21.0}, [EXPOSE_COMPUTED_ATTR]),
        {EXPOSE_COMPUTED_ATTR: 42.0},
    )


def test_the_probe_generates_with_an_empty_backlog(probe_package: Path) -> None:
    backlog = (probe_package / "IMPLEMENTATION_BACKLOG.md").read_text()
    assert "**Total**: 0 functions to implement" in backlog


def test_a_computed_attribute_reaches_its_consumer_as_a_channel(cart_package: Path) -> None:
    """``solar_battery``'s ``p_net_kw`` claim, on the fixture the exact route accepts.

    ``throughput_units = shift_count * units_per_shift`` is a FORMULA over two
    design attributes; the calc usage that reads it must take the computed
    module's channel, not a params key of its own.
    """
    pipeline = yaml.safe_load((cart_package / "pipelines" / "pipeline.yaml").read_text())
    modules = pipeline["modules"]

    computed = modules["costedcartdesign__cart_plant__throughput_units"]
    assert set(computed["inputs"]) == {"shift_count", "units_per_shift"}
    assert all("design_params." in source for source in computed["inputs"].values())

    consumer = modules["costedcartdesign__cart_plant__annual_handling"]
    throughput = consumer["inputs"]["throughput_units_in"]
    assert throughput.endswith(
        "CostedCartDesign__cart_plant__throughput_units__throughput_units.root"
    ), throughput
    assert "params." not in throughput


def test_the_computed_attribute_and_its_consumer_arithmetic(cart_package: Path) -> None:
    """3.0 x 250.0 = 750.0 units, at 0.4 each = 300.0."""
    throughput_body = extract_function_body(_impl(cart_package, "throughput_units"))
    assert throughput_body is not None
    throughput = execute_impl_body(
        throughput_body, {"shift_count": 3.0, "units_per_shift": 250.0}, ["throughput_units"]
    )
    assert throughput["throughput_units"] == 750.0

    handling_body = extract_function_body(_impl(cart_package, "throughputcostcalc"))
    assert handling_body is not None
    handling = execute_impl_body(
        handling_body,
        {"throughput_units_in": 750.0, "handling_cost_per_unit_in": 0.4},
        ["annual_handling_cost"],
    )
    assert handling["annual_handling_cost"] == 300.0
