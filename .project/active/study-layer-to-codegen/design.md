# Design: Move the study layer to sysml-codegen (WRAP-SPLIT Item 3)

**Status:** Approved for planning by the orchestrator, 2026-10-12, after one review round (Revise, applied; M1–M4 checked by the orchestrator, no re-review)
**Owner:** Reid W
**Created:** 2026-10-12
**Branch:** `study-layer-to-codegen` at `4960d6b` (first draft committed at `4533510`; spec amended at `4960d6b`)
**Run:** non-interactive design stage for the agentic-mbse orchestrator (`/_my_orchestrate`, 2026-10-12)

## Overview

The study layer moves into one new subpackage, `sysml_codegen.study`, and one skill bundle that `sysml-codegen install-commands` installs through agentic-mbse's installer. The code moves byte-faithfully except for the closed list B1–B12. Almost every item on that list comes down to replacing "where this file sits" with three named roots and one target-written declaration.

**Numbering.** "B1"–"B12" always mean the spec's closed list. The design's own bets are KB1–KB6 and its decisions are DD1–DD20. The spec's settled decisions are D6–D11.

## Related Artifacts

- **Spec:** `.project/active/study-layer-to-codegen/spec.md`. It has twelve criteria, the closed list B1–B12 (B12 added at `4960d6b`), and decisions D6–D11.
- **Reviews:** `spec-review.md` (Revise, applied) and `design-review.md` (Revise, applied in this revision).
- **Briefs:** `briefs/{spec,spec_review,spec_revision,design,design_review,design_revision}.md`. `design_revision.md` holds the orchestrator's decisions on the design review.
- **Product-lens ledger:** `product-lens.md`. The design-stage lens ran during the review (findings design-F1 to F5), and this revision disposes of all five (§ Revision 2026-10-12).
- **Epic and ledger (agentic-mbse, staged at `ac5fb1a`):** `.project/backlog/epic_wrap-split.md` Item 3; `.project/active/wrap-split-migration-ledger.md` (Item 2's row format).
- **Precedent:** agentic-mbse `.project/completed/20261012_goal-layer-port/design.md` (Appendix C ledger rows, Appendix D rehearsal and dry run) and `evidence/fusion-tea-runbook.md`.
- **Staged sources (gitignored):**
  - `.orchestrate-logs/src/fusion-tea@b06585709/`: tools, skill, policy, guide, tests, `CONSUMER_SURFACE.md`, `CONSUMER_ATTRIBUTES.md` and one committed record;
  - `.orchestrate-logs/src/agentic-mbse@main/`: `src/agentic_mbse/cli/installation.py` and `CLAUDE.md`.
- **Repackaging check:** `.orchestrate-logs/scratch/repack-check/{check.py,output.txt}`.
- **Decision records:**
  - `.project/adr/0007-agentic-mbse-owns-neutral-facts-codegen-owns-rendering.md` (dependency direction; the byte-faithful lesson);
  - `.project/adr/0008-cross-repo-merges-use-merge-commits.md` (merge order).
- **Product promises:** `.project/product/0001-design-search-free-variation.md`, `.project/product/0004-product-identity-parse-walk-emit.md`.

## The Point

A modeling project that uses sysml-codegen and teax gets the whole study capability by installing sysml-codegen and running `sysml-codegen install-commands`. The capability is the `run-study` skill with its runbook and record template, a study-policy template, and the tools those steps call. The project can then run a study from intake to a committed record, and hand it to a second agent, with nothing copied from fusion-tea.

- [OWNER] (epic header, 2026-10-06): the study layer ships from sysml-codegen, which owns the generated-package contracts the tools read. [OWNER-VERBATIM] "ported and generalized … installed like everything else" (research `:18`).
- [AGENT] (orchestrator Align reading, uncontested): the bar is a working capability in a fresh target, not copied files.
- [NEED] The owner's shape survives:
  - a lightweight skill, a runbook, a policy rulebook and tools;
  - indicators inform and never gate;
  - intake is collaborative;
  - one skill serves the executing and administrator roles;
  - an axis nothing pushes back on is surfaced as a sign the model is underdeveloped.
- [NEED] fusion-tea loses no information. [INFERRED] Study semantics change only by the closed list B1–B12. This is ADR-0007's lesson: "A boundary move is byte-faithful or it is a behavior change to be reviewed as one."
- [AGENT] (D8, SC8) `integrate` must judge any target, not just fusion-tea. What a return says a gate examined must be what that target's gate examined (B12).
- It ladders up to P-001: "the study layer owns exploration and decisions" over the generated package.

## Premise conflicts (decided)

**1. The installer dependency guarantee.** Accepted by the orchestrator on 2026-10-12. The spec's L3-9 requirement is amended at `4960d6b`. See DD5.

- **Why not a version bound.**
  - The v6 snapshot loader refuses a snapshot whose `authority.agentic_mbse_version` differs from the running agentic-mbse (`src/sysml_codegen/snapshot/envelope.py:459-473`). All 22 committed v6 fixtures record `0.1.3`.
  - This repo pins that version as a reviewed upstream authority (`_upstream_pins.py:36`; `tests/unit/test_package_metadata.py:19,32-33`).
  - fusion-tea requires `agentic-mbse[...]==0.1.3` exactly (`pyproject.toml:8`), and its gate-1a producer pins `VERSIONS["agentic-mbse"] = "0.1.3"` (`tests/test_dependency_provenance.py:28-32`).
  - No consumer resolves agentic-mbse by version (fusion-tea `pyproject.toml:36`; this repo's `pyproject.toml:63-64`).
- **The guarantee instead.** agentic-mbse exports `INSTALLER_API_VERSION`. sysml-codegen pins it in `_upstream_pins.py`, which is the existing pattern beside `SEMANTIC_EVIDENCE_API_VERSION` (`_upstream_pins.py:39`).
- **It cannot break other commands.** `install-commands` reads the constant lazily, inside its own handler, and refuses to install without it. An older agentic-mbse therefore cannot break `generate` or any other subcommand.

**2. A smaller correction.** The spec says fusion-tea's pin `adbef75` predates Item 1's native installer. fusion-tea's provenance test says the native skill distribution advanced the pin to `adbef75` (`tests/test_dependency_provenance.py:13-14`). That revision lacks this item's API either way.

**3. The fixture.** Accepted. `tests/fixtures/wi014_toy` was "imported verbatim" from fusion-tea WI-014 (`PROVENANCE.md:3`), so it fails SC4's "no fusion-tea file" rule. DD13 writes a new neutral model.

**4. `integrate` without teax.** Accepted, and the spec's B9 and SC3 are amended. `integrate` writes a return document on every exit path once the seam has started. When teax is missing, that return is its usual `BLOCKER`: gate 0, `could_not_run`, `env-missing`, detail naming teax. No producer runs.

The exits that write no document are invocation failures before the seam starts. An argparse usage error already does this today, with exit 2. B1 adds two: a missing project root and a conflicting one (DD2), both also exit 2. `verify` writes nothing without teax.

**5. Declared gates claimed fusion-tea's checks.** Raised by the review (M1) and decided by the orchestrator as new closed-list item B12. The `checked` text of rows 1a and 5 comes from the target's declaration, and there is no default. fusion-tea declares today's strings, so its returns stay identical (DD8).

## Research Findings

- **Root dependence (Evidence A, confirmed by reading).**
  - Project-root sites: `manifest.py:57-69`, `common.py:62`, `verify.py:93`, `identity.py:225`, `integrate.py:292, :311, :824, :1234`, and every `repo_relative_posix` call.
  - Tool-home sites: `manifest.py:35-41, :149-162`, `common.py:41-57`, `indicators.py:862`, and the `TOOL_SOURCE_FILES` tuples (`preflight.py:66-74`, `verify.py:60-67`, `integrate.py:89-97`).
  - `read_coverage.py:94` uses `Path(__file__).parents[1]` as a read root.
  - `repo_relative_posix` renders a path outside the root with `..` segments (`manifest.py:62-69`). So a wrong root never raises an error; it produces plausible but wrong paths.
- **fusion-tea pins cwd-independence twice.** `test_output_contract.py:232-240` runs `indicators` from `tmp_path`, outside the repository, and requires identical bytes. `test_identity.py:105-111` calls `chdir` in-process and requires the same identity document.
- **Schemas fix the shapes.** `verification_summary.v1.schema.json:39-43` says `command` is repo-relative so that "two agents produce identical bytes for identical facts".
- **agentic-mbse's installer** (`installation.py`, staged):
  - `__init__` merges both manifests into one `files` map (`:104-107`); `save()` writes `MANIFEST` (`:286-295`);
  - pruning stays inside the bundle being installed and inside the installer's own manifest (`:206-230`);
  - legacy-link adoption fires only for absolute links into an agentic-mbse checkout (`:47-68`);
  - the bundle install is the loop body at `:434-440`.
- **Conformance pins the CLI touches** (`tests/conformance/test_public_authority_switch.py`):
  - `:216-240` fails if any `sysml_codegen` module reachable from `sysml_codegen.cli` mentions `os.environ`, `os.getenv` or `getenv(` in its source (`:527-539`). Reachability is an AST walk that sees imports inside functions too (`:175-185`, `:541-563`).
  - `:243-254` pins `cli.__all__` by value, `CODEGEN_COMMANDS` included.
  - The moved code reads the environment in exactly two places: `integrate.py:291` and `read_coverage.py:95-96`.
- **Gate claims.** `GATES` fixes each row's `checked` text (`integrate.py:189-200`), and every row copies it into the return (`:609-619`, `:623-639`, `:1456-1465`). `unasked` builds its blocker from the gate's own `producer` (`:244-255`), so a gate table with `not declared` rows yields `not declared` rows in the return.
- **Read coverage watches the route's imports.**
  - `run_route` activates the observer before it imports the route module (`read_coverage.py:253-257`).
  - Eight fusion-tea `study_route.py` modules import `scripts.study` at module top (`CONSUMER_SURFACE.md:43, :50, :57, :62, :67, :72, :89, :97`).
  - All eight call `identity.build_sealed`, and no consumer calls `build_effective` (`CONSUMER_ATTRIBUTES.md:20`).
- **teax location.** The gate-0 probe prints `simkit.__file__`'s parent (`integrate.py:143`). For a non-editable teax in the project's `.venv`, that parent is `site-packages`, inside the target's own git work tree.
- **Gate 4's snapshot rule.** Gate 4 requires exactly one `*.snapshot.json` beside the models root (`integrate.py:1056-1073`). This repo's `CLAUDE.md:31` and all 22 fixtures use `instance_graph_snapshot.json`, which that glob does not match.
- **Lanes.**
  - Default run: `-m "not execution"` (`pyproject.toml:46-50`). License-gated tests use `requires_license` (`tests/conftest.py:20-34`).
  - The execution lane uses `CODEGEN_EXECUTION_PROVENANCE` and `TEAX_SIMKIT_PATH` (`tests/execution/conftest.py:15-24`).
  - `tests/execution/test_numeric_evidence_teax.py:33-86` runs a full simkit study on a generated package; it is the fixture route's precedent.
- **Fixtures.** No generated package is committed anywhere. 22 fixtures commit a v6 snapshot. Capture is deterministic (`envelope.py:44-45`), and live and snapshot generation agree (`tests/conformance/test_exact_route_generated_package.py`).
- **fusion-tea consumers.**
  - `CONSUMER_ATTRIBUTES.md` names 32 distinct module attributes (Appendix C), the 17 package names and 20 key prefixes SC5's test needs, and the pre-move documents SC7 needs.
  - `replay.py:161` builds `scripts/study/verify.py` as a file path.
- **fusion-tea tests.**
  - Its 51 study test files classify as 15 package-agnostic whole, 12 partly agnostic and 24 fusion-specific (Appendix F).
  - Fifteen of them, plus the spine test, reference moved internals or paths. Appendix H3 lists them.
- **verify's oracle contract** is `operand_bindings()` → `{constraint_id: {operand: {"kind": "input" | "channel", "key": ...}}}` (`verify.py:141-172`).

## Core Concept

The study layer becomes one subpackage, `sysml_codegen.study`, plus a skill bundle that the existing `install-commands` delivers through agentic-mbse's installer.

Every change the closed list allows comes from one fact: the original code located everything relative to where its own file sat, and installed code cannot. So the design names three roots once, in one module (`study/roots.py`). It sends every former `__file__` question to the root it actually meant:

- **project root** — for every path a document cites, and for the declaration. It is the git work tree that contains the package the tool was given. `SYSML_CODEGEN_PROJECT_ROOT`, or an in-process override for library callers, can name it instead.
- **tool home** — for tool identity. It is the directory that holds the installed `sysml_codegen` package.
- **teax root** — for anything that names teax's revision or permits teax's files: `TEAX_SIMKIT_PATH`, and nothing else.

`roots.py` is also the one module in the study package that reads the environment.

Some facts fusion-tea hard-coded about itself become one declaration table the target writes in its own `pyproject.toml`: its two repo-scope test files and what each checks, its extra environment variables, its costing distribution, and its backup prefix.

Installation reuses agentic-mbse's `Installer` with a separate manifest.

fusion-tea adopts later:

- its local copies become module aliases that pin its root in-process;
- its nine route modules import the installed package directly;
- every committed record stays valid as written.

**Why this is right, not just working.**

- The root split is the minimum change that makes installed code correct, and keeping it in one module makes it auditable.
- Anchoring the root to the package, not the working directory, makes the wrong-root case a refusal instead of quietly wrong paths.
- The declaration turns the only target-specific facts `integrate` holds into data the target owns, including the claim about what each repo gate checked.
- Reusing the installer keeps one implementation of the ownership rules.

Everything else stays byte-faithful, and SC12 proves it.

## Key Bets

- **KB1.** A study target keeps the package it studies inside a git work tree, and the work tree containing the package is the project the user means. The tools already require git: preflight's clean gate and integrate's audited-work commit.
  - *If false (a monorepo whose top level is not the modeling project) →* the tools run, but they cite paths relative to the top level and read the declaration from the top level's `pyproject.toml`. Nothing refuses this, because outside paths render with `..`. The guide and the runbook state the remedy: set `SYSML_CODEGEN_PROJECT_ROOT`.
  - **What is refused (exit 2):** a package in no work tree with no override set, and a working directory inside a different work tree from the package.
- **KB2.** agentic-mbse's ownership rules do not depend on which manifest file they persist to, and its own installs never touch paths absent from its own manifest.
  - *If false →* re-running one installer removes, or prompts for, the other's files, and SC2 fails. Coexistence tests in both repositories check this in both orders.
- **KB3.** A moved tool's output depends only on its inputs, the project root, the tool home and teax. Nothing else in fusion-tea's layout leaks into a document.
  - *If false →* SC12 finds an unlisted difference, and the orchestrator must add a closed-list item.
- **KB4.** A neutral model of about 40 lines, generated by this branch, runs on stock teax through the stock study lifecycle, as `test_numeric_evidence_teax.py` does.
  - *If false →* verify and integrate's `CANDIDATE` are unreachable on the fixture. Cut 2 applies, and verify keeps only negative-case coverage.
- **KB5.** fusion-tea's consumers depend only on names, signatures and project-root-relative behavior, with one exception the review found. Route modules run under read coverage, so the files their imports open matter (M2). Rewriting the nine route modules' imports handles that; module aliases cover every other consumer.
  - *If false →* adoption needs more consumer rewrites. Run C of the rehearsal shows it before merge, because it runs `integrate` and the gate-7 driver on a real fusion-tea package (Appendix H3).
- **KB6.** Nobody resolves agentic-mbse by version: every install is by git revision or path.
  - *If false →* a version bound becomes worth its snapshot cost (premise conflict 1).

## Key Decisions

- **DD1 · Package name and layout (OQ4).**
  - The package is `src/sysml_codegen/study/`: the eight moved modules, four new ones (`roots`, `census`, `declarations`, `__init__`), and `schemas/` with its seven files byte-identical.
  - The installable files live in `src/sysml_codegen/assets/`. Tool paths read `sysml_codegen/study/<tool>.py`.
  - *Rejected:* a top-level `studytools` package (a second import root in one wheel); `sysml_codegen.tools.study` (an extra level for one package).
- **DD2 · Project root (OQ3; review S1 and m1).** The first rule that applies wins:
  1. An in-process override, `roots.use_project_root(path)`. Only library callers set it; fusion-tea's wrappers are the one known caller.
  2. `SYSML_CODEGEN_PROJECT_ROOT`.
  3. On the CLI, the git work tree containing the tool's anchor path. In a library call, the git work tree of the working directory.

  **The anchor is the package the tool was given:**

  - `indicators`, `preflight gates`, `preflight clean` and `verify` anchor on `--package`.
  - `integrate` anchors on its single `--package`. When `--package` is absent or repeated, gate 0 rejects the request before judging anything, and the working directory's work tree anchors only the citations in that rejection.
  - The anchor is the nearest existing ancestor of the given path, so a missing package still fails where and how it failed before, with the same exit code.

  **What is refused.** Exit 2, a stderr message naming both paths, and no document:

  - the anchor is in no work tree and neither override is set;
  - the working directory is inside a different git work tree from the anchor.

  A working directory outside every work tree is not a conflict, which keeps fusion-tea's tmp-cwd determinism case working.

  **When an override applies.** No work-tree check runs. A package outside the root renders with `..`, as at `b06585709`, which keeps B1's "the same project gives the same paths".

  **Pinning and caching.**

  - `require_project_root(prog, anchor)` resolves once at CLI entry and pins the result in-process.
  - `integrate` exports the pinned root to its producers as `SYSML_CODEGEN_PROJECT_ROOT`.
  - The declaration is read from this root.
  - The library default is cached per (variable value, working directory).

  `roots.TOOL_HOME = Path(__file__).resolve().parents[2]`. That is the one place where `__file__` is right.

  - *Rejected:*
    - the working directory alone, because output varies with it;
    - the git top level of the working directory (the first draft), which silently gives a wrong root when an agent stands in another repository;
    - the nearest `pyproject.toml` that has a `[tool.sysml-codegen]` table, which leaves an undeclared target with no root at all;
    - a `--project-root` flag on four parsers, which changes every `command` argv.
- **DD3 · Tool CLI shape (OQ2; review M4 and m8).**
  - `sysml-codegen study <tool> [args]` lives in `cli/study.py`. Its `tool` positional uses `choices=("indicators", "preflight", "verify", "integrate")`, and `argparse.REMAINDER` passes the rest unchanged to `<tool>.main(argv)`.
  - `cmd_study` imports the four tool modules with static import statements inside the function. Startup stays fast, and the conformance walker still sees the imports.
  - `python -m sysml_codegen.study.<tool>` is equivalent.
  - `integrate` launches its producers and the generator with `sys.executable -m` (B3).
  - `tool.path`, `verify`'s `command[0]`, integrate's `command[0]` and `SEAM_PATH` all equal the tool-path literal (B2).
  - *Rejected:* four console scripts; `python -m` only; recording the invocation form in `command[0]`, which breaks byte-determinism.
- **DD4 · Installer mechanism (OQ1; review S4).**
  - Reuse agentic-mbse's `Installer` through a small API change (Appendix B): `manifest=`, `install_bundle()`, and `INSTALLER_API_VERSION`.
  - sysml-codegen keeps its own manifest at `.sysml-codegen/install.json` and calls `install_bundle(..., runtimes, link_mode="link", dev=False)`. `link_mode` and `dev` are constants on this side.
  - `cli/install.py` is imported only inside the `install-commands` handler, and it imports `agentic_mbse.cli.installation` only inside its functions.
  - *Rejected:* a standalone installer (a second implementation of the ownership rules); subclassing (couples to internals); a shared manifest (agentic-mbse would retire `run-study`).
- **DD5 · Dependency guarantee (OQ1; premise conflict 1, accepted).**
  - No version bump. The bound stays `agentic-mbse>=0.1.3,<0.2`.
  - `_upstream_pins.INSTALLER_API_VERSION = "installer/v1"` is checked in two places: by `tests/conformance/test_upstream_pins.py`, and at handler start by `require_installer_api()`. The latter reads `getattr(installation, "INSTALLER_API_VERSION", None)`; on a mismatch it exits 1, naming the agentic-mbse revision needed.
  - The version string covers the whole surface sysml-codegen calls:
    - `Installer(target, *, force, decide, manifest)`, with the decide vocabulary `skip`, `overwrite`, `backup`, `skip_all` and `overwrite_all`;
    - `parents`, `write` and `save`;
    - `actions`, with its keys `created`, `updated`, `skipped`, `backed_up`, `symlinked` and `removed`;
    - `install_bundle` and `frontmatter`.
  - `README.md` names the minimum agentic-mbse revision (the merge SHA) beside `installer/v1`. The SC1 transcript records the revision installed.
  - *Rejected:* bumping to 0.1.4 with a raised bound (premise conflict 1).
- **DD6 · Assistants and ownership (review S4 and m6).**
  - `--assistant {claude,codex,both}` defaults to `both`. `teax-completion` installs when `claude` is selected.
  - `modeling_project/STUDY_POLICY.md` is a project document. It is created when absent and otherwise untouched; `--force` replaces it. It stays out of the managed manifest.
  - A noninteractive conflict answers `skip`.
  - A `teax-completion.md` that today's installer left behind has no manifest entry. It is adopted only if its bytes equal the shipped file. Otherwise every noninteractive run preserves it and prints: "Preserved .claude/commands/teax-completion.md: it differs from the shipped file and is not in the install manifest; re-run interactively or with --force to replace it".
  - `.sysml-codegen/install.json` is tracked in the target, like `.agentic-mbse/install.json` in fusion-tea.
  - A test asserts that no asset name collides with agentic-mbse's shipped skill or command names, read from the installed agentic-mbse distribution.
- **DD7 · Skill files in the wheel; the CLI's public API (review M4).**
  - The assets live under `src/sysml_codegen/assets/`. `claude/commands/teax-completion.md` moves there, and `get_commands_dir()` and `CODEGEN_COMMANDS` are deleted.
  - `cli.__all__` drops `CODEGEN_COMMANDS`, which was the old installer's file list and is now the assets tree. It gains `cmd_study`, a dispatcher that constructs nothing. Appendix F names the test edit.
  - *Rejected:* `force-include` of a repo-root directory; `importlib.resources` traversal.
- **DD8 · Target declarations (OQ5; B5, B12; review M1, m4, m7).** The table is `[tool.sysml-codegen.integrate]` in the project root's `pyproject.toml`:
  - one sub-table per repo gate, `gates.pinned-packages` and `gates.model-family-spine`, each with two required keys:
    - `target`: a project-relative pytest target, optionally `path::node`;
    - `checked`: the text the return states that this gate examined (B12);
  - `environment`: extra variables gate 0 sweeps;
  - `record-distributions`: toolchain key → distribution;
  - `backup-prefix` (B10).

  **Validation is strict.**

  - Unknown keys, a gate without `checked`, a non-string value, or a target that is absolute or normalizes outside the project root are all malformed. A malformed declaration blocks at gate 0 with `input-invalid`. That outcome is new and is named under B5 and B12.
  - There is no default `checked` text.
  - Rows 1a and 5 of an undeclared gate carry `producer: "not declared"` and `checked: "not declared"`, and the gate raises `unasked` (D8).

  **Where it lives during a run.** `run()` loads the declaration and builds the gate table before anything else. `SequenceState` carries both. `gate_rows` and `build_return` take the table.

  **The guide** documents what each repo gate is meant to establish. fusion-tea's declaration reproduces today's rows byte for byte (Appendix D).

  - *Rejected:* a manifest field (the schema is byte-identical and strict); CLI flags (a repository property); a dedicated file; a default `checked` text (it would claim a check nobody declared).
- **DD9 · Census home (B11).**
  - `census.by_entry_type(package_root) -> dict[str, set[str]]` is fusion-tea's helper verbatim (`test_model_family_spines.py:174-182`).
  - `integrate.rederived_census` keeps its name and calls it.
  - *Rejected:* a typed version in `sysml_codegen.contracts`. Pydantic could refuse what the original accepted.
- **DD10 · teax discovery (OQ6; B7; review M3).**
  - `TEAX_SIMKIT_PATH`, this repo's lane variable, names a simkit root. It is the only source of a teax revision and the only teax root read coverage permits.
  - `integrate` prepends it to its producers' `PYTHONPATH`.
  - **Gate 0.** When the variable is set, its directory must hold `simkit/__init__.py` and the probe must land inside it. When it is unset, the probe must still succeed, because producers need simkit.
  - **Gate 1b**, in order:
    1. no expected revision → `unasked`, as today;
    2. `TEAX_SIMKIT_PATH` unset → `could_not_run`, `env-missing`, naming the variable;
    3. git cannot read HEAD there → `could_not_run`, as today;
    4. compare the revisions.
  - **Toolchain block.** `teax_revision` comes from the variable, or is `null` without it. `teax_module_path` comes from the probe, as today.
  - **Why gate 1b blocks, not gate 0.** Gate 0 sweeps what producers read. Gate 1b's comparison is the seam's own, like its unasked expectation.
  - `verify` keeps importing from the environment and raises a named teax error (B9).
  - *Rejected:*
    - the probe location as a fallback, because it returns the target's own HEAD when teax is installed in the project's `.venv`;
    - proving a checkout with `git ls-files`, which is more mechanism for a case the variable covers;
    - `STOP_PARSER_TEAX_ROOT`, a fusion-tea name;
    - a checkout-root variable plus the teax-internal `packages/teax-simkit` suffix.
- **DD11 · Record, annex and log locations (OQ7).**
  - Each studied package has one *studies directory*, named in the study policy's § Locations. It holds `ANNEX.md`, `DISCOVERY_LOG.md` and one `<study-id>/` per record.
  - fusion-tea's `exploration/<pkg>/studies/` becomes its policy's entry.
  - *Rejected:* a fixed root `studies/`; deriving the directory from the package path.
- **DD12 · Record checks (OQ8; review S6).**
  - No shipped check in this item. Runbook steps 14 and 15 each carry **Check:** lines the executor runs (Appendix I).
  - SC4's agent runs those installed lines and records what each printed before the evidence script `evidence/dry-run/check_record.py` runs. Any disagreement between the two is a finding.
  - A backlog follow-up ships the script as `sysml-codegen study check-record`.
  - *Rejected:* shipping it now; an installed pytest template.
- **DD13 · Fixture (OQ9).**
  - A new neutral pump-station model, `tests/fixtures/study_station/`, with a generated package and all study inputs (Appendix E).
  - `synthetic_pkg` moves for the indicators-only tests.
  - *Rejected:* extending `synthetic_pkg`; `wi014_toy`.
- **DD14 · fusion-tea adoption (OQ11; review M2 and m1).**
  - **Wrappers.** Each `scripts/study/<m>.py` and `scripts/integrate.py` becomes a module alias.
    - It calls `roots.use_project_root(...)` with fusion-tea's root, computed from its own location (`parents[2]`, or `parents[1]` for `scripts/integrate.py`). The call pins, overwriting any earlier value, because the wrapper's location is what `__file__` meant before.
    - It never touches `os.environ`.
    - Executed as `__main__`, by path or with `-m`, it calls `main()`. Otherwise it replaces itself in `sys.modules`.
  - **Route modules.** Runbook step 5 rewrites the nine `study_route.py` imports from `scripts.study` to `sysml_codegen.study`, which keeps read coverage within B8's permitted sources.
    - No sealed identity changes. All nine routes call `build_sealed`, whose digest is the package's sealed executable fingerprint with no adapter sources (`identity.py:135-159`).
    - The route files' own bytes do change. Any committed digest over route sources, such as a read-coverage receipt in committed integration evidence, would differ on a re-run, but stays valid as written history.
    - Step 8b (Appendix H3) proves the chosen record's identity recomputes before and after step 5. It also lists any `effective` identity document whose adapter sources name a rewritten route file; none is expected.
  - *Rejected:*
    - rewriting all ~36 consumers;
    - a declaration `read-roots` key, because it lets target configuration widen B8's permitted sources;
    - detecting alias modules inside `read_coverage`, which is hidden mechanism.
- **DD15 · Rehearsal separation (OQ12; review S2).** Runs A (as-is), B (dependencies moved) and C (switched) of fusion-tea's suite, in one recorded environment with teax and the license.
  - The step-5 test edits are drafted in advance from the staged tests (Appendix H3) and applied in C.
  - **C's pass rule.** No test fails or skips in C that passed in B. Tests failing in both are compared by message.
  - **B against A** is recorded and classified for the consequence note. It is not a gate on the move.
  - **On a real package**, B and C each run `integrate` and the gate-7 driver (Appendix H3).
- **DD16 · Policy template (OQ13).**
  - The template keeps the general rules (§§ 1–5, 9, 11) with their grade and date, under a header saying the target has ratified nothing.
  - Labelled examples are stripped of identifiers. The target slots are typed placeholders.
  - There is no oracle section.
  - *Rejected:* placeholders only; examples verbatim.
- **DD17 · Operator guide home (OQ14).**
  - `integration-guide.md` ships in the bundle beside the runbook. The guide-contract test moves and is rewritten.
  - *Rejected:* a resolver command; a project document.
- **DD18 · Annex template.**
  - `annex-template.md` holds the four sections the runbook reads and lists the package-owned pieces. It also states gate 4's snapshot rule (review S7).
  - A contract test holds the runbook's annex citations to the template.
- **DD19 · Smells.**
  - **Removed:** the `if __package__` path inserts (`indicators.py:42-43`, `preflight.py:55-56`, `verify.py:49-50`, `integrate.py:77-78`).
  - **Kept, each named as a follow-up:**
    - argparse `prog="<tool>.py"`;
    - `indicators.write_atomically`;
    - `read_coverage.py`'s untyped style;
    - `integrate.py`'s size;
    - gate 4's fixed `*.snapshot.json` glob, for which the follow-up is an explicit `--snapshot` flag.
  - **Typing:** ported modules go under one recorded mypy override. New modules are fully typed. Ruff findings in ported code get recorded per-file ignores.
- **DD20 · Environment reads (review M4).**
  - The study package reads the environment in exactly one module, `roots.py`.
  - `roots.environment()` returns a copy and replaces `integrate.py:291`. `roots.teax_simkit_path()` replaces `read_coverage.py:95-96`. Both sites are lines B1, B7 and B8 already edit.
  - The conformance pin gains one named allowance for `sysml_codegen.study.roots`, with the reason "study location settings, which do not affect generation authority". A second test asserts that no other study module reads the environment. Appendix F has the exact edits.
  - *Rejected:* hiding the import behind an `importlib` string, which hides the read instead of justifying it; scoping the pin to the construction closure only, which is a wider change to a pin this item does not own.

## Architecture

```
target project (work tree containing the package = project root)   installed sysml-codegen (tool home)
  pyproject.toml [tool.sysml-codegen.integrate]  ───────────────┐   study/roots.py   (three roots; the one env reader)
  modeling_project/STUDY_POLICY.md          (project document) │   study/*.py       (eight moved, census, declarations)
  .agents/skills/run-study/* + .claude/skills/run-study  (managed)│   study/schemas/   (seven, byte-identical)
  .sysml-codegen/install.json               (own manifest)    │   assets/          (skill, command, policy template)
  <studies-dir>/{ANNEX.md, DISCOVERY_LOG.md, <study-id>/}     │   cli/study.py, cli/install.py (lazy)
  package, manifest, axes, route, oracle  ──────────────────────┴──> sysml-codegen study <tool> ──> documents
teax checkout: TEAX_SIMKIT_PATH ──> producers' PYTHONPATH; gate 0; gate 1b's revision; read-coverage root
agentic-mbse installation.py <── cli/install.py: Installer(manifest=".sysml-codegen/install.json"), install_bundle()
```

**Install flow.**

1. The handler imports `cli/install.py`, which checks `INSTALLER_API_VERSION` and builds an `Installer` on its own manifest.
2. It runs `install_bundle` for each bundle, then writes `teax-completion`.
3. It applies the project-document rule to the policy and saves.

**Tool flow.**

1. `main()` calls `require_project_root(prog, anchor=args.package)`, which resolves, checks and pins the root, or exits 2.
2. The unchanged code runs.
3. Paths render against the pinned root. `tool` blocks are literals under the tool home.

**integrate flow.**

1. Pin the root.
2. Gate 0:
   - load the declaration (`input-invalid` on failure) and build the gate table;
   - build the request;
   - sweep `REQUIRED_ENV + environment`, then teax (`env-missing`);
   - run the clean check.
3. Run the ten gates with producers under `seam_env`: the project root and `TEAX_SIMKIT_PATH` on `PYTHONPATH`, plus `SYSML_CODEGEN_PROJECT_ROOT` and `STUDY_REQUIRE_TEAX=1`.
4. Return as today, with rows 1a and 5 from the declaration.

**Boundaries.**

- agentic-mbse imports nothing from sysml-codegen (ADR-0007).
- `cli/install.py` imports `agentic_mbse.cli.installation`, lazily.
- `sysml_codegen.study` reaches the rest of sysml-codegen only through `snapshot.capture`, at gate 4 and lazily.
- teax loads lazily.

## Required Invariants

- **I1. Byte-faithful outside B1–B12.** The same inputs give the same documents and exit codes, apart from the closed-list fields (SC12).
- **I2. Schemas.** The seven schema files equal `b06585709` byte for byte; a suite test pins their sha256 values.
- **I3. Paths.** A document's paths are relative to the project root and are the same from any working directory, including one outside every work tree. A tool refuses with exit 2, writing nothing, when it finds no root, or when the working directory is inside a different work tree from the package.
- **I4. Tool identity.**
  - `tool.path` and `source_digest.files[].path` start with `sysml_codegen/study/`.
  - `command[0] == tool.path`.
  - Digests recompute from the bytes under the tool home.
- **I5. Installer isolation.** Each installer reads and writes only its own manifest and prunes only under its own bundles.
- **I6. The policy.** An existing `STUDY_POLICY.md` is never written without `--force`.
- **I7. integrate's contract.**
  - Ten gates in order, two classes, fifteen slugs, exit codes 0, 1 and 2.
  - A `CANDIDATE` only when all ten gates passed.
  - An undeclared repo gate gives `BLOCKER`, `could_not_run`, `input-missing`.
- **I8. Dependency direction.** agentic-mbse imports nothing from sysml-codegen. teax and agentic-mbse load lazily.
- **I9. Without teax.** `verify` exits 1, names teax, and writes no document. `integrate` returns its `BLOCKER` naming teax at gate 0 and runs no producer.
- **I10. Generic text.** No shipped text or tool module carries an identifier from SC5's closed lists, except the record template's one history note.
- **I11. Gate claims.** Rows 1a and 5 state the declared `checked` text, or `not declared`. They never state text the target did not declare.
- **I12. teax revision.** A recorded or compared teax revision is always read from `TEAX_SIMKIT_PATH`, never from anywhere else.
- **I13. Environment reads.** Only `sysml_codegen.study.roots` reads the environment among the modules reachable from `sysml_codegen.cli`.

## Component Overview

| Component | Location | Responsibility |
|---|---|---|
| Roots | `src/sysml_codegen/study/roots.py` (new) | The three roots, the in-process override, `require_project_root`, the one environment reader |
| Moved tools | `src/sysml_codegen/study/{common,manifest,identity,indicators,preflight,verify,read_coverage,integrate}.py` | fusion-tea's code at `b06585709` plus Appendix A's edits |
| Census | `src/sysml_codegen/study/census.py` (new) | `by_entry_type` |
| Declarations | `src/sysml_codegen/study/declarations.py` (new) | Reads and validates `[tool.sysml-codegen.integrate]` |
| Study CLI | `src/sysml_codegen/cli/study.py` (new); `study` subparser in `cli/__init__.py` | `cmd_study` dispatch |
| Installer | `src/sysml_codegen/cli/install.py` (new, lazily imported) | `install_commands`, `list_assets`, `prompt_decision`, `require_installer_api` |
| Shipped text | `src/sysml_codegen/assets/skills/run-study/` | `SKILL.md`, `runbook.md`, `record-template.md`, `annex-template.md`, `integration-guide.md` |
| Policy template | `src/sysml_codegen/assets/project_templates/STUDY_POLICY.md.template` | Dated snapshot of the general rules plus slots |
| Upstream pin | `src/sysml_codegen/_upstream_pins.py` | Gains `INSTALLER_API_VERSION` |
| agentic-mbse API | agentic-mbse `src/agentic_mbse/cli/installation.py` | `manifest=`, `install_bundle()`, `INSTALLER_API_VERSION` (Appendix B) |
| Fixture | `tests/fixtures/study_station/` | The neutral project (Appendix E) |
| Tests | `tests/study/`, `tests/unit/test_install_commands.py`, `tests/execution/test_study_*.py`, two conformance edits | The three lanes (Appendix F) |
| Evidence and fusion-tea drafts | `.project/active/study-layer-to-codegen/evidence/` | Parity, read-through, runbook, rehearsal, transcripts; `fusion-tea/` holds the step-5 drafts (Appendices G–I) |

## Non-Goals

- Changing study semantics beyond B1–B12, teax APIs, or any committed study record.
- Moving fusion-tea's pin, merging, pushing, or writing to fusion-tea's main checkout.
- Fusion-specific study tests, fusion-tea's annexes, and regenerating fusion-tea's packages.
- These are named follow-ups, not built here:
  - a record checker (DD12);
  - the kept smells, including a `--snapshot` flag for gate 4 (DD19);
  - an agentic-mbse version change (DD5).
- Policy § 10's oracle conflict. Out of scope: it stays fusion-tea's decision, per the epic.

## Implementation Notes

- **Order.**
  1. The agentic-mbse change, on its own branch, with its tests and full suite. Install it here with `uv pip install -e <worktree>`, and run with `uv run --no-sync`.
  2. The package.
  3. The fixture, which needs the license for capture.
  4. The tests.
  5. Text, evidence and the fusion-tea drafts.
- **Port mechanically first.** Commit the byte-for-byte copy of the eight modules and the seven schemas on its own, then apply Appendix A's edits, tagged with B-ids.
- **Literals over derivation.** `TOOL_SOURCE_FILES` and `tool.path` are literals. A test checks that each resolves under `TOOL_HOME` and that each tool lists every study module it imports.
- **mypy and ruff.**
  - One `[[tool.mypy.overrides]]` block sets `disallow_untyped_defs = false` and names the eight ported modules one by one.
  - Add `ignore_missing_imports` for `simkit.*` if needed.
  - Other findings in ported code get recorded overrides or per-file ignores, listed in the plan.
- **Gate stand-ins.** The fixture's gate stand-ins are `gates/check_*.py`, which this repo's pytest never collects. If pytest refuses an explicit non-`test_` file, rename them `test_*.py` and add `collect_ignore` in `tests/conftest.py`.
- **`jsonschema`** joins the `dev` extra; re-lock with `uv lock`.
- **The environment move** (DD20) uses lines B1, B7 and B8 already edit. Nothing else in the moved code may mention `os.environ`, `getenv` or `getenv(`, comments included, because the pin greps source text.
- **Test isolation.** Tests that call `roots.use_project_root` reset it in a fixture, because the override is process-wide.

## Potential Risks

- **The agentic-mbse change must merge first.** It is small and merges with an explicit merge commit before sysml-codegen (ADR-0008). `require_installer_api()` fails clearly where it is missing.
- **The fixture route fails on stock teax (KB4).** The route copies `test_numeric_evidence_teax.py`'s lifecycle, and the first plan phase proves it in the execution lane. Cut 2 is the release valve.
- **The committed fixture package drifts from the generator.** One license-gated test regenerates it and names the regeneration commands. The spec accepted this coupling.
- **SC12 finds an unlisted difference.** Normalization patterns are declared and reported (Appendix G). A residual difference stops the item and goes to the orchestrator.
- **A fusion-tea route also imports another `scripts/*.py` module.** That module is no longer a permitted read source after B8, so gate 7 would refuse. The rehearsal's driver run on a real package shows it. The fix is the same import rewrite, or moving the helper into the route directory.
- **The fusion-tea test edits are incomplete.** The list is drafted from the staged tests in advance (Appendix H3). Run C's pass rule catches anything missing.
- **A monorepo target gets a plausible wrong root (KB1).** The guide and runbook state the `SYSML_CODEGEN_PROJECT_ROOT` rule.
- **The two copies drift between merge and adoption.** The runbook's drift check (step 1) stops the switch.

## Integration Strategy

- **Merge order.** The agentic-mbse branch first, then sysml-codegen, both with explicit merge commits (ADR-0008). fusion-tea adopts later through the runbook.
- **What it complements.** agentic-mbse `init` installs the goal layer. `install-commands` adds the study layer beside it. The runbook's review rule cites "the installed goal runbook" and states its own fallback.
- **What it replaces.** The single-file `install-commands` (`cli/__init__.py:1018-1050`), and fusion-tea's local skill and tools at adoption.
- **Docs.**
  - `README.md` and `CLAUDE.md` gain the study layer, `install-commands`, `sysml-codegen study`, the project-root rule, and the minimum agentic-mbse revision.
  - At close, a product-ledger entry cites the owner's 2026-10-06 decision.

## Validation Approach

| Criterion | How it is checked | Where |
|---|---|---|
| SC1 | Assets inside the package; `install_commands` layout; install transcript from wheels at both branches, recording the agentic-mbse revision | `tests/unit/test_install_commands.py`; `evidence/install-transcript.md` (H1) |
| SC2 | Noninteractive refresh and preserve; prompt hook; the policy kept, and replaced under `--force`; first-run `teax-completion`; name collisions; coexistence with `agentic-mbse init` in both orders | `tests/unit/test_install_commands.py`; agentic-mbse's installer tests |
| SC3 | Each tool completes and fails closed, in three lanes | Appendix F |
| SC4 | Dry run from installed files, with the installed Check lines run and recorded before the evidence script; cold administrator reading | `evidence/dry-run/` (H2) |
| SC5 | Grep test; per-line read-through | `tests/study/test_generic_text.py`; `evidence/read-through.md` |
| SC6 | Attribute existence and signature test against a table captured at `b06585709` | `tests/study/test_compat_surface.py` |
| SC7 | Prefix and digest recompute; committed pre-move documents; schema sha pins | `tests/study/test_tool_identity.py` |
| SC8 | Undeclared, declared and malformed gates; rows 1a and 5 of a non-fusion return pinned (B12); target-path validation; environment sweep; toolchain keys; gate 1b without `TEAX_SIMKIT_PATH` | `tests/study/test_integrate_declared.py`; the licensed lane |
| SC9 | Runbook draft, pre-drafted fusion-tea edits, and the A/B/C rehearsal with integrate and driver runs | `evidence/fusion-tea-runbook.md`, `evidence/fusion-tea/`, `evidence/rehearsal/` (H3) |
| SC10 | Ledger rows from the read-through's moved verdicts; fusion-tea branch diff | Appendix I |
| SC11 | Full suites here (2206 passed, 9 skipped, plus new) and in agentic-mbse; the two conformance edits; ruff and mypy clean under the recorded overrides | plan's final phase |
| SC12 | Parity script with declared normalization | `evidence/parity/` (Appendix G) |

## Next-Stage Handoff

- **Fixed:**
  - DD1–DD20;
  - Appendices A–E;
  - the declaration format, including `checked`;
  - the CLI forms;
  - the agentic-mbse API;
  - the lanes and the two conformance edits;
  - the parity method;
  - the runbook steps and the expected-edit list;
  - the read-through format.
- **Open for the plan:**
  - test-file splits inside `tests/study/`;
  - the ruff ignores that turn out to be needed;
  - the fixture's literal values, which come from the first generation;
  - the agentic-mbse test file name.
- **De-risk first:**
  1. The fixture route on stock teax (KB4).
  2. The agentic-mbse change and the coexistence test (KB2).
  3. The root split, so that `indicators` on the fixture equals the original layout's output.
- **Estimate.** About 47h execute, or about 42h with all four cuts (Appendix J). The review's two trims are taken and recorded as deferrals. Neither touches a never-cut criterion.
- **ADR candidates after approval** (builder register, `adr.sh new`):
  - "Study tools anchor the project root to the package's git work tree, with an explicit override". It records I3: the same bytes from any working directory, and a refusal on a conflicting work tree.
  - "Reuse agentic-mbse's installer through an API version pin, not a package-version bound". It names the producer gap.
  - "Study location settings are the one environment read reachable from the CLI".

---

## Appendix A — Package layout and the edit map

```
src/sysml_codegen/study/{__init__,roots,common,manifest,identity,indicators,preflight,verify,read_coverage,integrate,census,declarations}.py
src/sysml_codegen/study/schemas/{axis_declaration,baseline_result,indicators,package_identity,preflight_results,study_package_manifest,verification_summary}.v1.schema.json
src/sysml_codegen/cli/{study,install}.py
src/sysml_codegen/assets/skills/run-study/{SKILL,runbook,record-template,annex-template,integration-guide}.md
src/sysml_codegen/assets/commands/teax-completion.md                  (git mv from claude/commands/)
src/sysml_codegen/assets/project_templates/STUDY_POLICY.md.template
```

**`roots.py` (new, fully typed).**

```python
PROJECT_ROOT_ENV = "SYSML_CODEGEN_PROJECT_ROOT"; TEAX_SIMKIT_PATH = "TEAX_SIMKIT_PATH"
TOOL_HOME: Path = Path(__file__).resolve().parents[2]          # the directory holding sysml_codegen/
class RootError(Exception): ...
def use_project_root(root: Path | None) -> None: ...           # in-process override for library callers; None clears
def project_root() -> Path: ...                                # override, env var, else work tree of cwd; RootError
def require_project_root(prog: str, anchor: Path | None) -> Path: ...  # CLI: resolve, check, pin; exit 2 on RootError
def environment() -> dict[str, str]: ...                       # the study package's one read of os.environ (a copy)
def teax_simkit_path() -> Path | None: ...
```

**Edits per moved module.** Every module gets the import rewrite and the SC5 docstring edits, which remove `ADR-009`, `R-B1`, `R-E4`, `ADR-006`, `R-A3`, "design D10", "Item 3's", "Invariant 1", "M4", "M5" and the guide path.

| Module | Edits beyond the import rewrite | B |
|---|---|---|
| `common.py` | `tool_source_digest(files, root=TOOL_HOME)` reads `root / rel` (`:41-49`). The tools pass nothing; the record template's oracle digest passes the project root (review m2) | D7/B2 |
| `manifest.py` | `repo_root()` returns `roots.project_root()` (`:57-59`); `TOOL_SOURCE_FILES` → `sysml_codegen/study/{indicators,manifest,roots}.py` + three schemas (`:35-41`); `tool_source_digest()` under `TOOL_HOME` (`:149-162`) | B1, B2 |
| `identity.py` | none | — |
| `indicators.py` | remove the insert (`:42-43`); `tool.path` literal (`:862`); `main` calls `require_project_root("indicators", Path(args.package))` | B1, B2 |
| `preflight.py` | remove the insert (`:55-56`); `TOOL_SOURCE_FILES` (`:66-74`); `tool.path` ×2 (`:430,:449`); `main` requires the root, anchored on `--package` | B1, B2 |
| `verify.py` | remove the insert (`:49-50`); `TOOL_SOURCE_FILES` (`:60-67`); `tool.path`, `command[0]` (`:517,:520`); `import simkit` (`:484`) → `_import_simkit()` raising a `VerifyError` that names teax; `main` requires the root | B1, B2, B9 |
| `read_coverage.py` | declared roots (`:94-101`): the route dir, `TOOL_HOME / "sysml_codegen"`, and `roots.teax_simkit_path()` with its `*.egg-info` | B7, B8 |
| `integrate.py` | see below | B1–B7, B10–B12 |

**`integrate.py` edits.**

- **Imports and paths.**
  - Remove the insert (`:77-78`), and rewrite the imports, including the driver source (`:1216-1221`).
  - `SEAM_PATH` becomes `sysml_codegen/study/integrate.py` (`:84`).
  - `TOOL_SOURCE_FILES` becomes package paths plus `roots`, `census` and `declarations` (`:89-97`).
- **Environment and teax.**
  - `REQUIRED_ENV = ("SYSIDE_LICENSE_KEY",)` (`:128-135`); `TEAX_SIMKIT_SUBPATH` goes (`:139`).
  - `seam_env` (`:282-299`) starts from `roots.environment()` instead of `dict(os.environ)` (`:291`). It puts the project root and `TEAX_SIMKIT_PATH` on `PYTHONPATH` and sets `SYSML_CODEGEN_PROJECT_ROOT`.
  - `teax_revision()` runs only at `TEAX_SIMKIT_PATH` (`:316-321, :959`).
  - `toolchain_block(env, declaration)` (`:332-346`): keys `agentic_mbse`, `sysml_codegen`, the declared keys, `teax_revision` (`null` without the variable), then `teax_module_path` (the probe).
  - `assert_environment(env, declaration)` (`:502-536`) sweeps `REQUIRED_ENV + environment`, deduplicated and in order. Its teax checks follow DD10.
- **Gate table (B5, B12).**
  - `gate_table(declaration)` returns `GATES` (`:188-209`) with rows 1a and 5 rebuilt. Their `producer` is the declared `target` and their `checked` is the declared text, or `not declared` for both.
  - The manifest, preflight and verification producers become tool paths. The census-snapshot producer becomes `sysml_codegen.snapshot.capture; sysml_codegen/study/census.py`.
  - `SequenceState` gains `declaration` and `gates`. `run_sequence`, `gate_rows` and `build_return` use the table. Before any state exists, `run()` passes the undeclared table.
- **Repo gates.** `gate_pinned_packages` and `gate_model_family_spine` (`:939-946, :981-992`) run `state.declaration.gates[name].target`, or raise `unasked(state.gates[i], "the target declared no producer for this repo-scope gate; declare target and checked under [tool.sysml-codegen.integrate.gates.<gate>] in pyproject.toml")`.
- **Gate 1b** follows DD10's order.
- **Launches.** `sys.executable -m sysml_codegen.study.preflight` replaces the script path at `:552` and `:1304`, and `…verify` replaces it at `:1353`. The producer strings at `:558` and `:1270` become tool paths. The generator runs as `[sys.executable, "-m", "sysml_codegen", "generate", …]` (`:1006`).
- **Census.** `rederived_census` uses `census.by_entry_type` (`:1098`). The census-stale producer becomes `sysml_codegen/study/census.py::by_entry_type` (`:1161`).
- **Backup prefix.** `tempfile.mkdtemp(prefix=declaration.backup_prefix)` (`:1506`).
- **`run()`.**
  - It pins the root through `require_project_root("integrate", anchor)`, where the anchor is the single `--package`, or the working directory when there is not exactly one.
  - It then loads the declaration: a `DeclarationError` becomes `precondition_blocker("input-invalid", …)`, which is new and named under B5 and B12.

**`declarations.py` (new, fully typed).**

```python
REPO_GATES = ("pinned-packages", "model-family-spine")
FIXED_TOOLCHAIN_KEYS = ("agentic_mbse", "sysml_codegen", "teax_revision", "teax_module_path")
DEFAULT_BACKUP_PREFIX = "sysml-codegen-integration-backup-"
@dataclass(frozen=True)
class GateDeclaration: target: str; checked: str
@dataclass(frozen=True)
class IntegrateDeclaration:
    gates: dict[str, GateDeclaration]; environment: tuple[str, ...]
    record_distributions: tuple[tuple[str, str], ...]; backup_prefix: str
def load_declaration(project_root: Path) -> IntegrateDeclaration: ...   # no file or no table → empty; else DeclarationError
```

**Validation.**

- Table keys must be within `{gates, environment, record-distributions, backup-prefix}`.
- Gate names must be within `REPO_GATES`. Each gate has exactly `target` and `checked`, both non-empty strings.
- The `target`'s path part (before any `::`) must be relative and must stay inside the project root once normalized and resolved.
- Environment names must match `[A-Za-z_][A-Za-z0-9_]*` and be unique.
- Distribution keys must be identifiers outside `FIXED_TOOLCHAIN_KEYS`.
- The prefix must be non-empty and contain no `/`.
- A TOML error is a `DeclarationError`.

**`cli/study.py` (new).** `cmd_study(args) -> int` imports `indicators`, `preflight`, `verify` and `integrate` from `sysml_codegen.study` inside the function, maps `args.tool` to its `main`, and returns `main(args.args)`. `cli/__init__.py` adds the `study` subparser with `choices=` and `REMAINDER`.

## Appendix B — The agentic-mbse change (exact)

File: `src/agentic_mbse/cli/installation.py`. The version stays 0.1.3 (DD5).

1. Add `INSTALLER_API_VERSION = "installer/v1"`. Its comment lists the surface it covers and says to change the string whenever any of it changes shape:
   - `Installer(target, *, force, decide, manifest)`, with the decide vocabulary `skip`, `overwrite`, `backup`, `skip_all` and `overwrite_all`;
   - `parents`, `write` and `save`;
   - `actions` and its six keys;
   - `install_bundle` and `frontmatter`.
2. Change the constructor to `Installer.__init__(self, target: Path, *, force: bool, decide: Callable[[str], str], manifest: str = MANIFEST) -> None`. It stores `self.manifest`. It reads `(LEGACY_MANIFEST, MANIFEST)` only when `manifest == MANIFEST`, and otherwise only `(manifest,)`.
3. `save()` writes `self.manifest`.
4. Add `install_bundle(installer, source, *, runtimes: tuple[str, ...], link_mode: str, dev: bool) -> None`. It is the loop body of `install_assistants` (`:435-440`), and `install_assistants` calls it. This is a pure refactor.
5. `CLAUDE.md` "Change Coordination" gains one sentence: other repositories install their own bundles through `Installer` with their own manifest, marked by `INSTALLER_API_VERSION`.

Tests, in agentic-mbse's installer module:

- a custom manifest round-trips: an unmodified file is updated, an edited one is preserved, and `.agentic-mbse/install.json` is never written;
- a custom-manifest installer saves only its own entries even when both agentic-mbse manifests are present;
- `install_bundle` gives the same layout as `install_assistants`;
- a foreign bundle survives `init` and `install-commands`, run noninteractively, in both orders;
- one test exercises each name the version string covers (constructor keywords, decide values, `parents`, `write`, `save`, `actions` keys, `install_bundle`, `frontmatter`), so a shape change fails it;
- `INSTALLER_API_VERSION == "installer/v1"`.

The full suite passes.

**fusion-tea's pin** must reach the merge that carries the API. Items 1 and 2's pin moves do not reach it. Only the SHA changes, never the version string. If Item 2's F2 has not run yet, it can pin straight to the later merge.

## Appendix C — Import tiers (D9) and root-dependent behavior (SC6)

**Supported target API**, documented in the runbook and in `study/__init__.py`:

- **CLI:** `sysml-codegen study {indicators,preflight,verify,integrate}`.
- **Python, for route modules:** `identity.build_sealed(package_name=, package_root=)` and `common.write_document(document, path)`.
- **Python, for a record's oracle digest:** `common.tool_source_digest(files, root=<project root>)`.
- **Protocols the target implements:**
  - the route callable `execute_baseline(out, *, package_dir, manifest_path)`;
  - the oracle's `<callable>(point)` and `operand_bindings()`.
- **Document contracts:** the seven schemas, shipped at `sysml_codegen/study/schemas/`.

**fusion-tea compatibility surface.** These names exist with the same behavior but are not documented as public:

- `common`: `ToolError`, `assert_tree_clean`, `manifest_mod`, `read_json`, `relative_deviation`.
- `indicators`: `build_graph`, `predicate_operands`, `read_model_contract`, `read_pipelines`.
- `manifest`: `MANIFEST_SCHEMA_VERSION`, `ManifestError`, `assert_package_identity`, `assert_pin_matches`, `indicator_input_fingerprint`, `indicator_input_read_set`, `load`, `read_executable_fingerprint`, `read_package_name`, `read_semantic_fingerprint`, `repo_relative_posix`, `validate`.
- `verify`: `TOLERANCE`, `VerifyError`, `check_case`, `derive_verdict`, `feature_refs`, `manifest_mod`, `objective_channels`, `package_input_values`.
- `integrate`: `rederived_census`.

`tests/study/test_compat_surface.py` checks these against `tests/study/data/compat_surface.json`. A capture script run once against the staged modules writes that table, recording each name's kind and its parameters, bases, value or module identity, without annotations.

**Root-dependent behavior.**

- `manifest.repo_root()` returns `roots.project_root()`. In fusion-tea, the wrappers' in-process override makes it fusion-tea's root, as at `b06585709`.
- `manifest.repo_relative_posix(p)` is unchanged, given the root.
- **`RootError` for library callers.** A library caller with no override, no variable and a working directory outside every work tree gets `RootError` from inside `repo_relative_posix`. That is neither `ToolError` nor `ManifestError`. It cannot happen in fusion-tea, where the override is always set, and the runbook's "The tools" section documents it.
- `tool_source_digest` defaults to the tool home and takes an explicit root. No fusion-tea caller exists outside the moved set.

## Appendix D — CLI, installer and declaration surface

```bash
sysml-codegen install-commands [DIR] [--assistant {claude,codex,both}] [--force] [--list]
sysml-codegen study indicators --package DIR --manifest FILE --groups FILE [--group NAME]... [--out FILE]
sysml-codegen study indicators --package DIR --print-fingerprint
sysml-codegen study preflight gates --package DIR --manifest FILE --groups FILE --identity FILE --baseline-result FILE [--out FILE]
sysml-codegen study preflight clean --package DIR [--out FILE]
sysml-codegen study verify --package DIR --manifest FILE --identity FILE --store FILE... [--sample-size N] [--seed HEX] [--out FILE]
sysml-codegen study integrate --audited-work PATH@COMMIT --models-root DIR --package DIR --manifest FILE --groups FILE --route-sys-path DIR --route-module NAME --route-callable NAME --out-dir DIR [...]
```

**`install-commands` writes into `DIR`**, which defaults to `.` as today. It need not equal the tools' project root, because every installed file is found relative to `DIR` or to its own bundle. `README.md` advises installing at the project root.

**On-disk layout after `install-commands target`.**

```
target/.agents/skills/run-study/{SKILL,runbook,record-template,annex-template,integration-guide}.md   managed
target/.claude/skills/run-study -> ../../.agents/skills/run-study                                    managed link
target/.claude/commands/teax-completion.md                                                           managed
target/modeling_project/STUDY_POLICY.md                                                              project document
target/.sysml-codegen/install.json                                                                   sysml-codegen's manifest (tracked)
```

**`--list`** prints three groups: skills (with `run-study (workflow)` and its description, read through `frontmatter`), Claude commands, and project documents.

**`prompt_decision(relative)`** answers `skip` when stdin is not a TTY, and prints the reason when the file is unmanaged.

**Declaration: a fresh target.**

```toml
[tool.sysml-codegen.integrate]
environment = ["MYPROJ_WHEEL_DIR"]
backup-prefix = "myproj-integration-backup-"
[tool.sysml-codegen.integrate.gates.pinned-packages]
target = "tests/test_toolchain_pins.py"
checked = "the toolchain revisions this project pins"
[tool.sysml-codegen.integrate.gates.model-family-spine]
target = "tests/test_model_tree.py"
checked = "the model tree generates and matches the tracked census"
```

**Declaration: fusion-tea's.** It reproduces today's sweep, rows, toolchain block and prefix exactly.

```toml
[tool.sysml-codegen.integrate]
environment = ["STOP_PARSER_WHEEL_TARGET", "STOP_PARSER_AGENTIC_WHEEL", "STOP_PARSER_CODEGEN_WHEEL", "STOP_PARSER_COSTINGFE_WHEEL", "STOP_PARSER_TEAX_ROOT"]
backup-prefix = "fusion-tea-integration-backup-"
record-distributions = { costingfe = "1costingfe" }
[tool.sysml-codegen.integrate.gates.pinned-packages]
target = "tests/test_dependency_provenance.py"
checked = "the pinned package revisions and installed wheel artifacts"
[tool.sysml-codegen.integrate.gates.model-family-spine]
target = "tests/models/test_model_family_spines.py"
checked = "the canonical tree, the family twins and the tracked census"
```

**Where fusion-tea sets `TEAX_SIMKIT_PATH`.** It is `$STOP_PARSER_TEAX_ROOT/packages/teax-simkit`, set in two places:

- `.venv/integration.env`, for operator runs;
- a session fixture in `tests/study/conftest.py`, for the suite, including read coverage outside `integrate` (an Appendix H3 edit).

## Appendix E — The neutral fixture (`tests/fixtures/study_station/`)

**Model.** `models/station.sysml` defines one package, `PumpStation`. It has no units and only `out attribute` results. No calc parameter shares a name with the attribute bound to it.

| Element | Content | Baseline |
|---|---|---|
| Part attributes | `design_inflow` 0.30, `basin_area` 12.0, `allowed_rise_rate` 0.005, `installed_capacity` 0.25, `pump_head` 8.0, `energy_price` 0.10 | — |
| `calc def RequiredFlow(inflow, rise_rate, area)` | `required_flow = inflow - rise_rate * area` | 0.24 |
| `calc def PumpingCost(flow, head, price)` | `annual_cost = flow * head * price * 1000.0`, with `flow` bound to `demand.required_flow` | 192.0 (the objective) |
| `constraint def CapacityCoversDemand(capacity, demand_flow)` | `capacity >= demand_flow`, asserted as `pump_fit` | satisfied |

**Axes.**

- `basin_area` reaches the constraint and the objective.
- `installed_capacity` reaches the constraint only.
- `energy_price` reaches the objective only, so it reports `no_constraint_response`.

The grid is `basin_area ∈ {4, 8, 12, 16}` × `installed_capacity ∈ {0.20, 0.25, 0.30}`, which gives both verdicts.

**Files.** Everything here was written for this item, which `PROVENANCE.md` states.

- `PROVENANCE.md` — the regeneration commands:
  - `sysml-codegen snapshot --models models --output station.snapshot.json`;
  - `generate --from-snapshot … --output pkg/station_study --package-name station_study`;
  - re-pin the manifest with `--print-fingerprint`;
  - refresh `studies/baseline/` in the execution lane.

  It also states gate 4's rule: exactly one `*.snapshot.json` beside the models root.
- `models/station.sysml`, and `station.snapshot.json` beside it.
- `pkg/station_study/…` — the committed generated package.
- `studies/manifest.json` — literal values. The oracle is `oracle_entry.evaluate`, with `sys_path` `studies`.
- `studies/axes.json`, `studies/oracle_entry.py` and `studies/study_route.py`. The route runs stock teax only: `execute_baseline` and `run_grid`.
- `studies/baseline/{package_identity,baseline_result}.json` — committed for the default lane's `preflight gates`.
- `census.json`, `gates/check_pins.py` and `gates/check_census.py`.
- `pyproject.toml` — both gates, each with a `target` and its own `checked` text:
  - `checked = "the fixture's toolchain imports"`;
  - `checked = "the tracked entry-point census against the committed package"`.

  Empty environment; `backup-prefix = "station-integration-backup-"`.

**Use.** The fixture is its own project, and every path in it is relative to the fixture directory.

- Read-only tests use it in place, with `SYSML_CODEGEN_PROJECT_ROOT` set to the fixture directory.
- Tests that mutate it, and every integrate test, copy it into a fresh `tmp_path` git repository and commit.
- SC4 copies its tree into the target with the same relative layout (Appendix H2).

## Appendix F — Tests by lane

**Moves to `tests/study/`**, re-pointed at the neutral fixture or `synthetic_pkg`. The default lane applies unless marked.

- **Whole files:**
  - `test_common`;
  - `test_output_contract`, except `test_fingerprint_read_set_is_the_three_legs`;
  - `test_preflight_gates`, `test_preflight_negatives`, `test_identity`, `test_mechanical_failures`, `test_read_coverage`;
  - `test_integrate_preconditions` (its two simkit-probe tests go to the execution lane);
  - `test_integrate_guide_contract`, rewritten for the shipped guide. It checks slugs, `REQUIRED_ENV`, exit codes, flags, gates, scope phrases, the declaration keys including `checked`, `TEAX_SIMKIT_PATH`, `SYSML_CODEGEN_PROJECT_ROOT`, gate 4's snapshot rule and the monorepo rule.
- **Partial functions:**
  - `test_breeding_predicate` (3), `test_indicator_operands` (4) and `test_verify_operands` (all but the IFE one) go into `test_predicate_operands.py`;
  - `test_integrate_refusals`' two store-resolution tests;
  - `test_verify`'s two pure disjunction tests;
  - `test_generic`'s five agnostic functions go into `test_generic_text.py`;
  - `test_record_template`'s schema check goes into `test_tool_identity.py`.
- **Execution lane:** `test_verify`'s neutral-plus-teax set, and `test_stock_route`'s two sealed-identity tests.
- **Deferred (review trim 1).** These are package-agnostic but stay in fusion-tea, recorded as a deferral, and keep testing the moved code through the wrappers:
  - `test_provenance`, `test_valid_empty`, `test_read_set_coverage`, `test_absolute_tolerances`, `test_multipipeline`, `test_subset_flag`, `test_integrate_restore`;
  - `test_known_answers`' and `test_numeric_evidence`' single agnostic functions.
- **Stay** (fusion-specific): the 24 STAY files, `test_warnings` and `test_integration_workspace`.

**New tests, default lane.**

- `test_roots.py`:
  - the order override, variable, anchor's work tree;
  - a package in no work tree → exit 2;
  - a working directory inside a different work tree → exit 2, naming both;
  - a working directory outside every work tree → same bytes;
  - a missing package keeps its old failure and exit code;
  - no `os.environ` mutation;
  - `TOOL_HOME`.
- `test_tool_identity.py` (SC7).
- `test_generic_text.py` (SC5a). It covers the five bundle files, the policy template and every `sysml_codegen/study/*.py`. The closed lists are committed as literals with provenance: the nine `exploration/` names, and the 17 package names and 20 prefixes from `CONSUMER_ATTRIBUTES.md`, plus the spec's patterns. The one exemption is the record template's history note.
- `test_compat_surface.py` (SC6).
- `test_declarations.py`: every malformed shape, including a missing `checked`, an absolute target and a `../` target.
- `test_census.py`.
- `test_integrate_declared.py` (SC8). It uses a stub `simkit` in a `tmp_path` git repository and a dummy license value. It covers:
  - 1a undeclared → `unasked`, with row 1a reading `not declared`;
  - 1a declared, passing and refusing;
  - rows 1a and 5 of the fixture's return pinned to the fixture's own `checked` texts (B12);
  - 1b unasked, refused, and `TEAX_SIMKIT_PATH` unset → `env-missing`;
  - the environment sweep;
  - a malformed declaration → `input-invalid`;
  - the toolchain keys, with `teax_revision` `null` without the variable;
  - no teax → `env-missing` naming teax.
- `test_verify_without_teax.py` (B9).
- `test_study_cli.py`: dispatch, `choices`, `--help` passthrough, exit codes.
- `tests/unit/test_install_commands.py` (SC1, SC2): includes the first-run `teax-completion` case and the name-collision test.

**Conformance edits (DD7, DD20).**

- `tests/conformance/test_public_authority_switch.py::test_no_cli_flag_or_environment_variable_selects_a_route`: `assert readers == []` becomes `assert readers == ["sysml_codegen.study.roots"]`, with a comment: "One named allowance: study location settings (`SYSML_CODEGEN_PROJECT_ROOT`, `TEAX_SIMKIT_PATH`, the environment the integration seam hands its producers). They do not affect generation authority. No other reader may appear."
  - The flag loop gains no `study` entry. Its comment says why: integrate's `--route-*` flags name a study's execution route, a different sense of "route" that the closed list keeps byte-faithful.
- **New, same file:** `test_the_study_package_reads_the_environment_only_in_roots`. It walks every module under `sysml_codegen.study` with `pkgutil` and asserts that `_reads_the_environment` is true only for `sysml_codegen.study.roots`.
- `test_the_public_api_exports_no_second_construction_entry_point`: the pinned set drops `CODEGEN_COMMANDS` and gains `cmd_study`. A comment records why: the asset tree replaced the file list, and `cmd_study` constructs nothing.

**License lane** (`requires_license`), kept to the SC3 and SC8 minimum (review trim 2):

- `test_study_fixture_current.py`: the recapture and live generation equal the committed bytes;
- gate 5 undeclared → `unasked`, which needs gates 1a–4 to pass.

SC12 covers the other refusal paths once.

**Execution lane:**

- the route reproduces `studies/baseline/`;
- `verify` completes (SC3);
- gate 7 read-coverage and gate 8 verification refusals;
- `CANDIDATE`, which also needs the license. Cut 2 replaces it with a named-gate `BLOCKER`.

**Pre-move documents**, committed byte for byte at `tests/study/data/premove/` with their provenance: `indicators.json`, `preflight_results.json`, `verification_summary.json` and `integration-return.json` (prefix check only).

## Appendix G — SC12 parity script

**Where.** `evidence/parity/` holds `parity.py`, `README.md`, `report.md`, `patterns.json` and `cases/<case>/{orig,orig2,moved}/`.

**Inputs.**

- The fixture, and the staged originals.
- Wheels of both branches, installed non-editable into `$S/venv` with `jsonschema`.
- teax editable from the checkout, plus `SYSIDE_LICENSE_KEY` and `$TEAX`.

**Layout.**

- A git repository `$S/project` holds the fixture's contents at its root, so its relative paths resolve unchanged.
- The originals sit at `scripts/study/` and `scripts/integrate.py`.
- Stand-in gate files sit at fusion-tea's two paths. The spine stand-in carries `_contract` and `_by_entry_type` verbatim (`b06585709:174-182`) and one passing census test.
- `pyproject.toml` holds Appendix D's fusion-tea declaration.
- Both runs use this directory. `out/` is moved aside after each run.

**Which `identity` the fixture route imports.** In the original runs as well as the moved ones it imports `sysml_codegen.study.identity`, the moved module. The original `build_sealed` is covered by the library parity below.

**Runs.**

- **orig** — `python scripts/<tool>.py …`. The four wheel variables are set to dummies and `STOP_PARSER_TEAX_ROOT=$TEAX`. A `uv` shim on `PATH` runs `uv run X …` as `X …`, which is the harness side of B3.
- **orig2** — orig repeated.
- **moved** — `python -m sysml_codegen.study.<tool> …`, with the same environment plus `TEAX_SIMKIT_PATH`.

**Comparison** (review S3). Nothing is masked as a whole field.

1. Exit codes must be equal.
2. **Normalization by declared pattern.** `patterns.json` lists each pattern with its reason:
   - absolute temporary paths;
   - the 32-hex read-coverage token and `read-coverage-tmp-<hex>` directories;
   - `<prefix>XXXXXX/package` backup paths;
   - pytest timing tokens (`in N.NNs`);
   - traceback line numbers and file paths in `seam_traceback.txt`.

   orig and orig2 must be equal after normalization. Any residual difference is reported as unexplained noise and fails the case until a reviewed pattern explains it.
3. **Closed-list values that are determined are mapped, not masked**, by a fixed table:
   - `tool.path`, `command[0]`, gate and blocker `producer` strings (B2, B11);
   - rows 1a and 5, which must equal the declaration's `target` and `checked`, the same strings as orig (B5, B12).
4. **Closed-list values that are content-derived are masked by token:**
   - `source_digest.digest`, and `files[].sha256` of `.py` entries (B2). Schema entries' sha256 must be equal.
   - `files[]` entries present only in the moved run (`roots.py`, `census.py`, `declarations.py`) are listed as B2 additions.
   - Read-coverage `declarations` and `reads` entries under the two tool roots (orig `$S/project/scripts/`, moved `TOOL_HOME/sysml_codegen/`) are compared as sets after path mapping, and their category may differ (B8). All other entries must be equal.
   - `dependency_digest` (B8), and the 64-hex digest inside gate 7's `detail` sentence (B8).
5. Everything else must be equal, including every `detail` string after normalization. A changed blocker message is a difference.
6. **Library parity**, with `use_project_root($S/project)`, covers `indicator_input_fingerprint`, `build_sealed`, `repo_relative_posix` and `rederived_census`.

**Cases.**

- `indicators`: complete, pin mismatch, `--print-fingerprint`.
- `preflight gates`: complete, stale manifest.
- `preflight clean`: clean, dirty.
- `verify`: complete, oracle mutated.
- `integrate`:
  - gate 0: input-missing, input-invalid, env-missing, package-not-integrated;
  - 1a refused; 1b unasked and refused;
  - 2 refused;
  - 3 handwritten-lost: delete and commit one file under `handwritten/`. If the fixture package has no handwritten files, the case is recorded as unreachable;
  - 4 census unasked and census stale;
  - 5 refused;
  - 6 manifest stale;
  - 7 read-coverage refused: a parity-only route variant opens a file outside the declared roots;
  - 8 verification refused;
  - 9 unasked and lineage mismatch;
  - `seam-internal-error`: a census file missing `derived_against_semantic_fingerprint`;
  - `CANDIDATE`, unless cut 2 applies.

**Pass.** `report.md` lists each case as `EQUAL`, or `EQUAL after closed-list fields [ids]`, with every pattern application counted. No case may be `DIFFERENT`.

## Appendix H — Orchestrator-run evidence

`$EV` is `.project/active/study-layer-to-codegen/evidence/`.

**H1. SC1 install transcript.**

1. Build both wheels and install them into `/tmp/study-install-<stamp>/venv`.
2. Record `pip show agentic-mbse`, the `direct_url.json` revision, and both `__file__` paths, to show neither checkout is on the path.
3. Run `install-commands target --list`, then `install-commands target < /dev/null`.
4. Record the target's files and the manifest.
5. Edit `runbook.md` and re-run: it is skipped. Then run with `--force`.
6. Run `agentic-mbse init target < /dev/null` and list both manifests.

Save it as `$EV/install-transcript.md`.

**H2. SC4 dry run** in `/tmp/study-dry-run-<stamp>/`.

1. **Target** (review S8). Run `git init target`, then `install-commands target --assistant claude < /dev/null`. Copy the fixture's tree with its relative layout unchanged:
   - `models/` and `station.snapshot.json`;
   - `pkg/station_study/`;
   - `studies/study_route.py` and `studies/oracle_entry.py`;
   - under cut 3, also `studies/manifest.json`.

   The studies directory is `studies/`. Commit.
2. **Agent.** `claude -p` in `target/`, with the venv on `PATH`, `TEAX_SIMKIT_PATH` set, and Item 2's isolation from user-level configuration.
3. **Brief.**
   - Intake: "Study how the pump-fit constraint responds to basin area and installed pump capacity, and whether the energy price matters to it. The package is pkg/station_study."
   - Operator answers:
     - the studies directory is `studies/` (write it into the policy's § Locations);
     - the route is `execute_baseline` and `run_grid` in `studies/study_route.py`;
     - the oracle is `oracle_entry` there;
     - any `no_constraint_response` axis is ruled "proceed as sensitivity-only";
     - a coordinator review check suffices;
     - commit the record.
   - For anything else, write it under § 17 and stop.
4. **Checks** (review S6).
   - The agent runs each installed step-14 and step-15 **Check:** line and records its command and output in the record's § 14.
   - Then `check_record.py` runs. A disagreement with the Check lines is a finding.
   - Every tool document carries `tool.path` under `sysml_codegen/study/`.
   - The read-file list holds only target files, the installed skill and the venv.
5. **Administrator.** A fresh session reads the record directory only and writes `synthesis.md`.

The evidence names the pieces supplied ready-made: the package, models, snapshot, route and oracle, plus the manifest under cut 3.

**H3. SC9 runbook and rehearsal** (review S2, M2). `$EV/fusion-tea-runbook.md` follows Item 2's shape. `$FT` is the fusion-tea worktree and `$FTC` a disposable worktree of `b06585709`.

**Pre-drafted fusion-tea edits.** The implementing stage drafts these in `$EV/fusion-tea/`, and the orchestrator applies them on the fusion-tea branch:

- `wrappers/`: the eight wrapper modules;
- `routes.sed`: the nine route-import rewrites;
- `declaration.toml`: Appendix D;
- `step5-tests.patch`: the expected test edits below.

| fusion-tea file:line (`b06585709`) | Class | Edit |
|---|---|---|
| `tests/study/conftest.py:27` | schema home (DD1) | `SCHEMA_DIR` → `importlib.resources.files("sysml_codegen.study") / "schemas"` |
| `tests/study/conftest.py` (new fixture) | teax (B7, DD10) | session fixture sets `TEAX_SIMKIT_PATH` from `STOP_PARSER_TEAX_ROOT` |
| `test_absolute_tolerances.py:72`, `test_indicator_operands.py:80`, `test_record_template.py:15` | schema home | packaged schema path |
| `test_common.py:56, :67, :74-75` | tool home (D7, B2) | `sysml_codegen/study/…` paths |
| `test_read_coverage.py:190-191`; `:254` | B2; B7/B8 | package paths; `TEAX_SIMKIT_PATH` |
| `test_single_point_gate.py:24, :50`; `test_study_publication_fail_closed.py:215` | B7/B8 | set `TEAX_SIMKIT_PATH` |
| `test_integrate_preconditions.py:94`; `:146, :148, :167`; `:202, :211-213` | B4; B2; B7 | parametrize over `REQUIRED_ENV` + the declared environment; tool paths; `TEAX_SIMKIT_PATH` |
| `test_integrate_lineage.py:29`; `test_integrate_refusals.py:56, :224, :246`; `:166` | B2; B11 | tool paths; the census producer |
| `test_output_contract.py:183-187, :317`; `test_verify.py:234`; `test_preflight_gates.py:139` | B2 | package paths, `command[0]` |
| `test_integrate_guide_contract.py` | guide moved (DD17) | reduce to the supplement's own facts: sealed-wheel home, `WHEEL_HASHES`, ADR-0009 |
| `tests/models/test_model_family_spines.py:178-182` | B11 | `from sysml_codegen.study.census import by_entry_type as _by_entry_type` |

**Environment control.**

- One file, `$EV/rehearsal/env.sh`, is sourced for every run. It holds the license (record its presence, never its value), fusion-tea's `STOP_PARSER_*` values, and `TEAX_SIMKIT_PATH`. All runs use one shell and one copy, in sequence.
- Per run, record into `<run>/env.txt`: `python -V`, `uv pip list`, teax HEAD, and `env | grep -E '^(STOP_PARSER_|TEAX_SIMKIT_PATH|SYSML_CODEGEN_PROJECT_ROOT|PYTHONPATH)='`.

| Step | Runbook action | Rehearsal | Expected observation |
|---|---|---|---|
| 1 Drift | `git diff b06585709 origin/main -- .claude/skills/run-study modeling_project/STUDY_POLICY.md scripts/study scripts/integrate.py docs/integration_seam_operator_guide.md` prints nothing, or stop | same, on `$FT` | empty |
| 2 agentic-mbse pin | `uv run --no-sync python -c "from agentic_mbse.cli.installation import INSTALLER_API_VERSION as v; print(v)"` prints `installer/v1`, or move the pin first | after `uv pip install --python $FTC/.venv/bin/python --no-deps $AMBSE_WHEEL $CODEGEN_WHEEL` (this is run B's state) | `installer/v1` |
| 3 No loss | each ledger row's anchor greps in its destination | `git -C $FTC grep -n '<anchor>' -- <file>` on the fusion-tea branch tip | every row found |
| 4 Pin move | sysml-codegen `rev` → merged SHA; hand-edit `uv.lock`; `uv sync --frozen --extra e2e`; restore removed packages; `uv lock --check`; update `C_PROD`. No lock effect from this item's `pyproject.toml`: the dependencies are unchanged, `jsonschema` is in an extra fusion-tea does not request, there is no new console script, and the assets are inside the package | not rehearsed (needs the merged SHA) | — |
| 5 Switch | the wrappers; `routes.sed`; `git rm -r scripts/study/schemas`; `step5-tests.patch` | applied on `$FTC` | `python -c "import scripts.study.manifest as m, sysml_codegen.study.manifest as n; print(m is n)"` prints `True`; `git grep -n 'from scripts.study' -- 'exploration/*/studies/study_route.py' 'exploration/*/*/studies/study_route.py'` prints nothing |
| 6 Declare | Appendix D's table in `pyproject.toml`; `TEAX_SIMKIT_PATH` in `.venv/integration.env` | applied | `uv lock --check` unaffected by a `[tool]` table |
| 7 Re-install | `git rm -r .claude/skills/run-study .agents/skills/run-study`; drop `!.claude/skills/run-study/`; `uv run --no-sync sysml-codegen install-commands . < /dev/null` | same | five files under `.agents/skills/run-study/`; the link; "Preserved modeling_project/STUDY_POLICY.md"; `.sysml-codegen/install.json` |
| 8a Suite (cut 1) | `uv run --no-sync pytest tests/study tests/models/test_model_family_spines.py -q -rs --junitxml=…` | runs A, B, C; `junit-diff.py` compares ids, outcomes, skip counts and failure messages | **C:** no test fails or skips that passed in B, and tests failing in both fail with the same message. **B against A:** recorded and classified for step 9 |
| 8b Re-verify | before and after step 5, `identity.assert_matches` over the chosen record's identity document and package; then run the moved `verify` with the record's seed and sample size, and compare it with the record's summary, mapping `tool` and `command[0]`; the record directory's `git status` is empty; list every committed `package_identity.json` of kind `effective` whose adapter sources name a rewritten route file | on `20260916-primary-loop-sizing` if its sealed identity recomputes, otherwise the newest sealed-identity record that does | same digest before and after; same sampled cases, verdicts and worst deviation; the effective-identity list is empty |
| 8c Integrate on a real package (needs teax and the license; the orchestrator runs it) | in B (local tools) and in C (moved), run `integrate` with the fusion supplement's full stellarator request; in C also run the gate-7 driver directly | the driver: `PYTHONPATH=$FTC:$TEAX_SIMKIT_PATH SYSML_CODEGEN_PROJECT_ROOT=$FTC uv run --no-sync python -c 'import sys; from sysml_codegen.study.read_coverage import run_route; run_route(*sys.argv[1:])' exploration/stellarator_e2e/studies study_route execute_baseline /tmp/rc exploration/stellarator_e2e/pkg/stellarator_tea exploration/stellarator_e2e/studies/manifest.json rehearsal` | B and C stop at the same gate with the same class and condition, or both return `CANDIDATE`. Their returns differ only in closed-list fields under the parity comparator. The C driver writes `read_coverage.json` with `outcome: pass` and `violations: []` |
| 9 Consequence | the generator moves about 142 commits, so gate 2 may refuse fusion-tea packages and gate 4 snapshots may drift until each is regenerated in its modeling item; this is the pin move's consequence, from B against A and 8c | — | — |

Each step is marked rehearsed, not rehearsable (with the reason), or not run.

## Appendix I — Porting the text, the read-through, and the ledger

**Method.** Each file starts from its `b06585709` bytes. Edits are made by class, and general rules keep their wording:

- `envelope` — frontmatter;
- `path` — fusion-tea paths become the studies directory or a sibling file;
- `tool` — `scripts/study/x.py` becomes `sysml-codegen study x`;
- `objective` — LCOE becomes "objective";
- `route` — named teax entry points become the policy's route;
- `adapter` — adapter practice is removed, but the disclosure stays and the fields keep their names;
- `pointer` — `(Item n)`, record ids, `L-`/`T-` ids, requirement and decision numbers;
- `goal-layer` — "the installed goal runbook, § Review scope and evidence reuse; a target without the goal layer applies the study policy's § Process sizing";
- `project` — instructions that only make sense for one project move to fusion-tea.

**`SKILL.md`.**

- Triggers say "the objective" and "a studies directory".
- The record path becomes `<studies-dir>/<study-id>/`.
- "Then go here" names the four sibling files, the policy and the `sysml-codegen study` tools.
- The goal-layer pointer is rewritten.

**`runbook.md`.**

- Header paths, and every **Calls:** line.
- Steps 5, 8 and 9 lose their route and adapter content.
- **Step 13** keeps one general conditional line (review S5): "If the record's `teax.era_pin` is not null, state that pin as a reproduce prerequisite at the claim site, not only in a provenance note."
- Step 7's provenance citation moves; the rule stays.
- The goal-layer pointers, the `DISCOVERY_LOG.md` path, and "objective result".
- **New sections.**
  - "The tools" covers the CLI forms, `TEAX_SIMKIT_PATH`, and the project-root rule. The rule includes `SYSML_CODEGEN_PROJECT_ROOT` for monorepos and for running from outside a work tree, and `RootError` for library callers.
  - "What a package annex supplies" covers Appendix C's supported API.
- **Check: lines** in steps 14 and 15:
  - § 15's `<study-id>#<n>` ids equal, as a set, the Record-column ids the discovery log carries for this study id;
  - `grep -c '<' record.md` prints 0;
  - every `manifest.content_used.fingerprint_names` entry is a key under `fingerprints`;
  - every `arms[].store_id` is in `stores[]`;
  - every `arms[].artifacts[]` entry has a `sha256`.

**`record-template.md`.**

- The copy path; § 3 LCOE; § 10's route value; the `(Item 3)` markers become "(fixed by the tool's schema)".
- `tools[].path` becomes `sysml_codegen/study/<tool>.py`, with the one history note, worded: "**History: tool paths in older records.** Records written before the study tools shipped in sysml-codegen name each tool `scripts/study/<tool>.py`, and the integration seam `scripts/integrate.py`, in `tools[].path` and `source_digest.files[].path`. Those records stay valid as written: read the prefix as the tool's era, never as a file to open. Digests from the two eras never compare, because the path is part of the digested text."
- The oracle digest names `common.tool_source_digest(files, root=<project root>)`.
- `teax.era_pin`: "null, or the teax revision the route needs beyond the environment's".

**`integration-guide.md`.**

- Generic invocation and environment blocks.
- The declaration table, including what each repo gate is meant to establish and why `checked` has no default.
- `TEAX_SIMKIT_PATH`, which gate 1b requires.
- The project-root and monorepo rule.
- Gate 4's snapshot rule: exactly one `*.snapshot.json` beside the models root, so `instance_graph_snapshot.json` does not qualify (review S7).
- The exit-2 row adds two cases: the invocation could not start (an argparse usage error), and a missing or conflicting project root. Neither writes a document.
- fusion-tea's specifics move to its supplement.

**`annex-template.md`.** The four sections, the package-owned pieces, and the snapshot rule.

**`STUDY_POLICY.md.template`.** As in DD16 and Evidence B:

- an unratified header;
- §§ 1–5, 9 and 11, with examples stripped of identifiers;
- § 4's cross-reference corrected;
- § 5 restated without "demo", "criterion 5" or the named fusion rule;
- slots for § Locations, § Execution routes, § Hypotheses and an empty § Tripwire record;
- no § 10.

**Read-through record (SC5(b)).** `$EV/read-through.md` has one table per file, with ids `SK-`, `RB-`, `RT-`, `IG-` and `SP-`:

| Id | fusion-tea line(s) | Text (quoted, ≤ 12 words) | Class | Verdict | New text, or destination |
|---|---|---|---|---|---|

- The verdict is one of `kept: general`, `kept: labelled example`, `generalized` or `moved`.
- A `moved` row names a fusion-tea file and section, marked "exists at `b06585709:<line>`" or "added on `<branch>`".
- Every LCOE instance gets a row, and so does the step-13 era-pin line (`generalized`).

**Ledger rows (SC10).** The orchestrator appends "## Item 3 — study-layer-to-codegen" in Item 2's columns (Text | Was in | New fusion-tea home | Evidence). The rows group the `moved` verdicts by destination. Evidence holds the read-through ids, the branch diff, and runbook step 3's anchor.

The destinations:

- fusion-tea's `modeling_project/STUDY_POLICY.md`: it gains § Locations, the two-route and adapter rules in § 6, and step 7's provenance. Its existing text is the home of every `SP-` row.
- The annexes.
- `docs/integration_seam_operator_guide.md`, rewritten as fusion-tea's supplement.
- `CLAUDE.md`.

The implementing stage drafts these texts in `$EV/fusion-tea/`.

## Appendix J — Estimate (execute hours, rough ±30%)

| Criterion | Spec | First draft | Revised | Why it changed in this revision |
|---|---|---|---|---|
| SC1 | 2 | 2 | 2 | — |
| SC2 | 2.5 | 3.5 | 3.75 | S4: lazy import, collision test, first-run message |
| SC3 | 12 | 14.5 | 12 | S1's anchor and conflict tests +0.5; trim 1 (deferred moves) −1.75; trim 2 (licensed lane kept to the SC3/SC8 minimum) −1.25 |
| SC4 | 2 | 2 | 2 | S6 and S8 change the run's recipe, not its size |
| SC5 | 5 | 5 | 5.25 | S5's era-pin line; S7's snapshot rule; the monorepo rule |
| SC6 | 1 | 1 | 1 | — |
| SC7 | 1 | 1 | 1 | — |
| SC8 | 4 | 4 | 4.75 | B12's claims (M1), target validation (m4), gate 1b's rule (M3) |
| SC9 | 3 | 3.5 | 7.25 | fusion-tea step-5 test edits drafted here +2; M2's route rewrite and identity check +0.75; the tightened rehearsal with driver and integrate runs +1 |
| SC10 | 1.5 | 1.5 | 1.5 | — |
| SC11 | 0.5 | 1 | 1.75 | M4's conformance edits and the environment move +0.75 |
| SC12 | 2 | 3 | 3.5 | S3's token normalization and three more cases |
| Docs | 1 | 1 | 1.25 | README's minimum revision and the root rule |
| **Total** | **37.5** | **43** | **47** | about 42 with all four cuts |

The total is about 47h execute, plus about 6h of design (draft and revision) and 1h of plan: about 54h, roughly 6.75 days against the epic's 2.

Both review trims are taken and recorded as deferrals, and neither touches a never-cut criterion. Trim 1 leaves agnostic tests running in fusion-tea through the wrappers. Trim 2 keeps the licensed lane at what SC3 and SC8 require, and SC12 covers each refusal path once.

## Revision 2026-10-12

Revised after `design-review.md` (Revise) under the orchestrator's decisions in `briefs/design_revision.md`.

**Premise conflicts and must-fix items.**

- **Conflicts 1, 3 and 4.** Recorded as accepted. Conflict 1 now imports lazily (DD4, DD5). Conflict 4 is reworded (premise conflicts; I9).
- **M1 / conflict 5.** New closed-list item B12, added to the spec by the orchestrator:
  - declared gates carry `checked`, with no default;
  - a missing `checked` gives `input-invalid`;
  - fusion-tea's strings are declared verbatim;
  - affects DD8, I11, Appendices A, D and E, the B12 pin test in Appendix F, and SC12's row mapping.
- **M2.** Runbook step 5 rewrites the nine route imports. No sealed identity changes. Step 8b proves it, and 8c runs `integrate` and the gate-7 driver on a real package (DD14, KB5, Appendix H3).
- **M3.** The teax revision comes only from `TEAX_SIMKIT_PATH`. Gate 1b blocks without it, and the toolchain records `null` (DD10, I12).
- **M4.** The environment reads are confined to `roots.py`, the dispatch lives in `cli/study.py`, and two named conformance edits plus a new test cover it. `cli.__all__` is updated with its reason (DD3, DD7, DD20, I13, Appendix F).

**Should-fix items.**

- **S1.** The root anchors to the package's work tree. A conflicting working directory or no root gives exit 2. KB1 is corrected (DD2, I3).
- **S2.** The rehearsal has pre-drafted edits and a non-circular pass rule. The environment is controlled and recorded, skips and messages are compared, and 8c is added (DD15, H3).
- **S3.** The parity script normalizes by declared token pattern, never whole fields. It adds gate 3, gate-7 read-coverage and internal-error cases, and states which `identity` the route imports (Appendix G).
- **S4.** The whole installer surface is pinned, imports are lazy, the first-run `teax-completion` behavior is stated, and a collision test is added (DD4–DD6, Appendix B).
- **S5.** Step 13 keeps the conditional era-pin line (Appendix I).
- **S6.** The installed Check lines run before the evidence script (DD12, H2).
- **S7.** The snapshot rule is in the guide, the annex template and PROVENANCE, and `--snapshot` is a follow-up (DD18, DD19).
- **S8.** SC4 keeps the fixture's layout (H2).

**Minor items.**

- **m1.** In-process override; no `os.environ` mutation; the wrapper pins (DD2, DD14).
- **m2.** `tool_source_digest(files, root=TOOL_HOME)` (Appendices A and C).
- **m3.** The new outcomes are named: malformed declaration (B5, B12) and missing or conflicting root (B1).
- **m4.** Target paths are validated.
- **m5.** I3's narrowing goes into the ADR candidate. README and the SC1 transcript name the agentic-mbse revision.
- **m6.** The manifest is tracked.
- **m7.** The table and the declaration live on `SequenceState`.
- **m8.** `choices=`.
- **m9.** The bets are renamed KB1–KB6.
- **m10.** The estimate covers the step-5 edits, M2, M4 and README.

**Product-lens.** design-F1 → M1/B12; F2 → S5; F3 → S6; F4 and F5 → m5.

---

Next Step: re-review of M1–M4 only, as the review recommends, then `/_my_plan`.

## Amendment 2026-10-12 (orchestrator)

- **Nine route modules, not eight.** Phase 4 found `exploration/whole_plant_conversion/studies/study_route.py` (`CONSUMER_SURFACE.md:106`), which the design missed. The orchestrator verified at fusion-tea `b06585709` that all nine live route modules call `identity.build_sealed` and none uses an effective identity or adapter sources, so DD14's no-identity-change reasoning holds for the ninth. The counts above now read nine.
- **Record copies.** Committed records carry copies of route modules under `<record>/results/sources/` and `<record>/preparation/`. They must never be rewritten (spec Non-Goals). git's `*` pathspec crosses `/`, so a glob such as `exploration/*/studies/study_route.py` matches those copies. Every step-5 command and check names the nine live files explicitly.
- **DD2's missing-package sentence overclaims** (audit F7, recorded in the audit fix pass, 2026-10-12). DD2 says a missing package "still fails where and how it failed before, with the same exit code". That holds only when the anchor's nearest existing ancestor is in a git work tree or an override is set. Otherwise B1's root refusal comes first, exit 2 with no document, in three cases:
  - a `--package` whose nearest existing ancestor is in no work tree, where the original exited 1 naming the missing file (`roots.py:191-195`);
  - `indicators --print-fingerprint` for a package in no work tree (`indicators.py:962`), though that output cites no root-relative path;
  - `integrate` with `--package` absent, run from outside every work tree. The working directory is the anchor (`integrate.py:1565-1572`), so the message calls it "the package" (`roots.py:192`), and no return is written.
  Each is a B1 refusal that premise conflict 4 already lists, and none fails open. The decision stands; only the sentence overclaimed.
