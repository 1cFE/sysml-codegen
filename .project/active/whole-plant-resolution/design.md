# Design: Whole-Plant Cross-Part Value Resolution (PIPELINE-TRUTH Item 2)

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-06
**Branch:** pipeline-truth-epic
**Base commit:** e73a12f

## Overview

Carry each subsystem-attribute value the model already supplies (a subtype-def
literal, an override block, a dotted usage override, or an in-part redefinition)
into the plant-calc input that reads it, so the ten fusion-tea V11 offenders resolve
to filled entry points instead of valueless ones. The mechanism is **value-fill**:
materialize the supplied literal onto the source attribute as a design attribute
keyed by its source QN, then let the existing design-attribute resolution path carry
it to the consumer.

## Related Artifacts

- **Spec:** `.project/active/whole-plant-resolution/spec.md` (the contract — four
  mechanism targets (a)/(b)/(c)/(d), offender arithmetic 10 → zero, EP-keying-by-source-QN
  [HARD], the new plain-value precedence REQ, the SC-3 runner, the (d) escalation rule)
- **Spec review:** `.project/active/whole-plant-resolution/spec-review.md`
- **Epic:** `.project/backlog/epic_pipeline_truth.md` (Item 2; SC-A/SC-B; the mechanism-decision
  and 2-day-limit risk rows)
- **Before-state fixtures (Item 1):** `tests/fixtures/plant_values/` (a/b/c),
  `tests/fixtures/plant_value_shapes/` (`'Flow Sub'` = (d), DEGRADED),
  `tests/fixtures/spec_chain_twolevel/` (value-carrying cross-part + same-name fan-out)
- **Required Reading:** `reference/18-literal-value-propagation.md` (the LVP mechanism this
  item extends), `reference/11-analysis-backtracker.md`,
  `reference/12-virtual-binding-rewrite.md`, `reference/25-hierarchy-resolver.md`,
  `reference/07-graph-assembly.md`; RN-10 (`.project/active/cross-part-wiring/release-notes.md`);
  memory `cross-part-binding-v11-fallthrough`, `multihop-expose-offline-parity`, `plant-idiom-fixtures`
- **Research:** `.project/research/20260706_pipeline-truth-discovery.md`

---

## Research Findings

### Where the ten offenders die today (read from the real dispatch)

A cross-part binding like `in driver_efficiency = driver.efficiency` reaches the
backtracker's `_resolve_binding_via_registry` (`dependency_backtracker.py:520`). It
runs the CHAIN dispatch (registry lookups, Steps 1–2), then the design-attribute
match (Step 3, `_resolve_to_design_attribute:673`), then falls through to a **Step-4
per-consumer fallback entry point** (`:580`) with `default_value is None`. The graph
builder's `collect_uncovered_params` (`graph_builder.py:810`) sees that EP is
fell-through ∧ valueless ∧ wired → V11 offender. That is the "before" state the three
`plant_values` pins and the `'Flow Sub'` pin assert.

The reason Step 3 misses: the subsystem attribute (`driver.efficiency`,
`chamber.cost_per_unit`, `throughput`) is declared **valueless on its base def**. Its
value lives elsewhere — in a redefinition or an override — that no resolution step
consults. So Step 3's design-attribute index has no entry with a value to match.

### The values are already captured — nothing new to extract

Every one of the ten values is a model literal already serialized in the snapshot
(`hierarchy_data`), in one of two buckets:

| Shape | Example | Capture bucket | Keying link |
|-------|---------|----------------|-------------|
| (a) subtype-def `:>>` via retype | `Hif_Driver.efficiency = 0.35` | `redefinitions` (LITERAL, owner=`PlantValuesLib__Hif_Driver`) | `usage_type_map[(plant, driver)] = Hif_Driver` |
| (b) bare override block | `plant.target_factory.cost_per_target = 10.0` | `design_overrides` (owner=`…__target_factory`) | owner QN ends with `target_factory` |
| (c) dotted usage override | `plant.chamber.cost_per_unit = 7.0` | `design_overrides` (owner=`…__plant`, `target_path=["chamber","cost_per_unit"]`) | `target_path` |
| (d) in-part inherited redefine | `Flow_Sub.throughput = 8.0` | `redefinitions` (LITERAL, owner=`PlantValueShapesLib__Flow_Sub`) | `CalcUsageData.owning_part_def_qn = Flow_Sub` |

