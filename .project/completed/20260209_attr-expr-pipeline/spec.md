# Spec: Pipeline Integration -- Computed Attribute Modules

**Status:** Complete
**Owner:** Reid Westwood
**Created:** 2026-02-08 23:30
**Complexity:** HIGH
**Branch:** cost-pattern
**Epic:** ATTR-EXPR Item 3

---

## Business Goals

### Why This Matters

Item 2 built the extraction and classification machinery for computed attributes. Without pipeline integration, that machinery produces data that is never consumed -- no modules are generated, no YAML entries appear, and formulas like `attribute p_net_kw = p_net_mw * 1000.0` remain invisible to the pipeline. This item is the critical path that turns extraction results into executable code.

### Success Criteria

- [x] FORMULA computed attributes produce synthetic pipeline modules with auto-implementations
- [x] CalcUsage bindings that target FORMULA attributes resolve as MODULE_OUTPUT (not entry point)
- [x] FORMULA attributes removed from design_attributes before ParameterGroupDeriver (no false entry points)
- [x] Computed attribute chains (A depends on B depends on C) resolve in correct topological order
- [x] All existing tests pass with zero regressions (264 tests passing after hardening)
- [x] EXPOSE_PURE backtracker behavior documented (already handled OR alias added)

### Priority

P1 -- critical path for the ATTR-EXPR epic. Items 4 (E2E validation) and 5 (documentation/ADRs) depend on this.

---

## Problem Statement

### Current State

After Item 2:
- `extract_computed_attributes()` classifies PartDef attribute expressions as FORMULA, EXPOSE_PURE, EXPOSE_COMPUTED, LITERAL, or UNRESOLVABLE
- `ComputedAttributeData` carries the compiled Python expression for FORMULA patterns
- The extraction module is a leaf -- it does not import from analysis/, resolution/, or generation/
- The pipeline (`build_pipeline_context()` in `initialization.py`) has no awareness of computed attributes
- The backtracker resolves CalcUsage bindings using calc usages + design attributes only -- a binding to `p_net_kw` (which is FORMULA) falls through to ENTRY_POINT classification
- The graph builder creates `PipelineModule` objects only from `CalcUsageData` -- no mechanism for computed-attribute-sourced modules
- FORMULA attributes remain in the `design_attributes` dict and flow into `ParameterGroupDeriver`, potentially creating false entry points

### Desired Outcome

Running codegen on a model with FORMULA computed attributes produces:
- Synthetic `PipelineModule` entries in the `ComputationGraph`
- Auto-implemented `_impl.py` files with the compiled expression
- TEAx module wrappers with correct input/output schemas
- Pipeline YAML entries with `# source: computed_attribute` comment
- `IMPLEMENTATION_BACKLOG.md` entries showing "auto-implemented"
- Module registry entries in `__init__.py`
- Correct downstream wiring: CalcUsages binding to FORMULA attributes get MODULE_OUTPUT resolution

---

## Scope

### In Scope

1. **Step 4.5 orchestration** in `build_pipeline_context()` (`generation/initialization.py`)
2. **PipelineContext extension** to carry `list[ComputedAttributeData]`
3. **FORMULA removal from design_attributes** before Step 5
4. **Backtracker computed attribute awareness** (`analysis/dependency_backtracker.py`)
5. **Graph builder FORMULA module generation** (`resolution/graph_builder.py`)
6. **Per-part attribute resolution map** for input wiring (literal / expose_alias / formula / entry_point)
7. **`PipelineModule.is_computed_attribute` flag** (`resolution/models.py`)
8. **Code generation for computed attribute modules** (module wrappers, auto-impls, YAML, backlog, registry)
9. **Topological ordering** of computed attribute modules within the existing sort
10. **EXPOSE_PURE backtracker investigation** and documentation
11. **Integration tests** (`tests/integration/test_computed_attribute_pipeline.py`)

### Out of Scope

- EXPOSE_COMPUTED decomposition (deferred -- no concrete modeling need)
- Cross-part attribute references (Phase 3)
- `InvocationExpression` / function call support
- Hierarchy/multiplicity (Phase 3)
- Changes to TEAx runtime or module base classes
- Inline expressions in module wrappers (future optimization)
- E2E validation on real models (Item 4)
- ADR formalization (Item 5)

