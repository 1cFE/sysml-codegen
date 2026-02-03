---
date: 2026-02-02T18:00:00-06:00
researcher: Claude
topic: "Expression compilation, inline math, and native costing upgrade strategy evaluation"
tags: [research, codegen, expressions, architecture, strategy]
status: complete
last_updated: 2026-02-02
---

# Research: Expression Compilation, Inline Math, and Costing Upgrade Strategy

**Date**: 2026-02-02T18:00:00-06:00
**Researcher**: Claude
**Research Type**: Architecture / Strategy Evaluation / Feasibility

## Research Question

Given the gaps identified in the `20260202-120000_codegen-native-costing-upgrade-design.md` research report and the user's observation that putting ALL math into `calc` blocks creates excessive overhead, what is the best strategy for closing these gaps? How should we evaluate the five options identified, and is there a sixth option worth considering -- specifically, expression compilation that eliminates the need for handwritten `_impl.py` stubs for simple/medium-complexity calculations?

## Summary

- **The user's core pain point -- "ALL math must be `calc` blocks" -- is the single highest-leverage problem to solve.** Every arithmetic expression in SysML currently requires: (1) a CalcDef with inputs/outputs, (2) a CalcUsage with bindings, (3) a generated TEAx module wrapper, (4) a handwritten `_impl.py` stub, (5) pipeline YAML wiring. For `volume = pi * r^2 * h`, that's ~100 lines of infrastructure for 1 line of math.
- **The codegen already extracts expression ASTs but throws them away.** `CalculationDefinitionData.calc_expressions` captures raw strings; `BindingType.EXPRESSION` exists in the enum but is never classified in `usage_extractor.py`; `constraint_extractor.py` has a complete recursive expression reconstructor; `agentic_mbse.sysml.expression` has `evaluate_true_static_expression()` and `extract_feature_refs()`. The infrastructure is 60-70% built.
- **A new "Approach F" emerges: Expression-Aware Codegen** that combines the user's inline-expression insight with the research report's Approach D (expression compilation). Instead of just compiling CalcDef expressions into Python functions, this approach also handles **attribute-level expressions** (`attribute volume = pi * r^2 * h`) directly, bypassing the need for a CalcDef entirely for simple formulas.
- **The recommended path is a phased hybrid: E (modeling discipline) + F (expression-aware codegen), skipping C (plugin) entirely.** Phase 0 uses Approach E for immediate unblocking. Phase 1 builds the expression compiler to close the "GAP: does NOT implement calc logic" across all generated modules. Phase 2 adds attribute-expression capture to eliminate trivial CalcDefs. Phase 3 adds hierarchy/multiplicity/aggregation for the nested pattern.
- **The four gaps from the original research remain valid but are reframed.** Gaps 1-4 (binding resolution, multiplicity, aggregation, context) are real but affect the *advanced* nested-CalcUsage pattern. The *immediate* pain (bloat from trivial calc blocks) is a different problem with a different solution: expression compilation + attribute expression capture.

## Detailed Findings

### 1. Evaluation of the Five Existing Approaches

#### Approach A: Full Native Enhancement -- DEFER

**Assessment: Architecturally correct but premature.**

Approach A touches every layer (extraction, analysis, resolution, generation) to make codegen natively understand part hierarchies, `:>>` chains, multiplicity, and aggregation. The research report correctly identified this as high complexity.

The real issue is that Approach A solves Gap 1-4 (the advanced nested pattern) without addressing the more fundamental pain point: the overhead of wrapping every expression in a CalcDef. Even after implementing Approach A, a modeler would still need to create a `calc def VolumeCalc` for `volume = pi * r^2 * h` because codegen can't compile that expression into executable code.

**Verdict:** Defer until the expression compiler (Approach F, Phase 1) is built. At that point, Approach A becomes much simpler because the expression compiler provides the leaf-node computation that the hierarchy evaluator needs.

#### Approach B: Runtime Evaluator Module -- REJECT

**Assessment: Wrong direction.**

