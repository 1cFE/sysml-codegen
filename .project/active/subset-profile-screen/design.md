# Design: Read-only readiness check, live half (EXEC-SUBSET-CONTRACT Item 2b)

**Status:** Draft, revision 2 (2026-10-20). Revision 1 was reviewed (`design-review.md`, verdict Revise). Revision 2 applies the review's must-fix and should-fix points under the orchestrator's rulings, except the readiness rule (D8), which is **PARKED: owner decision pending**.
**Owner:** Reid Westwood
**Created:** 2026-10-20
**Branch / base:** sysml-codegen `subset-profile-screen` at `18714833`; agentic-mbse sibling worktree `/home/reid/src/subset-conformance/agentic-mbse` (no change needed there, see D12)
**Product lens:** `design` and `design_review` blocks in [product-lens.md](product-lens.md). The `design_review` gate is BLOCKED on design_review-F1 (the readiness rule) until the owner rules.

> **Revision 2 (2026-10-20), against `design-review.md`:**
>
> - **M1 (orchestrator ruling):** `prepare` and `assess_screen` now share one SysIDE load per command (D2 rewritten, new `load_source`). This removes the window in which `generate`'s second load could read files saved after the package was written. `elaborated_pipeline.py` gets one small edit: the load lines move into a function; its converters stay untouched. B1 and B3 rewritten.
> - **M2:** a model that loads with errors gives "screen not assessed: the model has parse errors" (D2, Validation).
> - **M3 (orchestrator ruling):** nothing after the seal may raise because of the screen or the report. Mapping happens inside `assess_screen`'s catch-all; `readiness_report`, `readiness` and `log_report` are total over their input types and tested for it; `generate`'s post-seal section has its own guard (D17, Invariant 3).
> - **M4 (orchestrator ruling):** what each command logs on a destination problem is pinned (D4, Invariant 5). The 2a harness's one-refusal-record rule holds, and `check` never logs a refusal record on a "builds, not ready" run. Validation 10 runs `check` with `--output`.
> - **C1 / design_review-F1, F2:** D8 is unchanged in substance and marked PARKED. The readiness rule is one pure function over the whole report, so the owner's answer changes that function, its tests and the readiness line only. The false handoff line about String values is removed.
> - **Question 3 / design_review-F4:** D4's changed first failure is recorded as a stated behaviour change, confirmed not RG-1 by the review. It is no longer parked.
> - **Minor m1–m7:** all applied. m1 is applied in its stronger form: the writers' re-checks are dropped, so `POST_WRITE_RECHECKS` is gone and D14 asserts that no covered site is reachable from `emit_package`.
>
> **Round 2 (2026-10-20), against `design-review.md` "Round 2", orchestrator rulings, no third review:**
>
> - **R2-1:** the constraint-name validator stays inside the pipeline writer, the registry writer and the contract builder (`pipeline.py:56`, `registry.py:266`, `model_contract.py:37`), pinned by `test_module_kind_faildloud.py:277-294`. D14 allows site 338 by name, with that reason. Only the unpinned re-checks are dropped (D3, D14).
> - **R2-2:** `emit_package` owns writer failures and logs today's single refusal record, byte-identical (D18).
> - **R2-3:** `readiness(report)` returns its reasons as data `log_report` prints without branching on them (D8, D17).
> - **R2-4:** `_generate_package_from_graph` is removed; its four test files move to `prepare_graph` (Architecture, Appendix A).

## Overview

`generate` is split into a read-only half (`prepare`) and a writing half (`emit_package`). A new `check` command runs only the read-only half, runs the shared subset screen on the same loaded model, and prints one report. `generate` prints the same report and then writes. The generator's route alone decides refused or builds; the screen only adds findings.

## Related Artifacts

- Spec: [spec.md](spec.md) (revision 3); spec review: [spec-review.md](spec-review.md); design review: [design-review.md](design-review.md); ledger: [product-lens.md](product-lens.md); owner answers: [briefs/align.md](briefs/align.md); snapshot spike: [spike-snapshot/FINDINGS.md](spike-snapshot/FINDINGS.md)
- 2a design (adapter, mapping, receipt, tripwire): `c381fb00:.project/active/subset-profile-conformance/design.md` § A, § B, D3, D8, D12, D13, D15; 2a RG-2 note: `c381fb00:.project/active/subset-profile-conformance/rg2-string-policy.md`
- Epic: agentic-mbse `.project/backlog/epic_executable-subset-contract.md`, Item 2b (no Required Reading listed), open owner decisions (`:318-319`); L6 spec `.project/completed/20261020_l6-subset-profile/spec.md:148, :158`; L6 display table (`agentic_mbse/validation/execution_target.py:176-193`)
- Split-off item: `.project/backlog/BACKLOG.md` `[SUBSET-SCREEN-SNAPSHOT-CARRIAGE]`
- Decision records read: `.project/adr/0005` (v6, no migration), `0007` (agentic-mbse owns neutral facts; codegen owns rendering), `0011` (projection boundary, snapshots as serialization), `0016` (API version pin, no package bump). This design contradicts none of them.

## The Point

A modeler needs one command that tells them, before anything is written, whether `generate` will build their model, every reason it won't, and every finding the shared screen has, honestly marked where something could not be assessed. `generate` must report the same findings in the same form. [ORCHESTRATOR]

That answer is only worth having if it is the generator's own answer. The owner ratified that the generator's route alone decides whether `generate` and `check` refuse; the screen only adds findings, and no route gains a refusal keyed on the screen, its version or its failure. [OWNER-ratified 2026-10-20, `briefs/align.md` Q1] Any change to what the generator accepts or refuses is the owner's (RG-1), as is String policy (RG-2) and merging and ADR filing (RG-3). [OWNER, epic gates 2026-10-18] The product never makes a bad model generate. [`.project/product/0003`, owner-verbatim]

So the design has three obligations. `check` must be the generator's route minus the writes, not a copy of it. The screen must be unable to change the generator's answer. And a refused `generate` must leave the destination as it found it, which today fails for one public refusal (`PARAM_FIELD_COLLISION`).

## Research Findings

How `generate` works today (`src/sysml_codegen/cli/__init__.py`):

