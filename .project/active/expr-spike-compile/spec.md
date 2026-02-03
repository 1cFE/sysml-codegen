# Spec: Spike -- Expression Compilation & Compilability Classification

**Status:** Complete
**Owner:** Reid Westwood
**Created:** 2026-02-03T01:57:00Z
**Complexity:** MEDIUM
**Branch:** cost-pattern
**Epic:** EXPR-CODEGEN Item 2

---

## Business Goals

### Why This Matters

Item 1 validated that 95.8% of CalcDef outputs have extractable expression ASTs and 98.6% of feature references resolve to declared inputs or sibling outputs. Those were necessary but not sufficient conditions. Item 2 answers the next two critical questions:

1. Can we turn those ASTs into **correct, executable Python**?
2. Can we **reliably classify** which CalcDefs are compilable vs. manual-required?

If compiled expressions don't match handwritten ground truth, or if the classifier produces false positives (says compilable but the output is wrong), the expression compiler module (Item 3) would be built on a faulty foundation.

### Success Criteria

- [ ] All compiled expressions pass `ast.parse()` (syntactically valid Python)
- [ ] For CalcDefs with existing handwritten impls, compiled output matches within `1e-10`
- [ ] Zero false positives: nothing classified `FULLY_COMPILABLE` produces wrong results
- [ ] Classifier boundaries documented: which CalcDefs compile, which don't, why
- [ ] Python operator mapping validated against all 5 operators found in Item 1

### Priority

P1 -- gates Item 3 (Expression Compiler Module). Sequential dependency on Item 1 (complete, GO recommendation).

---

## Problem Statement

### Current State

Item 1 proved we can extract ASTs and resolve references. But extraction and resolution are only the first half of compilation. We still don't know:

- Whether the recursive AST-to-Python transformation produces semantically correct code (not just syntactically valid)
- Whether the 5 operators found (`+`, `-`, `*`, `/`, `**`) map correctly to Python in all nesting contexts (e.g., Pattern C's CRF formula with parenthesized `**` at depth 4)
- Whether `LiteralRational` nodes reliably expose `.value` as a usable numeric (the concept doc assumes this but it hasn't been tested)
- Whether topological ordering of intermediate outputs (required for Pattern B's multi-step CalcDefs) correctly handles all 61 intermediate refs in solar_battery
- Whether the 3 unresolvable CATF refs (undeclared intermediates in `MagnetCryogenicLoad`, `VacuumPumpPower`, `CryoPumpRefrigeration`) should be handled by extended resolution or classified as `MANUAL_REQUIRED`
- Whether a compilability classifier can cleanly partition CalcDefs with zero false positives

### Desired Outcome

Two spike scripts that prove (or disprove) correct compilation and classification, validated against real models with handwritten ground truth. A documented accuracy report with per-CalcDef results and a validated operator mapping.

---

## Scope

### In Scope

**Question 3 (Q3): Can we produce correct Python from the AST?**

For each CalcDef where Q1+Q2 passed (AST extractable, refs resolvable):
1. Build an `ExpressionAST` (per concept Section 3.3) from the syside AST node
2. Compile to a Python expression string using `inputs.<name>` for input refs and bare names for intermediate refs
3. Verify syntactic validity with `ast.parse()`
4. For CalcDefs with existing handwritten impls (solar_battery), compare: execute compiled expression with test inputs vs. execute handwritten impl with same inputs. Assert match within `1e-10`.
5. For multi-output CalcDefs (Pattern B), emit outputs in topological dependency order and verify intermediate references resolve correctly

**Question 4 (Q4): Does the compilability classifier agree with reality?**

Run a compilability classifier on ALL CalcDefs across all model suites (chain_spike, sample_model, solar_battery, CATF):
1. For each CalcDef, classify as `FULLY_COMPILABLE`, `PARTIALLY_COMPILABLE`, or `MANUAL_REQUIRED`
2. Cross-reference: if `FULLY_COMPILABLE`, does Q3 confirm the compiled version produces correct results?
3. If `MANUAL_REQUIRED`, verify the reason is accurate (e.g., missing AST, unresolvable ref, unsupported construct)
4. If `PARTIALLY_COMPILABLE`, document which outputs compile and which don't

**Classification boundary rules** (restated from concept doc Section 2, Principle 2):
- `FULLY_COMPILABLE`: ALL output attributes have extractable ASTs AND all refs in every output resolve to declared inputs or sibling outputs (intermediates). The entire CalcDef can be auto-implemented.
- `PARTIALLY_COMPILABLE`: SOME output attributes compile (refs resolve, AST extractable) but at least one does not (missing AST, unresolvable ref, unsupported construct). The CalcDef has a mix -- some outputs get generated code, others get `NotImplementedError` stubs or TODOs.
- `MANUAL_REQUIRED`: NO output attributes can be compiled, OR the CalcDef contains constructs that make the entire impl unsafe to auto-generate (e.g., circular intermediate dependencies, unsupported operators in a critical output).

The boundary between `PARTIALLY_COMPILABLE` and `MANUAL_REQUIRED` is **per-output**: a CalcDef is `PARTIALLY_COMPILABLE` if at least one output compiles and at least one doesn't. It is `MANUAL_REQUIRED` only if zero outputs compile. The Q4 script validates that this rule produces correct classifications by cross-referencing against Q3's per-output compilation results.

**Operator mapping validation**:
- Confirm the Python operator mapping is correct for all 5 operators from Item 1: `+`, `-`, `*`, `/`, `**`
- Document handling of `^` (alias for `**`) and `[` (unit annotation strip) even though neither was observed in Item 1
- Validate operator precedence is correct for nested expressions (Pattern C: CRF formula at depth 4)

**Undeclared intermediates investigation**:
- Item 1 found 3 unresolvable refs in CATF (`thermal_load_cryo`, `pump_power_per_unit`, `thermal_load`) that are same-CalcDef members not declared as in/out
- Q3 SHOULD attempt extended resolution: check all CalcDef members (not just declared in/out) for these refs
- Document whether extended resolution succeeds, and recommend the handling strategy for Item 3
- **Data model impact**: If extended resolution succeeds, the finding feeds back into Item 3's data model design. Specifically, the concept doc's `ExpressionAST` defines `INPUT_REF` and `INTERMEDIATE_REF` where "intermediate" means a declared `out` attribute. If undeclared intermediates exist, either (a) the definition of `INTERMEDIATE_REF` expands to include undeclared same-CalcDef members, or (b) a new node type is needed (e.g., `UNDECLARED_MEMBER_REF`). The report MUST recommend which approach Item 3 should take.

**Model Coverage**:

| Suite | CalcDefs | Q1 Coverage | Q2 Resolution | Q3/Q4 Role |
|-------|----------|-------------|---------------|------------|
| chain_spike | 3 | 100% | 100% | Compilation smoke test (Pattern A) |
| sample_model | 7 | 100% | 100% | Additional Pattern A coverage |
| solar_battery | 15 | 100% | 100% | **Ground truth comparison** (Patterns A-D) |
| CATF | ~30 | 86.7% | 95.8% | Classifier boundary testing + undeclared intermediates |

**Ground truth comparison (solar_battery)**:

The solar_battery model has existing handwritten `_impl.py` files that serve as ground truth. The Q3 script validates compiled expressions against these handwritten impls.

**Comparison approach**: The script MUST NOT import the generated package or construct Pydantic input models. Instead, it uses **standalone execution**: for each CalcDef, the script builds a plain `dict` of input values, then:
1. Executes the **compiled expressions** directly: assigns `inputs = SimpleNamespace(**input_dict)`, runs each compiled expression line in order, collects output values.
2. Executes the **handwritten impl** the same way: reads the handwritten `_impl.py` file, extracts the function body (the math after the docstring, before the return), executes it with the same `SimpleNamespace` inputs.
3. Compares output values within `1e-10` relative tolerance.

This avoids importing the generated package (which may not be in a runnable state on this branch) and avoids fragile regex extraction of math from handwritten files. Both sides execute Python expression strings in the same controlled environment. If a handwritten impl uses patterns that can't be executed this way (e.g., imports, helper functions, multi-line logic), that CalcDef is excluded from numerical comparison and noted in the report.

**Test input sourcing**: All test inputs MUST be **strictly positive non-zero floats** (e.g., values in the range `[0.5, 100.0]`). This prevents domain issues in multi-output CalcDefs where intermediate values appear as divisors (e.g., Pattern B's `idiot_index = total_cost / material_cost` would divide by zero if `material_cost == 0`). Input values SHOULD be derived from:
1. Existing JSON input templates in the generated package (if available)
2. `default :=` values from the SysML model's CalcDef input attributes
3. Deterministic synthetic values (e.g., `{param_name: hash(param_name) % 100 + 1.0}`) as fallback

The fallback strategy ensures reproducibility without requiring external files.

### Out of Scope

- Building the final `expression_compiler.py` module (Item 3)
- Handling `InvocationExpression` (function calls like `sqrt`) -- zero occurrences in Item 1
- Conditional expressions (`if/else`) -- zero occurrences in CalcDef outputs in Item 1
- Modifying any pipeline code (extractor, resolution, generation)
- Attribute-level expressions on part definitions (Phase 2)
- `FeatureChainExpression` in CalcDef output expressions (Edge 5 from concept doc -- not observed in any model)
- `sum()` over collections (Pattern G -- classified `MANUAL_REQUIRED`)

### Edge Cases & Considerations

- **Literal-only outputs** (e.g., `PermittingCostCalc.material_cost = 0.0`): These compile to bare numeric literals. Q3 MUST handle `LiteralRational` as a root node (not just as an operand within `OperatorExpression`).

- **Passthrough outputs** (e.g., `PlasmaConfinement.p_fusion = p_fusion_input`): These are bare `FeatureReferenceExpression` nodes with no operators. They compile to `inputs.<name>` or a bare intermediate name. Q3 MUST handle this degenerate case.

- **Deeply nested expressions** (depth 4-6): `AnnualizedFinancialCalc.capital_recovery_factor` (depth 4), `LCOECalc.lcoe_per_mwh` (depth 5), `TorusVolume.volume` (depth 6). These stress-test operator precedence and parenthesization. Q3 MUST verify that the compiled expression respects Python operator precedence and adds parentheses only where needed.

- **Pi as repeated literal** (Pattern E): `TorusVolume.volume = 2.0 * 3.14159265359 * 3.14159265359 * ...`. The compiler MUST NOT substitute `math.pi` -- it faithfully reproduces the SysML literal per concept Section 3.7.

- **Multi-operand expressions**: Item 1 found expressions like `NetElectricPower.p_parasitic_total` with 7-input sums (depth 6). SysIDE may represent `a + b + c + d` as left-nested binary ops `((a+b)+c)+d` or as a single `OperatorExpression` with multiple operands. Q3 MUST handle both representations.

- **Floating-point representation of `LiteralRational`**: SysIDE's `LiteralRational` may expose values as strings (e.g., `"3.14159"`) rather than floats. Q3 MUST document the actual `.value` type and handle string-to-float conversion if needed.

- **Unary negation**: Item 1 found only binary operators, but SysML expressions like `out x = -y` would produce a unary `-` (`OperatorExpression` with a single operand). The concept doc's `ExpressionAST` includes `UNARY_OP` for this case. If unary negation is encountered during Q3, the script MUST handle it (emit `-<operand>` in Python). If not encountered, the report SHOULD note its absence so Item 3 can decide whether to include defensive handling.

---

## Requirements

### Functional Requirements

> Requirements below are from the epic backlog item and concept doc unless marked [INFERRED].

1. **FR-1**: Q3 script (`scripts/spike_compile_expressions.py`) MUST build an `ExpressionAST` from the syside AST for each compilable CalcDef output, compile it to a Python expression string, and verify with `ast.parse()`.

2. **FR-2**: Q3 script MUST handle all 3 node types from Item 1: `OperatorExpression`, `FeatureReferenceExpression`, `LiteralRational`.

3. **FR-3**: Q3 script MUST handle all 5 operators from Item 1: `+`, `-`, `*`, `/`, `**`.

4. **FR-4**: Q3 script MUST compile multi-output CalcDefs (Pattern B) with outputs in topological dependency order. Intermediate refs MUST use bare variable names (not `inputs.` prefix).

5. **FR-5**: Q3 script MUST compare compiled output against handwritten impls for solar_battery CalcDefs using the standalone execution approach (see "Ground truth comparison" in Scope). Comparison uses identical test inputs (strictly positive non-zero) and asserts match within `1e-10` relative tolerance. CalcDefs whose handwritten impls cannot be executed standalone (e.g., contain imports or helper functions) are excluded from numerical comparison and noted in the report.

6. **FR-6**: Q4 script (`scripts/spike_classify_compilability.py`) MUST classify ALL CalcDefs across all 4 model suites as `FULLY_COMPILABLE`, `PARTIALLY_COMPILABLE`, or `MANUAL_REQUIRED`.

7. **FR-7**: Q4 script MUST report the classification reason for every `PARTIALLY_COMPILABLE` and `MANUAL_REQUIRED` verdict (e.g., "missing AST for output X", "unresolvable ref: thermal_load_cryo").

8. **FR-8**: Q4 script MUST cross-reference verdicts against Q3 results: every `FULLY_COMPILABLE` CalcDef MUST have passed Q3's `ast.parse()` check and (where ground truth exists) numerical comparison.

9. **FR-9**: Both scripts MUST accept model paths as CLI arguments (one or more directories), defaulting to all in-repo fixture directories plus CATF if accessible.

10. **FR-10**: Both scripts MUST print results as formatted tables to stdout, suitable for copy-paste into the report.

11. **FR-11**: [INFERRED] Q3 script MUST handle the 3 unresolvable CATF refs by attempting extended resolution (checking all CalcDef members, not just declared in/out). Document whether this succeeds.

12. **FR-12**: Q3 script MUST generate a complete function body for each CalcDef (not just per-output expressions), including local variable assignments for intermediates and a return statement, to validate that the full compilation flow works end-to-end. This directly validates the topological sort and `CalcDefCompilationResult.execution_order` field from the concept doc (Section 3.3) -- the hardest part of compilation for multi-output CalcDefs.

### Non-Functional Requirements

- Scripts SHOULD run in under 60 seconds per model suite
- Scripts MUST NOT modify any source code, test fixtures, or pipeline files
- Scripts MUST be runnable via `uv run python scripts/spike_*.py`

---

## Evaluation Methodology

### Q3 Evaluation: Compilation Correctness

**Metric 1: Syntactic validity** = `ast_parse_pass / total_compiled * 100`

| Result | Interpretation | Action |
|--------|---------------|--------|
| 100% pass | All compiled expressions are valid Python | Go |
| 90-99% | Near-miss; investigate failures | Fix compiler logic, re-run |
| < 90% | Fundamental compilation issue | No-go; revisit AST-to-Python strategy |

**Metric 2: Numerical accuracy** (solar_battery only) = matched / compared

| Result | Interpretation | Action |
|--------|---------------|--------|
| 100% match within 1e-10 | Compiled code is semantically correct | Go |
| Any mismatch | Compiled code produces wrong results | Investigate: operator mapping? precedence? intermediate ordering? |

**Per-CalcDef reporting**: Every CalcDef MUST have a row in the results table showing: CalcDef name, outputs compiled, `ast.parse()` result, numerical match result (if ground truth exists), and any notes.

### Q4 Evaluation: Classifier Accuracy

**Critical metric: Zero false positives.** If ANY CalcDef is classified `FULLY_COMPILABLE` but Q3 shows it produces wrong results, the classifier is broken.

| Metric | Target | Notes |
|--------|--------|-------|
| False positive rate | 0% | Non-negotiable |
| False negative rate | < 20% | Acceptable initially; track for improvement |
| Classification coverage | 100% of CalcDefs across all suites | Every CalcDef gets a verdict |

**Per-CalcDef classification table**: CalcDef name, verdict, reason (if not FULLY_COMPILABLE), cross-reference to Q3 result.

### Go/No-Go Decision

**Go** requires ALL of:
- Q3 syntactic validity = 100%
- Q3 numerical accuracy = 100% match for all solar_battery CalcDefs with ground truth
- Q4 false positive rate = 0%
- Operator mapping validated for all 5 operators
- Topological ordering works for all multi-output CalcDefs

**No-go** if ANY of:
- Q3 numerical mismatch on any CalcDef with ground truth
- Q4 false positive (classified FULLY_COMPILABLE but produces wrong results)
- Fundamental operator mapping error

**Conditional go** (proceed with reduced scope) if:
- Some CalcDefs fail compilation due to edge cases not in Patterns A-F (e.g., undeclared intermediates), but the failures are correctly classified as `MANUAL_REQUIRED` by Q4

---

## Acceptance Criteria

### Core Functionality
- [ ] `scripts/spike_compile_expressions.py` exists and runs without errors on all model suites
- [ ] `scripts/spike_classify_compilability.py` exists and runs without errors on all model suites
- [ ] Q3 output includes: per-CalcDef per-output table with compiled expression, `ast.parse()` result, numerical match
- [ ] Q3 output includes: full function body generation for multi-output CalcDefs (intermediates + return)
- [ ] Q3 output includes: operator mapping validation table (all 5 operators)
- [ ] Q4 output includes: per-CalcDef classification table with verdict and reason
- [ ] Q4 output includes: cross-reference against Q3 results (zero false positives confirmed)
- [ ] Q4 output includes: summary statistics (counts per verdict, false positive rate)

### Deliverables
- [ ] `scripts/spike_compile_expressions.py`
- [ ] `scripts/spike_classify_compilability.py`
- [ ] `.project/active/expr-spike-compile/report.md` (accuracy report + operator map + go/no-go)

### Quality & Integration
- [ ] No existing tests broken
- [ ] Scripts are self-contained (no pipeline code modifications)
- [ ] Report contains quantitative evidence for every claim
- [ ] Undeclared intermediate handling strategy documented (for the 3 CATF refs)

---

## Known Model Inventory

### Compilation Targets by Pattern (from Item 1 findings)

**Pattern A -- Simple Binary** (chain_spike, sample_model):

| CalcDef | Output | Expression | Notes |
|---------|--------|-----------|-------|
| AreaCalc | area | `length * width` | 2 input refs, depth 1 |
| CostCalc | total_cost | `area * rate` | 2 input refs, depth 1 |
| SummaryCalc | cost_per_area | `cost / area` | 2 input refs, depth 1 |

**Pattern B -- Multi-Step Intermediate** (solar_battery, 10 CalcDefs):

Each cost CalcDef has 5 outputs with intermediate dependencies:
```
material_cost = inputs * inputs           (input refs only)
fab_cost = material_cost * fab_factor     (intermediate + input ref)
install_cost = material_cost * ...        (intermediate + input ref)
total_cost = material_cost + fab_cost + install_cost  (3 intermediate refs)
idiot_index = total_cost / material_cost  (2 intermediate refs)
```

CalcDefs: PVModuleCostCalc, InverterCostCalc, ArrayBOSCostCalc, BatteryPackCostCalc, HybridInverterCostCalc, BatteryBOSCostCalc, RackingCostCalc, ElectricalPanelCostCalc, PermittingCostCalc, AllocationCostCalc.

**Pattern C -- Complex Parenthesized** (solar_battery):

| CalcDef | Output | Depth | Operators |
|---------|--------|-------|-----------|
| AnnualizedFinancialCalc | capital_recovery_factor | 4 | `*, **, +, -, /` |
| LCOECalc | lcoe_per_mwh | 5 | `*, **, +, /` |

**Pattern D -- Literal Constants** (solar_battery):

| CalcDef | Output | Expression | Notes |
|---------|--------|-----------|-------|
| PermittingCostCalc | material_cost | `0.0` | Bare literal |
| EnergyProductionCalc | hours_per_year | `8760.0` | Bare literal |

**CATF -- Classifier Boundary Cases**:

| CalcDef | Expected Verdict | Reason |
|---------|-----------------|--------|
| PlasmaConfinement | PARTIALLY_COMPILABLE or MANUAL_REQUIRED | 2 outputs missing ASTs, 1 passthrough |
| TritiumBreedingRatio | PARTIALLY_COMPILABLE or MANUAL_REQUIRED | 2 outputs missing ASTs |
| MagnetCryogenicLoad | Investigate | 1 unresolvable ref (undeclared intermediate) |
| VacuumPumpPower | Investigate | 1 unresolvable ref (undeclared intermediate) |
| CryoPumpRefrigeration | Investigate | 1 unresolvable ref (undeclared intermediate) |
| ~25 other CATF CalcDefs | FULLY_COMPILABLE | All ASTs present, all refs resolve |

---

## Related Artifacts

- **Concept:** `.project/concepts/expression-aware-codegen.md` (Sections 3.3, 4, 5, 6)
- **Epic:** `.project/backlog/epic_expression_aware_codegen.md` (Item 2)
- **Research:** `.project/research/20260202-180000_expression-compilation-and-inline-math-strategy.md`
- **Item 1 Report:** `.project/active/expr-spike-ast/report.md` (AST findings, node type inventory, operator inventory)
- **Item 1 Spec:** `.project/active/expr-spike-ast/spec.md`
- **Design:** `.project/active/expr-spike-compile/design.md` (N/A -- spike has no design phase)

---

**Next Steps:** After approval, proceed directly to implementation (write spike scripts, run against all model suites, write report). No design phase needed for a research spike.
