# Test Migration Audit: Backtracker Internal Index Tests

**Created:** 2026-02-14
**Purpose:** Categorize all tests accessing `_computed_attr_index` and `_aggregation_output_index` for Item 4 migration.
**Scope:** `tests/unit/test_backtracker_computed_attrs.py` (19 tests), `tests/unit/test_backtracker_aggregation.py` (20 tests)

## Categories

- **(a) Registration behavior** — Tests that verify what keys exist in `_computed_attr_index` or `_aggregation_output_index`, or call private channel-building methods. **Migration:** Rewrite to test `build_output_registry()` + `registry.resolve(key)`.
- **(b) Resolution behavior** — Tests that verify binding resolution outcomes (`_binding_resolutions`) via `find_required_modules()`. **Migration:** Add `build_output_registry()` call, pass registry to backtracker, verify same resolution outcome.
- **(c) Integration** — Tests that verify end-to-end behavioral properties (trace log, LITERAL fast-path, backward compat) without directly accessing internal indexes. **Migration:** Minimal — add registry parameter if Item 4 requires it.

---

## test_backtracker_computed_attrs.py (19 tests)

### TestComputedAttrIndex — 7 tests, all (a)

| # | Test | Category | Internal Access | Migration Action |
|---|------|----------|----------------|-----------------|
| 1 | `test_index_keys_dotted_and_bare` | (a) | `_computed_attr_index["plant.p_net_kw"]`, `_computed_attr_index["p_net_kw"]` | Rewrite: `registry.resolve("plant.p_net_kw")` and `registry.resolve("p_net_kw")` both return non-None canonical channel |
| 2 | `test_expose_pure_excluded_from_index` | (a) | `_computed_attr_index` membership check | Rewrite: `registry.resolve("part.eta")` returns None (EXPOSE_PURE not registered in Phase 1 FORMULA block) |
| 3 | `test_expose_computed_excluded_from_index` | (a) | `_computed_attr_index` membership check | Rewrite: `registry.resolve("part.scaled")` returns None (EXPOSE_COMPUTED excluded) |
| 4 | `test_manual_required_formula_excluded_from_index` | (a) | `_computed_attr_index` membership check | Rewrite: `registry.resolve("part.broken")` returns None (MANUAL_REQUIRED excluded) |
| 5 | `test_empty_computed_attrs` | (a) | `_computed_attr_index == {}` | Rewrite: build registry with no computed attrs, verify resolve returns None for arbitrary keys |
| 6 | `test_none_computed_attrs` | (a) | `_computed_attr_index == {}` | Rewrite: same as #5 with `computed_attributes=None` → empty list default |
| 7 | `test_multiple_parts_in_index` | (a) | `_computed_attr_index` membership + `len()` | Rewrite: verify `registry.resolve()` returns distinct channels for each part's attrs |

### TestBuildComputedAttrChannel — 2 tests, all (a)

| # | Test | Category | Internal Access | Migration Action |
|---|------|----------|----------------|-----------------|
| 8 | `test_simple_channel_name` | (a) | `_build_computed_attr_channel()` | Rewrite: `registry.resolve("probe_design.area")` returns `"AttrExprProbeDesign__probe_design__area__area"` |
| 9 | `test_nested_namespace_channel` | (a) | `_build_computed_attr_channel()` | Rewrite: `registry.resolve("plant.p_net_kw")` returns `"CATFDesign__FusionPlant__plant__p_net_kw__p_net_kw"` |

### TestComputedAttrResolution — 6 tests: 4 (b), 2 (c)

