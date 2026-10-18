# Design Review: Independent conformance corpus and per-site codes (EXEC-SUBSET-CONTRACT Item 2a)

**Design:** `.project/active/subset-profile-conformance/design.md` (draft 2026-10-18, at `07fd2374`)
**Spec:** `.project/active/subset-profile-conformance/spec.md` (with `spec-review.md` Resolutions)
**Review File:** `.project/active/subset-profile-conformance/design-review.md`
**Date:** 2026-10-18

Checked against sysml-codegen `subset-conformance` at `07fd2374` and the agentic-mbse sibling worktree at its current `subset-conformance` head (base `ccd57d83`). Spike S1 ran in parallel and its findings were not available to this review, so bets B2 and B3 are judged on reading alone.

---

## The Point

**[INFERRED]** (ratified by owner, 2026-10-18) Prove, with evidence independent of the screen, that the shared subset contract in agentic-mbse matches what the generator actually does, and make drift between them fail a test in sysml-codegen. Test volume is not the goal, and neither are tests that check the screen against itself.

Why it matters: Item 1 wrote the contract as rule records and checked them once, against 80 probe runs of codegen `b5663c07`. Nothing fails today when the generator changes. Items 2b, 3 and 5 will tell modelers what will generate on the strength of this contract. Owner gates bound the work: RG-1 (generator accept/refuse), RG-2 (String policy), RG-3 (merges and ADR filing), and P-0003 (follow KerML, SysML v2 and SysIDE, no workarounds).

## Fundamental Assessment

**Concerns → Rework, scoped.** The core of the design is right. The part that needs rework is narrower: who checks agentic-mbse's records once the evidence moves out of agentic-mbse.

What is right, and should survive the rework unchanged:

- **Two stored answers per case, plus a pure agreement test between them** (Core Concept 1–3, D1, D3). This does stop the screen checking itself. A widened rule makes the screen refuse a case the generator builds. Updating the stored screen answer to match then fails the agreement test, unless someone adds a reviewed disagreement entry. Regenerating both answers from live runs only passes when the two really agree live, which is the property we want. (M2 below covers the remaining ways around it.)
- **Running the generator half through `run_codegen`** and reading typed errors from log data (D2) follows an existing codegen pattern (`cli/__init__.py:1208`).
- **D12 (no agentic-mbse version bump; `SUBSET_PROFILE_VERSION` pinned per ADR 0016).** I found no concrete harm, so the orchestrator's decision stands. One fact it relies on goes into C1: the version is tied to a digest of the records and the allowlist only, not to the evaluator or extractor code (`agentic-mbse tests/test_sysml/test_subset_profile_version.py`).

What fires the tripwire:

- **The product-lens fired the structural smell "changes who owns an invariant without saying so"** (`product-lens.md`, design block, design-F1). I confirmed it, with one narrowing. ADR 0001's Decision says agentic-mbse owns "the versioned, evidence-backed record", and invariant 1 says a record outcome needs retained evidence. Today agentic-mbse's own tests enforce that (`tests/test_subset_probe_evidence.py`). After D4 and Appendix B, agentic-mbse only checks that a citation is well formed. Whether a record is actually backed becomes checkable only in sysml-codegen. The design half-says this (one risk row and a deferred decision record) but never states the move or its consequences. The narrowing: moving occurrence parity (D6) is *not* an ownership change. ADR 0001 invariant 6, owner-chosen "A (ii)", already puts that test in codegen.
- **The mechanism the design relies on for the gap does not exist.** The risk table says "coordinated merges run codegen CI". Neither repository has CI configuration (no `.github/` in either). codegen depends on the sibling checkout by editable path (`pyproject.toml:122`). So codegen's tests run against an agentic-mbse change only when someone runs them by hand. Item 4 is editing agentic-mbse concurrently, so this gap is open right now, not in theory.
- **A second coverage loss in agentic-mbse that the design does not list** (C2). Two agentic-mbse test modules run the screen on the 80 probe models. The design deletes those models and the helper that loads them, and its list of kept tests does not mention either module.

