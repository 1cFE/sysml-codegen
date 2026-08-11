"""Gate 4C, row L-199: the Costed Component pattern end to end on the exact route.

The responsibility this replaces belonged to
``tests/integration/test_costed_component_e2e.py``, whose specimen is
``solar_battery_model`` — corpus row 33, a ratified ``expected-collapse`` the
exact route refuses with 24x ``SI_SELF_BINDING``. The pattern is re-authored as
``tests/fixtures/costed_cart_d5`` and driven through the shipped public entry
point, ``run_codegen``.

What is proven here, in the order the original proved it: leaf cost modules
auto-implement, the allocation usage auto-implements, every assembly emits one
aggregation module per cost attribute, the system-level usages wire to module
outputs rather than entry points, the backlog is empty, the pipeline YAML is
topologically ordered, and the arithmetic matches values derived by hand from
the model (``tests/fixtures/costed_cart_d5/PROVENANCE.md``), never read back
from the generator.

One property the original could not state is stated here: the exact route
**refuses** a rollup whose two terms read the same attribute name off different
children. That refusal is why the fixture uses named per-child aggregations,
so it is pinned rather than left as fixture folklore.
"""

from __future__ import annotations

import ast
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

FIXTURE = FIXTURES_DIR / "costed_cart_d5"
PACKAGE = "costed_cart"

# One module per leaf cost def, plus the allocation usage. Named, not counted:
# a count alone would not say which module went missing.
EXPECTED_LEAF_IMPLS = [
    "deckpanelcostcalc_impl.py",
    "castercostcalc_impl.py",
    "framerailcostcalc_impl.py",
    "crossbracecostcalc_impl.py",
]
ALLOCATION_IMPL = "allocationcostcalc_impl.py"

# Three rolled cost attributes plus the derived index, per assembly.
ROLLED_ATTRS = ["capital_cost", "raw_material_cost", "fabrication_cost", "idiot_index"]
ASSEMBLIES = ["deck_assembly", "frame_assembly", "cart_plant"]

# Hand-derived from library.sysml + design.sysml. Every factor is binary-exact,
# so these are exact, not tolerances. See the fixture's PROVENANCE.md.
LEAF_GROUND_TRUTH = [
    (
        "deckpanelcostcalc",
        {"area_in": 2.5, "cost_per_area_in": 12.0, "fab_factor_in": 0.5},
        {"material_cost": 30.0, "fab_cost": 15.0, "total_cost": 45.0, "idiot_index": 1.5},
    ),
    (
        "castercostcalc",
        {"load_rating_in": 80.0, "cost_per_kg_in": 0.75, "fab_factor_in": 0.5},
        {"material_cost": 60.0, "fab_cost": 30.0, "total_cost": 90.0, "idiot_index": 1.5},
    ),
    (
        "framerailcostcalc",
        {"length_in": 4.0, "cost_per_m_in": 25.0, "fab_factor_in": 0.5},
        {"material_cost": 100.0, "fab_cost": 50.0, "total_cost": 150.0, "idiot_index": 1.5},
    ),
    (
        "crossbracecostcalc",
        {"brace_count_in": 6.0, "cost_per_brace_in": 5.0, "fab_factor_in": 0.5},
        {"material_cost": 30.0, "fab_cost": 15.0, "total_cost": 45.0, "idiot_index": 1.5},
    ),
]

ALLOCATION_GROUND_TRUTH = (
    {
        "child_count_in": 20.0,
        "total_child_mass_in": 50.0,
        "fastener_cost_per_child_in": 0.5,
        "wiring_cost_per_kg_in": 2.0,
        "material_share_in": 0.8,
    },
    {
        "fastener_cost": 10.0,
        "wiring_cost": 100.0,
        "total_allocation": 110.0,
        "material_portion": 88.0,
    },
)

