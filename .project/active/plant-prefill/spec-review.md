# Spec Review: Plant-Idiom Literal Pre-Fill (SC-5 stage 1)

**Spec:** `.project/active/plant-prefill/spec.md`
**Contract:** `claude-pack/commands/_my_spec.md`
**Review File:** `.project/active/plant-prefill/spec-review.md`
**Date:** 2026-07-05

---

## Reality Check

**Concerns (proceed to full audit).** The spec is about the right work item, the
problem is real, and the direction is sound: the `base_cost` class is genuinely
Item 9's (literal, not channel), the fixtures and pins exist and say what the spec
says they say, and the four new REQ IDs are free at HEAD. But the spec's central
code-facing trace has a material gap. It routes the `alias_agg_probe` / `issue22`
flip through **scope 2** (the LVP entry-point backfill in `graph_builder.py`) and
names deep-path matching there as "the one real design risk." It never mentions
`_rewrite_virtual_bindings` (`pipeline_builder.py:190`) — the existing function that
rewrites virtual-instance CalcUsage bindings from `design_overrides`, *including
deep-path literals*, and mutates `BindingInfo` in place. That one omission bears on
three separate claims: which mechanism actually flips the fixtures, whether scope 2
is even the right layer, and whether the BindingInfo bug is "harmless today." The
work item survives; the mechanism story needs reconciling before design. Verdict:
**Revise**.

---

## Audit

### Lens 1 — Faithfulness

**L1-1 · Direct claim:** The "YES answer" trace omits the one function that most
directly does the work. The spec says the flip happens because scope 2 backfills the
`...cost_model.base_cost` entry point from the literal, and flags deep-path matching
inside `_find_literal_redefinition` (`graph_builder.py:1120`) as the sole design risk.
But `_rewrite_virtual_bindings` (`pipeline_builder.py:190`, called from
`_extract_hierarchy_and_rewrite_bindings:167`) already:
  - builds an override index from `hierarchy_data.design_overrides`, **handling
    deep-path overrides explicitly** (line 206: `override.is_deep_path and
    len(target_path) >= 2` → key `(owning_qn__intermediate, leaf)`), and
  - rewrites matching virtual-instance bindings to `BindingType.LITERAL` with the
    literal value, setting `source_path=None` (lines 248–252).

For `:>> widget.base_cost = 50.0` the override is deep-path
(`target_path=['widget','base_cost']`, `is_deep_path=True`, `literal_value=50.0`),
and the `base_cost` binding's `source_path` is
`AliasAggProbeLibrary::Widget::cost_model::base_cost` (verified in the snapshot),
so leaf extraction yields `base_cost` and the phase-2 key is `(parent_path,
'base_cost')`. That is exactly the shape the deep-path branch is built to match.
The plausible consequence: **relaxing the guard alone (scope 1) rewrites the binding
to a literal before `base_cost` ever becomes a valueless entry point — flipping V11
clean without scope 2 at all.** Either scope 2 is redundant for the `base_cost`
class, or there is a specific reason `_rewrite_virtual_bindings` does not fire here
(ordering, parent-path mismatch, the snapshot-rebuild path) that the spec must state.
As written, the spec's mechanism claim and its "one real design risk" are both
pointed at a function that may not be the one that fires. This is the finding to
resolve before design; see **L2-1**.

**L1-2 · Direct claim:** The BindingInfo "harmless today" justification is
contradicted by code. The spec says the shared-`BindingInfo` bug "is harmless today
(nothing rewrites per-instance)" (Problem, Hole 3). `_rewrite_virtual_bindings`
*does* rewrite per-instance today: it iterates virtual (non-template) CalcUsages and
**mutates `BindingInfo` objects in place** (its own docstring line 196; lines
249–254). `BindingInfo` is a plain mutable `@dataclass` (`usage_extractor.py:48`),
and `_create_virtual_calc_usage` shares those objects across siblings via
`bindings=list(template.bindings)` (`usage_extractor.py:393`). So the correct reason
the deep-copy fix is byte-exact is *not* "nothing rewrites" — it is "no committed
fixture currently has multiplicity->1 sibling instances whose override matches
diverge over a shared binding." That is a real, checkable claim the spec should make
(and the byte-exact suite is the right guard), but it is a different claim, and it
has teeth: once scope 1 lands and deep-path overrides feed the rewrite over
multiplicity parts like `widget [3]`, the shared-object bug becomes *active this
item*, not merely a latent Item 10 precondition. See **L2-3**.

