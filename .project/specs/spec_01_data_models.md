# Spec 01: Data Models -- ChannelAlias

**Epic**: OUTPUT-REGISTRY (Item 1)
**Target file**: `src/sysml_codegen/core/models.py`
**Status**: Draft
**Created**: 2026-02-13

---

## 1. Overview

This spec defines the `ChannelAlias` dataclass, a first-class data model representing an explicit alias for a pipeline output channel. A `ChannelAlias` maps one scoped dotted key (the alias) to another scoped dotted key (the canonical channel name) with provenance tracking.

`ChannelAlias` replaces two ad-hoc alias mechanisms:
- `AggregationExpressionData.aliases: list[str]` (unscoped, no provenance)
- The heuristic param_name divergence scan in Step 3.6 (`_enrich_aliases_from_bindings()`)

### Traceability

| Spike | Finding | How it informs this spec |
|-------|---------|--------------------------|
| Spike 3 | `expression_text` is NOT a dotted path for EXPOSE_PURE (SysIDE produces `".(component_cost)"`). Must use `references` field. | Canonical name construction rule for `source="expose_pure"` |
| Spike 6 | 41 DOTTED CHAIN redefs, 13 BARE CAS codes (not references). All DOTTED are `cost_model.{output_name}` pattern. | Construction rule for `source="redefinition"`, BARE filtering |
| Spike 8 | Zero collisions across 250 keys. Instance_path includes design prefix as first segment. | Scoping rules for alias_name and canonical_name |

---

## 2. ChannelAlias Dataclass

### 2.1 Location

Add to `src/sysml_codegen/core/models.py`, after the existing `BindingResolution` class.

### 2.2 Definition

```python
from dataclasses import dataclass


@dataclass
class ChannelAlias:
    """An explicit alias for a pipeline output channel.

    Maps one scoped dotted key (the alias) to another scoped dotted key (the
    canonical channel name). Aliases are produced by two authoritative sources:

    1. :>> CHAIN redefinitions (source="redefinition") -- produced in Step 3.5D
       when a PartDef attribute is redefined via a dotted path pointing at a
       child CalcUsage output. Example: :>> capital_cost = cost_model.total_cost

    2. EXPOSE_PURE classifications (source="expose_pure") -- produced in Step 4.5
       when a PartUsage attribute directly exposes a sibling CalcUsage output
       via a FeatureChainExpression. Example: total_capex = financial.total_cost

    Both alias_name and canonical_name are scoped dotted keys. They are NOT bare
    names and they are NOT in SysML :: format.

    Attributes:
        alias_name: Scoped dotted key for the alias.
            For redefinition: "{instance_path}.{redef.attribute_name}"
            For expose_pure: "{owning_part_short_name}.{python_name}"
        canonical_name: Scoped dotted key for the target channel.
            For redefinition: "{instance_path}.{redef.source_path}"
            For expose_pure: "{references[1].name}.{references[0].name}"
        owning_part_qn: Qualified name of the PartDef or PartUsage where
            the alias originates. Uses __ separator (ADR-003).
        source: Provenance tag. One of "redefinition" or "expose_pure".
    """

    alias_name: str
    canonical_name: str
    owning_part_qn: str
    source: str  # "redefinition" | "expose_pure"
```

### 2.3 Field Specifications

#### `alias_name: str`

**Type**: `str` -- scoped dotted key.

**Description**: The lookup key that downstream bindings use to reference this channel indirectly. This is the name visible in the design hierarchy (e.g., an attribute name on a PartDef that redefined a CalcUsage output).

**Format**: Dotted notation with scope prefix for `"redefinition"` source. **Bare python_name** for `"expose_pure"` source (scoped at Phase 3 registration time, not at production time). Never SysML `::` format.

**Construction rules by source**:

| Source | Construction | Example | When Scoped |
|--------|-------------|---------|-------------|
| `"redefinition"` | `f"{instance_path}.{redef.attribute_name}"` | `"solar_array.total_capex"` | At construction time |
| `"expose_pure"` | `ca.python_name` (bare) | `"total_capex"` | At Phase 3 registration: `f"{owning_part_short}.{alias_name}"` |

