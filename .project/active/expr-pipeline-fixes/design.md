# Design: Pipeline Integration Fixes -- Smart-Regen Field Comparison & Step 6.5 Logging

**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-02-07
**Complexity:** LOW
**Branch:** cost-pattern
**Epic:** EXPR-CODEGEN Item 4 (follow-up)

---

## Overview

Two targeted fixes: (1) enhance `FunctionSignature.matches()` to compare input field names so that adding/removing/renaming a CalcDef input triggers stencil regeneration, and (2) add INFO-level logging to the Step 6.5 expression compilation loop so verbose output shows compilation activity.

## Related Artifacts

- **Spec:** `.project/active/expr-pipeline-fixes/spec.md`
- **Parent spec:** `.project/active/expr-pipeline-integration/spec.md`
- **Manual test plan:** `.project/active/expr-pipeline-integration/manual-test-plan.md` (Tests 5 & 6)
- **Signature extractor:** `src/sysml_codegen/analysis/signature_extractor.py`
- **Preservation logic:** `src/sysml_codegen/generation/preservation.py`
- **Pipeline init:** `src/sysml_codegen/generation/initialization.py`

---

## Research Findings

### Signature Comparison (Bug)

**Current state of `FunctionSignature`** (`analysis/signature_extractor.py:17-51`):
- Dataclass has four fields: `function_name`, `input_type`, `return_type`, `input_fields`
- `input_fields: list[str] | None = None` -- the field already exists but is **unused in comparison**
- `matches()` (line 35) only compares the first three fields
- `generate_expected_signature()` (line 158) already populates `input_fields` from `calc_def.input_attributes`
- `extract_signature_from_impl()` (line 111) never populates `input_fields` -- it stays `None`

**How stencils expose input fields** (from template analysis):
- Both `implementation_stencil.py.jinja2` and `auto_implementation.py.jinja2` generate code with `from {pkg}.modules.{path} import {InputClassName}`
- The stub template shows `inputs.{param.name}` access patterns in the docstring
- The auto-impl template uses `inputs.{field}` in compiled expressions
- **Neither template embeds a machine-parseable list of input field names** in the impl file itself

**Key insight**: The generated module wrapper (in `modules/`) contains the `Input` Pydantic class with all fields declared. However, parsing the module wrapper to extract fields would be complex and fragile. A simpler approach exists: **parse the impl file's AST to find `inputs.X` attribute access patterns**, which directly reveals what fields the existing implementation references.

**Even simpler approach**: Since `generate_expected_signature()` already populates `input_fields`, the only missing piece is populating `input_fields` on the extracted side. The most robust approach:
1. **Extract from the impl file AST**: Walk the `run_*` function body for `inputs.X` patterns
2. **Compare sorted field lists** in `matches()`
3. **Graceful fallback**: If extracted `input_fields` is `None` (legacy/unparseable), skip field comparison (FR-3)

### Step 6.5 Logging (Gap)

**Current state** (`generation/initialization.py:168-186`):
- The loop iterates `calc_defs` and compiles those with `output_expression_asts`
- Only logging is `logger.warning()` in the `except` branch (line 181)
- Zero log output on the success path

**Logging patterns in codebase**:
- All modules use `logger = logging.getLogger(__name__)`
- `logger.info()` for completions/summaries (e.g., `parameter_groups.py` pattern: `"Derived {N} groups: {breakdown}"`)
- `logger.debug()` for per-item details
- `logger.warning()` for recoverable issues with fallback behavior

**CalcDefCompilationResult fields** (`extraction/expression_compiler.py:132-143`):
- `calc_def_name: str`
- `overall_compilability: Compilability` -- enum: `FULLY_COMPILABLE`, `PARTIALLY_COMPILABLE`, `MANUAL_REQUIRED`, `UNKNOWN`
- `output_results: list[CompilationResult]`
- `execution_order: list[str]`

The compilability enum provides the classification needed for per-CalcDef and summary logging.

### Existing Test Coverage

- No dedicated test file for `signature_extractor.py`
- `test_stencils.py` has a signature-related test (`test_auto_impl_same_function_signature_as_stub`) but tests template output, not `matches()`
- New unit tests needed for field-level comparison (spec AC: "New unit tests cover field-level signature comparison")

