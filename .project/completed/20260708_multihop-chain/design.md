# Design: Resolved Multi-Hop Chain Bindings

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-07
**Branch:** truth-debt-epic
**Commit:** 1548734
**Epic:** TRUTH-DEBT — Item 2 (R1–R4)

## Overview

Let a calc-usage parameter bound to a 3+-segment feature chain
(`station.array.derived_calc.derived_value`) resolve to its upstream channel instead of
hard-rejecting to an unbound entry point. Two such chains exist, both in `deep_cross_scope_probe`;
both flip to wired.

## Related Artifacts

- **Spec:** `.project/active/multihop-chain/spec.md` (revised through spec-review)
- **Spec review:** `.project/active/multihop-chain/spec-review.md`
- **Epic:** `.project/backlog/epic_truth_debt.md` (Item 2; R1–R4)
- **Adjacent (Item 1, landed):** `.project/active/f4-cutover/design.md`
- **Reference:** `docs/architecture/reference/24-dual-resolution-architecture.md`,
  `03-resolution-overview.md`, `04-input-resolver.md`
- **Memory:** `multihop-expose-offline-parity`, `deep-cross-scope-stale-baseline`,
  `byte-identity-captured-at-churn`, `cross-part-binding-v11-fallthrough`, `agentic-mbse-repo-path`

## Research Findings

**The registry already encodes the answer; only the lookup key is wrong.** Every calc output is
registered in the scoped registry under its design-prefix-stripped dotted instance path
(`make_scoped_key`, `identifier_types.py:46`): `derived_calc.derived_value` →
key `measurement_system.station.array.derived_calc.derived_value` → channel
`DeepCrossScopeDesign__measurement_system__station__array__derived_calc__derived_value`. So a deep
chain does not need a per-hop part-containment walker — it needs the **right scope prefix** on a
single `scoped_lookup`. The registry did the walking at registration time.

**The two corpus chains resolve differently, and one is already free.** The backtracker's CHAIN
dispatch (`_resolve_chain_dispatch`, `dependency_backtracker.py:589`) prefixes the source_path with
the consumer's scope (`_consumer_scope_dotted`, `:450` — `segments[1:-1]` of the consumer QN):

- **`derived_calc.base_metric` = `sensor.core.metric_value`.** Consumer scope
  `measurement_system.station.array`. Step-1 key
  `measurement_system.station.array.sensor.core.metric_value` — a **direct hit** on the existing
  ladder. `sensor` is a child of `derived_calc`'s parent, so the consumer-scope prefix is already
  correct. This chain resolves with **zero backtracker change** — it only needs extraction to stop
  rejecting it.
- **`chain_analysis.data_point` = `station.array.derived_calc.derived_value`.** Consumer scope
  `measurement_system.analyzer`. Step-1 key `measurement_system.analyzer.station.array…` — **miss**:
  `station` is a *sibling* of `analyzer`, not a child. The correct key is
  `measurement_system.station.array.derived_calc.derived_value` — the consumer scope with its last
  segment dropped. This is a one-level **scope climb**.

**Resolution is post-extraction, not at the reject site.** The scoped registry does not exist at
extraction time — it is built during pipeline assembly, and CHAIN bindings resolve in the
backtracker DFS (doc 24, REQ-DRA-01). The extraction reject at `usage_extractor.py:717-739` can
count segments but cannot know whether a chain resolves. This forces where the diagnostic lives
(D3 below).

**The attribute confirm walk is a poor donor.** `_resolve_reference_chain`
(`output_registry_builder.py:38`) walks attribute EXPOSE chains, but with a **fixed** instance
prefix plus recursive alias-terminal substitution — it never climbs scopes, and it handles a
terminal that is itself an alias (catf `tf_coil.volume` → `volume_calc.volume`). The corpus
calc-usage chains need the opposite: scope climbing, and a terminal that is a **direct** calc
output (no alias indirection). Reusing it would not resolve Pattern A and would pull the attribute
baselines into scope (spec byte-identity risk). See D2.

