# Implementation Plan: ChannelAlias Producers & Step Consolidation

**Status:** Complete
**Created:** 2026-02-13
**Last Updated:** 2026-02-13

## Source Documents
- **Spec:** `.project/active/alias-producers-step-consolidation/spec.md`
- **Design:** `.project/active/alias-producers-step-consolidation/design.md` ← See here for component details, dependencies, architecture

## Implementation Strategy

**Phasing Rationale:**
Phase 1 establishes the EXPOSE_PURE alias production pattern (return type change + ChannelAlias construction) — this is the foundation all other phases build on. Phase 2 adds CHAIN alias production using the same pattern, plus the shared `find_instance_paths_for_partdef()` utility. Phase 3 wires both alias sources through the pipeline (PipelineContext, step reordering). Phase 4 tackles the only behavioral change (`_rewrite_virtual_bindings()` leaf extraction) and the diagnostic-gated Step 3.6 removal — isolated last because it's the highest-risk change and depends on CHAIN aliases being fully produced.

**Overall Validation Approach:**
- Each phase starts with tests
- Each phase has automated + manual validation
- Continuous verification ensures no regressions
- Gate 2a after Phase 3, Gate 2b after Phase 4

---

## Phase 1: EXPOSE_PURE Alias Production

### Goal
Add `is_on_part_definition` field to `ComputedAttributeData`, change `extract_computed_attributes()` to return a 2-tuple, and produce `ChannelAlias` objects from EXPOSE_PURE attributes. This is the foundation — validates the alias production pattern before CHAIN aliases.

### Test Stencil (Write This First)
```python
# tests/unit/test_alias_producers.py — EXPOSE_PURE section
# Uses existing mock patterns from test_computed_attribute_extraction.py

class TestExposePureAliasProduction:
    def test_partusage_expose_pure_produces_channel_alias(self, mock_syside_adapter):
        """EXPOSE_PURE on PartUsage with 2 refs → ChannelAlias with bare alias_name."""
        # Setup: mock part element (PartUsage), attribute with EXPOSE_PURE refs
        # Execute: extract_computed_attributes(adapter, part_elem, calc_usage_names)
        # Verify: aliases list has 1 entry, alias_name is bare python_name,
        #         canonical_name = "instance.output", source = "expose_pure"

    def test_partdef_expose_pure_filtered(self, mock_syside_adapter):
        """EXPOSE_PURE on PartDef (is_on_part_definition=True) → no alias."""
        # Verify: aliases list is empty

    def test_expose_pure_fewer_than_2_refs_skipped(self, mock_syside_adapter, caplog):
        """EXPOSE_PURE with < 2 refs → warning logged, no alias."""
        # Verify: warning in caplog, aliases list is empty

    def test_expose_pure_stays_in_cad_list(self, mock_syside_adapter):
        """EXPOSE_PURE still appears in ComputedAttributeData list (graph builder compat)."""
        # Verify: results list contains the EXPOSE_PURE entry

    def test_is_on_part_definition_true_for_partdef(self, mock_syside_adapter):
        """PartDef element → is_on_part_definition=True on extracted attrs."""

    def test_is_on_part_definition_false_for_partusage(self, mock_syside_adapter):
        """PartUsage element → is_on_part_definition=False."""
```

### Changes Required

**See `design.md` for:**
- Component 1 details → `design.md#component-1-is_on_part_definition-field`
- Component 2 details → `design.md#component-2-extract_computed_attributes-return-type-change`
- EXPOSE_PURE ChannelAlias construction pattern → `design.md#component-2`
- Ref classification logic (instance vs output by calc_usage_names) → `design.md#component-2`

**Specific file changes:**

#### 1. Test File
**File:** `tests/unit/test_alias_producers.py` (NEW — write first)
- [ ] Create test file with mock fixtures (reuse patterns from `test_computed_attribute_extraction.py`)
- [ ] Implement EXPOSE_PURE alias production tests (6 tests from stencil)
- [ ] Implement `is_on_part_definition` field tests (2 tests)

