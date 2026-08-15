---
date: 2026-07-19 21:58 PDT
researcher: Claude
topic: "Gate B vacuity probe — can append-only constraint extension introduce a new V11 violation?"
tags: [spike, gate-b, v11, constraint-extension, lifecycle-item-3]
status: complete
branch: constraint-exec-epic
candidate: 3700fee (src/ byte-identical at run commit 14f042c)
last_updated: 2026-07-19
---

# Spike: Gate B vacuity — can constraint extension introduce a new V11 violation?

## Summary of Findings

**Verdict: vacuous.** Under current semantics at candidate `3700fee`, append-only constraint
extension cannot introduce a new V11 coverage violation. Every offender the extension-time check
can ever report is already present in the input graph, so the check has no reachable job. The
epic's step 3 branch resolves to *delete extension-time coverage validation*, not to build a
differential.

The proof is a reachability argument closed by construction, not an absence of counterexamples:

1. **Only appended module inputs could be new offenders.** Extension deep-copies the base modules
   and copies `fallback_entry_points` verbatim (`constraint_lowering.py:1499`), so every baseline
   offender is preserved exactly and none is added by the copy.
2. **Only two of the three appended-input paths can even be `entry_point`-sourced.**
   MODULE_OUTPUT inputs and every aggregator input are `module_output`, which V11's predicate
   never inspects.
3. **The MODELED_DEFAULT path mints a fresh synthetic key.** It can be valueless, and extension
   *does* raise if that key is forced into the fallback set (probe 4) — but the key is
   `{constraint_id}__{formal}`, and `constraint_id` ends in a 16-hex SHA-256 segment. The fallback
   set has exactly one writer (`dependency_backtracker.py:603`) and every member is
   `{calc_module_eqn}__{formal}`. Colliding needs a SHA-256 preimage.
4. **The DESIGN_ATTRIBUTE path cannot reach a fallback key.** Its identity is always a key of
   `design_attr_by_qn` (`producer_resolution.py:561`). Across 35 live fixture models — 60 fallback
   QNs, 846 design-attribute QNs — the intersection is empty (probe 2). Both constructible ways to
   force a collision are blocked at extraction (probe 3): two same-named members in one namespace
   are rejected outright, and a design attribute whose *name* embeds the `__` separator has it
   sanitized to `_`, so it lands in a different string than the `__`-joined fallback key.

A second, independent block also holds for the non-colliding case: a valueless usage-owned design
attribute is not extracted into the design-attribute index at all, so a constraint actual cannot
resolve to one — strict resolution raises INV-2 instead (probe 3, variants B and B″).

**What this means for the three shapes both Gate B reports name.** Shape A (pre-existing/unrelated)
reproduces exactly as reported — extension rejects a graph whose only offender is pre-existing.
Shapes B (newly consumed) and C (mixed) are *not constructible from a model*: they exist only when
the constraint input is hand-forged at the object layer (probe 1). The reports' "required negative
regression" — a pre-existing unwired fallback key newly consumed by a constraint, extension must
fail — has no model that produces it. That regression should not be written.

Outputs 2, 3, and 4 are below.

---

## Question / Goal

**Assumption under test.** Append-only constraint extension can introduce a new V11 violation, and
so extension-time coverage validation needs a differential (reject only introduced offenders)
rather than deletion.

**What would confirm it.** A constructed, runnable model at `3700fee` in which
`extend_graph_with_constraints` reports a V11 offender that `collect_uncovered_params` does not
report on the input graph.

**What would refute it.** A closed enumeration of every way an appended module input can satisfy
V11's predicate, with each path shown unreachable from a real model.

**Ground truth inherited (per the brief, not re-derived).** V11 fires only on calculation QNs;
`_fallback_entry_points.add` has exactly one writer; constraint actuals resolve strictly and never
mint a fallback entry point.

---

## Log

### Step 0 — pin the candidate

`git diff --stat 3700fee HEAD -- src/ tests/` is empty. The run commit `14f042c` is a docs-only
commit on top of the candidate, so every result below is at `3700fee` semantics.

### Step 1 — restate V11's predicate exactly

`collect_uncovered_params` (`graph_builder.py:806-851`) flags a module input when all three hold:

- `source.source_type == "entry_point"` with a non-empty `qualified_name`,
- that QN is in `graph.fallback_entry_points`,
- the entry point carries no value (`default_value is None`).

`extend_graph_with_constraints` (`constraint_lowering.py:1332-1506`) deep-copies base modules,
appends constraint and aggregator modules, copies `fallback_entry_points` unchanged (`:1499`), then
runs `_validate_channel_references` (`:1502`) and the collector (`:1503-1505`).

