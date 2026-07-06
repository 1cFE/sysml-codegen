# Spec: Plant-Idiom Literal Pre-Fill (SC-5 stage 1)

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-05
**Complexity:** HIGH
**Branch:** upstream-findings-epic
**Epic Item:** UPSTREAM-FINDINGS Item 9

---

## Problem

Literal values that the model states plainly never reach the generated input JSONs
for plant-idiom models. Two holes cause it, and one latent bug blocks the item that
follows.

**Hole 1 — plain-usage `:>>` overrides are dropped at extraction.** A `:>>` override
on a *plain* (non-`part redefines`) part usage is never captured. `extract_design_overrides`
(`hierarchy_resolver.py:187`) guards on `usage.owned_redefinitions`, which is non-empty
only for `part redefines` usages. A plain typed usage like
`part assembly : 'Widget Assembly' { :>> widget.base_cost = 50.0; }` has an empty
`owned_redefinitions` on the usage itself — its `:>>` lives on a member ReferenceUsage —
so the whole usage is skipped and the `50.0` vanishes. This is SC-5 mechanism C, and
ife_plant shape 5 (`baseline_plant :>> capacity_factor = 0.95`) pins the drop today
(`test_ife_plant.py::test_shape5_plain_usage_override_dropped`).

**Hole 2 — def-attribute literals don't pre-fill CalcUsage entry points.** The
literal-value-propagation mechanism (`_find_literal_redefinition`, `graph_builder.py:1120`,
doc 18 / REQ-LVP) backfills entry-point defaults from LITERAL `:>>` redefinitions — but
it is called **only** from the aggregation module builder (`_build_aggregation_module`,
REQ-LVP-02/03). A CalcUsage input whose value comes from a `:>>` literal redefinition
gets no backfill: it classifies to a bare, valueless entry point. Since Item 7 landed
the V11 params-coverage check, a valueless-but-wired entry point is now a **hard
generation abort**, not silent breakage. Two committed fixtures abort on exactly this:
`alias_agg_probe` and `issue22_model` (both `cost_model.base_cost`), pinned green in
`test_uncovered_params.py` and `test_alias_agg_probe_generation.py`.

**Latent bug — shared mutable `BindingInfo`.** `_create_virtual_calc_usage` does
`bindings=list(template.bindings)` (`usage_extractor.py:393`) — a shallow copy. Every
virtual instance created from one template shares the same `BindingInfo` objects. Any
per-instance binding rewrite corrupts sibling instances silently. This is harmless today
(nothing rewrites per-instance) but is a hard precondition for Item 10's per-instance
rewrite. It is cheap and safe to fix here, where the fixtures to prove it already exist.

The evidence base for why this matters: the WI-015 anchor showed fresh IFE generation
produced `ife_plant_params.json` with 2/16 keys and `hif_driver_params.json` as `{}`.
The checked-in fusion-tea inputs are hand-filled. The plant idiom gates fusion-tea's MFE
epic (SC-5), and Item 8 landed the fixtures that make this item's progress reviewable as
baseline diffs.

## The spec-time question: does scope 1+2 fix the `base_cost` class? — YES

Item 7's handoff asked whether this item's scope closes the bare-name
`:>> widget.base_cost = 50.0` redefinition class that V11 aborts on (`alias_agg_probe`,
`issue22_model`), and if so, flips `test_alias_agg_probe_aborts_with_v11...` back to clean
generation.

**Answer: yes, this is Item 9's class — literal pre-fill, not channel wiring.** Traced
against the fixtures and code:

- The value is a **literal** (`50.0` / `100.0`), captured by a `:>>` redefinition. No
  calc output, no cross-part edge is involved. That is definitionally literal pre-fill
  (this item), not the gamma→lcoe channel wiring of Item 10.
