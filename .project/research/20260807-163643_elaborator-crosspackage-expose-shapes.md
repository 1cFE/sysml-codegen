# Learning Test: Cross-package / multi-hop EXPOSE through the elaborator (Item 5 Phase 2, leg 1)

**Date**: 2026-08-07 · **Branch**: `source-identity-epic` @ `f8870a7` · **Author**: leg-1 session
**Upstream**: `.project/active/elaborator-breadth/plan.md` (Phase 2, first leg) ·
design `.project/active/elaborator-design/design.md` (D2/D5/D6)

## Summary of Findings

**The EXPOSE idiom is structurally untyped, and the elaborator now covers it.**
The leg's fixtures broke four premises the Phase-1 elaborator inherited from the
spike, and one contract-relevant discovery fell out; all are implemented and pinned
by 15 kept licensed tests (`tests/conformance/test_elaboration_expose_shapes.py`):

1. **Real plant models put everything on untyped part usages.** All 42 catf_mfe
   calc usages live under parts with no user-definition typing (73 untyped usages,
   nesting freely); d316 has zero user part defs. The typed occurrence index
   answers nothing for them. The elaborator now gives untyped usages
   elaboration-local contexts at their def-context-remapped qualified names — the
   legacy index is untouched.
2. **Attributes are declared on usages and packages, not only definitions.**
   Usage-declared attributes (catf's exposed channels) and package-owned
   attributes (d316's `seed_src`) now get nodes; package-level calc usages
   (`calc gen`) now place.
3. **Chains root at calc usages and at off-ancestor parts.** Sibling-calc chaining
   (`in area = area_calc.area`; root fact kind `CalculationUsage`) anchors AT the
   producer; a cross-package root (`catf_blanket.pump_power`; root kind
   `PartUsage`, owner `''`) anchors at the root element's own unique occurrence.
   One chain rule, two new anchor arms — no consumer special-casing.
4. **EXPOSE is an alias edge, not a value and not an input.** An attribute whose
   declared value is a pure feature chain (`pump_power = pump_load.pump_power`,
   wi014's `total_cost`) gets `AttrNode.alias_target`, resolved per occurrence
   with the same chain rule; consumers follow aliases transitively, so catf's
   two-hop `physics -> blanket.pump_power -> pump_load` collapses to ONE producer
   edge (spec R2 across package boundaries).
5. **catf_mfe itself authors the degenerate self-binding**
   (`in pumping_speed_total = pumping_speed_total`, `vacuum.sysml:176`) — so
   strict elaboration rightly rejects a corpus fixture. This forced the
   D9-sanctioned halt-vs-report switch NOW rather than at Phase 3:
   `elaborate(..., strict=False)` records the same findings as graph diagnostics
   and skips ONLY the offending bindings (identity never reinterpreted). The
   Phase-3 dual-run grind needs exactly this to diff fusion_tea / ife_plant /
   solar / catf, which all carry SRC-01 defects.

## Question / Goal

The Phase-1 elaborator was proven on fixtures whose parts are all **typed** and whose
chains root at part usages on the consumer's ancestor chain. The leg-1 fixtures
(wi014_toy, catf_mfe, d316_crosspart_expose) author the cross-package / EXPOSE idiom:
derived attributes exposing calc outputs (`pump_power = pump_load.pump_power`),
consumers in other packages chaining to them (`catf_blanket.pump_power`), sibling-calc
chaining (`area = area_calc.area`), package-level calc usages and attributes, and —
structurally — **untyped part usages** carrying all of it. Map what SysIDE provides for
each shape and what the elaborator does with it today, before implementing support.

## Log

### Probe A — wi014_toy declarations (licensed, scratchpad `probe_leg1.py`)

- `area_calc` / `cost_calc` are **templates** on `part def 'Toy Plant'`
  (`toy_plant__Toy_Plant__*`, `is_template=True`); `demo_plant : 'Toy Plant'` is the
  one typed occurrence — the Phase-1 remap places them.
- Sibling calc chain `in area = area_calc.area`: chain evidence root =
  `toy_plant::'Toy Plant'::area_calc`, **`element_kind=CalculationUsage`**,
  `owner_is_definition=True`, members `('area',)`. The Phase-1 anchor rule only
  checks part-occurrence paths, so a calc-usage root never anchors → the binding
  misses today.
- The EXPOSE attr `total_cost` on the part def: `feature_value_expression` is a
  `FeatureChainExpression`; `feature_chain_facts` gives root
  `toy_plant::'Toy Plant'::cost_calc` (CalculationUsage) + members `('cost',)` —
  everything an alias edge needs is available at the declaration.

### Probe B — d316_crosspart_expose (licensed, same script)

- The model has **zero user part definitions**: `part consumer { ... }` is untyped.
  `user_partdef_lookup` is empty, `occurrences_of_part_usage('D316Design::consumer')`
  returns `[]` — the whole Phase-1 occurrence universe is empty here.
- Package-level calc usage `calc gen` extracts concrete
  (`qualified_name='D316Design__gen'`, `is_template=False`,
  `parent_part_path=''`, `owning_part_def_qn=None`) — the Phase-1 placement rule
  (parent must be an occurrence) drops it.
- Package-level attribute referent: `in seed = seed_src` resolves to
  `D316Design::seed_src` with **`owner_qualified_name=''`** and
  `owner_is_definition=False` — a third referent-owner kind (package) neither
  Phase-1 arm handles.
- `in inp = exposed` resolves to `D316Design::consumer::exposed`,
  owner = the **untyped part usage** — the usage-level arm's
  `occurrences_of_part_usage` answers `[]` for it.

### Probe C — catf_mfe (licensed, scratchpad `probe_leg1b.py`)

- **All 42 calc usages sit under untyped part usages** (73 untyped usages total,
  including untyped-under-untyped nesting like
  `catf_vacuum_pumping::roughing_pumps`). catf_mfe is entirely invisible to the
  Phase-1 occurrence universe.
- The physics consumer (`CATFMFEPhysics__catf_physics__net_electric`) shows the two
  cross-package chain-root kinds side by side:
  - `p_electric_gross`: root `catf_physics::gross_electric`,
    `kind=CalculationUsage`, `owner_is_def=False` — a **concrete sibling calc** root
    (anchors via the consumer's ancestor once untyped contexts exist).
  - `p_pumps` etc.: root `CATFMFEBlanket::catf_blanket`, **`kind=PartUsage`,
    `owner_qualified_name=''`** — a package-level part in a *different package*,
    NOT on the consumer's ancestor chain. Anchoring must fall back to the root
    usage's own occurrence.
- The multi-hop link: `catf_blanket.pump_power` lands on attr `pump_power` whose own
  value expression is the FCE `pump_load.pump_power` (root kind CalculationUsage) —
  consumer → exposed attr → producer output is two hops, so consumer identity is the
  PRODUCER's channel only if the exposed attr carries a followable alias edge.

### Shape inventory → implementation obligations (leg 1)

| # | Shape | Fact base | Elaborator today | Obligation |
|---|---|---|---|---|
| 1 | Untyped part usages (73 in catf) | no FeatureTyping; members = attrs + calcs | invisible (no occurrence) | elaboration-local contexts from sanitized QN + def-context remap; legacy index untouched |
| 2 | Usage-declared attributes (typed + untyped usages) | AttributeUsage members with literal / FCE / expr values | no nodes | attr nodes per occurrence; literal → value; FCE → alias edge |
| 3 | Package-level attributes (`seed_src`) | referent owner `''` | unresolvable | package-attr nodes; referent fallback by exact QN |
| 4 | Package-level calc usages (`gen`) | concrete, `parent_part_path=''`, `owning_part_def_qn=None` | dropped | place at sanitized QN |
| 5 | Sibling-calc chain roots | root kind CalculationUsage | anchor miss | anchor loop also matches calc nodes → ProducerRef |
| 6 | Cross-package part-usage chain roots | root kind PartUsage, owner `''`, off-chain | anchor miss | fallback: root's own occurrence paths (unique, else ambiguous) |
| 7 | EXPOSE attrs (`total_cost`, `pump_power`, `exposed`) | FCE value expr, facts complete | value None, no edge | `AttrNode.alias_target` resolved per occurrence; consumer resolution follows aliases transitively |

Non-obligations (phase-planned elsewhere): OperatorExpression-valued attributes stay
value-less (FORMULA leg, D6); EXPRESSION redefinitions (aggregation leg); constraint
catalog (its own leg).

## Tests Written

`tests/conformance/test_elaboration_expose_shapes.py` — 15 kept licensed tests:

- **Fact pins (5)** — the SysIDE evidence each shape yields, held regardless of
  implementation: sibling-calc chain root kind, cross-package part-usage root with
  empty owner, untyped invisibility to the typed index, package-attr referent with
  no owner QN, complete chain facts on the EXPOSE declaration.
- **Shape behavior (10)** — the elaborated outcomes: wi014 sibling producer edge +
  constraint wiring + part-def expose alias; d316 package-level calc/attr +
  untyped-part expose follow-through; catf strict rejection of its real
  self-binding, lenient finding + skip, all-42 placement, multi-hop cross-package
  expose collapse, concrete sibling chain.

Implementation landed in the same leg (`elaboration/elaborate.py`, `graph.py`):
untyped contexts, usage/package attr nodes, alias edges + transitive
follow-through, two chain-anchor arms, package referent arm, `strict` switch.

## Reproduction

```bash
set -a && source /home/reid/1cfe/agentic-mbse/.env && set +a
uv run pytest tests/conformance/test_elaboration_expose_shapes.py -q
```

## Open Questions / Follow-ups

- Value-site taxonomy for usage-declared attribute literals: recorded as
  `DEFINITION_DEFAULT` (the usage IS the declaration). Whether projection classifies
  these DESIGN_ATTRIBUTE vs LIBRARY_DEFAULT is the projection leg's question —
  legacy classifies catf design attrs as DESIGN_ATTRIBUTE.
- Untyped part usage WITH multiplicity: no corpus instance found; QN-expansion
  contexts would drop the `[i]` index. Unprobed; block-loud stance covers it only if
  such a shape appears.
- Aliases whose chain cannot resolve (dead expose): named diagnostic, consumer then
  misses on the value-less node — surfaced in the dual-run grind if any fixture has one.
