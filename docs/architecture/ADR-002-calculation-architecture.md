# ADR-002: Calculation Architecture and Expression Handling

## Status
**Implemented** - 2025-12-28

## Context

The codegen pipeline transforms SysML v2 models into executable TEAx pipelines. A core architectural question is: **where are calculations defined, and how are different types of computational expressions handled?**

This ADR establishes the definitive specification for:
1. The location and form of calculation definitions
2. How different expression types are processed
3. The evaluation strategy for each expression type

### Background

SysML v2 supports multiple ways to express computed values:

```sysml
// Pattern 1: Calc def with expression (in library/)
calc def TorusVolume {
    in major_radius : Real;
    in minor_radius : Real;
    out volume : Real = 2.0 * π² * major_radius * minor_radius²;
}

// Pattern 2: Inline expression in design attribute
part plasma_region {
    attribute volume : Real = 2.0 * π² * R * a * a * κ;
}

// Pattern 3: Calc usage binding
calc vol_calc : TorusVolume {
    in major_radius = system.R;
}
```

The original codegen pipeline only handled Pattern 1 (calc defs) and Pattern 3 (bindings). Pattern 2 (inline expressions in design files) was extracted as string text but never evaluated, causing null values in downstream calculations.

### Semantic Distinction

Analysis revealed two fundamentally different categories of inline expressions:

| Category | Location | Count | Semantic Role | Evaluation |
|----------|----------|-------|---------------|------------|
| **Algorithm expressions** | Inside `calc def` blocks | 25 | Define calculation logic | Runtime (handwritten impl) |
| **Derived geometry** | In `designs/` attributes | 30 | Compute constants from literals | Static (extraction time) |

The 25 library expressions are NOT a problem - they define algorithm logic handled by handwritten `_impl.py` files. The codegen intentionally extracts only the interface (inputs/outputs) from calc defs.

The 30 design expressions ARE the problem - they compute geometry values (volumes, areas) that downstream modules need, but they were stringified and never evaluated.

**Critical Finding**: All 30 design expressions resolve transitively to literal constants. They form a closed dependency graph within `radial_build.sysml`:
- `minor_radius = (inner_radius + outer_radius) / 2.0 - major_radius`
- `volume = 2π²Ra²κ` (depends on `minor_radius`)
- Both evaluate to constants because all operands are literals.

## Decision

### Core Principle

> **Calculation definitions belong in `library/`. Design files contain values and wiring. Expressions that resolve to constants are evaluated at extraction time.**

This establishes a clear separation of concerns:
- `library/` = Reusable algorithms (behaviors)
- `designs/` = Configuration (values)

### Calculation Location Rules

#### Rule 1: Calc Defs in Library Only

All `calc def` declarations SHALL be in `models/library/`:

```sysml
// CORRECT: library/physics/power_balance.sysml
package FusionPhysics_PowerBalance {
    calc def AlphaNeutronSplit {
        in p_fusion : Real;
        out p_alpha : Real = p_fusion * 3.52 / 17.58;
        out p_neutron : Real = p_fusion * 14.06 / 17.58;
    }
}
```

```sysml
// INCORRECT: designs/catf_mfe/physics.sysml
calc def LocalCalc { ... }  // ERROR: Calc defs not allowed in designs/
```

**Rationale**:
- Calc defs are reusable algorithms that require testing, documentation, and implementation
- Placing them in library/ ensures they're properly managed as shared components
- The codegen generates module stubs and stencils for library calc defs

#### Rule 2: Calc Usages Wire to Design Values

Calc usages in `designs/` instantiate library calc defs and bind inputs to design values:

```sysml
// designs/catf_mfe/physics.sysml
package CATFMFEPhysics {
    part catf_physics {
        attribute p_fusion : Real = 2600.0 [MW];  // Entry point

        calc alpha_neutron_split : AlphaNeutronSplit {
            in p_fusion = catf_physics::p_fusion;  // Wiring
        }
    }
}
```

**Rationale**: Calc usages are the mechanism for connecting design-specific values to reusable algorithms.

