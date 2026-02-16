# Design: ChannelAlias Producers & Step Consolidation

**Status:** Complete
**Owner:** Reid Westwood
**Created:** 2026-02-13T22:58:30+00:00
**Branch:** cost-pattern
**Spec:** `.project/active/alias-producers-step-consolidation/spec.md`

---

## Overview

Modify the computed attribute extractor and hierarchy resolver to produce first-class `ChannelAlias` objects from EXPOSE_PURE attributes and `:>>` CHAIN redefinitions. Consolidate pipeline steps (merge 4.7 into 3.5, eliminate 3.6) and add CHAIN override support to virtual binding rewrite.

---

## Related Artifacts

- **Spec:** `.project/active/alias-producers-step-consolidation/spec.md`
- **Epic:** `.project/backlog/epic_output_registry_backtracker_redesign.md`
- **Design basis:** `.project/reports/08_algorithm_revised.md`
- **Spec review synthesis:** `.project/reports/spec_review_synthesis.md` (C1, C2 resolutions)
- **Item 1 code:** `core/models.py` (ChannelAlias), `core/output_registry.py` (OutputRegistry)

---

## Research Findings

### RF-1: Spec Review Synthesis Corrections

The spec review synthesis (`.project/reports/spec_review_synthesis.md`) identifies two cross-consistency issues that override our spec:

**C1: Return type (partial adoption)** — Spec 04 (authoritative) specifies `_extract_and_filter_computed_attributes()` returns a 3-tuple: `(list[ComputedAttributeData], list[ChannelAlias], list[CalcUsageData])`. The third element is synthetic CalcUsages, returned separately instead of appended in-place. However, `_extract_and_filter_computed_attributes()` does not currently create synthetic CalcUsages — that logic doesn't exist yet. **Item 2 adopts a 2-tuple** (first two elements only). The third element is deferred to when synthetic CalcUsage production is implemented. This is a C1 partial adoption — the 2-tuple→3-tuple upgrade is a backward-compatible addition of one element when needed.

**C2: EXPOSE_PURE alias_name scoping** — Spec 04 (authoritative) says `alias_name` should be **bare** at production (e.g., `"total_capex"`), with scoping applied at Phase 3 registration time (`f"{owning_short}.{alias.alias_name}"`). This matches the existing `ChannelAlias` model documentation (core/models.py:82-84). **Our spec FR-5 says to pre-scope — this is wrong per C2.** The design corrects this.

### RF-2: Graph Builder EXPOSE_PURE Dependency

The graph builder's `_build_attribute_resolution_map()` (graph_builder.py:696-701) iterates `computed_attrs` and processes EXPOSE_PURE attributes:

```python
elif ca.classification == ComputedAttributeClassification.EXPOSE_PURE:
    channel = _resolve_expose_pure(ca, calc_usage_names, output_catalog)
    if channel is not None:
        result[part_name][ca.python_name] = AttributeResolution(
            kind=AttributeResolutionKind.EXPOSE_ALIAS, channel_name=channel,
        )
```

`_resolve_expose_pure()` (graph_builder.py:613-653) uses `ca.references` to build a catalog lookup key. If EXPOSE_PURE is removed from `computed_attrs`, this code path breaks. This is Item 4 scope (graph builder simplification), not Item 2.

### RF-3: ExpressionRef Ordering (Confirmed)

Spike results confirm the `references` field ordering for EXPOSE_PURE attributes:

- `references[0].name` = output attribute name (e.g., `"total_cost"`) — the innermost/rightmost element
- `references[1].name` = CalcUsage instance name (e.g., `"component_cost"`) — the containing element

Formula: `canonical_name = f"{references[1].name}.{references[0].name}"` = `"component_cost.total_cost"`

The `expression_text` field contains raw AST reconstruction (e.g., `".(component_cost)"`) which is NOT a parseable dotted path. Never use it for canonical name construction.

### RF-4: Existing Test Patterns

Tests use mock AST elements with `SysideAdapter.is_instance()` monkeypatching. Key patterns from `test_computed_attribute_extraction.py`:

- Mock classes: `MockOperatorExpression`, `MockFeatureReferenceExpression`, `MockAttributeUsage`, `MockPartElement`
- `TYPE_MAP` dict maps mock class names to SysML type strings
- `mock_syside_adapter` fixture patches `SysideAdapter.is_instance` in all modules that use it
- Factory functions: `_make_computed_attr()`, `_make_refs()`, `_make_literal_redef_member()`
- Phase-based test organization (data models, classification logic, compilation, integration)

For hierarchy tests (`test_hierarchy_resolver.py`): `_make_chain_redef_member()`, `_make_deep_path_redef_member()` factories.

For pipeline tests (`test_hierarchy_pipeline.py`): `_make_virtual_calc_usage()` factory with `is_template=False`, `owning_part_def_qn` set. No `test_rewrite_virtual_bindings.py` exists yet — ready to create.

### RF-5: Instance Path Derivation Logic

Current logic in `_scope_aggregation_expressions()` (initialization.py:346-406):

- **Strategy 1 (Direct):** Virtual CalcUsages on same PartDef → parent QN from `qn.rsplit("__", 1)[0]`
- **Strategy 2 (Child-walk):** Match PartDef's child PartUsage names against CalcUsage QN segments

Both strategies produce `__`-separated instance paths (e.g., `"SolarBatteryDesign__solar_battery_plant__solar_array"`). For CHAIN alias scoping, convert to dotted with design prefix stripped: `".".join(path.split("__")[1:])` → `"solar_battery_plant.solar_array"`.

### RF-6: CHAIN Alias Production Location

The hierarchy resolver is a pure extraction module — it doesn't have access to `calc_usages` needed for instance path scoping. CHAIN alias production MUST happen in initialization.py where both `hierarchy_data.redefinitions` and `calc_usages` are available.

The existing BF-7 alias logic (hierarchy_resolver.py:535-544) appends `list[str]` aliases to `AggregationExpressionData.aliases`. This logic can remain (backward compat) while a new function produces proper `ChannelAlias` objects in initialization.py.

### RF-7: Backtracker and Computed Attributes

The backtracker only indexes FORMULA attributes in `_computed_attr_index` (dependency_backtracker.py:146-149). EXPOSE_PURE is already filtered out. The aggregation index (lines 189-197) reads `agg.expression.aliases` for BF-7 alias registration. Neither depends on EXPOSE_PURE being in the `computed_attrs` list — only the graph builder does (RF-2).

### RF-8: Only One Pipeline Caller

`extract_computed_attributes()` has exactly one pipeline caller: `_extract_and_filter_computed_attributes()` in initialization.py:188. Test files also call it directly. Changing the return type is safe — only one integration point to update.

---

## Design Decision: EXPOSE_PURE Retention in ComputedAttributeData List

### Context

Spec FR-2 says EXPOSE_PURE "MUST NOT appear in the ComputedAttributeData list." But the graph builder's `_build_attribute_resolution_map()` (graph_builder.py:696-701) iterates EXPOSE_PURE entries in that list to resolve FORMULA module inputs wired through EXPOSE aliases. Removing them now would break graph builder resolution — a regression.

### Options

**Option A: Keep EXPOSE_PURE in both places (Recommended)**
- EXPOSE_PURE stays in `ComputedAttributeData` list (graph builder continues to work)
- EXPOSE_PURE also produces `ChannelAlias` objects (new, for OutputRegistry in Item 3)
- Item 4 removes EXPOSE_PURE from the list when graph builder is updated to use OutputRegistry
- Zero regressions, purely additive change

**Option B: Remove EXPOSE_PURE from list, fix graph builder now**
- Follows FR-2 exactly
- Requires updating `_build_attribute_resolution_map()` and `_resolve_expose_pure()` to use `list[ChannelAlias]`
- Scope creep into Item 4 territory
- Higher regression risk

### Decision

**Option A** (approved by user). Rationale:

The desired-state algorithm (`08_algorithm_revised.md`, Section 5, lines ~557-559) specifies that EXPOSE_PURE attrs "exist ONLY as aliases in the OutputRegistry" and Step 4.5 output is "ComputedAttributeData list (FORMULA only)." However, the graph builder functions `_resolve_expose_pure()` and `_build_attribute_resolution_map()` are current-state artifacts that don't exist in the desired state — they're replaced by OutputRegistry resolution in Items 3-4. Removing EXPOSE_PURE from the list before the graph builder is rewritten (Item 4) would break FORMULA module input wiring through EXPOSE aliases.

