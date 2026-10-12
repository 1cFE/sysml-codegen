# Spec Review: Move the study layer to sysml-codegen (WRAP-SPLIT Item 3)

**Spec:** `.project/active/study-layer-to-codegen/spec.md` (at `21670e8`)
**Contract:** `claude-pack/commands/_my_spec.md`
**Review File:** `.project/active/study-layer-to-codegen/spec-review.md`
**Date:** 2026-10-12
**Run:** non-interactive, for the agentic-mbse orchestrator. Sources read: the spec, its brief, `product-lens.md`, the epic, the research audit, the run-study concept, fusion-tea's study layer at `b06585709`, `CONSUMER_SURFACE.md`, agentic-mbse's installer, Item 2's design and runbook, the repackaging check output, and this repo's `CLAUDE.md`, `.project/README.md`, ADR index, ADR-0007, P-001, P-003 and P-004.

---

## Reality Check

**Sound, with serious concerns.** The spec is about the right work item, and its Problem section is accurate. Its code-facing claims hold. I checked `get_commands_dir()` (`src/sysml_codegen/cli/__init__.py:59`), the wheel's package list (`pyproject.toml:41-42`), `manifest.py:57`, `:62-69`, `:88-95` and `:128-146`, `integrate.py:84`, `:128-135`, `:189-205`, `:343`, `:1006`, `:1098` and `:1506`, the fifteen condition slugs (`integrate.py:148-164`), `record-template.md:369`, and the runbook's annex lines (`:60`, `:94`, `:108`, `:129`). Evidence A is real work, and the `[NEED]` quotes are verbatim.

The problems are in three places:

- **The spec contradicts itself on semantics.** It says study semantics do not change, then requires changes to `integrate`'s fail-closed conditions, return shape and candidate rule. It also says schema versions stay fixed while leaving open identity options that the closed schemas forbid.
- **Two criteria cannot be audited without judgment.** These are SC7 (telling old documents from new) and SC5 (whose grep misses most of the consumer identifiers actually in the files).
- **The scope is roughly three times the epic's execute budget.** The spec has no estimate and no shed order.

None of these needs a rework. All of them need edits before design.

---

## Audit

### Lens 1 — Faithfulness

**L1-1 · Rewrite request:** The Problem section states the bar ("a working capability in a fresh target … can then run a study with nothing borrowed from fusion-tea", spec `:18`) without a grade. It comes from the orchestrator's brief ("What a good spec does here") and the epic's Critical Success Factor, which is agent-authored. The owner's own words are "ported and generalized … installed like everything else" (research `:18`). This bar is the premise that sizes SC4, so it needs a grade: `[AGENT] (orchestrator brief)` or `[INHERITED: epic CSF]`.

**L1-2 · Direct claim:** SC3 widens the epic's criterion and reverses the epic's own budget trade without saying so.

- The epic says "indicators, preflight, verify and integrate each complete **or** fail closed as documented" (epic Item 3 SC2).
- SC3 requires each tool to complete **and** to fail closed on a negative case. The `[INFERRED]` at spec `:107` then requires a fixture that drives "each tool's complete path".
- The epic's effort line paid for the installer work "at the expense of fixture breadth" (epic `:182`). The spec does the opposite: it grows the fixture to its largest possible size.

The widening may be right, but it is a scope decision. It needs to be visible and graded `[INFERRED]` with its reason, not folded into the fixture requirement.

**L1-3 · Direct claim:** SC4 cites "the shape of Item 2's dry run", but it is far larger than that precedent.

- Item 2's dry run supplied every operator answer in the brief and stopped after the first trail entry ("stop after writing `### T-001 start`", Item 2 design Appendix D3 step 4).
- SC4 runs a full study to a committed record. Its agent authors the annex, manifest and axis declaration from installed text, and a second agent writes the administrator synthesis.
- The administrator leg traces to the owner's concept SC-4 (cold pickup, run-study concept `:36`). That is a goal for the study capability, and fusion-tea has already exercised it. The port does not change the record contract, so this leg re-tests something this item does not touch.

