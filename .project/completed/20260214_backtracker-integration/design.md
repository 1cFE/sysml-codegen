# Design: OutputRegistry Construction + Backtracker Integration

**Status:** Complete
**Owner:** Reid Westwood
**Created:** 2026-02-14 00:56 UTC
**Branch:** cost-pattern
**Commit:** d9b23c4

## Overview

Wire the OutputRegistry into the pipeline as Step 5.5, build a parallel resolution path in the backtracker (`_resolve_binding_via_registry()`), and validate zero divergences against the existing cascade on all 4 models.

## Related Artifacts

- **Spec:** `.project/active/backtracker-integration/spec.md`
- **Epic:** `.project/backlog/epic_output_registry_backtracker_redesign.md` (Item 3)
- **Design basis:** `.project/reports/08_algorithm_revised.md`
- **OutputRegistry:** `src/sysml_codegen/core/output_registry.py`
- **ChannelAlias:** `src/sysml_codegen/core/models.py:71-112`
- **Backtracker:** `src/sysml_codegen/analysis/dependency_backtracker.py`
- **Initialization:** `src/sysml_codegen/generation/initialization.py`
- **Item 1 tests:** `tests/unit/test_output_registry.py` (41 tests)
- **Bug 2 xfail:** `tests/integration/test_bug2_regression.py`

## Research Findings

### Existing Code Analysis

**Backtracker constructor (lines 117-261)** builds 5 indexes:
1. `_computed_attr_index` (lines 144-155): `dict[str, ComputedAttributeData]` -- 3 key patterns per FORMULA attr (`part.attr`, bare `attr`, `SysML::QN::attr`)
2. `_aggregation_output_index` (lines 159-197): `dict[str, str]` -- 3+ key patterns per aggregation (dotted, bare, full instance dotted, + BF-7 aliases)
3. `_output_catalog` (lines 225-238): `dict[str, CalcUsageData]` -- 2 key patterns (qualified `EQN__output`, simple `instance.output`)
4. `_design_attr_binding_index` (lines 241-243): `dict[str, str]` -- `parent.attr` -> target (built by `_build_design_attr_binding_index`)
5. `_usage_by_name` (lines 212-221): `dict[str, CalcUsageData]` -- instance_name -> CalcUsageData (secondary)

**`_trace_dependencies()` resolution flow (lines 379-621)**:
1. LITERAL -> ENTRY_POINT (line 430-445)
2. Check `_computed_attr_index` with 3 fallbacks: exact, dotted-bare, `::`-bare (lines 449-469)
3. Check `_aggregation_output_index` with 3 fallbacks: exact, dotted-bare, `::`-sanitized (lines 472-498)
4. Call `_resolve_binding_to_usage()` -- 7-strategy cascade (lines 776-871)
5. Self-reference guard: `source_usage.qualified_name == usage.qualified_name` (lines 505-511)
6. If resolved: build channel name -> MODULE_OUTPUT (lines 513-538)
7. If not resolved: `_resolve_to_design_attribute()` -> ENTRY_POINT (lines 539-601)

**`_resolve_binding_to_usage()` cascade (lines 776-871)**:
- Strategy 1: Exact `_output_catalog` match
- Strategy 2a: Dotted parse -> `_usage_by_name` instance match
- Strategy 4: `_design_attr_binding_index` transitive resolution (MOVED UP)
- Strategy 2b: Cross-file attribute matching in `_output_catalog`
- Strategy 3: Bare `_usage_by_name` match
- Strategy 5: `::` normalization -> `_design_attr_binding_index`

**`build_pipeline_context()` step sequence (lines 546-709)**:
```
Step 3:    Extract calc usages
Step 3.5:  Hierarchy + rewrite + scoping + CHAIN aliases
Step 3.6:  Enrich aggregation aliases (retained)
Step 4:    Design attributes
Step 4.5:  Computed attributes + EXPOSE_PURE aliases
Step 5:    Parameter group deriver
Step 6:    Backtracker (line 629)
Step 6.5:  Compile expressions
Step 7:    Build ComputationGraph
```

