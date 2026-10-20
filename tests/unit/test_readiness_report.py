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

from sysml_codegen.cli.destination import (
    DESTINATION_CLEAN,
    DESTINATION_NOT_CHECKED,
    DestinationCheck,
    DestinationState,
)
from sysml_codegen.cli.prepare import PreparationStep, Prepared, Refused, prepare_graph
from sysml_codegen.cli.readiness import (
    AWAITING_OWNER,
    Disagreement,
    DisagreementKind,
    Readiness,
    ReadinessReport,
    ReadinessVerdict,
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
#: A failed write or seal is an environment failure; every other refusal is a refusal.
_REFUSED_VERDICTS = {kind: Readiness.REFUSED for kind in RefusalKind} | {
    RefusalKind.PACKAGE_WRITE: Readiness.ENVIRONMENT_FAILURE
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
    assert (
        len(SCREENS)
        == len(NotAssessedCause) + 2 * len(Verdict) * len(Outcome) * len(Qualification) + 1
    )


def test_report_functions_are_total(caplog):
    caplog.set_level(logging.INFO, logger="sysml_codegen.cli")
    for key, report in REPORTS.items():
        verdict = readiness(report)
        assert verdict.reasons, key
        assert verdict.value is not Readiness.READY, key
        if isinstance(report.generator, Refused):
            assert verdict.value is _REFUSED_VERDICTS[report.generator.refusal.kind], key
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
    ("generator", "verdict", "reason"),
    [
        (
            "refused-destination",
            Readiness.ENVIRONMENT_FAILURE,
            "generate could not write the package (step destination)",
        ),
        (
            "refused-emit",
            Readiness.ENVIRONMENT_FAILURE,
            "generate could not write the package (step emit)",
        ),
        ("refused-emit-generation", Readiness.REFUSED, "the generator refuses at step emit"),
    ],
)
def test_a_failed_write_is_an_environment_failure_not_a_refusal(generator, verdict, reason):
    """Spec, Outcomes: writing or sealing failing is not a refusal; a writer's refusal still is."""
    report = REPORTS[f"{generator}/clean/assessed-empty/none"]
    assert readiness(report) == ReadinessVerdict(verdict, (reason,))


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
    log_report(ReadinessReport(_prepared(), DESTINATION_NOT_CHECKED, screen, disagreement))
    lines = [r.getMessage() for r in caplog.records]
    start = next(i for i, m in enumerate(lines) if m.startswith("Screen "))
    end = lines.index("Readiness: not ready")
    assert lines[start + 1 : end] == [
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
        "Screen subset-profile/v2: verdict refused; 3 admitted, 2 excluded, 2 omitted, "
        "1 refused, 1 unconfirmed; 1 not assessed"
    )
