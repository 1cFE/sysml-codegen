"""Unit tests for CLI generation helpers (Bug 7)."""

import os
from pathlib import Path
from types import SimpleNamespace

import pytest
from agentic_mbse.sysml.constraint_facts import ConstraintFacts
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
    _seal_package,
    run_codegen,
)
from sysml_codegen.generation import CodeGenerationError
from sysml_codegen.generation.constraint_catalog import assemble_constraint_catalog
from sysml_codegen.resolution.models import (
    ComputationGraph,
    ConcreteConstraint,
    ConstraintCatalog,
    ConstraintCatalogEntry,
    ConstraintFormalIdentity,
    InputSource,
    ModuleInput,
    ModuleKind,
    ModuleOutput,
    PipelineModule,
)

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
            predicate_source_key=raw_key,
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


def _unsafe_name_context(name: str = "value"):
    predicate = OperatorNode(
        operator=">",
        operands=[
            FeatureReferenceNode(
                reference=FeatureReferenceFact(
                    source_name=name, target=None, target_types=[], chain_segments=[]
                ),
                operand_type=OperandTypeFact(category="real", enumeration=None, unit=None),
            ),
            FeatureReferenceNode(
                reference=FeatureReferenceFact(
                    source_name="limit", target=None, target_types=[], chain_segments=[]
                ),
                operand_type=OperandTypeFact(category="real", enumeration=None, unit=None),
            ),
        ],
        operand_type=None,
    )
    module = PipelineModule(
        name="c1",
        module_type="constraints.C1ConstraintModule",
        inputs=[
            ModuleInput(
                param_name=param_name,
                python_type="float",
                source=InputSource(
                    source_type="module_output", producer_channel=f"up__{param_name}"
                ),
                formal_identity=ConstraintFormalIdentity(raw_name=param_name),
            )
            for param_name in (name, "limit")
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
    catalog = ConstraintCatalog(
        concrete_entries=[
            ConstraintCatalogEntry(
                constraint_id="C1",
                usage_qualified_name="Pkg::C1",
                source_local_identity="C1",
                source_form="inline",
                owner_qualified_name="Pkg",
                definition_qualified_name=None,
                owner_instance_path="Pkg",
                membership_kind="assert",
                predicate_source_key="inline:Pkg::C1",
                is_negated=False,
                expected_value=True,
                predicate_ir=serialize_expression(predicate),
                evaluation_channel="c1__evaluation",
            )
        ],
        fingerprint="unsafe",
    )
    graph = ComputationGraph(
        modules=[module],
        entry_point_groups=[],
        execution_order=["c1"],
        constraint_catalog=catalog,
    )
    return SimpleNamespace(calc_defs=[], computation_graph=graph)


def _missing_catalog_context():
    context = _unsafe_name_context("safe_name")
    context.computation_graph = context.computation_graph.model_copy(
        update={"constraint_catalog": None}
    )
    return context


GRAPH_AWARE_WRITERS = (
    _generate_schemas,
    _generate_modules,
    _generate_stencils,
    _generate_pipeline,
    _generate_registry,
    _generate_entry_points,
    _generate_backlog,
    _generate_tests,
    _seal_package,
)


@pytest.mark.parametrize("writer", GRAPH_AWARE_WRITERS, ids=lambda writer: writer.__name__)
@pytest.mark.parametrize("initial_tree", ["absent", "populated"])
def test_unsafe_graph_rejected_before_writer_io(writer, initial_tree, tmp_path):
    output = tmp_path / "output"
    if initial_tree == "populated":
        (output / "nested").mkdir(parents=True)
        (output / "nested" / "marker.bin").write_bytes(b"unchanged\x00")
    before = (output.exists(), _complete_tree_manifest(output))
    config = GenerationConfig(output_path=output, package_name="pkg")
    ctx = _unsafe_name_context()
    template_env = _get_template_env()
    if writer in (_generate_backlog, _seal_package):
        args = (ctx, config)
    elif writer is _generate_modules:
        from sysml_codegen.generation.constraint_plan import ConstraintGenerationPlan

        args = (ctx, config, template_env, ConstraintGenerationPlan({}, None, {}))
    else:
        args = (ctx, config, template_env)
    with pytest.raises(CodeGenerationError) as error:
        writer(*args)
    assert error.value.name_safety_violation is not None
    assert error.value.name_safety_violation.final_binding == "value"
    assert (output.exists(), _complete_tree_manifest(output)) == before


@pytest.mark.parametrize("writer", GRAPH_AWARE_WRITERS, ids=lambda writer: writer.__name__)
@pytest.mark.parametrize("initial_tree", ["absent", "populated"])
def test_missing_catalog_rejected_before_writer_io(writer, initial_tree, tmp_path):
    output = tmp_path / "output"
    if initial_tree == "populated":
        (output / "nested").mkdir(parents=True)
        (output / "nested" / "marker.bin").write_bytes(b"unchanged\x00")
    before = (output.exists(), _complete_tree_manifest(output))
    config = GenerationConfig(output_path=output, package_name="pkg")
    ctx = _missing_catalog_context()
    template_env = _get_template_env()
    if writer in (_generate_backlog, _seal_package):
        args = (ctx, config)
    elif writer is _generate_modules:
        from sysml_codegen.generation.constraint_plan import ConstraintGenerationPlan

        args = (ctx, config, template_env, ConstraintGenerationPlan({}, None, {}))
    else:
        args = (ctx, config, template_env)
    with pytest.raises(CodeGenerationError) as error:
        writer(*args)
    assert error.value.name_safety_violation is not None
    assert error.value.name_safety_violation.kind == "catalog_module_join"
    assert error.value.name_safety_violation.final_binding == "c1"
    assert (output.exists(), _complete_tree_manifest(output)) == before


def _patch_colliding_context(monkeypatch) -> None:
    import sysml_codegen.orchestration.pipeline_builder as pipeline_builder

    monkeypatch.setattr(
        pipeline_builder, "build_pipeline_context", lambda *_args, **_kwargs: _colliding_context()
    )


def _patch_unsafe_name_context(monkeypatch, name: str) -> None:
    import sysml_codegen.orchestration.pipeline_builder as pipeline_builder

    monkeypatch.setattr(
        pipeline_builder,
        "build_pipeline_context",
        lambda *_args, **_kwargs: _unsafe_name_context(name),
    )


def _patch_missing_catalog_context(monkeypatch) -> None:
    import sysml_codegen.orchestration.pipeline_builder as pipeline_builder

    monkeypatch.setattr(
        pipeline_builder,
        "build_pipeline_context",
        lambda *_args, **_kwargs: _missing_catalog_context(),
    )


@pytest.mark.parametrize("name", ["value", "body", "verdict", "self"])
@pytest.mark.parametrize("initial_tree", ["absent", "populated"])
def test_run_codegen_name_collision_preserves_tree_and_logs_payload(
    name, initial_tree, tmp_path, monkeypatch, caplog
):
    _patch_unsafe_name_context(monkeypatch, name)
    output = tmp_path / "output"
    if initial_tree == "populated":
        (output / "nested").mkdir(parents=True)
        (output / "nested" / "marker.bin").write_bytes(b"unchanged\x00")
    before = (output.exists(), _complete_tree_manifest(output))
    config = GenerationConfig(output_path=output, models_path=tmp_path, overwrite=True)
    assert run_codegen(config) is False
    assert (output.exists(), _complete_tree_manifest(output)) == before
    records = [record for record in caplog.records if "name-safety violation" in record.message]
    assert len(records) == 1
    violation = records[0].constraint_name_safety
    assert violation.final_binding == name


@pytest.mark.parametrize("initial_tree", ["absent", "populated"])
def test_run_codegen_missing_catalog_preserves_tree_and_logs_payload(
    initial_tree, tmp_path, monkeypatch, caplog
):
    _patch_missing_catalog_context(monkeypatch)
    output = tmp_path / "output"
    if initial_tree == "populated":
        (output / "nested").mkdir(parents=True)
        (output / "nested" / "marker.bin").write_bytes(b"unchanged\x00")
    before = (output.exists(), _complete_tree_manifest(output))
    config = GenerationConfig(output_path=output, models_path=tmp_path, overwrite=True)
    assert run_codegen(config) is False
    assert (output.exists(), _complete_tree_manifest(output)) == before
    records = [record for record in caplog.records if "name-safety violation" in record.message]
    assert len(records) == 1
    violation = records[0].constraint_name_safety
    assert violation.kind == "catalog_module_join"
    assert violation.final_binding == "c1"


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
