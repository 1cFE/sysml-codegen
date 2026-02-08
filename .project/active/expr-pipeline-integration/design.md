# Design: Pipeline Integration -- CalcDef Expression Compilation

**Status:** Implemented
**Owner:** Reid Westwood
**Created:** 2026-02-07 16:12 UTC
**Branch:** cost-pattern (3aacf0e)
**Epic:** EXPR-CODEGEN Item 4

## Overview

Wire the expression compiler module (Item 3) into the extraction→resolution→generation pipeline so that codegen produces auto-implemented `_impl.py` files for compilable CalcDefs instead of `NotImplementedError` stubs.

## Related Artifacts

- **Spec:** `.project/active/expr-pipeline-integration/spec.md`
- **Epic:** `.project/backlog/epic_expression_aware_codegen.md` (Item 4)
- **Concept:** `.project/concepts/expression-aware-codegen.md`
- **Expression Compiler:** `src/sysml_codegen/extraction/expression_compiler.py`
- **Expression Utils:** `src/sysml_codegen/extraction/expression_utils.py`
- **Spike Reports:** `.project/active/expr-spike-ast/report.md`, `.project/active/expr-spike-compile/report.md`

---

## Research Findings

### Files Analyzed

| File | Key Observations |
|------|------------------|
| `extraction/expression_compiler.py` | Complete compiler with 5 data models, `compile_calc_def()` orchestrator, topological sort. Needs `expression_asts`, `all_member_names`, `member_expressions` arguments. |
| `extraction/expression_utils.py` | Shared AST-to-text: `reconstruct_expression()`, `OPERATOR_MAP`, `extract_feature_reference_name()`. Ready to replace `_extract_expression_text()`. |
| `extraction/data_models.py:108-135` | `CalculationDefinitionData` has no `output_expression_asts` field. Plain dataclass (not Pydantic). |
| `extraction/extractor.py:127-191` | `_extract_calculation_definition()` iterates `elem.owned_members` twice. Has access to raw AST via `member.feature_value_expression`. `_extract_expression_text()` at lines 612-634 is legacy partial text reconstruction. |
| `extraction/usage_extractor.py:273-332` | `_extract_single_binding()` handles Chain/Reference/Literal but OperatorExpression falls through to UNBOUND at line 327. |
| `generation/initialization.py:82-174` | `build_pipeline_context()` has 7 steps. `PipelineContext` is a dataclass with 8 fields. Step 6 (backtracker) at line 146, Step 7 (graph builder) at line 158. |
| `resolution/models.py:148-165` | `PipelineModule` is Pydantic BaseModel with 5 fields. No `compilability` field. |
| `resolution/graph_builder.py:49-125` | `build_computation_graph()` takes `result`, `calc_defs`, `design_attrs`, `group_deriver`. Creates modules at line 106 via `_build_pipeline_module()`. |
| `generation/stencils.py:85-151` | `generate_implementation_stencil()` unconditionally uses `implementation_stencil.py.jinja2`. Returns generated code string. |
| `generation/preservation.py:20-61` | `should_regenerate_stencil()` compares function signatures (name, input_type, return_type). Body-agnostic -- works for auto-impl without modification. |
| `cli/__init__.py:206-284` | `_generate_stencils()` iterates `ctx.calc_defs`, calls `generate_implementation_stencil()` per CalcDef. Has smart-regen path. This is where auto-impl vs stub selection happens. |
| `analysis/signature_extractor.py:16-51` | `FunctionSignature` compares `function_name`, `input_type`, `return_type`. Body is not inspected. |
| `templates/implementation_stencil.py.jinja2` | 19-line template: import, function signature, docstring, `raise NotImplementedError(...)`. |
| `agentic_mbse/sysml/types.py` | `BindingType.EXPRESSION` already exists in the enum. `BindingInfo` (agentic-mbse version) has `expression_ast` field. |

### Key Patterns Found

1. **Jinja2 template loading**: `_get_template_env()` in `cli/__init__.py:117-125` loads from `src/sysml_codegen/templates/` via `FileSystemLoader`.

2. **Stencil generation flow**: `_generate_stencils()` iterates `ctx.calc_defs` → for each, determines output path with ADR-003 namespacing → calls `generate_implementation_stencil()` → writes to file. Smart-regen wraps this with preservation check.

