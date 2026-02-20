# Component: Consolidate Naming Utilities into `core/` (7.3)

**Status**: DONE
**Created**: 2026-02-20
**Last updated**: 2026-02-20
**Updated by**: Claude build session for Phase 7.3

## Source Documents

- **Implementation plan entry**: `IMPLEMENTATION_PLAN.md` -- Step 7.3
- **Design intent**: [15-naming-conventions.md](../../concepts/refactor-design-intent/15-naming-conventions.md)
- **Related**: C02 (Naming Convention Conformance, Phase 1.2 -- 46 tests)
- **Depends on**: Phases 0-6 complete (Checkpoints 0-6 passed). Step 7.1 (orchestration extraction) is effectively complete (`orchestration/` exists, `initialization.py` at 109 lines). Step 7.2 (`resolution/input_resolver.py`) exists.
- **Deferred Issues in scope**: #5 (Two BindingInfo classes), #6 (Three expression reconstruction impls)

---

## 1. Assessment

### What This Step Does

Step 7.3 is a **pure structural refactor** -- no behavior changes. It eliminates the
backward-compatibility shim modules (`analysis/qualified_names.py`, `resolution/identifier_types.py`)
and their re-exports, consolidating all naming and identifier utilities into `core/`. It also
evaluates and addresses Deferred Issues #5 (two BindingInfo classes) and #6 (three expression
reconstruction impls).

### Current State

The consolidation is **partially done**. The real implementations already live in `core/`:

| File | Role | Status |
|------|------|--------|
| `core/qualified_names.py` | All naming functions (sanitize, EQN, PQN, module, channel) | **Authoritative** (133 lines) |
| `core/identifier_types.py` | NewType wrappers + dataclass types + derive functions | **Authoritative** (198 lines) |
| `analysis/qualified_names.py` | Re-export shim to `core/qualified_names` | **To delete** (27 lines) |
| `resolution/identifier_types.py` | Re-export shim to `core/identifier_types` | **To delete** (23 lines) |

**Import analysis:**

| Shim file | Direct importers in `src/` | Direct importers in `tests/` |
|-----------|---------------------------|------------------------------|
| `analysis/qualified_names.py` | 0 (zero -- all callers already migrated to core) | 0 |
| `resolution/identifier_types.py` | 4 production files (`generation/modules.py`, `generation/registry.py`, `generation/stencils.py`, `cli/__init__.py` x2), 1 internal (`generation/test_gen.py`) | 3 test files (`test_gen_module_wrappers.py`, `test_gen_stencils.py`, `test_gen_registry.py`) |

**Package-level re-exports to clean up:**

| Package `__init__.py` | Re-exports from | Consumers |
|------------------------|-----------------|-----------|
| `analysis/__init__.py` lines 27-31 | `core.qualified_names` (`sanitize_name`, `sysml_to_python_qualified_name`) | 0 external consumers |
| `resolution/__init__.py` lines 12-20 | `core.identifier_types` (6 symbols) | 0 external consumers |
| `core/__init__.py` lines 18-44 | Both `core/qualified_names.py` and `core/identifier_types.py` | Kept (this IS the canonical core package) |

### Deferred Issue #5: Two BindingInfo Classes

**Finding: NOT a consolidation target for 7.3.**

- **Local**: `extraction/usage_extractor.py:49` -- `@dataclass` with 8 fields + `expression_ast` + 2 properties. Used by extraction logic to create binding records from SysIDE AST. Has AST element references (`source_instance_elem`, `source_attribute_elem`).
- **Upstream**: `agentic_mbse.sysml.types:170` -- `BaseModel` (Pydantic). Has `references: list` field. Used by the backtracker only under `TYPE_CHECKING`.

These are different classes in different packages with different base types (dataclass vs Pydantic), different field sets, and different purposes. The local one carries AST element references needed for extraction; the upstream one is the shared interface type. Consolidating them would require cross-package changes to `agentic-mbse` or a breaking change to the local class hierarchy.

**Resolution**: Document as out-of-scope for 7.3. The upstream `BindingInfo` is only used for type annotations (`TYPE_CHECKING`), not runtime logic. The naming collision is confusing but harmless. A future cross-package refactor could unify them.