Generating a runtime evaluator that dynamically evaluates expressions is the opposite of what codegen should do. It creates generated code that's harder to understand than the handwritten `generate_costs.py` it replaces. The generated evaluator would need its own test strategy, debugging would be opaque, and it doesn't advance codegen's capabilities.

**Verdict:** Reject. The expression compiler (Approach F) achieves the same goal (no handwritten impl) with cleaner, inspectable, testable generated code.

#### Approach C: Plugin Interface -- SKIP

**Assessment: Unnecessary intermediate step.**

The plugin formalization was recommended as a short-term bridge. But if we adopt Approach E (modeling discipline) for the immediate term and go straight to expression compilation (Approach F) for the medium term, the plugin never serves a purpose. It would be architectural overhead for a pattern that only lives during a transition period.

**Verdict:** Skip entirely unless a concrete need arises for non-codegen module generators.

#### Approach D: Expression Compilation -- ABSORB INTO F

**Assessment: Right idea, too narrow.**

The original Approach D described compiling CalcDef expressions into Python functions plus a tree evaluator for hierarchy. This is the right technical direction but scoped too narrowly. It only compiles *CalcDef-level* expressions, still requiring every formula to live inside a `calc def` block.

The key insight is: **attribute-level expressions should also be compilable.** When a SysML model says:

```sysml
part blanket {
    attribute volume : Real = pi * r_outer^2 * h - pi * r_inner^2 * h;
}
```

This should NOT require a CalcDef. Codegen should capture this expression, compile it to Python, and wire it into the pipeline as a lightweight "computed attribute" -- either as an inline expression in the pipeline or as an auto-generated trivial module.

**Verdict:** Absorb into Approach F with expanded scope.

#### Approach E: Modeling Workaround -- KEEP AS PHASE 0

**Assessment: Pragmatically correct for now.**

The CATF model proves this works. The five modeling rules are sound engineering discipline. The verbosity tradeoff is acceptable at current scale (~50 CalcDefs, ~30 subsystems).

However, the user's feedback that "ALL math must be calc blocks" directly targets Approach E's biggest weakness: Rule 3 (aggregation is an explicit CalcDef) and Rule 1 (multiplicity is a parameter). These rules INCREASE the number of calc blocks because every aggregation, every multiplier, every trivial formula needs its own CalcDef+CalcUsage+module+impl.

**Verdict:** Keep as Phase 0 (immediate unblocking) but prioritize Phase 1 (expression compiler) to reduce the overhead.

### 2. Approach F: Expression-Aware Codegen (NEW)

This is the core recommendation. It combines the user's inline-expression insight with Approach D's expression compilation, expanded to cover two use cases:

#### Use Case 1: CalcDef Expression Compilation (Closes "GAP: does NOT implement calc logic")

**Current state:** Every generated `_impl.py` stencil contains `raise NotImplementedError(...)`. The SysML expressions are preserved as doc comments but not compiled to code.

**Proposed change:** When a CalcDef's expressions can be fully resolved to a computable Python expression (all operands are inputs or constants), generate the implementation automatically instead of a stub.

**What exists already:**
- `CalculationDefinitionData.calc_expressions: list[str]` -- raw expression strings (`data_models.py:118`)
- `extractor._extract_expression_text()` -- partial AST-to-text (`extractor.py:612-634`), handles OperatorExpression and FeatureReferenceExpression
- `constraint_extractor._reconstruct_expression()` -- complete AST-to-text (`constraint_extractor.py:137-171`), handles all node types
- `agentic_mbse.sysml.expression.evaluate_true_static_expression()` -- evaluates pure-constant expressions to float (`expression.py:374`)
- `agentic_mbse.sysml.expression.extract_feature_refs()` -- finds all variable references in an expression (`expression.py:119`)
- `agentic_mbse.sysml.expression.extract_operators()` -- finds all operators (`expression.py:225`)

