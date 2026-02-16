# Design: Cut-over, Cleanup, and E2E Validation

**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-02-14 20:45 UTC
**Branch:** cost-pattern
**Commit:** 157ba47

## Overview

Complete the OutputRegistry cut-over by removing the backtracker's 5 old indexes and 7-strategy cascade, simplifying the graph builder to use OutputRegistry for channel validation, migrating 39 tests, and performing E2E validation with YAML diffing against baselines.

## Related Artifacts

- **Spec:** `.project/active/cutover-validation/spec.md`
- **Epic:** `.project/backlog/epic_output_registry_backtracker_redesign.md` (Item 4)
- **Item 3 design:** `.project/active/backtracker-integration/design.md`
- **Test migration audit:** `.project/active/backtracker-integration/test_migration_audit.md`
- **OutputRegistry:** `src/sysml_codegen/core/output_registry.py`
- **Backtracker:** `src/sysml_codegen/analysis/dependency_backtracker.py`
- **Graph builder:** `src/sysml_codegen/resolution/graph_builder.py`
- **Initialization:** `src/sysml_codegen/generation/initialization.py`
- **Baseline YAML:** `tests/fixtures/baseline_yaml/` (4 files)

**Note:** Line numbers in this document are from commit 157ba47 (cost-pattern branch HEAD at design time). Verify against actual HEAD before implementation begins, as ongoing work may shift line numbers.

## Research Findings

### Critical Finding: Graph Builder Only Uses `channel_name`

The output catalog stores `(module_type, channel_name, field_name)` tuples, but **only `channel_name` (index 1) is ever read** by any consumer. Analysis of all 9 read sites:

| Site | Line | Method | Fields Used |
|------|------|--------|-------------|
| 1 | 644-652 | `_resolve_expose_pure()` | `_, channel_name, _ = entry` |
| 2 | 698 | `_build_attribute_resolution_map()` | via `_resolve_expose_pure()` |
| 3 | 920 | `_resolve_aggregation_input_channel()` | `any(v[1] == channel ...)` |
| 4 | 930-931 | `_resolve_aggregation_input_channel()` | `output_catalog[key][1]` |
| 5 | 1048 | `_build_aggregation_module()` | `any(v[1] == channel ...)` |
| 6 | 1055-1056 | `_build_aggregation_module()` | via `_resolve_aggregation_input_channel()` |
| 7 | 154-161 | `_build_pipeline_module()` | **NEVER USED** (declared, not referenced) |

- `module_type` (index 0): **never read** at any site
- `field_name` (index 2): **never read** at any site

**Implication**: This finding resolves the spec's FR-9 concern and the "Implementation Notes" discussion of "The `(module_type, channel_name, field_name)` Problem." Since only `channel_name` is consumed, no adapter or helper to derive `module_type`/`field_name` is needed. `OutputRegistry.resolve()` is a complete, direct replacement for every catalog read operation. The two `any(v[1] == channel ...)` iteration patterns become `channel in registry.canonical_channels` (O(1) set membership vs O(n) iteration).

### Backtracker State

**`_resolve_binding_via_registry()` (lines 691-753)**: Already implemented in Item 3. Handles:
- Direct `registry.resolve(source_path)` -> MODULE_OUTPUT
- REFERENCE secondary: leaf + parent scope via `_resolve_reference_via_registry()`
- Design attribute fallback via existing `_resolve_to_design_attribute()`
- Warning on unresolved bindings

**Self-reference guard (lines 712-719)**: Already adapted for channel-based resolution (`channel.rsplit("__", 1)[0]` comparison).

**Parallel validation (lines 755-776, insertions at 480-481, 511-512, 617-619)**: `_compare_with_registry()` + 3 insertion points. All to be removed.

**`_usage_by_name` (lines 214-230)**: Used by `find_required_modules()` at line 330 as fallback when `_output_catalog.get(target)` misses on dotted-format targets. Must be retained.

### `_build_pipeline_module()` Does Not Use the Catalog

Verified at `graph_builder.py:1212-1326`: despite receiving `output_catalog` as a parameter, the function body **never references it**. It uses `binding_resolutions` as the single source of truth (ADR-003 Phase 7). The parameter can simply be removed.

### Graph Builder Catalog Usage Patterns

Two distinct patterns for replacing:

**Pattern A -- Key lookup** (2 sites): `output_catalog.get(key)` or `output_catalog[key][1]`
- `_resolve_expose_pure()` line 644: `output_catalog.get(catalog_key)` -> extract `channel_name`
- `_resolve_aggregation_input_channel()` line 930: `output_catalog[catalog_key][1]`
- **Replacement**: `registry.resolve(key)` -- direct, returns channel name or None

