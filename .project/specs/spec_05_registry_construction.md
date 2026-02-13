# Spec 05: Step 5 -- OutputRegistry Construction (4-Phase Protocol)

**Spec ID**: SPEC-05
**Status**: Draft
**Created**: 2026-02-13
**Implements**: Epic OUTPUT-REGISTRY, Item 3 (partial) + Item 1 (construction wiring)
**Design Reference**: `08_algorithm_revised.md` Sections 6 and 12
**Spike Evidence**: Spikes 3, 4, 5, 6, 7, 8

---

## 1. Overview

Step 5 is a **NEW** step inserted into `build_pipeline_context()` in
`generation/initialization.py`, between Step 4.7 (aggregation scoping) and
Step 6 (dependency backtracking). It constructs a single `OutputRegistry`
instance from the outputs of Steps 1-4.5, following a strict 4-phase
registration protocol where each phase may only reference names registered in
prior phases.

The OutputRegistry replaces the five ad-hoc indexes currently built inside the
`DependencyBacktracker` constructor:

| Removed Index | Replaced By |
|---|---|
| `_computed_attr_index` | Phase 1 FORMULA registration + Phase 3 EXPOSE_PURE aliases |
| `_aggregation_output_index` | Phase 1 Aggregation registration + alias variants |
| `_output_catalog` | Phase 1 CalcUsage registration |
| `_design_attr_binding_index` | Phase 4 transitive design-attribute aliases |
| `_usage_by_name` | Phase 1 Key_A (dotted short) -- though `_usage_by_name` may be kept for non-resolution purposes |

---

## 2. Function Signature

```python
def _build_output_registry(
    calc_usages: list[CalcUsageData],
    calc_defs: list[CalculationDefinitionData],
    scoped_aggregation_data: list[ScopedAggregationData],
    computed_attrs: list[ComputedAttributeData],
    chain_aliases: list[ChannelAlias],
    expose_pure_aliases: list[ChannelAlias],
    design_attrs: dict[Path, list[DesignAttributeData]],
) -> OutputRegistry:
    """Build the OutputRegistry using the 4-phase registration protocol.

    This is Step 5 in the pipeline. It creates a single lookup structure
    that resolves any dotted binding source_path to a canonical channel name
    (PQN format).

    Phase ordering is a strict contract: each phase may ONLY reference names
    registered in prior phases. If a phase N alias cannot resolve, a warning
    is logged -- it is never silently dropped.

    Args:
        calc_usages: All CalcUsageData from Steps 3/3.5 (includes virtual
            CalcUsages from template expansion, excludes templates).
        calc_defs: All CalculationDefinitionData from Step 2.
        scoped_aggregation_data: ScopedAggregationData from Step 4.7
            (aggregation expressions scoped to design instance paths).
        computed_attrs: ComputedAttributeData list from Step 4.5
            (all classifications -- this function filters to FORMULA only).
        chain_aliases: ChannelAlias objects with source="redefinition"
            from Step 3.5(D). Already scoped and filtered (no BARE CAS codes).
        expose_pure_aliases: ChannelAlias objects with source="expose_pure"
            from Step 4.5. Already filtered (PartUsage only, no PartDef).
        design_attrs: Design attributes by file from Step 4, with FORMULAs
            already removed by Step 4.5.

    Returns:
        Populated OutputRegistry ready for use by the DependencyBacktracker.
    """
```

**Location**: `src/sysml_codegen/generation/initialization.py`

**Imports required**:
```python
from sysml_codegen.core.output_registry import OutputRegistry
from sysml_codegen.core.models import ChannelAlias
from sysml_codegen.core.qualified_names import get_channel_name, sysml_to_python_qualified_name
from sysml_codegen.extraction.data_models import (
    ComputedAttributeClassification,
    ComputedAttributeData,
    ScopedAggregationData,
)
from sysml_codegen.extraction.expression_compiler import Compilability
```

---

## 3. Phase 1: Register Canonical Channels

Phase 1 registers every output channel that produces a value in the pipeline.
Three families of outputs are registered. No aliases are created in this phase --
only canonical channels with their lookup keys.

### 3.1 CalcUsage Outputs

For each non-template CalcUsage, register one channel per output attribute on its
CalcDef. Three lookup keys per channel:

```python
# Build CalcDef lookup for output attribute enumeration
calc_def_lookup: dict[str, CalculationDefinitionData] = {cd.name: cd for cd in calc_defs}

for usage in calc_usages:
    if usage.is_template:
        continue

    calc_def = calc_def_lookup.get(usage.calc_def_name)
    if calc_def is None:
        logger.debug(
            "CalcUsage '%s' references unknown CalcDef '%s', skipping registration",
            usage.qualified_name, usage.calc_def_name,
        )
        continue

    for output_attr in calc_def.output_attributes:
        # Canonical channel name (PQN format: EQN + "__" + output_name)
        channel = get_channel_name(usage.qualified_name, output_attr.name)

        # Key_A: dotted short form ("instance_name.output_name")
        # For concrete CalcUsages: "net_electric.p_net"
        # For virtual CalcUsages: contains full EQN prefix (hybrid format)
        # NOTE: Key_A may collide for virtual CalcUsages with same instance_name
        # across different parent scopes. Collision policy: first registration wins.
        key_a = f"{usage.instance_name}.{output_attr.name}"

        # Key_B: full EQN form ("DesignPart__usage_path__output_name")
        # Globally unique. Used for EQN-based lookups.
        key_b = f"{usage.qualified_name}__{output_attr.name}"

        # Key_C: dotted hierarchy path (REQUIRED for Phase 2 CHAIN alias resolution)
        # Strips the design PartDef prefix (segments[0]), joins remaining with "."
        # Example:
        #   QN = "SolarBatteryDesign__solar_battery_plant__solar_array__pv_module__cost_model"
        #   Key_C = "solar_battery_plant.solar_array.pv_module.cost_model.total_cost"
        #
        # Spike 8: All 41 Phase 2 CHAIN aliases in solar_battery resolve
        # exclusively via Key_C. This key is the critical link between
        # hierarchy-scoped CHAIN redefinition canonical_names and virtual
        # CalcUsage outputs.
        #
        # For concrete (non-virtual) CalcUsages, Key_C may duplicate Key_A.
        # This is harmless -- same channel, collision policy keeps first.
        segments = usage.qualified_name.split("__")
        key_c = ".".join(segments[1:]) + "." + output_attr.name

        registry.register(channel, [key_a, key_b, key_c])
```

**Key format examples** (from Spike 8):

| CalcUsage QN | Output | Key_A | Key_B | Key_C |
|---|---|---|---|---|
| `SolarBatteryDesign__solar_battery_plant__lcoe` | `lcoe_per_mwh` | `lcoe.lcoe_per_mwh` | `SolarBatteryDesign__solar_battery_plant__lcoe__lcoe_per_mwh` | `solar_battery_plant.lcoe.lcoe_per_mwh` |
| `SolarBatteryDesign__solar_battery_plant__solar_array__pv_module__cost_model` | `total_cost` | `cost_model.total_cost` | `SolarBatteryDesign__...cost_model__total_cost` | `solar_battery_plant.solar_array.pv_module.cost_model.total_cost` |

**Invariant**: No bare-name registration. Spike 4 confirmed zero bare-name references across 94 bindings in 3 models. Bare names are ambiguous and collision-prone.

### 3.2 Aggregation Outputs

For each `ScopedAggregationData`, register one channel for the aggregation's
output attribute. Two lookup keys per channel, plus alias variants.

```python
for agg in scoped_aggregation_data:
    # Canonical channel name from the scoped module EQN
    # agg.module_eqn = f"{instance_path}__{expression.attribute_name}"
    channel = get_channel_name(agg.module_eqn, agg.expression.attribute_name)

    # instance_path format: "DesignPartDef__part_usage1__part_usage2" (__ separator)
    instance_parts = agg.instance_path.split("__")
    part_usage_name = instance_parts[-1]  # last segment: "solar_array"

    # Key_D: "part_usage_name.attribute_name"
    # Example: "solar_array.capital_cost"
    key_d = f"{part_usage_name}.{agg.expression.attribute_name}"

    # Key_E: full dotted instance path INCLUDING design prefix
    # Example: "SolarBatteryDesign.solar_battery_plant.solar_array.capital_cost"
    # NOTE: Includes the design PartDef prefix -- unlike Key_C which strips it.
    # This is intentional: instance_path includes the prefix, and we register
    # the full dotted form for completeness.
    key_e = ".".join(instance_parts) + "." + agg.expression.attribute_name

    registry.register(channel, [key_d, key_e])

    # Register alias variants from AggregationExpressionData.aliases
    # These come from :>> CHAIN redefinitions that alias the aggregation output.
    # Example: "total_capex" aliases "capital_cost" on the same PartDef.
    for alias_name in agg.expression.aliases:
        # Dotted short form alias
        registry.register_alias(
            f"{part_usage_name}.{alias_name}", channel
        )
        # Full dotted form alias
        registry.register_alias(
            ".".join(instance_parts) + "." + alias_name, channel
        )
```