**L1-3 · Question to the user:** Faithful to the epic, but the epic itself may be
wrong here. The epic's Item 9 scope 1 says the guard relaxation "also rescues
self-named bindings via the leaf-match rewrite." The research report is more careful:
mechanism D says self-named bindings "resolve to the calc's own parameter — **only
the rewrite path (C) can rescue them**" (`...deep-research.md:160`), and the rewrite
path is SC-5 stage 2 = Item 10. So the source the spec is built on already says the
self-named rescue depends on Item 10's machinery. The spec inherits the epic's scope-1
wording (REQ-HR-09) while its own Non-Goals assign the rewrite to Item 10. Is
REQ-HR-09 actually Item 9 work, or should it move wholesale to Item 10? See **L3-1**.

### Lens 2 — Problem & Approach

**L2-1 · Question to the user:** Given L1-1, does Item 9 need scope 2 at all for the
`base_cost` class? Two candidate mechanisms exist and the spec only considers one:
  - **(A)** relax the guard → `_rewrite_virtual_bindings` converts the `base_cost`
    binding to a literal (binding layer, extraction/orchestration phase); or
  - **(B)** the binding stays a reference → `base_cost` becomes a valueless entry
    point → scope 2 backfills its default (graph layer). This is the spec's plan.

These are *different layers*. `cost_model` is a plain CalcUsage, not an aggregation,
and scope 2 is described as "the classifier-path mirror of REQ-LVP-05, which fires
only inside `_build_aggregation_module`." If (A) fires, `base_cost` never reaches the
classifier and scope 2 is moot for this class. **Before design, someone should run
the guard relaxation in isolation and observe whether the two fixtures already flip.**
If they do, scope 2 collapses to "for entry points the rewrite doesn't cover" (if any)
and the spec's scope shrinks materially. If they don't, the spec should say *why* the
rewrite misses and keep scope 2 — but then REQ-LVP-10's deep-path matching must be
justified against the fact that `_rewrite_virtual_bindings` already has deep-path
matching that could be reused (R1: "extend, don't fork").

**L2-2 · Direct claim:** Scope 1 is not the inert "capture" the spec frames it as —
it activates binding rewrites. `_extract_single_redefinition`
(`hierarchy_resolver.py:99–141`) classifies *every* RHS into LITERAL / CHAIN /
EXPRESSION. Relaxing the guard feeds plain-usage overrides of *all three types* into
`design_overrides`, which `_rewrite_virtual_bindings` consumes — and it rewrites both
LITERAL **and CHAIN** bindings (lines 248–254). So a plain-usage CHAIN override (e.g.
`catf_mfe`'s cross-part references, or ife_plant shape 4's `cryo_load.magnet_volume`)
that is dropped today would, after relaxation, be captured and could rewrite a
binding's `source_path` — i.e. do a slice of Item 10's job early, or churn a baseline
the spec promises stays byte-identical. The spec must **require literal-RHS filtering
explicitly** (concern 3), either at capture (REQ-HR-08 filters to LITERAL) or with a
stated, tested guarantee that captured CHAIN/EXPRESSION overrides on plain usages
stay inert until Item 10. Right now REQ-HR-08 captures everything and only REQ-LVP-09
filters to LITERAL — and REQ-LVP-09 is on the *scope-2* path, which (per L2-1) may not
be the path that fires. There is also a latent crash: `_rewrite_virtual_bindings`
raises `ValueError` on a bare-name `source_path` (line 242), and today that line is
unreachable only because `override_index` is empty for these models (early return,
line 215). A self-named `in availability = availability` binding is exactly bare-name;
relaxing the guard could make the function reach that raise. This needs a test.

**L2-3 · Rewrite request:** Scope 3 (the deep-copy) is mis-framed as a pure Item 10
precondition. Per L1-2 and L2-2, once scope 1 feeds deep-path overrides into
`_rewrite_virtual_bindings` over multiplicity parts (`widget [3]`), the shared-object
bug is on the *active* path this item, not dormant. The spec should reframe scope 3 as
"required for correctness of multiplicity-part overrides *in this item*, and a
precondition for Item 10" — and its regression test should assert the divergent-sibling
case (two virtual instances, different override matches, independent results), not just
"two instances hold distinct objects." As written, the regression test the SC asks for
("mutating one never affects the other") proves the objects are distinct but does not
prove the *rewrite* respects the boundary, which is the property that matters.

### Lens 3 — Pipeline Risk

