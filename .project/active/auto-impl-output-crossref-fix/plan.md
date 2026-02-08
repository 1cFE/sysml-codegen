# Design & Implementation Plan: Auto-Impl Multi-Output Cross-Reference Fix

**Status:** Draft
**Created:** 2026-02-08
**Last Updated:** 2026-02-08

## Source Documents

- **Spec:** `.project/active/auto-impl-output-crossref-fix/spec.md`
- **Epic:** `.project/backlog/epic_expression_aware_codegen.md` (Item 4.1)
- **E2E Report:** `.project/active/expr-e2e-validation/report.md`

---

## Design

### Root Cause

`_build_auto_impl_context()` (stencils.py:149-200) partitions compilation results into two buckets using a single criterion — `is_undeclared_intermediate`:

1. `execution_steps`: undeclared intermediates → local variable assignments
2. `output_expressions`: declared outputs → inlined in return tuple

This is incorrect when declared output B's `python_expression` references declared output A by name (e.g., `(1.0 / q_eng)`). Output A is inlined, never assigned as a local variable, so B gets `NameError`.

### Why `intermediate_refs` Is the Right Detection Mechanism

`CompilationResult` already carries `intermediate_refs: list[str]` — populated by `_collect_refs()` during AST compilation. When a declared output references another declared output, the referenced name appears in `intermediate_refs` (because same-CalcDef members are classified as `INTERMEDIATE_REF` during AST building). No string parsing or AST re-analysis needed.

Confirmed by real data:
- EngineeringQFactor: `f_recirculating.intermediate_refs = ["q_eng"]`, `p_net.intermediate_refs = ["f_recirculating"]`
- AnnualizedFinancialCalc: `annualized_capital_cost.intermediate_refs = ["capital_recovery_factor"]`

### Proposed Change to `_build_auto_impl_context()`

```
Current logic:
  for name in execution_order:
    if is_undeclared_intermediate → execution_steps
  for name in output_attr_order:
    if declared output → output_expressions (inlined in return)

Proposed logic:
  1. Compute output_attr_set = set of declared output names
  2. Detect has_output_crossrefs:
       any declared output's intermediate_refs ∩ output_attr_set is non-empty
  3. If has_output_crossrefs:
       - execution_steps: ALL entries in execution_order (undeclared + declared)
       - output_expressions: declared output names only (expression = name)
     If not:
       - Current behavior (undeclared as steps, declared inlined)
```

When cross-refs exist, ALL declared outputs become local variable assignments in topological order. The return tuple references names only. This is simpler and safer than selectively promoting only referenced outputs — it avoids missed transitive dependencies and produces cleaner generated code.

### Template Change

The Jinja2 template (`auto_implementation.py.jinja2`) needs a minor adjustment. When outputs are assigned as local vars, the return tuple comment `# {{ output.name }}` is redundant (expression IS the name). Add a conditional to suppress it:

```jinja2
{% for output in output_expressions %}
{% if output.expression == output.name %}
        {{ output.expression }},
{% else %}
        {{ output.expression }},  # {{ output.name }}
{% endif %}
{% endfor %}
```

### What Does NOT Change

- Expression compiler (`expression_compiler.py`) — compilation results are correct
- Extraction, analysis, resolution layers — no changes
- Single-output path — `output_count == 1` branch untouched
- Multi-output NO-cross-ref path — detected as `has_output_crossrefs = False`, current behavior preserved
- Undeclared intermediate handling — still emitted as execution_steps (now alongside promoted declared outputs when cross-refs exist)

### Generated Code Examples

**Case: Full cascade (EngineeringQFactor)**

Before (buggy):
```python
return (
    (inputs.p_electric_gross / inputs.p_auxiliary_total),  # q_eng
    (1.0 / q_eng),  # f_recirculating        ← NameError
    (inputs.p_electric_gross * (1.0 - f_recirculating)),  # p_net  ← NameError
)
```

After (fixed):
```python
q_eng = (inputs.p_electric_gross / inputs.p_auxiliary_total)
f_recirculating = (1.0 / q_eng)
p_net = (inputs.p_electric_gross * (1.0 - f_recirculating))
return (
    q_eng,
    f_recirculating,
    p_net,
)
```

