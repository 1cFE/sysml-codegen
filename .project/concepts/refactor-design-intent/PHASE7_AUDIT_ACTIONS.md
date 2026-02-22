# Phase 7 Checkpoint Audit — Action Items

**Audit date**: 2026-02-20
**Auditor**: Claude Opus 4.6 (Phase 7 checkpoint review)
**Scope**: Phase 7 (7.1–7.7) structural refactoring + end-to-end codegen readiness
**Branch**: `cost-pattern-refactor`

---

## Executive Summary

Phase 7 is **nearly complete** with 6 of 7 sub-steps done and committed (7.1, 7.3, 7.4,
7.5/C26, 7.5a, 7.7). Step 7.6 (generation boundary enforcement) has completed its BUILD
phase — all 20 boundary tests pass, all 7 integration test failures have been fixed, and
the full suite is green. 7.6 is ready for VALIDATE.

**Current test suite**: 1810 passed, 4 skipped, 6 xfailed, **0 failed**.

**Key conclusions**:
1. Phase 7 is blocked only on 7.6 VALIDATE + commit.
2. End-to-end codegen DOES work and IS tested (integration tests pass).
3. Step 7.2 is effectively already done but not documented as such.
4. Zero generation/ files import from extraction/analysis (REQ-PIPE-07 satisfied).

---

## A. Completion Status by Sub-Step

### Completed & Committed

| Step | What | Commit | Tests Added | Status |
|------|------|--------|-------------|--------|
| 7.1 | Extract orchestration into `orchestration/` | `bd80342` | 0 (structural move; existing 1783 pass) | DONE |
| 7.3 | Consolidate naming utilities into `core/` | `cdbc7f1` | 0 (structural move; 1783 pass) | DONE |
| 7.4 | Dead code removal | `ef7abc9` | +6 conformance | DONE |
| 7.5 (C26) | PipelineModule field expansion | `441f566` | +27 conformance | DONE |
| 7.5a | Fix aggregation module_type | (earlier commit) | 0 (baseline updates) | DONE |

### Completed & Committed (since audit)

| Step | What | Commit | Status |
|------|------|--------|--------|
| **7.7** | Factory purity refactor | `fd119ba` | DONE |

### BUILD Complete, Awaiting VALIDATE + Commit

| Step | What | Status | Concern |
|------|------|--------|---------|
| **7.6** | Generation boundary enforcement | BUILD complete — all 20 boundary tests pass, 7 integration tests fixed, full suite green (1810 passed). Ready for VALIDATE. | Needs validation checklist walkthrough + commit. |

### Effectively Done (Needs Documentation Update)

| Step | What | Status | Concern |
|------|------|--------|---------|
| **7.2** | Extract input resolver into `resolution/input_resolver.py` | `input_resolver.py` already exists (10,793 bytes, created during C12/Phase 3.2). `resolve_input()` not inlined in `graph_builder.py` (confirmed by grep). | **IMPLEMENTATION_PLAN checkbox is `[ ]` — should be `[x]`.** |

---

## B. Bookkeeping Gaps

### B1. Step 7.2 Not Marked Complete

`IMPLEMENTATION_PLAN.md` line 572 reads:
```
- [ ] **7.2 — Extract input resolver into `resolution/input_resolver.py`**
```

This is effectively done. `resolution/input_resolver.py` was created as part of C12 (Phase 3.2,
completed 2026-02-17). `graph_builder.py` has zero `resolve_input` references (confirmed by
grep). The file contains `resolve_input()`, `ResolutionContext`, 4 strategy callables, and
`AGG_STRATEGIES` — exactly what the step specifies.

**Action**: Check the `[x]` box and add completion note: "Already done — created during
C12 (Phase 3.2). `resolve_input()` is in `resolution/input_resolver.py`, not inlined in
`graph_builder.py`."

### B2. ~~Step 7.7 Uncommitted Work~~

**RESOLVED**: 7.7 committed as `fd119ba`.

### B3. Step 7.3 Unchecked AC

`IMPLEMENTATION_PLAN.md` line 586 reads:
```
    - [ ] No duplicate function definitions across modules
```

But the 7.3 plan.md Validation section (line 191) says:
```
- [x] No duplicate function definitions across modules
```

**Action**: Check the `[x]` in IMPLEMENTATION_PLAN to match the plan.md validation result.

### B4. Step 7.3 Unchecked Consolidation Candidates

Lines 588-589:
```
    - [ ] Two `BindingInfo` classes consolidated
    - [ ] Three expression reconstruction implementations consolidated
```

