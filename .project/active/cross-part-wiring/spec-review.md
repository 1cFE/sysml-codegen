# Spec Review: Cross-Part Channel Wiring (SC-5 stage 2)

**Spec:** `.project/active/cross-part-wiring/spec.md`
**Contract:** `claude-pack/commands/_my_spec.md`
**Review File:** `.project/active/cross-part-wiring/spec-review.md`
**Date:** 2026-07-05

---

## Reality Check

**Concerns (Revise, not Rework).** The spec is about the right work item, the Problem
is directionally accurate, and its load-bearing discovery is **verified correct**: the
ife_plant fixture has no stage-(b) edge — `lcoe_calc` binds all 14 inputs to
plant-level literals, and the nested calc outputs (`driver_cost`, `chamber_yield`,
`cooling_power`) are consumed by no cross-part calc. The only committed cross-part
channel is shape 4.

But two things do not hold up under inspection, and both touch the headline:

1. The spec attributes the flip of the two committed V11 pins to the wrong mechanism.
   The pins are blocked by a *feature-chain-through-a-nested-part* classification, not
   by the PartDef-vs-PartUsage EXPOSE guard the spec's scope names. Implemented
   literally, the four scope pieces may not flip either pin.
2. The stage-(b) fixture gap is offered as a design *option* that includes breaking a
   HARD constraint (R1). A HARD constraint can't be one horn of a design choice.

Neither is fatal — the work item is right and the substrate is real — so this is a
Revise. But finding L1-1 is high-stakes: it changes what "stage (a)" actually is.

---

## Audit

### Lens 1 — Faithfulness

**L1-1 · Direct claim (highest stakes):** The spec's stage-(a) scope, implemented as
written, may not flip either committed V11 pin. Both pins are the *same* shape: a
cross-package binding to `radial_build.magnet_volume_total`
(`tests/fixtures/ife_plant/design.sysml:39`), where that attribute is
`tf_coil.volume_calc.volume` — a 3-segment feature chain reaching a calc output
**through the nested `tf_coil` part** (`subsystems.sysml:12`). `radial_build` is a
plain part *usage*. Two facts make this pin, not the spec's scope piece #3:

- The attribute is currently classified **FORMULA**, not EXPOSE_PURE. The classifier
  (`computed_attribute_extractor.py:95-109`) excludes EXPOSE_PURE whenever a sibling
  ref is present, and `tf_coil` is a sibling ref → FORMULA → dropped from
  `design_attributes` with a compile warning. That drop *is* why the consumer falls
  through to the fallback EP the collector pins. (Matches the recorded finding in
  `[[cross-part-binding-v11-fallthrough]]`.)
- `_resolve_expose_pure` (`graph_builder.py:759-803`) only ever builds a **2-segment**
  `instance.output` key (`:789`). It has no notion of a middle part segment, so it
  cannot resolve a `part.calc.output` chain even if the classification were fixed.

Scope piece #3 ("PartDef-level EXPOSE_PURE ... revises REQ-CA-03's `not is_part_def`
guard", spec `:89-94`) targets a *different* gap — the wi014_toy shape-A / SC-7
name-drop, where the EXPOSE sits on a part **def**. It does nothing for a plain-usage
feature-chain-through-a-nested-part. **The missing scope piece is multi-hop
EXPOSE-through-a-nested-part handling** (reclassify the 2-hop chain out of FORMULA into
an alias, and construct an N-segment alias key). Without it, "stage (a) alone flips
both committed V11 pins" (spec `:145`, `:56`, and the split economics) does not hold.
Recommend the spec name this mechanism explicitly and re-derive success criterion #1
against it. (This is exactly the "verify the fixture trace at design" flag the spec
itself raised — the trace confirms the gap is real.)

**L1-2 · Direct claim / Question to the user:** R1 is listed as a **[HARD]** constraint
— "New behavior lands with a real fixture + snapshot" (spec `:106-107`). But Open
Questions offers, as an acceptable design choice, "**(ii) accept live-only verification
for stage (b) and record the R1 exception**" (`:160-161`). You cannot put "violate a
HARD constraint" on the menu of design options. Given the verified fixture gap (no
committed fixture exercises the specialization-chain rewrite), stage (b)'s
gamma → lcoe success criterion is **not fixture-testable at all** without a new/augmented
fixture. So one of two things is true, and it's a spec-stage call, not a design punt:
- the stage-(b) fixture is a **requirement**, not an option (make it `[HARD]`), or
- R1 is **explicitly relaxed for stage (b)** with a user-approved exception recorded in
  the spec.