SC4 should either be sized honestly against the budget or cut back toward its precedent (see L2-2).

**L1-4 · If-then tradeoff:** The `[INFERRED]` at spec `:85` turns every function fusion-tea imports into "a supported import surface for every target, not a compatibility shim". That is a long-lived public-API commitment, and nobody stated it. The epic asks only for "thin wrappers **or** remove them" (epic scope 5).

- **If** a function is genuinely target-facing, supporting it is right. `identity.build_sealed` is one: every target's route module needs it.
- **If** a function is a fusion-tea usage pattern, freezing it as public API for all targets is a widening. Examples: `verify.package_input_values` and `verify.derive_verdict` (called from fusion-tea model tests), and `rederived_census` (called from fusion-tea `build.py` files).

The spec should split the two groups: a supported target surface, and compatibility re-exports that exist for fusion-tea's adoption.

**L1-5 · Direct claim (orchestrator question 1, OQ10):** The spec is right to route the separate-distribution question to the owner, but wrong to wait until the design "wants it".

- **Why the owner decides.** A second distribution changes the install story the CSF names ("`run-study` and its tools from `sysml-codegen install-commands`"). It also cuts against one of the owner's stated reasons: sysml-codegen "owns the generated-package contracts the tools read", and a separately versioned tools package can drift from the generator it reads.
- **Why ask now.** The motivation, fusion-tea's 142-commit pin jump, is already known. The answer changes SC1, SC9 and OQ12. Left conditional on the design's preference, a design that finds it costly will never ask, and the owner never sees the main lever for separating adoption from the generator jump.

The spec should change "if the design wants it" to an owner question asked at spec stage. L2-1 offers a second lever with the same effect that needs no reinterpretation.

**L1-6 · Rewrite request:** SC5 bans package names, key prefixes and fusion-tea paths even inside labelled examples. That is stricter than the owner's bar ("fusion vocabulary is acceptable in examples", epic `:19`) and comes from the epic's own Item 3 criterion (epic `:212`, agent-authored). The stricter rule is legitimate. But SC5 is presented as the owner's bar, so a later agent could treat it as owner-grade. Label the extra strictness `[INHERITED: epic Item 3 SC4]`.

### Lens 2 — Problem & Approach

**L2-1 · If-then tradeoff:** The spec freezes one mechanism as a requirement and silently rejects an alternative the research named.

- **The frozen mechanism.** "A sysml-codegen package that imports without the `scripts.` convention and has console entry points" (spec `:82`) is inherited from epic scope 3, which is agent-authored.
- **The alternative.** The research audit offered two forms under the same owner decision: "the tools become `sysml-codegen study ...` **or a `scripts/` directory it installs**" (research Open Question 1(a)). In the second form, `install-commands` installs the tool files into the target as managed assets, under the same ownership rule as skills.

What the installed-files form removes:

- **The root split.** `Path(__file__).parents[2]` is the target root again, so Evidence A finding 2 goes away.
- **The identity problem.** `tools[].path = scripts/study/<tool>.py` stays true. `tool-source-digest/v1` stays comparable across the move for byte-equal files. SC7's hardest question and L3-2's schema conflict both go away.
- **The wrapper work.** fusion-tea's `scripts.study` imports keep working with no wrappers, so SC6 holds by construction and OQ11 closes.
- **The pin coupling.** fusion-tea could take the files from a newer sysml-codegen run in a separate tool environment without moving its generator pin. That separates adoption from the 142-commit jump, which is what OQ10 is reaching for, without reinterpreting the owner's decision.

What it costs:

- Python copies in every target.
- Tools and generator can drift apart in version until the next re-install.
- No console entry points.
- A fixed `scripts/study/` location in the target.

**If** the budget is the binding constraint (L2-2), this form is worth weighing before design starts. **If** the package form stays, the spec should state the outcome as the requirement ("the tools run in a fresh target from what `install-commands` delivers; fusion-tea's imports keep working") and record why the package form is preferred.