**Case: Undeclared intermediates + declared cross-refs**

```python
temp = (inputs.x + 1)           # undeclared intermediate (already worked)
out_a = (temp * 2)              # declared output (now promoted to local var)
out_b = (out_a + 1)             # declared output (refs out_a)
return (
    out_a,
    out_b,
)
```

**Case: Multi-output, NO cross-refs (unchanged)**

```python
return (
    (inputs.x * 2),  # out0
    (inputs.y + 1),  # out1
)
```

---

## Synthetic Test Data Inventory

Six synthetic `CalcDefCompilationResult` fixtures covering all edge cases. Each is constructed from `CompilationResult` objects with explicit `intermediate_refs` — no SysIDE dependency.

### Test 1: Full cascade (3 declared outputs, A→B→C)

Mirrors EngineeringQFactor. Every output except the first references a predecessor.

```
CalcDef: "CascadeCalc", inputs: [a, b], outputs: [x, y, z]
  x: expression="(inputs.a + inputs.b)",   intermediate_refs=[]
  y: expression="(x * 2)",                 intermediate_refs=["x"]
  z: expression="(y - inputs.a)",           intermediate_refs=["y"]
  execution_order: ["x", "y", "z"]

Expected generated code:
  x = (inputs.a + inputs.b)
  y = (x * 2)
  z = (y - inputs.a)
  return (x, y, z)
```

### Test 2: Partial cascade (3 outputs, only B refs A; C is independent)

Tests that when ANY cross-ref exists, ALL outputs become local vars.

```
CalcDef: "PartialCascadeCalc", inputs: [a, b], outputs: [x, y, z]
  x: expression="(inputs.a * 2)",           intermediate_refs=[]
  y: expression="(x + inputs.b)",           intermediate_refs=["x"]
  z: expression="(inputs.b * 3)",           intermediate_refs=[]
  execution_order: ["x", "y", "z"]

Expected generated code:
  x = (inputs.a * 2)
  y = (x + inputs.b)
  z = (inputs.b * 3)
  return (x, y, z)
```

### Test 3: Multi-output, NO cross-refs (regression guard)

Two independent outputs. Must preserve current inline behavior.

```
CalcDef: "IndependentCalc", inputs: [a, b], outputs: [p, q]
  p: expression="(inputs.a * 2)",  intermediate_refs=[]
  q: expression="(inputs.b + 1)",  intermediate_refs=[]
  execution_order: ["p", "q"]

Expected generated code:
  return (
      (inputs.a * 2),  # p
      (inputs.b + 1),  # q
  )
```

### Test 4: Single output (regression guard)

Must use inline return, not local var assignment.

```
CalcDef: "SimpleCalc", inputs: [x], outputs: [result]
  result: expression="(inputs.x * 2)", intermediate_refs=[]
  execution_order: ["result"]

Expected generated code:
  return (inputs.x * 2)
```

(This already exists as `test_auto_impl_contains_return_expression` but we include it in the new test class for completeness of the matrix.)

### Test 5: Undeclared intermediates + declared cross-refs (mixed)

Both patterns coexist. Undeclared `temp` feeds declared `out_a`, which feeds declared `out_b`.

```
CalcDef: "MixedCalc", inputs: [x], outputs: [out_a, out_b]
  temp:  expression="(inputs.x + 1)",  intermediate_refs=[],     is_undeclared=True
  out_a: expression="(temp * 2)",      intermediate_refs=["temp"], is_undeclared=False
  out_b: expression="(out_a + 3)",     intermediate_refs=["out_a"], is_undeclared=False
  execution_order: ["temp", "out_a", "out_b"]

Expected generated code:
  temp = (inputs.x + 1)
  out_a = (temp * 2)
  out_b = (out_a + 3)
  return (
      out_a,
      out_b,
  )
```

### Test 6: Diamond pattern (4 declared outputs, shared dependency)

out_a is standalone. out_b and out_c both reference out_a. out_d references both out_b and out_c.

