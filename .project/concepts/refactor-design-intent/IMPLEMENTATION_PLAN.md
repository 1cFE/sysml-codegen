# Implementation Plan: Incremental Refactor

**Principle**: Build bottom-up, test-first, spike each component in isolation,
compose only after parts are proven. No mocks — every test uses real data models
and real SysML fixture output.

---

## Ground Rules

1. **No mock testing**. Every test uses real Pydantic models, real OutputRegistry instances,
   real extraction output from fixture SysML files. Stubs are acceptable ONLY for the SysIDE
   adapter boundary (since parsing requires the JVM), and only when a cached/serialized
   extraction result can substitute.
2. **Snapshot extraction results**. Before any refactoring begins, serialize extraction output
   from each fixture model (sample_model, solar_battery_model, catf_mfe_model) to JSON. These
   become the "known-good inputs" for all downstream component tests. This decouples downstream
   testing from extraction changes.
3. **One component = one PR**. Each component gets its own branch, tests, and PR. No mega-merges.
4. **Tests land before or with the code**. Never after.
5. **Checkpoints** compare actual pipeline output (ComputationGraph JSON, generated YAML, generated
   Python) against known-good baselines. Regressions are caught by diff, not by opinion.

---

## Phase 0: Test Infrastructure & Baselines

**Goal**: Establish the foundation that makes all subsequent work safe.

- [x] **0.1 — Snapshot extraction fixtures** *(2026-02-17, 54 tests)*
  - Run extraction on all 6 fixture models (sample, solar_battery, catf_mfe, attr_expr_probe, chain_spike, issue22)
  - Serialize to `tests/fixtures/{model}/extraction_snapshot.json` (755KB total)
  - `tests/helpers/snapshot_serializer.py` — recursive serializer handling dataclasses, Pydantic, Path, Enum, set, AST nullification
  - `tests/helpers/snapshot_loader.py` — full deserialization back to typed instances
  - `scripts/capture_extraction_snapshots.py` — re-runnable capture script
  - **Acceptance**: 54 tests green (9 methods x 6 models); round-trip preserves types, paths, enums, tuple keys

- [x] **0.2 — Snapshot pipeline baselines** *(2026-02-17, 16 tests)*
  - Run full pipeline on 4 models (solar_battery, attr_expr_probe, chain_spike, sample_model)
  - Capture: ComputationGraph JSON + registry __init__.py in `tests/fixtures/baseline_outputs/{model}/`
  - YAML baselines already existed in `tests/fixtures/baseline_yaml/` with live diff test
  - `scripts/capture_pipeline_baselines.py` — re-runnable capture script
  - **Acceptance**: 16 tests green; JSON round-trips through Pydantic; registry files parse as valid Python

- [x] **0.3 — Conformance test harness** *(2026-02-17)*
  - `tests/conformance/conftest.py` expanded to 72 lines: session-scoped snapshot fixtures, per-model convenience fixtures
  - `req` and `baseline` markers registered in both conftest.py and pyproject.toml
  - **Acceptance**: `pytest -m "req"` collects 205 conformance tests; snapshot fixtures load all 6 models in <1s

**Checkpoint 0**: [x] All baseline snapshots captured. 874 tests pass. Harness ready.
  Detailed plan: `.project/active/phase-0-test-infrastructure/plan.md`

---

## Phase 1: Foundation & Extraction Components

**Goal**: Validate and lock down the lowest-level building blocks and extraction layer.

- [x] **1.1 — Data Model Conformance (C01)** *(2026-02-17, 91 tests)*
  - **Refs**: [09-data-models.md](09-data-models.md)
  - Write `tests/conformance/test_data_models.py`:
    - Every model importable from documented location
    - Every enum has ALL documented values (parametrized over doc 09 table)
    - Field names and types match doc 09 (use `model_fields` introspection)
    - Construct each model from snapshot extraction data
  - **Acceptance**: REQ-DM-01 through REQ-DM-07 all green

- [x] **1.2 — Naming Convention Conformance (C02)** *(2026-02-17, 46 tests)*
  - **Refs**: [15-naming-conventions.md](15-naming-conventions.md)
  - Write `tests/conformance/test_naming_conventions.py`:
    - `sanitize_name()` with edge cases: quotes, spaces, reserved words, Unicode
    - EQN/PQN/module_name/module_type/channel derivation from known SysML QNs
    - Key_C derivation from known EQNs
    - Parametrize over real qualified names from extraction snapshots
  - **Acceptance**: REQ-NC-01 through REQ-NC-07 all green

