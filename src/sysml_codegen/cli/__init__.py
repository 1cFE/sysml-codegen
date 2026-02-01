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

# Note: Heavy imports moved inside run_codegen to avoid loading generation
# module at CLI import time. This keeps CLI startup fast.

logger = logging.getLogger(__name__)

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

    models_path: Path
    output_path: Path
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


def _generate_schemas(
    ctx: PipelineContext,
    config: GenerationConfig,
    template_env: jinja2.Environment,
) -> None:
    """Generate Pydantic schemas using multioutput helper."""
    from sysml_codegen.generation import generate_multioutput_model, should_use_multioutput

    schemas_dir = config.output_path / "schemas"

    # Generate multi-output schemas
    multioutput_count = 0
    for calc_def in ctx.calc_defs:
        if should_use_multioutput(calc_def):
            output_path = schemas_dir / f"{calc_def.name.lower()}_output.py"
            code = generate_multioutput_model(
                calc_def,
                template_env,
                output_path,
                package_name=config.package_name,
            )
            if code:
                output_path.write_text(code)
                multioutput_count += 1
                logger.debug(f"Generated schema: {output_path.name}")

    logger.info(f"Generated {multioutput_count} multi-output schemas")


def _generate_modules(
    ctx: PipelineContext,
    config: GenerationConfig,
    template_env: jinja2.Environment,
) -> None:
    """Generate TEAx module wrappers (ADR-003 namespacing)."""
    from sysml_codegen.generation import generate_teax_module
    from sysml_codegen.resolution.identifier_types import PythonModulePath, SysMLQualifiedName

    modules_dir = config.output_path / "modules"
    created_namespaces: set[str] = set()
    module_count = 0

    for calc_def in ctx.calc_defs:
        # Skip calc_defs without outputs (can't generate meaningful module)
        if not calc_def.output_attributes:
            logger.debug(f"Skipping {calc_def.name}: no output attributes")
            continue

        # ADR-003: Derive nested path from qualified name
        sqn = SysMLQualifiedName(calc_def.qualified_name)
        python_path = PythonModulePath.from_sysml(sqn)

        # Create namespace subdirectory if needed
        if python_path.directory:
            namespace_dir = modules_dir / python_path.directory
            namespace_dir.mkdir(parents=True, exist_ok=True)

            if python_path.directory not in created_namespaces:
                init_file = namespace_dir / "__init__.py"
                if not init_file.exists():
                    init_file.write_text('"""Namespace package for generated modules."""\n')
                created_namespaces.add(python_path.directory)

        output_path = modules_dir / python_path.full_path
        code = generate_teax_module(
            calc_def,
            template_env,
            output_path,
            config.package_name,
        )
        if code:
            output_path.write_text(code)
            module_count += 1
            logger.debug(f"Generated module: {output_path}")

    logger.info(f"Generated {module_count} TEAx module wrappers")


