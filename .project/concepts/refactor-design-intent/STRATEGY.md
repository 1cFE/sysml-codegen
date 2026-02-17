# Explainer Docs Strategy

## Goal
Decompose the entire sysml-codegen pipeline into "explain like I'm a software engineer" docs.
Each doc: max 250 lines, concrete examples, full scope, data model specs.

## Document Tree (top-down decomposition)

### Tier 1: Overview (DONE)
- [x] `00-pipeline-overview.md` -- 7-step pipeline, running example, package structure

### Tier 2: Major Pipeline Stages (DONE)
- [x] `01-extraction.md` -- 4 things extracted, binding types, redefinitions, aggregation
- [x] `02-orchestration.md` -- pipeline builder, output registry, virtual bindings, agg scoping
- [x] `03-resolution-overview.md` -- the one question, current vs refactored state
- [x] `08-generation.md` -- 6 output artifacts, template system

### Tier 3: Resolution Sub-Modules (DONE)
- [x] `04-input-resolver.md` -- 5 strategies, truth table
- [x] `05-module-factory.md` -- 3 module types
- [x] `06-entry-point-classifier.md` -- 3 entry point types, grouping
- [x] `07-graph-assembly.md` -- toposort, validation, ComputationGraph

### Tier 4: Reference (DONE)
- [x] `09-data-models.md` -- all key data models

### Tier 5: Detailed Decompositions (DONE)
- [x] `10-output-registry.md` -- 4-phase lookup table, Key_A/B/C/D/E/F formats, collision policy
- [x] `11-analysis-backtracker.md` -- DFS tracing, 4-step resolution cascade, concrete walkthrough
- [x] `12-virtual-binding-rewrite.md` -- override index, 3 mutation cases, before/after example
- [x] `13-aggregation-scoping.md` -- instance discovery, scoping, CHAIN alias construction
- [x] `14-expression-compiler.md` -- 3-phase pipeline, ExpressionAST IR, compilability verdicts
- [x] `15-naming-conventions.md` -- EQN, PQN, channels, Key formats, concrete trace

### Tier 6: Gap-Fill Docs (DONE)
- [x] `16-computed-attributes.md` -- FORMULA/EXPOSE classification, compilation, alias production
- [x] `17-parameter-group-deriver.md` -- 4 indexes, grouping, filtering, classify()

### Tier 7: Code-Drift Updates (DONE)
- [x] `18-literal-value-propagation.md` -- LITERAL :>> defaults for aggregation entry points, usage_type_map, backfill
- [x] `05-module-factory.md` (updated) -- added EXPOSE_PURE alias for LocalTerms, LITERAL fallback for SumTerm/SingletonTerm

### Tier 9: Extraction Layer Decompositions
- [x] `25-hierarchy-resolver.md` -- 4-phase extraction (redefinitions, design overrides, multiplicities, aggregation), mult_lookup, alias detection, usage_type_map

### Tier 10: Migration Planning
- [x] `26-pipeline-module-migration.md` -- REQ-PIPE-07 migration: missing PipelineModule fields, 4-phase migration strategy

### Tier 8: Generation Layer Decompositions (DONE)
Gap analysis (Session 6) found the generation layer lacks detailed decompositions.
Docs 08 covers the overview but not the invariants, rules, and per-generator logic.

- [x] `19-ast-dispatch-invariant.md` -- FCE/OE subtype ordering rule, all 9+ dispatch sites, why ordering matters
- [x] `20-module-registry-generation.md` -- import path derivation, aggregation type synthesis, name collision risk
- [x] `21-pipeline-yaml-generation.md` -- channel format rules, entry point prefix, type mapping, .root extraction
- [x] `22-output-schema-rules.md` -- MultiOutput vs RootModel, Field(default=...) constraints, TEAx interaction
- [x] `23-smart-regen-preservation.md` -- FunctionSignature matching, 4-case decision tree, stub upgrade, backup
- [x] `24-dual-resolution-architecture.md` -- CalcUsage vs aggregation resolution paths, shared OutputRegistry, domain-specific strategies

## Validation Status -- ALL PHASES COMPLETE (27 docs)

### Phase A: Source Code Accuracy -- COMPLETE
All 26 docs validated. 7 issues found and FIXED (Sessions 3-4). Docs 22-23 revalidated Session 16 (0 drift). Reports:
- `validation/phase-a-docs-00-04.md`
- `validation/phase-a-docs-05-09.md`
- `validation/phase-a-docs-10-16.md`

### Phase B: SysML Syntax Validation -- COMPLETE
23 SysML code blocks validated via syside check. 1 issue found in Doc 06 (shorthand
invocation syntax) and FIXED (replaced with full body syntax). Report:
- `validation/phase-b-sysml-syntax.md`

### Phase C: Scope Completeness -- COMPLETE
11 enumerated sets cross-referenced against source code. All PASS. Report:
- `validation/phase-c-scope-completeness.md`

### Validation Matrix