#### Rule 3: Design Attributes Contain Values, Not Computations

Design attributes SHALL contain:
- **Literal values**: Entry points for the pipeline (including unit annotations like `3.0 [m]`)
- **Bindings to calc outputs**: Wiring via EXPOSE pattern (see Rule 3 Amendment below)
- **True static expressions**: Expressions containing ONLY literals and arithmetic operators

Design attributes SHALL NOT contain:
- **Derived expressions**: Expressions referencing other design attributes (e.g., `diameter = radius * 2.0`)
- **Computations on calc outputs**: Expressions that modify calc output values (e.g., `power * 0.95`)

```sysml
// designs/catf_mfe/radial_build.sysml
part plasma_region {
    // ✅ Literal values (entry points)
    attribute inner_radius : Real = 3.0 [m];
    attribute major_radius : Real = 3.0 [m];

    // ✅ True static expressions (only literals)
    attribute pi_squared : Real = 3.14159 * 3.14159;

    // ❌ VIOLATION: Derived expression (references design attributes)
    // attribute minor_radius : Real = (inner_radius + outer_radius) / 2.0 - major_radius;
    // → Must be refactored to a calc def in library/
}
```

**Definition: True Static Expression**

An expression is "true static" if it contains:
1. Only literal values (numbers, strings, booleans)
2. Standard library references (SI::, ISQ::, ScalarValues::, UnitsAndScales::)
3. Arithmetic operators combining the above

**Structural Check**: `len(extract_feature_refs(expr)) == 0` after filtering standard library references.

**Standard Library Exemption**: References to SI units (like `SI::metre` in `3.0 [m]`), ISQ quantity types, and ScalarValues are NOT considered derived expressions. They are constant type references, not design-specific values.

| Expression | Feature Refs | Classification | V2 Result |
|------------|-------------|----------------|-----------|
| `= 3.0` | 0 | Literal | ✅ PASS |
| `= 3.0 [m]` | 0 (SI::metre filtered) | True Static | ✅ PASS |
| `= 3.14159 * 2.0` | 0 | True Static | ✅ PASS |
| `= radius * 2.0` | 1 (radius) | Derived | ❌ FAIL |
| `= my_calc.output` | 1 (EXPOSE) | EXPOSE Pattern | ✅ PASS |
| `= my_calc.output * 0.95` | 1 | Computation | ❌ FAIL |

#### Rule 3 Amendment: EXPOSE Pattern Exemption

Design attributes may reference calc outputs when following the **EXPOSE pattern**:

```sysml
part subsystem {
    calc instance_name : CalcDefFromLibrary {
        in some_input = ...;
    }

    // EXPOSE pattern: expose calc output at part boundary
    attribute exposed_name : Real = instance_name.calc_output;
}
```

**Why This Is Permitted**:
1. **No new computation**: The expression is pure value propagation, not calculation
2. **Preserves ADR-002 intent**: Calc defs remain in library/; this is just wiring
3. **Enables encapsulation**: Consumers bind to `subsystem.exposed_name` without knowing internal calc structure
4. **SysMLv2 recommended**: This pattern is officially recommended for exposing internal outputs

**Detection Criteria** (V2 check exemption):
1. Expression is a `FeatureChainExpression` (pattern: `instance.output`)
2. The intermediate element is a `CalculationUsage` in the same owner part
3. The target is a known calc output from a library calc def

**Examples**:

```sysml
// ALLOWED (EXPOSE pattern - pure value propagation)
attribute wall_plug_power : Real = wall_plug.wall_plug_power;

// VIOLATION (computation on calc output)
attribute adjusted_power : Real = wall_plug.wall_plug_power * 0.95;

// VIOLATION (multiple calc outputs combined)
attribute total_power : Real = calc1.output + calc2.output;
```

**Rationale**: The EXPOSE pattern is semantically different from actual V2 violations. While both reference calc outputs, EXPOSE is pure value propagation that enables clean cross-file interfaces without introducing unauthorized computation in design files.

### Expression Evaluation Strategy

#### Evaluation Taxonomy

