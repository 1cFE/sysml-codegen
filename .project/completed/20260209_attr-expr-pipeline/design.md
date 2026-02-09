# Design: Pipeline Integration -- Computed Attribute Modules (Alternative)

**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-02-09
**Branch:** cost-pattern
**Epic:** ATTR-EXPR Item 3

## Overview

Integrate Item 2's computed attribute extraction into the codegen pipeline so that FORMULA attributes produce executable pipeline modules with auto-implemented code, correct YAML wiring, and proper topological ordering alongside CalcUsage modules.

## Related Artifacts

- **Spec:** `.project/active/attr-expr-pipeline/spec.md`
- **Architectural Decisions:** `.project/concepts/attr-expr-architectural-decisions.md`
- **Research:** `.project/research/20260202-180000_expression-compilation-and-inline-math-strategy.md`
- **Item 2 Extraction:** `src/sysml_codegen/extraction/computed_attribute_extractor.py`
- **Item 2 Data Models:** `src/sysml_codegen/extraction/data_models.py`

---

## Research Findings

### EXPOSE_PURE Is Already Handled by the Backtracker (FR-21 Answered)

The existing backtracker handles EXPOSE_PURE patterns transitively for CalcUsage bindings. The mechanism:

1. `extract_design_attributes()` captures EXPOSE attributes as `DesignAttributeData` with `default_value` set to the path reference (e.g., `"alpha_neutron_split.p_alpha"`).
2. `_build_design_attr_binding_index()` (`dependency_backtracker.py:705-741`) detects path references via `_is_path_reference()` and builds the index: `"design_part.p_alpha_out" -> "{usage_qn}__p_alpha"`.
3. `_resolve_binding_to_usage()` Strategy 4 (`dependency_backtracker.py:670-677`) performs transitive resolution through the index.
4. The binding is recorded as `MODULE_OUTPUT` in `_binding_resolutions`.

**Conclusion:** No code changes needed for EXPOSE_PURE CalcUsage bindings. The only new EXPOSE_PURE work is in the graph builder's attribute resolution map for FORMULA module input wiring (FR-22).

### Generation Architecture Requires Two Extension Points

The CLI generation in `cli/__init__.py` uses two iteration patterns:

1. **CalcDef-driven:** `_generate_modules()` and `_generate_stencils()` iterate `ctx.calc_defs`, calling `generate_teax_module()` and `generate_implementation()` per CalcDef.
2. **Graph-driven:** `_generate_pipeline()` and `_generate_registry()` use `ctx.computation_graph`.

For computed attribute modules:
- **Graph-driven generation** (pipeline YAML, exit points) works automatically once `PipelineModule` objects are in the `ComputationGraph` -- no template changes needed.
- **CalcDef-driven generation** (module wrappers, auto-impls) needs **new parallel loops** because computed attribute modules don't have `CalculationDefinitionData` objects.

### Naming Uses Existing Infrastructure Unchanged

For a computed attribute with `owning_part_qualified_name = "AttrExprProbeDesign::probe_design"` and `name = "area"`:

| Property | Value | How Derived |
|----------|-------|-------------|
| SysML QN | `"AttrExprProbeDesign::probe_design::area"` | Synthetic: `{owning_part_qn}::{attr_name}` |
| Module EQN | `"AttrExprProbeDesign__probe_design__area"` | `sysml_to_python_qualified_name(sysml_qn)` |
| Module name | `"attrexprprobedesign__probe_design__area"` | `get_module_name(eqn)` = lowercase |
| Module type | `"attrexprprobedesign.probe_design.AreaModule"` | `derive_module_type(sysml_qn)` |
| Channel name | `"AttrExprProbeDesign__probe_design__area__area"` | `get_channel_name(eqn, attr_name)` |
| Python path | `"attrexprprobedesign/probe_design/area"` | `PythonModulePath.from_sysml(sqn)` |
| Impl path | `"attrexprprobedesign.probe_design.area_impl"` | `.impl_import_path` |

Zero changes to `qualified_names.py` or `identifier_types.py`.

### Input Names From Compiled Expressions

`ComputedAttributeData.compiled_expression` uses deterministic format: `"(inputs.length * inputs.width)"`. Input names extracted via `re.findall(r'inputs\.(\w+)', expr)`, deduplicated preserving order. Only needed for FULLY_COMPILABLE FORMULA attributes where `compiled_expression` is guaranteed non-None.

---

## Design Decisions

### Decision: Backtracker Integration Strategy

**Context:** The backtracker's `_trace_dependencies()` must recognize when a CalcUsage binds to a FORMULA computed attribute. Two approaches:

