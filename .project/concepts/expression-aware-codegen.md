# Design Concept: Expression-Aware Codegen

**Status**: Draft
**Date**: 2026-02-03
**Authors**: Reid + Claude
**Supersedes**: N/A
**Related**: ADR-001 (Entry Points), ADR-002 (Calc Architecture), ADR-003 (Signal Identifiers)

---

## 1. Vision

> Codegen should generate **executable code**, not just wiring scaffolding. When a
> SysML expression is fully resolvable to input parameters, the generated module
> should contain the actual computation -- no handwritten `_impl.py` needed.
> Additionally, simple attribute-level formulas should not require full `calc def`
> blocks at all.

---

## 2. Core Design Principles

### Principle 1: Two Module Archetypes

All pipeline computation falls into exactly two archetypes:

| Archetype | Source | Module file | Impl file | Who writes the math |
|-----------|--------|-------------|-----------|---------------------|
| **Calc Module** | `calc def` + `calc` usage | `modules/{lib}/{calc}.py` | `handwritten/{lib}/{calc}_impl.py` | Expression compiler OR human |
| **Computed Attribute** | `attribute x = expr` on a part | `modules/{part}__{attr}.py` | None (inline) | Always expression compiler |

A Calc Module always follows the current `validate_and_fill_default` / `run` /
lazy-import-impl pattern. The only change is that `_impl.py` may be
**auto-generated** instead of a `NotImplementedError` stub.

A Computed Attribute is a lighter-weight self-contained module where the
expression is inlined directly in `run()`. No separate `_impl.py` file.

### Principle 2: The Compiler Classifies, Never Guesses

Every expression gets a **compilability verdict** before code is emitted.
Verdicts use a `Compilability` enum (matching codebase conventions like
`EntryPointType(str, Enum)` and `BindingResolutionType(str, Enum)`):

```python
class Compilability(str, Enum):
    FULLY_COMPILABLE = "fully_compilable"
    PARTIALLY_COMPILABLE = "partially_compilable"
    MANUAL_REQUIRED = "manual_required"
```

| Verdict | Meaning | Action |
|---------|---------|--------|
| `FULLY_COMPILABLE` | All operand references resolve to declared inputs or constants | Auto-generate implementation |
| `PARTIALLY_COMPILABLE` | Some references resolve, others are unknown | Generate stub with partial code + TODOs |
| `MANUAL_REQUIRED` | Contains unsupported constructs (conditionals, unknown functions, sum-over-collection) | Generate `NotImplementedError` stub (current behavior) |

If the classifier can't prove an expression is safe, it falls back to the
current stub pattern. **No silent wrong code.**

### Principle 3: CalcDef Expressions Stay in `_impl.py`

Calc defs are the "library" -- reusable, testable units of computation. Even
when auto-implemented, their math lives in `_impl.py` so that:

- A human can override any auto-implementation by editing the file
- The `preservation.py` smart-regen detects edits and preserves them
- The module wrapper (`modules/`) remains a pure TEAx adapter, never
  containing domain logic
- Testing follows the existing pattern: import `_impl`, call with inputs,
  check outputs

Attribute expressions are different. They're one-off formulas tied to a specific
design part. There's no "library" reuse story. They inline in the module.

### Principle 4: Preserve All Existing Data Model Contracts

The expression compiler is a **new producer** feeding into the same consumer
chain. The `ComputationGraph` remains the single source of truth.
`binding_resolutions` remains authoritative. No downstream code changes.

```
                        EXISTING PIPELINE (build_pipeline_context)
                        ==========================================
Step 1: Load SysML models via SysideAdapter
Step 2: extract_calculation_definitions() → list[CalculationDefinitionData]
          + NEW: populate output_expression_asts on each CalcDef
Step 3: extract_calculation_usages() → list[CalcUsageData]
Step 3.5: [Phase 2] extract_computed_attributes() → list[ComputedAttributeData]
          + Generate synthetic CalcUsages, merge into usages list
Step 4: extract_design_attributes() → dict[Path, list[DesignAttributeData]]
Step 5: ParameterGroupDeriver(design_attrs, usages, calc_defs)
Step 6: DependencyBacktracker.find_required_modules() → BacktrackingResult
Step 6.5: classify_compilability(calc_defs, backtracking_result)
          + NEW: for each CalcDef, compile expressions, annotate verdicts
          + Runs AFTER backtracking because it needs resolved input names
            to verify that all expression refs map to declared inputs
Step 7: build_computation_graph() → ComputationGraph
          + NEW: attach compiled_expressions + compilability to PipelineModule
```

**Why Step 6.5?** The compiler needs two things: (1) the raw expression ASTs
(from Step 2), and (2) confirmed knowledge of which names are inputs vs
intermediates. The backtracker in Step 6 resolves all bindings, confirming
what each CalcUsage's inputs are. Only after that can the compiler verify
that every `FeatureReferenceExpression` in an output expression maps to a
declared input or sibling output. Running compilation before backtracking
would risk classifying expressions as compilable when they reference names
that the backtracker later determines are unresolvable.

```
                        NEW ADDITIONS SUMMARY
                        =====================
  Extraction (Steps 2-3.5):
    + ExpressionAST capture on CalcDefs       <-- new field on existing model
    + ComputedAttribute extraction from parts <-- new extraction pass [Phase 2]
    + Synthetic CalcUsage generation          <-- feeds existing pipeline [Phase 2]

  Analysis (Step 6.5):
    + Expression compilability classification <-- new step, after backtracking

  Resolution (Step 7):
    + compiled_expressions on PipelineModule  <-- new field, optional

  Generation:
    + Auto-impl template for _impl.py        <-- new template
    + Self-contained module template          <-- new template [Phase 2]
```

### Principle 5: Expression Patterns Are Finite and Enumerable

From analysis of every `.sysml` file across fusion-tea, fusion_modeling, and
test fixtures, the complete set of expression constructs actually used is:

