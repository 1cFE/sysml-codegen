# Design: Read-only readiness check, live half (EXEC-SUBSET-CONTRACT Item 2b)

**Status:** Draft, revision 1 (2026-10-20). Not yet reviewed.
**Owner:** Reid Westwood
**Created:** 2026-10-20
**Branch / base:** sysml-codegen `subset-profile-screen` at `18714833`; agentic-mbse sibling worktree `/home/reid/src/subset-conformance/agentic-mbse` (no change needed there, see D12)
**Product lens:** see the `design` block in [product-lens.md](product-lens.md).

## Overview

`generate` is split into a read-only half (`prepare`) and a writing half (`emit_package`). A new `check` command runs only the read-only half, runs the shared subset screen beside it, and prints one report. `generate` prints the same report and then writes. The generator's route alone decides refused or builds; the screen only adds findings.

## Related Artifacts

- Spec: [spec.md](spec.md) (revision 3); review: [spec-review.md](spec-review.md); ledger: [product-lens.md](product-lens.md); owner answers: [briefs/align.md](briefs/align.md); snapshot spike: [spike-snapshot/FINDINGS.md](spike-snapshot/FINDINGS.md)
- 2a design (adapter, mapping, receipt, tripwire): `c381fb00:.project/active/subset-profile-conformance/design.md` § A, § B, D3, D8, D12, D13, D15
- Epic: agentic-mbse `.project/backlog/epic_executable-subset-contract.md`, Item 2b (no Required Reading listed); Item 3's L6 display table (`agentic_mbse/validation/execution_target.py:176-193`)
- Split-off item: `.project/backlog/BACKLOG.md` `[SUBSET-SCREEN-SNAPSHOT-CARRIAGE]`
- Decision records read: `.project/adr/0005` (v6, no migration), `0007` (agentic-mbse owns neutral facts; codegen owns rendering), `0011` (projection boundary, snapshots as serialization), `0016` (API version pin, no package bump). This design contradicts none of them.

## The Point

A modeler needs one command that tells them, before anything is written, whether `generate` will build their model, every reason it won't, and every finding the shared screen has, honestly marked where something could not be assessed. `generate` must report the same findings in the same form. [ORCHESTRATOR]

That answer is only worth having if it is the generator's own answer. The owner ratified that the generator's route alone decides whether `generate` and `check` refuse; the screen only adds findings, and no route gains a refusal keyed on the screen, its version or its failure. [OWNER-ratified 2026-10-20, `briefs/align.md` Q1] Any change to what the generator accepts or refuses is the owner's (RG-1), as is String policy (RG-2) and merging and ADR filing (RG-3). [OWNER, epic gates 2026-10-18] The product never makes a bad model generate. [`.project/product/0003`, owner-verbatim]

So the design has three obligations. `check` must be the generator's route minus the writes, not a copy of it. The screen must be unable to change the generator's answer. And a refused `generate` must leave the destination as it found it, which today fails for one public refusal (`PARAM_FIELD_COLLISION`).

## Research Findings

How `generate` works today (`src/sysml_codegen/cli/__init__.py`):

- `run_codegen` (`:1166`) builds an `ExactPipelineContext` and reads its graph, converting each exception class into a logged refusal (`:1218-1259`). It then calls `_generate_package_from_graph` (`:1284`), which runs six pure preflights (`:1305-1324`), the destination link check (`:1327`), the constraint plan build (`:1337`), the coverage preflight (`:1343`), then the first write (`--overwrite` clear `:1346-1348`, folder creation `:1351`) and nine writers and the seal (`:1354-1394`).
- A refusal's public form is a log record: the message text plus `extra={"refusal": Refusal}` (`cli/refusal.py:49-90`), and `constraint_name_safety` for generation refusals. The 2a harness reads that record (`tests/helpers/subset_profile/observe.py:100-115`). About 70 test files call `run_codegen` and read its return value or log records.
- Rendering and writing are interleaved inside the writers. `_generate_modules` stages before writing (`:540-575`), but the others render and write in one loop, and `generate_all_derived_schemas` writes inside `generation/entry_point.py:63-101`. This is the one place the flow resists factoring (see Architecture).
- The writers re-run `_preflight_constraint_names` on the same graph (`:483, 534, 588, 685, 709, 733, 763, 784, 812`).
- The one late public refusal is `_refuse_colliding_field_names` (`generation/entry_point.py:21-45`, site account row 337), called per group inside `generate_all_derived_schemas` (`:79`). It is a pure check over `graph.entry_point_groups`. `_preflight_registry_class_names` (`cli/__init__.py:279-298`) is the precedent: the same pure detector, run before the first write.
- Every other raise site in the writer modules is `internal_invariant` (site account: `pipeline.py:180,201`, `preservation.py:181`, `registry.py:67,375`, `stencils.py:54,61,67,131,264`, `test_gen.py:61,77`). Eight sites in `generation/`, `cli/` and `contracts/` are `public_capability`, `malformed_input` or `unknown`; only `entry_point.py:38` runs after the first write.

