"""The writing half of ``generate``: everything that changes the destination (Item 2b D1).

``emit_package`` takes what ``prepare`` built and writes it: the destination link check, the
clear, the package folders, the writers and the seal. This is the only module on the generate
route that writes under the destination. Each failure is logged once, with the record
``generate`` has always logged for it, and returned.
"""

from __future__ import annotations

import logging
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from sysml_codegen.cli.prepare import (
    PreparationStep,
    Prepared,
    Refused,
    _get_python_path,
    log_refused,
    refused_at_generation,
)
from sysml_codegen.cli.refusal import Refusal, RefusalKind

if TYPE_CHECKING:
    import jinja2

    from sysml_codegen.cli import GenerationConfig
    from sysml_codegen.generation.constraint_plan import ConstraintGenerationPlan
    from sysml_codegen.resolution.models import ComputationGraph

#: The CLI's logger, so a record keeps the name it had before the writers moved here.
logger = logging.getLogger("sysml_codegen.cli")


@dataclass(frozen=True)
class DestinationProblem:
    """Why the destination cannot take a package: today's sealing-failure detail."""

    detail: str


def inspect_destination(path: Path) -> DestinationProblem | None:
    """Check, without writing, that no link sits on or under the destination."""
    from sysml_codegen.contracts import PackageSealError, ensure_package_tree_is_link_free

    try:
        ensure_package_tree_is_link_free(path)
    except (PackageSealError, OSError) as error:
        return DestinationProblem(str(error))
    return None


def destination_refused(problem: DestinationProblem) -> Refused:
    """The refusal ``generate`` logs when the destination cannot take a package."""
    return Refused(
        PreparationStep.DESTINATION,
        Refusal(RefusalKind.PACKAGE_WRITE),
        f"Package sealing failed: {problem.detail}",
    )


def emit_package(prepared: Prepared, config: GenerationConfig) -> Refused | None:
    """Write and seal one package. Returns ``None``, or the failure it logged.

    The destination is checked again first, because the tree can change after the caller
    checked it.
    """
    if config.package_name != prepared.package_name:
        raise ValueError(
            f"emit_package was given package {config.package_name!r} for a model prepared "
            f"as {prepared.package_name!r}"
        )
    problem = inspect_destination(config.output_path)
    if problem is not None:
        return _logged(destination_refused(problem))
    return _write_package(prepared, config)


def _logged(refused: Refused) -> Refused:
    log_refused(refused)
    return refused


def _write_package(prepared: Prepared, config: GenerationConfig) -> Refused | None:
    """Clear, write and seal, in today's order. Returns ``None`` or the logged failure."""
    from sysml_codegen.contracts import PackageSealError

    graph = prepared.graph
    template_env = prepared.template_env
    try:
        if config.overwrite:
            logger.info("Clearing existing output directory...")
            _clear_output_directory(config)

        logger.info("Creating output directory structure...")
        _setup_output_directories(config)

        # primitives.py is required for module imports.
        _generate_primitives(config)

        logger.info("Generating schemas...")
        _generate_schemas(graph, config, template_env)

        logger.info("Generating TEAx module wrappers...")
        _generate_modules(graph, config, template_env, prepared.constraint_plan)

        logger.info("Generating implementation stencils...")
        _generate_stencils(graph, config, template_env)

        logger.info("Generating pipeline configuration...")
        _generate_pipeline(graph, config, template_env)

        logger.info("Generating module registry...")
        _generate_registry(graph, config, template_env)

        logger.info("Generating entry point schemas and JSON templates...")
        _generate_entry_points(graph, config, template_env)

        logger.info("Generating implementation backlog...")
        _generate_backlog(graph, config)

        logger.info("Generating runnable tests...")
        _generate_tests(graph, config, template_env)

        # Seal over the final on-disk state, live and from-snapshot paths alike.
        logger.info("Sealing package...")
        try:
            _seal_package(graph, config)
        except (PackageSealError, OSError) as error:
            return _logged(
                Refused(
                    PreparationStep.EMIT,
                    Refusal(RefusalKind.PACKAGE_WRITE),
                    f"Package sealing failed: {error}",
                )
            )
    # Measured, and not changed here: any failure after the clear leaves the partially
    # written output tree on disk.
    except Exception as error:
        return _logged(refused_at_generation(PreparationStep.EMIT, error))

    logger.info("Code generation complete")
    return None


def _ensure_package_init_files(
    base_dir: Path, relative_path: str, docstring: str = '"""Namespace package."""\n'
) -> None:
    """Ensure __init__.py exists in all directories along relative_path."""
    parts = Path(relative_path).parts
    current = base_dir
    for part in parts:
        current = current / part
        init_file = current / "__init__.py"
        if not init_file.exists():
            init_file.write_text(docstring)


