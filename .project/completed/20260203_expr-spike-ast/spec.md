# Spec: Spike -- SysIDE Expression AST Extraction & Reference Resolution

**Status:** Draft
**Owner:** Reid Westwood
**Created:** 2026-02-03
**Complexity:** MEDIUM
**Branch:** cost-pattern
**Epic:** EXPR-CODEGEN Item 1

---

## Business Goals

### Why This Matters

The expression-aware codegen effort aims to eliminate `NotImplementedError` stubs
by auto-generating `_impl.py` files with real computation code. The entire effort
rests on two unvalidated assumptions about SysIDE's AST:

1. CalcDef output attributes expose their expression ASTs via `feature_value_expression`
2. All feature references within those expressions resolve to declared inputs or sibling outputs

If either assumption fails, the compiler design in the concept doc must be revised
before any implementation begins. This spike answers both questions with data from
real models.

### Success Criteria

- [ ] Q1 script runs on chain_spike, sample_model, and solar_battery models without errors
- [ ] >80% of CalcDef output attributes have extractable expression ASTs
- [ ] Complete inventory of all AST node types encountered across all models
- [ ] Q2 script confirms 100% of feature references resolve to input or intermediate (or documents every exception)
- [ ] Go/no-go recommendation documented with evidence

### Priority

P1 -- gates all subsequent items in the Expression-Aware Codegen epic. Items 2-5
are blocked until this spike produces a go recommendation.

---

## Problem Statement

### Current State

- `extractor.py:156` accesses `member.feature_value_expression` and calls
  `_extract_expression_text()`, which produces raw text strings stored in
  `calc_expressions: list[str]` on `CalculationDefinitionData`
- `_extract_expression_text()` (extractor.py:612-634) handles only
  `OperatorExpression` and `FeatureReferenceExpression`; everything else
  returns `"???"`
- The raw AST nodes are discarded after text extraction -- they are not
  preserved for downstream use
- `constraint_extractor._reconstruct_expression()` (constraint_extractor.py:137-257)
  is a more complete AST walker handling literals, chains, booleans, and
  multi-operand expressions, but it is not used for CalcDef extraction
- `agentic_mbse.sysml.expression.extract_feature_refs()` can extract
  feature references from expression ASTs but has never been run against
  CalcDef output expressions specifically
- We do not know: what percentage of CalcDef outputs have ASTs, what node
  types appear in practice, or whether all references are resolvable

### Desired Outcome

Empirical answers to two questions, validated against three model suites
(chain_spike, sample_model, solar_battery), with a clear go/no-go
recommendation for proceeding to the expression compiler.

---

## Scope

### In Scope

**Question 1 (Q1): Can we extract expression ASTs for all CalcDef outputs?**

For each CalcDef in each model suite, for each output attribute:
- Does `feature_value_expression` exist and is it non-None?
- What is the AST root node's type name?
- What is the maximum traversal depth?
- What distinct AST node types appear across the full traversal?
- Are there any node types not in the expected set?

Expected node types (from concept doc Section 5 and constraint_extractor):
`OperatorExpression`, `FeatureReferenceExpression`, `FeatureChainExpression`,
`LiteralRational`, `LiteralInteger`, `LiteralReal`, `LiteralBoolean`.

**Question 2 (Q2): Do all feature references resolve to inputs or intermediates?**

For each CalcDef with extractable ASTs, for each output attribute:
- Extract all `FeatureReferenceExpression` nodes from the expression
- For each ref, check: is `ref.name` in the CalcDef's `input_attributes`?
- If not: is `ref.name` in the CalcDef's `output_attributes` (intermediate)?
- If neither: flag as unresolvable, record the name and context

**Test Fixtures**: Copy `solar_battery/*.sysml` into `tests/fixtures/solar_battery_model/`.
Scripts accept arbitrary model paths via CLI argument, defaulting to in-repo fixtures.

**Model Coverage**:

| Model Suite | CalcDefs | Total Outputs | Expression Patterns Expected |
|-------------|----------|---------------|------------------------------|
| chain_spike | 3 | 3 | Simple binary (Pattern A) |
| sample_model | 1+ | 1+ | Simple binary (Pattern A) |
| solar_battery | 15 | 58 | Patterns A, B, C, D (multi-step, `**`, literals, compound) |

### Out of Scope

- Building the `expression_compiler.py` module
- Modifying any pipeline code (extractor, resolution, generation)
- Compiling expressions to Python -- this spike extracts and classifies only
- Attribute-level expressions on part definitions (Phase 2)
- Testing against CATF or fusion-tea production models (solar_battery is sufficient)

### Edge Cases & Considerations

