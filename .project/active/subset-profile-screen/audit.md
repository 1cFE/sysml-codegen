# Audit: Read-only readiness check, live half (EXEC-SUBSET-CONTRACT Item 2b)

**Verdict:** Needs Work
**Audited:** 2026-10-20
**Branch:** `subset-profile-screen` (base `556cbedf`)
**Commit:** `ccb6bd7f` (`src/` and `tests/` unchanged since `8621bac4`)

---

## The Point

A modeler needs one command, `check`, that says before anything is written whether `generate` will build their model, every reason it won't, and every finding the shared subset screen has, marked "not assessed" wherever the screen could not decide. `generate` must report the same findings in the same form. [ORCHESTRATOR]

That answer is only worth having if it is the generator's own answer. The owner ratified that the generator's route alone decides whether `generate` and `check` refuse; the screen only adds findings, and no route gains a refusal keyed on the screen, its version or its failure. [OWNER-ratified 2026-10-20, `briefs/align.md` Q1] RG-1 reserves to the owner any change to what the generator accepts or refuses, "including making a profile mismatch or a screen refusal stop `generate`" (`briefs/align.md`). RG-2 (String policy) and RG-3 (merges, ADR filing) are also the owner's. The product never makes a bad model generate (`.project/product/0003`).

So the work had three obligations: `check` is the generator's route minus the writes; the screen cannot change the generator's answer; and a refused `generate` leaves its destination as it found it, which at the base failed for `PARAM_FIELD_COLLISION`.

## Summary

The refactor is clean and the behaviour claims hold under independent re-measurement. I re-recorded the Phase 0 baselines from the base code in a separate worktree and compared them at HEAD: 0 package-byte differences over 123 subjects, and 1 of 173 refusal records changed, the expected one. `check` cannot write, and nothing after the seal can change `generate`'s exit code.

One defect blocks certification. `generate` now imports the screen's vocabulary module from agentic-mbse before it loads the model, outside any guard. If that module fails to import, `generate` crashes on a model that builds at the base. I reproduced this. It is exactly the "screen failure stops `generate`" case RG-1 reserves to the owner. The fix is small.

## Product Judgment

**This is the right piece of work.** It delivers what the owner asked for: one read-only route shared by both commands, the generator as the only authority, and the one late refusal moved ahead of the first write. The product-lens (audit block in `product-lens.md`) reached the same point independently and found no path where the screen's *result* reaches `prepare`, `emit_package` or the exit code.

**One owner-intent contradiction is still true in the code (product-lens audit-F1, BLOCK; Blocker B1 below).** The screen's *import* can stop `generate`. The product-lens smell "a test passes only because it selects one interpretation" fires here: the skew tests patch only the version string while the real module stays loaded, so Success Criterion 7 is checked off on a narrower proof than its words ("neither command shows a raw `ImportError`").

**Carried, not this audit's to clear: design_review-F1 (the readiness rule, D8, owner).** The shipped interim rule (plan A1) is honest. `readiness()` returns only REFUSED or NOT_READY (`cli/readiness.py:175-209`), so READY is unreachable, a snapshot is never ready, and the library-default String loss can never be called ready. The cost is that `check` cannot exit 0 on any real model, so it cannot yet serve as a pass/fail gate. Shipping it in that state is a merge decision, which RG-3 gives the owner.

## Blockers

**B1. A failure importing the screen's vocabulary module stops `generate` before it builds.**

