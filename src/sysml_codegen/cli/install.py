"""``sysml-codegen install-commands``: install the study layer into a project.

What it installs, and who owns each piece afterwards (design DD4-DD6, Appendix D):

- **Managed assets**: the ``run-study`` skill bundle at ``.agents/skills/run-study/``, with a
  ``.claude/skills/run-study`` link for Claude Code, and the ``teax-completion`` Claude command.
  They go through agentic-mbse's ``Installer`` on sysml-codegen's own manifest,
  ``.sysml-codegen/install.json``. So an unmodified file is refreshed, an edited one is kept
  (or asked about at a terminal), and agentic-mbse's ``init`` never sees them as its own.
- **Project documents**: the study policy, ``modeling_project/STUDY_POLICY.md``. It is created
  when absent and is the project's from then on. It stays out of the manifest, and only
  ``--force`` writes it again.

agentic-mbse's installer is imported only inside these functions, and the CLI imports this
module only inside the ``install-commands`` handler. An agentic-mbse without the pinned installer
API therefore breaks this one subcommand, loudly, through :func:`require_installer_api`.
"""

from __future__ import annotations

import sys
from collections.abc import Mapping
from pathlib import Path

from sysml_codegen._upstream_pins import INSTALLER_API_VERSION

#: sysml-codegen's install manifest in the project, beside agentic-mbse's own.
MANIFEST = ".sysml-codegen/install.json"
ASSETS = Path(__file__).resolve().parents[1] / "assets"
SKILLS = ASSETS / "skills"
COMMANDS = ASSETS / "commands"
PROJECT_TEMPLATES = ASSETS / "project_templates"
#: Each project document: the template it starts from, and where the project keeps it.
PROJECT_DOCUMENTS = (("STUDY_POLICY.md.template", "modeling_project/STUDY_POLICY.md"),)
#: The assistants each ``--assistant`` choice installs for.
RUNTIMES = {"claude": ("claude",), "codex": ("codex",), "both": ("claude", "codex")}
#: Claude's alias of a skill bundle is a relative link to the shared folder, as agentic-mbse's
#: ``init`` makes it by default. ``install_bundle`` takes "symlink" or "copy".
LINK_MODE = "symlink"
#: The first agentic-mbse ``main`` revision whose installer carries ``INSTALLER_API_VERSION``,
#: the merge of agentic-mbse PR #24. ``README.md`` names the same revision; a test holds the two
#: together.
INSTALLER_API_REVISION = "d42c8b9"
#: The answers to a conflict, as agentic-mbse's installer names them.
CHOICES = {"s": "skip", "b": "backup", "o": "overwrite", "S": "skip_all", "O": "overwrite_all"}


def require_installer_api() -> None:
    """Exit 1, naming the agentic-mbse revision needed, unless its installer API is the pinned one.

    The check reads the installed agentic-mbse's ``INSTALLER_API_VERSION``, which names the whole
    installer surface this module calls. A missing installer module counts as a missing API.
    """
    import agentic_mbse

    try:
        import agentic_mbse.cli.installation as installation
    except ModuleNotFoundError as error:
        if error.name != "agentic_mbse.cli.installation":
            raise
        provided = None
    else:
        provided = getattr(installation, "INSTALLER_API_VERSION", None)
    if provided != INSTALLER_API_VERSION:
        print(
            f"install-commands: needs agentic-mbse's installer API {INSTALLER_API_VERSION!r}, "
            f"first in agentic-mbse revision {INSTALLER_API_REVISION}. The agentic-mbse at "
            f"{Path(agentic_mbse.__file__).parent} provides {provided!r}. Install agentic-mbse "
            "at that revision or later, then re-run.",
            file=sys.stderr,
        )
        raise SystemExit(1)


def skill_bundles() -> list[Path]:
    """The shipped skill bundles: each folder under the assets' skills that holds a SKILL.md."""
    return sorted(entry.parent for entry in SKILLS.glob("*/SKILL.md"))


