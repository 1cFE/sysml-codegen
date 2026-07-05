# Design: Attribute Expression AST Discovery & Architecture Evaluation

**Status:** Complete
**Owner:** Reid Westwood
**Created:** 2026-02-08
**Branch:** cost-pattern
**Epic:** ATTR-EXPR Item 1

---

## Overview

Design a standalone spike script (`scripts/spike_attribute_expressions.py`) that inspects SysIDE API responses for PartDef attribute elements, inventories expression patterns across 3 model suites, attempts compilation using the Phase 1 expression compiler, and produces a structured report answering 7 research questions to gate the ATTR-EXPR epic.

## Related Artifacts

- **Spec:** `.project/active/attr-expr-spike/spec.md`
- **Epic:** `.project/backlog/epic_attribute_expression_capture.md`
- **Phase 1 AST Spike:** `.project/active/expr-spike-ast/report.md`
- **Phase 1 Compile Spike:** `.project/active/expr-spike-compile/report.md`
- **Research:** `.project/research/20260202-180000_expression-compilation-and-inline-math-strategy.md`

---

## Research Findings

### Existing Spike Infrastructure

Four Phase 1 spike scripts establish the pattern:
- `scripts/spike_extract_expression_asts.py` -- iterates CalcDef outputs, checks `feature_value_expression`, reports AST depth/node types
- `scripts/spike_resolve_expression_refs.py` -- extracts feature references, cross-checks with AST node counts
- `scripts/spike_compile_expressions.py` -- compiles CalcDef output expressions to Python, validates against ground truth
- `scripts/spike_classify_compilability.py` -- classifies CalcDefs as FULLY/PARTIALLY/MANUAL_REQUIRED

All scripts share a common pattern:
1. Load model via `SysMLDataExtractor` + `load_models()`
2. Get raw elements via `adapter.elements_of_type(model, "CalculationDefinition")`
3. Iterate `owned_members`, filter by `adapter.is_instance(member, "AttributeUsage")`
4. Access `member.feature_value_expression` for AST nodes
5. Use `extract_feature_refs()`, `traverse_expression()`, `extract_operators()` from `agentic_mbse.sysml.expression`

### Current Attribute Extraction Gap

`extractor.py:339-371` (`_extract_attribute()`) extracts literal defaults via `_extract_default_value()` (`extractor.py:373-394`) but discards any expression AST. `_extract_literal_value()` (`extractor.py:396-410`) handles only `LiteralRational`, `LiteralInteger`, `LiteralBoolean`, `LiteralString`. Non-literal expressions (OperatorExpression, FeatureReferenceExpression, etc.) return `None`, losing the expression entirely.

`AttributeInfo` (`data_models.py:33-60`) stores `default_value: str | None` but has no field for expression ASTs.

### Phase 1 Expression Compiler (expression_compiler.py)

`build_expression_ast()` (`expression_compiler.py:284-399`) accepts raw syside AST nodes and produces an `ExpressionAST` IR. It resolves references against `input_names`, `output_names`, and optionally `all_member_names`. It is explicitly CalcDef-agnostic -- there is nothing in the function that requires the context to be a CalcDef.

`compile_expression()` (`expression_compiler.py:181-219`) converts `ExpressionAST` IR to Python expression strings. Input references become `inputs.{name}`; intermediate references become bare variable names.

Key question for the spike: when applied to PartDef attribute expressions, what should `input_names` be? For CalcDefs, it's the declared `in` attributes. For PartDefs, it would be sibling attributes on the same part. The spike should test this mapping.

### Fixture Model Attribute Patterns

**solar_battery `design.sysml:60`:**
```sysml
attribute p_net_kw : Real = p_net_mw * 1000.0;  // FORMULA pattern
```
9 other attributes are pure literals (e.g., `p_net_mw = 0.008`, `plant_lifetime = 25.0`).

