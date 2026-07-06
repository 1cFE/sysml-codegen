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

- **Stage (a)** — additive edits in *classification + a confirm pass + registration + lookup*, all
  against **committed** fixtures, **no new fixture**. Flips **both** committed V11 pins (catf_mfe
  `[cryo_load.magnet_volume]`, ife_plant shape-4 `magnet_volume`) and lands the SC-7 shape-A test
  (wi014_toy). This is a real executable win shippable on its own.
- **Stage (b)** — a **new precedence resolver** inside the per-instance rewrite
  (`orchestration/pipeline_builder.py`) plus **three required companion fixtures** (one per
  mechanism). Delivers the gamma → lcoe edge (SC-2), instance-ambiguity disambiguation (SC-3),
  and mechanism-D positive rescue (SC-4). It is *not* "one seam" — see the honest scope in
  Component Overview and M4-driven Implementation Notes.

**Blast radius, stage (a) (widened by round-2, still no new fixture, no cross-codebase reach):**
additive seams — (1) capture `reference_chain` at extraction + serialize/deserialize (D9,
`data_models.py`, `serializer.py`, `loader.py:474`); (2) leaf tags a tentative on `reference_chain`
instead of dropping to FORMULA (`computed_attribute_extractor.py:104-109`); (3) a **confirm pass
(Phase 3b)** walks `reference_chain` and finalizes EXPOSE-or-FORMULA (`build_output_registry`);
(4) part-def alias expansion into `_scoped_alias` (guard at `computed_attribute_extractor.py:245`);
(5) the structured `_scoped_alias` lookup step (`dependency_backtracker.py:592-615`); (6) `else:
raise` asserts at four classification readers (INV-F); (7) the INV-G ordering fix — a second
FORMULA-removal pass + moving `group_deriver` after confirm. The [NEED] no-override rule holds — an
unconfirmed tentative reverts to today's FORMULA *and its design-attr removal is re-run* (INV-G).
Committed baselines flip (ife_plant shape-4, catf_mfe's pin + its enumerated multi-hop re-tag set
per M1, wi014_toy shape-A); the ~15 non-multi-hop snapshots load unchanged (no version bump), the
three non-flipping pipeline baselines stay byte-identical. Bigger than "relax a knockout," but
bounded — no new fixture in stage (a), no reach outside these files.

**Blast radius, stage (b) (restated honestly, M4).** No new *extraction* — the specialized-def
`:>>` values are already in `hierarchy_data.redefinitions` (`hierarchy_resolver.py:144-164`,
collected `:538-540`, no type filter). But the rewrite is a small **precedence resolver**, not a
one-liner: (1) a **second index** over `redefinitions` keyed by specializing-def QN (Item 9's
reused index is `design_overrides`-only, `pipeline_builder.py:202-216`); (2) a **type-selection**
step that consumes `usage_type_map` (threaded but not yet read by the rewrite) to pick which
specializing def applies per virtual instance; (3) the **three-tier merge** (usage override >
specialized-def `:>>` > base def); (4) **two** extended branches — the CHAIN branch
(`:262-264`) and the bare-name / mechanism-D branch (`:242-251`). All behind INV-2, built on
landed Items 4 and 9.

**Why not its own item (with a recalibrated guard):** stage (b) adds one resolver in one function
plus three small fixtures on machinery that already landed — no cross-codebase reach, no new
extraction. Splitting it into Item 10.5 would fragment gamma → lcoe from its enabling resolver for
no coverage gain. *Escalation guard (recalibrated per M4):* **if, at implement, stage (b) exceeds
a single day, STOP and report for a split-out ruling** — do not push through. The estimate is now
against the true scope (index + type-select + merge + two branches + three fixtures), not "one
seam."

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

**The two committed pins are NOT the same chain shape (corrected per C1).** Both are cross-part
references that drop, but their chains terminate differently, and the mechanism must flip *both*:

- **ife_plant — direct-calc-output terminal.**
  `radial_build.magnet_volume_total : Real = tf_coil.volume_calc.volume`
  (`tests/fixtures/ife_plant/subsystems.sysml:12`) — a pure feature chain that names the calc
  output `volume` explicitly, reached **through** the nested `tf_coil` part.
- **catf_mfe — EXPOSE-alias terminal, one hop further.**
  `magnet_volume_total : Real = tf_coil.volume` (`radial_build.sysml:582`), where `tf_coil.volume`
  is *itself* an EXPOSE alias: `attribute volume : Real = volume_calc.volume` (`:458`). So the
  terminal is an **attribute that aliases** a calc output, not the calc output itself.

Both are consumed cross-package by a `cryo_load.magnet_volume` binding (`design.sysml:39` for
ife_plant). The unifying observation: **each chain resolves to a canonical channel by a transitive
walk over the registry** — ife_plant terminates directly at a calc-output channel, catf_mfe
terminates at an EXPOSE alias that the walk follows one more hop to the channel. A discriminator
that only accepts a direct calc-output terminal flips ife_plant and misses catf_mfe → SC-1 fails.

Two code facts (both confirmed) drop these today:

1. **Classifier knockout.** `_classify_attribute_expression`
   (`computed_attribute_extractor.py:95-109`): `tf_coil` and `volume_calc` are QN-prefixed by
   `radial_build` → `sibling_refs`; `calc_refs` stays empty; Step 3 returns **FORMULA**
   (`:99-101`). FORMULA sends the attribute down the synthetic-module compile path and drops it
   from `design_attributes` with a warning — the consumer then falls through to the pinned EP.
