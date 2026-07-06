# Spec: Plant-Idiom Literal Pre-Fill (SC-5 stage 1)

**Status:** Draft (revised after spec-review — `spec-review.md`, verdict Revise)
**Owner:** Reid W
**Created:** 2026-07-05
**Complexity:** MEDIUM (revised down from HIGH — the empirical probe collapsed scope 2)
**Branch:** upstream-findings-epic
**Epic Item:** UPSTREAM-FINDINGS Item 9

---

## Problem

Literal values that a plant-idiom model states plainly don't reach the generated input
JSONs. One extraction hole causes it. One active bug threatens the item that follows.

**The hole — plain-usage `:>>` overrides are dropped at extraction.** A `:>>` override on
a *plain* (non-`part redefines`) part usage is never captured. `extract_design_overrides`
(`hierarchy_resolver.py:187`) guards on `usage.owned_redefinitions`, which is non-empty
only for `part redefines` usages. A plain typed usage like
`part assembly : 'Widget Assembly' { :>> widget.base_cost = 50.0; }` has an empty
`owned_redefinitions` on the usage itself — its `:>>` lives on a member ReferenceUsage — so
the whole usage is skipped and the `50.0` vanishes. This is SC-5 mechanism C. It has two
consequences today:

- **ife_plant shape 5** (`baseline_plant :>> capacity_factor = 0.95`) is dropped; only the
  def default (0.90) survives (`test_ife_plant.py::test_shape5_plain_usage_override_dropped`).
- **`alias_agg_probe` / `issue22_model`** (`cost_model.base_cost`) generate a wired-but-
  valueless entry point, which Item 7's V11 params-coverage check now hard-aborts on
  (pinned in `test_uncovered_params.py` and `test_alias_agg_probe_generation.py`).

**The active bug — shared mutable `BindingInfo`.** `_create_virtual_calc_usage` does
`bindings=list(template.bindings)` (`usage_extractor.py:393`) — a shallow copy, so every
virtual instance from one template shares the same `BindingInfo` objects. This is NOT
dormant: `_rewrite_virtual_bindings` (`pipeline_builder.py:190`) already mutates
`BindingInfo` in place per instance (its docstring, line 196). It is byte-exact today only
because no committed fixture has multiplicity→sibling instances whose overrides *diverge*
over a shared object. Once the guard relaxes (below) and deep-path overrides feed the
rewrite over a multiplicity part like `widget [3]`, the shared object becomes an active
correctness hazard **in this item**, and it is a hard precondition for Item 10's per-instance
rewrite.

The evidence base: the WI-015 anchor showed *fresh* fusion-tea IFE generation produced
`ife_plant_params.json` with 2/16 keys and `hif_driver_params.json = {}`. Those are the
*real* models before Items 4/5/7. Item 8's ife_plant **fixture** baseline was captured
after Items 4/5/7, so it already pre-fills the def-declared literals (see the scope-2
finding below); this item closes the remaining plain-usage-override gap and hardens the
rewrite for Item 10.

## The spec-time question, answered in two parts

**Part 1 — is the `base_cost` class Item 9's? YES, and it's settled.** The value is a
literal (`50.0` / `100.0`) captured by a `:>>` redefinition — no calc output, no cross-part
edge. That is literal pre-fill (this item), not the channel wiring of Item 10.

**Part 2 — which mechanism flips it? The existing binding rewrite, scope 1 alone.** This is
the correction the review forced. The flip does **not** go through a new graph-layer
backfill. `_rewrite_virtual_bindings` (`pipeline_builder.py:190`) already:

- builds an override index from `design_overrides`, handling **deep-path** overrides
  explicitly (line 206: `is_deep_path and len(target_path) >= 2` → key
  `(owning_qn__intermediate, leaf)`), and
- rewrites the matching virtual-instance binding to `BindingType.LITERAL` with the literal
  value, clearing `source_path` (lines 248–252).

For `:>> widget.base_cost = 50.0` the override is deep-path (`target_path=['widget','base_cost']`,
`literal_value=50.0`) and the `base_cost` binding's leaf is `base_cost` — exactly the shape
that branch matches. So relaxing the guard rewrites the binding to a literal *before*
`base_cost` ever becomes a valueless entry point.

