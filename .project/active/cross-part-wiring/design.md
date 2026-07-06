# Design: Cross-Part Channel Wiring (SC-5 stage 2)

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-05
**Complexity:** HIGH
**Branch:** upstream-findings-epic
**HEAD at design:** a3d3dbb
**Epic Item:** UPSTREAM-FINDINGS Item 10 (the riskiest item — design decides the split)

---

## Overview

Make cross-part calc-output bindings in the plant idiom resolve to real wired channels
instead of valueless fallback entry points. Delivered in two stages inside one item.

## THE SPLIT DECISION (first and loud)

**SPLIT. Two stages, both land within Item 10, stage (a) first. Stage (b) does NOT need
its own item.**

The two stages touch disjoint code, and stage (a) has zero dependency on stage (b):

- **Stage (a)** — three edits in *classification + registration + lookup*, all against
  **committed** fixtures, **no new fixture**. Flips **both** committed V11 pins (catf_mfe
  `[cryo_load.magnet_volume]`, ife_plant shape-4 `magnet_volume`) and lands the SC-7
  shape-A test (wi014_toy). This is a real executable win shippable on its own.
- **Stage (b)** — one edit in the *per-instance rewrite* (`orchestration/pipeline_builder.py`)
  plus a **required new companion fixture**. Delivers the gamma → lcoe edge (SC-2),
  instance-ambiguity disambiguation (SC-3), and mechanism-D positive rescue (SC-4).

**Blast radius, stage (a):** classifier knockout relax (`computed_attribute_extractor.py:104-109`);
N-segment key + part-def alias expansion (`graph_builder.py:789`, `output_registry_builder.py`
Phase 3, guard at `computed_attribute_extractor.py:245`); additive consumer-scoped alias step
(`dependency_backtracker.py:592-615`). All additive — the [NEED] no-override rule holds because
every new path only *adds* a resolution that previously fell through. Three committed baselines
flip (ife_plant, catf_mfe, wi014_toy); the other three stay byte-identical.

**Blast radius, stage (b):** one seam in `_rewrite_virtual_bindings`
(`pipeline_builder.py:262-264` CHAIN branch + `:242-251` bare-name branch), built directly on
landed Items 4 (superset index) and 9 (per-instance `BindingInfo` copy, INV-2). The risk is
concentrated in the **new fixture + baseline capture**, not in reaching across the codebase.

**Why not its own item:** stage (b) adds exactly one code seam and one fixture on top of
machinery that already landed. Splitting it into Item 10.5 would fragment the gamma → lcoe
deliverable from its enabling seam for no coverage gain. *Escalation guard:* if at plan time
the companion fixture + rewrite estimate exceeds a single implement pass, re-scope stage (b)
to its own item — but the evidence says both fit in Item 10.

## Related Artifacts

- **Spec:** `.project/active/cross-part-wiring/spec.md` (cross-map table, six scope pieces)
- **Spec review:** `.project/active/cross-part-wiring/spec-review.md` (L1-1 pin re-attribution)
- **Research:** `.project/research/20260705_upstream-findings-deep-research.md:151-174` (SC-5 four
  mechanisms A–D), `:190-201` (SC-7 shape A/B)
- **Required Reading:** `.project/active/type-indexing/design.md` (Item 4 superset index);
  `.project/active/plant-prefill/design.md` (Item 9, INV-2 per-instance copy);
  `tests/conformance/test_ife_plant.py` + `tests/fixtures/ife_plant/`;
  `docs/architecture/modeling-assumptions.md`
- **Auto-memory:** `cross-part-binding-v11-fallthrough`, `plant-idiom-fixtures`

## Research Findings

**The shape-4 pin trace (verified in fixture source).**
`radial_build.magnet_volume_total : Real = tf_coil.volume_calc.volume`
(`tests/fixtures/ife_plant/subsystems.sysml:12`) is a pure feature chain reaching a calc
output **through** the nested `tf_coil` part. Consumed cross-package by
`cryo_load.magnet_volume = radial_build.magnet_volume_total` (`design.sysml:39`). Two code
facts (both confirmed) drop it today:

1. **Classifier knockout.** `_classify_attribute_expression`
   (`computed_attribute_extractor.py:95-109`): `tf_coil` and `volume_calc` are QN-prefixed by
   `radial_build` → `sibling_refs`; `calc_refs` stays empty; Step 3 returns **FORMULA**
   (`:99-101`). FORMULA sends the attribute down the synthetic-module compile path and drops it
   from `design_attributes` with a warning — the consumer then falls through to the pinned EP.