| Expression Type | Location | Operands | Evaluation Time | Handler |
|-----------------|----------|----------|-----------------|---------|
| **Calc def formula** | `library/` calc def | Inputs | Runtime | Handwritten `_impl.py` |
| **Static expression** | `designs/` attribute | All resolve to literals | Extraction | Static evaluator |
| **Binding reference** | Calc usage binding | N/A (wiring) | N/A | Binding resolver |
| **Dynamic expression** | `designs/` attribute | Includes calc outputs | **Error** | Requires calc def |

#### Static Expression Evaluation

Static expressions are expressions where **all operands resolve transitively to literal values**.

**Definition**: An expression is static if:
1. All `LiteralRational`/`LiteralInteger` operands are constants
2. All `FeatureReferenceExpression` operands reference attributes that are themselves static
3. All `FeatureChainExpression` operands reference attributes that are static
4. No operand references a calc output (computed value)

**Evaluation Process**:

```python
def evaluate_static_expression(expr, context: dict[str, float]) -> float:
    """
    Evaluate an expression to a numeric constant.
    Raises StaticEvaluationError if any operand cannot be resolved.
    """
    if is_literal(expr):
        return extract_literal_value(expr)

    if is_unit_annotation(expr):  # operator == '['
        return evaluate_static_expression(first_operand(expr), context)

    if is_feature_reference(expr):
        name = expr.referent.declared_name
        if name not in context:
            raise StaticEvaluationError(f"Cannot resolve '{name}' to literal")
        return context[name]

    if is_operator_expression(expr):
        values = [evaluate_static_expression(op, context) for op in expr.operands]
        return apply_operator(expr.operator, values)

    raise StaticEvaluationError(f"Unsupported expression type: {type(expr)}")
```

**Dependency Ordering**: Expressions within a part SHALL be evaluated in topological order:

```
1. inner_radius = 3.0        → context["inner_radius"] = 3.0
2. outer_radius = 4.1        → context["outer_radius"] = 4.1
3. major_radius = 3.0        → context["major_radius"] = 3.0
4. minor_radius = (i + o)/2 - R  → context["minor_radius"] = 0.55
5. volume = 2π²Ra²κ          → context["volume"] = 53.74
```

**Cross-Part References**: Expressions may reference attributes from other parts using `FeatureChainExpression`:

```sysml
attribute first_wall_area : Real = 2π * major_radius *
    (plasma_region.outer_radius - major_radius) * elongation;
```

These are resolved by looking up the referenced part's context.

#### Dynamic Expression Error

If an expression references a calc output (computed value), it cannot be statically evaluated. This SHALL produce an extraction error:

```sysml
// ERROR: Cannot statically evaluate - depends on calc output
part system {
    attribute p_net : Real = gross_power_calc.p_gross - parasitic_power;
}
```

**Resolution**: Convert to a calc def in library/:

```sysml
// library/power_balance.sysml
calc def NetPower {
    in p_gross : Real;
    in p_parasitic : Real;
    out p_net : Real = p_gross - p_parasitic;
}

// designs/physics.sysml
calc net_power : NetPower {
    in p_gross = gross_power_calc.p_gross;
    in p_parasitic = parasitic_power;
}
attribute p_net : Real = net_power.p_net;
```

### Unit Handling

Units (e.g., `= 3.0 [m]`) are parsed as `OperatorExpression` with operator `[`. The static evaluator:
1. Recognizes unit annotation operator
2. Extracts the numeric value from the first operand
3. Preserves unit metadata for documentation (not computation)

```sysml
attribute major_radius : Real = 3.0 [m];
// AST: OperatorExpression(operator='[', operands=[LiteralRational(3.0), FeatureRef('m')])
// Evaluated: 3.0 (unit 'm' stored as metadata)
```

### Supported Operators

Static evaluation SHALL support these arithmetic operators:

| Operator | Behavior | Example |
|----------|----------|---------|
| `+` | Addition | `a + b` |
| `-` | Subtraction (binary) | `a - b` |
| `-` | Negation (unary) | `-a` |
| `*` | Multiplication | `a * b` |
| `/` | Division | `a / b` |
| `[` | Unit annotation | `3.0 [m]` |

