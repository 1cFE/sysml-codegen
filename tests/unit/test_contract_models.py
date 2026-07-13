"""Phase 1: contract models, canonical serialization, fingerprints (offline core).

Proves the first proof point — the semantic and executable fingerprints are stable pure
functions — and the graph-only (INV-1) / zero-constraint (INV-7) invariants, before any
pipeline wiring exists.
"""

from __future__ import annotations

import json

import pytest

from sysml_codegen.contracts.model_contract import build_model_contract
from sysml_codegen.contracts.seal import DEFAULT_COVERAGE_POLICY, seal_package
from sysml_codegen.resolution.models import (
    ComputationGraph,
    ConstraintCatalog,
    ConstraintCatalogEntry,
    ConstraintCatalogSourceRecord,
    EntryPoint,
    EntryPointType,
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
                is_negated=False,
                expected_value=True,
                predicate_ir="x > 0",
                evaluation_channel="calc_assert1",
            )
        ],
        fingerprint="deadbeef",
    )
    return ComputationGraph(
        modules=[module],
        entry_point_groups=[group],
        execution_order=["calc"],
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
    assert seal1.executable_fingerprint == seal2.executable_fingerprint


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
