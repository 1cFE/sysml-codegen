# Spec 04: Step 4.5 Computed Attribute Extractor Changes

**Status**: Draft
**Spec ID**: SPEC-04
**Epic**: OUTPUT-REGISTRY
**Affected files**:
- `src/sysml_codegen/generation/initialization.py` (modified -- `_extract_and_filter_computed_attributes`)
- `src/sysml_codegen/extraction/computed_attribute_extractor.py` (modified -- add `is_on_part_definition` tracking)
- `src/sysml_codegen/extraction/data_models.py` (modified -- add field to `ComputedAttributeData`)
- `src/sysml_codegen/extraction/usage_extractor.py` (read-only dependency -- `CalcUsageData`, `BindingInfo`)

**Design reference**: `.project/reports/08_algorithm_revised.md` Section 5 (Steps 4-4.5)

**Depends on**: SPEC-03 (for `ChannelAlias` data model in `core/models.py`)

---

## Summary of Changes

Step 4.5 currently extracts computed attributes and removes FORMULAs from design_attrs. This spec adds two new outputs:

1. **EXPOSE_PURE produces `ChannelAlias` objects** instead of being stored in a computed attribute index. This is the fix for Bug 2 (two-hop EXPOSE_PURE failure).
2. **FORMULA produces synthetic `CalcUsageData` objects** that flow through normal backtracking. This is the mechanism for getting FORMULA attributes into the pipeline as modules.

| Current | Target | Rationale |
|---------|--------|-----------|
| EXPOSE_PURE goes into `_computed_attr_index` alongside FORMULA | EXPOSE_PURE produces `ChannelAlias` (NOT module index entry) | Bug 2 root cause: backtracker builds channel name for a module that does not exist |
| FORMULA attrs: extracted and flagged, but no CalcUsageData created here | FORMULA attrs: synthetic `CalcUsageData` constructed and appended to calc_usages | Makes pipeline self-contained -- FORMULA attrs flow through standard backtracking |
| Return type: `list[ComputedAttributeData]` | Return type: `tuple[list[ComputedAttributeData], list[ChannelAlias], list[CalcUsageData]]` | Caller needs all three outputs |

---

## Change A: Add `is_on_part_definition` to `ComputedAttributeData`

### Problem

EXPOSE_PURE attributes on PartDefinitions produce PartDef-local canonical names (e.g., `"component_cost.total_cost"`) that cannot resolve against instance-scoped registry keys (e.g., `"solar_battery_plant.solar_array.pv_module.cost_model.total_cost"`). CHAIN aliases from Step 3.5 already handle PartDef aliasing (Spike 8: 41/41 resolved in solar_battery). PartDef EXPOSE_PURE must be filtered out.

### Current state

`ComputedAttributeData` (in `data_models.py`, lines 182-216) has no field indicating whether the owning element is a PartDefinition or PartUsage. The `owning_part_qualified_name` field stores the SysML `::` format QN but does not indicate element type.

### Solution: Add `is_on_part_definition` field

Add a new field to `ComputedAttributeData`:

```python
@dataclass
class ComputedAttributeData:
    # ... existing fields (lines 205-216) ...

    # True if the owning element is a PartDefinition (not a PartUsage).
    # Used to filter out PartDef EXPOSE_PURE in Step 4.5 (Spike 8: Issue 21).
    is_on_part_definition: bool = False
```

### How to populate it

The `_extract_and_filter_computed_attributes` function in `initialization.py` already knows whether each element is a PartDefinition or PartUsage because it iterates them separately (lines 178-179):

```python
# Current code (initialization.py lines 178-179):
part_elements = list(SysideAdapter.elements_of_type(model, "PartDefinition"))
part_elements.extend(SysideAdapter.elements_of_type(model, "PartUsage"))
```

The fix is to track which elements are PartDefinitions and pass that information through. Two options:

**Option A (preferred): Track in the loop and set post-hoc.**

