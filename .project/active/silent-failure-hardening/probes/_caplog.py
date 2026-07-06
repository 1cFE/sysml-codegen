"""Shared log-capture helper for the silent-failure probes.

Attaches a handler to the root logger (so every sysml_codegen child logger
propagates into it) and records the emitted LogRecords. Lets a probe assert
"nothing was logged at >= WARNING" — the core evidence for a silent failure.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field


@dataclass
class CapturedLogs:
    records: list[logging.LogRecord] = field(default_factory=list)

    def at_or_above(self, level: int) -> list[logging.LogRecord]:
        return [r for r in self.records if r.levelno >= level]

    def containing(self, substr: str) -> list[logging.LogRecord]:
        return [r for r in self.records if substr.lower() in r.getMessage().lower()]

    def dump(self, min_level: int = logging.DEBUG) -> str:
        lines = [
            f"    [{logging.getLevelName(r.levelno)}] {r.name}: {r.getMessage()}"
            for r in self.records
            if r.levelno >= min_level
        ]
        return "\n".join(lines) if lines else "    <no records>"


class _ListHandler(logging.Handler):
    def __init__(self, sink: CapturedLogs) -> None:
        super().__init__(level=logging.DEBUG)
        self._sink = sink

    def emit(self, record: logging.LogRecord) -> None:
        self._sink.records.append(record)


def capture_all() -> tuple[CapturedLogs, _ListHandler]:
    """Return (sink, handler). Caller attaches handler to a logger and reads sink."""
    sink = CapturedLogs()
    handler = _ListHandler(sink)
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    root.addHandler(handler)
    return sink, handler
