---
date: 2026-02-10T04:03:46+00:00
researcher: Claude
topic: "Root cause analysis of 4 codegen bugs found during E2E attribute expression validation"
tags: [research, codegen, bugs, backtracker, graph-builder, computed-attributes]
status: complete
last_updated: 2026-02-10
---

# Research: E2E Codegen Bug Root Cause Analysis

**Date**: 2026-02-10T04:03:46+00:00
**Researcher**: Claude
**Research Type**: Codebase / Bug Analysis

## Research Question

During E2E validation of Phases 1+2 (EXPR-CODEGEN + ATTR-EXPR) in the fusion-tea project, 4 codegen bugs were discovered requiring manual workarounds. What are the root causes, and what are the right and clean design fixes?

The bugs (from the fusion-tea plan.md):
1. **FORMULA entry point omission** -- FORMULA module inputs not in DesignParams schema/JSON
2. **FORMULA/EXPOSE backtracker wiring** -- CalcUsage bindings to FORMULA/EXPOSE attrs become ENTRY_POINT instead of MODULE_OUTPUT
3. **FORMULA module input type mismatch** -- FORMULA modules use `Float` (RootModel[float]) for inputs, CalcUsage modules use `float`
4. **ExitPoint float write handler** -- Multi-output CalcUsage `float` channels can't be serialized by ExitPoint

## Summary

- **Bugs 1 and 2 share a common architectural root cause**: the backtracker was designed with CalcUsage-only awareness and doesn't fully account for FORMULA computed attributes' participation in the dependency graph. The backtracker index key format doesn't match binding source_path format (Bug 2), and FORMULA module input dependencies are never registered as entry points (Bug 1).
- **Bug 3 is a simple hardcoded value error** in `cli/__init__.py` where the FORMULA module wrapper generation path bypasses the type mapping that CalcUsage modules use, hardcoding `"Float"` instead of `"float"`.
- **Bug 4 is a design gap in exit_point handling** where multi-output module channels carry bare `float` values but the exit_point serializer only handles Pydantic models.
- **All 4 bugs are fixable with well-scoped changes** to existing code. No architectural redesign is needed. Bugs 1+2 require backtracker + graph builder coordination changes. Bug 3 is a one-line fix. Bug 4 requires a design decision about where to wrap primitives.

## Detailed Findings

### Bug 1: FORMULA Entry Point Omission

**Symptom**: FORMULA synthetic modules reference design-level params (e.g., `design_params.E2EAttrExprDesign__e2e_plant__quantity`) but these are NOT included in the DesignParams schema or `design_params.json`. Only CalcUsage-scoped params are generated.

**Manual workaround applied**: Added 7 design-level params to schema + JSON by hand.

#### Root Cause: Sequencing gap in `build_computation_graph()`

The `build_computation_graph()` function in `resolution/graph_builder.py` executes in this order:

```
Step 4:   entry_points = _classify_entry_points(backtracking_result.entry_points, ...)
Step 5:   param_groups = _group_entry_points_via_deriver(entry_points, backtracking_result, ...)
Step 6:   Build CalcUsage modules
Step 6.5: Build FORMULA computed attr modules   <-- CREATES new entry points
Step 7:   Topological sort
Step 8:   Validation
Return:   ComputationGraph(entry_point_groups=param_groups, ...)
```

At Step 6.5, `_build_computed_attr_module()` (graph_builder.py:623-740) creates new `EntryPoint` objects for FORMULA module inputs that are literal sibling attributes (line 702):

```python
entry_points[ep_qname] = EntryPoint(
    qualified_name=ep_qname,
    simple_name=input_name,
    entry_type=EntryPointType.DESIGN_ATTRIBUTE,
    default_value=default_value,
    param_group=param_group,
)
```

These entry points are correctly created and the module inputs are correctly wired to them. **But `param_groups` was already frozen at Step 5.** The new entry points are never added to any `ParameterGroup`.