```python
part_defs = list(SysideAdapter.elements_of_type(model, "PartDefinition"))
part_usages = list(SysideAdapter.elements_of_type(model, "PartUsage"))

# Extract from PartDefinitions
for part_elem in part_defs:
    computed = extract_computed_attributes(None, part_elem, calc_usage_names)
    for ca in computed:
        ca.is_on_part_definition = True
    all_computed_attrs.extend(computed)

# Extract from PartUsages
for part_elem in part_usages:
    computed = extract_computed_attributes(None, part_elem, calc_usage_names)
    # is_on_part_definition defaults to False -- correct for PartUsages
    all_computed_attrs.extend(computed)
```

**Option B: Pass flag to `extract_computed_attributes`.**

This would require changing the signature of `extract_computed_attributes` in `computed_attribute_extractor.py`. Since that function is a leaf module, this is acceptable but Option A is simpler because it avoids changing the extraction-layer interface.

**Decision**: Use Option A. The orchestrator (`initialization.py`) sets the field post-hoc. The extractor (`computed_attribute_extractor.py`) does not need to change its signature.

---

## Change B: EXPOSE_PURE Produces `ChannelAlias`

### Current behavior

EXPOSE_PURE attributes are returned in the `list[ComputedAttributeData]` alongside FORMULA, EXPOSE_COMPUTED, and UNRESOLVABLE attributes. The backtracker's `_computed_attr_index` treats them the same as FORMULA, building a channel name for a module that does not exist -- this is Bug 2.

### Target behavior

EXPOSE_PURE attributes produce `ChannelAlias` objects. They are NOT added to any module index. They are NOT available for direct resolution. They exist ONLY as aliases in the OutputRegistry, which resolves them transitively.

### Critical implementation detail: use `references` field, NOT `expression_text`

```python
# WRONG: expression_text is raw AST text from SysIDE
# Spike 3 confirmed: expression_text = ".(component_cost)" -- NOT parseable
# canonical_target = parse_dotted(ca.expression_text)  # BROKEN

# CORRECT: reconstruct from references field
# references[0].name = "total_cost"       (output attribute name)
# references[1].name = "component_cost"   (CalcUsage instance name)
if len(ca.references) >= 2:
    instance_name = ca.references[1].name   # CalcUsage instance
    output_name = ca.references[0].name      # output attribute
    canonical_target = f"{instance_name}.{output_name}"
```

The `references` field is a `list[ExpressionRef]` from `agentic_mbse.sysml.types`. Each `ExpressionRef` has a `.name` and `.qualified_name`. The ordering is deterministic: for a pure `FeatureChainExpression` like `component_cost.total_cost`, the references are `[ExpressionRef(name="total_cost", ...), ExpressionRef(name="component_cost", ...)]` -- the leaf attribute first, then the instance.

### EXPOSE_PURE alias construction (in `_extract_and_filter_computed_attributes`)

```python
from sysml_codegen.core.models import ChannelAlias

expose_pure_aliases: list[ChannelAlias] = []

for ca in all_computed_attrs:
    if ca.classification != ComputedAttributeClassification.EXPOSE_PURE:
        continue

    # FILTER: Skip EXPOSE_PURE on PartDefs (Spike 8: Issue 21).
    # PartDef-local canonical names can't resolve against instance-scoped
    # registry keys. CHAIN aliases from Step 3.5 handle PartDef aliasing.
    if ca.is_on_part_definition:
        logger.debug(
            "Skipping PartDef EXPOSE_PURE '%s' on '%s' -- "
            "CHAIN aliases handle PartDef aliasing",
            ca.python_name, ca.owning_part_name,
        )
        continue

    # Reconstruct canonical target from references field.
    # Spike 3: expression_text is ".(component_cost)" -- raw AST, not parseable.
    # references[0].name = output attribute, references[1].name = CalcUsage instance.
    if len(ca.references) >= 2:
        instance_name = ca.references[1].name
        output_name = ca.references[0].name
        canonical_target = f"{instance_name}.{output_name}"
    else:
        logger.warning(
            "EXPOSE_PURE '%s' on '%s' has %d references (expected >= 2), skipping",
            ca.python_name, ca.owning_part_name, len(ca.references),
        )
        continue

    expose_pure_aliases.append(ChannelAlias(
        alias_name=ca.python_name,  # BARE -- scoped at Phase 3 registration (Spec 05)
        canonical_name=canonical_target,
        owning_part_qn=sysml_to_python_qualified_name(ca.owning_part_qualified_name),  # __ format per ADR-003
        source="expose_pure",
    ))

logger.info(
    "Step 4.5: Produced %d EXPOSE_PURE aliases (%d PartDef skipped)",
    len(expose_pure_aliases),
    sum(1 for ca in all_computed_attrs
        if ca.classification == ComputedAttributeClassification.EXPOSE_PURE
        and ca.is_on_part_definition),
)
```