Where:
- `instance_path` is the design-prefix-stripped, dotted form of the `ScopedAggregationData.instance_path`. Derivation: `".".join(instance_path.split("__")[1:])` -- strips the PascalCase design PartDef prefix, replaces `__` with `.`
- `redef.attribute_name` is the redefined attribute name from `RedefinitionData`
- `python_name` is the sanitized Python identifier from `ComputedAttributeData.python_name`
- Phase 3 scoping (Spec 05 Section 5): `owning_part_short = alias.owning_part_qn.split("__")[-1]`

#### `canonical_name: str`

**Type**: `str` -- scoped dotted key.

**Description**: The dotted key of the actual pipeline channel that this alias points to. Must resolve to a registered canonical channel in the OutputRegistry.

**Format**: Dotted notation matching one of the registered key formats (Key_A through Key_F). Never bare, never SysML `::` format.

**Construction rules by source**:

| Source | Construction | Example |
|--------|-------------|---------|
| `"redefinition"` | `f"{instance_path}.{redef.source_path}"` | `"solar_array.cost_model.total_cost"` |
| `"expose_pure"` | `f"{references[1].name}.{references[0].name}"` | `"component_cost.total_cost"` |

Where:
- `instance_path` is the same design-prefix-stripped dotted path used for `alias_name`
- `redef.source_path` is the RHS dotted path from the `:>>` redefinition (e.g., `"cost_model.total_cost"`)
- `references[1].name` is the CalcUsage instance name (e.g., `"component_cost"`)
- `references[0].name` is the output attribute name (e.g., `"total_cost"`)

**CRITICAL**: For `"expose_pure"` source, canonical_name MUST be constructed from the `ComputedAttributeData.references` field, NOT from `expression_text`. SysIDE produces `expression_text = ".(component_cost)"` which is not a parseable dotted key (Spike 3 finding).

#### `owning_part_qn: str`

**Type**: `str` -- SysML qualified name using `__` separator.

**Description**: The fully qualified name of the PartDef or PartUsage where the alias originates. Used for provenance tracking and debugging, not for key construction.

**Example**: `"SolarBatteryLibrary__PV_Module"` (for a redefinition on the PV_Module PartDef)

#### `source: str`

**Type**: `str` -- one of `"redefinition"` or `"expose_pure"`.

**Description**: Provenance tag identifying which extraction step produced this alias.

| Value | Producer Step | Semantic |
|-------|-------------|----------|
| `"redefinition"` | Step 3.5D | `:>>` CHAIN redefinition mapping attribute to CalcUsage output |
| `"expose_pure"` | Step 4.5 | `EXPOSE_PURE` computed attribute directly aliasing a CalcUsage output |

---

## 3. Construction Rules -- Detailed Examples

### 3.1 Redefinition Source (Step 3.5D)

**Input data**:
```python
# From hierarchy_resolver:
redef = RedefinitionData(
    owning_part_qn="SolarBatteryLibrary__PV_Module",
    attribute_name="capital_cost",
    redefinition_type=RedefinitionType.CHAIN,
    source_path="cost_model.total_cost",
)

# From ScopedAggregationData:
instance_path = "SolarBatteryDesign__solar_battery_plant__solar_array__pv_module"
```

**Derivation**:
```python
# Strip design prefix, replace __ with .
segments = instance_path.split("__")   # ["SolarBatteryDesign", "solar_battery_plant", "solar_array", "pv_module"]
dotted_instance = ".".join(segments[1:])  # "solar_battery_plant.solar_array.pv_module"

alias = ChannelAlias(
    alias_name=f"{dotted_instance}.{redef.attribute_name}",
    # => "solar_battery_plant.solar_array.pv_module.capital_cost"
    canonical_name=f"{dotted_instance}.{redef.source_path}",
    # => "solar_battery_plant.solar_array.pv_module.cost_model.total_cost"
    owning_part_qn=redef.owning_part_qn,
    # => "SolarBatteryLibrary__PV_Module"
    source="redefinition",
)
```

**Filtering rule**: Skip CHAIN redefinitions where `"." not in redef.source_path`. These are CAS codes (e.g., `"CAS220101"`) or string literals, not channel references. Spike 6 found 13 such cases in solar_battery, all `cas_category` attributes with CAS code values. Filter: `if redef.source_path and "." not in redef.source_path: continue`.

### 3.2 EXPOSE_PURE Source (Step 4.5)

