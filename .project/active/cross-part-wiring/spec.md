# Spec: Cross-Part Channel Wiring (SC-5 stage 2)

**Status:** Draft (revised after spec-review — `spec-review.md`, verdict Revise; L1-1/L1-2/L1-3/L2-1/L2-2/L3-1/L3-2/L3-3 resolved)
**Owner:** Reid W
**Created:** 2026-07-05
**Complexity:** HIGH
**Branch:** upstream-findings-epic
**Epic Item:** UPSTREAM-FINDINGS Item 10 (the riskiest item — design decides whether to split)

---

## Problem

A cross-part calc-output binding in the plant idiom never becomes a wired channel in
generated output. The consumer's input falls to a valueless Step-4 fallback entry point,
which the V11 collector flags. Two committed proof-of-gap pins sit here: catf_mfe's
`[cryo_load.magnet_volume]` and ife_plant's shape-4 `magnet_volume`.

The failure spans **two different mechanisms that must not be conflated** — the spec-review
found the first spec draft attributed the committed-pin flip to the wrong one:

1. **Multi-hop EXPOSE through a nested part (what actually blocks both committed pins).**
   Both pins are the same shape: a plain part *usage* whose attribute reaches a calc output
   *through a nested part* — `magnet_volume_total = tf_coil.volume_calc.volume`
   (`tests/fixtures/ife_plant/subsystems.sysml:12`), consumed cross-package by
   `cryo_load.magnet_volume = radial_build.magnet_volume_total` (`design.sysml:39`). Two code
   facts make this the blocker (verified):
   - The attribute is knocked **out of EXPOSE_PURE** because the classifier only accepts
     EXPOSE_PURE when there is no sibling ref (`computed_attribute_extractor.py:105-109`), and
     the nested-part ref `tf_coil` is a sibling → it is not resolved to a channel and drops.
   - Even if reclassified, `_resolve_expose_pure` builds only a **2-segment** `instance.output`
     key (`graph_builder.py:789`) — it has no notion of a middle part segment, so it cannot
     resolve a `part.calc.output` chain. This matches the recorded finding in
     `cross-part-binding-v11-fallthrough` (auto-memory).
   The PartDef-vs-PartUsage EXPOSE guard (REQ-CA-03) targets a *different* gap (the wi014_toy
   part-def shape-A, below) and does nothing for this plain-usage chain.

2. **The def/specialization channel idiom (the novel machinery — no committed fixture today).**
   Cross-part calc chains through *specialized nested parts* (`driver.cost_per_joule ←
   meier_cost.gamma`) — the genuine gamma → lcoe edge. Needs a per-instance binding rewrite
   through the specialization chain with redefinition precedence, plus a consumer-scoped alias
   lookup so the correct key can be constructed (CHAIN Step 2 is unscoped only). The **ife_plant
   fixture does not exercise this**: `lcoe_calc` binds all 14 inputs to plant-level literals, and
   the nested calc outputs (`driver_cost`, `chamber_yield`, `cooling_power`) are consumed by no
   cross-part calc (verified). So this mechanism has no committed fixture — a gap this spec closes
   by requiring one (Known Requirements), not by relaxing R1.

The research decomposed SC-5 into four mechanisms
(`.project/research/20260705_upstream-findings-deep-research.md:151-174`): **(A)** def-declared
`:>>` attributes (Item 9 landed the literal half; the channel half is mechanism 2 above),
**(B)** cross-part calc chains through specialized nested parts, **(C)** plain-usage `:>>`
overrides (Item 9 landed), **(D)** self-named bindings (`in x = x`) — the rewrite path is the
only rescue; handed here from Item 9. Item 9 landed the per-instance `BindingInfo` copy that
makes the rewrite safe; Item 4 landed retype-honoring indexing. This item is the remaining stage.