- `run_codegen` (`:1166`) builds an `ExactPipelineContext` and reads its graph, converting each exception class into a logged refusal (`:1218-1259`). It then calls `_generate_package_from_graph` (`:1284`), which runs six pure preflights (`:1305-1324`), the destination link check (`:1327`), the constraint plan build (`:1337`), the coverage preflight (`:1343`), then the first write (`--overwrite` clear `:1346-1348`, folder creation `:1351`) and nine writers and the seal (`:1354-1394`).
- A refusal's public form is a log record: the message text plus `extra={"refusal": Refusal}` (`cli/refusal.py:49-90`), and `constraint_name_safety` for generation refusals. The 2a harness reads that record and requires exactly one per refused run (`tests/helpers/subset_profile/observe.py:100-115`, `:238-241`). About 70 test files call `run_codegen` and read its return value or log records.
- Rendering and writing are interleaved inside the writers. `_generate_modules` stages before writing (`:540-575`), but the others render and write in one loop, and `generate_all_derived_schemas` writes inside `generation/entry_point.py:63-101`. This is the one place the flow resists factoring (see Architecture).
- The writers re-run `_preflight_constraint_names` on the same graph (`:483, 534, 588, 685, 709, 733, 763, 784, 812`).
- The one late public refusal is `_refuse_colliding_field_names` (`generation/entry_point.py:21-45`, site account row 337), called per group inside `generate_all_derived_schemas` (`:79`). It is a pure check over `graph.entry_point_groups`. `_preflight_registry_class_names` (`cli/__init__.py:279-298`) is the precedent: the same pure detector, run before the first write.
- Every other raise site in the writer modules is `internal_invariant` (site account: `pipeline.py:180,201`, `preservation.py:181`, `registry.py:67,375`, `stencils.py:54,61,67,131,264`, `test_gen.py:61,77`). Eight sites in `generation/`, `cli/` and `contracts/` are `public_capability`, `malformed_input` or `unknown`; only `entry_point.py:38` runs after the first write.

The live route and the screen:

- The live route reads the user's files in place. `build_exact_pipeline_context` (`orchestration/exact_pipeline_context.py:288-298`) calls `elaborate_model_paths`, which loads at `elaborated_pipeline.py:159-173` and elaborates through `elaborate_loaded_extractor` (`:267`). Only the capture route stages private copies (`:210-215`).
- Loading is `SysMLDataExtractor.load_models` (`extraction/extractor.py:62-77`), which calls `SysideAdapter.load_model` and returns `False` when the diagnostics contain errors (`:73-75`). `SysideAdapter.load_model` itself returns a model even with errors. 2a's screen half calls the same function and also stops on errors (`observe.py:369-378`).
- The screen is `evaluate_subset_profile(extract_subset_facts(model))` (agentic-mbse `subset_profile.py:1402`). Its result carries a `Verdict` (`:164-177`, `CLEAR` is the only clean one), findings with `Outcome` and `Qualification` (`:150-162`, `:242-253`), and `UnverifiedCheck`s for facts it could not read (`:754-761`).
- The adapter (`subset_profile_adapter.py`) holds `REASON_MAPPING`, `SubsetDiagnostic` and `render_finding`, and raises `ImportError` at import when the installed profile differs from the pin (`:29-35`). `render_finding` raises `ValueError` on a refused finding whose reason maps to `NO_REFUSAL` (`:118-123`), as does the test helper's `mapped_code` (`tests/helpers/subset_profile/cases.py:448-453`). The agreement rule that classifies disagreements lives only in test code (`cases.py:459-478`).
- 2a's tripwire (`observe.py:135-164`, `test_tripwire.py`) fails any generator-half run that calls the screen. Its docstring already says that in 2b the generator half is "the route with the screen bypassed".
- L6 shows `excluded` and `omitted` findings as warnings under the `generated` target, not errors (`execution_target.py:176-193`), as ratified in L6 `spec.md:148`. L6 bans readiness wording and leaves that claim to `check` (`spec.md:158`).
- One known silent String loss draws no screen finding: a calc def String default on an unbound input (case `candidate-es-010-refusal__string_library_default__unbound_input`, screen verdict `clear`, loss `rg2_pending`). This is why D8 is parked.

Cost: the spike measured fact extraction per model (`spike-snapshot/out/time_capture.md`): under 0.1 s for 21 of 23 committed models, about 3 s for each `catf_mfe` model. With a shared load (D2), extraction plus the screen is the whole added cost.

## Core Concept

Today `generate` is one function that checks and writes in the same pass. This design cuts it in two at the first write, and gives both halves and the screen the same loaded model.

- **`load_source`** opens the model source once. For live models it runs the SysIDE load and returns the loaded model, its source referents and whether the load had errors. It never raises: a load that fails outright is carried as a failed load. For a snapshot it returns the file path.
- **`prepare`** is the generator's route up to, not including, the first write. It takes the loaded source and a package name, never a destination, and returns a typed `Preparation`: either `Prepared` (the graph, the constraint plan, the template environment and the package name) or `Refused` (the refusal, the step that refused, and the exact log message `generate` prints today). It holds every model refusal the generator can raise, including `PARAM_FIELD_COLLISION`, moved to its last step.
- **`emit_package`** is everything after: the destination link check, the clear, the writers and the seal. It is the only code that changes the destination.
- **`assess_screen`** runs the shared screen on the same loaded model, after `prepare`. It never raises. A skewed profile, a raised screen, a load with errors or a snapshot source becomes a "not assessed" answer with a reason. Everything the report needs from the adapter (mapped codes, rendered findings) is computed inside it.
- **`ReadinessReport`** combines the answers: the generator outcome, the destination check, the screen findings, what was not assessed, any disagreement. One pure function, `readiness(report)`, decides ready, not ready or refused. One function renders the report to log lines.

`check` is `load_source`, `prepare`, `assess_screen` and the report. `generate` is `load_source` and `prepare`, then `emit_package` if the model builds, then `assess_screen`, with the same report around them (D16 gives the order). The generator's own route, which the conformance harness runs with the screen switched off, is `load_source`, `prepare` and `emit_package`.

The key insight is that the read-only boundary and the authority boundary are the same kind of cut. "check writes nothing" holds because check never calls the writing half, and the writing half lives in its own module. "The screen cannot change the outcome" holds because the screen runs after `prepare` and its result only flows into the report, never into `prepare`, the destination check, `emit_package` or the exit code. Tests prove both, but neither depends on a flag.

## Key Bets

