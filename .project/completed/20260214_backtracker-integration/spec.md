# Spec: OutputRegistry Construction + Backtracker Integration

**Status:** Complete
**Owner:** Reid Westwood
**Created:** 2026-02-14 00:43 UTC
**Complexity:** HIGH
**Branch:** cost-pattern
**Epic:** `.project/backlog/epic_output_registry_backtracker_redesign.md` (Item 3)

---

## Business Goals

### Why This Matters

Items 1-2b built the OutputRegistry class, ChannelAlias data model, and alias producers (EXPOSE_PURE + CHAIN). But all of that infrastructure is currently dormant -- the pipeline still uses the backtracker's 5 ad-hoc indexes and 7-strategy cascade for binding resolution. This item wires the OutputRegistry into the actual pipeline, proving through parallel validation that the new single-lookup resolution produces identical results to the old cascade. It also fixes Bug 2 (EXPOSE_PURE two-hop failure) via the new resolution path.

Without this item, the foundation code from Items 1-2b has no production impact. With it, the old cascade is validated as replaceable, unblocking Item 4's cut-over (index removal, graph builder simplification, test migration).

### Success Criteria

- [ ] OutputRegistry constructed with 4-phase protocol in `build_pipeline_context()` (new Step 5.5)
- [ ] Parallel validation: zero divergences on all 4 models (solar_battery, attr_expr_probe, chain_spike, sample_model)
- [ ] Bug 2: `financial.total_capex` in e2e_attr_expr resolves to MODULE_OUTPUT via new registry path
- [ ] REFERENCE secondary resolution: 4 computed attribute cases resolve to MODULE_OUTPUT
- [ ] Unresolved bindings produce `logger.warning()` (not silent fallthrough)
- [ ] Contract tests verify registry/backtracker key format agreement
- [ ] Test migration audit complete with migration plan for Item 4
- [ ] Baseline YAML captured for all 4 models (committed fixtures)
- [ ] All existing tests pass (zero regressions)

### Priority

P0 -- on the critical path for the OutputRegistry epic. Blocks Item 4 (cut-over, cleanup, E2E validation). Items 1, 2a, 2b are complete and all gates passed.

---

## Problem Statement

### Current State

- The backtracker builds 5 separate indexes in its constructor (lines 144-243):
  - `_computed_attr_index` (FORMULA computed attrs, 3 key patterns each)
  - `_aggregation_output_index` (aggregation outputs + BF-7 aliases, 3+ key patterns each)
  - `_output_catalog` ("instance.output" -> CalcUsageData, 2 key patterns each)
  - `_design_attr_binding_index` (transitive resolution, "parent.attr" -> target)
  - `_usage_by_name` (instance name -> CalcUsageData, secondary index)
- Resolution uses a 7-strategy cascade in `_resolve_binding_to_usage()` (lines 776-871) with 12+ lookup attempts and format conversions
- CHAIN and REFERENCE bindings also go through inline computed_attr_index and aggregation_output_index checks (lines 448-498) before the cascade
- Bug 2: EXPOSE_PURE `total_capex` two-hop resolution fails because the second hop's key format doesn't match virtual CalcUsage Key_A format
- OutputRegistry (Item 1) and ChannelAlias producers (Item 2a) exist but are not wired into the pipeline
- `PipelineContext.channel_aliases` carries alias data but nothing consumes it yet

### Desired Outcome

- A `build_output_registry()` function constructs the registry with the 4-phase protocol from real pipeline data
- The backtracker accepts an `OutputRegistry` and uses it for a parallel resolution path (`_resolve_binding_via_registry()`)
- Both old cascade and new registry resolution run on every binding, with divergences logged
- Old cascade remains authoritative during Item 3 (new path is shadow/validation only)
- Zero divergences on all 4 models proves the new path is ready to become the sole path in Item 4

---

## Scope

### In Scope

1. **Baseline YAML capture** -- run codegen on all 4 models, commit pipeline YAML as baselines in `tests/fixtures/baseline_yaml/` (standalone preparatory commit before any integration code)

