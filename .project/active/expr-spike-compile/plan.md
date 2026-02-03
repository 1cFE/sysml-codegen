# Implementation Plan: Spike -- Expression Compilation & Compilability Classification

**Status:** Complete
**Created:** 2026-02-03
**Last Updated:** 2026-02-03

## Source Documents
- **Spec:** `.project/active/expr-spike-compile/spec.md`
- **Concept:** `.project/concepts/expression-aware-codegen.md` (Sections 3.3, 4, 5, 6)
- **Item 1 Report:** `.project/active/expr-spike-ast/report.md`
- **Item 1 Scripts:** `scripts/spike_extract_expression_asts.py`, `scripts/spike_resolve_expression_refs.py` (reusable patterns)

## Implementation Strategy

**Phasing Rationale:**
The core risk is whether AST-to-Python transformation produces correct code. We de-risk this first (Phase 1-2) with syntactic validation, then prove semantic correctness against ground truth (Phase 3), then build the classifier on top of proven compilation results (Phase 4). The report is last because it synthesizes all findings.

**Key Finding from Investigation:**
Only **5 of 15** solar_battery handwritten impls have actual code. The other 10 are `NotImplementedError` stubs. Numerical comparison (Phase 3) is limited to:
- `AnnualizedFinancialCalc` -- Pattern C (CRF formula with `**`, depth 4)
- `LCOECalc` -- Pattern C (compound with `**`, depth 5)
- `EnergyProductionCalc` -- Pattern D (literal 8760.0 * inputs)
- `AnnualizedFuelCalc` -- Pattern A (simple binary)
- `AnnualizedOMCalc` -- Pattern A (simple binary)

The remaining 10 CalcDefs (all Pattern B cost calcs) are validated syntactically only. Their SysML docstring expressions serve as a secondary cross-check.

**Handwritten Impl Compatibility Note:**
The standalone execution approach from the spec (SimpleNamespace) works directly for 3 of 5 implemented CalcDefs (EnergyProductionCalc, AnnualizedFuelCalc, AnnualizedOMCalc -- they use `inputs.X` directly). AnnualizedFinancialCalc uses local variables (`r = inputs.discount_rate; n = inputs.plant_lifetime; crf = r * ...`), and LCOECalc uses a multi-line return expression. Both are executable standalone because they only reference `inputs.X` -- the local variable assignments are just Python, no imports beyond the type annotation line. The script can `exec()` the function body (skipping the import and type annotation line) with a SimpleNamespace.

**Overall Validation Approach:**
- Phase 1-2: `ast.parse()` on every compiled expression (syntactic gate)
- Phase 3: `exec()` + numerical comparison on 5 implemented CalcDefs (semantic gate)
- Phase 4: Classification cross-referenced against Phase 1-3 results (no false positives)
- Each phase runs the full script on all 4 model suites before proceeding

---

## Phase 1: AST-to-Python Compiler Core

### Goal
Build the core expression compiler that transforms syside AST nodes into Python expression strings. Validate on chain_spike (Pattern A) and solar_battery simple cases (Pattern D literals). This is the highest-risk phase -- if the recursive traversal doesn't produce valid Python, nothing else works.

### Test Stencil (Write This First)
```python
# Embedded in spike_compile_expressions.py as self-validation
# After compiling each expression, immediately verify:

import ast

compiled = compile_expression(syside_ast_node, input_names, output_names)
try:
    ast.parse(compiled, mode='eval')
    print(f"  PASS: {calc_name}.{output_name} -> {compiled}")
except SyntaxError as e:
    print(f"  FAIL: {calc_name}.{output_name} -> {compiled} ({e})")
    failures.append((calc_name, output_name, compiled, str(e)))
```

### Changes Required

#### 1. Q3 Script -- Core Compiler
**File:** `scripts/spike_compile_expressions.py` (NEW)