The reason `param_groups` doesn't include them: `_group_entry_points_via_deriver()` (graph_builder.py:123) calls `derive_groups_filtered()` which filters to only entry points present in `backtracking_result.entry_points`. But `backtracking_result.entry_points` was computed by the backtracker at Step 6 of `build_pipeline_context()`, which only traces CalcUsage dependencies. The backtracker never traces FORMULA module input dependencies because FORMULA modules are synthetic -- they don't exist in the CalcUsage list.

When the backtracker encounters a computed attribute match (dependency_backtracker.py:413):
```python
continue  # No recursive tracing -- graph builder creates the module
```

It correctly resolves the CalcUsage binding as MODULE_OUTPUT but does NOT recursively trace what the FORMULA module itself needs as inputs. This is by design -- the comment says the graph builder handles module creation. But the graph builder creates the entry points too late (after param_groups is frozen).

**Chain of failure:**
1. Backtracker doesn't trace FORMULA module input dependencies (not its job)
2. `backtracking_result.entry_points` doesn't contain FORMULA module inputs
3. `_group_entry_points_via_deriver()` filters by `backtracking_result.entry_points` -- excludes FORMULA inputs
4. `param_groups` is frozen without FORMULA module inputs
5. Step 6.5 adds new entry points to `entry_points` dict -- but `param_groups` is stale
6. `ComputationGraph.entry_point_groups = param_groups` -- missing FORMULA inputs
7. Schema and JSON generation iterate `entry_point_groups` -- FORMULA inputs absent

#### Clean Fix

**Add a Step 6.6: Incorporate FORMULA-created entry points into param_groups.**

After Step 6.5 builds all computed attribute modules (graph_builder.py, after line 167), add a reconciliation step:

```python
# Step 6.6: Incorporate FORMULA-created entry points into param_groups
# Entry points created in Step 6.5 are not yet in param_groups.
# Reconcile by finding new EPs and adding them to the appropriate group.
existing_ep_qnames = set()
for pg in param_groups:
    for param in pg.parameters:
        existing_ep_qnames.add(param.qualified_name)

for ep in entry_points.values():
    if ep.qualified_name not in existing_ep_qnames:
        # Find or create the appropriate parameter group
        target_group = _find_or_create_param_group(param_groups, ep, group_deriver)
        target_group.parameters.append(ep)
```

The `_find_or_create_param_group` helper would use `group_deriver.classify(ep.qualified_name)` (which is already called at line 700) to determine which group the entry point belongs to, then either find an existing matching group or create a new one.

**Why not fix in the backtracker?** The backtracker traces CalcUsage dependency graphs. FORMULA modules are synthetic (created by the graph builder, not extracted from SysML CalcUsages). Making the backtracker understand FORMULA module input dependencies would blur the separation of concerns. The graph builder already has the logic to identify FORMULA inputs (the `else` branch at line 687) -- it just needs to close the loop by syncing param_groups.

**Files to change:**
- `src/sysml_codegen/resolution/graph_builder.py` -- Add Step 6.6 after the computed attribute loop (line ~168)

---

### Bug 2: FORMULA/EXPOSE Backtracker Wiring

**Symptom**: CalcUsage inputs bound to FORMULA attributes (`energy.power_mw`, `lcoe.annual_om`) or EXPOSE aliases (`financial.total_capex`) are treated as entry point parameters instead of being wired to upstream MODULE_OUTPUT channels.

**Manual workaround applied**: Rewired 3 inputs in pipeline.yaml (Patterns 10-12).

#### Root Cause: Index key format mismatch + missing EXPOSE_PURE awareness

**Two distinct failure modes:**

##### Failure Mode A: FORMULA bindings (energy.power_mw, lcoe.annual_om)

The backtracker builds a `_computed_attr_index` (dependency_backtracker.py:138-145) with keys in two formats:
- `"e2e_plant.power_mw"` (dotted: `{owning_part_name}.{python_name}`)
- `"power_mw"` (bare: `{python_name}`)

When processing a CalcUsage binding like `in power_mw = power_mw` (a `FeatureReferenceExpression`), the usage extractor's `_parse_reference_expression()` (usage_extractor.py:373-389) returns `source_path = str(referent.qualified_name)`, which is a SysML qualified name using `::` separators:
```
"E2EAttrExprDesign::e2e_plant::power_mw"
```