2. **`build_output_registry()` function** in initialization.py (new Step 5.5, between Step 5 and Step 6):
   - Phase 1: Register CalcUsage outputs (Key_A, Key_B, Key_C), aggregation outputs (Key_D, Key_E + alias variants from `agg.expression.aliases` including Step 3.6 param_name aliases), FORMULA outputs (Key_F)
   - Phase 2: Register CHAIN aliases from `PipelineContext.channel_aliases` (source="redefinition")
   - Phase 3: Register EXPOSE_PURE aliases from `PipelineContext.channel_aliases` (source="expose_pure"), scoped with owning part short name
   - Phase 4: Register transitive design attr aliases (filter via `is_transitive_default()`)

3. **Contract tests (TDD, written before implementation)** -- for every binding in test fixtures, verify the key the backtracker constructs for `registry.resolve()` exists in the registry built from the same data

4. **Backtracker refactoring** -- accept optional `OutputRegistry` in constructor:
   - New method `_resolve_binding_via_registry(binding)` implementing CHAIN and REFERENCE resolution via registry
   - New helper `_get_parent_part_for_usage(usage)`: returns `segments[-2]` from qualified_name
   - New helper `_resolve_reference_via_registry(source_path, usage)`: secondary REFERENCE resolution (leaf + parent scope)
   - Self-reference guard adaptation: after resolving to MODULE_OUTPUT channel, check producing usage QN != current usage QN

5. **Parallel validation architecture** -- in `_trace_dependencies()`, call both `_resolve_binding_via_registry()` (new) and the existing inline computed_attr/aggregation/cascade resolution (old) for every binding with a source_path. Compare results. Log divergences with full context. Use old result as authoritative.

6. **Test migration audit** -- identify all 39 tests in `test_backtracker_computed_attrs.py` and `test_backtracker_aggregation.py` that access internal indexes, categorize as (a) registration behavior, (b) resolution behavior, or (c) integration, with migration plan for Item 4

### Out of Scope

- Removing old indexes or cascade (Item 4)
- Graph builder changes (Item 4)
- YAML diff validation against baselines (Item 4 -- we capture baselines here)
- Step 3.6 removal (deferred -- diagnostic found param_name gap; Step 3.6 aliases flow into Phase 1 registration naturally)
- Expression compiler changes (none needed)

### Edge Cases & Considerations

- **Step 3.6 param_name aliases**: These flow naturally into Phase 1 registration via `agg.expression.aliases` (populated by Step 3.6 before the registry is built). No special handling needed -- the same data the old `_aggregation_output_index` reads is available to Phase 1 registration. This ensures parallel validation compares like-for-like.

- **EXPOSE_PURE Phase 3 scoping**: EXPOSE_PURE aliases have bare `alias_name` (e.g., `"total_capex"`). Phase 3 registration must scope them: `f"{owning_part_short}.{alias.alias_name}"` where `owning_part_short = alias.owning_part_qn.split("__")[-1]`. This matches how the old computed_attr_index scoped these (dotted "part.attr" keys).

- **REFERENCE binding secondary resolution**: The old code resolves 4 REFERENCE->MODULE_OUTPUT cases via `_computed_attr_index` (bare-name and dotted-key lookups with `::` normalization). The new path must replicate this via `registry.resolve(f"{parent_part}.{leaf_name}")` where `parent_part = segments[-2]` of the CalcUsage QN. The key format must match what Phase 1 registered for FORMULA outputs (Key_F: `"owning_part.python_name"`).

- **Self-reference guard**: The old guard compares `CalcUsageData` objects (`source_usage.qualified_name == usage.qualified_name`). The new path resolves to a channel name (string), not a CalcUsageData. Guard must extract producing usage QN from channel: `channel.rsplit("__", 1)[0]` gives the usage EQN, then compare with `usage.qualified_name`.

- **`is_transitive` behavioral change**: `is_transitive` on `BindingResolution` will always be `False` for registry-resolved bindings. Phase 4 transitive aliases resolve within the registry, making the chain invisible. This field is not consumed by downstream logic -- only trace logging. Documented as a known behavioral change in parallel validation (divergence in `is_transitive` field is expected and accepted).

- **`_usage_by_name` retention**: Only its use in the cascade (Strategies 2a, 3) is replaced. `find_required_modules()` still uses it for target resolution. Mark for future cleanup.

- **Parallel validation scope**: Compare `resolution_type` and `qualified_name` fields of `BindingResolution`. The `is_transitive` field is expected to diverge (always `False` in new path) and should be excluded from divergence comparison.

---

## Requirements

### Functional Requirements

> Requirements below are from the epic Item 3 definition unless marked [INFERRED].

