# Component: Dead Code Removal (7.4)

**Status**: VALIDATE
**Created**: 2026-02-20
**Last updated**: 2026-02-20
**Updated by**: Claude Opus 4.6 (build session)

## Source Documents

- **Checklist entry**: `IMPLEMENTATION_PLAN.md` — 7.4 (lines 589-613)
- **Design intent**: Research L10 (20260217-030000 §1.L10), RB-03, RB-05 (revision_backlog.md)
- **Requirements**: No formal REQ-XX-NN — this is a pure cleanup step with empirical safety criteria
- **Depends on**: C11b (done), C26/7.5 (done), 7.5a (done)

---

## 1. Assessment

### What This Component Does

Step 7.4 removes unreachable code paths identified by research spikes and conformance testing. Each removal is validated by running the full test suite — only code with zero callers AND zero coverage is eligible.

### Current State

- **TRR-identified dead code (7 items)**: All 7 checked off — removed in C08/C11b
- **Research-identified dead paths (5 items)**: 3 present, 1 already gone, 1 ambiguous
- **Phase 5+6 audit-identified dead code**: 1 dead template confirmed (D2)
- **Deferred Issue #11**: 1 buggy-but-not-dead heuristic (endswith false positive)

### Triage of Each Item

| # | Item | IMPL_PLAN Ref | Source Location | Status |
|---|------|---------------|-----------------|--------|
| A | Bare-name handling in resolve() | Research §5.#1 | Was in OutputRegistry | Already removed (C11b) |
| B | SYSML_QN normalization / Strategy B | Research §5.#5, RB-03 | `input_resolver.py:117-140` (SysMLQNLookup fn) + `dependency_backtracker.py:599-607` (Step 1b) | **LIVE — remove** |
| C | Virtual binding rewrite for bare names | Research §5.#1 | `initialization.py:317-318` (`leaf = source` fallback) | **LIVE — remove** |
| D | Step 3.6 alias enrichment heuristic | Research §1.L10 | Not found in current source | Already removed (pre-C11b restructuring) |
| E | Bare-name registration keys | Research §1.L10 | Was in build_output_registry | Already removed (C11b) |
| F | teax_module_stub.py.jinja2 | Phase 5+6 audit D2 | `templates/teax_module_stub.py.jinja2` | **LIVE — delete file** |
| G | endswith() false positive | Deferred Issue #11 | `hierarchy_resolver.py:554` | **LIVE — fix** |

**Net actionable items: 4** (B, C, F, G)

### Design Consistency Check

- [x] All acceptance criteria from IMPLEMENTATION_PLAN are testable with real data (no mocks)
- [x] AC are consistent with the research findings and empirical evidence
- [x] No contradictions with other component specs
- [x] Removals don't affect upstream/downstream interfaces (they are unreachable by definition)
- [x] Ambiguities identified and resolved (see issues below)

**Issues found during review:**

1. **Strategy B is not 100% dead — it's part of the active strategy chain.** `AGG_STRATEGIES` at `input_resolver.py:228-233` includes `SysMLQNLookup` as strategy B. The function itself (`SysMLQNLookup` at lines 105-140) has two sub-paths:
   - **Line 120**: Direct `sysml_qn_lookup()` — this IS exercised by attr_expr_probe (2 REFERENCE MODULE_OUTPUTs verified in `test_dual_resolution.py:243-246`). NOT dead.
   - **Lines 125-138**: Normalized fallback (split `::`, construct ScopedKey) — research says 100% failure rate. This sub-path is dead.
   - **Resolution**: Remove only the normalized fallback (lines 125-138), not the entire function. The direct SysML QN lookup is live.

2. **Backtracker Step 1b (`dependency_backtracker.py:599-607`) mirrors the dead sub-path.** Same `::` split → ScopedKey construction. Research says 100% failure. Safe to remove.

3. **Deferred Issue #11 (endswith false positive) is a bug fix, not dead code.** Including it here because (a) the IMPLEMENTATION_PLAN defers it to Phase 7, and (b) the fix is 1 line — fits naturally with dead code cleanup. No fixture exercises the false positive, so the fix is risk-free.

4. **The conformance test `TestStrategyB::test_sysml_qn_lookup` (test_input_resolver.py:665-690) tests the LIVE part of Strategy B** (direct SysML QN lookup), not the dead normalized fallback. No test changes needed for the removal.

### Risks & Unknowns

- **Low risk**: Every removal is either (a) a function/branch with proven 0% hit rate across all fixture models, or (b) a file with zero source references. The test suite (1780 tests) is the safety net.
- **Only risk**: If a real-world model outside our fixtures exercises the normalized SysML QN fallback. Research says this is theoretically impossible because SysIDE resolves QNs to dotted format before extraction. Mitigated by keeping the direct `sysml_qn_lookup()` path alive.

---

## 2. Spike

**Decision**: SKIP
**Rationale**: All dead code paths were identified by prior spikes (Research §5, conformance tests). The triage above resolves every ambiguity. No unknowns remain.

---

## 3. Test Plan

**Test file**: `tests/conformance/test_dead_code_removal.py`
**Fixture data**: solar_battery_model, attr_expr_probe, catf_mfe_model

