"""Receipt-bound pipeline context built from the exact instance graph.

The legacy ``PipelineContext`` (``orchestration/pipeline_context.py``) and its
builders remain the shipped authority; nothing here replaces them. This is the
exact route's own construction, added beside them, so both can be run on the
same model and compared while the cutover is in progress.

What "defensive" means here, concretely. The context holds one thing: the
canonical bytes of the instance graph it was built from, plus a receipt over
those bytes, the selection, and the resulting computation graph. It does not
hold a ``ComputationGraph`` object at all.

Two consequences follow, and they are the point of the design:

- **Nothing can be mutated after the build.** Attribute assignment and deletion
  raise, and the context is not copyable or picklable, so there is no second
  context that could drift from the first.
- **Every read is checked and isolated.** ``computation_graph`` decodes the
  sealed bytes, re-projects them, and refuses to return anything whose receipt
  does not match. Each read returns a fresh object, so a caller that mutates the
  graph it received cannot affect what the next caller sees.

The receipt is a self-consistency check, not a forgery defence. It catches a
context whose authority moved underneath it — an in-place edit, a partially
constructed object, a projector whose semantics changed between reads. It
cannot make a snapshot's own claims about its sources true; that limit is
recorded on ``snapshot/envelope.py`` and accepted for the rebuild.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import NoReturn

from sysml_codegen.core.errors import CodeGenerationError
from sysml_codegen.elaboration.graph import GraphValidationError, InstanceGraph
from sysml_codegen.elaboration.project import ProjectionError, project
from sysml_codegen.resolution.models import ComputationGraph
from sysml_codegen.snapshot.instance_graph import (
    InstanceGraphCodecError,
    decode_instance_graph,
    encode_instance_graph,
)

__all__ = [
    "ExactPipelineContext",
    "build_exact_pipeline_context",
    "build_exact_pipeline_context_from_snapshot",
]

#: Bumped whenever projection semantics change in a way that would make an
#: older receipt meaningless. It is part of the digest so a receipt minted by a
#: different projector cannot be mistaken for a current one.
_PROJECTOR_SEMANTICS = "instance-projector/v1"

_CONSTRUCTION_ERROR = (
    "ExactPipelineContext is builder-created; use build_exact_pipeline_context or "
    "build_exact_pipeline_context_from_snapshot"
)


@dataclass(frozen=True, slots=True)
class ProjectionReceipt:
    """What a context promises about the graph it hands out."""

    instance_fingerprint: str
    targets: tuple[str, ...] | None
    projector_semantics: str
    computation_digest: str


def _receipt_failure(detail: str, cause: Exception | None = None) -> NoReturn:
    failure = CodeGenerationError(f"ExactPipelineContext receipt verification failed: {detail}")
    if cause is None:
        raise failure
    raise failure from cause


def _canonical_targets(targets: Sequence[str] | None) -> tuple[str, ...] | None:
    if targets is None:
        return None
    if isinstance(targets, (str, bytes)):
        raise TypeError("targets must be a sequence of output names, not a single string")
    canonical = tuple(sorted({*targets}))
    if not canonical:
        raise ValueError("targets must name at least one output; pass None for the whole graph")
    if any(not isinstance(target, str) or not target for target in canonical):
        raise TypeError("every target must be a nonempty string")
    return canonical


def _instance_fingerprint(instance_bytes: bytes) -> str:
    try:
        fingerprint = json.loads(instance_bytes)["fingerprint"]
    except (KeyError, TypeError, json.JSONDecodeError, UnicodeDecodeError) as error:
        _receipt_failure("canonical instance bytes are malformed", error)
    if not isinstance(fingerprint, str) or not fingerprint:
        _receipt_failure("canonical instance fingerprint is malformed")
    return fingerprint


def _computation_digest(graph: ComputationGraph) -> str:
    """Digest every semantic field, including the ones Pydantic excludes.

    ``fallback_entry_points`` is a set and ``constraint_catalog`` is excluded
    from ``model_dump`` on the parent, so a plain dump would leave both out of
    the receipt and a change in either would pass unnoticed.
    """
    payload = {
        "projector_semantics": _PROJECTOR_SEMANTICS,
        "modules": [module.model_dump(mode="json") for module in graph.modules],
        "entry_point_groups": [group.model_dump(mode="json") for group in graph.entry_point_groups],
        "execution_order": list(graph.execution_order),
        "fallback_entry_points": sorted(graph.fallback_entry_points),
        "output_aliases": [alias.model_dump(mode="json") for alias in graph.output_aliases],
        "constraint_catalog": (
            graph.constraint_catalog.model_dump(mode="json")
            if graph.constraint_catalog is not None
            else None
        ),
    }
    try:
        encoded = json.dumps(
            payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False
        ).encode()
    except (TypeError, ValueError) as error:
        raise CodeGenerationError(
            "the projected computation graph carries a non-finite or non-canonical value"
        ) from error
    return hashlib.sha256(encoded).hexdigest()


def _project_or_fail(graph: InstanceGraph, targets: tuple[str, ...] | None) -> ComputationGraph:
    try:
        return project(graph, targets)
    except (GraphValidationError, ProjectionError, TypeError, ValueError) as error:
        raise CodeGenerationError(f"exact graph projection failed: {error}") from error


class ExactPipelineContext:
    """One sealed instance graph plus the receipt for what it projects to."""

    __slots__ = ("_instance_bytes", "_receipt")

    _instance_bytes: bytes
    _receipt: ProjectionReceipt

    def __new__(cls, *args: object, **kwargs: object) -> ExactPipelineContext:
        del cls, args, kwargs
        raise TypeError(_CONSTRUCTION_ERROR)

    def __setattr__(self, name: str, value: object) -> NoReturn:
        del value
        raise TypeError(f"ExactPipelineContext is immutable; cannot set {name!r}")

    def __delattr__(self, name: str) -> NoReturn:
        raise TypeError(f"ExactPipelineContext is immutable; cannot delete {name!r}")

    def __copy__(self) -> NoReturn:
        raise TypeError("ExactPipelineContext cannot be copied; build another one")

    def __deepcopy__(self, memo: object) -> NoReturn:
        del memo
        raise TypeError("ExactPipelineContext cannot be copied; build another one")

    def __reduce__(self) -> NoReturn:
        raise TypeError("ExactPipelineContext cannot be pickled; build another one")

    @property
    def receipt(self) -> ProjectionReceipt:
        """What this context promises, for a caller that wants to record it."""
        return self._receipt

    @property
    def instance_fingerprint(self) -> str:
        """The sealed instance graph's own fingerprint."""
        return self._receipt.instance_fingerprint

    @property
    def computation_graph(self) -> ComputationGraph:
        """Re-derive the computation graph and refuse it if the receipt disagrees."""
        graph = self._verified_projection()
        return graph

    def _verified_projection(self) -> ComputationGraph:
        try:
            receipt = self._receipt
        except AttributeError as error:
            # Reachable only by bypassing __new__ (``object.__new__(cls)``). The
            # object exists but carries no authority, so there is nothing to
            # verify against and nothing safe to return.
            _receipt_failure("this context carries no sealed authority", error)
        if receipt.projector_semantics != _PROJECTOR_SEMANTICS:
            _receipt_failure(
                f"receipt was minted by projector {receipt.projector_semantics!r}, "
                f"this build projects {_PROJECTOR_SEMANTICS!r}"
            )
        if _instance_fingerprint(self._instance_bytes) != receipt.instance_fingerprint:
            _receipt_failure("the sealed instance bytes no longer match the receipt")
        try:
            graph = decode_instance_graph(self._instance_bytes)
        except (InstanceGraphCodecError, TypeError, ValueError) as error:
            _receipt_failure("the sealed instance bytes no longer decode", error)
        projected = _project_or_fail(graph, receipt.targets)
        if _computation_digest(projected) != receipt.computation_digest:
            _receipt_failure("the projected computation graph disagrees with the receipt")
        return projected


