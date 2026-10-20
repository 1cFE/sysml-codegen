"""The readiness report both ``check`` and ``generate`` print (EXEC-SUBSET-CONTRACT Item 2b).

A ``ReadinessReport`` holds four answers, each already decided elsewhere:

- the generator: ``Prepared`` (builds) or ``Refused``, from ``prepare``, the destination check
  or ``emit_package``;
- the destination check (``cli/destination.py``): not checked, clean, or the problem
  ``generate`` would stop at;
- the screen: ``ScreenAssessed`` or ``ScreenNotAssessed``, from ``assess_screen``;
- at most one disagreement between the generator and the screen (design D9).

Three pure functions read it. ``readiness`` decides ready, not ready, refused or an
environment failure, and is the one place that rule lives (design D8). ``log_report`` renders
it through the CLI's logger, in one fixed order: the generator's answer
(``prepare.log_generator_answer``), then ``log_assessment``. ``generate`` prints the
generator's answer before it writes and calls ``log_assessment`` after the seal. None of them
reads a table or raises on any member of the enums it switches on (design D17).

This module imports no SysIDE, not the adapter and nothing that writes, and it loads without
agentic-mbse's screen module. The screen's enums are imported only inside the functions that
read a ``ScreenAssessed``, which exists only once that module has imported. So ``check`` still
reports the generator's answer when the screen cannot be imported.
"""

from __future__ import annotations

import logging
from collections.abc import Collection, Sequence
from dataclasses import dataclass
from enum import Enum, StrEnum
from typing import TYPE_CHECKING

from sysml_codegen.cli.destination import DestinationCheck, DestinationState
from sysml_codegen.cli.prepare import PreparationStep, Prepared, Refused, log_generator_answer
from sysml_codegen.cli.refusal import RefusalItem, RefusalKind
from sysml_codegen.subset_screen import (
    NotAssessedCause,
    ScreenAssessed,
    ScreenNotAssessed,
)

if TYPE_CHECKING:
    from sysml_codegen.subset_profile_adapter import SubsetDiagnostic

#: The CLI's logger, so every report line has the name ``generate``'s lines have.
logger = logging.getLogger("sysml_codegen.cli")

#: The steps after ``prepare``. A refusal there is about the destination or the writing, not
#: the model, so the model still builds as far as the screen's agreement is concerned.
_AFTER_PREPARE = frozenset({PreparationStep.DESTINATION, PreparationStep.EMIT})

AWAITING_OWNER = "the readiness rule is awaiting the owner's decision (plan Phase 10)"


class DisagreementKind(StrEnum):
    GENERATOR_REFUSES_SCREEN_SILENT = "generator_refuses_screen_silent"
    SCREEN_REFUSES_GENERATOR_BUILDS = "screen_refuses_generator_builds"
    CODE_UNMAPPED = "code_unmapped"


@dataclass(frozen=True)
class RefusedFinding:
    """What the agreement rule reads from one ``refused`` screen finding."""

    reason: str
    #: The code ``REASON_MAPPING`` says the generator refuses the finding with.
    mapped_code: str


def disagreement_kind(
    builds: bool, refusal_codes: Collection[str], refused: Sequence[RefusedFinding]
) -> DisagreementKind | None:
    """The disagreement between the generator and the screen's refused findings, if any.

    Item 2a's agreement relation (design D7, D9): a refusal agrees with the screen when one
    refused finding's mapped code is among the refusal's codes. Total; reads no table.
    """
    if builds:
        return DisagreementKind.SCREEN_REFUSES_GENERATOR_BUILDS if refused else None
    if not refused:
        return DisagreementKind.GENERATOR_REFUSES_SCREEN_SILENT
    if {finding.mapped_code for finding in refused} & set(refusal_codes):
        return None
    return DisagreementKind.CODE_UNMAPPED


@dataclass(frozen=True)
class Disagreement:
    kind: DisagreementKind
    #: Sorted codes of the generator's refusal; empty when it builds.
    generator_codes: tuple[str, ...]
    #: Sorted, distinct reasons of the screen's ``refused`` findings.
    screen_reasons: tuple[str, ...]


@dataclass(frozen=True)
class ReadinessReport:
    generator: Prepared | Refused
    destination: DestinationCheck
    screen: ScreenAssessed | ScreenNotAssessed
    #: Computed only when the screen was assessed.
    disagreement: Disagreement | None


