# Design: Move the study layer to sysml-codegen (WRAP-SPLIT Item 3)

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-10-12
**Branch:** `study-layer-to-codegen` at `678e298` (spec approved for design at `a09bdb1`)
**Run:** non-interactive design stage for the agentic-mbse orchestrator (`/_my_orchestrate`, 2026-10-12)

## Overview

The study layer moves into one new subpackage, `sysml_codegen.study`, and one skill bundle that `sysml-codegen install-commands` installs through agentic-mbse's installer. The code moves byte-faithfully except for the closed list B1–B11. Almost every item on that list comes down to replacing "where this file sits" with three named roots and one target-written declaration.

## Related Artifacts

- **Spec:** `.project/active/study-layer-to-codegen/spec.md` (twelve criteria, closed list B1–B11, decisions D6–D11).
- **Spec review:** `spec-review.md` (verdict Revise, applied). **Briefs:** `briefs/{spec,spec_review,spec_revision,design}.md`.
- **Product-lens ledger:** `product-lens.md`. `/_my_design` does not call for a design-stage lens run, so none was run. The spec-stage dispositions bind here: spec-F1 (no adapter route as general practice; the fixture runs on the stock route) shapes DD13 and Appendix I.
- **Epic and ledger (agentic-mbse, staged at `ac5fb1a`):** `.project/backlog/epic_wrap-split.md` Item 3; `.project/active/wrap-split-migration-ledger.md` (Item 2's row format).
- **Precedent:** agentic-mbse `.project/completed/20261012_goal-layer-port/design.md` (Appendix C ledger rows, Appendix D rehearsal and dry run) and `evidence/fusion-tea-runbook.md`.
- **Staged sources (gitignored):** `.orchestrate-logs/src/fusion-tea@b06585709/` (tools, skill, policy, guide, tests, `CONSUMER_SURFACE.md`, `CONSUMER_ATTRIBUTES.md`, one committed record) and `.orchestrate-logs/src/agentic-mbse@main/` (`src/agentic_mbse/cli/installation.py`, `CLAUDE.md`).
- **Repackaging check:** `.orchestrate-logs/scratch/repack-check/{check.py,output.txt}`.
- **Decision records:** `.project/adr/0007-agentic-mbse-owns-neutral-facts-codegen-owns-rendering.md` (dependency direction; the byte-faithful lesson), `.project/adr/0008-cross-repo-merges-use-merge-commits.md` (merge order). **Product promises:** `.project/product/0001-design-search-free-variation.md`, `.project/product/0004-product-identity-parse-walk-emit.md`.

## The Point

A modeling project that uses sysml-codegen and teax gets the whole study capability by installing sysml-codegen and running `sysml-codegen install-commands`. The capability is the `run-study` skill with its runbook and record template, a study-policy template, and the tools those steps call. The project can then run a study from intake to a committed record, and hand it to a second agent, with nothing copied from fusion-tea.

- [OWNER] (epic header, 2026-10-06): the study layer ships from sysml-codegen, which owns the generated-package contracts the tools read. [OWNER-VERBATIM] "ported and generalized … installed like everything else" (research `:18`).
- [AGENT] (orchestrator Align reading, uncontested): the bar is a working capability in a fresh target, not copied files.
- [NEED] The owner's shape survives. It is a lightweight skill, a runbook, a policy rulebook and tools. Indicators inform and never gate. Intake is collaborative. One skill serves the executing and administrator roles. An axis nothing pushes back on is surfaced as a sign the model is underdeveloped.
- [NEED] fusion-tea loses no information. [INFERRED] Study semantics change only by the closed list B1–B11. This is ADR-0007's lesson: "A boundary move is byte-faithful or it is a behavior change to be reviewed as one."
- It ladders up to P-001: "the study layer owns exploration and decisions" over the generated package.

## Premise conflicts surfaced (read first)

**1. The installer dependency guarantee. Overturned with evidence, and reversible (DD5).** The spec requires, graded [INFERRED]: "sysml-codegen's declared agentic-mbse dependency must exclude every agentic-mbse revision that lacks that API." The brief asks for "the version and dependency-bound change". Excluding by declaration means bumping agentic-mbse past 0.1.3. That bump is far more expensive than it looks:

- The v6 snapshot loader refuses any snapshot whose `authority.agentic_mbse_version` differs from the running agentic-mbse (`src/sysml_codegen/snapshot/envelope.py:459-473`). All 22 committed v6 fixtures here record `0.1.3`. A bump makes every one of them unloadable until it is recaptured under the license, and the public package oracle must then be re-reviewed.
- This repo pins that version as a reviewed upstream authority (`src/sysml_codegen/_upstream_pins.py:36`; `tests/unit/test_package_metadata.py:19,32-33`).
- fusion-tea requires `agentic-mbse[...]==0.1.3` exactly (fusion-tea `pyproject.toml:8`). Its provenance suite, which is gate 1a's producer, pins `VERSIONS["agentic-mbse"] = "0.1.3"` (fusion-tea `tests/test_dependency_provenance.py:28-32`). Its tracked snapshots carry the same authority field.
- A version bound protects nothing in practice. Every consumer installs agentic-mbse by git revision or path (fusion-tea `pyproject.toml:36`; this repo's `pyproject.toml:63-64`), and every revision so far reports 0.1.3.

The design keeps the requirement's intent instead: no install ever runs against an installer that lacks the API. It does this through the mechanism this repo already uses for agentic-mbse API contracts. agentic-mbse exports `INSTALLER_API_VERSION`. sysml-codegen pins it in `_upstream_pins.py`, a test checks it, and `install-commands` checks it at start, failing closed with the revision needed.

**If the orchestrator wants the literal requirement**, the delta is:

- bump agentic-mbse to 0.1.4 and set the bound to `>=0.1.4,<0.2`;
- recapture the 22 snapshots and re-review the package oracle;
- update `_upstream_pins` and the metadata test;
- add fusion-tea's `==0.1.4` edit and a snapshot recapture to the runbook.

That is about +3h here, plus fusion-tea churn.

**2. A smaller correction.** The spec says fusion-tea's agentic-mbse pin `adbef75` predates Item 1's native installer. fusion-tea's provenance test says the opposite: the native skill distribution advanced the pin to `adbef75` (`tests/test_dependency_provenance.py:13-14`). It changes nothing here, because that revision lacks this item's API either way.

**3. The spec's fixture starting point is a fusion-tea file.** The nearest existing model with the right shape is `tests/fixtures/wi014_toy`. It was "imported verbatim" from fusion-tea WI-014 (`tests/fixtures/wi014_toy/PROVENANCE.md`), so it fails SC4's "no fusion-tea file" rule. DD13 writes a new neutral model instead.

**4. "Writes no output document" cannot apply to `integrate` literally.** SC3 and B9 say that without teax, `verify` and `integrate` "exit non-zero, name teax in the message, and write no output document". `integrate` writes a return document on every exit path. That is its documented contract (`integrate.py:43-47, :716-728`), and the two-class return rests on it. A literal reading would add a third outcome. The design reads B9 this way: `verify` writes nothing; `integrate` writes only its usual `BLOCKER` return (gate 0, `could_not_run`, `env-missing`, detail naming teax) and no producer output. I9 states this.

## Research Findings

- **Root dependence (Evidence A, confirmed by reading).**
  - The project-root sites are `manifest.py:57-69`, `common.py:62`, `verify.py:93`, `identity.py:225`, `integrate.py:292, :311, :824, :1234`, and every `repo_relative_posix` call.
  - The tool-home sites are `manifest.py:35-41, :149-162`, `common.py:41-57`, `indicators.py:862`, and the `TOOL_SOURCE_FILES` tuples (`preflight.py:66-74`, `verify.py:60-67`, `integrate.py:89-97`).
  - `read_coverage.py:94` uses `Path(__file__).parents[1]` as a read root.
- **fusion-tea pins cwd-independence twice.** `test_output_contract.py:232-240` runs `indicators` from `tmp_path`, outside the repository, and requires identical bytes. `test_identity.py:105-111` calls `chdir` in-process and requires the same identity document. So a root found only from the working directory would break fusion-tea's suite at adoption. DD2 and DD14 handle this together.
- **Schemas fix the shapes.** `verification_summary.v1.schema.json:39-43` says `command` is "repo-relative. No absolute paths, so two agents produce identical bytes for identical facts". That rules out recording the invocation form in `command[0]` (DD3).
- **agentic-mbse's installer** (`installation.py`, staged):
  - `Installer.__init__` reads both `.claude/.tool-hashes.json` and `.agentic-mbse/install.json` into one `files` map (`:104-107`). `save()` writes `MANIFEST` (`:286-295`).
  - Pruning removes only manifest keys under the bundle being installed (`:206-230`).
  - The bundle install is a five-line loop body in `install_assistants` (`:434-440`). It copies into `.agents/skills/<name>`, then `expose_to_claude` links `.claude/skills/<name>` (`:412-426`).
  - `CLAUDE.md` "Init File Ownership" says project documents are "create once and preserve on re-init; `--force` replaces them". It also says to "route managed assets through `Installer`; apply the appropriate explicit preservation rule when adding owner documents".
- **This repo's current installer** copies one file with no ownership rules. `get_commands_dir()` (`src/sysml_codegen/cli/__init__.py:59-68`) points outside the wheel, which packages only `src/sysml_codegen` (`pyproject.toml:41-42`). Non-`.py` files under that directory do ship: the Jinja2 templates load from `Path(__file__).parent.parent / "templates"` (`cli/__init__.py:147-155`).
- **Lanes.**
  - The default run is `-m "not execution"` (`pyproject.toml:46-50`). License-gated tests use `requires_license` (`tests/conftest.py:20-34`).
  - The execution lane binds simkit through `CODEGEN_EXECUTION_PROVENANCE` and `TEAX_SIMKIT_PATH` (`tests/execution/conftest.py:15-24`; `tests/helpers/teax_discovery.py:8`).
  - `tests/execution/test_numeric_evidence_teax.py:33-86` already runs a full simkit study (StudyRunner, PreparedListStrategy, StudyStore, StudyQuery) on a generated package. It is the route precedent for the fixture.
- **Fixtures.** No generated package is committed anywhere. 22 fixtures commit a v6 snapshot. Capture is deterministic: "the same model in the same environment produces byte-identical snapshot files" (`envelope.py:44-45`). That is what lets integrate's gate 4 pass on a fixture. `jsonschema` is imported nowhere today.
- **fusion-tea consumers.** `CONSUMER_ATTRIBUTES.md` names 32 distinct module attributes once its one false positive (`manifest.json`) is dropped; Appendix C sorts them into the two tiers. It also carries the 17 generated package names and 20 key prefixes SC5's test needs, and the pre-move record documents SC7 needs.
  - `whole_plant_conversion/studies/replay.py:161` builds `scripts/study/verify.py` as a file path.
  - `study_route.py` modules import `scripts.study` with the project root on `PYTHONPATH` (`integrate.py:292`).
- **fusion-tea's 51 study test files** (classified file by file, Appendix F): 15 are package-agnostic whole, 12 have agnostic functions, and 24 are fusion-specific. That is more than the epic's "about twelve".
- **verify's oracle contract** is `operand_bindings()` → `{constraint_id: {operand: {"kind": "input" | "channel", "key": ...}}}` (`verify.py:141-172`). The fixture's oracle publishes exactly this.

## Core Concept

The study layer becomes one subpackage, `sysml_codegen.study`, plus a skill bundle that the existing `install-commands` delivers through agentic-mbse's installer.

Every change the closed list allows comes from one fact: the original code located everything relative to where its own file sat, and installed code cannot. So the design names three roots once, in one module (`study/roots.py`), and sends every former `__file__` question to the root it actually meant:

- **project root** — for every path a document cites. It is `SYSML_CODEGEN_PROJECT_ROOT` when set, otherwise the git work tree the tool runs in.
- **tool home** — for tool identity. It is the directory that holds the installed `sysml_codegen` package.
- **teax root** — for teax. It is `TEAX_SIMKIT_PATH`, or wherever `simkit` imports from.

Some facts fusion-tea hard-coded about itself: its two repo-scope test files, its extra environment variables, its costing distribution, and its backup prefix. These become one declaration table the target writes in its own `pyproject.toml`.

Installation reuses agentic-mbse's `Installer` with a separate manifest. The two installers then share one set of ownership rules and never see each other's files.

fusion-tea adopts later. It swaps its local copies for module aliases that pin its own root, so every consumer and every committed record keeps working.

**Why this is right, not just working.** The root split is the minimum change that makes installed code correct, and doing it in one module makes it auditable. The declaration turns the only target-specific facts `integrate` holds into data the target owns, which is D8's intent. Reusing the installer keeps one implementation of the ownership rules (`CLAUDE.md` "Change Coordination": "There is one installer"). Everything else stays byte-faithful, and SC12 proves it.

## Key Bets

- **B1.** Every target that runs studies is a git work tree, and its top level is the project root a user means. The tools already require git: preflight's clean gate and integrate's audited-work commit. *If false →* a target outside git, or a tool run from outside the tree, is refused (exit 2) until it sets `SYSML_CODEGEN_PROJECT_ROOT`. It never emits different bytes.
- **B2.** agentic-mbse's ownership rules do not depend on which manifest file they persist to. Its own installs never touch paths that are absent from its own manifest. *If false →* re-running one installer removes, or prompts for, the other's files, and SC2 fails. Coexistence tests in both repos check this, in both orders.
- **B3.** A moved tool's output depends only on its inputs, the project root, the tool home and the environment's teax. Nothing else in fusion-tea's layout leaks into a document. *If false →* SC12 finds an unlisted difference, the move is not byte-faithful, and the orchestrator must add a closed-list item.
- **B4.** A neutral model of about 40 lines, generated by this branch, runs on stock teax through the stock study lifecycle, as `test_numeric_evidence_teax.py` does. *If false →* verify and integrate's `CANDIDATE` are unreachable on the fixture. Cut 2 applies, and verify keeps negative-case coverage only.
- **B5.** fusion-tea's consumers depend only on names, signatures and project-root-relative behavior. So module aliases that pin fusion-tea's root keep all ~36 consumers, `replay.py`'s path-built command, and its cwd-determinism tests working. *If false →* adoption needs consumer rewrites (DD14's rejected alternative). The rehearsal's run C (Appendix H) shows it before merge.
- **B6.** Nobody resolves agentic-mbse by version: every install is by git revision or path. *If false →* for example, if agentic-mbse is published to an index, a version bound becomes worth its snapshot cost (premise conflict 1).

## Key Decisions

Numbered DD to keep them apart from the spec's D6–D11, which stay settled.

- **DD1 · Package name and layout (OQ4).**
  - The package is `src/sysml_codegen/study/`: the eight moved modules, four new ones (`roots`, `census`, `declarations`, `__init__`), and `schemas/` with the seven files byte-identical.
  - The installable files go in `src/sysml_codegen/assets/` (Appendix A).
  - Tool paths read `sysml_codegen/study/<tool>.py`. The repo names subpackages by concern with one noun (`extraction`, `elaboration`, `snapshot`, `contracts`), and P-001 already names "the study layer".
  - *Rejected:* a top-level `studytools` package (a second import root in one wheel); `sysml_codegen.tools.study` (an extra level for one package).
- **DD2 · Project root (OQ3).**
  - `roots.project_root()` uses `SYSML_CODEGEN_PROJECT_ROOT` when it is set. Otherwise it uses `git rev-parse --show-toplevel` run in the current directory. If neither gives a root, it raises `RootError`, and each tool's `main` turns that into a stderr message and exit 2, the code argparse already uses for an unrunnable invocation.
  - Results are cached per (variable value, cwd).
  - `roots.TOOL_HOME = Path(__file__).resolve().parents[2]`. This is the one place `__file__` is right, because it asks where the tool's own sources are.
  - `integrate` exports the resolved root to every producer, so they all agree with the seam.
  - *Rejected:*
    - cwd alone, because output would vary by invocation directory;
    - a `--project-root` flag on four parsers, because it changes every `command` argv and every caller;
    - the git top level of `--package`, because library calls have no package and it would make two mechanisms.
- **DD3 · Tool CLI shape (OQ2).**
  - The supported form is `sysml-codegen study <tool> [args]`. It passes the arguments unchanged to `<tool>.main(argv)` and exits with its code. `python -m sysml_codegen.study.<tool>` is equivalent.
  - `integrate` launches its producers as `[sys.executable, "-m", "sysml_codegen.study.<tool>", …]` and the generator as `[sys.executable, "-m", "sysml_codegen", "generate", …]` (B3).
  - `tool.path`, `verify`'s `command[0]`, and integrate's `command[0]` and `SEAM_PATH` all equal the tool-path literal (B2). This keeps the existing rule that `command[0]` is the tool's path.
  - *Rejected:*
    - four console scripts, because the repo has one entry point with subcommands;
    - `python -m` only, because it is not discoverable from `sysml-codegen --help`;
    - recording the invocation form in `command[0]`, because it breaks the schema's "identical bytes for identical facts".
- **DD4 · Installer mechanism (OQ1).**
  - Reuse agentic-mbse's `Installer` through a small public API change (Appendix B): a `manifest=` parameter, an extracted `install_bundle()`, and `INSTALLER_API_VERSION`.
  - sysml-codegen keeps its own manifest at `.sysml-codegen/install.json`. It installs `run-study` through `install_bundle` (`.agents/skills/run-study/` plus the `.claude/skills/run-study` link), `teax-completion` through `Installer.write`, and the policy through the project-document rule (DD6).
  - *Rejected:*
    - a standalone installer, because it would be a second implementation of the same ownership rules;
    - subclassing to swap manifests, because it couples to the `files` attribute and the manifest format;
    - a shared manifest, because agentic-mbse would then see `run-study` as one of its own retired bundles.
- **DD5 · Dependency guarantee (OQ1).**
  - No version bump. The bound stays `agentic-mbse>=0.1.3,<0.2`.
  - `_upstream_pins.INSTALLER_API_VERSION = "installer/v1"` is checked by `tests/conformance/test_upstream_pins.py`, and at `install-commands` start by `require_installer_api()` in `cli/install.py`. On a mismatch it exits 1, naming the agentic-mbse revision needed.
  - fusion-tea's pin must reach the agentic-mbse merge that carries the API (runbook step 2).
  - *Rejected:* bumping to 0.1.4 with a raised bound. See premise conflict 1.
- **DD6 · Assistants and ownership.**
  - `--assistant {claude,codex,both}` defaults to `both`. The skill installs for whichever is selected. `teax-completion`, a Claude command, installs when `claude` is selected.
  - `modeling_project/STUDY_POLICY.md` follows the project-document rule. It is created when absent and otherwise left untouched. `--force` replaces it. It stays out of the managed manifest, so later runs never treat it as tool-owned.
  - The noninteractive prompt answer is `skip`, which preserves local edits.
  - *Rejected:* routing the policy through `Installer.write`, which would make it a managed asset that a re-install refreshes.
- **DD7 · Skill files in the wheel.**
  - The skill files go under `src/sysml_codegen/assets/` and ship with the existing hatch configuration. `claude/commands/teax-completion.md` moves there too.
  - `get_commands_dir()` and `CODEGEN_COMMANDS` are deleted.
  - *Rejected:* `force-include` of a repo-root directory (new build configuration and a second data root); `importlib.resources` traversal (`Installer.copy_tree` needs real paths).
- **DD8 · Target declarations (OQ5).** The target declares its integrate facts in `[tool.sysml-codegen.integrate]` in the project root's `pyproject.toml`:
  - `gates.pinned-packages` and `gates.model-family-spine`: pytest targets run from the project root;
  - `environment`: the extra variables gate 0 sweeps;
  - `record-distributions`: toolchain key → distribution name, recorded between `sysml_codegen` and `teax_revision`;
  - `backup-prefix`: B10's parameter.

  The table is validated strictly. Anything malformed blocks at gate 0 with `input-invalid`. Rows 1a and 5 of the per-invocation gate table carry the declared target as `producer`, or `not declared`; an undeclared gate raises `unasked` (D8). fusion-tea's declaration reproduces today's return byte for byte (Appendix D).
  - *Rejected:*
    - a manifest field, because the schema is byte-identical and its validator rejects unknown keys;
    - CLI flags, because this is a repository property and would be repeated on every invocation;
    - a dedicated file, because `pyproject.toml`'s `[tool.*]` table is the standard home.
- **DD9 · Census home (B11).**
  - `by_entry_type(package_root) -> dict[str, set[str]]` in `sysml_codegen/study/census.py` is fusion-tea's helper verbatim (`test_model_family_spines.py:174-182`, `_contract` and `_by_entry_type`), raw JSON in, the same sets out.
  - `integrate.rederived_census` keeps its name and calls it.
  - *Rejected:* a typed version in `sysml_codegen.contracts`. Pydantic could refuse a contract the original accepted, and the helper would leave the study digest set.
- **DD10 · teax discovery (OQ6).**
  - `TEAX_SIMKIT_PATH`, this repo's existing lane variable, names a simkit root. `integrate` prepends it to its producers' `PYTHONPATH`, and gate 0 requires `simkit` to import from inside it.
  - Without the variable, teax is whatever `simkit` the producers' environment imports.
  - Gate 1b runs `git rev-parse HEAD` at that location. If the location is not a checkout, gate 1b gives the existing could-not-run blocker, never a pass (B7).
  - `read_coverage` declares `TEAX_SIMKIT_PATH` and its `*.egg-info` (B8). The guide tells operators to set the variable whenever teax is a checkout. Without it, an editable simkit outside the runtime is an undeclared read, and gate 7 refuses, naming the file.
  - `verify` keeps importing from the environment and raises a named teax error (B9).
  - *Rejected:*
    - `STOP_PARSER_TEAX_ROOT`, a fusion-tea name banned by SC5;
    - a checkout-root variable plus the `packages/teax-simkit` suffix, which bakes teax's internal layout into the tools;
    - making `verify` read the variable, which is a behavior change not on the closed list.
- **DD11 · Record, annex and log locations (OQ7).**
  - Each studied package has one *studies directory*. The study policy's § Locations names it.
  - It holds `ANNEX.md`, `DISCOVERY_LOG.md` and one `<study-id>/` per record.
  - fusion-tea's `exploration/<pkg>/studies/` becomes its policy's Locations entry, with a ledger row.
  - *Rejected:* a fixed `studies/` at the project root, which moves fusion-tea files or makes fusion-tea an exception; deriving the directory from the package path, because fusion-tea's packages sit at different depths.
- **DD12 · Record checks (OQ8).**
  - No shipped check in this item. Runbook steps 14 and 15 state each condition with a concrete check the executor runs (Appendix I).
  - SC4's evidence runs `evidence/dry-run/check_record.py`, ported from fusion-tea's `test_records.py`. A backlog follow-up ships it as `sysml-codegen study check-record`.
  - *Rejected:* shipping it now (a new tool outside the estimate); an installed pytest template (it must find records across policy-named locations).
- **DD13 · Fixture (OQ9).**
  - A new neutral model, `tests/fixtures/study_station/`, a pump station of about 40 lines. Its package is generated by this branch, the manifest is literal, and it has a hand-written oracle, a stock-route module, committed baseline documents, a census, gate stand-ins and a declaration (Appendix E).
  - `synthetic_pkg` moves for the indicators-only tests.
  - *Rejected:* extending `synthetic_pkg` (no SysML source and no seal, so verify and gates 2–4 are unreachable); `wi014_toy` (a fusion-tea file, premise conflict 3).
- **DD14 · fusion-tea wrappers (OQ11).**
  - Each fusion-tea `scripts/study/<m>.py` and `scripts/integrate.py` becomes a short module alias. It sets `SYSML_CODEGEN_PROJECT_ROOT` to fusion-tea's root, computed from its own location (`parents[2]` under `scripts/study/`, `parents[1]` for `scripts/integrate.py`), which is today's meaning. It runs `main()` when executed, and otherwise replaces itself in `sys.modules` with `sysml_codegen.study.<m>`, so monkeypatching reaches the real module.
  - *Rejected:* rewriting about 36 consumers' imports. That is a larger diff, it breaks `replay.py:161` and fusion-tea's tmp-cwd determinism tests, and it changes committed protocol documents.
- **DD15 · Rehearsal separation (OQ12).** Three runs of fusion-tea's suite on the disposable copy:
  - **A** — as-is;
  - **B** — dependencies moved, local tools still in use;
  - **C** — after the switch.

  Failures in C but not B are the move's. Failures in B but not A belong to the generator and agentic-mbse jump (Appendix H).
- **DD16 · Policy template (OQ13).**
  - The template keeps the general rules (§§ 1–5, 9, 11 of the original) with their grade and date. A header says the grades record where each rule came from and that the target has ratified nothing until it records its own ratification.
  - Worked examples stay as labelled examples, with fusion vocabulary allowed and identifiers stripped.
  - Target slots are typed `<...>` placeholders: § Locations (new), § Execution routes, § Hypotheses, and an empty § Tripwire record.
  - There is no oracle section (epic).
  - *Rejected:* placeholders only, which loses the examples that make the R1–R4 ladder usable; examples verbatim, which keeps identifiers and fails SC5.
- **DD17 · Operator guide home (OQ14).**
  - The guide ships inside the bundle as `integration-guide.md`, beside the runbook, and refreshes with it.
  - The skill and runbook cite it as a sibling file.
  - The guide-contract test moves and is rewritten for the shipped guide.
  - *Rejected:* a resolver command (new mechanism); a project document (it would freeze at first install and drift from the code).
- **DD18 · Annex template.** The bundle ships `annex-template.md`, with the four sections the runbook reads and a list of the package-owned pieces: manifest, axis declaration, route and oracle. A contract test checks that every annex section the runbook cites exists in the template. *Rejected:* guidance prose in the runbook, which a test cannot hold to the runbook's citations.
- **DD19 · Smells.**
  - **Removed:** the `if __package__` path inserts (`indicators.py:42-43`, `preflight.py:55-56`, `verify.py:49-50`, `integrate.py:77-78`). They exist only to make `scripts.study` resolve, and inside a package they would put site-packages' parent on `sys.path`.
  - **Kept as written, each named as a follow-up, not fixed here:**
    - argparse `prog="indicators.py"` and its siblings (stderr only);
    - `indicators.write_atomically`, which duplicates `common.write_document`;
    - `read_coverage.py`'s untyped style;
    - `integrate.py`'s size.
  - **Typing:** the ported modules go under one recorded mypy override that turns off `disallow_untyped_defs`. New modules are fully typed. Ruff findings in ported code are handled by recorded per-file ignores, never by byte edits.

## Architecture

```
target project (git work tree = project root)               installed sysml-codegen (tool home)
  pyproject.toml [tool.sysml-codegen.integrate] ──────────┐   sysml_codegen/study/roots.py   (three roots)
  modeling_project/STUDY_POLICY.md     (project document) │   sysml_codegen/study/*.py       (eight moved, census, declarations)
  .agents/skills/run-study/*  + .claude/skills/run-study   │   sysml_codegen/study/schemas/   (seven, byte-identical)
  .sysml-codegen/install.json          (own manifest)     │   sysml_codegen/assets/          (skill, command, policy template)
  <studies-dir>/{ANNEX.md, DISCOVERY_LOG.md, <study-id>/} │
  package, manifest, axes, route, oracle ─────────────────┴──> sysml-codegen study <tool> ──> documents
teax checkout: TEAX_SIMKIT_PATH ──> producers' PYTHONPATH, gate 0 and 1b, read-coverage declared root
agentic-mbse (installation.py) <── cli/install.py: Installer(manifest=".sysml-codegen/install.json"), install_bundle()
```

**Install flow.**

1. `install-commands` checks `INSTALLER_API_VERSION` and builds an `Installer` on its own manifest.
2. It calls `install_bundle` for each bundle under `assets/skills/`, then writes `teax-completion`.
3. It applies the project-document rule to the policy, saves, and prints agentic-mbse-style actions.

**Tool flow.** Each `main()` first resolves the project root (exit 2 if none), then runs unchanged code. Every path in a document is `repo_relative_posix` against the project root. `tool` blocks are literals under the tool home.

**integrate flow.**

1. Gate 0: load the declaration (`input-invalid` on failure), build the request, sweep `REQUIRED_ENV + declared` and teax (`env-missing`), then the clean check.
2. Build the per-invocation gate table.
3. Run the ten gates in order, with producers as `sys.executable -m` subprocesses under `seam_env`. That is the project root and `TEAX_SIMKIT_PATH` on `PYTHONPATH`, plus `SYSML_CODEGEN_PROJECT_ROOT` and `STUDY_REQUIRE_TEAX=1`.
4. Return as today.

**Boundaries.** Dependencies run one way: agentic-mbse imports nothing from sysml-codegen (ADR-0007). Inside sysml-codegen, `cli/install.py` imports `agentic_mbse.cli.installation`. `sysml_codegen.study` reaches agentic-mbse only through `sysml_codegen.snapshot.capture`, which integrate imports lazily at gate 4 (`integrate.py:1078`); that is its only import from the rest of sysml-codegen. teax loads lazily, as today.

## Required Invariants

- **I1. Byte-faithful outside B1–B11.** The same inputs give the same documents and exit codes, apart from the closed-list fields (SC12, Appendix G).
- **I2. Schemas.** The seven schema files equal fusion-tea `b06585709` byte for byte. A suite test pins their seven sha256 values.
- **I3. Paths.** Every path a document cites is relative to the project root, and is the same from any working directory in the project. Outside a project a tool exits 2 and writes nothing. It never writes different bytes.
- **I4. Tool identity.** `tool.path` and every `source_digest.files[].path` start with `sysml_codegen/study/`. `command[0] == tool.path`. Each digest recomputes from the bytes under the tool home with the unchanged recipe.
- **I5. Installer isolation.** Each installer reads and writes only its own manifest and prunes only under its own bundles' prefixes.
- **I6. The policy.** An existing `STUDY_POLICY.md` is never written unless `--force` is given.
- **I7. integrate's contract.**
  - Ten gates in order, two return classes, fifteen slugs, exit codes 0, 1 and 2.
  - A `CANDIDATE` only when all ten gates passed.
  - An undeclared repo gate gives `BLOCKER`, `could_not_run`, `input-missing`.
- **I8. Dependency direction.** agentic-mbse imports nothing from sysml-codegen. `sysml_codegen.study` imports teax only inside functions that need it.
- **I9. Without teax.** `verify` exits 1, names teax, and writes no document. `integrate` exits 1 with its `BLOCKER` return naming teax at gate 0 and runs no producer (premise conflict 4).
- **I10. Generic text.** No shipped text or tool module carries an identifier from SC5's closed lists. The single exception is the record template's history note.

## Component Overview

| Component | Location | Responsibility |
|---|---|---|
| Roots | `src/sysml_codegen/study/roots.py` (new) | Project root, `TOOL_HOME`, `TEAX_SIMKIT_PATH`, `RootError`, `require_project_root(prog)` |
| Moved tools | `src/sysml_codegen/study/{common,manifest,identity,indicators,preflight,verify,read_coverage,integrate}.py` | Fusion-tea's code at `b06585709` plus the edits in Appendix A |
| Census | `src/sysml_codegen/study/census.py` (new) | `by_entry_type`, for gate 4 and fusion-tea's spine test |
| Declarations | `src/sysml_codegen/study/declarations.py` (new) | Reads and validates `[tool.sysml-codegen.integrate]` |
| Study CLI | `src/sysml_codegen/cli/__init__.py` (`study` subparser, `cmd_study`) | Dispatches `sysml-codegen study <tool>` |
| Installer | `src/sysml_codegen/cli/install.py` (new) | `install_commands()`, `list_assets()`, `prompt_decision()`, `require_installer_api()` |
| Shipped text | `src/sysml_codegen/assets/skills/run-study/` | `SKILL.md`, `runbook.md`, `record-template.md`, `annex-template.md`, `integration-guide.md` |
| Policy template | `src/sysml_codegen/assets/project_templates/STUDY_POLICY.md.template` | Dated snapshot of the general rules plus slots |
| Upstream pin | `src/sysml_codegen/_upstream_pins.py` | Gains `INSTALLER_API_VERSION` |
| agentic-mbse API | agentic-mbse `src/agentic_mbse/cli/installation.py` | `manifest=`, `install_bundle()`, `INSTALLER_API_VERSION` (Appendix B) |
| Fixture | `tests/fixtures/study_station/` | Neutral model, package, study inputs and gate stand-ins (Appendix E) |
| Tests | `tests/study/`, `tests/unit/test_install_commands.py`, `tests/execution/test_study_*.py` | The three lanes (Appendix F) |
| Evidence | `.project/active/study-layer-to-codegen/evidence/` | Parity script, read-through, runbook draft, transcripts (Appendices G–I) |

## Non-Goals

- Changing study semantics beyond B1–B11, teax APIs, or any committed study record (spec).
- Moving fusion-tea's pin, merging, pushing, or writing to fusion-tea's main checkout. The owner does these.
- Fusion-specific study tests, fusion-tea's annexes, and regenerating fusion-tea's packages.
- Shipping a record checker (DD12 files it as a follow-up), fixing the kept smells (DD19), and changing agentic-mbse's version (DD5).
- Policy § 10's oracle conflict. Out of scope: the template carries no oracle obligation, because the epic leaves that decision to fusion-tea.

## Implementation Notes

- **Order.**
  1. The agentic-mbse change goes on an agentic-mbse branch, with its own tests and full suite (Appendix B).
  2. Install it here with `uv pip install -e <agentic-mbse worktree>` and run with `uv run --no-sync`, because `[tool.uv.sources]` points at `../agentic-mbse`.
  3. The sysml-codegen package comes next. The fixture follows (it needs the license for snapshot capture), then the tests.
  4. Text, evidence and docs come last.
- **Port mechanically first.**
  - Copy the eight modules and seven schemas byte for byte and commit that copy as its own commit. SC12's edit map then reads as one diff.
  - Then apply Appendix A's edits, tagged with B-ids in the commit messages.
- **Literals over derivation.**
  - `TOOL_SOURCE_FILES` and `tool.path` are string literals.
  - A test asserts that each literal resolves under `TOOL_HOME`, that each tool's `tool.path` is in its own list, and that every module the tool imports from `sysml_codegen.study` is listed. The new `roots.py` joins the lists of `manifest`, `preflight` and `verify`. `census.py` and `declarations.py` join integrate's list.
- **mypy and ruff.**
  - Add one `[[tool.mypy.overrides]]` block with `disallow_untyped_defs = false`, whose `module` list names the eight ported modules one by one (`sysml_codegen.study.common`, `…manifest`, `…identity`, `…indicators`, `…preflight`, `…verify`, `…read_coverage`, `…integrate`).
  - Add `ignore_missing_imports` for `simkit.*` if mypy needs it.
  - Annotation-only fixes are allowed by the closed list. Any other mypy or ruff finding in ported code gets a recorded override or per-file ignore, listed in the plan with its rule code.
- **The fixture's gate stand-ins** are named `gates/check_*.py`, so this repo's pytest never collects them. The declaration runs them as explicit pytest targets. If pytest refuses an explicit non-`test_` file, name them `test_*.py` and add `collect_ignore` for `tests/fixtures/study_station/gates` in `tests/conftest.py`.
- **`jsonschema`** joins the `dev` extra. Re-lock this repo with `uv lock`.
- **The `if __package__` removal** counts as part of the import rewrite. Note it in the edit map so SC12's reviewer does not read it as an extra change.
- **`sysml-codegen study`** uses `argparse.REMAINDER` after a `tool` positional. A test pins that `sysml-codegen study verify --help` prints verify's own usage.

## Potential Risks

- **The agentic-mbse change must merge first.** Mitigation: it is small and lands on its own branch with an explicit merge commit before sysml-codegen merges (ADR-0008). `require_installer_api()` gives a clear failure on any environment that lacks it.
- **The fixture route fails on stock teax (B4).** Mitigation: the route copies `test_numeric_evidence_teax.py`'s lifecycle. The first plan phase builds the route and checks it in the execution lane before anything depends on it. Cut 2 is the release valve.
- **The committed fixture package drifts from the generator.** Mitigation: one license-gated test regenerates it from the committed snapshot and compares bytes, and its failure message names the regeneration commands (Appendix E). This is the coupling the spec accepted.
- **An unlisted difference surfaces in SC12.** Mitigation: the parity script measures run-to-run noise empirically before it compares. Any remaining difference stops the item and goes to the orchestrator; no mask is added silently.
- **fusion-tea tests that pin old strings or internals break at adoption.** Examples are `test_output_contract.py:317`, `test_verify.py:234`, `test_integrate_preconditions.py:146` and `SCHEMA_DIR`. Mitigation: rehearsal run C lists them, and the runbook's step 5 carries each edit.
- **Two copies drift between merge and adoption.** Mitigation: the runbook's drift check (step 1) stops the switch. The moved package is the authority from merge (spec § Delivery).

## Integration Strategy

- **Merge order.** The agentic-mbse branch (API change) merges first, then sysml-codegen `study-layer-to-codegen`. Both use explicit merge commits (ADR-0008). fusion-tea adopts later through the runbook: the owner moves the pin, then applies the switch.
- **What it complements.** agentic-mbse `init` installs the goal layer and project scaffold. `sysml-codegen install-commands` adds the study layer next to them. The runbook's review-scope rule cites "the installed goal runbook" and states its own fallback when the goal layer is absent.
- **What it replaces.** The single-file `install-commands` (`cli/__init__.py:1018-1050`). fusion-tea's local skill, policy-as-template and tools, at adoption.
- **Docs.** `README.md` and the `CLAUDE.md` overview gain the study layer, `install-commands` and `sysml-codegen study`. At close, a product-ledger entry cites the owner's 2026-10-06 decision (spec § Instruction text).

## Validation Approach

| Criterion | How it is checked | Where |
|---|---|---|
| SC1 | Suite test that the assets live inside the package and that `install_commands` lays them out. The install transcript from wheels, built at both branches, with neither checkout on the path | `tests/unit/test_install_commands.py`; `evidence/install-transcript.md` (Appendix H1) |
| SC2 | Noninteractive tests: refresh, preserve, prompt hook, policy kept and replaced under `--force`, coexistence with `agentic-mbse init` in both orders | `tests/unit/test_install_commands.py`; agentic-mbse's installer tests |
| SC3 | Each tool completes and fails closed, in three lanes | Appendix F |
| SC4 | Dry run from installed files, record checks, cold administrator reading | `evidence/dry-run/` (Appendix H2) |
| SC5 | Grep test over shipped text and modules; per-line read-through | `tests/study/test_generic_text.py`; `evidence/read-through.md` (Appendix I) |
| SC6 | Attribute existence and signature test against a table captured at `b06585709` | `tests/study/test_compat_surface.py` (Appendix C) |
| SC7 | Tool-path prefix and digest recompute; committed pre-move documents; schema sha pins | `tests/study/test_tool_identity.py` |
| SC8 | Undeclared gate, declared gate, declaration validation, env sweep, toolchain keys | `tests/study/test_integrate_declared.py` and the licensed and execution lanes |
| SC9 | Runbook draft and A/B/C rehearsal | `evidence/fusion-tea-runbook.md`, `evidence/rehearsal/` (Appendix H3) |
| SC10 | Ledger rows from the read-through's moved verdicts, plus a fusion-tea branch diff | Appendix I |
| SC11 | Full suites here (baseline 2206 passed, 9 skipped, plus new) and in agentic-mbse; ruff and mypy clean under the recorded overrides | plan's final phase |
| SC12 | Parity script on identical inputs | `evidence/parity/` (Appendix G) |

## Next-Stage Handoff

- **Fixed:**
  - DD1–DD19;
  - the module and file names in Appendices A–E;
  - the declaration format;
  - the CLI forms;
  - the agentic-mbse API;
  - the test lanes;
  - the parity method;
  - the runbook steps;
  - the read-through format.
- **Open for the plan:**
  - exact test-file splits inside `tests/study/`;
  - the per-file ruff ignores that turn out to be needed;
  - the fixture's literal values (fingerprints, pins), which come from the first generation;
  - the agentic-mbse test file name, which follows its convention.
- **De-risk first:**
  1. The fixture route on stock teax (B4).
  2. The agentic-mbse change and the coexistence test (B2).
  3. The root split, so that `indicators` on the fixture equals the original layout's output (the repack check's step 5, now with D7 identity).