### Edge Cases & Considerations

- **FORMULA-as-passthrough**: `attribute b = a` (single ref, no operators) classifies as FORMULA. Compiles to `inputs.a`. Generates a trivial passthrough module -- harmless, don't special-case.
- **Member name collision**: SysML prevents CalcUsage and AttributeUsage from sharing the same name on a part. If this assumption proves wrong, module naming needs a type prefix. For now rely on SysML's namespace rules.
- **FORMULA referencing EXPOSE_PURE**: `useful_power = p_fusion * thermal_efficiency` where `thermal_efficiency` is EXPOSE_PURE. The graph builder must resolve `thermal_efficiency` through the alias to the upstream calc output channel.
- **Empty computed attribute list**: If a model has no computed attributes, Step 4.5 produces an empty list and all downstream steps are no-ops.
- **FORMULA compilation failure**: Item 2 already handles this (degrades to `MANUAL_REQUIRED`). Item 3 should skip module generation for `MANUAL_REQUIRED` FORMULA attrs (they don't produce usable code).

---

## Requirements

### Functional Requirements

> Requirements below are from the epic doc and architectural decisions unless marked [INFERRED] or [FROM INVESTIGATION].

#### Pipeline Orchestration

1. **FR-1**: `build_pipeline_context()` MUST execute a new Step 4.5 after Step 4 (design attribute extraction) and before Step 5 (ParameterGroupDeriver). Step 4.5 calls `extract_computed_attributes()` on each PartDef/PartUsage element accessible from the loaded model.

2. **FR-2**: `PipelineContext` MUST have a new field `computed_attributes: list[ComputedAttributeData]` containing all extracted computed attributes (all classifications except LITERAL, which is already excluded by Item 2).

3. **FR-3**: Step 4.5 MUST remove FORMULA-classified attributes from the `design_attributes` dict (keyed by `(owning_part_qualified_name, attribute_name)`) before passing it to Step 5. EXPOSE_PURE, EXPOSE_COMPUTED, and LITERAL attributes MUST remain in `design_attributes`.

4. **FR-4**: [INFERRED] Step 4.5 MUST collect `calc_usage_names` per PartDef/PartUsage (from Step 3's `calc_usages` list) to pass to `extract_computed_attributes()`.

5. **FR-5**: [FROM INVESTIGATION] Step 4.5 needs access to PartDef/PartUsage elements. The `extractor` field on `PipelineContext` provides `extractor.model` (the SysIDE model). The extraction must iterate PartDef/PartUsage elements from the model using the adapter, similar to how `extract_design_attributes()` works.

#### Backtracker Awareness

6. **FR-6**: `DependencyBacktracker.__init__()` MUST accept an optional `computed_attributes: list[ComputedAttributeData]` parameter and build a lookup dict keyed by `(owning_part_qualified_name, attribute_name)` for O(1) resolution.

7. **FR-7**: During `_trace_dependencies()`, when a CalcUsage binding's `source_path` resolves to a part attribute that matches a FORMULA computed attribute, the backtracker MUST resolve it as `MODULE_OUTPUT` from the synthetic module `{part_name}__{attr_name}`, with channel name `{part_name}__{attr_name}__{attr_name}` (PQN format per ADR-003).

8. **FR-8**: The backtracker MUST record FORMULA-sourced MODULE_OUTPUT in `_binding_resolutions` with `BindingResolutionType.MODULE_OUTPUT`, using the computed attribute's synthetic module output channel as the `qualified_name`.

9. **FR-9**: [INFERRED] The backtracker MUST NOT create synthetic `CalcUsageData` objects. Computed attribute modules are generated by the graph builder directly from `ComputedAttributeData` (Option C architecture).

#### Graph Builder

10. **FR-10**: `build_computation_graph()` MUST accept a new parameter `computed_attributes: list[ComputedAttributeData]` and generate a `PipelineModule` for each FORMULA computed attribute with `compilability == FULLY_COMPILABLE`.

11. **FR-11**: Each FORMULA `PipelineModule` MUST have:
    - `name`: `{owning_part_name}__{python_name}` (lowercase, ADR-003)
    - `module_type`: PascalCase derived from the module name
    - `inputs`: One `ModuleInput` per reference in the expression, wired via the attribute resolution map
    - `outputs`: Single `ModuleOutput` with `field_name="root"`, `channel_name="{module_name}__{python_name}"` (PQN format)
    - `execution_order`: Assigned during topological sort
    - `compilability`: `Compilability.FULLY_COMPILABLE`
    - `is_computed_attribute`: `True`

12. **FR-12**: The graph builder MUST build a per-part **attribute resolution map** from the computed attribute list:
    - LITERAL sibling attribute (in `design_attributes`, not a computed attribute) -> entry point
    - FORMULA computed attribute -> upstream synthetic module output channel
    - EXPOSE_PURE computed attribute -> aliased upstream calc output channel (resolved from the EXPOSE attribute's `references` field)
    - Unknown/unresolved -> entry point (conservative default)

13. **FR-13**: Computed attribute modules MUST be included in the topological sort alongside CalcUsage modules. Dependencies between computed attribute modules (chains) and between computed attribute modules and CalcUsage modules MUST be correctly ordered.

14. **FR-14**: The output catalog (`_build_output_catalog`) MUST include computed attribute module outputs so that downstream CalcUsage bindings can wire to them.

#### Data Model

15. **FR-15**: `PipelineModule` in `resolution/models.py` MUST have a new field `is_computed_attribute: bool = False` for provenance marking.

#### Code Generation

16. **FR-16**: Computed attribute modules MUST reuse the existing `auto_implementation.py.jinja2` template for generating `_impl.py` files. The template context MUST be adapted from `ComputedAttributeData` (not `CalcDefCompilationResult`).

17. **FR-17**: Computed attribute modules MUST generate TEAx module wrappers using the existing `teax_module.py.jinja2` template (or a minimal adaptation). Each module has N inputs (one per expression reference) and 1 output (the computed attribute value).

18. **FR-18**: Pipeline YAML entries for computed attribute modules SHOULD include a `# source: computed_attribute` comment for debuggability.

19. **FR-19**: `IMPLEMENTATION_BACKLOG.md` MUST show computed attribute modules as auto-implemented (excluded from the manual implementation count, consistent with Phase 1 auto-implemented CalcDefs).

20. **FR-20**: The module registry (`__init__.py`) MUST include computed attribute modules alongside CalcUsage modules.

#### EXPOSE_PURE Investigation

21. **FR-21**: Item 3 MUST investigate whether the existing backtracker transitive resolution (`_design_attr_binding_index` + `_resolve_binding_to_usage` Strategy 4) already handles the EXPOSE_PURE pattern for CalcUsage bindings. Document findings. If already handled: no code changes needed for EXPOSE_PURE CalcUsage bindings. If not: implement alias resolution.

22. **FR-22**: Regardless of FR-21's outcome, the graph builder MUST handle EXPOSE_PURE for FORMULA module input wiring. When a FORMULA module references an EXPOSE_PURE attribute, the graph builder resolves through the alias to the upstream calc output channel.

---

## Acceptance Criteria

### Core Functionality

- [x] Step 4.5 integrated into `build_pipeline_context()` -- extracts computed attributes from all PartDefs/PartUsages
- [x] FORMULA attributes removed from `design_attributes` before Step 5
- [x] `PipelineContext.computed_attributes` populated correctly
- [x] Backtracker resolves CalcUsage bindings to FORMULA attributes as MODULE_OUTPUT
- [x] Graph builder generates `PipelineModule` for each FULLY_COMPILABLE FORMULA computed attribute
- [x] Computed attribute modules have correct inputs wired from resolution map
- [x] Topological ordering correct for chains (A -> B -> C all computed)
- [x] EXPOSE_PURE behavior documented (already handled by backtracker OR alias added)

### Generation Outputs

- [x] Pipeline YAML includes computed attribute modules in correct execution order
- [x] Auto-implementation files generated with compiled expressions
- [x] TEAx module wrappers generated with correct I/O schemas
- [x] `IMPLEMENTATION_BACKLOG.md` shows computed attribute modules as auto-implemented
- [x] Module registry includes computed attribute modules

### Quality & Integration

- [x] All existing tests pass with zero regressions (264 tests passing after hardening)
- [x] Integration tests cover: simple FORMULA, chain, FORMULA with EXPOSE_PURE input wiring
- [x] `uv run mypy src/` passes on all modified files
- [x] `uv run ruff check src/` passes

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_attribute_expression_capture.md` (ATTR-EXPR Item 3)
- **Architectural Decisions:** `.project/concepts/attr-expr-architectural-decisions.md`
- **Research:** `.project/research/20260202-180000_expression-compilation-and-inline-math-strategy.md`
- **Item 2 Extraction Module:** `src/sysml_codegen/extraction/computed_attribute_extractor.py`
- **Item 2 Data Models:** `src/sysml_codegen/extraction/data_models.py` (ComputedAttributeData, ComputedAttributeClassification)
- **Design:** `.project/active/attr-expr-pipeline/design.md` (to be created)

---

## Key Codebase Facts (from investigation)

These facts were discovered during spec research and constrain the design:

### Item 2 API Surface

- `extract_computed_attributes(adapter, part_element, calc_usage_names)` -> `list[ComputedAttributeData]`
- LITERAL excluded from results; UNRESOLVABLE included with warning
- `ComputedAttributeData.references` is `list[ExpressionRef]` (each has `.name` and `.qualified_name`)
- `ComputedAttributeData.compiled_expression` is the Python expression string (FORMULA only, e.g., `"(inputs.length * inputs.width)"`)
- `ComputedAttributeData.compilability` is `Compilability.FULLY_COMPILABLE` for successful FORMULA compilation, `MANUAL_REQUIRED` for failures
- The extraction does NOT set `source_file` or `source_line` (they default to `Path("unknown")` and `0`) -- this is acceptable for now but may be improved

### Pipeline Context Structure

- `build_pipeline_context()` in `initialization.py` has Steps 1-7 + Step 6.5
- `PipelineContext` is a `@dataclass` (not Pydantic) with 9 fields
- Step 4 returns `dict[Path, list[DesignAttributeData]]` -- keyed by source file path
- `DesignAttributeData` has `qualified_name`, `name`, `parent_part`, `default_value`
- The `extractor.model` provides access to loaded SysML elements

### Backtracker Resolution

- `_trace_dependencies()` iterates `usage.bindings` and calls `_resolve_binding_to_usage(binding.source_path)`
- `_resolve_binding_to_usage()` has 5 strategies: exact output catalog, direct instance, transitive design attr, cross-file, bare instance name
- Strategy 4 (transitive) uses `_design_attr_binding_index` -- populated from design attributes with path references (e.g., `"plant.p_net_kw"` -> `"calc.output"`)
- `_binding_resolutions` is the SINGLE SOURCE OF TRUTH for binding wiring (replaces deprecated `binding_to_entry_point`)
- Key format: `"{usage_qualified_name}|{param_name}"`

### Graph Builder Structure

- `build_computation_graph()` takes: `result`, `calc_defs`, `design_attrs`, `group_deriver`, `compilation_results`
- Step 5 builds `PipelineModule` from `result.required_usages` (already sorted)
- `_build_pipeline_module()` reads from `result.binding_resolutions` -- fail-fast if missing
- `_build_output_catalog()` maps `"{instance_name}.{output_attr}"` -> `(module_type, channel_name, field_name)`
- `_validate_channel_references()` verifies all module_output channels exist

### Generation Templates

- `auto_implementation.py.jinja2` expects: `function_name`, `calc_name`, `input_class_name`, `return_type`, `execution_steps`, `output_expressions`, `output_count`, `single_output_expression`, plus docstring context
- For single-output FORMULA computed attrs, we need: `execution_steps=[]`, `output_count=1`, `single_output_expression=compiled_expression`
- `teax_module.py.jinja2` expects: `class_name`, `input_class_name`, `output_class_name`, `handler_name`, `impl_import_path`, `input_attributes`, `output_attributes`, `package_name`, `is_multioutput`, etc.
- `generate_teax_module()` is CalcDef-specific -- computed attr modules will need either an adapter or a parallel function

### Naming Conventions (ADR-003)

- Module name: `get_module_name(qualified_name)` -> lowercase (e.g., `"probe_design__area"`)
- Channel name: `get_channel_name(module_qn, output_name)` -> `"{module_qn}__{output_name}"` (e.g., `"probe_design__area__area"`)
- Module type: PascalCase from module name via `derive_module_type()` (e.g., `"ProbeDesignAreaModule"`)

---

**Next Steps:** After approval, proceed to `/_my_design`