- [x] **1.3 — SysMLDataExtractor Conformance (C03)** *(2026-02-17, 44 tests)*
  - **Refs**: [01-extraction.md](01-extraction.md)
  - Write `tests/conformance/test_extractor.py`:
    - One `CalculationDefinitionData` per calc def in model
    - Every binding has exactly one BindingType
    - Every redefinition classified as exactly one RedefinitionType
    - Aggregation expressions decomposed into typed terms
    - Template calc usages produce virtual CalcUsageData per PartUsage instance
    - Extraction imports NOTHING from analysis/, resolution/, or generation/
    - `output_expression_asts` preserves raw SysIDE AST nodes
  - **Acceptance**: REQ-EXT-01 through REQ-EXT-07 all green

- [x] **1.4 — Expression Compiler Conformance (C04)** *(2026-02-17, 31 tests)*
  - **Refs**: [14-expression-compiler.md](14-expression-compiler.md), [19-ast-dispatch-invariant.md](19-ast-dispatch-invariant.md)
  - Write `tests/conformance/test_expression_compiler.py`:
    - Verify compiler with real calc def metadata from snapshots (AST serialization boundary prevents compiling from snapshots directly; tests use real attribute name sets + mock ASTs)
    - Verify ast.parse() succeeds on every compiled expression
    - Verify compilability verdicts match expected
    - Verify FCE-before-OE ordering at all dispatch sites (static analysis test)
  - **Acceptance**: REQ-EC-01 through REQ-EC-07, REQ-AST-01 all green

- [ ] **1.5 — Computed Attribute Classification Conformance (C05)**
  - **Refs**: [16-computed-attributes.md](16-computed-attributes.md)
  - Write `tests/conformance/test_computed_attributes.py`:
    - Classify every part def attribute from attr_expr_probe fixture
    - Verify 5-way classification is exhaustive and exclusive
    - Verify FORMULA attributes compile
    - Verify EXPOSE_PURE produces alias, not module
  - **Acceptance**: REQ-CA-01 through REQ-CA-07 all green

- [ ] **1.6 — Hierarchy Resolver Conformance (C06)**
  - **Refs**: [25-hierarchy-resolver.md](25-hierarchy-resolver.md), [13-aggregation-scoping.md](13-aggregation-scoping.md)
  - Write `tests/conformance/test_hierarchy_resolver.py`:
    - Template detection correct for all fixture models
    - Part usage hierarchy extracted with correct parent/child relationships
    - Multiplicity data extracted from PartUsage nodes
    - Aggregation term type classification correct (SumTerm, SingletonTerm, LocalTerm)
    - FCE classified as SingletonTerm (not LocalTerm) — AST dispatch invariant
  - **Acceptance**: REQ-HR-01 through REQ-HR-07 all green

- [ ] **1.7 — AST Dispatch Invariant Conformance (C07)**
  - **Refs**: [19-ast-dispatch-invariant.md](19-ast-dispatch-invariant.md)
  - Write `tests/conformance/test_ast_dispatch_invariant.py`:
    - Audit: every dual-check site checks FCE before OE
    - Comment present at every dual-check site
    - All 8+ dispatch sites follow canonical ordering: FCE, OE, FRE, Literal
    - Regression test: if FCE/OE order reversed, test fails
  - **Acceptance**: REQ-AST-01 through REQ-AST-07 all green

**Checkpoint 1**: [ ] Foundation locked. All naming, data model, extraction, and expression
compilation requirements verified. ~50-70 new conformance tests.

---

## Phase 2: Core Infrastructure Spikes

**Goal**: Build and validate the three infrastructure components that sit between
extraction and analysis. Each is independently testable.

- [ ] **2.1 — Output Registry Spike (C08)**
  - **Refs**: [10-output-registry.md](10-output-registry.md)
  - Write `tests/conformance/test_output_registry.py`:
    - Register channels using real PQNs from extraction snapshots
    - Verify all 6 key formats resolve to canonical PQN
    - Verify collision policy (first wins, warning logged)
    - Verify phase ordering enforcement
    - Verify Key_C derivation for scoped lookups
    - Verify Key_A is registered (diagnostic visibility) but resolution paths raise `UnscopedResolutionError` instead of silently using Key_A (REQ-OR-08)
  - If current impl needs changes, make them. If not, just lock it down with tests.
  - **Acceptance**: REQ-OR-01 through REQ-OR-08 all green

