# Design: OutputRegistry Foundation

**Status:** Complete
**Owner:** Reid Westwood
**Created:** 2026-02-13 22:01 UTC
**Complexity:** MEDIUM
**Branch:** cost-pattern
**Commit:** cfe48e0

## Overview

Create the `ChannelAlias` Pydantic model and `OutputRegistry` class -- the foundational data structures for replacing the backtracker's 5 ad-hoc indexes with a single exact-match lookup. This item is purely additive: no existing code is modified.

## Related Artifacts

- **Spec:** `.project/active/output-registry-foundation/spec.md`
- **Epic:** `.project/backlog/epic_output_registry_backtracker_redesign.md` (Item 1)
- **Design basis:** `.project/reports/08_algorithm_revised.md` (Sections 4, 6, 12)
- **Spike data:** `.project/research/20260213_spike_results_output_registry_e2e.md` (Spike 8)
- **Bug 2 analysis:** `.project/research/20260213-152845_bug2-expose-calcusage-wiring-persistent-failure.md`
- **Spec review synthesis:** `.project/reports/spec_review_synthesis.md` (C1, C2 resolutions)

## Research Findings

### Existing Patterns in `core/models.py`

The file follows a consistent pattern (`core/models.py:1-73`):
- Pydantic `BaseModel` subclasses with docstrings including attribute descriptions and examples
- `str` Enum for classification types
- `__all__` export list at the bottom
- No validators or computed fields -- plain data containers

`ChannelAlias` fits naturally alongside `BindingResolution` as a pipeline-level data model consumed across layers.

### Existing `core/` Module Structure

`core/__init__.py` re-exports all public symbols from submodules (`identifier_types`, `models`, `qualified_names`). New symbols from `models.py` and a new `output_registry.py` module need to be added to `__init__.py`.

### Key Utility: `get_channel_name()` (`core/qualified_names.py:98-100`)

```python
def get_channel_name(usage_qualified_name: str, output_attr_name: str) -> str:
    return f"{usage_qualified_name}__{output_attr_name}"
```

This produces Key_B format (EQN channel names). The OutputRegistry will use this directly for Phase 1 CalcUsage registration.

### No Existing Key_C Utility

`core/qualified_names.py` has no function for Key_C derivation (dotted hierarchy path). The Key_C formula is: `".".join(qn.split("__")[1:]) + "." + output_name`. This needs to be added as a method on `OutputRegistry` or as a standalone utility.

**Decision:** Place it as a `@staticmethod` on `OutputRegistry` since it's specific to registry key construction and not a general-purpose qualified name operation. This keeps `qualified_names.py` focused on ADR-003 identifiers.

### Test Factory Pattern (from `test_backtracker_aggregation.py:26-78`)

Existing tests use:
- Module-level factory functions (`_make_scoped_agg()`, `_make_calc_usage()`) with sensible defaults
- Lightweight `@dataclass` mocks (`SimpleCalcDef`, `SimpleAttrInfo`) for minimal dependency
- `pytest` class grouping (`class TestAggregationOutputIndex:`)
- Direct assertion on internal state (`bt._aggregation_output_index`)

The OutputRegistry tests will follow the same factory function pattern but construct `OutputRegistry` directly instead of going through the backtracker.

### Bug 2 Integration Test Pattern (from `test_hierarchy_e2e.py:1-50`)

Integration tests use:
- `build_pipeline_context([model_path])` to run the full pipeline
- `PipelineContext` fields to access backtracker and results
- `FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"`
- `scope="class"` fixtures for expensive pipeline runs

The Bug 2 xfail test will follow this pattern, loading `attr_expr_probe` and checking `binding_resolutions`.

### Bug 2 Root Cause (from Bug 2 research document)