def _clear_output_directory(config: GenerationConfig) -> None:
    """Clear existing output directory before regeneration.

    Respects preserve_handwritten flag to keep handwritten/ directory intact.
    """
    if not config.output_path.exists():
        return

    for item in config.output_path.iterdir():
        # Skip handwritten directory if preserve flag is set
        if config.preserve_handwritten and item.name == "handwritten":
            logger.debug("Preserving handwritten/ directory")
            continue

        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()

    logger.debug(f"Cleared output directory: {config.output_path}")


def _setup_output_directories(config: GenerationConfig) -> None:
    """Create output directory structure."""
    dirs = [
        config.output_path,
        config.output_path / "schemas",
        config.output_path / "modules",
        config.output_path / "handwritten",
        config.output_path / "pipelines",
        config.output_path / "inputs",
        config.output_path / "tests",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)

    # Bug 7 broader scope: ensure all subdirectories are proper Python packages.
    # Excludes output_path itself — its __init__.py is generated later by _generate_registry().
    for d in dirs:
        init_file = d / "__init__.py"
        if d != config.output_path and not init_file.exists():
            init_file.write_text('"""Generated package."""\n')


def _generate_primitives(config: GenerationConfig) -> None:
    """Generate primitives.py with RootModel wrappers."""
    content = '''"""Pydantic RootModel wrappers for primitive types."""
from pydantic import RootModel

Float = RootModel[float]
Int = RootModel[int]
String = RootModel[str]
Bool = RootModel[bool]

__all__ = ["Float", "Int", "String", "Bool"]
'''
    output_path = config.output_path / "primitives.py"
    output_path.write_text(content)
    logger.debug(f"Generated primitives: {output_path}")


def _generate_schemas(
    graph: ComputationGraph,
    config: GenerationConfig,
    template_env: jinja2.Environment,
) -> None:
    """Generate Pydantic schemas for multi-output modules."""
    from sysml_codegen.generation import generate_multioutput_model
    from sysml_codegen.resolution.models import ModuleKind

    schemas_dir = config.output_path / "schemas"

    multioutput_count = 0
    for module in graph.modules:
        if module.module_kind in (ModuleKind.CONSTRAINT, ModuleKind.REPORT_AGGREGATOR):
            continue
        if len(module.outputs) < 2:
            continue
        assert module.calc_def_name is not None
        output_path = schemas_dir / f"{module.calc_def_name.lower()}_output.py"
        code = generate_multioutput_model(
            module,
            template_env,
            output_path,
            package_name=config.package_name,
        )
        if code:
            output_path.write_text(code)
            multioutput_count += 1
            logger.debug(f"Generated schema: {output_path.name}")

    logger.info(f"Generated {multioutput_count} multi-output schemas")

    # Item 7 / D4: per-package evidence schemas, gated on the package actually having
    # constraint machinery that could run — one concrete entry. A corpus that declares no
    # constraint writes nothing here (INV-7), and so does one that declares constraints
    # none of which reach an instance: there would be nothing to populate the evidence
    # with. See `ships_constraint_machinery` for why the catalog's existence stopped being
    # the right question, and which item supersedes this rule.
    from sysml_codegen.resolution.models import ships_constraint_machinery

    if ships_constraint_machinery(graph):
        template = template_env.get_template("constraint_types.py.jinja2")
        code = template.render()
        if not code.endswith("\n"):
            code += "\n"
        (schemas_dir / "constraint_types.py").write_text(code)
        logger.info("Generated constraint evidence schemas: constraint_types.py")


def _generate_modules(
    graph: ComputationGraph,
    config: GenerationConfig,
    template_env: jinja2.Environment,
    constraint_plan: ConstraintGenerationPlan,
) -> None:
    """Generate TEAx module wrappers for all module types (ADR-003 namespacing)."""
    from sysml_codegen.generation import generate_teax_module
    from sysml_codegen.resolution.models import ModuleKind

    modules_dir = config.output_path / "modules"
    catalog = graph.constraint_catalog
    staged: list[tuple[Path, str]] = []

    if constraint_plan.predicates_code is not None:
        staged.append(
            (modules_dir / "constraints" / "predicates.py", constraint_plan.predicates_code)
        )

    for module in graph.modules:
        python_path = _get_python_path(module)
        output_path = modules_dir / python_path.full_path
        if module.module_kind in (ModuleKind.CONSTRAINT, ModuleKind.REPORT_AGGREGATOR):
            code = constraint_plan.rendered_modules[module.name]
        else:
            code = generate_teax_module(
                module,
                template_env,
                output_path,
                config.package_name,
            )
        if code:
            staged.append((output_path, code))

    # Rendering and semantic scope checks are complete. Only now may this writer mutate.
    initialized_namespaces: set[str] = set()
    for output_path, code in staged:
        relative_parent = output_path.parent.relative_to(modules_dir)
        namespace = relative_parent.as_posix()
        if namespace != "." and namespace not in initialized_namespaces:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            _ensure_package_init_files(
                modules_dir,
                namespace,
                '"""Namespace package for generated modules."""\n',
            )
            initialized_namespaces.add(namespace)
        output_path.write_text(code)
        logger.debug(f"Generated module: {output_path}")

    module_count = len(staged) - (1 if catalog is not None else 0)
    logger.info(f"Generated {module_count} TEAx module wrappers")


