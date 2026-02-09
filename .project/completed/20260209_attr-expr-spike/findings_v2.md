# Findings v2: Synthetic Attribute Expression Probe

**Date:** 2026-02-08
**Branch:** cost-pattern
**Epic:** ATTR-EXPR (Item 1 continued)
**Predecessor:** `.project/active/attr-expr-spike/report.md` (v1 findings from 3 real model suites)

---

## Purpose

The v1 spike (report.md) validated AST availability across real models but found only **1 FORMULA-pattern attribute** (`p_net_kw = p_net_mw * 1000.0`) out of 540 total attributes. This is because modelers deliberately avoided inline expressions since codegen couldn't handle them.

This v2 probe creates a purpose-built SysML fixture (`tests/fixtures/attr_expr_probe/`) containing 19 computed attributes + 2 CalcUsages across 4 pattern categories, then runs the existing spike against it. The goal: determine whether SysIDE produces correct ASTs for the **diverse FORMULA patterns** that future models will contain once the ATTR-EXPR epic enables them.

---

## Probe Fixture Design

**Files created:**
- `tests/fixtures/attr_expr_probe/library.sysml` -- 2 CalcDefs (ScaleCalc, SplitCalc)
- `tests/fixtures/attr_expr_probe/design.sysml` -- 1 PartUsage with 35 attributes (17 literal inputs, 14 FORMULA computed attrs, 4 EXPOSE attrs)

**Pattern categories tested:**
- **A (Simple binary):** `+`, `-`, `*`, `/` with 2 operands (4 attrs)
- **B (Complex):** 3-term product, multi-term sum, parenthesized sub-expressions, constant fractions, deep nesting with 7 refs (7 attrs)
- **C (Chains):** computed attr referencing other computed attrs, multi-hop, fan-in (3 attrs)
- **D (Mixed):** computed attr feeding CalcUsage input, CalcUsage output in expression, pure EXPOSE, multi-output EXPOSE (2 CalcUsages + 4 attrs)

---

## Results

### Overall Numbers

| Classification | Count | Compiled | Failed |
|---------------|-------|----------|--------|
| LITERAL | 17 | 17 | 0 |
| FORMULA | 14 | 14 | 0 |
| EXPOSE | 4 | 0 | 2 (sampled) |
| MIXED | 0 | -- | -- |
| UNRESOLVABLE | 0 | -- | -- |
| **Total** | **35** | **31** | **2** |

**100% of FORMULA patterns compiled successfully.** Zero unexpected node types.

### Pattern A: Simple Binary Operations -- All Pass

| ID | SysML | Compiled Python | Correct? |
|----|-------|----------------|----------|
| A1 | `length * width` | `(inputs.length * inputs.width)` | Yes |
| A2 | `p_fusion / p_input` | `(inputs.p_fusion / inputs.p_input)` | Yes |
| A3 | `length + width` | `(inputs.length + inputs.width)` | Yes |
| A4 | `length - 1.0` | `(inputs.length - 1.0)` | Yes |

All 4 arithmetic operators work. Mixed ref+literal operands (A4) work.

### Pattern B: Complex Expressions -- All Pass

| ID | SysML | Compiled Python | Notes |
|----|-------|----------------|-------|
| B1 | `length * width * height` | `((inputs.length * inputs.width) * inputs.height)` | Left-fold correct |
| B2 | `2.0 * length + 2.0 * width` | `((2.0 * inputs.length) + (2.0 * inputs.width))` | Precedence correct: `*` before `+` |
| B3 | `(r_inner + r_outer) / 2.0 - r_major` | `(((inputs.r_inner + inputs.r_outer) / 2.0) - inputs.r_major)` | Parenthesized grouping preserved |
| B4 | `eta_thermal * p_fusion + eta_direct * p_input` | `((inputs.eta_thermal * inputs.p_fusion) + (inputs.eta_direct * inputs.p_input))` | 4 refs, mixed ops |
| B5a | `p_fusion * 3.52 / 17.58` | `((inputs.p_fusion * 3.52) / 17.58)` | Constant fraction |
| B5b | `p_fusion * 14.06 / 17.58` | `((inputs.p_fusion * 14.06) / 17.58)` | Same pattern |
| B6 | `(m_n * p_f) + p_in + eta * (f_p * eta_p + f_sub) * (m_n * p_f)` | `(((inputs.m_neutron * inputs.p_fusion) + inputs.p_input) + ((inputs.eta_thermal * ((inputs.f_pump * inputs.eta_pump) + inputs.f_subsystem)) * (inputs.m_neutron * inputs.p_fusion)))` | 7 refs, deeply nested, correct |

