# 16 -- Computed Attributes: FORMULA, EXPOSE, and Classification

## What This Module Does

Some PartDef/PartUsage attributes have inline expressions rather than literal
values. The computed attribute extractor (`extraction/computed_attribute_extractor.py`)
discovers these, classifies each by how it should be handled in the pipeline, and
compiles FORMULA patterns into Python code.

```sysml
part def Solar_Array {
    attribute panel_count : Integer = 20;
    attribute panel_wattage : Real = 400.0;
    attribute dc_capacity : Real = panel_count * panel_wattage;  // <-- FORMULA
    attribute total_capex : Real = cost_model.total_cost;        // <-- EXPOSE_PURE
}
```

`dc_capacity` uses only sibling attributes -- it becomes a synthetic pipeline
module. `total_capex` delegates to a calc usage's output -- it becomes a channel
alias, not a module.

Source: `src/sysml_codegen/extraction/computed_attribute_extractor.py`

---

## The 5 Classifications

`ComputedAttributeClassification` (in `extraction/data_models.py`) classifies
each attribute expression by analyzing its feature references:

### FORMULA

All references are sibling attributes on the same PartDef.

```sysml
attribute dc_capacity = panel_count * panel_wattage;
```

**Pipeline effect**: generates a synthetic `PipelineModule` with
`is_computed_attribute=True`. The expression compiles to Python via
`build_expression_ast()` + `compile_expression()`. Inputs wire to sibling
attribute channels or entry points.

### EXPOSE_PURE

A single `FeatureChainExpression` to a calc usage's output. No arithmetic.

```sysml
attribute p_alpha_out = alpha_split.p_alpha;
```

**Pipeline effect**: produces a `ChannelAlias` (not a module). The alias maps
`PartName.p_alpha_out` to the output channel of `alpha_split.p_alpha` in the
OutputRegistry (Phase 3). Downstream bindings to `p_alpha_out` resolve
transparently through the alias.

Filter: only PartUsage-level EXPOSE_PURE attributes produce aliases.
PartDefinition-level ones are skipped (`is_on_part_definition` guard).

### EXPOSE_COMPUTED

A `FeatureChainExpression` mixed with arithmetic (e.g., `cost_model.total * 1.1`).

**Pipeline effect**: deferred. Currently no module or alias is generated.
Future work: decompose into a FORMULA module that reads the exposed output.

### LITERAL

Pure constant, no feature references (e.g., `attribute pi = 3.14159`).

**Pipeline effect**: excluded from computed attributes entirely. Stays in
the `design_attributes` path as a normal `DesignAttributeData`.

### UNRESOLVABLE

Contains references that cannot be resolved to known siblings or calc outputs.

**Pipeline effect**: included in the `ComputedAttributeData` list (for reporting)
but does not generate a module or alias. Logged as a warning.

---

## Classification Algorithm

`_classify_attribute_expression()` uses qualified-name analysis:

```
Step 1: No refs at all                                → LITERAL
Step 2: For each ref, classify by QN:
  2a: ref.name in calc_usage_names                    → skip (traversal artifact)
  2b: ref.qualified_name starts with owning part QN   → sibling_ref
  2c: ref.qualified_name is non-empty, other namespace → calc_ref
  2d: empty QN, fallback to name matching             → sibling or unresolvable
Step 3: Decision:
  - any unresolvable_refs                             → UNRESOLVABLE
  - no calc_refs (only sibling refs)                  → FORMULA
  - calc_refs + pure FeatureChainExpression + no siblings → EXPOSE_PURE
  - calc_refs + anything else                         → EXPOSE_COMPUTED
```

---

## FORMULA Compilation

For FORMULA attributes, the extractor immediately compiles the expression:

1. Build `input_names` from sibling attributes (excluding self to prevent
   circular self-reference).
2. Call `build_expression_ast(expr, input_names, output_names=set())`.
3. Call `compile_expression(ast_ir)` to produce Python string.
4. If compilation succeeds: `compilability = FULLY_COMPILABLE`.
5. If `CompilationError`: `compilability = MANUAL_REQUIRED`, `compiled_expression = None`.

Result stored on `ComputedAttributeData.compiled_expression` (e.g.,
`"(inputs.panel_count * inputs.panel_wattage)"`).

---

## EXPOSE_PURE Alias Production

For EXPOSE_PURE attributes on PartUsages (not PartDefs):