The live route and the screen:

- The live route loads through `SysMLDataExtractor.load_models` (`extraction/extractor.py:62-68`), which calls `SysideAdapter.load_model` (agentic-mbse `syside_adapter.py:327-343`). 2a's screen half calls the same function on the same root (`observe.py:369-378`). The loaded model is local to `_elaborate_model_paths` (`orchestration/elaborated_pipeline.py:157-180`).
- The screen is `evaluate_subset_profile(extract_subset_facts(model))` (agentic-mbse `subset_profile.py:1402`). Its result carries a `Verdict` (`:164-177`, `CLEAR` is the only clean one), findings with `Outcome` and `Qualification` (`:150-162`, `:242-253`), and `UnverifiedCheck`s for facts it could not read (`:754-761`).
- The adapter (`subset_profile_adapter.py`) holds `REASON_MAPPING`, `SubsetDiagnostic` and `render_finding`, and raises `ImportError` at import when the installed profile differs from the pin (`:29-35`). The agreement rule that classifies disagreements lives only in test code (`tests/helpers/subset_profile/cases.py:459-478`).
- 2a's tripwire (`observe.py:135-164`, `test_tripwire.py`) fails any generator-half run that calls the screen. Its docstring already says that in 2b the generator half is "the route with the screen bypassed".
- L6 shows `excluded` and `omitted` findings as warnings under the `generated` target, not errors (`execution_target.py:176-193`).

Cost of a second SysIDE load (D2): the spike measured capture (load, elaborate, seal) and fact extraction per model (`spike-snapshot/out/time_capture.md`). A second load costs less than the capture column: under 0.13 s for 20 of 23 models, under 0.7 s for `solar_battery_d5`, and under 3.7 s for each `catf_mfe` model. Extraction (3.2 s on `catf_mfe_d5`) is paid whichever way the model is loaded. I could not time the load alone: licensed commands needed approval this session.

## Core Concept

Today `generate` is one function that checks and writes in the same pass. This design cuts it in two at the first write.

- **`prepare`** is the generator's route up to, not including, the first write. It takes a model source and a package name, never a destination, and returns a typed `Preparation`: either `Prepared` (the graph, the constraint plan and the template environment) or `Refused` (the refusal, the step that refused, and the exact log message `generate` prints today). It holds every model refusal the generator can raise, including `PARAM_FIELD_COLLISION`, moved to its last step.
- **`emit_package`** is everything after: the destination link check, the clear, the writers and the seal. It is the only code that changes the destination; the one other function that reads it, the read-only `inspect_destination`, is the link check `emit_package` also starts with.
- **`assess_screen`** runs the shared screen on the same source, on its own SysIDE load. It never raises: a skewed profile, a raised screen or a model that does not load becomes a "not assessed" answer with a reason.
- **`ReadinessReport`** combines the two answers. It holds the generator outcome, the screen findings, what was not assessed, any disagreement, and a readiness verdict. One function renders it to log lines.

`check` is `prepare` + `assess_screen` + report. `generate` is `prepare`, then `emit_package` if the model builds, then `assess_screen`, with the same report around them (D16 gives the order). The generator's own route, which the conformance harness runs with the screen switched off, is `prepare` + `emit_package`.

The key insight is that the read-only boundary and the authority boundary are the same kind of cut. "check writes nothing" holds because check never calls the writing half, and the writing half lives in its own module. "The screen cannot change the outcome" holds because the screen's result only flows into the report, never into `prepare` or the decision to call `emit_package`. Tests prove both, but neither depends on a flag.

## Key Bets