Reuse infrastructure from Item 1 scripts:
- `load_and_extract()` pattern from `spike_extract_expression_asts.py`
- `sanitize_name()` helper
- `DEFAULT_SUITES` definition (all 4 model suites)
- CLI argument parsing pattern

New functions to implement:

- [ ] `compile_expression(expr, input_names: set[str], output_names: set[str]) -> str`
  - Recursive AST-to-Python compiler
  - Dispatches on node type: `OperatorExpression`, `FeatureReferenceExpression`, `LiteralRational`
  - Uses OPERATOR_MAP from `constraint_extractor.py:33-50` as reference (copy the 5 arithmetic operators: `+`, `-`, `*`, `/`, `**`)
  - `FeatureReferenceExpression` → `inputs.<name>` if in `input_names`, bare `<name>` if in `output_names` (intermediate), `UNRESOLVED_<name>` if neither
  - `LiteralRational` → `str(node.value)` (document actual `.value` type)
  - `OperatorExpression` with 2 operands → `(<left> <op> <right>)` (parenthesized for safety)
  - `OperatorExpression` with 1 operand → `(-<operand>)` (unary negation, if encountered)
  - `OperatorExpression` with >2 operands → left-fold `((a op b) op c)`

- [ ] `analyze_and_compile_suite(label, model_paths) -> list[CalcDefCompileResult]`
  - Loads models, iterates CalcDefs, compiles each output expression
  - Runs `ast.parse()` on each compiled expression
  - Prints per-output results table

- [ ] Data classes: `OutputCompileResult`, `CalcDefCompileResult`

#### 2. Operator Mapping Table
- [ ] Define `PYTHON_OPERATOR_MAP` with all 5 operators from Item 1 plus defensive entries:
  ```python
  PYTHON_OPERATOR_MAP = {
      "+": " + ", "-": " - ", "*": " * ", "/": " / ", "**": " ** ",
      "^": " ** ",   # alias (not observed in Item 1 but documented)
      "[": None,     # unit annotation -- strip, return value operand only
  }
  ```
- [ ] Print operator validation table showing: operator, Python mapping, encountered (bool), example expression

### Validation

**Automated:**
- [ ] `uv run python scripts/spike_compile_expressions.py tests/fixtures/chain_spike_model` → all 3 outputs compile, all pass `ast.parse()`
- [ ] `uv run python scripts/spike_compile_expressions.py tests/fixtures/solar_battery_model` → literal outputs (PermittingCostCalc.material_cost = `0.0`, EnergyProductionCalc.hours_per_year = `8760.0`) compile correctly

**Manual:**
- [ ] Verify compiled expressions are human-readable (e.g., `inputs.length * inputs.width`, not `(inputs.length * inputs.width)` with unnecessary outer parens)
- [ ] Verify `LiteralRational.value` type is documented in output
- [ ] Verify unary negation handling is noted (encountered or absent)

**What We Know Works After This Phase:**
Single-output CalcDefs (Patterns A, D) compile to syntactically valid Python. The 3 node types and 5 operators from Item 1 are handled. `LiteralRational.value` behavior is documented.

---

## Phase 2: Topological Ordering + Full Function Body

### Goal
Extend the compiler to handle multi-output CalcDefs (Pattern B) with intermediate references. Build complete function bodies with local variable assignments and return statements. This validates `CalcDefCompilationResult.execution_order` from the concept doc.

### Test Stencil (Write This First)
```python
# For each multi-output CalcDef, generate full function body and validate:

body = compile_calc_def_body(calc_def, raw_elem, adapter)
# body looks like:
#   material_cost = inputs.wattage * inputs.cost_per_watt
#   fab_cost = material_cost * inputs.fab_factor
#   ...
#   return (material_cost, fab_cost, install_cost, total_cost, idiot_index)

# Wrap in function def and parse entire function:
func_code = f"def run(inputs):\n" + textwrap.indent(body, "    ")
try:
    ast.parse(func_code)
    print(f"  PASS: {calc_name} full body ({len(outputs)} outputs)")
except SyntaxError as e:
    print(f"  FAIL: {calc_name} full body: {e}")
```

