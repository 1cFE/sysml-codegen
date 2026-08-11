"""Builder-created authority for exact elaboration and generation."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import TYPE_CHECKING, NoReturn

from sysml_codegen.resolution.models import ComputationGraph

if TYPE_CHECKING:
    from sysml_codegen.elaboration.graph import InstanceGraph
    from sysml_codegen.generation.constraint_name_safety import ConstraintNameViolation

_CONSTRUCTION_ERROR = (
    "PipelineContext is builder-created; use build_pipeline_context or "
    "build_pipeline_context_from_snapshot"
)
_PROJECTOR_SEMANTIC_MARKER = "instance-projector/v1"


class SysMLParsingError(Exception):
    """A live SysML model could not be parsed."""


class CodeGenerationError(Exception):
    """A model cannot produce a certifying generated package."""

    def __init__(
        self,
        message: str,
        *,
        name_safety_violation: ConstraintNameViolation | None = None,
    ) -> None:
        super().__init__(message)
        self.name_safety_violation = name_safety_violation


@dataclass(frozen=True, slots=True)
class _Selection:
    targets: tuple[str, ...]
    include_all: bool


@dataclass(frozen=True, slots=True)
class _ProjectionReceipt:
    instance_fingerprint: str
    targets: tuple[str, ...]
    include_all: bool
    projector_semantic_marker: str
    computation_digest: str


def _integrity_error(detail: str, error: Exception | None = None) -> NoReturn:
    failure = CodeGenerationError(f"PipelineContext receipt verification failed: {detail}")
    if error is None:
        raise failure
    raise failure from error


def _canonical_selection(
    targets: object = None,
    include_all: object = True,
) -> _Selection:
    if not isinstance(include_all, bool):
        raise TypeError("include_all must be a bool")
    if targets is None:
        values: tuple[object, ...] = ()
    elif isinstance(targets, (str, bytes)):
        raise TypeError("targets must be a sequence of nonempty strings or None")
    else:
        try:
            values = tuple(targets)  # type: ignore[arg-type]
        except TypeError as error:
            raise TypeError("targets must be a sequence of nonempty strings or None") from error
    if any(not isinstance(target, str) or not target for target in values):
        raise TypeError("every target must be a nonempty string")
    return _Selection(tuple(sorted(set(values))), include_all)  # type: ignore[arg-type]


def _instance_fingerprint(instance_bytes: bytes) -> str:
    try:
        document = json.loads(instance_bytes)
        fingerprint = document["fingerprint"]
    except (KeyError, TypeError, json.JSONDecodeError, UnicodeDecodeError) as error:
        _integrity_error("canonical instance bytes are malformed", error)
    if not isinstance(fingerprint, str):
        _integrity_error("canonical instance fingerprint is malformed")
    return fingerprint


def _computation_payload(graph: ComputationGraph) -> dict[str, object]:
    """Return every semantic field, including Pydantic-excluded fields."""
    return {
        "modules": [module.model_dump(mode="json") for module in graph.modules],
        "entry_point_groups": [
            group.model_dump(mode="json") for group in graph.entry_point_groups
        ],
        "execution_order": list(graph.execution_order),
        "fallback_entry_points": sorted(graph.fallback_entry_points),
        "output_aliases": [alias.model_dump(mode="json") for alias in graph.output_aliases],
        "constraint_catalog": (
            graph.constraint_catalog.model_dump(mode="json")
            if graph.constraint_catalog is not None
            else None
        ),
    }


def _computation_digest(graph: ComputationGraph) -> str:
    try:
        payload = json.dumps(
            {
                "projector_semantics": _PROJECTOR_SEMANTIC_MARKER,
                "computation_graph": _computation_payload(graph),
            },
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode()
    except (TypeError, ValueError) as error:
        raise CodeGenerationError(
            "ComputationGraph contains a non-finite or non-canonical value"
        ) from error
    return hashlib.sha256(payload).hexdigest()


def _project(graph: InstanceGraph, selection: _Selection) -> ComputationGraph:
    from sysml_codegen.elaboration.graph import GraphValidationError
    from sysml_codegen.elaboration.project import ProjectionError, project

    try:
        graph.validate()
        graph.require_projectable()
        return project(
            graph,
            targets=selection.targets,
            include_all=selection.include_all,
        )
    except CodeGenerationError:
        raise
    except (GraphValidationError, ProjectionError, TypeError, ValueError) as error:
        raise CodeGenerationError(f"Exact graph projection failed: {error}") from error


def _receipt_for(
    instance_bytes: bytes,
    selection: _Selection,
    graph: ComputationGraph,
) -> _ProjectionReceipt:
    return _ProjectionReceipt(
        instance_fingerprint=_instance_fingerprint(instance_bytes),
        targets=selection.targets,
        include_all=selection.include_all,
        projector_semantic_marker=_PROJECTOR_SEMANTIC_MARKER,
        computation_digest=_computation_digest(graph),
    )


class _VerifiedProjectionLease:
    """One receipt-verified graph held across a certifying write operation."""

    __slots__ = ("_context", "_digest", "computation_graph")

    def __init__(self, context: PipelineContext, graph: ComputationGraph) -> None:
        self._context = context
        self.computation_graph = graph
        self._digest = _computation_digest(graph)

    def verify_before_seal(self) -> None:
        fresh = self._context._verified_projection()
        if _computation_digest(self.computation_graph) != self._digest:
            _integrity_error("the leased computation graph changed during generation")
        if _computation_digest(fresh) != self._digest:
            _integrity_error("the bound projection changed during generation")


class PipelineContext:
    """Narrow immutable-byte-backed result returned only by public builders."""

    __slots__ = ("_instance_bytes", "_selection", "_receipt")

    _instance_bytes: bytes
    _selection: _Selection
    _receipt: _ProjectionReceipt

    def __new__(cls, *args: object, **kwargs: object) -> PipelineContext:
        del cls, args, kwargs
        raise TypeError(_CONSTRUCTION_ERROR)

    def __init__(self, *args: object, **kwargs: object) -> None:
        del self, args, kwargs
        raise TypeError(_CONSTRUCTION_ERROR)

    def __setattr__(self, name: str, value: object) -> NoReturn:
        del name, value
        raise TypeError("PipelineContext is immutable")

    def __delattr__(self, name: str) -> NoReturn:
        del name
        raise TypeError("PipelineContext is immutable")

    @property
    def computation_graph(self) -> ComputationGraph:
        """Return a fresh projection after checking every bound receipt field."""
        return self._verified_projection()

    def _verified_projection(self) -> ComputationGraph:
        try:
            instance_bytes = self._instance_bytes
            selection = self._selection
            receipt = self._receipt
        except (AttributeError, TypeError) as error:
            _integrity_error("private authority is absent or malformed", error)
        if not isinstance(instance_bytes, bytes):
            _integrity_error("canonical instance authority is not bytes")
        if not isinstance(selection, _Selection) or not isinstance(receipt, _ProjectionReceipt):
            _integrity_error("selection or receipt has the wrong type")
        if (
            receipt.targets != selection.targets
            or receipt.include_all is not selection.include_all
            or receipt.projector_semantic_marker != _PROJECTOR_SEMANTIC_MARKER
        ):
            _integrity_error("selection or projector marker disagrees with the receipt")
        try:
            from sysml_codegen.snapshot.instance_graph import (
                InstanceGraphCodecError,
                decode_instance_graph,
            )

            graph = decode_instance_graph(instance_bytes)
        except (InstanceGraphCodecError, TypeError, ValueError) as error:
            _integrity_error("canonical instance bytes do not decode", error)
        if _instance_fingerprint(instance_bytes) != receipt.instance_fingerprint:
            _integrity_error("instance fingerprint disagrees with the receipt")
        projected = _project(graph, selection)
        if _receipt_for(instance_bytes, selection, projected) != receipt:
            _integrity_error("projected computation disagrees with the receipt")
        return projected

    def _verified_projection_lease(self) -> _VerifiedProjectionLease:
        """Verify at certifying entry and retain that one graph until sealing."""
        return _VerifiedProjectionLease(self, self._verified_projection())

    def __copy__(self) -> NoReturn:
        raise TypeError("PipelineContext cannot be copied")

    def __deepcopy__(self, memo: object) -> NoReturn:
        del memo
        raise TypeError("PipelineContext cannot be deep-copied")

    def __reduce__(self) -> NoReturn:
        raise TypeError("PipelineContext cannot be pickled")

    def __reduce_ex__(self, protocol: object) -> NoReturn:
        del protocol
        raise TypeError("PipelineContext cannot be pickled")


def _make_pipeline_context(
    graph: InstanceGraph,
    targets: object = None,
    include_all: object = True,
) -> PipelineContext:
    """Create the public result after exact graph and selection validation."""
    from sysml_codegen.elaboration.graph import GraphValidationError
    from sysml_codegen.snapshot.instance_graph import (
        InstanceGraphCodecError,
        decode_instance_graph,
        encode_instance_graph,
    )

    selection = _canonical_selection(targets, include_all)
    try:
        graph.validate()
        graph.require_projectable()
        instance_bytes = encode_instance_graph(graph)
    except (GraphValidationError, InstanceGraphCodecError, TypeError, ValueError) as error:
        raise CodeGenerationError(f"Exact instance graph is not projectable: {error}") from error
    projected = _project(decode_instance_graph(instance_bytes), selection)
    receipt = _receipt_for(instance_bytes, selection, projected)
    context = object.__new__(PipelineContext)
    object.__setattr__(context, "_instance_bytes", instance_bytes)
    object.__setattr__(context, "_selection", selection)
    object.__setattr__(context, "_receipt", receipt)
    return context


__all__ = [
    "CodeGenerationError",
    "PipelineContext",
    "SysMLParsingError",
]
