"""The read-only destination check (Item 2b, design D4).

``inspect_destination`` checks, without writing, that no link sits on or under the destination.
``generate`` runs it before it writes and ``check --output`` runs it instead of writing; both
refuse a problem with ``destination_refused``, so ``check`` gives ``generate``'s answer. This
module imports nothing that writes. ``emit_package``
repeats the check first, because the tree can change in between.
"""

from __future__ import annotations

from dataclasses import dataclass
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