### Changes Required

**File:** `scripts/spike_compile_expressions.py` (extend)

- [ ] `build_dependency_graph(calc_def, raw_elem, adapter) -> dict[str, set[str]]`
  - For each output, extract refs that are in `output_names` (intermediate dependencies)
  - Build adjacency dict: `{output_name: set of output_names it depends on}`

- [ ] `topological_sort(dep_graph: dict[str, set[str]]) -> list[str]`
  - Standard Kahn's algorithm
  - Detect circular dependencies → report as error, mark CalcDef as non-compilable
  - Returns execution order (dependencies first)

- [ ] `compile_calc_def_body(calc_def, raw_elem, adapter) -> str | None`
  - Calls `build_dependency_graph()` then `topological_sort()`
  - For each output in topological order:
    - Compile expression using `compile_expression()`
    - Emit `{output_name} = {compiled_expression}`
  - Append `return ({output1}, {output2}, ...)` or `return {output1}` for single-output
  - Returns `None` if any output fails to compile (with reason logged)

- [ ] Extend results table to show: CalcDef, output count, execution order, full body pass/fail

- [ ] Handle CATF undeclared intermediates (FR-11):
  - In `compile_expression()`, when a ref is not in `input_names` or `output_names`, attempt extended resolution: check all `raw_elem.owned_members` by name
  - If found as an undeclared member, log as `"undeclared_intermediate"` and treat like a regular intermediate ref
  - Document the finding and recommend data model approach for Item 3

### Validation

**Automated:**
- [ ] `uv run python scripts/spike_compile_expressions.py tests/fixtures/solar_battery_model` → all 15 CalcDefs produce full function bodies that pass `ast.parse()`
- [ ] PVModuleCostCalc (5 outputs) → execution order is `material_cost, fab_cost, install_cost, total_cost, idiot_index`
- [ ] AnnualizedFinancialCalc (2 outputs) → execution order is `capital_recovery_factor, annualized_capital_cost`

**Manual:**
- [ ] Verify intermediate refs use bare names (not `inputs.` prefix) in compiled bodies
- [ ] Verify topological order matches the dependency chain in the SysML source
- [ ] Review CATF undeclared intermediate results -- document whether extended resolution works

**What We Know Works After This Phase:**
Multi-output CalcDefs with intermediate dependencies compile to complete, syntactically valid function bodies. Topological sort produces correct execution order. Undeclared intermediate strategy determined.

---

## Phase 3: Ground Truth Comparison

### Goal
Execute compiled expressions and handwritten impls side-by-side with identical inputs. Prove numerical match within `1e-10` for the 5 implemented solar_battery CalcDefs. This is the semantic correctness gate.

### Test Stencil (Write This First)
```python
from types import SimpleNamespace

# For each CalcDef with a handwritten impl that has actual code:
input_dict = generate_test_inputs(calc_def)  # strictly positive non-zero
inputs = SimpleNamespace(**input_dict)

# Execute compiled version
compiled_body = compile_calc_def_body(...)
exec_globals = {"inputs": inputs}
exec(compiled_body_as_assignments, exec_globals)
compiled_outputs = {name: exec_globals[name] for name in output_names}

# Execute handwritten version (extract function body, skip import + def lines)
handwritten_body = extract_handwritten_body(impl_path)
hw_globals = {"inputs": inputs}
exec(handwritten_body, hw_globals)
# ... collect outputs from hw_globals or return value

# Compare
for name in output_names:
    assert abs(compiled_outputs[name] - handwritten_outputs[name]) < 1e-10 * abs(handwritten_outputs[name])
```

### Changes Required

**File:** `scripts/spike_compile_expressions.py` (extend)