**Option A -- Check before existing resolution:** Insert a computed-attribute lookup in `_trace_dependencies()` BEFORE calling `_resolve_binding_to_usage()`. If the binding's `source_path` matches a FORMULA attribute, record `MODULE_OUTPUT` and skip the normal resolution chain.

**Option B -- Extend `_resolve_binding_to_usage()` with a new strategy:** Add a Strategy 0 inside `_resolve_binding_to_usage()` that checks the computed attribute index before other strategies.

**Decision: Option A.** The check in `_trace_dependencies()` is cleaner because:
1. Computed attribute resolution doesn't need recursive dependency tracing -- the graph builder creates the module, not the backtracker. The `continue` after recording the resolution skips the recursive `_trace_dependencies()` call that normal MODULE_OUTPUT resolutions require.
2. Putting the check inside `_resolve_binding_to_usage()` would return a `CalcUsageData` that doesn't exist, requiring awkward sentinel handling.

### Decision: Output Catalog Construction Order

**Context:** The graph builder's `_build_output_catalog()` currently only maps CalcUsage outputs. Computed attribute outputs must also appear so that downstream CalcUsage bindings can wire to them.

**Decision:** Build computed attribute outputs into the output catalog BEFORE building CalcUsage modules. This ensures that when `_build_pipeline_module()` processes a CalcUsage that depends on a computed attribute output, the channel reference already exists for validation.

### Decision: Topological Sort Approach

**Context:** Currently, the backtracker provides `required_usages` pre-sorted. Computed attribute modules are built by the graph builder, not the backtracker. How to interleave them?

**Decision:** The graph builder performs a unified topological sort across ALL modules (CalcUsage + computed attribute) after building them all. This replaces relying on the backtracker's pre-sort for final ordering.

**Rationale:** The backtracker's topological sort only covers CalcUsage modules. A computed attribute module might need to execute BEFORE a CalcUsage module that consumes its output, or AFTER another computed attribute in a chain. The only way to get correct ordering is a unified sort across the full module set.

---

## Proposed Design

### Architecture Overview

The design has 7 components spanning 4 pipeline layers. Changes flow through the pipeline in this order:

```
Step 4.5 (initialization.py)    -- Extract & filter computed attrs
    ↓
Step 6 (dependency_backtracker) -- Resolve CalcUsage→FORMULA bindings
    ↓
Step 7 (graph_builder)          -- Generate FORMULA modules + unified toposort
    ↓
Step 8 (cli/__init__.py)        -- Generate module wrappers + auto-impls
```

### Component 1: Data Model -- `PipelineModule.is_computed_attribute`

**File:** `src/sysml_codegen/resolution/models.py:149-167`
**Change:** Add one field.

```python
class PipelineModule(BaseModel):
    name: str
    module_type: str
    inputs: list[ModuleInput]
    outputs: list[ModuleOutput]
    execution_order: int
    compilability: Compilability = Compilability.UNKNOWN
    is_computed_attribute: bool = False  # NEW
```

All existing CalcUsage modules default to `False`. Computed attribute modules set `True`. Used by pipeline YAML (comment), backlog (auto-implemented status), and registry (include in imports).

### Component 2: PipelineContext Extension

**File:** `src/sysml_codegen/generation/initialization.py:60-91`
**Change:** Add one field to the dataclass.

```python
from sysml_codegen.extraction.data_models import ComputedAttributeData

@dataclass
class PipelineContext:
    # ... existing 9 fields ...
    computed_attributes: list[ComputedAttributeData] = field(default_factory=list)
```

### Component 3: Step 4.5 -- Extraction and FORMULA Removal

**File:** `src/sysml_codegen/generation/initialization.py`
**Location:** Between Step 4 (line 152) and Step 5 (line 155) in `build_pipeline_context()`

New function `_extract_and_filter_computed_attributes()`:

```python
def _extract_and_filter_computed_attributes(
    model: Any,
    calc_usages: list[CalcUsageData],
    design_attrs: dict[Path, list[DesignAttributeData]],
) -> list[ComputedAttributeData]:
```

**Algorithm:**

1. **Iterate part elements.** Use `SysideAdapter.elements_of_type(model, "PartDefinition")` and `SysideAdapter.elements_of_type(model, "PartUsage")`. Same pattern as `extract_design_attributes()` in `parameter_groups.py:87-125`.

2. **Build calc_usage_names per part.** For each part element, collect CalcUsage instance names:
   ```python
   calc_usage_names = {
       m.name for m in part_elem.owned_members
       if SysideAdapter.is_instance(m, "CalculationUsage")
   }
   ```

