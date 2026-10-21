"""``check`` gives ``generate``'s answer without writing.

Item 2b design D4, D6, D16, D18; Invariants 1, 3 and 5.

- ``check`` never calls ``emit_package`` and leaves a populated destination byte-identical.
- Exit codes: ``generate``'s answer, 0 when it would build and 1 when it would refuse. The
  test over every 2a case is ``subset_profile/test_report_form.py``.
- A model with parse errors: both commands log today's parsing record (M2).
- A symlinked destination (M4): ``generate`` and ``check --output`` both log the same one
  ``PACKAGE_WRITE`` record and exit 1. A refused model logs only its own refusal on both.
- ``generate`` prints the generator's answer before it writes.

Licensed.
"""

from __future__ import annotations

import logging
import os
import subprocess
import sys
from pathlib import Path

import pytest

from sysml_codegen import cli
from sysml_codegen.cli import CheckRequest, prepare, run_check
from tests.conformance.test_refusal_before_first_write import _sentinel, _tree
from tests.conftest import requires_license
from tests.helpers import refusal_records
from tests.helpers.subset_profile import cases

pytestmark = requires_license

#: A case the generator builds.
BUILDS_CASE = "anonymous-declaration__attribute_usage"
#: A case refused by ``prepare``'s last step.
REFUSED_CASE = "output-naming__param_field_collision"
BASE = refusal_records.load()

_PACKAGE_WRITE_SYMLINK = (
    "Package sealing failed: INVALID_PATH(elsewhere): symlinks are forbidden beneath the "
    "package root"
)


def _models(case_id: str) -> Path:
    return cases.model_root(cases.load_answer(case_id))


def _main(monkeypatch: pytest.MonkeyPatch, *argv: str | Path) -> int:
    monkeypatch.setattr(sys, "argv", ["sysml-codegen", *map(str, argv)])
    with pytest.raises(SystemExit) as exit_info:
        cli.main()
    code = exit_info.value.code
    assert isinstance(code, int)
    return code


def _parse_error_model(root: Path) -> Path:
    model = root / "model"
    model.mkdir()
    (model / "model.sysml").write_text("package SyntaxProbe;\npart def Broken { attribute\n")
    return model


def _fail(*_args: object, **_kwargs: object) -> None:
    raise AssertionError("check called emit_package")


def _messages(caplog: pytest.LogCaptureFixture, level: int) -> list[str]:
    return [r.getMessage() for r in caplog.records if r.levelno == level]


@pytest.mark.parametrize("case_id", [BUILDS_CASE, REFUSED_CASE])
def test_check_writes_nothing_and_never_calls_emit(case_id, monkeypatch, tmp_path):
    monkeypatch.setattr("sysml_codegen.cli.emit.emit_package", _fail)
    monkeypatch.setattr("sysml_codegen.cli.emit._write_package", _fail)
    destination = _sentinel(tmp_path, "populated")
    before = _tree(destination)
    code = _main(monkeypatch, "check", "--models", _models(case_id), "--output", destination)
    assert code == (0 if case_id == BUILDS_CASE else 1)
    assert _tree(destination) == before


def test_check_logs_a_refusal_only_for_a_refused_model(monkeypatch, tmp_path):
    destination = _sentinel(tmp_path, "populated")
    with refusal_records.capture_refusals(destination) as built:
        _main(monkeypatch, "check", "--models", _models(BUILDS_CASE), "--output", destination)
    with refusal_records.capture_refusals(destination) as refused:
        _main(monkeypatch, "check", "--models", _models(REFUSED_CASE), "--output", destination)
    assert built == []
    assert refused == BASE[f"case:{REFUSED_CASE}"]


def test_check_without_output_inspects_no_destination(monkeypatch):
    def inspected(*_args: object) -> None:
        raise AssertionError("check inspected a destination it was not given")

    monkeypatch.setattr("sysml_codegen.cli.destination.inspect_destination", inspected)
    generator = run_check(CheckRequest(prepare.LiveModels((_models(BUILDS_CASE),)), "pkg", None))
    assert isinstance(generator, prepare.Prepared)


