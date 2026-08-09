"""Internal complete route through the exact-ID elaborator.

This module exists for Item-5 dual-run evidence.  It is deliberately absent
from the CLI and does not call, adapt, or import the shipped legacy builder.
"""

from __future__ import annotations

from pathlib import Path

from sysml_codegen.elaboration import elaborate, project
from sysml_codegen.extraction.extractor import SysMLDataExtractor
from sysml_codegen.orchestration.pipeline_context import (
    CodeGenerationError,
    SysMLParsingError,
)
from sysml_codegen.resolution.models import ComputationGraph

__all__ = ["build_elaborated_pipeline"]


def build_elaborated_pipeline(model_paths: list[Path]) -> ComputationGraph:
    """Load, elaborate, and project one model through only the exact-ID route."""
    extractor = SysMLDataExtractor(model_paths)
    try:
        if not extractor.load_models():
            raise SysMLParsingError(
                f"Failed to load SysML models from: {[str(path) for path in model_paths]}"
            )
    except ValueError as error:
        raise SysMLParsingError(f"Failed to load SysML models: {error}") from error
    if extractor.diagnostics is None:
        raise SysMLParsingError("SysML validation diagnostics are unavailable after model loading")

    calc_defs = extractor.extract_calculation_definitions()
    if not calc_defs:
        raise CodeGenerationError(
            "No calculation definitions found in models. "
            "Ensure library models contain calc definitions."
        )
    return project(
        elaborate(
            extractor.model,
            calc_defs,
            validation_diagnostics=extractor.diagnostics.validation,
        )
    )