**What needs to be built:**
1. **Expression compiler** -- Takes a CalcDef's output expressions (from the AST, not the string), resolves all `FeatureReferenceExpression` nodes to input parameter names, and emits a Python expression string. This is a targeted extension of `constraint_extractor._reconstruct_expression()` where reference names are mapped to `inputs.<param_name>`.
2. **Compilability classifier** -- Determines whether a CalcDef's expressions can be fully compiled (all references resolve to inputs) or need handwritten impl (references to external state, complex control flow, function calls not in a supported set).
3. **Auto-impl generator** -- For compilable CalcDefs, generates the `_impl.py` with actual code instead of `NotImplementedError`. For non-compilable ones, generates the stub as today with a note about what couldn't be resolved.

**Example transformation:**

SysML:
```sysml
calc def TorusVolume {
    in r_major : Real;
    in r_minor : Real;
    out volume : Real = 2 * 3.14159 * 3.14159 * r_major * r_minor * r_minor;
}
```

Current generated `_impl.py`:
```python
def run_torusvolume(inputs: TorusVolumeInput) -> float:
    """..."""
    raise NotImplementedError("Manual implementation required for TorusVolume.")
```

Proposed generated `_impl.py`:
```python
def run_torusvolume(inputs: TorusVolumeInput) -> float:
    """Execute TorusVolume calculation.

    Auto-generated from SysML expression. Edit only if manual override needed.
    SysML Source: library.sysml:42
    """
    return 2 * 3.14159 * 3.14159 * inputs.r_major * inputs.r_minor * inputs.r_minor
```

**Impact:** Eliminates handwritten `_impl.py` for every CalcDef whose math is fully expressed in SysML. For the CATF model, this could auto-implement ~30-40 of ~50 CalcDefs (the ones that are pure arithmetic). The remaining ~10-20 would still need stubs (complex physics with function calls, conditionals, lookup tables).

#### Use Case 2: Attribute Expression Capture (Reduces calc block overhead)

**Current state:** An attribute like `attribute volume = pi * r^2 * h` on a PartDef is extracted as a `DesignAttributeData` with `default_value` set to the *evaluated result* (a float) if it's a static expression, or `None` if it contains references. The expression itself is lost.

**Proposed change:** When a PartDef attribute has an expression that references other attributes (possibly from other parts/calcs), capture that expression as a lightweight "computed attribute" that can be wired into the pipeline without requiring a full CalcDef.

**Two sub-patterns:**

**Pattern 2a: Definitive expressions (pure formulas on local attributes)**
```sysml
part blanket {
    attribute r_outer : Real;      // entry point
    attribute r_inner : Real;      // entry point
    attribute h : Real;            // entry point
    attribute volume : Real = 3.14159 * (r_outer**2 - r_inner**2) * h;
}
```

This `volume` doesn't need a CalcDef. The expression can be captured at extraction time and either:
- (a) Compiled into a trivial auto-generated module (`BlankVolumeModule` with 3 inputs, 1 output, auto-implemented), or
- (b) Inlined as a "computed entry point" that the pipeline evaluates before passing downstream

Option (a) is simpler because it reuses the existing module infrastructure. The module is auto-generated entirely (no `_impl.py` stub needed because the expression compiler provides the body).

**Pattern 2b: Aggregation expressions (references to calc outputs)**
```sysml
part plant {
    attribute total_cost = comp_a.cost + comp_b.cost + comp_c.cost;
}
```

The expression references outputs from other calculations. This is a wiring+computation pattern: the dependency backtracker can resolve `comp_a.cost` to a module output channel, and the expression compiler can generate `inputs.comp_a_cost + inputs.comp_b_cost + inputs.comp_c_cost`. A synthetic CalcDef is generated at extraction time.

**Impact on the "ALL math must be calc blocks" problem:**

| Current overhead for `volume = pi*r^2*h` | With Approach F |
|------------------------------------------|-----------------|
| Write CalcDef in library.sysml | Not needed |
| Write CalcUsage in design.sysml | Not needed |
| Generated TEAx module wrapper | Auto-generated from attribute expression |
| Handwritten `_impl.py` | Auto-generated from expression |
| Pipeline YAML wiring | Auto-generated |
| Entry point JSON params | Auto-generated (r, h become entry points) |

