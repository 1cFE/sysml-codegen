# Design Review: Resolved Multi-Hop Chain Bindings

**Design:** `.project/active/multihop-chain/design.md`
**Spec:** `.project/active/multihop-chain/spec.md`
**Review File:** `.project/active/multihop-chain/design-review.md`
**Date:** 2026-07-07

---

## Fundamental Assessment

**Sound.** The core insight is right and I verified it against the code: the scoped registry
already keys every calc output by its full design-prefix-stripped instance path, so a deep chain
needs the correct scope prefix on one `scoped_lookup`, not a per-hop containment walker. The design
is two small additive changes (stop rejecting at extraction; add a gated ancestor-scope climb to the
CHAIN dispatch) plus a forced relocation of the loud diagnostic. No new abstraction is introduced,
the reuse-vs-build calls are justified, and every Key Bet checks out against the registry build and
the backtracker dispatch. This is the minimal design that satisfies the spec.

It is not a clean **Approve**, because the design's own riskiest bet (B2) is mitigated by a claim
that is technically incomplete, and the loud-diagnostic relocation needs one more guarantee pinned
to genuinely preserve the Item-5 contract. Both are refinements to design text and test obligations,
not a reframe. Verdict: **Revise (light)** — the approach is approved; fix B2's honesty/guard and the
WARN-loudness pin, and annotate the spec for the deviation.

---

## Verification of the seven core moves

Each move in the review brief, checked against code.

**1. No-hop-walker claim — VERIFIED.** `make_scoped_key` (`identifier_types.py:62-63`) splits the
usage EQN on `__`, drops `segments[0]` (design prefix), joins the rest with `.`, appends
`.{attr}`. Phase 1a registers every calc-usage output under exactly this key
(`output_registry_builder.py:180-184`). So `derived_calc`'s output registers as
`measurement_system.station.array.derived_calc.derived_value`, and `scoped_lookup` is an exact dict
match (`output_registry.py:186-188`). A deep chain needs the right prefix, not a walker. Correct.

**2. Both derivations — VERIFIED.** `_consumer_scope_dotted` = `segments[1:-1]` of the usage QN
(`dependency_backtracker.py:457-460`).
- `base_metric` (on `derived_calc`): consumer scope `measurement_system.station.array`. Step-1 key
  `measurement_system.station.array.sensor.core.metric_value` — this is exactly `core`'s registered
  key, so it is a **direct Step-1 hit with no climb**. The design's claim that base_metric wires
  from the extraction change alone is correct; `sensor` is a sibling of `derived_calc` under
  `array`, so the consumer-scope prefix is already right.
- `data_point` (on `chain_analysis`): consumer scope `measurement_system.analyzer`. Step-1 key
  `measurement_system.analyzer.station.array.derived_calc.derived_value` — miss (`station` is a
  sibling of `analyzer`). The registered key is `measurement_system.station.array…`, i.e. the
  consumer scope with its last segment dropped. One-level climb. Correct.

**3. Climb false-positive risk — PARTIALLY protected; see M-1.** Within a single prefix,
`scoped_lookup` is an exact dict match, so there is no intra-level ambiguity. Across prefix levels,
longest-first gives innermost-wins, which is the right rule *for the common case*. But longest-first
does **not** close the first-segment-shadowing case, and the design claims it does. Details in M-1.
One structural fact the design should state, because it strengthens B3: the flat `alias_lookup`
(Step 2) is keyed `instance_name.attr` — always exactly one dot (`output_registry_builder.py:186`).
A gated chain has ≥2 dots, so it can **never** hit Step 2. Placing CLIMB after Step 2 is therefore
safe, and B3 ("resolves only through `scoped_lookup`") is guaranteed by key shape, not just by
convention. Say this.

