"""Internal complete route through the exact-ID elaborator.

This module exists for Item-5 dual-run evidence.  It is deliberately absent
from the CLI and does not call, adapt, or import the shipped legacy builder.

``elaborate_admitted_sources`` is the front half of that route taken from an
admitted source set rather than from raw caller paths.  It is what the live and
the v6 capture routes share, so both see the same parsed documents and the same
portable ``root-N/<relpath>`` source referents on every graph node.
"""

from __future__ import annotations

from pathlib import Path

from sysml_codegen.elaboration import elaborate, project
from sysml_codegen.elaboration.graph import AttrNode, CalcNode, ConstraintNode, InstanceGraph
from sysml_codegen.extraction.extractor import SysMLDataExtractor
from sysml_codegen.extraction.source_manifest import SourceAdmission
from sysml_codegen.orchestration.pipeline_context import (
    CodeGenerationError,
    SysMLParsingError,
)
from sysml_codegen.resolution.models import ComputationGraph

__all__ = ["build_elaborated_pipeline", "elaborate_admitted_sources"]


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


def elaborate_admitted_sources(admission: SourceAdmission) -> InstanceGraph:
    """Parse one admitted staged source set and return its exact instance graph.

    SysIDE only ever sees the private staged copies, so a source edited during
    the run cannot slip into the parsed model. After parsing, the admission
    re-checks the stage, the parsed document set, and the original tree; then
    every node's ``source_file`` is rewritten from its staged absolute path to
    the portable referent the manifest names it by.
    """
    extractor = SysMLDataExtractor(list(admission.staged_files))
    try:
        if not extractor.load_models():
            raise SysMLParsingError(
                "Failed to load admitted SysML sources: "
                f"{[item.referent for item in admission.files]}"
            )
    except ValueError as error:
        raise SysMLParsingError(f"Failed to load admitted SysML sources: {error}") from error
    if extractor.diagnostics is None:
        raise SysMLParsingError("SysML validation diagnostics are unavailable after model loading")

    graph = elaborate(
        extractor.model,
        extractor.extract_calculation_definitions(),
        validation_diagnostics=extractor.diagnostics.validation,
    )
    admission.verify_after_parse(extractor.model)
    _rewrite_sources_as_referents(graph, admission)
    return graph


def _rewrite_sources_as_referents(graph: InstanceGraph, admission: SourceAdmission) -> None:
    staged_to_referent = admission.staged_to_referent
    for nodes in (graph.attrs, graph.calcs, graph.constraints):
        for node in nodes.values():
            node.source_file = _referent_for(node, staged_to_referent)


def _referent_for(
    node: AttrNode | CalcNode | ConstraintNode, staged_to_referent: dict[str, str]
) -> str:
    referent = staged_to_referent.get(str(Path(node.source_file).resolve()))
    if referent is None:
        raise SysMLParsingError(
            f"elaborated source {node.source_file!r} is outside the admitted document set"
        )
    return referent
