# Spec 06: Step 6 -- Backtracker Changes (OutputRegistry Integration)

**Spec ID**: SPEC-06
**Status**: Draft
**Created**: 2026-02-13
**Implements**: Epic OUTPUT-REGISTRY, Item 3 (backtracker refactoring) + Item 4 (cleanup)
**Design Reference**: `08_algorithm_revised.md` Section 7
**Spike Evidence**: Spikes 1, 5, 8, 9

---

## 1. Overview

The `DependencyBacktracker` is **heavily modified** in this redesign. It
replaces five ad-hoc indexes and a 7-strategy cascade with a single
`OutputRegistry` for CHAIN binding resolution and a structured secondary
resolution path for REFERENCE bindings.

The fundamental contract remains unchanged:

> After backtracking, **every** input on **every** CalcUsage has exactly one
> `BindingResolution` stored in `binding_resolutions["{usage_qn}|{param_name}"]`.
> Each resolution is either `ENTRY_POINT` or `MODULE_OUTPUT`.
> There are no unresolved bindings. If resolution fails, it falls back to
> `ENTRY_POINT` with a logged warning.

What changes is **how** that resolution happens: from a 7-strategy cascade
across 5 indexes to a structured 3-path resolution using the OutputRegistry.

---

## 2. Constructor Changes

### 2.1 New Constructor Signature

```python
class DependencyBacktracker:
    def __init__(
        self,
        all_usages: list[CalcUsageData],
        calc_defs: list,
        design_attributes: dict[Path, list[DesignAttributeData]] | None = None,
        output_registry: OutputRegistry | None = None,
        # REMOVED: computed_attributes (now in OutputRegistry)
        # REMOVED: aggregation_data (now in OutputRegistry)
    ):
```

### 2.2 Indexes REMOVED

The following indexes are removed from the constructor body. Their
responsibilities are now handled by the `OutputRegistry` (built in Step 5).

| Removed Index | Lines in Current Code | Replacement |
|---|---|---|
| `_computed_attr_index` | Lines 144-155 | Phase 1 FORMULA registration in OutputRegistry |
| `_aggregation_output_index` | Lines 159-197 | Phase 1 Aggregation registration in OutputRegistry |
| `_output_catalog` | Lines 225-238 | Phase 1 CalcUsage registration in OutputRegistry |
| `_design_attr_binding_index` | Lines 241-243, 873-910 | Phase 4 transitive aliases in OutputRegistry |
| (`_usage_by_name`) | Lines 212-221 | Phase 1 Key_A in OutputRegistry; **may be kept for non-resolution purposes** |

### 2.3 Index ADDED

```python
self._output_registry: OutputRegistry = output_registry or OutputRegistry()
```

### 2.4 Indexes KEPT (Unchanged)

| Kept Index | Purpose | Why Not Replaced |
|---|---|---|
| `_calc_def_by_name` | CalcDef lookup by name | Used for input/output attribute enumeration, not for binding resolution |
| `_usage_by_qualified` | CalcUsage lookup by EQN | Used for DFS traversal, topological sort, not for binding resolution |
| `_usage_by_name` | CalcUsage lookup by instance name | **Decision point**: Keep for `find_required_modules()` target resolution (line 319) and `_build_dependency_graph()` (line 995). Remove only after these consumers are migrated to use `_usage_by_qualified`. |

### 2.5 Methods REMOVED

| Removed Method | Lines | Replacement |
|---|---|---|
| `_resolve_binding_to_usage()` | Lines 776-871 | Three distinct resolution paths (see Section 3) |
| `_build_design_attr_binding_index()` | Lines 873-909 | Phase 4 in OutputRegistry (Spec 05) |
| `_is_path_reference()` | Lines 911-935 | `_is_transitive_default()` in Spec 05 |
| `_resolve_target_to_qualified()` | Lines 937-970 | Phase 1 Key_B/Key_C in OutputRegistry (exact match) |
| `_build_channel_name_for_binding()` | Lines 710-774 | OutputRegistry `resolve()` returns canonical channel directly |
| `_build_computed_attr_channel()` | Lines 623-627 | Phase 1 FORMULA registration in OutputRegistry |

### 2.6 Methods ADDED

| New Method | Purpose |
|---|---|
| `_get_parent_part_for_usage()` | Extract parent PartUsage name for REFERENCE secondary resolution |
| `_resolve_to_design_attribute()` | **Simplified** version of current method -- no longer needs `CalcUsageData` parameter |

### 2.7 Constructor Pseudocode (Target State)

```python
def __init__(
    self,
    all_usages: list[CalcUsageData],
    calc_defs: list,
    design_attributes: dict[Path, list[DesignAttributeData]] | None = None,
    output_registry: OutputRegistry | None = None,
):
    self.all_usages = all_usages
    self.calc_defs = calc_defs
    self._design_attributes = design_attributes or {}
    self._output_registry = output_registry or OutputRegistry()

    # CalcDef lookup for input/output attribute enumeration
    self._calc_def_by_name: dict[str, object] = {c.name: c for c in calc_defs}

    # Primary index: qualified name (unique, no collisions)
    self._usage_by_qualified: dict[str, CalcUsageData] = {
        u.qualified_name: u for u in all_usages
    }

    # Secondary index: instance name (for target resolution in find_required_modules)
    # NOTE: Collisions expected and benign. Keep for backward compatibility
    # during migration. Remove after consumers migrated to _usage_by_qualified.
    self._usage_by_name: dict[str, CalcUsageData] = {}
    for u in all_usages:
        if u.instance_name not in self._usage_by_name:
            self._usage_by_name[u.instance_name] = u

    # Phantom detector for inline detection
    self._phantom_detector = PhantomDetector(all_usages, calc_defs)

    # Tracking state (reset per find_required_modules call)
    self._entry_point_context: dict[str, CalcUsageData] = {}
    self._entry_point_sources: dict[str, str] = {}
    self._trace_log: list[str] = []
    self._binding_to_entry_point: dict[str, str] = {}  # DEPRECATED
    self._binding_resolutions: dict[str, BindingResolution] = {}
```

