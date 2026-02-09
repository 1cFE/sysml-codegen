# Implementation Plan: Attribute Expression AST Discovery & Architecture Evaluation

**Status:** Complete
**Created:** 2026-02-08
**Last Updated:** 2026-02-08

## Source Documents
- **Spec:** `.project/active/attr-expr-spike/spec.md`
- **Design:** `.project/active/attr-expr-spike/design.md` -- See here for component details, data classes, classification logic, compilation approach

## Implementation Strategy

**Phasing Rationale:**
The critical risk is whether SysIDE populates `feature_value_expression` on PartDef attributes at all. Phase 1 answers this immediately -- if NO, the spike stops with a documented NO-GO and Phases 2-3 are skipped. If YES, Phase 2 characterizes the data (classification, references, inventory), and Phase 3 proves compilation and writes the report. Each phase extends the same script file incrementally.

**Overall Validation Approach:**
- No unit tests (research spike per spec)
- Validation = script runs without errors on all 3 model suites and produces concrete answers
- Each phase produces visible stdout output for interactive verification
- Final phase writes persistent report to `.project/active/attr-expr-spike/report.md`

---

## Phase 1: Scaffold + Q1 (AST Availability) -- The Hard Gate

### Goal
Build script skeleton with model loading, iterate PartDef/PartUsage attributes across 3 model suites, and answer Q1: does `feature_value_expression` exist on PartDef attributes? This is the single highest-risk question that gates the entire ATTR-EXPR epic.

### Test Stencil (Run This After Writing)
```bash
# No unit tests for spike. Validation is running the script:
uv run python scripts/spike_attribute_expressions.py

# Expected output (if ASTs exist):
#   === Suite: solar_battery_model ===
#   Parts found: N (PartDefinition: X, PartUsage: Y)
#   Part: solar_battery_plant (PartUsage)
#     p_net_mw        : has_expr=True  root=LiteralRational
#     p_net_kw        : has_expr=True  root=OperatorExpression  <-- KEY
#     ...
#
# Expected output (if ASTs DON'T exist):
#     p_net_kw        : has_expr=False  <-- STOP, document NO-GO
```

### Changes Required

**See `design.md` for:**
- Data classes (`AttributeExprInfo`, `SuiteResult`) -> `design.md#1-data-classes`
- Model loading pattern (`load_and_iterate_parts`) -> `design.md#2-model-loading-and-attribute-iteration`
- Attribute inspection (`inspect_attribute`) -> `design.md#2-model-loading-and-attribute-iteration`

**Specific file changes:**

#### 1. Spike Script
**File:** `scripts/spike_attribute_expressions.py` (NEW)
- [x] Create file with shebang, docstring, imports
- [x] Implement `AttributeExprInfo` and `SuiteResult` data classes
- [x] Implement `sanitize_name()`, `measure_depth()`, `collect_node_types()` helpers (reuse from `spike_extract_expression_asts.py`)
- [x] Implement `load_and_iterate_parts()` -- load model, iterate both `PartDefinition` and `PartUsage` elements
- [x] Implement `inspect_attribute()` -- check `feature_value_expression`, collect root node type, depth, node types, operators
- [x] Implement `run_q1()` -- iterate parts, inspect attributes, print per-suite AST availability table
- [x] Implement `main()` with `DEFAULT_SUITES` for solar_battery, catf_mfe, chain_spike (use `tests/fixtures/` paths, with comma-separated multi-dir for CATF)
- [x] Add FR-8: dump available API fields on first attribute with expression (use `dir()` or `hasattr()` checks for key fields)

### Validation