| Doc | Code Accuracy | SysML Syntax | Full Scope | Data Models | Real Example |
|-----|:---:|:---:|:---:|:---:|:---:|
| 00-pipeline-overview | ok | ok | ok | ok | ok |
| 01-extraction | ok (s18) | ok | ok (s18) | ok (s18) | ok |
| 02-orchestration | ok | ok | ok | ok | ok |
| 03-resolution-overview | ok (s18) | n/a | ok (s18) | ok (s18) | ok |
| 04-input-resolver | ok (s18) | n/a | ok (s18) | ok (s18) | ok |
| 05-module-factory | ok (s18) | n/a | ok (s18) | ok (s18) | ok |
| 06-entry-point-classifier | ok (s10) | ok | ok (s10) | ok (s10) | ok |
| 07-graph-assembly | ok | n/a | ok | ok | ok |
| 08-generation | ok (s18) | n/a | ok (s18) | ok | ok |
| 09-data-models | ok (s18) | n/a | ok (s18) | ok (s18) | ok |
| 10-output-registry | ok | n/a | ok | ok | ok |
| 11-analysis-backtracker | ok | n/a | ok | ok | ok |
| 12-virtual-binding-rewrite | ok | ok | ok | ok | ok |
| 13-aggregation-scoping | ok (s18) | ok | ok (s18) | ok | ok |
| 14-expression-compiler | ok (s18) | ok | ok (s18) | ok | ok |
| 15-naming-conventions | ok | ok | ok | ok | ok |
| 16-computed-attributes | ok (s18) | ok | ok (s18) | ok (s18) | ok |
| 17-parameter-group-deriver | ok | n/a | ok | ok | ok |
| 18-literal-value-propagation | ok | ok | ok | ok | ok |
| 19-ast-dispatch-invariant | ok (s11) | n/a | ok (s11) | ok (s11) | ok (s11) |
| 20-module-registry-generation | ok (s11) | n/a | ok (s11) | ok (s11) | ok (s11) |
| 21-pipeline-yaml-generation | ok (s11) | n/a | ok (s11) | ok (s11) | ok (s11) |
| 22-output-schema-rules | ok (s15) | n/a | ok (s12) | ok (s12) | ok (s12) |
| 23-smart-regen-preservation | ok (s15) | n/a | ok (s12) | ok (s12) | ok (s12) |
| 24-dual-resolution-architecture | ok (s18) | n/a | ok (s18) | ok (s18) | ok (s10) |
| 25-hierarchy-resolver | ok (s17) | ok (s17) | ok (s17) | ok (s17) | ok (s17) |
| 26-pipeline-module-migration | ok (s18) | n/a | ok (s18) | ok (s18) | n/a |

Key: `ok` = validated, `pending` = awaiting validation, `n/a` = no SysML blocks in this doc

## Issues Found & Fixed

### Phase A (7 issues, all fixed)
1. Doc 00: Package structure showed `orchestration/` as existing
2. Doc 01: UNBOUND binding description incomplete
3. Doc 03: Binding type count wrong (4->5), combinatorial count (216->270)
4. Doc 04: InputSource shown as dataclass instead of Pydantic BaseModel
5. Doc 08: Template count wrong (13->12), table incomplete
6. Doc 09: BindingType values wrong, HierarchyExtractionResult missing field
7. Doc 16: FORMULA module_type example wrong

### Phase B (1 issue, fixed)
8. Doc 06: Shorthand calc invocation syntax replaced with full body syntax

### Phase C (0 issues)
All 11 enumerated sets pass.

## Quality Pass: Provable Design + Cross-Links (COMPLETE)

### Goal
Every doc must meet two new quality bars:
1. **Provable requirements** -- explicit REQ-XX items with verification criteria
2. **Cross-document navigation** -- Related Documents footer + inline back-links

### Format Standard

**Requirements table** (placed after the intro, before detailed explanation):
```markdown
## Requirements

| ID | Requirement | Verified by |
|----|-------------|-------------|
| REQ-EXT-01 | Extraction SHALL produce one `CalculationDefinitionData` per calc def | `len(calc_defs) == count(calc def in AST)` |
```

**Related Documents footer** (last section of every doc):
```markdown
## Related Documents
- **Upstream**: [00-pipeline-overview](00-pipeline-overview.md) -- context in pipeline
- **Downstream**: [04-input-resolver](04-input-resolver.md) -- consumes extraction output
- **Data models**: [09-data-models](09-data-models.md) -- full field definitions
```

### Progress