**Key format examples** (from Spike 8):

| ScopedAggregation | Key_D | Key_E | Alias Variants |
|---|---|---|---|
| `solar_array__capital_cost` | `solar_array.capital_cost` | `SolarBatteryDesign.solar_battery_plant.solar_array.capital_cost` | `solar_array.total_capex`, `SolarBatteryDesign...total_capex` |

### 3.3 FORMULA Computed Attribute Outputs

For each FORMULA-classified computed attribute that is also FULLY_COMPILABLE,
register one channel. One lookup key per channel.

```python
for ca in computed_attrs:
    if ca.classification != ComputedAttributeClassification.FORMULA:
        continue
    if ca.compilability != Compilability.FULLY_COMPILABLE:
        continue

    # Build module EQN (same logic as DependencyBacktracker._build_computed_attr_channel)
    parent_eqn = sysml_to_python_qualified_name(ca.owning_part_qualified_name)
    module_eqn = f"{parent_eqn}__{ca.python_name}"

    # Canonical channel name
    channel = get_channel_name(module_eqn, ca.python_name)

    # Key_F: "owning_part_name.python_name"
    # Example: "e2e_plant.power_mw"
    # This is the key that REFERENCE bindings resolve against via the
    # backtracker's secondary resolution path (segments[-2] + leaf_name).
    key_f = f"{ca.owning_part_name}.{ca.python_name}"

    registry.register(channel, [key_f])
```

**Key format examples** (from Spike 8):

| Computed Attr | Channel | Key_F |
|---|---|---|
| `power_mw` on `e2e_plant` | `E2EDesign__e2e_plant__power_mw__power_mw` | `e2e_plant.power_mw` |

### 3.4 Phase 1 Logging

```python
phase_1_count = len(registry._canonical)
logger.info(
    "Step 5 Phase 1: Registered %d canonical channels "
    "(%d CalcUsage, %d aggregation, %d FORMULA)",
    phase_1_count,
    calc_usage_channel_count,
    agg_channel_count,
    formula_channel_count,
)
```

---

## 4. Phase 2: Register :>> CHAIN Aliases

CHAIN aliases come from Step 3.5(D). Each alias maps a scoped dotted key
(e.g., `"solar_battery_plant.solar_array.total_capex"`) to a canonical channel
registered in Phase 1.

### 4.1 Resolution Path

CHAIN alias `canonical_name` values resolve against **Key_C** (dotted hierarchy
path) from Phase 1 CalcUsage registration. This was empirically validated by
Spike 8: all 41 CHAIN aliases in solar_battery resolve exclusively via Key_C.

```python
phase_2_registered = 0
phase_2_failed = 0

for alias in chain_aliases:
    # chain_aliases are pre-filtered: source == "redefinition", BARE values excluded
    canonical_channel = registry.resolve(alias.canonical_name)
    if canonical_channel is not None:
        registry.register_alias(alias.alias_name, canonical_channel)
        phase_2_registered += 1
    else:
        logger.warning(
            "CHAIN alias '%s' -> '%s' could not resolve (Phase 2)",
            alias.alias_name, alias.canonical_name,
        )
        phase_2_failed += 1

logger.info(
    "Step 5 Phase 2: Registered %d CHAIN aliases, %d failed",
    phase_2_registered, phase_2_failed,
)
```

### 4.2 Preconditions