**Input data**:
```python
# From computed_attribute_extractor:
computed_attr = ComputedAttributeData(
    name="total_capex",
    python_name="total_capex",
    owning_part_name="e2e_plant",
    owning_part_qualified_name="E2EAttrExprDesign::e2e_plant",
    expression_text=".(component_cost)",    # DO NOT USE for canonical_name
    references=[
        ExpressionRef(name="total_cost", qualified_name="...::total_cost"),   # [0] = output attr
        ExpressionRef(name="component_cost", qualified_name="...::component_cost"),  # [1] = instance
    ],
    classification=ComputedAttributeClassification.EXPOSE_PURE,
    compilability=Compilability.MANUAL_REQUIRED,
)
```

**Derivation** (see Spec 04 Change B for authoritative construction):
```python
# owning_part_qn converted to Python QN format
owning_qn = sysml_to_python_qualified_name(computed_attr.owning_part_qualified_name)
# => "E2EAttrExprDesign__e2e_plant"

alias = ChannelAlias(
    alias_name=computed_attr.python_name,
    # => "total_capex"  (BARE -- scoped at Phase 3 registration time)
    canonical_name=f"{computed_attr.references[1].name}.{computed_attr.references[0].name}",
    # => "component_cost.total_cost"
    owning_part_qn=owning_qn,
    # => "E2EAttrExprDesign__e2e_plant"
    source="expose_pure",
)
# At Phase 3 registration (Spec 05):
#   owning_part_short = owning_qn.split("__")[-1]  => "e2e_plant"
#   scoped_alias = f"{owning_part_short}.{alias.alias_name}"  => "e2e_plant.total_capex"
#   registry.register_alias(scoped_alias, canonical_channel)
```

**Filtering rule**: Only produce ChannelAlias for EXPOSE_PURE on **PartUsages** (concrete design instances), NOT on PartDefs. PartDef-level EXPOSE_PURE attributes produce unscoped canonical names that cannot resolve against instance-scoped registry keys (Spike 8: Issue 21). CHAIN aliases from Step 3.5D handle the PartDef-level aliasing role (41/41 resolved in solar_battery).

**Filter heuristic**: A computed attribute is on a PartDef (not a PartUsage) if the owning_part_qualified_name does NOT contain a design PartDef prefix followed by a PartUsage name. In practice, check whether the owning element appears as a PartUsage in the design hierarchy. The specific filter implementation is deferred to the Spec 02 (OutputRegistry) construction logic, but the data model itself is agnostic -- the filter applies at alias production time, not at the dataclass level.

---

## 4. Validation Invariants

The following invariants MUST hold for every `ChannelAlias` instance:

### 4.1 Format Invariants

| Invariant | Rule | Rationale |
|-----------|------|-----------|
| Scoped alias_name for redefinition | `"." in alias.alias_name` when `source == "redefinition"` | Redefinition aliases are pre-scoped (Spike 4: zero bare-name references) |
| Bare alias_name for expose_pure | `"." not in alias.alias_name` when `source == "expose_pure"` | EXPOSE_PURE aliases are bare; scoped at Phase 3 registration (Spec 05) |
| No bare canonical_name | `"." in alias.canonical_name` | All canonical names are dotted paths (Spike 6: all DOTTED CHAIN redefs have `.`) |
| No SysML QN in alias_name | `"::" not in alias.alias_name` | Aliases use dotted format only (Spike 1: DOTTED for CHAIN) |
| No SysML QN in canonical_name | `"::" not in alias.canonical_name` | Canonical names use dotted format only |
| Valid source | `alias.source in ("redefinition", "expose_pure")` | Only two provenance types |
| Non-empty owning_part_qn | `len(alias.owning_part_qn) > 0` | Must have provenance |

### 4.2 Semantic Invariants

| Invariant | Rule | Rationale |
|-----------|------|-----------|
| Alias differs from canonical | `alias.alias_name != alias.canonical_name` | An alias that maps to itself is useless |
| Canonical resolves in registry | `registry.resolve(alias.canonical_name) is not None` at registration time | Phase ordering ensures canonical is already registered before alias |

### 4.3 Source-Specific Invariants

**For `source="redefinition"`**:
- `alias.canonical_name` contains at least two `.`-separated segments (instance + CalcUsage + output)
- The `redef.source_path` that produced the canonical_name has `"."` in it (BARE CAS codes filtered)

**For `source="expose_pure"`**:
- `alias.canonical_name` has exactly two segments: `{instance_name}.{output_name}`
- The canonical_name was constructed from `references`, NOT from `expression_text`
- The owning element is a PartUsage, not a PartDef (PartDef EXPOSE_PURE filtered)

