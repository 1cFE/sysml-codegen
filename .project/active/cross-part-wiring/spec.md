# Spec: Cross-Part Channel Wiring (SC-5 stage 2)

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-05
**Complexity:** HIGH
**Branch:** upstream-findings-epic
**Epic Item:** UPSTREAM-FINDINGS Item 10 (the riskiest item — design decides whether to split)

---

## Problem

A cross-part calc-output binding in the plant idiom never becomes a wired channel in
generated output. The consumer's input falls to a valueless Step-4 fallback entry point,
which the V11 collector then flags. Two committed proof-of-gap pins sit here today:
catf_mfe's `[cryo_load.magnet_volume]` and ife_plant's shape-4 `magnet_volume`.

The failure is specific. Cross-part references to *plain literal attributes on part usages*
and to *EXPOSE'd outputs of top-level parts* already work (catf_mfe's 42-module pipeline
wires because of them). What breaks is the **def/specialization idiom**: attributes declared
on part defs, valued by `:>>`, with parts nested and retyped. The research decomposed SC-5
into four mechanisms (`.project/research/20260705_upstream-findings-deep-research.md:151-174`):

- **(A)** def-declared attributes valued by `:>>` on a specialized PartDef — Item 9 landed the
  literal pre-fill half; the *channel* half (when the value is a calc output, not a literal)
  is still open here.
- **(B)** cross-part calc chains through specialized nested parts (`driver.cost_per_joule ←
  meier_cost.gamma`) — the genuine gamma → lcoe edge. Three stacked failures: retype not
  honored in the usage index (Item 4, landed), the one CHAIN alias keys to the workaround
  instance, and the backtracker has **no consumer-scoped alias lookup** (CHAIN Step 2 is
  unscoped only) so the correct key can never be constructed.
- **(C)** `:>>` overrides on plain part usages — Item 9 landed capture + pre-fill.
- **(D)** self-named bindings (`in availability = availability`) — the rewrite path is the
  only rescue; REQ-HR-09 was cut from Item 9 to here.

The precondition Item 9 landed — per-instance `BindingInfo` copy — makes the per-instance
rewrite safe. Item 4 landed retype-honoring indexing. This item is the remaining stage:
turn the cross-part binding into a real channel edge.

**Why now:** fusion-tea's MFE epic is entirely cross-part wiring and is gated on this. Their
current workarounds are semantically wrong under sweeps — gamma depends on driver parameters,
so the two-pass harness feedback (run-A's computed gamma pasted as a constant into the pass-2
input JSON) silently decouples them the moment a sweep varies those parameters
(`deep-research.md:153,164`). Landing this deletes the two-pass feedback and the
`hif_driver_instance` workaround upstream.

## Success Criteria

The epic's four criteria, annotated where the fixture substrate qualifies them (see the
fixture-coverage gap in Open Questions — this is the crux the design must resolve):

- [ ] **The two committed V11 pins flip to real channel wiring, clean strict generation:**
  catf_mfe `[cryo_load.magnet_volume]` and ife_plant shape-4 `magnet_volume` resolve to a
  producer channel instead of a valueless fallback EP. *Both are stage-(a) shapes
  (plain-usage cross-part EXPOSE) — achievable without the specialization-chain rewrite.*
- [ ] **The gamma → lcoe edge is present in generated pipeline YAML** and the IFE anchors
  reproduce end-to-end from generated wiring alone, with no harness-fed values (WI-015 run C's
  lcoe — verification procedure below). *This is the stage-(b) specialization-chain shape; no
  committed fixture exercises it today (Open Questions).*
- [ ] **Instance-ambiguity case covered by a test:** two same-type sibling parts (ife_plant
  shape 7, `chamber_a`/`chamber_b`) — a consumer binding disambiguates to the correct sibling's
  instance-scoped channel, not a collision or a first-wins alias.
- [ ] **Existing 4 pipeline baselines unchanged**, or every diff reviewed and justified through
  the capture scripts (R3). The additive consumer-scoped alias step must not reorder or reclassify
  resolutions for models that already wire.
- [ ] **Every new/changed registry key is consumer-scope-prefixed and unique by construction**
  (R1 / doc 10) — no new ambiguous string keys, no reliance on the alias registry's first-wins
  collision fallback.