- **B1. Elaboration does not change what the screen extracts from the loaded model.** The screen now reads the model after the generator has elaborated it. The screen cannot affect the generator, because it runs second. *If false → the screen's findings on a live run differ from 2a's stored screen answers, which were computed on a fresh load. Success Criterion 4 compares them on every 2a case and fails on the affected cases. Fallback: a second load with a source digest compared before each load, marking the screen not assessed when the files changed (the review's M1 alternative).*
- **B2. Every model refusal `generate` can raise is reachable before the first write once `PARAM_FIELD_COLLISION` moves.** The site account says the writers hold only `internal_invariant` sites. *If false → `check` says "builds" for a model `generate` refuses with a model code, and a refused `generate` leaves a partial package. The reachability test (D14) is built to catch exactly this.*
- **B3. Modelers accept the extra time of fact extraction on every live `generate`.** About 3 s on each `catf_mfe` model, under 0.1 s on every other committed model. *If false → `generate` feels slow on large models. There is no way to report findings on `generate` (Success Criterion 10) without paying extraction.*
- **B4. Moving the writers into their own module, dropping their re-checks and routing outcomes through `Preparation` changes no generated byte.** The writers move verbatim apart from the dropped re-check calls, which write nothing. *If false → seals change and the refactor is not behaviour-preserving. A byte-identity check over every builds case and fixture catches it (Validation).*
- **B5. A three-way answer (ready, not ready, refused) is something a modeler reads correctly.** "Not ready" means "generate will build this, but the screen cannot vouch for all of it", not "generate will fail". *If false → modelers or scripts treat not ready as failure. Every snapshot replay is not ready (spec option 3), so a script gating on exit 0 fails on replays.*

## Key Decisions

- **D1. Split at the first write into `prepare` (read-only) and `emit_package` (writes), in separate modules.** `load_source`, `prepare`, the six preflights and `_get_template_env` move to `cli/prepare.py`; the destination link check, clear, setup, nine writers and seal move to `cli/emit.py`. `cli/__init__.py` keeps argparse, the `cmd_*` functions, `run_codegen` and the new `run_check`. The import boundary keeps `prepare.py`, `readiness.py` and `subset_screen.py` from reaching writing code; a call-level test keeps `run_check` from calling `emit_package`, since it sits beside `run_codegen`. *Rejected: `check` as `run_codegen` with a skip-writes flag (the guarantee would rest on every writer honouring the flag). Rejected: moving only `prepare` out and leaving the writers in `cli/__init__.py` (it saves mechanical import edits but leaves one 1,400-line file mixing CLI parsing and package writing; the boundary strength is the same either way).*
- **D2. One SysIDE load per command, shared by `prepare` and `assess_screen`.** The load lines at `elaborated_pipeline.py:159-173` (with `_live_source_referents`) move into a function that returns the extractor, its source referents and whether the load had errors, without raising. `elaborate_model_paths` keeps its signature, now as that load plus `elaborate_loaded_extractor` (`:267`), so the capture route, `build_exact_pipeline_context` and existing tests are unchanged. `exact_pipeline_context.py` gains a builder that takes an already-loaded source. `prepare` turns a load with errors, or a failed load, into today's `SysMLParsingError` refusal, with today's message (rendered by `_render_parse_diagnostics`, `:94-128`). `assess_screen` runs only on a load without errors; otherwise it reports "not assessed: the model has parse errors" or "not assessed: the model did not load". The converters at `:295-371` are not edited. *Rejected: a second load in `assess_screen` (in `generate` it runs after writing, so it can read files saved since the package was built, and nothing detects it). Rejected: a second load plus a source digest (more machinery to detect a problem sharing removes).*
- **D3. `PARAM_FIELD_COLLISION` moves to the last step of `prepare`, after the coverage preflight.** `generation/entry_point.py` gains two pure functions: one that builds a group's field rows (used by both the writer and the check) and `refuse_param_field_collisions(groups)`, which runs `_refuse_colliding_field_names` over every group in order. The raise site, its code and its `SiteReason` do not move, so its site ID is unchanged. The schema writer (`entry_point.py:79`) no longer calls the check (m1, D14): no test pins `generate_all_derived_schemas` refusing on its own (its one direct test, `test_entry_point_generation.py:46-48`, passes non-colliding groups), and only `prepare` and in-repo tests call it. This differs from the constraint-name guards D14 keeps, which a test pins as their functions' own contract. Placing it last keeps the first reported code for any model with several model faults: every public check that runs before it today still runs before it. *Rejected: render everything in memory, then write. It would also move rendering's internal checks before the first write and let `check` render, but it means changing all nine writers, `entry_point.py`'s writing functions and smart-regen backups (`preservation.py:223-230`), for checks no well-formed model reaches.*
- **D4. The destination link check runs after `prepare`, and only when the model builds.** `inspect_destination(path)` is read-only (`ensure_package_tree_is_link_free`). Neither command inspects the destination of a refused model, so a refused run logs exactly one refusal record, the model's. When the model builds: `generate` always inspects, `check` only with `--output`. What each command logs on a problem:
  - `generate`: today's `Package sealing failed: …` line at ERROR with its `PACKAGE_WRITE` refusal payload, exactly as today. It stops without writing and exits 1. In the report, the generator outcome is `Refused` at the destination step.
  - `check --output`: the same message text, logged at WARNING with no `refusal` extra. The generator outcome stays "builds"; the report's destination entry holds the problem, and the readiness line says `generate` would stop at the destination. Exit 3.
  - `emit_package` repeats the check as its first step, because the tree can change in between; a failure there logs today's record, as now.

  **Stated behaviour change (confirmed not RG-1 by `design-review.md` question 3).** A model refused by the constraint plan build, the coverage preflight or `PARAM_FIELD_COLLISION`, run against a destination that contains a symlink, now reports the model refusal, where today it reports `PACKAGE_WRITE` (the link check ran at `:1327`, before the plan build). Both runs exit 1 and write nothing, no model moves between refused and builds, and `PACKAGE_WRITE` carries no code. A model that builds with a symlinked destination still gets `PACKAGE_WRITE`. *Rejected: keep the link check inside `prepare` when a destination is given (then `check --output` on a symlinked destination could not say whether the model builds).*
- **D5. One report type, one renderer, both commands.** `ReadinessReport` (`cli/readiness.py`) holds the generator outcome, the destination check, the screen assessment and at most one disagreement. `log_report(report)` writes it through the CLI's logger and is a function of the report alone: the two commands print different lines only where their reports hold different data (D4). The generator refusal line is byte-identical to today's, with the same `extra` payload. Screen lines are INFO. **Which findings print in full** (orchestrator decision, 2026-10-20; display only, no outcome changes): refused, unconfirmed and `candidate_refusal` findings, unverified checks and the disagreement print in full, with location and remedy, because a modeler must act on them or they block readiness. Admitted findings print as one count line. Omitted and excluded findings print as one line per rule (outcome, rule, reasons, count), with the rule's remedy once. There is no flag to print every finding. *Rejected: `generate` keeps its log lines and `check` gets its own printer (two forms that drift).*
- **D6. The `check` command.** `sysml-codegen check (--models PATH | --from-snapshot PATH) [--output DIR] [--package-name NAME] [--verbose]`, parsed into `CheckRequest(source: ModelSource, package_name: str, destination: Path | None)`, which `run_check(request) -> ReadinessReport` takes. `--package-name` matters because the constraint plan renders with it. `--output` adds the destination link check; without it the report says the destination was not checked. `check` takes no `--overwrite`, `--preserve-handwritten` or `--smart-regen`: they change only what `emit_package` does, never the model outcome. Exit codes: **0** ready, **1** refused, **3** builds but not ready. 2 is skipped because argparse and the study tools use it for a rejected request. When agentic-mbse is not installed, `check` exits 1 like `generate`, and the line says it is an environment problem, not a model refusal. `generate`'s exit codes do not change and never depend on the screen. *Rejected: a `--json` output now (not asked for; the report is a frozen dataclass, so it is a small later addition).*
- **D7. A screen finding joins a generator refusal by code, through `REASON_MAPPING`, and is shown with both locations.** A `refused` finding "matches the refusal" when its mapped code is among the refusal's codes. This is 2a's agreement relation, not a new one. No field is added to `Diagnostic`, `ReadinessFinding`, `CodeGenerationError` or `RefusalItem`, so the converters in `elaborated_pipeline.py:295-371` are not touched and cannot drop anything. `SubsetDiagnostic` (adapter, codegen-owned) gains `rule_id`, `outcome` and `qualification`, and its file is mapped to the portable `root-N/<path>` referent through the same referent map the generator's load produced. *Rejected: carry the screen's reason on the generator's refusal items (a new field through every converter, for no new information).*
- **D8. The readiness rule. PARKED: owner decision pending (`design-review.md` C1; ledger design_review-F1, F2).** Proposed rule: ready means the generator builds, the destination is clean if it was checked, the screen's verdict is `CLEAR`, and no finding is a `candidate_refusal`; `omitted` and `excluded` findings alone do not withhold ready, and the readiness line carries their counts. The review shows this makes READY reachable on the library-default String loss the screen does not report, and answers the epic's open decision on omissions and exclusions; the authority it would extend is L6 `spec.md:148`. The orchestrator is asking the owner. The rule lives in one pure function, `readiness(report) -> ReadinessVerdict`, which takes the whole report, including the `Prepared` graph. `ReadinessVerdict` is the `Readiness` value plus a tuple of reason strings, already worded; `log_report` prints them in order and never branches on what they say, so a new reason is a change to `readiness` alone (R2-3). Because it sees the whole report, any of the review's options (a)–(c) changes only that function, its tests and the readiness line. Nothing else in the design reads outcomes to decide readiness: the exit code, the readiness line and the tests all call `readiness`. One rule holds whichever way the owner decides: a snapshot source is never ready.
- **D9. The agreement rule moves into `cli/readiness.py` as a pure function; the test helper calls it.** Input: whether the generator builds, its refusal codes, and the reason and mapped code of each refused finding (already mapped by `assess_screen`). Output: no disagreement, or one of `generator_refuses_screen_silent`, `screen_refuses_generator_builds`, `code_unmapped`. It is computed only when the screen was assessed, and it is total: it reads no table and cannot raise. `tests/expectations/subset_profile/disagreements.json` stays the hand-edited oracle and is never read at runtime (2a D3's writer guard already covers `src/`). *Rejected: two copies of the rule, one in tests and one in `src/` (two representations kept in step by hand).*
- **D10. Skew is decided before the adapter is imported.** `subset_screen.py` compares agentic-mbse's `SUBSET_PROFILE_VERSION` with the pin in `_upstream_pins.py`; if they differ the screen is not assessed, naming both versions. Only then does it import the adapter, inside the function, under the catch-all. 2a's `test_nothing_in_src_imports_the_adapter` is replaced by a test that only `subset_screen.py` imports the adapter at run time (type-checking imports aside), and only inside `assess_screen`.
- **D11. The conformance harness's generator half becomes `load_source` + `prepare` + `emit_package`.** It reads the refusal from `Preparation` directly instead of from the log record. Its elaboration spy moves to the new seam: it wraps `elaborate_loaded_extractor`, which the new context builder looks up on `elaborated_pipeline` at call time. The entry-point spy is unchanged. The tripwire stays as it is. A separate test runs `run_codegen` on every case and requires its logged refusal to equal the generator half's.
- **D12. No agentic-mbse change and no version bump.** Everything 2b calls in agentic-mbse exists at the sibling's base. A bump would make all 23 committed v6 envelopes and the consumers' snapshots unloadable through the exact-version check (`snapshot/envelope.py:455-462`) and buy nothing. No gate rerun is required by the `[HARD]` rule. One procedural note: if 2b merges in one coordinated pair with 2a, 2a's D13 `pre_pr` step asks for a receipt naming 2b's final codegen commit, because 2b changes `src/` and `tests/conformance/subset_profile/`.
- **D13. An environment failure after the first write leaves a partial package, as today.** No rollback. With `--overwrite` the old package is already gone at that point. *Rejected: write to a staging folder and swap (protects the old package, but it is new machinery for a disk or permission failure the spec puts out of scope).*
- **D14. Reachability after the first write is decided statically, and nothing covered may be reachable.** The test extends `tests/helpers/subset_profile/site_scan.py`, which already records each raise site's enclosing function (`_FunctionScope`, `Site`): it adds a name-based call closure from `emit_package` over `src/sysml_codegen/` and joins it with the site account. No `public_capability`, `malformed_input`, `unknown` or `relay_plumbing` site may have its enclosing function in the closure, with one allowed site, named in the test with its reason:
  - **Site 338, `validate_constraint_graph_or_raise`** (`generation/errors.py:49`). It stays inside `generate_pipeline_yaml` (`generation/pipeline.py:56`), `generate_registry` (`generation/registry.py:266`) and `build_model_contract` (`contracts/model_contract.py:37`) as defence in depth: each of those functions refuses a bad graph on its own, and `test_module_kind_faildloud.py:277-294` pins that. It cannot fire after the first write in `generate`, because `prepare`'s constraint-names step runs the same function on the same `Prepared.graph`. The test also checks that the constraint-names step calls this function, so the allowance cannot outlive its reason.
  - **Dropped, because nothing pins them:** the nine repeated `_preflight_constraint_names` calls in the writers (`cli/__init__.py:483, 534, 588, 685, 709, 733, 763, 784, 812`) and the schema writer's parameter-field check (D3). `emit_package` takes a `Prepared`, which only `prepare` produces after those checks passed on the same graph. Dropping them cannot change what `generate` accepts or refuses (`design-review.md` Round 2, "m1 and RG-1").
  - A test asserts the graph's `model_dump()` is equal before and after `emit_package` on a corpus case, since the argument above rests on no writer changing the graph (Round 2's suggested guard).

  *Rejected: drop the three renderer guards and delete their test (it removes those functions' own contract to keep a list empty). Rejected: revision 1's exemption table for every re-check (it lists checks nothing pins). Rejected: a runtime trace over the corpus (only proves what the corpus exercises).* Limit: a call made through `getattr` or a stored callable is not followed.
- **D15. Parity evidence lanes.** The licensed default lane runs every criterion test. A byte-identity check compares every package `generate` writes for the corpus's builds cases and the 23 committed snapshots (live and from-snapshot) against a manifest recorded at the base before the refactor. The `execution` lane (124 TEAx tests) runs once before close, because 2b moves the writers. A wheel build is not run: 2b adds modules, no package data, and changes no template.
- **D16. Order inside each command.** `check`: `load_source`, `prepare`, `inspect_destination` (builds and `--output`), `assess_screen`, then `log_report`. `generate`: `load_source`, `prepare`, `inspect_destination` (builds), and the generator section of the report (so a refused run logs its refusal first, as today); then `emit_package` when the model builds and the destination is clean; then `assess_screen` and the rest of the report, under D17's guard. `log_report` renders sections in one fixed order; `generate`'s writing lines fall between the generator section and the screen section. *Rejected: screen before writing in `generate` (a native crash in the screen would then stop a package that builds today).*
- **D17. Nothing after the seal can fail `generate` because of the screen or the report.** Three layers:
  - `assess_screen` turns every `Exception` into "not assessed, screen failed", including mapping and rendering, which happen inside it (`render_finding`'s `ValueError` on a refused finding mapped to `NO_REFUSAL` becomes "not assessed" for the whole screen, naming the finding).
  - `readiness_report`, `readiness` and `log_report` take only already-checked frozen data, read no table, and handle every member of every enum they switch on. Readiness reasons are not an enum: `log_report` prints `ReadinessVerdict`'s reason strings as given (D8). A test builds a report for every combination of generator outcome kind, destination state, screen state, finding outcome and qualification, not-assessed cause and disagreement kind, and requires each function to return without raising.
  - `generate`'s post-seal section runs under a guard that catches any `Exception`, logs one WARNING line ("the screen report could not be produced: …"), and keeps the exit code the emit result set. `check` has no such guard: a report bug there is a `check` bug, and failing loudly is right.

- **D18. `emit_package` owns writer failures and logs today's record for each.** It wraps the writers and the seal with today's two handler blocks, moved from `_generate_package_from_graph` and `run_codegen` (`cli/__init__.py:1402-1410`, `:1411-1425` and `:1266-1281`), in the same order: `CodeGenerationError` logs "Code generation failed: …" with its `generation_refusal` and `constraint_name_safety`; `SysMLParsingError` logs today's parsing record; `OSError` logs "Writing the generated package failed: …" with `PACKAGE_WRITE`; the seal's `PackageSealError`/`OSError` logs "Package sealing failed: …" with `PACKAGE_WRITE`; anything else becomes `unexpected_public_failure` and logs "Code generation failed: …" with the `SI_INTERNAL_DEFECT` diagnostic refusal. Each is one record, byte-identical to today's, and `emit_package` returns the failure. `PreparationStep` gains `EMIT` so the report can name a writer failure. After a failed emit, `generate` still runs `assess_screen` and the rest of the report under D17's guard, and exits 1 as today. A test patches one writer to raise `CodeGenerationError`, `OSError` and a plain `RuntimeError` in turn and checks the single record, message and `extra`, against the base commit's.

## Architecture

```
                ┌────────────────────── read-only (both commands) ───────────────────────┐
source ──► load_source ──► LoadedSource ──► prepare(loaded, package_name) ──► Prepared | Refused
                               │                       │ (builds)
                               │                       └──► inspect_destination(dir) [generate; check --output]
                               └──► assess_screen(loaded) ──► ScreenAssessed | ScreenNotAssessed
                                                   all ──► readiness_report ──► ReadinessReport ──► log_report
                └─────────────────────────────────────────────────────────────────────────┘
generate only, when Prepared and the destination is clean:
        emit_package(prepared, config) ── link check, clear, write, seal   (before assess_screen; D16)
```

- **Data flow.** `ModelSource` is `LiveModels(paths)` or `SnapshotFile(path)`. `load_source` turns it into a `LoadedSource`: a live load (extractor, referents, error flag or load failure) or the snapshot path. `prepare` and `assess_screen` both read the `LoadedSource`; `assess_screen` always runs after `prepare`. `readiness_report` and `readiness` are pure. `emit_package` is the only step given a destination it may change, and it takes the package name and template environment from `Prepared`, not from the config (m2).
- **The steps inside `prepare`, in today's order.** Each has a name in a closed `PreparationStep` enum, carried on `Refused`: construction (load admission, elaboration, projection), generation metadata, exit-point types, constraint names, output paths, registry class names, constraint totality, constraint plan, coverage account, parameter field names (new, D3). The destination step is outside `prepare` but in the same enum, so a `generate` destination refusal names it. A test pins the order.
- **What `check` does not run, and why.** It does not run `emit_package`: the clear, the folder setup, template rendering for schemas, modules, stencils, pipeline, registry, entry points, backlog and tests, smart-regen's stencil reads and backups, and the seal. Rendering is the gap that matters: its raise sites are all `internal_invariant`, so a well-formed model cannot fail there, but a template defect would make `generate` fail with `SI_INTERNAL_DEFECT` where `check` said "builds". That is the stated limit (spec Success Criterion 3), not a model refusal.
- **Where the flow resists clean factoring, and what it costs.**
  - Rendering and writing are fused inside the writers (`cli/__init__.py:477-800`, `entry_point.py:48-145`), so `check` cannot render without writing. D3 accepts that instead of rewriting nine writers.
  - Churn from D1. About a dozen test files import a moved name and need a new import path; some imports are multi-line (`tests/conformance/test_constraint_generation_integration.py:28-37`). Three references monkeypatch a moved name (`tests/unit/test_cli_generation.py:466`, `:507`; `tests/conformance/test_public_package_oracle.py:55`, which patches `_get_template_env`, now in `cli/prepare.py`). A re-export would make those three patches silently dead, so all references are updated, not shimmed. The plan lists the exact import lines.
  - `test_public_diagnostic_totality.py:471-473` also patches a moved name; it joins the three above.
  - **`_generate_package_from_graph` is removed.** Its job is now `prepare_graph` (the preflight steps on a hand-made graph) followed, in production only, by `emit_package`. Its four test files move: `tests/unit/test_cli_generation.py:348, 366, 381, 466, 475, 490`, `tests/conformance/test_constraint_catalog_totality.py:110, 140, 269`, `tests/conformance/test_coverage_preflight.py:67` and the patch at `tests/conformance/test_public_diagnostic_totality.py:471-473`. Every direct call passes a graph a `prepare` step refuses, so each becomes a `prepare_graph` call that asserts the `Refused` value (step, refusal, message). Tests do not build a `Prepared` by hand to reach `emit_package`. The two tree-preservation tests (`test_cli_generation.py:472-490`) then no longer touch a destination; Success Criterion 1's sentinel runs cover that on the live route.
  - Any other test that drives a writer directly with a graph the preflights would refuse loses that refusal when D14 drops the unpinned re-checks, and moves to `prepare_graph` the same way. The plan finds them in Phase 0.
  - `orchestration/elaborated_pipeline.py` gets one extraction of existing lines (D2); its converters are not touched.
- **The snapshot seam.** `assess_screen` on a snapshot source returns "not assessed: snapshots do not carry the screen". That branch is the whole seam; `[SUBSET-SCREEN-SNAPSHOT-CARRIAGE]` replaces it with a reader for whatever the envelope then carries. `sysml-codegen snapshot` and `snapshot/` are not edited.
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

1. `load_source`, `prepare` and `assess_screen` take no destination and perform no file-system write, delete or create. `cli/prepare.py`, `cli/readiness.py` and `subset_screen.py` never import `cli/emit.py`, and `run_check` never calls `emit_package` (import-boundary and call-level tests).
2. The generator outcome and `generate`'s exit code are functions of `load_source`, `prepare`, `inspect_destination` and `emit_package` alone. Nothing from `ScreenAssessment` or the report flows into any of them. The one residual: a native SysIDE crash during the screen, after the seal, ends the process with a non-zero exit on a package that is already complete and sealed (Invariant 3).
3. Nothing after the seal in `generate` raises because of the screen or the report (D17). `assess_screen` never raises an `Exception` (which includes `MemoryError` and `RecursionError`), and never imports the adapter before the version comparison. `KeyboardInterrupt` and `SystemExit` propagate. A native crash inside SysIDE cannot be caught; D16 puts it after the seal.
4. No `public_capability`, `malformed_input`, `unknown` or relay site is reachable from `emit_package`, except two allowed by name (D14): site 338, because `prepare` runs the same check on the same graph first; and the `unexpected_public_failure` relay (`elaboration/elaborate.py`), which D18's handling of an unclassified writer failure calls and which owns no refusal of its own. The second was found in Phase 5; allowing it was the agent's call, ratified by the owner on 2026-10-20 (plan, Phase 5 notes).
5. Every refused `generate` run logs exactly one record carrying a `refusal` extra, and a `check` run logs one only when the model is refused (that record is identical to `generate`'s). Every such record (message and `extra`) is identical to the one at the base commit, with one named exception: D4's stated behaviour change, which has its own test pinning the new record. A `check` run that builds never logs a `refusal` extra.
6. Every package `generate` writes for the corpus's builds cases and the committed snapshots is byte-identical to the base commit's.
7. Readiness is decided only by `readiness(report)`. A snapshot source is never ready. The rest of the rule is D8, parked.
8. `disagreements.json` is never read by `src/`.

## Component Overview

- **`orchestration/elaborated_pipeline.py`.** The live load lines (`:159-173`) move into a non-raising load function; `elaborate_model_paths` becomes that load plus `elaborate_loaded_extractor` (D2).
- **`orchestration/exact_pipeline_context.py`.** A context builder that takes an already-loaded live source (D2).
- **`cli/prepare.py` (new).** `ModelSource`, `LoadedSource`, `load_source`, `PreparationStep`, `Prepared`, `Refused`, `prepare(loaded, package_name)`, `prepare_graph(graph, package_name)` (the steps after construction, for tests that drive a hand-made graph), `_get_template_env`, the six preflights moved from `cli/__init__.py`, and the new parameter-field step. Converts each refusal class to `Refused` once, with today's message prefixes.
- **`cli/emit.py` (new).** `inspect_destination(path)`, `emit_package(prepared, config)`, and the clear, setup, writer and seal functions moved, minus the unpinned re-check calls (D14). Holds today's post-write handler blocks (D18). Returns `None` on success or the failure it logged.
- **`cli/readiness.py` (new).** `ReadinessReport`, `DestinationCheck`, `Readiness` (`READY`, `NOT_READY`, `REFUSED`), `ReadinessVerdict`, `readiness(report)` (D8, the only home of the rule), `Disagreement`, the pure agreement rule (D9), `readiness_report(...)`, `log_report(report)`. Imports no SysIDE and does not import the adapter at run time.
- **`subset_screen.py` (new, beside the adapter).** `ScreenAssessed` (verdict, rendered and mapped findings, unverified checks as not-assessed entries, profile version) and `ScreenNotAssessed` (cause: profile skew with both versions, screen failed with detail, model has parse errors, model did not load, snapshot source). `assess_screen(loaded)`.
- **`subset_profile_adapter.py`.** `SubsetDiagnostic` gains `rule_id`, `outcome`, `qualification`; the module docstring's "nothing on the generate route imports this" is rewritten to D10.
- **`generation/entry_point.py`.** The field-row builder and `refuse_param_field_collisions` (D3).
- **`cli/__init__.py`.** `run_codegen(config) -> bool` keeps its contract and composes D16's order. New `CheckRequest`, `run_check(request) -> ReadinessReport`, `cmd_check` and the `check` subparser.
- **Tests and harness.** `observe.generator_half` and its elaboration spy (D11); the replacement boundary test (D10); the reachability test on `site_scan.py` (D14); the totality test (D17); the criterion tests listed in Validation. Site account row 337's evidence pointer is refreshed to the new call.

## Non-Goals

- Changing what the generator accepts or refuses (RG-1), String policy (RG-2), merges and ADR filing (RG-3).
- Carrying the screen in snapshots, a new envelope format or any change to `sysml-codegen snapshot`. That is `[SUBSET-SCREEN-SNAPSHOT-CARRIAGE]`.
- Rendering templates in `check` (D3), rollback after an environment failure (D13), machine-readable `check` output (D6).
- Any edit to agentic-mbse (D12), or to the refusal converters in `orchestration/elaborated_pipeline.py` (D7).
- Certifying runtime values, handwritten implementations or the TEAx lane beyond D15's regression run.

## Implementation Notes

- **Order of `prepare`'s refusal conversion.** `prepare` keeps the construction ladder (`cli/__init__.py:1218-1259`) and the part of the preflight ladder that covers its own steps; the post-write handling (`:1266-1281`, `:1399-1425`) belongs to `emit_package` (D18). Keep both ladders' behaviour exactly: each refusal class keeps its message prefix and `extra`, and an unclassified exception still becomes `unexpected_public_failure`. Refused types to keep apart: snapshot, readiness, diagnostic, parsing, generation, internal defect. A load failure carried by `load_source` is re-raised into the same ladder, so its message is today's.
- **`Refused` carries the logged form, not the exception.** Fields: `step`, `refusal: Refusal`, `message: str`, and the `constraint_name_safety` value when the refusal is a generation error. `log_report` must log exactly what today's code logs.

```python
@dataclass(frozen=True)
class ReadinessReport:
    generator: Prepared | Refused          # Prepared is shown as "builds"; its payload is not rendered
    destination: DestinationCheck          # NOT_CHECKED | CLEAN | Problem(message)
    screen: ScreenAssessed | ScreenNotAssessed
    disagreement: Disagreement | None      # only when the screen was assessed

def readiness(report: ReadinessReport) -> ReadinessVerdict: ...   # D8 lives here and nowhere else
```

- **Skew tests.** In-process: drop `sysml_codegen.subset_profile_adapter` from `sys.modules` and patch agentic-mbse's `SUBSET_PROFILE_VERSION` to an older and a newer value, so `assess_screen` exercises the real import path both ways. This is how "isolated artifacts" is met; installing two agentic-mbse versions is not attempted.
- **Location mapping.** Screen locations use the referent map the shared load produced. A path the map does not hold keeps its raw string rather than failing the screen.
- **Logger.** `log_report` logs through `logging.getLogger("sysml_codegen.cli")`, so today's records keep their logger name.

## Potential Risks

| Risk | Mitigation |
|---|---|
| Licensed suite slows: about 70 test files call `run_codegen`, which now screens each model | Extraction is under 0.1 s for most fixtures (spike table). Phase 0 times the suite at the base; the plan compares |
| A test asserts on the count or level of log records and breaks on the new report lines | The refusal line is unchanged (Invariant 5). Phase 0 greps for record-count assertions |
| Elaboration changes what the screen extracts (B1) | Success Criterion 4 runs on every 2a case; the fallback is in B1 |
| A test relied on a writer's re-check to refuse a hand-made graph (D14) | Phase 0 finds them; they move to `prepare_graph` |
| Byte identity (B4) fails because moved code finds a file by its own location. The two known cases, `verify.py` (`cli/__init__.py:831`) and the templates folder (`:134`), resolve from `Path(__file__).parent.parent`, which is unchanged for files in `cli/` | The byte-identity check names any file that differs |
| Sentinel runs (Success Criterion 1) are slow: every refused case times five flag sets times two sentinels | Refused cases stop before writing, so each run is a load plus elaboration. If the lane is too slow, share one tree copy per case; do not drop cases or flags |
| SysIDE crashes natively during the screen | Not catchable. In `generate` the package is already sealed; the run loses its report and exits by the crash. Accepted residual (Invariants 2, 3) |

## Integration Strategy

- `generate`'s outcome, exit code, refusal record and written bytes stay as they are, apart from D4's stated behaviour change; it gains report lines. Consumers that parse `generate`'s log for the refusal see the same record.
- `check` is new. The `run-study` skill and L6 are untouched; a later item can point them at `check`.
- 2a's tripwire, reach test, site account and record tests keep running; the harness change in D11 and the boundary test in D10 are the only 2a test changes in kind.
- The CLAUDE.md "Processing Pipeline" section and `docs/architecture/` get a short note on `prepare`/`emit_package` and `check` at close.

## Validation Approach

Every test that runs a live model or captures a snapshot is licensed, and a skip is not a pass (spec). Criterion numbers are the spec's.

- **1 (same refusal, sentinel unchanged).** For every refused 2a case: `check --output` and `generate` under no flags, `--overwrite`, `--preserve-handwritten`, `--smart-regen`, and `--overwrite --preserve-handwritten`, each on a populated and an empty sentinel. Same `Refusal`, same `PreparationStep`, sentinel tree byte-identical with no files added or removed, and exactly one `refusal` record per run.
- **2 (refused generate leaves the destination).** Covered by 1's `generate` half. Environment failures: D13.
- **3 (reachability).** D14's pure test.
- **4 (check equals stored answers).** For every 2a case: generator outcome and codes equal the stored generator answer; findings equal the stored screen answer under 2a's normalization; the computed disagreement equals the case's entry in `disagreements.json` (or its absence).
- **5 (replay).** For the 23 committed snapshots and every builds case captured on the fly: `check --from-snapshot` gives the same generator outcome as live, the screen is not assessed with the snapshot reason, readiness is never ready; `generate --from-snapshot` builds as before (byte identity).
- **6 (snapshots unchanged).** All 23 envelopes load; a refused envelope keeps its message; capture output is byte-identical with the adapter patched to raise and under patched skew.
- **7 (skew).** Both directions, both commands, on a builds case and a refused case: outcome unchanged, both versions named, `check` exits 3 or 1, no `ImportError` text in the output.
- **8 (screen fails).** `extract_subset_facts`, then `evaluate_subset_profile`, then `render_finding` patched to raise, on a builds case, both commands: outcome unchanged, screen not assessed.
- **9 (screen refuses, generator builds).** A builds case with `evaluate_subset_profile` patched to return one refused finding: disagreement `screen_refuses_generator_builds`, `check` exits 3, `generate` still builds.
- **10 (same form).** `generate` and `check --output` on the same cases and destination emit identical report lines (the refusal line, screen lines, disagreement, readiness).
- **11 (tripwire).** `test_tripwire.py` unchanged and passing against D11's generator half.
- **12 (baselines).** Phase 0, below.
- **Parse errors (M2).** A model with a SysIDE error, both commands: refused with today's parsing record; screen not assessed with "the model has parse errors"; no findings, no disagreement.
- **Destination records (M4).** On a builds case with a symlinked destination: `generate` logs one `PACKAGE_WRITE` record and exits 1; `check --output` logs the same text with no `refusal` extra and exits 3. On a refused case with a symlinked destination (D4's behaviour change): both log only the model refusal record, and the sentinel is unchanged.
- **Totality (D17).** The combination test above, plus `generate` on a builds case with `assess_screen`, then `readiness_report`, then `log_report` patched to raise: same bytes written and sealed, exit 0, one WARNING line.
- **Writer failures (D18).** One writer patched to raise `CodeGenerationError`, `OSError` and `RuntimeError` in turn: one refusal record each, message and `extra` equal to the base commit's, exit 1, screen report still printed.
- **Graph unchanged by emit (D14).** `Prepared.graph.model_dump()` equal before and after `emit_package` on a corpus case.
- **Invariants.** Import-boundary and call-level tests (1, 8); byte-identity check (6); step-order test.

## Next-Stage Handoff

**Fixed:** D1–D7 and D9–D18; the module names; `check`'s flags and exit codes; no agentic-mbse edit; the converters in `elaborated_pipeline.py` untouched.

**Parked for the owner:** D8, the readiness rule (`design-review.md` C1 and its options (a)–(c); ledger design_review-F1, F2). Only `readiness()`, its tests and the readiness line wait on the answer; the plan can schedule everything else.

**Phase 0, before any implementation (spec Success Criterion 12, not done in this session).** Licensed commands needed approval in the design session, so the baselines were not re-run. Phase 0 must: re-run both suites at the base with `baseline.md`'s commands (`--all-extras`, license sourced) and record failing test IDs in this folder; record mypy and ruff counts; time the licensed suite; record the byte-identity manifest for D15; list the exact test import lines D1 moves; and find any test that drives a writer directly with a graph the preflights would refuse (D14).

**De-risk first:** D14's call closure on `site_scan.py` (it should come back holding only site 338 once the unpinned re-checks are dropped), then B4's byte identity on one writer moved, then B1 on the 2a corpus with the shared load.

**Open for the plan:** report wording (keep within L6's "CLEAR is relative to the implemented rules"); how the sentinel matrix is parallelized.

**ADR candidates for the owner to file at merge (RG-3):** "destination writes live only in `cli/emit.py`; `prepare` takes no destination" (D1), and the readiness rule once the owner decides D8. No entry is filed by this design.

**Effort:** about 7.5–9 engineer-days for the live half, a guess: shared load and context builder 0.5; prepare/emit split, dropped re-checks and byte identity 1.5–2; screen, report, renderer and totality test 1.75; `check` CLI 0.5; the hoist 0.25; harness and boundary tests 0.75; criterion tests including the reachability test 2–2.5; Phase 0 and lanes 0.75–1.

## Appendix A — Files

| File | Change |
|---|---|
| `src/sysml_codegen/orchestration/elaborated_pipeline.py` | Load lines become a non-raising load function (D2) |
| `src/sysml_codegen/orchestration/exact_pipeline_context.py` | Context builder from a loaded source (D2) |
| `src/sysml_codegen/cli/__init__.py` | Keeps argparse, `cmd_*`, `run_codegen`; adds `CheckRequest`, `run_check`, `cmd_check`, the `check` subparser; loses preflights and writers |
| `src/sysml_codegen/cli/prepare.py` | New (D1, D2, D3) |
| `src/sysml_codegen/cli/emit.py` | New, moved writers without re-checks (D1, D4, D13, D14) |
| `src/sysml_codegen/cli/readiness.py` | New (D5, D8, D9, D17) |
| `src/sysml_codegen/subset_screen.py` | New (D2, D10, D17) |
| `src/sysml_codegen/subset_profile_adapter.py` | `SubsetDiagnostic` fields, docstring (D7, D10) |
| `src/sysml_codegen/generation/entry_point.py` | Field-row builder, `refuse_param_field_collisions`; writer no longer calls the check (D3) |
| `tests/helpers/subset_profile/observe.py` | `generator_half` and its elaboration spy (D11) |
| `tests/helpers/subset_profile/cases.py` | `disagreement` calls the `src/` rule (D9) |
| `tests/helpers/subset_profile/site_scan.py` | Call closure from `emit_package` (D14) |
| `tests/conformance/subset_profile/test_reason_mapping.py` | Boundary test replaced (D10) |
| `tests/expectations/subset_profile/site_account.csv` | Row 337 evidence pointer; any line refresh the account test asks for |
| About a dozen test files importing moved names (including `tests/conformance/test_entry_point_generation.py`); 4 monkeypatches (`tests/unit/test_cli_generation.py:466, :507`, `tests/conformance/test_public_package_oracle.py:55`, `tests/conformance/test_public_diagnostic_totality.py:471-473`) | New import paths and patch targets (Architecture) |
| The four test files using `_generate_package_from_graph` (`test_cli_generation.py`, `test_constraint_catalog_totality.py`, `test_coverage_preflight.py`, `test_public_diagnostic_totality.py`) | Move to `prepare_graph` and assert `Refused` (Architecture, R2-4) |
| New tests | Criteria 1, 3–10; parse errors; destination records; totality; step order; import boundary; byte identity |

---

**Next Step:** owner ruling on D8, then `/_my_plan` (the plan can start everything except `readiness()` before the ruling).