### Invariants

1. **Never use `expression_text`** for EXPOSE_PURE canonical target construction. It is raw AST text (e.g., `".(component_cost)"`), not a parseable dotted key. (Spike 3)
2. **PartDef EXPOSE_PURE are filtered out.** Only PartUsage EXPOSE_PURE produce aliases. (Spike 8: Issue 21)
3. **Reference count check.** If `len(ca.references) < 2`, log a warning and skip. This is a defensive guard against unexpected AST shapes.
4. **Alias `alias_name` is the bare python_name** (e.g., `"total_capex"`), not scoped. The OutputRegistry Phase 3 registration logic (separate spec) is responsible for scoping it with the owning part name (e.g., `"e2e_plant.total_capex"`).

### Traceability

- Spike 3: EXPOSE_PURE `expression_text` is `".(component_cost)"`. `references` field is the only reliable source.
- Spike 8: Issue 21 -- PartDef EXPOSE_PURE produces unresolvable canonical names. CHAIN aliases handle this role.
- Bug 2: `financial.total_capex` in e2e_attr_expr resolves to ENTRY_POINT because `_computed_attr_index` creates a channel for a module that does not exist. The fix is: EXPOSE_PURE produces a `ChannelAlias`, not a module index entry.

---

## Change C: FORMULA Produces Synthetic `CalcUsageData`

### Current behavior

FORMULA-classified computed attributes are extracted and flagged. The `graph_builder.py` (line 826) later creates `PipelineModule` objects with `is_computed_attribute=True` directly. However, the FORMULA inputs are not resolved through the standard backtracker pipeline -- they use a separate wiring path in graph_builder.

### Target behavior

FORMULA attributes produce synthetic `CalcUsageData` objects at Step 4.5 time. These synthetic usages are appended to `calc_usages` and flow through the standard backtracking pipeline (Step 6). Their CHAIN bindings resolve through the OutputRegistry like any other CalcUsage binding.

### Synthetic CalcUsageData construction

```python
from sysml_codegen.core.qualified_names import sysml_to_python_qualified_name
from sysml_codegen.extraction.usage_extractor import BindingInfo, CalcUsageData

synthetic_usages: list[CalcUsageData] = []

for ca in all_computed_attrs:
    if ca.classification != ComputedAttributeClassification.FORMULA:
        continue
    if ca.compilability != Compilability.FULLY_COMPILABLE:
        continue  # Only FULLY_COMPILABLE FORMULAs become pipeline modules

    # Build the execution qualified name (EQN) for the synthetic module.
    # Format: "{parent_eqn}__{python_name}"
    # The parent EQN comes from converting the SysML :: QN to __ format.
    parent_eqn = sysml_to_python_qualified_name(ca.owning_part_qualified_name)
    parent_short = ca.owning_part_name  # e.g., "e2e_plant"

    # Build bindings from references (exclude self-reference).
    # Each reference that is NOT the attribute itself becomes a CHAIN binding
    # with a scoped dotted source_path.
    formula_bindings: list[BindingInfo] = []
    for ref in ca.references:
        if ref.name == ca.python_name:
            continue  # exclude self-reference

        formula_bindings.append(BindingInfo(
            param_name=ref.name,
            binding_type=BindingType.CHAIN,
            source_path=f"{parent_short}.{ref.name}",
        ))

    synthetic_usage = CalcUsageData(
        instance_name=ca.python_name,
        calc_def_name="",                          # inline expression, no CalcDef
        calc_def_qualified_name="",                # no CalcDef
        module_type="",                            # derived later by graph_builder
        qualified_name=f"{parent_eqn}__{ca.python_name}",
        bindings=formula_bindings,
        unbound_params=[],
        is_template=False,
        owning_part_def_qn=None,
    )
    synthetic_usages.append(synthetic_usage)

logger.info(
    "Step 4.5: Created %d synthetic CalcUsageData from FORMULA attributes",
    len(synthetic_usages),
)
```