Why Rework and not Revise: the review command treats a fired structural smell as forcing Rework at Stage 0. The rework is confined to one group of decisions: D4, the agentic-mbse retirement list (Component Overview, Appendix B), D7's cross-repo link, and the ADR amendments. D1–D3, D5 and D8–D12 stand, subject to the Major findings below. I did the detailed review anyway, because the brief asked specific questions and one rework pass should cover everything. The design author should treat Stage 1 as input to that pass, not as a sign-off on the rest.

---

## Dimensional Review

### 1. Spec Compliance
**Assessment:** Concerns

- **The spec stages the ADR 0001 invariant 1 amendment as "cases admissible alongside probes"** (spec Gates, `[INFERRED]` from spec-review L1-2). D4 removes probe citations entirely. The staged text is therefore not the text the design needs (lens design-F3). The design can deviate from an `[INFERRED]` item, but it has to say so and stage the right amendment. Folded into C1.
- **Criterion B5, screen half** ("disabling the screen's recognition makes its cases report a mismatch"). As designed, the mismatch is measured against the stored screen answer, which is the screen checking itself (M1).
- **Criterion C2** asks that each refusing fixture end in *a* refused screen finding whose reason maps to the generator's code. § C applies the stricter per-case rule to fixtures instead (M3). Stricter is allowed, but here it produces false disagreements.
- **Criterion E5 (rescan)** is placed in P6 with the group E tail. If the split point is taken, E5 leaves with the tail, although it does not depend on the tail (M7).
- **A2** is open as written. The orchestrator accepted D12's replacement, and I found no harm.
- The R3 rows (Appendix C), the silent-loss families (§ D) and the RG-1/RG-2 parking all trace to the spec. I found nothing dropped.

### 2. Pattern Consistency
**Assessment:** Pass, with one duplication note

- It reuses codegen's existing idioms: `tests/expectations/<topic>/` with missing-fails and stranded-fails, the `extra=` structured-log pattern, `_refusal_record`'s sorted code multiset (`scripts/capture_v6_batch.py:110`), and `requires_license`. New directories `tests/helpers/subset_profile/` and `tests/conformance/subset_profile/` follow the existing layout.
- It does not reuse agentic-mbse's `scripts/subset_profile/codegen_suite.py`, which already runs codegen's suite against a chosen agentic-mbse revision in an isolated tree. That script is the fix for C1. The design retires `probe.py`, which that script imports from (`build_tree`, `child_env` and others). See C1 and m6.
- After 2a, codegen will have two raise-site scanners: the narrow one in `tests/conformance/test_diagnostic_provenance_sites.py:44-95` and the new `site_scan.py`. The design should say whether the old one folds into the new one (m9).

### 3. Abstraction Quality
**Assessment:** Concerns

- **`SiteReason` as one closed enum carried as an optional field** is a clean extension. It matches how `CodeGenerationError` already takes `name_safety_violation` as a keyword argument (`core/errors.py:41-49`). Using `extra={"refusal": error}` is the same pattern.
- **The type contradiction (M4).** D8 types `Diagnostic.reason` as `SiteReason | None` and requires its values to be disjoint from `SUBSET_REASON_CODES`. § A's `render_finding` sets that same `reason` to the subset reason. Both cannot be true.
- **`extra={"refusal": error}` on the `except Exception` branches** should carry the converted `unexpected_public_failure` diagnostic, not the raw exception (`cli/__init__.py:1211-1214, :1227-1230`). Otherwise the harness sees an untyped exception where users see `SI_INTERNAL_DEFECT` (m1).

### 4. Duplication Avoidance
**Assessment:** Concerns

- "Nothing is copied" is the right rule for facts. Applied to test inputs, it removes agentic-mbse's own screen regression tests (C2). Copying the probe *models* into both repos copies inputs, not facts, if agentic-mbse's copy claims only "the screen reproduces the record" and nothing about the generator. The rule should be stated for facts.
- Scanner overlap (m9).

### 5. Data Structure Clarity
**Assessment:** Concerns

