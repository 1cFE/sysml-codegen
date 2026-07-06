# Spec: Plant-Value & Blind-Spot Fixtures (PIPELINE-TRUTH Item 1)

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-06
**Complexity:** MEDIUM
**Branch:** pipeline-truth-epic

---

## Problem

The pipeline's fixtures do not cover the shapes fusion-tea actually uses to hand a
whole-plant calc its input values. `generate --models ~/1cfe/fusion-tea/models` aborts
at V11 on exactly 10 plain subsystem-attribute → plant-calc-input references. Those 10
references decompose into three value-provision mechanisms (discovery §D6):

- **(a) subtype-def literal `:>>` consumed cross-part through a usage-level retype** — 5
  of 10 refs (`hif_driver.sysml:81,83,84`). No fixture wires this end-to-end.
- **(b) bare `part :>> name { :>> attr = literal; }` override block, no retype** — 4 of
  10 refs (`hif_plant.sysml:36-49,51-65`). **Zero fixtures contain a no-retype `part
  :>>` block at all** — every existing fixture `part :>>` carries a type.
- **(c) `driver.cost_per_joule`** — 1 ref; the shape `spec_chain_twolevel` already
  covers (calc-output-valued variant only).

`spec_chain_twolevel` covers exactly one of ten; the `ife_plant` fixture covers none
(its lcoe binds plant-local literals). So there is no in-repo fixture that reproduces
the fusion-tea V11 abort — the "before" state Item 2 must flip. Without it, Item 2 has
no pinned before/after and Item 5 has no substrate for several of its shapes.

Alongside the value-provision gap, discovery named a set of secondary fusion-tea model
shapes that no fixture covers (attribute-def-typed attributes with nested `:>>`, bare
`default 10.0`, quoted enum defs, quoted output-parameter names, mixed `out attribute` +
`return` calc defs, deep specialization chains, assert constraints carrying cross-part /
self-named / unbound-defaulted bindings). Their current behavior — correct, degraded, or
diagnostic — is unknown because nothing exercises them. Two capture-hygiene gaps also
sit open: `deep_cross_scope_probe` drifts with no committed snapshot (D1-F6), and three
committed snapshots (`wi014_toy`, `self_named_binding_trap`, `quoted_owner_formula`)
drift from current live output (BACKLOG stale-fixture-refresh chore).

This item closes the fixture blind spot and pins the "before" state, so the mechanism
work (Item 2) and the diagnostic-truth work (Items 4, 5) build on real, reviewed
fixtures instead of invented shapes.

## Success Criteria

- [ ] A headline fixture (`plant_values`) loads, captures an extraction snapshot, builds
  its graph, and **trips V11 today** — its `collect_uncovered_params` result is a
  non-empty offender set that reproduces all three value-provision mechanisms (subtype-def
  literal via usage-level retype; bare no-retype `part :>>` override block; the
  `spec_chain_twolevel`-style chain), pinned by a test that fails if the offender set
  changes. This is the pinned "before" state Item 2 flips.
- [ ] `spec_chain_twolevel` is extended with the plain cross-part-attribute shape (the P1
  acceptance note), including one attribute consumed by **two** modules (the fan-out
  collapse case the bridge never exercised); its snapshot re-captures as a reviewed diff
  and its existing pins still hold.
- [ ] The high-value secondary shapes (subset decided below) load and capture; **each
  shape's current behavior — correct, degraded, or diagnostic — is pinned by a test,
  determined empirically at capture, not assumed.**
- [ ] The assert-constraint shape carrying cross-part + self-named + unbound-defaulted
  bindings exists in a fixture and is recorded as Item 4's fires-on-shape substrate (it
  is invisible to the drop report today — the CONSTRAINT-SILENCE bug).
- [ ] `deep_cross_scope_probe` gains a committed snapshot and a drift-pin test.
- [ ] The stale-fixture-refresh rider is executed in the same live-capture session (own
  commit, reviewed diff) — including the `quoted_owner_formula` reclassification, reviewed
  deliberately.
- [ ] All captures are script-reproducible via `scripts/capture_*.py`; every existing
  baseline **not deliberately touched by this item** stays byte-identical.
- [ ] The fixture-gap register records the deferred D6 shapes (pointer to discovery §D6),
  and the plant-value fixture shapes are recorded for Item 9's agentic-mbse impact list.

