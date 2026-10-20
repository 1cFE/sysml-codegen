# Spec: Read-only readiness check and snapshot authority (EXEC-SUBSET-CONTRACT Item 2b)

**Status:** Draft (revision 1)
**Owner:** Reid Westwood
**Created:** 2026-10-20
**Complexity:** HIGH
**Branch:** `subset-profile-screen` (from `main` `0c4b0281`; agentic-mbse sibling worktree at `main` `e268357f`)

> **Revision 1 (2026-10-20), against `spec-review.md` (verdict Revise).** Written by a spec-stage agent; the original author session was not available. What changed and why:
>
> - **Late refusals corrected (L1-1, L2-2, L4-1).** Only one public refusal fires after the first write, not three. Re-checked against `site_account.csv` and `cli/__init__.py`. Success Criteria 1 and 2 now cover that one refusal, exclude disk and OS errors, and add a guard for internal checks. The render-before-write question now leads with moving the one check ahead of the first write.
> - **Outcome words defined (L5-1).** A new "Outcomes" list says what `refused`, `builds`, `ready`, `not ready`, `not assessed` and `disagreement` mean. "Clean" and "stops" are gone. The criteria use only these words.
> - **Skew no longer stops `check` (L1-2, L1-5).** Under skew, `check` behaves like `generate` (orchestrator ruling 1). The narrowing of the epic's "keep temporary skew fail-closed" line is stated.
> - **No refusal keyed on the profile version, on any route (L1-3).** A snapshot is refused only by envelope format, as input compatibility (orchestrator ruling 2). "Supported snapshot" is defined (L1-4).
> - **Success Criterion 4 holds under every carriage option (L3-1).** A third carriage option, sealing the screen's facts, is listed (L2-4). A split trigger for the snapshot half is recorded (L2-3, orchestrator ruling 3).
> - **Owner-quote split (L1-6).** The owner's words stay `[NEED]`. The reading of them is `[INFERRED]`. The consumer recapture cost is recorded as a consequence (orchestrator finding 4). The website check may end as "unchecked" (ruling 5).
> - **Conditions for "not RG-1" stated (L2-1, ruling 6).** Same first refusal code as today. A refused `--overwrite` run leaves the old package in place, on purpose.
> - **Should-fix rewrites (L3-2 to L3-5, L3-7):** how deep `check` goes, which flags the sentinel tests use, `check` computes disagreements itself, the licensed-lane rule, and replacing the adapter-boundary test.
> - **Minor (L1-7, L1-8):** 23 committed snapshots, not 22. ADR 0005's citation is narrowed to v5→v6.
>
> Numbering: the new guard criterion is Success Criterion 3, so the review's criteria 3 to 12 are now 4 to 13. The review's 6 (installed skew) is now 7, and its 7 (snapshot skew) is now 8.
>
> Orchestrator rulings are graded `[INFERRED]` with "(orchestrator ruling, 2026-10-20)". They are not owner intent.

---

## Problem

Modelers have no way to ask "will this model generate?" without running `generate`. And one public refusal in `generate` fires after it has started writing. Item 2a made the shared subset contract (the screen in agentic-mbse `sysml/subset_profile.py`) agree with what the generator does. But nothing on the generate route uses it, and snapshots cannot carry it. Paths below are under `src/sysml_codegen/` and were read at `0c4b0281`.

