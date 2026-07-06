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
| REQ-CA-03 | PartUsage-level EXPOSE_PURE SHALL produce a Phase-3 `ChannelAlias`; PartDef-level EXPOSE_PURE (shape A, `total_cost = cost_calc.cost` on a `part def`) SHALL be expanded per design instance into the structured `_scoped_alias` namespace by `_register_partdef_expose_scoped_aliases` (Item 10 #4), not silently skipped | `test_wi014_toy.py::test_wi014_toy_shape_a_resolves_offline_via_scoped_alias` — `("demo_plant","total_cost")` maps to the `demo_plant__…__cost_calc__cost` channel |
| REQ-CA-10 | A well-formed multi-hop feature chain (part-typed waypoints, `reference_chain` ≥ 2 segments) SHALL be tagged `EXPOSE_CHAIN_TENTATIVE` at the leaf (INV-E gate), then finalized in the registry confirm pass (Phase 3b) — resolved to a canonical channel → `EXPOSE_PURE` + alias, else reverted to `FORMULA`. No downstream reader may observe a surviving tentative (INV-F) | Leaf tag: `test_computed_attribute_extraction.py::test_multihop_chain_tagged_tentative`; confirm-pass flips: `test_ife_plant.py::test_cross_part_inputs_pinned_or_baseline` (direct-calc-output terminal) and `test_computed_attributes_e2e.py::test_catf_mfe_wired_after_item10` (alias-terminal hop) |
| REQ-CA-04 | LITERAL attributes SHALL be excluded from computed attributes | Returns `LITERAL`; excluded by caller before adding to `ComputedAttributeData` list |
| REQ-CA-05 | UNRESOLVABLE attributes SHALL be logged but not generate modules or aliases | Included in list for reporting; no module or alias emitted |
| REQ-CA-06 | `AttributeResolutionKind` SHALL classify each FORMULA input as FORMULA, EXPOSE_ALIAS, or LITERAL | 3-value enum in `resolution/graph_builder.py`; `_build_attribute_resolution_map()` assigns one per input |
| REQ-CA-07 | FORMULA self-reference SHALL be excluded from `input_names` | `input_names = siblings - {self_name}` prevents circular dependency |
| REQ-CA-09 | Shape-A resolution (part-def EXPOSE): the wi014_toy `demo_plant.total_cost` consumer SHALL resolve via `_scoped_alias` to the `cost_calc__cost` channel (the Item-1 malformed-refs deferral, discharged by Item 10 #4/#1) | `test_wi014_toy.py` |
| REQ-CA-11 | Shape-A EXPOSE_PURE (part def) in the attribute resolution map SHALL route by `is_on_part_definition` to a LITERAL fallback (not the refs-parser) and consult `_scoped_alias` to decide the warning: a registered leaf is silent (the name resolves via Item 10 and surfaces via Item 11), an unregistered one warns naming the real cause — retiring the Item-1 malformed-refs warning (`_resolve_expose_pure`, `resolution/graph_builder.py`) for the resolvable case | `test_wi014_toy.py` |

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

## The Classifications: 5 Stable + 1 Transient

`ComputedAttributeClassification` (in `extraction/data_models.py`, see [data models](09-data-models.md)) classifies
each attribute expression by analyzing its feature references (REQ-CA-01). Five
values are stable — they are what downstream readers observe. The enum carries a
sixth, transient value, `EXPOSE_CHAIN_TENTATIVE` (Item 10): it exists only between
the extraction-time leaf tag and the Phase-3b confirm pass, which finalizes it to
`EXPOSE_PURE` or reverts it to `FORMULA`. No reader ever observes it (INV-F). See
[Multi-Hop EXPOSE](#multi-hop-expose-tentative-leaf-tag--confirm-pass-req-ca-10).

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

Filter: PartUsage-level EXPOSE_PURE attributes produce a Phase-3 `ChannelAlias`.
PartDef-level ones (shape A) are handled separately — expanded per design instance
into the `_scoped_alias` namespace (REQ-CA-03, see [Part-Def EXPOSE Scoped Aliases](#part-def-expose-scoped-aliases-shape-a-req-ca-03)),
not dropped.

### EXPOSE_COMPUTED

A `FeatureChainExpression` mixed with arithmetic (e.g., `cost_model.total * 1.1`).

**Pipeline effect**: deferred. Currently no module or alias is generated.
Future work: decompose into a FORMULA module that reads the exposed output.

### EXPOSE_CHAIN_TENTATIVE (transient)

A pure `FeatureChainExpression` whose `reference_chain` has ≥ 2 segments rooted at
a part-typed waypoint (e.g., `tf_coil.volume_calc.volume`) — a *candidate* multi-hop
EXPOSE.

**Pipeline effect**: none directly. The Phase-3b confirm pass finalizes it to
EXPOSE_PURE (registering the transitive channel) or reverts it to FORMULA before
any reader runs. See
[Multi-Hop EXPOSE](#multi-hop-expose-tentative-leaf-tag--confirm-pass-req-ca-10).

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
  - no calc_refs (only sibling refs):
      well-formed multi-hop chain (INV-E gate,
      _is_wellformed_multihop_chain)                  → EXPOSE_CHAIN_TENTATIVE
      otherwise                                       → FORMULA
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

## Multi-Hop EXPOSE: Tentative Leaf Tag + Confirm Pass (REQ-CA-10)

A cross-part chain like `magnet_volume_total = tf_coil.volume_calc.volume` names a
calc output *through* a nested part. The single-hop EXPOSE_PURE path cannot classify
it: the leaf extractor has instance names, not calc-def output sets, and catf_mfe's
alias terminal (`tf_coil.volume` is itself an EXPOSE alias) is undecidable without the
whole registry. So the decision is split across two layers.

**Leaf tags a tentative (INV-E gate).** `_classify_attribute_expression`
(`extraction/computed_attribute_extractor.py`) returns a sixth, transient enum value
`EXPOSE_CHAIN_TENTATIVE` when the root is a pure `FeatureChainExpression` AND
`reference_chain` (the full dotted segments captured at extraction by
`extract_feature_chain_segments`, `extraction/expression_utils.py`) has ≥ 2 segments
rooted at a part-typed waypoint (`reference_chain[0]` is not a calc-usage short name).
It does **not** decide EXPOSE-ness. Over-tagging is safe — an unresolvable tentative
reverts (INV-D).

**Confirm pass finalizes (Phase 3b).** `build_output_registry`
(`orchestration/output_registry_builder.py`) walks each tentative's `reference_chain`
against the registry via `_resolve_reference_chain` (the transitive N-segment walk,
with a `visited` cycle guard, the recursive analog of the aggregation input walker).
It runs after Phase 3 single-hop aliases, before Phase 4. Two outcomes, mutating the
shared CA in place:

- **Resolves** to a canonical channel (direct calc-output for ife_plant; one alias hop
  further for catf_mfe) → register the cross-part alias, set `EXPOSE_PURE`.
- **Does not resolve** → revert to `FORMULA` — byte-identical to pre-Item-10 behavior.

**No tentative escapes (INV-F).** The confirm loop raises if any tentative survives,
and the three post-confirm readers in `resolution/graph_builder.py` (module build,
aggregation alias map, attribute resolution map) each carry an `elif tentative: raise`.

**Offline parity (D-C).** On snapshot reload a multi-hop CA arrives already
`EXPOSE_PURE` (M6 serializes the post-confirm state), so the confirm walk would skip
it and Phase 3's naive 2-segment path would resolve the ambiguous terminal through the
first-wins-corrupted flat `_alias` (the wrong channel — a lying sim). Before Phase 3,
`build_output_registry` reconstructs the pre-confirm tentative state for exactly the
multi-hop candidates (an `EXPOSE_PURE` CA whose `reference_chain` is a part-rooted chain
of ≥ 2 segments), so the confirm pass reproduces the live registration order on both
paths. Live CAs are still tentative here → no-op on the live path.

## Part-Def EXPOSE Scoped Aliases (Shape A) (REQ-CA-03)

A derived `total_cost = cost_calc.cost` on a `part def` (not a usage) has no instances
at extraction, so it cannot register a scoped alias directly. Item 10 #4 expands it per
design instance. `_register_partdef_expose_scoped_aliases`
(`orchestration/pipeline_builder.py`, Step 5.55) iterates the EXPOSE_PURE CAs carrying
`is_on_part_definition`, resolves the calc-output channel per instance path via
`find_instance_paths_for_partdef` + `scoped_lookup`, and writes
`(instance_path, python_name) → channel` into the structured `_scoped_alias` namespace
on the [OutputRegistry](10-output-registry.md). The consumer-side reader is
`dependency_backtracker._resolve_chain_dispatch` Step 1c (REQ-BT-11, see
[11-analysis-backtracker](11-analysis-backtracker.md)). The same helper runs on the
offline path from `snapshot/graph_rebuild.py`, so shape A resolves without a license.

The extraction-time `not is_part_def` guard on the ChannelAlias is deliberately kept —
dropping it would emit a template alias Phase 3 cannot register (warning noise). The CA
itself carries `is_on_part_definition`, so the helper iterates `computed_attrs` directly
for the same D7 outcome.

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

### Shape-A EXPOSE_PURE reroute + warning retirement (REQ-CA-11)

`_build_attribute_resolution_map` splits the EXPOSE_PURE branch on
`ca.is_on_part_definition`:

- **Part usage (shape B)** — unchanged. It still calls `_resolve_expose_pure`, so a
  genuinely unresolvable shape-B EXPOSE still warns from `_resolve_expose_pure`
  (`resolution/graph_builder.py`).
- **Part def (shape A)** — does **not** call the refs parser. On a part def the
  calc-usage instance names are absent from `calc_usage_names`, so `_resolve_expose_pure`
  could not split the refs and would fire its malformed-refs warning — the
  Item-1 interim warning. Item 10 resolves shape A per instance through the
  `_scoped_alias` namespace instead, and this per-def map is structurally
  instance-blind, so shape A takes a LITERAL fallback (identical to the old
  post-warning behavior — no in-repo FORMULA consumes a shape-A exposed name). The map
  then consults `_scoped_alias` only to decide the warning: a registered leaf means the
  name resolved (Item 10) and now surfaces (Item 11) → **silent**; an unregistered leaf
  warns naming the real cause, not "Item 10/11."

This retires the Item-1 malformed-refs warning for the resolvable case
(`test_wi014_toy.py`, previously pinning the warning, now asserts silence + the
surfaced name).

### EXPOSE_PURE → surfaced name (Item 11 / SC-7)

The value already flows on its canonical channel; Item 10 computed the name→channel
mapping for both shapes and stored it with provenance. Item 11 reads those two sources
(`_scoped_alias` for shape A, `expose_pure` `ChannelAlias` objects for shape B) at the
end of graph construction and normalizes them into
[`ComputationGraph.output_aliases`](09-data-models.md) (a list of `OutputAlias`), then
renders each as the output filename on its channel's exit line in the pipeline YAML
([doc 21](21-pipeline-yaml-generation.md), REQ-PY-08). So `total_cost` (shape A,
`wi014_toy`) and `scale_result` / `half_vol` / `quarter_vol` (shape B,
`attr_expr_probe`) now reach generated output as named captures. EXPOSE_COMPUTED is
**not** surfaced — it stays rejected per [modeling-assumptions §3](../modeling-assumptions.md),
and its warning stays.

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