**L2-2 · Direct claim (orchestrator question 2):** The item is over budget by roughly a factor of three. The spec has no estimate and no shed order. Spec `:59` says scope that does not fit "is cut to a recorded deferral", but never says what is cut first, so the cut will happen silently during implementation.

My rough execute sizing (`[AGENT]`, for scale only) against the epic's 10h:

- package port, root split, identity, entry points: about 4h;
- `integrate` generalization (declared gates, environment, teax discovery, census home, backup prefix, launch form): about 4h;
- installer (wheel data, ownership manifest, both assistants, coexistence tests): about 4h;
- instruction text, policy template, ledger rows, fusion-tea branch text: about 5h;
- a neutral fixture that drives all four tools, including an `integrate` CANDIDATE (L3-6): about 5h;
- moved and new tests, plus typing for this repo's strict mypy (L3-12): about 4h;
- SC4's two-agent dry run: about 2h; the SC9 rehearsal and runbook: about 3h; docs: about 1h.

That totals about 32h, against 10h. Item 2 was smaller (instruction text, a one-step dry run) and still closed at about 2.4 days against the same 2-day ceiling (Item 2 design § Potential Risks).

The spec should carry an estimate and a ranked shed list, and mark each SC as **contract** (the product outcome) or **evidence** (proof gathered for this item). My recommended order, first cut first, with what each cut loses:

1. **SC4's administrator leg.** Loses a re-test of cold pickup, which this item does not change (L1-3).
2. **SC4's manifest authoring.** The fixture supplies the manifest, route and oracle. The agent still writes the annex and axis declaration, which tests the new annex guidance (spec `:100`). Loses proof that installed text alone teaches manifest writing.
3. **SC3's `integrate` CANDIDATE on the neutral fixture.** It becomes: `integrate` runs from the installed package and returns the documented blocker at a named gate. The CANDIDATE path is shown at fusion-tea adoption. Loses pre-merge proof that a non-fusion target reaches a candidate, and the fixture shrinks a lot (L3-6).
4. **SC9's suite and re-verification steps, if they cannot be separated from the generator jump.** These get marked "not rehearsed: needs the pin". Loses pre-merge semantic evidence from fusion-tea's fusion-specific tests. That is why L3-1's parity check should stay: it is the cheap substitute.

Never cut: SC1, SC2, SC5 with its read-through, SC6's existence check, SC7, the decoupling half of SC8, SC10, SC11, and the parity check.

**L2-3 · Direct claim (orchestrator question 5, repo fit):** The spec does not conflict with ADR-0007 or P-004, but it leaves two things unsaid.

- **ADR-0007.** Dependency direction holds: reusing agentic-mbse's `Installer` keeps sysml-codegen → agentic-mbse, and agentic-mbse gains no import. The census and indicator facts are facts about the generated output, which ADR-0007 places in sysml-codegen. ADR-0007 also records a lesson this item should cite: "A boundary move is byte-faithful or it is a behavior change to be reviewed as one" (`.project/adr/0007-agentic-mbse-owns-neutral-facts-codegen-owns-rendering.md`, § Why). It came from a "behavior-preserving" relocation in this repo that introduced two undocumented deviations. L3-1 applies it.
- **P-004.** The product-ledger entry at close (spec `:102`) is the right fix for P-004's "the product is those three steps". The spec could also cite P-001, which already gives "the study layer" a role (surfaces: studies; "the study layer owns exploration and decisions"). One more sentence is needed: the shipped tools keep adapter *disclosure* machinery because semantics are unchanged. That covers adapter sources in `identity.py:225`, the adapter roots in `read_coverage.py`, and `adapter_source_digest` in the snapshot. Disclosure is not injection, so it does not breach P-004. Saying so stops a later reader from flagging shipped adapter support as the smell.

### Lens 3 — Pipeline Risk

**L3-1 · Direct claim (contradiction; orchestrator question 4):** "Study semantics do not change" (spec `:68`) contradicts changes the spec itself requires. Each of these is a deliberate behavior change:

