# Spec Review: Exact Owner Anchoring for One-Segment References

**Spec:** `.project/active/qualified-reference-occurrence-anchoring/spec.md`
**Contract:** `claude-pack/commands/_my_spec.md`
**Review File:** `.project/active/qualified-reference-occurrence-anchoring/spec-review.md`
**Date:** 2026-08-15

---

## Reality Check

**Sound.** The spec is about the right work item, the Problem section is materially accurate, and I
verified its load-bearing code claims rather than trusting them. Two checks worth recording: the
`owner_is_definition` warning is correct — the field is a plain `bool = False`
(`../agentic-mbse/.../data_models.py:63-73`), so a package owner satisfies `not owner_is_definition`,
and **codegen currently consumes that field nowhere**, so insisting on
`SysideAdapter.is_instance(owner, "PartUsage")` is right. The multi-caller claim is also real:
`_expression_references` (`elaborate.py:2543-2552`) builds one-segment facts independently of
extraction for four callers (`:1051`, `:2384`, `:2458`, `:2587`).

The findings below are corrections and one sequencing problem, not a redirection.

---

## Audit

### Lens 1 — Faithfulness

**L1-1 · Question to the user (highest stakes):** The spec records the broader-invariant choice as
`[OWNER, 2026-08-15]` and `[NEED]`, i.e. settled. But the evidence that was explicitly sequenced to
*precede* that decision — the edge-level comparison of the 126 bare expression-side sites — **has not
returned yet.** The corpus scan named this exactly: it offered a narrow option and a broad one and
said the broad one "requires the broader evidence." The agreed sequencing was to measure first
"because if an edge changes, we need to judge whether that change is a fix or a regression, and that
judgment gets much harder once there is a diff to defend."

So the spec's central bet is currently settled ahead of its own gating evidence. That may be
perfectly fine — you can choose the broader invariant on architectural grounds and treat the
measurement as informing implementation only. **But the spec should say which it is.** As written,
`[NEED]` makes the choice hard to challenge, and if the measurement returns regressions there is no
recorded route back. Two clean options: mark the choice contingent on the measurement, or state
plainly that it was made on architectural grounds and the measurement cannot reopen it.

**L1-2 · Direct claim:** The u4–u7 promotion requirement is tagged `[INFERRED]` while its own text
says *"The owner explicitly authorized both as scope for this separate item (2026-08-15)."* Those
contradict. Per the capture-fidelity absorb mapping, owner-stated → `[NEED]`; `[INFERRED]` is for
what was implied, not stated. Either the tag is wrong or the sentence overstates the owner's words.

**L1-3 · Direct claim:** The `[NEED]` requiring correction of
`.project/active/self-binding-replacement/spec.md`, and the final Success Criterion resting on it,
are **substantially already discharged**. That spec is now at rev 4 and its D-6 bullet already
describes the positional behavior as codegen defect F-6, names this item as the owner of the repair,
and says the item "must not teach the defect as a modeling rule"; its Success Criteria at `:66-70`
and `:74-78` were rewritten to match. The spec should state what *remains* to be corrected rather
than requiring work already done — otherwise the criterion is vacuous at the moment of approval and
nobody can tell whether it was satisfied by this item or before it.

**L1-4 · Rewrite request:** The spec undersells its own authority, and the correction makes the item
easier to approve. I verified contract `:618-626`: **D-6 already ratifies exactly the target
behavior** — *"usage qualifier → occurrence-level feature."* So this repair does not introduce a new
invariant; it **restores conformance to a disposition ratified 2026-08-05** that the shipped route
deviates from. That framing changes how the risk reads (conformance restoration, not semantic
change) and it directly answers the "are we inventing occurrence semantics for `::`?" worry that
dominated the investigation. The `[INHERITED]` row cites D-6 but the Problem section does not use it.

**L1-5 · Question to the user:** The Problem quotes `[OWNER-VERBATIM, 2026-08-15]` as *"also repair
the self-biding spec."* If that is genuinely verbatim, keep the typo and leave it. If it was
transcribed, the verbatim stamp is doing work it hasn't earned. Worth one check, because
`[OWNER-VERBATIM]` is the strongest grade in the vocabulary.

