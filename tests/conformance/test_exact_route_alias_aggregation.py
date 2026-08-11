"""Gate 4C, row L-099: alias-aggregation generation on the exact route.

The responsibility this replaces belonged to
``tests/conformance/test_alias_agg_probe_generation.py``: a model whose calc defs
carry **quoted** names generates a package in which every file parses and every
derived identifier — module type, class name, file path — is quote- and
space-free, with an aggregation read both directly and through a chain alias.
Its specimens were ``alias_agg_probe`` and ``issue22_model``, corpus rows 3 and
20, both ratified ``expected-collapse`` (``SI_SELF_BINDING``).

``alias_agg_d5`` is ``alias_agg_probe`` with one edit — the leaf's cost model
binds ``in base_cost_in = base_cost`` — so the quoted names, the ``[3]`` widget
array, the aggregation, the chain alias, and the two consuming calc usages are
the probe's.

The arithmetic is checked as well as the identifiers: ``base_cost = 50.0`` at the
default ``markup_in = 1.5`` gives 75.0 per widget, 225.0 summed, and a margin of
33.75 at 15%.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest
import yaml

from sysml_codegen.cli import GenerationConfig, run_codegen
from sysml_codegen.orchestration.exact_pipeline_context import build_exact_pipeline_context
from tests.conftest import FIXTURES_DIR, requires_license
from tests.helpers.impl_execution import (
    assert_outputs_match,
    execute_impl_body,
    extract_function_body,
    find_impl_files,
)

pytestmark = requires_license

FIXTURE = FIXTURES_DIR / "alias_agg_d5"
PACKAGE = "alias_agg"


@pytest.fixture(scope="module")
def package(tmp_path_factory) -> Path:
    output = tmp_path_factory.mktemp("alias-agg") / "out"
    assert run_codegen(
        GenerationConfig(
            models_path=FIXTURE,
            output_path=output,
            package_name=PACKAGE,
            pipeline_name="pipeline",
        )
    ), "the exact route must generate alias_agg_d5"
    return output


def test_the_fixture_really_does_carry_quoted_calc_def_names() -> None:
    """Guard the premise: if the quotes went away the rest asserts nothing."""
    source = (FIXTURE / "model.sysml").read_text()
    for name in ("'Unit Cost Calc'", "'Margin Calc'", "'Report Calc'"):
        assert f"calc def {name}" in source


def test_every_generated_file_parses(package: Path) -> None:
    """No ``'margin calc'.py`` and no ``class 'Margin Calc'Module`` reaches disk.

    The ``[3]`` widget array also indexes its params keys, which used to make the
    schema a ``SyntaxError``; the S3 fix sanitizes the field name and keeps the
    key as the field's alias, so the whole package parses.
    """
    files = [path for path in package.rglob("*.py") if path.is_file()]
    assert files, "generation produced no Python files"
    for path in files:
        try:
            ast.parse(path.read_text())
        except SyntaxError as error:  # pragma: no cover - failure path
            pytest.fail(f"generated file {path.relative_to(package)} does not parse: {error}")


def test_every_derived_identifier_is_quote_and_space_free(package: Path) -> None:
    """Checked on the graph and on disk, because they derive names separately."""
    graph = build_exact_pipeline_context([FIXTURE]).computation_graph
    for module in graph.modules:
        assert all(segment.isidentifier() for segment in module.module_type.split(".")), (
            f"module_type {module.module_type!r} leaks a quoted identifier"
        )

    for path in package.rglob("*.py"):
        assert path.stem.isidentifier(), f"file name {path.name!r} leaks a quoted identifier"
        for part in path.relative_to(package).parts[:-1]:
            assert part.isidentifier(), f"directory {part!r} leaks a quoted identifier"


def test_the_aggregation_and_its_chain_alias_both_reach_a_consumer(package: Path) -> None:
    """One aggregation, two readers: one direct, one through ``reported_cost``."""
    pipeline = yaml.safe_load((package / "pipelines" / "pipeline.yaml").read_text())
    modules = pipeline["modules"]

    aggregation = next(key for key in modules if key.endswith("__total_cost"))
    channel = modules[aggregation]["outputs"]["root"]

    margin = next(key for key in modules if key.endswith("__margin_calc"))
    report = next(key for key in modules if key.endswith("__report_calc"))

    assert channel.split()[-1] in modules[margin]["inputs"]["cost_basis"]
    assert channel.split()[-1] in modules[report]["inputs"]["cost_input"], (
        "the chain alias did not resolve back to the aggregation's channel"
    )


def test_the_aggregation_sums_all_three_widgets(package: Path) -> None:
    impl = next(path for path in find_impl_files(package) if path.name == "total_cost_impl.py")
    body = extract_function_body(impl)
    assert body is not None
    result = execute_impl_body(
        body,
        {"total_cost_0": 75.0, "total_cost_1": 75.0, "total_cost_2": 75.0},
        ["total_cost"],
    )
    assert_outputs_match(result, {"total_cost": 225.0})


def test_the_quoted_calc_defs_compute_what_the_model_says(package: Path) -> None:
    """50.0 x 1.5 = 75.0 per widget; 225.0 x 0.15 = 33.75 margin; report passes through."""
    cases = [
        ("unit_cost_calc_impl.py", {"base_cost_in": 50.0, "markup_in": 1.5}, "unit_cost", 75.0),
        ("margin_calc_impl.py", {"cost_basis": 225.0, "margin_rate": 0.15}, "margin", 33.75),
        ("report_calc_impl.py", {"cost_input": 225.0}, "report_value", 225.0),
    ]
    for filename, inputs, output, expected in cases:
        impl = next(path for path in find_impl_files(package) if path.name == filename)
        body = extract_function_body(impl)
        assert body is not None, f"{filename} has no executable body"
        assert_outputs_match(execute_impl_body(body, inputs, [output]), {output: expected})


def test_the_package_generates_with_an_empty_backlog(package: Path) -> None:
    """The original's first property: generation completes, with nothing deferred."""
    assert "**Total**: 0 functions to implement" in (
        package / "IMPLEMENTATION_BACKLOG.md"
    ).read_text()
