# Epic: OutputRegistry Backtracker Redesign

**Epic ID**: OUTPUT-REGISTRY
**Status**: In Progress
**Priority**: P0
**Created**: 2026-02-13
**Estimated Effort**: 6-6.5 days

---

## Executive Summary

Replace the backtracker's 5 ad-hoc indexes and 7-strategy cascade with a single `OutputRegistry` that resolves any CHAIN binding source_path to a canonical channel name via exact match. This eliminates the root cause of Bug 2 (EXPOSE_PURE two-hop failure) and a class of key-format-mismatch bugs that have plagued the COST-PATTERN implementation.

**Critical Success Factor**: Every binding that currently resolves to MODULE_OUTPUT in the existing backtracker also resolves to MODULE_OUTPUT through the new OutputRegistry-backed backtracker, with zero regressions and Bug 2 fixed.

---

## Why This Epic?

**Current State**:
- The backtracker builds 5 separate indexes (`_computed_attr_index`, `_aggregation_output_index`, `_output_catalog`, `_design_attr_binding_index`, `_usage_by_name`) with incompatible key formats
- A 7-strategy cascade tries 12+ lookup attempts with 4+ format conversions to bridge the gaps (~200 lines of code)
- Bug 2 (EXPOSE_PURE two-hop failure) causes `financial.total_capex` to wire to ENTRY_POINT instead of MODULE_OUTPUT in e2e_attr_expr
- Step 3.6 (alias enrichment) is a heuristic patch deriving aliases from CalcUsage param_name divergence -- semantically wrong
- Every new module family (computed attrs, aggregation) required its own index + cascade modifications, creating new bugs
- Failures are **silent** -- unresolved CHAIN bindings fall through to ENTRY_POINT with no diagnostic

**Future State**:
- Single `OutputRegistry` with exact-match resolve replaces all 5 indexes
- EXPOSE_PURE attributes produce `ChannelAlias` objects (not module index entries), directly fixing Bug 2
- Aliases are first-class data models with explicit provenance tracking
- 4-phase registration protocol with ordered dependencies -- each phase resolves against prior phases
- CHAIN bindings resolve via `registry.resolve(source_path)` -- one call, no cascade
- REFERENCE bindings resolve via structured secondary resolution (leaf-name + parent-scope)
- Unresolved bindings emit warnings, not silent fallthrough

**Design basis**: `.project/reports/08_algorithm_revised.md` (3 iterations of review, 9 spikes, 22 issues all closed with empirical data from 215+ bindings across 4 models)

---

## Success Criteria

- [ ] OutputRegistry resolves all CHAIN binding source_paths that currently resolve to MODULE_OUTPUT (zero regressions, verified by parallel validation)
- [ ] Bug 2 is fixed: `financial.total_capex` in e2e_attr_expr resolves to MODULE_OUTPUT (not ENTRY_POINT)
- [ ] Issue 22 REFERENCE->aggregation case resolves to MODULE_OUTPUT (currently a false ENTRY_POINT)
- [ ] All existing tests pass (zero regressions across full test suite)
- [ ] Unresolved bindings produce warnings in the log (not silent fallthrough)
- [ ] Steps 3.6 and 4.7 eliminated as separate pipeline steps
- [ ] No bare-name registration or SYSML_QN normalization in the OutputRegistry (confirmed unnecessary by Spikes 1, 4, 5)

---

## Testing Approach

Tests are organized into two tiers with clear boundaries:

**Unit Tests** (synthetic data, fast, test one class/function):
- Use factory functions that produce representative `CalcUsageData`, `ScopedAggregationData`, `ComputedAttributeData`, and `ChannelAlias` objects (hardcoded from spike results, no SysIDE loading)
- Test `OutputRegistry` registration, collision handling, resolution, and phase ordering (Item 1)
- Test EXPOSE_PURE and CHAIN alias filtering logic with synthetic inputs (Item 2a)
- Test `_rewrite_virtual_bindings()` leaf extraction with synthetic bindings (Item 2b)
- Test contract: for every binding in fixtures, the key format the backtracker constructs matches what the registry contains (Item 3)
- **Negative tests** for OutputRegistry: verify `resolve()` returns `None` for keys that should NOT match (bare names, SYSML_QN paths) -- validates the "no normalization" contract (Item 1)
- **Collision logging test**: verify that when a Key_A collision occurs (e.g., `cost_model.total_cost` from 9 virtual CalcUsages), exactly one warning is logged and the first registration wins (Item 1)
- **Phase isolation test**: verify that Phase 2 alias registration fails if Phase 1 hasn't run (canonical channel doesn't exist) (Item 1)
- Location: `tests/unit/`

**Integration Tests** (real models, full pipeline, slow):
- Load models through SysIDE adapter and run the full pipeline
- **Parallel validation** (Item 3): Run both old cascade and new OutputRegistry resolution on 4 models (solar_battery, e2e_attr_expr, chain_spike, sample_model), assert zero divergences in `binding_resolutions`
- **E2E validation** (Item 4): Full codegen on all 4 models + Issue 22 fixture, verify pipeline YAML correctness
- **E2E YAML diff test** (Item 4): Diff generated pipeline YAML against known-good baselines for each model -- catches subtle wiring changes that might not show up in binding resolution comparisons
- These tests require the `agentic-mbse` dependency and SysIDE adapter
- Location: `tests/integration/`

**Model files**: Real models live in `tests/fixtures/` (e.g., `tests/fixtures/issue22_model/`). Pre-extracted fixture data (for unit tests) is created as factory functions in test files or `tests/conftest_output_registry.py`.

---

## Logical and Functional Changes

This section identifies every logical change between the current implementation and the target design. Cross-reference: `08_algorithm_revised.md` Appendix A (Desired-State Step Index).

### Change 1: New `ChannelAlias` data model

**What**: A first-class dataclass representing an explicit alias for a pipeline output channel.

**Where**: `core/models.py` (new dataclass). **Note**: Most data models live in `extraction/data_models.py`, but `ChannelAlias` is consumed by the core `OutputRegistry` and is a pipeline-level concept, so `core/models.py` is the deliberate choice.

**Interface**:
```python
@dataclass
class ChannelAlias:
    alias_name: str          # scoped dotted key (e.g., "solar_array.total_capex")
    canonical_name: str      # scoped dotted key of the target (e.g., "solar_array.cost_model.total_cost")
    owning_part_qn: str      # qualified name of the PartDef/PartUsage where the alias originates
    source: str              # provenance: "redefinition" | "expose_pure" | "design_override"
```

