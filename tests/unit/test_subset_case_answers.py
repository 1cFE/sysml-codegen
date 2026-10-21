"""Stored case answers load only in their stored form (Item 2a design D1).

Pure: every document is written under ``tmp_path``.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from sysml_codegen.elaboration.diagnostics import SiteReason
from tests.helpers.subset_profile.cases import (
    CaseAnswerError,
    GeneratorOutcome,
    LossDisposition,
    SeamKind,
    load_stored_answer,
)

CASE_ID = "binding-source__expression_source__owner_instantiated"
ANSWER = {
    "id": CASE_ID,
    "generator": {
        "outcome": "refused",
        "codes": ["SI_EXPRESSION_SOURCE_UNSUPPORTED", "SI_TYPE_INVALID"],
        "reasons": ["binding_source_form_unsupported"],
        "witnesses": ["ES-004"],
        "stubs": [{"output": "fx::Twice::r", "reason": "binding_source_form_unsupported"}],
        "seams": [{"kind": "entry_point", "declaration": "fx::Site::a", "expect": {"count": 1}}],
    },
    "construct": {"file": "model.sysml", "lines": [6, 9], "description": "a tuple actual"},
    "loss": {
        "family": "string_value",
        "disposition": "candidate_refusal",
        "rg1": "RG1-3",
        "control": "a_control_case",
    },
}


def _stored(tmp_path: Path, document: dict, name: str = CASE_ID) -> Path:
    path = tmp_path / f"{name}.json"
    path.write_text(json.dumps(document))
    return path


def test_stored_answer_loads_every_field(tmp_path):
    answer = load_stored_answer(_stored(tmp_path, ANSWER))
    assert answer.case_id == CASE_ID
    run = answer.generator.run
    assert run.outcome is GeneratorOutcome.REFUSED
    assert run.codes == ("SI_EXPRESSION_SOURCE_UNSUPPORTED", "SI_TYPE_INVALID")
    assert run.reasons == (SiteReason.BINDING_SOURCE_FORM_UNSUPPORTED,)
    assert answer.generator.witnesses == ("ES-004",)
    assert answer.generator.stubs[0].reason is SiteReason.BINDING_SOURCE_FORM_UNSUPPORTED
    assert answer.generator.seams[0].kind is SeamKind.ENTRY_POINT
    assert answer.generator.seams[0].expect == {"count": 1}
    assert (answer.construct.first_line, answer.construct.last_line) == (6, 9)
    assert answer.loss is not None
    assert answer.loss.disposition is LossDisposition.CANDIDATE_REFUSAL
    assert answer.loss.rg1 == "RG1-3"
    assert answer.loss.control == "a_control_case"


def test_loss_is_optional(tmp_path):
    document = {key: ANSWER[key] for key in ("id", "construct", "generator")}
    assert load_stored_answer(_stored(tmp_path, document)).loss is None


def _edited(edit) -> dict:
    document = copy.deepcopy(ANSWER)
    edit(document)
    return document


@pytest.mark.parametrize(
    ("document", "message"),
    [
        (_edited(lambda d: d.update(extra=1)), "unknown \\['extra'\\]"),
        (_edited(lambda d: d.pop("generator")), "missing \\['generator'\\]"),
        (_edited(lambda d: d.pop("construct")), "missing \\['construct'\\]"),
        (_edited(lambda d: d["generator"].update(codes=["SI_B", "SI_A"])), "must be sorted"),
        (_edited(lambda d: d["generator"].update(codes=[])), "a refused run has codes"),
        (_edited(lambda d: d["generator"].update(outcome="generated")), "a refused run has"),
        (_edited(lambda d: d["generator"].update(reasons=["not_a_reason"])), "not a SiteReason"),
        (_edited(lambda d: d["generator"].update(outcome="skipped")), "not a GeneratorOutcome"),
        (_edited(lambda d: d["generator"]["seams"][0].update(kind="x")), "not a SeamKind"),
        (_edited(lambda d: d["generator"]["stubs"][0].pop("reason")), "missing \\['reason'\\]"),
        (_edited(lambda d: d["construct"].update(lines=[9, 6])), "expected \\[first, last\\]"),
        (_edited(lambda d: d["loss"].update(rg1="RG1-x")), "expected RG1-<n>"),
        (_edited(lambda d: d["loss"].pop("rg1")), "names its RG1-<n>"),
        (_edited(lambda d: d["loss"].update(disposition="rg2_pending")), "names its RG1-<n>"),
        (_edited(lambda d: d["loss"].pop("control")), "missing \\['control'\\]"),
    ],
)
def test_stored_answer_refuses_a_malformed_document(tmp_path, document, message):
    with pytest.raises(CaseAnswerError, match=message):
        load_stored_answer(_stored(tmp_path, document))


def test_stored_answer_id_is_its_file_name(tmp_path):
    with pytest.raises(CaseAnswerError, match="is not the file name"):
        load_stored_answer(_stored(tmp_path, ANSWER, name="another_case"))
