"""The logged form of a ``run_codegen`` refusal, captured for comparison (Item 2b, Phase 0).

A refusal's public form is a log record carrying ``extra={"refusal": Refusal}`` (and
``constraint_name_safety`` for a generation refusal). This module captures every such record
a run logs and serializes it to plain JSON: logger name, level, message, and the extras.
Paths a run cannot control (its output folder, this checkout, the installed agentic-mbse)
are replaced by placeholders, so a record taken in one folder equals one taken in another.

``tests/expectations/subset_profile/refusal_records.json`` holds the records the base commit
logged, written by ``scripts/refusal_records.py``. Tests compare against it with ``BASE``.
"""

from __future__ import annotations

import dataclasses
import json
import logging
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from enum import Enum
from pathlib import Path
from typing import Any

import agentic_mbse
from pydantic import BaseModel

REPO = Path(__file__).resolve().parents[2]
RECORDS_PATH = REPO / "tests" / "expectations" / "subset_profile" / "refusal_records.json"
SCHEMA = "refusal-records/1"
_AGENTIC = Path(agentic_mbse.__file__).resolve().parents[1]


def _plain(value: Any) -> Any:
    if isinstance(value, Enum):
        return f"{type(value).__name__}.{value.name}"
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        return {f.name: _plain(getattr(value, f.name)) for f in dataclasses.fields(value)}
    if isinstance(value, BaseModel):
        return {name: _plain(getattr(value, name)) for name in type(value).model_fields}
    if isinstance(value, (list, tuple)):
        return [_plain(item) for item in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    raise TypeError(f"no plain form for {type(value).__name__}: {value!r}")


def _placeholders(text: str, output: Path | None) -> str:
    if output is not None:
        for form in {str(output.resolve()), str(output)}:
            text = text.replace(form, "<OUTPUT>")
    return text.replace(str(_AGENTIC), "<AGENTIC_SRC>").replace(str(REPO), "<REPO>")


def serialize(record: logging.LogRecord, output: Path | None) -> dict[str, Any]:
    """One refusal-carrying record as plain JSON, with uncontrolled paths replaced."""
    serialized: dict[str, Any] = {
        "logger": record.name,
        "level": record.levelname,
        "message": record.getMessage(),
        "refusal": _plain(record.refusal),  # type: ignore[attr-defined]
    }
    if hasattr(record, "constraint_name_safety"):
        serialized["constraint_name_safety"] = _plain(record.constraint_name_safety)
    return json.loads(_placeholders(json.dumps(serialized, sort_keys=True), output))


class _Capture(logging.Handler):
    def __init__(self) -> None:
        super().__init__(logging.DEBUG)
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:
        if hasattr(record, "refusal"):
            self.records.append(record)


@contextmanager
def capture_refusals(output: Path | None) -> Iterator[list[dict[str, Any]]]:
    """Collect, serialized, every refusal-carrying record logged under ``sysml_codegen``.

    The list is filled when the block exits.
    """
    handler = _Capture()
    logger = logging.getLogger("sysml_codegen")
    previous = logger.level
    logger.addHandler(handler)
    logger.setLevel(min(previous or logging.WARNING, logging.WARNING))
    collected: list[dict[str, Any]] = []
    try:
        yield collected
    finally:
        logger.setLevel(previous)
        logger.removeHandler(handler)
        collected.extend(serialize(record, output) for record in handler.records)


def load(path: Path = RECORDS_PATH) -> Mapping[str, list[dict[str, Any]]]:
    document = json.loads(path.read_text())
    if document.get("schema") != SCHEMA:
        raise ValueError(f"{path}: schema must be {SCHEMA!r}")
    return document["records"]
