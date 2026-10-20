# Design Review: Read-only readiness check, live half (EXEC-SUBSET-CONTRACT Item 2b)

**Design:** `.project/active/subset-profile-screen/design.md` (revision 1, at `b4caccc4`)
**Spec:** `.project/active/subset-profile-screen/spec.md` (revision 3)
**Review File:** `.project/active/subset-profile-screen/design-review.md`
**Date:** 2026-10-20
**Product lens:** `design_review` block appended to `product-lens.md` (gate BLOCKED on design_review-F1; smell 7 fired)

---

## The Point

A modeler needs one command, `check`, that says before anything is written whether `generate` will build their model, every reason it won't, and every finding the shared subset screen has, marked "not assessed" where the screen could not decide. `generate` must print the same findings in the same form. The answer is only worth having if it is the generator's own answer: the generator's route alone decides refused or builds, and the screen only reports (owner-ratified, `briefs/align.md` Q1). Changes to what the generator accepts or refuses (RG-1), String policy (RG-2), and merges and ADR filing (RG-3) stay with the owner. The product never makes a bad model generate (`.project/product/0003`). A refused `generate` must leave its destination untouched, which today fails for `PARAM_FIELD_COLLISION`.

## Fundamental Assessment

**Sound approach, one blocking owner decision.** Verdict: **Revise**, with the ledger gate BLOCKED until the owner rules on C1.

The core structure is right, and I would not change it:

- Cutting `generate` at its first write into a read-only `prepare` and a writing `emit_package` is the simplest way to make "`check` is the generator minus the writes" true by construction. A skip-writes flag would rest on every writer honouring it.
- The screen's result flows only into the report, never into `prepare`, `emit_package` or the exit code. I traced every arrow in the design and found no path where it does, apart from the gaps in M3 and M4 below, which are specification holes, not design choices.
- Hoisting `PARAM_FIELD_COLLISION` to the end of `prepare` follows the repo's own precedent (`_preflight_registry_class_names`, `cli/__init__.py:279-298`) and refuses the same models.

The problem is the readiness rule (D8). It makes `check` print READY and exit 0 on a model with a known silent String loss that the owner has not yet ruled on, and the design's handoff tells the owner the opposite (C1). The product lens fired smell 7 on this: D8 decides, through the definition of READY, a question the owner reserved. The review process says a fired smell means Rework. I am recording Revise instead, openly: the flaw is confined to one decision, the fix is an owner ruling plus a small rule change, and nothing else in the design depends on which way it goes. If the owner wants the rule decided differently, only D8, its tests and the readiness line change.

---

## Answers to the five questions asked

**1. The second SysIDE load (D2).** Not justified as written. The design argues the wrong risk and overstates the cost of the alternative. See M1. My recommendation is to share one load per command.

- The anonymous-element IDs the spike found are not a factor in 2b. The report joins a finding to a refusal by code (D7), not by element. The stored-answer comparison goes through 2a's `screen_answer` (`tests/conformance/subset_profile/test_screen_half.py:27`), which does not compare element IDs.
- The real risk the design does not state: the live route reads the user's files in place. `build_exact_pipeline_context` calls `elaborate_model_paths` on the given paths (`orchestration/exact_pipeline_context.py:288-298`, `elaborated_pipeline.py:159-168`); only the capture route stages private copies (`elaborated_pipeline.py:210-215`). Two loads at two times can read two different files. In `generate`, D16 puts the second load after the whole emit, so on `catf_mfe` the gap is several seconds. An editor save in that window gives a report about a file the package was not built from.
- The cost of sharing is smaller than D2 says. The split D2 says it would need already exists: loading is `elaborated_pipeline.py:159-173` and elaboration is `elaborate_loaded_extractor` (`:267`). Sharing means moving those lines into a load function, adding a context builder that takes a loaded extractor, and pointing the 2a elaboration spy at the new seam, which D11 rewrites anyway.
- D2's coupling worry runs one way only. In both commands the screen runs after `prepare`, so nothing the screen does to SysIDE state can reach the generator. The other direction (elaboration changing what the screen sees) is exactly what Success Criterion 4 tests on the corpus. The epic's "conformance becomes circular" risk (agentic-mbse epic, Risks table) is met by the 2a harness's own `screen_half` load, which is unaffected.

