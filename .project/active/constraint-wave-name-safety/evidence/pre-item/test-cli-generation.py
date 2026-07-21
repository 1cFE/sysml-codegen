"""Unit tests for CLI generation helpers (Bug 7)."""

import os
from pathlib import Path
from types import SimpleNamespace

from agentic_mbse.sysml.constraint_facts import ConstraintFacts
from agentic_mbse.sysml.expression_facts import FeatureReferenceFact, OperandTypeFact
from agentic_mbse.sysml.expression_ir import (
    FeatureReferenceNode,
    OperatorNode,
    serialize_expression,
)

from sysml_codegen.cli import GenerationConfig, run_codegen
from sysml_codegen.generation.constraint_catalog import assemble_constraint_catalog
from sysml_codegen.resolution.models import ComputationGraph, ConcreteConstraint

REPO_ROOT = Path(__file__).resolve().parents[2]
CHAIN_SNAPSHOT = REPO_ROOT / "tests/fixtures/chain_spike_model/extraction_snapshot.json"


class TestEnsurePackageInitFiles:
    """Bug 7: Intermediate __init__.py creation."""

    def test_creates_init_files_in_all_intermediate_dirs(self, tmp_path):
        from sysml_codegen.cli import _ensure_package_init_files

        (tmp_path / "a" / "b" / "c").mkdir(parents=True)
        _ensure_package_init_files(tmp_path, "a/b/c")
        assert (tmp_path / "a" / "__init__.py").exists()
        assert (tmp_path / "a" / "b" / "__init__.py").exists()
        assert (tmp_path / "a" / "b" / "c" / "__init__.py").exists()

    def test_does_not_overwrite_existing_init(self, tmp_path):
        from sysml_codegen.cli import _ensure_package_init_files

        (tmp_path / "a").mkdir()
        (tmp_path / "a" / "__init__.py").write_text("# custom\n")
        _ensure_package_init_files(tmp_path, "a")
        assert (tmp_path / "a" / "__init__.py").read_text() == "# custom\n"

    def test_uses_custom_docstring(self, tmp_path):
        from sysml_codegen.cli import _ensure_package_init_files

        (tmp_path / "x").mkdir()
        _ensure_package_init_files(tmp_path, "x", '"""Custom."""\n')
        assert (tmp_path / "x" / "__init__.py").read_text() == '"""Custom."""\n'

    def test_single_dir(self, tmp_path):
        from sysml_codegen.cli import _ensure_package_init_files

        (tmp_path / "pkg").mkdir()
        _ensure_package_init_files(tmp_path, "pkg")
        assert (tmp_path / "pkg" / "__init__.py").exists()


class TestSetupOutputDirectories:
    """Bug 7 broader scope: top-level subdirectory __init__.py creation."""

    def test_creates_init_py_in_all_subdirectories(self, tmp_path):
        from sysml_codegen.cli import GenerationConfig, _setup_output_directories

        output = tmp_path / "pkg"
        config = GenerationConfig(
            models_path=tmp_path / "models",
            output_path=output,
            package_name="pkg",
        )
        _setup_output_directories(config)

        expected_subdirs = ["schemas", "modules", "handwritten", "pipelines", "inputs", "tests"]
        for subdir in expected_subdirs:
            init_file = output / subdir / "__init__.py"
            assert init_file.exists(), f"Missing __init__.py in {subdir}/"
            assert init_file.read_text() == '"""Generated package."""\n'

    def test_does_not_create_init_py_in_output_path(self, tmp_path):
        from sysml_codegen.cli import GenerationConfig, _setup_output_directories

        output = tmp_path / "pkg"
        config = GenerationConfig(
            models_path=tmp_path / "models",
            output_path=output,
            package_name="pkg",
        )
        _setup_output_directories(config)

        assert not (output / "__init__.py").exists()

    def test_does_not_overwrite_existing_init_py(self, tmp_path):
        from sysml_codegen.cli import GenerationConfig, _setup_output_directories

        output = tmp_path / "pkg"
        (output / "schemas").mkdir(parents=True)
        (output / "schemas" / "__init__.py").write_text("# custom content\n")

        config = GenerationConfig(
            models_path=tmp_path / "models",
            output_path=output,
            package_name="pkg",
        )
        _setup_output_directories(config)

        assert (output / "schemas" / "__init__.py").read_text() == "# custom content\n"


def _colliding_context():
    def concrete(constraint_id: str, raw_key: str, operator: str) -> ConcreteConstraint:
        def ref(name: str) -> FeatureReferenceNode:
            return FeatureReferenceNode(
                reference=FeatureReferenceFact(
                    source_name=name, target=None, target_types=[], chain_segments=[]
                ),
                operand_type=OperandTypeFact(category="real", enumeration=None, unit=None),
            )

        predicate = OperatorNode(
            operator=operator, operands=[ref("a"), ref("b")], operand_type=None
        )
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

    facts = ConstraintFacts(definitions=[], usages=[], contexts=[], diagnostics=[])
    catalog = assemble_constraint_catalog(
        [concrete("C1", "Pkg::Foo", ">"), concrete("C2", "Pkg::foo", "<")], facts
    )
    graph = ComputationGraph(
        modules=[], entry_point_groups=[], execution_order=[], constraint_catalog=catalog
    )
    return SimpleNamespace(calc_defs=[], computation_graph=graph)


def _complete_tree_manifest(root: Path):
    records = []
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            records.append((relative, "symlink", os.readlink(path)))
        elif path.is_dir():
            records.append((relative, "directory", None))
        else:
            records.append((relative, "file", path.read_bytes()))
    return records


def _patch_colliding_context(monkeypatch) -> None:
    import sysml_codegen.orchestration.pipeline_builder as pipeline_builder

    monkeypatch.setattr(
        pipeline_builder, "build_pipeline_context", lambda *_args, **_kwargs: _colliding_context()
    )


def test_collision_rejection_preserves_absent_output(tmp_path, monkeypatch):
    _patch_colliding_context(monkeypatch)
    output = tmp_path / "absent"
    config = GenerationConfig(output_path=output, models_path=tmp_path, overwrite=True)
    assert run_codegen(config) is False
    assert not output.exists()


def test_collision_rejection_preserves_populated_tree(tmp_path, monkeypatch):
    _patch_colliding_context(monkeypatch)
    output = tmp_path / "populated"
    (output / "nested").mkdir(parents=True)
    (output / "one.bin").write_bytes(b"one\x00")
    (output / "nested" / "two.txt").write_bytes(b"two\n")
    try:
        (output / "link").symlink_to("nested/two.txt")
    except OSError:
        pass
    before = _complete_tree_manifest(output)
    config = GenerationConfig(output_path=output, models_path=tmp_path, overwrite=True)
    assert run_codegen(config) is False
    assert _complete_tree_manifest(output) == before


def test_generation_rejects_symlink_root_before_output_mutation(tmp_path, monkeypatch):
    target = tmp_path / "target"
    target.mkdir()
    marker = target / "marker.txt"
    marker.write_text("unchanged\n")
    output = tmp_path / "out"
    output.symlink_to(target, target_is_directory=True)
    clear_reached = False

    def record_clear(config):
        nonlocal clear_reached
        clear_reached = True

    monkeypatch.setattr("sysml_codegen.cli._clear_output_directory", record_clear)
    config = GenerationConfig(
        output_path=output,
        from_snapshot=CHAIN_SNAPSHOT,
        package_name="chain_spike",
        overwrite=True,
    )
    assert run_codegen(config) is False
    assert clear_reached is False
    assert marker.read_text() == "unchanged\n"
