# Spec: Move the study layer to sysml-codegen (WRAP-SPLIT Item 3)

**Status:** Approved for design by the orchestrator, 2026-10-12, after one review round (Revise, applied)
**Implementation:** In progress. Phase A and Phases 1–4 of the plan are done (2026-10-12): SC12's parity passes on all 28 cases under the orchestrator's ratified rules, and the fusion-tea code drafts are written and smoke-tested. Phase 5 is in progress; see `plan.md` Implementation Notes.
**Owner:** Reid W
**Created:** 2026-10-12
**Complexity:** HIGH
**Branch:** `study-layer-to-codegen` (base `aa35f06`)
**Epic:** WRAP-SPLIT, Item 3 (the epic lives in agentic-mbse, `.project/backlog/epic_wrap-split.md` at `ac5fb1a`)

---

## Problem

The study capability exists only inside fusion-tea, and nothing installs it. A new modeling project that uses sysml-codegen and teax cannot run a study without copying fusion-tea files by hand. The capability is:

- the `run-study` skill: `SKILL.md`, `runbook.md` and `record-template.md`;
- the rulebook `modeling_project/STUDY_POLICY.md`;
- the tools under `scripts/study/`, with seven JSON schemas;
- `scripts/integrate.py`, with its operator guide `docs/integration_seam_operator_guide.md`.

[OWNER] (epic header, 2026-10-06): the study layer ships from sysml-codegen. sysml-codegen already depends on agentic-mbse, owns the generated-package contracts the tools read, and already has an `install-commands` subcommand.

[AGENT] (orchestrator Align reading, 2026-10-12; the owner did not contest it): the bar is a working capability in a fresh target, not copied files. A target that uses sysml-codegen and teax runs `sysml-codegen install-commands` and can then run a study with nothing borrowed from fusion-tea. The owner's own words are "ported and generalized … installed like everything else" (research `:18`).

Five things make this a port rather than a copy:

- **The tools find the project from their own file location.** `manifest.repo_root()` is `Path(__file__).parents[2]` (fusion-tea `scripts/study/manifest.py:57`). Installed from a wheel, that is a directory inside site-packages, so every repo-relative path and every tool-source digest breaks. Evidence A has the detail.
- **fusion-tea uses the tools as a library.** About 30 package scripts import `scripts.study.{common, manifest, identity, indicators, verify}`, and six `build.py` files import `scripts.integrate.rederived_census`. The source is `CONSUMER_SURFACE.md`, which the orchestrator generated at fusion-tea `b06585709`.
- **Committed study records name the old tool paths.** The record template stores `tools[].path` as `scripts/study/<tool>.py` (`record-template.md:369`). The orchestrator counted 1,261 to 1,338 committed record files that mention these paths, depending on the pattern. Committed records must not change (epic Out of Scope).
- **`integrate.py` runs fusion-tea's own tests as gates.** Gate 1a runs `tests/test_dependency_provenance.py` and gate 5 runs `tests/models/test_model_family_spines.py`. `rederived_census` imports `_by_entry_type` from that second test module (`integrate.py:1098`).
- **`install-commands` cannot deliver this today.** It copies one Claude command, has no ownership rules, and does not work from a wheel. `get_commands_dir()` looks for `claude/commands/` at the checkout root (`src/sysml_codegen/cli/__init__.py:59`), but the wheel packages only `src/sysml_codegen` (`pyproject.toml:41-42`).

fusion-tea cannot adopt the moved layer inside this item. Its sysml-codegen pin is `8a758e9` (fusion-tea `pyproject.toml:37`), 142 commits behind this branch's base. Moving the pin also changes the code generator its packages are built with. So this item delivers the sysml-codegen side, and fusion-tea adopts after merge by a runbook (orchestrator decision 1, Known Requirements § Delivery).

## Success Criteria

Each criterion is tagged. **Contract** means a product outcome that ships. **Evidence** means proof gathered for this item. Effort and the cut order are in § Estimate and cut order.

- [x] **SC1 · contract · Fresh install from wheels.** The scratch target is set up like this:
  - sysml-codegen is installed from a wheel built from this branch;
  - agentic-mbse is installed from a wheel built at the revision sysml-codegen's dependency names. agentic-mbse is on no package index, so it comes from a local build or a git-revision install;
  - neither source checkout is on the import path.

  `sysml-codegen install-commands` then installs `run-study` (skill, runbook, record template) for Claude Code and Codex, the study-policy template, and the existing `teax-completion` helper. The listing option names all of them. *Checked by* an install transcript in item evidence and a suite test of the install logic.
- [x] **SC2 · contract · Ownership holds on re-install.** A second `install-commands` run:
  - refreshes unmodified skill files;
  - keeps a locally edited skill file (preserved without asking when run noninteractively; prompted for when interactive);
  - leaves an existing `STUDY_POLICY.md` untouched unless the force option is given.

  Running `agentic-mbse init` afterwards leaves the `run-study` install intact, and the reverse order holds too. *Checked by* noninteractive suite tests on scratch targets.
- [x] **SC3 · contract · The tools run from the installed package against the neutral fixture.** Each tool **completes** on the fixture when its runtime is present:
  - `indicators` exits 0, and its report validates against `indicators.v1`.
  - `preflight gates` exits 0 with all six checks passing, and its results validate against `preflight_results.v1`. `preflight clean` exits 0 on a clean tree.
  - `verify` (needs teax) exits 0 with `verdicts_rederived: true`, and its summary validates against `verification_summary.v1`.
  - `integrate` (needs teax and the syside license) returns `CANDIDATE` with exit 0. Cut 2 replaces this with a documented `BLOCKER` at a named gate on each refusal path the fixture reaches.

  Each tool also **fails closed** on at least one negative case. Each case comes from the fail-closed conditions the tool's module docstring documents and the runbook's "Fails closed when" lines. For `integrate`, the cases are at least the gate-0 preconditions blocker and the undeclared-gate blocker (SC8). Without teax, `verify` exits non-zero, names teax in its message, and writes no output document. `integrate` returns its usual `BLOCKER` naming teax and writes no producer output, because it writes a return on every exit path by contract (amended 2026-10-12 per design premise conflict 4, accepted by the orchestrator). *Checked by* tests in this repo's three lanes (default, teax execution, license-gated). Item evidence records one run with both teax and the license present. Source: [INFERRED] widening of epic Item 3 SC2, which says "complete **or** fail closed as documented". A tool that only refuses proves nothing about a working capability, which is the bar. The widening reverses the epic's trade of fixture breadth for installer work (epic `:182`). Its cost is in the estimate, and cut 2 is its release valve.
- [x] **SC4 · evidence · A fresh target runs a study from installed files only.** The run goes in four parts:
  - **Setup.** The scratch target holds no fusion-tea file. An agent follows only the installed skill, runbook, record template and policy template, and writes the fixture's annex, manifest and axis declaration from that text alone (cut 3: the fixture supplies the manifest).
  - **The study.** The agent runs one study through runbook steps 1–15 to a committed record.
  - **The record checks.** The record must pass the step 14 condition (every findings row joins a discovery-log row, and the reverse) and the step 15 conditions: no unreplaced placeholder, every fingerprint name resolves, every store id resolves, every artifact has a digest. Whatever enforces them in a fresh target checks them (OQ8). If no check ships, a script in item evidence does, and the evidence names it.
  - **The cold read.** A second agent in a fresh session reads only the record directory and writes `synthesis.md` (cut 4).

  *Checked by* the dry-run record in item evidence. The evidence names every package-owned piece the fixture supplied ready-made, such as the oracle or the route module. Source: [INFERRED]. This is larger than its precedent: Item 2's dry run stopped after the first trail entry (`### T-001 start`, Item 2 design Appendix D3 step 4). This one must reach a committed record, because the tools run only in steps 2–15. A dry run that stopped at intake would exercise none of them.
