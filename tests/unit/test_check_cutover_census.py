from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).parents[2] / "scripts" / "check_cutover_census.py"


def _git_repo(path: Path, filename: str, content: str) -> None:
    path.mkdir()
    subprocess.run(["git", "init", "-q", str(path)], check=True)
    subprocess.run(["git", "-C", str(path), "config", "user.email", "test@example.com"], check=True)
    subprocess.run(["git", "-C", str(path), "config", "user.name", "Test"], check=True)
    (path / filename).write_text(content)
    subprocess.run(["git", "-C", str(path), "add", filename], check=True)
    subprocess.run(["git", "-C", str(path), "commit", "-qm", "base"], check=True)


def _census(path: Path, *, deleted: bool = False, migrated: bool = False) -> None:
    policy = {
        "schema": "cutover-inventory-policy/v1",
        "markers": [[80, 105, 112, 101, 108, 105, 110, 101, 67, 111, 110, 116, 101, 120, 116]],
        "rows": [
            {
                "id": "INV-001",
                "repo": "codegen",
                "path": "owner.py",
                "kind": "production",
                "symbol_or_command": "PipelineContext",
                "responsibility_id": "PROD-01",
                "status": "existing",
                "current_owner": "legacy context",
                "disposition": "migrate",
                "final_owner": "builder context",
                "replacement_test": "CUT-API-01",
                "residue_gate": "NR-06",
            },
            {
                "id": "INV-002",
                "repo": "codegen",
                "path": "scripts/planned.py",
                "kind": "script",
                "symbol_or_command": "planned",
                "responsibility_id": "SCR-01",
                "status": "planned",
                "current_owner": "none",
                "disposition": "retain",
                "final_owner": "coordinator",
                "replacement_test": "CUT-PROMO-01",
                "residue_gate": "NR-13",
            },
        ],
    }
    if deleted:
        policy["rows"].append(
            {
                "id": "INV-003",
                "repo": "codegen",
                "path": "obsolete.py",
                "kind": "production",
                "symbol_or_command": "obsolete owner",
                "responsibility_id": "PROD-02",
                "status": "existing",
                "current_owner": "legacy owner",
                "disposition": "delete",
                "final_owner": "exact owner",
                "replacement_test": "CUT-ABS-01",
                "residue_gate": "NR-13",
            }
        )
    if migrated:
        policy["rows"].append(
            {
                "id": "INV-004",
                "repo": "codegen",
                "path": "migrated.py",
                "kind": "test",
                "symbol_or_command": "old oracle",
                "responsibility_id": "TEST-01",
                "status": "existing",
                "current_owner": "old test",
                "disposition": "migrate",
                "final_owner": "independent exact test",
                "replacement_test": "CUT-PROJ-01",
                "residue_gate": "NR-13",
            }
        )
    path.write_text(
        "# Census\n\n<!-- cutover-inventory-policy:v1\n"
        + json.dumps(policy, sort_keys=True)
        + "\n-->\n"
    )


def test_inventory_is_deterministic_and_compare_is_exact(tmp_path: Path) -> None:
    codegen = tmp_path / "codegen"
    agentic = tmp_path / "agentic"
    _git_repo(codegen, "owner.py", "PipelineContext = object\n")
    _git_repo(agentic, "neutral.py", "VALUE = 1\n")
    census = tmp_path / "census.md"
    inventory = tmp_path / "inventory.json"
    _census(census)

    command = [
        sys.executable,
        str(SCRIPT),
        "inventory",
        "--census",
        str(census),
        "--repo",
        f"codegen={codegen}",
        "--repo",
        f"agentic={agentic}",
        "--write",
        str(inventory),
    ]
    subprocess.run(command, check=True)
    first = inventory.read_bytes()
    subprocess.run(command, check=True)
    assert inventory.read_bytes() == first

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "compare",
            "--census",
            str(census),
            "--inventory",
            str(inventory),
            "--require-sorted",
            "--require-closed",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr
    document = json.loads(first)
    assert [row["id"] for row in document["rows"]] == ["INV-001", "INV-002"]
    assert document["repositories"]["codegen"]["dirty"] is False


def test_inventory_refuses_uncensused_marker_path(tmp_path: Path) -> None:
    codegen = tmp_path / "codegen"
    agentic = tmp_path / "agentic"
    _git_repo(codegen, "owner.py", "PipelineContext = object\n")
    _git_repo(agentic, "neutral.py", "VALUE = 1\n")
    (codegen / "missed.py").write_text("PipelineContext = object\n")
    census = tmp_path / "census.md"
    _census(census)

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "inventory",
            "--census",
            str(census),
            "--repo",
            f"codegen={codegen}",
            "--repo",
            f"agentic={agentic}",
            "--write",
            str(tmp_path / "inventory.json"),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "uncensused affected path" in result.stderr


def test_inventory_records_an_approved_deleted_existing_path(tmp_path: Path) -> None:
    codegen = tmp_path / "codegen"
    agentic = tmp_path / "agentic"
    _git_repo(codegen, "owner.py", "PipelineContext = object\n")
    _git_repo(agentic, "neutral.py", "VALUE = 1\n")
    census = tmp_path / "census.md"
    inventory = tmp_path / "inventory.json"
    _census(census, deleted=True)

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "inventory",
            "--census",
            str(census),
            "--repo",
            f"codegen={codegen}",
            "--repo",
            f"agentic={agentic}",
            "--write",
            str(inventory),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    deleted = next(
        row
        for row in json.loads(inventory.read_text())["rows"]
        if row["id"] == "INV-003"
    )
    assert deleted["worktree_state"] == "deleted"
    assert deleted["sha256"] is None
    assert deleted["size_bytes"] is None


def test_inventory_records_an_approved_migrated_away_path(tmp_path: Path) -> None:
    codegen = tmp_path / "codegen"
    agentic = tmp_path / "agentic"
    _git_repo(codegen, "owner.py", "PipelineContext = object\n")
    _git_repo(agentic, "neutral.py", "VALUE = 1\n")
    census = tmp_path / "census.md"
    inventory = tmp_path / "inventory.json"
    _census(census, migrated=True)

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "inventory",
            "--census",
            str(census),
            "--repo",
            f"codegen={codegen}",
            "--repo",
            f"agentic={agentic}",
            "--write",
            str(inventory),
        ],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    migrated = next(
        row
        for row in json.loads(inventory.read_text())["rows"]
        if row["id"] == "INV-004"
    )
    assert migrated["worktree_state"] == "deleted"
    assert migrated["sha256"] is None
    assert migrated["size_bytes"] is None