| Construct | Frequency | Example |
|-----------|-----------|---------|
| Binary arithmetic (`+`,`-`,`*`,`/`) | Very common | `wattage * cost_per_watt` |
| Power (`**`) | Occasional | `(1 + rate) ** lifetime` |
| Parenthesized grouping | Common | `(a + b) * c` |
| Literal constants | Very common | `3.14159`, `8760.0`, `1.0` |
| Feature references (inputs) | Very common | `wattage`, `p_fusion` |
| Multi-step intermediates | Common | `temp = a * b; result = temp + c` |
| Unit annotations (`[m]`) | Rare (1 file) | `3.0 [m]` |
| `sum()` over collections | Occasional | `sum(heater.capital_cost)` |
| Conditional `if/else` | Rare (1 file) | `if fuel_type == DT? ...` |
| `sqrt`, `sin`, `cos`, etc. | **Never observed** | -- |

The compiler needs to handle the top 6 constructs (covers >95% of expressions).
Unit annotations are stripped at extraction (already handled). `sum()`,
conditionals, and math functions are classified as `MANUAL_REQUIRED` initially.

---

## 3. Data Models

### 3.1 Existing Models (Unchanged)

These models retain their current structure and contracts. References are to the
authoritative DATA_FLOW_SPECIFICATION.md definitions.

| Model | Location | Role |
|-------|----------|------|
| `BindingType` | `agentic_mbse.sysml.types` | Enum: CHAIN, REFERENCE, LITERAL, EXPRESSION, UNBOUND |
| `BindingInfo` (agentic-mbse) | `agentic_mbse.sysml.types:170` | Pydantic model with `expression_ast`, `references` |
| `BindingInfo` (codegen) | `usage_extractor.py:44` | Dataclass with `source_instance_elem`, `raw_expression` |
| `CalcUsageData` | `usage_extractor.py:83` | Calc usage instance with bindings, unbound_params |
| `CalculationDefinitionData` | `data_models.py:107` | Calc def with inputs, outputs, `calc_expressions` |
| `DesignAttributeData` | `parameter_groups.py:47` | Design attribute with qualified_name, default_value |
| `BindingResolution` | `core/models.py:31` | Resolution result: ENTRY_POINT or MODULE_OUTPUT |
| `BacktrackingResult` | `dependency_backtracker.py` | `binding_resolutions` dict + entry_points + required_usages |
| `ComputationGraph` | `resolution/models.py:168` | SSOT: modules + entry_point_groups + execution_order |
| `PipelineModule` | `resolution/models.py:148` | Module with inputs (InputSource) and outputs (ModuleOutput) |

### 3.2 Extended Models (New Fields on Existing)

#### `CalculationDefinitionData` -- add expression ASTs

```python
@dataclass
class CalculationDefinitionData:
    # ... existing fields ...
    calc_expressions: list[str]          # EXISTING: raw text strings

    # NEW: structured AST for each output attribute's expression
    output_expression_asts: dict[str, Any] = field(default_factory=dict)
    #   key: output attribute name (e.g., "material_cost")
    #   value: raw syside AST node (OperatorExpression, etc.)
    #   None/missing = no expression found (manual impl required)
```

**Why a dict keyed by output name?** A multi-output CalcDef like PVModuleCostCalc
has 5 separate output expressions. They must be compiled individually and may
have different compilability verdicts (e.g., 4 compile, 1 needs manual).

#### `PipelineModule` -- add compilability metadata

```python
class PipelineModule(BaseModel):
    # ... existing fields ...

    # NEW: expression compilation metadata
    compilability: Compilability = Compilability.MANUAL_REQUIRED
    is_computed_attribute: bool = False
    #   True if this module was synthesized from an attribute expression,
    #   False if it came from a CalcDef+CalcUsage pair
```

**Note**: `compiled_expressions` are NOT stored on `PipelineModule`. The
resolution model should only carry the compilability verdict -- the actual
expression strings are passed directly from the compiler to the generator
via the `PipelineContext`, keeping resolution free of generation concerns.
See Section 3.3 for the `CalcDefCompilationResult` model that carries
expression strings alongside the `PipelineContext`.

### 3.3 New Models

#### `ExpressionNodeType` and `ExpressionAST` -- compiler's working representation

```python
class ExpressionNodeType(str, Enum):
    """Node types in the compiler's intermediate representation."""
    BINARY_OP = "binary_op"
    UNARY_OP = "unary_op"
    LITERAL = "literal"
    INPUT_REF = "input_ref"
    INTERMEDIATE_REF = "intermediate_ref"
    UNSUPPORTED = "unsupported"


@dataclass
class ExpressionAST:
    """Compiler's intermediate representation of a SysML expression.

    This is NOT stored long-term. It's constructed during compilation,
    used to produce a Python expression string, then discarded.
    """
    node_type: ExpressionNodeType

    # For BINARY_OP / UNARY_OP
    operator: str | None = None          # "+", "-", "*", "/", "**"
    left: "ExpressionAST | None" = None
    right: "ExpressionAST | None" = None  # None for unary

    # For LITERAL
    value: float | int | str | None = None

    # For INPUT_REF (resolved to a calc def input parameter)
    input_name: str | None = None        # e.g., "wattage"

    # For INTERMEDIATE_REF (resolved to a sibling output in same calc def)
    intermediate_name: str | None = None  # e.g., "material_cost"

    # For UNSUPPORTED
    raw_text: str | None = None          # best-effort text for stub comment
    reason: str | None = None            # why it's unsupported
```

**Design rationale**: The syside AST nodes are opaque objects with
duck-typed attributes. The `ExpressionAST` is a clean, testable intermediate
form that the compiler can reason about without touching syside. This
follows the project's key learning from ADR-003: *don't let downstream code
touch raw AST; extract structured data once and pass it forward.*

#### `CompilationResult` and `CalcDefCompilationResult` -- output of expression compiler