class Readiness(Enum):
    READY = "ready"
    NOT_READY = "not ready"
    REFUSED = "refused"
    #: Writing or sealing failed because of the disk, the OS or a link (``PACKAGE_WRITE``).
    #: Not a refusal: it says nothing about the model (spec, Outcomes).
    ENVIRONMENT_FAILURE = "environment failure"


@dataclass(frozen=True)
class ReadinessVerdict:
    value: Readiness
    #: Already worded, printed in order and never inspected.
    reasons: tuple[str, ...]


def model_builds(generator: Prepared | Refused) -> bool:
    """Whether the model itself builds: ``prepare`` accepted it, whatever happened after."""
    return isinstance(generator, Prepared) or generator.step in _AFTER_PREPARE


def generator_codes(generator: Prepared | Refused) -> tuple[str, ...]:
    if isinstance(generator, Prepared):
        return ()
    return tuple(sorted(item.code.value for item in generator.refusal.items))


def readiness_report(
    generator: Prepared | Refused,
    destination: DestinationCheck,
    screen: ScreenAssessed | ScreenNotAssessed,
) -> ReadinessReport:
    """Combine the answers, computing the disagreement when the screen was assessed."""
    disagreement = None
    if isinstance(screen, ScreenAssessed):
        from agentic_mbse.sysml.subset_profile import Outcome

        # A rendered finding carries a code exactly when it is refused (the adapter's contract).
        refused = [
            RefusedFinding(f.subset_reason, f.code.value)
            for f in screen.findings
            if f.outcome is Outcome.REFUSED and f.code is not None
        ]
        builds = model_builds(generator)
        codes = () if builds else generator_codes(generator)
        kind = disagreement_kind(builds, codes, refused)
        if kind is not None:
            reasons = tuple(sorted({finding.reason for finding in refused}))
            disagreement = Disagreement(kind, codes, reasons)
    return ReadinessReport(generator, destination, screen, disagreement)


def readiness(report: ReadinessReport) -> ReadinessVerdict:
    """Ready, not ready, refused or an environment failure, with the reasons in printed order.

    Interim rule (plan assumption A1) until the owner decides design D8: it decides only what
    that question does not touch, so READY is unreachable and every model that builds is not
    ready, with every reason that already holds and, failing those, ``AWAITING_OWNER``.
    """
    if isinstance(report.generator, Refused):
        if report.generator.refusal.kind is RefusalKind.PACKAGE_WRITE:
            return ReadinessVerdict(
                Readiness.ENVIRONMENT_FAILURE,
                (f"generate could not write the package (step {_step(report.generator)})",),
            )
        return ReadinessVerdict(
            Readiness.REFUSED, (f"the generator refuses at step {_step(report.generator)}",)
        )
    reasons: list[str] = []
    if report.destination.state is DestinationState.PROBLEM:
        reasons.append(f"generate would stop at the destination: {report.destination.message}")
    screen = report.screen
    if isinstance(screen, ScreenNotAssessed):
        if screen.cause is NotAssessedCause.SNAPSHOT_SOURCE:
            reasons.append("the source is a snapshot, and a snapshot is never ready")
        else:
            reasons.append(f"the screen was not assessed: {screen.reason}")
    else:
        from agentic_mbse.sysml.subset_profile import Qualification, Verdict

        if screen.unverified:
            reasons.append(f"{len(screen.unverified)} screen checks could not run")
        if screen.verdict is not Verdict.CLEAR:
            reasons.append(f"the screen's verdict is {screen.verdict.value}")
        candidates = sum(
            1 for f in screen.findings if f.qualification is Qualification.CANDIDATE_REFUSAL
        )
        if candidates:
            reasons.append(f"{candidates} findings are candidate refusals")
    if report.disagreement is not None:
        reasons.append(f"the screen and the generator disagree ({report.disagreement.kind})")
    if not reasons:
        reasons.append(AWAITING_OWNER)
    return ReadinessVerdict(Readiness.NOT_READY, tuple(reasons))


def log_report(report: ReadinessReport) -> None:
    """The whole report, as ``check`` prints it."""
    log_generator_answer(report.generator)
    log_assessment(report)


