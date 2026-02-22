# Component: Extract Orchestration into `orchestration/` Package (7.1)

**Status**: DONE
**Created**: 2026-02-20
**Last updated**: 2026-02-20
**Updated by**: Claude build session for Phase 7.1

## Source Documents

- **Implementation plan entry**: `IMPLEMENTATION_PLAN.md` — Step 7.1
- **Design intent**: [02-orchestration.md](../../concepts/refactor-design-intent/02-orchestration.md)
- **Related**: C19 (Orchestrator Step Ordering), verified in Phase 5
- **Depends on**: All Phases 0–6 complete (Checkpoints 0–6 passed)

---

## 1. Assessment

### What This Step Does

Step 7.1 is a **pure structural refactor** — no behavior changes. It extracts the pipeline
orchestration logic from `generation/initialization.py` (888 lines) into a new
`orchestration/` package, reflecting that this code is coordination logic, not generation
code. The design doc (02-orchestration.md) specifies the target layout:

```
orchestration/
    __init__.py
    pipeline_builder.py          -- build_pipeline_context() + helpers
    output_registry_builder.py   -- build_output_registry()
```

### Current State

- **Source file**: `src/sysml_codegen/generation/initialization.py` (888 lines)
- **`orchestration/` package**: Does not exist yet
- **Test coverage**: 1780+ tests passing (920 conformance + 860 existing), 6 xfailed
- **Direct importers of `generation.initialization`**:
  - Production: `generation/__init__.py`, `cli/__init__.py` (via generation re-export)
  - Tests: 26+ test files (conformance + unit + integration)
  - Scripts: 15+ spike/probe/capture scripts

### Functions in `initialization.py` and Their Target Locations

| Function | Lines | Target Module |
|----------|-------|---------------|
| `SysMLParsingError` | 57–66 | **Stays** in `generation/initialization.py` |
| `CodeGenerationError` | 69–78 | **Stays** in `generation/initialization.py` |
| `PipelineContext` | 82–127 | **Stays** in `generation/initialization.py` |
| `_remove_formula_from_design_attrs()` | 129–164 | → `orchestration/pipeline_builder.py` |
| `_extract_and_filter_computed_attributes()` | 167–227 | → `orchestration/pipeline_builder.py` |
| `_extract_hierarchy_and_rewrite_bindings()` | 230–263 | → `orchestration/pipeline_builder.py` |
| `_rewrite_virtual_bindings()` | 266–333 | → `orchestration/pipeline_builder.py` |
| `find_instance_paths_for_partdef()` | 337–403 | → `orchestration/pipeline_builder.py` |
| `_build_chain_aliases()` | 406–459 | → `orchestration/pipeline_builder.py` |
| `_scope_aggregation_expressions()` | 462–514 | → `orchestration/pipeline_builder.py` |
| `build_output_registry()` | 517–703 | → `orchestration/output_registry_builder.py` |
| `build_pipeline_context()` | 706–876 | → `orchestration/pipeline_builder.py` |

**After the move, `initialization.py` retains**: exception classes + PipelineContext dataclass ≈ 80–100 lines (well under 200).

### Design Consistency Check

- [x] All acceptance criteria from IMPLEMENTATION_PLAN are testable (line count, no circular imports, grep check)
- [x] AC are consistent with the design intent doc (02-orchestration.md §Post-refactor structure)
- [x] No contradictions with other component specs
- [x] Input/output interfaces don't change — this is a pure move
- [x] Ambiguities identified and resolved (see below)

**Issues found during review:**

1. **IMPLEMENTATION_PLAN lists `_classify_entry_points()` as a function to move.** This function
   is actually in `resolution/graph_builder.py:281`, not in `initialization.py`. It's already in
   the correct layer. The implementation plan entry is inaccurate for this function.
   *Resolution*: Skip — `_classify_entry_points` stays in `resolution/graph_builder.py` where it belongs.

2. **Design doc puts `PipelineContext` in `pipeline_builder.py`, but implementation plan AC says "only PipelineContext and helpers remain" in initialization.py.**
   *Resolution*: Keep PipelineContext in `generation/initialization.py` per the AC. It serves as the
   generation layer's interface type. `orchestration/pipeline_builder.py` imports it from there.
   This avoids an import cycle and matches the AC. Moving it to orchestration is a future option.

