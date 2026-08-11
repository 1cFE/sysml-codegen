"""The retirement runbook's prepared patches still apply.

The runbook (`.project/active/cutover-recovery/plan.md`) executes after the owner accepts,
so its per-file edits live as reviewable patches rather than as edits already made. A patch
is only reviewable if it still describes the tree it will be applied to, and the tree keeps
moving while the acceptance is pending. These nodes are what says so.

The patches are **sequenced**: step 2's patches were derived against the tree with step 1's
already applied, and several files (``snapshot/__init__.py`` and four test modules) are
edited by both steps. So the check replays them in order into a scratch directory seeded
from HEAD, rather than checking each one against HEAD independently.

The scratch directory holds only the files the patches touch. Deletions are not replayed —
``scripts/retire_step.py apply N`` does those, and no patch edits a file an earlier step
deletes (which is itself part of what a clean replay proves).
"""

from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
PATCH_ROOT = REPO_ROOT / ".project/active/cutover-recovery/runbook-patches"
STEPS = ("step1", "step2")

#: `diff -u`/`git diff` both write `+++ b/<path>`; the patches are all repo-relative.
_TARGET = re.compile(r"^\+\+\+ b/(.+)$", re.MULTILINE)


def _patches(step: str) -> list[Path]:
    return sorted((PATCH_ROOT / step).glob("*.patch"))


def _targets(patch: Path) -> list[str]:
    return _TARGET.findall(patch.read_text())


def test_the_patch_directories_are_not_empty() -> None:
    """An empty directory would make every node below vacuously green."""
    for step in STEPS:
        assert _patches(step), f"{step} carries no patch"


@pytest.mark.parametrize("step", STEPS)
def test_every_patch_names_exactly_one_existing_file(step: str) -> None:
    """One patch, one file — that is what makes the runbook's per-row table reviewable."""
    for patch in _patches(step):
        targets = _targets(patch)
        assert len(targets) == 1, f"{patch.name} touches {targets}"
        assert (REPO_ROOT / targets[0]).is_file(), f"{patch.name}: {targets[0]} is gone"


def test_the_prepared_patches_replay_cleanly_in_step_order() -> None:
    """Step 1's patches apply to HEAD, and step 2's to the result. In order, all of them.

    A failure here means the tree moved under a prepared edit: the patch has to be
    regenerated before the runbook can be executed, and the runbook's claim that its steps
    are mechanical is not true until it is.
    """
    everything = [patch for step in STEPS for patch in _patches(step)]
    touched = {target for patch in everything for target in _targets(patch)}

    with tempfile.TemporaryDirectory() as scratch_name:
        scratch = Path(scratch_name)
        for relative in sorted(touched):
            destination = scratch / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(REPO_ROOT / relative, destination)

        for step in STEPS:
            for patch in _patches(step):
                result = subprocess.run(
                    ["git", "apply", "--verbose", str(patch)],
                    cwd=scratch,
                    capture_output=True,
                    text=True,
                )
                assert result.returncode == 0, (
                    f"{step}/{patch.name} no longer applies:\n{result.stderr}"
                )
