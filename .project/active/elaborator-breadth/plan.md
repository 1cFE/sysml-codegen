# Plan: Elaborator Breadth — Learning Tests + Dual-Run (ELABORATE-FIRST Item 5)

**Status:** Ready to start (Item 4 design landed 2026-08-07)
**Design:** `.project/active/elaborator-design/design.md` · **Spec:** `../elaborator-design/spec.md`
**Prototype to graduate:** `.project/active/elaborator-spike/elab_prototype.py` (scratch — the
production package is written fresh against the design, stealing freely from it)

## The Point

Grow the production elaborator (`src/sysml_codegen/elaboration/`) across every supported shape,
each risky shape probed by a learning test BEFORE its implementation, and prove breadth
mechanically: old-vs-new `ComputationGraph` diff over all 37 fixtures, zero unclassified rows.
The inherited 29-cell contract matrix is the coverage checklist. Old front end stays
authoritative and untouched throughout.

## Phases

### Phase 1 — Package seed + spike parity
- [ ] `elaboration/graph.py` + `elaborate.py` per design D1–D5 (AST-walked calc/constraint
      population per D2 — NOT the extractor's expanded population; factor the per-binding
      evidence builders out of `usage_extractor` so both front ends share them).
- [ ] Port spike probes 1/2/4 as kept conformance tests (licensed) — spike parity is the
      Phase-1 gate: C25/C8/C24/C19/self-binding/deep-path/Bank/node-ID checks all green.

### Phase 2 — Shape learning tests (each BEFORE its implementation; kept, licensed)
- [ ] Cross-package / multi-hop EXPOSE (wi014_toy, catf_mfe shapes)
- [ ] Sibling same-name channels (sibling_channel_ambiguity)
- [ ] Specialization + usage-level retypes, two-level (spec_chain_twolevel, fusion_tea driver)
- [ ] FORMULA computed attributes incl. FORMULA→FORMULA (previously unsupported — expected to
      lift, design D6)
- [ ] EXPRESSION-redefinition aggregations incl. cross-part rollups
      (crosspart_rollup_twolevel, d38_caret, agg_localterm_probe)
- [ ] Constraint catalog through projection (design D7; nested_occurrence_override_probe strict
      run must now generate)
- [ ] Independent equal-valued literals stay distinct; shadowing/specialization referent
      fixtures (the capability-survey evidence gap — author the missing fixtures)
- [ ] Snapshot round-trip learning test: serialize instance graph → rebuild → project; parity
      with live projection (de-risks Item 6's format before anything is versioned)

### Phase 3 — Dual-run harness + corpus grind
- [ ] Internal parallel entry point (never a shipped flag) + ComputationGraph diff tool
      (modules, channels, wiring, entry-point sets)
- [ ] All 37 fixtures diffed; every row classified: expected-collapse (the 75 mints) /
      expected-fix (C19) / needs-review / new-bug. Zero unclassified at close.
- [ ] 29-cell matrix checklist: every supported cell green on the new path; every rejected
      cell fails with its named diagnostic.

**Stop condition:** a shape the Item-3 contract does not answer → surface to owner, never
disposition silently.

**Owner checkpoint:** the classified diff ledger, before Item 6 cutover.