The failure path: `financial` CalcUsage binds to `E2EDesign::e2e_plant::total_capex` (REFERENCE). Strategy 5 normalizes to `e2e_plant.total_capex`, finds it in `_design_attr_binding_index` with `default_value = "component_cost.total_cost"`. Second hop tries to resolve `component_cost.total_cost` via the output catalog. For virtual CalcUsages, `instance_name` is the full QN (`E2EAttrExprDesign__e2e_plant__component_cost`), so `component_cost.total_cost` doesn't match Key_A. Resolution falls through to ENTRY_POINT silently.

The xfail test must use the real `attr_expr_probe` model (not synthetic data) to capture this exact failure mode.

---

## Proposed Design

### Component 1: `ChannelAlias` Pydantic Model

**File:** `src/sysml_codegen/core/models.py`
**Location:** After `BindingResolution` class (line 68), before `__all__`

```python
class ChannelAlias(BaseModel):
    """An explicit alias for a pipeline output channel.

    Aliases map alternative lookup keys to canonical channel names.
    They are produced by two sources:
    - `:>>` CHAIN redefinitions (source="redefinition")
    - EXPOSE_PURE computed attributes (source="expose_pure")

    All fields use scoped dotted keys -- no bare names, no SYSML_QN (::) format.

    Attributes:
        alias_name: The alias lookup key. For CHAIN aliases, this is scoped
            (e.g., "solar_array.total_capex"). For EXPOSE_PURE aliases, this
            is bare (e.g., "total_capex") -- scoping happens at registration.
        canonical_name: The dotted target key that resolves to a canonical
            channel via the OutputRegistry (e.g., "component_cost.total_cost").
        owning_part_qn: Qualified name of the PartDef/PartUsage where the
            alias originates (e.g., "SolarBatteryLibrary__Solar_Array").
        source: Provenance tag: "redefinition" | "expose_pure" | "design_override".

    Example (CHAIN redefinition):
        ChannelAlias(
            alias_name="solar_battery_plant.solar_array.total_capex",
            canonical_name="solar_battery_plant.solar_array.cost_model.total_cost",
            owning_part_qn="SolarBatteryLibrary__Solar_Array",
            source="redefinition",
        )

    Example (EXPOSE_PURE):
        ChannelAlias(
            alias_name="total_capex",
            canonical_name="component_cost.total_cost",
            owning_part_qn="E2EAttrExprDesign__e2e_plant",
            source="expose_pure",
        )
    """

    alias_name: str
    canonical_name: str
    owning_part_qn: str
    source: Literal["redefinition", "expose_pure", "design_override"]
```

**Note:** `Literal` import from `typing` required. This provides Pydantic validation at construction time for zero cost -- the three values are already enumerated in the docstring.

**`__all__` update:** Add `"ChannelAlias"` to the existing list.

**`core/__init__.py` update:** Add `ChannelAlias` to the imports from `core.models` and to `__all__`.

### Component 2: `OutputRegistry` Class

**File:** `src/sysml_codegen/core/output_registry.py` (new)

**Internal state:**
- `_index: dict[str, str]` -- maps every lookup key (Key_A through Key_F, plus aliases) to a canonical channel name. This is the single lookup table.
- `_canonical: set[str]` -- set of all registered canonical channel names. Used by `register_alias()` to enforce the phase ordering contract (alias target must already be registered).

**Interface:**

