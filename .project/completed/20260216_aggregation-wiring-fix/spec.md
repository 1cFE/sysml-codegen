# Spec: Aggregation Wiring Fix

**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-02-15T23:45:37Z
**Complexity:** MEDIUM
**Branch:** cost-pattern

---

## Business Goals

### Why This Matters

Aggregation modules are the pipeline's roll-up mechanism: they sum child
component costs (with multiplicity) into assembly-level totals. When their
inputs are mis-wired as ENTRY_POINTs instead of MODULE_OUTPUTs, the generated
pipeline requires manual JSON input for values that should flow automatically
from upstream calculations. This defeats the purpose of automated codegen
and blocks E2E validation (Item 5 of the COST-PATTERN epic).

The OutputRegistry was designed as the single lookup for all channel
resolution. Aggregation module building currently bypasses it, using a
fragile parallel resolution path that fails on PartDef-to-PartUsage name
mismatches and unscoped keys.

### Success Criteria

- [ ] All resolvable aggregation inputs (SumTerms, SingletonTerms with dotted
      refs) wire to upstream MODULE_OUTPUTs, not ENTRY_POINTs
- [ ] The OutputRegistry is the primary resolution mechanism for aggregation
      inputs (CHAIN search becomes a redundant backup)
- [ ] No regressions in existing test suite (454 tests)
- [ ] solar_battery model: 12/12 resolvable inputs resolve to MODULE_OUTPUT

### Priority

Blocks COST-PATTERN Item 5 (E2E Validation & Documentation). Must complete
before the epic can close.

---

## Problem Statement

### Current State

The graph builder's `_resolve_aggregation_input_channel()` and SingletonTerm
processing have three interacting bugs that cause most aggregation inputs to
fall through to ENTRY_POINT status:

**Spike-validated data** (solar_battery model, 58 total inputs):
- 12 resolvable inputs (SumTerms with dotted refs)
- 46 LocalTerms (correctly become entry points — not bugs)
- Of the 12 resolvable: **8 succeed via CHAIN path**, **4 fail** (all
  `CHAIN_PART_MISMATCH`), **0 succeed via registry** (every registry
  lookup fails)

Source: `spike_report.md`, Spike B — Resolution Path Trace

### Desired Outcome

All 12 resolvable inputs resolve to MODULE_OUTPUT via the OutputRegistry.
The CHAIN search path continues to work as a backup but is no longer the
only functioning path. Plant-level → sub-assembly aggregation references
(currently hypothetical in this model but architecturally necessary) are
also supported.

---

## Scope

### In Scope

- Fix registry lookup scoping in `_resolve_aggregation_input_channel()`
- Add missing registration key (Key_E_stripped) in Phase 1b
- Fix SingletonTerm resolution order (registry-first)
- Extend Phase 1b alias variant registration to include scoped keys
- Unit tests for all new resolution paths
- Diagnostic logging for resolution path tracing

### Out of Scope

