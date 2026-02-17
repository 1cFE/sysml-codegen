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

- [x] **3.1b — DependencyBacktracker Typed Dispatch Migration (C11b)** *(completed 2026-02-17)*
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
    - Resolve 14 compat-only MODULE_OUTPUT resolutions: 12 catf_mfe cross-scope CHAIN
      (`minor_calc.a`) + 2 solar_battery REFERENCE secondary (`annualized_om.p_net_kw` via Key_F,
      `annualized_financial.total_capex` via Key_E_stripped).
      Options: cross-scope alias registration, sibling-scope lookup, or consumer-relative ScopedKey
    - Remove `_compat` dict and deprecated `resolve()` method from OutputRegistry
  - **Acceptance**:
    - All 43 C11a conformance tests still green (outcomes unchanged)
    - Static analysis: `_resolve_binding_via_registry()` calls `scoped_lookup`/`sysml_qn_lookup`/`alias_lookup` (not `resolve()`)
    - Zero `resolve()` calls in `dependency_backtracker.py` and `build_output_registry()`
    - Zero `_compat` references in `output_registry.py`
    - 14 previously-compat-only resolutions now resolve via typed lookups
    - EXPRESSION bindings produce documented behavior (ENTRY_POINT or explicit skip with warning)
  - **Risk**: The 14 compat-only resolutions (12 catf_mfe + 2 solar_battery) may require new alias
    registration in `build_output_registry()` or a new ScopedKey derivation strategy. C11b spike
    confirmed: Key_A aliases (first-wins) for catf_mfe cross-scope, Key_F scoped registration for
    solar_battery REFERENCE secondary case 1, existing Key_E_stripped for case 2.

- [x] **3.2 — Input Resolver (C12)** *(completed 2026-02-17)*
  - **Refs**: [04-input-resolver.md](04-input-resolver.md), [24-dual-resolution-architecture.md](24-dual-resolution-architecture.md)
  - Created `resolution/input_resolver.py`: `ResolutionContext` (frozen dataclass), 4 strategy callables (A: ScopedRegistryLookup, C: ChainRedefinitionFollow, B: SysMLQNLookup, D: DesignAttributeLookup), `resolve_input()`, `AGG_STRATEGIES`
  - Spike: 7 questions answered empirically (51 refs, 3 models). Strategy A resolves 94% of refs; A-first ordering safe; zero `::` refs; zero design attr duplicates.
  - 26 conformance tests in `tests/conformance/test_input_resolver.py`
  - Regression test verifies resolve_input() produces identical results to _resolve_aggregation_input_channel() for all 51 refs
  - graph_builder.py integration deferred to C16 (Aggregation Module Factory)
  - **Acceptance**: REQ-IR-01 through REQ-IR-07, REQ-DRA-02, REQ-DRA-04 all green (1299 tests, 0 failures)

- [x] **3.3 — ParameterGroupDeriver Conformance (C13)** *(completed 2026-02-17)*
  - **Refs**: [17-parameter-group-deriver.md](17-parameter-group-deriver.md)
  - 30 conformance tests in `tests/conformance/test_parameter_group_deriver.py`
  - 4-index precedence verified (attr > binding > unbound > literal) with solar_battery and catf_mfe
  - Group naming convention, filtered groups, classify(), get_default_value() all verified
  - No production code changes — conformance-only
  - **Acceptance**: REQ-PGD-01 through REQ-PGD-07 all green (1334 tests, 1329 passed, 5 xfailed, 0 failures)

- [x] **3.4 — Dual Resolution Consistency (X02)** *(completed 2026-02-17)*
  - **Refs**: [24-dual-resolution-architecture.md](24-dual-resolution-architecture.md)
  - 20 conformance tests in `tests/conformance/test_dual_resolution.py`
  - Cross-path consistency: backtracker vs resolve_input for CHAIN (3 models) and REFERENCE (3 models)
  - FORMULA map consistency: EXPOSE_PURE channels in canonical_channels, FORMULA channels in SysML QN registry
  - REQ-DRA-05 structural mapping: BindingResolution ↔ InputSource type correspondence
  - REQ-DRA-03 static analysis: no untyped dict.get() in resolution paths (4 tests)
  - Known asymmetry documented: backtracker REFERENCE Step 2 (leaf + parent scope) not replicated by Strategy B
  - No production code changes — conformance-only
  - **Acceptance**: REQ-DRA-03, REQ-DRA-04, REQ-DRA-05 all green (1349 tests passed, 5 xfailed, 0 failures)

**Checkpoint 3**: [x] All analysis and resolution logic independently proven. Backtracker uses
typed dispatch (no `_compat` dependency). The two resolution paths are verified consistent.
136 new conformance tests (C11a: 43, C11b: 17, C12: 26, C13: 30, X02: 20). 1349 total tests,
5 xfailed, 0 failures. *(2026-02-17)*

---

## Phase 4: Module Factory + Graph Assembly

**Goal**: Validate module construction and graph assembly as standalone functions.

