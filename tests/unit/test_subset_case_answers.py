"""The stored subset-profile answers load only in their Appendix A form (Item 2a D1)."""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from sysml_codegen.elaboration.diagnostics import SiteReason
from tests.helpers.subset_profile.cases import (
    CaseAnswerError,
    CaseHome,
    GeneratorOutcome,
    LossDisposition,
    SeamKind,
    load_packaged_case,
    load_stored_answer,
)

CASE_ID = "binding-source__expression_source__owner_instantiated"
SCREEN = {
    "verdict": "refused",
    "findings": [
        {
            "rule": "binding-source",
            "shape": "expression_source",
            "context": "owner_instantiated",
            "outcome": "refused",
            "subject": "fx::Site::t::xs",
        }
    ],
}
ANSWER = {
    "id": CASE_ID,
    "home": "codegen",
    "generator": {
        "outcome": "refused",
        "codes": ["SI_EXPRESSION_SOURCE_UNSUPPORTED", "SI_TYPE_INVALID"],
        "reasons": ["binding_source_form_unsupported"],
        "witnesses": ["ES-004"],
        "stubs": [{"output": "fx::Twice::r", "reason": "binding_source_form_unsupported"}],
        "seams": [{"kind": "entry_point", "declaration": "fx::Site::a", "expect": {"count": 1}}],
    },
    "screen": SCREEN,
    "loss": {"family": "string_value", "disposition": "candidate_refusal", "rg1": "RG1-3"},
}
PACKAGED = {
    "schema": "subset-case/1",
    "construct": {"file": "model.sysml", "lines": [6, 9]},
    "screen": SCREEN,
    "agentic_site_witnesses": ["AS-012"],
    "provenance": {"from_probe": CASE_ID, "note": "moved from the Item 1 probe"},
}


def _stored(tmp_path: Path, document: dict, name: str = CASE_ID) -> Path:
    path = tmp_path / f"{name}.json"
    path.write_text(json.dumps(document))
    return path


def _packaged(tmp_path: Path, document: dict) -> Path:
    case_dir = tmp_path / CASE_ID
    case_dir.mkdir()
    (case_dir / "case.json").write_text(json.dumps(document))
    return case_dir


def test_stored_answer_loads_every_field(tmp_path):
    answer = load_stored_answer(_stored(tmp_path, ANSWER))
    assert answer.case_id == CASE_ID
    assert answer.home is CaseHome.CODEGEN
    assert answer.generator.outcome is GeneratorOutcome.REFUSED
    assert answer.generator.codes == ("SI_EXPRESSION_SOURCE_UNSUPPORTED", "SI_TYPE_INVALID")
    assert answer.generator.reasons == (SiteReason.BINDING_SOURCE_FORM_UNSUPPORTED,)
    assert answer.generator.witnesses == ("ES-004",)
    assert answer.generator.stubs[0].reason is SiteReason.BINDING_SOURCE_FORM_UNSUPPORTED
    assert answer.generator.seams[0].kind is SeamKind.ENTRY_POINT
    assert answer.generator.seams[0].expect == {"count": 1}
    assert answer.screen is not None
    assert answer.screen.findings[0].context == "owner_instantiated"
    assert answer.loss is not None
    assert answer.loss.disposition is LossDisposition.CANDIDATE_REFUSAL
    assert answer.loss.rg1 == "RG1-3"


def test_agentic_home_answer_has_no_screen_block(tmp_path):
    document = {key: value for key, value in ANSWER.items() if key not in {"screen", "loss"}}
    document["home"] = "agentic"
    answer = load_stored_answer(_stored(tmp_path, document))
    assert answer.screen is None
    assert answer.loss is None


def _edited(edit) -> dict:
    document = copy.deepcopy(ANSWER)
    edit(document)
    return document


@pytest.mark.parametrize(
    ("document", "message"),
    [
        (_edited(lambda d: d.update(extra=1)), "unknown \\['extra'\\]"),
        (_edited(lambda d: d.pop("generator")), "missing \\['generator'\\]"),
        (_edited(lambda d: d.pop("screen")), "exactly for codegen-home cases"),
        (_edited(lambda d: d.update(home="agentic")), "exactly for codegen-home cases"),
        (_edited(lambda d: d["generator"].update(codes=["SI_B", "SI_A"])), "must be sorted"),
        (_edited(lambda d: d["generator"].update(reasons=["not_a_reason"])), "not a SiteReason"),
        (_edited(lambda d: d["generator"].update(outcome="skipped")), "not a GeneratorOutcome"),
        (_edited(lambda d: d["generator"]["seams"][0].update(kind="x")), "not a SeamKind"),
        (_edited(lambda d: d["generator"]["stubs"][0].pop("reason")), "missing \\['reason'\\]"),
        (_edited(lambda d: d["screen"]["findings"][0].update(rule="")), "non-empty string"),
        (_edited(lambda d: d["loss"].update(rg1="RG1-x")), "expected RG1-<n>"),
        (_edited(lambda d: d["loss"].pop("rg1")), "names its RG1-<n>"),
    ],
)
def test_stored_answer_refuses_a_malformed_document(tmp_path, document, message):
    with pytest.raises(CaseAnswerError, match=message):
        load_stored_answer(_stored(tmp_path, document))


def test_stored_answer_id_is_its_file_name(tmp_path):
    with pytest.raises(CaseAnswerError, match="is not the file name"):
        load_stored_answer(_stored(tmp_path, ANSWER, name="another_case"))


def test_packaged_case_loads_every_field(tmp_path):
    case = load_packaged_case(_packaged(tmp_path, PACKAGED))
    assert case.case_id == CASE_ID
    assert case.construct.lines == (6, 9)
    assert case.screen.verdict == "refused"
    assert case.agentic_site_witnesses == ("AS-012",)
    assert case.provenance.from_probe == CASE_ID


@pytest.mark.parametrize(
    ("edit", "message"),
    [
        (lambda d: d.update(schema="subset-case/2"), "expected 'subset-case/1'"),
        (lambda d: d["construct"].update(lines=[9, 6]), "expected \\[first, last\\]"),
        (lambda d: d["construct"].update(lines=[0, 6]), "expected \\[first, last\\]"),
        (lambda d: d["provenance"].pop("note"), "missing \\['note'\\]"),
    ],
)
def test_packaged_case_refuses_a_malformed_document(tmp_path, edit, message):
    document = copy.deepcopy(PACKAGED)
    edit(document)
    with pytest.raises(CaseAnswerError, match=message):
        load_packaged_case(_packaged(tmp_path, document))
