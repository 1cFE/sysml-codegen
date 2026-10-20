# Spec: Read-only readiness check, live half (EXEC-SUBSET-CONTRACT Item 2b)

**Status:** Revision 3, not yet reviewed. Revision 2 was approved by spec review round 2 (2026-10-20); revision 3 applies the scope split below. Implementation in progress (plan Phases 0-3 done, 2026-10-20).
**Owner:** Reid Westwood
**Created:** 2026-10-20
**Complexity:** HIGH
**Branch:** `subset-profile-screen` (from `main` `0c4b0281`; agentic-mbse sibling worktree at `main` `e268357f`)
**Effort:** about 6.5–9 engineer-days, and this is a guess. The live half is 6–8 days, a rough guess the snapshot spike made without a breakdown (`spike-snapshot/FINDINGS.md` §6). Reporting the screen as not assessed on replay is 0.5–1 day (same table, option 3). The epic's 6–10 days covered both halves and was never re-examined.

> **Revision 3 (2026-10-20): snapshot carriage split out.** The snapshot spike (`spike-snapshot/FINDINGS.md`) fired the split trigger this spec recorded. By orchestrator ruling (2026-10-20), carrying the screen in snapshots moves to backlog row `[SUBSET-SCREEN-SNAPSHOT-CARRIAGE]` (`.project/backlog/BACKLOG.md`). 2b ships the live half with option 3: the envelope stays v6, and replay reports the screen as not assessed, so replay is never ready. Generator decisions on replay still equal live. What changed:
>
> - **Success Criteria rewritten for option 3:** 5 (replay matches live on the generator outcome; the screen is not assessed on replay), 6 (snapshots load and capture exactly as today) and 7 (the capture clause). The screen-failure criterion now covers `generate` and `check` only, since capture does not run the screen.
> - **Dropped, moved to the backlog row:** the old Success Criterion 8 (snapshot-vs-build profile skew), and the new-format half of the old 6 (refusing an unsupported format by name with a recapture message). The old 9–13 are now 8–12.
> - **Carriage options and the spike summary** are now a short pointer in Open Questions. The split trigger is recorded as fired.
> - **Website question:** off 2b's path, because no new format ships in 2b. The owner quote stays.
> - **Epic link:** the epic's "supported upgrades" and full snapshot-authority scope are now partly in the backlog row. The agentic-mbse epic file needs updating at close, not now.
> - **Effort** added to the header, from the spike's guess.
>
> **Revision 2 (2026-10-20), against `spec-review.md` Round 2 (Approve with minor fixes):** R2-1 live-model criteria listed by number; R2-2 the reachability guard names its classes and exempts `environment`; R2-3 baselines cite 2a's record; R2-4 plan-build example is `PREDICATE_FUNCTION_NAME_COLLISION`; R2-5 design asks the owner before any new format if the website is unlocated.
>
> **Revision 1 (2026-10-20), against `spec-review.md` (verdict Revise):** one public late refusal, not three; outcome words defined; skew no longer stops `check`; no refusal keyed on the profile version; owner quote split from its reading; conditions for "not RG-1" stated; should-fix and minor rewrites. Full notes are in git history for this file.
>
> Orchestrator rulings are graded `[INFERRED]` with "(orchestrator ruling, 2026-10-20)". They are not owner intent.

---

## Problem

Modelers have no way to ask "will this model generate?" without running `generate`. And one public refusal in `generate` fires after it has started writing. Item 2a made the shared subset contract (the screen in agentic-mbse `sysml/subset_profile.py`) agree with what the generator does. But nothing on the generate route uses it, and snapshots cannot carry it. Paths below are under `src/sysml_codegen/` and were read at `0c4b0281`.