**L3-1 · If-then tradeoff:** REQ-HR-09 (self-named rescue) is a `[NEED]` with no
matching Success Criterion, and the spec both requires it and says it may not be
deliverable here. The Success Criteria list six outcomes; none of them is self-named
rescue. So an auditor cannot tell whether an un-rescued `in availability = availability`
at close is a met deferral or a missed requirement. **If** the rescue is genuinely
optional-this-item (research says it needs Item 10's rewrite), **then** REQ-HR-09
should be demoted to "extraction-side hook only, full rescue tracked to Item 10," with
its SC being "the hook lands and the trap fixture's before-state is preserved" — not
"self-named bindings are rescued." **If** the rescue must land here, it needs a real
SC and the Non-Goals contradiction (L1-3) has to be resolved the other way. The spec
cannot leave it as a `[NEED]` outcome that the same document says is probably Item 10.
The term "leaf-match rewrite" appears nowhere in the codebase — it is coined in the
epic and spec — so "rescue depth deferred to design" currently means "design invents
an undefined mechanism and decides how much of Item 10 to pull in." That is the
scope-creep seam concern 2 warns about, and the boundary statement is not yet crisp
enough to prevent it: the crisp version names *which specific code* the hook may touch
(extraction-side capture only) and states plainly that any `source_path` rewrite
through the specialization chain is Item 10.

**L3-2 · Question to the user:** Is the epic's "fresh IFE generation pre-fills"
criterion verified against the real fusion-tea IFE models or against the ife_plant
fixture as a proxy? The epic SC says "verified against the WI-015 anchor values"
(2/16 keys, `hif_driver_params.json = {}`) — those are the *real* models, which need a
live license. The spec's SC mixes registers: "the 16 def-declared literals reach
params" (the fixture) and "WI-015 evidence: previously 2/16 and 0 keys" (the real
models), without saying which is the gate. Item 3 handled the same tension explicitly
(demoted the live IFE re-run to opportunistic, D6). This spec should do likewise: name
the ife_plant fixture's input-JSON diff as the executable gate, and state the real-model
check as opportunistic/deferred with its blocker (license). As written the verification
vehicle for the epic's headline criterion is ambiguous.

**L3-3 · Rewrite request:** Enumerate the exact pin flips as a checklist, not prose.
The load-bearing assertions are three: `test_collector_pins_alias_agg_probe` and
`test_collector_pins_issue22_model` (both `[("base_cost","cost_model")]` → `[]`,
`test_uncovered_params.py:85,96`), and `test_alias_agg_probe_aborts_with_v11...`
(rewritten from raises-V11 to clean-package, `test_alias_agg_probe_generation.py:28`),
plus Item 8's `test_shape5_plain_usage_override_dropped`
(`test_ife_plant.py:161`, `[]` → asserts capture). The spec references these in prose
but never lists them as the definitive flip set. Design and audit both need the exact
list. (Confirmed free at HEAD: REQ-HR-08/09, REQ-LVP-09/10, REQ-VBR-08 are the next
unused IDs in each series.)

### Lens 4 — Hygiene

**L4-1 · Rewrite request:** Non-Goals says ife_plant shape 2 "stays captured-but-unwired
unless design finds a consumer (it should not)." That parenthetical asserts a negative
about the model the spec hasn't shown it verified. Either cite where shape 2's lack of
a consumer is established, or soften to "no consumer is known." Minor.

### Lens 5 — Reader Comprehension

