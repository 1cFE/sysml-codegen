# Spec Review: Whole-Plant Cross-Part Value Resolution (PIPELINE-TRUTH Item 2)

**Spec:** `.project/active/whole-plant-resolution/spec.md`
**Contract:** `claude-pack/commands/_my_spec.md`
**Review File:** `.project/active/whole-plant-resolution/spec-review.md`
**Date:** 2026-07-06

---

## Reality Check

**Concerns (Revise).** The work item is the right one and the spec is faithful to the
epic's headline: land the mechanism that carries subsystem attribute values across the
part boundary into the plant calc so fusion-tea's V11 abort clears. The three cross-part
mechanisms (a)/(b)/(c) are correctly captured from Item 1's `plant_values` fixture, the
mechanism decision is properly deferred to design, and the test discipline (independent
anchors, fires-on-shape V11 re-anchor, no byte-pin) is sound.

But the spec's "zero V11 offenders" success bar rests on the discovery register's clean
`(a) 5 + (b) 4 + (c) 1 = 10` decomposition, and the orchestrator's **live read of the
fusion-tea residual-gap table contradicts that decomposition on two of the ten
offenders**: offender #9 is an *in-part* self-reference (not one of the three cross-part
shapes the mechanism scopes), and offender #10 only exists because Item 3's workaround
instance is still present in the committed snapshot. As written, SC-1/SC-4/SC-A "zero
offenders" is unachievable by this item alone, and the spec never says what "zero" means
against the snapshot state that actually ships. That is a scope-and-success-criteria
defect, not a wrong-item defect — targeted edits fix it. Hence Revise, not Rework.

---

## Audit

### Lens 1 — Faithfulness

**L1-1 · Direct claim (the headline defect): offender #9 is IN-PART; the mechanism scope
is cross-part-only, so "zero offenders" is unachievable as written.**
The Problem section, the `[HARD]` mechanism requirement (spec lines 84–91), and SC-1 all
scope the fix to three **cross-part** shapes: subtype-def literal via retype (a), bare
`part :>>` override block (b), plain one-hop cross-part chain (c). All three are the
`plant_values` fixture's shapes. But the orchestrator's live read of the residual-gap
table (report.md:53–73) establishes that fusion-tea offender #9 —
`hif_plant__driver__meier_cost` input `driver_efficiency` ← its OWN part's `efficiency`
— is an **in-part self-reference through the calc-usage binding**: a binding to an
inherited attr the same def redefines below it (`hif_driver.sysml:74` vs `:81`). This is
*not* a cross-part reference. Item 1 already carries exactly this shape as substrate: the
`'Flow Sub'` part in `plant_value_shapes` (`library.sysml:81–86`), where
`calc flow_calc : FlowCalc { in flow_rate = throughput; }` binds an inherited attr that
`:>> throughput = 8.0` redefines below it — and the Item-1 pin records it **DEGRADED**,
with `_ep_default("flow_unit__flow_calc__flow_rate") is None`
(`test_plant_value_shapes.py:91–93`). A valueless EP of exactly the offender-#9 shape.
The spec is **silent** on this shape. If it stays silent, this item ships with fusion-tea
still aborting on #9, and SC-A/SC-4's "zero offenders" is false. This must be resolved one
of two ways: **(i)** require the mechanism to cover the in-part inherited-attr-redefine
shape (add it as a fourth `[HARD]` mechanism target, anchored on `'Flow Sub'`), or
**(ii)** explicitly scope it out with a recorded decision, restate SC-1/SC-4 against the
achievable offender count, and file #9 to whichever item owns it — but then SC-A cannot
claim "zero" on the committed snapshot and the epic's proxy definition needs the same
correction. Silence is the one unacceptable outcome.

