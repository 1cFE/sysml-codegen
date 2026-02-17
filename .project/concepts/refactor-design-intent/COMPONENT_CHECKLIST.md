# Component Checklist: Refactored Design

Cross-reference of every implementable component against design intent documents,
listing the requirements, interfaces, and acceptance criteria each must satisfy.

---

## Legend

- **Doc**: Design intent document number
- **REQs**: Requirement IDs that govern this component
- **Inputs/Outputs**: Data models consumed and produced
- **AC**: Acceptance criteria (all must pass with real data, NO MOCKS)

---

## Layer 0: Foundation (no pipeline dependencies)

### C01 — Data Models
- **Doc**: [09-data-models.md](09-data-models.md)
- **REQs**: REQ-DM-01 through REQ-DM-08
- **Current location**: `extraction/data_models.py`, `core/models.py`, `resolution/models.py`
- **Target location**: same (or consolidated per refactor)
- **Interfaces**:
  - 7 enums: BindingType, RedefinitionType, ComputedAttributeClassification, Compilability, ExpressionNodeType, BindingResolutionType, EntryPointType
  - Extraction models: CalculationDefinitionData, CalcUsageData, BindingInfo, PartDefinitionData, RedefinitionData, MultiplicityData, HierarchyExtractionResult, AttributeInfo, AggregationExpressionData, ScopedAggregationData
  - Analysis models: BacktrackingResult, DesignAttributeData, DerivedParameterGroup
  - Core models: BindingResolution, ChannelAlias, OutputRegistry
  - Resolution models: ComputationGraph, PipelineModule, ModuleInput, ModuleOutput, InputSource, EntryPoint, ParameterGroup
- **AC**: *(all verified 2026-02-17 — 91 tests in `tests/conformance/test_data_models.py`)*
  - [x] Every model referenced in docs 00-24 exists and is importable
  - [x] Every enum lists ALL values documented in 09
  - [x] Field lists match doc 09 exactly (names, types, optionality)
  - [x] Pydantic models validate with real data (construct from extraction output)
  - [x] Containment hierarchy matches doc 09 diagram
  - [x] AggregationExpressionData has all 15 fields
  - [ ] NewType wrappers (SysMLQN, EQN, PQN, CanonicalChannel, ScopedKey) defined and importable
  - [ ] Field types in extraction/analysis/core/resolution models use typed names per Doc 09 table
  - [ ] `CanonicalChannel` wraps PQN-format output channel names; constructor rejects `::` and `.`
  - [ ] `ScopedKey` wraps dotted hierarchy keys; constructor rejects `::`; `from_eqn()` replaces `derive_key_c()`

### C02 — Naming Conventions
- **Doc**: [15-naming-conventions.md](15-naming-conventions.md)
- **REQs**: REQ-NC-01 through REQ-NC-07
- **Current location**: `analysis/qualified_names.py`, `core/qualified_names.py`, `core/identifier_types.py`, `resolution/identifier_types.py`
- **Target location**: consolidate to `core/` (per refactor)
- **Functions under test**:
  - `sanitize_name()` — 6 transforms in order
  - `build_element_qualified_name()` — EQN from SysML QN
  - `build_parameter_qualified_name()` — PQN = EQN + __ + param
  - `get_module_name()` — EQN lowercased
  - `derive_module_type()` — namespace.ElementNameModule
  - `get_channel_name()` — PQN format
  - Key_C derivation — split EQN on __, drop segment[0], join with `.`
- **AC**: *(all verified 2026-02-17 -- 46 tests in `tests/conformance/test_naming_conventions.py`)*
  - [x] `sanitize_name()` applies all 6 transforms in documented order
  - [x] Reserved word handling for: class, def, import, from, return, yield
  - [x] EQN/PQN/module_name/module_type/channel_name all derive deterministically from SysML QN
  - [x] Key_C derivation strips design prefix correctly
  - [x] No `::` keys in any registry key format
  - [x] Test with names from every fixture model (sample, solar_battery, catf_mfe)

---

## Layer 1: Extraction (upstream of everything)

