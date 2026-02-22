# 16 -- Computed Attributes: FORMULA, EXPOSE, and Classification

## What This Module Does

Some PartDef/PartUsage attributes have inline expressions rather than literal
values. The computed attribute extractor (`extraction/computed_attribute_extractor.py`)
discovers these, classifies each by how it should be handled in the [pipeline](00-pipeline-overview.md), and
compiles FORMULA patterns into Python code via the [expression compiler](14-expression-compiler.md).

## Requirements

| ID | Requirement | Verified by |
|----|-------------|-------------|
| REQ-CA-01 | Classification SHALL produce exactly one of 5 values per attribute expression | `_classify_attribute_expression()` returns single `ComputedAttributeClassification` enum |
| REQ-CA-02 | FORMULA attributes SHALL compile to Python via `build_expression_ast()` + `compile_expression()` | Compilation path in extractor; compilability set to `FULLY_COMPILABLE` on success |
| REQ-CA-03 | EXPOSE_PURE SHALL produce `ChannelAlias` only for PartUsage-level (not PartDef) | `not is_part_def` guard before alias creation |
| REQ-CA-04 | LITERAL attributes SHALL be excluded from computed attributes | Returns `LITERAL`; excluded by caller before adding to `ComputedAttributeData` list |
| REQ-CA-05 | UNRESOLVABLE attributes SHALL be logged but not generate modules or aliases | Included in list for reporting; no module or alias emitted |
| REQ-CA-06 | `AttributeResolutionKind` SHALL classify each FORMULA input as FORMULA, EXPOSE_ALIAS, or LITERAL | 3-value enum in `resolution/graph_builder.py`; `_build_attribute_resolution_map()` assigns one per input |
| REQ-CA-07 | FORMULA self-reference SHALL be excluded from `input_names` | `input_names = siblings - {self_name}` prevents circular dependency |

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

`ComputedAttributeClassification` (in `extraction/data_models.py`, see [data models](09-data-models.md)) classifies
each attribute expression by analyzing its feature references (REQ-CA-01):

### FORMULA

All references are sibling attributes on the same PartDef.

```sysml
attribute dc_capacity = panel_count * panel_wattage;
```

**Pipeline effect**: generates a synthetic [`PipelineModule`](09-data-models.md) with
`is_computed_attribute=True` (REQ-CA-02). The expression compiles to Python via
`build_expression_ast()` + `compile_expression()` ([expression compiler](14-expression-compiler.md)). Inputs wire to sibling
attribute channels or [entry points](06-entry-point-classifier.md).

### EXPOSE_PURE

A single `FeatureChainExpression` to a calc usage's output. No arithmetic.

```sysml
attribute p_alpha_out = alpha_split.p_alpha;
```

**Pipeline effect**: produces a `ChannelAlias` (not a module). The alias maps
`PartName.p_alpha_out` to the output channel of `alpha_split.p_alpha` in the
[OutputRegistry](10-output-registry.md) (Phase 3). Downstream bindings to `p_alpha_out` resolve
transparently through the alias. See [naming conventions](15-naming-conventions.md) for Phase 3 key format.

Filter: only PartUsage-level EXPOSE_PURE attributes produce aliases (REQ-CA-03).
PartDefinition-level ones are skipped (`is_on_part_definition` guard).

### EXPOSE_COMPUTED

A `FeatureChainExpression` mixed with arithmetic (e.g., `cost_model.total * 1.1`).

**Pipeline effect**: deferred. Currently no module or alias is generated.
Future work: decompose into a FORMULA module that reads the exposed output.

### LITERAL

Pure constant, no feature references (e.g., `attribute pi = 3.14159`).

**Pipeline effect**: excluded from computed attributes entirely (REQ-CA-04). Stays in
the `design_attributes` path as a normal `DesignAttributeData`.

### UNRESOLVABLE

Contains references that cannot be resolved to known siblings or calc outputs.

**Pipeline effect**: included in the `ComputedAttributeData` list (for reporting)
but does not generate a module or alias (REQ-CA-05). Logged as a warning.

**Note**: UNRESOLVABLE is likely **unreachable for well-formed SysML**. SysIDE
always resolves attribute QNs (even inherited ones resolve to the supertype's
namespace), so the empty-QN fallback path (Step 2d) is never triggered. This
classification may only be reachable through SysIDE parser bugs, partially valid
SysML, or synthetic test data. Treat as a defensive fallback, not a primary
classification path. See Known Issues below.

---

## Classification Algorithm

`_classify_attribute_expression()` uses qualified-name analysis:

```
Step 1: No refs at all                                → LITERAL
Step 2: For each ref, classify by QN:
  2a: ref.name in calc_usage_names                    → skip (traversal artifact)
  2b: ref.qualified_name starts with owning part QN   → sibling_ref
      ⚠ KNOWN BUG: fails for inherited attrs (see Known Issues below)
  2c: ref.qualified_name is non-empty, other namespace → calc_ref
  2d: empty QN, fallback to name matching             → sibling or unresolvable
      ⚠ Likely unreachable for valid SysML (see UNRESOLVABLE note above)
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
   circular self-reference — REQ-CA-07).
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

`AttributeResolutionKind` (in `resolution/graph_builder.py`) — REQ-CA-06:

| Kind | When | Wiring |
|------|------|--------|
| `FORMULA` | Another FORMULA attr on the same part | Wire to that FORMULA [module's](05-module-factory.md) output channel |
| `EXPOSE_ALIAS` | An EXPOSE_PURE attr | Wire to the upstream calc output channel via [alias](10-output-registry.md) |
| `LITERAL` | Attr is a design attribute with literal default | [Entry point](06-entry-point-classifier.md) |

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
    owning_part_qn="SolarBatteryLibrary__Solar_Array",
    source="expose_pure",
)
```

