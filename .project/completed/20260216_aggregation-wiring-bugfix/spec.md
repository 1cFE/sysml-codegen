# Spec: Aggregation Wiring Bugfix (Bug A + Bug B)

**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-02-16 17:15 UTC
**Complexity:** MEDIUM
**Branch:** cost-pattern

---

## Business Goals

### Why This Matters

COST-PATTERN Item 5 (E2E Validation) is blocked. 58 of 70 aggregation inputs
in the solar_battery model are incorrectly classified as entry points instead
of wiring to upstream module outputs. The generated pipeline cannot execute
end-to-end for the costed component pattern until these wiring bugs are fixed.

Four diagnostic spikes (H1-H4) have empirically confirmed the root causes and
validated the fix approaches. A subsequent codebase audit found the same
FCE/OE check-ordering bug in two additional files. This spec covers all three
FCE/OE sites plus the LocalTerm resolution bug.

### Success Criteria

- [ ] 57 of 70 aggregation inputs wire to MODULE_OUTPUT (up from 12)
- [ ] 13 inputs remain as correct ENTRY_POINTs (12 multiplicity counts + 1 misc_hardware_cost)
- [ ] Zero regression in existing SumTerm wiring (12 inputs already working)
- [ ] All existing tests pass

### Priority

P0 — gates COST-PATTERN epic closure.

---

## Problem Statement

### Current State

Two classes of bug cause 45 aggregation inputs to be misclassified as entry
points. A codebase audit found the same root cause (FCE/OE ordering) in two
additional files beyond the original site.

**Bug A — FCE/OE check ordering (3 sites, 37 aggregation inputs):**
In SysIDE's type system, `FeatureChainExpression` is a subtype of
`OperatorExpression` — both `is_instance()` calls return True on the same
node. Any code that checks OE before FCE will route FCE nodes into the wrong
handler.

| # | File | Function | Lines | Impact |
|---|------|----------|-------|--------|
| A1 | `hierarchy_resolver.py` | `_walk_aggregation_ast()` | 328, 351 | **HIGH** — 37 aggregation inputs misclassified as LocalTerm |
| A2 | `expression_compiler.py` | `build_expression_ast()` | 313, 395 | **LOW** — both paths produce `ExpressionAST.unsupported()`, but with wrong diagnostic text (`"unsupported operator: ."` instead of `"feature chain expression not supported"`) |
| A3 | `expression_utils.py` | `reconstruct_expression()` | 44, 50 | **MEDIUM** — FCE nodes get mangled reconstruction (`".(array_bos)"` instead of `"array_bos.capital_cost"`). Affects expression text display in CalcDef extraction, constraint extraction, computed attribute extraction, and `RedefinitionData.expression_text` |

Site A1 causes the 37-input aggregation wiring failure. Sites A2 and A3 are
latent bugs — same root cause, same fix pattern, but with different
downstream effects. All three should be fixed together.

**Bug B — LocalTerm unconditional entry point (8 inputs):**
`_build_aggregation_module()` in `graph_builder.py` (lines 1015-1036)
unconditionally creates entry points for all LocalTerms without checking
whether a sibling aggregation module output exists. For
`idiot_index = capital_cost / raw_material_cost`, both `capital_cost` and
`raw_material_cost` are bare `FeatureReferenceExpression` nodes — correctly
classified as LocalTerms by the extraction. But they are outputs of sibling
aggregation modules at the same scope, not user-provided parameters.

### Desired Outcome

After fixing both bugs:

| Category | Count | Wiring |
|----------|-------|--------|
| SumTerms (already working) | 12 | MODULE_OUTPUT |
| Reclassified SingletonTerms (Bug A fix) | 37 | MODULE_OUTPUT |
| Sibling agg refs / idiot_index (Bug B fix) | 8 | MODULE_OUTPUT |
| Multiplicity counts (correct) | 12 | ENTRY_POINT |
| misc_hardware_cost (correct) | 1 | ENTRY_POINT |
| **Total** | **70** | **57 wired, 13 entry points** |

---

## Scope

### In Scope

- Bug A fix (3 sites): Reorder `FeatureChainExpression` check before
  `OperatorExpression` check in:
  - A1: `_walk_aggregation_ast()` in `hierarchy_resolver.py`
  - A2: `build_expression_ast()` in `expression_compiler.py`
  - A3: `reconstruct_expression()` in `expression_utils.py`
- Bug B fix: Add sibling aggregation output resolution for LocalTerms in
  `_build_aggregation_module()` before falling back to entry point creation
- Unit tests for all fixes
- Integration-level validation of wiring counts

### Out of Scope

- Architecture doc updates (08_algorithm_revised.md Section 9/12, ADR-007,
  ADR-008) — tracked as follow-up after implementation
- New OutputRegistry key formats (Key_E_stripped) — Spike D confirmed existing
  scoped keys and Key_D already resolve all cases
- Changes to `_resolve_aggregation_input_channel()` — it already works
  correctly once it receives SingletonTerms (confirmed by Spikes C and D)
- Changes to OutputRegistry or its key registration logic
- Other models beyond solar_battery
- Runtime/TEAx pipeline execution testing

### Edge Cases & Considerations

- Bug A fix MUST NOT regress the 12 working SumTerms. The `sum()` handler
  (InvocationExpression at line 364) is NOT affected by the reorder because
  `InvocationExpression` does not match `is_instance("OperatorExpression")`.
  Spike B empirically verified zero regression.
- Bug B's resolution attempt MUST NOT resolve `misc_hardware_cost` — it has no
  sibling aggregation module. Spike C confirmed this negative case.
