"""The two halves of a subset-profile case, each observed through its public surface.

Generator half: ``run_codegen`` on the case model, exactly as a user runs it. The refusal
comes from the ``extra={"refusal": ...}`` payload on its ERROR records, never from message
text, where a code can also appear inside detail. The instance graph comes from a spy on
``elaborated_pipeline.elaborate_model_paths`` as the exact pipeline context calls it, and the
catalog from the written ``contracts/model_contract.json``. The screen's three entry points
are tripwired for the run, so a generator answer can never be the screen's answer in
disguise.

Screen half: ``SysideAdapter.load_model``, then ``extract_subset_facts``, then
``evaluate_subset_profile``, as an agentic-mbse caller runs them.

Both halves need a syside license.
"""

from __future__ import annotations

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
    from tests.helpers.subset_profile.cases import GeneratorRun


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
def _screen_tripwire() -> Iterator[None]:
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
    with (
        tempfile.TemporaryDirectory() as out,
        _refusal_capture() as capture,
        _elaboration_spy(graphs),
        _screen_tripwire(),
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
    )


def screen_half(model_root: Path) -> SubsetProfileResult:
    """Run the screen on ``model_root`` (a file or a directory) as agentic-mbse's callers do."""
    from agentic_mbse.sysml.subset_extraction import extract_subset_facts
    from agentic_mbse.sysml.subset_profile import evaluate_subset_profile
    from agentic_mbse.sysml.syside_adapter import SysideAdapter

    model, diagnostics = SysideAdapter.load_model([model_root])
    if diagnostics.contains_errors():
        raise AssertionError([str(d) for d in diagnostics.all])
    return evaluate_subset_profile(extract_subset_facts(model))
