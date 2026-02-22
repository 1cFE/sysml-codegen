# Component: Orchestrator Step Ordering (C19)

**Status**: DONE
**Created**: 2026-02-17
**Last updated**: 2026-02-17
**Updated by**: Plan phase — C19 PROMPT-plan session

## Source Documents

- **Checklist entry**: `COMPONENT_CHECKLIST.md` — C19
- **Design intent**: [02-orchestration.md](../../concepts/refactor-design-intent/02-orchestration.md), [00-pipeline-overview.md](../../concepts/refactor-design-intent/00-pipeline-overview.md)
- **Requirements**: REQ-ORCH-01 through REQ-ORCH-07, REQ-PIPE-01 through REQ-PIPE-07
- **Depends on**: C08 (OutputRegistry), C09 (VBR), C10 (Aggregation Scoping), C11 (Backtracker), C12 (Input Resolver), C13 (ParameterGroupDeriver), C14-C16 (Module Factories), C17 (Entry Point Classification), C18 (Graph Assembly) — ALL complete

---

## 1. Assessment

### What This Component Does

The orchestrator (`build_pipeline_context()` in `generation/initialization.py`) is the conductor of the sysml-codegen pipeline. It calls extraction, analysis, resolution, and assembly layers in strict dependency order, threading data between them. It produces a `PipelineContext` containing the `ComputationGraph` — the single source of truth for downstream generation.

C19 verifies that the composition is correct: steps execute in the right order, data flows correctly between them, and the resulting graph satisfies all pipeline-level invariants.

### Current State

- **Exists?** Yes — `generation/initialization.py` (889 lines). Contains `build_pipeline_context()` (Steps 1–7), `build_output_registry()` (4-phase protocol), `_rewrite_virtual_bindings()`, `_scope_aggregation_expressions()`, `_build_chain_aliases()`, `_remove_formula_from_design_attrs()`, `_extract_and_filter_computed_attributes()`, `_extract_hierarchy_and_rewrite_bindings()`, `PipelineContext` dataclass.
- **Needs extraction/refactoring?** No code changes planned for C19 (conformance-only). Structural extraction to `orchestration/` package is deferred to Phase 7.1.
- **Current test coverage**: `test_step_4_5.py` unit tests FORMULA removal with mock data. `test_e2e_output_registry.py` and integration tests exercise the full pipeline with live SysIDE but without conformance-level assertions. C14–C18 conformance tests use `build_full_graph_from_snapshot()` to compose the pipeline from snapshots and verify component-level invariants. No conformance tests exist for the orchestration layer itself.

### Design Consistency Check

- [x] All acceptance criteria from COMPONENT_CHECKLIST are testable with real data (no mocks)
- [x] AC are consistent with the requirements in the design intent doc(s)
- [x] No contradictions with other component specs
- [x] Input/output interfaces match what upstream/downstream components expect
- [x] Any ambiguities or gaps identified and resolved (documented below)

**Issues found during review:**

1. **`build_pipeline_context()` requires live SysIDE (JVM) — cannot run in conformance tests.**
   *Resolution*: Test the orchestration logic two ways: (a) static analysis of `build_pipeline_context()` source verifying call ordering matches the DAG (proven pattern from C04, C07, C09), and (b) integration tests using `build_full_graph_from_snapshot()` which replicates the full pipeline from snapshots (proven in C17/C18). This covers all REQs without requiring the JVM.

2. **REQ-PIPE-07 ("Generation uses ONLY ComputationGraph") is violated today — generation modules import from extraction.**
   *Resolution*: C19 tests the orchestrator-side of REQ-PIPE-07: that `build_pipeline_context()` produces a `ComputationGraph` with all fields needed for generation. The generation-side fix (eliminating extraction imports) is Phase 7.6's responsibility. C19 documents the current violation count as a baseline for Phase 7.6.

3. **REQ-PIPE-06 ("all three module types") only applies to models that require all three.**
   *Resolution*: solar_battery exercises all 3 (CalcUsage + FORMULA + Aggregation). catf_mfe has CalcUsage only. chain_spike has CalcUsage only. attr_expr_probe has CalcUsage + FORMULA. Test PIPE-06 on solar_battery specifically; parametrize model-appropriate tests for PIPE-01 through PIPE-05.