**OutputRegistry (existing, Item 1):**
- `register(canonical_channel, lookup_keys)` -- Phase 1
- `register_alias(alias, canonical_channel)` -- Phases 2-4
- `resolve(source_path) -> str | None` -- exact match only
- `derive_key_c(usage_qn, output_attr_name) -> str` -- Key_C derivation
- `is_transitive_default(default_value) -> bool` -- Phase 4 filter

**Test landscape:**
- `test_backtracker_computed_attrs.py`: 19 tests, 11 access `bt._computed_attr_index`
- `test_backtracker_aggregation.py`: 20 tests, 15 access `bt._aggregation_output_index`
- `test_output_registry.py`: 41 tests (all pass, comprehensive coverage)
- `test_output_registry_smoke.py`: 3 tests (real data, Phase 1 only)
- `test_bug2_regression.py`: 1 xfail test (EXPOSE_PURE `total_capex` -> ENTRY_POINT)
- `test_step36_diagnostic.py`: 3 tests (confirms Step 3.6 retention for param_name gap)
- `tests/fixtures/baseline_yaml/` does NOT exist yet

**Key data available at Step 5.5 insertion point:**
- `calc_usages` (Step 3)
- `calc_defs` (Step 2)
- `scoped_agg_data` (Step 3.5)
- `computed_attrs` (Step 4.5)
- `chain_aliases` + `expose_aliases` -> `all_channel_aliases` (Steps 3.5 + 4.5)
- `design_attrs` (Step 4)
- `hierarchy_data` (Step 3.5)

### Reusable Patterns

- `get_channel_name(usage_qn, output_attr_name)` at `core/qualified_names.py:98-100`: builds PQN-format channel names (`usage_qn__output_attr_name`)
- `OutputRegistry.derive_key_c()` at `core/output_registry.py:126-148`: strips design prefix, joins with `.`
- `sysml_to_python_qualified_name()` at `core/qualified_names.py:103-105`: `::` -> `__`
- `sanitize_name()` at `core/qualified_names.py:13-36`: Python-safe identifier
- `is_transitive_default()` at `core/output_registry.py:167-193`: Phase 4 candidate filter
- Class-scoped fixture pattern in integration tests (e.g., `test_bug2_regression.py`)

---

## Proposed Design

### High-Level Architecture

```
                           initialization.py
                      build_pipeline_context()
                                 |
  Step 3.5 ──> scoped_agg_data, chain_aliases
  Step 4.5 ──> computed_attrs, expose_aliases
  Step 5   ──> group_deriver
                                 |
                    ┌────────────▼────────────┐
                    │  Step 5.5 (NEW)         │
                    │  build_output_registry() │
                    │  4-phase registration    │
                    └────────────┬────────────┘
                                 |
                                 ▼
                    OutputRegistry instance
                                 |
                    ┌────────────▼────────────┐
                    │  Step 6: Backtracker     │
                    │  Receives OutputRegistry │
                    │  Parallel validation     │
                    └─────────────────────────┘
```

Within the backtracker, for every binding with `source_path`:

```
  Old path (authoritative):
    computed_attr_index ─> aggregation_output_index ─> cascade ─> design_attr ─> ENTRY_POINT

  New path (shadow):
    registry.resolve(source_path) ─> secondary REFERENCE resolution ─> design_attr ─> ENTRY_POINT

  Compare results. Log divergences. Old path wins.
```

### Component 1: `build_output_registry()` in initialization.py

**Purpose:** Construct a fully-populated OutputRegistry from pipeline data, implementing the 4-phase registration protocol.

**Location:** `src/sysml_codegen/generation/initialization.py` (new function, ~120 lines)

**Signature:**
```python
def build_output_registry(
    calc_usages: list[CalcUsageData],
    calc_defs: list[CalculationDefinitionData],
    aggregation_data: list[ScopedAggregationData],
    computed_attributes: list[ComputedAttributeData],
    channel_aliases: list[ChannelAlias],
    design_attributes: dict[Path, list[DesignAttributeData]],
) -> OutputRegistry:
```

**Phase 1: Canonical channels** (~50 lines)

For each CalcUsage + its CalcDef outputs:
```python
for usage in calc_usages:
    calc_def = calc_def_by_name.get(usage.calc_def_name)
    if not calc_def:
        continue
    for attr in calc_def.output_attributes:
        canonical = get_channel_name(usage.qualified_name, attr.name)
        key_a = f"{usage.instance_name}.{attr.name}"
        key_b = canonical  # EQN format (self-registered by register())
        key_c = OutputRegistry.derive_key_c(usage.qualified_name, attr.name)
        registry.register(canonical, [key_a, key_c])
```