3. **Call `extract_computed_attributes(None, part_elem, calc_usage_names)`** for each part element. The first `adapter` param is unused at runtime -- Item 2's classification and compilation logic uses `SysideAdapter.is_instance` as a static method and never calls `adapter` instance methods. Passing `None` is safe and avoids constructing an adapter instance. Accumulate into `all_computed_attrs`.

4. **Remove FORMULA attributes from `design_attrs`.** Build a set of qualified names to remove:
   ```python
   formula_qns = set()
   for ca in all_computed_attrs:
       if ca.classification == ComputedAttributeClassification.FORMULA:
           part_qn_python = sysml_to_python_qualified_name(ca.owning_part_qualified_name)
           formula_qns.add(f"{part_qn_python}__{ca.python_name}")
   ```
   Then filter in-place:
   ```python
   for path in design_attrs:
       design_attrs[path] = [
           a for a in design_attrs[path]
           if a.qualified_name not in formula_qns
       ]
   ```

5. **Log summary.** Breakdown by classification and count of FORMULA removals.

**Data flow:** The filtered `design_attrs` flows into Step 5 (ParameterGroupDeriver) and Step 6 (backtracker). The `computed_attributes` list flows into Step 6 (backtracker) and Step 7 (graph builder).

**Integration in `build_pipeline_context()`:**

```python
# Step 4.5: Extract computed attributes and remove FORMULAs from design_attrs
computed_attrs = _extract_and_filter_computed_attributes(
    extractor.model, calc_usages, design_attrs
)

# Step 5 & 6 now use filtered design_attrs
# Step 6: backtracker receives computed_attrs
backtracker = DependencyBacktracker(
    calc_usages, calc_defs,
    design_attributes=design_attrs,
    computed_attributes=computed_attrs,  # NEW
)

# Step 7: graph builder receives computed_attrs
computation_graph = build_computation_graph(
    ...,
    computed_attributes=computed_attrs,  # NEW
)

# PipelineContext includes computed_attrs
return PipelineContext(
    ...,
    computed_attributes=computed_attrs,
)
```

### Component 4: Backtracker Computed Attribute Awareness

**File:** `src/sysml_codegen/analysis/dependency_backtracker.py`

#### 4a. Constructor -- Build FORMULA Lookup Index

Add `computed_attributes` parameter to `__init__()`:

```python
def __init__(
    self,
    all_usages: list[CalcUsageData],
    calc_defs: list,
    design_attributes: dict[Path, list[DesignAttributeData]] | None = None,
    computed_attributes: list[ComputedAttributeData] | None = None,  # NEW
):
```

Build a lookup dict keyed by patterns that match `binding.source_path`:

```python
self._computed_attr_index: dict[str, ComputedAttributeData] = {}
if computed_attributes:
    for ca in computed_attributes:
        if ca.classification != ComputedAttributeClassification.FORMULA:
            continue
        # Key by "parent_part.attr_name" (matches dotted source_path)
        key = f"{ca.owning_part_name}.{ca.python_name}"
        self._computed_attr_index[key] = ca
        # Also key by bare attr name (for same-part references)
        self._computed_attr_index[ca.python_name] = ca
```

**Why two keys?** CalcUsage bindings may reference FORMULA attributes as either `"plant.p_net_kw"` (dotted path, from FeatureChainExpression) or `"p_net_kw"` (bare name, from same-part FeatureReferenceExpression). Both forms appear in real models.

**Bare-name collision assumption:** The bare-name key (`ca.python_name`) assumes that no two FORMULA attributes across different parts share the same name AND are both referenced by the same CalcUsage. This is safe because:
1. SysML scoping rules prevent name collisions within a single part.
2. Cross-part references always use dotted paths (e.g., `"other_part.area"`), which hit the dotted-path key first.
3. Same-part bare-name references are unambiguous because a CalcUsage lives on exactly one part.
If this assumption proves wrong in practice, the fix is to scope bare-name lookups to the usage's parent part context by keying as `(owning_part_name, python_name)` instead of just `python_name`.

#### 4b. Computed Attribute Channel Builder

New method to build the synthetic module's output channel name:

```python
def _build_computed_attr_channel(self, ca: ComputedAttributeData) -> str:
    """Build output channel name for a FORMULA computed attribute's synthetic module."""
    part_qn_python = sysml_to_python_qualified_name(ca.owning_part_qualified_name)
    module_eqn = f"{part_qn_python}__{ca.python_name}"
    return get_channel_name(module_eqn, ca.python_name)
```

Requires importing `get_channel_name` from `sysml_codegen.core.qualified_names`.

#### 4c. Integration in `_trace_dependencies()`

Insert BEFORE the existing `_resolve_binding_to_usage()` call (around line 373). The check runs after the LITERAL case and before the source_path resolution:

```python
if binding.source_path:
    # NEW: Check computed attribute resolution first
    ca = self._computed_attr_index.get(binding.source_path)
    if ca is None and "." in binding.source_path:
        # Try bare name for dotted paths
        bare = binding.source_path.split(".")[-1]
        ca = self._computed_attr_index.get(bare)

    if ca is not None:
        channel = self._build_computed_attr_channel(ca)
        self._binding_resolutions[mapping_key] = BindingResolution(
            resolution_type=BindingResolutionType.MODULE_OUTPUT,
            qualified_name=channel,
            source_path=binding.source_path,
            is_transitive=False,
        )
        self._trace_log.append(
            f"    {param_name} -> COMPUTED_ATTR ({channel})"
        )
        continue  # No recursive tracing -- graph builder creates the module

    # Existing resolution flow continues unchanged
    source_usage = self._resolve_binding_to_usage(binding.source_path)
    ...
```

**Key insight:** No recursive `_trace_dependencies()` call for computed attributes. The graph builder creates the synthetic module directly from `ComputedAttributeData`. The backtracker's only job is to record the correct `MODULE_OUTPUT` wiring.

### Component 5: Graph Builder FORMULA Module Generation

**File:** `src/sysml_codegen/resolution/graph_builder.py`

This is the largest change. It involves 5 sub-components.

#### 5a. Signature Extension

```python
def build_computation_graph(
    result: BacktrackingResult,
    calc_defs: list,
    design_attrs: dict[Path, list[DesignAttributeData]],
    group_deriver: ParameterGroupDeriver,
    compilation_results: dict | None = None,
    computed_attributes: list[ComputedAttributeData] | None = None,  # NEW
) -> ComputationGraph:
```

#### 5b. Per-Part Attribute Resolution Map

New data structure and builder function. The resolution map tells the graph builder how to wire each FORMULA module input:

```python
@dataclass
class AttributeResolution:
    """How an attribute reference in a FORMULA expression should be wired."""
    kind: str  # "formula" | "expose_alias" | "literal"
    channel_name: str | None = None  # For formula and expose_alias

def _build_attribute_resolution_map(
    computed_attrs: list[ComputedAttributeData],
    design_attrs: dict[Path, list[DesignAttributeData]],
    output_catalog: dict[str, tuple[str, str, str]],
    calc_usage_names: set[str],
) -> dict[str, dict[str, AttributeResolution]]:
    """Build per-part map: owning_part_name -> {attr_name -> AttributeResolution}.

    Args:
        calc_usage_names: CalcUsage instance names, needed for EXPOSE_PURE
            resolution to distinguish instance refs from output refs.
    """
```

**Resolution logic per attribute:**

| Attribute Kind | Resolution | Channel Source |
|---------------|------------|----------------|
| FORMULA computed attr | `kind="formula"` | Synthetic module channel: `get_channel_name(module_eqn, attr_name)` |
| EXPOSE_PURE computed attr | `kind="expose_alias"` | Resolve via `_resolve_expose_pure()` (see below) |
| Design attribute (literal) | `kind="literal"` | None (becomes entry point) |
| Not found | `kind="literal"` | None (conservative: entry point) |

**EXPOSE_PURE resolution algorithm:** An EXPOSE_PURE attribute like `p_alpha_out = alpha_split.p_alpha` has a `references` list containing two `ExpressionRef` entries (from `extract_feature_refs()`):
1. The calc output ref: `ExpressionRef(name="p_alpha", qualified_name="Library::AlphaSplitCalc::p_alpha")` -- the output attribute on the CalcDef, in a different namespace.
2. The calc usage instance ref: `ExpressionRef(name="alpha_split", qualified_name="Pkg::Part::alpha_split")` -- the CalcUsage instance on the same part, filtered during classification step 2a but still present in the `references` list.

To resolve to an output_catalog channel:

```python
def _resolve_expose_pure(
    ca: ComputedAttributeData,
    calc_usage_names: set[str],
    output_catalog: dict[str, tuple[str, str, str]],
) -> str | None:
    """Resolve an EXPOSE_PURE attribute to its upstream calc output channel.

    Returns channel_name if resolved, None if the catalog key is not found.
    """
    # Separate refs into calc_usage instance and calc output
    instance_name: str | None = None
    output_attr_name: str | None = None

    for ref in ca.references:
        if ref.name in calc_usage_names:
            instance_name = ref.name  # e.g., "alpha_split"
        else:
            output_attr_name = ref.name  # e.g., "p_alpha"

    if instance_name is None or output_attr_name is None:
        logger.warning(
            "EXPOSE_PURE %s: could not identify instance/output from refs %s",
            ca.name, [r.name for r in ca.references],
        )
        return None

    # Build output_catalog key: "{instance_name}.{output_attr_name}"
    catalog_key = f"{instance_name}.{output_attr_name}"
    entry = output_catalog.get(catalog_key)
    if entry is None:
        logger.warning(
            "EXPOSE_PURE %s: catalog key '%s' not found. Available: %s",
            ca.name, catalog_key, list(output_catalog.keys()),
        )
        return None

    _, channel_name, _ = entry
    return channel_name
```