## Core Concept

A deep calc-usage chain does not need a new resolver — it needs the binding to **survive
extraction** and the backtracker to **try the right scope**. Two small, additive changes:

1. **Extraction stops rejecting.** The 3+-segment arm at `usage_extractor.py:717` currently counts
   segments and returns UNBOUND. Replace it: emit a normal `BindingType.CHAIN` with the **full**
   dotted source_path from `extract_feature_chain_segments` (the helper already yields every
   segment). This alone wires `base_metric`, whose consumer scope already matches.

2. **The backtracker climbs, and refuses when ambiguous.** Add one step to `_resolve_chain_dispatch`:
   when the existing scoped ladder misses, retry `scoped_lookup` with progressively shorter
   ancestor-scope prefixes (drop trailing segments of `consumer_scope`). Collect **every** hit, not
   the first. If they all point at one channel, resolve to it (innermost/longest is the natural
   pick, but they agree). If two prefixes reach **different** channels, refuse — fall through to the
   loud Step-4 fallback rather than silently pick. This wires Pattern A and keeps a genuine cross-scope
   collision from resolving silently.

The insight: prefixing the whole path with the ancestor scope where the **first segment** resolves
yields exactly the registered scoped key, because the registry key is the full downward instance
path from that scope. The resolution stays a pure `scoped_lookup` against Phase-1a calc-output
registrations, so it is deterministic and identical live and offline (no dependence on the
confirm-walk re-tag).

**One honest limit (B2, M-1).** Collect-all-and-refuse closes the case where two scopes both carry
the *full* path to different channels. It does **not** close the subtler case where an inner scope
declares only the *first segment* (and lacks the rest) while an outer scope carries the full path:
that produces a single hit — the outer channel — which strict SysML lexical resolution would instead
call unresolvable (bind the inner first segment, then fail the downward walk). Distinguishing it
needs per-segment scope inspection, which no corpus model requires. That residual is a documented
assumption, not a built guard — safe for the corpus (only one prefix hits `data_point`; the pins
verify the exact channel), filed under Non-Goals "file, don't build for hypothetical shapes."

The loud diagnostic for a genuinely unresolvable chain moves **with the resolution** to the
backtracker's Step-4 fallback: a 3+-segment CHAIN that misses every step warns loudly and surfaces
as an entry point — never truncated, never silent (the Item-5 contract, in its new home).

## Key Bets

- **B1.** Every corpus calc-usage output the deep chains target is registered in the **scoped**
  registry under its full design-prefix-stripped instance path. *If false → the climb misses and
  the chain falls to an entry point; the wire never lands.* (Verified: `make_scoped_key`
  `identifier_types.py:46` drops only `segments[0]`; both targets are calc outputs registered in
  Phase 1a.)
- **B2.** For the corpus chains, ancestor-scope climbing on the scoped key produces the correct
  terminal channel: exactly one ancestor prefix yields a `scoped_lookup` hit. *If false → a chain
  reaches a wrong same-named target in another scope (a silent mis-wire).* **Coverage is partial and
  the design says so:** the collect-all-and-refuse guard closes the case of two prefixes reaching
  *different* full-path channels (loud refuse, not a silent pick). It does **not** close the
  first-segment-shadowing single-hit case (inner declares the first segment but lacks the full path;
  outer supplies it) — that is a documented, filed assumption, not built (see Core Concept / Non-Goals).
  Mitigated for the corpus: the channel-identity pins assert the exact QN, not just "resolved," and
  only one prefix hits `data_point`.
