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

- [x] **1.5 — Computed Attribute Classification Conformance (C05)** *(2026-02-17, 37 tests)*
  - **Refs**: [16-computed-attributes.md](16-computed-attributes.md)
  - Write `tests/conformance/test_computed_attributes.py`:
    - Classify every part def attribute from attr_expr_probe fixture
    - Verify 5-way classification is exhaustive and exclusive
    - Verify FORMULA attributes compile
    - Verify EXPOSE_PURE produces alias, not module
  - **Acceptance**: REQ-CA-01 through REQ-CA-07 all green

- [x] **1.6 — Hierarchy Resolver Conformance (C06)** *(2026-02-17, 36 tests)*
  - **Refs**: [25-hierarchy-resolver.md](25-hierarchy-resolver.md), [13-aggregation-scoping.md](13-aggregation-scoping.md)
  - Write `tests/conformance/test_hierarchy_resolver.py`:
    - Template detection correct for all fixture models
    - Part usage hierarchy extracted with correct parent/child relationships
    - Multiplicity data extracted from PartUsage nodes
    - Aggregation term type classification correct (SumTerm, SingletonTerm, LocalTerm)
    - FCE classified as SingletonTerm (not LocalTerm) — AST dispatch invariant
  - **Acceptance**: REQ-HR-01 through REQ-HR-07 all green

- [x] **1.7 — AST Dispatch Invariant Conformance (C07)** *(2026-02-17, 26 tests)*
  - **Refs**: [19-ast-dispatch-invariant.md](19-ast-dispatch-invariant.md)
  - Write `tests/conformance/test_ast_dispatch_invariant.py`:
    - Audit: every dual-check site checks FCE before OE
    - Comment present at every dual-check site
    - All 8+ dispatch sites follow canonical ordering: FCE, OE, FRE, Literal
    - Regression test: if FCE/OE order reversed, test fails
  - **Acceptance**: REQ-AST-01 through REQ-AST-07 all green

**Checkpoint 1**: [x] Foundation locked. All naming, data model, extraction, and expression
compilation requirements verified. 311 new conformance tests. *(2026-02-17)*

---

## Phase TRR: Typed Registry Refactor — Design Doc Updates

**Goal**: Correct the design intent corpus to specify typed identifiers, typed registries,
and elimination of ambiguous key formats. NO code changes — docs only.

**Prerequisite**: Key_A fallback spike (`.project/research/20260217-060000_key-a-fallback-spike.md`)
proved the current docs are wrong in multiple places:
- REQ-BT-08 as written breaks 12 correct resolutions (10 EXPOSE_PURE aliases + 2 SysML QN keys)
- REQ-NC-07 ("no `::` keys") is factually incorrect — 14 SysML QN keys registered in attr_expr_probe
- 5 key formats (Key_A, Key_D, Key_E full, Key_F, bare) have zero resolution hits across all 6 models

**Spec**: `.project/active/typed-registry-refactor/spec.md`

### Execution Order (doc dependencies dictate sequencing)

- [x] **TRR-1 — 27-typed-registry-refactor.md** (NEW)
  - Type system: SysMLQN, EQN, PQN, CanonicalChannel, ScopedKey with format invariants
  - Three typed registries: Scoped (`dict[ScopedKey, CanonicalChannel]`), SysML QN (`dict[SysMLQN, CanonicalChannel]`), Alias (`dict[ScopedKey, CanonicalChannel]`)
  - Eliminated keys: Key_A, Key_D, Key_E full, Key_F, bare — with zero-hit evidence
  - Type-directed dispatch: CHAIN → scoped/alias, REFERENCE → SysML QN/scoped
  - **AC**: All 5 types defined, all 3 registries defined, dispatch table present, evidence cited

- [x] **TRR-2 — 09-data-models.md**
  - Add `CanonicalChannel` and `ScopedKey` NewType definitions to Name Type Wrappers section
  - Add field type rows for OutputRegistry typed keys/values
  - Replace `_index: dict[str, str]` with 3 typed registries in OutputRegistry description
  - Expand REQ-DM-08 to include new types
  - **AC**: All 5 typed identifiers present, OutputRegistry description uses typed registries

- [x] **TRR-3 — 15-naming-conventions.md**
  - Correct REQ-NC-07: SysML QN keys exist in own typed registry
  - Remove "no `::` keys" claim from Section 7 intro
  - Remove Key_A from Phase 1a table, Key_D from Phase 1b table, Key_F/bare from Phase 1c table
  - Update Section 10 Summary table: remove dead keys, add CanonicalChannel/ScopedKey
  - Add doc 27 to Related docs
  - **AC**: Zero dead key rows in Phase 1 tables, REQ-NC-07 accurate, types consistent

