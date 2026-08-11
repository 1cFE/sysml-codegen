"""Sole live route from staged SysML sources to a receipt-bound context."""

from __future__ import annotations

from pathlib import Path

from sysml_codegen.elaboration import AttrNode, CalcNode, ConstraintNode, InstanceGraph, elaborate
from sysml_codegen.extraction.extractor import SysMLDataExtractor
from sysml_codegen.orchestration.pipeline_context import (
    CodeGenerationError,
    PipelineContext,
    SysMLParsingError,
)
from sysml_codegen.snapshot.source_manifest import SourceAdmission


def _load_and_elaborate(
    admission: SourceAdmission,
    design_path_filter: str = "",
) -> InstanceGraph:
    """Parse one admitted staged source set and return its strict exact graph."""
    if not isinstance(design_path_filter, str):
        raise TypeError("design_path_filter must be a string")
    extractor = SysMLDataExtractor(list(admission.staged_files))
    try:
        if not extractor.load_models():
            raise SysMLParsingError(
                "Failed to load admitted staged SysML sources: "
                f"{[item.referent for item in admission.files]}"
            )
    except ValueError as error:
        raise SysMLParsingError(f"Failed to load admitted staged SysML sources: {error}") from error
    if extractor.diagnostics is None:
        raise SysMLParsingError("SysML validation diagnostics are unavailable after model loading")
    calc_definitions = extractor.extract_calculation_definitions()
    graph = elaborate(
        extractor.model,
        calc_definitions,
        validation_diagnostics=extractor.diagnostics.validation,
    )
    admission.verify_after_parse(extractor.model)
    _translate_graph_sources(graph, admission)
    graph.validate()
    graph.require_projectable()
    if not graph.calcs and not graph.constraints and not calc_definitions:
        raise CodeGenerationError(
            "No calculation definition or executable constraint usage found in models."
        )
    return graph


def _translate_graph_sources(graph: InstanceGraph, admission: SourceAdmission) -> None:
    staged_to_referent = admission.staged_to_referent
    for attr_node in graph.attrs.values():
        _translate_graph_source(attr_node, staged_to_referent)
    for calc_node in graph.calcs.values():
        _translate_graph_source(calc_node, staged_to_referent)
    for constraint_node in graph.constraints.values():
        _translate_graph_source(constraint_node, staged_to_referent)


def _translate_graph_source(
    node: AttrNode | CalcNode | ConstraintNode,
    staged_to_referent: dict[str, str],
) -> None:
    try:
        resolved = str(Path(node.source_file).resolve())
    except OSError as error:
        raise SysMLParsingError(
            f"cannot resolve elaborated source location {node.source_file!r}: {error}"
        ) from error
    referent = staged_to_referent.get(resolved)
    if referent is None:
        raise SysMLParsingError(
            f"elaborated source {node.source_file!r} is outside the admitted document set"
        )
    node.source_file = referent


def build_pipeline_context(
    model_paths: list[Path],
    targets: list[str] | None = None,
    include_all: bool = True,
    design_path_filter: str = "",
) -> PipelineContext:
    """Build one receipt-bound context from the staged exact route."""
    from sysml_codegen.orchestration.pipeline_context import _make_pipeline_context
    from sysml_codegen.snapshot.source_manifest import admit_sources

    with admit_sources(model_paths) as admission:
        graph = _load_and_elaborate(admission, design_path_filter)
    return _make_pipeline_context(graph, targets=targets, include_all=include_all)


__all__ = ["build_pipeline_context"]