---

## Proposed Design

### Fix 1: Field-Aware Signature Comparison

**Files modified:** `src/sysml_codegen/analysis/signature_extractor.py`

#### 1a. Enhance `FunctionSignatureVisitor` to extract input fields

In `FunctionSignatureVisitor.visit_FunctionDef()` (line 65), after extracting the basic signature, walk the function body to collect `inputs.X` attribute accesses:

```python
# In visit_FunctionDef, after creating self.signature:
input_fields = self._extract_input_field_refs(node)
if input_fields:
    self.signature.input_fields = sorted(input_fields)
```

New method `_extract_input_field_refs(self, func_node)`:
- Walk all nodes in the function body
- Find `ast.Attribute` nodes where `value` is `ast.Name(id='inputs')`
- Collect the `attr` names into a set
- Return sorted list (deterministic comparison)

This handles both stub templates (docstring patterns like `inputs.x = ...`) and auto-impl templates (expression patterns like `inputs.x + inputs.y`). The docstring patterns appear as string literals, not AST attribute accesses, so only actual code references are captured -- which is exactly what matters for detecting whether the impl uses the right fields.

**Important nuance**: Stub templates put `inputs.X` in the docstring (string literal), not in executable code. The `raise NotImplementedError(...)` is the only statement. So for unmodified stubs, the AST walk would find **zero** `inputs.X` references in executable code. This means `input_fields` would be `[]` (empty list) for untouched stubs.