- [ ] **2.2 — Virtual Binding Rewrite Spike (C09)**
  - **Refs**: [12-virtual-binding-rewrite.md](12-virtual-binding-rewrite.md)
  - **Approach**: Extract `_rewrite_virtual_bindings()` from `generation/initialization.py`
    into a standalone function (target: `orchestration/virtual_binding_rewrite.py` or keep
    in-place with clean interface)
  - Write `tests/conformance/test_virtual_binding_rewrite.py`:
    - Load solar_battery extraction snapshot
    - Apply rewrite
    - Verify LITERAL overrides: binding_type changed, literal_value set
    - Verify CHAIN overrides: source_path replaced
    - Verify template copies skipped
    - Verify already-LITERAL bindings untouched
    - Verify deep-path override index key format
  - **Acceptance**: REQ-VBR-01 through REQ-VBR-07 all green

- [ ] **2.3 — Aggregation Scoping Spike (C10)**
  - **Refs**: [13-aggregation-scoping.md](13-aggregation-scoping.md)
  - **Approach**: Extract `_scope_aggregation_expressions()` similarly
  - Write `tests/conformance/test_aggregation_scoping.py`:
    - Load solar_battery extraction snapshot
    - Scope aggregation expressions
    - Verify one-to-many expansion (count ScopedAggregationData vs PartDef count)
    - Verify instance path format (dotted, design prefix stripped)
    - Verify CHAIN alias generation
    - Verify module_eqn format
  - **Acceptance**: REQ-AS-01 through REQ-AS-07 all green

**Checkpoint 2**: [ ] Core infrastructure proven. Output registry, virtual binding rewrite,
and aggregation scoping all independently validated. ~40-60 new conformance tests.

---

## Phase 3: Analysis Components

**Goal**: Validate the two analysis components that consume infrastructure output.

- [ ] **3.1 — DependencyBacktracker Conformance (C11)**
  - **Refs**: [11-analysis-backtracker.md](11-analysis-backtracker.md), [24-dual-resolution-architecture.md](24-dual-resolution-architecture.md)
  - Write `tests/conformance/test_backtracker.py`:
    - Build real OutputRegistry from extraction snapshot
    - Run backtracker on real calc usages from each fixture model
    - Verify binding_resolutions key format
    - Verify scoped resolution (Step 0/Key_C) is primary path
    - Verify Step 1 raises `UnscopedResolutionError` when scoped resolution fails but unscoped Key_A would match (REQ-BT-08)
    - Verify cycle detection (construct a model with cycles if needed, or use synthetic calc data)
    - Verify self-reference guard
    - Verify topological ordering (every dependency appears before its consumer)
    - Verify total resolution (no unresolved bindings)
  - **Acceptance**: REQ-BT-01 through REQ-BT-08 all green

- [ ] **3.2 — Input Resolver Spike (C12)**
  - **Refs**: [04-input-resolver.md](04-input-resolver.md), [24-dual-resolution-architecture.md](24-dual-resolution-architecture.md)
  - **Approach**: This may need to be extracted from graph_builder.py into its own module.
    If it already exists as `resolve_input()`, write conformance tests. If not, spike it.
  - Write `tests/conformance/test_input_resolver.py`:
    - Build ResolutionContext from real extraction + real OutputRegistry
    - Test each strategy individually with known inputs
    - Test strategy ordering (C before A)
    - Test self-reference guard
    - Test fallback to entry_point
    - Test STANDARD_STRATEGIES and AGG_STRATEGIES ordering
    - Test immutability of ResolutionContext (attempt mutation, verify frozen)
  - **Acceptance**: REQ-IR-01 through REQ-IR-07 all green

- [ ] **3.3 — ParameterGroupDeriver Conformance (C13)**
  - **Refs**: [17-parameter-group-deriver.md](17-parameter-group-deriver.md)
  - Write `tests/conformance/test_parameter_group_deriver.py`:
    - Derive groups from real extraction data
    - Verify 4-index precedence
    - Verify group naming convention
    - Verify filtered groups exclude non-entry-point params
    - Verify default_value resolution through binding index
  - **Acceptance**: REQ-PGD-01 through REQ-PGD-07 all green

