# Spec Review: Item 7 — REQ/Matrix Reconciliation

**Spec:** `.project/active/matrix-truth/spec.md`
**Contract:** `claude-pack/commands/_my_spec.md`
**Review File:** `.project/active/matrix-truth/spec-review.md`
**Date:** 2026-07-06

---

## Reality Check

**Sound.** The spec is about the right work item and faithfully captures epic Item 7 — the F4 presumption, the three kill conditions, the fixed consequence set, F2's three-way, the divergent-PASS list, UNTESTED-12, marker hygiene, the 5-xfails decision, and the ~175-row sweep all trace back to the epic's Item 7 section (`epic_pipeline_truth.md:539-628`) and discovery §D7.

The load-bearing code claims check out against the code, not the comments:

- **F4 dead-code claim TRUE.** `resolve_input` / `AGG_STRATEGIES` have zero references in `src/` outside `input_resolver.py` itself. The live path is `_resolve_aggregation_input_channel`. Confirmed.
- **The 249-vs-248 count is real.** Recounted from rows: 249 `REQ-*` rows = 236 PASS + 12 UNTESTED + 1 PENDING (REQ-PGD-06, `matrix:380`). The summary block says 248. The uncounted row is exactly the PENDING one the spec names.
- **EXT-09 part-usage leg is discharged.** `test_extractor.py:888-934` is a new anti-pattern-free class that asserts the report spans calc-def/part-def/part-usage owners (`:908`, `:934`). The spec's "Item 4 may have landed it — verify" resolves to *yes, landed*.
- **ORCH-04 weakening is real.** `test_orchestrator.py:474` asserts `min(phase1_calls) < min(alias_calls)` — first-call-only, exactly as the spec describes.

No Stage-0 failure. Proceeding to the full audit. The findings below are refinements, not a redirection.

---

## Audit

### Lens 1 — Faithfulness

**L1-1 · Direct claim:** The spec says "24 skipifs" four times (Problem §1 line 27, SC-2 line 98, HARD-F4 line 132, HARD-precondition-1 line 143). The file has **22** `skipif` decorators (`test_input_resolver.py`: 20 gating `INPUT_RESOLVER_AVAILABLE`, plus the Strategy A–D block; grep-verified count is 22, line list `150 178 200 227 244 309 329 365 372 396 426 449 471 488 552 620 640 665 698 738 783 861`). The "24" is inherited verbatim from the epic (`epic_pipeline_truth.md:545,586`) and was never recounted. This is a small drift, but it lands badly in *this* item: the spec's whole thesis is "counts that lie," and it carefully recounted the 249 rows while carrying a stale skipif count next to it. Either recount and state 22, or drop the number and say "all skipifs in `test_input_resolver.py`" — the consequence set is "all of them" regardless, so the count adds no precision, only a target design will look for and not find.

**L1-2 · Question to the user:** The spec applies a "verify at implement" caveat to EXT-09 but not to **REQ-PGD-08**, and PGD-08's row has moved since discovery. The current matrix row (`matrix:382`) cites `test_matcher_fixes_item7.py` (backtracker propagation) and `test_parameter_group_deriver.py` — the first is an Item-7-adjacent test file that post-dates the D7 sweep. The spec carries discovery's verdict ("cited file doesn't cover the claim") as settled fact in both §3 (divergent) and §5 (no-marker). Should PGD-08 get the same "re-verify against the current row before acting" caveat EXT-09 got? Its row is demonstrably not in its discovery-era state.

**L1-3 · Direct claim (confirming):** The tag discipline is honest. The `[HARD]` items are genuinely forced (R4 protocol, atomicity, byte-identity, the anti-pattern ban) or are landed facts (PGD-06 dead, AST-10 added). The `[INFERRED]` items (derived-counts-reconciled-last; Items-2/5 rows will move) are genuinely inferable, not guesses dressed up. No invented mechanism is frozen as a requirement — the F4 verdict is explicitly left open with a presumption, which is the correct posture. Nothing to fix here; flagged so the reviewer knows faithfulness was stress-tested and held.

### Lens 2 — Problem & Approach

**L2-1 · If-then tradeoff (highest stakes):** The three F4 kill-condition probes are not equally runnable, and two of them let the presumption ("land the cutover") win by inertia — the exact failure the epic warns against ("evidence, not inertia").