- [ ] `generate_test_inputs(calc_def) -> dict[str, float]`
  - For each input attribute, produce a strictly positive non-zero float
  - Priority: (1) `default_value` from CalcDef input attributes, (2) deterministic synthetic: `hash(param_name) % 100 + 1.0`
  - All values in `[1.0, 101.0]` range

- [ ] `extract_handwritten_body(impl_path: Path) -> str | None`
  - Read the `_impl.py` file
  - Skip the import line and function definition line
  - Extract everything from after the docstring to the end of the function
  - Return `None` if the file contains `raise NotImplementedError` (stub -- skip comparison)
  - Return `None` if the body uses imports or complex patterns that can't be exec'd standalone

- [ ] `compare_compiled_vs_handwritten(calc_def, compiled_body, impl_path, input_dict) -> ComparisonResult`
  - Execute both sides with SimpleNamespace inputs
  - For single-return CalcDefs: compare the return value directly
  - For tuple-return CalcDefs: compare each element by output name
  - Handle the AnnualizedFinancialCalc pattern: local variable assignments (`r = inputs.discount_rate`) are valid Python and execute correctly in `exec()` with the SimpleNamespace
  - Report: match (bool), max_relative_error, per-output deltas

- [ ] `HANDWRITTEN_IMPL_DIR` constant pointing to `/home/reid/1cfe/fusion-tea/generated/solar_battery/handwritten/solarbatterylibrary/`

- [ ] Results table: CalcDef, comparison status (MATCH / MISMATCH / STUB / EXCLUDED), max relative error, notes

**Ground truth targets (5 implemented CalcDefs):**

| CalcDef | Pattern | Handwritten Style | Comparison Notes |
|---------|---------|-------------------|------------------|
| AnnualizedFinancialCalc | C | Local vars (`r`, `n`, `crf`), return tuple | Uses `inputs.X` -- exec-compatible |
| LCOECalc | C | Multi-line return expression | Uses `inputs.X` -- exec-compatible |
| EnergyProductionCalc | D + A | Single return expression | Uses `inputs.X` -- exec-compatible |
| AnnualizedFuelCalc | A | Single return expression | Uses `inputs.X` -- exec-compatible |
| AnnualizedOMCalc | A | Single return expression | Uses `inputs.X` -- exec-compatible |

**Stubs (10 CalcDefs -- comparison skipped):**
PVModuleCostCalc, InverterCostCalc, ArrayBOSCostCalc, BatteryPackCostCalc, HybridInverterCostCalc, BatteryBOSCostCalc, RackingCostCalc, ElectricalPanelCostCalc, PermittingCostCalc, AllocationCostCalc.

For stubs, comparison is skipped. Instead, the compiled output is cross-checked against the SysML expression shown in the docstring (a string-level sanity check, not numerical).

### Validation

**Automated:**
- [ ] All 5 implemented CalcDefs match within `1e-10` relative tolerance
- [ ] All 10 stub CalcDefs are correctly identified and skipped
- [ ] AnnualizedFinancialCalc (the most complex, Pattern C with `**`) matches

**Manual:**
- [ ] Review the compiled CRF expression vs the handwritten `r * (1 + r) ** n / ((1 + r) ** n - 1)` -- verify they're semantically equivalent
- [ ] Review the compiled LCOE expression vs the handwritten multi-line return
- [ ] Verify test inputs are all strictly positive non-zero

**What We Know Works After This Phase:**
Compiled expressions produce numerically correct results for all tested patterns (A, C, D). The compilation is semantically faithful to the SysML source.

---

## Phase 4: Compilability Classifier

### Goal
Build the Q4 script that classifies every CalcDef and cross-references against Q3 results. Validate zero false positives.