---

## 3. Strategy Cascade REPLACEMENT

### 3.1 Current State: 7-Strategy Cascade

The current `_resolve_binding_to_usage()` implements:

1. **Strategy 0**: Computed attribute index lookup (3 key patterns)
2. **Strategy 0b**: Aggregation output index lookup (3 key patterns + sanitized `::` fallback)
3. **Strategy 1**: Exact match in `_output_catalog`
4. **Strategy 2a**: Direct instance match via `_usage_by_name`
5. **Strategy 4**: Transitive design attribute index lookup (moved up from original position)
6. **Strategy 2b**: Cross-file attribute matching (fuzzy `.endswith()` search)
7. **Strategy 3**: Bare instance name lookup
8. **Strategy 5**: Normalized `::` to dotted design attr transitive
9. **Fallback**: Return None (becomes ENTRY_POINT)

This cascade makes 12+ lookup attempts across 5 indexes, with 4+ format
conversions. It is fragile, order-dependent, and produces silent wrong results
when an early strategy matches incorrectly.

### 3.2 Target State: Three Distinct Resolution Paths

The target replaces the cascade with three distinct resolution paths, one per
binding type. There is no cross-type fallthrough.

#### Path A: LITERAL Bindings

```python
if binding.binding_type == BindingType.LITERAL:
    # Always ENTRY_POINT. No change from current behavior.
    entry_point_qn = f"{usage.qualified_name}__{param_name}"
    self._binding_resolutions[mapping_key] = BindingResolution(
        resolution_type=BindingResolutionType.ENTRY_POINT,
        qualified_name=entry_point_qn,
        source_path=None,
        is_transitive=False,
    )
    # DEPRECATED: keep for backward compat during migration
    self._binding_to_entry_point[mapping_key] = entry_point_qn
    self._entry_point_context[entry_point_qn] = usage
    continue
```

**Invariant**: 100% of LITERAL bindings become ENTRY_POINT. No exceptions.

#### Path B: UNBOUND Parameters

```python
# After processing all bindings, handle unbound params
for param in usage.unbound_params:
    qualified_param_name = f"{usage.qualified_name}__{param}"
    mapping_key = f"{usage.qualified_name}|{param}"
    self._binding_resolutions[mapping_key] = BindingResolution(
        resolution_type=BindingResolutionType.ENTRY_POINT,
        qualified_name=qualified_param_name,
        source_path=None,
        is_transitive=False,
    )
    # DEPRECATED: keep for backward compat during migration
    self._binding_to_entry_point[mapping_key] = qualified_param_name
    self._entry_point_context[qualified_param_name] = usage
```

**Invariant**: 100% of UNBOUND params become ENTRY_POINT. No exceptions.

#### Path C: CHAIN Bindings (source_path is DOTTED)

CHAIN bindings always have a dotted `source_path` (e.g., `"alpha_split.p_alpha"`).
Spike 1 confirmed this invariant across 94 bindings in 3 models.

```python
# CHAIN binding: source_path is always DOTTED (Spike 1)
if binding.source_path and binding.binding_type != BindingType.LITERAL:
    # Determine if this is CHAIN (dotted) or REFERENCE (SYSML_QN)
    if "::" not in binding.source_path and "." in binding.source_path:
        # --- CHAIN RESOLUTION PATH ---
        channel = self._output_registry.resolve(binding.source_path)

        if channel is not None:
            # MODULE_OUTPUT: binding wires to upstream module output
            self._binding_resolutions[mapping_key] = BindingResolution(
                resolution_type=BindingResolutionType.MODULE_OUTPUT,
                qualified_name=channel,
                source_path=binding.source_path,
                is_transitive=False,
            )
            self._trace_log.append(
                f"    {param_name} -> MODULE_OUTPUT via registry ({channel})"
            )

            # Trace upstream dependency for DFS
            # Extract producing usage from channel name for dependency graph
            source_usage = self._find_usage_for_channel(channel)
            if source_usage and source_usage.qualified_name != usage.qualified_name:
                transitive = self._trace_dependencies(source_usage, visited, path)
                dependencies.update(transitive)
            continue

        # Registry miss: try design attribute fallback -> ENTRY_POINT
        design_attr_qn = self._resolve_to_design_attribute(binding.source_path)
        if design_attr_qn:
            self._binding_resolutions[mapping_key] = BindingResolution(
                resolution_type=BindingResolutionType.ENTRY_POINT,
                qualified_name=design_attr_qn,
                source_path=binding.source_path,
                is_transitive=False,
            )
            self._binding_to_entry_point[mapping_key] = design_attr_qn
            self._entry_point_context[design_attr_qn] = usage
            self._entry_point_sources[design_attr_qn] = binding.source_path
            self._trace_log.append(
                f"    {param_name} -> ENTRY_POINT (design attr: {design_attr_qn})"
            )
            continue

        # Final fallback: ENTRY_POINT with warning
        logger.warning(
            "CHAIN binding '%s' on '%s' could not be resolved. "
            "Treating as entry point.",
            binding.source_path, usage.qualified_name,
        )
        qualified_param_name = f"{usage.qualified_name}__{param_name}"
        self._binding_resolutions[mapping_key] = BindingResolution(
            resolution_type=BindingResolutionType.ENTRY_POINT,
            qualified_name=qualified_param_name,
            source_path=binding.source_path,
            is_transitive=False,
        )
        self._binding_to_entry_point[mapping_key] = qualified_param_name
        self._entry_point_context[qualified_param_name] = usage
        self._entry_point_sources[qualified_param_name] = binding.source_path
        self._trace_log.append(
            f"    {param_name} -> ENTRY_POINT (unresolved CHAIN: {binding.source_path})"
        )
        continue
```