---

## FORMULA-to-FORMULA Limitation

**REQ-CA-08**: FORMULA compilation SHALL NOT resolve sibling FORMULA outputs
as inputs. FORMULA attributes cannot reference other FORMULA outputs on the
same PartDef. The compiler receives `output_names=set()` (only inputs, not
sibling outputs), so a cross-FORMULA reference like `dc_capacity` in
`annual_output = dc_capacity * 8760` classifies `dc_capacity` as UNSUPPORTED.
Workaround: promote the dependency to a separate CalcDef or use EXPOSE_PURE.

## Known Issues

### Inherited Attribute Misclassification

**Status**: Confirmed bug. 5 of 6 test patterns affected. Fix deferred to a
future enhancement.

**Root cause**: When a PartDef inherits from a supertype via `:>` (e.g.,
`part def 'Derived' :> 'Base'`), SysIDE resolves inherited attribute QNs to
the **supertype's namespace**:

```
owning_part_qn:      "Library::'Derived Component'"
inherited attr QN:   "Library::'Base Component'::base_rate"   ← supertype prefix
expected (but wrong): "Library::'Derived Component'::base_rate"
```

Step 2b checks `qn.startswith(owning_part_qn + "::")`, which fails for
inherited attrs. They fall through to Step 2c as `calc_ref` (different namespace
= external CalcUsage output), pushing classification from FORMULA to
**EXPOSE_COMPUTED**.

**Additional factor**: `sibling_attr_names` is built from `owned_members`, which
per SysML v2 semantics only includes locally-declared attributes — inherited
attributes are excluded. So even Step 2d's fallback name check can't rescue
the classification.

**Impact**: Computed attributes referencing inherited attrs silently produce
**no pipeline module** and **no compiled expression**. They appear in
`computed_attributes` but EXPOSE_COMPUTED is currently unhandled,
so they are silent no-ops in the pipeline.

**Fix scope**: The classifier needs to walk the supertype chain when checking
QN prefixes. Instead of checking only the immediate `owning_part_qn`, check if
the QN starts with ANY ancestor PartDef's QN. This requires:

1. **Extraction enrichment**: Extract supertype chain information from
   SysIDE during `_extract_part_definitions()`.
2. **Classifier fix**: Accept `ancestor_part_qns: set[str]` parameter
   and augment the Step 2b prefix check.

**Fixture coverage**: `tests/fixtures/unresolvable_attr_probe/` exercises this
pattern with 5 xfailed tests in
`test_computed_attributes.py::TestInheritedAttrClassification`.

### UNRESOLVABLE Likely Dead Code

**Status**: Documented. No fix needed — defensive retention recommended.

SysIDE always resolves attribute QNs, even for inherited attributes (to the
supertype's namespace). The empty-QN path (Step 2d → UNRESOLVABLE) was not
triggered by any of the 8 fixture models tested, including the inheritance-
specific `unresolvable_attr_probe`. The UNRESOLVABLE classification may only
be reachable through SysIDE parser bugs, partially valid SysML that SysIDE
tolerates, or synthetic `ExpressionRef` data.

**Decision**: Retain the code path as a defensive fallback with documentation.
Do not invest in testing unreachable paths.

---

## Data Models & Source Files

Models: `ComputedAttributeClassification` (enum), `ComputedAttributeData` (`extraction/data_models.py`), `ChannelAlias` (`core/models.py`), `AttributeResolutionKind`/`AttributeResolution` (`resolution/graph_builder.py`).
Source: `extraction/computed_attribute_extractor.py`, `orchestration/pipeline_builder.py`, `resolution/graph_builder.py`.

## Related Documents

- **Upstream**: [01-extraction](01-extraction.md) (raw attribute data), [00-pipeline-overview](00-pipeline-overview.md) (Step 5)
- **Resolution**: [05-module-factory](05-module-factory.md) (FORMULA as module type), [06-entry-point-classifier](06-entry-point-classifier.md) (LITERAL→EP)
- **Registry**: [10-output-registry](10-output-registry.md) (Phase 3 EXPOSE_PURE aliases), [15-naming-conventions](15-naming-conventions.md) (key formats)
- **Expression**: [14-expression-compiler](14-expression-compiler.md) (AST+compile), [19-ast-dispatch-invariant](19-ast-dispatch-invariant.md) (FCE/OE ordering)
- **Generation**: [08-generation](08-generation.md) (stencils), [22-output-schema-rules](22-output-schema-rules.md), [23-smart-regen-preservation](23-smart-regen-preservation.md)
- **Data models**: [09-data-models](09-data-models.md) — `PipelineModule`, `ModuleInput`, `ModuleOutput` fields
