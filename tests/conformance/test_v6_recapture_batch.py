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
import subprocess
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


def test_the_batch_names_its_current_transition_authority() -> None:
    """The 4A/API and final A/B recaptures do not inherit the old owner's acceptance."""
    assert MANIFEST["status"] == (
        "TRANSITIONED — stop-reinventing-the-parser A/B contract, 2026-08-17"
    )


def test_the_batch_claims_every_corpus_fixture_exactly_once() -> None:
    ledger = batch.read_ledger_exact_outcomes()
    assert set(RECORDS) == set(ledger)
    assert len(RECORDS) == 37
    assert set(CAPTURED) | set(REFUSED) == set(RECORDS)
    assert not set(CAPTURED) & set(REFUSED)


def test_the_batch_splits_the_corpus_the_way_the_ledger_does() -> None:
    assert len(CAPTURED) == 14
    assert len(REFUSED) == 23


def test_only_the_two_named_a_b_outcomes_move_from_the_historical_corpus_ledger() -> None:
    assert batch.compare_to_ledger(RECORDS) == [
        "deep_cross_scope_probe: ledger says 'graph 5/4/0/1', capture says "
        "'error: SI_OCCURRENCE_MISSING'",
        "plant_value_shapes: ledger says 'error: 2× SI_SELF_BINDING', capture says "
        "'error: SI_TYPE_INVALID'",
    ]


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


def test_an_unknown_positional_fixture_name_is_refused_before_anything_loads() -> None:
    """A mistyped fixture name fails loud, license-free, naming the offender.

    The v5 capture scripts got this from their shared name filter, which loses its last
    caller when they retire. The rejection moves here, to the driver that survives
    (owner ruling 2026-08-11, REVISE step 2 item 6). License-free because the check reads
    only the committed manifest: no model is loaded on this path, which is what makes it
    runnable in the same place as the rest of this file.

    Named replacement for ``tests/unit/test_capture_fixtures_filter.py``'s
    ``test_unknown_fixture_name_errors`` and its four ``select_fixtures`` unit nodes.
    """
    result = subprocess.run(
        [sys.executable, "scripts/capture_v6_batch.py", "no_such_fixture", "sample_model"],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    assert result.returncode == 2, result.stdout
    assert "no_such_fixture" in result.stderr
    # The valid name in the same argument list is not treated as a partial success.
    assert "captured" not in result.stdout


def test_a_known_fixture_name_passes_the_same_check() -> None:
    """The refusal discriminates: ``--check`` with a real corpus name still runs.

    Without this, a driver that rejected every positional name would pass the node above.
    """
    result = subprocess.run(
        [sys.executable, "scripts/capture_v6_batch.py", "--check", "sample_model"],
        capture_output=True,
        text=True,
        cwd=ROOT,
    )
    assert result.returncode == 0, result.stdout + result.stderr
