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

from sysml_codegen.analysis.dependency_backtracker import DependencyBacktracker
from sysml_codegen.analysis.parameter_groups import (
    ParameterGroupDeriver,
    extract_design_attributes,
)
from sysml_codegen.extraction.extractor import SysMLDataExtractor
from sysml_codegen.extraction.usage_extractor import extract_calculation_usages
from sysml_codegen.resolution.graph_builder import build_computation_graph

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
    logger.info(f"Generating code from {config.models_path}")
    logger.info(f"Output to {config.output_path}")
    logger.info(f"Package name: {config.package_name}")

    # Step 1: Parse SysML models
    extractor = SysMLDataExtractor([config.models_path])
    if not extractor.load_models():
        logger.error("Failed to load SysML models")
        return False

    # Step 2: Extract calculation definitions
    calc_defs = extractor.extract_calculation_definitions()
    logger.info(f"Extracted {len(calc_defs)} calculation definitions")

    # Step 3: Extract calculation usages
    usages, report = extract_calculation_usages(
        extractor.model,
        known_calc_defs={cd.name for cd in calc_defs},
        calc_defs=calc_defs,
    )
    logger.info(f"Extracted {len(usages)} calculation usages")

    # Step 4: Extract design attributes
    design_attrs = extract_design_attributes(extractor.model)

    # Step 5: Run dependency backtracking
    backtracker = DependencyBacktracker(usages, calc_defs, design_attrs)
    result = backtracker.find_required_modules([], include_all=True)

    # Step 6: Build computation graph
    group_deriver = ParameterGroupDeriver(design_attrs, usages, calc_defs)
    graph = build_computation_graph(result, calc_defs, design_attrs, group_deriver)

    # Step 7: Generate code
    # TODO: Implement code generation using templates
    # This requires:
    # - Template loading from sysml_codegen.templates
    # - Module generation via sysml_codegen.generation.modules
    # - Pipeline generation via sysml_codegen.generation.pipeline
    # - Registry generation via sysml_codegen.generation.registry
    #
    # The implementation should:
    # - Parameterize package_name in all template contexts
    # - Parameterize schema_class_name (was: "FusionParams")
    # - Parameterize pipeline_name (was: "catf_fusion")
    # - Use config.output_path instead of hardcoded paths
    # - Run mypy/ruff on generated code if available

    logger.info(f"Computation graph built with {len(graph.modules)} modules")
    logger.info("Code generation complete (stub - full generation TODO)")
    return True


__all__ = [
    "main",
    "run_codegen",
    "GenerationConfig",
    "cmd_generate",
    "cmd_install_commands",
    "CODEGEN_COMMANDS",
]
