"""A refused ``generate`` leaves its destination exactly as it found it (Item 2b spec Criteria 1-2).

Since Phase 4 every model refusal is decided by ``prepare``, before the destination is
inspected, cleared, created or written (design D3, D4). Every 2a case the generator refuses
is run through ``run_codegen`` under each destination flag set, into a populated and into an
empty destination. The tree must be byte-identical afterwards, with no file added or
removed, and the run must log exactly one refusal record, equal to the one the base commit
logged for that case (``tests/expectations/subset_profile/refusal_records.json``).

``check --output`` gets the same matrix, without the flags it does not take (design D6): the
same tree check, the same single record, and the same ``Refused`` (step, refusal and message)
that ``generate`` hands to the logger for that case.

The one stated change (design D4) has its own test below: a model refused by its last check,
run against a destination holding a symlink, now reports the model's refusal where the base
reported ``PACKAGE_WRITE``. A model that builds still gets ``PACKAGE_WRITE`` there.

Licensed.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

from sysml_codegen import cli
from sysml_codegen.cli import GenerationConfig, prepare, run_codegen
from sysml_codegen.cli.prepare import Refused
from tests.conftest import requires_license
from tests.helpers import refusal_records
from tests.helpers.subset_profile import cases
from tests.helpers.subset_profile.cases import GeneratorOutcome, StoredAnswer

pytestmark = requires_license

REFUSED = [a for a in cases.all_answers() if a.generator.run.outcome is GeneratorOutcome.REFUSED]
BASE = refusal_records.load()

#: The destination flags ``generate`` takes; each changes only what writing does.
FLAGS = {
    "none": {},
    "overwrite": {"overwrite": True},
    "preserve-handwritten": {"preserve_handwritten": True},
    "smart-regen": {"smart_regen": True},
    "overwrite+preserve-handwritten": {"overwrite": True, "preserve_handwritten": True},
}

#: The D4 coincidence case: refused by the parameter-field check, ``prepare``'s last step.
LATE_REFUSAL_CASE = "output-naming__param_field_collision"
#: A case that builds (the one ``scripts/refusal_records.py`` patches a writer on).
BUILDS_CASE = "anonymous-declaration__attribute_usage"


def _sentinel(root: Path, kind: str) -> Path:
    destination = root / "pkg"
    destination.mkdir()
    if kind == "populated":
        (destination / "handwritten").mkdir()
        (destination / "handwritten" / "impl.py").write_text("# kept by hand\n")
        (destination / "schemas").mkdir()
        (destination / "schemas" / "old.py").write_bytes(b"stale\x00schema\n")
        (destination / "__init__.py").write_text('"""An older package."""\n')
    return destination


def _tree(root: Path) -> list[tuple[str, str, bytes | None]]:
    entries: list[tuple[str, str, bytes | None]] = []
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            entries.append((relative, "symlink", os.readlink(path).encode()))
        elif path.is_dir():
            entries.append((relative, "directory", None))
        else:
            entries.append((relative, "file", path.read_bytes()))
    return entries


def _generate(answer: StoredAnswer, destination: Path, **flags: bool) -> list[dict]:
    config = GenerationConfig(
        output_path=destination, models_path=cases.model_root(answer), **flags
    )
    with refusal_records.capture_refusals(destination) as records:
        assert run_codegen(config) is False
    return records


@pytest.mark.parametrize("sentinel", ["populated", "empty"])
@pytest.mark.parametrize("flags", sorted(FLAGS))
@pytest.mark.parametrize("answer", REFUSED, ids=lambda a: a.case_id)
def test_a_refused_generate_leaves_its_destination(answer, flags, sentinel, tmp_path):
    destination = _sentinel(tmp_path, sentinel)
    before = _tree(destination)
    records = _generate(answer, destination, **FLAGS[flags])
    assert _tree(destination) == before
    assert records == BASE[f"case:{answer.case_id}"]
    assert len(records) == 1


def _logged_refused(monkeypatch: pytest.MonkeyPatch) -> list[Refused]:
    """Every ``Refused`` either command hands to ``log_refused``."""
    seen: list[Refused] = []
    real = prepare.log_refused

    def spy(refused: Refused) -> None:
        seen.append(refused)
        real(refused)

    monkeypatch.setattr(prepare, "log_refused", spy)
    return seen


@pytest.mark.parametrize("sentinel", ["populated", "empty"])
@pytest.mark.parametrize("answer", REFUSED, ids=lambda a: a.case_id)
def test_check_refuses_as_generate_does_and_leaves_its_destination(
    answer, sentinel, monkeypatch, tmp_path
):
    seen = _logged_refused(monkeypatch)
    destination = _sentinel(tmp_path, sentinel)
    before = _tree(destination)
    argv = ["sysml-codegen", "check", "--models", str(cases.model_root(answer))]
    monkeypatch.setattr(sys, "argv", [*argv, "--output", str(destination)])
    with refusal_records.capture_refusals(destination) as records:
        with pytest.raises(SystemExit) as exit_info:
            cli.main()
    assert exit_info.value.code == 1
    assert _tree(destination) == before
    assert records == BASE[f"case:{answer.case_id}"]
    _generate(answer, tmp_path / "generated")
    [checked, generated] = seen
    assert checked == generated


def test_the_late_refusal_case_is_among_the_refused_cases():
    assert LATE_REFUSAL_CASE in {a.case_id for a in REFUSED}


def test_a_refused_model_with_a_symlinked_destination_reports_the_model(tmp_path):
    """D4's stated change: the model's refusal, not ``PACKAGE_WRITE``, and nothing written."""
    destination = _sentinel(tmp_path, "populated")
    (destination / "elsewhere").symlink_to(tmp_path)
    before = _tree(destination)
    records = _generate(cases.load_answer(LATE_REFUSAL_CASE), destination)
    assert _tree(destination) == before
    assert records == BASE[f"case:{LATE_REFUSAL_CASE}"]
    assert records == BASE[f"destination_link:{LATE_REFUSAL_CASE}"]
    [record] = records
    assert record["refusal"]["kind"] == "RefusalKind.GENERATION"
    assert "PARAM_FIELD_COLLISION" in record["message"]


def test_a_building_model_with_a_symlinked_destination_still_reports_package_write(tmp_path):
    destination = _sentinel(tmp_path, "populated")
    (destination / "elsewhere").symlink_to(tmp_path)
    before = _tree(destination)
    records = _generate(cases.load_answer(BUILDS_CASE), destination)
    assert _tree(destination) == before
    assert records == [
        {
            "level": "ERROR",
            "logger": "sysml_codegen.cli",
            "message": "Package sealing failed: INVALID_PATH(elsewhere): symlinks are "
            "forbidden beneath the package root",
            "refusal": {"items": [], "kind": "RefusalKind.PACKAGE_WRITE"},
        }
    ]
