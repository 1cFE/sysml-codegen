"""The complete route through the exact-ID elaborator.

This is the shipped authority.  It was Item-5 dual-run evidence while the
string-resolution builder was still in the tree; that builder is retired, so
there is no other route left to compare against.

``elaborate_admitted_sources`` is the front half of the capture route, taken
from an admitted source set rather than from raw caller paths.  The live route
deliberately does not share it (the route-parity comparison needs independent
arms; ``tests/conformance/test_snapshot_v6_routes.py`` pins the split), but both
arms render ``source_file`` the same way: every graph node carries the portable
``root-N/<relpath>`` referent, each route deriving it from the evidence it has —
the caller's model roots live, the sealed admission manifest during capture.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from agentic_mbse import SemanticEvidenceError
from agentic_mbse.sysml.syside_adapter import get_syside

from sysml_codegen.analysis.source_referent import map_live_source_referent
from sysml_codegen.core.errors import CodeGenerationError, SysMLParsingError
from sysml_codegen.elaboration import (
    Diagnostic,
    ElaborationCode,
    ElaborationDiagnosticError,
    GraphValidationError,
    project,
)
from sysml_codegen.elaboration.diagnostics import ElaborationInvariantError
from sysml_codegen.elaboration.elaborate import _build_instance_graph
from sysml_codegen.elaboration.graph import (
    AttrNode,
    CalcNode,
    ConstraintNode,
    ConstraintUsageRecord,
    InstanceGraph,
)
from sysml_codegen.extraction.errors import ExactTypeError
from sysml_codegen.extraction.extractor import SysMLDataExtractor
from sysml_codegen.extraction.source_manifest import SourceAdmission
from sysml_codegen.resolution.models import ComputationGraph

__all__ = [
    "build_elaborated_pipeline",
    "elaborate_admitted_sources",
    "elaborate_loaded_extractor",
    "elaborate_model_paths",
    "require_executable_content",
]


def build_elaborated_pipeline(model_paths: list[Path]) -> ComputationGraph:
    """Load, elaborate, and project one model through only the exact-ID route."""
    return project(elaborate_model_paths(model_paths))


def elaborate_model_paths(model_paths: list[Path], *, strict: bool = True) -> InstanceGraph:
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

    return elaborate_loaded_extractor(
        extractor,
        model_paths=tuple(model_paths),
        source_referents=_live_source_referents(extractor.model, tuple(model_paths)),
        strict=strict,
    )


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


def elaborate_admitted_sources(
    admission: SourceAdmission,
    *,
    strict: bool = True,
) -> InstanceGraph:
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

    graph = elaborate_loaded_extractor(
        extractor,
        model_paths=admission.staged_files,
        source_referents=admission.staged_to_referent,
        strict=strict,
    )
    admission.verify_after_parse(extractor.model)
    return graph


def elaborate_loaded_extractor(
    extractor: SysMLDataExtractor,
    *,
    model_paths: Sequence[Path],
    source_referents: Mapping[str, str],
    strict: bool,
) -> InstanceGraph:
    """Extract and elaborate one loaded model through the sole evidence bridge."""
    if extractor.diagnostics is None:
        raise SysMLParsingError("SysML validation diagnostics are unavailable after model loading")
    try:
        calc_definitions = extractor.extract_calculation_definitions()
        graph = _build_instance_graph(
            extractor.model,
            calc_definitions,
            validation_diagnostics=extractor.diagnostics.validation,
            model_paths=model_paths,
            strict=strict,
        )
        require_executable_content(graph, calc_definitions)
    except SemanticEvidenceError as error:
        diagnostics = (_semantic_evidence_diagnostic(error, source_referents),)
        raise ElaborationDiagnosticError(diagnostics) from error
    except ExactTypeError as error:
        location = ""
        if error.location is not None:
            raw_source, line = error.location
            referent = _lookup_referent(raw_source, source_referents)
            location = f" [{referent}:{line}]"
        diagnostics = (
            Diagnostic(
                code=error.code,
                consumer=None,
                consumer_display=error.reference,
                param_name=None,
                detail=f"{error.operation}: {error.detail}{location}",
            ),
        )
        raise ElaborationDiagnosticError(diagnostics) from error
    except ElaborationInvariantError as error:
        diagnostics = (
            Diagnostic(
                code=error.code,
                consumer=None,
                consumer_display="<model>",
                param_name=None,
                detail=error.detail,
            ),
        )
        raise ElaborationDiagnosticError(diagnostics) from error
    except GraphValidationError as error:
        raise ElaborationDiagnosticError(error.diagnostics) from error

    _rewrite_sources_as_referents(graph, source_referents)
    _rewrite_exclusion_locations(graph)
    return graph


def _live_source_referents(model: Any, model_paths: Sequence[Path]) -> dict[str, str]:
    """Bind every loaded live document path to its portable caller-root referent."""
    syside = get_syside()
    referents: dict[str, str] = {}
    for raw_source in model.uris(syside.DocumentKind.MODEL):
        raw_text = str(raw_source)
        try:
            referent = map_live_source_referent(raw_text, list(model_paths))
        except ValueError as error:
            raise SysMLParsingError(
                f"elaborated source {raw_text!r} is outside the supplied model roots"
            ) from error
        referents[raw_text] = referent
        referents[str(Path(raw_text).resolve())] = referent
    return referents


def _semantic_evidence_diagnostic(
    error: SemanticEvidenceError,
    source_referents: Mapping[str, str],
) -> Diagnostic:
    location = ""
    if error.location is not None:
        raw_source, line = error.location
        referent = _lookup_referent(raw_source, source_referents)
        location = f" [{referent}:{line}]"
    return Diagnostic(
        code=ElaborationCode.SI_EVIDENCE_INCOMPLETE,
        consumer=None,
        consumer_display=error.reference or "<model>",
        param_name=None,
        detail=f"{error.operation}: {error.detail}{location}",
    )


def _rewrite_sources_as_referents(
    graph: InstanceGraph,
    source_referents: Mapping[str, str],
) -> None:
    for nodes in (graph.attrs, graph.calcs, graph.constraints):
        for node in nodes.values():
            node.source_file = _referent_for(node, source_referents)
    # The usage tier carries a source location too, and it is sealed into the snapshot
    # and the catalog. Left as the staged absolute path it would make the captured bytes
    # vary by capture machine and disagree with the live route on the same model.
    for record in graph.constraint_usages.values():
        record.source_file = _referent_for(record, source_referents)


def _rewrite_exclusion_locations(graph: InstanceGraph) -> None:
    """Re-render every excluded constraint's location against a portable referent.

    ``exclusion_location`` carries a source path into the sealed constraint
    catalog, and the elaborator builds it from the raw parser path it happened
    to be handed — the checkout directory live, and the private staging
    directory during a capture. Both are absolute, both reach the catalog
    fingerprint and through it the model contract's semantic fingerprint, so a
    package built at a different path authenticated as a different model. Both
    routes rewrite ``source_file`` to the portable referent first, so the
    location is re-rendered from it here.
    """
    for node in graph.constraints.values():
        if node.exclusion_location is None:
            continue
        node.exclusion_location = f"{node.source_file}:{node.source_line}"


def _referent_for(
    node: AttrNode | CalcNode | ConstraintNode | ConstraintUsageRecord,
    source_referents: Mapping[str, str],
) -> str:
    return _lookup_referent(node.source_file, source_referents)


def _lookup_referent(raw_source: str, source_referents: Mapping[str, str]) -> str:
    referent = source_referents.get(raw_source)
    if referent is None:
        referent = source_referents.get(str(Path(raw_source).resolve()))
    if referent is None:
        raise SysMLParsingError(
            f"elaborated source {raw_source!r} is outside the declared source set"
        )
    return referent
