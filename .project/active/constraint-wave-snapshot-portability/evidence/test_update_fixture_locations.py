from __future__ import annotations

import importlib.util
import json
import shutil
import sys
from pathlib import Path

import pytest

MODULE_PATH = Path(__file__).with_name("update_fixture_locations.py")
SPEC = importlib.util.spec_from_file_location("update_fixture_locations", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)
FixtureLocationTransaction = MODULE.FixtureLocationTransaction
SOURCE_FIXTURES = Path("tests/fixtures").resolve()


def _legacyize_targets(root: Path) -> None:
    for relative_path, indices in MODULE.SPECS.items():
        target = root / relative_path
        raw = json.loads(target.read_text())
        source_root = SOURCE_FIXTURES / Path(relative_path).parent
        for index in indices:
            location = raw["constraint_facts"]["usages"][index]["location"]
            referent = location["file"]
            assert referent.startswith("root-0/")
            absolute = source_root / referent.removeprefix("root-0/")
            location["file"] = "///" + absolute.as_posix().lstrip("/")
        target.write_text(MODULE.snapshot_to_json(raw))


def _copied_legacy_fixtures(tmp_path: Path) -> Path:
    root = tmp_path / "fixtures"
    shutil.copytree(SOURCE_FIXTURES, root)
    _legacyize_targets(root)
    return root


def _target_bytes(root: Path) -> dict[str, bytes]:
    return {path: (root / path).read_bytes() for path in MODULE.SPECS}


def _transaction(tmp_path: Path) -> tuple[Path, FixtureLocationTransaction]:
    root = _copied_legacy_fixtures(tmp_path)
    return root, FixtureLocationTransaction(root, SOURCE_FIXTURES)


def test_prepare_validates_candidates_and_complete_manifests_without_writing(tmp_path):
    root, transaction = _transaction(tmp_path)
    before = _target_bytes(root)
    prepared = transaction.prepare()
    assert [fixture.relative_path for fixture in prepared.fixtures] == list(MODULE.SPECS)
    assert [len(fixture.changes) for fixture in prepared.fixtures] == [65, 1]
    assert set(prepared.original_fixture_manifest) == set(prepared.candidate_fixture_manifest)
    assert {
        path
        for path, digest in prepared.candidate_fixture_manifest.items()
        if prepared.original_fixture_manifest[path] != digest
    } == set(MODULE.SPECS)
    assert prepared.baseline_manifest == MODULE._file_manifest(root / "baseline_outputs")
    assert _target_bytes(root) == before
    assert not transaction.transaction_dir.exists()


def test_validation_failure_writes_nothing(tmp_path):
    root, transaction = _transaction(tmp_path)
    target = root / "constraint_non_numerical/extraction_snapshot.json"
    target.write_text(target.read_text().replace('"captured_at"', '"wrong_timestamp_key"', 1))
    before = _target_bytes(root)
    with pytest.raises(KeyError):
        transaction.prepare()
    assert _target_bytes(root) == before
    assert not transaction.transaction_dir.exists()


def test_staged_candidate_mismatch_restores_original_manifests(tmp_path):
    root, transaction = _transaction(tmp_path)
    originals = _target_bytes(root)
    prepared = transaction.prepare()
    transaction.stage(prepared)
    first = next(iter(MODULE.SPECS))
    staged = transaction.transaction_dir / "candidates" / first
    staged.write_bytes(staged.read_bytes() + b"corrupt")
    with pytest.raises(RuntimeError, match="staged candidate hash mismatch"):
        transaction.commit_staged()
    assert _target_bytes(root) == originals
    assert transaction._fixture_manifest() == prepared.original_fixture_manifest
    assert transaction._baseline_manifest() == prepared.baseline_manifest
    assert not transaction.transaction_dir.exists()