**Orchestrator probe (live license, recorded):** relaxing the `owned_redefinitions` guard
**alone** — no other change — `alias_agg_probe` generates cleanly end-to-end (no V11 abort)
and `system_design.json` mints
`"AliasAggProbeDesign__plant__assembly__widget__cost_model__base_cost": 50.0`. Guard
restored after the probe. `issue22_model` is the same shape (`:>> widget.base_cost = 100.0`
on a plain typed usage) and is expected to flip identically — **design confirms it with the
same isolated-probe method.**

**Consequence: scope 2 is cut.** See the next section.

## Scope-2 finding: no residual gap — the LVP entry-point backfill is not needed

The original spec proposed scope 2 (extend `_find_literal_redefinition` to the CalcUsage
classifier path) to pre-fill the ife_plant 16 def-declared literals. Ruling 1 asked whether
those literals are *already* filled post-Items-4/5/7. They are.

**Evidence (committed `baseline_outputs/ife_plant/computation_graph.json` entry-point
groups):** every def-declared literal is already pre-filled — `bank_energy=1e7`,
`efficiency=0.1`, `availability=0.7`, `blanket_energy_multiple=1.2`, `discount_rate=0.08`,
`gain=500.0`, `frequency=0.2`, and the rest of the ~14 Hawker parameters plus
`net_power_target`-class constants, all as `usage_literal` entry points with non-null
`default_value`. The **only** null entry point is `magnet_volume` — shape 4, the cross-part
CHAIN → Item 10.

So the def-literal pre-fill criterion is already met by the Item 8 baseline. There is no
def-literal class still landing valueless, hence **no residual gap for scope 2 to close.**
Scope 2 (REQ-LVP-09/10) is removed from this item. If design's issue22 re-probe or the
byte-exact sweep surfaces a *specific* def-literal class that is still valueless (none is
known), scope 2 is reinstated narrowed to exactly that class and no wider.

## Scope (revised)

1. **Capture plain-usage `:>>` overrides** — relax the `owned_redefinitions` guard, filtered
   to LITERAL RHS. The real fix; routes the flip through the existing rewrite.
2. ~~Propagate RedefinitionData literals to CalcUsage entry-point defaults~~ — **CUT** (no
   residual gap; see above).
3. **Fix shared mutable `BindingInfo`** (deep-copy) — active-hazard fix for multiplicity-part
   overrides *this item*, and Item 10 precondition.

## Success Criteria

The **executable gate** is the ife_plant fixture's input-JSON / baseline diff (license-free,
committed). The real fusion-tea IFE run is opportunistic evidence, recorded if run
(Item 3 D6 precedent) — it needs a live license (blocker).

- [ ] **Plain-usage `:>>` overrides are captured.** ife_plant shape 5
      (`baseline_plant :>> capacity_factor = 0.95`) reaches params as `0.95`, replacing the
      dropped-to-def-default `0.90`. Item 8's `test_shape5_plain_usage_override_dropped`
      (`test_ife_plant.py:161`) is rewritten from "asserts absence" to "asserts capture,"
      reviewed as a baseline diff.
- [ ] **`alias_agg_probe` and `issue22_model` generate cleanly.** The exact pin flips:
  - [ ] `test_uncovered_params.py::test_collector_pins_alias_agg_probe` — `[("base_cost","cost_model")]` → `[]`
  - [ ] `test_uncovered_params.py::test_collector_pins_issue22_model` — `[("base_cost","cost_model")]` → `[]`
  - [ ] `test_alias_agg_probe_generation.py::test_alias_agg_probe_aborts_with_v11...` —
        rewritten from raises-V11 to a clean, importable, `ast.parse`-valid package
        (restores the REQ-NC-08 file-parse coverage Item 5 deferred).
  - [ ] issue22 gains an equivalent E2E clean-generation assertion (design decides: a new
        E2E test or an extension of the collector pin — a test-coverage call, not scope).
- [ ] **Shared-`BindingInfo` divergent-sibling case is fixed and regression-tested.** The
      test asserts the *rewrite* respects the instance boundary: two virtual instances of
      one template, given **different** override matches, produce independent results — not
      merely that they hold distinct objects.