**2. Readiness for omitted and excluded findings.** This needs an owner decision. See C1.

- What L6 shipped: under the `generated` target, `excluded` and `omitted` are WARNING, not ERROR, and only refusals exit 1 (agentic-mbse `validation/execution_target.py:176-193`; L6 `spec.md:40, 82, 101`). The owner ratified that: "Under `generated`, exclusions and omissions are warnings, each with its own reason. String policy stays with Item 2" (L6 `spec.md:148`, [AGENT] ratified 2026-10-18). L6 also bans any readiness wording and says only `check` could make that claim (`spec.md:158`).
- So D8 matches L6 on how loud an omission is (exit 0, shown as a warning) and is stricter on `unconfirmed` (not ready, where L6 warns). That part is consistent.
- What L6 did not ratify is the word READY. D8 turns "a warning in a tool that makes no readiness claim" into "READY, exit 0". The epic still lists "blocking policy for exclusions/omissions" as open (agentic-mbse epic `:318`) and says that policy "must be stated, not inferred" (`:203`). D8 infers it from L6.
- On RG-2: yes, it steps on it, and the design's claim that it doesn't is false. Details in C1.

**3. D4's changed first failure.** Confirmed: not an accept/refuse change.

- The change touches only models refused by the constraint plan build, the coverage preflight, or `PARAM_FIELD_COLLISION`. Construction refusals and the six earlier preflights already run before the link check today (`cli/__init__.py:1305-1327`).
- For those models with a symlinked destination: today `PACKAGE_WRITE`, exit 1, nothing written (the check at `:1327` precedes the clear at `:1346`). After 2b: the model refusal, exit 1, nothing written. With `--overwrite` the link check still precedes the clear.
- A model that builds with a symlinked destination still gets `PACKAGE_WRITE` after `prepare`. No model moves between refused and builds. `PACKAGE_WRITE` carries no code (`cli/refusal.py:46`), and the spec counts it as an environment failure (`spec.md:51`).
- Keep it parked for the owner as the design does: the Align non-objection covered moving refusals earlier, not reordering two failures. M4 covers what the design still has to specify about the logged records in this case.

**4. Moving the writers to `cli/emit.py`.** The factoring is right; keep D1. The churn is smaller than the design says.

- Most references only import a moved name (about a dozen test files, some with multi-line imports such as `tests/conformance/test_constraint_generation_integration.py:28-37`) and need a new import path. I found only 3 that monkeypatch one (`tests/unit/test_cli_generation.py:466`, `:507`; `tests/conformance/test_public_package_oracle.py:55`). Only those would go silently dead behind a re-export. I did not produce an exact count of import lines.
- The smaller cut is to move only `prepare` and the preflights out and leave the writers in `cli/__init__.py` as `emit_package`. It saves the mechanical import edits. It costs a 1,400-line file that still mixes CLI parsing and package writing, and it gives up nothing in boundary strength, because `run_check` sits in `cli/__init__.py` beside `run_codegen` either way. So "`run_check` never calls `emit_package`" needs a call-level test in both versions (Invariant 1 already has one).
- The import boundary's real value is that `prepare.py`, `readiness.py` and `subset_screen.py` cannot reach writing code. That holds in either cut. I'd still take D1: the file split matches the concepts, and the import edits are mechanical.
- One gap: `_get_template_env` is used by both halves (the plan build in `prepare`, the writers in `emit`). The design should say where it lives (m3).

**5. Exit codes and the `check` CLI.** Consistent with the repo.

- Every subcommand returns 0 or 1 (`cli/__init__.py:851-1039`). The study tools use 2 for a rejected request or a missing project root (`study/roots.py:99`, `study/integrate.py:404, 716`), matching argparse. Skipping 2 and using 3 for "builds, not ready" fits that.
- Flags mirror `generate` (`--models`/`--from-snapshot` as a required exclusive group, `--package-name`, `--verbose`). Leaving out the three write-mode flags is right.
- Two notes. Exit 1 for "agentic-mbse is not installed" mixes an environment problem with "refused"; `generate` does the same, so it is consistent, but the report line should say which. And `check --output` on a symlinked destination exits 3 while `generate` on the same inputs exits 1 (M4).