3. **`compile_calc_def()` API**: Takes `calc_def`, `expression_asts: dict[str, Any]`, `all_member_names: set[str] | None`, `member_expressions: dict[str, Any] | None`. Returns `CalcDefCompilationResult`. All data must be captured during extraction since the raw syside element is not available at Step 6.5.

4. **Codegen `BindingInfo` vs agentic-mbse `BindingInfo`**: The codegen dataclass at `usage_extractor.py:44-66` does NOT have an `expression_ast` field. The agentic-mbse Pydantic model does. Adding the field to the codegen dataclass is needed for the OperatorExpression fix.

5. **Backlog report**: `generate_backlog_report()` in `stencils.py:188-345` currently lists ALL CalcDefs. Post-integration, it should only list `MANUAL_REQUIRED` CalcDefs.

---

## Design Decisions

| # | Decision | Rationale |
|---|----------|-----------|
| DD-1 | Template dispatch lives in `stencils.py` (`generate_implementation()`), not in CLI | Keeps generation layer self-contained and testable. CLI remains a thin orchestrator handling I/O, paths, and smart-regen. Consistent with existing pattern where CLI delegates to `stencils.py`. |
| DD-2 | `PipelineContext.compilation_results` is typed `dict[str, CalcDefCompilationResult]`, not `dict[str, Any]` | `expression_compiler.py` is a verified leaf module with no upstream dependencies. No circular import risk. `Any` typing would weaken type checking on a field that flows through the entire generation layer. |
| DD-3 | `_extract_expression_text()` MUST be deleted after replacement | Dead code removal prevents confusion about which code path is active. The method has no remaining callers after replacement with `reconstruct_expression()`. |
| DD-4 | `reconstruct_expression()` fallback output filtered via `startswith("<")` check | `str(expr_node)` for unknown syside types produces repr-like strings (`<syside.X object at 0x...>`). Filtering prevents garbage in `calc_expressions`. Unknown types logged at debug level for troubleshooting. |

---

## Proposed Design

### High-Level Architecture

The integration touches 4 layers in a clean data-flow chain:

```
EXTRACTION (Step 2)         ORCHESTRATION (Step 6.5)       RESOLUTION (Step 7)         GENERATION
─────────────────          ────────────────────────        ─────────────────           ──────────
CalculationDefinitionData   compile_calc_def()              PipelineModule              stencils.py:
  + output_expression_asts   → CalcDefCompilationResult      + compilability              generate_implementation()
  + all_member_names                                                                      dispatches auto_impl
  + member_expressions      stored on PipelineContext        set from compilation         vs stub internally
                             .compilation_results             results
```

### Component 1: Extraction Layer Changes

#### 1A. Add AST capture fields to `CalculationDefinitionData`

**File:** `src/sysml_codegen/extraction/data_models.py:108-135`

Add three new fields with defaults (backward-compatible since this is a dataclass with defaults at the end):

```python
@dataclass
class CalculationDefinitionData:
    # ... existing fields (name through source_hash) ...

    # NEW: Raw syside AST nodes for each output attribute's expression.
    # Key: sanitized output attribute name. Value: raw syside AST node.
    # Missing/None = no expression (manual impl required).
    output_expression_asts: dict[str, Any] = field(default_factory=dict)

    # NEW: All owned_member names from the raw CalcDef element.
    # Needed by expression compiler for undeclared intermediate resolution.
    all_member_names: set[str] = field(default_factory=set)

    # NEW: Raw syside AST nodes for non-input/non-output members.
    # Key: sanitized member name. Value: raw syside AST node.
    # Needed for undeclared intermediates (e.g., local variables in CalcDef body).
    member_expressions: dict[str, Any] = field(default_factory=dict)
```

**Why three fields instead of just `output_expression_asts`?** The `compile_calc_def()` function (expression_compiler.py:446) needs `all_member_names` and `member_expressions` to discover and compile undeclared intermediates -- CalcDef members that aren't classified as input or output but are referenced by output expressions. Without these, the 3 CATF intermediates (`thermal_load_cryo`, `pump_power_per_unit`, `thermal_load`) discovered in Item 2 spike cannot be compiled.