### Deferred Issue #6: Three Expression Reconstruction Impls

**Finding: Already resolved -- only ONE implementation exists.**

The codebase has a single `reconstruct_expression()` in `extraction/expression_utils.py:34`, used by 4 callers (hierarchy_resolver, constraint_extractor, extractor, computed_attribute_extractor). The "three impls" issue was likely overstated in the original research, or prior duplicates were already removed during earlier refactoring.

`compile_expression()` in `expression_compiler.py` is a *different* concern (SysIDE AST -> Python source code) -- not a reconstruction duplicate.

**Resolution**: No action needed. Already a single source of truth.

### Design Consistency Check

- [x] All acceptance criteria from COMPONENT_CHECKLIST are testable with real data (no mocks)
- [x] AC are consistent with the requirements in the design intent doc (15-naming-conventions.md)
- [x] No contradictions with other component specs
- [x] Input/output interfaces match what upstream/downstream components expect
- [x] Any ambiguities or gaps identified and resolved (documented below)

**Issues found during review:**

1. **analysis/__init__.py re-exports**: Lines 27-31 re-export `sanitize_name` and `sysml_to_python_qualified_name` from core. Zero external consumers use these. Removing them is safe but changes the public API of the `analysis` package. Since this is an internal package, the removal is acceptable.

2. **resolution/__init__.py re-exports**: Lines 12-20 re-export 6 identifier type symbols from core. Zero consumers use them via the `resolution` package. Removing them is safe.

3. **Deferred Issues #5 and #6 are not naming-consolidation work**: Both are documented as resolved/out-of-scope above.

### Risks & Unknowns

- **Low risk**: This is a mechanical import rewrite. The shim files exist solely for backward compatibility, and all internal callers except 9 files have already migrated.
- **No unknowns**: The exact set of files to change is fully enumerated.

---

## 2. Spike

**Decision**: SKIP
**Rationale**: The design is completely clear. The shim files are trivial re-exports. The import changes are mechanical (9 files). No unknowns exist -- every importer is enumerated, every target import path is known. The 46 C02 naming convention tests plus 1780+ total tests provide comprehensive regression coverage.

---

## 3. Test Plan

**Test file**: No new test file needed. Existing `tests/conformance/test_naming_conventions.py` (46 tests) already imports from `core/qualified_names` and `core/identifier_types`. After the shim deletion, these tests verify the canonical import path works.

**Validation approach**: Full test suite run. If any test fails, it means an import was missed.

### Test Cases

| Test | Requirement | What it verifies |
|------|-------------|------------------|
| Existing 46 naming tests | REQ-NC-01 through REQ-NC-07 | All naming functions importable from `core/` and produce correct results |
| Full suite (1780+ tests) | AC: No regressions | No import breaks from shim deletion |

### Post-Refactor Verification

| Check | Method |
|-------|--------|
| No imports from `analysis.qualified_names` | `git grep 'from sysml_codegen.analysis.qualified_names import'` returns empty |
| No imports from `resolution.identifier_types` | `git grep 'from sysml_codegen.resolution.identifier_types import'` returns empty |
| No re-exports of naming in `analysis/__init__.py` | Manual review |
| No re-exports of identifier_types in `resolution/__init__.py` | Manual review |
| Shim files deleted | `ls analysis/qualified_names.py resolution/identifier_types.py` fails |
| No duplicate function definitions | `grep -r 'def sanitize_name\|def derive_module_type\|def make_scoped_key' src/ | wc -l` returns exactly 1 per function |

### Test Infrastructure Needed
None.

### Gate: Ready for BUILD
- [x] Test plan reviewed
- [x] No test uses mocking

---

## 4. Build Plan

### Files to Delete

| File | Why |
|------|-----|
| `src/sysml_codegen/analysis/qualified_names.py` | Shim with zero direct importers. AC: "analysis/qualified_names.py deleted" |
| `src/sysml_codegen/resolution/identifier_types.py` | Shim with 9 importers (all migrated below). AC: "resolution/identifier_types.py deleted" |