# The rollups, evaluated at the leaf values above.
#   deck   capital = 4x45 + 4x90 + 110 = 650, raw = 4x30 + 4x60 + 88 = 448
#   frame  capital = 150 + 45 = 195,          raw = 100 + 30 = 130
#   plant  capital = 650 + 195 = 845,         raw = 448 + 130 = 578
IDIOT_INDEX_GROUND_TRUTH = [
    ("deck_assembly", {"capital_cost": 650.0, "raw_material_cost": 448.0}, 650.0 / 448.0),
    ("frame_assembly", {"capital_cost": 195.0, "raw_material_cost": 130.0}, 1.5),
    ("cart_plant", {"capital_cost": 845.0, "raw_material_cost": 578.0}, 845.0 / 578.0),
]


@pytest.fixture(scope="module")
def package(tmp_path_factory) -> Path:
    output = tmp_path_factory.mktemp("costed-cart") / "out"
    assert run_codegen(
        GenerationConfig(
            models_path=FIXTURE,
            output_path=output,
            package_name=PACKAGE,
            pipeline_name="pipeline",
        )
    ), "the exact route must generate costed_cart_d5"
    return output


def _impl(package: Path, filename: str) -> Path:
    matches = [path for path in find_impl_files(package) if path.name == filename]
    assert len(matches) == 1, f"expected exactly one {filename}, found {matches}"
    return matches[0]


def _run_impl(package: Path, filename: str, inputs: dict, outputs: list[str]) -> dict:
    impl = _impl(package, filename)
    assert is_auto_implemented(impl), f"{filename} must be auto-implemented"
    body = extract_function_body(impl)
    assert body is not None, f"{filename} has no executable body"
    return execute_impl_body(body, inputs, outputs)


def _tuple_order(package: Path, calc: str) -> list[str]:
    """The names the generated module unpacks its impl's return tuple into.

    A multi-output impl returns a bare tuple, so a value can only be read back
    under a name by using the package's own unpacking. Taking the order from
    the module — not from the impl — means the arithmetic assertions also prove
    the module and its impl agree about which slot is which.
    """
    module = next(
        path
        for path in (package / "modules").rglob("*.py")
        if path.stem == calc
    )
    line = next(
        text
        for text in module.read_text().splitlines()
        if f"= run_{calc}(" in text
    )
    return [name.strip() for name in line.split("=", 1)[0].split(",")]


def test_every_leaf_cost_model_and_the_allocation_usage_auto_implement(package: Path) -> None:
    names = {path.name for path in find_impl_files(package)}
    missing = [name for name in [*EXPECTED_LEAF_IMPLS, ALLOCATION_IMPL] if name not in names]
    assert missing == [], f"cost modules missing from the package: {missing}"
    for name in [*EXPECTED_LEAF_IMPLS, ALLOCATION_IMPL]:
        assert is_auto_implemented(_impl(package, name)), f"{name} fell back to a stub"


def test_each_assembly_emits_one_aggregation_module_per_cost_attribute(package: Path) -> None:
    """Three assemblies x four attributes, each with an auto-implemented module."""
    for assembly in ASSEMBLIES:
        for attribute in ROLLED_ATTRS:
            module = package / "modules" / "costedcartlibrary" / assembly / f"{attribute}.py"
            assert module.exists(), f"no aggregation module for {assembly}/{attribute}"
            impl = (
                package / "handwritten" / "costedcartlibrary" / assembly / f"{attribute}_impl.py"
            )
            assert impl.exists(), f"no aggregation impl for {assembly}/{attribute}"
            assert is_auto_implemented(impl), f"{assembly}/{attribute} fell back to a stub"


def test_the_per_child_sums_are_instance_scoped_modules(package: Path) -> None:
    """The arrayed children's sums live under the design occurrence, one per child role."""
    scoped = package / "modules" / "costedcartdesign" / "cart_plant" / "deck_assembly"
    emitted = sorted(path.stem for path in scoped.glob("*.py") if path.stem != "__init__")
    assert emitted == [
        "caster_capital",
        "caster_fabrication",
        "caster_material",
        "panel_capital",
        "panel_fabrication",
        "panel_material",
    ]


