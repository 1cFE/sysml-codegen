#!/usr/bin/env python3
"""Generate and compare the deterministic Item-7 two-repository cutover inventory."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

POLICY_START = "<!-- cutover-inventory-policy:v1\n"
POLICY_END = "\n-->"
POLICY_SCHEMA = "cutover-inventory-policy/v1"
INVENTORY_SCHEMA = "cutover-inventory/v1"
ROW_FIELDS = (
    "id",
    "repo",
    "path",
    "kind",
    "symbol_or_command",
    "responsibility_id",
    "status",
    "current_owner",
    "disposition",
    "final_owner",
    "replacement_test",
    "residue_gate",
)
DERIVED_FIELDS = ("sha256", "size_bytes", "worktree_state")
SKIP_PREFIXES = (".git/", ".project/", ".venv/", ".orchestrate-logs/")


class CensusError(ValueError):
    pass


def _canonical(value: object) -> bytes:
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n"
    ).encode()


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _run(repo: Path, *argv: str) -> bytes:
    result = subprocess.run(
        ["git", "-C", str(repo), *argv],
        check=False,
        capture_output=True,
    )
    if result.returncode != 0:
        raise CensusError(result.stderr.decode(errors="replace").strip())
    return result.stdout


def _parse_repo(values: list[str]) -> dict[str, Path]:
    repos: dict[str, Path] = {}
    for value in values:
        if "=" not in value:
            raise CensusError(f"invalid --repo {value!r}; expected NAME=PATH")
        name, raw_path = value.split("=", 1)
        path = Path(raw_path).resolve()
        if not name or name in repos or not path.is_dir():
            raise CensusError(f"invalid or duplicate repository mapping {value!r}")
        repos[name] = path
    if set(repos) != {"codegen", "agentic"}:
        raise CensusError("repository mappings must be exactly codegen and agentic")
    return repos


def _load_policy(path: Path) -> dict[str, Any]:
    text = path.read_text()
    start = text.find(POLICY_START)
    if start < 0:
        raise CensusError("census has no cutover inventory policy block")
    start += len(POLICY_START)
    end = text.find(POLICY_END, start)
    if end < 0:
        raise CensusError("census inventory policy block is unterminated")
    try:
        policy = json.loads(text[start:end])
    except json.JSONDecodeError as error:
        raise CensusError(f"invalid census inventory policy JSON: {error}") from error
    if policy.get("schema") != POLICY_SCHEMA:
        raise CensusError(f"unsupported policy schema {policy.get('schema')!r}")
    if set(policy) != {"schema", "markers", "rows"}:
        raise CensusError("policy keys must be exactly schema, markers, rows")
    return policy


def _validate_policy(policy: dict[str, Any], repos: set[str]) -> list[dict[str, str]]:
    markers = policy["markers"]
    if not isinstance(markers, list) or not all(
        isinstance(item, list) and item and all(isinstance(value, int) for value in item)
        for item in markers
    ):
        raise CensusError("policy markers must be nonempty Unicode-code-point arrays")
    rows = policy["rows"]
    if not isinstance(rows, list):
        raise CensusError("policy rows must be an array")
    seen_ids: set[str] = set()
    seen_keys: set[tuple[str, str, str, str]] = set()
    normalized: list[dict[str, str]] = []
    for index, raw in enumerate(rows):
        if not isinstance(raw, dict) or set(raw) != set(ROW_FIELDS):
            raise CensusError(f"policy row {index} has wrong keys")
        row = {field: raw[field] for field in ROW_FIELDS}
        if not all(isinstance(value, str) and value for value in row.values()):
            raise CensusError(f"policy row {index} has an empty/non-string value")
        if row["repo"] not in repos and row["repo"] != "coordination":
            raise CensusError(f"policy row {index} names unknown repository")
        if row["status"] not in {"existing", "planned", "runtime"}:
            raise CensusError(f"policy row {index} has invalid status")
        if row["disposition"] not in {"delete", "migrate", "retain"}:
            raise CensusError(f"policy row {index} has invalid disposition")
        key = (row["repo"], row["path"], row["symbol_or_command"], row["responsibility_id"])
        if row["id"] in seen_ids or key in seen_keys:
            raise CensusError(f"duplicate policy row {row['id']!r} or key {key!r}")
        seen_ids.add(row["id"])
        seen_keys.add(key)
        normalized.append(row)
    return sorted(
        normalized,
        key=lambda row: (
            row["repo"],
            row["path"],
            row["symbol_or_command"],
            row["responsibility_id"],
        ),
    )


def _worktree_paths(repo: Path) -> list[str]:
    payload = _run(repo, "ls-files", "--cached", "--others", "--exclude-standard", "-z")
    return sorted(item.decode() for item in payload.split(b"\0") if item)


def _discover(repo: Path, paths: list[str], markers: list[str]) -> set[str]:
    found: set[str] = set()
    for relative in paths:
        if relative.startswith(SKIP_PREFIXES):
            continue
        path = repo / relative
        if not path.is_file() or path.stat().st_size > 4_000_000:
            continue
        try:
            text = path.read_text()
        except (OSError, UnicodeDecodeError):
            continue
        if any(marker in text for marker in markers):
            found.add(relative)
    return found


def _repository_state(repo: Path) -> dict[str, object]:
    status = _run(repo, "status", "--porcelain=v1", "-z", "--untracked-files=all")
    dirty = bool(status)
    return {
        "path": str(repo),
        "head": _run(repo, "rev-parse", "HEAD").decode().strip(),
        "dirty": dirty,
        "dirty_state_sha256": _sha256(status),
        "comparison_basis": "current-worktree" if dirty else "head",
        "exact_base_comparison": not dirty,
    }


def _materialize_row(
    row: dict[str, str],
    repos: dict[str, Path],
    departed_paths: set[tuple[str, str]],
) -> dict[str, object]:
    result: dict[str, object] = dict(row)
    if row["status"] == "existing":
        if row["repo"] not in repos:
            raise CensusError(f"existing row {row['id']} must name a repository")
        path = repos[row["repo"]] / row["path"]
        if not path.is_file() and (row["repo"], row["path"]) in departed_paths:
            result.update(sha256=None, size_bytes=None, worktree_state="deleted")
            return result
        if not path.is_file():
            raise CensusError(f"existing row {row['id']} path is absent: {path}")
        payload = path.read_bytes()
        result.update(
            sha256=_sha256(payload),
            size_bytes=len(payload),
            worktree_state="present",
        )
    else:
        result.update(sha256=None, size_bytes=None, worktree_state=row["status"])
    return result


def _inventory(census: Path, repos: dict[str, Path], write: Path) -> None:
    policy = _load_policy(census)
    rows = _validate_policy(policy, set(repos))
    paths_by_repo = {name: _worktree_paths(repo) for name, repo in repos.items()}
    markers = ["".join(chr(value) for value in item) for item in policy["markers"]]
    policy_existing = {(row["repo"], row["path"]) for row in rows if row["status"] == "existing"}
    discovered = {
        (name, relative)
        for name, repo in repos.items()
        for relative in _discover(repo, paths_by_repo[name], markers)
    }
    missing = sorted(discovered - policy_existing)
    if missing:
        rendered = ", ".join(f"{repo}:{path}" for repo, path in missing)
        raise CensusError(f"uncensused affected path(s): {rendered}")
    dispositions_by_path: dict[tuple[str, str], set[str]] = {}
    for row in rows:
        if row["status"] == "existing":
            dispositions_by_path.setdefault((row["repo"], row["path"]), set()).add(
                row["disposition"]
            )
    departed_paths = {
        key
        for key, dispositions in dispositions_by_path.items()
        if dispositions <= {"delete", "migrate"}
    }
    materialized = [_materialize_row(row, repos, departed_paths) for row in rows]
    document = {
        "schema": INVENTORY_SCHEMA,
        "generated_from": {
            "census_path": str(census.resolve()),
            "census_sha256": _sha256(census.read_bytes()),
            "policy_sha256": _sha256(_canonical(policy)),
            "enumeration": "git-ls-files-cached-plus-untracked/v1",
            "affected_scan": "unicode-marker-substring/v1",
            "discovered_affected_paths": len(discovered),
        },
        "repositories": {name: _repository_state(repo) for name, repo in sorted(repos.items())},
        "rows": materialized,
    }
    write.parent.mkdir(parents=True, exist_ok=True)
    write.write_bytes(
        json.dumps(document, sort_keys=True, indent=2, ensure_ascii=True).encode() + b"\n"
    )
    print(
        json.dumps(
            {"rows": len(materialized), "discovered": len(discovered), "write": str(write)},
            sort_keys=True,
        )
    )


def _compare(
    census: Path, inventory_path: Path, require_sorted: bool, require_closed: bool
) -> None:
    policy = _load_policy(census)
    policy_rows = _validate_policy(policy, {"codegen", "agentic"})
    inventory = json.loads(inventory_path.read_text())
    if inventory.get("schema") != INVENTORY_SCHEMA or not isinstance(inventory.get("rows"), list):
        raise CensusError("invalid inventory schema")
    generated_from = inventory.get("generated_from")
    if not isinstance(generated_from, dict) or generated_from.get("census_sha256") != _sha256(
        census.read_bytes()
    ):
        raise CensusError("inventory was not generated from the current census bytes")
    if generated_from.get("policy_sha256") != _sha256(_canonical(policy)):
        raise CensusError("inventory policy digest does not match the current census policy")
    rows = inventory["rows"]
    expected_row_fields = set(ROW_FIELDS) | set(DERIVED_FIELDS)
    if any(not isinstance(row, dict) or set(row) != expected_row_fields for row in rows):
        raise CensusError("inventory row has wrong keys")
    keys = [
        (
            row.get("repo"),
            row.get("path"),
            row.get("symbol_or_command"),
            row.get("responsibility_id"),
        )
        for row in rows
    ]
    if require_sorted and keys != sorted(keys):
        raise CensusError("inventory rows are not sorted")
    if len(keys) != len(set(keys)) or len({row.get("id") for row in rows}) != len(rows):
        raise CensusError("inventory IDs or stable keys are not unique")
    stripped = [{field: row.get(field) for field in ROW_FIELDS} for row in rows]
    if stripped != policy_rows:
        raise CensusError("inventory/census exact-set mismatch")
    if require_closed:
        bad = [
            row["id"]
            for row in stripped
            if row["status"] not in {"existing", "planned", "runtime"}
            or row["disposition"] not in {"delete", "migrate", "retain"}
            or any(
                token in json.dumps(row).upper() for token in ("TBD", "TOBEDECIDED", "PLACEHOLDER")
            )
        ]
        if bad:
            raise CensusError(f"inventory has unresolved rows: {bad}")
    print(json.dumps({"rows": len(rows), "sorted": True, "closed": True}, sort_keys=True))


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    inventory = subparsers.add_parser("inventory")
    inventory.add_argument("--census", type=Path, required=True)
    inventory.add_argument("--repo", action="append", default=[], required=True)
    inventory.add_argument("--write", type=Path, required=True)
    compare = subparsers.add_parser("compare")
    compare.add_argument("--census", type=Path, required=True)
    compare.add_argument("--inventory", type=Path, required=True)
    compare.add_argument("--require-sorted", action="store_true")
    compare.add_argument("--require-closed", action="store_true")
    return parser


def main() -> int:
    args = _parser().parse_args()
    try:
        if args.command == "inventory":
            _inventory(args.census, _parse_repo(args.repo), args.write)
        else:
            _compare(args.census, args.inventory, args.require_sorted, args.require_closed)
    except (CensusError, OSError, json.JSONDecodeError) as error:
        print(str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
