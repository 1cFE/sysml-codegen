# Verification Matrix

Traceability matrix mapping every REQ-\* tag to its conformance test file and status.

## Summary

| Metric | Count |
|--------|-------|
| Total requirements | 252 |
| PASS (test exists and passes) | 240 |
| UNTESTED (no dedicated test) | 12 |
| DEFERRED | 0 |
| REQ families | 30 |
| Distinct test files cited | 56 |

**Status definitions:**
- **PASS**: At least one conformance test references this requirement and passes
- **UNTESTED**: No conformance test directly references this requirement
- **DEFERRED**: Behavior implemented; real-fixture test deferred to a later item (none open — REQ-CA-09 discharged by Item 10)

UNTESTED requirements are either cross-cutting architectural principles verified
indirectly through component-level tests, or design-only requirements that constrain
the documentation rather than executable code.

## Index

- [AS — Aggregation Scoping](#as) (8/8 pass)
- [AST — AST Dispatch Invariant](#ast) (9/9 pass)
- [BASE — Baseline Conformance](#base) (6/6 pass)
- [BT — Backtracker](#bt) (11/11 pass)
- [CA — Computed Attributes](#ca) (10/11 pass, 1 untested)
- [DM — Data Models](#dm) (8/9 pass)
- [DRA — Dual Resolution Architecture](#dra) (5/5 pass)
- [EC — Expression Compiler](#ec) (7/7 pass)
- [EPC — Entry Point Classification](#epc) (8/8 pass)
- [EXT — Extraction](#ext) (14/14 pass)
- [GA — Graph Assembly](#ga) (8/8 pass)
- [GEN — Generation](#gen) (5/7 pass)
- [HR — Hierarchy Resolver](#hr) (8/8 pass)
- [IR — Input Resolver](#ir) (7/7 pass)
- [LVP — Literal Value Propagation](#lvp) (9/9 pass)
- [MF — Module Factory](#mf) (8/8 pass)
- [NC — Naming Conventions](#nc) (9/9 pass)
- [OR — Output Registry](#or) (9/9 pass)
- [ORCH — Orchestration](#orch) (7/7 pass)
- [OSR — Output Schema Rules](#osr) (7/7 pass)
- [PGD — Parameter Group Deriver](#pgd) (8/8 pass)
- [PIPE — Pipeline](#pipe) (7/7 pass)
- [PMM — PipelineModule Migration](#pmm) (5/5 pass)
- [PY — Pipeline YAML](#py) (8/8 pass)
- [REG — Module Registry](#reg) (8/8 pass)
- [RES — Resolution Overview](#res) (0/8 pass)
- [SNAP — Snapshots: Extraction Format & Snapshot-Driven Generation](#snap) (19/19 pass)
- [SR — Smart Regen / Preservation](#sr) (7/7 pass)
- [SVM — Supplied-Value Materializer](#svm) (4/4 pass)
- [VBR — Virtual Binding Rewrite](#vbr) (11/11 pass)

---

## Requirements by Family

### AS

**Aggregation Scoping** — Component C10 — [reference/13-aggregation-scoping.md](reference/13-aggregation-scoping.md)

| REQ ID | Requirement | Test File | Status |
|--------|-------------|-----------|--------|
| REQ-AS-01 | Each PartDef-level aggregation SHALL produce one `ScopedAggregationData` per design insta... | `test_aggregation_scoping.py` | PASS |
| REQ-AS-02 | Instance discovery SHALL try direct match (Strategy 1) BEFORE child-walk fallback (Strate... | `test_aggregation_scoping.py` | PASS |
| REQ-AS-03 | Instance paths SHALL be converted from `__`-separated to dotted format with design prefix... | `test_aggregation_scoping.py` | PASS |
| REQ-AS-04 | CHAIN aliases SHALL only be produced for non-deep-path redefinitions whose `source_path` ... | `test_aggregation_scoping.py` | PASS |
| REQ-AS-05 | Phase 1b SHALL register a canonical channel for each `ScopedAggregationData` | `test_aggregation_scoping.py` | PASS |
| REQ-AS-06 | Phase 2 SHALL resolve `ChannelAlias.canonical_name` in registry before registering alias | `test_aggregation_scoping.py` | PASS |
| REQ-AS-07 | `module_eqn` property SHALL be `"{instance_path}__{attribute_name}"` | `test_aggregation_scoping.py` | PASS |
| REQ-AS-08 | The scoping function SHALL log a WARNING (not just info) when an | `test_aggregation_scoping.py` | PASS |

### AST

**AST Dispatch Invariant** — Component C07 — [reference/19-ast-dispatch-invariant.md](reference/19-ast-dispatch-invariant.md)

| REQ ID | Requirement | Test File | Status |
|--------|-------------|-----------|--------|
| REQ-AST-01 | Every `is_instance()` dispatch that checks both FCE and OE SHALL check FCE first | `test_ast_dispatch_invariant.py`, `test_expression_compiler.py` | PASS |
| REQ-AST-02 | Every dispatch site checking both FCE and OE SHALL include a comment: "MUST be before Ope... | `test_ast_dispatch_invariant.py` | PASS |
| REQ-AST-03 | Among reference/operator branches ordering SHALL be FCE, OE, FRE; literal/null branches SHALL dispatch before the invocation catch-all | `test_ast_dispatch_invariant.py` | PASS |
| REQ-AST-04 | New dispatch sites SHALL follow REQ-AST-03 ordering | `test_ast_dispatch_invariant.py` | PASS |
| REQ-AST-05 | `hierarchy_resolver._walk_aggregation_ast()` SHALL classify FCE nodes as `SingletonTerm` ... | `test_ast_dispatch_invariant.py` | PASS |
| REQ-AST-06 | `expression_compiler.build_expression_ast()` SHALL return `unsupported` for FCE (not "uns... | `test_ast_dispatch_invariant.py` | PASS |
| REQ-AST-07 | `expression_utils.reconstruct_expression()` SHALL return `"name.attr"` for FCE (not `".(n... | `test_ast_dispatch_invariant.py` | PASS |
| REQ-AST-08 | `reconstruct_expression` SHALL dispatch all literal/`NullExpression` branches (via `is_instance`) before the invocation catch-all | `test_expression_reconstruction_fidelity.py`, offline totality guard | PASS |
| REQ-AST-09 | `reconstruct_operator_expression` SHALL parenthesize a child operand iff it binds looser than its parent, or equal and on the associativity-unfavored side | `test_expression_reconstruction_fidelity.py`, `test_expression_paren_helper.py` | PASS |
| REQ-AST-10 | `hierarchy_resolver._walk_aggregation_ast()` SHALL dispatch all literal/null branches before the invocation catch-all | `test_agg_literal_dispatch.py` (`agg_literal_probe` fixture) | PASS |

### BASE

**Baseline Conformance** — Baseline Tests

| REQ ID | Requirement | Test File | Status |
|--------|-------------|-----------|--------|
| REQ-BASE-01 | ComputationGraph JSON matches captured baseline | `test_baselines.py` | PASS |
| REQ-BASE-02 | Baseline JSON deserializes back to valid ComputationGraph | `test_baselines.py` | PASS |
| REQ-BASE-03 | Registry __init__.py baseline is syntactically valid Python | `test_baselines.py` | PASS |
| REQ-BASE-04 | execution_order length equals modules length in every baseline | `test_baselines.py` | PASS |
| REQ-BASE-05 | solar_battery (YAML + graph + registry) and catf_mfe (graph + registry) re-captured via scripts, ordering-only, reviewed | `test_gen_pipeline_yaml.py`, `test_pipeline_e2e.py`, `test_e2e_output_registry.py` | PASS |
| REQ-BASE-06 | `entry_point_groups` SHALL be name-sorted in every ComputationGraph, so a model-discovery-order shift cannot redden a byte-exact baseline | `test_graph_assembly.py` | PASS |

### BT

**Backtracker** — Component C11 — [reference/11-analysis-backtracker.md](reference/11-analysis-backtracker.md)

| REQ ID | Requirement | Test File | Status |
|--------|-------------|-----------|--------|
| REQ-BT-01 | Every non-literal binding SHALL be resolved via `_resolve_binding_via_registry()` through... | `test_backtracker.py` | PASS |
| REQ-BT-02 | Resolution SHALL dispatch on binding format: CHAIN bindings (no `::` in source_path) quer... | `test_backtracker.py` | PASS |
| REQ-BT-03 | DFS SHALL detect cycles via path tracking and raise `CircularDependencyError` | `test_backtracker.py` | PASS |
| REQ-BT-04 | Every binding SHALL resolve to exactly one `BindingResolution` — no binding left dangling | `test_backtracker.py` | PASS |
| REQ-BT-05 | `binding_resolutions` key format SHALL be `"{usage_qn}\ | `test_backtracker.py` | PASS |
| REQ-BT-06 | Topological sort SHALL produce dependency-first ordering or raise on cycles | `test_backtracker.py` | PASS |
| REQ-BT-07 | Self-reference guard SHALL prevent a usage from wiring to its own output | `test_backtracker.py` | PASS |
| REQ-BT-08 | Resolution SHALL use type-directed dispatch on `BindingType` format to select the correct... | `test_backtracker.py` | PASS |
| REQ-BT-09 | The FORMULA `::`-QN REFERENCE path SHALL per-segment sanitize (`sanitize_qualified_name`) before comparison/lookup so a quoted-owner QN matches the sanitized design-attribute QN (Bug A; six-site lockstep flip, INV-1) | `test_matcher_fixes_item7.py`, `test_dual_resolution.py` | PASS |
| REQ-BT-10 | A design attribute owned by a part **def** (empty `parent_part`) SHALL match its binding via a leaf-unique fallback over design-part attributes (calc-def I/O excluded), returning a QN only when exactly one candidate exists, else None (Bug B; INV-2, no cross-wire) | `test_matcher_fixes_item7.py` | PASS |
| REQ-BT-11 | `_resolve_chain_dispatch` SHALL query the structured `_scoped_alias` namespace (Step 1c) by splitting `source_path` at the last dot, trying the consumer-scope-prefixed key `(consumer_scope.prefix, leaf)` before the bare `(prefix, leaf)` (Item 10 #1 / D-D sibling disambiguation), ordered after Step 1b and before the unscoped Step 2 (INV-A: additive, only where the ladder fell through) | `test_sibling_channel_ambiguity.py`, `test_wi014_toy.py` | PASS |

### CA

**Computed Attributes** — Component C05 — [reference/16-computed-attributes.md](reference/16-computed-attributes.md)

| REQ ID | Requirement | Test File | Status |
|--------|-------------|-----------|--------|
| REQ-CA-01 | Classification SHALL produce exactly one of the 5 stable values per attribute expression (the transient sixth, `EXPOSE_CHAIN_TENTATIVE`, never survives the Phase-3b confirm pass to a reader — INV-F) | `test_computed_attributes.py` | PASS |
| REQ-CA-02 | FORMULA attributes SHALL compile to Python via `build_expression_ast()` + `compile_expres... | `test_computed_attributes.py` | PASS |
| REQ-CA-03 | EXPOSE_PURE SHALL produce a `ChannelAlias` for a PartUsage-level derived attribute; a PartDef-level EXPOSE (shape A) SHALL be expanded per design instance path into the structured `_scoped_alias` namespace (`_register_partdef_expose_scoped_aliases`, Item 10 #4) rather than emitting a template alias | `test_computed_attributes.py`, `test_wi014_toy.py` | PASS |
| REQ-CA-10 | A pure `FeatureChainExpression` whose `reference_chain` is a part-rooted ≥2-segment single-terminal chain (INV-E) SHALL be tagged `EXPOSE_CHAIN_TENTATIVE`, then the Phase-3b confirm walk over `reference_chain` SHALL finalize it to EXPOSE_PURE (+register the transitive channel) or revert to FORMULA; no tentative SHALL survive to any reader (INV-F raises) | `test_computed_attribute_extraction.py`, `test_ife_plant.py` | PASS |
| REQ-CA-04 | LITERAL attributes SHALL be excluded from computed attributes | `test_computed_attributes.py` | PASS |
| REQ-CA-05 | UNRESOLVABLE attributes SHALL be logged but not generate modules or aliases | `test_computed_attributes.py` | PASS |
| REQ-CA-06 | `AttributeResolutionKind` SHALL classify each FORMULA input as FORMULA, EXPOSE_ALIAS, or ... | `test_computed_attributes.py` | PASS |
| REQ-CA-07 | FORMULA self-reference SHALL be excluded from `input_names` | `test_computed_attributes.py` | PASS |
| REQ-CA-08 | FORMULA compilation SHALL NOT resolve sibling FORMULA outputs | — | UNTESTED |
| REQ-CA-09 | Shape-A resolution (part-def EXPOSE): the wi014_toy `demo_plant.total_cost` consumer SHALL resolve via `_scoped_alias` to the `cost_calc__cost` channel (the Item-1 malformed-refs deferral, discharged by Item 10 #4/#1) | `test_wi014_toy.py` | PASS |
| REQ-CA-11 | Shape-A EXPOSE_PURE (part def) in the attribute resolution map SHALL route by `is_on_part_definition` to a LITERAL fallback (not the refs-parser) and consult `_scoped_alias` to decide the warning: a registered leaf is silent (the name resolves via Item 10 and surfaces via Item 11), an unregistered one warns naming the real cause — retiring the Item-1 malformed-refs warning (`_resolve_expose_pure` in `graph_builder.py`) for the resolvable case | `test_wi014_toy.py` | PASS |

### DM

**Data Models** — Component C01 — [reference/09-data-models.md](reference/09-data-models.md)

| REQ ID | Requirement | Test File | Status |
|--------|-------------|-----------|--------|
| REQ-DM-01 | Every model referenced by another doc in this set SHALL appear here or have an explicit d... | `test_data_models.py` | PASS |
| REQ-DM-02 | Every enum SHALL list ALL values with no omissions | `test_data_models.py` | PASS |
| REQ-DM-03 | Field lists SHALL match source code (name, type, optionality) | `test_data_models.py` | PASS |
| REQ-DM-04 | Every model SHALL state its parent class and source file location | `test_data_models.py` | PASS |
| REQ-DM-05 | At least one populated `ComputationGraph` example SHALL demonstrate both `entry_point` an... | `test_data_models.py` | PASS |
| REQ-DM-06 | Models with dedicated docs SHALL link to those docs, not duplicate detail | `test_data_models.py` | PASS |
| REQ-DM-07 | The data flow diagram SHALL show all pipeline stages and their primary I/O models | `test_data_models.py` | PASS |
| REQ-DM-08 | Name fields with semantic format constraints SHALL use NewType wrappers, not bare `str` | — | UNTESTED |
| REQ-DM-09 | `ComputationGraph.output_aliases: list[OutputAlias]` SHALL be a serialized field (no `exclude`, contrast `fallback_entry_points`) carrying each EXPOSE_PURE modeler name, its canonical channel (validated to exist — INV-3), instance path, and `shape`; stable-sorted by `(instance_path, alias_name)` (INV-5) so regen yields no ordering-only diff | `test_data_models.py`, `test_graph_assembly.py` | PASS |

### DRA

**Dual Resolution Architecture** — Component X02 — [reference/24-dual-resolution-architecture.md](reference/24-dual-resolution-architecture.md)

**Status (F4, Item 7):** the `resolve_input()` path these rows compare against is the not-yet-wired consolidation (see the [IR family note](#ir)); the parity checks compare it against the **backtracker DFS**, which is the live comparand, not against `_resolve_aggregation_input_channel` (the function the cutover replaces — [ITEM7-F4-CUTOVER]'s own gate). The live aggregation path is `_resolve_aggregation_input_channel`.

| REQ ID | Requirement | Test File | Status |
|--------|-------------|-----------|--------|
| REQ-DRA-01 | CalcUsage resolution SHALL happen during backtracker DFS; the DFS decision (recurse vs st... | `test_backtracker.py` | PASS |
| REQ-DRA-02 | FORMULA SHALL use pre-computed attribute resolution map; aggregation SumTerm/SingletonTerm resolution is validated by `resolve_input()` (the not-yet-wired consolidation) against the backtracker — the live path is `_resolve_aggregation_input_channel` | `test_input_resolver.py`, `test_dual_resolution.py` | PASS |
| REQ-DRA-03 | Both paths SHALL use typed registries (10-output-registry): `scoped_lookup(ScopedKey)` fo... | `test_backtracker.py`, `test_dual_resolution.py` | PASS |
| REQ-DRA-04 | Both paths SHALL produce the same wiring for the same reference. A binding `"cost_model.t... | `test_dual_resolution.py`, `test_input_resolver.py` | PASS |
| REQ-DRA-05 | The backtracker SHALL produce `BindingResolution` objects; `resolve_input()` SHALL produc... | `test_dual_resolution.py` | PASS |

### EC

**Expression Compiler** — Component C04 — [reference/14-expression-compiler.md](reference/14-expression-compiler.md)

| REQ ID | Requirement | Test File | Status |
|--------|-------------|-----------|--------|
| REQ-EC-01 | `FeatureChainExpression` SHALL be checked BEFORE `OperatorExpression` (FCE is OE subtype ... | `test_expression_compiler.py` | PASS |
| REQ-EC-02 | N-ary operands SHALL be left-folded into binary `BINARY_OP` nodes | `test_expression_compiler.py` | PASS |
| REQ-EC-03 | Unit annotations (`[` operator) SHALL be stripped; only the value operand is retained | `test_expression_compiler.py` | PASS |
| REQ-EC-04 | Every compiled expression SHALL be validated via `python_ast.parse(result, mode="eval")` | `test_expression_compiler.py` | PASS |
| REQ-EC-05 | Cycle detection in dependency graph SHALL mark ALL outputs as `MANUAL_REQUIRED` | `test_expression_compiler.py` | PASS |
| REQ-EC-06 | `classify_compilability()` SHALL use worst-case roll-up semantics | `test_expression_compiler.py` | PASS |
| REQ-EC-07 | Undeclared intermediates SHALL be discovered iteratively from `member_expressions` | `test_expression_compiler.py` | PASS |

### EPC

**Entry Point Classification** — Component C17 — [reference/06-entry-point-classifier.md](reference/06-entry-point-classifier.md)

| REQ ID | Requirement | Test File | Status |
|--------|-------------|-----------|--------|
| REQ-EPC-01 | Every entry point SHALL be classified as exactly one EntryPointType: {`DESIGN_ATTRIBUTE`,... | `test_entry_point_classifier.py` | PASS |
| REQ-EPC-02 | Classification SHALL follow strict precedence: `DESIGN_ATTRIBUTE` > `LIBRARY_DEFAULT` > `... | `test_entry_point_classifier.py` | PASS |
| REQ-EPC-03 | `default_value` SHALL be converted to `float` at classification time; if conversion fails... | `test_entry_point_classifier.py` | PASS |
| REQ-EPC-04 | Every classified entry point SHALL be assigned a `param_group` via ParameterGroupDeriver.... | `test_entry_point_classifier.py` | PASS |
| REQ-EPC-05 | Every entry point SHALL belong to exactly one ParameterGroup. Orphans SHALL land in a `"s... | `test_entry_point_classifier.py` | PASS |
| REQ-EPC-06 | After FORMULA and aggregation module construction, parameter groups SHALL be rebuilt from... | `test_entry_point_classifier.py` | PASS |
| REQ-EPC-07 | `_classify_entry_points()` SHALL be a pure function: input data in, `dict[str, EntryPoint... | `test_entry_point_classifier.py` | PASS |
| REQ-EPC-08 | Entry points created by FORMULA and aggregation factories SHALL have `entry_type=DESIGN_A... | `test_entry_point_classifier.py` | PASS |

### EXT

**Extraction** — Component C03 — [reference/01-extraction.md](reference/01-extraction.md)

| REQ ID | Requirement | Test File | Status |
|--------|-------------|-----------|--------|
| REQ-EXT-01 | Extraction SHALL produce exactly one CalculationDefinitionData per `calc def` in the SysM... | `test_extractor.py` | PASS |
| REQ-EXT-02 | Every parameter binding on a CalcUsageData SHALL have exactly one BindingType from {CHAIN... | `test_extractor.py` | PASS |
| REQ-EXT-03 | Every `:>>` redefinition SHALL be classified as exactly one RedefinitionType from {LITERA... | `test_extractor.py` | PASS |
| REQ-EXT-04 | Every aggregation expression SHALL be decomposed into typed terms: SumTerm, SingletonTerm... | `test_extractor.py` | PASS |
| REQ-EXT-05 | Template calc usages (`is_template=True`) SHALL produce one virtual CalcUsageData per Par... | `test_extractor.py` | PASS |
| REQ-EXT-06 | Extraction SHALL NOT import from `analysis/`, `resolution/`, or `generation/`. | `test_extractor.py` | PASS |
| REQ-EXT-07 | `output_expression_asts` SHALL preserve raw SysIDE AST nodes for downstream expression co... | `test_extractor.py` | PASS |
| REQ-EXT-08 | A `calc def` extracting with zero output attributes SHALL raise `ValueError` at extraction (V7), never reaching generation | `test_extractor.py` | PASS |
| REQ-EXT-09 | Every `ConstraintUsage` (calc-def, part-def, part-usage owners) SHALL be reported dropped: one INFO each + one summary WARN with the model-wide total | `test_extractor.py` | PASS |
| REQ-EXT-10 | A direction-carrying `ReferenceUsage` member (named `return`, bare `in`) SHALL extract as a parameter; a named inline `return y : Real = expr` SHALL auto-implement | `test_return_style_extraction.py` | PASS |
| REQ-EXT-11 | A calc def with an anonymous `return` (empty `declared_name`) SHALL raise the V8 diagnostic before V7 | `test_return_style_extraction.py` | PASS |
| REQ-EXT-12 | The `return attribute y; y = expr` form SHALL extract `y` once with no double-ingestion (direction-None body ref excluded) | `test_return_style_extraction.py` | PASS |
| REQ-EXT-13 | `_build_part_usage_index` SHALL index each PartUsage under all its owned FeatureTyping targets and every user-model PartDef in `usage.types` (user-filtered), never by list position | `test_type_indexing.py` | PASS |
| REQ-EXT-14 | Same-named templates from a retyped usage's super/subtype (same virtual QN) SHALL keep the most-specific owner + emit V9; differently-named templates SHALL both instantiate | `test_type_indexing.py` | PASS |

### GA

**Graph Assembly** — Component C18 — [reference/07-graph-assembly.md](reference/07-graph-assembly.md)

| REQ ID | Requirement | Test File | Status |
|--------|-------------|-----------|--------|
| REQ-GA-01 | `execution_order` SHALL be a valid topological sort: no module reads from a module that e... | `test_graph_assembly.py` | PASS |
| REQ-GA-02 | If a cycle exists, `_unified_topological_sort` SHALL raise `CircularDependencyError` list... | `test_graph_assembly.py` | PASS |
| REQ-GA-03 | Every `module_output` `producer_channel` SHALL resolve to a declared output channel. | `test_graph_assembly.py` | PASS |
| REQ-GA-04 | A module SHALL NOT depend on itself, even if its own output channel name appears in its i... | `test_graph_assembly.py` | PASS |
| REQ-GA-05 | The returned `ComputationGraph` SHALL contain exactly the reviewed field set: sorted `modules`, `entry_point_groups`, `execution_order`, in-memory `fallback_entry_points` (REQ-GA-08), serialized `output_aliases` (REQ-DM-09); any field-set change is a deliberate reviewed rev (the exact-set test flips red) | `test_graph_assembly.py` | PASS |
| REQ-GA-06 | `execution_order` list SHALL equal `[m.name for m in modules]` (names match module orderi... | `test_graph_assembly.py` | PASS |
| REQ-GA-07 | The topological sort SHALL run in O(V + E) time using Kahn's algorithm with `deque`. | `test_graph_assembly.py` | PASS |
| REQ-GA-08 | A two-layer params-coverage check SHALL exist: a pure collector `collect_uncovered_params(graph)` returning the wired fell-through-valueless violations (sibling to REQ-GA-03), and an always-strict generation boundary raising V11 on any violation. `ComputationGraph.fallback_entry_points` (in-memory, `exclude=True`) feeds it | `test_uncovered_params.py`, `test_graph_assembly.py`, `test_data_models.py` | PASS |

### GEN

**Generation** — Component C21 — [reference/08-generation.md](reference/08-generation.md)

| REQ ID | Requirement | Test File | Status |
|--------|-------------|-----------|--------|
| REQ-GEN-01 | Pipeline YAML generation SHALL consume only `ComputationGraph` -- no extraction models. | `test_generation_boundary.py` | PASS |
| REQ-GEN-02 | Every PipelineModule SHALL produce exactly one module wrapper file in `modules/`. | `test_gen_module_wrappers.py` | PASS |
| REQ-GEN-03 | Multi-output modules (2+ outputs) SHALL get a `MultiOutput` schema in `schemas/`; single-... | — | UNTESTED |
| REQ-GEN-04 | FULLY_COMPILABLE calc defs SHALL produce auto-implemented stencils; all others SHALL prod... | `test_gen_stencils.py`, `test_generation_boundary.py` | PASS |
| REQ-GEN-05 | Each ParameterGroup SHALL produce one JSON template (`inputs/`) and one Pydantic schema (... | `test_gen_json_templates.py` | PASS |
| REQ-GEN-06 | SysML type mapping (`Real`->`float`, `Integer`->`int`, `Boolean`->`bool`, `String`->`str`... | `test_type_mapping_consolidation.py` | PASS |
| REQ-GEN-07 | Every generated module SHALL be registered in `__init__.py` for TEAx framework discovery. | — | UNTESTED |

### HR

**Hierarchy Resolver** — Component C06 — [reference/25-hierarchy-resolver.md](reference/25-hierarchy-resolver.md)

| REQ ID | Requirement | Test File | Status |
|--------|-------------|-----------|--------|
| REQ-HR-01 | Every `:>>` redefinition SHALL be classified as exactly one RedefinitionType from {LITERA... | `test_hierarchy_resolver.py` | PASS |
| REQ-HR-02 | Both `FeatureChainExpression` and `FeatureReferenceExpression` value expressions SHALL pr... | `test_hierarchy_resolver.py` | PASS |
| REQ-HR-03 | Deep-path redefinitions SHALL set `is_deep_path=True` and populate `target_path` from `ch... | `test_hierarchy_resolver.py` | PASS |
| REQ-HR-04 | Multiplicity extraction SHALL use `cached_lower_bound` (not `cached_upper_bound`) due to ... | `test_hierarchy_resolver.py` | PASS |
| REQ-HR-05 | `_walk_aggregation_ast()` SHALL check `FeatureChainExpression` BEFORE `OperatorExpression... | `test_hierarchy_resolver.py` | PASS |
| REQ-HR-06 | `sum(child.attr)` SHALL be transformed to `(count_attr * child.attr)` using the `mult_loo... | `test_hierarchy_resolver.py` | PASS |
| REQ-HR-07 | CHAIN-type sibling redefinitions that reference the aggregation attribute SHALL be added ... | `test_hierarchy_resolver.py` | PASS |
| REQ-HR-08 | `extract_design_overrides()` SHALL scan `:>>` overrides on plain part usages (not only `part redefines`), keeping a newly-scanned plain-usage override only when its RHS is LITERAL; `part redefines` keeps all RHS types | `test_virtual_binding_rewrite.py`, `test_uncovered_params.py` | PASS |

### IR

**Input Resolver** — Component C12 — [reference/04-input-resolver.md](reference/04-input-resolver.md)

**Status (F4, Item 7):** `resolve_input()` / `AGG_STRATEGIES` (`input_resolver.py`) is a **backtracker-parity-validated consolidation that is not yet wired to the live path** — it has zero production callers; the live aggregation path is `_resolve_aggregation_input_channel` (`graph_builder.py`). These rows pin the module's **capability**, not live usage: the skipif-gated `test_input_resolver.py` unit tests exercise the module directly, and `test_dual_resolution.py::TestResolveInputParityExtended` proves parity with the backtracker DFS over Item 1's fixtures (1 MODULE_OUTPUT + 5 entry-point checks) alongside the committed catf_mfe/solar_battery suite. Wiring is filed as `[ITEM7-F4-CUTOVER]`.

| REQ ID | Requirement | Test File | Status |
|--------|-------------|-----------|--------|
| REQ-IR-01 | `resolve_input()` SHALL always return an InputSource -- never raise on unresolved refs. | `test_input_resolver.py` | PASS |
| REQ-IR-02 | Strategies SHALL execute in declared list order; first non-None result wins. | `test_input_resolver.py` | PASS |
| REQ-IR-03 | Self-reference guard SHALL reject channels where the producing module EQN matches `ctx.mo... | `test_input_resolver.py` | PASS |
| REQ-IR-04 | ResolutionContext SHALL be immutable (`frozen=True`); no strategy mutates it. | `test_input_resolver.py` | PASS |
| REQ-IR-05 | `AGG_STRATEGIES` SHALL order `ChainRedefinitionFollow` at position 2 (after `ScopedRegistryLookup`, before `SysMLQNLookup`) — the strategy list an aggregation caller receives once wired (capability, not live usage — see family note) | `test_input_resolver.py` | PASS |
| REQ-IR-06 | Fallback SHALL produce an `entry_point` InputSource with qualified name `"{module_eqn}__{... | `test_input_resolver.py` | PASS |
| REQ-IR-07 | `resolve_input()` with `AGG_STRATEGIES` SHALL resolve a SumTerm/SingletonTerm ref to the same channel the backtracker DFS resolves it to (parity-validated; not yet the live aggregation path — see family note) | `test_input_resolver.py`, `test_dual_resolution.py` | PASS |

### LVP

**Literal Value Propagation** — Component C16 — [reference/18-literal-value-propagation.md](reference/18-literal-value-propagation.md)

| REQ ID | Requirement | Test File | Status |
|--------|-------------|-----------|--------|
| REQ-LVP-01 | `_find_literal_redefinition()` SHALL try type-aware resolution (Strategy 1) before name-b... | `test_factory_aggregation.py` | PASS |
| REQ-LVP-02 | SumTerm fallback SHALL call `_find_literal_redefinition()` when channel resolution fails | `test_factory_aggregation.py` | PASS |
| REQ-LVP-03 | SingletonTerm fallback SHALL call `_find_literal_redefinition()` when channel resolution ... | `test_factory_aggregation.py` | PASS |
| REQ-LVP-04 | LocalTerms SHALL NOT use literal redefinition lookup (different resolution path) | `test_factory_aggregation.py` | PASS |
| REQ-LVP-05 | Entry point default backfill SHALL replace `None` defaults with literal values discovered... | `test_factory_aggregation.py` | PASS |
| REQ-LVP-06 | `usage_type_map` SHALL be threaded from `HierarchyExtractionResult` through `build_comput... | `test_factory_aggregation.py` | PASS |
| REQ-LVP-08 | `usage_type_map` SHALL resolve each `(owning_qn, usage_name)` to the most-specific owned FeatureTyping target (not `next(iter(member.types))`); incomparable multi-typings resolve sorted-first with V10 | `test_type_indexing.py` | PASS |
| REQ-LVP-09 | `_index_usage_level_retypes` SHALL index usage-level retypes of inherited part usages (`part hif_plant : Base { part :>> driver : Subtype }`) into `usage_type_map` keyed by the CONTAINER usage's instance QN, limited to GENUINE retypes (a `:>>` redefinition whose most-specific owned type differs from the base def's declared type for that member) so value-only `:>>` overrides are excluded and non-two-level snapshots stay byte-identical (REQ-HR-09 released) | `test_spec_chain_twolevel.py` | PASS |
| REQ-LVP-07 | Literal default found SHALL keep module `FULLY_COMPILABLE`; no default SHALL set `MANUAL_... | `test_factory_aggregation.py` | PASS |

### MF

**Module Factory** — Component C14 — [reference/05-module-factory.md](reference/05-module-factory.md)

| REQ ID | Requirement | Test File | Status |
|--------|-------------|-----------|--------|
| REQ-MF-01 | All three factory functions SHALL be pure data transformers: return `(PipelineModule, dic... | `test_factory_aggregation.py`, `test_factory_calc_usage.py`, `test_factory_formula.py`, `test_factory_purity.py` | PASS |
| REQ-MF-02 | CalcUsage factory SHALL fail-fast (`ValueError`) on missing `binding_resolutions` key -- ... | `test_factory_calc_usage.py` | PASS |
| REQ-MF-03 | FORMULA factory SHALL set `is_computed_attribute=True` and `compilability=FULLY_COMPILABL... | `test_factory_formula.py` | PASS |
| REQ-MF-04 | Aggregation factory SHALL handle all three extraction term types: SumTerm, SingletonTerm,... | `test_factory_aggregation.py` | PASS |
| REQ-MF-05 | Every ModuleInput SHALL have exactly one InputSource with `source_type` in {`module_outpu... | `test_factory_aggregation.py`, `test_factory_calc_usage.py`, `test_factory_formula.py` | PASS |
| REQ-MF-06 | SumTerm and SingletonTerm LITERAL fallback SHALL use `_find_literal_redefinition()` to pr... | `test_factory_aggregation.py` | PASS |
| REQ-MF-07 | LocalTerm resolution SHALL try: (1) sibling aggregation output, (2) EXPOSE_PURE alias, (3... | `test_factory_aggregation.py` | PASS |
| REQ-MF-08 | Single-output modules SHALL use `field_name="root"`; multi-output SHALL use attribute nam... | `test_factory_calc_usage.py` | PASS |

### NC

**Naming Conventions** — Component C02 — [reference/15-naming-conventions.md](reference/15-naming-conventions.md)

| REQ ID | Requirement | Test File | Status |
|--------|-------------|-----------|--------|
| REQ-NC-01 | EQN SHALL be constructed by joining sanitized owner-chain segments with `__` | `test_naming_conventions.py` | PASS |
| REQ-NC-02 | PQN SHALL extend an EQN with `__{param_name}` | `test_naming_conventions.py` | PASS |
| REQ-NC-03 | Module name SHALL equal the EQN lowercased | `test_naming_conventions.py` | PASS |
| REQ-NC-04 | Module type SHALL use `{namespace}.{ElementName}Module` format | `test_naming_conventions.py` | PASS |
| REQ-NC-05 | Channel names SHALL be PQNs — no separate channel concept exists | `test_naming_conventions.py` | PASS |
| REQ-NC-06 | `sanitize_name()` SHALL apply 6 transforms in order: strip quotes, spaces→`_`, non-alnum→... | `test_naming_conventions.py` | PASS |
| REQ-NC-07 | Registry keys SHALL use typed wrappers: scoped and alias registries use `ScopedKey` (dott... | `test_naming_conventions.py` | PASS |
| REQ-NC-08 | Identifier derivation SHALL sanitize each qualified-name segment before it becomes a class name, module file path, or FORMULA module_eqn/channel | `test_alias_agg_probe_generation.py` | PASS |
| REQ-NC-09 | Generation SHALL fail fast when two distinct SysML names sanitize to one output path, naming both source names and the shared path | `test_duplicate_path_failfast.py` | PASS |

### OR

**Output Registry** — Component C08 — [reference/10-output-registry.md](reference/10-output-registry.md)

| REQ ID | Requirement | Test File | Status |
|--------|-------------|-----------|--------|
| REQ-OR-01 | Registry SHALL map every reference format (FCE dotted path, FRE qualified name, redefinit... | `test_output_registry.py` | PASS |
| REQ-OR-02 | Each typed registry SHALL have its own exact-match lookup method — no single `resolve()` ... | `test_output_registry.py` | PASS |
| REQ-OR-03 | Collision policy: scoped and SysML QN registries SHALL raise on duplicate (unique by cons... | `test_output_registry.py` | PASS |
| REQ-OR-04 | `register_alias()` SHALL enforce phase ordering — target must already be in `_canonical` | `test_output_registry.py` | PASS |
| REQ-OR-05 | Phase 1 SHALL register: Key_C as `ScopedKey` and Key_A as a guarded first-wins alias (`register_alias`) per CalcUsage output (Phase 1a); Key_E_stripped scoped for aggregation (Phase 1b); Key_F scoped for FORMULA REFERENCE-secondary (Phase 1c). The ambiguous Key_A format is kept out of the scoped registry — it exists only as a phase-order-guarded alias (target must be in `_canonical`, REQ-OR-04) | `test_output_registry.py` | PASS |
| REQ-OR-06 | Phase 2-4 aliases SHALL resolve their canonical target through typed **resolution-time** lookup (`scoped_lookup`/`alias_lookup`) before registering. The construction-time `instance_attr_to_channel` Key_A dict is a build-time helper that feeds only guarded `register_alias` calls — it registers nothing itself | `test_output_registry.py` | PASS |
| REQ-OR-07 | Key_C SHALL be constructed via `make_scoped_key()` — strip design prefix from EQN, join w... | `test_output_registry.py` | PASS |
| REQ-OR-08 | Key_A SHALL NOT be registered as a scoped key — the ambiguous format is kept out of the scoped registry (Key_C is its scoped form). Key_A IS registered as a guarded first-wins alias (Phase 1a `register_alias`), reachable via `alias_lookup` for cross-scope CHAIN resolution | `test_output_registry.py` | PASS |
| REQ-OR-09 | The FORMULA sysml-QN key SHALL be registered per-segment sanitized (`sanitize_qualified_name`), and the per-collision alias line SHALL be DEBUG with one WARNING count-summary at build (Item 7 / D5, lockstep site 1) | `test_output_registry.py`, `test_output_registry_construction.py`, `test_warning_reconciliation.py` | PASS |

### ORCH

**Orchestration** — Component C19 — [reference/02-orchestration.md](reference/02-orchestration.md)

| REQ ID | Requirement | Test File | Status |
|--------|-------------|-----------|--------|
| REQ-ORCH-01 | `build_pipeline_context()` SHALL execute steps in strict dependency order: 3.5 before 4, ... | `test_orchestrator.py` | PASS |
| REQ-ORCH-02 | Step 3.5 SHALL rewrite virtual bindings in-place before any downstream step reads `calc_u... | `test_orchestrator.py` | PASS |
| REQ-ORCH-03 | Step 4.5 SHALL remove FORMULA-classified computed attributes from `design_attrs` before P... | `test_orchestrator.py` | PASS |
| REQ-ORCH-04 | OutputRegistry SHALL register outputs in strict phase order: 1a/1b/1c (canonical) then 2/... | `test_orchestrator.py` | PASS |
| REQ-ORCH-05 | Each aggregation expression SHALL be scoped to its concrete design instance path(s) via v... | `test_orchestrator.py` | PASS |
| REQ-ORCH-06 | `build_pipeline_context()` SHALL return a PipelineContext where `computation_graph` is th... | `test_orchestrator.py` | PASS |
| REQ-ORCH-07 | CHAIN alias canonical names SHALL resolve to Phase 1 channels. Unresolvable aliases produ... | `test_orchestrator.py` | PASS |

### OSR

**Output Schema Rules** — Component C22 — [reference/22-output-schema-rules.md](reference/22-output-schema-rules.md)

| REQ ID | Requirement | Test File | Status |
|--------|-------------|-----------|--------|
| REQ-OSR-01 | Single-output modules SHALL use `RootModel[float]` with `field_name="root"` | `test_gen_schemas.py` | PASS |
| REQ-OSR-02 | Multi-output modules (2+ outputs) SHALL generate a named `MultiOutput` subclass | `test_gen_schemas.py` | PASS |
| REQ-OSR-03 | Output field names SHALL match SysML `output_attributes` names exactly | `test_gen_schemas.py` | PASS |
| REQ-OSR-04 | SysML types SHALL map to Python types per the type mapping table | `test_gen_schemas.py` | PASS |
| REQ-OSR-05 | Output fields on `MultiOutput` MUST NOT have `default=...` values | `test_gen_schemas.py` | PASS |
| REQ-OSR-06 | Aggregation and computed-attribute modules SHALL always be single-output (`"root"`) | `test_gen_schemas.py` | PASS |
| REQ-OSR-07 | Output channels SHALL use PQN format via `get_channel_name()` | `test_gen_schemas.py` | PASS |

### PGD

**Parameter Group Deriver** — Component C13 — [reference/17-parameter-group-deriver.md](reference/17-parameter-group-deriver.md)

| REQ ID | Requirement | Test File | Status |
|--------|-------------|-----------|--------|
| REQ-PGD-01 | Every entry point SHALL be assigned to exactly one parameter group | `test_parameter_group_deriver.py` | PASS |
| REQ-PGD-02 | Four indexes SHALL be built with strict precedence: attr > binding > unbound > literal | `test_parameter_group_deriver.py` | PASS |
| REQ-PGD-03 | Grouping SHALL mirror SysML source file structure (one group per file) | `test_parameter_group_deriver.py` | PASS |
| REQ-PGD-04 | `derive_groups_filtered()` SHALL remove parameters not in `backtracking_result.entry_poin... | `test_parameter_group_deriver.py` | PASS |
| REQ-PGD-05 | `classify()` SHALL check indexes in precedence order and return group name or `None` | `test_parameter_group_deriver.py` | PASS |
| REQ-PGD-06 | The deriver SHALL resolve each entry point's numeric default from its owning index (attr / binding / unbound / literal) | *(pinning tests removed with the dead accessor in Item 8 — re-frame/retire pending)* | PENDING-ITEM7 · `[ITEM7-PGD06]` |
| REQ-PGD-07 | Group names SHALL follow `{snake_case_stem}_params` / `{PascalCaseStem}Params` convention | `test_parameter_group_deriver.py` | PASS |
| REQ-PGD-08 | No deriver change is required for def-owned design-attribute matching (D1): once the backtracker (REQ-BT-10) returns the design-attr QN, the deriver's `_attr_index`-keyed classification and inline default resolution handle grouping and default automatically | `test_matcher_fixes_item7.py` (backtracker propagation), `test_parameter_group_deriver.py` | PASS |

### PIPE

**Pipeline** — Component C19 — [reference/00-pipeline-overview.md](reference/00-pipeline-overview.md)

| REQ ID | Requirement | Test File | Status |
|--------|-------------|-----------|--------|
| REQ-PIPE-01 | The pipeline SHALL produce exactly one ComputationGraph from a set of SysML model files. | `test_orchestrator.py`, `test_pipeline_e2e.py` | PASS |
| REQ-PIPE-02 | Every ModuleInput SHALL be wired to exactly one source: `module_output` or `entry_point`. | `test_orchestrator.py`, `test_pipeline_e2e.py` | PASS |
| REQ-PIPE-03 | Every `module_output` reference SHALL resolve to a canonical channel in the OutputRegistr... | `test_orchestrator.py`, `test_pipeline_e2e.py` | PASS |
| REQ-PIPE-04 | `execution_order` SHALL be a valid topological sort -- no module reads from a module that... | `test_orchestrator.py`, `test_pipeline_e2e.py` | PASS |
| REQ-PIPE-05 | Every EntryPoint SHALL be classified as exactly one of {`LIBRARY_DEFAULT`, `DESIGN_ATTRIB... | `test_orchestrator.py`, `test_pipeline_e2e.py` | PASS |
| REQ-PIPE-06 | The graph SHALL include all three module types: CalcUsage, FORMULA, and Aggregation. | `test_orchestrator.py`, `test_pipeline_e2e.py` | PASS |
| REQ-PIPE-07 | Generation SHALL produce output exclusively from `ComputationGraph` -- no back-references... | `test_gen_module_wrappers.py`, `test_generation_boundary.py`, `test_orchestrator.py`, `test_pipeline_e2e.py` | PASS |

### PMM

**PipelineModule Migration** — Component C26 — [reference/26-pipeline-module-migration.md](reference/26-pipeline-module-migration.md)

| REQ ID | Requirement | Test File | Status |
|--------|-------------|-----------|--------|
| REQ-PMM-01 | `PipelineModule` SHALL carry all metadata needed by module wrapper generation (calc def n... | `test_pipeline_module_expansion.py` | PASS |
| REQ-PMM-02 | `ModuleInput` and `ModuleOutput` SHALL carry `description` and `default_value` fields for... | `test_pipeline_module_expansion.py` | PASS |
| REQ-PMM-03 | `PipelineModule` SHALL carry `calc_expressions` for stencil comment generation. | `test_pipeline_module_expansion.py` | PASS |
| REQ-PMM-04 | Migration SHALL produce byte-identical output compared to pre-migration baselines. | `test_pipeline_module_expansion.py` | PASS |
| REQ-PMM-05 | Migration SHALL proceed in phases: add fields, create variants, deprecate, remove. | `test_pipeline_module_expansion.py` | PASS |

### PY

**Pipeline YAML** — Component C20 — [reference/21-pipeline-yaml-generation.md](reference/21-pipeline-yaml-generation.md)

| REQ ID | Requirement | Test File | Status |
|--------|-------------|-----------|--------|
| REQ-PY-01 | ALL entry point sources in pipeline YAML SHALL include a `param_group.` prefix | `test_gen_pipeline_yaml.py` | PASS |
| REQ-PY-02 | `InputSource.param_group` SHALL NOT be None for any entry point in the ComputationGraph | `test_gen_pipeline_yaml.py` | PASS |
| REQ-PY-03 | ALL numeric pipeline input types SHALL be `"float"` (including multiplicity counts) | `test_gen_pipeline_yaml.py` | PASS |
| REQ-PY-04 | MODULE_OUTPUT sources with `field_name == "root"` SHALL append `.root` to the channel name | `test_gen_pipeline_yaml.py` | PASS |
| REQ-PY-05 | `channel_field_map` SHALL contain an entry for every `ModuleOutput` in the graph | `test_gen_pipeline_yaml.py` | PASS |
| REQ-PY-06 | Exit point type SHALL be `RootModel[T]` when `field_name == "root"`, else `T` | `test_gen_pipeline_yaml.py` | PASS |
| REQ-PY-07 | Entry point module inputs SHALL list one JSON file per `ParameterGroup` | `test_gen_json_templates.py`, `test_gen_pipeline_yaml.py` | PASS |
| REQ-PY-08 | An aliased channel's exit line SHALL render the modeler's instance-qualified name as its output filename (`{instance_path}__{alias_name}.json`); the exit **key** stays the canonical channel and the type token is unchanged (REQ-PY-06 holds), so simkit's key-is-a-channel check still passes | `test_gen_pipeline_yaml.py` | PASS |

### REG

**Module Registry** — Component C24 — [reference/20-module-registry-generation.md](reference/20-module-registry-generation.md)

| REQ ID | Requirement | Test File | Status |
|--------|-------------|-----------|--------|
| REQ-REG-01 | Aggregation module import paths SHALL use design-scoped EQN (`module_eqn`), not library Q... | `test_gen_registry.py` | PASS |
| REQ-REG-02 | Import paths in registry SHALL match actual filesystem paths generated by CLI | `test_gen_registry.py` | PASS |
| REQ-REG-03 | Class names in `module_type_override` dict SHALL be globally unique | `test_gen_registry.py` | PASS |
| REQ-REG-04 | When class names collide, registry SHALL use aliased imports (`import X as Assembly_X`) | `test_gen_registry.py` | PASS |
| REQ-REG-05 | CalcUsage, computed attribute, and aggregation modules SHALL all derive paths from design... | `test_gen_registry.py` | PASS |
| REQ-REG-06 | `CUSTOM_SCHEMA_TYPES` SHALL include all exit point primitive types used by any module | `test_gen_registry.py` | PASS |
| REQ-REG-07 | Registry generation SHALL detect and report name collisions before rendering | `test_gen_registry.py` | PASS |
| REQ-REG-08 | After parent-segment aliasing, registry SHALL re-check class-name uniqueness and fail fast on any residual collision | `test_sc11_recheck.py` | PASS |

### RES

**Resolution Overview** — Component — — [reference/03-resolution-overview.md](reference/03-resolution-overview.md)

| REQ ID | Requirement | Test File | Status |
|--------|-------------|-----------|--------|
| REQ-RES-01 | Every ModuleInput SHALL resolve to exactly one of {`module_output`, `entry_point`}. | — | UNTESTED |
| REQ-RES-02 | Three live resolution mechanisms: CalcUsage uses backtracker DFS cascade (11); FORMULA uses the pre-computed attribute resolution map (16); aggregation SumTerm/SingletonTerm uses `_resolve_aggregation_input_channel` (`graph_builder.py`). The consolidated `resolve_input()` is parity-validated but not yet wired ([ITEM7-F4-CUTOVER]) | — | UNTESTED |
| REQ-RES-03 | Factory functions SHALL return `(PipelineModule, dict[str, EntryPoint])` -- no mutation o... | — | UNTESTED |
| REQ-RES-04 | Every `module_output` reference SHALL resolve to a canonical channel in the OutputRegistr... | — | UNTESTED |
| REQ-RES-05 | The orchestrator SHALL be a linear sequence: classify -> build modules -> rebuild groups ... | — | UNTESTED |
| REQ-RES-06 | `binding_resolutions` from the backtracker SHALL be the single source of truth for CalcUs... | — | UNTESTED |
| REQ-RES-07 | Resolution of scope-relative references (CHAIN `source_path`) SHALL use the consumer's pa... | — | UNTESTED |
| REQ-RES-08 | Consumer scope derivation SHALL apply to ALL live resolution paths: backtracker (CalcUsage), attribute resolution map (FORMULA), and `_resolve_aggregation_input_channel` (aggregation) — and to the parity-validated `resolve_input()` via `ResolutionContext.consumer_scope` | — | UNTESTED |

### SNAP

**Extraction Snapshots** — Extraction Snapshots

| REQ ID | Requirement | Test File | Status |
|--------|-------------|-----------|--------|
| REQ-SNAP-01 | Snapshot files exist and deserialize without error | `test_extraction_snapshots.py` | PASS |
| REQ-SNAP-02 | CalculationDefinitionData fields populated | `test_extraction_snapshots.py` | PASS |
| REQ-SNAP-03 | CalcUsageData bindings have typed BindingType | `test_extraction_snapshots.py` | PASS |
| REQ-SNAP-04 | HierarchyExtractionResult round-trips with tuple keys | `test_extraction_snapshots.py` | PASS |
| REQ-SNAP-05 | AST fields are None (not serialized Java objects) | `test_extraction_snapshots.py` | PASS |
| REQ-SNAP-06 | Path fields are Path instances, not strings | `test_extraction_snapshots.py` | PASS |
| REQ-SNAP-07 | Enum fields are typed enum instances, not raw strings | `test_extraction_snapshots.py` | PASS |
| REQ-SNAP-08 | Promoted snapshot helpers live only in `src`; no second copy (INV-3) | `test_snapshot_contract.py` | PASS |
| REQ-SNAP-09 | Missing/mismatched `snapshot_format_version` is a hard error before deserialization (INV-2, V1/V2) | `test_snapshot_contract.py` | PASS |
| REQ-SNAP-10 | Re-captured expression-bearing snapshot carries `compilation_results` (INV-5) | `test_snapshot_contract.py` | PASS |
| REQ-SNAP-11 | Version-current snapshot missing `compilation_results` degrades with a warning (V4) | `test_snapshot_contract.py` | PASS |
| REQ-SNAP-12 | Stale source hash warns; run continues (V3) | `test_snapshot_contract.py` | PASS |
| REQ-SNAP-13 | Snapshot context has null extractor/backtracker and still generates (INV-4/B1) | `test_snapshot_generation.py` | PASS |
| REQ-SNAP-14 | `generate --from-snapshot` completes with no license at runtime (INV-1) | `test_snapshot_generation.py` | PASS |
| REQ-SNAP-15 | No provenance/version text appears in a generated artifact (INV-6) | `test_snapshot_generation.py` | PASS |
| REQ-SNAP-16 | CLI accepts exactly one extraction input; rejects `--design-path-filter` + snapshot (INV-7/V6) | `test_snapshot_generation.py` | PASS |
| REQ-SNAP-17 | CalcUsage auto-implements from a snapshot (SC-10) | `test_snapshot_generation.py` | PASS |
| REQ-SNAP-18 | The lone `generation_timestamp` template var has zero render sites | `test_snapshot_generation.py` | PASS |
| REQ-SNAP-19 | Live generation is byte-identical to snapshot generation, incl. symlinked models (license-gated; skips cleanly without a license, verified live during Item 2) | `test_snapshot_generation.py` | PASS |

### SR

**Smart Regen / Preservation** — Component C23 — [reference/23-smart-regen-preservation.md](reference/23-smart-regen-preservation.md)

| REQ ID | Requirement | Test File | Status |
|--------|-------------|-----------|--------|
| REQ-SR-01 | Signature comparison SHALL use two-level matching: type-level (required) then field-level... | `test_gen_stencils.py` | PASS |
| REQ-SR-02 | Field comparison SHALL be order-independent (sorted) | `test_gen_stencils.py` | PASS |
| REQ-SR-03 | `should_regenerate_stencil()` SHALL implement the 4-case decision tree | `test_gen_stencils.py` | PASS |
| REQ-SR-04 | Stub upgrade SHALL require all 3 conditions: signature match, `NotImplementedError` prese... | `test_gen_stencils.py` | PASS |
| REQ-SR-05 | Backup SHALL be created before every regeneration or upgrade | `test_gen_stencils.py` | PASS |
| REQ-SR-06 | Aggregation and computed-attribute modules are synthetic and always regenerated in practi... | `test_gen_stencils.py` | PASS |
| REQ-SR-07 | `--preserve-handwritten` SHALL skip ALL existing handwritten files without comparison | `test_gen_stencils.py` | PASS |

### SVM

**Supplied-Value Materializer** (PIPELINE-TRUTH Item 2) — `resolution/supplied_values.py` — [reference/25-hierarchy-resolver.md](reference/25-hierarchy-resolver.md#supplied-value-materializer-req-svm-01-04). Reuses doc 18's shared `_find_literal_redefinition` helper (Strategy 1); sibling of doc 12's per-consumer VBR-03 (this mechanism keys by source QN and collapses across consumers).

| REQ ID | Requirement | Test File | Status |
|--------|-------------|-----------|--------|
| REQ-SVM-01 | For a referenced subsystem-attr binding, synthesize a design attribute carrying the LITERAL value resolved by precedence (usage override > specialized-def `:>>` > base def), `default_value` as a string | `test_supplied_values.py` | PASS |
| REQ-SVM-02 | Key the synthetic attribute by source QN so differently-named consumers collapse to one entry point | `test_supplied_values.py`, `test_fusion_tea_snapshot.py` | PASS |
| REQ-SVM-03 | A synthetic attribute SHALL never overwrite a real captured design attribute; on collision the real one wins and the materializer WARNs | `test_supplied_values.py` | PASS |
| REQ-SVM-04 | Apply LITERAL only; emit a count-summary WARN naming non-literal (CHAIN/EXPRESSION) skips; a referenced non-literal-only binding falls through to Step-4 (V11), never a silent drop | `test_supplied_values.py` | PASS |

### VBR

**Virtual Binding Rewrite** — Component C09 — [reference/12-virtual-binding-rewrite.md](reference/12-virtual-binding-rewrite.md)

| REQ ID | Requirement | Test File | Status |
|--------|-------------|-----------|--------|
| REQ-VBR-01 | Override index SHALL be keyed by `(full_parent_path, leaf_attribute_name)` | `test_virtual_binding_rewrite.py` | PASS |
| REQ-VBR-02 | Deep-path overrides SHALL join intermediate `target_path` segments with `__` to form `ful... | `test_virtual_binding_rewrite.py` | PASS |
| REQ-VBR-03 | LITERAL override SHALL set `binding_type=LITERAL`, copy `literal_value`, clear `source_pa... | `test_virtual_binding_rewrite.py` | PASS |
| REQ-VBR-04 | CHAIN override SHALL replace `source_path` with the redefinition's `source_path` | `test_virtual_binding_rewrite.py` | PASS |
| REQ-VBR-05 | Template copies (`is_template=True`) SHALL be skipped during rewriting | `test_virtual_binding_rewrite.py` | PASS |
| REQ-VBR-06 | Bindings already LITERAL or with no `source_path` SHALL be skipped (no double-rewrite) | `test_virtual_binding_rewrite.py` | PASS |
| REQ-VBR-07 | Rewriting SHALL complete BEFORE any downstream processing (Step 3.5 ordering) | `test_virtual_binding_rewrite.py` | PASS |
| REQ-VBR-08 | `_create_virtual_calc_usage` SHALL shallow-copy each `BindingInfo` so no two virtual instances share a binding object (divergent-sibling rewrite correctness; Item 10 precondition) | `test_virtual_binding_rewrite.py` | PASS |
| REQ-VBR-09 | `_rewrite_virtual_bindings` SHALL NOT raise on a bare-name `source_path`; it logs DEBUG and skips the override match | `test_virtual_binding_rewrite.py` | PASS |
| REQ-VBR-10 | Mechanism-D home (Item 10 #3): `_rewrite_specialized_chain` SHALL rewrite a `part_usage.attr` CHAIN binding through the retyped usage's specialized-def `:>>` chain (three-tier merge: usage override > specialized-def `:>>` > base def); and `_rescue_self_named_bindings` SHALL rewrite a full-QN self-reference (`in x = x`) to its upstream channel when an outer same-named EXPOSE resolves, else leave it as-is (the `self_named_binding_trap` negative) | `test_spec_chain_channel.py`, `test_self_named_rescue.py` | PASS |
| REQ-VBR-11 | The `_rewrite_specialized_chain` type-select SHALL be instance-aware: it SHALL try the consumer INSTANCE's path key (`usage.qualified_name.rsplit("__",1)[0]`, `part_usage`) in `usage_type_map` before the declaring-def key, so a two-level specialization (usage-level `:>> driver : Subtype` on an inherited part usage) selects the specialized def where the declaring-def key sees only the base type | `test_spec_chain_twolevel.py` | PASS |

---

## Untested Requirements

These requirements have no dedicated conformance test. Most are cross-cutting
architectural principles or documentation-only constraints.

- **REQ-CA-08**: FORMULA compilation SHALL NOT resolve sibling FORMULA outputs
  - Source: [reference/16-computed-attributes.md](reference/16-computed-attributes.md)
- **REQ-DM-08**: Name fields with semantic format constraints SHALL use NewType wrappers, not bare `str`
  - Source: [reference/09-data-models.md](reference/09-data-models.md)
- **REQ-GEN-03**: Multi-output modules (2+ outputs) SHALL get a `MultiOutput` schema in `schemas/`; single-output modules SHALL use `Root...
  - Source: [reference/08-generation.md](reference/08-generation.md)
- **REQ-GEN-07**: Every generated module SHALL be registered in `__init__.py` for TEAx framework discovery.
  - Source: [reference/08-generation.md](reference/08-generation.md)
- **REQ-RES-01**: Every ModuleInput SHALL resolve to exactly one of {`module_output`, `entry_point`}.
  - Source: [reference/03-resolution-overview.md](reference/03-resolution-overview.md)
- **REQ-RES-02**: Three live resolution mechanisms: CalcUsage backtracker DFS cascade (11); FORMULA attribute resolution map (16); aggregation `_resolve_aggregation_input_channel`. The consolidated `resolve_input()` is parity-validated but not yet wired ([ITEM7-F4-CUTOVER]).
  - Source: [reference/03-resolution-overview.md](reference/03-resolution-overview.md)
- **REQ-RES-03**: Factory functions SHALL return `(PipelineModule, dict[str, EntryPoint])` -- no mutation of shared state (REQ-RES-03a: n...
  - Source: [reference/03-resolution-overview.md](reference/03-resolution-overview.md)
- **REQ-RES-04**: Every `module_output` reference SHALL resolve to a canonical channel in the OutputRegistry.
  - Source: [reference/03-resolution-overview.md](reference/03-resolution-overview.md)
- **REQ-RES-05**: The orchestrator SHALL be a linear sequence: classify -> build modules -> rebuild groups -> toposort -> validate.
  - Source: [reference/03-resolution-overview.md](reference/03-resolution-overview.md)
- **REQ-RES-06**: `binding_resolutions` from the backtracker SHALL be the single source of truth for CalcUsage input wiring. Key format: ...
  - Source: [reference/03-resolution-overview.md](reference/03-resolution-overview.md)
- **REQ-RES-07**: Resolution of scope-relative references (CHAIN `source_path`) SHALL use the consumer's parent scope to construct a `Sco...
  - Source: [reference/03-resolution-overview.md](reference/03-resolution-overview.md)
- **REQ-RES-08**: Consumer scope derivation SHALL apply to ALL resolution paths: backtracker (CalcUsage), attribute resolution map (FORMU...
  - Source: [reference/03-resolution-overview.md](reference/03-resolution-overview.md)

---

## Related Documents

- [Architecture Overview](overview.md)
- [Modeling Assumptions](modeling-assumptions.md)
- Design docs: [reference/](reference/) (28 documents)
- Conformance tests: `tests/conformance/` (33 test files)
