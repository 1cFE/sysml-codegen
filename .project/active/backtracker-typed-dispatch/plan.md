# Component: DependencyBacktracker Typed Dispatch Migration (C11b)

**Status**: DONE
**Created**: 2026-02-17
**Last updated**: 2026-02-17
**Updated by**: Plan prompt — Claude Opus 4.6

## Source Documents

- **Checklist entry**: `COMPONENT_CHECKLIST.md` — C11
- **Design intent**: [11-analysis-backtracker.md](../../concepts/refactor-design-intent/11-analysis-backtracker.md), [27-typed-registry-refactor.md](../../concepts/refactor-design-intent/27-typed-registry-refactor.md), [24-dual-resolution-architecture.md](../../concepts/refactor-design-intent/24-dual-resolution-architecture.md)
- **Requirements**: REQ-BT-01 through REQ-BT-08, REQ-DRA-01, REQ-DRA-03, FR-4 (doc 27)
- **Depends on**: C11a (conformance safety net — DONE, 43 tests), C08 (typed registry — DONE)

---

## 1. Assessment

### What This Component Does

C11b migrates the DependencyBacktracker's resolution mechanism from the deprecated `resolve()` cascade (which hits `_compat` dict containing Key_A/Key_D/Key_F/bare keys) to type-directed dispatch using typed registry lookup methods. It also migrates 3 `resolve()` calls in `build_output_registry()` (Phases 2/3/4 alias registration) and removes `_compat` and `resolve()` entirely from `OutputRegistry`.

### Current State

- **Exists?** Yes — `analysis/dependency_backtracker.py` (715 lines), `core/output_registry.py` (271 lines), `generation/initialization.py` (~896 lines)
- **Needs refactoring?** Yes — 5 call sites use `resolve()`:
  1. `dependency_backtracker.py:481` — `_resolve_binding_via_registry()` Step 1
  2. `dependency_backtracker.py:491` — `_resolve_binding_via_registry()` Step 1b (SysML QN normalization)
  3. `dependency_backtracker.py:453` — `_resolve_reference_via_registry()` (REFERENCE secondary)
  4. `initialization.py:646` — Phase 2 CHAIN alias registration
  5. `initialization.py:672` — Phase 3 EXPOSE_PURE alias registration
  6. `initialization.py:694` — Phase 4 transitive alias registration
- **Current test coverage**: 43 C11a conformance tests verify resolution _outcomes_. 1250 total tests (0 failures). The C11a tests are the regression safety net for this migration.

### Design Consistency Check

- [x] All acceptance criteria from IMPLEMENTATION_PLAN 3.1b are testable with real data
- [x] AC are consistent with REQ-BT-08, REQ-DRA-03, FR-4 from design intent docs
- [x] No contradictions with other component specs
- [x] Input/output interfaces match — typed registries (C08) are already in place
- [x] Ambiguities resolved (documented below)

**Issues found during review:**

#### Issue #1: 12 catf_mfe cross-scope CHAIN resolutions need new mechanism

**Problem**: 12 CHAIN bindings in catf_mfe reference `minor_calc.a` from sibling calc usages in different radial build layers (vacuum_gap, first_wall, etc.). The producer is in `plasma_region` scope. Consumer-scoped lookup produces `catf_radial_build.vacuum_gap.minor_calc.a` but the scoped registry has `catf_radial_build.plasma_region.minor_calc.a`. Currently resolves through `_compat` via Key_A `minor_calc.a`.

**Resolution**: Register `{instance_name}.{attr}` as aliases during Phase 1a CalcUsage output registration. This creates an alias `ScopedKey("minor_calc.a") → CanonicalChannel` in the alias registry, replacing the Key_A _compat entry. The alias registry's first-wins collision policy handles the case where multiple producers share the same `instance_name.attr` pattern — same behavior as current _compat first-wins. Spike should verify: (a) how many Key_A-format keys have collisions, and (b) whether first-wins gives the correct resolution for all 12 catf_mfe cases.

#### Issue #2: 1 solar_battery REFERENCE secondary normalization is wrong

**Problem**: The REFERENCE secondary resolution (`_resolve_reference_via_registry()` at line 429) builds `parent_part.leaf` using only `segments[-2]` of the consuming usage's qualified name. For `SolarBatteryDesign::solar_battery_plant::annualized_om::p_net_kw`, it builds `annualized_om.p_net_kw` — but the scoped registry has `solar_battery_plant.annualized_om.p_net_kw` (full path minus design prefix).

**Resolution**: The REFERENCE Step 2 normalization should extract the full path from the `::` source_path: split on `::`, drop segment[0] (design prefix), sanitize each segment, join with `.`, then `scoped_lookup(ScopedKey(...))`. This produces `solar_battery_plant.annualized_om.p_net_kw` which IS in the scoped registry.

#### Issue #3: Phase 3 EXPOSE_PURE resolve() uses Key_A canonical_name format (D1 spike question)

**Problem**: `extract_computed_attributes()` produces `ChannelAlias(canonical_name=f"{instance_name}.{output_name}", ...)` for EXPOSE_PURE aliases. This `{instance_name}.{output_name}` is Key_A format (e.g., `cost_model.total_cost`), which doesn't match the scoped registry Key_C format (e.g., `parent.cost_model.total_cost`). Currently resolves through `_compat`. This is the core of the **D1 spike question** from IMPLEMENTATION_PLAN 3.1b.