**CATF `physics.sysml:114-122`:**
```sysml
attribute p_alpha_out : Real = alpha_neutron_split.p_alpha;        // EXPOSE pattern
attribute p_neutron_out : Real = alpha_neutron_split.p_neutron;    // EXPOSE pattern
attribute p_thermal_out : Real = blanket_thermal.p_thermal;        // EXPOSE pattern
...
```
9 EXPOSE-pattern attributes referencing CalcUsage outputs via dot notation. 8 literal attributes (e.g., `p_fusion = 2600.0`).

**CATF `system.sysml:204`:**
```sysml
attribute auxiliary_power : Real = auxiliary_load.auxiliary_power;  // EXPOSE pattern
```

**CATF `magnets.sysml:96`, `blanket.sysml:209`:**
```sysml
attribute cooling_power : Real = cryo_load.cooling_power;    // EXPOSE pattern
attribute pump_power : Real = pump_load.pump_power;          // EXPOSE pattern
```

**chain_spike `design.sysml:7-10`:**
```sysml
attribute length : Real = 10.0;   // LITERAL
attribute width : Real = 5.0;     // LITERAL
attribute rate : Real = 12.0;     // LITERAL
attribute scale : Real = 1.0;     // LITERAL
```
All 4 are pure literals, no computed attributes.

**CATF has many more attributes** across magnets, blanket, shield, etc. -- predominantly literals with unit annotations (e.g., `0.4 [m]`, `20 [K]`). The EXPOSE patterns are concentrated in physics.sysml, system.sysml, magnets.sysml, and blanket.sysml.

### SysIDE API Access Pattern for PartDef Attributes

To inspect PartDef attributes, the spike needs to iterate `PartUsage` or `PartDefinition` elements, not CalcDefinitions. The existing spike scripts iterate CalcDefs. The new spike must:

1. Use `adapter.elements_of_type(model, "PartDefinition")` to find PartDefs
2. Additionally iterate `PartUsage` elements (since solar_battery uses `part solar_battery_plant : 'Solar Battery Plant'`, which is a PartUsage)
3. For each part's `owned_members`, filter `AttributeUsage` elements
4. Check `member.feature_value_expression` on each attribute
5. Use `traverse_expression()` to classify the expression structure

The critical unknown: Phase 1 proved `feature_value_expression` exists on CalcDef output attributes. The spike must verify this on PartDef/PartUsage attributes.

---

## Proposed Design

### Architecture: Single Self-Contained Spike Script

Following the Phase 1 spike pattern, the deliverable is a single script `scripts/spike_attribute_expressions.py` that:
1. Loads each model suite via `SysMLDataExtractor`
2. Iterates all PartDef/PartUsage elements and their attribute members
3. Inspects each attribute's `feature_value_expression`
4. Classifies attributes (FORMULA / EXPOSE / LITERAL / UNRESOLVABLE)
5. Attempts compilation of at least one expression using Phase 1's compiler
6. Produces a structured text report answering Q1-Q7

The script does NOT modify any production code.

### Script Structure

```
scripts/spike_attribute_expressions.py
├── Data classes (AttributeExprInfo, SuiteResult, PatternInventory)
├── Model loading (reuses existing load_and_extract pattern)
├── Q1: AST Availability
│   ├── iterate_part_attributes() -- get all PartDef/PartUsage attribute members
│   ├── check_feature_value_expression() -- does it exist? what root node type?
│   └── report_ast_availability() -- per-suite table
├── Q2: Reference Resolution
│   ├── extract_and_classify_refs() -- use extract_feature_refs()
│   ├── classify_ref_target() -- sibling attribute? calc output? unknown?
│   └── report_reference_resolution() -- per-attribute ref table
├── Q3: EXPOSE Pattern
│   ├── detect_expose_pattern() -- single FeatureChainExpression or FeatureReferenceExpression to calc output
│   ├── check_backtracker_overlap() -- does existing resolution handle this?
│   └── report_expose_analysis()
├── Q4: Cross-Part References
│   ├── detect_cross_part_refs() -- references with dotted paths to other parts
│   └── report_cross_part_analysis()
├── Q5: Pattern Inventory
│   ├── classify_attribute() -- FORMULA / EXPOSE / MIXED / LITERAL / UNRESOLVABLE
│   └── report_pattern_inventory() -- per-model table
├── Q6: Compiler Reuse
│   ├── attempt_compilation() -- call build_expression_ast() + compile_expression()
│   └── report_compiler_reuse() -- what worked, what failed, why
├── Q7: Architecture Evaluation
│   └── report_architecture_recommendation() -- grounded in Q1-Q6 findings
└── Main
    ├── DEFAULT_SUITES -- solar_battery, catf_mfe, chain_spike
    └── run_all_questions() -- orchestrate and print report
```

