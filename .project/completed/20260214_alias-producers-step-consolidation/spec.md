# Spec: ChannelAlias Producers & Step Consolidation

**Status:** Complete
**Owner:** Reid Westwood
**Created:** 2026-02-13T22:53:12+00:00
**Complexity:** MEDIUM
**Branch:** cost-pattern
**Epic:** `.project/backlog/epic_output_registry_backtracker_redesign.md` (Items 2a + 2b)

---

## Business Goals

### Why This Matters

The OutputRegistry (Item 1, complete) provides a single exact-match lookup for resolving binding source_paths to canonical channel names. But it needs data to populate: specifically, `ChannelAlias` objects from two authoritative sources — EXPOSE_PURE computed attributes and `:>>` CHAIN redefinitions. Today, EXPOSE_PURE attributes incorrectly enter `_computed_attr_index` as if they were modules (root cause of Bug 2), and alias discovery relies on a heuristic in Step 3.6 (`_enrich_aliases_from_bindings()`) that infers aliases from parameter name divergence — semantically wrong and brittle.

This item produces the alias data that the OutputRegistry consumes, using authoritative structural information from the SysML model rather than heuristics. It also consolidates pipeline steps (merging Step 4.7 into 3.5, eliminating Step 3.6) and adds CHAIN override support to virtual binding rewrite.

### Success Criteria

- [ ] EXPOSE_PURE computed attributes produce `ChannelAlias` objects (not module index entries)
- [ ] `:>>` CHAIN redefinitions produce scoped `ChannelAlias` objects
- [ ] Virtual binding rewrite handles CHAIN overrides (not just LITERAL), with leaf extraction from SYSML_QN and DOTTED formats
- [ ] Step 3.6 (`_enrich_aliases_from_bindings()`) eliminated after diagnostic confirmation
- [ ] Step 4.7 logic merged into Step 3.5
- [ ] All existing tests pass (zero regressions)

### Priority

P0 — on the critical path for the OutputRegistry epic. Blocks Item 3 (OutputRegistry Construction + Backtracker Integration) and Item 4 (Cut-over).

---

## Problem Statement

### Current State

1. **EXPOSE_PURE misrouting (Bug 2 root cause):** `extract_computed_attributes()` returns all non-LITERAL computed attributes as a flat `list[ComputedAttributeData]`. EXPOSE_PURE attributes enter `_computed_attr_index` alongside FORMULA attributes, where they generate phantom channel names for nonexistent modules. When a binding resolves against one of these phantom channels, it wires to ENTRY_POINT instead of MODULE_OUTPUT.

2. **No `is_on_part_definition` field:** `ComputedAttributeData` lacks provenance tracking for whether the attribute lives on a PartDefinition vs. PartUsage. PartDef-level EXPOSE_PURE attributes have unscoped canonical names that can't resolve against instance-scoped registry keys — they must be filtered, but no field exists to filter them.

3. **Heuristic alias discovery (Step 3.6):** `_enrich_aliases_from_bindings()` (initialization.py:297-343) scans CalcUsage bindings for parameter names that differ from aggregation attribute names and adds the parameter names as aliases. This is semantically wrong — the alias relationship should come from the `:>>` CHAIN redefinition structure, not from incidental parameter naming.

4. **CHAIN alias production is partial:** The hierarchy resolver currently appends CHAIN redef aliases to `AggregationExpressionData.aliases` (a `list[str]`) at extraction time (hierarchy_resolver.py:535-544). These are not first-class `ChannelAlias` objects with provenance, scoping, or the interface needed for OutputRegistry registration.

5. **Virtual binding rewrite only handles bare names:** `_rewrite_virtual_bindings()` (initialization.py:238-294) only matches bindings with bare-name source_paths (no `.` or `::`). Spike 1 showed zero bare-name bindings across 94 bindings in 3 models — the current matching logic is dead code. Real bindings use SYSML_QN (`::`) or DOTTED (`.`) format.