| Doc | Requirements | Cross-links | Status |
|-----|:---:|:---:|--------|
| 00-pipeline-overview | 7 REQ-PIPE | tables + inline | **DONE** (Session 7) |
| 01-extraction | 7 REQ-EXT | tables + footer | **DONE** (Session 7) |
| 02-orchestration | 7 REQ-ORCH | tables + footer + inline | **DONE** (Session 8) |
| 03-resolution-overview | 8 REQ-RES | tables + footer | **UPDATED** (Session 10: REQ-RES-02 corrected, structure rewritten) |
| 04-input-resolver | 7 REQ-IR | tables + footer + inline | **UPDATED** (Session 10: scope clarified for FORMULA/Agg only) |
| 05-module-factory | 8 REQ-MF | tables + footer + inline | **UPDATED** (Session 10: factory purity claim fixed) |
| 06-entry-point-classifier | 8 REQ-EPC | tables + footer + inline | **UPDATED** (Session 10: +REQ-EPC-08, Two Creation Paths section) |
| 07-graph-assembly | 7 REQ-GA | tables + footer + inline | **DONE** (Session 9) |
| 08-generation | 7 REQ-GEN | tables + footer + inline | **DONE** (Session 9) |
| 09-data-models | 7 REQ-DM | tables + footer + inline | **DONE** (Session 12: full rewrite — WHY, enums, complete fields, populated example, delegations, cross-links) |
| 10-output-registry | 7 REQ-OR | tables + footer + inline | **DONE** (Session 12) |
| 11-analysis-backtracker | 7 REQ-BT | tables + footer + inline | **DONE** (Session 13: +Step 0 scoped resolve, 5-step cascade, cross-links) |
| 12-virtual-binding-rewrite | 7 REQ-VBR | tables + footer + inline | **DONE** (Session 14) |
| 13-aggregation-scoping | 7 REQ-AS | tables + footer + inline | **DONE** (Session 14: +AggregationExpressionData missing fields fixed) |
| 14-expression-compiler | 7 REQ-EC | tables + footer + inline | **DONE** (Session 14) |
| 15-naming-conventions | 7 REQ-NC | tables + footer + inline | **DONE** (Session 15: +reserved words list expanded) |
| 16-computed-attributes | 7 REQ-CA | tables + footer + inline | **DONE** (Session 15) |
| 17-parameter-group-deriver | 7 REQ-PGD | tables + footer + inline | **DONE** (Session 15: +classify() Step 4 usage noted) |
| 18-literal-value-propagation | 7 REQ-LVP | tables + footer + inline | **DONE** (Session 15: +line drift fixes) |
| 19-ast-dispatch-invariant | 7 REQ-AST | footer + inline | **DONE** (Session 11) |
| 20-module-registry-generation | 7 REQ-REG | footer + inline | **DONE** (Session 11) |
| 21-pipeline-yaml-generation | 7 REQ-PY | footer + inline | **DONE** (Session 11) |
| 22-output-schema-rules | 7 REQ-OSR | tables + footer + inline | **DONE** (Session 12) |
| 23-smart-regen-preservation | 7 REQ-SR | tables + footer + inline | **DONE** (Session 12) |
| 24-dual-resolution-architecture | 5 REQ-DRA | tables + footer + inline | **DONE** (Session 10: full rewrite with requirements) |

| 25-hierarchy-resolver | 7 REQ-HR | tables + footer + inline | **DONE** (Session 17) |

## Session 10: Design Logic Bugs

### Findings (verified against source code)

**Bug 1: "Unified resolver" structurally impossible for CalcUsage (CRITICAL)**
- Docs 03/04 claim `resolve_input()` replaces ALL resolution paths
- Source code reality: the backtracker's DFS (`_trace_dependencies`) calls `_resolve_binding_via_registry()` during traversal (line 364 of dependency_backtracker.py). It MUST resolve bindings to decide whether to recurse (MODULE_OUTPUT → recurse) or stop (ENTRY_POINT → stop).
- CalcUsage resolution CANNOT move to `resolve_input()` — DFS traversal structurally requires it
- The "unified resolver" can only unify FORMULA and aggregation resolution
- The backtracker already has scoped resolution (Step 0, line 512-519: consumer_scope + source_path → Key_C)
- Doc 24 documents dual resolution as-is, but contradicts docs 03/04's "unified" claim
- **Impact**: Anyone implementing from docs 03/04 will hit a structural impossibility

**Bug 2: Factory entry points hardcoded to DESIGN_ATTRIBUTE (MEDIUM)**
- `_classify_entry_points()` runs FIRST (Step 4 in code, line 120) with 3-strategy classification
- FORMULA modules (Step 6.5) create entry points hardcoded to `DESIGN_ATTRIBUTE` (line 721)
- Aggregation modules (Step 6.7) create entry points hardcoded to `DESIGN_ATTRIBUTE` (lines 993, 1028, 1105, 1174)
- These are NEVER re-classified — only re-grouped (Step 6.6 rebuilds param_groups)
- This is undocumented. Could be wrong for some cases (e.g., aggregation fallback that should be USAGE_LITERAL)
- Doc 06 doesn't document this split. Doc 05 doesn't mention entry_type assignment.

**Bug 3: Doc 00 step ordering contradicts code (LOW)**
- Doc 00: Step 3 (resolve) → Step 4 (build) → Step 5 (classify) → Step 6 (sort)
- Actual code: Step 4 (classify) → Step 5 (group) → Step 6 (build CalcUsage) → Step 6.5 (build FORMULA) → Step 6.7 (build aggregation) → Step 7 (sort)
- Doc 03 pseudocode shows classify-then-build (matching code) but Doc 00 shows build-then-classify