| # | Test | Category | Internal Access | Migration Action |
|---|------|----------|----------------|-----------------|
| 10 | `test_binding_to_formula_resolves_module_output` | (b) | `_binding_resolutions[key]` | Add `output_registry` param. Assertion unchanged — MODULE_OUTPUT with same channel. |
| 11 | `test_dotted_path_bare_name_fallback` | (b) | `_binding_resolutions[key]` | Add `output_registry` param. Bare-name fallback now happens inside `registry.resolve()`. Same outcome. |
| 12 | `test_non_formula_binding_unchanged` | (b) | `_binding_resolutions[key]` | Add `output_registry` param. EXPOSE_PURE still not resolvable via Phase 1 FORMULA → ENTRY_POINT. Same outcome. |
| 13 | `test_bare_name_binding_resolves` | (b) | `_binding_resolutions[key]` | Add `output_registry` param. Same outcome. |
| 14 | `test_trace_log_contains_computed_attr_entry` | (c) | `result.trace_log` | Item 4: trace log label may change from `COMPUTED_ATTR` to `REGISTRY` or similar. Update expected string. |
| 15 | `test_literal_binding_not_affected_by_computed_attrs` | (c) | `_binding_resolutions[key]` | Minimal — LITERAL fast-path unchanged by registry. Add `output_registry` if backtracker requires it. |

### TestSysmlQualifiedNameIndex — 2 tests, all (a)

| # | Test | Category | Internal Access | Migration Action |
|---|------|----------|----------------|-----------------|
| 16 | `test_sysml_qn_key_in_index` | (a) | `_computed_attr_index` membership + `len()` | Rewrite: `registry.resolve("E2EDesign::e2e_plant::power_mw")` returns non-None |
| 17 | `test_sysml_qn_key_skipped_when_no_owning_part_qn` | (a) | `_computed_attr_index` + `len()` | Rewrite: `registry.resolve("::area")` returns None (no SysML QN key registered for empty owning_part_qn) |

### TestColonColonBindingResolution — 2 tests, all (b)

| # | Test | Category | Internal Access | Migration Action |
|---|------|----------|----------------|-----------------|
| 18 | `test_colon_colon_binding_resolves_to_module_output` | (b) | `_binding_resolutions[key]` | Add `output_registry` param. `::` source_path resolves via `registry.resolve()`. Same outcome. |
| 19 | `test_colon_colon_binding_to_expose_pure_resolves_transitively` | (b) | `_binding_resolutions[key]` | Add `output_registry` param. Transitive resolution now via Phase 4 alias. Same MODULE_OUTPUT outcome. Note: `is_transitive` will change from True to False (documented known change). |

---

## test_backtracker_aggregation.py (20 tests)

### TestAggregationOutputIndex — 7 tests, all (a)

| # | Test | Category | Internal Access | Migration Action |
|---|------|----------|----------------|-----------------|
| 1 | `test_dotted_reference_resolves` | (a) | `_aggregation_output_index` membership | Rewrite: `registry.resolve("solar_array.capital_cost")` returns non-None |
| 2 | `test_bare_reference_resolves` | (a) | `_aggregation_output_index` membership | Rewrite: `registry.resolve("capital_cost")` returns non-None |
| 3 | `test_full_instance_dotted_resolves` | (a) | `_aggregation_output_index` membership | Rewrite: `registry.resolve("Design.plant.solar_array.capital_cost")` returns non-None |
| 4 | `test_channel_name_format` | (a) | `_aggregation_output_index[key]` value | Rewrite: `registry.resolve("solar_array.capital_cost")` returns `"Design__plant__solar_array__capital_cost__capital_cost"` |
| 5 | `test_bare_key_no_collision` | (a) | `_aggregation_output_index` membership + value comparison | Rewrite: `registry.resolve("capital_cost")` returns same channel as `registry.resolve("solar_array.capital_cost")` (first-registered wins) |
| 6 | `test_empty_aggregation_data` | (a) | `_aggregation_output_index == {}` | Rewrite: build registry with no aggregation data, verify resolve returns None |
| 7 | `test_none_aggregation_data` | (a) | `_aggregation_output_index == {}` | Rewrite: same with `aggregation_data=None` |

### TestSystemCalcWiresToAggregation — 5 tests: 3 (b), 2 (c)