- Bug A and Bug B are independent — Bug B's 8 idiot_index LocalTerms are
  bare `FeatureReferenceExpression` nodes correctly classified by current code.
- Plant-level SingletonTerms (12 of Bug A's 37) require the existing
  `_resolve_aggregation_input_channel()` scoped key + Key_D resolution, which
  Spike D confirmed already works.

---

## Requirements

### Functional Requirements

> Requirements are derived from spike results
> (`.project/active/aggregation-wiring-spikes/plan.md`) and research
> (`.project/research/20260216-aggregation-expression-misclassification.md`).

1. **FR-1**: The `FeatureChainExpression` type check MUST execute before the
   `OperatorExpression` type check in ALL three Bug A sites:
   - A1: `_walk_aggregation_ast()` in `hierarchy_resolver.py` (lines 328, 351)
   - A2: `build_expression_ast()` in `expression_compiler.py` (lines 313, 395)
   - A3: `reconstruct_expression()` in `expression_utils.py` (lines 44, 50)

2. **FR-2**: After Bug A1 fix, 37 terms MUST reclassify from LocalTerm to
   SingletonTerm. The before/after counts MUST match Spike B results:
   before `{sum: 12, singleton: 0, local: 46}` →
   after `{sum: 12, singleton: 37, local: 9}`.

3. **FR-2a**: After Bug A2 fix, `build_expression_ast()` MUST produce
   `ExpressionAST.unsupported()` with the diagnostic text
   `"feature chain expression not supported in CalcDef output"`, not
   `"unsupported operator: ."`.

4. **FR-2b**: After Bug A3 fix, `reconstruct_expression()` MUST produce
   `"array_bos.capital_cost"` for a FeatureChainExpression node, not
   `".(array_bos)"`.

5. **FR-3**: The LocalTerm processing loop in `_build_aggregation_module()`
   MUST attempt to resolve each LocalTerm to a sibling aggregation module
   output before creating an entry point. Resolution SHOULD use the
   double-attr canonical channel format
   (`{instance_path}__{attr}__{attr}`) checked against `canonical_channels`,
   with Key_D registry fallback (`{part_usage}.{attr}`).

6. **FR-4**: LocalTerms that do not resolve MUST still become entry points,
   preserving current behavior for genuine local attributes like
   `misc_hardware_cost`.

### Non-Functional Requirements

- Existing test suite (647 tests) MUST continue to pass
- No changes to OutputRegistry, its key registration, or
  `_resolve_aggregation_input_channel()`

---

## Acceptance Criteria

### Core Functionality

- [ ] A1: `_walk_aggregation_ast()` classifies `array_bos.capital_cost` as
      `SingletonTerm("array_bos.capital_cost")`, not `LocalTerm("array_bos")`
- [ ] A1: SumTerm count unchanged at 12 across all aggregation expressions
- [ ] A1: SingletonTerm count increases from 0 to 37
- [ ] A1: LocalTerm count decreases from 46 to 9
- [ ] A2: `build_expression_ast()` produces correct diagnostic for FCE nodes
- [ ] A3: `reconstruct_expression()` produces `"child.attr"` for FCE nodes
- [ ] B: 8 idiot_index LocalTerms (`capital_cost`, `raw_material_cost` on
      4 assemblies) wire to sibling aggregation MODULE_OUTPUTs
- [ ] B: `misc_hardware_cost` remains an ENTRY_POINT
- [ ] Total wired aggregation inputs: 57 of 70

### Quality & Integration

- [ ] Existing tests pass (`uv run pytest tests/`)
- [ ] New unit tests for Bug A1: FCE-before-OE ordering with dual-match nodes
- [ ] New unit tests for Bug A2: FCE handling in expression compiler
- [ ] New unit tests for Bug A3: FCE reconstruction in expression_utils
- [ ] New unit tests for Bug B: LocalTerm resolution against sibling agg outputs
- [ ] Integration test validating aggregation wiring counts

---

## Spike Evidence Summary

All four hypotheses CONFIRMED by `scripts/spike_agg_wiring_h1_h4.py`:

| Spike | Hypothesis | Verdict | Key Evidence |
|-------|-----------|---------|-------------|
| A (H1) | FCE is subtype of OE | CONFIRMED | 37/37 nodes dual-match FCE+OE |
| B (H2) | Check reorder reclassifies ~37 | CONFIRMED | Exactly 37 LT→ST, 0 SumTerm regression |
| C (H3) | Sibling agg outputs in registry | CONFIRMED | 8/8 idiot_index resolve via Key_D |
| D (H4) | Plant-level resolution works | CONFIRMED | 12/12 resolve via scoped key + Key_D |

---

## Related Artifacts

- **Spike results:** `.project/active/aggregation-wiring-spikes/plan.md`
- **Spike spec:** `.project/active/aggregation-wiring-spikes/spec.md`
- **Spike script:** `scripts/spike_agg_wiring_h1_h4.py`
- **Research (full scope):** `.project/research/20260216-001500_aggregation-wiring-full-scope-analysis.md`
- **Research (misclassification):** `.project/research/20260216-aggregation-expression-misclassification.md`
- **Research (arch review):** `.project/research/20260215-235500_aggregation-wiring-design-vs-architecture-review.md`
- **Epic:** `.project/backlog/epic_costed_component_pattern.md`

---

## Follow-Up Items (Post-Implementation)

1. Update `08_algorithm_revised.md` Section 9 (Step 7) and Section 12 scope
   clarification to reflect OutputRegistry usage for aggregation inputs
2. Update ADR-008 Decision 2 key table and Decision 5 scope
3. Update ADR-007 Decision 2 with resolution mechanism detail

---

**Next Steps:** After approval, proceed to `/_my_design` for implementation design.
