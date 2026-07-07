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

### The machinery to reuse — and where it stops (a distinct mechanism)

Three existing literal-to-entry-point paths sit near this, and the materializer is
**none** of them — it reuses one helper and is honestly its own mechanism (a new
REQ-SVM family, D3):

- **Aggregation LVP (doc 18, REQ-LVP-01..09).** `_find_literal_redefinition`
  (`graph_builder.py:1308`) fills an EP `default_value` from a LITERAL `:>>` redef — but
  **only** for an aggregation SumTerm/SingletonTerm. Doc 18 **explicitly fences off**
  CalcUsage-binding literals as "a path separate from the `_find_literal_redefinition()`
  lookup this document describes" (`18:163-167`) and excludes LocalTerms (REQ-LVP-04). So
  filing CalcUsage value-fill under LVP contradicts the doc's own boundary. The materializer
  **reuses the helper's value-lookup** but is not the LVP mechanism.
- **Virtual-binding rewrite (REQ-VBR-03).** `_rewrite_virtual_bindings`
  (`pipeline_builder.py`) already applies a design-override LITERAL to a CalcUsage binding
  by rewriting it to a LITERAL binding — but that keys per-consumer (`usage_qn__param`, a
  USAGE_LITERAL EP), so it does **not** collapse a renamed-consumer fan-out. Extending it
  would fail the source-QN [HARD]. REQ-VBR-03 is a sibling, not the host.
- **REQ-VBR-10 is not this at all.** VBR-10 rewrites a `:>> attr = calc.output` CHAIN
  binding to an output channel; it never fills a plain literal.

What the materializer **does** reuse:

- **`_find_literal_redefinition` (`graph_builder.py:1308`)** for the tier-2 specialized-def
  lookup via `usage_type_map` (Strategy 1). Note: its Strategy-2 name-fallback does NOT fit
  (d) cleanly — (d) needs a direct owner match, added below (F4).
- **`_resolve_to_design_attribute` (`dependency_backtracker.py:673`)** for source-QN keying
  and fan-out collapse. It matches on the binding's `source_path` (dotted at `:701-710`,
  bare at `:748-760`) and **ignores the consumer's `param_name`** — so two differently-named
  consumers of `= driver.efficiency` produce the same `source_path` and resolve to the same
  synthesized QN → one EP, by construction. This keying is why the mechanism is distinct
  from VBR-03: it dedupes across consumers, VBR-03 does not.
- **`design_overrides` is loaded but dropped on the floor**: `graph_rebuild.py:148-149` and
  `pipeline_builder.py:800-815` thread `redefinitions` + `usage_type_map` into
  `build_computation_graph`, but not `design_overrides`. Both call sites must thread it
  (an F-A-style thread-through), or (b)/(c) have no value source.

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

So the whole mechanism is one pre-pass — a **supplied-value materializer** (a new
REQ-SVM family, D3) — that, for each referenced subsystem-attr binding, reads the two
capture buckets (`redefinitions` ∪ `design_overrides`), resolves the plain-value
precedence (usage override > specialized-def `:>>` > base def — the same three-tier merge
vocabulary doc 12 uses), and emits a synthetic `DesignAttributeData` per supplied
attribute, keyed by its source QN and carrying the resolved literal **as a string** (to
match how real design attributes serialize, e.g. `"0.35"`). It merges these into the
`design_attributes` map before backtracking. From there the existing path runs:
`_resolve_to_design_attribute` matches the source path to the synthesized attribute
(Step 3), the EP is keyed by source QN (fan-out collapse, free), and
`_classify_entry_points` marks it DESIGN_ATTRIBUTE with the value.

The mechanism reuses seams but touches sharp code in four spots the design pins rather
than assumes: `_classify_entry_points` drops a `0.0` default via a truthiness test (F2,
fixed to `is not None`); a synthetic attr must never overwrite a real one (F3, real wins +
WARN); (d)'s literal lookup needs a direct owner match, not the name-fallback (F4); and a
referenced non-literal must skip loudly, not silently (F5). These are the seams where the
choke point meets code that does not, unmodified, do what it needs.

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