---

## 5. Modifications to Existing Models

### 5.1 `__all__` Export in `core/models.py`

Add `"ChannelAlias"` to the `__all__` list:

```python
__all__ = [
    "BindingResolution",
    "BindingResolutionType",
    "ChannelAlias",
]
```

### 5.2 PipelineContext (Future -- Item 3)

`PipelineContext` in `generation/initialization.py` will need an `output_registry` field when Item 3 integrates the OutputRegistry into the pipeline. This is OUT OF SCOPE for Item 1 but noted here for traceability:

```python
# Future addition (Item 3):
@dataclass
class PipelineContext:
    # ... existing fields ...
    output_registry: OutputRegistry  # Added by Item 3
```

The `output_registry` field replaces the need for `PipelineContext` to carry `ChannelAlias` lists directly. The `OutputRegistry` owns all alias registrations and provides `resolve()` for downstream consumers.

### 5.3 AggregationExpressionData.aliases (Future -- Item 2)

The `aliases: list[str]` field on `AggregationExpressionData` in `extraction/data_models.py` will be superseded by `ChannelAlias` objects. Item 2 will either:
- Remove the field entirely, or
- Keep it for backward compatibility during the transition and ignore it in favor of `ChannelAlias`

This is OUT OF SCOPE for Item 1 but noted for awareness.

### 5.4 No Changes to BindingResolution

`BindingResolution` is unchanged. It remains the output of the backtracker. `ChannelAlias` is an input to the OutputRegistry (which is an input to the backtracker). They occupy different layers:

```
ChannelAlias -> OutputRegistry -> DependencyBacktracker -> BindingResolution
```

---

## 6. Dataclass Design Rationale

### Why a dataclass (not Pydantic BaseModel)?

`ChannelAlias` follows the pattern of other extraction/analysis data models in this codebase (`RedefinitionData`, `ComputedAttributeData`, `ScopedAggregationData`) which are all `@dataclass`. Pydantic `BaseModel` is used for serializable pipeline output models (`BindingResolution`, `ComputationGraph`). `ChannelAlias` is an intermediate analysis artifact, not a serialized output.

### Why not an enum for `source`?

The `source` field uses `str` rather than an enum for simplicity and forward compatibility. Only two values exist today. If a third source type emerges (unlikely given the design), it can be added without modifying an enum definition. The validation invariant `source in ("redefinition", "expose_pure")` enforces the contract at test time.

### Why scoped dotted keys (not bare names)?

Spike 4 proved zero bare-name references exist in practice across 94 bindings and 4 models. Spike 8 proved zero collisions with scoped keys across 250 keys and 2 models. Bare names create ambiguity (e.g., `total_cost` is produced by 9 different virtual CalcUsages in solar_battery). Scoped dotted keys are unambiguous by construction.

---

## 7. Test Requirements

Unit tests for `ChannelAlias` should verify:

1. **Construction from redefinition data**: Given a `RedefinitionData` and `instance_path`, produce a `ChannelAlias` with correct scoping
2. **Construction from EXPOSE_PURE data**: Given a `ComputedAttributeData` with `references`, produce a `ChannelAlias` using `references[1].name` and `references[0].name`
3. **BARE filtering**: Verify that CHAIN redefs with no `.` in `source_path` are excluded before `ChannelAlias` construction
4. **PartDef filtering**: Verify that EXPOSE_PURE on PartDefs does not produce a `ChannelAlias`
5. **Format invariants**: Assert no `::` in alias_name or canonical_name, assert `.` present in both
6. **Equality**: Two `ChannelAlias` instances with identical fields compare equal (dataclass default)

---

## 8. File Diff Summary

### `src/sysml_codegen/core/models.py`

```diff
+ from dataclasses import dataclass
+
  # After BindingResolution class:
+
+ @dataclass
+ class ChannelAlias:
+     """An explicit alias for a pipeline output channel.
+     ... (full docstring as specified in Section 2.2)
+     """
+     alias_name: str
+     canonical_name: str
+     owning_part_qn: str
+     source: str  # "redefinition" | "expose_pure"
+
  __all__ = [
      "BindingResolution",
      "BindingResolutionType",
+     "ChannelAlias",
  ]
```

No other files are modified by this spec. Construction logic (the code that creates `ChannelAlias` instances) is specified in the epic's Item 2 scope (alias producers).

---

**Last Updated**: 2026-02-13