For each ScopedAggregationData:
```python
for agg in aggregation_data:
    canonical = get_channel_name(agg.module_eqn, agg.expression.attribute_name)
    instance_parts = agg.instance_path.split("__")
    part_usage = instance_parts[-1] if instance_parts else agg.expression.owning_part_name

    key_d = f"{part_usage}.{agg.expression.attribute_name}"
    key_e = ".".join(instance_parts + [agg.expression.attribute_name])
    keys = [key_d, key_e]

    # Bare key
    keys.append(agg.expression.attribute_name)

    # BF-7 alias variants (from agg.expression.aliases including Step 3.6 param_name aliases)
    for alias_name in agg.expression.aliases:
        keys.append(f"{part_usage}.{alias_name}")
        keys.append(alias_name)
        keys.append(".".join(instance_parts + [alias_name]))

    registry.register(canonical, keys)
```

For each FORMULA computed attribute (FULLY_COMPILABLE only):
```python
for ca in computed_attributes:
    if ca.classification != ComputedAttributeClassification.FORMULA:
        continue
    if ca.compilability != Compilability.FULLY_COMPILABLE:
        continue
    part_qn_python = sysml_to_python_qualified_name(ca.owning_part_qualified_name)
    module_eqn = f"{part_qn_python}__{ca.python_name}"
    canonical = get_channel_name(module_eqn, ca.python_name)

    key_f = f"{ca.owning_part_name}.{ca.python_name}"
    keys = [key_f, ca.python_name]  # dotted + bare

    # SysML QN key
    if ca.owning_part_qualified_name:
        sysml_qn = f"{ca.owning_part_qualified_name}::{ca.name}"
        keys.append(sysml_qn)

    registry.register(canonical, keys)
```

**Phase 2: CHAIN aliases** (~10 lines)
```python
for alias in channel_aliases:
    if alias.source == "redefinition":
        resolved = registry.resolve(alias.canonical_name)
        if resolved:
            registry.register_alias(alias.alias_name, resolved)
        else:
            logger.warning("Phase 2: CHAIN alias '%s' canonical '%s' not in registry",
                           alias.alias_name, alias.canonical_name)
```

**Phase 3: EXPOSE_PURE aliases** (~10 lines)
```python
for alias in channel_aliases:
    if alias.source == "expose_pure":
        owning_part_short = alias.owning_part_qn.split("__")[-1]
        scoped_key = f"{owning_part_short}.{alias.alias_name}"
        resolved = registry.resolve(alias.canonical_name)
        if resolved:
            registry.register_alias(scoped_key, resolved)
        else:
            logger.warning("Phase 3: EXPOSE_PURE alias '%s' canonical '%s' not in registry",
                           scoped_key, alias.canonical_name)
```

**Phase 4: Transitive design attribute aliases** (~15 lines)
```python
for _path, attrs in design_attributes.items():
    for attr in attrs:
        if not is_transitive_default(attr.default_value):
            continue
        key = f"{attr.parent_part}.{attr.name}"
        resolved = registry.resolve(str(attr.default_value))
        if resolved:
            registry.register_alias(key, resolved)
```

**Logging:** Summary log at end with counts per phase.

**Duplication note:** Phase 1 registration intentionally duplicates key-generation logic from the backtracker constructor (lines 144-197). This is necessary during the parallel validation phase -- both old indexes and new registry must exist simultaneously. Add `# TODO(Item-4): Remove after OutputRegistry cut-over` comments to the backtracker constructor's index-building blocks for traceability.

### Component 2: Step 5.5 Wiring in `build_pipeline_context()`

**Purpose:** Insert registry construction between Step 5 and Step 6.

**Location:** `src/sysml_codegen/generation/initialization.py:625-635` (existing Step 5/6 boundary)