- **One public refusal happens after writing starts.** Most preparation checks run before the first write. The first write is the `--overwrite` clear (`_clear_output_directory`, `cli/__init__.py:1346-1348`), or folder creation (`_setup_output_directories`, `:1351`) when `--overwrite` is not set. One public refusal fires later: `PARAM_FIELD_COLLISION` (`generation/entry_point.py:38`), in `_generate_entry_points` at step 8 (`cli/__init__.py:1376`). 2a's site account classifies it `public_capability`, with the witness case `output-naming__param_field_collision` (`tests/expectations/subset_profile/site_account.csv` row 337). The other raises inside rendering are internal checks no well-formed model reaches (`internal_invariant`). They include `MODULE_KIND_UNRENDERABLE` (`modules.py:455`, row 350; `stencils.py:61`, row 380) and the repeated metadata checks (`stencils.py:54,67,131,264`, `test_gen.py:61,77`, rows 379, 381-385). Each is guarded by a check that already runs before the first write, for example `_preflight_generation_metadata` (`cli/__init__.py:253-276`). A refused `generate` that reaches step 8 leaves a partial package. With `--overwrite`, the old package is already gone by then (`cli/__init__.py:1408-1415` records this). A read-only check that stops before writing would miss this refusal.
- **Public refusals come before it in today's order.** The link-free check (`:1326`), the constraint plan build (`:1337`) and the coverage preflight (`:1343`) all run before the clear. The plan build can raise public refusals of its own (for example `PREDICATE_FUNCTION_NAME_COLLISION`, `modules.py:133`, site account row 341, `public_capability`, reached through `compile_shared_predicates` from `constraint_plan.py:53`). So a model with two faults reports one of those first today. Moving `PARAM_FIELD_COLLISION` earlier could change which code it reports first.
- **The generator stops at its first refusing stage.** A modeler fixes one problem per run. The screen can report every independent finding at once, but it is not called on the generate route (`subset_profile_adapter.py:11`; pinned by `tests/conformance/subset_profile/test_reason_mapping.py:186-195`). The adapter raises `ImportError` at import time when the installed agentic-mbse profile differs from the pin (`subset_profile_adapter.py:29-34`).
- **Snapshots cannot reproduce the screen.** A v6 snapshot holds only the sealed elaborated graph: no parse tree and no screen facts. Refused models never seal, so live and replay already agree on accept or refuse. They cannot agree on the screen's findings for a model the generator builds. 2b does not fix this. It makes replay say so, and leaves carriage to `[SUBSET-SCREEN-SNAPSHOT-CARRIAGE]`.
- **Versions are brittle.** The loader requires both package versions to match exactly (`snapshot/envelope.py:455-462`). Any version bump makes all 23 committed v6 envelopes unloadable: 22 `instance_graph_snapshot.json` fixtures plus `tests/fixtures/study_station/station.snapshot.json`, which the study-layer tests depend on. That is why 2a pinned `SUBSET_PROFILE_VERSION` instead of bumping it (ADR 0016 pattern).

Governing obligations carried into this item:

- **[INHERITED: epic, owner gates 2026-10-18]** RG-1: any change to what the generator accepts or refuses needs owner approval. RG-2: String metadata policy is the owner's. RG-3: merges, PRs and ADR filing are the owner's.
- **[INHERITED: P-0003]** "we do NOT create workarounds to accept bad models -- we follow what KerML, SysMLv2 and SysIDE support".

## Outcomes

These are the words the criteria use. They name outcomes only. Output format and exit codes stay with design.

- **Refused:** the generator's own route refuses the model, with a refusal code. `generate` writes nothing (see Success Criterion 2); `check` writes nothing ever.
- **Builds:** the generator's own route accepts the model. For `generate`, the package is written and sealed. For `check`, nothing is written; "builds" is its prediction.
- **Ready:** `check`'s strongest answer. The model builds, every screen finding was assessed, no finding is a `candidate_refusal`, and there is no disagreement. Anything else that builds is **not ready**. Not ready is not a refusal. Whether an omission or exclusion finding alone makes a model not ready stays open (see Open Questions).
- **Not assessed:** a screen finding, or the whole screen, that could not be evaluated. The report names the reason: profile skew (with both versions), the screen raised, a fact was missing, or the input is a snapshot, which does not carry the screen. A not-assessed finding is never treated as passing.
- **Disagreement:** the generator's outcome and the screen's reasons do not match under the reason mapping (`REASON_MAPPING`). `check` and `generate` compute this for any model. It is reported beside the outcome. It never changes whether the model is refused or builds.
- **Environment failure:** writing or sealing fails because of the disk, permissions or the OS, or because the seal-time link check finds a symlink in the written tree (`PACKAGE_WRITE` from an `OSError` or from sealing, `cli/__init__.py:1416-1430`, `_seal_package` at `:802-847`, link check `contracts/seal.py:52`). This is not a refusal. It cannot be detected before writing.