- `chain_aliases` have already been filtered by Step 3.5(D):
  - Only DOTTED source_paths (`"." in redef.source_path`)
  - BARE CAS codes (like `CAS220101`) excluded
  - Both `alias_name` and `canonical_name` are scoped with instance-path prefix
- Phase 1 CalcUsage registration MUST include Key_C for this phase to succeed

### 4.3 Spike Evidence

| Model | CHAIN Aliases | Phase 2 Resolved | Resolution Key |
|---|---|---|---|
| solar_battery | 41 | 41 (100%) | All via Key_C |
| e2e_attr_expr | 0 | n/a | n/a |

---

## 5. Phase 3: Register EXPOSE_PURE Aliases (PartUsage Only)

EXPOSE_PURE aliases come from Step 4.5. Each alias maps a scoped dotted key
(e.g., `"e2e_plant.total_capex"`) to a canonical channel registered in Phase 1
or Phase 2.

### 5.1 Resolution Path

EXPOSE_PURE alias `canonical_name` values are constructed from the `references`
field (NOT `expression_text` -- Spike 3). They resolve against Key_A (CalcUsage
dotted short) from Phase 1, or against Phase 2 CHAIN aliases.

```python
phase_3_registered = 0
phase_3_failed = 0

for alias in expose_pure_aliases:
    # expose_pure_aliases are pre-filtered:
    #   source == "expose_pure", PartDef EXPOSE_PURE excluded (Spike 8: Issue 21)
    canonical_channel = registry.resolve(alias.canonical_name)
    if canonical_channel is not None:
        # Derive short parent name from owning_part_qn for scoping
        # Example: "E2EDesign__e2e_plant" -> "e2e_plant"
        owning_part_short = alias.owning_part_qn.split("__")[-1]
        scoped_alias = f"{owning_part_short}.{alias.alias_name}"
        registry.register_alias(scoped_alias, canonical_channel)
        phase_3_registered += 1
    else:
        logger.warning(
            "EXPOSE_PURE alias '%s' -> '%s' could not resolve (Phase 3)",
            alias.alias_name, alias.canonical_name,
        )
        phase_3_failed += 1

logger.info(
    "Step 5 Phase 3: Registered %d EXPOSE_PURE aliases, %d failed",
    phase_3_registered, phase_3_failed,
)
```

### 5.2 Preconditions

- `expose_pure_aliases` have already been filtered by Step 4.5:
  - Only PartUsage-level EXPOSE_PURE (not PartDef -- Spike 8: Issue 21)
  - `canonical_name` built from `references` field: `f"{references[1].name}.{references[0].name}"`
  - NOT from `expression_text` (SysIDE produces `".(component_cost)"`, not a parseable dotted key)

### 5.3 Why PartDef EXPOSE_PURE Is Filtered

Spike 8 demonstrated that PartDef-level EXPOSE_PURE produces unscoped canonical
names (e.g., `"cost_model.total_cost"` without instance path prefix) that cannot
resolve against instance-scoped registry keys. CHAIN aliases from Step 3.5
already handle the PartDef aliasing role (41/41 resolved in solar_battery).

### 5.4 Spike Evidence

| Model | EXPOSE_PURE Aliases (PartUsage) | Phase 3 Resolved |
|---|---|---|
| e2e_attr_expr | 1 | 1 (100%) |
| solar_battery | 0 (1 total, but PartDef-level, filtered in Step 4.5) | n/a |

---

## 6. Phase 4: Register Design-Attribute Transitive Aliases (PartUsage Only)

Design attributes whose `default_value` is a dotted path pointing to a module
output create transitive aliases. This collapses the two-hop resolution problem
where a binding references a design attribute that forwards to a calc output.

### 6.1 Transitive Default Detection

```python
def _is_transitive_default(attr: DesignAttributeData) -> bool:
    """Check if a design attribute's default_value is a dotted path reference.

    A transitive default is a design attribute whose default_value is a dotted
    path like "cost_model.total_cost" (pointing to a module output), as opposed
    to a literal value like "0.92" or "3.14".

    Identification criteria:
    1. default_value is not None
    2. default_value contains "."
    3. default_value is NOT a valid float (excludes "3.14", "2600.0")

    Spike 7: 2 transitive defaults found across 128 design attributes in
    solar_battery, both DOTTED_PATH format, both resolved. Filter correctly
    excluded all 126 non-transitive attributes.

    Args:
        attr: Design attribute to check.

    Returns:
        True if the default_value is a dotted path reference.
    """
    if attr.default_value is None:
        return False
    val = str(attr.default_value)
    if "." not in val:
        return False
    try:
        float(val)
        return False  # numeric like "3.14" or "2600.0"
    except (ValueError, TypeError):
        return True  # dotted path like "cost_model.total_cost"
```