- [x] **TRR-4 — 10-output-registry.md**
  - REQ-OR-02: typed lookup methods per registry (not `resolve()`)
  - REQ-OR-05: eliminate Key_A/D/E-full/F/bare from Phase 1
  - REQ-OR-08: Key_A not registered at all (no guard needed)
  - Replace `dict[str, str]` with 3 typed registries throughout
  - Replace `resolve()` API with `scoped_lookup()`, `sysml_qn_lookup()`, `alias_lookup()`
  - Remove dead key rows from all Phase 1 tables
  - Rewrite concrete example with typed constructors
  - **AC**: Zero `resolve()` as single API method, zero `dict[str, str]`, zero dead key rows

- [x] **TRR-5 — 11-analysis-backtracker.md**
  - REQ-BT-08: replace "Step 1 raises" with "dispatch on BindingType"
  - Rename "5-Step Cascade" → "Type-Directed Resolution Dispatch"
  - DELETE Step 1 entirely (Key_A guard removed)
  - Transform Step 0 to CHAIN primary path with ScopedKey
  - Transform Step 1b to REFERENCE primary path (SysMLQN registry)
  - Rewrite concrete walkthrough for CHAIN and REFERENCE paths
  - Remove all `UnscopedResolutionError` references
  - **AC**: Zero Key_A refs, zero UnscopedResolutionError, CHAIN/REFERENCE dispatch documented

- [x] **TRR-6 — 04-input-resolver.md**
  - Strategy A: delete Key_A warning block, query scoped registry
  - Strategy B: transform to SysML QN registry lookup (remove REMOVAL_CANDIDATE)
  - Strategy C: produce ScopedKey, query scoped registry
  - Update ResolutionContext, AGG_STRATEGIES, truth table
  - **AC**: Zero Key_A refs, strategies use typed registries

- [x] **TRR-7 — 24-dual-resolution-architecture.md**
  - REQ-DRA-03: typed registries, no untyped `dict.get()`
  - Path 1 cascade: binding-type dispatch (CHAIN/REFERENCE paths)
  - Delete Key_A guard from Stage 1
  - Transform Stage 1b to REFERENCE SysML QN lookup
  - Full rewrite of Strategy Overlap table for typed registries
  - **AC**: Zero Key_A refs, typed registries in cascade, strategy table accurate

- [x] **TRR-8 — 03-resolution-overview.md**
  - REQ-RES-07: ScopedKey + typed registries, remove UnscopedResolutionError
  - Replace `dict[str,str]` with typed registries in Scope Problem section
  - Update CalcUsage/pseudocode sections with typed references
  - Add doc 27 to Related docs
  - **AC**: Zero `dict[str,str]` describing OutputRegistry, zero UnscopedResolutionError

### Cascade Updates (secondary docs — mention-level updates only)

| Doc | Change |
|-----|--------|
| 00-pipeline-overview.md | Note typed registries in Step 5.5 description if OutputRegistry mentioned |
| 01-extraction.md | No changes needed (extraction is upstream of registries) |
| 02-orchestration.md | Note typed registry in Step 5.5 if OutputRegistry mentioned |
| 05-module-factory.md | Note typed registry lookups if resolve() referenced |
| 13-aggregation-scoping.md | Note ScopedKey for Key_E_stripped if mentioned |
| revision_backlog.md | Mark RB-01 as superseded by doc 27 |

### Validation Criteria

After all TRR edits:
1. `grep -r "Key_A" *.md` in design intent dir → zero hits outside doc 27 rationale and `_intermediate_` files
2. `grep -r "dict\[str, str\]" *.md` → zero hits describing OutputRegistry
3. `grep -r "UnscopedResolutionError" *.md` → zero hits outside `_intermediate_` files
4. `grep -r "resolve()" *.md` → zero hits describing OutputRegistry single-method API
5. All REQ cross-references consistent between definition and citation docs
6. `ScopedKey`, `CanonicalChannel`, `SysMLQN` used consistently across docs 03, 04, 09, 10, 11, 15, 24, 27
7. No orphan requirement references (every REQ-XX-NN cited exists in its home doc)

### Impact on Subsequent Phases

