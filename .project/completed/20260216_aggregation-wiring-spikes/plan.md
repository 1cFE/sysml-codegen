# Implementation Plan: Aggregation Wiring Diagnostic Spikes

**Status:** Complete (all 4 phases done)
**Created:** 2026-02-16
**Last Updated:** 2026-02-16

## Source Documents

- **Spec:** `.project/active/aggregation-wiring-spikes/spec.md`
- **Research (full scope):** `.project/research/20260216-001500_aggregation-wiring-full-scope-analysis.md`
- **Research (misclassification):** `.project/research/20260216-aggregation-expression-misclassification.md`
- **Algorithm doc:** `.project/reports/08_algorithm_revised.md` (Section 12: Key Format Specification)
- **Existing spike pattern:** `scripts/spike_aggregation_validation.py`

## Implementation Strategy

**Phasing Rationale:**
H1 (FCE-is-subtype-of-OE) is the foundational hypothesis — if falsified, Spikes B
and D need redesign. So Phase 1 tests H1 first. H2 (check reorder) quantifies the
fix and must precede H4 (plant-level resolution) which applies the fix. H3
(sibling agg resolution) is independent and can run after shared infra exists.

**Architecture Decision: Single script, shared context.**
All 4 spikes share one `build_pipeline_context()` call (~10s model load). Each spike
is a function returning a structured verdict dict. A `main()` runner calls them in
sequence and prints a consolidated report.

**Validation Approach:**
Each spike produces a `dict` with `hypothesis`, `verdict` (CONFIRMED/FALSIFIED),
`evidence` (structured data), and `notes` (human-readable explanation). The runner
prints a summary table at the end.

---

## Phase 1: Common Infrastructure + Spike A (H1: FCE is subtype of OE)

### Goal

Build the shared script skeleton and test the foundational hypothesis. If H1 is
falsified, we stop and reassess before writing Spikes B-D.

### Validation Stencil (What Spike A Must Produce)

```python
# Spike A output structure:
{
    "hypothesis": "H1: FCE is subtype of OE in SysIDE type system",
    "verdict": "CONFIRMED" | "FALSIFIED",
    "evidence": {
        "nodes_tested": 37,          # total non-sum term nodes examined
        "dual_match_fce_and_oe": 37,  # nodes matching BOTH types
        "fce_only": 0,               # nodes matching FCE but not OE
        "oe_only": 0,                # nodes matching OE but not FCE
        "node_details": [
            {
                "assembly": "solar_array",
                "attribute": "capital_cost",
                "node_text": "array_bos.capital_cost",
                "is_oe": True,
                "is_fce": True,
                "operator": ".",
                "target_feature": "capital_cost",
                "operand_0_type": "FeatureReferenceExpression",
            },
            # ...
        ],
    },
}
```

### Changes Required

#### 1. Create spike script
**File:** `scripts/spike_agg_wiring_h1_h4.py` (NEW)

- [x] Script header, imports, `REPO_ROOT` / `MODEL_PATH` constants
- [x] `_load_context()` — calls `build_pipeline_context([MODEL_PATH])`, validates
      `.output_registry` and `.aggregation_expressions` are populated
- [x] `_print_verdict(result: dict)` — formatted output helper
- [x] `spike_a_ast_dual_match(ctx: PipelineContext) -> dict` implementing:
  - Iterate `ctx.aggregation_expressions`
  - For each `ScopedAggregationData`, get `expression.raw_expression_text` and
    the original `RedefinitionData.expression_ast` from `ctx.hierarchy_data`
  - Walk the AST nodes that correspond to non-sum operands in the `+` tree
  - For each leaf node, check `SysideAdapter.is_instance(node, "OperatorExpression")`
    and `SysideAdapter.is_instance(node, "FeatureChainExpression")`
  - Collect `operator`, `target_feature.name`, `operands[0]` type
  - Produce verdict dict per stencil above

**Key implementation detail:** To get the raw AST nodes, we need the
`RedefinitionData.expression_ast` from hierarchy extraction. Access via:
```python
hierarchy_data = ctx.hierarchy_data
for redef in hierarchy_data.redefinitions:
    if redef.redefinition_type == RedefinitionType.EXPRESSION:
        # redef.expression_ast is the raw SysIDE AST root node
```
Then walk the `+` operator tree to find leaf nodes (the non-sum operands).
SumTerms are wrapped in `InvocationExpression(func="sum")` — skip those.
The remaining leaf nodes are the ones we test for dual-match.

