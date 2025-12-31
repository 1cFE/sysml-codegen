"""CLI entry point for sysml-codegen.

CRITICAL CHANGES:
- Parameterized all hardcoded values
- Removed CATF-specific references
- Package name is now a CLI argument
"""

from __future__ import annotations

import argparse
import logging
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


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Generate Python code from SysML v2 models"
    )
    parser.add_argument(
        "--models", "-m",
        type=Path,
        required=True,
        help="Path to SysML model directory or file"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        required=True,
        help="Output directory for generated code"
    )
    parser.add_argument(
        "--package-name",
        type=str,
        default="generated_code",
        help="Python package name for generated code (default: generated_code)"
    )
    parser.add_argument(
        "--schema-class",
        type=str,
        default="Params",
        help="Name for the main schema class (default: Params)"
    )
    parser.add_argument(
        "--pipeline-name",
        type=str,
        default="pipeline",
        help="Name for the pipeline configuration (default: pipeline)"
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing files"
    )
    parser.add_argument(
        "--preserve-handwritten",
        action="store_true",
        help="Preserve handwritten implementations during regeneration"
    )
    parser.add_argument(
        "--smart-regen",
        action="store_true",
        help="Smart regeneration with signature comparison"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )

    args = parser.parse_args()

    # Configure logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")

    # Validate agentic-mbse is installed
    try:
        import agentic_mbse
        logger.debug(f"agentic-mbse version: {agentic_mbse.__version__}")
    except ImportError:
        logger.error("agentic-mbse is not installed. Please install it first.")
        sys.exit(1)

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
    sys.exit(0 if success else 1)


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


__all__ = ["main", "run_codegen", "GenerationConfig"]
