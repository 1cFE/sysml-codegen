# Design: Computed Attribute Extraction & Data Models

**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-02-08
**Branch:** cost-pattern
**Epic:** ATTR-EXPR (Item 2)

---

## Overview

Add data models and extraction logic to classify PartDef/PartUsage attribute expressions (FORMULA, EXPOSE_PURE, EXPOSE_COMPUTED, LITERAL, UNRESOLVABLE) and compile FORMULA patterns to Python using the existing Phase 1 expression compiler. Two files modified, one file created.

## Related Artifacts

- **Spec:** `.project/active/attr-expr-extraction/spec.md`
- **Spike findings (v2):** `.project/active/attr-expr-spike/findings_v2.md`
- **Architectural decisions:** `.project/concepts/attr-expr-architectural-decisions.md`
- **Epic:** `.project/backlog/epic_attribute_expression_capture.md` (Item 2)
- **Existing data models:** `src/sysml_codegen/extraction/data_models.py`
- **Expression compiler:** `src/sysml_codegen/extraction/expression_compiler.py`
- **Expression utils:** `src/sysml_codegen/extraction/expression_utils.py`
- **Spike classification logic:** `scripts/spike_attribute_expressions.py:218-276`

---

## Research Findings

### Existing Patterns & Utilities to Reuse

