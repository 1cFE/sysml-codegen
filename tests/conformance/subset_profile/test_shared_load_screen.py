"""The screen reads the same answer from the model the generator just elaborated (Item 2b B1).

Design D2 gives a command one SysIDE load, shared by the generator and the screen, and the
screen runs second. That is only sound if elaboration leaves what the screen extracts
unchanged. 2a stored every case's screen answer from a fresh load
(``test_screen_half.py``); here the generator first builds its context from the shared load,
refused or not, and the screen then runs on that same loaded model and must give the stored
answer. No 2a case has parse errors (a parse refusal carries no code, so 2a could not store
one), so every case loads.

Licensed.
"""

from __future__ import annotations

import pytest
from agentic_mbse.sysml.conformance_case import screen_answer
from agentic_mbse.sysml.subset_extraction import extract_subset_facts
from agentic_mbse.sysml.subset_profile import evaluate_subset_profile

from sysml_codegen.core.errors import CodeGenerationError, SysMLParsingError
from sysml_codegen.elaboration import ElaborationDiagnosticError, ElaborationError
from sysml_codegen.orchestration.elaborated_pipeline import LiveLoad, load_live_models
from sysml_codegen.orchestration.exact_pipeline_context import (
    build_exact_pipeline_context_from_live_load,
)
from tests.conftest import requires_license
from tests.helpers.subset_profile import cases
from tests.helpers.subset_profile.cases import StoredAnswer

pytestmark = requires_license


@pytest.mark.parametrize("answer", cases.all_answers(), ids=lambda a: a.case_id)
def test_screen_after_elaboration_equals_the_stored_screen_answer(answer: StoredAnswer):
    loaded = load_live_models([cases.model_root(answer)])
    assert isinstance(loaded, LiveLoad), loaded
    try:
        build_exact_pipeline_context_from_live_load(loaded)
    except (
        CodeGenerationError,
        ElaborationDiagnosticError,
        ElaborationError,
        SysMLParsingError,
    ):
        pass  # a refused case: the generator still elaborated as far as it goes

    live = screen_answer(evaluate_subset_profile(extract_subset_facts(loaded.extractor.model)))
    assert live == cases.screen_of(answer)