4. **CHAIN alias unresolvable warning (REQ-ORCH-07) — no fixture model naturally produces an unresolvable CHAIN alias.**
   *Resolution*: All fixture models have fully-resolvable CHAIN aliases. Test the warning path with constructed data: build a real registry from a fixture, then add a ChannelAlias with a canonical_name that doesn't match any scoped key. This follows the same pattern as C14 (constructed edge case with real qualified names).

5. **Overlap with C08–C18 conformance tests.**
   *Resolution*: C19's pipeline-level invariant tests (REQ-PIPE-01 through PIPE-06) are not duplicates of C14–C18. Prior components tested individual functions in isolation. C19 verifies the **composed** pipeline end-to-end from snapshots. The `build_full_graph_from_snapshot()` helper exercises all components together: extraction snapshot → output registry → backtracker → entry point classification → 3 module factories → topological sort → channel validation → ComputationGraph assembly. C18 verified this for baseline comparison; C19 verifies pipeline-level invariants that span multiple components.

### Risks & Unknowns

- **Low risk**: All patterns are proven from prior components. Static analysis (C04, C07), snapshot-based pipeline (C17, C18), log capture (standard pytest), constructed edge cases (C14, C16).
- **No blockers**: All upstream components (C08–C18) complete. All fixture snapshots available.

---

## 2. Spike

**Decision**: SKIP
**Rationale**: All testing patterns are proven from prior components. Static analysis of function source (AST parsing) is proven in C04, C07, C09. Snapshot-based pipeline composition is proven in C17, C18. `_remove_formula_from_design_attrs()` is a simple function with existing unit tests — real-data conformance just extends the pattern. No unknowns that could invalidate the build plan.

---

## 3. Test Plan

**Test file**: `tests/conformance/test_orchestrator.py`
**Fixture data**: solar_battery_model, catf_mfe_model, chain_spike_model, attr_expr_probe_model extraction snapshots

### Test Cases

> Every requirement (REQ-XX-NN) must have at least one test case.
> Every test uses real data — no mocks. Stubs only at SysIDE adapter boundary.

