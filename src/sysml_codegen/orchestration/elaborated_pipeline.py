"""The complete route through the exact-ID elaborator.

This is the shipped authority.  It was Item-5 dual-run evidence while the
string-resolution builder was still in the tree; that builder is retired, so
there is no other route left to compare against.

``elaborate_admitted_sources`` is the front half of the route taken from an
admitted source set rather than from raw caller paths.  It is what the live and
the v6 capture routes share, so both see the same parsed documents and the same
portable ``root-N/<relpath>`` source referents on every graph node.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from pathlib import Path

from sysml_codegen.analysis.source_referent import map_live_source_referent
from sysml_codegen.core.errors import CodeGenerationError, SysMLParsingError
from sysml_codegen.elaboration import elaborate, project
from sysml_codegen.elaboration.graph import (
    AttrNode,
    CalcNode,
    ConstraintNode,
    ConstraintUsageRecord,
    InstanceGraph,
)
from sysml_codegen.extraction.extractor import SysMLDataExtractor
from sysml_codegen.extraction.source_manifest import SourceAdmission
from sysml_codegen.resolution.models import ComputationGraph

__all__ = [
    "build_elaborated_pipeline",
    "elaborate_admitted_sources",
    "elaborate_model_paths",
    "require_executable_content",
]


def build_elaborated_pipeline(model_paths: list[Path]) -> ComputationGraph:
    """Load, elaborate, and project one model through only the exact-ID route."""
    return project(elaborate_model_paths(model_paths))


def elaborate_model_paths(model_paths: list[Path]) -> InstanceGraph:
    """Load and elaborate live models, stopping at the exact instance graph.

    The projection half is deliberately not here: a caller that seals the graph
    before projecting (``orchestration/exact_pipeline_context.py``) needs the
    graph itself, and a caller that only wants the public surface takes
    ``build_elaborated_pipeline``. Both reach the elaborator by this one path.
    """
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
    graph = elaborate(
        extractor.model,
        calc_defs,
        validation_diagnostics=extractor.diagnostics.validation,
        model_paths=model_paths,
    )
    require_executable_content(graph, calc_defs)
    # The live route keeps raw parser paths on ``source_file`` — they are the
    # checkout, and the provenance comment says so on purpose. The excluded
    # constraint location is different: it is sealed into the catalog and the
    # model contract, so it is normalized here and nowhere else.
    _rewrite_exclusion_locations(
        graph, lambda node: map_live_source_referent(node.source_file, model_paths)
    )
    return graph


def require_executable_content(graph: InstanceGraph, calc_definitions: Sequence[object]) -> None:
    """Refuse a model that carries nothing this pipeline could ever execute.

    The gate is graph-level emptiness — no calculation, no constraint, and no
    calculation definition — not the presence of a ``calc def`` on its own. That
    follows the B37-01 ruling (recovery plan, Phase 2): modeled aggregation is
    executable, so a model whose only computation is an aggregation expression is
    legitimate even though the legacy pre-elaboration ``calc def`` check refuses
    it. Both routes in this module share this one gate so capture cannot seal
    something the live route would reject.
    """
    if not graph.calcs and not graph.constraints and not calc_definitions:
        raise CodeGenerationError(
            "No calculation, constraint, or calculation definition found in models. "
            "There is nothing to generate: check that the model paths include the "
            "library and design files you meant to load."
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

    calc_definitions = extractor.extract_calculation_definitions()
    graph = elaborate(
        extractor.model,
        calc_definitions,
        validation_diagnostics=extractor.diagnostics.validation,
        model_paths=admission.staged_files,
    )
    admission.verify_after_parse(extractor.model)
    require_executable_content(graph, calc_definitions)
    _rewrite_sources_as_referents(graph, admission)
    # ``source_file`` is already the referent by the line above, so the excluded
    # location is re-rendered from it rather than from the staged absolute path
    # the elaborator saw.
    _rewrite_exclusion_locations(graph, lambda node: node.source_file)
    return graph


def _rewrite_sources_as_referents(graph: InstanceGraph, admission: SourceAdmission) -> None:
    staged_to_referent = admission.staged_to_referent
    for nodes in (graph.attrs, graph.calcs, graph.constraints):
        for node in nodes.values():
            node.source_file = _referent_for(node, staged_to_referent)
    # The usage tier carries a source location too, and it is sealed into the snapshot
    # and the catalog. Left as the staged absolute path it would make the captured bytes
    # vary by capture machine and disagree with the live route on the same model.
    for record in graph.constraint_usages.values():
        record.source_file = _referent_for(record, staged_to_referent)


def _rewrite_exclusion_locations(
    graph: InstanceGraph, referent_of: Callable[[ConstraintNode], str]
) -> None:
    """Re-render every excluded constraint's location against a portable referent.

    ``exclusion_location`` is the one field in the sealed constraint catalog that
    carries a source path, and the elaborator builds it from the raw parser path
    it happened to be handed — the checkout directory live, and the private
    staging directory during a capture. Both are absolute, both reach the catalog
    fingerprint and through it the model contract's semantic fingerprint, so a
    package built at a different path authenticated as a different model. Each
    route supplies the mapping it can prove; the rendering is one shape.
    """
    for node in graph.constraints.values():
        if node.exclusion_location is None:
            continue
        node.exclusion_location = f"{referent_of(node)}:{node.source_line}"


def _referent_for(
    node: AttrNode | CalcNode | ConstraintNode | ConstraintUsageRecord,
    staged_to_referent: dict[str, str],
) -> str:
    referent = staged_to_referent.get(str(Path(node.source_file).resolve()))
    if referent is None:
        raise SysMLParsingError(
            f"elaborated source {node.source_file!r} is outside the admitted document set"
        )
    return referent