### Files to Modify

| File | Change | Why |
|------|--------|-----|
| `src/sysml_codegen/generation/modules.py:20` | `from sysml_codegen.resolution.identifier_types import ...` -> `from sysml_codegen.core.identifier_types import ...` | Migrate off shim |
| `src/sysml_codegen/generation/registry.py:31` | Same migration | Migrate off shim |
| `src/sysml_codegen/generation/test_gen.py:19` | Same migration | Migrate off shim |
| `src/sysml_codegen/generation/stencils.py:32` | Same migration | Migrate off shim |
| `src/sysml_codegen/cli/__init__.py:184,624` | Both imports: `from sysml_codegen.resolution.identifier_types import ...` -> `from sysml_codegen.core.identifier_types import ...` | Migrate off shim (2 locations) |
| `tests/conformance/test_gen_module_wrappers.py:37` | Same migration | Migrate off shim |
| `tests/conformance/test_gen_stencils.py:46` | Same migration | Migrate off shim |
| `tests/conformance/test_gen_registry.py:32` | Same migration | Migrate off shim |
| `src/sysml_codegen/analysis/__init__.py:27-31` | Remove `from sysml_codegen.core.qualified_names import ...` re-export block and corresponding `__all__` entries (`sanitize_name`, `sysml_to_python_qualified_name`) | Remove unnecessary re-export; zero consumers |
| `src/sysml_codegen/resolution/__init__.py:12-20` | Remove `from sysml_codegen.core.identifier_types import ...` re-export block and corresponding `__all__` entries (6 symbols) | Remove unnecessary re-export; zero consumers |

### Files NOT Changed

| File | Why kept |
|------|----------|
| `src/sysml_codegen/core/__init__.py` | Canonical re-export location. Kept as-is. |
| `src/sysml_codegen/core/qualified_names.py` | Authoritative implementation. No changes needed. |
| `src/sysml_codegen/core/identifier_types.py` | Authoritative implementation. No changes needed. |

### Implementation Notes

1. **Order matters**: Update all imports first, then delete shim files. This prevents intermediate states where imports break.
2. **cli/__init__.py has lazy imports**: The two import sites (lines 184 and 624) are inside functions, not at module level. The migration is the same -- just change the `from` path.
3. **`resolution/__init__.py` still has `models` re-exports**: After removing the identifier_types re-exports, this file still exports `BindingResolution`, `ComputationGraph`, `PipelineModule`, etc. from `resolution.models`. Those stay.
4. **`analysis/__init__.py` still exports backtracker, parameter_groups, etc.**: Only the `core.qualified_names` re-exports are removed. Everything else stays.
5. **No behavior changes**: Every import path change points to the same underlying functions. This is purely a one-hop shortcut removal.

### Gate: Ready for VALIDATE
- [x] All test cases pass
- [x] No regressions in full test suite (`uv run pytest tests/`) — 1783 passed, 2 skipped, 6 xfailed
- [x] Lint clean (`uv run ruff check src/`) — all modified files pass

---

## 5. Validation

- [x] `analysis/qualified_names.py` deleted
- [x] `resolution/identifier_types.py` deleted
- [x] Single import path for all naming functions: `from sysml_codegen.core.qualified_names import ...`
- [x] Single import path for all identifier types: `from sysml_codegen.core.identifier_types import ...`
- [x] No duplicate function definitions across modules
- [x] `git grep 'from sysml_codegen.analysis.qualified_names import'` returns empty
- [x] `git grep 'from sysml_codegen.resolution.identifier_types import'` returns empty
- [x] Full test suite passes (record count: 1783 tests, 0 failures)
- [x] Deferred Issue #5 documented as out-of-scope with rationale
- [x] Deferred Issue #6 documented as already-resolved

### Baseline Impact
None. This is a pure import restructuring with no behavior changes. No baselines affected.

---

## 6. Learnings

### Findings