- **(i) parity-fails-when-extended — runnable.** "If the two implementations disagree on any new shape, that is a kill" is a concrete bar (per-fixture value/wiring equality). The fixtures exist on disk (`tests/fixtures/plant_values`, `plant_value_shapes`, `deep_cross_scope_probe`, `ife_plant`), so design can run it. Good. One gap: the spec says "Item 1's plant fixtures **and any shapes beyond the committed corpus**" — name the exact fixture set the extended suite must cover, so "beyond the committed corpus" isn't a hole design can skip through.
- **(ii) Strategy-D-dedup-is-unwanted — under-specified.** The probe is "review the params-JSON key-set diff." Against *which* baselines? No corpora named. The bar — "collapses keys a consumer depends on, or is otherwise unwanted" — is a pure judgment call with no artifact requirement. As written, a design agent can wave it through.
- **(iii) module-drifted-materially — no threshold.** "If re-syncing costs more than the cutover buys, that is a kill" is entirely subjective. There is no drift measure and no required diff artifact.

The fix is not to invent false thresholds for (ii)/(iii) — some of this is genuine judgment. The fix is to require each probe to **produce a named artifact** that the verdict cites: (i) the extended parity result over an enumerated fixture set; (ii) the actual key-set diff against named params-JSON corpora; (iii) the both-directions diff with a divergence inventory (which live-path post-COST-PATTERN fixes are absent from the module, listed). Then the judgment rests on evidence a reviewer can see, and the presumption can't win by default.

**L2-2 · Question to the user:** F4 gets a presumption plus three probes; **F2 gets no presumption** — just "decide at design against doc 10's intent" (Open Questions line 220). The F2 question is real (is the construction-time `instance_attr_to_channel` dict a deliberate optimization to document, or a divergence to remove?), but leaving it with no default risks a design stall on a decision the spec could frame a lean toward. Do you want F2 to carry a presumption (e.g., "presume the dict is a documented optimization; flip to removal only if it actually contradicts a consumer"), or is the three-way genuinely 50/50 and better left fully open? The ORCH-04 restoration is correctly fixed regardless either way.

### Lens 3 — Pipeline Risk