- **D3. New REQ family = REQ-SVM (supplied-value materializer), not REQ-LVP-10.** The
  mechanism is genuinely distinct: it keys entry points by **source QN and collapses across
  consumers**, which neither aggregation LVP (per-term) nor VBR-03 (per-consumer) does. Doc
  18 **explicitly fences** CalcUsage-binding literals out of LVP as "a path separate from
  `_find_literal_redefinition()`" (`18:163-167`); filing under LVP-10 would contradict that
  fence by assertion — the same muddying the spec's Must-Fix 4 bans, aimed at a different
  doc. So: a small new family **REQ-SVM-01..04** (below), documented in a new doc 25 section
  that cross-references doc 18's shared `_find_literal_redefinition` helper and doc 12's
  VBR-03 sibling. *Rejected: REQ-LVP-10* (contradicts doc 18's boundary). *Rejected:
  widening doc 18's title/scope to "entry points generally"* (orchestrator option ii) — the
  source-QN-collapse behavior is not what doc 18 describes, so unifying would blur two real
  mechanisms rather than clarify. The REQ-SVM set:
  - **REQ-SVM-01** — for a referenced subsystem-attr binding, synthesize a design attribute
    carrying the LITERAL value resolved by precedence (usage override > specialized-def
    `:>>` > base def), `default_value` as a string.
  - **REQ-SVM-02** — key the synthetic attribute by source QN (owning-instance-scope,
    part_usage, attr) so differently-named consumers collapse to one EP.
  - **REQ-SVM-03** — a synthetic attribute never overwrites a real captured design attribute;
    on collision the real one wins and the materializer WARNs (F3).
  - **REQ-SVM-04** — apply LITERAL only; emit a count-summary WARN naming non-literal
    (CHAIN/EXPRESSION) skips; a referenced non-literal-only binding falls through to Step-4
    (V11), never a silent drop (F5).

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

- **B2. The design-attribute matcher keys on `source_path` and ignores `param_name`.** *If
  false →* differently-named consumers would not collapse and the renamed-consumer fan-out
  stays N keys, violating the EP-keys-by-source-QN [HARD]. Verified in the matcher itself
  (`_resolve_to_design_attribute:701-710`): it matches `(name, parent_part)` parsed from the
  binding's `source_path`, never the consumer input name. (The existing
  `test_fanout_collapses_to_one_producer_channel` proves only the *same*-name case — `in s =
  scale` twice; the renamed-consumer property is proven by this item's new renamed-consumer
  fixture leg, not that test.)

- **B3. Registry resolution (Steps 1–2) runs strictly before design-attribute resolution
  (Step 3).** *If false →* a synthesized design attribute could shadow a real calc-output
  channel and regress Item 10's `gamma → lcoe` edge. Verified in `_resolve_binding_via_registry`
  (`:547-563`): channel lookups return first; design-attribute match is reached only on
  fall-through.

- **B4. (d)'s in-part link is a direct owner match, needing no `usage_type_map`.** *If
  false →* (d) is un-landable in `plant_value_shapes` (its `usage_type_map` is empty) and the
  (d) escalation rule fires. Verified: `flow_calc.owning_part_def_qn == redef.owning_part_qn
  == Flow_Sub`, an exact match (leg 2b). This is NOT the same as `_find_literal_redefinition`'s
  Strategy-2 name-fallback, which happens to match here only because the owner's last segment
  equals the part-def name — brittle for a supertype-owned inherited redef, so (d) uses the
  direct-owner leg (F4).

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
- (d) `throughput` (bare): match a LITERAL redef by **direct owner**
  `redef.owning_part_qn == calc.owning_part_def_qn` (both `Flow_Sub`) → 8.0; emits attr
  (name=`throughput`, value=8.0). NOT the name-fallback (F4).

**Precedence resolution (REQ-SVM-01)** — for each (instance, part_usage, attr) the
materializer resolves, highest wins:

1. **Usage override** — a `design_overrides` entry on this instance targeting (part_usage,
   attr) by `target_path` or owner QN.
2. **Specialized-def `:>>`** — a LITERAL `redefinitions` entry matched by either:
   (2a) part_usage's retyped type via `usage_type_map` (reuse `_find_literal_redefinition`
   Strategy 1); or (2b, the in-part (d) leg) **direct owner** `redef.owning_part_qn ==
   calc.owning_part_def_qn`. The materializer must NOT rely on `_find_literal_redefinition`'s
   Strategy-2 last-segment name-fallback — it is brittle for an inherited redefinition owned
   by a supertype and is not (d)'s natural operation (F4). Add leg (2b) either to
   `_find_literal_redefinition` as a new strategy or as a materializer-local exact match.