| Test | Requirement | What it verifies |
|------|-------------|------------------|
| **Static Analysis: Step Ordering** | | |
| `test_step_ordering_call_sequence` | REQ-ORCH-01 | `build_pipeline_context()` calls appear in strict DAG order: extract_calc_defs → extract_usages → hierarchy/VBR → design_attrs → computed_attrs → PGD → output_registry → backtracker → compile → build_computation_graph |
| `test_vbr_before_registry_and_backtracker` | REQ-ORCH-02 | `_extract_hierarchy_and_rewrite_bindings` call site appears before `build_output_registry` and `DependencyBacktracker` in source |
| `test_formula_removal_before_pgd_in_source` | REQ-ORCH-03 | `_extract_and_filter_computed_attributes` call appears before `ParameterGroupDeriver(` in source |
| `test_registry_before_backtracker_in_source` | REQ-ORCH-04 | `build_output_registry` call appears before `DependencyBacktracker(` in source |
| `test_computation_graph_is_last_step` | REQ-ORCH-06 | `build_computation_graph(` is the last significant call before `return PipelineContext(` |
| **FORMULA Removal (REQ-ORCH-03)** | | |
| `test_formula_removal_attr_expr_probe` | REQ-ORCH-03 | `_remove_formula_from_design_attrs()` with attr_expr_probe snapshot: all 14 FORMULA QNs removed from design_attrs; returns count=14 (or however many actually match) |
| `test_formula_removal_solar_battery` | REQ-ORCH-03 | `_remove_formula_from_design_attrs()` with solar_battery snapshot: FORMULA CA QNs removed |
| `test_formula_removal_preserves_non_formula` | REQ-ORCH-03 | Non-FORMULA design_attrs survive removal (count unchanged for non-matching QNs) |
| **Registry Phase Ordering (REQ-ORCH-04)** | | |
| `test_phase_ordering_static_analysis` | REQ-ORCH-04 | `build_output_registry()` source has Phase 1 registration calls before Phase 2/3/4 (AST line number comparison) |
| `test_all_aliases_target_canonical_channels[solar_battery]` | REQ-ORCH-04 | Every alias_lookup result is in `registry.canonical_channels` |
| `test_all_aliases_target_canonical_channels[catf_mfe]` | REQ-ORCH-04 | Same for catf_mfe (cross-scope CHAIN aliases) |
| **Aggregation Scoping (REQ-ORCH-05)** | | |
| `test_scoped_count_ge_expression_count[solar_battery]` | REQ-ORCH-05 | `len(scoped_agg_data) >= len(hierarchy_data.aggregation_expressions)` for solar_battery |
| **CHAIN Alias Warning (REQ-ORCH-07)** | | |
| `test_unresolvable_chain_alias_logs_warning` | REQ-ORCH-07 | Build registry with unresolvable CHAIN alias → captures WARNING log, no exception raised |
| `test_resolvable_chain_aliases_no_warning[solar_battery]` | REQ-ORCH-07 | Build registry with solar_battery data → no Phase 2 warning logged |
| **Pipeline Invariants (parametrized over models)** | | |
| `test_produces_computation_graph[solar_battery]` | REQ-PIPE-01 | `build_full_graph_from_snapshot` returns a `ComputationGraph` instance |
| `test_produces_computation_graph[catf_mfe]` | REQ-PIPE-01 | Same for catf_mfe |
| `test_produces_computation_graph[chain_spike]` | REQ-PIPE-01 | Same for chain_spike |
| `test_produces_computation_graph[attr_expr_probe]` | REQ-PIPE-01 | Same for attr_expr_probe |
| `test_every_module_input_wired[solar_battery]` | REQ-PIPE-02 | Every ModuleInput has source.source_type in {"module_output", "entry_point"} |
| `test_every_module_input_wired[catf_mfe]` | REQ-PIPE-02 | Same for catf_mfe |
| `test_every_module_input_wired[chain_spike]` | REQ-PIPE-02 | Same for chain_spike |
| `test_every_module_input_wired[attr_expr_probe]` | REQ-PIPE-02 | Same for attr_expr_probe |
| `test_every_producer_channel_declared[solar_battery]` | REQ-PIPE-03 | Every `producer_channel` in every ModuleInput resolves to a declared ModuleOutput channel_name |
| `test_every_producer_channel_declared[catf_mfe]` | REQ-PIPE-03 | Same for catf_mfe |
| `test_every_producer_channel_declared[chain_spike]` | REQ-PIPE-03 | Same for chain_spike |
| `test_every_producer_channel_declared[attr_expr_probe]` | REQ-PIPE-03 | Same for attr_expr_probe |
| `test_valid_topological_sort[solar_battery]` | REQ-PIPE-04 | No module reads from a module with a higher execution_order |
| `test_valid_topological_sort[catf_mfe]` | REQ-PIPE-04 | Same for catf_mfe |
| `test_valid_topological_sort[chain_spike]` | REQ-PIPE-04 | Same for chain_spike |
| `test_valid_topological_sort[attr_expr_probe]` | REQ-PIPE-04 | Same for attr_expr_probe |
| `test_every_entry_point_classified[solar_battery]` | REQ-PIPE-05 | Every EP has entry_type in EntryPointType |
| `test_every_entry_point_classified[catf_mfe]` | REQ-PIPE-05 | Same for catf_mfe |
| `test_every_entry_point_classified[chain_spike]` | REQ-PIPE-05 | Same for chain_spike |
| `test_every_entry_point_classified[attr_expr_probe]` | REQ-PIPE-05 | Same for attr_expr_probe |
| `test_all_three_module_types_solar_battery` | REQ-PIPE-06 | solar_battery graph has CalcUsage (not computed, not agg), FORMULA (is_computed_attribute), and Aggregation (is_aggregation) modules |
| **Generation Boundary (REQ-PIPE-07)** | | |
| `test_computation_graph_has_all_generation_fields` | REQ-PIPE-07 | ComputationGraph has `modules`, `entry_point_groups`, `execution_order` — the three fields generators consume |
| `test_generation_extraction_import_count` | REQ-PIPE-07 | Count generation/ files importing from extraction/ (baseline for Phase 7.6). Currently expected to be >0 (known violation). |