---

## Dimensional Review

### 1. Spec Compliance
**Assessment:** Concerns

- Criteria 1–12 each have a design element and a validation line. The spec's open questions (late refusal, CLI, join, omissions, lanes) are each answered.
- The spec's "Ready" definition (`spec.md:48`) is satisfied, but the spec left "whether an omission or exclusion finding alone makes a model not ready" open. The design closed it as an agent decision without returning it to the owner, and its stated reason ("so String policy stays with RG-2") is wrong for the one known String loss (C1). This is the capture-fidelity issue: an open, owner-reserved question was settled by agent inference.
- Criterion 10 ("same form") holds only when `check` is given `--output`, because `generate` always checks the destination and `check` only with `--output`. Validation 10 should say so (M4).

### 2. Pattern Consistency
**Assessment:** Concerns (minor)

- The hoist follows `_preflight_registry_class_names`. Refusal records keep today's text and `extra`. Exit codes fit the repo (question 5).
- D14 builds a new name-based call-closure helper. `tests/helpers/subset_profile/site_scan.py` already scans every raise site with its enclosing function (`_FunctionScope`, `Site`). D14 should extend that rather than add a second scanner (m1).

### 3. Abstraction Quality
**Assessment:** Concerns

- `Preparation` (`Prepared | Refused`), `emit_package`, `assess_screen` and one `ReadinessReport` each earn their place. A reader gets the model from the Core Concept section alone.
- The "screen cannot change the outcome" guarantee has two holes the design does not close: code that handles screen output outside `assess_screen`'s catch-all (M3), and destination records whose meaning differs between the two commands (M4).

### 4. Duplication Avoidance
**Assessment:** Pass

- D9 moving the agreement rule into `src/` with the test helper calling it removes the one real duplication risk. D5 gives one renderer to both commands.
- The writers keep re-running `_preflight_constraint_names` (`cli/__init__.py:483, 534, 588, …`) and D3 keeps a dead re-check of the field collision. That is pre-existing, and D14 accounts for it openly. Dropping the re-checks would shrink D14's exemption table to nothing; see m1.

### 5. Data Structure Clarity
**Assessment:** Concerns (minor)

- `Prepared` is built with a package name, and `emit_package(prepared, config)` also gets one in `config`. Two sources for one value; take it from `Prepared` or assert they agree (m2).
- `run_check(request)`: the request type is not defined (m7).
- `DestinationCheck` is described in a comment only (`NOT_CHECKED | CLEAN | problem text`). Fine for a design, but the plan should type it.

### 6. Route Safety
**Assessment:** Concerns

- Every route is explicit: `check` and `generate`, each from `--models` or `--from-snapshot`, and the snapshot seam is one branch in `assess_screen`.
- M3: Invariant 2 can break through `readiness_report` or `log_report` raising after the seal.
- M4: what `generate` and `check` log when a model refusal and a destination problem coincide, and what `check` logs for a destination problem on a model that builds, are unspecified, and the 2a harness requires exactly one logged refusal per refused run (`tests/helpers/subset_profile/observe.py:238-241`).

### 7. Bets & Decisions Integrity
**Assessment:** Concerns

- B1 is aimed at the wrong risk. Anonymous IDs don't matter in 2b (question 1). The risk that matters is unstated (hidden bet below).
- **Hidden bet: the source files do not change between the two loads.** Nothing detects it, and D16 widens the window in `generate` (M1).
- **Hidden bet: everything that handles screen output after `assess_screen` returns is total.** The agreement rule as it exists today raises on a refused finding whose reason maps to `NO_REFUSAL` (`tests/helpers/subset_profile/cases.py:448-453`). M3.
- **Hidden bet in D8: the screen reports every String loss.** It doesn't: the library-default String loss has no finding (C1).
- B3 (accepted extra time) is honest, and sharing the load would shrink it to fact extraction only.
- Decisions D1–D16 each name the alternative and why it lost. D2's rejection reasons are overstated (question 1).