| # | Test | Category | Internal Access | Migration Action |
|---|------|----------|----------------|-----------------|
| 8 | `test_dotted_binding_resolves_to_module_output` | (b) | `_binding_resolutions[key]` | Add `output_registry` param. Same MODULE_OUTPUT + channel. |
| 9 | `test_bare_reference_resolves_for_top_level` | (b) | `_binding_resolutions[key]` | Add `output_registry` param. Same MODULE_OUTPUT. |
| 10 | `test_sysml_qn_reference_normalizes` | (b) | `_binding_resolutions[key]` | Add `output_registry` param. `::` normalization now via `registry.resolve()`. Same MODULE_OUTPUT. |
| 11 | `test_trace_log_contains_aggregation_entry` | (c) | `result.trace_log` | Item 4: trace log label may change from `AGGREGATION` to `REGISTRY`. Update expected string. |
| 12 | `test_literal_binding_not_affected` | (c) | `_binding_resolutions[key]` | Minimal — LITERAL fast-path unchanged. Add `output_registry` if required. |

### TestNoAggregationDataGraceful — 2 tests: 1 (a), 1 (c)

| # | Test | Category | Internal Access | Migration Action |
|---|------|----------|----------------|-----------------|
| 13 | `test_none_aggregation_data_works` | (c) | `_binding_resolutions[key]` | Minimal — add `output_registry` if required. Same ENTRY_POINT outcome. |
| 14 | `test_empty_list_aggregation_data_works` | (a) | `_aggregation_output_index == {}` | Rewrite: same as TestAggregationOutputIndex #6 |

### TestAggregationAliasResolution — 6 tests: 5 (a), 1 (b)

| # | Test | Category | Internal Access | Migration Action |
|---|------|----------|----------------|-----------------|
| 15 | `test_alias_in_index_resolves_to_module_output` | (a) | `_aggregation_output_index` membership | Rewrite: `registry.resolve("solar_battery_plant.total_capex")` returns non-None |
| 16 | `test_bare_alias_resolves` | (a) | `_aggregation_output_index` membership | Rewrite: `registry.resolve("total_capex")` returns non-None |
| 17 | `test_alias_channel_matches_original` | (a) | `_aggregation_output_index[key]` value comparison | Rewrite: `registry.resolve("solar_battery_plant.total_capex") == registry.resolve("solar_battery_plant.capital_cost")` |
| 18 | `test_full_dotted_alias_resolves` | (a) | `_aggregation_output_index` membership | Rewrite: `registry.resolve("Design.plant.solar_battery_plant.total_capex")` returns non-None |
| 19 | `test_no_aliases_no_extra_keys` | (a) | `_aggregation_output_index` membership | Rewrite: `registry.resolve("total_capex")` returns None when no aliases |
| 20 | `test_sanitized_partdef_name_in_fallback` | (b) | `_binding_resolutions[key]` | Add `output_registry` param. `::` sanitization now via `registry.resolve()`. Same MODULE_OUTPUT. |

---

## Summary

| Category | Computed Attrs | Aggregation | Total | Migration Effort |
|----------|---------------|-------------|-------|-----------------|
| **(a) Registration** | 11 | 13 | **24** | High — rewrite to use `build_output_registry()` + `registry.resolve()` |
| **(b) Resolution** | 6 | 4 | **10** | Medium — add `output_registry` param, verify same `_binding_resolutions` outcome |
| **(c) Integration** | 2 | 3 | **5** | Low — add `output_registry` param if required, update trace log strings |
| **Total** | **19** | **20** | **39** | |

---

## Migration Plan for Item 4

### Step 1: Create shared test helper for registry construction

Add a `_build_registry_from_test_data()` helper (or reuse `build_output_registry()` directly) that builds an `OutputRegistry` from the same synthetic data the test already constructs. This avoids duplicating factory logic.

```python
def _build_test_registry(
    computed_attributes=None, aggregation_data=None, calc_usages=None,
    calc_defs=None, channel_aliases=None, design_attributes=None,
):
    """Build OutputRegistry from synthetic test data."""
    from sysml_codegen.generation.initialization import build_output_registry
    return build_output_registry(
        calc_usages=calc_usages or [],
        calc_defs=calc_defs or [],
        aggregation_data=aggregation_data or [],
        computed_attributes=computed_attributes or [],
        channel_aliases=channel_aliases or [],
        design_attributes=design_attributes or {},
    )
```

### Step 2: Migrate category (a) tests — Registration (24 tests)

**Action:** Replace `_computed_attr_index` / `_aggregation_output_index` assertions with `registry.resolve()` assertions.

