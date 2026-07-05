# Hierarchy Pipeline Deep Investigation

**Date**: 2026-02-12
**Investigator**: Claude (Opus 4.6)
**Scope**: COST-PATTERN Items 1-4 architecture validation and E2E test failure root causes
**Status**: COMPLETE — all 5 root causes identified and probe-validated

## Purpose

This investigation provides a definitive, proof-style documentation of how the hierarchy pipeline algorithms work, identifies where assumptions diverge from reality (real SysIDE AST vs mocks), and defines a non-mocked test strategy that validates the actual data representations.

## Report Index

| Report | Status | Contents |
|--------|--------|----------|
| `01_algorithm_proof.md` | Complete | Formal algorithm documentation with invariants, 9 assumption gaps identified |
| `02_failing_test_investigation.md` | Complete | Line-level trace of 4 failing E2E tests (note: CollectExpression theory refuted by probes) |
| `03_ast_probe_results.md` | Complete | Inline in 05_synthesis — probe results embedded with analysis |
| `04_test_strategy.md` | Complete | Three-tier non-mocked test plan with real AST validation |
| `05_synthesis_and_fixes.md` | **Complete** | **START HERE** — Definitive root causes, fix plan, priority order |

## Quick Summary: 5 Root Causes

| RC | Description | File:Line | Fix Complexity |
|----|-------------|-----------|----------------|
| RC 1 | `_unwrap_invocation()` strips FeatureChainExpression (has `function.name='.'`) | `hierarchy_resolver.py:294` | 1-line add |
| RC 2 | `reconstruct_expression()` checks InvocationExpression before FeatureReferenceExpression | `expression_utils.py:47-58` | Reorder checks |
| RC 3 | `_walk_aggregation_ast()` doesn't check Chain/Ref types before function.name | `hierarchy_resolver.py:346` | Add type checks |
| RC 4 | `_scope_aggregation_expressions()` misses all-singleton assemblies | `initialization.py:332` | Add Strategy 3 |
| RC 5 | Alias detection searches PartDef redefs, not CalcUsage bindings | `hierarchy_resolver.py:519-528` | Add binding scan |

## Key Discovery: SysIDE AST Properties

```
FeatureReferenceExpression  has function.name='Evaluation' AND referent.name='pv_module'
FeatureChainExpression      has function.name='.'          AND target_feature.name='capital_cost'
InvocationExpression (sum)  has function.name='sum'

Using hasattr(node, "function") as a test for InvocationExpression produces FALSE POSITIVES.
```

## Probe Scripts

Located in `scripts/probes/`:

| Script | Status | Key Finding |
|--------|--------|-------------|
| `probe_sum_ast_structure.py` | Ran | sum() operand is FeatureChainExpression (NOT CollectExpression) |
| `probe_redefinition_structure.py` | Ran | All CHAIN redefs show "Evaluation().X" due to RC 2 |
| `probe_alias_resolution.py` | Ran | No alias redefs on any PartDef; total_capex is CalcUsage binding |
| `probe_multiplicity_structure.py` | Ran | Clean: pv_module(20), inverter(4), battery_pack(8) |
| `probe_backtracker_resolution.py` | Available | Full pipeline wiring check |

## The 4 Failing Tests → Root Cause Mapping

```
test_bf1_no_unsupported_nodes           → RC 2 (Evaluation() in text), RC 3 (unsupported flag)
test_bf1_sum_terms_have_real_names      → RC 1 (sum_terms empty, arrayed as LocalTerm)
test_bf7_aliases_extracted              → RC 5 (wrong data source), RC 4 (Plant not scoped)
test_bf7_total_capex_wired_to_module_output → RC 4 (no Plant agg module), RC 5 (no alias key)
```

## Prior Hypotheses: Corrected

1. ~~SysIDE wraps sum() operands in InvocationExpression(Evaluation)~~ → **No.** sum() operand is directly a FeatureChainExpression. The Evaluation is on the inner FeatureReferenceExpression.
2. ~~CollectExpression (OperatorExpression subclass) wraps operands~~ → **Refuted by probe.** No CollectExpression exists in the AST.
3. ~~Alias detection order matters~~ → **Wrong framing.** The alias doesn't exist as a PartDef redef at all — it's a CalcUsage binding.
4. ~~Site Infrastructure name mismatch~~ → **Partially correct but wrong root cause.** The real issue is zero multiplicity children, not name mismatch.