| Phase.Step | Component | Impact |
|-----------|-----------|--------|
| 2.1 | C08 — Output Registry | Conformance tests must verify typed registries, not flat `dict[str,str]`. Test `scoped_lookup()`, `sysml_qn_lookup()`, `alias_lookup()` instead of `resolve()`. |
| 3.1a | C11a — DependencyBacktracker | Conformance tests verify binding-type dispatch outcomes (CHAIN/REFERENCE). Done. |
| 3.1b | C11b — Backtracker Migration | Typed dispatch implementation + `_compat` removal. Subsumes 3 items from Phase 7.4 (`resolve()`, Step 1 block, `_key_a_keys`). |
| 3.2 | C12 — Input Resolver | Strategies use typed registry methods. Strategy A queries scoped registry. Strategy B queries SysML QN registry. |
| 7.4 | Dead code removal | 7 remaining TRR items (3 moved to C11b: `resolve()`, Step 1 block, `_key_a_keys`) |

**Checkpoint TRR**: [x] All 8 design docs updated. Validation criteria 1-7 pass. *(2026-02-17, commit a64c622)*
All conformance test acceptance criteria in C08, C11, C12 updated to match typed registries.

---

## Phase 2: Core Infrastructure Spikes

**Goal**: Build and validate the three infrastructure components that sit between
extraction and analysis. Each is independently testable.

- [x] **2.1 — Output Registry (C08)** *(completed 2026-02-17)*
  - **Refs**: [10-output-registry.md](10-output-registry.md), [27-typed-registry-refactor.md](27-typed-registry-refactor.md)
  - Created 5 `NewType` wrappers (`SysMLQN`, `EQN`, `PQN`, `CanonicalChannel`, `ScopedKey`) + 2 constructor functions in `core/identifier_types.py`
  - Refactored `OutputRegistry`: 3 typed dicts + typed lookup methods + `_compat` dict for legacy keys
  - Refactored `build_output_registry()`: typed registration + legacy compat keys
  - 32 conformance tests in `tests/conformance/test_output_registry.py`
  - Dead keys (Key_A, Key_F, bare) in `_compat` only (invisible to typed lookups), removed in C11
  - **Acceptance**: REQ-OR-01 through REQ-OR-08 all green (1080 tests, 0 failures)

- [x] **2.2 — Virtual Binding Rewrite Spike (C09)** *(completed 2026-02-17)*
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
  - **Acceptance**: REQ-VBR-01 through REQ-VBR-07 all green (1118 tests, 0 failures)

- [x] **2.3 — Aggregation Scoping Spike (C10)** *(completed 2026-02-17)*
  - **Refs**: [13-aggregation-scoping.md](13-aggregation-scoping.md)
  - Validated all 3 scoping functions (`find_instance_paths_for_partdef`, `_scope_aggregation_expressions`, `_build_chain_aliases`) with real solar_battery and issue22 data
  - Added REQ-AS-08 implementation: `logger.warning()` for zero-instance case (6 lines in `initialization.py`)
  - 47 conformance tests in `tests/conformance/test_aggregation_scoping.py`
  - Both Strategy 1 (direct match) and Strategy 2 (child-walk fallback) covered by real data
  - 41 CHAIN aliases verified against snapshot; 12 cas_category CHAIN redefs correctly filtered
  - **Acceptance**: REQ-AS-01 through REQ-AS-08 all green (1165 tests, 0 failures)

**Checkpoint 2**: [x] Core infrastructure proven. 117 new conformance tests
(C08: 32, C09: 38, C10: 47). 1165 total tests, 0 failures. *(2026-02-17)*

---

## Phase 3: Analysis Components

**Goal**: Validate the two analysis components that consume infrastructure output.
Migrate backtracker to typed dispatch (C11b) before downstream components depend on it.

- [x] **3.1a — DependencyBacktracker Conformance (C11a)** *(completed 2026-02-17)*
  - **Refs**: [11-analysis-backtracker.md](11-analysis-backtracker.md), [24-dual-resolution-architecture.md](24-dual-resolution-architecture.md)
  - Spike: diagnosed resolution paths for 7 models (41 MODULE_OUTPUT, 13 compat-only)
  - 43 conformance tests in `tests/conformance/test_backtracker.py`
  - CHAIN → scoped/alias, REFERENCE → sysml_qn/scoped dispatch outcomes verified
  - 13 compat-only resolutions documented (12 catf_mfe cross-scope + 1 solar_battery secondary REFERENCE)
  - EXPRESSION bindings silently skipped (gap documented for C11b)
  - Cycle detection, topological sort, self-reference guard, key format all verified
  - **Acceptance**: REQ-BT-01 through REQ-BT-08, REQ-DRA-01 all green (1238 tests, 0 failures)

