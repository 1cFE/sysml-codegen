# Verification Matrix

Traceability matrix mapping every REQ-\* tag to its conformance test file and status.

## Summary

| Metric | Count |
|--------|-------|
| Total requirements | 259 |
| PASS (test exists and passes) | 258 |
| UNTESTED (no dedicated test) | 1 |
| DEFERRED | 0 |
| REQ families | 30 |
| Distinct test files cited | 65 |

**Status definitions:**
- **PASS**: At least one conformance test references this requirement and passes
- **UNTESTED**: No conformance test directly references this requirement
- **DEFERRED**: Behavior implemented; real-fixture test deferred to a later item (none open — REQ-CA-09 discharged by Item 10)

UNTESTED requirements are either cross-cutting architectural principles verified
indirectly through component-level tests, or design-only requirements that constrain
the documentation rather than executable code.

> **Sweep note (PIPELINE-TRUTH Item 7).** The ~175-row deep-read sweep found ~30 PASS
> rows whose cited test passes but pins *less* than the full requirement text (e.g.
> field-name-only compares, `>=` count floors, self-contained parse checks). None is a
> correctness lie. They are enumerated with per-row dispositions in
> `[ITEM7-MATRIX-SWEEP-RESIDUE]` (backlog), to fix when each owning component is next
> touched. ~46 qualifying rows remain un-deep-read (named there — not asserted swept).

## Index