#### 1B. Modify `_extract_calculation_definition()` to capture ASTs

**File:** `src/sysml_codegen/extraction/extractor.py:127-191`

During the existing `owned_members` iteration, additionally capture:
1. **Output ASTs**: For each output attribute with `feature_value_expression`, store the raw AST node in `output_expression_asts` keyed by sanitized attribute name.
2. **All member names**: Collect sanitized names of ALL `AttributeUsage` members (input, output, and undeclared) into `all_member_names`.
3. **Member expressions**: For members that are neither input nor output but have `feature_value_expression`, store in `member_expressions`.

This can be done in the existing loops -- no new iteration over `owned_members` needed.

#### 1C. Replace `_extract_expression_text()` with `expression_utils.reconstruct_expression()`

**File:** `src/sysml_codegen/extraction/extractor.py:612-634`

Replace the call at line 158:
```python
# BEFORE:
expr_text = self._extract_expression_text(expr)

# AFTER:
from sysml_codegen.extraction.expression_utils import reconstruct_expression
expr_text = reconstruct_expression(expr)
```

The `expression_utils.reconstruct_expression()` function handles the same node types plus additional ones (FeatureChainExpression, LiteralBoolean, LiteralString, NullExpression).

**Dead code removal:** After this replacement, `_extract_expression_text()` (extractor.py:612-634) MUST be deleted. It is dead code with no remaining callers.

**Fallback behavior:** `reconstruct_expression()` returns `str(expr_node)` for unhandled node types, which produces repr-like strings (e.g., `<syside.OperatorExpression object at 0x...>`). This would produce garbage `calc_expressions` entries like `attr_name = <syside...>`. To prevent this, the calling code at line 159 MUST filter using a check that rejects repr-like output:

```python
# BEFORE:
if expr_text and expr_text != "???":

# AFTER:
if expr_text and not expr_text.startswith("<"):
```

This filters out Python repr strings (which always start with `<`) while accepting all legitimate expression text. A `logger.debug()` call SHOULD be added when a repr-like string is filtered, to aid troubleshooting if new node types are encountered in future models.

#### 1D. Fix OperatorExpression binding classification

**File:** `src/sysml_codegen/extraction/usage_extractor.py:327-332`

Add `OperatorExpression` handling before the UNBOUND fallthrough:

```python
# BEFORE (line 316-332):
elif _is_literal_expression(expr):
    ...

return BindingInfo(
    param_name=param_name,
    source_path=None,
    binding_type=BindingType.UNBOUND,
    raw_expression=f"Unknown expression type: {type(expr).__name__}",
)

# AFTER:
elif _is_literal_expression(expr):
    ...

elif SysideAdapter.is_instance(expr, "OperatorExpression"):
    return BindingInfo(
        param_name=param_name,
        source_path=None,
        binding_type=BindingType.EXPRESSION,
        raw_expression=f"OperatorExpression: {type(expr).__name__}",
        expression_ast=expr,  # Store raw AST for Phase 2
    )

return BindingInfo(...)
```

This also requires adding an `expression_ast` field to the codegen `BindingInfo` dataclass:

**File:** `src/sysml_codegen/extraction/usage_extractor.py:44-66`

```python
@dataclass
class BindingInfo:
    # ... existing fields ...
    literal_value: float | int | str | bool | None = None

    # NEW: Raw AST node for EXPRESSION bindings (Phase 2 will use this)
    expression_ast: Any = None
```

### Component 2: Pipeline Orchestration (Step 6.5)

#### 2A. Add Step 6.5 to `build_pipeline_context()`

**File:** `src/sysml_codegen/generation/initialization.py:82-174`

Between Step 6 (line 155) and Step 7 (line 158), insert Step 6.5:

```python
# Step 6.5: Compile expressions and classify compilability
from sysml_codegen.extraction.expression_compiler import (
    CalcDefCompilationResult,
    compile_calc_def,
)

compilation_results: dict[str, CalcDefCompilationResult] = {}
for calc_def in calc_defs:
    if calc_def.output_expression_asts:
        result = compile_calc_def(
            calc_def=calc_def,
            expression_asts=calc_def.output_expression_asts,
            all_member_names=calc_def.all_member_names or None,
            member_expressions=calc_def.member_expressions or None,
        )
        compilation_results[calc_def.name] = result
```