3. **Base def default** — existing behavior; no synthesis needed.
4. **Collision guard (REQ-SVM-03)** — before emitting, if a real captured design attribute
   already covers the source QN (or `(name, parent_part)`), the real one wins: skip
   synthesis and WARN. Never overwrite a real attr (`_classify_entry_points` builds
   `design_attr_by_qname` last-wins by QN, `graph_builder.py:457-461`, so an un-guarded
   synthetic could clobber a real value order-dependently).

**SC-3 executor runner** (new) — reads the generated pipeline YAML for order + wiring,
imports the modules, feeds JSON inputs, executes, returns `channel → value`; SC-3 asserts
within `rel 1e-6`. Signature pinned in Component Overview (F7); reusable by Item 3.

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
- **INV-6 (0.0 carried faithfully, not dropped to null).** A synthesized EP resolves at
  Step 3, so it is NOT in `_fallback_entry_points` — V11 (`collect_uncovered_params`) keys
  on the fell-through set, so a `0.0` default silently dropped to `None` would emit `null`
  and **escape V11**, the exact failure this epic kills. `_classify_entry_points:482` uses
  `if attr.default_value:` (truthiness, drops `0.0`/`""`); change it to `is not None` (F2).
  Pinned by a 0.0-valued supplied literal that must emit as `0.0`, not `null`.
- **INV-7 (non-literal skips loudly).** A referenced binding whose only supplied value is a
  non-literal (CHAIN/EXPRESSION) is not synthesized; it falls through to Step-4 → V11, and
  the materializer emits a count-summary WARN (REQ-SVM-04). Never a silent drop.

---

## Component Overview

- **`supplied_value_materializer` (new, REQ-SVM-01..04).** Location:
  `extraction/hierarchy_resolver.py` (it reads `hierarchy_data`) or a small new
  `resolution/supplied_values.py`. Input: `redefinitions`, `design_overrides`,
  `usage_type_map`, the design usages, the calc usages (for `owning_part_def_qn`), and the
  real `design_attributes` (for the collision guard). Reuses `_find_literal_redefinition`
  Strategy 1 for tier-2a; adds the tier-2b direct-owner leg (F4) and the tier-1
  `design_overrides` lookup. Emits `DesignAttributeData` with `default_value` as a **string**
  (matches `parameter_groups.py:51` `str | None`), skipping any source a real attr already
  covers (F3) and WARNing on non-literal skips (F5). Owns the precedence (D3).
- **`build_computation_graph` (extend signature).** Add a `design_overrides` parameter;
  thread it from both call sites (`graph_rebuild.py:139`, `pipeline_builder.py:800-815`). Run
  the materializer, merge into `design_attrs` before constructing the backtracker.
- **`_classify_entry_points` (one-line fix, F2).** Change `if attr.default_value:` (`:482`)
  to `if attr.default_value is not None:` so a supplied `0.0` is carried, not dropped to
  `null`. Otherwise consumes the merged attributes as it consumes real ones today.
- **`_resolve_to_design_attribute` (unchanged).** Matches the merged attributes on
  `source_path`; collision safety is enforced upstream by the materializer's guard (F3).
- **`pipeline_runner` (new).** The SC-3 executor with a pinned interface (below). Reusable
  by Item 3.
- **Tests (new/flip).** Headline flips in `test_plant_values.py`; (d) flip in
  `test_plant_value_shapes.py` (`8.0`, via the direct-owner leg); three-tier precedence
  fixture (authors the usage-override tier); **a 0.0-supplied-literal pin** (emits `0.0`, not
  `null`, F2); **a constructed-collision pin** (real attr wins + WARN, F3); **a non-literal
  skip pin** (falls to V11 + WARN summary, F5); the SC-3 executor test; the re-anchored V11
  raise-proof on Shape 1; the renamed-consumer fan-out leg (B2).

### SC-3 runner interface (pinned for Item 3, F7)

```python
# tests/runtime/pipeline_runner.py (or src/.../runtime/)
def run_pipeline(
    package_dir: Path,               # generated package: modules/, pipelines/*.yaml, inputs/*.json
    inputs: dict[str, float] | None = None,  # optional entry-point overrides (Item 3 perturbation); else emitted JSON
) -> dict[str, float]:               # channel_name -> computed value, for every module output
    ...
```

Contract: reads the pipeline YAML for execution order + per-module input wiring; imports
each generated module; feeds entry-point inputs from `inputs` (falling back to the emitted
JSON) and module_output inputs from prior outputs; executes in order; returns every
channel's value. Item 3 consumes this signature sight-unseen. The teax-vs-fixture-local
driver form is a plan-time open; the signature is not.