def test_the_system_level_usages_wire_to_module_outputs_not_entry_points(package: Path) -> None:
    """FR-5's subject: the rolled-up capital cost and the computed throughput are channels."""
    pipeline = yaml.safe_load((package / "pipelines" / "pipeline.yaml").read_text())
    modules = pipeline["modules"]

    financial = modules["costedcartdesign__cart_plant__annualized_financial"]
    total_capex = financial["inputs"]["total_capex_in"]
    assert "CostedCartDesign__cart_plant__capital_cost__capital_cost" in total_capex
    assert "params." not in total_capex, f"total_capex_in reads a params key: {total_capex}"

    handling = modules["costedcartdesign__cart_plant__annual_handling"]
    throughput = handling["inputs"]["throughput_units_in"]
    assert "CostedCartDesign__cart_plant__throughput_units__throughput_units" in throughput
    assert "params." not in throughput, f"throughput_units_in reads a params key: {throughput}"


def test_the_backlog_is_empty(package: Path) -> None:
    backlog = (package / "IMPLEMENTATION_BACKLOG.md").read_text()
    assert "**Total**: 0 functions to implement" in backlog


def test_the_pipeline_yaml_orders_producers_before_consumers(package: Path) -> None:
    """Leaf costs -> per-child sums -> assembly rollups -> plant rollup -> system usages."""
    pipeline = yaml.safe_load((package / "pipelines" / "pipeline.yaml").read_text())
    keys = list(pipeline["modules"])

    def position(name: str) -> int:
        for index, key in enumerate(keys):
            if key == name:
                return index
        raise AssertionError(f"module {name!r} not in the pipeline")

    chain = [
        "costedcartdesign__cart_plant__deck_assembly__deck_panel[0]__cost_model",
        "costedcartdesign__cart_plant__deck_assembly__panel_capital",
        "costedcartdesign__cart_plant__deck_assembly__capital_cost",
        "costedcartdesign__cart_plant__capital_cost",
        "costedcartdesign__cart_plant__annualized_financial",
    ]
    positions = [position(name) for name in chain]
    assert positions == sorted(positions), (
        f"the producer chain is out of topological order: {list(zip(chain, positions))}"
    )


def test_every_generated_file_is_valid_python(package: Path) -> None:
    """Including the params schema, which this fixture's ``[4]`` children index.

    When this module was authored the schema was a ``SyntaxError``: a modelled
    multiplicity mints ``…__caster[0]__load_rating`` and that key was written
    straight into a class body. The S3 fix sanitizes the field name and keeps the
    key as its alias. The whole-package check stays here as the local guard; the
    subject itself is owned by
    ``tests/conformance/test_generated_schema_importable.py``.
    """
    for path in sorted(package.rglob("*.py")):
        ast.parse(path.read_text(), filename=str(path))


@pytest.mark.parametrize(
    "calc,inputs,expected",
    LEAF_GROUND_TRUTH,
    ids=[case[0] for case in LEAF_GROUND_TRUTH],
)
def test_leaf_cost_arithmetic_matches_the_model(
    package: Path, calc: str, inputs: dict, expected: dict
) -> None:
    order = _tuple_order(package, calc)
    assert sorted(order) == sorted(expected), (
        f"{calc} publishes {sorted(order)}, the model declares {sorted(expected)}"
    )
    result = _run_impl(package, f"{calc}_impl.py", inputs, order)
    assert_outputs_match(result, expected)


def test_allocation_arithmetic_matches_the_model(package: Path) -> None:
    inputs, expected = ALLOCATION_GROUND_TRUTH
    order = _tuple_order(package, "allocationcostcalc")
    assert sorted(order) == sorted(expected)
    result = _run_impl(package, ALLOCATION_IMPL, inputs, order)
    assert_outputs_match(result, expected)


@pytest.mark.parametrize(
    "assembly,inputs,expected",
    IDIOT_INDEX_GROUND_TRUTH,
    ids=[case[0] for case in IDIOT_INDEX_GROUND_TRUTH],
)
def test_idiot_index_aggregation_arithmetic(
    package: Path, assembly: str, inputs: dict, expected: float
) -> None:
    impl = package / "handwritten" / "costedcartlibrary" / assembly / "idiot_index_impl.py"
    body = extract_function_body(impl)
    assert body is not None
    result = execute_impl_body(body, inputs, ["idiot_index"])
    assert_outputs_match(result, {"idiot_index": expected})