### 6.2 Registration

```python
phase_4_registered = 0
phase_4_failed = 0

for path_attrs in design_attrs.values():
    for attr in path_attrs:
        if not _is_transitive_default(attr):
            continue

        # FILTER: PartDef-level attributes with dotted defaults are PartDef-local
        # and can't resolve against instance-scoped registry keys.
        # Spike 8: 1/2 transitive defaults resolved (PartUsage), 1/2 failed (PartDef).
        #
        # Identification: Check whether attr.parent_part corresponds to a PartDef
        # or PartUsage. Approach: if the attr's qualified_name starts with a known
        # PartDef name (from calc_def parents), it's PartDef-level.
        # Alternative: add is_on_part_definition to DesignAttributeData during extraction.
        #
        # For now, attempt resolution and log failures -- PartDef attrs will
        # simply fail to resolve (harmless: they'd create an alias to nothing).
        canonical_channel = registry.resolve(str(attr.default_value))
        if canonical_channel is not None:
            alias_key = f"{attr.parent_part}.{attr.name}"
            registry.register_alias(alias_key, canonical_channel)
            phase_4_registered += 1
        else:
            logger.debug(
                "Transitive design attr '%s.%s' -> '%s' could not resolve (Phase 4)",
                attr.parent_part, attr.name, attr.default_value,
            )
            phase_4_failed += 1

logger.info(
    "Step 5 Phase 4: Registered %d transitive design attr aliases, %d failed",
    phase_4_registered, phase_4_failed,
)
```

### 6.3 Spike Evidence

| Model | Transitive Defaults | Resolved | Failed | Failure Reason |
|---|---|---|---|---|
| solar_battery | 2 | 1 | 1 | PartDef-level attr (unscoped key) |
| e2e_attr_expr | 0 | n/a | n/a | n/a |

---

## 7. Integration into `build_pipeline_context()`

### 7.1 Call Site

The new step is inserted between the current Step 4.7 (aggregation scoping) and
Step 5 (parameter group deriver). The current step numbering shifts:

| Current Step | New Step | Description |
|---|---|---|
| Step 4.7 | Step 4.7 | Scope aggregation expressions (unchanged) |
| -- | **Step 5** | **Build OutputRegistry (NEW)** |
| Step 5 | Step 5.5 | Parameter group deriver (renumbered) |
| Step 6 | Step 6 | Backtracker (now receives OutputRegistry) |

```python
# In build_pipeline_context(), after Step 4.7:

# Step 5: Build OutputRegistry (SINGLE LOOKUP for binding resolution)
output_registry = _build_output_registry(
    calc_usages=calc_usages,
    calc_defs=calc_defs,
    scoped_aggregation_data=scoped_agg_data,
    computed_attrs=computed_attrs,
    chain_aliases=chain_aliases,         # from Step 3.5(D)
    expose_pure_aliases=expose_aliases,   # from Step 4.5
    design_attrs=design_attrs,
)

# Step 5.5: Create parameter group deriver (uses filtered design_attrs)
group_deriver = ParameterGroupDeriver(design_attrs, calc_usages, calc_defs)

# Step 6: Create backtracker and run (now with OutputRegistry)
backtracker = DependencyBacktracker(
    calc_usages,
    calc_defs,
    design_attributes=design_attrs,
    output_registry=output_registry,   # NEW parameter
    # computed_attributes=computed_attrs,   # REMOVED (now in registry)
    # aggregation_data=scoped_agg_data,     # REMOVED (now in registry)
)
```

### 7.2 PipelineContext Update

Add `output_registry` to the `PipelineContext` dataclass:

```python
@dataclass
class PipelineContext:
    # ... existing fields ...
    output_registry: OutputRegistry | None = None
```

This allows downstream consumers (graph builder, tests) to inspect the registry
if needed.