The backtracker lookup (dependency_backtracker.py:397-400):
```python
ca = self._computed_attr_index.get(binding.source_path)       # "E2E...::power_mw" -- MISS
if ca is None and "." in binding.source_path:                  # No "." in "::" path -- SKIP
    bare = binding.source_path.split(".")[-1]
    ca = self._computed_attr_index.get(bare)
```

**The index uses `"e2e_plant.power_mw"` (dotted) and `"power_mw"` (bare) keys, but the lookup value is `"E2EAttrExprDesign::e2e_plant::power_mw"` (SysML qualified with `::`).**

Neither key format matches. The dotted-path fallback doesn't trigger because `"::"` doesn't contain `"."`. The lookup misses completely, and the binding falls through to `_resolve_binding_to_usage()` which also doesn't find a CalcUsage producing `power_mw` (it's a computed attribute, not a calc output), so it becomes an ENTRY_POINT.

**Why did solar_battery's E2E tests pass?** The ATTR-EXPR E2E tests (test_computed_attributes_e2e.py) validated that `annualized_om.p_net_kw` was wired as MODULE_OUTPUT. This means either:
1. The solar_battery binding produces a source_path in a format that matches the index (e.g., bare name or dotted path), OR
2. The binding goes through the design attribute transitive resolution path (`_resolve_to_design_attribute` -> `_design_attr_binding_index`), which accidentally resolves correctly for solar_battery's simpler model structure

The likely explanation is that the solar_battery SysML model's binding `in p_net_kw = p_net_kw` produces a source_path that happens to match due to SysIDE's resolution behavior for that specific model structure (fewer nested namespaces). The e2e_attr_expr model's deeper nesting produces longer qualified names that don't match.

##### Failure Mode B: EXPOSE_PURE bindings (financial.total_capex)

The `_computed_attr_index` explicitly excludes non-FORMULA attributes (dependency_backtracker.py:140-141):
```python
if ca.classification != ComputedAttributeClassification.FORMULA:
    continue
```

EXPOSE_PURE attributes are never indexed. The backtracker has **zero awareness** of EXPOSE_PURE attributes.

ADR-004 Section "Decision 4" states: *"EXPOSE_PURE backtracker transitive resolution already worked."* This was observed for the solar_battery and CATF models where the design attribute binding index (`_design_attr_binding_index`) provides a transitive path: `total_capex` -> design attr -> `component_cost.total_cost` -> calc output -> MODULE_OUTPUT.

However, for this transitive path to work, the EXPOSE_PURE attribute must remain in `design_attributes` (it does -- Step 4.5 only removes FORMULA attributes) AND the design attribute binding index must properly map it. If the binding index construction can't trace through the EXPOSE expression, the resolution falls through to ENTRY_POINT.

The e2e_attr_expr model's `total_capex = component_cost.total_cost` may not resolve transitively if the binding index doesn't recognize the expression format for this model structure. This would explain why the manual workaround was needed.

#### Clean Fix

**Fix A: Normalize `_computed_attr_index` keys to include SysML qualified names.**

In the backtracker's `__init__` (dependency_backtracker.py:138-145), add the SysML qualified name as a third key per FORMULA attribute:

```python
self._computed_attr_index: dict[str, ComputedAttributeData] = {}
for ca in self._computed_attributes:
    if ca.classification != ComputedAttributeClassification.FORMULA:
        continue
    if ca.compilability != Compilability.FULLY_COMPILABLE:
        continue
    # Existing keys
    self._computed_attr_index[f"{ca.owning_part_name}.{ca.python_name}"] = ca
    self._computed_attr_index[ca.python_name] = ca
    # NEW: SysML qualified name key (what FeatureReferenceExpression produces)
    sysml_qn = f"{ca.owning_part_qualified_name}::{ca.name}"
    self._computed_attr_index[sysml_qn] = ca
```

Also add normalization in the lookup path (dependency_backtracker.py:397-400) to handle `::` paths:

```python
ca = self._computed_attr_index.get(binding.source_path)
if ca is None:
    if "." in binding.source_path:
        bare = binding.source_path.split(".")[-1]
        ca = self._computed_attr_index.get(bare)
    elif "::" in binding.source_path:
        bare = binding.source_path.split("::")[-1]
        ca = self._computed_attr_index.get(bare)
```

**Fix B: Add EXPOSE_PURE to the backtracker index with alias resolution.**

Either:
1. **Verify transitive resolution works** for the e2e_attr_expr model's EXPOSE_PURE pattern. If it does, no backtracker changes needed for EXPOSE.
2. If transitive resolution fails, add EXPOSE_PURE to a separate index and implement alias resolution in `_trace_dependencies()`:

```python
# In __init__:
self._expose_pure_index: dict[str, ComputedAttributeData] = {}
for ca in self._computed_attributes:
    if ca.classification == ComputedAttributeClassification.EXPOSE_PURE:
        self._expose_pure_index[f"{ca.owning_part_name}.{ca.python_name}"] = ca
        self._expose_pure_index[ca.python_name] = ca
        sysml_qn = f"{ca.owning_part_qualified_name}::{ca.name}"
        self._expose_pure_index[sysml_qn] = ca

# In _trace_dependencies(), after FORMULA check:
if ca is None:
    expose = self._expose_pure_index.get(binding.source_path)
    # (also try bare/qualified variants)
    if expose:
        # Resolve alias: trace through to upstream calc output
        channel = self._resolve_expose_alias_channel(expose)
        # ... create MODULE_OUTPUT resolution ...
```

**Files to change:**
- `src/sysml_codegen/analysis/dependency_backtracker.py` -- `__init__` (index keys), `_trace_dependencies()` (lookup normalization + EXPOSE path)

---

### Bug 3: FORMULA Module Input Type Mismatch

**Symptom**: FORMULA module wrappers use `Float` (RootModel[float]) for input types, while CalcUsage modules use plain `float`. TEAx feeds `float` values to FORMULA modules, causing type mismatch.

**Manual workaround applied**: Changed all 6 FORMULA module Input classes and method signatures from `Float` to `float`.

#### Root Cause: Hardcoded type hint in `_generate_computed_attr_modules()`

There are **two separate code paths** for generating module wrappers:

| Path | Location | `type_hint` | Result |
|------|----------|------------|--------|
| CalcUsage | `generation/modules.py` -> `_map_input_type()` | `"float"` | Correct |
| FORMULA | `cli/__init__.py` -> `_generate_computed_attr_modules()` | `"Float"` | **Bug** |

The CalcUsage path calls `_map_input_type()` (modules.py:171-195) which maps SysML types to Python primitives:
```python
mapping = {"Real": "float", "Integer": "int", ...}
```

The FORMULA path in `cli/__init__.py:264-267` bypasses this mapping entirely and hardcodes `"Float"`:
```python
input_attributes = [
    {"name": n, "type_hint": "Float", "description": f"Input {n}"}
    for n in input_names
]
```

`Float` is `RootModel[float]` -- a Pydantic wrapper that expects JSON input `{"root": 5.0}`, not bare `5.0`. The pipeline passes bare `float` values between modules, so FORMULA module inputs fail validation.

**Note**: The output type is correctly `Float` (RootModel[float]) for single-output modules. This is the TEAx convention -- single outputs are wrapped in RootModel, and downstream consumers extract via `.root`. The bug is **only in the input types**.

#### Clean Fix

Change one line in `cli/__init__.py:265`:

```python
# Before:
{"name": n, "type_hint": "Float", "description": f"Input {n}"}
# After:
{"name": n, "type_hint": "float", "description": f"Input {n}"}
```

No other changes needed. The `Float` import for output wrapping is already unconditionally added at line 274:
```python
primitive_types.add("Float")  # Output is always Float for computed attrs
```

**Files to change:**
- `src/sysml_codegen/cli/__init__.py` -- Line 265: `"Float"` -> `"float"`

---

### Bug 4: ExitPoint Float Write Handler Missing

**Symptom**: Multi-output CalcUsage modules produce `float` channels, but ExitPoint only has write handlers for Pydantic models. The pipeline can't serialize multi-output results to JSON files.

