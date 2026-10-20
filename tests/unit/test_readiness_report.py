"""The report functions are total, and the interim readiness rule never says READY (Item 2b).

Design D17's second layer: ``readiness_report``, ``readiness`` and ``log_report`` return for
every combination of generator outcome kind, destination state, screen state, finding outcome
and qualification, not-assessed cause and disagreement kind. Plan assumption A1: until the
owner decides D8, every model that builds is NOT_READY with a worded reason, so READY is
unreachable. A snapshot source is never ready whichever way the owner decides.
"""

from __future__ import annotations

import itertools
import logging

import pytest
from agentic_mbse.sysml.subset_profile import Outcome, Qualification, Verdict

from sysml_codegen.cli.prepare import PreparationStep, Prepared, Refused, prepare_graph
from sysml_codegen.cli.readiness import (
    AWAITING_OWNER,
    DESTINATION_CLEAN,
    DESTINATION_NOT_CHECKED,
    DestinationCheck,
    DestinationState,
    Disagreement,
    DisagreementKind,
    Readiness,
    ReadinessReport,
    RefusedFinding,
    disagreement_kind,
    log_report,
    readiness,
    readiness_report,
)
from sysml_codegen.cli.refusal import Refusal, RefusalItem, RefusalKind
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
DESTINATIONS = {
    "not-checked": DESTINATION_NOT_CHECKED,
    "clean": DESTINATION_CLEAN,
    "problem": DestinationCheck(DestinationState.PROBLEM, "Package sealing failed: probe"),
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
    for (g, generator), (d, destination), (s, screen), (k, disagreement) in itertools.product(
        GENERATORS.items(), DESTINATIONS.items(), SCREENS.items(), DISAGREEMENTS.items()
    ):
        yield f"{g}/{d}/{s}/{k}", ReadinessReport(generator, destination, screen, disagreement)


REPORTS = dict(_reports())


def test_the_combinations_cover_every_enum_member():
    assert len(REPORTS) == len(GENERATORS) * len(DESTINATIONS) * len(SCREENS) * len(DISAGREEMENTS)
    assert len(SCREENS) == len(NotAssessedCause) + 2 * len(Verdict) * len(Outcome) * len(
        Qualification
    ) + 1


def test_report_functions_are_total(caplog):
    caplog.set_level(logging.INFO, logger="sysml_codegen.cli")
    for key, report in REPORTS.items():
        verdict = readiness(report)
        assert verdict.reasons, key
        assert verdict.value is not Readiness.READY, key
        if isinstance(report.generator, Refused):
            assert verdict.value is Readiness.REFUSED, key
        caplog.clear()
        log_report(report)
        assert caplog.records, key
        rebuilt = readiness_report(report.generator, report.destination, report.screen)
        assert isinstance(rebuilt, ReadinessReport), key


@pytest.mark.parametrize("generator", ["builds", "refused-construction"])
def test_a_snapshot_is_never_ready(generator):
    report = readiness_report(
        GENERATORS[generator],
        DESTINATION_CLEAN,
        ScreenNotAssessed(NotAssessedCause.SNAPSHOT_SOURCE, "snapshots do not carry the screen"),
    )
    assert readiness(report).value is not Readiness.READY


def test_with_nothing_against_it_a_model_waits_on_the_owner():
    report = readiness_report(
        _prepared(), DESTINATION_CLEAN, ScreenAssessed("subset-profile/v2", Verdict.CLEAR, (), ())
    )
    assert report.disagreement is None
    verdict = readiness(report)
    assert (verdict.value, verdict.reasons) == (Readiness.NOT_READY, (AWAITING_OWNER,))


def test_reasons_are_printed_in_order(caplog):
    caplog.set_level(logging.INFO, logger="sysml_codegen.cli")
    key = "builds/problem/clear-omitted-candidate_refusal-1/screen_refuses_generator_builds"
    report = REPORTS[key]
    log_report(report)
    lines = [r.getMessage() for r in caplog.records]
    reasons = readiness(report).reasons
    start = lines.index("Readiness: not ready")
    assert lines[start + 1 :] == [f"  - {reason}" for reason in reasons]
    assert len(reasons) == 4


def test_a_check_destination_problem_is_a_warning_with_no_refusal(caplog):
    report = REPORTS["builds/problem/assessed-empty/none"]
    log_report(report)
    [warning] = [r for r in caplog.records if r.levelno == logging.WARNING]
    assert warning.getMessage() == "Package sealing failed: probe"
    assert not any(hasattr(r, "refusal") for r in caplog.records)


def test_a_generate_destination_refusal_logs_its_record_once(caplog):
    report = REPORTS["refused-destination/problem/assessed-empty/none"]
    log_report(report)
    assert [r.getMessage() for r in caplog.records if r.levelno >= logging.WARNING] == [
        "Package sealing failed: probe"
    ]
    assert sum(hasattr(r, "refusal") for r in caplog.records) == 1


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
    report = readiness_report(
        GENERATORS["refused-emit"],
        DESTINATION_CLEAN,
        ScreenAssessed("subset-profile/v2", Verdict.CLEAR, (), ()),
    )
    assert report.disagreement is None
