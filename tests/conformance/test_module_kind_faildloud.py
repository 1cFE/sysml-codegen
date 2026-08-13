"""Conformance tests for the module_kind seam contract (Item 6 fail-loud -> Item 7 fill-in).

Item 6 made every calc-shaped seam refuse a CONSTRAINT/REPORT_AGGREGATOR module rather than
mis-render it as a calculation. Item 7 fills in three of those seams for real (module-wrapper,
pipeline-yaml, registry) and turns the other three into clean skips (test-gen, stencil,
backlog-report) — D8. This file flips the six original refuse-assertions accordingly; the
duplicate-path check (the S4 "fourth calc-shaped seam") also now tolerates constraint kinds.
"""

from __future__ import annotations

from pathlib import Path

import jinja2
import pytest
from agentic_mbse.sysml.expression_facts import FeatureReferenceFact, OperandTypeFact
from agentic_mbse.sysml.expression_ir import (
    FeatureReferenceNode,
    OperatorNode,
    serialize_expression,
)

from sysml_codegen.contracts.model_contract import build_model_contract
from sysml_codegen.generation import CodeGenerationError
from sysml_codegen.generation.modules import compile_shared_predicates, generate_teax_module
from sysml_codegen.generation.pipeline import generate_pipeline_yaml
from sysml_codegen.generation.registry import generate_registry
from sysml_codegen.generation.stencils import generate_backlog_report
from sysml_codegen.generation.test_gen import generate_test_implementations
from sysml_codegen.resolution.models import (
    ComputationGraph,
    ConstraintCatalog,
    ConstraintCatalogEntry,
    ConstraintFormalIdentity,
    InputSource,
    ModuleInput,
    ModuleKind,
    ModuleOutput,
    PipelineModule,
)

TEMPLATE_DIR = Path(__file__).parent.parent.parent / "src" / "sysml_codegen" / "templates"


@pytest.fixture(scope="session")
def template_env():
    """Jinja2 template environment, matching test_gen_registry.py / test_gen_module_wrappers.py."""
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(TEMPLATE_DIR)),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def _ref(name: str) -> FeatureReferenceNode:
    return FeatureReferenceNode(
        reference=FeatureReferenceFact(
            source_name=name, target=None, target_types=[], chain_segments=[]
        ),
        operand_type=OperandTypeFact(category="real", enumeration=None, unit=None),
    )


def _predicate_ir() -> str:
    ir = OperatorNode(operator=">", operands=[_ref("a"), _ref("b")], operand_type=None)
    return serialize_expression(ir)


def _catalog() -> ConstraintCatalog:
    entry = ConstraintCatalogEntry(
        declaration_id="decl-C1",
        constraint_id="C1",
        usage_qualified_name="Pkg::Def::assert1",
        source_local_identity="assert1",
        source_form="definition_typed",
        owner_qualified_name="Pkg::Def",
        definition_qualified_name="Pkg::Def",
        owner_instance_path="Pkg__Def",
        membership_kind="assert",
        predicate_source_key="definition:Pkg::Def",
        is_negated=False,
        expected_value=True,
        predicate_ir=_predicate_ir(),
        evaluation_channel="c1__evaluation",
    )
    return ConstraintCatalog(concrete_entries=[entry], fingerprint="deadbeef")


