# Spec: Aggregation Wiring Fix — Validation Spikes

**Status:** Draft
**Created:** 2026-02-15
**Complexity:** LOW
**Prerequisite:** `.project/research/20260215-225131_aggregation-wiring-gap-analysis.md`

---

## Business Goals

Before committing code changes to fix the aggregation wiring gap, validate
the root cause analysis with runtime data. The proposed fix changes registry
lookup paths and adds registration keys — if the analysis is wrong, the fix
could break existing working pipelines or mask the real problem.

### Success Criteria

- [ ] Each of the 3 identified bugs confirmed or refuted with runtime data
- [ ] Any failure modes the static analysis missed are surfaced
- [ ] Clear go/no-go for implementing the proposed 3-part fix

### Priority

Blocking: must complete before implementing the fix.

---

## Problem Statement

### Current State

The root cause analysis identified 3 bugs explaining why 62 of 70 aggregation
module inputs fail to resolve as MODULE_OUTPUT:

| Bug | Description | Confidence | Key Unknown |
|-----|-------------|------------|-------------|
| 1 | Registry lookup uses unscoped `"part.attr"` instead of scoped `"path.to.part.attr"` | High (code is clear) | Do the proposed scoped keys actually exist in the registry? |
| 2 | SingletonTerm builds wrong channel (misses double-attr in aggregation naming) | High (code is clear) | Are there SingletonTerm→aggregation cases in this model? |
| 3 | Missing scoped registration key for plant-level → sub-assembly | Medium | Does existing Key_D already suffice, or is a new key needed? |

The analysis was done by reading code, not by observing runtime behavior.

### Desired Outcome

Runtime data confirming or refuting the analysis before writing production
code changes. Each spike answers a specific question with data.

---

## Scope

### In Scope

- 3 investigative spikes (read-only scripts, no production code changes)
- Each produces a data artifact (structured report)
- All 3 can be implemented as a single Python script

### Not In Scope

- Implementing the actual fix (follows after validation)
- Modifying any files under `src/`
- Fixing issues found (document only)

---

## Requirements

### Spike A: Registry Key Inventory

**Goal:** Dump the full registry after construction and, for each aggregation
input, show what key the code currently tries vs what the fix would try.

| ID | Requirement |
|----|-------------|
| FR-A1 | Run `build_pipeline_context()` with `solar_battery` model to get a real `output_registry` and `aggregation_data` |
| FR-A2 | Dump all `output_registry._index` entries (key → canonical channel) |
| FR-A3 | For each aggregation input (~70), log: input type (`SumTerm`/`SingletonTerm`/`LocalTerm`), symbolic ref, `instance_path`, current lookup key (as code builds it now), proposed scoped key (using `instance_path`), hit/miss for each |
| FR-A4 | Produce summary: total inputs, current hits, proposed hits, still missing after fix |

**Validates:** Bug 1 (unscoped vs scoped keys) and Bug 3 (missing registration key).

**Answers:** "Do the proposed scoped keys actually match existing registry entries?"

---

### Spike B: Resolution Path Trace

**Goal:** For each of the ~70 aggregation inputs, trace which resolution path
fires (CHAIN search vs registry lookup) and why it succeeds or fails.

| ID | Requirement |
|----|-------------|
| FR-B1 | For each input, log: (a) input type + symbolic ref, (b) CHAIN search result, (c) if CHAIN missed — reason: no matching `attribute_name`, part name mismatch via `sanitize_name().lower()`, or chain target channel doesn't exist in `canonical_channels`, (d) registry lookup key + result, (e) final outcome (MODULE_OUTPUT or ENTRY_POINT) |
| FR-B2 | Produce breakdown: N succeeded via CHAIN, N succeeded via registry, N failed at CHAIN (with reason sub-counts), N failed at registry |

**Validates:** Confirms 8 successes are all CHAIN-path. Identifies whether
failures are CHAIN bugs vs registry bugs. Reveals any failure modes the
analysis didn't predict.

**Answers:** "Is the 8-vs-62 split exactly what we predicted, or are there surprises?"

