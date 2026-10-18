"""Spike S1 (throwaway): the two halves of a conformance case, in-process.

Generator half: `run_codegen` on the case model with the screen patched to raise
(tripwire), observing the refusal codes from the ERROR log records and, through a spy on
`elaborated_pipeline.elaborate_model_paths`, the calc nodes' compilability.
Screen half: `SysideAdapter.load_model` -> `extract_subset_facts` -> `evaluate_subset_profile`.
"""

from __future__ import annotations

import logging
import re
import sys
import tempfile
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

PROBES = Path("/home/reid/src/subset-conformance/agentic-mbse/tests/fixtures/subset_profile/probes")
SPIKE = Path(__file__).resolve().parent
CODE_RE = re.compile(r"\b(SI_[A-Z0-9_]+):")


@dataclass(frozen=True)
class Case:
    case_id: str
    model: Path


def probe(name: str) -> Case:
    return Case(name, PROBES / name / "model.sysml")


def local(name: str) -> Case:
    return Case(name, SPIKE / "models" / name / "model.sysml")


CASES: list[Case] = [
    probe("candidate-es-002__constraint_binds_calc_input__binding_value"),
    probe("part-multiplicity__range__expanded_part_usage"),
    probe("candidate-es-008__nested_named_subset__part_usage"),
    local("recursive_containment"),
    probe("invocation-callable__unsupported_callable__attribute_value"),
    local("calc_stub_operator"),
    local("calc_stub_gt"),
    probe("candidate-es-009__composition_by_subsetting__part_usage"),
    probe("binding-source__expression_source__owner_instantiated"),
    probe("indexed-reference__indexed_reference__attribute_value"),
    probe("string-value-omission__numeric_value__attribute_value"),
]


@dataclass
class GenObs:
    ok: bool
    codes: tuple[str, ...]
    stubs: tuple[tuple[str, str], ...]
    first_error: str = ""
    seconds: float = 0.0

    def key(self) -> tuple[Any, ...]:
        return (self.ok, self.codes, self.stubs)


class _Capture(logging.Handler):
    def __init__(self) -> None:
        super().__init__(logging.ERROR)
        self.messages: list[str] = []

    def emit(self, record: logging.LogRecord) -> None:
        self.messages.append(record.getMessage())


class ScreenCalled(AssertionError):
    pass


def _patch_everywhere(original: Any, replacement: Any) -> list[tuple[Any, str, Any]]:
    patched = []
    for mod in list(sys.modules.values()):
        d = getattr(mod, "__dict__", None)
        if not isinstance(d, dict):
            continue
        for k, v in list(d.items()):
            if v is original:
                patched.append((mod, k, v))
                setattr(mod, k, replacement)
    return patched


@contextmanager
def screen_tripwire():
    from agentic_mbse.sysml import occurrence_extraction, subset_extraction, subset_profile

    def boom(*_a: Any, **_k: Any) -> Any:
        raise ScreenCalled("generator half called the screen")

    patched: list[tuple[Any, str, Any]] = []
    for fn in (
        subset_extraction.extract_subset_facts,
        subset_profile.evaluate_subset_profile,
        occurrence_extraction.extract_occurrence_structure,
    ):
        patched += _patch_everywhere(fn, boom)
    try:
        yield len(patched)
    finally:
        for mod, k, v in patched:
            setattr(mod, k, v)


def run_generator(case: Case) -> GenObs:
    from sysml_codegen.cli import GenerationConfig, run_codegen
    from sysml_codegen.orchestration import elaborated_pipeline

    graphs: list[Any] = []
    real = elaborated_pipeline.elaborate_model_paths

    def spy(*a: Any, **k: Any) -> Any:
        g = real(*a, **k)
        graphs.append(g)
        return g

    cap = _Capture()
    root = logging.getLogger()
    root.addHandler(cap)
    elaborated_pipeline.elaborate_model_paths = spy
    t0 = time.perf_counter()
    try:
        with screen_tripwire(), tempfile.TemporaryDirectory() as out:
            ok = run_codegen(GenerationConfig(output_path=Path(out) / "pkg", models_path=case.model))
    finally:
        elaborated_pipeline.elaborate_model_paths = real
        root.removeHandler(cap)
    dt = time.perf_counter() - t0
    codes = tuple(sorted(c for m in cap.messages for c in CODE_RE.findall(m)))
    stubs: tuple[tuple[str, str], ...] = ()
    if graphs:
        stubs = tuple(
            sorted(
                (c.calc_def_qualified_name, c.compilability.value)
                for c in graphs[0].calcs.values()
                if c.compilability.value != "fully_compilable"
            )
        )
    first = cap.messages[0][:200] if cap.messages else ""
    return GenObs(ok, codes, stubs, first, dt)


@dataclass
class ScreenObs:
    verdict: str
    findings: tuple[tuple[str, str, str, str], ...]
    seconds_load: float = 0.0
    seconds_extract: float = 0.0
    seconds_eval: float = 0.0
    facts: Any = field(default=None, repr=False)


def run_screen(case: Case) -> ScreenObs:
    from agentic_mbse.sysml.subset_extraction import extract_subset_facts
    from agentic_mbse.sysml.subset_profile import evaluate_subset_profile
    from agentic_mbse.sysml.syside_adapter import SysideAdapter

    t0 = time.perf_counter()
    model, _diags = SysideAdapter.load_model([case.model])
    t1 = time.perf_counter()
    facts = extract_subset_facts(model)
    t2 = time.perf_counter()
    result = evaluate_subset_profile(facts)
    t3 = time.perf_counter()
    findings = tuple(
        sorted((f.rule_id, f.shape_id, str(f.context_id), str(f.outcome)) for f in result.findings)
    )
    return ScreenObs(str(result.verdict), findings, t1 - t0, t2 - t1, t3 - t2, facts)
