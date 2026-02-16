# Manual Test Plan: Pipeline Integration -- CalcDef Expression Compilation

**Created:** 2026-02-07
**Prerequisite:** All 131 automated tests pass (`uv run pytest tests/`)
**Branch:** cost-pattern

---

## Test Environment Setup

All tests use the **chain_spike_model** fixture at `tests/fixtures/chain_spike_model/`.

This model defines 3 CalcDefs in `library.sysml`, each with a single output whose expression is fully specified in SysML:

| CalcDef | Inputs | Output | Expression |
|---------|--------|--------|------------|
| `AreaCalc` | `length`, `width` | `area` | `length * width` |
| `CostCalc` | `area`, `rate` | `total_cost` | `area * rate` |
| `SummaryCalc` | `area`, `cost` | `cost_per_area` | `cost / area` |

The design file (`design.sysml`) wires them into a 3-module pipeline:

```
length=10.0 ──┐
               ├──> AreaCalc ──> area ──┬──> CostCalc ──> total_cost ──┐
width=5.0  ───┘                        │                               │
rate=12.0  ────────────────────────────┘    SummaryCalc <──────────────┘
                                              └──> cost_per_area
```

All 3 CalcDefs have `output_expression_asts` populated during extraction, so all 3 should be `FULLY_COMPILABLE` and receive auto-implemented `_impl.py` files.

---

## Test 1: Auto-Implementation File Generation

**Goal:** Verify codegen produces auto-implemented `_impl.py` files (not `NotImplementedError` stubs) for all 3 compilable CalcDefs.

### Steps

```bash
# Clean slate
rm -rf /tmp/manual-test-output

# Run codegen
uv run sysml-codegen generate \
  --models tests/fixtures/chain_spike_model \
  --output /tmp/manual-test-output \
  --package-name chain_spike \
  --verbose
```

### Expected Results

1. **Exit status**: Command exits successfully (exit code 0).

2. **Implementation files exist** -- run:
   ```bash
   find /tmp/manual-test-output/handwritten -name '*_impl.py' ! -name '__init__.py' | sort
   ```
   Expect 3 files (exact paths depend on ADR-003 namespace resolution; look for filenames containing `areacalc`, `costcalc`, `summarycalc`).

3. **Each file contains auto-impl code** -- for each `_impl.py`:
   ```bash
   grep -l 'AUTO_IMPLEMENTED = True' /tmp/manual-test-output/handwritten/**/*_impl.py
   ```
   All 3 files should match.

4. **No `NotImplementedError` in auto-impl files**:
   ```bash
   grep -rl 'NotImplementedError' /tmp/manual-test-output/handwritten/**/*_impl.py
   ```
   Should return **no results** (zero matches).

5. **Each file is syntactically valid Python**:
   ```bash
   for f in $(find /tmp/manual-test-output/handwritten -name '*_impl.py' ! -name '__init__.py'); do
     python -c "import ast; ast.parse(open('$f').read())" && echo "OK: $f" || echo "FAIL: $f"
   done
   ```
   All should print `OK`.

6. **Spot-check expressions** -- open the AreaCalc impl file and verify:
   - Module-level `AUTO_IMPLEMENTED = True`
   - A `def run_areacalc(inputs: AreaCalcInput) -> float:` function
   - A return expression referencing `inputs.length` and `inputs.width` with `*` operator
   - No undeclared intermediate local variables (AreaCalc has none)

---

## Test 2: Stub Files for Non-Compilable CalcDefs

**Goal:** Verify that CalcDefs without expression ASTs still produce `NotImplementedError` stubs.

### Setup: Create Synthetic Model

Create a temporary model that has one CalcDef **without** an output expression (output declared but no `=` assignment):

```bash
mkdir -p /tmp/manual-test-models
```

Write `/tmp/manual-test-models/library.sysml`:
```sysml
package MixedLibrary {
    private import ScalarValues::Real;

    // Compilable: has output expression
    calc def SimpleCalc {
        in attribute x : Real;
        out attribute y : Real = x * 2;
    }

    // Not compilable: output has no expression
    calc def ManualCalc {
        in attribute a : Real;
        in attribute b : Real;
        out attribute result : Real;
    }
}
```

Write `/tmp/manual-test-models/design.sysml`:
```sysml
package MixedDesign {
    private import ScalarValues::Real;
    private import MixedLibrary::*;

    part mixed_design {
        attribute x_val : Real = 5.0;
        attribute a_val : Real = 1.0;
        attribute b_val : Real = 2.0;

        calc simple : SimpleCalc {
            in x = x_val;
        }

        calc manual : ManualCalc {
            in a = a_val;
            in b = b_val;
        }
    }
}
```

### Steps