### C03 — SysMLDataExtractor
- **Doc**: [01-extraction.md](01-extraction.md)
- **REQs**: REQ-EXT-01 through REQ-EXT-07
- **Current location**: `extraction/extractor.py`, `extraction/usage_extractor.py`
- **Interfaces**:
  - Input: `.sysml` file paths
  - Output: `list[CalculationDefinitionData]`, `list[CalcUsageData]`, `list[PartDefinitionData]`, `HierarchyExtractionResult`
- **AC**: *(all verified 2026-02-17 — 44 tests in `tests/conformance/test_extractor.py`)*
  - [x] One `CalculationDefinitionData` per calc def in model
  - [x] Every binding has exactly one BindingType (CHAIN, REFERENCE, LITERAL, EXPRESSION, UNBOUND)
  - [x] Every redefinition classified as exactly one RedefinitionType (LITERAL, CHAIN, EXPRESSION)
  - [x] Every aggregation expression decomposed into typed terms (SumTerm, SingletonTerm, LocalTerm)
  - [x] Template calc usages produce one virtual CalcUsageData per PartUsage instance
  - [x] Extraction imports NOTHING from analysis/, resolution/, or generation/
  - [x] `output_expression_asts` preserves raw SysIDE AST nodes — field+type verified; content deferred to C04 (ASTs null in snapshots per serialization boundary)
  - [x] Verified with solar_battery_model (4 of 5 binding types; EXPRESSION absent from all fixtures) and catf_mfe_model (has hierarchy)

### C04 — Expression Compiler
- **Doc**: [14-expression-compiler.md](14-expression-compiler.md)
- **REQs**: REQ-EC-01 through REQ-EC-07
- **Current location**: `extraction/expression_compiler.py`, `extraction/expression_utils.py`
- **Interfaces**:
  - Input: `CalculationDefinitionData` with `output_expression_asts`
  - Output: compiled Python expressions, compilability verdicts per output
- **AC**: *(all verified 2026-02-17 — 31 tests in `tests/conformance/test_expression_compiler.py`)*
  - [x] FCE checked BEFORE OE at every dispatch site (doc 19 invariant)
  - [x] N-ary operands left-folded into binary nodes
  - [x] Unit annotations stripped from expressions
  - [x] Every compiled expression validates via `ast.parse()`
  - [x] Cycles mark all outputs MANUAL_REQUIRED
  - [x] Worst-case roll-up for calc-level compilability
  - [x] Undeclared intermediates discovered iteratively
  - [x] Test with real calc defs from all fixture models (metadata + SysIDE boundary stub)

### C05 — Computed Attribute Extractor
- **Doc**: [16-computed-attributes.md](16-computed-attributes.md)
- **REQs**: REQ-CA-01 through REQ-CA-07
- **Current location**: `extraction/computed_attribute_extractor.py`
- **Interfaces**:
  - Input: PartDefinitionData attribute expressions
  - Output: ComputedAttributeClassification per attribute, ComputedAttributeData
- **AC**: *(all verified 2026-02-17 — 37 tests in `tests/conformance/test_computed_attributes.py`)*
  - [x] Every attribute expression classified as exactly one of: FORMULA, EXPOSE_PURE, EXPOSE_COMPUTED, LITERAL, UNRESOLVABLE
  - [x] FORMULA attributes compile to valid Python
  - [x] EXPOSE_PURE only for PartUsage-level single-FCE
  - [x] LITERAL attributes excluded (no module, no alias)
  - [x] UNRESOLVABLE logged but no module/alias created — zero fixture coverage (same gap as C03 EXPRESSION)
  - [x] Self-reference excluded from input_names
  - [x] Test with attr_expr_probe fixture (primary), solar_battery (cross-model), catf_mfe (cross-model)

