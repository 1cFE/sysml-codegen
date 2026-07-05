# Implementation Plan: Aggregation Wiring Fix — Validation Spikes

**Status:** Draft
**Created:** 2026-02-15
**Last Updated:** 2026-02-15

## Source Documents
- **Spec:** `.project/active/aggregation-fix-validation/spec.md`
- **Root cause analysis:** `.project/research/20260215-225131_aggregation-wiring-gap-analysis.md`
- **No design.md** — spec is self-contained (read-only spike script, no production changes)

## Implementation Strategy

**Phasing Rationale:**
A single Python script built incrementally across 3 phases. Each phase adds
one spike's logic and produces verifiable output. Phase ordering follows data
dependencies: Spike A establishes the registry inventory that Spikes B and C
reference. The script loads the model once and shares context across all spikes.

**Overall Validation Approach:**
- No unit tests (this IS the validation — it produces data, not production code)
- Each phase validated by running the script and inspecting structured output
- No files under `src/` are modified at any point
- Final artifact: `spike_report.md` with go/no-go recommendation

---

## Phase 1: Script Scaffolding + Spike A (Registry Key Inventory)

### Goal
Stand up the spike script, load the solar_battery model via
`build_pipeline_context()`, and implement Spike A — dump the full registry
and compare current vs proposed lookup keys for all ~70 aggregation inputs.
This validates Bug 1 (unscoped keys) and Bug 3 (missing registration key).

### Test Stencil (Write This First)
```python
# Quick smoke test — run the script and verify it produces output
# No pytest needed; the script IS the test. Validate by:
#
# 1. Run: uv run python scripts/spike_aggregation_validation.py
# 2. Check stdout for "=== Spike A: Registry Key Inventory ==="
# 3. Verify summary line: "Total inputs: N, Current hits: N, Proposed hits: N"
# 4. Check that N inputs > 0 (model loaded successfully)
```

### Changes Required

#### 1. Create spike script
**File:** `scripts/spike_aggregation_validation.py` (NEW)

- [ ] Import `build_pipeline_context` from `sysml_codegen.generation.initialization`
- [ ] Import `sanitize_name`, `get_channel_name` from `sysml_codegen.core.qualified_names`
- [ ] Import data model types: `SumTerm`, `SingletonTerm`, `LocalTerm`
- [ ] Load model: `build_pipeline_context([Path("tests/fixtures/solar_battery_model")])`
- [ ] Extract from context:
  - `output_registry` → access `._index` (dict[str, str]) and `._canonical` (set)
  - `aggregation_expressions` → list of `ScopedAggregationData`
  - `hierarchy_data.redefinitions` → list of `RedefinitionData`
- [ ] **Spike A logic** (FR-A1 through FR-A4):
  - Dump all `output_registry._index` entries (key → canonical channel)
  - For each aggregation expression, iterate its `expression.sum_terms`,
    `expression.singleton_terms`, and `expression.local_terms`
  - For each SumTerm: log input type, symbolic ref (`{part_usage_name}.{attribute_name}`),
    `instance_path`, current key (`{part_usage}.{attr}`), proposed scoped key
    (`".".join(instance_path.split("__")[1:]) + "." + part_usage + "." + attr`),
    hit/miss for each
  - For each SingletonTerm: log `source_path`, current direct-construction channel,
    proposed scoped key, hit/miss
  - Produce summary: total inputs, current hits, proposed hits, still missing

### Validation (How to Verify This Phase)

**Automated:**
- [ ] `uv run python scripts/spike_aggregation_validation.py` → runs without error
- [ ] Output contains registry dump section
- [ ] Output contains per-input comparison table
- [ ] Summary line shows counts

**Manual:**
- [ ] Verify total inputs ≈ 70
- [ ] Verify current hits ≈ 8 (matches known 8-success count)
- [ ] Verify proposed hits > current hits (scoped keys find more matches)
- [ ] Spot-check a few registry entries make sense

