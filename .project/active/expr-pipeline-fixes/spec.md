# Spec: Pipeline Integration Fixes -- Smart-Regen Field Comparison & Step 6.5 Logging

**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-02-07 23:45 UTC
**Complexity:** LOW
**Branch:** cost-pattern
**Epic:** EXPR-CODEGEN Item 4 (follow-up)

---

## Business Goals

### Why This Matters

Manual testing of the expr-pipeline-integration feature (Item 4) revealed two issues that undermine confidence in the pipeline:

1. **Smart-regen is field-blind (Bug):** When a CalcDef's inputs change (added, removed, or renamed), the stencil is incorrectly preserved because signature comparison only checks the input type *name* (e.g., `"AreaCalcInput"`), not the actual *fields* of that type. This silently produces broken code -- the impl file references stale inputs while its module wrapper has already been regenerated with the new signature.

2. **Step 6.5 is silent on success (Gap):** Expression compilation produces zero log output when all CalcDefs compile cleanly. There is no way to verify from CLI output that the compilation step ran, which CalcDefs were compiled, or what their compilability results are.

### Success Criteria

- [ ] Smart-regen detects input field changes (add/remove/rename) and regenerates the stencil
- [ ] Smart-regen correctly backs up the old file before regenerating
- [ ] Verbose output shows compilation activity for every CalcDef processed
- [ ] Manual test plan Tests 5 and 6 pass on re-execution

### Priority

P1 for the signature bug (blocks E2E validation confidence). P2 for the logging gap (observability).

---

## Problem Statement

### Current State

**Signature comparison (Bug):**
- `FunctionSignature.matches()` compares only `function_name`, `input_type` (class name string), and `return_type`
- `generate_expected_signature()` already extracts `input_fields` from the CalcDef but the data is unused in comparison
- `extract_signature_from_impl()` does not extract input field information at all (defaults to `None`)
- Adding a new input `scale` to `AreaCalc` does not change the type name `"AreaCalcInput"`, so the comparison reports "Signature unchanged" and the stencil is preserved with the old 2-input expression

**Step 6.5 logging (Gap):**
- The compilation loop in `initialization.py` (line ~168) only has `logger.warning()` in the `except` branch
- On the success path (normal case), there are zero log calls
- Running with `--verbose` and grepping for `compil|expression` returns no output

### Desired Outcome

- Signature comparison detects any change to a CalcDef's input fields and triggers regeneration with backup
- Step 6.5 emits INFO-level log messages showing compilation progress and results

---

## Scope

### In Scope

1. **Signature comparison** (`analysis/signature_extractor.py`)
   - `FunctionSignature.matches()` MUST compare input fields, not just input type name
   - The comparison MUST use the most robust method available to detect field-level changes

2. **Step 6.5 logging** (`generation/initialization.py`)
   - INFO-level log messages for compilation activity

### Out of Scope

- Changes to the expression compiler itself
- Changes to template rendering
- Changes to `preservation.py` flow (the `should_regenerate_stencil` decision logic is correct; only its `matches()` input is incomplete)
- New manual test plan tests (existing Tests 5 and 6 cover these fixes)

### Edge Cases & Considerations

- **Field ordering:** Renaming an input and adding another input in the same edit should both be detected
- **Backwards compatibility:** Existing impl files that predate the fix (where `input_fields` is `None` on the extracted side) SHOULD be treated conservatively -- if field information cannot be determined, the comparison SHOULD fall back to current behavior (match on type name) rather than force regeneration
- **Output field changes:** The current scope addresses *input* field changes only. Output field changes already trigger regeneration because the return type changes (single float vs tuple)

---

## Requirements

### Functional Requirements

> All requirements are from manual test results.

1. **FR-1**: `FunctionSignature.matches()` MUST return `False` when the input fields of two signatures differ (field added, removed, or renamed)

2. **FR-2**: The field comparison MUST use the most robust method available to detect changes -- the specific mechanism (parsing the module wrapper, embedding field metadata in the impl file, or other approach) is a design decision

3. **FR-3**: When `input_fields` cannot be determined for the existing implementation (e.g., legacy files), `matches()` SHOULD fall back to the current type-name-only comparison rather than forcing regeneration

4. **FR-4**: Step 6.5 MUST emit an INFO-level log message when the compilation step begins

5. **FR-5**: Step 6.5 MUST emit an INFO-level log message for each CalcDef compiled, including the CalcDef name and its compilability result

6. **FR-6**: Step 6.5 MUST emit an INFO-level summary after all CalcDefs are processed, indicating how many were compiled and the breakdown by compilability category

---

## Acceptance Criteria

### Core Functionality

- [ ] Adding an input to a CalcDef triggers stencil regeneration (not preservation) under `--smart-regen`
- [ ] Removing an input from a CalcDef triggers stencil regeneration under `--smart-regen`
- [ ] Renaming an input in a CalcDef triggers stencil regeneration under `--smart-regen`
- [ ] Old impl file is backed up before regeneration when signature changes
- [ ] Regenerated impl file contains the updated expression referencing new inputs
- [ ] Legacy impl files without field metadata are preserved (not force-regenerated)
- [ ] `--verbose` output contains INFO-level lines about compilation start, per-CalcDef results, and summary
- [ ] No WARNING or ERROR messages appear for cleanly compilable models

### Quality & Integration

- [ ] All 131 existing automated tests pass with zero regressions
- [ ] Manual test plan Tests 5 and 6 pass on re-execution
- [ ] `uv run mypy src/` passes on all modified files
- [ ] `uv run ruff check src/` passes on all modified files
- [ ] New unit tests cover field-level signature comparison (match, mismatch, None fallback)

---

## Related Artifacts

- **Parent spec:** `.project/active/expr-pipeline-integration/spec.md` (FR-13 verification gap)
- **Manual test plan:** `.project/active/expr-pipeline-integration/manual-test-plan.md` (Tests 5 & 6)
- **Signature extractor:** `src/sysml_codegen/analysis/signature_extractor.py`
- **Preservation logic:** `src/sysml_codegen/generation/preservation.py`
- **Pipeline init:** `src/sysml_codegen/generation/initialization.py`
- **Stencil generation:** `src/sysml_codegen/cli/__init__.py` (`_generate_stencils`)

### Files Modified (Expected)

| File | Change |
|------|--------|
| `analysis/signature_extractor.py` | Fix `matches()` to compare input fields; fix or augment `extract_signature_from_impl()` |
| `generation/initialization.py` | Add INFO-level logging to Step 6.5 |

---

**Next Steps:** After approval, proceed to `/_my_design`