The spec recommends option (i), which is the right instinct — but leaving (ii) live
leaves the contract self-contradictory. **Which is it: fixture required, or R1 exception
approved?**

**L1-3 · Direct claim (census accuracy):** The numbering census (`:119-126`) omits the
**REQ-HR** family entirely, yet the spec leans on "REQ-HR-09" four times as the
self-named-rescue requirement handed from Item 9 (`:35`, `:114`, `:208`, `:225`).
Verified: REQ-HR-09 appears **only** in Item 9's handoff artifacts
(`.project/active/plant-prefill/`), never in committed docs — the highest doc-committed
is **REQ-HR-08** (`docs/architecture/reference/25-hierarchy-resolver.md:29`). So
REQ-HR-09 is a *reserved-but-uncommitted* label, not a landed requirement. Compounding
it, the spec assigns mechanism D two different REQ homes: "REQ-HR-09"
(Problem/constraints) vs. "likely extends **REQ-VBR-10+**" (census, `:125-126`). Pick one
home for mechanism D, and either add REQ-HR to the census (highest committed = 08, 09
reserved for this item) or drop the REQ-HR-09 references in favor of the REQ-VBR line.

### Lens 2 — Problem & Approach

**L2-1 · Question to the user:** The Problem section frames the failure as "the
**def/specialization idiom**: attributes declared on part defs, valued by `:>>`, with
parts nested and retyped" (`:22-24`). But the two committed, testable pins are *not*
that idiom — they're plain-usage EXPOSE-through-a-nested-part (L1-1). The genuine
def/specialization machinery is stage (b), which has no fixture. So the Problem's
framing points the reader at the part of the work that *isn't* fixture-backed, while the
only committed value (the pin flips) is a different mechanism. A reader could reasonably
conclude the headline (def/specialization → gamma → lcoe) is fixture-proven when it
isn't. Recommend the Problem separate "what the committed fixtures actually exercise
(plain-usage multi-hop EXPOSE)" from "the novel def/specialization machinery (stage b,
no fixture)."

**L2-2 · If-then tradeoff:** The split decision depends on L1-1. **If** stage (a) is
re-scoped to include multi-hop EXPOSE-through-a-nested-part (the actual pin blocker),
then it flips both pins and delivers reviewable value independently — the split is
clean and worth taking. **If** stage (a) stays as written (consumer-scoped alias lookup
+ PartDef EXPOSE guard only), it flips *nothing committed*, and the split gives design a
first stage with no executable win. The spec states what each stage is *supposed* to
deliver, but because stage (a)'s definition is incomplete, design cannot currently split
cleanly from the spec as written. Fix L1-1 and the split economics become statable.

### Lens 3 — Pipeline Risk