Item 2 is explicitly characterized in the epic as "purely additive" (no existing behavior modified). The graph builder rewrite is Item 4 scope. Producing `ChannelAlias` objects is the primary deliverable — that's what Item 3 needs to populate the OutputRegistry. Item 4 removes EXPOSE_PURE from the `ComputedAttributeData` list when it replaces these graph builder functions.

---

## Proposed Design

### Architecture Overview

```
Phase A: ChannelAlias Producers
  ┌─────────────────────────────────┐
  │ extract_computed_attributes()   │ Returns (list[CAD], list[ChannelAlias])
  │ computed_attribute_extractor.py │ EXPOSE_PURE → ChannelAlias (bare alias_name)
  │ + is_on_part_definition field   │ EXPOSE_PURE also stays in CAD list (compat)
  └─────────────┬───────────────────┘
                │
  ┌─────────────▼───────────────────┐
  │ _build_chain_aliases()          │ New function in initialization.py
  │ + find_instance_paths_for_      │ CHAIN redefs → scoped ChannelAlias
  │   partdef() utility             │ Filters bare CAS codes
  └─────────────┬───────────────────┘
                │
  ┌─────────────▼───────────────────┐
  │ PipelineContext                 │ New field: channel_aliases
  │ Carries both alias sources     │ EXPOSE_PURE + CHAIN aliases merged
  └─────────────────────────────────┘

Phase B: Rewrite Enhancement + Step Consolidation
  ┌─────────────────────────────────┐
  │ _rewrite_virtual_bindings()     │ CHAIN override support
  │ Leaf extraction from ::/.       │ Not just bare-name matching
  └─────────────────────────────────┘
  ┌─────────────────────────────────┐
  │ Step consolidation              │ 4.7 → 3.5, 3.6 removed
  └─────────────────────────────────┘
```

### Component 1: `is_on_part_definition` Field

**File:** `src/sysml_codegen/extraction/data_models.py`

Add `is_on_part_definition: bool = False` to `ComputedAttributeData` after the `compiled_expression` field (line 214). Default `False` (PartUsage) because that's the common case.

```python
compiled_expression: str | None = None
is_on_part_definition: bool = False  # True if owning element is a PartDefinition
```

**Population:** In `extract_computed_attributes()` (computed_attribute_extractor.py), detect using `SysideAdapter.is_instance(part_element, "PartDefinition")` at the top of the function (before the loop), store as a local variable, and pass to each `ComputedAttributeData` constructor:

```python
# At function top, after building context (line ~134)
is_part_def = SysideAdapter.is_instance(part_element, "PartDefinition")

# In constructor (line ~219-231), add:
is_on_part_definition=is_part_def,
```

This is a static check per `part_element` — all attributes on the same element share the same value.

Note: the existing code calls `_sanitize_name(attr_name)` inline in the `ComputedAttributeData` constructor (line 222). To avoid duplicating this call for alias construction, extract it to a local variable before the constructor:

```python
python_name = _sanitize_name(attr_name)
```

Then use `python_name` in both the `ComputedAttributeData(python_name=python_name, ...)` constructor and the `ChannelAlias(alias_name=python_name, ...)` constructor. This keeps the alias_name consistent with `ca.python_name` by construction.

### Component 2: `extract_computed_attributes()` Return Type Change

**File:** `src/sysml_codegen/extraction/computed_attribute_extractor.py`

Change return type from `list[ComputedAttributeData]` to `tuple[list[ComputedAttributeData], list[ChannelAlias]]`.

**Internal flow:**
1. Initialize two lists: `results: list[ComputedAttributeData]` and `aliases: list[ChannelAlias]`
2. For each attribute classified as EXPOSE_PURE:
   a. **Still append** to `results` (graph builder compat per Design Decision above)
   b. If `is_part_def`: skip alias production (PartDef-level, unscoped canonical names)
   c. If `len(refs) < 2` after filtering: log warning, skip alias production
   d. Build `ChannelAlias` and append to `aliases`