**Pattern B -- Value iteration** (2 sites): `any(v[1] == channel for v in output_catalog.values())`
- `_resolve_aggregation_input_channel()` line 920
- `_build_aggregation_module()` line 1048
- **Replacement**: `channel in registry.canonical_channels` -- O(1) set lookup via existing `OutputRegistry.canonical_channels` property (`core/output_registry.py:161-164`)

### Constructor Parameter Analysis

After cut-over, the backtracker constructor (`dependency_backtracker.py:119-137`) needs:

| Parameter | Keep/Remove | Reason |
|-----------|-------------|--------|
| `all_usages` | Keep | Core input |
| `calc_defs` | Keep | CalcDef lookup (DFS traversal) |
| `design_attributes` | Keep | `_resolve_to_design_attribute()` still uses this |
| `computed_attributes` | **Remove** | Only used for `_computed_attr_index` construction |
| `aggregation_data` | **Remove** | Only used for `_aggregation_output_index` construction |
| `output_registry` | Keep, **make required** | Sole resolution path |

**Wait -- verify `computed_attributes` and `aggregation_data` removability.** Let me check if they're used anywhere else in the backtracker beyond index construction.

After checking: `computed_attributes` is only used in the constructor (lines 144-162) for building `_computed_attr_index`. `aggregation_data` is only used in the constructor (lines 163-205) for building `_aggregation_output_index`. Both can be removed once the indexes are removed.

### `find_required_modules()` Impact

`find_required_modules()` (lines 274-344) currently uses:
1. `self._output_catalog.get(target)` at line 325 -- primary lookup
2. `self._usage_by_name.get(instance_name)` at line 330 -- fallback

After removing `_output_catalog`, `_usage_by_name` becomes the sole lookup. This is functionally equivalent for the common case: targets are always dotted format like `"net_electric.p_net"` (per docstring and all observed callers). The `_output_catalog.get(target)` primary lookup and the `_usage_by_name.get(instance_name)` fallback both resolve to the same `CalcUsageData` because they're populated from the same data -- the catalog just does it without parsing the dotted format.

---

## Proposed Design

### High-Level Architecture

```
                    Item 4 Cut-over
                    ===============

BEFORE (dual-path):
  ┌─────────────────────────────────────────────┐
  │  Backtracker constructor                     │
  │  5 indexes: _computed_attr_index,            │
  │  _aggregation_output_index, _output_catalog, │
  │  _design_attr_binding_index, _usage_by_name  │
  └──────────────┬──────────────────────────────┘
                 │
  ┌──────────────▼──────────────────────────────┐
  │  _trace_dependencies() dual-path            │
  │  OLD: inline checks + cascade (authoritative)│
  │  NEW: _resolve_binding_via_registry() (shadow)│
  │  _compare_with_registry() at 3 points       │
  └──────────────┬──────────────────────────────┘
                 │
  ┌──────────────▼──────────────────────────────┐
  │  Graph builder                               │
  │  Builds its own output_catalog               │
  │  3 construction functions                    │
  └─────────────────────────────────────────────┘

AFTER (sole registry path):
  ┌─────────────────────────────────────────────┐
  │  Backtracker constructor                     │
  │  1 index: _usage_by_name (find_required_modules only)│
  │  Required: output_registry                   │
  └──────────────┬──────────────────────────────┘
                 │
  ┌──────────────▼──────────────────────────────┐
  │  _trace_dependencies() sole path            │
  │  _resolve_binding_via_registry() only       │
  │  No inline checks, no cascade               │
  └──────────────┬──────────────────────────────┘
                 │
  ┌──────────────▼──────────────────────────────┐
  │  Graph builder                               │
  │  Receives OutputRegistry                     │
  │  registry.resolve() + .canonical_channels    │
  └─────────────────────────────────────────────┘
```

### Component 1: Step 3.6 Diagnostic

**Purpose:** Determine if Step 3.6 (`_enrich_aliases_from_bindings()`) is dead code.

**Location:** Run as a one-time diagnostic script or test before starting implementation.

**Approach:**
1. Temporarily skip the `_enrich_aliases_from_bindings()` call in `build_pipeline_context()` (line 781-783)
2. Run `uv run pytest tests/integration/test_parallel_validation.py -v`
3. If zero divergences on all 4 models: Step 3.6 is dead, safe to remove
4. If divergences: log which bindings diverge, retain Step 3.6

**Implementation**: Write a small integration test that:
```python
def test_step36_is_dead_code():
    """Verify Step 3.6 aliases are redundant with CHAIN aliases."""
    # Build pipeline context normally (includes Step 3.6)
    ctx_with = build_pipeline_context([model_path])

    # Build without Step 3.6 (monkeypatch _enrich_aliases_from_bindings to no-op)
    # Compare binding_resolutions
```

**Outcome**: Documented decision. If dead, `_enrich_aliases_from_bindings()` and its call site are removed in the dead code cleanup sub-task.

