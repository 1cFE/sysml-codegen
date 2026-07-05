# Spec: Attribute Expression AST Discovery & Architecture Evaluation

**Status:** Complete
**Owner:** Reid Westwood
**Created:** 2026-02-08T17:55:20+00:00
**Complexity:** MEDIUM
**Branch:** cost-pattern
**Epic:** ATTR-EXPR Item 1

---

## Business Goals

### Why This Matters

Phase 1 (EXPR-CODEGEN) eliminated the `_impl.py` authoring bottleneck for CalcDefs, but the full CalcDef+CalcUsage ceremony remains mandatory for every formula. A modeler writing `attribute volume = pi * r^2 * h` on a PartDef must still create a CalcDef in `library.sysml`, a CalcUsage in `design.sysml`, and wire them through the pipeline -- ~100 lines of infrastructure for 1 line of math.

Phase 2 (ATTR-EXPR) aims to eliminate this ceremony by detecting computed attributes and generating pipeline modules automatically. **This spike is the hard gate**: it validates whether SysIDE even provides the expression ASTs on PartDef attributes that the approach requires. If ASTs are unavailable, Phase 2 is rescoped or deferred before investing 5+ days in implementation.

### Success Criteria

- [ ] Concrete data proving or disproving AST availability on PartDef attributes
- [ ] Pattern inventory with per-model counts of FORMULA, EXPOSE, MIXED, LITERAL, UNRESOLVABLE attributes
- [ ] At least one attribute expression compiled to Python using the existing Phase 1 compiler
- [ ] Architecture recommendation (Option A/B/C/D) with rationale grounded in findings
- [ ] Documented go/no-go decision with clear criteria

### Priority

P1 -- gates the entire ATTR-EXPR epic (Items 2-4 depend on this). Sequential dependency: this MUST complete before any Phase 2 implementation begins.

---

## Problem Statement

### Current State

- `extractor._extract_attribute()` (lines 339-371) extracts literal defaults via `_extract_default_value()` but discards any expression AST
- `AttributeInfo` stores only `default_value` as a string -- no `expression_ast` or `feature_value_expression` field
- Phase 1 proved CalcDef output attributes have `feature_value_expression` populated (95.8% coverage, 92/96 outputs), but this has NOT been verified for PartDef attributes
- Real models have attribute-level expressions today:
  - Solar_battery `design.sysml:60`: `attribute p_net_kw : Real = p_net_mw * 1000.0;` (FORMULA pattern)
  - CATF `physics.sysml:114-122`: `attribute p_alpha_out : Real = alpha_neutron_split.p_alpha;` (EXPOSE pattern)
- It is unknown whether these attributes produce expression ASTs in the SysIDE API response, or whether they are stored differently than CalcDef output expressions
- The Phase 1 expression compiler (`build_expression_ast()`, `compile_expression()`) is CalcDef-agnostic but has only been tested on CalcDef output ASTs
- Four candidate architectures exist for integrating computed attributes into the pipeline, with no empirical basis for choosing between them

### Desired Outcome

A research report answering 7 specific questions (listed below) with concrete data from real SysML models, enabling a confident go/no-go decision and architecture choice for the ATTR-EXPR epic.

---

## Scope

### In Scope

**7 Research Questions** (from ATTR-EXPR epic Item 1):

1. **Q1 -- AST Availability**: Do PartDef attributes with expressions have `feature_value_expression` populated in the SysIDE API response? What about literal-only attributes -- do they have an AST or just a value?

2. **Q2 -- Reference Resolution**: For `p_net_kw = p_net_mw * 1000.0`, does the AST contain `FeatureReferenceExpression` nodes pointing to `p_net_mw`? Can references be resolved to sibling attributes on the same PartDef?

3. **Q3 -- EXPOSE Pattern**: For `attribute p_alpha_out = alpha_neutron_split.p_alpha`, does this produce an expression AST? Is it a `FeatureChainExpression` or a binding? Is this pattern already handled by the backtracker's transitive resolution (`dependency_backtracker.py` lines 567-624)?

4. **Q4 -- Cross-Part References**: Can attribute expressions reference attributes on other parts? What AST structure do cross-part references produce? How common is this pattern across existing models?

5. **Q5 -- Pattern Inventory**: Across solar_battery, CATF, and chain_spike models, how many PartDef attributes have expressions? Classify each as FORMULA / EXPOSE / MIXED / LITERAL / UNRESOLVABLE.

6. **Q6 -- Compiler Reuse**: Can Phase 1's `build_expression_ast()` and `compile_expression()` process attribute expression ASTs without modification? What new `ExpressionNodeType` variants, if any, are needed?

7. **Q7 -- Architecture Evaluation**: Given Q1-Q6 findings, which integration approach is best?
   - **Option A**: Synthetic CalcDef+CalcUsage -- inject into extraction pipeline, reuse all existing infrastructure
   - **Option B**: Synthetic CalcUsage only -- reference a generated "computed attribute" CalcDef
   - **Option C**: Direct graph integration -- add `ComputedAttributeData` to `PipelineContext`, extend graph builder
   - **Option D**: Inline in parameter schemas -- `@computed_field` on Pydantic schemas, no separate modules