This function is called from `_build_attribute_resolution_map()` for each EXPOSE_PURE computed attribute. The `calc_usage_names` set is the same one used during extraction (Step 4.5). If resolution fails, the attribute falls through to `kind="literal"` (conservative: entry point), and a warning is logged with the available catalog keys for debugging.

#### 5c. Computed Attribute Output Catalog Extension

Before building CalcUsage modules, extend the output catalog with computed attribute outputs:

```python
if computed_attributes:
    for ca in computed_attributes:
        if (ca.classification != ComputedAttributeClassification.FORMULA
                or ca.compilability != Compilability.FULLY_COMPILABLE):
            continue

        sysml_qn = f"{ca.owning_part_qualified_name}::{ca.name}"
        module_eqn = sysml_to_python_qualified_name(sysml_qn)
        module_type = derive_module_type(sysml_qn)
        channel_name = get_channel_name(module_eqn, ca.python_name)

        # Key: "part_name.attr_name" for binding resolution
        key = f"{ca.owning_part_name}.{ca.python_name}"
        output_catalog[key] = (module_type, channel_name, "root")
```

This must happen BEFORE `_build_pipeline_module()` calls, so CalcUsage modules that reference computed attribute outputs can validate their channel references.

#### 5d. FORMULA Module Builder

New function to build a `PipelineModule` from a `ComputedAttributeData`:

```python
def _build_computed_attr_module(
    ca: ComputedAttributeData,
    resolution_map: dict[str, AttributeResolution],
    entry_points: dict[str, EntryPoint],
    param_groups: list[ParameterGroup],
    design_attrs: dict[Path, list[DesignAttributeData]],
    group_deriver: ParameterGroupDeriver,
) -> PipelineModule:
```

**Naming:**
```python
sysml_qn = f"{ca.owning_part_qualified_name}::{ca.name}"
module_eqn = sysml_to_python_qualified_name(sysml_qn)
module_name = get_module_name(module_eqn)
module_type = derive_module_type(sysml_qn)
```

**Input construction:**
1. Extract input names from compiled expression: `re.findall(r'inputs\.(\w+)', ca.compiled_expression)`, deduplicate preserving order.
2. For each input name, look up in `resolution_map[ca.owning_part_name]`:
   - `kind == "formula"` or `kind == "expose_alias"` → `InputSource(source_type="module_output", producer_channel=channel_name)`
   - `kind == "literal"` or not found → Create/reuse entry point. Build qualified name as `{part_eqn}__{input_name}` where `part_eqn = sysml_to_python_qualified_name(ca.owning_part_qualified_name)`. Look up default value from `design_attrs`. Create `EntryPoint` with `entry_type=DESIGN_ATTRIBUTE`. Add to `entry_points` dict and appropriate parameter group.

**Output construction:** Single `ModuleOutput`:
```python
ModuleOutput(
    field_name="root",
    python_type="float",
    channel_name=get_channel_name(module_eqn, ca.python_name),
)
```

**Module construction:**
```python
PipelineModule(
    name=module_name,
    module_type=module_type,
    inputs=inputs,
    outputs=[output],
    execution_order=0,  # Assigned during unified toposort
    compilability=Compilability.FULLY_COMPILABLE,
    is_computed_attribute=True,
)
```

#### 5e. Unified Topological Sort

After building ALL modules (CalcUsage from existing loop + computed attribute from new loop), perform a unified topological sort:

```python
def _unified_topological_sort(modules: list[PipelineModule]) -> list[PipelineModule]:
    """Sort all modules by their inter-module dependencies."""
    # Build channel→module lookup
    channel_to_module: dict[str, str] = {}
    for m in modules:
        for out in m.outputs:
            channel_to_module[out.channel_name] = m.name

    # Build dependency graph: module_name → [dependency_module_names]
    graph: dict[str, list[str]] = {m.name: [] for m in modules}
    for m in modules:
        for inp in m.inputs:
            if inp.source.source_type == "module_output" and inp.source.producer_channel:
                dep_module = channel_to_module.get(inp.source.producer_channel)
                if dep_module and dep_module != m.name:
                    if dep_module not in graph[m.name]:
                        graph[m.name].append(dep_module)

    # Kahn's algorithm
    sorted_names = _kahn_sort(graph)

    # Reassign execution_order
    name_to_order = {name: i for i, name in enumerate(sorted_names)}
    for m in modules:
        m.execution_order = name_to_order[m.name]

    return sorted(modules, key=lambda m: m.execution_order)
```