1. Separate refs into instance ref (name in `calc_usage_names`) and output ref.
2. Produce `ChannelAlias(alias_name=python_name, canonical_name="{instance}.{output}",
   source="expose_pure")`.
3. At Phase 3 of OutputRegistry construction, the alias is scoped to the owning
   part and registered.

---

## AttributeResolution Map (graph_builder.py)

When building FORMULA modules, the graph builder needs to know how each input
reference in the compiled expression should be wired. This is handled by
`_build_attribute_resolution_map()` which produces:

```python
attr_resolution_map: dict[str, dict[str, AttributeResolution]]
# owning_part_name -> {attr_name -> AttributeResolution}
```

`AttributeResolutionKind` (in `graph_builder.py`, line 526):

| Kind | When | Wiring |
|------|------|--------|
| `FORMULA` | Another FORMULA attr on the same part | Wire to that FORMULA module's output channel |
| `EXPOSE_ALIAS` | An EXPOSE_PURE attr | Wire to the upstream calc output channel via alias |
| `LITERAL` | Attr is a design attribute with literal default | Entry point |

```python
@dataclass
class AttributeResolution:
    kind: AttributeResolutionKind
    channel_name: str | None = None  # For FORMULA and EXPOSE_ALIAS
```

---

## Concrete Example: Solar_Array

```sysml
part def Solar_Array {
    attribute panel_count : Integer = 20;
    attribute panel_wattage : Real = 400.0;
    attribute dc_capacity : Real = panel_count * panel_wattage;  // FORMULA
    attribute total_capex : Real = cost_model.total_cost;        // EXPOSE_PURE
    attribute adjusted_cost : Real = cost_model.total_cost * 1.1; // EXPOSE_COMPUTED
}
```

**Classification results:**

| Attribute | Refs | Classification | Produces |
|-----------|------|----------------|----------|
| `panel_count` | `[]` (literal) | LITERAL | Excluded (stays as design attr) |
| `panel_wattage` | `[]` (literal) | LITERAL | Excluded |
| `dc_capacity` | `[panel_count, panel_wattage]` (siblings) | FORMULA | PipelineModule + OutputRegistry Phase 1c |
| `total_capex` | `[cost_model, total_cost]` (calc refs, FCE) | EXPOSE_PURE | ChannelAlias (Phase 3) |
| `adjusted_cost` | `[cost_model, total_cost]` (calc refs + arithmetic) | EXPOSE_COMPUTED | Nothing (deferred) |

**FORMULA module for dc_capacity:**

```python
PipelineModule(
    name="solarbatterylibrary__solar_array__dc_capacity",
    module_type="solarbatterylibrary.solar_array.dc_capacityModule",
    inputs=[
        ModuleInput("panel_count", source=entry_point("...solar_array__panel_count")),
        ModuleInput("panel_wattage", source=entry_point("...solar_array__panel_wattage")),
    ],
    outputs=[ModuleOutput("root", channel="...solar_array__dc_capacity__dc_capacity")],
    is_computed_attribute=True,
    compilability=FULLY_COMPILABLE,
    compiled_expression="(inputs.panel_count * inputs.panel_wattage)",
)
```

**EXPOSE_PURE alias for total_capex:**

```python
ChannelAlias(
    alias_name="total_capex",
    canonical_name="cost_model.total_cost",
    owning_part_qn="SolarBatteryLibrary::Solar_Array",
    source="expose_pure",
)
```

---

## Data Models

| Model | File | Role |
|-------|------|------|
| `ComputedAttributeClassification` | `extraction/data_models.py` | 5-value enum |
| `ComputedAttributeData` | `extraction/data_models.py` | Per-attribute extraction result |
| `ChannelAlias` | `core/models.py` | EXPOSE_PURE alias for OutputRegistry |
| `AttributeResolutionKind` | `resolution/graph_builder.py` | FORMULA input wiring classification |
| `AttributeResolution` | `resolution/graph_builder.py` | Per-input wiring decision for FORMULA modules |

## Key Source Files

| File | Function |
|------|----------|
| `extraction/computed_attribute_extractor.py` | `extract_computed_attributes()`, `_classify_attribute_expression()` |
| `generation/initialization.py` | `_extract_and_filter_computed_attributes()` (Step 4.5 orchestration) |
| `resolution/graph_builder.py` | `_build_attribute_resolution_map()`, `_build_computed_attr_module()` |