- [AS — Aggregation Scoping](#as) (8/8 pass)
- [AST — AST Dispatch Invariant](#ast) (10/10 pass)
- [BASE — Baseline Conformance](#base) (6/6 pass)
- [BT — Backtracker](#bt) (13/13 pass)
- [CA — Computed Attributes](#ca) (12/12 pass)
- [DM — Data Models](#dm) (8/9 pass, 1 untested)
- [DRA — Dual Resolution Architecture](#dra) (5/5 pass)
- [EC — Expression Compiler](#ec) (7/7 pass)
- [EPC — Entry Point Classification](#epc) (8/8 pass)
- [EXT — Extraction](#ext) (14/14 pass)
- [GA — Graph Assembly](#ga) (8/8 pass)
- [GEN — Generation](#gen) (7/7 pass)
- [HR — Hierarchy Resolver](#hr) (8/8 pass)
- [IR — Input Resolver](#ir) (7/7 pass)
- [LVP — Literal Value Propagation](#lvp) (9/9 pass)
- [MF — Module Factory](#mf) (9/9 pass)
- [NC — Naming Conventions](#nc) (9/9 pass)
- [OR — Output Registry](#or) (9/9 pass)
- [ORCH — Orchestration](#orch) (7/7 pass)
- [OSR — Output Schema Rules](#osr) (7/7 pass)
- [PGD — Parameter Group Deriver](#pgd) (7/8 pass, 1 untested)
- [PIPE — Pipeline](#pipe) (7/7 pass)
- [PMM — PipelineModule Migration](#pmm) (5/5 pass)
- [PY — Pipeline YAML](#py) (8/8 pass)
- [REG — Module Registry](#reg) (9/9 pass)
- [RES — Resolution Overview](#res) (6/8 pass, 2 untested)
- [SNAP — Snapshots: Extraction Format & Snapshot-Driven Generation](#snap) (20/20 pass)
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
| REQ-BT-12 | For a 3+-segment CHAIN (`source_path.count(".") >= 2`), `_resolve_chain_dispatch` SHALL, after Step 2 misses, retry `scoped_lookup` over progressively shorter ancestor prefixes of the consumer scope (Step CLIMB, Item 2), collect every distinct non-self-reference hit, resolve iff exactly one, and refuse (return None → loud Step-4 fallback) on two or more — never silently pick (M-1 / INV-2b). Gated so 2-segment resolutions stay byte-identical (D4) | `test_dependency_backtracker.py`, `test_deep_cross_scope_probe.py` | PASS |
| REQ-BT-13 | A 3+-segment CHAIN that reaches the Step-4 fallback SHALL emit a genuine `logger.warning` (WARNING level, distinct from the benign per-binding DEBUG line) naming the full untruncated chain, and surface as an entry point — never truncated to root, never silently wired (Item-5 loud-diagnostic contract, D3 home) | `test_dependency_backtracker.py` (fires-on-shape + silent-on-clean) | PASS |

### CA

**Computed Attributes** — Component C05 — [reference/16-computed-attributes.md](reference/16-computed-attributes.md)

**Classification contract (Item 4, fixed):** an attribute that references only inherited and/or local attributes classifies FORMULA. An inherited attribute's QN resolves into the **supertype (ancestor PartDef)** namespace; Step-2b now prefix-matches the owning part QN OR any ancestor PartDef QN (`computed_attribute_extractor._ancestor_part_qns`), so an inherited-attr ref is a sibling, not a cross-namespace calc output. A genuine calc output (D3 `mixed_expose`) still classifies EXPOSE_COMPUTED — the over-correction control. Pinned positively by **REQ-CA-12** and the 7-row `TestInheritedAttrClassification` table; the old `test_misclassification_documented` xfail site is deleted (no vacuous parametrization). The prior framing called this misclassification "**loud** (EXPOSE_COMPUTED rejection)" — that was wrong: a misclassified inherited-attr FORMULA was a **silent no-op**, dropped by the graph builder with no module and no diagnostic (`graph_builder.py:269-288`; `test_computed_attributes_e2e.py`); only the "not a silent wrong value" half was true. The residual no-module outcome for these MANUAL_REQUIRED FORMULAs is now loud at generation via the graph-builder D5 diagnostic; actually compiling them is the filed follow-on `[TRUTH-DEBT-INHERITED-FORMULA-COMPILE]`.

| REQ ID | Requirement | Test File | Status |
|--------|-------------|-----------|--------|
| REQ-CA-01 | Classification SHALL produce exactly one of the 5 stable values per attribute expression (the transient sixth, `EXPOSE_CHAIN_TENTATIVE`, never survives the Phase-3b confirm pass to a reader — INV-F) | `test_computed_attributes.py` | PASS |
| REQ-CA-02 | FORMULA attributes SHALL compile to Python via `build_expression_ast()` + `compile_expres... | `test_computed_attributes.py` | PASS |
| REQ-CA-03 | EXPOSE_PURE SHALL produce a `ChannelAlias` for a PartUsage-level derived attribute; a PartDef-level EXPOSE (shape A) SHALL be expanded per design instance path into the structured `_scoped_alias` namespace (`_register_partdef_expose_scoped_aliases`, Item 10 #4) rather than emitting a template alias | `test_computed_attributes.py`, `test_wi014_toy.py` | PASS |
| REQ-CA-10 | A pure `FeatureChainExpression` whose `reference_chain` is a part-rooted ≥2-segment single-terminal chain (INV-E) SHALL be tagged `EXPOSE_CHAIN_TENTATIVE`, then the Phase-3b confirm walk over `reference_chain` SHALL finalize it to EXPOSE_PURE (+register the transitive channel) or revert to FORMULA; no tentative SHALL survive to any reader (INV-F raises) | `test_computed_attribute_extraction.py`, `test_ife_plant.py` | PASS |
| REQ-CA-04 | LITERAL attributes SHALL be excluded from computed attributes | `test_computed_attributes.py` | PASS |
| REQ-CA-05 | No `EXPOSE_PURE` alias exists for a non-EXPOSE_PURE attribute; and all fixtures contain zero UNRESOLVABLE computed attributes (the "UNRESOLVABLE SHALL not generate modules/aliases" contract is unexercised — documented coverage gap) | `test_computed_attributes.py` | PASS |
| REQ-CA-06 | `AttributeResolutionKind` SHALL classify each FORMULA input as FORMULA, EXPOSE_ALIAS, or ... | `test_computed_attributes.py` | PASS |
| REQ-CA-07 | FORMULA self-reference SHALL be excluded from `input_names` | `test_computed_attributes.py` | PASS |
| REQ-CA-08 | FORMULA compilation SHALL NOT resolve sibling FORMULA outputs | `test_computed_attributes.py` | PASS |
| REQ-CA-09 | Shape-A resolution (part-def EXPOSE): the wi014_toy `demo_plant.total_cost` consumer SHALL resolve via `_scoped_alias` to the `cost_calc__cost` channel (the Item-1 malformed-refs deferral, discharged by Item 10 #4/#1) | `test_wi014_toy.py` | PASS |
| REQ-CA-11 | Shape-A EXPOSE_PURE (part def) in the attribute resolution map SHALL route by `is_on_part_definition` to a LITERAL fallback (not the refs-parser) and consult `_scoped_alias` to decide the warning: a registered leaf is silent (the name resolves via Item 10 and surfaces via Item 11), an unregistered one warns naming the real cause — retiring the Item-1 malformed-refs warning (`_resolve_expose_pure` in `graph_builder.py`) for the resolvable case | `test_wi014_toy.py` | PASS |
| REQ-CA-12 | A reference whose QN sits under the owning part OR any **ancestor PartDef** namespace SHALL be treated as a sibling (Step-2b widened via `_ancestor_part_qns`, transitive), so an attribute referencing only inherited/local attributes classifies FORMULA — not EXPOSE_COMPUTED; a reference under a top-level CalcDef namespace SHALL stay a `calc_ref` (D3 over-correction control, `mixed_expose`). A FORMULA computed attribute that reaches graph-build without being FULLY_COMPILABLE SHALL emit a WARN and produce no module (D5 — the no-module outcome is loud, never a silent drop) | `test_computed_attributes.py`, `test_computed_attribute_extraction.py`, `test_graph_builder_computed_attrs.py` | PASS |

### DM

**Data Models** — Component C01 — [reference/09-data-models.md](reference/09-data-models.md)

| REQ ID | Requirement | Test File | Status |
|--------|-------------|-----------|--------|
| REQ-DM-01 | Every model referenced by another doc in this set SHALL appear here or have an explicit d... | `test_data_models.py` | PASS |
| REQ-DM-02 | Every enum SHALL list ALL values with no omissions | `test_data_models.py` | PASS |
| REQ-DM-03 | Field lists SHALL match source code (name, type, optionality) | `test_data_models.py` | PASS |
| REQ-DM-04 | Every model SHALL state its parent class and source file location | `test_data_models.py` | PASS |
| REQ-DM-05 | At least one populated `ComputationGraph` example SHALL demonstrate both `entry_point` an... | `test_data_models.py` | PASS |
| REQ-DM-06 | The delegated data models (`ComputedAttributeData`, `ExpressionRef`, `PhantomDetectionReport`) are importable from their source modules (the doc-linking / no-duplication claim is not tested) | `test_data_models.py` | PASS |
| REQ-DM-07 | Resolution-model field type annotations (`ComputationGraph`, `PipelineModule`, `ModuleInput`, `ParameterGroup`) match the documented containment hierarchy from doc 09 (no data-flow diagram is checked) | `test_data_models.py` | PASS |
| REQ-DM-08 | The typed-registry **enforced surface** SHALL use NewType wrappers: the wrappers in `identifier_types.py` are genuine `NewType`s over their bases, the four `OutputRegistry` registry dicts are annotated `dict[NewType, NewType]`, and `make_scoped_key`/`make_canonical_channel` return their NewType. (The `resolution/models.py` field annotations remain bare `str` by design — documented in 09-data-models.md and filed `[DM08-MODEL-FIELD-TYPING]`; `register_alias`'s `\| str` unions are a designed boundary, not drift) | `test_dm08_enforced_surface.py` (AST-scan — PEP-526 `self.x` annotations never reach `__annotations__`) | PASS |
| REQ-DM-09 | `ComputationGraph.output_aliases: list[OutputAlias]` SHALL be a serialized field (no `exclude`, contrast `fallback_entry_points`) carrying each EXPOSE_PURE modeler name, its canonical channel (validated to exist — INV-3), instance path, and `shape`; stable-sorted by `(instance_path, alias_name)` (INV-5) so regen yields no ordering-only diff | `test_data_models.py`, `test_graph_assembly.py` | PASS |

### DRA

**Dual Resolution Architecture** — Component X02 — [reference/24-dual-resolution-architecture.md](reference/24-dual-resolution-architecture.md)

**Status (F4 cutover LANDED, TRUTH-DEBT Item 1):** `resolve_input()` / `AGG_STRATEGIES` (`input_resolver.py`) is now the **live** aggregation SumTerm/SingletonTerm resolution path — wired through the `_build_agg_input_source()` choke point in `graph_builder._build_aggregation_module`. The channel-only `_resolve_aggregation_input_channel` and the three inline entry-point fallbacks are deleted. These parity checks compare the live path against the **backtracker DFS** (the independent comparand).

| REQ ID | Requirement | Test File | Status |
|--------|-------------|-----------|--------|
| REQ-DRA-01 | CalcUsage resolution SHALL happen during backtracker DFS; the DFS decision (recurse vs st... | `test_backtracker.py` | PASS |
| REQ-DRA-02 | FORMULA SHALL use pre-computed attribute resolution map; aggregation SumTerm/SingletonTerm resolution runs live through `resolve_input(AGG_STRATEGIES)` via `_build_agg_input_source()` (`graph_builder.py`), parity-checked against the backtracker | `test_input_resolver.py`, `test_dual_resolution.py` | PASS |
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
| REQ-EXT-07 | The `CalculationDefinitionData.output_expression_asts` field SHALL exist as `dict[str, Any]` and be nullified at the snapshot serialization boundary (raw-AST content is exercised via REQ-EXT-10's live-extraction population check, not here) | `test_extractor.py` | PASS |
| REQ-EXT-08 | A `calc def` extracting with zero output attributes SHALL raise `ValueError` at extraction (V7), never reaching generation | `test_extractor.py` | PASS |
| REQ-EXT-09 | Every `ConstraintUsage` (calc-def, part-def, part-usage owners) SHALL be reported dropped: one INFO each + one summary WARN with the model-wide total | `test_extractor.py` | PASS |
| REQ-EXT-10 | A direction-carrying `ReferenceUsage` member (named `return`, bare `in`) SHALL extract as a parameter; a named inline `return y : Real = expr` SHALL auto-implement | `test_return_style_extraction.py` | PASS |
| REQ-EXT-11 | A calc def with an anonymous `return` (empty `declared_name`) SHALL raise the V8 diagnostic before V7 | `test_return_style_extraction.py` | PASS |
| REQ-EXT-12 | The `return attribute y; y = expr` form SHALL extract `y` once with no double-ingestion (direction-None body ref excluded) | `test_return_style_extraction.py` | PASS |
| REQ-EXT-13 | `_build_part_usage_index` SHALL index each PartUsage under all its owned FeatureTyping targets and every user-model PartDef in `usage.types` (user-filtered), never by list position | `test_type_indexing.py` | PASS |
| REQ-EXT-14 | Same-named templates from a retyped usage's super/subtype (same virtual QN) SHALL keep the most-specific owner + emit V9; differently-named templates SHALL both instantiate (the collision warning fires only for same-named clashes) | `test_type_indexing.py` | PASS |

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
| REQ-GA-07 | Static: `_unified_topological_sort` source uses `deque`, `popleft()`, and Kahn-pattern identifiers (`in_degree`, `successors`); O(V + E) complexity is asserted structurally, not measured | `test_graph_assembly.py` | PASS |
| REQ-GA-08 | A two-layer params-coverage check SHALL exist: a pure collector `collect_uncovered_params(graph)` returning the wired fell-through-valueless violations (sibling to REQ-GA-03), and an always-strict generation boundary raising V11 on any violation. `ComputationGraph.fallback_entry_points` (in-memory, `exclude=True`) feeds it | `test_uncovered_params.py`, `test_graph_assembly.py`, `test_data_models.py` | PASS |

### GEN

**Generation** — Component C21 — [reference/08-generation.md](reference/08-generation.md)

| REQ ID | Requirement | Test File | Status |
|--------|-------------|-----------|--------|
| REQ-GEN-01 | Pipeline YAML generation SHALL consume only `ComputationGraph` -- no extraction models. | `test_generation_boundary.py` | PASS |
| REQ-GEN-02 | Every CalcUsage `PipelineModule` renders non-empty wrapper code in memory (no filesystem or exactly-one-file check; FORMULA/aggregation modules excluded) | `test_gen_module_wrappers.py` | PASS |
| REQ-GEN-03 | Multi-output modules (2+ outputs) SHALL get a `MultiOutput` schema in `schemas/`; single-... | `test_gen_schemas.py` | PASS |
| REQ-GEN-04 | FULLY_COMPILABLE calc defs SHALL produce auto-implemented stencils; all others SHALL prod... | `test_gen_stencils.py`, `test_generation_boundary.py` | PASS |
| REQ-GEN-05 | Each ParameterGroup SHALL produce one JSON template (`inputs/`) and one Pydantic schema (... | `test_gen_json_templates.py` | PASS |
| REQ-GEN-06 | SysML type mapping (`Real`->`float`, `Integer`->`int`, `Boolean`->`bool`, `String`->`str`... | `test_type_mapping_consolidation.py` | PASS |
| REQ-GEN-07 | Every generated module SHALL be registered in `__init__.py` for TEAx framework discovery. | `test_gen_registry.py` | PASS |

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

**Status (F4 cutover LANDED, TRUTH-DEBT Item 1):** `resolve_input()` / `AGG_STRATEGIES` (`input_resolver.py`) is now **live** — the aggregation SumTerm/SingletonTerm path calls it through `_build_agg_input_source()` in `graph_builder._build_aggregation_module`, and the LocalTerm expose-alias reroute takes its channel (D5 `module_output`-only guard). The deleted `_resolve_aggregation_input_channel` and the three inline fallbacks are gone; the cutover proved byte-identical baselines. These rows pin **live code**. Evidence: the skipif-gated `test_input_resolver.py` unit tests (incl. the surviving M3 new-side EP-key guard, the LocalTerm reroute pin, and MANUAL_REQUIRED preservation) and `test_dual_resolution.py::TestResolveInputParityExtended` (backtracker-DFS parity over Item 1's fixtures). Strategy D (`DesignAttributeLookup`) was deleted — zero live surface.

| REQ ID | Requirement | Test File | Status |
|--------|-------------|-----------|--------|
| REQ-IR-01 | `resolve_input()` SHALL always return an InputSource -- never raise on unresolved refs. | `test_input_resolver.py` | PASS |
| REQ-IR-02 | Strategies SHALL execute in declared list order; first non-None result wins. | `test_input_resolver.py` | PASS |
| REQ-IR-03 | Self-reference guard SHALL reject channels where the producing module EQN matches `ctx.mo... | `test_input_resolver.py` | PASS |
| REQ-IR-04 | ResolutionContext SHALL be immutable (`frozen=True`); no strategy mutates it. | `test_input_resolver.py` | PASS |
| REQ-IR-05 | `AGG_STRATEGIES` SHALL order `ChainRedefinitionFollow` at position 2 (after `ScopedRegistryLookup`, before `SysMLQNLookup`); the live list is `[A, C, B, E]` — `DirectChannelConstruction` (E) reproduces the SingletonTerm Try-2 channel, Strategy D deleted | `test_input_resolver.py` | PASS |
| REQ-IR-06 | Fallback SHALL produce an `entry_point` InputSource with qualified name `"{module_eqn}__{... | `test_input_resolver.py` | PASS |
| REQ-IR-07 | `resolve_input()` with `AGG_STRATEGIES` SHALL resolve a SumTerm/SingletonTerm ref to the same channel the backtracker DFS resolves it to — this is the live aggregation path (F4 cutover landed) | `test_input_resolver.py`, `test_dual_resolution.py` | PASS |

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
| REQ-MF-09 | The aggregation compile step SHALL substitute each symbolic ref with its `inputs.X` form on whole-token boundaries (`re.sub(r"\bref\b", …)`), never a plain substring `.replace()` — a ref that is a substring of another (`cost`/`cost_total`) SHALL NOT corrupt to `inputs.inputs.cost_total`; disjoint refs compile byte-identically (TRUTH-DEBT Item 6, Site 2) | `test_hygiene_tail_agg_compile.py` | PASS |

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
| REQ-PGD-06 | The deriver SHALL resolve each entry point's numeric default inline from its owning index (attr / binding / unbound / literal) via `_parse_default_value` in `_derive_from_*` | — *(no dedicated test: the numeric default is a side-output of `_derive_from_*` grouping, which REQ-PGD-01/08 pin; it is not independently asserted, and the standalone accessor that once pinned it was deleted as dead by Item 8)* | UNTESTED |
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
| REQ-PY-01 | No entry-point qualified name appears as a bare (unprefixed) source in pipeline-YAML module-input lines (the `param_group.` prefix string itself is not positively validated — blacklist coverage) | `test_gen_pipeline_yaml.py` | PASS |
| REQ-PY-02 | `InputSource.param_group` SHALL NOT be None for any entry point in the ComputationGraph | `test_gen_pipeline_yaml.py` | PASS |
| REQ-PY-03 | No pipeline-YAML module-input line declares type `"int"` (numeric-is-`"float"` verified as a blacklist, not positively; multiplicity counts not separately asserted) | `test_gen_pipeline_yaml.py` | PASS |
| REQ-PY-04 | MODULE_OUTPUT sources with `field_name == "root"` SHALL append `.root` to the channel name | `test_gen_pipeline_yaml.py` | PASS |
| REQ-PY-05 | `ModuleOutput` channel_names are unique across the graph (a rebuilt `{channel: field}` dict has one entry per output); the generated YAML `channel_field_map` is not inspected; first 2 models only | `test_gen_pipeline_yaml.py` | PASS |
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
| REQ-REG-09 | `_collect_exit_point_primitive_types` SHALL warn (not silently skip) on a single-output (`field_name="root"`) exit point whose `python_type` is outside `{float,int,str,bool}` — notably `"Any"` (latent on the current corpus, reachable live via `extractor.py:492`; TRUTH-DEBT Item 6, Site 3) | `test_hygiene_tail_registry.py` | PASS |

### RES

**Resolution Overview** — Component — — [reference/03-resolution-overview.md](reference/03-resolution-overview.md)

| REQ ID | Requirement | Test File | Status |
|--------|-------------|-----------|--------|
| REQ-RES-01 | Every ModuleInput SHALL resolve to exactly one of {`module_output`, `entry_point`}. | `test_orchestrator.py` | PASS |
| REQ-RES-02 | Three live resolution mechanisms: CalcUsage uses backtracker DFS cascade (11); FORMULA uses the pre-computed attribute resolution map (16); aggregation SumTerm/SingletonTerm uses `resolve_input(AGG_STRATEGIES)` via `_build_agg_input_source()` (`graph_builder.py`) — the F4 cutover wired it and deleted `_resolve_aggregation_input_channel` | `test_backtracker.py`, `test_computed_attributes.py`, `test_factory_aggregation.py` | PASS |
| REQ-RES-03 | Factory functions SHALL return `(PipelineModule, dict[str, EntryPoint])` -- no mutation o... | `test_factory_purity.py` | PASS |
| REQ-RES-04 | Every `module_output` reference SHALL resolve to a canonical channel in the OutputRegistr... | `test_graph_assembly.py` | PASS |
| REQ-RES-05 | The orchestrator SHALL be a linear sequence: classify -> build modules -> rebuild groups ... | `test_orchestrator.py` (`TestInnerStepOrdering` — source-order pin of `build_computation_graph`'s five internal milestones, distinct from the outer REQ-ORCH-01 pin; "rebuild groups" = `derive_groups()`) | PASS |
| REQ-RES-06 | `binding_resolutions` from the backtracker SHALL be the single source of truth for CalcUs... | `test_factory_calc_usage.py` | PASS |
| REQ-RES-07 | Resolution of scope-relative references (CHAIN `source_path`) SHALL use the consumer's pa... | `test_input_resolver.py` | PASS |
| REQ-RES-08 | Consumer-scope application SHALL hold on each live resolution path, per that path's own mechanism: backtracker base leg (`_consumer_scope_dotted`, QN `segments[1:-1]`), backtracker ancestor-scope climb (Step CLIMB, 3+-segment chains), aggregation (`ResolutionContext.consumer_scope` from the module EQN, consumed by Strategy A's primary form), and FORMULA (owner-keyed resolution map — the owner IS the consumer; no dotted scope string). Per-path application over the enumerated paths, not an exhaustiveness proof | `test_res08_consumer_scope_paths.py` (four legs, hand-authored expectations over `plant_values`/`catf_mfe`/`solar_battery`/`deep_cross_scope_probe`) | PASS |

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
| REQ-SNAP-20 | A missing load-bearing field on a deserialized dict is loud (V7): `python_type`/`binding_type`/`parent_part_path`/`owning_part_def_qn` warn and degrade to their defaults; `qualified_name` (keying) raises `SnapshotFormatError`; benign fields keep their `.get(default)` silently (TRUTH-DEBT Item 6, Site 1) | `test_hygiene_tail_loader.py` | PASS |

### SR

**Smart Regen / Preservation** — Component C23 — [reference/23-smart-regen-preservation.md](reference/23-smart-regen-preservation.md)

| REQ ID | Requirement | Test File | Status |
|--------|-------------|-----------|--------|
| REQ-SR-01 | Signature comparison SHALL use two-level matching: type-level (required) then field-level... | `test_gen_stencils.py` | PASS |
| REQ-SR-02 | Field comparison SHALL be order-independent (sorted) | `test_gen_stencils.py` | PASS |
| REQ-SR-03 | `should_regenerate_stencil()` SHALL implement the 6-case decision tree (Item 5 split the unparseable leaf: preserve-on-transient / preserve-non-empty / regenerate-empty) | `test_gen_stencils.py` | PASS |
| REQ-SR-04 | Stub upgrade SHALL require all 3 conditions: signature match, `NotImplementedError` prese... | `test_gen_stencils.py` | PASS |
| REQ-SR-05 | Backup SHALL be created before every regeneration or upgrade | `test_gen_stencils.py` | PASS |
| REQ-SR-06 | Aggregation and computed-attribute modules are synthetic and always regenerated in practi... | `test_gen_stencils.py` | PASS |
| REQ-SR-07 | Static: `_generate_stencils` source contains a `preserve_handwritten` + `output_path.exists()` branch whose body does not call `should_regenerate_stencil` (the skip behavior is not executed) | `test_gen_stencils.py` | PASS |

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

These requirements have no dedicated conformance test; each carries its argument in its matrix row above (INV-B).

- **REQ-PGD-06**: numeric default resolves inline via `_parse_default_value` (live), but as a side-output of grouping — not independently asserted; the standalone accessor was deleted by Item 8.

(TRUTH-DEBT Item 3 discharged the other three `[ITEM7-MATRIX-TEST-GAPS]` rows: REQ-DM-08
via `test_dm08_enforced_surface.py` with its text reframed to the enforced surface,
REQ-RES-05 via `TestInnerStepOrdering`, REQ-RES-08 via
`test_res08_consumer_scope_paths.py` with its text reframed to the per-path mechanisms.)

## Related Documents

- [Architecture Overview](overview.md)
- [Modeling Assumptions](modeling-assumptions.md)
- Design docs: [reference/](reference/) (28 documents)
- Conformance tests: `tests/conformance/`, `tests/unit/`, `tests/integration/` (62 distinct test files cited by matrix rows — 44 in conformance/, 18 in unit/ + integration/)