```python
import logging
from typing import Any

logger = logging.getLogger(__name__)


class OutputRegistry:
    """Single lookup for resolving binding source_paths to canonical channel names.

    Replaces the backtracker's 5 ad-hoc indexes with one exact-match dict.
    No normalization, no cascade, no fallback. If a key isn't registered,
    resolve() returns None.

    Usage protocol (4-phase registration):
        Phase 1: register() -- CalcUsage outputs (Key_A, Key_B, Key_C),
                 aggregation outputs (Key_D, Key_E), FORMULA outputs (Key_F)
        Phase 2: register_alias() -- CHAIN redefinition aliases
        Phase 3: register_alias() -- EXPOSE_PURE aliases (PartUsage only)
        Phase 4: register_alias() -- Transitive design attribute aliases
    """

    def __init__(self) -> None:
        self._index: dict[str, str] = {}
        self._canonical: set[str] = set()

    def register(self, canonical_channel: str, lookup_keys: list[str]) -> None:
        """Register a canonical channel with its lookup keys (Phase 1).

        The canonical_channel itself is also registered as a self-referencing
        key, so resolve(canonical_channel) always works.

        Collision policy: refuse overwrite. If a key already maps to a
        different canonical channel, log a warning and keep the first
        registration. This prevents silent mis-wiring from duplicate keys.

        Args:
            canonical_channel: The PQN-format channel name
                (e.g., "Design__plant__lcoe__lcoe_per_mwh").
            lookup_keys: List of alternative key formats (Key_A, Key_B,
                Key_C, etc.) that should resolve to this channel.
        """
        ...

    def register_alias(self, alias: str, canonical_channel: str) -> None:
        """Register an alias pointing to an existing canonical channel (Phases 2-4).

        Enforces phase ordering: the canonical_channel MUST already be
        registered (via register() or a prior register_alias()). If not,
        logs a warning and skips -- this catches phase ordering violations
        and unresolvable alias targets.

        Note: The source design document (08_algorithm_revised.md, Section 12)
        uses ``assert`` for phase ordering enforcement. This implementation
        intentionally uses ``logger.warning()`` + skip instead, because an
        assert crash on data issues in a production pipeline is too harsh --
        a warning with diagnostic context is more actionable. The spec (FR-2)
        allows either "assert/warn", so this satisfies the contract.

        Collision policy: same as register() -- refuse overwrite on collision.

        Args:
            alias: The alias lookup key (scoped dotted format).
            canonical_channel: The canonical channel this alias points to.
                Must already exist in the registry.
        """
        ...

    def resolve(self, source_path: str) -> str | None:
        """Resolve a binding source_path to a canonical channel name.

        EXACT MATCH ONLY. No normalization, no :: -> . conversion,
        no bare-name fallback. This is a pure dict lookup.

        Empirically validated contracts (do NOT add normalization):
        - Spike 4: Zero bare-name references across 94 bindings
        - Spike 5: SYSML_QN normalization is broken (consuming path
          differs from producing path)

        Args:
            source_path: The binding's source_path in dotted format.

        Returns:
            Canonical channel name, or None if not found.
        """
        ...

    @staticmethod
    def derive_key_c(usage_qualified_name: str, output_attr_name: str) -> str:
        """Derive Key_C: dotted hierarchy path (strips design prefix).

        Key_C is CRITICAL for Phase 2 CHAIN alias resolution. Spike 8
        confirmed: ALL 41 Phase 2 CHAIN aliases in solar_battery resolve
        EXCLUSIVELY via Key_C.

        Algorithm: split QN on '__', drop segments[0] (design PartDef
        prefix), join remaining with '.', append '.' + output_attr_name.

        Args:
            usage_qualified_name: The CalcUsage EQN
                (e.g., "SolarBatteryDesign__solar_battery_plant__lcoe").
            output_attr_name: The output attribute name
                (e.g., "lcoe_per_mwh").

        Returns:
            Dotted hierarchy path
            (e.g., "solar_battery_plant.lcoe.lcoe_per_mwh").
        """
        segments = usage_qualified_name.split("__")
        return ".".join(segments[1:]) + "." + output_attr_name

    def __len__(self) -> int:
        """Number of lookup keys in the registry (for diagnostics)."""
        return len(self._index)

    def __repr__(self) -> str:
        """Diagnostic repr showing key and channel counts."""
        return (
            f"OutputRegistry(keys={len(self._index)}, "
            f"channels={len(self._canonical)})"
        )

    @property
    def canonical_channels(self) -> frozenset[str]:
        """Read-only view of all canonical channel names."""
        return frozenset(self._canonical)
```

**Implementation details for `register()`:**