### Component Details

#### 1. Data Classes

```python
@dataclass
class AttributeExprInfo:
    part_name: str            # owning PartDef/PartUsage name
    attr_name: str            # attribute name
    has_expression: bool      # feature_value_expression exists
    root_node_type: str       # type(expr).__name__ or ""
    is_literal_only: bool     # expression is pure literal (no refs)
    classification: str       # FORMULA / EXPOSE / LITERAL / UNRESOLVABLE
    ref_names: list[str]      # resolved reference names
    ref_qualified_names: list[str]  # qualified names for references
    depth: int                # AST depth
    node_types: list[str]     # all node types in AST
    operators: list[str]      # all operators in AST
    compiled_python: str | None  # compiled expression or None
    compilation_error: str | None  # error message if compilation failed

@dataclass
class SuiteResult:
    suite_name: str
    model_paths: list[Path]
    attributes: list[AttributeExprInfo]
    part_count: int
    error: str | None = None
```

#### 2. Model Loading and Attribute Iteration

Reuse `load_and_extract()` from existing spike scripts. Extend to iterate parts:

```python
def load_and_iterate_parts(model_paths: list[Path]):
    """Load model, return all part elements with their attribute members."""
    extractor = SysMLDataExtractor(model_paths)
    if not extractor.load_models():
        return [], None

    parts = []
    # Try both PartDefinition and PartUsage
    for type_name in ("PartDefinition", "PartUsage"):
        for elem in extractor.adapter.elements_of_type(extractor.model, type_name):
            parts.append(elem)

    return parts, extractor.adapter
```

For each part, iterate `owned_members` filtering `AttributeUsage`:

```python
def inspect_attribute(adapter, part_elem, attr_member) -> AttributeExprInfo:
    """Inspect a single attribute member on a PartDef/PartUsage."""
    expr = getattr(attr_member, 'feature_value_expression', None)
    has_expression = expr is not None

    if not has_expression:
        return AttributeExprInfo(
            part_name=sanitize_name(part_elem.name),
            attr_name=sanitize_name(attr_member.name),
            has_expression=False,
            root_node_type="",
            is_literal_only=True,
            classification="NO_EXPRESSION",
            ...
        )

    # Analyze expression: node types, depth, operators, references
    root_type = type(expr).__name__
    refs = extract_feature_refs(expr, ignore_std_lib=True)
    node_types = collect_node_types(expr)
    operators = extract_operators(expr)
    depth = measure_depth(expr)

    # Classify
    classification = classify_attribute_expression(expr, refs, adapter, part_elem)

    return AttributeExprInfo(...)
```

#### 3. Classification Logic (Q5)