- Removing the CHAIN redef search path (future cleanup — research
  recommendation #3)
- Improving `sanitize_name()` for PartDef→PartUsage matching
- Updating `08_algorithm_revised.md` documentation
- Validating Bug 2 (SingletonTerm) with a model that has SingletonTerm→
  aggregation references (none exist in solar_battery)

### Edge Cases & Considerations

- **Key_D collisions**: Multiple assemblies share the same short key pattern
  (e.g., `solar_array.capital_cost` vs `battery_system.capital_cost`). The
  scoped key fix avoids collisions by using the full hierarchy path. The
  unscoped Key_D lookup MUST remain as a fallback after the scoped lookup.
  (Spike A confirmed Key_D collisions exist in the registry.)

- **Aggregation alias variants**: Phase 1b registers `agg.expression.aliases`
  (e.g., `"total_capex"` aliasing `"capital_cost"`). These alias variants
  MUST also receive scoped keys (Key_E_stripped format) for the same
  reason as the primary attribute.

- **Design prefix assumption**: The scoped key construction assumes
  `instance_path` segments[0] is the design PartDef prefix (e.g.,
  `"SolarBatteryDesign"`). This is validated by
  `_scope_aggregation_expressions()` which derives `design_prefix` from
  virtual CalcUsage QNs (initialization.py:470-478).

- **Cycle detection**: `_resolve_aggregation_input_channel` already has
  cycle detection via `_visited`. The scoped registry lookup MUST be
  added before the cycle guard check returns, not after.

- **SingletonTerm direct construction**: The existing direct channel
  construction (lines 932-937) correctly handles CalcUsage targets
  (e.g., `allocation_model.total_allocation`). It MUST be preserved
  as a fallback after registry-first resolution, not removed.

---

## Requirements

### Functional Requirements

> Requirements are derived from the root cause analysis
> (`.project/research/20260215-225131_aggregation-wiring-gap-analysis.md`)
> and validated by the spike report
> (`.project/active/aggregation-fix-validation/spike_report.md`).

#### FR-1: Scoped Registry Lookup (Bug 1 Fix)

`_resolve_aggregation_input_channel()` (graph_builder.py:815-820) MUST
construct a scoped registry key by:

1. Splitting `instance_path` on `"__"` to get segments
2. Stripping the design prefix (segments[0])
3. Joining remaining segments with `"."`
4. Appending `".{part_usage}.{attr}"` to form the scoped key

The function MUST try resolution in this order:
1. CHAIN redefinition search (existing, lines 790-813 — no change)
2. Scoped registry lookup (new — primary fix)
3. Unscoped Key_D lookup (existing, moved after scoped — fallback)

**Evidence**: Spike A confirmed 0/12 current (unscoped) hits, 12/12
proposed (scoped) hits. Spike C Case 2 confirmed the scoped key
`solar_battery_plant.solar_array.inverter.capital_cost` resolves where
CHAIN fails due to `String_Inverter` ≠ `inverter` mismatch.

#### FR-2: Key_E_stripped Registration (Bug 3 Fix)

Phase 1b aggregation output registration (initialization.py:550-573)
MUST register an additional key format:

- **Key_E_stripped**: `".".join(instance_parts[1:] + [attribute_name])`
  — the dotted hierarchy path without the design prefix

This key MUST be registered only when `len(instance_parts) > 1` (i.e.,
the instance path has more than just the design prefix segment).

Alias variants (from `agg.expression.aliases`) MUST also receive
Key_E_stripped format keys.

**Evidence**: Spike C Case 4 confirmed the hypothetical scoped key
`solar_battery_plant.solar_array.capital_cost` does NOT resolve in
the current registry. Key_D (`solar_battery_plant.capital_cost`)
incorrectly resolves to the plant's own output, not the sub-assembly.

#### FR-3: SingletonTerm Registry-First Resolution (Bug 2 Fix)

SingletonTerm processing (graph_builder.py:930-941) MUST try
`_resolve_aggregation_input_channel()` before direct channel
construction, not after. Resolution order:

1. Registry-first via `_resolve_aggregation_input_channel()` (new)
2. Direct channel construction (existing — CalcUsage fallback)
3. Entry point fallback (existing — last resort)

**Evidence**: Bug 2 was not directly testable (no SingletonTerms in the
solar_battery model), but the code path is clear: direct construction
builds `instance_path__prefix__output` which assumes CalcUsage EQN
format. Aggregation outputs use `instance_path__attr__attr` (attribute
appears twice), so direct construction produces wrong channels for
aggregation targets.

#### FR-4: Diagnostic Logging

`_resolve_aggregation_input_channel()` SHOULD log which resolution path
succeeded (CHAIN, scoped registry, unscoped Key_D) at DEBUG level. On
failure, it SHOULD log the attempted keys at WARNING level.

This is per research recommendation #2 and aids future debugging.

### Non-Functional Requirements

- **NFR-1**: No changes to `OutputRegistry.resolve()` contract (exact
  match only — empirically validated by Spikes 4-5).
- **NFR-2**: No changes to Phase 2 CHAIN alias registration logic
  (correctly scoped via `_build_chain_aliases()`).
- **NFR-3**: Registry collision policy (refuse overwrite) MUST be
  preserved. New Key_E_stripped keys may collide with existing
  registrations; collisions MUST be logged and the first registration
  kept.

---

## Acceptance Criteria

### Core Functionality

- [ ] **AC-1**: SumTerm with CHAIN redef available continues to resolve
      via CHAIN path (existing behavior preserved)
- [ ] **AC-2**: SumTerm where CHAIN fails (e.g., PartDef→PartUsage name
      mismatch) resolves via scoped registry lookup
- [ ] **AC-3**: SumTerm referencing an aggregation output (agg-to-agg)
      resolves via scoped registry lookup or Key_D fallback
- [ ] **AC-4**: SingletonTerm referencing a CalcUsage output resolves
      (via registry or direct construction)
- [ ] **AC-5**: SingletonTerm referencing an aggregation output resolves
      via registry (double-attr channel format)
- [ ] **AC-6**: Plant-level aggregation referencing sub-assembly
      aggregation resolves via Key_E_stripped
- [ ] **AC-7**: Key_D collisions do not cause mis-wiring (scoped key
      takes priority)

### Quality & Integration

- [ ] **AC-8**: All existing tests pass (`uv run pytest tests/` — 454+
      tests, 0 failures)
- [ ] **AC-9**: New unit tests cover AC-1 through AC-7
- [ ] **AC-10**: No changes to files outside `resolution/graph_builder.py`
       and `generation/initialization.py` (except test files)

---

## Related Artifacts

- **Research:** `.project/research/20260215-225131_aggregation-wiring-gap-analysis.md`
- **Spike Plan:** `.project/active/aggregation-fix-validation/plan.md`
- **Spike Report:** `.project/active/aggregation-fix-validation/spike_report.md`
- **Spike Script:** `scripts/spike_aggregation_validation.py`
- **Design:** `.project/active/aggregation-wiring-fix/design.md` (to be created)
- **Epic:** COST-PATTERN (`.project/backlog/epic_costed_component_pattern.md`)

---

## Traceability Matrix

| Requirement | Bug | Spike Evidence | Acceptance Criteria |
|-------------|-----|----------------|---------------------|
| FR-1 | Bug 1 (unscoped lookup) | Spike A: 0→12 hits; Spike C Case 2 | AC-2, AC-3, AC-7 |
| FR-2 | Bug 3 (missing key) | Spike C Case 4: key not found | AC-6 |
| FR-3 | Bug 2 (SingletonTerm order) | Not testable; code analysis | AC-4, AC-5 |
| FR-4 | — (diagnostic) | Research rec #2 | — |
| — | CHAIN_PART_MISMATCH (new) | Spike B: 4 failures | AC-2 (resolved by FR-1) |

---

**Next Steps:** After approval, proceed to `/_my_design`
