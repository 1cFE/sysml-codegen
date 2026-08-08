# Learning Test: Shadowing + equal-valued literal identity (Item 5 Phase 2, leg 7)

**Date**: 2026-08-07 · **Branch**: `source-identity-epic` (after `483443e`) · **Author**: leg-7 session
**Upstream**: `.project/active/elaborator-breadth/plan.md` (Phase 2, shadowing/literals leg)

## Summary of Findings

**The capability-survey referent gap is closed with one authored fixture and one
tier-2 ordering fix.**

1. **Two-level specialized-def literal shadowing now has a fixture**
   (`tests/fixtures/elab_shadowing_probe/`, authored this leg) and correct
   semantics: a subtype's `:>>` and its supertype's `:>>` both expand onto the
   same occurrence (subtype-closure enumeration), so tier 2 now tracks the
   winning owner per node and lets only a MORE SPECIFIC definition overwrite
   (`_def_declares`, the same closure test everywhere else uses) — Leaf's 9.0
   at a Leaf occurrence, Mid's 5.0 at a Mid occurrence, never redefinition list
   order. This closes the ordering hole flagged in the leg-3 findings.
2. **Equal-valued independent literals stay distinct** (the ratified 2026-08-05
   rule): two occurrences overriding to the same 4.0 get two nodes, each
   consumer wired to its own — pinned, value coincidence can never merge
   identity.
3. **Scope shadowing** (`shadowed_reference`, audit F2's fixture): the
   `::`-qualified referent resolves to the OUTER 2.0 node; the same-named 7.0
   shadow on the consumer's own owner is never selected. No elaborator change
   needed — the usage-level referent arm already lands on the referent's own
   occurrence.
4. **SysIDE authoring fact** worth keeping: `feature-value-overriding` — a
   `:>>` cannot override a BOUND (`=`) value; every overridable level must use
   `default`, including intermediate redefinitions (`:>> rate default 5.0`).
   Recorded in the fixture header.

## Question / Goal

Close the capability survey's "no shadowing/specialization referent fixtures"
gap: prove innermost-wins across a two-level def chain, equal-valued
independence, and shadow-immunity of qualified referents.

## Log

- Fixture authored; first two loads failed on `feature-value-overriding`
  (bound values are not overridable) → `default` at base and mid levels.
- Tier-2 fix: `_apply_value_tiers` now keeps a per-node winning-owner map;
  probe shows 9.0/5.0 per occurrence, both `specialized_def` sites.
- shadowed_reference probe: qualified referent → outer node, zero diagnostics.

## Tests Written

`tests/conformance/test_elaboration_shadowing.py` — 4 kept licensed tests:
innermost-def-wins per occurrence; base-authored consumer reads each
occurrence's node; equal-valued distinctness with per-occurrence wiring;
qualified reference never selects the scope shadow.

## Reproduction

```bash
set -a && source /home/reid/1cfe/agentic-mbse/.env && set +a
uv run pytest tests/conformance/test_elaboration_shadowing.py -q
```

## Open Questions / Follow-ups

- Incomparable tier-2 owners (a diamond where two unrelated defs redefine the
  same inherited attribute) keep the first writer deterministically but without
  a semantic ruling — no corpus fixture authors it; surface if the grind finds
  one.