### C06 — Hierarchy Resolver
- **Doc**: [25-hierarchy-resolver.md](25-hierarchy-resolver.md), [13-aggregation-scoping.md](13-aggregation-scoping.md)
- **REQs**: REQ-HR-01 through REQ-HR-07
- **Current location**: `extraction/hierarchy_resolver.py`
- **AC**: *(all verified 2026-02-17 — 36 tests in `tests/conformance/test_hierarchy_resolver.py`)*
  - [x] `part_usage_names` correctly maps assembly PartDefs to child PartUsage names for all fixture models
  - [x] Part usage hierarchy extracted with correct parent/child relationships (`usage_type_map` tuple keys)
  - [x] Multiplicity data extracted from PartUsage nodes (pv_module=20, inverter=4, battery_pack=8)
  - [x] Aggregation term type classification correct (SumTerm, SingletonTerm, LocalTerm); all 3 present in solar_battery
  - [x] FCE classified as SingletonTerm (not LocalTerm) — verified by static analysis + dotted source_path check
  - [x] Verified with solar_battery_model (78 redefs, 13 overrides, 3 mults, 20 aggs), issue22_model (edge cases), cross-model on all 6 fixtures
  - Note: REQ-HR-07 alias detection has zero positive-case fixture coverage (no model has CHAIN sibling aliases)

### C07 — AST Dispatch Invariant
- **Doc**: [19-ast-dispatch-invariant.md](19-ast-dispatch-invariant.md)
- **REQs**: REQ-AST-01 through REQ-AST-07
- **Cross-cutting**: affects C04, C05, C06
- **AC**: *(all verified 2026-02-17 — 26 tests in `tests/conformance/test_ast_dispatch_invariant.py`)*
  - [x] Audit: every dual-check site checks FCE before OE (5 parametrized static analysis tests)
  - [x] Comment present at every dual-check site (5 parametrized tests; comments added to `_extract_single_binding` and `_extract_default_value`)
  - [x] All 8 multi-type dispatch sites follow canonical ordering: FCE, OE, FRE, Literal (with documented deviation for elif-chain sites)
  - [x] Regression test: if FCE/OE order reversed, test fails (behavioral test with dual-match mock)
  - Note: Plan listed `extract_binding_info` for site #4; actual function is `_extract_single_binding` in usage_extractor.py

---

## Layer 2: Core Infrastructure

### C08 — Output Registry (Typed)
- **Doc**: [10-output-registry.md](10-output-registry.md), [27-typed-registry-refactor.md](27-typed-registry-refactor.md)
- **REQs**: REQ-OR-01 through REQ-OR-08
- **Current location**: `core/output_registry.py`
- **Interfaces**:
  - `register_scoped(ScopedKey, CanonicalChannel)` — Phase 1 CalcUsage (Key_C) and Aggregation (Key_E_stripped)
  - `register_sysml_qn(SysMLQN, CanonicalChannel)` — Phase 1c FORMULA SysML QN keys
  - `register_alias(ScopedKey, CanonicalChannel)` — Phase 2-4 aliases with phase enforcement
  - `scoped_lookup(ScopedKey) -> CanonicalChannel | None` — primary lookup for CHAIN bindings
  - `sysml_qn_lookup(SysMLQN) -> CanonicalChannel | None` — REFERENCE binding lookup
  - `alias_lookup(ScopedKey) -> CanonicalChannel | None` — cross-package EXPOSE_PURE lookup
  - `ScopedKey.from_eqn(usage_eqn, attr_name)` — replaces `derive_key_c()`
- **AC**:
  - [ ] Three typed registries: scoped (`dict[ScopedKey, CanonicalChannel]`), SysML QN (`dict[SysMLQN, CanonicalChannel]`), alias (`dict[ScopedKey, CanonicalChannel]`)
  - [ ] No `dict[str, str]` — all registry internals use typed keys and values
  - [ ] No `resolve(key)` single-method API — each registry has its own typed lookup
  - [ ] Key_A, Key_D, Key_E full, Key_F, bare keys NOT registered (eliminated per FR-3)
  - [ ] Scoped and SysML QN registries: unique by construction (no collision policy needed)
  - [ ] Alias registry: first-wins collision policy retained (with warning)
  - [ ] `register_alias()` enforces phase ordering (target must already be canonical)
  - [ ] Phase 2-4 aliases resolve through typed lookup before registering
  - [ ] `ScopedKey.from_eqn()` strips design prefix, joins with dots (replaces `derive_key_c()`)
  - [ ] `canonical_channels` property returns `frozenset[CanonicalChannel]`
  - [ ] Verified with real channels from solar_battery and catf_mfe extraction output