6. **`find_instance_paths_for_partdef()` not factored out:** The logic to derive dotted instance paths from virtual CalcUsage parent QNs is inlined in `_scope_aggregation_expressions()` (initialization.py:346-406). CHAIN alias construction needs the same logic.

7. **Step ordering:** Aggregation scoping (Step 4.7) runs after design attribute extraction (Step 4) and computed attribute extraction (Step 4.5), but it depends only on hierarchy data (Step 3.5) and calc_usages (Step 3). It should be co-located with hierarchy extraction.

### Desired Outcome

- `extract_computed_attributes()` separates EXPOSE_PURE into `ChannelAlias` objects, returning a 2-tuple: `(list[ComputedAttributeData], list[ChannelAlias])`
- `ComputedAttributeData` has `is_on_part_definition: bool` for PartDef-level filtering
- CHAIN redefinitions produce scoped `ChannelAlias` objects with instance-path prefixes
- `find_instance_paths_for_partdef()` is a shared utility
- `_rewrite_virtual_bindings()` handles CHAIN overrides with leaf extraction from SYSML_QN and DOTTED formats
- Step 3.6 is removed (after diagnostic validation)
- Step 4.7 is merged into Step 3.5
- All alias data flows as `list[ChannelAlias]` through the pipeline, ready for OutputRegistry registration in Item 3

---

## Scope

### In Scope

**Phase A (Item 2a): ChannelAlias Producers**

1. Add `is_on_part_definition: bool` field to `ComputedAttributeData` in `extraction/data_models.py`
2. Populate `is_on_part_definition` at extraction time in `computed_attribute_extractor.py` using `SysideAdapter.is_instance(owning_element, "PartDefinition")`
3. Modify `extract_computed_attributes()` to return `tuple[list[ComputedAttributeData], list[ChannelAlias]]` — EXPOSE_PURE attributes produce `ChannelAlias` objects instead of remaining in the ComputedAttributeData list
4. EXPOSE_PURE `ChannelAlias` construction: `canonical_name` from `references` field (`f"{references[1].name}.{references[0].name}"`), NOT `expression_text`; filter PartDef-level via `is_on_part_definition`; scope alias keys with `owning_part_qn.split("__")[-1]`
5. Extract `find_instance_paths_for_partdef()` as a shared utility from `_scope_aggregation_expressions()` logic
6. CHAIN redef `ChannelAlias` production in hierarchy resolver or initialization: filter bare CAS codes (`"." not in redef.source_path`); scope both alias_name and canonical_name with instance_path prefix (dotted, prefix-stripped)
7. Update `_extract_and_filter_computed_attributes()` to handle the new return type
8. Thread `list[ChannelAlias]` through `PipelineContext` for downstream consumption

**Phase B (Item 2b): Virtual Binding Rewrite Enhancement + Step Consolidation**

9. Modify `_rewrite_virtual_bindings()`: add CHAIN override support with leaf extraction from SYSML_QN (`source_path.rsplit("::", 1)[-1]`) and DOTTED (`source_path.rsplit(".", 1)[-1]`) formats; CHAIN override rewrites `binding.source_path = matched.source_path`
10. Move aggregation scoping from Step 4.7 into Step 3.5 (scoping depends on hierarchy data, not on downstream steps)
11. Diagnostic-gated removal of `_enrich_aliases_from_bindings()` (Step 3.6): write a committed test proving all Step 3.6 aliases are a subset of CHAIN-derived aliases, then remove

### Out of Scope

- Building or wiring the OutputRegistry into the pipeline (Item 3)
- Modifying the backtracker resolution logic (Item 3)
- Expression compiler changes (none needed)
- Graph builder changes (Item 4)
- Removing `AggregationExpressionData.aliases` field (Item 4 cleanup — retained for backward compat during transition)

### Edge Cases & Considerations