### Test Stencil (Write This First)
```python
# For each CalcDef:
verdict = classify_compilability(calc_def, raw_elem, adapter)
# verdict is one of: FULLY_COMPILABLE, PARTIALLY_COMPILABLE, MANUAL_REQUIRED

# Cross-reference: if FULLY_COMPILABLE, Q3 must have succeeded
if verdict == "FULLY_COMPILABLE":
    assert calc_name in q3_pass_set, f"FALSE POSITIVE: {calc_name} classified FULLY_COMPILABLE but Q3 failed"

# If MANUAL_REQUIRED, verify no outputs compiled in Q3
if verdict == "MANUAL_REQUIRED":
    assert calc_name not in q3_any_output_compiled, f"FALSE NEGATIVE: {calc_name} has compilable outputs"
```

### Changes Required

**File:** `scripts/spike_classify_compilability.py` (NEW)

Reuse infrastructure:
- `load_and_extract()`, `sanitize_name()`, `DEFAULT_SUITES` from Item 1 scripts
- `compile_expression()`, `build_dependency_graph()`, `topological_sort()` from Q3 script (import or inline)

New functions:

- [ ] `classify_output(output_name, raw_elem, calc_def, adapter) -> tuple[str, str | None]`
  - Returns `("compilable", None)` or `("not_compilable", reason)`
  - Checks: has AST? All refs resolve? No unsupported operators? No circular deps?

- [ ] `classify_calc_def(calc_def, raw_elem, adapter) -> tuple[str, str | None, dict]`
  - Calls `classify_output()` for each output
  - Applies boundary rules from spec:
    - All outputs compilable → `FULLY_COMPILABLE`
    - Some compilable, some not → `PARTIALLY_COMPILABLE`
    - None compilable → `MANUAL_REQUIRED`
  - Returns `(verdict, reason, per_output_details)`

- [ ] `cross_reference_q3(classifications, q3_results) -> list[str]`
  - For every `FULLY_COMPILABLE` CalcDef: verify all outputs passed `ast.parse()` in Q3
  - For every `FULLY_COMPILABLE` CalcDef with ground truth: verify numerical match in Q3
  - Return list of false positive CalcDef names (should be empty)

- [ ] Results tables:
  - Per-CalcDef classification table: CalcDef, suite, verdict, reason, outputs compilable/total
  - Summary: counts per verdict per suite
  - Cross-reference: false positive count (must be 0)
  - False negative inventory: `MANUAL_REQUIRED` CalcDefs that have compilable outputs (tracked for improvement)

**Expected classifications:**

| Suite | FULLY | PARTIAL | MANUAL | Notes |
|-------|-------|---------|--------|-------|
| chain_spike | 3 | 0 | 0 | All Pattern A |
| sample_model | ~7 | 0 | 0 | All Pattern A |
| solar_battery | 15 | 0 | 0 | All Patterns A-D, 100% AST coverage |
| CATF | ~25 | ~3 | ~2 | 3 undeclared intermediates → PARTIAL; 2 missing ASTs → PARTIAL or MANUAL |

### Validation

**Automated:**
- [ ] `uv run python scripts/spike_classify_compilability.py` → runs on all 4 suites
- [ ] Zero false positives (cross-reference check passes)
- [ ] chain_spike + sample_model + solar_battery: all `FULLY_COMPILABLE`
- [ ] CATF: PlasmaConfinement and TritiumBreedingRatio classified `PARTIALLY_COMPILABLE` or `MANUAL_REQUIRED`

**Manual:**
- [ ] Review CATF `MANUAL_REQUIRED` reasons -- verify they're accurate
- [ ] Review undeclared intermediate CalcDefs -- verify classification matches the finding from Phase 2
- [ ] Verify no `FULLY_COMPILABLE` CalcDef has any unresolvable refs or missing ASTs

**What We Know Works After This Phase:**
The classifier correctly partitions CalcDefs with zero false positives. Boundary rules produce expected results across all 4 model suites. The classifier's output directly feeds Item 3's `Compilability` enum design.

---

## Phase 5: Report

### Goal
Write the findings report with per-CalcDef results tables, operator mapping validation, undeclared intermediate recommendation, and go/no-go decision.

### Changes Required

**File:** `.project/active/expr-spike-compile/report.md` (NEW)