**Not Supported** (require calc def):
- Exponentiation (`**`, `^`)
- Functions (`sin`, `cos`, `sqrt`)
- Conditionals (`if`, `?:`)

### Integration with Codegen Pipeline

#### Extraction Phase (Job 1)

1. Parse SysML files using SysIDE
2. For each `AttributeUsage` in design files:
   - If literal value → extract as `DesignAttributeData`
   - If binding reference → extract source path
   - If arithmetic expression → attempt static evaluation
     - Success → store numeric value as `default_value`
     - Failure → raise `StaticEvaluationError` with guidance

#### Classification Phase (Job 2)

Static expressions result in numeric `default_value`, making them indistinguishable from literals for classification purposes. This is correct - they ARE constants.

#### Module Generation (Job 3)

No changes. Static expressions don't generate modules - they're constants.

#### Pipeline Generation (Job 4)

Static expressions appear in entry point JSON as numeric values:

```json
{
  "CATFMFERadialBuild__plasma_region__volume": 53.74,
  "CATFMFERadialBuild__plasma_region__minor_radius": 0.55
}
```

### Validation Rules

The extraction phase SHALL enforce these rules:

| Rule | Condition | Error Message |
|------|-----------|---------------|
| V1 | Calc def in designs/ | "Calculation definitions must be in library/, not designs/" |
| V2 | Static eval failure | "Expression '{expr}' cannot be statically evaluated. Operand '{name}' is not a literal. Consider extracting to a calc def in library/." |
| V3 | Circular reference | "Circular dependency detected: {cycle}" |
| V4 | Unknown operator | "Unsupported operator '{op}' in static expression. Use calc def for complex calculations." |

### Relationship to ADR-001

This ADR complements ADR-001 (Input Parameter Definition):

| ADR-001 Concept | ADR-002 Clarification |
|-----------------|----------------------|
| Type 1: LIBRARY DEFAULT | Calc def inputs with defaults, used when binding omitted |
| Type 2: DESIGN ATTRIBUTE | Literal values AND statically-evaluated expressions |
| Type 3: USAGE LITERAL | Literal values in calc usage bindings |

**Key Addition**: Statically-evaluated expressions become Type 2 entry points. From the pipeline's perspective, `volume = 53.74` (computed) is indistinguishable from `volume = 53.74` (literal).

## Consequences

### Positive

1. **Clear architecture**: Calc defs in library/, values in designs/
2. **No null values**: Geometry expressions are evaluated to constants
3. **Semantic clarity**: Expressions that ARE constants are treated as constants
4. **Validation**: Dynamic expressions caught early with actionable guidance
5. **Minimal complexity**: Static evaluation at extraction, no new runtime concepts
6. **Backward compatible**: Existing literals and bindings unchanged

### Negative

1. **Modeling constraint**: Complex expressions require calc def refactoring
2. **Limited operators**: Only arithmetic; functions need calc defs
3. **Static limitation**: Cannot express design attributes that depend on calc outputs without calc def

### Implementation Requirements

#### Phase 1: Static Evaluator (~4 hours)

Add to `scripts/codegen/parameter_group_derivation.py`:

```python
class StaticEvaluationError(Exception):
    """Raised when an expression cannot be statically evaluated."""
    pass

def evaluate_static_expression(
    expr,
    context: dict[str, float],
    all_parts: dict[str, dict[str, float]]
) -> float:
    """Evaluate an expression to a numeric constant."""
    # Implementation per Decision section
```

#### Phase 2: Integration with Extraction (~4 hours)

1. In `_extract_single_attribute()`:
   - Detect `OperatorExpression` value
   - Build context from already-processed attributes
   - Call `evaluate_static_expression()`
   - Store numeric result in `default_value`
   - Catch `StaticEvaluationError` and re-raise with guidance

2. Add topological sort for attribute processing order within each part

#### Phase 3: Cross-Part Resolution (~2 hours)

