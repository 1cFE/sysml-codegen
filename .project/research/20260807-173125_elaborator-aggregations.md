# Learning Test: EXPRESSION-redefinition aggregations through the elaborator (Item 5 Phase 2, leg 5)

**Date**: 2026-08-07 · **Branch**: `source-identity-epic` (after `78d1691`) · **Author**: leg-5 session
**Upstream**: `.project/active/elaborator-breadth/plan.md` (Phase 2, fifth leg) · design D6

## Summary of Findings

**D6's aggregation fold lands, and the Item-10 cross-part collapse family dies by
construction.** What was implemented and what it proved:

1. **EXPRESSION `:>>` redefinitions convert to computed nodes** after the value
   tiers (an occurrence-literal override outranks the expression). The
   value-carrying redefinition sweep now classifies all three non-literal kinds
   from the AST — chain → EXPOSE alias (leg 3), expression → computed node,
   indexed → screened — for definitions AND usages uniformly.
2. **Term edges come from the shared neutral decomposition**
   (`agentic_mbse.sysml.aggregation.decompose_aggregation_expression`), whose
   terms carry the Item-2 salvaged resolved facts; each term resolves by the
   same referent rules as bindings (alias follow-through included). All six
   mixed_consumers rollups wire strict-clean: chain terms, a qualified
   def-referent term, a producer-output chain, a cross-owner local, and the sum.
3. **`sum(part.attr)` expands per concrete instance** under the node's anchor —
   `bank_total` gets `cell[0..2]__cell_cost` node edges;
   `agg_localterm_probe`'s sum gets three per-instance PRODUCER edges because
   each `cell[i]`'s `:>> capital_cost = cost_model.cost` alias (leg 3) is
   followed per instance, plus the plain `markup` local term. The Item-10
   qualifier-drop collapse (`crosspart_rollup_twolevel`) cannot occur: the
   rollup's terms follow each child's own alias to DISTINCT producers
   (a: 3.0-based, b: 5.0-based — the value-coincidence trap is moot).
4. **A def-level referent declared by no enclosing occurrence** (the
   `'Qual Plant'::level + 1.0` aggregation on the CONTAINING station) needed an
   off-ancestor fallback mirroring the chain rule's: the owning definition's
   occurrences, preferring one under the consumer's contexts, unique otherwise;
   the fallback owns its dispositions (one diagnostic per miss).
5. **SURFACED — d38_caret blocks loud and stays blocked.** It authors a
   parameterized multiplicity (`cell[n]`); occurrence enumeration raises
   `NonFiniteCardinalityError` at elaborator construction. The legacy pipeline
   reads `sum` over that part as parametric multiply (`n * cell.value`) and
   generates; the ratified stance (spec Non-Goals: expand-finite or block-loud,
   no third disposition) forecloses that reading here. The plan named d38_caret
   as a leg fixture — the conflict is surfaced, not silently resolved: the
   kept test pins the block as the sanctioned disposition, d38's Phase-3 ledger
   row is "blocked (non-finite)", and whether a parametric-sum form returns is
   the owner's call at the pre-Item-6 checkpoint. The caret operator's
   XOR-vs-`**` concern is a rendering question that only exists at projection.

Corpus SRC-01 census keeps growing: `crosspart_rollup_twolevel`
(`cost_calc.base`) and `agg_localterm_probe` (`cost_model.area`) are the fifth
and sixth fixtures authoring the degenerate `in R = R` idiom.

## Question / Goal

Whether D6's computed-node fold covers EXPRESSION redefinitions — plain
arithmetic, qualified terms, producer chains, and `sum()` over multiplicity —
and whether cross-part rollups keep per-child channel identity.

## Log

- Probe (`probe_leg5.py`): mixed_consumers all six rollups exact, zero
  diagnostics (after adding the def-referent off-ancestor fallback for
  `qual_total`); crosspart rollup distinct a/b producers; d38_caret raises
  NonFiniteCardinalityError at init.
- Probe (`probe_leg5b.py`): agg_localterm_probe mixes per-instance producers
  with the local term exactly.
- No new dispatch site: term classification reuses the shared neutral
  decomposition (its `_decompose_node` is already an audited site).

## Tests Written

`tests/conformance/test_elaboration_aggregations.py` — 7 kept licensed tests:
expression redefinition → computed node (strict-clean); per-instance sum edges;
qualified term via the off-ancestor fallback; producer-chain term; cross-part
rollup distinctness + downstream consumer; local-term mix; d38 block-loud pin.

## Reproduction

```bash
set -a && source /home/reid/1cfe/agentic-mbse/.env && set +a
uv run pytest tests/conformance/test_elaboration_aggregations.py -q
```

## Open Questions / Follow-ups

- **Owner checkpoint item (pre-Item-6):** d38_caret-class models (parameterized
  multiplicity under an aggregation) — stay blocked, or ratify a parametric-sum
  form? Blocking regresses a shape legacy generates.
- Aggregation rendering (operator spelling incl. `^` → `**`, sum expansion
  form) is projection-leg scope; the graph carries `expression_ast`.