**Manual workaround applied**: Removed multi-output channels from exit_point; verify script checks them via direct `_impl` call instead.

#### Root Cause: Type asymmetry between single-output and multi-output channels

The `_build_exit_points()` function in `generation/pipeline.py:200-231` assigns exit point types based on `field_name`:

```python
if out.field_name == "root":
    output_type = f"RootModel[{out.python_type}]"   # Single-output: "RootModel[float]"
else:
    output_type = out.python_type                     # Multi-output: "float"
```

| Module Type | Channel Value | Exit Type | TEAx Can Serialize? |
|------------|--------------|-----------|---------------------|
| Single-output (`field_name="root"`) | `Float` (RootModel[float]) | `RootModel[float]` | Yes -- `.model_dump_json()` |
| Multi-output (`field_name="material_cost"`) | bare `float` | `float` | **No** -- no handler |

TEAx's ExitPoint module automatically extracts fields from a `MultiOutput` BaseModel and places the raw `float` value onto individual named channels. When ExitPoint tries to serialize these bare `float` values to JSON files, it has no handler for Python primitive types.

The multi-output module wrapper (from teax_module.py.jinja2) returns:
```python
return ModuleResult(data=ComponentCostCalcOutput(
    material_cost=material_cost,  # float field
    ...
))
```

TEAx extracts each field → bare `float` on channel → ExitPoint can't write it.

#### Prior Art: This Was Solved in fusion_modeling (2024-12-24)

This exact issue was encountered and resolved in the pre-migration `fusion_modeling` project. Four related bugs were identified and fixed in:
- `~/fusion_modeling/project/research/20251224-045908_multioutput-float-wrapping-bug.md`
- `~/fusion_modeling/project/research/20251224-041936_exitpoint-write-handler-error.md`
- `~/fusion_modeling/project/research/20251224-070000_audit-multioutput-fixes.md`

The **established architectural rule** from that work is:

| Pattern | Channel Contents | Exit Point Type | Handler |
|---------|-----------------|-----------------|---------|
| Single-output | `RootModel[float]` | `RootModel[float]` | JSON model writer (via CUSTOM_SCHEMA_TYPES -- Gap 2 fix) |
| Multi-output | bare `float` | `float` | **Primitive write handler** (`write_json_primitive`) |

**Key decisions from the prior work:**

1. **Do NOT wrap multi-output channels in RootModel.** This was tried (fusion_modeling Bug 1) and caused breakage -- the module template wrapping values in `Float()` broke schema validation because `MultiOutput` fields expect plain `float`, not `RootModel[float]`.

2. **Keep the type asymmetry.** It reflects how TEAx actually works: the executor auto-extracts multi-output fields to bare primitives on channels. This is not a bug -- it's the intended design (see `~/teax/docs/rootmodel-and-primitives.md`).

3. **Add a primitive write handler** to the output router for `float` (and other primitives). The fusion_modeling fix used a custom `write_json_primitive` function registered in the run script.

The sysml-codegen "Gap 2" fix (completed 2026-02-01) handles the single-output side by registering `Float` in `CUSTOM_SCHEMA_TYPES`. But the multi-output primitive handler was never ported to sysml-codegen's generated code.

#### Clean Fix (Consistent with Prior Decision)

**Generate a primitive write handler in the output router configuration.**

The fix belongs in the code generation for `run_pipeline.py` (or the output router setup). When multi-output modules exist in the pipeline, the generated code must register a primitive write handler:

```python
import json
from pathlib import Path

def write_json_primitive(data, file_path: Path):
    """Write a primitive value (float, int, str, bool) to JSON."""
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

# Register primitive handlers in the output router
router.register_handler("float", WriteHandler(fn=write_json_primitive, extension=".json"))
router.register_handler("int", WriteHandler(fn=write_json_primitive, extension=".json"))
```

Alternatively, sysml-codegen can detect when multi-output modules exist and include primitive types in the `CUSTOM_SCHEMA_TYPES` list alongside a custom handler. The cleanest approach is:

1. Extend `_collect_exit_point_primitive_types()` in `registry.py` to also collect bare primitive type names for multi-output channels
2. Generate a `PRIMITIVE_WRITE_HANDLERS` dict in the registry that maps `"float"` → `write_json_primitive`
3. Pass these handlers to `create_output_router_with_json_schemas()` or register them separately

**`_build_exit_points()` stays exactly as-is** -- it correctly uses bare `float` for multi-output (this is the canonical type per the prior decision).

**Files to change:**
- `src/sysml_codegen/generation/registry.py` -- Extend to collect multi-output primitive types and generate handler registration
- `src/sysml_codegen/templates/run_pipeline.py.jinja2` (or equivalent) -- Include primitive write handler function and registration
- No changes to `pipeline.py` or TEAx

---

## Cross-Bug Analysis

### Relationship Between Bugs 1 and 2

Bugs 1 and 2 are **complementary gaps** in the computed attribute integration:

- **Bug 2** (backtracker wiring): The backtracker doesn't correctly resolve CalcUsage→FORMULA bindings as MODULE_OUTPUT (index key mismatch)
- **Bug 1** (entry points): Even when Bug 2 is fixed, the FORMULA module's OWN input dependencies (literal sibling attributes) are never registered as entry points in param_groups

Fixing Bug 2 alone does NOT fix Bug 1. They require separate fixes:
- Bug 2 fix: Normalize backtracker index keys
- Bug 1 fix: Add Step 6.6 in graph builder to incorporate late-created entry points

### Why Solar Battery Tests Passed But E2E Attr Expr Failed

