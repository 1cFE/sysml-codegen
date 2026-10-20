"""What the report says about the destination (EXEC-SUBSET-CONTRACT Item 2b, design D4).

``generate`` decides this before it writes, so the module imports nothing from agentic-mbse's
screen and nothing that writes.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


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