---

## 8. OutputRegistry Class Specification

The `OutputRegistry` class lives in `src/sysml_codegen/core/output_registry.py`.

```python
"""Single lookup for resolving binding source_paths to canonical channel names.

The OutputRegistry replaces the five ad-hoc indexes previously built inside the
DependencyBacktracker constructor. It maps dotted binding source_paths to
canonical channel names (PQN format) using exact-match resolution.

Design reference: 08_algorithm_revised.md Section 12.
"""

import logging

logger = logging.getLogger(__name__)


class OutputRegistry:
    """Single lookup for resolving any binding source_path to a channel name.

    Every pipeline output (CalcUsage output, FORMULA computed attribute output,
    aggregation module output) is registered with a canonical channel name and
    a set of lookup keys (aliases).

    Resolution is exact-match only. No normalization, no bare-name fallback,
    no SYSML_QN -> EQN conversion. These design decisions are empirically
    grounded:
    - Spike 1: CHAIN bindings always use DOTTED format
    - Spike 4: Zero bare-name references across 94 bindings
    - Spike 5: SYSML_QN normalization (:: -> __) is broken -- the consuming
      path differs from the producing path in all 4 MODULE_OUTPUT cases

    Usage:
        registry = OutputRegistry()
        registry.register("ns__calc__output", ["calc.output", "ns__calc__output"])
        registry.register_alias("alias.output", "ns__calc__output")
        assert registry.resolve("calc.output") == "ns__calc__output"
        assert registry.resolve("alias.output") == "ns__calc__output"
        assert registry.resolve("unknown") is None
    """

    def __init__(self) -> None:
        self._index: dict[str, str] = {}     # lookup_key -> canonical channel
        self._canonical: set[str] = set()     # set of all canonical channel names

    def register(self, canonical_channel: str, lookup_keys: list[str]) -> None:
        """Register a channel with all its lookup keys.

        The canonical channel name is also registered as a lookup key
        (self-referential). Lookup keys are dotted and EQN formats only --
        bare names are NOT registered (Spike 4: zero bare-name references).

        Collision policy: If a lookup_key is already registered to a DIFFERENT
        canonical channel, the registration is REFUSED (first registration wins)
        and a warning is logged. This prevents silent wrong wiring.

        Args:
            canonical_channel: The canonical PQN channel name
                (e.g., "SolarBatteryDesign__...cost_model__total_cost").
            lookup_keys: List of lookup keys that should resolve to this channel
                (e.g., ["cost_model.total_cost", "SolarBatteryDesign__...total_cost",
                        "solar_battery_plant.solar_array.pv_module.cost_model.total_cost"]).
        """
        self._canonical.add(canonical_channel)
        self._index[canonical_channel] = canonical_channel
        for key in lookup_keys:
            if key in self._index and self._index[key] != canonical_channel:
                logger.warning(
                    "OutputRegistry key collision: '%s' already maps to '%s', "
                    "refusing to overwrite with '%s'",
                    key, self._index[key], canonical_channel,
                )
                continue
            self._index[key] = canonical_channel

    def register_alias(self, alias: str, canonical_channel: str) -> None:
        """Register an alias that maps to an existing canonical channel.

        The canonical_channel MUST already be registered (either as a canonical
        channel via register() or resolvable through the index). This is
        enforced by an assertion.

        Collision policy: Same as register() -- refuse overwrite, log warning.

        Args:
            alias: The alias key (e.g., "solar_array.total_capex").
            canonical_channel: The canonical PQN channel name this alias
                resolves to. Must already exist in the registry.

        Raises:
            AssertionError: If canonical_channel is not registered.
        """
        assert canonical_channel in self._canonical, (
            f"Cannot alias to unregistered channel: {canonical_channel}"
        )
        if alias in self._index and self._index[alias] != canonical_channel:
            logger.warning(
                "OutputRegistry alias collision: '%s' already maps to '%s', "
                "refusing to overwrite with '%s'",
                alias, self._index[alias], canonical_channel,
            )
            return
        self._index[alias] = canonical_channel

    def resolve(self, source_path: str) -> str | None:
        """Resolve a source_path to a canonical channel name.

        Exact match only. No normalization, no cascade, no fallback.

        This method is a pure function: given the same registry state and
        source_path, it always returns the same result.

        Empirically validated:
        - Spike 1: CHAIN bindings always use DOTTED format (exact match works)
        - Spike 5: SYSML_QN normalization is broken (so we don't try it)
        - Spike 4: Bare names never appear (so we don't check for them)

        Args:
            source_path: The binding source path to resolve.
                Typically DOTTED format (e.g., "alpha_split.p_alpha").

        Returns:
            Canonical channel name (PQN format) if found, None otherwise.
        """
        return self._index.get(source_path)

    # Diagnostic methods -- see Spec 02 Section 3 for the authoritative
    # OutputRegistry class interface (including __len__, __contains__,
    # channels(), keys()). The methods below are supplementary diagnostics
    # specific to the construction protocol.

    @property
    def canonical_count(self) -> int:
        """Number of registered canonical channels."""
        return len(self._canonical)

    @property
    def total_keys(self) -> int:
        """Total number of registered lookup keys (including aliases)."""
        return len(self._index)

    def dump(self) -> dict[str, str]:
        """Return a copy of the full index (for debugging/testing)."""
        return dict(self._index)
```