```python
def register(self, canonical_channel: str, lookup_keys: list[str]) -> None:
    self._canonical.add(canonical_channel)
    # Self-register the canonical channel name
    if canonical_channel not in self._index:
        self._index[canonical_channel] = canonical_channel
    for key in lookup_keys:
        if key in self._index:
            if self._index[key] != canonical_channel:
                logger.warning(
                    "OutputRegistry key collision: '%s' already maps to '%s', "
                    "refusing to overwrite with '%s'",
                    key, self._index[key], canonical_channel,
                )
            continue  # skip duplicate or collision
        self._index[key] = canonical_channel
```

**Implementation details for `register_alias()`:**

```python
def register_alias(self, alias: str, canonical_channel: str) -> None:
    if canonical_channel not in self._canonical:
        logger.warning(
            "OutputRegistry alias '%s' targets unregistered channel '%s' "
            "(possible phase ordering violation)",
            alias, canonical_channel,
        )
        return
    if alias in self._index:
        if self._index[alias] != canonical_channel:
            logger.warning(
                "OutputRegistry key collision: '%s' already maps to '%s', "
                "refusing to overwrite with '%s'",
                alias, self._index[alias], canonical_channel,
            )
        return
    self._index[alias] = canonical_channel
```

**Implementation details for `resolve()`:**

```python
def resolve(self, source_path: str) -> str | None:
    return self._index.get(source_path)
```

### Component 3: `is_transitive_default()` Utility

**File:** `src/sysml_codegen/core/output_registry.py` (module-level function)

**Purpose:** Filter design attribute `default_value` to identify dotted-path defaults (transitive aliases) vs. numeric literals, `None`, or bare names.

```python
def is_transitive_default(default_value: Any) -> bool:
    """Check if a design attribute default_value is a dotted-path reference.

    A transitive default is a design attribute whose default_value is a
    dotted path pointing to a module output (e.g., "cost_model.total_cost"),
    as opposed to a numeric literal ("3.14"), None, or a bare name ("width").

    Used by Phase 4 registration to filter candidates for transitive alias
    registration. Empirically validated by Spike 7: 128 attrs tested,
    correct for all. Only 2 transitive defaults exist across all models.

    Args:
        default_value: The design attribute's default_value (any type).

    Returns:
        True if the value looks like a dotted-path reference.
    """
    if default_value is None:
        return False
    val = str(default_value)
    if "." not in val:
        return False
    try:
        float(val)
        return False  # numeric like "3.14"
    except (ValueError, TypeError):
        return True   # dotted path like "cost_model.total_cost"
```

**Design notes:**
- This is a module-level function (not a method on `OutputRegistry`) because it's a pure predicate that doesn't require registry state. It's also used as a filter in the pipeline construction step (Item 3), not by the registry itself.
- **Spec deviation:** The spec (FR-4) names this `_is_transitive_default()` with a leading underscore. This design uses `is_transitive_default()` (no underscore) because it will be imported by `initialization.py` in Item 3 -- a leading underscore would signal "private, don't import" which contradicts the usage pattern.

### Component 4: `core/__init__.py` Updates

Add exports for `ChannelAlias` and `OutputRegistry`:

```python
from sysml_codegen.core.models import (
    BindingResolution,
    BindingResolutionType,
    ChannelAlias,  # NEW
)
from sysml_codegen.core.output_registry import (
    OutputRegistry,          # NEW
    is_transitive_default,   # NEW
)
```

And add to `__all__`:
```python
"ChannelAlias",
"OutputRegistry",
"is_transitive_default",
```

### Component 5: Unit Tests

**File:** `tests/unit/test_output_registry.py` (new)

**Structure:** Factory functions at module level, pytest classes grouping related tests.

#### Test Factories