## Known Requirements

### The headline fixture (`plant_values`)

- **[HARD]** New fixture directory `tests/fixtures/plant_values/` (a separate fixture, not
  an edit of `ife_plant` — see Decision D1). Follows the existing plant-idiom layout
  (`library.sysml` + `design.sysml`, plus a subsystems file if a cross-package half is
  needed), parseable by SysIDE as one model.
- **[HARD]** Reproduces the D6 recipe: a base plant def declaring `part sub :
  AbstractBase` plus a calc usage **and** an assert-constraint usage binding
  `sub.<plain_attr>`; a plant part USAGE containing both (a) a bare no-retype `part :>> sub
  { :>> attr = <literal>; }` block — the shape zero fixtures contain — and (b) a
  usage-level retype whose subtype def supplies other attrs via literal `:>>`. Mechanism
  (c) is present via a `driver.cost_per_joule`-style chain (reuse the twolevel shape).
- **[HARD]** The fixture trips V11 today. Concretely: `build_full_graph_from_snapshot`
  builds the graph (V11 fires at the generation boundary, not at graph build — like
  `chain_override_probe`), and `collect_uncovered_params(graph)` returns a non-empty
  offender set covering the three mechanisms. The test pins the exact offender set (the
  `chain_override_probe` / `ife_plant` pattern in `test_uncovered_params.py` and
  `test_ife_plant.py`). Item 2 flips this pin as it wires.
- **[HARD]** The assert constraint carries three binding sub-shapes in one place: a
  cross-part binding, a self-named binding (`in x = x`), and an unbound defaulted param.
  These are visible to the binding resolver and are the substrate Item 5 hardens; the
  assert constraint itself is invisible to the drop report today (Item 4 substrate).
- **[HARD]** Committed baselines for `plant_values` are captured via the scripts (see
  Baseline discipline below), so Item 2's resolution lands as a reviewed diff.
- **[INFERRED]** Hand-computed expected values for whatever the fixture's calc chain
  produces are recorded in the plan/fixture provenance, so Item 2's after-state can be
  anchored independently of the resolver (SC-B lineage; matches the ife_plant provenance
  style).

### Extend `spec_chain_twolevel`

- **[HARD]** Add the plain cross-part-attribute shape (a subsystem attribute referenced by
  a plant-calc input, no calc-output in the chain — the P1 acceptance note distinct from
  the existing calc-output-valued `driver.cost_per_joule`), and one attribute consumed by
  **two** modules (fan-out). Re-capture the snapshot; update `test_spec_chain_twolevel.py`
  to add pins for the new shapes while preserving the existing `usage_type_map` retype pin.
- **[HARD]** The extension keeps the fixture the one Item 2's SC-B in-repo tolerance test
  and Item 3's SNAP-19 parity parametrization run against (both name "the extended
  `spec_chain_twolevel`").

### Secondary shapes (the high-value subset — Decision D4)

- **[HARD]** Cover, with a test pinning each shape's **observed** current behavior:
  attribute-def-typed attribute with nested `:>>` (the 14-econ-params shape); bare
  `default 10.0` (no `:=`); doc bodies inside calc usages and on `:>>` redefinitions; an
  in-binding referencing an inherited attr the same def redefines below it; a 5-deep
  specialization chain with abstract ends; quoted enum def + usage-level quoted enum `:>>`;
  a quoted OUTPUT parameter name (`out attribute 'net cost'`); Style-E calc def (mixed `out
  attribute` + `return` in one def, inside a quoted def) and a return-in-quoted-def row.
- **[NEED]** Non-float entry-point literal shapes exist so Item 5 has a substrate: a
  bool/string/enum-valued attribute one hop from an entry point (fusion-tea's `wall_type`
  enum shape). Recorded for Item 5; its current behavior (silent `None`-omission per
  adversarial SC-5) is pinned as observed.
- **[INFERRED]** These live in a small second fixture (`plant_value_shapes`) rather than in
  the headline, so the V11-tripping headline stays minimal and legible. Split further only
  if a shape cannot co-exist in one parseable model.

### Capture hygiene

- **[HARD]** Commit `deep_cross_scope_probe`'s extraction snapshot (register it in the
  appropriate capture list — full-pipeline if it builds a graph, else extraction-only) and
  add a test pinning its current (drift) shape so future silent drift fails.