- **B1. Two SysIDE loads of the same paths give the same model, apart from anonymous element UUIDs.** The spike's runs A and B, separate processes, gave equal screen results on 269 of 269 subjects once anonymous UUIDs were set aside (`FINDINGS.md` §4). *If false → the screen describes a different parse than the generator built, and Success Criterion 4 (check's findings equal the stored screen answers) fails on the affected cases. Fallback: share the generator's load (D2's rejected option).*
- **B2. Every model refusal `generate` can raise is reachable before the first write once `PARAM_FIELD_COLLISION` moves.** The site account says the writers hold only `internal_invariant` sites. *If false → `check` says "builds" for a model `generate` refuses with a model code, and a refused `generate` leaves a partial package. The reachability test (D14) is built to catch exactly this.*
- **B3. Modelers accept the extra time on every live `generate`: a second load plus fact extraction.** Worst case is the `catf_mfe` models, a few seconds each on top of a few seconds today; every other committed model adds well under a second. *If false → `generate` feels slow on large models. Sharing the load saves only the load, not extraction; there is no way to report findings on `generate` (Success Criterion 10) without paying extraction.*
- **B4. Moving the writers into their own module and routing outcomes through `Preparation` changes no generated byte.** The writers move verbatim. *If false → seals change, consumers' `integrate` reports `snapshot-drift`-like package drift, and the refactor is not behaviour-preserving. A byte-identity check over every builds case and fixture catches it (Validation).*
- **B5. A three-way answer (ready, not ready, refused) is something a modeler reads correctly.** "Not ready" means "generate will build this, but the screen cannot vouch for all of it", not "generate will fail". *If false → modelers or scripts treat not ready as failure. Every snapshot replay is not ready (spec option 3), so a script gating on exit 0 fails on replays.*

## Key Decisions