```python
@dataclass
class CompilationResult:
    """Result of compiling one output attribute's expression."""
    output_name: str                     # e.g., "material_cost"
    compilability: Compilability          # uses the same enum everywhere
    python_expression: str | None = None # e.g., "inputs.wattage * inputs.cost_per_watt"
    input_refs: list[str] = field(default_factory=list)
    #   Input parameter names referenced (for validation)
    intermediate_refs: list[str] = field(default_factory=list)
    #   Sibling output names referenced (for ordering)
    unsupported_reason: str | None = None


@dataclass
class CalcDefCompilationResult:
    """Aggregate compilation result for an entire CalcDef.

    Carried alongside PipelineContext from Step 6.5 to generation.
    Keyed by calc_def.name so the generator can look up expression
    strings without them living on the resolution model.
    """
    calc_def_name: str
    overall_compilability: Compilability  # worst-case across all outputs
    output_results: list[CompilationResult]
    #   One per output attribute, in topological order (dependencies first)
    execution_order: list[str]
    #   Output names in dependency order for code emission
```

**Vocabulary alignment**: The `Compilability` enum is used consistently on
`CompilationResult.compilability`, `CalcDefCompilationResult.overall_compilability`,
and `PipelineModule.compilability`. No separate "verdict" terminology.

#### `ComputedAttributeData` -- extracted from part attribute expressions

```python
@dataclass
class ComputedAttributeData:
    """An attribute on a PartDef/PartUsage that has a computable expression.

    Discovered during a new extraction pass over parts. Each one becomes
    a synthetic CalcUsage feeding into the existing pipeline.
    """
    attribute_name: str                  # e.g., "volume"
    owning_part_name: str                # e.g., "blanket"
    owning_part_qualified_name: str      # e.g., "CATFDesign__blanket"
    expression_ast: Any                  # raw syside AST
    referenced_names: list[str]          # ["r_outer", "r_inner", "h"]
    source_file: Path
    source_line: int

    # After compilation:
    compiled_expression: str | None = None  # "3.14159 * (inputs.r_outer**2 - ...)"
    compilability: Compilability = Compilability.MANUAL_REQUIRED
```

### 3.4 Data Flow Diagram

```
SysML Model Files
       |
       v
  Step 1: Load models
       |
       v
  Step 2: extract_calculation_definitions()
       |  + NEW: populate output_expression_asts
       v
  CalcDefs (with ASTs)
       |
       v
  Step 3: extract_calculation_usages()
       |
       |    Step 3.5 [Phase 2]: extract_computed_attributes()
       |         |
       |         v
       |    ComputedAttributeData
       |         |
       |         | generate synthetic CalcUsages
       |         v
       +-------> merged CalcUsages list
       |
       v
  Step 4: extract_design_attributes()
       |
       v
  Step 5: ParameterGroupDeriver
       |
       v
  Step 6: DependencyBacktracker → BacktrackingResult
       |
       v
  Step 6.5: classify_compilability()                    <-- NEW
       |    For each CalcDef: compile expressions,
       |    verify refs against resolved bindings,
       |    produce CalcDefCompilationResult
       v
  dict[str, CalcDefCompilationResult]
       |
       v
  Step 7: build_computation_graph()
       |  + annotate PipelineModule.compilability
       v
  ComputationGraph + compilation_results
       |
       v
  Generation (conditional: auto-impl vs stub vs inline)
       |
       v
  Generated Code
    modules/        <-- module wrappers (unchanged shape)
    handwritten/    <-- _impl.py: auto-generated OR stub
    pipelines/      <-- YAML (unchanged)
    schemas/        <-- (unchanged)
    inputs/         <-- JSON (unchanged)
```

The `CalcDefCompilationResult` dict is stored on `PipelineContext` alongside
the `ComputationGraph`. The generator looks up expression strings by
`calc_def_name` when rendering `_impl.py` files. This keeps the resolution
model (`PipelineModule`) clean -- it only carries the `Compilability` enum
for downstream decision-making, not the expression strings themselves.

### 3.5 Consolidation: Existing Expression Code

After Phase 1, the codebase has had multiple AST-walking paths. This section
specifies which survive and which are replaced.

| Code Path | Location | Fate | Rationale |
|-----------|----------|------|-----------|
| `extractor._extract_expression_text()` | `extractor.py:612-634` | **REPLACED** by shared utility | Currently partial (only OperatorExpression + FeatureReference). Replaced by the expression compiler's `ast_to_python()` for CalcDef expression text. |
| `constraint_extractor._reconstruct_expression()` | `constraint_extractor.py:137-257` | **EXTRACTED** into shared utility | Most complete AST-to-text logic. The core recursive dispatcher, operator map, and helper functions are extracted into `extraction/expression_utils.py`. The constraint extractor imports from there. |
| `agentic_mbse.sysml.expression` module | `agentic_mbse/sysml/expression.py` | **UNCHANGED** (upstream dependency) | `extract_feature_refs()`, `extract_operators()`, `evaluate_true_static_expression()` remain in agentic-mbse. The expression compiler calls them -- it does not duplicate them. |
| `agentic_mbse.sysml.binding.classify_binding()` | `agentic_mbse/sysml/binding.py:13` | **UNCHANGED** | Already correctly classifies EXPRESSION bindings. Codegen's usage_extractor needs to respect this classification (fix the UNBOUND fallthrough). |
| Codegen `usage_extractor._extract_single_binding()` | `usage_extractor.py:273-332` | **FIXED** | The `OperatorExpression` fallthrough to UNBOUND is fixed to classify as `BindingType.EXPRESSION` and store the AST. |

**Post-consolidation file layout**:

```
extraction/
  expression_utils.py     <-- NEW: shared AST-to-text reconstruction
                              (extracted from constraint_extractor)
  expression_compiler.py  <-- NEW: ExpressionAST, compile, classify
                              (imports from expression_utils + agentic_mbse)
  constraint_extractor.py <-- imports _reconstruct_expression from expression_utils
  extractor.py            <-- uses expression_utils for calc_expressions text
  usage_extractor.py      <-- EXPRESSION binding type handled correctly
```