#### 2. Data Model
**File:** `src/sysml_codegen/extraction/data_models.py:214`
- [ ] Add `is_on_part_definition: bool = False` field to `ComputedAttributeData` after `compiled_expression`

#### 3. Computed Attribute Extractor
**File:** `src/sysml_codegen/extraction/computed_attribute_extractor.py:110-234`
- [ ] Add `from sysml_codegen.core.models import ChannelAlias` import
- [ ] Change return type to `tuple[list[ComputedAttributeData], list[ChannelAlias]]`
- [ ] Add `is_part_def = SysideAdapter.is_instance(part_element, "PartDefinition")` at function top
- [ ] Extract `python_name = _sanitize_name(attr_name)` to local var before CAD constructor
- [ ] Pass `is_on_part_definition=is_part_def` to CAD constructor
- [ ] Initialize `aliases: list[ChannelAlias] = []`
- [ ] Add EXPOSE_PURE → ChannelAlias block after `results.append()` (see `design.md#component-2` for ref classification logic)
- [ ] Return `(results, aliases)`

### Validation

**Automated:**
- [ ] `uv run pytest tests/unit/test_alias_producers.py -v` → All EXPOSE_PURE tests pass
- [ ] `uv run pytest tests/unit/test_computed_attribute_extraction.py -v` → No regressions (return type change may require fixture updates)
- [ ] `uv run mypy src/sysml_codegen/extraction/computed_attribute_extractor.py` → Type-clean

**Manual:**
- [ ] Verify `extract_computed_attributes()` return type is `tuple[list[CAD], list[ChannelAlias]]` in function signature

**What We Know Works After This Phase:**
EXPOSE_PURE attributes correctly produce `ChannelAlias` objects with bare `alias_name`, `canonical_name` from refs, PartDef filtering, and refs < 2 guard. The `is_on_part_definition` field is populated. The extractor still returns EXPOSE_PURE in the CAD list for graph builder compat. Note: `_extract_and_filter_computed_attributes()` caller will break (fixed in Phase 3) — unit tests for the extractor itself pass.

---

## Phase 2: Instance Path Utility + CHAIN Alias Production

### Goal
Extract `find_instance_paths_for_partdef()` as a shared utility, build `_build_chain_aliases()`, and refactor `_scope_aggregation_expressions()` to use the utility. This produces the second alias source (CHAIN redefinitions).

### Test Stencil (Write This First)
```python
# tests/unit/test_alias_producers.py — CHAIN + utility section

class TestFindInstancePathsForPartdef:
    def test_direct_match_strategy(self):
        """Virtual CalcUsage on same PartDef → correct dotted path."""
        # Setup: calc_usage with owning_part_def_qn matching target
        # Verify: returns ["part_usage.nested_part"] (dotted, prefix-stripped)

    def test_child_walk_strategy(self):
        """Child PartUsage name match → correct dotted path."""

    def test_no_match_returns_empty(self):
        """No matching CalcUsages → empty list."""

class TestBuildChainAliases:
    def test_chain_redef_with_dot_produces_alias(self):
        """CHAIN redef with '.' in source_path → ChannelAlias with scoped names."""
        # Verify: alias_name = "instance_path.redef.attribute_name"
        #         canonical_name = "instance_path.redef.source_path"
        #         source = "redefinition"

    def test_bare_cas_code_filtered(self):
        """CHAIN redef with no '.' in source_path (CAS220101) → filtered."""

    def test_deep_path_redef_filtered(self):
        """CHAIN redef with is_deep_path=True → filtered."""
```

### Changes Required

**See `design.md` for:**
- Component 4 details → `design.md#component-4-find_instance_paths_for_partdef-utility`
- Component 5 details → `design.md#component-5-_build_chain_aliases--chain-redef--channelalias`
- Instance path derivation strategies → `design.md#rf-5-instance-path-derivation-logic`
- Filter criteria (bare CAS, deep-path) → `design.md#component-5`

**Specific file changes:**

#### 1. Test File
**File:** `tests/unit/test_alias_producers.py` (extend)
- [ ] Add `TestFindInstancePathsForPartdef` class (3 tests from stencil)
- [ ] Add `TestBuildChainAliases` class (3 tests from stencil)
- [ ] Use `_make_virtual_calc_usage()` factory pattern from `test_hierarchy_pipeline.py`

