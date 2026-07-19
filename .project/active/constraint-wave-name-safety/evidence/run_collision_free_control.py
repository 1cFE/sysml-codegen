"""Point to the kept real-execution node used for collision-free evidence."""

from __future__ import annotations

import subprocess
import sys

if __name__ == "__main__":
    raise SystemExit(
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                "-q",
                "-m",
                "execution",
                "tests/execution/test_constraint_execution.py",
                "-k",
                "name_safety_collision_free",
            ],
            check=False,
        ).returncode
    )
