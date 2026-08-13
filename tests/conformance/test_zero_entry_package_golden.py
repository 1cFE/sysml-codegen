"""SC-8: what a zero-entry, constraint-declaring package actually ships, pinned to bytes.

Item 2's audit left residual **R3**: the calc-def-only package shape had no committed byte
baseline. Item 5 closes it, and closing it needed a genuinely new mechanism rather than a row
in an existing table.

**Why a new mechanism.** Every byte gate in the tree at the time this was written compares
*two runs of the same route* — `test_exact_route_generated_package.py`,
`test_public_route_baselines.py`, `test_exact_route_whole_tree_portability.py`,
`test_v6_recapture_batch.py`. Those prove determinism: that the generator agrees with itself.
None of them proves the bytes are the *right* bytes. `tests/fixtures/baseline_outputs/` has one
reader that never regenerates anything, and `tests/fixtures/baseline_yaml/` has no reader at
all. So this is the tree's first committed-bytes gate.

**Why this fixture.** `constraint_domain_satisfy_calc_def` genuinely has the shape R3 names:
non-empty `usage_records`, empty `concrete_entries` — constraints declared, none reaching. Its
v6 snapshot is committed beside it, so this test is **license-free**.

**Note that R3's own wording is stale, and the expected bytes are the inverse of what it said.**
R3 was written inside Item 2's window, when the machinery bar was one *concrete entry*, and it
predicted this shape ships *no* `schemas/constraint_types.py`. Item 3 moved the bar to one
*authored usage* (`resolution/models.py::ships_constraint_machinery`), so a zero-entry
constraint-declaring package now **does** ship the schema, the registry imports, and an
aggregator carrying an empty denominator. That inversion is the thing worth pinning.

**Scoped to two files deliberately.** A whole-tree golden churns on every unrelated generator
change and gets abandoned within an item — which is exactly how `baseline_yaml/` was orphaned.
Two files is the smallest set that pins "what a zero-entry package ships".

The goldens are **generator-owned bytes and stay format-exempt**: never run a formatter over
them, or the gate starts failing for a reason that has nothing to do with the generator.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from sysml_codegen.cli import (
    GenerationConfig,
    _generate_entry_points,
    _generate_modules,
    _generate_pipeline,
    _generate_registry,
    _generate_schemas,
    _generate_stencils,
    _get_template_env,
    _setup_output_directories,
)
from sysml_codegen.generation.constraint_plan import build_constraint_generation_plan
from sysml_codegen.orchestration.exact_pipeline_context import (
    build_exact_pipeline_context_from_snapshot,
)
from tests.conftest import FIXTURES_DIR

FIXTURE = FIXTURES_DIR / "constraint_domain_satisfy_calc_def"
SNAPSHOT = FIXTURE / "instance_graph_snapshot.json"
GOLDEN = Path(__file__).parent / "golden" / "zero_entry_package"
PACKAGE = "zero_entry"

#: The two files that *are* the shape. Relative to the generated package root.
PINNED = (
    "schemas/constraint_types.py",
    "modules/constraints/constraintreportaggregatormodule.py",
)


@pytest.fixture(scope="module")
def generated(tmp_path_factory) -> Path:
    """Regenerate the package from the committed snapshot. License-free."""
    output = tmp_path_factory.mktemp("zero-entry") / "pkg"
    config = GenerationConfig(
        output_path=output, package_name=PACKAGE, pipeline_name="zero_entry_pipeline"
    )
    context = build_exact_pipeline_context_from_snapshot(SNAPSHOT)
    graph = context.computation_graph
    template_env = _get_template_env()
    plan = build_constraint_generation_plan(graph, template_env, config.package_name)
    _setup_output_directories(config)
    _generate_schemas(graph, config, template_env)
    _generate_modules(graph, config, template_env, plan)
    _generate_stencils(graph, config, template_env)
    _generate_pipeline(graph, config, template_env)
    _generate_registry(graph, config, template_env)
    _generate_entry_points(graph, config, template_env)
    return output


def test_the_fixture_still_has_the_shape_r3_names(generated):
    """If the fixture stopped being zero-entry, this gate would pin the wrong thing."""
    catalog = build_exact_pipeline_context_from_snapshot(SNAPSHOT).computation_graph.constraint_catalog
    assert catalog is not None
    assert catalog.usage_records, "fixture declares no constraint usages"
    assert not catalog.concrete_entries, "fixture is no longer zero-entry"


@pytest.mark.parametrize("relative", PINNED)
def test_the_zero_entry_package_ships_the_bytes_we_committed(generated, relative):
    actual = (generated / relative).read_bytes()
    expected = (GOLDEN / relative).read_bytes()
    assert actual == expected, (
        f"{relative} differs from its committed golden. If the generator changed on purpose, "
        f"re-commit the golden deliberately — do not format it."
    )


def test_the_registry_imports_the_constraint_machinery(generated):
    """The third thing the Item 3 bar turned on, asserted by name rather than by bytes."""
    registry = (generated / "__init__.py").read_text()
    assert "ConstraintEvaluation" in registry
    assert "ConstraintReport" in registry