def _constraint_module() -> PipelineModule:
    return PipelineModule(
        name="c1",
        module_type="pkg.C1ConstraintModule",
        inputs=[
            ModuleInput(
                param_name="a",
                python_type="float",
                source=InputSource(source_type="module_output", producer_channel="upstream__a"),
                formal_identity=ConstraintFormalIdentity(raw_name="a"),
            ),
            ModuleInput(
                param_name="b",
                python_type="float",
                source=InputSource(source_type="module_output", producer_channel="upstream__b"),
                formal_identity=ConstraintFormalIdentity(raw_name="b"),
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


def _aggregator_module() -> PipelineModule:
    return PipelineModule(
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


def _graph_with_constraint() -> ComputationGraph:
    return ComputationGraph(
        modules=[_constraint_module(), _aggregator_module()],
        entry_point_groups=[],
        execution_order=["c1", "constraint_report_aggregator"],
        constraint_catalog=_catalog(),
    )


# ---------------------------------------------------------------------------
# Render: module-wrapper, pipeline-yaml, registry
# ---------------------------------------------------------------------------


def test_module_wrapper_renders_constraint(template_env):
    catalog = _catalog()
    compiled = compile_shared_predicates(catalog)
    code = generate_teax_module(
        _constraint_module(),
        template_env=template_env,
        output_path=Path("/tmp/test_wrapper.py"),
        catalog=catalog,
        compiled_predicates=compiled,
    )
    assert "class C1ConstraintModule" in code
    assert "CONSTRAINT_ID = \"C1\"" in code
    assert "def run(self, a: float, b: float)" in code


def test_module_wrapper_renders_report_aggregator(template_env):
    catalog = _catalog()
    code = generate_teax_module(
        _aggregator_module(),
        template_env=template_env,
        output_path=Path("/tmp/test_agg.py"),
        catalog=catalog,
    )
    assert "class ConstraintReportAggregatorModule" in code
    assert 'CATALOG_FINGERPRINT = "deadbeef"' in code
    assert "C1: ConstraintEvaluation" in code


def test_module_wrapper_without_catalog_still_refuses(template_env):
    """A caller that forgets to pass the catalog gets a loud, named error — not a
    silent mis-render — distinct from Item 6's generic unrenderable-kind refusal."""
    with pytest.raises(CodeGenerationError, match="ConstraintCatalog"):
        generate_teax_module(
            _constraint_module(), template_env=template_env, output_path=Path("/tmp/x.py")
        )


def test_generate_pipeline_yaml_renders_constraint(template_env):
    yaml_text = generate_pipeline_yaml(
        _graph_with_constraint(), package_name="pkg", template_env=template_env
    )
    assert "c1__evaluation" in yaml_text
    assert "constraint_report" in yaml_text


def test_registry_seam_renders_constraint(template_env):
    code = generate_registry(
        graph=_graph_with_constraint(),
        package_name="pkg",
        template_env=template_env,
        output_path=Path("/tmp/test_registry.py"),
    )
    assert "C1ConstraintModule" in code
    assert "ConstraintReportAggregatorModule" in code
    assert "ConstraintEvaluation" in code and "ConstraintReport" in code


@pytest.mark.parametrize("renderer", ["pipeline", "registry", "model_contract"])
def test_graph_renderers_reject_constraint_module_without_catalog(renderer, template_env):
    graph = _graph_with_constraint().model_copy(update={"constraint_catalog": None})
    with pytest.raises(CodeGenerationError) as error:
        if renderer == "pipeline":
            generate_pipeline_yaml(graph, package_name="pkg", template_env=template_env)
        elif renderer == "registry":
            generate_registry(
                graph=graph,
                package_name="pkg",
                template_env=template_env,
                output_path=Path("/tmp/missing_catalog_registry.py"),
            )
        else:
            build_model_contract(graph)
    assert error.value.name_safety_violation is not None
    assert error.value.name_safety_violation.kind == "catalog_module_join"
    assert error.value.name_safety_violation.final_binding == "c1"


def test_check_duplicate_output_paths_tolerates_constraint():
    from sysml_codegen.cli import _check_duplicate_output_paths

    _check_duplicate_output_paths([_constraint_module(), _aggregator_module()])  # no raise


# ---------------------------------------------------------------------------
# Skip: test-gen, stencil, backlog-report (D8)
# ---------------------------------------------------------------------------


def test_generate_test_implementations_skips_constraint(template_env):
    content = generate_test_implementations(
        _graph_with_constraint(),
        package_name="pkg",
        template_env=template_env,
        output_path=Path("/tmp/test_gen.py"),
    )
    assert "C1" not in content
    assert "constraint_report_aggregator" not in content


def test_generate_backlog_report_skips_constraint():
    markdown = generate_backlog_report(
        _graph_with_constraint(), output_path=Path("/tmp/BACKLOG.md"), package_name="pkg"
    )
    assert "C1" not in markdown
    assert "constraint_report_aggregator" not in markdown


def test_generate_stencils_skips_constraint(tmp_path):
    """The stencil seam's skip happens at the orchestration loop (cli._generate_stencils),
    not inside the single-module `generate_implementation` (which has no rendering for a
    constraint kind by design — the loop never reaches it for one)."""
    from sysml_codegen.cli import GenerationConfig, _generate_stencils, _get_template_env

    config = GenerationConfig(output_path=tmp_path, package_name="pkg")
    (tmp_path / "handwritten").mkdir(parents=True)

    class _Ctx:
        computation_graph = _graph_with_constraint()

    _generate_stencils(_Ctx().computation_graph, config, _get_template_env())
    written = list((tmp_path / "handwritten").rglob("*.py"))
    assert written == []