### C09 — Virtual Binding Rewrite
- **Doc**: [12-virtual-binding-rewrite.md](12-virtual-binding-rewrite.md)
- **REQs**: REQ-VBR-01 through REQ-VBR-07
- **Current location**: `generation/initialization.py` (to be extracted)
- **Interfaces**:
  - Input: `list[CalcUsageData]`, `HierarchyExtractionResult`
  - Output: mutated `CalcUsageData.bindings` (in-place)
- **AC**:
  - [ ] Override index keyed by `(full_parent_path, leaf_attribute_name)`
  - [ ] Deep-path joins intermediate segments with `__`
  - [ ] LITERAL override: sets binding_type=LITERAL, copies literal_value
  - [ ] CHAIN override: replaces source_path
  - [ ] Template copies (is_template=True) skipped
  - [ ] Already-LITERAL or no source_path skipped
  - [ ] Rewrite completes before downstream (backtracker, registry build)
  - [ ] Test: extract solar_battery, apply rewrite, verify binding changes

### C10 — Aggregation Scoping
- **Doc**: [13-aggregation-scoping.md](13-aggregation-scoping.md)
- **REQs**: REQ-AS-01 through REQ-AS-08
- **Current location**: `generation/initialization.py` (to be extracted)
- **Interfaces**:
  - Input: extraction aggregation data, PartDefinitionData, CalcUsageData
  - Output: `list[ScopedAggregationData]`, `list[ChannelAlias]`
- **AC**:
  - [ ] One ScopedAggregationData per design instance (one-to-many expansion)
  - [ ] Direct CalcUsage match strategy before child-walk fallback
  - [ ] Instance paths: `__`-separated converted to dotted, design prefix stripped
  - [ ] CHAIN aliases only for non-deep-path with `.` in source_path
  - [ ] Phase 1b registration of canonical channels per ScopedAggregationData
  - [ ] Phase 2 resolution of ChannelAlias before registering
  - [ ] module_eqn = `"{instance_path}__{attribute_name}"`
  - [ ] Test: solar_battery model produces expected scoped modules
  - [ ] Zero-instance case logs WARNING with PartDef QN and attribute name (REQ-AS-08)

---

## Layer 3: Analysis

### C11 — DependencyBacktracker (Type-Directed)
- **Doc**: [11-analysis-backtracker.md](11-analysis-backtracker.md), [24-dual-resolution-architecture.md](24-dual-resolution-architecture.md), [27-typed-registry-refactor.md](27-typed-registry-refactor.md)
- **REQs**: REQ-BT-01 through REQ-BT-08, REQ-DRA-01
- **Current location**: `analysis/dependency_backtracker.py`
- **Interfaces**:
  - Input: root calc usages, OutputRegistry (typed), CalcUsageData, CalculationDefinitionData
  - Output: `BacktrackingResult` (required_usages, dependency_graph, entry_points, binding_resolutions)
- **AC**:
  - [ ] Every non-literal binding resolved via `_resolve_binding_via_registry()`
  - [ ] CHAIN bindings (no `::` in source_path): ScopedKey → scoped registry, then alias registry (cross-package)
  - [ ] REFERENCE bindings (`::` in source_path): SysMLQN → SysML QN registry, then normalized ScopedKey → scoped registry
  - [ ] No Key_A references — type-directed dispatch replaces Step 1 cascade
  - [ ] No `UnscopedResolutionError` — eliminated with Key_A
  - [ ] Cycle detection via path tracking — cycles don't crash, they warn
  - [ ] Every binding resolves (fallback guarantees total resolution)
  - [ ] Key format: `"{usage_qn}|{param_name}"` for binding_resolutions
  - [ ] Topological sort produces dependency-first ordering
  - [ ] Self-reference guard prevents wiring module to its own output
  - [ ] Test with real typed OutputRegistry + real extraction from all fixture models

