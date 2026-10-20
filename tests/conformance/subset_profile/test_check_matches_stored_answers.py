"""``check`` gives every case's stored answers, and computes the recorded disagreements itself.

Item 2b spec Success Criterion 4, design Validation 4. For every 2a case, ``run_check``:

- reports the generator outcome, codes and site reasons the case stores;
- reports the screen verdict and findings the case stores, under 2a's normalization (rule,
  outcome and line);
- computes the disagreement the stored answers imply, through ``REASON_MAPPING``, and every
  disagreement the record lists (read through ``cases.read_disagreements``) appears. The
  record is read here, as the oracle, and never by ``src/``.

Licensed.
"""

from __future__ import annotations

from collections import Counter
from functools import cache
from pathlib import Path

import pytest

from sysml_codegen.cli import CheckRequest, prepare, run_check
from sysml_codegen.cli.report import Report
from sysml_codegen.subset_screen import ScreenAssessed
from tests.conftest import FIXTURES_DIR, requires_license
from tests.helpers.subset_profile import cases
from tests.helpers.subset_profile.cases import GeneratorOutcome, GeneratorRun, StoredAnswer

pytestmark = requires_license

ANSWERS = cases.all_answers()
ENTRIES = cases.read_disagreements()


@cache
def _check(model_root: Path) -> Report:
    return run_check(CheckRequest(prepare.LiveModels((model_root,)), "generated_code", None))


def _generator_run(report: Report) -> GeneratorRun:
    generator = report.generator
    if isinstance(generator, prepare.Prepared):
        return GeneratorRun(GeneratorOutcome.GENERATED, (), ())
    items = generator.refusal.items
    return GeneratorRun(
        GeneratorOutcome.REFUSED,
        tuple(sorted(item.code.value for item in items)),
        tuple(sorted(item.reason for item in items if item.reason is not None)),
    )


def _computed(subject: str, report: Report) -> cases.Disagreement | None:
    found = report.disagreement
    if found is None:
        return None
    return cases.Disagreement(subject, found.kind, found.generator_codes, found.screen_reasons)


@pytest.mark.parametrize("answer", ANSWERS, ids=lambda a: a.case_id)
def test_check_reports_the_stored_generator_answer(answer: StoredAnswer):
    assert _generator_run(_check(cases.model_root(answer))) == answer.generator.run


@pytest.mark.parametrize("answer", ANSWERS, ids=lambda a: a.case_id)
def test_check_reports_the_stored_screen_answer(answer: StoredAnswer):
    screen = _check(cases.model_root(answer)).screen
    assert isinstance(screen, ScreenAssessed), screen
    stored = cases.screen_of(answer)
    assert screen.verdict == stored.verdict
    assert Counter((f.rule_id, f.outcome, f.source_line) for f in screen.findings) == Counter(
        (f.rule, f.outcome, f.line) for f in stored.findings
    )


@pytest.mark.parametrize("answer", ANSWERS, ids=lambda a: a.case_id)
def test_check_computes_the_disagreement_the_stored_answers_imply(answer: StoredAnswer):
    expected = cases.disagreement(answer.subject, answer.generator.run, cases.screen_of(answer))
    assert _computed(answer.subject, _check(cases.model_root(answer))) == expected


@pytest.mark.parametrize("entry", ENTRIES, ids=lambda e: e.disagreement.subject)
def test_every_recorded_disagreement_appears(entry: cases.DisagreementEntry):
    subject = entry.disagreement.subject
    kind, _, key = subject.partition(":")
    if kind == "case":
        root = cases.model_root(cases.load_answer(key))
    else:
        root = FIXTURES_DIR / key
    assert _computed(subject, _check(root)) == entry.disagreement