The 7.3 plan.md documents:
- Deferred Issue #5 (BindingInfo): **Out of scope** — cross-package concern
- Deferred Issue #6 (expression reconstruction): **Already resolved** — single impl exists

These should be struck through or marked as N/A with rationale, not left as open checkboxes.

**Action**: Update to reflect out-of-scope/resolved status. Also update Deferred Issues table
(line 714-715) which already has the correct status.

### B5. Phase 7 Test Count in Summary Table

Line 674 reads:
```
| 7 | Refactor | Structural cleanup, dead code gone, PipelineModule expanded (C26), factory purity (7.7) | 10 (actual: 7.7 purity: 10) |
```

This undercounts. Phase 7 actual new tests:
- 7.4 dead code removal: **6** conformance tests
- 7.5 C26 PipelineModule expansion: **27** conformance tests
- 7.7 factory purity: **10** conformance tests
- Total: **43** new conformance tests (not counting the 20 test_generation_boundary.py tests
  for 7.6 which are written but not yet passing)

**Action**: Update summary table to `43 (actual: 7.4: 6, C26: 27, 7.7: 10)`.

### B6. Final Checkpoint Not Checked

Line 657 reads:
```
**Final Checkpoint**: [ ] Full test suite green...
```

Cannot be checked yet — 7.6 is incomplete and 7.7 is uncommitted. But the Final Checkpoint
criteria should be reviewed against current state when 7.6 completes.

---

## C. Implementation Quality Findings

### ~~C1. `auto_impl_context` Field Added but Not Populated~~

**RESOLVED**: `auto_impl_context` is now populated by `graph_builder.py` for CalcUsage
(via `_build_auto_impl_context_for_calcusage()`), FORMULA (via `_build_simple_auto_impl_context()`),
and aggregation modules. All 8 `test_auto_impl_context_populated/none_for_manual` tests pass.

### ~~C2. Stencils.py `_from_graph()` Variant Gap~~

**RESOLVED**: `generate_implementation()` (née `generate_implementation_from_graph()`) now
dispatches on `module.auto_impl_context`: when populated, renders auto-impl template; when
None, renders stub template. Both `test_from_graph_stencil_auto_impl_dispatch` and
`test_from_graph_stencil_stub_dispatch` pass.

### C3. 7.6 Scope Is Large

The generation-boundary plan identifies:
- **9 files** with extraction/analysis imports in `generation/`
- **5 sequential build phases** (auto_impl_context, new _from_graph variants, switch CLI,
  move PipelineContext, remove old functions)
- **13 files to modify** in production code
- **1 file to create** (`orchestration/pipeline_context.py`)
- **20 test cases** (14 failing, 5 passing, 1 skipped)

Estimate: This is the largest single step remaining. It touches generation/, orchestration/,
cli/, and requires function renames across the codebase.

**Risk**: Medium. The build plan is thorough and the pattern is proven (C26 _from_graph()
variants are the template). But the volume of changes and the CLI refactoring add complexity.

### C4. `constraint_comments.py` Removal Decision

The 7.6 plan proposes removing `generation/constraint_comments.py` entirely since its only
consumer (`schemas.py`) won't use it after old functions are removed. However, constraint
support may be needed for downstream API consumers beyond the CLI.

**Recommendation**: Move to `extraction/` rather than deleting. Or document the removal
decision explicitly. The constraint infrastructure took effort to build and may be needed
when constraint handling is extended.

---

## D. Learnings That Affect Design Intent

### D1. PipelineModule Now Has 18+ Fields

With C26 and the `auto_impl_context` addition, PipelineModule has grown significantly:
- Original fields (9): name, module_type, inputs, outputs, execution_order, compilability,
  compiled_expression, is_computed_attribute, is_aggregation
- C26 fields (6): calc_def_name, calc_def_qualified_name, doc_comment, calc_expressions,
  source_file, source_line
- 7.6 field (1): auto_impl_context
- Plus optional fields on ModuleInput (3) and ModuleOutput (4)

This is by design (doc 26 migration strategy), but the model is getting heavy. All new fields
are `Optional[...] = None` which preserves backward compatibility but means there's no
compile-time guarantee that the fields are populated.

**Recommendation**: After 7.6, consider whether a non-optional `PopulatedPipelineModule`
subtype (or a Pydantic validator) would catch population bugs at construction time.

### D2. Registry Import Ordering Non-Determinism