## Success Criteria

Criteria 1, 4, 5, 6, 8, 9, 10 and 11 run live models or capture snapshots, so they run on the licensed lane (`SYSIDE_LICENSE_KEY`), as does any other criterion design chooses to test on a live model. A skipped test there is not a pass. Criterion 3 (the reachability guard) may not need a live model.

- [ ] For every refused case in 2a's conformance corpus, including `output-naming__param_field_collision`, `check` and `generate` refuse with the same code at the same preparation stage. After each run, a sentinel destination (pre-populated files, and separately an empty folder) is byte-identical, with no files added or removed. This holds with no flags and with each destination-changing flag: `--overwrite` (the only flag that deletes, `cli/__init__.py:70`), `--preserve-handwritten` and `--smart-regen` (both read the destination and write backups, `cli/__init__.py:621-660`, `preservation.py:223-230`). Design lists any flag combinations it also tests.
- [ ] A refused `generate` leaves its destination as it found it: no model refusal fires after the first write. Environment failures are outside this criterion. Design states what an environment failure after the first write leaves behind (a partial package, as today, or a rollback).
- [ ] A test fails if a raise site that the 2a site account classifies as `public_capability`, `malformed_input` or `unknown`, or a relay of one of those, becomes reachable after the first write. Sites classed `environment` are exempt, because they are environment failures: the seal-time link check (`contracts/seal.py:52`, site account row 36), which `_seal_package` re-runs over the written tree (`cli/__init__.py:822`, `:839`), stays after the first write. Design picks how the test decides reachability. If an internal check does fire after the first write, it leaves the destination as an environment failure would. That is a stated limit, not a goal.
- [ ] On every 2a case, `check` reports the generator outcome equal to the stored generator answer, and screen findings equal to the stored screen answer. `check` computes disagreements itself, from the generator's code and the screen's reasons through `REASON_MAPPING`. The recorded entries in `tests/expectations/subset_profile/disagreements.json` are the test oracle and are never read at runtime. Every recorded disagreement appears as a disagreement.
- [ ] For every committed snapshot fixture and every corpus case that builds, `check` from a snapshot reports the same generator outcome as `check` on the live model. On replay, the whole screen is reported as not assessed, with the reason that snapshots do not carry the screen, and the outcome is never ready: a model that builds is not ready. `generate --from-snapshot` reports the screen as not assessed for the same reason and builds or refuses exactly as it does today.
- [ ] Snapshots load and capture exactly as they do today. The envelope stays v6, so all 23 committed envelopes load without recapture, and a snapshot the loader refuses today is still refused with the same message. `sysml-codegen snapshot` does not run the screen, so its output for a given model is byte-identical to today's, with or without profile skew and with the screen patched to raise.
- [ ] Profile skew between the installed agentic-mbse and the pin, in both directions (newer and older), leaves `check` and `generate` on the generator route's answer. Both mark the screen findings not assessed, name both versions, and never report the model as ready. A model that builds gets a not-ready outcome from `check`, with an exit status distinct from both ready and refused. Neither command shows a raw `ImportError`. Tested on isolated artifacts.
- [ ] If the screen fails while `generate` or `check` runs (it raises, or a fact is missing), the refused-or-builds outcome is unchanged, and the affected findings are not assessed. A test patches the screen to raise and checks this on a corpus case that builds, for both commands.
- [ ] When the screen refuses but the generator builds, `generate` and `check` report a disagreement, and `check` reports not ready. A constructed witness tests this, because 2a's corpus has no such case (for example, a test-only screen change that refuses a case that builds).
- [ ] `generate` and `check` both report every collected screen finding alongside the generator's own outcome, in the same form.
- [ ] 2a's tripwire (`test_tripwire.py`, the generator half with the screen patched to raise) still passes.
- [ ] Both repositories' tests, mypy and ruff are no worse than the recorded baselines. 2a recorded them in `c381fb00:.project/active/subset-profile-conformance/evidence/baseline.md` (failing test IDs, exact commands, static-check counts) and `c381fb00:.project/active/subset-profile-conformance/audit.md` line 262. `baseline.md` lists 10 codegen failures; the audit says 9, because one now passes (it does not name which). For agentic-mbse the comparison set is the 5 IDs in the "all extras" section. Because `main` has moved since 2a, design re-runs both suites at 2b's base, with the commands in `baseline.md` (including `--all-extras` and the license key), and records the failing test IDs in this item's folder before implementation starts. Those IDs become the baseline, so the 10-versus-9 gap is settled by test ID, not by count. A fresh gate receipt exists if agentic-mbse `src/agentic_mbse/sysml/` or `errors.py` changed.