So a **new** offender must be an appended module input. Nothing else changes.

### Step 2 — probe 1: run the three reported shapes

`probes/p1_shapes.py` (license-free). Builds the fusion rollup shape as real `ComputationGraph` and
`ConcreteConstraint` objects and calls the real extension function.

```
uv run python .project/active/constraint-lifecycle-gate-b/probes/p1_shapes.py
```

```
=== A  pre-existing / unrelated ===
  base graph V11 offenders (baseline): ['plant_params.plant__lcoe_calc__total_capital']
  extend_graph_with_constraints RAISED CodeGenerationError
    V11 coverage violations in extended graph: [UncoveredInput(module='lcoe_calc', ...)]

=== B  newly consumed (forced) ===
  base graph V11 offenders (baseline): []
  extend_graph_with_constraints RAISED CodeGenerationError
    V11 coverage violations in extended graph: [UncoveredInput(module='cb', input='total_capital', ...)]

=== B' control (safe constraint) ===
  base graph V11 offenders (baseline): []
  extend SUCCEEDED; extended V11 offenders: []

=== C  mixed (forced) ===
  base graph V11 offenders (baseline): ['plant_params.plant__lcoe_calc__total_capital']
  extend_graph_with_constraints RAISED CodeGenerationError
    ... [UncoveredInput(module='lcoe_calc', ...), UncoveredInput(module='cc', ...)]
```

Shape A reproduces the reported collision. Shapes B and C show extension *would* report a genuinely
new offender — but only because probe 1 hand-sets `design_attribute_qn` to the fallback key. That
is a forged lower-layer object. Whether a model can produce it is the entire question, and Step 3
onward answers it.

**Reduction.** An appended constraint input is `entry_point`-sourced only via
`ConstraintInputResolution.DESIGN_ATTRIBUTE` (QN = `inp.design_attribute_qn`,
`constraint_lowering.py:1401-1415`) or `MODELED_DEFAULT` (QN = `{constraint_id}__{formal}`,
`:1416-1421`). Aggregator inputs are all `module_output` (`:1464-1471`). So:

> Can a DESIGN_ATTRIBUTE or MODELED_DEFAULT mint produce a QN that is in `fallback_entry_points`
> **and** resolves to a valueless entry point?

### Step 3 — probe 2: is the namespace disjoint across the whole corpus?

`probes/p2_reachability.py` runs the live public path `build_pipeline_context` over every fixture
model directory and intersects `fallback_entry_points` with the design-attribute QN index.

```
set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a
uv run python .project/active/constraint-lifecycle-gate-b/probes/p2_reachability.py
```

```
models built: 35   skipped: 10
total fallback EP QNs: 60   total design-attribute QNs: 846
COLLISIONS (design attr QN that is also a fallback key): 0
```

The 10 skips are fixtures that fail by design (no calc defs, deliberate profile/collision guards);
they are named in the run output. Every model that builds shows `intersection=0`. Representative
pairs from the output:

```
solar_battery_model  fallback 'SolarBatteryDesign__solar_battery_plant__annualized_financial__discount_rate'
                     design_attr 'SolarBatteryDesign__solar_battery_plant__discount_rate'
ife_plant            fallback 'IfePlantDesign__baseline_plant__chamber_a__yield_calc__blanket_multiple'
                     design_attr 'IfePlantLib__Base_Driver__bank_energy'
```

The shape is consistent: a fallback key always carries a **calc-usage segment** the design-attribute
QN does not have. Empirical zero is not a proof, so Step 4 tries to break it.

### Step 4 — probe 3: force the collision from a real model

`probes/p3_forced_collision.py`, with the model sources in `probes/collision_model/`,
`probes/collision_control/`, and `probes/collision_sep/`.

```
set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a
uv run python .project/active/constraint-lifecycle-gate-b/probes/p3_forced_collision.py
```

**Vector A — two same-named members in one namespace.** A calc usage `the_rig` and a part usage
`the_rig` in the same package, so the part's `gain` attribute would have QN
`GateBCollision__the_rig__gain` — the same string as the calc's fallback key.

```
=== A same-name siblings ===
  REJECTED before extension: CodeGenerationError
    usage-owned constraint's owner 'the_rig' has no qualified name — an expected instance cannot be formed

=== A' control (renamed) ===
  fallback_entry_points : []
  design attribute index: {'GateBCollision__Scaler__scaled': None, 'GateBCollision__the_rig__gain': '7.0'}
  INTERSECTION          : []
    constraint input v <- entry_point GateBCollision__the_rig__gain
  V11 offenders on the built (already extended) graph: []
```

