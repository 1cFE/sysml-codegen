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

> **Evidence update, 2026-08-15 14:27 — the gating measurement has since returned**
> (`.project/research/20260815-142743_bare-expression-side-measurement.md`). This is evidence, not
> a resolution; L1-1 remains the owner's call.
>
> **Zero of the 126 change.** 91 join to an exact typed wire edge and all 91 compare equal; 35 are
> unjoinable, each for a named structural reason. So the risk L1-1 raises did not materialize, and
> the owner's choice is retrospectively safe.
>
> **But the equality is forced, not earned**, and that distinction should survive into the spec.
> Every joined bare site has leaf-slot fan-out of one — a single occurrence in the whole model
> carries the referenced slot — so the lineage walk and the owner-anchored walk *cannot* land
> differently. The qualified corpus has discriminating topologies (4 sites at fan-out two, and they
> are 4 of the 5 changed); the bare corpus has none. Zero changes here is a no-cost result, not a
> certification of the broader predicate.
>
> **Two coverage holes survive, and they bear directly on L2-2 and SC 6.** The corpus contains **no**
> usage-owned direct reference in a typed alias and **none** in an inline constraint predicate — the
> two callers the shared repair is principally justified by. It also has no plural (`sum()`) bare
> site and no discriminating bare topology. The measurement recommends authored probes; SC 6 already
> requires exactly those four regression families, so the spec is doing the right work here — but SC
> 6 should be read as the *only* evidence covering those callers, not as supplementary.
>
> **The measurement also corrects the corpus scan's composition of the 126**: only 76 are new caller
> coverage (computed-attribute terms), 15 are constraint bindings sharing the same `_resolve_bindings`
> caller as the calc bindings, and **zero are aliases or predicates**. The scan's 63-vs-62 calc
> binding count is one `non_finite_literal` site whose root refuses elaboration, not a disagreement.
>
> **On narrow-vs-broad, the measurement recommends broad** — the narrow option is genuinely
> available (authored text was recovered from CST byte spans for all 189 sites), but its whole
> purpose is to shield bare sites from a change that measures at zero, at the cost of threading
> authored-form evidence through three callers that share one resolver and know nothing about
> spelling.

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

`[OWNER 2026-08-15]` **"All changes should be made."** Every finding is accepted for incorporation.
Recorded per finding below, with the two decision-shaped items ruled by the orchestrator under the
standing no-reserved-gates ruling and marked `[AGENT]` so they stay challengeable.

- **[L1-1]** Accepted. The gating measurement returned before resolution
  (`.project/research/20260815-142743_bare-expression-side-measurement.md`): **zero of 126 change**,
  so the broader invariant is retrospectively safe and stays `[NEED]`. The spec must cite the
  measurement as its basis **and carry the caveat that the equality is forced, not earned** — every
  joined bare site has leaf-slot fan-out of one, so the two walks could not have differed. The zero
  is a no-cost result, never evidence of correctness. Both halves are required; citing the count
  without the caveat is the failure mode this resolution exists to prevent.
- **[L1-2]** Accepted. Regrade the u4–u7 promotion row `[INFERRED]` → `[NEED]` (owner-stated), or
  soften the sentence if the owner did not in fact state it. Prefer the regrade.
- **[L1-3]** Accepted. `self-binding-replacement/spec.md` is at rev 4 and already carries the
  corrected D-6 description. Restate the requirement and its success criterion as **what remains**,
  so the criterion is falsifiable at approval instead of vacuous.
- **[L1-4]** Accepted. Reframe the Problem section around contract `:618-626` — D-6 ratified
  "usage qualifier → occurrence-level feature" on 2026-08-05, so this item **restores conformance to
  a ratified disposition** rather than introducing an invariant.
- **[L1-5]** Accepted. Verify the `[OWNER-VERBATIM]` quote character-for-character. Keep the typo if
  genuine; drop the verbatim stamp if transcribed.
- **[L2-1]** Accepted. Record the *reasoning* behind the broad-over-narrow choice, not just the
  choice: the narrow option is genuinely available (authored text is recoverable from CST byte spans
  for all 189 sites) but exists to shield bare sites from a change measuring at zero, at the cost of
  threading spelling evidence through three callers that share one resolver and know nothing about
  spelling.
- **[L2-2]** Accepted. SC 7 must require each change **adjudicated fix-or-regression with reasoning**,
  not merely attributed to the invariant. Note also that the bare surface classification SC 7 asks
  for has now been performed once; the `[INFERRED]` re-derivation row still governs at implementation
  time, so state SC 7 as re-derive-and-confirm rather than as first-time work.
- **[L2-3]** `[AGENT]` **Ruled: the documentation tail stays in this item, and the spec names its
  verifier.** L1-3 shrank the tail to the guidance-surface inventory alone, since the self-binding
  spec is already corrected. A tail that small, split out, becomes an orphan nobody re-opens — and
  the stale explanation it removes is the exact hazard this item exists to end. Keeping it costs one
  named owner; splitting it risks the correction never landing.
- **[L3-1]** Accepted. Resolve the SC 2 / Non-Goal 5 conflict explicitly. A package-level `part` is a
  `PartUsage`, so the carve-out is believed to govern and u4's change is in scope — but the spec must
  say so rather than leave two adjacent readings that disagree.
- **[L3-2]** Accepted. Give SC 9 (strict/lenient parity) a backing requirement, or cite the existing
  invariant it inherits from.
- **[L3-3]** Accepted. State what happens if the no-recapture prediction proves wrong — specifically
  whether a stale snapshot carrying a mis-anchored edge is **detectable** after the repair or replays
  silently with the old wiring. A silent replay would displace this item's own failure mode into the
  snapshot route and needs a criterion, not an assumption.