- **B3.** The two calc-usage deep chains resolve purely through `scoped_lookup`, never the
  first-wins flat `alias_lookup`. *If false → an offline snapshot bakes in a mis-wire — a lying sim,
  not a crash* (the Phase-5 failure class, memory `multihop-expose-offline-parity`). **This is
  structurally guaranteed, not merely mitigated:** flat `alias_lookup` keys are always
  `instance.attr` — exactly one dot (`output_registry_builder.py:186`) — and a gated chain has ≥2
  dots, so it can **never** match the Step-2 alias step. Placing the climb after Step 2 is therefore
  safe by key shape, and both chains resolve deterministically through `scoped_lookup`, identically
  live and offline. The parity guard confirms live == offline.

## Key Decisions

- **D1. Extraction emits the full-path CHAIN; the backtracker resolves it.** The reject arm
  (`usage_extractor.py:717`) becomes a CHAIN builder using the full segment list. *Rejected:
  resolving at extraction (no registry exists there — doc 24); truncating to a 2-segment
  representation (loses the middle hops the scoped key needs).*
- **D2. Build the walk as ancestor-scope climbing inside `_resolve_chain_dispatch`, not a shared
  walk.** The cleanest choke point for calc-usage CHAIN resolution is where CHAIN bindings already
  resolve. *Rejected: reusing `_resolve_reference_chain` (`output_registry_builder.py:38`) — it
  does not climb scopes (fixed instance prefix), so it cannot resolve Pattern A, and sharing it
  pulls the attribute baselines `station_output` / ife_plant `magnet_volume_total` into
  byte-identity scope for no benefit.*
- **D3. The loud diagnostic moves from extraction to the backtracker Step-4 fallback.** A 3+-segment
  CHAIN (`"::" not in source_path` and `source_path.count(".") >= 2`) that reaches Step 4 emits a
  genuine `logger.warning` — a distinct WARNING level, **not** folded into the deliberately-DEBUG
  benign line it sits next to (`dependency_backtracker.py:569-576`) — and surfaces as an entry point.
  The message names the full untruncated chain. *Rejected: keeping the reject at
  extraction (extraction cannot detect unresolvability without the registry — the seam the spec's
  "narrow the reject site" phrasing assumed does not hold; see Non-Goals / Risks).* **This is a
  deliberate deviation from the spec's literal "reject site is not deleted, it is narrowed" wording
  — the substance (loud + entry-point + never-truncated) is preserved; only the location moves, for
  a hard technical reason.**
- **D4. Gate the new climb step on `source_path.count(".") >= 2`.** A 2-segment chain never enters
  the climb, so every existing 2-segment resolution is byte-identical; only 3+-segment chains —
  none of which reach the backtracker today (all rejected at extraction) — get new behavior.
  *Rejected: an ungated climb (correct but widens the byte-identity surface to every CHAIN binding
  for no corpus benefit).*
- **D5. Fires-on-shape substrate is a synthetic backtracker unit test, not a fixture.** Feed a
  3+-segment CHAIN `BindingInfo` whose tail names a non-existent output into
  `_resolve_binding_via_registry` with a registry that lacks it; assert ENTRY_POINT, level=WARNING,
  and the full untruncated returned QN (M-2). *Rejected: a new dangling-chain fixture (adds a
  captured baseline + snapshot + a
  byte-identity surface for a negative case; the warning lives at the backtracker, so a unit test
  exercises the exact path faithfully).*

## Architecture

**Data flow, per calc-usage chain binding, after the change:**

```
extraction (usage_extractor.py):
  FeatureChainExpression → extract_feature_chain_segments → full dotted source_path
    → BindingInfo(CHAIN, source_path="station.array.derived_calc.derived_value")   # no reject

backtracker (_resolve_chain_dispatch):
  Step 1   scoped_lookup(consumer_scope + "." + path)         # base_metric hits here
  Step 1b  scoped_lookup(path)
  Step 1c  scoped_alias_lookup(...)
  Step 2   alias_lookup(path)
  Step CLIMB (new, gated ".">=2): collect scoped_lookup(prefix + "." + path) over
             ancestors(consumer_scope); {} → miss; {1 distinct channel} → MODULE_OUTPUT (data_point);
             {≥2 distinct channels} → refuse (fall through, no silent pick)
  → BindingResolution(MODULE_OUTPUT, channel)

  Step 4 fallback (miss): if 3+-segment chain → logger.warning + fallback_entry_points  # loud diagnostic
```