This replaces the assumption that `result.required_usages` ordering is sufficient. The sorted modules list is used for `ComputationGraph.modules` and `execution_order`.

#### 5f. Integration in `build_computation_graph()`

Updated main function flow:

```python
def build_computation_graph(...):
    # Step 1: Build calc def lookup
    calc_def_map = ...

    # Step 2: Build output catalog (CalcUsage outputs)
    output_catalog = _build_output_catalog(result.required_usages, calc_def_map)

    # Step 2.5: Extend output catalog with computed attribute outputs
    if computed_attributes:
        _extend_output_catalog_with_computed_attrs(output_catalog, computed_attributes)

    # Step 3: Build attribute resolution map (for FORMULA module input wiring)
    #   calc_usage_names needed for EXPOSE_PURE resolution
    calc_usage_names = {u.instance_name for u in result.required_usages}
    attr_resolution_map = {}
    if computed_attributes:
        attr_resolution_map = _build_attribute_resolution_map(
            computed_attributes, design_attrs, output_catalog, calc_usage_names
        )

    # Step 4: Classify entry points (existing)
    entry_points = _classify_entry_points(...)

    # Step 5: Group entry points (existing)
    param_groups = _group_entry_points_via_deriver(...)

    # Step 6: Build CalcUsage modules (existing loop)
    modules = []
    for idx, usage in enumerate(result.required_usages):
        module = _build_pipeline_module(...)
        modules.append(module)

    # Step 6.5: Build computed attribute modules
    if computed_attributes:
        for ca in computed_attributes:
            if (ca.classification == ComputedAttributeClassification.FORMULA
                    and ca.compilability == Compilability.FULLY_COMPILABLE):
                module = _build_computed_attr_module(
                    ca, attr_resolution_map, entry_points,
                    param_groups, design_attrs, group_deriver,
                )
                modules.append(module)

    # Step 7: Unified topological sort (replaces pre-sorted assumption)
    modules = _unified_topological_sort(modules)

    # Step 8: Validate channel references (existing)
    _validate_channel_references(modules)

    return ComputationGraph(
        modules=modules,
        entry_point_groups=param_groups,
        execution_order=[m.name for m in modules],
    )
```

### Component 6: Code Generation for Computed Attribute Modules

**File:** `src/sysml_codegen/cli/__init__.py`

#### 6a. Module Wrapper Generation

New function `_generate_computed_attr_modules()`, called after `_generate_modules()`:

Iterates `ctx.computed_attributes`, filters to FORMULA with FULLY_COMPILABLE. For each:

1. **Build synthetic SysML QN:** `f"{ca.owning_part_qualified_name}::{ca.name}"`
2. **Derive paths:** `SysMLQualifiedName(sysml_qn)` → `PythonModulePath.from_sysml(sqn)`
3. **Extract input names:** `re.findall(r'inputs\.(\w+)', ca.compiled_expression)`, deduplicate
4. **Build template context** for `teax_module.py.jinja2`:

```python
context = {
    "class_name": derive_module_type(sysml_qn).split(".")[-1],  # e.g., "AreaModule"
    "input_class_name": derive_module_type(sysml_qn).split(".")[-1].replace("Module", "Input"),
    "output_class_name": None,  # Not used (single-output)
    "schema_name": None,
    "handler_name": get_module_name(module_eqn),
    "impl_import_path": python_path.impl_import_path,
    "doc_comment": f"Computed attribute module.\n\nSysML Expression: {ca.expression_text}",
    "package_name": config.package_name,
    "is_multioutput": False,
    "input_attributes": [
        {"name": n, "type_hint": "float", "description": f"Input {n}"}
        for n in input_names
    ],
    "output_attributes": [{"name": ca.python_name, "description": f"Computed {ca.name}"}],
    "calc_expressions": [ca.expression_text],
    "sysml_source": f"{ca.source_file}:{ca.source_line}",
    "primitive_imports": ["Float"],
}
```

5. **Render** with `teax_module.py.jinja2`. Write to `modules/{python_path.full_path}`.

The existing `teax_module.py.jinja2` template should work without modification because computed attribute modules are single-output (like most CalcUsage modules).

#### 6b. Auto-Implementation Generation

