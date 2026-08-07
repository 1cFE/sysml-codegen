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
- [x] `elaboration/graph.py` + `elaborate.py` per design D1–D5 (AST-walked calc/constraint
      population per D2 — NOT the extractor's expanded population; factor the per-binding
      evidence builders out of `usage_extractor` so both front ends share them).
- [x] Port spike probes 1/2/4 as kept conformance tests (licensed) — spike parity is the
      Phase-1 gate: C25/C8/C24/C19/self-binding/deep-path/Bank/node-ID checks all green.

### Phase 2 — Shape learning tests (each BEFORE its implementation; kept, licensed)
- [x] Cross-package / multi-hop EXPOSE (wi014_toy, catf_mfe shapes) — DONE 2026-08-07.
      Findings: `.project/research/20260807-163643_elaborator-crosspackage-expose-shapes.md`;
      15 kept tests in `tests/conformance/test_elaboration_expose_shapes.py`. Landed:
      untyped-part contexts, usage/package attr nodes, package-level calc placement,
      sibling-calc + off-ancestor chain anchors, EXPOSE alias edges with transitive
      follow-through, and the D9 `strict` halt-vs-report switch (forced early: catf_mfe
      itself authors a real SRC-01 self-binding, `vacuum.sysml:176` — strict rejects it,
      pinned; lenient records + skips only that binding, which Phase 3's grind requires).
- [x] Sibling same-name channels (sibling_channel_ambiguity) — DONE 2026-08-07. Holds by
      construction (occurrence-path identity: no flat namespace to collide in); zero
      elaborator changes. 5 kept tests in `tests/conformance/test_elaboration_sibling_channels.py`;
      findings `.project/research/20260807-165502_elaborator-sibling-channels.md`. The fixture
      itself authors `in fuel = fuel` (SRC-01) — third member of the "fixture authors
      SRC-01" class with catf_mfe and fusion_tea.
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

## Implementation Notes

### Phase 1 Completion
**Completed:** 2026-08-07

**Changes made:**
- Created `src/sysml_codegen/extraction/binding_evidence.py` — the five per-binding
  evidence builders + CST written-form helpers moved out of `usage_extractor.py`
  with public names (`chain_evidence`, `reference_evidence`, `literal_evidence`,
  `expression_evidence`, `bound_formal_facts`, `written_qualifier`,
  `written_reference_text`, `WRITTEN_UNKNOWN`); `usage_extractor` call sites updated
  (no other importers existed).
- `screen_source_readiness` (`source_evidence.py`) no longer skips templates: the
  filter was caller policy and no caller passed templates. The elaborator screens
  declarations templates-included — fusion_tea's `in gain = gain` lives in
  `part def 'IFE Power Plant'`, so the template skip would have hidden it from the
  unexpanded population D2 mandates.
- Created `src/sysml_codegen/elaboration/{__init__,graph,elaborate}.py`.
  `graph.py`: `InstanceGraph`, `AttrNode`, `CalcNode`, `ConstraintNode`, typed input
  refs (`NodeRef`/`ProducerRef`/`LiteralInput`), `ValueSite`, `ElaborationCode` +
  `Diagnostic`. `elaborate.py`: `elaborate(model, calc_defs)`, the one pass per
  D2–D5 with the def-context remap rule shared by override anchoring and
  calc/constraint placement.
- Created `tests/conformance/test_elaboration_spike_parity.py` (16 licensed tests):
  all probe-1/2/4 checks green — C25 collapse + 2-consumer count, C8, C24
  ProducerRef, C12/C13/C15, stamp-vs-authored-literal, C11 calc+constraint
  convergence, deep-path 43.0, C19 80.0 both paths, fusion_tea SI_SELF_BINDING,
  Bank cells, node-ID/edge/value stability across independent loads.
- Registered `_constraint_actuals` as an audited FCE+OE dispatch site in
  `test_ast_dispatch_invariant.py` (dual-check 3→4, multi-type 5→6, elif-ordering +
  invariant-comment checks now cover it).

**Deviations from prototype (deliberate, production-shaped):**
- Two-pass node build then binding resolution: the spike resolved while creating
  nodes, so a chain into a producer (C24) only resolved because of AST iteration
  order luck. All calc/constraint nodes now exist before any binding resolves.
- Calc population per D2: `extract_calculation_usages(expand_templates=False)` +
  the remap rule places templates AND def-nested-usage calcs (the spike consumed
  the legacy expansion, rejected by D10). Node created only where the parent path
  is a concrete occurrence; a declaration with no occurrence context logs a
  warning (no corpus fixture has package-level calc usages — verified against all
  37 snapshots).
- Heritage walk for definition attributes follows `Subclassification` into USER
  part defs only — following implicit specialization into the standard library
  minted `Part::isSolid` nodes (43 attrs vs the spike's 20; caught by probe,
  fixed, exact 20/12/5 parity restored).
- `default`-keyword values extract via the default-membership surface
  (`owned_memberships.is_default`), which `feature_value_expression` alone can
  miss — same dual surface as `SysMLDataExtractor._extract_default_value`.
  Probed live: `default 1.0/5.0/0.9` all captured.
- Constraint actuals ride the SAME factored evidence builders and resolution
  rules as calc bindings (D7); unsupported forms (self-binding/indexed/
  expression) hard-fail with contract codes at resolution (spec R3), misses are
  named diagnostics (`SI_OCCURRENCE_MISSING`/`SI_OCCURRENCE_AMBIGUOUS`), never
  fallback inputs.

**Known scope holds (phase-planned, not gaps):**
- EXPRESSION-redefined attrs (station_total etc.) are value-less nodes — computed
  nodes are D6, Phase 2.
- Multi-level specialized-def `:>>` literal shadowing (innermost def wins within
  tier 2) is not ordered yet — the Phase-2 spec-chain leg; no Phase-1 fixture
  authors it.

**Gates at completion:** full licensed suite 3172 passed / 47 skipped / 18
deselected, zero `no live syside license` skip lines; ruff clean; mypy at the
72-error baseline (zero new); no fixture/baseline/snapshot changes.