**Resolution**: This is actually fine. If a stub has never been edited by a human, regenerating it is harmless (it's still just a stub). The important case is when a human has written real implementation code that references `inputs.X` -- in that case, the AST walk correctly captures the fields they're using. For the empty-list case, we treat it like `None` -- skip field comparison. Updated logic:

```python
input_fields = self._extract_input_field_refs(node)
if input_fields:  # Only set if non-empty (actual field references found)
    self.signature.input_fields = sorted(input_fields)
# else: leave as None (unmodified stub or no detectable field refs)
```

#### 1b. Enhance `matches()` to compare input fields

Update `FunctionSignature.matches()` (line 35) to include field comparison after the existing checks:

```python
def matches(self, other: "FunctionSignature") -> bool:
    # Existing checks (function name, input type, return type)
    if not (
        self.function_name == other.function_name
        and self.input_type == other.input_type
        and self.return_type == other.return_type
    ):
        return False

    # Field-level comparison (FR-1, FR-2)
    # If either side has no field info, fall back to type-name match (FR-3)
    if self.input_fields is not None and other.input_fields is not None:
        return sorted(self.input_fields) == sorted(other.input_fields)

    # Graceful fallback: no field info available on one/both sides
    return True
```

**Design rationale:**
- `sorted()` on both sides ensures field ordering doesn't cause false mismatches (spec edge case: "Field ordering")
- `None` on either side triggers fallback to current behavior (FR-3: backwards compatibility)
- `generate_expected_signature()` already populates `input_fields`, so the "expected" side always has field info
- The "extracted" side has field info only when the impl file contains `inputs.X` references in code (human-edited impls)

#### 1c. No changes to `preservation.py`

The spec explicitly states: "Changes to `preservation.py` flow ... is correct; only its `matches()` input is incomplete." The `should_regenerate_stencil` function calls `existing_sig.matches(expected_sig)` -- once `matches()` and `extract_signature_from_impl()` are fixed, preservation works correctly with no further changes.

### Fix 2: Step 6.5 Logging

**File modified:** `src/sysml_codegen/generation/initialization.py`

Add three logging points to the Step 6.5 block (lines 168-186):

#### 2a. Start message (FR-4)

Before the loop:
```python
logger.info("Step 6.5: Compiling expressions for %d calculation definitions", len(calc_defs))
```

#### 2b. Per-CalcDef message (FR-5)

After successful compilation (inside the `try`, after `compilation_results[calc_def.name] = result_comp`):
```python
logger.info(
    "  Compiled '%s': %s",
    calc_def.name,
    result_comp.overall_compilability.value,
)
```

Also add a log line for CalcDefs skipped (no expression ASTs):
```python
# In the else branch (when not calc_def.output_expression_asts)
# No explicit log needed -- these are CalcDefs without expressions, which is the normal
# case for CalcDefs that don't have SysML expression bodies. They stay UNKNOWN.
```

Actually, reviewing the loop: it only processes `calc_defs` that have `output_expression_asts`. CalcDefs without ASTs are silently skipped. For completeness of the summary (FR-6), we should count them.

#### 2c. Summary message (FR-6)

After the loop, emit a summary:
```python
# Count by compilability
compilability_counts: dict[str, int] = {}
for result in compilation_results.values():
    key = result.overall_compilability.value
    compilability_counts[key] = compilability_counts.get(key, 0) + 1

skipped = len(calc_defs) - len(compilation_results)
breakdown = ", ".join(f"{v} {k}" for k, v in sorted(compilability_counts.items()))
logger.info(
    "Step 6.5 complete: %d compiled (%s), %d skipped (no expressions)",
    len(compilation_results),
    breakdown or "none",
    skipped,
)
```

**Follows existing patterns**: This mirrors the style in `parameter_groups.py` (e.g., `"Derived {N} groups: {breakdown}"`) and `entry_point.py` (e.g., `"Generated entry point schema with {N} parameters"`).

### Fix 3: New Unit Tests

**New file:** `tests/unit/test_signature_extractor.py`

Test cases for field-level signature comparison:

1. **`test_matches_with_identical_fields`** -- Both signatures have same `input_fields` → `True`
2. **`test_matches_detects_added_field`** -- Expected has extra field → `False`
3. **`test_matches_detects_removed_field`** -- Expected missing a field → `False`
4. **`test_matches_detects_renamed_field`** -- Field name changed → `False`
5. **`test_matches_field_order_independent`** -- Same fields, different order → `True`
6. **`test_matches_none_fallback_extracted`** -- Extracted `input_fields=None`, expected has fields → `True` (FR-3)
7. **`test_matches_none_fallback_both`** -- Both `None` → `True`
8. **`test_matches_type_change_still_detected`** -- Different `input_type` with same fields → `False` (existing behavior preserved)
9. **`test_extract_input_field_refs_from_impl`** -- Parse a sample impl file with `inputs.x` patterns → correct field list
10. **`test_extract_input_field_refs_empty_stub`** -- Unmodified stub with only `raise NotImplementedError` → `input_fields` is `None`

---

## Potential Risks

1. **Stub regeneration churn**: Unmodified stubs where `input_fields` extracts as `None` won't detect field changes. This is acceptable per FR-3 (conservative fallback), and regenerating an unmodified stub is harmless anyway since the content is generated fresh.

2. **False positives from non-input attribute access**: If an impl accesses `inputs.some_method()` or similar, it would be collected as a field name. Risk is low -- generated Input classes are Pydantic models with only field attributes, and the convention is `inputs.field_name` for data access.

3. **Auto-impl field detection**: Auto-generated impls use `inputs.X` in compiled expressions, so field extraction works correctly for these. If a CalcDef's inputs change and the auto-impl is preserved incorrectly, the new field comparison will catch it.

## Integration Strategy

Both fixes are isolated changes that don't alter the pipeline's data flow:
- Fix 1 changes comparison logic within the existing `matches()` contract
- Fix 2 adds logging within the existing Step 6.5 block
- No new dependencies, no API changes, no template changes
- Existing `preservation.py` and `_generate_stencils()` work unchanged

## Validation Approach

### Automated Testing
- New `test_signature_extractor.py` with 10 test cases covering match/mismatch/fallback
- All 131 existing tests must pass (`uv run pytest tests/`)
- Type check: `uv run mypy src/`
- Lint: `uv run ruff check src/`

### Manual Testing
- Re-run manual test plan Tests 5 and 6 from `.project/active/expr-pipeline-integration/manual-test-plan.md`
- Test 5: Verify smart-regen detects field changes (add `scale` input to AreaCalc)
- Test 6: Verify `--verbose` shows Step 6.5 compilation activity

---

**Next Step:** After approval → `/_my_implement`