- **D1. Split at the first write into `prepare` (read-only) and `emit_package` (writes), in separate modules.** `prepare` and the six preflights move to `cli/prepare.py`; the destination link check, clear, setup, nine writers and seal move verbatim to `cli/emit.py`. `cli/__init__.py` keeps argparse, the `cmd_*` functions, `run_codegen` and the new `run_check`. *Rejected: `check` as `run_codegen` with a skip-writes flag (the guarantee would rest on every writer honouring the flag). Rejected: keeping both halves in `cli/__init__.py` (the boundary would be a convention inside one 1,400-line file, not an import a test can check).*
- **D2. The screen runs on its own SysIDE load of the same paths.** `assess_screen` calls `SysideAdapter.load_model`, exactly as 2a's screen half does, so the live answer is computed the way the stored answers were. `orchestration/elaborated_pipeline.py` is not edited. *Rejected: reuse the generator's loaded model. It saves at most the load time (B3), but it needs `_elaborate_model_paths` split to hand out its model, couples the screen to the generator's parse (anything the screen's extraction does to SysIDE state then sits upstream or downstream of elaboration), and moves the 2a harness's elaboration spy.*
- **D3. `PARAM_FIELD_COLLISION` moves to the last step of `prepare`, after the coverage preflight.** `generation/entry_point.py` gains two pure functions: one that builds a group's field rows (used by both the writer and the check) and `refuse_param_field_collisions(groups)`, which runs `_refuse_colliding_field_names` over every group in order. The raise site, its code and its `SiteReason` do not move, so its site ID is unchanged. The call inside the writer stays, as a re-check that can no longer fire. Placing it last keeps the first reported code for any model with several faults: every public check that runs before it today still runs before it. *Rejected: render everything in memory, then write. It would also move rendering's internal checks before the first write and let `check` render, but it means changing all nine writers, `entry_point.py`'s writing functions and smart-regen backups (`preservation.py:223-230`), for checks no well-formed model reaches.*
- **D4. The destination link check runs after `prepare`, not inside it.** `inspect_destination(path)` is read-only (`ensure_package_tree_is_link_free`). Both commands run it in the read-only half when they have a destination: `generate` always, `check` only with `--output`. A problem renders as today's `Package sealing failed` line with its `PACKAGE_WRITE` refusal payload; `generate` then stops without writing and exits 1, and `check` reports not ready. `emit_package` repeats the check as its first step, because the tree can change in between. One visible change: a model with a model refusal and a symlink in its destination now reports the model refusal, where today it reports `PACKAGE_WRITE` (the link check ran at `:1327`, before the plan build). Both runs fail either way, so what is refused does not change, and `PACKAGE_WRITE` carries no code, so the spec's "same first refusal code" condition (L2-1) is about model codes and still holds. *Rejected: keep the link check inside `prepare` when a destination is given. Then `check --output` on a symlinked destination could not say whether the model builds.*
- **D5. One report type, one renderer, both commands.** `ReadinessReport` (`cli/readiness.py`) holds the generator outcome, the screen assessment, at most one disagreement, the destination check and a `Readiness` verdict. `log_report(report)` writes it through the CLI's logger. The generator refusal line is byte-identical to today's, with the same `extra` payload, so the 2a harness, the ~70 `run_codegen` test files and any log reader see no change to it. Every other report line is INFO. *Rejected: `generate` keeps its log lines and `check` gets its own printer (two forms that drift).*
- **D6. The `check` command.** `sysml-codegen check (--models PATH | --from-snapshot PATH) [--output DIR] [--package-name NAME] [--verbose]`. `--package-name` matters because the constraint plan renders with it. `--output` adds the destination link check; without it the report says the destination was not checked. `check` takes no `--overwrite`, `--preserve-handwritten` or `--smart-regen`: they change only what `emit_package` does, never the model outcome. Exit codes: **0** ready, **1** refused (also when agentic-mbse is not installed, as `generate` does), **3** builds but not ready. 2 is skipped because argparse exits 2 on a usage error. `generate`'s exit codes do not change and never depend on the screen. *Rejected: exit 2 for not ready (collides with usage errors). Rejected: a `--json` output now (not asked for; the report is a frozen dataclass, so it is a small later addition).*
- **D7. A screen finding joins a generator refusal by code, through `REASON_MAPPING`, and is shown with both locations.** A `refused` finding "matches the refusal" when its mapped code is among the refusal's codes. This is 2a's agreement relation, not a new one. No field is added to `Diagnostic`, `ReadinessFinding`, `CodeGenerationError` or `RefusalItem`, so the field-by-field converters in `elaborated_pipeline.py:295-371` are not touched and cannot drop anything. `SubsetDiagnostic` (adapter, codegen-owned) gains `rule_id`, `outcome` and `qualification`, and its file is mapped to the portable `root-N/<path>` referent the generator's refusals use (`map_live_source_referent`, `analysis/source_referent.py:43`). *Rejected: carry the screen's reason on the generator's refusal items (a new field through every converter, for no new information).*
- **D8. Ready means: the generator builds, the screen's verdict is `CLEAR`, no finding is a `candidate_refusal`, and the destination is clean if it was checked.** `CLEAR` already excludes refused, unconfirmed and unverified results and narrowed roots (`subset_profile.py:164-177`), and when the generator builds and the verdict is `CLEAR` no disagreement is possible. An `omitted` or `excluded` finding alone does not make a model not ready; it is shown with what the package leaves out, and the readiness line itself carries the counts ("READY; the package leaves out 2 omitted and 1 excluded element"), so READY never reads as "nothing lost". This follows the records and L6, which shows those outcomes as warnings under the `generated` target. If the owner rules under RG-1 or RG-2 that a loss should block, the records mark it `candidate_refusal` or refused, and `check` follows with no code change. *Rejected: every omission is not ready (it would decide String policy, RG-2, by the back door, and make any model with a String attribute permanently not ready).*
- **D9. The agreement rule moves into `cli/readiness.py` as a pure function; the test helper calls it.** Input: whether the generator builds, its refusal codes, and the reason and mapped code of each refused finding. Output: no disagreement, or one of `generator_refuses_screen_silent`, `screen_refuses_generator_builds`, `code_unmapped`. It is computed only when the screen was assessed. `tests/expectations/subset_profile/disagreements.json` stays the hand-edited oracle and is never read at runtime (2a D3's writer guard already covers `src/`). *Rejected: two copies of the rule, one in tests and one in `src/` (smell 1: two representations kept in step by hand).*
- **D10. Skew is decided before the adapter is imported.** `subset_screen.py` compares agentic-mbse's `SUBSET_PROFILE_VERSION` with the pin in `_upstream_pins.py`; if they differ the screen is not assessed, naming both versions. Only then does it import the adapter, inside the function, under a catch-all that turns any failure into "not assessed, screen failed". 2a's `test_nothing_in_src_imports_the_adapter` is replaced by a test that only `subset_screen.py` imports the adapter at run time (type-checking imports aside), and only inside `assess_screen`.
- **D11. The conformance harness's generator half becomes `prepare` + `emit_package`.** It reads the refusal from `Preparation` directly instead of from the log record, and keeps its elaboration and entry-point spies (`prepare` still reaches `elaborate_model_paths` through `build_exact_pipeline_context`). The tripwire stays as it is. A separate test runs `run_codegen` on every case and requires its logged refusal to equal the generator half's.
- **D12. No agentic-mbse change and no version bump.** Everything 2b calls in agentic-mbse exists at the sibling's base. A bump would make all 23 committed v6 envelopes and the consumers' snapshots unloadable through the exact-version check (`snapshot/envelope.py:455-462`) and buy nothing. No gate rerun is required by the `[HARD]` rule. One procedural note: if 2b merges in one coordinated pair with 2a, 2a's D13 `pre_pr` step asks for a receipt naming 2b's final codegen commit, because 2b changes `src/` and `tests/conformance/subset_profile/`.
- **D13. An environment failure after the first write leaves a partial package, as today.** No rollback. With `--overwrite` the old package is already gone at that point. *Rejected: write to a staging folder and swap (protects the old package, but it is new machinery for a disk or permission failure the spec puts out of scope).*
- **D14. Reachability after the first write is decided statically.** A pure test builds a name-based call closure from `emit_package` over `src/sysml_codegen/` and joins it with the site account. Every `public_capability`, `malformed_input`, `unknown` or `relay_plumbing` site whose enclosing function is in the closure must appear in a short table, `POST_WRITE_RECHECKS`, naming the `prepare` step that runs the same check first. Each entry with a witness case is proven by running that case: `prepare` refuses with the site's `SiteReason`. Expected entries: the re-run `_preflight_constraint_names` calls (`validate_constraint_graph_or_raise`, `assert_unique_predicate_function_names`) and `_refuse_colliding_field_names`. *Rejected: a runtime trace over the corpus (only proves what the corpus exercises).* Limit: a call made through `getattr` or a stored callable is not followed.
- **D16. Order inside each command.** `check`: `prepare`, `inspect_destination` (with `--output`), `assess_screen`, then `log_report`. `generate`: `prepare`, `inspect_destination`, and the generator section of the report (the refusal line, so a refused run logs it first, as today); then `emit_package` when the model builds; then `assess_screen` and the rest of the report. `log_report` renders sections in one fixed order, so both commands print the same report lines in the same order; `generate`'s writing lines fall between the generator section and the screen section. *Rejected: screen before writing in `generate` (a screen crash, or an `Exception` the catch-all misses through a bug, would then stop a package that builds today, which is a failure keyed on the screen).*
- **D15. Parity evidence lanes.** The licensed default lane runs every criterion test. A byte-identity check compares every package `generate` writes for the corpus's builds cases and the 23 committed snapshots (live and from-snapshot) against a manifest recorded at the base before the refactor. The `execution` lane (124 TEAx tests) runs once before close, because 2b moves the writers. A wheel build is not run: 2b adds modules, no package data, and changes no template.

## Architecture

```
            ┌──────────────── read-only (both commands) ────────────────┐
source ───► prepare(source, package_name) ──► Preparation (Prepared | Refused)
   │                                                     │
   └──────► assess_screen(source) ──► ScreenAssessment ──┼──► readiness_report(...) ──► ReadinessReport ──► log_report
            [optional] inspect_destination(dir) ─────────┘
            └────────────────────────────────────────────────────────────┘
generate only, when Prepared:  emit_package(prepared, config)  ── link check, clear, write, seal
                               (generate runs it before assess_screen; D16)
```

- **Data flow.** The model source is `LiveModels(paths)` or `SnapshotFile(path)`. `prepare` reads the source and nothing else. `assess_screen` reads the source and the installed agentic-mbse. `readiness_report` is pure. `emit_package` is the only step given a destination it may change.
- **The steps inside `prepare`, in today's order.** Each has a name in a closed `PreparationStep` enum, carried on `Refused`: construction (context build and projection), generation metadata, exit-point types, constraint names, output paths, registry class names, constraint totality, constraint plan, coverage account, parameter field names (new, D3). A test pins this order.
- **What `check` does not run, and why.** It does not run `emit_package`: the clear, the folder setup, template rendering for schemas, modules, stencils, pipeline, registry, entry points, backlog and tests, smart-regen's stencil reads and backups, and the seal. Rendering is the gap that matters: its raise sites are all `internal_invariant`, so a well-formed model cannot fail there, but a template defect would make `generate` fail with `SI_INTERNAL_DEFECT` where `check` said "builds". That is the stated limit (spec Success Criterion 3), not a model refusal.
- **Where the flow resists clean factoring, and what it costs.** Rendering and writing are fused inside the writers (`cli/__init__.py:477-800`, `entry_point.py:48-145`), so `check` cannot render without writing. D3 accepts that instead of rewriting nine writers. The second cost is churn: about 20 test references patch or import private names on `sysml_codegen.cli` (`_get_template_env`, `_check_duplicate_output_paths`, `_clear_output_directory`, `_setup_output_directories`, `_generate_stencils`, `_seal_package`, `_ensure_package_init_files`, `_generate_package_from_graph`). After D1 they must patch the new module. Re-exporting the names would make those patches silently ineffective, so the tests are updated, not shimmed. The third: the nine writers keep their repeated `_preflight_constraint_names` calls, which D14 has to account for. `orchestration/elaborated_pipeline.py` and its converters are not touched.
- **The snapshot seam.** `assess_screen(SnapshotFile)` returns "not assessed: snapshots do not carry the screen". That branch is the whole seam; `[SUBSET-SCREEN-SNAPSHOT-CARRIAGE]` replaces it with a reader for whatever the envelope then carries. `sysml-codegen snapshot` and `snapshot/` are not edited.
- **What the modeler sees.** A sketch, not the final wording:

```
ERROR: Code generation failed: PARAM_FIELD_COLLISION: parameter group ...        ← unchanged line
INFO: Screen subset-profile/v2: verdict refused; 1 refused, 2 omitted; 0 not assessed
INFO:   refused  binding_source_expression  root-0/plant.sysml:14  Plant::p::x  → SI_EXPRESSION_SOURCE_UNSUPPORTED
INFO:            remedy: <the rule record's remedy>
INFO: Disagreement (generator_refuses_screen_silent): the generator refused with PARAM_FIELD_COLLISION; no screen rule covers it
INFO: Readiness: REFUSED. Readiness covers generation only, not runtime behaviour or handwritten code.
```

## Required Invariants

1. `prepare` takes no destination and performs no file-system write, delete or create. `cli/prepare.py`, `cli/readiness.py` and `subset_screen.py` never import `cli/emit.py`, and `run_check` never calls `emit_package` (import-boundary test).
2. The generator outcome and `generate`'s exit code are functions of `prepare`, `inspect_destination` and `emit_package` alone. Nothing from `ScreenAssessment` flows into any of them.
3. `assess_screen` never raises an `Exception` (which includes `MemoryError` and `RecursionError`), and never imports the adapter before the version comparison. `KeyboardInterrupt` and `SystemExit` propagate. The accepted residual is a native crash inside SysIDE, which no handler can catch; D16 puts the screen after the seal in `generate`, so such a crash cannot cost a package that builds.
4. No `public_capability`, `malformed_input`, `unknown` or relay site is reachable from `emit_package` unless `POST_WRITE_RECHECKS` names the `prepare` step that runs the same check first (D14).
5. For every input, `generate`'s refusal log record (message and `extra`) is identical to the one at the base commit, with one named exception: a model refusal together with a symlinked destination now logs the model refusal instead of `PACKAGE_WRITE` (D4). That case has its own test, which pins the new record.
6. Every package `generate` writes for the corpus's builds cases and the committed snapshots is byte-identical to the base commit's.
7. Readiness is `READY` only under D8's four conditions. A snapshot source is never `READY`.
8. `disagreements.json` is never read by `src/`.

## Component Overview

- **`cli/prepare.py` (new).** `ModelSource`, `PreparationStep`, `Prepared`, `Refused`, `prepare(source, package_name)`, `prepare_graph(graph, package_name)` (the steps after construction, for tests that drive a hand-made graph), the six preflights moved from `cli/__init__.py`, and the new parameter-field step. Converts each refusal class to `Refused` once, with today's message prefixes.
- **`cli/emit.py` (new).** `inspect_destination(path)`, `emit_package(prepared, config)`, and the clear, setup, writer and seal functions moved verbatim. Returns `None` on success or the environment failure it logged.
- **`cli/readiness.py` (new).** `ReadinessReport`, `Readiness` (`READY`, `NOT_READY`, `REFUSED`), `Disagreement`, the pure agreement rule (D9), `readiness_report(...)`, `log_report(report)`. Imports no SysIDE and does not import the adapter at run time.
- **`subset_screen.py` (new, beside the adapter).** `ScreenAssessed` (verdict, rendered findings, unverified checks as not-assessed entries, profile version) and `ScreenNotAssessed` (cause: profile skew with both versions, screen failed with detail, model did not load, snapshot source). `assess_screen(source)`.
- **`subset_profile_adapter.py`.** `SubsetDiagnostic` gains `rule_id`, `outcome`, `qualification`; the module docstring's "nothing on the generate route imports this" is rewritten to D10.
- **`generation/entry_point.py`.** The field-row builder and `refuse_param_field_collisions` (D3).
- **`cli/__init__.py`.** `run_codegen(config) -> bool` keeps its contract and becomes prepare, screen, report, then emit. New `run_check(request) -> ReadinessReport` and `cmd_check`, and the `check` subparser.
- **Tests and harness.** `observe.generator_half` (D11); the replacement boundary test (D10); the reachability test and its call-closure helper (D14); the criterion tests listed in Validation. Site account row 337's evidence pointer is refreshed to the new call.

## Non-Goals

- Changing what the generator accepts or refuses (RG-1), String policy (RG-2), merges and ADR filing (RG-3).
- Carrying the screen in snapshots, a new envelope format or any change to `sysml-codegen snapshot`. That is `[SUBSET-SCREEN-SNAPSHOT-CARRIAGE]`.
- Rendering templates in `check` (D3), rollback after an environment failure (D13), machine-readable `check` output (D6).
- Any edit to agentic-mbse (D12) or to `orchestration/elaborated_pipeline.py` (D2, D7).
- Certifying runtime values, handwritten implementations or the TEAx lane beyond D15's regression run.

## Implementation Notes

- **Order of `prepare`'s refusal conversion.** Keep today's two `except` ladders' behaviour exactly (`cli/__init__.py:1218-1259` and `:1264-1281`, `:1399-1425`): each refusal class keeps its message prefix and `extra`, and an unclassified exception still becomes `unexpected_public_failure`. Refused types to keep apart: snapshot, readiness, diagnostic, parsing, generation, internal defect.
- **`Refused` carries the logged form, not the exception.** Fields: `step`, `refusal: Refusal`, `message: str`, and the `constraint_name_safety` value when the refusal is a generation error. `log_report` must log exactly what today's code logs.

```python
@dataclass(frozen=True)
class ReadinessReport:
    generator: Prepared | Refused          # Prepared is shown as "builds"; its payload is not rendered
    screen: ScreenAssessed | ScreenNotAssessed
    disagreement: Disagreement | None      # only when the screen was assessed
    destination: DestinationCheck          # NOT_CHECKED | CLEAN | problem text
    @property
    def readiness(self) -> Readiness: ...  # D8; a SnapshotFile source can never be READY
```

- **Skew tests.** In-process: drop `sysml_codegen.subset_profile_adapter` from `sys.modules` and patch agentic-mbse's `SUBSET_PROFILE_VERSION` to an older and a newer value, so `assess_screen` exercises the real import path both ways. This is how "isolated artifacts" is met; installing two agentic-mbse versions is not attempted.
- **Location mapping.** `map_live_source_referent(raw, model_paths)` accepts the `///` form SysIDE reports (spike §4). On `ValueError` keep the raw string rather than failing the screen.
- **Logger.** `log_report` logs through `logging.getLogger("sysml_codegen.cli")`, so today's records keep their logger name.

## Potential Risks

| Risk | Mitigation |
|---|---|
| Licensed suite slows: about 70 test files call `run_codegen`, which now loads each model twice and screens it | Most fixtures load in well under 0.1 s (spike table). Phase 0 times the suite at the base; the plan compares |
| A test asserts on the count or level of INFO records and breaks on the new report lines | Report lines are INFO, the refusal line is unchanged (Invariant 5). Phase 0 greps for record-count assertions |
| The call closure (D14) is noisy and the table grows past the three expected entries | Measure the closure first, before any other D14 work; each extra entry needs a named guard |
| Byte identity (B4) fails because moved code finds a file by its own location. The two known cases, `verify.py` (`cli/__init__.py:831`) and the templates folder (`:134`), resolve from `Path(__file__).parent.parent`, which is unchanged for files in `cli/` | The byte-identity check names any file that differs |
| Sentinel runs (Success Criterion 1) are slow: every refused case times four flag sets times two sentinels | Refused cases stop before writing, so each run is a load plus elaboration. If the lane is too slow, share one tree copy per case; do not drop cases or flags |
| SysIDE crashes natively during the screen's load or extraction | Not catchable. D16 runs the screen after the seal in `generate`, so the package is complete; the run loses its report and exits by the crash. `check` would crash the same way. Accepted residual (Invariant 3) |
| A screen finding's location cannot be mapped to a referent | Keep the raw path (Implementation Notes); the finding is still reported |

## Integration Strategy

- `generate`'s outcome, exit code, refusal record and written bytes stay as they are; it gains report lines. Consumers that parse `generate`'s log for the refusal see the same record.
- `check` is new. The `run-study` skill and L6 are untouched; a later item can point them at `check`.
- 2a's tripwire, reach test, site account and record tests keep running; the harness changes in D11 and the boundary test in D10 are the only 2a test changes in kind.
- The CLAUDE.md "Processing Pipeline" section and `docs/architecture/` get a short note on `prepare`/`emit_package` and `check` at close.

## Validation Approach

Every test that runs a live model or captures a snapshot is licensed, and a skip is not a pass (spec). Criterion numbers are the spec's.

- **1 (same refusal, sentinel unchanged).** For every refused 2a case: `check --output` and `generate` under no flags, `--overwrite`, `--preserve-handwritten`, `--smart-regen`, and `--overwrite --preserve-handwritten`, each on a populated and an empty sentinel. Same `Refusal`, same `PreparationStep`, sentinel tree byte-identical with no files added or removed.
- **2 (refused generate leaves the destination).** Covered by 1's `generate` half. Environment failures: D13.
- **3 (reachability).** D14's pure test plus its witness runs.
- **4 (check equals stored answers).** For every 2a case: generator outcome and codes equal the stored generator answer; findings equal the stored screen answer under 2a's normalization; the computed disagreement equals the case's entry in `disagreements.json` (or its absence).
- **5 (replay).** For the 23 committed snapshots and every builds case captured on the fly: `check --from-snapshot` gives the same generator outcome as live, the screen is not assessed with the snapshot reason, readiness is never ready; `generate --from-snapshot` builds as before (byte identity).
- **6 (snapshots unchanged).** All 23 envelopes load; a refused envelope keeps its message; capture output is byte-identical with the adapter patched to raise and under patched skew.
- **7 (skew).** Both directions, both commands, on a builds case and a refused case: outcome unchanged, both versions named, `check` exits 3 or 1, no `ImportError` text in the output.
- **8 (screen fails).** `extract_subset_facts` and then `evaluate_subset_profile` patched to raise, on a builds case, both commands: outcome unchanged, screen not assessed.
- **9 (screen refuses, generator builds).** A builds case with `evaluate_subset_profile` patched to return one refused finding: disagreement `screen_refuses_generator_builds`, `check` exits 3, `generate` still builds.
- **10 (same form).** `generate` and `check` on the same cases emit identical report lines (the refusal line, screen lines, disagreement, readiness).
- **11 (tripwire).** `test_tripwire.py` unchanged and passing against D11's generator half.
- **12 (baselines).** Phase 0, below.
- **Invariants.** Import-boundary test (1, 8); byte-identity check (5, 6); step-order test; one test for D4's changed record (a refused case with a symlinked sentinel logs the model refusal, and nothing in the sentinel changes); one test for D16 (with `assess_screen` patched to raise, `generate` on a builds case writes and seals the same bytes and exits 0).

## Next-Stage Handoff

**Fixed:** D1–D16; the module names; `check`'s flags and exit codes; the readiness rule; no agentic-mbse edit; `elaborated_pipeline.py` untouched.

**Phase 0, before any implementation (spec Success Criterion 12, not done in this session).** Licensed commands needed approval this session, so I did not re-run the baselines. Phase 0 must: re-run both suites at the base with `baseline.md`'s commands (`--all-extras`, license sourced) and record failing test IDs in this folder; record mypy and ruff counts; time the licensed suite; record the byte-identity manifest for D15; and time a second `SysideAdapter.load_model` on `catf_mfe_d5` and `catf_mfe_gated` to put a number on B3.

**De-risk first:** D14's call closure size, then B4's byte identity on one writer moved.

**Open for the plan:** report wording (keep within L6's "CLEAR is relative to the implemented rules"); how the sentinel matrix is parallelized.

**Parked for the owner:**

- Nothing in 2b changes what the generator accepts or refuses. D4 changes which failure a run reports first when a model refusal and a symlinked destination occur together; I judge that outside RG-1 because both runs fail, and flag it for review rather than decide it silently.
- D8 leaves omitted String values out of the readiness verdict, so String policy stays with RG-2.
- ADR candidates for the owner to file at merge (RG-3): "destination writes live only in `cli/emit.py`; `prepare` takes no destination" (D1), and the readiness rule (D8). No entry is filed by this design.

**Effort:** about 7–8.5 engineer-days for the live half, a guess: prepare/emit split and byte identity 1.5–2; screen, report and renderer 1.5; `check` CLI 0.5; the hoist 0.25; harness and boundary tests 0.75; criterion tests including the reachability test 2–2.5; Phase 0 and lanes 0.75–1.

## Appendix A — Files

| File | Change |
|---|---|
| `src/sysml_codegen/cli/__init__.py` | Keeps argparse, `cmd_*`, `run_codegen`; adds `run_check`, `cmd_check`, the `check` subparser; loses preflights and writers |
| `src/sysml_codegen/cli/prepare.py` | New (D1, D3) |
| `src/sysml_codegen/cli/emit.py` | New, moved writers (D1, D4, D13) |
| `src/sysml_codegen/cli/readiness.py` | New (D5, D8, D9) |
| `src/sysml_codegen/subset_screen.py` | New (D2, D10) |
| `src/sysml_codegen/subset_profile_adapter.py` | `SubsetDiagnostic` fields, docstring (D7, D10) |
| `src/sysml_codegen/generation/entry_point.py` | Field-row builder, `refuse_param_field_collisions` (D3) |
| `tests/helpers/subset_profile/observe.py` | `generator_half` (D11) |
| `tests/helpers/subset_profile/cases.py` | `disagreement` calls the `src/` rule (D9) |
| `tests/conformance/subset_profile/test_reason_mapping.py` | Boundary test replaced (D10) |
| `tests/expectations/subset_profile/site_account.csv` | Row 337 evidence pointer; any line refresh the account test asks for |
| About 20 test references to moved private names | Patch the new module (Architecture) |
| New tests | Criteria 1, 3–10; step order; import boundary; byte identity |

---

**Next Step:** `/_my_design_review` in a fresh session, then `/_my_plan`.