**Replaces**: `list[str]` aliases on `AggregationExpressionData` + heuristic param_name scan in Step 3.6.

### Change 2: New `OutputRegistry` class

**What**: Single lookup data structure that maps dotted binding source_paths to canonical channel names (PQN format). Replaces the 5 ad-hoc backtracker indexes.

**Where**: `core/output_registry.py` (new file)

**Interface**:
```python
class OutputRegistry:
    def register(self, canonical_channel: str, lookup_keys: list[str]) -> None
    def register_alias(self, alias: str, canonical_channel: str) -> None
    def resolve(self, source_path: str) -> str | None  # exact match only
```

**Key format contract** (from Spike 8):
- Phase 1 CalcUsage: Key_A (`instance.output`), Key_B (EQN), Key_C (dotted hierarchy path -- REQUIRED for Phase 2 resolution)
- Phase 1 Aggregation: Key_D (`part_usage.attr`), Key_E (full dotted with prefix)
- Phase 1 FORMULA: Key_F (`owning_part.python_name`)
- Phase 2: CHAIN aliases (resolve against Key_C)
- Phase 3: EXPOSE_PURE aliases (resolve against Key_A, PartUsage-only)
- Phase 4: Transitive design attr aliases (resolve against Phase 1-3)

**Collision policy**: Refuse overwrite on collision (log warning, keep first registration).

### Change 3: EXPOSE_PURE produces `ChannelAlias` instead of module index entries

**What**: EXPOSE_PURE computed attributes produce `ChannelAlias` objects. They no longer enter `_computed_attr_index`. They do NOT generate modules.

**Where**: `extraction/computed_attribute_extractor.py` (Step 4.5)