> **NOTE**: The authoritative OutputRegistry class interface is defined in
> **Spec 02**. This spec (Spec 05) defines the *construction protocol* and
> supplementary diagnostics. If Spec 02 and Spec 05 disagree on the class
> interface, Spec 02 takes precedence.

---

## 9. Invariants and Contracts

### 9.1 Phase Ordering Contract

| Phase | May Reference | Produces |
|---|---|---|
| Phase 1 | Nothing (builds from raw data) | Canonical channels + Key_A/B/C/D/E/F |
| Phase 2 | Phase 1 keys only | CHAIN alias -> canonical channel |
| Phase 3 | Phase 1 + Phase 2 keys | EXPOSE_PURE alias -> canonical channel |
| Phase 4 | Phase 1 + Phase 2 + Phase 3 keys | Transitive design attr alias -> canonical channel |

**Violation handling**: If any phase N alias fails to resolve against prior
phases, a warning is logged. The alias is NOT registered (it cannot map to
an unknown channel). This is a diagnostic signal, not a crash -- downstream
backtracking will handle the unresolved binding via its design-attribute
fallback path.

### 9.2 Key Uniqueness

- **Canonical channels** are globally unique (PQN format encodes full hierarchy).
- **Lookup keys** may collide across different channels. Collision policy:
  first registration wins, warning logged, overwrite refused.
- Spike 8 validated: zero collisions across 217 keys in solar_battery and
  33 keys in e2e_attr_expr.

### 9.3 No Bare Names

- No bare-name registration (Spike 4: zero bare-name references in 94 bindings).
- All keys are either dotted (`"instance.output"`) or EQN (`"ns__usage__output"`).

### 9.4 No SYSML_QN Keys

- No `::` format keys in the registry (Spike 5: SYSML_QN normalization is broken).
- REFERENCE bindings (which use `::` format) are handled by the backtracker's
  secondary resolution path, not by the OutputRegistry.

### 9.5 Registration Completeness

After Phase 1 completes, the following guarantee holds:

> For every non-template CalcUsage in the pipeline, and for every output
> attribute on its CalcDef, there exists exactly one canonical channel in the
> registry, reachable via Key_A, Key_B, or Key_C.

> For every ScopedAggregationData, there exists exactly one canonical channel,
> reachable via Key_D or Key_E.

> For every FORMULA FULLY_COMPILABLE computed attribute, there exists exactly
> one canonical channel, reachable via Key_F.

---

## 10. Error Handling

### 10.1 Missing CalcDef for CalcUsage

If a CalcUsage references a CalcDef name not in `calc_defs`, skip it with a
debug log. This can happen with synthetic CalcUsages for computed attributes
where `calc_def_name` may be `None`.

### 10.2 Phase Resolution Failures

Each phase logs warnings for aliases that fail to resolve. The summary log
at the end of each phase reports registered vs. failed counts.

### 10.3 Collision Logging

Key collisions are logged at WARNING level with the colliding key, the existing
target channel, and the refused new channel. This provides full diagnostic
context for debugging.

---

