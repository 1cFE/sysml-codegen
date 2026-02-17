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
  - [ ] NewType wrappers (SysMLQN, EQN, PQN, RegistryKey) defined and importable
  - [ ] Field types in extraction/analysis/core/resolution models use typed names per Doc 09 table

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
- **AC**:
  - [ ] One `CalculationDefinitionData` per calc def in model
  - [ ] Every binding has exactly one BindingType (CHAIN, REFERENCE, LITERAL, EXPRESSION, UNBOUND)
  - [ ] Every redefinition classified as exactly one RedefinitionType (LITERAL, CHAIN, EXPRESSION)
  - [ ] Every aggregation expression decomposed into typed terms (SumTerm, SingletonTerm, LocalTerm)
  - [ ] Template calc usages produce one virtual CalcUsageData per PartUsage instance
  - [ ] Extraction imports NOTHING from analysis/, resolution/, or generation/
  - [ ] `output_expression_asts` preserves raw SysIDE AST nodes (not None, not empty)
  - [ ] Verified with solar_battery_model (has all binding types) and catf_mfe_model (has hierarchy)

### C04 — Expression Compiler
- **Doc**: [14-expression-compiler.md](14-expression-compiler.md)
- **REQs**: REQ-EC-01 through REQ-EC-07
- **Current location**: `extraction/expression_compiler.py`, `extraction/expression_utils.py`
- **Interfaces**:
  - Input: `CalculationDefinitionData` with `output_expression_asts`
  - Output: compiled Python expressions, compilability verdicts per output
- **AC**:
  - [ ] FCE checked BEFORE OE at every dispatch site (doc 19 invariant)
  - [ ] N-ary operands left-folded into binary nodes
  - [ ] Unit annotations stripped from expressions
  - [ ] Every compiled expression validates via `ast.parse()`
  - [ ] Cycles mark all outputs MANUAL_REQUIRED
  - [ ] Worst-case roll-up for calc-level compilability
  - [ ] Undeclared intermediates discovered iteratively
  - [ ] Test with real calc defs from all fixture models

### C05 — Computed Attribute Extractor
- **Doc**: [16-computed-attributes.md](16-computed-attributes.md)
- **REQs**: REQ-CA-01 through REQ-CA-07
- **Current location**: `extraction/computed_attribute_extractor.py`
- **Interfaces**:
  - Input: PartDefinitionData attribute expressions
  - Output: ComputedAttributeClassification per attribute, ComputedAttributeData
- **AC**:
  - [ ] Every attribute expression classified as exactly one of: FORMULA, EXPOSE_PURE, EXPOSE_COMPUTED, LITERAL, UNRESOLVABLE
  - [ ] FORMULA attributes compile to valid Python
  - [ ] EXPOSE_PURE only for PartUsage-level single-FCE
  - [ ] LITERAL attributes excluded (no module, no alias)
  - [ ] UNRESOLVABLE logged but no module/alias created
  - [ ] Self-reference excluded from input_names
  - [ ] Test with attr_expr_probe fixture

### C06 — Hierarchy Resolver
- **Doc**: [01-extraction.md](01-extraction.md), [13-aggregation-scoping.md](13-aggregation-scoping.md)
- **Current location**: `extraction/hierarchy_resolver.py`
- **AC**:
  - [ ] Template detection (is_template) correct for all fixture models
  - [ ] Part usage hierarchy extracted with correct parent/child relationships
  - [ ] Multiplicity data extracted from PartUsage nodes
  - [ ] Aggregation term type classification correct (SumTerm, SingletonTerm, LocalTerm)
  - [ ] FCE classified as SingletonTerm (not LocalTerm) — AST dispatch invariant

### C07 — AST Dispatch Invariant
- **Doc**: [19-ast-dispatch-invariant.md](19-ast-dispatch-invariant.md)
- **REQs**: REQ-AST-01 through REQ-AST-07
- **Cross-cutting**: affects C04, C05, C06
- **AC**:
  - [ ] Audit: every dual-check site checks FCE before OE
  - [ ] Comment present at every dual-check site
  - [ ] All 8+ dispatch sites follow canonical ordering: FCE, OE, FRE, Literal
  - [ ] Regression test: if FCE/OE order reversed, test fails