**Estimated test count**: ~35 tests (5 static analysis + 4 FORMULA removal + 3 registry phase + 1 agg scoping + 2 CHAIN warning + 20 parametrized pipeline invariants + 2 generation boundary)

### Test Infrastructure Needed

- **Reuse**: `build_full_graph_from_snapshot()` from `test_entry_point_classifier.py` (already used by C18)
- **Reuse**: `build_classifier_inputs_from_snapshot()` from `test_entry_point_classifier.py`
- **Reuse**: `load_extraction_snapshot()` from `tests/helpers/snapshot_loader.py`
- **Reuse**: `build_output_registry()` from `generation/initialization.py`
- **New**: Session-scoped fixtures for full graphs from 4 models (extend C18 pattern)
- **New**: Helper to build scoped_agg_data from snapshot (reuse `_scope_aggregation_expressions()`)

### Gate: Ready for BUILD
- [x] Test file exists with all test cases written
- [x] Tests run (expected: all PASS — this is conformance-only, no production code changes)
- [x] No test uses mocking (verified by grep for `mock`, `patch`, `MagicMock`)

---

## 4. Build Plan

### Files to Modify

| File | Change | Why |
|------|--------|-----|
| *None* | No production code changes | C19 is conformance-only |

### Files to Create

| File | Purpose |
|------|---------|
| `tests/conformance/test_orchestrator.py` | ~35 conformance tests for REQ-ORCH-01 through REQ-ORCH-07 and REQ-PIPE-01 through REQ-PIPE-07 |

### Implementation Notes

**Static analysis approach (REQ-ORCH-01, ORCH-02, ORCH-04)**:
Parse `build_pipeline_context()` and `build_output_registry()` source using `inspect.getsource()` + `textwrap.dedent()` + `ast.parse()`. Walk the AST to find function call nodes. Compare line numbers to verify ordering. This pattern is identical to C04 (expression compiler dispatch ordering), C07 (AST dispatch invariant), and C09 (VBR before downstream). Key call sites to locate in `build_pipeline_context()`:
- Line ~765: `_extract_hierarchy_and_rewrite_bindings` (Step 3.5, contains VBR)
- Line ~770: `extract_design_attributes` (Step 4)
- Line ~773: `_extract_and_filter_computed_attributes` (Step 4.5, contains FORMULA removal)
- Line ~781: `ParameterGroupDeriver(` (Step 5)
- Line ~784: `build_output_registry(` (Step 5.5)
- Line ~794: `DependencyBacktracker(` (Step 6)
- Line ~848: `build_computation_graph(` (Step 7)

**FORMULA removal tests (REQ-ORCH-03)**:
Call `_remove_formula_from_design_attrs()` directly with real `computed_attrs` and `design_attrs` from snapshots. attr_expr_probe has 14 FORMULA computed attributes — verify the correct count is removed and non-matching attrs survive.

**Registry phase ordering (REQ-ORCH-04)**:
Build a full registry via `build_output_registry()` with real snapshot data. Then verify every value returned by `alias_lookup()` is in `registry.canonical_channels`. This proves Phase 2-4 aliases point to Phase 1 channels.

**CHAIN alias warning (REQ-ORCH-07)**:
Build a registry from real snapshot data, then call `build_output_registry()` again with an additional constructed `ChannelAlias(alias_name="fake.alias", canonical_name="nonexistent.channel", source="redefinition")`. Use `caplog` fixture to verify WARNING is logged and no exception raised.