- **One public refusal happens after writing starts.** Most preparation checks run before the first write. The first write is the `--overwrite` clear (`_clear_output_directory`, `cli/__init__.py:1346-1348`), or folder creation (`_setup_output_directories`, `:1351`) when `--overwrite` is not set. One public refusal fires later: `PARAM_FIELD_COLLISION` (`generation/entry_point.py:38`), in `_generate_entry_points` at step 8 (`cli/__init__.py:1376`). 2a's site account classifies it `public_capability`, with the witness case `output-naming__param_field_collision` (`tests/expectations/subset_profile/site_account.csv` row 337). The other raises inside rendering are internal checks no well-formed model reaches (`internal_invariant`). They include `MODULE_KIND_UNRENDERABLE` (`modules.py:455`, row 350; `stencils.py:61`, row 380) and the repeated metadata checks (`stencils.py:54,67,131,264`, `test_gen.py:61,77`, rows 379, 381-385). Each is guarded by a check that already runs before the first write, for example `_preflight_generation_metadata` (`cli/__init__.py:253-276`). A refused `generate` that reaches step 8 leaves a partial package. With `--overwrite`, the old package is already gone by then (`cli/__init__.py:1408-1415` records this). A read-only check that stops before writing would miss this refusal.
- **Public refusals come before it in today's order.** The link-free check (`:1326`), the constraint plan build (`:1337`) and the coverage preflight (`:1343`) all run before the clear. The plan build can raise public refusals of its own (for example `PREDICATE_COMPILE_FAILED`, relayed at `modules.py:186`, site account row 343). So a model with two faults reports one of those first today. Moving `PARAM_FIELD_COLLISION` earlier could change which code it reports first.
- **The generator stops at its first refusing stage.** A modeler fixes one problem per run. The screen can report every independent finding at once, but it is not called on the generate route (`subset_profile_adapter.py:11`; pinned by `tests/conformance/subset_profile/test_reason_mapping.py:186-195`). The adapter raises `ImportError` at import time when the installed agentic-mbse profile differs from the pin (`subset_profile_adapter.py:29-34`).
- **Snapshots cannot reproduce the screen.** A v6 snapshot holds only the sealed elaborated graph: no parse tree and no screen facts. The loader refuses unknown keys (`snapshot/envelope.py:340-343`). Refused models never seal, so live and replay already agree on accept or refuse. They cannot agree on the screen's non-blocking findings (omissions, exclusions, candidate refusals) for a model the generator builds. The snapshot also records no profile version, so profile skew against a snapshot is invisible.
- **Versions are brittle.** The loader requires both package versions to match exactly (`envelope.py:455-462`). No upgrade path exists. Any version bump makes all 23 committed v6 envelopes unloadable: 22 `instance_graph_snapshot.json` fixtures plus `tests/fixtures/study_station/station.snapshot.json`, which the study-layer tests depend on. That is why 2a pinned `SUBSET_PROFILE_VERSION` instead of bumping it (ADR 0016 pattern).

Governing obligations carried into this item:

- **[INHERITED: epic, owner gates 2026-10-18]** RG-1: any change to what the generator accepts or refuses needs owner approval. RG-2: String metadata policy is the owner's. RG-3: merges, PRs and ADR filing are the owner's.
- **[INHERITED: P-0003]** "we do NOT create workarounds to accept bad models -- we follow what KerML, SysMLv2 and SysIDE support".

## Outcomes

These are the words the criteria use. They name outcomes only. Output format and exit codes stay with design.

- **Refused:** the generator's own route refuses the model, with a refusal code. `generate` writes nothing (see Success Criterion 2); `check` writes nothing ever.
- **Builds:** the generator's own route accepts the model. For `generate`, the package is written and sealed. For `check`, nothing is written; "builds" is its prediction.
- **Ready:** `check`'s strongest answer. The model builds, every screen finding was assessed, no finding is a `candidate_refusal`, and there is no disagreement. Anything else that builds is **not ready**. Not ready is not a refusal. Whether an omission or exclusion finding alone makes a model not ready stays open (see Open Questions).
- **Not assessed:** a screen finding, or the whole screen, that could not be evaluated. The report names the reason: profile skew (with both versions), the screen raised, a fact was missing, or the snapshot does not carry what the screen needs. A not-assessed finding is never treated as passing.
- **Disagreement:** the generator's outcome and the screen's reasons do not match under the reason mapping (`REASON_MAPPING`). `check` and `generate` compute this for any model. It is reported beside the outcome. It never changes whether the model is refused or builds.
- **Environment failure:** writing or sealing fails because of the disk, permissions or the OS (`PACKAGE_WRITE` from an `OSError` or from sealing, `cli/__init__.py:1416-1430`, `_seal_package` at `:802-847`). This is not a refusal. It cannot be detected before writing.

