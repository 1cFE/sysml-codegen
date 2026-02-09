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

from agentic_mbse.sysml.syside_adapter import SysideAdapter

from sysml_codegen.analysis.dependency_backtracker import (
    BacktrackingResult,
    DependencyBacktracker,
)
from sysml_codegen.analysis.parameter_groups import (
    DesignAttributeData,
    ParameterGroupDeriver,
    extract_design_attributes,
)
from sysml_codegen.core.qualified_names import sysml_to_python_qualified_name
from sysml_codegen.extraction.data_models import (
    CalculationDefinitionData,
    ComputedAttributeClassification,
    ComputedAttributeData,
)
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

    # Computed attributes extracted from PartDef/PartUsage elements (Step 4.5).
    computed_attributes: list[ComputedAttributeData] = field(default_factory=list)


def _remove_formula_from_design_attrs(
    computed_attrs: list[ComputedAttributeData],
    design_attrs: dict[Path, list[DesignAttributeData]],
) -> int:
    """Remove FORMULA computed attributes from design_attrs in-place.

    FORMULA attributes must be removed before ParameterGroupDeriver to prevent
    false entry points. The QN format built here must match what
    build_element_qualified_name() produces for DesignAttributeData.qualified_name.

    Args:
        computed_attrs: All computed attributes (only FORMULA classification filtered).
        design_attrs: Design attributes dict to modify in-place.

    Returns:
        Count of removed attributes.
    """
    formula_qns: set[str] = set()
    for ca in computed_attrs:
        if ca.classification == ComputedAttributeClassification.FORMULA:
            part_qn_python = sysml_to_python_qualified_name(ca.owning_part_qualified_name)
            formula_qns.add(f"{part_qn_python}__{ca.python_name}")

    if not formula_qns:
        return 0

    removed = 0
    for path in design_attrs:
        original_len = len(design_attrs[path])
        design_attrs[path] = [
            a for a in design_attrs[path]
            if a.qualified_name not in formula_qns
        ]
        removed += original_len - len(design_attrs[path])

    return removed


def _extract_and_filter_computed_attributes(
    model: Any,
    calc_usages: list[CalcUsageData],
    design_attrs: dict[Path, list[DesignAttributeData]],
) -> list[ComputedAttributeData]:
    """Step 4.5: Extract computed attributes and remove FORMULAs from design_attrs.

    Iterates PartDefinition and PartUsage elements from the model, calls
    extract_computed_attributes() for each, then removes FORMULA-classified
    attributes from design_attrs to prevent false entry points.

    Args:
        model: Parsed SysIDE model (from extractor.model).
        calc_usages: Pipeline's calc usages (reserved for future use).
        design_attrs: Design attributes dict, modified in-place to remove FORMULAs.

    Returns:
        All extracted computed attributes (all classifications).
    """
    from sysml_codegen.extraction.computed_attribute_extractor import (
        extract_computed_attributes,
    )

    all_computed_attrs: list[ComputedAttributeData] = []

    # Iterate PartDefinition and PartUsage elements
    part_elements = list(SysideAdapter.elements_of_type(model, "PartDefinition"))
    part_elements.extend(SysideAdapter.elements_of_type(model, "PartUsage"))

    for part_elem in part_elements:
        # Build calc_usage_names for this part from its owned members
        calc_usage_names = {
            m.name for m in part_elem.owned_members
            if SysideAdapter.is_instance(m, "CalculationUsage")
        }

        computed = extract_computed_attributes(None, part_elem, calc_usage_names)
        all_computed_attrs.extend(computed)

    # Remove FORMULA attributes from design_attrs
    removed_count = _remove_formula_from_design_attrs(all_computed_attrs, design_attrs)

    # Log summary
    by_classification: dict[str, int] = {}
    for ca in all_computed_attrs:
        key = ca.classification.value
        by_classification[key] = by_classification.get(key, 0) + 1

    breakdown = ", ".join(f"{v} {k}" for k, v in sorted(by_classification.items()))
    logger.info(
        "Step 4.5: Extracted %d computed attributes (%s), removed %d FORMULA from design_attrs",
        len(all_computed_attrs),
        breakdown or "none",
        removed_count,
    )

    return all_computed_attrs


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

    # Step 4.5: Extract computed attributes and remove FORMULAs from design_attrs
    computed_attrs = _extract_and_filter_computed_attributes(
        extractor.model, calc_usages, design_attrs
    )

    # Step 5: Create parameter group deriver (uses filtered design_attrs)
    group_deriver = ParameterGroupDeriver(design_attrs, calc_usages, calc_defs)

    # Step 6: Create backtracker and run
    backtracker = DependencyBacktracker(
        calc_usages,
        calc_defs,
        design_attributes=design_attrs,
        computed_attributes=computed_attrs,
    )
    backtracking_result = backtracker.find_required_modules(
        targets or [],
        include_all=include_all,
    )

    # Step 6.5: Compile expressions and classify compilability
    logger.info(
        "Step 6.5: Compiling expressions for %d calculation definitions",
        len(calc_defs),
    )
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
                logger.info(
                    "  Compiled '%s': %s",
                    calc_def.name,
                    result_comp.overall_compilability.value,
                )
            except Exception:
                logger.warning(
                    "Expression compilation failed for '%s', "
                    "falling back to UNKNOWN compilability",
                    calc_def.name,
                    exc_info=True,
                )

    skipped = len(calc_defs) - len(compilation_results)
    compilability_counts: dict[str, int] = {}
    for result in compilation_results.values():
        key = result.overall_compilability.value
        compilability_counts[key] = compilability_counts.get(key, 0) + 1
    breakdown = ", ".join(f"{v} {k}" for k, v in sorted(compilability_counts.items()))
    logger.info(
        "Step 6.5 complete: %d compiled (%s), %d skipped (no expressions)",
        len(compilation_results),
        breakdown or "none",
        skipped,
    )

    # Step 7: Build ComputationGraph (single source of truth)
    computation_graph = build_computation_graph(
        result=backtracking_result,
        calc_defs=calc_defs,
        design_attrs=design_attrs,
        group_deriver=group_deriver,
        compilation_results=compilation_results,
        computed_attributes=computed_attrs,
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
        computed_attributes=computed_attrs,
    )


__all__ = [
    "CodeGenerationError",
    "PipelineContext",
    "SysMLParsingError",
    "_remove_formula_from_design_attrs",
    "build_pipeline_context",
]
