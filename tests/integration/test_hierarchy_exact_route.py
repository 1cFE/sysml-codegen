"""Gate 4C, row L-203: hierarchy aggregation on the exact route.

The responsibility this replaces is BF-3/BF-4/BF-5 in
``tests/integration/test_hierarchy_e2e.py``: aggregation wrappers carry real
inputs, their module paths are instance-scoped rather than library-scoped, and
no evaluation artefact leaks into the pipeline YAML. Its specimen is
``solar_battery_model``, corpus row 33, which the exact route refuses.

The fixture here is ``costed_cart_d5``, and the aggregation set is read from the
projected graph's ``ModuleKind.AGGREGATION`` modules — the same graph-only
identification the original used, so a renamed file cannot make the assertions
vacuous.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from sysml_codegen.cli import GenerationConfig, run_codegen
from sysml_codegen.orchestration.exact_pipeline_context import build_exact_pipeline_context
from sysml_codegen.resolution.models import ModuleKind
from tests.conftest import FIXTURES_DIR, requires_license

pytestmark = requires_license

FIXTURE = FIXTURES_DIR / "costed_cart_d5"
PACKAGE = "costed_cart"


@pytest.fixture(scope="module")
def package(tmp_path_factory) -> Path:
    output = tmp_path_factory.mktemp("hierarchy-exact") / "out"
    assert run_codegen(
        GenerationConfig(
            models_path=FIXTURE,
            output_path=output,
            package_name=PACKAGE,
            pipeline_name="pipeline",
        )
    )
    return output


@pytest.fixture(scope="module")
def aggregation_modules() -> list:
    graph = build_exact_pipeline_context([FIXTURE]).computation_graph
    modules = [
        module for module in graph.modules if module.module_kind == ModuleKind.AGGREGATION
    ]
    assert modules, "the projected graph has no aggregation modules"
    return modules


def _wrapper_files(package: Path, modules: list) -> list[Path]:
    wanted = {module.calc_def_name.lower() + ".py" for module in modules}
    found = [
        path
        for path in (package / "modules").rglob("*.py")
        if path.name != "__init__.py" and path.name in wanted
    ]
    assert found, f"no wrapper file on disk for any of {sorted(wanted)}"
    return found


def test_the_aggregation_set_is_the_six_per_child_sums(aggregation_modules) -> None:
    """Named, not counted: the arrayed children's sums are what ``sum`` produced."""
    names = sorted(module.calc_def_name for module in aggregation_modules)
    assert names == [
        "caster_capital",
        "caster_fabrication",
        "caster_material",
        "panel_capital",
        "panel_fabrication",
        "panel_material",
    ]


def test_bf3_every_aggregation_wrapper_declares_its_terms_as_inputs(
    package: Path, aggregation_modules
) -> None:
    """Each sum over a ``[4]`` child takes four inputs, not an empty Input class."""
    for wrapper in _wrapper_files(package, aggregation_modules):
        text = wrapper.read_text()
        fields = [line for line in text.splitlines() if "Field(" in line]
        assert len(fields) == 4, (
            f"{wrapper.name} declares {len(fields)} input fields, expected the "
            f"four members of the arrayed child"
        )


def test_bf4_bf5_aggregation_module_paths_are_instance_scoped(
    package: Path, aggregation_modules
) -> None:
    """The wrapper lives under the design occurrence, not under the part definition."""
    for wrapper in _wrapper_files(package, aggregation_modules):
        relative = wrapper.relative_to(package / "modules").as_posix()
        assert relative.startswith("costedcartdesign/cart_plant/deck_assembly/"), (
            f"aggregation wrapper is not instance-scoped: {relative}"
        )


def test_bf1_no_evaluation_artifact_reaches_the_pipeline_yaml(package: Path) -> None:
    yaml_files = list((package / "pipelines").glob("*.yaml"))
    assert yaml_files
    for path in yaml_files:
        text = path.read_text()
        assert "Evaluation" not in text, f"{path.name} carries an evaluation artefact"
        assert "()" not in text, f"{path.name} carries an unresolved reference call"


def test_the_aggregation_channels_reach_the_rollup_that_consumes_them(package: Path) -> None:
    """The wiring the hierarchy exists for: sums feed the assembly rollup."""
    import yaml as yaml_module

    pipeline = yaml_module.safe_load((package / "pipelines" / "pipeline.yaml").read_text())
    rollup = pipeline["modules"]["costedcartdesign__cart_plant__deck_assembly__capital_cost"]
    sources = set(rollup["inputs"].values())
    assert any("panel_capital" in source for source in sources), sources
    assert any("caster_capital" in source for source in sources), sources
    # ``misc_hardware_cost`` is an EXPOSE-pure alias, so it mints no module of
    # its own: the rollup reads the allocation calc's channel directly.
    assert any("allocation_model__total_allocation" in source for source in sources), sources
    assert not any("misc_hardware_cost" in source for source in sources), sources