- **Literal-only outputs** (e.g., PermittingCostCalc `material_cost = 0.0`):
  The expression AST may be a bare `LiteralRational` with no operator or
  reference nodes. Q1 should still report these as "has AST" since they are
  compilable (they compile to a literal assignment).

- **Expressions spanning multiple lines** (e.g., AnnualizedFinancialCalc's
  `capital_recovery_factor`): The AST should be a single tree regardless of
  source formatting. Verify traversal depth handles deeply nested `**` expressions.

- **`default :=` expressions on input attributes**: These are NOT output
  expressions. The spike MUST only examine output attributes (`is_output` direction).
  Default values are already handled by the existing entry-point system.

- **Costing.sysml dependency**: The solar_battery library imports `Costing::*`.
  The `costing.sysml` file must be included in the fixture copy. SysIDE
  needs all transitive imports available to parse the model.

---

## Requirements

### Functional Requirements

> Requirements below are from the epic backlog item and concept doc unless marked [INFERRED].

1. **FR-1**: Q1 script (`scripts/spike_extract_expression_asts.py`) MUST load
   models via `SysMLDataExtractor`, iterate all CalcDefs, and for each output
   attribute report: has AST (bool), root node type, traversal depth, set of
   all node types in subtree.

2. **FR-2**: Q1 script MUST accept model paths as CLI arguments (one or more
   directories). When no arguments are given, it MUST default to all three
   in-repo fixture directories (`chain_spike_model/`, `sample_model/`,
   `solar_battery_model/`).

3. **FR-3**: Q2 script (`scripts/spike_resolve_expression_refs.py`) MUST use
   `agentic_mbse.sysml.expression.extract_feature_refs()` to find all feature
   references in each output expression, then classify each as `input`,
   `intermediate` (sibling output), or `unresolvable`.

4. **FR-4**: Q2 script MUST use the same CLI interface as Q1 (accept model
   paths, default to fixtures).

5. **FR-5**: Both scripts MUST print results as formatted tables to stdout,
   suitable for copy-paste into the report.

6. **FR-6**: [INFERRED] Solar battery model fixtures (`library.sysml`,
   `design.sysml`, `costing.sysml`) MUST be copied to
   `tests/fixtures/solar_battery_model/` so the spike is self-contained
   and repeatable within this repo.

7. **FR-7**: [INFERRED] Q1 script MUST separately identify output attributes
   whose `feature_value_expression` is None/missing vs. those that have a
   parseable AST, so that the coverage percentage is unambiguous.

### Non-Functional Requirements

- Scripts SHOULD run in under 60 seconds per model suite (SysIDE load time
  dominates; extraction itself is fast)
- Scripts MUST NOT modify any source code or test fixtures
- Scripts MUST be runnable via `uv run python scripts/spike_*.py`

---

## Evaluation Methodology

### Q1 Evaluation: AST Extraction Coverage

**Metric**: `coverage = outputs_with_ast / total_outputs * 100`

| Result | Interpretation | Action |
|--------|---------------|--------|
| Coverage >= 80% | Core assumption validated | Go for compiler design |
| Coverage 50-80% | Partial validation | Investigate missing ASTs; may need SysIDE workarounds |
| Coverage < 50% | Assumption invalid | No-go; revisit approach (possibly extract from text instead) |

**Per-model breakdown required**: Report coverage for each model suite separately
so we can distinguish fixture issues from systematic SysIDE limitations.