1. **FR-1**: A `build_output_registry()` function MUST be added to `initialization.py` implementing the 4-phase registration protocol. It MUST accept `calc_usages`, `calc_defs`, `aggregation_data`, `computed_attributes`, `channel_aliases`, and `design_attributes` as inputs and return an `OutputRegistry`.

2. **FR-2**: Phase 1 MUST register CalcUsage outputs with Key_A (`instance_name.output`), Key_B (EQN channel name via `get_channel_name()`), and Key_C (dotted hierarchy via `OutputRegistry.derive_key_c()`).

3. **FR-3**: Phase 1 MUST register aggregation outputs with Key_D (`part_usage.attr`), Key_E (full dotted instance path), and alias variants from `agg.expression.aliases` (including Step 3.6 param_name aliases). This mirrors the existing `_aggregation_output_index` construction (backtracker lines 157-197).

4. **FR-4**: Phase 1 MUST register FORMULA computed attribute outputs with Key_F (`owning_part.python_name`), plus bare-name and SysML QN keys matching the existing `_computed_attr_index` construction (backtracker lines 144-155).

5. **FR-5**: Phase 2 MUST register CHAIN aliases from `channel_aliases` where `source="redefinition"`. Each alias's `canonical_name` is resolved against the registry (Phase 1 entries) via `registry.resolve()`.

6. **FR-6**: Phase 3 MUST register EXPOSE_PURE aliases from `channel_aliases` where `source="expose_pure"`. Alias keys MUST be scoped: `f"{owning_part_qn.split('__')[-1]}.{alias.alias_name}"`. Canonical names resolved against Phase 1+2 entries.

7. **FR-7**: Phase 4 MUST register transitive design attribute aliases. Filter candidates via `is_transitive_default(attr.default_value)`. Key: `f"{attr.parent_part}.{attr.name}"`. Canonical: `registry.resolve(attr.default_value)`.

8. **FR-8**: `DependencyBacktracker.__init__()` MUST accept an optional `output_registry: OutputRegistry | None = None` parameter. When provided, parallel validation is enabled.

9. **FR-9**: A `_resolve_binding_via_registry()` method MUST implement CHAIN resolution: `registry.resolve(source_path)` -> MODULE_OUTPUT, or fall through to ENTRY_POINT. REFERENCE resolution: exact match, then secondary resolution (leaf + parent scope), then `_resolve_to_design_attribute()`, then ENTRY_POINT with warning.

10. **FR-10**: [INFERRED] `_get_parent_part_for_usage(usage)` MUST return `usage.qualified_name.split("__")[-2]` -- the parent part name needed for REFERENCE secondary resolution.

11. **FR-11**: Parallel validation MUST run both old and new resolution for every binding when `output_registry` is provided. Divergences in `resolution_type` or `qualified_name` MUST be logged as warnings with full context (binding source_path, old result, new result). The `is_transitive` field is excluded from comparison. Old result is authoritative.

12. **FR-12**: [INFERRED] Unresolved bindings in the new registry path MUST produce `logger.warning()` messages (not silent fallthrough to ENTRY_POINT).

13. **FR-13**: Baseline pipeline YAML MUST be captured for all 4 models (solar_battery, attr_expr_probe, chain_spike, sample_model) and committed to `tests/fixtures/baseline_yaml/` before any integration code.

14. **FR-14**: [INFERRED] The `build_output_registry()` call MUST be placed as Step 5.5 in `build_pipeline_context()` -- after Step 5 (parameter group deriver) and before Step 6 (backtracker creation), because it needs `computed_attrs` from Step 4.5 and `scoped_agg_data` from Step 3.5, and the backtracker needs the registry.

---

## Acceptance Criteria

### Baseline YAML Capture
- [ ] Pipeline YAML committed to `tests/fixtures/baseline_yaml/` for all 4 models
- [ ] Committed as standalone preparatory commit before integration code

### OutputRegistry Construction
- [ ] `build_output_registry()` function exists in `initialization.py`
- [ ] Phase 1: CalcUsage outputs registered with Key_A, Key_B, Key_C
- [ ] Phase 1: Aggregation outputs registered with Key_D, Key_E, alias variants (including Step 3.6 param_name aliases)
- [ ] Phase 1: FORMULA outputs registered with Key_F, bare-name, SysML QN keys
- [ ] Phase 2: CHAIN aliases registered (41 on solar_battery, matching Item 2a count)
- [ ] Phase 3: EXPOSE_PURE aliases registered with scoped keys
- [ ] Phase 4: Transitive design attr aliases registered (2 across all models per Spike 7)
- [ ] Registry passed to `DependencyBacktracker` constructor