- **[HARD]** Run the stale-fixture-refresh rider (Decision D3): re-capture `wi014_toy`,
  `self_named_binding_trap` (path canonicalization only) and `quoted_owner_formula` (path
  canonicalization + the `net_margin`/`total_payout` design-attr → computed-attr
  reclassification). Own commit, reviewed diff. The reclassification is reviewed
  deliberately against post-Item-7 computed-attribute behavior — confirmed correct or
  filed, never waved through.

### Cross-cutting

- **[HARD]** R3 baseline discipline: all captures via `scripts/capture_*.py`; the live
  syside license is used for capture (available, monthly renewal). Every existing baseline
  not deliberately touched stays byte-identical. Deliberately-touched set is enumerated
  below and nowhere else changes.
- **[HARD]** Zero production-code changes. Fixtures, snapshots, baselines, tests, and the
  capture-script registration lists only.
- **[INFERRED]** New fixtures follow ADR-002 SysML conventions and the plant-idiom
  provenance-doc-comment style already in `ife_plant` (source, reference, last-updated).

## Non-Goals

- Any production-code change (the mechanism that resolves the three value shapes is Item
  2; loud-diagnostic code is Items 4/5).
- Fixture rows for shapes this epic defers: conditionals, non-uniform arrays,
  EXPOSE_COMPUTED, supertype-chain template inheritance for plain usages.
- Wiring the headline fixture's cross-part values (that is exactly the "before" state Item
  2 flips; here it must trip V11).
- The full D6 shape list — the low-leverage remainder is FILED to the fixture-gap register,
  not built (Decision D4).

## Decisions (made at spec-time, autonomous run)

**D1 — New `plant_values` fixture, not an extension of `ife_plant`.** The epic allows
either. Chosen: new fixture. Rationale: `ife_plant`'s committed baselines are pinned
byte-identical by many downstream tests, and its shapes deliberately build without
tripping V11 (they fall to Step-4 fallbacks). The headline fixture must TRIP V11 — a
different success bar. Folding it into `ife_plant` would churn `ife_plant`'s baselines and
muddy its per-shape labels, violating the byte-identity criterion. A dedicated fixture
keeps `ife_plant` untouched and makes Item 2's before/after diff legible on one fixture.

**D2 — Extend `spec_chain_twolevel` in place (re-capture its snapshot).** The epic and
Item 2's SC-B both name "the extended `spec_chain_twolevel`," so it must be the same
fixture. Its snapshot re-captures as a reviewed diff; the "existing baselines
byte-identical" criterion therefore means every fixture *other than* the ones this item
deliberately edits. The existing retype pin is preserved; new pins are added for the plain
cross-part + fan-out shapes.

**D3 — Run the stale-fixture-refresh rider: YES.** The epic leans yes and BACKLOG lists it
as a candidate rider decided at this spec. We hold a live license and are running a
live-capture session anyway; running the refresh now ends the committed corpus
script-reproducible in one pass. Own commit, reviewed diff, per the BACKLOG entry. The
`quoted_owner_formula` reclassification (two attrs move design-attr → computed) is a
snapshot-content change reflecting already-landed post-Item-7 behavior, not a code change,
so it is in scope; it is reviewed deliberately and filed if it turns out to hide a real
question rather than confirmed.

**D4 — High-value secondary subset = the eight shapes the epic Item 1 §3 names, plus the
adversarial-pass rows (Style-E / quoted-return, quoted-output param, bool/string/enum
EP).** The remaining D6 shapes are FILED to the fixture-gap register (pointer to discovery
§D6), with rationale:
- *Selective import of quoted names* — parser/import concern, no value-provision or
  diagnostic-truth leverage for Items 2/5. FILED.
- *Standalone package-level instance whose `:>>` literals feed a def-owned calc's
  bindings* — a value-provision variant, but a fourth path beyond the three the headline
  pins; adds fixture surface without moving Item 2's before/after. FILED (noted as an
  Item-2 follow variant).
- *Constraint def consuming a defaulted param* — Item 4 (constraint truth) territory; the
  headline already carries an assert constraint with an unbound-defaulted binding. FILED to
  Item 4's scope.