@pytest.mark.parametrize("failed_ordinal", [1, 2])
def test_replace_failure_restores_both_originals(tmp_path, monkeypatch, failed_ordinal):
    root, transaction = _transaction(tmp_path)
    originals = _target_bytes(root)
    prepared = transaction.prepare()
    real_replace = transaction._replace_target
    replacements = 0

    def fail_selected_replace(staged, target):
        nonlocal replacements
        replacements += 1
        if replacements == failed_ordinal:
            raise RuntimeError(f"injected replacement {failed_ordinal} failure")
        real_replace(staged, target)

    monkeypatch.setattr(transaction, "_replace_target", fail_selected_replace)
    with pytest.raises(RuntimeError, match=f"replacement {failed_ordinal}"):
        transaction.apply()
    assert _target_bytes(root) == originals
    assert transaction._fixture_manifest() == prepared.original_fixture_manifest
    assert transaction._baseline_manifest() == prepared.baseline_manifest
    assert not transaction.transaction_dir.exists()


def test_post_write_manifest_failure_rolls_back_complete_manifests(tmp_path, monkeypatch):
    root, transaction = _transaction(tmp_path)
    originals = _target_bytes(root)
    prepared = transaction.prepare()
    transaction.stage(prepared)
    real_verify = transaction._verify_manifests
    failed = False

    def fail_candidate_manifest(expected_fixture, expected_baseline):
        nonlocal failed
        if expected_fixture == prepared.candidate_fixture_manifest and not failed:
            failed = True
            raise RuntimeError("injected post-write manifest failure")
        real_verify(expected_fixture, expected_baseline)

    monkeypatch.setattr(transaction, "_verify_manifests", fail_candidate_manifest)
    with pytest.raises(RuntimeError, match="post-write manifest"):
        transaction.commit_staged()
    assert _target_bytes(root) == originals
    assert transaction._fixture_manifest() == prepared.original_fixture_manifest
    assert transaction._baseline_manifest() == prepared.baseline_manifest
    assert not transaction.transaction_dir.exists()


def _leave_interrupted_at(transaction: FixtureLocationTransaction, phase: str) -> None:
    prepared = transaction.prepare()
    transaction.stage(prepared)
    if phase == "prepared":
        return
    for ordinal, relative_path in enumerate(MODULE.SPECS, start=1):
        staged = transaction.transaction_dir / "candidates" / relative_path
        transaction._replace_target(staged, transaction._target(relative_path))
        transaction._set_phase("first_replaced" if ordinal == 1 else "second_replaced")
        if phase == "first_replaced" and ordinal == 1:
            return
    if phase == "second_replaced":
        return
    transaction._verify_manifests(prepared.candidate_fixture_manifest, prepared.baseline_manifest)
    transaction._set_phase("verified")


@pytest.mark.parametrize("phase", ["prepared", "first_replaced", "second_replaced", "verified"])
def test_every_journal_phase_recovers_original_pair_and_manifests(tmp_path, phase):
    root, transaction = _transaction(tmp_path)
    originals = _target_bytes(root)
    original_manifest = transaction._fixture_manifest()
    baseline_manifest = transaction._baseline_manifest()
    _leave_interrupted_at(transaction, phase)
    assert json.loads(transaction.journal_path.read_text())["phase"] == phase
    assert transaction.recover_interrupted_run() is True
    assert _target_bytes(root) == originals
    assert transaction._fixture_manifest() == original_manifest
    assert transaction._baseline_manifest() == baseline_manifest
    assert not transaction.transaction_dir.exists()


def test_success_verifies_candidate_manifests_and_canonical_rerun_is_idempotent(tmp_path):
    root, transaction = _transaction(tmp_path)
    prepared = transaction.prepare()
    result = transaction.apply()
    assert result["phase"] == "verified"
    assert result["original_fixture_manifest"] == prepared.original_fixture_manifest
    assert result["candidate_fixture_manifest"] == prepared.candidate_fixture_manifest
    assert result["baseline_manifest"] == prepared.baseline_manifest
    assert transaction._fixture_manifest() == prepared.candidate_fixture_manifest
    assert transaction._baseline_manifest() == prepared.baseline_manifest
    assert not transaction.transaction_dir.exists()
    after = _target_bytes(root)
    rerun = transaction.prepare()
    assert all(fixture.original == fixture.candidate for fixture in rerun.fixtures)
    assert rerun.original_fixture_manifest == rerun.candidate_fixture_manifest
    assert _target_bytes(root) == after
