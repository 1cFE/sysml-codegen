# Spec Review: Self-Binding Replacement (rev 5)

**Spec:** `.project/active/self-binding-replacement/spec.md` (rev 5, 2026-08-16)
**Contract:** `claude-pack/commands/_my_spec.md`
**Review File:** `.project/active/self-binding-replacement/spec-review.md`
**Date:** 2026-08-16
**Prior review:** `spec-review-20260815-rev3.md` (rev-3 Revise verdict + owner resolutions, archived
under that name so the spec's `[NEED]` citations keep resolving; this file is the fresh rev-5 review)

**Conflict-of-interest disclosure:** the rev-5 accuracy edits were made this session by the same
agent writing this review, at owner direction. The review treats those edits as suspect on the same
terms as the rest of the spec; two findings below (L1-1, L5-1) are against them.

---

## Reality Check

**Sound.** The work item is real and correctly framed: the self-named binding (`in R = R`) is
refused by the shipped route, the customer models carry it, and the published guidance still
teaches it. Every load-bearing claim was re-verified today against code and repos:

- `SI_SELF_BINDING` refusal sites confirmed (`src/sysml_codegen/extraction/source_evidence.py:227-230`,
  `src/sysml_codegen/elaboration/elaborate.py:2004-2005`).
- Fusion-tea self-binding count re-measured: **15**. Stellarator: **114**, literal `in R = R` at
  `models/designs/generic_mfe/mfe_plant.sysml:117`.
- The four refused examples in `agentic-mbse/docs/patterns/plant-idiom.md` confirmed at lines 79,
  84, 85, and the EXPOSE example at 200.
- The `[NEED]` owner quote appears verbatim in the epic at `:71-78`; the critical success factor and
  mission invariant are at `:31-33` and `:84-86` as cited; contract D-4 sits at `:604` as cited.
- The stocktake report exists and validated both scope calls
  (`.project/research/20260815-103905_item8-bounded-stocktake.md`).
- The archived rev-3 review carries every resolution the spec's `[NEED]`/`[INFERRED]` rows cite
  (L1-2/L2-2/L3-3 at `:366`, L3-4 at `:419`, L3-2 at `:432`).
- `tests/conformance/test_usage_owned_reference_anchoring.py` exists and pins post-repair behavior.

The spec would not badly mislead design. The findings below are targeted.

---

## Audit

### Lens 1 — Faithfulness

**L1-1 · Direct claim + rewrite request (against the rev-5 edit):** The `[HARD]` qualified-reference
row draws the supersession boundary too narrowly, and asserts it without evidence. It says the
spike's **u4–u7 and arrayed** rows are superseded by the anchoring repair — but *every* row in
`spike/findings.md` was measured on the pre-repair resolver at `6e3c18d`, and the repair rewrote the
shared one-segment arm those measurements exercised. The evidence that the D-5/D-7 rows survive
exists — the anchoring item's corpus adjudication shows 404 of 409 sites unchanged with zero
edge drift outside the five repaired sites — but the spec neither cites it nor extends it to F-2
through F-5, which were never corpus sites and have **no** post-repair evidence at all (see L3-2).
What needs to be true: the row states which spike measurements are superseded, which are proven
to survive (with the citation), and which are simply unmeasured on the repaired resolver.

**L1-2 · Question to the user:** The `[NEED]` owner quote drops its bookends — *"all I care about
is:"* and *"that's it, that's all I care about."* The design (`design.md:48-54`) quotes them in full
and calls them "the scope limiter," i.e. load-bearing payload against gold-plating. Compression law
says owner payload survives at the owner's emphasis. Should the spec's `[NEED]` carry the full
quote? Cheap to fix, and it prevents a future reading of the `[NEED]` as a floor without a ceiling.

### Lens 2 — Problem & Approach

**L2-1 · Direct claim (design-facing, recorded here so it isn't lost):** The guidance's *reason*
for not recommending D-6 has changed under it. Pre-repair, the danger was silent mis-wiring;
post-repair, the arrayed case refuses loudly and the scalar case anchors the exact owner. The
ratified D-5 recommendation stands (`[OWNER 2026-08-15]`, ruling 3), but any guidance prose that
justifies it by the old silent-failure behavior would be false the day it ships. SC4's "never
presents positional slot search as the language semantics" covers half of this; the design's D-6
section must derive its cautions from post-repair behavior.

**L2-2 · Question to the user:** Who teaches the arrayed aggregation split? The re-audit measured
that `sum(comp_a::length)` refuses while `sum(comp_a.length)` aggregates both occurrences silently
— carried as `independent-audit-F1` toward the *anchoring* item's close. But the only
guidance-writing vehicle in flight is **this** item, and its Success Criteria say nothing about
arrayed shapes. If F1's disposition turns out to be "document it," does that documentation land in
this item's guidance rewrite (scope grows by one taught shape), or in a separate follow-up (two
hands editing the same guidance docs)? Deciding now avoids a scope surprise mid-implementation.

### Lens 3 — Pipeline Risk

**L3-1 · Question to the user (spec-stage, answerable now):** The Open Question "ADR owner call —
whether the lasting modelling rule should be promoted to ADR-010" is contradicted by the design,
which already commits to it: D9 at `design.md:366-367` says "ADR-010 **is filed**" and the
deliverables table repeats it. Either the owner decides now (the question is answerable — nothing
blocks it), or the design must un-commit. As written, the pipeline ships an owner decision nobody
made.

**L3-2 · Direct claim:** The spec's Related Artifacts row presents F-2 (validator false positive),
F-3 (unhandled `GraphValidationError` traceback out of `graph.py:448`), F-4, and F-5 as live
measured findings, and the design plans an F-3 repair in `elaboration/elaborate.py` and
`elaboration/graph.py`. All four were measured pre-repair, and the anchoring repair rewrote the
resolver region the F-3 repair targets. Whether F-2/F-3 still reproduce — and in the same shape —
is unknown. The spec should mark these "re-establish on the repaired resolver before design relies
on them," the same discipline its own Provenance note applied to the reverted work.

**L3-3 · Rewrite request:** The "Provenance note on measured requirements" governs a marker no row
carries anymore ("measurement pending re-establishment" — nothing in rev 5 is so marked). It reads
as vestigial. Either delete it or repurpose it to govern the new post-repair re-establishment
obligation from L1-1/L3-2 — that is exactly the situation it was written for, one revision later.

### Lens 4 — Hygiene

**L4-1 · Rewrite request:** The header still pins `Branch: main (codegen 9ce5548)` — roughly 30
commits and one landed repair behind the tree the spec now describes. Rev 5's claims were checked
at today's HEAD; the header should say what baseline the current revision speaks from.

### Lens 5 — Reader Comprehension

**L5-1 · Rewrite request (against the rev-5 edit):** The rewritten `[HARD]` qualified-reference row
is one nineteen-line bullet carrying five separate facts (repair status, re-audit status,
supersession, the arrayed refusal, the aggregation split). A tired engineer cannot pull one fact
out of it. Split it: one row for the repair's state and authority, one for what supersedes what
(per L1-1), one for the guidance-bearing post-repair facts.

**L5-2 · Rewrite request (against the rev-5 edit):** SC2 now reads "checked against the landed
exact-owner repair, not the repaired positional defect" — "repaired X" as the thing *not* to check
against parses backwards. Say it plainly: checked against the shipped post-repair behavior, never
against the superseded positional behavior.

---

## Engagement Summary

**Overall take:** The item is sound and the spec is fundamentally accurate — every code-facing and
provenance claim re-verified clean today. The faults that remain are seams from the anchoring
detour: the spec updated its headline fact (the repair landed) but not the evidence boundary
underneath it (which pre-repair measurements still count), and two decisions the pipeline needs are
sitting undecided while the design has silently pre-answered one of them.

**Here's what I need you to weigh in on:**

1. **[L3-1]** ADR-010: the spec parks it as your call; the design already filed it. Decide —
   promote the rule to ADR-010, or strike it from the design.
2. **[L2-2]** The arrayed `::`-vs-`.` aggregation split: if it needs documenting, does that land in
   this item's guidance rewrite or in the anchoring item's follow-up? One sentence from you fixes
   the scope boundary.
3. **[L1-1, L3-2, L3-3]** Approve the re-establishment rule: spike rows u4–u7/arrayed are
   superseded; D-5/D-7 rows survive on the corpus-adjudication evidence (cite it); F-2 through F-5
   are unmeasured post-repair and must be re-established before design relies on them. The spec's
   own Provenance note should be repurposed to say this.
4. **[L1-2]** Restore the owner quote's bookends ("all I care about is… that's it") in the `[NEED]`
   row? The design treats them as the scope ceiling; the spec dropped them.

---

## Resolutions

*(Filled in as the owner resolves findings; keyed by ID.)*

---

**Verdict:** Revise
**Next Steps:** Record resolutions here, then fold them into the spec (rev 6) and re-run the
product lens — rev 5 has not had a lens pass. The design review that follows this review already
evaluates the design against the landed repair; its findings supersede the design-facing halves of
L2-1 and L3-1.