def _generate_stencils(
    graph: ComputationGraph,
    config: GenerationConfig,
    template_env: jinja2.Environment,
) -> None:
    """Generate implementation stencils for all module types (ADR-003 namespacing)."""
    from sysml_codegen.generation import (
        backup_implementation,
        generate_implementation,
        should_regenerate_stencil,
    )
    from sysml_codegen.resolution.models import ModuleKind

    handwritten_dir = config.output_path / "handwritten"
    backup_dir = handwritten_dir / "backup"

    stats = {"new": 0, "preserved": 0, "regenerated": 0}

    for module in graph.modules:
        if module.module_kind in (ModuleKind.CONSTRAINT, ModuleKind.REPORT_AGGREGATOR):
            # D8: fully generated, no handwritten implementation to stencil.
            continue
        python_path = _get_python_path(module)

        # Create namespace subdirectory with __init__.py in all intermediates
        if python_path.directory:
            namespace_dir = handwritten_dir / python_path.directory
            namespace_dir.mkdir(parents=True, exist_ok=True)
            _ensure_package_init_files(
                handwritten_dir,
                python_path.directory,
                '"""Handwritten implementations."""\n',
            )
            output_path = namespace_dir / f"{python_path.filename}_impl.py"
        else:
            output_path = handwritten_dir / f"{python_path.filename}_impl.py"

        # Smart regeneration logic
        if config.smart_regen and output_path.exists():
            should_regen, reason = should_regenerate_stencil(module, output_path)
            if should_regen:
                backup_implementation(output_path, backup_dir)
                code = generate_implementation(
                    module,
                    template_env,
                    output_path,
                    config.package_name,
                )
                if code:
                    output_path.write_text(code)
                stats["regenerated"] += 1
                logger.debug(f"Regenerated stencil ({reason}): {output_path.name}")
            else:
                # Smart-regen: signature unchanged. Check if stub can be upgraded.
                existing_content = output_path.read_text()
                is_stub = "raise NotImplementedError" in existing_content
                has_auto_impl = module.auto_impl_context is not None
                if is_stub and has_auto_impl:
                    backup_implementation(output_path, backup_dir)
                    code = generate_implementation(
                        module,
                        template_env,
                        output_path,
                        config.package_name,
                    )
                    if code:
                        output_path.write_text(code)
                    stats["regenerated"] += 1
                    logger.debug(f"Upgraded stub to auto-impl: {output_path.name}")
                else:
                    stats["preserved"] += 1
                    logger.debug(f"Preserved stencil ({reason}): {output_path.name}")
        elif config.preserve_handwritten and output_path.exists():
            stats["preserved"] += 1
            logger.debug(f"Preserved existing stencil: {output_path.name}")
        else:
            code = generate_implementation(
                module,
                template_env,
                output_path,
                config.package_name,
            )
            if code:
                output_path.write_text(code)
            stats["new"] += 1

    if config.smart_regen:
        logger.info(
            f"Stencils - New: {stats['new']}, "
            f"Preserved: {stats['preserved']}, "
            f"Regenerated: {stats['regenerated']}"
        )
    else:
        logger.info(f"Generated {stats['new']} implementation stencils")


def _generate_pipeline(
    graph: ComputationGraph,
    config: GenerationConfig,
    template_env: jinja2.Environment,
) -> None:
    """Generate pipeline YAML from computation graph."""
    from sysml_codegen.generation import generate_pipeline_yaml

    pipelines_dir = config.output_path / "pipelines"
    output_path = pipelines_dir / f"{config.pipeline_name}.yaml"

    yaml_content = generate_pipeline_yaml(
        graph=graph,
        package_name=config.package_name,
        template_env=template_env,
    )
    if yaml_content:
        output_path.write_text(yaml_content)
        logger.debug(f"Generated pipeline: {output_path}")

    logger.info(f"Generated pipeline configuration: {config.pipeline_name}.yaml")