- **EXPOSE_PURE with < 2 references:** Skip with warning. The `references` field may have fewer entries for degenerate expressions. Log and exclude.
- **PartDef-level EXPOSE_PURE filtering:** Spike 8 confirmed PartDef EXPOSE_PURE canonical names are unscoped (e.g., `"component_cost.total_cost"` without instance prefix). These can't match instance-scoped registry keys, so they MUST be filtered via `is_on_part_definition=True`.
- **Bare CAS codes in CHAIN redefs:** Spike 6 found 13 bare CAS code redefs (e.g., `CAS220101`) in solar_battery out of 54 total CHAIN redefs. These have no `.` in `source_path` and are not channel references — they must be filtered.
- **Instance path derivation:** `instance_path` from `ScopedAggregationData` uses `__` separator. For dotted CHAIN alias scoping, convert via `".".join(instance_path.split("__")[1:])` (strip design PartDef prefix, replace `__` with `.`).
- **`_rewrite_virtual_bindings()` behavior change:** The matching logic changes from "bare name only" to "leaf name from SYSML_QN or DOTTED format." This is a functional behavior change (not purely additive) — Gate 2b is critical.
- **Step 3.6 removal safety:** The diagnostic test MUST pass before removal. If any Step 3.6 alias is NOT produced by CHAIN redefs, that's a blocker requiring investigation.

---

## Requirements

### Functional Requirements

> Requirements below are from the epic unless marked [INFERRED].

**Phase A: ChannelAlias Producers**

1. **FR-1**: `ComputedAttributeData` MUST have an `is_on_part_definition: bool` field, populated at extraction time from the SysIDE AST.

2. **FR-2**: `extract_computed_attributes()` MUST return `tuple[list[ComputedAttributeData], list[ChannelAlias]]`. EXPOSE_PURE classified attributes MUST produce `ChannelAlias` objects. During the transition period (Items 2-3), EXPOSE_PURE remains in the `ComputedAttributeData` list for backward compatibility with the existing backtracker's `_computed_attr_index`. EXPOSE_PURE is removed from the CAD list in Item 4 after the old index is deleted. (Note: the target design prohibits EXPOSE_PURE in the *index*, not the *list* — see 08_algorithm_revised.md Section 5.)

3. **FR-3**: EXPOSE_PURE `ChannelAlias.canonical_name` MUST be constructed from `references[1].name` + `"."` + `references[0].name`. `expression_text` MUST NOT be used (SysIDE produces `".(component_cost)"`, not a parseable dotted key).

4. **FR-4**: EXPOSE_PURE attributes where `is_on_part_definition=True` MUST be filtered out (not converted to aliases). Only PartUsage-level EXPOSE_PURE attributes produce aliases.

5. **FR-5**: EXPOSE_PURE `ChannelAlias.alias_name` MUST be the bare `python_name` (e.g., `"total_capex"`). Scoping with the owning part's short name (`f"{owning_part_qn.split('__')[-1]}.{alias_name}"`) happens at Phase 3 OutputRegistry registration (Item 3), not at production time. This matches the C2 resolution in `spec_review_synthesis.md` and the target design (08_algorithm_revised.md Section 5 production vs Section 12 Phase 3 registration). The `source` field MUST be `"expose_pure"`.

6. **FR-6**: EXPOSE_PURE with fewer than 2 entries in `references` MUST be skipped with a `logger.warning()`.

7. **FR-7**: A shared utility `find_instance_paths_for_partdef(owning_part_qn, calc_usages)` MUST be extracted from the current `_scope_aggregation_expressions()` logic, returning design-prefix-stripped, dot-separated instance paths.

8. **FR-8**: `:>>` CHAIN redefinitions MUST produce `ChannelAlias` objects with `source="redefinition"`. CHAIN redefs where `"." not in redef.source_path` MUST be filtered out (bare CAS codes).