---

## Non-Goals

- **fusion-tea repo changes (Item 3):** deleting `hif_driver_instance`, retiring the
  gamma two-pass / `sanitize_names.py`, the live acceptance run. This item's fusion-tea
  gate is the license-free from-snapshot proxy (SC-4).
- **Cross-part supertype *template* expansion for plain usages** — deferred (MFE epic).
  Distinct from (d): (d) is in-part inherited-attr-redefine, resolved within one part's
  own hierarchy, IN scope.
- **Non-literal RHS** in override/redefinition (CHAIN/EXPRESSION beyond Item 10) — out of
  scope, but **not silent**: a referenced non-literal falls through to V11 and the
  materializer WARNs a count summary (REQ-SVM-04 / INV-7). The materializer applies LITERAL
  only.
- **Deep re-redefinition** (a value re-redefined below the tier read) — out of scope, but
  INV-3 requires it be loud, not silently wrong.
- **Constraint resolution/execution**, the teax OutputRouter/WriteHandler harness — not here.

---

## Implementation Notes

- **Thread `design_overrides` first** — without it (b)/(c) have no value source. Both the
  snapshot path (`graph_rebuild.py:139`) and the live generate path must pass it. Missing
  either silently reverts (b)/(c) to valueless.
- **New REQ family = REQ-SVM-01..04** (F1 / D3). Author a new `### SVM` block in the matrix
  (4-col: REQ ID | Requirement | Test File | Status) and a new doc 25 section
  ("Supplied-Value Materializer") that cross-references doc 18's `_find_literal_redefinition`
  helper and doc 12's VBR-03 sibling. Leave REQ-LVP-*, REQ-VBR-* rows unchanged — the code
  they name does not change. Do NOT file under LVP-10 (contradicts doc 18's `18:163-167`
  fence).
- **F2 one-line fix:** `_classify_entry_points:482` `if attr.default_value:` →
  `is not None`. Add a 0.0-supplied-literal capture row (plan's Item-2 capture rider on
  `plant_values` or `plant_value_shapes`) and a pin that it emits `0.0`, not `null`.
- **F3 collision:** materializer skips synthesis + WARNs when a real design attr already
  covers the source; never overwrite the last-wins `design_attr_by_qname` (`:457-461`).
- **F4 (d) lookup:** add the direct-owner leg (`redef.owning_part_qn ==
  calc.owning_part_def_qn`); do NOT rely on `_find_literal_redefinition` Strategy-2
  name-fallback. `plant_value_shapes`' `usage_type_map` is empty — (d) must not route through it.
- **F5 non-literal:** count-summary WARN, Item-5 sentinel style — e.g. "materializer scanned
  N override entries: M literal applied, K non-literal skipped (deferred shapes: <list>)".
  Zero skipped → no WARN (INFO summary only); silent-on-clean holds.
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
- **0.0 supplied literal escapes V11 (INV-6).** A Step-3-resolved EP is not fell-through, so
  a `0.0` dropped to `None` would emit `null` uncaught. *Mitigation:* the `is not None` fix
  at `:482` + a 0.0 regression pin (F2). Latent-Critical if unaddressed.
- **Synthetic attr overwrites a real design attribute (INV-, F3).** `design_attr_by_qname`
  is last-wins by QN. *Mitigation:* the materializer's collision guard (real wins + WARN),
  pinned by a constructed-collision test.
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
- **F2/F3/F5 pins:** 0.0 supplied literal emits `0.0` not `null`; a constructed synthetic/real
  QN collision keeps the real value + WARNs; a referenced non-literal falls to V11 with the
  count-summary WARN. (d)'s `8.0` resolves via the direct-owner leg (F4).
- **SC-3:** the extended `spec_chain_twolevel` package executed through the runner within
  `rel 1e-6` of the hand-computed value (execution, not graph inspection).
- **SC-4:** `generate --from-snapshot` on the committed fusion-tea snapshot → true zero V11
  offenders (all ten cleared).
- **SC-5:** four cross-part baselines byte-identical or justified; V11 raise-proof
  re-anchored to Shape 1 still fires; `plant_values`/`'Flow Sub'` regenerate to zero-offender.
- **SC-6:** a new doc 25 "Supplied-Value Materializer" section + docs 11/12 + modeling-assumptions
  §5 record the four shapes, the REQ-SVM family, and the fan-out-by-source-QN rule; matrix
  gains a `### SVM` block (cross-refs to doc 18's helper and doc 12's VBR-03).