- **Where.** `run_codegen` imports `cli/readiness.py` as its first statement (`cli/__init__.py:482`), and again through `_destination_check` (`cli/__init__.py:142`, called at `:503`). Both are before the first write and outside D17's guard. `cli/readiness.py:29` imports `Outcome, Qualification, Verdict` from `agentic_mbse.sysml.subset_profile` at module level. That module validates its packaged rule records when it is imported, so it can raise on a bad record as well as on a renamed name.
- **What changed.** At the base nothing on the `generate` route imported that module. I checked this by importing every generator module at HEAD: `agentic_mbse.sysml.subset_profile` is not loaded.
- **Reproduced.** With that module made unimportable (`sys.modules[...] = None`), `run_codegen` on `anonymous-declaration__attribute_usage`: base code returns `True` and writes 23 files; HEAD raises `ModuleNotFoundError`, writes nothing, and logs no refusal record (`build/audit-2b/tools/screen_import_fails.py`). The same import runs on `--from-snapshot`, the license-free route. `check` has the same import (`cli/__init__.py:107`).
- **Why it blocks.** It contradicts the owner-ratified rule that the screen only reports, RG-1's reserved case ("a profile mismatch … stop `generate`"), design Invariant 2 (the exit code depends only on load, `prepare`, the destination check and `emit_package`), and the intent of Success Criteria 7 and 8. The plan recorded this import as an agent decision (Phase 8 notes: "`generate` already needs agentic-mbse, and `readiness` adds only its screen enums"). The reasoning is incomplete: `generate` needs agentic-mbse, but not this module, and this is the module most likely to change between versions.
- **What should change.** `generate` should reach `agentic_mbse.sysml.subset_profile` only inside the screen's guard. For example, the generator section (`log_generator_section`) and `_destination_check` should not need the screen vocabulary, and `readiness` should be imported only inside `_report_after_the_seal`. Add a test that makes that import fail and checks that `generate --models` and `--from-snapshot` still write the same bytes, with the screen reported as not assessed. Then the CLAUDE.md and `02-orchestration.md` sentence "under a guard that cannot change its exit code" becomes true (it is false today; product-lens audit-F2).

## Advisory

Ranked by importance. None blocks certification.

1. **The import-boundary test does not cover `readiness.py`.** Invariant 1 names `prepare.py`, `readiness.py` and `subset_screen.py`; `tests/unit/test_cli_module_boundary.py` checks only the first and last. Today `readiness.py` imports nothing that writes, but nothing stops that changing. Add it to the test.
2. **The read-only destination check lives in the writing module.** `inspect_destination`, `destination_refused` and `DestinationProblem` are in `cli/emit.py:39-62`, so `run_check` imports and calls into `emit` (`cli/__init__.py:135`, `:140-147`). "`check` cannot write" therefore rests on the call-level test (`test_check_command.py:78-86`, which patches `emit_package` and `_write_package` to fail) and the sentinel tests, not on module structure. Both pass, and the design accepted this (D1). Moving the three read-only names next to `prepare` would let the import structure prove it too.
3. **The live construction ladder exists three times.** `elaborate_model_paths` (`orchestration/elaborated_pipeline.py:230-252`), `build_exact_pipeline_context` (`exact_pipeline_context.py:292-314`) and the new `build_exact_pipeline_context_from_live_load` (`:317-341`) each repeat the same pass-through-or-wrap `except` blocks. `build_exact_pipeline_context` has no caller under `src/` any more, only 14 test files. It could become `load_live_models` plus the live-load builder, so the relay rule lives once.
4. **The package name is carried twice and kept in step by a runtime check.** The writers still read `config.package_name` (`cli/emit.py:246, 301, 372, …`). `emit_package` raises `ValueError` if it differs from `Prepared.package_name` (`cli/emit.py:71-75`). Design m2 said `emit_package` takes the name from `Prepared`. Passing it from `Prepared` to the writers would remove the second copy and the guard.
5. **The report calls an environment failure "refused".** A writing `OSError` or a symlinked destination in `generate` prints "Readiness: refused, the generator refuses at step emit/destination" (`cli/readiness.py:182-185`). The spec's Outcomes section says an environment failure "is not a refusal". This is display only; the exit code and record match the base. Wording it as "generate stopped at …" for those two steps would match the spec.
6. **Success Criterion 10's wording no longer matches the report.** It says both commands report "every collected screen finding". Since the report-length ruling (design D5), admitted findings are one count line and omitted or excluded findings are one line per rule. `test_report_form.py` proves both commands print the same lines; the unit test pins the shape. The spec text should be amended to the ruling so the checked box claims what is shipped.
7. **The interim reason points at an internal plan.** A modeler sees "awaiting the owner's decision (plan Phase 10)" (`cli/readiness.py:54`), and CLAUDE.md lists "exit 0 ready" without saying no model can reach it yet. Phase 10 replaces this line, so it only matters if the branch merges before Phase 10.

## Findings Detail

### Plan completion

Phases 0-9 are verified complete against their changes and validation items. Phase 10 is open by design.