```bash
rm -rf /tmp/manual-test-mixed-output

uv run sysml-codegen generate \
  --models /tmp/manual-test-models \
  --output /tmp/manual-test-mixed-output \
  --package-name mixed_pkg \
  --verbose
```

### Expected Results

1. **SimpleCalc impl**: Has `AUTO_IMPLEMENTED = True`, contains `return` with expression, no `NotImplementedError`.
2. **ManualCalc impl**: Has `raise NotImplementedError(...)`, does NOT have `AUTO_IMPLEMENTED`.

```bash
# Auto-impl check
grep -l 'AUTO_IMPLEMENTED = True' /tmp/manual-test-mixed-output/handwritten/**/*_impl.py
# Should list SimpleCalc file only

# Stub check
grep -l 'NotImplementedError' /tmp/manual-test-mixed-output/handwritten/**/*_impl.py
# Should list ManualCalc file only
```

---

## Test 3: Backlog Report Excludes Auto-Implemented CalcDefs

**Goal:** The `IMPLEMENTATION_BACKLOG.md` should only list CalcDefs that require manual work.

### Steps

Use the output from **Test 1** (chain_spike_model):

```bash
cat /tmp/manual-test-output/IMPLEMENTATION_BACKLOG.md
```

### Expected Results

1. **Backlog contains "0 functions to implement"** (or the table is empty) because all 3 chain_spike CalcDefs are `FULLY_COMPILABLE`.

2. Use the output from **Test 2** (mixed model):
   ```bash
   cat /tmp/manual-test-mixed-output/IMPLEMENTATION_BACKLOG.md
   ```
   - Should list **1 function** to implement: `ManualCalc` / `run_manualcalc`.
   - Should NOT list `SimpleCalc`.

---

## Test 4: Preservation Lifecycle (Smart Regen)

**Goal:** Verify that hand-edited auto-impl files are preserved on regeneration when the SysML signature hasn't changed.

### Steps

```bash
# 1. Fresh generation
rm -rf /tmp/manual-test-preserve
uv run sysml-codegen generate \
  --models tests/fixtures/chain_spike_model \
  --output /tmp/manual-test-preserve \
  --package-name chain_spike \
  --verbose
```

```bash
# 2. Find the AreaCalc impl file
AREA_IMPL=$(find /tmp/manual-test-preserve/handwritten -name '*areacalc*_impl.py' | head -1)
echo "Found: $AREA_IMPL"

# 3. Record its content hash before editing
md5sum "$AREA_IMPL"
```

```bash
# 4. Simulate a hand-edit: add a comment at the top
sed -i '1s/^/# Hand-edited by engineer\n/' "$AREA_IMPL"
md5sum "$AREA_IMPL"
# Hash should be different from step 3
```

```bash
# 5. Re-run with --smart-regen (SysML unchanged)
uv run sysml-codegen generate \
  --models tests/fixtures/chain_spike_model \
  --output /tmp/manual-test-preserve \
  --package-name chain_spike \
  --smart-regen \
  --verbose
```

### Expected Results

1. **Log output** should say `Preserved` for the AreaCalc stencil (signature unchanged).
2. **File content preserved** -- the hand-edit comment is still present:
   ```bash
   head -1 "$AREA_IMPL"
   # Should print: # Hand-edited by engineer
   ```