- [x] **SC5 · contract · The shipped text and tools are generic.** Two checks.
  - **(a) Identifier grep.** A suite test covers the installed skill, runbook, record template, policy template, `integrate`'s operator guide and every tool module. It finds no identifier from these classes, including inside labelled examples:
    - **fusion-tea paths:** `exploration/`, `.project/`, `tests/models`, `docs/integration_seam`. Also `scripts/study` and `scripts/integrate`, except in the one labelled history note in the record template that tells readers of old records the pre-move prefix (D7).
    - **fusion-tea package names and key prefixes, as a closed list committed in the test:**
      - the nine `exploration/` package directories in `CONSUMER_SURFACE.md`: `aries_integrated`, `component_alternatives`, `costed_loop_brayton`, `exchanger_architecture`, `ife_e2e`, `magnet_materials`, `stellarator_e2e`, `stellarator_materials`, `whole_plant_conversion`;
      - every generated package name and key prefix those packages' contracts and manifests carry at `b06585709`. Known now: `stellarator_tea`, `ife_tea`, `stellarator_09__stellaris__` and `hif_plant_pkg__hif_plant__`. The implementing stage gets the rest from the orchestrator, because the staged sources do not hold every contract.
    - **requirement, decision and work-item numbers:** `MR-`, `PR-`, `WI-`, `ADR-` or `SC-` followed by a digit, and `R-` followed by a capital letter and a digit. `integrate.py` carries `ADR-009` `:14`, `R-B1` `:186`, `R-E4` `:333`, `ADR-006` `:416` and `R-A3` `:430`.
    - **fusion-tea process pointers:** `(Item <n>)` markers (record template `:250-444`), study-record ids of the form `YYYYMMDD-slug` (such as `20260905-stored-energy-basis`, runbook `:123`), and goal lesson and task ids (`L-` or `T-` with three digits).
    - **machine paths, environment variables and adapters:** `/home/`, `~/1cfe`, `STOP_PARSER_`, `era_adapter`.

    The test does not check vocabulary. Fusion words stay legal in labelled examples ([NEED], owner's bar). The stricter rule, that identifiers are banned even inside examples, is [INHERITED: epic Item 3 SC4]. This extends fusion-tea's `tests/study/test_generic.py` to the instruction files.
  - **(b) Read-through record.** A per-line record covers the four ported instruction files (`SKILL.md`, `runbook.md`, `record-template.md`, the integration operator guide) and the policy template. Every fusion-specific line gets one verdict: kept (a general rule or a labelled example), generalized in place, or moved to fusion-tea with its destination. The record catches what a grep cannot see: pointers used as authority, and instructions that only make sense for one project, such as "barred in demo studies" and "criterion 5" (Evidence B). Its moved-to-fusion-tea rows are SC10's ledger input. The precedent is Item 4's per-file read-through record. *Checked by* the record in item evidence.
- [x] **SC6 · contract · fusion-tea's compatibility surface exists (D9).** The design enumerates every attribute fusion-tea's consumers use on the moved modules. It finds them by grepping attribute access (`common.X`, `manifest.X`, `identity.X`, `indicators.X`, `verify.X`, `integrate.X`) and `from … import` names across the files `CONSUMER_SURFACE.md` lists. The staged sources hold only the import lines, not the consumer bodies, so the orchestrator supplies that grep from fusion-tea `b06585709`. A test checks that each attribute exists and has the signature it has at `b06585709`. Behaviour means the same result for the same inputs when the project root resolves to the consumer's repo. The design defines behaviour for the root-dependent functions (`manifest.repo_root`, `manifest.repo_relative_posix`, `common.tool_source_digest`). Behaviour is checked by SC12 and, at adoption, by fusion-tea's suite (SC9).
- [x] **SC7 · contract · Tool identity is mechanical, and old records stay valid (D7).**
  - **The rule.** The discriminating fields are `tool.path` and `source_digest.files[].path`. A pre-move value starts with `scripts/study/` or is `scripts/integrate.py`. A post-move value starts with the package prefix `sysml_codegen/<pkg>/`, relative to the installed distribution's import root. `source_digest.digest` is the revision.
  - **What stays fixed.** The seven schema files are byte-identical to fusion-tea `b06585709`: the diff is empty. Every `schema_version` string and the `indicator-input-fingerprint/v1` recipe are unchanged. No shipped check reads a committed record's tool path or command as a live file.

  *Checked by* three things:
  - a test that runs each moved tool on the fixture, validates its output against the unchanged schema, and checks the post-move prefix;
  - a test that validates one real pre-move document against the unchanged schemas and checks its `scripts/study/` prefix. That document is committed as a fixture, byte-for-byte, with its fusion-tea provenance. The staged sources hold no committed record, so the orchestrator stages one record document (a `verification_summary.json` or `indicators.json`). Failing that, the test uses the pre-move `indicators` report that the repackaging check's baseline run produces from the staged tools at `b06585709`, labelled as such;
  - the empty schema diff.
- [x] **SC8 · contract · `integrate` judges any target, not fusion-tea (D8).** `integrate` names no target test file, no target environment variable and no target-only dependency (SC5 grep plus a test). A repo-scope gate the target did not declare blocks with the existing `unasked()` outcome (`integrate.py:246-255`): class `BLOCKER`, exit 1, mode `could_not_run`, condition `input-missing`. A `CANDIDATE` still means all ten gates passed (`integrate.py:670-681`). A fixture that declares gates equivalent to fusion-tea's two gets the same ten gates in the same order. Its return differs from today's only in the fields the closed list names (§ What the move may change). *Checked by* tests.
- [ ] **SC9 · evidence · fusion-tea has a rehearsed adoption runbook (D10).** The implementing stage drafts the runbook in this item folder, and the orchestrator moves it to agentic-mbse before close. It has these steps, in order:
  1. **Drift check.** Diff fusion-tea's study skill, policy, tools, `integrate.py` and operator guide against `b06585709`. Stop on any change until it reaches sysml-codegen or its fusion-tea home.
  2. **agentic-mbse pin check.** fusion-tea's agentic-mbse pin must satisfy what sysml-codegen's dependency requires. If the design reuses agentic-mbse's `Installer`, that means a revision with the native installer, so Item 1's and Item 2's pin moves land first.
  3. **No-loss check.** Before anything local is removed, every ledger destination is present in fusion-tea's tree.
  4. **Pin move.** List every change this item makes to sysml-codegen's `pyproject.toml`, and say for each whether fusion-tea's hand-edited `uv.lock` still holds. Console scripts and package data do not touch the lock's dependency metadata. A new runtime dependency or a changed agentic-mbse bound does. Record `uv lock --check`.
  5. **Switch.** fusion-tea's copies become thin wrappers or are removed. fusion-tea's spine test (`tests/models/test_model_family_spines.py`) switches to the shipped census helper, so that gates 4 and 5 keep one implementation.
  6. **Declare.** fusion-tea declares its two repo-scope gates, its environment variables and its recorded distributions for `integrate`.
  7. **Re-install.** Install for both assistants. Remove the local `run-study`, its `.gitignore` whitelist line and its `.agents/skills` link.
  8. **Verify.** Run the study suite, then re-verify one existing record (definition under Known Requirements § Delivery).
  9. **Consequence note.** State the regeneration-gate consequence of the pin move.

  The orchestrator rehearses on a disposable copy of fusion-tea, with this branch's wheel installed into the copy's environment. Steps 1, 2, 3, 5, 6, 7 and 8's re-verification are expected to be rehearsable; so is 8's suite run, which is cut 1. Step 4 needs the merged SHA and is marked not rehearsed. The evidence marks each step as rehearsed, not rehearsable (with the reason), or not run, so "could not" is distinguishable from "did not". This criterion replaces epic Item 3 criterion 3 for this item.
- [x] **SC10 · contract · No loss of information for fusion-tea.** Every fusion-specific line removed from the ported skill, runbook, record template, operator guide or policy has a row in the shared migration ledger with its fusion-tea destination. The rows come from SC5(b)'s moved-to-fusion-tea verdicts. Each destination exists on a fusion-tea branch before the sysml-codegen change merges. *Checked by* the ledger rows and that branch's diff.
- [ ] **SC11 · contract · Suites pass.** The sysml-codegen full suite (`uv run --env-file <file holding SYSIDE_LICENSE_KEY> pytest tests/`; the orchestrator's baseline used sysml-codegen's main-checkout `.env`) shows the baseline of 2206 passed and 9 skipped, plus the new tests. No failure appears other than the known one, `tests/conformance/test_self_binding_guidance_contract.py::test_zero_unmarked_self_named_examples_across_all_trees`, which is not this item's. `ruff` and `mypy` are clean on `src/`, under the recorded per-module override Known Requirements § Fixture and tests allows. If the design changes agentic-mbse, its full suite passes too.
- [x] **SC12 · evidence · The move is byte-faithful apart from the closed list.** fusion-tea's original tools (the staged `b06585709` copy, run in fusion-tea's layout) and the moved tools run on identical inputs. Their output documents are byte-equal except in the fields § What the move may change names, and their exit codes are equal. Coverage is every tool the fixture can drive: `indicators`, `preflight gates` and `clean`, `verify` (teax lane), and `integrate` on each refusal path the fixture reaches, plus `CANDIDATE` unless cut 2 applies. *Checked by* a parity script in item evidence. The originals are gitignored, so this is evidence, not a suite test. Source: [INFERRED], applying ADR-0007's lesson (below). Evidence A compared outputs for `indicators` only, and only about 12 of fusion-tea's 55 study tests move here.