3. **Logger name changes when functions move.** The logger `sysml_codegen.generation.initialization`
   becomes `sysml_codegen.orchestration.pipeline_builder` and
   `sysml_codegen.orchestration.output_registry_builder`. Two tests in `test_orchestrator.py`
   (lines 572, 603) reference the old logger name in `caplog.at_level()` calls.
   *Resolution*: Update the logger name references in the test.

4. **15+ spike scripts import from `generation.initialization`.**
   *Resolution*: Update scripts alongside test files. Scripts are part of the repo and should
   use canonical import paths. Re-exports in `generation/initialization.py` for moved functions
   would satisfy the import but violate AC3.

5. **`generation/__init__.py` re-exports `build_pipeline_context` and `PipelineContext` as public API.**
   *Resolution*: Update `generation/__init__.py` to import `build_pipeline_context` from
   `orchestration.pipeline_builder` instead of `generation.initialization`. The public API
   (`from sysml_codegen.generation import build_pipeline_context`) continues to work.
   `PipelineContext` stays imported from `initialization` since it still lives there.

### Risks & Unknowns

- **Volume of import updates**: 40+ files need import path changes. Risk of typos or missed files.
  Mitigation: `git grep` verification after changes + full test suite.
- **Circular imports**: `orchestration/` imports from `generation/initialization` (PipelineContext)
  while `generation/__init__` re-exports from `orchestration/`. This is safe because
  `generation/initialization.py` does NOT import from `orchestration/`.
- **No behavior risk**: This is pure structural refactoring. All 1780+ tests serve as the safety net.

---

## 2. Spike

**Decision**: SKIP
**Rationale**: The design is clear and the existing code confirms the boundaries. Every function to
move is self-contained. The only question (circular imports) is analyzed above and confirmed safe
by tracing the import graph: `orchestration.pipeline_builder` → `generation.initialization`
(PipelineContext) and `generation.__init__` → `orchestration.pipeline_builder`
(build_pipeline_context). No cycle exists because `generation.initialization` does not
import from `orchestration/` or `generation.__init__`.

---

## 3. Test Plan

**Test file**: No new test file — all 1780+ existing tests serve as regression coverage.
**Structural assertions**: Added to existing test infrastructure.

### Test Cases

Since this is a pure structural refactor, the test strategy is:

| Test | What it verifies |
|------|------------------|
| Full test suite green | `uv run pytest tests/` — all 1780+ tests pass, 0 failures |
| AC1: `initialization.py` line count | `wc -l initialization.py` < 200 |
| AC2: No circular imports | `python -c "from sysml_codegen.orchestration import pipeline_builder"` succeeds |
| AC3: Import grep | `git grep 'from.*initialization import'` returns only PipelineContext/exception imports |
| Lint clean | `uv run ruff check src/` — no errors |

### Gate: Ready for BUILD
- [x] Acceptance criteria understood
- [x] Full test suite baseline captured (1783 tests, 2 skipped, 6 xfailed)

---

## 4. Build Plan

### Step 1: Create `orchestration/` Package

| File | Purpose |
|------|---------|
| `src/sysml_codegen/orchestration/__init__.py` | Package init with public API re-exports |
| `src/sysml_codegen/orchestration/pipeline_builder.py` | `build_pipeline_context()` + all Step 3.5/4.5 helpers |
| `src/sysml_codegen/orchestration/output_registry_builder.py` | `build_output_registry()` |

### Step 2: Move Functions

**`orchestration/pipeline_builder.py`** receives:
- `build_pipeline_context()` (line 706–876)
- `_extract_hierarchy_and_rewrite_bindings()` (line 230–263)
- `_rewrite_virtual_bindings()` (line 266–333)
- `find_instance_paths_for_partdef()` (line 337–403)
- `_build_chain_aliases()` (line 406–459)
- `_scope_aggregation_expressions()` (line 462–514)
- `_extract_and_filter_computed_attributes()` (line 167–227)
- `_remove_formula_from_design_attrs()` (line 129–164)

**`orchestration/output_registry_builder.py`** receives:
- `build_output_registry()` (line 517–703)