```
CalcDef: "DiamondCalc", inputs: [x], outputs: [a, b, c, d]
  a: expression="(inputs.x * 2)",     intermediate_refs=[]
  b: expression="(a + 1)",            intermediate_refs=["a"]
  c: expression="(a - 1)",            intermediate_refs=["a"]
  d: expression="(b * c)",            intermediate_refs=["b", "c"]
  execution_order: ["a", "b", "c", "d"]

Expected generated code:
  a = (inputs.x * 2)
  b = (a + 1)
  c = (a - 1)
  d = (b * c)
  return (a, b, c, d)
```

### Validation Matrix

| Test | Outputs | Cross-refs? | Undeclared? | Tests requirement |
|------|---------|-------------|-------------|-------------------|
| 1. Full cascade | 3 | Yes (chain) | No | FR-1, FR-2 |
| 2. Partial cascade | 3 | Yes (partial) | No | FR-1, FR-2 |
| 3. Independent | 2 | No | No | Regression (current behavior) |
| 4. Single output | 1 | No | No | FR-3 regression |
| 5. Mixed | 2 + 1 undeclared | Yes | Yes | FR-1, FR-4 |
| 6. Diamond | 4 | Yes (diamond) | No | FR-1, FR-2 (non-linear DAG) |

---

## Implementation Strategy

**Phasing Rationale:** Test-first with synthetic data catches edge cases before touching production code. The fix itself is a single function + template change, but the edge case matrix is non-trivial. Phase 3 validates on real models.

**Overall Validation Approach:**
- Phase 1: synthetic unit tests define correctness (expect failures)
- Phase 2: fix makes all tests pass
- Phase 3: real-model E2E tests confirm end-to-end correctness

---

## Phase 1: Write Synthetic Unit Tests (Test-First)

### Goal

Create 6 unit tests in `test_stencils.py` covering the full edge case matrix. Tests 1, 2, 5, 6 will FAIL (they exercise the bug). Tests 3, 4 will PASS (regression guards). This establishes ground truth before any production code changes.

### Test Stencil

```python
class TestAutoImplOutputCrossRefs:
    """Tests for multi-output CalcDefs with declared output cross-references.

    Covers Item 4.1 fix: declared outputs that reference other declared outputs
    must be emitted as local variable assignments, not inlined in return tuple.
    """

    def test_full_cascade_3_outputs(self):
        """A→B→C: all outputs in a dependency chain become local vars."""
        env = _get_template_env()
        calc_def = _make_calc_def(name="CascadeCalc", qualified_name="CascadeCalc",
                                  num_inputs=2, num_outputs=3)
        result = CalcDefCompilationResult(
            calc_def_name="CascadeCalc",
            overall_compilability=Compilability.FULLY_COMPILABLE,
            output_results=[
                CompilationResult(output_name="out0", compilability=Compilability.FULLY_COMPILABLE,
                                  python_expression="(inputs.x0 + inputs.x1)", input_refs=["x0", "x1"]),
                CompilationResult(output_name="out1", compilability=Compilability.FULLY_COMPILABLE,
                                  python_expression="(out0 * 2)", intermediate_refs=["out0"]),
                CompilationResult(output_name="out2", compilability=Compilability.FULLY_COMPILABLE,
                                  python_expression="(out1 - inputs.x0)", input_refs=["x0"],
                                  intermediate_refs=["out1"]),
            ],
            execution_order=["out0", "out1", "out2"],
        )
        code = generate_implementation(calc_def, env, Path("out.py"), "test_pkg",
                                       compilation_result=result)
        ast.parse(code)  # Must be syntactically valid
        assert "out0 = (inputs.x0 + inputs.x1)" in code
        assert "out1 = (out0 * 2)" in code
        assert "out2 = (out1 - inputs.x0)" in code
        assert "return (" in code
        # Return tuple uses names, not inlined expressions
        assert "(inputs.x0 + inputs.x1)," not in code
```

### Changes Required

#### 1. Test File
**File:** `tests/unit/test_stencils.py` (MODIFY — append new test class)
- [ ] Add `TestAutoImplOutputCrossRefs` class with 6 test methods
- [ ] Each test constructs synthetic `CalcDefCompilationResult` per inventory above
- [ ] Each test asserts `ast.parse(code)` (syntactic validity)
- [ ] Each test asserts specific local var assignments present/absent
- [ ] Each test asserts return tuple structure (names vs inlined expressions)