**Node type inventory**: List every distinct node type encountered. Compare against
the expected set. Any unexpected types need to be categorized as:
- Handleable (can be added to compiler's supported set)
- Blocking (fundamentally incompatible with the compiler design)

### Q2 Evaluation: Reference Resolution

**Metric**: `resolution_rate = resolved_refs / total_refs * 100`

| Result | Interpretation | Action |
|--------|---------------|--------|
| Resolution = 100% | Core assumption validated | Go -- all refs are inputs or intermediates |
| Resolution 90-99% | Near-miss | Investigate failures; likely a small set of edge cases to handle |
| Resolution < 90% | Assumption partially invalid | Categorize failures; may need reference resolution strategy changes |

**Per-ref classification required**: Every reference must be tagged as one of:
- `input` -- matches a declared `in attribute` by name
- `intermediate` -- matches a sibling `out attribute` by name
- `unresolvable` -- matches neither; record the name, the CalcDef, and the output it appears in

**Zero tolerance for silent failures**: If `extract_feature_refs()` returns
an empty list for an expression that visually contains references (e.g.,
`wattage * cost_per_watt`), that is a bug in the extraction, not evidence
of "no references." The script MUST cross-check: if the expression AST
contains `FeatureReferenceExpression` nodes (by type check), then
`extract_feature_refs()` MUST return at least that many refs.

### Go/No-Go Decision

**Go** requires ALL of:
- Q1 coverage >= 80% across all model suites
- Q2 resolution = 100% (or all exceptions have documented workarounds)
- No blocking node types discovered
- The set of encountered expression patterns is a subset of Patterns A-F from the concept doc

**No-go** if ANY of:
- Q1 coverage < 50% on any model suite
- Q2 resolution < 90%
- A blocking node type is discovered with no feasible workaround

**Conditional go** (proceed with reduced scope) if:
- Q1 coverage 50-80% with clear explanation of missing cases
- Q2 resolution 90-99% with documented edge cases that can be classified as `MANUAL_REQUIRED`

---

## Acceptance Criteria

### Core Functionality
- [ ] `scripts/spike_extract_expression_asts.py` exists and runs without errors on all three model suites
- [ ] `scripts/spike_resolve_expression_refs.py` exists and runs without errors on all three model suites
- [ ] Solar battery fixtures copied to `tests/fixtures/solar_battery_model/` (3 files)
- [ ] Q1 output includes: per-CalcDef per-output table with AST presence, root type, depth, node types
- [ ] Q1 output includes: summary coverage percentage per model suite
- [ ] Q1 output includes: complete node type inventory across all models
- [ ] Q2 output includes: per-CalcDef per-output per-ref table with resolution classification
- [ ] Q2 output includes: summary resolution rate
- [ ] Q2 output includes: cross-check validation (ref count vs FeatureReferenceExpression node count)

### Deliverables
- [ ] `scripts/spike_extract_expression_asts.py`
- [ ] `scripts/spike_resolve_expression_refs.py`
- [ ] `tests/fixtures/solar_battery_model/library.sysml` (copied from fusion-tea)
- [ ] `tests/fixtures/solar_battery_model/design.sysml` (copied from fusion-tea)
- [ ] `tests/fixtures/solar_battery_model/costing.sysml` (copied from fusion-tea)
- [ ] `.project/active/expr-spike-ast/report.md` (findings + go/no-go recommendation)

### Quality & Integration
- [ ] No existing tests broken
- [ ] Scripts are self-contained (no pipeline code modifications)
- [ ] Report contains quantitative evidence for every claim

---

## Known Model Inventory

For reference, these are the CalcDefs across all three model suites and the
expression patterns expected based on reading the SysML source:

### chain_spike (3 CalcDefs, 3 outputs)

| CalcDef | Output | SysML Expression | Expected Pattern |
|---------|--------|-----------------|------------------|
| AreaCalc | area | `length * width` | A (simple binary) |
| CostCalc | total_cost | `area * rate` | A |
| SummaryCalc | cost_per_area | `cost / area` | A |

### solar_battery (15 CalcDefs, 58 outputs)

| CalcDef | Outputs | Expression Patterns |
|---------|---------|-------------------|
| PVModuleCostCalc | 5 | B (multi-step intermediates) |
| InverterCostCalc | 5 | B |
| ArrayBOSCostCalc | 5 | B + compound material_cost (`a*b + c*d`) |
| BatteryPackCostCalc | 5 | B + 3-way product (`a * b * c`) |
| HybridInverterCostCalc | 5 | B |
| BatteryBOSCostCalc | 5 | B |
| RackingCostCalc | 5 | B |
| ElectricalPanelCostCalc | 5 | B + addition in material_cost (`a + b*c`) |
| PermittingCostCalc | 5 | D (literal 0.0 outputs) + A |
| AllocationCostCalc | 5 | B + literal factor (`total * 0.8`) |
| EnergyProductionCalc | 1 | D (literal 8760.0) + A |
| AnnualizedOMCalc | 1 | A |
| AnnualizedFuelCalc | 1 | A |
| AnnualizedFinancialCalc | 2 | C (parenthesized, `**` power) |
| LCOECalc | 1 | C (parenthesized, `**` power, compound) |

**Prediction**: All 15 CalcDefs, all 58 outputs should have extractable ASTs
and 100% resolvable references. Every expression uses only arithmetic operators,
feature references to declared inputs, intermediate references to sibling
outputs, and numeric literals.

---

## Related Artifacts

- **Concept:** `.project/concepts/expression-aware-codegen.md` (design reference, Sections 2-6)
- **Epic:** `.project/backlog/epic_expression_aware_codegen.md` (Item 1)
- **Research:** `.project/research/20260202-180000_expression-compilation-and-inline-math-strategy.md`
- **Design:** `.project/active/expr-spike-ast/design.md` (N/A -- spike has no design phase)

---

**Next Steps:** After approval, proceed directly to implementation (write spike scripts, copy fixtures, run, write report). No design phase needed for a research spike.
