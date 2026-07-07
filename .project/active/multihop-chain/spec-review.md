# Spec Review: Resolved Multi-Hop Chain Bindings

**Spec:** `.project/active/multihop-chain/spec.md`
**Contract:** `claude-pack/commands/_my_spec.md`
**Review File:** `.project/active/multihop-chain/spec-review.md`
**Date:** 2026-07-07

---

## Reality Check

**Concerns.** The spec is about the right work item, the Problem section is accurate, and the
core code claims (reject site `usage_extractor.py:717-739`, the count-only helper
`expression_utils.py:279`, the Pattern-A pins) all verified against the code. But the spec rests
one of its HARD requirements — and its whole byte-identity safety story — on a factual error: it
claims `deep_cross_scope_probe/design.sysml:70` is the **only** 3+-segment dot chain in the repo.
It is not. There are two more, and one of them (`derived_calc.base_metric = sensor.core.metric_value`,
`library.sysml:86`) is a second calc-usage chain **inside the same fixture** that hits the exact
reject the item removes. When the capability lands, it flips too — a second wire the spec's scope,
success criteria, channel-identity pin, and decomposition requirement all omit. This is fixable
with targeted edits (the work item is sound), so the verdict is **Revise**, but the miscount
touches enough of the contract that I would not let design start on the spec as written.

---

## Audit

### Lens 1 — Faithfulness

**L1-1 · Direct claim:** The HARD "only model with a 3+-segment dot chain" requirement is false.
Spec lines 94-97 state `deep_cross_scope_probe/design.sysml:70` is "the **only** model in the repo
with a 3+-segment dot chain (verified by corpus grep)." A grep of the fixture corpus
(`grep -rnE '=[^;]*\b\w+\.\w+\.\w+' tests/fixtures --include=*.sysml | grep -v '::'`) returns four
deep dot chains, not one:
- `design.sysml:70` — `station.array.derived_calc.derived_value` (Pattern A, `chain_analysis.data_point`) — the one the spec names.
- `library.sysml:86` — `sensor.core.metric_value` (`derived_calc.base_metric`) — a second **calc-usage input** chain, same fixture.
- `library.sysml:104` — `array.derived_calc.derived_value` (`station_output`, an **attribute** binding).
- `ife_plant/subsystems.sysml:12` — `tf_coil.volume_calc.volume` (`magnet_volume_total`, an **attribute** binding, a different fixture).

The claim as written is wrong. The spec needs to distinguish the two extraction paths (below) and
recount honestly.