**Implementation note:** The `+` tree walker must check FCE *before* OE
to collect dotted refs as leaves. SysIDE's `operator` attribute on
OperatorExpression uses a type that doesn't compare with Python `==`
against string literals (despite printing as `+`). The FCE-first approach
avoids this by checking type identity rather than operator value.

- [x] `main()` — loads context, runs spike_a, prints verdict, exits early if FALSIFIED
- [x] `if __name__ == "__main__": main()`

### Validation

**Automated:**
- [x] `uv run python scripts/spike_agg_wiring_h1_h4.py` → runs without error
- [x] Spike A verdict printed with node-level detail table

**Manual:**
- [x] Verify node count aligns with research (expect ~37 non-sum leaf nodes)
      → CONFIRMED: 37 dual-match nodes + 9 genuinely local = 46 total
- [x] Verify every standalone dotted ref (e.g., `array_bos.capital_cost`) shows
      `is_oe=True, is_fce=True` → CONFIRMED: all 37 dotted refs are dual-match
- [ ] Cross-reference against SysML source (`library.sysml` lines 615-763)

**Gate:** If H1 is FALSIFIED, stop. Do not proceed to Phase 2.

**What We Know Works After This Phase:**
- Model loads and `PipelineContext` is fully populated
- We have empirical proof of whether FCE nodes match the OE type check
- The script skeleton is ready for Spikes B-D

---

## Phase 2: Spike B (H2: Check Reorder Produces ~37 Reclassifications)

### Goal

Measure the exact impact of moving the FCE check before the OE check in
`_walk_aggregation_ast()`. Confirm ~37 LocalTerms become SingletonTerms with
zero regression in the 12 working SumTerms.

### Validation Stencil

```python
{
    "hypothesis": "H2: Check reorder reclassifies ~37 LocalTerms to SingletonTerms",
    "verdict": "CONFIRMED" | "FALSIFIED",
    "evidence": {
        "before": {"sum_terms": 12, "singleton_terms": 0, "local_terms": 46},
        "after":  {"sum_terms": 12, "singleton_terms": 37, "local_terms": 9},
        "sum_term_regression": False,       # CRITICAL: must be False
        "reclassified_terms": [
            {
                "assembly": "solar_array",
                "attribute": "capital_cost",
                "was": "LocalTerm(attribute_name='array_bos')",
                "now": "SingletonTerm(source_path='array_bos.capital_cost')",
            },
            # ...
        ],
        "remaining_local_terms": [
            # These should be genuinely local: misc_hardware_cost,
            # capital_cost/raw_material_cost in idiot_index, etc.
        ],
    },
}
```

### Changes Required

**File:** `scripts/spike_agg_wiring_h1_h4.py` (ADD function)

- [x] `spike_b_check_reorder(ctx: PipelineContext) -> dict` implementing:
  - Import `_walk_aggregation_ast`, `_AggregationContext`, `_unwrap_invocation`
    from `hierarchy_resolver` (or copy the function locally)
  - **Before run:** For each `ScopedAggregationData`, collect current term counts
    from `agg.expression.{sum_terms, singleton_terms, local_terms}`
    (these were produced by the CURRENT code ordering)
  - **After run:** Create a local copy of `_walk_aggregation_ast` with FCE check
    moved before OE check. Re-walk each `RedefinitionData.expression_ast` using
    the patched function with the same `mult_lookup`. Collect new term counts.
  - Compare before/after:
    - `sum_terms` count MUST be identical (zero regression check — FR-4)
    - Count LocalTerms that became SingletonTerms
    - List each reclassified term with before/after representation
    - List remaining LocalTerms (should be genuinely local)
  - Produce verdict dict per stencil above

**Key implementation detail:** The patched function is a LOCAL COPY — not a
monkey-patch of the module-level function. This ensures no side effects.
To build `mult_lookup`, use `ctx.hierarchy_data.multiplicities` keyed by
`part_usage_name`. The `expression_ast` is on the `RedefinitionData` objects
in `ctx.hierarchy_data.redefinitions` where `redefinition_type == EXPRESSION`.

