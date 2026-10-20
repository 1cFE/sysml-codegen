"""The subset screen, run on the model the generator just loaded (EXEC-SUBSET-CONTRACT Item 2b).

``assess_screen`` runs agentic-mbse's subset screen (``extract_subset_facts``, then
``evaluate_subset_profile``) on the shared load, and renders each finding in the generator's
terms through ``subset_profile_adapter``. It never raises. Every way the screen cannot answer
becomes a ``ScreenNotAssessed`` with its cause and a worded reason:

- agentic-mbse's screen, or the adapter that reads it, cannot be imported;
- the installed screen's ``SUBSET_PROFILE_VERSION`` differs from the pin (decided before the
  adapter is imported, design D10);
- the model has parse errors, or did not load (design D2);
- the source is a snapshot, which does not carry the screen (the snapshot seam);
- the screen, the reason mapping or the rendering raised (design D17).

The answer only ever reaches the report. Nothing here takes a destination or writes a file.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from enum import StrEnum
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping

    from agentic_mbse.sysml.subset_profile import Verdict

    from sysml_codegen.cli.prepare import LoadedSource
    from sysml_codegen.orchestration.elaborated_pipeline import LiveLoad
    from sysml_codegen.subset_profile_adapter import SubsetDiagnostic

__all__ = [
    "NotAssessedCause",
    "ScreenAssessed",
    "ScreenNotAssessed",
    "UnverifiedEntry",
    "assess_screen",
]


class NotAssessedCause(StrEnum):
    SCREEN_NOT_IMPORTABLE = "screen_not_importable"
    PROFILE_SKEW = "profile_skew"
    SCREEN_FAILED = "screen_failed"
    PARSE_ERRORS = "parse_errors"
    NOT_LOADED = "not_loaded"
    SNAPSHOT_SOURCE = "snapshot_source"


@dataclass(frozen=True)
class ScreenNotAssessed:
    """The screen gave no answer for this model."""

    cause: NotAssessedCause
    #: Already worded for the report, e.g. "the model has parse errors".
    reason: str


@dataclass(frozen=True)
class UnverifiedEntry:
    """One screen check that could not run, so its rule was not assessed on this model."""

    rule_id: str
    #: The failure code's value, from agentic-mbse's closed failure vocabularies.
    cause: str
    detail: str
    source_file: str | None
    source_line: int | None


@dataclass(frozen=True)
class ScreenAssessed:
    """The screen's answer, rendered in the generator's terms."""

    profile_version: str
    verdict: Verdict
    #: One per finding, in the screen's order, with its file as a portable referent.
    findings: tuple[SubsetDiagnostic, ...]
    unverified: tuple[UnverifiedEntry, ...]


def assess_screen(loaded: LoadedSource) -> ScreenAssessed | ScreenNotAssessed:
    """Run the screen on the shared load. Never raises.

    The source types are told apart without importing ``sysml_codegen.cli``, whose package
    imports the writing half.
    """
    from sysml_codegen.orchestration.elaborated_pipeline import (
        FailedLoad,
        LiveLoad,
        LoadFailureKind,
    )

    if isinstance(loaded, FailedLoad):
        if loaded.kind is LoadFailureKind.PARSE_ERRORS:
            return ScreenNotAssessed(NotAssessedCause.PARSE_ERRORS, "the model has parse errors")
        return ScreenNotAssessed(NotAssessedCause.NOT_LOADED, "the model did not load")
    if not isinstance(loaded, LiveLoad):
        # The third member of ``LoadedSource``: a ``SnapshotFile``.
        return ScreenNotAssessed(
            NotAssessedCause.SNAPSHOT_SOURCE, "snapshots do not carry the screen"
        )
    try:
        return _screen(loaded)
    except Exception as error:
        return ScreenNotAssessed(
            NotAssessedCause.SCREEN_FAILED, f"the screen failed: {type(error).__name__}: {error}"
        )


def _screen(loaded: LiveLoad) -> ScreenAssessed | ScreenNotAssessed:
    """Compare the version, then import the adapter and run the screen. May raise."""
    from sysml_codegen._upstream_pins import SUBSET_PROFILE_VERSION

    try:
        from agentic_mbse.sysml import subset_profile
    except ImportError as error:
        return _not_importable(error, SUBSET_PROFILE_VERSION)

    installed = subset_profile.SUBSET_PROFILE_VERSION
    if installed != SUBSET_PROFILE_VERSION:
        return ScreenNotAssessed(
            NotAssessedCause.PROFILE_SKEW,
            f"the installed subset profile is {installed!r}, but the reason mapping was "
            f"reviewed against {SUBSET_PROFILE_VERSION!r}",
        )

    try:
        from agentic_mbse.sysml.subset_extraction import extract_subset_facts

        from sysml_codegen.subset_profile_adapter import render_finding
    except ImportError as error:
        return _not_importable(error, SUBSET_PROFILE_VERSION)

    rules = subset_profile.PACKAGED_RULES
    result = subset_profile.evaluate_subset_profile(
        extract_subset_facts(loaded.extractor.model), rules
    )
    referents = loaded.source_referents
    return ScreenAssessed(
        profile_version=result.subset_profile_version,
        verdict=result.verdict,
        findings=tuple(
            _portable(render_finding(finding, rules), referents) for finding in result.findings
        ),
        unverified=tuple(
            UnverifiedEntry(
                rule_id=check.rule_id,
                cause=str(check.cause.value),
                detail=check.detail,
                source_file=_referent(check.subject.file, referents) if check.subject else None,
                source_line=check.subject.line if check.subject else None,
            )
            for check in result.unverified
        ),
    )


def _not_importable(error: ImportError, pin: str) -> ScreenNotAssessed:
    return ScreenNotAssessed(
        NotAssessedCause.SCREEN_NOT_IMPORTABLE,
        f"agentic-mbse's subset screen could not be imported, so the model was not checked "
        f"against {pin!r}: {error}",
    )


def _portable(diagnostic: SubsetDiagnostic, referents: Mapping[str, str]) -> SubsetDiagnostic:
    return replace(diagnostic, source_file=_referent(diagnostic.source_file, referents))


def _referent(path: str | None, referents: Mapping[str, str]) -> str | None:
    """The load's ``root-N/<path>`` referent for a path; a path it does not hold stays raw.

    The screen names a file as SysIDE's URI path (``///home/...``), so the resolved form is
    tried too, as the generator's own lookup does (``elaborated_pipeline._lookup_referent``).
    """
    if path is None:
        return None
    return referents.get(path) or referents.get(str(Path(path).resolve())) or path