**L1-2 · Direct claim:** There are two extraction paths for deep chains, and the spec conflates
them. `extract_feature_chain_segments` has two callers: `usage_extractor.py:723` (calc-usage param
bindings — the reject site this item removes) and `computed_attribute_extractor.py:220` (attribute
value bindings). The attribute path already extracts the **full** segment list into a
`reference_chain` and feeds a "multi-hop EXPOSE confirm walk" (`computed_attribute_extractor.py:217-220`).
So the two attribute chains (`station_output`, ife_plant's `magnet_volume_total`) go through
machinery that **already resolves deep chains** — confirmed: ife_plant's baseline has no
`magnet_volume_total` reject and wires `volume_calc__volume` normally. This is why ife_plant is in
fact safe — not because "there is only one chain," but because its chain doesn't touch the reject
path. The spec's byte-identity guarantee depends on this distinction, and the spec never draws it.
Two consequences the spec must absorb: (a) the true scope statement is "the only **calc-usage
input-parameter** 3+-segment chains are the two inside `deep_cross_scope_probe`"; (b) the attribute
path's existing confirm walk is the likely reuse target for "where the walk lives" (Open Question 1),
which the spec should point design at.

**L1-3 · Direct claim:** The spec omits the second in-fixture wire flip. `derived_calc.base_metric`
is currently an unbound entry point from a rejected 3-segment chain — snapshot
`extraction_snapshot.json:394-397` lists `base_metric` (twice) in `derived_calc.unbound_params`,
and the offender-set test's own docstring names it: *"the Pattern-A deep CHAIN
`chain_analysis.data_point` **and the mid-level `derived_calc.base_metric`** — are 3+-segment chains
the extractor can no longer truncate"* (`test_deep_cross_scope_probe.py:42-48`). When the walk lands,
`sensor.core.metric_value` resolves to the `core` module's `metric_value` output
(instance QN `...__station__array__sensor__core`, snapshot `:383`). So the re-capture carries **two**
intended wire flips, not one. Every place the spec says "the Pattern-A wire" as if it were the single
change — Success Criteria (lines 70-71, 78-79), the channel-identity HARD req (88-93), and the
decomposition HARD req (98-106) — is undercounted.

### Lens 2 — Problem & Approach

**L2-1 · If-then tradeoff:** The byte-identity bet is sound in substance but stated on a false
premise. The real reason no other model's output changes is that the reject path is only reachable
from calc-usage param bindings, and the only two such deep chains are both in `deep_cross_scope_probe`
(L1-2/L1-3). That holds **if** design builds the walk into the usage path only. **If** design instead
factors a shared segment-resolution walk that the attribute path also adopts (a plausible and even
attractive refactor, given the attribute path already has a confirm walk), then `station_output` and
ife_plant's `magnet_volume_total` could re-resolve and their baselines shift. The spec's re-confirm
instruction ("Re-confirm the grep at implement; if another model surfaces the shape, its baseline
change is in scope") is the right instinct — but the grep it prescribes will re-find ife_plant and
read as a violation, contradicting the "only model" prose. Fix: restate the guarantee as
path-scoped, and make the implement-time gate "no calc-usage-param baseline other than
deep_cross_scope_probe changes; if the walk is shared with the attribute path, ife_plant/station_output
baselines are in scope and reviewed."

**L2-2 · Question to the user:** Should the second in-fixture chain (`base_metric`) get its own
independently-anchored channel-identity pin? The spec's L1-style discipline — assert the exact wired
channel QN, computed independently of the code under test — is the item's headline safety property.
If `base_metric`'s flip lands unpinned, part of the re-capture diff has no test guarding it, which is
exactly the silent-mis-wire the item exists to prevent. My recommendation: yes, pin both wires
(`data_point → derived_calc__derived_value`, `base_metric → sensor__core__metric_value`) with
hardcoded expected QNs. Confirm you want both in scope.

### Lens 3 — Pipeline Risk

**L3-1 · Direct claim:** The fires-on-shape leg of the retained reject diagnostic has no corpus
substrate after the flip, and the spec asserts the pair holds anyway. The HARD/R1 requirement
(lines 107-110) says the retained reject warning must have a "fires-on-shape" test that "still names
an unresolvable deeper chain." But both calc-usage deep chains in the corpus resolve cleanly:
`station.array.derived_calc.derived_value` and `sensor.core.metric_value` both terminate at real
module outputs (L1-3). After the flip there is **no** fixture with a genuinely unresolvable
3+-segment chain, so nothing remains for the warning to fire on. The spec needs to require an
explicit unresolvable-chain substrate — a new minimal fixture with a dangling deep chain, or a
targeted unit test with a synthetic unresolvable chain — or the retained diagnostic ships with only
its silent-on-clean half tested, violating the R1 discipline the item is built around. This is the
sharpest gap in the spec.

**L3-2 · Direct claim:** The decomposition HARD requirement is actionable but undercounts the parts.
Lines 98-106 frame the re-capture diff as "the intended multi-hop change separated from the stale
[entry-point-classification] flip." With L1-3 folded in, the diff has **three** distinct parts:
(1) `data_point` EP→CHAIN wire, (2) `base_metric` EP→CHAIN wire, (3) the pre-existing stale
`entry_type` / `source_calc_usage` flip (memory `deep-cross-scope-stale-baseline`, verified: the
4-line flip reproduces on pre-F4 commit `ba3bca4`, non-aggregation). The requirement's mechanism —
separate intended from stale, root-cause the stale before commit — is correct and actionable; it
just needs to name all three so the reviewer can check each line of the diff against a known cause.

**L3-3 · If-then tradeoff:** The live/offline parity guard is well-formed but license-gated, and the
spec doesn't say so. The existing live test `test_pattern_a_deep_chain_warns_on_extraction`
(`test_deep_cross_scope_probe.py:83`) already drives `SysMLDataExtractor` live under
`@requires_license`, so a live-leg assertion or a live-vs-offline identity check is feasible on that
same path — the INFERRED requirement (lines 116-122) is buildable. But that leg is **skipped**
whenever the syside license is absent (headless/license-free CI). So the parity guard only actually
runs when the licensed suite runs; in license-free CI the committed-snapshot pin is the sole guard,
and the snapshot is precisely where an offline mis-wire would be baked in. The spec should state that
the guard is `@requires_license`-gated and therefore its protection is only as frequent as the
licensed suite — otherwise "guard the divergence with a live assertion" reads as an always-on
safeguard it isn't.

**L3-4 · Question to the user:** Is live/offline parity really `[INFERRED]`, or `[HARD]`? The spec
tags it INFERRED (line 116). But memory `multihop-expose-offline-parity` documents that this exact
failure — a multi-hop EXPOSE resolving live yet mis-wiring from a snapshot — **already happened**
(the Phase-5 miss). A requirement mitigating a failure mode that has already occurred on this shape
reads as forced, not inferred. The mechanism (which guard) can stay open; the obligation to have one
is HARD. Your call on the tag.

### Lens 4 — Hygiene

No material hygiene findings. The spec is well-structured and the tag discipline is otherwise honest.

### Lens 5 — Reader Comprehension

**L5-1 · Rewrite request:** The single most load-bearing fact — that there are two calc-usage deep
chains in the fixture and both flip — is absent, and its absence makes the Problem and Success
Criteria read as a cleaner one-wire change than it is. Once L1-3 is incorporated, the Problem section
should state up front: two calc-usage param bindings in this fixture hit the reject
(`data_point`, `base_metric`); both resolve when the walk lands; the re-capture carries both flips
plus the known stale classification flip. A tired reader should see the true shape of the diff before
reaching the decomposition requirement, not have to reconstruct it from the offender-set test.

---

## Engagement Summary

**Overall take:** Right work item, accurate reject-site analysis, honest R1–R4 discipline — but the
spec miscounts the deep chains it is about. It treats Pattern A as the lone 3+-segment chain and the
lone wire flip; in fact a second calc-usage chain in the same fixture (`base_metric`) flips too, two
attribute chains (one in another fixture) exist on a separate already-resolving path, and after the
flip no fixture is left for the retained reject warning to fire on. These are targeted fixes, not a
reframe — Revise.

**Here's what I need you to weigh in on:**

1. **[L1-1, L1-2, L1-3]** The "only 3+-segment dot chain" HARD requirement is false. Correct it to a
   path-scoped statement (calc-usage param bindings vs the attribute path), and add the second wire
   flip (`base_metric → sensor.core.metric_value`) to scope, success criteria, and decomposition.
2. **[L3-1]** After the flip, nothing in the corpus is an unresolvable deep chain, so the retained
   reject warning's fires-on-shape test has no substrate. Decide: new minimal dangling-chain fixture,
   or a targeted synthetic unit test. Without one, the diagnostic ships half-tested.
3. **[L2-2]** Pin both wires with independently-anchored QNs, or accept `base_metric` flipping
   unpinned? Recommendation: pin both.
4. **[L2-1, L3-2]** Restate byte-identity as path-scoped, and make the decomposition requirement name
   all three diff parts (two wires + the stale classification flip) so each diff line has a known cause.
5. **[L3-3, L3-4]** The live/offline parity guard is license-gated (skipped in license-free CI) — say
   so. And decide whether the parity obligation is HARD (the failure already happened once) rather
   than INFERRED.

---

## Resolutions

*Filled in during Stage 5, keyed by finding ID, once the human engages.*

---

**Verdict:** Revise
**Next Steps:** Record resolutions above, then re-run `/_my_spec` (or return to the spec-agent
session) and point it at this review to incorporate. The reviewer does not edit the spec.