- [ ] **3.4 — Dual Resolution Consistency (X02)**
  - **Refs**: [24-dual-resolution-architecture.md](24-dual-resolution-architecture.md)
  - Write `tests/conformance/test_dual_resolution.py`:
    - For a shared reference that appears in both CalcUsage and FORMULA context,
      verify both paths produce the same wiring decision
    - Use real extraction data where such overlap exists (or construct minimal fixture)
  - **Acceptance**: REQ-DRA-04 green

**Checkpoint 3**: [ ] All analysis and resolution logic independently proven. The two resolution
paths are verified consistent. ~50-70 new conformance tests total at this point.

---

## Phase 4: Module Factory + Graph Assembly

**Goal**: Validate module construction and graph assembly as standalone functions.

- [ ] **4.1 — CalcUsage Module Factory (C14)**
  - **Refs**: [05-module-factory.md](05-module-factory.md)
  - Write `tests/conformance/test_factory_calc_usage.py`:
    - Build modules from real BacktrackingResult + real calc defs
    - Verify pure function (no side effects on inputs)
    - Verify fail-fast on missing binding_resolutions
    - Verify single vs multi output field naming
    - Verify every ModuleInput has exactly one InputSource
  - **Acceptance**: REQ-MF-01, REQ-MF-02, REQ-MF-05, REQ-MF-08 all green

- [ ] **4.2 — FORMULA Module Factory (C15)**
  - **Refs**: [05-module-factory.md](05-module-factory.md), [16-computed-attributes.md](16-computed-attributes.md)
  - Write `tests/conformance/test_factory_formula.py`:
    - Build FORMULA modules from real ComputedAttributeData
    - Verify is_computed_attribute=True, FULLY_COMPILABLE
    - Verify uses attribute resolution map (not resolve_input)
    - Verify single-output field_name="root"
    - Verify factory-created entry points typed DESIGN_ATTRIBUTE
  - **Acceptance**: REQ-MF-01, REQ-MF-03, REQ-MF-05 all green

- [ ] **4.3 — Aggregation Module Factory (C16)**
  - **Refs**: [05-module-factory.md](05-module-factory.md), [18-literal-value-propagation.md](18-literal-value-propagation.md)
  - Write `tests/conformance/test_factory_aggregation.py`:
    - Build aggregation modules from real ScopedAggregationData
    - Verify SumTerm, SingletonTerm, LocalTerm handling
    - Verify `_find_literal_redefinition()` strategy order (type-aware first)
    - Verify LocalTerm does NOT use literal redef fallback
    - Verify default backfill replaces None
    - Verify FULLY_COMPILABLE vs MANUAL_REQUIRED
  - **Acceptance**: REQ-MF-01, REQ-MF-04, REQ-MF-05, REQ-MF-06, REQ-MF-07, REQ-LVP-01 through REQ-LVP-07 all green

- [ ] **4.4 — Entry Point Classification (C17)**
  - **Refs**: [06-entry-point-classifier.md](06-entry-point-classifier.md)
  - Write `tests/conformance/test_entry_point_classifier.py`:
    - Classify entry points from real BacktrackingResult
    - Verify precedence: DESIGN_ATTRIBUTE > LIBRARY_DEFAULT > USAGE_LITERAL
    - Verify float conversion of default_value
    - Verify orphan -> "system_design" fallback
    - Verify factory EPs not re-classified
  - **Acceptance**: REQ-EPC-01 through REQ-EPC-08 all green

- [ ] **4.5 — Graph Assembly (C18)**
  - **Refs**: [07-graph-assembly.md](07-graph-assembly.md)
  - Write `tests/conformance/test_graph_assembly.py`:
    - Assemble graph from real PipelineModules + ParameterGroups
    - Verify topological sort validity (no forward references)
    - Verify cycle detection with synthetic cycle
    - Verify channel reference validation (no dangling wires)
    - Verify ComputationGraph shape (3 fields)
  - **Acceptance**: REQ-GA-01 through REQ-GA-07 all green

**Checkpoint 4**: [ ] Every component from extraction through graph assembly independently tested.
All 3 module types verified. Graph assembly proven correct. This is the critical milestone —
the pipeline "spine" is validated end-to-end in parts.

**Assessment**: Compare ComputationGraph produced by running all components in sequence
against baseline snapshots from Phase 0. Must match exactly (or document intentional changes).

---

## Phase 5: Orchestrator Integration

**Goal**: Wire all proven components into the orchestrator and verify the end-to-end pipeline.

