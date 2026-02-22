# Component: AST Dispatch Invariant (C07)

**Status**: DONE
**Created**: 2026-02-17
**Last updated**: 2026-02-17
**Updated by**: C07 build session

## Source Documents

- **Checklist entry**: `COMPONENT_CHECKLIST.md` -- C07
- **Design intent**: [19-ast-dispatch-invariant.md](../../concepts/refactor-design-intent/19-ast-dispatch-invariant.md)
- **Requirements**: REQ-AST-01 through REQ-AST-07
- **Depends on**: C04 (Expression Compiler -- complete), C05 (Computed Attributes -- complete), C06 (Hierarchy Resolver -- plan complete, build pending)

---

## 1. Assessment

### What This Component Does

C07 is a cross-cutting invariant audit. It verifies that every `SysideAdapter.is_instance()` dispatch site in the codebase that checks both `FeatureChainExpression` (FCE) and `OperatorExpression` (OE) always checks FCE first. FCE is a subtype of OE in SysIDE's type system, so checking OE first misclassifies FCE nodes. This was the root cause of Bug A (commit `20b720e`), which broke 37 aggregation inputs.

C07 does not own a single module -- it audits all dispatch sites across 5 files and enforces the invariant via static analysis, comment presence checks, and behavioral regression tests.

### Current State

- **Exists?** The invariant is enforced at the 3 Bug A sites (fixed in `20b720e`). Two additional dual-check sites (`usage_extractor.py`, `parameter_groups.py`) also have FCE before OE but lack the invariant comment and don't follow canonical ordering.
- **Needs extraction/refactoring?** Minor: add invariant comments to 2 sites. No reordering needed (elif chains are safe).
- **Current test coverage**:
  - C04 conformance: REQ-AST-01 static analysis for `expression_compiler.py:build_expression_ast` and `expression_utils.py:reconstruct_expression` (2 of 5 dual-check sites)
  - C06 plan: REQ-HR-05 static analysis for `hierarchy_resolver.py:_walk_aggregation_ast` (1 of 5 dual-check sites)
  - No codebase-wide audit test exists. No test for the remaining 2 dual-check sites. No behavioral tests for REQ-AST-05/06/07.

### Design Consistency Check

- [x] All acceptance criteria from COMPONENT_CHECKLIST are testable with real data (no mocks) -- **except REQ-AST-05/06/07 behavioral tests which require SysIDE adapter boundary stubs (Ground Rule 1)**
- [x] AC are consistent with the requirements in the design intent doc(s)
- [x] No contradictions with other component specs
- [x] Input/output interfaces match what upstream/downstream components expect
- [x] Any ambiguities or gaps identified and resolved (documented below)

**Issues found during review:**

1. **Two dual-check sites missing invariant comment (REQ-AST-02 violation).**
   `usage_extractor.py:extract_binding_info` (line 521) and `parameter_groups.py:_extract_default_value` (line 181) both check FCE before OE but lack the "MUST be before OperatorExpression" comment. Both use `elif` chains, making them safe from the subtype overlap, but REQ-AST-02 requires the comment at every dual-check site.
   **Resolution**: Build phase adds the invariant comment to both sites. Tests initially expect this comment, so they'll fail before the fix and pass after.

