"""``sysml-codegen study <tool>`` hands its arguments to the tool unchanged (design DD3)."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import pytest

from sysml_codegen.cli.study import STUDY_TOOLS, cmd_study
from tests.study.conftest import SYNTHETIC_AXES, SYNTHETIC_MANIFEST, SYNTHETIC_PACKAGE


def _cli(*argv: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "sysml_codegen", "study", *argv],
        capture_output=True, text=True, cwd=str(cwd),
    )


def _module(tool: str, *argv: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", f"sysml_codegen.study.{tool}", *argv],
        capture_output=True, text=True, cwd=str(cwd),
    )


def test_the_dispatcher_offers_exactly_the_four_tools() -> None:
    assert STUDY_TOOLS == ("indicators", "preflight", "verify", "integrate")


def test_a_run_through_the_cli_equals_the_module_run(repo_root: Path) -> None:
    argv = (
        "--package", str(SYNTHETIC_PACKAGE),
        "--manifest", str(SYNTHETIC_MANIFEST),
        "--groups", str(SYNTHETIC_AXES),
    )
    via_cli = _cli("indicators", *argv, cwd=repo_root)
    via_module = _module("indicators", *argv, cwd=repo_root)
    assert via_cli.returncode == via_module.returncode == 0, via_cli.stderr
    assert via_cli.stdout == via_module.stdout
    assert '"path": "sysml_codegen/study/indicators.py"' in via_cli.stdout


def test_a_tool_failure_keeps_its_exit_code(repo_root: Path, tmp_path: Path) -> None:
    """indicators exits 1 on a mechanical failure; the dispatcher must not flatten it."""
    missing = tmp_path / "absent.json"
    argv = ("--package", str(SYNTHETIC_PACKAGE), "--manifest", str(missing),
            "--groups", str(SYNTHETIC_AXES))
    via_cli = _cli("indicators", *argv, cwd=repo_root)
    via_module = _module("indicators", *argv, cwd=repo_root)
    assert via_cli.returncode == via_module.returncode == 1
    assert via_cli.stdout == ""
    assert via_cli.stderr == via_module.stderr


@pytest.mark.parametrize("tool", STUDY_TOOLS)
def test_help_passes_through_to_the_tool(tool: str, repo_root: Path) -> None:
    via_cli = _cli(tool, "--help", cwd=repo_root)
    assert via_cli.returncode == 0
    assert via_cli.stdout == _module(tool, "--help", cwd=repo_root).stdout
    assert via_cli.stdout.startswith(f"usage: {tool}.py")


def test_a_subcommand_reaches_the_tool_unchanged(repo_root: Path) -> None:
    via_cli = _cli("preflight", "clean", "--help", cwd=repo_root)
    assert via_cli.returncode == 0
    assert via_cli.stdout.startswith("usage: preflight.py clean")


@pytest.mark.parametrize(
    "argv,message",
    [
        ((), "the following arguments are required: tool"),
        (
            ("bogus",),
            "invalid choice: 'bogus' (choose from indicators, preflight, verify, integrate)",
        ),
    ],
)
def test_a_missing_or_unknown_tool_is_a_usage_error(
    argv: tuple[str, ...], message: str, repo_root: Path
) -> None:
    done = _cli(*argv, cwd=repo_root)
    assert done.returncode == 2
    assert message in done.stderr


def test_a_tool_usage_error_keeps_exit_2(repo_root: Path) -> None:
    done = _cli("verify", cwd=repo_root)
    assert done.returncode == 2
    assert done.stderr.startswith("usage: verify.py")


def test_cmd_study_returns_the_tools_exit_code_in_process(repo_root: Path) -> None:
    code = cmd_study(argparse.Namespace(
        tool="indicators",
        args=["--package", str(SYNTHETIC_PACKAGE), "--print-fingerprint"],
    ))
    assert code == 0