def list_assets() -> list[str]:
    """The listing ``--list`` prints: skills, Claude commands and project documents."""
    from agentic_mbse.cli.installation import frontmatter

    lines = ["Skills, for Claude Code and Codex (.agents/skills/, linked from .claude/skills/):"]
    for bundle in skill_bundles():
        meta = frontmatter(bundle / "SKILL.md")[0]
        description = " ".join(str(meta["description"]).split())
        lines.append(f"  - {bundle.name} ({meta['metadata']['kind']}): {description}")
    lines.append("Claude commands (.claude/commands/):")
    lines.extend(f"  - {command.stem}" for command in sorted(COMMANDS.glob("*.md")))
    lines.append("Project documents, created once and then the project's own:")
    lines.extend(f"  - {relative} (from {template})" for template, relative in PROJECT_DOCUMENTS)
    return lines


def prompt_decision(relative: str, *, managed: bool) -> str:
    """How to treat ``relative``, which differs from both the shipped file and what was installed.

    ``managed`` says whether sysml-codegen's manifest records the file. Without a terminal on
    standard input the answer is "skip", and the reason is printed. At a terminal it asks, and
    returns one of agentic-mbse's decide answers.
    """
    if managed:
        reason = "it was edited after sysml-codegen installed it"
    else:
        reason = "it differs from the shipped file and is not in the install manifest"
    if not sys.stdin.isatty():
        print(f"Preserved {relative}: {reason}; re-run interactively or with --force to replace it")
        return "skip"
    print(f"\n{relative}: {reason}.")
    print("  [s]kip      - keep this version")
    print("  [b]ackup    - save it beside the file as .backup, then install the shipped one")
    print("  [o]verwrite - install the shipped one")
    print("  [S]kip all  - keep every such file")
    print("  [O]verwrite all - install every shipped file, like --force")
    while True:
        answer = input("  Choice [s/b/o/S/O]: ").strip()
        if answer in CHOICES:
            return CHOICES[answer]
        print("  Please enter s, b, o, S or O.")


def install_commands(target: Path, *, assistant: str, force: bool) -> dict[str, list[str]]:
    """Install the study layer into ``target`` and return what was done, by installer action.

    ``assistant`` is a key of :data:`RUNTIMES`. The keys of the result are the installer's:
    created, updated, skipped, backed_up, symlinked and removed. A preserved project document is
    listed as skipped.
    """
    from agentic_mbse.cli.installation import Installer, install_bundle

    def decide(relative: str) -> str:
        return prompt_decision(relative, managed=relative in installer.files)

    installer = Installer(target, force=force, decide=decide, manifest=MANIFEST)
    runtimes = RUNTIMES[assistant]
    for bundle in skill_bundles():
        install_bundle(installer, bundle, runtimes=runtimes, link_mode=LINK_MODE, dev=False)
    if "claude" in runtimes:
        for command in sorted(COMMANDS.glob("*.md")):
            relative = f".claude/commands/{command.name}"
            installer.write(relative, command.read_bytes(), source=command)
    for template, relative in PROJECT_DOCUMENTS:
        if not installer.parents(relative):
            continue
        path = target / relative
        exists = path.exists() or path.is_symlink()
        if exists and not force:
            print(f"Preserved {relative}: it is this project's document; --force replaces it")
            installer.actions["skipped"].append(relative)
            continue
        if path.is_symlink():
            path.unlink()
        path.write_bytes((PROJECT_TEMPLATES / template).read_bytes())
        installer.actions["updated" if exists else "created"].append(relative)
    installer.save()
    return installer.actions


def summarize(target: Path, actions: Mapping[str, list[str]]) -> list[str]:
    """The report a run prints: each action's entries, under a heading that counts them."""
    lines = [f"Installed sysml-codegen's study layer in {target}"]
    for action, heading, mark in (
        ("symlinked", "Symlinked", "@"),
        ("created", "Created", "+"),
        ("updated", "Updated, rewritten with the shipped bytes", "~"),
        ("backed_up", "Backed up, originals saved beside them as .backup", "B"),
        ("removed", "Removed, retired and unmodified", "-"),
        ("skipped", "Skipped, kept as they are", "."),
    ):
        if actions[action]:
            lines.append(f"{heading} ({len(actions[action])}):")
            lines.extend(f"  {mark} {entry}" for entry in actions[action])
    return lines