- [ ] **Docs and matrix move with the code** (R1): REQ-BT-08 and docs 11/24 updated for the new
  CHAIN step; REQ-CA-03 revised for PartDef-level EXPOSE_PURE; new REQ/V numbers allocated from
  the census below; verification-matrix rows added.

## Known Requirements

### The four scope pieces (forced by the epic + landed substrate)

- **[HARD]** A **consumer-scoped alias lookup** step in the backtracker's CHAIN dispatch
  (`dependency_backtracker._resolve_chain_dispatch`), additive and ordered *before* the existing
  unscoped `alias_lookup` (Step 2). Today CHAIN dispatch is: consumer-scoped `scoped_lookup` →
  direct `scoped_lookup` → unscoped `alias_lookup`. The cross-part alias is registered under a
  consumer-scoped key the unscoped step can never construct; this step constructs it. Update
  REQ-BT-08 and docs 11/24.
- **[HARD]** A **per-instance binding rewrite through the specialization chain** with redefinition
  precedence: **usage override > specialized-def `:>>` > base def**. Builds on Item 4 (retype
  indexing gives the correct subtype) and Item 9 (per-instance `BindingInfo` copy so a rewrite on
  one virtual instance cannot corrupt its siblings — INV-2 of `plant-prefill/design.md`). This is
  the genuinely novel machinery.
- **[HARD]** **PartDef-level EXPOSE_PURE with instance-scoped alias keys** — revises REQ-CA-03,
  which today produces a `ChannelAlias` only for PartUsage-level EXPOSE_PURE (`not is_part_def`
  guard, `graph_builder.py`, doc 16). PartDef-level EXPOSE (the specialized-def shape) must now
  produce aliases keyed by instance scope, so each instantiation resolves to its own channel. Also
  fixes SC-7's shape-A resolution path (the reworded warning from Item 1 gets its real test here or
  in Item 11).
- **[HARD]** **Every new registry key consumer-scope-prefixed and unique by construction** (R1,
  doc 10). The alias registry's current collision policy is first-wins-with-warning
  (`output_registry.register_alias`) — the source of catf_mfe's repetitive alias-collision noise.
  New keys must not depend on that fallback; instance scope makes them unique.

### Constraints inherited from the epic and the codebase

- **[HARD]** **No ComputationGraph schema field is added by this item.** The graph-level alias
  field (`output_aliases`) is Item 11's deliberate rev (R1 / REQ-PIPE-07). This item wires
  channels through resolution only. Any field addition would be an out-of-discipline drive-by.
- **[HARD]** **Real Item-8 fixtures, no mocks** (R1). New behavior lands with a real fixture +
  snapshot. Constructed unit tests build real Pydantic/extraction objects, never mock nodes
  (mocks masked SC-6 and SC-3).
- **[HARD]** **Baseline/snapshot regen goes through `scripts/capture_*.py` with reviewed diffs**
  (R3), never hand-edited. Live extraction needs the syside license (**expires 2026-08-06**) —
  schedule capture work before that window or after renewal.