- [x] Update `main()` to call `spike_b` after spike_a (only if H1 confirmed)

### Validation

**Automated:**
- [x] `uv run python scripts/spike_agg_wiring_h1_h4.py` → Spikes A+B run
- [x] SumTerm count identical before/after (12 == 12)
- [x] Reclassified terms list printed with dotted source paths

**Manual:**
- [x] Verify reclassified count is ~37 (research report 2 prediction)
      → CONFIRMED: exactly 37 reclassified
- [x] Verify each reclassified SingletonTerm has a correct dotted path
      (e.g., `array_bos.capital_cost`, not just `array_bos`) → CONFIRMED
- [x] Verify remaining LocalTerms are genuinely local attributes
      (e.g., `misc_hardware_cost`, `capital_cost` in idiot_index) → CONFIRMED: 9 remaining

**What We Know Works After This Phase:**
- Exact count of terms affected by the fix
- Proof that SumTerms don't regress
- The complete list of terms that change classification (for the fix design doc)

---

## Phase 3: Spike C (H3: Sibling Agg Outputs in Registry)

### Goal

Prove that when `_build_aggregation_module()` processes idiot_index LocalTerms,
the OutputRegistry already contains the sibling aggregation module outputs
(e.g., `solar_array.capital_cost`, `solar_array.raw_material_cost`).

### Validation Stencil

```python
{
    "hypothesis": "H3: Sibling agg outputs resolvable via Key_D at LocalTerm processing time",
    "verdict": "CONFIRMED" | "FALSIFIED",
    "evidence": {
        "assemblies_tested": ["solar_array", "battery_system", "site_infra", "solar_battery_plant"],
        "queries": [
            {
                "assembly": "solar_array",
                "expression": "idiot_index",
                "local_term": "capital_cost",
                "key_d_query": "solar_array.capital_cost",
                "key_d_result": "solarb...design__solar_battery_plant__solar_array__capital_cost__capital_cost",
                "resolved": True,
            },
            {
                "assembly": "solar_array",
                "expression": "idiot_index",
                "local_term": "raw_material_cost",
                "key_d_query": "solar_array.raw_material_cost",
                "key_d_result": "solarb...design__solar_battery_plant__solar_array__raw_material_cost__raw_material_cost",
                "resolved": True,
            },
            # ... for all 4 assemblies × 2 terms = 8 queries
        ],
        "all_resolved": True,
    },
}
```

### Changes Required

**File:** `scripts/spike_agg_wiring_h1_h4.py` (ADD function)