```python
def _make_registry_with_calc_usage() -> OutputRegistry:
    """Build a registry with one concrete CalcUsage (2 outputs).

    Represents: solar_battery lcoe CalcUsage with lcoe_per_mwh and npv outputs.
    Registers Key_A, Key_B, Key_C for each output.
    """
    ...

def _make_registry_with_virtual_calc_usage() -> OutputRegistry:
    """Build a registry with one virtual CalcUsage (1 output).

    Represents: solar_battery cost_model template instance with total_cost output.
    Key_C is the ONLY key that Phase 2 CHAIN aliases can resolve against.
    """
    ...

def _make_registry_with_aggregation() -> OutputRegistry:
    """Build a registry with one aggregation output.

    Represents: solar_array.capital_cost aggregation module.
    Registers Key_D and Key_E.
    """
    ...

def _make_registry_with_formula() -> OutputRegistry:
    """Build a registry with one FORMULA computed attribute.

    Represents: e2e_plant.power_mw synthetic module.
    Registers Key_F.
    """
    ...
```

These factories call `OutputRegistry.register()` directly with hardcoded key values derived from Spike 8 data. They do NOT construct `CalcUsageData` objects -- the OutputRegistry is tested in isolation from the data models it will consume in Item 3.

#### Test Classes

**`class TestRegister`** -- FR-2 basic registration:
- `test_register_single_key` -- register with one lookup key, resolve returns canonical
- `test_register_multiple_keys` -- register with Key_A + Key_B + Key_C, all resolve to same canonical
- `test_canonical_channel_self_resolves` -- `resolve(canonical_channel)` returns itself
- `test_register_duplicate_key_same_channel_is_noop` -- no warning, idempotent
- `test_len_reflects_registered_keys` -- `len(registry)` counts all keys

**`class TestCollisionHandling`** -- FR-2 collision policy:
- `test_collision_refuses_overwrite` -- register same key with different channel, first wins
- `test_collision_logs_warning` -- `caplog` captures exactly one warning per collision
- `test_nine_virtual_calc_usage_collision` -- Key_A `cost_model.total_cost` from 9 virtual CalcUsages: first wins, 8 warnings logged

**`class TestRegisterAlias`** -- FR-2 alias registration:
- `test_alias_resolves_to_canonical` -- after `register_alias()`, `resolve(alias)` returns canonical
- `test_alias_to_unregistered_channel_warns` -- warns and skips (phase ordering violation)
- `test_alias_collision_refuses_overwrite` -- same collision policy as `register()`

**`class TestResolve`** -- FR-2 + FR-5 resolution:
- `test_resolve_exact_match` -- registered key returns canonical
- `test_resolve_unregistered_returns_none` -- unknown key returns `None`
- `test_resolve_bare_name_returns_none` -- `resolve("total_cost")` returns `None` (negative)
- `test_resolve_sysml_qn_returns_none` -- `resolve("Namespace::Part::calc")` returns `None` (negative)
- `test_resolve_no_normalization` -- register `"a.b"`, resolve `"a__b"` returns `None`

**`class TestKeyFormats`** -- FR-3 key format contract (Spike 8 data):
- `test_key_a_dotted_short_resolves` -- `"lcoe.lcoe_per_mwh"` resolves
- `test_key_b_eqn_resolves` -- `"SolarBatteryDesign__solar_battery_plant__lcoe__lcoe_per_mwh"` resolves
- `test_key_c_dotted_hierarchy_resolves` -- `"solar_battery_plant.lcoe.lcoe_per_mwh"` resolves
- `test_key_c_virtual_calc_usage` -- `"solar_battery_plant.solar_array.pv_module.cost_model.total_cost"` resolves
- `test_key_d_aggregation_resolves` -- `"solar_array.capital_cost"` resolves
- `test_key_f_formula_resolves` -- `"e2e_plant.power_mw"` resolves

**`class TestDeriveKeyC`** -- FR-6 Key_C utility:
- `test_concrete_calc_usage` -- `"Design__plant__lcoe"` + `"lcoe_per_mwh"` -> `"plant.lcoe.lcoe_per_mwh"`
- `test_virtual_calc_usage_deep` -- `"SolarBatteryDesign__solar_battery_plant__solar_array__pv_module__cost_model"` + `"total_cost"` -> `"solar_battery_plant.solar_array.pv_module.cost_model.total_cost"`
- `test_single_segment_after_prefix` -- `"Design__lcoe"` + `"out"` -> `"lcoe.out"`

