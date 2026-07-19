"""Frozen cross-revision probes for GAP-CLOSE Item 1.

This file deliberately imports only production seams present at the pinned baseline. It is
copied byte-for-byte into detached baseline and candidate worktrees.
"""

from __future__ import annotations

import hashlib
import inspect
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace

import pytest
from agentic_mbse.sysml.constraint_facts import ConstraintFacts
from agentic_mbse.sysml.expression_facts import (
    FeatureReferenceFact,
    LiteralFact,
    OperandTypeFact,
)
from agentic_mbse.sysml.expression_ir import (
    FeatureReferenceNode,
    LiteralNode,
    OperatorNode,
    serialize_expression,
)

import sysml_codegen
import sysml_codegen.generation.modules as generation_modules
from sysml_codegen.cli import GenerationConfig, run_codegen
from sysml_codegen.generation import CodeGenerationError
from sysml_codegen.generation.constraint_catalog import assemble_constraint_catalog
from sysml_codegen.generation.modules import compile_shared_predicates
from sysml_codegen.generation.predicate_compiler import compile_predicate, load_predicate
from sysml_codegen.resolution.models import ComputationGraph, ConcreteConstraint

BASE_REVISION = "6db321225a5c8568db0287b67ed1d04c03079cc2"
PRODUCTION_PATHS = (
    "src/sysml_codegen/generation/modules.py",
    "src/sysml_codegen/cli/__init__.py",
    "src/sysml_codegen/templates/constraint_module.py.jinja2",
)


