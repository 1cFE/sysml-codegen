# Bug 11: Output Fields Have Incorrect Defaults

**Status**: FIXED (2026-02-20)
**Requirement**: REQ-OSR-05
**Discovered**: 2026-02-18 (C22 conformance testing)
**Tracking**: Hard assertion in `tests/conformance/test_gen_schemas.py::TestOutputFieldsHaveNoDefaults`

---

## 10. Fix Applied

**Date**: 2026-02-20

### Changes Made

1. **`src/sysml_codegen/generation/schemas.py:74`** — Changed `"default": out.default_value` to `"default": None` with REQ-OSR-05 comment. Output fields in MultiOutput schemas never carry defaults.

2. **`tests/conformance/test_gen_schemas.py:391-392`** — Expanded parametrization from `PARAMETRIZED_MODELS[:1]` (solar_battery only) to `PARAMETRIZED_MODELS` (solar_battery + catf_mfe).

3. **`tests/conformance/test_gen_schemas.py:433-439`** — Replaced `pytest.xfail(...)` soft marker with hard `assert not violations` assertion.

### Test Results

- **Full suite**: 1812 passed, 4 skipped, 5 xfailed (down from 6 xfailed)
- **Bug 11 test**: `test_output_fields_have_no_defaults[solar_battery]` PASSED, `test_output_fields_have_no_defaults[catf_mfe]` PASSED
- **No regressions**: Zero failures across unit, integration, and conformance tests

---

## 1. Problem Statement

Generated `MultiOutput` Pydantic schemas render `Field(default=0.0, ...)` on output
fields when the underlying SysML model has fixed bound values (`= 0.0`) on output
attributes. The extractor misclassifies these as "defaults," and the generation layer
passes them through unchecked. This violates REQ-OSR-05 and breaks TEAx pipeline wiring.

**Generated (buggy):**
```python
class PermittingCostCalcOutput(MultiOutput):
    material_cost: float = Field(default=0.0, description="material_cost output")  # BUG
    fab_cost: float = Field(default=0.0, description="fab_cost output")            # BUG
    install_cost: float = Field(default=0.0, description="install_cost output")    # BUG
    total_cost: float = Field(description="total_cost output")                     # OK
    idiot_index: float = Field(default=0.0, description="idiot_index output")      # BUG
```

**Expected (correct):**
```python
class PermittingCostCalcOutput(MultiOutput):
    material_cost: float = Field(description="material_cost output")
    fab_cost: float = Field(description="fab_cost output")
    install_cost: float = Field(description="install_cost output")
    total_cost: float = Field(description="total_cost output")
    idiot_index: float = Field(description="idiot_index output")
```

---

## 2. Why This Matters (TEAx Impact)

TEAx's `create_registry()` uses Pydantic field introspection:

- **No default** → field is a **required output** → registered as pipeline output channel
- **Has default** → field is **optional** → NOT registered as a pipeline output

When `Field(default=0.0)` appears on an output:
1. TEAx treats it as optional, not a required output
2. Field not registered as pipeline output channel
3. Downstream modules looking for that channel get `None`
4. Pipeline wiring fails **silently** (no error, just missing data)

---

## 3. Root Cause Analysis

### Data Flow Trace

```
SysML Model                      Extraction                    Resolution                      Generation
─────────────                    ──────────                    ──────────                      ──────────
out attribute                    AttributeInfo                 ModuleOutput                    Jinja2 Template
  material_cost : Real = 0.0  →   .default_value = "0.0"   →   .default_value = "0.0"    →   Field(default=0.0)
                                  ↑ MISCLASSIFIED                                              ↑ BUG: should be None
                                  (fixed binding, not default)
```

**Stage 1 — Extraction** (`extraction/extractor.py:374-395`):
`_extract_default_value()` is **semantically incorrect**. It has two code paths:

1. **Path 1** (lines 376-380): Checks `feature_value_expression` — if it's a literal,
   stores it as `default_value`. This fires for `out attribute material_cost : Real = 0.0`.