### 8. Reader Comprehension
**Assessment:** Pass

The Overview and Core Concept give the mental model in a few sentences before the mechanism. The decisions are long but each leads with its choice. The output sketch helps.

---

## Issues by Severity

### Critical (must fix before planning)

- **C1. D8 makes READY reachable on a known silent String loss the owner has not ruled on, and the handoff tells the owner it doesn't.** — Spec Compliance, Bets
  - The case `candidate-es-010-refusal__string_library_default__unbound_input`: a calc def String default ("liter") on an input the usage leaves unbound. The generator builds it as a `str` entry point with a null default, so the model's value appears nowhere in the package. The 2a RG-2 note calls it the only silent String loss (`c381fb00:.project/active/subset-profile-conformance/rg2-string-policy.md`). The stored answer records screen verdict `clear`, no findings, and loss disposition `rg2_pending` (`tests/expectations/subset_profile/cases/candidate-es-010-refusal__string_library_default__unbound_input.json`).
  - Under D8 this model is READY with "0 omitted, 0 excluded" and exits 0. That puts "keep the loss" in place before the owner chooses. The handoff line "D8 leaves omitted String values out of the readiness verdict, so String policy stays with RG-2" (`design.md:219`) is false for this case.
  - D8 also answers the epic's open owner decision 2 (blocking policy for exclusions and omissions) for `check` without saying so. It is consistent with the L6 severity the owner ratified, but READY with exit 0 is a stronger claim than L6 makes.
  - Fix: correct the handoff and put the decision to the owner (question below). Cite L6 `spec.md:148` in D8 as the authority it actually extends.

### Major (should fix before planning)

- **M1. The second load leaves an undetected window in which the screen and the generator read different files; D2's case against sharing is overstated.** — Bets, Abstraction
  - Recommend: load once per command and hand the loaded model to both `prepare` and `assess_screen`, using the existing split at `elaborate_loaded_extractor`. This removes B1, the file-change window and the extra load time. The screen still runs after `prepare`, so it cannot affect the generator. Criterion 4 detects any effect elaboration has on what the screen sees. Expect about half a day, mostly the context builder and moving the elaboration spy.
  - If the design keeps two loads, it must at least digest the source files before each load and mark the screen not assessed ("sources changed during the run") when they differ, and restate B1 around file stability, not anonymous IDs.
- **M2. `assess_screen` does not say what happens when the model loads with errors.** — Route Safety
  - `SysideAdapter.load_model` returns a model even when it has errors. The generator refuses on errors (`extraction/extractor.py:73-75`) and 2a's screen half does too (`observe.py:375-377`). Without the same check, a model refused for parse errors gets screen findings from a broken parse and a disagreement computed from them. Add "not assessed: the model has parse errors" and test it on both commands. With a shared load (M1) this becomes "the screen runs only on a load without errors".
- **M3. Invariant 2 can break after the seal: code that handles screen output outside `assess_screen`'s catch-all is not required to be total.** — Route Safety, Bets
  - `readiness.py` may not import the adapter (D10), so mapping a finding to a code (`REASON_MAPPING`, `code_for`) has to happen inside `assess_screen`. Today's rule raises on a refused finding whose reason maps to `NO_REFUSAL` (`cases.py:448-453`). If that raise, or any bug in `readiness_report` or `log_report`, happens after `emit_package` in `generate`, a package that built and sealed exits non-zero: a failure keyed on the screen.
  - Fix: state that `ScreenAssessed` carries every finding already mapped and rendered, with mapping failures turned into "not assessed" inside the catch-all, and that `readiness_report` and `log_report` take only already-checked data. Extend the D16 test to patch `readiness_report` to raise as well, or give `generate`'s post-seal report its own guard that logs and keeps exit 0.
- **M4. The destination check's logged records are underspecified.** — Route Safety, Spec Compliance
  - `generate`, refused model, symlinked destination: does it still run `inspect_destination`? If it does and logs its `PACKAGE_WRITE` record, the run has two refusal records, and the 2a harness requires exactly one. Invariant 5 implies it should not run; say so.
  - `check --output`, model builds, symlinked destination: D4 says the problem renders as today's line with its `PACKAGE_WRITE` refusal payload, but `check` exits 3 ("builds, not ready"). A log reader would see a refusal record on a run that is not refused. Recommend the same line text in both commands, with the `refusal` extra only in `generate`, where it stops the run, and a readiness line in `check` that says `generate` would stop at the destination.
  - Validation 10 should run `check` with `--output` so the two commands print the same sections.