### Lens 2 — Problem & Approach

**L2-1 · Direct claim:** The central bet is recorded as a choice but not as *reasoning*. The spec
says the owner picked the broader invariant "after being presented the qualified-only and broader
alternatives" and never records **why**, or what the narrow option would have cost. The corpus scan
priced the narrow option concretely — carry authored-form evidence into every shared resolver caller
— and that cost is absent here. Without the reasoning, a future challenge to this decision has
nothing to re-derive against, which is precisely what the settled-item discipline exists to prevent.

**L2-2 · Direct claim:** Success Criterion 7 sets a weaker bar than the work needs. It requires that
"every change is explained by the exact owner invariant" and that there are "zero unclassified
semantic differences." **A change can be fully explained by the invariant and still be a
regression** — for instance an alias or predicate that resolves usefully today and, under owner
anchoring, refuses because the exact owner has no occurrence in that consumer's context. Explanation
is classification; it is not a correctness judgment. The criterion needs each change adjudicated
fix-or-regression, with reasoning, not merely attributed to the invariant.

**L2-3 · If-then tradeoff:** Sizing. Twelve success criteria spanning a resolver change, a 126-site
classification, four new regression families, a public mutation proof on two routes, strict/lenient
parity, snapshot classification, **and** correcting a second spec plus guidance surfaces. That is
coherent as one causal story, but the documentation-correction tail is separable from the resolver
repair and has a different reviewer, different risk, and different done-condition. **If** you want
this item to land fast and be auditable as a semantics change, split the doc tail out. **If** you
want the stale explanation to be impossible to forget, keep it — but then say who verifies it, since
nothing in the criteria names an owner for the guidance-surface inventory.

### Lens 3 — Pipeline Risk

**L3-1 · Direct claim (contradiction):** Success Criterion 2 and Non-Goal 5 appear to conflict.
SC 2 requires the promoted u4 case to resolve `shared_component::length` to a **package-level**
`shared_component.length` with no occurrence diagnostic — u4 measured as `SI_OCCURRENCE_MISSING`
today, so this is a behavior change on a package-level owner. Non-Goal 5 says the item does not
change "package-owner semantics," with the carve-out that "exact owner anchoring still applies when
those callers resolve a one-segment usage-owned reference." The carve-out may resolve it — a
package-level `part` usage is a `PartUsage`, so the branch legitimately fires — but the spec is
relying on the reader to work that out. Two adjacent readings, one of which forbids what a success
criterion mandates, is exactly the ambiguity that produces a wrong implementation. State which it is.

**L3-2 · Direct claim (missing requirement):** Success Criterion 9 (strict and lenient elaboration
agree on semantic identity, with lenient recording the exact diagnostic multiset) has **no backing
requirement**. Every other criterion traces to a `[NEED]`, `[INHERITED]`, or `[INFERRED]` row; this
one is asserted only as an acceptance condition. Either it is inherited from an existing invariant —
in which case cite it — or it is a new obligation that needs a tagged requirement.

**L3-3 · Question to the user:** The `[INHERITED]` snapshot row states that snapshots hold resolved
final edges and cannot rerun owner selection, so "a changed live edge requires recapture; replay
cannot repair an old edge." The corpus scan predicts no recapture is needed, so this is probably
moot — but the spec never says what happens **if the prediction is wrong**. Specifically: is a stale
snapshot carrying a mis-anchored edge *detectable* after the repair, or does it replay silently with
the old wiring? If the latter, that is the same silent-wrong failure mode this item exists to delete,
displaced into the snapshot route, and it deserves a criterion rather than an assumption.

**L3-4 · Rewrite request:** The Open Questions list is well-formed except for one item that reads as
spec-stage, not design-stage: *"How the 126 already-inventoried bare expression-side consumers are
joined to stable before/after edge records."* That is the method of the measurement currently in
flight, and its answer arrives before design starts. It should either be removed as answered or
restated as whatever genuinely remains open once the measurement lands.

