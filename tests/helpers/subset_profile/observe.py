"""The two halves of a subset-profile case, each observed through its public surface.

Generator half: ``run_codegen`` on the case model, exactly as a user runs it. The refusal
comes from the ``extra={"refusal": ...}`` payload on its ERROR records, never from message
text, where a code can also appear inside detail. The instance graph comes from a spy on
``elaborated_pipeline.elaborate_model_paths`` as the exact pipeline context calls it, and the
catalog from the written ``contracts/model_contract.json``. The screen's three entry points
are tripwired for the run, so a generator answer can never be the screen's answer in
disguise.

Seams (design D9): a stored answer can assert one fact about one declaration at a named
point of the generator's output. The declaration is found by qualified name in the loaded
model and compared by ``DeclarationId``, never by text. Entry points carry no declaration,
so the harness records the owner node of each one as projection mints it, through a spy on
``_Projection._entry_source`` (``elaboration/project.py``), the one private name it patches.

Screen half: ``SysideAdapter.load_model``, then ``extract_subset_facts``, then
``evaluate_subset_profile``, as an agentic-mbse caller runs them.

Both halves need a syside license.
"""

from __future__ import annotations

import importlib
import json
import logging
import sys
import tempfile
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from agentic_mbse.sysml.subset_profile import SubsetProfileResult

    from sysml_codegen.cli.refusal import Refusal, RefusalItem
    from sysml_codegen.elaboration import InstanceGraph
    from sysml_codegen.elaboration.identity import DeclarationId
    from tests.helpers.subset_profile.cases import GeneratorRun, SeamKind


class ScreenCalledError(AssertionError):
    """The generator half reached one of the screen's entry points."""


@dataclass(frozen=True)
class GeneratorObservation:
    generated: bool
    #: The one logged refusal of a failed run; ``None`` when the run generated.
    refusal: Refusal | None
    #: The graph elaboration returned; ``None`` when elaboration itself refused.
    graph: InstanceGraph | None
    #: The written model contract; ``None`` when no package was written.
    contract: dict[str, Any] | None
    #: Each entry point projection minted, with its owner node's declaration.
    entry_points: frozenset[tuple[str, DeclarationId]]

    @property
    def refusals(self) -> tuple[RefusalItem, ...]:
        return () if self.refusal is None else self.refusal.items

    def run(self) -> GeneratorRun:
        """This run's outcome, codes and site reasons, in stored-answer form.

        A refusal that carries no code is a harness failure, not an answer (design D15): every
        raise on the route carries one, and an unclassified failure is ``SI_INTERNAL_DEFECT``.
        """
        from tests.helpers.subset_profile.cases import GeneratorOutcome, GeneratorRun

        if self.generated:
            return GeneratorRun(GeneratorOutcome.GENERATED, (), ())
        if not self.refusals:
            raise AssertionError(f"run_codegen refused with no code: {self.refusal}")
        return GeneratorRun(
            GeneratorOutcome.REFUSED,
            tuple(sorted(item.code.value for item in self.refusals)),
            tuple(sorted(item.reason for item in self.refusals if item.reason is not None)),
        )


class _RefusalCapture(logging.Handler):
    def __init__(self) -> None:
        super().__init__(logging.ERROR)
        self.refusals: list[Refusal] = []

    def emit(self, record: logging.LogRecord) -> None:
        refusal = getattr(record, "refusal", None)
        if refusal is not None:
            self.refusals.append(refusal)


def _rebind_everywhere(original: object, replacement: object) -> list[tuple[object, str]]:
    """Point every module-level name bound to ``original`` at ``replacement``.

    By-name imports (``from x import f``) hold their own binding, so patching the defining
    module alone would miss them.
    """
    rebound: list[tuple[object, str]] = []
    for module in list(sys.modules.values()):
        namespace = getattr(module, "__dict__", None)
        if not isinstance(namespace, dict):
            continue
        for name, value in list(namespace.items()):
            if value is original:
                setattr(module, name, replacement)
                rebound.append((module, name))
    return rebound


