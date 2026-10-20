"""``assess_screen`` on the shared load gives the stored screen answer, and never raises (Item 2b).

Design D2, D7, D17. For every 2a case the live screen, run through ``assess_screen`` on a
``load_live_models`` load, has the stored verdict and the stored findings (rule, outcome
and line), each rendered with its rule, outcome, qualification and a portable
``root-N/<path>`` file. When the screen, the reason mapping or the renderer raises, the whole
screen is not assessed, naming the failure. A model with parse errors is not assessed.

Licensed.
"""

from __future__ import annotations

from collections import Counter
from types import MappingProxyType

import pytest
from agentic_mbse.sysml import subset_extraction, subset_profile
from agentic_mbse.sysml.subset_profile import Outcome

from sysml_codegen import subset_profile_adapter
from sysml_codegen.orchestration.elaborated_pipeline import LiveLoad, load_live_models
from sysml_codegen.subset_screen import (
    NotAssessedCause,
    ScreenAssessed,
    ScreenNotAssessed,
    assess_screen,
)
from tests.conftest import requires_license
from tests.helpers.subset_profile import cases
from tests.helpers.subset_profile.cases import StoredAnswer

pytestmark = requires_license

#: A case whose screen refuses one finding (reason ``part_multiplicity_ordered``).
REFUSED_FINDING_CASE = "part-multiplicity__ordered__expanded_part_usage"
#: A case the generator builds.
BUILDS_CASE = "anonymous-declaration__attribute_usage"


def _loaded(case_id: str) -> LiveLoad:
    loaded = load_live_models([cases.model_root(cases.load_answer(case_id))])
    assert isinstance(loaded, LiveLoad), loaded
    return loaded


@pytest.mark.parametrize("answer", cases.all_answers(), ids=lambda a: a.case_id)
def test_the_screen_on_the_shared_load_gives_the_stored_answer(answer: StoredAnswer):
    loaded = load_live_models([cases.model_root(answer)])
    assert isinstance(loaded, LiveLoad), loaded
    result = assess_screen(loaded)
    assert isinstance(result, ScreenAssessed), result
    stored = cases.screen_of(answer)
    assert result.verdict == stored.verdict
    assert Counter((f.rule_id, f.outcome, f.source_line) for f in result.findings) == Counter(
        (f.rule, f.outcome, f.line) for f in stored.findings
    )
    for finding in result.findings:
        assert finding.source_file is None or finding.source_file.startswith("root-"), finding
        assert (finding.code is not None) == (finding.outcome is Outcome.REFUSED)


@pytest.mark.parametrize(
    ("module", "name"),
    [
        (subset_extraction, "extract_subset_facts"),
        (subset_profile, "evaluate_subset_profile"),
        (subset_profile_adapter, "render_finding"),
    ],
    ids=["extract_subset_facts", "evaluate_subset_profile", "render_finding"],
)
def test_a_screen_that_raises_is_not_assessed(monkeypatch, module, name):
    def crash(*_args, **_kwargs):
        raise RuntimeError(f"probe: {name} crashed")

    monkeypatch.setattr(module, name, crash)
    # The refused-finding case has findings, so the renderer is reached too.
    result = assess_screen(_loaded(REFUSED_FINDING_CASE))
    assert result == ScreenNotAssessed(
        NotAssessedCause.SCREEN_FAILED, f"the screen failed: RuntimeError: probe: {name} crashed"
    )


def test_a_refused_finding_mapped_to_no_refusal_makes_the_screen_not_assessed(monkeypatch):
    mapping = dict(subset_profile_adapter.REASON_MAPPING)
    mapping["part_multiplicity_ordered"] = subset_profile_adapter.NO_REFUSAL
    monkeypatch.setattr(subset_profile_adapter, "REASON_MAPPING", MappingProxyType(mapping))
    result = assess_screen(_loaded(REFUSED_FINDING_CASE))
    assert isinstance(result, ScreenNotAssessed)
    assert result.cause is NotAssessedCause.SCREEN_FAILED
    assert "part-multiplicity/ordered" in result.reason
    assert "maps to NO_REFUSAL" in result.reason


def test_a_building_case_is_assessed():
    assert isinstance(assess_screen(_loaded(BUILDS_CASE)), ScreenAssessed)


def test_a_model_with_parse_errors_is_not_assessed(tmp_path):
    model = tmp_path / "model"
    model.mkdir()
    (model / "model.sysml").write_text("package SyntaxProbe;\npart def Broken { attribute\n")
    assert assess_screen(load_live_models([model])) == ScreenNotAssessed(
        NotAssessedCause.PARSE_ERRORS, "the model has parse errors"
    )