**Critical details** (from Spikes 3, 8):
- Canonical name MUST use `references` field: `f"{references[1].name}.{references[0].name}"`. DO NOT use `expression_text` (SysIDE produces `".(component_cost)"`, not a parseable dotted key).
- Filter out PartDef-level EXPOSE_PURE (canonical names are unscoped, can't resolve against instance-scoped registry keys).
- Alias keys are scoped: `f"{owning_part_short_name}.{python_name}"` where `owning_part_short_name = owning_part_qn.split("__")[-1]`.

**Fixes**: Bug 2 -- the current code builds a channel name for a nonexistent module.

### Change 4: `:>>` CHAIN redefinitions produce `ChannelAlias`

**What**: `:>>` CHAIN redefinitions create scoped `ChannelAlias` objects in Step 3.5.

**Where**: `extraction/hierarchy_resolver.py` + `generation/initialization.py` (Step 3.5D)

**Critical details** (from Spike 6):
- Filter BARE non-reference values: `if "." not in redef.source_path: continue` (24% of CHAIN redefs are CAS codes like `CAS220101`, not channel references).
- Scope both alias_name and canonical_name with instance_path prefix: `f"{instance_path}.{redef.attribute_name}"` / `f"{instance_path}.{redef.source_path}"`.
- `instance_path` derivation: strip design PartDef prefix from `ScopedAggregationData.instance_path`, replace `__` with `.` (Spike 8: `".".join(instance_path.split("__")[1:])`).

### Change 5: CHAIN override support in virtual binding rewrite

**What**: Step 3.5E currently only handles LITERAL overrides. Target handles both LITERAL and CHAIN overrides, and extracts leaf names from SYSML_QN and DOTTED formats (not just bare names).

**Where**: `generation/initialization.py` (`_rewrite_virtual_bindings`)

**Critical details** (from Spike 1):
- Leaf extraction from SYSML_QN: `source_path.rsplit("::", 1)[-1]`
- Leaf extraction from DOTTED: `source_path.rsplit(".", 1)[-1]`
- Bare names never observed (94 bindings, 3 models) but defensive fallback kept.
- CHAIN override: rewrite `binding.source_path = matched.source_path`.

### Change 6: Aggregation scoping consolidation

**What**: Step 4.7 (`_scope_aggregation_expressions()`) moves into Step 3.5 as a sub-step. Step 5 only registers already-scoped results.

**Where**: `generation/initialization.py`

**Rationale**: Scoping depends on hierarchy extraction results (from Step 3.5), not on the OutputRegistry.

### Change 7: Step 3.6 elimination

**What**: `_enrich_aliases_from_bindings()` is removed entirely.

**Where**: `generation/initialization.py`

**Rationale**: The heuristic (param_name != source_leaf -> alias) is semantically wrong. Aliases now come exclusively from authoritative sources: `:>>` CHAIN redefs (Change 4) and EXPOSE_PURE classification (Change 3).

### Change 8: OutputRegistry construction in `build_pipeline_context()`

**What**: New Step 5 in the initialization pipeline. Builds the OutputRegistry with the 4-phase registration protocol from Section 12 of the design.

**Where**: `generation/initialization.py`

**Critical details**:
- Phase 1: Register CalcUsage outputs (Key_A, Key_B, **Key_C**), aggregation outputs (Key_D, Key_E + alias variants), FORMULA outputs (Key_F).
- Phase 2: Register CHAIN aliases (resolve canonical_name against Phase 1).
- Phase 3: Register EXPOSE_PURE aliases (PartUsage only, resolve against Phase 1+2).
- Phase 4: Register transitive design attr aliases (PartUsage only, filter via `_is_transitive_default()`).
- The `_is_transitive_default()` filter: `"." in str(val)` and `float(str(val))` raises `ValueError` (try/except required -- see Item 1 spec). Spike 7: 2 transitive defaults, both resolve.

### Change 9: Backtracker refactoring

**What**: Replace the 5 internal indexes + 7-strategy cascade with OutputRegistry-backed resolution.

**Where**: `analysis/dependency_backtracker.py`

**New resolution flow**:
- **CHAIN bindings**: `registry.resolve(source_path)` -> MODULE_OUTPUT or design_attr fallback -> ENTRY_POINT.
- **REFERENCE bindings**: exact match (rare) -> secondary resolution (leaf-name + `segments[-2]` scoped resolve) -> `_resolve_to_design_attribute()` -> ENTRY_POINT with warning.
- **LITERAL/UNBOUND**: Always ENTRY_POINT (unchanged).

**New methods**:
- `_get_parent_part_for_usage(usage)`: Returns `usage.qualified_name.split("__")[-2]` (Spike 8: validated against all 4 REFERENCE->MODULE_OUTPUT cases).
- `_resolve_to_design_attribute(source_path)`: Extract leaf from SYSML_QN or DOTTED, search design_attrs by `(parent_path, leaf_name)` match, return literal-valued attrs only (Spike 5: 119 REFERENCE->ENTRY_POINT cases).
- `_find_usage_for_channel(channel)`: Extract producing CalcUsage QN from channel name (`channel.rsplit("__", 1)`). Used for self-reference guard and DFS traversal.

**Self-reference guard adaptation**: The current guard (lines 502-505) compares resolved `CalcUsageData` objects. In the new design, CHAIN resolution returns a channel name (string), not a `CalcUsageData`. After resolving to MODULE_OUTPUT, the guard must check `_find_usage_for_channel(channel).qualified_name == usage.qualified_name`. Spec 06 Section 14.4 specifies this.

**`is_transitive` behavioral change**: `is_transitive` on `BindingResolution` will always be `False` in the new implementation. Phase 4 transitive aliases resolve within the OutputRegistry, making the chain invisible to the backtracker. This field is not consumed by downstream logic (graph builder, generation) -- only trace logging. Documented as a known behavioral change.

**Removes**: `_computed_attr_index`, `_aggregation_output_index`, `_output_catalog`, `_design_attr_binding_index`, and the 7-strategy cascade in `_resolve_binding_to_usage()`. **`_usage_by_name` is retained** for `find_required_modules()` target resolution (e.g., `find_required_modules(["net_electric.p_net"])`). Only its use in `_resolve_binding_to_usage()` (Strategies 2a, 3) is removed. Mark for future cleanup when `find_required_modules()` is updated to use `_usage_by_qualified`. Spec 06 Section 14.1 documents this retention.

### Change 10: Graph builder simplification

**What**: Graph builder no longer builds its own output catalog. It consumes `binding_resolutions` from the backtracker (already the case) and `ScopedAggregationData` for aggregation modules.

**Where**: `resolution/graph_builder.py`

**Rationale**: Output catalog construction is now the OutputRegistry's responsibility (Step 5). The graph builder is a pure consumer.

**Interface note**: The graph builder's channel reference validation currently needs `(module_type, channel_name, field_name)` tuples. The OutputRegistry provides channel existence checks via `resolve()`. The `field_name` extraction (typically the last `__`-separated segment of the channel name) can be derived inline. The `module_type` can be derived from the CalcDef map. Specify the exact interface during Item 4 implementation.

---

## Backlog Items

### Item 1: OutputRegistry Foundation [~1 day]

**Type**: Implementation

**Objective**: Create the `ChannelAlias` data model and `OutputRegistry` class with comprehensive unit tests that verify the key format contract and 4-phase registration protocol.

**Current State**:
- `ChannelAlias` does not exist
- `OutputRegistry` does not exist
- Alias representation is `list[str]` on `AggregationExpressionData`

**Scope**:
1. **`ChannelAlias` dataclass** in `core/models.py`:
   - Fields: `alias_name`, `canonical_name`, `owning_part_qn`, `source`
   - Interface contract: all fields are scoped dotted keys (no bare names, no SYSML_QN)
2. **`OutputRegistry` class** in `core/output_registry.py`:
   - `register(canonical_channel, lookup_keys)`: Register channel with multiple lookup keys. Refuse overwrite on collision (log warning).
   - `register_alias(alias, canonical_channel)`: Register alias to existing canonical channel. Assert canonical exists.
   - `resolve(source_path) -> str | None`: Exact match only. No normalization.
   - Key_C derivation utility: `".".join(qn.split("__")[1:]) + "." + output_name`
   - `_is_transitive_default(attr)` filter: `"." in str(default_value)` and `float(str(default_value))` raises `ValueError` (i.e., it's a dotted path like `"cost_model.total_cost"`, not a numeric like `"3.14"`). Implementation requires try/except around `float()`:
     ```python
     def _is_transitive_default(attr):
         val = str(attr.default_value)
         if "." not in val:
             return False
         try:
             float(val)
             return False  # numeric like "3.14"
         except (ValueError, TypeError):
             return True   # dotted path
     ```

**Out of Scope**:
- Wiring the OutputRegistry into the pipeline (Item 3)
- Modifying existing extractors (Item 2)
- SYSML_QN normalization (proven broken by Spike 5 -- not implemented)
- Bare-name registration (proven unnecessary by Spike 4 -- not implemented)

**Success Criteria**:
- [x] `ChannelAlias` dataclass exists with all fields
- [x] `OutputRegistry.register()` correctly indexes multiple keys per channel
- [x] `OutputRegistry.register()` refuses to overwrite on collision (logs warning, returns first)
- [x] `OutputRegistry.register_alias()` asserts canonical channel exists
- [x] `OutputRegistry.resolve()` returns exact match or `None`
- [x] Phase ordering test: Phase 2 alias resolves only after Phase 1 canonical is registered
- [x] Phase ordering test: Phase 3 alias resolves against Phase 1+2
- [x] Phase ordering test: Phase 4 alias resolves against Phase 1-3
- [x] Key format tests using Spike 8 data:
  - Key_A (dotted short) resolves for concrete CalcUsage outputs
  - Key_B (EQN) resolves for all CalcUsage outputs
  - Key_C (dotted hierarchy) resolves for virtual CalcUsage outputs
  - Key_D (part_usage.attr) resolves for aggregation outputs
  - Key_F (owning_part.attr) resolves for FORMULA outputs
- [x] Collision test: two CalcUsages with same `total_cost` output -- Key_A collision logged, first wins
- [x] `is_transitive_default()` correctly identifies dotted-path defaults and rejects numeric/None defaults
- [x] **Negative tests**: `resolve()` returns `None` for bare names (`total_cost`), SYSML_QN paths (`Namespace::Part::calc`), and unregistered keys -- validates "no normalization" contract
- [x] **Collision logging test**: When Key_A collision occurs (e.g., `cost_model.total_cost` from 9 virtual CalcUsages), exactly one warning is logged and first registration wins
- [x] **Phase isolation test**: Phase 2 `register_alias()` fails/warns if the canonical channel hasn't been registered in Phase 1
- [x] **Bug 2 xfail regression test (written BEFORE implementation)**: A separate failing integration test that exposes Bug 2 (EXPOSE_PURE `financial.total_capex` resolves to ENTRY_POINT instead of MODULE_OUTPUT). Marked `@pytest.mark.xfail(reason="Bug 2: EXPOSE_PURE two-hop failure")`. When Item 3 completes, the `xfail` is removed and the test goes green. This is the definitive proof the fix works.
  ```python
  @pytest.mark.xfail(reason="Bug 2: EXPOSE_PURE two-hop failure")
  def test_bug2_expose_pure_total_capex_currently_fails():
      """EXPOSE_PURE financial.total_capex should be MODULE_OUTPUT but is ENTRY_POINT."""
  ```

**Test Fixtures** (from Spike 8 data):

Create factory functions in the test file (or `tests/conftest_output_registry.py`) that produce representative data objects for unit testing. These are synthetic, fast, and test one class/function:
- 1 concrete `CalcUsageData` with 2 outputs (validates Key_A, Key_B, Key_C registration)
- 1 virtual `CalcUsageData` with 1 output (validates Key_C critical path for Phase 2 CHAIN alias resolution)
- 1 `ScopedAggregationData` with 1 alias (validates Key_D, Key_E + alias variant registration)
- 1 FORMULA `ComputedAttributeData` (validates Key_F registration)

These fixtures ground the unit tests in real spike data without requiring SysIDE model loading.

**Estimated Effort**: 1 day (spec 1h, design 1h, plan 0.5h, execute 5h)

**Location**: `.project/active/output-registry-foundation/`

**Dependencies**: None

**Deliverables**:
- `src/sysml_codegen/core/output_registry.py` (new file)
- `src/sysml_codegen/core/models.py` (ChannelAlias addition)
- `tests/unit/test_output_registry.py` (new file, comprehensive unit tests)

**Smoke Test (real model data)**: Build an `OutputRegistry` from real `solar_battery` extracted data (loaded via SysIDE), verify `resolve()` returns non-`None` for a known CHAIN binding `source_path`. This catches failures where synthetic fixtures pass but real data diverges.

**Reference spikes**: Spike 4 (zero bare names), Spike 5 (SYSML_QN broken), Spike 8 (key format contract, zero collisions across 250 keys)

---

### Item 2a: ChannelAlias Producers [~1 day]

**Type**: Implementation

**Objective**: Modify the computed attribute extractor and hierarchy resolver to produce `ChannelAlias` objects. Add `is_on_part_definition` to `ComputedAttributeData`. Extract `find_instance_paths_for_partdef()` as a shared utility.

**Current State**:
- EXPOSE_PURE attrs go into `_computed_attr_index` alongside FORMULA attrs (Bug 2 root cause)
- `:>>` CHAIN redefs partially produce aliases on `AggregationExpressionData.aliases`
- `ComputedAttributeData` has `owning_part_name` and `owning_part_qualified_name` but no `is_on_part_definition` boolean
- `find_instance_paths_for_partdef()` does not exist as a reusable function; similar logic is inlined in `_scope_aggregation_expressions()` in initialization.py

**Scope**:
1. **Add `is_on_part_definition: bool` to `ComputedAttributeData`** (extraction/data_models.py):
   - Populated at extraction time from SysIDE AST (whether owning part is a PartDefinition vs. PartUsage)
   - **Detection mechanism**: `is_on_part_definition = SysideAdapter.is_instance(owning_element, "PartDefinition")` during the `_scan_part_members()` extraction loop in `computed_attribute_extractor.py` (lines 110-234). The owning element is already available in the loop context.
   - Used by Step 4.5 EXPOSE_PURE filter (Change 3)
2. **Extract `find_instance_paths_for_partdef()`** as a shared utility:
   - Derives dotted instance paths from virtual CalcUsage parent QNs (logic currently inlined in `_scope_aggregation_expressions()`)
   - Returns design-prefix-stripped, dot-separated instance paths
   - Used by CHAIN alias construction (Change 4)
3. **EXPOSE_PURE -> ChannelAlias** (Change 3):
   - Modify `computed_attribute_extractor.py`: EXPOSE_PURE produces `ChannelAlias`, not index entries
   - Use `references` field for canonical_name construction (NOT `expression_text`)
   - Filter PartDef-level EXPOSE_PURE using `ca.is_on_part_definition`
   - Scope alias keys with `owning_part_qn.split("__")[-1]`
   - Interface: `extract_and_classify_computed_attributes()` returns `(list[ComputedAttributeData], list[ChannelAlias])`
4. **CHAIN redef -> ChannelAlias** (Change 4):
   - Modify hierarchy_resolver.py or initialization.py: produce `ChannelAlias` from CHAIN redefs
   - Filter: skip if `"." not in redef.source_path` (BARE CAS codes)
   - Scope: prefix both alias_name and canonical_name with instance_path (dotted, prefix-stripped) via `find_instance_paths_for_partdef()`
   - Interface: Step 3.5 returns `list[ChannelAlias]` alongside `HierarchyExtractionResult`

**Out of Scope**:
- Building the OutputRegistry (Item 3)
- Virtual binding rewrite changes (Item 2b)
- Step consolidation (Item 2b)
- Expression compiler changes (none needed)

**Success Criteria**:
- [ ] `ComputedAttributeData.is_on_part_definition` field exists and is correctly populated at extraction time
- [ ] `find_instance_paths_for_partdef()` utility exists and returns correct dotted instance paths
- [ ] EXPOSE_PURE on e2e_attr_expr `total_capex` produces a `ChannelAlias` with:
  - `alias_name = "total_capex"` (or scoped form)
  - `canonical_name = "component_cost.total_cost"` (from references field)
  - `source = "expose_pure"`
- [ ] EXPOSE_PURE on solar_battery PartDef `misc_hardware_cost` is FILTERED (not an alias) via `is_on_part_definition`
- [ ] `:>>` CHAIN redefs on solar_battery produce 41 `ChannelAlias` objects (matching Spike 8 count)
- [ ] BARE CAS code redefs (13 instances in solar_battery) are filtered out
- [ ] CHAIN aliases have instance-path-scoped canonical_names (dotted, prefix-stripped)
- [ ] All existing tests pass (zero regressions)

**Unit Tests for Filtering Logic** (synthetic, fast):
- [ ] Test: CHAIN redef with `"."` in source_path -> produces ChannelAlias
- [ ] Test: CHAIN redef with `"CAS220101"` (no dot) -> filtered out
- [ ] Test: EXPOSE_PURE on PartDef (`is_on_part_definition=True`) -> filtered out
- [ ] Test: EXPOSE_PURE on PartUsage (`is_on_part_definition=False`) -> produces ChannelAlias with correct `canonical_name` from `references`
- [ ] Test: EXPOSE_PURE with < 2 references -> skipped with warning

**Estimated Effort**: 1 day (spec 1h, design 1.5h, plan 0.5h, execute 5h)

**Location**: `.project/active/alias-producers/`

**Dependencies**: Item 1 (ChannelAlias data model)

**Deliverables**:
- `src/sysml_codegen/extraction/data_models.py` (add `is_on_part_definition` to `ComputedAttributeData`)
- `src/sysml_codegen/extraction/computed_attribute_extractor.py` (modified: EXPOSE_PURE -> ChannelAlias)
- `src/sysml_codegen/extraction/hierarchy_resolver.py` (modified: CHAIN -> ChannelAlias)
- `src/sysml_codegen/generation/initialization.py` (extract `find_instance_paths_for_partdef()` utility)
- `tests/unit/test_computed_attribute_extractor.py` (EXPOSE_PURE alias + filtering tests)
- `tests/unit/test_hierarchy_resolver.py` (CHAIN alias + filtering tests)

**Smoke Test (real model data)**: Extract computed attributes from real `attr_expr_probe` model, verify EXPOSE_PURE `total_capex` produces a `ChannelAlias` (not a module index entry). This catches the class of bugs where synthetic fixtures pass but real data fails (exactly what Bug 2 was).

**Reference spikes**: Spike 3 (references field), Spike 6 (CHAIN RHS formats), Spike 8 (PartDef filter, instance_path format, 41 CHAIN aliases)

---

### Item 2b: Virtual Binding Rewrite Enhancement + Step Consolidation [~0.5 days]

**Type**: Implementation

**Objective**: Add CHAIN override support to `_rewrite_virtual_bindings()`, consolidate aggregation scoping into Step 3.5, and eliminate Step 3.6.

**Current State**:
- Virtual binding rewrite only handles LITERAL overrides with bare-name matching
- Step 3.6 heuristically derives aliases from CalcUsage param_name divergence
- Step 4.7 runs aggregation scoping as a separate step

**Scope**:
1. **CHAIN override support** (Change 5):
   - Modify `_rewrite_virtual_bindings()`: handle CHAIN overrides (not just LITERAL)
   - Extract leaf from SYSML_QN (`::` split) and DOTTED (`.` split)
   - **NOTE**: This is a larger change than bare-name matching alone -- the fundamental matching logic changes from "bare name only" to "leaf name from SYSML_QN or DOTTED format." Spike 1 showed zero bare-name bindings, so the current bare-name matching is technically dead code; the new logic handles the actual formats observed.
   - CHAIN override: rewrite `binding.source_path = matched.source_path`
2. **Step consolidation** (Changes 6, 7):
   - Move aggregation scoping from Step 4.7 into Step 3.5 (scoping sub-step)
   - **Before removing Step 3.6**: Run a diagnostic pass that logs every alias produced by `_enrich_aliases_from_bindings()` and verifies each is a subset of CHAIN-derived aliases from Item 2a. This validates the Spike 6 assertion that CHAIN redefs are sufficient. If any Step 3.6 alias is NOT produced by CHAIN redefs, investigate before removing.
   - Remove `_enrich_aliases_from_bindings()` (Step 3.6) only after diagnostic confirms CHAIN coverage
   - Update `build_pipeline_context()` call sequence in `initialization.py`

**Out of Scope**:
- Building the OutputRegistry (Item 3)
- ChannelAlias production (Item 2a)
- Expression compiler changes (none needed)

**Success Criteria**:
- [ ] CHAIN override test: virtual CalcUsage binding with SYSML_QN source_path gets leaf extracted and matched
- [ ] CHAIN override test: virtual CalcUsage binding with DOTTED source_path gets leaf extracted and matched
- [ ] **Step 3.6 diagnostic (committed test, not just a log)**: All aliases produced by `_enrich_aliases_from_bindings()` confirmed as a subset of CHAIN-derived aliases from Item 2a. This is a committed test, not just a diagnostic run:
  ```python
  def test_step36_aliases_are_subset_of_chain_aliases():
      """All aliases from _enrich_aliases_from_bindings() are also produced by CHAIN."""
  ```
  If this test fails, it means Step 3.6 covers a case that CHAIN doesn't, and investigation is required before removal.
- [ ] Step 3.6 is removed: `_enrich_aliases_from_bindings()` no longer called (only after committed test passes)
- [ ] Step 4.7 logic merged into Step 3.5: `ScopedAggregationData` produced by hierarchy step
- [ ] All existing tests pass (zero regressions)

**Estimated Effort**: 0.5 days (spec 0.5h, design 0.5h, plan 0.5h, execute 2.5h)

**Location**: `.project/active/step-consolidation/`

**Dependencies**: Item 2a (ChannelAlias producers must exist first)

**Deliverables**:
- `src/sysml_codegen/generation/initialization.py` (modified: CHAIN override + step consolidation)
- `tests/unit/test_rewrite_virtual_bindings.py` (CHAIN override + leaf extraction tests)

**Smoke Test (real model data)**: Run `_rewrite_virtual_bindings()` on real `solar_battery` data with CHAIN override handling, verify rewrite count matches expected. This validates the leaf extraction logic against real SYSML_QN and DOTTED format bindings.

**Reference spikes**: Spike 1 (source_path formats, zero bare names), Spike 6 (CHAIN RHS formats)

---

### Item 3: OutputRegistry Construction + Backtracker Integration [~1.5 days]

**Type**: Implementation

**Objective**: Build the OutputRegistry during pipeline initialization (new Step 5), refactor the backtracker to use it for CHAIN and REFERENCE binding resolution, and validate via parallel execution that results are identical to the current implementation.

**Prerequisites**:
- **Fixture mapping (resolved)**: `e2e_attr_expr` = `tests/fixtures/attr_expr_probe/`. The name `e2e_attr_expr` refers to the E2E design model defined in the `attr_expr_probe` fixture directory (contains `design.sysml` and `library.sysml`). No new fixture needed.

**Current State**:
- No OutputRegistry construction step exists
- Backtracker builds 5 separate indexes in its constructor
- 7-strategy cascade in `_resolve_binding_to_usage()` with 12+ lookups
- Bug 2: EXPOSE_PURE -> ENTRY_POINT instead of MODULE_OUTPUT
- 4 REFERENCE->MODULE_OUTPUT cases resolved through computed_attr_index (will be removed)

**Scope**:
1. **Baseline YAML capture** (before any integration work):
   - Run full codegen on all 4 models (solar_battery, e2e_attr_expr/attr_expr_probe, chain_spike, sample_model) and commit generated pipeline YAML as baseline fixtures in `tests/fixtures/baseline_yaml/`
   - These baselines are used for YAML diff validation in Item 4
2. **Contract tests FIRST** (test-driven development for the integration boundary):
   - Write contract tests that define the interface before implementing it -- for every binding, the key the backtracker constructs exists in the registry
   - These tests fail initially (no registry construction yet) and go green as integration is implemented
   - **Sequence**: (a) Write contract tests (fail), (b) Write `build_output_registry()` in initialization.py, (c) Make contract tests pass, (d) Write parallel validation, (e) Wire backtracker to registry
3. **OutputRegistry construction** (Change 8):
   - Add Step 5 to `build_pipeline_context()` in `initialization.py`
   - Phase 1: Register CalcUsage outputs (Key_A, Key_B, **Key_C**), aggregation outputs (Key_D, Key_E + alias variants), FORMULA outputs (Key_F)
   - Phase 2: Register CHAIN aliases from Item 2a
   - Phase 3: Register EXPOSE_PURE aliases from Item 2a (PartUsage only)
   - Phase 4: Register transitive design attr aliases (filter via `_is_transitive_default()`)
   - Interface: `OutputRegistry` passed to `DependencyBacktracker` constructor
4. **Backtracker refactoring** (Change 9):
   - Accept `OutputRegistry` in constructor
   - CHAIN resolution: `registry.resolve(source_path)` -> MODULE_OUTPUT or `_resolve_to_design_attribute()` -> ENTRY_POINT
   - REFERENCE resolution: exact match -> secondary (leaf + `segments[-2]` scope) -> `_resolve_to_design_attribute()` -> ENTRY_POINT with warning
   - New method `_get_parent_part_for_usage()`: `segments[-2]` of qualified_name
   - New method `_resolve_to_design_attribute()`: extract leaf, search by (parent, leaf), literal-valued only
5. **Parallel validation gate**:
   - During transition: run BOTH old cascade AND new OutputRegistry resolution
   - **Architecture**: Add a `_resolve_binding_via_registry(binding)` method alongside the existing `_resolve_binding_to_usage(binding)`. In the backtracker's `_resolve_single_binding()`, call both paths unconditionally. Compare results. Log divergences with full context (binding source_path, old result type+channel, new result type+channel). Use the OLD result as the authoritative output during Item 3 (new path is shadow/validation only). No feature flag needed -- both paths run unconditionally during Item 3, and the old path is removed in Item 4.
   - Assert `binding_resolutions` are identical for every binding
   - Log any divergences with full context (binding, old result, new result)
   - Gate: do NOT remove old code until parallel validation passes on all models
6. **Contract test between OutputRegistry and Backtracker** (written in step 2, validated here):
   - For every binding in test fixtures, verify that the key the backtracker constructs for `registry.resolve()` exists in the registry built from the same test data
   - This explicitly tests the interface contract and catches the class of key-format-mismatch bugs that produced the original problem (5 indexes with incompatible formats)
7. **Test migration preparation**:
   - Audit `test_backtracker_computed_attrs.py` (19 tests accessing `bt._computed_attr_index` and internal methods) and `test_backtracker_aggregation.py` for internal index access
   - Identify which tests need migration to test OutputRegistry-based resolution behavior instead of internal index structure
   - Mark tests for migration (actual migration completes in Item 4)

**Out of Scope**:
- Removing old indexes (Item 4)
- Graph builder changes (Item 4)
- Expression compiler changes (none needed)

**Success Criteria**:
- [ ] OutputRegistry constructed with 4-phase protocol in `build_pipeline_context()`
- [ ] Parallel validation: **zero divergences** on solar_battery model (all bindings)
- [ ] Parallel validation: **zero divergences** on e2e_attr_expr model (all bindings)
- [ ] Parallel validation: **zero divergences** on chain_spike model (all bindings)
- [ ] Parallel validation: **zero divergences** on sample_model (all bindings)
- [ ] Bug 2 test: `financial.total_capex` in e2e_attr_expr resolves to MODULE_OUTPUT via new path
- [ ] REFERENCE secondary resolution: 4 computed attribute cases resolve to MODULE_OUTPUT (solar_battery: `p_net_kw`, `capital_cost`; e2e_attr_expr: `power_mw`, `annual_om`)
- [ ] **REFERENCE→MODULE_OUTPUT transition test**: For each of the 4 REFERENCE→MODULE_OUTPUT cases, explicitly verify that `registry.resolve(f"{parent_part}.{leaf_name}")` returns the same channel as the old `_computed_attr_index[key]`. This validates that secondary resolution (segments[-2] + leaf name) produces equivalent results to the removed index.
- [ ] `_get_parent_part_for_usage()` returns `segments[-2]` for all tested CalcUsages
- [ ] `_resolve_to_design_attribute()` resolves 119+ REFERENCE bindings to ENTRY_POINT
- [ ] Unresolved bindings produce `logger.warning()` (not silent)
- [ ] Contract test: for every binding in test fixtures, the key the backtracker constructs for `registry.resolve()` exists in the registry built from the same data
- [ ] Test migration audit complete: list of tests in `test_backtracker_computed_attrs.py` and `test_backtracker_aggregation.py` that access internal indexes, with migration plan
- [ ] All existing tests pass (zero regressions)

**Estimated Effort**: 1.5 days (spec 1h, design 2h, plan 1h, execute 8h)

**Location**: `.project/active/backtracker-integration/`

**Dependencies**: Item 1 (OutputRegistry class), Item 2a (alias producers), Item 2b (step consolidation)

**Deliverables**:
- `src/sysml_codegen/generation/initialization.py` (Step 5 added)
- `src/sysml_codegen/analysis/dependency_backtracker.py` (refactored)
- `tests/unit/test_output_registry_construction.py` (real model data tests)
- `tests/unit/test_backtracker_output_registry.py` (parallel validation tests)
- `tests/integration/test_parallel_validation.py` (E2E divergence check)

**Reference spikes**: All spikes (1-9). Key: Spike 5 (119 REFERENCE->ENTRY_POINT, 4 REFERENCE->MODULE_OUTPUT), Spike 8 (segments[-2] validated, Key_C required)

---

### Item 4: Cut-over, Cleanup, and E2E Validation [~2-2.5 days]

**Type**: Implementation / Testing

**Objective**: Remove the old backtracker indexes after parallel validation passes, simplify the graph builder, and perform comprehensive E2E validation that Bug 2 is fixed and all models generate correct pipeline wiring.

**Current State**:
- Old indexes still present in backtracker (behind parallel validation from Item 3)
- Graph builder builds its own output catalog (redundant with OutputRegistry)
- Bug 2 is fixed in new path but old path still exists
- Steps 3.6 and 4.7 code may still exist as dead code

**Scope**:
1. **Remove old backtracker indexes** (Change 9 completion):
   - Remove `_computed_attr_index`, `_aggregation_output_index`, `_output_catalog`, `_design_attr_binding_index`, `_usage_by_name`
   - Remove `_resolve_binding_to_usage()` (the 7-strategy cascade)
   - Remove parallel validation code (no longer needed)
   - Remove any dead code from Steps 3.6 and 4.7
2. **Graph builder simplification** (Change 10):
   - Clarify: `_build_output_catalog()` in graph_builder.py (line 107) builds a mapping used for downstream channel reference validation. This is a **validation** step, not binding resolution.
   - **Three functions to reconcile** (not just `_build_output_catalog()`):
     - `_build_output_catalog()` (line ~255): builds the base output catalog from CalcUsage outputs
     - `_extend_output_catalog_with_computed_attrs()` (line ~583): extends with FORMULA computed attribute channels
     - `_extend_output_catalog_with_aggregation()` (line ~830): extends with aggregation module channels
   - **Recommended approach**: Replace all three with a single validation pass using `OutputRegistry` as the authority. The graph builder should query the OutputRegistry for channel existence checks instead of building its own parallel catalog. This eliminates the last remaining parallel index.
   - Verify graph builder only consumes `binding_resolutions` and `ScopedAggregationData` for module construction
3. **Migrate tests from internal indexes to OutputRegistry-based behavior** (~0.5 day effort):
   - **Scope**: 39 tests total (19 in `test_backtracker_computed_attrs.py` accessing `bt._computed_attr_index`, 20 in `test_backtracker_aggregation.py` accessing `bt._aggregation_output_index`)
   - Complete migration of tests identified in Item 3 audit
   - Rewrite to test OutputRegistry-based resolution behavior instead of internal index structure
   - **Migration strategy**: For each test, determine if it tests (a) registration behavior (move to `test_output_registry.py`), (b) resolution behavior (rewrite to use `registry.resolve()` instead of direct index access), or (c) backtracker integration (keep in backtracker test file, update to use new API)
   - **Note**: This is substantial work (~39 tests). Budget accordingly -- this is the primary effort driver for Item 4.
4. **E2E validation**:
   - Run full codegen on solar_battery model, verify all wiring correct
   - Run full codegen on e2e_attr_expr model, verify Bug 2 is fixed
   - Run full codegen on chain_spike and sample_model, verify no regressions
   - Run full codegen on **Issue 22 fixture** (`tests/fixtures/issue22_model/`) -- validates REFERENCE->aggregation same-scope case (Spike 9)
   - Verify `IMPLEMENTATION_BACKLOG.md` output is correct
   - Verify pipeline YAML has no false entry points for values that should be module outputs
5. **Documentation**:
   - Update ADR references if needed
   - Capture lessons learned

**Out of Scope**:
- New features (expression compiler improvements, Phase 2/3 from expression-aware-codegen concept)
- Performance optimization (OutputRegistry is already O(1) lookup)

**Success Criteria**:
- [ ] Old backtracker indexes completely removed (zero references to `_computed_attr_index`, `_aggregation_output_index`, etc.)
- [ ] `_resolve_binding_to_usage()` cascade removed
- [ ] Graph builder does not construct its own output catalog (all three functions removed: `_build_output_catalog()`, `_extend_output_catalog_with_computed_attrs()`, `_extend_output_catalog_with_aggregation()`)
- [ ] E2E: solar_battery codegen produces identical pipeline YAML to current (or improved, with Bug 2 fixes)
- [ ] E2E: e2e_attr_expr `financial.total_capex` wired to MODULE_OUTPUT (`component_cost.total_cost`)
- [ ] E2E: chain_spike codegen produces correct pipeline YAML
- [ ] E2E: Issue 22 fixture (`tests/fixtures/issue22_model/`) REFERENCE->aggregation same-scope resolves to MODULE_OUTPUT
- [ ] All migrated tests (from `test_backtracker_computed_attrs.py`, `test_backtracker_aggregation.py`) pass against OutputRegistry-based resolution
- [ ] All tests pass (zero regressions across full test suite: `uv run pytest tests/`)
- [ ] **YAML diff validation**: Generated pipeline YAML for each model diffed against known-good baselines (captured before Item 4 cut-over). Only expected changes (Bug 2 fix, Issue 22 fix) should appear.
- [ ] No dead code from Steps 3.6, 4.7, or old backtracker cascade
- [ ] `uv run mypy src/` passes
- [ ] `uv run ruff check src/` passes

**Estimated Effort**: 2-2.5 days (spec 0.5h, design 0.5h, plan 0.5h, execute 5h, test migration 8h, graph builder changes 4h). The test migration alone (39 tests) and graph builder interface changes are substantial -- previous estimate of 1.5 days was tight.

**Location**: `.project/active/cutover-validation/`

**Dependencies**: Item 3 (parallel validation must pass first)

**Deliverables**:
- `src/sysml_codegen/analysis/dependency_backtracker.py` (cleaned up)
- `src/sysml_codegen/resolution/graph_builder.py` (simplified)
- `src/sysml_codegen/generation/initialization.py` (dead code removed)
- `tests/integration/test_e2e_output_registry.py` (E2E validation tests)
- Validation report documenting test results

---

## Dependencies

**External**:
- `agentic-mbse` library (unchanged -- no modifications needed)
- SysIDE adapter (unchanged -- extraction layer stays the same)

**Internal**:
- COST-PATTERN epic items 1-4 complete (done)
- Design document `.project/reports/08_algorithm_revised.md` finalized (done -- 3 iterations, 22 issues closed)
- Spikes 1-9 complete with results documented (done)

**Item Dependency Graph**:
```
Item 1: OutputRegistry Foundation (no dependencies)
  |
  v
Item 2a: ChannelAlias Producers (depends on Item 1)
  |
  v
Item 2b: Virtual Binding Rewrite + Step Consolidation (depends on Item 2a)
  |
  v
Item 3: OutputRegistry Construction + Backtracker Integration (depends on Items 1+2a+2b)
  |
  v
Item 4: Cut-over, Cleanup, and E2E Validation (depends on Item 3)
```

All items are sequential. No parallelism (each builds on the previous). Item 2a is independently testable; Item 2b can be deferred if issues arise in 2a without blocking integration testing.

**Regression Gates** (mandatory between items):

Each gate must pass before proceeding to the next item. These are explicit enforcement checkpoints, not just success criteria.

| Gate | Runs After | Command | Additional Checks |
|------|-----------|---------|-------------------|
| Gate 1 | Item 1 | `uv run pytest tests/` | Trivial -- purely additive, no existing code modified |
| Gate 2a | Item 2a | `uv run pytest tests/` | + specifically run `uv run pytest tests/unit/test_computed_attribute_extractor.py tests/integration/ -v` |
| Gate 2b | Item 2b | `uv run pytest tests/` | + specifically run `uv run pytest tests/unit/test_rewrite_virtual_bindings.py tests/integration/ -v` -- **critical gate** because Item 2b changes fundamental matching logic in `_rewrite_virtual_bindings()` (behavior change, not purely additive) |
| Gate 3 | Item 3 | `uv run pytest tests/` | + parallel validation zero-divergence on all 4 models + `uv run mypy src/` |
| Gate 4 | Item 4 | `uv run pytest tests/` | + `uv run mypy src/` + `uv run ruff check src/` + E2E YAML diff against baselines |

---

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Parallel validation reveals divergences on a model not covered by spikes | High | Spikes covered 4 models (solar_battery, e2e_attr_expr, chain_spike, sample_model) and 215+ bindings. Divergences trigger investigation, not bypass. |
| PartDef EXPOSE_PURE filter is too aggressive (filters a needed alias) | Medium | Spike 8 showed CHAIN aliases handle all PartDef cases (41/41). If a future model needs PartDef EXPOSE_PURE, the filter can be relaxed with instance-scoped expansion. |
| Key_C derivation produces collisions for models with naming edge cases | Medium | Spike 8: zero collisions across 250 keys in 2 models. Collision policy (refuse overwrite) prevents silent wrong wiring. |
| REFERENCE secondary resolution (`segments[-2]`) fails for deeply nested hierarchy | Low | Spike 8+9 validated for all observed cases. Known limitation documented. If triggered, resolution falls back to ENTRY_POINT with warning. |
| `_is_transitive_default()` filter misclassifies a default_value | Low | Spike 7: 128 attrs, filter correct for all. Only 2 transitive defaults exist across all models. False positives resolve harmlessly (redundant alias), false negatives fall through to existing ENTRY_POINT path. |
| Phantom detector depends on removed indexes | Low | PhantomDetector (initialized in backtracker constructor, line 246) uses `all_usages` and `calc_defs` to produce `PhantomDetectionReport`. **Verified:** PhantomDetector does NOT depend on `_computed_attr_index`, `_aggregation_output_index`, `_output_catalog`, `_design_attr_binding_index`, or `_usage_by_name`. It operates on the raw CalcUsage/CalcDef lists. Safe to remove the 5 indexes without affecting phantom detection. |

**Rollback Strategy**:

Items 1-2b are purely additive (new classes, new fields, new return values). They do not modify existing behavior. If parallel validation in Item 3 reveals blocking divergences that can't be resolved quickly:

1. The OutputRegistry code remains dormant -- it exists but doesn't affect pipeline output.
2. The old cascade continues operating as the authoritative resolution path (it's still the primary path during Item 3; the new path is shadow-only).
3. Investigation of divergences informs a targeted fix before re-attempting parallel validation.
4. No git revert needed -- the additive code is safe to leave in place.

Item 4 (cut-over) is the only destructive step, and it only proceeds after parallel validation passes with zero divergences. If issues emerge during Item 4 cut-over, git revert to the post-Item-3 state restores the dual-path configuration.

---

## Timeline

**Total Effort**: ~6-6.5 days

| Item | Effort | Dependencies |
|------|--------|--------------|
| Item 1: OutputRegistry Foundation | 1 day | None |
| Item 2a: ChannelAlias Producers | 1 day | Item 1 |
| Item 2b: Virtual Binding Rewrite + Step Consolidation | 0.5 days | Item 2a |
| Item 3: OutputRegistry Construction + Backtracker Integration | 1.5 days | Items 1+2a+2b |
| Item 4: Cut-over, Cleanup, and E2E Validation | 2-2.5 days | Item 3 |

---

## Key Reference Documents

| Document | Role |
|----------|------|
| `.project/reports/08_algorithm_revised.md` | Authoritative desired-state design (3 iterations, 22 issues closed) |
| `.project/reports/07_open_issues.md` | Root cause analysis of current problems |
| `.project/reports/06_algorithm_overview.md` | Current pipeline documentation |
| `.project/reports/design_revision_comments.md` | Iteration 1 review (Issues 1-8, Spikes 1-4) |
| `.project/reports/design_revision_comments_v2.md` | Iteration 2 review (Issues 9-14, Spikes 5-7) |
| `.project/reports/design_revision_comments_v3.md` | Iteration 3 review (Issues 15-22, Spikes 8-9) |
| `.project/research/20260213_spike_results_syside_assumptions.md` | Spike 1-4 results |
| `.project/research/20260213_spike_results_iteration2.md` | Spike 5-7 results |
| `.project/research/20260213_spike_results_output_registry_e2e.md` | Spike 8-9 results |
| `.project/research/20260213-152845_bug2-expose-calcusage-wiring-persistent-failure.md` | Bug 2 root cause analysis |
| `.project/concepts/expression-aware-codegen.md` | Original expression-aware concept (data models, patterns A-M) |
| `.project/reports/spec_review_synthesis.md` | Spec cross-consistency issues and resolutions (C1: `_extract_and_filter_computed_attributes()` returns 3-tuple per Spec 04; C2: EXPOSE_PURE alias_name scoping per Spec 04) |

---

**Last Updated**: 2026-02-13
**Revision**: v4 -- applied second review feedback:
- GAP-1: Documented `_usage_by_name` retention for `find_required_modules()` in Change 9 (only cascade usage removed)
- GAP-2: Added `_find_usage_for_channel()` method and self-reference guard adaptation to Change 9
- GAP-3: Documented `is_transitive` always-False behavioral change in Change 9
- GAP-4: Resolved fixture mapping: `e2e_attr_expr` = `tests/fixtures/attr_expr_probe/`
- GAP-5: Added baseline YAML capture step to Item 3 (before integration work)
- T1: Bug 2 xfail regression test written BEFORE implementation (Item 1)
- T2: Contract tests written BEFORE integration code (Item 3 resequenced)
- T3: Real-model smoke tests added to Items 1, 2a, 2b
- T4: Step 3.6 diagnostic elevated to committed test (Item 2b)
- E1: Item 4 estimate increased to 2-2.5 days (total 6-6.5 days)
- E2: Graph builder validation interface details added to Change 10
- Added `spec_review_synthesis.md` to Key Reference Documents (C1, C2 resolutions)
**Next Action**: Begin Item 2a (ChannelAlias Producers) -- Item 1 complete, audited, all gates passed