### Fix Plan (this session: 2-3 docs)

**Fix 1: Doc 03 — Honest about what's unified** ← DOING
- Replace "Thin Orchestrator" pseudocode with accurate design that acknowledges DFS constraint
- CalcUsage: backtracker resolves bindings during DFS (stays as-is)
- FORMULA + Aggregation: factories call resolve_input() (the actual unification)
- Rename from "unified" to "consolidated" — it consolidates 3→2 resolution paths, not 3→1
- Add explicit section: "Why CalcUsage resolution stays in the backtracker"

**Fix 2: Doc 24 — Reconcile with docs 03/04** ← DOING
- Position as the DESIGN RATIONALE for why dual resolution is architecturally necessary
- Add section: "How the refactored design handles this" — backtracker does CalcUsage, resolve_input() does FORMULA/aggregation
- Cross-link to doc 03 (which now honestly describes the constraint)
- Remove the current framing that treats dual resolution as accidental/legacy

**Fix 3: Doc 06 — Document two EP creation paths** ← DOING
- Add section: "Two Entry Point Creation Paths"
- Path 1: Backtracker → _classify_entry_points() → 3-strategy classification
- Path 2: Factory fallback → hardcoded DESIGN_ATTRIBUTE
- Document WHY factory EPs are hardcoded (they don't have binding context for 3-strategy classification)
- Add REQ-EPC-08: factory-created entry points SHALL have entry_type=DESIGN_ATTRIBUTE

### Deferred items (resolved)
- ~~Doc 00 step ordering fix (Bug 3)~~ — **FIXED Session 13**
- ~~Doc 05 "pure data transformer" claim~~ — **FIXED Session 10** (replaced with "Structured Resolution" table)

## Remaining Work

### Cross-Cutting Concerns Not Yet Documented (FUTURE, low priority)
- [ ] Error handling: what happens when resolution fails, what the warnings mean
- [ ] The 270-combination matrix: which combinations are actually reachable

### Gap Analysis: E2E Post-Codegen Validation (Session 6)
Phase 5 of fusion-tea e2e validation found 4 bugs (8-11) exposing documentation gaps:
- Bug 8: `__init__.py` wrong import paths + name collisions for aggregation modules → **Doc 20**
- Bug 9: Missing `system_design.` prefix on entry point channels in pipeline.yaml → **Doc 21**
- Bug 10: `int` type for multiplicity counts (TEAx expects all `float`) → **Doc 21**
- Bug 11: `default=0.0` on MultiOutput fields breaks TEAx output detection → **Doc 22**
- FCE/OE ordering as system invariant (not just expression compiler) → **Doc 19**
- Smart-regen overwrites manual Bug 9/10/11 workarounds → **Doc 23**
- Dual resolution architecture undocumented → **Doc 24**

### Code Drift Items Identified in Session 5
Commits `b626c59` (literal value propagation) and `b424c75` (bug fixes) added:
- `_find_literal_redefinition()` -- new function in graph_builder.py
- `expose_aliases` map (Step 6.6b) -- EXPOSE_PURE alias for LocalTerm resolution
- `usage_type_map` on HierarchyExtractionResult -- type-aware PartDef QN resolution
- Entry point default backfill -- updates existing EPs with literal defaults
- Doc 09 was already accurate (usage_type_map field documented)
- Doc 05 needed updates (aggregation term resolution strategies)

## Session Log
- Session 1: Created 00-09 (first pass from research doc)
- Session 2: Created strategy, wrote 10-15 (first pass decompositions)
- Session 3: Ran validation Phase A on all docs. Created 16-17 gap-fill docs. All 3 Phase A reports complete. Phase B (SysML syntax) also completed via syside check.
- Session 4: Fixed all 7 Phase A issues + 1 Phase B issue. Completed Phase C (scope completeness). ALL VALIDATION COMPLETE. 18 docs, all passing all checks.
- Session 5: Code drift analysis. Commits b626c59/b424c75 added LITERAL value propagation, EXPOSE_PURE LocalTerm resolution, usage_type_map. Created doc 18 (literal-value-propagation). Updated doc 05 (module factory) with new aggregation behaviors.
- Session 6: E2E gap analysis against Phase 5 bugs (8-11). 6 research agents completed. Wrote docs 19-24 (Tier 8: generation layer decompositions). All 6 docs cover: AST dispatch invariant, registry generation, pipeline YAML, output schemas, smart-regen, dual resolution. Validation pending.
- Session 7: Quality pass -- provable requirements + cross-links. Rewrote docs 00, 01, 03 with: (a) requirements tables (7+7+6 = 20 REQ-XX items with verification criteria), (b) Related Documents footers with upstream/downstream/data-model links, (c) inline cross-links throughout. Established the format standard for remaining 15 docs. Line counts: 00=172, 01=163, 03=171 (all under 250 limit). Next session should target docs 02, 04, 05 (orchestration, input resolver, module factory).
- Session 8a: Quality pass continued -- docs 02, 04, 05 upgraded with requirements tables + cross-links (7 REQ-ORCH + 7 REQ-IR + 8 REQ-MF = 22 new requirements).
- Session 8b: **DESIGN FIX -- The Scope Problem.** Review found critical design flaw: CHAIN binding `source_path` from extraction is scope-relative (e.g. `"cost_model.total_cost"`) but registry is a flat global namespace. Unscoped lookup (Key_A) silently miswires when instance names collide across scopes. Fix: (1) Doc 03 -- added "The Scope Problem" section + REQ-RES-07 (scoped before unscoped) + REQ-RES-08 (consumer_scope for all module types). (2) Doc 04 -- reordered strategies C before A in both STANDARD_STRATEGIES and AGG_STRATEGIES; added `consumer_scope` field to ResolutionContext; rewrote Strategy C description with WHY; updated truth table to show scoped CHAIN binding resolution. (3) Doc 00 -- Key_C marked as critical key, linked to Scope Problem. (4) Doc 02 -- registry section links to Scope Problem, Key_C marked as critical. This is the most important design decision in the resolution layer.
- Session 9: Quality pass continued -- docs 06, 07, 08 upgraded. (a) Requirements tables: 7 REQ-EPC + 7 REQ-GA + 7 REQ-GEN = 21 new requirements (63 total across 9 docs). (b) Related Documents footers with categorized links (upstream/downstream/sub-processes/registry/data-models). (c) Inline cross-links throughout (data model refs, related doc refs). (d) Source code verified via 3 parallel Explore agents against graph_builder.py, models.py, generation/*.py. Key corrections: doc 06 index name fixed (design_attr_by_qname), python_type field added to EntryPoint discussion; doc 07 CircularDependencyError origin documented (analysis/dependency_backtracker.py); doc 08 REQ-GEN-06 documents 4-copy _map_input_type() duplication as known violation. Line counts: 06=233, 07=245, 08=218 (all under 250). Next session should target docs 09, 10, 11 (data-models, output-registry, analysis-backtracker).
- Session 10: **DESIGN LOGIC BUGS -- 4 bugs found, 3 fixed.** Source code verified via 2 Explore agents against graph_builder.py (1418 lines) and dependency_backtracker.py.
  - **Bug 1 (CRITICAL): "Unified resolver" claim was structurally impossible.** The backtracker's DFS calls `_resolve_binding_via_registry()` during traversal (line 364) to decide recurse vs stop. CalcUsage resolution CANNOT move to `resolve_input()`. Fix: (a) Doc 03 rewritten — renamed "Thin Orchestrator" to "Consolidated Resolution", added "Why CalcUsage Resolution Stays in the Backtracker" section, fixed REQ-RES-02 to honestly state CalcUsage uses backtracker while FORMULA/Agg use resolve_input(), fixed pseudocode. (b) Doc 24 rewritten — repositioned as "Why Resolution Has Two Paths (and Must Stay That Way)", added structural constraint explanation, added 5 REQ-DRA requirements, strategy overlap table, corrected "scoped key construction: No" error for CalcUsage (backtracker DOES have Step 0 scoped lookup). (c) Doc 04 title changed from "Unified" to "Consolidated", opening rewritten to clarify scope (FORMULA/Agg only), REQ-IR-07 updated, "What this eliminates" section corrected.
  - **Bug 2 (MEDIUM): Factory entry points hardcoded to DESIGN_ATTRIBUTE — undocumented.** Fix: Doc 06 — added REQ-EPC-08, added "Two Entry Point Creation Paths" section documenting Path 1 (backtracker → 3-strategy classification) and Path 2 (factory → hardcoded DESIGN_ATTRIBUTE), explained WHY (factory EPs lack binding context). Doc 05 — fixed "pure data transformer" claim, replaced with "Structured Resolution" table showing which factory types receive pre-resolved data vs call resolve_input().
  - **Bug 3 (LOW): Doc 00 step ordering contradicts code.** Deferred to next session.
  - **Bug 4 (in Bug 1): Doc 24 strategy table error.** CalcUsage row said "Scoped key construction: No" but backtracker has Step 0 scoped lookup (line 512). Fixed in rewrite.
  - Line counts: 03=217, 04=251, 05=236, 06=239, 24=172 (04 is 1 line over, acceptable).
  - Next session: (a) Fix Doc 00 step ordering (Bug 3), (b) continue quality pass on docs 09-11 (requirements + cross-links).
- Session 11: **Phase 5 Bug Traceability — Docs 19, 20, 21 upgraded.** Focus: make design verifiably address Bugs 8-10 from fusion-tea Phase 5 validation.
  - **Doc 19 (AST dispatch invariant)**: Added 7 REQ-AST requirements tracing to Bug A (commit 20b720e). Verified all 8 dispatch sites via Explore agent. Condensed site listings into summary tables. Added before/after concrete example showing SingletonTerm vs LocalTerm misclassification. Added Related Documents footer with links to docs 13, 14, 10, 05, 00, 09. Line count: 149.
  - **Doc 20 (module registry generation)**: Added 7 REQ-REG requirements tracing to Bug 8 (import paths + name collisions). Verified via Explore agent that registry.py:126 uses library `owning_part_qn` while CLI uses design-scoped `module_eqn` — root cause confirmed. Added concrete correct vs buggy path example. Added name collision scenario with 5 class names across 4 assemblies. Added Related Documents footer. Line count: 172.
  - **Doc 21 (pipeline YAML generation)**: Added 7 REQ-PY requirements tracing to Bug 9 (param_group prefix) and Bug 10 (int→float). Verified via Explore agent that pipeline.py:168-171 is the Bug 9 fix site and graph_builder.py:1039 is the Bug 10 fix site. Updated type mapping table with REQ-PY-03 compliance column. Added param_group explanation with 3 group names. Added Related Documents footer. Line count: 219.
  - **Totals**: 21 new requirements (84 cumulative across 12 docs). All 3 docs verified against source code via parallel Explore agents. All under 250 line limit.
  - Next session: (a) Docs 22-23 quality pass (Bug 11 + smart-regen), (b) continue docs 09-11 sequential quality pass, or (c) fix Doc 00 step ordering (deferred Bug 3).
- Session 12: **Quality pass — Docs 10, 22, 23 upgraded.** All 3 verified against source code via parallel Explore agents before editing.
  - **Doc 10 (output-registry)**: Added 7 REQ-OR requirements. Added inline cross-links to naming conventions (doc 15), scope problem (doc 03), input resolver (doc 04), module factory (doc 05). Added Related Documents footer with 8 categorized links (upstream, downstream, sub-processes, naming, data models). Verified all 12 claims against source — perfect accuracy. Line count: 241.
  - **Doc 22 (output-schema-rules)**: Added 7 REQ-OSR requirements tracing to Bug 11 (default=0.0 breaks TEAx output detection). Fixed type mapping table: added `ScalarValues::` prefixed variants and `float` default fallback. Clarified `primitives.py` is a generated file (written by `cli/__init__.py:120-134`), not in source control. Added inline cross-links to extraction (doc 01), naming (doc 15), output registry (doc 10). Added Related Documents footer. Line count: 186.
  - **Doc 23 (smart-regen-preservation)**: Added 7 REQ-SR requirements. Fixed `generate_expected_signature()` code example: added missing 0-output case (`return_type = "None"`) verified at `signature_extractor.py:222-229`. Added inline cross-links to data models (doc 09), aggregation scoping (doc 13), computed attributes (doc 16). Added Related Documents footer. Line count: 216.
  - **Totals**: 21 new requirements (105 cumulative across 15 docs). 1 code accuracy fix (doc 23: missing 0-output case). 1 completeness fix (doc 22: ScalarValues:: prefixes). All under 250 line limit.
  - Next session: (a) Continue sequential quality pass on docs 09, 11 (data-models, analysis-backtracker), (b) fix Doc 00 step ordering (deferred Bug 3), (c) continue docs 12-18.
- Session 13: **Quality pass + Bug 3 fix — Docs 09, 11, 00 updated.** All 3 verified against source code via parallel Explore agents before editing.
  - **Doc 09 (data-models)**: Fixed BindingInfo field drift — added missing `source_instance_elem` and `source_attribute_elem` fields. Strategy table was already showing DONE (Session 12) but the BindingInfo omission was caught by verification. Line count: 250.
  - **Doc 11 (analysis-backtracker)**: Full quality pass. Added 7 REQ-BT requirements. **Critical fix: added missing Step 0 (scoped resolve)** — the PRIMARY resolution path for CHAIN bindings (prepends consumer_scope to source_path for Key_C match). Renamed from "4-Step" to "5-Step Resolution Cascade". Added Related Documents footer with 5 categories (upstream, architecture, downstream, cross-cutting, data models). Added inline cross-links to docs 03, 04, 06, 09, 10, 11, 12, 15, 24. Updated walkthrough to show Step 0 → Step 1 cascade. Line count: 218.
  - **Doc 00 (pipeline-overview): Bug 3 FIXED.** Reordered Steps 3-6 to match actual code execution order:
    - Step 3: "Trace deps" (was "Resolve inputs") — backtracker DFS + CalcUsage binding resolution → links docs 11, 03, 24
    - Step 4: "Classify entries" (was Step 5) — happens BEFORE module building inside build_computation_graph()
    - Step 5: "Build modules" (was Step 4) — includes FORMULA/Agg resolution via consolidated resolver → links docs 05, 04, 13, 16
    - Step 6: "Sort modules" (unchanged)
    Updated package structure to show analysis/ as Step 3, resolution/ as Steps 4-6. Fixed Key_C reference from "resolver" to "backtracker". Line count: 193.
  - **Totals**: 7 new requirements (112 cumulative across 16 docs). 1 critical doc fix (Step 0 in backtracker). 1 deferred bug fixed (Bug 3). All under 250 line limit.
  - Next session: Continue quality pass on docs 12-15 (virtual-binding-rewrite, aggregation-scoping, expression-compiler, naming-conventions).
- Session 14: **Quality pass — Docs 12, 13, 14 upgraded.** All 3 verified against source code via parallel Explore agents before editing.
  - **Doc 12 (virtual-binding-rewrite)**: Added 7 REQ-VBR requirements. Added inline cross-links to docs 00, 06, 07, 09, 10, 11, 13, 17, 18, 24. Added Related Documents footer with 5 categories (upstream, architecture, downstream, cross-cutting, data models). All 13 source code claims verified — perfect accuracy. Line count: 190.
  - **Doc 13 (aggregation-scoping)**: Added 7 REQ-AS requirements. **Fixed DRIFT: `AggregationExpressionData` data model section was missing 8 fields** (`owning_part_name`, `raw_expression_text`, `transformed_expression`, `entry_points`, `compilability`, `has_unsupported_nodes`, `source_file`, `source_line`). Added inline cross-links to docs 00, 04, 05, 06, 09, 10, 14, 15, 24. Added Related Documents footer. Line count: 203.
  - **Doc 14 (expression-compiler)**: Added 7 REQ-EC requirements. Added inline cross-links to docs 01, 05, 08, 09, 16, 19, 22, 23. Added Related Documents footer. All 14 source code claims verified — perfect accuracy. Line count: 208.
  - **Totals**: 21 new requirements (133 cumulative across 19 docs). 1 data model completeness fix (doc 13: AggregationExpressionData missing fields). All under 250 line limit.
  - Next session: Continue quality pass on docs 15-17 (naming-conventions, computed-attributes, parameter-group-deriver).
- Session 15: **Quality pass — Docs 15, 16, 17 upgraded.** All 3 verified against source code via parallel Explore agents before editing.
  - **Doc 15 (naming-conventions)**: Added 7 REQ-NC requirements. Expanded `sanitize_name()` reserved words to list all 6 words (`class`, `def`, `import`, `from`, `return`, `yield`). Added inline cross-links to docs 01, 03, 04, 05, 06, 09, 10, 12, 16. Added Related Documents footer with 13 categorized links. All claims verified — perfect accuracy. Line count: 226.
  - **Doc 16 (computed-attributes)**: Added 7 REQ-CA requirements. Added inline cross-links to docs 00, 05, 06, 09, 10, 14, 15, 19, 22, 23. Added Related Documents footer with 6 categories. All 12 major claims verified — perfect accuracy. Minor note: `ComputedAttributeData` has 2 additional undocumented fields (`source_file`, `source_line`) — metadata, not core functionality. Line count: 249.
  - **Doc 17 (parameter-group-deriver)**: Added 7 REQ-PGD requirements. **Fixed: `classify()` usage scope** — doc previously said "called during Steps 6.5–6.7" but it's also called at Step 4 for initial classification. Updated description to note both usages. Added inline cross-links to docs 01, 02, 05, 06, 07, 09, 13, 16, 18, 21, 22. Added Related Documents footer with 11 categorized links. All 18 claims verified — perfect accuracy. Line count: 211.
  - **Totals**: 21 new requirements (154 cumulative across 22 docs). 1 minor accuracy fix (doc 17: classify() Step 4 usage). 1 completeness fix (doc 15: reserved words). All under 250 line limit.
  - Next session: Final quality pass on doc 18 (literal-value-propagation) — the LAST remaining doc. After that, all 25 docs will have requirements + cross-links.
- Session 16: **Final quality pass + revalidation — Doc 18 upgraded, Docs 22-23 revalidated.** All docs verified against source code via parallel Explore agents.
  - **Docs 22-23 Phase A revalidation**: Ran fresh source code accuracy checks. Doc 22: 7/7 claims PASS (schemas.py, graph_builder.py, templates all match). Doc 23: 9/9 claims PASS (signature_extractor.py, preservation.py, cli/__init__.py all match). No drift since Session 12.
  - **Doc 15 (naming-conventions)**: Reverified — 11/11 claims PASS. Already had requirements + Related Documents.
  - **Doc 16 (computed-attributes)**: Reverified — 11/11 claims PASS. Already had requirements + Related Documents.
  - **Doc 17 (parameter-group-deriver)**: Reverified — 10/10 claims PASS. Already had requirements + Related Documents.
  - **Doc 18 (literal-value-propagation)**: Added 7 REQ-LVP requirements. Added Related Documents footer (8 links). **Fixed 2 line number drifts**: SumTerm fallback line 974→975, SingletonTerm fallback line 1081→1087. All 10 claims verified — no logic errors. Line count: 208.
  - **Totals**: 7 new requirements (161 cumulative across all 25 docs). 2 line drift fixes. All under 250 line limit.
  - **QUALITY PASS COMPLETE**: All 25 docs now have requirements tables + Related Documents footers + inline cross-links. 161 total requirements across 25 docs. (Session 18 added 8 more: 169 total across 27 docs.)
- Session 17: **Gap fill + drift audit — Doc 25 created, Docs 09/10 fixed.**
  - **Code drift audit**: Ran 2 parallel Explore agents against OutputRegistry refactor (commits Feb 13-15). Result: NO MAJOR DRIFT. The OutputRegistry API, 4-phase protocol, and all doc claims remain accurate. One minor gap: `canonical_channels` property (used by graph_builder for membership checks) was undocumented.
  - **Hierarchy resolver gap analysis**: Ran parallel Explore agent against `hierarchy_resolver.py` (572 lines). Found only ~55-60% coverage across 5 scattered docs. No dedicated doc existed for this module.
  - **Doc 25 (hierarchy-resolver)**: Created new dedicated doc. Covers: 4 extraction phases (redefinitions, design overrides, multiplicities, aggregation), deep-path detection, SysIDE lower-bound convention, mult_lookup mechanism, AST walking dispatch order, alias detection logic, usage_type_map extraction. Added 7 REQ-HR requirements. Validated via Explore agent: 19/20 claims ACCURATE, 1 minor fix (added "evaluate" to wrapper list). Line count: 233.
  - **Doc 10 (output-registry)**: Added `canonical_channels` property to API table. Line count: 242.
  - **Doc 09 (data-models)**: Added `canonical_channels` property to OutputRegistry description. Added cross-link to doc 25. Line count: 251.
  - **Doc 01 (extraction)**: Added cross-link to doc 25 in Section 4 and Related Documents footer. Line count: 165.
  - **Totals**: 7 new requirements (168 cumulative across 26 docs). 1 new doc created. 3 docs updated with cross-links/drift fixes. All under 250 line limit (doc 09 at 251, same tolerance as doc 04).
  - Next session: Consider documenting `expression_utils.py` (201 lines, shared AST utilities) or addressing remaining cross-cutting concerns (error handling, 270-combination matrix).
- Session 18: **Quality review fix pass — 12 issues across 15 files.**
  - **Issue 10 (Doc 01)**: Fixed UNBOUND binding storage claim — `unbound_params` are string names only, NOT in the `bindings` list as BindingInfo objects.
  - **Issue 11 (Doc 16)**: Fixed QN separator inconsistency — `ChannelAlias.owning_part_qn` uses `__` (codegen format), not `::` (raw SysML).
  - **Issue 12 (Docs 03, 24)**: Fixed cascade stage count — "4-stage cascade" → "5-step resolution cascade" in doc 03; added clarifying note in doc 24 that stages 0-3 are resolution steps, stage 4 is guaranteed fallback.
  - **Issue 3 (Docs 09, 01)**: Added `AggregationExpressionData` (15 fields) and `ScopedAggregationData` to doc 09. Added ComputedAttributeData reference note to doc 01. Reclaimed lines by condensing PipelineContext and concrete example.
  - **Issue 2 (Docs 03, 04, 05)**: Fixed FORMULA resolution path — FORMULA uses pre-computed attribute resolution map, NOT `resolve_input()`. Updated REQ-RES-02 to honestly state 3 resolution mechanisms. Removed FORMULA from doc 04 scope. Updated doc 05 summary table.
  - **Issue 4 (Doc 04)**: Added `consumer_scope` clarification for aggregation modules (always 3+ EQN segments).
  - **Issue 5 (Doc 03)**: Added EXPRESSION binding note — `source_path=None` bindings intentionally skipped during DFS (expression AST is the source).
  - **Issue 6 (Doc 13)**: Added zero-instance aggregation edge case + REQ-AS-08 (WARNING on zero scoped modules).
  - **Issue 7 (Doc 16)**: Added FORMULA-to-FORMULA dependency limitation + REQ-CA-08 (`output_names=set()` prevents cross-FORMULA references).
  - **Issue 8 (Doc 14)**: Added "Two AST Processing Pipelines" comparison table (expression compiler vs aggregation walker).
  - **Issue 1 (Doc 26)**: Created new doc 26 (PipelineModule migration) with REQ-PMM-01 through REQ-PMM-05. Updated docs 00 and 08 with cross-references.
  - **Issue 9 (Doc 08)**: Added template context variable summaries for 3 key generators.
  - **Tracking docs**: Updated COMPONENT_CHECKLIST (C01 +AggregationExpressionData/ScopedAggregationData, C10 +REQ-AS-08, C12 scope narrowed, C15 attr resolution map, C16 +LocalTerm AC, C26 new, X02 updated to 3-path). Updated IMPLEMENTATION_PLAN (Phase 4.2 attr map, Phase 7.5 PipelineModule expansion, Risk 6 FORMULA map assumption).
  - **Totals**: 12 issues fixed. 1 new doc (26). 15 files modified. 8 new requirements (REQ-AS-08, REQ-CA-08, REQ-PMM-01 through REQ-PMM-05, REQ-IR-07 updated). All docs under 250 line limit.