- **Generation-stage refusals have no code (M6).** `CodeGenerationError` carries its code only as a message prefix (Research Findings). `_refusal_record` collects codes only from `.diagnostics` and `.findings`. `REASON_MAPPING` holds only `ElaborationCode`/`ReadinessCode` values. So the 3 corpus fixtures that refuse at generation, and the 10 naming-collision sites, get `codes: []`. The agreement rule ("refused with codes C … C is covered") is undefined when C is empty.
- **`Diagnostic` is part of the v6 snapshot encoding (M5).** `snapshot/instance_graph.py:947-995` encodes and decodes it with a fixed key set, through `graph.diagnostics` (`:1029`). D8 adds `reason` to `Diagnostic` and does not say what happens to that encoding. D9 and D12 both avoid invalidating the 22 committed snapshots, and D8 may do exactly that.
- The expectation schema (Appendix A) is clear. A case's intended (rule, shape, context) is carried only by its ID. D4's prefix check turns that into a test, which is good. Renaming a case is a reviewed diff.

### 6. Route Safety
**Assessment:** Concerns (minor)

- **E3 turns a reachable plain-exception site into a coded refusal** and calls that outside RG-1 (spec L3-2). That is true only if the exception reaches `run_codegen`'s `except Exception` today. If some caller catches it and falls back, the way `CompilationError` becomes a stub at `expression_compiler.py:291`, then the change flips accept to refuse, and that is RG-1. The design should state that condition and check it per site (m2).
- D5's named fallback (a hand patch for each site elision cannot reach) is explicit and safe.

### 7. Bets & Decisions Integrity
**Assessment:** Concerns

B1–B5 are genuine bets with "if false" consequences. B2 and B3 wait on spike S1. The decisions name their rejected alternatives. Hidden bets:

- **H1. "Someone runs codegen's suite when agentic-mbse changes."** It is false today: there is no CI, and the dependency is an editable path. The cross-repo design depends on this belief (C1).
- **H2. "`SUBSET_PROFILE_VERSION` changes whenever screen behavior changes."** It is false. The digest covers the records TOML and the allowlist, not `subset_extraction.py` or the rule recognizers in `subset_profile.py`. An extractor change keeps the version, codegen's pin test stays green, and only the screen half of the live tests can notice (C1).
- **H3. "Each refusing model reports refusals from one stage."** B1 relies on this for single-construct cases, where it is plausible. § C applies it to multi-construct fixtures too, where it is not (M3).
- **H4. "A screen mutation that changes the stored screen answer shows independence."** It does not (M1).

### 8. Reader Comprehension
**Assessment:** Pass

The Core Concept states the model plainly before any mechanism: two stored answers, live tests, a pure agreement test, everything else checked against the corpus. The fact-placement rule is one sentence. Two terms are used before they are explained: "SA-1" in § B (it is defined in the spec but not in the design) and "seam". Neither blocks understanding.

---

## Issues by Severity

### Critical

- **C1. Evidence ownership moves to codegen without being stated, and nothing checks the gap it leaves.** (Stage 0 / Bets; lens design-F1, design-F3)
  - *What moves.* After D4, agentic-mbse checks only that a `case:` citation is well formed. Whether a record is backed by evidence becomes checkable only in codegen.
  - *Why nothing catches drift.* Neither repo has CI, so nothing runs codegen's suite when agentic-mbse changes (H1).
  - *What happens to a record edit.* The digest test (`test_subset_profile_version.py`) forces a version bump on any edit to the records or allowlist. codegen's pin test then fails, but only the next time someone runs codegen's suite.
  - *What happens to a code edit.* A change to the evaluator or extractor code changes neither the digest nor the version (H2). It is caught only by codegen's licensed screen-half tests, run by hand.
  - *Fix:*
    - (a) State the move in the design, and stage the ADR 0001 amendment over the Decision sentence and invariant 1: cases *replace* probes; codegen enforces invariant 1; and a `case:<id>` resolves to `sysml-codegen tests/expectations/subset_profile/cases/<id>.json`.
    - (b) Keep `scripts/subset_profile/codegen_suite.py`, together with the tree-building code it imports from `probe.py`. Make "run codegen's subset-profile conformance tests, licensed, against this agentic-mbse revision" a required step before any agentic-mbse merge that touches `subset_profile*`, `subset_extraction.py`, `occurrence_extraction.py` or `invocation_allowlist.py`. Name it in the amendment and in the coordinated-merge procedure. Rename the design's "codegen CI" to whatever actually runs.
    - (c) Say what protects L6 and guidance (Items 3 and 5, which read agentic-mbse directly) between an agentic-mbse merge and that run.
  - *Filing* the amendment stays RG-3.