**L3-1 · Missing success criterion:** Mechanism D (self-named rescue) is picked up as an
`[INFERRED]` requirement (`:114-117`) — good, it did **not** fall through the crack. But
it has **no success criterion**, and the only committed fixture
(`self_named_binding_trap`) is a *negative*, extraction-only case that resolves to the
calc's own parameter (per `[[plant-idiom-fixtures]]`). There is no positive test that
the per-instance rewrite actually *rescues* a self-named binding to an upstream channel.
A `[HARD]`/`[INFERRED]` behavior with nothing that would catch it if the rewrite fails to
rescue. Add a positive rescue fixture/test to the success criteria, or explicitly
re-defer mechanism D with rationale (don't leave it inferred-but-uncovered).

**L3-2 · Rewrite request / placement:** SC-7 shape-A's test is left "here or in Item 11"
(`:169`, `:94`). But scope piece #3 (the PartDef-EXPOSE_PURE *resolution machinery*) is
scheduled to land in **this** item. Machinery and its test should not split across items —
landing the resolution path here while deferring its only test to Item 11 risks shipping
untested machinery. Tie the test's home to the machinery's home: if scope piece #3 lands
here, its shape-A test lands here.

**L3-3 · If-then tradeoff:** The instance-ambiguity success criterion (`:61-63`, shape 7
`chamber_a`/`chamber_b`) is qualified by the spec's own Open Question (`:164-168`): shape
7 today only proves two virtual `yield_calc` instances *exist*, not that a *consumer*
disambiguates between their outputs. So this SC, as a **channel** test, likely needs the
same fixture augmentation as stage (b). **If** the stage-(b) fixture is authored (L1-2),
fold the consumer-disambiguation edge into it; **if** not, this SC is stranded alongside
the gamma → lcoe SC. It should not be presented as independently satisfiable when it
shares stage (b)'s fixture dependency. Cluster the decision with L1-2.

### Lens 4 — Hygiene

**L4-1 · Rewrite request (minor):** The census (`:119-126`) is presented as the
authoritative "next free number" table but is incomplete (L1-3, REQ-HR missing).
Since the spec explicitly tells design/plan to "allocate from the census," an
incomplete census is a small correctness trap. Fold the fix into L1-3.

### Lens 5 — Reader Comprehension

**L5-1 · Rewrite request:** The spec runs three overlapping taxonomies at once —
mechanisms **(A)–(D)**, stages **(a)/(b)**, and fixture **shapes 2/3/4/5/7** — without a
single place that maps them to each other. A tired reader hitting "stage (a) flips both
V11 pins" (`:145`) cannot quickly tell which mechanism and which shape that is, or why
it's stage (a) and not (b). Given that the crux of the whole item is *which* shapes are
stage (a) vs (b) (and L1-1 shows the current mapping is itself wrong), this is
load-bearing, not cosmetic. Recommend one small table: shape → mechanism → stage →
committed-fixture? → what flips it. It would also have surfaced L1-1 during authoring.

---

## Engagement Summary

**Overall take:** The spec is pointed at the right item and its central discovery (stage
(b) has no committed fixture) is verified true — but it misattributes the mechanism that
flips its own two headline pins, and it offers a HARD-constraint violation as a design
option. Both are fixable with targeted edits; the work item is sound. Revise.

**Here's what I need you to weigh in on:**

1. **[L1-1]** The two V11 pins are blocked by a feature-chain-through-a-nested-part
   (classified FORMULA) plus `_resolve_expose_pure`'s 2-segment-only key — **not** by the
   PartDef-EXPOSE guard scope piece #3 names. As written, stage (a) may flip neither pin.
   Should the spec add "multi-hop EXPOSE-through-a-nested-part" as an explicit scope
   piece and re-derive success criterion #1 against it?
2. **[L1-2, L3-3]** Stage (b) has no fixture, so its gamma → lcoe (and the
   instance-ambiguity channel) criteria are un-testable under R1. R1 is HARD. Decide now,
   at spec: is the stage-(b) fixture a **requirement**, or is R1 **explicitly relaxed**
   for stage (b) with the exception recorded? It can't stay a design option.
3. **[L2-1, L2-2]** Given L1-1, the Problem's "def/specialization idiom" framing points
   at the un-fixtured stage (b), while the committed value is plain-usage multi-hop
   EXPOSE. Reframe so the split boundary is statable, then let design take (or decline)
   the split.
4. **[L3-1]** Mechanism D (self-named rescue) is picked up but has no success criterion
   and only a negative fixture. Add a positive rescue test, or explicitly re-defer.
5. **[L1-3]** Fix the census: REQ-HR family is missing (highest committed REQ-HR-08;
   REQ-HR-09 is reserved-not-committed), and mechanism D is given two REQ homes
   (REQ-HR-09 vs REQ-VBR-10+). Pick one.
6. **[L3-2]** Route SC-7 shape-A's test to wherever scope piece #3's machinery lands —
   don't split machinery from its test across items.

---

## Resolutions

*(Filled in during Stage 5 as the reviewer resolves each finding, keyed by ID.)*

---

**Verdict:** Revise
**Next Steps:** Record resolutions above (especially L1-1 and L1-2 — they change what
stage (a) is and whether the stage-(b) fixture is optional). Then re-run `/_my_spec`
(or return to the spec-agent session) and point it at this review to incorporate. The
reviewer does not edit the spec.