- **Regression:** `test_spec_chain_channel.py` / `test_spec_chain_twolevel.py` stay green
  (INV-1); the renamed-consumer fan-out leg collapses to one source EP (INV-2).

## Next-Stage Handoff

- **Fixed:** value-fill (D1); materialize-into-`design_attributes` choke point, reusing
  Step 3 + `_find_literal_redefinition` Strategy 1 (D2); the **REQ-SVM family** for the
  plain-value precedence, not LVP (D3/F1); the F2 `is not None` fix; the F3 collision rule
  (real wins + WARN); the F4 (d) direct-owner leg; the F5 non-literal loud skip; the SC-3
  runner signature (F7); no split (D5 fallback); Shape 1 as the V11 re-anchor.
- **Open (plan resolves):** whether the materializer lives in `hierarchy_resolver.py` or a
  new `resolution/supplied_values.py`; the SC-3 runner's teax-vs-fixture-local driver form;
  the precedence fixture's home; where the 0.0 capture row lands (`plant_values` vs
  `plant_value_shapes`); whether leg 2b extends `_find_literal_redefinition` or is
  materializer-local.
- **De-risk first:** thread `design_overrides` into `build_computation_graph` and confirm
  (b)/(c) fill — that thread-through is the single point of failure. Then the F2 0.0 fix
  (one line + pin, independent) and (d)'s direct-owner leg. The SC-3 runner is independent
  and can proceed in parallel.

---

## Resolutions

Keyed by the design-review Finding IDs (Revise; foundation sound).

- **F1 — REQ-LVP-10 placement contradicts doc 18's boundary.** RESOLVED via orchestrator
  ruling 1, option (i): a new **REQ-SVM** family (SVM-01..04), not LVP-10. Doc 18 explicitly
  fences CalcUsage-binding literals off from `_find_literal_redefinition` (`18:163-167`), and
  the mechanism's source-QN collapse is neither aggregation LVP nor per-consumer VBR-03.
  Argued in D3; documented in a new doc 25 section cross-referencing doc 18's helper and doc
  12's VBR-03. Option (ii) (widen doc 18's fence) rejected — it would blur two real mechanisms.
- **F2 — 0.0 supplied literal silently escapes V11.** RESOLVED via ruling 2: change
  `_classify_entry_points:482` to `is not None`; add a 0.0-valued supplied-literal capture
  row (plan's Item-2 rider) and a pin that it emits `0.0`, not `null`. INV-6, Risks, D2/component
  note, validation updated. Materializer carries `default_value` as a string.
- **F3 — synthetic/real collision under-specified.** RESOLVED via ruling 3: a synthetic attr
  never overwrites a real captured design attribute; on QN or `(name, parent_part)` collision
  the real one wins and the materializer WARNs (REQ-SVM-03, precedence step 4). Pinned by a
  constructed-collision test.
- **F4 — (d)'s `_find_literal_redefinition` reuse overstated.** RESOLVED via ruling 4: add
  the direct-owner leg `redef.owning_part_qn == calc.owning_part_def_qn` (leg 2b); do not rely
  on the Strategy-2 name-fallback. Pinned by `'Flow Sub'` (`8.0`). B4, data-flow, precedence,
  component updated.
- **F5 — non-literal skip loudness not stated.** RESOLVED via ruling 5: count-summary WARN,
  Item-5 sentinel style ("scanned N: M literal applied, K non-literal skipped (deferred: <list>)");
  a referenced non-literal falls through to V11. Zero skipped → INFO-only, silent-on-clean holds.
  REQ-SVM-04, INV-7, Non-Goals updated.
- **F6 (minor) — B2 evidence.** RESOLVED: B2 now cites the matcher keying on `source_path` and
  ignoring `param_name` (`:701-710`) and leans on the new renamed-consumer fixture, not the
  same-name test.
- **F7 (minor) — SC-3 runner interface unpinned.** RESOLVED: `run_pipeline(package_dir, inputs)
  -> dict[str, float]` pinned in Component Overview as the Item-3 reuse contract; only the
  teax-vs-fixture-local driver form stays a plan-time open.
- **F8 (non-must-fix) — baseline-drift argument thin.** ACKNOWLEDGED: no design change; the
  SC-5 capture-diff review ("expected zero, verify each diff") is the mitigation, kept explicit.

---
Next Step: After approval → `/_my_plan`