**L3-1 · Rewrite request (high stakes):** The ~175-row sweep has **no bounded-effort rule**, and the "D7 heuristics" it leans on are named but never operationalized. Priority: the epic budgets Item 7 at 1.5–2 days total (`epic:542`); an open-ended deep-read of 175 rows can silently swallow that budget, and the spec's Open Questions (line 225-227) even concedes "the count and character of what it finds cannot be known until the sweep runs." That's an unbounded task with an unbounded appetite. Two things need to be true:
  1. **A stopping rule.** A time-box, a sampling strategy, or a triage-then-deep-read split — something that makes the sweep terminate on schedule and `log`s what it did *not* deep-read (silent truncation reads as "swept everything" when it wasn't).
  2. **Operationalized heuristics.** "Strong-words REQs," "diagnostics," and "structural counts" are labels, not definitions — neither the spec nor discovery §D7 says what qualifies. State the concrete filter (e.g., strong-words = rows whose text contains SHALL/ALL/every/never/exactly; structural-counts = rows asserting a numeric count) or point at where it's defined, so two implementers would select the same rows.

**L3-2 · Direct claim (atomicity gap):** The F4 consequence set names rows that cite `test_dual_resolution.py` — DRA-04 and DRA-05 — but **misses DRA-03 and BT-09, which also cite it** (`matrix:166` and `matrix:120`). If either F4 outcome changes the parity suite's meaning — and both do: cutover deletes the inline comparand, excise deletes the module — then `test_dual_resolution.py` is rewritten or removed, and DRA-03 and BT-09 are left with a dangling citation. The consequence set claims to be "fixed regardless of outcome" (HARD, line 130-134), so it must enumerate *every* row that cites the moving test file. Add DRA-03 and BT-09 to the set, or state explicitly why their `test_dual_resolution.py` citation survives the move untouched.

**L3-3 · Direct claim (internal contradiction):** REQ-PGD-08 is listed in two places with conflicting dispositions. §3 (line 52) lists it as divergent-PASS ("cited file doesn't cover the claim"). §5 (line 72) lists it among the 7 no-marker rows with the directive "Verify and add [markers]." But discovery §D7 says coverage exists "for all but PGD-08" (`discovery:233`) — meaning PGD-08 has *neither* a marker *nor* real coverage. You cannot add a `# REQ-PGD-08` marker to a test that doesn't pin the claim. The two instructions collide: §5 says add a marker, §3 says the coverage is absent. Reconcile — PGD-08's real fix is a genuine test or a re-frame (the §3 path), not a marker (the §5 path). The spec should pull PGD-08 out of the "add markers to all 7" instruction and route it through the divergent-row disposition only.

### Lens 4 — Hygiene

None material. The spec follows the contract's section shape, the tags are present and honest, and the Related Artifacts / re-verify list is concrete.

### Lens 5 — Reader Comprehension

**L5-1 · Rewrite request (minor):** The Problem section's seven groups mostly work — each leads with a bold plain claim before the identifier detail, which is the method working. The exception is groups 1 and 2, which run 15+ lines of dense, comma-spliced identifier prose (line 21-35, 37-46) before a reader can catch a breath. A tired reviewer opening the epic's largest item hits a wall there. Not a blocker — the bold lead sentences carry the gist — but if it's cheap, breaking groups 1 and 2 into 2–3 short sub-points each (the claim; the evidence; the "why it's stuck") would let the section be skimmed rather than parsed. Lower priority than any Lens 2/3 finding.

---

## Engagement Summary

**Overall take:** This is a strong, faithful spec — the code claims that matter all verified true, the tags are honest, and the F4 posture (presumption + probes, verdict deferred to design) is exactly right. It is not Approve-ready only because two of the three F4 kill-probes are too soft to force a real verdict, and the ~175-row sweep has no leash. Both are fixable with targeted edits; the work item is sound.

**Here's what I need you to weigh in on (must-fix, ranked):**

1. **[L2-1]** Make F4 kill-probes (ii) and (iii) produce **named evidence artifacts** — the Strategy-D key-set diff against specified corpora, and the both-directions divergence inventory — so the "land the cutover" presumption can't win by default. Probe (i) is fine; enumerate its fixture set. **This is the top fix: it's the difference between "design ran the probes" and "design assumed the answer."**
2. **[L3-1]** Put a **stopping rule** on the ~175-row sweep and **define the D7 heuristics** concretely, or the sweep can eat the whole 1.5–2 day budget. Require it to `log` what it did not deep-read.
3. **[L3-2]** Add **DRA-03 and BT-09** to the F4 consequence set (both cite `test_dual_resolution.py`), or state why their citation survives the move. The set claims to be complete "regardless of outcome"; right now it isn't.
4. **[L3-3]** Reconcile **PGD-08's double listing** — it's tagged both "add a marker" (§5) and "coverage is absent" (§3). Those contradict; route it through the divergent-row fix only.
5. **[L1-1]** Recount the **"24 skipifs"** — the real number is 22. Small, but this item can't ship a stale count in its own contract. (Or drop the number.)
6. **[L1-2, L2-2]** Two quick calls: should **PGD-08** get the "re-verify at implement" caveat EXT-09 got (its row moved since discovery)? And should **F2** carry a presumption like F4 does, or stay fully open?

---

## Resolutions

*(To be filled in during Stage 5 as the reviewer resolves each finding, keyed by ID. The spec agent reads this section to incorporate the review; the reviewer does not edit the spec directly.)*

- **[L2-1]**
- **[L3-1]**
- **[L3-2]**
- **[L3-3]**
- **[L1-1]**
- **[L1-2]**
- **[L2-2]**

---

**Verdict:** **Revise.** The work item is sound and the spec is faithful and well-grounded — every load-bearing code claim verified true. It needs targeted edits before it becomes the design contract: harden the two soft F4 probes (L2-1), leash the sweep (L3-1), close the two atomicity gaps (L3-2, L3-3), and fix the stale skipif count (L1-1). None of these touch the spec's direction.

**Next Steps:** Once resolutions are recorded here, re-run `/_my_spec` (or return to the spec-agent session) and point it at this review to incorporate. The reviewer records resolutions in this file; the review agent does not edit `spec.md`.