def _generate_stencils(
    ctx: PipelineContext,
    config: GenerationConfig,
    template_env: jinja2.Environment,
) -> None:
    """Generate implementation stencils (ADR-003 namespacing)."""
    from sysml_codegen.generation import (
        backup_implementation,
        generate_implementation_stencil,
        should_regenerate_stencil,
    )
    from sysml_codegen.resolution.identifier_types import (
        PythonModulePath,
        SysMLQualifiedName,
    )

    handwritten_dir = config.output_path / "handwritten"
    backup_dir = handwritten_dir / "backup"
    created_namespaces: set[str] = set()

    stats = {"new": 0, "preserved": 0, "regenerated": 0}

    for calc_def in ctx.calc_defs:
        # Skip calc_defs without outputs (nothing to implement)
        if not calc_def.output_attributes:
            continue

        sqn = SysMLQualifiedName(calc_def.qualified_name)
        python_path = PythonModulePath.from_sysml(sqn)

        # Create namespace subdirectory if needed
        if python_path.directory:
            namespace_dir = handwritten_dir / python_path.directory
            namespace_dir.mkdir(parents=True, exist_ok=True)

            if python_path.directory not in created_namespaces:
                init_file = namespace_dir / "__init__.py"
                if not init_file.exists():
                    init_file.write_text('"""Handwritten implementations."""\n')
                created_namespaces.add(python_path.directory)

            output_path = namespace_dir / f"{python_path.filename}_impl.py"
        else:
            output_path = handwritten_dir / f"{python_path.filename}_impl.py"

        # Smart regeneration logic
        if config.smart_regen and output_path.exists():
            should_regen, reason = should_regenerate_stencil(calc_def, output_path)
            if should_regen:
                backup_implementation(output_path, backup_dir)
                code = generate_implementation_stencil(
                    calc_def, template_env, output_path, config.package_name
                )
                if code:
                    output_path.write_text(code)
                stats["regenerated"] += 1
                logger.debug(f"Regenerated stencil ({reason}): {output_path.name}")
            else:
                stats["preserved"] += 1
                logger.debug(f"Preserved stencil ({reason}): {output_path.name}")
        elif config.preserve_handwritten and output_path.exists():
            stats["preserved"] += 1
            logger.debug(f"Preserved existing stencil: {output_path.name}")
        else:
            code = generate_implementation_stencil(
                calc_def, template_env, output_path, config.package_name
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
    from sysml_codegen.generation import generate_registry_function
    from sysml_codegen.generation.registry import _collect_exit_point_primitive_types

    output_path = config.output_path / "__init__.py"

    # Filter calc_defs to only those with outputs (matching module generation)
    calc_defs_with_outputs = [
        cd for cd in ctx.calc_defs if cd.output_attributes
    ]

    exit_point_types = _collect_exit_point_primitive_types(ctx.computation_graph.modules)

    code = generate_registry_function(
        calc_defs=calc_defs_with_outputs,
        package_name=config.package_name,
        template_env=template_env,
        output_path=output_path,
        entry_point_groups=ctx.computation_graph.entry_point_groups,
        exit_point_primitive_types=exit_point_types,
    )
    if code:
        output_path.write_text(code)
        logger.debug(f"Generated registry: {output_path}")

    logger.info(f"Generated module registry with {len(calc_defs_with_outputs)} modules")


def _generate_entry_points(
    ctx: PipelineContext,
    config: GenerationConfig,
    template_env: jinja2.Environment,
) -> None:
    """Generate entry point parameter group schemas and JSON templates."""
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
    from sysml_codegen.generation import generate_backlog_report

    output_path = config.output_path / "IMPLEMENTATION_BACKLOG.md"

    # Filter to calc_defs with outputs (matching module generation)
    calc_defs_with_outputs = [
        cd for cd in ctx.calc_defs if cd.output_attributes
    ]

    markdown = generate_backlog_report(
        calc_defs_with_outputs,
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
    from sysml_codegen.generation import generate_test_implementations

    tests_dir = config.output_path / "tests"
    tests_dir.mkdir(parents=True, exist_ok=True)

    output_path = tests_dir / "test_implementations_runnable.py"

    # Filter to calc_defs with outputs (matching module generation)
    calc_defs_with_outputs = [
        cd for cd in ctx.calc_defs if cd.output_attributes
    ]

    content = generate_test_implementations(
        calc_defs=calc_defs_with_outputs,
        package_name=config.package_name,
        template_env=template_env,
        output_path=output_path,
    )
    output_path.write_text(content)
    logger.info(f"Generated runnable tests: {output_path.name}")


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

    config = GenerationConfig(
        models_path=args.models,
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
    parser = argparse.ArgumentParser(
        description="SysML v2 code generation tools"
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Generate subcommand
    gen_parser = subparsers.add_parser(
        "generate",
        help="Generate Python code from SysML v2 models"
    )
    gen_parser.add_argument(
        "--models", "-m",
        type=Path,
        required=True,
        help="Path to SysML model directory or file"
    )
    gen_parser.add_argument(
        "--output", "-o",
        type=Path,
        required=True,
        help="Output directory for generated code"
    )
    gen_parser.add_argument(
        "--package-name",
        type=str,
        default="generated_code",
        help="Python package name for generated code (default: generated_code)"
    )
    gen_parser.add_argument(
        "--schema-class",
        type=str,
        default="Params",
        help="Name for the main schema class (default: Params)"
    )
    gen_parser.add_argument(
        "--pipeline-name",
        type=str,
        default="pipeline",
        help="Name for the pipeline configuration (default: pipeline)"
    )
    gen_parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing files"
    )
    gen_parser.add_argument(
        "--preserve-handwritten",
        action="store_true",
        help="Preserve handwritten implementations during regeneration"
    )
    gen_parser.add_argument(
        "--smart-regen",
        action="store_true",
        help="Smart regeneration with signature comparison"
    )
    gen_parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    gen_parser.add_argument(
        "--design-path-filter",
        type=str,
        default="",
        help="Substring filter for design file paths (default: accept all files)"
    )
    gen_parser.set_defaults(func=cmd_generate)

    # Install-commands subcommand
    install_parser = subparsers.add_parser(
        "install-commands",
        help="Install teax-completion helper command"
    )
    install_parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Target directory (default: current directory)"
    )
    install_parser.add_argument(
        "--list",
        action="store_true",
        help="List available commands without installing"
    )
    install_parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing files"
    )
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
    from sysml_codegen.generation import (
        CodeGenerationError,
        SysMLParsingError,
        build_pipeline_context,
    )

    logger.info(f"Generating code from {config.models_path}")
    logger.info(f"Output to {config.output_path}")
    logger.info(f"Package name: {config.package_name}")

    try:
        # Step 1: Build pipeline context (7-step initialization)
        logger.info("Building pipeline context...")
        ctx = build_pipeline_context(
            [config.models_path],
            design_path_filter=config.design_path_filter,
        )
        logger.info(f"Extracted {len(ctx.calc_defs)} calculation definitions")
        logger.info(f"Built computation graph with {len(ctx.computation_graph.modules)} modules")

        # Step 2: Clear and setup output directories
        if config.overwrite:
            logger.info("Clearing existing output directory...")
            _clear_output_directory(config)

        logger.info("Creating output directory structure...")
        _setup_output_directories(config)

        # Step 3: Generate primitives.py (required for module imports)
        _generate_primitives(config)

        # Step 4: Setup Jinja2 template environment
        template_env = _get_template_env()

        # Step 5: Generate schemas
        logger.info("Generating schemas...")
        _generate_schemas(ctx, config, template_env)

        # Step 6: Generate modules and stencils
        logger.info("Generating TEAx module wrappers...")
        _generate_modules(ctx, config, template_env)

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

        logger.info("Code generation complete")
        return True

    except SysMLParsingError as e:
        logger.error(f"SysML parsing failed: {e}")
        return False
    except CodeGenerationError as e:
        logger.error(f"Code generation failed: {e}")
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