**Boundaries:**
- `extraction/usage_extractor.py` — the `FeatureChainExpression` arm builds CHAIN for any segment
  count; the `> 2` reject block is removed. No registry contact.
- `analysis/dependency_backtracker.py` — `_resolve_chain_dispatch` gains the climb step;
  `_resolve_binding_via_registry` Step-4 fallback gains the multi-hop WARN.
- Tests — `test_deep_cross_scope_probe.py` pins flip (both wires); new base_metric pin, new
  fires-on-shape unit test, new @requires_license live/offline parity test.
- Baselines — `deep_cross_scope_probe` re-captured (extraction snapshot + computation_graph); all
  others byte-identical.

## Required Invariants

- **INV-1.** Both deep chains resolve to their exact channel:
  `data_point → DeepCrossScopeDesign__measurement_system__station__array__derived_calc__derived_value`
  and `base_metric → …__station__array__sensor__core__metric_value`. Each pinned by an
  independently-anchored assertion of the full QN (not "resolved" / "left fallback").
- **INV-2.** A 3+-segment chain that resolves through no step still warns loudly (a genuine
  `logger.warning`, WARNING level, distinct from the sibling DEBUG line) and surfaces as an entry
  point — never truncated to root, never silently wired (Item-5 contract, D3 home).
- **INV-2b.** The climb never silently picks among conflicting channels: if two ancestor prefixes
  reach different channels, it refuses and falls to the loud Step-4 fallback (M-1 guard). Only a
  single distinct climb channel resolves to a wire.
- **INV-3.** The climb resolves only through `scoped_lookup`; no deep chain resolves through the
  flat `alias_lookup`. Live and offline produce identical wires for both chains.
- **INV-4.** Path-scoped byte-identity: no calc-usage-param baseline other than
  `deep_cross_scope_probe` changes. (The climb is gated to 3+-segment chains; the only such
  calc-usage chains in the corpus are the two in this fixture. The attribute path is untouched, so
  `station_output` / ife_plant baselines do not move.)
- **INV-5.** `deep_cross_scope_probe`'s re-capture is a reviewed diff decomposed into its three
  parts (§Re-capture), each line checked against a known cause before commit.

## Component Overview

- **CHAIN extraction arm (`usage_extractor.py:717`).** Replace the `len(segments) > 2` reject with a
  CHAIN build over the full segment list. The 2-segment `_parse_chain_expression` path stays; the
  3+-segment path now joins all segments into `source_path` and returns `BindingType.CHAIN`. No
  truncation, no warning here. **The deep-chain arm intentionally sets only `source_path`** — it
  omits `source_instance_elem` / `source_attribute_elem` / `is_cross_file` (N-1). The backtracker
  consumes none of those three for CHAIN resolution (only `source_path`), so this is safe; a
  plan-stage implementer must **not** reach back into `_parse_chain_expression` to populate them.
- **Scope-climb step (`_resolve_chain_dispatch`, new, gated).** After Step 2, if
  `source_path.count(".") >= 2`, iterate ancestor prefixes of `consumer_scope` (drop trailing
  segments), collect every non-self-reference `scoped_lookup(prefix + "." + source_path)` hit into a
  set of distinct channels. Empty → return None (fall through). Exactly one → resolve to it. Two or
  more → return None and let Step 4 fire the loud fallback (the M-1 ambiguity guard — refuse, never
  silently pick). Additive (INV-A): ordered after the existing ladder, only adds a hit where it fell
  through.
- **Multi-hop fallback WARN (`_resolve_binding_via_registry` Step 4).** When a fallthrough binding
  is a 3+-segment CHAIN, emit a genuine `logger.warning` (level WARNING, distinct from the sibling
  DEBUG line) naming the full untruncated chain, in addition to the fallback entry point. The
  silent-on-clean sibling: both corpus chains resolve, so no WARN fires on the corpus.