def _seal(graph: InstanceGraph, targets: tuple[str, ...] | None) -> ExactPipelineContext:
    try:
        graph.validate()
        graph.require_projectable()
        instance_bytes = encode_instance_graph(graph)
    except (GraphValidationError, InstanceGraphCodecError, TypeError, ValueError) as error:
        raise CodeGenerationError(f"exact instance graph is not projectable: {error}") from error

    # Project from the decoded bytes rather than from the caller's object, so the
    # receipt describes what a later read will actually re-derive. Projecting the
    # live object here would let an encode/decode asymmetry mint a receipt that
    # every subsequent read then fails against.
    projected = _project_or_fail(decode_instance_graph(instance_bytes), targets)
    receipt = ProjectionReceipt(
        instance_fingerprint=_instance_fingerprint(instance_bytes),
        targets=targets,
        projector_semantics=_PROJECTOR_SEMANTICS,
        computation_digest=_computation_digest(projected),
    )
    context = object.__new__(ExactPipelineContext)
    object.__setattr__(context, "_instance_bytes", instance_bytes)
    object.__setattr__(context, "_receipt", receipt)
    return context


def build_exact_pipeline_context(
    model_paths: Sequence[Path],
    *,
    targets: Sequence[str] | None = None,
) -> ExactPipelineContext:
    """Load and elaborate live models, then seal the projection into a context."""
    from sysml_codegen.orchestration.elaborated_pipeline import elaborate_model_paths

    return _seal(elaborate_model_paths(list(model_paths)), _canonical_targets(targets))


def build_exact_pipeline_context_from_snapshot(
    snapshot_path: Path,
    *,
    targets: Sequence[str] | None = None,
    source_roots: Sequence[Path] | None = None,
) -> ExactPipelineContext:
    """Load a v6 instance-graph snapshot and seal its projection into a context.

    ``source_roots`` is passed straight through to the loader. Supplying it is
    what turns a structural load into a provenance-checked one; without it a
    snapshot proves its own shape and nothing about the files it names.
    """
    from sysml_codegen.snapshot.envelope import load_instance_graph_snapshot

    graph = load_instance_graph_snapshot(snapshot_path, source_roots=source_roots)
    return _seal(graph, _canonical_targets(targets))