---

### Spike C: Scoped Key Spot-Check

**Goal:** For 4 representative failing inputs, manually construct the proposed
scoped key and verify it resolves correctly against the actual registry.

| ID | Requirement |
|----|-------------|
| FR-C1 | Select 4 cases: (1) SumTerm from mid-level aggregation (e.g., `solar_array`), (2) SumTerm from a different mid-level aggregation (different parent), (3) SingletonTerm referencing a sub-assembly aggregation output (if any exist), (4) input from top-level aggregation (`solar_battery_plant`) |
| FR-C2 | For each case: show `instance_path`, symbolic ref, proposed scoped key (`".".join(instance_path.split("__")[1:]) + "." + part + "." + attr`), whether key exists in registry, if hit: the canonical channel (and verify it's the correct one), if miss: 5 closest keys by prefix match |
| FR-C3 | For the top-level case (#4), also test: what scoped key would it need? Does it exist? If not, construct the Bug 3 registration key (`".".join(instance_parts[1:] + [attr])`) and verify it would map to the correct canonical channel |

**Validates:** Proposed key construction works end-to-end. Tests Bug 3 fix
for the top-level case. Catches edge cases in key format.

**Answers:** "If we build scoped keys as proposed, do they actually resolve to
the right channels?"

---

## Acceptance Criteria

### Per Spike

- [ ] **Spike A:** Registry dump produced. All ~70 inputs compared. Summary
  table with current vs proposed hit counts.
- [ ] **Spike B:** All ~70 inputs traced. Breakdown by path and failure
  reason. 8 successes accounted for.
- [ ] **Spike C:** 4 representative cases spot-checked. Scoped key verified
  against actual registry. Top-level case tested with Bug 3 key.

### Overall

- [ ] All data artifacts written to `.project/active/aggregation-fix-validation/`
- [ ] No files under `src/` modified
- [ ] Go/no-go decision documented: "analysis confirmed, proceed to fix"
  or "analysis has gaps, revise before fixing"

---

## Implementation Notes

### Single Script Approach

All 3 spikes SHOULD be implemented as one Python script:

1. Call `build_pipeline_context()` with the `solar_battery` model path
2. Extract `output_registry`, `aggregation_data`, `hierarchy_data.redefinitions`
3. Access `output_registry._index` directly (internal field, acceptable for spike)
4. Iterate over `aggregation_data`, simulate the resolution logic for each input
5. Write structured output to `.project/active/aggregation-fix-validation/spike_report.md`

### Finding the Model Path

Look for `solar_battery` model in:
- `tests/` directories (check existing test fixtures)
- The fusion-tea repo: `~/1cfe/fusion-tea/models/tests/solar_battery/`
- Same path used in Phase 4 of the E2E validation

### Key Functions to Import/Simulate

- `build_pipeline_context()` from `sysml_codegen.generation.initialization`
- `sanitize_name()` from `sysml_codegen.core.qualified_names` (for CHAIN part name matching)
- `get_channel_name()` from `sysml_codegen.core.qualified_names` (for channel construction)
- The `_resolve_aggregation_input_channel` logic should be **replicated** in the
  spike script with added tracing, not called directly

### Constraint

MUST NOT modify any files under `src/`. All instrumentation stays in the spike script.

---

## Related Artifacts

- **Root cause analysis:** `.project/research/20260215-225131_aggregation-wiring-gap-analysis.md`
- **Phase 4 findings:** `~/1cfe/fusion-tea/.project/active/e2e-post-codegen-validation/plan.md` (Phase 4 Completion section)
- **Code under investigation:**
  - `src/sysml_codegen/resolution/graph_builder.py` — `_resolve_aggregation_input_channel` (L740-821), `_build_aggregation_module` (L824-1025)
  - `src/sysml_codegen/generation/initialization.py` — `build_output_registry` (L502-665)
  - `src/sysml_codegen/core/output_registry.py` — `OutputRegistry`

---

**Next Steps:** Implement spike script → run against solar_battery → analyze results → go/no-go on fix
