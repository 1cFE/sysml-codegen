"""The subjects the 2b parity scripts run ``run_codegen`` on (EXEC-SUBSET-CONTRACT Item 2b).

Shared by ``package_manifest.py`` and ``refusal_records.py``. A subject is one call of
``run_codegen(GenerationConfig(...))``, the contract every 2b phase keeps: a 2a case model
live, a committed v6 snapshot replayed, or the snapshot's source models live where they exist
in this checkout. Licensed.
"""

from __future__ import annotations

import json
import logging
import sys
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

#: Committed v6 snapshot → the directory holding its source models. The catf_mfe_d5 sources
#: are not committed; they were regenerated into the untracked ``build/snapshot-regen/`` (the
#: resolver is in Item 2b's history, ``spike-snapshot/resolve_sources.py``). A subject whose
#: source directory is absent is skipped and named by ``missing_sources``.
SNAPSHOT_SOURCES = REPO / "scripts/snapshot_sources.json"


@dataclass(frozen=True)
class Subject:
    #: Stable key: ``case:<id>``, ``live:<snapshot path>`` or ``replay:<snapshot path>``.
    key: str
    models: Path | None
    snapshot: Path | None


def case_subjects(outcome: str) -> Iterator[Subject]:
    """Every 2a case whose stored generator outcome is ``outcome`` (generated or refused)."""
    from tests.helpers.refusal_cases import cases

    for answer in cases.all_answers():
        if answer.generator.run.outcome.value == outcome:
            yield Subject(f"case:{answer.case_id}", cases.model_root(answer), None)


def snapshot_subjects() -> Iterator[Subject]:
    """Each committed snapshot replayed, and its sources live where they are present."""
    for snapshot, sources in sorted(json.loads(SNAPSHOT_SOURCES.read_text()).items()):
        yield Subject(f"replay:{snapshot}", None, REPO / snapshot)
        if (REPO / sources).is_dir():
            yield Subject(f"live:{snapshot}", REPO / sources, None)


def missing_sources() -> list[str]:
    return [
        snapshot
        for snapshot, sources in sorted(json.loads(SNAPSHOT_SOURCES.read_text()).items())
        if not (REPO / sources).is_dir()
    ]


def config_for(subject: Subject, output: Path):  # -> GenerationConfig
    from sysml_codegen.cli import GenerationConfig

    return GenerationConfig(
        output_path=output, models_path=subject.models, from_snapshot=subject.snapshot
    )


def quiet() -> None:
    """Keep ``run_codegen``'s INFO lines off the terminal; records still reach handlers."""
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")