- **[L3-4]** Accepted. The "how are the 126 joined" open question is answered by the measurement.
  Remove it or restate whatever genuinely remains open.
- **[L4-1]** Accepted. `$my-design` → `/_my_design`.
- **[L5-1]** Accepted. Explain what a "one-segment reference" is, and why one versus two segments
  decides the outcome, before the `comp_a::length` example.
- **[L5-2]** Accepted. Gloss `u4`–`u7` in the success criteria so they are readable without the spike
  findings open.

### Two additions from the measurement, to incorporate alongside the findings

- **[M-1]** The corpus contains **no** usage-owned direct reference in a typed alias and **none** in
  an inline constraint predicate — the two callers the shared repair is principally justified by —
  plus no plural (`sum()`) bare site and no discriminating bare topology. SC 6 already requires those
  regression families; the spec must state that SC 6 is therefore the **sole** evidence covering
  those callers, not one source among several.
- **[M-2]** The measurement corrects the corpus scan's composition of the 126: 76 are new caller
  coverage (computed-attribute terms), 15 are constraint bindings sharing the `_resolve_bindings`
  caller with the calc bindings, and zero are aliases or predicates. The scan's 63-vs-62 calc-binding
  count is one `non_finite_literal` site whose root refuses elaboration, not a disagreement. Any spec
  text inheriting the scan's numbers should inherit the corrected ones.

---

**Verdict (rev 1):** **Revise** — superseded by the re-review below.

---

# Re-review — spec rev 2 (2026-08-15)

**Subject:** `spec.md` rev 2, at codegen `c615eb4`. **Verdict: Approve.**

## Method

I verified the edits against the spec and against source, not against the revision record. The
revision summary accounted for 15 of 17 IDs, so I checked the two it omitted (**L2-2**, **L3-3**)
directly: both did land — the summary was incomplete, the work was not. Independent checks:

- **L1-4's D-6 citation** — `constraint-execution-authoritative-lifecycle-contract.md:618-626` reads
  as quoted, ratified 2026-08-05. Confirmed independently in the rev-1 audit and again here.
- **L3-2's new citation** — `elaborator-design/design.md:320-324` and invariants 10–12 at `:374-376`
  do say strict/lenient may change halt-versus-report behavior and never identity. The criterion now
  traces to a real inherited invariant.
- **L3-1's fix** — Non-Goal 5 now states that a `PartUsage` declared at package scope is still
  usage-owned and remains in scope, naming the u4 shape. The contradiction with SC 2 is gone.
- **Provenance census** — 3 `[NEED]`, 9 `[INHERITED]`, 4 `[INFERRED]`, **zero `[HARD]`**. No
  mechanism is dressed as a constraint, which was the tag failure most worth watching for here.

## What the revision did better than asked

**A criterion nobody requested, and it is the best edit in the pass.** The measurement's
forced-not-earned caveat could have been absorbed as a disclaimer and forgotten. Instead the spec
adds a criterion requiring a kept bare-reference regression with a *discriminating topology* — one
where consumer-lineage and exact-owner selection can land on different occurrences — that "fails if
the implementation merely preserves the corpus's accidental fan-out-of-one equality." That converts
a caveat into a tripwire. It is the difference between recording that the evidence was weak and
refusing to let the weakness pass silently into implementation.

**M-1 landed with its numbers.** The alias/predicate criterion carries the specific counts (9 direct
alias leaves, 17 direct predicate leaves, all definition-owned; 18 usage-owned predicate references
on unasserted constraints reaching no node) with a line-cited source, and states outright that
dropping the criterion "strips the shared-resolver justification of all its evidence." A reader can
now see why that criterion is load-bearing rather than taking it on faith.

**L1-5 was flagged, not resolved away.** No second in-repo source for the `[OWNER-VERBATIM]` quote
exists, so the spec says the grade rests on the preserved misspelling alone and names the downgrade
path. That is the correct handling of an unverifiable provenance claim: surface it, do not launder it.

## Findings

None blocking. Two residuals, neither a spec defect:

**R-1 · Owner item — the only thing an agent cannot close.** The `[OWNER-VERBATIM]` grade on *"also
repair the self-biding spec"* has no corroborating record anywhere in the repository. `[OWNER-VERBATIM]`
is the strongest grade in the vocabulary, and it currently rests on a preserved typo. One confirmation
from Reid closes it; absent that, the spec's own named downgrade to `[OWNER]` applies. Nothing
downstream depends on the distinction, which is why this is a residual and not a finding.

**R-2 · Process gap — the product-lens pass did not run.** The spec agent could not read
`~/.claude/scripts/product-lens.md` (outside the session's allowed directory) and correctly declined
to write a lens verdict it had not derived. `product-lens.md` still carries `Gate: CLEAR` from rev 1.
The rev-2 changes add citations, evidence, and two strengthened criteria and narrow nothing, so the
prior gate is unlikely to move — but that is judgment, not a lens result, and the lens should be run
before design starts.

## Verdict

**Approve.** I would bet the design on this spec as written.

The item is now better argued than when it was drafted: the qualified half is conformance restoration
to a disposition ratified 2026-08-05 rather than new semantics; the broader half rests on returned
evidence rather than on a choice made ahead of it; and the weakness in that evidence is pinned by a
criterion that fails if implementation exploits it. The two callers with no corpus coverage are named
as such, with the consequence of dropping their regressions stated in the criterion itself.

**Next Steps:** Run the product-lens pass (R-2), confirm or downgrade the verbatim grade (R-1), then
proceed to `/_my_design`. Neither residual blocks design from starting.