### Minor (consider)

- **m1.** D14: build on `site_scan.py`'s enclosing-function scan instead of a new helper. Consider dropping the dead re-checks in the writers (D3's kept call and the repeated `_preflight_constraint_names`), which would leave `POST_WRITE_RECHECKS` empty and the test simpler. Keeping them is defensible; the design should say why if it keeps them.
- **m2.** Take the package name from `Prepared` in `emit_package`, or assert it equals `config.package_name`.
- **m3.** Say where `_get_template_env` lives, since both halves use it and `test_public_package_oracle.py:55` patches it.
- **m4.** Correct the churn description in Architecture: most references are imports that need a new path; only 3 are monkeypatches that a re-export would silently break.
- **m5.** Invariant 2 should name the native-crash residual that Invariant 3 accepts (a crash after the seal exits non-zero on a sealed package).
- **m6.** The report line for "agentic-mbse is not installed" should say it is an environment problem, even though the exit code stays 1 like `generate`.
- **m7.** Define `run_check`'s request type.

---

## Recommendations

1. Take C1 to the owner with the corrected premise, and rewrite D8 and the handoff to match the answer.
2. Share one SysIDE load per command (M1), which also settles M2.
3. Make everything after `assess_screen` total, and say where finding-to-code mapping happens (M3).
4. Specify the destination records for both commands and the coincidence case (M4).
5. Fold in the minor points while revising.

---

## Owner decision needed (C1)

Where things stand: the design is sound apart from the readiness rule. `check` will print READY and exit 0 for a model the generator builds when the screen is clear and nothing is a candidate refusal. One known String loss passes that test silently: a calc def String default on an unbound input generates as a `str` entry point with a null default, and the screen has no rule that reports it. RG-2 (String policy) is yours and still open.