2. **Path 2** (lines 385-393): Checks `membership.is_default` — only stores values where
   `isDefault=true`. This is the correct path for actual SysML defaults.

Path 1 short-circuits before Path 2, so the extractor never checks whether the
FeatureValue is actually a default (`isDefault=true`) or a fixed binding
(`isDefault=false`). Per the SysML/KerML spec:

- `out attribute material_cost : Real = 0.0` → **fixed bound value** (`isDefault=false`)
  — a permanent equivalence constraint, NOT a default
- `in attribute cost_per_kw : Real default := 187.5` → **default initial value**
  (`isDefault=true`) — an overridable default

The extractor conflates these two distinct SysML concepts. Calling `= 0.0` a
"default_value" is a metadata misrepresentation, not just a rendering issue.

> **Upstream fix (not needed now, tracked as future work)**: Have the extractor check
> `is_default` on the FeatureValue before labeling something as `default_value`, or add
> a separate field like `bound_value` for fixed bindings. This matters for future
> consumers of `ModuleOutput.default_value` that might trust it as an actual SysML
> default, and for documentation generation that might say "default: 0.0" when the
> SysML model actually means "always exactly 0.0."

**Stage 2 — Resolution** (`resolution/graph_builder.py:1543`):
`_build_pipeline_module()` blindly copies `output_attr.default_value` to `ModuleOutput`:
```python
outputs.append(
    ModuleOutput(
        field_name=field_name,
        python_type="float",
        channel_name=channel_name,
        description=output_attr.description,
        default_value=output_attr.default_value,  # ← propagates "0.0"
        unit=output_attr.unit,
    )
)
```

This propagates the misclassified value. The resolution layer trusts extraction metadata.

**Stage 3 — Generation** (`generation/schemas.py:74`):
`generate_multioutput_model()` passes `default_value` directly to the template:
```python
field_data = {
    "name": out.field_name,
    "type": out.python_type,
    "description": _build_field_description(out),
    "default": out.default_value,  # ← THE BUG: should always be None for outputs
}
```

**Stage 4 — Template** (`templates/multioutput_model.py.jinja2:12-16`):
```jinja2
{% if field.default %}
    {{ field.name }}: {{ field.type }} = Field(default={{ field.default }}, ...)
{% else %}
    {{ field.name }}: {{ field.type }} = Field(description="{{ field.description }}")
{% endif %}
```

The template correctly branches on `field.default`. When given `None`, it renders without
default. The template is not the problem.

### Two Bugs, One Fix

There are actually two problems in the pipeline:

1. **Extraction bug** (semantic): `_extract_default_value()` misclassifies fixed bindings
   (`= 0.0`, `isDefault=false`) as defaults. The `default_value` field on output
   `AttributeInfo` objects doesn't represent a SysML default — it represents a fixed
   bound value.

2. **Generation bug** (rendering): `schemas.py` passes `default_value` through to the
   template for output fields without filtering. Even if `default_value` were semantically
   correct, output fields in Pydantic `MultiOutput` schemas must never have defaults
   (TEAx output detection).

The generation fix (section 5) addresses bug #2 and neutralizes the downstream effect of
bug #1. The extraction fix is tracked as future work — it requires SysIDE adapter changes
and a broader audit of all `default_value` consumers.

---

## 4. Blast Radius Assessment

### Affected Modules (Baseline Scan)

Scanned all 5 baseline computation graphs for multi-output modules with non-null
`default_value` on outputs:

| Model | Multi-Output Modules | Modules With Output Defaults |
|-------|---------------------|------------------------------|
| solar_battery | 11 | **1** (permitting__cost_model) |
| catf_mfe | 3 | 0 |
| chain_spike | 0 | 0 |
| attr_expr_probe | 1 | 0 |
| sample_model | 0 | 0 |
| **Total** | **15** | **1** |

**Only 1 module affected**: `solarbatterydesign__...permitting__cost_model`
with 4 output fields (`material_cost`, `fab_cost`, `install_cost`, `idiot_index`).

The 5th output (`total_cost`) has `default_value: null` because it's computed from
`system_capacity_kw * cost_per_kw`, not a literal.

