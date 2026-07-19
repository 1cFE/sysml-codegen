"""CLI entry point for sysml-codegen.

CRITICAL CHANGES:
- Parameterized all hardcoded values
- Removed CATF-specific references
- Package name is now a CLI argument
- Added install-commands subcommand for TEAx completion helper
"""

from __future__ import annotations

import argparse
import logging
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import jinja2

if TYPE_CHECKING:
    from sysml_codegen.generation import PipelineContext
    from sysml_codegen.generation.constraint_plan import ConstraintGenerationPlan
    from sysml_codegen.resolution.models import ComputationGraph, PipelineModule

# Note: Heavy imports moved inside run_codegen to avoid loading generation
# module at CLI import time. This keeps CLI startup fast.

logger = logging.getLogger(__name__)


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


# Commands available for installation
CODEGEN_COMMANDS = [
    "teax-completion.md",
]


def get_commands_dir() -> Path:
    """Get path to bundled commands directory.

    Path calculation:
    - __file__ = sysml-codegen/src/sysml_codegen/cli/__init__.py
    - parent.parent.parent.parent = sysml-codegen/
    - result = sysml-codegen/claude/commands/
    """
    package_root = Path(__file__).parent.parent.parent.parent
    return package_root / "claude" / "commands"


@dataclass
class GenerationConfig:
    """Configuration for code generation."""

    output_path: Path
    models_path: Path | None = None  # None when generating from a snapshot
    from_snapshot: Path | None = None  # snapshot to generate from (else live)
    package_name: str = "generated_code"  # Parameterized, was: fusion_simkit
    schema_class_name: str = "Params"  # Parameterized, was: FusionParams
    pipeline_name: str = "pipeline"  # Parameterized, was: catf_fusion
    overwrite: bool = False
    preserve_handwritten: bool = False
    smart_regen: bool = False
    design_path_filter: str = ""


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


def _get_template_env() -> jinja2.Environment:
    """Set up Jinja2 environment with package templates."""
    # Use __file__ to find templates relative to package
    template_dir = Path(__file__).parent.parent / "templates"
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(template_dir)),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def _get_python_path(module):
    """Get PythonModulePath from PipelineModule (all module types)."""
    from sysml_codegen.core.identifier_types import PythonModulePath, SysMLQualifiedName
    from sysml_codegen.generation.errors import unrenderable_module_kind_error
    from sysml_codegen.resolution.models import ModuleKind

    if module.module_kind in (ModuleKind.CONSTRAINT, ModuleKind.REPORT_AGGREGATOR):
        # module_type is already a Python-dotted path (D9 naming), not a SysML "::"
        # qualified name — derive directly rather than routing through from_sysml.
        # D9: "file stem lowercased" — the whole final segment, lowercased as-is.
        parts = module.module_type.split(".")
        return PythonModulePath(directory="/".join(parts[:-1]), filename=parts[-1].lower())
    if module.module_kind == ModuleKind.FORMULA:
        sysml_qn = f"{module.calc_def_qualified_name}::{module.calc_def_name}"
    elif module.module_kind == ModuleKind.AGGREGATION:
        sysml_qn = module.name.replace("__", "::")
    elif module.module_kind == ModuleKind.CALCULATION:
        sysml_qn = module.calc_def_qualified_name
    else:
        raise unrenderable_module_kind_error(module, "python-path")
    sqn = SysMLQualifiedName(sysml_qn)
    return PythonModulePath.from_sysml(sqn)


def _raw_source_name(module: PipelineModule) -> str:
    """Raw SysML spelling of a module, for duplicate-path provenance.

    After sanitize the colliding modules share a derived identifier, so the
    error must recover each raw name. For a FORMULA module that is the owner QN
    plus the raw attribute name; for a calc-usage module the raw calc-def QN.
    Both are raw (never sanitized) on every module type that can collide.
    """
    from sysml_codegen.generation.errors import unrenderable_module_kind_error
    from sysml_codegen.resolution.models import ModuleKind

    if module.module_kind == ModuleKind.FORMULA:
        return f"{module.calc_def_qualified_name}::{module.calc_def_name}"
    if module.module_kind in (ModuleKind.AGGREGATION, ModuleKind.CALCULATION):
        return module.calc_def_qualified_name or module.name
    if module.module_kind in (ModuleKind.CONSTRAINT, ModuleKind.REPORT_AGGREGATOR):
        return module.name
    raise unrenderable_module_kind_error(module, "raw-source-name")