### CalcUsageData field notes

The `CalcUsageData` dataclass (usage_extractor.py lines 91-131) requires these fields:

| Field | Value for synthetic usage | Notes |
|-------|--------------------------|-------|
| `instance_name` | `ca.python_name` | e.g., `"power_mw"` |
| `calc_def_name` | `""` (empty string) | No CalcDef -- inline expression |
| `calc_def_qualified_name` | `""` (empty string) | No CalcDef |
| `module_type` | `""` (empty string) | Graph builder derives this |
| `qualified_name` | `f"{parent_eqn}__{ca.python_name}"` | e.g., `"E2EDesign__e2e_plant__power_mw"` |
| `bindings` | `list[BindingInfo]` from references | CHAIN bindings with scoped dotted source_paths |
| `unbound_params` | `[]` | All inputs come from references |
| `is_template` | `False` | Synthetic usages are always concrete |
| `owning_part_def_qn` | `None` | Not a template expansion |

### How the graph builder uses synthetic CalcUsages

After Step 6 (backtracking), the synthetic CalcUsages have `BindingResolution` entries in `binding_resolutions` just like any other CalcUsage. The graph builder creates `PipelineModule` objects with `is_computed_attribute=True` from them. The `compiled_expression` from the `ComputedAttributeData` provides the auto-implementation.

### Note on `is_computed_attribute` flag

The `CalcUsageData` dataclass does not currently have an `is_computed_attribute` field. The graph builder currently identifies computed attribute modules by matching against the `computed_attributes` list. Two options:

**Option A: Add `is_computed_attribute` flag to `CalcUsageData`.**

```python
# In CalcUsageData:
is_computed_attribute: bool = False
```

Set `synthetic_usage.is_computed_attribute = True` during construction. The graph builder checks this flag.

**Option B (current behavior): Match by QN against computed_attributes list.**

The graph builder already does this (it iterates `computed_attributes` separately). No change to CalcUsageData needed.

**Decision**: Option A is cleaner and should be used. Add the field to `CalcUsageData` with a default of `False`. This makes the synthetic usages self-describing and simplifies graph_builder logic.

---

## Updated Function Signature: `_extract_and_filter_computed_attributes`

### Current signature

```python
def _extract_and_filter_computed_attributes(
    model: Any,
    calc_usages: list[CalcUsageData],
    design_attrs: dict[Path, list[DesignAttributeData]],
) -> list[ComputedAttributeData]:
```

### Target signature

```python
def _extract_and_filter_computed_attributes(
    model: Any,
    calc_usages: list[CalcUsageData],
    design_attrs: dict[Path, list[DesignAttributeData]],
) -> tuple[list[ComputedAttributeData], list[ChannelAlias], list[CalcUsageData]]:
    """Step 4.5: Extract computed attributes, produce EXPOSE_PURE aliases,
    create FORMULA synthetic CalcUsages, and remove FORMULAs from design_attrs.

    Iterates PartDefinition and PartUsage elements from the model, calls
    extract_computed_attributes() for each, then:
    1. Removes FORMULA-classified attributes from design_attrs (prevents false entry points)
    2. Produces ChannelAlias objects from EXPOSE_PURE attributes (NOT module index entries)
    3. Creates synthetic CalcUsageData from FORMULA attributes (flow through backtracking)

    Args:
        model: Parsed SysIDE model (from extractor.model).
        calc_usages: Pipeline's calc usages (not mutated here; synthetic usages returned separately).
        design_attrs: Design attributes dict, modified in-place to remove FORMULAs.

    Returns:
        Tuple of:
        - list[ComputedAttributeData]: All extracted computed attributes (all classifications)
        - list[ChannelAlias]: EXPOSE_PURE aliases (PartUsage-only, PartDef filtered)
        - list[CalcUsageData]: Synthetic CalcUsages from FORMULA attributes
    """
```

### Target implementation