def _assert_selected_source() -> None:
    expected_repo = Path(os.environ["EXPECTED_REPO"]).resolve()
    expected_revision = os.environ.get("EXPECTED_REV", BASE_REVISION)
    actual_revision = subprocess.run(
        ["git", "-C", str(expected_repo), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    assert actual_revision == expected_revision
    expected_src = (expected_repo / "src").resolve()
    assert Path(sysml_codegen.__file__).resolve().is_relative_to(expected_src)
    modules_source = inspect.getsourcefile(generation_modules)
    assert modules_source is not None
    assert Path(modules_source).resolve().is_relative_to(expected_src)

    expected_patch_sha = os.environ.get("EXPECTED_PATCH_SHA")
    if expected_patch_sha:
        production_diff = subprocess.run(
            [
                "git",
                "-C",
                str(expected_repo),
                "diff",
                "--binary",
                expected_revision,
                "--",
                *PRODUCTION_PATHS,
            ],
            check=True,
            capture_output=True,
        ).stdout
        assert hashlib.sha256(production_diff).hexdigest() == expected_patch_sha


_assert_selected_source()


def _ref(name: str) -> FeatureReferenceNode:
    return FeatureReferenceNode(
        reference=FeatureReferenceFact(
            source_name=name, target=None, target_types=[], chain_segments=[]
        ),
        operand_type=OperandTypeFact(category="real", enumeration=None, unit=None),
    )


def _literal(value: float) -> LiteralNode:
    return LiteralNode(
        literal=LiteralFact(kind="LiteralRational", value=value, result_type="real"),
        operand_type=OperandTypeFact(category="real", enumeration=None, unit=None),
    )


def _comparison(operator: str, left, right) -> OperatorNode:
    return OperatorNode(operator=operator, operands=[left, right], operand_type=None)


def _concrete(
    constraint_id: str,
    raw_key: str,
    predicate: OperatorNode,
) -> ConcreteConstraint:
    return ConcreteConstraint(
        constraint_id=constraint_id,
        usage_qualified_name=raw_key,
        source_local_identity=raw_key.rsplit("::", 1)[-1],
        source_form="inline",
        owner_kind="part_def",
        owner_qualified_name="Pkg::Owner",
        owner_instance_path="Pkg__owner",
        membership_kind="assert",
        is_negated=False,
        expected_value=True,
        predicate_ir=serialize_expression(predicate),
        inputs=[],
        evaluation_channel=f"{constraint_id}__evaluation",
        eligible=True,
    )


def _catalog(raw_keys: tuple[str, str]):
    entries = [
        _concrete("C1", raw_keys[0], _comparison(">", _ref("a"), _ref("b"))),
        _concrete("C2", raw_keys[1], _comparison("<", _ref("a"), _ref("b"))),
    ]
    facts = ConstraintFacts(definitions=[], usages=[], contexts=[], diagnostics=[])
    return assemble_constraint_catalog(entries, facts)


@dataclass(frozen=True)
class CollisionCase:
    raw_keys: tuple[str, str]
    expected_name: str


COLLISION_CASES = (
    CollisionCase(("Pkg::Foo", "Pkg::foo"), "constraint_pred_pkg__foo"),
    CollisionCase(("Pkg::foo__bar", "Pkg::foo_bar"), "constraint_pred_pkg__foo_bar"),
    CollisionCase(("Pkg::'Foo-Bar'", "Pkg::Foo_Bar"), "constraint_pred_pkg__foo_bar"),
)


@pytest.mark.parametrize(
    "collision_case", COLLISION_CASES, ids=("case-fold", "underscore-run", "quoted-hyphen")
)
def test_f2_collision_rejected(collision_case: CollisionCase) -> None:
    with pytest.raises(CodeGenerationError) as error:
        compile_shared_predicates(_catalog(collision_case.raw_keys))
    message = str(error.value)
    assert collision_case.expected_name in message
    assert all(repr(key) in message for key in sorted(collision_case.raw_keys))


def test_pre_fix_later_body_overwrites_earlier() -> None:
    compiled = compile_shared_predicates(_catalog(("Pkg::Foo", "Pkg::foo")))
    first_name, first_source, _ = compiled["Pkg::Foo"]
    second_name, second_source, _ = compiled["Pkg::foo"]
    assert first_name == second_name == "constraint_pred_pkg__foo"
    namespace: dict[str, object] = {}
    exec(first_source, namespace)
    assert namespace[first_name](a=2.0, b=1.0).actual_value is True
    exec(second_source, namespace)
    assert namespace[first_name](a=2.0, b=1.0).actual_value is False


def _raising_cases():
    division = OperatorNode(operator="/", operands=[_ref("a"), _ref("b")], operand_type=None)
    power = OperatorNode(operator="**", operands=[_ref("a"), _ref("b")], operand_type=None)
    direct = (
        (
            "division-by-zero",
            _comparison(">", division, _literal(0.0)),
            {"a": 1.0, "b": 0.0},
            ZeroDivisionError,
            "float division by zero",
        ),
        (
            "zero-negative-power",
            _comparison(">", power, _literal(0.0)),
            {"a": 0.0, "b": -1.0},
            ZeroDivisionError,
            "0.0 cannot be raised to a negative power",
        ),
        (
            "exponent-overflow",
            _comparison(">", power, _literal(0.0)),
            {"a": 10.0, "b": 400.0},
            OverflowError,
            "(34, 'Numerical result out of range')",
        ),
    )
    nested = OperatorNode(
        operator="and",
        operands=[direct[0][1], _comparison(">", _ref("a"), _literal(-1.0))],
        operand_type=None,
    )
    return (
        *direct,
        (
            "nested-connective",
            nested,
            {"a": 1.0, "b": 0.0},
            ZeroDivisionError,
            "float division by zero",
        ),
    )


@pytest.mark.parametrize(
    ("case_name", "expression", "values", "error_type", "message"),
    _raising_cases(),
    ids=lambda value: value if isinstance(value, str) else None,
)
def test_f1_unmangled_raise(case_name, expression, values, error_type, message) -> None:
    del case_name
    source, _ = compile_predicate(expression, "evidence_predicate")
    predicate = load_predicate(source, "evidence_predicate")
    with pytest.raises(error_type) as error:
        predicate(**values)
    assert str(error.value) == message


def _colliding_context():
    return SimpleNamespace(
        calc_defs=[],
        computation_graph=ComputationGraph(
            modules=[],
            entry_point_groups=[],
            execution_order=[],
            constraint_catalog=_catalog(("Pkg::Foo", "Pkg::foo")),
        ),
    )


def _manifest(root: Path):
    records = []
    if not root.exists():
        return records
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            records.append((relative, "symlink", os.readlink(path)))
        elif path.is_dir():
            records.append((relative, "directory", None))
        else:
            records.append((relative, "file", path.read_bytes()))
    return records


def _patch_live_context(monkeypatch) -> None:
    import sysml_codegen.orchestration.pipeline_builder as pipeline_builder

    monkeypatch.setattr(
        pipeline_builder, "build_pipeline_context", lambda *_a, **_k: _colliding_context()
    )


def test_collision_rejection_preserves_absent_output(tmp_path, monkeypatch) -> None:
    _patch_live_context(monkeypatch)
    output = tmp_path / "absent"
    config = GenerationConfig(output_path=output, models_path=tmp_path, overwrite=True)
    assert run_codegen(config) is False
    assert not output.exists()


def test_collision_rejection_preserves_populated_tree(tmp_path, monkeypatch) -> None:
    _patch_live_context(monkeypatch)
    output = tmp_path / "populated"
    (output / "nested").mkdir(parents=True)
    (output / "one.bin").write_bytes(b"one\x00")
    (output / "nested" / "two.txt").write_bytes(b"two\n")
    try:
        (output / "link").symlink_to("nested/two.txt")
    except OSError:
        pass
    before = _manifest(output)
    config = GenerationConfig(output_path=output, models_path=tmp_path, overwrite=True)
    assert run_codegen(config) is False
    assert _manifest(output) == before