- [ ] **5.1 — Orchestrator Step Ordering (C19)**
  - **Refs**: [02-orchestration.md](02-orchestration.md)
  - Write `tests/conformance/test_orchestrator.py`:
    - Run full orchestrator on each fixture model
    - Verify step ordering via instrumentation or output inspection
    - Verify FORMULA attrs removed from design_attrs before param group construction
    - Verify OutputRegistry phase ordering
    - Verify CHAIN alias unresolvable = warning, not error (check logs)
  - **Acceptance**: REQ-ORCH-01 through REQ-ORCH-07 all green

- [ ] **5.2 — End-to-End Pipeline Validation**
  - **Refs**: [00-pipeline-overview.md](00-pipeline-overview.md)
  - Write `tests/conformance/test_pipeline_e2e.py`:
    - Run full pipeline on solar_battery_model
    - Verify ComputationGraph matches baseline (or improved baseline if bugs fixed)
    - Verify all 3 module types present
    - Verify every ModuleInput wired
    - Verify every module_output resolvable
    - Verify execution_order is valid topological sort
    - Run full pipeline on catf_mfe_model (larger model)
    - Compare against baseline
  - **Acceptance**: REQ-PIPE-01 through REQ-PIPE-07 all green

**Checkpoint 5**: [ ] Orchestrated pipeline produces identical output to current implementation
on all fixture models. This proves the refactored components compose correctly. All 161
requirements verified.

---

## Phase 6: Generation Layer Validation

**Goal**: Verify generators consume only ComputationGraph and produce correct output.

- [ ] **6.1 — Pipeline YAML Generator (C20)**
  - **Refs**: [21-pipeline-yaml-generation.md](21-pipeline-yaml-generation.md)
  - Write `tests/conformance/test_gen_pipeline_yaml.py`:
    - Generate YAML from real ComputationGraph
    - Verify param_group prefix on all entry points
    - Verify all numerics are float
    - Verify .root suffix on single-output references
    - Parse generated YAML and validate structure
  - **Acceptance**: REQ-PY-01 through REQ-PY-07 all green

- [ ] **6.2 — Module Wrapper Generator (C21)**
  - **Refs**: [08-generation.md](08-generation.md)
  - Write `tests/conformance/test_gen_module_wrappers.py`:
    - Generate wrappers from real ComputationGraph
    - One wrapper per PipelineModule
    - Import path matches filesystem path
    - Input/output types match module definition
  - **Acceptance**: REQ-GEN-02 all green

- [ ] **6.3 — Schema Generator (C22)**
  - **Refs**: [22-output-schema-rules.md](22-output-schema-rules.md)
  - Write `tests/conformance/test_gen_schemas.py`:
    - Generate schemas from real ComputationGraph
    - Verify RootModel for single-output, MultiOutput for multi-output
    - Verify no default values on output fields
    - Import and instantiate generated schemas
  - **Acceptance**: REQ-OSR-01 through REQ-OSR-07 all green

- [ ] **6.4 — Module Registry Generator (C24)**
  - **Refs**: [20-module-registry-generation.md](20-module-registry-generation.md)
  - Write `tests/conformance/test_gen_registry.py`:
    - Generate __init__.py from real ComputationGraph
    - Verify design-scoped import paths
    - Verify no name collisions (or proper aliasing)
  - **Acceptance**: REQ-REG-01 through REQ-REG-07 all green

- [ ] **6.5 — Stencil + Smart Regen (C23)**
  - **Refs**: [23-smart-regen-preservation.md](23-smart-regen-preservation.md)
  - Write `tests/conformance/test_gen_stencils.py`:
    - Generate stencils for FULLY_COMPILABLE (auto-impl) and MANUAL_REQUIRED (stub)
    - Verify smart regen decision tree with modified files
    - Verify backup creation
  - **Acceptance**: REQ-SR-01 through REQ-SR-07, REQ-GEN-04 all green

- [ ] **6.6 — JSON Template + Parameter Schema Generator (C25)**
  - **Refs**: [08-generation.md](08-generation.md), [21-pipeline-yaml-generation.md](21-pipeline-yaml-generation.md)
  - Write `tests/conformance/test_gen_json_templates.py`:
    - Each ParameterGroup produces one JSON template + one Pydantic schema
    - JSON template values match entry point default_value
    - Schema field types match declared SysML types
  - **Acceptance**: REQ-GEN-05, REQ-PY-07 all green