```python
def _extract_and_filter_computed_attributes(
    model: Any,
    calc_usages: list[CalcUsageData],
    design_attrs: dict[Path, list[DesignAttributeData]],
) -> tuple[list[ComputedAttributeData], list[ChannelAlias], list[CalcUsageData]]:
    from sysml_codegen.core.models import ChannelAlias
    from sysml_codegen.extraction.computed_attribute_extractor import (
        extract_computed_attributes,
    )

    all_computed_attrs: list[ComputedAttributeData] = []

    # --- Extraction: PartDefinitions (set is_on_part_definition=True) ---
    part_defs = list(SysideAdapter.elements_of_type(model, "PartDefinition"))
    for part_elem in part_defs:
        calc_usage_names = {
            m.name for m in part_elem.owned_members
            if SysideAdapter.is_instance(m, "CalculationUsage")
        }
        computed = extract_computed_attributes(None, part_elem, calc_usage_names)
        for ca in computed:
            ca.is_on_part_definition = True
        all_computed_attrs.extend(computed)

    # --- Extraction: PartUsages (is_on_part_definition defaults to False) ---
    part_usages = list(SysideAdapter.elements_of_type(model, "PartUsage"))
    for part_elem in part_usages:
        calc_usage_names = {
            m.name for m in part_elem.owned_members
            if SysideAdapter.is_instance(m, "CalculationUsage")
        }
        computed = extract_computed_attributes(None, part_elem, calc_usage_names)
        all_computed_attrs.extend(computed)

    # --- Remove FORMULA attributes from design_attrs ---
    removed_count = _remove_formula_from_design_attrs(all_computed_attrs, design_attrs)

    # --- Produce EXPOSE_PURE aliases (Change B) ---
    expose_pure_aliases: list[ChannelAlias] = []
    partdef_expose_skipped = 0

    for ca in all_computed_attrs:
        if ca.classification != ComputedAttributeClassification.EXPOSE_PURE:
            continue

        # FILTER: Skip EXPOSE_PURE on PartDefs (Spike 8: Issue 21)
        if ca.is_on_part_definition:
            partdef_expose_skipped += 1
            logger.debug(
                "Skipping PartDef EXPOSE_PURE '%s' on '%s'",
                ca.python_name, ca.owning_part_name,
            )
            continue

        # Reconstruct canonical target from references field (Spike 3)
        if len(ca.references) >= 2:
            instance_name = ca.references[1].name
            output_name = ca.references[0].name
            canonical_target = f"{instance_name}.{output_name}"
        else:
            logger.warning(
                "EXPOSE_PURE '%s' on '%s' has %d references (expected >= 2), skipping",
                ca.python_name, ca.owning_part_name, len(ca.references),
            )
            continue

        expose_pure_aliases.append(ChannelAlias(
            alias_name=ca.python_name,  # BARE -- scoped at Phase 3 registration (Spec 05)
            canonical_name=canonical_target,
            owning_part_qn=sysml_to_python_qualified_name(ca.owning_part_qualified_name),  # __ format
            source="expose_pure",
        ))

    # --- Create FORMULA synthetic CalcUsages (Change C) ---
    synthetic_usages: list[CalcUsageData] = []

    for ca in all_computed_attrs:
        if ca.classification != ComputedAttributeClassification.FORMULA:
            continue
        if ca.compilability != Compilability.FULLY_COMPILABLE:
            continue  # Only FULLY_COMPILABLE FORMULAs become pipeline modules

        parent_eqn = sysml_to_python_qualified_name(ca.owning_part_qualified_name)
        parent_short = ca.owning_part_name

        formula_bindings: list[BindingInfo] = []
        for ref in ca.references:
            if ref.name == ca.python_name:
                continue  # exclude self-reference
            formula_bindings.append(BindingInfo(
                param_name=ref.name,
                binding_type=BindingType.CHAIN,
                source_path=f"{parent_short}.{ref.name}",
            ))

        synthetic_usage = CalcUsageData(
            instance_name=ca.python_name,
            calc_def_name="",
            calc_def_qualified_name="",
            module_type="",
            qualified_name=f"{parent_eqn}__{ca.python_name}",
            bindings=formula_bindings,
            unbound_params=[],
            is_template=False,
            owning_part_def_qn=None,
        )
        synthetic_usages.append(synthetic_usage)

    # --- Log summary ---
    by_classification: dict[str, int] = {}
    for ca in all_computed_attrs:
        key = ca.classification.value
        by_classification[key] = by_classification.get(key, 0) + 1

    breakdown = ", ".join(f"{v} {k}" for k, v in sorted(by_classification.items()))
    logger.info(
        "Step 4.5: Extracted %d computed attributes (%s), "
        "removed %d FORMULA from design_attrs, "
        "produced %d EXPOSE_PURE aliases (%d PartDef skipped), "
        "created %d synthetic CalcUsages",
        len(all_computed_attrs),
        breakdown or "none",
        removed_count,
        len(expose_pure_aliases),
        partdef_expose_skipped,
        len(synthetic_usages),
    )

    return all_computed_attrs, expose_pure_aliases, synthetic_usages
```