**Resolution order for CHAIN**:
1. `OutputRegistry.resolve(source_path)` -- exact dotted match
2. `_resolve_to_design_attribute(source_path)` -- design attribute fallback
3. ENTRY_POINT with WARNING -- final fallback

#### Path D: REFERENCE Bindings (source_path is SYSML_QN)

REFERENCE bindings have a `::` format `source_path` (e.g.,
`"FusionPhysics::GrossEfficiency::eta_gross"`). Spike 1 confirmed this invariant.

Of REFERENCE bindings, Spike 5 showed:
- **119/123** resolve to ENTRY_POINT (design attributes with literal values)
- **4/123** resolve to MODULE_OUTPUT (all computed attribute outputs)

The 4 MODULE_OUTPUT cases are resolved by the backtracker's **secondary
resolution path** (leaf-name extraction + parent-scoped OutputRegistry lookup),
not by the OutputRegistry directly.

```python
    elif "::" in binding.source_path:
        # --- REFERENCE RESOLUTION PATH ---

        # Step 1: Try OutputRegistry exact match (rare but handles any
        # dotted aliases that might match a SYSML_QN source_path)
        channel = self._output_registry.resolve(binding.source_path)

        if channel is None:
            # Step 2: Secondary resolution for computed attributes
            # Extract leaf name from SYSML_QN, try parent-scoped dotted lookup.
            # This handles the 4 REFERENCE -> MODULE_OUTPUT cases (Spike 5).
            #
            # Example:
            #   source_path = "SolarBatteryLibrary::'PV Module'::cost_model::wattage"
            #   leaf_name = "wattage"  (after strip("'"))
            #   parent_part = "pv_module"  (from segments[-2] of usage QN)
            #   resolve_key = "pv_module.wattage"
            #
            # Spike 8 validated: segments[-2] produces the correct parent for
            # all 4 REFERENCE->MODULE_OUTPUT cases across both models.
            leaf_name = binding.source_path.rsplit("::", 1)[-1].strip("'")
            parent_part = self._get_parent_part_for_usage(usage)
            if parent_part:
                resolve_key = f"{parent_part}.{leaf_name}"
                channel = self._output_registry.resolve(resolve_key)
                if channel is not None:
                    self._trace_log.append(
                        f"    {param_name} -> MODULE_OUTPUT via secondary "
                        f"('{resolve_key}' -> {channel})"
                    )

        if channel is not None:
            # MODULE_OUTPUT (4 cases: Spike 5)
            self._binding_resolutions[mapping_key] = BindingResolution(
                resolution_type=BindingResolutionType.MODULE_OUTPUT,
                qualified_name=channel,
                source_path=binding.source_path,
                is_transitive=False,
            )

            # Trace upstream dependency for DFS
            source_usage = self._find_usage_for_channel(channel)
            if source_usage and source_usage.qualified_name != usage.qualified_name:
                transitive = self._trace_dependencies(source_usage, visited, path)
                dependencies.update(transitive)
            continue

        # Step 3: Design attribute fallback (119 cases: Spike 5)
        design_attr_qn = self._resolve_to_design_attribute(binding.source_path)
        if design_attr_qn:
            self._binding_resolutions[mapping_key] = BindingResolution(
                resolution_type=BindingResolutionType.ENTRY_POINT,
                qualified_name=design_attr_qn,
                source_path=binding.source_path,
                is_transitive=False,
            )
            self._binding_to_entry_point[mapping_key] = design_attr_qn
            self._entry_point_context[design_attr_qn] = usage
            self._entry_point_sources[design_attr_qn] = binding.source_path
            self._trace_log.append(
                f"    {param_name} -> ENTRY_POINT (design attr: {design_attr_qn})"
            )
            continue

        # Final fallback: ENTRY_POINT with warning
        logger.warning(
            "REFERENCE binding '%s' on '%s' could not be resolved. "
            "Treating as entry point.",
            binding.source_path, usage.qualified_name,
        )
        qualified_param_name = f"{usage.qualified_name}__{param_name}"
        self._binding_resolutions[mapping_key] = BindingResolution(
            resolution_type=BindingResolutionType.ENTRY_POINT,
            qualified_name=qualified_param_name,
            source_path=binding.source_path,
            is_transitive=False,
        )
        self._binding_to_entry_point[mapping_key] = qualified_param_name
        self._entry_point_context[qualified_param_name] = usage
        self._entry_point_sources[qualified_param_name] = binding.source_path
        self._trace_log.append(
            f"    {param_name} -> ENTRY_POINT (unresolved REFERENCE: {binding.source_path})"
        )
        continue
```