- [ ] **3.1b — DependencyBacktracker Typed Dispatch Migration (C11b)**
  - **Refs**: [11-analysis-backtracker.md](11-analysis-backtracker.md), [27-typed-registry-refactor.md](27-typed-registry-refactor.md)
  - **Depends on**: C11a (conformance safety net), C08 (typed registry)
  - **Scope** (per Phase 2 audit D4 and C11 plan Issue #1):
    - Refactor `_resolve_binding_via_registry()` to use type-directed dispatch:
      CHAIN → `scoped_lookup(ScopedKey)` then `alias_lookup(ScopedKey)`;
      REFERENCE → `sysml_qn_lookup(SysMLQN)` then normalized `scoped_lookup(ScopedKey)`
    - Implement `_consumer_scope_dotted(usage)` for ScopedKey construction
    - Add EXPRESSION binding dispatch path (currently silently skipped — C1 audit finding)
    - Migrate 3 `resolve()` calls in `build_output_registry()` Phases 2/3/4 (Key_A canonical
      names → typed keys, per D1 audit item)
    - **D1 spike question**: How do Phase 2/3/4 alias registration calls in
      `build_output_registry()` migrate away from `resolve()` when `canonical_name` values
      are in Key_A format (`instance_name.attr`)? Options:
      (a) Convert Key_A canonical_names to ScopedKey during alias construction,
      (b) Register Key_A values as scoped keys during Phase 1,
      (c) Keep `_compat` for alias registration only and eliminate it for resolution
    - Resolve 13 compat-only MODULE_OUTPUT resolutions: 12 catf_mfe cross-scope CHAIN
      (`minor_calc.a`) + 1 solar_battery REFERENCE secondary (`annualized_om.p_net_kw`).
      Options: cross-scope alias registration, sibling-scope lookup, or consumer-relative ScopedKey
    - Remove `_compat` dict and deprecated `resolve()` method from OutputRegistry
  - **Acceptance**:
    - All 43 C11a conformance tests still green (outcomes unchanged)
    - Static analysis: `_resolve_binding_via_registry()` calls `scoped_lookup`/`sysml_qn_lookup`/`alias_lookup` (not `resolve()`)
    - Zero `resolve()` calls in `dependency_backtracker.py` and `build_output_registry()`
    - Zero `_compat` references in `output_registry.py`
    - 13 previously-compat-only resolutions now resolve via typed lookups
    - EXPRESSION bindings produce documented behavior (ENTRY_POINT or explicit skip with warning)
  - **Risk**: The 13 compat-only resolutions may require new alias registration in
    `build_output_registry()` or a new ScopedKey derivation strategy. Spike findings suggest
    cross-scope alias registration for catf_mfe and consumer-relative ScopedKey for solar_battery
    REFERENCE secondary.

- [ ] **3.2 — Input Resolver Spike (C12)**
  - **Refs**: [04-input-resolver.md](04-input-resolver.md), [24-dual-resolution-architecture.md](24-dual-resolution-architecture.md)
  - **Approach**: This may need to be extracted from graph_builder.py into its own module.
    If it already exists as `resolve_input()`, write conformance tests. If not, spike it.
  - Write `tests/conformance/test_input_resolver.py`:
    - Build ResolutionContext from real extraction + real OutputRegistry
    - Test each strategy individually with known inputs
    - Test strategy ordering (A before B per AGG_STRATEGIES)
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

**Checkpoint 3**: [ ] All analysis and resolution logic independently proven. Backtracker uses
typed dispatch (no `_compat` dependency). The two resolution paths are verified consistent.
~50-70 new conformance tests total at this point.

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
  - **TRR-identified dead code** (typed registry refactor):
    - [ ] Key_A registration code in `build_output_registry()` Phase 1a
    - [ ] Key_D registration code in `build_output_registry()` Phase 1b
    - [ ] Key_E full (with design prefix) registration code in Phase 1b
    - [ ] Key_F registration code in `build_output_registry()` Phase 1c
    - [ ] Bare-name registration code in Phase 1b and 1c
    - [ ] `derive_key_c()` method (replaced by `ScopedKey.from_eqn()`)
    - [ ] `UnscopedResolutionError` class definition
  - **Moved to C11b (Phase 3.1b)** — these are removed as part of typed dispatch migration:
    - `resolve()` single-method API on OutputRegistry
    - Step 1 code block in `_resolve_binding_via_registry()`
    - `_key_a_keys: set[str]` (moot — Key_A not registered)
    - `_compat` dict on OutputRegistry

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
| 1 | 16/20 aggregation impls produce invalid Python (`.()` syntax) | Resolved by C06 | Bug was fixed in commit `20b720e` (FCE-before-OE). C06 confirms all 20 solar_battery transformed expressions pass `ast.parse()`. REQ-HR-05 static analysis test prevents regression. |
| 2 | EXPOSE_COMPUTED pattern deferred | Out of scope | Acknowledged in Doc 16; no model exercises this yet |
| 3 | agentic-mbse V2 validation rejects valid FORMULA | Out of scope | Upstream fix; tracked in agentic-mbse |
| 4 | 28+ ADR references point to nonexistent docs | In scope — documentation | Low priority; fix as encountered |
| 5 | Two BindingInfo classes un-consolidated | Deferred to Phase 7 | Add to 7.3 naming consolidation |
| 6 | Three expression reconstruction impls | Deferred to Phase 7 | Add to 7.3 or new 7.7 item |
| 7 | Deeply-nested cross-scope REFERENCE | Out of scope | Not observed in any tested model |
| 8 | sum() is only recognized aggregation | Out of scope | Feature request, not refactor |
| 9 | Inherited attribute misclassification in `_classify_attribute_expression` | C05 fix (before Phase 3 recommended) | Classifier assumes flat namespace; SysIDE resolves inherited QNs to supertype. 5 of 6 test patterns affected. Fix requires supertype chain walk in Step 2b + C03 extraction enrichment. See Doc 16 Known Issues. |
| 10 | UNRESOLVABLE classification likely dead code for valid SysML | Document only | SysIDE always resolves attribute QNs; empty-QN fallback (Step 2d) unreachable without parser bugs. Retain as defensive fallback. |

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

### C05 Computed Attribute Conformance (2026-02-17)

1. **UNRESOLVABLE classification absent from all 6 fixture models.** Same pattern as
   C03's EXPRESSION binding type gap. The code path exists and is unit-tested with mock
   data, but no real SysML model produces UNRESOLVABLE computed attributes. Documented
   as a coverage gap.

2. **REQ-CA-06 resolution map testable with minimal OutputRegistry.** Building a
   lightweight registry from snapshot data (FORMULA channels + calc usage outputs) was
   sufficient to test `_build_attribute_resolution_map()`. No full pipeline infrastructure
   needed. This pattern may be reusable for C08 (Output Registry).

3. **All 14 FORMULA compiled expressions pass ast.parse().** Confirms C04 expression
   compiler output is valid Python for all attr_expr_probe formulas. Parametrized
   regression tests lock down exact expression strings.

### C06 Hierarchy Resolver Conformance (2026-02-17)

1. **REQ-HR-07 alias detection has zero positive-case fixture coverage.** All 20
   solar_battery aggregation expressions have empty `aliases` lists. No CHAIN sibling
   redefinition has `source_path` ending with an aggregation `attribute_name` in any
   fixture model. The code path exists (`hierarchy_resolver.py:550-557`) but is never
   exercised with real data.

2. **Deferred Issue #1 (.() syntax) confirmed resolved.** All 20 transformed
   expressions in solar_battery pass `ast.parse()`. The root cause (FCE-before-OE
   ordering) is locked down by REQ-HR-05 static analysis test. No `.()` pattern
   found in any snapshot.

3. **issue22 SumTerm has null multiplicity.** The `widget` PartUsage has multiplicity
   `[3]` but `count_attribute_name` is None (literal count, no named attribute). The
   parametric multiply transformation is correctly skipped — `transformed_expression`
   is just `"widget.total_cost"` with no `*` operator.

4. **Static analysis helpers copied, not shared.** `_find_is_instance_calls_in_function`
   and `_is_syside_is_instance_call` are duplicated from C04's test file. These are
   test utilities specific to static analysis verification; sharing via import would
   create coupling between conformance test files. C07 will likely need the same
   helpers — consider extracting to `tests/helpers/` if a third copy appears.

### C07 AST Dispatch Invariant Conformance (2026-02-17)

1. **Plan's function name for usage_extractor dispatch site was wrong.** The plan
   and design doc listed `extract_binding_info` for dispatch site #4, but the actual
   function containing the FCE/OE checks at lines 521/557 is `_extract_single_binding`.
   The top-level `extract_binding_info` delegates to `_extract_single_binding`.

2. **13 functions call `is_instance()` on expression types, not 8.** Using the broader
   `*.is_instance()` pattern (catching `self.adapter.is_instance()` in `extractor.py`)
   finds 13. 5 are single-type helpers where ordering doesn't matter. The meaningful
   guardrail is "functions with 2+ expression type checks" = 8.

3. **SysideAdapter name-based fallback works for behavioral tests without monkeypatching.**
   The `MockFeatureChainExpressionOperatorExpression` class name triggers the name-based
   fallback for both FCE and OE checks. No monkeypatching needed.

4. **Third copy of static analysis helpers created.** C04, C06, and C07 each have their
   own copy of `_find_is_instance_calls_in_function` and `_is_*_is_instance_call`. C07's
   version is broader (`_is_any_is_instance_call`). If a fourth copy appears, extract to
   `tests/helpers/static_analysis.py`.

### C09 Virtual Binding Rewrite Conformance (2026-02-17)

1. **Pre-rewrite reconstruction from post-rewrite snapshots works reliably.** The approach
   of reversing `owning_part_def_qn` from `__` to `::` format to reconstruct `source_path`
   is deterministic for all 13 solar_battery overrides. This pattern is directly reusable
   for C10 (aggregation scoping) which faces the same post-mutation snapshot issue.

2. **`_rewrite_virtual_bindings()` is idempotent.** Calling on already-rewritten data returns
   0 with no side effects. LITERAL bindings have `source_path=None`, triggering the guard
   before leaf extraction.

3. **Zero CHAIN overrides across all 6 fixture models.** All `design_overrides` in every
   fixture model are `RedefinitionType.LITERAL`. CHAIN override behavior verified only with
   constructed test data using real qualified names from solar_battery.

4. **EXPRESSION overrides silently skipped.** The function's `if/elif` handles only LITERAL
   and CHAIN. EXPRESSION overrides match in the index but fall through without mutation.
   This is correct per the design intent doc but undocumented.

### C3 (Phase 2 Audit) — Inherited Attribute Classification (2026-02-17)

1. **UNRESOLVABLE classification is likely dead code for well-formed SysML.** SysIDE always
   resolves inherited attribute QNs (to the supertype's namespace), so the empty-QN fallback
   path (Step 2d in `_classify_attribute_expression`) is never hit. The UNRESOLVABLE code path
   requires `ref.qualified_name` to be empty, which only happens if SysIDE fails to resolve —
   not observed with any valid SysML construct tested.

2. **Classifier misclassifies inherited attributes as EXPOSE_COMPUTED instead of FORMULA.**
   SysIDE resolves inherited attr QNs to the supertype's namespace (e.g.,
   `'Base Component'::base_rate`), not the subtype's (`'Derived Component'::base_rate`).
   Step 2b's prefix check fails → Step 2c (calc_ref) → EXPOSE_COMPUTED. 5 of 6 test patterns
   affected. **Fix scope**: C05 classifier or Phase 7 refactor — walk the supertype chain.

3. **`owned_members` excludes inherited attributes.** SysIDE's `owned_members` only returns
   locally-declared members. Inherited attributes are NOT in `sibling_attr_names`. This is
   consistent with SysML v2 semantics (`owned` = locally owned, not inherited).

4. **SysML v2 syntax: `:>` on part usages expects a Feature, not a PartDefinition.**
   `part probe :> 'Base Component'` produces `error (reference-error): Expected Feature element
   but found PartDefinition`. Correct syntax for PartDef inheritance is
   `part def 'Derived' :> 'Base'` (definition-to-definition). Part usages use `: 'Type'` typing.

5. **Practical consequence: computed attributes referencing inherited attrs produce no pipeline
   module.** Since they're misclassified as EXPOSE_COMPUTED (unhandled — Deferred Issue #2),
   they silently produce no module, no compiled expression, and no alias.

### C10 Aggregation Scoping Conformance (2026-02-17)

1. **All three scoping functions fully testable with real fixture data.** Unlike C09 (which
   needed constructed CHAIN override data), C10 has complete coverage from solar_battery:
   41 qualifying CHAIN redefinitions, both instance discovery strategies exercised, and 20
   scoped aggregation outputs verifiable against the snapshot. No constructed test data needed.

2. **Strategy 2 (child-walk) is the dominant instance discovery strategy.** 3 of 4 PartDefs
   with aggregation expressions use Strategy 2 (Battery_System, Site_Infrastructure,
   Solar_Battery_Plant). Only Solar_Array uses Strategy 1 (direct match). This is because
   assembly-level PartDefs don't own virtual CalcUsages directly — they aggregate child
   PartUsage outputs.

3. **cas_category CHAIN redefinitions correctly filtered by dot-in-source_path guard.** 12
   CHAIN redefinitions with bare CAS codes (no dot in `source_path`) are filtered out. These
   are entry-point identifiers, not channel chains. This validates REQ-AS-04's filter design.

4. **C09 Learning #1 (post-mutation snapshot) NOT needed for C10.** C10's scoping functions
   create new `ScopedAggregationData` objects from raw inputs — they don't mutate the hierarchy
   data. The snapshot contains both raw inputs and expected outputs side-by-side, enabling
   straightforward input→output comparison without reconstruction.

### C11 DependencyBacktracker Conformance (2026-02-17)

1. **13 compat-only MODULE_OUTPUT resolutions across 2 models.** 12 in catf_mfe (cross-scope
   `minor_calc.a` CHAIN bindings — consumers in different radial build layers than the
   `plasma_region` producer) + 1 in solar_battery (REFERENCE secondary path `annualized_om.p_net_kw`
   resolving through Key_A in `_compat`). These resolve through the deprecated `resolve()` cascade
   hitting `_compat` dict. Under typed dispatch, they need a new resolution strategy — potentially
   cross-scope alias registration or sibling-scope lookup. This is the primary C11b migration concern.

2. **EXPRESSION bindings silently skipped by backtracker.** `source_path=None` causes the
   `if binding.source_path:` guard to skip them — no resolution created, no crash. The pipeline
   crash from Issue #2 occurs downstream (graph builder or generation), not in the backtracker.

3. **build_backtracker_from_snapshot() is simpler than anticipated.** Snapshots contain
   post-VBR, post-scoping data, so the helper only needs: load snapshot → build_output_registry() →
   instantiate backtracker → run. No manual VBR or scoping replication needed.

4. **catf_mfe cross-package resolution confirmed working.** 10 alias_lookup hits validate the
   Phase 2 CHAIN alias bridge between CATFMFEMagnets and CATFMFERadialBuild packages.

5. **sample_model produces 0 usages/resolutions.** Not useful for conformance testing — excluded
   from parametrized model lists.

6. **Static analysis via textwrap.dedent + ast.parse for method source.** `inspect.getsource()`
   returns indented method source. Must `textwrap.dedent()` before `ast.parse()`.

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
| 16-computed-attributes.md | Note UNRESOLVABLE has zero coverage in fixture models | C05 conformance (2026-02-17) | No |
| COMPONENT_CHECKLIST.md | Consider adding REQ-CA-08 (FORMULA-to-FORMULA limitation) to AC list | C05 conformance — present in design doc but absent from checklist (2026-02-17) | No |
| COMPONENT_CHECKLIST.md | C06: changed doc ref from `01-extraction.md` to `25-hierarchy-resolver.md`; added REQ-HR-01 through REQ-HR-07; clarified "Template detection" AC to "part_usage_names maps assembly PartDefs to child names" | C06 conformance (2026-02-17) | Yes |
| 25-hierarchy-resolver.md | Note REQ-HR-07 alias detection has zero positive-case fixture coverage | C06 conformance (2026-02-17) | No |
| 27-typed-registry-refactor.md | NEW: Type system, typed registries, eliminated keys, dispatch tables | Typed Registry Refactor spec (2026-02-17) | Yes (TRR-1) |
| 09-data-models.md | Add CanonicalChannel, ScopedKey types; typed registries replace dict[str,str] | TRR spec (2026-02-17) | Yes (TRR-2) |
| 15-naming-conventions.md | Correct REQ-NC-07; remove dead keys from tables; add typed key rows | TRR spike findings (2026-02-17) | Yes (TRR-3) |
| 10-output-registry.md | Typed registries replace flat dict; resolve() → typed lookups; dead keys removed | TRR spec (2026-02-17) | Yes (TRR-4) |
| 11-analysis-backtracker.md | REQ-BT-08 corrected; Step 1 deleted; type-directed dispatch | TRR spike findings (2026-02-17) | Yes (TRR-5) |
| 04-input-resolver.md | Strategies use typed registries; Key_A warning removed | TRR spec (2026-02-17) | Yes (TRR-6) |
| 24-dual-resolution-architecture.md | Strategy tables rewritten for typed registries | TRR spec (2026-02-17) | Yes (TRR-7) |
| 03-resolution-overview.md | Scope Problem updated; Key_A refs removed; typed registries | TRR spec (2026-02-17) | Yes (TRR-8) |
| 19-ast-dispatch-invariant.md | Correct "8 files" → "8 multi-type dispatch functions across 5 files"; note `_extract_single_binding` not `extract_binding_info` | C07 conformance (2026-02-17) | No |
| 19-ast-dispatch-invariant.md | Note 5 additional single-type helper functions exist (13 total with `is_instance` on expression types) | C07 conformance (2026-02-17) | No |
| IMPLEMENTATION_PLAN.md Step 2.3 | Change "REQ-AS-01 through REQ-AS-07" to "REQ-AS-01 through REQ-AS-08" in acceptance criteria | C10 conformance (2026-02-17) | Yes |
| 04-input-resolver.md | Add `CanonicalChannel` return type to strategy signatures and code examples; remove stale Key_A reference | Phase 2 audit — TRR validation criterion 5 (2026-02-17) | Yes |
| 27-typed-registry-refactor.md | Add `_compat` bridge dict transitional architecture section | C08 conformance — dead keys load-bearing through backtracker (2026-02-17) | Yes |
| 16-computed-attributes.md | Note inherited attribute misclassification: QNs resolve to supertype namespace, causing FORMULA→EXPOSE_COMPUTED misclassification. Classifier needs supertype chain walk. | C3 probe (Phase 2 audit) (2026-02-17) | Yes (2026-02-17) — Known Issues §Inherited Attribute Misclassification + Step 2b annotation |
| 16-computed-attributes.md | Note UNRESOLVABLE is likely dead code for valid SysML — SysIDE always resolves QNs | C3 probe (Phase 2 audit) (2026-02-17) | Yes (2026-02-17) — Known Issues §UNRESOLVABLE Likely Dead Code + UNRESOLVABLE section note + Step 2d annotation |
| 11-analysis-backtracker.md | Note EXPRESSION bindings silently skipped (source_path=None → no resolution). Gap for C11b | C11 conformance (2026-02-17) | No |
| 11-analysis-backtracker.md | Document 13 compat-only resolutions: 12 catf_mfe cross-scope CHAIN, 1 solar_battery REFERENCE secondary. C11b migration concern | C11 conformance (2026-02-17) | No |
| IMPLEMENTATION_PLAN.md Deferred Issues | Add issues #9 (inherited attribute misclassification) and #10 (UNRESOLVABLE dead code) to Deferred Issues table | C3 probe (Phase 2 audit) (2026-02-17) | Yes (2026-02-17) |
| 09-data-models.md | Add footnote to ComputedAttributeClassification enum noting inherited attr misclassification and UNRESOLVABLE dead code status | C3 probe (Phase 2 audit) (2026-02-17) | Yes (2026-02-17) |
| 01-extraction.md | Add note to Part Definitions section about supertype chain data needed for C05 classifier | C3 probe (Phase 2 audit) (2026-02-17) | Yes (2026-02-17) |
| COMPONENT_CHECKLIST.md | C05: update UNRESOLVABLE AC, add inherited attr AC + sibling_attr_names AC; C03: add supertype chain AC | C3 probe (Phase 2 audit) (2026-02-17) | Yes (2026-02-17) |

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
| C05 Computed Attributes | 956 | 37 | 993 | 2026-02-17 |
| C06 Hierarchy Resolver | 986 | 36 | 1022 | 2026-02-17 |
| C07 AST Dispatch Invariant | 1027 | 26 | 1053 | 2026-02-17 |
| C08 Output Registry | 1053 | 32 | 1080 | 2026-02-17 |
| C09 Virtual Binding Rewrite | 1080 | 38 | 1118 | 2026-02-17 |
| C10 Aggregation Scoping | 1118 | 47 | 1165 | 2026-02-17 |
| C1 EXPRESSION Binding (audit) | 1165 | 19 | 1184 | 2026-02-17 |
| C2 CHAIN Override (audit) | 1184 | 10 | 1194 | 2026-02-17 |
| C3 Inherited Attr (audit) | 1194 | 56 | 1250 | 2026-02-17 |
| C11 Backtracker Conformance | — | 43 | 1250 (+5 xfail) | 2026-02-17 |