@contextmanager
def screen_tripwire() -> Iterator[None]:
    """Fail the run, after it ends, if the generator called the screen.

    The tripwire records the call and raises; ``run_codegen`` turns that raise into an
    ``SI_INTERNAL_DEFECT`` refusal, so the record is what makes the call fail the test.
    """
    from agentic_mbse.sysml import occurrence_extraction, subset_extraction, subset_profile

    calls: list[str] = []
    entries: tuple[Callable[..., Any], ...] = (
        subset_extraction.extract_subset_facts,
        subset_profile.evaluate_subset_profile,
        occurrence_extraction.extract_occurrence_structure,
    )
    rebound: list[tuple[object, str, object]] = []
    for entry in entries:

        def tripped(*_args: object, _name: str = entry.__name__, **_kwargs: object) -> Any:
            calls.append(_name)
            raise ScreenCalledError(f"the generator half called {_name}")

        rebound += [(m, n, entry) for m, n in _rebind_everywhere(entry, tripped)]
    try:
        yield
    finally:
        for module, name, original in rebound:
            setattr(module, name, original)
    if calls:
        raise ScreenCalledError(f"the generator half called the screen: {calls}")


@contextmanager
def _elaboration_spy(graphs: list[InstanceGraph]) -> Iterator[None]:
    from sysml_codegen.orchestration import elaborated_pipeline

    real = elaborated_pipeline.elaborate_model_paths

    def spy(*args: Any, **kwargs: Any) -> InstanceGraph:
        graph = real(*args, **kwargs)
        graphs.append(graph)
        return graph

    elaborated_pipeline.elaborate_model_paths = spy
    try:
        yield
    finally:
        elaborated_pipeline.elaborate_model_paths = real


@contextmanager
def _entry_point_spy(minted: set[tuple[str, DeclarationId]]) -> Iterator[None]:
    # ``sysml_codegen.elaboration`` re-exports the ``project`` function under the module's name.
    project = importlib.import_module("sysml_codegen.elaboration.project")
    real = project._Projection._entry_source

    def spy(self: Any, *, qualified_name: str, owner: Any, **kwargs: Any) -> Any:
        minted.add((qualified_name, owner.declaration_id))
        return real(self, qualified_name=qualified_name, owner=owner, **kwargs)

    project._Projection._entry_source = spy
    try:
        yield
    finally:
        project._Projection._entry_source = real


@contextmanager
def _refusal_capture() -> Iterator[_RefusalCapture]:
    capture = _RefusalCapture()
    logger = logging.getLogger("sysml_codegen")
    logger.addHandler(capture)
    try:
        yield capture
    finally:
        logger.removeHandler(capture)


def generator_half(model_root: Path) -> GeneratorObservation:
    """Run ``run_codegen`` on ``model_root`` (a file or a directory) and observe it."""
    from sysml_codegen.cli import GenerationConfig, run_codegen

    graphs: list[InstanceGraph] = []
    minted: set[tuple[str, DeclarationId]] = set()
    with (
        tempfile.TemporaryDirectory() as out,
        _refusal_capture() as capture,
        _elaboration_spy(graphs),
        _entry_point_spy(minted),
        screen_tripwire(),
    ):
        package_dir = Path(out) / "pkg"
        generated = run_codegen(GenerationConfig(output_path=package_dir, models_path=model_root))
        contract_path = package_dir / "contracts" / "model_contract.json"
        contract = json.loads(contract_path.read_text()) if generated else None

    if len(graphs) > 1:
        raise AssertionError(f"run_codegen elaborated {len(graphs)} times; expected at most one")
    if generated and capture.refusals:
        raise AssertionError(f"run_codegen generated but logged refusals: {capture.refusals}")
    if not generated and len(capture.refusals) != 1:
        raise AssertionError(
            f"run_codegen refused with {len(capture.refusals)} logged refusals; expected one"
        )
    return GeneratorObservation(
        generated=generated,
        refusal=None if generated else capture.refusals[0],
        graph=graphs[0] if graphs else None,
        contract=contract,
        entry_points=frozenset(minted),
    )


def declaration_in(model_root: Path, qualified_name: str) -> DeclarationId:
    """The identity of the one feature named ``qualified_name`` in the model (every seam is one)."""
    from agentic_mbse.sysml.syside_adapter import SysideAdapter

    from sysml_codegen.elaboration.identity import declaration_id_for

    model, diagnostics = SysideAdapter.load_model([model_root])
    if diagnostics.contains_errors():
        raise AssertionError([str(d) for d in diagnostics.all])
    named = [
        element
        for element in SysideAdapter.elements_of_type(model, "Feature", include_subtypes=True)
        if str(getattr(element, "qualified_name", None)) == qualified_name
    ]
    if len(named) != 1:
        raise AssertionError(f"{len(named)} features are named {qualified_name!r}")
    return declaration_id_for(named[0])


