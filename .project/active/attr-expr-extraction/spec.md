# Spec: Computed Attribute Extraction & Data Models

**Status:** Complete
**Owner:** Reid Westwood
**Created:** 2026-02-08T21:01:12+00:00
**Complexity:** MEDIUM
**Branch:** cost-pattern
**Epic:** ATTR-EXPR (Item 2)

---

## Business Goals

### Why This Matters

The ATTR-EXPR epic eliminates the CalcDef+CalcUsage ceremony for simple attribute-level formulas. Item 2 builds the foundational data models and extraction logic that all downstream work (pipeline integration, E2E validation, documentation) depends on. Without `ComputedAttributeData` and correct classification, the pipeline cannot generate synthetic modules for `attribute volume = length * width * height`.

This is the first implementation item after the Item 1 spike (complete, GO). The spike proved that SysIDE populates `feature_value_expression` on all PartDef attributes (35/35), that 14/14 FORMULA patterns compile with the Phase 1 compiler (zero changes), and that chains require no special handling in extraction or compilation.

### Success Criteria

- [ ] Standalone extraction module with data models, classification, and compilation -- fully tested and independent of pipeline integration
- [ ] All 5 classification categories correctly identified using qualified name resolution
- [ ] FORMULA patterns compile to valid Python via the existing Phase 1 expression compiler
- [ ] Zero changes to the Phase 1 expression compiler
- [ ] All existing tests pass (167+ baseline)

### Priority

P1. On the critical path -- Items 3-5 are blocked until this is complete.

---

## Problem Statement

### Current State

- `_extract_attribute()` in `extractor.py` (lines 339-371) captures basic metadata (name, type, default_value) but makes no distinction between computed and literal attributes
- `_extract_default_value()` (lines 373-410) checks `feature_value_expression` but only extracts literal values -- computed expressions return `None`
- `AttributeInfo` stores only `default_value` as string; no AST, no classification, no compiled expression
- `DesignAttributeData` in `parameter_groups.py` tracks `parent_part` and `qualified_name` but has no computed attribute awareness
- The Phase 1 expression compiler (`build_expression_ast()`, `compile_expression()`) works on any SysIDE AST node but is currently only invoked for CalcDef outputs

### Desired Outcome

A new extraction module that:
1. Scans PartDef/PartUsage attributes for `feature_value_expression`
2. Classifies each expression using qualified name resolution (FORMULA, EXPOSE_PURE, EXPOSE_COMPUTED, LITERAL, UNRESOLVABLE)
3. Compiles FORMULA expressions to Python using the existing Phase 1 compiler
4. Stores results in a `ComputedAttributeData` dataclass ready for pipeline integration in Item 3

---

## Scope

### In Scope

- `ComputedAttributeClassification` enum in `extraction/data_models.py`
- `ComputedAttributeData` dataclass in `extraction/data_models.py`
- `extract_computed_attributes()` function in new `extraction/computed_attribute_extractor.py`
- Classification logic using `ref.qualified_name` (not `ref.name`)
- Compilation of FORMULA patterns via Phase 1 `build_expression_ast()` + `compile_expression()`
- Unit tests for all 5 classification categories plus qualified-name collision edge case

### Out of Scope

- Pipeline integration -- Step 4.5, `PipelineContext` changes (Item 3)
- Backtracker changes -- computed attribute resolution (Item 3)
- Graph builder changes -- synthetic `PipelineModule` generation (Item 3)
- EXPOSE_COMPUTED compilation or decomposition (deferred beyond this epic)
- `InvocationExpression` / function call support
- Cross-part attribute references (Phase 3)
- Chain-awareness in extraction -- chains are purely a graph-ordering concern (Item 3)

### Edge Cases & Considerations

- **Qualified name collision**: A sibling attribute named `p_alpha` and a CalcDef output also named `p_alpha` MUST be distinguished via `ref.qualified_name` namespace, not `ref.name`. The v1 spike found 19 CATF misclassifications with simple-name matching.
- **`reconstruct_expression()` loses parenthesization**: `expression_text` field is display-only. All semantic analysis MUST use the raw AST. B3 probe result: text shows `r_inner + r_outer / 2.0 - r_major` but AST correctly preserves `(r_inner + r_outer) / 2.0 - r_major`.
- **FORMULA-as-passthrough**: `attribute b = a` (single ref, no operators) classifies as FORMULA and compiles to `inputs.a`. Functionally correct but wasteful. Do not special-case -- a trivial passthrough module is harmless.
- **FeatureChainExpression refs decompose into segments**: `extract_feature_refs()` returns `['result', 'scale_calc']` as separate refs for `scale_calc.result`, not a single dotted path. Classification must handle this decomposition.
- **EXPOSE refs in FeatureChainExpression**: The first ref's `qualified_name` identifies the CalcDef output (e.g., `AttrExprProbeLibrary::ScaleCalc::result`). The second ref's `qualified_name` identifies the CalcUsage instance (e.g., `AttrExprProbeDesign::probe_design::scale_calc`).