### Why Only Permitting?

Other cost calc modules (PVModuleCostCalc, InverterCostCalc, etc.) share the same
CalcDef structure but their output attributes are computed expressions, not fixed
bindings to literals. PermittingCostCalc is unique: it has fixed bound values
`= 0.0` on outputs because permitting costs have no material/fab/install split —
those outputs are permanently zero by definition (equivalence constraints in SysML).
The extractor's Path 1 fires on these literals, misclassifying them as defaults.

### Consumers of `ModuleOutput.default_value`

Only ONE consumer in the generation layer:
- `generation/schemas.py:74` — the multioutput model generator

`entry_point.py` uses `default_value` on `ModuleInput` and `EntryPoint` objects,
NOT on `ModuleOutput`. No other generation code reads output defaults.

---

## 5. Fix Design

### Chosen Approach: Fix at Generation Layer (`schemas.py:74`)

**File**: `src/sysml_codegen/generation/schemas.py`
**Line**: 74

**Before:**
```python
field_data = {
    "name": out.field_name,
    "type": out.python_type,
    "description": _build_field_description(out),
    "default": out.default_value,
}
```

**After:**
```python
field_data = {
    "name": out.field_name,
    "type": out.python_type,
    "description": _build_field_description(out),
    "default": None,  # REQ-OSR-05: output fields must never have defaults
}
```

### Why This Location (Not Resolution Layer)

| Criterion | Generation Fix (schemas.py) | Resolution Fix (graph_builder.py) |
|-----------|---------------------------|----------------------------------|
| Lines changed | 1 | 1 |
| Baseline JSONs affected | 0 | 4 (computation graph JSONs) |
| Data fidelity | Preserves extraction data in ComputationGraph | Loses extraction data |
| Architectural fit | Generation decides rendering policy | Resolution is structural, not semantic |
| Future use | `default_value` available if extraction is later fixed | Data permanently discarded |

The generation layer is where the rendering rule "outputs don't have defaults" belongs.
Even though the resolution layer's `default_value` is currently misclassified (fixed
bindings labeled as defaults — see Stage 1 analysis), keeping it preserves the option
to fix the extraction layer upstream later without touching resolution or generation.

### Alternative Considered: Fix at Resolution Layer

**File**: `src/sysml_codegen/resolution/graph_builder.py:1543`

```python
# Would change to:
default_value=None,  # Strip output defaults at source
```

Rejected because:
- Changes 4 baseline computation graph JSONs (solar_battery, potentially others)
- Loses extraction data that would be needed if the upstream extraction bug is fixed
  (the field would need to be repurposed for actual `isDefault=true` values)
- Resolution layer's job is to structure data, not apply rendering policy

### Alternative Considered: Fix in Template

Adding output/input role awareness to the Jinja2 template was rejected as
over-engineering — the template should remain a simple renderer.

---

## 6. Test Changes

### 6a. Harden the xfail test → hard assertion

**File**: `tests/conformance/test_gen_schemas.py:433-439`

**Before** (soft xfail):
```python
if violations:
    pytest.xfail(
        "REQ-OSR-05 violation (Bug 11): output fields have defaults.\n"
        + "\n".join(violations)
    )
```

**After** (hard assertion):
```python
assert not violations, (
    "REQ-OSR-05 violation: output fields have defaults:\n"
    + "\n".join(violations)
)
```

This changes the test from "we know this is broken" to "this must not be broken".

### 6b. Extend model coverage

The current test is parametrized on `PARAMETRIZED_MODELS[:1]` (solar_battery only).
After the fix, extend to all models:

**Before:**
```python
@pytest.mark.parametrize("model_name", PARAMETRIZED_MODELS[:1],
                         ids=[MODEL_IDS[m] for m in PARAMETRIZED_MODELS[:1]])
```

**After:**
```python
@pytest.mark.parametrize("model_name", PARAMETRIZED_MODELS,
                         ids=[MODEL_IDS[m] for m in PARAMETRIZED_MODELS])
```

