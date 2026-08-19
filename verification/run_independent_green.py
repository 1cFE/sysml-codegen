#!/usr/bin/env python3
"""Run the closed artifact test battery and stage the six evidence-only files."""

from __future__ import annotations

import argparse
import email
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tomllib
import urllib.parse
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from typing import Any

from verification.build_artifacts import REPOSITORY_NAMES

RUN_SCHEMA_VERSION = "stop-parser-independent-green/v1"
COUNT_FIELDS = (
    "collected",
    "selected",
    "passed",
    "failed",
    "errors",
    "skipped",
    "xfailed",
    "deselected",
)
REQUIRED_RUN_IDS = (
    "agentic-focused",
    "agentic-fast",
    "agentic-strict",
    "agentic-mypy-baseline",
    "agentic-ruff-baseline",
    "costingfe-pytest",
    "costingfe-ruff",
    "teax-pytest",
    "codegen-strict",
    "codegen-mypy-baseline",
    "codegen-default",
    "codegen-live-snapshot",
    "codegen-generated-package",
    "codegen-execution",
    "fusion-lock-check",
    "fusion-pytest",
    "fusion-models-primary",
    "fusion-models-exploration",
    "fusion-generated-execution",
    "fusion-ruff",
    "fusion-mypy",
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
    outcomes = (
        counts["passed"]
        + counts["failed"]
        + counts["errors"]
        + counts["skipped"]
        + counts["xfailed"]
    )
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
    policies = record.get("skip_policies", [])
    if not isinstance(policies, list):
        raise IndependentRunError(f"{run_id}: skip policies must be a list")
    for policy in policies:
        if not isinstance(policy, dict) or set(policy) != {"node_id", "reason"}:
            raise IndependentRunError(f"{run_id}: skip policy is malformed")
        if not all(isinstance(value, str) for value in policy.values()):
            raise IndependentRunError(f"{run_id}: skip policy patterns must be strings")
    if run_id in EXPECTED_RUNS:
        committed_policies = _skip_policies(str(run_id))
        if policies != committed_policies:
            raise IndependentRunError(f"{run_id}: skip policies differ from the committed contract")
        classified = [item for item in observed if _skip_matches(item, committed_policies)]
        if allowed != classified:
            raise IndependentRunError(f"{run_id}: allowed skips do not match committed policies")
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
    if class_name:
        parts = class_name.split(".")
        owner_start = next(
            (index for index, part in enumerate(parts) if part[:1].isupper()),
            len(parts),
        )
        module_path = parts[:owner_start]
        owner = parts[owner_start:]
        if module_path:
            return "::".join(["/".join(module_path) + ".py", *owner, name])
    return "::".join(part for part in (class_name, name) if part)


def _junit_counts(path: Path, output: str) -> tuple[dict[str, int], list[dict[str, str]]]:
    root = _junit_root(path)
    cases = _testcases(root)
    failed = _integer_attribute(root, "failures")
    errors = _integer_attribute(root, "errors")
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
    passed = selected - failed - errors - skipped - xfailed
    deselected_matches = re.findall(r"(?:^|\s)(\d+) deselected(?:,|\s|$)", output)
    deselected = int(deselected_matches[-1]) if deselected_matches else 0
    return (
        {
            "collected": selected + deselected,
            "selected": selected,
            "passed": passed,
            "failed": failed,
            "errors": errors,
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
        [executable, "-c", probe, json.dumps(modules)],
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


def _skip_matches(item: dict[str, str], policies: list[dict[str, str]]) -> bool:
    return any(
        re.fullmatch(policy["node_id"], item["node_id"]) is not None
        and re.fullmatch(policy["reason"], item["reason"]) is not None
        for policy in policies
    )


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
    tool_paths = [str(Path(str(run.get("python") or command[0])).parent)]
    uv = shutil.which("uv")
    if uv is not None:
        tool_paths.append(str(Path(uv).parent))
    environment["PATH"] = os.pathsep.join((*tool_paths, os.defpath))
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
    normalized_output = (result.stdout + "\n" + result.stderr).replace(
        str(artifact_root.resolve()), "<ARTIFACT_ROOT>"
    )
    output_hash = hashlib.sha256(normalized_output.encode()).hexdigest()
    if is_pytest:
        counts, observed = _junit_counts(junit, result.stdout + "\n" + result.stderr)
    else:
        counts = {
            "collected": 0,
            "selected": 0,
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "skipped": 0,
            "xfailed": 0,
            "deselected": 0,
        }
        observed = []
    policies = run.get("skip_policies", [])
    allowed = [item for item in observed if _skip_matches(item, policies)]
    unexpected = [item for item in observed if item not in allowed]
    imports = _import_files(run, environment)
    import_probe_bytes = _canonical_json(imports).encode()
    import_probe_path = report_root / f"{run_id}.imports.json"
    import_probe_path.write_bytes(import_probe_bytes)
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
        "stdout": {
            "path": str((report_root / f"{run_id}.stdout").relative_to(artifact_root)),
            "sha256": _sha256(report_root / f"{run_id}.stdout"),
        },
        "stderr": {
            "path": str((report_root / f"{run_id}.stderr").relative_to(artifact_root)),
            "sha256": _sha256(report_root / f"{run_id}.stderr"),
        },
        "import_probe": {
            "path": str(import_probe_path.relative_to(artifact_root)),
            "sha256": _sha256(import_probe_path),
        },
        "skip_policies": policies,
        "allowed_skips": allowed,
        "observed_skips": observed,
        "unexpected_skips": unexpected,
        "import_roots": [str(Path(value).resolve()) for value in run.get("import_roots", [])],
        "import_files": imports,
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


ZERO_COUNTS = {field: 0 for field in COUNT_FIELDS}
EXPECTED_RUNS: dict[str, dict[str, Any]] = {
    "agentic-focused": {
        "status": 0,
        "counts": {
            "collected": 841,
            "selected": 841,
            "passed": 840,
            "failed": 0,
            "errors": 0,
            "skipped": 1,
            "xfailed": 0,
            "deselected": 0,
        },
    },
    "agentic-fast": {
        "status": 1,
        "counts": {
            "collected": 1923,
            "selected": 1918,
            "passed": 1899,
            "failed": 18,
            "errors": 0,
            "skipped": 1,
            "xfailed": 0,
            "deselected": 5,
        },
        "output_sha256": "0" * 64,
    },
    "agentic-strict": {"status": 0, "counts": ZERO_COUNTS},
    "agentic-mypy-baseline": {
        "status": 1,
        "counts": ZERO_COUNTS,
        "output_sha256": "0" * 64,
    },
    "agentic-ruff-baseline": {
        "status": 1,
        "counts": ZERO_COUNTS,
        "output_sha256": "0" * 64,
    },
    "costingfe-pytest": {
        "status": 0,
        "counts": {
            "collected": 660,
            "selected": 660,
            "passed": 602,
            "failed": 0,
            "errors": 0,
            "skipped": 58,
            "xfailed": 0,
            "deselected": 0,
        },
    },
    "costingfe-ruff": {"status": 0, "counts": ZERO_COUNTS},
    "teax-pytest": {
        "status": 0,
        "counts": {
            "collected": 406,
            "selected": 406,
            "passed": 406,
            "failed": 0,
            "errors": 0,
            "skipped": 0,
            "xfailed": 0,
            "deselected": 0,
        },
    },
    "codegen-strict": {"status": 0, "counts": ZERO_COUNTS},
    "codegen-mypy-baseline": {
        "status": 1,
        "counts": ZERO_COUNTS,
        "output_sha256": "0" * 64,
    },
    "codegen-default": {
        "status": 0,
        "counts": {
            "collected": 2625,
            "selected": 2531,
            "passed": 2497,
            "failed": 0,
            "errors": 0,
            "skipped": 34,
            "xfailed": 0,
            "deselected": 94,
        },
    },
    "codegen-live-snapshot": {
        "status": 0,
        "counts": {
            "collected": 4,
            "selected": 4,
            "passed": 4,
            "failed": 0,
            "errors": 0,
            "skipped": 0,
            "xfailed": 0,
            "deselected": 0,
        },
    },
    "codegen-generated-package": {
        "status": 0,
        "counts": {
            "collected": 25,
            "selected": 25,
            "passed": 25,
            "failed": 0,
            "errors": 0,
            "skipped": 0,
            "xfailed": 0,
            "deselected": 0,
        },
    },
    "codegen-execution": {
        "status": 0,
        "counts": {
            "collected": 94,
            "selected": 94,
            "passed": 94,
            "failed": 0,
            "errors": 0,
            "skipped": 0,
            "xfailed": 0,
            "deselected": 0,
        },
    },
    "fusion-lock-check": {"status": 0, "counts": ZERO_COUNTS},
    "fusion-pytest": {
        "status": 1,
        "counts": {
            "collected": 517,
            "selected": 517,
            "passed": 401,
            "failed": 58,
            "errors": 0,
            "skipped": 58,
            "xfailed": 0,
            "deselected": 0,
        },
        "output_sha256": "0" * 64,
    },
    "fusion-models-primary": {
        "status": 1,
        "counts": ZERO_COUNTS,
        "output_sha256": "0" * 64,
    },
    "fusion-models-exploration": {
        "status": 1,
        "counts": ZERO_COUNTS,
        "output_sha256": "0" * 64,
    },
    "fusion-generated-execution": {
        "status": 0,
        "counts": {
            "collected": 23,
            "selected": 23,
            "passed": 23,
            "failed": 0,
            "errors": 0,
            "skipped": 0,
            "xfailed": 0,
            "deselected": 0,
        },
    },
    "fusion-ruff": {"status": 0, "counts": ZERO_COUNTS},
    "fusion-mypy": {"status": 0, "counts": ZERO_COUNTS},
}


def _run_checked(command: list[str], *, cwd: Path | None = None) -> str:
    environment = os.environ.copy()
    environment["PYTHONPATH"] = ""
    result = subprocess.run(
        command,
        cwd=cwd,
        env=environment,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise IndependentRunError(
            f"preparation command failed ({' '.join(command)}): "
            f"{detail or result.returncode}"
        )
    return result.stdout.strip()


def _input_root(artifact_root: Path, inputs: dict[str, Any], name: str) -> Path:
    return _artifact_member(
        artifact_root,
        inputs[name].get("extracted_root", ""),
        label=f"{name} extracted root",
        directory=True,
    )


def _input_artifact(
    artifact_root: Path, inputs: dict[str, Any], name: str, kind: str
) -> Path:
    record = inputs[name].get(kind)
    if not isinstance(record, dict):
        raise IndependentRunError(f"{name} omits its {kind} record")
    relative = record.get("filename")
    if kind == "wheel":
        relative = f"wheels/{relative}"
    return _artifact_member(
        artifact_root, relative, label=f"{name} {kind}"
    )


def _wheel_identity(path: Path) -> tuple[str, str]:
    try:
        with zipfile.ZipFile(path) as archive:
            names = [
                name
                for name in archive.namelist()
                if name.endswith(".dist-info/METADATA") and name.count("/") == 1
            ]
            if len(names) != 1:
                raise IndependentRunError(
                    f"wheel has {len(names)} top-level METADATA files: {path}"
                )
            message = email.message_from_bytes(archive.read(names[0]))
    except (OSError, zipfile.BadZipFile) as error:
        raise IndependentRunError(f"cannot inspect wheel {path}: {error}") from error
    name = message.get("Name")
    version = message.get("Version")
    if not name or not version:
        raise IndependentRunError(f"wheel metadata omits Name or Version: {path}")
    return name, version


def _teax_pyarrow_requirement(teax: Path) -> str:
    lock_path = teax / "uv.lock"
    try:
        with lock_path.open("rb") as stream:
            lock = tomllib.load(stream)
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise IndependentRunError(f"cannot read frozen TEAx lock {lock_path}: {error}") from error
    packages = lock.get("package")
    if not isinstance(packages, list):
        raise IndependentRunError("frozen TEAx lock omits its package inventory")
    rows = [row for row in packages if isinstance(row, dict) and row.get("name") == "pyarrow"]
    if len(rows) != 1:
        raise IndependentRunError(f"frozen TEAx lock has {len(rows)} pyarrow rows")
    wheels = rows[0].get("wheels")
    if not isinstance(wheels, list):
        raise IndependentRunError("frozen TEAx pyarrow row omits wheels")
    suffix = "cp312-cp312-manylinux_2_28_x86_64.whl"
    candidates = [
        wheel
        for wheel in wheels
        if isinstance(wheel, dict)
        and str(wheel.get("url", "")).endswith(suffix)
        and re.fullmatch(r"sha256:[0-9a-f]{64}", str(wheel.get("hash", "")))
    ]
    if len(candidates) != 1:
        raise IndependentRunError(
            f"frozen TEAx lock has {len(candidates)} CPython 3.12 Linux pyarrow wheels"
        )
    wheel = candidates[0]
    url = str(wheel["url"])
    digest = str(wheel["hash"]).removeprefix("sha256:")
    filename = Path(urllib.parse.urlparse(url).path).name
    if not filename.endswith(suffix):
        raise IndependentRunError("frozen TEAx pyarrow URL has an invalid filename")
    return f"pyarrow @ {url}#sha256={digest}"


def _write_wheelhouse_requirements(wheelhouse: Path, destination: Path) -> dict[str, str]:
    rows: list[tuple[str, str, str, str]] = []
    inventory: dict[str, str] = {}
    for wheel in sorted(wheelhouse.glob("*.whl")):
        name, version = _wheel_identity(wheel)
        digest = _sha256(wheel)
        rows.append((name.lower().replace("_", "-"), version, digest, wheel.name))
        inventory[wheel.name] = digest
    if not rows:
        raise IndependentRunError("wheelhouse download produced no wheels")
    normalized = [name for name, _version, _digest, _filename in rows]
    if len(normalized) != len(set(normalized)):
        raise IndependentRunError("wheelhouse contains multiple versions of one distribution")
    destination.write_text(
        "# Generated by verification/run_independent_green.py from retained wheel bytes.\n"
        + "".join(
            f"{name}=={version} --hash=sha256:{digest}  # {filename}\n"
            for name, version, digest, filename in rows
        )
    )
    return dict(sorted(inventory.items()))


def _prepare_environment(
    artifact_root: Path,
    evidence_output: Path,
    inputs: dict[str, Any],
) -> dict[str, Any]:
    uv = shutil.which("uv")
    if uv is None:
        raise IndependentRunError("uv is required to prepare the isolated environment")
    private = artifact_root / "runner-private"
    private.mkdir(exist_ok=False)
    wheelhouse = private / "wheelhouse"
    wheelhouse.mkdir()
    venv = private / "isolated-venv"
    requirements = evidence_output / "wheelhouse-requirements.txt"

    agentic_wheel = _input_artifact(artifact_root, inputs, "agentic", "wheel")
    codegen_wheel = _input_artifact(artifact_root, inputs, "codegen", "wheel")
    costingfe_wheel = _input_artifact(artifact_root, inputs, "costingfe", "wheel")
    agentic_uri = (
        f"{agentic_wheel.as_uri()}#sha256={inputs['agentic']['wheel']['sha256']}"
    )
    codegen_uri = (
        f"{codegen_wheel.as_uri()}#sha256={inputs['codegen']['wheel']['sha256']}"
    )
    costingfe_uri = (
        f"{costingfe_wheel.as_uri()}#sha256={inputs['costingfe']['wheel']['sha256']}"
    )
    teax = _input_root(artifact_root, inputs, "teax")
    local_wheels = [
        f"agentic-mbse[extract-full,web] @ {agentic_uri}",
        codegen_uri,
        costingfe_uri,
        _teax_pyarrow_requirement(teax),
    ]
    fusion = _input_root(artifact_root, inputs, "fusion")
    exported = private / "fusion-locked-requirements.txt"
    _run_checked(
        [
            uv,
            "export",
            "--frozen",
            "--no-emit-project",
            "--no-emit-package",
            "agentic-mbse",
            "--no-emit-package",
            "sysml-codegen",
            "--no-emit-package",
            "1costingfe",
            "--output-file",
            str(exported),
        ],
        cwd=fusion,
    )
    _run_checked(
        [
            uv,
            "run",
            "--with",
            "pip",
            "--no-project",
            "python",
            "-m",
            "pip",
            "wheel",
            "--wheel-dir",
            str(wheelhouse),
            "--extra-index-url",
            "https://gitlab.com/api/v4/projects/69960816/packages/pypi/simple",
            "--requirement",
            str(exported),
            *local_wheels,
        ]
    )
    inventory = _write_wheelhouse_requirements(wheelhouse, requirements)
    _run_checked([uv, "venv", "--python", "3.12", str(venv)])
    python = venv / "bin/python"
    _run_checked(
        [
            uv,
            "pip",
            "sync",
            "--python",
            str(python),
            "--no-index",
            "--find-links",
            str(wheelhouse),
            "--require-hashes",
            str(requirements),
        ]
    )
    site_packages_text = _run_checked(
        [
            str(python),
            "-c",
            "import sysconfig; print(sysconfig.get_paths()['purelib'])",
        ]
    )
    site_packages = Path(site_packages_text).resolve()
    freeze = _run_checked([uv, "pip", "freeze", "--python", str(python)])
    versions = json.loads(
        _run_checked(
            [
                str(python),
                "-c",
                (
                    "import importlib.metadata as m,json,platform; "
                    "print(json.dumps({'python':platform.python_version(),"
                    "'syside':m.version('syside'),'agentic-mbse':m.version('agentic-mbse'),"
                    "'sysml-codegen':m.version('sysml-codegen'),"
                    "'1costingfe':m.version('1costingfe')}))"
                ),
            ]
        )
    )
    return {
        "uv": uv,
        "python": python,
        "bin": venv / "bin",
        "site_packages": site_packages,
        "wheelhouse": wheelhouse,
        "wheelhouse_inventory": inventory,
        "requirements": requirements,
        "freeze": freeze.splitlines(),
        "versions": versions,
        "wheels": {
            "agentic": agentic_wheel,
            "codegen": codegen_wheel,
            "costingfe": costingfe_wheel,
        },
    }


def _execution_provenance(
    artifact_root: Path,
    inputs: dict[str, Any],
    prepared: dict[str, Any],
) -> dict[str, Any]:
    codegen_root = _input_root(artifact_root, inputs, "codegen")
    teax_root = _input_root(artifact_root, inputs, "teax")
    codegen_archive = _input_artifact(artifact_root, inputs, "codegen", "archive")
    teax_archive = _input_artifact(artifact_root, inputs, "teax", "archive")
    agentic_wheel = prepared["wheels"]["agentic"]
    return {
        "schema_version": "stop-parser-execution-provenance/v1",
        "artifact_root": str(artifact_root.resolve()),
        "python": {
            "executable": str(prepared["python"]),
            "version": prepared["versions"]["python"],
        },
        "roots": {
            "codegen_source": {
                "path": str((codegen_root / "src").resolve()),
                "commit": inputs["codegen"]["commit"],
                "artifact_path": str(codegen_archive),
                "archive_sha256": inputs["codegen"]["archive"]["sha256"],
            },
            "agentic_install": {
                "path": str(prepared["site_packages"]),
                "commit": inputs["agentic"]["commit"],
                "artifact_path": str(agentic_wheel),
                "wheel_sha256": inputs["agentic"]["wheel"]["sha256"],
            },
            "teax_source": {
                "path": str(teax_root),
                "commit": inputs["teax"]["commit"],
                "artifact_path": str(teax_archive),
                "archive_sha256": inputs["teax"]["archive"]["sha256"],
            },
            "teax_simkit": {
                "path": str((teax_root / "packages/teax-simkit").resolve()),
                "commit": inputs["teax"]["commit"],
                "artifact_path": str(teax_archive),
                "archive_sha256": inputs["teax"]["archive"]["sha256"],
            },
        },
        "installed_artifacts": {
            "agentic-mbse": {
                "path": str(prepared["wheels"]["agentic"]),
                "sha256": inputs["agentic"]["wheel"]["sha256"],
            },
            "sysml-codegen": {
                "path": str(prepared["wheels"]["codegen"]),
                "sha256": inputs["codegen"]["wheel"]["sha256"],
            },
            "1costingfe": {
                "path": str(prepared["wheels"]["costingfe"]),
                "sha256": inputs["costingfe"]["wheel"]["sha256"],
            },
        },
    }


def _skip_policies(run_id: str) -> list[dict[str, str]]:
    policies = {
        "agentic-focused": [
            {
                "node_id": (
                    r"tests/test_sysml/test_adr002\.py::"
                    r"test_real_model_expose_patterns_exempt"
                ),
                "reason": r"Requires fusion_modeling CATF models not in this repo",
            }
        ],
        "agentic-fast": [
            {
                "node_id": (
                    r"tests/test_sysml/test_adr002\.py::"
                    r"test_real_model_expose_patterns_exempt"
                ),
                "reason": r"Requires fusion_modeling CATF models not in this repo",
            }
        ],
        "costingfe-pytest": [
            {
                "node_id": r"tests/.*",
                "reason": r"size_from_power / optimize_lcoe / use_0d_model gated off for release",
            }
        ],
        "codegen-default": [
            {
                "node_id": r"tests/conformance/test_calc_compat_parity\.py::.*",
                "reason": r".*: no calc output expressions in the golden",
            },
            {
                "node_id": r"tests/conformance/test_computed_attribute_golden\.py::.*",
                "reason": r".*: no computed attributes in the golden",
            }
        ],
        "fusion-pytest": [
            {
                "node_id": r"tests/scoring_v2/test_spec_conformance\.py::.*",
                "reason": r"KNOWN_DRIFTS carve-out: .*",
            },
            {
                "node_id": r"tests/models/test_foundation\.py::.*",
                "reason": r"(?:types|units|materials)\.sysml not found",
            },
            {
                "node_id": (
                    r"tests/models/test_power_balance\.py::TestPowerBalanceParsing::"
                    r"test_power_balance_parses_without_errors"
                ),
                "reason": r"No power balance files found",
            },
            {
                "node_id": (
                    r"tests/models/test_example\.py::TestModelStructure::"
                    r"test_example_definition_exists"
                ),
                "reason": r"Customize this test with your actual definition names",
            },
        ],
    }
    return policies.get(run_id, [])


def _base_run(
    run_id: str,
    command: list[str],
    cwd: Path,
    artifact_root: Path,
    *,
    environment: dict[str, str],
    import_roots: list[Path],
    import_modules: list[str],
    python: Path,
) -> dict[str, Any]:
    expected = EXPECTED_RUNS[run_id]
    return {
        "id": run_id,
        "command": command,
        "cwd": str(cwd.relative_to(artifact_root)),
        "environment": environment,
        "python": str(python),
        "expected_status": expected["status"],
        "expected_counts": expected["counts"],
        "expected_output_sha256": expected.get("output_sha256"),
        "skip_policies": _skip_policies(run_id),
        "allowed_skips": [],
        "import_roots": [str(path.resolve()) for path in import_roots],
        "import_modules": import_modules,
    }


def _committed_runs(
    artifact_root: Path,
    inputs: dict[str, Any],
    prepared: dict[str, Any],
    provenance_path: Path,
) -> list[dict[str, Any]]:
    python = Path(prepared["python"])
    uv = str(prepared["uv"])
    agentic = _input_root(artifact_root, inputs, "agentic")
    codegen = _input_root(artifact_root, inputs, "codegen")
    costingfe = _input_root(artifact_root, inputs, "costingfe")
    teax = _input_root(artifact_root, inputs, "teax")
    fusion = _input_root(artifact_root, inputs, "fusion")
    site = Path(prepared["site_packages"])
    simkit = teax / "packages/teax-simkit"
    battery = teax / "packages/battery-tea-demo"
    source_manifest = artifact_root / "artifact-source-inputs.json"
    agentic_env = {"PYTHONPATH": str(agentic / "src")}
    costingfe_env = {"PYTHONPATH": str(costingfe / "src")}
    teax_env = {"PYTHONPATH": os.pathsep.join((str(simkit), str(battery)))}
    codegen_env = {
        "PYTHONPATH": str(codegen / "src"),
        "STOP_PARSER_ARTIFACT_SOURCE_INPUTS": str(source_manifest),
    }
    execution_env = codegen_env | {
        "PYTHONPATH": os.pathsep.join((str(codegen / "src"), str(simkit))),
        "CODEGEN_EXECUTION_PROVENANCE": str(provenance_path),
        "TEAX_SIMKIT_PATH": str(simkit),
    }
    fusion_env = {
        "PYTHONPATH": os.pathsep.join((str(fusion), str(simkit))),
        "STOP_PARSER_WHEEL_TARGET": str(site),
        "STOP_PARSER_AGENTIC_WHEEL": str(prepared["wheels"]["agentic"]),
        "STOP_PARSER_CODEGEN_WHEEL": str(prepared["wheels"]["codegen"]),
        "STOP_PARSER_COSTINGFE_WHEEL": str(prepared["wheels"]["costingfe"]),
        "STOP_PARSER_TEAX_ROOT": str(teax),
    }
    common = {"artifact_root": artifact_root, "python": python}
    runs = [
        _base_run(
            "agentic-focused",
            [
                str(python),
                "-m",
                "pytest",
                "tests/test_sysml",
                "tests/test_validation",
                "tests/test_errors.py",
            ],
            agentic,
            environment=agentic_env,
            import_roots=[agentic / "src"],
            import_modules=["agentic_mbse"],
            **common,
        ),
        _base_run(
            "agentic-fast",
            [str(python), "-m", "pytest", "tests", "-m", "not slow"],
            agentic,
            environment=agentic_env,
            import_roots=[agentic / "src"],
            import_modules=["agentic_mbse"],
            **common,
        ),
        _base_run(
            "agentic-strict",
            [
                str(prepared["bin"] / "mypy"),
                "--strict",
                "src/agentic_mbse/errors.py",
                "src/agentic_mbse/sysml/reference_use.py",
            ],
            agentic,
            environment=agentic_env,
            import_roots=[agentic / "src"],
            import_modules=["agentic_mbse"],
            **common,
        ),
        _base_run(
            "agentic-mypy-baseline",
            [str(prepared["bin"] / "mypy"), "src"],
            agentic,
            environment=agentic_env,
            import_roots=[agentic / "src"],
            import_modules=["agentic_mbse"],
            **common,
        ),
        _base_run(
            "agentic-ruff-baseline",
            [str(prepared["bin"] / "ruff"), "check", "src", "tests"],
            agentic,
            environment=agentic_env,
            import_roots=[agentic / "src"],
            import_modules=["agentic_mbse"],
            **common,
        ),
        _base_run(
            "costingfe-pytest",
            [str(python), "-m", "pytest", "tests"],
            costingfe,
            environment=costingfe_env,
            import_roots=[costingfe / "src"],
            import_modules=["costingfe"],
            **common,
        ),
        _base_run(
            "costingfe-ruff",
            [str(prepared["bin"] / "ruff"), "check", "src", "tests"],
            costingfe,
            environment=costingfe_env,
            import_roots=[costingfe / "src"],
            import_modules=["costingfe"],
            **common,
        ),
        _base_run(
            "teax-pytest",
            [
                str(python),
                "-m",
                "pytest",
                "packages/teax-simkit/simkit/tests",
                "packages/battery-tea-demo/battery_tea/tests",
                "-q",
            ],
            teax,
            environment=teax_env,
            import_roots=[simkit, battery],
            import_modules=["simkit", "battery_tea"],
            **common,
        ),
        _base_run(
            "codegen-strict",
            [
                str(prepared["bin"] / "mypy"),
                "--strict",
                "src/sysml_codegen/extraction/binding_source.py",
                "src/sysml_codegen/elaboration/expression_evidence.py",
            ],
            codegen,
            environment=codegen_env,
            import_roots=[codegen / "src", site],
            import_modules=["sysml_codegen", "agentic_mbse"],
            **common,
        ),
        _base_run(
            "codegen-mypy-baseline",
            [str(prepared["bin"] / "mypy"), "src"],
            codegen,
            environment=codegen_env,
            import_roots=[codegen / "src", site],
            import_modules=["sysml_codegen", "agentic_mbse"],
            **common,
        ),
        _base_run(
            "codegen-default",
            [str(python), "-m", "pytest", "tests"],
            codegen,
            environment=codegen_env,
            import_roots=[codegen / "src", site],
            import_modules=["sysml_codegen", "agentic_mbse"],
            **common,
        ),
        _base_run(
            "codegen-live-snapshot",
            [
                str(python),
                "-m",
                "pytest",
                "tests/conformance/test_exact_route_generated_package.py",
            ],
            codegen,
            environment=codegen_env,
            import_roots=[codegen / "src", site],
            import_modules=["sysml_codegen", "agentic_mbse"],
            **common,
        ),
        _base_run(
            "codegen-generated-package",
            [
                str(python),
                "-m",
                "pytest",
                "tests/conformance/test_generated_schema_importable.py",
                "tests/conformance/test_output_schema_contract.py",
            ],
            codegen,
            environment=codegen_env,
            import_roots=[codegen / "src", site],
            import_modules=["sysml_codegen", "agentic_mbse"],
            **common,
        ),
        _base_run(
            "codegen-execution",
            [str(python), "-m", "pytest", "tests/execution", "-m", "execution", "-q"],
            codegen,
            environment=execution_env,
            import_roots=[codegen / "src", site, simkit],
            import_modules=["sysml_codegen", "agentic_mbse", "simkit"],
            **common,
        ),
        _base_run(
            "fusion-lock-check",
            [uv, "lock", "--check", "--offline"],
            fusion,
            environment=fusion_env,
            import_roots=[site, simkit],
            import_modules=["agentic_mbse", "sysml_codegen", "costingfe", "simkit"],
            **common,
        ),
        _base_run(
            "fusion-pytest",
            [str(python), "-m", "pytest", "tests"],
            fusion,
            environment=fusion_env,
            import_roots=[site, simkit],
            import_modules=["agentic_mbse", "sysml_codegen", "costingfe", "simkit"],
            **common,
        ),
        _base_run(
            "fusion-models-primary",
            [str(prepared["bin"] / "agentic-mbse"), "validate", "--complete", "models"],
            fusion,
            environment=fusion_env,
            import_roots=[site],
            import_modules=["agentic_mbse"],
            **common,
        ),
        _base_run(
            "fusion-models-exploration",
            [
                str(prepared["bin"] / "agentic-mbse"),
                "validate",
                "--complete",
                "exploration/ife_e2e/models",
            ],
            fusion,
            environment=fusion_env,
            import_roots=[site],
            import_modules=["agentic_mbse"],
            **common,
        ),
        _base_run(
            "fusion-generated-execution",
            [
                str(python),
                "-m",
                "pytest",
                "tests/test_codegen_teax_acceptance.py",
                "tests/test_occurrence_mutation_teax.py",
                "tests/test_dependency_provenance.py",
            ],
            fusion,
            environment=fusion_env,
            import_roots=[site, simkit],
            import_modules=["agentic_mbse", "sysml_codegen", "costingfe", "simkit"],
            **common,
        ),
        _base_run(
            "fusion-ruff",
            [
                str(prepared["bin"] / "ruff"),
                "check",
                "tests/test_codegen_teax_acceptance.py",
                "tests/test_occurrence_mutation_teax.py",
                "tests/test_dependency_provenance.py",
            ],
            fusion,
            environment=fusion_env,
            import_roots=[site, simkit],
            import_modules=["agentic_mbse", "sysml_codegen", "costingfe", "simkit"],
            **common,
        ),
        _base_run(
            "fusion-mypy",
            [
                str(prepared["bin"] / "mypy"),
                "tests/test_codegen_teax_acceptance.py",
                "tests/test_occurrence_mutation_teax.py",
            ],
            fusion,
            environment=fusion_env,
            import_roots=[site, simkit],
            import_modules=["agentic_mbse", "sysml_codegen", "costingfe", "simkit"],
            **common,
        ),
    ]
    if tuple(run["id"] for run in runs) != REQUIRED_RUN_IDS:
        raise IndependentRunError("committed run inventory drifted from REQUIRED_RUN_IDS")
    return runs


def _reconciliation_ledger(inputs: dict[str, Any]) -> str:
    c_prod = inputs["codegen"]["commit"]
    a_final = inputs["agentic"]["commit"]
    rows = {
        "L-01": "tests/conformance/test_definition_owned_reference_positions.py",
        "L-02": "tests/conformance/test_occurrence_calc_domain_derivation.py",
        "L-03": "tests/conformance/test_expression_evidence_integrity.py",
        "L-04": "tests/conformance/test_occurrence_multiplicity_authority.py",
        "L-05": "tests/conformance/test_feature_typing_integrity.py",
        "L-06": "tests/conformance/test_expression_evidence_integrity.py",
        "L-07": "tests/conformance/test_ast_dispatch_invariant.py",
        "L-08": "tests/unit/test_expression_evidence_boundary.py",
        "L-09": "tests/conformance/test_expression_evidence_integrity.py",
        "L-10": "tests/conformance/test_expression_evidence_integrity.py",
        "L-11": "tests/conformance/test_feature_typing_integrity.py",
        "L-12": "tests/conformance/test_generation_exit_type_preflight.py",
        "L-13": "tests/conformance/test_stop_parser_documentation_contract.py",
        "L-14": "tests/conformance/test_output_schema_contract.py",
        "U-1": "tests/conformance/test_feature_typing_integrity.py",
        "U-2": "tests/unit/test_expression_evidence_boundary.py",
    }
    lines = [
        "# Stop-reinventing-the-parser reconciliation ledger",
        "",
        f"Final production identity: Codegen `{c_prod}`; Agentic `{a_final}`.",
        "The rows below name retained final tests. They do not certify unrun cases.",
        "",
        "| Row | Final proof | Production identity |",
        "|---|---|---|",
    ]
    lines.extend(f"| {row} | `{proof}` | `{c_prod}` |" for row, proof in rows.items())
    return "\n".join(lines) + "\n"


def run_battery(artifact_root: Path, evidence_output: Path) -> dict[str, object]:
    if not artifact_root.is_dir():
        raise IndependentRunError(f"artifact root does not exist: {artifact_root}")
    if (artifact_root / "run-contract.json").exists():
        raise IndependentRunError(
            "external run staging is forbidden; commands and expectations are committed"
        )
    if evidence_output.exists() and any(evidence_output.iterdir()):
        raise IndependentRunError(f"evidence output must be new and empty: {evidence_output}")
    evidence_output.mkdir(parents=True, exist_ok=True)
    build = _load_json(artifact_root / "artifact-build.json")
    if build.get("schema_version") != "stop-parser-artifact-build/v1":
        raise IndependentRunError("artifact-build.json has the wrong schema")
    inputs = build.get("inputs")
    if not isinstance(inputs, dict) or set(inputs) != set(REPOSITORY_NAMES):
        raise IndependentRunError("artifact-build.json does not contain exactly five inputs")
    prepared = _prepare_environment(artifact_root, evidence_output, inputs)
    provenance = _execution_provenance(artifact_root, inputs, prepared)
    provenance_path = evidence_output / "execution-provenance.json"
    provenance_path.write_text(_canonical_json(provenance))
    runs = _committed_runs(
        artifact_root, inputs, prepared, provenance_path
    )
    reports = artifact_root / "run-reports"
    reports.mkdir(exist_ok=False)
    records = [_run_one(run, artifact_root=artifact_root, report_root=reports) for run in runs]
    codegen_root = _input_root(artifact_root, inputs, "codegen")
    runner = codegen_root / "verification/run_independent_green.py"
    independent: dict[str, object] = {
        "schema_version": RUN_SCHEMA_VERSION,
        "input_repositories": list(REPOSITORY_NAMES),
        "artifact_build_sha256": _sha256(artifact_root / "artifact-build.json"),
        "committed_runner": {
            "path": str(runner.relative_to(artifact_root)),
            "sha256": _sha256(runner),
        },
        "runs": records,
    }
    (evidence_output / "independent-green.json").write_text(_canonical_json(independent))

    dependencies = {
        "schema_version": "stop-parser-dependencies/v1",
        "inputs": inputs,
        "python": {
            "version": prepared["versions"]["python"],
            "executable": str(prepared["python"]),
        },
        "syside": {"version": prepared["versions"]["syside"]},
        "wheelhouse": {
            "directory": str(prepared["wheelhouse"].relative_to(artifact_root)),
            "files": prepared["wheelhouse_inventory"],
            "pip_freeze": prepared["freeze"],
        },
    }
    (evidence_output / "dependencies.json").write_text(_canonical_json(dependencies))
    (evidence_output / "reconciliation-ledger.md").write_text(
        _reconciliation_ledger(inputs)
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