---

## Layer 2: Core Infrastructure

### C08 — Output Registry
- **Doc**: [10-output-registry.md](10-output-registry.md)
- **REQs**: REQ-OR-01 through REQ-OR-07
- **Current location**: `core/output_registry.py`
- **Interfaces**:
  - `register(key, canonical_channel)`
  - `register_alias(alias_key, target)` — with phase enforcement
  - `resolve(key) -> canonical_channel | None`
  - `derive_key_c(eqn) -> str`
- **AC**:
  - [ ] Maps every key format (A through F) to canonical PQN
  - [ ] `resolve()` is exact-match only — no normalization, no fuzzy matching
  - [ ] Collision policy: first registration wins, logs warning, does not overwrite
  - [ ] `register_alias()` enforces phase ordering (reject alias to unknown canonical)
  - [ ] Phase 1 registers all key variants for each channel
  - [ ] Phase 2-4 aliases resolve through registry before registering
  - [ ] Key_C strips design prefix, joins with dots
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

### C11 — DependencyBacktracker
- **Doc**: [11-analysis-backtracker.md](11-analysis-backtracker.md), [24-dual-resolution-architecture.md](24-dual-resolution-architecture.md)
- **REQs**: REQ-BT-01 through REQ-BT-07, REQ-DRA-01
- **Current location**: `analysis/dependency_backtracker.py`
- **Interfaces**:
  - Input: root calc usages, OutputRegistry, CalcUsageData, CalculationDefinitionData
  - Output: `BacktrackingResult` (required_usages, dependency_graph, entry_points, binding_resolutions)
- **AC**:
  - [ ] Every non-literal binding resolved via `_resolve_binding_via_registry()`
  - [ ] Scoped resolution (Step 0/Key_C) runs before unscoped (Step 1/Key_A)
  - [ ] Cycle detection via path tracking — cycles don't crash, they warn
  - [ ] Every binding resolves (Step 4 fallback guarantees total resolution)
  - [ ] Key format: `"{usage_qn}|{param_name}"` for binding_resolutions
  - [ ] Topological sort produces dependency-first ordering
  - [ ] Self-reference guard prevents wiring module to its own output
  - [ ] Test with real OutputRegistry + real extraction from all fixture models

### C12 — Input Resolver (resolve_input)
- **Doc**: [04-input-resolver.md](04-input-resolver.md), [24-dual-resolution-architecture.md](24-dual-resolution-architecture.md)
- **REQs**: REQ-IR-01 through REQ-IR-07, REQ-DRA-02
- **Target location**: `resolution/input_resolver.py` (new, extracted from graph_builder)
- **Scope**: Aggregation SumTerm/SingletonTerm inputs only. FORMULA uses pre-computed attribute resolution map (not resolve_input). LocalTerm uses factory-specific cascade.
- **Interfaces**:
  - `resolve_input(ref, ctx, strategies) -> InputSource`
  - `ResolutionContext`: frozen dataclass with output_registry, redefinitions, design_attrs, module_eqn, consumer_scope, instance_path
  - 5 strategies for aggregation SumTerm/SingletonTerm: A (DirectRegistryLookup), B (SysmlQnNormalization), C (ScopedRegistryLookup), D (ChainRedefinitionFollow), E (DesignAttributeLookup)
- **AC**:
  - [ ] Always returns InputSource, NEVER raises
  - [ ] Strategies execute in declared order; first match wins
  - [ ] Self-reference guard rejects wiring to own channels
  - [ ] ResolutionContext is immutable (frozen=True)
  - [ ] AGG_STRATEGIES has ChainRedefinitionFollow at position 2 (before A/B)
  - [ ] Fallback produces entry_point (never unresolved)
  - [ ] STANDARD_STRATEGIES has 5 strategies with C first
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