3. **No backup created** for AreaCalc (signature didn't change, so no regeneration):
   ```bash
   ls /tmp/manual-test-preserve/handwritten/backup/ 2>/dev/null
   # Should be empty or not exist
   ```

---

## Test 5: Preservation with Signature Change (Backup + Regenerate)

**Goal:** Verify that when SysML changes the CalcDef signature, the old file is backed up and a new auto-impl is generated.

### Steps

```bash
# 1. Start from Test 4's output (has hand-edited file)
# Confirm the hand-edit is present
head -1 "$AREA_IMPL"
```

```bash
# 2. Create a modified model with an extra input on AreaCalc
cp -r tests/fixtures/chain_spike_model /tmp/chain_spike_modified

# Edit the library to add a third input to AreaCalc
```

Edit `/tmp/chain_spike_modified/library.sysml` to change AreaCalc:
```sysml
    calc def AreaCalc {
        in attribute length : Real;
        in attribute width : Real;
        in attribute scale : Real;       // NEW input

        out attribute area : Real = length * width * scale;
    }
```

Edit `/tmp/chain_spike_modified/design.sysml` to bind the new input:
```sysml
        attribute scale : Real = 1.0;    // NEW entry point (add after rate)

        calc area_calc : AreaCalc {
            in length = length;
            in width = width;
            in scale = scale;            // NEW binding
        }
```

```bash
# 3. Re-run with --smart-regen pointing to the MODIFIED model
#    but writing to the SAME output directory
uv run sysml-codegen generate \
  --models /tmp/chain_spike_modified \
  --output /tmp/manual-test-preserve \
  --package-name chain_spike \
  --smart-regen \
  --verbose
```

### Expected Results

1. **Log output** should say `Regenerated` for AreaCalc (signature changed: new input means different `AreaCalcInput`).
2. **Backup created**:
   ```bash
   ls /tmp/manual-test-preserve/handwritten/backup/
   # Should contain a timestamped backup of the old AreaCalc impl
   ```
3. **New file is auto-impl** (not the hand-edited version):
   ```bash
   head -1 "$AREA_IMPL"
   # Should NOT be "# Hand-edited by engineer"
   grep 'AUTO_IMPLEMENTED = True' "$AREA_IMPL"
   # Should match
   ```
4. **New expression references `scale`**:
   ```bash
   grep 'scale' "$AREA_IMPL"
   # Should find the new expression referencing inputs.scale
   ```

---

## Test 6: Verbose Logging of Step 6.5

**Goal:** Verify that expression compilation logging is visible with `--verbose`.

### Steps

```bash
uv run sysml-codegen generate \
  --models tests/fixtures/chain_spike_model \
  --output /tmp/manual-test-verbose \
  --package-name chain_spike \
  --verbose 2>&1 | grep -i -E 'compil|step 6|expression'
```

### Expected Results

Look for log lines indicating:
- The compilation step ran (mentions compilation, expression, or compilability)
- No `WARNING` about compilation failures (all 3 CalcDefs should compile cleanly)

---

## Test 7: Graceful Degradation on Compilation Error (M-1 Fix)

**Goal:** Verify that a CalcDef whose compilation raises an exception does not crash the pipeline.

This is primarily validated by the unit test suite, but can be verified indirectly: if a model contains a CalcDef with a malformed expression AST, the pipeline should log a warning and fall through to `UNKNOWN` compilability (stub template).

### Steps

Run codegen with `--verbose` on any model. Confirm:
1. No `ERROR`-level log messages about compilation
2. If a CalcDef fails compilation, it gets a `WARNING` log and a stub `_impl.py`

Since chain_spike has no malformed expressions, this test is a **negative confirmation** -- the absence of warnings means all compilations succeeded. For a positive test, you would need a model with an expression type not supported by the compiler (e.g., a `FeatureChainExpression` in an output). This is covered by unit tests (`test_edge5_feature_chain_returns_manual` in `test_expression_compiler.py`).

---

## Results Checklist

**Executed:** 2026-02-07 | **Prerequisite:** 131/131 automated tests pass | **Overall: 5/7 PASS**

| # | Test | Pass/Fail | Notes |
|---|------|-----------|-------|
| 1 | Auto-impl file generation (chain_spike) | **PASS** | 3 `_impl.py` files generated; all have `AUTO_IMPLEMENTED = True`; no `NotImplementedError`; all valid Python (`ast.parse` OK); AreaCalc spot-check: correct `run_areacalc(inputs: AreaCalcInput) -> float` signature, `return (inputs.length * inputs.width)` |
| 2 | Stub files for non-compilable CalcDefs | **PASS** | SimpleCalc: `AUTO_IMPLEMENTED = True`, `return (inputs.x * 2)`. ManualCalc: `raise NotImplementedError(...)`, no `AUTO_IMPLEMENTED`. No cross-contamination. |
| 3 | Backlog report excludes FULLY_COMPILABLE | **PASS** | chain_spike: "0 functions to implement", empty table. Mixed model: "1 functions to implement", lists ManualCalc only. SimpleCalc correctly excluded. |
| 4 | Preservation: hand-edit preserved (same signature) | **PASS** | All 3 stencils logged `Preserved stencil (Signature unchanged)`. `Stencils - New: 0, Preserved: 3, Regenerated: 0`. Hand-edit comment `# Hand-edited by engineer` retained at line 1. No `backup/` directory created. |
| 5 | Preservation: backup + regen (changed signature) | **FAIL** | **BUG:** `FunctionSignature.matches()` only compares input type *name* (`AreaCalcInput`), not actual *fields*. Adding `scale` input doesn't change the type name, so stencil is incorrectly preserved. Module wrapper was correctly regenerated with `scale`, but impl file still has old 2-input expression. `input_fields` data is extracted by `generate_expected_signature()` but never compared. See `signature_extractor.py`. |
| 6 | Verbose logging of Step 6.5 | **FAIL** | **GAP:** No logging on success path in `initialization.py` Step 6.5 (line ~168). Only the `except` branch has `logger.warning()`. Zero output about compilation when all CalcDefs compile cleanly. Missing: step start, per-CalcDef results, compilability classification. |
| 7 | Graceful degradation on compilation error | **PASS** | No `ERROR` or `WARNING` messages in clean run. Unit test `test_edge5_feature_chain_returns_manual` confirms graceful fallback to `MANUAL_REQUIRED` for unsupported expression types (FeatureChainExpression). |