### Validation

**Automated:**
- [ ] `uv run pytest tests/unit/test_stencils.py::TestAutoImplOutputCrossRefs -v`
  - Tests 1, 2, 5, 6: FAIL (expected — bug not yet fixed)
  - Tests 3, 4: PASS (regression — current behavior is correct for these)
- [ ] `uv run pytest tests/unit/test_stencils.py -v` — all pre-existing tests still pass

**What We Know Works After This Phase:**
Test matrix is executable. Regression guards confirm non-cross-ref paths are stable. Failures precisely match the bug.

---

## Phase 2: Fix `_build_auto_impl_context()` + Template

### Goal

Modify the production code to detect declared output cross-references and emit those outputs as local variable assignments. All 6 new tests pass. All pre-existing tests pass.

### Changes Required

#### 1. `_build_auto_impl_context()` in stencils.py
**File:** `src/sysml_codegen/generation/stencils.py:149-200` (MODIFY)

- [ ] After line 169 (`result_map = ...`), compute `output_attr_set = set(output_attr_order)`
- [ ] Detect cross-references:
  ```python
  has_output_crossrefs = any(
      set(result_map[name].intermediate_refs) & output_attr_set
      for name in output_attr_order
      if name in result_map and result_map[name].intermediate_refs
  )
  ```
- [ ] When `has_output_crossrefs is True`:
  - Build `execution_steps` from ALL entries in `execution_order` (both undeclared intermediates AND declared outputs), preserving topological order
  - Build `output_expressions` with `expression = name` (not the python_expression) for each declared output in `output_attr_order`
- [ ] When `has_output_crossrefs is False`:
  - Keep existing logic unchanged (undeclared as steps, declared inlined in return)
- [ ] Single-output path (`output_count == 1`) is unaffected — `has_output_crossrefs` is only meaningful for multi-output

**Key ordering detail:** `execution_order` is topological (set by compiler). Declared outputs in `execution_steps` MUST follow this order, not `output_attr_order`. The return tuple uses `output_attr_order` (declaration order from SysML) to preserve the CalcDef's declared output contract.

#### 2. Jinja2 Template
**File:** `src/sysml_codegen/templates/auto_implementation.py.jinja2:28-30` (MODIFY)

- [ ] In the multi-output return tuple loop, suppress redundant `# name` comment when expression equals name:
  ```jinja2
  {% for output in output_expressions %}
  {% if output.expression == output.name %}
          {{ output.expression }},
  {% else %}
          {{ output.expression }},  # {{ output.name }}
  {% endif %}
  {% endfor %}
  ```

### Validation

**Automated:**
- [ ] `uv run pytest tests/unit/test_stencils.py -v` — ALL tests pass (new + pre-existing)
- [ ] `uv run pytest tests/unit/ -v` — full unit suite, no regressions
- [ ] `uv run mypy src/sysml_codegen/generation/stencils.py` — type check passes
- [ ] `uv run ruff check src/sysml_codegen/generation/stencils.py` — lint passes

**Manual:**
- [ ] Inspect generated code for Test 1 (full cascade) — verify local vars in topo order, return uses names
- [ ] Inspect generated code for Test 3 (no cross-refs) — verify return still inlines expressions
- [ ] Inspect generated code for Test 5 (mixed) — verify undeclared intermediate BEFORE declared outputs

**What We Know Works After This Phase:**
All synthetic corner cases produce syntactically valid, semantically correct Python. No regressions in any unit test.

---

## Phase 3: E2E Validation on Real Models

### Goal

Remove 2 `xfail` markers from E2E tests. Verify EngineeringQFactor and AnnualizedFinancialCalc execute correctly with expected numerical results. Full test suite green with 0 xfail.

### Changes Required

#### 1. E2E Test File
**File:** `tests/integration/test_expression_compilation_e2e.py` (MODIFY)

- [ ] Remove `xfail` marker from AnnualizedFinancialCalc test (lines 49-53): remove `marks=pytest.mark.xfail(...)` wrapper, convert `pytest.param(...)` back to plain tuple
- [ ] Remove `xfail` marker from `test_pattern_b_engineering_q_factor` (lines 274-279): remove `@pytest.mark.xfail(...)` decorator

