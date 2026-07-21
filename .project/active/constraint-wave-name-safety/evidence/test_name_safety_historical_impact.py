"""Baseline-only R-3 historical-impact evidence, separate from the frozen rejection overlay."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

import jinja2
import pytest
from agentic_mbse.sysml.expression_facts import FeatureReferenceFact, OperandTypeFact
from agentic_mbse.sysml.expression_ir import (
    FeatureReferenceNode,
    OperatorNode,
    serialize_expression,
)
from pydantic import BaseModel

import sysml_codegen
from sysml_codegen.generation.modules import compile_shared_predicates, render_constraint_module
from sysml_codegen.generation.predicate_compiler import compile_predicate
from sysml_codegen.resolution.models import (
    ConstraintCatalog,
    ConstraintCatalogEntry,
    InputSource,
    ModuleInput,
    ModuleKind,
    ModuleOutput,
    PipelineModule,
)

EXPECTED_HEAD = "512786c7dfab44fba7a0185d09e845b7494c702d"
TREE = Path(os.environ["EXPECTED_TREE"]).resolve()
assert Path(sysml_codegen.__file__).resolve().is_relative_to(TREE)
assert (
    subprocess.run(
        ["git", "-C", str(TREE), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    == EXPECTED_HEAD
)
TEMPLATE_DIR = Path(sysml_codegen.__file__).resolve().parent / "templates"


def _ref(name: str) -> FeatureReferenceNode:
    return FeatureReferenceNode(
        reference=FeatureReferenceFact(
            source_name=name, target=None, target_types=[], chain_segments=[]
        ),
        operand_type=OperandTypeFact(category="real", enumeration=None, unit=None),
    )


def _predicate(left: str, right: str = "limit") -> OperatorNode:
    return OperatorNode(
        operator="<=",
        operands=[_ref(left), _ref(right)],
        operand_type=None,
    )


def _load_predicate(left: str):
    source, arguments = compile_predicate(_predicate(left), "historical_predicate")
    namespace: dict[str, object] = {}
    exec(source, namespace)
    return namespace["historical_predicate"], arguments


def test_value_formal_reports_wrong_positive_margin_for_violation():
    predicate, arguments = _load_predicate("value")
    assert arguments == ["value", "limit"]
    result = predicate(value=4.0, limit=3.0)
    assert result.actual_value is False
    assert result.status == "violated"
    assert result.margin == 3.0
    assert result.margin > 0.0


def test_status_formal_reports_none_margin_for_simple_inequality():
    predicate, arguments = _load_predicate("status")
    assert arguments == ["status", "limit"]
    result = predicate(status=4.0, limit=3.0)
    assert result.actual_value is False
    assert result.status == "violated"
    assert result.margin is None


def _render_wrapper(formal_name: str) -> tuple[str, str]:
    predicate_ir = _predicate(formal_name)
    catalog = ConstraintCatalog(
        concrete_entries=[
            ConstraintCatalogEntry(
                constraint_id="C1",
                usage_qualified_name="Pkg::C1",
                owner_instance_path="Pkg",
                membership_kind="assert",
                is_negated=False,
                expected_value=True,
                predicate_ir=serialize_expression(predicate_ir),
                evaluation_channel="c1__evaluation",
            )
        ],
        fingerprint="historical-impact",
    )
    module = PipelineModule(
        name="c1",
        module_type="constraints.C1ConstraintModule",
        inputs=[
            ModuleInput(
                param_name=name,
                python_type="float",
                source=InputSource(source_type="module_output", producer_channel=f"up__{name}"),
            )
            for name in (formal_name, "limit")
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
    predicate_function_name = next(iter(compiled.values()))[0]
    template_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(TEMPLATE_DIR)),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    return (
        render_constraint_module(module, catalog, compiled, template_env, "pkg"),
        predicate_function_name,
    )


def _install_wrapper_runtime(monkeypatch, predicate_function_name: str) -> None:
    class MultiOutput(BaseModel):
        pass

    class ModuleBase:
        @classmethod
        def __class_getitem__(cls, _item):
            return cls

    class ModuleResult:
        @classmethod
        def __class_getitem__(cls, _item):
            return cls

        def __init__(self, *, data):
            self.data = data

    class ConstraintEvaluation(BaseModel):
        constraint_id: str
        actual_value: bool | None
        status: str
        margin: float | None
        observed: dict[str, float]

    modules: dict[str, ModuleType] = {}
    for name in (
        "simkit",
        "simkit.config",
        "simkit.config.schema",
        "simkit.core",
        "simkit.core.base",
        "pkg",
        "pkg.schemas",
        "pkg.schemas.constraint_types",
        "pkg.modules",
        "pkg.modules.constraints",
        "pkg.modules.constraints.predicates",
    ):
        module = ModuleType(name)
        module.__path__ = []
        modules[name] = module
        monkeypatch.setitem(sys.modules, name, module)
    modules["simkit.config.schema"].MultiOutput = MultiOutput
    modules["simkit.core.base"].ModuleBase = ModuleBase
    modules["simkit.core.base"].ModuleResult = ModuleResult
    modules["pkg.schemas.constraint_types"].ConstraintEvaluation = ConstraintEvaluation

    def predicate(*_args, **_kwargs):
        return SimpleNamespace(actual_value=False, status="violated", margin=-1.0)

    setattr(modules["pkg.modules.constraints.predicates"], predicate_function_name, predicate)


def test_verdict_formal_rebinding_raises_type_error(monkeypatch):
    source, predicate_function_name = _render_wrapper("verdict")
    _install_wrapper_runtime(monkeypatch, predicate_function_name)
    namespace: dict[str, object] = {}
    exec(source, namespace)
    module_class = namespace["C1ConstraintModule"]
    with pytest.raises(TypeError, match="float"):
        module_class().run(verdict=4.0, limit=3.0)


def test_self_formal_emits_duplicate_parameter_syntax_error():
    source, _predicate_function_name = _render_wrapper("self")
    with pytest.raises(SyntaxError, match="duplicate argument 'self'"):
        compile(source, "<generated-self-collision>", "exec")