For the "flat aggregation" pattern (Approach E Rule 3), this means:
```sysml
// BEFORE: Explicit CalcDef required
calc def TotalCost {
    in cost_a; in cost_b; in cost_c;
    out total = cost_a + cost_b + cost_c;
}

// AFTER: Inline attribute expression suffices
part plant {
    attribute total_cost = comp_a.cost + comp_b.cost + comp_c.cost;
}
```

### 3. Technical Feasibility: Change Surface Analysis

#### Layer 1: Extraction Changes

**File: `extraction/extractor.py`**

| Change | Lines Affected | Complexity |
|--------|---------------|------------|
| Upgrade `_extract_expression_text()` to use `constraint_extractor._reconstruct_expression()` logic | 612-634 | LOW -- logic already exists, just needs to be shared |
| Store raw AST alongside string in `CalculationDefinitionData` | 107-135 (data_models.py) | LOW -- add `expression_asts: list[Any]` field |
| Classify compilability during extraction | New method | MEDIUM -- needs to check all refs resolve to inputs |

**File: `extraction/usage_extractor.py`**

| Change | Lines Affected | Complexity |
|--------|---------------|------------|
| Handle `BindingType.EXPRESSION` in `_extract_single_binding()` | 273-332 | MEDIUM -- currently falls to UNBOUND |
| Extract expression AST for EXPRESSION bindings | 273-332 | LOW -- store `expression_ast` on BindingInfo |

**File: `extraction/constraint_extractor.py`**

| Change | Lines Affected | Complexity |
|--------|---------------|------------|
| Extract `_reconstruct_expression()` and helpers into shared utility | 137-257 | LOW -- pure refactor, no logic change |

**New file: `extraction/expression_compiler.py`**

| Component | Complexity |
|-----------|------------|
| `compile_calc_expression(ast, input_names) -> str` | MEDIUM -- maps refs to `inputs.<name>` |
| `classify_compilability(calc_def) -> CompilabilityLevel` | MEDIUM -- checks ref resolution |
| `CompilabilityLevel` enum: `FULLY_AUTO`, `NEEDS_HELPERS`, `MANUAL_REQUIRED` | LOW |

**New file or extension: `extraction/attribute_expression_extractor.py`**

| Component | Complexity |
|-----------|------------|
| `extract_computed_attributes(model) -> list[ComputedAttributeData]` | MEDIUM-HIGH -- new extraction pass |
| `ComputedAttributeData`: expression AST, references, owning part, compilability | LOW |
| Synthetic CalcUsageData generation from computed attributes | MEDIUM |

#### Layer 2: Analysis Changes

**File: `analysis/dependency_backtracker.py`**

| Change | Lines Affected | Complexity |
|--------|---------------|------------|
| Handle EXPRESSION bindings in `_trace_dependencies()` | 305-484 | MEDIUM -- extract refs from AST, resolve each |
| Support synthetic CalcUsages from computed attributes | Minimal | LOW -- they look like normal CalcUsages |

#### Layer 3: Resolution Changes

**File: `resolution/models.py`**

| Change | Lines Affected | Complexity |
|--------|---------------|------------|
| Add `is_auto_implemented: bool` to `PipelineModule` | 148-165 | LOW |
| Add `compiled_expression: str | None` to `PipelineModule` | 148-165 | LOW |
| (Optional) Add `multiplicity: int = 1` for future Phase 3 | 148-165 | LOW |

**File: `resolution/graph_builder.py`**

| Change | Lines Affected | Complexity |
|--------|---------------|------------|
| Pass compilability info through to PipelineModule | 423-539 | LOW |

#### Layer 4: Generation Changes

**File: `generation/stencils.py`**

| Change | Lines Affected | Complexity |
|--------|---------------|------------|
| For auto-implemented modules, generate actual code instead of stub | 85-151 | MEDIUM |
| New template: `auto_implementation.py.jinja2` | New file | LOW |
| Preservation logic: don't overwrite if user has edited auto-impl | 20-61 (preservation.py) | LOW -- existing smart_regen handles this |