- `assembly : 'Widget Assembly'` is a **plain typed usage** (`design.sysml:6`), so its
  `:>>` is dropped today by Hole 1. Scope 1 (relax the guard) captures it. The redefinition
  is **deep-path** (`widget.base_cost`): `attribute_name='base_cost'`,
  `target_path=['widget','base_cost']`, `is_deep_path=True`, `literal_value=50.0` — the
  deep-path capture machinery already exists (REQ-HR-03), only the guard blocks the plain
  usage from reaching it.
- Scope 2 (propagate to CalcUsage entry points) then backfills the `...widget__cost_model.base_cost`
  entry point with `50.0`, so V11 no longer sees a valueless wired input, and
  `alias_agg_probe` / `issue22_model` generate cleanly.

**The one real design risk, called out here so design owns it:** the propagation match
must handle the **deep-path** target. The existing `_find_literal_redefinition` matches a
`(part_usage, attr)` pair against `redef.attribute_name` and the *owning* usage's name.
For `:>> widget.base_cost` the owning usage is `assembly`, but the target part is `widget`
(from `target_path[0]`). Scope 2 must match on the deep-path target, not the owning
usage's last segment. This stays entirely within literal pre-fill — no Item 10 alias/channel
machinery is needed. **Contingency:** if design discovers the match genuinely requires
Item 10's per-instance alias resolution (it should not), that is a recorded scope boundary,
not a silent punt — but the plan of record, corroborated by three handoff artifacts
(Item 7 release notes V11 table, `test_alias_agg_probe_generation.py` docstring,
`test_uncovered_params.py:15-16`), is that Item 9 flips both fixtures.

**What Item 9 does NOT flip (stays V11-pinned → Item 10):** `catf_mfe` and ife_plant
shape 4 (`cryo_load.magnet_volume`) are cross-part **CHAIN** references to a calc output
(EXPOSE reaching `tf_coil.volume`), not literals. Channel wiring, Item 10.

## Success Criteria

- [ ] **Plain-usage `:>>` overrides are captured.** ife_plant shape 5
      (`baseline_plant :>> capacity_factor = 0.95`) is captured at extraction; the drop
      pin `test_shape5_plain_usage_override_dropped` flips (rewritten to assert capture),
      reviewed as a snapshot diff.
- [ ] **Def-attribute literals pre-fill CalcUsage entry points.** The ife_plant input
      JSONs pre-fill the plant-def literals (the 16 def-declared literals reach params;
      WI-015 evidence base: previously 2/16 and 0 keys) — a valueless-but-wired CalcUsage
      entry point that has a discoverable `:>>` LITERAL default is filled, not left `None`.
- [ ] **`alias_agg_probe` and `issue22_model` generate cleanly.** V11 no longer aborts:
      `collect_uncovered_params` returns empty for both (the `base_cost` pins in
      `test_uncovered_params.py` flip), and `test_alias_agg_probe_aborts_with_v11...` is
      rewritten to assert a clean, importable, `ast.parse`-valid package (restoring the
      REQ-NC-08 file-parse coverage Item 5 deferred). issue22 gains equivalent E2E coverage.
- [ ] **Shared-`BindingInfo` aliasing is fixed and regression-tested.** Two virtual
      instances from one template hold independent `BindingInfo` objects: mutating one
      never affects the other. A dedicated regression test proves it.
- [ ] **Existing 4 committed baselines byte-identical**, EXCEPT: the plant-fixture
      baselines (ife_plant — known-incomplete pins flip, reviewed diffs) and the
      V11-tracked fixtures whose class lands here (`alias_agg_probe`, `issue22_model`).
      `catf_mfe` stays V11-pinned (Item 10). The deep-copy fix alone churns no baseline
      (prove: byte-exact suite).
- [ ] **Requirement IDs, verification-matrix rows, and reference docs move with the code**
      (R1): doc 18 (extend REQ-LVP to the classifier path), doc 25 / hierarchy-resolver
      (guard relaxation + self-named leaf-match), doc 12 (BindingInfo deep-copy precondition
      for VBR), modeling-assumptions §5 as applicable.
- [ ] **agentic-mbse impact recorded** (R2) in the close-out.