**Resolution candidates** (evaluated in spike, see Spike Question #6):
- **(a)** Convert Key_A canonical_names to ScopedKey format upstream (in `extract_computed_attributes()` and `_build_chain_aliases()`) — cleanest long-term but widens the change surface
- **(b)** Build a local `instance_attr_to_channel: dict[str, CanonicalChannel]` mapping during Phase 1a registration within `build_output_registry()`. Map `{instance_name}.{attr} → CanonicalChannel` for each CalcUsage output. This is a local variable, not a persistent `_compat` — it exists only during registry construction. **Initial recommendation** based on assessment (spike verifies).
- **(c)** Keep `_compat` for alias registration only — simplest but leaves deprecated infrastructure partially alive, violating the "zero _compat references" AC

Spike must determine which option(s) work for ALL Phase 2/3/4 canonical_name formats across all fixture models.

#### Issue #4: Phase 2 CHAIN alias canonical_name format

**Assessment**: CHAIN alias `canonical_name` from `_build_chain_aliases()` is `{dotted_path}.{source_path}` (e.g., `solar_battery_plant.solar_array.sizing.nameplate_capacity`). This IS ScopedKey format matching Key_C in the scoped registry. Direct `scoped_lookup(ScopedKey(canonical_name))` should work. Spike should verify this for all Phase 2 aliases across fixture models.

#### Issue #5: Phase 4 transitive alias canonical_name format

**Assessment**: Phase 4 `val` is a dotted-path default_value (e.g., `cost_model.total_cost`). This is the same Key_A format as Issue #3. The same `instance_attr_to_channel` local dict can resolve it. Alternatively, `scoped_lookup()` + `alias_lookup()` cascading may work since Phase 2/3 aliases would have been registered by this point.

### Risks & Unknowns

1. **Risk: Key_A alias collisions.** If multiple CalcUsage outputs produce the same `instance_name.attr` key, first-wins may give wrong results. Need to verify the 12 catf_mfe cases all resolve to the correct channel.
2. **Risk: EXPOSE_PURE canonical_name edge cases.** May not all follow `{instance_name}.{output_name}` pattern.
3. **Unknown: Phase 4 resolve() targets.** Are all Phase 4 canonical values resolvable through scoped + alias lookups by Phase 4 (after Phase 2/3 aliases are registered)?
4. **Risk: EXPRESSION binding behavior.** No fixture coverage for EXPRESSION bindings. Documenting as ENTRY_POINT fallback is conservative but correct.

---

## 2. Spike

**Decision**: SPIKE
**Rationale**: Three unknowns require empirical verification before building:
1. The Key_A alias collision risk for catf_mfe (Issue #1) — need to verify all 12 compat-only CHAIN resolutions would get correct channels with first-wins alias registration.
2. The Phase 2/3/4 `resolve()` canonical_name formats (Issues #3-5) — need to verify which can use `scoped_lookup()` directly vs. need the `instance_attr_to_channel` helper.
3. The REFERENCE normalization fix (Issue #2) — need to verify the full-path ScopedKey construction matches the scoped registry for the solar_battery case.

### Spike Questions

1. For the 12 catf_mfe compat-only CHAIN resolutions: if `ScopedKey("{instance_name}.{attr}")` is registered as an alias (first-wins), does each resolution get the correct CanonicalChannel? Are there Key_A collisions that would give wrong results?
2. For Phase 2 `resolve(alias.canonical_name)`: does `scoped_lookup(ScopedKey(alias.canonical_name))` return the same result for ALL CHAIN aliases across all fixture models?
3. For Phase 3 `resolve(alias.canonical_name)`: what are the actual canonical_name values? Can they be resolved via `scoped_lookup()`, `alias_lookup()`, or do they need the `instance_attr_to_channel` helper?
4. For Phase 4 `resolve(val)`: by the time Phase 4 runs, are all transitive default values resolvable via `scoped_lookup()` + `alias_lookup()` (without `_compat`)?
5. For the solar_battery REFERENCE secondary: does the full-path normalization (`split(::) → drop[0] → sanitize → join(.)`) produce a ScopedKey that matches the scoped registry?
6. **D1 spike question** (from IMPLEMENTATION_PLAN): How do Phase 2/3/4 alias registration calls in `build_output_registry()` migrate away from `resolve()` when `canonical_name` values are in Key_A format (`instance_name.attr`)? Evaluate all three options:
   - **(a)** Convert Key_A canonical_names to ScopedKey during alias construction (in `_build_chain_aliases()` and `extract_computed_attributes()`) — upstream change, would make Phase 2/3/4 `resolve()` trivially replaceable
   - **(b)** Register Key_A values as scoped keys during Phase 1 (the `instance_attr_to_channel` local dict approach from Issue #3) — localized to `build_output_registry()`, no upstream changes
   - **(c)** Keep `_compat` for alias registration only and eliminate it for resolution — simplest but leaves deprecated infrastructure partially alive
   The spike must determine which option is correct by testing all Phase 2/3/4 canonical_name values against each option across all fixture models.

### Spike Approach

Write a diagnostic script that:
1. Loads each fixture model's extraction snapshot
2. Builds `build_output_registry()` with instrumented Phase 2/3/4 that logs: canonical_name value, `resolve()` result, `scoped_lookup()` result, `alias_lookup()` result, and `instance_attr_to_channel` result.
3. For the 12 catf_mfe compat-only: build the alias-registry alternative and verify outcomes.
4. For solar_battery REFERENCE secondary: verify full-path normalization produces correct ScopedKey.
5. **D1 evaluation**: For each Phase 2/3/4 `resolve(canonical_name)` call, test all 3 options:
   - (a) Would a ScopedKey-format canonical_name (constructed upstream) match `scoped_lookup()`?
   - (b) Would `instance_attr_to_channel[canonical_name]` return the correct CanonicalChannel?
   - (c) Would a restricted `_compat` (alias-registration-only) still be needed?
   Report pass/fail per option per model, with recommendation.
6. Report: which resolve() calls can be replaced with direct typed lookups, which need the helper dict.

### Spike Findings

**Diagnostic script**: `scripts/spike_c11b_typed_dispatch.py`

#### Q1: catf_mfe Key_A alias collision — PASS

- 25 Key_A collisions across catf_mfe (`minor_calc.a` × 11 layers, `volume_calc.volume` × 11 layers, `pump_load.pump_power` × 2)
- All 12 compat-only resolutions get the CORRECT channel with first-wins policy (they all reference `plasma_region`'s producer, which IS the first-wins value)
- **Safe to register `ScopedKey(f"{instance_name}.{attr}")` as alias during Phase 1a**

#### Q2: Phase 2 CHAIN scoped_lookup — PASS

- 41/41 solar_battery CHAIN aliases resolve via `scoped_lookup(ScopedKey(alias.canonical_name))`
- CHAIN `canonical_name` IS ScopedKey format (dotted hierarchy path from `_build_chain_aliases()`)
- catf_mfe, attr_expr_probe, chain_spike have 0 CHAIN aliases (these models use EXPOSE_PURE instead)

#### Q3: Phase 3 EXPOSE_PURE — Option B required

- 47 EXPOSE_PURE aliases (44 catf_mfe + 3 attr_expr_probe)
- **Option A (scoped_lookup): 0/47** — `canonical_name` is Key_A format (`instance_name.attr`), NOT ScopedKey format
- **Option B (instance_attr_to_channel): 47/47** — ALL PASS
- alias_lookup: 0/47 — not registered as aliases
- Example: `cn=wall_plug.wall_plug_power` → helper finds `CATFMFEHeating__catf_heating__wall_plug__wall_plug_power`

#### Q4: Phase 4 transitive — Option B required

- 47 resolvable transitive aliases (44 catf_mfe + 3 attr_expr_probe), 1 unresolvable (solar_battery `allocation_model.total_allocation`)
- scoped + alias: 0/47 — neither typed lookup works (values are Key_A format like `wall_plug.wall_plug_power`)
- **instance_attr_to_channel: 47/47** — ALL PASS
- Phase 4 values are the SAME Key_A-format strings as Phase 3 `canonical_name` values (transitive defaults mirror EXPOSE_PURE aliases)

#### Q5: REFERENCE secondary — PLAN CORRECTION NEEDED

**2 compat-only REFERENCE resolutions found (not 1 as C11a estimated):**

1. `annualized_om|p_net_kw`: source_path=`SolarBatteryDesign::solar_battery_plant::annualized_om::p_net_kw`
   - Step 1b normalization produces `annualized_om.p_net_kw` → resolve() None → falls to Step 2
   - Step 2 (REFERENCE secondary): `parent_part.leaf = solar_battery_plant.p_net_kw`
   - Resolves through `_compat` via **Key_F** (`{owning_part_name}.{python_name}` for FORMULA computed attribute `p_net_kw` on `solar_battery_plant`)
   - **Full-path normalization produces `solar_battery_plant.annualized_om.p_net_kw` — NOT in scoped registry, WRONG**
   - Fix: register Key_F as ScopedKey during Phase 1c

2. `annualized_financial|total_capex`: source_path=`SolarBatteryLibrary::'Solar Battery Plant'::capital_cost`
   - Step 1b normalization produces `solar_battery_plant.capital_cost` → resolve() hits Key_E_stripped (aggregation) → FOUND
   - Under typed dispatch: `scoped_lookup(ScopedKey("solar_battery_plant.capital_cost"))` → FOUND (already in scoped from Phase 1b)
   - This case works with the current plan's Step 1b rewrite (scoped_lookup after normalization)

**Critical finding**: The plan's Issue #2 full-path normalization approach is WRONG for case 1. The `parent_part.leaf` construction from the current code is correct; only the `resolve()` call needs replacement.

**C11a count correction**: The C11a spike counted 13 compat-only (12 catf_mfe + 1 solar_battery). Actual count is 14 (12 catf_mfe + 2 solar_battery). The second solar_battery case (`annualized_financial|total_capex`) was missed because the C11a typed-reachability check only tested sysml_qn_lookup and scoped_lookup for REFERENCE Step 1b — it didn't test alias_lookup. The current resolve() cascade finds it via scoped, but the C11a check was narrower.

#### Q6: D1 recommendation — Option B for Phase 3/4, Option A for Phase 2

| Phase | Count | Option A (scoped_lookup) | Option B (helper) | Recommendation |
|-------|-------|-------------------------|-------------------|----------------|
| Phase 2 CHAIN | 41 | 41/41 | 0/41 | **Option A** — canonical_name IS ScopedKey format |
| Phase 3 EXPOSE_PURE | 47 | 0/47 | 47/47 | **Option B** — canonical_name is Key_A format |
| Phase 4 Transitive | 47 | 0/47 | 47/47 | **Option B** — values are Key_A format |

**Additional requirement discovered**: Phase 1c FORMULA registration must also register Key_F as ScopedKey in the scoped registry (`register_scoped(ScopedKey(key_f), canonical)`). This is needed for the REFERENCE secondary path to find FORMULA outputs via `scoped_lookup()`.

### Spike Impact on Plan

#### Changes to Build Plan

1. **Issue #2 REWRITTEN**: ~~Full-path normalization for REFERENCE secondary~~. Instead: keep `parent_part.leaf` construction (it's correct), replace `resolve(scoped_key)` with `scoped_lookup(ScopedKey(key)) or alias_lookup(ScopedKey(key))` cascade. The current `_resolve_reference_via_registry()` approach at line 452 is correct in its key construction — only the resolution method changes.

2. **Issue #3 CONFIRMED**: Option B (instance_attr_to_channel local dict) for Phase 3 and Phase 4. Build this dict during Phase 1a registration in `build_output_registry()`.

3. **NEW: Phase 1c Key_F scoped registration**: Add `register_scoped(ScopedKey(f"{ca.owning_part_name}.{ca.python_name}"), canonical)` during Phase 1c. This makes FORMULA outputs discoverable by the REFERENCE secondary `scoped_lookup()` path. Only 1 FORMULA across all models (solar_battery `p_net_kw`), but the registration is cheap.

4. **Build plan §3 update**: `_resolve_reference_via_registry()` rewrite uses `scoped_lookup()` then `alias_lookup()` cascade instead of full-path normalization. Keep `parent_part.leaf` construction unchanged.

5. **Test plan update**: `test_c11b_solar_reference_secondary_via_scoped` should verify the `parent_part.leaf` approach resolves via `scoped_lookup()` (for Key_F hit) or `alias_lookup()` (for CHAIN alias hit), not via full-path normalization.

6. **Count update**: 14 compat-only resolutions total (12 catf_mfe + 2 solar_battery), not 13.

---

## 3. Test Plan

**Test file**: `tests/conformance/test_backtracker.py` (extend existing C11a file)
**Fixture data**: solar_battery_model, catf_mfe_model, attr_expr_probe, chain_spike_model

### Test Cases

> C11b tests verify the _mechanism_ (typed dispatch), not just outcomes.
> C11a tests (43 existing) verify outcomes remain unchanged.
> Combined: mechanism + outcomes = complete coverage.

| Test | Requirement | What it verifies |
|------|-------------|------------------|
| All 43 existing C11a tests | REQ-BT-01–08, REQ-DRA-01 | Outcomes unchanged after migration (regression safety net) |
| `test_c11b_no_resolve_calls_in_backtracker` | REQ-BT-08, FR-4 | Static analysis: `_resolve_binding_via_registry()` and `_resolve_reference_via_registry()` do NOT call `self._output_registry.resolve()`. Must call `scoped_lookup`, `sysml_qn_lookup`, or `alias_lookup` instead. |
| `test_c11b_no_resolve_calls_in_build_registry` | FR-4 | Static analysis: `build_output_registry()` does NOT call `registry.resolve()`. |
| `test_c11b_no_compat_dict_in_registry` | FR-3 | `OutputRegistry` class has no `_compat` attribute. `hasattr(OutputRegistry(), '_compat')` is False. |
| `test_c11b_no_resolve_method_on_registry` | FR-2 | `OutputRegistry` class has no `resolve` method. `hasattr(OutputRegistry(), 'resolve')` is False. |
| `test_c11b_chain_dispatch_uses_scoped_then_alias` | REQ-BT-08, REQ-DRA-03 | For solar_battery CHAIN MODULE_OUTPUTs: the resolved channel equals `registry.scoped_lookup(ScopedKey(consumer_scope + "." + source_path))` or `registry.alias_lookup(ScopedKey(source_path))`. No compat fallback needed. |
| `test_c11b_reference_dispatch_uses_sysml_qn_then_scoped` | REQ-BT-08, REQ-DRA-03 | For attr_expr_probe REFERENCE MODULE_OUTPUTs: the resolved channel equals `registry.sysml_qn_lookup(SysMLQN(source_path))` or `registry.scoped_lookup(ScopedKey(normalized_path))`. |
| `test_c11b_14_compat_only_now_typed` | REQ-BT-08, FR-4 | The 14 previously-compat-only resolutions (12 catf_mfe + 2 solar_battery) now resolve via typed lookups. Assert: for each, at least one of `scoped_lookup`, `alias_lookup`, `sysml_qn_lookup` returns the same CanonicalChannel as before. |
| `test_c11b_catf_cross_scope_via_alias` | REQ-BT-02 | The 12 catf_mfe cross-scope `minor_calc.a` CHAIN bindings resolve via `alias_lookup(ScopedKey("minor_calc.a"))` → correct CanonicalChannel. |
| `test_c11b_solar_reference_secondary_via_typed` | REQ-BT-02 | The 2 solar_battery REFERENCE secondary resolutions resolve via typed lookups: (a) `annualized_om\|p_net_kw` via `scoped_lookup(ScopedKey("solar_battery_plant.p_net_kw"))` (Key_F hit), (b) `annualized_financial\|total_capex` via Step 1b scoped_lookup after :: normalization. |
| `test_c11b_expression_binding_entry_point` | REQ-BT-01 gap | EXPRESSION bindings (if encountered) produce `BindingResolution(ENTRY_POINT)` with a warning log, not silent skip. |
| `test_c11b_consumer_scope_dotted` | FR-4 | `_consumer_scope_dotted(usage)` for `Design__solar_battery_plant__lcoe` returns `"solar_battery_plant"`. For `Design__catf_radial_build__vacuum_gap__volume_calc` returns `"catf_radial_build.vacuum_gap"`. |
| `test_c11b_phase2_alias_no_resolve` | FR-4 | Phase 2 CHAIN alias registration resolves canonical_name via `scoped_lookup()` (not `resolve()`). Verified by registry content equality: same aliases registered before and after migration. |
| `test_c11b_phase3_expose_pure_no_resolve` | FR-4 | Phase 3 EXPOSE_PURE alias registration resolves canonical_name without `resolve()`. Same aliases registered. |
| `test_c11b_phase4_transitive_no_resolve` | FR-4 | Phase 4 transitive alias registration resolves without `resolve()`. Same aliases registered. |
| `test_c11b_no_deprecated_register_method` | FR-3 | `OutputRegistry` has no `register()` method (the deprecated compat registration). |

### Test Infrastructure Needed

- **`_consumer_scope_dotted()` function**: New function in `dependency_backtracker.py`. Extracts consumer scope from usage.qualified_name by splitting on `__`, dropping segment[0] (design prefix) and segment[-1] (usage name), joining with `.`.
- **Existing**: `build_backtracker_from_snapshot()` helper from C11a tests.
- **New assertion helpers**: `_check_typed_reachability()` (adapted from spike script) for verifying each resolution is typed-reachable.

### Gate: Ready for BUILD
- [x] Test file exists with all test cases written (18 C11b tests: 16 from plan + 2 bonus)
- [x] Tests run (2 expected failures: resolve() and register() still on OutputRegistry; 58 pass)
- [x] No test uses mocking (verified by grep for mock, patch, MagicMock)

---

## 4. Build Plan

### Files to Modify

| File | Change | Why |
|------|--------|-----|
| `analysis/dependency_backtracker.py` | Rewrite `_resolve_binding_via_registry()` to use type-directed dispatch; rewrite `_resolve_reference_via_registry()` to use typed lookups; add `_consumer_scope_dotted()`; add EXPRESSION binding dispatch | REQ-BT-08, FR-4 |
| `core/output_registry.py` | Remove `_compat` dict, `resolve()` method, `register()` method, `derive_key_c()` static method | FR-2, FR-3, remove deprecated API |
| `generation/initialization.py` | Migrate 3 `resolve()` calls in `build_output_registry()` Phases 2/3/4 to typed lookups; register instance_name.attr aliases during Phase 1a; remove compat key registration in Phase 1a/1b/1c | FR-4, eliminate _compat dependency |
| `resolution/graph_builder.py` | Migrate 3 `resolve()` calls in `_resolve_expose_pure()` and `_resolve_aggregation_input_channel()` to `scoped_lookup` then `alias_lookup` cascades | DEV-3: missed in original plan, required because `resolve()` removed from OutputRegistry |

### Implementation Notes

#### 1. `_consumer_scope_dotted(usage)` (new function)

```python
def _consumer_scope_dotted(self, usage: CalcUsageData) -> str:
    """Extract consumer scope from usage QN for ScopedKey construction.

    "Design__solar_battery_plant__lcoe" → "solar_battery_plant"
    "Design__catf_radial_build__vacuum_gap__volume_calc" → "catf_radial_build.vacuum_gap"
    """
    segments = usage.qualified_name.split("__")
    if len(segments) <= 2:
        return ""
    return ".".join(segments[1:-1])
```

#### 2. `_resolve_binding_via_registry()` rewrite

Replace the current `resolve()` cascade (lines 476-535) with:

```
CHAIN (no "::" in source_path):
  Step 1: scoped_lookup(ScopedKey(consumer_scope + "." + source_path))
  Step 2: alias_lookup(ScopedKey(source_path))  [cross-scope]
  Step 3: design_attribute match → ENTRY_POINT
  Step 4: fallback → ENTRY_POINT with warning

REFERENCE ("::" in source_path):
  Step 1: sysml_qn_lookup(SysMLQN(source_path))
  Step 2: Full-path normalization → scoped_lookup(ScopedKey(normalized))
  Step 3: design_attribute match → ENTRY_POINT
  Step 4: fallback → ENTRY_POINT with warning

EXPRESSION (source_path is None but binding_type is EXPRESSION):
  Log warning, create ENTRY_POINT resolution
```

Each step includes the self-reference guard.

#### 3. `_resolve_reference_via_registry()` rewrite

**Spike finding**: The plan's original full-path normalization approach is WRONG for case 1 (`annualized_om.p_net_kw` — this key doesn't exist in the scoped registry). The current `parent_part.leaf` construction is correct. Only the resolution method changes:

Replace `resolve(scoped_key)` at line 453 with `scoped_lookup() → alias_lookup()` cascade:

```python
# Keep existing parent_part.leaf construction (correct)
parent_part = self._get_parent_part_for_usage(usage)
if parent_part:
    scoped_key = ScopedKey(f"{parent_part}.{leaf}")
    channel = self._output_registry.scoped_lookup(scoped_key)
    if channel is None:
        channel = self._output_registry.alias_lookup(scoped_key)
    if channel is not None:
        # Self-reference guard (unchanged)
        ...
```

The `scoped_lookup` path covers Key_F (FORMULA outputs registered in Phase 1c) and Key_E_stripped (aggregation outputs). The `alias_lookup` fallback covers CHAIN aliases that bridge the same key.

#### 4. `build_output_registry()` migration

**Phase 1a**: In addition to typed registration, register `ScopedKey(f"{instance_name}.{attr.name}")` as an alias for each CalcUsage output. This replaces Key_A in `_compat` with an explicit alias (first-wins collision policy — 25 collisions in catf_mfe, all giving correct results per spike Q1). Also build a local `instance_attr_to_channel: dict[str, CanonicalChannel]` for Phase 3/4 use. Remove the `registry.register(canonical, [key_a])` compat call.

**Phase 1b**: Remove compat registration calls (`registry.register(canonical, compat_keys)`).

**Phase 1c**: Remove compat registration (`registry.register(canonical, [key_f, ca.python_name])`). **NEW (spike Q5)**: Also register Key_F as ScopedKey: `registry.register_scoped(ScopedKey(f"{ca.owning_part_name}.{ca.python_name}"), canonical)`. This makes FORMULA outputs discoverable by the REFERENCE secondary `scoped_lookup()` path.

**Phase 2**: Replace `registry.resolve(alias.canonical_name)` with `registry.scoped_lookup(ScopedKey(alias.canonical_name))`. CHAIN alias canonical_name is already ScopedKey format.

**Phase 3**: Replace `registry.resolve(alias.canonical_name)` with `instance_attr_to_channel.get(alias.canonical_name)` fallback to `registry.scoped_lookup(ScopedKey(alias.canonical_name))`.

**Phase 4**: Replace `registry.resolve(val)` with `instance_attr_to_channel.get(val)` then `registry.scoped_lookup(ScopedKey(val))` then `registry.alias_lookup(ScopedKey(val))`. (Spike Q4 confirmed scoped+alias alone gives 0/47 — values are Key_A format, requiring the helper first.)

#### 5. OutputRegistry cleanup

Remove from `OutputRegistry`:
- `_compat: dict[str, CanonicalChannel]` attribute
- `register()` method
- `resolve()` method
- `derive_key_c()` static method
- `_compat` from `__len__()` calculation
- `_compat` from `__repr__()`

#### 6. EXPRESSION binding dispatch

In `_trace_dependencies()`, after the `if binding.source_path:` block (line 362), add an explicit EXPRESSION handling block:

```python
elif binding.binding_type == BindingType.EXPRESSION:
    # EXPRESSION bindings not yet supported — create ENTRY_POINT
    entry_point_qn = f"{usage.qualified_name}__{param_name}"
    logger.warning(
        "EXPRESSION binding %s|%s: no dispatch path, treating as entry point",
        usage.qualified_name, param_name,
    )
    self._binding_resolutions[mapping_key] = BindingResolution(
        resolution_type=BindingResolutionType.ENTRY_POINT,
        qualified_name=entry_point_qn,
        source_path=None,
        is_transitive=False,
    )
```

### Gate: Ready for VALIDATE
- [x] All test cases pass (43 existing C11a + 18 C11b = 61 conformance, 1273 total)
- [x] No regressions in full test suite (`uv run pytest tests/` — 1273 passed, 5 xfailed)
- [x] Lint clean (0 new errors; 19 pre-existing)

---

## 5. Validation

- [x] Every acceptance criterion from IMPLEMENTATION_PLAN 3.1b is satisfied:
  - [x] All 43 C11a conformance tests still green (outcomes unchanged) *(60 total C11 tests pass)*
  - [x] Static analysis: `_resolve_binding_via_registry()` calls `scoped_lookup`/`sysml_qn_lookup`/`alias_lookup` (not `resolve()`)
  - [x] Zero `resolve()` calls in `dependency_backtracker.py` and `build_output_registry()`
  - [x] Zero `_compat` references in `output_registry.py`
  - [x] 14 previously-compat-only resolutions now resolve via typed lookups
  - [x] EXPRESSION bindings produce ENTRY_POINT with warning
- [x] Every REQ-XX-NN has at least one passing test
- [x] Full test suite passes (record count: 1273 tests, 0 failures, 5 xfailed)
- [x] Cross-check: design intent docs 11, 24, 27 match implementation *(verified 2026-02-17)*
- [x] No unresolved TODOs or FIXMEs in new/modified code
- [x] COMPONENT_CHECKLIST and IMPLEMENTATION_PLAN have been updated *(2026-02-17 audit session)*

### Baseline Impact

The migration should be outcome-preserving for the 27 typed-reachable resolutions. The 14 compat-only resolutions (12 catf_mfe cross-scope CHAIN + 2 solar_battery REFERENCE secondary) will now resolve through different registry lookups: alias for catf_mfe (instance_name.attr aliases), scoped for solar_battery case 1 (Key_F registration), scoped for solar_battery case 2 (Key_E_stripped already in scoped). The resolved channels MUST be identical — any difference is a bug. Pipeline baselines should be unchanged.

---

## 6. Learnings

### Findings

1. **1 unresolvable Phase 4 transitive alias: `allocation_model.total_allocation`** (solar_battery).
   This value resolves to `None` in ALL approaches (scoped, alias, instance_attr_to_channel).
   The current `resolve()` cascade also returns None → alias is not registered. This is
   outcome-preserving behavior — either dead data in the model or a resolution gap upstream.
   No action needed; documented for future investigation.

2. **C11b spike corrected compat-only count from 13 to 14.** The second solar_battery case
   (`annualized_financial|total_capex`) was missed by C11a because the typed-reachability check
   only tested sysml_qn_lookup and scoped_lookup for REFERENCE Step 1b — it didn't test the
   Step 1b normalization producing a key already in the scoped registry (Key_E_stripped hit).

3. **Phase 4 requires instance_attr_to_channel, not just scoped+alias.** The build plan §4
   originally said scoped+alias for Phase 4, but spike Q4 confirmed 0/47 pass with
   scoped+alias alone (values are Key_A format). Corrected to use the helper first.

### Design Doc Updates Needed
| Doc | What to update | Why |
|-----|---------------|-----|
| {filled after build} | | |

### Cross-Component Impact
| Component | Impact | Action needed |
|-----------|--------|---------------|
| C12 (Input Resolver) | If `resolve()` is removed from OutputRegistry, C12 strategies must use typed lookups from the start | No change — C12 design docs already specify typed lookups |
| Phase 7.4 (Dead code) | `resolve()`, `register()`, `_compat`, `derive_key_c()` removed here — mark as done in 7.4 | Update IMPLEMENTATION_PLAN |

### Deviations from Plan

#### DEV-1: CHAIN dispatch Step 1b — direct scoped_lookup without consumer prefix

**Where**: `dependency_backtracker.py:577-581` (`_resolve_chain_dispatch`)
**Plan said** (§4.2): Steps 1 (consumer-scoped), 2 (alias) only.
**Implementation adds**: Step 1b — `scoped_lookup(ScopedKey(source_path))` without consumer scope prefix.
**Why**: Key_F FORMULA outputs (e.g., `plant.p_net_kw`) are registered as bare ScopedKeys in Phase 1c. Step 1 builds `consumer_scope.source_path` (e.g., `solar_battery_plant.plant.p_net_kw`) — doesn't exist. Step 2 (alias) — not in alias registry. Without Step 1b, these CHAIN bindings silently fall through to ENTRY_POINT, breaking wiring.
**Risk**: LOW — restores behavior `_compat` previously provided. Conformance outcomes unchanged.

#### DEV-2: REFERENCE secondary consumer_scope fallback

**Where**: `dependency_backtracker.py:489-497` (`_resolve_reference_via_registry`)
**Plan said** (§4.3): Keep `parent_part.leaf` construction, only replace `resolve()` with `scoped_lookup`/`alias_lookup`.
**Implementation adds**: Full consumer scope fallback using `_consumer_scope_dotted()` when `parent_part` alone doesn't resolve.
**Why**: `_get_parent_part_for_usage()` returns only `segments[-2]` (e.g., `assembly`) but Key_E_stripped aggregation outputs are registered with full scope (e.g., `plant.assembly.total_cost`). Without the fallback, these bindings break.
**Risk**: LOW-MEDIUM — adds a new resolution path that expands the search space for REFERENCE secondary. Self-reference guard is applied. Conformance outcome tests provide the safety net.

#### DEV-3: graph_builder.py modifications not in plan

**Where**: `resolution/graph_builder.py` — 3 call sites (`_resolve_expose_pure`, `_resolve_aggregation_input_channel` ×2)
**Plan said** (§4 "Files to Modify"): 3 files only (backtracker, registry, initialization).
**Implementation also modifies**: `graph_builder.py` — migrated 3 `resolve()` calls to `scoped_lookup` then `alias_lookup` cascades.
**Why**: `resolve()` was removed from `OutputRegistry`, so ALL consumers must migrate. The plan missed these 3 call sites in graph_builder.py.
**Risk**: LOW — `scoped_lookup → alias_lookup` cascade is semantically equivalent to what `resolve()` did for these key formats.

---

## 7. Commit

**Branch**: `cost-pattern-refactor` (current branch)
**Commit convention**: one commit per component

- [x] All validation checks above are green *(verified 2026-02-17: 1273 passed, 5 xfailed, 0 failures)*
- [ ] `git add` specific files: `dependency_backtracker.py`, `output_registry.py`, `initialization.py`, `test_backtracker.py`, plus IMPLEMENTATION_PLAN.md and COMPONENT_CHECKLIST.md
- [ ] Commit message format:
  ```
  refactor(C11b): DependencyBacktracker typed dispatch migration

  - Rewrite _resolve_binding_via_registry() to type-directed dispatch
  - Migrate build_output_registry() Phases 2/3/4 from resolve() to typed lookups
  - Register instance_name.attr aliases for cross-scope CHAIN resolution
  - Add EXPRESSION binding → ENTRY_POINT dispatch path
  - Remove _compat dict, resolve(), register() from OutputRegistry
  - Tests: N new mechanism tests in tests/conformance/test_backtracker.py
  - Refs: REQ-BT-01 through REQ-BT-08, REQ-DRA-01, REQ-DRA-03, FR-4
  - Design intent: 11, 24, 27
  ```
- [ ] Committed successfully

---

## Progress Log

### Session: 2026-02-17 — Plan prompt

**Phase**: PLANNING
**Work done**:
- Read all design docs (11, 24, 27), component checklist, implementation plan
- Read current source: `dependency_backtracker.py` (715 lines, 6 resolve() call sites), `output_registry.py` (271 lines, _compat/resolve/register), `initialization.py` (~896 lines, build_output_registry Phase 2/3/4)
- Read C11a plan with spike findings (13 compat-only, resolution breakdown per model)
- Read C11a conformance tests (43 tests, all passing)
- Read spike diagnostic script with typed reachability analysis
- Read `identifier_types.py` (NewType definitions and constructors)
- Read `extract_computed_attributes()` EXPOSE_PURE alias construction (canonical_name = Key_A format)
- Identified 5 design consistency issues with resolutions
- Made SPIKE decision (Key_A alias collision risk + Phase 2/3/4 canonical_name format investigation)
- Wrote 16-test plan (mechanism verification) + 43 existing C11a outcome tests
- Wrote build plan for 3 production files + test extension
**Stopped at**: Plan complete, ready for SPIKE execution
**Next step**: Execute spike (diagnostic verifying alias collision safety + Phase 2/3/4 typed lookup feasibility), then BUILD
**Blockers**: None

### Session: 2026-02-17 — Spike execution + TEST entry

**Phase**: SPIKE → TEST
**Work done**:
- Wrote `scripts/spike_c11b_typed_dispatch.py` (370 lines) answering all 6 spike questions
- Q1 (catf_mfe alias collision): PASS — 25 collisions, all 12 compat-only get correct channel with first-wins
- Q2 (Phase 2 CHAIN scoped_lookup): PASS — 41/41 CHAIN aliases resolve via scoped_lookup
- Q3 (Phase 3 EXPOSE_PURE): Option B (instance_attr_to_channel) required — 47/47 work, scoped_lookup 0/47
- Q4 (Phase 4 transitive): Option B required — 47/47 work, scoped+alias 0/47
- Q5 (REFERENCE secondary): **PLAN CORRECTION** — full-path normalization WRONG for case 1. Keep parent_part.leaf, use scoped→alias cascade. Found 2 compat-only (not 1): second case resolves through Key_F for FORMULA computed attribute. Need Phase 1c Key_F scoped registration.
- Q6 (D1 evaluation): Phase 2 = Option A (scoped), Phase 3/4 = Option B (helper), Phase 1c = Key_F scoped registration
- Updated build plan §3 (REFERENCE rewrite), §4 (Phase 1a/1b/1c), test plan (14 compat-only, not 13)
- Advanced status to TEST
**Stopped at**: Spike complete, plan updated. Ready for TEST phase (write test cases).
**Next step**: Write C11b test cases in `tests/conformance/test_backtracker.py`
**Blockers**: None

### Session: 2026-02-17 — TEST + BUILD

**Phase**: TEST → BUILD (in progress)

**Critical finding**: C11a (committed as f481dbe) already implemented ~90% of C11b's scope:
- Backtracker typed dispatch (`_resolve_chain_dispatch`, `_resolve_reference_dispatch`) — DONE
- `_consumer_scope_dotted()` — DONE
- `_compat` removal from OutputRegistry — DONE
- `derive_key_c()` removal — DONE
- Phase 1a alias registration (instance_name.attr as ScopedKey) — DONE
- Phase 1c Key_F scoped registration — DONE
- `build_output_registry()` Phases 2/3/4 resolve() calls migrated — DONE
- EXPRESSION binding → ENTRY_POINT dispatch — DONE

**Remaining C11b scope**: Remove `resolve()` and `register()` convenience methods from OutputRegistry.

**TEST phase work done**:
- Found 2 missing tests from plan: `test_c11b_no_resolve_method_on_registry`, `test_c11b_no_deprecated_register_method` — added
- Fixed C11a gap test `test_expression_bindings_silently_skipped` → `test_expression_bindings_resolve_as_entry_point` (C11a already handles EXPRESSION bindings)
- Fixed `test_c11b_typed_lookups_present_in_backtracker` — AST analysis now checks `_resolve_chain_dispatch`/`_resolve_reference_dispatch` (C11a split dispatch into helper methods)
- Fixed `test_c11b_catf_cross_scope_via_alias` — all minor_calc.a bindings resolve locally via scoped_lookup (each layer has own minor_calc); test now verifies alias IS registered (first-wins → plasma_region) and each binding resolves to correct scope
- TEST gate satisfied: 58 pass, 2 expected failures (resolve/register still on OutputRegistry)

**BUILD phase work done**:
- Removed `resolve()` and `register()` from `OutputRegistry` class
- Created `tests/helpers/registry_compat.py` with `registry_resolve()` and `registry_register()` test helpers
- Updating 10 test files to use helpers instead of removed methods (subagent in progress)
  - tests/unit/test_output_registry.py
  - tests/unit/test_output_registry_construction.py
  - tests/unit/test_graph_builder_aggregation.py
  - tests/unit/test_backtracker_aggregation.py
  - tests/unit/test_backtracker_computed_attrs.py
  - tests/unit/test_graph_builder_computed_attrs.py
  - tests/integration/test_output_registry_smoke.py
  - tests/integration/test_parallel_validation.py
  - tests/conformance/test_computed_attributes.py
  - tests/conformance/test_output_registry.py

**Stopped at**: BUILD in progress — subagent updating test files with registry_compat helpers
**Next step**: Run full test suite, fix any remaining failures, advance to VALIDATE
**Blockers**: None

### Session: 2026-02-17 — BUILD completion

**Phase**: BUILD → VALIDATE ready

**Production code fixes** (3 issues found during full test suite run):

1. **CHAIN dispatch Step 1b** (`dependency_backtracker.py`): Added direct `scoped_lookup(ScopedKey(source_path))` without consumer scope prefix. Key_F FORMULA outputs (e.g., `plant.p_net_kw`) are registered as bare scoped keys but CHAIN dispatch only tried consumer-scoped (`Part.plant.p_net_kw`) then alias. Step 1b covers the direct scoped path.

2. **REFERENCE secondary consumer_scope fallback** (`dependency_backtracker.py`): `_get_parent_part_for_usage()` returns only `segments[-2]` (e.g., `assembly`) but Key_E_stripped aggregation outputs are registered with full scope (e.g., `plant.assembly.total_cost`). Added fallback using `_consumer_scope_dotted()` for full consumer scope when parent_part alone doesn't resolve.

3. **Aggregation input alias_lookup fallback** (`graph_builder.py`): `_resolve_aggregation_input_channel()` only did `scoped_lookup` for scoped keys but EXPOSE_PURE aliases (e.g., `inverter.fabrication_cost`) are in the alias registry, not scoped. Added `alias_lookup` fallback after `scoped_lookup` in the scoped path.

**Additional fix**: Removed unused `part_usage` variable in `initialization.py:582` (F841 lint error introduced by compat removal).

**Test file updates** (25 unit test failures fixed across 4 files via parallel agents):
- `tests/unit/test_backtracker_aggregation.py` — Updated all assertions from old Key_D/bare key formats to Key_E_stripped. Updated usage qualified_names to produce correct consumer scopes. (20 tests pass)
- `tests/unit/test_backtracker_computed_attrs.py` — Changed bare key assertions to negative, updated SysML QN tests, fixed transitive EXPOSE_PURE test scoping. (19 tests pass)
- `tests/unit/test_output_registry_construction.py` — Converted bare/legacy key tests to negative assertions, fixed synthetic EXPOSE_PURE canonical_name from EQN to Key_A format. (47 tests pass)
- `tests/unit/test_output_registry.py` — Updated `__repr__` assertions to remove `compat=` field, updated alias counts. (41 tests pass)
- `tests/integration/test_parallel_validation.py` — Updated `test_reference_secondary_capital_cost` to Key_E_stripped format.
- `tests/fixtures/baseline_yaml/solar_battery.yaml` — No change (verified: `git diff` shows no diff; baselines unchanged by this migration).

**BUILD gate results**:
- Full test suite: **1273 passed, 5 xfailed, 0 failures**
- Lint: 19 pre-existing errors, 0 new (F841 fixed)
- No regressions

**Stopped at**: BUILD complete. Ready for VALIDATE.
**Next step**: Work through §5 Validation checklist
**Blockers**: None