```python
def classify_attribute_expression(expr, refs, adapter, part_elem) -> str:
    """Classify an attribute expression pattern.

    LITERAL:       No feature references (pure constants/operators)
    FORMULA:       References only sibling attributes on same part
    EXPOSE:        Single reference to calc usage output (dotted path)
    MIXED:         References both sibling attributes and calc outputs
    UNRESOLVABLE:  References that can't be resolved
    """
    if not refs:
        # Check if it's a literal or an operator expression with only literals
        return "LITERAL"

    # Get sibling attribute names and calc usage names from the part
    sibling_attr_names = set()
    calc_usage_names = set()
    for member in part_elem.owned_members:
        if adapter.is_instance(member, "AttributeUsage"):
            name = sanitize_name(member.name)
            if name:
                sibling_attr_names.add(name)
        elif adapter.is_instance(member, "CalculationUsage"):
            name = sanitize_name(member.name)
            if name:
                calc_usage_names.add(name)

    has_sibling_ref = False
    has_calc_ref = False
    has_unresolvable = False

    for ref in refs:
        ref_name = ref.name
        # Check if it's a sibling attribute reference
        if ref_name in sibling_attr_names:
            has_sibling_ref = True
        # Check if first segment of dotted path is a calc usage
        elif '.' in ref_name or any(ref_name.startswith(cn) for cn in calc_usage_names):
            has_calc_ref = True
        else:
            # Try qualified name resolution
            has_unresolvable = True

    if has_unresolvable:
        return "UNRESOLVABLE"
    if has_sibling_ref and has_calc_ref:
        return "MIXED"
    if has_calc_ref:
        return "EXPOSE"
    if has_sibling_ref:
        return "FORMULA"
    return "LITERAL"
```

Note: The exact reference name format from `extract_feature_refs()` needs to be discovered during the spike. The classification logic may need adjustment based on what the SysIDE API actually returns for attribute expressions. The spike script's purpose is precisely to discover this.

#### 4. Compilation Attempt (Q6)

Try to compile at least one FORMULA-pattern attribute using Phase 1 compiler:

```python
def attempt_compilation(attr_info, expr, sibling_attr_names):
    """Attempt to compile an attribute expression using Phase 1 compiler.

    For FORMULA patterns: input_names = sibling attributes on the same part.
    For EXPOSE patterns: may need different reference resolution.
    """
    from sysml_codegen.extraction.expression_compiler import (
        build_expression_ast,
        compile_expression,
        CompilationError,
    )

    try:
        # For attribute expressions, "inputs" are sibling attributes
        ast_ir = build_expression_ast(
            syside_node=expr,
            input_names=sibling_attr_names,
            output_names=set(),  # no sibling outputs for attributes
        )
        compiled = compile_expression(ast_ir)
        return compiled, None
    except CompilationError as e:
        return None, str(e)
    except Exception as e:
        return None, f"Unexpected: {e}"
```

The key test case is solar_battery's `p_net_kw = p_net_mw * 1000.0`. If `build_expression_ast()` correctly identifies `p_net_mw` as an input reference and `1000.0` as a literal, it should compile to `(inputs.p_net_mw * 1000.0)`. This validates the entire Phase 1 compiler pipeline works for attribute expressions.

For EXPOSE patterns (`p_alpha_out = alpha_neutron_split.p_alpha`), the expression is likely a `FeatureChainExpression` which `build_expression_ast()` currently marks as UNSUPPORTED. The spike should document this and note it as a gap to address in Item 2.

#### 5. Spike Report Generation

The script writes results to stdout (for interactive review) and to `.project/active/attr-expr-spike/report.md` (for persistent record). Report structure:

```
# Spike Report: Attribute Expression AST Discovery
## Q1: AST Availability
  [table: part, attribute, has_expression, root_node_type]
## Q2: Reference Resolution
  [table: attribute, ref_name, resolved_to, ref_type]
## Q3: EXPOSE Pattern Analysis
  [findings on FeatureChainExpression vs. binding]
## Q4: Cross-Part References
  [findings on cross-part dotted paths]
## Q5: Pattern Inventory
  [table: model suite | FORMULA | EXPOSE | LITERAL | UNRESOLVABLE | total]
## Q6: Compiler Reuse
  [compilation attempt results with actual Python output]
## Q7: Architecture Recommendation
  [grounded in Q1-Q6 findings]
## Go/No-Go Decision
```