- [ ] **Existing 4 committed baselines byte-identical**, EXCEPT the plant-fixture baseline
      (ife_plant — shape-5 flip, reviewed diff) and the V11-tracked fixtures whose class
      lands here (`alias_agg_probe`, `issue22_model`). `catf_mfe` stays V11-pinned (Item 10).
      The deep-copy fix alone churns no baseline (prove: byte-exact suite).
- [ ] **CHAIN/EXPRESSION plain-usage overrides stay inert; no bare-name crash.** A
      relaxed-guard capture of a CHAIN override (Item 10's job) does not rewrite a binding
      here, and a self-named / bare-name `source_path` does not raise (see requirements).
- [ ] **REQ IDs, verification-matrix rows, reference docs move with the code** (R1): doc 25 /
      hierarchy-resolver (guard relaxation + literal filter), doc 12 / virtual-binding-rewrite
      (BindingInfo deep-copy + bare-name safety), modeling-assumptions §5 as applicable. Doc 18
      (LVP) is **not** touched — scope 2 is cut.
- [ ] **agentic-mbse impact recorded** (R2) in the close-out.

## Known Requirements

**Scope 1 — capture `:>>` on plain part usages (LITERAL-filtered)**

- **[HARD]** `extract_design_overrides` (`hierarchy_resolver.py:167`) SHALL scan `:>>`
  member redefinitions on plain part usages, not only `part redefines` usages — the
  `owned_redefinitions` guard (line 187) SHALL NOT skip a usage whose *members* carry `:>>`
  overrides. (New: **REQ-HR-08**.)
- **[HARD]** Plain-usage overrides captured by REQ-HR-08 SHALL be filtered to **LITERAL** RHS.
  CHAIN/EXPRESSION overrides on plain usages (e.g. `catf_mfe`'s cross-part refs, ife_plant
  shape 4) SHALL NOT enter the literal-rewrite path — that is Item 10's job. Rationale:
  `_rewrite_virtual_bindings` rewrites CHAIN bindings too (line 253); un-filtered capture
  would let this item do a slice of Item 10 early and/or churn a baseline this item promises
  stays byte-identical. The filter applies to the *newly-scanned plain usages only* — the
  existing `part redefines` path keeps all RHS types (unchanged behavior). (Part of REQ-HR-08.)
- **[HARD]** `_rewrite_virtual_bindings` SHALL NOT raise on a bare-name `source_path`
  (`pipeline_builder.py:242`). Today that raise is unreachable only because `override_index`
  is empty for these models (early return, line 215); once REQ-HR-08 populates the index, a
  self-named `in availability = availability` binding (bare-name `source_path`) can reach it.
  Replace the raise with a skip-with-DEBUG. (New: **REQ-VBR-09**.)

**Scope 3 — fix shared mutable `BindingInfo`**

- **[HARD]** `_create_virtual_calc_usage` (`usage_extractor.py:393`) SHALL deep-copy each
  `BindingInfo` so no two virtual instances share a binding object. Required for correctness
  of multiplicity-part overrides *in this item* (once REQ-HR-08 feeds deep-path literals into
  the per-instance rewrite over `widget [3]`-style parts), and a precondition for Item 10.
  (New: **REQ-VBR-08**.)
- **[HARD]** The deep-copy SHALL NOT change any generated output — prove byte-exact suite
  (R3). It is a corruption-prevention fix, not a behavior change.

**Cross-cutting (R1)**

- **[HARD]** ComputationGraph is the sole generation input; no drive-by schema field. This
  item touches extraction and orchestration-phase binding rewrite, not the graph schema.
- **[HARD]** New behavior lands with real fixtures (Item 8's), never mocks. Matrix rows for
  every new REQ; the V-rule set is unchanged (this item *satisfies* V11 for the literal
  class, it adds no V-rule). "Extend, don't fork" — reuse `_rewrite_virtual_bindings`'
  deep-path matching; do not add a parallel matcher.

## Non-Goals

- **Cross-part channel wiring (Item 10).** The gamma→lcoe edge, consumer-scoped alias
  lookup, per-instance binding *rewrite through the specialization chain*, and PartDef-level
  EXPOSE with instance-scoped keys. This item only fixes the shared-object precondition
  (scope 3) and the bare-name crash-safety (REQ-VBR-09).
- **CHAIN/EXPRESSION plain-usage override handling** — captured-but-inert here at most;
  their actual rewrite is Item 10.
- **Self-named-binding *rescue* (mechanism D).** Cut from this item. The research is explicit
  that rescuing `in availability = availability` (resolving it to the outer attribute rather
  than the calc's own parameter) needs Item 10's per-instance rewrite path
  (`...deep-research.md:160`). This item only makes the path *crash-safe* on the bare-name
  source (REQ-VBR-09); the rescue itself is an **Item 10 handoff**. The `self_named_binding_trap`
  fixture's current degenerate-self-reference baseline is preserved as the before-state.
- **Flipping `catf_mfe` / ife_plant shape 4** — cross-part CHAIN, Item 10.
- **Wiring ife_plant shape 2** (`Shielded Core :>> scope_multiplier`) — captured; no consumer
  is known, so literal pre-fill creates no value-bearing entry point for it.
- **Scope-2 LVP backfill** — cut (no residual gap).
- **Alias emission (Item 11), constraint execution, EXPOSE_COMPUTED** — untouched.

## Open Questions / Deferred to design

- **LITERAL-filter site (REQ-HR-08).** Whether the filter lives in `extract_design_overrides`
  (skip non-LITERAL members on plain usages) or in `_rewrite_virtual_bindings` (only act on
  LITERAL overrides from plain usages). Design chooses; the *outcome* (CHAIN/EXPRESSION plain
  overrides stay inert) is HARD.
- **issue22 E2E coverage form.** New E2E test vs. collector-pin extension — a test-coverage
  call.
- **Deep-copy depth (REQ-VBR-08).** `copy.deepcopy` per `BindingInfo` vs. field-wise copy of
  the mutable fields the rewrite touches (`binding_type`, `literal_value`, `source_path`).
  Design picks the minimal correct copy; the byte-exact suite is the guard.

---

## agentic-mbse impact (R2 — finalized at close-out)

Expected, pending implement-time confirmation:

- **New supported shape to teach:** plain-usage `:>>` **literal** overrides are now honored —
  MODELING_GUIDE / sysml-conventions should present `part x : Type { :>> nested.attr = <literal>; }`
  as supported (executed in Item 12, once Item 10 also lands).
- **Self-named-binding check (register A-1, Item 12 Level-2 FAIL):** unchanged by this item —
  the rescue is deferred to Item 10, so the check stays a FAIL/advisory against
  `self_named_binding_trap` until then. Recorded as an Item 10 handoff.
- **No new checker script lands here.** The accumulated list executes in Item 12.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_upstream_findings.md` (Item 9 + R1/R2/R3 + Item 10)
- **Spec review:** `.project/active/plant-prefill/spec-review.md` (verdict Revise; this
  revision resolves L1-1/L1-2/L1-3/L2-1/L2-2/L2-3/L3-1/L3-2/L3-3/L4-1/L5-1)
- **Required Reading:**
  - `~/1cfe/fusion-tea/.project/reports/2026-07-05-upstream-findings-register.md`
  - `.project/research/20260705_upstream-findings-deep-research.md` (SC-5 — four mechanisms; D → Item 10)
  - `docs/architecture/modeling-assumptions.md` (§5, Validation Rules V1–V11)
- **Item 8 substrate (diff base):** `tests/fixtures/{ife_plant,wi014_toy,self_named_binding_trap}/`,
  `tests/conformance/test_ife_plant.py`, `.project/active/plant-fixtures/plan.md`
- **Item 7 landscape:** `tests/conformance/test_alias_agg_probe_generation.py`,
  `tests/unit/test_uncovered_params.py`, `.project/active/warning-reconciliation/release-notes.md`
- **Code:** `extraction/hierarchy_resolver.py:167,187` (guard / `extract_design_overrides`),
  `orchestration/pipeline_builder.py:190` (`_rewrite_virtual_bindings` — the mechanism that
  fires; deep-path branch line 206, bare-name raise line 242),
  `extraction/usage_extractor.py:393` (shared `BindingInfo`)
- **Docs to update:** `reference/25-hierarchy-resolver.md`,
  `reference/12-virtual-binding-rewrite.md`, `docs/architecture/verification-matrix.md`
  (REQ-HR-08, REQ-VBR-08, REQ-VBR-09). Doc 18 (LVP) NOT touched.
- **Design:** `.project/active/plant-prefill/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_design`.