**L5-1 · Rewrite request:** The spec-time-question section ("does scope 1+2 fix the
`base_cost` class? — YES") reads as settled, but per L1-1/L2-1 the mechanism under the
"YES" is the part in doubt. The headline answer (this *is* Item 9's class — literal,
not channel) is correct and should stay. What needs softening is the *mechanism*
confidence: the section presents scope 2 + deep-path matching in `_find_literal_redefinition`
as the plan of record and buries the one genuine uncertainty ("does the existing binding
rewrite already do this?") — which is never raised at all. A tired engineer reads "YES,
here's the mechanism, here's the one risk" and does not learn that the real open question
is *which of two mechanisms fires*. Restructure so the reader sees: class = literal
(settled) → mechanism = one of two paths (open, resolve before design) → deep-path
matching is the risk *on whichever path is chosen*.

---

## Engagement Summary

**Overall take:** Right problem, right class, real fixtures — but the spec's mechanism
trace skips `_rewrite_virtual_bindings`, the existing function that rewrites
virtual-instance bindings from design overrides including deep-path literals. That
single omission destabilizes three of the spec's claims: which mechanism flips the
fixtures (maybe scope 1 alone, not scope 2), why the BindingInfo fix is byte-exact
("nothing rewrites per-instance" is false), and whether scope 1 is inert capture (it
feeds an active rewrite that also handles CHAIN). Fixable, but not by wording — the
scope needs re-tracing against that function first.

**Here's what I need you to weigh in on:**

1. **[L1-1, L2-1]** Run the guard relaxation (scope 1) in isolation against
   `alias_agg_probe` / `issue22` and see whether they already flip clean via
   `_rewrite_virtual_bindings`. If they do, scope 2 (REQ-LVP-09/10) is redundant for
   the `base_cost` class and the spec shrinks. If they don't, the spec must say why the
   existing rewrite misses. This is the one thing to resolve before design.
2. **[L2-2]** Require literal-RHS filtering explicitly. Relaxing the guard captures
   CHAIN/EXPRESSION plain-usage overrides too, and `_rewrite_virtual_bindings` rewrites
   CHAIN bindings — a slice of Item 10's job, plus a `ValueError` crash risk on bare-name
   `source_path` (self-named bindings). Decide: filter to LITERAL at capture, or prove
   non-literal captures stay inert with a test.
3. **[L1-2, L2-3]** Fix the BindingInfo justification ("nothing rewrites per-instance"
   is contradicted by `pipeline_builder.py:196`) and strengthen scope 3's regression
   test to assert the divergent-sibling rewrite case, not just object distinctness.
4. **[L3-1, L1-3]** Decide REQ-HR-09's home. The research says self-named rescue needs
   Item 10's rewrite path; the spec both requires it (`[NEED]`) and says it's probably
   Item 10, with no SC to verify it. Demote to "extraction hook only, rescue → Item 10,"
   or move it wholesale — and define/scope "leaf-match rewrite," which exists nowhere in
   the code today.
5. **[L3-2]** State the verification vehicle for "fresh IFE generation pre-fills": the
   ife_plant fixture's input-JSON diff is the executable gate; the real fusion-tea
   models are the opportunistic/deferred check (license-blocked), à la Item 3's D6.

---

## Resolutions

Resolved 2026-07-05 via the orchestrator-run empirical probe (live license) + a static
check of the committed ife_plant baseline. Spec revised in place.

- **L1-1 / L2-1 (mechanism + does scope 2 survive):** Probe run. Relaxing the guard **alone**
  flips `alias_agg_probe` clean E2E — `system_design.json` mints
  `...assembly__widget__cost_model__base_cost: 50.0` via `_rewrite_virtual_bindings`' deep-path
  branch. The spec-time-question section is restructured to Part 1 (class = literal, settled) /
  Part 2 (mechanism = existing rewrite, scope 1 alone). The graph-layer backfill is not the
  path that fires.
- **L2-1 / Ruling 1 (scope 2):** **CUT.** The committed `baseline_outputs/ife_plant/computation_graph.json`
  already pre-fills all def-declared literals (bank_energy=1e7, efficiency=0.1, availability=0.7,
  discount_rate=0.08, … the ~14 Hawker params) as valued `usage_literal` EPs; only cross-part
  `magnet_volume` (Item 10) is null. No residual gap. New "Scope-2 finding" section documents
  this; REQ-LVP-09/10 removed; doc 18 no longer touched. Reinstatement clause kept for a
  specific still-valueless def-literal class if one surfaces (none known).
- **L2-2 / Ruling 2 (literal filter + bare-name crash):** REQ-HR-08 now mandates LITERAL-RHS
  filtering on the newly-scanned plain usages (CHAIN/EXPRESSION stay inert → Item 10). New
  REQ-VBR-09 replaces the `pipeline_builder.py:242` `ValueError` with a skip-with-DEBUG; SC and
  Non-Goals updated.
- **L1-2 / L2-3 / Ruling 3 (BindingInfo):** Problem "Hole 3" rewritten — the bug is an **active
  hazard this item** (rewrite mutates in place today; byte-exact only because no divergent
  siblings exist yet), not merely latent. Scope 3 reframed; SC now requires the divergent-sibling
  regression test (rewrite respects the boundary), not object distinctness.
- **L1-3 / L3-1 / Ruling 4 (REQ-HR-09 self-named rescue):** **CUT** from Item 9 → Item 10 handoff.
  Only crash-safety (REQ-VBR-09) stays. The coined phrase "leaf-match rewrite" is removed. Non-Goals
  and agentic-mbse impact updated.
- **L3-2 / Ruling 5 (verification vehicle):** SC now names the ife_plant fixture input-JSON /
  baseline diff as the executable gate; the real fusion-tea IFE run is opportunistic/deferred
  (license blocker), à la Item 3 D6.
- **L3-3 (pin-flip checklist):** SC "generate cleanly" bullet now enumerates the four load-bearing
  assertions as a checklist (two collector pins, the V11-abort rewrite, plus shape-5).
- **L4-1 (shape 2 parenthetical):** softened to "no consumer is known."
- **L5-1 (reader comprehension):** the spec-time-question restructured to settled-class →
  open-mechanism-now-resolved → the deep-path handling shown to already exist in the rewrite.

---

**Verdict:** Revise

**Next Steps:** Resolve L2-1 first — it's an empirical check (relax the guard, observe
the two fixtures), and its answer determines whether scope 2 survives and how much of
this spec needs rewriting. Once resolutions are recorded here, re-run `/_my_spec` (or
return to the spec-agent session) and point it at this review to incorporate. The
reviewer does not edit the spec.
