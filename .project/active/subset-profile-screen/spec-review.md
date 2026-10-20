# Spec Review: Read-only readiness check and snapshot authority (EXEC-SUBSET-CONTRACT Item 2b)

**Spec:** `.project/active/subset-profile-screen/spec.md` (draft on `bab17736`)
**Contract:** `claude-pack/commands/_my_spec.md`
**Review File:** `.project/active/subset-profile-screen/spec-review.md`
**Date:** 2026-10-20

---

## Reality Check

Sound, with two factual errors that change the work. The spec is about the right item, and its central decision (the generator's own route decides refusal; the screen only reports) matches the owner's ratification and is carried into `generate` correctly. But the Problem section's list of "late refusals" is mostly wrong: 2a's own site account classifies two of the three named kinds as unreachable internal checks, so only one model refusal actually fires after writing starts (L1-1). And the rescoping that cleared the product-lens BLOCK moved the same tension from `generate` into `check` and into the snapshot loader rather than removing it (L1-2, L1-3). Targeted edits fix both. Rework is not needed.

---

## Audit

### Lens 1 — Faithfulness

**L1-1 · Direct claim (must-fix):** The Problem says "three refusal kinds fire later, during rendering": `PARAM_FIELD_COLLISION`, `MODULE_KIND_UNRENDERABLE` and the repeated metadata checks. 2a's site account (`tests/expectations/subset_profile/site_account.csv`) says otherwise:

- `PARAM_FIELD_COLLISION` (`generation/entry_point.py:38`, row 337) is `public_capability`, with a real witness case (`output-naming__param_field_collision`). It runs in `_generate_entry_points`, step 8, after the clear (`cli/__init__.py:1376`). This one is real.
- `MODULE_KIND_UNRENDERABLE` at `modules.py:455` (row 350) is `internal_invariant`: "the CLI renders report aggregators through the constraint plan". Same for `stencils.py:61` (row 380).
- The metadata checks at `stencils.py:54,67` and `test_gen.py:61,77` (rows 379, 381, 384, 385) are `internal_invariant`, guarded by `_preflight_generation_metadata` (`cli/__init__.py:253-276`), which already runs before the first write.

So one public model refusal fires after writing, not three. This matters in two places. Success Criterion 1 asks for "one fixture per post-write refusal kind above", and 2a found that no well-formed model can reach two of them, so the criterion cannot be met through the public route. And the Open Question on render-before-write is framed around a large refactor ("render everything in memory"), when the repo already has the pattern for the one real case: hoist a pure detector into preflight, as `_preflight_registry_class_names` did (`cli/__init__.py:279-298`, whose docstring describes this exact fix). The spec should correct the Problem, cite the site account, and rewrite Success Criterion 1 to cover the one public late refusal. It should keep the in-memory option open, but state honestly what it would buy (see L3-2).

**L1-2 · Direct claim (must-fix):** The spec-F1 BLOCK is cleared for `generate`, but the same contradiction now sits inside `check`. The ratified line (Known Requirements, `[INFERRED]` ratified 2026-10-20) says "the generator's own route alone decides whether `generate` and `check` refuse." Success Criterion 6 says profile skew "stops `check`". In a skewed install, a model that `generate` builds would be stopped by `check`. So the screen's version decides `check`'s outcome, which is what the ratified line rules out, and `check` no longer predicts `generate`. There are two ways out, and the spec has to pick one or ask:

- Treat "stops" as a third outcome, separate from "refused": `check` could not assess the screen, so it does not claim ready (epic principle 6: "a tool's inability to assess it is not a confirmed refusal"). The spec then has to say that a stopped `check` is not a refusal and reports the generator's answer if it has one.
- Make `check` behave as `generate` does: report the generator's outcome and mark screen findings not assessed, naming both versions.

I'd take the second. It keeps `check` and `generate` identical on every input, which is the whole point of the item, and it still never claims ready. Either way, the ledger's "BLOCK cleared by rescoping" holds only once this is fixed.

**L1-3 · Direct claim (must-fix):** Success Criterion 7 allows "a snapshot whose screen authority differs from the build is refused with a recapture message". If the loader refuses, `generate --from-snapshot` refuses too, because both go through one loader (`snapshot/envelope.py:455-462`). That is the spec-F1 problem again on the snapshot route: the screen's version would decide whether `generate` builds. The difference from today is real but narrow. The loader already refuses on any `agentic_mbse_version` mismatch, so a new refusal happens only when the profile version changes without a package version change. The spec should say which route the "refused" branch applies to. If it applies to `generate --from-snapshot`, it needs either an RG-1 disposition or an argument, written down, that refusing a snapshot is input compatibility and not a model accept/refuse change. The second argument is plausible, and ADR 0005 already treats v5 refusal that way, but the spec has to make it rather than leave it inside an "or".

**L1-4 · Direct claim (must-fix):** The owner asked that the spec say what "supported" now means. It doesn't. Success Criterion 5 says "A supported snapshot loads" without defining supported, and the epic's "supported historical snapshots" and "supported upgrades" (Item 2b scope 3; epic Success Criteria, live/snapshot bullet) are not reconciled anywhere. Given the owner's Q2 answer, the plain reading is: a supported snapshot is one captured by the current build; no snapshot from before 2b is supported; no upgrade path is offered. If that is the intent, the spec should say so and record it as a narrowing of the two epic criteria, citing the `[NEED]`. If design might keep v6 (Open Question 1), "supported" includes today's v6 snapshots, and the spec should say that too.

**L1-5 · Rewrite request (should-fix):** The skew wording against the epic. The intent asked for consistency with the Epic Strategy line "keep temporary skew fail-closed". The spec's line "fails closed for the screen only" is a reinterpretation of that line, but the spec never says it is narrowing the epic. Ask the spec agent to name the epic line and state the narrowing: fail-closed now means "the screen's findings are never trusted under skew", not "the build stops". The epic line is agent-grade strategy, so narrowing it under the ratified decision is legitimate. It just has to be visible.

**L1-6 · Question to the user (should-fix):** The `[NEED]` line carries the owner's quote, then adds "So no consumer's saved snapshots need to keep loading". That sentence is the agent's reading, not the owner's words. One consumer may not have been in view when the question was asked. The study layer's `integrate` gate 4 recaptures the snapshot and requires it to match the tracked one byte for byte (`study/integrate.py:1188-1198`, `snapshot-drift`). Any consumer project with a tracked `*.snapshot.json` will fail `integrate` until it recaptures and commits. This already happens on every agentic-mbse version bump, so it is not new in kind, but a format change forces it at once. **Did you know a format change makes every consumer's `integrate` run fail with `snapshot-drift` until they recapture? If that's fine, the spec should record it as an accepted consequence. If not, the carriage choice in Open Question 1 changes.** Separately, the spec should split the line: the quote stays `[NEED]`, and the "so no consumer..." consequence becomes `[INFERRED]`.

**L1-7 · Direct claim (minor):** The spec says 22 committed snapshots. `git ls-files -- '*snapshot*.json'` shows 22 `instance_graph_snapshot.json` fixtures plus `tests/fixtures/study_station/station.snapshot.json`, which is also a v6 envelope. That makes 23. The station fixture matters because the study-layer tests depend on it, and CLAUDE.md warns not to reformat its package.

**L1-8 · Direct claim (minor):** The Related Artifacts entry "ADR 0005 (no snapshot migration)" points at `.project/adr/0005-exact-identity-elaboration-replaces-string-resolution.md`. Its no-migration clause (lines 49, 56) is about v5 to v6 only. Citing it as a general rule against upgrades overstates it. The owner's Q2 answer is the real authority for "no upgrade" in 2b.

### Lens 2 — Problem & Approach

**L2-1 · Judgment on the owner's question 4 (record in spec):** Is "a refused `generate` leaves its destination as it found it" an RG-1 change? My judgment: it changes *when* the refusal fires, not *what* is refused, so it is not RG-1. That holds on two conditions the spec should state:

- **The first code reported stays the same.** Moving `PARAM_FIELD_COLLISION` before the clear makes it fire earlier than the link-free check (`cli/__init__.py:1326`), the constraint plan build and the coverage preflight (`:1339`). A model with two faults could then report a different first code than it does today. Accept/refuse is unchanged, but the reported code is a public contract that 2a's corpus pins per case. Either keep the order, or list any case whose first code changes.
- **A visible side effect changes with `--overwrite`.** Today a refused `--overwrite` run that reaches step 8 has already cleared the old package. After 2b, the old package stays. That is the point of the change, but a consumer that read "package present" as "this run built" would now see a stale package, still sealed, after a refusal. The spec should say this is intended.

With both stated, I agree with the Align assumption that this is not RG-1.

**L2-2 · Direct claim (must-fix):** Success Criterion 2 ("No refusal it can raise happens after the first write") is false as written for refusals that come from the environment. `PACKAGE_WRITE` refusals come from `OSError` during writing (`cli/__init__.py:1416-1430`) and from sealing, which runs over the final on-disk tree (`_seal_package`, `cli/__init__.py:802-847`). Sealing re-runs `_preflight_constraint_names` and `ensure_package_tree_is_link_free` after every write. A full disk or a permission error cannot be detected before writing. The spec should limit the criterion to model refusals (public capability and output naming codes, in the site account's terms), and say what an environment failure after the first write leaves behind. It could be a partial package, as today, or a rollback; design picks.

**L2-3 · If-then tradeoff (should-fix), the owner's question 3 on scope:** I'd split snapshot authority into its own item (2c), and not wait for the spike to force it. Reasons:

- Its central decision, how a snapshot carries the screen, is open, and the spec itself asks for a spike before design.
- The live-route work is useful on its own: `check`, findings on `generate`, no write before a model refusal. It ships without snapshot carriage. On replay, findings are reported as not assessed, which Success Criterion 4's second clause already allows, and which is honest under principle 8 and the Risk "Snapshot route bypasses new decisions".
- The live half is bigger than it looks. Running fact extraction (`subset_extraction.py`, which reads SysIDE) on every live `generate` adds a new cost and a new way to fail. The 6–10 day estimate was never examined, and 2a grew from 17–27 to 25–35 days at its own spec review.
- Against splitting: once the late refusal is a preflight hoist (L1-1), the live half may be small. If the spike shows that sealing the findings and the profile version is a day's work plus recapturing 23 fixtures, one item is fine.

**If** the owner wants one item, make the spike a gate with a stated threshold, for example "split if carriage needs a new envelope version plus more than N days". **If** the owner is happy to split now, 2b's snapshot criteria shrink to: replay never claims ready while screen findings are not assessed, and profile skew on replay is reported.

**L2-4 · If-then tradeoff (should-fix):** Open Question 1 names two carriage options: seal the findings, or keep v6. There is a third: seal the screen's facts (`SubsetFacts`, pure dataclasses, `agentic_mbse/sysml/subset_facts.py`) and re-run the screen on replay. Sealed findings go stale the moment the profile moves. Sealed facts let a replay under a newer profile compute fresh findings, which is the only option that fits the recorded premise that snapshots are a serialization choice (ADR 0011 "Why"; product-lens spec-F6). The cost is a larger envelope and a schema for the facts. The spec should list it so the spike weighs it.

### Lens 3 — Pipeline Risk

**L3-1 · Direct claim (must-fix), design decision in disguise:** Success Criterion 4 requires `check` from a snapshot to report "the same findings as `check` on the live model". Under the keep-v6 option in Open Question 1, replay cannot report any screen finding, so the criterion fails by construction. The criterion quietly picks carriage option 1 while the Open Question says design chooses. Rewrite it to hold under either option. The generator decision must always match. Screen findings must either match, or be named as not assessed with no ready claim.

**L3-2 · Rewrite request (should-fix):** The read-only path's depth is ambiguous, and two engineers would build different things. Known Requirements say the shared path includes "body and plan compilation", but not whether `check` renders the schema, module, stencil, pipeline, registry and test templates in memory. If `check` stops at preflight and the constraint plan, a template failure or internal-invariant raise in rendering makes `generate` refuse where `check` said it builds. Success Criterion 1 would not catch that, because it only covers corpus refusals. State the outcome needed, for example: "`check` runs every step `generate` runs except writing, or names the steps it skips." Leave the method to design.

**L3-3 · Rewrite request (should-fix):** The sentinel tests in Success Criterion 1 don't name the flags. `--overwrite` is the only flag that deletes anything (`_clear_output_directory`, `cli/__init__.py:70`). `--smart-regen` and `--preserve-handwritten` read the destination and write backups (`cli/__init__.py:621-660`, `preservation.py:223-230`). A sentinel test without `--overwrite` would pass today for every pre-write refusal and prove little. The criterion should cover each destination-mutating flag combination.

**L3-4 · Rewrite request (should-fix):** "Recorded disagreements appear as disagreements" (Success Criterion 3) can be read two ways. Either `check` reads `tests/expectations/subset_profile/disagreements.json` at runtime, which would ship test data in the product, or it computes the disagreement from the generator's code and the screen's reasons through `REASON_MAPPING`. Only the second works for models outside the corpus. Say that `check` computes it, and that the recorded entries are the test oracle. Note the volume too: 129 of the 136 recorded entries are `generator_refuses_screen_silent`. If each one is shown as a disagreement, most refusals will carry one. That may be right, since it is honest about L6's "CLEAR is relative" (agentic-mbse `subset_profile.py:23`), but the spec should decide it, not leave it to the report format.

**L3-5 · Rewrite request (should-fix):** Several criteria depend on the licensed lane. Success Criteria 1, 3 and 4 run live models, which need `SYSIDE_LICENSE_KEY`, and CLAUDE.md says license-gated tests skip without the key, "so a green run with no key is not a full run". The criteria should say they run licensed, and that a skip is not a pass. Success Criterion 12's baselines ("9 known failures; agentic-mbse: 5") should cite where they are recorded.

**L3-6 · Question to the user (should-fix):** The `[NEED]` line asks design to "confirm that the website artifacts do not load snapshots". The Align brief says no repo under `~/src` holds the website. Design won't find it either. **Where do the website's artifacts live? If you can't say right now, is "should be stand-alone" enough to skip the check?** This is a question for now, not for design.

**L3-7 · Direct claim (minor):** `tests/conformance/subset_profile/test_reason_mapping.py:186-195` (`test_nothing_in_src_imports_the_adapter`) asserts that nothing under `src/` imports the adapter. 2b must retire or invert it. That is fine, but no requirement says so, and the adapter raises `ImportError` at import time on skew (`subset_profile_adapter.py:29-34`). A requirement should state that the generate route reaches the adapter only in a way that cannot fail the build. The test that pins this should replace the 2a test, so the boundary stays tested and isn't just deleted.

### Lens 4 — Hygiene

**L4-1 · Rewrite request (minor):** The `Problem` cites `cli/__init__.py:1346` as "where the output folder is cleared or created". Line 1346 is the `--overwrite` branch. Folder creation is `_setup_output_directories` at `:1351`. Small, but the sentinel criteria rest on exactly this point.

### Lens 5 — Reader Comprehension

**L5-1 · Rewrite request (should-fix):** The criteria use six outcome words without defining them: "refuse", "stop", "ready", "clean", "disagreement" and "not assessed". "Ready" and "clean" seem to mean the same thing; "stops" seems to differ from "refuses", but the spec never says so. A reader can't tell how many outcomes `check` has, and the L1-2 contradiction hides in that gap. Ask the spec agent to add a short plain-words list of the outcomes `check` and `generate` can report. It should cover the outcomes only, not the output format or exit codes, which stay with design. The criteria should then use only those words.

---

## Engagement Summary

**Overall take:** The headline decision is right and is carried into `generate` faithfully: the generator route decides, and the screen reports. But the spec misreads its own evidence on late refusals: one is real, not three. And the BLOCK clearance only moved the screen-decides problem into `check` and into the snapshot loader. Fix those, define the outcome words and what "supported" means, and the spec is a sound contract. I'd also split snapshot authority out.

**Here's what I need you to weigh in on:**

1. **[L1-2]** Under profile skew, should `check` behave exactly like `generate` (report the generator's answer, with screen findings marked not assessed)? Or should it stop, as a third outcome that is explicitly not a refusal? I recommend the first, because it keeps `check` and `generate` identical.
2. **[L1-3]** If a snapshot's profile version differs from the build, may `generate --from-snapshot` refuse it? That is either RG-1 or "input compatibility" (the ADR 0005 precedent), and the spec has to say which.
3. **[L2-3]** Split snapshot authority into its own item now, or keep one item with the spike as a gate and a stated threshold? I recommend splitting.
4. **[L1-6]** A new snapshot format makes every consumer's `integrate` run fail with `snapshot-drift` until they recapture. Is that acceptable under your Q2 answer?
5. **[L3-6]** Where do the website artifacts live, or is "should be stand-alone" enough to skip the check?
6. **[L2-1]** My judgment on your question 4: not RG-1, if the first reported code is kept and the `--overwrite` stale-package effect is stated as intended. Confirm.
7. **[L1-1, L2-2, L3-1]** Corrections the spec agent can make without you: only `PARAM_FIELD_COLLISION` is a public late refusal; "no refusal after the first write" applies to model refusals, not disk errors; Success Criterion 4 must hold under either carriage option.

**Must-fix:** L1-1, L1-2, L1-3, L1-4, L2-2, L3-1.
**Should-fix:** L1-5, L1-6, L2-1 (record the conditions), L2-3, L2-4, L3-2, L3-3, L3-4, L3-5, L3-6, L3-7, L5-1.
**Minor:** L1-7, L1-8, L4-1.

**Not checked:** the handoff at `/tmp/handoff-20261020-140211.md`; whether any consumer project (fusion-tea or others) actually tracks a snapshot (this session could not list `~/src`); 2a's `rg1-recommendations.md` and `rg2-string-policy.md`; whether `build_constraint_generation_plan` itself can raise a public refusal before the first write that would compete with a hoisted `PARAM_FIELD_COLLISION` for the first reported code.

---

## Resolutions

[To be filled in when the owner answers. One entry per finding ID.]

---

**Verdict:** Revise
**Next Steps:** Once the owner answers summary items 1–6, record them under Resolutions, then return to the spec agent with this review to incorporate. The reviewer does not edit the spec.