def test_the_deck_rollup_sums_its_four_panels_and_the_allocation(package: Path) -> None:
    """The rollup itself, at the values the leaves produce: 4x45 + 4x90 + 110 = 650."""
    panel = _run_impl(
        package,
        "panel_capital_impl.py",
        {f"capital_cost_{index}": 45.0 for index in range(4)},
        ["panel_capital"],
    )
    caster = _run_impl(
        package,
        "caster_capital_impl.py",
        {f"capital_cost_{index}": 90.0 for index in range(4)},
        ["caster_capital"],
    )
    assert panel["panel_capital"] == 180.0
    assert caster["caster_capital"] == 360.0

    rollup = extract_function_body(
        package / "handwritten" / "costedcartlibrary" / "deck_assembly" / "capital_cost_impl.py"
    )
    assert rollup is not None
    total = execute_impl_body(
        rollup,
        {"panel_capital": 180.0, "caster_capital": 360.0, "misc_hardware_cost": 110.0},
        ["capital_cost"],
    )
    assert total["capital_cost"] == 650.0


def test_a_two_term_same_name_rollup_is_refused(tmp_path: Path) -> None:
    """The constraint that shaped the fixture, pinned as public behaviour.

    Two rollup terms reading the same attribute name off different children both
    render the parameter ``capital_cost`` — the exact route names an expression
    parameter after the reference's last member and drops the qualifier — so the
    projection refuses the model rather than silently dropping a term.
    """
    source = tmp_path / "model.sysml"
    source.write_text(
        "package TwoTermRollup {\n"
        "    private import ScalarValues::*;\n"
        "    private import NumericalFunctions::sum;\n"
        "    abstract part def 'Costed' { attribute capital_cost : Real; }\n"
        "    calc def LeafCalc { in x_in : Real; out attribute total : Real = x_in * 2.0; }\n"
        "    part def 'PanelX' :> 'Costed' {\n"
        "        attribute x : Real;\n"
        "        calc cm : LeafCalc { in x_in = x; }\n"
        "        :>> capital_cost = cm.total;\n"
        "    }\n"
        "    part def 'CasterX' :> 'Costed' {\n"
        "        attribute x : Real;\n"
        "        calc cm : LeafCalc { in x_in = x; }\n"
        "        :>> capital_cost = cm.total;\n"
        "    }\n"
        "    part def 'AsmX' :> 'Costed' {\n"
        "        part panel : 'PanelX' [2];\n"
        "        part caster : 'CasterX' [2];\n"
        "        :>> capital_cost = sum(panel.capital_cost) + sum(caster.capital_cost);\n"
        "    }\n"
        "    part asm : 'AsmX' { :>> panel.x = 1.0; :>> caster.x = 3.0; }\n"
        "}\n"
    )

    from sysml_codegen.generation import CodeGenerationError
    from sysml_codegen.orchestration.exact_pipeline_context import build_exact_pipeline_context

    with pytest.raises(CodeGenerationError) as refusal:
        build_exact_pipeline_context([tmp_path])
    assert "SI_RENDERING_COLLISION" in str(refusal.value)
    assert "capital_cost_0" in str(refusal.value)

    # The same model refused through the public surface, without a half-written tree.
    output = tmp_path / "out"
    assert run_codegen(
        GenerationConfig(models_path=tmp_path, output_path=output, package_name="two_term")
    ) is False
    assert not output.exists(), "a refused model must leave no output tree"


def test_the_fixture_is_not_a_corpus_fixture() -> None:
    """It joins no ledger: the 37-path corpus run must not see it."""
    ledger = (
        Path(__file__).resolve().parents[2]
        / ".project/completed/20260809_elaborator-breadth/diff-ledger.md"
    )
    assert "costed_cart_d5" not in ledger.read_text()
