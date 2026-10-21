"""``check`` gives every case's stored generator answer (Item 2b Success Criterion 4).

For every 2a case, ``run_check`` reports the generator outcome, codes and site reasons the case
stores.

Licensed.
"""

from __future__ import annotations

import pytest

from sysml_codegen.cli import CheckRequest, prepare, run_check
from tests.conftest import requires_license
from tests.helpers.subset_profile import cases
from tests.helpers.subset_profile.cases import GeneratorOutcome, GeneratorRun, StoredAnswer

pytestmark = requires_license


def _generator_run(generator: prepare.Prepared | prepare.Refused) -> GeneratorRun:
    if isinstance(generator, prepare.Prepared):
        return GeneratorRun(GeneratorOutcome.GENERATED, (), ())
    items = generator.refusal.items
    return GeneratorRun(
        GeneratorOutcome.REFUSED,
        tuple(sorted(item.code.value for item in items)),
        tuple(sorted(item.reason for item in items if item.reason is not None)),
    )


@pytest.mark.parametrize("answer", cases.all_answers(), ids=lambda a: a.case_id)
def test_check_reports_the_stored_generator_answer(answer: StoredAnswer):
    request = CheckRequest(prepare.LiveModels((cases.model_root(answer),)), "generated_code", None)
    assert _generator_run(run_check(request)) == answer.generator.run
