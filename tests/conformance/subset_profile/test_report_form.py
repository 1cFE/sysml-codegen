"""``check`` gives ``generate``'s answer and prints the same report, on every 2a case (Item 2b).

Spec Success Criteria 3 and 10, design D5, D6 and Validation 10. On every 2a case, ``check
--output`` and then ``generate`` run on the same model and the same, still empty, destination.

- ``check``'s exit code equals ``generate``'s: 0 when it builds, 1 when it refuses. Both equal
  the generator outcome the case stores. The generator's route alone decides (owner, Align Q1).
- The report lines each prints are identical, in order: the refusal record or the "builds"
  line, then the screen's findings and any disagreement. The writers log under the same logger
  name, so a report line is told apart by the module that logged it: ``cli/report.py``, or
  ``cli/prepare.py`` for the generator's answer.
- No line either command prints calls the model ready or clean. "not ready" is allowed: it is
  the generator's own refusal text from the base commit, which the refusal records pin.

Licensed.
"""

from __future__ import annotations

import logging
import re
import sys

import pytest

from sysml_codegen import cli
from tests.conftest import requires_license
from tests.helpers.subset_profile import cases
from tests.helpers.subset_profile.cases import GeneratorOutcome, StoredAnswer

pytestmark = requires_license

#: The modules that print the report: the renderer, and ``prepare`` for the generator's answer.
_REPORT_MODULES = frozenset({"report", "prepare"})
_EXIT = {GeneratorOutcome.GENERATED: 0, GeneratorOutcome.REFUSED: 1}
_OUTCOME_CLAIM = re.compile(r"(?<!not )\bready\b|\bclean\b|\breadiness\b", re.IGNORECASE)


def _report_lines(caplog: pytest.LogCaptureFixture) -> list[tuple[str, str]]:
    return [(r.levelname, r.getMessage()) for r in caplog.records if r.module in _REPORT_MODULES]


def _claims(caplog: pytest.LogCaptureFixture) -> list[str]:
    return [r.getMessage() for r in caplog.records if _OUTCOME_CLAIM.search(r.getMessage())]


def _main(monkeypatch: pytest.MonkeyPatch, *argv: str) -> int:
    monkeypatch.setattr(sys, "argv", ["sysml-codegen", *argv])
    with pytest.raises(SystemExit) as exit_info:
        cli.main()
    code = exit_info.value.code
    assert isinstance(code, int)
    return code


@pytest.mark.parametrize("answer", cases.all_answers(), ids=lambda a: a.case_id)
def test_check_gives_generate_s_answer_and_report(
    answer: StoredAnswer, monkeypatch, tmp_path, caplog
):
    caplog.set_level(logging.INFO, logger="sysml_codegen")
    args = ["--models", str(cases.model_root(answer)), "--output", str(tmp_path / "pkg")]
    checked_exit = _main(monkeypatch, "check", *args)
    checked = _report_lines(caplog)
    assert _claims(caplog) == []
    caplog.clear()
    generated_exit = _main(monkeypatch, "generate", *args)
    assert _claims(caplog) == []
    assert checked_exit == generated_exit == _EXIT[answer.generator.run.outcome]
    assert _report_lines(caplog) == checked