**Changes:**
```python
# Step 5: Create parameter group deriver (uses filtered design_attrs)
group_deriver = ParameterGroupDeriver(design_attrs, calc_usages, calc_defs)

# Step 5.5: Build OutputRegistry (NEW)
from sysml_codegen.core.output_registry import OutputRegistry, is_transitive_default
output_registry = build_output_registry(
    calc_usages=calc_usages,
    calc_defs=calc_defs,
    aggregation_data=scoped_agg_data,
    computed_attributes=computed_attrs,
    channel_aliases=all_channel_aliases,
    design_attributes=design_attrs,
)

# Step 6: Create backtracker and run (MODIFIED - pass output_registry)
backtracker = DependencyBacktracker(
    calc_usages,
    calc_defs,
    design_attributes=design_attrs,
    computed_attributes=computed_attrs,
    aggregation_data=scoped_agg_data,
    output_registry=output_registry,  # NEW
)
```

**PipelineContext addition:** Add `output_registry: OutputRegistry | None = None` field to PipelineContext dataclass (for downstream consumers and testing). Import at top of file.

### Component 3: Backtracker Modifications

**Purpose:** Accept OutputRegistry, add parallel resolution path, compare results.

**Location:** `src/sysml_codegen/analysis/dependency_backtracker.py`

#### 3a. Constructor Change (line 117-124)

Add `output_registry` parameter:
```python
def __init__(
    self,
    all_usages: list[CalcUsageData],
    calc_defs: list,
    design_attributes: dict[Path, list[DesignAttributeData]] | None = None,
    computed_attributes: list | None = None,
    aggregation_data: list | None = None,
    output_registry: OutputRegistry | None = None,  # NEW
):
```

Store: `self._output_registry = output_registry`

Imports (TYPE_CHECKING guard):
```python
if TYPE_CHECKING:
    from sysml_codegen.core.output_registry import OutputRegistry
```
The `BindingInfo` type is already available via `agentic_mbse.sysml.data_models` under TYPE_CHECKING.

#### 3b. New Method: `_resolve_binding_via_registry()`

**Purpose:** Resolve a single binding using the OutputRegistry (new path).

**Location:** New method on `DependencyBacktracker` (~60 lines)

Note: `BindingInfo` type available via existing `from __future__ import annotations` + TYPE_CHECKING import from `agentic_mbse.sysml.data_models`.

```python
def _resolve_binding_via_registry(
    self,
    binding: BindingInfo,
    usage: CalcUsageData,
) -> BindingResolution:
    """Resolve a binding via the OutputRegistry (parallel validation path).

    Resolution order:
    1. registry.resolve(source_path) -> MODULE_OUTPUT
    2. REFERENCE secondary: leaf + parent scope -> MODULE_OUTPUT
    3. _resolve_to_design_attribute() -> ENTRY_POINT
    4. Fallback -> ENTRY_POINT with warning
    """
    source_path = binding.source_path
    param_name = binding.param_name

    # Step 1: Direct registry resolve
    channel = self._output_registry.resolve(source_path)

    if channel is not None:
        # Self-reference guard (adapted for channel-based resolution)
        producing_usage_qn = channel.rsplit("__", 1)[0] if "__" in channel else channel
        if producing_usage_qn == usage.qualified_name:
            logger.debug("Registry self-reference: %s -> %s, treating as entry point",
                         source_path, channel)
            channel = None

    # Step 2: REFERENCE secondary resolution (if step 1 didn't resolve)
    if channel is None and binding.binding_type == BindingType.REFERENCE:
        channel = self._resolve_reference_via_registry(source_path, usage)

    if channel is not None:
        return BindingResolution(
            resolution_type=BindingResolutionType.MODULE_OUTPUT,
            qualified_name=channel,
            source_path=source_path,
            is_transitive=False,  # Always False in registry path
        )

    # Step 3: Design attribute resolution (existing method, unchanged)
    design_attr_qn = self._resolve_to_design_attribute(source_path, usage)
    if design_attr_qn:
        return BindingResolution(
            resolution_type=BindingResolutionType.ENTRY_POINT,
            qualified_name=design_attr_qn,
            source_path=source_path,
            is_transitive=False,
        )

    # Step 4: Fallback entry point with warning
    logger.warning(
        "Registry unresolved: %s|%s source_path='%s'",
        usage.qualified_name, param_name, source_path,
    )
    return BindingResolution(
        resolution_type=BindingResolutionType.ENTRY_POINT,
        qualified_name=f"{usage.qualified_name}__{param_name}",
        source_path=source_path,
        is_transitive=False,
    )
```