#### 2. Instance Path Utility
**File:** `src/sysml_codegen/generation/initialization.py`
- [ ] Add `find_instance_paths_for_partdef()` function (extract from `_scope_aggregation_expressions()` lines 361-397)
- [ ] Returns sorted list of dotted, design-prefix-stripped paths
- [ ] Includes both Strategy 1 (direct) and Strategy 2 (child-walk)

#### 3. CHAIN Alias Builder
**File:** `src/sysml_codegen/generation/initialization.py`
- [ ] Add `_build_chain_aliases()` function (see `design.md#component-5` for signature and logic)
- [ ] Filters: `redef.is_deep_path` → skip; `"." not in redef.source_path` → skip
- [ ] Scopes both alias_name and canonical_name with instance_path prefix

#### 4. Refactor `_scope_aggregation_expressions()`
**File:** `src/sysml_codegen/generation/initialization.py:346-406`
- [ ] Refactor to call `find_instance_paths_for_partdef()` internally
- [ ] Reconstruct `__`-separated paths for `ScopedAggregationData.instance_path` from dotted return

### Validation

**Automated:**
- [ ] `uv run pytest tests/unit/test_alias_producers.py -v` → All tests pass (Phase 1 + Phase 2)
- [ ] `uv run pytest tests/unit/test_hierarchy_pipeline.py -v` → No regressions (refactored `_scope_aggregation_expressions()`)
- [ ] `uv run pytest tests/ -v` → Full suite (catch any `_scope_aggregation_expressions()` refactoring issues)

**Manual:**
- [ ] Verify `find_instance_paths_for_partdef()` returns dotted paths (not `__`-separated)
- [ ] Verify `_scope_aggregation_expressions()` still produces identical `ScopedAggregationData` output after refactoring

**What We Know Works After This Phase:**
Both alias sources produce correct `ChannelAlias` objects. Instance path utility works for both strategies. CHAIN redefs correctly filter bare CAS codes and deep-path entries. `_scope_aggregation_expressions()` refactoring is equivalent to original.

---

## Phase 3: Pipeline Integration

### Goal
Wire both alias sources through the pipeline: update `_extract_and_filter_computed_attributes()` for 2-tuple, add `PipelineContext.channel_aliases`, reorder steps (merge 4.7 into 3.5), and merge EXPOSE_PURE + CHAIN aliases.

### Test Stencil (Write This First)
```python
# No new test file — validation through existing integration tests
# The key verification is that build_pipeline_context() runs without error
# and PipelineContext.channel_aliases is populated

# Extend existing integration tests if needed:
def test_pipeline_context_has_channel_aliases():
    """PipelineContext.channel_aliases populated after build."""
    # Run build_pipeline_context() on e2e_attr_expr model
    # Verify: ctx.channel_aliases is non-empty list of ChannelAlias
```

### Changes Required

**See `design.md` for:**
- Component 3 → `design.md#component-3-_extract_and_filter_computed_attributes-update`
- Component 6 → `design.md#component-6-pipelinecontext-update`
- Component 7 → `design.md#component-7-build_pipeline_context-step-reordering`

**Specific file changes:**

#### 1. `_extract_and_filter_computed_attributes()`
**File:** `src/sysml_codegen/generation/initialization.py:152-208`
- [ ] Change return type to `tuple[list[ComputedAttributeData], list[ChannelAlias]]`
- [ ] Initialize `all_expose_aliases: list[ChannelAlias] = []` before loop
- [ ] Unpack 2-tuple from `extract_computed_attributes()`: `computed, expose_aliases = ...`
- [ ] Extend: `all_expose_aliases.extend(expose_aliases)`
- [ ] Return `(all_computed_attrs, all_expose_aliases)`

#### 2. PipelineContext
**File:** `src/sysml_codegen/generation/initialization.py:72-111`
- [ ] Add `channel_aliases: list[ChannelAlias] = field(default_factory=list)` after `aggregation_expressions`
- [ ] Add `from sysml_codegen.core.models import ChannelAlias` import

