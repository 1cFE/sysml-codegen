"""``check`` reports without writing, and ``generate`` prints the same report after the seal.

Item 2b design D4, D6, D16, D17, D18; Invariants 1, 3 and 5.

- ``check`` never calls ``emit_package`` and leaves a populated destination byte-identical.
- Exit codes: 1 refused, 3 builds but not ready, 0 ready. No model reaches ready until the
  owner decides the readiness rule (plan assumption A1), so 0 is shown with ``readiness``
  patched.
- A model with parse errors: both commands log today's parsing record, and the screen is not
  assessed because of the parse errors (M2).
- A symlinked destination (M4): ``generate`` logs one ``PACKAGE_WRITE`` record and exits 1;
  ``check --output`` logs the same text at WARNING with no ``refusal`` extra and exits 3. A
  refused model logs only its own refusal on both commands.
- After the seal, nothing in the screen or the report can change ``generate``'s result: each
  of the three report steps patched to raise leaves the same bytes, exit 0, and one WARNING.

Licensed.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

import pytest

from sysml_codegen import cli
from sysml_codegen.cli import CheckRequest, prepare, readiness, run_check
from sysml_codegen.cli.destination import DESTINATION_NOT_CHECKED
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
_GUARD_WARNING = "the screen report could not be produced: "


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
    assert code == (3 if case_id == BUILDS_CASE else 1)
    assert _tree(destination) == before


def test_check_logs_a_refusal_only_for_a_refused_model(monkeypatch, tmp_path):
    destination = _sentinel(tmp_path, "populated")
    with refusal_records.capture_refusals(destination) as built:
        _main(monkeypatch, "check", "--models", _models(BUILDS_CASE), "--output", destination)
    with refusal_records.capture_refusals(destination) as refused:
        _main(monkeypatch, "check", "--models", _models(REFUSED_CASE), "--output", destination)
    assert built == []
    assert refused == BASE[f"case:{REFUSED_CASE}"]


def test_check_exits_0_when_readiness_says_ready(monkeypatch):
    ready = readiness.ReadinessVerdict(readiness.Readiness.READY, ())
    monkeypatch.setattr("sysml_codegen.cli.readiness.readiness", lambda _report: ready)
    assert _main(monkeypatch, "check", "--models", _models(BUILDS_CASE)) == 0


def test_check_without_output_leaves_the_destination_unchecked():
    report = run_check(CheckRequest(prepare.LiveModels((_models(BUILDS_CASE),)), "pkg", None))
    assert isinstance(report.generator, prepare.Prepared)
    assert report.destination == DESTINATION_NOT_CHECKED


@pytest.mark.parametrize("command", ["generate", "check"])
def test_a_model_with_parse_errors(command, monkeypatch, tmp_path, caplog):
    caplog.set_level(logging.INFO, logger="sysml_codegen")
    model = _parse_error_model(tmp_path)
    output = tmp_path / "pkg"
    with refusal_records.capture_refusals(output) as records:
        code = _main(monkeypatch, command, "--models", model, "--output", output)
    assert code == 1
    [record] = records
    assert record["message"].startswith("SysML parsing failed: ")
    assert record["refusal"]["kind"] == "RefusalKind.PARSING"
    infos = _messages(caplog, logging.INFO)
    assert "Screen not assessed: the model has parse errors" in infos
    assert not any(line.startswith(("  refused ", "Disagreement")) for line in infos)
    assert not output.exists()


def test_generate_with_a_symlinked_destination_refuses_once(monkeypatch, tmp_path, caplog):
    caplog.set_level(logging.INFO, logger="sysml_codegen")
    destination = _sentinel(tmp_path, "populated")
    (destination / "elsewhere").symlink_to(tmp_path)
    before = _tree(destination)
    with refusal_records.capture_refusals(destination) as records:
        code = _main(monkeypatch, "generate", "--models", _models(BUILDS_CASE), "-o", destination)
    assert code == 1
    assert [r["message"] for r in records] == [_PACKAGE_WRITE_SYMLINK]
    assert records[0]["refusal"] == {"items": [], "kind": "RefusalKind.PACKAGE_WRITE"}
    assert _messages(caplog, logging.WARNING) == []
    assert _tree(destination) == before


def test_check_with_a_symlinked_destination_warns_and_says_builds(monkeypatch, tmp_path, caplog):
    caplog.set_level(logging.INFO, logger="sysml_codegen")
    destination = _sentinel(tmp_path, "populated")
    (destination / "elsewhere").symlink_to(tmp_path)
    before = _tree(destination)
    with refusal_records.capture_refusals(destination) as records:
        code = _main(monkeypatch, "check", "--models", _models(BUILDS_CASE), "-o", destination)
    assert code == 3
    assert records == []
    warnings = [m.replace(str(destination), "<OUTPUT>") for m in _messages(caplog, logging.WARNING)]
    assert warnings == [_PACKAGE_WRITE_SYMLINK]
    assert f"  - generate would stop at the destination: {_PACKAGE_WRITE_SYMLINK}" in [
        m.replace(str(destination), "<OUTPUT>") for m in _messages(caplog, logging.INFO)
    ]
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


@pytest.mark.parametrize(
    "target",
    [
        "sysml_codegen.subset_screen.assess_screen",
        "sysml_codegen.cli.readiness.readiness_report",
        "sysml_codegen.cli.readiness.log_assessment",
    ],
)
def test_generate_survives_a_report_failure(target, monkeypatch, tmp_path, caplog):
    """D17's third layer: same bytes, exit 0, one WARNING naming the failure."""
    unpatched = tmp_path / "unpatched"
    assert _main(monkeypatch, "generate", "--models", _models(BUILDS_CASE), "-o", unpatched) == 0

    def raising(*_args: object, **_kwargs: object) -> None:
        raise RuntimeError("probe: the report broke")

    monkeypatch.setattr(target, raising)
    caplog.clear()
    caplog.set_level(logging.INFO, logger="sysml_codegen")
    patched = tmp_path / "patched"
    assert _main(monkeypatch, "generate", "--models", _models(BUILDS_CASE), "-o", patched) == 0
    assert _tree(patched) == _tree(unpatched)
    assert _messages(caplog, logging.WARNING) == [
        f"{_GUARD_WARNING}RuntimeError: probe: the report broke"
    ]


