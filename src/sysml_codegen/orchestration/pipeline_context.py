"""Pipeline context dataclass and exception classes.

PipelineContext encapsulates all extracted data and components needed for
code generation, ensuring consistent initialization across all codegen scripts.

Moved from generation/initialization.py (Step 7.6) to enforce the boundary
that generation/ consumes only ComputationGraph.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

from sysml_codegen.analysis.dependency_backtracker import (
    BacktrackingResult,
    DependencyBacktracker,
)
from sysml_codegen.analysis.parameter_groups import (
    DesignAttributeData,
    ParameterGroupDeriver,
)
from sysml_codegen.core.models import ChannelAlias
from sysml_codegen.core.output_registry import OutputRegistry
from sysml_codegen.extraction.constraint_report import ConstraintManifestEntry
from sysml_codegen.extraction.data_models import (
    CalculationDefinitionData,
    ComputedAttributeData,
    HierarchyExtractionResult,
    ScopedAggregationData,
)
from sysml_codegen.extraction.expression_compiler import CalcDefCompilationResult
from sysml_codegen.extraction.usage_extractor import CalcUsageData
from sysml_codegen.resolution.models import ComputationGraph, ConcreteConstraint

if TYPE_CHECKING:
    from agentic_mbse.sysml.constraint_facts import ConstraintFacts


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

    # Hierarchy data from extract_hierarchy_data() (Step 3.5).
    hierarchy_data: HierarchyExtractionResult | None = None

    # Aggregation expressions scoped to design instances (Step 3.5).
    aggregation_expressions: list[ScopedAggregationData] = field(default_factory=list)

    # Channel aliases from EXPOSE_PURE + CHAIN redefinitions (Steps 3.5 + 4.5).
    channel_aliases: list[ChannelAlias] = field(default_factory=list)

    # Model-wide dropped-constraint manifest (Step 2.5). Serialized into the
    # snapshot so the from-snapshot path can replay the drop report (Item 4).
    constraint_manifest: list[ConstraintManifestEntry] = field(default_factory=list)

    # OutputRegistry from Step 5.5 (None if not yet constructed).
    output_registry: OutputRegistry | None = None

    # Concrete constraint catalog from [P1 RESOLVE] (Item 5, D7). Empty when no
    # constraint facts are admitted. Carries eligible (executable) and
    # unassessed (eligible=False) records alike, until Item 7's catalog
    # runtime exists.
    concrete_constraints: list[ConcreteConstraint] = field(default_factory=list)

    # Neutral constraint facts from Step 2.6 (Item 5) — the source-level vocabulary
    # `generation/constraint_catalog.py` reads for the catalog's `source_records` (D6).
    # `None` when the model has zero constraint usages (no lowering ran).
    constraint_facts: "ConstraintFacts | None" = None


__all__ = [
    "CodeGenerationError",
    "PipelineContext",
    "SysMLParsingError",
]
