"""When agentic-mbse's subset screen cannot be imported, the generator still answers (Item 2b).

Audit B1, spec Success Criteria 7 and 8, design D17 and Invariant 2. Each run is a fresh
interpreter in which ``agentic_mbse.sysml.subset_profile`` fails to import
(``tests/helpers/blocked_screen_import.py``), the way an incompatible agentic-mbse would fail.

- ``generate --models`` on a case that builds writes the same files, byte for byte, as
  ``generate`` with the screen importable, exits 0, and reports the screen not assessed.
- ``generate --from-snapshot`` does the same. A snapshot is never screened, so its reason is
  the snapshot one, and nothing tries the import.
- ``check`` reports the generator's answer with the screen not assessed: exit 0 for the case
  that builds, exit 1 with today's refusal record for the case that refuses.

None of them shows a traceback or ``ImportError`` text. The screen's own version cannot be read
when its module does not import, so the reason names the pin and the import error.

Licensed.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

from sysml_codegen._upstream_pins import SUBSET_PROFILE_VERSION
from tests.conftest import FIXTURES_DIR, requires_license
from tests.helpers.subset_profile import cases

pytestmark = requires_license

REPO = Path(__file__).resolve().parents[2]
#: A case the generator builds.
BUILDS_CASE = "anonymous-declaration__attribute_usage"
#: A case refused by ``prepare``'s last step.
REFUSED_CASE = "output-naming__param_field_collision"
SNAPSHOT = FIXTURES_DIR / "sample_model" / "instance_graph_snapshot.json"
NOT_IMPORTABLE = (
    "INFO: Screen not assessed: agentic-mbse's subset screen could not be imported, so the "
    f"model was not checked against {SUBSET_PROFILE_VERSION!r}: "
)


#: How each run starts: the CLI as its console script runs it, or with the screen blocked.
_UNBLOCKED = [
    "-c",
    "import sys; from sysml_codegen.cli import main; sys.argv[0] = 'sysml-codegen'; main()",
]
_BLOCKED = ["-m", "tests.helpers.blocked_screen_import"]


def _cli(*argv: str | Path, blocked: bool) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *(_BLOCKED if blocked else _UNBLOCKED), *map(str, argv)],
        cwd=REPO,
        env=os.environ.copy(),
        capture_output=True,
        text=True,
        check=False,
    )


def _models(case_id: str) -> Path:
    return cases.model_root(cases.load_answer(case_id))


def _tree(root: Path) -> dict[str, bytes]:
    return {
        p.relative_to(root).as_posix(): p.read_bytes()
        for p in sorted(root.rglob("*"))
        if p.is_file()
    }


def _clean(run: subprocess.CompletedProcess[str]) -> str:
    output = run.stdout + run.stderr
    assert "Traceback" not in output, output
    assert "ImportError" not in output, output
    return output


@pytest.mark.parametrize(
    "source",
    [("--models", _models(BUILDS_CASE)), ("--from-snapshot", SNAPSHOT)],
    ids=["models", "snapshot"],
)
def test_generate_builds_the_same_package_when_the_screen_cannot_be_imported(source, tmp_path):
    plain = _cli("generate", *source, "--output", tmp_path / "plain", blocked=False)
    assert plain.returncode == 0, plain.stderr
    blocked = _cli("generate", *source, "--output", tmp_path / "blocked", blocked=True)
    output = _clean(blocked)
    assert blocked.returncode == 0, output
    assert _tree(tmp_path / "blocked") == _tree(tmp_path / "plain")
    assert "INFO: Code generation complete" in output
    if source[0] == "--models":
        assert NOT_IMPORTABLE in output
    else:
        assert "INFO: Screen not assessed: snapshots do not carry the screen" in output


def test_check_reports_a_model_that_builds_as_building(tmp_path):
    run = _cli(
        "check", "--models", _models(BUILDS_CASE), "--output", tmp_path / "pkg", blocked=True
    )
    output = _clean(run)
    assert run.returncode == 0, output
    assert "INFO: Generator: builds (1 modules)" in output
    assert NOT_IMPORTABLE in output
    assert not (tmp_path / "pkg").exists()


def test_check_reports_a_refused_model_with_its_refusal(tmp_path):
    run = _cli("check", "--models", _models(REFUSED_CASE), blocked=True)
    output = _clean(run)
    assert run.returncode == 1, output
    assert "ERROR: Code generation failed: PARAM_FIELD_COLLISION" in output
    assert NOT_IMPORTABLE in output