**Resolution order for REFERENCE**:
1. `OutputRegistry.resolve(source_path)` -- exact match (rare, for dotted aliases)
2. Secondary resolution: extract `leaf_name` + `parent_part` (via `_get_parent_part_for_usage()`), then `OutputRegistry.resolve(f"{parent_part}.{leaf_name}")`
3. `_resolve_to_design_attribute(source_path)` -- design attribute fallback
4. ENTRY_POINT with WARNING -- final fallback

#### Path E: Bare-Name Bindings (No Dot, No ::)

Spike 1 confirmed: bare-name bindings were **never observed** (94 bindings,
3 models). However, for defensive robustness, handle them:

```python
    else:
        # --- BARE NAME OR NO SOURCE PATH ---
        # This path should be unreachable based on Spike 1 (zero bare names).
        # If reached, treat as unresolvable -> ENTRY_POINT with warning.
        if binding.source_path:
            logger.warning(
                "Unexpected bare-name binding '%s' on '%s'. "
                "Treating as entry point.",
                binding.source_path, usage.qualified_name,
            )
        qualified_param_name = f"{usage.qualified_name}__{param_name}"
        self._binding_resolutions[mapping_key] = BindingResolution(
            resolution_type=BindingResolutionType.ENTRY_POINT,
            qualified_name=qualified_param_name,
            source_path=binding.source_path,
            is_transitive=False,
        )
        self._binding_to_entry_point[mapping_key] = qualified_param_name
        self._entry_point_context[qualified_param_name] = usage
        if binding.source_path:
            self._entry_point_sources[qualified_param_name] = binding.source_path
```

---

## 4. New Helper Methods

### 4.1 `_get_parent_part_for_usage()`

```python
def _get_parent_part_for_usage(self, usage: CalcUsageData) -> str | None:
    """Get the immediate parent PartUsage name for scoping secondary resolution.

    Returns the second-to-last segment of the CalcUsage's qualified_name.
    This is the PartUsage that directly contains the CalcUsage.

    Used by REFERENCE binding secondary resolution to construct parent-scoped
    dotted keys for OutputRegistry lookup. The parent part name matches Key_F
    (FORMULA) or Key_D (aggregation) or Key_A (CalcUsage) registration keys.

    Spike 8 validated: segments[-2] produces the correct parent for all 4
    REFERENCE -> MODULE_OUTPUT cases across both models:

    | CalcUsage QN | segments[-2] | Resolves Against |
    |---|---|---|
    | SolarBatteryDesign__solar_battery_plant__annualized_financial | solar_battery_plant | Key_D or Key_F |
    | SolarBatteryDesign__solar_battery_plant__solar_array__pv_module__cost_model | pv_module | Key_A |
    | E2EDesign__e2e_plant__financial | e2e_plant | Key_F |
    | E2EDesign__e2e_plant__om_calc | e2e_plant | Key_F |

    Spike 9 (Issue 22) validated: CalcUsage and aggregation on the same PartDef
    share scope. Virtual expansion preserves shared scope, so segments[-2]
    equals the PartUsage instance name that Key_D is registered under.

    Known limitation: deeply nested CalcUsages referencing parent-scope
    aggregation outputs (e.g., CalcUsage on child PartDef referencing
    grandparent aggregation) would fail. If that scenario arises, resolution
    would need to walk up the hierarchy. Currently not observed in any model.

    Args:
        usage: The CalcUsage whose parent is needed.

    Returns:
        The parent PartUsage name (e.g., "solar_battery_plant"), or None
        if the qualified_name has fewer than 2 segments.

    Examples:
        >>> usage.qualified_name = "SolarBatteryDesign__solar_battery_plant__lcoe"
        >>> _get_parent_part_for_usage(usage)
        "solar_battery_plant"

        >>> usage.qualified_name = "SolarBatteryDesign__solar_battery_plant__solar_array__pv_module__cost_model"
        >>> _get_parent_part_for_usage(usage)
        "pv_module"

        >>> usage.qualified_name = "simple_calc"
        >>> _get_parent_part_for_usage(usage)
        None
    """
    segments = usage.qualified_name.split("__")
    if len(segments) < 2:
        return None
    return segments[-2]
```

### 4.2 `_resolve_to_design_attribute()` (Simplified)

The current `_resolve_to_design_attribute()` takes a `CalcUsageData` parameter
for file-context disambiguation. The new version drops this parameter because
the OutputRegistry handles multi-scope disambiguation via scoped keys.