- [x] **4.1 — CalcUsage Module Factory (C14)** *(completed 2026-02-17)*
  - **Refs**: [05-module-factory.md](05-module-factory.md)
  - 48 conformance tests in `tests/conformance/test_factory_calc_usage.py`
  - Parametrized over 3 models (solar_battery, catf_mfe, chain_spike)
  - Pure data transformer verified (no mutation of entry_points or binding_resolutions)
  - Fail-fast on missing binding_resolutions key and missing entry_point
  - Single-output field_name="root", multi-output uses attribute names (constructed test)
  - Every ModuleInput has exactly one InputSource (module_output or entry_point)
  - Module name/type/execution_order/default flags all verified
  - No production code changes — conformance-only
  - **Acceptance**: REQ-MF-01, REQ-MF-02, REQ-MF-05, REQ-MF-08 all green (1397 tests, 0 failures, 5 xfailed)

- [x] **4.2 — FORMULA Module Factory (C15)** *(completed 2026-02-17)*
  - **Refs**: [05-module-factory.md](05-module-factory.md), [16-computed-attributes.md](16-computed-attributes.md)
  - 34 conformance tests in `tests/conformance/test_factory_formula.py` (36 collected, 2 skipped)
  - Parametrized over 2 models (attr_expr_probe: 14 FORMULA CAs, solar_battery: 1 FORMULA CA)
  - FORMULA-to-FORMULA chain wiring verified (cost→area, marked_up_cost→cost, cost_density→cost+volume)
  - Entry point mutation documented with explicit purity-deviation test (symmetric to C14's no-mutation test; deferred to Phase 7)
  - No EXPOSE_ALIAS inputs in FORMULA expressions across fixture models (tested defensively)
  - No production code changes — conformance-only
  - **Acceptance**: REQ-MF-01, REQ-MF-03, REQ-MF-05 all green (1431 tests, 0 failures, 5 xfailed)

- [x] **4.3 — Aggregation Module Factory (C16)** *(completed 2026-02-17)*
  - **Refs**: [05-module-factory.md](05-module-factory.md), [18-literal-value-propagation.md](18-literal-value-propagation.md)
  - 32 conformance tests in `tests/conformance/test_factory_aggregation.py`
  - Parametrized over 2 models (solar_battery, issue22)
  - All 3 term types verified: SumTerm (channel + multiplicity), SingletonTerm (channel + literal fallback), LocalTerm (sibling + expose alias + EP fallback)
  - `_find_literal_redefinition()` Strategy 1 (type-aware) proven essential for aliased usage names
  - Key finding: LITERAL redef fallback naturally exercised by SingletonTerms, not SumTerms
  - No production code changes — conformance-only
  - **Acceptance**: REQ-MF-01, REQ-MF-04, REQ-MF-05, REQ-MF-06, REQ-MF-07, REQ-LVP-01, REQ-LVP-04 through REQ-LVP-07 all green (1461 tests, 0 failures, 5 xfailed)

- [x] **4.4 — Entry Point Classification (C17)** *(completed 2026-02-17)*
  - **Refs**: [06-entry-point-classifier.md](06-entry-point-classifier.md)
  - 35 conformance tests in `tests/conformance/test_entry_point_classifier.py`
  - Parametrized over 3 models (solar_battery, catf_mfe, chain_spike)
  - Precedence verified via catf_mfe (all 3 types present from classifier Path 1)
  - Float conversion verified for all 3 branches (DA, LD, UL)
  - Factory EPs retain DESIGN_ATTRIBUTE (runtime check on solar_battery full graph)
  - Static analysis: `_classify_entry_points()` called exactly once, before factory calls
  - Pure function verified (deep-copy comparison of all inputs)
  - Graph-level grouping invariant verified (every EP in some ParameterGroup after orphan handling)
  - Key finding: solar_battery has zero DESIGN_ATTRIBUTE EPs from classifier (DA QNs don't match EP QNs); catf_mfe exercises all 3 types
  - No production code changes — conformance-only
  - **Acceptance**: REQ-EPC-01 through REQ-EPC-08 all green (1498 tests, 0 failures, 5 xfailed)

- [x] **4.5 — Graph Assembly (C18)** *(completed 2026-02-17)*
  - **Refs**: [07-graph-assembly.md](07-graph-assembly.md)
  - 34 conformance tests in `tests/conformance/test_graph_assembly.py`
  - Parametrized over 3 models (solar_battery, catf_mfe, chain_spike)
  - Topological sort validity verified (no forward references across 3 models)
  - Cycle detection verified with synthetic 2-module cycle (CircularDependencyError with participant names)
  - Channel reference validation verified (3 models + dangling channel ValueError)
  - Self-dependency guard verified (3 models + synthetic self-referencing module)
  - ComputationGraph shape (exactly 3 fields) and execution_order invariant verified
  - Static analysis confirms Kahn's algorithm pattern (deque, popleft, in_degree, successors)
  - Checkpoint 4 baseline comparison: 3 models (solar_battery, chain_spike, attr_expr_probe) match Phase 0 baselines
  - Baseline normalization: CalcUsage compilability (unknown vs fully_compilable, snapshot serialization boundary) and parameter ordering within groups (dict iteration order)
  - No production code changes — conformance-only
  - **Acceptance**: REQ-GA-01 through REQ-GA-07 all green (1532 tests, 0 failures, 5 xfailed)

**Checkpoint 4**: [x] Every component from extraction through graph assembly independently tested.
All 3 module types verified. Graph assembly proven correct. This is the critical milestone —
the pipeline "spine" is validated end-to-end in parts.
149 new conformance tests (C14: 48, C15: 34, C16: 32, C17: 35, C18: 34). 1532 passed,
2 skipped, 5 xfailed, 0 failures (1539 collected). *(2026-02-17)*

**Assessment**: ComputationGraph produced by `build_full_graph_from_snapshot()` matches Phase 0
baselines for solar_battery, chain_spike, and attr_expr_probe (after normalizing CalcUsage
compilability and entry_point_groups parameter ordering — known snapshot-vs-live differences).

---

## Phase 5: Orchestrator Integration

**Goal**: Wire all proven components into the orchestrator and verify the end-to-end pipeline.

- [x] **5.1 — Orchestrator Step Ordering (C19)** *(completed 2026-02-17)*
  - **Refs**: [02-orchestration.md](02-orchestration.md), [00-pipeline-overview.md](00-pipeline-overview.md)
  - 39 conformance tests in `tests/conformance/test_orchestrator.py`
  - Static analysis: build_pipeline_context() call ordering matches DAG (5 tests)
  - FORMULA removal with real + constructed data (5 tests)
  - Registry 4-phase ordering + alias canonical channel validation (3 tests)
  - Aggregation scoping instance count (1 test)
  - CHAIN alias warning path with constructed unresolvable alias (2 tests)
  - Pipeline invariants parametrized over 4 models (20 tests)
  - Module types (PIPE-06 solar_battery) + generation boundary (PIPE-07) (3 tests)
  - No production code changes — conformance-only
  - **Acceptance**: REQ-ORCH-01 through REQ-ORCH-07, REQ-PIPE-01 through REQ-PIPE-07 all green (1571 tests, 0 failures, 5 xfailed)

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
    - [x] Key_A registration code in `build_output_registry()` Phase 1a *(C11b — replaced with alias registration)*
    - [x] Key_D registration code in `build_output_registry()` Phase 1b *(C11b — removed)*
    - [x] Key_E full (with design prefix) registration code in Phase 1b *(C11b — removed)*
    - [x] Key_F registration code in `build_output_registry()` Phase 1c *(C11b — replaced with ScopedKey registration)*
    - [x] Bare-name registration code in Phase 1b and 1c *(C11b — removed)*
    - [x] `derive_key_c()` method (replaced by `ScopedKey.from_eqn()`) *(C08 — replaced by `make_scoped_key()`)*
    - [x] `UnscopedResolutionError` class definition *(already absent from src/)*
  - **Moved to C11b (Phase 3.1b)** — removed as part of typed dispatch migration:
    - [x] `resolve()` single-method API on OutputRegistry *(C11b — production callers migrated, method removal pending test migration)*
    - [x] Step 1 code block in `_resolve_binding_via_registry()` *(C11b — replaced with typed dispatch)*
    - [x] `_key_a_keys: set[str]` *(moot — Key_A not registered; field never existed in typed registry)*
    - [x] `_compat` dict on OutputRegistry *(C11b — removed; Key_A values moved to alias registry)*
    - [x] `register()` convenience method on OutputRegistry *(C11b — pending test migration)*

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

- [ ] **7.7 — Factory entry_points mutation → pure return refactor**
  - All 3 module factories deviate from REQ-MF-01's "pure data transformer" aspiration in the same way:
    - C14 (CalcUsage): reads but does not mutate entry_points (already pure)
    - C15 (FORMULA): mutates entry_points dict in-place (documented deviation)
    - C16 (Aggregation): mutates entry_points dict in-place (documented deviation)
  - **Fix**: Refactor C15 and C16 factories to return `(PipelineModule, dict[str, EntryPoint])` instead of mutating the shared dict. Callers merge returned EPs.
  - **AC**:
    - [ ] No `entry_points[k] = v` inside any factory function body
    - [ ] All 3 factories return `(PipelineModule, dict[str, EntryPoint])`
    - [ ] Callers (`build_computation_graph()`) merge returned dicts into the shared entry_points
    - [ ] All conformance tests still green (C14: 48, C15: 32, C16: 32)

**Final Checkpoint**: [ ] Full test suite green (660+ existing + ~200-250 new conformance tests).
All baselines match. All 168+ requirements have at least one test. Codebase matches target
architecture from STRATEGY.md.

---

## Summary: Checkpoint Schedule

| Checkpoint | After Phase | What We Verify | Approx New Tests |
|------------|-------------|----------------|------------------|
| 0 | Infrastructure | Baselines captured, harness ready | 70 (actual) |
| 1 | Foundation + Extraction | Data models, naming, extraction, expressions locked | 311 (actual) |
| 2 | Infrastructure | Registry, VBR, agg scoping proven | 117 (actual) |
| 3 | Analysis | Backtracker, resolver, groups, dual consistency | 136 (actual) |
| 4 | Factories + Graph | All module types + graph assembly | 183 (actual: C14: 48, C15: 34, C16: 32, C17: 35, C18: 34) |
| 5 | Orchestrator | E2E pipeline matches baselines | ~20 |
| 6 | Generation | All generators validated against graph | ~40 |
| 7 | Refactor | Structural cleanup, dead code gone, PipelineModule expanded (C26), factory purity (7.7) | ~10 |

**Total**: 800+ new conformance tests on top of existing 660 (865 actual through C18; C19-C25 pending).

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
| 7 | Deeply-nested cross-scope REFERENCE | Partially addressed (C6 probe) | Fixture created (`deep_cross_scope_probe`) with 3 binding patterns. Step 1b normalization drops intermediate QN segments for 5+ segment paths — potential resolution failure. Idiomatic SysML uses import + `.` chain (CHAIN binding), not deep `::` paths (REFERENCE). Snapshot pending SysIDE validation. See PHASE2_AUDIT_ACTIONS.md C6 UPDATE. |
| 8 | sum() is only recognized aggregation | Out of scope | Feature request, not refactor |
| 9 | Inherited attribute misclassification in `_classify_attribute_expression` | C05 fix (before Phase 3 recommended) | Classifier assumes flat namespace; SysIDE resolves inherited QNs to supertype. 5 of 6 test patterns affected. Fix requires supertype chain walk in Step 2b + C03 extraction enrichment. See Doc 16 Known Issues. |
| 10 | UNRESOLVABLE classification likely dead code for valid SysML | Document only | SysIDE always resolves attribute QNs; empty-QN fallback (Step 2d) unreachable without parser bugs. Retain as defensive fallback. |
| 11 | `endswith()` false positive in alias detection (`hierarchy_resolver.py:550-557`) | Deferred to Phase 7 | `source_path.endswith(agg.attribute_name)` matches `"child.total_cost"` against `"total_cost"`. Fix: `source_path == agg.attribute_name or source_path.endswith("." + agg.attribute_name)`. No fixture exercises this. Low risk — identified in C5 alias_agg_probe audit. |

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

1. **14 compat-only MODULE_OUTPUT resolutions across 2 models.** 12 in catf_mfe (cross-scope
   `minor_calc.a` CHAIN bindings — consumers in different radial build layers than the
   `plasma_region` producer) + 2 in solar_battery (REFERENCE secondary: `annualized_om.p_net_kw`
   via Key_F, `annualized_financial.total_capex` via Key_E_stripped). C11b spike corrected from 13
   to 14 — the second solar_battery case was missed by C11a typed-reachability check. These resolved
   through the deprecated `resolve()` cascade; C11b migrated them to typed lookups (Key_A aliases
   for catf_mfe, Key_F scoped registration for solar_battery case 1).

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

### C5 Alias Agg Probe (Phase 2 Audit) (2026-02-17)

1. **REQ-HR-07 alias detection works correctly with real SysML data.** The
   `hierarchy_resolver.py:550-557` code path successfully detects `:>> reported_cost = total_cost`
   as a CHAIN alias for the `sum(widget.total_cost)` aggregation. `agg.aliases = ["reported_cost"]`.

2. **Full pipeline succeeds with alias-based CalcUsage resolution.** The pipeline produces 4
   modules in correct topological order: `cost_model → total_cost (agg) → margin_calc → report_calc`.
   The `report_calc` CalcUsage binds `cost_input = reported_cost` (through the alias) and resolves
   correctly to the aggregation output.

3. **Literal multiplicity `[3]` produces `count_attribute_name=None`.** Same pattern as issue22.
   The `sum()` walker logs a warning ("no multiplicity data for 'widget'") but still creates the
   SumTerm with `multiplicity_attr=None`. The SumTerm transformation skips parametric multiply
   when no count attribute exists.

4. **Potential `endswith()` false positive in alias detection.** The check
   `sibling.source_path.endswith(agg.attribute_name)` would match dotted paths like
   `"child.total_cost"` against `attribute_name="total_cost"`. This could incorrectly alias
   a child reference. No fixture exercises this edge case. Low risk — documented for future
   investigation if a model triggers it.

### C6 Deep Cross-Scope Probe (Phase 2 Audit) (2026-02-17)

1. **Step 1b normalization drops intermediate QN segments for deep paths.** The current code
   at `_resolve_binding_via_registry()` splits on `::` and takes only `parts[-2]` and
   `parts[-1]`. For a 6-segment path like `A::B::C::D::E::F`, this extracts `E.F`, discarding
   `B::C::D`. The OutputRegistry ScopedKey includes the full instance path (e.g.,
   `station.array.sensor.core`), so the 2-segment lookup `core.metric_value` will not match.
   **C11b typed dispatch fix**: construct full `ScopedKey` from ALL intermediate segments.

2. **Idiomatic SysML v2 cross-scope references use import + `.` chain (CHAIN), not deep `::` (REFERENCE).**
   Evidence from catf_mfe: all cross-package bindings use `private import Package::part;`
   then `in x = part.attr;` — producing CHAIN bindings. The `::` notation is used for
   self-references within the same part (`catf_physics::p_fusion`). Deep `::` REFERENCE
   bindings are non-idiomatic and may only arise from programmatic model generation.

3. **Deep CHAIN bindings (4+ dot levels) are more practically relevant than deep REFERENCE.**
   Pattern A (`station.array.derived.derived_value`) exercises a 4-level feature chain,
   which is how real models access deeply nested outputs. This is the pattern that C11b
   and C12 should prioritize for deep cross-scope resolution support.

4. **SysIDE `::` navigation through parts (not just packages) is confirmed for 2 segments**
   (catf_mfe: `catf_physics::p_fusion`), **but untested at 5+ segments.** Pattern B
   (`measurement_system::station::array::sensor::core::metric_value`) may be rejected by
   SysIDE or parsed differently at deep nesting levels. Snapshot capture will determine.

5. **The Step 1b limitation is a C11b concern, not a C6 concern.** The fixture model
   documents the potential failure, but the actual fix belongs in the typed dispatch
   migration (C11b), where `_resolve_binding_via_registry()` is rewritten to use
   `ScopedKey` construction from all path segments.

### C12 Input Resolver (2026-02-17)

1. **Strategy A is the dominant aggregation resolution path (94% hit rate).** 48/51 refs resolve
   via ScopedRegistryLookup across 3 models. Strategy C (ChainRedefinitionFollow) resolves 26/51,
   all of which are also resolved by A with the same channel. Zero ordering conflicts between
   A-first and C-first — safe to use the design doc's A-C-B-D ordering.

2. **Strategy B (SysMLQNLookup) and Strategy D (DesignAttributeLookup) are zero-exercise for
   aggregation scope.** No aggregation term ref contains `::`. No aggregation entry point
   duplicates a design attribute name. Both implemented for completeness; tested only with
   constructed ResolutionContext data.

3. **No natural REQ-DRA-04 overlap in fixture models.** CalcUsage bindings and aggregation terms
   reference different parts in different scopes. Cross-path consistency tested by constructing
   ResolutionContext from CalcUsage binding metadata. Solar_battery: all CHAIN MODULE_OUTPUT
   resolutions match through both paths.

4. **STANDARD_STRATEGIES not needed.** No non-aggregation caller identified for resolve_input().
   Removed default parameter — always require explicit strategies argument.

5. **graph_builder.py integration deferred to C16.** The resolve_input() function is proven
   equivalent to `_resolve_aggregation_input_channel()` via regression test (51/51 refs match).
   Wiring the call sites is the Aggregation Module Factory's responsibility (C16, Phase 4).

### X02 Dual Resolution Consistency (2026-02-17)

1. **Backtracker REFERENCE Step 2 not replicated by Strategy B.** The backtracker's
   `_resolve_reference_dispatch` Step 2 (leaf + parent_part scoped lookup) resolves
   solar_battery `annualized_om|p_net_kw` via Key_F (`solar_battery_plant.p_net_kw`).
   Strategy B normalizes to `annualized_om.p_net_kw` (penultimate + last `::` segment),
   which doesn't match. This is expected — REFERENCE bindings are not aggregation scope
   (C12 spike: zero `::` in aggregation refs). Not a consistency violation.

2. **All CHAIN cross-path verifications pass perfectly across 3 models.** Every CHAIN
   MODULE_OUTPUT from the backtracker matches resolve_input with AGG_STRATEGIES for
   solar_battery, catf_mfe, and chain_spike. Strategy A is sufficient for all CHAIN cases.

3. **FORMULA SysML QN registration complete.** Every FORMULA channel in the attribute
   resolution map has a corresponding SysML QN key in the registry.

### C18 Graph Assembly (2026-02-17)

1. **Baseline comparison requires two normalizations for snapshot-vs-live pipelines.** CalcUsage
   modules get `compilability='unknown'` from `build_full_graph_from_snapshot()` because
   `compilation_results=None` (AST fields null in snapshots). FORMULA and aggregation modules set
   compilability directly in their factories, so those match. Also, `entry_point_groups` parameter
   ordering within groups differs between live and snapshot pipelines (dict iteration order differences
   in orphan EP collection). Both are documented in the baseline comparison test.

2. **`build_full_graph_from_snapshot()` (from C17) is the complete Checkpoint 4 vehicle.** It
   exercises the full pipeline: extraction → backtracker → 3 module factories → entry point
   classification → topological sort → channel validation → ComputationGraph assembly. All 3
   baseline models (solar_battery, chain_spike, attr_expr_probe) match their Phase 0 baselines.

3. **All 34 C18 tests pass on first run.** Confirms graph assembly is conformance-only — no
   production code changes needed. The toposort, channel validation, and ComputationGraph shape
   all behave as documented in design intent doc 07.

### C19 Orchestrator Step Ordering (2026-02-17)

1. **FORMULA QNs and design attribute QNs have zero overlap in all fixture models.** The
   `_remove_formula_from_design_attrs()` safety net function returns 0 for all 6 models.
   FORMULA QNs (`sysml_to_python_qualified_name(owning_part_qn)__python_name`) and design
   attribute QNs (from `extract_design_attributes()`) occupy disjoint attribute namespaces.
   The removal logic is verified correct with constructed overlap data.

2. **`build_pipeline_context()` step ordering verified deterministically via AST.** The
   static analysis pattern (C04, C07, C09) extends cleanly to the orchestrator. All 10 major
   call sites appear in strict DAG order. `build_computation_graph` is the last significant
   call before `return PipelineContext(...)`.

3. **REQ-PIPE-07 (generation uses ONLY ComputationGraph) has 9 violating files.** All files
   in `generation/` that import from `extraction/` or `analysis/` were counted. This is the
   known violation baseline for Phase 7.6 to drive toward zero.

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

### C16 Aggregation Module Factory (2026-02-17)

1. **LITERAL redef fallback is naturally exercised by SingletonTerms, not SumTerms.**
   The plan assumed "permitting soft costs" are SumTerms, but Permitting_Interconnect
   is referenced as SingletonTerms in Site_Infrastructure aggregations. All SumTerms in
   solar_battery resolve via channel successfully. SumTerm literal fallback path is valid
   code but requires constructed test data to exercise.

2. **Strategy 1 (type-aware) in `_find_literal_redefinition` is essential for aliased usage
   names.** When the PartUsage name differs from the PartDef name (e.g., `permitting` usage →
   `Permitting_Interconnect` PartDef), Strategy 2 (name-based) fails because
   `sanitize_name("Permitting_Interconnect").lower()` = `"permitting_interconnect"` !=
   `"permitting"`. Strategy 1 resolves this via `usage_type_map[(owning_qn, "permitting")]`
   → `"Permitting_Interconnect"`.

3. **All 9 LocalTerms in solar_battery resolve naturally.** 8 via sibling aggregation output
   (capital_cost, raw_material_cost in each assembly), 1 via EXPOSE_PURE alias
   (misc_hardware_cost in Solar_Array). No natural EP fallback case exists. The
   `test_localterm_entry_point_fallback` uses a synthetic `LocalTerm("nonexistent_cost_attr")`.

4. **C16 produced 32 tests, not the estimated 25.** 6 tests parametrized over 2 models =
   12 parametrized + 20 solar_battery-specific. Some plan-listed tests were consolidated,
   but constructed edge cases added new tests.

### C17 Entry Point Classification (2026-02-17)

1. **solar_battery has zero DESIGN_ATTRIBUTE EPs from the classifier (Path 1).** Design
   attribute QNs use library-qualified names (`SolarBatteryLibrary__PVModuleCostCalc__cost_per_watt`)
   while EP QNs use design-qualified names (`SolarBatteryDesign__solar_battery_plant__...`). The QNs
   never match in `design_attr_by_qname`, so all solar_battery EPs are classified as LIBRARY_DEFAULT
   or USAGE_LITERAL. DESIGN_ATTRIBUTE EPs come exclusively from factory construction (Path 2).
   catf_mfe_model produces all 3 types from the classifier.

2. **13 solar_battery EPs have param_group=None from the classifier.** Deeply-nested QNs
   (e.g., `SolarBatteryDesign__solar_battery_plant__battery_system__battery_pack__cost_model__capacity_kwh`)
   don't match any `ParameterGroupDeriver.classify()` pattern. These become orphans handled by
   Step 6.8 in `build_computation_graph()`. catf_mfe and chain_spike have zero param_group=None EPs.

3. **REQ-EPC-04 is a graph-level invariant, not a classifier-level invariant.** The classifier
   sets `param_group = group_deriver.classify(qname)` which CAN return None. The orphan handling
   at Step 6.8 ensures every EP belongs to some ParameterGroup after full graph assembly.

4. **`build_full_graph_from_snapshot()` helper enables graph-level verification.** Calling
   `build_computation_graph()` with all inputs exercises the full Path 1 + Path 2 + Step 6.6
   rebuild + Step 6.8 orphan pipeline. Reusable for C18 (Graph Assembly).

---

## Design Doc Amendments

> Design intent doc updates triggered by implementation findings.
> Tracked here; applied in a dedicated PROMPT-plan session, not during build.

| Doc | Amendment needed | Triggered by | Applied? |
|-----|-----------------|--------------|----------|
| 01-extraction.md | Note EXPRESSION binding type has zero coverage in fixture models | C03 conformance (2026-02-17) | Yes — §Binding Types EXPRESSION coverage note |
| COMPONENT_CHECKLIST.md | C03 AC8: clarify "all binding types" — solar_battery has 4 of 5 (EXPRESSION absent) | C03 conformance (2026-02-17) | Yes — C03 AC lines 76, 82 |
| 10-output-registry.md | Added REQ-OR-08: Key_A diagnostic-only, resolution SHALL raise instead of silent fallback | Design review discussion (2026-02-17) | Yes |
| 11-analysis-backtracker.md | Added REQ-BT-08: Step 1 raises `UnscopedResolutionError`; rewrote Step 1 section and concrete walkthrough | Design review discussion (2026-02-17) | Yes |
| 03-resolution-overview.md | Strengthened REQ-RES-07: unscoped Key_A fallback explicitly prohibited | Design review discussion (2026-02-17) | Yes |
| 04-input-resolver.md | Strategy A cross-reference to REQ-OR-08; flagged same Key_A ambiguity concern | Consistency review (2026-02-17) | Yes |
| 24-dual-resolution-architecture.md | Updated REQ-DRA-03 and Stage 1 cascade description to reflect Key_A error behavior | Consistency review (2026-02-17) | Yes |
| IMPLEMENTATION_PLAN.md Step 1.4 | Clarified "compile every output from snapshot calc defs" → "verify compiler with real calc def metadata from snapshots" | C04 conformance — AST serialization boundary (2026-02-17) | Yes |
| IMPLEMENTATION_PLAN.md Deferred Issues | Reassigned issue #1 (".() syntax") from C04 to C06/C07 | C04 conformance — reconstruct_expression() not used by expression compiler (2026-02-17) | Yes |
| 16-computed-attributes.md | Note UNRESOLVABLE has zero coverage in fixture models | C05 conformance (2026-02-17) | Yes — §UNRESOLVABLE coverage note + Known Issues |
| COMPONENT_CHECKLIST.md | Consider adding REQ-CA-08 (FORMULA-to-FORMULA limitation) to AC list | C05 conformance — present in design doc but absent from checklist (2026-02-17) | Yes — C05 AC line 117 |
| COMPONENT_CHECKLIST.md | C06: changed doc ref from `01-extraction.md` to `25-hierarchy-resolver.md`; added REQ-HR-01 through REQ-HR-07; clarified "Template detection" AC to "part_usage_names maps assembly PartDefs to child names" | C06 conformance (2026-02-17) | Yes |
| 25-hierarchy-resolver.md | Note REQ-HR-07 alias detection has zero positive-case fixture coverage | C06 conformance (2026-02-17) | Yes — superseded by C5 probe (line 1122); §Alias Detection coverage note |
| 27-typed-registry-refactor.md | NEW: Type system, typed registries, eliminated keys, dispatch tables | Typed Registry Refactor spec (2026-02-17) | Yes (TRR-1) |
| 09-data-models.md | Add CanonicalChannel, ScopedKey types; typed registries replace dict[str,str] | TRR spec (2026-02-17) | Yes (TRR-2) |
| 15-naming-conventions.md | Correct REQ-NC-07; remove dead keys from tables; add typed key rows | TRR spike findings (2026-02-17) | Yes (TRR-3) |
| 10-output-registry.md | Typed registries replace flat dict; resolve() → typed lookups; dead keys removed | TRR spec (2026-02-17) | Yes (TRR-4) |
| 11-analysis-backtracker.md | REQ-BT-08 corrected; Step 1 deleted; type-directed dispatch | TRR spike findings (2026-02-17) | Yes (TRR-5) |
| 04-input-resolver.md | Strategies use typed registries; Key_A warning removed | TRR spec (2026-02-17) | Yes (TRR-6) |
| 24-dual-resolution-architecture.md | Strategy tables rewritten for typed registries | TRR spec (2026-02-17) | Yes (TRR-7) |
| 03-resolution-overview.md | Scope Problem updated; Key_A refs removed; typed registries | TRR spec (2026-02-17) | Yes (TRR-8) |
| 19-ast-dispatch-invariant.md | Correct "8 files" → "8 multi-type dispatch functions across 5 files"; note `_extract_single_binding` not `extract_binding_info` | C07 conformance (2026-02-17) | Yes — §Dispatch Site Audit heading + Other Sites table |
| 19-ast-dispatch-invariant.md | Note 5 additional single-type helper functions exist (13 total with `is_instance` on expression types) | C07 conformance (2026-02-17) | Yes — §Dispatch Site Audit note block |
| IMPLEMENTATION_PLAN.md Step 2.3 | Change "REQ-AS-01 through REQ-AS-07" to "REQ-AS-01 through REQ-AS-08" in acceptance criteria | C10 conformance (2026-02-17) | Yes |
| 04-input-resolver.md | Add `CanonicalChannel` return type to strategy signatures and code examples; remove stale Key_A reference | Phase 2 audit — TRR validation criterion 5 (2026-02-17) | Yes |
| 27-typed-registry-refactor.md | Add `_compat` bridge dict transitional architecture section | C08 conformance — dead keys load-bearing through backtracker (2026-02-17) | Yes |
| 16-computed-attributes.md | Note inherited attribute misclassification: QNs resolve to supertype namespace, causing FORMULA→EXPOSE_COMPUTED misclassification. Classifier needs supertype chain walk. | C3 probe (Phase 2 audit) (2026-02-17) | Yes (2026-02-17) — Known Issues §Inherited Attribute Misclassification + Step 2b annotation |
| 16-computed-attributes.md | Note UNRESOLVABLE is likely dead code for valid SysML — SysIDE always resolves QNs | C3 probe (Phase 2 audit) (2026-02-17) | Yes (2026-02-17) — Known Issues §UNRESOLVABLE Likely Dead Code + UNRESOLVABLE section note + Step 2d annotation |
| 11-analysis-backtracker.md | Note EXPRESSION bindings silently skipped (source_path=None → no resolution). Gap for C11b | C11 conformance (2026-02-17) | Yes (2026-02-17) — DFS §3 EXPRESSION bullet added |
| 11-analysis-backtracker.md | Document 14 compat-only resolutions: 12 catf_mfe cross-scope CHAIN, 2 solar_battery REFERENCE secondary (C11b spike corrected count from 13). C11b migration concern | C11 conformance (2026-02-17) | Yes (2026-02-17) — Compat-Only Resolution Migration section added |
| IMPLEMENTATION_PLAN.md Deferred Issues | Add issues #9 (inherited attribute misclassification) and #10 (UNRESOLVABLE dead code) to Deferred Issues table | C3 probe (Phase 2 audit) (2026-02-17) | Yes (2026-02-17) |
| 09-data-models.md | Add footnote to ComputedAttributeClassification enum noting inherited attr misclassification and UNRESOLVABLE dead code status | C3 probe (Phase 2 audit) (2026-02-17) | Yes (2026-02-17) |
| 01-extraction.md | Add note to Part Definitions section about supertype chain data needed for C05 classifier | C3 probe (Phase 2 audit) (2026-02-17) | Yes (2026-02-17) |
| COMPONENT_CHECKLIST.md | C05: update UNRESOLVABLE AC, add inherited attr AC + sibling_attr_names AC; C03: add supertype chain AC | C3 probe (Phase 2 audit) (2026-02-17) | Yes (2026-02-17) |
| 25-hierarchy-resolver.md | Update REQ-HR-07 note: positive-case coverage now exists in alias_agg_probe. Note `endswith()` false-positive edge case for dotted source_paths | C5 probe (Phase 2 audit) (2026-02-17) | Yes — §Alias Detection coverage note with endswith edge case |
| COMPONENT_CHECKLIST.md | C06: Update REQ-HR-07 note from "zero positive-case coverage" to "alias_agg_probe exercises positive case" | C5 probe (Phase 2 audit) (2026-02-17) | Yes — C06 AC line 132 |
| 11-analysis-backtracker.md | Note Step 1b normalization limitation: only extracts last 2 segments of `::` QN, losing intermediate hierarchy for 5+ segment paths. Fix in C11b typed dispatch. | C6 probe (Phase 2 audit) (2026-02-17) | Yes (2026-02-17) — REFERENCE Step 2 limitation note added |
| IMPLEMENTATION_PLAN.md Deferred Issues | Update issue #7 from "Out of scope" to "Partially addressed (C6 probe)" with Step 1b normalization analysis | C6 probe (Phase 2 audit) (2026-02-17) | Yes (2026-02-17) |
| 04-input-resolver.md | Remove STANDARD_STRATEGIES default from resolve_input() signature; always require explicit strategies | C12 spike: no non-aggregation caller (2026-02-17) | Yes (2026-02-17) — signature updated, description revised |
| 04-input-resolver.md | Correct REQ-IR-05 "DirectRegistryLookup" → "SysMLQNLookup" | C12 plan Issue #2 (2026-02-17) | Yes (2026-02-17) — also fixed position number (2→1) |
| 04-input-resolver.md | Note Strategy B zero-exercise for aggregation; Strategy D is no-op placeholder | C12 spike findings (2026-02-17) | Yes (2026-02-17) — coverage notes added to §B and §D |
| 24-dual-resolution-architecture.md | Note Strategy B asymmetry: backtracker REFERENCE Step 2 (leaf + parent scope) not replicated by SysMLQNLookup | X02 conformance finding #1 (2026-02-17) | Yes (2026-02-17) — Known Asymmetry subsection added to Strategy Overlap |
| 18-literal-value-propagation.md | Note LITERAL redef fallback naturally exercised by SingletonTerms in solar_battery, not SumTerms. SumTerm fallback path valid but not naturally tested | C16 conformance finding #1 (2026-02-17) | Yes (2026-02-17) — §Where It's Called conformance note added |
| 05-module-factory.md | Note Strategy 1 (type-aware) essential when usage name differs from PartDef name (permitting → Permitting_Interconnect) | C16 conformance finding #2 (2026-02-17) | Yes (2026-02-17) — §4 Aggregation Modules conformance note added |
| 06-entry-point-classifier.md | Note solar_battery has zero DESIGN_ATTRIBUTE EPs from Path 1 classifier. catf_mfe exercises all 3 types. | C17 conformance finding #1 (2026-02-17) | Yes (2026-02-17) — Path 1 coverage note added |
| 06-entry-point-classifier.md | Clarify REQ-EPC-04: param_group may be None from classifier; orphan handling (REQ-EPC-05) ensures graph-level invariant | C17 conformance finding #3 (2026-02-17) | Yes (2026-02-17) — REQ-EPC-04 description expanded |

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
| C5 Alias Agg Probe (audit) | 1250 | 10 | 1260 (+5 xfail) | 2026-02-17 |
| C11b Typed Dispatch (C11b) | 1260 | 17 conformance (net +13 after unit test updates) | 1273 (+5 xfail) | 2026-02-17 |
| C12 Input Resolver | 1273 | 26 | 1299 (+5 xfail) | 2026-02-17 |
| C13 ParameterGroupDeriver | 1304 | 30 | 1334 (+5 xfail) | 2026-02-17 |
| X02 Dual Resolution | 1329 | 20 | 1349 (+5 xfail) | 2026-02-17 |
| C14 CalcUsage Factory | 1349 | 48 | 1397 (+5 xfail) | 2026-02-17 |
| C15 FORMULA Factory | 1397 | 34 | 1431 (+5 xfail) | 2026-02-17 |
| C16 Aggregation Factory | 1431 | 32 | 1463 (+5 xfail) | 2026-02-17 |
| C17 Entry Point Classifier | 1463 | 35 | 1498 (+5 xfail) | 2026-02-17 |
| C18 Graph Assembly | 1498 | 34 | 1532 (+5 xfail) | 2026-02-17 |
| C19 Orchestrator Step Ordering | 1532 | 39 | 1571 (+5 xfail) | 2026-02-17 |