## Success Criteria

Criteria 1, 3 and 4 run live models, so they run on the licensed lane (`SYSIDE_LICENSE_KEY`). A skipped test there is not a pass.

- [ ] For every refused case in 2a's conformance corpus, including `output-naming__param_field_collision`, `check` and `generate` refuse with the same code at the same preparation stage. After each run, a sentinel destination (pre-populated files, and separately an empty folder) is byte-identical, with no files added or removed. This holds with no flags and with each destination-changing flag: `--overwrite` (the only flag that deletes, `cli/__init__.py:70`), `--preserve-handwritten` and `--smart-regen` (both read the destination and write backups, `cli/__init__.py:621-660`, `preservation.py:223-230`). Design lists any flag combinations it also tests.
- [ ] A refused `generate` leaves its destination as it found it: no model refusal fires after the first write. Environment failures are outside this criterion. Design states what an environment failure after the first write leaves behind (a partial package, as today, or a rollback).
- [ ] A test fails if a raise site that the 2a site account classifies as anything other than `internal_invariant` becomes reachable after the first write. Design picks how the test decides reachability. If an internal check does fire after the first write, it leaves the destination as an environment failure would. That is a stated limit, not a goal.
- [ ] On every 2a case, `check` reports the generator outcome equal to the stored generator answer, and screen findings equal to the stored screen answer. `check` computes disagreements itself, from the generator's code and the screen's reasons through `REASON_MAPPING`. The recorded entries in `tests/expectations/subset_profile/disagreements.json` are the test oracle and are never read at runtime. Every recorded disagreement appears as a disagreement.
- [ ] For every committed snapshot fixture and every corpus case that builds, `check` from a snapshot reports the same generator outcome as `check` on the live model. Each screen finding either matches the live finding, or is named as not assessed, in which case the model is not ready. This holds under whichever carriage option design picks.
- [ ] A supported snapshot loads. A snapshot whose envelope format is not supported is refused by name, with a message saying how to recapture. Both are tested on isolated artifacts. "Supported" means captured by the current build: the current envelope format version, and the package versions the existing equality checks in `snapshot/envelope.py:455-462` require. If design changes the envelope format, no snapshot captured before 2b is supported and no upgrade path is offered. If design keeps v6, today's v6 snapshots with matching package versions stay supported.
- [ ] Profile skew between the installed agentic-mbse and the pin, in both directions (newer and older), leaves `check` and `generate` on the generator route's answer. Both mark the screen findings not assessed, name both versions, and never report the model as ready. A model that builds gets a not-ready outcome from `check`, with an exit status distinct from both ready and refused. Neither command shows a raw `ImportError`. `sysml-codegen snapshot` also seals under skew whatever it seals today; if the envelope carries screen findings or facts, they are recorded as not assessed with the reason. Tested on isolated artifacts.
- [ ] A snapshot whose recorded profile version differs from the build, in both directions, loads if its envelope is otherwise supported. Its screen findings are reported as not assessed, naming both versions. No route refuses a snapshot because of its profile version. Tested on isolated artifacts. This reaches only skew where the agentic-mbse package version is unchanged (as today in development: `subset-profile/v2` on agentic-mbse `0.1.3`). Across released versions the kept package-version check refuses first, as it does today; design either states that limit or relaxes the check with a stated reason.
- [ ] If the screen fails while `generate`, `check` or `snapshot` runs (it raises, or a fact is missing), the refused-or-builds outcome is unchanged, a model that seals today still seals, and the affected findings are not assessed. A test patches the screen to raise and checks this on a corpus case that builds, for each of the three commands.
- [ ] When the screen refuses but the generator builds, `generate` and `check` report a disagreement, and `check` reports not ready. A constructed witness tests this, because 2a's corpus has no such case (for example, a test-only screen change that refuses a case that builds).
- [ ] `generate` and `check` both report every collected screen finding alongside the generator's own outcome, in the same form.
- [ ] 2a's tripwire (`test_tripwire.py`, the generator half with the screen patched to raise) still passes.
- [ ] Both repositories' tests, mypy and ruff are no worse than the recorded baselines. The draft gave 9 known failures for codegen and 5 for agentic-mbse, but no record of those counts was found in the repo; the handoff in `/tmp` was not readable from this session. Before implementation starts, design records the failing test IDs for each repository in this item's folder, and they become the baseline. A fresh gate receipt exists if agentic-mbse `src/agentic_mbse/sysml/` or `errors.py` changed.