**`class TestPhaseOrdering`** -- FR-3 4-phase protocol:
- `test_phase2_alias_resolves_via_phase1_key_c` -- register Phase 1 (Key_C), then Phase 2 CHAIN alias resolves against it
- `test_phase3_alias_resolves_via_phase1_and_phase2` -- Phase 3 EXPOSE_PURE alias resolves against Phase 1+2 entries
- `test_phase4_alias_resolves_via_phase1_through_3` -- Phase 4 transitive alias resolves against Phase 1-3
- `test_phase2_before_phase1_warns` -- `register_alias()` warns if canonical isn't registered yet

**`class TestIsTransitiveDefault`** -- FR-4:
- `test_dotted_path_is_transitive` -- `"cost_model.total_cost"` returns `True`
- `test_numeric_with_dot_not_transitive` -- `"3.14"` returns `False`
- `test_none_not_transitive` -- `None` returns `False`
- `test_bare_name_not_transitive` -- `"width"` returns `False`
- `test_integer_not_transitive` -- `"42"` returns `False`
- `test_empty_string_not_transitive` -- `""` returns `False`
- `test_complex_dotted_path_is_transitive` -- `"solar_array.cost_model.total_cost"` returns `True`
- `test_scientific_notation_not_transitive` -- `"1.5e3"` returns `False`

### Component 6: Smoke Test (Real Model Data)

**File:** `tests/integration/test_output_registry_smoke.py` (new)

**Purpose:** Build an `OutputRegistry` from real `solar_battery` extracted data (loaded via SysIDE) and verify `resolve()` returns non-`None` for a known CHAIN binding source_path. This catches failures where synthetic fixtures pass but real data diverges -- exactly the class of bugs that produced Bug 2.

**Approach:** This test manually constructs an `OutputRegistry` from the real extracted data (CalcUsages, aggregation data) using the same key derivation logic that Item 3 will formalize in `build_output_registry()`. It's an early integration proof that the registry's key format contract holds on real data.

```python
"""Smoke test: OutputRegistry with real solar_battery model data.

Validates that the OutputRegistry key format contract holds for real
extracted data, not just synthetic fixtures. This catches key format
mismatches that would only surface with real SysIDE AST data.

See: spec "Smoke Test (real model data)" requirement.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from sysml_codegen.core.output_registry import OutputRegistry
from sysml_codegen.core.qualified_names import get_channel_name
from sysml_codegen.generation.initialization import build_pipeline_context

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


class TestOutputRegistrySmokeRealData:
    """Build an OutputRegistry from real solar_battery data and verify resolution."""

    @pytest.fixture(scope="class")
    def pipeline_context(self):
        model_path = FIXTURES_DIR / "solar_battery_model"
        return build_pipeline_context([model_path])

    @pytest.fixture(scope="class")
    def registry(self, pipeline_context) -> OutputRegistry:
        """Build a Phase 1 registry from real extracted CalcUsage data."""
        reg = OutputRegistry()
        ctx = pipeline_context

        # Phase 1: Register CalcUsage outputs (Key_A, Key_B, Key_C)
        calc_def_map = {cd.name: cd for cd in ctx.calc_defs}
        for usage in ctx.calc_usages:
            calc_def = calc_def_map.get(usage.calc_def_name)
            if not calc_def:
                continue
            for attr in calc_def.output_attributes:
                canonical = get_channel_name(usage.qualified_name, attr.name)
                key_a = f"{usage.instance_name}.{attr.name}"
                key_b = canonical  # EQN format = canonical
                key_c = OutputRegistry.derive_key_c(
                    usage.qualified_name, attr.name,
                )
                reg.register(canonical, [key_a, key_b, key_c])

        return reg

    def test_registry_has_entries(self, registry: OutputRegistry):
        """Sanity: registry should have registered keys from real data."""
        assert len(registry) > 0, "Registry should have entries from solar_battery"

    def test_known_chain_source_path_resolves(self, registry: OutputRegistry):
        """A known CHAIN binding source_path resolves to non-None.

        solar_battery has CHAIN bindings in dotted format that should
        resolve via Key_C (dotted hierarchy path).
        """
        # lcoe.lcoe_per_mwh is a known concrete CalcUsage output (Key_A)
        result = registry.resolve("lcoe.lcoe_per_mwh")
        assert result is not None, (
            "Expected 'lcoe.lcoe_per_mwh' (Key_A) to resolve in "
            "solar_battery registry"
        )

    def test_key_c_resolves_for_virtual_calc_usage(self, registry: OutputRegistry):
        """A virtual CalcUsage output resolves via Key_C (dotted hierarchy).

        cost_model template instances produce outputs accessible only via
        Key_C in the real solar_battery model.
        """
        # This is a known virtual CalcUsage Key_C path from Spike 8
        key_c = "solar_battery_plant.solar_array.pv_module.cost_model.total_cost"
        result = registry.resolve(key_c)
        assert result is not None, (
            f"Expected Key_C '{key_c}' to resolve for virtual CalcUsage "
            "in solar_battery registry"
        )
```