- **Estimate.** About 43h execute against the spec's 37.5h (Appendix J). The cut order is unchanged.
  - One lever beyond the cuts, for the orchestrator only: leave the lower-value test moves in fusion-tea as a recorded deferral, saving about 2h. Those are `test_provenance`, `test_valid_empty`, `test_read_set_coverage`, `test_absolute_tolerances`, `test_multipipeline`, `test_subset_flag`, `test_integrate_restore` and the merged partial functions. They keep running against the moved code through the wrappers.
- **ADR candidates after approval** (builder register, via `adr.sh new`):
  - "Study tools resolve the project root from `SYSML_CODEGEN_PROJECT_ROOT` or the git work tree";
  - "Reuse agentic-mbse's installer through an API version pin, not a package-version bound".

---

## Appendix A — Package layout and the edit map

```
src/sysml_codegen/study/{__init__,roots,common,manifest,identity,indicators,preflight,verify,read_coverage,integrate,census,declarations}.py
src/sysml_codegen/study/schemas/{axis_declaration,baseline_result,indicators,package_identity,preflight_results,study_package_manifest,verification_summary}.v1.schema.json
src/sysml_codegen/assets/skills/run-study/{SKILL,runbook,record-template,annex-template,integration-guide}.md
src/sysml_codegen/assets/commands/teax-completion.md                  (git mv from claude/commands/)
src/sysml_codegen/assets/project_templates/STUDY_POLICY.md.template
```

