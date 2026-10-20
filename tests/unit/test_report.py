"""The report functions are total, and the report never decides or claims an outcome (Item 2b).

Design D17's second layer: ``build_report`` and ``log_report`` return for every combination of
generator outcome kind, screen state, finding outcome and qualification, not-assessed cause and
disagreement kind. The generator alone decides the outcome (owner, Align Q1); the report logs
at most the generator's own refusal record and never a line calling a model ready or clean.
"""

from __future__ import annotations

import itertools
import logging
import re

import pytest
from agentic_mbse.sysml.subset_profile import Outcome, Qualification, Verdict

from sysml_codegen.cli.prepare import PreparationStep, Prepared, Refused, prepare_graph
from sysml_codegen.cli.refusal import Refusal, RefusalItem, RefusalKind
from sysml_codegen.cli.report import (
    Disagreement,
    DisagreementKind,
    RefusedFinding,
    Report,
    build_report,
    disagreement_kind,
    log_report,
)
from sysml_codegen.core.errors import GenerationCode
from sysml_codegen.elaboration.diagnostics import ElaborationCode
from sysml_codegen.resolution.models import ComputationGraph
from sysml_codegen.subset_profile_adapter import SubsetDiagnostic
from sysml_codegen.subset_screen import (
    NotAssessedCause,
    ScreenAssessed,
    ScreenNotAssessed,
    UnverifiedEntry,
)


def _prepared() -> Prepared:
    prepared = prepare_graph(
        ComputationGraph(modules=[], entry_point_groups=[], execution_order=[]), "pkg"
    )
    assert isinstance(prepared, Prepared)
    return prepared


def _refused(step: PreparationStep) -> Refused:
    if step in (PreparationStep.DESTINATION, PreparationStep.EMIT):
        return Refused(step, Refusal(RefusalKind.PACKAGE_WRITE), "Package sealing failed: probe")
    item = RefusalItem(ElaborationCode.SI_MULTIPLICITY_UNSUPPORTED, None, "root-0/m.sysml", 3)
    return Refused(step, Refusal(RefusalKind.DIAGNOSTIC, (item,)), "Model failed: probe")


GENERATORS = {
    "builds": _prepared(),
    "refused-construction": _refused(PreparationStep.CONSTRUCTION),
    "refused-destination": _refused(PreparationStep.DESTINATION),
    "refused-emit": _refused(PreparationStep.EMIT),
    "refused-emit-generation": Refused(
        PreparationStep.EMIT,
        Refusal(
            RefusalKind.GENERATION,
            (RefusalItem(GenerationCode.MODULE_KIND_UNRENDERABLE, None, None, None),),
        ),
        "Code generation failed: probe",
        None,
    ),
    "refused-generation": Refused(
        PreparationStep.CONSTRAINT_NAMES,
        Refusal(
            RefusalKind.GENERATION,
            (RefusalItem(GenerationCode.CONSTRAINT_NAME_UNSAFE, None, None, None),),
        ),
        "Code generation failed: probe",
        None,
    ),
}


def _finding(outcome: Outcome, qualification: Qualification) -> SubsetDiagnostic:
    refused = outcome is Outcome.REFUSED
    return SubsetDiagnostic(
        code=ElaborationCode.SI_MULTIPLICITY_UNSUPPORTED if refused else None,
        rule_id="part-multiplicity",
        outcome=outcome,
        qualification=qualification,
        subset_reason="part_multiplicity_ordered",
        remedy="probe remedy",
        subject=None,
        source_file="root-0/m.sysml" if refused else None,
        source_line=3,
    )


def _screens():
    for cause in NotAssessedCause:
        yield f"not-assessed-{cause}", ScreenNotAssessed(cause, f"probe {cause}")
    unverified = (UnverifiedEntry("binding-source", "probe_cause", "probe", None, None),)
    for verdict, outcome, qualification in itertools.product(Verdict, Outcome, Qualification):
        findings = (_finding(outcome, qualification),)
        for extra in ((), unverified):
            key = f"{verdict}-{outcome}-{qualification}-{len(extra)}"
            yield key, ScreenAssessed("subset-profile/v2", verdict, findings, extra)
    yield "assessed-empty", ScreenAssessed("subset-profile/v2", Verdict.CLEAR, (), ())


SCREENS = dict(_screens())
DISAGREEMENTS = {"none": None} | {
    kind.value: Disagreement(kind, ("SI_X",), ("probe",)) for kind in DisagreementKind
}


def _reports():
    for (g, generator), (s, screen), (k, disagreement) in itertools.product(
        GENERATORS.items(), SCREENS.items(), DISAGREEMENTS.items()
    ):
        yield f"{g}/{s}/{k}", Report(generator, screen, disagreement)


REPORTS = dict(_reports())


def test_the_combinations_cover_every_enum_member():
    assert len(REPORTS) == len(GENERATORS) * len(SCREENS) * len(DISAGREEMENTS)
    assert (
        len(SCREENS)
        == len(NotAssessedCause) + 2 * len(Verdict) * len(Outcome) * len(Qualification) + 1
    )


#: A word that would call a model ready or clean. "not ready" is the generator's own refusal
#: text from the base commit, which the refusal records pin.
OUTCOME_CLAIM = re.compile(r"(?<!not )\bready\b|\bclean\b|\breadiness\b", re.IGNORECASE)


def test_report_functions_are_total_and_claim_no_outcome(caplog):
    caplog.set_level(logging.INFO, logger="sysml_codegen.cli")
    for key, report in REPORTS.items():
        caplog.clear()
        log_report(report)
        assert caplog.records, key
        assert not [r for r in caplog.records if OUTCOME_CLAIM.search(r.getMessage())], key
        records = sum(hasattr(r, "refusal") for r in caplog.records)
        assert records == (1 if isinstance(report.generator, Refused) else 0), key
        rebuilt = build_report(report.generator, report.screen)
        assert isinstance(rebuilt, Report), key