---

## Step 4.5 Output Contract

After Step 4.5 completes, the following data is available:

| Output | Type | Description |
|--------|------|-------------|
| Computed attributes | `list[ComputedAttributeData]` | All classifications (FORMULA, EXPOSE_PURE, EXPOSE_COMPUTED, UNRESOLVABLE). LITERAL excluded. |
| EXPOSE_PURE aliases | `list[ChannelAlias]` | PartUsage-only. Appended to CHAIN aliases from Step 3.5. |
| Synthetic CalcUsages | `list[CalcUsageData]` | One per FORMULA attribute. Appended to `calc_usages`. |
| Design attributes | `dict[Path, list[DesignAttributeData]]` | Mutated in-place: FORMULAs removed. |

### Post-conditions

1. `design_attrs` has all FORMULA-classified attributes removed (prevents false entry points).
2. EXPOSE_PURE attributes on PartDefs are filtered out. Only PartUsage EXPOSE_PURE produce aliases.
3. Each EXPOSE_PURE alias has `canonical_name` reconstructed from `references[1].name` (instance) and `references[0].name` (output). The `expression_text` field is never used.
4. Each synthetic CalcUsage has CHAIN bindings with scoped dotted `source_path` values (e.g., `"e2e_plant.power_output"`). These resolve through the OutputRegistry in Step 6.
5. Synthetic CalcUsages have empty `calc_def_name` and `calc_def_qualified_name` (inline expressions, no CalcDef).

---

## Data Model Changes Summary

### `ComputedAttributeData` (data_models.py)

Add one field:

```python
@dataclass
class ComputedAttributeData:
    # ... existing fields ...
    source_file: Path = field(default_factory=lambda: Path("unknown"))
    source_line: int = 0

    # NEW: True if owning element is a PartDefinition (not PartUsage).
    # Set post-hoc by _extract_and_filter_computed_attributes() in initialization.py.
    # Used to filter PartDef EXPOSE_PURE (Spike 8: Issue 21).
    is_on_part_definition: bool = False
```

### `CalcUsageData` (usage_extractor.py)

Optionally add one field (see Decision in Change C):

```python
@dataclass
class CalcUsageData:
    # ... existing fields ...
    owning_part_def_qn: str | None = None
    raw_element: object | None = None

    # NEW: True for synthetic CalcUsages from FORMULA computed attributes.
    # Used by graph_builder to set is_computed_attribute on PipelineModule.
    is_computed_attribute: bool = False
```

---

## Caller-Side Changes in `build_pipeline_context`

The call site in `build_pipeline_context()` (initialization.py) changes to handle the new return type:

```python
# Step 4.5: Extract computed attributes, produce EXPOSE_PURE aliases,
#           create FORMULA synthetic CalcUsages
computed_attrs, expose_pure_aliases, synthetic_usages = _extract_and_filter_computed_attributes(
    extractor.model, calc_usages, design_attrs
)

# Merge aliases from Steps 3.5 and 4.5
all_channel_aliases = chain_aliases + expose_pure_aliases

# Append synthetic CalcUsages to the main list
# IMPORTANT: This must happen BEFORE Step 6 (backtracking) so the
# backtracker processes FORMULA synthetic usages alongside real usages.
calc_usages.extend(synthetic_usages)
```

### Ordering constraint