`study/__init__.py` holds a docstring that names the supported API (Appendix C) and imports nothing.

**`roots.py` (new, fully typed).**

```python
PROJECT_ROOT_ENV = "SYSML_CODEGEN_PROJECT_ROOT"
TEAX_SIMKIT_PATH = "TEAX_SIMKIT_PATH"
TOOL_HOME: Path = Path(__file__).resolve().parents[2]   # the directory holding sysml_codegen/
class RootError(Exception): ...
def project_root() -> Path: ...                          # env var, else git top level of cwd, else RootError
def require_project_root(prog: str) -> Path: ...         # stderr "<prog>: cannot find the project root ..." and SystemExit(2)
def teax_simkit_path(env: Mapping[str, str]) -> Path | None: ...
```

**Edits per moved module.** Every module gets the import rewrite (`scripts.study` → `sysml_codegen.study`) and the SC5 docstring edits. SC5's docstring edits remove fusion-tea pointers: `ADR-009`, `R-B1`, `R-E4`, `ADR-006`, `R-A3`, "design D10", "Item 3's", "Invariant 1", "M4", "M5", and the guide path. The rule wording stays.

| Module | Edits beyond the import rewrite | B |
|---|---|---|
| `common.py` | `tool_source_digest(files)` reads `roots.TOOL_HOME / rel` (`:43-49`) | D7/B2 |
| `manifest.py` | `repo_root()` returns `roots.project_root()` (`:57-59`); `TOOL_SOURCE_FILES` → `sysml_codegen/study/{indicators,manifest,roots}.py` + three schemas (`:35-41`); `tool_source_digest()` under `TOOL_HOME` (`:149-162`) | B1, B2 |
| `identity.py` | none (adapter sources stay project-root-relative, `:225`) | — |
| `indicators.py` | remove insert (`:42-43`); `tool.path` literal (`:862`); `main` calls `require_project_root("indicators")` | B1, B2 |
| `preflight.py` | remove insert (`:55-56`); `TOOL_SOURCE_FILES` paths + `roots.py` (`:66-74`); `tool.path` ×2 (`:430,:449`); `main` requires the root | B1, B2 |
| `verify.py` | remove insert (`:49-50`); `TOOL_SOURCE_FILES` paths + `roots.py` (`:60-67`); `tool.path`, `command[0]` (`:517,:520`); `import simkit` (`:484`) → `_import_simkit()` raising `VerifyError` that names teax; `main` requires the root | B1, B2, B9 |
| `read_coverage.py` | declared roots (`:94-101`): route dir, `TOOL_HOME / "sysml_codegen"`, `TEAX_SIMKIT_PATH` and its `*.egg-info` | B7, B8 |
| `integrate.py` | see below | B1–B7, B10, B11 |

