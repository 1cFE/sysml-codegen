#!/usr/bin/env python3
"""Run the closed artifact test battery and stage the six evidence-only files."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from verification.build_artifacts import REPOSITORY_NAMES

RUN_SCHEMA_VERSION = "stop-parser-independent-green/v1"
CONTRACT_SCHEMA_VERSION = "stop-parser-run-contract/v1"
COUNT_FIELDS = (
    "collected",
    "selected",
    "passed",
    "failed",
    "skipped",
    "xfailed",
    "deselected",
)
EVIDENCE_SIBLINGS = (
    "dependencies.json",
    "wheelhouse-requirements.txt",
    "execution-provenance.json",
    "independent-green.json",
    "reconciliation-ledger.md",
)
PRODUCTION_LOCK_INPUTS = (
    "verification/probe-fixture-lock.json",
    "verification/expected-transitions.md",
)


class IndependentRunError(RuntimeError):
    """An isolated command, import, count, or skip violated the run contract."""


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _canonical_json(value: object) -> str:
    return json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True) + "\n"


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise IndependentRunError(f"cannot read JSON input {path}: {error}") from error
    if not isinstance(value, dict):
        raise IndependentRunError(f"JSON input must be an object: {path}")
    return value


def _artifact_member(
    artifact_root: Path, value: object, *, label: str, directory: bool = False
) -> Path:
    relative = Path(str(value))
    if relative.is_absolute() or ".." in relative.parts:
        raise IndependentRunError(f"{label} must be artifact-root-relative")
    result = (artifact_root / relative).resolve()
    if not result.is_relative_to(artifact_root.resolve()):
        raise IndependentRunError(f"{label} escapes the artifact root")
    exists = result.is_dir() if directory else result.is_file()
    if not exists:
        kind = "directory" if directory else "file"
        raise IndependentRunError(f"{label} {kind} is missing: {result}")
    return result


def _under(path: Path, roots: list[Path]) -> bool:
    resolved = path.resolve()
    return any(resolved.is_relative_to(root.resolve()) for root in roots)


def validate_run_record(record: dict[str, Any]) -> None:
    """Require one result to carry total counts, declared skips, and closed imports."""
    run_id = record.get("id", "<unnamed>")
    command = record.get("command")
    if not isinstance(command, list) or not command or not all(
        isinstance(item, str) and item for item in command
    ):
        raise IndependentRunError(f"{run_id}: command must be a non-empty string list")
    executed = record.get("executed_command")
    if not isinstance(executed, list) or not executed or not all(
        isinstance(item, str) and item for item in executed
    ):
        raise IndependentRunError(f"{run_id}: executed command must be a non-empty string list")
    expected_status = record.get("expected_status")
    if not isinstance(expected_status, int):
        raise IndependentRunError(f"{run_id}: expected status is missing")
    if record.get("status") != expected_status:
        raise IndependentRunError(
            f"{run_id}: command status is {record.get('status')!r}, expected {expected_status}"
        )
    counts = record.get("counts")
    if not isinstance(counts, dict) or set(counts) != set(COUNT_FIELDS):
        raise IndependentRunError(f"{run_id}: count record must contain {list(COUNT_FIELDS)}")
    if any(not isinstance(counts[field], int) or counts[field] < 0 for field in COUNT_FIELDS):
        raise IndependentRunError(f"{run_id}: counts must be non-negative integers")
    if counts["collected"] != counts["selected"] + counts["deselected"]:
        raise IndependentRunError(f"{run_id}: collected count does not close")
    outcomes = counts["passed"] + counts["failed"] + counts["skipped"] + counts["xfailed"]
    if counts["selected"] != outcomes:
        raise IndependentRunError(f"{run_id}: selected count does not close")
    expected_counts = record.get("expected_counts")
    if not isinstance(expected_counts, dict) or set(expected_counts) != set(COUNT_FIELDS):
        raise IndependentRunError(f"{run_id}: expected count record is incomplete")
    if counts != expected_counts:
        raise IndependentRunError(
            f"{run_id}: measured counts {counts} differ from expected {expected_counts}"
        )
    if "pytest" in command and counts["selected"] == 0:
        raise IndependentRunError(f"{run_id}: pytest selection is vacuous")
    output_hash = record.get("output_sha256")
    if not isinstance(output_hash, str) or re.fullmatch(r"[0-9a-f]{64}", output_hash) is None:
        raise IndependentRunError(f"{run_id}: output hash is missing")
    expected_output_hash = record.get("expected_output_sha256")
    if expected_status != 0 and expected_output_hash != output_hash:
        raise IndependentRunError(
            f"{run_id}: nonzero baseline output differs from its exact declared hash"
        )
    unexpected = record.get("unexpected_skips")
    if unexpected:
        raise IndependentRunError(f"{run_id}: unexpected skip records: {unexpected}")
    allowed = record.get("allowed_skips")
    observed = record.get("observed_skips")
    if not isinstance(allowed, list) or not isinstance(observed, list):
        raise IndependentRunError(f"{run_id}: skip records must be lists")
    if observed != allowed:
        raise IndependentRunError(
            f"{run_id}: observed skip set/reasons differ from the declared allow-list"
        )
    roots_raw = record.get("import_roots")
    imports_raw = record.get("import_files")
    if not isinstance(roots_raw, list) or not roots_raw:
        raise IndependentRunError(f"{run_id}: import roots are missing")
    if not isinstance(imports_raw, list):
        raise IndependentRunError(f"{run_id}: import files are missing")
    roots = [Path(value) for value in roots_raw]
    for imported in imports_raw:
        if not _under(Path(imported), roots):
            raise IndependentRunError(
                f"{run_id}: import root violation for {imported}; allowed roots are {roots_raw}"
            )


def _junit_root(path: Path) -> ET.Element:
    try:
        root = ET.parse(path).getroot()
    except (OSError, ET.ParseError) as error:
        raise IndependentRunError(f"cannot read JUnit report {path}: {error}") from error
    if root.tag == "testsuite":
        return root
    if root.tag != "testsuites":
        raise IndependentRunError(f"unexpected JUnit root {root.tag!r}: {path}")
    return root


def _integer_attribute(root: ET.Element, name: str) -> int:
    if name in root.attrib:
        return int(root.attrib[name])
    return sum(int(suite.attrib.get(name, "0")) for suite in root.findall("testsuite"))


def _testcases(root: ET.Element) -> list[ET.Element]:
    return list(root.iter("testcase"))


def _node_id(case: ET.Element) -> str:
    file_name = case.attrib.get("file")
    name = case.attrib.get("name", "<unnamed>")
    class_name = case.attrib.get("classname", "")
    if file_name:
        module_parts = Path(file_name).with_suffix("").parts
        class_parts = class_name.split(".")
        common = 0
        for module, classified in zip(module_parts, class_parts, strict=False):
            if module != classified:
                break
            common += 1
        owner = class_parts[common:]
        return "::".join([file_name, *owner, name])
    return "::".join(part for part in (class_name, name) if part)


def _junit_counts(path: Path, output: str) -> tuple[dict[str, int], list[dict[str, str]]]:
    root = _junit_root(path)
    cases = _testcases(root)
    failed = _integer_attribute(root, "failures") + _integer_attribute(root, "errors")
    skipped = 0
    xfailed = 0
    observed: list[dict[str, str]] = []
    for case in cases:
        skip = case.find("skipped")
        if skip is None:
            continue
        reason = skip.attrib.get("message") or (skip.text or "").strip()
        row = {"node_id": _node_id(case), "reason": reason}
        if skip.attrib.get("type") == "pytest.xfail" or reason.lower().startswith("xfail"):
            xfailed += 1
        else:
            skipped += 1
            observed.append(row)
    selected = len(cases)
    passed = selected - failed - skipped - xfailed
    deselected_matches = re.findall(r"(?:^|\s)(\d+) deselected(?:,|\s|$)", output)
    deselected = int(deselected_matches[-1]) if deselected_matches else 0
    return (
        {
            "collected": selected + deselected,
            "selected": selected,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "xfailed": xfailed,
            "deselected": deselected,
        },
        observed,
    )


def _import_files(run: dict[str, Any], environment: dict[str, str]) -> list[str]:
    modules = run.get("import_modules", [])
    if not isinstance(modules, list) or not all(isinstance(item, str) for item in modules):
        raise IndependentRunError(f"{run.get('id')}: import_modules must be a string list")
    if not modules:
        supplied = run.get("import_files", [])
        if not isinstance(supplied, list) or not all(isinstance(item, str) for item in supplied):
            raise IndependentRunError(f"{run.get('id')}: import_files must be a string list")
        return supplied
    command = run["command"]
    executable = str(run.get("python") or command[0])
    probe = (
        "import importlib,json,sys; "
        "names=json.loads(sys.argv[1]); "
        "print(json.dumps([str(importlib.import_module(n).__file__) for n in names]))"
    )
    result = subprocess.run(
        [executable, "-I", "-c", probe, json.dumps(modules)],
        env=environment,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise IndependentRunError(
            f"{run.get('id')}: import probe failed: {(result.stderr or result.stdout).strip()}"
        )
    try:
        imports = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise IndependentRunError(f"{run.get('id')}: import probe emitted invalid JSON") from error
    if not isinstance(imports, list) or not all(isinstance(item, str) for item in imports):
        raise IndependentRunError(f"{run.get('id')}: import probe result is not a string list")
    return imports


def _run_one(
    run: dict[str, Any],
    *,
    artifact_root: Path,
    report_root: Path,
) -> dict[str, Any]:
    run_id = run.get("id")
    if not isinstance(run_id, str) or not run_id:
        raise IndependentRunError("run contract contains an unnamed command")
    command = run.get("command")
    if (
        not isinstance(command, list)
        or not command
        or not all(isinstance(item, str) for item in command)
    ):
        raise IndependentRunError(f"{run_id}: command must be a non-empty string list")
    cwd_relative = Path(str(run.get("cwd", ".")))
    if cwd_relative.is_absolute() or ".." in cwd_relative.parts:
        raise IndependentRunError(f"{run_id}: cwd must be artifact-root-relative")
    cwd = (artifact_root / cwd_relative).resolve()
    if not cwd.is_relative_to(artifact_root.resolve()) or not cwd.is_dir():
        raise IndependentRunError(f"{run_id}: cwd is outside or absent from the artifact root")
    environment = os.environ.copy()
    environment["PYTHONPATH"] = ""
    environment["UV_OFFLINE"] = "1"
    environment["UV_NO_SYNC"] = "1"
    additions = run.get("environment", {})
    if not isinstance(additions, dict) or not all(
        isinstance(key, str) and isinstance(value, str) for key, value in additions.items()
    ):
        raise IndependentRunError(f"{run_id}: environment must be a string map")
    environment.update(additions)

    is_pytest = "pytest" in command
    junit = report_root / f"{run_id}.xml"
    executed = list(command)
    if is_pytest:
        if "-ra" not in executed:
            executed.append("-ra")
        if not any(item.startswith("--junitxml") for item in executed):
            executed.append(f"--junitxml={junit}")
    result = subprocess.run(
        executed,
        cwd=cwd,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
    )
    (report_root / f"{run_id}.stdout").write_text(result.stdout)
    (report_root / f"{run_id}.stderr").write_text(result.stderr)
    output_hash = hashlib.sha256((result.stdout + "\n" + result.stderr).encode()).hexdigest()
    if is_pytest:
        counts, observed = _junit_counts(junit, result.stdout + "\n" + result.stderr)
    else:
        counts = {
            "collected": 0,
            "selected": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "xfailed": 0,
            "deselected": 0,
        }
        observed = []
    allowed = run.get("allowed_skips", [])
    unexpected = [item for item in observed if item not in allowed]
    record = {
        "id": run_id,
        "command": command,
        "executed_command": executed,
        "cwd": str(cwd),
        "status": result.returncode,
        "expected_status": run.get("expected_status"),
        "counts": counts,
        "expected_counts": run.get("expected_counts"),
        "output_sha256": output_hash,
        "expected_output_sha256": run.get("expected_output_sha256"),
        "allowed_skips": allowed,
        "observed_skips": observed,
        "unexpected_skips": unexpected,
        "import_roots": [str(Path(value).resolve()) for value in run.get("import_roots", [])],
        "import_files": _import_files(run, environment),
        "junit": str(junit) if is_pytest else None,
    }
    return record


def build_evidence_lock(repository: Path, staging: Path) -> dict[str, object]:
    """Hash five sibling evidence files and the two production-side lock inputs."""
    files: dict[str, str] = {}
    for name in EVIDENCE_SIBLINGS:
        path = staging / name
        if not path.is_file():
            raise IndependentRunError(f"evidence sibling is missing: {path}")
        files[f"verification/{name}"] = _sha256(path)
    for relative in PRODUCTION_LOCK_INPUTS:
        path = repository / relative
        if not path.is_file():
            raise IndependentRunError(f"production lock input is missing: {path}")
        files[relative] = _sha256(path)
    return {
        "schema_version": "stop-parser-evidence-lock/v1",
        "files": dict(sorted(files.items())),
    }


def _copy_required(source: Path, destination: Path, *, label: str) -> None:
    if not source.is_file():
        raise IndependentRunError(f"{label} is missing: {source}")
    shutil.copyfile(source, destination)


def run_battery(artifact_root: Path, evidence_output: Path) -> dict[str, object]:
    if not artifact_root.is_dir():
        raise IndependentRunError(f"artifact root does not exist: {artifact_root}")
    if evidence_output.exists() and any(evidence_output.iterdir()):
        raise IndependentRunError(f"evidence output must be new and empty: {evidence_output}")
    evidence_output.mkdir(parents=True, exist_ok=True)
    build = _load_json(artifact_root / "artifact-build.json")
    if build.get("schema_version") != "stop-parser-artifact-build/v1":
        raise IndependentRunError("artifact-build.json has the wrong schema")
    inputs = build.get("inputs")
    if not isinstance(inputs, dict) or set(inputs) != set(REPOSITORY_NAMES):
        raise IndependentRunError("artifact-build.json does not contain exactly five inputs")
    contract = _load_json(artifact_root / "run-contract.json")
    if contract.get("schema_version") != CONTRACT_SCHEMA_VERSION:
        raise IndependentRunError(f"run-contract.json schema must be {CONTRACT_SCHEMA_VERSION}")
    runs = contract.get("runs")
    if not isinstance(runs, list) or not runs:
        raise IndependentRunError("run-contract.json contains no runs")
    reports = artifact_root / "run-reports"
    reports.mkdir(exist_ok=False)
    records = [_run_one(run, artifact_root=artifact_root, report_root=reports) for run in runs]
    independent: dict[str, object] = {
        "schema_version": RUN_SCHEMA_VERSION,
        "input_repositories": list(REPOSITORY_NAMES),
        "artifact_build_sha256": _sha256(artifact_root / "artifact-build.json"),
        "runs": records,
    }
    (evidence_output / "independent-green.json").write_text(_canonical_json(independent))

    dependencies = {
        "schema_version": "stop-parser-dependencies/v1",
        "inputs": inputs,
        "python": contract.get("python"),
        "syside": contract.get("syside"),
        "wheelhouse": contract.get("wheelhouse"),
    }
    (evidence_output / "dependencies.json").write_text(_canonical_json(dependencies))
    _copy_required(
        _artifact_member(
            artifact_root,
            contract.get("wheelhouse_requirements", ""),
            label="wheelhouse requirements",
        ),
        evidence_output / "wheelhouse-requirements.txt",
        label="hash-pinned wheelhouse requirements",
    )
    provenance = contract.get("execution_provenance")
    if not isinstance(provenance, dict):
        raise IndependentRunError("run contract omits execution_provenance")
    provenance = dict(provenance, schema_version="stop-parser-execution-provenance/v1")
    (evidence_output / "execution-provenance.json").write_text(_canonical_json(provenance))
    _copy_required(
        _artifact_member(
            artifact_root,
            contract.get("reconciliation_ledger", ""),
            label="reconciliation ledger",
        ),
        evidence_output / "reconciliation-ledger.md",
        label="reconciliation ledger",
    )
    codegen_root = _artifact_member(
        artifact_root,
        contract.get("codegen_source_root", ""),
        label="codegen source root",
        directory=True,
    )
    lock = build_evidence_lock(codegen_root, evidence_output)
    (evidence_output / "evidence-lock.json").write_text(_canonical_json(lock))

    failures: list[str] = []
    for record in records:
        try:
            validate_run_record(record)
        except IndependentRunError as error:
            failures.append(str(error))
    if failures:
        raise IndependentRunError("independent battery failed:\n" + "\n".join(failures))
    return independent


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-root", required=True, type=Path)
    parser.add_argument("--evidence-output", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    run_battery(arguments.artifact_root.resolve(), arguments.evidence_output.resolve())
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except IndependentRunError as error:
        print(f"INDEPENDENT RUN REFUSED: {error}", file=sys.stderr)
        raise SystemExit(2) from error