**Key finding: The AST preserves parenthesized grouping even though `reconstruct_expression()` loses it.** The `sysml_text` for B3 displays as `r_inner + r_outer / 2.0 - r_major` (no parens), but the compiled output correctly shows `(((inputs.r_inner + inputs.r_outer) / 2.0) - inputs.r_major)`. **The AST is the source of truth, not the text reconstruction.** Item 2 should rely on AST compilation, never on text reconstruction, for correctness.

### Pattern C: Chains -- All Pass (Critical Result)

| ID | SysML | Compiled Python | Dependency |
|----|-------|----------------|-----------|
| C1 | `area * rate` | `(inputs.area * inputs.rate)` | `area` is computed (A1) |
| C2 | `cost * markup` | `(inputs.cost * inputs.markup)` | `cost` is computed (C1), 2-hop chain |
| C3 | `cost / volume` | `(inputs.cost / inputs.volume)` | Fan-in: `cost` (C1) + `volume` (B1) |

**The compiler treats computed attributes identically to literal attributes.** It emits `inputs.area` without knowing or caring that `area = length * width`. Chain resolution is entirely a graph-builder concern (topological ordering), not a compiler concern. This is the single most important finding for Items 2 and 3.

### Pattern D: Mixed/EXPOSE -- Expected Failures

| ID | SysML | Root Node | Classification | Compilation |
|----|-------|-----------|---------------|-------------|
| D1 | `calc { in value = area; }` | N/A (CalcUsage) | N/A | N/A -- SysIDE accepted computed attr in binding |
| D2 | `scale_calc.result * 2.0` | OperatorExpression | EXPOSE | `CompilationError: unsupported operator: .` |
| D3 | `scale_calc.result` | FeatureChainExpression | EXPOSE | `CompilationError: unsupported operator: .` |
| D4a | `split.half` | FeatureChainExpression | EXPOSE | (not sampled) |
| D4b | `split.quarter` | FeatureChainExpression | EXPOSE | (not sampled) |

**D1 is notable:** SysIDE accepts a computed attribute (`area`) as a CalcUsage binding input. This confirms that computed attributes and CalcUsages can coexist on the same PartUsage without syntax issues.

---

## Deviations from Predictions

### 1. D2 classified as EXPOSE, not MIXED (prediction was MIXED)

The plan predicted `scaled_area = scale_calc.result * 2.0` would classify as MIXED (refs to both calc output and literal). Instead it classified as EXPOSE.

**Root cause:** `extract_feature_refs()` returns two refs: `result` (qname: `AttrExprProbeLibrary::ScaleCalc::result`) and `scale_calc` (qname: `AttrExprProbeDesign::probe_design::scale_calc`). The classifier sees `scale_calc` matching a calc usage name, and `result` not matching any sibling attribute name. The `2.0` literal produces no ref. Since no ref matches a sibling attribute, `has_sibling_ref` stays False, and the classifier returns EXPOSE.

**Impact on Item 2:** The MIXED classification as currently defined requires refs to **both sibling attributes AND calc outputs**. D2 has refs to calc outputs and a literal operator, but no sibling attribute refs. This is actually a different sub-pattern: **EXPOSE+operator** (an expression that wraps a calc output reference in arithmetic). Item 2's `ComputedAttributeClassification` should decide whether this is a sub-type of EXPOSE or a distinct category. See recommendation below.

### 2. `reconstruct_expression()` loses parenthesization

The `sysml_text` for B3 shows `r_inner + r_outer / 2.0 - r_major` but the AST (and compiled output) correctly preserves `(r_inner + r_outer) / 2.0 - r_major`. Similarly, B6's text omits grouping.