## Known Requirements

- **[INHERITED: epic Item 2b scope 2]** `generate` and `check` share one read-only preparation path: admission, facts and capability assessment, elaboration, projection, generation metadata/type/name/collision/totality checks, body and plan compilation, and coverage checks. Destination mutation and emission stay outside it.
- **[INFERRED]** (from review L3-2) `check` runs every step `generate` runs except writing to the destination, or names each step it skips and why. A skipped step is a place where `check` can say "builds" and `generate` can still fail; the named list makes that visible.
- **[INHERITED: epic Item 2b scope 2]** `check` writes no generated package and clears no folder.
- **[INHERITED: epic Item 2b scope 2]** Destination and environment checks that need separate assessment are stated. Today these are the symlink check on the output tree (`contracts/seal.py:48`) and the `--overwrite`, `--preserve-handwritten` and `--smart-regen` handling. There is no TEAx, permission or existing-package check.
- **[INHERITED: epic Item 2b scope 1, principle 5]** Shared decisions run where their facts exist, and independent findings are collected before any output is written. Occurrence facts exist only after elaboration, so not all facts are assumed to exist before it. A finding whose facts are missing is not assessed, never passing.
- **[INHERITED: epic Item 2b scope 3]** Snapshot authority, certifiability, receipts and version checks account for the new policy. A snapshot without the required facts is assessed, rejected or upgraded, never silently screened as if it were live.
- **[INHERITED: epic principle 3; 2a spec]** The generator's own route stays runnable with the screen switched off, so conformance keeps comparing two independent answers.
- **[INHERITED: epic Item 2b scope 2]** The readiness claim is bounded. It does not certify runtime behavior or handwritten implementation correctness.
- **[INFERRED]** `check`'s wording does not contradict L6's ("CLEAR is relative to the implemented rules", agentic-mbse `subset_profile.py:23`).
- **[INFERRED]** (agent decision, 2026-10-20; ratified by owner at orchestration Align, 2026-10-20) The generator's own route alone decides whether `generate` and `check` refuse. Screen findings are added to the report. When the screen refuses but the generator builds, the result is reported as a disagreement and generation proceeds. Reason: making the screen a gate would change what `generate` accepts wherever the screen is wrong, which is an RG-1 change. 2a's corpus has no such case (`tests/expectations/subset_profile/disagreements.json`: 0 `screen_refuses_generator_builds` entries out of 136), but models outside the corpus are unchecked.
- **[INFERRED]** (agent decision, 2026-10-20, from review L3-4; not owner-ratified) Every disagreement is reported, including the kind where the generator refuses and the screen says nothing. That kind is 129 of the 136 recorded entries, so most refusals will carry one. It is reported because L6 says the screen's clear answer is relative to its rules, and hiding the gap would overstate the screen. The report keeps this kind distinct from the screen-refuses-generator-builds kind. It changes no outcome.
- **[INFERRED]** (orchestrator ruling, 2026-10-20, derived from the owner-ratified line above; review L1-2, L1-5) Profile skew between the installed agentic-mbse and the pin never changes the refused-or-builds outcome of `check` or `generate`. This narrows the Epic Strategy line "keep temporary skew fail-closed" (agent-grade strategy): fail-closed now means the screen's findings are never trusted under skew, not that the build or the check stops. Making skew stop `generate` would be a new refusal and would need RG-1 approval; it is not taken here.
- **[INFERRED]** (orchestrator ruling, 2026-10-20, same derivation; review L1-3) No new refusal is keyed on the subset profile version, on any route. Refusing a snapshot by envelope format version is an input-compatibility refusal about the snapshot file, not a change to what models the generator accepts. ADR 0005 is the precedent for v5→v6 (`.project/adr/0005-exact-identity-elaboration-replaces-string-resolution.md` lines 49, 56). The owner's answer below is the authority for applying it in 2b. The existing package-version equality checks (`snapshot/envelope.py:455-462`) stay unless design changes them with a stated reason.
- **[NEED]** (owner, 2026-10-20, orchestration Align, asked whether anyone needs snapshots saved before 2b to keep loading): "the only thing to check is the artifacts on our website. but those should be stand-alone".
- **[INFERRED]** (agent reading of the quote above) No consumer's saved snapshots need to keep loading. A new snapshot format that refuses older snapshots by name with a recapture message is acceptable. This narrows the epic's "supported historical snapshots" and "supported upgrades" (Item 2b scope 3; epic Success Criteria, live/snapshot bullet) to the definition of "supported" in Success Criterion 6.
- **[INFERRED]** (orchestrator finding, verified 2026-10-20) Consumers do commit snapshots. dc3 has `exploration/ac_dc_baseline/dc3_baseline.snapshot.json` and `exploration/ac_dc_baseline/studies/20261013-study-ready-baseline/snapshot.json`. fusion-tea has three `recaptured.snapshot.json` files under `.project/active/`. These already stop loading on any agentic-mbse version bump, because of the exact-version check. Under the owner's answer, a new format is acceptable. The stated consequence: those consumers must recapture, and the study layer's `integrate` reports `snapshot-drift` until they do (`study/integrate.py:1188-1198`).
- **[INFERRED]** (owner question still open, 2026-10-20) Design confirms that the website's artifacts do not load snapshots, or accounts for them if they do. The website's location is unknown. If design cannot locate it, design records the check as unchecked.
- **[INFERRED]** (orchestrator ruling, 2026-10-20, on review L2-1) Moving `PARAM_FIELD_COLLISION` ahead of the first write changes when `generate` refuses, not what it refuses, so it is not RG-1. Two conditions hold it there. First, a model with several faults reports the same first refusal code as today. Second, a refused `--overwrite` run leaves the existing package in place. That is intended: a consumer that reads "package present" as "this run built" will see the old, still-sealed package after a refusal.
- **[INFERRED]** A model with a `candidate_refusal` finding is never reported ready by `check`. The finding is shown whatever RG-1 later decides.
- **[INFERRED]** (from review L3-7) The generate route reaches the screen adapter only in a way that cannot fail the build, including the import-time `ImportError` on skew (`subset_profile_adapter.py:29-34`). `test_nothing_in_src_imports_the_adapter` (`tests/conformance/subset_profile/test_reason_mapping.py:186-195`) is replaced by a test that pins the new boundary, not deleted.
- **[HARD]** A change to agentic-mbse `src/agentic_mbse/sysml/` or `errors.py` needs a gate rerun and a new receipt (`scripts/subset_profile/codegen_suite.py`; D13).

