#!/usr/bin/env python3
"""Record or compare the refusal records ``run_codegen`` logs (EXEC-SUBSET-CONTRACT Item 2b).

The second check every 2b refactor phase runs. Each entry is the list of refusal-carrying
records one run logs, in the form ``tests/helpers/refusal_records.py`` serializes:

- ``case:<id>``: every 2a case the generator refuses, into an empty destination;
- ``destination_link:<id>``: design D4's coincidence case, a model refused by its last check
  (the parameter-field collision) run against a destination holding a symlink. The base
  commit logged ``PACKAGE_WRITE`` here; since 2b Phase 4 it logs the model's own refusal, the
  one stated change, so this entry was re-recorded then and equals ``case:<id>``;
- ``writer_failure:<Exception>``: design D18, one writer (``_generate_pipeline``) patched to
  raise ``CodeGenerationError``, ``OSError`` and ``RuntimeError`` in turn on a builds case.

Usage (licensed; source the license first)::

    uv run --all-extras python scripts/refusal_records.py record
    uv run --all-extras python scripts/refusal_records.py compare

``record`` writes ``tests/expectations/refusal_cases/refusal_records.json``; ``compare``
re-records and exits 1 naming every entry that differs from that file.
"""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

import _generate_corpus as corpus  # noqa: E402

from tests.helpers import refusal_records  # noqa: E402

DESTINATION_LINK_CASE = "output-naming__param_field_collision"
WRITER_FAILURE_CASE = "anonymous-declaration__attribute_usage"


def _run(subject: corpus.Subject, output: Path) -> list[dict[str, Any]]:
    from sysml_codegen.cli import run_codegen

    with refusal_records.capture_refusals(output) as records:
        run_codegen(corpus.config_for(subject, output))
    return records


def _case(case_id: str) -> corpus.Subject:
    from tests.helpers.refusal_cases import cases

    return corpus.Subject(f"case:{case_id}", cases.model_root(cases.load_answer(case_id)), None)


def _rebind_everywhere(original: object, replacement: object) -> list[tuple[object, str]]:
    """Point every module-level name bound to ``original`` at ``replacement``.

    By-name imports (``from x import f``) hold their own binding, so patching the defining
    module alone would miss them.
    """
    rebound: list[tuple[object, str]] = []
    for module in list(sys.modules.values()):
        namespace = getattr(module, "__dict__", None)
        if not isinstance(namespace, dict):
            continue
        for name, value in list(namespace.items()):
            if value is original:
                setattr(module, name, replacement)
                rebound.append((module, name))
    return rebound


@contextmanager
def _writer_raising(error: Exception) -> Iterator[None]:
    """Rebind ``_generate_pipeline`` wherever a module holds it, so the patch follows a move."""
    real = _find_pipeline_writer()

    def raising(*_args: object, **_kwargs: object) -> None:
        raise error

    rebound = _rebind_everywhere(real, raising)
    try:
        yield
    finally:
        for module, name in rebound:
            setattr(module, name, real)


def _find_pipeline_writer() -> Callable[..., Any]:
    """The writer's home: ``cli`` at the base, ``cli.emit`` from 2b Phase 2 on."""
    import importlib

    for name in ("sysml_codegen.cli.emit", "sysml_codegen.cli"):
        try:
            module = importlib.import_module(name)
        except ModuleNotFoundError:
            continue
        writer = getattr(module, "_generate_pipeline", None)
        if writer is not None:
            return writer
    raise AssertionError("no _generate_pipeline writer found")


def _writer_failures() -> Iterator[tuple[str, Exception]]:
    from sysml_codegen.core.errors import CodeGenerationError, GenerationCode

    yield (
        "CodeGenerationError",
        CodeGenerationError(
            "probe: the pipeline writer refused", code=GenerationCode.MODULE_KIND_UNRENDERABLE
        ),
    )
    yield "OSError", OSError("probe: the disk refused the write")
    yield "RuntimeError", RuntimeError("probe: an unclassified writer failure")


def record(work: Path) -> dict[str, list[dict[str, Any]]]:
    corpus.quiet()
    entries: dict[str, list[dict[str, Any]]] = {}
    for number, subject in enumerate(corpus.case_subjects("refused")):
        entries[subject.key] = _run(subject, work / f"case-{number:03d}" / "pkg")

    destination = work / "destination-link" / "pkg"
    destination.mkdir(parents=True)
    (destination / "elsewhere").symlink_to(work)
    entries[f"destination_link:{DESTINATION_LINK_CASE}"] = _run(
        _case(DESTINATION_LINK_CASE), destination
    )

    for name, error in _writer_failures():
        with _writer_raising(error):
            entries[f"writer_failure:{name}"] = _run(
                _case(WRITER_FAILURE_CASE), work / f"writer-{name}" / "pkg"
            )
    return entries


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("command", choices=("record", "compare"))
    args = parser.parse_args()

    with tempfile.TemporaryDirectory(prefix="refusal-records-") as work:
        entries = record(Path(work))
    if args.command == "record":
        document = {"schema": refusal_records.SCHEMA, "records": entries}
        refusal_records.RECORDS_PATH.write_text(
            json.dumps(document, indent=1, sort_keys=True, ensure_ascii=False) + "\n"
        )
        print(f"recorded {len(entries)} entries to {refusal_records.RECORDS_PATH}")
        return 0
    base = refusal_records.load()
    found = [
        key for key in sorted(base.keys() | entries.keys()) if base.get(key) != entries.get(key)
    ]
    for key in found:
        print(f"{key}:\n  base: {base.get(key)}\n  now:  {entries.get(key)}")
    print(f"{len(found)} of {len(base)} entries differ")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