**`integrate.py` edits.**

- **Imports and tool paths.**
  - Remove the insert (`:77-78`). Rewrite the imports, including the driver source (`:1216-1221`).
  - `SEAM_PATH` becomes `sysml_codegen/study/integrate.py` (`:84`).
  - `TOOL_SOURCE_FILES` becomes package paths plus `roots`, `census` and `declarations` (`:89-97`).
- **Environment and teax.**
  - `REQUIRED_ENV = ("SYSIDE_LICENSE_KEY",)` (`:128-135`), and `TEAX_SIMKIT_SUBPATH` goes (`:139`).
  - `seam_env` (`:282-299`): `PYTHONPATH` gets the project root and `TEAX_SIMKIT_PATH`, and `SYSML_CODEGEN_PROJECT_ROOT` is set.
  - The teax location is `TEAX_SIMKIT_PATH`, or the parent of the probe's simkit directory. `teax_revision()` runs there (`:316-321, :959`).
  - `toolchain_block(env, declaration)` (`:332-346`): the keys are `agentic_mbse`, `sysml_codegen`, the declared keys in order, then `teax_revision` and `teax_module_path`.
  - `assert_environment(env, declaration)` (`:502-536`): it sweeps `REQUIRED_ENV + declared` in that order, deduplicated. The teax checks name `TEAX_SIMKIT_PATH`. The no-teax message reads "teax is not available to the seam's producers: simkit does not import; set TEAX_SIMKIT_PATH to a teax checkout's simkit root".
