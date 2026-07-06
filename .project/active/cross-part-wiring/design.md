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

**Blast radius, stage (a):** four low-risk seams, all additive: (1) the leaf tags a tentative
instead of dropping to FORMULA (`computed_attribute_extractor.py:104-109`); (2) a **confirm pass**
runs the transitive walk and finalizes EXPOSE-or-FORMULA (generalizes `graph_builder.py:789`, runs
at `build_output_registry`); (3) part-def alias expansion (guard at
`computed_attribute_extractor.py:245`, Phase-3 registration); (4) a structured consumer-scoped
lookup step (`dependency_backtracker.py:592-615`). The [NEED] no-override rule holds — every new
path only *adds* a resolution that previously fell through, and an unconfirmed tentative reverts to
today's FORMULA. Committed baselines flip (ife_plant shape-4, catf_mfe's pin + its enumerated
multi-hop re-tag set per M1, wi014_toy shape-A); the other three stay byte-identical. This is
larger than "relax a knockout," but still no new fixture and no cross-codebase reach.

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
change. Stage (a) also expands part-def exposes per instance and adds a consumer-scoped alias
lookup in its own key namespace.

**Reason two — the producing calc's own bindings are wrong per instance, so the value on the
channel is wrong (or self-referential).** A specialized nested part's calc needs its inputs
resolved through the redefinition chain (usage override > specialized-def `:>>` > base def), and
a self-named `in x = x` needs redirecting to its upstream. This *does* rewrite bindings, per
instance, and is the novel machinery. This is **stage (b)**, built on Item 9's per-instance copy.

The key insight the spec-review surfaced: **the two committed pins are reason one, not reason
two.** Stage (a) alone flips them. Stage (b)'s value (gamma → lcoe) is reason two and has no
committed fixture — so stage (b) brings its own (three, one per mechanism).