What the question decides: whether `check` may say READY while a loss you have not ruled on is in the package, and more generally whether omitted and excluded findings block READY (the epic's open decision 2). L6 already has your ratification that they are warnings, not errors, under the `generated` target; READY with exit 0 goes one step further.

Options:

- **(a) Decide RG-2 now.** The 2a note `rg2-string-policy.md` lays out the options and a recommendation. Whatever you choose, `check` then follows the records with no special case. Cost: a decision now, and a rule change in agentic-mbse if the choice is to report or refuse the loss (which needs a gate rerun).
- **(b) Withhold READY on this loss until RG-2 is decided.** `check` reports "builds, not ready" when the prepared graph has a library-default `str` entry point with no default. That is a fact from the generator's own route, not the screen, and it changes nothing `generate` does. Cost: a narrow special case to remove once RG-2 is decided.
- **(c) Accept READY with this loss as a stated limit,** written into the readiness line and the D8 ADR candidate. Cost: READY with exit 0 on a package missing a model value.

My recommendation is (b) if RG-2 cannot be decided before 2b ships, because a READY with exit 0 is what a script gates on and it never reads the counts. (a) is better if you are ready to decide RG-2. Separately, please confirm that omitted and excluded findings the screen does report should leave READY intact (shown with counts), as D8 proposes, or say if they should make the model "not ready" instead.

---

## Resolutions

Design agent, 2026-10-20, design revision 2, under the orchestrator's rulings:

- **C1:** open, with the owner (orchestrator asking now). D8 left as is and marked PARKED; the rule lives only in `readiness(report)`, which takes the whole report, so options (a)–(c) change only that function, its tests and the readiness line. The false handoff line about String values is removed.
- **M1:** applied (orchestrator ruling). One SysIDE load per command, shared by `prepare` and `assess_screen` through the existing seam (`elaborated_pipeline.py:159-173`, `:267`). D2, B1, B3 rewritten.
- **M2:** applied. A load with errors gives "screen not assessed: the model has parse errors"; tested on both commands.
- **M3:** applied (orchestrator ruling). New D17: mapping inside `assess_screen`'s catch-all, total report functions with a combination test, and a post-seal guard in `generate`.
- **M4:** applied (orchestrator ruling). D4 pins each command's records: no destination check on a refused model; `check` never logs a `refusal` extra on a run that builds. Validation 10 runs `check --output`.
- **Question 3:** recorded in D4 as a stated behaviour change, not RG-1, no longer parked.
- **m1:** applied in the stronger form: the writers' re-checks are dropped and the exemption table is gone; D14 extends `site_scan.py`. **m2–m7:** applied. No minor point conflicted with the rulings.

Design agent, 2026-10-20, Round 2 points, under the orchestrator's rulings (no third review):

- **R2-1:** applied. The constraint-name validator stays in `generate_pipeline_yaml`, `generate_registry` and `build_model_contract` (pinned by `test_module_kind_faildloud.py:277-294`). D14 allows site 338 by name with that reason and checks that `prepare`'s constraint-names step calls the same function. Only the unpinned re-checks are dropped: the nine `_preflight_constraint_names` calls and the schema writer's parameter-field check (D3 says why: nothing pins it). Invariant 4 and the de-risk line updated. Your suggested `model_dump()` guard around `emit_package` is added.
- **R2-2:** applied as new D18. `emit_package` holds today's post-write handler blocks and logs the same single record per failure, byte-identical; `PreparationStep.EMIT` names it; the screen report still runs after a failed emit, under D17's guard. A test patches a writer to raise three kinds of exception and checks each record.
- **R2-3:** applied. `ReadinessVerdict` carries reason strings already worded; `log_report` prints them without branching, so option (b) changes only `readiness` and its tests.
- **R2-4:** applied. `_generate_package_from_graph` is removed; its four test files move to `prepare_graph` and assert `Refused`; tests do not build a `Prepared` by hand. `test_public_diagnostic_totality.py:471-473` is in the churn list.

---

**Overall:** Revise. Ledger gate BLOCKED on C1 until the owner rules.
**Next Steps:** Get the owner's answer on C1. Record it under Resolutions, then re-run `/_my_design` (or return to the design-agent session) and point it at this review to incorporate C1 and M1–M4. The reviewer does not edit the design.

---

## Round 2 (2026-10-20, design revision 2 at `2fa80bca`)

**Verdict: Revise, narrowly.** Every round-1 must-fix and should-fix point is resolved, and D8 is isolated as claimed, with one condition (R2-3). Two new gaps would make the plan build the wrong thing: D14's reachability test will not come back empty as the design predicts (R2-1), and no step is named to log a failure raised by a writer (R2-2). Both are small, checkable edits. A third review round is not needed: the orchestrator can confirm the edits against the points below. The ledger gate stays BLOCKED on C1 (the readiness rule) until the owner rules.

Scope of this round: the round-1 points, D8's isolation, and m1 against RG-1 (the owner's rule that only the owner changes what the generator accepts or refuses). D8's substance was not reviewed. The product lens was not re-run: The Point is unchanged, and a round-2 disposition line is added to `product-lens.md`.

### Round-1 points