- [ ] Q3 Results: per-CalcDef per-output table (compiled expression, `ast.parse()` result, numerical match)
- [ ] Q3 Summary: syntactic validity rate, numerical accuracy rate
- [ ] Q4 Results: per-CalcDef classification table (verdict, reason, cross-reference)
- [ ] Q4 Summary: counts per verdict, false positive rate, false negative inventory
- [ ] Operator Mapping: validated table with all 5 operators + `^` and `[` entries
- [ ] `LiteralRational.value` type documentation
- [ ] Unary negation: encountered (yes/no) and recommendation for Item 3
- [ ] Undeclared intermediates: extended resolution results, data model recommendation for Item 3
- [ ] Ground truth comparison details: per-CalcDef comparison for the 5 implemented impls
- [ ] Limitations: only 5/15 solar_battery CalcDefs have numerical ground truth
- [ ] Go/no-go recommendation with evidence summary

### Validation

- [ ] Report contains quantitative evidence for every claim (spec requirement)
- [ ] All acceptance criteria from spec addressed
- [ ] Go/no-go decision references all 5 required conditions from spec

**What We Know Works After This Phase:**
Complete documented evidence for the Item 2 gate decision. Item 3 can proceed (or not) with clear data.

---

## Environment Setup

See CLAUDE.md for full environment rules. Scripts run via:
```bash
uv run python scripts/spike_compile_expressions.py [model_path ...]
uv run python scripts/spike_classify_compilability.py [model_path ...]
```

Handwritten impls at: `/home/reid/1cfe/fusion-tea/generated/solar_battery/handwritten/solarbatterylibrary/`

---

## Risk Management

| Risk | Phase | Mitigation |
|------|-------|------------|
| `LiteralRational.value` is a string, not float | Phase 1 | Document actual type; add `float(node.value)` conversion if needed |
| Multi-operand OperatorExpression (n-ary, not binary) | Phase 1 | Handle both: binary → `(left op right)`; n-ary → left-fold `((a op b) op c)`. Constraint_extractor already handles this pattern. |
| Handwritten impls use patterns that can't be exec'd standalone | Phase 3 | All 5 implemented impls inspected -- they use only `inputs.X` and local vars, no imports in body. If any fail, exclude and note in report. |
| Circular intermediate dependencies in CATF | Phase 2 | Topological sort detects cycles → mark as `MANUAL_REQUIRED`. Concept doc Edge Case 2 covers this. |
| Undeclared intermediates break the ExpressionAST data model | Phase 2 | Document finding; recommend approach (expand INTERMEDIATE_REF vs new node type) for Item 3. Don't block the spike on a data model decision. |
| Parenthesization of compiled expressions is wrong | Phase 1 | Over-parenthesize initially (`(left op right)` for every binary op). This is safe -- Python ignores redundant parens. Optimization can happen in Item 3. |

---

## Implementation Notes

### Phase 1 Completion
**Completed:** 2026-02-03
**Actual Changes:**
- Created `scripts/spike_compile_expressions.py` with `compile_expression()`, `PYTHON_OPERATOR_MAP`, `OutputCompileResult`, `CalcDefCompileResult` data classes
- Reused `load_and_extract()`, `sanitize_name()`, `DEFAULT_SUITES` from Item 1 scripts
- Implemented recursive AST-to-Python compiler dispatching on OperatorExpression, FeatureReferenceExpression, LiteralRational
- chain_spike: 3/3 PASS, solar_battery simple cases: all PASS

**Issues:** None
**Deviations:** None