- **C2. agentic-mbse loses its only screen-on-real-model tests for 8 rules, and the design does not list them.** (Spec compliance / Duplication)
  - *The tests.* `tests/test_sysml/test_subset_profile_rules_instantiation.py` and `test_subset_profile_rules_modelwide.py` load the probe models through `tests/helpers/subset_probe_judge.py`. They check three things: the evaluator reproduces each record at its construct; controls draw no refusal; candidate reproductions are not refused.
  - *What the design does.* It deletes the probes and `subset_probe_judge.py`. Its "kept" list names "synthetic-fact evaluator tests" and neither of these modules.
  - *What is left.* After the move, agentic-mbse runs extraction on real models only through `test_subset_extraction.py` and its 8 files in `tests/fixtures/subset_profile/cases/`. A recognizer regression, for example from the concurrent Item 4 work, would pass agentic-mbse's tests.
  - *Fix.* Keep the probe models in agentic-mbse as screen regression inputs, with their generator observations (`observation.json`) removed, and keep both modules, asserting against the packaged records. That is a copy of inputs, not of facts, so it does not create a second authority under invariant 5. Also list every agentic-mbse test file the move touches: `test_subset_matrix.py` and `test_subset_site_account.py` read the account and matrix that D7 changes.

### Major

- **M1. Screen mutations prove only that the screen matches its own stored answer.** (Spec B5 / Bets H4) Patching a recognizer changes the live screen output, so a mismatch against the stored screen answer is guaranteed whenever the case reaches that recognizer. *Fix:* a screen mutation passes only when the mutated live screen answer *fails the agreement rule against the stored generator answer*. For example, a refusing case loses its refused finding and becomes `generator_refuses_screen_silent`, or a generating case gains one. This costs nothing extra, since the agreement function already exists in `cases.py`.
- **M2. The write path for stored answers, the mapping and the disagreement record is not specified.** The agreement test closes the "regenerate both sides" route. It does not close a tool that also writes `disagreements.json` from the computed set: that makes D3's equality test true by construction. *Fix:*
  - If any capture tool exists, it writes only the `generator` and `screen` blocks.
  - It refuses to write a screen answer that fails agreement unless a matching disagreement entry already exists.
  - `disagreements.json` and `REASON_MAPPING` are edited by hand only.
  - A pure test rejects a disagreement entry with an empty owner or reason, and an `rg1_pending` entry that names no `RG1-<n>`.
  - State all of this as an invariant next to Required Invariant 1.
- **M3. The fixture agreement rule will record false disagreements.** § C applies "the same rule" to fixtures: every refused finding's mapped code must be in C. A multi-construct fixture can have two refusals that the generator hits at different stages. It reports only the first (`ElaborationError` and `CodeGenerationError` are separate exits), so the second becomes a "disagreement" that is not drift. Item 3 would then read it as a coverage gap. *Fix:* for fixtures, use spec C2's rule (at least one refused finding maps into C; a generating fixture has no refused finding). Or define the stage order and excuse findings from stages after the one that refused.
- **M4. `reason` has two incompatible meanings.** D8 makes `Diagnostic.reason` a `SiteReason`, whose values are disjoint from subset reasons. § A's renderer stores a subset reason in it. *Fix:* use a separate `subset_reason` field on rendered diagnostics, or a typed union, and say which.
- **M5. Adding `reason` to `Diagnostic` touches the v6 snapshot encoding** (`snapshot/instance_graph.py:947-995`, strict key set). *Fix:* say whether `reason` is encoded (which invalidates the 22 committed snapshots, the harm D9 and D12 avoid) or dropped on round-trip. If dropped, list it beside D9's live-only limit. Alternatively, show that no `Diagnostic` carrying a `SiteReason` ever lands in `graph.diagnostics`.
- **M6. Generation-stage refusals have no code to compare.** Generation-stage refusals produce `codes: []`, as Dimension 5 shows. *Fix:* say how a `CodeGenerationError` contributes to `codes`, for example a `code` field added next to `reason` and populated from the existing prefix. Then say how the agreement rule and `REASON_MAPPING` treat those codes.
- **M7. The split point has no estimate to trigger it, and taking it drops E5.** The trigger is "group E passes its estimate", but the design gives no estimate for group E or for its head and tail. The spec gives only 25–35 days for the whole item. E5 sits in P6, so a split also removes a spec criterion that tail sites do not block, because their account rows already exist. *Fix:* give the head and tail estimates in the design, or require the plan to set them before P5 starts. Move E5 to P7. Change P7's dependency to "P3–P5, and P6 unless split".

