"""Phase 1: contract models, canonical serialization, fingerprints (offline core).

Proves the first proof point — the semantic and executable fingerprints are stable pure
functions — and the graph-only (INV-1) / zero-constraint (INV-7) invariants, before any
pipeline wiring exists.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
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

from sysml_codegen.contracts.model_contract import build_model_contract
from sysml_codegen.contracts.seal import DEFAULT_COVERAGE_POLICY, seal_package
from sysml_codegen.resolution.models import (
    ComputationGraph,
    ConstraintCatalog,
    ConstraintCatalogEntry,
    ConstraintCatalogSourceRecord,
    ConstraintFormalIdentity,
    EntryPoint,
    EntryPointType,
    InputSource,
    ModuleInput,
    ModuleOutput,
    ParameterGroup,
    PipelineModule,
)


def _graph_with_constraints() -> ComputationGraph:
    group = ParameterGroup(
        name="physics_params",
        class_name="PhysicsParams",
        source_file="design.sysml",
        parameters=[
            EntryPoint(
                qualified_name="Pkg__part__p_fusion",
                simple_name="p_fusion",
                entry_type=EntryPointType.LIBRARY_DEFAULT,
                default_value=1.0,
                python_type="float",
            )
        ],
    )
    module = PipelineModule(
        name="calc",
        module_type="CalcModule",
        inputs=[],
        outputs=[
            ModuleOutput(
                field_name="root",
                python_type="float",
                channel_name="calc_p_fusion",
            )
        ],
        execution_order=0,
        module_kind="calculation",
    )
    constraint_module = PipelineModule(
        name="c1",
        module_type="constraints.C1ConstraintModule",
        inputs=[
            ModuleInput(
                param_name="x",
                python_type="float",
                source=InputSource(source_type="module_output", producer_channel="calc_p_fusion"),
                formal_identity=ConstraintFormalIdentity(raw_name="x"),
            )
        ],
        outputs=[
            ModuleOutput(
                field_name="evaluation",
                python_type="ConstraintEvaluation",
                channel_name="calc_assert1",
            )
        ],
        execution_order=1,
        module_kind="constraint",
    )
    predicate_ir = serialize_expression(
        OperatorNode(
            operator=">",
            operands=[
                FeatureReferenceNode(
                    reference=FeatureReferenceFact(
                        source_name="x", target=None, target_types=[], chain_segments=[]
                    ),
                    operand_type=OperandTypeFact(category="real", enumeration=None, unit=None),
                ),
                LiteralNode(
                    literal=LiteralFact(kind="LiteralRational", value=0.0, result_type="real"),
                    operand_type=OperandTypeFact(category="real", enumeration=None, unit=None),
                ),
            ],
            operand_type=None,
        )
    )
    catalog = ConstraintCatalog(
        source_records=[
            ConstraintCatalogSourceRecord(
                definition_qualified_name="Pkg__constraint_def",
                formal_names=["x"],
            )
        ],
        concrete_entries=[
            ConstraintCatalogEntry(
                constraint_id="c1",
                usage_qualified_name="Pkg__part__assert1",
                owner_instance_path="Pkg__part",
                membership_kind="assert",
                predicate_source_key="inline:Pkg__part__assert1",
                is_negated=False,
                expected_value=True,
                predicate_ir=predicate_ir,
                evaluation_channel="calc_assert1",
            )
        ],
        fingerprint="deadbeef",
    )
    return ComputationGraph(
        modules=[module, constraint_module],
        entry_point_groups=[group],
        execution_order=["calc", "c1"],
        constraint_catalog=catalog,
    )


def _graph_without_constraints() -> ComputationGraph:
    return ComputationGraph(modules=[], entry_point_groups=[], execution_order=[])


def _write_fixture(directory) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "modules").mkdir()
    (directory / "modules" / "calc.py").write_text("def run():\n    return 1\n")
    (directory / "pipelines").mkdir()
    (directory / "pipelines" / "p.yaml").write_text("modules: []\n")


def test_model_contract_is_graph_only(monkeypatch):
    """INV-1 / SC-5: patch filesystem access to raise; build still succeeds."""

    def _raise(*args, **kwargs):
        raise AssertionError("build_model_contract touched the filesystem")

    monkeypatch.setattr("builtins.open", _raise)
    mc = build_model_contract(_graph_with_constraints())
    assert mc.semantic_fingerprint


def test_fingerprints_are_deterministic(tmp_path):
    graph = _graph_with_constraints()
    mc1 = build_model_contract(graph)
    mc2 = build_model_contract(graph)
    assert mc1.semantic_fingerprint == mc2.semantic_fingerprint

    _write_fixture(tmp_path / "a")
    _write_fixture(tmp_path / "b")
    seal1 = seal_package(tmp_path / "a", "pkg", DEFAULT_COVERAGE_POLICY)
    seal2 = seal_package(tmp_path / "b", "pkg", DEFAULT_COVERAGE_POLICY)
    assert list(seal1.artifact_hashes) == list(seal2.artifact_hashes)
    assert seal1.artifact_hashes == seal2.artifact_hashes
    assert seal1.executable_fingerprint == seal2.executable_fingerprint


FORBIDDEN_SYMLINK_MESSAGE = "symlinks are forbidden beneath the package root"


def _link_target(tmp_path: Path, package: Path, target_kind: str, entry_kind: str) -> Path:
    if target_kind == "internal":
        return package / ("modules/calc.py" if entry_kind == "file" else "modules")
    target = tmp_path / f"{target_kind}-{entry_kind}"
    if target_kind == "escaping":
        if entry_kind == "file":
            target.write_text("outside\n")
        else:
            target.mkdir()
    return target


@pytest.mark.parametrize("entry_kind", ["file", "directory"])
@pytest.mark.parametrize("target_kind", ["internal", "escaping", "dangling"])
def test_direct_seal_rejects_every_symlink(tmp_path, entry_kind, target_kind):
    from sysml_codegen.contracts import seal as seal_module

    package = tmp_path / "pkg"
    _write_fixture(package)
    link = package / "alias"
    link.symlink_to(
        _link_target(tmp_path, package, target_kind, entry_kind),
        target_is_directory=entry_kind == "directory",
    )

    with pytest.raises(seal_module.PackageSealError) as caught:
        seal_package(package, "pkg")

    assert caught.value.kind == "INVALID_PATH"
    assert caught.value.path == "alias"
    assert caught.value.message == FORBIDDEN_SYMLINK_MESSAGE
    assert str(caught.value) == f"INVALID_PATH(alias): {FORBIDDEN_SYMLINK_MESSAGE}"


def test_direct_seal_rejects_symlink_root_and_excluded_link(tmp_path):
    from sysml_codegen.contracts import seal as seal_module

    target = tmp_path / "target"
    _write_fixture(target)
    root_link = tmp_path / "root"
    root_link.symlink_to(target, target_is_directory=True)
    with pytest.raises(seal_module.PackageSealError) as root_error:
        seal_package(root_link, "pkg")
    assert root_error.value.path == "."

    excluded = target / "contracts/package_contract.json"
    excluded.parent.mkdir()
    excluded.symlink_to(tmp_path / "missing-seal")
    with pytest.raises(seal_module.PackageSealError) as excluded_error:
        seal_package(target, "pkg")
    assert excluded_error.value.path == "contracts/package_contract.json"


def test_direct_seal_propagates_preflight_walk_failure(tmp_path, monkeypatch):
    package = tmp_path / "pkg"
    _write_fixture(package)
    original_rglob = Path.rglob

    def deny_walk(path, pattern):
        if path == package:
            raise PermissionError("walk denied")
        return original_rglob(path, pattern)

    monkeypatch.setattr(Path, "rglob", deny_walk)
    with pytest.raises(PermissionError, match="walk denied"):
        seal_package(package, "pkg")


def test_zero_constraint_graph_seals():
    """SC-6 / INV-7: a constraint-free graph yields a well-formed, stable contract."""
    mc = build_model_contract(_graph_without_constraints())
    assert mc.constraint_catalog is None
    assert json.loads(mc.model_dump_json())["constraint_catalog"] is None
    assert mc.semantic_fingerprint


def test_model_contract_json_bytes_are_stable(tmp_path):
    """INV-6: on-disk contract bytes are a deterministic function of the graph."""
    from sysml_codegen.contracts.serialize import write_contract_json

    graph = _graph_with_constraints()
    mc1 = build_model_contract(graph)
    mc2 = build_model_contract(graph)

    path1 = tmp_path / "a" / "model_contract.json"
    path2 = tmp_path / "b" / "model_contract.json"
    path1.parent.mkdir(parents=True)
    path2.parent.mkdir(parents=True)
    write_contract_json(path1, mc1)
    write_contract_json(path2, mc2)
    assert path1.read_bytes() == path2.read_bytes()


def test_semantic_fingerprint_excludes_itself():
    """INV-2: no circularity — the fingerprint is not an input to its own payload."""
    mc = build_model_contract(_graph_with_constraints())
    payload_without_fp = mc.model_dump(exclude={"semantic_fingerprint"})
    assert "semantic_fingerprint" not in payload_without_fp


@pytest.mark.parametrize("field", ["parameters", "outputs"])
def test_model_contract_projects_graph_fields(field):
    mc = build_model_contract(_graph_with_constraints())
    assert getattr(mc, field), f"expected at least one projected {field}"


def test_glob_matcher_bodies_identical_across_seal_and_verify():
    """Drift guard (Item 9 audit Finding 1): the coverage-glob matcher is
    deliberately duplicated in seal.py (producer) and verify.py (stdlib-only
    consumer, D7). Their executable code must stay identical — docstrings may
    differ — or seal-time and verify-time coverage decisions silently diverge.
    (_is_covered differs by design: typed CoveragePolicy vs raw dict.)"""
    import ast
    import inspect
    import textwrap

    from sysml_codegen.contracts import seal, verify

    def code_body(fn):
        tree = ast.parse(textwrap.dedent(inspect.getsource(fn)))
        fdef = tree.body[0]
        # drop a leading docstring expression if present
        body = fdef.body
        if (
            body
            and isinstance(body[0], ast.Expr)
            and isinstance(getattr(body[0], "value", None), ast.Constant)
        ):
            body = body[1:]
        return [ast.dump(node) for node in body]

    assert code_body(seal._glob_to_regex) == code_body(verify._glob_to_regex)


def test_package_tree_inspector_bodies_identical_across_seal_and_verify():
    import ast
    import inspect
    import textwrap

    from sysml_codegen.contracts import seal, verify

    def code_body(function):
        tree = ast.parse(textwrap.dedent(inspect.getsource(function)))
        return [ast.dump(node) for node in tree.body[0].body]

    assert code_body(seal._inspect_package_tree) == code_body(verify._inspect_package_tree)