3. Return `(results, aliases)`

**EXPOSE_PURE → ChannelAlias construction** (new code block after the existing `results.append()` at line 231):

```python
if classification == ComputedAttributeClassification.EXPOSE_PURE and not is_part_def:
    if len(refs) < 2:
        logger.warning(
            "EXPOSE_PURE '%s' on '%s' has fewer than 2 references, "
            "skipping alias production: refs=%s",
            attr_name, part_name, [r.name for r in refs],
        )
    else:
        # Classify refs by role, not index position.
        # Index-based access (refs[0], refs[1]) relies on ordering from
        # extract_feature_refs() which is an implementation detail. Instead,
        # use calc_usage_names to identify the instance ref — same proven
        # pattern as graph_builder._resolve_expose_pure() (line 630-634).
        instance_name = None
        output_name = None
        for ref in refs:
            if ref.name in calc_usage_names:
                instance_name = ref.name
            else:
                output_name = ref.name

        if instance_name and output_name:
            # Bare alias_name per C2 resolution — scoping at Phase 3 registration
            aliases.append(ChannelAlias(
                alias_name=python_name,  # already sanitized (see Component 1)
                canonical_name=f"{instance_name}.{output_name}",
                owning_part_qn=part_qn,
                source="expose_pure",
            ))
```

**Import addition:** Add `from sysml_codegen.core.models import ChannelAlias` at the top.

### Component 3: `_extract_and_filter_computed_attributes()` Update

**File:** `src/sysml_codegen/generation/initialization.py`

Update to handle the 2-tuple return from `extract_computed_attributes()`:

```python
# Line 188 changes from:
computed = extract_computed_attributes(None, part_elem, calc_usage_names)
all_computed_attrs.extend(computed)

# To:
computed, expose_aliases = extract_computed_attributes(None, part_elem, calc_usage_names)
all_computed_attrs.extend(computed)
all_expose_aliases.extend(expose_aliases)
```

Initialize `all_expose_aliases: list[ChannelAlias] = []` before the loop.

**Return type:** Change from `list[ComputedAttributeData]` to `tuple[list[ComputedAttributeData], list[ChannelAlias]]`. Return `(all_computed_attrs, all_expose_aliases)`.

**Import:** Add `from sysml_codegen.core.models import ChannelAlias`.

### Component 4: `find_instance_paths_for_partdef()` Utility

**File:** `src/sysml_codegen/generation/initialization.py`

Extract from `_scope_aggregation_expressions()`. This function encapsulates both Strategy 1 (direct) and Strategy 2 (child-walk) instance path resolution.

```python
def find_instance_paths_for_partdef(
    owning_part_qn: str,
    calc_usages: list[CalcUsageData],
    part_usage_names: dict[str, set[str]] | None = None,
) -> list[str]:
    """Find dotted design instance paths for a PartDef.

    Derives instance paths from virtual CalcUsage parent QNs, strips
    the design PartDef prefix, and converts to dotted format.

    Strategy 1: Direct — virtual CalcUsages on same PartDef.
    Strategy 2: Child-walk — match PartDef's child PartUsage names
        against CalcUsage QN segments (handles PartDef/PartUsage naming
        differences, BF-6).

    Args:
        owning_part_qn: Qualified name of the PartDef.
        calc_usages: All calc usages (filters to virtual only).
        part_usage_names: Optional child PartUsage names by PartDef QN.

    Returns:
        Sorted list of dotted, design-prefix-stripped instance paths
        (e.g., "solar_battery_plant.solar_array").
    """
```

**Return format:** Dotted, design-prefix-stripped. This matches how callers use the result — the `08_algorithm_revised.md` pseudocode directly uses the return value in dotted expressions like `f"{instance_path}.{redef.attribute_name}"`. Returning `__`-separated paths would push conversion to every call site; returning dotted centralizes it.

**Logic** — extracted from `_scope_aggregation_expressions()` (initialization.py:361-397), with the dotted conversion applied internally:
1. Build `virtual_qns_by_partdef` index (virtual CalcUsages grouped by `owning_part_def_qn`)
2. Strategy 1: Direct match from `virtual_qns_by_partdef[owning_part_qn]` → `qn.rsplit("__", 1)[0]`
3. Strategy 2: If no direct match, child-walk using `part_usage_names`
4. Convert each `__`-separated path to dotted: `".".join(path.split("__")[1:])` — strips design PartDef prefix (segment 0), joins remaining with `.`
5. Return `sorted(dotted_paths)`