The control isolates the cause: renaming the calc usage makes the identical model build and
generate cleanly, so the duplicate name — not anything else in the model — is what extraction
rejects.

**Vector B — a design attribute whose name embeds the `__` separator.** No duplicate names. A calc
usage `scaler` with a self-named binding falls through to `GateBSep__the_host__scaler__gain`; an
attribute literally named `scaler__gain` on the same part would join to the same string.

```
=== B separator, valueless ===
  REJECTED before extension: CodeGenerationError
    GateBSep__the_host.v: unresolved actual 'scaler__gain' (strict mode: no fallback, no
    entry-point synthesis — INV-2)

=== B' separator, valued ===
  fallback_entry_points : ['GateBSep__the_host__scaler__gain']
  design attribute index: {..., 'GateBSep__the_host__scaler_gain': '3.0'}
  INTERSECTION          : []
    EP GateBSep__the_host__scaler__gain  USAGE_LITERAL  default=40.0
    EP GateBSep__the_host__scaler_gain   DESIGN_ATTRIBUTE  default=3.0
    constraint input v <- entry_point GateBSep__the_host__scaler_gain
  V11 offenders on the built (already extended) graph: []

=== B'' separator, valueless, no assert ===
  fallback_entry_points : ['GateBSep__the_host__scaler__gain']
  design attribute index: {'GateBSep__Scaler__scaled': None, 'GateBSep__the_host__gain': '40.0'}
```

Two independent blocks, visible side by side:

- **Name sanitization.** `scaler__gain` becomes QN `..._scaler_gain` (single underscore), while the
  fallback key is `..__scaler__gain`. The design-attribute QN namespace cannot reproduce a
  `__`-joined fallback key from a name that contains `__`.
- **Valuelessness is unreachable on this path.** In B″ the valueless attribute `scaler__gain` is
  absent from the design-attribute index entirely. That is why B (valueless) raises strict-unresolved
  while B′ (the same model with `= 3.0`) resolves. A constraint actual can only resolve to a
  *valued* design attribute, so a freshly minted DESIGN_ATTRIBUTE entry point always carries a
  value and fails V11's second leg.

Scope note on the second block: it closes the fresh-mint case, not the reuse case.
`mint()` returns early for a QN already in a group (`constraint_lowering.py:1371-1372`) without
updating its default, so under a hypothetical QN collision the reused valueless entry point would
survive. The QN-collision block is therefore the load-bearing one; valuelessness is a second,
independent block covering the rest of the space.

### Step 5 — probe 4: the MODELED_DEFAULT mint

`probes/p4_modeled_default.py` (license-free). A modeled default whose IR is not a plain literal
makes `_literal_float` return `None`, so this is the one place extension mints a *valueless* entry
point.

```
uv run python .project/active/constraint-lifecycle-gate-b/probes/p4_modeled_default.py
```

```
=== real: synthetic QN not in fallback set ===
  minted EP plant__p__safe__0123456789abcdef__threshold  LIBRARY_DEFAULT  default=None
  V11 offenders: []

=== counterfactual: synthetic QN forced into fallback set ===
  extend RAISED CodeGenerationError: V11 coverage violations in extended graph: [...]
```

So the path mints valueless, and extension does raise when the key is in the fallback set — but the
key is `{constraint_id}__{formal}` where `constraint_id` is
`{instance_path}__{source_local}__{sha256[:16]}` (`constraint_lowering.py:204-223`), and every
fallback-set member is `{calc_module_eqn}__{formal}` from the lenient calculation consumer. A
collision requires a calc usage whose EQN ends in a specific 16-hex SHA-256 digest of the
constraint's own canonical tuple. Structurally expressible, cryptographically unreachable.

### Step 6 — what deleting the check would break

`grep` for `collect_uncovered_params` across `src/` and `tests/`: no test asserts the
extension-time raise. `tests/unit/test_constraint_graph_extension.py:240-255` is named
`test_v11_violation_raises_on_uncovered_module_output` but its own docstring and its
`pytest.raises(ValueError, match="power_calc")` show it exercises `_validate_channel_references`,
which stays. Deletion has zero existing test surface.

---

## Output 2 — what becomes deletable, and every caller

Deletable, and nothing else:

- `src/sysml_codegen/analysis/constraint_lowering.py:1503-1505` — the
  `collect_uncovered_params(extended)` call and its `raise _generation_error(...)`.
- `src/sysml_codegen/analysis/constraint_lowering.py:1359` — the `collect_uncovered_params` name in
  the function-local import. Keep `_validate_channel_references` on `:1358` and its call on `:1502`
  (LC-E03).