### C12 — Input Resolver (resolve_input, Typed)
- **Doc**: [04-input-resolver.md](04-input-resolver.md), [24-dual-resolution-architecture.md](24-dual-resolution-architecture.md), [27-typed-registry-refactor.md](27-typed-registry-refactor.md)
- **REQs**: REQ-IR-01 through REQ-IR-07, REQ-DRA-02
- **Target location**: `resolution/input_resolver.py` (new, extracted from graph_builder)
- **Scope**: Aggregation SumTerm/SingletonTerm inputs only. FORMULA uses pre-computed attribute resolution map (not resolve_input). LocalTerm uses factory-specific cascade.
- **Interfaces**:
  - `resolve_input(ref, ctx, strategies) -> InputSource`
  - `ResolutionContext`: frozen dataclass with typed output_registry, redefinitions, design_attrs, module_eqn, consumer_scope, instance_path
  - 4 strategies for aggregation SumTerm/SingletonTerm: A (ScopedRegistryLookup → `scoped_lookup(ScopedKey)`), B (SysMLQNLookup → `sysml_qn_lookup(SysMLQN)`), C (ChainRedefinitionFollow), D (DesignAttributeLookup)
- **AC**:
  - [ ] Always returns InputSource, NEVER raises
  - [ ] Strategies execute in declared order; first match wins
  - [ ] Strategy A produces `ScopedKey`, queries scoped registry (no Key_A ambiguity possible)
  - [ ] Strategy B queries SysML QN registry for `::` references (not REMOVAL_CANDIDATE — promoted to typed lookup)
  - [ ] Strategy C produces `ScopedKey` from chain target, queries scoped registry
  - [ ] Self-reference guard rejects wiring to own channels
  - [ ] ResolutionContext is immutable (frozen=True), holds typed OutputRegistry
  - [ ] AGG_STRATEGIES has ChainRedefinitionFollow at position 2 (before B)
  - [ ] Fallback produces entry_point (never unresolved)
  - [ ] Same reference in same scope produces same wiring as backtracker (REQ-DRA-04)

### C13 — ParameterGroupDeriver
- **Doc**: [17-parameter-group-deriver.md](17-parameter-group-deriver.md)
- **REQs**: REQ-PGD-01 through REQ-PGD-07
- **Current location**: `analysis/parameter_groups.py`
- **Interfaces**:
  - Input: DesignAttributeData, CalcUsageData, CalculationDefinitionData
  - Output: `list[DerivedParameterGroup]`, group classification per qualified name
- **AC**:
  - [ ] Every entry point in exactly one group
  - [ ] 4 indexes with strict precedence: attr > binding > unbound > literal
  - [ ] Grouping mirrors SysML source file structure
  - [ ] Filtered groups remove non-entry-point parameters
  - [ ] `classify()` checks indexes in precedence order
  - [ ] `get_default_value()` resolves through binding index
  - [ ] Group names follow `{snake_case_stem}_params` / `{PascalCaseStem}Params` convention

---

## Layer 4: Resolution (Module Construction)

### C14 — Module Factory: CalcUsage
- **Doc**: [05-module-factory.md](05-module-factory.md)
- **REQs**: REQ-MF-01, REQ-MF-02, REQ-MF-05, REQ-MF-08
- **Current location**: `resolution/graph_builder.py` (`_build_pipeline_module`)
- **Interfaces**:
  - Input: CalcUsageData, BacktrackingResult.binding_resolutions, CalculationDefinitionData
  - Output: `(PipelineModule, dict[str, EntryPoint])`
- **AC**:
  - [ ] Pure data transformer — no shared state mutation
  - [ ] Fails fast on missing binding_resolutions key
  - [ ] Every ModuleInput has exactly one InputSource (module_output or entry_point)
  - [ ] Single output uses field_name="root"; multi uses attribute names
  - [ ] Wiring matches binding_resolutions exactly

