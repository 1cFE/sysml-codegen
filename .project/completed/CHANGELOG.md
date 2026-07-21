# Changelog

Historical record of completed work.

---

## [2026-07-13] - [CONSTRAINT-EXEC] Constraint Execution and Design-Space Studies

**Type**: Epic
**Duration**: ~1 day wall-clock (created 2026-07-12; archived 2026-07-13; one ~14h orchestrated run + owner close session)

### Summary
Modeled physical limits (`assert constraint`) previously died at a drop-report warning, and every
design study re-implemented the judgment by hand. This epic makes modeled assertions execute inside
the generated forward model — Kleene-compiled graph modules feeding an exact-schema report
aggregator, verdicts as data beside ordinary outputs — and adds sealed package contracts plus a
crash-safe study layer (evaluator → store/runner → policy/query/CLI) in teax. Snapshots carry
constraint facts load-bearing (v3); `ExpressionAST` retired onto the shared `ExpressionIR`; the IFE
sweep's hand-coded viability rule is deleted, replaced by the generated assertion (2294/2301 exact,
7 model-favoring boundary rows, [OWNER] ratified).

### Deliverables
- 15 items (0–14) across four repos, each with spec/design/plan/audit + briefs; 8 item folders
  archived here, 3 in agentic-mbse, 4 in teax; fusion-tea acceptance evidence in
  `exploration/ife_e2e/study/` there.
- Independent findings audit: `20260713_epic_constraint_execution_audit_independent.md` (every
  sampled claim reproduced exactly: both mutation probes verbatim, all final gates, boundary rows
  at data level, CE-F1..F3 at source).
- Follow-ons: CE-F1 (standalone catalog emission) and CE-F2 (multi-channel CandidateBridge) in
  BACKLOG; CE-F3 fixed post-run (teax `0d606a4`).
- Gates at close: sysml-codegen 2330/23, mypy 76 baseline, ruff clean; agentic-mbse 1401/1; teax
  fully green 262.

### Lessons Learned
- Item-level certification covers what the item's fixtures exercise: the first real
  multi-entry-channel package through the certified path surfaced three integration gaps the
  single-channel toy fixture could not. An epic-level integration acceptance (real package, all
  layers) belongs in the plan, not just at the end.
- Audits that cannot execute should write "requested live probes" for the orchestrator; the
  probe-addendum + independent re-execution pattern held (both re-run probes reproduced verbatim).

---

## [2026-07-08] - [TRUTH-DEBT] Truth-Debt Retirement

**Type**: Epic
**Duration**: ~2 days (created 2026-07-06; archived 2026-07-08)

### Summary
Retired the PIPELINE-TRUTH follow-on ledger in one pass. The live aggregation path now runs
through `resolve_input(AGG_STRATEGIES)`, 3+-segment calc-usage chains resolve instead of
hard-rejecting, matrix test gaps are pinned, inherited-attr classification is fixed, and the
remaining sweep and hygiene debt is either closed or filed with named residue.

### Deliverables
- Archived item artifacts: `spec.md`, `design.md` where present, `plan.md`, `audit.md`, and
  supporting probes/impact notes for six TRUTH-DEBT items.
- Item 1: F4 aggregation-resolution cutover, Strategy D deletion, and `param_groups` typing cleanup.
- Item 2: resolved multi-hop CHAIN bindings with loud fallback diagnostics and live/offline parity.
- Item 3: REQ-DM-08, REQ-RES-05, and REQ-RES-08 test pins and matrix flips.
- Item 4: inherited-attribute classifier fix, snapshot recapture, and xfail retirement.
- Item 5: matrix sweep residue pass, EC-04/AS-06 mutation-proven strengthens, reframes, citations,
  and named overflow filing.
- Item 6: D3 hygiene-tail hardening for loader, aggregation compile, and registry warnings, plus
  site-4 reclassification.
- Pre-PR gates: 2120 passed / 4 skipped / 0 xfailed; ruff src clean; mypy src 97.

### Lessons Learned
- [TODO: Add lessons learned]

---

## [2026-02-10] - [COST-PATTERN] Item 4: Pipeline Integration -- Hierarchy-Aware Module Generation