**Automated:**
- [x] `uv run python scripts/spike_attribute_expressions.py` runs without errors
- [x] `uv run pytest tests/` -- existing tests still pass (sanity check, script doesn't touch src/)

**Manual:**
- [x] Output shows solar_battery `p_net_kw` attribute with `has_expr=True` and root `OperatorExpression` (if ASTs exist)
- [x] Output shows CATF physics EXPOSE attributes with `has_expr=True` (if ASTs exist)
- [x] Output shows chain_spike literal attributes (control group)
- [x] If `has_expr=False` for all non-literal attributes: STOP, write NO-GO report, skip Phases 2-3

**What We Know Works After This Phase:**
- Model loading works for all 3 suites
- PartDef/PartUsage iteration finds all parts with attributes
- Q1 answered: concrete yes/no on `feature_value_expression` availability for PartDef attributes

---

## Phase 2: Q2-Q5 (Reference Resolution, Pattern Classification, Inventory)

### Goal
Extract references from attribute expressions, classify each attribute as FORMULA/EXPOSE/LITERAL/UNRESOLVABLE, and build the pattern inventory table. This answers Q2 (reference resolution), Q3 (EXPOSE pattern structure), Q4 (cross-part references), and Q5 (pattern inventory).

### Test Stencil (Run This After Writing)
```bash
uv run python scripts/spike_attribute_expressions.py

# Expected Q2 output:
#   === Q2: Reference Resolution ===
#   solar_battery_plant.p_net_kw:
#     ref: p_net_mw -> sibling attribute (RESOLVED)
#
# Expected Q5 output:
#   === Q5: Pattern Inventory ===
#   | Suite          | FORMULA | EXPOSE | LITERAL | UNRESOLVABLE | Total |
#   | solar_battery  |    1    |    0   |    9    |      0       |  10   |
#   | catf_mfe       |    0    |   12   |   80+   |      ?       |  92+  |
#   | chain_spike    |    0    |    0   |    4    |      0       |   4   |
```

### Changes Required

**See `design.md` for:**
- Classification logic (`classify_attribute_expression`) -> `design.md#3-classification-logic-q5`
- Reference resolution approach -> `design.md#2-model-loading-and-attribute-iteration`

**Specific file changes:**

#### 1. Extend Spike Script
**File:** `scripts/spike_attribute_expressions.py` (MODIFY)
- [x] Implement `classify_attribute_expression()` -- classify refs against sibling attrs and calc usages on the same part (see `design.md#3-classification-logic-q5`)
- [x] Update `inspect_attribute()` to call classification and populate `ref_names`, `ref_qualified_names`, `classification`
- [x] Implement `run_q2()` -- per-attribute reference table showing ref name, resolved target, ref type
- [x] Implement `run_q3()` -- filter EXPOSE-pattern attributes, document AST structure (FeatureChainExpression vs FeatureReferenceExpression), note backtracker overlap
- [x] Implement `run_q4()` -- scan for cross-part references (dotted paths beyond `calc.output`), report findings or "none found"
- [x] Implement `run_q5()` -- aggregate classification counts per suite into inventory table
- [x] Handle edge cases from spec: unit annotations `[m]`, `:>>` redefinitions, untyped attributes -- log any encountered

### Validation

**Automated:**
- [x] `uv run python scripts/spike_attribute_expressions.py` runs without errors
- [x] Q2-Q5 sections produce non-empty output for each suite

**Manual:**
- [x] solar_battery `p_net_kw` classified as FORMULA with ref to `p_net_mw`
- [x] CATF physics EXPOSE attributes (lines 114-122) classified as EXPOSE with dotted refs
- [x] chain_spike attributes classified as LITERAL (control group)
- [x] Inventory table has counts for all 3 suites with no "unknown" entries
- [x] Any unexpected node types (InvocationExpression, etc.) logged per FR-9

**What We Know Works After This Phase:**
- Reference extraction works on attribute expressions
- Classification logic correctly distinguishes FORMULA/EXPOSE/LITERAL patterns
- EXPOSE pattern AST structure documented (Q3)
- Cross-part reference patterns documented or absence confirmed (Q4)
- Pattern inventory complete across all 3 model suites (Q5)

---

## Phase 3: Q6 + Q7 (Compilation Proof, Architecture Recommendation) + Report

### Goal
Attempt to compile at least one FORMULA-pattern attribute using Phase 1's `build_expression_ast()` + `compile_expression()`, evaluate architecture options grounded in Q1-Q5 data, and write the final structured report with go/no-go decision.

### Test Stencil (Run This After Writing)
```bash
uv run python scripts/spike_attribute_expressions.py

# Expected Q6 output:
#   === Q6: Compiler Reuse ===
#   Compiling solar_battery_plant.p_net_kw (FORMULA):
#     input_names: {p_net_mw, n_mod, plant_availability, ...}
#     build_expression_ast: OK
#     compile_expression:   (inputs.p_net_mw * 1000.0)  <-- SUCCESS
#
#   Compiling catf_physics.p_alpha_out (EXPOSE):
#     build_expression_ast: UNSUPPORTED (FeatureChainExpression)  <-- EXPECTED GAP

# Verify report written:
cat .project/active/attr-expr-spike/report.md | head -20
```

### Changes Required

**See `design.md` for:**
- Compilation approach (`attempt_compilation`) -> `design.md#4-compilation-attempt-q6`
- Report structure -> `design.md#5-spike-report-generation`

**Specific file changes:**

#### 1. Extend Spike Script
**File:** `scripts/spike_attribute_expressions.py` (MODIFY)
- [x] Implement `attempt_compilation()` -- call `build_expression_ast()` with sibling attr names as `input_names`, then `compile_expression()` (see `design.md#4-compilation-attempt-q6`)
- [x] Implement `run_q6()` -- attempt compilation on all FORMULA-pattern attributes, attempt on at least one EXPOSE for gap documentation; report successes/failures with compiled Python or error messages
- [x] Implement `run_q7()` -- evaluate Options A/B/C/D based on Q1-Q6 findings, print recommendation with rationale
- [x] Implement `write_report()` -- write structured markdown to `.project/active/attr-expr-spike/report.md` with all Q1-Q7 answers, inventory table, compilation results, architecture recommendation, and go/no-go decision
- [x] Update `main()` to orchestrate Q1-Q7 in sequence, then write report

#### 2. Report File
**File:** `.project/active/attr-expr-spike/report.md` (NEW, generated by script)
- [x] Written automatically by `write_report()`
- [x] Verify structure matches `design.md#5-spike-report-generation`

### Validation

**Automated:**
- [x] `uv run python scripts/spike_attribute_expressions.py` runs without errors and writes report
- [x] `uv run pytest tests/` -- existing tests still pass (final sanity check)

**Manual:**
- [x] Q6: At least one attribute expression compiles to valid Python (spec AC)
- [x] Q6: solar_battery `p_net_kw` compiles to something like `(inputs.p_net_mw * 1000.0)`
- [x] Q6: EXPOSE-pattern compilation failure documented with specific AST structure
- [x] Q7: Architecture recommendation is one of Option A/B/C/D with rationale referencing Q1-Q6 data
- [x] Report at `.project/active/attr-expr-spike/report.md` is well-structured, answers all 7 questions
- [x] Go/no-go decision documented with clear criteria
- [x] No files modified in `src/` or `tests/`

**What We Know Works After This Phase:**
- Phase 1 expression compiler works (or documented gaps) for attribute expressions
- Architecture recommendation grounded in empirical data
- Complete report ready for ATTR-EXPR epic Item 2 decision
- Go/no-go gate resolved

---

## Environment Setup

**See CLAUDE.md for full environment rules**

```bash
# No new dependencies needed -- spike uses existing packages
# Verify environment:
uv run python -c "from sysml_codegen.extraction.extractor import SysMLDataExtractor; print('OK')"
uv run python -c "from sysml_codegen.extraction.expression_compiler import build_expression_ast, compile_expression; print('OK')"
```

---

## Risk Management

**See `design.md#potential-risks` for detailed risk analysis**

**Phase-Specific Mitigations:**
- **Phase 1**: If `feature_value_expression` is missing on PartDef attributes, stop immediately and write NO-GO report. Do not proceed to Phase 2-3.
- **Phase 2**: Classification logic may need runtime adjustment based on actual `extract_feature_refs()` output format. The design notes this explicitly -- iterate on classification heuristics until results match expected patterns from the SysML source.
- **Phase 3**: If compilation fails on ALL attributes (not just EXPOSE), investigate whether `build_expression_ast()` needs a new reference resolution path for attribute context. Document the gap even if compilation doesn't work.

## Implementation Notes

All three phases implemented in a single pass (all-at-once execution).

### Phase 1 Completion
**Completed:** 2026-02-08
**Actual Changes:** Created `scripts/spike_attribute_expressions.py` with full scaffold: data classes (`AttributeExprInfo`, `SuiteResult`), `load_and_iterate_parts()`, `inspect_attribute()`, `sanitize_name()`, `measure_depth()`, `collect_node_types()`, `inventory_api_fields()` (FR-8), and `run_q1()`.
**Issues:** Minor `DeprecationWarning` on `is_read_only` API field -- changed to `is_constant`.
**Deviations:**
- Used `tests/fixtures/catf_mfe_model/library` and `.../designs/catf_mfe` instead of external `/home/reid/fusion_modeling/models/` paths. Fixture copy works correctly.
- Added `part_type` field to `AttributeExprInfo` to distinguish PartDefinition vs PartUsage (not in original design).
- Added `sysml_text` field using `reconstruct_expression()` for human-readable display.

### Phase 2 Completion
**Completed:** 2026-02-08
**Actual Changes:** Added `classify_attribute_expression()`, `run_q2()`, `run_q3()`, `run_q4()`, `run_q5()`.
**Issues:** None.
**Deviations:**
- Classification reveals 19 MIXED-pattern attributes in CATF where refs match both sibling attribute names AND calc usage names. This happens because EXPOSE-pattern refs (e.g., `wall_plug_power`) match the attribute's own name in `sibling_attr_names`. The qualified name shows the ref actually points to a CalcDef output. Future Item 2 should use qualified name resolution, not just simple name matching.
- Q4 found 0 dotted references -- `extract_feature_refs()` returns separate ref names for each segment of a FeatureChainExpression, not dotted paths. The cross-part info is in the Q2/Q3 analysis instead.

### Phase 3 Completion
**Completed:** 2026-02-08
**Actual Changes:** Added `attempt_compilation()`, `run_q6()`, `run_q7()`, `run_go_nogo()`, `run_fr9()`, `write_report()`.
**Issues:** None.
**Deviations:**
- Added `run_fr9()` for unsupported node type inventory (no unexpected types found).
- Report written in markdown with code blocks wrapping each section for readability.
- `LiteralString` compilation fails (e.g., CATF `system_type = "NBI"`) -- the Phase 1 compiler doesn't handle `LiteralString`. This is expected and documented.

### Key Findings
- **Q1 -- GO**: 375/540 attributes have `feature_value_expression`. ASTs available on both PartDef and PartUsage.
- **Q5 Inventory**: 1 FORMULA, 26 EXPOSE, 327 LITERAL, 2 UNRESOLVABLE, 19 MIXED, 165 NO_EXPRESSION
- **Q6**: 260/331 compiled successfully. `p_net_kw` -> `(inputs.p_net_mw * 1000.0)`. EXPOSE fails as expected (FeatureChainExpression unsupported).
- **Go/No-Go: GO** -- proceed to ATTR-EXPR Item 2

### Validation Results
- `uv run python scripts/spike_attribute_expressions.py` -- runs without errors on all 3 suites
- `uv run pytest tests/` -- 167 tests pass, no regressions
- Report written to `.project/active/attr-expr-spike/report.md` (2130 lines)
- No production code modified

---

**Status**: Complete