## 11. Testing Strategy

### 11.1 Unit Tests

Tests in `tests/unit/test_output_registry.py`:

1. **OutputRegistry basic operations**:
   - `register()` adds keys to index
   - `register()` collision handling (first wins, warning logged)
   - `register_alias()` maps to canonical channel
   - `register_alias()` assertion on unregistered canonical
   - `resolve()` exact match returns canonical
   - `resolve()` unknown returns None

2. **Phase ordering tests**:
   - Phase 2 alias resolves only after Phase 1 canonical is registered
   - Phase 3 alias resolves against Phase 1 + Phase 2
   - Phase 4 alias resolves against Phase 1 + Phase 2 + Phase 3

3. **Key format tests** (from Spike 8 data):
   - Key_A resolves for concrete CalcUsage outputs
   - Key_B resolves for all CalcUsage outputs
   - Key_C resolves for virtual CalcUsage outputs
   - Key_D resolves for aggregation outputs
   - Key_E resolves for aggregation outputs (full dotted)
   - Key_F resolves for FORMULA outputs
   - Aggregation alias variants resolve

4. **`_is_transitive_default()` tests**:
   - `None` default -> False
   - `"0.92"` (no dot... wait, it has a dot) -> False (float)
   - `"3.14"` -> False (float)
   - `"2600.0"` -> False (float)
   - `"cost_model.total_cost"` -> True (dotted path)
   - `"true"` -> False (no dot)
   - `"some_name"` -> False (no dot)

### 11.2 Integration Tests

Tests in `tests/unit/test_output_registry_construction.py`:

1. **`_build_output_registry()` with synthetic data**: Verify that a registry
   built from representative CalcUsage, aggregation, and computed attribute
   data resolves all expected keys.

2. **Phase summary logging**: Verify that each phase logs the correct
   registered/failed counts.

### 11.3 Contract Tests

Tests verifying the interface contract between OutputRegistry and Backtracker:

1. For every CHAIN binding in test fixtures, the key the backtracker constructs
   for `registry.resolve()` exists in the registry built from the same data.
2. For every REFERENCE binding that should resolve to MODULE_OUTPUT, the
   secondary resolution key (`parent_part.leaf_name`) exists in the registry.

---

## 12. Traceability to Design Document

| Design Section | Spec Section | Key Decisions |
|---|---|---|
| 08_algorithm S6 (Step 5) | Sections 3-6 | 4-phase registration protocol |
| 08_algorithm S12 (Output Registry) | Section 8 | OutputRegistry class design |
| 08_algorithm S12 Key Format | Section 3 | Key_A through Key_F formats |
| Spike 4 | Section 9.3 | No bare-name registration |
| Spike 5 | Section 9.4 | No SYSML_QN keys |
| Spike 6 | Section 4 | CHAIN alias filtering (BARE CAS codes) |
| Spike 7 | Section 6 | Transitive default detection |
| Spike 8 | Sections 3.1, 4.3, 5.4, 6.3 | Key_C requirement, PartDef filter, zero collisions |

---

## 13. Open Questions

### 13.1 PartDef vs. PartUsage Identification for Phase 4

Phase 4 filters PartDef-level transitive defaults (they can't resolve).
The current approach is to attempt resolution and let failures fall through
harmlessly. A more robust approach would add `is_on_part_definition` to
`DesignAttributeData` during extraction (mirroring the approach for
`ComputedAttributeData`). Decision deferred to implementation.

### 13.2 Synthetic CalcUsage Registration

Synthetic CalcUsages created from FORMULA computed attributes in Step 4.5
may not have a `calc_def_name` in the `calc_def_lookup`. The Phase 1 CalcUsage
loop should handle this gracefully (skip or use a different path). The FORMULA
channel is registered separately in Phase 1 Section 3.3.

### 13.3 Key_A Collisions for Virtual CalcUsages

Virtual CalcUsages with the same `instance_name` across different parent scopes
(e.g., two `cost_model` usages under different PartDefs) will produce Key_A
collisions. The collision policy (first wins, warning logged) handles this.
Key_B (EQN, globally unique) and Key_C (dotted hierarchy, scope-differentiated)
remain collision-free for these cases.

---

**Last Updated**: 2026-02-13