### C15 — Module Factory: FORMULA
- **Doc**: [05-module-factory.md](05-module-factory.md), [16-computed-attributes.md](16-computed-attributes.md)
- **REQs**: REQ-MF-01, REQ-MF-03, REQ-MF-05
- **Current location**: `resolution/graph_builder.py` (`_build_computed_attr_module`)
- **Interfaces**:
  - Input: ComputedAttributeData, ResolutionContext
  - Output: `(PipelineModule, dict[str, EntryPoint])`
- **AC**:
  - [ ] Pure data transformer
  - [ ] Sets is_computed_attribute=True
  - [ ] Sets compilability=FULLY_COMPILABLE
  - [ ] Uses pre-computed attribute resolution map (`_build_attribute_resolution_map()`) for input wiring
  - [ ] Every ModuleInput has exactly one InputSource
  - [ ] Always single-output with field_name="root"
  - [ ] Factory-created entry points have entry_type=DESIGN_ATTRIBUTE

### C16 — Module Factory: Aggregation
- **Doc**: [05-module-factory.md](05-module-factory.md), [18-literal-value-propagation.md](18-literal-value-propagation.md)
- **REQs**: REQ-MF-01, REQ-MF-04, REQ-MF-05, REQ-MF-06, REQ-MF-07, REQ-LVP-01 through REQ-LVP-07
- **Current location**: `resolution/graph_builder.py` (`_build_aggregation_module`)
- **Interfaces**:
  - Input: ScopedAggregationData, ResolutionContext, usage_type_map
  - Output: `(PipelineModule, dict[str, EntryPoint])`
- **AC**:
  - [ ] Pure data transformer
  - [ ] Handles SumTerm: wires to upstream, uses multiplicity, falls back to literal redef
  - [ ] Handles SingletonTerm: direct child reference, falls back to literal redef
  - [ ] Handles LocalTerm: 3 strategies (sibling lookup, chain follow, entry point), NO literal redef fallback
  - [ ] LocalTerm resolution does NOT go through resolve_input() — uses factory-specific 3-strategy cascade
  - [ ] `_find_literal_redefinition()`: type-aware (Strategy 1) before name-based (Strategy 2)
  - [ ] Default backfill replaces None with literal values
  - [ ] Always single-output with field_name="root"
  - [ ] FULLY_COMPILABLE when all terms wire; MANUAL_REQUIRED when literal not found

### C17 — Entry Point Classification
- **Doc**: [06-entry-point-classifier.md](06-entry-point-classifier.md)
- **REQs**: REQ-EPC-01 through REQ-EPC-08
- **Current location**: `generation/initialization.py`
- **Interfaces**:
  - Input: BacktrackingResult entry points, DesignAttributeData, CalcUsageData
  - Output: `dict[str, EntryPoint]` with classified types
- **AC**:
  - [ ] Exactly one EntryPointType per entry point
  - [ ] Strict precedence: DESIGN_ATTRIBUTE > LIBRARY_DEFAULT > USAGE_LITERAL
  - [ ] `default_value` converted to float at classification time
  - [ ] Every entry point assigned a param_group
  - [ ] Orphans land in "system_design" fallback group
  - [ ] Groups rebuilt after FORMULA/Aggregation module construction
  - [ ] `_classify_entry_points()` is a pure function
  - [ ] Factory-created entry points retain entry_type=DESIGN_ATTRIBUTE (never re-classified)

### C18 — Graph Assembly
- **Doc**: [07-graph-assembly.md](07-graph-assembly.md)
- **REQs**: REQ-GA-01 through REQ-GA-07
- **Current location**: `resolution/graph_builder.py`
- **Interfaces**:
  - Input: `list[PipelineModule]`, `list[ParameterGroup]`
  - Output: `ComputationGraph`