```python
def _resolve_to_design_attribute(
    self,
    source_path: str,
) -> str | None:
    """Resolve source_path to a literal-valued design attribute qualified name.

    This is the fallback after OutputRegistry resolution fails. It handles
    the 119 REFERENCE -> ENTRY_POINT cases (Spike 5) and CHAIN bindings that
    point to design attributes (not module outputs).

    Transitive design attrs (whose default_value is a dotted path pointing
    to a module output) are handled by Phase 4 OutputRegistry aliases and
    never reach this method.

    Resolution:
    1. Extract leaf name from source_path:
       - SYSML_QN ("Ns::Part::attr") -> last segment after "::", strip quotes
       - DOTTED ("instance.output") -> last segment after "."
       - BARE ("attr_name") -> use as-is
    2. If DOTTED: extract parent_part from first segment, search by
       (parent_part, leaf_name) exact match
    3. If SYSML_QN: convert to Python QN, search by exact qualified_name match
    4. If BARE: search by leaf_name match across all design attrs
    5. Return the design attribute's qualified_name if found with literal/None
       default_value, or None

    Args:
        source_path: Binding source path (DOTTED, SYSML_QN, or BARE format).

    Returns:
        Design attribute qualified name if found, None otherwise.
    """
    # Handle dotted paths (parent_part.attribute_name)
    if "." in source_path and "::" not in source_path:
        parts = source_path.split(".")
        parent_part = parts[0]
        attr_name = parts[-1]

        # Search by (parent_part, attr_name) match
        for file_path, attrs in self._design_attributes.items():
            for attr in attrs:
                if attr.name == attr_name and attr.parent_part == parent_part:
                    return attr.qualified_name
        return None

    # Handle SysML qualified names (contain '::' separator)
    if "::" in source_path:
        python_qname = sysml_to_python_qualified_name(source_path)
        for file_path, attrs in self._design_attributes.items():
            for attr in attrs:
                if attr.qualified_name == python_qname:
                    return attr.qualified_name

        # No exact match -- try leaf name extraction + parent matching
        leaf_name = source_path.rsplit("::", 1)[-1].strip("'")
        # Extract parent from the segment before leaf
        sysml_parts = source_path.split("::")
        if len(sysml_parts) >= 2:
            parent_candidate = sanitize_name(sysml_parts[-2])
            for file_path, attrs in self._design_attributes.items():
                for attr in attrs:
                    if attr.name == leaf_name and attr.parent_part.lower() == parent_candidate.lower():
                        return attr.qualified_name
        return None

    # Handle bare names (no dot, no ::)
    # Search by name match across all design attrs
    candidates: list[DesignAttributeData] = []
    for file_path, attrs in self._design_attributes.items():
        for attr in attrs:
            if attr.name == source_path:
                candidates.append(attr)

    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0].qualified_name

    # Multiple candidates -- log warning, use first
    logger.warning(
        "Ambiguous design attribute '%s': %d matches found. Using %s",
        source_path, len(candidates), candidates[0].qualified_name,
    )
    return candidates[0].qualified_name
```

**Key change from current**: The `usage: CalcUsageData` parameter is removed.
File-context disambiguation was needed because the old output_catalog used
simple keys (`instance.output`) that could collide. The OutputRegistry uses
scoped keys (Key_C includes full hierarchy), so file context is no longer
needed for disambiguation.

### 4.3 `_find_usage_for_channel()` (New)

When a binding resolves to MODULE_OUTPUT, the backtracker needs the producing
CalcUsage to continue DFS traversal. The canonical channel name encodes the
producing usage's EQN.

```python
def _find_usage_for_channel(self, channel: str) -> CalcUsageData | None:
    """Find the CalcUsage that produces a given channel.

    Channel format is PQN: "{usage_eqn}__{output_name}".
    The producing usage's qualified_name is everything before the last "__".

    Args:
        channel: Canonical channel name (PQN format).

    Returns:
        The producing CalcUsage, or None if not found.
    """
    # Channel = usage_eqn + "__" + output_name
    # Reverse: strip the last "__" segment to get usage_eqn
    parts = channel.rsplit("__", 1)
    if len(parts) < 2:
        return None
    usage_eqn = parts[0]
    return self._usage_by_qualified.get(usage_eqn)
```