- **Gate table and producers.**
  - `gate_table(declaration)` replaces rows 1a and 5 of `GATES` (`:188-209`) with the declared target as `producer`, or `not declared`.
  - The manifest, preflight and verification producers become tool paths. The census-snapshot producer becomes `sysml_codegen.snapshot.capture; sysml_codegen/study/census.py`.
  - `run_sequence`, `gate_rows` and `build_return` take the table instead of reading the module constant.
- **Repo gates.** `gate_pinned_packages` and `gate_model_family_spine` (`:939-946, :981-992`) run the declared target, or raise `unasked(gate, "the target declared no producer for this repo-scope gate; declare one under [tool.sysml-codegen.integrate.gates] in pyproject.toml")`.
- **Launches.**
  - `[sys.executable, "-m", "sysml_codegen.study.preflight", …]` replaces the script path at `:552` and `:1304`, and `…verify` replaces it at `:1353`. The producer strings at `:558` and `:1270` become tool paths.
  - The generator launch becomes `[sys.executable, "-m", "sysml_codegen", "generate", …]` (`:1006`).
- **Census.** `rederived_census` imports `census.by_entry_type` (`:1098`). The census-stale producer becomes `sysml_codegen/study/census.py::by_entry_type` (`:1161`).
- **Backup prefix.** `tempfile.mkdtemp(prefix=declaration.backup_prefix)` (`:1506`). The default is `sysml-codegen-integration-backup-`.
- **Run order.** `run()` loads the declaration first. A `DeclarationError` becomes `precondition_blocker("input-invalid", …)`.

**`declarations.py` (new, fully typed).**

```python
REPO_GATES = ("pinned-packages", "model-family-spine")
FIXED_TOOLCHAIN_KEYS = ("agentic_mbse", "sysml_codegen", "teax_revision", "teax_module_path")
DEFAULT_BACKUP_PREFIX = "sysml-codegen-integration-backup-"
@dataclass(frozen=True)
class IntegrateDeclaration:
    gates: dict[str, str]; environment: tuple[str, ...]
    record_distributions: tuple[tuple[str, str], ...]; backup_prefix: str
class DeclarationError(Exception): ...
def load_declaration(project_root: Path) -> IntegrateDeclaration: ...   # no file or no table → empty declaration
```

Validation: the table keys must be within `{gates, environment, record-distributions, backup-prefix}`. Gate keys must be within `REPO_GATES`, with non-empty string values. Environment names must match `[A-Za-z_][A-Za-z0-9_]*` and be unique. Distribution keys must be identifiers that are not in `FIXED_TOOLCHAIN_KEYS`, with non-empty values. The prefix must be non-empty and contain no `/`. A TOML syntax error is a `DeclarationError`.

## Appendix B — The agentic-mbse change (exact)

File: `src/agentic_mbse/cli/installation.py`. The package version stays 0.1.3 (DD5).

1. Add `INSTALLER_API_VERSION = "installer/v1"`, with a comment: "the public surface other installers build on: `Installer(manifest=…)` and `install_bundle()`; change the string when either changes shape".
2. Change the signature to `Installer.__init__(self, target: Path, *, force: bool, decide: Callable[[str], str], manifest: str = MANIFEST) -> None`. It stores `self.manifest`. It reads `(LEGACY_MANIFEST, MANIFEST)` only when `manifest == MANIFEST`, and otherwise reads only `(manifest,)`. Behavior is unchanged for every existing call.
3. `Installer.save()` writes `self.manifest`, with the same atomic replace. The redirected-parent error names the manifest.
4. New `install_bundle(installer: Installer, source: Path, *, runtimes: tuple[str, ...], link_mode: str, dev: bool) -> None` holds the loop body of `install_assistants` (`:435-440`): the dev link or `copy_tree` into `.agents/skills/<name>`, then `expose_to_claude` when `"claude" in runtimes`. `install_assistants` calls it. This is a pure refactor.
5. `CLAUDE.md` "Change Coordination" gains one sentence: other repositories install their own bundles through `Installer` with their own manifest, and `INSTALLER_API_VERSION` marks that surface.

Tests, in agentic-mbse's installer test module:

- a custom manifest round-trips: a second run updates an unmodified file and preserves an edited one, and `.agentic-mbse/install.json` is never written;
- with both agentic-mbse manifests present, a custom-manifest `Installer` saves only its own entries;
- `install_bundle` gives the same layout as `install_assistants` for one bundle;
- a bundle installed under a custom manifest survives a noninteractive `init` and `install-commands`, and the reverse order holds too;
- `INSTALLER_API_VERSION == "installer/v1"`.

The full agentic-mbse suite passes (SC11).

**What fusion-tea's pin then needs.** fusion-tea's agentic-mbse revision must be at or after the merge commit that carries `INSTALLER_API_VERSION`. Items 1 and 2's pin moves do not reach it, so this is a further pin move with the same hand-edited lock procedure (Item 2 runbook step 1). Only the SHA changes, never the version string. If Item 2's F2 has not run yet, it can pin straight to the later merge.

## Appendix C — Import tiers (D9) and root-dependent behavior (SC6)