**Pipeline invariants (REQ-PIPE-01 through PIPE-06)**:
Use `build_full_graph_from_snapshot()` (from C17) to compose the full pipeline for each model. Apply pipeline-level assertions that span multiple components:
- PIPE-02: iterate all modules → all inputs → assert source.source_type in {"module_output", "entry_point"}
- PIPE-03: collect all declared output channel_names, then verify every module_output reference exists
- PIPE-04: build execution_order index, verify no forward references
- PIPE-05: iterate all entry_point_groups → all parameters → assert entry_type in EntryPointType
- PIPE-06: solar_battery specific — count modules by type (CalcUsage, FORMULA, Aggregation)

**Generation boundary (REQ-PIPE-07)**:
Structural test: verify ComputationGraph model has exactly the 3 fields (`modules`, `entry_point_groups`, `execution_order`). Import baseline: count files in `generation/` that import from `extraction/` or `analysis/` — record as a known violation count. Full fix is Phase 7.6.

### Gate: Ready for VALIDATE
- [x] All test cases pass (39 passed)
- [x] No regressions in full test suite (1571 passed, 2 skipped, 5 xfailed)
- [x] Lint clean (no new issues in test file; pre-existing issues in src/)

---

## 5. Validation

- [x] Every acceptance criterion from COMPONENT_CHECKLIST is satisfied
- [x] Every REQ-ORCH-NN and REQ-PIPE-NN has at least one passing test
- [x] Full test suite passes (record count: 1571 tests passed, 2 skipped, 5 xfailed, 0 failures)
- [x] Cross-check: re-read design intent docs 00 and 02, verify implementation matches
- [x] No unresolved TODOs or FIXMEs in new/modified code
- [x] COMPONENT_CHECKLIST and IMPLEMENTATION_PLAN have been updated

### AC → Test Mapping

| Acceptance Criterion | Tests Covering It |
|---------------------|-------------------|
| Steps execute in strict dependency order | `test_step_ordering_call_sequence` |
| VBR completes before downstream steps | `test_vbr_before_registry_and_backtracker` |
| FORMULA attrs removed from design_attrs before PGD | `test_formula_removal_before_pgd_in_source`, `test_formula_removal_attr_expr_probe`, `test_formula_removal_solar_battery` |
| OutputRegistry phases in strict order | `test_phase_ordering_static_analysis`, `test_registry_before_backtracker_in_source`, `test_all_aliases_target_canonical_channels` |
| Each aggregation expression scoped to instances | `test_scoped_count_ge_expression_count` |
| ComputationGraph is single source of truth | `test_computation_graph_is_last_step`, `test_computation_graph_has_all_generation_fields` |
| CHAIN alias unresolvable = warning not error | `test_unresolvable_chain_alias_logs_warning`, `test_resolvable_chain_aliases_no_warning` |
| Every ModuleInput wired to exactly one source | `test_every_module_input_wired` (×4 models) |
| Every module_output resolves to canonical channel | `test_every_producer_channel_declared` (×4 models) |
| execution_order is valid topological sort | `test_valid_topological_sort` (×4 models) |
| Graph includes all 3 module types | `test_all_three_module_types_solar_battery` |
| Generation uses ONLY ComputationGraph | `test_generation_extraction_import_count` (baseline — known violation) |

### Baseline Impact
No baseline changes — C19 is conformance-only.

---

## 6. Learnings

### Findings

1. **FORMULA QNs and design attribute QNs have zero overlap in all fixture models.** The `_remove_formula_from_design_attrs()` function returns 0 for all 6 models. FORMULA QNs are built from `sysml_to_python_qualified_name(owning_part_qualified_name) + "__" + python_name` (e.g., `AttrExprProbeDesign__probe_design__cost`), while design attribute QNs come from `extract_design_attributes()` (e.g., `AttrExprProbeDesign__probe_design__eta_pump`). The FORMULA CAs and design attrs occupy disjoint attribute namespaces in these models. The safety net function is still correct — verified with constructed overlap data.

2. **39 tests (not estimated 35).** The plan estimated ~35. Additions: `test_formula_removal_constructed_overlap` (constructed overlap to exercise actual removal logic) and `test_formula_removal_idempotent` (with constructed data). Removed: some plan-listed tests consolidated into parametrized fixtures.

