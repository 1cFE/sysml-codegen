# Design Review: Move the study layer to sysml-codegen (WRAP-SPLIT Item 3)

**Design:** `.project/active/study-layer-to-codegen/design.md` (committed `4533510`)
**Spec:** `.project/active/study-layer-to-codegen/spec.md` (`a09bdb1`)
**Review File:** `.project/active/study-layer-to-codegen/design-review.md`
**Date:** 2026-10-12
**Run:** non-interactive `/_my_design_review` stage for the agentic-mbse orchestrator. Every claim below was checked against the staged sources (`.orchestrate-logs/src/`) or this worktree; nothing was executed against a scratch copy. The product-lens instructions were unreadable, so the lens ran on the same fallback method as the spec stage; its block and my disposition are appended to `product-lens.md`.

---

## The Point

A modeling project that uses sysml-codegen and teax gets the whole study capability by installing sysml-codegen and running `sysml-codegen install-commands`. The capability is the `run-study` skill with its runbook and record template, a study-policy template, and the tools those steps call. The project can then run a study from intake to a committed record, and hand it to a second agent, with nothing copied from fusion-tea.

- [OWNER] (epic header, 2026-10-06): the study layer ships from sysml-codegen. [OWNER-VERBATIM] "ported and generalized … installed like everything else".
- [AGENT] (orchestrator Align reading): the bar is a working capability in a fresh target, not copied files.
- [NEED] The owner's shape survives: lightweight skill, runbook, policy rulebook and tools; indicators never gate; intake is collaborative; one skill serves the executing and administrator roles; an unresisted axis is surfaced as a sign the model is underdeveloped.
- [NEED] fusion-tea loses no information. [INFERRED] Semantics change only by the closed list B1–B11 (ADR-0007's byte-faithful lesson).
- The move must also leave `integrate` able to judge any target, not just fusion-tea (D8, SC8).

## Fundamental Assessment

**Sound, with four must-fix defects. Verdict: Revise.**

This is the right piece of work, and the approach is the right one. The design does what a byte-faithful move should do: it copies the code, then replaces every "where this file sits" question with one of three named roots in one module (`roots.py`). It reuses agentic-mbse's installer instead of writing a second one. It turns fusion-tea's hard-coded facts into a declaration the target owns. It surfaces its premise conflicts up front instead of resolving them silently. I would not ask for a different architecture.

The problems are in the seams where the move meets things the design did not look at closely enough. Four of them would ship a wrong result or block the plan:

- **M1. A `CANDIDATE` for a non-fusion target claims checks that never ran.** Gates 1a and 5 keep fusion-tea's `checked` text ("installed wheel artifacts", "the family twins") while running whatever test the target declared.
- **M2. fusion-tea's integrate gate 7 would refuse every package after adoption.** Its route modules import the tools through the `scripts.study` wrappers, and the new read-coverage roots do not permit those wrapper files.
- **M3. Gate 1b can read the target's own git HEAD as teax's revision.** The fallback teax location is "the parent of wherever `simkit` imports from", which is inside the target's work tree when teax is installed into a project `.venv`.
- **M4. The `sysml-codegen study` dispatch fails an existing conformance pin.** `tests/conformance/test_public_authority_switch.py:216-240` asserts that no module reachable from `sysml_codegen.cli` reads the environment; the study tools do.

**On the product-lens.** The lens gate is CLEAR (no owner or [HARD] contradiction). It reported structural smell (b) as fired: DD8 moves what gates 1a and 5 certify into the target's declaration without saying so. I reproduced the defect it points at (M1). I re-graded the smell itself: the ownership move is stated, in spec D8/B5 and in the design's Core Concept (`design.md:95`, `:101`). What is unstated is that the return document still asserts fusion-tea's checks. That is a defect in the move, fixable locally, not a hidden shift that undermines the foundation. So I recommend Revise, not Rework. If the orchestrator holds the lens's grading, the process rule makes this Rework scoped to DD8's return semantics, which is the same work as M1. Smell (a) fired twice, both disclosed; I disposed of both in the ledger.

**Is the complexity right for the problem?** Mostly. The design is large (19 decisions, 10 appendices) because the spec has 12 criteria, a closed list and a parity criterion. The new code is small and well bounded: `roots.py`, `declarations.py`, `census.py`, `cli/install.py`. The 43-hour estimate is driven by the spec's widened criteria (SC3, SC4, SC12), which D11 already accepted. I found little gold-plating; see area 6 below.

---

## Premise conflicts: the orchestrator's provisional positions, checked

- **Conflict 1 (no agentic-mbse version bump; `INSTALLER_API_VERSION` instead): holds.**
  - The cost of a bump is real. The snapshot loader refuses any snapshot whose `authority.agentic_mbse_version` differs from the running agentic-mbse (`src/sysml_codegen/snapshot/envelope.py:459-473`), and 22 v6 snapshots are committed.
  - The replacement follows an existing pattern, not a new one. `_upstream_pins.py:39` already pins `SEMANTIC_EVIDENCE_API_VERSION = "semantic-evidence/v2"` beside the package version, and `tests/unit/test_package_metadata.py` checks both.
  - It fails closed: an old agentic-mbse makes `install-commands` exit 1 with the revision needed.
  - The remaining hole is in the implementation, not the route. If `cli/install.py` imports `install_bundle` or `INSTALLER_API_VERSION` by name at module top, and `cli/__init__.py` imports `cli/install.py`, an old agentic-mbse breaks every subcommand, including `generate`, with an `ImportError`. See S4.
  - The API string must cover everything sysml-codegen calls, not just the two names in the comment (S4).
- **Conflict 3 (a new neutral model instead of `wi014_toy`): holds.** `tests/fixtures/wi014_toy/PROVENANCE.md:3` says "Imported verbatim … from the fusion-tea WI-014". The fixture's gate-2 and gate-4 premises also hold: live and snapshot generation are byte-identical (pinned by `tests/conformance/test_exact_route_generated_package.py`), and capture is deterministic (`envelope.py:44-45`), with sources recorded as portable referents.
- **Conflict 4 (`integrate` writes its usual `BLOCKER` when teax is missing): holds.** Gate 0 already probes `simkit` today (`scripts/integrate.py:525-536`), so I9 is today's outcome with a new message. One inconsistency to fix in wording (m3): the conflict's argument is "integrate writes a return document on every exit path", but DD2 adds an exit 2 with no document when no project root is found. Unknown argparse flags already exit 2 with no document today, so the new case is consistent with practice. The design should say so instead of claiming every path writes a document.
- **New, not surfaced by the design: premise conflict 5.** The closed list keeps the `checked` text of gates 1a and 5 byte-faithful, which works against SC8's goal that `integrate` judges any target. This needs an orchestrator decision (M1).

---

## Dimensional Review

### 1. Spec Compliance
**Assessment:** Concerns

- Every criterion SC1–SC12 has a design element and a validation row (`design.md:338-353`). Every open question gets a decision with rejected alternatives.
- **SC8 is met in form but not in meaning (M1).** A non-fusion `CANDIDATE` says what fusion-tea's gates checked.
- **B7 is not met (M3).** B7 says "gate 1b never passes without comparing a revision". The design compares a revision, but possibly of the wrong repository.
- **SC9's rehearsal cannot see the adoption break in M2.** Run C runs only `pytest tests/study tests/models/…`; the break shows only when integrate executes a real fusion route under read coverage (S2).
- **SC4 can pass on the evidence script alone** without showing that the installed Check lines would have stopped a bad record (S6, lens design-F3).
- **The era-pin disclosure rule is lost** (S5, lens design-F2).
- **Capture fidelity is good.** The design treats the [INFERRED] dependency-bound requirement (`spec.md:193`) as challengeable and surfaces it as a premise conflict instead of silently dropping it. It carries grades into The Point. The one miss is conflict 5 above, which law 4 says to surface.

### 2. Pattern Consistency
**Assessment:** Concerns

- **Good:** the subpackage name follows the repo's one-noun-per-concern layout; the API pin follows `_upstream_pins.py`; `[tool.<name>]` is the standard home for target configuration; the installer is reused; `sysml-codegen study <tool>` keeps the single entry point.
- **Collision with a conformance pin (M4).** `test_no_cli_flag_or_environment_variable_selects_a_route` walks every `sysml_codegen` module reachable by import from `sysml_codegen.cli`, using an AST walk that sees imports inside functions too (`test_public_authority_switch.py:175-185`, `:541-563`). It fails if any of them mentions `os.environ` or `getenv`. `roots.py`, `integrate.py` and `read_coverage.py` all do. The test's purpose is "no environment variable selects a construction route", which the study tools do not violate, so the right fix is to scope the pin, not to hide the import behind a string. That is a recorded decision, not a plan detail.
- **Second pin.** `test_the_public_api_exports_no_second_construction_entry_point` (`:243-254`) pins `cli.__all__` by value, including `CODEGEN_COMMANDS`, which DD7 deletes. Small, but the design should name it.

### 3. Abstraction Quality
**Assessment:** Concerns

- **`roots.py` is the right abstraction.** One module, three named roots, `__file__` used once where it is actually correct (`TOOL_HOME`). This is not a lift-and-shift with new names. The bulk of the package is deliberately byte-faithful, which is what ADR-0007's lesson asks for.
- **The project-root rule has a silent failure mode the design misstates (S1).** Bet B1 says that if the target is not the git top level, the tool "is refused (exit 2)". It is not refused. In a monorepo, or when an agent's working directory is inside a different repository than the package, `git rev-parse --show-toplevel` returns a root and the tool writes paths relative to it. `repo_relative_posix` renders paths outside the root with `..` segments by design (`manifest.py:62-69`), so the output looks plausible. The declaration is also read from that root's `pyproject.toml`.
- **The fusion-tea wrappers mutate `os.environ` at import time (m1).** That is a process-wide side effect of an `import` statement. An in-process override in `roots.py` would do the same job for library imports; the variable is only needed when the wrapper runs as a script.
- **`common.tool_source_digest(files)` becomes tool-home-only (m2).** D7 says the same recipe covers a target's oracle digest, whose sources live under the project root (record template `:304-312`). After the move, no shipped function can compute it. A `root` parameter defaulting to `TOOL_HOME` keeps the function general at no cost.
- **Per-invocation gate table.** The idea is right, but the gate functions take `(request, env, state)` and reference `GATES[i]` directly (`integrate.py:944-945`, `:990-991`). Say where the table and declaration live during the run (m7).

### 4. Duplication Avoidance
**Assessment:** Pass

- One installer, reused with a separate manifest. One census implementation, which fusion-tea's spine test switches to (runbook step 5), so gates 4 and 5 stop disagreeing by construction.
- The two-copies window between merge and adoption is bounded by the runbook's drift check.
- The licensed-lane gate-refusal tests overlap the SC12 parity cases. That is defensible (durable tests versus one-shot evidence) but is a trim candidate if the estimate needs it (area 6).

### 5. Data Structure Clarity
**Assessment:** Concerns

- `IntegrateDeclaration` is typed and strictly validated; the declaration format has worked examples for a fresh target and for fusion-tea (`design.md:543-569`).
- **The declaration lacks the field M1 needs.** The `checked` claim for each repo gate is part of what the target declares, but the shape has nowhere to put it.
- **Gate targets are unvalidated strings.** An absolute path or `../` path runs a test outside the project and still records a pass (m4).

### 6. Route Safety
**Assessment:** Concerns

- **Good:** the undeclared-gate path is fail-closed. No file, no table, or a misspelled table name all give an empty declaration, so both repo gates raise `unasked` and the run ends in `BLOCKER`. A malformed table blocks at gate 0 with `input-invalid`. A declared gate whose file is missing makes pytest exit 4, which `run_pytest_gate` reports as could-not-run (`integrate.py:928-933`).
- **Unsafe fallback (M3).** Without `TEAX_SIMKIT_PATH`, gate 1b runs `git rev-parse HEAD` at the parent of the probe's `simkit` directory (`design.md:430`). When teax is a non-editable install in the target's `.venv`, that directory is `.venv/lib/python3.x/site-packages`, which is inside the target's git work tree. `git -C` succeeds there and returns the target's own HEAD. The toolchain block then records the target's commit as `teax_revision` on every return, and gate 1b compares against it.
- **Unsafe fallback (S1).** The git fallback for the project root picks the wrong root silently in two common layouts.
- **Dispatch.** `sysml-codegen study <tool>` should use `choices=` on the tool positional so an unknown tool is an argparse error, not an import error.

### 7. Bets & Decisions Integrity
**Assessment:** Concerns

- Every decision names its rejected alternatives with a reason. That is well done.
- **B1's stated failure mode is wrong** (S1): the realistic failure is a silent wrong root, not exit 2.
- **B5, the riskiest bet, is partly false (M2).** fusion-tea's consumers do depend only on names, signatures and root-relative behaviour, but integrate's read-coverage gate also depends on which files those imports open.
- **Hidden bets, unstated and each false:**
  - The `checked` text of gates 1a and 5 is target-neutral (M1).
  - The parent of the `simkit` import location is a teax checkout (M3).
  - No existing test forbids environment reads in modules reachable from the CLI (M4).
  - fusion-tea route modules stay inside read coverage after the switch (M2).
- **One hidden bet that holds:** the importlib `sys.modules` replacement trick in DD14 works for `import scripts.study.x`, `from scripts.study import x` and `python -m scripts.study.x`. CPython's loader re-reads `sys.modules[name]` after executing a module and sets the parent attribute from it. The wrapper must still handle `__name__ == "__main__"` for the `-m` form (`exploration/aries_integrated/studies/design_protocol.md:23` uses it).

### 8. Reader Comprehension
**Assessment:** Concerns

- The design gives a mental model before mechanism: The Point, then "three roots, one declaration, one installer" in the Core Concept. A tired engineer gets the shape from the first 100 lines.
- **Two different "B" series collide.** Key Bets are B1–B6 and the spec's closed list is B1–B11, and the design uses both bare. "B4" means "a neutral model runs on stock teax" in the Risks section (`design.md:325`) and "gate 0's environment sweep" in the closed list. "B7" in DD10 means the closed list. Rename the bets (for example KB1–KB6) so a citation is unambiguous.
- Appendix-level density is appropriate for a plan input.

---

## The six areas the brief asked about

1. **Engineering quality.** `sysml_codegen.study` is a clean, bounded package. The ported modules are deliberately unchanged apart from the edit map, and the edit map's SC5 docstring edits cover every identifier the spec's patterns find in the staged tools (I ran them). Weak points: the project-root rule's silent wrong-root cases (S1), wrapper environment mutation (m1), and library callers getting `RootError` from deep inside `repo_relative_posix`, which is neither `ToolError` nor `ManifestError`. That last point is harmless in fusion-tea, where the wrappers always set the root, but it should be documented in Appendix C. **Remaining fusion-tea layout smells:** the `checked` text (M1); gate 4's snapshot discovery, which requires exactly one `*.snapshot.json` beside the models root (`integrate.py:1056-1073`), while this repo's own docs and fixtures name snapshots `instance_graph_snapshot.json`, which that glob does not match (S7); and `prog="verify.py"` in `sysml-codegen study verify --help` (a kept cosmetic smell).
2. **Declaration surface.** `pyproject.toml`'s `[tool.*]` table is the right home. A target without a `pyproject.toml` simply has no declaration and blocks, which is fail-closed. To declare, it creates a `pyproject.toml` holding only the tool table. Before shipping that advice, check how `uv run` behaves in a directory whose `pyproject.toml` has no `[project]` table; I did not verify it. A monorepo is the real gap: the declaration is read from the git top level unless `SYSML_CODEGEN_PROJECT_ROOT` is set (S1). The undeclared-gate path is truly fail-closed (Dimension 6). The new hole is that a declared gate can pass while the return claims fusion-tea's checks (M1).
3. **Installer reuse.** Appendix B is minimal and behaviour-preserving for agentic-mbse's callers. The default manifest keeps reading both legacy and current files, and `install_bundle` is the exact loop body of `install_assistants` (`installation.py:434-440`). Separate manifests do isolate the two installers in both orders. Pruning only visits keys under the bundle being installed, from the installer's own manifest (`:206-230`). Legacy-link adoption only fires for absolute links into an agentic-mbse source checkout at the same relative path (`:47-68`), and agentic-mbse never shipped `run-study` or `teax-completion`. Residual risks: a future name collision between the two installers' assets (both would treat the other's file as a local edit), and first-run handling of an existing unmanaged `teax-completion.md` (S4). `install_bundle` is an acceptable seam. It leaks `link_mode` and `dev`, which sysml-codegen should pass as constants.
4. **Byte-faithfulness.** The edit map stays inside B1–B11, with two unlisted items to name explicitly: the new gate-0 `input-invalid` path for a malformed declaration (under B5), and the no-root exit 2 (under B1); see m3. SC12's whole-document comparison after masks can catch an unlisted difference. Two weaknesses (S3): the noise step masks whole fields that differ between two original runs, which would also hide wording changes in `detail` strings that embed pytest timings or temporary paths; and coverage skips gate 3, a gate-7 read-coverage refusal and the internal-error path. The masks for B2 and B8 are legitimate. One point to state: the fixture's route imports `sysml_codegen.study.identity` in both runs, so integrate-level parity never exercises the original `build_sealed`; the in-process library parity is what covers it.
5. **fusion-tea adoption.** The module aliases do keep `replay.py`, the `-m` invocations, both cwd-determinism tests and the 32 compatibility names working. I checked the mechanism and the attribute list against `CONSUMER_ATTRIBUTES.md`. They do not keep integrate working (M2). The three-run rehearsal can in principle separate move failures from the 142-commit jump, but as written it has a circular pass criterion and cannot see M2 (S2).
6. **Plan-readiness and size.** A plan stage could phase this without redesign once M1–M4 are decided. Each needs a choice the plan should not make on its own. The 43-hour estimate (about 6 days against the epic's 2) is honest, but it omits three things: the fusion-tea step-5 test edits (15 staged fusion test files reference the old paths or variables, and nobody is assigned to draft them), the fix for M2, and the conformance amendment (M4). I found little gold-plating. Trim candidates if the plan needs hours: make the design's own "defer lower-value test moves" lever the default (about 2h), and keep the licensed-lane gate-refusal tests to the SC3 and SC8 minimum, since SC12 already covers each refusal once (about 1–1.5h).

---

## Issues by Severity

### Critical (must fix before planning)

- **M1. Gates 1a and 5 assert fusion-tea's checks for any target.** *(Spec Compliance, Data Structures; lens design-F1)*
  - Evidence: `GATES` fixes `checked` for 1a as "the pinned package revisions and installed wheel artifacts" and for gate 5 as "the canonical tree, the family twins and the tracked census" (`scripts/integrate.py:189-190`, `:199-200`). Every row, passing or not, copies it into the return (`:1456-1465`, `:609-619`). DD8 changes only `producer` (`design.md:165`, `:434`). The fixture's own gates check that two packages import and that a census matches (`design.md:607`), yet its `CANDIDATE` will claim wheel artifacts and family twins were checked.
  - Why it matters: a `CANDIDATE` exists to say what was proven. This is the "passed versus nobody checked" confusion the seam was built to prevent.
  - Fix: raise premise conflict 5 with the orchestrator and ask for a closed-list item under B5. Let each declared gate carry its `checked` text, for example `[tool.sysml-codegen.integrate.gates.pinned-packages] target = "…", checked = "…"`. fusion-tea declares today's two strings, so SC12 parity and SC8's "same ten gates" hold. With no declared text, the row states what ran ("the target-declared check `<target>` passed"). Add a test that pins rows 1a and 5 of a non-fusion return. Document in the integration guide what each repo gate is meant to establish.
- **M2. After adoption, fusion-tea's gate 7 refuses every package.** *(Spec Compliance, Bets; brief area 5)*
  - Evidence: eight fusion-tea `study_route.py` modules import `from scripts.study import common, identity` at module top (`CONSUMER_SURFACE.md:43, :50, :57, :62, :67, :72, :89, :97`; for example `exploration/stellarator_e2e/studies/study_route.py:64`). `run_route` activates the read observer before it imports the route module (`read_coverage.py:253-257`). So every file those imports open is checked against the declared roots. Today the declared roots include fusion-tea's whole `scripts/` directory (`read_coverage.py:94`). After B8 they are the route directory, `TOOL_HOME/sysml_codegen` and teax (`design.md:418`). The wrapper files at `fusion-tea/scripts/study/{common,identity}.py` are in none of them, and the fusion root is not under `sys.prefix`, so `classification` raises "undeclared dependency read" (`read_coverage.py:126-132`). Gate 7 refuses with `read-coverage-refused`.
  - Fix, choose one and record it:
    - (a) At runbook step 5, rewrite only the route modules' imports to `sysml_codegen.study`. These are about 8 package-owned files, not committed records. Keep the wrappers for every other consumer.
    - (b) Add an optional `read-roots` key to the declaration. fusion-tea declares `scripts/study`.
    - (c) Have `read_coverage` also declare the files of any module that aliases into `sysml_codegen.study`.

    I recommend (a). It is the smallest change, it keeps B8's "permitted sources by meaning" clean, and route modules are exactly the "supported target API" callers that should import the package directly. Either way, add an integrate run on one real fusion package to the rehearsal (S2).
- **M3. Gate 1b and the toolchain block can record the target's own commit as teax's revision.** *(Route Safety; B7)*
  - Evidence: without `TEAX_SIMKIT_PATH`, the teax location is "the parent of the probe's simkit directory" and `teax_revision()` runs there (`design.md:430`). The probe prints `simkit.__file__`'s parent (`integrate.py:143`). For a non-editable teax in a project `.venv`, that parent is `site-packages` inside the target's work tree, where `git -C … rev-parse HEAD` returns the target's HEAD (`integrate.py:316-321`).
  - Fix: read a teax revision only from `TEAX_SIMKIT_PATH`. Without it, gate 1b is could-not-run (`env-missing`, naming the variable) and `toolchain.teax_revision` is `null`, which is today's convention for an unavailable fact (`integrate.py:332-337`). If the design wants to keep a fallback, it must prove the location is a teax checkout: the git top level contains the `simkit` directory as a tracked path (`git ls-files --error-unmatch`). The shorter rule is simpler, and B7 already says that no checkout means block.
- **M4. The CLI dispatch fails two existing conformance pins.** *(Pattern Consistency, plan-readiness)*
  - Evidence: `tests/conformance/test_public_authority_switch.py:216-240` fails if any module reachable from `sysml_codegen.cli` mentions `os.environ` or `getenv`. `roots.py`, `integrate.py` and `read_coverage.py` do. `:243-254` pins `cli.__all__` by value, including `CODEGEN_COMMANDS`, which DD7 deletes.
  - Fix: decide the amendment in the design and record it as a builder-register ADR. Recommended: put the study dispatch in its own module (`cli/study.py`). Scope the environment-reader pin to the construction closure (`run_codegen` and the `generate`, `snapshot` and `seal` handlers) or add a reviewed allowlist naming `sysml_codegen.study.*`. Keep the pin's purpose: no environment variable selects a construction route. Do not hide the import behind an `importlib` string to dodge the walker.

### Major (should fix)

- **S1. The project-root rule picks a wrong root silently, and Key Bet B1 misstates it.** *(Abstraction, Route Safety, Bets)*
  - Cases: a monorepo, where the git top level is not the modeling project; and an agent working directory inside another repository while `--package` points at the target.
  - Effects: paths render relative to the wrong root with `..` segments, and the declaration is read from the wrong `pyproject.toml`.
  - Fix:
    - Correct B1's "if false" line.
    - Every CLI that takes `--package` refuses (exit 2) when the package does not resolve under the project root. Check the unresolved path too, since fusion-tea's tracked package roots can be symlinks (`integrate.py:734-736`).
    - Document the monorepo rule (set `SYSML_CODEGEN_PROJECT_ROOT`) in the guide and runbook.
    - Make `install-commands`' default directory agree with the tools' project root, or say why it need not.
    - Consider anchoring the root at the nearest ancestor `pyproject.toml` that has a `[tool.sysml-codegen]` table, before falling back to git. That makes the declaration's home and the project root the same thing.
- **S2. The rehearsal (DD15, Appendix H3) cannot see the failures that matter, and its pass criterion is circular.** *(Spec Compliance SC9; brief area 5)*
  - The expected observation is "C−B lists only failures with a step-5 edit", but step 5 is defined as "each fusion-tea test edit that run C attributes to the move". Enumerate the expected edits now from the staged tests. Examples:
    - `SCHEMA_DIR` (`tests/study/conftest.py:27`), which step 5's `git rm` breaks;
    - `integrate.TEAX_SIMKIT_SUBPATH` and `REQUIRED_ENV` (`test_integrate_preconditions.py:94`, `:213`; `test_integrate_guide_contract.py:34`);
    - read coverage declared through `STOP_PARSER_TEAX_ROOT` (`test_read_coverage.py:254`, `test_single_point_gate.py:24`, `:50`, `test_study_publication_fail_closed.py:215`);
    - old tool-path literals in 8 files.
  - Then the acceptance rule: every C−B failure falls in a pre-listed class; anything else is a defect until shown otherwise.
  - Run A, B and C in one recorded environment with the license and teax present, and report skip counts per run. A test that skips in C but not B is a failure.
  - Compare failure messages, not only test ids, so a test that fails in B for the generator jump and in C for the move is not hidden.
  - Add one integrate run on a real fusion package in B and C. That is the only step that would show M2.
  - Say who drafts the fusion-tea step-5 edits, where (`$EV/fusion-tea/`), and with what hours.
  - Say where fusion-tea sets `TEAX_SIMKIT_PATH` for read coverage outside integrate, not only in `.venv/integration.env`.
- **S3. SC12 parity: mask by token, not by field, and close two coverage gaps.** *(brief area 4)*
  - Normalize known noise (temporary directories, uuid tokens, pytest timing lines) with a declared pattern list, and list every pattern and mask in `report.md` with its reason. Whole-field masks on `detail` would hide changed blocker wording.
  - Add cases for gate 3 (`handwritten-lost`), a gate-7 read-coverage refusal (the route reads an undeclared file), and `seam-internal-error`.
  - State which `identity` the fixture route imports in the original runs.
- **S4. Pin the whole installer surface, import it lazily, and say what happens to existing files.** *(brief area 3; Conflict 1)*
  - `INSTALLER_API_VERSION`'s comment and agentic-mbse's test should name everything sysml-codegen calls: the `Installer(…, manifest=)` constructor and its `decide` vocabulary (`skip`, `overwrite`, `backup`, `skip_all`, `overwrite_all`), `write`, `actions` and its keys, `save`, `install_bundle` and `frontmatter`.
  - `require_installer_api()` reads the constant with `getattr` from the module, and `cli/install.py` is imported only inside the `install-commands` handler, so an old agentic-mbse cannot break `generate`.
  - Add a sysml-codegen test that no asset name collides with agentic-mbse's shipped bundle and command names.
  - State first-run behaviour for a target with a `teax-completion.md` from today's installer, which has no manifest entry. It is adopted only if its bytes equal the shipped file; otherwise it is reported as skipped on every noninteractive run until `--force`. The output should say so.
- **S5. Keep the era-pin disclosure rule.** *(lens design-F2)* The record template keeps a non-null `teax.era_pin` meaning (`design.md:814`). But step 13's sentence "the report states that pin as a reproduce prerequisite at the claim site" (fusion-tea `runbook.md:198-202`) leaves with the adapter class. Keep one conditional line in the general step 13, or move non-null pins wholly to target policy with their rule and a ledger row.
- **S6. SC4 must show the installed checks work, not only the evidence script.** *(lens design-F3)* The dry-run agent runs each installed step-14 and step-15 Check line and records what each printed, before `check_record.py` runs. Any disagreement between the two is a finding.
- **S7. Document gate 4's snapshot convention for general targets.** Gate 4 finds the snapshot by globbing exactly one `*.snapshot.json` beside the models root (`integrate.py:1056-1073`). This repo's `CLAUDE.md` example and all 22 fixtures use `instance_graph_snapshot.json`, which that glob does not match. The behaviour cannot change under the closed list, so the shipped guide and annex template must state the rule. File a follow-up for an explicit `--snapshot` flag.
- **S8. Fix the SC4 dry-run copy recipe under cut 3.** H2 relocates the package to `packages/station_study/` and the oracle and route to `studies/station/` (`design.md:731-733`). Under cut 3 it copies the fixture's manifest, whose oracle `sys_path` is `studies` (`design.md:599`). `verify` resolves the oracle as `project root / sys_path` (`verify.py:93`), so it would fail. Either keep the fixture's relative layout in the target, or state the manifest edits.

### Minor (consider)

- **m1.** DD14 wrappers should not mutate `os.environ` on import. Give `roots.py` an in-process override for imports, and set the variable only when the wrapper runs as a script. Also say whether it overwrites or `setdefault`s.
- **m2.** Give `common.tool_source_digest(files, root=TOOL_HOME)` a root parameter so the supported API can compute the oracle digest D7 describes.
- **m3.** Name the two new outcomes under the closed list: malformed declaration → gate-0 `input-invalid` (B5), and no project root → exit 2 with no document (B1). Reword premise conflict 4 so it does not claim every exit path writes a document.
- **m4.** Validate declared gate targets as project-relative paths that stay inside the root.
- **m5.** Lens design-F4: record I3's narrowing ("same bytes anywhere in the project; refusal outside") in the planned project-root ADR. Lens design-F5: README names the minimum agentic-mbse revision beside `installer/v1`, and the SC1 transcript records the revision installed.
- **m6.** Say whether `.sysml-codegen/install.json` is tracked or ignored in a target, consistent with agentic-mbse's `.agentic-mbse/`.
- **m7.** Say where the per-invocation gate table and the declaration live during a run (for example on `SequenceState`). The gate functions take `(request, env, state)` and index `GATES` directly today.
- **m8.** Use `choices=` for the `study` tool positional.
- **m9.** Rename the Key Bets (for example KB1–KB6) so they cannot be confused with the closed list's B1–B11.
- **m10.** Add the unestimated work to Appendix J: fusion-tea step-5 test edits, the M2 fix, the conformance amendment and README.

---

## Recommendations

1. Take premise conflict 5 to the orchestrator and fix M1 by letting each declared repo gate carry its `checked` text.
2. Choose M2's fix (recommended: rewrite fusion-tea's eight route-module imports at step 5) and add an integrate run on a real fusion package to the rehearsal.
3. Make gate 1b read teax only from `TEAX_SIMKIT_PATH` (M3).
4. Decide and record the conformance-pin amendment, with the study dispatch in its own CLI module (M4).
5. Tighten the root rule with a package-under-root check and a stated monorepo rule (S1). Rewrite the rehearsal's pass criterion around a pre-enumerated edit list, with identical environments and skip accounting (S2).
6. Apply S3–S8 and the minor items as text changes in the design.

---

## Resolutions

*None yet. This run was non-interactive. The orchestrator records resolutions here, or the design agent reads this review directly. M1 needs an orchestrator decision on a closed-list item before the design can apply it.*

---

**Overall:** Revise
**Next Steps:** The orchestrator decides premise conflict 5 (M1) and records it under Resolutions. Then re-run `/_my_design` (or resume the design-agent session) and point it at this review to incorporate M1–M4, S1–S8 and the minor items. The reviewer does not edit the design. A re-review is warranted only for M1–M4. S3–S8 are verifiable text changes.