2. **2-segment key, no transitivity.** Even reclassified, `_resolve_expose_pure`
   (`graph_builder.py:759-803`) builds only `instance.output` (`:789`) — no middle part segment,
   so it cannot resolve `part.calc.output` (ife_plant) and cannot follow an alias terminal one hop
   to its channel (catf_mfe). Both need a transitive N-segment walk.

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
The upstream calc output *is* computed (the coil's `volume_calc.volume`), but the attribute that
exposes it (`magnet_volume_total`) is dropped as a FORMULA and its alias key is malformed, so the
consumer's lookup misses. No binding is rewritten, no instance re-computed — the fix is
**classification + key construction + one more lookup namespace**. This is **stage (a)**, and the
key move is *where* the classification decision happens: the leaf extractor cannot know whether a
chain terminal is a calc output (it has instance names, not calc-def output sets, and is barred
from resolving them). So the leaf makes a **tentative** call (a pure feature-chain with part-typed
waypoints *might* be a multi-hop EXPOSE) and a later pass, at the layer where the OutputRegistry
holds every channel and alias, **confirms** it by a **transitive walk** — resolving the chain hop
by hop to a canonical channel (following an alias terminal one more hop, so catf_mfe flips too).
A tentative that fails to resolve **reverts to FORMULA** — today's exact behavior, no silent
change. The walk reads the full chain segments captured as data (D9's `reference_chain`), since the
truncated `references` and the replay-nulled AST cannot feed it. Stage (a) also expands part-def
exposes per instance and adds a structured scoped-alias lookup in its own key namespace.

**Reason two — the producing calc's own bindings are wrong per instance, so the value on the
channel is wrong (or self-referential).** A specialized nested part's calc needs its inputs
resolved through the redefinition chain (usage override > specialized-def `:>>` > base def), and
a self-named `in x = x` needs redirecting to its upstream. This *does* rewrite bindings, per
instance, and is the novel machinery. This is **stage (b)**, built on Item 9's per-instance copy.

The key insight the spec-review surfaced: **the two committed pins are reason one, not reason
two.** Stage (a) alone flips them. Stage (b)'s value (gamma → lcoe) is reason two and has no
committed fixture — so stage (b) brings its own (three, one per mechanism).

This composes with existing pieces, adding no parallel mechanism: the leaf still classifies (now
tagging a tentative), the confirm pass reuses the recursive walk shape of
`_resolve_aggregation_input_channel` (cycle guard included), part-def expansion reuses
`_build_chain_aliases`'s per-instance-path pattern, the
lookup stays in `_resolve_chain_dispatch`'s ordered ladder (with its own key namespace), and the
rewrite stays in `_rewrite_virtual_bindings` behind INV-2.

## Key Bets

- **B1.** Every committed V11 pin is reason-one (an *already-computed* value whose reference
  can't reach its key), never reason-two. *If false → stage (a) does not flip both pins, and the
  split's headline claim collapses; stage (b) would be on the critical path for the pins.*
  (Verified for both pins by source trace above; a probe at implement re-confirms against the
  live registry.)
- **B2.** A tentatively-classified chain that **resolves to a canonical channel** by the transitive
  walk is a genuine EXPOSE; one that does not resolve is a FORMULA. *If false → the confirm step
  admits a chain that resolves to an unrelated channel (a false-positive resolution) and mis-wires
  a model that works today.* This is weaker than the original "structural discriminator" claim (the
  code's only arithmetic test is the *root-node* `FeatureChainExpression` check at
  `computed_attribute_extractor.py:104-106`, not a tree scan). The safety now rests on
  **confirm-or-revert** (a wrong tentative reverts to FORMULA, no mis-wire) plus the structured
  resolution key (INV-B), not on the leaf being decisive.
- **B5 (was hidden — surfaced per Bets review).** The multi-hop discriminator is **not** decidable
  at the `_classify_attribute_expression` leaf — the leaf has instance names, not calc-def output
  sets, and its docstring bars it from resolving them (`:7-8`). *If false (i.e. if it WERE
  cheaply decidable at the leaf) → the tentative/confirm split would be unnecessary overhead.* It
  is not: verified, the terminal-is-an-output test needs a resolved calc def, and catf_mfe's
  alias-terminal needs the whole registry. This is why D6 moves the decision downstream.
- **B6 (was hidden — surfaced).** The two committed pins are **different** chain shapes
  (direct-calc-output vs alias-terminal), so a single-terminal discriminator flips only one. *If
  false → the mechanism as first written would have sufficed.* Verified false in source (C1);
  the transitive walk is the response.
- **B7 (new, load-bearing per C4).** Live extraction *can* produce the full chain segments as data.
  *If false → the confirm walk has no input on any path (the AST is None on replay, `references` is
  truncated to `[tf_coil]`), and stage (a) flips neither pin.* Verified producible:
  `extract_feature_chain_name` (`expression_utils.py:250-280`) already walks the whole chain via
  `.operands[0]` + `.target_feature.name` — D9 returns the segment list instead of the joined
  string. **The one residual unknown** is *why* `extract_feature_refs` truncates (agentic-mbse
  internal, unread) — the first probe (Handoff), but it does not gate B7 because D9 uses the
  in-repo chain walker, not `extract_feature_refs`.
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
- **D2. Fix #2 in the classification/alias path, not the FORMULA synthetic-module path.**
  A multi-hop chain must end up as an alias, not a synthetic module. *Rejected: leave it FORMULA
  and special-case the chain in resolution — FORMULA already mints a synthetic module and tries to
  compile the chain (today's broken behavior); we would special-case two paths instead of one.*
  *How* the classification is decided is D6.
- **D6. Decide the multi-hop classification by TENTATIVE-at-leaf + CONFIRM-at-registry (C2
  mechanism ii), not by plumbing calc-def output sets into the leaf (mechanism i).** The leaf tags
  a structural candidate `EXPOSE_CHAIN_TENTATIVE` when the captured chain (D9's `reference_chain`)
  has **≥ 2 segments** rooted at a part-typed waypoint (INV-E) — *not* "one non-instance ref after
  removing waypoints," which the round-2 trace showed yields **zero** refs for the real pin
  (`references` is truncated to `[tf_coil]`, C4). A confirm pass inside `build_output_registry`
  runs the transitive walk **over `reference_chain`** (D9), after Phase-3 single-hop aliases and
  before Phase-4 (INV-G order); on resolution it finalizes to the EXPOSE alias variant, else
  **reverts to FORMULA** (today's behavior — INV-D). *Rejected: mechanism (i), plumb calc-def
  output sets into `_classify_attribute_expression`* — the leaf is barred from resolution imports
  (`:7-8`), and catf_mfe's alias-terminal is undecidable even with calc-def outputs (needs the whole
  registry, B5). *Tentative-state representation (C2):* a distinct enum value **no downstream
  consumer reads** — the confirm pass rewrites `ca.classification` **in place** (M6) before Step
  6/7, and every classification reader raises on a survivor (INV-F, made real per C6a).
- **D9. Extraction captures the full chain as data (`reference_chain: list[str]`) — the C4 fix,
  R1-consistent.** Today `extract_feature_refs` truncates `tf_coil.volume_calc.volume` to its root
  waypoint `[tf_coil]`, and the snapshot nullifies `expression_ast` (serializer `_AST_FIELDS`;
  loader.py:474) — so **neither `references` nor the AST can feed the walk on the offline path**.
  Fix: add an additive-optional `reference_chain: list[str] | None = None` to `ComputedAttributeData`
  (`data_models.py:214-217` default block; it is a dataclass, so a trailing defaulted field is
  safe), populated at live extraction by the **segment-list analog** of `extract_feature_chain_name`
  (`expression_utils.py:250-280` already walks the full chain via `.operands[0]` + `.target_feature.name`,
  but joins to a string — verified producible, Q2). Serialization auto-includes it
  (`serializer.py:171` loops `dataclasses.fields`); the loader adds `reference_chain=d.get("reference_chain")`
  (`loader.py:467-485`). **No `SNAPSHOT_FORMAT_VERSION` bump** — old snapshots: field absent →
  `None` → walk unavailable → classification stays FORMULA (today's behavior; the SC-10 additive-
  degrade precedent). Only fixtures needing multi-hop EXPOSE are recaptured (M6). *Rejected: read
  the AST at confirm time* — gone on replay (Q5); *re-parse `expression_text`* — also truncated to
  `"tf_coil"`.
- **D7. The #1 lookup uses a STRUCTURED tuple key in its own registry namespace, with BOTH sides
  written (C3 + C5).** A `ScopedAliasKey = NewType(tuple[str, str])` = `(scope, leaf)` in a dedicated
  `_scoped_alias` dict on `OutputRegistry`, distinct from the flat `_alias` — the tuple is stored
  **unjoined**, so `("a.b","c")` and `("a","b.c")` never collapse (leaf is always a single segment,
  so `("a","b.c")` cannot even arise). *Registration side (what writes it, when):* #4's per-instance
  part-def-expose expansion writes `(instance_path, exposed_leaf)` during the Phase-3 alias walk —
  wi014_toy → `("demo_plant", "total_cost")` → the `demo_plant__…__cost_calc__cost` channel. Stage
  (b)'s #3 also writes here, prefixing the consumer instance scope. *Lookup side (what #1 builds):*
  from a consumer binding's `source_path`, split at the **last** dot → `(prefix, leaf)` and look up
  `_scoped_alias`; `demo_plant.total_cost` → `("demo_plant","total_cost")` → hit. **They meet by
  construction:** both derive `(path-prefix, single-leaf)` from the *same* model dotted reference,
  split identically. `_is_self_reference` reused unchanged (channel-based; round-2 confirmed no
  re-derive needed). *Rejected: reserved-separator string key* — still one flat dict, still stringly
  typed. This makes #1 **load-bearing in stage (a)** — for #4's part-def exposes (SC-5 shape-A),
  *not* the two V11 pins (which resolve via #2 + the unscoped Step 2), resolving Open Question 1.
- **D3. The required stage-(b) fixture is a COMPANION, not an extension of ife_plant.**
  *Rejected: extend ife_plant.* Reasons: (i) ife_plant's shapes 2/3/5/7 pins were just set by
  Item 9 — adding a gamma → lcoe consumer edge churns them in the *same* baseline diff as stage
  (b), so the reviewed diff can't be attributed; (ii) stage (a) already flips ife_plant's shape-4
  pin — piling stage-(b) churn on top compounds two stages in one fixture; (iii) the Item 8
  pattern isolates novel mechanisms in dedicated fixtures (`self_named_binding_trap` isolates
  mechanism D) — dedicated stage-(b) fixtures match it and keep each baseline a clean standalone
  diff. *Cost accepted:* more baselines to maintain, and ife_plant never shows the full end-to-end
  idiom — acceptable because the live WI-015 fusion-tea run is the real end-to-end anchor and
  ife_plant's job is the shape catalog, not the full pipeline.
- **D8. Three companion fixtures, one per mechanism — NOT one folded model (M3).** Folding
  gamma → lcoe (SC-2, specialization-chain resolution), sibling disambiguation (SC-3, two same-type
  instances), and mechanism-D rescue (SC-4, self-named rewrite) into one model reintroduces the
  exact attribution problem D3 uses to reject extending ife_plant — three code paths, one baseline
  diff. So: **(b1)** `spec_chain_channel` — a retyped nested part whose calc *output* wires into a
  cross-part consumer (the gamma → lcoe analog); **(b2)** `sibling_channel_ambiguity` — two
  same-type siblings where a consumer binding disambiguates to the correct instance-scoped channel;
  **(b3)** `self_named_rescue` — a self-named `in x = x` with a *resolvable* upstream, rewritten to
  the channel (the positive companion to `self_named_binding_trap`'s negative). Each is minimal,
  each captures current-incomplete then flips as a separately-attributable diff. *Rejected: one
  model with three separately-assertable pins* — separable pins don't make the baseline diff
  separable, which is the point of the Item 8 pattern.
- **D4. #1 lands in stage (a) and is load-bearing there — it resolves #4's part-def exposes, not
  the two V11 pins (updated per C5).** Round-1 left #1's stage-(a) role unclear ("test rides stage
  (b)"); round-2's C5 forced the question and the answer is cleaner: `_scoped_alias` **is populated
  in stage (a) by #4** (D7 registration), and #1 is the reader that resolves a consumer of a part-def
  expose (wi014_toy's SC-5 shape-A). The **two V11 pins do not need #1** — they are top-level-usage
  exposes registered in the flat `_alias` and found by the unscoped Step 2 (Open Question 1 now
  answered). Stage (b)'s #3 extends the same `_scoped_alias` with consumer-instance scope. *Rejected:
  move #1 wholly to stage (b)* — it would leave #4's part-def exposes unreachable in stage (a) and
  strand the SC-5 shape-A test from its resolver. An **inertness gate** (below) fails if
  `_scoped_alias` is empty after registering the stage-(a) fixtures.
- **D5. Mechanism D has exactly one home: REQ-VBR-10** (the rewrite that implements the rescue).
  *Rejected: REQ-HR-09* — reserved-but-never-committed in Item 9's handoff; released here.

## Architecture

Data flow, left to right, with the stage that touches each seam:

Orchestration order, finalized (the INV-G order that fixes C6b), verified against
`pipeline_builder.py:505-604`:

```
4.5  leaf classify + capture reference_chain (D9); remove genuine FORMULAs from design_attrs
5.5  build_output_registry:
        Phase 1  channels (calc outputs)          Phase 2  CHAIN aliases
        Phase 3  single-hop EXPOSE aliases         →  #4 writes (instance_path, leaf) to _scoped_alias
        Phase 3b CONFIRM tentatives  ← #2 walk reference_chain vs registry; resolve→EXPOSE(+register)
                                        else→FORMULA (in place); cycle guard per M5
        Phase 4  transitive design-attr aliases  (now sees FINAL classifications)
5.6  re-run _remove_formula_from_design_attrs   ← reverted tentatives removed (no false EP, C6b)
5.7  group_deriver (moved after confirm: consumes FINAL design_attrs)
6    backtracker  ← #1 structured _scoped_alias lookup in _resolve_chain_dispatch
7    graph build  ← every .classification reader raises on a surviving tentative (INV-F/C6a)
```

- **#2 (stage a)** — leaf tags `EXPOSE_CHAIN_TENTATIVE` (`computed_attribute_extractor.py:56-109`)
  and records `reference_chain` (D9). The **confirm pass (Phase 3b)** walks `reference_chain` hop by
  hop against the registry — following an alias terminal one more hop (catf_mfe's `tf_coil.volume`)
  or landing on a calc-output channel directly (ife_plant), with the M5 `_visited` cycle guard.
  Resolve → finalize EXPOSE + register the alias; else → revert to FORMULA. REQ-CA-10.
- **#4 (stage a)** drops the `not is_part_def` guard (`:245`) and expands the part-def expose alias
  per instance path (reusing `_build_chain_aliases`'s pattern), writing `(instance_path, leaf)` into
  `_scoped_alias` (D7). REQ-CA-03 revised.
- **#1 (stage a)** inserts a **structured** lookup step in `_resolve_chain_dispatch`, keyed by
  `ScopedAliasKey((prefix, leaf))` split from the consumer's `source_path` against the dedicated
  `_scoped_alias` registry (D7), ordered *before* the unscoped Step 2. REQ-BT-11.
- **#3 (stage b)** is a precedence resolver in `_rewrite_virtual_bindings`: a second index over
  `redefinitions` by specializing-def QN, a `usage_type_map`-driven type-select per virtual
  instance, a three-tier merge (usage override > specialized-def `:>>` > base def), extending the
  CHAIN branch (`:262-264`) and the bare-name/mechanism-D branch (`:242-251`) — per instance,
  behind INV-2. REQ-VBR-10.

## Required Invariants

- **INV-A (no-override).** Every new resolution path only *adds* a hit where the old code fell
  through; it never reorders or overrides an existing hit. #1 runs before the unscoped step but
  after both scoped steps, so a model that already wires via scoped/unscoped lookup is unchanged.
  (Serves the [NEED] constraint and "existing baselines unchanged".)
- **INV-B (unique keys — registration AND lookup, extended per C3).** Every new key is unique by
  construction, and this now covers *lookup* keys, not just registered ones. Registered keys
  (part-def expose, confirmed multi-hop alias) carry the instance path and never rely on the
  first-wins fallback (`output_registry.register_alias:113-125`). The #1 *lookup* key is a
  structured `ScopedAliasKey = (prefix, leaf)` tuple in its own `_scoped_alias` namespace (D7),
  written by #4 and read by #1 from the *same* split of the model's dotted reference — it cannot
  collapse to, or collide with, any flat `_alias` string key. No stringly-typed scope boundary
  anywhere.
- **INV-C (INV-2 preserved).** Stage (b)'s rewrite mutates only per-instance shallow-copied
  bindings; no template or sibling binding is touched (`usage_extractor.py:399`, code is
  `[copy.copy(b) ...]`).
- **INV-D (classification stability via confirm-or-revert).** A tentative multi-hop classification
  becomes EXPOSE **only** if the transitive walk resolves it to a canonical channel; otherwise it
  reverts to FORMULA — byte-identical to today. Over-tagging at the leaf is *safe*: an
  unresolvable tentative changes nothing.
- **INV-E (well-formed chain — the leaf-tag gate, restated on `reference_chain` per C4).** A tag
  requires `reference_chain` with **≥ 2 segments** (root waypoint + ≥ 1 more) and a **single
  terminal leaf** (the last segment). A chain that would leave two competing non-instance terminals
  — the case the single-ref alias resolvers (`computed_attribute_extractor.py:260-264`,
  `graph_builder._resolve_expose_pure:776-780`) mishandle — **stays FORMULA** (never tagged). This
  is what keeps the confirm pass and the Item 6 aggregation walker (`graph_builder.py:264-277,1172+`)
  from ever seeing an ambiguous EXPOSE alias. The confirm walk reads `reference_chain`, not
  `references` (truncated) or the AST (None on replay).
- **INV-F (no tentative escapes — asserts are REAL, C6a).** No downstream consumer may read
  `EXPOSE_CHAIN_TENTATIVE`. The current readers are silent `if`/`elif` with no `else`, so a survivor
  would *vanish* from the graph, not fail. This item **adds an explicit `else: raise`** at every
  reader: `output_registry_builder.py:120` (Phase 1c), `graph_builder.py:253` (module build), `:274`
  (aggregation alias map), `:834` (`_build_attribute_resolution_map`). Until those asserts exist,
  INV-F is not enforced — so they are required stage-(a) edits, not aspiration.
- **INV-G (finalize before consumers — the phase order that fixes C6b).** `ca.classification` must
  be final, and `design_attrs` must reflect it, before any consumer that branches on classification
  or on design-attr membership runs. Concretely: the confirm pass (Phase 3b) runs *before* Phase 4
  and the backtracker; `_remove_formula_from_design_attrs` runs a **second time after confirm**
  (Step 5.6) so a tentative reverted to FORMULA is removed (no false JSON entry point); and
  `group_deriver` moves to Step 5.7, after that removal. The first removal at Step 4.5 stays (genuine
  FORMULAs). Without the second removal, a reverted tentative — absent at 4.5, FORMULA at 5.5 —
  leaks as an entry point, breaking INV-D's "no silent change" claim at the *side-effect* level.

## Component Overview

- **`reference_chain` capture** (`ComputedAttributeData` at `data_models.py:214-217`;
  `computed_attribute_extractor.py` extraction; serializer auto-includes, loader.py:474
  `d.get(...)`) — the additive full-chain-segments field the confirm walk reads (D9). Stage (a), #2.
- **`_classify_attribute_expression`** (`computed_attribute_extractor.py:56-109`) — tag a structural
  candidate `EXPOSE_CHAIN_TENTATIVE` when `reference_chain` is well-formed (INV-E gate); do **not**
  decide EXPOSE-ness here. Stage (a), #2. REQ-CA-10.
- **Confirm pass (Phase 3b)** — new step in `build_output_registry` that walks each tentative's
  `reference_chain` against the registry (the recursive analog of `_resolve_aggregation_input_channel`,
  `graph_builder.py:1043-1079`, **with its `_visited` cycle guard**, M5), finalizing to EXPOSE
  (+ alias registration) or reverting to FORMULA. Stage (a), #2. REQ-CA-10.
- **Classification-reader asserts** (`output_registry_builder.py:120`, `graph_builder.py:253/274/834`)
  — add `else: raise` on a surviving tentative (INV-F/C6a). Stage (a).
- **Second FORMULA-removal pass + group_deriver move** (`pipeline_builder.py:133` twin at Step 5.6;
  group_deriver from :528 to Step 5.7) — the INV-G ordering fix (C6b). Stage (a).
- **Part-def expose alias expansion** — new helper in `pipeline_builder.py` mirroring
  `_build_chain_aliases`; drop the `not is_part_def` guard at `computed_attribute_extractor.py:245`
  and write `(instance_path, leaf)` into `_scoped_alias`. Stage (a), #4. REQ-CA-03 revised.
- **`OutputRegistry` `_scoped_alias` namespace + `ScopedAliasKey`** (`core/output_registry.py`,
  `core/identifier_types.py`) — a tuple-keyed registry + NewType written by #4, read by #1, distinct
  from the flat `_alias` dict. Stage (a), #1/C3/C5. REQ-BT-11.
- **`_resolve_chain_dispatch`** (`dependency_backtracker.py:592-615`) — insert the structured
  `_scoped_alias` lookup before Step 2; reuse `_is_self_reference` unchanged. Stage (a), #1.
  REQ-BT-11; docs 11/24.
- **`_rewrite_virtual_bindings`** (`pipeline_builder.py:190-266`) — the stage-(b) precedence
  resolver: second `redefinitions` index by specializing-def QN, `usage_type_map` type-select,
  three-tier merge, extended CHAIN + bare-name branches. Stage (b), #3. REQ-VBR-10; doc 12.
- **Three companion fixtures** (`tests/fixtures/spec_chain_channel/`, `sibling_channel_ambiguity/`,
  `self_named_rescue/`) — one novel mechanism each (D8). Stage (b), fixture requirement.

## Non-Goals

- **Alias emission into generated output** — the graph-level `output_aliases` field and its YAML
  render are Item 11. **No ComputationGraph field is added here.**
- **Supertype-chain template inheritance** for plain `part x : Subtype` (Item 4 MFE note).
- **EXPOSE_COMPUTED** (calc output + arithmetic) — stays rejected (modeling-assumptions §3).
- **Deleting fusion-tea workarounds** — the `hif_driver_instance` part and two-pass gamma
  feedback are deleted upstream; this item records the coordination note.

## Implementation Notes

- **D9 `reference_chain` capture (do this first — it unblocks everything).** At live extraction,
  populate `reference_chain: list[str]` with the full dotted segments (`["tf_coil","volume_calc","volume"]`)
  using the **segment-list analog** of `extract_feature_chain_name` (`expression_utils.py:250-280`
  already recurses `.operands[0]` + `.target_feature.name` to build the joined string — return the
  list instead of joining). Additive dataclass field (`data_models.py:214-217`); loader adds
  `reference_chain=d.get("reference_chain")`; **no version bump**. Old snapshots: absent → `None` →
  no tag → FORMULA (today's behavior).
- **#2 leaf tag (structural only, on `reference_chain`, INV-E).** Tag `EXPOSE_CHAIN_TENTATIVE` when
  the root is a pure `FeatureChainExpression` (`:104-106`) AND `reference_chain` has **≥ 2 segments**
  rooted at a part-typed waypoint with a single terminal leaf. Do **not** test terminal-is-an-output
  — the leaf cannot (B5). Over-tagging is safe (INV-D). (The round-1 "one ref after removing
  waypoints" rule gave zero for the real pin — C4 — so it is replaced by this.)
- **#2 confirm pass (Phase 3b, the transitive walk).** For each tentative, walk `reference_chain`
  left-to-right building an instance path from the waypoint segments; at the terminal look up a
  scoped channel (direct calc output — ife_plant) OR an alias, following one alias hop to its channel
  (catf_mfe's `tf_coil.volume`). Carry a `_visited` cycle guard modeled on
  `_resolve_aggregation_input_channel` (`graph_builder.py:1043-1050`, the **real** recursive analog —
  not the Phase-4 transitive-default, which is a single dotted lookup, no walk, M5). Resolve →
  register alias + set EXPOSE; else → set FORMULA. Runs after Phase 3, before Phase 4 (INV-G).
- **#4 expansion timing.** The part def has no instances at extraction, so emit a *template* expose
  alias (`is_on_part_definition=True`) and expand per instance path in `pipeline_builder.py`, writing
  `(instance_path, exposed_leaf)` into `_scoped_alias`. `find_instance_paths_for_partdef` is the same
  helper `_build_chain_aliases` uses.
- **#1 structured key (C3/C5).** Lookup: split the consumer's `source_path` at the **last** dot →
  `ScopedAliasKey((prefix, leaf))`, query `_scoped_alias` (not `_alias`); order after Step 1b, before
  the unscoped Step 2; reuse `_is_self_reference`. Registration (#4/#3) and this lookup derive the
  tuple from the same split — they meet by construction (D7). **Inertness gate:** a stage-(a) test
  asserts `_scoped_alias` is non-empty (contains `("demo_plant","total_cost")`) after registering
  wi014_toy.
- **#3 precedence resolver (M4 scope).** Build a second index over `hierarchy_data.redefinitions`
  keyed by specializing-def QN (Item 9's `override_index` at `pipeline_builder.py:202-216` is
  `design_overrides`-only, so this is new). Per virtual instance, use `usage_type_map` to pick the
  applicable specializing def (type-select), then merge three tiers (usage override >
  specialized-def `:>>` > base def) and rewrite `source_path` to the instance-scoped upstream
  channel. Self-named `in x = x`: rewrite to the upstream channel; no resolvable upstream → leave
  as-is (still a modeling error — the negative `self_named_binding_trap` case).
- **Numbering (allocate at plan):** REQ-BT-11 (#1), REQ-CA-10 (#2), REQ-CA-03 revised (#4),
  REQ-VBR-10 (#3, sole mechanism-D home). REQ-HR-09 released. New V-rules from V12: e.g. V12
  multi-hop-EXPOSE coverage, V13 specialization-chain channel coverage.

## Potential Risks

- **#2 over-broadens classification** (INV-D/INV-E). Mitigation: over-tagging is safe by
  construction — an unresolvable tentative reverts to FORMULA; the INV-E single-ref guard keeps
  two-terminal chains out of the alias resolvers; the three non-flipping baselines are the net.
- **catf_mfe reclassification churn beyond the pin (M1).** Relaxing the knockout re-tags *every*
  multi-hop expose on catf_mfe — `blanket_volume_total = blanket.volume`,
  `magnet_volume_total = tf_coil.volume`, and others at `radial_build.sysml:582-602` — some with no
  cross-part consumer. An unconsumed reclassification still drops its synthetic module: a baseline
  diff larger than "the pin flips." Mitigation: **enumerate the full re-tag set at plan** (an
  expected-churn table, per M1) so the captured diff is attributable, not surprising. `first_wall_area`
  / `magnet_surface_area` are single-hop (their producer is a sibling *calc*) — already EXPOSE_PURE,
  not affected.
- **The confirm pass double-resolves an EXPOSE alias into the aggregation walker (M2).** More
  EXPOSE aliases feed `_build_aggregation_module`'s alias map (`graph_builder.py:264-277,1172+`).
  Mitigation: INV-E (single non-instance ref) + INV-F (no tentative survives) are the guards; add
  the assertion at the walker entry and cover it with an aggregation-fixture regression.
- **Reverted-tentative false entry point (C6b, now closed by INV-G).** Was: a tentative reverting to
  FORMULA after the Step-4.5 removal leaked a JSON entry point. Mitigation in the design: the second
  removal pass at Step 5.6 + `group_deriver` moved to 5.7. Residual risk is ordering-fragility —
  covered by a regression asserting no entry point for a reverted tentative.
- **Snapshot recapture set + in-place mutation (M6).** No `SNAPSHOT_FORMAT_VERSION` bump (D9), so the
  ~15 non-multi-hop snapshots load unchanged. The fixtures that **must** be recaptured to carry
  `reference_chain` are exactly those with a multi-hop EXPOSE: **catf_mfe, ife_plant, and the three
  stage-(b) fixtures** — a license-gated task (expires **2026-08-06**). Second M6 constraint: the "no
  tentative is ever serialized" guarantee holds only if the confirm pass mutates the **shared**
  `computed_attrs` objects in place; an implementer who rebuilds from copies would serialize live
  tentatives. Both are stated as implement constraints.
- **Companion-fixture capture blocked by license** (expires **2026-08-06**). Mitigation: author and
  capture the three fixtures' current-incomplete baselines *before* the window, or after renewal;
  stage (a)'s flips are license-free offline snapshots (the recaptured multi-hop fixtures aside).
- **catf_mfe alias-collision noise doesn't clear** after unique keys. Mitigation: the collision
  count summary (`output_registry.alias_collision_count`) is the assertion target; a residual count
  is a reviewed diff, not a silent pass.

## Integration Strategy

Stage (a) ships first as a self-contained pass: leaf tag + confirm pass + #4 expansion + #1
structured lookup + REQ-CA-03 revision. Three baselines flip (ife_plant shape-4, catf_mfe's
`cryo_load.magnet_volume` pin *plus its enumerated multi-hop re-tag set*, wi014_toy shape-A); the
other three stay byte-identical; docs 16/11/24/10 move with the code. Stage (b) is a continuation
pass in the same artifacts: the precedence resolver + three companion fixtures (each captured
current-incomplete then flipped as a separate reviewed diff, Item 8 pattern), doc 12 +
verification-matrix rows. Both complete before Item 11 (which adds `output_aliases` and surfaces the
names). agentic-mbse impact is recorded here, executed in Item 12: the MODELING_GUIDE content list
(supported cross-part shapes + the precedence rule) and the self-named-binding FAIL check with its
`self_named_binding_trap` negative fixture.

## Validation Approach

- **Stage (a) executable gate (license-free):** ife_plant shape-4 pin flips (`EXPECTED_UNCOVERED`
  in `test_ife_plant.py` shrinks by `cryo_load.magnet_volume`) — **direct-calc-output** shape;
  catf_mfe `[cryo_load.magnet_volume]` flips via the **alias-terminal** transitive hop with clean
  strict generation, and its enumerated multi-hop re-tag set matches the expected-churn table (M1);
  wi014_toy shape-A resolves and its REQ-CA-09 recorded-deferral pin flips to PASS (asserted alias
  `demo_plant.total_cost`). Plus three guard tests forced by round-2: **inertness** (`_scoped_alias`
  non-empty after registering wi014_toy, C5); **no false EP** (a tentative reverted to FORMULA
  produces no JSON entry point, C6b/INV-G); **tentative fail-fast** (a synthetic surviving tentative
  raises at each reader, C6a/INV-F). A negative: a genuine multi-hop FORMULA (arithmetic over a
  chain) stays FORMULA (INV-D). Red-first unit tests on real Pydantic/extraction objects (no mocks).
- **Stage (b) executable gate (three fixtures, separate diffs):** `spec_chain_channel` — gamma → lcoe
  channel edge asserted present in pipeline YAML (SC-2); `sibling_channel_ambiguity` — the consumer
  binding resolves to the correct instance-scoped channel, not a collision (SC-3);
  `self_named_rescue` — the self-named binding is rewritten to its upstream channel (SC-4). Each
  captured current-incomplete before its code lands.
- **WI-015 live anchor (on top of committed gates):** generate the fusion-tea IFE set with no
  hand-plumbing, assert the gamma → lcoe edge in the artifact, run run-C end-to-end, compare lcoe
  to the register's anchor within tolerance (spec procedure §WI-015). Record gamma's moved
  channel name for the fusion-tea coordination note.
- **Regression net:** the three non-flipping baselines (incl. solar_battery) stay byte-identical;
  `mypy src/` and `ruff check src/` clean.

## Next-Stage Handoff

- **Fixed:** the split (stage a first, both in Item 10); #2 in the classification/alias path (D2)
  via tentative-at-leaf + confirm-by-transitive-walk over `reference_chain` (D6/D9); structured
  `_scoped_alias` key with both sides written (D7); #1 load-bearing in stage (a) for #4's exposes
  (D4); three per-mechanism fixtures (D8); mechanism D homed in REQ-VBR-10 (D5); INV-F asserts real
  (C6a); INV-G phase order (C6b); no ComputationGraph field; no snapshot version bump (D9/M6).
- **Open (resolve at implement, probe-first; license live, expires 2026-08-06):**
  (1) **why `extract_feature_refs` truncates** the chain (agentic-mbse internal, unread) — confirms
  D9's segment-list capture is the right seam; the *first* probe. (2) the confirm walk over
  `reference_chain` on *both* pin shapes — ife_plant's direct calc-output terminal AND catf_mfe's
  alias terminal one hop further (validates C1). (3) the full catf_mfe multi-hop re-tag set for the
  M1 churn table. (4) `find_instance_paths_for_partdef` returns `demo_plant`'s path for #4.
  (5) the specialization-chain resolution on each stage-(b) fixture once authored.
- **De-risk first:** probe (1) then capture `reference_chain` for one fixture and confirm the walk
  flips one pin *before* the full build-out — it validates B7 and the whole D9→confirm chain.
- **Fallback if a probe fails (m1):** if a pin turns out reason-two, or the confirm walk cannot
  reach its terminal, that pin moves to stage (b) and the split headline is revised to "stage (a)
  flips the pin(s) it can, stage (b) covers the rest" — stated now rather than discovered at
  implement. The source trace says B1 holds, so this is a low-probability path.
- **Escalation (M4):** if stage (b) exceeds a single day at implement, STOP and report for a
  split-out ruling — do not push through.

## Round-3 Amendment (D-C, applied at implement — offline==live parity, APPROVED)

**Problem the design did not anticipate.** M6 says serialize the POST-confirm `EXPOSE_PURE` state; the
Phase-3b confirm walk (the only code that resolves a multi-hop chain to its correct transitive channel)
runs only on `EXPOSE_CHAIN_TENTATIVE` CAs. Those two facts contradict D9's stated intent ("`reference_chain`
is captured so the walk can run on the offline path"). On snapshot reload a multi-hop pin arrives already
`EXPOSE_PURE`, the confirm walk skips it, and the naive Phase-3 alias path resolves the ambiguous terminal
through the first-wins-corrupted flat `_alias` — the exact B2 false-positive. Result: catf's
`cryo_load.magnet_volume` wired LIVE to the correct `tf_coil__volume_calc__volume` but OFFLINE to the wrong
`plasma_region__volume_calc__volume` (a lying sim, not a crash). The live path never hits this because the CA
is still tentative when Phase 3 runs.

**Amendment (D-C).** `build_output_registry` (`output_registry_builder.py`) reconstructs the pre-confirm
tentative state, before Phase 3, for exactly the multi-hop candidates: an already-`EXPOSE_PURE` CA whose
`reference_chain` is a part-rooted chain of ≥2 segments (`reference_chain[0]` is not a calc-usage short name
— the durable INV-E signal; the AST is None on replay, but `EXPOSE_PURE` already encodes the pure-FeatureChain
root the live leaf-tag checked). The existing confirm pass then reproduces the live registration order
identically on both paths. Live CAs are still tentative here → this is a no-op on the live path.

**Why this and not "serialize the tentative marker" (the rejected alternative).** Serializing
`EXPOSE_CHAIN_TENTATIVE` would leak an *unconfirmed* classification across the snapshot format boundary — a
worse contract than reconstructing it deterministically at load from the durable `reference_chain`. M6's
serialized state stays `EXPOSE_PURE`; no reader ever sees a tentative (the confirm pass always finalizes
before any reader, and INV-F's terminal raise still guards a survivor). This reconciles M6 with D9 rather
than overriding either.

**Verification evidence (offline == live, both pin shapes):**
- catf (alias-terminal hop): OFFLINE and LIVE both → `CATFMFERadialBuild__catf_radial_build__tf_coil__volume_calc__volume`.
- ife (direct calc-output): OFFLINE and LIVE both → `IfePlantSubsystems__radial_build__tf_coil__volume_calc__volume`.
- Pinned by the regenerated catf pipeline baseline (`cryo_load` module's `producer_channel` is the tf_coil channel)
  and the full green gate (1947 passed; ruff src/ 21; mypy src/ 109).
- Implementation gotcha: `CalcUsageData.instance_name` is short in some fixtures but the full QN in others —
  derive short calc-usage names from `qualified_name.rsplit("__", 1)[-1]`.

**Invariant impact:** none broken. INV-D (confirm-or-revert), INV-F (no tentative escapes), INV-G (phase
order) all hold; D-C only reconstructs the input state the confirm pass was always meant to consume offline.

---

## Round-4 Amendments (applied at Phase-7 scoping — stage (b) mechanism seams, APPROVED)

Phase 7's empirical scoping (three companion fixtures probed live + offline) confirmed M4's "not one
seam." The design's Architecture bullet said all three stage-(b) mechanisms land in
`_rewrite_virtual_bindings` (#3). Two of the three actually live elsewhere or take a different shape.
These are seam/shape corrections, not architecture changes — each still delivers its SC criterion behind
the same invariants.

**Amendment D-D (b2 sibling disambiguation lives in the backtracker #1 lookup, not the rewrite).**
The design put SC-3 (two same-type siblings, consumer disambiguates to the correct instance channel) in
`_rewrite_virtual_bindings`. But stage (a)'s #4 already registers the instance-scoped aliases
(`('twin_plant.chamber_a','power')`, `('twin_plant.chamber_b','power')`) into `_scoped_alias`, and the
consumer binding `chamber_b.power` is a plain CHAIN — nothing to *rewrite*. The gap is purely in the
**reader**: `_resolve_chain_dispatch`'s #1 step (`dependency_backtracker.py:610-622`) splits `chamber_b.power`
at the last dot → `('chamber_b','power')`, which MISSES the registered `('twin_plant.chamber_b','power')`
because it lacks the consumer's instance-scope prefix. **This is CONSISTENT with stage (a)'s design, not a
departure from it:** #1 is the `ScopedAliasKey` reader (D4/D7), and Step 1 of the very same dispatch
(`:596-602`) already prepends `_consumer_scope_dotted(usage)` to the plain scoped lookup. D-D just gives the
`_scoped_alias` step (#1, Step 1c) the identical consumer-scope prepend Step 1 has — try
`(consumer_scope + '.' + prefix, leaf)` before the bare `(prefix, leaf)`, ordered before the unscoped Step 2
(INV-A: only adds a hit where the ladder fell through). So SC-3 is delivered by extending the stage-(a) #1
machinery, and REQ-BT-11 (#1) — not REQ-VBR-10 (#3) — is its home.

**Amendment D-E (b3 mechanism-D rescue is full-QN self-reference detection, not the bare-name branch).**
The design said "extend the bare-name / mechanism-D branch (`_rewrite_virtual_bindings:242-251`) — self-named
`in x = x`." But a self-named binding does NOT reach the rewrite as a bare name: extraction resolves it to a
full REFERENCE QN pointing at the calc usage's OWN parameter (`RescueLib::'Rescue Plant'::sink_calc::throughput`
— identical shape to `self_named_binding_trap`, confirmed by the committed trap snapshot). The bare-name branch
(`:243-253`) never sees it; the binding is a REFERENCE, not a bare CHAIN. So mechanism D is a **self-reference
detection**: the binding's `source_path` parent is the consuming usage itself and its leaf is one of that calc
def's input params, AND an outer same-named part attribute resolves to a real channel → rewrite to that
upstream channel; no resolvable upstream → leave as-is (the trap, still a modeling error). The rescue may land
as a pre-resolution rewrite (rewrite the self-ref `source_path` to the outer instance-scoped attribute path,
`rescue_plant.throughput`, which the existing chain dispatch then resolves through the EXPOSE alias) — the
faithful reading of "rewrite to the upstream channel." REQ-VBR-10 remains mechanism D's sole home (D5); only
the detected *shape* changes. Intent unchanged; characterization corrected.

**Amendment D-F (b1 fixture idiom — the `:>>` redefinition MUST be the bare form).** Not a code change; a
fixture/authoring constraint the design implied but did not state. A value-carrying `:>>` redefinition must be
authored as bare `:>> attr = value` (which parses as a ReferenceUsage), NOT `attribute :>> attr = value`
(an AttributeUsage). `_extract_single_redefinition` (`hierarchy_resolver.py:71`) only scans ReferenceUsage
members, so an `attribute :>>` chain redefinition is silently NOT extracted — `hierarchy_data.redefinitions`
comes back empty and #3 has nothing to read. b1 `spec_chain_channel` uses the bare form (matching ife_plant
shape 2 and the real fusion-tea idiom — see the agentic-mbse note). This `attribute :>>` gap is recorded as an
agentic-mbse guidance/validation candidate for Item 12 (below), NOT fixed in this item — fusion-tea uses only
the bare form (86 occurrences, zero `attribute :>>`; the real gamma edge is
`hif_driver.sysml:82 :>> cost_per_joule = meier_cost.gamma`, exactly b1's shape), so no extraction relaxation
is needed here.

**agentic-mbse impact addition (Item 12, MODELING_GUIDE / validation).** Add to the content list: the
value-carrying redefinition idiom is the **bare** `:>> attr = value` form; `attribute :>> attr = <expression>`
is a **known-unsupported** shape (the AttributeUsage redefinition is dropped at extraction,
`hierarchy_resolver.py:71`). Item-12 guidance should teach the bare form and add a validation warning when an
`attribute :>>` carries an expression RHS (silent no-op today). This is guidance/validation, not codegen code.

**Invariant impact:** none broken. D-D preserves INV-A (additive reader hit). D-E preserves INV-2
(per-instance rewrite, no sibling corruption) and REQ-VBR-10's mechanism-D homing. D-F is authoring guidance.

---
Next Step: After approval → `/_my_plan`. Stage (a): red-first tests + leaf tag + confirm pass + #4
+ #1 + baseline flips (with the M1 churn table). Stage (b): precedence resolver + three companion
fixtures + captures.
