# Design Review: Cross-Part Channel Wiring (SC-5 stage 2)

**Design:** `.project/active/cross-part-wiring/design.md`
**Spec:** `.project/active/cross-part-wiring/spec.md`
**Review File:** `.project/active/cross-part-wiring/design-review.md`
**Date:** 2026-07-05
**HEAD reviewed:** a3d3dbb (matches design's `HEAD at design`)

---

## Fundamental Assessment

**Concerns — Revise (not Rework).** The foundation is right. The split is well-argued, the
classification-layer fix (D2) is the correct home for #2, and the companion-fixture decision
(D3) is defensible. B1 — the split's load-bearing bet — **holds**: I traced both committed pins
independently against fixture source and both are reason-one (already-computed, instance-
independent, single canonical channel). So the split's headline economics are real.

But the review found four problems that land on the item's own stated failure mode — silent
mis-wiring — and three of them sit on the critical stage-(a) path:

1. **The two committed pins are not the same chain shape** (the design and spec both assert they
   are). catf_mfe terminates at an EXPOSE-alias attribute, not a calc output. The #2 discriminator
   as written fires on one pin and not the other.
2. **The #2 discriminator is not decidable at the classifier seam** the design names. That leaf
   has instance names but not calc-def output sets, and is barred from resolving them.
3. **The #1 consumer-scoped lookup key can silently cross-wire** — a false lookup hit that INV-B
   does not reason about, sharing a flat dict with same-shaped registered keys.
4. **Stage (b) is a new precedence resolver, not "one seam."** No new extraction (good, verified),
   but a new index + type-selection + merge + two branches. The escalation guard is being
   evaluated against an understated scope.

None is fatal. The work item is sound and each finding has a concrete fix. But #2's discriminator
is the weakest joint in the design and it carries SC-1 (both pin flips), so this is a real Revise,
not a rubber stamp.

I verified the design's code anchors: `_rewrite_virtual_bindings` (190-266), the override index
(202-216), `_build_chain_aliases` (338-391), and `usage_extractor.py:399` (INV-2) are all accurate.
INV-2 is stronger in code (`[copy.copy(b) ...]`) than Item 9's design text describes — B3 holds.

---

## Dimensional Review

### 1. Spec Compliance
**Assessment:** Concerns

The design meets the spec's structure — split decided, six scope pieces mapped, companion fixture
chosen, census allocated, WI-015 procedure inherited. Two compliance gaps:

- **SC-1 is at risk for one of its two pins (Critical, see C1).** The spec cross-map (spec:70)
  and the design's Research Findings (design.md:65-69) both state both pins are the shape
  `magnet_volume_total = tf_coil.volume_calc.volume`. Verified against source: **only ife_plant
  is.** catf_mfe's actual RHS is `attribute magnet_volume_total : Real = tf_coil.volume`
  (`tests/fixtures/catf_mfe_model/designs/catf_mfe/radial_build.sysml:582`), where `tf_coil.volume`
  is itself an EXPOSE alias (`radial_build.sysml:458: attribute volume : Real = volume_calc.volume`).
  So catf_mfe's chain terminal is an **attribute that aliases** a calc output, not the calc output
  itself. The #2 discriminator the design specifies ("terminal feature is a calc-usage output",
  design.md:136,254-256) matches ife_plant but not catf_mfe. SC-1 says stage (a) flips *both* pins;
  as specified it flips one.