**File: `generation/modules.py`**

| Change | Lines Affected | Complexity |
|--------|---------------|------------|
| (Optional) For trivial single-expression modules, inline the expression in the module class itself, skipping the separate `_impl.py` | 82-168 | MEDIUM |

**Template: `implementation_stencil.py.jinja2`**

| Change | Lines Affected | Complexity |
|--------|---------------|------------|
| Conditional: if `compiled_expression`, emit code; else emit NotImplementedError | 1-18 | LOW |

#### TEAx / Runtime Changes

| Change | Complexity |
|--------|------------|
| None required for Phase 1 (expression compilation) | -- |
| None required for Phase 2 (attribute expression capture) | -- |
| Phase 3 (hierarchy/multiplicity): May need `MultiplicityModule` base class or wrapper | MEDIUM |

#### Model Pattern Changes

| Phase | Model Changes |
|-------|--------------|
| Phase 0 (Approach E) | Follow 5 modeling rules, document as ADR |
| Phase 1 (expression compiler) | None -- existing CalcDefs get auto-implemented |
| Phase 2 (attribute expressions) | Modelers can write `attribute x = expr` instead of CalcDefs for simple math |
| Phase 3 (hierarchy) | Modelers can return to idiomatic nested CalcUsage-in-PartDef patterns |

### 4. What About Function Calls?

The expression compiler will encounter expressions like `sqrt(x)`, `min(a, b)`, `abs(x)`. These appear as `InvocationExpression` in the AST, which none of the current extractors handle.

**Recommended approach:** Maintain a whitelist of safe mathematical functions that map to Python builtins or `math` module:

```python
SAFE_MATH_FUNCTIONS = {
    "sqrt": "math.sqrt",
    "abs": "abs",
    "min": "min",
    "max": "max",
    "sin": "math.sin",
    "cos": "math.cos",
    "tan": "math.tan",
    "exp": "math.exp",
    "log": "math.log",
    "log10": "math.log10",
    "pi": "math.pi",
    "pow": "math.pow",
}
```

If an expression uses only whitelisted functions and resolvable references, it's `FULLY_AUTO`. If it uses unknown functions, it's `MANUAL_REQUIRED`.

### 5. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Expression ASTs vary across syside versions | LOW | HIGH | Use duck-typing pattern (already used in constraint_extractor) |
| Compiled expressions have subtle precision differences from handwritten code | LOW | LOW | Both use Python float arithmetic |
| Modelers rely on auto-impl but need to override | MEDIUM | LOW | Existing preservation.py handles this -- won't overwrite edited files |
| `InvocationExpression` handling is incomplete | MEDIUM | MEDIUM | Whitelist approach; unknown functions fall back to manual stub |
| Attribute expression extraction misidentifies entry points | MEDIUM | MEDIUM | Reuse existing ParameterGroupDeriver classification |
| Performance impact from many trivial auto-generated modules | LOW | LOW | Each module is a thin wrapper; TEAx pipeline overhead is per-module, not per-expression |

### 6. Phased Roadmap (Revised)