- **C1 (readiness rule):** open with the owner, as intended. D8 is marked PARKED, cites L6 `spec.md:148`, and the false handoff line about String values is gone (`design.md:98`, `:242`).
- **M1 (one load):** resolved. D2 shares one load through the existing seam (`elaborated_pipeline.py:159-173`, `:267`), and B1 now names the real risk with a fallback.
- **M2 (parse errors):** resolved. D2 and the Validation line "Parse errors" both state and test it.
- **M3 (nothing after the seal raises):** resolved by D17. Mapping and rendering happen inside `assess_screen`'s catch-all, the report functions get a combination test, and `generate` has a post-seal guard.
- **M4 (destination records):** resolved. D4 pins both commands' records, Invariant 5 holds the one-record rule, and Validation 10 runs `check --output`.
- **Question 3 (D4's reorder):** recorded as a stated behaviour change with its own test (`design.md:94`, Invariant 5).
- **m2, m3, m5, m6, m7:** resolved (`design.md:126`, D1, Invariant 2, D6, D6).
- **m4 (churn list):** resolved, with two omissions, both in R2-4.
- **m1 (drop the writers' re-checks):** RG-1 holds (below), but D14's prediction does not (R2-1).

### m1 and RG-1: dropping the re-checks cannot change what `generate` accepts or refuses

The reasoning, checked against the code:

- **One production path reaches the writers.** Today the writers are called only from `_generate_package_from_graph` (`cli/__init__.py:1284`), and that is called only from `run_codegen` (`:1263`). No other module in `src/` imports a writer from `cli`. After 2b, D16 calls `emit_package` only from `run_codegen`, and only on a `Prepared`.
- **The snapshot route is the same path.** `run_codegen` differs between sources only in which context builder it calls (`:1210-1214`). Everything after that is shared, so `prepare` runs every step for `--from-snapshot` too.
- **The writers would re-check the same, unchanged graph.** `run_codegen` reads the graph once (`:1217`), and `Prepared` carries that one object, not the context (which re-projects on every read). `ComputationGraph` is not frozen, but I found no writer that changes it: the only rebuild in `generation/` is a `model_copy` of the catalog (`generation/modules.py:166`), which copies. The checks are deterministic over the graph. So a check that passed in `prepare` cannot fail later in a writer.
- **Moving the field check is the same.** `_refuse_colliding_field_names` reads only the group's entry points (`generation/entry_point.py:21-45`), which the writers do not change.

What I did not prove: that no writer mutates the graph. I checked by search, not by running anything. The byte-identity check (Invariant 6) would not catch a mutation that only matters for a refused model. A cheap guard: have the plan assert in one test that the graph's `model_dump()` is equal before and after `emit_package` on a corpus case.

One weak spot, for tests only: `Prepared` is a plain frozen dataclass, so a test can build one by hand and hand `emit_package` a graph `prepare` never checked. That cannot affect `generate`, but it would let a test pass on a graph `generate` refuses. The four test files that call `_generate_package_from_graph` today (see R2-4) are the ones at risk.

### New points

- **R2-1 (Major). D14's reachability test will not be empty after the nine re-checks are dropped.** The constraint-name validator `validate_constraint_graph_or_raise` (site account row 338, `public_capability`) is also called inside three functions the writers use. These calls are not among the nine the design drops: `generate_pipeline_yaml` (`generation/pipeline.py:56`), `generate_registry` (`generation/registry.py:266`) and `build_model_contract` (`contracts/model_contract.py:37`, called by `_seal_package`). An existing test requires each of these three to refuse a bad graph on its own: `test_graph_renderers_reject_constraint_module_without_catalog` (`tests/conformance/test_module_kind_faildloud.py:277-294`). So the de-risk step ("it should come back empty") fails on day one, and the plan has to choose between deleting a pinned behaviour and bringing back an exemption list.
  - Fix: decide it in the design. I recommend keeping the three guards and the test, since they are those functions' own contract. D14 then allows site 338 by name, with the reason that `prepare`'s constraint-names step runs the same function on `Prepared.graph`. A test should check that the allowed site's function is called by a named `prepare` step. That is a one-row list, not revision 1's table. The other option is to drop the three guards and delete the test, which keeps D14 empty. Either is RG-1-safe, for the reasons above.
  - Apply the same rule to the parameter-field check, so the design treats both alike. If renderer guards stay, say why the schema writer's guard (`entry_point.py:79`) goes. Dropping it is fine; the public `generate_all_derived_schemas` then no longer refuses a colliding group on its own, and only in-repo tests call it.
  - I checked the other covered sites in `cli/`, `generation/`, `contracts/` and `core/`. The predicate compiler and coverage sites (rows 336, 341, 343, 357) are reached only through the constraint plan build, which is in `prepare`. The exit-point site (row 377) is `internal_invariant`.
- **R2-2 (Major). No step is named to log a failure raised inside a writer.** `emit_package` "returns `None` on success or the environment failure it logged" (`design.md:162`). Today the writers also raise `CodeGenerationError` (the three renderer guards above, `internal_invariant` sites in stencils, registry and pipeline) and unclassified exceptions. Today's two handler blocks catch them and log one refusal record each (`cli/__init__.py:1402-1410` and `:1266-1281`). The Implementation Notes place those blocks under "`prepare`'s refusal conversion", but `prepare` never runs the writers. If the plan follows the text literally, a template defect in `generate` becomes an uncaught traceback instead of today's `SI_INTERNAL_DEFECT` record. That breaks Invariant 5 and the stated limit in Architecture ("`generate` fail[s] with `SI_INTERNAL_DEFECT`").
  - Fix: state that `emit_package` (or `run_codegen` around it) keeps today's post-write handling exactly: `CodeGenerationError` gives "Code generation failed" with its refusal, `OSError` gives "Writing the generated package failed" with `PACKAGE_WRITE`, and anything else gives the internal-defect refusal. Add a `PreparationStep` member for a writer failure so the report can name it. Also say whether `generate` still runs `assess_screen` after a failed emit.
- **R2-3 (condition on D8's isolation). The readiness line's reasons must not be a closed enum that `log_report` switches on.** D17 has `log_report` handle "every member of every enum". If the verdict's reasons are an enum, the owner's option (b) adds a member, and `log_report` and the totality test change too. Fix: `readiness` returns its reasons as rendered text (or as data that `log_report` prints without branching on it). Then the isolation claim holds as written.
- **R2-4 (Minor). The churn list misses `_generate_package_from_graph`.** The design never says what becomes of it. Four test files call or patch it: `tests/unit/test_cli_generation.py:348, 366, 381, 466, 475, 490`, `tests/conformance/test_constraint_catalog_totality.py:110, 140, 269`, `tests/conformance/test_coverage_preflight.py:67`, and a fourth patch at `tests/conformance/test_public_diagnostic_totality.py:471-473`, which the design's three-patch list omits. Every direct call passes a graph that a `prepare` step refuses, so these tests move to `prepare_graph`. The design should say so, and say that tests do not build a `Prepared` by hand to reach `emit_package`. The two tree-preservation tests (`test_cli_generation.py:472-490`) then no longer touch a destination. Criterion 1's sentinel runs cover that on the live route.

### D8 isolation, checked against the owner's three options

- **READY, with the omission counts on the line:** this is the proposed rule, so only `readiness` needs to change.
- **"Builds, not ready" for the unbound String-default case:** the fact is already in the prepared graph. A String literal default fails `float()` in `resolve_modeled_default` and sets `unresolved_default_kind` (`extraction/modeled_defaults.py:47-51`). Projection carries that onto `EntryPoint` (`elaboration/project.py:508`), next to `entry_type`, `python_type` and `default_value` (`resolution/models.py:80-88`). `readiness(report)` receives `Prepared.graph` (D8), so it can test for a library-default `str` entry point with an unresolved default without any change to `prepare`, `Prepared` or the report. I inferred this from the code. I did not run the case to see the field's value.
- **A generator change under RG-2 that removes the case:** nothing in 2b changes. If RG-2 is instead settled by a new screen rule in agentic-mbse, the profile version, the pin, `REASON_MAPPING` and 2a's stored answers change. That cost comes from the cross-repo change itself, not from how 2b is built.
- **In every case,** the exit code, the readiness line and the tests all go through `readiness` (D6, D8, Invariant 7). No Validation line asserts READY or exit 0 on a corpus case. "A snapshot is never ready" holds under all three options. Subject to R2-3, nothing outside `readiness`, its tests and the readiness line has to change.

### What I did not check

I did not run any test or licensed command. I did not build the call closure from `emit_package`. I traced callers by name search, so a call through `getattr` or a stored callable would be missed (the same limit D14 states). I did not re-verify round-1 citations that the revision did not touch.

**Overall (Round 2):** Revise. Apply R2-1, R2-2 and R2-3, and R2-4 if convenient. The orchestrator can confirm these against this section without another review round. The ledger gate stays BLOCKED on C1 until the owner rules.
**Next Steps:** Send R2-1 to R2-4 to the design agent. After the owner's D8 ruling, record it under Resolutions and continue to `/_my_plan`. The reviewer does not edit the design.