- **"Existing baselines unchanged" is under-scoped for catf_mfe (Major, see M1).** The design says
  three baselines flip and "the other three stay byte-identical" (design.md:38). It scopes the
  catf_mfe flip as "`[cryo_load.magnet_volume]` flips to a producer channel" (design.md:306) — a
  single pin. But relaxing the knockout reclassifies **every** multi-hop expose on catf_mfe, and
  catf_mfe carries several top-level aggregates of that shape:
  `blanket_volume_total = blanket.volume`, `magnet_surface_area = magnet_surface_calc.area`,
  `first_wall_area = first_wall_area_calc.area` (`radial_build.sysml:582-602`), some with no
  cross-part consumer. Reclassifying an unconsumed aggregate FORMULA→EXPOSE changes its extraction
  path (drops the synthetic module) — a baseline diff beyond the pin. The design's blast-radius
  section does not enumerate this. The diff may still be acceptable (it's a reviewed capture), but
  it is bigger than "the pin flips," and the reviewer of that capture needs the enumeration to
  attribute it.

### 2. Pattern Consistency
**Assessment:** Pass (with one note)

The design reuses existing patterns well and adds no parallel mechanism: classification stays in
`computed_attribute_extractor`, alias expansion reuses `_build_chain_aliases`'s per-instance-path
walk (verified at `pipeline_builder.py:338-391`), lookup stays in `_resolve_chain_dispatch`'s
ordered ladder, rewrite stays in `_rewrite_virtual_bindings`. B4 (part-def expose reuses the CHAIN
per-instance-path machinery) is a genuine structural match. The companion-vs-extend decision (D3)
correctly follows the Item 8 "one novel mechanism per dedicated fixture" pattern — which is exactly
why folding three mechanisms into one companion (M3) is in tension with it.

### 3. Abstraction Quality
**Assessment:** Concerns

The layering is right (extraction → registration → lookup → orchestration, each stage owning its
seam). The problem is at one specific seam:

- **#2's discriminator is placed in a layer that cannot compute it (Critical, C2).**
  `_classify_attribute_expression` (`computed_attribute_extractor.py:35-109`) is a leaf extractor.
  Its docstring (lines 7-8) states it "does NOT import from analysis/, resolution/, or
  generation/." Its inputs are `refs`, `owning_part_qualified_name`, `calc_usage_names` (instance
  *names*), `sibling_attr_names`, `expression_ast`. To decide "terminal feature is a calc-usage
  **output**" you need the calc definition's output set — computed downstream as
  `{attr.name for attr in calc_def.output_attributes}` (`expression_compiler.py:481`) from a
  resolved calc def. This leaf has no calc def and cannot resolve one. Walking `expression_ast`
  recovers the terminal *name*; it cannot confirm the name is an *output*. The design's "probe the
  live AST first" note (design.md:258,328) recovers the name, not the output-ness. So the
  discriminator as written is either (a) not implementable at the named seam without plumbing
  calc-def output sets into a leaf that is architecturally barred from having them — a real new
  input, not a "relax the knockout" one-liner — or (b) implemented as a weaker structural proxy
  (pure chain + a `calc_ref` present + a relaxed sibling), which is broader than the design intends
  and reopens exactly the INV-D over-classification risk the knockout guards. This has to be
  resolved before "#2 is three additive edits" is believable.

### 4. Duplication Avoidance
**Assessment:** Pass

No parallel structures introduced. Reuse of `_build_chain_aliases`, the Item 9 override index, and
the CHAIN ladder is genuine, not copy-paste. The good news from the stage-(b) trace: the
specialized-def `:>>` values are **already extracted** into `hierarchy_data.redefinitions`
(`hierarchy_resolver.py:144-164`, no type filter; collected at `:538-540`) — stage (b) reads
existing data, it does not duplicate the extraction. Verified.

### 5. Data Structure Clarity
**Assessment:** Concerns

The N-segment key design is clear where segment count differs, but the consumer-scoped key is
ambiguous:

- **The #1 key `f"{consumer_scope}.{source_path}"` is not unique by construction (Critical, C3).**
  Both operands can be dotted, and they are joined with a bare `.`, so the boundary is
  unrecoverable. Two logically different bindings collapse to one string. Concrete construction:
  consumer QN `Design__a__x` gives `consumer_scope="a"` (`_consumer_scope_dotted`,
  `dependency_backtracker.py:461-464`) and CHAIN `source_path="b.c"` → key `a.b.c`; consumer QN
  `Design__a__b__y` gives `consumer_scope="a.b"` and `source_path="c"` → key `a.b.c`. Worse, that
  same string is the shape of a **registered** #4 part-def-expose key (`a.b` exposing `c`,
  `output_registry_builder.py:179`). All three live in one flat `_alias` dict
  (`output_registry.py:43`), looked up by raw `.get` (`:140-142`); segment count is never stored
  or checked. So the #1 lookup can hit an unrelated third channel and silently mis-wire. The
  `_is_self_reference` guard (`dependency_backtracker.py:601`) only rejects the consumer's *own*
  output — a false hit onto a third channel passes it. INV-B ("unique by construction, no reliance
  on first-wins") reasons only about *registration* collisions; #1 and #2 are *lookup* keys that
  register nothing, so INV-B is a category error for them and leaves this risk unaddressed. This is
  the epic's own failure mode (silent mis-wiring), on the stage-(a) path.

### 6. Route Safety
**Assessment:** Concerns

INV-A (no-override, additive-only) is the right discipline and the ordering rule (#1 before
unscoped Step 2, after both scoped steps) is stated. But two routing hazards:

- The #1 false-hit (C3) is a route-safety failure: an additive lookup step that can resolve to the
  wrong channel is not "additive-only" in effect, even if it never reorders a *hit* that already
  existed.
- **The relaxation is not classification-local (Major, M2).** Relaxing the knockout produces more
  EXPOSE_PURE aliases, which feed the Item 6 aggregation walker's alias map
  (`graph_builder.py:264-277`, consumed by `_build_aggregation_module` at `:1172+`). And both alias
  resolvers (`computed_attribute_extractor.py:260-264` and `graph_builder._resolve_expose_pure`
  `:776-780`) assume **exactly one** non-instance ref, assigning `output_name = ref.name` in a loop
  that silently overwrites. Today the knockout guarantees that (no sibling survives into
  EXPOSE_PURE). The multi-hop shape the design wants carries a local part-usage segment that
  bucket 2b tags as a `sibling_ref` (`:80`) — so the relaxed path can carry two non-instance refs,
  and the loop picks whichever iterates last. The design's blast-radius claim that "classification
  stays in `computed_attribute_extractor`" (design.md:121-124) understates this downstream reach.

### 7. Bets & Decisions Integrity
**Assessment:** Concerns

The stated bets are honest in form (each has an "if false"). Verification results:

- **B1 — confirmed true.** Both pins traced to single-instance, def-literal-fed producers. Solid.
  This is the design's best-supported bet and the reason the split is worth taking.
- **B2 — shakier than stated.** B2 says the discriminator is "structural — pure chain, no
  arithmetic, terminal is a calc output." Verified: the *only* arithmetic test in the code is the
  root-node `is_instance(expression_ast, "FeatureChainExpression")` check (`:104-106`) — a proxy
  that rules out *top-level* arithmetic, not a scan of the tree, and it is only consulted *after*
  the knockout. And "terminal is a calc output" is the undecidable part (C2). B2 reads as more
  proven than it is.
- **B3 — confirmed true.** INV-2 per-instance shallow copy is in the code (`usage_extractor.py:399`).
- **B4 — confirmed plausible.** The per-instance-path machinery matches.
- **Hidden bet (surface this):** *"The #2 discriminator is implementable at the
  `_classify_attribute_expression` leaf."* The design never states this and it is the load-bearing
  belief under D2 and #2. Verification says it is false without new input plumbing (C2). This is
  the most expensive unstated assumption in the design.
- **Hidden bet #2 (surface this):** *"Both committed pins have the same chain shape, so one
  discriminator flips both."* Stated as fact, false in source (C1).

Decisions are well-argued with named rejected alternatives. D2 is the right call *if* C2 is
resolved. D3's rejection reasoning is sound but collides with M3 (see below).

### 8. Reader Comprehension
**Assessment:** Pass

The core concept ("two reasons a cross-part reference fails, cleanly separable") is a strong mental
model, stated plainly before mechanism. The "reason one / reason two" frame is genuinely
clarifying and the split falls out of it naturally. The cross-map inherited from the spec earns
its place. One comprehension cost, not blocking: the "one seam" language (design.md:40,45) actively
misleads the reader about stage (b)'s size (M4) — that's a correctness-of-claim issue more than a
voice one.

---

## Issues by Severity

### Critical (must address before implementation)

- **C1 — The two committed pins are not the same chain shape; the #2 discriminator as specified
  flips one, not both.** ife_plant terminates at a calc output (`subsystems.sysml:12`); catf_mfe
  terminates at an EXPOSE-alias attribute `tf_coil.volume` (`radial_build.sysml:582` + `:458`).
  SC-1 requires both. Either the discriminator must also chase EXPOSE-alias terminals (more work,
  even less decidable at the leaf) and the N-segment key must resolve transitively through the
  intermediate alias, or the design must re-derive how catf_mfe flips. The design's Research
  Findings and the spec cross-map both need the catf_mfe shape corrected. *Dimension 1, 7.*

- **C2 — #2's "terminal is a calc output" discriminator is not decidable at the classifier leaf.**
  `_classify_attribute_expression` has instance names, not calc-def output sets, and its docstring
  bars it from resolving them (`computed_attribute_extractor.py:7-8`). Faithful implementation needs
  a new input (calc-def outputs plumbed into a leaf) or a weaker proxy that reopens INV-D. Decide
  which, and re-scope #2 accordingly — it is not obviously "three additive edits." *Dimension 3, 7.*

- **C3 — The #1 consumer-scoped lookup key can silently cross-wire.**
  `f"{consumer_scope}.{source_path}"` with both sides dotted is ambiguous, shares the flat `_alias`
  dict with same-shaped registered part-def-expose keys, and passes the `_is_self_reference` guard
  on a false hit. INV-B does not cover lookup keys. Make the scope boundary unambiguous (reserved
  separator, or a segment-count/scope tag), or prove `source_path` is never dotted when
  `consumer_scope` is multi-segment. *Dimension 5, 6.*

### Major (should address)

- **M1 — catf_mfe reclassification churn beyond the pin is unenumerated.** Relaxing the knockout
  reclassifies all multi-hop exposes on catf_mfe (`blanket_volume_total`, `magnet_surface_area`,
  `first_wall_area`, ...), some unconsumed — a baseline diff larger than "the pin flips." Enumerate
  at plan so the capture diff is attributable. *Dimension 1.*

- **M2 — The relaxation reaches past classification into the Item 6 aggregation walker and a
  single-ref assumption.** More EXPOSE_PURE aliases feed `_build_aggregation_module`'s alias map
  (`graph_builder.py:264-277,1172+`), and the alias resolvers assume exactly one non-instance ref
  (`:260-264`, `:776-780`) — an assumption the multi-hop shape can break. State this interaction in
  the blast radius and add a guard/assertion. *Dimension 6.*

- **M3 — The companion fixture folds three distinct mechanisms into one model, contradicting D3's
  own attribution argument.** D3 rejects extending ife_plant because it would "compound two stages
  in one fixture / can't attribute the diff" (design.md:159-167) — then folds gamma→lcoe (SC-2,
  specialization-chain resolution), sibling disambiguation (SC-3, two same-type instances), and
  mechanism-D positive rescue (SC-4, self-named rewrite) into "one purpose-built model"
  (design.md:167). These are three different shapes exercising three different code paths. If a
  single model carries all three, a baseline diff can't be attributed to one mechanism — the exact
  problem D3 used to reject ife_plant, and the exact reason Item 8 uses one fixture per novel
  mechanism (which D3 cites approvingly). Either show the companion's shape and prove the three are
  separately assertable, or split into per-mechanism fixtures. *Dimension 2, 7.*