**4. D4 additive gate — VERIFIED.** `_parse_chain_expression` builds `source_path` from at most two
parts — first operand name + target-feature name (`usage_extractor.py:811-829`) — so every CHAIN
reaching the dispatch today has ≤1 dot. 3+-segment chains are rejected to `UNBOUND` with
`source_path=None` (`usage_extractor.py:724-739`). So no CHAIN with `count(".") >= 2` reaches the
backtracker today; the gate is genuinely additive and every existing resolution is byte-identical.
Correct.

**5. D2 (don't reuse the attribute confirm walk) — SOUND.** `_resolve_reference_chain`
(`output_registry_builder.py:38-88`) walks with a **fixed** `instance_prefix` and recurses only to
substitute an alias-terminal's own `reference_chain`. It never shortens the prefix — it cannot
climb scopes — so it structurally cannot resolve `data_point` (which needs the climb). And it runs
in the registry-build phase over `ComputedAttributeData`, pulling the attribute baselines into scope
for no benefit. Rejecting reuse is justified on both counts.

**6. The flagged deviation (loud diagnostic moves to backtracker Step-4) — APPROVED, with one
condition (M-2).** The forced-move argument is **correct**: `build_output_registry` is called only
in `pipeline_builder.py:780` and `graph_rebuild.py:40` — assembly and snapshot rebuild, never
extraction. Extraction can count segments but cannot know whether a chain resolves, because the
registry it would query does not yet exist. The spec's "narrow the reject site" phrasing assumed a
seam (extraction can tell resolvable from unresolvable) that does not hold. Moving the diagnostic to
where the registry lookup actually fails (Step-4 fallback) is the only faithful location.

Substance preserved at the new home, checked against `_resolve_binding_via_registry`
(`dependency_backtracker.py:569-587`):
- **Entry point** ✓ — `fallback_qn = f"{usage.qualified_name}__{param_name}"`, added to
  `_fallback_entry_points`.
- **Never truncated** ✓ — `fallback_qn` is the full usage QN + param, never the root segment.
- **Loud** — *conditionally.* The current Step-4 line is deliberately `logger.debug` and its own
  comment calls it "the primary benign noise" (`:569-576`). Emitting a WARNING here for the
  3+-segment branch preserves loudness **only if** it is a genuine, distinct WARNING (not folded
  into the benign DEBUG/reconciliation stream). This is the M-2 condition.

Approve the deviation. Require the spec's HARD Item-5 requirement (spec `:123-126`) be annotated:
the reject site is not narrowed at extraction — the loud+entry-point+never-truncated contract moves
to the backtracker Step-4 fallback, for the hard technical reason that no registry exists at
extraction time.

**7. D5 (fires-on-shape as a synthetic backtracker unit test) — SATISFIES R1, with one pin
(M-2).** Feeding a synthetic 3+-dot CHAIN `BindingInfo` whose tail names a non-existent output into
`_resolve_binding_via_registry`, with a registry lacking the key, drives the exact Step-4 path: all
dispatch steps miss, fallback fires. The input is constructed independently of the resolution code
(independent anchoring). Silent-on-clean is the two corpus chains resolving with no WARN. This is
faithful and cheaper than a captured dangling-chain fixture. The one addition: the assertion must
pin **WARNING level** and that the returned QN is the **full untruncated** `usage_qn__param` — so
the test locks the "loud + never-truncated" substance, not merely "an entry point came back."

---

## Dimensional Review

### 1. Spec Compliance
**Assessment:** Concerns
Every spec success criterion maps to a design element: both wires (INV-1), the loud tail (INV-2),
parity (INV-3), path-scoped byte-identity (INV-4), the three-part re-capture (INV-5). The two HARD
requirements the spec-review added — pin both wires, and a fires-on-shape substrate — are both
honored (base_metric gets its own channel-identity pin; D5 is the substrate). The single deviation
from spec's literal wording (reject-site location) is called out, argued, and — per this review —
approvable. The only compliance gap is procedural: the spec's HARD Item-5 text still says "narrowed,
not deleted" at extraction, and must be annotated to match the approved deviation (M-2).

### 2. Pattern Consistency
**Assessment:** Pass
The climb is a new ordered step inside the existing `_resolve_chain_dispatch` ladder, using the same
`scoped_lookup` + `_is_self_reference` guard the other steps use. It mirrors the consumer-scope
prepend already in Step 1 and Step 1c. No new pattern is invented. The design correctly declines to
reuse `_resolve_reference_chain` (D2) precisely because that would be the *wrong* pattern (fixed
prefix, no climb).

### 3. Abstraction Quality
**Assessment:** Pass
No new class or module. The change is a loop over ancestor prefixes and a WARN branch — the right
altitude for the problem. The design resists the tempting-but-wrong abstraction (a shared
segment-resolution walk across the calc-usage and attribute paths) with a concrete reason
(byte-identity scope + it can't climb).

### 4. Duplication Avoidance
**Assessment:** Pass
The climb reuses the existing `scoped_lookup` and self-reference guard rather than duplicating
resolution logic. It does re-prepend consumer-scope-derived prefixes (as Step 1 and 1c do), but
that is the same operation at different prefix lengths, not parallel structure that will drift.

### 5. Data Structure Clarity
**Assessment:** Concerns
The deep-chain CHAIN `BindingInfo` built at extraction will carry `source_path` (the full dotted
path) but **not** `source_instance_elem` / `source_attribute_elem` / `is_cross_file`, which the
2-segment `_parse_chain_expression` path sets. I verified the backtracker uses none of those three
fields, so this is safe for resolution — but the design should state it explicitly (a one-line note
that the deep-chain arm intentionally omits the element refs and that nothing downstream consumes
them for CHAIN bindings), so a plan-stage implementer does not reintroduce `_parse_chain_expression`
to "fill them in." See N-1.

### 6. Route Safety
**Assessment:** Concerns
The climb is a new resolution route. It is gated (`count(".") >= 2`), ordered after the existing
ladder (additive), and guarded against self-reference. The residual route-safety concern is the
cross-scope shadowing case in M-1: longest-first is not a complete uniqueness guarantee, and a
future 3+ chain could take the climb route to the wrong same-named channel silently. Safe for the
two corpus chains (pins verify); latent for the general shape.

### 7. Bets & Decisions Integrity
**Assessment:** Concerns
B1 and B3 are genuine bets, each verified true (B1 against Phase 1a; B3 guaranteed by the 1-dot
alias-key shape — the design under-claims here, it is stronger than "mitigated"). B2 is the honest,
load-bearing bet — and its stated mitigation is **incomplete**. "Longest-first ordering =
innermost-wins" closes the *outer-shadows-inner* direction but not the *inner-declares-first-segment-
but-lacks-the-full-path* direction (M-1). The bet is real and correctly identified as the riskiest;
the mitigation text just overstates its own coverage. No hidden bets surfaced — the design is candid
about the registry dependency, the parity trap, and the stale-classification flip. Decisions D1-D5
each name the rejected alternative with a concrete reason.

### 8. Reader Comprehension
**Assessment:** Pass
The Core Concept states the mental model plainly before the mechanism ("survive extraction, then try
the right scope"). The two-chains-resolve-differently split (base_metric = Step-1 hit; data_point =
climb) is the load-bearing fact and it is up front. Terms are anchored to code locations. A tired
engineer can skim this once and know what changes and why.

---

## Issues by Severity

### Critical
None. The approach is sound and the deviation is approvable.

### Major
- **M-1 — B2's mitigation is incomplete: longest-first does not close the shadowing case.**
  [Bets Integrity / Route Safety] The climb picks the innermost ancestor prefix whose **full**
  downward path is a registered key. True SysML lexical resolution binds the **first segment** in
  the nearest scope that declares it, then walks down. These differ when an inner scope declares the
  first segment but does not contain the full downward path, while an outer scope does: lexical
  resolution binds inner-then-fails (unresolvable), but the climb skips the inner miss and silently
  resolves to the outer channel — a silent mis-wire, the exact failure class this epic exists to
  kill. The two corpus chains are safe (only one prefix hits for `data_point`; the channel-identity
  pins verify both), so this does not block the item. But the design should either (a) add a cheap
  ambiguity guard — collect all prefix hits, and if more than one **distinct** channel is reachable
  across prefixes, warn-and-surface instead of silently picking longest — or (b) restate B2 honestly:
  longest-first covers the corpus; the cross-scope first-segment-shadowing shape is deferred/filed
  (consistent with Non-Goals "file, don't build for hypothetical shapes"), with a code comment naming
  the assumption. Option (b) is acceptable given the corpus is safe; what is not acceptable is
  leaving the mitigation text claiming a completeness it does not have.

- **M-2 — Pin the "loud" and "never-truncated" substance at the new Step-4 home.** [Spec
  Compliance / Route Safety] The deviation is approved, but the Item-5 contract's *loud* leg is only
  preserved if the new branch is a genuine WARNING distinct from the deliberately-DEBUG benign line
  it sits next to (`dependency_backtracker.py:569-576`). Two required actions: (1) the design must
  specify the multi-hop fallback emits a WARNING (level, not just "a message"), separate from the
  DEBUG/reconciliation digest, so it is not swallowed as benign noise; (2) the D5 fires-on-shape
  test must assert **level=WARNING** and that the returned QN is the full untruncated
  `usage_qn__param`. And annotate the spec's HARD Item-5 requirement (spec `:123-126`) to record
  that the reject moves to the backtracker rather than being narrowed at extraction, for the
  registry-timing reason.

### Minor
- **N-1 — State that the deep-chain CHAIN arm intentionally omits the element refs.** [Data
  Structure Clarity] Verified safe (backtracker consumes none of `source_instance_elem` /
  `source_attribute_elem` / `is_cross_file` for CHAIN). Add a one-line note in the D1 / Component
  section so a plan-stage implementer does not reach back for `_parse_chain_expression` to populate
  them.
- **N-2 — Strengthen the B3 claim.** [Bets Integrity] B3 is not merely "mitigated" — it is
  structurally guaranteed: flat `alias_lookup` keys are always `instance.attr` (one dot,
  `output_registry_builder.py:186`), so a ≥2-dot gated chain can never match Step 2. State this; it
  turns a soft bet into a proof and reassures the offline-parity reviewer.

---

## Recommendations

1. **M-1:** Decide guard-vs-document for the shadowing case and correct B2's mitigation text either
   way. A distinct-channel ambiguity guard is cheap and aligns with the epic's anti-silent-mis-wire
   theme; documenting the assumption is acceptable since the corpus is pinned-safe. Do not ship B2
   claiming longest-first is complete.
2. **M-2:** Specify a genuine WARNING at the Step-4 multi-hop branch and pin it (level + untruncated
   QN) in the D5 test; annotate spec `:123-126` for the approved reject-site relocation.
3. **N-2 / N-1:** Fold the two structural facts (1-dot alias-key shape guaranteeing B3; deep-chain
   arm intentionally omitting element refs) into the design text so the plan stage inherits them.
4. Everything else — the additive gate (D4), the base_metric-Step-1-vs-data_point-climb split, the
   D2 reuse rejection, the three-part re-capture, the byte-identity method — is verified and needs
   no change.

---

## Resolutions

*Filled in during Stage 4 once the user engages. One entry per resolved issue — this is what the
design agent reads to incorporate the review.*

---

**Overall:** Revise (light) — approach approved, including the reject-site deviation; address M-1
(B2 honesty/guard) and M-2 (loud + never-truncated pinned at Step-4, spec annotated) before
implement. N-1/N-2 are text-only.
**Next Steps:** Record resolutions above, then re-run `/_my_design` (or return to the design-agent
session) and point it at this review to incorporate. The reviewer does not edit the design.