**Why now:** fusion-tea's MFE epic is entirely cross-part wiring and is gated on this. Their
current workaround is semantically wrong under sweeps — gamma depends on driver parameters, so
the two-pass harness feedback (run-A's computed gamma pasted as a constant into the pass-2 input
JSON) silently decouples them the moment a sweep varies those parameters
(`deep-research.md:153,164`). Landing this deletes the two-pass feedback and the
`hif_driver_instance` workaround upstream.

### Cross-map: mechanism × shape × stage × pin/criterion (the one place these line up)

The item runs three taxonomies — mechanisms (A–D), fixture shapes (2–7 + the multi-hop EXPOSE),
and stages (a/b). This table maps them so "stage (a) flips both pins" is checkable at a glance.

| Shape / fixture | Mechanism | What it is | Stage | Committed fixture? | Scope piece | Serves |
|---|---|---|---|---|---|---|
| ife_plant shape 4 **=** catf_mfe `magnet_volume` | B (multi-hop EXPOSE) | plain-usage attr `= part.calc.output`, consumed cross-part | **a** | **yes — both V11 pins** | **#2** (+ #1 to reach it) | **flips both V11 pins (SC-1)** |
| wi014_toy shape-A | — (SC-7 name-drop) | EXPOSE on a part **def**, name dropped | **a** | yes (wi014_toy) | **#4** (REQ-CA-03 revise) | SC-7 shape-A test (SC-6) |
| **new stage-(b) fixture** (nested calc output → cross-part consumer) | B / A channel half | a specialized nested part's calc **output** wired into a cross-part consumer calc — the gamma → lcoe analog | **b** | **REQUIRED — author (R1)** | **#3** | gamma → lcoe edge (SC-2) |
| stage-(b) fixture, sibling-consumer edge | — (instance ambiguity) | two same-type siblings; a consumer disambiguates their outputs | **b** | folded into the stage-(b) fixture | #3 | instance-ambiguity channel test (SC-3) |
| `self_named_binding_trap` + positive rescue | D (self-named) | `in x = x` rescued to the upstream channel | **b** | trap committed (negative); positive rescue added | #3 | mechanism-D rescue (SC-4) |
| ife_plant shape 2 | A (`:>>` literal on specialized def) | Item 9 captured the literal; unwired | — | yes (Item 9) | — | (Item 9) |
| ife_plant shape 3 | — (retype) | subtype template instantiation | — | yes | — | (Item 4, preserved) |
| ife_plant shape 5 | C (plain `:>>` override) | literal pre-fill | — | yes (Item 9) | — | (Item 9) |

