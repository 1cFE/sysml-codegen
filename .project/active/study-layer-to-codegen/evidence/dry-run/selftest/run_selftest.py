#!/usr/bin/env python3
"""Self-test ``check_record.py`` against the installed runbook's own Check lines (design DD12).

Two small records sit beside this file. ``good/`` meets all five conditions. ``bad/`` breaks each
condition once: § 15 and the discovery log disagree both ways, record.md keeps a placeholder, a
fingerprint name has no key, an arm's store is not in ``stores[]``, and an artifact has no digest.

For each record this runs the five Check commands from the shipped runbook
(``src/sysml_codegen/assets/skills/run-study/runbook.md``, steps 14 and 15) and ``check_record.py``,
and requires that they agree condition by condition: on ``good/`` every one passes, and on ``bad/``
every one fails. It exits 0 only then.

Usage: run_selftest.py
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[5]
RUNBOOK = REPO / "src/sysml_codegen/assets/skills/run-study/runbook.md"
CHECK_RECORD = HERE.parent / "check_record.py"
STUDY_ID = "20261012-pump-fit"
#: What each Check line prints when its condition holds, in the runbook's order.
PASSING = ["[]", "0", "[]", "[]", "[]"]


def check_lines() -> list[str]:
    """The ``python3 -c`` commands in the code block after each **Check:** line, in order."""
    commands: list[str] = []
    lines = RUNBOOK.read_text().splitlines()
    for i, line in enumerate(lines):
        if not line.startswith("**Check:**"):
            continue
        start = next(j for j in range(i + 1, len(lines)) if lines[j].startswith("```"))
        end = next(j for j in range(start + 1, len(lines)) if lines[j].startswith("```"))
        commands += [c for c in lines[start + 1 : end] if c.startswith("python3 -c")]
    return commands


def runbook_verdicts(record_dir: Path) -> list[bool]:
    """Whether each runbook Check line printed its passing answer in ``record_dir``."""
    verdicts = []
    for command, passing in zip(check_lines(), PASSING, strict=True):
        run = subprocess.run(
            ["bash", "-c", command.replace("<study-id>", STUDY_ID)],
            cwd=record_dir, capture_output=True, text=True, check=False,
        )
        if run.returncode != 0:
            sys.exit(f"run_selftest: a runbook Check line failed to run in {record_dir}:\n"
                     f"{command}\n{run.stderr}")
        verdicts.append(run.stdout.strip() == passing)
    return verdicts


def check_record_verdicts(record_dir: Path) -> tuple[int, list[bool]]:
    """check_record.py's exit code, and whether it passed each of its five conditions."""
    run = subprocess.run(
        [sys.executable, str(CHECK_RECORD), str(record_dir)],
        capture_output=True, text=True, check=False,
    )
    verdicts = [line.startswith("PASS") for line in run.stdout.splitlines()
                if re.match(r"(PASS|FAIL) \d ", line)]
    return run.returncode, verdicts


def main() -> int:
    commands = check_lines()
    if len(commands) != len(PASSING):
        print(f"run_selftest: expected {len(PASSING)} Check commands in {RUNBOOK}, "
              f"found {len(commands)}")
        return 1
    failures = 0
    for name, expect_pass, expect_code in (("good", True, 0), ("bad", False, 1)):
        record_dir = HERE / name / STUDY_ID
        theirs = runbook_verdicts(record_dir)
        code, ours = check_record_verdicts(record_dir)
        agree = theirs == ours
        as_expected = theirs == [expect_pass] * len(PASSING) and code == expect_code
        verdict = f"{'agree' if agree else 'DISAGREE'}, "
        verdict += "as expected" if as_expected else "UNEXPECTED"
        print(f"{name}: runbook Check lines {theirs}, check_record.py {ours} (exit {code}); "
              f"{verdict}")
        failures += (not agree) + (not as_expected)
    print("run_selftest: pass" if failures == 0 else f"run_selftest: {failures} problem(s)")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