**Note:** This test only exercises Phase 1 registration (CalcUsage outputs). Phase 2-4 alias construction requires Item 2a (ChannelAlias producers), which is out of scope. The test validates the core contract: real CalcUsage data produces registry keys that match real binding source_paths.

### Component 7: Bug 2 xfail Regression Test

**File:** `tests/integration/test_bug2_regression.py` (new)

**Purpose:** A failing test that captures the exact Bug 2 failure in the real pipeline. Written BEFORE the fix (Item 3) so it serves as definitive proof when the xfail is removed.

**Structure:**

```python
"""Bug 2 regression test: EXPOSE_PURE two-hop resolution failure.

Bug 2: In e2e_attr_expr (attr_expr_probe fixture), the EXPOSE_PURE attribute
`total_capex` on `e2e_plant` should wire to MODULE_OUTPUT (component_cost's
total_cost output), but instead falls through to ENTRY_POINT due to the
second-hop resolution failure with virtual CalcUsages.

This test is written BEFORE the fix (Item 1, epic OUTPUT-REGISTRY) and marked
xfail. When Item 3 (OutputRegistry backtracker integration) is complete,
the xfail is removed and this test goes green -- definitive proof the fix works.

See: .project/research/20260213-152845_bug2-expose-calcusage-wiring-persistent-failure.md
"""
from __future__ import annotations

from pathlib import Path

import pytest

from sysml_codegen.core.models import BindingResolutionType
from sysml_codegen.generation.initialization import build_pipeline_context

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


class TestBug2ExposesPureTwoHopFailure:
    """Regression test for Bug 2: EXPOSE_PURE total_capex wiring."""

    @pytest.fixture(scope="class")
    def pipeline_context(self):
        model_path = FIXTURES_DIR / "attr_expr_probe"
        return build_pipeline_context([model_path])

    @pytest.mark.xfail(
        reason="Bug 2: EXPOSE_PURE two-hop failure -- total_capex resolves "
               "to ENTRY_POINT instead of MODULE_OUTPUT. Fix expected in "
               "epic OUTPUT-REGISTRY Item 3.",
        strict=True,
    )
    def test_total_capex_resolves_to_module_output(self, pipeline_context):
        """EXPOSE_PURE financial.total_capex should be MODULE_OUTPUT.

        In the current implementation, the second hop of transitive
        resolution fails for virtual CalcUsages because the output catalog
        key format doesn't match the dotted source_path format.
        """
        resolutions = pipeline_context.backtracking_result.binding_resolutions

        # Find the total_capex binding resolution
        capex_keys = [
            k for k in resolutions
            if "total_capex" in k or "capex" in k
        ]
        assert capex_keys, (
            "Expected at least one binding resolution containing 'total_capex' "
            f"or 'capex'. Available keys: {list(resolutions.keys())[:20]}"
        )

        # At least one total_capex resolution should be MODULE_OUTPUT
        capex_resolutions = [resolutions[k] for k in capex_keys]
        has_module_output = any(
            r.resolution_type == BindingResolutionType.MODULE_OUTPUT
            for r in capex_resolutions
        )
        assert has_module_output, (
            f"Bug 2: total_capex should resolve to MODULE_OUTPUT but got: "
            f"{[(k, r.resolution_type) for k, r in zip(capex_keys, capex_resolutions)]}"
        )
```