Confirmed against the committed snapshots (probed `extraction_snapshot.json` for both
fixtures). Two consequences that shape the design:

- **The (a) retype link exists**: `usage_type_map` carries
  `("PlantValuesDesign__plant","driver") → PlantValuesLib__Hif_Driver`.
- **The (d) in-part link exists with no `usage_type_map`**: the flow_calc usage carries
  `owning_part_def_qn = PlantValueShapesLib__Flow_Sub`, which is exactly the redef owner.
  `plant_value_shapes`' `usage_type_map` is empty, so (d) must NOT depend on it.

### The machinery to extend, not fork

- **This is the LVP mechanism, extended.** Doc 18 ("Literal Value Propagation for
  Aggregation Entry Points", REQ-LVP-01..09) already fills an entry point's `default_value`
  from a LITERAL `:>>` redefinition — but **only** when an aggregation SumTerm/SingletonTerm
  fails channel resolution. This item extends the SAME idea to **CalcUsage** cross-part/in-part
  entry points. It is not a new concept; it is LVP reaching a second consumer class.
- **`_find_literal_redefinition` (`graph_builder.py:1308`)** is the LVP value-lookup:
  it resolves a LITERAL `:>>` redefinition with `usage_type_map` (Strategy 1, exact PartDef
  QN) or a name-based fallback (Strategy 2). Its lookup is exactly what (a)/(d) need — reuse it.
- **`_resolve_to_design_attribute` (`dependency_backtracker.py:673`)** already matches
  BOTH a dotted source (`chamber.cost_per_unit` → parent_part=`chamber`, attr=`cost_per_unit`,
  `:701`) and a bare source (`throughput`, `:748`) against the design-attribute index,
  and returns the attribute's QN. Two consumers binding the same source resolve to the
  **same** QN → fan-out collapse is already how design attributes dedupe (this is what
  `test_fanout_collapses_to_one_producer_channel` exercises — both `scale_a`/`scale_b` →
  one `…__scale` EP). Reuse this for the source-QN keying; do not build a second dedup path.
- **REQ-VBR-03 is the tier-1 precedent**: a LITERAL usage override already flips a virtual
  CalcUsage binding to a DESIGN_ATTRIBUTE entry point (doc 12). The materializer applies the
  same override→DESIGN_ATTRIBUTE semantics to a subsystem attr read cross-part.
- **REQ-VBR-10 is NOT this.** VBR-10 rewrites a `:>> attr = calc.output` CHAIN binding
  through the specialized chain (a `source_path` rewrite to an output channel); it never
  fills a plain literal. Carrying `:>> efficiency = 0.35` onto an entry point is a
  different operation — hence a new REQ, not a VBR-10 overload (D3).
- **`design_overrides` is loaded but dropped on the floor**: `graph_rebuild.py:148-149`
  threads `redefinitions` and `usage_type_map` into `build_computation_graph`, but not
  `design_overrides`. Both call sites (live + snapshot) must thread it (an F-A-style
  thread-through), or (b)/(c) have no value source.

### RN-10: the calc-output edge this item must not disturb

RN-10 wired the four cross-part **calc-output** shapes (`gamma → lcoe`) via
`_rewrite_specialized_chain`, the OutputRegistry, and EXPOSE channels — the registry
Steps 1–2 that run BEFORE Step 3. RN-10 recorded these **plain-value** references as
the residual plant gap ("the full fusion-tea YAML does NOT yet emit"). This item fills
Step 3, strictly downstream of the registry steps, so calc-output resolution is
untouched by construction.

---

## Core Concept

**The subsystem attribute already has a value; the pipeline just never looks where it
lives. Put the value where the resolver already looks.**

The design-attribute resolution path is a working value-carrier: it matches a binding's
source path to a design attribute that has a value, keys the entry point by that
attribute's source QN, and collapses fan-out because two consumers of one attribute
resolve to one QN. It fails for the ten offenders only because their source attributes
are valueless on the base def — their value sits in a redefinition or override the path
does not read.

So the whole mechanism is one pre-pass — a **supplied-value materializer**, the LVP
mechanism (doc 18) extended from aggregation terms to CalcUsage inputs — that reads the
two capture buckets (`redefinitions` ∪ `design_overrides`), resolves the plain-value
precedence (usage override > specialized-def `:>>` > base def — the same three-tier merge
doc 12 names), and emits a synthetic `DesignAttributeData` per supplied subsystem
attribute, keyed by its source QN and carrying the resolved literal (reusing
`_find_literal_redefinition` for the tier-2/(d) lookup). It merges these into the
`design_attributes` map before backtracking. From there, nothing new runs:
`_resolve_to_design_attribute` matches the source path to the synthesized attribute
(Step 3), the EP is keyed by source QN (fan-out collapse, free), and
`_classify_entry_points` marks it DESIGN_ATTRIBUTE with the value (V11 clears).

This is why value-fill is the right decision and channel wiring is not (below): the
ten values are all literals, so a filled entry point carries the exact anchor semantics
the bridge already validated, and the params stay JSON-fillable keys — the harness
contract. Wiring would move them to computed outputs, break the bridge's key set, and
buy nothing, because there is no upstream calc to wire to.

The one choke point covers all four shapes because the materializer resolves the value
regardless of which bucket holds it, and the source-QN keying is uniform. (a) and (d)
read `redefinitions` (via `usage_type_map` and `owning_part_def_qn` respectively); (b)
and (c) read `design_overrides` (via owner QN and `target_path`). Precedence lives in
one place. No per-mechanism dispatch.

---

## Key Decisions

- **D1. Value-fill, not channel wiring.** Materialize the supplied literal onto the
  source attribute; the consumer input becomes a pre-filled DESIGN_ATTRIBUTE entry point.
  *Rejected: channel wiring* (make the input a module_output/shared-source channel).
  Rejected because all ten sources are literals with no producing calc to wire to — there
  is no output channel to point at; the bridge validated value-propagation semantics
  bit-exactly (anchor C); and wiring removes the params from the entry-point groups,
  breaking fusion-tea's harness key set and `run_anchors_bridged.py`'s exactly-10 guard
  for no gain. Value-fill preserves the JSON key category (Item 3 re-anchors values, not
  the input/output split).

- **D2. Materialize into the existing `design_attributes` map; reuse Step 3 for
  resolution and collapse.** *Rejected: a new backtracker "Step 3.5" supplied-value
  resolver* that computes a source QN and carries the value via `entry_point_sources`.
  Rejected because it forks a second EP-keying-and-dedup path parallel to the
  design-attribute one — exactly the parallel mechanism the design guidance warns
  against — and would re-derive the fan-out collapse Step 3 already provides. The pre-pass
  adds zero new dispatch branches: it only populates the index Step 3 already reads.

- **D3. New REQ = REQ-LVP-10, extending the LVP family.** The plain-value precedence —
  usage override > specialized-def `:>>` > base def — reaches a CalcUsage entry point as a
  filled `default_value`. That is the doc-18 LVP operation (LITERAL redef →
  entry-point default) applied to a new consumer class, so it belongs in the LVP family:
  **REQ-LVP-10** (next free after LVP-09), authored in doc 18 + doc 25 + the matrix.
  *Rejected: a fresh REQ-RES-##* — it would hide that this is the same mechanism as
  aggregation LVP, just reaching CalcUsage terms. *Rejected: overloading REQ-VBR-10* —
  VBR-10 is the `:>> attr = calc.output` CHAIN rewrite (a `source_path` rewrite to an
  output channel), not a plain-literal fill; overloading it misdescribes both (spec
  Must-Fix 4). REQ-VBR-03 (LITERAL override → DESIGN_ATTRIBUTE EP) is cited as the tier-1
  precedent, not extended.

- **D4. Do not split the item; keep the split line as a documented fallback.** The
  mechanism is one pre-pass reusing existing paths, (d) is landable with data that
  already exists (`owning_part_def_qn`), and the SC-3 runner is small (~60–100 lines).
  If the runner plus the fan-out-rename fixture push past budget, the fallback split is:
  **core** = materializer + (a)/(b)/(c)/(d) + precedence + headline flips + SC-4; **follow-on**
  = SC-3 executor runner + the renamed-consumer fan-out leg + any deep-chain edge. The
  core alone delivers the epic CSF (zero V11 offenders on the fusion-tea snapshot), since
  SC-4 is graph-level; only SC-3's execution gate would slip. *Rejected: pre-emptive split*
  — it loses no coverage but adds handoff cost the evidence does not justify.

- **D5. New V11 raise-proof anchor = `plant_value_shapes` Shape 1 (`rated_cost__rate`).**
  `'Flow Sub'` clears under (d), so it can no longer prove V11 still fires. Shape 1 (the
  econ-param nested `:>> value = 0.70` that does not reach the cross-part `rated_cost.rate`)
  stays valueless after this item: its value lives in a nested **attribute-def** bundle,
  not a part redefinition or design override the materializer reads. *Rejected: `'Flow Sub'`*
  (dissolved by this item), *Shape 9* (non-float enum EP — Item 5's substrate, avoid entangling).

---

## Key Bets

- **B1. Every one of the ten offender values is a plain model literal.** *If false →*
  value-fill cannot carry a non-literal (an expression/chain RHS) and the anchor would
  need a computed upstream — the whole value-vs-wiring decision flips. Verified: all four
  captured values are LITERAL-typed with numeric `literal_value`; the discovery bridge
  reproduced anchor C bit-exactly from the ten literals.

- **B2. The design-attribute path's source-QN keying is what collapses fan-out.** *If
  false →* filling a per-consumer EP would leave the renamed-consumer fan-out as N keys,
  violating the EP-keys-by-source-QN [HARD]. Verified: `test_fanout_collapses_to_one_producer_channel`
  collapses `scale_a`/`scale_b` onto one `…__scale` EP via `_resolve_to_design_attribute`.

- **B3. Registry resolution (Steps 1–2) runs strictly before design-attribute resolution
  (Step 3).** *If false →* a synthesized design attribute could shadow a real calc-output
  channel and regress Item 10's `gamma → lcoe` edge. Verified in `_resolve_binding_via_registry`
  (`:547-563`): channel lookups return first; design-attribute match is reached only on
  fall-through.

- **B4. (d)'s in-part link needs no `usage_type_map`.** *If false →* (d) is un-landable in
  `plant_value_shapes` (its `usage_type_map` is empty) and the (d) escalation rule fires.
  Verified: the flow_calc usage carries `owning_part_def_qn = Flow_Sub`, matching the redef
  owner directly.

---

## Architecture

Pipeline position — one new step, upstream of the backtracker, everything else unchanged:

```
extraction / snapshot load
      │  hierarchy_data = { redefinitions, design_overrides, usage_type_map, ... }
      ▼
[NEW] supplied-value materializer ──► synthetic DesignAttributeData (source-QN keyed, valued)
      │                                        │
      │   merge into design_attributes ◄───────┘
      ▼
DependencyBacktracker
   _resolve_binding_via_registry
      Step 1–2  registry (calc-output/EXPOSE)   ← unchanged (RN-10 / VBR-10)
      Step 3    _resolve_to_design_attribute     ← now matches the synthesized attrs
      Step 4    fallback EP                       ← the ten offenders no longer reach here
      ▼
build_computation_graph
   _classify_entry_points  → DESIGN_ATTRIBUTE with default_value  ← V11 clears
```

**Data flow for each shape** (all converge on Step 3):

- (a) `driver.efficiency`: materializer resolves driver's type via `usage_type_map` →
  `Hif_Driver`, finds LITERAL redef `efficiency=0.35`, emits attr (parent_part=`driver`,
  name=`efficiency`, value=0.35, QN=`PlantValuesDesign__plant__driver__efficiency`).
- (b) `target_factory.cost_per_target`: override owner ends with `target_factory` → 10.0.
- (c) `chamber.cost_per_unit`: override `target_path=["chamber","cost_per_unit"]` → 7.0.
- (d) `throughput` (bare): calc's `owning_part_def_qn = Flow_Sub`, LITERAL redef
  `throughput=8.0`, emits attr (name=`throughput`, value=8.0).

**Precedence resolution (D3, the new REQ)** — for each (instance, part_usage, attr) the
materializer resolves, highest wins:

1. **Usage override** — a `design_overrides` entry on this instance targeting (part_usage,
   attr) by `target_path` or owner QN.
2. **Specialized-def `:>>`** — a LITERAL `redefinitions` entry on part_usage's resolved
   type (`usage_type_map` retype, else base type), or on the calc's `owning_part_def_qn`
   for the in-part (d) case.
3. **Base def default** — existing behavior; no synthesis needed.

**SC-3 executor runner** (new, `tests/runtime/pipeline_runner.py` or a `runtime/` helper):
reads the generated pipeline YAML for the execution order and per-module input wiring;
imports each generated module; feeds entry-point inputs from the emitted JSON and
module_output inputs from prior outputs; executes in order; returns `channel → value`.
SC-3 asserts the target within `rel 1e-6`. Written to be driven by Item 3's fusion-tea
gate too (drive `registry_init` if teax imports in-repo; else a fixture-local driver).

---

## Required Invariants

- **INV-1 (RN-10 / VBR-10 untouched).** Registry Steps 1–2 resolve first; a synthesized
  design attribute never shadows a calc-output channel. The `gamma → lcoe` twolevel chain
  stays wired; `test_spec_chain_channel.py` / `test_spec_chain_twolevel.py` stay green.
- **INV-2 (source-QN keying).** A synthesized attribute's QN is derived only from
  (owning-instance-scope, part_usage, attr) — identical for every consumer of that source.
  Differently-named consumers collapse onto one EP.
- **INV-3 (precedence total & loud).** For any attr with values at multiple tiers, tier 1
  beats tier 2 beats tier 3, deterministically. A value re-redefined in a **deeper**
  specialization than the one read is out of scope — the materializer must be loud
  (warn/skip), never silently pick the wrong tier.
- **INV-4 (demand-scoped, no baseline drift).** The materializer synthesizes only for a
  subsystem attr that (i) is referenced by a calc-usage binding AND (ii) has a LITERAL
  override/redefinition value — never supply-side over all redefinitions. Because Step 3
  runs after the registry steps (INV-1), a synthesized attr for something the registry also
  resolves is harmlessly ignored, so demand-scoping is for boundedness, not correctness. It
  must not fabricate an attribute that shadows an existing design attribute or cross-wires a
  bare-name match (guard: scope dotted matches by parent_part; prefer same-instance for bare
  (d); reuse `_is_calc_def_owned`).
- **INV-5 (value-carried, not test-supplied).** All three headline values (0.35, 10.0,
  7.0) and (d)'s 8.0 arrive from the model literals; the `48.5714…` anchor is hand-derived,
  never read back from the resolver.

---

## Component Overview

- **`supplied_value_materializer` (new, REQ-LVP-10).** Location:
  `extraction/hierarchy_resolver.py` (it reads `hierarchy_data`) or a small new
  `resolution/supplied_values.py`. Input: `redefinitions`, `design_overrides`,
  `usage_type_map`, the design usages, and the calc usages (for `owning_part_def_qn`).
  Reuses `_find_literal_redefinition` (graph_builder.py:1308) for the tier-2/(d) redef
  lookup; adds the tier-1 `design_overrides` lookup. Output: `list[DesignAttributeData]`
  to merge into the `design_attributes` map. Owns the precedence (D3).
- **`build_computation_graph` (extend signature).** Add a `design_overrides` parameter;
  thread it from both call sites (`graph_rebuild.py`, the live generate path). Run the
  materializer, merge its output into `design_attrs` before constructing the backtracker.
- **`_resolve_to_design_attribute` / `_classify_entry_points` (unchanged).** Consume the
  merged attributes exactly as they consume real design attributes today.
- **`pipeline_runner` (new).** The SC-3 executor. Reusable by Item 3.
- **Tests (new/flip).** Headline flips in `test_plant_values.py` (empty offender set +
  per-mechanism value pins); (d) flip in `test_plant_value_shapes.py` (`8.0`); the
  three-tier precedence fixture (design authors the usage-override tier); the SC-3 executor
  test; the re-anchored V11 raise-proof on Shape 1; the renamed-consumer fan-out leg.

---

## Non-Goals

- **fusion-tea repo changes (Item 3):** deleting `hif_driver_instance`, retiring the
  gamma two-pass / `sanitize_names.py`, the live acceptance run. This item's fusion-tea
  gate is the license-free from-snapshot proxy (SC-4).
- **Cross-part supertype *template* expansion for plain usages** — deferred (MFE epic).
  Distinct from (d): (d) is in-part inherited-attr-redefine, resolved within one part's
  own hierarchy, IN scope.
- **Non-literal RHS** in override/redefinition (CHAIN/EXPRESSION beyond Item 10) — out
  unless it falls out free; the materializer reads LITERAL only.
- **Deep re-redefinition** (a value re-redefined below the tier read) — out of scope, but
  INV-3 requires it be loud, not silently wrong.
- **Constraint resolution/execution**, the teax OutputRouter/WriteHandler harness — not here.

---

## Implementation Notes

- **Thread `design_overrides` first** — without it (b)/(c) have no value source. Both the
  snapshot path (`graph_rebuild.py:139`) and the live generate path must pass it. Missing
  either silently reverts (b)/(c) to valueless.
- **New REQ ID = REQ-LVP-10** (LVP-09 is the current highest; the family is doc 18 /
  doc 25). Author it in three places: doc 18's requirement table (3-col: ID | Requirement |
  Verified by), doc 25, and the matrix (4-col: REQ ID | Requirement | Test File | Status;
  under the `### LVP` block). Leave REQ-VBR-10/11 and REQ-VBR-03 rows unchanged — the code
  they name does not change.
- **(d) uses `owning_part_def_qn`, not `usage_type_map`** — `plant_value_shapes`'
  `usage_type_map` is empty; do not route (d) through it.
- **Precedence fixture (SC-2):** no existing fixture exercises the usage-override tier
  beating the specialized-def tier. Author it: base `efficiency` valueless / `Hif_Driver`
  `:>> efficiency = 0.35` (tier 2) / plant usage `:>> driver.efficiency = 0.99` (tier 1
  dotted override) → resolves to 0.99. Distinct values prove tier 1 > tier 2 > tier 3.
- **Anchor:** `(target_cost + chamber_cost) / driver_efficiency = (10 + 7) / 0.35 =
  48.5714…`. Hand-transcribed literal in the test; if the F1/F2 cure lands a chamber
  literal other than 7.0, the anchor follows the cure commit (per SC-1).
- **Sequencing:** implement runs AFTER Item 4's format-bump re-capture. This design is
  doc-only. Capture against whatever snapshot format is live at implement.

### Interface sketch (pseudo-code, not implementation)

```python
def materialize_supplied_values(
    redefinitions, design_overrides, usage_type_map,
    design_usages, calc_usages,
) -> list[DesignAttributeData]:
    # for each subsystem attr referenced by a cross-part/in-part binding whose
    # base def is valueless: resolve tier1(override) > tier2(spec-def :>>) > None,
    # emit DesignAttributeData(parent_part, name, default_value, qualified_name=source_qn).
    ...
```

---

## Potential Risks

- **Bare-name (d) ambiguity.** The materializer emits a `throughput` attribute matched by
  bare name; a second unrelated `throughput` could cross-wire. *Mitigation:* prefer
  same-instance/same-file (existing `_resolve_to_design_attribute` logic) and scope
  synthesis to attrs actually referenced by an in-part binding. Covered by INV-4.
- **Baseline drift on the four existing cross-part baselines (SC-5).** If any currently
  has a valueless-and-referenced subsystem attr the materializer now fills, its baseline
  flips. *Mitigation:* expected zero (Item 10 wired their calc-output shapes; their
  plain-value attrs were already design attributes) — but verify each diff at capture and
  justify any change.
- **Deep re-redefinition silently wrong (INV-3).** *Mitigation:* the materializer resolves
  only the tier it can see and warns on a deeper redefinition it does not follow.
- **SC-3 runner scope creep.** If teax is not importable in-repo, the fixture-local driver
  must reproduce module import + input feed faithfully. *Mitigation:* keep it minimal and
  YAML-driven; it is the D4 split's follow-on candidate if it over-runs.

## Integration Strategy

The mechanism is additive at Step 3 of an existing four-step dispatch and a new pre-pass
that only populates an index already consumed. It replaces nothing. Item 3 reuses the
SC-3 runner verbatim for the fusion-tea live gate and re-anchors the (now-filled) values.
Item 9 records the four supported value shapes for the agentic-mbse MODELING_GUIDE impact.

## Validation Approach

- **SC-1 / SC-1d:** headline `plant_values` offender set flips to empty; per-mechanism EP
  value pins (0.35 / 10.0 / 7.0); `'Flow Sub'` flips to 8.0. Behavior-observing pins, not
  byte-equality.
- **SC-2:** three-tier precedence fixture with distinct values; a tier-skip/reorder fails.
- **SC-3:** the extended `spec_chain_twolevel` package executed through the runner within
  `rel 1e-6` of the hand-computed value (execution, not graph inspection).
- **SC-4:** `generate --from-snapshot` on the committed fusion-tea snapshot → true zero V11
  offenders (all ten cleared).
- **SC-5:** four cross-part baselines byte-identical or justified; V11 raise-proof
  re-anchored to Shape 1 still fires; `plant_values`/`'Flow Sub'` regenerate to zero-offender.
- **SC-6:** docs 18 (LVP — the primary home), 11/12/25 + modeling-assumptions §5 record
  the four shapes, REQ-LVP-10, and the fan-out-by-source-QN rule; matrix `### LVP` row added.
- **Regression:** `test_spec_chain_channel.py` / `test_spec_chain_twolevel.py` stay green
  (INV-1); the renamed-consumer fan-out leg collapses to one source EP (INV-2).

## Next-Stage Handoff

- **Fixed:** value-fill (D1); materialize-into-`design_attributes` choke point, reusing
  Step 3 + `_find_literal_redefinition` (D2); REQ-LVP-10 for the plain-value precedence
  (D3); no split (D5 fallback line documented); Shape 1 as the V11 re-anchor.
- **Open (plan resolves):** whether the materializer lives in `hierarchy_resolver.py` or a
  new `resolution/supplied_values.py`; the SC-3 runner's teax-vs-fixture-local form; the
  precedence fixture's home (extend `plant_values` or a sibling). (REQ ID is fixed:
  REQ-LVP-10.)
- **De-risk first:** thread `design_overrides` into `build_computation_graph` and confirm
  (b)/(c) fill — that thread-through is the single point of failure. Then (d)'s
  `owning_part_def_qn` path. The SC-3 runner is independent and can proceed in parallel.

---
Next Step: After approval → `/_my_plan`