**Exploration targets**:
- Solar_battery model: `p_net_kw = p_net_mw * 1000.0` (design.sysml:60) -- FORMULA pattern
- CATF model: `p_alpha_out = alpha_neutron_split.p_alpha` and siblings (physics.sysml:114-122) -- EXPOSE pattern
- Chain_spike model: CalcDef output attributes (library.sysml) -- control group (already handled by Phase 1)

**Compilation proof**:
- Attempt to compile at least one PartDef attribute expression using the existing Phase 1 compiler functions (`build_expression_ast()`, `compile_expression()`)
- Document any modifications or workarounds required

### Out of Scope

- Any production code changes (this is a spike -- exploration script only)
- `InvocationExpression` / function call support (document if encountered, but do not implement)
- Hierarchy/multiplicity patterns (Phase 3 scope)
- Cross-part references beyond what naturally appears in existing fixture models
- Benchmarking or performance analysis
- Design of the computed attribute data models (Item 2)

### Edge Cases & Considerations

- **Literal expressions that look like formulas**: `attribute x : Real = 3.14159 * 2.0` -- pure constants with operators. These may have ASTs but produce static values. Should be classified as LITERAL or FORMULA? The spike SHOULD document how these present.
- **Unit annotations**: `attribute thickness : Real = 3.0 [m]` -- does the unit annotation affect the expression AST? Phase 1 found units are separate from expressions, but verify for attributes.
- **Redefinition (`:>>`) attributes**: Some attributes may use `:>>` to redefine inherited features. These are structurally different from `=` expressions. The spike SHOULD note if any appear and how they present in the API.
- **Attributes without types**: `attribute x = expr` vs `attribute x : Real = expr`. The spike SHOULD document whether untyped attributes behave differently.

---

## Requirements

### Functional Requirements

> All requirements below are from the ATTR-EXPR epic Item 1 definition.

1. **FR-1**: The spike MUST produce an exploration script (`scripts/spike_attribute_expressions.py`) that inspects SysIDE API responses for PartDef attributes.

2. **FR-2**: The script MUST test against at least two model suites: solar_battery (FORMULA pattern) and CATF (EXPOSE pattern).

3. **FR-3**: The script MUST attempt to compile at least one attribute expression using Phase 1's `build_expression_ast()` and `compile_expression()`.

4. **FR-4**: The report MUST answer all 7 research questions (Q1-Q7) with concrete data from real models, not theoretical analysis.

5. **FR-5**: The report MUST include a pattern inventory table with per-model counts of attribute classification (FORMULA / EXPOSE / MIXED / LITERAL / UNRESOLVABLE).

6. **FR-6**: The report MUST include an architecture recommendation (Option A/B/C/D) with rationale grounded in the empirical findings.

7. **FR-7**: The report MUST include a go/no-go decision with clear criteria. Go criteria: attribute ASTs are available on >=1 real model with expression coverage sufficient to justify implementation.

8. **FR-8**: [INFERRED] The spike SHOULD inventory what SysIDE API fields are available on PartDef attribute elements (analogous to Phase 1's `feature_value_expression` discovery for CalcDef outputs).

9. **FR-9**: [INFERRED] The spike SHOULD document any `InvocationExpression` or other unsupported node types encountered on attribute expressions, even though implementing support is out of scope.

---

## Acceptance Criteria

### Core Functionality

- [ ] `scripts/spike_attribute_expressions.py` exists and runs against solar_battery and CATF fixtures
- [ ] Script inspects SysIDE API response for PartDef attribute elements, reporting which fields are available (especially `feature_value_expression` or equivalent)
- [ ] Q1 answered: concrete yes/no on AST availability for PartDef attributes, with examples
- [ ] Q2 answered: reference resolution demonstrated or documented as infeasible
- [ ] Q3 answered: EXPOSE pattern AST structure documented, backtracker overlap assessed
- [ ] Q4 answered: cross-part reference structure documented (even if none found in models)
- [ ] Q5 answered: pattern inventory table with counts for all 3 model suites
- [ ] Q6 answered: Phase 1 compiler reuse verified or gaps identified
- [ ] Q7 answered: architecture recommendation with rationale
- [ ] At least one attribute expression compiled to valid Python using existing compiler
- [ ] Go/no-go decision documented

### Quality & Integration

- [ ] Report written to `.project/active/attr-expr-spike/report.md`
- [ ] No production code modified (spike script only)
- [ ] Existing tests unaffected (spike does not modify `src/` or `tests/`)

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_attribute_expression_capture.md` (ATTR-EXPR)
- **Phase 1 Epic:** `.project/backlog/epic_expression_aware_codegen.md` (EXPR-CODEGEN -- complete)
- **Research:** `.project/research/20260202-180000_expression-compilation-and-inline-math-strategy.md` (Phase 2 roadmap, Approach F Use Case 2)
- **Phase 1 Spike Reports:**
  - `.project/active/expr-spike-ast/report.md` (AST extraction findings -- analogous to this spike)
  - `.project/active/expr-spike-compile/report.md` (compilation proof findings)
- **Design:** `.project/active/attr-expr-spike/design.md` (not applicable -- research item, no design phase)

---

**Next Steps:** Execute the spike. On GO, proceed to ATTR-EXPR Item 2 with `/_my_spec` for Computed Attribute Extraction & Data Models.