def _check_duplicate_output_paths(modules: list[PipelineModule]) -> None:
    """Fail fast when two distinct SysML names sanitize to one output file.

    Run BEFORE _clear_output_directory so a collision never wipes or silently
    overwrites existing output. Covers the two write key spaces a
    sanitize-collision spans (D2):

    - Modules + stencils share the derived python path (stencils are
      `{filename}_impl.py` from the same _get_python_path output), so one path
      check covers both.
    - Schemas are keyed on `calc_def_name.lower()` (only multi-output modules
      reach the schema pass), a *different* key space: two calc defs whose names
      lower to one identifier collide on `x_output.py` even when module paths
      differ.

    Only a collision between *different* raw sources is an error -- multiple
    usages of one calc def legitimately derive the same path.
    """
    from sysml_codegen.generation import CodeGenerationError

    module_paths: dict[str, str] = {}
    for module in modules:
        path = _get_python_path(module).full_path
        raw = _raw_source_name(module)
        prior = module_paths.get(path)
        if prior is not None and prior != raw:
            raise CodeGenerationError(
                f"Duplicate output path: SysML names {prior!r} and {raw!r} both "
                f"derive modules/{path}. Rename one, or this would silently overwrite."
            )
        module_paths[path] = raw

    schema_sources: dict[str, str] = {}
    for module in modules:
        if len(module.outputs) < 2 or not module.calc_def_name:
            continue
        schema_file = f"{module.calc_def_name.lower()}_output.py"
        raw = _raw_source_name(module)
        prior = schema_sources.get(schema_file)
        if prior is not None and prior != raw:
            raise CodeGenerationError(
                f"Duplicate output path: SysML names {prior!r} and {raw!r} both "
                f"derive schemas/{schema_file}. Rename one, or this would silently "
                f"overwrite."
            )
        schema_sources[schema_file] = raw


def _reconcile_params_coverage(graph: ComputationGraph) -> None:
    """Reconcile the fell-through-valueless entry points (Item 7 / D4, M1).

    Runs at the generation boundary, BEFORE output is cleared, beside
    ``_check_duplicate_output_paths``. Partitions the fell-through, valueless
    entry points by whether pipeline wiring references them:

    - **unwired** remainder → one WARNING reconciliation summary (tracked
      residue; no runtime ``KeyError``). Logged FIRST so the digest reaches the
      operator even when generation aborts.
    - **wired** half → V11 hard error, generation aborts. The JSON never mints
      the key but the pipeline references it → guaranteed runtime ``KeyError``.

    Always strict (no escape-hatch flag). Raises ``CodeGenerationError`` on any
    wired violation, matching the ``_check_duplicate_output_paths`` fail-fast
    idiom (caught by ``run_codegen``, aborts the run).
    """
    from sysml_codegen.generation import CodeGenerationError
    from sysml_codegen.resolution.graph_builder import (
        collect_uncovered_params,
        collect_unwired_fallthrough,
    )

    # Reconciliation summary first (unwired remainder), so the operator sees the
    # digest even if the V11 raise below aborts the run.
    unwired = collect_unwired_fallthrough(graph)
    if unwired:
        logger.warning(
            "Unresolved after assembly: %d entry point(s) fell through and still "
            "lack a value (unwired): %s",
            len(unwired),
            unwired,
        )

    uncovered = collect_uncovered_params(graph)
    if uncovered:
        details = "; ".join(
            f"module '{u.module}' input '{u.input}' -> params key '{u.missing_key}'"
            for u in uncovered
        )
        raise CodeGenerationError(
            f"V11: {len(uncovered)} module input(s) reference a params key that no "
            f"parameter group provides — the JSON never mints the key, so the "
            f"pipeline will KeyError at load. Cause: an unresolved cross-part "
            f"reference not yet wired (Items 9-11) or a resolution bug. "
            f"Offenders: {details}"
        )


