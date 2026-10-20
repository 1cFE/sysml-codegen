"""The read-only destination check, and what the report says about it (Item 2b, design D4).

``inspect_destination`` checks, without writing, that no link sits on or under the destination.
``generate`` runs it before it writes and ``check --output`` runs it instead of writing, so this
module imports nothing that writes and nothing from agentic-mbse's screen. ``emit_package``
repeats the check first, because the tree can change in between.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from sysml_codegen.cli.prepare import PreparationStep, Refused
from sysml_codegen.cli.refusal import Refusal, RefusalKind


@dataclass(frozen=True)
class DestinationProblem:
    """Why the destination cannot take a package: today's sealing-failure detail."""

    detail: str


def inspect_destination(path: Path) -> DestinationProblem | None:
    """Check, without writing, that no link sits on or under the destination."""
    from sysml_codegen.contracts import PackageSealError, ensure_package_tree_is_link_free

    try:
        ensure_package_tree_is_link_free(path)
    except (PackageSealError, OSError) as error:
        return DestinationProblem(str(error))
    return None


def destination_refused(problem: DestinationProblem) -> Refused:
    """The refusal ``generate`` logs when the destination cannot take a package."""
    return Refused(
        PreparationStep.DESTINATION,
        Refusal(RefusalKind.PACKAGE_WRITE),
        f"Package sealing failed: {problem.detail}",
    )


class DestinationState(Enum):
    NOT_CHECKED = "not checked"
    CLEAN = "clean"
    PROBLEM = "problem"


@dataclass(frozen=True)
class DestinationCheck:
    state: DestinationState
    #: The ``Package sealing failed: …`` text; set exactly when the state is ``PROBLEM``.
    message: str | None = None

    def __post_init__(self) -> None:
        if (self.state is DestinationState.PROBLEM) != (self.message is not None):
            raise ValueError("a destination check has a message exactly when it has a problem")


DESTINATION_NOT_CHECKED = DestinationCheck(DestinationState.NOT_CHECKED)
DESTINATION_CLEAN = DestinationCheck(DestinationState.CLEAN)


def destination_check(problem: DestinationProblem | None) -> DestinationCheck:
    """The report's destination entry, worded as the refusal ``generate`` would log."""
    if problem is None:
        return DESTINATION_CLEAN
    return DestinationCheck(DestinationState.PROBLEM, destination_refused(problem).message)