### Contract Tests
- [ ] For every binding in test fixtures, the key the backtracker constructs exists in the registry built from the same data
- [ ] Contract tests written BEFORE implementation (TDD sequence)

### Parallel Validation
- [ ] Zero divergences on solar_battery (all bindings)
- [ ] Zero divergences on e2e_attr_expr/attr_expr_probe (all bindings)
- [ ] Zero divergences on chain_spike (all bindings)
- [ ] Zero divergences on sample_model (all bindings)
- [ ] Bug 2: `financial.total_capex` resolves to MODULE_OUTPUT via new registry path
- [ ] REFERENCE secondary resolution: 4 computed attribute cases resolve to MODULE_OUTPUT (solar_battery: `p_net_kw`, `capital_cost`; e2e_attr_expr: `power_mw`, `annual_om`)
- [ ] Divergences logged with full context (binding, old result type+channel, new result type+channel)
- [ ] `is_transitive` divergences excluded from comparison (documented known change)

### Backtracker Integration
- [ ] `DependencyBacktracker` accepts optional `output_registry` parameter
- [ ] `_resolve_binding_via_registry()` method exists
- [ ] `_get_parent_part_for_usage()` returns `segments[-2]`
- [ ] Self-reference guard works with channel-name-based resolution
- [ ] Unresolved bindings in new path produce `logger.warning()`

### Test Migration Audit
- [ ] All 39 tests in `test_backtracker_computed_attrs.py` (19) and `test_backtracker_aggregation.py` (20) audited
- [ ] Each test categorized: (a) registration behavior, (b) resolution behavior, (c) integration
- [ ] Migration plan documented for Item 4