**Refactor `_scope_aggregation_expressions()`** to call this utility. Since `_scope_aggregation_expressions()` currently builds `ScopedAggregationData` with `__`-separated `instance_path`, and `ScopedAggregationData.module_eqn` constructs EQNs using `__` (data_models.py:362), the refactored caller must convert the dotted path back to `__`-separated for `ScopedAggregationData.instance_path`. This is a one-line conversion: `"__".join([segments[0]] + dotted.split("."))` where `segments[0]` is the design prefix. Alternatively, keep the raw `__`-separated set as an internal variable and convert to dotted only for the return value. The cleaner approach: the utility returns dotted, and `_scope_aggregation_expressions()` reconstructs the `__` form by prepending the design prefix. The design prefix is `owning_part_qn.split("__")[0]` (or the first segment of any matched CalcUsage QN).

**Simpler approach:** Since `_scope_aggregation_expressions()` is the only consumer that needs `__`-separated paths, and it already has the raw QN data, it can call `find_instance_paths_for_partdef()` for dotted paths and reconstruct `__`-separated for `ScopedAggregationData` internally. All other consumers (CHAIN alias construction) use dotted directly.

### Component 5: `_build_chain_aliases()` — CHAIN Redef → ChannelAlias

**File:** `src/sysml_codegen/generation/initialization.py`

New function that produces `ChannelAlias` objects from CHAIN redefinitions.

```python
def _build_chain_aliases(
    hierarchy_data: HierarchyExtractionResult,
    calc_usages: list[CalcUsageData],
) -> list[ChannelAlias]:
    """Build ChannelAlias objects from :>> CHAIN redefinitions.

    For each non-deep-path CHAIN redefinition on a PartDef, finds the
    design instance paths and produces scoped aliases.

    Filters:
    - Skip if "." not in redef.source_path (bare CAS codes like "CAS220101")
    - Skip deep-path redefinitions (those are design overrides, not aliases)

    Args:
        hierarchy_data: Extraction result with redefinitions.
        calc_usages: For instance path resolution.

    Returns:
        List of scoped ChannelAlias objects with source="redefinition".
    """
```

**Filters** (two fields on `RedefinitionData`, defined in data_models.py:232-254):
- `redef.is_deep_path` (bool, line 252): `True` when the redefinition targets a nested path like `:>> pv_module.wattage = 400.0`. These are design-level overrides that rewrite virtual bindings (Component 8), not channel aliases.
- `redef.source_path` (str, line 245): The RHS of a CHAIN redef (e.g., `"cost_model.total_cost"`). Bare CAS codes (e.g., `"CAS220101"`) have no `.` and are not channel references.

**Logic:**
1. Group CHAIN redefinitions by `owning_part_qn`
2. For each group:
   a. Call `find_instance_paths_for_partdef(owning_part_qn, calc_usages, hierarchy_data.part_usage_names)` to get dotted instance paths
   b. For each CHAIN redef in the group:
      - Filter: skip if `redef.is_deep_path` (design overrides, not aliases)
      - Filter: skip if `"." not in redef.source_path` (bare CAS codes)
      - For each instance path:
        - Convert to dotted: `dotted_path = ".".join(instance_path.split("__")[1:])`
        - Build `ChannelAlias`:
          - `alias_name = f"{dotted_path}.{redef.attribute_name}"`
          - `canonical_name = f"{dotted_path}.{redef.source_path}"`
          - `owning_part_qn = redef.owning_part_qn`
          - `source = "redefinition"`
3. Return all aliases

**Note:** The existing BF-7 alias logic in hierarchy_resolver.py:535-544 (appending to `AggregationExpressionData.aliases`) is LEFT IN PLACE for backward compatibility. The backtracker currently reads `agg.expression.aliases` for aggregation index registration (dependency_backtracker.py:189-197). This will be cleaned up in Item 4.

### Component 6: `PipelineContext` Update