def _graph(observation: GeneratorObservation) -> InstanceGraph:
    if observation.graph is None:
        raise AssertionError("the run elaborated no graph, so it has no graph seam")
    return observation.graph


def _contract(observation: GeneratorObservation) -> dict[str, Any]:
    if observation.contract is None:
        raise AssertionError("the run wrote no package, so it has no catalog seam")
    return observation.contract


def _graph_attr(observation: GeneratorObservation, declaration: DeclarationId) -> Any:
    """How many attribute nodes the instance graph holds for the declaration."""
    nodes = [a for a in _graph(observation).attrs.values() if a.declaration_id == declaration]
    return {"count": len(nodes)}


def _attr_value(observation: GeneratorObservation, declaration: DeclarationId) -> Any:
    """Each attribute node of the declaration: its value and where the value came from."""
    nodes = [a for a in _graph(observation).attrs.values() if a.declaration_id == declaration]
    return sorted(
        ({"value": a.value, "value_site": a.value_site.value} for a in nodes),
        key=lambda n: (n["value_site"], repr(n["value"])),
    )


def _entry_point(observation: GeneratorObservation, declaration: DeclarationId) -> Any:
    """The entry points projection minted from a node of the declaration, by public key."""
    return sorted(name for name, owner in observation.entry_points if owner == declaration)


def _catalog_usage(observation: GeneratorObservation, declaration: DeclarationId) -> Any:
    """The catalog's disposition of the constraint usage."""
    catalog = _contract(observation)["constraint_catalog"]
    (record,) = [
        r for r in catalog["usage_records"] if r["declaration_id"] == declaration.to_wire()
    ]
    return {"kind": record["disposition_kind"], "reason": record["disposition_reason"]}


def _calc_compilability(observation: GeneratorObservation, declaration: DeclarationId) -> Any:
    """Each calc node of the usage: its compilability and the names of its outputs."""
    nodes = [c for c in _graph(observation).calcs.values() if c.declaration_id == declaration]
    return sorted(
        (
            {"compilability": c.compilability.value, "outputs": sorted(c.output_names.values())}
            for c in nodes
        ),
        key=lambda n: (n["compilability"], n["outputs"]),
    )


def _occurrences(observation: GeneratorObservation, declaration: DeclarationId) -> Any:
    """The occurrence indices the instance graph holds for the part usage (null: unindexed)."""
    records = [
        o for o in _graph(observation).occurrences.values() if o.effective_usage_id == declaration
    ]
    indices = [o.occurrence_index for o in records]
    return {"count": len(records), "indices": sorted(indices, key=lambda i: (i is not None, i))}


def seam_value(
    observation: GeneratorObservation, kind: SeamKind, declaration: DeclarationId
) -> Any:
    """The fact a stored seam asserts about ``declaration``, read from this run's output."""
    from tests.helpers.subset_profile.cases import SeamKind

    readers: dict[SeamKind, Callable[[GeneratorObservation, DeclarationId], Any]] = {
        SeamKind.GRAPH_ATTR: _graph_attr,
        SeamKind.ATTR_VALUE: _attr_value,
        SeamKind.ENTRY_POINT: _entry_point,
        SeamKind.CATALOG_USAGE: _catalog_usage,
        SeamKind.CALC_COMPILABILITY: _calc_compilability,
        SeamKind.OCCURRENCES: _occurrences,
    }
    return readers[kind](observation, declaration)


def screen_half(model_root: Path) -> SubsetProfileResult:
    """Run the screen on ``model_root`` (a file or a directory) as agentic-mbse's callers do."""
    from agentic_mbse.sysml.subset_extraction import extract_subset_facts
    from agentic_mbse.sysml.subset_profile import evaluate_subset_profile
    from agentic_mbse.sysml.syside_adapter import SysideAdapter

    model, diagnostics = SysideAdapter.load_model([model_root])
    if diagnostics.contains_errors():
        raise AssertionError([str(d) for d in diagnostics.all])
    return evaluate_subset_profile(extract_subset_facts(model))