## Known Requirements

**Scope 1 — capture `:>>` on plain part usages**

- **[HARD]** `extract_design_overrides` (`hierarchy_resolver.py:167`) SHALL scan `:>>`
  member redefinitions on plain part usages, not only `part redefines` usages — i.e. the
  `owned_redefinitions` guard at line 187 SHALL NOT skip a usage whose *members* carry
  `:>>` overrides. Forced by SC-5 mechanism C: the value is otherwise unreachable.
  (New: **REQ-HR-08**.)
- **[HARD]** Relaxing the guard SHALL NOT capture spurious redefinitions that churn the
  existing 4 baselines. `catf_mfe` carries many plain usages — verify its committed
  baseline is byte-identical (or its churn is a reviewed, justified V11-class flip, not an
  accident). (Verification obligation on REQ-HR-08.)
- **[NEED]** Self-named bindings (`in availability = availability`, SC-5 mechanism D) are
  rescued via the leaf-match rewrite so they resolve to the outer attribute rather than
  the calc's own parameter. The `self_named_binding_trap` fixture (Item 8) is the
  substrate; its current degenerate self-reference baseline is the before-state.
  (New: **REQ-HR-09**. Design decides whether the full rescue lands here or the rewrite
  hook is staged for Item 10 — deferred to design.)

**Scope 2 — propagate RedefinitionData literals to CalcUsage entry-point defaults**

- **[HARD]** A CalcUsage entry point whose `default_value` would be `None` SHALL be
  backfilled from a matching LITERAL `:>>` redefinition — the classifier-path mirror of
  REQ-LVP-05 (which fires only inside `_build_aggregation_module` today). Found literal
  keeps the module compilable; no literal leaves `default_value=None` as before.
  (New: **REQ-LVP-09**.)
- **[HARD]** The propagation match SHALL handle **deep-path** redefinitions
  (`:>> widget.base_cost = 50.0`): match on the deep-path target
  (`target_path`), not the owning usage's last segment. This is the mechanism that flips
  `alias_agg_probe` / `issue22_model`. (New: **REQ-LVP-10**.)
- **[INFERRED]** Reuse the existing `_find_literal_redefinition` / `usage_type_map`
  machinery (doc 18) rather than inventing a parallel matcher — "compute once, look up
  thereafter" (R1). Extend it; do not fork it.

**Scope 3 — fix shared mutable `BindingInfo`**

- **[HARD]** `_create_virtual_calc_usage` (`usage_extractor.py:393`) SHALL deep-copy each
  `BindingInfo` so no two virtual instances share a binding object. Precondition for
  Item 10's per-instance rewrite (doc 12 / REQ-VBR). (New: **REQ-VBR-08**.)
- **[HARD]** The deep-copy SHALL NOT change any generated output — prove byte-exact suite
  (R3). It is a latent-corruption fix, not a behavior change.

**Cross-cutting (R1)**

- **[HARD]** ComputationGraph is the sole generation input; no drive-by schema field.
  This item touches extraction and the entry-point classifier/backfill, not the graph
  schema — keep it that way.