#### 3c. New Helper: `_get_parent_part_for_usage()`

```python
def _get_parent_part_for_usage(self, usage: CalcUsageData) -> str | None:
    """Return segments[-2] of usage.qualified_name (the parent part name).

    E.g., "Design__solar_battery_plant__lcoe" -> "solar_battery_plant"
    """
    segments = usage.qualified_name.split("__")
    if len(segments) >= 2:
        return segments[-2]
    return None
```

#### 3d. New Helper: `_resolve_reference_via_registry()`

```python
def _resolve_reference_via_registry(
    self,
    source_path: str,
    usage: CalcUsageData,
) -> str | None:
    """Secondary REFERENCE resolution via leaf + parent scope.

    For REFERENCE bindings (FeatureReferenceExpression), the source_path
    is often a SysML qualified name (Package::Part::attr) or dotted path.
    Extract the leaf, combine with parent_part from the consuming CalcUsage,
    and resolve against the registry.
    """
    # Extract leaf name
    if "::" in source_path:
        leaf = source_path.rsplit("::", 1)[-1]
    elif "." in source_path:
        leaf = source_path.rsplit(".", 1)[-1]
    else:
        leaf = source_path

    parent_part = self._get_parent_part_for_usage(usage)
    if parent_part:
        scoped_key = f"{parent_part}.{leaf}"
        channel = self._output_registry.resolve(scoped_key)
        if channel is not None:
            # Self-reference guard
            producing_usage_qn = channel.rsplit("__", 1)[0] if "__" in channel else channel
            if producing_usage_qn != usage.qualified_name:
                return channel

    return None
```

#### 3e. Parallel Validation in `_trace_dependencies()`

**Purpose:** After the old path stores its result, call the new path and compare. Log divergences.

**Approach:** Extract a `_compare_with_registry()` helper. Call it at **3 insertion points** in the existing `_trace_dependencies()` loop -- one per resolution exit. No control flow restructuring; existing `continue` statements and `if/else` structure are untouched.

**Helper method:**
```python
def _compare_with_registry(
    self,
    binding: BindingInfo,
    usage: CalcUsageData,
    mapping_key: str,
) -> None:
    """Compare old-path result with registry resolution. Log divergences."""
    if not binding.source_path or mapping_key not in self._binding_resolutions:
        return
    new_resolution = self._resolve_binding_via_registry(binding, usage)
    old_resolution = self._binding_resolutions[mapping_key]
    if (new_resolution.resolution_type != old_resolution.resolution_type or
            new_resolution.qualified_name != old_resolution.qualified_name):
        logger.warning(
            "PARALLEL DIVERGENCE: %s|%s: old=%s/%s new=%s/%s",
            usage.qualified_name, binding.param_name,
            old_resolution.resolution_type.value,
            old_resolution.qualified_name,
            new_resolution.resolution_type.value,
            new_resolution.qualified_name,
        )
```

**3 insertion points** (each guarded by `if self._output_registry is not None:`):

| # | Location | Old-path outcome | Line |
|---|----------|-----------------|------|
| 1 | Before `continue` at line 469 | Computed attr -> MODULE_OUTPUT | `dependency_backtracker.py:469` |
| 2 | Before `continue` at line 498 | Aggregation -> MODULE_OUTPUT | `dependency_backtracker.py:498` |
| 3 | End of `if binding.source_path:` block, ~line 601 | Cascade resolved (MODULE_OUTPUT) or unresolved (ENTRY_POINT) | `dependency_backtracker.py:~601` |

At each point, insert:
```python
if self._output_registry is not None:
    self._compare_with_registry(binding, usage, mapping_key)
```

**Why 3, not 4:** The cascade `if source_usage: ... else: ...` block (lines 513-600) has two outcomes but only one exit point -- both branches fall through to the same place at ~line 601. A single comparison call after the `if/else` block covers both MODULE_OUTPUT and ENTRY_POINT outcomes from the cascade.

### Component 4: Baseline YAML Capture

**Purpose:** Capture pipeline YAML for all 4 models as committed fixtures for Item 4 diff validation.