- No placeholder code, TODOs, dead functions or leftover aliases in the new modules. Every name defined in `cli/prepare.py`, `cli/emit.py`, `cli/readiness.py`, `subset_screen.py` and the new `elaborated_pipeline.py` functions has a caller. `_generate_package_from_graph` is gone, with no shim.
- The documented deviations (two allowed sites in the reachability test; three R2-4 call sites moved to `run_codegen` instead of `prepare_graph`; the template environment created before the link check; `log_agentic_mbse_missing` moved into `cmd_check`) are each recorded in the plan with a reason. The second allowed site is ratified by the owner (design Invariant 4).
- The Phase 8 agent decision to import `readiness` before writing is the cause of B1.

### Spec conformance

Each checked box was compared with its named test. All named tests exist, ran and passed in my licensed run.

- **SC1 (same refusal, sentinel unchanged).** Verified. `test_refusal_before_first_write.py:91-134`: 169 refused cases × 5 flag sets × populated and empty for `generate`; 169 × 2 for `check --output`, with the `Refused` (step included) equal to `generate`'s. The base records it compares against are the ones I re-recorded independently (all 169 `case:*` entries equal).
- **SC2 (refused `generate` leaves the destination).** Verified by SC1's `generate` half and `test_emit_writer_failures.py`. The partial package after an environment failure is stated in design D13, not tested; the spec asks only that design state it.
- **SC3 (reachability).** Verified. `test_emit_reachability.py` holds the reachable covered sites equal to the two allowed by name, and pins that `prepare` still runs site 338's check. Its limit (no `getattr` or stored-callable calls) is stated.
- **SC4 (`check` equals stored answers).** Verified on 246 cases. One note: since D9 moved the agreement rule into `src/`, the per-case disagreement test compares the rule with itself applied to stored answers. The independent oracle is the hand-edited record, checked by `test_every_recorded_disagreement_appears` (136 entries) and 2a's record test.
- **SC5 (replay).** Verified. `test_check_snapshots.py:96-117` (23 committed snapshots, 77 captured on the fly). `generate --from-snapshot` bytes: my independent manifest compare covers all 23 replays.
- **SC6 (snapshots load and capture as today).** Verified, with one gap in the test. The named test compares capture bytes with and without screen faults at HEAD only. I compared `sysml-codegen snapshot` capture bytes between the base code and HEAD for all 23 committed source sets: identical (`build/audit-2b/capture-{base,head}.json`). So the criterion holds; the test alone does not prove "as today".
- **SC7 (skew).** Met for version-string skew, which is what the named test covers. Not met for a skew that breaks the module's import: B1. The box is checked on the narrower proof.
- **SC8 (screen fails).** Met for the three raise points and the report steps. Not met when the screen's module fails to import: B1.
- **SC9 (screen refuses, generator builds).** Verified. Constructed witness; `check` exits 3 with the disagreement; `generate` writes identical bytes.
- **SC10 (same form).** Verified that both commands print identical report lines on all 246 cases. See Advisory 6 on the word "every".
- **SC11 (tripwire).** Verified. `test_tripwire.py` is unchanged since the base (`git diff 556cbedf HEAD` is empty for it) and passes.
- **SC12 (baselines).** Verified by test ID. My licensed run: 11227 passed, 9 failed, 9 skipped. The 9 failures and 9 skips are exactly the base IDs. All 77 base-passing IDs missing at HEAD are planned: site IDs renamed by the `cli/__init__.py` → `cli/prepare.py` and `_elaborate_model_paths` → `_load_live_models` moves (each has its renamed counterpart passing), the 49 `test_cli_generation.py` tests the plan removed or replaced, and the replaced adapter boundary test. mypy: clean, 91 files. ruff `src/`: clean. ruff `src/ tests/`: 94, as at the base. agentic-mbse is clean at `e268357f`, so no gate receipt is due.
- **Tagged requirements.** The `[INFERRED]` "screen reached only in a way that cannot fail the build" (spec line 95) is not met: B1. Every other tagged requirement is met. Non-goals respected: no agentic-mbse edit, no envelope change, no change to `snapshot/`, no RG-2 decision.

### Design conformance

The code follows D1-D7 and D9-D18, with the deviations the plan records. Additional points:

- **Invariant 2 (exit code depends only on the generator route):** violated by B1's import. Otherwise holds: `run_codegen` returns `isinstance(generator, Prepared)` (`cli/__init__.py:512`), `generator` is never reassigned after `emit_package`, and the only screen work after the seal is inside `_report_after_the_seal`'s `except Exception` (`:515-533`). D17's guard is tested on all three report steps (`test_check_command.py:178-200`).
- **Invariant 1 (`check` writes nothing):** holds. By imports: `prepare.py` and `subset_screen.py` cannot reach `emit` (tested); `readiness.py` does not today but is untested (Advisory 1). By call: `run_check` calls only `inspect_destination` and `destination_refused` from `emit`, both read-only, and the call-level test fails if it reaches `emit_package` or `_write_package`. By behaviour: 338 `check --output` sentinel runs leave populated and empty destinations byte-identical.
- **m2 (`emit_package` takes the package name from `Prepared`):** partly followed (Advisory 4).

### Code integrity

The four new modules are well factored. `prepare.py` has two refusal ladders, one per stage, with no copy between them; `emit.py` owns the writing failures; `readiness.py` keeps the rule in one function and prints reasons as data; `subset_screen.py` turns every failure into a typed "not assessed". The tests test behaviour on real models; the few patches (writer raising, screen raising, `readiness` forced to READY) each target a seam the test is about, not a mock standing in for the thing under test.

- Duplicated relay ladder: Advisory 3.
- Two representations kept in step: Advisory 4.
- Failure honesty: `assess_screen`'s `except Exception` is intended (D17) and turns every failure into a named "not assessed" with the exception type and message. `inspect_destination` catches only `PackageSealError` and `OSError`. No silent fallbacks found.

---

## Certification

**Independent checks run in this audit (licensed, output under `build/audit-2b/`):**

- Base baselines re-recorded from `556cbedf` in a temporary worktree (`src/` there is identical to Phase 0's commit `7cf785f1`; Phase 0's scripts were overlaid). Both equal the implementer's: the package manifest exactly (123 subjects, 3418 files), the refusal records exactly (173 entries).
- At HEAD against my base: package manifest 0 differences. Refusal records: 1 of 173 differs, `destination_link:output-naming__param_field_collision`, from `Package sealing failed: … symlinks are forbidden …` (`PACKAGE_WRITE`) to the model's own `PARAM_FIELD_COLLISION` record, which equals that case's clean-destination record. That is design D4's stated change.
- Destination flags on building models, which the manifest does not cover: for all 77 building cases, generate, then re-generate with `--overwrite --preserve-handwritten`, then with `--smart-regen`, into the same folder. Base and HEAD give identical outcomes and identical file hashes at every step.
- Snapshot capture bytes, base vs HEAD, 23 source sets: identical.
- B1 reproduced on base and HEAD.
- Full licensed codegen suite, mypy and ruff at HEAD.

**Tracking artifacts not updated.** The brief for this audit allows writes only to this file and `build/audit-2b/`, so no plan, spec, epic or CURRENT_WORK checkbox was changed. The verdict is Needs Work in any case. The spec's SC7 and SC8 boxes are checked on a narrower proof than their words (see Spec conformance). One more file changed: the audit command's product-lens step appended its block to `product-lens.md`.

**What this audit cannot certify until Phase 10 lands:** the readiness rule itself (D8); any READY answer or exit 0 on a real model; whether omitted and excluded findings withhold READY; how the library-default String loss is reported (RG-2); and design D8's claim that the owner's answer changes only `readiness()`, its tests and the readiness line.

**Not checked:**

- The TEAx execution lane was not re-run. The branch's receipt (`evidence/execution-lane/README.md`: 124 passed at `556cbedf` and at `8621bac4`, same IDs) covers HEAD's code, since `src/` and `tests/` are unchanged since `8621bac4`. I did not verify the receipt's digests.
- The agentic-mbse all-extras suite was not re-run, because running it would write inside the sibling. agentic-mbse is unchanged and clean at `e268357f`.
- `catf_mfe_d5` was covered only through the package manifest and capture comparison (its sources are in the untracked `spike-snapshot/regen/`); its live `check` was not re-run by hand.
- Whether a realistic agentic-mbse change breaks the `subset_profile` import. B1 was reproduced with a forced import failure.
- The 2a site account's role classifications, which the reachability test trusts.
- A wheel build, and `generate` on Windows or with non-default `--schema-class` or `--pipeline-name`.
- Timings were not re-measured; the plan reports about 3 s added per `catf_mfe` model, after the seal.