### Validation

**Automated:**
- [ ] `uv run pytest tests/integration/test_expression_compilation_e2e.py -v` — all 17 tests PASS, 0 xfail
- [ ] `uv run pytest tests/ -v` — full suite (161+ tests), 0 failures, 0 xfail
- [ ] `uv run mypy src/sysml_codegen/generation/stencils.py`
- [ ] `uv run ruff check src/sysml_codegen/generation/`

**Manual:**
- [ ] Verify EngineeringQFactor produces: q_eng=7.5, f_recirculating=0.1333..., p_net=1300.0
- [ ] Verify AnnualizedFinancialCalc produces correct capital_recovery_factor and annualized_capital_cost
- [ ] Verify MagnetCryogenicLoad still passes (cooling_power=3375.0)

**What We Know Works After This Phase:**
Real-world CalcDefs with multi-output cross-references produce correct, executable auto-implementations. Epic 1 is fully closed. Zero xfail tests. Ready for Epic 2.

---

## Risk Management

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| `intermediate_refs` doesn't contain declared output names for cross-ref case | LOW | HIGH | Phase 1 tests mirror real data shapes. If detection fails, tests 1/2/5/6 won't assert correctly even before the fix. Would surface immediately. |
| Template change affects single-output path | LOW | MEDIUM | Test 4 is explicit regression guard. Single-output uses `output_count == 1` branch which bypasses the multi-output loop entirely. |
| Topological vs declaration order mismatch | MEDIUM | HIGH | Test 1 (cascade) and Test 6 (diamond) have specific ordering requirements. Assertions check assignment order, not just presence. |
| Existing `test_auto_impl_multi_output` breaks | LOW | LOW | This test has independent outputs (no cross-refs). `has_output_crossrefs` will be False, preserving inline behavior. Test 3 doubles as a guard. |
| E2E tests pass in unit but fail on real models due to expression content differences | LOW | MEDIUM | Phase 3 runs real codegen pipeline. If expressions differ from synthetic tests, we'll see it in the numerical comparison. |

---

## Implementation Notes

*TO BE FILLED DURING IMPLEMENTATION*

### Phase 1 Completion
**Completed:** 2026-02-08
**Actual Changes:**
- Added `TestAutoImplOutputCrossRefs` class with 6 test methods to `tests/unit/test_stencils.py`
- Tests 3, 4 passed (regression guards); tests 1, 2, 5, 6 failed (exercised the bug) — exactly as predicted
- Fixed regression guard assertions to use `"out0 = ("` pattern instead of `"out0 = "` to avoid false matches against docstring example lines

**Issues:** None
**Deviations:** Minor assertion pattern change (`" = ("` instead of `" = "`) to avoid docstring example false positives — no impact on test coverage.

### Phase 2 Completion
**Completed:** 2026-02-08
**Actual Changes:**
- Modified `_build_auto_impl_context()` in `src/sysml_codegen/generation/stencils.py:149-210` to detect `has_output_crossrefs` via `intermediate_refs ∩ output_attr_set`, emit all outputs as local vars when cross-refs exist
- Modified `src/sysml_codegen/templates/auto_implementation.py.jinja2:28-34` to suppress redundant `# name` comment when `output.expression == output.name`
- All 16 stencil tests pass, 130 unit tests pass, mypy clean on stencils.py, ruff clean

**Issues:** None
**Deviations:** None — implementation exactly matches the plan.

### Phase 3 Completion
**Completed:** 2026-02-08
**Actual Changes:**
- Removed `pytest.param(..., marks=pytest.mark.xfail(...))` wrapper from AnnualizedFinancialCalc in `tests/integration/test_expression_compilation_e2e.py:45-54`, converted back to plain tuple
- Removed `@pytest.mark.xfail(...)` decorator from `test_pattern_b_engineering_q_factor` in same file (lines 274-279)
- All 17 E2E tests pass, all 167 tests pass with 0 xfail, 0 failures

**Issues:** None
**Deviations:** None

---

**Status**: ~~Draft~~ → ~~In Progress~~ → **Complete**
