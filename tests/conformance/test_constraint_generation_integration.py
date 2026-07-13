"""Offline, license-free integration test for Item 7's full constraint generation surface.

Drives every `cli._generate_*` step against a hand-built ComputationGraph carrying a
CONSTRAINT + REPORT_AGGREGATOR module and a real ConstraintCatalog — the same functions
`run_codegen` calls, in the same order, writing to a real tmp output tree. Each `cli._generate_*`
function only reads `ctx.computation_graph`, so a minimal stand-in context is sufficient; no
live SysIDE model or syside license is needed (contrast the `@requires_license`
`test_constraint_pipeline_threading.py`, which exercises the live lowering path this test
starts downstream of).

Every generated Python artifact is parsed with `ast.parse` (no `simkit` import needed — that
package is execution-lane only, per [[teax-simkit-execution-env]]) to catch real syntax bugs
the isolated unit tests in `test_constraint_emission.py` / `test_module_kind_faildloud.py`
render in memory but never write to disk together.
"""

from __future__ import annotations

import ast

from agentic_mbse.sysml.expression_facts import FeatureReferenceFact, OperandTypeFact
from agentic_mbse.sysml.expression_ir import (
    FeatureReferenceNode,
    OperatorNode,
    serialize_expression,
)

from sysml_codegen.cli import (
    GenerationConfig,
    _generate_backlog,
    _generate_entry_points,
    _generate_modules,
    _generate_pipeline,
    _generate_registry,
    _generate_schemas,
    _generate_stencils,
    _generate_tests,
    _get_template_env,
    _setup_output_directories,
)
from sysml_codegen.resolution.models import (
    ComputationGraph,
    ConstraintCatalog,
    ConstraintCatalogEntry,
    InputSource,
    ModuleInput,
    ModuleKind,
    ModuleOutput,
    PipelineModule,
)


def _ref(name: str) -> FeatureReferenceNode:
    return FeatureReferenceNode(
        reference=FeatureReferenceFact(
            source_name=name, target=None, target_types=[], chain_segments=[]
        ),
        operand_type=OperandTypeFact(category="real", enumeration=None, unit=None),
    )


def _predicate_ir() -> str:
    ir = OperatorNode(operator="<=", operands=[_ref("cost"), _ref("budget")], operand_type=None)
    return serialize_expression(ir)


def _graph() -> ComputationGraph:
    constraint_module = PipelineModule(
        name="c1",
        module_type="toy_plant.DemoPlantAffordableConstraintModule",
        inputs=[
            ModuleInput(
                param_name="cost",
                python_type="float",
                source=InputSource(source_type="module_output", producer_channel="plant__cost"),
            ),
            ModuleInput(
                param_name="budget",
                python_type="float",
                source=InputSource(source_type="module_output", producer_channel="plant__budget"),
            ),
        ],
        outputs=[
            ModuleOutput(
                field_name="evaluation",
                python_type="ConstraintEvaluation",
                channel_name="c1__evaluation",
            )
        ],
        execution_order=0,
        module_kind=ModuleKind.CONSTRAINT,
    )
    aggregator_module = PipelineModule(
        name="constraint_report_aggregator",
        module_type="constraints.ConstraintReportAggregatorModule",
        inputs=[
            ModuleInput(
                param_name="C1",
                python_type="ConstraintEvaluation",
                source=InputSource(source_type="module_output", producer_channel="c1__evaluation"),
            )
        ],
        outputs=[
            ModuleOutput(
                field_name="constraint_report",
                python_type="ConstraintReport",
                channel_name="constraint_report",
            )
        ],
        execution_order=1,
        module_kind=ModuleKind.REPORT_AGGREGATOR,
    )
    catalog = ConstraintCatalog(
        concrete_entries=[
            ConstraintCatalogEntry(
                constraint_id="C1",
                usage_qualified_name="ToyPlant::DemoPlant::affordable",
                owner_instance_path="ToyPlant__DemoPlant",
                membership_kind="assert",
                is_negated=False,
                expected_value=True,
                predicate_ir=_predicate_ir(),
                evaluation_channel="c1__evaluation",
            )
        ],
        fingerprint="abc123",
    )
    return ComputationGraph(
        modules=[constraint_module, aggregator_module],
        entry_point_groups=[],
        execution_order=["c1", "constraint_report_aggregator"],
        constraint_catalog=catalog,
    )


class _Ctx:
    def __init__(self, graph: ComputationGraph) -> None:
        self.computation_graph = graph


def test_full_constraint_surface_generates_and_parses(tmp_path):
    config = GenerationConfig(output_path=tmp_path, package_name="toypkg")
    _setup_output_directories(config)
    template_env = _get_template_env()
    ctx = _Ctx(_graph())

    _generate_schemas(ctx, config, template_env)
    _generate_modules(ctx, config, template_env)
    _generate_stencils(ctx, config, template_env)
    _generate_pipeline(ctx, config, template_env)
    _generate_registry(ctx, config, template_env)
    _generate_entry_points(ctx, config, template_env)
    _generate_backlog(ctx, config)
    _generate_tests(ctx, config, template_env)

    # Constraint evidence schemas (D4).
    constraint_types = tmp_path / "schemas" / "constraint_types.py"
    assert constraint_types.exists()
    ast.parse(constraint_types.read_text())

    # Shared predicates module (D3) — compile-once.
    predicates = tmp_path / "modules" / "constraints" / "predicates.py"
    assert predicates.exists()
    predicates_src = predicates.read_text()
    ast.parse(predicates_src)
    assert predicates_src.count("def constraint_pred_") == 1

    # Constraint module (D9 naming) + aggregator (D5/D11).
    constraint_files = [
        p for p in (tmp_path / "modules" / "toy_plant").glob("*.py") if p.name != "__init__.py"
    ]
    assert len(constraint_files) == 1
    constraint_src = constraint_files[0].read_text()
    ast.parse(constraint_src)
    assert "class DemoPlantAffordableConstraintModule" in constraint_src

    aggregator_file = tmp_path / "modules" / "constraints" / "constraintreportaggregatormodule.py"
    assert aggregator_file.exists()
    aggregator_src = aggregator_file.read_text()
    ast.parse(aggregator_src)
    assert 'CATALOG_FINGERPRINT = "abc123"' in aggregator_src
    assert "C1: ConstraintEvaluation" in aggregator_src

    # No stencil/test/backlog entries for constraint kinds (D8).
    handwritten_files = [
        p for p in (tmp_path / "handwritten").rglob("*.py") if p.name != "__init__.py"
    ]
    assert handwritten_files == []
    backlog = (tmp_path / "IMPLEMENTATION_BACKLOG.md").read_text()
    assert "C1" not in backlog
    runnable_tests = (tmp_path / "tests" / "test_implementations_runnable.py").read_text()
    assert "C1" not in runnable_tests

    # Pipeline YAML renders both modules (D7 reuse).
    pipeline_yaml = (tmp_path / "pipelines" / "pipeline.yaml").read_text()
    assert "c1__evaluation" in pipeline_yaml
    assert "constraint_report" in pipeline_yaml

    # Registry: 4th partition + constraint schema imports.
    registry_src = (tmp_path / "__init__.py").read_text()
    ast.parse(registry_src)
    assert "DemoPlantAffordableConstraintModule" in registry_src
    assert "ConstraintReportAggregatorModule" in registry_src
    assert "ConstraintEvaluation" in registry_src and "ConstraintReport" in registry_src