def test_check_has_no_guard(monkeypatch):
    """A report bug in ``check`` is a ``check`` bug, so it fails loudly (D17)."""

    def raising(*_args: object, **_kwargs: object) -> None:
        raise RuntimeError("probe: the report broke")

    monkeypatch.setattr("sysml_codegen.cli.readiness.log_assessment", raising)
    with pytest.raises(RuntimeError, match="probe: the report broke"):
        _main(monkeypatch, "check", "--models", _models(BUILDS_CASE))


def test_generate_prints_the_report_after_writing(monkeypatch, tmp_path, caplog):
    """D16: the generator section, then the writing, then the screen and readiness."""
    caplog.set_level(logging.INFO, logger="sysml_codegen")
    output = tmp_path / "pkg"
    assert _main(monkeypatch, "generate", "--models", _models(BUILDS_CASE), "-o", output) == 0
    infos = _messages(caplog, logging.INFO)
    builds = next(i for i, m in enumerate(infos) if m.startswith("Generator: builds ("))
    screen = next(i for i, m in enumerate(infos) if m.startswith("Screen "))
    sealed = [i for i, m in enumerate(infos) if "seal" in m.lower()]
    assert sealed and all(builds < i < screen for i in sealed), infos
    assert infos[screen - 1] == "Destination: clean"
    assert infos[-2:] == ["Readiness: not ready", f"  - {readiness.AWAITING_OWNER}"]