#### 3. `_extract_hierarchy_and_rewrite_bindings()` Update
**File:** `src/sysml_codegen/generation/initialization.py:211-235`
- [ ] Update to also call `_scope_aggregation_expressions()` and `_build_chain_aliases()`
- [ ] Change return type to `tuple[HierarchyExtractionResult, list[ScopedAggregationData], list[ChannelAlias]]`

#### 4. `build_pipeline_context()` Step Reordering
**File:** `src/sysml_codegen/generation/initialization.py:409-571`
- [ ] Step 3.5: Unpack 3-tuple from updated `_extract_hierarchy_and_rewrite_bindings()`
- [ ] Remove Step 4.7 (`_scope_aggregation_expressions()` call) — now in Step 3.5
- [ ] Step 4.5: Unpack 2-tuple from `_extract_and_filter_computed_attributes()`
- [ ] Merge aliases: `all_channel_aliases = chain_aliases + expose_aliases`
- [ ] Pass `channel_aliases=all_channel_aliases` to PipelineContext constructor

### Validation

**Automated:**
- [ ] `uv run pytest tests/ -v` → Full suite passes (zero regressions)
- [ ] Gate 2a: `uv run pytest tests/unit/test_alias_producers.py tests/integration/ -v` → All pass
- [ ] `uv run mypy src/sysml_codegen/generation/initialization.py` → Type-clean

**Manual:**
- [ ] Verify step ordering in `build_pipeline_context()`: 3.5 now includes scoping + CHAIN aliases, no 4.7
- [ ] Verify PipelineContext constructor receives `channel_aliases`

**What We Know Works After This Phase:**
Complete Phase A (Item 2a) is done. Both alias sources flow through the pipeline into `PipelineContext.channel_aliases`. Step 4.7 merged into 3.5. All existing tests pass. Gate 2a cleared.

---

## Phase 4: Virtual Binding Rewrite Enhancement + Step 3.6 Removal

### Goal
Add CHAIN override support with leaf extraction to `_rewrite_virtual_bindings()`, write diagnostic test proving Step 3.6 is redundant, then remove Step 3.6. This is the only behavioral change in Item 2.

### Test Stencil (Write This First)
```python
# tests/unit/test_rewrite_virtual_bindings.py (NEW)

class TestRewriteVirtualBindingsLeafExtraction:
    def test_sysml_qn_format_leaf_extraction(self):
        """SYSML_QN source_path (Lib::CostModel::total_cost) → leaf 'total_cost' matched."""
        # Setup: binding with "::" source_path, matching override
        # Verify: binding.source_path rewritten to override's source_path

    def test_dotted_format_leaf_extraction(self):
        """DOTTED source_path (cost_model.total_cost) → leaf 'total_cost' matched."""

    def test_chain_override_rewrites_source_path(self):
        """CHAIN override → binding.source_path = matched.source_path, type unchanged."""

    def test_literal_override_unchanged(self):
        """LITERAL override → existing behavior (binding_type → LITERAL)."""

    def test_no_match_binding_unchanged(self):
        """No matching override → binding left as-is."""

# tests/integration/test_step36_diagnostic.py (NEW)

def test_step36_aliases_are_subset_of_chain_aliases():
    """All aliases from _enrich_aliases_from_bindings() are subset of CHAIN aliases."""
    # Load solar_battery model
    # Run pipeline up through Step 3.5 (with CHAIN aliases)
    # Capture what Step 3.6 would produce
    # Assert: every Step 3.6 alias has a corresponding CHAIN alias
```

### Changes Required

**See `design.md` for:**
- Component 8 → `design.md#component-8-_rewrite_virtual_bindings-enhancement`
- Component 9 → `design.md#component-9-step-36-diagnostic-test--removal`
- Leaf extraction logic → `design.md#component-8`

**Specific file changes:**

#### 1. Virtual Binding Rewrite Tests
**File:** `tests/unit/test_rewrite_virtual_bindings.py` (NEW — write first)
- [x] Create test file with mock fixtures
- [x] Implement 7 tests (SYSML_QN, DOTTED, bare-name, CHAIN override, LITERAL, no match, CHAIN dotted)