**Pattern:**
```python
# Before (Item 3):
bt = DependencyBacktracker([], [], computed_attributes=[ca])
assert "plant.p_net_kw" in bt._computed_attr_index

# After (Item 4):
registry = _build_test_registry(computed_attributes=[ca])
assert registry.resolve("plant.p_net_kw") is not None
```

**Key considerations:**
- Channel name format tests (#4 in aggregation, #8-9 in computed attrs): assert `registry.resolve(key) == expected_channel` instead of reading from index.
- Collision tests (#5 in aggregation): assert `registry.resolve("capital_cost") == registry.resolve("solar_array.capital_cost")` — first-registered wins behavior preserved by `OutputRegistry.register()`.
- Exclusion tests (#2-4 in computed attrs, #19 in aggregation): assert `registry.resolve(key) is None`.
- `_build_computed_attr_channel()` tests (#8-9): private method will be removed. Test via `registry.resolve()` returning the expected channel string.

**File restructuring:** Consider moving category (a) tests into `tests/unit/test_output_registry_construction.py` alongside existing contract tests, since they now test `build_output_registry()` rather than backtracker internals.

### Step 3: Migrate category (b) tests — Resolution (10 tests)

**Action:** Add `output_registry` param to `DependencyBacktracker` constructor. Assertions on `_binding_resolutions` stay the same — the resolution outcome should be identical.

**Pattern:**
```python
# Before (Item 3):
bt = DependencyBacktracker([usage], [calc_def], computed_attributes=[ca])

# After (Item 4):
registry = _build_test_registry(computed_attributes=[ca], calc_usages=[usage], calc_defs=[calc_def])
bt = DependencyBacktracker([usage], [calc_def], computed_attributes=[ca], output_registry=registry)
```

**Key considerations:**
- `is_transitive` change (test #19 in computed attrs): `test_colon_colon_binding_to_expose_pure_resolves_transitively` currently expects `resolution.is_transitive == True`. After Item 4, transitive resolution happens inside the registry (Phase 4 alias), so `is_transitive` will be `False`. Update assertion.
- All other `_binding_resolutions` assertions (resolution_type, qualified_name, source_path) should be identical.

### Step 4: Migrate category (c) tests — Integration (5 tests)

**Action:** Minimal changes. Add `output_registry` param if the backtracker constructor requires it after Item 4 removes the old indexes.

**Key considerations:**
- Trace log tests (#14 computed attrs, #11 aggregation): The trace log string `"COMPUTED_ATTR"` / `"AGGREGATION"` is produced by the old inline resolution. If Item 4 removes those code paths, these tests need updated expected strings or removal if the new path uses a different logging pattern.
- LITERAL and backward compat tests (#15, #12, #13): Functionally unchanged. LITERAL fast-path runs before any resolution mechanism.

### Step 5: Remove old internal indexes

After all tests are migrated:
1. Remove `_computed_attr_index` construction (backtracker lines 144-155)
2. Remove `_aggregation_output_index` construction (backtracker lines 159-197)
3. Remove `_output_catalog` construction (backtracker lines 225-238) — not tested in these files but used by cascade
4. Remove `_design_attr_binding_index` construction (backtracker lines 241-243) — handled by Phase 4 aliases
5. Remove `_usage_by_name` if `find_required_modules()` no longer needs it (check separately)
6. Remove `_resolve_binding_to_usage()` 7-strategy cascade (lines 776-871)
7. Remove `_build_computed_attr_channel()` private method
8. Remove inline computed_attr/aggregation checks in `_trace_dependencies()` (lines 448-498)
9. Remove `_compare_with_registry()` and 3 insertion points (parallel validation no longer needed)
10. Make `_resolve_binding_via_registry()` the sole resolution path

### Ordering

1. Migrate (a) tests first — validates registry registration covers all key patterns
2. Migrate (b) tests — validates resolution outcomes match
3. Migrate (c) tests — minimal changes
4. Remove old indexes and cascade
5. Run full suite to confirm zero regressions
6. YAML diff against baselines (captured in Phase 1) to confirm identical pipeline output