**Why after backtracking?** Per concept Section 3.2: the compiler needs confirmed knowledge of which names are inputs vs intermediates. The backtracker resolves all bindings in Step 6. However, note that `compile_calc_def()` uses `calc_def.input_attributes` and `calc_def.output_attributes` for reference resolution -- it does NOT use `backtracking_result.binding_resolutions`. The backtracking dependency is conceptual (ensuring the pipeline is valid), not a data dependency. The compiler could theoretically run at Step 2.5, but Step 6.5 placement follows the concept specification and keeps the ordering principle that analysis precedes classification.

#### 2B. Add `compilation_results` to `PipelineContext`

**File:** `src/sysml_codegen/generation/initialization.py:54-79`

Add a top-level import of `CalcDefCompilationResult` and a new field to the dataclass:

```python
from sysml_codegen.extraction.expression_compiler import CalcDefCompilationResult

@dataclass
class PipelineContext:
    # ... existing fields ...
    computation_graph: ComputationGraph

    # NEW: Expression compilation results keyed by calc_def.name.
    # Contains per-output CompilationResult with Python expression strings.
    # Used by generation layer to select auto-impl vs stub template.
    compilation_results: dict[str, CalcDefCompilationResult] = field(default_factory=dict)
```

**Typing rationale:** `CalcDefCompilationResult` is imported directly, not typed as `Any`. The `expression_compiler.py` module is a leaf with no upstream dependencies (verified: it only imports from `agentic_mbse` and `expression_utils`), so there is no circular import risk. The `extractor: Any` pattern in `PipelineContext` exists only because `SysMLDataExtractor` imports from `extraction/data_models.py` which is also imported by `initialization.py` -- a genuine circular import concern that does not apply here.

#### 2C. Pass `compilation_results` to graph builder

Modify the Step 7 call:

```python
# Step 7: Build ComputationGraph (single source of truth)
computation_graph = build_computation_graph(
    result=backtracking_result,
    calc_defs=calc_defs,
    design_attrs=design_attrs,
    group_deriver=group_deriver,
    compilation_results=compilation_results,  # NEW
)
```

### Component 3: Resolution Layer Changes

#### 3A. Add `compilability` to `PipelineModule`

**File:** `src/sysml_codegen/resolution/models.py:148-165`

```python
from sysml_codegen.extraction.expression_compiler import Compilability

class PipelineModule(BaseModel):
    name: str
    module_type: str
    inputs: list[ModuleInput]
    outputs: list[ModuleOutput]
    execution_order: int
    compilability: Compilability = Compilability.UNKNOWN  # NEW
```

**Import note:** This creates a dependency from `resolution/models.py` → `extraction/expression_compiler.py`. The expression_compiler is a leaf module with no upstream dependencies within the package, so no circular import risk.

#### 3B. Set compilability in `build_computation_graph()`

**File:** `src/sysml_codegen/resolution/graph_builder.py:49-125`

Add `compilation_results` parameter (defaulting to `None` for backward compatibility):

```python
def build_computation_graph(
    result: BacktrackingResult,
    calc_defs: list,
    design_attrs: dict[Path, list[DesignAttributeData]],
    group_deriver: ParameterGroupDeriver,
    compilation_results: dict | None = None,  # NEW
) -> ComputationGraph:
```

In Step 5 (module building loop, line 98), after `_build_pipeline_module()` returns, set compilability:

```python
for idx, usage in enumerate(result.required_usages):
    calc_def = calc_def_map.get(usage.calc_def_name)
    # ...
    module = _build_pipeline_module(...)

    # NEW: Set compilability from compilation results
    if compilation_results and usage.calc_def_name in compilation_results:
        module.compilability = compilation_results[usage.calc_def_name].overall_compilability

    modules.append(module)
```

**Note:** `PipelineModule` is a Pydantic model, so `module.compilability = ...` works via Pydantic's attribute setter. The default `UNKNOWN` stays for CalcDefs that weren't compiled (no ASTs).

