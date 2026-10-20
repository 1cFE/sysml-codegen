# Spec: Read-only readiness check and snapshot authority (EXEC-SUBSET-CONTRACT Item 2b)

**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-10-20
**Complexity:** HIGH
**Branch:** `subset-profile-screen` (from `main` `0c4b0281`; agentic-mbse sibling worktree at `main` `e268357f`)

---

## Problem

Modelers have no way to ask "will this model generate?" without running `generate`, and `generate` itself can fail after it has started writing. Item 2a made the shared subset contract (the screen in agentic-mbse `sysml/subset_profile.py`) agree with what the generator does, but nothing on the generate route uses it, and snapshots cannot carry it. Paths below are under `src/sysml_codegen/` and were read at `0c4b0281`.

- **Refusals happen after writing starts.** Most preparation checks run before the first write (`cli/__init__.py:1346`, where the output folder is cleared or created). Three refusal kinds fire later, during rendering: `PARAM_FIELD_COLLISION` (`generation/entry_point.py:38`), `MODULE_KIND_UNRENDERABLE` (`modules.py:456-464`) and repeated metadata checks (`stencils.py:54,67`, `test_gen.py:61,77`). A refused `generate` can leave a partial package (`cli/__init__.py:1418-1420`), and a check that stops before writing would miss these refusals.
- **The generator stops at its first refusing stage.** A modeler fixes one problem per run. The screen can report every independent finding at once, but it is not called on the generate route (`subset_profile_adapter.py:11`; pinned by `tests/conformance/subset_profile/test_reason_mapping.py:186-195`).
- **Snapshots cannot reproduce the screen.** A v6 snapshot holds only the sealed elaborated graph: no parse tree and no screen facts, and the loader refuses unknown keys (`snapshot/envelope.py:340-343`). Refused models never seal, so live and replay already agree on accept/refuse. They cannot agree on the screen's non-blocking findings (omissions, exclusions, candidate refusals) for an admitted model. The snapshot also records no profile version, so profile skew against a snapshot is invisible.
- **Versions are brittle.** The loader requires exact equality of both package versions (`envelope.py:455-462`) and has no upgrade path (ADR 0005). Any version bump makes all 22 committed snapshots unloadable, which is why 2a pinned `SUBSET_PROFILE_VERSION` instead of bumping (ADR 0016 pattern).

Governing obligations carried into this item:

- **[INHERITED: epic, owner gates 2026-10-18]** RG-1: any change to what the generator accepts or refuses needs owner approval. RG-2: String metadata policy is the owner's. RG-3: merges, PRs and ADR filing are the owner's.
- **[INHERITED: P-0003]** "we do NOT create workarounds to accept bad models -- we follow what KerML, SysMLv2 and SysIDE support".

## Success Criteria

- [ ] For every refusing case in 2a's conformance corpus, and for one fixture per post-write refusal kind above, `check` and `generate` refuse with the same code at the same preparation stage, and a sentinel destination (pre-populated files and an empty folder) is byte-identical afterwards, with no files added or removed.
- [ ] A refused `generate` leaves its destination as it found it. No refusal it can raise happens after the first write.
- [ ] On every 2a case, `check` reports the generator outcome equal to the stored generator answer and screen findings equal to the stored screen answer. Recorded disagreements appear as disagreements, not as clean results.
- [ ] For every committed snapshot fixture and every admitted corpus case, `check` from a snapshot reports the same decision and the same findings as `check` on the live model. Where a finding cannot be assessed from the snapshot, it says so by name, and the model is not reported as ready.
- [ ] A snapshot that lacks what the current build needs is refused with a message saying how to recapture. A supported snapshot loads. Both are tested on isolated artifacts.
- [ ] Profile skew between the installed agentic-mbse and the pin, in both directions (newer and older), stops `check` with a message naming both versions. `generate` builds or refuses exactly as its own route decides, and it reports the screen findings as not assessed, naming both versions. This is tested on isolated artifacts.
- [ ] Profile skew between a snapshot and the current build, in both directions, is detected. A snapshot whose screen authority differs from the build is refused with a recapture message, or its findings are reported as not assessed. It never silently passes. This is tested on isolated artifacts.
- [ ] If the screen fails while `generate` runs (it raises, or a fact is missing), the build-or-refuse outcome is unchanged, and the affected findings appear as not assessed. A test patches the screen to raise and checks this on a corpus case that builds.
- [ ] When the screen refuses but the generator builds, `generate` and `check` report a disagreement and do not call the model clean. A constructed witness tests this, because 2a's corpus has no such case (for example, a test-only screen mutation that refuses a built case).
- [ ] `generate` and `check` both report every collected screen finding alongside the generator's own outcome, in the same form.
- [ ] 2a's tripwire (`test_tripwire.py`, the generator half with the screen patched to raise) still passes.
- [ ] Both repositories' tests, mypy and ruff are no worse than the recorded baselines (codegen: 9 known failures; agentic-mbse: 5). A fresh gate receipt exists if agentic-mbse `src/agentic_mbse/sysml/` or `errors.py` changed.

## Known Requirements

