"""``sysml-codegen install-commands`` installs the study layer with agentic-mbse's ownership rules.

The skill bundle and the Claude command are managed assets on sysml-codegen's own manifest; the
study policy is a project document (spec SC1, SC2; design DD4-DD6, Appendix D). Every run here is
noninteractive unless a test hands it a terminal, so a conflict answers ``skip``.
"""

from __future__ import annotations

import hashlib
import io
import json
import os
import subprocess
import sys
from argparse import Namespace
from pathlib import Path

import agentic_mbse.cli.installation as installation
import pytest
from agentic_mbse.cli import (
    TOOL_OWNED_TEMPLATES,
    USER_OWNED_TEMPLATES,
    cmd_init,
    get_skills_dir,
)

from sysml_codegen import _upstream_pins
from sysml_codegen.cli import install
from sysml_codegen.cli.install import (
    INSTALLER_API_REVISION,
    MANIFEST,
    install_commands,
    list_assets,
    require_installer_api,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
RUN_STUDY = install.SKILLS / "run-study"
BUNDLE_FILES = sorted(p.name for p in RUN_STUDY.iterdir() if p.is_file())
TEAX_COMPLETION = install.COMMANDS / "teax-completion.md"
POLICY_TEMPLATE = install.PROJECT_TEMPLATES / "STUDY_POLICY.md.template"
POLICY = "modeling_project/STUDY_POLICY.md"
RUNBOOK = ".agents/skills/run-study/runbook.md"
COMMAND = ".claude/commands/teax-completion.md"
ALIAS = ".claude/skills/run-study"
#: DD6's message for a command today's installer left behind with other bytes.
UNMANAGED_COMMAND = (
    "Preserved .claude/commands/teax-completion.md: it differs from the shipped file and is "
    "not in the install manifest; re-run interactively or with --force to replace it"
)


class Terminal(io.StringIO):
    """Standard input that reads as an interactive terminal, answering from ``answers``."""

    def isatty(self) -> bool:
        return True


@pytest.fixture(autouse=True)
def noninteractive(monkeypatch: pytest.MonkeyPatch) -> None:
    """No test reads the real standard input; a test that wants a terminal replaces this."""
    monkeypatch.setattr(sys, "stdin", io.StringIO(""))


def tree(target: Path) -> list[str]:
    """Every file and link under ``target``, relative, as ``find -type f -o -type l`` lists them."""
    return sorted(
        p.relative_to(target).as_posix()
        for p in target.rglob("*")
        if p.is_symlink() or p.is_file()
    )


def manifest(target: Path, name: str = MANIFEST) -> dict[str, str]:
    return json.loads((target / name).read_text())["files"]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_if_present(path: Path) -> bytes | None:
    return path.read_bytes() if path.exists() else None


def init(target: Path) -> int:
    """agentic-mbse's own ``init``, noninteractive, as a project runs it."""
    return cmd_init(Namespace(path=str(target), force=False, dev=False))


def test_a_fresh_install_lays_out_appendix_d(tmp_path: Path) -> None:
    actions = install_commands(tmp_path, assistant="both", force=False)

    bundle = [f".agents/skills/run-study/{name}" for name in BUNDLE_FILES]
    assert BUNDLE_FILES == [
        "SKILL.md", "annex-template.md", "integration-guide.md", "record-template.md", "runbook.md"
    ]
    assert tree(tmp_path) == sorted([*bundle, ALIAS, COMMAND, POLICY, MANIFEST])
    for name in BUNDLE_FILES:
        assert (tmp_path / ".agents/skills/run-study" / name).read_bytes() == (
            RUN_STUDY / name
        ).read_bytes()
    assert os.readlink(tmp_path / ALIAS) == "../../.agents/skills/run-study"
    assert (tmp_path / ALIAS / "runbook.md").read_bytes() == (RUN_STUDY / "runbook.md").read_bytes()
    assert (tmp_path / COMMAND).read_bytes() == TEAX_COMPLETION.read_bytes()
    assert (tmp_path / POLICY).read_bytes() == POLICY_TEMPLATE.read_bytes()

    # The policy is the project's document, so the managed manifest never records it.
    assert sorted(manifest(tmp_path)) == sorted([*bundle, ALIAS, COMMAND])
    assert not (tmp_path / ".agentic-mbse").exists()
    assert sorted(actions["created"]) == sorted([*bundle, COMMAND, POLICY])
    assert actions["symlinked"] == [ALIAS]
    assert actions["skipped"] == actions["updated"] == actions["removed"] == []


def test_list_names_the_skill_the_command_and_the_project_document() -> None:
    listing = "\n".join(list_assets())
    meta = installation.frontmatter(RUN_STUDY / "SKILL.md")[0]
    description = " ".join(meta["description"].split())

    assert "run-study (workflow)" in listing and description in listing
    assert "teax-completion" in listing
    assert f"{POLICY} (from STUDY_POLICY.md.template)" in listing
    headings = [line for line in list_assets() if not line.startswith(" ")]
    assert len(headings) == 3


def test_a_reinstall_refreshes_an_unmodified_file(tmp_path: Path) -> None:
    """A file still as an earlier release installed it takes the shipped bytes, without asking."""
    install_commands(tmp_path, assistant="both", force=False)
    earlier = b"the runbook as an earlier release shipped it\n"
    (tmp_path / RUNBOOK).write_bytes(earlier)
    files = manifest(tmp_path)
    files[RUNBOOK] = sha256(earlier)
    (tmp_path / MANIFEST).write_text(json.dumps({"version": 2, "files": files}))

    actions = install_commands(tmp_path, assistant="both", force=False)

    assert (tmp_path / RUNBOOK).read_bytes() == (RUN_STUDY / "runbook.md").read_bytes()
    # agentic-mbse's installer rewrites every managed file it may, and lists each as updated.
    assert RUNBOOK in actions["updated"]
    assert actions["skipped"] == [POLICY]
    assert manifest(tmp_path)[RUNBOOK] == sha256((RUN_STUDY / "runbook.md").read_bytes())


def test_a_reinstall_keeps_an_edited_skill_file_and_the_policy(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    install_commands(tmp_path, assistant="both", force=False)
    (tmp_path / RUNBOOK).write_text("edited")
    (tmp_path / POLICY).write_text("ours")
    capsys.readouterr()

    actions = install_commands(tmp_path, assistant="both", force=False)

    assert (tmp_path / RUNBOOK).read_text() == "edited"
    assert (tmp_path / POLICY).read_text() == "ours"
    assert not (tmp_path / ".agentic-mbse/install.json").exists()
    assert sorted(actions["skipped"]) == sorted([RUNBOOK, POLICY])
    out = capsys.readouterr().out
    assert (
        f"Preserved {RUNBOOK}: it was edited after sysml-codegen installed it; "
        "re-run interactively or with --force to replace it"
    ) in out
    assert f"Preserved {POLICY}: it is this project's document; --force replaces it" in out
    # The skipped edit keeps its baseline, so the next run still sees an edit, not a new file.
    assert manifest(tmp_path)[RUNBOOK] == sha256((RUN_STUDY / "runbook.md").read_bytes())


def test_force_replaces_an_edited_skill_file_and_the_policy(tmp_path: Path) -> None:
    install_commands(tmp_path, assistant="both", force=False)
    (tmp_path / RUNBOOK).write_text("edited")
    (tmp_path / POLICY).write_text("ours")

    actions = install_commands(tmp_path, assistant="both", force=True)

    assert (tmp_path / RUNBOOK).read_bytes() == (RUN_STUDY / "runbook.md").read_bytes()
    assert (tmp_path / POLICY).read_bytes() == POLICY_TEMPLATE.read_bytes()
    assert RUNBOOK in actions["updated"] and POLICY in actions["updated"]
    assert actions["skipped"] == []


@pytest.mark.parametrize(
    ("answers", "runbook", "backups"),
    [
        ("x\no\n", "shipped", []),        # an unknown answer asks again
        ("b\n", "shipped", ["runbook.md.backup"]),
        ("s\n", "edited", []),
    ],
)
def test_an_interactive_run_asks_about_an_edited_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    answers: str,
    runbook: str,
    backups: list[str],
) -> None:
    install_commands(tmp_path, assistant="both", force=False)
    (tmp_path / RUNBOOK).write_text("edited")
    monkeypatch.setattr(sys, "stdin", Terminal(answers))
    capsys.readouterr()

    install_commands(tmp_path, assistant="both", force=False)

    shipped = (RUN_STUDY / "runbook.md").read_text()
    assert (tmp_path / RUNBOOK).read_text() == (shipped if runbook == "shipped" else "edited")
    found = sorted(p.name for p in (tmp_path / RUNBOOK).parent.glob("runbook.md.backup*"))
    assert found == backups
    out = capsys.readouterr().out
    assert f"{RUNBOOK}: it was edited after sysml-codegen installed it." in out
    assert ("Please enter s, b, o, S or O." in out) == answers.startswith("x")
    # Only the runbook is asked about. The policy is the project's, kept without a prompt.
    assert out.count("Choice [s/b/o/S/O]:") == answers.count("\n")
    assert f"Preserved {POLICY}" in out


def test_the_first_run_adopts_a_command_left_with_the_shipped_bytes(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Today's installer copied teax-completion with no manifest; identical bytes are adopted."""
    (tmp_path / ".claude/commands").mkdir(parents=True)
    (tmp_path / COMMAND).write_bytes(TEAX_COMPLETION.read_bytes())

    actions = install_commands(tmp_path, assistant="both", force=False)

    assert COMMAND in actions["updated"] and COMMAND not in actions["skipped"]
    assert manifest(tmp_path)[COMMAND] == sha256(TEAX_COMPLETION.read_bytes())
    assert "Preserved" not in capsys.readouterr().out


def test_the_first_run_preserves_a_command_left_with_other_bytes(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    (tmp_path / ".claude/commands").mkdir(parents=True)
    (tmp_path / COMMAND).write_text("an older teax-completion\n")

    for run in range(2):
        actions = install_commands(tmp_path, assistant="both", force=False)
        assert actions["skipped"] == ([COMMAND] if run == 0 else [COMMAND, POLICY])
        assert UNMANAGED_COMMAND in capsys.readouterr().out
        assert (tmp_path / COMMAND).read_text() == "an older teax-completion\n"
        assert COMMAND not in manifest(tmp_path)

    install_commands(tmp_path, assistant="both", force=True)
    assert (tmp_path / COMMAND).read_bytes() == TEAX_COMPLETION.read_bytes()
    assert COMMAND in manifest(tmp_path)


@pytest.mark.parametrize(
    ("assistant", "claude"),
    [("both", True), ("claude", True), ("codex", False)],
)
def test_the_assistant_choice_decides_the_claude_entries(
    tmp_path: Path, assistant: str, claude: bool
) -> None:
    """Every choice installs the shared bundle and the policy; Claude's entries need Claude."""
    install_commands(tmp_path, assistant=assistant, force=False)

    bundle = [f".agents/skills/run-study/{name}" for name in BUNDLE_FILES]
    claude_entries = [ALIAS, COMMAND] if claude else []
    assert tree(tmp_path) == sorted([*bundle, *claude_entries, POLICY, MANIFEST])
    assert (tmp_path / ".claude").exists() == claude


@pytest.mark.parametrize("ours_first", [True, False], ids=["ours-then-init", "init-then-ours"])
def test_the_study_layer_and_agentic_mbse_init_coexist(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], ours_first: bool
) -> None:
    """Each installer keeps to its own manifest: neither prunes, asks about or claims the other's.

    Each order runs twice, so each installer also runs over the other's completed install.
    """
    alone = tmp_path / "alone"
    alone.mkdir()
    install_commands(alone, assistant="both", force=False)
    ours_alone = manifest(alone)

    target = tmp_path / "target"
    target.mkdir()
    order = ["ours", "init"] if ours_first else ["init", "ours"]
    for step in order * 2:
        capsys.readouterr()
        if step == "ours":
            theirs_before = read_if_present(target / installation.MANIFEST)
            skipped = install_commands(target, assistant="both", force=False)["skipped"]
            # Nothing of agentic-mbse's is asked about or kept back; only our own policy is kept.
            assert skipped in ([], [POLICY])
            assert read_if_present(target / installation.MANIFEST) == theirs_before
        else:
            ours_before = read_if_present(target / MANIFEST)
            assert init(target) == 0
            out = capsys.readouterr().out
            for ours in ("run-study", "teax-completion", "STUDY_POLICY", ".sysml-codegen"):
                assert ours not in out, out
            assert read_if_present(target / MANIFEST) == ours_before

    assert manifest(target) == ours_alone
    for relative in ours_alone:
        if relative == ALIAS:
            assert os.readlink(target / ALIAS) == "../../.agents/skills/run-study"
        else:
            assert (target / relative).read_bytes() == (alone / relative).read_bytes(), relative
    assert (target / POLICY).read_bytes() == POLICY_TEMPLATE.read_bytes()
    theirs = manifest(target, installation.MANIFEST)
    assert not [key for key in theirs if key in ours_alone or key == POLICY]
    agentic_skills = sorted(p.parent.name for p in get_skills_dir().glob("*/SKILL.md"))
    for skill in agentic_skills:
        assert (target / ".claude/skills" / skill / "SKILL.md").is_file(), skill


def test_no_asset_name_collides_with_what_agentic_mbse_ships() -> None:
    """Read from the installed agentic-mbse: its bundle names, which also name the Claude
    commands it retires, and the project paths its templates take."""
    agentic_bundles = {p.parent.name for p in get_skills_dir().glob("*/SKILL.md")}
    assert agentic_bundles, "agentic-mbse's installed distribution ships no skill bundles"
    ours = {p.parent.name for p in install.SKILLS.glob("*/SKILL.md")}
    ours |= {p.stem for p in install.COMMANDS.glob("*.md")}
    assert ours == {"run-study", "teax-completion"}
    assert ours.isdisjoint(agentic_bundles)

    agentic_documents = {dest for _, dest in [*USER_OWNED_TEMPLATES, *TOOL_OWNED_TEMPLATES]}
    assert {dest for _, dest in install.PROJECT_DOCUMENTS}.isdisjoint(agentic_documents)
    assert MANIFEST != installation.MANIFEST


def test_the_pinned_installer_api_passes(capsys: pytest.CaptureFixture[str]) -> None:
    assert install.INSTALLER_API_VERSION == _upstream_pins.INSTALLER_API_VERSION == "installer/v1"
    require_installer_api()
    assert capsys.readouterr().err == ""


@pytest.mark.parametrize("upstream", [None, "installer/v0"], ids=["missing", "different"])
def test_an_agentic_mbse_without_the_pinned_api_is_refused(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], upstream: str | None
) -> None:
    if upstream is None:
        monkeypatch.delattr(installation, "INSTALLER_API_VERSION")
    else:
        monkeypatch.setattr(installation, "INSTALLER_API_VERSION", upstream)

    with pytest.raises(SystemExit) as exit_:
        require_installer_api()

    assert exit_.value.code == 1
    err = capsys.readouterr().err
    assert "installer/v1" in err and INSTALLER_API_REVISION in err and repr(upstream) in err


@pytest.mark.parametrize("listing", [False, True], ids=["install", "list"])
def test_the_handler_checks_the_api_before_it_does_anything(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, listing: bool
) -> None:
    """Fails closed: an old agentic-mbse writes nothing and lists nothing."""
    from sysml_codegen.cli import cmd_install_commands

    monkeypatch.delattr(installation, "INSTALLER_API_VERSION")
    args = Namespace(directory=str(tmp_path), assistant="both", force=False, list=listing)
    with pytest.raises(SystemExit) as exit_:
        cmd_install_commands(args)
    assert exit_.value.code == 1
    assert list(tmp_path.iterdir()) == []


def test_the_command_installs_with_no_input(tmp_path: Path) -> None:
    """The subcommand as a user runs it, ``< /dev/null``, in a fresh process."""
    run = subprocess.run(
        [sys.executable, "-m", "sysml_codegen", "install-commands", str(tmp_path)],
        stdin=subprocess.DEVNULL, capture_output=True, text=True, check=False,
    )
    assert run.returncode == 0, run.stderr
    assert f"Created ({len(BUNDLE_FILES) + 2}):" in run.stdout
    assert f"  @ {ALIAS}" in run.stdout
    assert (tmp_path / MANIFEST).is_file()

    again = subprocess.run(
        [sys.executable, "-m", "sysml_codegen", "install-commands", str(tmp_path)],
        stdin=subprocess.DEVNULL, capture_output=True, text=True, check=False,
    )
    assert again.returncode == 0, again.stderr
    assert f"Preserved {POLICY}: it is this project's document; --force replaces it" in again.stdout
    assert f"Skipped, kept as they are (1):\n  . {POLICY}" in again.stdout
    assert "Created" not in again.stdout


def test_the_command_refuses_a_target_that_is_not_a_directory(tmp_path: Path) -> None:
    run = subprocess.run(
        [sys.executable, "-m", "sysml_codegen", "install-commands", str(tmp_path / "absent")],
        stdin=subprocess.DEVNULL, capture_output=True, text=True, check=False,
    )
    assert run.returncode == 1
    assert f"{tmp_path / 'absent'} is not a directory" in run.stderr
    assert not (tmp_path / "absent").exists()


def test_list_writes_nothing(tmp_path: Path) -> None:
    run = subprocess.run(
        [sys.executable, "-m", "sysml_codegen", "install-commands", str(tmp_path), "--list"],
        stdin=subprocess.DEVNULL, capture_output=True, text=True, check=False,
    )
    assert run.returncode == 0, run.stderr
    assert "run-study (workflow)" in run.stdout and "teax-completion" in run.stdout
    assert list(tmp_path.iterdir()) == []


def test_the_readme_names_the_revision_the_refusal_names() -> None:
    """O5 moves the minimum revision to agentic-mbse's merge commit; both places move together."""
    readme = (REPO_ROOT / "README.md").read_text()
    assert f"`{INSTALLER_API_REVISION}`" in readme and "`installer/v1`" in readme


def test_no_shipped_asset_names_a_machine_path() -> None:
    """Every asset ships into every project, so none may point into one machine's home."""
    offenders = [
        f"{path.relative_to(install.ASSETS)}:{number}"
        for path in sorted(install.ASSETS.rglob("*"))
        if path.is_file()
        for number, line in enumerate(path.read_text().splitlines(), start=1)
        if "/home/" in line or "/Users/" in line
    ]
    assert offenders == []