def _preflight_constraint_names(ctx: PipelineContext) -> None:
    """Validate both generated constraint scopes before a graph-aware boundary acts."""
    from sysml_codegen.generation.errors import validate_constraint_graph_or_raise

    validate_constraint_graph_or_raise(ctx.computation_graph)
    catalog = ctx.computation_graph.constraint_catalog
    if catalog is not None:
        from sysml_codegen.generation.modules import assert_unique_predicate_function_names

        assert_unique_predicate_function_names(catalog)


def _generate_schemas(
    ctx: PipelineContext,
    config: GenerationConfig,
    template_env: jinja2.Environment,
) -> None:
    """Generate Pydantic schemas for multi-output modules."""
    _preflight_constraint_names(ctx)
    from sysml_codegen.generation import generate_multioutput_model
    from sysml_codegen.resolution.models import ModuleKind

    schemas_dir = config.output_path / "schemas"

    multioutput_count = 0
    for module in ctx.computation_graph.modules:
        if module.module_kind in (ModuleKind.CONSTRAINT, ModuleKind.REPORT_AGGREGATOR):
            continue
        if len(module.outputs) < 2:
            continue
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

    # Item 7 / D4: per-package evidence schemas, gated on a constraint catalog existing
    # on the graph. A constraint-free corpus writes nothing here (INV-7).
    catalog = ctx.computation_graph.constraint_catalog
    if catalog is not None:
        template = template_env.get_template("constraint_types.py.jinja2")
        code = template.render()
        if not code.endswith("\n"):
            code += "\n"
        (schemas_dir / "constraint_types.py").write_text(code)
        logger.info("Generated constraint evidence schemas: constraint_types.py")


def _generate_modules(
    ctx: PipelineContext,
    config: GenerationConfig,
    template_env: jinja2.Environment,
    constraint_plan: ConstraintGenerationPlan,
) -> None:
    """Generate TEAx module wrappers for all module types (ADR-003 namespacing)."""
    _preflight_constraint_names(ctx)
    from sysml_codegen.generation import generate_teax_module
    from sysml_codegen.resolution.models import ModuleKind

    modules_dir = config.output_path / "modules"
    catalog = ctx.computation_graph.constraint_catalog
    staged: list[tuple[Path, str]] = []

    if constraint_plan.predicates_code is not None:
        staged.append(
            (modules_dir / "constraints" / "predicates.py", constraint_plan.predicates_code)
        )

    for module in ctx.computation_graph.modules:
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
    ctx: PipelineContext,
    config: GenerationConfig,
    template_env: jinja2.Environment,
) -> None:
    """Generate implementation stencils for all module types (ADR-003 namespacing)."""
    _preflight_constraint_names(ctx)
    from sysml_codegen.generation import (
        backup_implementation,
        generate_implementation,
        should_regenerate_stencil,
    )
    from sysml_codegen.resolution.models import ModuleKind

    handwritten_dir = config.output_path / "handwritten"
    backup_dir = handwritten_dir / "backup"

    stats = {"new": 0, "preserved": 0, "regenerated": 0}

    for module in ctx.computation_graph.modules:
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
    ctx: PipelineContext,
    config: GenerationConfig,
    template_env: jinja2.Environment,
) -> None:
    """Generate pipeline YAML from computation graph."""
    _preflight_constraint_names(ctx)
    from sysml_codegen.generation import generate_pipeline_yaml

    pipelines_dir = config.output_path / "pipelines"
    output_path = pipelines_dir / f"{config.pipeline_name}.yaml"

    yaml_content = generate_pipeline_yaml(
        graph=ctx.computation_graph,
        package_name=config.package_name,
        template_env=template_env,
    )
    if yaml_content:
        output_path.write_text(yaml_content)
        logger.debug(f"Generated pipeline: {output_path}")

    logger.info(f"Generated pipeline configuration: {config.pipeline_name}.yaml")