**Impact on Item 2:** Never use `reconstruct_expression()` output for semantic analysis or correctness validation. Always compile from the AST. The text is useful only for human-readable display in logs/reports, and should include a caveat that grouping may not be shown.

### 3. EXPOSE ref structure: two separate refs, not a dotted path

`extract_feature_refs()` returns `['result', 'scale_calc']` as two separate refs for `scale_calc.result`, not a single dotted ref `'scale_calc.result'`. The Q4 cross-part analysis finds 0 dotted references because of this decomposition.

**Impact on Item 2:** EXPOSE resolution must reconstruct the dotted path from the two FeatureChainExpression segments. The first ref's `qualified_name` (`AttrExprProbeLibrary::ScaleCalc::result`) identifies the CalcDef output. The second ref's `qualified_name` (`AttrExprProbeDesign::probe_design::scale_calc`) identifies the CalcUsage instance. Item 2's extraction logic should match on the CalcUsage qualified name to resolve the upstream module and output channel.

---

## Answers to Key Questions

### Can the Phase 1 compiler handle chains (computed-attr-referencing-computed-attr)?

**Yes, trivially.** C1 (`area * rate` where `area = length * width`) compiles to `(inputs.area * inputs.rate)`. The compiler treats `area` as just another input name. Chain resolution is a **graph-builder concern** (topological ordering in Item 3), not a compiler concern (Item 2).

### Does SysIDE produce correct ASTs for diverse FORMULA patterns?

**Yes, for all 14 FORMULA patterns tested.** Operator precedence, parenthesized grouping, N-ary left-fold, deeply nested sub-expressions (7 refs, B6), and mixed ref+literal operands all produce correct ASTs that compile to correct Python.

### Can computed attributes feed CalcUsage inputs?

**Yes.** D1 (`calc scale_calc : ScaleCalc { in value = area; }` where `area` is computed) parses without error. SysIDE treats the binding `in value = area` the same whether `area` is a literal or a computed attribute.

### What node types does the probe encounter?

Only expected types: `OperatorExpression`, `FeatureReferenceExpression`, `FeatureChainExpression`, `LiteralRational`. Zero unexpected types (FR-9 clean).

---

## Recommended Changes to Epic Items

### Item 2: Computed Attribute Extraction & Data Models

**Change 1: No chain-awareness needed in extraction logic.**

The epic's Item 2 scope includes: *"Chain reference: `y = x * 2` where x is also computed (FORMULA, dependency chain)"* as a unit test case. This is still a valid test case, but the extraction/compilation logic doesn't need any special handling for it. The test should verify that `y = x * 2` compiles to `(inputs.x * 2.0)` -- the same as if `x` were a literal. The "chain" aspect is purely Item 3's concern.

**Suggested change:** In Item 2's scope section, clarify that the "chain reference" unit test validates that compilation produces `(inputs.x * 2.0)` without special chain handling. Remove any implication that the extraction module needs to detect or resolve chains. Add a note: "Chain dependency ordering is deferred to Item 3 (graph builder)."

**Change 2: Refine MIXED classification to capture EXPOSE+operator.**

The current MIXED definition is "references both sibling attributes and calc outputs." The probe found a pattern (D2: `scale_calc.result * 2.0`) that is an operator expression wrapping a calc output reference with a literal -- not captured by the current MIXED definition (no sibling attribute refs).

**Suggested change:** Add a sub-classification or flag for EXPOSE patterns that involve arithmetic:
- `EXPOSE_PURE`: Single FeatureChainExpression, no operators (D3, D4a, D4b) -- can be wired as a direct alias
- `EXPOSE_COMPUTED`: FeatureChainExpression inside OperatorExpression (D2) -- needs either FeatureChainExpression compiler support or decomposition into EXPOSE + FORMULA

Alternatively, keep the existing four categories but define MIXED more broadly: "any expression containing both FeatureChainExpression nodes and other operands (refs or literals)." Under this definition, D2 would be MIXED as originally predicted.

**Change 3: Use qualified names for classification, not simple names.**

The v1 spike (plan.md Phase 2 notes) documented that 19 CATF attributes were misclassified as MIXED because EXPOSE ref simple names collided with sibling attribute names. The probe confirms that `qualified_name` reliably distinguishes: `AttrExprProbeLibrary::ScaleCalc::result` vs. `AttrExprProbeDesign::probe_design::area`. Item 2's classifier MUST use qualified name resolution.