- *Consumer calc in a part-usage body reaching a subtype-only calc-derived attribute
  through a usage-level retyped child* — structurally covered by the headline's retype +
  the extended twolevel; the standalone variant FILED if not naturally covered at capture.

**D5 — Per-shape behavior labels are determined empirically at capture, not pre-judged.**
Following the `ife_plant` precedent (capture current-incomplete first; label
correct/degraded/diagnostic from the observed snapshot). The spec requires a pinning test
per shape; the plan records the observed label. This is the R4-flavored discipline applied
to fixtures — the "before" is measured, not assumed.

## Deliberately-touched baseline set (everything else byte-identical)

- **New**: `tests/fixtures/plant_values/` (snapshot + pipeline baseline outputs);
  `tests/fixtures/plant_value_shapes/` (snapshot; baseline outputs only if it builds a
  full graph); `tests/fixtures/deep_cross_scope_probe/extraction_snapshot.json` (new).
- **Re-captured (reviewed diff)**: `spec_chain_twolevel` (extension); `wi014_toy`,
  `self_named_binding_trap`, `quoted_owner_formula` (rider — own commit).
- **Capture-script registration**: additions to `capture_extraction_snapshots.py` and, for
  fixtures with committed graph baselines, `capture_pipeline_baselines.py`.
- **Everything else** (`catf_mfe`, `solar_battery`, `sample_model`, `ife_plant`,
  `attr_expr_probe`, `chain_spike`, the Item-10 companion fixtures, etc.): byte-identical.

## Open Questions / Deferred to design

- **Headline-fixture shape layout** — whether the assert constraint, the bare `part :>>`
  block, and the usage-level retype all sit on one plant usage or split across sibling
  usages; whether the cross-part half needs a separate package (as `ife_plant` does with
  `IfePlantSubsystems`). Deferred to the plan/execution; the SysML must parse and trip V11
  with the three mechanisms, however arranged.
- **Whether `deep_cross_scope_probe` captures full-pipeline or extraction-only** — depends
  on whether it builds a graph without an unsupported binding type. Determined at capture.
- **Whether `plant_value_shapes` needs to split into more than one fixture** — depends on
  whether the quoted-enum, Style-E, and 5-deep-chain shapes co-exist in one parseable
  model. Determined at capture.
- **Exact offender-set contents for `plant_values`'s V11 pin** — the precise
  `(module, input, missing_key)` tuples are read from the captured graph, not predicted
  here (independently-anchored, per R1).

## Known limitation

The fusion-tea exemplar files (`ife_plant.sysml`, `hif_plant.sysml`, `hif_driver.sysml`,
`ife_cost_parameters.sysml`) live outside this session's allowed working directory and
could not be read directly. The fixture shapes are copied from discovery §D6, which
carries each shape with its fusion-tea `file:line` exemplar, and from the existing
`ife_plant` / `spec_chain_twolevel` fixtures (already shaped after those files). At
execution, when the live-capture session runs, spot-verify the authored shapes against the
live fusion-tea files so the fixtures are copied from reality, not from the register's
paraphrase.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_pipeline_truth.md` (Item 1; R1–R4; SC-A/B)
- **Required Reading:** discovery register §D6 + §D1-F6
  (`.project/research/20260706_pipeline-truth-discovery.md`);
  `docs/architecture/reference/25-hierarchy-resolver.md` (the epic cites it as
  `25-hierarchy-extraction.md` — renamed; same doc); `docs/architecture/modeling-assumptions.md`
  §5; memory note `plant-idiom-fixtures`; BACKLOG stale-fixture-refresh + CONSTRAINT-SILENCE.
- **Fusion-tea exemplars (register-cited, not directly readable this session):**
  `~/1cfe/fusion-tea/models/{ife_plant,hif_plant,hif_driver,ife_cost_parameters}.sysml`.
- **Research:** `.project/research/20260706_pipeline-truth-discovery.md`
- **Downstream:** Item 2 (`whole-plant-resolution`), Item 5 (`silent-failure-hardening`),
  Item 4 (`subtype-enumeration`, assert-constraint substrate), Item 9 (agentic-mbse impact).
- **Design:** none — this item is fixtures + captures; it goes spec → plan → implement
  (no `/_my_design`).

---

**Next Steps:** After approval, proceed to `/_my_plan` (the Item-8 plant-fixtures plan is
the template). No `/_my_design` — fixtures + captures carry no design surface.