- **M4 — Stage (b) is a new precedence resolver, not "one seam."** Verified: no new *extraction*
  (values are in `hierarchy_data.redefinitions`). But the rewrite needs a **second index** over
  `redefinitions` keyed by specializing-def QN (the reused Item 9 index is `design_overrides`-only,
  `pipeline_builder.py:202-216`), a **type-selection** step to pick which specializing def applies
  per virtual instance (`usage_type_map` is threaded but not consumed by the rewrite today), the
  **three-tier merge**, and **two** extended branches (CHAIN + bare-name). "One seam" (design.md:40,
  45) understates this. The split's escalation guard (design.md:47-49) — "if stage (b) exceeds a
  single implement pass, re-scope to its own item" — is being evaluated against the wrong size.
  Restate stage (b)'s scope honestly, then re-check the guard. *Dimension 8.*

### Minor (consider addressing)

- **m1 — No recorded fallback if the B1 probe fails.** The design gates stage-(a) pin flips on
  probe (1) and calls it "de-risk first" (design.md:333), but Potential Risks only covers the mild
  "#1 turns out load-bearing" case. It records no path for "the probe shows a pin is reason-two /
  the discriminator doesn't reach it." My trace says B1 holds, so the risk is low — but given it's
  the load-bearing bet, state the fallback (that pin moves to stage (b); split headline revised)
  rather than hoping. Fold in the C1/C2 probe outcomes too. *Dimension 6.*

- **m2 — Two stale cross-references, harmless but worth a note.** Item 9's design text describes the
  INV-2 copy as `list(template.bindings)` (shared objects); the code is `[copy.copy(b) ...]`
  (per-object). And catf_mfe's chain is documented as `tf_coil.volume_calc.volume` in the design
  when the source is `tf_coil.volume`. Neither breaks the design; both mislead a reader tracing it.

- **m3 — Census and MODELING_GUIDE list: Pass.** REQ allocation (BT-11, CA-10, CA-03-revised,
  VBR-10, HR-09 released) matches the spec census and resolves spec-review L1-3. The agentic-mbse
  content list (supported shapes + precedence rule + self-named FAIL check + negative fixture) is
  complete for an Item-12 handoff. No action.

---

## Recommendations

1. **Fix C1 first — it's cheap to check and it moves the headline.** Re-trace catf_mfe's actual
   chain, correct the design's Research Findings and the spec cross-map, and decide explicitly how
   catf_mfe's EXPOSE-alias terminal flips in stage (a). This likely forces the #2 discriminator to
   handle transitive alias terminals, which feeds directly into C2.

2. **Resolve C2 before committing to "#2 = three additive edits."** Decide: plumb calc-def output
   sets into the classifier (new input, honest scope increase), or accept a structural proxy and
   re-characterize INV-D's guarantee against it. This is the design's weakest joint; settle it now,
   not at implement.

3. **Redesign the #1 key to be unambiguous (C3).** A reserved separator or an explicit
   (scope, path) structured key, not two dotted strings joined by a dot. This is the epic's own
   failure mode on the stage-(a) path.