- **Pins (`test_deep_cross_scope_probe.py`).** Flip `test_pattern_a_deep_chain_falls_to_own_entry_point`
  and `_no_truncated_binding` to resolved-wire assertions; rewrite `test_offender_set_pinned`'s
  docstring (the set stays empty, but now because both are *wired*, not rejected-to-clean-EP —
  re-verify the assertion); add a `base_metric` channel-identity pin; replace the extraction-warns
  test with the fires-on-shape unit test + the live/offline parity test.
- **Fires-on-shape unit test (new).** Synthetic 3+-segment dangling CHAIN → backtracker → assert
  ENTRY_POINT, **level=WARNING**, and that the returned QN is the full untruncated `usage_qn__param`
  (D5, M-2 — the assertion locks the "loud + never-truncated" substance, not merely "an EP came
  back").
- **Live/offline parity test (new, @requires_license).** Extract + resolve the fixture live; assert
  both channel QNs equal the committed-snapshot wires.

## Non-Goals

- Pattern B (`::` 6-segment REFERENCE, `design.sysml:82`) — not a CHAIN loud-reject; already
  resolves via the REFERENCE arm. If wrong, file it.
- A literal per-hop part-containment walker. The scoped registry already keys every output by its
  full instance path; the climb + one `scoped_lookup` reaches the terminal without walking
  intermediate hops.
- The first-segment-shadowing single-hit shape (inner scope declares the chain's first segment but
  lacks the full downward path; an outer scope supplies it). No corpus model exercises it; closing
  it needs per-segment scope inspection the climb does not do. Filed, not built (B2, M-1) — a code
  comment must name the assumption at the climb site.
- Sharing a resolution walk with the attribute confirm path (D2).
- The duplicated `unbound_params` entries (`data_point`×2, `base_metric`×2) — resolving the
  bindings likely clears them; do not chase unless they survive the re-capture.
- agentic-mbse code changes (sandbox-blocked; record the shape for MODELING_GUIDE, R2).

## Implementation Notes

- **Re-capture plan (three-part diff, R3).** Re-capture `deep_cross_scope_probe` via
  `scripts/capture_*.py` only. Both `extraction_snapshot.json` and `computation_graph.json` change:
  1. `chain_analysis.data_point`: `unbound_params` loses `data_point`×2; a CHAIN binding
     (source_path `station.array.derived_calc.derived_value`) appears; the computation_graph input
     flips entry_point → module_output `…__derived_calc__derived_value`.
  2. `derived_calc.base_metric`: `unbound_params` loses `base_metric`×2; CHAIN binding
     `sensor.core.metric_value`; input flips to module_output `…__sensor__core__metric_value`.
  3. The pre-existing stale entry-point-classification flip (`entry_type`
     usage_literal→library_default, `source_calc_usage` null→Analysis_Calc/Derived_Metric — memory
     `deep-cross-scope-stale-baseline`, reproduces on `ba3bca4`). Root-cause code-correct vs
     baseline-correct before commit. It may be partly mooted once data_point/base_metric become
     wired (their EPs vanish); decompose whatever survives.
- **Byte-identity method** (memory `byte-identity-captured-at-churn`): a full re-capture rewrites
  every `captured_at`; diff, confirm only `captured_at` churned on untouched fixtures, revert those
  so only `deep_cross_scope_probe` shows.
- **Parity guard is @requires_license-gated** — skipped in license-free CI. There the
  committed-snapshot pin is the *only* always-on guard, and the snapshot is exactly where an
  offline mis-wire would be baked in. The channel-identity pins run offline; treat them as the
  primary safeguard, the live parity as confirmation.
- **Warn surfacing.** The extraction warning went to the `extract_calculation_usages` report; the
  new WARN lives at the backtracker. The fires-on-shape test asserts it via `caplog` on the
  backtracker logger (or the backtracker's warnings channel if one exists — confirm at plan).
- **Self-reference guard** already wraps each dispatch step; the climb reuses it so a chain does not
  resolve to its own consumer's output.

## Potential Risks

- **The climb newly-resolves a chain in another fixture (INV-4 churn).** *Mitigation:* the D4 gate
  (`.count(".") >= 2`) means only 3+-segment chains are affected, and none reach the backtracker
  today; the full-suite byte-identity gate catches any surprise as a diff to root-cause.
- **The spec expected the reject to stay at extraction (D3 deviation).** *Mitigation:* recorded
  prominently as a decision; the substance of the HARD Item-5 contract is preserved. Surface at
  design-review for explicit sign-off.
- **B2 wrong scope wins (silent mis-wire).** *Mitigation:* the M-1 collect-all-and-refuse guard
  turns a cross-scope collision (two prefixes, different channels) into a loud refusal, not a silent
  pick; the channel-identity pins assert exact QNs, computed independently of the code under test
  (R1). *Residual:* the first-segment-shadowing single-hit shape is filed, not built (safe for the
  corpus — only one prefix hits `data_point`).
- **The stale classification flip is code-wrong, not baseline-wrong.** *Mitigation:* root-cause
  before commit (R4 verify-then-fix); it reproduces on `ba3bca4`, so it is not caused by this item.

## Integration Strategy

The change composes with the F4 cutover landscape (Item 1): the aggregation path's
`ChainRedefinitionFollow` (`graph_builder.py:1187`) is adjacent chain-follow logic, untouched here.
This item adds a resolution step to the **CalcUsage** path (backtracker), not the aggregation path.
R1: record the newly-supported chain shape for the agentic-mbse MODELING_GUIDE in the item close-out
(sandbox-blocked this session); update `24-dual-resolution-architecture.md` CHAIN-dispatch section
to document the climb step in the same change.

## Validation Approach

- **Both wires pinned** (INV-1): exact-QN assertions for `data_point` and `base_metric`,
  independently anchored to the fixture source.
- **Loud tail** (INV-2): fires-on-shape unit test (dangling chain → WARN + EP) + silent-on-clean
  (no WARN when the two corpus chains resolve).
- **Parity** (INV-3): live/offline identity test (@requires_license) — both channels equal offline.
- **Byte-identity** (INV-4): full-suite baseline re-capture; only `deep_cross_scope_probe` diffs,
  as the reviewed three-part diff; all others byte-identical via the timestamp-churn method.
- **Gates:** `uv run pytest tests/` green; `mypy src/`, `ruff check src/` no new findings.

## Next-Stage Handoff

- **Fixed:** extraction emits full-path CHAIN (D1); the walk is ancestor-scope climbing in
  `_resolve_chain_dispatch`, gated to 3+-segment (D2/D4), with a collect-all-and-refuse ambiguity
  guard (M-1/INV-2b); the loud diagnostic moves to the backtracker Step-4 fallback as a genuine
  `logger.warning` (D3/M-2); fires-on-shape is a synthetic unit test asserting level=WARNING + the
  untruncated QN (D5); resolution is `scoped_lookup`-only, structurally guaranteed by the 1-dot
  alias-key shape (B3/INV-3); base_metric resolves via the existing Step 1 (no climb).
- **Open at plan:** exact form of the ancestor-prefix iteration; the code comment naming the
  filed first-segment-shadowing assumption at the climb site (B2); how the backtracker surfaces the
  new WARN (caplog target); whether the stale classification flip survives the wire flips
  (root-cause at re-capture).
- **De-risk first:** confirm the climb resolves `data_point` to the exact expected channel **and**
  that no other baseline diffs — run the byte-identity gate before writing the pins, so a surprise
  churn surfaces before the pins encode it.

---
Next Step: After approval → `/_my_plan` or `/_my_implement`.