### 3.6 Preservation Interaction for Auto-Generated Impls

The existing `preservation.py` + `signature_extractor.py` system compares
function signatures: `(function_name, input_type, return_type)`. It does
**not** inspect the function body. This means it works correctly for
auto-implemented files without modification:

**Lifecycle scenarios**:

| Scenario | What Happens |
|----------|-------------|
| First codegen run, expression is compilable | `_impl.py` generated with actual code. `AUTO_IMPLEMENTED = True` header. |
| Re-run, SysML unchanged | `should_regenerate_stencil()` finds signature match → **preserves** file. Correct. |
| Re-run, SysML inputs changed (e.g., new parameter) | Signature mismatch (input_type differs) → **backup + regenerate** with new auto-impl. Correct. |
| User edits the auto-impl body (but keeps signature) | `should_regenerate_stencil()` finds signature match → **preserves** user edit. Correct. The system doesn't care that the body changed. |
| User edits AND SysML inputs change | Signature mismatch → **backup** user's version, then regenerate. User can merge from backup. Correct. |
| Expression was compilable, now isn't (e.g., added `sum()`) | Same signature → preserve existing auto-impl (which still works). On next full regen, stencil generator checks `Compilability` and emits stub, but preservation sees signature match and preserves. **This is correct** -- the old auto-impl still computes the old expression faithfully. If the user wants the new expression, they delete the file and re-run. |

**The `AUTO_IMPLEMENTED = True` sentinel** is a human-readable convention,
not a machine-checked flag. The preservation system uses signature comparison
exclusively. The sentinel helps developers scanning files understand provenance:
- `AUTO_IMPLEMENTED = True`: machine-generated, safe to overwrite
- `AUTO_IMPLEMENTED = False` (or absent): human-edited, preserve

If we later need machine-checked provenance (e.g., to force-regenerate all
auto-impls when the compiler improves), we can add a check for the sentinel
in `should_regenerate_stencil()`. But this is not needed for Phase 1.

### 3.7 Scope Decision: `math.pi` and Named Constants

The compiler does NOT emit `math.pi` or any named constants. SysML models
use literal `3.14159265359` (Pattern E), and the compiler faithfully reproduces
these literals. Rationale:

1. **Semantic fidelity**: The compiled code should match the SysML source.
   If the modeler writes `3.14159`, the generated code says `3.14159`.
2. **No hidden precision changes**: `math.pi` has more digits than `3.14159`.
   Substituting it would silently change computed results.
3. **No import overhead**: Keeping auto-impls free of `import math` makes them
   simpler and eliminates a potential failure mode.

If a future SysML model uses a named constant like `SI::pi`, the compiler would
need to recognize it. That's a future enhancement, not Phase 1 scope. The
`SAFE_MATH_FUNCTIONS` concept from the research doc is deferred until we
encounter actual `InvocationExpression` nodes in real models (currently: zero
occurrences).

---

## 4. Expression Pattern Catalog

Every expression pattern observed in the codebase, with the compiler's handling.

### Pattern A: Simple Binary Arithmetic

**SysML**: `out attribute area : Real = length * width;`
**Frequency**: Very common (appears in nearly every CalcDef)
**Verdict**: `FULLY_COMPILABLE`

```python
# Compiled output:
area = inputs.length * inputs.width
```

**Compiler logic**: Both `length` and `width` are `FeatureReferenceExpression`
nodes that resolve to declared `in` parameters of the same CalcDef. The
`OperatorExpression` node has `operator="*"` and 2 operands.

### Pattern B: Multi-Step Intermediate Computation

**SysML**:
```sysml
calc def PVModuleCostCalc {
    in wattage; in cost_per_watt; in fab_factor; in install_factor;
    out material_cost = wattage * cost_per_watt;
    out fab_cost = material_cost * fab_factor;
    out install_cost = material_cost * install_factor;
    out total_cost = material_cost + fab_cost + install_cost;
    out idiot_index = total_cost / material_cost;
}
```
**Frequency**: Common (6+ files)
**Verdict**: `FULLY_COMPILABLE`

```python
# Compiled output (topologically ordered):
material_cost = inputs.wattage * inputs.cost_per_watt
fab_cost = material_cost * inputs.fab_factor
install_cost = material_cost * inputs.install_factor
total_cost = material_cost + fab_cost + install_cost
idiot_index = total_cost / material_cost
return (material_cost, fab_cost, install_cost, total_cost, idiot_index)
```

**Compiler logic**: `fab_cost`'s expression references `material_cost`, which is
a sibling output (not an input). The compiler recognizes this as an
`intermediate_ref` and ensures `material_cost` is computed first. Topological
sort of output dependencies within the CalcDef.

**Key data model interaction**: `CompilationResult.intermediate_refs` for
`fab_cost` contains `["material_cost"]`. The generator emits outputs in
dependency order.

### Pattern C: Complex Parenthesized Expression

**SysML**:
```sysml
out attribute crf : Real = discount_rate * (1.0 + discount_rate) ** plant_lifetime
                           / ((1.0 + discount_rate) ** plant_lifetime - 1.0);
```
**Frequency**: Occasional (solar_battery library)
**Verdict**: `FULLY_COMPILABLE`

```python
# Compiled output:
crf = (inputs.discount_rate * (1.0 + inputs.discount_rate) ** inputs.plant_lifetime
       / ((1.0 + inputs.discount_rate) ** inputs.plant_lifetime - 1.0))
```

**Compiler logic**: The AST is deeply nested `OperatorExpression` nodes. The
recursive compiler walks each node, prefixing every `FeatureReferenceExpression`
with `inputs.`. The `**` operator maps to Python's `**`.

**Edge case**: Division by zero when `discount_rate == 0` and `lifetime == 0`.
This is a domain concern, not a compiler concern. The compiled code is
mathematically faithful to the SysML source.

### Pattern D: Expression with Literal Constants