### Quality & Integration
- [ ] `uv run pytest tests/` passes (zero regressions)
- [ ] `uv run mypy src/` passes (no new type errors)
- [ ] Bug 2 xfail test (`test_bug2_regression.py`) passes via new registry path (but xfail NOT yet removed -- that's Item 4, when old path is removed and new path becomes authoritative)

---

## Implementation Notes

### Resolution Flow Mapping (Old -> New)

The current backtracker `_trace_dependencies()` resolves bindings in this order (lines 448-601):

1. **Check computed_attr_index** (lines 448-469): exact match, dotted bare fallback, `::` bare fallback -> MODULE_OUTPUT
2. **Check aggregation_output_index** (lines 471-498): exact match, dotted bare fallback, `::` sanitized fallback -> MODULE_OUTPUT
3. **Call `_resolve_binding_to_usage()`** (line 500): 7-strategy cascade -> CalcUsageData or None
4. **Self-reference guard** (lines 502-511): if resolved usage == current usage, treat as None
5. **If resolved**: build channel name -> MODULE_OUTPUT (lines 513-538)
6. **If not resolved**: `_resolve_to_design_attribute()` -> ENTRY_POINT (lines 539-601)

The new `_resolve_binding_via_registry()` consolidates steps 1-3 into:

1. **`registry.resolve(source_path)`** -> if found, MODULE_OUTPUT with returned channel
2. **REFERENCE secondary resolution** (if step 1 returns None and binding is REFERENCE):
   - Extract leaf from source_path (last `::` or `.` segment)
   - Get parent part: `_get_parent_part_for_usage(usage)` = `segments[-2]`
   - Try `registry.resolve(f"{parent_part}.{leaf}")` -> MODULE_OUTPUT
3. **`_resolve_to_design_attribute()`** -> ENTRY_POINT (existing method, unchanged)
4. **Fallback**: ENTRY_POINT with warning

### Key Format Matching Between Old Indexes and New Registry

| Old Index | Old Key Pattern | New Registry Phase | New Key Format | Match? |
|-----------|----------------|-------------------|----------------|--------|
| `_computed_attr_index` | `"part.attr"` | Phase 1 (Key_F) | `"owning_part.python_name"` | Same |
| `_computed_attr_index` | `"attr"` (bare) | Phase 1 (Key_F) | bare `python_name` | Same |
| `_computed_attr_index` | `"QN::attr"` (SysML) | Phase 1 (Key_F) | SysML QN key | Same |
| `_aggregation_output_index` | `"part.attr"` (Key_D) | Phase 1 (Key_D) | `"part_usage.attr"` | Same |
| `_aggregation_output_index` | `"attr"` (bare) | Phase 1 | bare `attr_name` | Same |
| `_aggregation_output_index` | full dotted (Key_E) | Phase 1 (Key_E) | full dotted instance | Same |
| `_aggregation_output_index` | alias variants | Phase 1 | alias + instance variants | Same |
| `_output_catalog` | `"instance.output"` | Phase 1 (Key_A) | `"instance_name.output"` | Same |
| `_output_catalog` | EQN key | Phase 1 (Key_B) | `get_channel_name()` | Same |
| N/A (Bug 2 gap) | N/A | Phase 1 (Key_C) | dotted hierarchy | **NEW** |
| `_design_attr_binding_index` | `"parent.attr"` | Phase 4 | transitive alias | Same |

### Where `build_output_registry()` Fits in the Pipeline

```
Step 3.5:  Hierarchy + rewrite + scoping + CHAIN aliases
Step 3.6:  Enrich aggregation aliases (retained — feeds Phase 1)
Step 4:    Design attributes
Step 4.5:  Computed attributes + EXPOSE_PURE aliases
Step 5:    Parameter group deriver
Step 5.5:  build_output_registry()  <-- NEW
Step 6:    Backtracker (now receives OutputRegistry)
Step 6.5:  Compile expressions
Step 7:    Build computation graph
```

Step 5.5 needs: `calc_usages`, `calc_defs`, `scoped_agg_data` (Step 3.5), `computed_attrs` (Step 4.5), `channel_aliases` (Steps 3.5 + 4.5), `design_attrs` (Step 4).

### Parallel Validation Architecture

```python
# In _trace_dependencies(), after processing binding source_path:
if self._output_registry is not None and binding.source_path:
    new_resolution = self._resolve_binding_via_registry(binding, usage)
    old_resolution = <result from existing inline resolution above>

    if new_resolution.resolution_type != old_resolution.resolution_type or \
       new_resolution.qualified_name != old_resolution.qualified_name:
        logger.warning(
            "PARALLEL DIVERGENCE: %s|%s: old=%s/%s new=%s/%s",
            usage.qualified_name, binding.param_name,
            old_resolution.resolution_type, old_resolution.qualified_name,
            new_resolution.resolution_type, new_resolution.qualified_name,
        )
```

Old result is authoritative -- `_binding_resolutions[mapping_key]` always gets the old result during Item 3.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_output_registry_backtracker_redesign.md`
- **Design basis:** `.project/reports/08_algorithm_revised.md` (Sections 12, 14)
- **Item 1 code:** `src/sysml_codegen/core/output_registry.py`, `src/sysml_codegen/core/models.py`
- **Item 2 code:** `src/sysml_codegen/extraction/computed_attribute_extractor.py`, `src/sysml_codegen/generation/initialization.py`
- **Item 1 tests:** `tests/unit/test_output_registry.py`, `tests/integration/test_output_registry_smoke.py`
- **Bug 2 xfail:** `tests/integration/test_bug2_regression.py`
- **Step 3.6 diagnostic:** `tests/integration/test_step36_diagnostic.py`
- **Spike references:** Spike 5 (119 REFERENCE->ENTRY_POINT, 4 REFERENCE->MODULE_OUTPUT), Spike 7 (2 transitive defaults), Spike 8 (key format contract, segments[-2] validated)

---

## Deliverables

| File | Type | Description |
|------|------|-------------|
| `tests/fixtures/baseline_yaml/` | New | Baseline pipeline YAML for 4 models |
| `src/sysml_codegen/generation/initialization.py` | Modified | `build_output_registry()` + Step 5.5 wiring |
| `src/sysml_codegen/analysis/dependency_backtracker.py` | Modified | `output_registry` param, parallel validation, `_resolve_binding_via_registry()` |
| `tests/unit/test_output_registry_construction.py` | New | Contract tests + `build_output_registry()` unit tests |
| `tests/integration/test_parallel_validation.py` | New | Parallel validation on all 4 models |
| `.project/active/backtracker-integration/test_migration_audit.md` | New | Audit of 39 tests with migration plan |

---

**Next Steps:** After approval, proceed to `/_my_design`