2. **Two dual-check sites don't follow canonical ordering (REQ-AST-03).**
   - `usage_extractor.py:extract_binding_info`: FCE(521), FRE(534), Literal(546), OE(557) -- should be FCE, OE, FRE, Literal
   - `parameter_groups.py:_extract_default_value`: Literal(163-174), FRE(176), FCE(181), OE(186) -- should be FCE, OE, FRE, Literal
   Both are functionally correct due to `elif` chains. The design doc acknowledges this: "Sites using elif chains are safe because first-match-wins prevents misclassification. However, they should still follow canonical ordering for consistency."
   **Resolution**: The critical invariant (FCE before OE) holds at both sites. Reordering elif chains is low-value, high-risk (changes behavioral order even if types don't overlap). C07 tests verify the critical invariant (FCE < OE line number) but accept non-canonical FRE/Literal placement in elif chains. Document the non-canonical ordering as a known deviation, not a blocker.

3. **C07 overlaps with C04 and C06 for 3 of 5 dual-check sites.**
   C04 covers `build_expression_ast` + `reconstruct_expression` static analysis. C06 covers `_walk_aggregation_ast` static analysis. C07 re-verifies all 5 sites in a single parametrized audit test. The overlap is intentional -- C07 is the comprehensive codebase-wide audit, C04/C06 are component-scoped. If a future refactor adds a new dispatch site, C07's total-site-count test catches it.

4. **REQ-AST-04 is a process requirement, not a code property.**
   "New dispatch sites SHALL follow REQ-AST-03 ordering" can't be tested against existing code. **Resolution**: C07 tests the total count of dispatch functions with `is_instance` calls referencing expression types. If a new dispatch function appears, the count test fails, forcing the developer to verify ordering.

5. **REQ-AST-05/06/07 behavioral tests need SysIDE adapter boundary stubs.**
   AST fields are null in snapshots (Phase 0 Learning #2). Behavioral tests for `_walk_aggregation_ast()`, `build_expression_ast()`, and `reconstruct_expression()` with FCE/OE mock nodes require monkeypatched `SysideAdapter.is_instance()`. Acceptable per Ground Rule 1. The dual-match mock class (`MockFeatureChainExpressionOperatorExpression`) from C04 proves SysideAdapter's name-based fallback handles the subtype case.

### Risks & Unknowns

- **Low risk**: Static analysis approach proven by C04/C06. All dispatch sites already identified.
- **No unknowns**: All 8 dispatch functions audited, all 5 dual-check sites confirmed correct.
- **Comment-addition risk**: Adding comments to `usage_extractor.py` and `parameter_groups.py` is trivial (no behavioral change).

---

## 2. Spike

**Decision**: SKIP
**Rationale**:
1. All 8 dispatch functions and 5 dual-check sites are fully enumerated (grep complete).
2. Static analysis approach proven by C04 (2 tests, all passing).
3. Mock infrastructure for behavioral tests (dual-match class, monkeypatch) exists from C04.
4. The two missing comments are the only code change needed -- trivial and safe.
5. No unknowns that could invalidate the build plan.

---

## 3. Test Plan

**Test file**: `tests/conformance/test_ast_dispatch_invariant.py`
**Fixture data**: solar_battery extraction snapshot (for REQ-AST-05 SingletonTerm verification). SysIDE adapter boundary stubs for REQ-AST-05/06/07 behavioral tests.

### Complete Dispatch Site Inventory

This inventory is the foundation for all audit tests. Every dispatch function with `is_instance()` calls referencing expression types:

| # | File | Function | Types checked | Dual-check? | Order | Comment? |
|---|------|----------|--------------|-------------|-------|----------|
| 1 | `expression_utils.py` | `reconstruct_expression` | FCE:48, OE:51, FRE:54 | Yes | Canonical | Yes |
| 2 | `expression_compiler.py` | `build_expression_ast` | FCE:316, OE:323, FRE:381, Literal:395+ | Yes | Canonical | Yes |
| 3 | `hierarchy_resolver.py` | `_walk_aggregation_ast` | FCE:331, OE:338, FRE:361 | Yes | Canonical | Yes |
| 4 | `usage_extractor.py` | `extract_binding_info` | FCE:521, FRE:534, Literal:546, OE:557 | Yes (elif) | FCE<OE ✓, non-canonical | **No** |
| 5 | `parameter_groups.py` | `_extract_default_value` | Literal:163, FRE:176, FCE:181, OE:186 | Yes (elif) | FCE<OE ✓, non-canonical | **No** |
| 6 | `hierarchy_resolver.py` | `_extract_single_redefinition` | FCE:105, FRE:116 | No (FCE+FRE) | N/A | N/A |
| 7 | `hierarchy_resolver.py` | `_unwrap_invocation` | FCE:294, FRE:296 | No (FCE+FRE) | N/A | N/A |
| 8 | `extractor.py` | `_parse_expression_to_path` | FCE:276, FRE:295 | No (FCE+FRE) | N/A | N/A |

### Test Cases

> Every requirement (REQ-AST-01 through REQ-AST-07) has at least one test.
> Static analysis tests use Python `ast` module on source files (no mocks).
> Behavioral tests use SysIDE adapter boundary stubs per Ground Rule 1.

| Test | Requirement | What it verifies |
|------|-------------|------------------|
| **REQ-AST-01: FCE before OE at every dual-check site** | | |
| `test_fce_before_oe_all_dual_check_sites[reconstruct_expression]` | REQ-AST-01 | Static: FCE line < OE line in `expression_utils.py:reconstruct_expression` |
| `test_fce_before_oe_all_dual_check_sites[build_expression_ast]` | REQ-AST-01 | Static: FCE line < OE line in `expression_compiler.py:build_expression_ast` |
| `test_fce_before_oe_all_dual_check_sites[_walk_aggregation_ast]` | REQ-AST-01 | Static: FCE line < OE line in `hierarchy_resolver.py:_walk_aggregation_ast` |
| `test_fce_before_oe_all_dual_check_sites[extract_binding_info]` | REQ-AST-01 | Static: FCE line < OE line in `usage_extractor.py:extract_binding_info` |
| `test_fce_before_oe_all_dual_check_sites[_extract_default_value]` | REQ-AST-01 | Static: FCE line < OE line in `parameter_groups.py:_extract_default_value` |
| **REQ-AST-02: Comment present at every dual-check site** | | |
| `test_invariant_comment_at_all_dual_check_sites[reconstruct_expression]` | REQ-AST-02 | "MUST be before OperatorExpression" comment within 5 lines of FCE check |
| `test_invariant_comment_at_all_dual_check_sites[build_expression_ast]` | REQ-AST-02 | Same for expression_compiler.py |
| `test_invariant_comment_at_all_dual_check_sites[_walk_aggregation_ast]` | REQ-AST-02 | Same for hierarchy_resolver.py |
| `test_invariant_comment_at_all_dual_check_sites[extract_binding_info]` | REQ-AST-02 | Same for usage_extractor.py -- **fails before build** |
| `test_invariant_comment_at_all_dual_check_sites[_extract_default_value]` | REQ-AST-02 | Same for parameter_groups.py -- **fails before build** |
| **REQ-AST-03: Canonical ordering at all dual-check sites** | | |
| `test_canonical_ordering_fce_oe_fre[reconstruct_expression]` | REQ-AST-03 | FCE < OE < FRE (lines) in `reconstruct_expression` |
| `test_canonical_ordering_fce_oe_fre[build_expression_ast]` | REQ-AST-03 | FCE < OE < FRE (lines) in `build_expression_ast` |
| `test_canonical_ordering_fce_oe_fre[_walk_aggregation_ast]` | REQ-AST-03 | FCE < OE < FRE (lines) in `_walk_aggregation_ast` |
| `test_elif_sites_fce_before_oe[extract_binding_info]` | REQ-AST-03 | FCE < OE (critical invariant) in elif-chain site (full canonical not required) |
| `test_elif_sites_fce_before_oe[_extract_default_value]` | REQ-AST-03 | FCE < OE (critical invariant) in elif-chain site (full canonical not required) |
| **REQ-AST-04: Total dispatch site guardrail** | | |
| `test_total_dual_check_site_count` | REQ-AST-04 | Exactly 5 functions in the codebase have both FCE and OE `is_instance()` checks. Fails if a new unaudited site appears. |
| `test_total_dispatch_function_count` | REQ-AST-04 | Exactly 8 functions in the codebase have `is_instance()` calls on expression types. Fails if a new unaudited function appears. |
| **REQ-AST-05: FCE → SingletonTerm in aggregation** | | |
| `test_fce_classified_as_singleton_term_solar_battery` | REQ-AST-05 | Every SingletonTerm in solar_battery snapshot has dotted `source_path` (from FCE, not bare FRE). No SingletonTerm has an undotted source_path. |
| `test_no_singleton_term_in_local_terms` | REQ-AST-05 | No solar_battery aggregation has a LocalTerm whose `attribute_name` contains `.` (would indicate FCE mis-classified as LocalTerm -- Bug A regression). |
| `test_walk_aggregation_ast_fce_produces_singleton_behavioral` | REQ-AST-05 | Behavioral: mock FCE node fed to `_walk_aggregation_ast` produces SingletonTerm in ctx (not LocalTerm). Uses SysIDE adapter boundary stub. |
| **REQ-AST-06: Expression compiler FCE diagnostic** | | |
| `test_build_expression_ast_fce_produces_feature_chain_reason` | REQ-AST-06 | Dual-match FCE+OE mock node → `build_expression_ast` returns UNSUPPORTED with "feature chain" in reason, NOT "unsupported operator: ." |
| `test_build_expression_ast_fce_no_dot_operator_error` | REQ-AST-06 | Same node: reason does NOT contain "unsupported operator" |
| **REQ-AST-07: reconstruct_expression FCE output format** | | |
| `test_reconstruct_expression_fce_returns_dotted_name` | REQ-AST-07 | Dual-match FCE+OE mock node with operands=[FRE("instance")] and target_feature.name="attr" → returns "instance.attr", NOT ".(instance)" |
| `test_reconstruct_expression_fce_no_dot_paren_format` | REQ-AST-07 | Result does NOT contain ".(" pattern (Bug A symptom) |
| `test_transformed_expressions_no_dot_paren_in_snapshots` | REQ-AST-07 | No solar_battery transformed_expression contains the `.()` pattern |
| **Regression: order reversal detection** | | |
| `test_regression_if_oe_checked_before_fce_in_walk_agg_ast` | REQ-AST-01 | Construct mock node matching both FCE and OE. With correct order: gets SingletonTerm. With reversed order (simulated by redefining dispatch): would get OE handler. Verify the current code takes the FCE path. |

**Expected test count**: ~28 tests (some parametrized over 3-5 dispatch sites).

### Test Infrastructure Needed

**Static analysis helpers** -- reuse from C04 (same `_find_is_instance_calls_in_function` + `_is_syside_is_instance_call`).

**Mock infrastructure** -- reuse from C04:
- `MockFeatureChainExpressionOperatorExpression` (dual-match class)
- `MockFeatureReferenceExpression`, `MockFeatureChainExpression`
- `mock_syside_adapter` fixture (monkeypatch)

**New helpers needed**:
- `_find_all_dispatch_functions(src_dir)` -- walks all `.py` files in `src/`, finds functions containing `is_instance(..., "FeatureChainExpression")` or `is_instance(..., "OperatorExpression")` calls. Returns dict of `{(file, function_name): {type_name: line_number}}`. Used by total count and comprehensive audit tests.
- `_find_comment_near_line(source_lines, target_line, pattern, window=5)` -- checks if a comment matching `pattern` appears within `window` lines above `target_line`. Used by REQ-AST-02 tests.

**Snapshot fixtures** -- existing `solar_battery_snapshot` from `tests/conformance/conftest.py`.

### Gate: Ready for BUILD
- [x] Test file exists with all test cases written
- [x] Tests run (expected: 2 REQ-AST-02 tests FAIL pending comment addition; all others PASS)
- [x] No test uses mocking outside SysIDE adapter boundary (verified by review)

---

## 4. Build Plan

### Files to Modify

| File | Change | Why |
|------|--------|-----|
| `src/sysml_codegen/extraction/usage_extractor.py` | Add invariant comment before line 521 (`is_instance(expr, "FeatureChainExpression")`) | REQ-AST-02: comment required at every dual-check site |
| `src/sysml_codegen/analysis/parameter_groups.py` | Add invariant comment before line 181 (`is_instance(expr, "FeatureChainExpression")`) | REQ-AST-02: comment required at every dual-check site |

### Files to Create

| File | Purpose |
|------|---------|
| `tests/conformance/test_ast_dispatch_invariant.py` | C07 conformance tests (~28 tests covering REQ-AST-01 through REQ-AST-07) |

### Implementation Notes

1. **Test organization**: Group tests by requirement in classes:
   `TestReqAst01FceBeforeOe`, `TestReqAst02CommentPresent`, `TestReqAst03CanonicalOrdering`,
   `TestReqAst04DispatchSiteGuardrail`, `TestReqAst05SingletonTermClassification`,
   `TestReqAst06ExpressionCompilerDiagnostic`, `TestReqAst07ReconstructExpressionFormat`,
   `TestRegressionOrderReversal`.
   Each class tagged with `@pytest.mark.req("REQ-AST-0N")`.

2. **Parametrized audit tests (REQ-AST-01, REQ-AST-02)**: Define a `DUAL_CHECK_SITES` list of tuples: `(source_path, function_name)` for all 5 dual-check sites. Parametrize over this list for both ordering and comment presence tests. This makes adding a new site trivial.

3. **Comprehensive dispatch function finder (REQ-AST-04)**: Walk all `.py` files under `src/sysml_codegen/`, parse with `ast` module, find all `FunctionDef` nodes containing `is_instance()` calls referencing expression type names (`FeatureChainExpression`, `OperatorExpression`, `FeatureReferenceExpression`). Return `{(relative_path, function_name): set_of_types}`. The total count tests compare against known counts (5 dual-check, 8 total dispatch functions).

4. **Comment addition format**: Match existing pattern from the 3 Bug A sites. Example for `usage_extractor.py`:
   ```python
   # FeatureChainExpression MUST be before OperatorExpression -- FCE is a
   # subtype of OE in SysIDE's type system (doc 19 invariant).
   if SysideAdapter.is_instance(expr, "FeatureChainExpression"):
   ```
   For `parameter_groups.py`, the comment goes before the `elif` for FCE (line 181). The elif chain makes the invariant implicit, but the comment documents the requirement.

5. **REQ-AST-03 split for canonical vs elif sites**: The 3 Bug A sites use `if`/`if`/`if` chains (not elif), so they must follow canonical order. The 2 elif sites need FCE before OE but don't need full canonical ordering (FRE/Literal placement is safe in elif chains). Split tests accordingly.

6. **Mock for _walk_aggregation_ast behavioral test (REQ-AST-05)**: Need to import `_walk_aggregation_ast` and `_AggregationContext` from `hierarchy_resolver.py`. Feed a mock FCE node + mock OE node, verify FCE → SingletonTerm (not LocalTerm). Monkeypatch `SysideAdapter.is_instance` + `extract_feature_chain_name` for this test.

7. **Mock for reconstruct_expression behavioral test (REQ-AST-07)**: Feed a dual-match FCE+OE mock node to `reconstruct_expression()`. The mock needs `operands` (list with one FRE element) and `target_feature.name` (for FCE path extraction). Verify result is `"instance.attr"`, NOT `".(instance)"`.

### Gate: Ready for VALIDATE
- [x] All test cases pass (26/26 pass, including the 2 that required comment addition)
- [x] No regressions in full test suite (1053 passed, 2 pre-existing spike failures unrelated to C07)
- [x] Lint clean on test file (pre-existing lint issues in usage_extractor.py and parameter_groups.py not introduced by C07)

---

## 5. Validation

### Acceptance Criteria (from COMPONENT_CHECKLIST C07)

- [x] AC1: Audit: every dual-check site checks FCE before OE (5 parametrized tests)
- [x] AC2: Comment present at every dual-check site (5 parametrized tests)
- [x] AC3: All 8+ dispatch sites follow canonical ordering: FCE, OE, FRE, Literal (with documented deviation for elif-chain sites) (3 canonical + 2 elif tests)
- [x] AC4: Regression test: if FCE/OE order reversed, test fails (1 behavioral regression test)

### Requirements Traceability

- [x] Every REQ-AST-01 through REQ-AST-07 has at least one passing test
- [x] Full test suite passes (record count: 1053 tests, 0 C07 failures; 2 pre-existing spike failures)
- [x] Cross-check: re-read design intent doc 19, verify all 7 requirements covered
- [x] No unresolved TODOs or FIXMEs in new/modified code

### Baseline Impact

No baseline impact expected. Comment additions are non-behavioral. No output changes.

---

## 6. Commit

**Branch**: `cost-pattern-refactor` (current branch)
**Commit convention**: one commit per component, message references component code

- [x] All validation checks above are green
- [x] `git add` only the files listed in Build Plan + test file + COMPONENT_CHECKLIST.md (no unrelated changes)
- [x] Commit message format:
  ```
  refactor(C07): AST Dispatch Invariant conformance tests

  - Tests: 26 new conformance tests in tests/conformance/test_ast_dispatch_invariant.py
  - Added invariant comments to usage_extractor.py and parameter_groups.py
  - Refs: REQ-AST-01 through REQ-AST-07
  - Design intent: 19-ast-dispatch-invariant.md
  ```
- [x] Committed successfully (b126d23)

---

## 7. Learnings

### Findings

1. **Plan's function name for usage_extractor dispatch site was wrong.** The plan
   listed `extract_binding_info` but the actual function containing the FCE/OE
   checks at lines 521/557 is `_extract_single_binding` (a private helper called
   by `extract_binding_info`). Corrected in the test file. Line numbers matched.

2. **Broader `is_instance()` search finds 13 functions, not 8.** The plan counted
   8 "dispatch functions" but used the narrower `SysideAdapter.is_instance()` pattern.
   Using the broader `*.is_instance()` pattern (which also catches `self.adapter.is_instance()`
   in `extractor.py`) finds 13 functions total. 5 of these check only a single expression
   type (e.g., `_extract_simple_reference` checks only FRE). The meaningful count for
   dispatch site auditing is "functions checking 2+ expression types" = 8. This is what
   the guardrail test verifies.

3. **SysideAdapter name-based fallback eliminates need for monkeypatching.** All behavioral
   tests (REQ-AST-05/06/07) work without monkeypatching because the dual-match mock class
   `MockFeatureChainExpressionOperatorExpression` triggers SysideAdapter's class-name-based
   type checking. This is simpler than the plan's suggestion to monkeypatch.

4. **Static analysis helper broadened for C07.** C04/C06 used `_is_syside_is_instance_call`
   (checks `SysideAdapter.is_instance()`). C07 uses `_is_any_is_instance_call` (checks any
   `*.is_instance()`) to catch `self.adapter.is_instance()` in `extractor.py`. This is the
   third copy of the helper — per C06 learning #4, consider extracting to `tests/helpers/`
   if a fourth copy appears.

### Design Doc Updates Needed

| Doc | What to update | Why |
|-----|---------------|-----|
| 19-ast-dispatch-invariant.md | Update Dispatch Site Audit table: correct line numbers (may have shifted since doc was written) and note elif-chain sites as "safe but non-canonical" | Line numbers in doc may not match current source |
| 19-ast-dispatch-invariant.md | Clarify "8 files" → "8 dispatch functions across 5 files" in Section "Dispatch Site Audit" | Doc says "8 files" but there are 8 functions in 5 files |
| COMPONENT_CHECKLIST.md | C07 AC3: add "(with documented deviation for elif-chain sites)" qualifier | elif sites are safe and reordering is higher risk than value |

### Cross-Component Impact

| Component | Impact | Action needed |
|-----------|--------|---------------|
| C06 (Hierarchy Resolver) | C07 covers `_walk_aggregation_ast` dispatch ordering; C06's REQ-HR-05 tests overlap | No action -- overlap is intentional (component-scoped vs. cross-cutting) |
| C04 (Expression Compiler) | C07 re-verifies `build_expression_ast` + `reconstruct_expression`; C04's REQ-AST-01 tests overlap | No action -- overlap is intentional |
| Future components | REQ-AST-04 total-count test catches new unaudited dispatch sites | New dispatch functions must be added to the DUAL_CHECK_SITES list and verified |

### Deviations from Plan

1. **Function name correction**: `extract_binding_info` → `_extract_single_binding` in
   DUAL_CHECK_SITES and ELIF_SITES. The plan's dispatch site inventory listed the wrong
   function name for site #4; the actual function at those line numbers is `_extract_single_binding`.

2. **Total dispatch count definition narrowed**: Plan said "8 functions have is_instance()
   calls on expression types." Implementation counts "8 functions dispatch on 2+ expression
   types" because the broader search finds 13 (including 5 single-type helper functions
   where ordering is irrelevant). This is a more meaningful guardrail.

3. **No monkeypatching needed for behavioral tests**: Plan notes 5 and 6 suggested
   monkeypatching SysideAdapter.is_instance. Instead, the SysideAdapter name-based fallback
   works directly with the dual-match mock class — no monkeypatching required. Simpler and
   more representative of real behavior.

4. **26 tests instead of ~28**: Plan estimated ~28. Actual count is 26. The difference is
   minor and all requirements are covered with at least one test each.

---

## Progress Log

### Session: 2026-02-17 -- C07 Planning
**Phase**: PLANNING
**Work done**:
- Read design intent doc 19-ast-dispatch-invariant.md (all 7 REQ-AST requirements)
- Read IMPLEMENTATION_PLAN step 1.7 and COMPONENT_CHECKLIST C07
- Read all 5 source files with dispatch sites: expression_utils.py, expression_compiler.py, hierarchy_resolver.py, usage_extractor.py, parameter_groups.py, extractor.py
- Performed comprehensive grep of all `is_instance()` calls referencing expression types -- confirmed 8 dispatch functions across 5 files, 5 dual-check sites
- Read C04 plan (complete) and C06 plan (planning) for overlap analysis
- Read existing C04 conformance test file (817 LOC) to understand static analysis approach and mock infrastructure
- Identified 5 design consistency issues (all resolved):
  1. Two dual-check sites missing invariant comment → add in build phase
  2. Two elif-chain sites non-canonical ordering → document deviation, verify critical invariant only
  3. C07 overlaps C04/C06 → intentional (cross-cutting vs. component-scoped)
  4. REQ-AST-04 is a process requirement → implement as total-count guardrail test
  5. REQ-AST-05/06/07 behavioral tests need SysIDE stubs → acceptable per Ground Rule 1
- Produced complete plan with ~28 test cases across 8 test classes
- Spike decision: SKIP (all dispatch sites identified, approach proven by C04/C06)
**Stopped at**: Plan complete, ready for review
**Next step**: Approve plan, then proceed to BUILD phase (write test file + add comments)
**Blockers**: None

### Session: 2026-02-17 -- C07 Build (TEST + BUILD + VALIDATE)
**Phase**: DONE
**Work done**:
- Wrote `tests/conformance/test_ast_dispatch_invariant.py` (26 tests in 8 classes)
- Discovered plan naming error: `extract_binding_info` → `_extract_single_binding` (corrected)
- Discovered broader search finds 13 dispatch functions (5 single-type helpers); narrowed guardrail to count 2+ type functions = 8
- TEST phase: 24 pass, 2 expected fail (REQ-AST-02 comment tests for `_extract_single_binding` and `_extract_default_value`)
- BUILD phase: Added invariant comments to `usage_extractor.py:521` and `parameter_groups.py:181`
- All 26 tests pass after comment addition
- Full suite: 1053 passed, 2 pre-existing spike failures (unrelated)
- Lint clean on test file; pre-existing lint issues in modified source files not introduced by C07
- All 4 acceptance criteria verified ✓
- All 7 requirements (REQ-AST-01 through REQ-AST-07) have passing tests ✓
- No TODOs/FIXMEs in new code ✓
- No baseline impact (comment additions are non-behavioral) ✓
**Stopped at**: VALIDATE complete, ready for commit
**Next step**: Commit, then update IMPLEMENTATION_PLAN.md
**Blockers**: None
