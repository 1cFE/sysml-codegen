# Fixture-Gap Register — Plant-Value & Blind-Spot Fixtures (PIPELINE-TRUTH Item 1)

**Created:** 2026-07-06
**Owner:** Reid W
**Source:** discovery register §D6 (`.project/research/20260706_pipeline-truth-discovery.md`)

Records the D6 value-provision / secondary shapes this item DEFERRED rather than built
(Decision D4), each with a pointer to §D6, plus any secondary shape removed under the
Phase-1 L2-2 escape hatch (with crash evidence). Promotable to `BACKLOG.md` if the epic
wants it tracked corpus-wide.

## Deferred D6 shapes (D4 filed remainder — pointer to §D6)

Each is low-leverage for Items 2/5 or a fourth value-provision path beyond the three the
headline pins; deferred to keep the headline minimal and legible.

1. **Selective import of quoted names** — a parser/import concern with no value-provision
   or diagnostic-truth leverage for Items 2/5. FILED. (§D6)
2. **Standalone package-level instance whose `:>>` literals feed a def-owned calc's
   bindings** — a value-provision variant, but a FOURTH path beyond the three the headline
   pins (a/b/c); adds fixture surface without moving Item 2's before/after. FILED, noted as
   an Item-2 follow variant. (§D6)
3. **Constraint def consuming a defaulted param** — Item 4 (constraint truth) territory;
   the headline already carries an `assert constraint` with an unbound-defaulted binding
   (`threshold`). FILED to Item 4's scope. (§D6)
4. **Consumer calc reaching a subtype-only calc-derived attribute through a usage-level
   retyped child (standalone variant)** — structurally covered by the headline's retype
   (mechanism a) + the extended `spec_chain_twolevel`; the standalone variant is FILED as
   not naturally covered at capture. (§D6)

## Escape-hatch removals (L2-2 — crash evidence)

**None.** No secondary shape crashed the extractor. Every named D4 shape — including the
two likely crash candidates, `out attribute 'net cost'` (quoted output param) and the
Style-E `'Mixed Output Style'` (mixed `out attribute` + `return`) — LOADED and captured
cleanly (see `plant_value_shapes`; both pinned CORRECT in `test_plant_value_shapes.py`).
The only Phase-1 authoring fixes were reserved-keyword collisions (`flow` param → `flow_rate`;
`derived` calc-usage name → `derived_calc`) and one over-a-bound-value `:>>` (base attr made
valueless) — parse errors, not extractor crashes, so no `src/` change and no filing needed.

## Observed degradations worth a follow-up (not blocking Item 1)

These are captured-and-pinned degradations (not deferrals) surfaced during Item 1; noted
here so a future item can pick them up:

- **Multi-hop CHAIN source_path truncation** — a deep dot-chain binding
  (`station.array.derived_calc.derived_value`, or any 2+-hop `a.b.c`) truncates its
  `source_path` to the FIRST segment. Exposed by `deep_cross_scope_probe` (Pattern A) and
  the reason mechanism (c) was authored as a one-hop chain. Pinned in
  `test_deep_cross_scope_probe.py::test_pattern_a_deep_chain_source_path_truncates_degradation`.
- **Econ-param nested `:>>` doesn't reach a cross-part input** — the attribute-def-typed
  nested `:>>` (`'Econ Param'`) value does not propagate to a cross-part calc input (DEGRADED).
  Pinned in `test_plant_value_shapes.py::test_shape1_econ_param_nested_redef_does_not_reach_cross_part_input`.
- **Inherited-attr-redefined-below doesn't propagate** — `:>> throughput = 8.0` below an
  in-binding that reads the inherited `throughput` does not reach the calc input (DEGRADED).