This step is unique: we're removing code, not adding it. The primary validation is that the existing 1780 tests still pass. But we need a few positive tests to lock in the removals (prevent regression).

### Test Cases

| Test | Requirement | What it verifies |
|------|-------------|------------------|
| `test_teax_module_stub_template_absent` | 7.4 dead file removal | `teax_module_stub.py.jinja2` does not exist on disk |
| `test_strategy_b_no_normalized_fallback` | 7.4 Strategy B cleanup | `SysMLQNLookup` function source code does NOT contain `parts = ref.split("::")` (the normalized fallback is gone) |
| `test_backtracker_no_step_1b_normalization` | 7.4 Backtracker cleanup | `_resolve_reference_dispatch` source code does NOT contain `sanitized_part = sanitize_name(parts[-2])` |
| `test_vbr_no_bare_name_fallback` | 7.4 VBR cleanup | `_rewrite_virtual_bindings` source code does NOT contain `leaf = source  # bare name` |
| `test_alias_detection_no_endswith_false_positive` | Deferred Issue #11 fix | `hierarchy_resolver.py` alias detection uses exact match or `.` prefix, not bare `endswith()` |
| `test_strategy_b_direct_lookup_still_works` | Safety — live path preserved | `SysMLQNLookup` with a `::` ref against attr_expr_probe registry returns the correct channel (regression guard for the live path we're keeping) |

### Test Infrastructure Needed

- `inspect.getsource()` for static analysis assertions (no new fixtures needed)
- Existing `_build_registry_from_snapshot()` helper for Strategy B regression guard

### Gate: Ready for BUILD
- [x] Test file exists with all test cases written
- [x] Tests run (expected: most FAIL before removals, `test_strategy_b_direct_lookup_still_works` passes)
- [x] No test uses mocking (verified by grep)

---

## 4. Build Plan

### Files to Modify

| File | Change | Why |
|------|--------|-----|
| `src/sysml_codegen/resolution/input_resolver.py` | Remove lines 125-138 (normalized fallback in `SysMLQNLookup`). Keep lines 117-123 (direct SysML QN lookup) and the `return None` at line 140. | Research §5.#5: 100% failure rate on normalized fallback |
| `src/sysml_codegen/analysis/dependency_backtracker.py` | Remove lines 599-607 (Step 1b normalization block). Step 1 direct lookup (line 594-597) and Step 2 (line 609-611) remain. | Mirror of Strategy B dead path in backtracker |
| `src/sysml_codegen/generation/initialization.py` | In `_rewrite_virtual_bindings()` at lines 311-318, remove the `else: leaf = source` branch. Make the `if/elif` exhaustive by raising a `ValueError` if source has no `::` or `.` separator (bare names proven non-existent across all models). | Research §5.#1: zero bare-name source_paths across 94 bindings, 3 models |
| `src/sysml_codegen/extraction/hierarchy_resolver.py` | At line 554, change `sibling.source_path.endswith(agg.attribute_name)` to `(sibling.source_path == agg.attribute_name or sibling.source_path.endswith("." + agg.attribute_name))` | Deferred Issue #11: prevents false positive matching `child.total_cost` vs `total_cost` |

### Files to Delete

| File | Purpose |
|------|---------|
| `src/sysml_codegen/templates/teax_module_stub.py.jinja2` | Dead template — zero Python source references (confirmed by C21 conformance test `test_stub_template_unused`) |

### Implementation Notes

- **Order of operations**: Delete template first (zero-risk), then fix endswith (zero-risk), then remove normalized fallback (low-risk), then remove bare-name fallback (low-risk). Run full suite after each.
- **Strategy B function signature unchanged** — only the internal fallback is removed. `AGG_STRATEGIES` list unchanged. No caller changes needed.
- **Backtracker Step 1b removal**: The `_resolve_reference_dispatch` method becomes: Step 1 (direct SysML QN lookup) → Step 2 (leaf + parent scope). No renumbering needed — the comment "Step 1b" is removed with the code.
- **VBR bare-name fallback**: Replace the `else` branch with a `ValueError` raise — this is a defensive assertion, not dead code removal. If a bare name somehow appears in the future, it will fail loudly instead of silently producing wrong results. Message: `f"Unexpected bare-name source_path: {source!r}"`.

### Gate: Ready for VALIDATE
- [x] All test cases pass
- [x] No regressions in full test suite (`uv run pytest tests/`) — 1783 passed, 0 failed
- [x] Lint clean (`uv run ruff check src/`) — no new lint errors introduced

---

## 5. Validation

- [x] 4 dead code paths removed (Strategy B normalized fallback, backtracker Step 1b, VBR bare-name, teax_module_stub template)
- [x] 1 bug fixed (endswith false positive — Deferred Issue #11)
- [x] Full test suite passes (record count: 1783 tests, 0 failures, 6 xfailed)
- [x] Conformance test `test_strategy_b_direct_lookup_still_works` passes (live path preserved)
- [x] `git grep teax_module_stub` returns only test/project files (no source references)
- [x] `git grep "leaf = source"` in initialization.py returns only `leaf = source.rsplit(...)` (live paths)
- [x] IMPLEMENTATION_PLAN.md updated: 7.4 checked items, Deferred Issue #11 marked resolved
- [x] COMPONENT_CHECKLIST.md: no updates needed (7.4 is not a component)

### Baseline Impact

None. Dead code removal and the endswith fix do not change any pipeline outputs. All baselines remain unchanged.

---

## 6. Learnings

### Findings
1. **10 existing tests used bare-name source_paths in test data.** 3 were testing dead code directly (deleted), 7 were testing live override functionality with bare-name test data (updated to use dotted format). This is expected — the test data predated the research finding that bare names don't exist in real models.
2. **Removing Step 1b from backtracker left `sanitize_name` import unused.** Cleaned up the import (F401 lint fix).
3. **endswith fix introduced E501 (line too long).** Reformatted to multi-line `and` expression.
4. **Test count went from 1780 to 1783.** +6 new conformance tests, -3 deleted dead-code tests.

### Design Doc Updates Needed
| Doc | What to update | Why |
|-----|---------------|-----|
| 04-input-resolver.md | Remove Strategy B normalized fallback from the strategy description; keep direct SysML QN lookup | Code no longer has the fallback |
| 24-dual-resolution-architecture.md | Update "Stage 1b: SysML QN normalization" to note it was removed as dead code | Matches codebase |

### Cross-Component Impact
| Component | Impact | Action needed |
|-----------|--------|---------------|
| C12 (Input Resolver) | Strategy B function simplified | None — conformance tests still pass |
| C11 (Backtracker) | Step 1b removed | None — conformance tests still pass |
| C09 (VBR) | Bare-name fallback replaced with ValueError | None — no model exercises this |
| C06 (Hierarchy Resolver) | endswith fix | None — no model exercises the false positive |

### Deviations from Plan
1. **Test updates not anticipated in plan.** Plan didn't account for existing unit tests using bare-name source_paths in test data. 7 tests updated to dotted format, 3 tests deleted (tested dead code). This was a natural consequence of the VBR ValueError change.
2. **Additional file changes.** Modified `test_hierarchy_pipeline.py`, `test_rewrite_virtual_bindings.py`, `test_virtual_binding_rewrite.py`, and `test_backtracker_aggregation.py` (test data updates). These weren't in the build plan's "Files to Modify" table.

---

## 7. Commit

**Branch**: `cost-pattern-refactor` (current branch)
**Commit convention**: one commit for the whole step

- [ ] All validation checks above are green
- [ ] `git add` only the modified/deleted files + test file + IMPLEMENTATION_PLAN.md
- [ ] Commit message format:
  ```
  refactor(7.4): Dead code removal — 4 dead paths + Deferred Issue #11 fix

  - Tests: N new conformance tests in tests/conformance/test_dead_code_removal.py
  - Removed: Strategy B normalized fallback (input_resolver.py, backtracker.py)
  - Removed: VBR bare-name fallback (initialization.py) → ValueError assertion
  - Removed: teax_module_stub.py.jinja2 (zero references)
  - Fixed: endswith() false positive in alias detection (hierarchy_resolver.py)
  - Research: §5.#1, §5.#5, L10, RB-03; Deferred Issue #11
  ```
- [ ] Committed successfully

---

## Progress Log

### Session: 2026-02-20 — Planning
**Phase**: PLAN
**Work done**:
- Triaged all 12 IMPL_PLAN items: 7 already done (C08/C11b), 4 actionable, 1 already gone
- Verified live code locations for all 4 actionable items
- Confirmed Strategy B direct lookup is LIVE (attr_expr_probe exercises it) — only normalized fallback is dead
- Wrote test plan (6 tests), build plan (4 file edits + 1 deletion)
**Stopped at**: Plan complete, ready for build
**Next step**: Write tests, then execute build plan
**Blockers**: None

### Session: 2026-02-20 — Build
**Phase**: TEST → BUILD → VALIDATE
**Work done**:
- Wrote 6 conformance tests in `tests/conformance/test_dead_code_removal.py`
- Verified pre-build: 5 FAIL, 1 PASS (regression guard) — as expected
- Deleted `teax_module_stub.py.jinja2` via `git rm`
- Fixed endswith false positive in `hierarchy_resolver.py:554`
- Removed Strategy B normalized fallback in `input_resolver.py:125-138`
- Removed Step 1b normalization in `dependency_backtracker.py:599-607`
- Removed VBR bare-name fallback in `initialization.py:317-318` → ValueError
- Cleaned up unused `sanitize_name` import in `dependency_backtracker.py`
- Fixed 10 test failures: deleted 3 tests testing dead code, updated 7 tests to use dotted source_paths
- Fixed E501 lint error in hierarchy_resolver.py (endswith fix line too long)
- Full suite: 1783 passed, 0 failed, 2 skipped, 6 xfailed
- All validation checks green
- IMPLEMENTATION_PLAN.md updated: 7.4 checked off, all research items marked done
**Stopped at**: All validation complete, ready for commit
**Next step**: Commit
**Blockers**: None
