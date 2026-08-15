# Learning Test: FORMULA computed attributes through the elaborator (Item 5 Phase 2, leg 4)

**Date**: 2026-08-07 · **Branch**: `source-identity-epic` (after `a1ad27a`) · **Author**: leg-4 session
**Upstream**: `.project/active/elaborator-breadth/plan.md` (Phase 2, fourth leg) · design D6

## Summary of Findings

**D6's computed-node fold works, including the previously-unsupported
FORMULA→FORMULA chains — every attr_expr_probe pattern wired on the first run.**
The representation decision that made it clean: a computed attribute IS a calc
node at the attribute's own occurrence path (no attribute node exists for it).
Its single output is the attribute's name, its inputs are the expression's
feature terms (deduplicated; keyed by sanitized reference path), resolved by the
SAME referent rules as calc bindings, with alias follow-through. Consumers
referencing a computed attribute get a producer edge via one shared lookup
(`_attr_or_computed`), used by the def-level, usage-level, and package referent
arms and by chain descent — so:

- FORMULA→FORMULA (`cost = area * rate`, `marked_up_cost = cost * markup`) and
  fan-in (`cost_density = cost / volume`) are ordinary producer edges.
- A computed attribute feeding a calc usage (`in value = area`) and a calc
  output inside an expression (`scaled_area = scale_calc.result * 2.0`) both
  wire without special cases.
- Pure-chain values stay EXPOSE aliases (leg 1), never computed nodes — the
  expose/formula boundary is exactly literal/chain/expression on the declared
  value, decided in one place (`_attribute_facts`).

Unsupported term kinds (invocations — `sum(...)`) make the walk return None and
the attribute stays a value-less node with a warning: aggregations are the next
leg's, and nothing silently half-computes.

Scale note: catf_mfe lifts 144 computed attributes on top of its 42 calc usages
(the leg-1 placement test now counts non-computed nodes). The expression AST
rides on the node (`expression_ast`) for projection to render; its snapshot wire
form is the round-trip leg's question.

## Question / Goal

Whether D6's fold — computed attributes as calc nodes with term edges from the
shared referent rules — covers attr_expr_probe's patterns A (binary ops),
B (multi-term/nested/duplicate terms), C (FORMULA→FORMULA), D (mixed with calc
usages), without consumer special-casing.

## Log

- Implementation first-pass (term walk + computed CalcNode + `_attr_or_computed`
  + chain-descent computed arm), probe `probe_leg4.py`: 15/15 computed nodes,
  all edges exact, strict-clean, zero diagnostics.
- Guardrail: the term walk is a new FCE+OE dispatch site; the nested closure
  double-counted, so the walk was lifted to `_collect_expression_terms` and
  registered (5 dual-check / 7 multi-type audited sites).
- Leg-1's catf placement test adjusted to count non-computed nodes (42).

## Tests Written

`tests/conformance/test_elaboration_computed_attrs.py` — 9 kept licensed tests:
strict+clean elaboration; simple expression → computed node (and no competing
attr node); duplicate-term dedup (B6); FORMULA→FORMULA; fan-in; computed feeds
calc usage; calc output inside expression; pure EXPOSE stays an alias; all 15
computed attributes lift.

## Reproduction

```bash
set -a && source /home/reid/1cfe/agentic-mbse/.env && set +a
uv run pytest tests/conformance/test_elaboration_computed_attrs.py -q
```

## Open Questions / Follow-ups

- An occurrence ``:>>`` literal override TARGETING a computed attribute has no
  node to land on (OVERRIDE_TARGET_MISSING today). No fixture authors it; if the
  corpus grind surfaces one, the contract's value-tier answer (occurrence
  override wins → the computed node reverts to a valued attr node?) needs a
  ruling — do not disposition silently.
- `expression_ast` is live-AST-only; the snapshot round-trip leg owns its wire
  form (likely the shared neutral ExpressionIR).