**SysML**: `out attribute p_alpha : Real = p_fusion * 3.52 / 17.58;`
**Frequency**: Common
**Verdict**: `FULLY_COMPILABLE`

```python
p_alpha = inputs.p_fusion * 3.52 / 17.58
```

**Compiler logic**: `LiteralRational` nodes have a `.value` attribute. They
compile to Python numeric literals directly. No `inputs.` prefix.

### Pattern E: Pi as Repeated Literal

**SysML**: `out volume = 2.0 * 3.14159265359 * 3.14159265359 * r_major * a * a * kappa;`
**Frequency**: Occasional (geometry calcs)
**Verdict**: `FULLY_COMPILABLE`

```python
volume = 2.0 * 3.14159265359 * 3.14159265359 * inputs.r_major * inputs.a * inputs.a * inputs.kappa
```

**Note**: The compiler does NOT "optimize" `3.14159 * 3.14159` to `pi**2`. It
faithfully reproduces the SysML expression. Optimizations are out of scope and
would risk semantic drift.

### Pattern F: Unit-Annotated Literal

**SysML**: `attribute major_radius : Real = 3.0 [m];`
**Frequency**: Rare (1 file, radial_build.sysml)
**Verdict**: `FULLY_COMPILABLE` (unit is metadata, not computation)

```python
major_radius = 3.0  # [m] - unit annotation stripped
```

**Compiler logic**: The `[` operator in SysIDE produces an `OperatorExpression`
with `operator="["` and operands `[value_expr, unit_expr]`. The existing
`evaluate_true_static_expression()` in agentic-mbse already handles this by
extracting the value operand and discarding the unit. Same pattern here.

### Pattern G: Expression with `sum()` Over Collection

**SysML**: `capital_cost = sum(heater.capital_cost) + pump.capital_cost;`
**Frequency**: Occasional (coffee_maker, solar_battery, multiplicity tests)
**Verdict**: `MANUAL_REQUIRED`

**Why**: `sum()` over a collection implies iteration over part usages with
multiplicity. The expression compiler cannot resolve `heater.capital_cost` to
a single value -- it's a collection of values from multiple instances. This
is the nested-CalcUsage-in-PartDef pattern that requires Phase 3 (hierarchy).

**Generated stub**:
```python
def run_...(inputs: ...Input) -> float:
    """...
    NOTE: Expression contains sum() over collection -- manual implementation required.
    SysML: capital_cost = sum(heater.capital_cost) + pump.capital_cost
    """
    raise NotImplementedError(
        "Contains sum() over collection. See SysML source."
    )
```

### Pattern H: Conditional Expression

**SysML**:
```sysml
if fuel_type == FuelType::DT? p_nrl * 3.52 / 17.58
else if fuel_type == FuelType::DD? p_nrl * 0.82 / 7.3
else p_nrl * 1.0
```
**Frequency**: Rare (1 occurrence across all models)
**Verdict**: `MANUAL_REQUIRED` (Phase 1). Could become `FULLY_COMPILABLE` in a
future phase if we add `SelectExpression` handling.

### Pattern I: Inline Attribute Expression (Part-Level)

**SysML**:
```sysml
part blanket {
    attribute r_outer : Real;
    attribute r_inner : Real;
    attribute h : Real;
    attribute volume : Real = 3.14159 * (r_outer ** 2 - r_inner ** 2) * h;
}
```
**Frequency**: Currently rare in existing models (because modelers have been
forced to use CalcDefs). Expected to become common once codegen supports it.
**Verdict**: `FULLY_COMPILABLE` as a Computed Attribute module

**Generated module** (self-contained, no `_impl.py`):
```python
class BlanketVolumeModule(ModuleBase[BlanketVolumeInput, Float]):
    def run(self, r_outer: float, r_inner: float, h: float) -> ModuleResult[Float]:
        v = self.validate_and_fill_default(r_outer, r_inner, h)
        volume = 3.14159 * (v.r_outer ** 2 - v.r_inner ** 2) * v.h
        return ModuleResult(data=Float(volume))
```

**Compiler logic**: The attribute expression's `FeatureReferenceExpression` nodes
resolve to sibling attributes on the same part. These become the module's inputs.
The expression itself compiles identically to a CalcDef expression.

### Pattern J: Attribute Expression Referencing Calc Outputs (Aggregation)

**SysML**:
```sysml
part plant {
    calc comp_a_cost : CostCalc { ... }
    calc comp_b_cost : CostCalc { ... }
    attribute total_cost = comp_a_cost.total + comp_b_cost.total;
}
```
**Frequency**: This is the aggregation pattern. Currently done via explicit
CalcDefs (Approach E Rule 3).
**Verdict**: `FULLY_COMPILABLE` as a Computed Attribute, BUT requires the
dependency backtracker to resolve `comp_a_cost.total` to a module output channel.

**How it flows through the pipeline**:

1. Extraction discovers `total_cost` attribute with expression AST
2. `extract_feature_refs()` finds references: `comp_a_cost.total`, `comp_b_cost.total`
3. These are `FeatureChainExpression` nodes (instance.output pattern)
4. A synthetic `CalcUsageData` is created with:
   - `instance_name`: `plant__total_cost_calc` (synthetic name)
   - `bindings`: `[BindingInfo(param_name="comp_a_cost__total", source_path="comp_a_cost.total", binding_type=CHAIN), ...]`
5. The backtracker resolves `comp_a_cost.total` to `MODULE_OUTPUT` -- this is
   exactly what it already does for chain bindings in calc usages
6. The expression compiler generates: `inputs.comp_a_cost__total + inputs.comp_b_cost__total`

**Key insight**: The synthetic CalcUsage looks identical to a real one from the
backtracker's perspective. No backtracker changes needed for this pattern.

### Pattern K: EXPOSE Pattern (`attribute x = calc.output`)