Each module gets its own imports (copied from `initialization.py`, trimmed to what's needed)
plus an import of `PipelineContext`, `SysMLParsingError`, `CodeGenerationError` from
`sysml_codegen.generation.initialization`.

### Step 3: Trim `generation/initialization.py`

Remove moved functions. Remaining contents:
- Module docstring
- `SysMLParsingError` class
- `CodeGenerationError` class
- `PipelineContext` dataclass
- `__all__` listing only the 3 remaining symbols

Imports trimmed to only what PipelineContext needs.

### Step 4: Update `orchestration/__init__.py`

Re-export public API:
```python
from sysml_codegen.orchestration.pipeline_builder import (
    build_pipeline_context,
    find_instance_paths_for_partdef,
    _rewrite_virtual_bindings,
    _build_chain_aliases,
    _scope_aggregation_expressions,
    _remove_formula_from_design_attrs,
)
from sysml_codegen.orchestration.output_registry_builder import (
    build_output_registry,
)
```

### Step 5: Update `generation/__init__.py`

Change import of `build_pipeline_context` from `generation.initialization` to
`sysml_codegen.orchestration.pipeline_builder`. Keep `PipelineContext`,
`SysMLParsingError`, `CodeGenerationError` imported from `generation.initialization`.

### Step 6: Update All Import Sites

Every file that imports moved functions from `generation.initialization` must be updated
to import from `sysml_codegen.orchestration.pipeline_builder` or
`sysml_codegen.orchestration.output_registry_builder`.

**Production code** (2 files):
| File | Change |
|------|--------|
| `generation/__init__.py:31-36` | Import `build_pipeline_context` from `orchestration.pipeline_builder` |
| `cli/__init__.py:1033-1037` | Already uses `from sysml_codegen.generation import ...` — no change needed if generation re-exports |

**Conformance tests** (14 files):
| File | Import(s) to Update |
|------|---------------------|
| `test_aggregation_scoping.py:32-37` | `_build_chain_aliases`, `_scope_aggregation_expressions`, `build_output_registry`, `find_instance_paths_for_partdef` |
| `test_backtracker.py:40` | `build_output_registry` |
| `test_dead_code_removal.py:17,97` | `build_output_registry`, `_rewrite_virtual_bindings` |
| `test_dual_resolution.py:27` | `build_output_registry` |
| `test_entry_point_classifier.py:38` | `build_output_registry` |
| `test_factory_aggregation.py:41` | `build_output_registry` |
| `test_factory_calc_usage.py:32` | `build_output_registry` |
| `test_factory_formula.py:38` | `build_output_registry` |
| `test_input_resolver.py:29` | `build_output_registry` |
| `test_orchestrator.py:34-39` | `_remove_formula_from_design_attrs`, `_scope_aggregation_expressions`, `build_output_registry`, `build_pipeline_context` + logger name at lines 572, 603 |
| `test_output_registry.py:25` | `build_output_registry` |
| `test_pipeline_e2e.py` | Check if imports from initialization |
| `test_virtual_binding_rewrite.py:34` | `_rewrite_virtual_bindings` |

**Unit tests** (7 files):
| File | Import(s) to Update |
|------|---------------------|
| `test_alias_producers.py:551,629+` | `find_instance_paths_for_partdef`, `_build_chain_aliases` |
| `test_backtracker_aggregation.py:31` | `build_output_registry` |
| `test_backtracker_computed_attrs.py:36` | `build_output_registry` |
| `test_hierarchy_pipeline.py:23` | Multiple from initialization |
| `test_output_registry_construction.py:37,670,692,753` | `build_output_registry`, `build_pipeline_context` |
| `test_parameter_groups.py:99` | `build_pipeline_context` |
| `test_rewrite_virtual_bindings.py:14` | `_rewrite_virtual_bindings` |
| `test_step_4_5.py:72,103,125,152,175,212` | Multiple from initialization |

**Integration tests** (6 files):
| File | Import(s) to Update |
|------|---------------------|
| `test_bug2_regression.py:20` | `build_pipeline_context` |
| `test_computed_attribute_pipeline.py:44` | `build_output_registry`, `_remove_formula_from_design_attrs` |
| `test_e2e_output_registry.py:17` | `build_pipeline_context` |
| `test_hierarchy_e2e.py:15` | `PipelineContext` stays, `build_pipeline_context` moves |
| `test_output_registry_smoke.py:19` | `build_pipeline_context` |
| `test_parallel_validation.py:18` | `build_output_registry`, `build_pipeline_context` |

**Scripts** (13+ files):
All `scripts/*.py` and `scripts/spikes/*.py` files that import from `generation.initialization`.
Update to import from `orchestration` modules.

### Step 7: Update Logger Name References

In `tests/conformance/test_orchestrator.py`:
- Line 572: `logger="sysml_codegen.generation.initialization"` → `"sysml_codegen.orchestration.pipeline_builder"`
- Line 603: Same change

### Implementation Notes

1. **Import pattern**: Use `from sysml_codegen.orchestration.pipeline_builder import X` for
   functions that moved to pipeline_builder. Use
   `from sysml_codegen.orchestration.output_registry_builder import build_output_registry`
   for the registry builder. This is the canonical pattern — do NOT import from `orchestration/__init__.py`
   except in `generation/__init__.py` for re-export.

2. **Late imports**: `build_pipeline_context()` has a late import of `SysMLDataExtractor`
   (line 738) and `_extract_and_filter_computed_attributes()` has a late import of
   `extract_computed_attributes` (line 186). These must be preserved in the moved code.

3. **`__all__` lists**: Update in `initialization.py` (trim to 3 symbols) and add in new modules.

4. **Order of operations**: Create new files first, then update imports, then trim initialization.py.
   This way git can track the move and tests remain green during the transition.

5. **`_extract_and_filter_computed_attributes` and `_extract_hierarchy_and_rewrite_bindings`**
   are private to `build_pipeline_context()` — they are only called from there. They are NOT
   imported by any test or external file. Move them alongside `build_pipeline_context()`.

### Gate: Ready for VALIDATE
- [x] All test cases pass
- [x] No regressions in full test suite (`uv run pytest tests/`) — 1783 passed, 2 skipped, 6 xfailed
- [x] Lint clean (`uv run ruff check src/sysml_codegen/orchestration/`)

---

## 5. Validation

- [x] `generation/initialization.py` line count < 200 (109 lines)
- [x] `python -c "from sysml_codegen.orchestration import pipeline_builder"` succeeds
- [x] `python -c "from sysml_codegen.orchestration import output_registry_builder"` succeeds
- [x] No circular imports: `python -c "from sysml_codegen.generation import PipelineContext"` succeeds (build_pipeline_context removed from generation re-exports to avoid circular import)
- [x] `git grep 'from.*generation\.initialization import'` — only imports of `PipelineContext`, `SysMLParsingError`, `CodeGenerationError`
- [x] `git grep 'from.*generation import.*build_pipeline_context'` — none (removed from re-exports; cli uses direct orchestration import)
- [x] Full test suite passes (1783 tests, 0 failures, 2 skipped, 6 xfailed)
- [x] `uv run ruff check src/sysml_codegen/orchestration/` — no lint errors
- [x] IMPLEMENTATION_PLAN checkbox for 7.1 updated

### Baseline Impact

None. This is a pure structural refactor — no output baselines change.

---

## 6. Learnings

### Findings
1. **Circular import via `generation/__init__.py` re-export.** The plan predicted no cycle because
   `generation.initialization` doesn't import from `orchestration/`. But Python's package init
   semantics mean importing `generation.initialization` triggers `generation/__init__.py`, which
   imported `build_pipeline_context` from `orchestration.pipeline_builder` — creating a cycle.
   **Fix**: Removed `build_pipeline_context` from `generation/__init__.py` re-exports. `cli/__init__.py`
   now imports directly from `sysml_codegen.orchestration.pipeline_builder`.

2. **Two static analysis tests inspected `initialization` module source.** `test_virtual_binding_rewrite.py`
   lines 696 and 737 used `inspect.getsource(initialization)` to verify call ordering. Updated to
   inspect `orchestration.pipeline_builder` instead.

3. **Two unused imports in pipeline_builder.py.** `BacktrackingResult` and `Compilability` were
   imported in the original but only used transitively. Removed to satisfy ruff.

4. **Stale spike scripts reference `_enrich_aliases_from_bindings`.** Three scripts
   (`spike_issue22_agg_ref.py`, `spike_output_registry_e2e.py`, `spike_reference_resolution.py`)
   imported a function that no longer exists. Import was removed during update.

5. **`capture_extraction_snapshots.py` imported `extract_calculation_usages` and
   `extract_design_attributes` via `initialization.py`** — they were re-exported implicitly.
   Updated to import from their actual source modules.

### Design Doc Updates Needed
| Doc | What to update | Why |
|-----|---------------|-----|
| 02-orchestration.md | Update "Post-refactor structure" if PipelineContext placement differs from spec | PipelineContext stays in initialization.py per AC |

### Cross-Component Impact
| Component | Impact | Action needed |
|-----------|--------|---------------|
| 7.4 (dead code) | May reference `generation.initialization` import paths | Update any 7.4 work to use orchestration paths |
| 7.6 (generation ComputationGraph) | Will import from orchestration instead | No blocker — pure refactor |

### Deviations from Plan
1. **`build_pipeline_context` NOT re-exported from `generation/__init__.py`** — plan Step 5 said to
   re-export, but this created a circular import. Instead, `cli/__init__.py` imports directly from
   `sysml_codegen.orchestration.pipeline_builder`. The public API change is: callers must use
   `from sysml_codegen.orchestration.pipeline_builder import build_pipeline_context` instead of
   `from sysml_codegen.generation import build_pipeline_context`.

2. **`_enrich_aliases_from_bindings` removed from spike script imports** — function doesn't exist
   in codebase; was already dead code in those scripts.

---

## 7. Commit

**Branch**: `cost-pattern-refactor` (continuing on current branch)
**Commit convention**: one commit for the structural move

- [ ] All validation checks above are green
- [ ] `git add` only the files listed in Build Plan + modified test/script files
- [ ] Commit message format:
  ```
  refactor(7.1): Extract orchestration into orchestration/ package

  - Move build_pipeline_context() + helpers to orchestration/pipeline_builder.py
  - Move build_output_registry() to orchestration/output_registry_builder.py
  - Update all import paths across src/, tests/, scripts/
  - generation/initialization.py retains PipelineContext + exception classes only
  - Design intent: 02-orchestration.md
  ```
- [ ] Committed successfully

---

## Progress Log

### Session: 2026-02-20 — Planning
**Phase**: PLANNING
**Work done**:
- Read IMPLEMENTATION_PLAN step 7.1 and all AC
- Read design intent doc 02-orchestration.md (post-refactor structure)
- Read full `generation/initialization.py` (888 lines, 11 functions)
- Catalogued all 40+ import sites across production code, tests, and scripts
- Identified 5 design consistency issues and documented resolutions
- Confirmed `_classify_entry_points()` is already in `resolution/graph_builder.py` (plan inaccuracy)
- Confirmed no circular import risk via import graph analysis
- Spike SKIPPED — design is clear, no unknowns
**Stopped at**: Plan complete, ready for review
**Next step**: Build — create orchestration/ package, move functions, update imports
**Blockers**: None

### Session: 2026-02-20 — Build
**Phase**: BUILD → VALIDATE
**Work done**:
- Captured test baseline: 1783 passed, 2 skipped, 6 xfailed
- Created `orchestration/` package with 3 files:
  - `__init__.py` — public API re-exports
  - `pipeline_builder.py` — `build_pipeline_context()` + 7 helpers
  - `output_registry_builder.py` — `build_output_registry()`
- Trimmed `generation/initialization.py` from 888 → 109 lines (PipelineContext + 2 exceptions)
- Updated `generation/__init__.py` — removed `build_pipeline_context` re-export (circular import fix)
- Updated `cli/__init__.py` — direct import from `orchestration.pipeline_builder`
- Updated 40+ test files (conformance, unit, integration) import paths
- Updated 13+ script files import paths
- Fixed 2 static analysis tests that inspected moved source code
- Fixed 2 lint errors (unused imports in pipeline_builder.py)
- Removed stale `_enrich_aliases_from_bindings` imports from 3 spike scripts
- All 1783 tests pass, 0 failures, 2 skipped, 6 xfailed
- All validation checks in section 5 pass
**Stopped at**: VALIDATE phase — all checks green
**Next step**: Update IMPLEMENTATION_PLAN, commit
**Blockers**: None