1. Build part contexts for all parts before evaluating cross-references
2. Handle `FeatureChainExpression` by looking up target part context

#### Phase 4: Validation & Testing (~2 hours)

1. Add tests for all 30 radial build expressions
2. Verify MagnetCryogenicLoad receives correct geometry values
3. Add test for dynamic expression error case

## Examples

### Example 1: Radial Build Geometry (Current Problem Solved)

```sysml
// models/designs/catf_mfe/radial_build.sysml
part catf_radial_build {
    attribute major_radius : Real = 3.0 [m];
    attribute elongation : Real = 3.0;

    part plasma_region {
        attribute inner_radius : Real = 3.0 [m];
        attribute outer_radius : Real = 4.1 [m];

        // These expressions are statically evaluated:
        attribute minor_radius : Real =
            (inner_radius + outer_radius) / 2.0 - major_radius;
            // → 0.55

        attribute volume : Real =
            2.0 * 3.14159265359 * 3.14159265359 *
            major_radius * minor_radius * minor_radius * elongation;
            // → 53.74
    }
}
```

**Extraction Result**:
```python
DesignAttributeData(
    name="volume",
    sysml_type="Real",
    default_value="53.74",  # Numeric, not string expression
    parent_part="plasma_region",
    qualified_name="CATFMFERadialBuild__plasma_region__volume"
)
```

### Example 2: Dynamic Expression Error

```sysml
// ERROR CASE
part system {
    calc thermal_cycle : ThermalCycleEfficiency { ... }

    // This CANNOT be statically evaluated
    attribute plant_output : Real =
        thermal_cycle.p_thermal * 0.95;  // Depends on calc output!
}
```

**Extraction Error**:
```
StaticEvaluationError: Expression 'thermal_cycle.p_thermal * 0.95' cannot be
statically evaluated. Operand 'thermal_cycle.p_thermal' is a calculation output,
not a literal.

Guidance: Extract this calculation to a calc def in library/:

  calc def PlantOutput {
      in p_thermal : Real;
      in efficiency : Real = 0.95;
      out p_output : Real = p_thermal * efficiency;
  }

Then use a calc usage in your design file.
```

### Example 3: Complex Calculation Stays in Library

```sysml
// models/library/analyses/thermal_loads.sysml
calc def MagnetCryogenicLoad {
    doc /* Uses geometry values as inputs - these are entry points */

    in magnet_volume : Real;          // From radial_build (statically evaluated)
    in first_wall_area : Real;        // From radial_build (statically evaluated)
    in magnet_surface_area : Real;    // From radial_build (statically evaluated)

    // Complex calculation with multiple intermediate values
    attribute neutron_heating : Real = ...;
    attribute surface_heat_load : Real = ...;
    attribute conduction_load : Real = ...;

    out cooling_power : Real =
        (neutron_heating + surface_heat_load + conduction_load) / carnot_efficiency;
}
```

**This is correctly a calc def** because:
- It's a reusable algorithm (thermal load calculation)
- It needs testing and documentation
- It has intermediate values and complex logic
- The geometry inputs ARE now statically evaluated, so they're available as entry points

## Implementation Notes

**Completed**: 2025-12-28

### Key Implementation Files
- Static evaluator: `sysml_utils/expression.py`
- V1/V2/V4 checks: `scripts/sysml_checks/adr002_checks.py`
- Geometry calc defs: `models/library/physics/geometry.sysml`
- Entry point deduplication: `scripts/codegen/parameter_group_derivation.py`
- EXPOSE pattern detection: `sysml_utils/expose_utils.py`

### Test Coverage
- Static evaluator tests: `tests/test_sysml_utils/test_expression.py` (24 tests)
- EXPOSE pattern tests: `tests/test_expose_pattern.py` (10 tests)
- V1/V2/V4 validation tests: `tests/test_adr002.py` (17 tests)
- Parameter group tests: `tests/test_parameter_group_derivation.py`
- Full test suite: 878 tests pass

