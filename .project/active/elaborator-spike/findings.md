# Spike: Elaborator go/no-go (ELABORATE-FIRST Item 3)

**Date**: 2026-08-07 · **Branch**: `source-identity-epic` @ `b5422ff` · **Author**: spike session
**agentic-mbse**: `elaborate-first-salvage` @ `65a35d7` (required — 5-tuple + ResolvedTargetFact)

## Summary of Findings

**Verdict: the assumption is CONFIRMED. No kill criterion triggered. [AGENT] recommendation: GO**
(the go/no-go checkpoint itself is the owner's; recorded below as pending).

A **381-line throwaway elaborator** (`elab_prototype.py`) — occurrence expansion via the existing
`PartInstanceIndex`, innermost-wins redefinition application, and referent-to-node resolution over
the Item-2 salvaged evidence — passed **every product-behavior check** on all three fixture legs,
and the **real generation layer rendered pipeline YAML + registry from the projected
`ComputationGraph` untouched**:

1. **Customer collapse (C25)**: `def_authored_calc` and `usage_authored_calc` — different binding
   contexts, different referent classes — resolve to the SAME node
   (`avail_ctx__avail_plant__availability`, value 0.8 from the occurrence override). The generated
   YAML wires both modules to ONE `design_params` input. The stamp-route consumer stays a node
   reference (no literal identity theft); the authored literal stays a distinct literal.
2. **C8 twins**: two occurrences, two nodes, 11.0 / 22.0 — distinct by construction.
3. **C24**: the chain to `producer_calc.result` becomes a producer edge; no input minted.
4. **C19 (the fixture the string pipeline cannot fix)**: the def-relative deep-path
   `:>> source.reading = 80.0` lands on `the_design__panel__source__reading` via the def-context
   remap rule, and BOTH the calc and the constraint consumer read that node.
5. **`in gain = gain` (fusion_tea)**: elaboration fails loudly with `SI_SELF_BINDING` naming every
   offending binding. No rescue, no reinterpretation — the owner ruling enforced at zero code cost.
6. **Aggregation**: `sum(cell.cell_cost)` term evidence resolves against the three
   `bank__cell[i]__cell_cost` occurrence nodes (multiplicity handled by occurrence enumeration).
7. **Node IDs**: `instance_path`-based IDs identical across independent loads (37 nodes, 17 edges).

**Kill-criteria verdicts:**
- (a) *SysIDE fact missing* — NOT triggered. Every fact the elaborator needed was available
  (probe 0): referents, redefinition target QNs, occurrence expansion, chain root+members.
- (b) *Consumer-specific special-casing* — NOT triggered. Three referent classes, one rule each
  (chain: anchor root at innermost enclosing occurrence, descend members; def-level referent:
  innermost enclosing occurrence whose def declares it; usage-level referent: the owner usage's
  occurrence on the consumer's ancestor chain). One shared def-context remap rule serves override
  anchoring AND calc placement — and that rule *is* the C19 fix.
- (c) *Projection rejected* — NOT triggered. `generate_pipeline_yaml` + `generate_registry`
  accepted the projected graph with zero generation-layer changes.

**Scale signal**: 381 scratch lines cover what matters, vs. the 742-line manifest layer that
controlled nothing. The production elaborator will be bigger (constraints catalog, expression
attributes, diagnostics), but the core is small.

**Owner go/no-go checkpoint: PENDING.**

## Question / Goal

**Assumption under test:** one elaboration pass over the live SysIDE AST — occurrence
expansion + innermost-wins redefinition application + referent-to-node resolution — produces an
instance graph from which a thin projection yields a valid `ComputationGraph`, with the existing
generation layer untouched.

**Product-behavior checks (from the epic's Item 3):**
1. Customer shape (`source_identity_mixed_consumers` C25 + stamp route): consumers of one
   modeled value converge on ONE node → one public input; C8 twins stay TWO nodes (11.0 / 22.0).
2. `nested_occurrence_override_probe` (C19): the deep-path `:>> source.reading = 80.0` lands on
   the node both the calc and the constraint read.
3. Aggregation (`mixed_consumers` Bank): `sum(cell.cell_cost)` resolves to the three
   `cell[i].cell_cost` occurrence nodes.
4. `fusion_tea`: `in gain = gain` self-binding → hard diagnostic, never reinterpreted.
5. Node-ID probe: `InstanceOccurrence.instance_path` works as a stable node ID.
6. Projection: a `ComputationGraph` built from the instance graph is accepted by the existing
   generation layer unchanged.

**Kill criteria (written before work; from the epic):**
- (a) SysIDE cannot supply a fact the elaborator needs at a probe site.
- (b) Def-referent contextualization requires consumer-specific special-casing rather than one
  rule.
- (c) The projection cannot produce a valid `ComputationGraph` the existing generation layer
  accepts unchanged.

## Log

### Probe 0 — input survey (`probe0_survey.py`, `probe0b_constraints_aggs.py`)

Ran both against `source_identity_mixed_consumers` (licensed). Facts established:

- **Occurrences**: `PartInstanceIndex` renders exactly the node IDs we need —
  `source_identity_mixed_consumers__bank__cell[0..2]` with per-step `occurrence_index`;
  `PathStep(owning_def_qn, feature_name, occurrence_index)`.
- **Override capture**: every `RedefinitionData` carries `member_qualified_name` +
  `redefined_target_qns` (exact raw QNs; deep path = the chain `('Deep Panel'::deep_rig,
  Rig::gain_setting)`). Override owner paths are **definition-relative** for def-nested usages
  (`...__Deep_Design__panel_two`) — the C19 mismatch, which the elaborator resolves by
  def-context expansion (longest def-key prefix → occurrence paths).
- **Calc evidence**: expanded usages carry occurrence-level referents (`'Twin Bay'::sensor_a::
  reading`, chain root `'Twin Bay'::sensor_a`) — exactly what node resolution needs.
- **DISCOVERY**: calcs declared inside part *usages* (`bare_calc`, `child_calc`,
  `usage_authored_calc`) come out of the legacy extractor **definition-relative**
  (`...__Bare_Station__bare_rig__bare_calc`, `owner_def=None`) — the legacy expansion misses
  them. The elaborator must do its own def-context remap for calc nodes too (same rule as
  overrides — one rule, reused).
- **Aggregation terms**: every term (SUM/SINGLETON/LOCAL) carries leaf + chain root + member
  names after the Item-2 salvage — the recovery report's C24 chain-root gap is closed.
- **Constraints**: `elements_of_type(model, "ConstraintUsage", include_subtypes=True)` is the
  correct sweep (plain `"ConstraintUsage"` misses `AssertConstraintUsage` — probe 0's empty
  result was that flag, not missing data).

## Reproduction

All probes run from the repo root with the license sourced:

```bash
set -a && source /home/reid/1cfe/agentic-mbse/.env && set +a
uv run python .project/active/elaborator-spike/<probe>.py
```

Requires agentic-mbse checked out on `elaborate-first-salvage` (the editable install reads that
working tree).

### Probe 1 — mixed_consumers product checks (`probe1_mixed_consumers.py`)

22/22 PASS on first run: C25 collapse, C8 distinctness, C24 producer edge, C12/C13/C15
contextualization, stamp vs authored literal, C11 chain + constraint convergence, deep-path 43.0,
Bank cells, one-node-two-consumers count. Zero diagnostics. 20 attr nodes, 17 calc/constraint
nodes.

### Probe 2 — C19 + self-binding (`probe2_c19_and_selfbinding.py`)

5/5 PASS: 80.0 on `the_design__panel__source__reading` (value_site=occurrence_override), calc
`noop.x` and constraint `within.v` both read that node; fusion_tea elaboration raises
`ElaborationError("SI_SELF_BINDING: ...")` listing every self-bound param (via the salvaged
`screen_source_readiness`).

### Probe 3 — projection acceptance (`probe3_projection.py`)

Projected 12 calc modules + 10 entry points into a real `ComputationGraph`;
`generate_pipeline_yaml` + `generate_registry` (real template env, `cli._get_template_env`)
rendered without modification. YAML asserts: one availability input consumed by both consumers, no
minted `computed_calc__value_in`, producer channel present, twins distinct. Iteration notes:
`entry_point_groups` is a list; modules need `calc_def_qualified_name` for the registry template;
`generate_registry` returns text (caller writes). Output kept in `projection_out/`.

### Probe 4 — node-ID stability (`probe4_node_id_stability.py`)

Two independent extractor loads → identical 37 node IDs, 17 edges, values, and value sites.

## Open Questions / Follow-ups

- **Constraint catalog projection** not probed (Item 4 design scope) — constraint *binding
  resolution* is proven; catalog assembly + report aggregator projection is not.
- **Expression-valued redefinitions** (`:>> station_total = rig.gain_setting + 100.0`) were not
  folded into computed-attribute nodes; term-level evidence resolution is proven, full
  aggregation/FORMULA module projection belongs to Items 4–5.
- **Legacy extractor inconsistency discovered**: calcs declared inside part *usages*
  (`bare_calc`, `child_calc`, `usage_authored_calc`) come out definition-relative
  (`owner_def=None`) — the legacy expansion misses them. The elaborator's remap handles it; the
  Item-4 design should decide whether production elaboration keeps consuming
  `extract_calculation_usages` or walks calc usages off the AST directly.
- **Cross-package EXPOSE / multi-file models** not probed — Item 5 breadth learning tests.
- **Multi-occurrence definition-default ruling** (one shared input vs per-occurrence) — still the
  owner question the epic names; this fixture set never forces it.