**Type**: Epic Item (COST-PATTERN Item 4)
**Duration**: ~1 day

### Summary
Integrated hierarchy-aware extraction (Items 2-3) into the full codegen pipeline. Virtual CalcUsage binding rewriting resolves `:>>` redefinitions (LITERAL, CHAIN, design deep-path) before the backtracker runs. Aggregation modules generate from `AggregationExpressionData` with symbolic channel resolution, multiplicity entry points, and `# source: aggregation` YAML comments. Extended CLI generation layer with aggregation module wrappers, auto-implementations, registry entries, and backlog reporting.

### Deliverables
- Pipeline Step 3.5: `_extract_hierarchy_and_rewrite_bindings()` in initialization.py
- Pipeline Step 4.7: Aggregation expression storage on `PipelineContext`
- Graph builder: `_build_aggregation_module()`, `_extend_output_catalog_with_aggregation()`, symbolic channel resolution
- Backtracker: `_resolve_from_aggregation_output()` strategy (Strategy 7)
- CLI: `_generate_aggregation_modules()`, `_generate_aggregation_stencils()`, registry and backlog extensions
- Generation: `_module_to_context()` aggregation comment, `generate_registry_function()` and `generate_backlog_report()` aggregation params
- 454 tests, 0 failures (141 new tests across 4 phases)

### Lessons Learned
- Computed attribute pattern provided clean template for aggregation CLI generation
- `ScopedAggregationData` with `module_eqn` property cleanly handled ADR-003 naming
- Deriving input names from `PipelineModule` (vs regex-parsing expressions) was the cleaner approach

---

## [2026-02-09] - [ATTR-EXPR] Attribute Expression Capture

**Type**: Epic
**Duration**: ~2 days (estimated: ~6.5-8.5 days)

### Summary
Enabled SysML modelers to express computations as attribute-level expressions (`attribute volume = pi * r^2 * h`) instead of requiring full CalcDef+CalcUsage ceremony. Codegen detects computed attributes on PartDefs, classifies them via a 5-way scheme (FORMULA, EXPOSE_PURE, EXPOSE_COMPUTED, LITERAL, UNRESOLVABLE), generates synthetic pipeline modules for FORMULA patterns, and auto-implements them using the Phase 1 expression compiler.

### Deliverables
- `ComputedAttributeData` model and 5-way `ComputedAttributeClassification` enum
- `extract_computed_attributes()` extraction module (Step 4.5 in pipeline)
- Graph builder extension for FORMULA synthetic module generation
- Backtracker computed attribute awareness (FORMULA -> MODULE_OUTPUT resolution)
- 21 E2E tests validating probe fixture (9 ground-truth values) and solar_battery `p_net_kw`
- ADR-004: Computed Attribute Pipeline Integration
- ADR-005: Computed Attribute Classification
- ADR-001 clarification (computed attribute entry points)
- ADR-002 amendment (FORMULA pattern exemption, modeling guidance)
- Full test suite: 285 tests, 0 failures, 0 xfail

### Lessons Learned
- Spike de-risked the entire epic with purpose-built probe fixture
- Phase 1 expression compiler reused with zero changes
- Option C (direct graph integration) cleaner than original Option A recommendation
- Chain handling was a non-issue (biggest simplification)
- ADR migration from monorepo should have been done during repo split

---

## [2026-02-08] - [EXPR-CODEGEN] Expression-Aware Code Generation

**Type**: Epic
**Duration**: ~8.5 days

### Summary
Built expression compiler that auto-implements CalcDef output expressions as Python code. 15/15 solar_battery CalcDefs, 19/21 CATF CalcDefs auto-implemented. Eliminated the `_impl.py` handwriting bottleneck.

### Deliverables
- Expression compiler (`expression_compiler.py`)
- Auto-implementation template (`auto_implementation.py.jinja2`)
- Step 6.5 pipeline integration
- 167 tests, 0 xfail

### Lessons Learned
- CalcDef-agnostic compiler design enabled reuse in Phase 2 (ATTR-EXPR) with zero changes

---