---

## Requirements

### Functional Requirements

> Requirements below are from the epic Item 2 scope and architectural decisions document unless marked [INFERRED] or [FROM INVESTIGATION].

**Data Models**

1. **FR-1**: `ComputedAttributeClassification(str, Enum)` with 5 values:
   - `FORMULA` -- arithmetic on sibling attributes only (generates synthetic module)
   - `EXPOSE_PURE` -- single FeatureChainExpression, no operators (channel alias, no module)
   - `EXPOSE_COMPUTED` -- FeatureChainExpression inside arithmetic (deferred)
   - `LITERAL` -- pure constants, no feature references (not a computed attribute)
   - `UNRESOLVABLE` -- references that can't be resolved (warning, skip)

2. **FR-2**: `ComputedAttributeData` dataclass with fields:
   - `name: str` -- attribute name
   - `python_name: str` -- sanitized Python identifier
   - `owning_part_name: str` -- owning PartDef/PartUsage name
   - `owning_part_qualified_name: str` -- qualified name for resolution (SysML `::` format)
   - `expression_ast: Any` -- raw SysIDE AST node (source of truth for compilation)
   - `expression_text: str` -- human-readable SysML via `reconstruct_expression()` (display only, does NOT preserve parenthesization)
   - `references: list[ExpressionRef]` -- resolved references (each has `.name` and `.qualified_name`, structurally paired)
   - `classification: ComputedAttributeClassification`
   - `compilability: Compilability` -- reuse Phase 1 enum
   - `compiled_expression: str | None` -- Python expression from compiler (None for non-FORMULA)
   - `source_file: Path`
   - `source_line: int`

3. **FR-3**: [INFERRED] Data model follows project convention: `@dataclass` (not Pydantic) for extraction-layer models, consistent with `AttributeInfo`, `CalculationDefinitionData`, `CalcUsageData`, `DesignAttributeData`.

**Extraction Logic**

4. **FR-4**: New file `extraction/computed_attribute_extractor.py` with function:
   ```
   extract_computed_attributes(adapter, part_element, calc_usage_names) -> list[ComputedAttributeData]
   ```
   - Iterates `part_element.owned_members`, filters `AttributeUsage` with `feature_value_expression`
   - Uses `hasattr()` guard before accessing `feature_value_expression` (project convention)

5. **FR-5**: Classification MUST use `ref.qualified_name` (not `ref.name`) to distinguish sibling attribute refs from calc output refs. Classification rules:
   - All refs share owning part's namespace -> FORMULA
   - Any ref has CalcDef output namespace or matches a calc usage name -> EXPOSE_PURE (if no operators) or EXPOSE_COMPUTED (if operators present)
   - No refs (pure constants) -> LITERAL
   - Any ref unresolvable -> UNRESOLVABLE

6. **FR-6**: FORMULA expressions compiled using Phase 1's `build_expression_ast(syside_node, input_names=sibling_attr_names, output_names=set())` + `compile_expression(ast)`. Sibling attribute names (all `AttributeUsage` on the same part, excluding the attribute being classified) serve as `input_names`.

7. **FR-7**: No chain-awareness needed in extraction. `cost = area * rate` where `area` is computed compiles to `(inputs.area * inputs.rate)` -- identical to if `area` were literal. Chain resolution is Item 3's concern.

8. **FR-8**: [INFERRED] Attributes with no `feature_value_expression` or with pure literal expressions (where `_extract_literal_value()` succeeds) are skipped -- they are not computed attributes. Only attributes with non-trivial expressions (OperatorExpression, FeatureReferenceExpression to siblings, FeatureChainExpression) produce `ComputedAttributeData`.

9. **FR-9**: [FROM INVESTIGATION] `extract_feature_refs()` returns refs with decomposed FeatureChainExpression segments. For `scale_calc.result`, two refs are returned: one with `qualified_name` pointing to the CalcDef output, another to the CalcUsage instance. Classification logic must check calc usage names against ref qualified names that match calc usage qualified name patterns on the owning part.