9. **FR-9**: CHAIN `ChannelAlias` alias_name and canonical_name MUST both be scoped with instance_path prefix (dotted, design-prefix-stripped via `find_instance_paths_for_partdef()`): `f"{instance_path}.{redef.attribute_name}"` / `f"{instance_path}.{redef.source_path}"`.

10. **FR-10**: `_extract_and_filter_computed_attributes()` MUST be updated to handle the new 2-tuple return and thread `list[ChannelAlias]` to `PipelineContext`.

11. **FR-11**: [INFERRED] `PipelineContext` MUST have a new field `channel_aliases: list[ChannelAlias]` to carry alias data downstream to Item 3's OutputRegistry construction.

**Phase B: Virtual Binding Rewrite + Step Consolidation**

12. **FR-12**: `_rewrite_virtual_bindings()` MUST handle CHAIN overrides (not just LITERAL). For CHAIN overrides, rewrite `binding.source_path = matched.source_path` (do not change binding_type to LITERAL).

13. **FR-13**: `_rewrite_virtual_bindings()` MUST extract leaf names from SYSML_QN format (`source_path.rsplit("::", 1)[-1]`) and DOTTED format (`source_path.rsplit(".", 1)[-1]`). Bare-name fallback SHOULD be retained defensively.

14. **FR-14**: Aggregation scoping (current Step 4.7) MUST be moved into Step 3.5 (`_extract_hierarchy_and_rewrite_bindings()`). `_scope_aggregation_expressions()` SHOULD use the extracted `find_instance_paths_for_partdef()` utility.

15. **FR-15**: `_enrich_aliases_from_bindings()` (Step 3.6) MUST be removed, but ONLY after a committed diagnostic test confirms all aliases it produces are a subset of CHAIN-derived aliases from FR-8/FR-9.

16. **FR-16**: [INFERRED] The Step 3.5 function MUST return CHAIN aliases alongside `HierarchyExtractionResult`, either by extending the return type or adding a field to `HierarchyExtractionResult`.

---

## Acceptance Criteria

### Core Functionality

- [ ] `ComputedAttributeData.is_on_part_definition` exists and is correctly set for PartDef vs PartUsage elements
- [ ] `extract_computed_attributes()` returns 2-tuple; EXPOSE_PURE appears in BOTH lists (CAD for backward compat, ChannelAlias for OutputRegistry)
- [ ] EXPOSE_PURE on e2e_attr_expr `total_capex` produces `ChannelAlias(alias_name="...", canonical_name="component_cost.total_cost", source="expose_pure")`
- [ ] EXPOSE_PURE on solar_battery PartDef `misc_hardware_cost` is FILTERED via `is_on_part_definition`
- [ ] `:>>` CHAIN redefs on solar_battery produce 41 `ChannelAlias` objects (Spike 8 count)
- [ ] Bare CAS code CHAIN redefs (13 in solar_battery) are filtered out
- [ ] CHAIN aliases have instance-path-scoped alias_name and canonical_name
- [ ] `_rewrite_virtual_bindings()` handles CHAIN override with SYSML_QN leaf extraction
- [ ] `_rewrite_virtual_bindings()` handles CHAIN override with DOTTED leaf extraction
- [ ] Step 3.6 diagnostic test passes: all `_enrich_aliases_from_bindings()` aliases are subset of CHAIN aliases
- [ ] Step 3.6 removed after diagnostic passes
- [ ] Step 4.7 merged into Step 3.5
- [ ] `PipelineContext.channel_aliases` carries alias data

### Unit Tests (synthetic, fast)

- [ ] CHAIN redef with `"."` in source_path produces ChannelAlias
- [ ] CHAIN redef with `"CAS220101"` (no dot) is filtered out
- [ ] EXPOSE_PURE on PartDef (`is_on_part_definition=True`) is filtered out
- [ ] EXPOSE_PURE on PartUsage (`is_on_part_definition=False`) produces ChannelAlias with correct `canonical_name` from `references`
- [ ] EXPOSE_PURE with < 2 references is skipped with warning
- [ ] `_rewrite_virtual_bindings()` CHAIN override with SYSML_QN format
- [ ] `_rewrite_virtual_bindings()` CHAIN override with DOTTED format
- [ ] `find_instance_paths_for_partdef()` returns correct dotted paths

