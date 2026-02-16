# Explainer Docs Strategy

## Goal
Decompose the entire sysml-codegen pipeline into "explain like I'm a software engineer" docs.
Each doc: max 200 lines, concrete examples, full scope, data model specs.

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

### Tier 8: Generation Layer Decompositions (IN PROGRESS)
Gap analysis (Session 6) found the generation layer lacks detailed decompositions.
Docs 08 covers the overview but not the invariants, rules, and per-generator logic.

- [ ] `19-ast-dispatch-invariant.md` -- FCE/OE subtype ordering rule, all 9+ dispatch sites, why ordering matters
- [ ] `20-module-registry-generation.md` -- import path derivation, aggregation type synthesis, name collision risk
- [ ] `21-pipeline-yaml-generation.md` -- channel format rules, entry point prefix, type mapping, .root extraction
- [ ] `22-output-schema-rules.md` -- MultiOutput vs RootModel, Field(default=...) constraints, TEAx interaction
- [ ] `23-smart-regen-preservation.md` -- FunctionSignature matching, 4-case decision tree, stub upgrade, backup
- [ ] `24-dual-resolution-architecture.md` -- CalcUsage vs aggregation resolution paths, shared OutputRegistry, domain-specific strategies

## Validation Status -- ALL PHASES COMPLETE

### Phase A: Source Code Accuracy -- COMPLETE
All 18 docs validated. 7 issues found and FIXED. Reports:
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
| 01-extraction | ok | ok | ok | ok | ok |
| 02-orchestration | ok | ok | ok | ok | ok |
| 03-resolution-overview | ok | n/a | ok | ok | ok |
| 04-input-resolver | ok | n/a | ok | ok | ok |
| 05-module-factory | ok | n/a | ok | ok | ok |
| 06-entry-point-classifier | ok | ok | ok | ok | ok |
| 07-graph-assembly | ok | n/a | ok | ok | ok |
| 08-generation | ok | n/a | ok | ok | ok |
| 09-data-models | ok | n/a | ok | ok | ok |
| 10-output-registry | ok | n/a | ok | ok | ok |
| 11-analysis-backtracker | ok | n/a | ok | ok | ok |
| 12-virtual-binding-rewrite | ok | ok | ok | ok | ok |
| 13-aggregation-scoping | ok | ok | ok | ok | ok |
| 14-expression-compiler | ok | ok | ok | ok | ok |
| 15-naming-conventions | ok | ok | ok | ok | ok |
| 16-computed-attributes | ok | ok | ok | ok | ok |
| 17-parameter-group-deriver | ok | n/a | ok | ok | ok |
| 18-literal-value-propagation | ok | ok | ok | ok | ok |
| 19-ast-dispatch-invariant | pending | n/a | pending | pending | pending |
| 20-module-registry-generation | pending | n/a | pending | pending | pending |
| 21-pipeline-yaml-generation | pending | n/a | pending | pending | pending |
| 22-output-schema-rules | pending | n/a | pending | pending | pending |
| 23-smart-regen-preservation | pending | n/a | pending | pending | pending |
| 24-dual-resolution-architecture | pending | n/a | pending | pending | pending |

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

## Quality Pass: Provable Design + Cross-Links (IN PROGRESS)

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
| 00-pipeline-overview | pending | partial | **Session 7 target** |
| 01-extraction | pending | none | **Session 7 target** |
| 02-orchestration | pending | none | queued |
| 03-resolution-overview | pending | none | **Session 7 target** |
| 04-input-resolver | pending | none | queued |
| 05-module-factory | pending | none | queued |
| 06-entry-point-classifier | pending | none | queued |
| 07-graph-assembly | pending | none | queued |
| 08-generation | pending | none | queued |
| 09-data-models | pending | none | queued |
| 10-output-registry | pending | none | queued |
| 11-analysis-backtracker | pending | none | queued |
| 12-virtual-binding-rewrite | pending | none | queued |
| 13-aggregation-scoping | pending | none | queued |
| 14-expression-compiler | pending | none | queued |
| 15-naming-conventions | pending | none | queued |
| 16-computed-attributes | pending | none | queued |
| 17-parameter-group-deriver | pending | none | queued |
| 18-literal-value-propagation | pending | none | queued |

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
- Session 6: E2E gap analysis against Phase 5 bugs (8-11). 6 research agents completed: registry gen, pipeline YAML gen, smart-regen, AST dispatch, output schemas, dual resolution. Updated STRATEGY.md with Tier 8 plan (docs 19-24). Writing docs 19-24.
- Session 7: Quality pass -- provable requirements + cross-links. Targeting docs 00, 01, 03 to establish the pattern. Added quality pass framework to STRATEGY.md.
