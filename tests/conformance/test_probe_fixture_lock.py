"""The probe/fixture lock, verified against the historical tree it names.

Until now this leg existed only as a hand-run, and that was the one real residual gap in
the evidence contract.  See
`.project/active/stop-reinventing-the-parser/design.md#the-missing-committed-check--phase-1-adds-it`.

Three legs verify the lock, and every locked byte is covered by exactly one of them:

1. **This module, leg 1** — the 118 locked hashes recompute against the tree the lock's own
   `probe_fixture_commit` field names, read from Git.  Never the working tree: those bytes
   are history, and nothing in this item writes them.
2. **Leg 2** — current outputs are validated by `verification/capture_baseline.py`'s
   transition-ledger machinery, not against the lock.  Its committed callers live in
   `tests/conformance/test_stop_parser_documentation_contract.py`.
3. **This module, leg 3** — the six non-fixture rows are live code.  They are pinned at their
   *current* bytes, and any difference from lock-time bytes must be owned by a named row in
   `verification/expected-transitions.md`.

A mismatch in leg 1 means evidence tampering or a history rewrite.  It returns the item to
design; it never authorizes a replacement lock.  Nothing here writes the lock file.

The historical bytes are read through the same `git show` route `capture_baseline._git_bytes`
uses, so this module requires the declared artifact-source manifest exactly as its sibling
verification tests do.  Without it the tests fail loudly rather than skipping.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import pytest

REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
LOCK_PATH = REPOSITORY_ROOT / "verification" / "probe-fixture-lock.json"
LEDGER_PATH = REPOSITORY_ROOT / "verification" / "expected-transitions.md"

#: The tree the lock's hashes describe.  Asserted against the lock's own field below and
#: never used to *find* that field.  `43edf9bd…` is the lock file's home commit — the commit
#: whose entire diff is adding the lock — not the tree its hashes describe.
PROBE_FIXTURE_COMMIT = "20f9e60a19b30bc1ec9a27aacb08380f4bc45602"
PROBE_FIXTURE_PARENT = "7b29d8b636e284364a4fdce9079f153c51c867ea"
LOCKED_ROW_COUNT = 118

#: The live code the lock pins.  Leg 3 owns these; legs 1 and 2 do not.
NON_FIXTURE_ROWS = (
    ".project/active/stop-reinventing-the-parser/probes/b10_document_origin.py",
    ".project/active/stop-reinventing-the-parser/probes/b2_containment_address_feasibility.py",
    ".project/active/stop-reinventing-the-parser/probes/b8_resolved_fact_totality.py",
    ".project/active/stop-reinventing-the-parser/probes/probe_support.py",
    ".project/active/stop-reinventing-the-parser/probes/test_probe_contracts.py",
    "verification/capture_baseline.py",
)

#: One explicit non-fixture metadata input used by the retained probes.  This is an
#: allowlist, not a general structural classifier; any future ``verification/*`` row is
#: rejected until its responsibility is reviewed and added deliberately.
FIXTURE_METADATA_EXCEPTIONS = ("verification/fixture-manifest.json",)


@pytest.fixture(scope="module")
def lock() -> dict:
    return json.loads(LOCK_PATH.read_text())


@pytest.fixture(scope="module")
def history_root() -> Path:
    """The declared Git history, resolved the way `capture_baseline` resolves it."""
    from verification.artifact_sources import codegen_history_root

    return codegen_history_root(REPOSITORY_ROOT)


def _git_bytes(history: Path, commit: str, path: str) -> bytes:
    return subprocess.run(
        ["git", "-C", str(history), "show", f"{commit}:{path}"],
        check=True,
        capture_output=True,
    ).stdout


def test_lock_names_its_own_authoritative_tree(lock: dict) -> None:
    """Leg 1 reads the commit from the lock, then checks it — not the other way round."""
    assert lock["schema_version"] == "stop-parser-probe-lock/v1"
    assert lock["probe_fixture_commit"] == PROBE_FIXTURE_COMMIT
    assert lock["probe_fixture_parent"] == PROBE_FIXTURE_PARENT


def test_recorded_probe_commit_parentage_holds(history_root: Path) -> None:
    """The recorded parent relationship is part of the lock's provenance."""
    parent = subprocess.run(
        ["git", "-C", str(history_root), "rev-parse", f"{PROBE_FIXTURE_COMMIT}^"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    assert parent == PROBE_FIXTURE_PARENT


def test_every_locked_hash_recomputes_against_the_named_historical_tree(
    lock: dict,
    history_root: Path,
) -> None:
    """Leg 1: all 118 rows, read from Git at the tree the lock names."""
    commit = lock["probe_fixture_commit"]
    assert commit == PROBE_FIXTURE_COMMIT

    rows = lock["files"]
    mismatches: list[str] = []
    read = 0
    for row in rows:
        historical = _git_bytes(history_root, commit, row["path"])
        read += 1
        actual = hashlib.sha256(historical).hexdigest()
        if actual != row["sha256"]:
            mismatches.append(f"{row['path']}: locked {row['sha256']}, recomputed {actual}")

    # Anti-vacuity: a lock that verified zero rows would otherwise pass silently.
    assert read == len(rows) == LOCKED_ROW_COUNT
    assert not mismatches, f"lock does not recompute against {commit}: {mismatches}"


def test_locked_paths_are_unique_and_repository_relative(lock: dict) -> None:
    """Anti-vacuity: 118 rows, each naming a distinct portable path."""
    paths = [row["path"] for row in lock["files"]]
    assert len(set(paths)) == LOCKED_ROW_COUNT
    assert not [path for path in paths if Path(path).is_absolute() or ".." in Path(path).parts]


def test_locked_rows_split_into_fixture_inputs_and_verification_code(lock: dict) -> None:
    """The two classes are verified differently, so the split itself is pinned."""
    paths = {row["path"] for row in lock["files"]}
    assert set(NON_FIXTURE_ROWS) <= paths
    fixture_inputs = paths - set(NON_FIXTURE_ROWS)
    assert len(fixture_inputs) == LOCKED_ROW_COUNT - len(NON_FIXTURE_ROWS)
    assert all(
        path.startswith("tests/fixtures/") or path in FIXTURE_METADATA_EXCEPTIONS
        for path in fixture_inputs
    )
    assert set(FIXTURE_METADATA_EXCEPTIONS) <= fixture_inputs


def _ledger_row_for_path(path: str) -> tuple[str, ...]:
    matches: list[tuple[str, ...]] = []
    for line in LEDGER_PATH.read_text().splitlines():
        if not line.startswith("|"):
            continue
        cells = tuple(cell.strip().strip("`") for cell in line.strip().strip("|").split("|"))
        if cells and cells[0] == path:
            matches.append(cells)
    assert len(matches) == 1, f"expected one ledger row for {path}, found {matches}"
    return matches[0]


@pytest.mark.parametrize("locked_path", NON_FIXTURE_ROWS)
def test_locked_verification_code_is_pinned_at_current_bytes(
    lock: dict,
    locked_path: str,
) -> None:
    """Leg 3: live code is pinned now, and every difference is ledger-owned.

    `verification/capture_baseline.py` is the one file that differs from its lock-time
    bytes today; its row cites `da4aa78` and `46694e2`.  The five probe scripts are
    unchanged and are pinned at their lock-time hashes.
    """
    [row] = [item for item in lock["files"] if item["path"] == locked_path]
    current = hashlib.sha256((REPOSITORY_ROOT / locked_path).read_bytes()).hexdigest()
    if current == row["sha256"]:
        return

    ledger_row = _ledger_row_for_path(locked_path)
    assert row["sha256"] in ledger_row, f"ledger row for {locked_path} omits its lock-time hash"
    assert current in ledger_row, f"ledger row for {locked_path} omits its current hash {current}"


def test_the_lock_file_is_never_rewritten_by_this_check(lock: dict) -> None:
    """Reading the lock must not disturb it; re-locking would erase the provenance."""
    assert json.loads(LOCK_PATH.read_text()) == lock