- **AC**:
  - [ ] Valid topological sort: no module reads from a module later in execution_order
  - [ ] Cycle detection raises `CircularDependencyError`
  - [ ] Every `producer_channel` in every ModuleInput resolves to a declared ModuleOutput
  - [ ] No self-dependency in the graph
  - [ ] ComputationGraph has exactly 3 fields: modules, entry_point_groups, execution_order
  - [ ] execution_order list matches module ordering
  - [ ] O(V+E) Kahn's algorithm with deque

---

## Layer 5: Orchestration

### C19 — Pipeline Builder (Orchestrator)
- **Doc**: [02-orchestration.md](02-orchestration.md), [00-pipeline-overview.md](00-pipeline-overview.md)
- **REQs**: REQ-ORCH-01 through REQ-ORCH-07, REQ-PIPE-01 through REQ-PIPE-07
- **Current location**: `generation/initialization.py` (`build_pipeline_context`)
- **Target location**: `orchestration/` (new package)
- **Interfaces**:
  - Input: extraction results (calc_defs, calc_usages, part_defs, hierarchy)
  - Output: `ComputationGraph` (the single artifact for generation)
- **AC**:
  - [ ] Steps execute in strict dependency order (documented 7-step + substeps)
  - [ ] Virtual binding rewrite completes before downstream steps
  - [ ] FORMULA attributes removed from design_attrs before parameter group construction
  - [ ] OutputRegistry phases in strict order (1a/1b/1c then 2/3/4)
  - [ ] Each aggregation expression scoped to concrete instance paths
  - [ ] ComputationGraph is single source of truth for generation
  - [ ] CHAIN alias unresolvable = warning, not error
  - [ ] Every ModuleInput wired to exactly one source
  - [ ] Every module_output reference resolves to canonical channel in OutputRegistry
  - [ ] execution_order is a valid topological sort
  - [ ] Graph includes all 3 module types when model requires them
  - [ ] Generation uses ONLY ComputationGraph — no back-references

---

## Layer 6: Generation

### C20 — Pipeline YAML Generator
- **Doc**: [21-pipeline-yaml-generation.md](21-pipeline-yaml-generation.md)
- **REQs**: REQ-PY-01 through REQ-PY-07
- **Current location**: `generation/pipeline.py`
- **AC**:
  - [ ] All entry point sources include `param_group.` prefix
  - [ ] All numeric types are "float" (including multiplicity)
  - [ ] Single-output references append `.root`
  - [ ] channel_field_map covers every ModuleOutput
  - [ ] Exit point type matches upstream output type
  - [ ] One JSON file per ParameterGroup
  - [ ] Consumes ONLY ComputationGraph (gold standard)

### C21 — Module Wrapper Generator
- **Doc**: [08-generation.md](08-generation.md)
- **REQs**: REQ-GEN-02
- **Current location**: `generation/modules.py`
- **AC**:
  - [ ] One wrapper per PipelineModule
  - [ ] Import path matches filesystem path
  - [ ] Input/output types match module definition

### C22 — Schema Generator
- **Doc**: [22-output-schema-rules.md](22-output-schema-rules.md)
- **REQs**: REQ-OSR-01 through REQ-OSR-07
- **Current location**: `generation/schemas.py`
- **AC**:
  - [ ] Single-output uses `RootModel[float]` with field_name="root"
  - [ ] Multi-output generates named MultiOutput subclass
  - [ ] Field names match SysML output_attributes names
  - [ ] Type mapping: Real->float, Integer->int, Boolean->bool, String->str
  - [ ] Output fields MUST NOT have default values
  - [ ] Aggregation and FORMULA always single-output ("root")

### C23 — Stencil Generator + Smart Regen
- **Doc**: [08-generation.md](08-generation.md), [23-smart-regen-preservation.md](23-smart-regen-preservation.md)
- **REQs**: REQ-GEN-04, REQ-SR-01 through REQ-SR-07
- **Current location**: `generation/stencils.py`, `generation/preservation.py`
- **AC**:
  - [ ] FULLY_COMPILABLE gets auto-impl; others get stubs
  - [ ] Two-level signature matching (type-level required, field-level order-independent)
  - [ ] 4-case decision tree for should_regenerate_stencil
  - [ ] Stub-to-auto-impl upgrade requires 3 conditions
  - [ ] Backup before every regen/upgrade
  - [ ] Aggregation/FORMULA modules always regenerated
  - [ ] --preserve-handwritten skips without comparison

