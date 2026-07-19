"""Recoverably update the two Item 4 named-exclusion fixture projections.

Both complete candidates and the prospective corpus manifest are validated before the first
replacement. A durable same-filesystem journal and immutable backups restore both originals after
any failed or interrupted replacement.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agentic_mbse.sysml import constraint_facts as constraint_facts_module
from agentic_mbse.sysml.executable_profile import evaluate_profile

from sysml_codegen.analysis.constraint_lowering import excluded_usage_indices
from sysml_codegen.analysis.source_referent import (
    map_live_source_referent,
    validate_snapshot_source_referent,
)
from sysml_codegen.snapshot.serializer import snapshot_to_json

SPECS = {
    "catf_mfe_model/extraction_snapshot.json": tuple(range(65)),
    "constraint_non_numerical/extraction_snapshot.json": (0,),
}


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _file_manifest(root: Path, excluded_root: Path | None = None) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): _sha256(path.read_bytes())
        for path in sorted(root.rglob("*"))
        if path.is_file() and (excluded_root is None or not path.is_relative_to(excluded_root))
    }


def _fsync_file(path: Path) -> None:
    with path.open("rb") as stream:
        os.fsync(stream.fileno())


def _fsync_dir(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


@dataclass(frozen=True)
class PointerChange:
    fixture: str
    index: int
    usage_qualified_name: str | None
    old: str
    new: str


@dataclass(frozen=True)
class PreparedFixture:
    relative_path: str
    original: bytes
    candidate: bytes
    changes: tuple[PointerChange, ...]


@dataclass(frozen=True)
class PreparedTransaction:
    fixtures: tuple[PreparedFixture, ...]
    original_fixture_manifest: dict[str, str]
    candidate_fixture_manifest: dict[str, str]
    baseline_manifest: dict[str, str]


class FixtureLocationTransaction:
    def __init__(self, fixtures_root: Path, source_fixtures_root: Path | None = None):
        self.fixtures_root = fixtures_root.resolve()
        self.source_fixtures_root = (
            source_fixtures_root.resolve()
            if source_fixtures_root is not None
            else self.fixtures_root
        )
        self.transaction_dir = self.fixtures_root / ".snapshot-location-transaction"
        self.journal_path = self.transaction_dir / "journal.json"
        self.baseline_root = self.fixtures_root / "baseline_outputs"

    def _target(self, relative_path: str) -> Path:
        return self.fixtures_root / relative_path

    def _write_json(self, path: Path, value: Any) -> None:
        path.write_text(json.dumps(value, indent=2, sort_keys=True))
        _fsync_file(path)

    def _set_phase(self, phase: str) -> None:
        journal = json.loads(self.journal_path.read_text())
        journal["phase"] = phase
        self._write_json(self.journal_path, journal)
        _fsync_dir(self.transaction_dir)

    def _replace_target(self, staged: Path, target: Path) -> None:
        os.replace(staged, target)
        _fsync_dir(target.parent)

    def _clear_transaction(self) -> None:
        for path in sorted(self.transaction_dir.rglob("*"), reverse=True):
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                path.rmdir()
        self.transaction_dir.rmdir()

    def _fixture_manifest(self) -> dict[str, str]:
        return _file_manifest(self.fixtures_root, self.transaction_dir)

    def _baseline_manifest(self) -> dict[str, str]:
        return _file_manifest(self.baseline_root)

    def _verify_manifests(
        self, expected_fixture: dict[str, str], expected_baseline: dict[str, str]
    ) -> None:
        if self._fixture_manifest() != expected_fixture:
            raise RuntimeError("fixture manifest mismatch")
        if self._baseline_manifest() != expected_baseline:
            raise RuntimeError("baseline_outputs manifest mismatch")

    def _verify_staged_candidates(self, journal: dict[str, Any]) -> None:
        for relative_path, expected_hash in journal["candidate_hashes"].items():
            staged = self.transaction_dir / "candidates" / relative_path
            if not staged.is_file() or _sha256(staged.read_bytes()) != expected_hash:
                raise RuntimeError(f"staged candidate hash mismatch for {relative_path}")

    def recover_interrupted_run(self) -> bool:
        if not self.journal_path.exists():
            return False
        journal = json.loads(self.journal_path.read_text())
        for relative_path in SPECS:
            backup = self.transaction_dir / "backups" / relative_path
            if _sha256(backup.read_bytes()) != journal["original_hashes"][relative_path]:
                raise RuntimeError(f"backup hash mismatch for {relative_path}")
            target = self._target(relative_path)
            restore = self.transaction_dir / "restore" / relative_path
            restore.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(backup, restore)
            _fsync_file(restore)
            self._replace_target(restore, target)
            if _sha256(target.read_bytes()) != journal["original_hashes"][relative_path]:
                raise RuntimeError(f"rollback hash mismatch for {relative_path}")
        self._verify_manifests(journal["original_fixture_manifest"], journal["baseline_manifest"])
        self._clear_transaction()
        return True

    @staticmethod
    def _validate_candidate_diff(fixture: PreparedFixture) -> None:
        removed: list[str] = []
        added: list[str] = []
        original_lines = fixture.original.decode("utf-8").splitlines()
        candidate_lines = fixture.candidate.decode("utf-8").splitlines()
        for line in difflib.ndiff(original_lines, candidate_lines):
            if line.startswith("- "):
                removed.append(line[2:].strip())
            elif line.startswith("+ "):
                added.append(line[2:].strip())
        changed = [change for change in fixture.changes if change.old != change.new]
        expected_removed = [f'"file": {json.dumps(change.old)},' for change in changed]
        expected_added = [f'"file": {json.dumps(change.new)},' for change in changed]
        if removed != expected_removed or added != expected_added:
            raise RuntimeError(f"{fixture.relative_path}: diff exceeds location.file allowlist")

    def prepare(self) -> PreparedTransaction:
        self.recover_interrupted_run()
        original_manifest = self._fixture_manifest()
        baseline_manifest = self._baseline_manifest()
        prepared: list[PreparedFixture] = []
        for relative_path, expected_indices in SPECS.items():
            target = self._target(relative_path)
            original = target.read_bytes()
            original_text = original.decode("utf-8")
            raw = json.loads(original_text)
            if snapshot_to_json(raw) != original_text:
                raise RuntimeError(f"{relative_path} is not byte-stable through snapshot_to_json")
            before_timestamp = raw["captured_at"]
            before_usages = json.loads(json.dumps(raw["constraint_facts"]["usages"]))
            facts = constraint_facts_module.parse(json.dumps(raw["constraint_facts"]))
            decisions = evaluate_profile(facts).decisions
            selected = excluded_usage_indices(facts, decisions)
            located_named = tuple(
                index
                for index in selected
                if facts.usages[index].identity.name is not None
                and facts.usages[index].location is not None
            )
            if located_named != expected_indices:
                raise RuntimeError(
                    f"{relative_path}: selected named-location indices {located_named!r}, "
                    f"expected {expected_indices!r}"
                )
            model_root = self.source_fixtures_root / Path(relative_path).parent
            changes: list[PointerChange] = []
            for index in expected_indices:
                usage = raw["constraint_facts"]["usages"][index]
                old = usage["location"]["file"]
                try:
                    new = validate_snapshot_source_referent(old)
                except ValueError:
                    new = map_live_source_referent(old, [model_root])
                validate_snapshot_source_referent(new)
                usage["location"]["file"] = new
                changes.append(
                    PointerChange(
                        fixture=relative_path,
                        index=index,
                        usage_qualified_name=usage["identity"]["qualified_name"],
                        old=old,
                        new=new,
                    )
                )
            if raw["captured_at"] != before_timestamp:
                raise RuntimeError(f"{relative_path}: captured_at changed during preparation")
            after_usages = raw["constraint_facts"]["usages"]
            for index, (before, after) in enumerate(zip(before_usages, after_usages, strict=True)):
                if index in expected_indices:
                    restored = json.loads(json.dumps(after))
                    restored["location"]["file"] = before["location"]["file"]
                    if restored != before:
                        raise RuntimeError(f"{relative_path}: non-location usage delta at {index}")
                elif after != before:
                    raise RuntimeError(f"{relative_path}: unselected usage delta at {index}")
            candidate = snapshot_to_json(raw).encode("utf-8")
            reversed_raw = json.loads(candidate)
            for change in changes:
                reversed_raw["constraint_facts"]["usages"][change.index]["location"]["file"] = (
                    change.old
                )
            if snapshot_to_json(reversed_raw).encode("utf-8") != original:
                raise RuntimeError(f"{relative_path}: reverse substitution is not byte-identical")
            fixture = PreparedFixture(
                relative_path=relative_path,
                original=original,
                candidate=candidate,
                changes=tuple(changes),
            )
            self._validate_candidate_diff(fixture)
            prepared.append(fixture)
        prospective = dict(original_manifest)
        for fixture in prepared:
            prospective[fixture.relative_path] = _sha256(fixture.candidate)
        changed = {path for path in prospective if prospective[path] != original_manifest.get(path)}
        allowed = set(SPECS)
        if changed not in (set(), allowed):
            raise RuntimeError(
                f"prospective fixture delta is {sorted(changed)!r}, expected {sorted(allowed)!r}"
            )
        if self._baseline_manifest() != baseline_manifest:
            raise RuntimeError("baseline_outputs changed during preparation")
        return PreparedTransaction(
            fixtures=tuple(prepared),
            original_fixture_manifest=original_manifest,
            candidate_fixture_manifest=prospective,
            baseline_manifest=baseline_manifest,
        )

    def stage(self, prepared: PreparedTransaction) -> None:
        self._verify_manifests(prepared.original_fixture_manifest, prepared.baseline_manifest)
        self.transaction_dir.mkdir()
        original_hashes: dict[str, str] = {}
        candidate_hashes: dict[str, str] = {}
        pointer_changes: list[dict[str, Any]] = []
        for fixture in prepared.fixtures:
            backup = self.transaction_dir / "backups" / fixture.relative_path
            staged = self.transaction_dir / "candidates" / fixture.relative_path
            backup.parent.mkdir(parents=True, exist_ok=True)
            staged.parent.mkdir(parents=True, exist_ok=True)
            backup.write_bytes(fixture.original)
            staged.write_bytes(fixture.candidate)
            _fsync_file(backup)
            _fsync_file(staged)
            original_hashes[fixture.relative_path] = _sha256(fixture.original)
            candidate_hashes[fixture.relative_path] = _sha256(fixture.candidate)
            pointer_changes.extend(change.__dict__ for change in fixture.changes)
        self._write_json(
            self.journal_path,
            {
                "phase": "prepared",
                "original_hashes": original_hashes,
                "candidate_hashes": candidate_hashes,
                "pointer_changes": pointer_changes,
                "original_fixture_manifest": prepared.original_fixture_manifest,
                "candidate_fixture_manifest": prepared.candidate_fixture_manifest,
                "baseline_manifest": prepared.baseline_manifest,
            },
        )
        _fsync_dir(self.transaction_dir)

    def commit_staged(self) -> dict[str, Any]:
        try:
            journal = json.loads(self.journal_path.read_text())
            self._verify_staged_candidates(journal)
            relative_paths = list(SPECS)
            for ordinal, relative_path in enumerate(relative_paths, start=1):
                staged = self.transaction_dir / "candidates" / relative_path
                self._replace_target(staged, self._target(relative_path))
                self._set_phase("first_replaced" if ordinal == 1 else "second_replaced")
            journal = json.loads(self.journal_path.read_text())
            for relative_path, expected_hash in journal["candidate_hashes"].items():
                if _sha256(self._target(relative_path).read_bytes()) != expected_hash:
                    raise RuntimeError(f"post-write hash mismatch for {relative_path}")
            self._verify_manifests(
                journal["candidate_fixture_manifest"], journal["baseline_manifest"]
            )
            self._set_phase("verified")
            result = json.loads(self.journal_path.read_text())
            self._clear_transaction()
            return result
        except BaseException:
            self.recover_interrupted_run()
            raise

    def apply(self) -> dict[str, Any]:
        prepared = self.prepare()
        self.stage(prepared)
        return self.commit_staged()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixtures-root", type=Path, default=Path("tests/fixtures"))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    transaction = FixtureLocationTransaction(args.fixtures_root)
    if args.check:
        prepared = transaction.prepare()
        print(
            json.dumps(
                {
                    fixture.relative_path: {
                        "original": _sha256(fixture.original),
                        "candidate": _sha256(fixture.candidate),
                        "changes": [change.__dict__ for change in fixture.changes],
                    }
                    for fixture in prepared.fixtures
                },
                indent=2,
                sort_keys=True,
            )
        )
    else:
        print(json.dumps(transaction.apply(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