def _generate_registry(
    ctx: PipelineContext,
    config: GenerationConfig,
    template_env: jinja2.Environment,
) -> None:
    """Generate registry function in __init__.py."""
    _preflight_constraint_names(ctx)
    from sysml_codegen.generation import generate_registry
    from sysml_codegen.generation.registry import _collect_exit_point_primitive_types

    output_path = config.output_path / "__init__.py"

    exit_point_types = _collect_exit_point_primitive_types(ctx.computation_graph.modules)

    code = generate_registry(
        graph=ctx.computation_graph,
        package_name=config.package_name,
        template_env=template_env,
        output_path=output_path,
        exit_point_primitive_types=exit_point_types,
    )
    if code:
        output_path.write_text(code)
        logger.debug(f"Generated registry: {output_path}")

    logger.info(f"Generated module registry with {len(ctx.computation_graph.modules)} modules")


def _generate_entry_points(
    ctx: PipelineContext,
    config: GenerationConfig,
    template_env: jinja2.Environment,
) -> None:
    """Generate entry point parameter group schemas and JSON templates."""
    _preflight_constraint_names(ctx)
    from sysml_codegen.generation import (
        generate_all_derived_jsons_from_graph,
        generate_all_derived_schemas_from_graph,
    )

    entry_point_groups = ctx.computation_graph.entry_point_groups

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
    ctx: PipelineContext,
    config: GenerationConfig,
) -> None:
    """Generate implementation backlog report."""
    _preflight_constraint_names(ctx)
    from sysml_codegen.generation import generate_backlog_report

    output_path = config.output_path / "IMPLEMENTATION_BACKLOG.md"

    markdown = generate_backlog_report(
        ctx.computation_graph,
        output_path,
        config.package_name,
    )
    if markdown:
        output_path.write_text(markdown)
        logger.info(f"Generated implementation backlog: {output_path.name}")


def _generate_tests(
    ctx: PipelineContext,
    config: GenerationConfig,
    template_env: jinja2.Environment,
) -> None:
    """Generate runnable test file for implementations."""
    _preflight_constraint_names(ctx)
    from sysml_codegen.generation import generate_test_implementations

    tests_dir = config.output_path / "tests"
    tests_dir.mkdir(parents=True, exist_ok=True)

    output_path = tests_dir / "test_implementations_runnable.py"

    content = generate_test_implementations(
        graph=ctx.computation_graph,
        package_name=config.package_name,
        template_env=template_env,
        output_path=output_path,
    )
    output_path.write_text(content)
    logger.info(f"Generated runnable tests: {output_path.name}")


def _seal_package(
    ctx: PipelineContext,
    config: GenerationConfig,
) -> None:
    """Step 9: seal the generated package (D1).

    Order is the seal-well-formedness invariant (INV-3): every covered artifact must be
    final on disk before ``seal_package`` runs, and ``package_contract.json`` is written
    last, never in its own coverage.
    """
    _preflight_constraint_names(ctx)
    from sysml_codegen.contracts import (
        DEFAULT_COVERAGE_POLICY,
        build_model_contract,
        ensure_package_tree_is_link_free,
        seal_package,
    )
    from sysml_codegen.contracts.serialize import write_contract_json

    ensure_package_tree_is_link_free(config.output_path)
    contracts_dir = config.output_path / "contracts"
    contracts_dir.mkdir(parents=True, exist_ok=True)

    # (1) ModelContract — pure graph projection, written first.
    model_contract = build_model_contract(ctx.computation_graph)
    write_contract_json(contracts_dir / "model_contract.json", model_contract)

    # (2) The canonical verifier, copied verbatim (INV-8 drift guard).
    verify_source = Path(__file__).resolve().parent.parent / "contracts" / "verify.py"
    shutil.copy(verify_source, contracts_dir / "verify.py")

    # (3)+(4) Seal everything now on disk (including the two files above) and write the
    # seal last — it is the only thing excluded from its own coverage.
    package_contract = seal_package(
        config.output_path, config.package_name, DEFAULT_COVERAGE_POLICY
    )
    write_contract_json(contracts_dir / "package_contract.json", package_contract)