def _generate_registry(
    graph: ComputationGraph,
    config: GenerationConfig,
    template_env: jinja2.Environment,
) -> None:
    """Generate registry function in __init__.py."""
    from sysml_codegen.generation import generate_registry

    output_path = config.output_path / "__init__.py"

    code = generate_registry(
        graph=graph,
        package_name=config.package_name,
        template_env=template_env,
        output_path=output_path,
    )
    if code:
        output_path.write_text(code)
        logger.debug(f"Generated registry: {output_path}")

    logger.info(f"Generated module registry with {len(graph.modules)} modules")


def _generate_entry_points(
    graph: ComputationGraph,
    config: GenerationConfig,
    template_env: jinja2.Environment,
) -> None:
    """Generate entry point parameter group schemas and JSON templates."""
    from sysml_codegen.generation import (
        generate_all_derived_jsons_from_graph,
        generate_all_derived_schemas_from_graph,
    )

    entry_point_groups = graph.entry_point_groups

    if entry_point_groups:
        schema_files = generate_all_derived_schemas_from_graph(
            entry_point_groups,
            template_env,
            config.output_path,
        )
        logger.info(f"Generated {len(schema_files)} parameter group schemas")

        json_files = generate_all_derived_jsons_from_graph(
            entry_point_groups,
            config.output_path,
        )
        logger.info(f"Generated {len(json_files)} JSON input templates")
    else:
        logger.info("No entry point groups to generate")


def _generate_backlog(
    graph: ComputationGraph,
    config: GenerationConfig,
) -> None:
    """Generate implementation backlog report."""
    from sysml_codegen.generation import generate_backlog_report

    output_path = config.output_path / "IMPLEMENTATION_BACKLOG.md"

    markdown = generate_backlog_report(
        graph,
        output_path,
        config.package_name,
    )
    if markdown:
        output_path.write_text(markdown)
        logger.info(f"Generated implementation backlog: {output_path.name}")


def _generate_tests(
    graph: ComputationGraph,
    config: GenerationConfig,
    template_env: jinja2.Environment,
) -> None:
    """Generate runnable test file for implementations."""
    from sysml_codegen.generation import generate_test_implementations

    tests_dir = config.output_path / "tests"
    tests_dir.mkdir(parents=True, exist_ok=True)

    output_path = tests_dir / "test_implementations_runnable.py"

    content = generate_test_implementations(
        graph=graph,
        package_name=config.package_name,
        template_env=template_env,
        output_path=output_path,
    )
    output_path.write_text(content)
    logger.info(f"Generated runnable tests: {output_path.name}")


def _seal_package(
    graph: ComputationGraph,
    config: GenerationConfig,
) -> None:
    """Step 9: seal the generated package (D1).

    Order is the seal-well-formedness invariant (INV-3): every covered artifact must be
    final on disk before ``seal_package`` runs, and ``package_contract.json`` is written
    last, never in its own coverage.
    """
    from sysml_codegen.contracts import (
        DEFAULT_COVERAGE_POLICY,
        build_generation_manifest,
        build_model_contract,
        ensure_package_tree_is_link_free,
        seal_package,
    )
    from sysml_codegen.contracts.serialize import write_contract_json

    ensure_package_tree_is_link_free(config.output_path)
    contracts_dir = config.output_path / "contracts"
    contracts_dir.mkdir(parents=True, exist_ok=True)

    # (1) ModelContract — pure graph projection, written first.
    model_contract = build_model_contract(graph)
    write_contract_json(contracts_dir / "model_contract.json", model_contract)

    # (2) The canonical verifier, copied verbatim (INV-8 drift guard).
    verify_source = Path(__file__).resolve().parent.parent / "contracts" / "verify.py"
    shutil.copy(verify_source, contracts_dir / "verify.py")

    # (3) The generation manifest (Item 7): provenance the re-seal gate consults so a foreign
    # file cannot be laundered as codegen-produced. Built from the tree as it stands now —
    # ModelContract and verify.py present, manifest and seal not yet — so `codegen_produced`
    # is the covered tree minus handwritten/runtime plus the manifest's own path. Written
    # before the seal so it is itself a covered (hashed, frozen) artifact.
    manifest_entries = ensure_package_tree_is_link_free(config.output_path)
    manifest = build_generation_manifest(manifest_entries, DEFAULT_COVERAGE_POLICY)
    write_contract_json(contracts_dir / "generation_manifest.json", manifest)

    # (4)+(5) Seal everything now on disk (including the three files above) and write the
    # seal last — it is the only thing excluded from its own coverage.
    package_contract = seal_package(
        config.output_path, config.package_name, DEFAULT_COVERAGE_POLICY
    )
    write_contract_json(contracts_dir / "package_contract.json", package_contract)