New function `_generate_computed_attr_stencils()`, called after `_generate_stencils()`:

For each FORMULA+FULLY_COMPILABLE computed attribute:

1. **Build template context** for `auto_implementation.py.jinja2`:

```python
context = {
    "function_name": f"run_{get_module_name(module_eqn)}",
    "calc_name": module_eqn,
    "input_class_name": input_class_name,  # Same as module wrapper
    "return_type": "float",
    "execution_steps": [],  # No intermediate steps
    "output_expressions": [{"name": ca.python_name, "expression": ca.compiled_expression}],
    "output_count": 1,
    "single_output_expression": ca.compiled_expression,
    "module_import_path": python_path.import_path,
    "package_name": config.package_name,
    "sysml_source": f"{ca.source_file}:{ca.source_line}",
    "sysml_expressions": [ca.expression_text],
    "docstring": f"Execute {ca.name} computed attribute.\n\nSysML Expression: {ca.expression_text}",
}
```

2. **Render** with `auto_implementation.py.jinja2`. Write to `handwritten/{python_path.directory}/{python_path.filename}_impl.py`.

The auto_implementation template already handles single-output with `single_output_expression` -- no template changes needed.

#### 6c. Registry Extension

**File:** `src/sysml_codegen/generation/registry.py`

Extend `generate_registry_function()` to accept computed attributes:

```python
def generate_registry_function(
    calc_defs: list[CalculationDefinitionData],
    package_name: str,
    template_env: jinja2.Environment,
    output_path: Path,
    entry_point_groups: list[ModelParameterGroup],
    exit_point_primitive_types: list[str] | None = None,
    computed_attributes: list[ComputedAttributeData] | None = None,  # NEW
) -> str:
```

Add computed attribute modules to `all_modules` list and `imports` list:

```python
if computed_attributes:
    for ca in computed_attributes:
        if ca.classification == ComputedAttributeClassification.FORMULA and \
           ca.compilability == Compilability.FULLY_COMPILABLE:
            sysml_qn = f"{ca.owning_part_qualified_name}::{ca.name}"
            sqn = SysMLQualifiedName(sysml_qn)
            python_path = PythonModulePath.from_sysml(sqn)
            module_type_full = derive_module_type(sysml_qn)
            class_name = module_type_full.split(".")[-1]

            all_modules.append({
                "class_name": class_name,
                "module_type": module_type_full,
            })
            imports.append(
                f"from {package_name}.modules.{python_path.import_path} import {class_name}"
            )
```

#### 6d. Backlog Extension

**File:** `src/sysml_codegen/generation/stencils.py`

Extend `generate_backlog_report()` to accept and report on computed attributes:

```python
def generate_backlog_report(
    calc_defs: list[CalculationDefinitionData],
    compilation_results: dict[str, CalcDefCompilationResult] | None = None,
    computed_attributes: list[ComputedAttributeData] | None = None,  # NEW
) -> str:
```

FORMULA+FULLY_COMPILABLE computed attributes are excluded from the manual implementation count (auto-implemented). Add a summary line: "N computed attribute modules (auto-implemented)".

#### 6e. Pipeline YAML Comment

**File:** `src/sysml_codegen/generation/pipeline.py`

In `_module_to_context()`, use `is_computed_attribute` to add a source comment:

```python
def _module_to_context(module, channel_field_map):
    return {
        ...,
        "name": (
            f"source: computed_attribute ({module.module_type})"
            if module.is_computed_attribute
            else module.module_type
        ),
    }
```

The YAML template already uses `{{ module.name }}` in the comment line above each module entry. This change makes computed attribute modules self-documenting in the generated YAML.

### Component 7: Integration Tests

**File:** `tests/integration/test_computed_attribute_pipeline.py`

Using mock infrastructure consistent with existing test patterns (`test_computed_attribute_extraction.py`):

#### Test 1: Simple FORMULA Module Generation

Create a mock part with `area = length * width`. Run through graph builder. Verify:
- `PipelineModule` created with `is_computed_attribute=True`
- Inputs: `length`, `width` wired to entry points
- Output: channel `{part_qn}__area__area`
- `compilability == FULLY_COMPILABLE`

#### Test 2: FORMULA Chain

Create `area = l * w` and `cost = area * rate`. Verify:
- Two `PipelineModule` objects created
- `cost` module's `area` input wired to `area` module's output channel
- `area.execution_order < cost.execution_order`

#### Test 3: FORMULA With EXPOSE_PURE Input

Create calc usage with output, EXPOSE_PURE alias, and FORMULA referencing the alias. Verify:
- Only FORMULA module generated (not EXPOSE)
- FORMULA module's input wired to calc output channel (through alias resolution)

