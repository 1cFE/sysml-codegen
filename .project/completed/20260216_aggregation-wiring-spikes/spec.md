# Spec: Aggregation Wiring Diagnostic Spikes

**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-02-16 16:19 UTC
**Complexity:** MEDIUM
**Branch:** cost-pattern

---

## Business Goals

### Why This Matters

COST-PATTERN Item 5 (E2E Validation) is blocked by 58 of 70 aggregation inputs
being misclassified as entry points instead of wiring to upstream module outputs.
Three research reports have converged on root cause hypotheses, but the prior
research cycle demonstrated the cost of acting on unverified assumptions (Error 2:
scoping the fix to the wrong layer, fixing 4 of 58 inputs).

These spikes empirically verify or falsify each hypothesis before committing to
implementation, preventing another misdirected fix cycle.

### Success Criteria

- [ ] Each of the 4 hypotheses has a clear CONFIRMED or FALSIFIED verdict backed by data
- [ ] If any hypothesis is falsified, the spike output points toward the actual root cause
- [ ] The spike results give sufficient confidence to write a fix design document
- [ ] Zero production code is modified by the spikes

### Priority

P0 — gates COST-PATTERN epic closure. The spikes are the fastest path to
understanding whether the proposed fixes will actually resolve all 58 inputs.

---

## Problem Statement

### Current State

Three research reports identified root causes for 58 unwired aggregation inputs:

| Root Cause | Layer | Count | Notes |
|-----------|-------|-------|-------|
| Bug A: FCE-as-OE check ordering | Extraction | 37 | Includes 12 plant-level terms |
|   of which: plant-level resolution (H4) | Resolution | 12 of 37 | Subset: needs Key_D or Key_E_stripped after Bug A fix |
| Bug B: LocalTerm → entry point | Graph builder | 8 | Independent of Bug A |
| (Multiplicity counts — correct) | N/A | 12 | Not a bug |
| (SumTerms — already working) | N/A | 12 | Not a bug |
| (misc_hardware_cost — correct) | N/A | 1 | True entry point |
| **Total** | | **70** | |

Note: Bug A's 37 count already includes the 12 plant-level terms (Report 2
lines 116-119: plant × 4 cost attrs = 12). RC-2 is a resolution-layer concern
within that same set — after Bug A reclassifies them as SingletonTerms, these
12 must additionally resolve via the registry. The counts are:
37 (Bug A) + 8 (Bug B) + 1 (misc_hardware_cost) = 46 misclassified/unwired,
plus 12 multiplicity + 12 SumTerms = 70 total.

The hypotheses are derived from AST dumps, code tracing, and SysML source
analysis — but have not been empirically verified against the live pipeline.

### Desired Outcome

4 targeted spike scripts that load the real solar_battery model, exercise the
exact code paths identified in the research, and produce structured verdicts
for each hypothesis.

---

## Scope

### In Scope

- Spike A: AST type dual-match verification (H1: FCE is subtype of OE)
- Spike B: Check reorder impact measurement (H2: ~37 LocalTerms → SingletonTerms)
- Spike C: Sibling aggregation resolution feasibility (H3: idiot_index resolvable)
- Spike D: Plant-level cascading resolution (H4: Key_D vs Key_E_stripped)
- All spikes use the real solar_battery model loaded via SysIDE adapter
- Structured output (JSON or formatted text) with pass/fail per hypothesis

### Out of Scope

- Actual bug fixes (deferred to post-spike design)
- RC-3 multiplicity count naming (deferred to Phase 5 pipeline execution)
- Runtime/TEAx pipeline execution testing
- Changes to any production source code
- Other models besides solar_battery (solar_battery contains all 5 aggregation patterns)

### Edge Cases & Considerations

- SysIDE adapter initialization requires the agentic-mbse dependency and model loading
- Monkey-patching in Spike B must not affect the module-level function (use local copies)
- Spike C/D depend on the OutputRegistry being built — may need to run the
  pipeline through Step 5 to get a populated registry
- If H1 is falsified (FCE does NOT match OE), all downstream spikes need redesign

---

## Requirements

### Functional Requirements

> Requirements below are from user's request unless marked [INFERRED].

1. **FR-1**: Spike A MUST load the real SysIDE AST for all solar_battery
   aggregation expressions and check `is_instance("OperatorExpression")` AND
   `is_instance("FeatureChainExpression")` on each non-sum top-level term node.

2. **FR-2**: Spike A MUST report which nodes match both types, which match only
   one, and dump `operator`, `target_feature.name`, and `operands[0]` type for
   any dual-match nodes.

3. **FR-3**: Spike B MUST run `_walk_aggregation_ast()` in both orderings
   (current OE-first and patched FCE-first) on ALL solar_battery aggregation
   expressions and produce before/after term counts.

4. **FR-4**: Spike B MUST verify zero regression in the 12 already-working
   SumTerms (same count, same term contents).

5. **FR-5**: Spike B MUST report the exact list of terms that changed
   classification (from LocalTerm to SingletonTerm) with their source paths.