### Deviations from Original Design
1. **Part 2.6 Amendment**: Added prohibition on derived expressions (not just dynamic expressions). Derived expressions reference other design attributes (e.g., `diameter = radius * 2.0`) and must be refactored to calc defs.
2. **EXPOSE Pattern Exemption**: Added exemption for pure value propagation from calc outputs. Design attributes may reference sibling calc outputs via the EXPOSE pattern (e.g., `attribute p_thermal = blanket_calc.p_thermal`).
3. **Pipeline Refactor (Part 5)**: Created single source of truth architecture with unified graph builder and identifier system per ADR-003.
4. **Static Evaluation Scope**: Limited to arithmetic operators (`+`, `-`, `*`, `/`, `[`). Functions and exponentiation require calc defs.

## Amendment: FORMULA Computed Attributes (2026-02-09)

### Context

The ATTR-EXPR epic (Phase 2) adds support for attribute-level expressions that reference sibling attributes on the same part. These are classified as FORMULA computed attributes per ADR-005. This amendment relaxes Rule 3 to permit FORMULA patterns and documents the pipeline treatment, conditions, and modeling guidance.

### Rule 3 Amendment

Design attributes MAY contain arithmetic expressions referencing only sibling attributes on the same part (FORMULA pattern per ADR-005). These expressions generate synthetic pipeline modules with auto-implemented code (see ADR-004).

**Conditions** -- ALL of the following must hold for the FORMULA exemption:
- All feature references MUST resolve to sibling attributes (same owning part)
- No `FeatureChainExpression` nodes (no calc output references, no cross-part references)
- Supported operators: `+`, `-`, `*`, `/`

**Pipeline treatment**: FORMULA expressions generate synthetic `PipelineModule` instances. The Phase 1 expression compiler processes the attribute's AST and produces auto-implemented Python code. The module's literal-valued sibling inputs become DESIGN_ATTRIBUTE entry points (per ADR-001 Type 2). See ADR-004 for full pipeline integration details.

### Updated Expression Taxonomy

The original "Derived expression" row is split into two categories:

| Expression | Feature Refs | Classification | Result |
|------------|-------------|----------------|--------|
| `= 3.0` | 0 | Literal | PASS |
| `= 3.0 [m]` | 0 (SI::metre filtered) | True Static | PASS |
| `= 3.14159 * 2.0` | 0 | True Static | PASS |
| `= length * width` | >=1 (sibling attrs only) | **FORMULA expression** | **PASS** (generates pipeline module) |
| `= radius * 2.0` (where radius is a sibling) | >=1 (sibling attrs only) | **FORMULA expression** | **PASS** (generates pipeline module) |
| `= my_calc.output` | 1 (EXPOSE) | EXPOSE Pattern | PASS |
| `= my_calc.output * 0.95` | 1 (calc output + arithmetic) | **Derived expression** | FAIL (requires CalcDef) |
| `= calc1.output + calc2.output` | >=1 (calc output refs) | **Derived expression** | FAIL (requires CalcDef) |

The key distinction: FORMULA expressions reference **only sibling attributes** (same part, no dotted paths). Derived expressions reference **calc outputs** (via `FeatureChainExpression`). The classifier uses `ref.qualified_name` to distinguish these cases reliably (see ADR-005, Decision 3).

### Known UX Gap: EXPOSE_COMPUTED

After this amendment, this works:
```sysml
attribute area : Real = length * width;                    // FORMULA -- works!
```

But this does NOT:
```sysml
attribute adjusted_cost : Real = cost_calc.total * 1.15;   // EXPOSE_COMPUTED -- deferred
```

From a modeler's perspective, these look similar -- both are "attribute equals expression." The distinction (sibling attribute refs vs. calc output refs) is an implementation detail of how SysIDE represents dotted paths. This is documented as a known UX gap in ADR-005.

**Workaround**: Create a CalcDef for the adjustment. Phase 1 auto-implements it, so no handwritten `_impl.py` is needed.

**Future resolution**: The decomposition strategy (resolve FeatureChainExpression to upstream channel, compile remaining expression as FORMULA) is technically tractable and would be added if modelers hit this gap frequently.

### Modeling Guidance

