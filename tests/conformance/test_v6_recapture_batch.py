"""The proposed v6 recapture batch is re-derivable from the committed files.

The batch is the "replacements ready in the same candidate" that the plan's Gate 4C rule
requires before the v5 fixtures may retire. A manifest nobody re-checks is exactly the kind
of written-down claim this recovery exists to distrust, so these read the committed bytes
and rebuild the claim: every corpus fixture is claimed once, every captured snapshot loads
and projects to the outcome recorded for it, every refusal is typed, and the whole set still
agrees with the amended Phase 2 corpus ledger.

Only the projection half needs no license — loading a sealed snapshot and projecting it is
the offline route — so most of this file runs license-free. That is the point: the batch has
to be checkable by someone who cannot capture.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

import capture_v6_batch as batch  # noqa: E402

from sysml_codegen.elaboration import project  # noqa: E402
from sysml_codegen.snapshot.envelope import load_instance_graph_snapshot  # noqa: E402

MANIFEST = json.loads(batch.MANIFEST.read_text())
RECORDS: dict[str, dict] = MANIFEST["records"]
CAPTURED: list[str] = MANIFEST["captured"]
REFUSED: list[str] = MANIFEST["refused"]


def test_the_batch_is_marked_proposed_and_not_accepted() -> None:
    """It is readiness, not authority, until the owner says otherwise at Phase 5."""
    assert MANIFEST["status"].startswith("PROPOSED")
    assert "owner acceptance pending" in MANIFEST["status"]


def test_the_batch_claims_every_corpus_fixture_exactly_once() -> None:
    ledger = batch.read_ledger_exact_outcomes()
    assert set(RECORDS) == set(ledger)
    assert len(RECORDS) == 37
    assert set(CAPTURED) | set(REFUSED) == set(RECORDS)
    assert not set(CAPTURED) & set(REFUSED)


def test_the_batch_splits_the_corpus_the_way_the_ledger_does() -> None:
    assert len(CAPTURED) == 15
    assert len(REFUSED) == 22


def test_every_recorded_outcome_still_agrees_with_the_corpus_ledger() -> None:
    assert batch.compare_to_ledger(RECORDS) == []


@pytest.mark.parametrize("name", CAPTURED)
def test_a_captured_snapshot_loads_and_projects_to_the_outcome_recorded_for_it(
    name: str,
) -> None:
    """The recorded numbers are re-derived from the committed bytes, not trusted."""
    record = RECORDS[name]
    snapshot = ROOT / record["snapshot"]
    assert snapshot.is_file(), f"{name}: the manifest names a snapshot that is not committed"

    outcome = batch._graph_outcome(project(load_instance_graph_snapshot(snapshot)))
    for field in ("modules", "entry_points", "aliases", "constraints"):
        assert outcome[field] == record[field], f"{name}: {field} moved since capture"


@pytest.mark.parametrize("name", CAPTURED)
def test_a_captured_snapshot_is_byte_identical_to_its_recorded_digest(name: str) -> None:
    import hashlib

    snapshot = ROOT / RECORDS[name]["snapshot"]
    assert hashlib.sha256(snapshot.read_bytes()).hexdigest() == RECORDS[name]["sha256"]


@pytest.mark.parametrize("name", REFUSED)
def test_a_refusal_record_is_typed_and_carries_its_exact_code_multiset(name: str) -> None:
    """A refusal is an outcome. Summarising it would lose the thing that makes it one."""
    record = RECORDS[name]
    assert record["error_type"], f"{name}: refusal with no error type"
    assert record["message"], f"{name}: refusal with no message"
    assert record["codes"] == sorted(record["codes"]), f"{name}: codes are not canonical"


def test_the_batch_carries_no_absolute_path() -> None:
    """A batch that names a checkout root is not portable, and portability is the point."""
    assert str(ROOT) not in batch.MANIFEST.read_text()
    for name in CAPTURED:
        assert str(ROOT) not in (ROOT / RECORDS[name]["snapshot"]).read_text()


def test_every_corpus_fixture_with_a_snapshot_is_one_the_batch_claims() -> None:
    """Restricted to the corpus: a v6 snapshot beside a corpus fixture must be in the batch.

    Not every committed v6 snapshot belongs to the corpus. The Gate 4C part 6 D-5 variants
    carry their own so a repointed test can read them without a licence, and they are
    deliberately outside the batch — they are coverage fixtures, not corpus rows. Comparing
    over the whole fixtures tree would make adding one of those look like batch drift.
    """
    on_disk = {
        path.parent.name
        for path in (ROOT / "tests" / "fixtures").glob(f"*/{batch.SNAPSHOT_NAME}")
    }
    assert set(CAPTURED) == on_disk & set(RECORDS), (
        "the batch and the committed corpus snapshots disagree"
    )