This ensures all 4 models are verified (solar_battery, catf_mfe, chain_spike,
attr_expr_probe), not just the one known to have the bug.

---

## 7. Casualty Analysis

### What Changes

| Item | Change | Risk |
|------|--------|------|
| `schemas.py:74` | `out.default_value` → `None` | None — only affects output field rendering |
| `test_gen_schemas.py:433-439` | `pytest.xfail(...)` → `assert not violations` | None — test becomes stricter |
| `test_gen_schemas.py:391` | `PARAMETRIZED_MODELS[:1]` → `PARAMETRIZED_MODELS` | Low — adds coverage for models with no multi-output modules (test skips cleanly via the `len(multi_output_modules) > 0` assert) |

### What Does NOT Change

| Item | Why Unchanged |
|------|---------------|
| `resolution/models.py` | `ModuleOutput.default_value` field preserved (extraction data) |
| `resolution/graph_builder.py:1543` | Still propagates extraction's `default_value` (misclassified but preserved for future upstream fix) |
| `templates/multioutput_model.py.jinja2` | Template logic unchanged — gets `None` so takes else branch |
| Computation graph baselines (4 JSONs) | Fix is in generation, not resolution |
| Pipeline YAML baselines | Schema generation doesn't affect YAML |
| Registry baselines | Schema generation doesn't affect registry |
| Entry point / input schema generation | Uses `ModuleInput.default_value`, not `ModuleOutput` |
| `entry_point.py` | Deals with inputs and entry points, not output schemas |
| All other conformance tests | No dependency on output default_value in schema rendering |
| xfail count | Drops from 6 to 5 (the 5 inherited-attr xfails from Deferred Issue #9 remain) |

### Regression Risk

**None identified.** The fix narrows output — removing a `default=` keyword from generated
code. No existing test depends on output fields HAVING defaults. The only test that
references this behavior is the Bug 11 xfail test itself.

The 1803 existing passing tests, 20 integration tests, and 16 E2E conformance tests are
unaffected because:
- No test asserts `default=` on output fields
- Schema identity tests (`test_pipeline_module_expansion.py`) test multi-output modules
  from solar_battery but check structure (class exists, fields present), not default values

---

## 8. Execution Plan

### Step 1: Fix `schemas.py` (1 line)

```
src/sysml_codegen/generation/schemas.py:74
  "default": out.default_value  →  "default": None
```

### Step 2: Harden test (3 lines changed)

```
tests/conformance/test_gen_schemas.py:391
  PARAMETRIZED_MODELS[:1]  →  PARAMETRIZED_MODELS
  (and matching ids= line)

tests/conformance/test_gen_schemas.py:433-439
  pytest.xfail(...)  →  assert not violations, (...)
```

### Step 3: Run test suite

```bash
uv run pytest tests/ -x
```

Expected: 1803+ passed, 5 xfailed (inherited attr only), 0 failed.
The Bug 11 xfail becomes a pass. Net xfail count drops from 6 to 5.

### Step 4: Verify generated output

```bash
uv run pytest tests/conformance/test_gen_schemas.py -v -k "output_fields"
```

Should show PASSED (not xfail).

---

## 9. Cross-References

| Document | Section | Relevance |
|----------|---------|-----------|
| `22-output-schema-rules.md` | "Bug 11: Confirmed REQ-OSR-05 Violation" (lines 154-169) | Design rule and root cause |
| `PHASE56_AUDIT_ACTIONS.md` | Amendment B1 | Bug discovery and deferral |
| `PHASE7_AUDIT_ACTIONS.md` | Section F4, Section G | Fix scheduling, xfail inventory |
| `IMPLEMENTATION_PLAN.md` | Line 1161 | Deferred issue tracking |
| `schema-generator/plan.md` | Lines 41, 137, 171, 243 | C22 conformance findings |

**Note**: "Deferred Issue #11" (endswith false positive in hierarchy_resolver) is a
SEPARATE issue from "Bug 11" (output field defaults). Deferred Issue #11 was already
fixed in commit `ef7abc9` (Phase 7.4).