### Lens 4 — Hygiene

**L4-1 · Rewrite request:** `**Next Steps:** After approval, proceed to `$my-design`` — the command
is `/_my_design`. Trivial, but it is the last line a reader acts on.

### Lens 5 — Reader Comprehension

**L5-1 · Rewrite request:** The spec's title, every success criterion, and most requirements turn on
the phrase **"one-segment reference"**, and the spec never explains what a segment is or why one
versus two decides the outcome. That distinction *is* the defect: a two-segment reference
(`driver.cost`) carries a root the resolver can anchor an occurrence on, so its leaf lookup happens
inside an already-fixed occurrence; a one-segment reference has no root, so the collapsed slot ends
up doing occurrence selection. A reader who does not already know that cannot evaluate a single
criterion in this document, and the reader most likely to review it is the one who has not spent the
day in `_resolve_leaf`. Two or three plain sentences in the Problem section, before the sharp
`comp_a::length` example, would fix it.

**L5-2 · Rewrite request:** Success Criteria 2–5 are written as `u4`/`u5`/`u6`/`u7` probe names with
no gloss. Those names are meaningful only to someone holding the spike findings open. Each needs a
few words saying what shape it is — as SC 4 nearly does when it mentions "the competing enclosing
`plant.comp_b.length`."

---

## Engagement Summary

**Overall take:** The work item is sound and better-founded than the spec claims — D-6 already
ratified this exact behavior in August, so this is conformance restoration, not new semantics, and
the spec should say so. The one real problem is sequencing: the central bet is recorded as settled
while the evidence that was explicitly ordered to precede it is still running. Everything else is
correction — two tag/provenance errors, one contradiction, one already-discharged requirement, and a
comprehension gap around the term the whole document rests on.

**Here's what I need you to weigh in on:**

1. **[L1-1]** The broader-invariant choice is stamped `[NEED]` settled, but the 126-site measurement
   that was sequenced to precede it hasn't returned. Decide: is the choice contingent on that result,
   or was it made on architectural grounds such that the measurement can only inform implementation?
   Whichever it is, the spec should say it — right now there's no recorded route back if the
   measurement returns regressions.
2. **[L2-2]** SC 7 asks that every change be *explained by* the invariant. That's classification, not
   correctness — a change can be explained and still be a regression. Should it require a
   fix-or-regression adjudication per change?
3. **[L3-1]** SC 2 mandates a behavior change on a package-level owner that Non-Goal 5 appears to
   forbid. Probably resolved by the carve-out, but two adjacent readings shouldn't disagree about
   what's in scope.
4. **[L1-4]** D-6 (contract `:618-626`) already ratifies "usage qualifier → occurrence-level
   feature." Reframing the item as restoring conformance to a ratified disposition — rather than
   introducing an invariant — makes it materially easier to approve. Worth doing.
5. **[L1-3]** The requirement to correct the self-binding spec is largely already done at rev 4.
   Restate it as what remains, or the criterion is unfalsifiable at approval time.
6. **[L2-3]** Decide whether the documentation-correction tail stays in this item or splits out. If
   it stays, name who verifies the guidance-surface inventory.
7. **[L1-2]** Tag error: u4–u7 promotion is `[INFERRED]` but its text says the owner explicitly
   authorized it. Fix the tag or soften the sentence.

---

## Resolutions

*(To be filled in as findings are resolved. Keyed by finding ID.)*

---

**Verdict:** **Revise** — the underlying work item is sound, and one finding (L1-4) makes it stronger
than the spec currently argues. The edits are corrections plus one sequencing decision that only the
owner can make.

**Next Steps:** Record resolutions above, then re-run `/_my_spec` (or return to the spec-agent
session) pointed at this review to incorporate. The reviewer does not edit the spec. Note that
**L1-1 should be resolved after the 126-site measurement returns**, since its result may itself be
the answer.