**Key invariant:** `compilation_results` is keyed by `calc_def.name`. The graph builder looks up results via `usage.calc_def_name`. This works because `usage.calc_def_name` is populated from the same CalcDef's `name` field during extraction (`usage_extractor.py:200`), and the `calc_def_map` in `build_computation_graph()` is also keyed by `calc_def.name` (graph_builder.py:70). All three keys reference the same sanitized CalcDef name, so the lookup is correct. Multiple CalcUsages referencing the same CalcDef will share a single `CalcDefCompilationResult` -- which is correct since compilability is a property of the CalcDef's expressions, not the usage.

### Component 4: Generation Layer Changes

#### 4A. New auto-implementation template

**File:** `src/sysml_codegen/templates/auto_implementation.py.jinja2` (NEW)

This template generates actual computation code instead of `NotImplementedError`. Structure follows the existing `implementation_stencil.py.jinja2` pattern (same function signature) but replaces the `raise` with computation logic:

```jinja2
"""Auto-generated implementation for {{ calc_name }}.

AUTO_IMPLEMENTED = True

SysML Source: {{ sysml_source }}

SysML Expressions:
{% for expr in sysml_expressions %}
    {{ expr }}
{% endfor %}
"""

AUTO_IMPLEMENTED = True

from {{ package_name }}.modules.{{ module_import_path }} import {{ input_class_name }}


def {{ function_name }}(inputs: {{ input_class_name }}) -> {{ return_type }}:
    """{{ docstring }}"""
{% for step in execution_steps %}
{% if step.is_undeclared_intermediate %}
    {{ step.name }} = {{ step.expression }}
{% endif %}
{% endfor %}
{% if output_count == 1 %}
    return {{ single_output_expression }}
{% else %}
    return (
{% for step in execution_steps %}
{% if not step.is_undeclared_intermediate %}
        {{ step.expression }},  # {{ step.name }}
{% endif %}
{% endfor %}
    )
{% endif %}
```

**Key design decisions:**
- `AUTO_IMPLEMENTED = True` as module-level constant (concept Section 3.6)
- Same function signature as stub template (preserves preservation.py compatibility)
- Undeclared intermediates emitted as local variables before the return statement
- Single-output: bare `return expression`; multi-output: `return (expr1, expr2, ...)`
- Execution steps follow topological order from `CalcDefCompilationResult.execution_order`

#### 4B. Unified generation function with internal dispatch

**File:** `src/sysml_codegen/generation/stencils.py`

The template selection logic (auto-impl vs stub) belongs in `stencils.py`, not in the CLI. This keeps the generation layer self-contained and testable without CLI context, consistent with the existing pattern where the CLI is a thin orchestrator.

Add a unified entry point that internally dispatches:

```python
def generate_implementation(
    calc_def: CalculationDefinitionData,
    template_env: jinja2.Environment,
    output_path: Path,
    package_name: str = "generated_code",
    compilation_result: CalcDefCompilationResult | None = None,
) -> str:
    """Generate implementation file for a CalcDef.

    Dispatches to auto-implementation template for FULLY_COMPILABLE CalcDefs,
    or to NotImplementedError stub template for all others.

    Args:
        calc_def: Calculation definition to implement
        template_env: Jinja2 environment
        output_path: Where to write handwritten/ file
        package_name: Package name for imports
        compilation_result: Compilation result from Step 6.5, or None

    Returns:
        Generated Python code
    """
    is_auto_impl = (
        compilation_result is not None
        and compilation_result.overall_compilability == Compilability.FULLY_COMPILABLE
    )

    # Build shared context (function name, signature, docstring, etc.)
    context = _build_stencil_context(calc_def, output_path, package_name)

    if is_auto_impl:
        # Add auto-impl-specific context
        context.update(_build_auto_impl_context(compilation_result, calc_def))
        template = template_env.get_template("auto_implementation.py.jinja2")
    else:
        template = template_env.get_template("implementation_stencil.py.jinja2")

    code = template.render(**context)
    if not code.endswith('\n'):
        code += '\n'
    return code
```

**Helper functions:**
- `_build_stencil_context(calc_def, output_path, package_name) -> dict`: Extracts the shared template context (function_name, calc_name, sysml_source, input_params, output_names, return_type, docstring, input_class_name, module_import_path, package_name). Refactored from the existing `generate_implementation_stencil()` body.
- `_build_auto_impl_context(compilation_result, calc_def) -> dict`: Builds `execution_steps` list from `compilation_result.output_results` in topological order, `output_count`, `single_output_expression`.