6. **FR-6**: Spike C MUST run the pipeline through Step 5 (OutputRegistry
   construction) for solar_battery, then query the registry at the point where
   idiot_index LocalTerms would be processed.

7. **FR-7**: Spike C MUST test resolution using Key_D format
   (`"{part_usage}.{attr_name}"`) and the double-attr canonical format
   (`"{instance_path}__{attr_name}__{attr_name}"`).

8. **FR-8**: Spike D MUST call `_resolve_aggregation_input_channel()` directly
   with the actual `instance_path`, `redefinitions`, and `output_registry` from
   the pipeline context, for each plant-level SingletonTerm that Spike B shows
   will be reclassified (`solar_array.capital_cost`, `battery_system.capital_cost`,
   `site_infra.capital_cost`).

9. **FR-9**: Spike D MUST report which of the 3 resolution steps succeeded for
   each term: (1) CHAIN redef search, (2) scoped key lookup, (3) unscoped Key_D
   fallback. This determines whether Key_E_stripped is needed for robustness.

10. **FR-10**: [INFERRED] Each spike MUST be a standalone Python script in
    `scripts/` that can be run independently via `uv run python scripts/spike_X.py`.

11. **FR-11**: [INFERRED] Each spike SHOULD produce structured output (JSON or
    clearly formatted text) with explicit CONFIRMED/FALSIFIED verdicts.

12. **FR-12**: [INFERRED] Spikes MAY share a common runner script that executes
    all four in sequence.

### Non-Functional Requirements

- No production code modifications — spikes use monkey-patching, inspection, or
  local function copies only
- Spikes SHOULD complete in under 60 seconds each (model loading is the bottleneck)
- Spikes SHOULD reuse the single model load across all four if combined

---

## Acceptance Criteria

### Core Functionality

- [ ] Spike A produces a table of AST nodes with dual-match results (H1 verdict)
- [ ] Spike B produces before/after term counts with exact term change list (H2 verdict)
- [ ] Spike B confirms 12 SumTerms unchanged (zero regression)
- [ ] Spike C shows registry query results for idiot_index LocalTerms (H3 verdict)
- [ ] Spike D shows resolution results for plant-level SingletonTerms (H4 verdict)

### Quality & Integration

- [ ] All spikes run successfully against the solar_battery model
- [ ] No production source files are modified
- [ ] Existing tests continue to pass (`uv run pytest tests/`)
- [ ] Spike output is clear enough to inform a fix design document

---

## Hypotheses Under Test

### H1: FCE is a subtype of OE in SysIDE's type system

**Tested by:** Spike A
**Evidence for:** Research report 2 found `is_instance("OperatorExpression") = True`
on FeatureChainExpression nodes via AST dump
**Falsified if:** Standalone dotted ref nodes do NOT match `is_instance("OperatorExpression")`

### H2: Check reorder produces exactly ~37 term reclassifications

**Tested by:** Spike B
**Evidence for:** Research report 2 counted 37 affected inputs across 16 aggregation
expressions by matching `.(name)` patterns in raw expression text
**Falsified if:** Different count, or SumTerms regress, or unexpected side effects

### H3: Sibling aggregation outputs are in the registry when LocalTerms are processed

**Tested by:** Spike C
**Evidence for:** Algorithm doc Section 12 shows Key_D registration
(`"{part_usage}.{attr_name}"`) happens in Phase 1, before graph building
**Falsified if:** Registry doesn't contain sibling agg outputs at that point
(ordering issue in `_build_aggregation_module`)

### H4: Plant-level SingletonTerms resolve through the actual resolution code path

**Tested by:** Spike D
**Evidence for:** `_resolve_aggregation_input_channel()` tries 3 steps in order:
(1) CHAIN redef search, (2) scoped key lookup, (3) unscoped Key_D fallback.
Key_D = `"{part_usage}.{attr_name}"` IS registered in Phase 1b.
**Falsified if either:**
- Key_D collides between sub-assembly agg output and leaf-part cost_model output
  (ambiguous resolution)
- Key_D works only as unscoped fallback (scoped path fails because Key_E_stripped
  isn't registered), meaning robustness depends on implementing Key_E_stripped

**Expected nuanced outcome:** CONFIRMED with caveat — Step 1 (CHAIN redef) fails
because the redefs are EXPRESSION type, not CHAIN. Step 2 (scoped key) fails
because Key_E_stripped isn't registered. Step 3 (Key_D fallback) succeeds. This
means Key_E_stripped should be implemented for robustness even though the unscoped
fallback handles the immediate test case.

---

## Related Artifacts

- **Research (full scope):** `.project/research/20260216-001500_aggregation-wiring-full-scope-analysis.md`
- **Research (misclassification):** `.project/research/20260216-aggregation-expression-misclassification.md`
- **Algorithm doc:** `.project/reports/08_algorithm_revised.md`
- **Existing spike:** `scripts/spike_aggregation_validation.py`
- **Epic:** `.project/backlog/epic_costed_component_pattern.md`
- **Design (next):** `.project/active/aggregation-wiring-spikes/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_plan` for spike implementation planning.