## Non-Goals

- Changing what the generator accepts or refuses. Out of scope because it is RG-1. This includes RG1-12 (`[ITEM-OWNED-PART-REFUSED]`); `check` reports whatever the generator does at the time.
- Deciding String metadata policy (RG-2).
- Filing the staged ADR 0001, 0012 and 0016 and P-0001 amendments (RG-3).
- Editing consumer repositories (dc3, fusion-tea). Out of scope because recapturing their snapshots is the consumers' work; this item states the cost.
- Detecting unknown silent losses in general. This is a recorded limit of the epic, not an acceptance gate.
- Certifying runtime values or the TEAx execution lane.

## Open Questions / Deferred to design

- **How a snapshot carries the screen.** The owner's answer removes the compatibility cost of a new format; design still chooses. Three options:
  - Seal the screen's findings and the profile version into a new envelope version, and recapture the 23 fixtures. Sealed findings go stale when the profile moves.
  - Seal the screen's facts (`SubsetFacts`, pure dataclasses in agentic-mbse `sysml/subset_facts.py`) and re-run the screen on replay. A replay under a newer profile then computes fresh findings. This fits the recorded premise that snapshots are a serialization choice (ADR 0011 "Why"; product-lens spec-F6). The cost is a larger envelope and a schema for the facts.
  - Keep v6 and report screen findings as not assessed on replay. A license-free replay then can never report ready for a model with screen findings (product-lens spec-F6).
  
  A spike comes before design commits.
