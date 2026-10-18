"""Stored subset-profile answers load only in their stored form, and agreement follows § C.

Item 2a design D1 (the stored answer), D3 (the disagreement record) and § C (the agreement
rule). Pure: every document is written under ``tmp_path``.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
from agentic_mbse.sysml.conformance_case import ScreenAnswer, ScreenFinding
from agentic_mbse.sysml.subset_profile import ContextId, Outcome, Verdict

from sysml_codegen.elaboration.diagnostics import SiteReason
from tests.helpers.subset_profile.cases import (
    CaseAnswerError,
    CaseHome,
    Disagreement,
    DisagreementKind,
    GeneratorOutcome,
    GeneratorRun,
    LossDisposition,
    Resolution,
    SeamKind,
    disagreement,
    load_stored_answer,
    read_disagreements,
    recorded,
)

CASE_ID = "binding-source__expression_source__owner_instantiated"
FINDING = {
    "rule": "binding-source",
    "shape": "expression_source",
    "context": "owner_instantiated",
    "outcome": "refused",
    "subject": "fx::Site::t::xs",
    "line": 7,
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
    "construct": {"file": "model.sysml", "lines": [6, 9], "description": "a tuple actual"},
    "screen": {"verdict": "refused", "findings": [FINDING]},
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
    assert (answer.case_id, answer.home, answer.subject) == (
        CASE_ID,
        CaseHome.CODEGEN,
        f"case:{CASE_ID}",
    )
    run = answer.generator.run
    assert run.outcome is GeneratorOutcome.REFUSED
    assert run.codes == ("SI_EXPRESSION_SOURCE_UNSUPPORTED", "SI_TYPE_INVALID")
    assert run.reasons == (SiteReason.BINDING_SOURCE_FORM_UNSUPPORTED,)
    assert answer.generator.witnesses == ("ES-004",)
    assert answer.generator.stubs[0].reason is SiteReason.BINDING_SOURCE_FORM_UNSUPPORTED
    assert answer.generator.seams[0].kind is SeamKind.ENTRY_POINT
    assert answer.generator.seams[0].expect == {"count": 1}
    assert answer.codegen is not None
    assert (answer.codegen.construct.first_line, answer.codegen.construct.last_line) == (6, 9)
    assert answer.codegen.screen.findings[0].context is ContextId.OWNER_INSTANTIATED
    assert answer.loss is not None
    assert answer.loss.disposition is LossDisposition.CANDIDATE_REFUSAL
    assert answer.loss.rg1 == "RG1-3"
    assert answer.loss.control == "a_control_case"


def test_agentic_home_answer_has_no_construct_or_screen(tmp_path):
    document = {key: ANSWER[key] for key in ("id", "generator")} | {"home": "agentic"}
    answer = load_stored_answer(_stored(tmp_path, document))
    assert answer.codegen is None and answer.loss is None


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
        (_edited(lambda d: d.pop("construct")), "exactly for codegen-home cases"),
        (_edited(lambda d: d.update(home="agentic")), "exactly for codegen-home cases"),
        (_edited(lambda d: d["generator"].update(codes=["SI_B", "SI_A"])), "must be sorted"),
        (_edited(lambda d: d["generator"].update(codes=[])), "a refused run has codes"),
        (_edited(lambda d: d["generator"].update(outcome="generated")), "a refused run has"),
        (_edited(lambda d: d["generator"].update(reasons=["not_a_reason"])), "not a SiteReason"),
        (_edited(lambda d: d["generator"].update(outcome="skipped")), "not a GeneratorOutcome"),
        (_edited(lambda d: d["generator"]["seams"][0].update(kind="x")), "not a SeamKind"),
        (_edited(lambda d: d["generator"]["stubs"][0].pop("reason")), "missing \\['reason'\\]"),
        (_edited(lambda d: d["construct"].update(lines=[9, 6])), "expected \\[first, last\\]"),
        (_edited(lambda d: d["screen"]["findings"][0].update(rule="")), "non-empty text"),
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


# ---- agreement (design § C) -------------------------------------------------------------------

GENERATED = GeneratorRun(GeneratorOutcome.GENERATED, (), ())


def _refused(*codes: str) -> GeneratorRun:
    return GeneratorRun(GeneratorOutcome.REFUSED, tuple(sorted(codes)), ())


def _screen(*findings: tuple[str, str, ContextId, Outcome]) -> ScreenAnswer:
    return ScreenAnswer(
        Verdict.CLEAR,
        tuple(ScreenFinding(r, s, c, o, "fx::Site::x", 7) for r, s, c, o in findings),
    )


EXPRESSION_REFUSED = (
    "binding-source",
    "expression_source",
    ContextId.OWNER_INSTANTIATED,
    Outcome.REFUSED,
)
EXPRESSION_ADMITTED = (
    "binding-source",
    "expression_source",
    ContextId.OWNER_UNINSTANTIATED,
    Outcome.ADMITTED,
)


@pytest.mark.parametrize(
    ("run", "screen", "kind"),
    [
        (GENERATED, _screen(), None),
        (GENERATED, _screen(EXPRESSION_ADMITTED), None),
        (GENERATED, _screen(EXPRESSION_REFUSED), DisagreementKind.SCREEN_REFUSES_GENERATOR_BUILDS),
        (_refused("SI_EXPRESSION_SOURCE_UNSUPPORTED"), _screen(EXPRESSION_REFUSED), None),
        # an extra generator code beside the mapped one still agrees (several constructs, O7)
        (_refused("SI_EXPRESSION_SOURCE_UNSUPPORTED", "SI_X"), _screen(EXPRESSION_REFUSED), None),
        (
            _refused("SI_OCCURRENCE_MISSING"),
            _screen(),
            DisagreementKind.GENERATOR_REFUSES_SCREEN_SILENT,
        ),
        (
            _refused("SI_OCCURRENCE_MISSING"),
            _screen(EXPRESSION_ADMITTED),
            DisagreementKind.GENERATOR_REFUSES_SCREEN_SILENT,
        ),
        (
            _refused("SI_OCCURRENCE_MISSING"),
            _screen(EXPRESSION_REFUSED),
            DisagreementKind.CODE_UNMAPPED,
        ),
        # a generation-stage code is never mapped, so it alone never agrees (D15)
        (
            _refused("PROJECTION_FAILED"),
            _screen(EXPRESSION_REFUSED),
            DisagreementKind.CODE_UNMAPPED,
        ),
    ],
)
def test_agreement_rule(run, screen, kind):
    found = disagreement("case:x", run, screen)
    assert (None if found is None else found.kind) == kind
    if found is not None:
        assert found.generator_codes == run.codes
        refused = any(f.outcome is Outcome.REFUSED for f in screen.findings)
        assert found.screen_reasons == (("binding_source_expression",) if refused else ())


def test_a_refused_finding_of_a_no_refusal_reason_is_an_inconsistency():
    screen = _screen(
        ("string-value-omission", "string_value", ContextId.ATTRIBUTE_VALUE, Outcome.REFUSED)
    )
    with pytest.raises(ValueError, match="maps to NO_REFUSAL"):
        disagreement("case:x", _refused("SI_X"), screen)


# ---- the disagreement record (design D3) --------------------------------------------------------

ENTRY = {
    "subject": "case:x",
    "kind": "generator_refuses_screen_silent",
    "generator_codes": ["SI_OCCURRENCE_MISSING"],
    "screen_reasons": [],
    "resolution": "reproduced_gap",
    "r3_row": "ES-002",
    "owner": "sysml-codegen",
    "reason": "no rule recognizes the shape",
}


def _record(tmp_path: Path, *entries: dict) -> Path:
    path = tmp_path / "record.json"
    path.write_text(json.dumps({"schema": "subset-disagreements/1", "entries": list(entries)}))
    return path


def test_record_entry_matches_its_computed_disagreement(tmp_path):
    (entry,) = read_disagreements(_record(tmp_path, ENTRY))
    assert entry.resolution is Resolution.REPRODUCED_GAP and entry.rg1 is None
    computed = disagreement("case:x", _refused("SI_OCCURRENCE_MISSING"), _screen())
    assert computed == Disagreement(
        "case:x", DisagreementKind.GENERATOR_REFUSES_SCREEN_SILENT, ("SI_OCCURRENCE_MISSING",), ()
    )
    assert recorded(computed, (entry,))
    other = disagreement("case:x", _refused("SI_REDEFINITION_INVALID"), _screen())
    assert other is not None and not recorded(other, (entry,))


@pytest.mark.parametrize(
    ("changes", "message"),
    [
        ({"owner": ""}, "owner: expected a non-empty string"),
        ({"reason": " "}, "reason: expected a non-empty string"),
        ({"resolution": "rg1_pending"}, "names its RG1-<n>"),
        ({"rg1": "RG1-2"}, "names its RG1-<n>"),
        ({"subject": "probe:x"}, "case:<id> or fixture:<path>"),
        ({"kind": "screen_silent"}, "not a DisagreementKind"),
        ({"generator_codes": ["SI_B", "SI_A"]}, "must be sorted"),
    ],
)
def test_record_refuses_a_malformed_entry(tmp_path, changes, message):
    with pytest.raises(CaseAnswerError, match=message):
        read_disagreements(_record(tmp_path, ENTRY | changes))


def test_an_rg1_pending_entry_loads_with_its_recommendation(tmp_path):
    (entry,) = read_disagreements(
        _record(tmp_path, ENTRY | {"resolution": "rg1_pending", "rg1": "RG1-1"})
    )
    assert entry.rg1 == "RG1-1"


def test_record_refuses_a_subject_listed_twice(tmp_path):
    with pytest.raises(CaseAnswerError, match="listed twice"):
        read_disagreements(_record(tmp_path, ENTRY, ENTRY | {"kind": "code_unmapped"}))
