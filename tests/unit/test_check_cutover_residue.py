from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).parents[2] / "scripts" / "check_cutover_residue.py"


def _inventory(path: Path, repo_path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "schema": "cutover-inventory/v1",
                "repositories": {"codegen": {"path": str(repo_path)}},
                "rows": [
                    {
                        "id": "INV-001",
                        "repo": "codegen",
                        "path": "legacy.py",
                        "status": "existing",
                        "disposition": "delete",
                    }
                ],
            }
        )
    )


def test_residue_distinguishes_inventoried_from_absent(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    banned = "".join(
        chr(value) for value in (79, 117, 116, 112, 117, 116, 82, 101, 103, 105, 115, 116, 114, 121)
    )
    (repo / "legacy.py").write_text(f"{banned} = object\n")
    inventory = tmp_path / "inventory.json"
    _inventory(inventory, repo)

    base = [
        sys.executable,
        str(SCRIPT),
        "--repo",
        f"codegen={repo}",
        "--inventory",
        str(inventory),
        "--rule",
        "all",
    ]
    inventoried = subprocess.run(
        [*base, "--expect", "inventoried"], capture_output=True, text=True, check=False
    )
    assert inventoried.returncode == 0, inventoried.stderr
    absent = subprocess.run(
        [*base, "--expect", "absent"], capture_output=True, text=True, check=False
    )
    assert absent.returncode == 1
    assert "legacy.py" in absent.stderr


def test_checker_source_contains_no_plain_banned_oracle() -> None:
    source = SCRIPT.read_text()
    banned = "".join(
        chr(value) for value in (79, 117, 116, 112, 117, 116, 82, 101, 103, 105, 115, 116, 114, 121)
    )
    assert banned not in source