- `src/sysml_codegen/analysis/constraint_lowering.py:1353-1355` — the docstring sentence claiming
  the function re-runs the collector.

`collect_uncovered_params` itself is **not** deletable. Its remaining production caller is the
final generation gate, which LC-E04 requires unchanged:

- `src/sysml_codegen/cli/__init__.py:263, 278` — `_reconcile_params_coverage`.

Both callers of `extend_graph_with_constraints` are covered by changing the function body, so
neither call site needs an edit:

- `src/sysml_codegen/orchestration/pipeline_builder.py:996-1004` (live capture, behind
  `if concrete_constraints:`).
- `src/sysml_codegen/snapshot/graph_rebuild.py:213-225` (from-snapshot rebuild).

Test callers of the collector (all unaffected — they call it directly, not through extension):
`tests/unit/test_uncovered_params.py`, `tests/conformance/test_plant_values.py`,
`tests/conformance/test_plant_value_shapes.py`, `tests/conformance/test_deep_cross_scope_probe.py`,
`tests/conformance/test_fusion_tea_snapshot.py`,
`tests/conformance/test_constraint_pipeline_threading.py`, `tests/conformance/test_ife_plant.py`.

## Output 3 — introduced-violation identity

Not owed: the verdict is vacuous, so no differential check is built and nothing needs a semantic
identity to key on. Recorded for the counterfactual only: if a later change makes the QN collision
reachable (see Output 4), the identity that would distinguish an introduced offender is
`(module name, input param_name, entry-point QN)` — not the QN alone, because shape C in probe 1
shows the same QN appearing as both a baseline offender and a new one on different modules, which a
QN-keyed multiset difference would cancel to zero.

## Output 4 — V11-widening disposition (Item 2 PC-3 context)

Two widenings, opposite answers:

- **Widening the writer to other lenient consumers** (the aggregation consumer, per the I10 note at
  `dependency_backtracker.py:598-603`) does **not** change extension-time behavior. Those keys are
  minted by `entry_point_qualified_name` in the same `{consumer_eqn}__{key}` family
  (`producer_resolution.py:462-474`), so they stay disjoint from design-attribute QNs by the same
  sanitization and namespace arguments, and stay unreachable from a constraint actual. Vacuity holds
  and this item's deletion stands.
- **Widening membership to design-attribute QNs** — letting a design attribute itself land in
  `fallback_entry_points` — breaks vacuity immediately. Probe 1 shape B becomes reachable from a
  model, and extension-time V11 acquires a real job. Any change that puts a design-attribute QN into
  the fallback set must re-open this item.

The dividing line is therefore not "calculation QNs" as such, but whether the fallback set and the
design-attribute index can ever share a key. As long as fallback membership is restricted to
consumer-minted `{consumer_eqn}__{key}` strings, extension-time V11 stays vacuous.

---

## Reproduction

From the repo root at `3700fee` (or any commit where `git diff 3700fee HEAD -- src/` is empty):

```bash
# license-free
uv run python .project/active/constraint-lifecycle-gate-b/probes/p1_shapes.py
uv run python .project/active/constraint-lifecycle-gate-b/probes/p4_modeled_default.py

# licensed (live extraction)
set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a
uv run python .project/active/constraint-lifecycle-gate-b/probes/p2_reachability.py
uv run python .project/active/constraint-lifecycle-gate-b/probes/p3_forced_collision.py
```

`p2` takes a few minutes (35 live model builds). `p3` writes each variant to a temp dir, so the
`.sysml` sources under `probes/` are inputs only — nothing is added to `tests/`.

No production code was changed and no fixture was committed to `tests/`.

## Open Questions / Follow-ups

- **`shared_producer`'s fixture comment looks stale.** Its header says neither consumer reaches a
  terminal miss, but probe 2 reports `fallback=1` with
  `SharedProducer__the_rig__scaler__gain` on it — the calc's self-named binding does fall through.
  This does not affect the verdict (the constraint still resolves positively to a different,
  valued QN), but the fixture's stated invariant and its live behavior disagree. Worth a look from
  whoever owns Item 2's I9 evidence.
- **Name sanitization as a load-bearing guard.** The `__` → `_` collapse is what closes collision
  vector B. It is currently an entry-point-naming convenience, not a documented V11 precondition.
  If the deletion in Output 2 lands, nothing downstream depends on it for coverage — but if the
  widening in Output 4 ever happens, it becomes safety-critical and should be stated as such.
- **The 10 skipped fixtures in probe 2** fail for their own designed reasons before a graph exists,
  so they contribute no evidence either way. None of them is a constraint-plus-deferred-input shape.