- [x] `spike_c_sibling_agg_resolution(ctx: PipelineContext) -> dict` implementing:
  - Find all idiot_index aggregation expressions from `ctx.aggregation_expressions`
    (filter where `agg.expression.attribute_name == "idiot_index"`)
  - For each idiot_index expression, get its LocalTerms
    (`agg.expression.local_terms`)
  - Derive the `part_usage_name` from `agg.instance_path` (last `__` segment)
  - For each LocalTerm, query `ctx.output_registry.resolve()` with:
    - Key_D format: `f"{part_usage_name}.{l_term.attribute_name}"`
    - Also try double-attr canonical: direct lookup in `registry._canonical`
      for pattern `*__{attr}__{attr}`
  - Record which queries resolve and to what channel
  - Also check: is `misc_hardware_cost` on `solar_array.capital_cost` correctly
    NOT in the registry? (It's a genuine entry point)
  - Produce verdict dict per stencil above

**Key implementation detail:** Phase 1-4 registration completes during Step 5.5
inside `build_pipeline_context()`, before `_build_aggregation_module()` runs in
Step 7. The registry is read-only after Step 5.5 (no new registrations during
graph building). So sibling agg outputs registered in Phase 1b ARE available when
LocalTerms are processed in Step 7. The spike verifies this by checking specific
keys exist via `registry.resolve()`.

- [x] Update `main()` to call `spike_c` (independent of H1/H2 — always runs)

### Validation

**Automated:**
- [x] All 8 idiot_index LocalTerm queries resolve via Key_D
- [x] `misc_hardware_cost` does NOT resolve (confirms genuine entry point)

**Manual:**
- [x] Verify resolved channels match expected double-attr format
      → All 8 channels end with `__attr__attr` (e.g., `...solar_array__capital_cost__capital_cost`)
- [ ] Cross-reference channel names against `ctx.computation_graph.modules`

**What We Know Works After This Phase:**
- The registry key format supports sibling aggregation resolution
- The fix for Bug B (adding resolution before entry point creation) is feasible
- We know exactly which key format to use in the fix

---

## Phase 4: Spike D (H4: Plant-Level Resolution via Actual Code Path)

### Goal

Trace the real 3-step resolution code path in `_resolve_aggregation_input_channel()`
for plant-level aggregation references. Determine which step succeeds and whether
Key_E_stripped is needed for robustness.

### Validation Stencil

```python
{
    "hypothesis": "H4: Plant-level SingletonTerms resolve through actual resolution code path",
    "verdict": "CONFIRMED" | "CONFIRMED_WITH_CAVEAT" | "FALSIFIED",
    "evidence": {
        "plant_expressions_tested": 4,   # capital, raw_material, fabrication, installation
        "resolution_traces": [
            {
                "source_path": "solar_array.capital_cost",
                "instance_path": "SolarBatteryDesign__solar_battery_plant",
                "step_1_chain_redef": {
                    "attempted": True,
                    "result": "MISS",
                    "reason": "redef is EXPRESSION type, not CHAIN",
                },
                "step_2_scoped_key": {
                    "attempted": True,
                    "scoped_key": "solar_battery_plant.solar_array.capital_cost",
                    "result": "MISS",
                    "reason": "Key_E_stripped not registered",
                },
                "step_3_unscoped_key_d": {
                    "attempted": True,
                    "key_d": "solar_array.capital_cost",
                    "result": "HIT",
                    "channel": "...solar_array__capital_cost__capital_cost",
                },
                "final_result": "RESOLVED",
                "resolved_via": "step_3_unscoped_key_d",
            },
            # ... for all 12 plant-level terms
        ],
        "summary": {
            "resolved_via_step_1": 0,
            "resolved_via_step_2": 0,
            "resolved_via_step_3": 12,  # all via unscoped fallback
            "unresolved": 0,
        },
        "key_e_stripped_recommendation": "Implement for robustness — unscoped Key_D "
            "fallback works for solar_battery but could collide if two assemblies "
            "have identically-named sub-parts at different hierarchy levels.",
    },
}
```

### Changes Required

**File:** `scripts/spike_agg_wiring_h1_h4.py` (ADD function)

- [x] `spike_d_plant_level_resolution(ctx: PipelineContext) -> dict` implementing:
  - Import `_resolve_aggregation_input_channel` from
    `sysml_codegen.resolution.graph_builder` (confirmed exportable via `__all__`)
  - Find plant-level aggregation expressions from `ctx.aggregation_expressions`
    (filter where instance_path ends with `solar_battery_plant`)
  - From Spike B results, get the plant-level terms that would become
    SingletonTerms after Bug A fix (e.g., `solar_array.capital_cost`)
  - For each new SingletonTerm, call `_resolve_aggregation_input_channel()`
    with the actual parameters from the pipeline context:
    - `symbolic_ref`: the SingletonTerm source_path (e.g., `"solar_array.capital_cost"`)
    - `instance_path`: from the `ScopedAggregationData` (e.g., `"SolarBatteryDesign__solar_battery_plant"`)
    - `redefinitions`: from `ctx.hierarchy_data.redefinitions`
    - `output_registry`: from `ctx.output_registry`
  - **Additionally**, trace the 3 internal steps independently:
    - Step 1: CHAIN redef search — check if any redefs match with `redefinition_type == CHAIN`
      and attribute name matching the ref's part name
    - Step 2: Scoped key — construct `dotted_scope.symbolic_ref` and call `registry.resolve()`
    - Step 3: Unscoped Key_D — call `registry.resolve(symbolic_ref)` directly
  - Report which step succeeded for each term
  - Check for collisions: verify the resolved channel is an aggregation output
    (double-attr format), not a CalcUsage output
  - Produce verdict dict per stencil above

**Key implementation detail:** We call the REAL function (not a mock) — this
tests the actual code path that will execute after Bug A is fixed. The 3-step
trace is done separately as diagnostic instrumentation to understand WHY the
function returns what it returns.

The expected outcome is CONFIRMED_WITH_CAVEAT: all resolve, but only via
Step 3 (unscoped fallback). This is valuable data for the fix design doc:
implement Key_E_stripped anyway for robustness, even though it's not strictly
required for this model.

- [x] Update `main()` to call `spike_d` after spike_b (only if H2 confirmed)
- [x] Add `_print_summary(results: list[dict])` — prints a consolidated table:
      ```
      ┌────────────┬──────────────────────┬──────────────────────────────────────┐
      │ Hypothesis │ Verdict              │ Key Evidence                         │
      ├────────────┼──────────────────────┼──────────────────────────────────────┤
      │ H1         │ CONFIRMED            │ 37/37 nodes dual-match FCE+OE       │
      │ H2         │ CONFIRMED            │ 37 LT→ST, 0 SumTerm regression      │
      │ H3         │ CONFIRMED            │ 8/8 idiot_index resolve via Key_D   │
      │ H4         │ CONFIRMED_W/CAVEAT   │ 12/12 resolve, all via step 3 only  │
      └────────────┴──────────────────────┴──────────────────────────────────────┘
      ```

### Validation

**Automated:**
- [x] All 12 plant-level terms resolve (function returns non-None)
- [x] Each resolved channel is an aggregation output (double-attr pattern)
- [x] The 3-step trace shows which step actually succeeds

**Manual:**
- [x] Verify Step 1 (CHAIN redef) fails for all — redefs are EXPRESSION type → CONFIRMED
- [x] ~~Verify Step 2 (scoped key) fails~~ — DEVIATION: Step 2 SUCCEEDS for all 12!
      Key_E_stripped IS registered. See Phase 4 Completion notes.
- [x] Verify Step 3 (Key_D fallback) succeeds — Key_D IS in registry (both S2 and S3 HIT)

**Final validation:**
- [x] `uv run pytest tests/` → 647 passed, no regressions

**What We Know Works After This Phase:**
- Complete picture: all 4 hypotheses have empirical verdicts
- We know exactly which resolution step works and which don't
- Design doc recommendation: implement Key_E_stripped for robustness
- Summary table ready for pasting into fix design document

---

## Environment Setup

See CLAUDE.md for full environment rules. Key commands:
```bash
uv pip install -e ~/agentic-mbse && uv pip install -e ".[dev]"
uv run python scripts/spike_agg_wiring_h1_h4.py
uv run pytest tests/
```

---

## Risk Management

| Risk | Impact | Mitigation |
|------|--------|-----------|
| H1 falsified | Spikes B+D invalid | Phase 1 is the gate; stop and reassess |
| Model loading fails | All spikes blocked | Use same pattern as existing `spike_aggregation_validation.py` |
| Patched walker has side effects | False Spike B results | Use local function copy, not module-level monkey-patch |
| Registry key collision in H4 | Key_E_stripped needed | Spike D traces all 3 resolution steps; reports which succeeds |
| expression_ast is None on some redefs | Spike A/B incomplete | Filter to `EXPRESSION` type redefs only; log any missing ASTs |

**PipelineContext field availability (verified):**
All required attributes exist on the `PipelineContext` dataclass
(`initialization.py:75-121`):
- `hierarchy_data: HierarchyExtractionResult | None` (line 111)
- `output_registry: OutputRegistry | None` (line 120)
- `aggregation_expressions: list[ScopedAggregationData]` (line 114)
- `computation_graph: ComputationGraph` (line 101)

`_resolve_aggregation_input_channel` is exported in `graph_builder.py`'s
`__all__` (line 1260) and is importable directly.

---

## Implementation Notes

### Phase 1 Completion
**Completed:** 2026-02-16
**Actual Changes:**
- Created `scripts/spike_agg_wiring_h1_h4.py` with shared infrastructure
  (`_load_context`, `_print_verdict`) and `spike_a_ast_dual_match()`
- Implemented `_collect_non_sum_leaves()` walker with FCE-before-OE ordering
- `main()` runs Spike A, prints verdict, gates on H1

**Issues:**
- SysIDE `OperatorExpression.operator` attribute does not compare with Python
  `==` against string literals (e.g., `getattr(node, "operator", "") == "+"`
  fails even when the value prints as `+`). Resolved by using FCE-before-OE
  type check ordering instead of operator-value-based tree walking.

**Deviations:**
- Plan specified walking the `+` tree by checking `operator == "+"`. Changed
  to FCE-first type checking due to the operator comparison issue above.
  This approach is actually better — it directly demonstrates what the fix does
  (check FCE before OE) while confirming the subtype relationship.
- Added `neither_fce_nor_oe` count (9 genuinely local FRE nodes) not in
  original stencil. Provides useful context without changing verdict logic.

**Results:**
- H1 CONFIRMED: 37/37 dotted refs match BOTH OE and FCE (operator `.`)
- 9 genuinely local refs (FRE) match neither — `misc_hardware_cost`,
  `capital_cost`/`raw_material_cost` in idiot_index expressions
- 647/647 tests pass

### Phase 2 Completion
**Completed:** 2026-02-16
**Actual Changes:**
- Added `_walk_aggregation_ast_patched()` — local copy with FCE check before OE
- Added `spike_b_check_reorder()` — compares before/after term counts
- Updated `_print_verdict()` to handle reclassified_terms and remaining_local_terms
- Updated `main()` to call spike_b after spike_a

**Issues:** None — results matched predictions exactly.

**Deviations:** None.

**Results:**
- H2 CONFIRMED: before={sum:12, singleton:0, local:46} → after={sum:12, singleton:37, local:9}
- Zero SumTerm regression (12 == 12)
- 37 reclassified LocalTerms → SingletonTerms with correct dotted paths
- 9 remaining LocalTerms are genuinely local (misc_hardware_cost, idiot_index refs)

### Phase 3 Completion
**Completed:** 2026-02-16
**Actual Changes:**
- Added `spike_c_sibling_agg_resolution()` to `scripts/spike_agg_wiring_h1_h4.py`
- Extended `_print_verdict()` with handlers for `queries` and `negative_test_misc_hardware_cost`
- Updated `main()` to call spike_c after spike_b

**Issues:** None — results matched predictions exactly.

**Deviations:**
- Added `is_double_attr_channel` field to query results (not in original stencil)
  to verify resolved channels use the expected aggregation output format.
- Added deduplication (`seen_neg`) on negative tests to avoid duplicate
  `misc_hardware_cost` entries from multiple scoped aggregation instances.

**Results:**
- H3 CONFIRMED: 8/8 idiot_index LocalTerms resolve via Key_D
- Assemblies tested: solar_array, battery_system, site_infra, solar_battery_plant
- All resolved channels have double-attr format (`*__attr__attr`)
- misc_hardware_cost correctly unresolved (1 negative test, PASS)
- 647/647 tests pass

### Phase 4 Completion
**Completed:** 2026-02-16
**Actual Changes:**
- Added `spike_d_plant_level_resolution()` to `scripts/spike_agg_wiring_h1_h4.py`
- Added `_print_summary()` for consolidated verdict table
- Extended `_print_verdict()` with handler for `resolution_traces`
- Added imports for `_resolve_aggregation_input_channel` and `sanitize_name`
- Updated `main()` to call spike_d (gated on H2) and print summary

**Issues:** None — all 12 terms resolve successfully.

**Deviations:**
- **MAJOR: H4 verdict is CONFIRMED, not CONFIRMED_WITH_CAVEAT.** The plan
  predicted Step 2 (scoped key) would fail because Key_E_stripped wasn't
  registered. In fact, Step 2 SUCCEEDS for all 12 terms — the scoped key
  format (e.g., `solar_battery_plant.solar_array.capital_cost`) IS registered.
  This means the resolution is MORE robust than predicted: it resolves via
  the scoped path (Step 2) rather than falling back to unscoped Key_D (Step 3).
  Both S2 and S3 hit, so there are two resolution paths available.
- Key_E_stripped recommendation changes from "implement for robustness" to
  "already sufficient — current resolution logic handles all cases."

**Results:**
- H4 CONFIRMED: 12/12 plant-level SingletonTerms resolve
- Step 1 (CHAIN redef): 0 hits (all EXPRESSION type, as expected)
- Step 2 (scoped key): 12 hits (Key_E_stripped IS registered!)
- Step 3 (unscoped Key_D): 12 hits (also available as fallback)
- All resolved channels are aggregation outputs (double-attr format)
- 647/647 tests pass

---

**Status**: ~~Draft~~ → ~~In Progress~~ → **Complete**
