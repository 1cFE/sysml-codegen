"""Write the execution-provenance manifest that binds this item's development teax lane.

This binds a development lane, not immutable evidence. The artifacts are
``git archive HEAD`` exports of the three checkouts, taken when the script runs,
while the roots it records are those same working checkouts. Uncommitted edits
in a checkout are therefore visible to the lane but absent from its artifact.
The manifest proves which commits the lane was started against, nothing more.

It writes ``/tmp/study-lane/artifacts/{codegen,agentic,teax}.tar`` and
``/tmp/study-lane/execution-provenance.json`` (schema
``stop-parser-execution-provenance/v1``, loaded by
``tests/execution/environment_pins.py``). Run it with any Python, then::

    export TEAX_SIMKIT_PATH=/home/reid/1cfe/teax/packages/teax-simkit
    export CODEGEN_EXECUTION_PROVENANCE=/tmp/study-lane/execution-provenance.json

It refuses when teax HEAD is not the revision this item was planned against.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

WORKTREE = Path(__file__).resolve().parents[5]
AGENTIC = Path("/home/reid/1cfe/agentic-mbse-study-layer")
TEAX = Path("/home/reid/1cfe/teax")
TEAX_SIMKIT = TEAX / "packages" / "teax-simkit"
TEAX_PREFIX = "8d87746"
LANE = Path("/tmp/study-lane")
ARTIFACTS = LANE / "artifacts"
MANIFEST = LANE / "execution-provenance.json"
PYTHON = WORKTREE / ".venv" / "bin" / "python"


def head(repo: Path) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        check=True, capture_output=True, text=True,
    ).stdout.strip()


def archive(repo: Path, name: str) -> tuple[Path, str]:
    target = ARTIFACTS / f"{name}.tar"
    subprocess.run(
        ["git", "-C", str(repo), "archive", "--format=tar", "-o", str(target), "HEAD"],
        check=True,
    )
    return target, hashlib.sha256(target.read_bytes()).hexdigest()


def python_version() -> str:
    return subprocess.run(
        [str(PYTHON), "-c", "import platform; print(platform.python_version())"],
        check=True, capture_output=True, text=True,
    ).stdout.strip()


def main() -> int:
    teax_commit = head(TEAX)
    if not teax_commit.startswith(TEAX_PREFIX):
        print(f"teax HEAD is {teax_commit}, not {TEAX_PREFIX}…; refusing", file=sys.stderr)
        return 1
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    codegen_tar, codegen_sha = archive(WORKTREE, "codegen")
    agentic_tar, agentic_sha = archive(AGENTIC, "agentic")
    teax_tar, teax_sha = archive(TEAX, "teax")
    teax_row = {"commit": teax_commit, "artifact_path": str(teax_tar), "archive_sha256": teax_sha}
    record = {
        "schema_version": "stop-parser-execution-provenance/v1",
        "artifact_root": str(ARTIFACTS),
        "python": {"executable": str(PYTHON), "version": python_version()},
        "roots": {
            "codegen_source": {
                "path": str(WORKTREE / "src"),
                "commit": head(WORKTREE),
                "artifact_path": str(codegen_tar),
                "archive_sha256": codegen_sha,
            },
            "agentic_install": {
                "path": str(AGENTIC / "src"),
                "commit": head(AGENTIC),
                "artifact_path": str(agentic_tar),
                "wheel_sha256": agentic_sha,
            },
            "teax_source": {"path": str(TEAX), **teax_row},
            "teax_simkit": {"path": str(TEAX_SIMKIT), **teax_row},
        },
    }
    MANIFEST.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print(MANIFEST)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