4. **Re-scope stage (b) honestly (M4) and re-run the escalation guard.** "One function, new
   precedence resolver (index + type-select + merge) + two branches" is the accurate description.
   The good news (no new extraction) survives; the "one seam" framing does not.

5. **Decide the companion fixture's shape (M3) — one model with three separately-assertable
   mechanisms, or three fixtures.** Show it, don't assert it.

6. **Enumerate catf_mfe's reclassification churn (M1) and the aggregation-walker interaction (M2)
   at plan**, so the stage-(a) capture diff is attributable rather than surprising.

---

## Resolutions

**C1 — ACCEPTED, fixed.** The design now states the two pins as *different* shapes:
ife_plant terminates at a calc output (`subsystems.sysml:12`), catf_mfe at an EXPOSE-alias
attribute `tf_coil.volume` (`radial_build.sysml:582` + `:458`). The unifying mechanism is a
**transitive N-segment walk** that follows an alias terminal one more hop to a channel, so it
flips both. Design: Research Findings (two-pin block), Core Concept, B6, D2/D6 confirm pass,
Architecture, Validation. The spec cross-map correction is flagged as a spec follow-up (design
records the true shape; the reviewer does not edit the spec).

**C2 — ACCEPTED, chose mechanism (ii).** The discriminator moves off the leaf. D6: the leaf tags
`EXPOSE_CHAIN_TENTATIVE` (structural only, INV-E), a **confirm pass** at `build_output_registry`
time (Step 5.5, where the registry exists) runs the transitive walk and finalizes to EXPOSE or
reverts to FORMULA (INV-D — no silent change). Tentative-state representation: a distinct enum
value no downstream consumer reads; the confirm pass rewrites `ca.classification` before Step 6/7,
and the graph builder + aggregation walker fail-fast if a tentative survives (INV-F). Rejected
mechanism (i) (plumb calc-def outputs into the leaf) — barred by the leaf's boundary and still
undecidable for catf_mfe's alias terminal (B5, surfaced as a hidden bet).

**C3 — ACCEPTED, fixed.** D7: the #1 consumer-scoped key is a structured
`ConsumerScopedKey = NewType(tuple[str, str])` in a dedicated `_consumer_scoped` registry
namespace, not a dotted string in the shared `_alias` dict — so the `a.b.c` ⇄ `a.b`-exposes-`c`
collapse cannot occur. `_is_self_reference` re-derived for the new step. INV-B extended to cover
**lookup** keys, not just registration.

**M1 — ACCEPTED.** Potential Risks now names the catf_mfe multi-hop re-tag set
(`blanket_volume_total`, `magnet_volume_total`, ...) as churn beyond the pin, with an
**expected-churn table enumerated at plan** and a probe (Handoff probe 3). Noted that
`first_wall_area`/`magnet_surface_area` are single-hop (sibling calc) and unaffected.

**M2 — ACCEPTED.** INV-E makes the single-non-instance-ref assumption an explicit invariant with a
guard (multi-ref chains stay FORMULA); the aggregation-walker reach
(`graph_builder.py:264-277,1172+`) is stated in blast radius and Potential Risks, with an
assertion + aggregation-fixture regression.

**M3 — ACCEPTED.** D8: split into three per-mechanism fixtures — `spec_chain_channel` (SC-2),
`sibling_channel_ambiguity` (SC-3), `self_named_rescue` (SC-4) — honoring D3's own attribution
argument and the Item 8 one-mechanism-per-fixture pattern.

**M4 — ACCEPTED.** Stage (b) restated as a precedence resolver (second `redefinitions` index by
specializing-def QN + `usage_type_map` type-select + three-tier merge + two branches) in the
split-decision blast radius, Component Overview, and Implementation Notes. The escalation guard is
recalibrated: **exceeds a single day at implement → STOP and report for a split-out ruling.**

**m1 — ACCEPTED.** Handoff now records the B1-fail fallback (a reason-two pin moves to stage (b);
split headline revised) and folds the C1/C2 probe outcomes into the probe list.

**m2 — ACCEPTED.** Stale refs corrected: INV-C states the code is `[copy.copy(b) ...]` (per-object);
Research Findings states catf_mfe's chain as `tf_coil.volume` (not `tf_coil.volume_calc.volume`).

**m3 — No action (Pass).** Census and MODELING_GUIDE list unchanged.

---

## Targeted Verification Round 2 (the three reshaped mechanisms)

