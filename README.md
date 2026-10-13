# sysml-codegen

Parse SysML v2 models, resolve their modeled occurrences, and emit executable Python packages for TEAx. Both live models and sealed v6 snapshots use the same exact elaboration and projection authority. Unsupported model forms refuse with diagnostics. It also ships the study layer, which runs parameter studies over those packages (see [The study layer](#the-study-layer)).

## Installation

From this repository, with `agentic-mbse` checked out beside it:

```bash
uv pip install -e ../agentic-mbse
uv pip install -e ".[dev]"
```

With pip, use the same relative paths: `pip install -e ../agentic-mbse` and `pip install -e ".[dev]"`. Live parsing and snapshot capture require a valid `SYSIDE_LICENSE_KEY`.

## Generation

```bash
# Live models: needs a SysIDE license.
uv run sysml-codegen generate --models path/to/models --output path/to/output --package-name my_package

# Capture once with the license, then generate without it.
uv run sysml-codegen snapshot --models path/to/models --output path/to/instance_graph_snapshot.json
uv run sysml-codegen generate --from-snapshot path/to/instance_graph_snapshot.json --output path/to/output --package-name my_package
```

The generated package includes schemas, input JSON, module wrappers, implementations, pipeline YAML, and semantic/physical contracts. Preserve completed implementations with `--overwrite --preserve-handwritten`; use `--smart-regen` for signature-aware regeneration. Units written on values remain parser facts; declaration comments are human documentation and do not supply generated units.

## The study layer

sysml-codegen also ships the study layer: a `run-study` skill for Claude Code and Codex, a study-policy template, and the tools a study calls. A project that generates a package with sysml-codegen and runs it with teax can run a parameter study on it, from intake to a committed record, with nothing else copied in.

Install it at the project root:

```bash
uv run sysml-codegen install-commands .          # --assistant claude|codex|both (default both), --list, --force
```

It writes four things:

- `.agents/skills/run-study/`: the skill, its runbook, the record and annex templates, and the integration guide, with a `.claude/skills/run-study` link for Claude Code;
- `.claude/commands/teax-completion.md`, for Claude Code;
- `modeling_project/STUDY_POLICY.md`, from the policy template;
- `.sysml-codegen/install.json`, the install manifest. Commit it with the rest.

**Who owns what.** The skill files and the command are managed. A re-install refreshes an unmodified file and keeps an edited one (at a terminal it asks); `--force` replaces it. The study policy is the project's document: it is created once, and only `--force` writes it again. The installer is agentic-mbse's, on sysml-codegen's own manifest, so `agentic-mbse init` and `install-commands` leave each other's files alone, in either order.

**agentic-mbse revision.** `install-commands` needs agentic-mbse's installer API `installer/v1`, which first ships in agentic-mbse revision `d42c8b9`. It checks this before it writes anything and refuses with exit 1, naming that revision, when the installed agentic-mbse lacks it. No other command needs it.

**The tools.** Each runs as `sysml-codegen study <tool>`, or as `python -m sysml_codegen.study.<tool>`:

```bash
uv run sysml-codegen study indicators --package DIR --manifest FILE --groups FILE
uv run sysml-codegen study preflight gates --package DIR --manifest FILE --groups FILE --identity FILE --baseline-result FILE
uv run sysml-codegen study preflight clean --package DIR
uv run sysml-codegen study verify --package DIR --manifest FILE --identity FILE --store FILE
uv run sysml-codegen study integrate ...     # see the installed integration-guide.md
```

The installed runbook's "The tools" section gives every form, and `integration-guide.md` documents `integrate` and the `[tool.sysml-codegen.integrate]` table it reads from the project's `pyproject.toml`.

- **teax.** `verify` and `integrate` need teax's `simkit` importable. Set `TEAX_SIMKIT_PATH` to the simkit root, the directory that holds `simkit/`. `integrate` reads the teax revision there.
- **The project root.** Every path a study document cites is relative to the project root: `SYSML_CODEGEN_PROJECT_ROOT` when it is set, and otherwise the git work tree that contains `--package`. A tool refuses with exit 2, writing nothing, when the package is in no work tree and the variable is unset, or when the working directory is inside a different work tree from the package. In a monorepo whose top level is not the modeling project, set the variable.

## Development

```bash
uv run --extra dev pytest tests/
uv run --extra dev mypy src/
uv run --extra dev ruff check src/
```

The default suite excludes the real-TEAx lane. Full licensed acceptance requires zero license skips; a green unlicensed subset is not a full validation result. See [CLAUDE.md](CLAUDE.md) for environment commands and [the architecture overview](docs/architecture/overview.md) for the generation route.

The real-TEAx lane (`pytest tests/execution/ -m execution`) needs TEAx's evidence schema v3 numeric-publication capability. Numeric single-output and multi-output values must reach study evidence under their existing exit keys, including dependent arithmetic and reopened-study checks. Boolean values retain numeric 0/1 representation; structured constraint outputs are excluded from numeric evidence.

Bind immutable dependencies with `CODEGEN_EXECUTION_PROVENANCE` and `TEAX_SIMKIT_PATH` as required by [the execution fixture](tests/execution/conftest.py). Live tests also need the license. Evidence schema v3 starts a new study lineage; querying an old store cannot restore omitted values. The runtime fix changes no generated-package representation.

## Dependencies and license

`agentic-mbse` supplies the SysIDE adapter, neutral model facts and the installer `install-commands` uses; Jinja2 renders templates; Pydantic defines schemas; PyYAML writes pipeline configuration. MIT license.