#### 2. Diagnostic Test
**File:** `tests/integration/test_step36_diagnostic.py` (NEW)
- [x] Create diagnostic test loading solar_battery model
- [x] Compare Step 3.6 aliases against CHAIN-derived aliases
- [x] Assert relationship (diagnostic found gap — param_name aliases not in CHAIN)

#### 3. `_rewrite_virtual_bindings()` Enhancement
**File:** `src/sysml_codegen/generation/initialization.py:256-323`
- [x] Replace bare-name matching with leaf extraction logic
- [x] Add CHAIN override branch: `binding.source_path = matched.source_path`
- [x] Keep LITERAL override branch unchanged

#### 4. Step 3.6 Removal (conditional on diagnostic passing)
**File:** `src/sysml_codegen/generation/initialization.py`
- [ ] ~~Remove `_enrich_aliases_from_bindings()` function definition~~ — DEFERRED: diagnostic found gap
- [ ] ~~Remove Step 3.6 call in `build_pipeline_context()`~~ — DEFERRED: retained until Item 3/4

### Validation

**Automated:**
- [x] `uv run pytest tests/unit/test_rewrite_virtual_bindings.py -v` → 7 passed
- [x] `uv run pytest tests/integration/test_step36_diagnostic.py -v` → 3 passed (gap documented)
- [x] `uv run pytest tests/ -v` → 591 passed, 1 xfailed (zero regressions)
- [x] Gate 2b: All pass
- [x] `uv run mypy src/` → Only pre-existing `agentic_mbse` import-untyped errors (no new type errors from Phase 4)

**Manual:**
- [x] Verify `_enrich_aliases_from_bindings()` is RETAINED (diagnostic found gap — correct decision)
- [x] Verify Step 3.6 call retained in `build_pipeline_context()` line 610 (deferred removal)

**What We Know Works After This Phase:**
Item 2a (alias producers + pipeline integration) is complete. Item 2b is partially complete: virtual binding rewrite handles CHAIN overrides with leaf extraction from SYSML_QN and DOTTED formats (done), but Step 3.6 removal is deferred — diagnostic found that param_name aliases from CalcUsage binding divergence are not produced by CHAIN redefs. Step 4.7 merged into 3.5 (done in Phase 3). All alias data flows through `PipelineContext.channel_aliases`. Gate 2a cleared. Gate 2b cleared for the rewrite enhancement; Step 3.6 removal deferred to Item 3/4.

---

## Environment Setup

**See CLAUDE.md for full environment rules**

Key commands:
- `uv run pytest tests/` — full test suite
- `uv run pytest tests/unit/test_alias_producers.py -v` — alias producer tests
- `uv run mypy src/` — type checking
- `uv run ruff check src/` — linting

---

## Risk Management

**See `design.md#potential-risks` for detailed risk analysis**

**Phase-Specific Mitigations:**
- **Phase 1**: Ref ordering risk mitigated by instance/output classification loop (not index-based). Test with both orderings.
- **Phase 2**: `find_instance_paths_for_partdef()` is mechanical extraction — verify identical output from `_scope_aggregation_expressions()` before/after refactoring.
- **Phase 3**: Pure wiring phase — lowest risk. Existing integration tests are the safety net.
- **Phase 4**: Highest risk (behavioral change). Isolated last. Diagnostic test gates Step 3.6 removal. If diagnostic fails, investigate rather than remove.

## Implementation Notes

[TO BE FILLED DURING IMPLEMENTATION]

### Phase 1 Completion
**Completed:** 2026-02-13
**Actual Changes:**
- Created `tests/unit/test_alias_producers.py` with 8 tests (6 EXPOSE_PURE alias + 2 is_on_part_definition)
- Added `is_on_part_definition: bool = False` to `ComputedAttributeData` in `data_models.py:215`
- Added `ChannelAlias` import to `computed_attribute_extractor.py`
- Changed `extract_computed_attributes()` return type to `tuple[list[ComputedAttributeData], list[ChannelAlias]]`
- Added `is_part_def` detection via `SysideAdapter.is_instance(part_element, "PartDefinition")`
- Extracted `python_name = _sanitize_name(attr_name)` to local var
- Added EXPOSE_PURE → ChannelAlias block with ref classification by `calc_usage_names`
- Updated 5 existing test callsites in `test_computed_attribute_extraction.py` for tuple return
- Fixed `initialization.py:188` caller minimally (unpack tuple, discard aliases until Phase 3)
**Issues:** None
**Deviations:**
- Fixed `initialization.py` caller in Phase 1 (plan said Phase 3) to keep full test suite green (572 passed)