The rework closed all seven round-1 findings *in concept* — the tentative/confirm split is the
right shape for C2, the tuple key is the right shape for C3, three fixtures is right for M3. But a
code-grounded trace of each reshaped mechanism against the actual data it will run on found three
new load-bearing gaps, all of the same class the epic exists to kill (silent mis-wire / silent
drop). **This does not approve.** The concepts are sound; the specifications are not yet airtight.

### What now holds (verified airtight)

- **Alias-terminal hop (C1's catf_mfe half).** Following an EXPOSE alias to its channel is exactly
  **one** dict lookup and cannot recurse: `register_alias` refuses any target not already a
  registered canonical channel (`output_registry.py:105-112`), and Phase 3 resolves the terminal
  channel *at registration time* (`output_registry_builder.py:180-184`). A cycle is impossible by
  construction (aliases point at channels, never other aliases) — the design needs no cycle guard
  *for the walk as specified*. Good.
- **FORMULA gate.** A genuine arithmetic-over-chain formula has an OperatorExpression root, so it
  fails the `is_instance(..., "FeatureChainExpression")` check (`computed_attribute_extractor.py:104-106`)
  and is never tagged tentative. B2's front gate is real.
- **C3 tuple key.** `("a","b.c")` and `("a.b","c")` hash distinct; the design stores the *unjoined*
  tuple (design.md:219,379); a dedicated `_consumer_scoped` dict cannot collide with `_alias`
  strings. The collapse the review found is closed.
- **`_is_self_reference`.** Already channel-based and key-shape-independent
  (`dependency_backtracker.py:635-644`) — the new step can reuse it unchanged. D7 slightly
  overstates the "re-derive" work; no real change needed.
- **Snapshot boundary (C2 replay hypothesis, benign).** Capture runs the *full* pipeline including
  the Step-5.5 confirm before serializing (`snapshot/capture.py:42-55`), and the confirm mutates
  `ca.classification` in place, so a correctly-built confirm pass leaves no tentative to serialize.
  Adding the enum value deserializes fine on old snapshots (value-lookup, additive). The
  hypothesized "snapshots contain live tentatives" break does **not** occur — *provided* the
  confirm pass mutates the shared objects in place (design states this; nothing enforces it).

### Critical (new — must address before implementation)

- **C4 — The confirm walk's input segments do not exist in the data it reads, and under the
  design's own leaf-tag rule the ife_plant pin is never tagged.** This is the sharpest finding.
  Extraction truncates the cross-part chain to its **root waypoint only**: the committed
  `tests/fixtures/ife_plant/extraction_snapshot.json:1536-1556` shows `magnet_volume_total`'s
  `references` is `[tf_coil]` — `volume_calc` and `volume` are gone, and `expression_text` collapsed
  to `"tf_coil"`. So:
  - The design says the confirm pass "generalizes `_resolve_expose_pure`" (design.md:281,335),
    which loops over `ca.references` (`graph_builder.py:776-780`). Over `[tf_coil]` there is nothing
    to walk — the middle and terminal segments are absent. "Generalize `_resolve_expose_pure`"
    cannot recover them; only re-parsing `expression_ast` can. The design conflates the two
    (Implementation Notes #2 says both), and they are different mechanisms.
  - Worse, the design's leaf-tag condition (design.md:209,364-367) is "exactly one non-instance
    ref remains after removing part-typed waypoints." For the real pin, removing `tf_coil` leaves
    **zero** refs, not one — so the pin **fails the tag condition and stays FORMULA**. As specified,
    stage (a) flips *neither* the ife_plant pin nor (by the same truncation) catf_mfe. This directly
    breaks B1/B6/SC-1 ("stage (a) flips both committed pins").
  - The only viable input is `expression_ast` — but on the **snapshot-replay path** the loader
    nullifies it (`expression_ast=None`, `loader.py:474`; confirm re-runs in `graph_rebuild.py:39-46`
    with no AST). The design claims stage (a)'s gate is "license-free offline snapshots"
    (design.md:416,436). If the offline gate replays AST-less snapshots and the walk needs the AST,
    the license-free-offline claim is contradicted. **Resolve which input the walk reads, re-derive
    the leaf-tag/INV-E conditions against AST segments, and confirm the offline gate has the AST it
    needs.** Design Open Question 2 flags "probe the walk on both pin shapes" — the trace shows that
    probe *fails* against the references-based spec and forces this re-design, so it is a design
    gap, not a probe-to-confirm. *Dimension 1, 3, 5, 7.*

- **C5 — Nothing populates `_consumer_scoped`; the #1 step is inert as specified.** Every mention
  of `_consumer_scoped` describes the **lookup** side (design.md:288-290,341-343,379-382); none
  describes a registration. #4 registers its part-def exposes into `_alias`, not `_consumer_scoped`
  (design.md:285-287, Phase-3 `register_alias`). So #1 reads a namespace nothing writes — it always
  misses. The load-bearing unwritten piece is the **registration method and its key derivation**:
  a consumer-scoped key is built at *registration* time (before any consumer exists) yet must match
  a lookup key `(consumer_scope, source_path)` built from the *consumer* — a non-trivial mapping the
  design never states, and exactly where a mis-key could re-introduce a wrong-channel hit with
  nothing to review. Inertness would not be caught by any stage-(a) gate (D4 rides #1's test on
  stage (b); Open Question 1 still asks whether #1 is even load-bearing). **Specify what registers
  into `_consumer_scoped`, when, and how its key is derived.** *Dimension 5, 6.*

- **C6 — INV-F's fail-fast does not exist, and the tentative/confirm split introduces a concrete
  false-entry-point regression.** Two parts:
  - **Fail-fast is fiction.** Every downstream reader of `.classification` is a silent `if`/`elif`
    with no `else`: `output_registry_builder.py:120`, `graph_builder.py:253`, `:274`, `:834-862`.
    A surviving `EXPOSE_CHAIN_TENTATIVE` is silently *skipped* (no module, no alias, no resolution
    entry) — the attribute vanishes from the graph rather than tripping an assert. INV-F's "graph
    builder + aggregation walker assert none survives" describes code that is not present. The
    asserts must be *added* at those sites; until then INV-F is aspirational.
  - **Removal-ordering regression (concrete new bug).** `_remove_formula_from_design_attrs` runs at
    Step 4.5 *before* confirm and removes only `== FORMULA` (`pipeline_builder.py:69,133`), and it
    runs exactly once. A tentative escapes removal at 4.5; if the confirm pass **reverts it to
    FORMULA** at 5.5, removal has already run — so the reverted attribute **stays in `design_attrs`
    and surfaces as a false JSON entry point.** This breaks the design's own claim that reverting to
    FORMULA is "today's exact behavior, no silent change" (design.md:141): the *classification*
    reverts, but the *side effect* FORMULA used to have (design-attr removal) does not. Move/repeat
    the removal after confirm, or have the revert re-trigger it. *Dimension 6.*

### Major (new)

- **M5 — The Phase-4 "transitive-default precedent" the confirm pass claims to mirror does not
  exist.** Phase 4 (`output_registry_builder.py:200-214`) is a **single dotted key** tried against
  three registries, then one alias registered — no hop-by-hop walk, no N-segment path assembly.
  "Transitive" there means only "the value is a dotted string" (`is_transitive_default`), not a
  transitive algorithm. The genuine recursive analog is `_resolve_aggregation_input_channel`
  (`graph_builder.py:1043-1079`), which follows `source_path` recursively and *therefore* carries an
  explicit `_visited` cycle guard. If the confirm walk is built to chase `:>>` chains the way that
  function does, it will need that guard — which the design does not specify. The "we already do
  this in Phase 4" reassurance is unfounded; cite the real analog and its cycle guard. *Dimension 2, 7.*

- **M6 — Snapshot format version and the in-place-mutation assumption.** If this item bumps
  `SNAPSHOT_FORMAT_VERSION` (`snapshot/__init__.py`), all 18 committed `extraction_snapshot.json`
  fixtures fail the load gate (`loader.py:81-92`) and must be recaptured — a license-gated,
  window-bound task (expires 2026-08-06). And the "no tentative is ever serialized" guarantee rests
  on the confirm pass mutating the *shared* `computed_attrs` objects in place; if an implementer
  rebuilds from copies, `ctx.computed_attributes` keeps the tentatives and the serializer writes
  them with no validation. State both as implement constraints. *Dimension 5.*

### Round-2 verdict

The three reshaped mechanisms are the right *concepts* but not yet safe *specifications*. C4 is the
most serious: as written, the headline (stage (a) flips both pins) is not just unproven but
contradicted by the committed extraction snapshot — the pin never gets tagged, and the walk has no
segments to follow. C5 makes #1 inert. C6 turns "revert to FORMULA is a no-op" into a false-entry
regression and shows INV-F's guards are not in the code. None is fatal to the approach; each needs a
concrete re-spec against the actual extraction/registry/orchestration behavior before plan. The
probes the design already lists (Open Questions 1-2) will *surface* C4 and C5 — but as re-design
triggers, not confirmations, so they belong resolved in the design, not deferred to implement.

---

## Round-2 Resolutions

**C4 — ACCEPTED, fixed (D9 + revised D6, INV-E).** Confirmed the truncation in the committed
snapshot (`references: [tf_coil]`, `expression_text: "tf_coil"`, `expression_ast: null`) and that
the replay path nullifies the AST (`loader.py:474`; serializer `_AST_FIELDS`). Fix per the ruling:
extraction captures an **additive `reference_chain: list[str]`** (`ComputedAttributeData` dataclass
default block, `data_models.py:214-217`), populated by the segment-list analog of
`extract_feature_chain_name` (`expression_utils.py:250-280` already walks the full chain via
`.operands[0]` + `.target_feature.name` — **verified producible**, B7). Serializer auto-includes it;
loader adds `reference_chain=d.get(...)`; **no `SNAPSHOT_FORMAT_VERSION` bump** — old snapshots
degrade to FORMULA (today's behavior; SC-10 precedent). The confirm walk reads `reference_chain`,
**not** `references` (truncated) or the AST (None) — the round-1 "generalize `_resolve_expose_pure`
over `references`" conflation is removed. The leaf-tag/INV-E condition is re-derived on
`reference_chain` (≥ 2 segments + single terminal leaf), replacing the "one ref after removing
waypoints" rule that gave **zero** for the real pin. The *why-it-truncates* question
(agentic-mbse internal, unreadable) is the first probe (B7 doesn't depend on it — D9 uses the
in-repo walker). Design: D9, D6, INV-E, B7, blast radius, Handoff.

**C5 — ACCEPTED, fixed (revised D7, D4).** Both sides written and shown to meet by construction.
`_scoped_alias` (renamed from `_consumer_scoped`) is a tuple-keyed `ScopedAliasKey = (prefix, leaf)`
namespace. **Registration:** #4's per-instance part-def-expose expansion writes `(instance_path,
exposed_leaf)` at Phase 3 (wi014_toy → `("demo_plant","total_cost")`). **Lookup:** #1 splits the
consumer's `source_path` at the last dot → `(prefix, leaf)`. They meet because both split the same
model dotted reference identically. This makes #1 **load-bearing in stage (a)** (for #4's part-def
exposes / SC-5 shape-A), while the two V11 pins resolve via #2 + the unscoped Step 2 — answering
Open Question 1. **Inertness gate** added: a stage-(a) test fails if `_scoped_alias` is empty after
registering wi014_toy. Design: D7, D4, INV-B, Validation.

**C6 — ACCEPTED, both parts fixed (INV-F real, INV-G order).** (a) The four silent readers
(`output_registry_builder.py:120`, `graph_builder.py:253/274/834`) get an explicit `else: raise` on
a surviving `EXPOSE_CHAIN_TENTATIVE` — stated as required stage-(a) edits, with a fail-fast test;
INV-F is no longer aspirational. (b) Removal ordering fixed with a stated phase order (INV-G):
confirm runs as **Phase 3b** (after single-hop aliases, before Phase 4); `_remove_formula_from_design_attrs`
runs a **second time at Step 5.6** so a reverted tentative is removed (no false JSON entry point);
`group_deriver` moves to Step 5.7 to consume final `design_attrs`. Evidence for the order: confirm
needs the registry channels (so it can't precede Phase 1/3), and Phase 4 / group_deriver must see
final classifications (so they follow confirm). Design: INV-G, Architecture phase diagram, D6,
Validation (no-false-EP test).

**M5 — ACCEPTED.** Corrected the precedent: the confirm walk carries a `_visited` cycle guard
modeled on `_resolve_aggregation_input_channel` (`graph_builder.py:1043-1050`), the real recursive
analog — not the Phase-4 transitive-default (a single dotted lookup, no walk). Design: D6, confirm-pass
Implementation Note, Component Overview.

**M6 — ACCEPTED.** No version bump (D9). Recapture set enumerated: **catf_mfe, ife_plant, and the
three stage-(b) fixtures** (the multi-hop-EXPOSE carriers); the ~15 others load unchanged. The
"no tentative serialized" guarantee is stated to depend on the confirm pass mutating the **shared**
`computed_attrs` in place — an implement constraint. Design: Potential Risks (M6 bullet), D9.

---

**Overall:** Revise (round 1 findings resolved; round 2 opened C4/C5/C6 + M5/M6 — **not Approve**)
**Next Steps:** Address C4, C5, C6 in the design before plan — they are the same silent-mis-wire /
silent-drop class the epic targets, now inside the *fixes* for the round-1 findings. Specifically:
(C4) re-specify the confirm walk's input (AST vs `references`), re-derive the leaf-tag/INV-E
conditions against AST segments, and confirm the license-free offline gate has that input; (C5)
specify the `_consumer_scoped` registration path and key derivation; (C6) add INV-F's asserts for
real and fix the Step-4.5-vs-confirm removal ordering. Then re-run `/_my_design` and point it back
at this review. The reviewer does not edit the design.
