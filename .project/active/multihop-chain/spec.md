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

The one fixture that exercises this shape is `deep_cross_scope_probe` (Pattern A,
`design.sysml:70`). It is currently pinned as a rejection (`test_deep_cross_scope_probe.py:53-99`);
this item flips that pin to a resolved-chain assertion.

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
- **Pattern A pin — CONFIRMED as a rejection.** `test_deep_cross_scope_probe.py` currently pins:
  empty offender set (`:41`), the consumer input landing on its own EP (`:53`,
  `…__chain_analysis__data_point`), no truncated `station` binding (`:61`), and a fires-on-shape
  extraction warning naming `station.array.derived_calc.derived_value` (`:83`). All must flip.
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

- [ ] A 3+-segment chain binding (`station.array.derived_calc.derived_value`) resolves to the
  correct wired channel, verified by an **independently-anchored** test that asserts the **exact
  channel QN** (not merely "resolved" / "left the entry-point set").
- [ ] `deep_cross_scope_probe` Pattern A pins a **resolved chain**, not a rejection: `data_point`
  on `chain_analysis` wires to the `derived_calc.derived_value` output channel.
- [ ] A genuinely unresolvable deep chain still **hard-diagnoses** — loud warning + surfaced entry
  point, never truncated to root (the Item-5 contract).
- [ ] Fires-on-shape + silent-on-clean pair holds: the resolved wire is asserted on Pattern A;
  the retained reject diagnostic stays **silent** when the chain resolves and still **fires** on
  an unresolvable tail.
- [ ] Live and `--from-snapshot` paths produce the **same** Pattern-A wire (no offline mis-wire).
- [ ] Covered production/fixture baselines byte-identical (only `deep_cross_scope_probe` changes);
  its re-capture lands as a reviewed, decomposed diff.
- [ ] agentic-mbse MODELING_GUIDE impact recorded (sandbox-blocked this session → for a later sync).

## Known Requirements

- **[HARD]** The loud-diagnostic contract holds for the unresolvable tail (Item-5 contract). A
  3+-segment chain that cannot be fully resolved must still warn loudly and surface as an entry
  point — never truncate to root, never silently wire. The reject site (`usage_extractor.py:717`)
  is not deleted; it is narrowed to the tail the new path cannot resolve.
- **[HARD]** Channel-identity assertion. The Pattern-A test asserts the exact wired channel QN of
  the `derived_calc.derived_value` output, not "resolved" or "left `fallback_entry_points`." A
  mis-wire also removes the input from the fallback set (it becomes the *wrong* module output) —
  checking the fallback set alone cannot catch it (memory: `multihop-expose-offline-parity`, the
  prior Phase-5 miss). Anchor the expected QN to the fixture source, computed independently of the
  code under test (R1).
- **[HARD]** Covered baselines byte-identical. `deep_cross_scope_probe/design.sysml:70` is the
  **only** model in the repo with a 3+-segment dot chain (verified by corpus grep). Building the
  capability must change no other model's output. Re-confirm the grep at implement; if another
  model surfaces the shape, its baseline change is in scope and must be reviewed, not waved.
- **[HARD]** `deep_cross_scope_probe` re-capture is a deliberate, reviewed diff (R3). Its
  extraction snapshot and `computation_graph.json` baseline both change: `data_point` on
  `chain_analysis` flips from unbound-EP (currently only in `unbound_params`, listed twice) to a
  resolved CHAIN wire. **The same re-capture also carries a known, pre-existing stale
  entry-point-classification flip** (`entry_type` usage_literal→library_default, `source_calc_usage`
  null→Analysis_Calc/Derived_Metric — memory: `deep-cross-scope-stale-baseline`; it reproduces on
  the pre-F4 parent commit and is not multi-hop-caused). The re-capture diff MUST be decomposed:
  the intended multi-hop change separated from the stale flip, and the stale flip root-caused
  (code-correct vs baseline-correct) before commit. Capture via `scripts/capture_*.py` only.
- **[HARD / R1]** Every new-or-changed diagnostic lands with a fires-on-shape test (independently
  anchored) and a silent-on-clean sibling. Here the retained reject diagnostic changes scope, so
  both legs move: silent-on-clean = no multi-hop warning when Pattern A resolves; fires-on-shape =
  the warning still names an unresolvable deeper chain.
- **[NEED / R2]** The newly-supported chain shape is recorded for the agentic-mbse MODELING_GUIDE.
  agentic-mbse (`/home/reid/1cfe/agentic-mbse`) is **sandbox-blocked** this session (confirmed:
  outside the working directory — memory `agentic-mbse-repo-path`). Record the impact in this
  item's close-out for a later sync; do not fail the item. Disposition may be "no change needed,"
  but the shape is recorded either way.
- **[INFERRED]** Live/offline parity. A multi-hop cross-part chain is exactly the shape where the
  live path and the `--from-snapshot` path diverge — the confirm-walk that resolves the transitive
  channel runs only on `EXPOSE_CHAIN_TENTATIVE` CAs, and snapshots serialize the post-confirm state
  (memory: `multihop-expose-offline-parity`). The Pattern-A pin runs from the committed snapshot
  (`build_full_graph_from_snapshot`); the resolution must produce the identical wire live, or an
  offline mis-wire ships as a lying sim, not a crash. Guard the divergence with a live assertion or
  a live-vs-offline identity check, not the snapshot pin alone.

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
- The duplicate `data_point` entry in `chain_analysis.unbound_params` (`["data_point",
  "data_point"]`, snapshot line 271-272). Note it — resolving the binding likely clears it — but do
  not chase it as its own fix unless it survives the re-capture.

## Open Questions / Deferred to design

- **Where the multi-hop walk lives.** Two candidate seams: (a) extend `_parse_chain_expression`
  (`usage_extractor.py:807`) at extraction to emit the full dotted `source_path` + terminal
  element, then let the backtracker/registry `scoped_lookup` resolve the deep path; or (b) a
  dedicated resolution walk. The scoped registry may not carry deep-dotted keys — design must
  confirm `scoped_lookup` handles the full path or add the walk. The reference is
  `24-dual-resolution-architecture.md` (CHAIN dispatch) + `04-input-resolver.md`.
- **Confirm-walk re-tag vs pure CHAIN lookup.** Whether Pattern A's terminal needs the
  `EXPOSE_CHAIN_TENTATIVE` confirm-walk re-tag (the offline-parity trap, memory
  `multihop-expose-offline-parity`) or resolves purely through CHAIN `scoped_lookup`. Depends on
  where resolution lands (extraction-time CHAIN vs registry confirm pass).
- **Hop-resolution algorithm and the tail boundary.** How each segment resolves (part containment
  → calc usage → output), and exactly where the "unresolvable tail" line is drawn — which failure
  modes warn-and-surface vs resolve. This is the core mechanism; defer to design, but it must
  produce a testable "fires on unresolvable, silent on resolvable" boundary.
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
- **Key code:** `extraction/usage_extractor.py:717-750` (reject + 2-seg CHAIN),
  `extraction/expression_utils.py:279` (`extract_feature_chain_segments`)
- **Fixture:** `tests/fixtures/deep_cross_scope_probe/{design,library}.sysml`,
  its committed snapshot + `tests/fixtures/baseline_outputs/deep_cross_scope_probe/`
- **Pins:** `tests/conformance/test_deep_cross_scope_probe.py`
- **Design:** `.project/active/multihop-chain/design.md` (to be created)

---

**Next Steps:** After review, proceed to `/_my_design`.