**Supported target API** (documented in the runbook's "What a package annex supplies" and in `study/__init__.py`):

- CLI: `sysml-codegen study {indicators,preflight,verify,integrate}`.
- Python, for a route module: `sysml_codegen.study.identity.build_sealed(package_name=, package_root=)` and `sysml_codegen.study.common.write_document(document, path)`.
- Protocols the target implements:
  - the route callable `execute_baseline(out, *, package_dir, manifest_path) -> {"identity": path, "baseline_result": path}`;
  - the oracle module's `<callable>(point) -> channels` and `operand_bindings()` (`verify.py:88-116, :141-172`).
- Document contracts: the seven schemas, shipped at `sysml_codegen/study/schemas/`.

**fusion-tea compatibility surface.** These names exist with the same behavior but are not documented. They come from `CONSUMER_ATTRIBUTES.md`.

- `common`: `ToolError`, `assert_tree_clean`, `manifest_mod`, `read_json`, `relative_deviation`.
- `identity`: none beyond the supported `build_sealed`.
- `indicators`: `build_graph`, `predicate_operands`, `read_model_contract`, `read_pipelines`.
- `manifest`: `MANIFEST_SCHEMA_VERSION`, `ManifestError`, `assert_package_identity`, `assert_pin_matches`, `indicator_input_fingerprint`, `indicator_input_read_set`, `load`, `read_executable_fingerprint`, `read_package_name`, `read_semantic_fingerprint`, `repo_relative_posix`, `validate`.
- `verify`: `TOLERANCE`, `VerifyError`, `check_case`, `derive_verdict`, `feature_refs`, `manifest_mod`, `objective_channels`, `package_input_values`.
- `integrate`: `rederived_census`.

`tests/study/test_compat_surface.py` reads `tests/study/data/compat_surface.json`. A capture script run once against the staged `b06585709` modules writes that table: per name, the kind and either the parameters (name, kind, default `repr`), the base classes, a constant's value, or module identity for `manifest_mod`. It records its provenance in the file's header. Annotations are not compared, so typing the ported code cannot fail the test.

**Root-dependent behavior.**

- `manifest.repo_root()` returns `roots.project_root()`. In fusion-tea the wrappers set `SYSML_CODEGEN_PROJECT_ROOT` to the repository root, so it returns what it returned at `b06585709`.
- `manifest.repo_relative_posix(p)` is `relpath(resolve(p), project_root())` as POSIX, unchanged given the root.
- `common.tool_source_digest(files)` and `manifest.tool_source_digest()` digest files under `TOOL_HOME`. They have no fusion-tea caller outside the moved set (spec Evidence A, finding 2), so no prior behavior is owed.

## Appendix D — CLI, installer and declaration surface

**Invocations.**

```bash
sysml-codegen install-commands [DIR] [--assistant {claude,codex,both}] [--force] [--list]
sysml-codegen study indicators --package DIR --manifest FILE --groups FILE [--group NAME]... [--out FILE]
sysml-codegen study indicators --package DIR --print-fingerprint
sysml-codegen study preflight gates --package DIR --manifest FILE --groups FILE --identity FILE --baseline-result FILE [--out FILE]
sysml-codegen study preflight clean --package DIR [--out FILE]
sysml-codegen study verify --package DIR --manifest FILE --identity FILE --store FILE... [--sample-size N] [--seed HEX] [--out FILE]
sysml-codegen study integrate --audited-work PATH@COMMIT --models-root DIR --package DIR --manifest FILE --groups FILE --route-sys-path DIR --route-module NAME --route-callable NAME --out-dir DIR [...]
```

**On-disk layout after `install-commands target`** (default `--assistant both`).

```
target/.agents/skills/run-study/{SKILL,runbook,record-template,annex-template,integration-guide}.md   managed
target/.claude/skills/run-study -> ../../.agents/skills/run-study                                    managed link
target/.claude/commands/teax-completion.md                                                           managed
target/modeling_project/STUDY_POLICY.md                                                              project document
target/.sysml-codegen/install.json                                                                   sysml-codegen's manifest
```

The `--list` output has three groups:

- "Skills (installed to .agents/skills/, linked for Claude)", with `run-study (workflow)` and the first line of its description, read through `installation.frontmatter`;
- "Claude commands", with `teax-completion`;
- "Project documents (created once, kept on re-install)", with `modeling_project/STUDY_POLICY.md`.

`prompt_decision(relative)` answers `skip` when stdin is not a TTY. On a TTY it asks for one of skip, overwrite, backup, skip all or overwrite all. It returns the strings `Installer.permit` accepts.

**Declaration: a fresh target.**

```toml
[tool.sysml-codegen.integrate]
environment = ["MYPROJ_WHEEL_DIR"]
backup-prefix = "myproj-integration-backup-"
[tool.sysml-codegen.integrate.gates]
pinned-packages = "tests/test_toolchain_pins.py"
model-family-spine = "tests/test_model_tree.py"
[tool.sysml-codegen.integrate.record-distributions]
solver = "my-solver-dist"
```

**Declaration: fusion-tea's.** This reproduces today's sweep, rows, toolchain block and prefix exactly.

```toml
[tool.sysml-codegen.integrate]
environment = ["STOP_PARSER_WHEEL_TARGET", "STOP_PARSER_AGENTIC_WHEEL", "STOP_PARSER_CODEGEN_WHEEL", "STOP_PARSER_COSTINGFE_WHEEL", "STOP_PARSER_TEAX_ROOT"]
backup-prefix = "fusion-tea-integration-backup-"
[tool.sysml-codegen.integrate.gates]
pinned-packages = "tests/test_dependency_provenance.py"
model-family-spine = "tests/models/test_model_family_spines.py"
[tool.sysml-codegen.integrate.record-distributions]
costingfe = "1costingfe"
```

fusion-tea also exports `TEAX_SIMKIT_PATH="$STOP_PARSER_TEAX_ROOT/packages/teax-simkit"` in its `.venv/integration.env`.

## Appendix E — The neutral fixture (`tests/fixtures/study_station/`)

**Model.** `models/station.sysml` defines one package, `PumpStation`, with no units, and only `out attribute` results. No calc parameter shares a name with the attribute bound to it, which avoids the self-binding trap that `wi014_toy`'s notes record.

| Element | Content | Baseline value |
|---|---|---|
| Part attributes | `design_inflow` 0.30, `basin_area` 12.0, `allowed_rise_rate` 0.005, `installed_capacity` 0.25, `pump_head` 8.0, `energy_price` 0.10 | — |
| `calc def RequiredFlow(inflow, rise_rate, area)` | `required_flow = inflow - rise_rate * area` | 0.24 |
| `calc def PumpingCost(flow, head, price)` | `annual_cost = flow * head * price * 1000.0`, with `flow` bound to `demand.required_flow` | 192.0 (the objective) |
| `constraint def CapacityCoversDemand(capacity, demand_flow)` | `capacity >= demand_flow`, asserted as `pump_fit` | satisfied |

**Axes.**

- `basin_area` reaches the constraint and the objective.
- `installed_capacity` reaches the constraint only.
- `energy_price` reaches the objective only. So it reports `no_constraint_response`, which exercises the ruling and the model-development finding.

The grid is `basin_area ∈ {4, 8, 12, 16}` × `installed_capacity ∈ {0.20, 0.25, 0.30}`: 12 points with both verdicts, so verify sees two strata.

**Files.** Everything in this directory was written for this item, and it states that in `PROVENANCE.md`.

- `PROVENANCE.md` — the regeneration commands:
  - `sysml-codegen snapshot --models models --output station.snapshot.json` (license);
  - `sysml-codegen generate --from-snapshot station.snapshot.json --output pkg/station_study --package-name station_study`;
  - re-pin the manifest with `sysml-codegen study indicators --package pkg/station_study --print-fingerprint`;
  - rerun the route in the execution lane to refresh `studies/baseline/`.
- `models/station.sysml` and `station.snapshot.json`. The snapshot sits beside the models root, which is gate 4's shape.
- `pkg/station_study/…` — the committed generated package.
- `studies/manifest.json` — literal: pin, recorded fingerprints, objective `annual_cost`, empty ties, baseline point, headline and verdict, oracle `oracle_entry.evaluate` with `sys_path` `studies`.
- `studies/axes.json` — the three axes.
- `studies/oracle_entry.py` — `evaluate(point)` mirrors the two equations. `operand_bindings()` returns `{pump_fit id: {"capacity": input key, "demand_flow": channel key}}`.
- `studies/study_route.py` — stock teax lifecycle only, with no adapter and no glue:
  - `execute_baseline(out, *, package_dir, manifest_path)` writes `package_identity.json` (`build_sealed`), `baseline_result.json` and `_work/station-baseline-v1.db`;
  - `run_grid(out, *, package_dir, points)` returns the store path.
- `studies/baseline/{package_identity,baseline_result}.json` — the route's output, committed so the default lane can run `preflight gates`.
- `census.json` — the census gate 4 checks.
- `gates/check_pins.py` (asserts sysml-codegen and agentic-mbse import) and `gates/check_census.py` (asserts `census.json` equals `census.by_entry_type` over the committed package).
- `pyproject.toml` — only the `[tool.sysml-codegen.integrate]` table: both gates, empty environment, `backup-prefix = "station-integration-backup-"`.

**How tests use it.** The fixture is its own project. Every path in its manifest, axis declaration and `pyproject.toml` is relative to `tests/fixtures/study_station/`: for example `pkg/station_study`, and the oracle's `sys_path` `studies`.

- Read-only default-lane tests use it in place, with `SYSML_CODEGEN_PROJECT_ROOT` set to the fixture directory. Git still answers `preflight clean`, because the directory sits inside this repository's work tree.
- Tests that mutate it copy it into a fresh `tmp_path` git repository and commit, so that copy is the project root. Integrate tests always do this. `tests/study/data/synthetic_pkg/` moves unchanged for the indicators-only tests. SC4 copies only the package, models, snapshot, route and oracle into its target, plus the manifest under cut 3.

## Appendix F — Tests by lane

The classification of fusion-tea's 51 files is by file and function, at `b06585709`.

**Moves to `tests/study/` (default lane unless marked), re-pointed at the neutral fixture or `synthetic_pkg`:**

- whole files: `test_common`, `test_output_contract` (all but `test_fingerprint_read_set_is_the_three_legs`), `test_preflight_gates`, `test_preflight_negatives`, `test_identity`, `test_mechanical_failures`, `test_multipipeline`, `test_subset_flag`, `test_provenance`, `test_valid_empty`, `test_read_coverage`, `test_read_set_coverage`, `test_absolute_tolerances`, `test_integrate_preconditions` (its two simkit-probe tests go to the execution lane), `test_integrate_restore` (license);
- `test_integrate_guide_contract`, rewritten for the shipped guide. It checks the slugs, `REQUIRED_ENV`, exit codes, flags, gates and scope phrases. It also checks the declaration keys, `TEAX_SIMKIT_PATH` and `SYSML_CODEGEN_PROJECT_ROOT`. The fusion-only checks for the sealed wheels and ADR-0009 stay in fusion-tea;
- functions merged into `test_predicate_operands.py`: `test_breeding_predicate` (3), `test_indicator_operands` (4), `test_verify_operands` (all but the IFE one);
- functions merged elsewhere:
  - `test_integrate_refusals`' two store-resolution tests;
  - `test_verify`'s two pure disjunction tests;
  - `test_known_answers`' `test_every_constraint_carries_all_three_identities`;
  - `test_numeric_evidence`' `test_verification_refuses_partial_numeric_coverage`;
  - the five agnostic functions of `test_generic`, which go into `test_generic_text.py`;
  - `test_record_template`'s schema check, which goes into `test_tool_identity.py`.
- **Execution lane** (`tests/execution/test_study_*.py`):
  - `test_verify`'s neutral-plus-teax set: schema, parity, both stratification tests, both seed tests, no absolute paths, bindings digest, planted deviation, missing `operand_bindings`, unresolvable binding, empty result, stores never written;
  - `test_stock_route`'s two sealed-identity tests.
- Stay in fusion-tea: the 24 STAY files, plus `test_warnings` (needs ties and suffix siblings the neutral fixture lacks) and `test_integration_workspace` (fusion's workspace helper). They keep testing the moved code through the wrappers.

**New tests.**

- Default lane:
  - `test_roots.py` — variable, git, refusal with exit 2, any subdirectory, `TOOL_HOME`;
  - `test_tool_identity.py` (SC7) — the prefix and the digest recompute for indicators, preflight `gates` and `clean`, and a gate-0 integrate return; the pre-move documents, which validate and keep their old prefix; the schema sha pins;
  - `test_generic_text.py` (SC5a). It scans the five bundle files, the policy template, and every `sysml_codegen/study/*.py`. The closed lists are committed as literals with their provenance: the nine `exploration/` directory names, and the 17 package names and 20 key prefixes from `CONSUMER_ATTRIBUTES.md`. The spec's path, number, pointer, machine-path and adapter patterns complete them. The record template's history-note paragraph is the one exemption;
  - `test_compat_surface.py` (SC6);
  - `test_declarations.py`;
  - `test_census.py`;
  - `test_integrate_declared.py` (SC8). It uses a stub `simkit` inside a `tmp_path` git repository plus a dummy license value. It covers: 1a undeclared → `unasked`; 1a declared pass and refuse; 1b unasked, refused, and not a checkout; the declared environment sweep; malformed declaration → `input-invalid`; the toolchain key order; no teax → `env-missing` naming teax;
  - `test_verify_without_teax.py` (B9: exit 1, names teax, no `--out` file);
  - `test_study_cli.py` — dispatch, `--help` passthrough, exit codes;
  - `tests/unit/test_install_commands.py` (SC1, SC2).
- License lane (`requires_license`): `test_study_fixture_current.py` (a snapshot recapture equals the committed snapshot, and live generation equals the committed package); `test_integrate_gates_licensed.py` (gate 2 refused after a committed edit; gate 4 snapshot drift, census stale, census unasked; gate 5 undeclared and refused; gate 6 manifest stale).
- Execution lane: the route reproduces `studies/baseline/`; `verify` completes (SC3); integrate gate 7 read-coverage and gate 8 verification refusals; `CANDIDATE` (also needs the license; cut 2 replaces it with a named-gate `BLOCKER`).

The pre-move documents are committed byte for byte at `tests/study/data/premove/`, with a `PROVENANCE.md` naming fusion-tea `b06585709` and the record path. There are four: `indicators.json`, `preflight_results.json`, `verification_summary.json` and `integration-return.json`, which carries no schema and gets a prefix check only.

## Appendix G — SC12 parity script

**Where.** `.project/active/study-layer-to-codegen/evidence/parity/` holds `parity.py`, `README.md`, `report.md` and `cases/<case>/{orig,orig2,moved}/`. Run it with the scratch venv's Python.

**Inputs.**

- The neutral fixture, and the staged originals `.orchestrate-logs/src/fusion-tea@b06585709/scripts/{study/,integrate.py}`.
- Wheels of this branch and of the agentic-mbse branch, installed non-editable into `$S/venv` along with `jsonschema`.
- teax installed editable from the checkout. `SYSIDE_LICENSE_KEY` and the teax checkout path `$TEAX` come from the environment.

**Layout.** A single git repository, `$S/project`, holds the fixture's contents at its root, so the fixture's relative paths resolve unchanged. It also holds:

- the originals at `scripts/study/` and `scripts/integrate.py`, byte-identical;
- stand-in gate files at fusion-tea's two paths. `tests/models/test_model_family_spines.py` contains `_contract` and `_by_entry_type` verbatim (`b06585709:174-182`) plus one passing census test;
- `pyproject.toml`, holding Appendix D's fusion-tea declaration.

Both tools run in this same directory, so absolute paths agree. `out/` is gitignored, and each run's output is moved aside before the next run.

**Runs per case.**

- **orig** — `python scripts/<tool>.py …`, with the five fusion-tea variables set: the four wheel variables as dummies and `STOP_PARSER_TEAX_ROOT=$TEAX`. A `uv` shim first on `PATH` runs `uv run X …` as `X …` from the venv, which is the harness side of B3.
- **orig2** — orig repeated, to measure noise.
- **moved** — `python -m sysml_codegen.study.<tool> …`, with the same environment plus `TEAX_SIMKIT_PATH=$TEAX/packages/teax-simkit`.

Arguments are identical relative paths.

**Comparison.**

1. Exit codes must be equal.
2. Fields that differ between orig and orig2 are noise. They are reported and masked; expect the read-coverage token, temporary paths and the backup path.
3. Closed-list fields are mapped where the new value is determined:
   - `tool.path` and `command[0]` (B2);
   - the gate and blocker `producer` strings, through a fixed table from each script path or the census helper to its package form (B2, B11).

   They are masked where the value is content-derived: `tool.source_digest` (B2); read-coverage `declarations`, `dependency_digest`, and `reads[].category` under the tool home, plus the digest inside gate 7's detail (B8).
4. Everything else must be equal. Text outputs (`--print-fingerprint`, stdout documents) must be byte-equal.
5. Library parity runs in-process, with `SYSML_CODEGEN_PROJECT_ROOT=$S/project`. It compares the original and moved results of `indicator_input_fingerprint`, `build_sealed`, `repo_relative_posix` and `rederived_census`.

**Cases.**

- `indicators`: complete; pin mismatch; `--print-fingerprint`.
- `preflight gates`: complete; stale manifest.
- `preflight clean`: clean; dirty.
- `verify` (teax): complete on a grid store; oracle mutated → exit 1, no document.
- `integrate`:
  - gate 0: input-missing (stdout document), input-invalid (out-dir inside the package), env-missing (a variable unset), package-not-integrated (dirty);
  - 1a refused; 1b unasked and refused;
  - 2 refused (committed byte edit);
  - 4 census unasked and census stale;
  - 5 refused;
  - 6 manifest stale;
  - 8 verification refused;
  - 9 unasked and lineage mismatch;
  - `CANDIDATE`, unless cut 2 applies.

**Pass.** `report.md` lists every case as `EQUAL` or `EQUAL after closed-list fields [ids]`, with no `DIFFERENT` row.

## Appendix H — Orchestrator-run evidence

`$EV` is `.project/active/study-layer-to-codegen/evidence/`.

**H1. SC1 install transcript.**

1. Run `uv build` here and in the agentic-mbse branch.
2. `uv venv /tmp/study-install-<stamp>/venv`, then `uv pip install` both wheels. syside comes from its index, as agentic-mbse requires.
3. Check that neither checkout is on `sys.path`: `python -c 'import sysml_codegen, agentic_mbse; print(sysml_codegen.__file__, agentic_mbse.__file__)'`.
4. Run `sysml-codegen install-commands target --list`, then `sysml-codegen install-commands target < /dev/null`.
5. Record `find target -type f -o -type l | sort` and `cat target/.sysml-codegen/install.json`.
6. Edit `runbook.md` and re-run: expect "skipped". Re-run with `--force` and check the policy is replaced.
7. Run `agentic-mbse init target < /dev/null` and re-list both manifests.

Save it as `$EV/install-transcript.md`.

**H2. SC4 dry run** in `/tmp/study-dry-run-<stamp>/`, following the H1 venv recipe plus teax.

1. **Target.** `git init target`, then `sysml-codegen install-commands target --assistant claude < /dev/null`. Copy from the fixture:
   - `models/` and `station.snapshot.json`;
   - `pkg/station_study/` → `packages/station_study/`;
   - `studies/study_route.py` and `studies/oracle_entry.py` → `studies/station/`;
   - under cut 3 also `studies/manifest.json`.

   Commit.
2. **Agent.** `claude -p` in `target/`, with the venv on `PATH`, `TEAX_SIMKIT_PATH` set, and Item 2's isolation from user-level configuration. Capture stream-json.
3. **Brief.**
   - Intake, as the owner's words: "Study how the pump-fit constraint responds to basin area and installed pump capacity, and whether the energy price matters to it. The package is packages/station_study."
   - Operator answers given in advance:
     - the studies directory is `studies/station/` (write it into the policy's § Locations);
     - the route is `execute_baseline` and `run_grid` in `studies/station/study_route.py`;
     - the oracle is `oracle_entry` there;
     - any `no_constraint_response` axis is ruled "proceed as sensitivity-only";
     - a coordinator review check suffices;
     - commit the record.
   - For anything else, write it under § 17 and stop.
   - The agent writes the annex, manifest (unless cut 3) and axis declaration from the installed text.
4. **Checks.**
   - `python $EV/dry-run/check_record.py <record> --log studies/station/DISCOVERY_LOG.md` passes.
   - Every tool document carries `tool.path` under `sysml_codegen/study/`.
   - The read-file list holds only target files, the installed skill and the venv.
5. **Administrator** (cut 4 is last). A fresh `claude -p` session in the record directory reads only that directory and writes `synthesis.md`.

Evidence goes to `$EV/dry-run/`. It names the pieces the fixture supplied ready-made: the package, models, snapshot, route and oracle, plus the manifest under cut 3.

**H3. SC9 runbook and rehearsal.** The runbook draft is `$EV/fusion-tea-runbook.md`, in Item 2's shape: Before you start, then numbered steps, each with "Observed in the rehearsal". The orchestrator moves it to agentic-mbse before close (D10).

| Step | Runbook action | Rehearsal command on `$FTC` (disposable worktree of `b06585709`) | Expected observation |
|---|---|---|---|
| 1 Drift | `git diff b06585709 origin/main -- .claude/skills/run-study modeling_project/STUDY_POLICY.md scripts/study scripts/integrate.py docs/integration_seam_operator_guide.md` must print nothing, or stop | same, on `$FT` | empty |
| 2 agentic-mbse pin | `uv run --no-sync python -c "from agentic_mbse.cli.installation import INSTALLER_API_VERSION as v; print(v)"` prints `installer/v1`, or move the pin first (Item 2's step 1 procedure) | after `uv pip install --python $FTC/.venv/bin/python --no-deps $AMBSE_WHEEL $CODEGEN_WHEEL` | `installer/v1` |
| 3 No loss | each Item 3 ledger row's anchor greps in its destination file | `git -C $FTC grep -n '<anchor>' -- <file>` per row, on the fusion-tea branch tip | every row found |
| 4 Pin move | sysml-codegen `rev` → merged SHA; hand-edit `uv.lock` (`8a758e9…` → the SHA); `uv sync --frozen --extra e2e`; restore removed packages; `uv lock --check`; update `C_PROD` in `tests/test_dependency_provenance.py`. This item's `pyproject.toml` changes do not touch fusion-tea's lock: the dependencies are unchanged, `jsonschema` is in the `dev` extra fusion-tea does not request, there is no new console script, and assets ship inside the package | not rehearsed (needs the merged SHA) | — |
| 5 Switch | the wrappers (DD14) for `scripts/study/{common,identity,indicators,manifest,preflight,read_coverage,verify}.py` and `scripts/integrate.py`; `git rm -r scripts/study/schemas`; the spine test's `_by_entry_type` → `from sysml_codegen.study.census import by_entry_type as _by_entry_type`; each fusion-tea test edit that run C attributes to the move | applied on `$FTC` | `python -c "import scripts.study.manifest as m, sysml_codegen.study.manifest as n; print(m is n)"` prints `True` |
| 6 Declare | add Appendix D's table to `pyproject.toml`; add `TEAX_SIMKIT_PATH` to `.venv/integration.env` | applied | `uv lock --check` unchanged by the `[tool]` table |
| 7 Re-install | `git rm -r .claude/skills/run-study .agents/skills/run-study`; drop `.gitignore`'s `!.claude/skills/run-study/`; `uv run --no-sync sysml-codegen install-commands . < /dev/null` | same on `$FTC` | five files created under `.agents/skills/run-study/`; the `.claude/skills/run-study` link; "Preserved modeling_project/STUDY_POLICY.md"; `.sysml-codegen/install.json` |
| 8a Suite (cut 1) | `uv run --no-sync pytest tests/study tests/models/test_model_family_spines.py -q --junitxml=…` | runs A, B and C (DD15); `$EV/rehearsal/junit-diff.py A.xml B.xml C.xml` | C−B lists only failures with a step-5 edit; none is a defect |
| 8b Re-verify | moved `verify` over one record whose identity still recomputes on the current package, with the record's seed and sample size; compare with that record's summary, masking `tool` and `command[0]`; the record directory's `git status` is empty | same, on the staged record `20260916-primary-loop-sizing` if its identity recomputes, otherwise the newest record that does | same sampled cases, verdicts and worst deviation |
| 9 Consequence | state that the generator moves about 142 commits, that gate 2 may refuse fusion-tea packages and gate 4 snapshots may drift until each is regenerated in its modeling item, and that this is the pin move's consequence, not the switch's | — | — |

Rehearsal evidence goes to `$EV/rehearsal/`. Each step is marked rehearsed, not rehearsable (with the reason), or not run.

## Appendix I — Porting the text, the read-through, and the ledger

**Method.** Each file starts from its `b06585709` bytes, and edits are made by class:

- `envelope` — frontmatter: list-form `allowed-tools`, `metadata.kind: workflow`;
- `path` — fusion-tea paths become the studies directory or a sibling file;
- `tool` — `scripts/study/x.py` becomes `sysml-codegen study x`;
- `objective` — LCOE becomes "objective";
- `route` — named teax entry points become "the execution route the study policy names, supplied by the package annex";
- `adapter` — adapter, glue and era-pin practice is removed, but the disclosure stays with "none" as the general case and record fields keep their names;
- `pointer` — `(Item n)`, record ids, `L-`/`T-` ids, requirement and decision numbers, "gap G1";
- `goal-layer` — `work/orchestration/GOAL_RUNBOOK.md` becomes "the installed goal runbook, § Review scope and evidence reuse; a target without the goal layer applies the study policy's § Process sizing";
- `project` — instructions that only make sense for one project move to fusion-tea.

General rules and their wording stay.

**Per file, the main changes.**

- **`SKILL.md`.**
  - Triggers: "LCOE" → "the objective", and "exploration/.../studies/" → "a studies directory".
  - Record path → `<studies-dir>/<study-id>/`, with the policy's § Locations naming `<studies-dir>`.
  - "Then go here" names the four sibling files, `modeling_project/STUDY_POLICY.md` and the `sysml-codegen study` tools.
  - The goal-layer pointer at `:35` is rewritten.
- **`runbook.md`.**
  - The header's record and annex paths, and every **Calls:** line.
  - Steps 5, 8, 9 and 13 lose their route, adapter and era content: the route is the policy's, and the glue disclosure defaults to "none".
  - Step 7's provenance citation moves; the rule stays.
  - The goal-layer pointers at steps 4, 12 and 14.
  - Administer step 2 says "objective result".
  - The `DISCOVERY_LOG.md` path.
  - New, short: "The tools" (the CLI forms, `TEAX_SIMKIT_PATH`, the project root), and "What a package annex supplies" (the supported API and protocols, Appendix C).
  - Steps 14 and 15 each gain a **Check:** line (DD12). Each is a test the executor runs; nothing is left to judgment:
    - § 15's `<study-id>#<n>` ids equal, as a set, the Record-column ids the discovery log carries for this study id;
    - `grep -c '<' record.md` prints 0;
    - every `manifest.content_used.fingerprint_names` entry is a key under `fingerprints`;
    - every `arms[].store_id` is in `stores[]`;
    - every `arms[].artifacts[]` entry has a `sha256`.
- **`record-template.md`.**
  - The copy path; § 3 LCOE; § 10's route values become `<the route the study policy names>`.
  - The `(Item 3)` markers become "(fixed by the tool's schema)"; "gap G1, run-study-cold-pickup" goes.
  - `tools[].path` becomes `sysml_codegen/study/<tool>.py`, with the history note: "**History: tool paths in older records.** Records written before the study tools shipped in sysml-codegen name each tool `scripts/study/<tool>.py`, and the integration seam `scripts/integrate.py`, in `tools[].path` and `source_digest.files[].path`. Those records stay valid as written: read the prefix as the tool's era, never as a file to open. Digests from the two eras never compare, because the path is part of the digested text."
  - `teax.era_pin` keeps its name: "null, or the teax revision the route needs beyond the environment's".
- **`integration-guide.md`.**
  - Generic invocation and environment blocks, with the declaration table and `TEAX_SIMKIT_PATH`.
  - The repo-gate section describes declared gates and the undeclared blocker.
  - Removed and moved to fusion-tea's supplement: the `~/1cfe/agentic-mbse/.env` invocation, the stellarator example arguments, the second-checkout procedure, the sealed-wheel paths and `WHEEL_HASHES`, the `mfe_census.json` path, ADR-0009 and the `tests/study` pointer.
  - Exit codes, slugs and gates are unchanged. The exit-2 row adds one case: the invocation could not start, as with an argparse usage error or no project root (DD2), in which case no document is written.
- **`annex-template.md`** (new). Sections `## § Declared ties`, `## § Baseline pin`, `## § Oracle`, `## § Validity masks`, each with what goes there, plus a "Package-owned pieces" list: manifest path, axis declaration path, route module and callable, oracle module, callable and `sys_path`.
- **`STUDY_POLICY.md.template`.** Evidence B's table, applied as DD16:
  - an unratified-template header;
  - §§ 1–5, 9 and 11 general, with examples stripped of identifiers (`mfe_viability.sysml`, `mfe_plasma_scaling.sysml:24,66`, WI-019, WI-022, WI-024, MR-4, the research path);
  - § 4's "(§7)" corrected to the tripwire section;
  - § 5's heading loses "demo"; "criterion 5" and "no-fallbacks rule" are restated as the rule itself;
  - § 9 names the installed indicators tool;
  - new slots: § Locations, § Execution routes, § Hypotheses, § Tripwire record (empty);
  - no § 10.

**Read-through record (SC5(b)).** `$EV/read-through.md` has one table per file:

| Id | fusion-tea line(s) | Text (quoted, ≤ 12 words) | Class | Verdict | New text, or destination |
|---|---|---|---|---|---|

- Ids are `SK-n` (skill), `RB-n` (runbook), `RT-n` (record template), `IG-n` (guide), `SP-n` (policy).
- The verdict is one of: `kept: general`, `kept: labelled example`, `generalized`, `moved`.
- A `moved` row names a fusion-tea file and section, marked "exists at `b06585709:<line>`" or "added on `<fusion-tea branch>`".
- Every "LCOE" instance gets a row.

**Ledger rows (SC10).** The orchestrator appends a "## Item 3 — study-layer-to-codegen" section. Its rows group the `moved` verdicts by destination, in Item 2's columns:

| Text | Was in (fusion-tea) | New fusion-tea home | Evidence |
|---|---|---|---|

The Evidence column holds the read-through ids, the fusion-tea branch diff, and the anchor text runbook step 3 greps for.

The expected destinations:

- fusion-tea `modeling_project/STUDY_POLICY.md`, which stays and is preserved by the installer. It gains:
  - § Locations (`exploration/<pkg>/studies/`);
  - § 6 additions: the two-route rule, the adapter route with its loader exception, glue and era pin;
  - step 7's provenance line.

  Its existing text is the home for every `SP-` moved row.
- fusion-tea annexes: the optional `§ Loader exception and glue` and `§ Era pin` sections stay where they exist.
- fusion-tea `docs/integration_seam_operator_guide.md`, rewritten as fusion-tea's integration supplement: the environment file, sealed wheels, second checkout, the stellarator example, the census path and ADR-0009.
- fusion-tea `CLAUDE.md`: one line saying run-study installs from sysml-codegen and where fusion-tea's study specifics live.

The implementing stage drafts these texts in `$EV/fusion-tea/`, and the orchestrator applies them on a fusion-tea branch before sysml-codegen merges (spec decision 1).

## Appendix J — Estimate (execute hours, rough ±30%)

| Criterion | Spec | Design | Why it changed |
|---|---|---|---|
| SC1 | 2 | 2 | — |
| SC2 | 2.5 | 3.5 | the agentic-mbse change, its tests and suite, and the API pin |
| SC3 | 12 | 14.5 | the test move is 15 whole files and 12 partial ones, not about 12 files; the fixture costs the same (new model instead of extended `synthetic_pkg`; the integrate pieces are shared) |
| SC4 | 2 | 2 | — |
| SC5 | 5 | 5 | the annex template and guide port fit inside |
| SC6 | 1 | 1 | — |
| SC7 | 1 | 1 | — |
| SC8 | 4 | 4 | — |
| SC9 | 3 | 3.5 | the A/B/C differential |
| SC10 | 1.5 | 1.5 | — |
| SC11 | 0.5 | 1 | two repositories' suites |
| SC12 | 2 | 3 | 25 cases, noise runs, library parity |
| Docs | 1 | 1 | — |
| **Total** | **37.5** | **43** | about 38.5 with all four cuts |

With design (4h) and plan (1h), the item is about 48h, roughly 6 days against the epic's 2. This is stated for the orchestrator's report to the owner (D11).

---

Next Step: `/_my_design_review` in a fresh session, then `/_my_plan`.