def log_assessment(report: ReadinessReport) -> None:
    """Destination, screen, disagreement and readiness, in that order."""
    _log_destination(report)
    _log_screen(report)
    if report.disagreement is not None:
        d = report.disagreement
        logger.info(
            f"Disagreement: {d.kind}: generator codes {list(d.generator_codes)}, "
            f"screen reasons {list(d.screen_reasons)}"
        )
    verdict = readiness(report)
    logger.info(f"Readiness: {verdict.value.value}")
    for reason in verdict.reasons:
        logger.info(f"  - {reason}")


def _log_destination(report: ReadinessReport) -> None:
    destination = report.destination
    if destination.state is DestinationState.NOT_CHECKED:
        logger.info("Destination: not checked")
    elif destination.state is DestinationState.CLEAN:
        logger.info("Destination: clean")
    elif not (
        isinstance(report.generator, Refused)
        and report.generator.step is PreparationStep.DESTINATION
    ):
        # Not a refusal record: the generator outcome stays "builds" (design D4). When the
        # generator was refused here, its record already carries this text.
        logger.warning(destination.message)


def _log_screen(report: ReadinessReport) -> None:
    screen = report.screen
    if isinstance(screen, ScreenNotAssessed):
        logger.info(f"Screen not assessed: {screen.reason}")
        return
    from agentic_mbse.sysml.subset_profile import Outcome, Qualification, Verdict

    counts: dict[str, int] = {}
    for finding in screen.findings:
        counts[finding.outcome.value] = counts.get(finding.outcome.value, 0) + 1
    tally = ", ".join(f"{n} {outcome}" for outcome, n in sorted(counts.items())) or "no findings"
    verdict = screen.verdict.value
    if screen.verdict is Verdict.CLEAR:
        verdict += " (over the implemented rules; not a promise the generator accepts the model)"
    logger.info(
        f"Screen {screen.profile_version}: verdict {verdict}; {tally}; "
        f"{len(screen.unverified)} not assessed"
    )
    refusal_items = report.generator.refusal.items if isinstance(report.generator, Refused) else ()
    admitted = 0
    grouped: dict[tuple[str, str], list[SubsetDiagnostic]] = {}
    for finding in screen.findings:
        # Printed in full: what a modeler must act on (design D5). Admitted findings are one
        # count line; omitted and excluded ones are one line per rule.
        acted_on = finding.outcome in (Outcome.REFUSED, Outcome.UNCONFIRMED)
        if acted_on or finding.qualification is Qualification.CANDIDATE_REFUSAL:
            _log_finding(finding, refusal_items)
        elif finding.outcome is Outcome.ADMITTED:
            admitted += 1
        else:
            grouped.setdefault((finding.outcome.value, finding.rule_id), []).append(finding)
    if admitted:
        logger.info(f"  admitted, not listed: {admitted} findings")
    for (outcome, rule_id), findings in grouped.items():
        reasons = ", ".join(sorted({f.subset_reason for f in findings}))
        logger.info(f"  {outcome} {rule_id} ({reasons}): {len(findings)} findings")
        logger.info(f"    remedy: {findings[0].remedy}")
    for entry in screen.unverified:
        logger.info(
            f"  not assessed {entry.rule_id} ({entry.cause}) at "
            f"{_location(entry.source_file, entry.source_line)}: {entry.detail}"
        )


def _log_finding(finding: SubsetDiagnostic, refusal_items: Sequence[RefusalItem]) -> None:
    """One finding in full: where it is, what the generator does with it, and its remedy."""
    from agentic_mbse.sysml.subset_profile import Qualification

    where = _location(finding.source_file, finding.source_line)
    line = (
        f"  {finding.outcome.value} {finding.rule_id} ({finding.subset_reason}) "
        f"{finding.subject or '<anonymous>'} at {where}"
    )
    if finding.qualification is not Qualification.NONE:
        line += f" [{finding.qualification.value}]"
    if finding.code is not None:
        matched = [item for item in refusal_items if item.code.value == finding.code.value]
        if matched:
            there = _location(matched[0].source_file, matched[0].source_line)
            line += f"; matches the generator's {finding.code.value} at {there}"
        else:
            line += f"; the generator would refuse it with {finding.code.value}"
    logger.info(line)
    logger.info(f"    remedy: {finding.remedy}")


def _step(refused: Refused) -> str:
    return refused.step.name.lower().replace("_", " ")


def _location(file: str | None, line: int | None) -> str:
    if file is None:
        return "no location"
    return file if line is None else f"{file}:{line}"