2. **2-segment key.** Even reclassified, `_resolve_expose_pure` (`graph_builder.py:759-803`)
   builds only `instance.output` (`:789`) — it has no middle part segment, so it cannot resolve
   `part.calc.output`.

**Alias production and registration (the seams stage (a) edits).**
EXPOSE_PURE `ChannelAlias` objects are produced at `computed_attribute_extractor.py:244-273`,
gated by `not is_part_def` (`:245`). They register in `build_output_registry` **Phase 3**
(`output_registry_builder.py:169-193`) under scoped key `owning_part_short.alias_name`. CHAIN
redefinition aliases expand **per instance path** via `_build_chain_aliases`
(`pipeline_builder.py:338-391`, alias emit at `:382-389`) and register in **Phase 2**
(`output_registry_builder.py:147-163`). This per-instance-path expansion is the exact pattern
#4 reuses for part-def EXPOSE.

**The per-instance rewrite (the seam stage (b) edits).**
`_rewrite_virtual_bindings` (`pipeline_builder.py:190-266`). Item 9's literal branch
(`:256-261`) flips a binding to LITERAL and clears `source_path`; a CHAIN branch already exists
(`:262-264`) that only re-points `source_path` — **this is stage (b)'s insertion point**. The
bare-name branch (`:242-251`) explicitly defers self-named `in x = x` to "Item 10's rewrite" —
mechanism D's home. Safe because `_create_virtual_calc_usage` gives each virtual instance its
own shallow-copied bindings (`usage_extractor.py:399`, INV-2).

## Core Concept

A cross-part reference fails to wire for one of two reasons, and the two are cleanly separable.

**Reason one — the value already exists on a channel, but the reference can't reach its key.**
The upstream calc output *is* computed (the coil's `volume_calc.volume`), but the attribute
that exposes it (`magnet_volume_total`) is misclassified and its alias key is malformed, so the
consumer's lookup misses. The fix is **classification + key construction + one more lookup key
shape** — no binding is rewritten, no instance is re-computed. This is **stage (a)**: teach the
extractor that a pure feature-chain-to-a-calc-output is an EXPOSE (not a formula), teach
`_resolve_expose_pure` to build an N-segment key, expand part-def exposes per instance, and add
a consumer-scoped alias lookup so a consumer-local key can be found.

**Reason two — the producing calc's own bindings are wrong per instance, so the value on the
channel is wrong (or self-referential).** A specialized nested part's calc needs its inputs
resolved through the redefinition chain (usage override > specialized-def `:>>` > base def), and
a self-named `in x = x` needs redirecting to its upstream. This *does* rewrite bindings, per
instance, and is the novel machinery. This is **stage (b)**, built on Item 9's per-instance copy.

The key insight the spec-review surfaced: **the two committed pins are reason one, not reason
two.** Stage (a) alone flips them. Stage (b)'s value (gamma → lcoe) is reason two and has no
committed fixture — so stage (b) brings its own.

This composes with existing pieces, adding no parallel mechanism: classification stays in
`computed_attribute_extractor`, alias expansion reuses `_build_chain_aliases`'s per-instance-path
pattern, lookup stays in `_resolve_chain_dispatch`'s ordered ladder, and the rewrite stays in
`_rewrite_virtual_bindings` behind INV-2.

## Key Bets

- **B1.** Every committed V11 pin is reason-one (an *already-computed* value whose reference
  can't reach its key), never reason-two. *If false → stage (a) does not flip both pins, and the
  split's headline claim collapses; stage (b) would be on the critical path for the pins.*
  (Verified for both pins by source trace above; a probe at implement re-confirms against the
  live registry.)
- **B2.** A pure `FeatureChainExpression` whose waypoints are part/calc segments and whose
  terminal feature is a calc-usage output is *always* an EXPOSE, never a genuine formula. *If
  false → relaxing the sibling knockout reclassifies a real formula as an alias and mis-wires a
  model that works today.* (Discriminator is structural — pure chain, no arithmetic, terminal is
  a calc output — so a genuine formula, which carries arithmetic, cannot match.)
- **B3.** Item 9's per-instance `BindingInfo` copy (INV-2) makes a *channel* rewrite as safe as
  the literal rewrite it already hosts — sibling instances cannot be corrupted. *If false →
  stage (b)'s rewrite silently poisons same-type siblings (the exact bug INV-2 was built to
  prevent).*
- **B4.** The part-def EXPOSE alias can be expanded to instance-scoped keys with the *same*
  per-instance-path machinery `_build_chain_aliases` already uses for CHAIN redefs. *If false →
  #4 needs its own instantiation walk, enlarging stage (a).* (Both need "for each instance path
  of this part def, emit a scoped alias" — identical shape.)

## Key Decisions

- **D1. Split into stage (a)/(b), both in Item 10, stage (a) first.** *Rejected: single
  undivided pass (stage (a)'s committed win would be held hostage to stage (b)'s new-fixture
  risk); stage (b) as its own item (fragments gamma → lcoe from its one enabling seam for no
  coverage gain).*
- **D2. Fix #2 by extending classification, not by resolving FORMULA at the registry layer.**
  Relax the sibling knockout when the expression is a pure feature chain terminating at a calc
  output; classify it as EXPOSE so it takes the alias path. *Rejected: leave it FORMULA and
  special-case the chain in resolution — FORMULA already mints a synthetic module and tries to
  compile the chain (today's broken behavior); we would special-case two paths instead of one,
  and the alias path already exists.*
- **D3. The required stage-(b) fixture is a COMPANION, not an extension of ife_plant.**
  *Rejected: extend ife_plant.* Reasons: (i) ife_plant's shapes 2/3/5/7 pins were just set by
  Item 9 — adding a gamma → lcoe consumer edge churns them in the *same* baseline diff as stage
  (b), so the reviewed diff can't be attributed; (ii) stage (a) already flips ife_plant's shape-4
  pin — piling stage-(b) churn on top compounds two stages in one fixture; (iii) the Item 8
  pattern isolates novel mechanisms in dedicated fixtures (`self_named_binding_trap` isolates
  mechanism D) — a companion "specialization-chain channel" fixture matches it and keeps stage
  (b)'s baseline a clean standalone diff; (iv) the companion folds SC-3 (two same-type siblings +
  a disambiguating consumer) and SC-4 (positive self-named rescue) into one purpose-built model.
  *Cost accepted:* one more baseline to maintain, and ife_plant never shows the full end-to-end
  idiom — acceptable because the live WI-015 fusion-tea run is the real end-to-end anchor and
  ife_plant's job is the shape catalog, not the full pipeline.
- **D4. #1 (consumer-scoped alias lookup) lands in stage (a) per the spec, but its positive
  channel test rides stage (b)'s fixture.** *Rejected: move #1 to stage (b).* The source trace
  says the *pins* resolve through the existing unscoped Step 2 once #2 registers
  `radial_build.magnet_volume_total` (the consumer references that exact dotted path). #1 is
  functionally the mechanism-B (gamma → lcoe) precondition. It is a 4-line additive step with
  zero override risk, so landing it in stage (a) hardens the instance-scope discipline early; a
  probe at implement (Open Question 3) confirms whether the pins strictly need it. Its executable
  test is stage (b)'s fixture — acceptable because both stages are inside Item 10 (no
  cross-item machinery/test split).