1. **Completely mechanical refactor — zero surprises.** Every import target enumerated in the plan was correct. No hidden importers were discovered.
2. **Import sorting (I001) required after migration.** Changing `resolution.identifier_types` to `core.identifier_types` moved the import earlier alphabetically, triggering ruff I001 in 6 files. Fixed with `ruff check --fix`.
3. **analysis/qualified_names.py had zero importers.** The shim was already fully orphaned — no code changes needed before deletion. The `analysis/__init__.py` re-exports were the only remaining references.

### Design Doc Updates Needed
| Doc | What to update | Why |
|-----|---------------|-----|
| (none anticipated) | | Import paths in doc 15 already reference `core/` |

### Cross-Component Impact
| Component | Impact | Action needed |
|-----------|--------|---------------|
| Deferred Issue #5 | BindingInfo consolidation is cross-package (agentic-mbse), not naming-layer work | Document in IMPLEMENTATION_PLAN as a separate future item |
| Deferred Issue #6 | Already resolved -- single `reconstruct_expression()` in `expression_utils.py` | Mark as resolved in IMPLEMENTATION_PLAN |

### Deviations from Plan
None. All changes exactly matched the build plan.

---

## 7. Commit

**Branch**: `cost-pattern-refactor`
**Commit convention**: one commit per component, message references step

- [x] All validation checks above are green
- [x] `git add` only the modified/deleted files listed in Build Plan
- [x] Commit message format:
  ```
  refactor(7.3): Consolidate naming utilities — delete shims, unify imports to core/

  - Deleted: analysis/qualified_names.py, resolution/identifier_types.py (backward-compat shims)
  - Updated: 9 files migrated from resolution.identifier_types -> core.identifier_types
  - Cleaned: analysis/__init__.py and resolution/__init__.py re-exports removed
  - Deferred Issue #5 (BindingInfo): out-of-scope (cross-package concern)
  - Deferred Issue #6 (expression reconstruction): already resolved (single impl)
  ```
- [x] Committed successfully (`cdbc7f1`)

---

## Progress Log

### Session: 2026-02-20 -- Planning
**Phase**: PLANNING
**Work done**:
- Read IMPLEMENTATION_PLAN.md step 7.3, COMPONENT_CHECKLIST.md C02, 15-naming-conventions.md
- Read all 4 source files: core/qualified_names.py, core/identifier_types.py, analysis/qualified_names.py, resolution/identifier_types.py
- Mapped all importers: 0 for analysis shim, 9 for resolution shim
- Mapped package __init__.py re-exports: analysis (2 symbols, 0 consumers), resolution (6 symbols, 0 consumers)
- Investigated Deferred Issue #5 (two BindingInfo): different packages, different base types, TYPE_CHECKING only -- out of scope
- Investigated Deferred Issue #6 (three expression reconstruction): only one impl exists in expression_utils.py -- already resolved
- Checked C02 naming-conventions learnings: all naming functions work correctly, 46 conformance tests
**Stopped at**: Plan complete, ready for build
**Next step**: Execute the build plan (update 9 imports, clean 2 __init__.py files, delete 2 shim files, run tests)
**Blockers**: None

### Session: 2026-02-20 -- Build + Validate
**Phase**: BUILD → VALIDATE → DONE
**Work done**:
- Migrated 9 import sites from `resolution.identifier_types` → `core.identifier_types` (5 production, 1 internal, 3 test files)
- Removed `analysis/__init__.py` re-exports (2 symbols: `sanitize_name`, `sysml_to_python_qualified_name`) and docstring reference
- Removed `resolution/__init__.py` re-exports (6 symbols: `ElementQualifiedName`, `ModuleType`, `PythonModulePath`, `SysMLQualifiedName`, `derive_module_type`, `derive_python_path`)
- Deleted 2 shim files via `git rm`: `analysis/qualified_names.py`, `resolution/identifier_types.py`
- Fixed import sorting (ruff I001) in 6 files via `ruff check --fix`
- Verified: `git grep` returns empty for both old import paths
- Full test suite: 1783 passed, 2 skipped, 6 xfailed, 0 failures
- Lint clean on all modified files
- All validation checkboxes checked
**Stopped at**: Complete. Ready for commit.
**Next step**: Commit with prescribed message
**Blockers**: None