**L1-2 · Direct claim: SC-4's "zero offenders on the committed snapshot" collides with
offender #10, which Item 3 (not Item 2) removes.**
SC-4 (spec 67–69) and the epic's SC-A proxy both assert the *committed* fusion-tea
snapshot generates with **zero** V11 offenders as Item 2's license-free gate. But the
orchestrator's read (point 3) is that offender #10 vanishes only when the workaround
instance (`hif_driver_instance`) is deleted — Item 3's job — and the committed snapshot
still contains that instance. So on the snapshot that ships today, #10 is present
regardless of what Item 2's mechanism does. "Zero offenders" is therefore not a
well-defined bar for this item until the spec pins: does SC-4 run against the current
committed snapshot (in which case the achievable target is #10-and-#9-excluded, i.e. not
zero), or against a re-captured snapshot (which is Item 3/Item 4 work)? Right now SC-4
promises a number this item cannot hit. State the exact offender arithmetic: N total, M
this item clears, which specific offenders remain and who owns them.

**L1-3 · If-then tradeoff: "REQ-VBR-10 precedence" is overloaded — the documented REQ is
scoped to calc-OUTPUT chains, not plain-literal values.**
SC-2 and the `[HARD]` at spec 92–95 treat "REQ-VBR-10 precedence (usage override >
specialized-def `:>>` > base def)" as an existing invariant the new mechanism must honor
"identically." But REQ-VBR-10 as documented
(`reference/12-virtual-binding-rewrite.md:32`, `verification-matrix.md:509`) is
specifically about a `:>> attr = calc.output` CHAIN rewrite through
`_rewrite_specialized_chain` — the calc-output shape Item 10 already wired — plus the
self-named rescue (mechanism D). Its cited tests (`test_spec_chain_channel.py`,
`test_self_named_rescue.py`) exercise the calc-output chain, **not** a three-tier
plain-literal precedence with distinct values at each tier. Mechanism (a) — carrying a
plain literal `:>> efficiency = 0.35` cross-part — is a *different* operation that
`_rewrite_specialized_chain` does not handle today (that's the gap this item fills). So
the plain-value three-tier precedence is **new behavior**, not an existing VBR-10
invariant being preserved. This matters: if it's an extension of VBR-10, the REQ text and
its matrix row must change; if it's a new REQ, say so. The spec's docs requirement (146)
hedges "any new REQ," but SC-2 and the `[HARD]` name VBR-10 as THE precedence contract.
Decide and state: does plain-value precedence extend REQ-VBR-10 or land as a new REQ?

**L1-4 · Direct claim: no current fixture exercises three precedence tiers with distinct
values — the usage-override tier is unexercised anywhere.**
The `[HARD]` precedence test (spec 108–110) requires "all three tiers (usage override,
specialized-def `:>>`, base def) with distinct values at each tier." `plant_values` has
only two populated tiers: base `efficiency` (valueless) and subtype `:>> efficiency =
0.35`; the plant usage retypes `part :>> driver : 'Hif Driver'` but never overrides
`efficiency` at the usage level. So the top tier — usage override beating specialized-def
`:>>` — is not present in any Item-1 fixture, and (per L1-3) is not proven by the
existing VBR-10 tests either. The spec correctly parks the fixture choice in "Smaller
design calls" (229–230), so this is not a hard defect — but the reviewer should know the
precedence invariant SC-2 leans on is currently *asserted, not substantiated at its top
tier*, and the "reuse or extend an Item-1 fixture" instruction will in practice force an
extension (a usage-level `:>> efficiency = <distinct literal>` on top of the subtype
literal). Confirm design is expected to author that tier, not just reuse.

### Lens 2 — Problem & Approach

**L2-1 · Question to the user: is the in-part shape (#9) genuinely a different mechanism,
or does the chosen resolver cover it for free?**
This is the substance behind L1-1. The in-part inherited-attr-redefine shape resolves a
value within one part's own specialization hierarchy (`:>> throughput = 8.0` reaching
`in flow_rate = throughput`), whereas (a)/(b)/(c) cross a part boundary. A value-fill
mechanism that walks the specialization chain to find the literal might cover both in one
operation; a channel-wiring mechanism keyed on cross-part source parts might not touch the
in-part case at all. So whether #9 is in-scope may itself depend on the mechanism design
decides. The spec should at least **name #9 as a decision input to design** (alongside the
value-fill-vs-wiring inputs it already lists), so design consciously decides whether its
mechanism subsumes the in-part shape or leaves it for another item. Right now design could
pick a mechanism, satisfy every stated `[HARD]`, and still ship #9 broken without ever
having been asked.