**File:** `src/sysml_codegen/generation/initialization.py`

Add `channel_aliases` field to `PipelineContext`:

```python
# After aggregation_expressions field (line ~111)
channel_aliases: list[ChannelAlias] = field(default_factory=list)
```

Import `ChannelAlias` from `sysml_codegen.core.models`.

### Component 7: `build_pipeline_context()` Step Reordering

**File:** `src/sysml_codegen/generation/initialization.py`

Updated step sequence:

```
Step 1:   Load models
Step 2:   Extract calc defs
Step 3:   Extract calc usages
Step 3.5: Extract hierarchy + rewrite bindings + scope aggregation + build CHAIN aliases
          (was: extract hierarchy + rewrite bindings only)
Step 4:   Extract design attributes
Step 4.5: Extract computed attributes + EXPOSE_PURE aliases
          (now returns 2-tuple)
Step 5:   Create parameter group deriver
Step 6:   Create backtracker
Step 6.5: Compile expressions
Step 7:   Build computation graph
```

**Concrete changes to `build_pipeline_context()`:**

1. **Step 3.5** — Update `_extract_hierarchy_and_rewrite_bindings()` to also:
   - Call `_scope_aggregation_expressions()` (moved from Step 4.7)
   - Call `_build_chain_aliases()` (new)
   - Return `tuple[HierarchyExtractionResult, list[ScopedAggregationData], list[ChannelAlias]]`

2. **Remove Step 3.6** — Delete the `_enrich_aliases_from_bindings()` call (lines 473-475), after diagnostic test passes

3. **Remove Step 4.7** — Delete the `_scope_aggregation_expressions()` call (line 486), now in Step 3.5

4. **Step 4.5** — Update to receive 2-tuple return:
   ```python
   computed_attrs, expose_aliases = _extract_and_filter_computed_attributes(...)
   ```

5. **Merge aliases** — Combine CHAIN aliases (from Step 3.5) and EXPOSE_PURE aliases (from Step 4.5):
   ```python
   all_channel_aliases = chain_aliases + expose_aliases
   ```

6. **Pass to PipelineContext:**
   ```python
   channel_aliases=all_channel_aliases,
   ```

### Component 8: `_rewrite_virtual_bindings()` Enhancement

**File:** `src/sysml_codegen/generation/initialization.py`

**Current behavior** (lines 283-293): Only matches bare-name bindings — if source_path has no `.` or `::`, looks up `(parent_path, source_path)` in override_index. Only handles LITERAL overrides.

**New behavior:**

1. **Leaf extraction** — Replace the bare-name-only check with leaf extraction:

```python
# Replace lines 283-293 with:
source = binding.source_path

# Extract leaf name from source_path
if "::" in source:
    leaf = source.rsplit("::", 1)[-1]
elif "." in source:
    leaf = source.rsplit(".", 1)[-1]
else:
    leaf = source  # bare name (defensive fallback)

key = (parent_path, leaf)
matched = override_index.get(key)

if matched:
    if matched.redefinition_type == RedefinitionType.LITERAL:
        binding.binding_type = BindingType.LITERAL
        binding.literal_value = matched.literal_value
        binding.source_path = None
        rewrite_count += 1
    elif matched.redefinition_type == RedefinitionType.CHAIN:
        binding.source_path = matched.source_path
        rewrite_count += 1
```

2. **Key change:** The matching logic changes from "bare name only" to "leaf name from any format." This is a behavioral change — Gate 2b is critical.

3. **LITERAL rewrite** — unchanged (binding_type → LITERAL, literal_value set, source_path cleared)

4. **CHAIN rewrite** — new: `binding.source_path = matched.source_path` (binding_type preserved, source_path updated to point to the overriding chain target)

### Component 9: Step 3.6 Diagnostic Test + Removal

**Approach:** Before removing `_enrich_aliases_from_bindings()`, write a committed integration test that validates all aliases it would produce are also produced by `_build_chain_aliases()`.

**Test file:** `tests/integration/test_step36_diagnostic.py`