This composes with existing pieces, adding no parallel mechanism: the leaf still classifies (now
tagging a tentative), the confirm pass reuses `_resolve_expose_pure`'s resolution generalized to a
transitive walk, part-def expansion reuses `_build_chain_aliases`'s per-instance-path pattern, the
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
  a structural candidate `EXPOSE_CHAIN_TENTATIVE` (pure `FeatureChainExpression`, ≥1 part-typed
  waypoint, exactly one non-instance terminal ref — see INV-E). A confirm pass at
  `build_output_registry` time (Step 5.5, where the registry holds all channels + Phase-2/3
  aliases) runs the transitive walk; on resolution it finalizes to the EXPOSE alias variant, else
  **reverts to FORMULA** (today's behavior — no silent change, INV-D). *Rejected: mechanism (i),
  plumb calc-def output sets into `_classify_attribute_expression`* — the leaf is architecturally
  barred from resolution imports (`:7-8`), and catf_mfe's alias-terminal is undecidable even with
  calc-def outputs (it needs the whole registry, B5). *Tentative-state representation (C2
  requirement):* a distinct classification enum value that **no downstream consumer reads** —
  the confirm pass rewrites `ca.classification` in place before Step 6/7, and the graph builder +
  aggregation walker assert no `EXPOSE_CHAIN_TENTATIVE` survives (fail-fast).
- **D7. The #1 consumer-scoped lookup uses a STRUCTURED key in its own registry namespace, not a
  dotted string in the shared `_alias` dict (C3).** A `ConsumerScopedKey = NewType(tuple[str, str])`
  over `(consumer_scope, source_path)`, stored in and looked up from a dedicated
  `_consumer_scoped` dict on `OutputRegistry` — so it cannot collide with flat `_alias` string keys
  (the `a.b.c` ⇄ `a.b`-exposes-`c` ambiguity the review found). The `_is_self_reference` guard is
  re-derived for the new step (channel-based, key-shape-independent). *Rejected: reserved-separator
  string key* — still one flat dict, still a stringly-typed boundary doc 10 exists to forbid.
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

Orchestration order (verified `pipeline_builder.py:505-604`):
Step 4.5 classify (leaf) → Step 5.5 `build_output_registry` (Phases 1-4 + **new confirm pass**)
→ Step 6 backtracker lookup → Step 7 graph build.

```
extraction (4.5)        registry build (5.5)              lookup (6)            orchestration/rewrite
────────────────        ────────────────────              ──────────           ─────────────────────
classify attr    ─(a)→  CONFIRM tentatives ────────(a)→   _resolve_chain_      _rewrite_virtual_bindings
 (#2 tag TENTATIVE) │    (#2 transitive walk;             dispatch (#1          (#3 stage-b precedence
                    │     resolve→EXPOSE else→FORMULA)     structured consumer-   resolver: index +
                    │    #4 part-def expose expand         scoped step, own       type-select + merge,
                    │     per instance path                namespace)      ─(b)→  CHAIN + bare-name)
                    └→ (finalized classification only reaches Step 6/7)
```

- **#2 (stage a)** spans two seams across two steps. The leaf tags a candidate
  `EXPOSE_CHAIN_TENTATIVE` (`computed_attribute_extractor.py:56-109`). The **confirm pass** at
  registry-build time runs the transitive N-segment walk (generalizing `_resolve_expose_pure`,
  `graph_builder.py:789`): resolve the chain hop by hop against the registry, following an alias
  terminal one more hop (catf_mfe) or landing on a calc-output channel directly (ife_plant). Resolve
  → finalize EXPOSE + register the alias; no resolution → revert to FORMULA. REQ-CA-10.
- **#4 (stage a)** drops the `not is_part_def` guard (`:245`) and expands the part-def expose alias
  per instance path (reusing `_build_chain_aliases`'s pattern) before Phase-3 registration, yielding
  instance-scoped keys like `demo_plant.total_cost`. REQ-CA-03 revised.
- **#1 (stage a)** inserts a **structured** consumer-scoped lookup step in `_resolve_chain_dispatch`,
  keyed by `ConsumerScopedKey(consumer_scope, source_path)` against a dedicated `_consumer_scoped`
  registry namespace (D7), ordered *before* the unscoped Step 2. REQ-BT-11.
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
  first-wins fallback (`output_registry.register_alias:113-125`). The #1 consumer-scoped *lookup*
  key is a structured `(consumer_scope, source_path)` tuple in its own registry namespace (D7) —
  it cannot collapse to, or collide with, any flat `_alias` string key. No stringly-typed
  scope boundary anywhere.
- **INV-C (INV-2 preserved).** Stage (b)'s rewrite mutates only per-instance shallow-copied
  bindings; no template or sibling binding is touched (`usage_extractor.py:399`, code is
  `[copy.copy(b) ...]`).
- **INV-D (classification stability via confirm-or-revert).** A tentative multi-hop classification
  becomes EXPOSE **only** if the transitive walk resolves it to a canonical channel; otherwise it
  reverts to FORMULA — byte-identical to today. Over-tagging at the leaf is *safe*: an
  unresolvable tentative changes nothing.
- **INV-E (single non-instance ref — the aggregation-walker/alias-resolver guard, M2).** The
  alias resolvers (`computed_attribute_extractor.py:260-264`, `graph_builder._resolve_expose_pure`
  `:776-780`) assign `output_name = ref.name` in a loop that assumes **exactly one** non-instance
  ref. The multi-hop shape can carry a part-usage waypoint that bucket 2b tags as a sibling ref
  (`:80`) — two non-instance refs, last-iteration-wins. Guard: a tentative with more than one
  non-instance ref after removing part-typed waypoints **stays FORMULA** (never tagged). Stated so
  the confirm pass and the Item 6 aggregation walker (`graph_builder.py:264-277,1172+`) never see
  an ambiguous EXPOSE alias.
- **INV-F (no tentative escapes, C2).** No downstream consumer reads `EXPOSE_CHAIN_TENTATIVE`.
  The confirm pass finalizes every tentative before Step 6/7; the graph builder and aggregation
  walker assert none survives (fail-fast).

## Component Overview

- **`_classify_attribute_expression`** (`computed_attribute_extractor.py:56-109`) — tag a
  structural candidate `EXPOSE_CHAIN_TENTATIVE` (INV-E gate), do **not** decide EXPOSE-ness here.
  Stage (a), #2. REQ-CA-10.
- **Confirm pass** — new step in `build_output_registry`/`pipeline_builder.py` (Step 5.5) that runs
  the transitive N-segment walk (generalizing `_resolve_expose_pure`, `graph_builder.py:759-803`)
  over each tentative, finalizing to EXPOSE (+ alias registration) or reverting to FORMULA. Stage
  (a), #2. REQ-CA-10.
- **Part-def expose alias expansion** — new helper in `pipeline_builder.py` mirroring
  `_build_chain_aliases`; drop the `not is_part_def` guard at `computed_attribute_extractor.py:245`
  and expand per instance path. Stage (a), #4. REQ-CA-03 revised in place.
- **`OutputRegistry` `_consumer_scoped` namespace + `ConsumerScopedKey`** (`core/output_registry.py`,
  `core/identifier_types.py`) — a tuple-keyed registry + NewType for the #1 lookup, distinct from
  the flat `_alias` dict. Stage (a), #1/C3. REQ-BT-11.
- **`_resolve_chain_dispatch`** (`dependency_backtracker.py:592-615`) — insert the structured
  consumer-scoped lookup before Step 2; re-derive `_is_self_reference` for the new step. Stage (a),
  #1. REQ-BT-11; docs 11/24.
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

- **#2 leaf tag (structural only, INV-E).** The leaf tags `EXPOSE_CHAIN_TENTATIVE` when: root is a
  pure `FeatureChainExpression` (`:104-106`), at least one waypoint is a part-typed sibling ref, and
  after removing part-typed waypoints **exactly one** non-instance ref remains (the terminal). It
  does **not** test terminal-is-an-output — it cannot (B5). Over-tagging is safe (INV-D).
- **#2 confirm pass (the transitive walk).** At Step 5.5, for each tentative, walk the chain
  left-to-right building an instance path from the waypoint segments; at the terminal look up a
  scoped channel (direct calc output, ife_plant) OR an alias, following alias indirection to a
  canonical channel (catf_mfe's `tf_coil.volume`). Resolve → register the alias, set classification
  to the EXPOSE variant; no resolution → set FORMULA. Ordering: run **after** Phase-3 single-hop
  EXPOSE aliases register, so an alias terminal is already present to follow (a Phase-3b, mirroring
  the Phase-4 transitive-default precedent). Probe the live AST/registry first (see Handoff).
- **#4 expansion timing.** The part def has no instances at extraction, so emit a *template* expose
  alias (mark `source="expose_pure"`, `is_on_part_definition=True`) and expand per instance path in
  `pipeline_builder.py` before the aliases reach `build_output_registry`.
  `find_instance_paths_for_partdef` is the same helper `_build_chain_aliases` uses.
- **#1 structured key (C3).** `ConsumerScopedKey((consumer_scope, source_path))` where
  `consumer_scope = self._consumer_scope_dotted(usage)`, looked up in the dedicated
  `_consumer_scoped` registry (not `_alias`); re-derive `_is_self_reference` for the new step; order
  after Step 1b, before the unscoped Step 2.
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
- **#1 turns out load-bearing for the pins after all** (contradicts the source trace). Mitigation:
  probe the registered key vs the consumer's constructed key (Open Question 1) *before* committing
  the stage-(a) flips; #1 is already in stage (a), so a positive finding needs only a note.
- **Companion-fixture capture blocked by license** (expires **2026-08-06**). Mitigation: author and
  capture the three fixtures' current-incomplete baselines *before* the window, or after renewal;
  stage (a)'s flips are license-free offline snapshots.
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
  `demo_plant.total_cost`). A negative: a genuine multi-hop FORMULA (arithmetic over a chain) stays
  FORMULA (INV-D). Red-first unit tests on real Pydantic/extraction objects (no mocks).
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
  via tentative-at-leaf + confirm-by-transitive-walk (D6); structured consumer-scoped key (D7);
  three per-mechanism fixtures (D8); #1 in stage (a) (D4); mechanism D homed in REQ-VBR-10 (D5); no
  ComputationGraph field.
- **Open (resolve at implement, probe-first; license live, expires 2026-08-06):**
  (1) registered key vs consumer-constructed key for the shape-4 pin — is #1 load-bearing for the
  pins? (2) the confirm-pass transitive walk on *both* pin shapes — ife_plant's direct calc-output
  terminal AND catf_mfe's alias terminal one hop further (validates C1's fix); (3) the full
  catf_mfe multi-hop re-tag set for the M1 expected-churn table; (4) `find_instance_paths_for_partdef`
  returns `demo_plant`'s path for #4; (5) the specialization-chain resolution on each stage-(b)
  fixture once authored.
- **De-risk first:** probes (2) and (3) before committing stage-(a) flips — they validate B1/B6 and
  bound the catf_mfe diff.
- **Fallback if a probe fails (m1):** if a pin turns out reason-two, or the confirm walk cannot
  reach its terminal, that pin moves to stage (b) and the split headline is revised to "stage (a)
  flips the pin(s) it can, stage (b) covers the rest" — stated now rather than discovered at
  implement. The source trace says B1 holds, so this is a low-probability path.
- **Escalation (M4):** if stage (b) exceeds a single day at implement, STOP and report for a
  split-out ruling — do not push through.

---
Next Step: After approval → `/_my_plan`. Stage (a): red-first tests + leaf tag + confirm pass + #4
+ #1 + baseline flips (with the M1 churn table). Stage (b): precedence resolver + three companion
fixtures + captures.