**Location:** `tests/fixtures/baseline_yaml/` (new directory)

**Approach:** Write a standalone script/test that runs `build_pipeline_context()` + YAML generation for each model and saves the output:
```
tests/fixtures/baseline_yaml/
    solar_battery.yaml
    attr_expr_probe.yaml
    chain_spike.yaml
    sample_model.yaml
```

**Implementation:** Use the existing pipeline + generation path to produce the YAML. The simplest approach is a test fixture that:
1. Builds `PipelineContext` for each model
2. Renders the pipeline template
3. Writes YAML to `tests/fixtures/baseline_yaml/`

This should be done as the **first commit** before any integration code, so baselines reflect the pre-change state.

### Component 5: Contract Tests

**Purpose:** TDD -- verify the key format agreement between `build_output_registry()` and the backtracker's registry queries.

**Location:** `tests/unit/test_output_registry_construction.py` (new file)

**Approach:** For each binding type, verify that the key the backtracker would construct for `registry.resolve()` actually exists in a registry built from the same data.

**Key test cases:**
1. CHAIN binding `source_path` (dotted format) -> `registry.resolve(source_path)` returns non-None
2. REFERENCE binding -> `registry.resolve(f"{parent_part}.{leaf}")` returns non-None for the 4 known MODULE_OUTPUT cases
3. Aggregation binding -> `registry.resolve(source_path)` returns correct channel
4. FORMULA computed attr binding -> `registry.resolve(source_path)` returns correct channel
5. EXPOSE_PURE `total_capex` scoped key -> `registry.resolve("e2e_plant.total_capex")` returns MODULE_OUTPUT channel (Bug 2 fix proof)

**Fixture strategy:** Factory functions producing synthetic data matching spike results (same pattern as `test_output_registry.py`). For integration-level contract tests, use real model data.

### Component 6: Parallel Validation Integration Tests

**Purpose:** Run both paths on all 4 real models, assert zero divergences.

**Location:** `tests/integration/test_parallel_validation.py` (new file)

**Test structure:** One class per model (class-scoped fixture avoids redundant SysIDE loading). The pattern follows existing integration tests (e.g., `test_bug2_regression.py`).

```python
import logging
from pathlib import Path

import pytest
from sysml_codegen.generation.initialization import build_pipeline_context


class TestParallelValidationSolarBattery:
    @pytest.fixture(scope="class")
    def pipeline_context(self, solar_battery_model_path):
        return build_pipeline_context([solar_battery_model_path])

    def test_zero_divergences(self, pipeline_context, caplog):
        with caplog.at_level(logging.WARNING):
            pass  # Pipeline already ran during fixture setup
        divergences = [r for r in caplog.records if "PARALLEL DIVERGENCE" in r.message]
        assert divergences == [], f"Divergences: {[r.message for r in divergences]}"


class TestParallelValidationAttrExprProbe:
    @pytest.fixture(scope="class")
    def pipeline_context(self, fixtures_path):
        return build_pipeline_context([fixtures_path / "attr_expr_probe"])

    def test_zero_divergences(self, pipeline_context, caplog):
        # ... same pattern ...


class TestParallelValidationChainSpike:
    @pytest.fixture(scope="class")
    def pipeline_context(self, chain_spike_model_path):
        return build_pipeline_context([chain_spike_model_path])

    def test_zero_divergences(self, pipeline_context, caplog):
        # ... same pattern ...


class TestParallelValidationSampleModel:
    @pytest.fixture(scope="class")
    def pipeline_context(self, sample_model_path):
        return build_pipeline_context([sample_model_path])

    def test_zero_divergences(self, pipeline_context, caplog):
        # ... same pattern ...
```

**Why separate classes instead of `@pytest.mark.parametrize`:** Class-scoped fixtures can't be parametrized with session-level model paths cleanly. Separate classes also allow model-specific targeted tests (Bug 2 on attr_expr_probe, REFERENCE cases on solar_battery) alongside the shared zero-divergence check.

**Additional specific tests:**
- Bug 2: Assert `financial.total_capex` binding resolves to MODULE_OUTPUT in new path
- REFERENCE secondary: Assert 4 specific cases (`p_net_kw`, `capital_cost`, `power_mw`, `annual_om`) resolve to MODULE_OUTPUT
- Unresolved warning: Assert unresolved bindings produce `logger.warning()`