**What We Know Works After This Phase:**
- Model loads successfully via `build_pipeline_context`
- Registry structure is accessible and populated
- Scoped key construction matches (or doesn't match) registry entries
- Bug 1 and Bug 3 confirmed or refuted with data

---

## Phase 2: Spike B (Resolution Path Trace)

### Goal
Add resolution path tracing to the script. For each aggregation input,
replicate the `_resolve_aggregation_input_channel` logic with added tracing
to show which path fires (CHAIN search vs registry lookup) and why it
succeeds or fails. Produces the breakdown counts.

### Test Stencil (Write This First)
```python
# Validate by running script and checking Spike B section:
#
# 1. Run: uv run python scripts/spike_aggregation_validation.py
# 2. Check stdout for "=== Spike B: Resolution Path Trace ==="
# 3. Verify per-input trace shows: input type, symbolic ref, CHAIN result,
#    registry result, final outcome
# 4. Verify summary: N via CHAIN + N via registry + N failed = total
# 5. Verify CHAIN successes ≈ 8
```

### Changes Required

**See research doc for:**
- Resolution algorithm → `research/20260215-225131_aggregation-wiring-gap-analysis.md#5-why-8-inputs-succeed`
- Bug interaction flow → same doc, Section 6

**Specific changes to `scripts/spike_aggregation_validation.py`:**

- [ ] Add `trace_resolution()` function that replicates `_resolve_aggregation_input_channel`
      (graph_builder.py:740-821) with added tracing:
  - Step 1: CHAIN redef search — log whether attribute_name matched, whether
    part_name matched via `sanitize_name().lower()`, whether chain target channel
    exists in `canonical_channels`
  - Step 2: Registry lookup — log the key tried, hit/miss
  - Return a `TraceResult` with: path taken, success/failure, reason
- [ ] Add `trace_singleton_resolution()` for SingletonTerm direct construction path
      (graph_builder.py:924-976)
- [ ] For each aggregation input, call the appropriate trace function
- [ ] Produce breakdown: N succeeded via CHAIN, N succeeded via registry,
      N failed at CHAIN (with reason sub-counts), N failed at registry
- [ ] Log CHAIN failure reasons: no matching `attribute_name`, part name mismatch,
      chain target channel doesn't exist

### Validation (How to Verify This Phase)

**Automated:**
- [ ] Script runs without error
- [ ] Spike B section appears in output
- [ ] All ~70 inputs traced

**Manual:**
- [ ] CHAIN successes ≈ 8 (confirms prediction)
- [ ] Failure reason sub-counts add up to total failures
- [ ] No unexpected failure modes (or if present, documented)
- [ ] Cross-check: Spike A misses align with Spike B registry-path failures

**What We Know Works After This Phase:**
- The 8-vs-62 split is confirmed or surprising patterns revealed
- CHAIN failure reasons are categorized (missing redef vs name mismatch vs channel missing)
- Any failure modes the static analysis missed are surfaced

---

## Phase 3: Spike C (Scoped Key Spot-Check) + Report Generation

### Goal
Select 4 representative failing inputs from Spike B data, manually construct
proposed scoped keys, verify against actual registry, and generate the final
structured report to `.project/active/aggregation-fix-validation/spike_report.md`.

### Test Stencil (Write This First)
```python
# Validate by running script and checking:
#
# 1. Spike C section: 4 cases with instance_path, symbolic ref, proposed key,
#    hit/miss, closest keys on miss
# 2. Top-level case (#4): Bug 3 key constructed and tested
# 3. spike_report.md written to .project/active/aggregation-fix-validation/
# 4. Report contains go/no-go recommendation
```

### Changes Required

**See spec for case selection criteria:**
- spec.md FR-C1: 4 specific case types required
- spec.md FR-C2: per-case data fields
- spec.md FR-C3: top-level Bug 3 key test

**Specific changes to `scripts/spike_aggregation_validation.py`:**

- [ ] Add case selection logic — from Spike B failure data, select:
  1. SumTerm from mid-level aggregation (e.g., `solar_array`)
  2. SumTerm from a different mid-level aggregation (different parent)
  3. SingletonTerm referencing a sub-assembly aggregation output (if any exist)
  4. Input from top-level aggregation (`solar_battery_plant`)
- [ ] For each case (FR-C2):
  - Show `instance_path`, symbolic ref, proposed scoped key
  - Check if key exists in registry
  - If hit: show canonical channel, verify it's correct
  - If miss: show 5 closest keys by prefix match (simple prefix comparison on `_index` keys)
- [ ] For top-level case (#4, FR-C3):
  - Construct Bug 3 registration key: `".".join(instance_parts[1:] + [attr])`
  - Check if it would map to correct canonical channel
  - Document what registration is missing
- [ ] Generate `spike_report.md` with all data from Spikes A, B, C
  - Summary tables
  - Per-input details
  - Go/no-go recommendation based on findings

### Validation (How to Verify This Phase)

**Automated:**
- [ ] Script runs without error
- [ ] `spike_report.md` written to `.project/active/aggregation-fix-validation/`
- [ ] No files under `src/` modified: `git diff --name-only src/` shows nothing

**Manual:**
- [ ] 4 spot-check cases cover the required types from FR-C1
- [ ] Scoped keys match or near-miss patterns are clear
- [ ] Top-level Bug 3 key test shows what registration is needed
- [ ] Go/no-go recommendation is supported by data
- [ ] Report is readable and actionable

**What We Know Works After This Phase:**
- All 3 bugs confirmed or refuted with runtime data
- Proposed scoped key construction verified end-to-end
- Go/no-go decision documented with evidence
- Ready to proceed to implementing the fix (or revise analysis)

---

## Environment Setup

**Per CLAUDE.md:**
```bash
# Install dependencies (if not already)
uv pip install -e ~/agentic-mbse && uv pip install -e ".[dev]"

# Run spike script
uv run python scripts/spike_aggregation_validation.py

# Verify no src changes
git diff --name-only src/
```

**Model path:** `tests/fixtures/solar_battery_model` (from `tests/conftest.py:39-41`)

---

## Risk Management

**See research doc for detailed bug analysis:**
`.project/research/20260215-225131_aggregation-wiring-gap-analysis.md`

**Phase-Specific Mitigations:**
- **Phase 1**: If model fails to load, check that `agentic-mbse` is installed and SysIDE
  adapter is available. Fall back to the path used in test_parallel_validation.py.
- **Phase 2**: If CHAIN redef search produces unexpected results, compare against
  `hierarchy_data.redefinitions` directly to verify data integrity.
- **Phase 3**: If no SingletonTerm→aggregation cases exist in this model, document the
  gap and note that Bug 2 cannot be validated with this model.

## Implementation Notes

[TO BE FILLED DURING IMPLEMENTATION]

### Phase 1 Completion
**Completed:** 2026-02-15
**Actual Changes:**
- Created `scripts/spike_aggregation_validation.py` with model loading + Spike A logic
- Spike A dumps full registry (278 keys → 77 canonical channels), compares current vs
  proposed keys for all aggregation inputs

**Findings:**
- 58 total inputs: 12 SumTerms (resolvable) + 46 LocalTerms (always entry points)
- **0** current hits — Bug 1 fully confirmed (every unscoped registry lookup fails)
- **12** proposed hits — scoped key fix resolves ALL resolvable inputs
- No SingletonTerms found in this model (Bug 2 cannot be validated with this data)
- Key collisions observed for Key_D (bare-name) entries across assemblies (solar_array,
  battery_system, site_infra share capital_cost, raw_material_cost, etc.)
- The "70 inputs" from the E2E validation likely counted differently (possibly including
  multiplicity entry points, or came from a different model version)

**Issues:** None — script runs cleanly
**Deviations:**
- Input count is 58 (12 resolvable + 46 LocalTerm), not ~70 as predicted.
  The 70 figure from Phase 4 E2E likely counted multiplicity EPs or used a
  different counting method. The analysis still holds: all SumTerm registry
  lookups fail, scoped keys fix all of them.

### Phase 2 Completion
**Completed:** 2026-02-15
**Actual Changes:**
- Added `TraceResult` dataclass, `trace_sumterm_resolution()`, `trace_singleton_resolution()`,
  and `run_spike_b()` to the spike script
- Replicates `_resolve_aggregation_input_channel` (graph_builder.py:740-821) and
  SingletonTerm handling (lines 924-976) with full diagnostic tracing

**Findings:**
- 12 non-local inputs total: **8 resolved via CHAIN**, **0 via registry**, **4 failed → ENTRY_POINT**
- The 8 CHAIN successes match the prediction exactly — all are SumTerms where:
  - PV_Module PartDef has matching CHAIN redef (e.g., `:>> capital_cost = cost_model.total_cost`)
  - Battery_Pack also has matching CHAIN redefs (same cost_model pattern)
- **All 4 failures are CHAIN_PART_MISMATCH** — the `inverter` PartUsage:
  - There ARE CHAIN redefs for `capital_cost` etc. (9 candidates found)
  - But `String_Inverter` (the PartDef name) doesn't match `inverter` (the PartUsage name)
    via `sanitize_name("String_Inverter").lower()` → `"string_inverter"` ≠ `"inverter"`
  - This is a PartDef-name-to-PartUsage-name mismatch bug in the CHAIN search
- 0 SingletonTerms in this model (Bug 2 still unvalidated)
- 0 registry successes (all 4 failures also miss registry — confirms Bug 1)
- The research doc's prediction was correct: all successes are CHAIN-path

**Key Insight — New Bug Found:**
The `inverter` failures reveal a 4th bug not in the original analysis:
the CHAIN search matches `sanitize_name(owning_part_qn.split("__")[-1]).lower()`
against `part_usage.lower()`, but PartDef names (e.g., `String_Inverter`) don't
always match PartUsage names (e.g., `inverter`). The scoped registry fix will
resolve these since Phase 2 CHAIN aliases are correctly scoped.

**Issues:** None — script runs cleanly
**Deviations:** Found unexpected 4th failure mode (PartDef→PartUsage name mismatch)
not identified in the static analysis. This actually strengthens the case for the
registry-first fix, since registry aliases are scoped correctly regardless of naming.

### Phase 3 Completion
**Completed:** 2026-02-15
**Actual Changes:**
- Added `SpotCheckCase` dataclass, `find_closest_keys()`, `run_spike_c()`,
  and `generate_report()` to the spike script
- Generated `.project/active/aggregation-fix-validation/spike_report.md`

**Findings:**
- Case 1 (CHAIN success): scoped key also resolves → registry has the alias, confirming
  the registry-first approach would work even for currently-working CHAIN paths
- Case 2 (CHAIN_PART_MISMATCH): scoped key `solar_battery_plant.solar_array.inverter.capital_cost`
  resolves correctly → the fix would repair `String_Inverter` vs `inverter` mismatch
- Case 3 (substitute for SingletonTerm): scoped key resolves correctly for all
  tested failure cases
- Case 4 (top-level, Bug 3): hypothetical scoped key `solar_battery_plant.solar_array.capital_cost`
  does NOT resolve (confirms Key_E_stripped is needed). Bug 3 key
  `solar_battery_plant.capital_cost` resolves to the plant's OWN output, not the
  sub-assembly — a Key_D collision confirming the need for scoped keys.

**Issues:** None — all 3 spikes ran cleanly, report generated
**Deviations:**
- Case 3 substituted a SumTerm for SingletonTerm (none in model). Bug 2 remains
  unvalidated but is a clear code bug.
- Case 4 is hypothetical since top-level aggs use LocalTerms. The data still
  confirms Key_E_stripped is needed and the current Key_D collides.

---

**Status**: Complete