@pytest.mark.parametrize("command", ["generate", "check"])
def test_a_model_with_parse_errors(command, monkeypatch, tmp_path):
    model = _parse_error_model(tmp_path)
    output = tmp_path / "pkg"
    with refusal_records.capture_refusals(output) as records:
        code = _main(monkeypatch, command, "--models", model, "--output", output)
    assert code == 1
    [record] = records
    assert record["message"].startswith("SysML parsing failed: ")
    assert record["refusal"]["kind"] == "RefusalKind.PARSING"
    assert not output.exists()


@pytest.mark.parametrize("command", ["generate", "check"])
def test_a_symlinked_destination_refuses_once(command, monkeypatch, tmp_path, caplog):
    """``check --output`` gives ``generate``'s answer: the same one record, exit 1."""
    caplog.set_level(logging.INFO, logger="sysml_codegen")
    destination = _sentinel(tmp_path, "populated")
    (destination / "elsewhere").symlink_to(tmp_path)
    before = _tree(destination)
    with refusal_records.capture_refusals(destination) as records:
        code = _main(monkeypatch, command, "--models", _models(BUILDS_CASE), "-o", destination)
    assert code == 1
    assert [r["message"] for r in records] == [_PACKAGE_WRITE_SYMLINK]
    assert records[0]["refusal"] == {"items": [], "kind": "RefusalKind.PACKAGE_WRITE"}
    assert _messages(caplog, logging.WARNING) == []
    assert _tree(destination) == before


@pytest.mark.parametrize("command", ["generate", "check"])
def test_a_refused_model_with_a_symlinked_destination_logs_only_the_model(
    command, monkeypatch, tmp_path, caplog
):
    caplog.set_level(logging.INFO, logger="sysml_codegen")
    destination = _sentinel(tmp_path, "populated")
    (destination / "elsewhere").symlink_to(tmp_path)
    before = _tree(destination)
    with refusal_records.capture_refusals(destination) as records:
        code = _main(monkeypatch, command, "--models", _models(REFUSED_CASE), "-o", destination)
    assert code == 1
    assert records == BASE[f"case:{REFUSED_CASE}"]
    assert _messages(caplog, logging.WARNING) == []
    assert _tree(destination) == before


def test_generate_prints_its_answer_before_writing(monkeypatch, tmp_path, caplog):
    """D16: the generator's answer, then the writing."""
    caplog.set_level(logging.INFO, logger="sysml_codegen")
    output = tmp_path / "pkg"
    assert _main(monkeypatch, "generate", "--models", _models(BUILDS_CASE), "-o", output) == 0
    infos = _messages(caplog, logging.INFO)
    builds = next(i for i, m in enumerate(infos) if m.startswith("Generator: builds ("))
    sealed = [i for i, m in enumerate(infos) if "seal" in m.lower()]
    assert sealed and all(builds < i for i in sealed), infos


def test_check_never_loads_the_writing_module(tmp_path):
    """Invariant 1 by structure: a ``check`` run in a fresh interpreter never imports ``emit``."""
    driver = (
        "import sys\n"
        "from sysml_codegen.cli import main\n"
        "sys.argv[0] = 'sysml-codegen'\n"
        "try:\n"
        "    main()\n"
        "except SystemExit as done:\n"
        "    print('exit', done.code, 'emit loaded', 'sysml_codegen.cli.emit' in sys.modules)\n"
    )
    models = str(_models(BUILDS_CASE))
    run = subprocess.run(
        [sys.executable, "-c", driver, "check", "--models", models, "--output", str(tmp_path)],
        env=os.environ.copy(),
        capture_output=True,
        text=True,
        check=False,
    )
    assert run.stdout.strip().splitlines()[-1] == "exit 0 emit loaded False", run.stderr