def cmd_generate(args: argparse.Namespace) -> int:
    """Run the code generation command."""
    # Configure logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")

    # Validate agentic-mbse is installed
    try:
        import agentic_mbse

        logger.debug(f"agentic-mbse version: {agentic_mbse.__version__}")
    except ImportError:
        logger.error("agentic-mbse is not installed. Please install it first.")
        return 1

    # --design-path-filter is baked into the snapshot at capture, so re-applying
    # it at generation is meaningless — reject rather than silently no-op (V6).
    if args.from_snapshot is not None and args.design_path_filter:
        logger.error(
            "--design-path-filter cannot be combined with --from-snapshot "
            "(the filter is baked into the snapshot at capture)."
        )
        return 1

    config = GenerationConfig(
        models_path=args.models,
        from_snapshot=args.from_snapshot,
        output_path=args.output,
        package_name=args.package_name,
        schema_class_name=args.schema_class,
        pipeline_name=args.pipeline_name,
        overwrite=args.overwrite,
        preserve_handwritten=args.preserve_handwritten,
        smart_regen=args.smart_regen,
        design_path_filter=args.design_path_filter,
    )

    success = run_codegen(config)
    return 0 if success else 1


def cmd_snapshot(args: argparse.Namespace) -> int:
    """Capture a versioned extraction snapshot from live models."""
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")

    try:
        import agentic_mbse  # noqa: F401
    except ImportError:
        logger.error("agentic-mbse is not installed. Please install it first.")
        return 1

    from sysml_codegen.snapshot import capture_snapshot

    models_path: Path = args.models
    output_path: Path = args.output or (models_path / "extraction_snapshot.json")
    out = capture_snapshot([models_path], output_path, design_path_filter=args.design_path_filter)
    logger.info(f"Wrote snapshot to {out}")
    return 0


def cmd_seal(args: argparse.Namespace) -> int:
    """Re-seal an existing generated package (D2).

    Recomputes the ``PackageContract`` only — graph-free, license-free — over a package
    directory that has already been sealed once by ``generate``. Use this after editing a
    handwritten stencil to make the seal match the edited bytes again.
    """
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")

    from sysml_codegen.contracts import (
        DEFAULT_COVERAGE_POLICY,
        PackageSealError,
        ensure_package_tree_is_link_free,
        seal_package,
    )
    from sysml_codegen.contracts.serialize import write_contract_json

    package_dir: Path = args.package_dir
    try:
        ensure_package_tree_is_link_free(package_dir)
    except (PackageSealError, OSError) as error:
        logger.error(f"Package sealing failed: {error}")
        return 1

    model_contract_path = package_dir / "contracts" / "model_contract.json"
    if not model_contract_path.is_file():
        logger.error(
            f"{model_contract_path} not found. `seal` re-seals a package `generate` has "
            "already sealed once (D2) — it does not build a ModelContract from scratch."
        )
        return 1

    try:
        package_contract = seal_package(package_dir, args.package_name, DEFAULT_COVERAGE_POLICY)
    except (PackageSealError, OSError) as error:
        logger.error(f"Package sealing failed: {error}")
        return 1
    write_contract_json(package_dir / "contracts" / "package_contract.json", package_contract)
    logger.info(f"Re-sealed {package_dir} as {args.package_name!r}")
    return 0


