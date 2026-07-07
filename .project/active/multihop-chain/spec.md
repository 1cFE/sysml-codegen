# Spec: Resolved Multi-Hop Chain Bindings

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-06
**Complexity:** MEDIUM
**Branch:** truth-debt-epic
**Epic:** TRUTH-DEBT — Item 2

---

## Problem

A binding that reaches through three or more segments — `station.array.derived_calc.derived_value`
— is a **loud rejection today**, not a resolved wire. The extractor sees the deep chain, counts
its segments, warns, and drops the parameter to an unbound entry point. The consumer that wanted
that upstream value never gets wired to it; the modeler is handed a JSON entry point to fill by
hand instead.

This was a deliberate stop, not a bug. The prior epic's Item 5 built the loud reject on purpose:
the ≤2-segment chain parser (`_parse_chain_expression`, `usage_extractor.py:807`) cannot represent
a 3+-segment path, so rather than truncate `a.b.c.d` to its root `a` (a silent mis-wire), the code
hard-rejects and surfaces the parameter loudly (`usage_extractor.py:717-739`). The segment
extractor it needs already exists — `extract_feature_chain_segments` (`expression_utils.py:279`)
yields every segment — but Item 5 used it only to **count** for the reject diagnostic
(`usage_extractor.py:723`).

The gap is a missing capability: **walk the segments the extractor already yields, resolve each
hop to its owning part or channel, and terminate at the referenced output** — so a supported deep
chain resolves to its wire instead of degrading to an entry point. The genuinely unresolvable tail
must keep its loud diagnostic; the Item-5 contract (never a silent truncation) holds unchanged.

### Two extraction paths for deep chains — only one hits the reject

`extract_feature_chain_segments` has **two** callers, and they behave differently:

- **The calc-usage param-binding path** (`usage_extractor.py:723`) is the reject site this item
  removes. Deep chains here hard-reject.
- **The attribute value-binding path** (`computed_attribute_extractor.py:220`) already extracts the
  full segment list into a `reference_chain` and feeds a multi-hop EXPOSE confirm walk
  (`computed_attribute_extractor.py:217-220`). Deep chains here **already resolve**.

This distinction is the load-bearing fact behind the byte-identity guarantee (below), and it is the
likely reuse target for where the new walk lives (design Open Question 1).

### Two calc-usage chains flip — both inside `deep_cross_scope_probe`

The two calc-usage param bindings that hit the reject are both in this one fixture, and **both**
resolve when the walk lands. The re-capture carries both wire flips plus a third, unrelated change:

1. **`chain_analysis.data_point`** (Pattern A) = `station.array.derived_calc.derived_value`
   (`design.sysml:70`) → wires to the `derived_calc` calc's `derived_value` output.
2. **`derived_calc.base_metric`** (mid-level) = `sensor.core.metric_value` (`library.sysml:86`,
   currently unbound — snapshot `:394-397`) → wires to the `core` calc's `metric_value` output.
3. A **pre-existing stale entry-point-classification flip** already latent in the committed baseline
   (memory: `deep-cross-scope-stale-baseline`) — unrelated to multi-hop, folded into the same diff.

The two **attribute** deep chains in the corpus (`station_output` at `library.sysml:104`;
ife_plant's `magnet_volume_total` at `subsystems.sysml:12`) go through the already-resolving
attribute path and do **not** flip — ife_plant's baseline already wires `volume_calc__volume`
normally, with no `magnet_volume_total` reject.

The fixture is currently pinned as a rejection for both chains
(`test_deep_cross_scope_probe.py:41-99`); this item flips both pins to resolved-chain assertions.

### Verification at HEAD (R4 — filed pointers re-checked, post-Item-1)

Every filed claim in the epic was re-verified against HEAD before writing requirements. Filed
pointers are static-read verdicts until reproduced; these are the corrections.

- **Loud-reject site — CONFIRMED.** `usage_extractor.py:717-739` (epic cited `:756-779`; the
  region moved). The `FeatureChainExpression` arm: `len(segments) > 2` → append warning
  ("multi-hop chains are not resolved — surfacing as an entry point (not truncated to root)") →
  return `BindingType.UNBOUND` with `raw_expression` = "FeatureChainExpression (unresolved
  3+-segment) -> …". No truncation. The 2-segment path below it (`:740`) still builds a `CHAIN`.
- **Extractor helper — CONFIRMED.** `extract_feature_chain_segments` (`expression_utils.py:279`)
  expands `target_feature.chaining_features`, so `tf_coil.volume_calc.volume` yields all three
  segments. Called at `usage_extractor.py:723` for the count only.