#### Test 4: FORMULA Removal From design_attributes

Verify FORMULA attributes absent from `design_attrs` after Step 4.5. Non-FORMULA attributes preserved.

#### Test 5: Backtracker Resolution

CalcUsage with `in p_net_kw = p_net_kw` where `p_net_kw` is FORMULA. Verify:
- `binding_resolutions` contains `MODULE_OUTPUT` (not `ENTRY_POINT`)
- Channel points to synthetic module output

#### Test 6: Empty Computed Attributes

Model with no computed attributes. Verify zero impact on existing pipeline behavior.

---

## Potential Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| `binding.source_path` format doesn't match computed attr index keys | Medium | High | Support both bare name and dotted path in index; test with real binding extraction patterns |
| Unified toposort changes relative order of CalcUsage modules | Low | Medium | The unified sort respects the same dependency edges; verify with full regression suite |
| Computed attr naming collides with CalcUsage module naming | Low | Medium | SysML namespace rules prevent this; spec documents the assumption |
| `design_attributes` qualified name format mismatch during FORMULA removal | Medium | Medium | Unit test removal logic with exact format from `build_element_qualified_name()` |
| EXPOSE_PURE alias resolution fails when output_catalog key format doesn't match | Medium | High | Test with real CATF EXPOSE patterns; log mismatches with available catalog keys |
| Entry points created by FORMULA modules don't get grouped properly | Low | Medium | Reuse `group_deriver.classify()` for consistent grouping |

---

## Integration Strategy

### Files Changed

| File | Change Type | Approx. Lines |
|------|------------|---------------|
| `resolution/models.py` | Field addition | ~1 |
| `generation/initialization.py` | Step 4.5 + field | ~50 |
| `analysis/dependency_backtracker.py` | Constructor + resolution | ~40 |
| `resolution/graph_builder.py` | Module gen + attr resolution map + toposort | ~150 |
| `cli/__init__.py` | Generation loops | ~80 |
| `generation/pipeline.py` | Comment support | ~5 |
| `generation/registry.py` | Computed attr inclusion | ~25 |
| `generation/stencils.py` | Backlog extension | ~15 |

### Files NOT Changed

- `extraction/computed_attribute_extractor.py` -- Item 2 code untouched
- `extraction/data_models.py` -- No new fields needed
- `extraction/expression_compiler.py` -- Reused as-is
- `analysis/parameter_groups.py` -- Receives pre-filtered design_attrs
- `templates/auto_implementation.py.jinja2` -- Works as-is for single-output
- `templates/teax_module.py.jinja2` -- Works as-is for single-output
- `templates/pipeline_yaml.jinja2` -- Comment change handled in `pipeline.py`

### Implementation Order

1. **`resolution/models.py`** -- Trivial, no dependencies. Unblocks everything else.
2. **`generation/initialization.py`** -- Step 4.5 extraction + filtering. Must be done before backtracker/graph builder changes because those need computed_attributes as input.
3. **`analysis/dependency_backtracker.py`** -- Computed attribute awareness. Can be tested independently with unit tests.
4. **`resolution/graph_builder.py`** -- Heaviest change: attribute resolution map, FORMULA module building, unified toposort. Depends on 1-3.
5. **`generation/pipeline.py`** -- Comment support. Trivial.
6. **`cli/__init__.py`** -- Module wrapper + auto-impl generation loops. Depends on 4.
7. **`generation/registry.py` + `generation/stencils.py`** -- Extensions. Light.
8. **`tests/integration/test_computed_attribute_pipeline.py`** -- Full integration validation.

---

## Validation Approach

### Automated Testing

- **Unit tests:** FORMULA removal from design_attrs, backtracker computed attr resolution, attribute resolution map, FORMULA module construction, unified toposort
- **Integration tests:** End-to-end from extraction through graph building (Component 7 scenarios)
- **Regression:** `uv run pytest tests/` (182+ tests must pass)
- **Type checking:** `uv run mypy src/`
- **Lint:** `uv run ruff check src/`

### Manual Verification

After implementation, run codegen on the `attr_expr_probe` fixture and verify:
- Pipeline YAML contains computed attribute modules with `# source: computed_attribute` comments
- Auto-implementation files contain correct compiled expressions (e.g., `return (inputs.length * inputs.width)`)
- Module wrappers have correct input/output schemas
- `IMPLEMENTATION_BACKLOG.md` shows computed attrs as auto-implemented
- Module registry includes computed attribute module imports
- Topological ordering is correct (chains execute in dependency order)

---

**Next Step:** After approval -> `/_my_plan` for implementation planning, then `/_my_implement`