**xfail semantics:** `strict=True` means the test is expected to FAIL. If it unexpectedly passes (before the fix is in), pytest will report an error. When Item 3 is complete and Bug 2 is fixed, remove the `@pytest.mark.xfail` decorator -- the test becomes a normal passing test.

**Note on test discovery:** The test searches for binding resolution keys containing `total_capex` or `capex` rather than hardcoding an exact key, because the key format depends on the CalcUsage qualified name which varies depending on template expansion behavior. This makes the test robust against minor key format differences while still asserting the core contract (MODULE_OUTPUT, not ENTRY_POINT).

---

## Potential Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Bug 2 xfail test doesn't find `total_capex` in binding keys | Test would fail with a confusing assertion error | The test includes a diagnostic message listing available keys. If attr_expr_probe doesn't produce a `total_capex` binding, investigate the model fixture before committing. |
| `is_transitive_default()` false positive on version strings like `"1.2.3"` | Would attempt registry resolution on non-path strings | `float("1.2.3")` raises `ValueError`, so multi-dot strings pass the filter. But `resolve()` returns `None` for unregistered keys, so the false positive is harmless (no incorrect alias registered). |
| Smoke test Key_C path hardcoded from Spike 8 | If solar_battery model changes, test breaks | The path `solar_battery_plant.solar_array.pv_module.cost_model.total_cost` is from a committed fixture. If the fixture changes, update the test constant. |

## Integration Strategy

This item is **purely additive** -- no existing files are modified except `core/models.py` (adding a class) and `core/__init__.py` (adding exports). The OutputRegistry is not wired into the pipeline until Item 3.

**Downstream consumers (Items 2-4):**
- Item 2a: `ChannelAlias` model imported for EXPOSE_PURE and CHAIN alias construction
- Item 3: `OutputRegistry` instantiated in `build_pipeline_context()`, passed to `DependencyBacktracker`
- Item 4: Old backtracker indexes removed, graph builder simplified

**No circular dependencies:** `core/output_registry.py` imports only `logging` (stdlib). `core/models.py` imports only `pydantic` and `enum`. Both are leaf modules in the dependency graph.

## Validation Approach

### Gate 1 Checklist (from epic)

```bash
# Must all pass before proceeding to Item 2a
uv run pytest tests/unit/test_output_registry.py -v            # New unit tests
uv run pytest tests/integration/test_output_registry_smoke.py -v  # Smoke test (real data)
uv run pytest tests/integration/test_bug2_regression.py -v     # xfail expected
uv run pytest tests/                                           # Full regression
uv run mypy src/sysml_codegen/core/output_registry.py          # Type check new file
uv run mypy src/sysml_codegen/core/models.py                   # Type check modified file
uv run ruff check src/sysml_codegen/core/                      # Lint new + modified
```

### Expected Test Outcomes

- `tests/unit/test_output_registry.py`: All tests pass (pure unit tests, no model loading)
- `tests/integration/test_output_registry_smoke.py`: All tests pass (validates real model data resolves)
- `tests/integration/test_bug2_regression.py`: 1 xfail (expected failure, Bug 2 not yet fixed)
- `tests/`: Full suite passes (purely additive changes, no regressions possible)

---

**Next Step:** After approval -> `/_my_plan` or `/_my_implement`