```
Phase 0 (Immediate): Approach E -- Modeling Discipline
  - Document 5 modeling rules as ADR
  - Apply to current models
  - No tooling changes
  - ALREADY PROVEN by CATF model

Phase 1: Expression Compiler (Closes "GAP: does NOT implement calc logic")
  Scope:
  - Shared expression reconstruction utility (refactor from constraint_extractor)
  - Expression compilability classifier
  - Auto-implementation generator for compilable CalcDefs
  - Handle BindingType.EXPRESSION in usage_extractor
  - Store expression ASTs on CalculationDefinitionData

  Impact:
  - ~30-40 of ~50 CalcDefs auto-implemented (no more handwritten _impl.py)
  - Remaining ~10-20 get better stubs (partial compilation with TODOs)
  - Generated IMPLEMENTATION_BACKLOG.md shrinks dramatically

  Changes:
  - extraction/expression_compiler.py (NEW)
  - extraction/extractor.py (upgrade _extract_expression_text)
  - extraction/data_models.py (add expression_asts field)
  - extraction/usage_extractor.py (handle EXPRESSION binding type)
  - generation/stencils.py (conditional auto-impl vs stub)
  - templates/implementation_stencil.py.jinja2 (conditional template)
  - resolution/models.py (add is_auto_implemented, compiled_expression)

Phase 2: Attribute Expression Capture (Reduces calc block overhead)
  Scope:
  - Extract computed attributes with expression ASTs
  - Generate synthetic CalcUsages from attribute expressions
  - Auto-implement the synthetic modules
  - Reduce need for explicit CalcDefs for simple formulas

  Impact:
  - Modelers write `attribute volume = pi*r^2*h` instead of full CalcDef
  - Aggregation expressions (`total = a + b + c`) don't need CalcDefs
  - Approach E Rule 3 becomes optional (codegen handles inline aggregation)

  Changes:
  - extraction/attribute_expression_extractor.py (NEW)
  - analysis/dependency_backtracker.py (resolve expression references)
  - generation/initialization.py (add attribute expression step)
  - Model pattern: attribute expressions become first-class pipeline nodes

Phase 3: Hierarchy, Multiplicity, Aggregation (Native nested patterns)
  Scope:
  - Part hierarchy extraction with multiplicity
  - :>> redefinition chain resolution
  - Tree-to-DAG flattening with synthetic rollup modules
  - Per-instance parameter context

  Impact:
  - Approach E Rules 1-4 become optional
  - Idiomatic SysML nested CalcUsage-in-PartDef pattern works natively
  - Model reuse across fusion concepts

  Changes:
  - extraction/usage_extractor.py (template detection, instantiation)
  - analysis/dependency_backtracker.py (redefinition chain resolution)
  - resolution/models.py (multiplicity field)
  - resolution/graph_builder.py (hierarchy-aware module generation)

  Trigger: When Approach E verbosity measurably impedes productivity
  (>15 explicit aggregation inputs, >15 non-uniform array instances,
  or cross-concept model reuse becomes a requirement)
```

### 7. Comparison: Original Recommendations vs. Revised

| Original Research | This Analysis | Rationale |
|-------------------|---------------|-----------|
| Phase 0: Approach E | Same | Proven, immediate |
| Phase 1: Approach C (plugin) | **SKIP** | Unnecessary bridge; go straight to expression compiler |
| Phase 2: Approach D Phase 1 (expression compiler) | **Phase 1: Approach F** (expanded expression compiler) | Broader scope: also handles attribute expressions and BindingType.EXPRESSION |
| Phase 3: Approach D Phase 2 (tree evaluator) | **Phase 3**: hierarchy/multiplicity/aggregation | Same end goal, but builds on expression compiler foundation |
| -- | **Phase 2: Attribute expression capture** (NEW) | Directly addresses user's "all math must be calc blocks" pain |

## Code References

### Existing expression infrastructure (ready to leverage)
- `extraction/constraint_extractor.py:137-171` -- Complete `_reconstruct_expression()` recursive dispatcher
- `extraction/constraint_extractor.py:174-203` -- `_reconstruct_operator_expression()` with 15+ operators
- `extraction/constraint_extractor.py:206-257` -- Feature reference and chain expression name extraction
- `extraction/constraint_extractor.py:33-50` -- `OPERATOR_MAP` constant
- `agentic_mbse/sysml/expression.py:119` -- `extract_feature_refs()` finds all variable references
- `agentic_mbse/sysml/expression.py:225` -- `extract_operators()` finds all operators
- `agentic_mbse/sysml/expression.py:374` -- `evaluate_true_static_expression()` evaluates constant expressions
- `agentic_mbse/sysml/binding.py:13` -- `classify_binding()` already classifies EXPRESSION type
- `agentic_mbse/sysml/binding.py:165-174` -- EXPRESSION binding populates `expression_ast` and `references`