The existing `generate_implementation_stencil()` is preserved for backward compatibility but refactored to call `_build_stencil_context()` internally.

**`PARTIALLY_COMPILABLE` handling (FR-12):** Falls through to stub generation (conservative). Only `FULLY_COMPILABLE` gets the auto-impl template.

#### 4C. CLI calls unified generation function

**File:** `src/sysml_codegen/cli/__init__.py:206-284`

The CLI's `_generate_stencils()` is simplified -- it no longer contains dispatch logic. It calls the unified `generate_implementation()` function, passing the compilation result (or None):

```python
from sysml_codegen.generation.stencils import generate_implementation

for calc_def in ctx.calc_defs:
    if not calc_def.output_attributes:
        continue

    # ... existing path computation (unchanged) ...

    # Look up compilation result (may be None if no ASTs)
    compilation_result = ctx.compilation_results.get(calc_def.name)

    # Smart regeneration logic (existing pattern, unchanged)
    if config.smart_regen and output_path.exists():
        should_regen, reason = should_regenerate_stencil(calc_def, output_path)
        if should_regen:
            backup_implementation(output_path, backup_dir)
            code = generate_implementation(
                calc_def, template_env, output_path, config.package_name,
                compilation_result=compilation_result,
            )
            if code:
                output_path.write_text(code)
            # ... stats ...
    # ... same pattern for non-smart-regen and fresh generation paths ...
```

The CLI remains a thin orchestrator: it handles file I/O, path computation, smart-regen decisions, and stats. All generation logic (including template dispatch) lives in `stencils.py`.

#### 4D. Update backlog report to exclude auto-implemented CalcDefs

**File:** `src/sysml_codegen/generation/stencils.py:188-345`

`generate_backlog_report()` should accept `compilation_results` and exclude CalcDefs that are `FULLY_COMPILABLE`:

```python
def generate_backlog_report(
    calc_defs: list[CalculationDefinitionData],
    output_path: Path,
    package_name: str = "generated_code",
    compilation_results: dict | None = None,  # NEW
) -> str:
```

In the items loop, skip CalcDefs whose compilation result is `FULLY_COMPILABLE`. This ensures the backlog only lists genuinely manual work, per epic success criteria.

### Component 5: Preservation Verification

No changes to `preservation.py` or `signature_extractor.py`. The auto-implementation template MUST produce the same function signature as the stub template:
- Same `function_name`: `run_{calc_def.name.lower()}`
- Same `input_type`: `{calc_def.name}Input`
- Same `return_type`: `float` or `tuple[float, ...]`

