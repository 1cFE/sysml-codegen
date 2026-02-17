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

- [ ] **0.1 — Snapshot extraction fixtures**
  - Run extraction on all 4 fixture models
  - Serialize to `tests/fixtures/{model}/extraction_snapshot.json`
  - Write a `load_extraction_snapshot(model_name)` helper
  - **Acceptance**: snapshot loads, round-trips through Pydantic, matches live extraction

- [ ] **0.2 — Snapshot pipeline baselines**
  - Run full pipeline on solar_battery_model and catf_mfe_model
  - Capture: ComputationGraph JSON, generated pipeline YAML, generated __init__.py
  - Store in `tests/fixtures/baseline_outputs/{model}/`
  - **Acceptance**: `pytest --baseline` confirms current code reproduces baselines exactly

- [ ] **0.3 — Conformance test harness**
  - Create `tests/conformance/` directory
  - Write parametrized test template: `test_req_{REQ_ID}` naming convention
  - Tag tests with `@pytest.mark.req("REQ-XX-NN")` for traceability
  - **Acceptance**: `pytest -m "req"` runs all conformance tests; mapping to doc requirements is clear

**Checkpoint 0**: [ ] All baseline snapshots captured. Current tests pass (660+). Harness ready.

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

- [ ] **1.3 — SysMLDataExtractor Conformance (C03)**
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

- [ ] **1.4 — Expression Compiler Conformance (C04)**
  - **Refs**: [14-expression-compiler.md](14-expression-compiler.md), [19-ast-dispatch-invariant.md](19-ast-dispatch-invariant.md)
  - Write `tests/conformance/test_expression_compiler.py`:
    - Compile every output expression from snapshot calc defs
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
  - If current impl needs changes, make them. If not, just lock it down with tests.
  - **Acceptance**: REQ-OR-01 through REQ-OR-07 all green

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
    - Verify scoped-before-unscoped resolution order (instrument or use known-ambiguous case)
    - Verify cycle detection (construct a model with cycles if needed, or use synthetic calc data)
    - Verify self-reference guard
    - Verify topological ordering (every dependency appears before its consumer)
    - Verify total resolution (no unresolved bindings)
  - **Acceptance**: REQ-BT-01 through REQ-BT-07 all green

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
  - Update all imports
  - Run full test suite — must be green

- [ ] **7.2 — Extract input resolver into `resolution/input_resolver.py`**
  - If `resolve_input()` is currently inline in graph_builder.py, extract it
  - Update imports
  - Run full test suite

- [ ] **7.3 — Consolidate naming utilities into `core/`**
  - Merge `analysis/qualified_names.py` and `core/qualified_names.py`
  - Remove duplicated identifier_types
  - Run full test suite

- [ ] **7.4 — Dead code removal**
  - Identify unreachable code paths (functions never called, branches never taken)
  - Remove one file/function at a time
  - Run full test suite after each removal
  - **Safety**: only remove code that has zero callers and zero test coverage

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
| 0 | Infrastructure | Baselines captured, harness ready | ~10 |
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

## Accumulated Learnings

> Findings from completed components that affect other components.
> Updated during the LEARN phase of each component (see `component-loop.md` template).

{none yet}

---

## Design Doc Amendments

> Design intent doc updates triggered by implementation findings.
> Tracked here; applied in a dedicated PROMPT-plan session, not during build.

| Doc | Amendment needed | Triggered by | Applied? |
|-----|-----------------|--------------|----------|

---

## Test Count Tracking

| Milestone | Existing | New Conformance | Total | Date |
|-----------|----------|-----------------|-------|------|
| Baseline (pre-refactor) | 660 | 0 | 660 | 2026-02-17 |
| C01 Data Models | 667 | 91 | 758 | 2026-02-17 |
| C02 Naming Conventions | 758 | 46 | 804 | 2026-02-17 |
