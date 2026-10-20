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

from sysml_codegen.cli import GenerationConfig, run_codegen
from sysml_codegen.cli.emit import (
    _generate_backlog,
    _generate_entry_points,
    _generate_modules,
    _generate_pipeline,
    _generate_registry,
    _generate_schemas,
    _generate_stencils,
    _generate_tests,
    _seal_package,
)
from sysml_codegen.cli.prepare import (
    PreparationStep,
    Refused,
    _get_template_env,
    log_refused,
    prepare_graph,
)
from sysml_codegen.cli.refusal import Refusal, RefusalItem, RefusalKind
from sysml_codegen.core.errors import GenerationCode
from sysml_codegen.elaboration.diagnostics import ElaborationCode, SiteReason
from sysml_codegen.generation import CodeGenerationError
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
from tests.helpers.retired_catalog_assembly import (
    FixtureConstraint,
    assemble_constraint_catalog,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
D38_MODEL = REPO_ROOT / "tests/fixtures/d38_caret"


class TestEnsurePackageInitFiles:
    """Bug 7: Intermediate __init__.py creation."""

    def test_creates_init_files_in_all_intermediate_dirs(self, tmp_path):
        from sysml_codegen.cli.emit import _ensure_package_init_files

        (tmp_path / "a" / "b" / "c").mkdir(parents=True)
        _ensure_package_init_files(tmp_path, "a/b/c")
        assert (tmp_path / "a" / "__init__.py").exists()
        assert (tmp_path / "a" / "b" / "__init__.py").exists()
        assert (tmp_path / "a" / "b" / "c" / "__init__.py").exists()

    def test_does_not_overwrite_existing_init(self, tmp_path):
        from sysml_codegen.cli.emit import _ensure_package_init_files

        (tmp_path / "a").mkdir()
        (tmp_path / "a" / "__init__.py").write_text("# custom\n")
        _ensure_package_init_files(tmp_path, "a")
        assert (tmp_path / "a" / "__init__.py").read_text() == "# custom\n"

    def test_uses_custom_docstring(self, tmp_path):
        from sysml_codegen.cli.emit import _ensure_package_init_files

        (tmp_path / "x").mkdir()
        _ensure_package_init_files(tmp_path, "x", '"""Custom."""\n')
        assert (tmp_path / "x" / "__init__.py").read_text() == '"""Custom."""\n'

    def test_single_dir(self, tmp_path):
        from sysml_codegen.cli.emit import _ensure_package_init_files

        (tmp_path / "pkg").mkdir()
        _ensure_package_init_files(tmp_path, "pkg")
        assert (tmp_path / "pkg" / "__init__.py").exists()


class TestSetupOutputDirectories:
    """Bug 7 broader scope: top-level subdirectory __init__.py creation."""

    def test_creates_init_py_in_all_subdirectories(self, tmp_path):
        from sysml_codegen.cli import GenerationConfig
        from sysml_codegen.cli.emit import _setup_output_directories

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
        from sysml_codegen.cli import GenerationConfig
        from sysml_codegen.cli.emit import _setup_output_directories

        output = tmp_path / "pkg"
        config = GenerationConfig(
            models_path=tmp_path / "models",
            output_path=output,
            package_name="pkg",
        )
        _setup_output_directories(config)

        assert not (output / "__init__.py").exists()

    def test_does_not_overwrite_existing_init_py(self, tmp_path):
        from sysml_codegen.cli import GenerationConfig
        from sysml_codegen.cli.emit import _setup_output_directories

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
    def concrete(constraint_id: str, raw_key: str, operator: str) -> FixtureConstraint:
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
        return FixtureConstraint(
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
    return graph


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
                declaration_id="decl-C1",
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
    return graph


def _missing_catalog_context():
    return _unsafe_name_context("safe_name").model_copy(update={"constraint_catalog": None})


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


def _refused(graph: ComputationGraph) -> Refused:
    refused = prepare_graph(graph, "pkg")
    assert isinstance(refused, Refused)
    return refused


@pytest.mark.parametrize("name", ["value", "body", "verdict", "self"])
def test_a_name_collision_is_refused_at_the_constraint_names_step(name):
    refused = _refused(_unsafe_name_context(name))
    assert refused.step is PreparationStep.CONSTRAINT_NAMES
    assert "name-safety violation" in refused.message
    assert refused.constraint_name_safety is not None
    assert refused.constraint_name_safety.final_binding == name


def test_a_missing_catalog_is_refused_at_the_constraint_names_step():
    refused = _refused(_missing_catalog_context())
    assert refused.step is PreparationStep.CONSTRAINT_NAMES
    assert "name-safety violation" in refused.message
    assert refused.constraint_name_safety is not None
    assert refused.constraint_name_safety.kind == "catalog_module_join"
    assert refused.constraint_name_safety.final_binding == "c1"


def _logged_refusals(caplog) -> list[Refusal]:
    return [record.refusal for record in caplog.records if hasattr(record, "refusal")]


def test_name_collision_refusal_carries_code_and_site_reason():
    assert _refused(_unsafe_name_context("value")).refusal == Refusal(
        RefusalKind.GENERATION,
        (
            RefusalItem(
                GenerationCode.CONSTRAINT_NAME_UNSAFE,
                SiteReason.GENERATION_CONSTRAINT_NAME_UNSAFE,
                None,
                None,
            ),
        ),
    )


def test_a_generation_refusal_logs_one_record_with_its_name_safety_payload(caplog):
    refused = _refused(_unsafe_name_context("value"))
    log_refused(refused)
    [record] = [record for record in caplog.records if hasattr(record, "refusal")]
    assert record.name == "sysml_codegen.cli"
    assert record.getMessage() == refused.message
    assert record.refusal == refused.refusal
    assert record.constraint_name_safety == refused.constraint_name_safety


def test_projection_refusal_logs_the_diagnostics_it_wraps(monkeypatch):
    """The user's message names the projection's own code, so the payload carries it too."""
    from sysml_codegen.cli.refusal import generation_refusal
    from sysml_codegen.elaboration.graph import Diagnostic
    from sysml_codegen.elaboration.project import ProjectionError
    from sysml_codegen.orchestration import exact_pipeline_context

    collision = Diagnostic(
        ElaborationCode.SI_RENDERING_COLLISION,
        None,
        "fx::site::s",
        None,
        "two declarations render to one entry point",
        source_file="root-0/model.sysml",
        source_line=5,
    )

    def refuse(*_args):
        raise ProjectionError([collision])

    monkeypatch.setattr(exact_pipeline_context, "project", refuse)
    with pytest.raises(CodeGenerationError) as error:
        exact_pipeline_context._project_or_fail(SimpleNamespace(), None)
    assert error.value.code is GenerationCode.PROJECTION_FAILED
    assert "SI_RENDERING_COLLISION" in str(error.value)
    assert generation_refusal(error.value).items == (
        RefusalItem(GenerationCode.PROJECTION_FAILED, None, None, None),
        RefusalItem(ElaborationCode.SI_RENDERING_COLLISION, None, "root-0/model.sysml", 5),
    )


_INTERNAL_DEFECT_REFUSAL = Refusal(
    RefusalKind.DIAGNOSTIC,
    (
        RefusalItem(
            ElaborationCode.SI_INTERNAL_DEFECT,
            SiteReason.INTERNAL_FAILURE_UNCLASSIFIED,
            None,
            None,
        ),
    ),
)


def _unclassified_failure(*_args, **_kwargs):
    raise RuntimeError("unclassified")


def _loaded_without_syside(monkeypatch) -> None:
    """Make the live load succeed with a stand-in, so construction is the step under test."""
    monkeypatch.setattr(
        "sysml_codegen.orchestration.elaborated_pipeline.load_live_models",
        lambda _paths: SimpleNamespace(),
    )


def test_unclassified_construction_failure_logs_the_internal_defect_refusal(
    tmp_path, monkeypatch, caplog
):
    _loaded_without_syside(monkeypatch)
    monkeypatch.setattr(
        "sysml_codegen.orchestration.exact_pipeline_context."
        "build_exact_pipeline_context_from_live_load",
        _unclassified_failure,
    )
    config = GenerationConfig(output_path=tmp_path / "output", models_path=tmp_path)
    assert run_codegen(config) is False
    assert _logged_refusals(caplog) == [_INTERNAL_DEFECT_REFUSAL]


def test_unclassified_generation_failure_logs_the_internal_defect_refusal(
    tmp_path, monkeypatch, caplog
):
    # The first preflight is patched to fail, so the graph is never read past its module count.
    context = SimpleNamespace(computation_graph=SimpleNamespace(modules=[]))
    _loaded_without_syside(monkeypatch)
    monkeypatch.setattr(
        "sysml_codegen.orchestration.exact_pipeline_context."
        "build_exact_pipeline_context_from_live_load",
        lambda _loaded: context,
    )
    monkeypatch.setattr(
        "sysml_codegen.cli.prepare._preflight_generation_metadata", _unclassified_failure
    )
    config = GenerationConfig(output_path=tmp_path / "output", models_path=tmp_path)
    assert run_codegen(config) is False
    assert _logged_refusals(caplog) == [_INTERNAL_DEFECT_REFUSAL]


def test_a_colliding_constraint_graph_is_refused_before_the_destination():
    assert _refused(_colliding_context()).step is PreparationStep.CONSTRAINT_NAMES


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

    monkeypatch.setattr("sysml_codegen.cli.emit._clear_output_directory", record_clear)
    config = GenerationConfig(
        output_path=output,
        models_path=D38_MODEL,
        package_name="d38_caret",
        overwrite=True,
    )
    assert run_codegen(config) is False
    assert clear_reached is False
    assert marker.read_text() == "unchanged\n"