**SysML**:
```sysml
part plasma_region {
    calc minor_calc : TorusMinorRadius { ... }
    attribute minor_radius : Real = minor_calc.a;  // EXPOSE
}
```
**Frequency**: Common (the standard pattern for cross-file data flow)
**Verdict**: **NOT a Computed Attribute** -- this is pure value forwarding.

The EXPOSE pattern does NOT need a module. It's already handled by the
backtracker's transitive resolution (Strategy 4). When downstream code binds
to `plasma_region.minor_radius`, the backtracker traces through to
`minor_calc.a` and resolves to `MODULE_OUTPUT`.

**Decision rule**: If an attribute expression is a single `FeatureChainExpression`
with no operators, it's an EXPOSE, not a computed attribute. Skip it.

### Pattern L: Default Value Expression (`default :=`)

**SysML**: `in attribute fab_factor : Real default := 0.6;`
**Frequency**: Common in library CalcDefs
**Verdict**: Already handled. The default value is extracted as a literal and
becomes the `EntryPoint.default_value`. No expression compilation needed.

### Pattern M: Derived Design Attribute (Currently Prohibited by ADR-002)

**SysML**:
```sysml
// CURRENTLY PROHIBITED:
part design {
    attribute radius : Real = 3.0;
    attribute diameter : Real = radius * 2.0;  // ADR-002 violation
}
```
**Frequency**: Zero (prohibited by ADR-002 Rule 3)
**Verdict**: Phase 2 (Computed Attribute) would make this legal and handle it
correctly. This is actually a key motivator for Phase 2 -- it relaxes ADR-002
to allow computed attributes.

**ADR-002 evolution**: When Phase 2 is implemented, ADR-002 Rule 3 would be
amended: "Design attributes may contain **compilable expressions** referencing
sibling attributes. The expression compiler will generate the computation."

---

## 5. Edge Cases and Failure Modes

### Edge 1: Expression References an Attribute That's Not a Declared Input

**Scenario**: CalcDef output expression references a name that doesn't match
any `in` parameter.

```sysml
calc def BadCalc {
    in x : Real;
    out result : Real = x * mystery_value;  // mystery_value is not declared
}
```

**Handling**: The compiler's reference resolver checks every
`FeatureReferenceExpression` against the CalcDef's declared input names. If
`mystery_value` is not found, the `ExpressionAST` node gets `node_type="unsupported"`
with `reason="unresolved reference: mystery_value"`. The verdict becomes
`PARTIALLY_COMPILABLE` or `MANUAL_REQUIRED`.

### Edge 2: Circular Intermediate References

**Scenario**: Two outputs reference each other.

```sysml
calc def CircularCalc {
    in x : Real;
    out a : Real = b + x;  // references b
    out b : Real = a * 2;  // references a
}
```

**Handling**: Topological sort of intermediate dependencies detects the cycle.
Verdict: `MANUAL_REQUIRED` with reason "circular dependency among outputs: a, b".

### Edge 3: Expression AST Not Available