### Dependencies

**External packages (already installed):**
- `agentic_mbse.sysml.expression` -- `extract_feature_refs()`, `traverse_expression()`, `extract_operators()`
- `agentic_mbse.sysml.syside_adapter` -- `SysideAdapter` (via `SysMLDataExtractor`)

**Internal modules:**
- `sysml_codegen.extraction.extractor` -- `SysMLDataExtractor` for model loading
- `sysml_codegen.extraction.expression_compiler` -- `build_expression_ast()`, `compile_expression()` for Q6
- `sysml_codegen.extraction.expression_utils` -- `reconstruct_expression()`, `extract_feature_reference_name()` for human-readable expression text

### Testing Strategy

This is a spike -- no unit tests are needed. Validation is:
1. Script runs without errors on all 3 model suites
2. Q1-Q7 are answered with concrete data (not N/A or "unknown")
3. At least one attribute expression compiles to valid Python
4. Report is coherent and grounded in observed data

### Error Handling

- Model load failures: log error, skip suite, continue with remaining
- Missing `feature_value_expression`: record as `has_expression=False`, classify as appropriate
- Compilation failures: record error message, still classify the attribute
- Unexpected node types: log them explicitly (FR-9 requirement)

---

## Potential Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| `feature_value_expression` is NOT populated on PartDef attributes | HIGH -- blocks entire ATTR-EXPR epic | This is precisely what the spike validates. If unavailable, report as NO-GO with documented evidence. |
| PartUsage vs PartDefinition confusion -- attributes may be on PartUsages, not PartDefs | MEDIUM | Iterate both `PartDefinition` and `PartUsage` element types. Document which has the attributes. |
| EXPOSE-pattern expressions are `FeatureChainExpression` which the Phase 1 compiler marks UNSUPPORTED | LOW | Expected outcome. Document the AST structure so Item 2 can add support. |
| Reference names from `extract_feature_refs()` don't match sibling attribute names | MEDIUM | Compare qualified_name, name, and all available identifiers. Log discrepancies for manual analysis. |
| Unit annotations `[m]` on attribute expressions create unexpected AST structure | LOW | Phase 1 found units are separate from expressions. The `[` operator in `build_expression_ast()` already strips unit annotations. |

---

## Integration Strategy

This spike is fully standalone:
- No production code changes (`src/` untouched)
- No test modifications (`tests/` untouched)
- Single new file: `scripts/spike_attribute_expressions.py`
- Report output: `.project/active/attr-expr-spike/report.md`

The spike's findings feed directly into:
- **If GO:** Item 2 (spec + design for `ComputedAttributeData` model and extraction logic)
- **If NO-GO:** Epic is rescoped or deferred, documented in the report

---

## Validation Approach

**Success criteria (from spec AC):**
- [ ] Script exists at `scripts/spike_attribute_expressions.py`
- [ ] Runs against solar_battery and CATF fixtures without error
- [ ] Q1: Concrete yes/no on AST availability with examples
- [ ] Q2: Reference resolution demonstrated or documented as infeasible
- [ ] Q3: EXPOSE pattern AST structure documented
- [ ] Q4: Cross-part reference structure documented
- [ ] Q5: Pattern inventory table with counts for all 3 suites
- [ ] Q6: Phase 1 compiler reuse verified or gaps identified
- [ ] Q7: Architecture recommendation with rationale
- [ ] At least one attribute expression compiled to valid Python
- [ ] Go/no-go decision documented
- [ ] Report at `.project/active/attr-expr-spike/report.md`
- [ ] No production code modified

**Manual verification:**
1. Run `uv run python scripts/spike_attribute_expressions.py` and verify output
2. Confirm report.md is well-structured and all 7 questions answered
3. Verify existing tests still pass: `uv run pytest tests/`

---

Next Step: After approval -> `/_my_implement` or `/_my_plan` for execution