- **Reject pins — CONFIRMED, and there are TWO chains, not one.** `test_deep_cross_scope_probe.py`
  currently pins the rejection for both: empty offender set (`:41`, whose docstring `:42-48`
  explicitly names *both* `chain_analysis.data_point` **and** `derived_calc.base_metric`), the
  Pattern-A input landing on its own EP (`:53`), no truncated `station` binding (`:61`), and a
  fires-on-shape warning naming `station.array.derived_calc.derived_value` (`:83`). All must flip.
  Corpus grep confirms four deep dot chains total: two calc-usage bindings
  (`design.sysml:70` data_point, `library.sysml:86` base_metric — both flip) and two attribute
  bindings (`library.sysml:104` station_output, ife_plant `subsystems.sysml:12` magnet_volume_total
  — already resolved via the attribute path, do not flip).
- **Reference doc — CORRECTED.** The epic cites `reference/24-binding-resolution.md`, which does
  **not exist**. The actual binding-resolution reference is
  `docs/architecture/reference/24-dual-resolution-architecture.md` (the two resolution paths and
  the type-directed CHAIN/REFERENCE dispatch), with `03-resolution-overview.md` and
  `04-input-resolver.md` as the companions. Use these.
- **Adjacent region (post-Item-1) — NOTED.** Item 1's F4 cutover landed; the live aggregation
  path now runs `resolve_input(…, AGG_STRATEGIES)` via `_build_agg_input_source`
  (`graph_builder.py:1252`), and `ChainRedefinitionFollow` is one of the strategies
  (`graph_builder.py:1187` references its CHAIN matching pattern). This is the chain-follow logic
  adjacent to the multi-hop work — a new resolution path built next to it, not a change to it.

## Success Criteria