- **[HARD]** New behavior lands with real fixtures (Item 8's), never mocks. Matrix rows
  for every new REQ; the V-rule set is unchanged (V11 is the latest; this item adds no
  V-rule — it *satisfies* V11 for the literal class).

## Non-Goals

- **Cross-part channel wiring (Item 10).** The gamma→lcoe edge, consumer-scoped alias
  lookup, per-instance binding *rewrite through the specialization chain*, and PartDef-level
  EXPOSE with instance-scoped keys are all Item 10. This item only fixes the *shared-object*
  precondition (scope 3), it does not perform the rewrite.
- **Flipping `catf_mfe` / ife_plant shape 4** — cross-part CHAIN, Item 10.
- **Wiring ife_plant shape 2** (`Shielded Core :>> scope_multiplier`) — captured but has
  no consumer; nothing reads it, so literal pre-fill creates no value-bearing entry point.
  It stays captured-but-unwired unless design finds a consumer (it should not).
- **Alias *emission* into generated output (Item 11).**
- **Constraint execution, EXPOSE_COMPUTED** — pre-existing backlog, untouched.

## Open Questions / Deferred to design

- **Self-named-binding rescue depth (REQ-HR-09).** Whether the leaf-match rewrite fully
  rescues `in availability = availability` here, or only the extraction-side hook lands and
  the per-instance rewrite completes in Item 10. The epic lists the rescue under Item 9
  scope 1 ("also rescues self-named bindings via the leaf-match rewrite"), but the actual
  rewrite is Item 10 machinery. Design decides the seam. The trap fixture pins the
  before-state either way.
- **Deep-path match site.** Whether REQ-LVP-10's deep-path matching extends
  `_find_literal_redefinition` in place or adds a sibling helper for the classifier path.
  Mechanism choice — deferred to design.
- **Entry-point backfill insertion point.** Whether scope 2 backfills inside
  `_classify_entry_points` (`graph_builder.py:387`, Strategy 2/3) or as a post-classify
  pass over `entry_points`. Deferred to design; doc 06 (entry-point-classifier) is the home.
- **`issue22_model` E2E coverage.** issue22 has only a collector pin today
  (`test_uncovered_params.py`), no E2E generation test. Whether to add a full E2E test or
  extend the collector pin flip — deferred to design (a test-coverage call, not a scope
  change).

---

## agentic-mbse impact (R2 — to be finalized at close-out)

Expected, pending implement-time confirmation:

- **New supported shape to teach:** plain-usage `:>>` literal overrides and def-attribute
  literal pre-fill are now honored — MODELING_GUIDE / sysml-conventions should present the
  plant-idiom literal pattern (`part x : Type { :>> nested.attr = <literal>; }`) as
  supported (executed in Item 12, once Item 10 also lands).
- **Self-named-binding check (register A-1, Item 12 Level-2 FAIL check):** REQ-HR-09's
  rescue changes what the auditor should say about `in availability = availability`. If
  rescued, the check becomes advisory (the pattern now resolves correctly); if only staged,
  the check stays a FAIL until Item 10. Record which, with the `self_named_binding_trap`
  fixture as the negative reference.
- **No new checker script lands in this item** unless the self-named rescue completes here;
  the accumulated list executes in Item 12.

Full "agentic-mbse impact" list is completed in the close-out per R2 (possibly "none new"
beyond the above).

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_upstream_findings.md` (Item 9 + R1/R2/R3 + Item 10)
- **Required Reading:**
  - `~/1cfe/fusion-tea/.project/reports/2026-07-05-upstream-findings-register.md` (findings register)
  - `.project/research/20260705_upstream-findings-deep-research.md` (SC-5 section — the four mechanisms)
  - `docs/architecture/modeling-assumptions.md` (supported-subset contract; §5, Validation Rules V1–V11)
- **Item 8 substrate (diff base):** `tests/fixtures/{ife_plant,wi014_toy,self_named_binding_trap}/`,
  `tests/conformance/test_ife_plant.py`, `.project/active/plant-fixtures/plan.md`
- **Item 7 landscape:** `tests/conformance/test_alias_agg_probe_generation.py`,
  `tests/unit/test_uncovered_params.py`, `.project/active/warning-reconciliation/release-notes.md`
- **Code:** `extraction/hierarchy_resolver.py` (guard, `extract_design_overrides`),
  `extraction/usage_extractor.py:393` (BindingInfo), `resolution/graph_builder.py`
  (`_find_literal_redefinition`, `_classify_entry_points`)
- **Docs to update:** `reference/18-literal-value-propagation.md`,
  `reference/25-hierarchy-resolver.md`, `reference/12-virtual-binding-rewrite.md`,
  `reference/06-entry-point-classifier.md`, `docs/architecture/verification-matrix.md`
- **Design:** `.project/active/plant-prefill/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_design`.