**Edge case**: For FORMULA computed attribute channels, the channel format is
`{parent_eqn}__{python_name}__{python_name}` (the python_name appears twice:
once in the module EQN, once as the output name). The `rsplit("__", 1)` strips
the output name, leaving the module EQN, which is NOT in `_usage_by_qualified`
(it's a synthetic module, not a CalcUsage). This returns `None`, which is
correct -- FORMULA modules don't have recursive dependencies that need tracing
(their inputs resolve through the OutputRegistry).

**Edge case**: For aggregation channels, the channel format is
`{instance_path}__{attr_name}__{attr_name}`. Similarly returns `None` -- correct
because aggregation modules are built by the graph builder from
`ScopedAggregationData`, not from CalcUsage DFS traversal.

---

## 5. Binding Type Detection

The current code determines binding type from `BindingType` enum (LITERAL, CHAIN,
REFERENCE, etc.) and `source_path` format. The target uses a cleaner dispatch:

```python
for binding in usage.bindings:
    param_name = binding.param_name
    mapping_key = f"{usage.qualified_name}|{param_name}"

    # Path A: LITERAL binding -> always ENTRY_POINT
    if binding.binding_type == BindingType.LITERAL:
        # ... (Section 3.2, Path A)
        continue

    # No source_path -> treat as unresolvable -> ENTRY_POINT
    if not binding.source_path:
        # ... (Section 3.2, Path E)
        continue

    # Guard: self-referential bindings must not create self-loops
    # (unchanged from current code)
    # ... self-reference check ...

    # Dispatch by source_path format (Spike 1: exactly two formats)
    if "::" in binding.source_path:
        # Path D: REFERENCE binding (SYSML_QN format)
        # ... (Section 3.2, Path D)
    elif "." in binding.source_path:
        # Path C: CHAIN binding (DOTTED format)
        # ... (Section 3.2, Path C)
    else:
        # Path E: Bare name (should not occur per Spike 1)
        # ... (Section 3.2, Path E)
```

**Key insight**: The binding type classification (`BindingType.CHAIN` vs
`BindingType.REFERENCE`) and the source_path format (`"." in source_path` vs
`"::" in source_path`) are **correlated but not identical**. Spike 1 showed
that CHAIN bindings always have dotted source_paths and REFERENCE bindings
always have SYSML_QN source_paths. The target uses source_path format as the
primary dispatch (more reliable than the BindingType enum, which is set by the
extractor using heuristics).

---

## 6. Dependency Graph Building Changes

### 6.1 Current `_build_dependency_graph()`

The current implementation re-calls `_resolve_binding_to_usage()` for every
binding on every required usage (line 995). This duplicates resolution work and
can produce different results from the resolution done in `_trace_dependencies()`.

### 6.2 Target `_build_dependency_graph()`

The target builds the dependency graph from `_binding_resolutions` (already
populated by `_trace_dependencies()`), avoiding re-resolution.

```python
def _build_dependency_graph(
    self,
    required_usages: list[CalcUsageData],
) -> dict[str, list[str]]:
    """Build dependency graph from binding_resolutions.

    Uses the already-computed binding_resolutions from _trace_dependencies()
    instead of re-resolving bindings. This guarantees consistency between
    the resolution phase and the dependency graph.

    Args:
        required_usages: List of required CalcUsageData.

    Returns:
        Dict mapping qualified_name -> list of dependency qualified_names.
    """
    graph: dict[str, list[str]] = {}
    required_names = {u.qualified_name for u in required_usages}

    for usage in required_usages:
        deps: list[str] = []

        for binding in usage.bindings:
            mapping_key = f"{usage.qualified_name}|{binding.param_name}"
            resolution = self._binding_resolutions.get(mapping_key)

            if resolution is None:
                continue
            if resolution.resolution_type != BindingResolutionType.MODULE_OUTPUT:
                continue

            # Extract producing usage from channel name
            source_usage = self._find_usage_for_channel(resolution.qualified_name)
            if (
                source_usage
                and source_usage.qualified_name in required_names
                and source_usage.qualified_name != usage.qualified_name
            ):
                if source_usage.qualified_name not in deps:
                    deps.append(source_usage.qualified_name)

        graph[usage.qualified_name] = deps

    return graph
```

---

## 7. The Guarantee

After `find_required_modules()` completes:

1. **Completeness**: For every non-template CalcUsage in `required_usages`,
   and for every input parameter (both bound and unbound), there exists exactly
   one entry in `binding_resolutions[f"{usage_qn}|{param_name}"]`.

2. **Determinism**: Each `BindingResolution` is either `ENTRY_POINT` or
   `MODULE_OUTPUT`. There is no third state. There are no unresolved bindings.

3. **Warning on fallback**: If resolution fails for a CHAIN or REFERENCE
   binding, a `logger.warning()` is emitted before creating the ENTRY_POINT
   fallback. This replaces the current silent fallthrough.

4. **No self-loops**: Self-referential bindings (where `source_path` resolves
   back to the same CalcUsage) are detected and treated as ENTRY_POINT.

5. **Consistency**: The dependency graph (`_build_dependency_graph()`) uses
   `binding_resolutions` from the resolution phase. There is no re-resolution
   that could produce different results.

---

## 8. Migration Strategy

### 8.1 Feature Flag

During migration, both the old cascade and new registry-based resolution run
in parallel. The feature flag controls which result is used.

```python
# In DependencyBacktracker.__init__:
self._use_output_registry = output_registry is not None

# In _trace_dependencies:
if self._use_output_registry:
    # New registry-based resolution (Paths C, D)
    ...
else:
    # Old cascade resolution (Strategies 0-5)
    ...
```

### 8.2 Parallel Validation

When both paths are active, assert that they produce identical
`binding_resolutions` for every binding:

```python
if self._use_output_registry and _PARALLEL_VALIDATION:
    old_resolution = self._resolve_via_cascade(binding, usage)
    new_resolution = self._resolve_via_registry(binding, usage)

    if old_resolution != new_resolution:
        logger.error(
            "PARALLEL VALIDATION DIVERGENCE:\n"
            "  Binding: %s on %s\n"
            "  Old: %s\n"
            "  New: %s",
            binding.source_path, usage.qualified_name,
            old_resolution, new_resolution,
        )
        # During validation: use old result (safe)
        # After validation passes: switch to new result
```

### 8.3 Validation Criteria

Parallel validation must pass on all four test models:

| Model | Expected Bindings | Known Divergences |
|---|---|---|
| solar_battery | ~200 | Bug 2 fix: 1 binding changes from ENTRY_POINT to MODULE_OUTPUT |
| e2e_attr_expr | ~30 | Bug 2 fix: `financial.total_capex` changes from ENTRY_POINT to MODULE_OUTPUT |
| chain_spike | ~10 | None expected |
| sample_model | ~50 | None expected |

**Bug 2 divergences are expected and correct** -- they represent the fix.
All other divergences indicate a regression and must be investigated.

### 8.4 Cut-over Steps

1. Parallel validation passes on all models (Item 3)
2. Remove old indexes from constructor (Item 4)
3. Remove `_resolve_binding_to_usage()` cascade (Item 4)
4. Remove `_build_design_attr_binding_index()` (Item 4)
5. Remove `_is_path_reference()` (Item 4)
6. Remove `_resolve_target_to_qualified()` (Item 4)
7. Remove `_build_channel_name_for_binding()` (Item 4)
8. Remove `_build_computed_attr_channel()` (Item 4)
9. Remove parallel validation code (Item 4)
10. Remove `_binding_to_entry_point` DEPRECATED field (separate cleanup task)

---

## 9. Removed Methods: Detailed Specification

### 9.1 `_resolve_binding_to_usage()` -- REMOVED

**Current**: Lines 776-871. A 7-strategy cascade that:
1. Tries exact match in `_output_catalog`
2. Parses dotted paths for instance name
3. Does transitive design attribute resolution
4. Does cross-file fuzzy matching (`.endswith()`)
5. Tries bare instance name lookup
6. Normalizes `::` to dotted for design attr lookup

**Why removed**: Replaced by:
- CHAIN path: `OutputRegistry.resolve()` (exact match)
- REFERENCE path: secondary resolution (leaf + parent scope)
- Design attribute fallback: `_resolve_to_design_attribute()`

### 9.2 `_build_design_attr_binding_index()` -- REMOVED

**Current**: Lines 873-909. Builds a dict mapping `parent.attr` to
target output paths, with recursive resolution via
`_resolve_target_to_qualified()`.

**Why removed**: Phase 4 of OutputRegistry construction handles transitive
design attribute aliases. The OutputRegistry's exact-match resolve handles
the transitive chain in a single lookup (the alias points directly to the
canonical channel).

### 9.3 `_build_channel_name_for_binding()` -- REMOVED

**Current**: Lines 710-774. Given a binding source and resolved usage,
builds the channel name by:
1. Checking `_design_attr_binding_index` for transitive chains
2. Parsing dotted format for output attribute name
3. Constructing `{usage_eqn}__{output_attr}` format

**Why removed**: The OutputRegistry `resolve()` returns the canonical channel
name directly. No post-resolution channel construction needed.

### 9.4 `_build_computed_attr_channel()` -- REMOVED

**Current**: Lines 623-627. Builds channel name for FORMULA computed attributes.

**Why removed**: Phase 1 FORMULA registration in OutputRegistry registers the
channel. The backtracker gets the channel from `resolve()`, not from building
it locally.

---

## 10. `BacktrackingResult` Changes

### 10.1 Field Deprecation Timeline

| Field | Status | Removal |
|---|---|---|
| `binding_resolutions` | **ACTIVE** -- single source of truth | Never (permanent) |
| `binding_to_entry_point` | **DEPRECATED** -- kept during migration | Remove after all consumers updated |
| `entry_point_sources` | **ACTIVE** -- used by phantom detection | Keep |
| `trace_log` | **ACTIVE** -- debug diagnostics | Keep |

### 10.2 No Schema Changes

The `BacktrackingResult` Pydantic model schema is unchanged. Only the internal
resolution logic changes. Downstream consumers (graph builder, parameter group
deriver) continue to read `binding_resolutions` as before.

---

## 11. Testing Strategy

### 11.1 Unit Tests: New Methods

```
tests/unit/test_backtracker_registry.py
```

**`_get_parent_part_for_usage()` tests:**
- 2-segment QN: `"Design__calc"` -> `"Design"`
- 3-segment QN: `"Design__plant__calc"` -> `"plant"`
- 5-segment QN: `"Design__plant__array__module__cost"` -> `"module"`
- 1-segment QN: `"calc"` -> `None`
- Empty QN: `""` -> `None`

**`_resolve_to_design_attribute()` tests:**
- DOTTED path with matching design attr -> returns qualified_name
- DOTTED path with no match -> returns None
- SYSML_QN path with exact qualified_name match -> returns qualified_name
- SYSML_QN path with leaf + parent match -> returns qualified_name
- SYSML_QN path with no match -> returns None
- Bare name with single match -> returns qualified_name
- Bare name with multiple matches -> returns first with warning
- Bare name with no match -> returns None

**`_find_usage_for_channel()` tests:**
- CalcUsage channel: `"Design__plant__calc__output"` -> CalcUsage with QN `"Design__plant__calc"`
- FORMULA channel: `"Design__plant__attr__attr"` -> None (synthetic module, not in `_usage_by_qualified`)
- Aggregation channel: `"Design__plant__array__cost__cost"` -> None (not a CalcUsage)
- Single-segment channel: `"output"` -> None

### 11.2 Unit Tests: Resolution Paths

**CHAIN resolution (Path C):**
- CHAIN binding with registry hit -> MODULE_OUTPUT with correct channel
- CHAIN binding with registry miss, design attr match -> ENTRY_POINT with design attr QN
- CHAIN binding with registry miss, no design attr -> ENTRY_POINT with warning

**REFERENCE resolution (Path D):**
- REFERENCE binding, exact registry match -> MODULE_OUTPUT (rare)
- REFERENCE binding, secondary resolution hit -> MODULE_OUTPUT with correct channel
- REFERENCE binding, no match, design attr fallback -> ENTRY_POINT with design attr QN
- REFERENCE binding, no match, no design attr -> ENTRY_POINT with warning

**LITERAL resolution (Path A):**
- LITERAL binding -> ENTRY_POINT (always)

**UNBOUND resolution (Path B):**
- Unbound param -> ENTRY_POINT (always)

### 11.3 Integration Tests: Parallel Validation

```
tests/integration/test_parallel_validation.py
```

- Run both old cascade and new registry resolution on synthetic model data
- Assert identical `binding_resolutions` for all non-Bug-2 bindings
- Assert Bug 2 binding diverges correctly (old: ENTRY_POINT, new: MODULE_OUTPUT)

### 11.4 Contract Tests: Registry-Backtracker Interface

```
tests/unit/test_registry_backtracker_contract.py
```

For every CHAIN binding in test fixtures:
1. Build OutputRegistry from the same CalcUsage/aggregation/computed attr data
2. Verify that `registry.resolve(binding.source_path)` returns a non-None result
3. Verify the returned channel matches the expected MODULE_OUTPUT channel

For every REFERENCE -> MODULE_OUTPUT binding in test fixtures:
1. Build OutputRegistry from the same data
2. Extract leaf_name and parent_part using `_get_parent_part_for_usage()`
3. Verify that `registry.resolve(f"{parent_part}.{leaf_name}")` returns non-None
4. Verify the returned channel matches the expected MODULE_OUTPUT channel

---

## 12. Traceability to Spike Data

| Spike | Finding | Impact on Spec |
|---|---|---|
| Spike 1 | source_path formats: SYSML_QN (REFERENCE), DOTTED (CHAIN), zero bare names | Section 5: dispatch by source_path format |
| Spike 5 | 119/123 REFERENCE -> ENTRY_POINT, 4/123 -> MODULE_OUTPUT (all computed attrs). SYSML_QN normalization broken. | Section 3.2 Path D: secondary resolution for 4 cases |
| Spike 8 | segments[-2] correct for all 4 REFERENCE->MODULE_OUTPUT cases. Key_C required. PartDef filter needed. | Section 4.1: `_get_parent_part_for_usage()` |
| Spike 9 | Issue 22: same-scope REFERENCE->aggregation verified. segments[-2] resolves CalcUsage+aggregation on same PartDef. | Section 4.1: known limitation documented |

---

## 13. Traceability to Design Document

| Design Section | Spec Section | Key Decisions |
|---|---|---|
| 08_algorithm S7 (Step 6) | Sections 3-5 | Three resolution paths replacing cascade |
| 08_algorithm S7 CHAIN | Section 3.2 Path C | OutputRegistry.resolve() for CHAIN |
| 08_algorithm S7 REFERENCE | Section 3.2 Path D | Secondary resolution with segments[-2] |
| 08_algorithm S7 `_resolve_to_design_attribute()` | Section 4.2 | Simplified method spec |
| 08_algorithm S7 `_get_parent_part_for_usage()` | Section 4.1 | Parent extraction spec |
| 08_algorithm S7 The guarantee | Section 7 | Completeness/determinism contract |
| 08_algorithm Appendix C | Section 8 | Migration strategy with parallel validation |

---

## 14. Open Questions

### 14.1 `_usage_by_name` Retention

The current code uses `_usage_by_name` in three places:
1. `find_required_modules()` target resolution (line 319)
2. `_resolve_binding_to_usage()` Strategy 2a and 3 (removed)
3. `_build_dependency_graph()` (refactored to use `binding_resolutions`)

After the refactoring, only use (1) remains. Decision: keep `_usage_by_name`
for target resolution backward compatibility, mark for removal in a future
cleanup when `find_required_modules()` is updated to use `_usage_by_qualified`.

### 14.2 DFS Traversal for Non-CalcUsage Channels

When a CHAIN or REFERENCE binding resolves to a FORMULA or aggregation channel,
`_find_usage_for_channel()` returns `None` (these aren't CalcUsages). The DFS
doesn't traverse into these modules. This is correct because:
- FORMULA modules' inputs resolve through the OutputRegistry normally (they are
  synthetic CalcUsages created in Step 4.5 that flow through backtracking)
- Aggregation modules' inputs are constructed by the graph builder from
  `ScopedAggregationData` (not from backtracker DFS)

### 14.3 `is_transitive` Field

The current code sets `is_transitive=True` when a binding goes through
`_design_attr_binding_index`. In the new design, Phase 4 transitive aliases
in the OutputRegistry make the transitive chain invisible to the backtracker --
`resolve()` returns the final canonical channel directly. The `is_transitive`
field will always be `False` in the new implementation. This is acceptable:
the field was only used for trace logging, not for downstream logic.

If transitive tracking is needed in the future, the OutputRegistry could return
metadata alongside the channel name (e.g., `ResolveResult(channel, is_alias)`).
This is deferred -- no current consumer needs it.

### 14.4 Self-Reference Guard

The current self-reference guard (lines 505-511) checks whether the resolved
usage is the same as the current usage. In the new design, CHAIN Path C resolves
to a channel, not a usage. The self-reference check needs to be adapted:

```python
# After resolving to MODULE_OUTPUT channel:
source_usage = self._find_usage_for_channel(channel)
if source_usage and source_usage.qualified_name == usage.qualified_name:
    logger.debug(
        "Self-reference detected for %s: %s -> %s, treating as entry point",
        param_name, binding.source_path, channel,
    )
    # Override to ENTRY_POINT
    ...
```

---

**Last Updated**: 2026-02-13