This ensures:
- Auto-gen → hand-edit → re-gen: signature match → preserves user edit
- Auto-gen → SysML change → re-gen: signature mismatch → backup + regenerate
- Stub → auto-impl upgrade: same signature → preserves existing stub (intentional -- if a user already filled in the stub, we don't overwrite with auto-impl)

**Important edge case:** When upgrading from stub to auto-impl on a *fresh* regeneration (no `--smart-regen`), the existing stub is simply overwritten. This is correct because without smart-regen, all files are regenerated from scratch.

---

## Potential Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Circular import from `resolution/models.py` → `extraction/expression_compiler.py` | Build failure | Verified: expression_compiler.py is a leaf module with no upstream dependencies. No circular risk. |
| `compile_calc_def()` produces syntactically invalid Python | Auto-impl files have syntax errors | The compiler already validates every expression via `python_ast.parse()` (expression_compiler.py:212-217). Additionally, the auto-impl template produces a complete function that should be validated as a whole. |
| Smart-regen preserves old stub when CalcDef becomes compilable | Users don't get auto-impl | By design -- preservation means the existing file (which works) is kept. Users delete the file and re-run to get auto-impl. Per concept Section 3.6: this is correct behavior. |
| `output_expression_asts` capture misses some members | Compiler can't find undeclared intermediates | Capture ALL `AttributeUsage` members' names and expressions, not just inputs/outputs. The `all_member_names` and `member_expressions` fields ensure complete coverage. |
| Existing tests break due to new fields on data models | Test failures | All new fields have defaults (`field(default_factory=...)`) so existing test construction is unaffected. |
| Backlog report changes break downstream consumers | Report format changes | Only items are filtered (auto-implemented excluded). Format and structure unchanged. |

---

## Integration Strategy

### Execution Order

Changes should be implemented in dependency order:

1. **Data model additions** (data_models.py, usage_extractor.py BindingInfo) -- no behavioral change, just new defaulted fields
2. **Extraction changes** (extractor.py) -- capture ASTs during existing extraction, replace `_extract_expression_text()`, delete `_extract_expression_text()` method
3. **OperatorExpression fix** (usage_extractor.py) -- small fix, can be tested independently
4. **Resolution model update** (models.py) -- add `compilability` field with default
5. **Graph builder update** (graph_builder.py) -- accept and apply compilation results
6. **Pipeline orchestration** (initialization.py) -- Step 6.5 + `PipelineContext` update (properly typed)
7. **Auto-impl template + unified dispatch** (new .jinja2 file, stencils.py `generate_implementation()` with internal dispatch)
8. **CLI integration** (cli/__init__.py) -- call `generate_implementation()` passing compilation_result (thin orchestrator, no dispatch logic)
9. **Backlog report update** (stencils.py) -- filter auto-implemented CalcDefs

Steps 1-3 can proceed independently. Steps 4-5 depend on the expression_compiler import. Steps 6-9 depend on all previous steps.

### Backward Compatibility

- All new data model fields have defaults → existing code unaffected
- `build_computation_graph()` gets `compilation_results=None` default → existing callers work
- `generate_backlog_report()` gets `compilation_results=None` default → existing callers work
- `PipelineModule.compilability` defaults to `UNKNOWN` → existing serialized graphs are compatible

---

## Validation Approach

### Unit Tests

1. **Extraction tests**: Verify `output_expression_asts`, `all_member_names`, `member_expressions` are populated during extraction. Mock a CalcDef element with known members and verify capture.

2. **OperatorExpression fix test**: Construct a mock param_elem with OperatorExpression `feature_value_expression`, verify `_extract_single_binding()` returns `BindingType.EXPRESSION`.

3. **Step 6.5 test**: Construct a `CalculationDefinitionData` with populated `output_expression_asts`, call `compile_calc_def()`, verify `CalcDefCompilationResult` has correct `overall_compilability` and `output_results`.

4. **Graph builder test**: Pass `compilation_results` to `build_computation_graph()`, verify `PipelineModule.compilability` is set correctly.

5. **Auto-impl template test**: Render the auto-implementation template with known inputs, verify output is syntactically valid Python (parse with `ast.parse()`).

6. **Unified dispatch test**: Call `generate_implementation()` with a `FULLY_COMPILABLE` compilation result and verify auto-impl output. Call with `None` and verify stub output. Call with `MANUAL_REQUIRED` and verify stub output. All tests target `stencils.py` directly (no CLI dependency).

### Integration Tests

1. **Chain_spike model**: Run full `build_pipeline_context()` on chain_spike model, verify all 3 CalcDefs have `FULLY_COMPILABLE` compilation results and auto-impl code is generated.

2. **Preservation lifecycle**: Generate auto-impl, modify the file, re-run with `--smart-regen`, verify the modified file is preserved (signature match).

### Success Criteria (from spec)

- [ ] `CalculationDefinitionData` has `output_expression_asts` field populated
- [ ] `PipelineContext` has `compilation_results` populated by Step 6.5
- [ ] `PipelineModule` has `compilability` field set from compilation results
- [ ] Codegen on chain_spike produces `_impl.py` with actual code for all 3 CalcDefs
- [ ] `usage_extractor._extract_single_binding()` classifies `OperatorExpression` as `BindingType.EXPRESSION`
- [ ] Auto-impl template produces syntactically valid Python with `AUTO_IMPLEMENTED = True`
- [ ] Stub template still used for `MANUAL_REQUIRED` and `UNKNOWN` CalcDefs
- [ ] All existing tests pass with zero regressions

---

**Next Step:** After approval → `/_my_plan` or `/_my_implement`
