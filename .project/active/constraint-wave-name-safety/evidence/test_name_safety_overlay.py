"""Baseline-compatible R-3 rejection overlay used in detached worktrees."""

from __future__ import annotations

from pathlib import Path
import os
import subprocess

import jinja2
import pytest
import sysml_codegen
from agentic_mbse.sysml.expression_facts import (
    FeatureReferenceFact,
    IdentityFact,
    OperandTypeFact,
)
from agentic_mbse.sysml.expression_ir import (
    FeatureReferenceNode,
    OperatorNode,
    serialize_expression,
)

from sysml_codegen.generation import CodeGenerationError
from sysml_codegen.generation.modules import compile_shared_predicates, render_constraint_module
from sysml_codegen.generation.predicate_compiler import PredicateCompileError, compile_predicate
from sysml_codegen.resolution.models import (
    ConstraintCatalog,
    ConstraintCatalogEntry,
    InputSource,
    ModuleInput,
    ModuleKind,
    ModuleOutput,
    PipelineModule,
)

TREE = Path(os.environ["EXPECTED_TREE"]).resolve()
assert Path(sysml_codegen.__file__).resolve().is_relative_to(TREE)
assert (
    subprocess.run(
        ["git", "-C", str(TREE), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    == "512786c7dfab44fba7a0185d09e845b7494c702d"
)
TEMPLATE_DIR = Path(sysml_codegen.__file__).resolve().parent / "templates"


def _ref(name: str, qn: str | None = None) -> FeatureReferenceNode:
    target = IdentityFact(kind="Feature", name=name, qualified_name=qn) if qn else None
    return FeatureReferenceNode(
        reference=FeatureReferenceFact(
            source_name=name, target=target, target_types=[], chain_segments=[]
        ),
        operand_type=OperandTypeFact(category="real", enumeration=None, unit=None),
    )


def _predicate(left: str, right: str = "limit", *, left_qn=None, right_qn=None) -> OperatorNode:
    return OperatorNode(
        operator="<=",
        operands=[_ref(left, left_qn), _ref(right, right_qn)],
        operand_type=None,
    )


def _template_env() -> jinja2.Environment:
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(TEMPLATE_DIR)),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def _render_wrapper(predicate_name: str, wrapper_name: str, qn: str | None = None) -> None:
    ir = _predicate(predicate_name, left_qn=qn)
    catalog = ConstraintCatalog(
        concrete_entries=[
            ConstraintCatalogEntry(
                constraint_id="C1",
                usage_qualified_name="Pkg::C1",
                owner_instance_path="Pkg",
                membership_kind="assert",
                is_negated=False,
                expected_value=True,
                predicate_ir=serialize_expression(ir),
                evaluation_channel="c1__evaluation",
            )
        ],
        fingerprint="overlay",
    )
    module = PipelineModule(
        name="c1",
        module_type="constraints.C1ConstraintModule",
        inputs=[
            ModuleInput(
                param_name=name,
                python_type="float",
                source=InputSource(source_type="module_output", producer_channel=f"up__{name}"),
                formal_identity={
                    "raw_name": predicate_name if name == wrapper_name else name,
                    "qualified_name": qn if name == wrapper_name else None,
                },
            )
            for name in (wrapper_name, "limit")
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
    compiled = compile_shared_predicates(catalog)
    render_constraint_module(module, catalog, compiled, _template_env(), "pkg")


@pytest.mark.parametrize("name", ["value", "status"])
def test_predicate_reserved_name_rejected(name):
    with pytest.raises(PredicateCompileError) as error:
        compile_predicate(_predicate(name), "overlay_predicate")
    assert error.value.name_safety_violation.final_binding == name


@pytest.mark.parametrize("name", ["self", "verdict"])
def test_wrapper_reserved_name_rejected(name):
    with pytest.raises(CodeGenerationError) as error:
        _render_wrapper(name, name)
    assert error.value.name_safety_violation.final_binding == name


def test_predicate_identity_collapse_rejected():
    ir = OperatorNode(
        operator="<=",
        operands=[_ref("x", "A::x"), _ref("x", "B::x")],
        operand_type=None,
    )
    with pytest.raises(PredicateCompileError) as error:
        compile_predicate(ir, "overlay_predicate")
    assert error.value.name_safety_violation.kind == "binding_identity_collision"


def test_wrapper_identity_collapse_rejected():
    with pytest.raises(CodeGenerationError) as error:
        _render_wrapper("safe_name", "self", "Pkg::safe_name")
    assert error.value.name_safety_violation is not None


def test_cross_path_disagreement_rejected():
    with pytest.raises(CodeGenerationError) as error:
        _render_wrapper("raw_name", "other_name", "Pkg::formal")
    assert error.value.name_safety_violation.kind == "cross_scope_binding_disagreement"
