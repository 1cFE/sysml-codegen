"""Skew, a failing screen and a screen-only refusal leave the generator's answer alone (Item 2b).

Spec Success Criteria 7, 8 and 9, design Validation 7-9. Each runs on a case that builds and
a case the generator refuses, through both commands' public entry point.

- Skew: the installed profile version patched older and newer than the pin. The outcome is
  unchanged, the screen is not assessed, both versions are named, the model is never ready,
  and no ``ImportError`` text appears. As design § Implementation Notes says, this is how
  "isolated artifacts" is met: the adapter is dropped from ``sys.modules`` and the installed
  version patched, so the real import path runs, and the adapter must stay unimported.
- The screen raising at each of its three points, on cases with findings so the renderer
  runs: outcome unchanged, screen not assessed.
- A constructed witness for "the screen refuses, the generator builds": the case that builds
  is screened with another case's real refused result. ``check`` reports the disagreement and
  exits 3; ``generate`` writes the same bytes as without it and exits 0.

Licensed.
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

import pytest
from agentic_mbse.sysml import subset_extraction, subset_profile
from agentic_mbse.sysml.subset_profile import Outcome

from sysml_codegen import cli, subset_profile_adapter
from sysml_codegen.cli.readiness import DisagreementKind
from tests.conftest import requires_license
from tests.helpers.subset_profile import cases, observe
from tests.helpers.subset_profile.cases import GeneratorOutcome

pytestmark = requires_license

#: A case the generator builds.
BUILDS_CASE = "anonymous-declaration__attribute_usage"
#: A case refused by ``prepare``'s last step.
REFUSED_CASE = "output-naming__param_field_collision"
#: A case that builds, with one screen finding, so the renderer runs.
SCREENED_BUILDS_CASE = "binding-source__expression_source__owner_other"
#: Exit codes when the screen gives no answer, generate's and check's, by generator outcome.
EXITS = {
    GeneratorOutcome.GENERATED: {"generate": 0, "check": 3},
    GeneratorOutcome.REFUSED: {"generate": 1, "check": 1},
}
PIN = subset_profile.SUBSET_PROFILE_VERSION
ADAPTER = "sysml_codegen.subset_profile_adapter"


def _main(monkeypatch: pytest.MonkeyPatch, *argv: str | Path) -> int:
    monkeypatch.setattr(sys, "argv", ["sysml-codegen", *map(str, argv)])
    with pytest.raises(SystemExit) as exit_info:
        cli.main()
    code = exit_info.value.code
    assert isinstance(code, int)
    return code


def _exit(case_id: str, command: str) -> int:
    return EXITS[cases.load_answer(case_id).generator.run.outcome][command]


def _run(monkeypatch, command: str, case_id: str, output: Path) -> int:
    models = cases.model_root(cases.load_answer(case_id))
    return _main(monkeypatch, command, "--models", models, "--output", output)


def _infos(caplog: pytest.LogCaptureFixture) -> list[str]:
    return [r.getMessage() for r in caplog.records if r.levelno == logging.INFO]


def _tree(root: Path) -> dict[str, bytes]:
    return {
        p.relative_to(root).as_posix(): p.read_bytes()
        for p in sorted(root.rglob("*"))
        if p.is_file() and not os.path.islink(p)
    }


@pytest.mark.parametrize("installed", ["subset-profile/v1", "subset-profile/v3"])
@pytest.mark.parametrize("command", ["generate", "check"])
@pytest.mark.parametrize("case_id", [BUILDS_CASE, REFUSED_CASE])
def test_profile_skew_leaves_the_generator_s_answer(
    installed, command, case_id, monkeypatch, tmp_path, caplog
):
    caplog.set_level(logging.INFO, logger="sysml_codegen")
    monkeypatch.setattr(subset_profile, "SUBSET_PROFILE_VERSION", installed)
    monkeypatch.delitem(sys.modules, ADAPTER, raising=False)
    assert _run(monkeypatch, command, case_id, tmp_path / "pkg") == _exit(case_id, command)
    assert ADAPTER not in sys.modules
    screen = next(m for m in _infos(caplog) if m.startswith("Screen not assessed: "))
    assert repr(installed) in screen and repr(PIN) in screen
    assert "Readiness: ready" not in _infos(caplog)
    assert "ImportError" not in caplog.text


def _raising(*_args: object, **_kwargs: object) -> None:
    raise RuntimeError("probe: the screen broke")


@pytest.mark.parametrize(
    ("module", "name"),
    [
        (subset_extraction, "extract_subset_facts"),
        (subset_profile, "evaluate_subset_profile"),
        (subset_profile_adapter, "render_finding"),
    ],
    ids=lambda v: v if isinstance(v, str) else v.__name__,
)
@pytest.mark.parametrize("command", ["generate", "check"])
@pytest.mark.parametrize("case_id", [SCREENED_BUILDS_CASE, "agreeing-refused"])
def test_a_failing_screen_leaves_the_generator_s_answer(
    module, name, command, case_id, monkeypatch, tmp_path, caplog
):
    if case_id == "agreeing-refused":
        case_id = _agreeing_refused_case()
    assert cases.screen_of(cases.load_answer(case_id)).findings
    caplog.set_level(logging.INFO, logger="sysml_codegen")
    monkeypatch.setattr(module, name, _raising)
    assert _run(monkeypatch, command, case_id, tmp_path / "pkg") == _exit(case_id, command)
    assert (
        "Screen not assessed: the screen failed: RuntimeError: probe: the screen broke"
        in _infos(caplog)
    )


def _agreeing_refused_case() -> str:
    """A case the generator refuses, whose screen refuses it with a code that agrees."""
    for answer in cases.all_answers():
        refused = [f for f in cases.screen_of(answer).findings if f.outcome is Outcome.REFUSED]
        if (
            answer.generator.run.outcome is GeneratorOutcome.REFUSED
            and refused
            and cases.disagreement(answer.subject, answer.generator.run, cases.screen_of(answer))
            is None
        ):
            return answer.case_id
    raise AssertionError("no case where the screen and the generator agree on a refusal")


@pytest.fixture(scope="module")
def refused_screen_result():
    root = cases.model_root(cases.load_answer(_agreeing_refused_case()))
    result = observe.screen_half(root)
    assert any(f.outcome is Outcome.REFUSED for f in result.findings)
    return result


def test_the_screen_refusing_a_model_that_builds_is_a_disagreement_on_check(
    refused_screen_result, monkeypatch, tmp_path, caplog
):
    caplog.set_level(logging.INFO, logger="sysml_codegen")
    monkeypatch.setattr(
        subset_profile, "evaluate_subset_profile", lambda *_a, **_k: refused_screen_result
    )
    assert _run(monkeypatch, "check", BUILDS_CASE, tmp_path / "pkg") == 3
    kind = DisagreementKind.SCREEN_REFUSES_GENERATOR_BUILDS
    infos = _infos(caplog)
    assert any(m.startswith(f"Disagreement: {kind}:") for m in infos)
    assert f"  - the screen and the generator disagree ({kind})" in infos


def test_the_screen_refusing_a_model_that_builds_leaves_generate_building(
    refused_screen_result, monkeypatch, tmp_path, caplog
):
    plain = tmp_path / "plain"
    assert _run(monkeypatch, "generate", BUILDS_CASE, plain) == 0
    caplog.set_level(logging.INFO, logger="sysml_codegen")
    monkeypatch.setattr(
        subset_profile, "evaluate_subset_profile", lambda *_a, **_k: refused_screen_result
    )
    witnessed = tmp_path / "witnessed"
    assert _run(monkeypatch, "generate", BUILDS_CASE, witnessed) == 0
    assert _tree(witnessed) == _tree(plain)
    assert any(
        m.startswith(f"Disagreement: {DisagreementKind.SCREEN_REFUSES_GENERATOR_BUILDS}:")
        for m in _infos(caplog)
    )