def cmd_install_commands(args: argparse.Namespace) -> int:
    """Install teax-completion helper command to a project."""
    if args.list:
        print("Available codegen helper commands:")
        for cmd in CODEGEN_COMMANDS:
            print(f"  - {cmd}")
        return 0

    target_dir = Path(args.directory).resolve()
    if not target_dir.is_dir():
        print(f"Error: {target_dir} is not a directory", file=sys.stderr)
        return 1

    commands_dir = target_dir / ".claude" / "commands"
    commands_dir.mkdir(parents=True, exist_ok=True)

    source_dir = get_commands_dir()
    copied = 0
    for cmd in CODEGEN_COMMANDS:
        src = source_dir / cmd
        dst = commands_dir / cmd
        if dst.exists() and not args.force:
            print(f"Skipping {cmd} (exists, use --force to overwrite)")
            continue
        if src.exists():
            shutil.copy(src, dst)
            print(f"Installed {cmd}")
            copied += 1
        else:
            print(f"Warning: {cmd} not found in package", file=sys.stderr)

    print(f"Installed {copied} command(s) to {commands_dir}")
    return 0


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="SysML v2 code generation tools")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Generate subcommand
    gen_parser = subparsers.add_parser("generate", help="Generate Python code from SysML v2 models")
    # Exactly one extraction input: live --models or a captured --from-snapshot
    # (both-forbidden / neither-forbidden come free from a required group — INV-7).
    gen_input = gen_parser.add_mutually_exclusive_group(required=True)
    gen_input.add_argument(
        "--models", "-m", type=Path, help="Path to SysML model directory or file (live extraction)"
    )
    gen_input.add_argument(
        "--from-snapshot",
        type=Path,
        help="Path to a captured extraction snapshot (license-free generation)",
    )
    gen_parser.add_argument(
        "--output", "-o", type=Path, required=True, help="Output directory for generated code"
    )
    gen_parser.add_argument(
        "--package-name",
        type=str,
        default="generated_code",
        help="Python package name for generated code (default: generated_code)",
    )
    gen_parser.add_argument(
        "--schema-class",
        type=str,
        default="Params",
        help="Name for the main schema class (default: Params)",
    )
    gen_parser.add_argument(
        "--pipeline-name",
        type=str,
        default="pipeline",
        help="Name for the pipeline configuration (default: pipeline)",
    )
    gen_parser.add_argument("--overwrite", action="store_true", help="Overwrite existing files")
    gen_parser.add_argument(
        "--preserve-handwritten",
        action="store_true",
        help="Preserve handwritten implementations during regeneration",
    )
    gen_parser.add_argument(
        "--smart-regen", action="store_true", help="Smart regeneration with signature comparison"
    )
    gen_parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    gen_parser.add_argument(
        "--design-path-filter",
        type=str,
        default="",
        help="Substring filter for design file paths (default: accept all files)",
    )
    gen_parser.set_defaults(func=cmd_generate)

    # Snapshot subcommand — capture a versioned snapshot from live models (D5)
    snap_parser = subparsers.add_parser(
        "snapshot", help="Capture a versioned extraction snapshot from live models"
    )
    snap_parser.add_argument(
        "--models", "-m", type=Path, required=True, help="Path to SysML model directory or file"
    )
    snap_parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=None,
        help="Snapshot output path (default: <models>/extraction_snapshot.json)",
    )
    snap_parser.add_argument(
        "--design-path-filter",
        type=str,
        default="",
        help="Substring filter for design file paths (baked into the snapshot)",
    )
    snap_parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    snap_parser.set_defaults(func=cmd_snapshot)

    # Seal subcommand — re-seal a generated package in place (D1/D2)
    seal_parser = subparsers.add_parser(
        "seal", help="Re-seal a generated package (recomputes the PackageContract only)"
    )
    seal_parser.add_argument(
        "package_dir", type=Path, help="Path to the generated package directory"
    )
    seal_parser.add_argument(
        "--package-name", type=str, required=True, help="Package name to record in the seal"
    )
    seal_parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    seal_parser.set_defaults(func=cmd_seal)

    # Install-commands subcommand
    install_parser = subparsers.add_parser(
        "install-commands", help="Install teax-completion helper command"
    )
    install_parser.add_argument(
        "directory", nargs="?", default=".", help="Target directory (default: current directory)"
    )
    install_parser.add_argument(
        "--list", action="store_true", help="List available commands without installing"
    )
    install_parser.add_argument("--force", action="store_true", help="Overwrite existing files")
    install_parser.set_defaults(func=cmd_install_commands)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    sys.exit(args.func(args))


