#!/usr/bin/env python3
"""Run the approved B37 accepted-candidate batch exactly once."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import agentic_mbse
import syside

import sysml_codegen
from sysml_codegen.elaboration import ElaborationDiagnosticError
from sysml_codegen.orchestration import (
    build_pipeline_context,
    build_pipeline_context_from_snapshot,
)
from sysml_codegen.snapshot import capture_snapshot, load_snapshot
from sysml_codegen.snapshot.envelope import canonical_json

ROOT = Path(__file__).resolve().parents[1]
CENSUS = ROOT / ".project/active/elaborator-cutover/cutover-census.md"
FIXTURES = ROOT / "tests/fixtures"
CANDIDATE_DIR = Path("/tmp/elaborator-cutover-item7-candidate")
AGENTIC_ROOT = ROOT.parent / "agentic-mbse"
TEAX_ROOT = ROOT.parent / "teax"
TEAX_INTERPRETER = TEAX_ROOT / ".venv/bin/python"
TEAX_HEAD = "fa0e06a99b070346e68a3b3c29cfec546f3ac728"
PROJECTOR_MARKER = "instance-projector/v1"

_ROW = re.compile(
    r"^\| `(B37-[0-9]{2})` \| `([^`]+)` \| (.*?) \| (.*?) \|$",
    re.MULTILINE,
)
_DIAGNOSTIC = re.compile(r"(?:(\d+)× )?`(SI_[A-Z0-9_]+)`")


@dataclass(frozen=True, slots=True)
class ManifestRow:
    id: str
    fixture: str
    outcome: str
    diagnostics: tuple[tuple[str, int], ...]
    classification: str
    required: str
    governing_contract: str

    def expected_record(self) -> dict[str, object]:
        record: dict[str, object] = {
            "id": self.id,
            "fixture": self.fixture,
            "required": self.outcome,
            "actual": self.outcome,
            "diagnostics": dict(self.diagnostics),
            "classification": self.classification,
            "artifact": None,
        }
        if self.outcome == "v6":
            record["artifact"] = f"snapshots/{self.id}-{self.fixture}.json"
            record["route_equality"] = True
        if self.outcome == "control":
            record["exception"] = "CodeGenerationError"
        return record


def load_approved_manifest(census_path: Path = CENSUS) -> tuple[ManifestRow, ...]:
    """Parse the approved B37 table without discovering any fixture."""
    rows: list[ManifestRow] = []
    for identifier, fixture, required, governing in _ROW.findall(census_path.read_text()):
        if required.startswith("V6"):
            outcome = "v6"
        elif "CodeGenerationError" in required:
            outcome = "control"
        else:
            outcome = "refusal"
        diagnostics = tuple(
            sorted((code, int(count or "1")) for count, code in _DIAGNOSTIC.findall(required))
        )
        classification = (
            "expected-fix" if "expected-fix" in governing else "expected-collapse"
        )
        rows.append(
            ManifestRow(
                id=identifier,
                fixture=fixture,
                outcome=outcome,
                diagnostics=diagnostics,
                classification=classification,
                required=required,
                governing_contract=governing,
            )
        )
    expected_ids = [f"B37-{index:02d}" for index in range(1, 38)]
    if [row.id for row in rows] != expected_ids:
        raise ValueError("approved census must contain B37-01 through B37-37 exactly once")
    if len({row.fixture for row in rows}) != 37:
        raise ValueError("approved census must contain exactly 37 unique fixture paths")
    return tuple(rows)


def validate_candidate_record(
    candidate: dict[str, object],
    manifest: tuple[ManifestRow, ...],
) -> None:
    """Fail closed on count, outcome, artifact, diagnostic, and classification drift."""
    rows = candidate.get("rows")
    if not isinstance(rows, list) or len(rows) != 37:
        raise ValueError("candidate must contain exactly 37 rows")
    expected = {row.id: row for row in manifest}
    actual_ids = [row.get("id") for row in rows if isinstance(row, dict)]
    if actual_ids != [row.id for row in manifest]:
        raise ValueError("candidate row IDs/order disagree with the approved manifest")

    computed = Counter()
    for actual in rows:
        if not isinstance(actual, dict):
            raise ValueError("candidate rows must be JSON objects")
        approved = expected[str(actual["id"])]
        if actual.get("fixture") != approved.fixture:
            raise ValueError(f"{approved.id} fixture path changed")
        if actual.get("actual") != approved.outcome:
            raise ValueError(f"{approved.id} outcome is unexpected")
        computed[approved.outcome] += 1
        artifact = actual.get("artifact")
        if approved.outcome == "v6":
            if not isinstance(artifact, str) or not artifact:
                raise ValueError(f"{approved.id} is missing its v6 artifact")
            if actual.get("route_equality") is not True:
                raise ValueError(f"{approved.id} route digests disagree")
        elif artifact is not None:
            raise ValueError(f"{approved.id} has an unexpected artifact")
        if dict(approved.diagnostics) != actual.get("diagnostics", {}):
            raise ValueError(f"{approved.id} diagnostic multiset changed")
        if actual.get("classification") != approved.classification:
            raise ValueError(f"{approved.id} semantic classification changed")
        if approved.outcome == "control" and actual.get("exception") != "CodeGenerationError":
            raise ValueError(f"{approved.id} control did not raise CodeGenerationError")

    required_counts = {"v6": 14, "refusal": 22, "control": 1}
    if dict(candidate.get("counts", {})) != required_counts or dict(computed) != required_counts:
        raise ValueError("candidate outcome counts are not 14 v6 / 22 refusal / 1 control")
    semantic_diffs = candidate.get("semantic_diffs")
    if not isinstance(semantic_diffs, dict) or semantic_diffs.get("unclassified") != []:
        raise ValueError("candidate contains an unclassified semantic diff")
    if semantic_diffs.get("classified") != [row.id for row in manifest]:
        raise ValueError("candidate does not classify all 37 semantic outcomes")
    if candidate.get("v5_artifacts") != []:
        raise ValueError("candidate contains a v5 artifact")


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _file_sha256(path: Path) -> str:
    return _sha256(path.read_bytes())


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _status(repo: Path) -> dict[str, object]:
    raw = subprocess.run(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=repo,
        check=True,
        capture_output=True,
    ).stdout
    return {
        "entries": len(raw.decode().splitlines()),
        "sha256": _sha256(raw),
    }


def _environment() -> dict[str, object]:
    teax_status = _git(TEAX_ROOT, "status", "--porcelain=v1", "--untracked-files=all")
    teax_head = _git(TEAX_ROOT, "rev-parse", "HEAD")
    if teax_head != TEAX_HEAD or teax_status:
        raise RuntimeError("the pinned TEAx checkout is not clean at the approved revision")
    memory_kib = 0
    for line in Path("/proc/meminfo").read_text().splitlines():
        if line.startswith("MemTotal:"):
            memory_kib = int(line.split()[1])
            break
    return {
        "captured_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "platform": platform.platform(),
        "kernel": platform.release(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "memory_kib": memory_kib,
        "python": sys.version,
        "python_executable": sys.executable,
        "uv": subprocess.run(
            ["uv", "--version"], check=True, capture_output=True, text=True
        ).stdout.strip(),
        "syside_version": syside.__version__,
        "syside_license_present": bool(os.environ.get("SYSIDE_LICENSE_KEY")),
        "sysml_codegen_version": sysml_codegen.__version__,
        "agentic_mbse_version": agentic_mbse.__version__,
        "repositories": {
            "codegen": {
                "head": _git(ROOT, "rev-parse", "HEAD"),
                "status": _status(ROOT),
                "lock_sha256": _file_sha256(ROOT / "uv.lock"),
            },
            "agentic": {
                "head": _git(AGENTIC_ROOT, "rev-parse", "HEAD"),
                "status": _status(AGENTIC_ROOT),
                "lock_sha256": _file_sha256(AGENTIC_ROOT / "uv.lock"),
            },
            "teax": {
                "head": teax_head,
                "status": "clean",
                "interpreter": str(TEAX_INTERPRETER),
                "interpreter_sha256": _file_sha256(TEAX_INTERPRETER),
                "lock_sha256": _file_sha256(TEAX_ROOT / "uv.lock"),
            },
        },
        "candidate_id": "__PENDING_PHASE9__",
    }


def _write_json(path: Path, value: object) -> None:
    payload = json.dumps(
        value,
        sort_keys=True,
        indent=2,
        ensure_ascii=True,
        allow_nan=False,
    ).encode() + b"\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o444)
    with os.fdopen(descriptor, "wb") as stream:
        stream.write(payload)
        stream.flush()
        os.fsync(stream.fileno())


def _projected_digest(graph: Any) -> str:
    payload = graph.model_dump(mode="json")
    payload["fallback_entry_points"] = sorted(graph.fallback_entry_points)
    payload["constraint_catalog"] = (
        graph.constraint_catalog.model_dump(mode="json")
        if graph.constraint_catalog is not None
        else None
    )
    return _sha256(
        json.dumps(
            {"projector_semantics": PROJECTOR_MARKER, "computation_graph": payload},
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode()
    )


def _graph_counts(graph: Any) -> dict[str, int]:
    return {
        "occurrences": len(graph.occurrences),
        "attributes": len(graph.attrs),
        "calculations": len(graph.calcs),
        "constraints": len(graph.constraints),
        "nodes": len(graph.attrs) + len(graph.calcs) + len(graph.constraints),
        "edges": sum(node.alias_target is not None for node in graph.attrs.values())
        + sum(len(node.inputs) for node in graph.calcs.values())
        + sum(len(node.inputs) for node in graph.constraints.values()),
    }


def _normalized_envelope_digest(path: Path) -> str:
    document = json.loads(path.read_bytes())
    document["capture"]["captured_at"] = "__NORMALIZED_CAPTURE_TIME__"
    document.pop("integrity")
    return _sha256(canonical_json(document))


def _failure(error: BaseException) -> dict[str, object]:
    diagnostics: dict[str, int] = {}
    if isinstance(error, ElaborationDiagnosticError):
        diagnostics = dict(sorted(Counter(item.code.value for item in error.diagnostics).items()))
    return {
        "exception": type(error).__name__,
        "message": str(error),
        "diagnostics": diagnostics,
    }


def _actual_outcome(failure: dict[str, object]) -> str:
    if failure["exception"] == "ElaborationDiagnosticError":
        return "refusal"
    if failure["exception"] == "CodeGenerationError":
        return "control"
    return "unexpected-error"


def _run_row(row: ManifestRow, candidate_dir: Path) -> dict[str, object]:
    fixture = FIXTURES / row.fixture
    snapshot = candidate_dir / "snapshots" / f"{row.id}-{row.fixture}.json"
    record: dict[str, object] = {
        "id": row.id,
        "fixture": row.fixture,
        "required": row.outcome,
        "classification": row.classification,
        "governing_contract": row.governing_contract,
        "artifact": None,
    }

    try:
        live_context = build_pipeline_context([fixture])
    except BaseException as live_error:
        live_failure = _failure(live_error)
        record["live"] = live_failure
        try:
            capture_snapshot([fixture], snapshot)
        except BaseException as capture_error:
            capture_failure = _failure(capture_error)
            record["capture"] = capture_failure
            record["actual"] = _actual_outcome(capture_failure)
            record["diagnostics"] = capture_failure["diagnostics"]
            record["exception"] = capture_failure["exception"]
            record["no_artifact"] = not snapshot.exists()
            record["live_capture_failure_equal"] = (
                live_failure["exception"] == capture_failure["exception"]
                and live_failure["diagnostics"] == capture_failure["diagnostics"]
            )
            return record
        record["actual"] = "v6"
        record["artifact"] = str(snapshot.relative_to(candidate_dir))
        record["diagnostics"] = {}
        record["unexpected_live_failure"] = live_failure
        return record

    try:
        capture_snapshot([fixture], snapshot)
    except BaseException as capture_error:
        capture_failure = _failure(capture_error)
        record["actual"] = _actual_outcome(capture_failure)
        record["capture"] = capture_failure
        record["diagnostics"] = capture_failure["diagnostics"]
        record["exception"] = capture_failure["exception"]
        record["no_artifact"] = not snapshot.exists()
        record["unexpected_live_success"] = True
        return record

    snapshot.chmod(0o444)
    moved = candidate_dir / "relocated" / snapshot.name
    moved.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(snapshot, moved)
    moved.chmod(0o444)

    in_place_context = build_pipeline_context_from_snapshot(snapshot)
    relocated_context = build_pipeline_context_from_snapshot(moved)
    graph = load_snapshot(snapshot)
    moved_graph = load_snapshot(moved)
    document = json.loads(snapshot.read_bytes())
    fingerprints = {
        "capture": document["instance_graph"]["fingerprint"],
        "in_place": document["instance_graph"]["fingerprint"],
        "relocated": json.loads(moved.read_bytes())["instance_graph"]["fingerprint"],
    }
    digests = {
        "live": _projected_digest(live_context.computation_graph),
        "in_place": _projected_digest(in_place_context.computation_graph),
        "relocated": _projected_digest(relocated_context.computation_graph),
    }
    record.update(
        {
            "actual": "v6",
            "artifact": str(snapshot.relative_to(candidate_dir)),
            "relocated_artifact": str(moved.relative_to(candidate_dir)),
            "diagnostics": {},
            "route_equality": len(set(fingerprints.values())) == 1
            and len(set(digests.values())) == 1,
            "fingerprints": fingerprints,
            "projected_digests": digests,
            "graph_counts": _graph_counts(graph),
            "relocated_graph_counts": _graph_counts(moved_graph),
            "envelope_bytes": snapshot.stat().st_size,
            "envelope_sha256": _file_sha256(snapshot),
            "normalized_envelope_sha256": _normalized_envelope_digest(snapshot),
            "source_count": len(document["sources"]["files"]),
        }
    )
    return record


def run_candidate_batch(candidate_dir: Path = CANDIDATE_DIR) -> dict[str, object]:
    """Run all and only the approved B37 rows under a fresh one-shot directory."""
    candidate_dir.mkdir(mode=0o700)
    manifest = load_approved_manifest()
    start = {
        "started_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "manifest_sha256": _file_sha256(CENSUS),
        "rows": [row.id for row in manifest],
        "one_shot": True,
    }
    _write_json(candidate_dir / "batch-start.json", start)
    environment = _environment()
    _write_json(candidate_dir / "environment.json", environment)
    _write_json(
        candidate_dir / "approved-manifest.json",
        [
            {
                "id": row.id,
                "fixture": row.fixture,
                "outcome": row.outcome,
                "diagnostics": dict(row.diagnostics),
                "classification": row.classification,
                "required": row.required,
                "governing_contract": row.governing_contract,
            }
            for row in manifest
        ],
    )

    rows = [_run_row(row, candidate_dir) for row in manifest]
    counts = dict(Counter(str(row["actual"]) for row in rows))
    classified = [
        row["id"]
        for row, approved in zip(rows, manifest, strict=True)
        if row["actual"] == approved.outcome
        and row.get("diagnostics", {}) == dict(approved.diagnostics)
    ]
    unclassified = [row["id"] for row in rows if row["id"] not in classified]
    candidate: dict[str, object] = {
        "schema": "elaborator-cutover-accepted-batch/v1",
        "status": "pending-owner-acceptance",
        "candidate_id": "__PENDING_PHASE9__",
        "rows": rows,
        "counts": counts,
        "semantic_diffs": {
            "classified": classified,
            "unclassified": unclassified,
        },
        "v5_artifacts": [],
        "environment": "environment.json",
        "completed_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
    }
    validation_error: str | None = None
    try:
        validate_candidate_record(candidate, manifest)
    except ValueError as error:
        validation_error = str(error)
        candidate["batch_result"] = "failed"
        candidate["validation_error"] = validation_error
    else:
        candidate["batch_result"] = "passed"

    _write_json(candidate_dir / "normalized-diffs.json", candidate["semantic_diffs"])
    _write_json(candidate_dir / "accepted-batch.json", candidate)
    if validation_error is not None:
        raise RuntimeError(validation_error)
    return candidate


def main() -> int:
    try:
        candidate = run_candidate_batch()
    except (FileExistsError, RuntimeError, ValueError) as error:
        print(f"candidate batch failed: {error}", file=sys.stderr)
        return 1
    print(
        json.dumps(
            {
                "candidate_dir": str(CANDIDATE_DIR),
                "counts": candidate["counts"],
                "result": candidate["batch_result"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