C26 found that FORMULA/aggregation import ordering in `registry.py` is source-dependent
(extraction order vs execution order). Both old and new paths now sort deterministically.
This is a cosmetic difference but it means the C26 identity test uses normalized comparison
for the registry.

**Impact on 7.6**: When renaming `_from_graph()` variants to drop the suffix, the registry
function's output will be the normalized (sorted) version. Any downstream consumers that
depend on specific import ordering would break. In practice, Python import order is irrelevant.

### D3. Single-Output `field_name="root"` Loses Original Attribute Name

C26 added `_output_attr_name()` helper that recovers the original name from PQN format
(`channel_name.split("__")[-1]`). This works but is fragile — it depends on the PQN invariant
from ADR-003. A dedicated `original_attr_name` field on ModuleOutput would be more robust.

**Recommendation**: Consider adding `original_attr_name: str | None = None` to ModuleOutput
if the PQN recovery pattern appears in more than 3 call sites.

---

## E. End-to-End Codegen Status

### E1. Integration Tests PASS

`tests/integration/test_full_pipeline.py` contains **20 tests** that run full code generation
via `run_codegen(config)`:

| Test Class | Tests | What It Verifies |
|-----------|-------|------------------|
| `TestRunCodegenPhases` | 5 | Directory structure, schemas, modules+stencils, pipeline+registry, entry points+extras |
| `TestCodegenRuntimeGapFixes` | 5 | JSON populated with defaults, CUSTOM_SCHEMA_TYPES, no FusionParams schema, design_path_filter CLI flag |
| `TestInstallCommands` | 4 | CLI install, list, skip-existing, force-overwrite |
| standalone | 6 | Full pipeline, CLI help, config defaults, no hardcoding, extractor loads, cross-layer imports |

**All 20 pass in 1.68s.** These use `sample_model_path` and `chain_spike_model_path` fixtures
pointing to real `.sysml` files.

### E2. Conformance E2E Tests PASS

`tests/conformance/test_pipeline_e2e.py` contains **16 tests** verifying:
- ComputationGraph produced for all 4 models
- Every input wired
- Every producer channel declared
- Valid topological sort
- Entry points classified
- Module types correct
- Baseline comparison (4 models match snapshots)

**All 16 pass.**

### E3. E2E Coverage Assessment

The end-to-end tests exercise the FULL pipeline:
1. ✅ Extraction (SysML → data models) — via snapshot fixtures or live extractor
2. ✅ Analysis (backtracking, parameter groups) — via `build_pipeline_context()`
3. ✅ Resolution (graph building) — via `build_computation_graph()`
4. ✅ Generation (YAML, modules, stencils, schemas, registry, JSON templates) — via `run_codegen()`

**Gap**: The e2e tests don't verify the CONTENT of generated Python files (only that they
exist and have basic structure). For example, `test_generates_modules_and_stencils` checks
`len(module_files) > 0` but doesn't verify the generated code is syntactically valid Python
or that imports resolve. This is partially covered by the conformance tests (C20-C25) which
render templates from ComputationGraph and verify content, but those don't go through the
CLI path.

### E4. No "Compile the Generated Code" Test

There is no test that:
1. Runs `run_codegen()` to generate a package
2. Runs `python -c "import generated_package"` to verify the generated code is importable
3. Runs the generated pipeline to verify it produces output

This would be the ultimate e2e validation. However, it would require:
- A TEAx framework dependency (or mock)
- Generated stencils with implementations (not stubs)
- Valid input JSON files