- [x] **Both** calc-usage 3+-segment chains resolve to their correct wired channels, each verified
  by an **independently-anchored** test asserting the **exact channel QN** (not "resolved" / "left
  the entry-point set"):
  - `chain_analysis.data_point` → `…__station__array__derived_calc__derived_value`.
  - `derived_calc.base_metric` → `…__station__array__sensor__core__metric_value`.
- [x] `deep_cross_scope_probe` pins both as **resolved chains**, not rejections (the current
  rejection pins at `test_deep_cross_scope_probe.py:41-99` flip).
- [x] A genuinely unresolvable deep chain still **hard-diagnoses** — loud warning + surfaced entry
  point, never truncated to root (the Item-5 contract).
- [x] Fires-on-shape + silent-on-clean pair holds, **fully tested**: silent-on-clean is proven on
  the two now-resolving chains; fires-on-shape is proven on a **new unresolvable-chain substrate**
  (a dangling-chain fixture or a synthetic unit test — no corpus chain is unresolvable after the
  flip).
- [x] Live and `--from-snapshot` paths produce the **same** wires for both chains (no offline
  mis-wire). Note: the live leg is `@requires_license`-gated (below). [audit: verified statically;
  live re-execution sandbox-blocked — audit.md Note 1]
- [x] Byte-identity holds **path-scoped**: no calc-usage-param baseline other than
  `deep_cross_scope_probe` changes; `deep_cross_scope_probe`'s re-capture lands as a reviewed diff
  decomposed into its **three** parts (two wires + the stale classification flip).
- [x] agentic-mbse MODELING_GUIDE impact recorded (sandbox-blocked this session → for a later sync).

## Known Requirements

- **[HARD]** The loud-diagnostic contract holds for the unresolvable tail (Item-5 contract). A
  3+-segment chain that cannot be fully resolved must still warn loudly and surface as an entry
  point — never truncate to root, never silently wire. ~~The reject site (`usage_extractor.py:717`)
  is not deleted; it is narrowed to the tail the new path cannot resolve.~~
  **[DESIGN ANNOTATION 2026-07-07 — deviation APPROVED at design-review]** The reject site is **not**
  narrowed at extraction. Extraction has no registry, so it cannot tell a resolvable chain from an
  unresolvable one; the loud + entry-point + never-truncated contract **moves to the backtracker
  Step-4 fallback** (`dependency_backtracker.py:569`), where the registry lookup actually fails, as
  a genuine `logger.warning`. The substance is preserved; only the location moves, for the hard
  registry-timing reason. See design.md D3 and design-review.md move 6.
- **[HARD]** Channel-identity assertion — for **both** wires. Each test asserts the exact wired
  channel QN, not "resolved" or "left `fallback_entry_points`." A mis-wire also removes the input
  from the fallback set (it becomes the *wrong* module output) — checking the fallback set alone
  cannot catch it (memory: `multihop-expose-offline-parity`, the prior Phase-5 miss). Anchor each
  expected QN to the fixture source, computed independently of the code under test (R1):
  `data_point → …__station__array__derived_calc__derived_value` and
  `base_metric → …__station__array__sensor__core__metric_value` (the `core` instance QN is
  `DeepCrossScopeDesign__measurement_system__station__array__sensor__core`, snapshot `:383`;
  confirm exact casing at implement). If `base_metric`'s flip lands unpinned, part of the re-capture
  diff has no test guarding it — exactly the silent mis-wire this item exists to prevent.
- **[HARD]** Covered baselines byte-identical — **path-scoped**. The reject path is reachable
  **only** from calc-usage param bindings, and the only two such 3+-segment chains are both in
  `deep_cross_scope_probe` (`design.sysml:70`, `library.sysml:86`). The two attribute deep chains
  (`station_output`, ife_plant's `magnet_volume_total`) go through the already-resolving attribute
  path (`computed_attribute_extractor.py:217-220`) and do not touch the reject. So the guarantee is:
  no calc-usage-param baseline other than `deep_cross_scope_probe` changes. Implement-time gate:
  re-grep, and **if design factors a shared segment-resolution walk the attribute path also adopts**
  (a plausible refactor — the attribute path already has a confirm walk), then `station_output` and
  ife_plant's `magnet_volume_total` may re-resolve and their baselines are in scope and reviewed,
  not a violation.
- **[HARD]** `deep_cross_scope_probe` re-capture is a deliberate, reviewed diff (R3) with **three**
  distinct parts — the reviewer checks each diff line against a known cause:
  1. `chain_analysis.data_point` flips from unbound-EP (currently only in `unbound_params`, listed
     twice) to a resolved CHAIN wire.
  2. `derived_calc.base_metric` flips from unbound-EP (snapshot `:394-397`) to a resolved CHAIN wire.
  3. A known, pre-existing stale entry-point-classification flip (`entry_type`
     usage_literal→library_default, `source_calc_usage` null→Analysis_Calc/Derived_Metric — memory:
     `deep-cross-scope-stale-baseline`; the 4-line flip reproduces on pre-F4 commit `ba3bca4`,
     non-aggregation). Root-cause it (code-correct vs baseline-correct) before commit.
  Both the extraction snapshot and `computation_graph.json` change; capture via
  `scripts/capture_*.py` only.
- **[HARD / R1]** Every new-or-changed diagnostic lands with a fires-on-shape test (independently
  anchored) and a silent-on-clean sibling — **both legs fully tested**. The retained reject
  diagnostic changes scope: silent-on-clean = no multi-hop warning when the two corpus chains
  resolve. But after the flip **no corpus chain is unresolvable**, so fires-on-shape has no
  substrate — this item MUST add one: a new minimal fixture with a dangling deep chain, or a
  targeted unit test with a synthetic unresolvable chain. Without it the diagnostic ships with only
  its silent-on-clean half tested, violating the R1 discipline the item is built on.
- **[NEED / R2]** The newly-supported chain shape is recorded for the agentic-mbse MODELING_GUIDE.
  agentic-mbse (`/home/reid/1cfe/agentic-mbse`) is **sandbox-blocked** this session (confirmed:
  outside the working directory — memory `agentic-mbse-repo-path`). Record the impact in this
  item's close-out for a later sync; do not fail the item. Disposition may be "no change needed,"
  but the shape is recorded either way.
- **[HARD]** Live/offline parity. A multi-hop cross-part chain is exactly the shape where the live
  path and the `--from-snapshot` path diverge — the confirm-walk that resolves the transitive
  channel runs only on `EXPOSE_CHAIN_TENTATIVE` CAs, and snapshots serialize the post-confirm state
  (memory: `multihop-expose-offline-parity`). This exact failure — resolving live yet mis-wiring
  from a snapshot — **already happened** on this shape (the Phase-5 miss), which is why the
  obligation is HARD, not inferred; the mechanism (which guard) stays open for design. The two
  wire pins run from the committed snapshot (`build_full_graph_from_snapshot`); the resolution must
  produce the identical wires live, or an offline mis-wire ships as a lying sim, not a crash.
  **Caveat — the guard is `@requires_license`-gated.** A live or live-vs-offline check runs on the
  same licensed path as the existing `test_pattern_a_deep_chain_warns_on_extraction`
  (`test_deep_cross_scope_probe.py:83`), so it is **skipped in license-free CI**. There, the
  committed-snapshot pin is the *only* always-on guard — and the snapshot is precisely where an
  offline mis-wire would be baked in. Do not treat the live parity check as an always-on safeguard.

## Non-Goals

- **Pattern B** (`measurement_system::station::array::sensor::core::metric_value`, a 6-segment
  `::` REFERENCE, `design.sysml:82`). It goes through the `FeatureReferenceExpression` arm
  (`usage_extractor.py:752`), which does **not** loud-reject; it already "resolves" today
  (`test_deep_cross_scope_probe.py:102` pins it to `DeepCrossScopeProducer__Core_Metric__metric_value`,
  possibly via Step-1b last-2-segment normalization). This item is scoped to the CHAIN loud-reject.
  If Pattern B's resolution is genuinely wrong, **file it**, don't fix it here.
- Expression-valued chain RHS beyond what the prior epic's Item 10 already wired.
- Chain shapes no supported model uses. Build for `deep_cross_scope_probe` Pattern A and any real
  shape a model exercises; **file, don't build** for hypothetical deeper/branching shapes.
- The duplicated entries in `unbound_params` — `data_point` twice on `chain_analysis`
  (snapshot `:271-272`) and `base_metric` twice on `derived_calc` (snapshot `:395-396`). Note
  them — resolving the bindings likely clears both — but do not chase the duplication as its own
  fix unless it survives the re-capture.

## Open Questions / Deferred to design

- **Where the multi-hop walk lives.** Candidate seams: (a) extend `_parse_chain_expression`
  (`usage_extractor.py:807`) at extraction to emit the full dotted `source_path` + terminal
  element, then let the backtracker/registry `scoped_lookup` resolve the deep path; (b) a dedicated
  resolution walk; or (c) **reuse the attribute path's existing multi-hop confirm walk**
  (`computed_attribute_extractor.py:217-220`), which already resolves deep chains from a
  `reference_chain` — the most likely reuse target. The scoped registry may not carry deep-dotted
  keys — design must confirm `scoped_lookup` handles the full path or add the walk. **Watch the
  byte-identity boundary:** if design shares a walk with the attribute path (option c or a shared
  factoring), the attribute chains (`station_output`, ife_plant) come into scope — see the
  path-scoped byte-identity requirement. The reference is `24-dual-resolution-architecture.md`
  (CHAIN dispatch) + `04-input-resolver.md`.
- **Confirm-walk re-tag vs pure CHAIN lookup.** Whether Pattern A's terminal needs the
  `EXPOSE_CHAIN_TENTATIVE` confirm-walk re-tag (the offline-parity trap, memory
  `multihop-expose-offline-parity`) or resolves purely through CHAIN `scoped_lookup`. Depends on
  where resolution lands (extraction-time CHAIN vs registry confirm pass).
- **Hop-resolution algorithm and the tail boundary.** How each segment resolves (part containment
  → calc usage → output), and exactly where the "unresolvable tail" line is drawn — which failure
  modes warn-and-surface vs resolve. This is the core mechanism; defer to design, but it must
  produce a testable "fires on unresolvable, silent on resolvable" boundary.
- **Unresolvable-chain substrate — fixture or unit test.** The retained reject diagnostic needs a
  fires-on-shape substrate (HARD, above), but the *form* is open: a new minimal fixture with a
  dangling deep chain (a chain whose tail names a non-existent output), or a targeted unit test
  feeding a synthetic unresolvable chain. A unit test is cheaper and does not add a captured
  baseline; a fixture is more faithful. Design decides.
- **Baseline sequencing.** Recommended: fold the stale-classification root-cause into this item's
  re-capture, since Item 2 must re-capture `deep_cross_scope_probe` anyway (it is the only Pattern-A
  fixture). Alternative: a separate prior change for the stale flip. Design/plan decides; either
  way the diff is decomposed and each part independently justified.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_truth_debt.md` (Item 2; R1–R4; Risks table)
- **Required Reading:**
  - BACKLOG `[MULTIHOP-CHAIN-PARSE]` (`.project/backlog/BACKLOG.md`)
  - Discovery register §D3-2 (`.project/research/20260706_pipeline-truth-discovery.md`)
  - Memory: `multihop-expose-offline-parity`, `cross-part-binding-v11-fallthrough`,
    `deep-cross-scope-stale-baseline`, `agentic-mbse-repo-path`
  - `docs/architecture/reference/24-dual-resolution-architecture.md` (**corrected** from the
    epic's non-existent `24-binding-resolution.md`), with `03-resolution-overview.md`,
    `04-input-resolver.md`
- **Adjacent (Item 1, landed):** `.project/active/f4-cutover/{design,plan}.md` — the F4 cutover
  region; `graph_builder.py:1187/1252` (`ChainRedefinitionFollow`, `_build_agg_input_source`)
- **Key code:** `extraction/usage_extractor.py:717-750` (reject + 2-seg CHAIN);
  `extraction/expression_utils.py:279` (`extract_feature_chain_segments`, the shared helper);
  `extraction/computed_attribute_extractor.py:217-220` (the attribute path's already-resolving
  multi-hop confirm walk — the second caller, and the likely reuse target)
- **Fixture:** `tests/fixtures/deep_cross_scope_probe/{design,library}.sysml`,
  its committed snapshot + `tests/fixtures/baseline_outputs/deep_cross_scope_probe/`
- **Pins:** `tests/conformance/test_deep_cross_scope_probe.py`
- **Design:** `.project/active/multihop-chain/design.md` (to be created)

---

**Next Steps:** After review, proceed to `/_my_design`.