## Estimate and cut order

**[AGENT] (orchestrator, 2026-10-12, D11).** The spec carries an estimate per criterion and a total. Overrunning the epic's 2 days is acceptable if it is stated: the owner accepted Item 2 at 2.4 days. The orchestrator reports the overrun to the owner at the end.

Execute estimate, in hours ([AGENT], spec author, rough ±30%):

| Criterion | Type | Hours | What the hours buy |
|---|---|---|---|
| SC1 | contract | 2 | skill data in the wheel; install from wheels; transcript |
| SC2 | contract | 2.5 | ownership manifest, both assistants, coexistence tests |
| SC3 | contract | 12 | package port, root split, entry points and teax message 3; fixture for `indicators`, `preflight` and `verify` 2; moved and new tests 3; typing under the override 1; `integrate` `CANDIDATE` fixture 3 (cut 2) |
| SC4 | evidence | 2 | executing agent 1.5, of which manifest authoring 0.5 (cut 3); administrator 0.5 (cut 4) |
| SC5 | contract | 5 | four instruction files, policy template and annex guidance 3; read-through record 1; grep test 1 |
| SC6 | contract | 1 | attribute list from the orchestrator's grep; signature test |
| SC7 | contract | 1 | prefix tests; pre-move document fixture; schema diff |
| SC8 | contract | 4 | declared gates, environment, teax discovery, census home, backup prefix, launch form |
| SC9 | evidence | 3 | runbook draft 1.5; rehearsal 1.5, of which the suite steps 0.5 (cut 1) |
| SC10 | contract | 1.5 | ledger rows and fusion-tea branch text |
| SC11 | contract | 0.5 | full-suite runs |
| SC12 | evidence | 2 | parity script and runs |
| Docs | — | 1 | `README.md` and the `CLAUDE.md` overview |

Total execute: about 37.5 hours. Design about 4 hours and plan about 1 hour bring the item to about 42.5 hours, roughly 5.3 days against the epic's 2. With all four cuts applied, execute drops to about 33 hours. The review's independent sizing was about 32 hours before the parity check was added.

**Cut order** [AGENT] (orchestrator, D11), first to last. A cut applies only if the plan's estimate demands it:

1. SC9's fusion-tea suite steps in the rehearsal. The install, wrapper and re-verify steps stay.
2. Requiring `integrate` to reach `CANDIDATE` on the neutral fixture. Its refusal paths and the gate-declaration tests stay.
3. SC4's agent writing the manifest. The fixture supplies it instead.
4. SC4's second (administrator) agent.

The administrator reading is cut last, unlike the review's order, which cut it first. That reading directly tests an owner-verbatim statement ("sufficient structure in the artifacts … so that another agent can effectively pick up the results"), and it is one short read-only run.

Never cut: SC1, SC2, SC5 with its read-through, SC6, SC7, SC8, SC10, SC11 and SC12.

## Known Requirements

### Ownership and the owner's bar

- **[NEED]** The `run-study` skill and the tools it calls (`scripts/study/*`, `integrate.py`) ship from sysml-codegen. Source: epic header, 2026-10-06.
- **[NEED]** No loss of information for fusion-tea. An instruction removed from the ported text because it is consumer-specific moves into fusion-tea's own files and is recorded in the shared migration ledger. fusion-tea holds it before the removal merges. Source: epic header and epic Success Criteria.
- **[NEED]** Shipped text reads as a general rule or practice. Fusion vocabulary is acceptable in examples. These must go: pointers into fusion-tea or sysml-codegen internals as authority, hard-coded machine paths, consumer requirement numbers such as MR-7, and instructions that only make sense for one project. Source: epic header.
- **[INFERRED]** From the owner's "keep the item count low": the move lands as this one item. Scope that does not fit the budget follows the cut order above. Anything cut is recorded as a deferral, not split into a new epic item.

### The capability's shape (preserved, not redesigned)

- **[NEED]** The capability factors as a lightweight skill, a runbook, a policy rulebook and tools. Agent judgment is not frozen into tools. Source: fusion-tea `.project/concepts/run-study-skill.md:142`.
- **[NEED]** Indicators are context, never gates. Only mechanical conditions stop a study. Source: run-study concept `:143`.
- **[NEED]** Intake is collaborative and flexible. [OWNER-VERBATIM] "the user should construct the guidelines of the study collaboratively. In my case, it was just 'study whatever you can find'. but more often, it may be a focus on a particular part of the system, a particular goal, or very specific parameters. The agent must be flexible." Source: run-study concept `:23`.
- **[NEED]** One skill serves the executing and administrator roles. [OWNER-VERBATIM] "I prefer having sufficient structure in the artifacts from the executing study agent (e.g. context, goals, plan) so that another agent can effectively pick up the results and do the synthesis. I think to start with though, we should be able to use the same skill." Source: run-study concept `:24`.
- **[NEED]** An axis that nothing pushes back on is surfaced to the user as a sign the model is underdeveloped. [OWNER-VERBATIM] "if the user asks to study something and nothing pushes back — a signal the model is underdeveloped". Source: run-study concept `:21`.
- **[INHERITED: epic Item 3 Out of Scope]** Study semantics do not change beyond the closed list in the next section. The moved tools keep:
  - their gates, fail-closed conditions and exit codes;
  - every document `schema_version`;
  - the `indicator-input-fingerprint/v1` recipe. It hashes package-relative paths (`manifest.py:128-146`), so keeping it keeps every committed manifest pin valid;
  - the sampling scheme and the tolerances.

  `integrate` keeps its ten gates in order, its two return classes, its exit codes 0, 1 and 2, its fifteen condition slugs, and its rule that a `CANDIDATE` means all ten gates passed.

### What the move may change (closed list)

**[INFERRED]** This list is closed. Everything not on it moves byte-faithfully in behaviour: the same inputs give the same output documents and exit codes, and SC12 checks that. The rule applies ADR-0007's lesson: "A boundary move is byte-faithful or it is a behavior change to be reviewed as one." That lesson came from a "behavior-preserving" relocation in this repo that introduced two undocumented deviations (`.project/adr/0007-agentic-mbse-owns-neutral-facts-codegen-owns-rendering.md:32-35`). Source edits are limited to:

- the import rewrite;
- the changes below;
- type annotations that mypy needs;
- comment and docstring edits that SC5 requires.

The deliberate behaviour changes:

