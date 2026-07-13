"""Live-license generation-level reproduction of the S4 slice + the compile-once fixture.

`test_constraint_generation_integration.py` proves the full generation surface offline against
a hand-built graph. This file proves the same surface against a *real* lowered graph — wi014_toy
(the S4 slice: one eligible assertion, cost <= budget) and constraint_multi_instance (three
occurrences of one definition, the compile-once fixture) — driven through the actual live
lowering path (`build_pipeline_context(..., lower_constraints_enabled=True)`), matching
`test_constraint_pipeline_threading.py`'s convention.
"""

from __future__ import annotations

import ast

from sysml_codegen.cli import (
    GenerationConfig,
    _generate_modules,
    _generate_pipeline,
    _generate_registry,
    _generate_schemas,
    _get_template_env,
    _setup_output_directories,
)
from sysml_codegen.orchestration.pipeline_builder import build_pipeline_context
from tests.conftest import FIXTURES_DIR, requires_license


class _Ctx:
    def __init__(self, ctx) -> None:
        self.computation_graph = ctx.computation_graph


@requires_license
def test_s4_slice_generation_level_reproduction(tmp_path):
    """wi014_toy: one eligible assertion (`affordable`, cost <= budget) generates a real
    constraint module + aggregator + shared predicate + evidence schemas + registry entries."""
    ctx = build_pipeline_context(
        [FIXTURES_DIR / "wi014_toy"], lower_constraints_enabled=True
    )
    assert ctx.computation_graph.constraint_catalog is not None
    assert len(ctx.computation_graph.constraint_catalog.concrete_entries) == 1

    config = GenerationConfig(output_path=tmp_path, package_name="wi014")
    _setup_output_directories(config)
    template_env = _get_template_env()
    fake_ctx = _Ctx(ctx)

    _generate_schemas(fake_ctx, config, template_env)
    _generate_modules(fake_ctx, config, template_env)
    _generate_pipeline(fake_ctx, config, template_env)
    _generate_registry(fake_ctx, config, template_env)

    assert (tmp_path / "schemas" / "constraint_types.py").exists()

    predicates = tmp_path / "modules" / "constraints" / "predicates.py"
    predicates_src = predicates.read_text()
    ast.parse(predicates_src)
    assert predicates_src.count("def constraint_pred_") == 1

    constraint_files = [
        p for p in (tmp_path / "modules" / "toy_plant").glob("*.py") if p.name != "__init__.py"
    ]
    assert len(constraint_files) == 1
    constraint_src = constraint_files[0].read_text()
    ast.parse(constraint_src)
    assert "cost" in constraint_src and "budget" in constraint_src

    aggregator_file = tmp_path / "modules" / "constraints" / "constraintreportaggregatormodule.py"
    ast.parse(aggregator_file.read_text())

    registry_src = (tmp_path / "__init__.py").read_text()
    ast.parse(registry_src)
    assert "ConstraintReportAggregatorModule" in registry_src


@requires_license
def test_two_instances_of_one_definition_generation_level_compile_once(tmp_path):
    """constraint_multi_instance: three Cell occurrences of one `nonneg` assertion share
    exactly one compiled predicate function at the generation level (INV-1), not per-instance
    inline duplication — the integration seam S4 never ran."""
    ctx = build_pipeline_context(
        [FIXTURES_DIR / "constraint_multi_instance"], lower_constraints_enabled=True
    )
    assert ctx.computation_graph.constraint_catalog is not None
    assert len(ctx.computation_graph.constraint_catalog.concrete_entries) == 3

    config = GenerationConfig(output_path=tmp_path, package_name="cmi")
    _setup_output_directories(config)
    template_env = _get_template_env()
    fake_ctx = _Ctx(ctx)

    _generate_schemas(fake_ctx, config, template_env)
    _generate_modules(fake_ctx, config, template_env)

    predicates_src = (tmp_path / "modules" / "constraints" / "predicates.py").read_text()
    ast.parse(predicates_src)
    assert predicates_src.count("def constraint_pred_") == 1  # compile-once (INV-1/D3)

    constraint_modules = [
        m for m in ctx.computation_graph.modules if m.module_kind.value == "constraint"
    ]
    assert len(constraint_modules) == 3  # class-per-assertion (three files, one function)