- **D5. Mechanism D has exactly one home: REQ-VBR-10** (the rewrite that implements the rescue).
  *Rejected: REQ-HR-09* — reserved-but-never-committed in Item 9's handoff; released here.

## Architecture

Data flow, left to right, with the stage that touches each seam:

```
extraction            resolution/registration        backtracker lookup       orchestration
─────────             ───────────────────────        ─────────────────        ─────────────
classify attr   ─(a)→ produce ChannelAlias    ─(a)→  _resolve_chain_dispatch   _rewrite_virtual
 (#2 relax        │    (#4 drop is_part_def     │      (#1 consumer-scoped        _bindings
  knockout)       │     guard, expand           │       alias step)          ─(b)→ (#3 specialization
                  │     per-instance)           │                                   -chain + mech-D)
                  └→ _resolve_expose_pure  ─────┘
                     (#2 N-segment key)
```

- **#2 (stage a)** spans two seams: the classifier stops dropping the chain
  (`computed_attribute_extractor.py:104-109`), and `_resolve_expose_pure` builds an N-segment key
  (`graph_builder.py:789`) so the alias points at the right nested-calc output channel.
- **#4 (stage a)** drops the `not is_part_def` guard (`:245`) and expands the part-def expose
  alias per instance path (reusing `_build_chain_aliases`'s pattern) before Phase-3 registration,
  yielding instance-scoped keys like `demo_plant.total_cost`.
- **#1 (stage a)** inserts a consumer-scoped `alias_lookup` step in `_resolve_chain_dispatch`,
  ordered *before* the existing unscoped Step 2.
- **#3 (stage b)** extends the CHAIN branch of `_rewrite_virtual_bindings` (`:262-264`) to walk
  the specialization chain with redefinition precedence, and the bare-name branch (`:242-251`) to
  rescue self-named bindings — both per instance, behind INV-2.

## Required Invariants

- **INV-A (no-override).** Every new resolution path only *adds* a hit where the old code fell
  through; it never reorders or overrides an existing hit. #1 runs before the unscoped step but
  after both scoped steps, so a model that already wires via scoped/unscoped lookup is unchanged.
  (Serves the [NEED] constraint and "existing baselines unchanged".)
- **INV-B (unique keys).** Every new registry key is instance/consumer-scope-prefixed and unique
  by construction — no new key relies on the alias registry's first-wins collision fallback
  (`output_registry.register_alias:113-125`). Part-def expose keys carry the instance path;
  consumer-scoped keys carry the consumer scope.
- **INV-C (INV-2 preserved).** Stage (b)'s rewrite mutates only per-instance shallow-copied
  bindings; no template or sibling binding is touched (`usage_extractor.py:399`).
- **INV-D (classification stability).** Relaxing the sibling knockout reclassifies *only* pure
  feature-chains terminating at a calc output; any expression carrying arithmetic stays FORMULA.

## Component Overview

- **`_classify_attribute_expression`** (`computed_attribute_extractor.py:56-109`) — add the
  multi-hop-EXPOSE discriminator so `part.calc.output` chains classify as EXPOSE, not FORMULA.
  Stage (a), #2. REQ-CA-10.
- **`_resolve_expose_pure`** (`graph_builder.py:759-803`) — build an N-segment catalog key from
  the chain waypoints instead of `instance.output`. Stage (a), #2. REQ-CA-10.
- **Part-def expose alias expansion** — new helper in `pipeline_builder.py` mirroring
  `_build_chain_aliases`; drop the `not is_part_def` guard at `computed_attribute_extractor.py:245`
  and expand per instance path. Stage (a), #4. REQ-CA-03 revised in place.
- **`_resolve_chain_dispatch`** (`dependency_backtracker.py:592-615`) — insert consumer-scoped
  `alias_lookup` before Step 2. Stage (a), #1. REQ-BT-11; docs 11/24.
- **`_rewrite_virtual_bindings`** (`pipeline_builder.py:190-266`) — extend CHAIN + bare-name
  branches for specialization-chain channel rewrite and mechanism-D rescue. Stage (b), #3.
  REQ-VBR-10; doc 12.
- **Companion fixture** (`tests/fixtures/<name>/`) — specialization-chain channel + sibling
  disambiguation + positive self-named rescue. Stage (b), fixture requirement.

## Non-Goals

- **Alias emission into generated output** — the graph-level `output_aliases` field and its YAML
  render are Item 11. **No ComputationGraph field is added here.**
- **Supertype-chain template inheritance** for plain `part x : Subtype` (Item 4 MFE note).
- **EXPOSE_COMPUTED** (calc output + arithmetic) — stays rejected (modeling-assumptions §3).
- **Deleting fusion-tea workarounds** — the `hif_driver_instance` part and two-pass gamma
  feedback are deleted upstream; this item records the coordination note.

## Implementation Notes

- **#2 discriminator (the delicate one).** The classifier must know the chain's terminal is a
  calc output. Use the AST: a pure `FeatureChainExpression` (already tested at `:104-106`) whose
  intermediate segments resolve to part/calc usages and whose terminal feature is a calc-usage
  output. Do **not** relax the knockout for attribute-typed siblings — that would swallow real
  formulas (INV-D). Probe the live AST first to confirm the terminal is reachable.
- **#4 expansion timing.** The part def has no instances at extraction, so emit a *template*
  expose alias (mark `source="expose_pure"`, `is_on_part_definition=True`) and expand it per
  instance path in `pipeline_builder.py` alongside the CHAIN redefs, before the aliases reach
  `build_output_registry`. `find_instance_paths_for_partdef` is the same helper `_build_chain_aliases`
  uses.
- **#1 key shape.** `ScopedKey(f"{consumer_scope}.{source_path}")` against `alias_lookup`, where
  `consumer_scope = self._consumer_scope_dotted(usage)`; guard with `_is_self_reference`; order
  after Step 1b, before Step 2.
- **#3 precedence.** Resolve each binding's source through usage override > specialized-def `:>>`
  > base def, then rewrite `source_path` to the instance-scoped upstream channel. Reuse Item 9's
  override index (`pipeline_builder.py:202-216`) for the override tier. Self-named `in x = x`:
  rewrite to the upstream channel; if no resolvable upstream, leave as-is (still a modeling error
  — the negative `self_named_binding_trap` case).
- **Numbering (allocate at plan):** REQ-BT-11 (#1), REQ-CA-10 (#2), REQ-CA-03 revised (#4),
  REQ-VBR-10 (#3, sole mechanism-D home). REQ-HR-09 released. New V-rules from V12: e.g. V12
  multi-hop-EXPOSE coverage, V13 specialization-chain channel coverage.

## Potential Risks

- **#2 over-broadens classification** (INV-D). Mitigation: structural discriminator (pure chain +
  calc-output terminal); a probe on the live AST before coding; the three non-flipping baselines
  are the regression net.
- **#1 turns out load-bearing for the pins after all** (contradicts the source trace). Mitigation:
  probe the live registry key vs the consumer's constructed key (Open Question 3) *before*
  committing the stage-(a) pin flips; #1 is already in stage (a), so a positive finding needs no
  re-plumbing, only a note.
- **Companion-fixture capture blocked by license** (expires **2026-08-06**). Mitigation: author
  and capture the companion fixture's current-incomplete baseline *before* the window, or after
  renewal; stage (a)'s flips are license-free offline snapshots.
- **catf_mfe alias-collision noise doesn't clear** after unique keys. Mitigation: the collision
  count summary (`output_registry.alias_collision_count`) is the assertion target; a residual
  count is a reviewed diff, not a silent pass.

## Integration Strategy

Stage (a) ships first as a self-contained pass: three additive edits + REQ-CA-03 revision, three
baselines flip (ife_plant shape-4, catf_mfe pin, wi014_toy shape-A), other three unchanged, docs
16/11/24/10 move with the code. Stage (b) is a continuation pass in the same artifacts: one seam
edit + the companion fixture (captured current-incomplete, then flipped as a reviewed diff, Item
8 pattern), doc 12 + verification-matrix rows. Both complete before Item 11 (which adds
`output_aliases` and surfaces the names). agentic-mbse impact is recorded here, executed in Item
12: the MODELING_GUIDE content list (supported cross-part shapes + the precedence rule) and the
self-named-binding FAIL check with its `self_named_binding_trap` negative fixture.

## Validation Approach

- **Stage (a) executable gate (license-free):** ife_plant shape-4 pin flips (`EXPECTED_UNCOVERED`
  in `test_ife_plant.py` shrinks by `cryo_load.magnet_volume`); catf_mfe `[cryo_load.magnet_volume]`
  flips to a producer channel with clean strict generation; wi014_toy shape-A resolves and its
  REQ-CA-09 recorded-deferral pin flips to PASS (asserted alias `demo_plant.total_cost`). Red-first
  unit tests on real Pydantic/extraction objects (no mocks — mocks masked SC-6/SC-3).
- **Stage (b) executable gate:** companion fixture's current-incomplete baseline captured before
  the code; then gamma → lcoe channel edge asserted present in pipeline YAML (SC-2); sibling
  disambiguation asserted to the correct instance-scoped channel, not a collision (SC-3); positive
  self-named rescue asserted rewritten to upstream (SC-4).
- **WI-015 live anchor (on top of committed gates):** generate the fusion-tea IFE set with no
  hand-plumbing, assert the gamma → lcoe edge in the artifact, run run-C end-to-end, compare lcoe
  to the register's anchor within tolerance (spec procedure §WI-015). Record gamma's moved
  channel name for the fusion-tea coordination note.
- **Regression net:** the three non-flipping baselines (incl. solar_battery) stay byte-identical;
  `mypy src/` and `ruff check src/` clean.

## Next-Stage Handoff

- **Fixed:** the split (stage a first, both in Item 10); classification-layer fix for #2 (D2);
  companion fixture for stage (b) (D3); #1 in stage (a) (D4); mechanism D homed in REQ-VBR-10 (D5);
  no ComputationGraph field.
- **Open (resolve at implement, probe-first):** (1) exact registered key vs consumer-constructed
  key for the shape-4 pin — decides whether #1 is load-bearing for the pins (Open Question 3);
  (2) the live AST shape of `tf_coil.volume_calc.volume` — confirms the #2 discriminator is
  implementable; (3) `find_instance_paths_for_partdef` returns `demo_plant`'s path for #4
  expansion; (4) the companion fixture's specialization-chain resolution once authored. License is
  live now (expires 2026-08-06) — run the probes and the stage-(b) capture inside the window.
- **De-risk first:** probe (1) before committing the stage-(a) pin flips — it validates B1, the
  load-bearing bet of the whole split.

---
Next Step: After approval → `/_my_plan` (four-ish phases: stage-(a) red-first tests + three edits
+ baseline flips; then stage-(b) companion fixture + rewrite + capture).