**Scenario**: SysIDE doesn't populate `feature_value_expression` for some
attribute (e.g., it's defined via a `return` statement or inherited).

**Handling**: `output_expression_asts[output_name]` is `None`. That output
gets verdict `MANUAL_REQUIRED`. Other outputs in the same CalcDef may still
compile. A CalcDef is `PARTIALLY_COMPILABLE` if some but not all outputs compile.

### Edge 4: Operator Not in Supported Set

**Scenario**: Expression uses an operator like `%` (modulo) or string
concatenation.

**Handling**: `OPERATOR_MAP` lookup fails. Node becomes `unsupported` with
reason "unsupported operator: %". Verdict escalates to `MANUAL_REQUIRED`.

Supported operator set (from SYSIDE_BINDING_REFERENCE and constraint_extractor):
`+`, `-`, `*`, `/`, `**`, `^` (alias for `**`), `[` (unit annotation, stripped).

### Edge 5: FeatureChainExpression in CalcDef Output

**Scenario**: Output expression references a chain like `subsystem.value`.

```sysml
calc def WeirdCalc {
    in subsystem : SubsystemType;
    out result : Real = subsystem.value * 2;
}
```

**Handling**: `FeatureChainExpression` in a CalcDef output expression means the
input is a structured type, not a scalar. The compiler cannot resolve
`subsystem.value` to a simple input name. Verdict: `MANUAL_REQUIRED`.

**Exception**: If the chain resolves to a sibling output (intermediate ref),
it's handled normally. The classifier checks intermediate outputs first, then
declared inputs, then flags as unsupported.

### Edge 6: Attribute Expression That Looks Like EXPOSE But Has Operators

**Scenario**:
```sysml
attribute doubled_cost : Real = cost_calc.total_cost * 2.0;
```

**Handling**: This is NOT a pure EXPOSE (it has an operator). It IS a Computed
Attribute. The classifier checks: "Is this expression a single
FeatureChainExpression with no operators?" If no, it's a computed attribute.
If yes, it's an EXPOSE (skip).

### Edge 7: Same Output Name in Different CalcDefs

**Scenario**: `CalcA` and `CalcB` both have `out total_cost`. When used as
intermediates in the same pipeline, channel names could collide.

**Handling**: Already solved by ADR-003. Channel names use PQN format:
`{usage_qualified_name}__{output_name}`. The usage qualified name is globally
unique, so `calca_usage__total_cost` and `calcb_usage__total_cost` never
collide.

### Edge 8: Computed Attribute References an Attribute from a Different Part

**Scenario**:
```sysml
part plant {
    part reactor { attribute power : Real = 100.0; }
    attribute scaled_power : Real = reactor.power * 1.5;
}
```

**Handling**: `reactor.power` is a `FeatureChainExpression`. The synthetic
CalcUsage gets a binding: `BindingInfo(param_name="reactor__power",
source_path="reactor.power", binding_type=CHAIN)`. The backtracker resolves
`reactor.power` -- if it's a literal design attribute, it becomes an
ENTRY_POINT. If it's a calc output (via EXPOSE), it becomes a MODULE_OUTPUT.
Either way, standard resolution applies.

### Edge 9: Auto-Implemented Code Fails at Runtime

**Scenario**: Generated expression `a / b` throws `ZeroDivisionError` because
`b == 0` in the input JSON.

**Handling**: This is equivalent to a handwritten `_impl.py` dividing by zero.
The TEAx pipeline framework handles module exceptions uniformly. The compiler
is not responsible for domain-level input validation. Pydantic constraints on
the Input model (already generated from SysML constraints) are the right place
for this.

---

## 6. Development and Testing Strategy

### The Problem with "Just Implement It"

Past experience shows that jumping into codegen changes leads to cascading
failures because:

1. SysIDE AST behavior varies across expression types in ways that aren't
   documented
2. The pipeline has 4 layers, and a change in extraction ripples through
   analysis, resolution, and generation
3. Integration tests require real SysML models loaded through SysIDE, which
   is slow and makes iteration painful
4. Edge cases in expression forms only surface when processing diverse models

### Strategy: Answer Questions Bottom-Up Before Integration

Each phase starts with **standalone scripts** that test a specific hypothesis
against real SysML models. Only after all questions are answered do we touch
the codegen pipeline.

### Phase 1 Questions: Expression Compiler

#### Q1: Can we extract expression ASTs for all CalcDef outputs?

**Script**: `scripts/spike_extract_expression_asts.py`

```python
"""Load the chain_spike + solar_battery + CATF models.
For each CalcDef, for each output attribute:
  - Does feature_value_expression exist?
  - What is its type name?
  - Can we traverse it recursively?
Print a table: CalcDef | Output | AST Type | Depth | Has Unhandled Nodes
"""
```

**What we learn**: Which CalcDefs have extractable ASTs, which don't, and
what AST node types we encounter. This grounds the `ExpressionAST` design
in reality rather than assumptions.

**Pass criteria**: >80% of outputs have extractable ASTs. The set of
encountered node types is a subset of: `OperatorExpression`,
`FeatureReferenceExpression`, `FeatureChainExpression`, `LiteralRational`,
`LiteralInteger`, `LiteralBoolean`.

#### Q2: Can we resolve all FeatureReferenceExpression nodes to input names?

**Script**: `scripts/spike_resolve_expression_refs.py`

```python
"""For each CalcDef with extractable ASTs:
  - Run extract_feature_refs() on each output expression
  - For each ref, check: is ref.name in the CalcDef's input_attributes?
  - Or: is ref.name in the CalcDef's other output_attributes (intermediate)?
Print: CalcDef | Output | Ref Name | Resolves To | Resolution Type
Flag any ref that resolves to neither input nor intermediate.
"""
```

**What we learn**: Whether the assumption "all refs in a CalcDef expression
are either inputs or sibling outputs" holds. If it doesn't, we need to
understand what the other references are.

**Pass criteria**: 100% of refs resolve to either input or intermediate.
Any failure means our compilation model is wrong.

#### Q3: Can we produce correct Python from the AST?

**Script**: `scripts/spike_compile_expressions.py`

```python
"""For each CalcDef where Q1+Q2 passed:
  - Build ExpressionAST from the syside AST
  - Compile to Python expression string
  - Verify the string is syntactically valid Python (ast.parse)
  - For CalcDefs with known handwritten impls, compare:
    execute the compiled expression with test inputs vs
    execute the handwritten impl with same inputs
    assert outputs match within floating-point tolerance
"""
```

**What we learn**: Whether the compiler produces correct, executable Python.
The comparison with existing handwritten impls is the ground truth.

**Pass criteria**: All compiled expressions are valid Python. For CalcDefs
with existing impls (PVModuleCostCalc, EnergyProductionCalc, etc.),
outputs match within `1e-10` relative tolerance.

#### Q4: Does the compilability classifier agree with reality?

**Script**: `scripts/spike_classify_compilability.py`

```python
"""Run the classifier on ALL CalcDefs across all models.
Print the verdict for each.
Cross-reference with the handwritten _impl.py files:
  - If verdict is FULLY_COMPILABLE, does an _impl.py exist?
    If yes, would the compiled version produce the same result?
  - If verdict is MANUAL_REQUIRED, is the _impl.py doing something
    the compiler can't handle? (Verify the reason is accurate.)
"""
```

**What we learn**: Whether the classifier's boundaries are correct. False
positives (says FULLY_COMPILABLE but compiled code is wrong) are bugs.
False negatives (says MANUAL_REQUIRED but could have compiled) are
acceptable initially but should be tracked for improvement.

### Phase 2 Questions: Attribute Expression Capture

#### Q5: Can we discover attribute expressions on parts?

**Script**: `scripts/spike_discover_computed_attributes.py`

```python
"""For each PartDef and PartUsage in the model:
  - Iterate owned_members that are AttributeUsage
  - Check: does it have feature_value_expression?
  - Is the expression a single FeatureChainExpression (EXPOSE) or
    does it have operators (Computed Attribute)?
  - For Computed Attributes: extract refs, classify compilability
Print: Part | Attribute | Expression Type | Refs | Compilability
"""
```

**What we learn**: How many computed attributes exist in real models, and
whether they're distinguishable from EXPOSEs.

#### Q6: Do synthetic CalcUsages wire correctly through the backtracker?

**Script**: `scripts/spike_synthetic_calc_usages.py`

```python
"""Take the computed attributes from Q5.
Manually construct CalcUsageData objects for them.
Feed them into the existing DependencyBacktracker alongside real CalcUsages.
Check: does the backtracker resolve their bindings correctly?
Does the ComputationGraph include them with correct wiring?
"""
```

**What we learn**: Whether synthetic CalcUsages are transparent to the
existing pipeline. This is the critical integration question -- if the
answer is no, we need to understand what the backtracker assumes about
CalcUsages that synthetic ones violate.

**Pass criteria**: Synthetic CalcUsages appear in the ComputationGraph
with correctly resolved inputs (MODULE_OUTPUT for chain refs, ENTRY_POINT
for literal/design attrs).

### Phase 3 Questions: Hierarchy/Multiplicity (Future)

These are deferred but documented for completeness:

- **Q7**: Can we extract multiplicity from PartUsage elements?
- **Q8**: Can we detect `:>>` redefinition chains and resolve them?
- **Q9**: Can we build a part-usage tree from the design?
- **Q10**: Can synthetic rollup modules aggregate child outputs?

### Integration Order

Only after spike scripts validate the design:

```
Step 1: Expression compiler module
  - New file: extraction/expression_compiler.py
  - Contains: ExpressionAST, CompilationResult, compile_expression(),
    classify_compilability()
  - Tested: Unit tests using manually constructed ASTs (no syside dependency)
  - Tested: Integration tests using spike script fixtures

Step 2: AST extraction in extractor
  - Modify: extraction/extractor.py (_extract_calculation_definition)
  - Add: output_expression_asts population
  - Tested: Existing tests still pass + new tests for AST extraction

Step 3: Compilability annotation in resolution
  - Modify: resolution/models.py (add fields to PipelineModule)
  - Modify: resolution/graph_builder.py (annotate modules)
  - Tested: Existing graph builder tests still pass

Step 4: Conditional generation
  - Modify: generation/stencils.py (auto-impl vs stub)
  - Add: templates/auto_implementation.py.jinja2
  - Tested: Generate for chain_spike model, verify auto-impls are correct

Step 5: Attribute expression extraction (Phase 2)
  - New: extraction/attribute_expression_extractor.py
  - Modify: generation/initialization.py (add extraction step)
  - Tested: Spike Q5+Q6 results reproduced in integration tests

Step 6: End-to-end validation
  - Run codegen on solar_battery model
  - Verify: auto-implemented modules produce same outputs as handwritten ones
  - Verify: non-compilable modules still get proper stubs
  - Verify: preservation.py correctly handles auto-impl -> hand-edit -> regen
```

### Test Fixture Strategy

| Fixture | Purpose | Location |
|---------|---------|----------|
| `chain_spike_model/` | Simple 3-calc chain, all compilable | Existing |
| `sample_model/` | Basic calcs (simple_calc, multi_output, deps) | Existing |
| `expression_patterns/` | NEW: One .sysml per pattern (A through M) | New fixture |
| `solar_battery model` | Real-world model with handwritten impls for ground truth | Existing in fusion-tea |

The `expression_patterns/` fixture should contain minimal SysML files that
exercise each pattern in isolation. This makes it possible to test the compiler
against specific constructs without loading a full model.

---

## 7. What This Does NOT Cover

- **Nested CalcUsage-in-PartDef instantiation** (Phase 3) -- template detection,
  per-PartUsage module generation, `:>>` redefinition chain resolution
- **Multiplicity/aggregation** (Phase 3) -- `sum()` over collections, tree
  evaluation, synthetic rollup modules
- **Runtime model dependency elimination** -- Phase 3 aspiration
- **Plugin/extension API** -- Approach C, explicitly skipped
- **Conditional expression compilation** -- Future enhancement if demand exists

---

## 8. Success Criteria

### Phase 1 (Expression Compiler) is done when:

1. Running codegen on the chain_spike model produces `_impl.py` files with
   actual code (not `NotImplementedError`) for all 3 CalcDefs
2. Running codegen on the solar_battery model auto-implements at least 10 of
   15 CalcDefs, and the auto-implemented code produces outputs matching the
   existing handwritten implementations within `1e-10` tolerance
3. Non-compilable CalcDefs still get proper `NotImplementedError` stubs
4. Existing tests pass with zero regressions
5. `IMPLEMENTATION_BACKLOG.md` only lists modules that genuinely need manual work

### Phase 2 (Attribute Expressions) is done when:

1. A test model with `attribute volume = pi * r^2 * h` on a part generates
   a working self-contained module with no `_impl.py`
2. A test model with `attribute total = a.cost + b.cost` generates a module
   with correctly wired inputs from upstream calc output channels
3. ADR-002 Rule 3 is amended to permit compilable attribute expressions
4. Existing models continue to work without modification

---

## 9. References

| Document | Relevance |
|----------|-----------|
| `fusion_modeling/docs/codegen/DATA_FLOW_SPECIFICATION.md` | Authoritative pipeline spec; 13 data structures |
| `fusion_modeling/docs/codegen/SYSIDE_BINDING_REFERENCE.md` | AST traversal patterns, 7 pitfalls |
| `fusion_modeling/docs/codegen/STUDY_1_EXTRACTION.md` | Extraction analysis, Gap G1b (expression literals become ???) |
| `fusion_modeling/docs/architecture/ADR-001-input-parameter-definition.md` | Entry point taxonomy |
| `fusion_modeling/docs/architecture/ADR-002-calculation-architecture.md` | Calc location rules, expression handling |
| `fusion_modeling/docs/architecture/ADR-003-signal-identifiers.md` | Identifier contracts, no-reconstruction rule |
| `.project/research/20260202-180000_expression-compilation-and-inline-math-strategy.md` | Strategy evaluation, Approach F definition |
| `.project/research/20260109-205122_cost-modeling-codegen-changes.md` | Nested CalcUsage analysis, template detection |
| `fusion-tea/.project/research/20260202-120000_codegen-native-costing-upgrade-design.md` | Gap analysis, 5 approaches |

---

## Changelog

| Date | Change |
|------|--------|
| 2026-02-03 | Initial draft |
| 2026-02-03 | Rev 2: Added pipeline integration point (Step 6.5). Used Enums for Compilability, ExpressionNodeType, aligned verdict vocabulary. Added consolidation plan (Section 3.5). Added preservation.py interaction analysis (Section 3.6). Added math.pi scope decision (Section 3.7). Moved compiled_expressions off PipelineModule into CalcDefCompilationResult on PipelineContext. |