- [ ] **6.7 — Type Mapping Consolidation (X01)**
  - **Refs**: [08-generation.md](08-generation.md) REQ-GEN-06
  - Identify all copies of `_map_input_type()` / `_map_output_type()`
  - Consolidate to single function
  - Verify all generators use the same mapping
  - **Acceptance**: REQ-GEN-06 green (currently violated — this is a fix)

**Checkpoint 6**: [ ] Full generation validated. Generated output matches baselines.
Type mapping inconsistency resolved. All generation requirements green.

---

## Phase 7: Structural Refactoring & Dead Code Removal

**Goal**: Now that everything is tested and proven, restructure the codebase to match
the target architecture. This is pure refactoring — no behavior changes.

- [ ] **7.1 — Extract orchestration into `orchestration/` package**
  - Move `build_pipeline_context()` and friends from `generation/initialization.py`
  - Functions moved: `build_pipeline_context()`, `_rewrite_virtual_bindings()`, `_scope_aggregation_expressions()`, `_classify_entry_points()`
  - Update all imports
  - Run full test suite — must be green
  - **AC**:
    - [ ] `generation/initialization.py` line count drops below 200 (currently ~860; only PipelineContext and helpers remain)
    - [ ] No circular imports between `orchestration/` and `generation/`
    - [ ] All imports updated; `git grep 'from.*initialization import'` returns only allowed paths

- [ ] **7.2 — Extract input resolver into `resolution/input_resolver.py`**
  - If `resolve_input()` is currently inline in graph_builder.py, extract it
  - Update imports
  - Run full test suite