### Component 2: Backtracker Cut-over

**Purpose:** Remove old indexes, cascade, inline checks, and parallel validation. Make `_resolve_binding_via_registry()` the sole path.

**Location:** `src/sysml_codegen/analysis/dependency_backtracker.py`

#### 2a. Constructor Changes

**Remove from constructor:**
- `_computed_attr_index` construction (lines 144-162)
- `_aggregation_output_index` construction (lines 163-205)
- `_output_catalog` construction (lines 232-248)
- `_design_attr_binding_index` construction and `_build_design_attr_binding_index()` method (lines 250-254 + lines 1021-1058)
- `_resolve_target_to_qualified()` helper (lines 1085-1118, only used by `_build_design_attr_binding_index`)

**Retain in constructor:**
- `_usage_by_name` (lines 214-230) -- used by `find_required_modules()`
- `_usage_by_qualified` (line 210) -- used by `_trace_dependencies()` for DFS
- `self._output_registry = output_registry` (existing)

**Remove from parameter list:**
- `computed_attributes` -- only used for `_computed_attr_index`
- `aggregation_data` -- only used for `_aggregation_output_index`

**Make required:**
- `output_registry: OutputRegistry` -- no longer `| None = None`

**New constructor signature:**
```python
def __init__(
    self,
    all_usages: list[CalcUsageData],
    calc_defs: list,
    design_attributes: dict[Path, list[DesignAttributeData]] | None = None,
    output_registry: OutputRegistry,  # REQUIRED, was optional
):
```