**L2-2 · Direct claim: the in-repo fan-out fixture only covers SAME-name consumers;
fusion-tea's fan-out renames per consumer.**
The spec's fan-out discussion (185–188, 202–204) and the extended `spec_chain_twolevel`
fixture both exercise one source feeding two consumers with the **same input name**:
`scale` → `scale_a`/`scale_b`, both binding `in s = scale`
(`spec_chain_twolevel/library.sysml`). But the orchestrator's read (point 2) is that
fusion-tea's real fan-out **renames per consumer**: `driver.efficiency` →
`lcoe_calc.driver_efficiency` AND `recirc_calc.eta` (different input names); likewise
`chamber.blanket_energy_multiple` feeds two differently-named consumers. Whether the
mechanism collapses to one channel (wiring) or mints N keys (value-fill), the
different-input-name case is the one that actually ships and it is **untested in-repo**.
Either the fan-out requirement / fixture must add a different-input-name consumer pair, or
the spec must record that different-name fan-out is validated only on fusion-tea (Item 3)
and say why in-repo same-name coverage is sufficient. As written, an engineer could make
`scale_a`/`scale_b` pass and still mis-handle the rename case.

**L2-3 · If-then tradeoff: the value-fill fan-out cost is stated two ways that appear to
conflict.**
Spec 186–188 says value-fill's cost is "fan-out stays N independent keys," then in the
same bullet says the twolevel fan-out "currently collapses to one shared entry point
(`test_fanout_collapses_to_one_producer_channel`); value-fill must preserve that collapse
or justify divergence." If the current behavior is a one-shared-EP collapse and value-fill
"stays N independent keys," value-fill would *change* current behavior — which is the
opposite of "preserve the collapse." This reads as an unresolved tension rather than a
stated cost. Clarify: is the existing `scale` fan-out collapse a producer-channel collapse
(calc-output) that value-fill leaves alone, or an entry-point collapse that value-fill
would break? The reviewer needs to know whether value-fill has a known regression against
an existing green test before design weighs the two mechanisms.

### Lens 3 — Pipeline Risk

**L3-1 · Question to the user: is "through the teax executor path" concrete enough to
build SC-3/SC-B against?**
SC-3 (63–66) and the `[HARD]` at 111–114 require the extended `spec_chain_twolevel`
package to compute its lcoe-analog "through the **generated package executed on the teax
executor path** (not just graph-level inspection)" within `rel 1e-6`. There is **no
existing executor-path test in the repo** (grep for a teax executor / run-pipeline harness
in `tests/` finds only baseline `registry_init.py` files, no runner). So SC-3 is asking
for test *infrastructure* that does not exist yet, not just a new assertion on existing
scaffolding. That may be fine — but the spec presents it as a straightforward pin. Confirm:
does design own standing up the executor harness (which runner — the generated
`registry_init` module registry driven by teax? a fixture-local driver?), and is that
lift inside this item's 8–11h estimate or does it push toward the split? If the harness is
non-trivial, this is a hidden cost the effort line doesn't show.