- **B1 · Project root.** The design's mechanism finds the project root (OQ3) instead of `Path(__file__).parents[2]`. The same project gives the same paths.
- **B2 · Tool identity values.** `tool.path`, `source_digest.files[].path` and `source_digest.digest` follow D7. `verify`'s `command[0]`, `integrate`'s `tool.path` and `command[0]` (`SEAM_PATH`), and the gate `producer` strings that name script paths all name the installed tools instead.
- **B3 · Launch.** `integrate` starts `preflight`, `verify` and the generator through the installed package. It no longer uses `scripts/study/*.py` paths or a hard-coded `uv run` (`integrate.py:552, :1006, :1304, :1353`).
- **B4 · Gate 0's environment sweep.** `SYSIDE_LICENSE_KEY` stays on the tool's fixed list. The four `STOP_PARSER_*_WHEEL` variables and `STOP_PARSER_TEAX_ROOT` leave it (`integrate.py:128-135`). The target declares the variables its own gate producers need, and fusion-tea declares its five.
- **B5 · Repo-scope gates 1a and 5.** They run the producers the target declares. An undeclared gate blocks as D8 says.
- **B6 · The toolchain block.** `costingfe` is no longer a fixed key (`integrate.py:343`, emitted at `:696`). The block records the distributions the target declares, so fusion-tea's declaration keeps that record. The design settles the exact key mapping.
- **B7 · teax discovery.** Gate 1b's revision check (`integrate.py:316-321, :949-966`) and `read_coverage`'s teax roots (`read_coverage.py:95-101`) take teax from the general discovery mechanism (OQ6). Gate 1b never passes without comparing a revision. If discovery finds no checkout, gate 1b blocks; it does not pass.
- **B8 · `read_coverage`'s permitted sources.** They are stated by meaning (the tool's own sources, the route directory, the declared teax) instead of `Path(__file__).parents[1]` (`read_coverage.py:94`).
- **B9 · The teax-missing message.** A tool that needs teax exits non-zero with a message naming teax. `verify` writes no document; `integrate` writes only its usual `BLOCKER` return (design premise conflict 4). Today the failure is a bare `import simkit` traceback (`verify.py:484`).
- **B10 · The backup prefix.** The `fusion-tea-integration-backup-` prefix (`integrate.py:1506`) becomes a parameter.
- **B11 · The census helper.** Gate 4 and `rederived_census` use the shipped helper instead of fusion-tea's test module. The grouping stays the same (`test_model_family_spines.py:178-182`).
- **B12 · Declared gate claims.** [AGENT] (orchestrator, 2026-10-12, from design review M1) The text a return states about what repo gates 1a and 5 examined comes from the target's declaration, not from fusion-tea's fixed strings (`integrate.py:189-200`). A declared gate without that text is an invalid declaration and blocks at gate 0 with `input-invalid`; there is no default text, because a default would claim a check nobody declared. fusion-tea's declaration supplies today's strings byte for byte, so its returns stay identical (SC12).
- **B13 · Interpreter platform data.** [AGENT] (orchestrator, 2026-10-12, from Phase 2 and Phase 3 findings) `read_coverage` classifies two kinds of read as runtime reads, the same as reads under `sys.prefix`, not as undeclared dependencies: `/dev/urandom` and `/dev/random`, exactly those two paths; and files under the interpreter's own time-zone search path, `zoneinfo.TZPATH`. Under uv's standalone CPython 3.12.11, the neutral station's route opens `/dev/urandom` (first import of `random`) and `/usr/share/zoneinfo/UTC` (pandas asks dateutil for UTC at import), and gate 7 refused each in turn. Under fusion-tea's system Python 3.12.3, `sys.prefix` is `/usr`, so the zone read already counted as runtime there and the entropy device was never opened. The rule makes uv's interpreter behave as the system one already does: this is platform data a target cannot declare or pin. Following `zoneinfo.TZPATH`, not a hard-coded path, keeps the rule tied to the interpreter's own setting. Caveat: zone data can in principle affect a time-zone conversion; a route that depends on one declares it as an input. With this rule, the station returns `CANDIDATE` with all ten gates (Phase 3 scratch run). Rejected: running integrate only on a system-Python venv, because uv's default interpreter would make gate 7 refuse every general target. Also rejected: pre-importing in the route driver, because it works around the observer. fusion-tea's runs and SC12's parity (which runs on `/usr/bin/python3.12`) are unaffected.
  - *Consequence for read-coverage receipts (B1, B13)* [AGENT] (orchestrator, 2026-10-12, from Phase 3's finding): the moved observer imports `roots` (and through it `subprocess`) and `zoneinfo` before observation starts. A module imported before observation is never recorded, so a moved receipt omits the standard-library `.pyc` reads of those modules that the original receipt lists as `runtime-observed`. This is the only receipt difference these items cause. SC12 compares receipts with that set excluded, and only that set, measured in the parity environment and recorded in evidence. Rejected: lazy imports in `roots`, because they fall outside the closed list and the `zoneinfo` group has no import-free way to read `zoneinfo.TZPATH`.

### Installer

- **[HARD]** Installation works when sysml-codegen comes from a built wheel. fusion-tea installs sysml-codegen from a git revision (`pyproject.toml:37`), and uv builds a wheel from it. Today that wheel lacks `teax-completion.md`, because it packages only `src/sysml_codegen` and `get_commands_dir()` looks at the checkout root.
- **[INHERITED: epic Item 3 scope 1; agentic-mbse `CLAUDE.md` "Init File Ownership"; epic product-lens epic-F3]** `install-commands` gains the tool-owned and user-owned distinction. Skill files are managed assets. An unmodified one is updated. A locally edited one is preserved when run noninteractively and prompted for when interactive. The study-policy template is a project document: created once, preserved on re-install, and replaced only under the force option.
- **[INFERRED]** `run-study` installs for both Claude Code and Codex. fusion-tea installs it for both today: its tracked `.agents/skills/run-study` links to `../../.claude/skills/run-study`. agentic-mbse's installer installs every skill for both assistants.
- **[INFERRED]** The two installers coexist in one target. Neither removes, overwrites or claims the other's files, and re-running either one leaves the other's install intact.
- **[INFERRED]** The `teax-completion` helper keeps installing. It is the subcommand's only job today.
- **[AGENT] (orchestrator, 2026-10-12, decision 3)** The installer mechanism is the design's call: reuse agentic-mbse's `Installer` (`src/agentic_mbse/cli/installation.py:91`) or build a standalone sysml-codegen installer. A small agentic-mbse change is allowed if the design picks reuse.
- **[INFERRED]** If the design reuses agentic-mbse's `Installer`, sysml-codegen's declared agentic-mbse dependency must exclude every agentic-mbse revision that lacks that API. Today's bound, `agentic-mbse>=0.1.3,<0.2` (`pyproject.toml:24`), cannot do that alone. agentic-mbse reports 0.1.3 both at `main` and at fusion-tea's pin `adbef75`, which predates Item 1's native installer. The design states how the guarantee is made. **Amended 2026-10-12** [AGENT] (orchestrator, accepting design premise conflict 1): the guarantee is an exported `INSTALLER_API_VERSION` that `install-commands` checks, lazily, before it installs, not a version bound. Bumping agentic-mbse past 0.1.3 would make every committed v6 snapshot unloadable, because the snapshot loader rejects a mismatched `agentic_mbse_version` (`src/sysml_codegen/snapshot/envelope.py:459-473`, verified by the orchestrator).
- **[INHERITED: `.project/adr/0007-agentic-mbse-owns-neutral-facts-codegen-owns-rendering.md`]** The dependency stays one-way. sysml-codegen may import agentic-mbse, and agentic-mbse gains no import of sysml-codegen.

### Tools

- **[AGENT] (orchestrator, 2026-10-12, D6)** The tools ship as an importable package inside the `sysml-codegen` distribution, with console entry points. `integrate` moves the same way, with its provenance-test read and backup prefix parameterized (B5, B10). Reason: the tools read contracts that sysml-codegen's generator writes (`model_contract.json`, `package_contract.json`, pipelines, inputs). One distribution keeps the reader and the writer at the same version. This is the literal reading of the owner's "ships from sysml-codegen", so it needs no owner ruling, which closes product-lens spec-F2's concern. Accepted cost: the root split, the tool-identity change and the fusion-tea wrappers.
  - Rejected: a separate distribution. Its benefit, adopting without moving fusion-tea's generator pin, is temporary, because fusion-tea must move that pin to get generator fixes anyway. Meanwhile it opens a version skew between the contract writer and the contract reader.
  - Rejected: installing the tool files into each target (review L2-1). It brings back hand-copied drift, the problem this epic removes, and it breaks the co-versioning above.
- **[AGENT] (orchestrator, 2026-10-12, decision 4)** teax stays an optional runtime dependency. sysml-codegen does not depend on teax, and teax is on no package index. A tool imports teax only when it needs it (B9).
- **[INHERITED: fusion-tea `tests/study/test_generic.py::test_the_tool_resolves_its_own_repo_root`; `manifest.py:62-69` (M4)]** Paths in tool outputs are relative to the target project. They are byte-identical whatever directory the tool is invoked from. The move keeps this property even though its mechanism, `__file__`, cannot survive (B1; Evidence A, finding 2).
- **[AGENT] (orchestrator, 2026-10-12, D7)** Tool identity after the move fits the existing schema fields, and all seven schema files stay byte-identical to `b06585709`.
  - **`tool.path`** is the tool module's path relative to the installed distribution's import root, for example `sysml_codegen/<pkg>/indicators.py`.
  - **`tool-source-digest/v1`** is computed over those package-relative paths and their bytes. The recipe's algorithm is unchanged: a recipe line, then sorted `<path> <sha256>` lines (`manifest.py:88-95`). Its "repo-relative path" is read as "relative to the root the digested sources live under". That is the meaning at both homes. In fusion-tea the tools lived under the repo root, so the two readings agree there. Installed, the sources live under the import root. The same reading covers a target's oracle digest (record template `:304-312`), whose sources live under the project root.
  - **Telling old from new.** The `tool.path` prefix separates pre-move from post-move: `scripts/study/` (or `scripts/integrate.py`) against `sysml_codegen/<pkg>/`. The digest is the revision, because it is content-addressed. sysml-codegen's version string, `0.1.1` at every commit, names nothing.
  - **Old records.** They stay valid as written. No shipped check treats a record's `tools[].path` or a summary's `command` as a live path, and none requires an old digest to recompute. Old and new digests never compare: paths enter the digest, so a moved file gets a new digest even when its bytes are equal.
  - **The record template** carries one labelled history note naming the pre-move prefix, for readers of old records. It is the one exception to SC5's `scripts/study` ban.
  - **If a field cannot fit,** the design raises it through the orchestrator. It does not bump a schema version on its own.
- **[AGENT] (orchestrator, 2026-10-12, D9)** The moved package has two import tiers.
  - **The supported target API** is what the installed runbook and record template tell a target to call, such as `identity.build_sealed` from a route module. It is documented.
  - **The fusion-tea compatibility surface** is every other symbol fusion-tea's consumers use (`CONSUMER_SURFACE.md`). It keeps the same name and behaviour, is not documented as public, and SC6 tests it.

  The design enumerates both lists, including module attributes. It also defines the behaviour of root-dependent functions under the split, such as `manifest.repo_root()`. This replaces the first draft's reading, which made the whole consumer surface a public API for every target.
- **[INFERRED]** `integrate` names no target test, no target environment variable and no target-only dependency. The target declares its repo-scope gates (B4–B6).
- **[AGENT] (orchestrator, 2026-10-12, D8)** A repo-scope gate the target did not declare blocks with `integrate`'s existing `unasked()` outcome (`integrate.py:246-255`): class `BLOCKER`, exit 1, mode `could_not_run`, condition `input-missing`. A `CANDIDATE` still means all ten gates passed (`integrate.py:670-681`). A target that wants a `CANDIDATE` declares both repo gates. This keeps the two return classes and the fifteen slugs.
- **[INFERRED]** The entry-point census gets an importable home in sysml-codegen. It is a four-line grouping of `contracts/model_contract.json` `parameters[]` by `entry_type` (fusion-tea `tests/models/test_model_family_spines.py:178-182`), and both fields exist on `ContractParameter` (`src/sysml_codegen/contracts/models.py:30-35`). `integrate.py:1091-1097` already files the missing home as a smell.
- **[INFERRED]** The tools find teax, the code generator and each other by general means (B3, B7). fusion-tea's environment keeps working through its own declarations or wrappers.
- **[INFERRED]** The tools keep their adapter *disclosure* machinery unchanged: adapter sources in `identity.py:225`, the adapter roots in `read_coverage.py`, and `adapter_source_digest` in the snapshot. Disclosure is not injection, so this is not P-004's smell. The instruction-text requirement below, that shipped text present no adapter route as general practice, is about instructions, not about these fields.
- **[INHERITED: epic Item 3 Success Criteria; fusion-tea `tests/study/test_generic.py`]** The tools name no package, key prefix or adapter. The invariant holds in the new home and extends to the instruction files (SC5).

### Instruction text

- **[INHERITED: epic Item 3 scope 1; research § 1b]** "LCOE" becomes "objective" where the objective is meant: the `SKILL.md` triggers, record template § 3 (`:61-62`), and the runbook's administer step 2 (`:251`). The SC5(b) read-through records each instance.
- **[INHERITED: epic Item 3 scope 1]** The route step becomes "the execution route the target's study policy names, supplied by the package annex". The runbook stops naming the `teax-study` CLI, `StudyRunner` and `PreparedListStrategy` (runbook steps 8-9). That content moves to fusion-tea's policy or annexes, with a ledger row.
- **[INFERRED]** `integrate`'s operator guide ships with `integrate`. It maps each of the fifteen condition slugs to an operator action. fusion-tea's `tests/study/test_integrate_guide_contract.py` holds it to the code, requiring every slug, environment variable and exit code to appear. That contract test is package-agnostic and moves with the guide. The guide's fusion-specific lines move to fusion-tea: the `~/1cfe/agentic-mbse/.env` invocation, the stellarator example arguments, and the second-checkout procedure. This spec reads the revision brief's "four ported instruction files" as `SKILL.md`, `runbook.md`, `record-template.md` and this guide.
- **[INFERRED]** The ported text states the record, annex and discovery-log locations generally. fusion-tea's `exploration/<pkg>/studies/` layout remains a valid instance of the rule without moving any file.
- **[INHERITED: epic Item 3 Dependencies]** References to the goal layer cite "the installed goal runbook" and its section by name, and work whether or not the goal layer is installed. [INFERRED] The text says what applies in a target that does not run the goal layer.
- **[INHERITED: epic Item 3 scope 2; Item 2 design D7 precedent]** The study-policy template is a dated snapshot of the policy's general sections. It keeps each rule's grade and date. fusion-tea's ratified policy is not authority for other targets, and because the template is user-owned, a target's filled copy diverges by design.
- **[INFERRED]** The template also carries a slot for the target's execution route or routes, and an empty tripwire table. General text points at both: the rewritten route step names "the route the target's study policy names", and § 4's resolution ladder sends an unresolved cycle to the tripwire record. Evidence B gives the section-by-section re-check.
- **[INFERRED]** The installed text tells a target what a package annex holds and which package-owned pieces the target supplies: annex, manifest, axis declaration, route and oracle. The runbook reads named annex sections (§ Declared ties, § Baseline pin, § Oracle, § Validity masks; runbook `:60, :94, :108, :129`), and today the only annexes are fusion-tea's. Whether this is an annex template or guidance in the runbook is the design's call.
- **[INFERRED]** Shipped text does not present an adapter-and-glue route or an era pin as general practice. That text moves to fusion-tea with ledger rows (runbook steps 5, 8, 9 and 13; record template § 10 and `teax.era_pin`). The disclosure obligation stays. A record still states what the harness supplies, with "none" as the expected general case, and the record fields keep their names. Grounds:
  - [OWNER]: glue is temporary and "studies will not need glue" (run-study concept, amended 2026-08-18, `:5`, `:117`);
  - [OWNER-VERBATIM] P-004, under which a harness-injected value is "a massive, disgusting smell" (`.project/product/0004-product-identity-parse-walk-emit.md:27-34, :43-48`).
- **[INFERRED]** sysml-codegen's own statements of what it is cover the study layer. `README.md` and the `CLAUDE.md` overview describe `install-commands` and the study tools, which they do not today (`README.md:3-27`). At close, the product ledger gains an entry for the study layer that cites the owner's 2026-10-06 decision, so that P-004's parse-walk-emit definition is not read as excluding it. P-001 already gives the layer a role: "the study layer owns exploration and decisions" (`.project/product/0001-design-search-free-variation.md:66-67`, carried there as [INHERITED] from a concept).

### Fixture and tests

- **[AGENT] (orchestrator, 2026-10-12, decision 5)** The neutral fixture starts from fusion-tea's `tests/study/data/synthetic_pkg`. The design may replace it with a better one.
- **[INFERRED]** The fixture carries enough to complete each tool per SC3, and to run the dry run in SC4.
  - **What `synthetic_pkg` lacks today.** It supports `indicators` only. Its manifest says "the synthetic package has no oracle", and it has no generated modules, no sealed artifact hashes and no SysML source.
  - **What the runbook expects the annex to supply.** Steps 7 and 10 fail closed without an oracle, and steps 5 and 9 need a route.
  - **What the fixture carries.** It supplies the pieces SC4 does not have the dry-run agent write. They are written for the neutral package and borrowed from no fusion-tea package. The fixture loads on the stock route, with no loader exception and no glue.
  - **What a `CANDIDATE` from `integrate` adds** (review L3-6; cut 2 removes it):
    - a git repository with an audited-work commit;
    - a models root with exactly one tracked `*.snapshot.json` beside it;
    - a committed package that regenerates byte-identically under this branch's generator. This ties the fixture to future generator output, as `tests/fixtures/baseline_outputs` already is;
    - a tracked census, and both repo gates declared and backed by real tests;
    - a teax-executed store, a teax checkout with a revision, and the license.
- **[INHERITED: epic Item 3 scope 4]** The package-agnostic subset of fusion-tea's study tests moves, including the guide-contract test. Fusion-specific tests stay in fusion-tea.
- **[INFERRED]** Tests follow this repo's lanes. The default suite needs neither teax nor the syside license. Tests that need teax join the opt-in execution lane (`pyproject.toml` marker `execution`, located through `tests/helpers/teax_discovery.py`). Tests that need the license skip without `SYSIDE_LICENSE_KEY`. `jsonschema` joins the `dev` extra, not the runtime dependencies.
- **[INFERRED]** SC11's clean mypy run may use a recorded per-module override that relaxes `disallow_untyped_defs` (`pyproject.toml:56`) for the ported modules. New and changed functions are fully typed. Reason: annotating about 4,900 lines of ported code is a byte change that ADR-0007's lesson asks to keep out of a move, and it is not in the estimate. The design may type more, and records the override if it keeps one.

### Delivery

- **[AGENT] (orchestrator, 2026-10-12, decision 1)** This item delivers the sysml-codegen side: the skill, tools, installer work, neutral fixture and tests. It also delivers three fusion-tea pieces:
  - a fusion-tea adoption runbook in the shape of Item 2's;
  - the ledger rows;
  - any fusion-tea text that must exist before the ported text drops it. The orchestrator writes that text on a fusion-tea branch.

  Epic criterion 3 becomes runbook verification (SC9). Moving the pin is the owner's call.
- **[AGENT] (orchestrator, 2026-10-12, decision 2)** Artifacts live here, in `.project/active/study-layer-to-codegen/`. The orchestrator adds the pointer and the ledger rows in agentic-mbse.
- **[AGENT] (orchestrator, 2026-10-12, D10)** The adoption runbook's durable home is agentic-mbse's epic tracking, next to the shared ledger, because the epic owns the fusion-tea integration step. The implementing stage drafts it in this item folder. The orchestrator moves it to agentic-mbse before close, so one copy remains and this repo's close-and-delete rule (`.project/README.md` § 4, [OWNER, 2026-08-23]) loses nothing. The review also offered a durable doc in this repo and keeping the item open until adoption; neither was taken.
- **[INHERITED: epic Item 3 scope 5]** fusion-tea keeps its package annexes and its fusion-specific tests. Its local copies of the tools become thin wrappers or are removed.
- **[INFERRED]** From the sysml-codegen merge, the moved package and text are the authority for the general study layer. fusion-tea's local copies stay in use until adoption, so a fix fusion-tea makes to them in that window must reach sysml-codegen by an ordinary change. The adoption runbook's drift check (SC9 step 1) stops the switch until it has. This follows Item 2's runbook precedent ("If it prints a change … stop").
- **[INFERRED]** "One existing study record re-verifies unchanged" means three things together:
  - the record directory's committed files stay byte-identical;
  - re-running the moved `verify` over that record's store, package and manifest, with the record's seed and sample size, reproduces its verification outcome: the same sampled cases, the same re-derived verdicts, and the worst deviation within tolerance;
  - the new summary differs from the record's only in the B2 fields, and that difference is expected, not a failure.
- **[INFERRED]** The adoption runbook states what moving the pin does beyond this item. The generator moves forward by 142 commits, so `integrate`'s regeneration gate (which requires regeneration to change no byte) may refuse fusion-tea packages until they are regenerated. That is a consequence of the pin move. The runbook records it so the owner decides with it in view.

## Non-Goals

- Changing study semantics beyond the closed list, teax APIs, or any committed study record. Source: epic.
- Resolving fusion-tea's policy § 10 against runbook steps 7 and 10 on the oracle. That stays a fusion-tea decision, and the template carries no oracle obligation. Source: epic. The runbook keeps steps 7 and 10 as written, so a fresh target still needs a package-owned oracle.
- The goal layer and the design-choice principle (Item 2).
- Moving fusion-tea's sysml-codegen pin, merging, pushing, and writing to fusion-tea's main checkout. These are the owner's.
- Regenerating fusion-tea's packages under the newer generator.
- Moving fusion-specific study tests or package annexes.
- Fixing the pre-existing guidance-contract failure named in SC11.
- Runtimes other than teax, and new study features such as adaptive strategies or plotting conventions. The adaptive-strategy exclusion is an owner non-goal in the run-study concept.

## Open Questions / Deferred to design

1. **Installer mechanism.** Reuse agentic-mbse's `Installer` or build a standalone installer. Also: where the ownership manifest lives, how the user picks assistants, and how the skill files get into the wheel. If the design reuses the `Installer`, it also says how sysml-codegen's dependency guarantees that API exists (Known Requirements § Installer).
2. **Tool CLI shape.** A `sysml-codegen study <tool>` group, separate console scripts, or `python -m`. Also: what `verify`'s `command[0]` and `integrate`'s `command` and gate producers say (B2).
3. **How the tools find the project root**, given that `__file__` no longer works. Options include an explicit argument, the working directory, or the git top level of the package. Whatever the choice, outputs must stay independent of the working directory.
4. **Closed by D7.** Left to the design: the package name `<pkg>`, and the wording of the record template's history note.
5. **Target-declared gates.** Where a target declares its repo-scope gates, environment variables and recorded distributions (manifest field, configuration file, or arguments). Also: how fusion-tea declares its own, and where the census helper lives in sysml-codegen. D8 settles the undeclared case.
6. **teax discovery.** fusion-tea uses `STOP_PARSER_TEAX_ROOT` plus `packages/teax-simkit`. sysml-codegen's execution lane uses `TEAX_SIMKIT_PATH`. A plain import from the environment is a third option, but it gives gate 1b no checkout to read (B7). `read_coverage`'s permitted-source roots need the same answer (B8).
7. **Record, annex and discovery-log locations** for a general target, given that fusion-tea's layout must stay valid.
8. **Which runbook fail-closed conditions a shipped check enforces** in a fresh target, and which the executor enforces. Today two are fusion-tea tests: the step 14 findings-to-log join and the step 15 placeholder check (`tests/study/test_records.py`). SC4 depends on the answer.
9. **The fixture.** Extend `synthetic_pkg`, or generate a neutral package from a small SysML model, as this repo's fixtures already do. Also: exactly which fusion-tea study tests move. The epic counts about twelve of 55 as package-agnostic, and research § 1b lists candidates.
10. **Closed by D6.**
11. **Wrapper shape in fusion-tea.** One option: re-export modules at `scripts/study/*.py`, which keeps `python scripts/study/verify.py` command lines and `whole_plant_conversion/studies/replay.py:161`'s path-built command working. The other: rewrite the imports in the roughly 36 consumer files.
12. **The rehearsal.** How the rehearsal separates failures caused by the 142-commit generator change from failures caused by the move. SC9 lists which steps are expected to be rehearsable.
13. **Examples or placeholders in the policy template.** The epic's scope says placeholders. The owner's bar allows labelled fusion examples, as long as they carry no fusion-tea identifier (SC5). Also: how the template shows grades. An owner-graded rule was ratified for fusion-tea, and a target adopts it by ratifying its own copy.
14. **Where the operator guide lives once installed.** It could ship inside the package and be found through a resolver, as agentic-mbse's pattern docs are. Or `install-commands` could install it into the target. Either way the skill and runbook must say where it is.

---

## Evidence A: the import-repackaging check

The epic names this check as its one untested bet ("Risks" and "De-risking"). The question: can `scripts.study` and `integrate.py` import as a package without the `scripts.` convention, and what happens to `manifest.repo_root()` and to schema lookup?

**How it was done.** I read the code at fusion-tea `b06585709` and classified every root-dependent call. I also wrote an executable check. It copies the tools into a scratch package, rewrites the imports, and runs every module, the CLIs, and an `indicators` run against `synthetic_pkg`, with a baseline run in fusion-tea's own layout. The script is `.orchestrate-logs/scratch/repack-check/check.py` (gitignored) and runs with `.venv/bin/python .orchestrate-logs/scratch/repack-check/check.py`. The spec session could not run Python, because the command needed approval, so the findings below were first written from reading the code.

**Executed by the orchestrator, 2026-10-12** [AGENT, verified by orchestrator]: exit 0, output at `.orchestrate-logs/scratch/repack-check/output.txt`. It confirms findings 1–5 and 7 as written, with no correction:
- All eight modules import as a package from a target directory.
- `manifest.tool_source_digest()` raises `tool source file missing: scripts/study/indicators.py`, and `common.tool_source_digest` raises the same for `common.py`. `python -m studytools.indicators` on `synthetic_pkg` exits 1 with no stdout.
- With only the two roots split (project root = working directory, tool home = package directory), `indicators` exits 0. Its report equals the fusion-tea-layout baseline in every top-level key except `tool`. The schema files' per-file hashes are equal; the digest differs because paths enter it, and `indicators.py`'s own hash differs only because of the import rewrite.
- `read_coverage`'s declared-source root resolves to the directory holding the package (site-packages when installed).
- `integrate.rederived_census` raises `ModuleNotFoundError: No module named 'tests.models'` in a target without fusion-tea's tests.
- No runtime schema read exists; `importlib.resources` finds a packaged schema.
- `indicators`, `preflight`, `verify` and `integrate` answer `--help` from the package.

The run also shows something D7 must handle. With the root split alone, `indicators`'s `tool.path` rendered as `../pkgsrc/studytools/indicators.py` (`output.txt:73`), because `indicators.py:862` derives it from the project root. Under D7 it must come from the tool home, relative to the import root.

**Verdict: the bet holds.** Nothing found blocks a package import. The cost sits in three places: the root split, tool identity, and `integrate`'s fusion-tea couplings. Each is a requirement above. Only `indicators` was compared output-to-output. `preflight`, `verify` and `integrate` were imported and asked for `--help`, which is why SC12 exists.

1. **The import rewrite is mechanical.** There are eleven `from scripts.study …` lines in six modules: `common`, `identity`, `indicators`, `preflight`, `verify` and `integrate`. One of them sits mid-file at `integrate.py:1218`. Module-level imports are the standard library plus `yaml` (`indicators.py:40`). The rest load lazily, inside functions:
   - `simkit` (teax), at `verify.py:410-411, :484`;
   - `sysml_codegen.snapshot.capture`, at `integrate.py:1078`. It exists at this base with the signature `integrate` calls (`src/sysml_codegen/snapshot/capture.py:17`);
   - `tests.models.test_model_family_spines`, at `integrate.py:1098`.

   The `if __package__ in (None, "")` path inserts become dead code. Expected result: all eight modules import as a package, and only `rederived_census` fails, at call time, in a target with no fusion-tea `tests/` tree.
2. **`repo_root()` means two different things.** Most call sites mean the target project root:
   - repo-relative paths in outputs and errors, across `indicators`, `verify`, `identity`, `preflight` and `integrate`;
   - the `git status` working directory (`common.py:62`);
   - the oracle's `sys_path` (`verify.py:93`);
   - adapter sources (`identity.py:225`);
   - store lookup (`integrate.py:1234`);
   - subprocess working directories (`integrate.py:311, :824`).

   A few call sites mean "where the tool's own sources are": `manifest.tool_source_digest` (`:149`), `common.tool_source_digest` (`:41`), the `TOOL_SOURCE_FILES` lists, and `indicators.py:862`'s `tool.path`. Installed, `parents[2]` lands inside site-packages, so both meanings break. Every target path renders relative to site-packages, and every tool-source digest raises "tool source file missing: scripts/study/…". `indicators`, `preflight`, `verify` and `integrate` all stamp their own digest, so all four would exit 1 with no output. The fix is to split the one root into a project root and a tool home.

   `common.tool_source_digest` is a general function over a named file list. The record template uses the same recipe for an oracle's sources, which live under the project root (record template `:304-312`), and D7's reading of the recipe covers both. [AGENT, verified by orchestrator 2026-10-12]: fusion-tea code outside `scripts/study/` and `tests/study/` never calls `tool_source_digest` or reads `TOOL_SOURCE_FILES`. The only caller outside the tools is `scripts/integrate.py:89` and `:687`, which moves too. The check was a `git grep` at `b06585709` over `exploration/**/*.py`, `tests/**/*.py` and `scripts/*.py`, excluding committed records. So the root split has no fusion-tea caller outside the moved set to preserve.
3. **Tool identity is hard-coded as fusion-tea paths.**
   - `preflight.py:430, :449` and `verify.py:517` write `scripts/study/<tool>.py` as `tool.path`.
   - `verify.py:520` writes `command: ["scripts/study/verify.py", …]`.
   - `integrate.py:84` (`SEAM_PATH`) and the gate producers at `:189-205` name script paths.
   - `integrate` launches the other tools as `[sys.executable, "scripts/study/preflight.py" | "scripts/study/verify.py", …]` with the working directory at the repo root (`:552, :1304, :1353`), and it launches the generator as `uv run sysml-codegen generate` (`:1006`).

   fusion-tea tests pin these strings: `test_output_contract.py:317`, `test_verify.py:234` and `test_integrate_preconditions.py:146`.
4. **Schema lookup needs no runtime resolver.** No tool reads a schema at run time. The schemas appear only in the `TOOL_SOURCE_FILES` digest lists and in tests that validate output with `jsonschema` (`test_output_contract.py:142, :247, :252`; `test_identity.py`; `test_verify.py`). The move needs three things:
   - The schemas ship inside the package. This repo's wheel already ships non-Python package files, such as the ten Jinja2 templates under `src/sysml_codegen/templates/`.
   - Tests find the schemas as package resources.
   - `jsonschema` becomes a test dependency here. fusion-tea lists it, and sysml-codegen does not.

   The schemas close the `tool` block: `additionalProperties: false`, exactly `path` and `source_digest`, and `recipe` pinned to `tool-source-digest/v1` in two of them. That is why D7 fits identity into the existing values.
5. **`read_coverage` declares sources by location.** `read_coverage.py:94` treats every `.py` under `Path(__file__).parents[1]` (fusion-tea's `scripts/`) as a permitted read source, plus the teax tree under `STOP_PARSER_TEAX_ROOT` (`:95-101`). Installed, `parents[1]` is site-packages, which is a different and much larger set. The permitted set has to be stated by meaning (B8), not inherited by location.
6. **`integrate` is coupled to fusion-tea beyond the epic's list.** The epic names the provenance-test read and the backup prefix. On top of those:
   - `REQUIRED_ENV` (`:128-135`) holds four `STOP_PARSER_*_WHEEL` variables, read by fusion-tea's provenance test, including one for 1costingFE;
   - the toolchain block records the `1costingfe` version (`:343`);
   - gates 1a and 5 run fusion-tea tests;
   - the census helper is imported from a fusion-tea test module.
7. **The package-side fingerprint is unaffected.** `indicator-input-fingerprint/v1` hashes package-relative paths (`manifest.py:128-146`), so committed manifest pins stay valid after the move. Only `tool-source-digest/v1` changes, because its canonical text includes the path (`manifest.py:88-95`).

## Evidence B: the policy split, re-checked

The research audit classed `STUDY_POLICY.md` §§ 1–5, 9 and 11 as general, and §§ 6–8, 10 and all worked examples as fusion-specific ([INHERITED: research § 1b], an agent classification). At section level the split holds, with two corrections:

- §§ 6 and 8 need empty slots in the template.
- Several general sections carry fusion-specific lines. Each such line gets a verdict in the SC5(b) read-through, and a moved line gets a ledger row.

| Section | Research | Re-check | Fusion-specific lines inside it |
|---|---|---|---|
| Header ("Status", "Consumers", "Why this exists") | not classed | fusion; the template needs its own header | ratification record, stellarator demo, `~/1cfe/sysml-codegen/.project/research/02-…` (a machine path and a sysml-codegen internal) |
| § 1 Mechanism | general | general | the "Current state (verified 2026-08-02)" paragraph naming `mfe_viability.sysml` asserts |
| § 2 Axis rule [OWNER] | general | general | § 2.2's `mfe_plasma_scaling.sysml:24,66` is an example; § 2.3's 1costingFE / WI-024 sentence |
| § 3 Constraint triage [AGENT, ratified] | general | general | "MR-4-cited" (a consumer requirement number); the `.project/research/…failure-classes…` path |
| § 4 Resolution ladder [AGENT, ratified] | general | general | every worked example (coil thickness, ISS04, pump power, structural mass), including WI-019 and WI-022; its "tripwire (§7)" cross-reference means § 8 |
| § 5 Anti-patterns | general | general | "barred in demo studies"; "criterion 5" (a fusion concept criterion); "no-fallbacks rule" (a fusion-tea rule cited by name) |
| § 6 teax machinery in scope | fusion | fusion content, **but the template needs a slot**: the rewritten route step points at "the route the target's study policy names" | the IFE harness path; "to confirm at Item 5 spec time" |
| § 7 Hypotheses | fusion | fusion | — |
| § 8 Tripwire record | fusion | **the empty table is general**: § 4 sends an unresolved cycle there. fusion-tea's table is empty today | — |
| § 9 Axis forces and framing [OWNER] | general | general | the `scripts/study/indicators.py` path becomes "the installed indicators tool"; the concept SC-2/SC-3 citation becomes a provenance line |
| § 10 Verification [OWNER] | fusion | fusion; the template stays silent on the oracle (epic) | — |
| § 11 Process sizing [AGENT] | general | general | the `work/orchestration/GOAL_RUNBOOK.md` citation becomes "the installed goal runbook" |

---

## Revision 2026-10-12

Revised after the fresh review (`spec-review.md`, verdict Revise) and the orchestrator's decisions in `briefs/spec_revision.md` (D6–D11). Changes by review ID:

- **L3-1** (semantics contradiction). "Study semantics do not change" now reads "beyond the closed list". A new section, § What the move may change, lists B1–B11, and SC12 is the parity criterion. ADR-0007's byte-faithful lesson is cited. D8 settles the undeclared-gate outcome: the existing `unasked()` blocker.
- **L3-2, L3-3** (schemas, SC7). D7 is recorded: schemas byte-identical, `tool.path` relative to the import root, `tool-source-digest/v1` read as "relative to the root the sources live under", and the prefix rule as the discriminator. SC7 is now mechanical, with a pre-move-document test. OQ4 is closed.
- **L3-4, L1-6, L3-5** (SC5). The identifier classes are widened, the package names and prefixes are a closed list, and the SC5(b) per-line read-through is added and feeds SC10. The example strictness is labelled [INHERITED: epic Item 3 SC4]. The LCOE grep sentence is gone. One labelled history note may name `scripts/study` (D7).
- **L2-2, L1-2, L1-3, L5-1** (budget). A new section, § Estimate and cut order, carries D11's cut order and the estimate: about 37.5h execute and about 5.3 days total against the epic's 2, stated, not hidden. Every SC is tagged contract or evidence. SC3's widening and SC4's size are graded [INFERRED] against epic Item 3 SC2 and Item 2's D3 dry run, which stopped after round 1.
- **L3-12** (runbook home). D10 is recorded: drafted here, moved to agentic-mbse before close.
- **L1-1.** The Problem's bar is graded [AGENT] (orchestrator Align reading).
- **L1-4, L3-7.** D9 records the two import tiers, and SC6 now enumerates attributes and signatures and defines behaviour for the root-dependent functions.
- **L1-5, L2-1.** D6 records the package form inside the distribution and the two rejected alternatives. OQ10 is closed.
- **L2-3.** P-001 is cited, and a requirement keeps the adapter disclosure machinery, which is not P-004's smell.
- **L3-6.** SC3 defines "complete" per tool and where negative cases are documented. The fixture requirement lists what an `integrate` `CANDIDATE` costs, and cut 2 removes it.
- **L3-8.** The orchestrator's verified fact is in Evidence A finding 2, and D7's reading covers oracle digests.
- **L3-9.** A new Installer requirement covers the dependency guarantee for a reused `Installer`. OQ1 asks how it is made, and SC9 step 2 checks fusion-tea's agentic-mbse pin.
- **L3-10.** SC9 step 4 now covers `pyproject.toml` changes under fusion-tea's hand-edited lock. `jsonschema` goes in the `dev` extra.
- **L3-11.** A recorded per-module mypy override is allowed, and the estimate assumes it.
- **L3-13.** SC1 says how agentic-mbse is supplied. SC2 states the noninteractive outcome. SC4 names its record checks and ties them to OQ8. SC9 lists the steps expected to be rehearsable.
- **L3-14.** SC9 step 5 switches fusion-tea's spine test to the shipped census helper.
- **Scope added by interpretation.** The revision brief counts "four ported instruction files", and the first draft covered three. This revision reads the fourth as `integrate`'s operator guide, which fusion-tea's guide-contract test ties to the code. A new requirement ships it, and OQ14 asks where it lives once installed. Its hours are inside SC5's estimate.
- **Product-lens.** spec-F2's concern (ask the owner before reinterpreting "ships from sysml-codegen") is met by D6, which keeps the literal reading. The lens was not re-run on this revision.

---

## Related Artifacts

- **Epic:** agentic-mbse `.project/backlog/epic_wrap-split.md` at `ac5fb1a`, Item 3, header "Owner decisions carried in", Success Criteria.
- **Required Reading (from the epic):** research § 1b and Open Question 1; fusion-tea `.claude/skills/run-study/{SKILL,runbook,record-template}.md`; fusion-tea `modeling_project/STUDY_POLICY.md`; fusion-tea `.project/concepts/run-study-skill.md` (owner factoring, `:19-27`, `:142-143`); fusion-tea `tests/study/test_generic.py` and `conftest.py`; `src/sysml_codegen/cli/__init__.py` `install-commands`. All fusion-tea paths were read at `b06585709`.
- **Research:** agentic-mbse `.project/research/20261005-204804_wrap-split-agentic-mbse-fusion-tea.md` § 1b, Open Question 1.
- **Shared ledger:** agentic-mbse `.project/active/wrap-split-migration-ledger.md` (Item 3 appends its own section).
- **Precedent:** agentic-mbse `.project/completed/20261012_goal-layer-port/design.md` D7 (dated-snapshot authority) and Appendix D3 (the dry run), and `evidence/fusion-tea-runbook.md` (post-merge runbook shape).
- **Consumer surface:** fusion-tea `CONSUMER_SURFACE.md` (orchestrator-generated at `b06585709`).
- **Briefs:** `.project/active/study-layer-to-codegen/briefs/spec.md` and `briefs/spec_revision.md`.
- **Spec review:** `.project/active/study-layer-to-codegen/spec-review.md` (verdict Revise, committed `7224e54`).
- **Repackaging check script:** `.orchestrate-logs/scratch/repack-check/check.py` (gitignored; executed by the orchestrator 2026-10-12, output `output.txt` beside it; see Evidence A).
- **Product-lens:** `.project/active/study-layer-to-codegen/product-lens.md`.
- **Design:** `.project/active/study-layer-to-codegen/design.md` (to be created).

---

**Next Steps:** After approval, proceed to `/_my_design`.