**Suggested change:** In Item 2 scope section 2 (Extraction logic), add: "Classification MUST resolve references via `qualified_name`, not `ref.name`, to avoid false MIXED classification when a CalcDef output shares a simple name with a sibling attribute."

**Change 4: `reconstruct_expression()` is display-only, not semantic.**

**Suggested change:** Add to Item 2 scope: "`ComputedAttributeData.expression_text` is populated via `reconstruct_expression()` for display/logging only. It does not preserve parenthesization. All semantic analysis and compilation MUST use the raw AST (`expression_ast` field)."

### Item 3: Pipeline Integration

**Change 1: Chain resolution = topological ordering only.**

The probe proves that the compiler emits `inputs.area` for computed attrs the same way it emits `inputs.length` for literals. Item 3's backtracker/graph-builder work for chains is purely about **ordering modules correctly**, not about transforming expressions.

**Suggested change:** In Item 3 scope section 2 (Dependency resolution), simplify the chain-handling description:

> *Current:* "When a CalcUsage binds to a design attribute that is computed (not a literal), resolve the binding through the computed attribute's expression to its upstream dependencies"
>
> *Revised:* "Computed attributes generate synthetic modules. When a downstream module (CalcUsage or another computed attribute) references a computed attribute's output, the graph builder wires the upstream module's output to the downstream module's input. The expression compiler handles this transparently -- no expression transformation needed. The key requirement is correct topological ordering: computed attribute modules must be ordered after their dependencies."

**Change 2: EXPOSE wiring strategy is clear now.**

The probe confirms EXPOSE patterns (`scale_calc.result`) produce FeatureChainExpression nodes that fail compilation with `unsupported operator: .`. Two approaches for Item 3:

- **Option A (Alias):** Pure EXPOSE (`D3: scale_result = scale_calc.result`) doesn't need a synthetic module at all. It's a channel alias: map the attribute name to the upstream CalcUsage output channel. No compilation needed.
- **Option B (Decompose EXPOSE+operator):** D2 (`scaled_area = scale_calc.result * 2.0`) could be decomposed: first resolve the EXPOSE ref to the upstream channel, then generate a FORMULA module that takes the channel output as an input and applies `* 2.0`.

**Suggested change:** Add to Item 3 scope: "Pure EXPOSE attributes are wired as channel aliases (no synthetic module). EXPOSE+operator attributes (FeatureChainExpression inside OperatorExpression) are decomposed: the FeatureChain ref resolves to an upstream output channel, which becomes an input to a synthetic FORMULA module applying the remaining arithmetic."

**Change 3: D1 validates computed-attr-to-CalcUsage binding.**

The probe confirms that CalcUsage bindings can reference computed attributes (`in value = area` where `area` is computed). This means Item 3's backtracker must detect when a CalcUsage binding points to a computed attribute and wire the dependency through the computed attribute's synthetic module.

**Suggested change:** In Item 3 scope section 2, add: "When a CalcUsage binding references a computed attribute (verified working by D1 probe test), the backtracker should resolve the binding to the computed attribute's synthetic module output, creating a dependency edge in the computation graph."

### Item 4: E2E Validation

**Change 1: Reuse `attr_expr_probe` fixture.**

Item 4 planned to create `tests/fixtures/computed_attribute_model/` with chains, multi-reference formulas, EXPOSE patterns, and mixed patterns. The `attr_expr_probe` fixture already contains all of these (14 FORMULA + 3 chain + 4 EXPOSE + 2 CalcUsages with computed attr inputs).

**Suggested change:** Reuse `tests/fixtures/attr_expr_probe/` as the primary E2E validation fixture for Item 4, rather than creating a new one. Extend it if needed (e.g., add numerical ground-truth values for validation), but don't duplicate the fixture.

**Change 2: Numerical validation targets are derivable.**

Since all literal input values are specified in the probe fixture, ground-truth computed values can be calculated:

| Attribute | Expression | Expected Value |
|-----------|-----------|----------------|
| area | 10.0 * 5.0 | 50.0 |
| volume | 10.0 * 5.0 * 3.0 | 150.0 |
| cost | 50.0 * 12.0 | 600.0 |
| marked_up_cost | 600.0 * 1.15 | 690.0 |
| cost_density | 600.0 / 150.0 | 4.0 |
| q_scientific | 2600.0 / 50.0 | 52.0 |
| perimeter | 2.0 * 10.0 + 2.0 * 5.0 | 30.0 |
| minor_radius | (4.2 + 4.4) / 2.0 - 3.0 | 1.3 |
| p_alpha | 2600.0 * 3.52 / 17.58 | ~520.36... |
| p_blanket_thermal | (1.1*2600) + 50 + 0.46*(0.06*0.5+0.03)*(1.1*2600) | ~2980.44... |
| scale_calc.result | 50.0 * 1.15 | 57.5 |
| scaled_area | 57.5 * 2.0 | 115.0 |
| half_vol | 150.0 / 2.0 | 75.0 |
| quarter_vol | 150.0 / 4.0 | 37.5 |

These can be used directly as E2E assertions with exact floating-point equality (no tolerance needed -- all inputs are exact rationals).

---

## Updated Risk Assessment

| Risk (from Epic) | Original Rating | Updated Rating | Rationale |
|-------------------|----------------|----------------|-----------|
| SysIDE does not populate `feature_value_expression` on PartDef attributes | High | **RETIRED** | v1 proved ASTs available. v2 confirms across 35 attrs. |
| Attribute references cannot be resolved to sibling attributes via AST | High | **RETIRED** | v2 confirms: all 14 FORMULA patterns resolve refs to siblings via simple name match. |
| EXPOSE pattern already handled by backtracker transitive resolution | Low (positive) | **Unchanged** | Still needs investigation in Item 3. |
| Synthetic module approach creates excessive pipeline modules | Medium | **Low** | FORMULA attrs naturally map 1:1 to modules. Pure EXPOSE can be aliases (no module). |
| Cross-part attribute references require hierarchy support | Medium | **Low** | v2 probe has 0 cross-part refs. v1 also had 0. This is a Phase 3 concern. |
| Existing CalcDef auto-implementations regress | Low | **Unchanged** | 167 tests still pass after probe addition. |
| Architecture decision wrong | Medium | **Low** | Probe data strongly supports Option C (direct graph integration): FORMULA compiles, EXPOSE needs alias wiring, chains are graph ordering. |

### New Risks Identified

| Risk | Rating | Mitigation |
|------|--------|-----------|
| EXPOSE+operator pattern (D2) requires FeatureChainExpression compiler support or decomposition | Medium | Item 3 should implement decomposition: resolve EXPOSE ref to channel, feed into FORMULA module. Avoids compiler changes. |
| `reconstruct_expression()` losing parenthesization could mislead debugging | Low | Document as display-only. Item 2 `expression_text` field should note this limitation. |
| CATF MIXED misclassification (19 attrs in v1) due to simple-name collision | Medium | Item 2 MUST use qualified name resolution. v2 confirms qualified names are reliable. |

---

## Conclusion

The probe provides strong empirical evidence that **FORMULA patterns work comprehensively and reliably**. All 14 FORMULA attributes (including 3-term products, nested parenthesized expressions, 7-ref deep nesting, and computed-attr chains) produce correct ASTs and compile to correct Python. The Phase 1 compiler requires **zero changes** for FORMULA patterns.

The critical chain finding -- that the compiler treats computed attributes identically to literal attributes -- significantly simplifies Items 2 and 3. Item 2's extraction logic doesn't need chain-awareness. Item 3's chain handling is purely topological ordering in the graph builder.

EXPOSE patterns fail compilation as expected (FeatureChainExpression unsupported), but pure EXPOSE can be implemented as channel aliases without compilation. The EXPOSE+operator sub-pattern (D2) is a tractable decomposition problem for Item 3.

**Go/no-go: GO, with high confidence.** The v1 spike answered "are ASTs available?" (yes). The v2 probe answers "do diverse FORMULA patterns compile correctly?" (yes, 14/14). The remaining work in Items 2-4 is integration engineering, not research.