### Quality & Integration

- [ ] Existing tests pass: `uv run pytest tests/`
- [ ] Gate 2a: `uv run pytest tests/unit/test_computed_attribute_extractor.py tests/integration/ -v`
- [ ] Gate 2b: `uv run pytest tests/unit/test_rewrite_virtual_bindings.py tests/integration/ -v`
- [ ] `uv run mypy src/` passes (type annotations correct for 2-tuple return)

---

## Implementation Notes

### Item 1 Verification (Complete)

Item 1 deliverables verified against epic contract:

| Component | Epic Contract | Actual | Status |
|-----------|--------------|--------|--------|
| `ChannelAlias` fields | `alias_name`, `canonical_name`, `owning_part_qn`, `source` | Matches exactly | OK |
| `ChannelAlias` type | `@dataclass` | Pydantic `BaseModel` | Acceptable — consistent with project |
| `OutputRegistry.register()` | `(canonical_channel, lookup_keys)` | Matches | OK |
| `OutputRegistry.register_alias()` | Assert canonical exists | Warns + skips (documented) | OK — spec allows |
| `OutputRegistry.resolve()` | Exact match, `str \| None` | Matches | OK |
| `derive_key_c()` | Utility on OutputRegistry | Static method | OK |
| `is_transitive_default()` | Method taking `attr` | Module-level fn taking `default_value` | OK — simpler |

No blocking deviations. Item 1 is ready for Item 2 to build on.

### Key Code Locations

| File | Current State | Item 2 Changes |
|------|--------------|----------------|
| `extraction/data_models.py:182-217` | `ComputedAttributeData` without `is_on_part_definition` | Add field |
| `extraction/computed_attribute_extractor.py:110-234` | Returns `list[ComputedAttributeData]` | Returns 2-tuple, EXPOSE_PURE -> ChannelAlias |
| `extraction/hierarchy_resolver.py:535-544` | CHAIN aliases on `AggregationExpressionData.aliases` | Produce `ChannelAlias` objects |
| `generation/initialization.py:238-294` | `_rewrite_virtual_bindings()` bare-name only | CHAIN override + leaf extraction |
| `generation/initialization.py:297-343` | `_enrich_aliases_from_bindings()` | Remove (after diagnostic) |
| `generation/initialization.py:346-406` | `_scope_aggregation_expressions()` | Extract utility, merge into 3.5 |
| `generation/initialization.py:409-571` | `build_pipeline_context()` | Update step ordering |

### Phasing

Phase A (Item 2a) is independently testable. Phase B (Item 2b) depends on Phase A for the CHAIN alias data to validate the Step 3.6 diagnostic. Both phases MUST pass their respective regression gates before proceeding to Item 3.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_output_registry_backtracker_redesign.md`
- **Design basis:** `.project/reports/08_algorithm_revised.md`
- **Item 1 code:** `src/sysml_codegen/core/models.py`, `src/sysml_codegen/core/output_registry.py`
- **Item 1 tests:** `tests/unit/test_output_registry.py`, `tests/integration/test_output_registry_smoke.py`, `tests/integration/test_bug2_regression.py`
- **Spike references:** Spike 1 (source_path formats), Spike 3 (references field), Spike 6 (CHAIN RHS formats, 13 bare CAS codes), Spike 8 (PartDef filter, 41 CHAIN aliases, instance_path format)
- **Spec review synthesis:** `.project/reports/spec_review_synthesis.md` (C1: 3-tuple return per Spec 04; C2: EXPOSE_PURE alias_name scoping)

---

**Next Steps:** After approval, proceed to `/_my_design`