1. **`extract_feature_refs(expr, ignore_std_lib=True)`** (`agentic_mbse.sysml.expression`):
   Returns `list[ExpressionRef]` where each `ExpressionRef` has `.name` (simple) and `.qualified_name` (full `::` path).

   **Critical: FeatureChainExpression produces TWO refs, not one.** For `scale_calc.result`, the traversal (`traverse_expression` at `expression.py:24-86`) fires the visitor on the FeatureChainExpression node AND recurses into its `operands` (via the `elif hasattr(expr, "operands")` fallback at line 75). This produces:
   - Ref 1: `name="result"`, `qualified_name="AttrExprProbeLibrary::ScaleCalc::result"` (from FeatureChainExpression's `target_feature`)
   - Ref 2: `name="scale_calc"`, `qualified_name="AttrExprProbeDesign::probe_design::scale_calc"` (from the child FeatureReferenceExpression in `operands`)

   **Confirmed empirically** by spike v2 findings (`findings_v2.md:102,114`): *"`extract_feature_refs()` returns two refs: `result` (qname: `AttrExprProbeLibrary::ScaleCalc::result`) and `scale_calc` (qname: `AttrExprProbeDesign::probe_design::scale_calc`)"*.

   **Design consequence:** Ref 2's QN starts with the owning part's QN (`AttrExprProbeDesign::probe_design::`), so naive `startswith()` would misclassify it as a sibling ref. The classification logic must use positive identification (calc_usage_names check) rather than negative inference ("not a sibling → calc ref"). See Classification Rules below.

2. **`build_expression_ast(syside_node, input_names, output_names, all_member_names)`** (`expression_compiler.py:284-399`):
   Converts raw syside AST to IR. For attribute expressions, we pass `input_names=sibling_attr_names`, `output_names=set()`, `all_member_names=None`. The key behavior: `FeatureReferenceExpression` nodes matching `input_names` become `INPUT_REF` (compiled to `inputs.{name}`). Unknown names become `UNSUPPORTED`. `FeatureChainExpression` nodes always become `UNSUPPORTED` -- which is correct for EXPOSE patterns (we don't compile them).

3. **`compile_expression(ast)`** (`expression_compiler.py:181-219`):
   Pure recursive descent. Raises `CompilationError` on UNSUPPORTED nodes. We catch this for graceful degradation.

4. **`reconstruct_expression(expr_node)`** (`expression_utils.py:34-68`):
   Converts AST to human-readable SysML text. Loses parenthesization but useful for display.

5. **`SysideAdapter.is_instance(node, type_name)`** (static method):
   The project's duck-typing adapter for syside AST nodes. Used throughout extraction. Tests monkeypatch this to work with mock classes.

6. **Spike classification logic** (`spike_attribute_expressions.py:218-276`):
   Uses simple `ref.name` matching against sibling attribute names and calc usage names. This is the prototype that Item 2 must upgrade to qualified name resolution. The spike logic iterates `part_elem.owned_members` to build sibling sets -- same pattern we'll use.

7. **`ExpressionRef` type** (`agentic_mbse.sysml.types:97-122`):
   Pydantic BaseModel with fields: `name: str`, `qualified_name: str = ""`, `document_path: str | None = None`, `element: Any | None`.

### Source Location Pattern

CalcDef extraction uses `adapter.get_source_location(elem)` → `(file_path, line)` at `extractor.py:242-248`. For attribute elements, the extractor currently hardcodes `source_line=0`. The adapter method should work on attribute elements too since it's generic.

### Naming Conventions

- SysML qualified names use `::` separator: `Package::PartDef::attribute`
- Internal codegen identifiers use `__` separator (ADR-003)
- `_sanitize_name()` strips quotes, replaces spaces with underscores (`expression_compiler.py:166-178`)

### Test Mock Pattern

Tests in `test_expression_compiler.py:506-561` define:
- `MockOperatorExpression(operator, operands)`
- `MockFeatureReferenceExpression(name)` -- sets `self.referent = SimpleNamespace(name=name)`
- `MockLiteralRational(value)`
- `MockFeatureChainExpression` (empty)
- `mock_syside_adapter` fixture monkeypatches `SysideAdapter.is_instance`

The computed attribute tests will need additional mocks: `MockAttributeUsage` (with `name`, `feature_value_expression`, `qualified_name`) and `MockCalculationUsage` (with `name`, `qualified_name`).

---

## Proposed Design

### Component 1: Data Models (`extraction/data_models.py`)

**Changes:** Add `ComputedAttributeClassification` enum and `ComputedAttributeData` dataclass to the existing file.

#### ComputedAttributeClassification

```python
class ComputedAttributeClassification(str, Enum):
    FORMULA = "formula"
    EXPOSE_PURE = "expose_pure"
    EXPOSE_COMPUTED = "expose_computed"
    LITERAL = "literal"
    UNRESOLVABLE = "unresolvable"
```

Follows the `(str, Enum)` pattern used by `Compilability`, `EntryPointType`, `BindingResolutionType` throughout the codebase.

#### ComputedAttributeData

```python
@dataclass
class ComputedAttributeData:
    name: str                                          # Attribute name (e.g., "area")
    python_name: str                                   # Sanitized Python identifier
    owning_part_name: str                              # PartDef/PartUsage name
    owning_part_qualified_name: str                    # SysML :: format
    expression_ast: Any                                # Raw syside AST node
    expression_text: str                               # Display-only (from reconstruct_expression)
    references: list[ExpressionRef]                    # Refs from extract_feature_refs (structurally paired name+qn)
    classification: ComputedAttributeClassification
    compilability: Compilability                        # Reuse from expression_compiler
    compiled_expression: str | None = None             # Python expr (FORMULA only)
    source_file: Path = field(default_factory=lambda: Path("unknown"))
    source_line: int = 0
```

Follows the `@dataclass` pattern used by all extraction-layer models (`AttributeInfo`, `CalcUsageData`, `DesignAttributeData`). Source tracking follows the `source_file: Path` / `source_line: int` pattern from `PartDefinitionData` and `CalculationDefinitionData`.

**Update `__all__`** to export both new types.

### Component 2: Extraction Module (`extraction/computed_attribute_extractor.py`)

New file with a single public function and internal helpers.

#### Public Function

```python
def extract_computed_attributes(
    adapter: SysideAdapter,
    part_element: Any,
    calc_usage_names: set[str],
) -> list[ComputedAttributeData]:
```

**Parameters:**
- `adapter`: SysIDE adapter for type checking
- `part_element`: Raw syside PartDef/PartUsage element with `.owned_members`, `.name`, `.qualified_name`
- `calc_usage_names`: Set of CalcUsage instance names on this part (e.g., `{"scale_calc", "split"}`). Passed by the caller rather than re-derived, so Item 3's pipeline orchestrator can supply this from already-extracted data.

**Returns:** List of `ComputedAttributeData` for all non-LITERAL attributes. LITERAL attributes are skipped (they stay in the design_attributes path). UNRESOLVABLE attributes are included (with a logged warning) so the caller can report them.

**Algorithm:**

```
1. Build context:
   - sibling_attr_names: set[str] from part_element.owned_members (AttributeUsage)
   - part_name = sanitize_name(part_element.name)
   - part_qn = str(getattr(part_element, 'qualified_name', '') or part_name)

2. For each owned_member that is AttributeUsage (via adapter.is_instance):
   a. Guard: if not hasattr(member, 'feature_value_expression') or
      member.feature_value_expression is None → skip
   b. Extract refs via extract_feature_refs(expr, ignore_std_lib=True)
   c. Classify via _classify_attribute_expression(
        refs, part_qn, calc_usage_names, sibling_attr_names, expr)
   d. Skip if LITERAL
   e. If FORMULA: compile via build_expression_ast + compile_expression
      (with self-exclusion from input_names)
   f. Build ComputedAttributeData and append

3. Return list
```

#### Internal: Classification Function

**Classification Rules (using qualified names with positive identification):**

The key improvement over the spike logic is using `ref.qualified_name` for sibling identification and `calc_usage_names` for positive calc ref identification. We do NOT use "not a sibling → must be calc ref" because that's too broad (would misclassify refs from unrelated namespaces) and because FeatureChainExpression produces a CalcUsage-instance ref whose QN starts with the owning part's QN (see Research Finding #1).

```python
def _classify_attribute_expression(
    refs: list[ExpressionRef],
    owning_part_qualified_name: str,
    calc_usage_names: set[str],
    sibling_attr_names: set[str],
    expression_ast: Any,
) -> ComputedAttributeClassification:
```

```
1. If no refs → LITERAL

2. For each ref, classify by POSITIVE IDENTIFICATION:
   a. If ref.name in calc_usage_names → skip (CalcUsage instance ref from
      FeatureChainExpression traversal; this is a traversal artifact, not a
      semantically meaningful reference for classification)
   b. If ref.qualified_name is non-empty AND starts with
      owning_part_qualified_name + "::" → sibling_ref
   c. If ref.qualified_name is non-empty AND does NOT start with
      owning_part_qualified_name + "::" → calc_ref (CalcDef output
      from a different namespace -- this is the target_feature ref from
      a FeatureChainExpression)
   d. If ref.qualified_name is empty → fall back to simple name:
      - ref.name in sibling_attr_names → sibling_ref
      - ref.name in calc_usage_names → skip (already handled by 2a)
      - otherwise → unresolvable_ref

3. After processing all refs, decide:
   - Any unresolvable_ref → UNRESOLVABLE
   - Only sibling_refs (no calc_refs) → FORMULA
   - Any calc_ref present (with or without sibling_refs):
     - No sibling_refs AND expression root is FeatureChainExpression → EXPOSE_PURE
     - Otherwise → EXPOSE_COMPUTED
```

**Why step 2a (filter CalcUsage instance refs) is essential:**

For `scale_calc.result`, `extract_feature_refs()` returns TWO refs:
- `name="result"`, `qn="Library::ScaleCalc::result"` → classified as calc_ref (step 2c)
- `name="scale_calc"`, `qn="Design::probe_design::scale_calc"` → QN starts with owning part QN!

Without step 2a, the second ref would be classified as sibling_ref (step 2b), causing the expression to be classified as EXPOSE_COMPUTED (mixed sibling + calc refs) instead of EXPOSE_PURE. Step 2a filters it out because `"scale_calc" in calc_usage_names`.

**Worked examples:**

*FORMULA: `attribute area = length * width` on `probe_design` (QN: `AttrExprProbeDesign::probe_design`):*
- Ref: `name="length"`, `qn="AttrExprProbeDesign::probe_design::length"` → 2b: starts with part QN → sibling_ref
- Ref: `name="width"`, `qn="AttrExprProbeDesign::probe_design::width"` → 2b: starts with part QN → sibling_ref
- Decision: only sibling_refs → **FORMULA**

*EXPOSE_PURE: `attribute p_alpha_out = alpha_neutron_split.p_alpha` on `FusionPlasmaPhysics` (QN: `CATFDesign::FusionPlasmaPhysics`):*
- Ref: `name="p_alpha"`, `qn="CATFLibrary::AlphaNeutronSplitCalc::p_alpha"` → 2c: doesn't start with part QN → calc_ref
- Ref: `name="alpha_neutron_split"`, `qn="CATFDesign::FusionPlasmaPhysics::alpha_neutron_split"` → 2a: name in calc_usage_names → skip
- Decision: only calc_refs, root is FeatureChainExpression → **EXPOSE_PURE**

*EXPOSE_COMPUTED: `attribute scaled_area = scale_calc.result * 2.0` on `probe_design`:*
- Ref: `name="result"`, `qn="Library::ScaleCalc::result"` → 2c: calc_ref
- Ref: `name="scale_calc"`, `qn="Design::probe_design::scale_calc"` → 2a: in calc_usage_names → skip
- Decision: calc_ref present, root is OperatorExpression (not FeatureChainExpression) → **EXPOSE_COMPUTED**

*Qualified name collision (CATF bug): `attribute p_alpha_out = alpha_neutron_split.p_alpha` where sibling `p_alpha` also exists:*
- Ref: `name="p_alpha"`, `qn="CATFLibrary::AlphaNeutronSplitCalc::p_alpha"` → 2c: QN doesn't start with part QN → calc_ref (NOT sibling, despite name collision)
- → Correctly classified as EXPOSE, not FORMULA

**Edge case -- empty qualified_name:** If `ref.qualified_name` is empty (possible in some syside edge cases), fall back to `ref.name in sibling_attr_names` matching (step 2d). This preserves the spike's behavior as a safety net.

#### Internal: EXPOSE_PURE vs EXPOSE_COMPUTED Distinction

The distinction is made inside `_classify_attribute_expression` using the `expression_ast` parameter. When calc_refs are present:

- If `SysideAdapter.is_instance(expression_ast, "FeatureChainExpression")` → root is a pure chain, no operators → **EXPOSE_PURE**
- If `SysideAdapter.is_instance(expression_ast, "OperatorExpression")` → operators wrap the chain → **EXPOSE_COMPUTED**
- Otherwise → **EXPOSE_COMPUTED** (conservative default)

This is a simple type check on the root node, not a tree traversal. The spike confirmed that pure EXPOSE (D3: `scale_calc.result`) has root type `FeatureChainExpression`, while EXPOSE+operator (D2: `scale_calc.result * 2.0`) has root type `OperatorExpression`.

#### Compilation Flow (FORMULA only)

```python
# Exclude self from input_names, matching the spike's pattern
# (spike_attribute_expressions.py:610: `if name and name != attr_info.attr_name`).
# In normal models, self-reference in an expression would be an error,
# but excluding self ensures the compiler flags it as UNSUPPORTED
# (unresolved reference) rather than masking it as an INPUT_REF.
input_names = sibling_attr_names - {attr_name}

try:
    ast_ir = build_expression_ast(
        syside_node=expr,
        input_names=input_names,
        output_names=set(),      # no outputs for attribute expressions
        all_member_names=None,   # None is correct: attribute expressions have
                                 # no intermediates (unlike CalcDefs which may
                                 # have undeclared internal members)
    )
    compiled = compile_expression(ast_ir)
    compilability = Compilability.FULLY_COMPILABLE
except CompilationError:
    compiled = None
    compilability = Compilability.MANUAL_REQUIRED
```

This matches the spike's `attempt_compilation()` pattern (`spike_attribute_expressions.py:593-624`) including self-exclusion, with the addition of graceful degradation per FR-10.

#### Logging

- `logger = logging.getLogger(__name__)`
- `logger.debug(...)` for each classified attribute (name, classification, compiled_expression)
- `logger.warning(...)` for UNRESOLVABLE attributes (with ref names that couldn't be resolved)
- `logger.warning(...)` for FORMULA compilation failures (with the CompilationError message)

### Component 3: Unit Tests (`tests/unit/test_computed_attribute_extraction.py`)

#### Mock Infrastructure

Extend the existing mock pattern from `test_expression_compiler.py`:

```python
class MockAttributeUsage:
    """Mock syside AttributeUsage element."""
    def __init__(self, name: str, expr=None, qualified_name: str = ""):
        self.name = name
        self.feature_value_expression = expr
        self.qualified_name = qualified_name or f"TestPkg::TestPart::{name}"

class MockCalculationUsage:
    """Mock syside CalculationUsage element."""
    def __init__(self, name: str, qualified_name: str = ""):
        self.name = name
        self.qualified_name = qualified_name or f"TestPkg::TestPart::{name}"

class MockPartElement:
    """Mock syside PartDef/PartUsage element."""
    def __init__(self, name: str, owned_members: list, qualified_name: str = ""):
        self.name = name
        self.owned_members = owned_members
        self.qualified_name = qualified_name or f"TestPkg::{name}"
```

Reuse `MockOperatorExpression`, `MockFeatureReferenceExpression`, `MockLiteralRational`, `MockFeatureChainExpression` from the existing test file (duplicate them locally for now). If a third test file needs these same mocks, consolidate into `tests/conftest.py` or `tests/helpers.py`.

The `mock_syside_adapter` fixture's `TYPE_MAP` must be extended to include the new mock types:

```python
TYPE_MAP = {
    "MockOperatorExpression": "OperatorExpression",
    "MockFeatureReferenceExpression": "FeatureReferenceExpression",
    "MockLiteralRational": "LiteralRational",
    "MockFeatureChainExpression": "FeatureChainExpression",
    "MockAttributeUsage": "AttributeUsage",
    "MockCalculationUsage": "CalculationUsage",
}
```

This ensures `adapter.is_instance(member, "AttributeUsage")` works correctly when iterating mock part elements.

#### Mock for `extract_feature_refs`

The tests need to mock `extract_feature_refs` to return `ExpressionRef` objects with controlled `name` and `qualified_name` values. This is critical for testing qualified name resolution. Monkeypatch at the import site in the new module:

```python
monkeypatch.setattr(
    "sysml_codegen.extraction.computed_attribute_extractor.extract_feature_refs",
    mock_extract_feature_refs,
)
```

#### Test Cases (8 total, per FR-11)

**Test class: `TestClassifyAttributeExpression`**

1. **`test_formula_simple_binary`**: `area = length * width`
   - Mock: OperatorExpression(`*`, [FeatureRef("length"), FeatureRef("width")])
   - Refs: `[ExpressionRef(name="length", qn="Pkg::Part::length"), ExpressionRef(name="width", qn="Pkg::Part::width")]`
   - Assert: classification=FORMULA, compiled=`"(inputs.length * inputs.width)"`, compilability=FULLY_COMPILABLE

2. **`test_formula_complex_nested`**: `p_blanket = m_n * p_f + p_in + eta * (f_p * eta_p + f_sub) * (m_n * p_f)`
   - Build nested MockOperatorExpression tree
   - Assert: classification=FORMULA, compiled expression matches expected nested output

3. **`test_formula_chain_no_special_handling`**: `cost = area * rate` where `area` is also computed
   - Refs include `ExpressionRef(name="area", qn="Pkg::Part::area")` -- a sibling, regardless of being computed
   - Assert: classification=FORMULA, compiled=`"(inputs.area * inputs.rate)"` -- no chain awareness

4. **`test_expose_pure`**: `p_alpha_out = alpha_split.p_alpha`
   - Expression: MockFeatureChainExpression (root is FeatureChainExpression, not OperatorExpression)
   - Refs (two, matching real behavior): `[ExpressionRef(name="p_alpha", qn="Library::AlphaSplitCalc::p_alpha"), ExpressionRef(name="alpha_split", qn="Pkg::Part::alpha_split")]`
   - calc_usage_names includes `"alpha_split"` → second ref is filtered by step 2a
   - Assert: classification=EXPOSE_PURE, compiled_expression=None

5. **`test_expose_computed`**: `scaled_area = scale_calc.result * 2.0`
   - Expression: MockOperatorExpression wrapping FeatureChainExpression + MockLiteralRational
   - Refs (two): `[ExpressionRef(name="result", qn="Library::ScaleCalc::result"), ExpressionRef(name="scale_calc", qn="Pkg::Part::scale_calc")]`
   - calc_usage_names includes `"scale_calc"` → second ref is filtered; first ref is calc_ref
   - Root is OperatorExpression → EXPOSE_COMPUTED (not EXPOSE_PURE)
   - Assert: classification=EXPOSE_COMPUTED, compiled_expression=None

6. **`test_literal_skipped`**: `length = 10.0`
   - Expression: MockLiteralRational(10.0) -- no refs
   - Assert: not included in output (LITERAL is skipped)

7. **`test_unresolvable`**: `broken = length * mystery`
   - Refs: one sibling ("length"), one with unresolvable qualified_name
   - Assert: classification=UNRESOLVABLE

8. **`test_qualified_name_collision`**: Attribute `p_alpha` exists as sibling AND a CalcDef output is named `p_alpha`
   - Ref `name="p_alpha"` with `qualified_name="Library::CalcDef::p_alpha"` (CalcDef namespace, NOT owning part namespace)
   - Assert: classified as calc_ref, NOT sibling_ref
   - This is the regression test for the 19-CATF-misclassification bug

**Test class: `TestExtractComputedAttributes`**

Integration test of the full `extract_computed_attributes()` function with mock part element containing multiple attributes. Verifies:
- FORMULA attributes are compiled
- LITERAL attributes are excluded
- EXPOSE attributes are classified but not compiled
- Result list contains correct count and ordering

**Test class: `TestComputedAttributeClassification`**

Simple enum value tests (following `TestCompilability` pattern):
- All 5 values exist
- String inheritance

**Test class: `TestComputedAttributeData`**

Dataclass construction test:
- All fields populated correctly
- Default values work (`compiled_expression=None`, `source_line=0`)

---

## Potential Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| FeatureChainExpression ref count varies in future syside versions | Low | Medium | Two-ref behavior empirically confirmed by spike v2. Classification uses positive calc_usage_names check (step 2a) which is robust regardless of ref count. Unit tests mock exact observed behavior. |
| Qualified name format varies across models (different `::` conventions) | Low | Medium | Use `startswith(owning_part_qn + "::")` which handles any depth. Fall back to simple name matching if QN is empty. |
| Compilation failure on unexpected FORMULA AST patterns | Low | Low | Graceful degradation: catch CompilationError, set MANUAL_REQUIRED. Spike proved 14/14 patterns compile. |
| Monkeypatching `extract_feature_refs` in tests doesn't cover real behavior | Medium | Low | Unit tests validate classification logic in isolation. Item 4 E2E tests validate with real models. |
| Self-referential expression in a model (e.g., `attribute x = x + 1`) | Very Low | Low | Self-exclusion from input_names means the compiler flags `x` as unresolved → UNSUPPORTED → CompilationError caught → MANUAL_REQUIRED. Safe degradation. |

---

## Integration Strategy

This module is deliberately standalone with **zero impact on existing code paths**:

- `data_models.py` gets two new types appended; no existing types are modified
- `computed_attribute_extractor.py` is a new file with no imports from analysis/, resolution/, or generation/
- No modifications to `expression_compiler.py` (NFR-3)
- No modifications to `extractor.py`

Item 3 will wire this into the pipeline by calling `extract_computed_attributes()` at Step 4.5 in `initialization.py` and passing results to the backtracker and graph builder.

---

## Validation Approach

### Automated Testing

- **Unit tests**: 8 classification test cases + data model tests + integration test (Component 3 above)
- **Existing regression**: `uv run pytest tests/` must pass with all 167+ tests unchanged
- **Type checking**: `uv run mypy src/` must pass on all new code

### Manual Verification

After implementation, verify with:
```bash
uv run pytest tests/unit/test_computed_attribute_extraction.py -v
uv run pytest tests/ --tb=short  # full regression
uv run mypy src/
```

---

## Files Changed Summary

| File | Action | Changes |
|------|--------|---------|
| `src/sysml_codegen/extraction/data_models.py` | Modify | Add `ComputedAttributeClassification` enum, `ComputedAttributeData` dataclass, update `__all__` |
| `src/sysml_codegen/extraction/computed_attribute_extractor.py` | Create | `extract_computed_attributes()`, `_classify_attribute_expression()` |
| `tests/unit/test_computed_attribute_extraction.py` | Create | 4 test classes, 8+ test methods, mock infrastructure |

---

**Next Step:** After approval → `/_my_plan` or `/_my_implement`