def test_the_screen_never_logs_an_error(caplog):
    """The screen's lines are information and warnings; only the generator's refusal is an error."""
    caplog.set_level(logging.INFO, logger="sysml_codegen.cli")
    for key, report in REPORTS.items():
        if isinstance(report.generator, Refused):
            continue
        caplog.clear()
        log_report(report)
        assert all(r.levelno <= logging.WARNING for r in caplog.records), key


@pytest.mark.parametrize(
    ("builds", "codes", "refused", "kind"),
    [
        (True, (), [], None),
        (True, (), [RefusedFinding("r", "SI_A")], DisagreementKind.SCREEN_REFUSES_GENERATOR_BUILDS),
        (False, ("SI_A",), [], DisagreementKind.GENERATOR_REFUSES_SCREEN_SILENT),
        (False, ("SI_A",), [RefusedFinding("r", "SI_A")], None),
        (False, ("SI_A",), [RefusedFinding("r", "SI_B")], DisagreementKind.CODE_UNMAPPED),
    ],
)
def test_the_agreement_rule(builds, codes, refused, kind):
    assert disagreement_kind(builds, codes, refused) is kind


def test_a_refusal_after_prepare_still_counts_as_the_model_building():
    report = build_report(
        GENERATORS["refused-emit"], ScreenAssessed("subset-profile/v2", Verdict.CLEAR, (), ())
    )
    assert report.disagreement is None


def _shaped(outcome: Outcome, rule_id: str, reason: str, *, line: int, **extra) -> SubsetDiagnostic:
    return SubsetDiagnostic(
        code=extra.get("code"),
        rule_id=rule_id,
        outcome=outcome,
        qualification=extra.get("qualification", Qualification.NONE),
        subset_reason=reason,
        remedy=f"{rule_id} remedy",
        subject=f"P::x{line}",
        source_file="root-0/m.sysml",
        source_line=line,
    )


def test_the_screen_section_prints_in_full_only_what_a_modeler_must_act_on(caplog):
    """Design D5, orchestrator ruling 2026-10-20: the shape both commands print.

    Refused, unconfirmed and ``candidate_refusal`` findings, unverified checks and the
    disagreement in full; admitted findings as one count; omitted and excluded findings as one
    line per rule, with the remedy once.
    """
    refused_code = ElaborationCode.SI_MULTIPLICITY_UNSUPPORTED
    findings = (
        _shaped(Outcome.ADMITTED, "calc-owned-assertion", "calc_owned", line=1),
        _shaped(Outcome.OMITTED, "string-value-omission", "string_value", line=2),
        _shaped(Outcome.REFUSED, "part-multiplicity", "ordered", line=3, code=refused_code),
        _shaped(Outcome.OMITTED, "string-value-omission", "string_value", line=4),
        _shaped(Outcome.EXCLUDED, "redefinition", "redef_a", line=5),
        _shaped(
            Outcome.ADMITTED,
            "binding-source",
            "expression",
            line=6,
            qualification=Qualification.CANDIDATE_REFUSAL,
        ),
        _shaped(Outcome.ADMITTED, "calc-owned-assertion", "calc_owned", line=7),
        _shaped(Outcome.UNCONFIRMED, "occurrence", "unconfirmed_occ", line=8),
        _shaped(Outcome.EXCLUDED, "redefinition", "redef_b", line=9),
    )
    unverified = (UnverifiedEntry("binding-source", "probe_cause", "probe detail", None, None),)
    screen = ScreenAssessed("subset-profile/v2", Verdict.REFUSED, findings, unverified)
    disagreement = Disagreement(DisagreementKind.CODE_UNMAPPED, ("SI_X",), ("ordered",))
    caplog.set_level(logging.INFO, logger="sysml_codegen.cli")
    log_report(Report(_prepared(), screen, disagreement))
    records = caplog.records
    lines = [r.getMessage() for r in records]
    start = next(i for i, m in enumerate(lines) if m.startswith("Screen "))
    assert lines[:start] == ["Generator: builds (0 modules)"]
    assert lines[start + 1 :] == [
        "  refused part-multiplicity (ordered) P::x3 at root-0/m.sysml:3; the generator would "
        "refuse it with SI_MULTIPLICITY_UNSUPPORTED",
        "    remedy: part-multiplicity remedy",
        "  admitted binding-source (expression) P::x6 at root-0/m.sysml:6 [candidate_refusal]",
        "    remedy: binding-source remedy",
        "  unconfirmed occurrence (unconfirmed_occ) P::x8 at root-0/m.sysml:8",
        "    remedy: occurrence remedy",
        "  admitted, not listed: 2 findings",
        "  omitted string-value-omission (string_value): 2 findings",
        "    remedy: string-value-omission remedy",
        "  excluded redefinition (redef_a, redef_b): 2 findings",
        "    remedy: redefinition remedy",
        "  not assessed binding-source (probe_cause) at no location: probe detail",
        "Disagreement: code_unmapped: generator codes ['SI_X'], screen reasons ['ordered']",
    ]
    assert lines[start] == (
        "Screen subset-profile/v2 (information; the generator's answer above decides): verdict "
        "refused; 3 admitted, 2 excluded, 2 omitted, 1 refused, 1 unconfirmed; 1 not assessed"
    )
    # The findings printed in full are warnings; everything else is information.
    warned = [r.getMessage() for r in records if r.levelno == logging.WARNING]
    assert warned == lines[start + 1 : start + 7]