- **Gate 0 loses fail-closed conditions.** Dropping the four `STOP_PARSER_*_WHEEL` variables and `STOP_PARSER_TEAX_ROOT` (spec `:87`, `:89`) removes them from gate 0's environment sweep (`integrate.py:128-135`).
- **The return shape changes.** The `toolchain` block carries a `costingfe` key (`integrate.py:343`, emitted at `:696`). SC8 promises "the same return shape".
- **Undeclared gates break the candidate rule.** SC8 says an undeclared gate is "not declared, never a pass". But the return assembly raises, and the seam exits 2, whenever no blocker exists and any gate did not pass (`integrate.py:670-681`: "a CANDIDATE exists only when all ten gates passed"). An undeclared gate therefore either stops the sequence or breaks that rule, and the spec chooses neither.
- **teax discovery changes gate 1b and `read_coverage`.** Gate 1b runs `git rev-parse` on the `STOP_PARSER_TEAX_ROOT` checkout (`integrate.py:325-329`). `read_coverage` builds its permitted roots from the same variable (`read_coverage.py:94-101`). A plain-import option (OQ6) has no checkout to read.
- **The teax-missing message changes.** SC3's "names teax" changes `verify`'s failure, which today is a bare `import simkit` (`verify.py:484`).
- **Tool identity changes.** This is SC7's subject.

None of these is wrong. The spec needs to name them. It should:

- state the **closed list of deliberate behavior changes**, and say everything else moves byte-faithfully (ADR-0007's lesson);
- choose the undeclared-gate outcome. I recommend the existing `unasked` pattern (`integrate.py`, `unasked()`: a `BLOCKER`, mode `could_not_run`, condition `input-missing`). It keeps two return classes, fifteen slugs and the CANDIDATE rule. Its consequence should be stated plainly: a target must declare both repo-scope gates before `integrate` can ever return a CANDIDATE;
- enforce the closed list with a **parity criterion**. Run fusion-tea's original tool (the `.orchestrate-logs` copy) and the moved tool on identical inputs. Outputs must be equal except in the fields the list names.

The parity criterion matters because Evidence A compared outputs for `indicators` only. `preflight`, `verify` and `integrate` were only imported and asked for `--help` (`output.txt` §§ 2, 9). The moved test subset is about 12 of 55 tests, so most semantic pins stay in fusion-tea and only meet the moved code at adoption.

**L3-2 · Direct claim (contradiction):** SC7 fixes every `schema_version` string, but the schemas close the `tool` block. Each one sets `additionalProperties: false` and requires exactly `path` and `source_digest` (`indicators.v1.schema.json:23-37`, `preflight_results.v1.schema.json:19-31`, `verification_summary.v1.schema.json:30-37`). `preflight_results` and `verification_summary` also pin `source_digest.recipe` to `{"const": "tool-source-digest/v1"}`. So OQ4's options "add the distribution version" and "define a v2 recipe" need one of two things: edit schema bodies under an unchanged `v1` string, or bump the version, which SC7 forbids. SC7's "schema diff against `b06585709`" does not say whether the diff must be empty.

The spec must decide:

- **Schemas stay byte-identical.** Then tool identity can live only in the *values* of `tool.path` and `source_digest.files[].path`, and OQ4 shrinks to match.
- **Schemas may change.** Then state the rule, for example "additive only; every pre-move document still validates".

**L3-3 · Direct claim (checkability; orchestrator question 3):** SC7 cannot be audited without judgment.

- **"A reader can tell it apart from a pre-move document" is a reader's impression.** It is not a check.
- **"Names … which revision" has no defined meaning.** sysml-codegen's version is `0.1.1` (`pyproject.toml:7`) at every commit, and fusion-tea installs it by git revision, so a distribution version names no revision.

SC7 should name the field and the value rule that separates old from new. Then a test should apply that rule to a committed pre-move document, for example a fusion-tea `verification_summary.json` at `b06585709`, and to a post-move one.

**L3-4 · Direct claim (checkability; orchestrator question 3):** SC5's grep list does not cover the owner's bar. It misses most of the consumer identifiers actually present in the files being ported. Under the owner's bar, the vocabulary may stay in labelled examples. These are pointers, numbers and paths that must go:

- **Requirement and decision numbers SC5 does not catch.** `integrate.py` carries `ADR-009` (`:14`), `R-B1` (`:186`), `R-E4` (`:333`), `ADR-006` (`:416`) and `R-A3` (`:430`). The policy carries `WI-019`, `WI-022` and `WI-024` (§§ 2 and 4). SC5 catches only `MR-` followed by a digit. The owner named MR-7 as an example of a class, not as the class.
- **Internal pointers SC5 does not catch.** The record template has about twenty `(Item 3)` markers pointing at fusion-tea's run-study epic (`record-template.md:250-444`) and "gap G1, run-study-cold-pickup" (`:306`). Runbook step 7 cites `20260905-stored-energy-basis` and goal lesson `L-008` (`runbook.md:123-124`). `integrate.py:146` cites fusion-tea's operator guide.
- **An open name set.** "A fusion-tea package name or key prefix" has no list. fusion-tea's own `test_generic.py` pins only `stellarator_tea` and one prefix, while `CONSUMER_SURFACE.md` shows at least eight package directories.
- **An internal contradiction.** "LCOE appears only in labelled examples" cannot be decided by a grep, and it contradicts the sentence before it, "The test does not check vocabulary".
- **Two legs of the owner's bar that no grep can see.** These are "pointers … as authority" and "instructions that only make sense for one project". Evidence B's "barred in demo studies" and "criterion 5" are examples.

SC5 should:

- widen the identifier classes to the ones found above;
- enumerate the package names and prefixes as a closed list;
- add a per-line read-through record for what a grep cannot see. Item 4's per-file verdict is the precedent. Each row records a removed or changed line and its disposition (generalized in place, or moved to fusion-tea). Those rows are exactly SC10's ledger input, so the record does double duty.

**L3-5 · If-then tradeoff:** SC5 bans `scripts/study` in the record template. But OQ4 asks whether the template describes the pre-move form for readers of old records, and SC7 wants readers to tell old from new. A sentence such as "records written before the move name `scripts/study/<tool>.py`" would fail SC5. **If** old records need that explanation, allow the string in one labelled history note. **If** not, close that option in OQ4.

**L3-6 · If-then tradeoff (hidden premise; orchestrator question 4):** Nothing yet shows that a neutral fixture can drive `integrate` to completion, and the cost is unstated. Today the only CANDIDATE test uses fusion-tea's committed, already-integrated stellarator package (`tests/study/test_integrate_success.py:3-5`). The repackaging check ran `integrate` only with `--help`.

For `integrate` to return a CANDIDATE, the fixture needs all of the following:

- a git repository with an audited-work commit;
- a models root with exactly one tracked `*.snapshot.json` beside it (`tracked_snapshot()` in `integrate.py`);
- a committed package that regenerates byte-identically under this branch's generator, which is gate 2;
- a tracked census;
- both repo-scope gates declared and backed by real tests;
- a manifest, groups file and route module;
- a teax-executed store and an oracle;
- a teax checkout with a git revision for gate 1b;
- the syside license.

Gate 2 also couples the fixture byte-for-byte to every future change in generator output, as `tests/fixtures/baseline_outputs` already is.

**If** the spec wants that, it should say so and size it. **If** not, it should define "complete" for `integrate` as a documented blocker at a named gate. Either way, SC3 should define "complete" for each tool, for example "`preflight gates` exits 0 with all six gates passing", and say where the negative cases are "documented".

**L3-7 · Direct claim (checkability):** SC6 cannot check what it promises.

- **Imports do not show which functions are used.** fusion-tea consumers mostly import whole modules: `from scripts.study import common, manifest` appears across `CONSUMER_SURFACE.md`. A test that imports "each symbol by name" from that list proves only that modules exist.
- **Import tests cannot show behaviour.** Importing a name says nothing about what it does.
- **The root-dependent functions must change behaviour.** `manifest.repo_root`, `manifest.repo_relative_posix` and `common.tool_source_digest` change once the root splits (Evidence A finding 2).

SC6 should list the module *attributes* consumers use, found by grepping attribute access. It should check their existence and signatures mechanically. It should define behaviour for the root-dependent functions as "same result when the project root resolves to the consumer's repo". And it should say behaviour is checked by L3-1's parity check or by fusion-tea's suite in SC9.

**L3-8 · Direct claim (hidden premise, unverified):** Evidence A finding 2 counts `common.tool_source_digest` (`common.py:41`) as a "where the tool's own sources are" call. But it is a general function over "a named list of repo-relative source files". The record template also computes the oracle's `source_digest` with the same recipe over *target* files (`record-template.md:304-312`). If fusion-tea's package scripts call it for oracle files, it needs project-root semantics there, not tool-home semantics. Consumer function bodies are not in the snapshot, so this is unverified. To verify: grep fusion-tea for `tool_source_digest` outside `scripts/study/`. The design needs that answer before it splits the root.

**L3-9 · Direct claim (hidden premise):** If the design reuses agentic-mbse's `Installer` (`installation.py:91`), nothing in the dependency declaration guarantees it exists.

- sysml-codegen requires `agentic-mbse>=0.1.3,<0.2` (`pyproject.toml:24`).
- agentic-mbse reports version 0.1.3 at `main` (this worktree's venv).
- fusion-tea pins 0.1.3 at `adbef75` (fusion-tea `pyproject.toml`). That revision predates Item 2 (Item 2 runbook: "fusion's pin `adbef75` lacks `design-choices.md`") and likely predates Item 1's native installer.

So fusion-tea's adoption would depend on the Item 1 and Item 2 pin moves landing first. The epic says Item 3 has no such dependency (epic `:183`). OQ1 should also ask how the dependency guarantees the reused installer. The SC9 runbook should check fusion-tea's agentic-mbse pin.

**L3-10 · Direct claim (runbook content):** fusion-tea moves pins by hand-editing `uv.lock`, because `uv lock` fails on sysml-codegen's path source (Item 2 runbook, step 1.3). Item 2's runbook stops if the dependency's `pyproject.toml` changed. This item will almost certainly change sysml-codegen's `pyproject.toml`: console scripts, package data, and `jsonschema` in the `dev` extra. SC9's pin-move step must say what those changes do to the hand-edited lock and to `uv lock --check`.

**L3-11 · Direct claim (hidden cost):** This repo's mypy runs with `disallow_untyped_defs = true` (`pyproject.toml:56`). SC11 requires mypy to be clean on `src/`.

- The tools are about 4,900 lines written under fusion-tea's looser config.
- Several functions have unannotated parameters, for example `verify_store(..., loaded, identity_doc, evaluate, ...)` at `verify.py:484`.
- Every typing edit is a byte change to reviewed code, which is exactly what L3-1's parity check has to guard.

The spec should either count this work in the estimate or allow a recorded per-module mypy override.

**L3-12 · Direct claim (repo fit, conflicts with an `[OWNER]` rule; orchestrator question 5):** sysml-codegen's close rule is "Close = record, then delete. Git history is the archive. There is no `completed/` folder" (`.project/README.md:44-53`, `[OWNER, 2026-08-23]`). The SC9 adoption runbook and its evidence live in `.project/active/study-layer-to-codegen/`, and the owner uses the runbook *after* merge. If the item closes at merge, the runbook leaves HEAD before anyone runs it. Item 2's runbook survives only because agentic-mbse keeps `completed/`. The spec must say where the runbook lives after close. Three options: a durable doc in this repo, a home the orchestrator owns in agentic-mbse, or keeping the item open until adoption.

**L3-13 · Rewrite request (checkability, smaller items):**

- **SC4: "passes the record checks".** It names no checker. Today the step 14 and step 15 checks are fusion-tea tests, and OQ8 leaves open whether any shipped check enforces them. SC4 should name the check or tie it to OQ8's answer.
- **SC2: "(or prompts for it)".** It should say the noninteractive case preserves the file.
- **SC9: "every step it can".** It should list the steps expected to be rehearsable, so "could not" is distinguishable from "did not".
- **SC1: "no source checkout on the path".** agentic-mbse is not on a package index either. SC1 should say how it may be supplied.

**L3-14 · Direct claim (premise verified, with one gap):** `rederived_census` can get a home in sysml-codegen. `_by_entry_type` is a four-line grouping of `contracts/model_contract.json` `parameters[]` by `entry_type` into `qualified_name` sets (fusion-tea `tests/models/test_model_family_spines.py:178-182`). Both fields exist on `ContractParameter` (`src/sysml_codegen/contracts/models.py:30-34`). One gap: `integrate` imports the helper rather than reimplementing it, so that gate 4 and gate 5 cannot disagree (`integrate.py:1088-1096`). After the move, gate 4 uses the shipped helper while fusion-tea's spine test (gate 5) keeps its private copy. The adoption runbook should switch that test to import the shipped helper.

### Lens 4 — Hygiene

Nothing material beyond what Lens 3 covers.

### Lens 5 — Reader Comprehension

**L5-1 · Rewrite request:** The success criteria mix product outcomes with evidence-gathering activities. SC1, SC2, SC5 and SC7 describe what ships. SC4 and SC9 describe proof activities run by agents and the orchestrator. A reader cannot see which criteria define the product and which could shrink. Each SC should be tagged **contract** or **evidence**. The shed list in L2-2 then has a visible home.

---

## Engagement Summary

**Overall take:** The work item is right and the problem is captured accurately. The repackaging evidence is real, and the owner's shape for the capability is carried intact. But the spec promises "no semantic change" while requiring several, and it leaves two criteria (SC5, SC7) that an auditor cannot pass or fail mechanically. It also plans roughly three times the epic's budget with no order for what to drop.

**Here's what I need you to weigh in on:**

1. **[L3-1]** Accept a closed list of deliberate behavior changes plus a parity check, and pick the undeclared-gate outcome. My recommendation is the existing `unasked` blocker, which means a target must declare both repo gates before it can get a CANDIDATE.
2. **[L3-2, L3-3]** Decide whether the seven schemas stay byte-identical. That answer decides which OQ4 options survive and what SC7's mechanical discriminator can be.
3. **[L2-2, L1-2, L1-3, L5-1]** Accept an estimate and the ranked shed list: the administrator leg first, then manifest authoring, then the `integrate` CANDIDATE on the fixture, then the rehearsal's suite steps.
4. **[L2-1]** Before design, weigh installing the tool files into the target instead of shipping an importable package. It removes the root split, the identity problem, the wrappers, and the pin coupling. It costs Python copies in every target and version drift between re-installs.
5. **[L1-5]** Question for the owner, through the orchestrator, now rather than at design: does "ships from sysml-codegen" allow a second, separately installable distribution built from this repo, so that fusion-tea can adopt the tools without moving its generator pin?
6. **[L3-4]** Widen SC5 to the identifier classes actually present (ADR-, WI-, R-, "(Item 3)", record ids, closed package-name list) and add a read-through record that doubles as SC10's ledger input.
7. **[L3-12]** Name where the fusion-tea adoption runbook lives after this repo's close-and-delete step.

---

## Must-fix and should-fix

**Must-fix**, for the orchestrator to feed back to the spec author:

1. **[L3-1]** List the deliberate behavior changes as a closed set. Decide the undeclared-gate outcome against the CANDIDATE rule (`integrate.py:670-681`). Add a parity criterion: original and moved tools on identical inputs, differing only in the listed fields. Cite ADR-0007's byte-faithful lesson.
2. **[L3-2]** State whether schema files stay byte-identical or may change under a stated additive rule. Prune OQ4 to the options that survive.
3. **[L3-3]** Make SC7 mechanical: name the discriminating field and value rule, define "revision", and test both against a committed pre-move document.
4. **[L3-4]** Fix SC5:
   - add the missing identifier classes;
   - give a closed package-name and prefix list;
   - add a read-through record for what a grep cannot see;
   - resolve the "LCOE only in labelled examples" contradiction.
5. **[L2-2, L1-2, L1-3, L5-1]** Add an effort estimate and a ranked shed list, and tag each SC as contract or evidence. Grade SC3's widening and SC4's size against their sources: epic Item 3 SC2 for SC3, and Item 2's D3 dry run for SC4.
6. **[L3-12]** Say where the SC9 runbook and its evidence live after close, given the `[OWNER]` close-and-delete rule.

**Should-fix:**

- **[L1-1]** Grade the Problem section's "working capability" bar.
- **[L1-4]** Split the import surface into a supported target API and fusion-tea compatibility re-exports.
- **[L1-5]** Turn OQ10 into an owner question asked now.
- **[L1-6]** Label SC5's example strictness as inherited from the epic.
- **[L2-1]** State the tools requirement as an outcome, or record why the package form beats installed files.
- **[L2-3]** Cite P-001. Say that adapter disclosure machinery stays and is not P-004's smell.
- **[L3-5]** Reconcile SC5's `scripts/study` ban with OQ4's history-note option.
- **[L3-6]** Define "complete" per tool, and size or shrink the `integrate` fixture.
- **[L3-7]** Make SC6 enumerate attributes and define behaviour for the root-dependent functions.
- **[L3-8]** Verify how fusion-tea uses `common.tool_source_digest` before the root split is designed.
- **[L3-9]** Add the installer-reuse dependency question to OQ1, and a fusion-tea agentic-mbse pin check to SC9.
- **[L3-10]** Make the SC9 pin-move step handle sysml-codegen `pyproject.toml` changes under the hand-edited lock.
- **[L3-11]** Count strict-mypy typing in the estimate, or allow a recorded override.
- **[L3-13]** Tighten SC1, SC2, SC4 and SC9 wording.
- **[L3-14]** Add a runbook step that switches fusion-tea's spine test to the shipped census helper.

## The orchestrator's five questions, answered

1. **Owner intent.** Every `[NEED]` is owner-stated and every quote is verbatim. Three items drift:
   - the ungraded Problem bar (L1-1);
   - SC3 and SC4 grown beyond their sources (L1-2, L1-3);
   - the import surface promoted to a public API (L1-4).

   The spec is right to route OQ10 to the owner, but should ask now (L1-5).
2. **Scope against budget.** The item is about three times the execute budget, with no shed order (L2-2). Load-bearing criteria: SC1, SC2, SC5, SC6 (existence), SC7, SC8 (decoupling), SC10, SC11. Evidence that can shrink, in order: SC4's administrator leg, SC4's manifest authoring, SC3's `integrate` CANDIDATE, then SC9's suite steps. L2-1 would shrink more than all of these.
3. **Checkability.** SC7 and SC5 fail as written (L3-3, L3-4). SC3, SC4, SC6 and SC9 each have a judgment word to replace (L3-6, L3-7, L3-13).
4. **Hidden premises.** "Identical semantics" is contradicted by the spec's own requirements and verified only for `indicators` (L3-1). The census home is verified as trivial, with one runbook gap (L3-14). The `integrate` fixture premise is unverified and expensive (L3-6). Also unverified or unstated:
   - how `common.tool_source_digest` is really used (L3-8);
   - whether a reused installer is guaranteed by the dependency (L3-9);
   - how lock changes affect the pin move (L3-10);
   - the strict-mypy typing cost (L3-11).
5. **Repo fit.** There is no conflict with ADR-0007's dependency direction or P-004, though both deserve a sentence (L2-3). There is one real conflict, with the `[OWNER]` close-and-delete rule, over where the adoption runbook lives (L3-12).

---

## Resolutions

None yet. This review ran non-interactively. The orchestrator relays the owner's answer to L1-5 and records resolutions here by finding ID.

---

**Verdict:** Revise
**Next Steps:** The orchestrator feeds the must-fix list to the spec author and puts L1-5 to the owner. Once resolutions are recorded, re-run `/_my_spec` (or return to the spec-agent session) and point it at this review. The reviewer does not edit the spec.