### Minor

- **m1.** `extra={"refusal": …}` on the `except Exception` branches should carry the converted diagnostic. Also say what the snapshot-refused and parse-failure branches carry.
- **m2.** E3's plain-exception-to-coded-refusal change is outside RG-1 only for exceptions that reach `run_codegen` today. State that condition and check it per site.
- **m3.** (lens design-F2) The witnesses for agentic-mbse's 61 sites live in codegen, while their rows live in agentic-mbse. Neither repo checks the join. Record this as a named limit with an owner, or include it in C1(b)'s gate run.
- **m4.** Cite ADR 0001 invariant 6 for D6. That part of the move is already decided and is not part of the ownership change.
- **m5.** The design says "codegen CI" in several places, and ADR 0001 invariant 6 does too. Neither repo has CI. Say what actually runs the tests, and who runs them.
- **m6.** The retirement list should be complete, file by file. It omits `codegen_suite.py` (keep it, see C1), `occurrence_port_run.py` and `validate_diff.py`.
- **m7.** D12 was accepted without challenge. For the record, the pin identifies the records and the allowlist, not screen code (H2). C1 covers that.
- **m8.** Screen mutations patch private agentic-mbse functions from codegen tests. List the patched names in one place (`mutate.py`), so an agentic-mbse rename fails by name and not by a confusing `AttributeError`.
- **m9.** Say whether `test_diagnostic_provenance_sites.py`'s scanner folds into `site_scan.py`.

---

## Recommendations

1. **Rework the evidence-ownership group of decisions (C1, C2).**
   - State that enforcement of ADR 0001 invariant 1 moves to codegen.
   - Stage the correct amendment: cases replace probes, which repo enforces, how a `case:` citation resolves, and what protects L6 and guidance.
   - Keep `codegen_suite.py` as the required gate before agentic-mbse merges.
   - Keep the probe models in agentic-mbse as screen-only regression inputs, so agentic-mbse's recognizers are still tested in agentic-mbse.
   - Make the retirement list complete, file by file.
2. **Make screen mutations compare against the generator answer (M1), and specify the write path for stored answers and the disagreement record (M2).** These two close the remaining ways to get a self-confirming green run.
3. **Fix the data gaps: M4 (`reason` type), M5 (snapshot encoding), M6 (generation-stage codes) and M3 (fixture rule).** Each one is a sentence or two of design, but the implementer will hit each in P1 or P2.
4. **Give group E head and tail estimates, and move E5 out of the tail (M7).**
5. Minors as listed, during the same pass.

---

## Resolutions

None yet. This review ran non-interactively for the orchestrator. No owner or orchestrator resolutions have been recorded.

---

**Overall:** Rework (scoped to the evidence-ownership decisions: D4, the agentic-mbse retirement list and Appendix B, D7's cross-repo link, the ADR 0001 amendment). The core concept and D1–D3, D5 and D8–D12 stand, subject to M1–M7.
**Next Steps:** Record resolutions here, then re-run `/_my_design` (or return to the design-agent session) and point it at this review. The reviewer does not edit the design. Read spike S1's findings next to this review, because B2 and B3 were not judged on evidence here. Re-run `/_my_design_review` after the rework, because the fired smell needs a fresh judgment. Not checked: spike S1 results; whether 0.1.3 was ever pushed to a package index; the bodies of the 155 fixture directories; the exact line ranges the design cites in `calc_compat_renderer.py` and `elaborate.py`, except where quoted above.