### C24 — Module Registry Generator
- **Doc**: [20-module-registry-generation.md](20-module-registry-generation.md)
- **REQs**: REQ-REG-01 through REQ-REG-07
- **Current location**: `generation/registry.py`
- **AC**:
  - [ ] Uses design-scoped EQN (module_eqn), not library QN
  - [ ] Import paths match actual filesystem paths
  - [ ] Globally unique class names via module_type_override
  - [ ] Aliased imports when names collide
  - [ ] Name collision detection and reporting before rendering

### C25 — JSON Template + Parameter Schema Generator
- **Doc**: [08-generation.md](08-generation.md), [21-pipeline-yaml-generation.md](21-pipeline-yaml-generation.md)
- **REQs**: REQ-GEN-05, REQ-PY-07
- **Current location**: `generation/entry_point.py`, `generation/schemas.py`
- **AC**:
  - [ ] Each ParameterGroup produces one JSON template + one Pydantic schema
  - [ ] JSON template values match entry point default_value
  - [ ] Schema field types match declared SysML types

---

### C26 — PipelineModule Migration
- **Doc**: [26-pipeline-module-migration.md](26-pipeline-module-migration.md)
- **REQs**: REQ-PMM-01 through REQ-PMM-05
- **Interfaces**:
  - 6 new fields on PipelineModule/ModuleInput/ModuleOutput
  - `_from_graph()` generator variants
- **AC**:
  - [ ] PipelineModule has all 6 additional fields populated
  - [ ] All generators have `_from_graph()` variants
  - [ ] Generated output identical before/after migration (REQ-PMM-04)

### C27 — Typed Registry Refactor (Design Intent)
- **Doc**: [27-typed-registry-refactor.md](27-typed-registry-refactor.md)
- **REQs**: FR-1 through FR-6, NFR-1 through NFR-3
- **Scope**: Design intent document defining the type system and registry architecture
- **AC**:
  - [ ] All 5 typed identifier types defined: SysMLQN, EQN, PQN, CanonicalChannel, ScopedKey
  - [ ] All 3 typed registries defined: Scoped, SysML QN, Alias
  - [ ] All 5 eliminated key formats documented with zero-hit evidence: Key_A, Key_D, Key_E full, Key_F, bare
  - [ ] Type-directed dispatch table present: CHAIN → scoped/alias, REFERENCE → SysML QN/scoped
  - [ ] Constructor invariants documented: ScopedKey rejects `::`, SysMLQN rejects `__`
  - [ ] Uniqueness guarantee: scoped/SysML QN unique by construction, alias retains first-wins
  - [ ] NFR notes: NewType for zero runtime cost, mypy --strict, incremental adoption
  - [ ] Evidence base: citations from spike research
  - [ ] Cross-references to all 7 amended docs (03, 04, 09, 10, 11, 15, 24)

---

## Cross-Cutting Concerns

### X01 — Type Mapping Consistency
- **Doc**: [08-generation.md](08-generation.md) (REQ-GEN-06 — currently violated)
- **AC**:
  - [ ] Single `_map_input_type()` / `_map_output_type()` function used everywhere
  - [ ] No divergent copies across generators

### X02 — Resolution Consistency (3 paths)
- **Doc**: [24-dual-resolution-architecture.md](24-dual-resolution-architecture.md)
- **REQs**: REQ-DRA-01 through REQ-DRA-05
- **Paths**: (1) Backtracker DFS cascade (CalcUsage), (2) Pre-computed attribute resolution map (FORMULA), (3) resolve_input() with AGG_STRATEGIES (Aggregation SumTerm/SingletonTerm) + factory cascade (LocalTerm)
- **AC**:
  - [ ] Same reference in same scope produces identical wiring from all applicable paths
  - [ ] Test: for every Agg input that COULD be a CalcUsage input, both paths agree