```python
def test_step36_aliases_are_subset_of_chain_aliases():
    """All aliases from _enrich_aliases_from_bindings() are also in CHAIN aliases."""
    # Load solar_battery model
    # Run extraction + hierarchy + rewrite
    # Capture Step 3.6 aliases
    # Build CHAIN aliases via _build_chain_aliases()
    # Assert: every Step 3.6 alias has a corresponding CHAIN alias
```

If this test passes: remove `_enrich_aliases_from_bindings()` and its call in `build_pipeline_context()`.

If this test fails: investigate before removing — there may be edge cases Step 3.6 covers that CHAIN doesn't.

---

## Potential Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| `refs` ordering differs for some EXPOSE_PURE patterns | Medium | Use instance/output classification loop (like graph builder), not index-based access |
| `_rewrite_virtual_bindings()` leaf extraction matches wrong override | Medium | Gate 2b regression test on all 4 models |
| Step 3.6 diagnostic reveals uncovered alias case | Low | Investigation before removal (not blind deletion) |
| CHAIN alias count differs from Spike 8's 41 | Low | Instance path resolution is extracted from proven `_scope_aggregation_expressions()` logic |
| `find_instance_paths_for_partdef()` produces different paths than inline version | Low | Refactoring is mechanical — inline logic moves unchanged to utility function |

---

## Integration Strategy

Item 2 is **purely additive** — no existing behavior changes:

1. EXPOSE_PURE stays in `ComputedAttributeData` list (graph builder compat)
2. EXPOSE_PURE also produces `ChannelAlias` (new data flow)
3. CHAIN redefs continue appending to `AggregationExpressionData.aliases` (backward compat)
4. CHAIN redefs also produce `ChannelAlias` (new data flow)
5. `PipelineContext.channel_aliases` carries both sources downstream
6. `_rewrite_virtual_bindings()` enhancement is the only behavioral change
7. Step 3.6 removal is gated on diagnostic test

Item 3 consumes `PipelineContext.channel_aliases` to populate the OutputRegistry.
Item 4 removes the backward-compat dual data flows.

---

## Validation Approach

### Unit Tests (synthetic, fast)

**New file: `tests/unit/test_alias_producers.py`**

Using existing mock patterns (MockPartElement, mock_syside_adapter fixture):

1. **EXPOSE_PURE alias production:**
   - PartUsage EXPOSE_PURE with 2 refs → ChannelAlias with bare alias_name, correct canonical_name
   - PartDef EXPOSE_PURE (is_on_part_definition=True) → filtered, no ChannelAlias
   - EXPOSE_PURE with < 2 refs → warning logged, no ChannelAlias
   - EXPOSE_PURE stays in ComputedAttributeData list (dual output)

2. **is_on_part_definition field:**
   - PartDef element → `is_on_part_definition=True` on all extracted attrs
   - PartUsage element → `is_on_part_definition=False`

3. **CHAIN alias production:**
   - CHAIN redef with `.` in source_path → ChannelAlias with scoped names
   - CHAIN redef with bare CAS code → filtered
   - Deep-path CHAIN redef → filtered

4. **find_instance_paths_for_partdef():**
   - Strategy 1 (direct CalcUsage match) → correct paths
   - Strategy 2 (child-walk) → correct paths
   - No match → empty list

**New file: `tests/unit/test_rewrite_virtual_bindings.py`**

5. **CHAIN override support:**
   - SYSML_QN format source_path → leaf extracted, matched, source_path rewritten
   - DOTTED format source_path → leaf extracted, matched, source_path rewritten
   - LITERAL override → existing behavior (binding_type changed)
   - No match → binding unchanged

### Integration Tests

**New file: `tests/integration/test_step36_diagnostic.py`**

6. Step 3.6 subset validation on solar_battery model

**Existing: `tests/integration/test_bug2_regression.py`**

7. Bug 2 xfail test continues to xfail (fix comes in Item 3)

### Regression Gates

| Gate | Command | Critical Check |
|------|---------|---------------|
| Gate 2a | `uv run pytest tests/` | + `uv run pytest tests/unit/test_alias_producers.py tests/integration/ -v` |
| Gate 2b | `uv run pytest tests/` | + `uv run pytest tests/unit/test_rewrite_virtual_bindings.py tests/integration/ -v` |

---

**Next Step:** After approval → `/_my_plan` for implementation planning, then `/_my_implement`
