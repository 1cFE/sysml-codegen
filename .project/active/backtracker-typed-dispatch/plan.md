# Component: DependencyBacktracker Typed Dispatch Migration (C11b)

**Status**: PLANNING
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

{Filled in after spike execution.}

### Spike Impact on Plan

{Filled in after spike.}

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
| `test_c11b_13_compat_only_now_typed` | REQ-BT-08, FR-4 | The 13 previously-compat-only resolutions (12 catf_mfe + 1 solar_battery) now resolve via typed lookups. Assert: for each, at least one of `scoped_lookup`, `alias_lookup`, `sysml_qn_lookup` returns the same CanonicalChannel as before. |
| `test_c11b_catf_cross_scope_via_alias` | REQ-BT-02 | The 12 catf_mfe cross-scope `minor_calc.a` CHAIN bindings resolve via `alias_lookup(ScopedKey("minor_calc.a"))` → correct CanonicalChannel. |
| `test_c11b_solar_reference_secondary_via_scoped` | REQ-BT-02 | The 1 solar_battery REFERENCE secondary (`annualized_om.p_net_kw`) resolves via `scoped_lookup(ScopedKey("solar_battery_plant.annualized_om.p_net_kw"))`. |
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
- [ ] Test file exists with all test cases written
- [ ] Tests run (expected: static analysis tests FAIL, outcome tests PASS)
- [ ] No test uses mocking (verified by grep for `mock`, `patch`, `MagicMock`)

---

## 4. Build Plan

### Files to Modify

| File | Change | Why |
|------|--------|-----|
| `analysis/dependency_backtracker.py` | Rewrite `_resolve_binding_via_registry()` to use type-directed dispatch; rewrite `_resolve_reference_via_registry()` to use typed lookups; add `_consumer_scope_dotted()`; add EXPRESSION binding dispatch | REQ-BT-08, FR-4 |
| `core/output_registry.py` | Remove `_compat` dict, `resolve()` method, `register()` method, `derive_key_c()` static method | FR-2, FR-3, remove deprecated API |
| `generation/initialization.py` | Migrate 3 `resolve()` calls in `build_output_registry()` Phases 2/3/4 to typed lookups; register instance_name.attr aliases during Phase 1a; remove compat key registration in Phase 1a/1b/1c | FR-4, eliminate _compat dependency |

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

Replace `resolve(scoped_key)` at line 453 with full-path normalization:

```python
# For source_path "SolarBatteryDesign::solar_battery_plant::annualized_om::p_net_kw"
parts = source_path.split("::")
# Drop segment[0] (design prefix), sanitize remaining, join with "."
sanitized = [sanitize_name(p).lower() for p in parts[1:]]
scoped_key = ScopedKey(".".join(sanitized))
# → "solar_battery_plant.annualized_om.p_net_kw"
channel = self._output_registry.scoped_lookup(scoped_key)
```

This replaces the current `parent_part.leaf` approach which only uses 2 segments.

#### 4. `build_output_registry()` migration

**Phase 1a**: In addition to typed registration, register `ScopedKey(f"{instance_name}.{attr.name}")` as an alias for each CalcUsage output. This replaces Key_A in `_compat` with an explicit alias. Also build a local `instance_attr_to_channel: dict[str, CanonicalChannel]` for Phase 3/4 use.

**Phase 1b/1c**: Remove compat registration calls (`registry.register(canonical, compat_keys)`).

**Phase 2**: Replace `registry.resolve(alias.canonical_name)` with `registry.scoped_lookup(ScopedKey(alias.canonical_name))`. CHAIN alias canonical_name is already ScopedKey format.

**Phase 3**: Replace `registry.resolve(alias.canonical_name)` with `instance_attr_to_channel.get(alias.canonical_name)` fallback to `registry.scoped_lookup(ScopedKey(alias.canonical_name))`.

**Phase 4**: Replace `registry.resolve(val)` with `registry.scoped_lookup(ScopedKey(val))` then `registry.alias_lookup(ScopedKey(val))`.

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
- [ ] All test cases pass (43 existing C11a + ~16 new C11b)
- [ ] No regressions in full test suite (`uv run pytest tests/`)
- [ ] Lint clean (`uv run ruff check src/`)

---

## 5. Validation

- [ ] Every acceptance criterion from IMPLEMENTATION_PLAN 3.1b is satisfied:
  - [ ] All 43 C11a conformance tests still green (outcomes unchanged)
  - [ ] Static analysis: `_resolve_binding_via_registry()` calls `scoped_lookup`/`sysml_qn_lookup`/`alias_lookup` (not `resolve()`)
  - [ ] Zero `resolve()` calls in `dependency_backtracker.py` and `build_output_registry()`
  - [ ] Zero `_compat` references in `output_registry.py`
  - [ ] 13 previously-compat-only resolutions now resolve via typed lookups
  - [ ] EXPRESSION bindings produce ENTRY_POINT with warning
- [ ] Every REQ-XX-NN has at least one passing test
- [ ] Full test suite passes (record count: ___ tests, 0 failures)
- [ ] Cross-check: re-read design intent docs 11, 24, 27, verify implementation matches
- [ ] No unresolved TODOs or FIXMEs in new/modified code
- [ ] COMPONENT_CHECKLIST and IMPLEMENTATION_PLAN have been updated

### Baseline Impact

The migration should be outcome-preserving for the 28 typed-reachable resolutions. The 13 compat-only resolutions will now resolve through different registry lookups (alias for catf_mfe, scoped for solar_battery). The resolved channels MUST be identical — any difference is a bug. Pipeline baselines should be unchanged.

---

## 6. Learnings

{Filled during/after build.}

### Findings

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

---

## 7. Commit

**Branch**: `cost-pattern-refactor` (current branch)
**Commit convention**: one commit per component

- [ ] All validation checks above are green
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