- **[INHERITED: epic Item 2b scope 2]** `generate` and `check` share one read-only preparation path: admission, facts and capability assessment, elaboration, projection, generation metadata/type/name/collision/totality checks, body and plan compilation, and coverage checks. Destination mutation and emission stay outside it.
- **[INHERITED: epic Item 2b scope 2]** `check` writes no generated package and clears no folder.
- **[INHERITED: epic Item 2b scope 2]** Destination and environment checks that need separate assessment are stated. Today these are the symlink check on the output tree (`contracts/seal.py:48`) and the `--overwrite`, `--preserve-handwritten` and `--smart-regen` handling. There is no TEAx, permission or existing-package check.
- **[INHERITED: epic Item 2b scope 1, principle 5]** Shared decisions run where their facts exist, and independent findings are collected before any output is written. Occurrence facts exist only after elaboration, so not all facts are assumed to exist before it. A finding whose facts are missing is reported as not assessed, never as clean.
- **[INHERITED: epic Item 2b scope 3]** Snapshot authority, certifiability, receipts and version checks account for the new policy. A snapshot without the required facts is assessed, rejected or upgraded, never silently screened as if it were live.
- **[INHERITED: epic principle 3; 2a spec]** The generator's own route stays runnable with the screen switched off, so conformance keeps comparing two independent answers.
- **[INHERITED: epic Item 2b scope 2]** The readiness claim is bounded. It does not certify runtime behavior or handwritten implementation correctness.
- **[INFERRED]** `check`'s wording does not contradict L6's ("CLEAR is relative to the implemented rules", agentic-mbse `subset_profile.py:23`).
- **[INFERRED]** (agent decision, 2026-10-20; ratified by owner at orchestration Align, 2026-10-20) The generator's own route alone decides whether `generate` and `check` refuse. Screen findings are added to the report. When the screen refuses but the generator builds, the result is reported as a disagreement and generation proceeds. Reason: making the screen a gate would change what `generate` accepts wherever the screen is wrong, which is an RG-1 change. 2a's corpus has no such case (`tests/expectations/subset_profile/disagreements.json`: 0 `screen_refuses_generator_builds` entries out of 136), but models outside the corpus are unchecked.
- **[NEED]** (owner, 2026-10-20, orchestration Align, asked whether anyone needs snapshots saved before 2b to keep loading): "the only thing to check is the artifacts on our website. but those should be stand-alone". So no consumer's saved snapshots need to keep loading, and a new snapshot format that refuses older snapshots by name with a recapture message is acceptable. Design must confirm that the website artifacts do not load snapshots, or account for them if they do.
- **[INFERRED]** (agent decision, 2026-10-20; rescoped after product-lens spec-F1) A profile-version mismatch fails closed for the screen only. `check` stops, and `generate` keeps its own route's outcome and reports the screen as not assessed. Neither shows a raw `ImportError` (`subset_profile_adapter.py:29-34`). Making the mismatch stop `generate` would be a new refusal, so it would need RG-1 approval. That option is open to the owner and is not taken here.
- **[INFERRED]** A model with a `candidate_refusal` finding is never described as clean by `check`. The finding is shown whatever RG-1 later decides.
- **[HARD]** A change to agentic-mbse `src/agentic_mbse/sysml/` or `errors.py` needs a gate rerun and a new receipt (`scripts/subset_profile/codegen_suite.py`; D13).

## Non-Goals

- Changing what the generator accepts or refuses. Out of scope because it is RG-1. This includes RG1-12 (`[ITEM-OWNED-PART-REFUSED]`); `check` reports whatever the generator does at the time.
- Deciding String metadata policy (RG-2).
- Filing the staged ADR 0001, 0012 and 0016 and P-0001 amendments (RG-3).
- Detecting unknown silent losses in general. This is a recorded limit of the epic, not an acceptance gate.
- Certifying runtime values or the TEAx execution lane.

## Open Questions / Deferred to design

- **How a snapshot carries the screen.** The owner's answer above removes the compatibility cost of a new format; design still chooses. One option is to seal the screen's findings and the profile version into a new envelope version and recapture the 22 snapshots. The other is to keep v6 and report screen findings as not assessed on replay. Either way, consumers' saved snapshots (the study layer captures them) become unloadable or less informative. With the second option, a license-free replay could never report ready for an admitted model that has screen findings (product-lens spec-F6). A spike is advised before design commits.
- Whether to bump the agentic-mbse version. This depends on the snapshot decision: if recapture happens anyway, a bump costs little more.
- How rendering moves before the first write. One option is to render everything in memory, then write. The cost is memory and the edits to `_generate_modules`, `_generate_stencils` and smart-regen backups (`preservation.py:223-230`). A spike is advised.
- The `check` CLI: its inputs (`--models`/`--from-snapshot`, and an optional destination for the destination checks), exit codes and output format.
- How a `SubsetDiagnostic` joins a generator refusal in the report (2a left this to 2b).
- What `check` says for a model with `candidate_refusal` or omission findings that the generator builds.
- The codegen `execution` lane (124 TEAx tests), from-snapshot generation, and a wheel build with packaged cases, which 2a did not assess. Design states which of these the parity evidence runs.

---

## Related Artifacts

- **Epic:** agentic-mbse `.project/backlog/epic_executable-subset-contract.md`, Item 2b, with Design principles, Epic Strategy and Risks
- **Prior item (2a):** `c381fb00:.project/active/subset-profile-conformance/{spec,design,plan,audit}.md`, `adr-0016-amendment.md`, `rg1-recommendations.md`, `rg2-string-policy.md`
- **ADRs:** 0005 (no snapshot migration), 0011 (projection boundary), 0016 (API version pins); product P-006
- **Handoff:** `/tmp/handoff-20261020-140211.md`
- **Product lens:** `.project/active/subset-profile-screen/product-lens.md`
- **Design:** `.project/active/subset-profile-screen/design.md` (to be created)

---

**Next Steps:** After approval, spikes on snapshot carriage and render-before-write, then `/_my_design`.