**Split boundary, one sentence per stage:**
- **Stage (a)** makes cross-part references to *already-computed* values resolve to their
  canonical channel and be found from the consumer scope — the multi-hop EXPOSE chain (#2), the
  consumer-scoped alias lookup that reaches it (#1), and the part-def EXPOSE shape-A name (#4).
  It flips **both committed V11 pins** and lands the SC-7 shape-A test, all against committed
  fixtures.
- **Stage (b)** rewrites a specialized nested part's *own* calc bindings per-instance through the
  redefinition chain (usage override > specialized-def `:>>` > base def) so its calc **output**
  becomes a wired producer channel a cross-part consumer can bind (the gamma → lcoe edge), and
  rescues self-named bindings (#3). It requires the new stage-(b) fixture.

## Success Criteria

- [x] **SC-1 — the two committed V11 pins flip to real channel wiring, clean strict generation:**
  catf_mfe `[cryo_load.magnet_volume]` and ife_plant shape-4 `magnet_volume` resolve to a
  producer channel instead of a valueless fallback EP. Delivered by **scope #2 (multi-hop EXPOSE
  through a nested part) + scope #1 (consumer-scoped CHAIN alias lookup)** — *not* the part-def
  EXPOSE guard. Stage (a); committed-fixture backed.
- [~] **SC-2 — the gamma → lcoe edge is present in generated pipeline YAML** and the IFE anchors
  *(AUDIT: met at the GRAPH level only — the edge is present in the fusion-tea ComputationGraph from
  generated wiring alone; `driver_cost_constant` left the V11 offender list 11→10. The full YAML does NOT
  emit (aborts at V11 on 10 other cross-part bindings, out of scope), and run-C stays
  recorded-not-reproduced. Left partial `[~]` per the honest caveat; BACKLOG P1 follow-up filed.)*
  reproduce end-to-end from generated wiring alone, with no harness-fed values (WI-015 run C's
  lcoe — procedure below). Delivered by **scope #3 (per-instance specialization-chain rewrite)**.
  Stage (b); backed by the **required** stage-(b) fixture (Known Requirements), whose
  current-incomplete baseline is captured before the stage-(b) code lands so the wiring shows as a
  reviewed diff (Item 8 pattern).
- [x] **SC-3 — instance-ambiguity channel test:** two same-type sibling parts (`chamber_a`/
  `chamber_b`-shaped) where a *consumer* binding disambiguates to the correct sibling's
  instance-scoped channel — not a collision or a first-wins alias. Folded into the stage-(b)
  fixture (it shares that fixture's consumer-edge dependency).
- [x] **SC-4 — mechanism D self-named rescue, positive test:** a self-named binding (`in x = x`)
  that today resolves to the calc's own parameter is rewritten by scope #3 to its upstream
  channel. The `self_named_binding_trap` fixture (Item 8) is the substrate; the positive case is
  its rescue (or a self-named binding in the stage-(b) fixture). Stage (b).
- [x] **SC-5 — SC-7 shape-A name-drop test lands here** with scope #4 (the REQ-CA-03 /
  `is_part_def` revision it exercises): the wi014_toy part-def EXPOSE resolves through the revised
  path. The deferral chain (Item 1 → 8 → "10 or 11") ends here — machinery and its test land
  together. Stage (a).
- [~] **Existing 4 pipeline baselines unchanged**, or every diff reviewed and justified through
  the capture scripts (R3). The additive consumer-scoped alias step and the EXPOSE reclassification
  must not reorder or reclassify resolutions for models that already wire.
  *(AUDIT: catf regenerated + reviewed; the ife_plant graph baseline is STALE — still shows
  `magnet_volume` as `entry_point`/null while the recaptured snapshot wires it to `tf_coil`. No
  comparison test catches it. Left partial pending regen/removal — audit Finding 2.)*
- [x] **Every new/changed registry key is consumer-scope-prefixed and unique by construction**
  (R1 / doc 10) — no new ambiguous string keys, no reliance on the alias registry's first-wins
  collision fallback.
- [x] **Docs and matrix move with the code** (R1): REQ-BT-08 + docs 11/24 (new CHAIN step);
  REQ-CA-03 revised + doc 16 (part-def EXPOSE); the multi-hop EXPOSE requirement + doc 16/11; the
  rewrite requirement + doc 12; new REQ/V numbers from the census; verification-matrix rows.

## Known Requirements

### Scope pieces (each forced by the epic + the verified pin trace)

- **[HARD] #1 — consumer-scoped alias lookup in CHAIN dispatch.** A step in
  `dependency_backtracker._resolve_chain_dispatch`, additive and ordered *before* the existing
  unscoped `alias_lookup` (Step 2). Today CHAIN dispatch is: consumer-scoped `scoped_lookup` →
  direct `scoped_lookup` → unscoped `alias_lookup`. The cross-part alias is registered under a
  consumer-scoped key the unscoped step never constructs; this step constructs it. Update
  REQ-BT-08 and docs 11/24. **REQ-BT-11.**
- **[HARD] #2 — multi-hop EXPOSE through a nested part (the committed-pin blocker; new vs the
  first draft).** A plain-usage attribute `= part.calc.output` (a chain reaching a calc output
  through a nested part) must resolve to that calc's canonical channel and register as an alias.
  Two parts: (i) stop dropping it — the nested-part sibling ref must not knock it out of a
  resolvable classification (`computed_attribute_extractor.py:105-109`); (ii) build an
  **N-segment** alias key (`_resolve_expose_pure` currently builds 2-segment only,
  `graph_builder.py:789`). This is what flips both committed V11 pins. **REQ-CA-10.**
- **[HARD] #3 — per-instance binding rewrite through the specialization chain**, with redefinition
  precedence **usage override > specialized-def `:>>` > base def**. Builds on Item 4 (retype
  indexing → correct subtype) and Item 9 (per-instance `BindingInfo` copy so a rewrite on one
  virtual instance cannot corrupt its siblings — INV-2 of `plant-prefill/design.md`). This is the
  novel machinery and the single home of mechanism D (self-named rescue). **REQ-VBR-10.**
- **[HARD] #4 — PartDef-level EXPOSE_PURE with instance-scoped alias keys** — revises REQ-CA-03,
  which today produces a `ChannelAlias` only for PartUsage-level EXPOSE_PURE (`not is_part_def`
  guard, doc 16). PartDef-level EXPOSE (the wi014_toy shape-A) must produce aliases keyed by
  instance scope. Its SC-7 shape-A test lands here with it (SC-5). **REQ-CA-03 revised in place.**
- **[HARD] Every new registry key consumer-scope-prefixed and unique by construction** (R1, doc
  10). The alias registry's current policy is first-wins-with-warning
  (`output_registry.register_alias`) — the source of catf_mfe's repetitive alias-collision noise.
  New keys must not depend on that fallback; instance scope makes them unique.

### The stage-(b) fixture is required (R1 — not a design option)

- **[HARD] A committed fixture that wires a nested part's calc *output* into a cross-part consumer
  calc** — the gamma → lcoe analog — SHALL land with the stage-(b) code. R1 is non-negotiable on
  this epic; it exists *because* a fixture blind spot let SC-5 survive 1,500+ tests, and the
  riskiest item is the last place to relax it. Design picks **which** form, not **whether**:
  - extend ife_plant so `lcoe_calc` (or a new plant calc) consumes `driver`'s cost-calc output —
    accepting that this may churn ife_plant's committed shape-4/shape-7 pins, or
  - a companion fixture, if churning ife_plant's committed pins is worse.
  Its snapshot + **current-incomplete baseline are captured at implement before the stage-(b) code
  lands** (Item 8 pattern), so the wiring shows as a reviewed baseline diff. The instance-ambiguity
  consumer edge (SC-3) folds into this fixture.

### Constraints inherited from the epic and codebase

- **[HARD] No ComputationGraph schema field is added by this item.** The graph-level alias field
  (`output_aliases`) is Item 11's deliberate rev (R1 / REQ-PIPE-07). This item wires channels
  through resolution only.
- **[HARD] Real fixtures, no mocks** (R1). Constructed unit tests build real Pydantic/extraction
  objects (mocks masked SC-6 and SC-3).
- **[HARD] Baseline/snapshot regen goes through `scripts/capture_*.py` with reviewed diffs** (R3),
  never hand-edited. Live extraction needs the syside license (**expires 2026-08-06**) — schedule
  the stage-(b) fixture capture before that window or after renewal.
- **[NEED]** The additive consumer-scoped alias step and the EXPOSE reclassification leave models
  that already wire (catf_mfe's working paths, the 4 baselines) behaviorally unchanged — the new
  paths only *add* a resolution that previously fell through, never override an existing hit.
- **[INFERRED]** Mechanism D (self-named rescue) is executed by scope #3's per-instance rewrite —
  a self-named `in x = x` is rewritten to the upstream channel rather than binding to the calc's
  own parameter. Tagged inferred: the epic hands D here but does not spell out that the rewrite is
  its rescue. Now carries a positive success criterion (SC-4); if design finds the rescue needs
  machinery beyond this item, it may propose re-deferral **with evidence** — the default is
  delivery here.

### Numbering census (allocate deliberately at design/plan — R1)

- **V-rules:** highest committed **V11**. Next free: **V12+**.
- **REQ-BT:** highest **REQ-BT-10** → **REQ-BT-11** (scope #1).
- **REQ-CA:** highest **REQ-CA-09**; **REQ-CA-03 revised in place** (scope #4); **REQ-CA-10** for
  multi-hop EXPOSE (scope #2).
- **REQ-VBR:** highest **REQ-VBR-09** (Item 9's bare-name skip) → **REQ-VBR-10** (scope #3 — the
  specialization-chain rewrite; **the single REQ home of mechanism D**).
- **REQ-HR:** highest **committed** **REQ-HR-08** (`reference/25-hierarchy-resolver.md:29`). Item
  9's handoff *reserved* the label "REQ-HR-09" for the self-named rescue, but that label was never
  committed. Mechanism D is homed in **REQ-VBR-10** (the rewrite that implements the rescue), so
  the reserved REQ-HR-09 is released — mechanism D has exactly one home. Listed here so the census
  is complete for the family the item may touch.

## Non-Goals

- **Alias *emission* into generated output** — the graph-level `output_aliases` field and its YAML
  rendering are Item 11. This item makes the channel resolvable; Item 11 surfaces the modeler's
  name.
- **Supertype-chain template inheritance** for plain `part x : Subtype` usages (the MFE-epic note
  from Item 4).
- **EXPOSE_COMPUTED** (calc output + arithmetic) — stays rejected per modeling-assumptions §3.
- **Constraint execution** (SC-1 future epic).

## Open Questions / Deferred to design

- **The split decision (the epic's explicit design-phase call).** Two stages, now cleanly
  statable (Problem cross-map):
  - **Stage (a):** scope #1 (consumer-scoped CHAIN alias lookup) + scope #2 (multi-hop EXPOSE
    through a nested part) + scope #4 (part-def EXPOSE shape-A). **Flips both committed V11 pins
    and lands the SC-7 shape-A test**, all against committed fixtures — a real executable win.
  - **Stage (b):** scope #3 (per-instance specialization-chain rewrite + mechanism-D rescue) — the
    gamma → lcoe machinery, requiring the new stage-(b) fixture.
  If design splits, stage (a) ships first and still flips catf_mfe.
- **Which form the required stage-(b) fixture takes** — extend ife_plant (risk: churns its
  committed shape-4/shape-7 pins) vs a companion fixture. Design decides *which*; that it exists is
  a requirement, not a choice.
- **Exact interplay of #1 and #2 for the committed pins.** #2 registers the alias (the actual
  blocker); the consumer then reaches it via #1 or the existing unscoped `alias_lookup`. Design
  confirms whether the shape-4/catf key strictly needs the consumer-scoped segment or resolves
  through the existing step once #2 registers it.
- **Final REQ/V number allocation** from the census — deliberate assignment at design/plan.

## WI-015 Anchor Verification Procedure

The concrete numeric anchors (run A/B/C parameter sets and run C's lcoe value) live only in the
fusion-tea register (`~/1cfe/fusion-tea/.project/reports/2026-07-05-upstream-findings-register.md`),
outside this repo's sandbox. The procedure is structural; the implement session (which can read
fusion-tea and has a live license) pulls the numeric target from the register:

1. **Generate** the fusion-tea IFE model set through `sysml-codegen generate` (live or
   `--from-snapshot`) with no hand-built plumbing — no `sanitize_names.py`, no hand-filled input
   JSONs, no harness two-pass feedback.
2. **Assert the edge exists in the artifact:** the generated pipeline YAML contains the
   gamma → lcoe channel edge (gamma's calc output wired into lcoe's input). gamma's EQN/channel
   name **moves** under correct wiring — record the new name for the fusion-tea coordination note.
3. **Run the generated pipeline for run C** end-to-end from generated wiring and pre-filled inputs
   alone (Item 9 pre-fills the ~14 Hawker parameters; this item wires the cross-part edge).
4. **Compare** the pipeline's run-C lcoe against the register's WI-015 run-C anchor value; match
   within the register's stated tolerance = pass. This replaces the harness-fed result.
5. **Confirm the workarounds are deletable:** with the edge wired, `hif_driver_instance` and the
   two-pass gamma feedback are no longer referenced — record for the fusion-tea coordination note
   (deletion is upstream, not here).

The committed executable gate is the ife_plant + catf_mfe V11-pin flips (stage a, license-free
offline snapshots) **and the required stage-(b) fixture's V11-flip** (stage b, captured before the
code). The live WI-015 run is the end-to-end anchor on top of the committed gates.

## agentic-mbse Impact (R2 — recorded, executed in Item 12)

This item **defines the supported plant-idiom shapes** — its impact list is the substrate for
Item 12's MODELING_GUIDE and validation work:

- **MODELING_GUIDE / sysml-conventions:** teach the supported cross-part shapes this item wires —
  multi-hop EXPOSE through a nested part on a plain usage, cross-part calc chains through retyped
  nested parts, part-def-level EXPOSE reaching a calc output — with the redefinition precedence
  (usage override > specialized-def `:>>` > base def) stated as the rule modelers rely on.
- **Validation checks (Level 2 / Level 6):** the self-named-binding check (mechanism D) — since
  the rewrite now rescues a *resolvable* self-named binding but a self-named binding with no
  resolvable upstream is still a modeling error, this is a FAIL check with a negative fixture
  (`self_named_binding_trap`). Any new check gets a negative fixture (R2).
- **fusion-tea coordination note (success criterion, not afterthought):** channel names move
  (gamma's EQN — record the concrete before/after from the live run); the `hif_driver_instance`
  workaround and the two-pass gamma feedback become deletable upstream.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_upstream_findings.md` (Item 10 + R1/R2/R3; Item 11 downstream)
- **Spec review:** `.project/active/cross-part-wiring/spec-review.md` (this revision resolves it)
- **Required Reading:**
  - `.project/research/20260705_upstream-findings-deep-research.md` (SC-5 §, `:151-174`; SC-7 §)
  - `.project/active/type-indexing/design.md` (Item 4 — retype indexing, superset index)
  - `.project/active/plant-prefill/design.md` (Item 9 — literal pre-fill, `BindingInfo`
    per-instance copy precondition, D5 V11 re-anchor, self-named-rescue handoff)
  - `tests/conformance/test_ife_plant.py` + `tests/fixtures/ife_plant/` (shape 4 = cross-part
    chain pinned incomplete; shape 7 = sibling ambiguity)
  - `docs/architecture/modeling-assumptions.md` (supported subset, V-rules)
  - fusion-tea register (WI-015 anchors)
- **Auto-memory:** `cross-part-binding-v11-fallthrough` (how the multi-hop chain trips the V11
  collector — confirms the L1-1 pin trace); `plant-idiom-fixtures` (shape labels)
- **Code:** `analysis/dependency_backtracker.py` (`_resolve_chain_dispatch` — CHAIN dispatch, #1
  insertion point); `extraction/computed_attribute_extractor.py:105-109` (EXPOSE_PURE
  classification, #2); `resolution/graph_builder.py:789` (`_resolve_expose_pure` 2-segment key, #2;
  REQ-CA-03 `is_part_def` guard, #4); `core/output_registry.py` (`register_alias`/`alias_lookup`,
  doc 10); `extraction/usage_extractor.py` (virtual-instance machinery, #3)
- **Docs to update:** `reference/10-output-registry.md`, `11-analysis-backtracker.md`,
  `24-dual-resolution-architecture.md`, `25-hierarchy-resolver.md`, `16-computed-attributes.md`,
  `12-virtual-binding-rewrite.md`, `verification-matrix.md`, `modeling-assumptions.md`
- **Design:** `.project/active/cross-part-wiring/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_design` — where the split decision and the form
of the required stage-(b) fixture are settled.