- **Scope split trigger** (orchestrator ruling, 2026-10-20; review L2-3). Snapshot authority stays in this item for now. If the snapshot-carriage spike shows the snapshot half cannot be done within the item's estimate, or its format decision is still open after the spike, the snapshot half splits into its own item. The live half then ships alone and reports screen findings on replay as not assessed. The item's estimate (6–10 days, from the epic) has not been re-examined; the spike should restate it.
- Whether to bump the agentic-mbse version. This depends on the snapshot decision: if recapture happens anyway, a bump costs little more.
- **How the late refusal moves ahead of the first write.** Leading option: move the field-collision check ahead of the first write, as `_preflight_registry_class_names` did for registry collisions (`cli/__init__.py:279-298`, whose docstring describes this fix). To keep the first reported code, it would sit after the coverage preflight (`:1343`) and before the clear (`:1346`). The other option is to render everything in memory, then write. What that would buy: rendering's internal checks would also fire before the first write, and `check` could run the template rendering without writing. The cost is memory and edits to `_generate_modules`, `_generate_stencils` and smart-regen backups (`preservation.py:223-230`).
- The `check` CLI: its inputs (`--models`/`--from-snapshot`, and an optional destination for the destination checks), its exit codes (which must tell ready, not ready and refused apart) and its output format.
- How a `SubsetDiagnostic` joins a generator refusal in the report (2a left this to 2b).
- Whether an omission or exclusion finding, on its own, makes a model that builds not ready, and what `check` says for it.
- The codegen `execution` lane (124 TEAx tests), from-snapshot generation, and a wheel build with packaged cases, which 2a did not assess. Design states which of these the parity evidence runs.

---

## Related Artifacts

- **Epic:** agentic-mbse `.project/backlog/epic_executable-subset-contract.md`, Item 2b, with Design principles, Epic Strategy and Risks
- **Prior item (2a):** `c381fb00:.project/active/subset-profile-conformance/{spec,design,plan,audit}.md`, `adr-0016-amendment.md`, `rg1-recommendations.md`, `rg2-string-policy.md`
- **ADRs:** 0005 (exact-identity elaboration; its no-migration clause covers v5→v6 only), 0011 (projection boundary), 0016 (API version pins); product P-006
- **Orchestration Align:** `.project/active/subset-profile-screen/briefs/align.md`
- **Spec review:** `.project/active/subset-profile-screen/spec-review.md`
- **Handoff:** `/tmp/handoff-20261020-140211.md`
- **Product lens:** `.project/active/subset-profile-screen/product-lens.md`
- **Design:** `.project/active/subset-profile-screen/design.md` (to be created)

---

**Next Steps:** After approval, the snapshot-carriage spike (which also applies the split trigger), then `/_my_design`.