**L3-2 · Direct claim: SC-1's chamber_cost = 7.0 is a test-input choice, not a fixture
value — make sure the anchor's independence is stated precisely.**
SC-1 (51–57) anchors `plant_cost = (10 + 7) / 0.35 = 48.571`. The `10.0` (b) and `0.35`
(a) are literals in the fixture; `chamber_cost` (c) is genuinely valueless (no model
literal) and `7.0` is a value the **test's input JSON** supplies. The arithmetic is
correct and the anchor is honestly hand-derived. The one thing to state explicitly so the
next reader doesn't trip: `7.0` is not a fixture literal — it is the test-chosen user-fill
input that proves (c) resolves to a *real* user-fill key the JSON mints (the (c) success
condition is "the key exists and is fillable," distinct from (a)/(b)'s "the model literal
arrives"). The spec conflates the three into one `48.571` anchor; a one-line note that (c)
is validated by *presence-and-fill*, not by a carried literal, would keep the anchor's
provenance clean.

**L3-3 · If-then tradeoff: SC-5's V11 raise-proof re-anchor may land on `plant_value_shapes`
— which contains the in-part #9 shape.**
SC-5 (70–75) and the `[HARD]` at 115–117 require re-anchoring the V11 raise-proof to a
"still-uncovered fixture" after `plant_values` clears. The natural candidate is a shape in
`plant_value_shapes` — but that fixture contains `'Flow Sub'` (the in-part #9 shape,
valueless EP). If L1-1 resolves as "cover #9," then `'Flow Sub'` stops being a valid
raise-proof anchor (it would clear too), and the re-anchor must find a genuinely-deferred
shape. If L1-1 resolves as "defer #9," then `'Flow Sub'` is a fine anchor but the spec
should name it and confirm it stays uncovered by design. Either way, the V11 re-anchor
target is entangled with the L1-1 decision and can't be finalized until L1-1 is. Flag the
dependency so design doesn't pick an anchor that the same item's mechanism dissolves.

**L3-4 · Direct claim: the "supertype-chain template inheritance" non-goal may collide
with the in-part shape.**
Non-Goals (158–159) defers "supertype-chain template inheritance for *plain* usages" and
justifies it with "D6 confirmed the 10 offenders don't touch it." But offender #9 *is* an
inherited-attribute shape (the value lives on a supertype's redefinition). If a reader
maps "#9 is inherited-attr" onto "supertype-chain template inheritance," they'll conclude
#9 is out of scope by this non-goal — which may or may not be intended. The two concepts
are distinct (in-part inherited-attr-redefine ≠ cross-part supertype template expansion),
but the spec never draws the line, so the non-goal reads as silently disposing of #9. When
L1-1 is resolved, this non-goal needs a sentence distinguishing the two so the boundary is
explicit.

### Lens 4 — Hygiene

**L4-1 · Rewrite request: the Problem section's mechanism list and the Known-Requirements
`[HARD]` list restate the same (a)/(b)/(c) taxonomy three times** (Problem 37–42, SC-1
54–56, `[HARD]` 84–91). Not wrong, but a tired reader hits the same three-way split
repeatedly before learning what's *new*. Consider stating the taxonomy once and referring
back. Minor — only worth doing while other edits are in flight.

### Lens 5 — Reader Comprehension

**L5-1 · Rewrite request: the offender arithmetic is never stated as numbers, so the "zero
offenders" bar can't be checked on one read.** The spec says "10 references" and "three
mechanisms" and "zero offenders" but never lays out the N-total / M-cleared-by-this-item /
which-remain-and-who-owns-them table. Given L1-1 and L1-2 (two of the ten are not the
cross-part shapes this item covers), that table is now load-bearing. A short block —
"fusion-tea has N V11 offenders: X cross-part (this item), 1 in-part #9 (decision:
in/out), 1 instance-dependent #10 (Item 3); this item's zero-bar is defined as …" — is the
single highest-value comprehension fix. Right now the reader has to reconstruct it from the
register, the orchestrator's read, and three spec sections that don't cross-reference.

---

## Engagement Summary

**Overall take:** The item is right and the spec is faithful to the epic, but its
"zero V11 offenders" success bar is built on the register's tidy 10 = 5+4+1 cross-part
decomposition, and the live fusion-tea read breaks that on two offenders: #9 is in-part
(outside the three scoped mechanisms) and #10 depends on a workaround instance Item 3
deletes. Until the spec says exactly what "zero" means and whether #9 is in or out, SC-1 /
SC-4 / the epic's SC-A promise a number this item can't hit. Everything else is
tightening.

**Here's what I need you to weigh in on:**

1. **[L1-1, L2-1, L5-1]** Offender #9 is in-part, and Item 1's `'Flow Sub'` fixture
   already carries it as a valueless (DEGRADED) EP. Decide: does Item 2's mechanism cover
   the in-part inherited-attr-redefine shape (add it as a `[HARD]` target + design input),
   or is it explicitly scoped out with a recorded decision and SC-1/SC-4/SC-A restated
   against the achievable count? Silence is not an option.
2. **[L1-2]** SC-4 promises "zero offenders on the committed fusion-tea snapshot," but
   offender #10 is present until Item 3 deletes the workaround instance and re-captures.
   Pin the exact offender arithmetic and the snapshot state SC-4 runs against.
3. **[L2-2]** In-repo fan-out coverage is same-input-name only (`scale`→`s`/`s`);
   fusion-tea renames per consumer (`efficiency`→`driver_efficiency`/`eta`). Add a
   different-name fan-out to the requirement/fixture, or record that the rename case is
   validated only on fusion-tea (Item 3) and why that's sufficient.
4. **[L1-3, L1-4]** The "REQ-VBR-10 precedence" invariant SC-2 leans on is documented as a
   calc-OUTPUT-chain rewrite; plain-value three-tier precedence is new behavior with no
   fixture exercising the top (usage-override) tier. Decide: extend VBR-10 or land a new
   REQ, and confirm design authors the missing top-tier fixture.
5. **[L3-1]** SC-3/SC-B want execution "through the teax executor path," but no executor
   test harness exists in the repo today. Confirm design owns building it and that the lift
   fits the effort estimate (or feeds the split decision).
6. **[L2-3]** The value-fill fan-out cost is stated both as "stays N independent keys" and
   "must preserve the one-shared-EP collapse" — resolve which, and whether value-fill has a
   known regression against `test_fanout_collapses_to_one_producer_channel`.

---

## Must-Fix List (numbered, for the spec agent)

1. **Resolve offender #9 (in-part).** Either add a `[HARD]` mechanism target for the
   in-part inherited-attr-redefine shape (anchored on `plant_value_shapes` `'Flow Sub'`)
   and name it a design decision input, or record an explicit out-of-scope decision, file
   #9 to its owning item, and restate SC-1/SC-4 (and flag the epic's SC-A proxy) against
   the achievable offender count. [L1-1, L2-1]
2. **Pin the offender arithmetic for SC-4/SC-A.** State N total, M cleared by this item,
   which offenders remain (#9 per item 1, #10 via Item 3's instance deletion), and against
   which snapshot state "zero" is measured. Do not leave SC-4 promising an unreachable
   zero. [L1-2, L5-1]
3. **Cover different-input-name fan-out**, or record that the rename case is validated only
   on fusion-tea (Item 3) with a stated reason the same-name in-repo fixture suffices.
   [L2-2]
4. **Disambiguate the precedence REQ.** State whether plain-value three-tier precedence
   extends REQ-VBR-10 (with the REQ text + matrix-row edit) or lands as a new REQ; confirm
   design must author a fixture with distinct values at all three tiers including the
   currently-unexercised usage-override tier. [L1-3, L1-4]
5. **Make the executor-path gate concrete.** Name the runner SC-3/SC-B executes through,
   confirm design owns standing up the harness (none exists today), and confirm the lift
   fits the estimate or feeds the split. [L3-1]
6. **Resolve the value-fill fan-out contradiction** (N-keys vs preserve-collapse) and state
   whether value-fill regresses `test_fanout_collapses_to_one_producer_channel`. [L2-3]
7. **Tie the V11 raise-proof re-anchor to the #9 decision** — if #9 is covered, `'Flow Sub'`
   can't be the raise-proof anchor; name a genuinely-deferred shape. [L3-3]
8. **Distinguish the supertype-chain non-goal from the in-part shape** so the non-goal
   doesn't silently dispose of #9. [L3-4]
9. **State (c)'s anchor provenance precisely** — `7.0` is a test-chosen user-fill input,
   not a fixture literal; (c) is validated by key-presence-and-fill, not a carried value.
   [L3-2]

Non-blocking: L4-1 (taxonomy restated three times).

---

## Resolutions

*Filled in during Stage 5 as the user resolves findings, keyed by ID. The spec agent reads
this section to incorporate the review; the reviewer does not edit the spec.*

---

**Verdict:** Revise
**Next Steps:** Record resolutions above (especially the offender-#9 scope call and the
SC-4 offender arithmetic, which change success criteria), then re-run `/_my_spec` (or
return to the spec-agent session) pointed at this review to incorporate. The reviewer does
not edit the spec.
