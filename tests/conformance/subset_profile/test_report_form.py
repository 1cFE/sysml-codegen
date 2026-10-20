"""``generate`` and ``check`` print the same report for the same model and destination (Item 2b).

Spec Success Criterion 10, design D5 and Validation 10. On every 2a case, ``check --output``
and then ``generate`` run on the same model and the same, still empty, destination. The report
lines each prints must be identical, in order: the refusal record or the "builds" line, the
destination, the screen with every finding, any disagreement, and readiness. The writers log
under the same logger name, so a report line is told apart by the module that logged it:
``cli/readiness.py``, or ``cli/prepare.py`` for a refusal record.

Licensed.
"""

from __future__ import annotations

import logging
import sys

import pytest

from sysml_codegen import cli
from tests.conftest import requires_license
from tests.helpers.subset_profile import cases
from tests.helpers.subset_profile.cases import StoredAnswer

pytestmark = requires_license

#: The modules that print the report: the renderer, and ``prepare.log_refused`` for a refusal.
_REPORT_MODULES = frozenset({"readiness", "prepare"})


def _report_lines(caplog: pytest.LogCaptureFixture) -> list[tuple[str, str]]:
    return [(r.levelname, r.getMessage()) for r in caplog.records if r.module in _REPORT_MODULES]


def _main(monkeypatch: pytest.MonkeyPatch, *argv: str) -> None:
    monkeypatch.setattr(sys, "argv", ["sysml-codegen", *argv])
    with pytest.raises(SystemExit):
        cli.main()


@pytest.mark.parametrize("answer", cases.all_answers(), ids=lambda a: a.case_id)
def test_generate_and_check_print_the_same_report(
    answer: StoredAnswer, monkeypatch, tmp_path, caplog
):
    caplog.set_level(logging.INFO, logger="sysml_codegen")
    args = ["--models", str(cases.model_root(answer)), "--output", str(tmp_path / "pkg")]
    _main(monkeypatch, "check", *args)
    checked = _report_lines(caplog)
    caplog.clear()
    _main(monkeypatch, "generate", *args)
    assert _report_lines(caplog) == checked
    assert checked[-1][1].startswith(("Readiness: ", "  - "))
