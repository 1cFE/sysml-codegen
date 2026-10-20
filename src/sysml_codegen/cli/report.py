"""The report both ``check`` and ``generate`` print (EXEC-SUBSET-CONTRACT Item 2b).

The generator's own route alone decides whether a model is refused (owner, Align Q1). This
report adds the subset screen's findings under that answer, as information. It never changes
an exit code.

A ``Report`` holds three answers, each already decided elsewhere:

- the generator: ``Prepared`` (builds) or ``Refused``, from ``prepare``, the destination check
  or ``emit_package``;
- the screen: ``ScreenAssessed`` or ``ScreenNotAssessed``, from ``assess_screen``;
- at most one disagreement between the generator and the screen (design D9).

``log_report`` renders it through the CLI's logger, in one fixed order: the generator's answer
(``prepare.log_generator_answer``), then ``log_screen_section``. ``generate`` prints the
generator's answer before it writes and calls ``log_screen_section`` after the seal. Neither
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
from enum import StrEnum
from typing import TYPE_CHECKING

from sysml_codegen.cli.prepare import PreparationStep, Prepared, Refused, log_generator_answer
from sysml_codegen.cli.refusal import RefusalItem
from sysml_codegen.subset_screen import ScreenAssessed, ScreenNotAssessed

if TYPE_CHECKING:
    from sysml_codegen.subset_profile_adapter import SubsetDiagnostic

#: The CLI's logger, so every report line has the name ``generate``'s lines have.
logger = logging.getLogger("sysml_codegen.cli")

#: The steps after ``prepare``. A refusal there is about the destination or the writing, not
#: the model, so the model still builds as far as the screen's agreement is concerned.
_AFTER_PREPARE = frozenset({PreparationStep.DESTINATION, PreparationStep.EMIT})


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
class Report:
    generator: Prepared | Refused
    screen: ScreenAssessed | ScreenNotAssessed
    #: Computed only when the screen was assessed.
    disagreement: Disagreement | None


def model_builds(generator: Prepared | Refused) -> bool:
    """Whether the model itself builds: ``prepare`` accepted it, whatever happened after."""
    return isinstance(generator, Prepared) or generator.step in _AFTER_PREPARE


def generator_codes(generator: Prepared | Refused) -> tuple[str, ...]:
    if isinstance(generator, Prepared):
        return ()
    return tuple(sorted(item.code.value for item in generator.refusal.items))


def build_report(
    generator: Prepared | Refused, screen: ScreenAssessed | ScreenNotAssessed
) -> Report:
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
    return Report(generator, screen, disagreement)


def log_report(report: Report) -> None:
    """The whole report, as ``check`` prints it."""
    log_generator_answer(report.generator)
    log_screen_section(report)


def log_screen_section(report: Report) -> None:
    """The screen's findings, then any disagreement: information under the generator's answer."""
    _log_screen(report)
    if report.disagreement is not None:
        d = report.disagreement
        logger.info(
            f"Disagreement: {d.kind}: generator codes {list(d.generator_codes)}, "
            f"screen reasons {list(d.screen_reasons)}"
        )


def _log_screen(report: Report) -> None:
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
        f"Screen {screen.profile_version} (information; the generator's answer above "
        f"decides): verdict {verdict}; {tally}; "
        f"{len(screen.unverified)} not assessed"
    )
    refusal_items = report.generator.refusal.items if isinstance(report.generator, Refused) else ()
    admitted = 0
    grouped: dict[tuple[str, str], list[SubsetDiagnostic]] = {}
    for finding in screen.findings:
        # Printed in full, as warnings: what a modeler must act on (design D5). Admitted
        # findings are one count line; omitted and excluded ones are one line per rule.
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
    """One finding in full, as warnings: its place, the generator's view and its remedy."""
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
    logger.warning(line)
    logger.warning(f"    remedy: {finding.remedy}")


def _location(file: str | None, line: int | None) -> str:
    if file is None:
        return "no location"
    return file if line is None else f"{file}:{line}"