**Import change:** Move `OutputRegistry` from TYPE_CHECKING to runtime import (it's now a required parameter, needs runtime access).

#### 2b. `_trace_dependencies()` Simplification

**Current flow** (lines 390-640, ~250 lines):
```
1. LITERAL -> ENTRY_POINT (lines 441-456)
2. Computed attr inline check (lines 459-482, ~24 lines)    ← REMOVE
   + parallel validation insertion #1 (lines 480-481)       ← REMOVE
3. Aggregation inline check (lines 484-513, ~30 lines)      ← REMOVE
   + parallel validation insertion #2 (lines 511-512)       ← REMOVE
4. _resolve_binding_to_usage() cascade (line 515)           ← REPLACE
5. Self-reference guard old path (lines 517-526)            ← REMOVE
6. If resolved: build channel -> MODULE_OUTPUT (lines 528-553) ← REMOVE
7. If not resolved: design_attr -> ENTRY_POINT (lines 554-616) ← REMOVE
   + parallel validation insertion #3 (lines 617-619)       ← REMOVE
```

**New flow** (~30 lines replacing ~200):
```
1. LITERAL/UNBOUND -> ENTRY_POINT (unchanged)
2. CHAIN/REFERENCE with source_path:
     resolution = self._resolve_binding_via_registry(binding, usage)
     self._binding_resolutions[mapping_key] = resolution
     if resolution.resolution_type == MODULE_OUTPUT:
         # DFS into producing usage
         producing_usage = self._find_usage_for_channel(resolution.qualified_name)
         if producing_usage and producing_usage not in visited:
             self._trace_dependencies(producing_usage, visited, path, order)
```

**Key detail**: The existing `_resolve_binding_via_registry()` (lines 691-753) already handles self-reference guard, REFERENCE secondary resolution, design attribute fallback, and unresolved warning. The old path's ~150 lines of inline resolution collapse to a single method call.

**New helper `_find_usage_for_channel()`:**
```python
def _find_usage_for_channel(self, channel: str) -> CalcUsageData | None:
    """Extract producing CalcUsage from a channel name for DFS traversal.

    Channel format: "Design__part__usage__output" (PQN format).
    Producing usage EQN: everything before the last "__" segment.
    """
    if "__" not in channel:
        return None
    usage_eqn = channel.rsplit("__", 1)[0]
    return self._usage_by_qualified.get(usage_eqn)
```

This replaces the old pattern where `_resolve_binding_to_usage()` returned a `CalcUsageData` directly. The new path resolves to a channel name (string), so we need to derive the producing usage for DFS traversal.

**Note on `_resolve_to_design_attribute()`**: This method (lines 777-856) is **retained**. It's called from within `_resolve_binding_via_registry()` (line 733) as Step 3 of the resolution flow. It doesn't depend on any of the removed indexes -- it operates on `self._design_attributes` directly.

#### 2c. Methods to Remove

| Method | Lines | Reason |
|--------|-------|--------|
| `_compare_with_registry()` | 755-776 | Parallel validation scaffolding |
| `_resolve_binding_to_usage()` | 924-1019 | 7-strategy cascade replaced by registry |
| `_build_design_attr_binding_index()` | 1021-1058 | Index replaced by Phase 4 aliases |
| `_resolve_target_to_qualified()` | 1085-1118 | Only used by above |
| `_build_computed_attr_channel()` | 642-646 | Only used by old inline resolution |

#### 2d. Methods to Retain

| Method | Lines | Reason |
|--------|-------|--------|
| `_resolve_binding_via_registry()` | 691-753 | Sole resolution path |
| `_resolve_reference_via_registry()` | ~660-690 | REFERENCE secondary resolution |
| `_get_parent_part_for_usage()` | ~648-660 | Parent part extraction for REFERENCE |
| `_resolve_to_design_attribute()` | 777-856 | Design attr fallback (called by registry path) |
| `find_required_modules()` | 274-344 | Public API (updated) |
| `_trace_dependencies()` | 390-640 | Core DFS (simplified) |

#### 2e. `find_required_modules()` Update

**Current lines 325-336:**
```python
usage = self._output_catalog.get(target)
if not usage:
    if "." in target:
        instance_name = target.split(".")[0]
        usage = self._usage_by_name.get(instance_name)
```

**After removing `_output_catalog`:**
```python
# Parse instance name from dotted "instance.output" format, or use as-is
if "." in target:
    instance_name = target.split(".")[0]
else:
    instance_name = target
usage = self._usage_by_name.get(instance_name)
```

In practice, `find_required_modules()` targets are always dotted format like `"net_electric.p_net"` (per docstring). The `_usage_by_name` index handles this directly via instance name parsing. No `_usage_by_qualified` lookup is needed -- EQN-format targets (`"Design__plant__lcoe__lcoe_per_mwh"`) are not used by any caller in the codebase.

### Component 3: Graph Builder Simplification

**Purpose:** Replace the 3 output catalog construction functions with OutputRegistry-backed channel validation.

**Location:** `src/sysml_codegen/resolution/graph_builder.py`

#### 3a. Signature Change

```python
def build_computation_graph(
    result: BacktrackingResult,
    calc_defs: list,
    design_attrs: dict[Path, list[DesignAttributeData]],
    group_deriver: ParameterGroupDeriver,
    output_registry: OutputRegistry,  # NEW - replaces output_catalog
    compilation_results: dict | None = None,
    computed_attributes: list[ComputedAttributeData] | None = None,
    aggregation_data: list[ScopedAggregationData] | None = None,
    hierarchy_redefinitions: list[RedefinitionData] | None = None,
) -> ComputationGraph:
```

Add `OutputRegistry` import (TYPE_CHECKING or runtime depending on usage).

#### 3b. Remove Construction Functions

Remove entirely:
- `_build_output_catalog()` (lines 255-303)
- `_extend_output_catalog_with_computed_attrs()` (lines 583-611)
- `_extend_output_catalog_with_aggregation()` (lines 830-854)

Remove from `build_computation_graph()`:
- Lines 107, 111, 115 (catalog construction + extension calls)

#### 3c. Replace Catalog Usage Sites

**Site 1: `_resolve_expose_pure()` (line 644)**

Before:
```python
catalog_key = f"{instance_name}.{output_attr_name}"
entry = output_catalog.get(catalog_key)
if entry is None:
    logger.warning(...)
    return None
_, channel_name, _ = entry
return channel_name
```

After:
```python
catalog_key = f"{instance_name}.{output_attr_name}"
channel_name = output_registry.resolve(catalog_key)
if channel_name is None:
    logger.warning(...)
    return None
return channel_name
```

**Signature change**: `output_catalog: dict[str, tuple[str, str, str]]` -> `output_registry: OutputRegistry`

**Site 2: `_build_attribute_resolution_map()` (line 698)**

Before:
```python
channel = _resolve_expose_pure(ca, calc_usage_names, output_catalog)
```

After:
```python
channel = _resolve_expose_pure(ca, calc_usage_names, output_registry)
```

**Signature change**: Same pattern -- replace `output_catalog` parameter.

**Site 3: `_resolve_aggregation_input_channel()` line 920 (channel existence check)**

Before:
```python
if any(v[1] == channel for v in output_catalog.values()):
    return channel
```

After:
```python
if channel in canonical_channels:
    return channel
```

Uses existing `OutputRegistry.canonical_channels` property (`output_registry.py:161-164`), which returns `frozenset[str]`. This is O(1) vs the old O(n) iteration.

**Performance note:** `canonical_channels` constructs a new `frozenset` on each property access. In functions called per-term in a loop (Sites 3 and 5), capture it once at the top of the calling function:
```python
canonical_channels = output_registry.canonical_channels  # capture once
```
Then use `channel in canonical_channels` throughout. This applies to `_resolve_aggregation_input_channel()` (receives it as a parameter from `_build_aggregation_module()`) and `_build_aggregation_module()` (captures at function entry).

**Site 4: `_resolve_aggregation_input_channel()` line 930-931 (key lookup)**

Before:
```python
catalog_key = f"{part_usage}.{attr}"
if catalog_key in output_catalog:
    return output_catalog[catalog_key][1]
```

After:
```python
catalog_key = f"{part_usage}.{attr}"
channel = output_registry.resolve(catalog_key)
if channel is not None:
    return channel
```

**Signature change**: Replace `output_catalog` parameter with `output_registry: OutputRegistry`.

**Site 5: `_build_aggregation_module()` line 1048 (channel existence check)**

Before:
```python
if any(v[1] == channel for v in output_catalog.values()):
    s_source = InputSource(...)
```

After:
```python
if channel in canonical_channels:  # captured at function entry
    s_source = InputSource(...)
```

**Site 6: `_build_aggregation_module()` line 1055-1056 (CHAIN resolution)**

Before:
```python
resolved = _resolve_aggregation_input_channel(
    s_term.source_path, agg.instance_path, redefinitions, output_catalog,
)
```

After:
```python
resolved = _resolve_aggregation_input_channel(
    s_term.source_path, agg.instance_path, redefinitions, output_registry,
)
```

**Site 7: `_build_pipeline_module()` line 1215 (unused parameter)**

Remove `output_catalog` from parameter list entirely. Also remove from call site at line 157.

#### 3d. Call Site Updates in `build_computation_graph()`

```python
# Step 3: Build attribute resolution map (for FORMULA module input wiring)
calc_usage_names = {u.instance_name for u in result.required_usages}
attr_resolution_map: dict[str, dict[str, AttributeResolution]] = {}
if computed_attributes:
    attr_resolution_map = _build_attribute_resolution_map(
        computed_attributes, design_attrs, output_registry, calc_usage_names  # was output_catalog
    )

# Step 6: Build CalcUsage pipeline modules
module = _build_pipeline_module(
    usage=usage,
    calc_def=calc_def,
    # output_catalog parameter REMOVED
    entry_points=entry_points,
    execution_order=idx,
    binding_resolutions=result.binding_resolutions,
)

# Step 6.7: Build aggregation modules
agg_module = _build_aggregation_module(
    agg, hierarchy_redefinitions or [], output_registry,  # was output_catalog
    entry_points, group_deriver,
)
```

#### 3e. Call Site Update in `initialization.py`

```python
# Step 7: Build ComputationGraph
computation_graph = build_computation_graph(
    result=backtracking_result,
    calc_defs=calc_defs,
    design_attrs=design_attrs,
    group_deriver=group_deriver,
    output_registry=output_registry,  # NEW
    compilation_results=compilation_results,
    computed_attributes=computed_attrs,
    aggregation_data=scoped_agg_data,
    hierarchy_redefinitions=hierarchy_data.redefinitions if hierarchy_data else None,
)
```

### Component 4: Test Migration

**Purpose:** Migrate 39 tests from internal index access to OutputRegistry-based assertions.

**Location:** `tests/unit/test_backtracker_computed_attrs.py` (19 tests), `tests/unit/test_backtracker_aggregation.py` (20 tests)

**Shared helper** (add to a common location, e.g., `tests/conftest_output_registry.py` or inline in each file):
```python
def _build_test_registry(
    calc_usages=None, calc_defs=None, computed_attributes=None,
    aggregation_data=None, channel_aliases=None, design_attributes=None,
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

#### 4a. Category (a) Registration Tests (24 tests)

**Pattern: Index membership → `registry.resolve()` assertion**

Before:
```python
bt = DependencyBacktracker([], [], computed_attributes=[ca])
assert "plant.p_net_kw" in bt._computed_attr_index
```

After:
```python
registry = _build_test_registry(computed_attributes=[ca], calc_usages=[], calc_defs=[])
assert registry.resolve("plant.p_net_kw") is not None
```

**Exclusion tests** (EXPOSE_PURE, EXPOSE_COMPUTED, MANUAL_REQUIRED):
```python
# Before: assert "part.eta" not in bt._computed_attr_index
# After: EXPOSE_PURE is not registered in Phase 1 FORMULA block
registry = _build_test_registry(computed_attributes=[ca])
assert registry.resolve("part.eta") is None  # Not a FORMULA, not registered
```

**Channel format tests** (tests #8-9 in computed attrs, #4 in aggregation):
```python
# Before: assert bt._build_computed_attr_channel(ca) == expected_channel
# After: verify resolution returns the expected channel string
registry = _build_test_registry(computed_attributes=[ca], calc_usages=[], calc_defs=[])
assert registry.resolve("probe_design.area") == expected_channel
```

**File organization (final decision)**: Keep category (a) tests in their original files (`test_backtracker_computed_attrs.py`, `test_backtracker_aggregation.py`). Rename test classes to reflect they now test registry construction (e.g., `TestComputedAttrIndex` -> `TestComputedAttrRegistration`). Rationale: minimizes file churn, preserves git history, and these tests still validate the same domain concern (computed attr / aggregation key patterns) even though the underlying mechanism changed. The spec's suggestion to move them is noted but the pragmatic choice is to keep them in place.

#### 4b. Category (b) Resolution Tests (10 tests)

**Pattern: Add `output_registry` parameter, same `_binding_resolutions` assertions**

Before:
```python
bt = DependencyBacktracker([usage], [calc_def], computed_attributes=[ca])
key = f"{usage.qualified_name}|{binding.param_name}"
resolution = bt._binding_resolutions[key]
assert resolution.resolution_type == BindingResolutionType.MODULE_OUTPUT
```

After:
```python
registry = _build_test_registry(computed_attributes=[ca], calc_usages=[usage], calc_defs=[calc_def])
bt = DependencyBacktracker([usage], [calc_def], design_attributes=design_attrs, output_registry=registry)
key = f"{usage.qualified_name}|{binding.param_name}"
resolution = bt._binding_resolutions[key]
assert resolution.resolution_type == BindingResolutionType.MODULE_OUTPUT
```

**`is_transitive` change (test #19)**:
```python
# Before: assert resolution.is_transitive is True
# After: Phase 4 alias resolves inside registry, is_transitive always False
assert resolution.is_transitive is False
```

#### 4c. Category (c) Integration Tests (5 tests)

**Trace log tests**: The old inline resolution logs with labels like `COMPUTED_ATTR` and `AGGREGATION`. After cut-over, the registry path has different logging. Two options:
1. Update expected log strings to match registry path logging
2. Remove trace log assertion (if the specific label is implementation detail)

**Recommendation**: Update to check for the binding resolution outcome (MODULE_OUTPUT or ENTRY_POINT presence in trace_log) rather than specific label strings. This makes tests resilient to logging changes.

### Component 5: Bug 2 Xfail Removal

**Purpose:** Remove the xfail marker after cut-over makes registry path authoritative.

**Location:** `tests/integration/test_bug2_regression.py`

**Change:** Remove `@pytest.mark.xfail(strict=True, reason="Bug 2: ...")`. The test should pass green because:
- EXPOSE_PURE `total_capex` produces a `ChannelAlias` (Phase 3)
- Phase 3 alias resolves to the upstream CalcUsage output
- `_resolve_binding_via_registry()` finds it via `registry.resolve("financial.total_capex")`
- Returns MODULE_OUTPUT instead of ENTRY_POINT

**Timing:** Must happen in the same commit as the backtracker cut-over (Component 2), because:
- `strict=True` means unexpected pass = test failure
- Once old path is removed, the registry path becomes authoritative
- The test will pass, violating the xfail, causing suite failure

### Component 6: E2E Validation and YAML Diff

**Purpose:** Verify full codegen produces correct pipeline YAML for all models.

**Location:** `tests/integration/test_e2e_output_registry.py` (new file)

#### 6a. YAML Diff Tests

**YAML rendering function chain** (researched from existing code):

```
PipelineContext.computation_graph  →  generate_pipeline_yaml()  →  YAML string
```

- **Function**: `generate_pipeline_yaml(graph, package_name, template_env)` at `generation/pipeline.py:24-63`
- **Template**: `templates/pipeline_yaml.jinja2` (Jinja2 template)
- **Returns**: YAML string directly (no disk write needed)
- **Existing pattern**: `scripts/capture_baseline_yaml.py` demonstrates the exact call chain for tests

```python
import jinja2
from sysml_codegen.generation.initialization import build_pipeline_context
from sysml_codegen.generation.pipeline import generate_pipeline_yaml

class TestYamlDiffValidation:
    """Diff generated YAML against pre-cutover baselines."""

    @pytest.fixture(scope="class")
    def template_env(self):
        template_dir = Path(__file__).parent.parent.parent / "src" / "sysml_codegen" / "templates"
        return jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(template_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    @pytest.fixture(scope="class")
    def baseline_dir(self):
        return Path(__file__).parent.parent / "fixtures" / "baseline_yaml"

    def _generate_yaml(self, model_path, template_env, package_name="test"):
        """Run full codegen and return pipeline YAML string."""
        ctx = build_pipeline_context([model_path])
        return generate_pipeline_yaml(
            graph=ctx.computation_graph,
            package_name=package_name,
            template_env=template_env,
        )

    def test_solar_battery_yaml_matches_baseline(self, baseline_dir, template_env, solar_battery_model_path):
        generated = self._generate_yaml(solar_battery_model_path, template_env, "solar_battery")
        baseline = (baseline_dir / "solar_battery.yaml").read_text()
        assert generated == baseline  # Exact match expected (no Bug 2 changes on this model)

    def test_attr_expr_probe_yaml_improves_on_baseline(self, baseline_dir, template_env, fixtures_path):
        generated = self._generate_yaml(fixtures_path / "attr_expr_probe", template_env, "attr_expr_probe")
        baseline = (baseline_dir / "attr_expr_probe.yaml").read_text()
        # Bug 2 fix: total_capex should change from entry_point to module_output
        # Exact match NOT expected -- assert the specific improvement instead
        assert "module_output" in generated or generated != baseline
        # More specific: check that total_capex is wired to module_output in generated
```

#### 6b. Issue 22 Integration Test

```python
class TestIssue22ReferenceToAggregation:
    """REFERENCE->aggregation same-scope resolves to MODULE_OUTPUT."""

    @pytest.fixture(scope="class")
    def pipeline_context(self, fixtures_path):
        return build_pipeline_context([fixtures_path / "issue22_model"])

    def test_reference_aggregation_resolves_to_module_output(self, pipeline_context):
        """Issue 22: REFERENCE binding to same-scope aggregation output."""
        # Check binding_resolutions for the specific REFERENCE binding
        resolutions = pipeline_context.backtracking_result.binding_resolutions
        # Find the REFERENCE binding that targets an aggregation output
        # Assert it resolves to MODULE_OUTPUT
        ...
```

### Component 7: Initialization Pipeline Updates

**Purpose:** Thread OutputRegistry to graph builder, make backtracker registry required.

**Location:** `src/sysml_codegen/generation/initialization.py`

**Changes to `build_pipeline_context()`:**

1. **Step 6 (line 809-826)**: Remove `computed_attributes` and `aggregation_data` from backtracker constructor call. Make `output_registry` required (not keyword):

```python
# Step 6: Create backtracker (MODIFIED)
backtracker = DependencyBacktracker(
    calc_usages,
    calc_defs,
    design_attributes=design_attrs,
    output_registry=output_registry,  # Required
)
```

2. **Step 7 (line 866-875)**: Pass `output_registry` to `build_computation_graph()`:

```python
computation_graph = build_computation_graph(
    result=backtracking_result,
    calc_defs=calc_defs,
    design_attrs=design_attrs,
    group_deriver=group_deriver,
    output_registry=output_registry,  # NEW
    compilation_results=compilation_results,
    computed_attributes=computed_attrs,
    aggregation_data=scoped_agg_data,
    hierarchy_redefinitions=hierarchy_data.redefinitions if hierarchy_data else None,
)
```

3. **Step 3.6 removal** (if diagnostic passes): Remove lines 781-783:
```python
# REMOVE:
# alias_count = _enrich_aliases_from_bindings(hierarchy_data, calc_usages)
# if alias_count:
#     logger.info("Step 3.6: ...")
```

And remove `_enrich_aliases_from_bindings()` function definition (lines 331-377).

### Component 8: Dead Code Cleanup

**Files and items to remove:**

| Item | File | Lines | Condition |
|------|------|-------|-----------|
| `_enrich_aliases_from_bindings()` | initialization.py | 331-377 | Step 3.6 diagnostic passes |
| Call site for Step 3.6 | initialization.py | 781-783 | Step 3.6 diagnostic passes |
| `_compare_with_registry()` | backtracker.py | 755-776 | Always |
| 3 insertion points | backtracker.py | 480-481, 511-512, 617-619 | Always |
| `_computed_attr_index` block | backtracker.py | 144-162 | Always |
| `_aggregation_output_index` block | backtracker.py | 163-205 | Always |
| `_output_catalog` block | backtracker.py | 232-248 | Always |
| `_design_attr_binding_index` block | backtracker.py | 250-254 | Always |
| Inline computed_attr check | backtracker.py | 459-482 | Always |
| Inline aggregation check | backtracker.py | 484-513 | Always |
| Old cascade resolution | backtracker.py | 515-616 | Always |
| `_resolve_binding_to_usage()` | backtracker.py | 924-1019 | Always |
| `_build_design_attr_binding_index()` | backtracker.py | 1021-1058 | Always |
| `_resolve_target_to_qualified()` | backtracker.py | 1085-1118 | Always |
| `_build_computed_attr_channel()` | backtracker.py | 642-646 | Always |
| `_build_output_catalog()` | graph_builder.py | 255-303 | Always |
| `_extend_output_catalog_with_computed_attrs()` | graph_builder.py | 583-611 | Always |
| `_extend_output_catalog_with_aggregation()` | graph_builder.py | 830-854 | Always |
| `__all__` entries for removed functions | graph_builder.py | 1336-1339 | Always |

**Estimated lines removed**: ~550 lines from backtracker, ~120 lines from graph builder, ~50 lines from initialization = ~720 lines of dead code.

---

## Potential Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| `find_required_modules()` breaks after `_output_catalog` removal | Medium | `_usage_by_name` becomes sole lookup (see Component 2e). Functional test: call `find_required_modules(["net_electric.p_net"])` on solar_battery and verify same result. |
| `_find_usage_for_channel()` channel parsing edge case | Low | Channel format is deterministic PQN: `usage_qn__output_name`. `rsplit("__", 1)` handles all cases. Aggregation and FORMULA channels follow the same format. |
| Removing `computed_attributes` and `aggregation_data` from backtracker constructor breaks external callers | Medium | Search for all `DependencyBacktracker(` call sites. Only `initialization.py` constructs backtracker instances in production code. Tests will need updating (part of test migration). |
| Step 3.6 diagnostic shows divergences (not dead code) | Low | Retain with documentation. The aliases flow into Phase 1 registration naturally. No code change needed beyond documenting the finding. |
| Graph builder tests depend on output catalog directly | Medium | Search for `output_catalog` in graph builder test files. Any tests constructing catalogs directly need migration to use OutputRegistry. |
| `_build_computed_attr_module()` uses `output_catalog` transitively via `_resolve_expose_pure()` | Low | Already handled -- `_resolve_expose_pure()` is updated to use `output_registry` in Component 3c. The resolution map is built before module construction. |

## Integration Strategy

### Sub-task Ordering (Optimized)

```
1. Step 3.6 diagnostic            [~30 min]  — resolve open question
2. Test migration: category (a)   [~2 hours] — validate registry coverage
   pytest gate
3. Test migration: category (b)   [~1 hour]  — validate resolution outcomes
   pytest gate
4. Test migration: category (c)   [~30 min]  — update trace logs
   pytest gate
5. Backtracker cut-over +         [~3 hours] — sole registry path
   Bug 2 xfail removal                        — same commit
   pytest gate
6. Graph builder simplification   [~2 hours] — OutputRegistry-backed validation
   pytest gate
7. E2E validation + Issue 22 test [~2 hours] — YAML diff, new integration test
   pytest gate
8. Dead code cleanup              [~1 hour]  — Step 3.6 if dead, remaining artifacts
9. Quality gate                   [~30 min]  — pytest + mypy + ruff
```

**Why test migration before cut-over**: Tests using old API patterns will break when old indexes are removed. Migrating first means the cut-over commit only changes production code, and tests already expect the new API. This makes the cut-over commit reviewable -- if tests fail, it's a production code issue, not a test setup issue.

**Why Bug 2 xfail in same commit as cut-over**: The `strict=True` xfail means the test MUST fail. Once the registry is authoritative, it passes. If xfail isn't removed simultaneously, the suite fails.

### Initialization Pipeline Threading

```
build_pipeline_context()
  |
  Step 5.5: output_registry = build_output_registry(...)  # existing
  |
  Step 6: backtracker = DependencyBacktracker(
              ..., output_registry=output_registry)        # updated
  |
  Step 7: computation_graph = build_computation_graph(
              ..., output_registry=output_registry)        # updated
  |
  PipelineContext(output_registry=output_registry)         # existing
```

## Validation Approach

### Testing Strategy

1. **Step 3.6 diagnostic**: Integration test with/without Step 3.6, compare binding_resolutions
2. **Test migration (39 tests)**: Each migrated test passes independently before cut-over
3. **Cut-over validation**: Full `uv run pytest tests/` after removing old indexes
4. **Graph builder validation**: Existing graph builder tests pass with OutputRegistry parameter
5. **Bug 2 regression**: `test_bug2_regression.py` passes green (xfail removed)
6. **E2E YAML diff**: Generated YAML matches baselines (4 models)
7. **Issue 22 regression**: New integration test for REFERENCE->aggregation same-scope
8. **Quality gate**: `uv run pytest tests/` + `uv run mypy src/` + `uv run ruff check src/`

### Success Criteria (from spec)

- [ ] Zero references to `_computed_attr_index`, `_aggregation_output_index`, `_output_catalog`, `_design_attr_binding_index` in production code
- [ ] `_resolve_binding_to_usage()` cascade removed
- [ ] Graph builder's 3 output catalog functions removed
- [ ] All 39 migrated tests pass
- [ ] Pipeline YAML matches baselines for all 4 models
- [ ] Bug 2 fixed: `total_capex` resolves to MODULE_OUTPUT
- [ ] Issue 22: REFERENCE->aggregation resolves to MODULE_OUTPUT
- [ ] `pytest` + `mypy` + `ruff check` all pass
- [ ] ~720 lines of dead code removed

---

Next Step: After approval -> `/_my_plan` for implementation sequencing, then `/_my_implement`