- [ ] **7.3 — Consolidate naming utilities into `core/`**
  - Merge `analysis/qualified_names.py` and `core/qualified_names.py`
  - Remove duplicated identifier_types
  - Run full test suite
  - **AC**:
    - [ ] Single import path for all naming functions: `from sysml_codegen.core.qualified_names import ...`
    - [ ] `analysis/qualified_names.py` deleted
    - [ ] `resolution/identifier_types.py` deleted (merged into `core/identifier_types.py`)
    - [ ] No duplicate function definitions across modules
  - **Consolidation candidates** (from Deferred Issues #5, #6):
    - [ ] Two `BindingInfo` classes consolidated
    - [ ] Three expression reconstruction implementations consolidated (or new 7.7 item)

- [ ] **7.4 — Dead code removal**
  - Identify unreachable code paths (functions never called, branches never taken)
  - Remove one file/function at a time
  - Run full test suite after each removal
  - **Safety**: only remove code that has zero callers and zero test coverage
  - **Research-identified dead paths**:
    - [ ] Bare-name handling in resolve() (Research §5.#1)
    - [ ] SYSML_QN normalization / Strategy B (Research §5.#5, RB-03)
    - [ ] Virtual binding rewrite for bare names (Research §5.#1)
    - [ ] Step 3.6 alias enrichment heuristic (Research §1.L10)
    - [ ] Bare-name registration keys (Research §1.L10)

- [ ] **7.5 — PipelineModule Field Expansion (C26)**
  - **Refs**: [26-pipeline-module-migration.md](26-pipeline-module-migration.md)
  - Add 6 missing fields to PipelineModule, ModuleInput, ModuleOutput
  - Populate during graph building
  - Create `_from_graph()` generator variants
  - Verify output identity with baselines (REQ-PMM-04)
  - **Acceptance**: REQ-PMM-01 through REQ-PMM-05 all green

- [ ] **7.6 — Verify generation only consumes ComputationGraph**
  - Audit each generator: does it import from extraction or analysis?
  - If yes, refactor to pass needed data through ComputationGraph/PipelineModule
  - This is the REQ-PIPE-07 / REQ-GEN-01 endgame

**Final Checkpoint**: [ ] Full test suite green (660+ existing + ~200-250 new conformance tests).
All baselines match. All 168+ requirements have at least one test. Codebase matches target
architecture from STRATEGY.md.

---

## Summary: Checkpoint Schedule

| Checkpoint | After Phase | What We Verify | Approx New Tests |
|------------|-------------|----------------|------------------|
| 0 | Infrastructure | Baselines captured, harness ready | 70 (actual) |
| 1 | Foundation + Extraction | Data models, naming, extraction, expressions locked | ~60 |
| 2 | Infrastructure | Registry, VBR, agg scoping proven | ~50 |
| 3 | Analysis | Backtracker, resolver, groups, dual consistency | ~40 |
| 4 | Factories + Graph | All module types + graph assembly | ~40 |
| 5 | Orchestrator | E2E pipeline matches baselines | ~20 |
| 6 | Generation | All generators validated against graph | ~40 |
| 7 | Refactor | Structural cleanup, dead code gone, PipelineModule expanded (C26) | ~10 |

**Total**: ~270 new conformance tests on top of existing 660.

---

## Risk Mitigations

1. **Extraction snapshot staleness**: If extraction changes during refactor, re-snapshot
   and re-baseline. Never silently drift.

2. **Baseline drift**: If a component fix improves output, update baselines deliberately
   with a documented reason. Never auto-accept changed output.

3. **The big merge**: Phase 7 (refactoring) is pure structure — tests guarantee behavior.
   If any test breaks during structural moves, stop and fix immediately.

4. **Scope creep**: Each phase has a clear checklist of REQs. A phase is done when its
   REQs are green, not when it "feels done."

5. **The SysIDE dependency**: Extraction tests that need the JVM parser use serialized
   snapshots. Only the snapshot-capture step (Phase 0.1) needs the live parser.

6. **FORMULA resolution map assumption**: The attribute resolution map is
   pre-computed at classification time. If classification logic changes, FORMULA
   wiring can silently break. Conformance tests must verify map -> module wiring
   chain end-to-end.

---

## Deferred Issues

Issues from the research retrospective (§7) with explicit scope decisions.

| # | Issue | Scope Decision | Rationale |
|---|-------|---------------|-----------|
| 1 | 16/20 aggregation impls produce invalid Python (`.()` syntax) | Reassigned C04→C06/C07 | `.()` syntax comes from `reconstruct_expression()` in aggregation walker, not expression compiler. Expression compiler only imports `extract_feature_reference_name` from expression_utils.py. |
| 2 | EXPOSE_COMPUTED pattern deferred | Out of scope | Acknowledged in Doc 16; no model exercises this yet |
| 3 | agentic-mbse V2 validation rejects valid FORMULA | Out of scope | Upstream fix; tracked in agentic-mbse |
| 4 | 28+ ADR references point to nonexistent docs | In scope — documentation | Low priority; fix as encountered |
| 5 | Two BindingInfo classes un-consolidated | Deferred to Phase 7 | Add to 7.3 naming consolidation |
| 6 | Three expression reconstruction impls | Deferred to Phase 7 | Add to 7.3 or new 7.7 item |
| 7 | Deeply-nested cross-scope REFERENCE | Out of scope | Not observed in any tested model |
| 8 | sum() is only recognized aggregation | Out of scope | Feature request, not refactor |

---

## Accumulated Learnings

> Findings from completed components that affect other components.
> Updated during the LEARN phase of each component (see `component-loop.md` template).

### C03 Extractor Conformance (2026-02-17)

1. **EXPRESSION binding type absent from all 6 fixture models.** No model exercises
   `OperatorExpression` bindings. The code path exists in `usage_extractor.py:557-564`
   but has zero fixture coverage. Future fixture models should include `in x = a + b`
   style bindings to close this gap.

2. **AST fields confirmed null in snapshots.** `output_expression_asts` and
   `member_expressions` are nullified during serialization (SysIDE Java objects).
   REQ-EXT-07 content verification deferred to C04 (expression compiler with live
   extraction). This is the serialization boundary from Phase 0 Learning #2.

3. **Virtual usage naming invariant: `instance_name == qualified_name`.** The
   `_create_virtual_calc_usage` function sets instance_name to the full design-relative
   qualified_name. Concrete usages have short instance_name distinct from qualified_name.
   This is a reliable discriminator for virtual vs concrete usages.

### C04 Expression Compiler Conformance (2026-02-17)

1. **Deferred Issue #1 mis-assigned to C04.** The `.()` syntax issue comes from
   `reconstruct_expression()` in `expression_utils.py`, used by
   `hierarchy_resolver._walk_aggregation_ast()`. The expression compiler does NOT
   use `reconstruct_expression()` — it only imports `extract_feature_reference_name`.
   Reassigned to C06 (Hierarchy Resolver) or C07 (AST Dispatch Invariant).

2. **REQ-AST-01 scoped to expression compiler dispatch sites for C04.** C04 verifies
   FCE-before-OE ordering in `build_expression_ast()` (expression_compiler.py) and
   `reconstruct_expression()` (expression_utils.py). C07 will cover the remaining
   6+ dispatch sites across the codebase.

3. **Static analysis via Python ast module is effective for dispatch ordering verification.**
   Parsing source with `ast.parse()` and walking for `is_instance()` calls provides
   deterministic line-number verification without executing SysIDE code.

4. **Cross-model validation confirms compiler handles all real name sets.** 39 calc defs
   across 3 fixture models (solar_battery: 15, catf_mfe: 21, chain_spike: 3) all
   classify correctly when tested with real attribute names from snapshots.

### Phase 0 (2026-02-17)

1. **Extraction data models are dataclasses, not Pydantic.** Serialization requires
   `dataclasses.asdict()` with custom handlers for Path, Enum, set, and AST nullification.
   Pydantic types (`ChannelAlias`, `ExpressionRef`) use `.model_dump()`. The serializer
   in `tests/helpers/snapshot_serializer.py` handles both.

2. **AST fields are the serialization boundary.** Fields holding SysIDE Java objects
   (`output_expression_asts`, `member_expressions`, `expression_ast`, `source_instance_elem`,
   `source_attribute_elem`, `raw_element`) are nullified during serialization. Downstream
   tests that need real ASTs (C04 expression compiler) must use live extraction.

3. **Tuple dict keys need JSON encoding.** `HierarchyExtractionResult.usage_type_map`
   has `tuple[str, str]` keys. Serialized as `json.dumps([str, str])` strings;
   deserialized back to tuples.

4. **Audit finding — no live regression test for ComputationGraph JSON baselines.**
   The YAML baselines have a live diff test (`test_e2e_output_registry.py`), but the
   new ComputationGraph JSON baselines only have static validation. A live comparison
   test should be added when Phase 5 (orchestrator integration) is implemented.

---

## Design Doc Amendments

> Design intent doc updates triggered by implementation findings.
> Tracked here; applied in a dedicated PROMPT-plan session, not during build.

| Doc | Amendment needed | Triggered by | Applied? |
|-----|-----------------|--------------|----------|
| 01-extraction.md | Note EXPRESSION binding type has zero coverage in fixture models | C03 conformance (2026-02-17) | No |
| COMPONENT_CHECKLIST.md | C03 AC8: clarify "all binding types" — solar_battery has 4 of 5 (EXPRESSION absent) | C03 conformance (2026-02-17) | No |
| 10-output-registry.md | Added REQ-OR-08: Key_A diagnostic-only, resolution SHALL raise instead of silent fallback | Design review discussion (2026-02-17) | Yes |
| 11-analysis-backtracker.md | Added REQ-BT-08: Step 1 raises `UnscopedResolutionError`; rewrote Step 1 section and concrete walkthrough | Design review discussion (2026-02-17) | Yes |
| 03-resolution-overview.md | Strengthened REQ-RES-07: unscoped Key_A fallback explicitly prohibited | Design review discussion (2026-02-17) | Yes |
| 04-input-resolver.md | Strategy A cross-reference to REQ-OR-08; flagged same Key_A ambiguity concern | Consistency review (2026-02-17) | Yes |
| 24-dual-resolution-architecture.md | Updated REQ-DRA-03 and Stage 1 cascade description to reflect Key_A error behavior | Consistency review (2026-02-17) | Yes |
| IMPLEMENTATION_PLAN.md Step 1.4 | Clarified "compile every output from snapshot calc defs" → "verify compiler with real calc def metadata from snapshots" | C04 conformance — AST serialization boundary (2026-02-17) | Yes |
| IMPLEMENTATION_PLAN.md Deferred Issues | Reassigned issue #1 (".() syntax") from C04 to C06/C07 | C04 conformance — reconstruct_expression() not used by expression compiler (2026-02-17) | Yes |

---

## Test Count Tracking

| Milestone | Existing | New Conformance | Total | Date |
|-----------|----------|-----------------|-------|------|
| Baseline (pre-refactor) | 660 | 0 | 660 | 2026-02-17 |
| C01 Data Models | 667 | 91 | 758 | 2026-02-17 |
| C02 Naming Conventions | 758 | 46 | 804 | 2026-02-17 |
| Phase 0 Infrastructure | 804 | 70 | 874 | 2026-02-17 |
| C03 Extractor Conformance | 874 | 44 | 918 | 2026-02-17 |
| C04 Expression Compiler | 918 | 31 | 949 | 2026-02-17 |
