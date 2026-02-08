"""Shared initialization for codegen scripts.

Provides the canonical initialization sequence used by codegen scripts.
This module consolidates the 7-step initialization sequence that was
previously duplicated across multiple scripts, ensuring consistent
behavior and reducing maintenance burden.
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# UPDATED: Import from sysml_codegen package
from sysml_codegen.analysis.dependency_backtracker import (
    BacktrackingResult,
    DependencyBacktracker,
)
from sysml_codegen.analysis.parameter_groups import (
    DesignAttributeData,
    ParameterGroupDeriver,
    extract_design_attributes,
)
from sysml_codegen.extraction.data_models import CalculationDefinitionData
from sysml_codegen.extraction.expression_compiler import (
    CalcDefCompilationResult,
    compile_calc_def,
)
from sysml_codegen.extraction.usage_extractor import CalcUsageData, extract_calculation_usages
from sysml_codegen.resolution.graph_builder import build_computation_graph
from sysml_codegen.resolution.models import ComputationGraph

logger = logging.getLogger(__name__)


class SysMLParsingError(Exception):
    """Error during SysML model parsing.

    Raised when:
    - Model paths do not exist
    - SysML syntax errors in model files
    - Model loading fails for any reason
    """

    pass


class CodeGenerationError(Exception):
    """Error during code generation.

    Raised when:
    - No calculation definitions found in models
    - Required model elements are missing
    - Generation process fails
    """

    pass


@dataclass
class PipelineContext:
    """Complete context for pipeline code generation.

    This dataclass encapsulates all extracted data and components
    needed for code generation, ensuring consistent initialization
    across all codegen scripts.

    Attributes:
        extractor: SysMLDataExtractor with loaded models
        calc_defs: Extracted calculation definitions
        calc_usages: Extracted calculation usages with binding info
        design_attributes: Design attributes by source file
        group_deriver: Parameter grouping logic
        backtracker: Dependency analysis component
        backtracking_result: Result of dependency backtracking
        computation_graph: The single source of truth for pipeline structure
    """

    extractor: Any  # SysMLDataExtractor - use Any to avoid circular import
    calc_defs: list[CalculationDefinitionData]
    calc_usages: list[CalcUsageData]
    design_attributes: dict[Path, list[DesignAttributeData]]
    group_deriver: ParameterGroupDeriver
    backtracker: DependencyBacktracker
    backtracking_result: BacktrackingResult
    computation_graph: ComputationGraph

    # Expression compilation results keyed by calc_def.name.
    # Contains per-output CompilationResult with Python expression strings.
    compilation_results: dict[str, CalcDefCompilationResult] = field(default_factory=dict)


def build_pipeline_context(
    model_paths: list[Path],
    targets: list[str] | None = None,
    include_all: bool = True,
    design_path_filter: str = "",
) -> PipelineContext:
    """Build complete pipeline context from SysML models.

    This is the canonical initialization sequence used by all codegen scripts.
    It performs the following 7-step sequence:

    1. Load models via SysMLDataExtractor
    2. Extract calculation definitions
    3. Extract calculation usages with enhanced algorithm param detection
    4. Extract design attributes for group derivation
    5. Create parameter group deriver
    6. Create backtracker and run dependency analysis
    7. Build ComputationGraph (single source of truth)

    Args:
        model_paths: Paths to SysML model directories (library + designs)
        targets: Target outputs for subset generation (e.g., ["net_electric.p_net"])
        include_all: If True, include all usages; if False, only those needed for targets

    Returns:
        PipelineContext with all components initialized

    Raises:
        SysMLParsingError: If model loading fails
        CodeGenerationError: If no calculation definitions found
    """
    # Late import to avoid circular import
    from sysml_codegen.extraction.extractor import SysMLDataExtractor

    # Step 1: Load models via SysMLDataExtractor
    extractor = SysMLDataExtractor(model_paths)
    try:
        if not extractor.load_models():
            raise SysMLParsingError(
                f"Failed to load SysML models from: {[str(p) for p in model_paths]}"
            )
    except ValueError as e:
        raise SysMLParsingError(f"Failed to load SysML models: {e}") from e

    # Step 2: Extract calculation definitions
    calc_defs = extractor.extract_calculation_definitions()
    if not calc_defs:
        raise CodeGenerationError(
            "No calculation definitions found in models. "
            "Ensure library models contain calc definitions."
        )

    # Step 3: Extract calculation usages with enhanced algorithm param detection
    calc_usages, _report = extract_calculation_usages(
        extractor.model,
        calc_defs=calc_defs,
    )

    # Step 4: Extract design attributes for group derivation
    design_attrs = extract_design_attributes(extractor.model, design_path_filter=design_path_filter)

    # Step 5: Create parameter group deriver
    group_deriver = ParameterGroupDeriver(design_attrs, calc_usages, calc_defs)

    # Step 6: Create backtracker and run
    backtracker = DependencyBacktracker(
        calc_usages,
        calc_defs,
        design_attributes=design_attrs,
    )
    backtracking_result = backtracker.find_required_modules(
        targets or [],
        include_all=include_all,
    )

    # Step 6.5: Compile expressions and classify compilability
    compilation_results: dict[str, CalcDefCompilationResult] = {}
    for calc_def in calc_defs:
        if calc_def.output_expression_asts:
            try:
                result_comp = compile_calc_def(
                    calc_def=calc_def,
                    expression_asts=calc_def.output_expression_asts,
                    all_member_names=calc_def.all_member_names or None,
                    member_expressions=calc_def.member_expressions or None,
                )
                compilation_results[calc_def.name] = result_comp
            except Exception:
                logger.warning(
                    "Expression compilation failed for '%s', "
                    "falling back to UNKNOWN compilability",
                    calc_def.name,
                    exc_info=True,
                )

    # Step 7: Build ComputationGraph (single source of truth)
    computation_graph = build_computation_graph(
        result=backtracking_result,
        calc_defs=calc_defs,
        design_attrs=design_attrs,
        group_deriver=group_deriver,
        compilation_results=compilation_results,
    )

    return PipelineContext(
        extractor=extractor,
        calc_defs=calc_defs,
        calc_usages=calc_usages,
        design_attributes=design_attrs,
        group_deriver=group_deriver,
        backtracker=backtracker,
        backtracking_result=backtracking_result,
        computation_graph=computation_graph,
        compilation_results=compilation_results,
    )


__all__ = [
    "CodeGenerationError",
    "PipelineContext",
    "SysMLParsingError",
    "build_pipeline_context",
]