### Component 7: Test Migration Audit

**Purpose:** Categorize all 39 tests accessing internal indexes for Item 4 migration.

**Location:** `.project/active/backtracker-integration/test_migration_audit.md` (new file)

**Categories:**
- **(a) Registration behavior** -- tests that verify what keys exist in `_computed_attr_index` or `_aggregation_output_index` -> migrate to test `build_output_registry()` registration
- **(b) Resolution behavior** -- tests that verify binding resolution outcomes (MODULE_OUTPUT, ENTRY_POINT) -> rewrite to use `registry.resolve()` or check `_binding_resolutions`
- **(c) Integration** -- tests that verify end-to-end binding resolution through `_trace_dependencies()` -> keep, update to not access internal indexes

---

## Potential Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Phase 1 registration misses a key format used by bindings | High - divergences | Contract tests verify every binding key exists. Real-model integration tests catch gaps. |
| EXPOSE_PURE Phase 3 scoping mismatch | Medium - Bug 2 fix fails | Spike 8 validated the scoping format. Integration test specifically asserts `total_capex` resolution. |
| REFERENCE secondary resolution `segments[-2]` wrong for edge cases | Low | Spike 8+9 validated for all 4 REFERENCE->MODULE_OUTPUT cases. Falls back to ENTRY_POINT with warning. |
| Self-reference guard channel parsing fails | Low | Channel format is deterministic: `usage_qn__output_name`. `rsplit("__", 1)[0]` is robust. |
| Step 3.6 param_name aliases not in registry | Medium - divergences on aggregation | Phase 1 registration explicitly includes `agg.expression.aliases` which contains Step 3.6-enriched aliases. Like-for-like comparison ensured. |
| `_compare_with_registry` at insertion points missed | Medium - silent untested bindings | There are exactly 3 insertion points (see Section 3e table). Code review must verify all 3 are present. |
| `is_transitive` divergence causes noise | Low | Spec explicitly excludes `is_transitive` from comparison. Only `resolution_type` and `qualified_name` compared. |

## Integration Strategy

- **Build order:** (1) Baseline YAML capture, (2) Contract tests (failing), (3) `build_output_registry()`, (4) Contract tests pass, (5) Backtracker `_resolve_binding_via_registry()` + helpers, (6) Parallel validation wiring, (7) Integration tests, (8) Test migration audit
- **Step 5.5 placement:** Between group deriver and backtracker -- all inputs available, output consumed by backtracker
- **Old path untouched:** All 5 indexes and the cascade remain. Only addition is `output_registry` parameter and `_compare_with_registry()` calls
- **Backward compatibility:** `output_registry=None` means no parallel validation (safe default for existing tests)

## Validation Approach

### Testing Strategy

1. **Contract tests (TDD):** Written first, fail initially, go green when `build_output_registry()` is implemented
2. **Unit tests for `build_output_registry()`:** Synthetic data, verify registration counts and key resolution
3. **Unit tests for `_resolve_binding_via_registry()`:** Synthetic bindings, verify resolution outcomes
4. **Integration tests:** Real models, zero-divergence assertion via `caplog` scanning
5. **Bug 2 regression:** Assert `total_capex` resolves to MODULE_OUTPUT in new path (integration test, not the xfail -- that stays for Item 4)
6. **Existing tests:** All 39 computed_attr + aggregation tests must pass unchanged (old path untouched)
7. **Full suite:** `uv run pytest tests/` and `uv run mypy src/` clean

### Success Criteria (from spec)

- [ ] `build_output_registry()` exists with 4-phase protocol
- [ ] Zero divergences on all 4 models
- [ ] Bug 2: `financial.total_capex` -> MODULE_OUTPUT via new path
- [ ] REFERENCE secondary: 4 cases -> MODULE_OUTPUT
- [ ] Unresolved bindings produce `logger.warning()`
- [ ] Contract tests verify key format agreement
- [ ] Test migration audit complete
- [ ] Baseline YAML captured for all 4 models
- [ ] All existing tests pass

---

Next Step: After approval -> `/_my_plan` for implementation sequencing, then `/_my_implement`