def run_codegen(config: GenerationConfig) -> bool:
    """Run the code generation pipeline.

    Args:
        config: Generation configuration with paths and options.

    Returns:
        True if generation succeeded, False otherwise.
    """
    from sysml_codegen.contracts import PackageSealError, ensure_package_tree_is_link_free
    from sysml_codegen.generation import (
        CodeGenerationError,
        SysMLParsingError,
    )
    from sysml_codegen.generation.constraint_plan import build_constraint_generation_plan
    from sysml_codegen.orchestration.pipeline_builder import build_pipeline_context

    source = config.from_snapshot if config.from_snapshot is not None else config.models_path
    logger.info(f"Generating code from {source}")
    logger.info(f"Output to {config.output_path}")
    logger.info(f"Package name: {config.package_name}")

    try:
        # Step 1: Build pipeline context — from a snapshot (license-free) or from
        # live extraction (7-step initialization). Both converge on PipelineContext.
        logger.info("Building pipeline context...")
        if config.from_snapshot is not None:
            from sysml_codegen.orchestration.snapshot_context import (
                build_pipeline_context_from_snapshot,
            )

            ctx = build_pipeline_context_from_snapshot(config.from_snapshot)
        else:
            assert config.models_path is not None  # guaranteed by the CLI group
            ctx = build_pipeline_context(
                [config.models_path],
                design_path_filter=config.design_path_filter,
            )
        logger.info(f"Extracted {len(ctx.calc_defs)} calculation definitions")
        logger.info(f"Built computation graph with {len(ctx.computation_graph.modules)} modules")

        # Validate both generated constraint scopes before overwrite clearing or output creation.
        _preflight_constraint_names(ctx)

        # Step 1.5: Fail fast on a sanitize-collision BEFORE clearing output, so a
        # duplicate path never wipes or silently overwrites existing files.
        _check_duplicate_output_paths(ctx.computation_graph.modules)

        # Step 1.6: Params-coverage reconciliation (Item 7 / D4, M1). Always
        # strict — logs the unwired-remainder summary, then raises V11 on any
        # wired fell-through-valueless input. Before output clear, like 1.5.
        _reconcile_params_coverage(ctx.computation_graph)

        try:
            ensure_package_tree_is_link_free(config.output_path)
        except (PackageSealError, OSError) as error:
            logger.error(f"Package sealing failed: {error}")
            return False

        # Build every constraint body and wrapper while the target tree is still untouched.
        template_env = _get_template_env()
        constraint_plan = build_constraint_generation_plan(ctx, template_env, config.package_name)

        # Step 2: Clear and setup output directories
        if config.overwrite:
            logger.info("Clearing existing output directory...")
            _clear_output_directory(config)

        logger.info("Creating output directory structure...")
        _setup_output_directories(config)

        # Step 3: Generate primitives.py (required for module imports)
        _generate_primitives(config)

        # Step 5: Generate schemas
        logger.info("Generating schemas...")
        _generate_schemas(ctx, config, template_env)

        # Step 6: Generate modules and stencils (all types unified via graph)
        logger.info("Generating TEAx module wrappers...")
        _generate_modules(ctx, config, template_env, constraint_plan)

        logger.info("Generating implementation stencils...")
        _generate_stencils(ctx, config, template_env)

        # Step 7: Generate pipeline and registry
        logger.info("Generating pipeline configuration...")
        _generate_pipeline(ctx, config, template_env)

        logger.info("Generating module registry...")
        _generate_registry(ctx, config, template_env)

        # Step 8: Generate entry points and extras
        logger.info("Generating entry point schemas and JSON templates...")
        _generate_entry_points(ctx, config, template_env)

        logger.info("Generating implementation backlog...")
        _generate_backlog(ctx, config)

        logger.info("Generating runnable tests...")
        _generate_tests(ctx, config, template_env)

        # Step 9: Seal the package (D1) — over final on-disk state, both live and
        # from-snapshot paths alike (D8).
        logger.info("Sealing package...")
        try:
            _seal_package(ctx, config)
        except (PackageSealError, OSError) as error:
            logger.error(f"Package sealing failed: {error}")
            return False

        logger.info("Code generation complete")
        return True

    except SysMLParsingError as e:
        logger.error(f"SysML parsing failed: {e}")
        return False
    except CodeGenerationError as e:
        logger.error(
            f"Code generation failed: {e}",
            extra={"constraint_name_safety": e.name_safety_violation},
        )
        return False
    except Exception as e:
        import traceback

        logger.error(f"Unexpected error: {e}")
        logger.debug(traceback.format_exc())
        return False


__all__ = [
    "main",
    "run_codegen",
    "GenerationConfig",
    "cmd_generate",
    "cmd_install_commands",
    "CODEGEN_COMMANDS",
]