**Rule**: Attribute expressions can reference sibling attributes on the same part. To reference a calc output, use the EXPOSE pattern (pure alias, no arithmetic) or create a CalcDef.

**When to use attribute expressions (FORMULA)**:
- One-off simple formula tied to a specific design part
- Arithmetic on sibling attributes only (`+`, `-`, `*`, `/`)
- Examples: `attribute area = length * width`, `attribute total_cost = a + b + c`, `attribute p_net_kw = p_net_mw * 1000.0`

**When to use CalcDefs**:
- Reusable calculations shared across multiple parts
- Complex logic with multiple intermediate values
- References to calc outputs (requires `FeatureChainExpression`)
- Functions, conditionals, or operators beyond basic arithmetic

**Examples of what works (FORMULA)**:
```sysml
part plant {
    attribute length : Real = 10.0;
    attribute width : Real = 5.0;
    attribute area : Real = length * width;           // FORMULA: siblings only
    attribute cost : Real = area * 12.0;              // FORMULA: chain is fine
    attribute p_net_kw : Real = p_net_mw * 1000.0;   // FORMULA: unit conversion
}
```

**Examples of what doesn't work yet (EXPOSE_COMPUTED)**:
```sysml
part plant {
    calc cost_calc : TotalCostCalc { ... }
    attribute adjusted : Real = cost_calc.total * 1.15;   // EXPOSE_COMPUTED: deferred
    attribute combined : Real = cost_calc.a + cost_calc.b; // EXPOSE_COMPUTED: deferred
}
```

**Workaround for EXPOSE_COMPUTED patterns**:
```sysml
// Instead of: attribute adjusted = cost_calc.total * 1.15
// Create a CalcDef (Phase 1 auto-implements it):
calc def AdjustedCost {
    in total : Real;
    in factor : Real = 1.15;
    out adjusted : Real = total * factor;
}

calc adjusted_cost : AdjustedCost {
    in total = cost_calc.total;
}
attribute adjusted : Real = adjusted_cost.adjusted;  // EXPOSE_PURE: works!
```

## References

- **ADR-001**: `docs/architecture/ADR-001-input-parameter-definition.md` - Input parameter taxonomy
- **ADR-004**: `docs/architecture/ADR-004-computed-attribute-pipeline-integration.md` - Computed attribute pipeline integration (Option C, Step 4.5, module naming, backtracker)
- **ADR-005**: `docs/architecture/ADR-005-computed-attribute-classification.md` - Computed attribute classification scheme (FORMULA, EXPOSE_PURE, EXPOSE_COMPUTED, LITERAL, UNRESOLVABLE)
- **Study 1**: `docs/codegen/STUDY_1_EXTRACTION.md` - Gap G1 analysis
- **Study 4**: `docs/codegen/STUDY_4_PIPELINE.md` - Inline calculation impact
- **Foundation**: `docs/codegen/FOUNDATION.md` - Pipeline architecture
- **Analysis**: `project/active/adr002-inline-calculations/design_alternatives.md` - Options evaluated
- **Opinion**: `project/active/adr002-inline-calculations/opinion.md` - Decision rationale

## Changelog

| Date | Change |
|------|--------|
| 2026-02-09 | **Amendment: FORMULA computed attributes permitted** (Rule 3 relaxation). Design attributes MAY contain arithmetic on sibling attributes, generating synthetic pipeline modules. Updated expression taxonomy. Documented EXPOSE_COMPUTED UX gap with workaround. Added modeling guidance. See ADR-004 for pipeline integration, ADR-005 for classification scheme. |
| 2025-12-28 | **Implemented**: All parts complete. Added Implementation Notes section documenting key files, test coverage (878 tests), and deviations from original design |
| 2025-12-22 | Amendment: Prohibited derived expressions in Rule 3; clarified "true static" definition; added structural check and standard library exemption documentation |
| 2025-12-22 | Amendment: Added EXPOSE pattern exemption (Rule 3 Amendment) for pure value propagation from sibling calc outputs |
| 2025-12-21 | Initial version - established calculation architecture and static expression evaluation |