3. **All pipeline invariants pass on first run across all 4 models.** No surprises — conformance-only component with no production code changes. Every module input is wired, every producer channel is declared, topological sort is valid, every entry point is classified.

### Design Doc Updates Needed
| Doc | What to update | Why |
|-----|---------------|-----|
| *None* | No design doc updates needed | C19 is conformance-only; all findings confirm existing behavior |

### Cross-Component Impact
No cross-component impact. C19 is conformance-only — no production code changes.

### Deviations from Plan

1. **FORMULA removal tests use constructed data instead of natural overlap.** The plan assumed attr_expr_probe FORMULA QNs would overlap with design attribute QNs, but overlap is zero for all models. Tests adapted to use constructed `DesignAttributeData` with matching QNs to exercise the removal logic. Real-data tests verify the function runs correctly and returns 0 (which is the correct behavior).

2. **Test count 39 vs estimated 35.** Additional constructed tests for FORMULA removal, slightly different parametrization grouping.

---

## 7. Commit

**Branch**: `cost-pattern-refactor` (continuing on active branch)
**Commit convention**: one commit per component, message references component code

- [x] All validation checks above are green
- [ ] `git add` only the files listed in Build Plan + test file, plus IMPLEMENTATION_PLAN and COMPONENT_CHECKLIST
- [ ] Commit message format:
  ```
  refactor(C19): Orchestrator Step Ordering conformance tests

  - Tests: N new conformance tests in tests/conformance/test_orchestrator.py
  - Refs: REQ-ORCH-01 through REQ-ORCH-07, REQ-PIPE-01 through REQ-PIPE-07
  - Design intent: 02-orchestration.md, 00-pipeline-overview.md
  ```
- [x] Committed successfully (29f1af8)

---

## Progress Log

### Session: 2026-02-17 — Build + Validate
**Phase**: PLANNING → VALIDATE
**Work done**:
- Wrote `tests/conformance/test_orchestrator.py`: 39 conformance tests
  - 5 static analysis tests (step ordering, VBR, FORMULA, registry, last step)
  - 5 FORMULA removal tests (attr_expr_probe, solar_battery, preserve, constructed overlap, idempotent)
  - 3 registry phase ordering tests (static analysis, solar_battery aliases, catf_mfe aliases)
  - 1 aggregation scoping test (solar_battery instance count)
  - 2 CHAIN alias warning tests (unresolvable warning, no false warnings)
  - 20 parametrized pipeline invariant tests (PIPE-01 through PIPE-05 × 4 models)
  - 1 module types test (PIPE-06 solar_battery)
  - 2 generation boundary tests (PIPE-07 fields, import baseline)
- All 39 tests pass on first run (after 3 initial fixes: FORMULA QN overlap, ChannelAlias constructor, idempotent test data)
- Full suite: 1571 passed, 2 skipped, 5 xfailed, 0 failures
- No production code changes (conformance-only)
- Lint clean (no new issues)
- Validation section completed: all checkboxes green except IMPLEMENTATION_PLAN update
**Stopped at**: VALIDATE complete, ready for IMPLEMENTATION_PLAN update and commit
**Next step**: Update IMPLEMENTATION_PLAN.md (mark C19 complete, add learnings, update test count), update COMPONENT_CHECKLIST.md, then commit
**Blockers**: None

### Session: 2026-02-17 — Plan phase
**Phase**: PLANNING
**Work done**:
- Read all context: IMPLEMENTATION_PLAN, COMPONENT_CHECKLIST, design intent docs (00, 02), component-loop template
- Read current source: `generation/initialization.py` (889 lines), `resolution/graph_builder.py` signature
- Read existing test infrastructure: `build_full_graph_from_snapshot()`, `build_classifier_inputs_from_snapshot()`, C18 baseline comparison pattern
- Analyzed overlap with C08–C18 conformance tests
- Identified 5 design consistency issues and documented resolutions
- Decision: SKIP spike (all patterns proven)
- Wrote test plan: ~35 tests across 8 test classes
- Wrote build plan: conformance-only, no production code changes
**Stopped at**: Plan complete, ready for review
**Next step**: Review plan, then proceed to BUILD phase
**Blockers**: None