### Phase 2 Completion
**Completed:** 2026-02-13
**Actual Changes:**
- Added 9 tests to `test_alias_producers.py`: 4 for `find_instance_paths_for_partdef()`, 5 for `_build_chain_aliases()`
- Added `ChannelAlias` import to `initialization.py`
- Implemented `find_instance_paths_for_partdef()` — extracted from `_scope_aggregation_expressions()`, returns dotted prefix-stripped paths
- Implemented `_build_chain_aliases()` — CHAIN redefs → scoped ChannelAlias, filters bare CAS codes and deep-path
- Refactored `_scope_aggregation_expressions()` to use `find_instance_paths_for_partdef()`, reconstructs `__`-separated paths from dotted return via design prefix
- Updated `__all__` to export new functions
**Issues:** None
**Deviations:** None — refactored `_scope_aggregation_expressions()` produces identical output (22 hierarchy pipeline tests pass)

### Phase 3 Completion
**Completed:** 2026-02-13
**Actual Changes:**
- Added `channel_aliases: list[ChannelAlias]` field to `PipelineContext`
- Updated `_extract_and_filter_computed_attributes()` to return `tuple[list[CAD], list[ChannelAlias]]`
- Updated `_extract_hierarchy_and_rewrite_bindings()` to return 3-tuple: `(HierarchyExtractionResult, list[ScopedAggregationData], list[ChannelAlias])`
  - Now also calls `_scope_aggregation_expressions()` (moved from Step 4.7) and `_build_chain_aliases()`
- Updated `build_pipeline_context()`:
  - Step 3.5 unpacks 3-tuple (hierarchy, scoped_agg, chain_aliases)
  - Removed Step 4.7 `_scope_aggregation_expressions()` call (now in Step 3.5)
  - Step 4.5 unpacks 2-tuple (computed_attrs, expose_aliases)
  - Merges: `all_channel_aliases = chain_aliases + expose_aliases`
  - Passes `channel_aliases=all_channel_aliases` to PipelineContext
- Gate 2a passed: 133 tests (alias producers + integration) all pass
**Issues:** None
**Deviations:** None

### Phase 4 Completion
**Completed:** 2026-02-14
**Actual Changes:**
- Created `tests/unit/test_rewrite_virtual_bindings.py` with 7 tests (3 leaf extraction + 4 CHAIN override support)
- Created `tests/integration/test_step36_diagnostic.py` with 3 tests (CHAIN populated, param_name gap documented, both sources present)
- Enhanced `_rewrite_virtual_bindings()` (initialization.py:256-323) with leaf extraction from SYSML_QN (`::`) and DOTTED (`.`) formats, plus CHAIN override branch (`binding.source_path = matched.source_path`)
- Retained LITERAL override behavior unchanged
- Step 3.6 (`_enrich_aliases_from_bindings()`) NOT removed — diagnostic revealed it produces param_name aliases (e.g., `total_capex`) that CHAIN redefs do not cover
**Issues:**
- Step 3.6 diagnostic found a gap: param_name aliases from CalcUsage binding divergence are NOT produced by CHAIN redefs. Step 3.6 is retained until backtracker uses OutputRegistry (Item 3/4)
**Deviations:**
- Plan item 4.4 (Step 3.6 removal) deferred — diagnostic correctly gated this. Step 3.6 remains in pipeline at line 610
- 7 tests instead of plan's 5 (added bare-name leaf test and CHAIN-with-dotted-source test for better coverage)

---

**Status**: ~~Draft~~ → ~~In Progress~~ → **Complete** (Step 3.6 removal deferred to Item 3/4)