### Phase 2 Completion
**Completed:** 2026-02-03
**Actual Changes:**
- Added `build_dependency_graph()`, `topological_sort()` (Kahn's algorithm), `compile_calc_def_body()`
- Extended resolution for undeclared intermediates via `get_all_member_names()` checking all owned_members
- All 15 solar_battery CalcDefs produce valid full function bodies
- PVModuleCostCalc execution order: material_cost → fab_cost → install_cost → total_cost → idiot_index (correct)
- AnnualizedFinancialCalc execution order: capital_recovery_factor → annualized_capital_cost (correct)

**Issues:** None
**Deviations:**
- Extended resolution for CATF undeclared intermediates succeeded for all 3 refs. Plan expected these might be PARTIALLY_COMPILABLE but they're FULLY_COMPILABLE. Better than expected.

### Phase 3 Completion
**Completed:** 2026-02-03
**Actual Changes:**
- Added `generate_test_inputs()`, `extract_handwritten_body()`, `compare_compiled_vs_handwritten()`
- Fixed handwritten body extraction to always wrap in function (handles `return` statements)
- All 5 implemented CalcDefs match at 0.00e+00 relative error
- 10 stub CalcDefs correctly identified and skipped

**Issues:**
- Initial attempt to `exec()` handwritten bodies failed because they contain `return` statements. Fixed by wrapping in `def _hw(inputs):` before execution.

**Deviations:** None

### Phase 4 Completion
**Completed:** 2026-02-03
**Actual Changes:**
- Created `scripts/spike_classify_compilability.py` with `classify_output()`, `classify_calc_def()`, `cross_reference_q3()`
- Imports Q3 functions directly (same PYTHONPATH)
- 42/44 FULLY_COMPILABLE, 2 PARTIALLY_COMPILABLE, 0 MANUAL_REQUIRED
- Zero false positives confirmed (44/44 cross-references pass)
- PlasmaConfinement and TritiumBreedingRatio correctly classified PARTIALLY_COMPILABLE

**Issues:** None
**Deviations:**
- CATF has 0 MANUAL_REQUIRED (plan expected ~2). Extended resolution handles all undeclared intermediates successfully.
- CATF has 2 PARTIALLY_COMPILABLE (plan expected ~3). Only PlasmaConfinement and TritiumBreedingRatio have missing ASTs.

### Phase 5 Completion
**Completed:** 2026-02-03
**Actual Changes:**
- Created `.project/active/expr-spike-compile/report.md` with full results tables, operator mapping, ground truth comparison, classifier results, go/no-go decision
- Report addresses all acceptance criteria from spec

**Issues:** None
**Deviations:** None

### Post-Completion: Audit Fixes
**Completed:** 2026-02-03
**Changes:**
1. **Issue 1 (Medium-High): Undeclared intermediates not emitted in function body.**
   - `build_dependency_graph()` now returns 3-tuple including `undeclared_intermediates` set
   - Added `get_member_expression()` for fetching expressions from any owned_member (not just outputs)
   - Graph expansion: undeclared intermediates are added as graph nodes, their expressions extracted and compiled, their deps recursively discovered
   - `compile_calc_def_body()` emits undeclared intermediates as local variable assignments; return statement only includes declared outputs
   - `classify_calc_def()` now validates that undeclared intermediates have compilable expressions
   - MagnetCryogenicLoad went from 1 output to 5 (1 declared + 4 undeclared), all compiled and emitted correctly

2. **Issue 2 (Medium): Cross-reference validates syntax only, not semantics.**
   - `run_suite()` now runs ground truth comparison for solar_battery and records `ground_truth_match` in Q3 results
   - `cross_reference_q3()` checks `ground_truth_match is False` as an additional false-positive condition
   - Output now reports "Semantic (ground truth match): 5" vs "Syntax-only (no ground truth): 37"

3. **Minor report corrections:**
   - PermittingCostCalc pattern label changed from B+D to D (pure literals + one input-only formula)
   - sample_model CalcDef count corrected: 5 CalcDefs not 7 (Item 1 conflated CalcDefs with outputs)
   - Added limitations section documenting Pattern B has zero runtime ground truth
   - Noted 37/42 FULLY_COMPILABLE are syntax-validated only
   - Updated undeclared intermediates section to document full code emission requirement for Item 3

---

**Status**: Complete