### Current gaps to close
- `extraction/usage_extractor.py:327-332` -- `OperatorExpression` falls through to UNBOUND (should be EXPRESSION)
- `extraction/extractor.py:612-634` -- `_extract_expression_text()` partial, doesn't handle literals/chains/invocations
- `extraction/data_models.py:118` -- `calc_expressions: list[str]` stores strings, not ASTs
- `resolution/models.py:148-165` -- `PipelineModule` has no expression/compilability fields
- `generation/stencils.py:85-151` -- Always generates `NotImplementedError` stub

### Key data models involved
- `agentic_mbse/sysml/types.py:18-49` -- `BindingType` enum (EXPRESSION exists but unused in codegen)
- `agentic_mbse/sysml/types.py:170-221` -- `BindingInfo` with `expression_ast` and `references` fields
- `agentic_mbse/sysml/types.py:97-122` -- `ExpressionRef` with name, qualified_name, document_path
- `extraction/data_models.py:107-135` -- `CalculationDefinitionData` (needs expression_asts field)
- `extraction/usage_extractor.py:44-80` -- Codegen's `BindingInfo` dataclass (parallel to agentic-mbse's)
- `resolution/models.py:148-165` -- `PipelineModule` (needs is_auto_implemented, compiled_expression)

## Architecture Insights

### The Two BindingInfo Problem

There are **two separate `BindingInfo` classes**: one in `agentic_mbse.sysml.types` (Pydantic, with `expression_ast` and `references`) and one in `sysml_codegen.extraction.usage_extractor` (dataclass, with `source_instance_elem` and `raw_expression`). The agentic-mbse version already handles EXPRESSION bindings correctly via `classify_binding()` and `extract_bindings()`. The codegen version does NOT -- it falls through to UNBOUND.

**Recommendation:** Either (a) migrate codegen to use the agentic-mbse BindingInfo directly, or (b) port the EXPRESSION handling from `agentic_mbse.sysml.binding.extract_bindings()` into codegen's `_extract_single_binding()`. Option (b) is lower risk.

### Expression Reconstruction Already Exists in Three Places

1. `extractor._extract_expression_text()` -- partial (OperatorExpression + FeatureReference only)
2. `constraint_extractor._reconstruct_expression()` -- complete (all node types)
3. `agentic_mbse.sysml.expression` module -- evaluation-focused (static expressions only)

These should be consolidated. The constraint_extractor's implementation is the most complete for text reconstruction. The agentic-mbse module is best for semantic analysis (refs, operators, compilability). The expression compiler should combine both: use agentic-mbse for analysis, constraint_extractor's logic for code generation.

### Smart Regeneration Already Handles the Override Story

`generation/preservation.py` already implements signature-based comparison and timestamped backups. When an auto-implemented `_impl.py` is later hand-edited by a user (because they need to override the auto-generated logic), the preservation system will detect the signature match and preserve the handwritten version on subsequent codegen runs. This means auto-implementation is safe -- users can always override.

## Open Questions

1. **Should auto-implemented modules use a different base class or marker?** A `# AUTO-GENERATED -- DO NOT EDIT` header would help distinguish auto-impl from hand-edited. But the preservation system needs to handle transitions: auto-impl -> hand-edited -> auto-impl (if SysML changes).

2. **How should `**` (power) operator be handled?** SysML uses `^` for power; Python uses `**`. The OPERATOR_MAP in constraint_extractor has both. The expression compiler needs a Python-specific operator mapping.

3. **Should synthetic CalcUsages from attribute expressions be visible in the pipeline YAML?** They could be named `{part_name}__{attr_name}_calc` and appear as normal modules. Or they could be "virtual" and inlined. The former is simpler and more debuggable.

4. **What's the testing strategy for compiled expressions?** The existing `test_gen.py` generates runnable tests. Auto-implemented modules should pass these tests automatically (they compute the right thing by construction). But we need integration tests that verify the compiled expression matches the SysML source expression semantically.

5. **Should the expression compiler handle `if-then-else` (SelectExpression)?** SysML v2 supports conditional expressions. These would need `x if condition else y` in Python. Adding this significantly increases the compiler scope but covers a real modeling need (piecewise functions).