Moved to `[SUBSET-SCREEN-SNAPSHOT-CARRIAGE]`, one line each:

- Replay reporting the same screen findings as live (the old Success Criterion 5's "each finding matches" branch).
- Refusing an unsupported envelope format by name with a recapture message, and what "supported" means after a format change (the new-format half of the old Success Criterion 6).
- Snapshot-vs-build profile skew: a snapshot recording its profile version, and loading with findings not assessed when it differs (the old Success Criterion 8). A v6 envelope records no profile version.

## Known Requirements

- **[INHERITED: epic Item 2b scope 2]** `generate` and `check` share one read-only preparation path: admission, facts and capability assessment, elaboration, projection, generation metadata/type/name/collision/totality checks, body and plan compilation, and coverage checks. Destination mutation and emission stay outside it.
- **[INFERRED]** (from review L3-2) `check` runs every step `generate` runs except writing to the destination, or names each step it skips and why. A skipped step is a place where `check` can say "builds" and `generate` can still fail; the named list makes that visible.
- **[INHERITED: epic Item 2b scope 2]** `check` writes no generated package and clears no folder.
- **[INHERITED: epic Item 2b scope 2]** Destination and environment checks that need separate assessment are stated. Today these are the symlink check on the output tree (`contracts/seal.py:48`) and the `--overwrite`, `--preserve-handwritten` and `--smart-regen` handling. There is no TEAx, permission or existing-package check.
- **[INHERITED: epic Item 2b scope 1, principle 5]** Shared decisions run where their facts exist, and independent findings are collected before any output is written. Occurrence facts exist only after elaboration, so not all facts are assumed to exist before it. A finding whose facts are missing is not assessed, never passing.
- **[INHERITED: epic Item 2b scope 3]** Snapshot authority, certifiability, receipts and version checks account for the new policy. A snapshot without the required facts is assessed, rejected or upgraded, never silently screened as if it were live. In 2b this is met only by its last clause: replay reports the screen as not assessed (Success Criterion 5). Sealing the screen, receipts that carry it, and upgrades move to `[SUBSET-SCREEN-SNAPSHOT-CARRIAGE]` (orchestrator ruling, 2026-10-20).
- **[INHERITED: epic principle 3; 2a spec]** The generator's own route stays runnable with the screen switched off, so conformance keeps comparing two independent answers.
- **[INHERITED: epic Item 2b scope 2]** The readiness claim is bounded. It does not certify runtime behavior or handwritten implementation correctness.
- **[INFERRED]** `check`'s wording does not contradict L6's ("CLEAR is relative to the implemented rules", agentic-mbse `subset_profile.py:23`).
- **[INFERRED]** (agent decision, 2026-10-20; ratified by owner at orchestration Align, 2026-10-20) The generator's own route alone decides whether `generate` and `check` refuse. Screen findings are added to the report. When the screen refuses but the generator builds, the result is reported as a disagreement and generation proceeds. Reason: making the screen a gate would change what `generate` accepts wherever the screen is wrong, which is an RG-1 change. 2a's corpus has no such case (`tests/expectations/subset_profile/disagreements.json`: 0 `screen_refuses_generator_builds` entries out of 136), but models outside the corpus are unchecked.
- **[INFERRED]** (agent decision, 2026-10-20, from review L3-4; not owner-ratified) Every disagreement is reported, including the kind where the generator refuses and the screen says nothing. That kind is 129 of the 136 recorded entries, so most refusals will carry one. It is reported because L6 says the screen's clear answer is relative to its rules, and hiding the gap would overstate the screen. The report keeps this kind distinct from the screen-refuses-generator-builds kind. It changes no outcome.
- **[INFERRED]** (orchestrator ruling, 2026-10-20, derived from the owner-ratified line above; review L1-2, L1-5) Profile skew between the installed agentic-mbse and the pin never changes the refused-or-builds outcome of `check` or `generate`. This narrows the Epic Strategy line "keep temporary skew fail-closed" (agent-grade strategy): fail-closed now means the screen's findings are never trusted under skew, not that the build or the check stops. Making skew stop `generate` would be a new refusal and would need RG-1 approval; it is not taken here.
- **[INFERRED]** (orchestrator ruling, 2026-10-20, same derivation; review L1-3) No new refusal is keyed on the subset profile version, on any route. 2b changes no envelope format. If `[SUBSET-SCREEN-SNAPSHOT-CARRIAGE]` does, refusing a snapshot by format version is an input-compatibility refusal about the file, not a change to what models the generator accepts (ADR 0005 is the v5→v6 precedent, `.project/adr/0005-exact-identity-elaboration-replaces-string-resolution.md` lines 49, 56). The existing package-version equality checks (`snapshot/envelope.py:455-462`) stay as they are.
- **[NEED]** (owner, 2026-10-20, orchestration Align, asked whether anyone needs snapshots saved before 2b to keep loading): "the only thing to check is the artifacts on our website. but those should be stand-alone".
- **[INFERRED]** (follow-up to the quote above, revision 3) No new snapshot format ships in 2b, so 2b breaks no saved snapshot and the website check is not on 2b's path. The question of where the website lives is still with the owner (asked by the orchestrator 2026-10-20, unanswered). It moves with `[SUBSET-SCREEN-SNAPSHOT-CARRIAGE]`, together with the agent reading that consumers' old snapshots need not keep loading, and the recorded cost that dc3 (`exploration/ac_dc_baseline/dc3_baseline.snapshot.json`, `exploration/ac_dc_baseline/studies/20261013-study-ready-baseline/snapshot.json`) and fusion-tea (three `recaptured.snapshot.json` under `.project/active/`) would recapture, with `integrate` reporting `snapshot-drift` until they do (`study/integrate.py:1188-1198`). That row asks the owner before committing any new format if the website is still unlocated (review R2-5).
- **[INFERRED]** (orchestrator ruling, 2026-10-20, on review L2-1) Moving `PARAM_FIELD_COLLISION` ahead of the first write changes when `generate` refuses, not what it refuses, so it is not RG-1. Two conditions hold it there. First, a model with several faults reports the same first refusal code as today. Second, a refused `--overwrite` run leaves the existing package in place. That is intended: a consumer that reads "package present" as "this run built" will see the old, still-sealed package after a refusal.
- **[INFERRED]** A model with a `candidate_refusal` finding is never reported ready by `check`. The finding is shown whatever RG-1 later decides.
- **[INFERRED]** (from review L3-7) The generate route reaches the screen adapter only in a way that cannot fail the build, including the import-time `ImportError` on skew (`subset_profile_adapter.py:29-34`). `test_nothing_in_src_imports_the_adapter` (`tests/conformance/subset_profile/test_reason_mapping.py:186-195`) is replaced by a test that pins the new boundary, not deleted.
- **[HARD]** A change to agentic-mbse `src/agentic_mbse/sysml/` or `errors.py` needs a gate rerun and a new receipt (`scripts/subset_profile/codegen_suite.py`; D13).

## Non-Goals

- Changing what the generator accepts or refuses. Out of scope because it is RG-1. This includes RG1-12 (`[ITEM-OWNED-PART-REFUSED]`); `check` reports whatever the generator does at the time.
- Carrying the screen in snapshots: a new envelope format, sealed findings or facts, profile version in the envelope, recapture, and upgrades. Out of scope because the spike fired the split trigger; it is `[SUBSET-SCREEN-SNAPSHOT-CARRIAGE]`.
- Deciding String metadata policy (RG-2).
- Filing the staged ADR 0001, 0012 and 0016 and P-0001 amendments (RG-3).
- Editing consumer repositories (dc3, fusion-tea).
- Detecting unknown silent losses in general. This is a recorded limit of the epic, not an acceptance gate.
- Certifying runtime values or the TEAx execution lane.

## Open Questions / Deferred to design

- **Snapshot carriage: decided for 2b, rest split out.** The spike (`spike-snapshot/FINDINGS.md`) fired the split trigger: sealing findings or facts costs 4.5–6 days, past the estimate, and the format choice waits on owner input. 2b keeps v6 and reports the screen as not assessed on replay (option 3). Spike summary for the backlog row: the screen needs only `SubsetFacts`, which round-trip through JSON exactly on 269 subjects, including license-free replay. Locations need portable source names, and anonymous elements must be compared by location. Option 3's cost is that every license-free replay is not ready, including the 19 committed snapshots with no findings. The option analysis lives in the spike and `[SUBSET-SCREEN-SNAPSHOT-CARRIAGE]`.
- Whether to bump the agentic-mbse version. With v6 kept, a bump makes all 23 committed envelopes and the consumers' snapshots unloadable through the exact-version check. Design decides and states that cost if it bumps.
- **How the late refusal moves ahead of the first write.** Leading option: move the field-collision check ahead of the first write, as `_preflight_registry_class_names` did for registry collisions (`cli/__init__.py:279-298`, whose docstring describes this fix). To keep the first reported code, it would sit after the coverage preflight (`:1343`) and before the clear (`:1346`). The other option is to render everything in memory, then write. What that would buy: rendering's internal checks would also fire before the first write, and `check` could run the template rendering without writing. The cost is memory and edits to `_generate_modules`, `_generate_stencils` and smart-regen backups (`preservation.py:223-230`).
- The `check` CLI: its inputs (`--models`/`--from-snapshot`, and an optional destination for the destination checks), its exit codes (which must tell ready, not ready and refused apart) and its output format.
- How a `SubsetDiagnostic` joins a generator refusal in the report (2a left this to 2b).
- Whether an omission or exclusion finding, on its own, makes a model that builds not ready, and what `check` says for it.
- The codegen `execution` lane (124 TEAx tests), from-snapshot generation, and a wheel build with packaged cases, which 2a did not assess. Design states which of these the parity evidence runs.

---

## Related Artifacts

- **Epic:** agentic-mbse `.project/backlog/epic_executable-subset-contract.md`, Item 2b, with Design principles, Epic Strategy and Risks. After the split, part of Item 2b scope 3 (snapshot authority, certifiability, receipts) and the epic's "supported upgrades" criterion live in `[SUBSET-SCREEN-SNAPSHOT-CARRIAGE]`. The epic file needs updating to say so at 2b's close; it is not edited now.
- **Split-off item:** `.project/backlog/BACKLOG.md`, `[SUBSET-SCREEN-SNAPSHOT-CARRIAGE]`
- **Snapshot spike:** `.project/active/subset-profile-screen/spike-snapshot/FINDINGS.md`
- **Prior item (2a):** `c381fb00:.project/active/subset-profile-conformance/{spec,design,plan,audit}.md`, `adr-0016-amendment.md`, `rg1-recommendations.md`, `rg2-string-policy.md`
- **ADRs:** 0005 (exact-identity elaboration; its no-migration clause covers v5→v6 only), 0011 (projection boundary), 0016 (API version pins); product P-006
- **Orchestration Align:** `.project/active/subset-profile-screen/briefs/align.md`
- **Spec review:** `.project/active/subset-profile-screen/spec-review.md`
- **Handoff:** `/tmp/handoff-20261020-140211.md`
- **Product lens:** `.project/active/subset-profile-screen/product-lens.md`
- **Design:** `.project/active/subset-profile-screen/design.md` (to be created)

---

**Next Steps:** `/_my_design`.