**Risk**: Low for the refactor scope (the refactor doesn't change generation behavior).
Higher risk for long-term confidence in the generator.

**Recommendation**: Consider adding a "generated code imports successfully" test using
`importlib` on the generated `__init__.py` and a selection of generated modules. This would
catch import path bugs, missing type references, and syntax errors without needing TEAx.

---

## F. Remaining Work Items

### ~~F1. Commit 7.7 (Immediate)~~

**RESOLVED**: 7.7 committed as `fd119ba`.

### F2. Complete 7.6 (Generation Boundary Enforcement)

**BUILD COMPLETE.** All 5 build phases done:
1. ✅ `auto_impl_context` populated (was already done in prior session)
2. ✅ Missing `_from_graph()` variants created (backlog, test_gen, preservation)
3. ✅ CLI callers switched to unified graph-driven loops
4. ✅ PipelineContext moved to `orchestration/pipeline_context.py`
5. ✅ Old CalcDef-consuming functions removed; zero extraction/analysis imports in generation/

**Integration test fixes** (7 tests updated to match graph-only behavior):
- CATF MFE: 21→18 impl files (3 CalcDefs without usages correctly excluded)
- Hierarchy: aggregation module detection via graph metadata instead of content markers
- Full pipeline: switched from empty-graph fixture to chain_spike

**Remaining**: VALIDATE checklist walkthrough + commit.

### F3. Mark 7.2 Complete (Bookkeeping)

Update IMPLEMENTATION_PLAN.md line 572 to `[x]`.

### F4. Bug 11 (Output Field Defaults)

Still tracked as xfail. Not addressed in Phase 7. The fix is small (strip defaults from
output fields in schema generator) but it's not blocking.

**Recommendation**: Fix as part of 7.6 when refactoring `schemas.py` to use the
`_from_graph()` variant. The xfail test is in `test_gen_schemas.py`.

### F5. Design Doc Updates

Multiple plan.md files identify design doc updates that haven't been applied:

| Source | Doc | Update Needed |
|--------|-----|---------------|
| C26 plan.md | 26-pipeline-module-migration.md | Add source_file, source_line, ModuleOutput.unit/default_value; rename qualified_name → calc_def_qualified_name; document CalcUsage-only scope |
| C26 plan.md | 09-data-models.md | Update PipelineModule/ModuleInput/ModuleOutput field lists |
| 7.4 plan.md | 04-input-resolver.md | Remove Strategy B normalized fallback description |
| 7.4 plan.md | 24-dual-resolution-architecture.md | Update Stage 1b removal note |
| 7.7 plan.md | 05-module-factory.md | Remove "in the refactored state" qualifier from REQ-MF-01 |

**Recommendation**: Batch these into a single doc-update commit after 7.6 completes.

---

## G. Accumulated xfail Inventory

| Test | xfail Reason | Component | Fix Target |
|------|-------------|-----------|------------|
| `test_computed_attributes::TestInheritedAttrClassification` (5 tests) | Inherited attr misclassification — FORMULA→EXPOSE_COMPUTED | C05 | Deferred Issue #9 |
| `test_gen_schemas::test_output_fields_have_no_defaults` (1 test) | Bug 11 — Permitting_Interconnect defaults on outputs | C22 | 7.6 or standalone |

**Total**: 6 xfailed tests. Unchanged from Phase 5+6 audit.

---

## H. Risk Assessment for Remaining Work

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| 7.6 introduces regressions in generated output | Low | High | C26 identity tests verify _from_graph() output; 1803 tests as safety net |
| 7.6 CLI refactoring breaks FORMULA/aggregation generation | Medium | High | E2E integration tests (20 in test_full_pipeline.py) catch this |
| Uncommitted 7.7 work conflicts with 7.6 changes | Medium | Low | Both touch graph_builder.py — commit 7.7 FIRST, then start 7.6 |
| Constraint infrastructure lost in 7.6 cleanup | Low | Medium | Move to extraction/ rather than deleting |
| Generated code not importable after refactor | Low | High | Add "import generated code" test (E4 recommendation) |

---

## I. Verdict: Is Phase 7 Complete?

**Nearly.** Phase 7 is approximately **95% complete**.

| Sub-step | Status | Blocking? |
|----------|--------|-----------|
| 7.1 | ✅ Committed | No |
| 7.2 | ✅ Done (needs checkbox) | No |
| 7.3 | ✅ Committed | No |
| 7.4 | ✅ Committed | No |
| 7.5/C26 | ✅ Committed | No |
| 7.5a | ✅ Committed | No |
| 7.7 | ✅ Committed (`fd119ba`) | No |
| 7.6 | ⚠️ BUILD complete, awaiting VALIDATE + commit | **Yes — validation + commit needed** |

**To close Phase 7:**
1. ~~Commit 7.7~~ DONE
2. ~~Complete 7.6 build phases 1-5~~ DONE
3. VALIDATE 7.6 (section 5 checklist)
4. Commit 7.6
5. Fix bookkeeping items B1-B5
6. Check Final Checkpoint criteria
7. Batch design doc updates

**End-to-end codegen is functional and tested.** All 1810 tests pass. The generation/
boundary is enforced (zero extraction/analysis imports).

---

## Progress Tracking

| Date | Items Completed | By |
|------|----------------|----|
| 2026-02-20 | Phase 7 audit performed, action items written | Phase 7 checkpoint review |
| 2026-02-20 | 7.7 committed (`fd119ba`); 7.6 BUILD complete (all 5 phases); 7 integration tests fixed; C1, C2, F1, F2, B2 resolved | Build session 4 |