10. **FR-10**: [INFERRED] FORMULA compilation failure (e.g., unsupported AST node) SHOULD downgrade `compilability` to `MANUAL_REQUIRED` and set `compiled_expression = None` rather than raising an exception. Log a warning. The attribute is still classified as FORMULA -- it just can't be auto-implemented.

**Unit Tests**

11. **FR-11**: Unit tests in `tests/unit/test_computed_attribute_extraction.py` covering:
    - Simple FORMULA: `area = length * width` -> compiled `(inputs.length * inputs.width)`, classification FORMULA
    - Complex FORMULA: `p_blanket = m_n * p_f + p_in + eta * (f_p * eta_p + f_sub) * (m_n * p_f)` -> correct nested compilation
    - Chain FORMULA: `cost = area * rate` where `area` is also computed -> compiled `(inputs.area * inputs.rate)`, classification FORMULA (no special handling)
    - EXPOSE_PURE: `p_alpha_out = alpha_split.p_alpha` -> classification EXPOSE_PURE, `compiled_expression = None`
    - EXPOSE_COMPUTED: `scaled_area = scale_calc.result * 2.0` -> classification EXPOSE_COMPUTED, `compiled_expression = None`
    - LITERAL: `length = 10.0` -> classification LITERAL (skipped, not a `ComputedAttributeData`)
    - UNRESOLVABLE: `broken = length * mystery` -> classification UNRESOLVABLE
    - Qualified name collision: verify that a ref named `p_alpha` with CalcDef qualified name is NOT classified as sibling ref even when a sibling named `p_alpha` exists

12. **FR-12**: [INFERRED] Tests follow project convention: mock syside nodes (no full SysIDE loading), monkeypatch `adapter.is_instance()`, lazy imports inside test functions, `pytest` assertions.

### Non-Functional Requirements

- **NFR-1**: `uv run mypy src/` passes on all new code
- **NFR-2**: `uv run pytest tests/` -- all existing 167+ tests unaffected (zero regressions)
- **NFR-3**: Zero changes to Phase 1 expression compiler (`expression_compiler.py`)

---

## Acceptance Criteria

### Core Functionality

- [ ] `ComputedAttributeClassification` enum defined with 5 values (FR-1)
- [ ] `ComputedAttributeData` dataclass defined with all 13 fields (FR-2)
- [ ] `extract_computed_attributes()` correctly classifies FORMULA, EXPOSE_PURE, EXPOSE_COMPUTED, LITERAL, UNRESOLVABLE (FR-4, FR-5)
- [ ] Classification uses `ref.qualified_name` -- test proves simple-name collision is handled (FR-5, FR-11)
- [ ] FORMULA compilation produces valid Python expressions (FR-6)
- [ ] FORMULA compilation failure degrades gracefully (MANUAL_REQUIRED, not exception) (FR-10)
- [ ] `expression_text` populated via `reconstruct_expression()` with display-only semantics (FR-2)
- [ ] No chain-awareness in extraction logic (FR-7)
- [ ] Unit tests pass covering all 8 test patterns (FR-11)

### Quality & Integration

- [ ] `uv run mypy src/` passes (NFR-1)
- [ ] `uv run pytest tests/` -- all existing tests unaffected (NFR-2)
- [ ] Zero changes to `expression_compiler.py` (NFR-3)
- [ ] New code follows project dataclass conventions (FR-3)

---

## Related Artifacts

- **Spike findings (v1):** `.project/active/attr-expr-spike/report.md`
- **Spike findings (v2):** `.project/active/attr-expr-spike/findings_v2.md`
- **Architectural decisions:** `.project/concepts/attr-expr-architectural-decisions.md`
- **Epic:** `.project/backlog/epic_attribute_expression_capture.md` (Item 2)
- **Design:** `.project/active/attr-expr-extraction/design.md` (to be created)
- **Existing extractor:** `src/sysml_codegen/extraction/extractor.py` (lines 339-410)
- **Existing data models:** `src/sysml_codegen/extraction/data_models.py`
- **Expression compiler:** `src/sysml_codegen/extraction/expression_compiler.py`
- **Expression utils:** `src/sysml_codegen/extraction/expression_utils.py`

---

**Next Steps:** After approval, proceed to `/_my_design`