The ATTR-EXPR E2E tests (sysml-codegen's `test_computed_attributes_e2e.py`) validated the solar_battery fixture, which has:
- 1 FORMULA computed attribute (`p_net_kw`)
- 1 downstream CalcUsage binding to it
- A model structure that likely produces simpler source_path formats matching the index

The e2e_attr_expr model has:
- 6 FORMULA computed attributes
- 3 CalcUsage bindings to FORMULA/EXPOSE attributes (Patterns 10-12)
- A deeper namespace structure producing longer SysML qualified names

The index key mismatch (Bug 2) manifests only when `FeatureReferenceExpression` produces a full SysML qualified name with `::` separators that doesn't match the dotted/bare keys. The solar_battery fixture may have produced source_paths in a format that happened to match.

### Priority Order for Fixes

| Priority | Bug | Effort | Impact |
|----------|-----|--------|--------|
| 1 | Bug 2 (backtracker wiring) | Medium | Fixes Patterns 10-12 (FORMULA→CalcUsage and EXPOSE→CalcUsage wiring) |
| 2 | Bug 1 (entry points) | Medium | Fixes FORMULA module input params appearing in schema/JSON |
| 3 | Bug 3 (type mismatch) | Trivial | One-line fix, `"Float"` -> `"float"` |
| 4 | Bug 4 (exit_point) | Low-Medium | Design decision needed re: where to wrap primitives |

Bugs 1+2 should be addressed together as they share the computed attribute integration theme. Bug 3 is independent and trivial. Bug 4 may require coordination with TEAx.

## Code References

### Bug 1 (Entry Point Omission)
- `src/sysml_codegen/resolution/graph_builder.py:111-128` -- Steps 4-5 where entry_points and param_groups are frozen
- `src/sysml_codegen/resolution/graph_builder.py:156-167` -- Step 6.5 where new entry points are created
- `src/sysml_codegen/resolution/graph_builder.py:688-715` -- `_build_computed_attr_module()` else branch creating entry points
- `src/sysml_codegen/resolution/graph_builder.py:176-179` -- Return with stale param_groups
- `src/sysml_codegen/analysis/parameter_groups.py:467-481` -- `derive_groups_filtered()` filtering by backtracking result

### Bug 2 (Backtracker Wiring)
- `src/sysml_codegen/analysis/dependency_backtracker.py:138-145` -- `_computed_attr_index` construction (dotted/bare keys only)
- `src/sysml_codegen/analysis/dependency_backtracker.py:395-413` -- `_trace_dependencies()` computed attr lookup (no `::` handling)
- `src/sysml_codegen/extraction/usage_extractor.py:373-389` -- `_parse_reference_expression()` returns qualified_name with `::`
- `src/sysml_codegen/analysis/dependency_backtracker.py:140-141` -- EXPOSE_PURE explicitly excluded from index

### Bug 3 (Type Mismatch)
- `src/sysml_codegen/cli/__init__.py:264-267` -- Hardcoded `"Float"` for FORMULA input type_hint
- `src/sysml_codegen/generation/modules.py:171-195` -- `_map_input_type()` correctly maps `"Real"` -> `"float"` for CalcUsage
- `src/sysml_codegen/templates/teax_module.py.jinja2:29` -- Template renders `type_hint` into Input class fields

### Bug 4 (ExitPoint Handler)
- `src/sysml_codegen/generation/pipeline.py:200-231` -- `_build_exit_points()` type assignment (field_name-dependent)
- `src/sysml_codegen/generation/registry.py:37-61` -- `_collect_exit_point_primitive_types()` only collects for `field_name == "root"`
- `src/sysml_codegen/templates/teax_module.py.jinja2:104-116` -- Multi-output module returns BaseModel (TEAx auto-extracts fields as bare primitives)

## Recommendations

### Immediate Actions

1. **Fix Bug 3** (trivial, no risk): Change `"Float"` to `"float"` in `cli/__init__.py:265`
2. **Fix Bug 2** (medium, targeted): Add SysML qualified name keys to `_computed_attr_index` + normalize lookup
3. **Fix Bug 1** (medium, targeted): Add Step 6.6 in graph builder to reconcile param_groups
4. **Fix Bug 4** (low-medium, consistent with prior art): Generate primitive write handler registration for multi-output `float` channels in the output router setup (same pattern as fusion_modeling's `write_json_primitive` fix from 2024-12-24)

### Testing Strategy

After fixes, the E2E validation should be re-run against the e2e_attr_expr model:
1. Codegen with zero manual workarounds
2. All 16 numerical values pass (exact and tolerance checks)
3. All 12 patterns validated structurally (FORMULA modules, wiring, EXPOSE aliases)
4. Solar battery regression (existing ATTR-EXPR E2E tests still pass)

### Architectural Observation

The root cause of Bugs 1+2 is a **responsibility gap** between the backtracker and graph builder:
- The backtracker was designed to trace CalcUsage dependency graphs only
- FORMULA computed attributes are synthetic modules created by the graph builder
- The backtracker needs enough awareness of computed attributes to resolve bindings to them (Bug 2), but the graph builder handles module creation and input wiring
- The entry point registration for FORMULA module inputs falls between the two (Bug 1)

The clean separation is:
- **Backtracker**: Resolves CalcUsage bindings (including bindings to FORMULA/EXPOSE attrs) → produces `BindingResolution`
- **Graph builder**: Creates FORMULA modules, wires their inputs, creates their entry points, reconciles param_groups

This keeps the backtracker's role focused (binding resolution) while the graph builder handles the synthetic module lifecycle end-to-end.

## Open Questions

1. **Why did solar_battery's binding produce a matching source_path?** Need to inspect the actual `source_path` value from `_parse_reference_expression()` for the solar_battery fixture to confirm whether it's a bare name, dotted path, or qualified name. This determines whether the fix needs to be defensive (handle all formats) or targeted.

2. **Does EXPOSE_PURE transitive resolution work for e2e_attr_expr?** The plan says `total_capex` failed, but ADR-004 says transitive resolution "already worked." Need to trace the `_design_attr_binding_index` for the e2e_attr_expr model to determine if the EXPOSE fix is needed in the backtracker or if there's a separate issue in how the binding index handles expression-based attributes.

3. ~~**Should Bug 4 be fixed in sysml-codegen or TEAx?**~~ **RESOLVED by prior art.** The fusion_modeling project (2024-12-24) established that the fix is a primitive write handler (`write_json_primitive`) registered in the output router, generated by sysml-codegen. The type asymmetry (single-output=RootModel, multi-output=bare primitive) is the correct TEAx architecture and should NOT be changed. See `~/fusion_modeling/project/research/20251224-045908_multioutput-float-wrapping-bug.md` for the complete analysis.