- **[NEED]** The additive consumer-scoped alias step and the EXPOSE_PURE revision leave models
  that already wire (catf_mfe's working paths, the 4 baselines) behaviorally unchanged — the new
  step only *adds* a resolution that previously fell through, it never overrides an existing hit.
- **[INFERRED]** The self-named-binding rescue (mechanism D, REQ-HR-09 handed off from Item 9) is
  resolved by the same per-instance rewrite path — a self-named `in x = x` that today binds to the
  calc's own parameter is rewritten to the upstream channel. Tagged inferred: the epic hands D to
  this item but does not spell out that the rewrite is its rescue; confirm at design.

### Numbering census (allocate deliberately at design/plan — R1)

- **V-rules:** highest committed is **V11**. Next free: **V12+**.
- **REQ-BT** (backtracker): highest is **REQ-BT-10**. Next free: **REQ-BT-11+** (the new CHAIN step).
- **REQ-CA** (computed attributes): highest is **REQ-CA-09**; **REQ-CA-03 is revised in place**, not
  re-numbered. A new PartDef-EXPOSE requirement, if separated, is **REQ-CA-10+**.
- **REQ-VBR** (virtual-binding rewrite): highest is **REQ-VBR-09** (Item 9's bare-name skip). The
  specialization-chain rewrite likely extends this family: **REQ-VBR-10+**.

## Non-Goals

- **Alias *emission* into generated output** — the graph-level `output_aliases` field and its YAML
  rendering are Item 11. This item makes the channel resolvable; Item 11 surfaces the modeler's
  name.
- **Supertype-chain template inheritance** for plain `part x : Subtype` usages (the MFE-epic note
  from Item 4). This item honors retype indexing that already landed; it does not add the
  supertype-chain walk.
- **EXPOSE_COMPUTED** (calc output + arithmetic) — stays rejected per modeling-assumptions §3.
- **Constraint execution** (SC-1 future epic).

## Open Questions / Deferred to design

- **The split decision (the epic's explicit design-phase call).** Two candidate stages, surfaced
  without pre-deciding:
  - **Stage (a) — smaller:** the consumer-scoped CHAIN alias lookup + PartDef-level EXPOSE_PURE
    shape-A. This alone **flips both committed V11 pins** (catf_mfe and ife_plant shape-4 are both
    plain-usage cross-part EXPOSE shapes) and delivers reviewable value independently.
  - **Stage (b) — novel:** the per-instance binding rewrite through the specialization chain with
    redefinition precedence. This is what produces the true **gamma → lcoe** edge and ends the
    two-pass feedback. It is the hard part and (see next question) the part without a committed
    fixture.
  - If design splits, stage (a) ships first and still flips catf_mfe; stage (b) follows.
- **The stage-(b) fixture-coverage gap (high-leverage — verify at design).** The ife_plant fixture
  as authored exercises stage (a) only. Its single cross-part *channel* is shape 4 (a plain-usage
  EXPOSE). `lcoe_calc` binds all 14 inputs to plant-level def-declared **literals**; the nested
  parts' calc outputs (`driver_cost`, `chamber_yield`, `cooling_power`) are **consumed by no
  cross-part calc**. So the specialization-chain per-instance rewrite (stage b) — and the true
  gamma → lcoe channel edge — has **no committed fixture**; it would be verified only against the
  live fusion-tea IFE model (license-gated), which strains R1 ("no new behavior without a real
  fixture"). Design must choose: (i) author a fixture shape that binds a plant-level calc input
  cross-part to a nested specialized part's calc output — likely an ife_plant augmentation, needing
  a live-license capture (R3) — or (ii) accept live-only verification for stage (b) and record the
  R1 exception. Recommendation: option (i); it is what makes the headline success criterion
  fixture-testable and gives stage (b) its own V11-flip proof. Deferred to design because it is a
  coverage/scope call tied to the split.
- **Instance-ambiguity as a *channel* case.** Shape 7 (`chamber_a`/`chamber_b`) today proves two
  virtual `yield_calc` instances exist; it does not prove a *consumer* disambiguates between their
  outputs. Making the success criterion "instance-ambiguity covered by a test" a channel test may
  need the same fixture augmentation as above (a consumer binding `chamber_a`'s output vs
  `chamber_b`'s). Design to decide whether the existing shape suffices or needs a consumer edge.
- **Where SC-7 shape-A gets its real test — here or Item 11.** The scope says "here or in Item 11."
  Design/Item-11 coordination to place it.
- **REQ/V number allocation** from the census above — deliberate assignment at design/plan.

## WI-015 Anchor Verification Procedure

The concrete numeric anchors (run A/B/C parameter sets and run C's lcoe value) live only in the
fusion-tea register (`~/1cfe/fusion-tea/.project/reports/2026-07-05-upstream-findings-register.md`),
which is outside this repo's sandbox. The procedure is defined structurally; the implement session
(which can read fusion-tea and has a live license) pulls the numeric target from the register:

1. **Generate** the fusion-tea IFE model set through `sysml-codegen generate` (live or
   `--from-snapshot`) with no hand-built plumbing — no `sanitize_names.py`, no hand-filled input
   JSONs, no harness two-pass feedback.
2. **Assert the edge exists in the artifact:** the generated pipeline YAML contains the
   gamma → lcoe channel edge (gamma's calc output wired into lcoe's input). gamma's EQN/channel
   name **moves** under correct wiring — record the new name for the fusion-tea coordination note.
3. **Run the generated pipeline for run C** end-to-end from the generated wiring and pre-filled
   inputs alone (Item 9 pre-fills the ~14 Hawker parameters; this item wires the cross-part edge).
4. **Compare** the pipeline's run-C lcoe against the register's WI-015 run-C anchor value. Match
   within the register's stated tolerance = pass. This replaces the harness-fed result the two-pass
   feedback currently supplies.
5. **Confirm the workarounds are deletable:** with the edge wired, `hif_driver_instance` and the
   two-pass gamma feedback are no longer referenced — record this for the fusion-tea coordination
   note (not deleted here; deletion is upstream).

The committed executable gate remains the ife_plant + catf_mfe V11-pin flips (license-free, offline
snapshots). The live WI-015 run is the end-to-end anchor; if a stage-(b) fixture is authored (Open
Questions), it carries its own committed V11-flip proof so stage (b) is not live-only.

## agentic-mbse Impact (R2 — recorded, executed in Item 12)

This item **defines the supported plant-idiom shapes** — its impact list is the substrate for
Item 12's MODELING_GUIDE and validation work. To record at design/close-out:

- **MODELING_GUIDE / sysml-conventions:** teach the supported cross-part shapes this item wires —
  def-declared `:>>` attributes on specialized PartDefs, cross-part calc chains through retyped
  nested parts, PartDef-level EXPOSE reaching a calc output — with the redefinition precedence
  (usage override > specialized-def `:>>` > base def) stated as the rule modelers rely on.
- **Validation checks (Level 2 / Level 6):** the self-named-binding check (mechanism D / REQ-HR-09)
  — a FAIL check with a negative fixture, since the rewrite now rescues it but a bare self-named
  binding without a resolvable upstream is still a modeling error. Any new check gets a negative
  fixture (R2).
- **fusion-tea coordination note (success criterion, not afterthought):** channel names move
  (gamma's EQN — record the concrete before/after from the live run); the `hif_driver_instance`
  workaround and the two-pass gamma feedback become deletable upstream.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_upstream_findings.md` (Item 10 + R1/R2/R3; Item 11 downstream)
- **Required Reading:**
  - `.project/research/20260705_upstream-findings-deep-research.md` (SC-5 §, `:151-174`; SC-7 §)
  - `.project/active/type-indexing/design.md` (Item 4 — retype indexing, superset index)
  - `.project/active/plant-prefill/design.md` (Item 9 — literal pre-fill, `BindingInfo` per-instance
    copy precondition, D5 V11 re-anchor, REQ-HR-09 handoff)
  - `tests/conformance/test_ife_plant.py` + `tests/fixtures/ife_plant/` (shape 4 = cross-part chain
    pinned incomplete; shape 7 = sibling ambiguity)
  - `docs/architecture/modeling-assumptions.md` (supported subset, V-rules)
  - fusion-tea register (WI-015 anchors) — `~/1cfe/fusion-tea/.project/reports/2026-07-05-upstream-findings-register.md`
- **Code:** `analysis/dependency_backtracker.py` (`_resolve_chain_dispatch` — CHAIN dispatch,
  consumer-scope insertion point); `core/output_registry.py` (`register_alias`/`alias_lookup` —
  alias machinery, doc 10); `extraction/usage_extractor.py` (virtual-instance machinery);
  `resolution/graph_builder.py` (`_resolve_expose_pure`, REQ-CA-03 guard)
- **Docs to update:** `reference/10-output-registry.md`, `11-analysis-backtracker.md`,
  `24-dual-resolution-architecture.md`, `25-hierarchy-resolver.md`, `16-computed-attributes.md`,
  `verification-matrix.md`, `modeling-assumptions.md`
- **Design:** `.project/active/cross-part-wiring/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_spec_review` (adversarial audit before design),
then `/_my_design` — where the split decision and the stage-(b) fixture-coverage gap are resolved.