Synthetic CalcUsages MUST be appended to `calc_usages` BEFORE Step 6 (backtracking). The backtracker iterates `calc_usages` and resolves bindings for every usage. If synthetic usages are not in the list, their bindings are never resolved and the graph builder cannot wire their inputs.

---

## Interaction with OutputRegistry (Step 5, separate spec)

The EXPOSE_PURE aliases produced here are registered in Phase 3 of the OutputRegistry. The OutputRegistry spec (separate) defines how these aliases are scoped:

```python
# Phase 3 registration (OutputRegistry spec):
for alias in expose_pure_aliases:
    canonical_channel = registry.resolve(alias.canonical_name)
    if canonical_channel:
        owning_part_short = alias.owning_part_qn.split("__")[-1]
        scoped_alias = f"{owning_part_short}.{alias.alias_name}"
        registry.register_alias(scoped_alias, canonical_channel)
```

This spec does NOT define the OutputRegistry registration logic. It only defines the production of `ChannelAlias` objects with the correct `alias_name`, `canonical_name`, `owning_part_qn`, and `source` fields.

---

## Test Plan

### Unit tests for EXPOSE_PURE alias production

1. **PartUsage EXPOSE_PURE produces alias**: Given a `ComputedAttributeData` with `classification=EXPOSE_PURE`, `is_on_part_definition=False`, and `references=[ExpressionRef(name="total_cost"), ExpressionRef(name="component_cost")]`, verify a `ChannelAlias` is produced with `alias_name="total_capex"` (from `python_name`), `canonical_name="component_cost.total_cost"`, and `source="expose_pure"`.

2. **PartDef EXPOSE_PURE filtered**: Given a `ComputedAttributeData` with `classification=EXPOSE_PURE` and `is_on_part_definition=True`, verify no alias is produced and a debug log is emitted.

3. **Insufficient references skipped**: Given a `ComputedAttributeData` with `classification=EXPOSE_PURE` and `references=[ExpressionRef(name="x")]` (only 1 ref), verify a warning is logged and no alias is produced.

4. **expression_text never used**: Verify that the `expression_text` field is not accessed during alias construction (the test can mock it to a known-bad value like `".(garbage)"` and verify the alias is still correct).

### Unit tests for FORMULA synthetic CalcUsageData

1. **Basic construction**: Given a FORMULA `ComputedAttributeData` with `owning_part_qualified_name="E2EDesign::e2e_plant"`, `python_name="power_mw"`, and `references=[ExpressionRef(name="power_output"), ExpressionRef(name="power_mw")]`, verify synthetic usage has:
   - `qualified_name="E2EDesign__e2e_plant__power_mw"`
   - `instance_name="power_mw"`
   - `calc_def_name=""`
   - One binding: `BindingInfo(param_name="power_output", binding_type=BindingType.CHAIN, source_path="e2e_plant.power_output")`
   - Self-reference `power_mw` excluded from bindings.

2. **Empty references**: Given a FORMULA with no references (constant expression), verify synthetic usage has empty bindings list and empty unbound_params.

3. **Non-FORMULA skipped**: Verify that EXPOSE_PURE, EXPOSE_COMPUTED, LITERAL, and UNRESOLVABLE attributes do not produce synthetic CalcUsages.

### Unit tests for `is_on_part_definition` tracking

1. **PartDef elements flagged**: Given a PartDefinition element, verify all extracted `ComputedAttributeData` have `is_on_part_definition=True`.

2. **PartUsage elements not flagged**: Given a PartUsage element, verify all extracted `ComputedAttributeData` have `is_on_part_definition=False`.

### Integration tests

1. **Return type**: Verify `_extract_and_filter_computed_attributes` returns a 3-tuple of `(list[ComputedAttributeData], list[ChannelAlias], list[CalcUsageData])`.

2. **Synthetic usages appended before backtracking**: Verify that `calc_usages` contains synthetic entries before `DependencyBacktracker` is constructed.

3. **Bug 2 regression test**: For the e2e_attr_expr model, verify that `financial.total_capex` resolves to MODULE_OUTPUT (not ENTRY_POINT) when the full pipeline runs with the OutputRegistry.

4. **FORMULA removal from design_attrs**: Verify that FORMULA-classified attributes are removed from `design_attrs` (existing behavior preserved).
