# Design: Production Elaborator + Projection (ELABORATE-FIRST Item 4)

**Date**: 2026-08-07 · **Status**: Draft (post-spike; mechanics proven in
`.project/active/elaborator-spike/elab_prototype.py`)

## Shape

```
src/sysml_codegen/elaboration/          (new package)
  graph.py        InstanceGraph, AttrNode, CalcNode, ConstraintNode, node IDs
  elaborate.py    the one pass: occurrences -> attr nodes -> value tiers ->
                  calc/constraint nodes -> binding resolution -> diagnostics
  project.py      InstanceGraph -> ComputationGraph (modules, EP groups,
                  execution order, output aliases, constraint catalog)
```

Substrate reused, not rebuilt: `PartInstanceIndex` (occurrence expansion, the one walker),
the Item-2 evidence builders (`source_evidence.py`, `usage_extractor` evidence arms,
`ResolvedTargetFact`/`feature_chain_facts`), `extract_hierarchy_data` (AST facts),
`constraint_lowering` (already occurrence-based), the expression compiler, and
`core/qualified_names` naming (ADR-003 unchanged).

## Decisions

**D1 — Node identity is the occurrence path.** `InstanceOccurrence.instance_path` extended
with member leaves, `__`-joined. Spike-proven stable across loads. Indexed occurrences are
positional (`cell[2]`); a model edit that reorders siblings renames those nodes — accepted and
recorded, matrix-visible at Item-6 review.

**D2 — The elaborator walks calc/constraint usages off the AST itself.** It consumes
*declarations* (template calc usages + `ConstraintUsage` with `include_subtypes=True`) and
expands them per occurrence with the def-context remap rule. It does NOT consume the legacy
virtual expansion (`_expand_template_calc_usages`) — that path half-misses def-nested-usage
calcs (spike discovery: `owner_def=None`, definition-relative) and is on the deletion ledger.
The per-binding evidence builders are factored so both front ends share them during dual-run.

**D3 — One remap rule, two jobs.** Longest def-key prefix of a definition-relative path →
one path per occurrence of that def. Anchors occurrence overrides (this IS the C19 fix) and
places def-declared calcs/constraints. No other bridge exists (the one-bridge constraint).

**D4 — Value tiers, innermost-wins.** Occurrence `:>>` (deepest anchor) > specialized-def
`:>>` > definition default. Literal tiers set node values; EXPRESSION-valued redefinitions
become computed nodes (D6). Value-site is recorded per node (`occurrence_override` /
`specialized_def` / `definition_default`) and drives entry-point classification directly —
the group-deriver value backfill has no role.

**D5 — Three referent classes, one rule each** (spike-proven, no consumer special-casing):
- *Chain*: anchor the root usage at the innermost enclosing occurrence that contains it,
  descend resolved member names; a member that is a calc node yields a producer-output edge.
- *Def-level referent*: innermost enclosing occurrence whose definition (incl. supertype
  closure) declares the referent.
- *Usage-level referent* (occurrence-rooted redefining feature): the owner usage's occurrence
  on the consumer's ancestor chain; unique otherwise; else `SI_OCCURRENCE_AMBIGUOUS`.
Misses are named diagnostics (`SI_OCCURRENCE_MISSING`), never fallback inputs.

**D6 — Computed attributes and aggregations are calc nodes.** A FORMULA attribute or
EXPRESSION redefinition (e.g. `:>> station_total = rig.gain_setting + 100.0`,
`sum(cell.cell_cost)`) elaborates to a computed node whose input edges come from the same
three referent rules applied to its term evidence (chain root + members on every term after
Item 2). Aggregation instance discovery is `occurrences_of` under the owning occurrence —
no QN string surgery. This folds the separate `attr_resolution_map` path into the one model;
FORMULA→FORMULA edges follow naturally.

**D7 — Constraints ride the same graph.** Constraint nodes get their actuals from the same
binding resolution; `constraint_lowering`'s catalog assembly is adapted to read resolved
node/producer edges instead of running its own actual-resolution ladder. Catalog attachment to
the graph is part of projection (the seam caveat from the research report).

**D8 — Projection is mechanical.** Calc node → `PipelineModule` (names via
`get_module_name`/`derive_module_type`; channels via `get_channel_name` on node IDs — spike
note: modules need `calc_def_qualified_name` for the registry template). Consumed attr node →
one `EntryPoint`; classification from value-site (`occurrence_override`/`definition_default` →
DESIGN_ATTRIBUTE vs LIBRARY_DEFAULT per contract; authored literal → USAGE_LITERAL, minted
consumer-local because an authored literal is its own source). Parameter groups derive from
node source files. Toposort over producer edges. `entry_point_groups` is a list;
`generate_registry` returns text.

**D9 — Diagnostics catalog.** The contract's D8 codes: `SI_SELF_BINDING`,
`SI_INDEXED_SOURCE_UNSUPPORTED`, `SI_EXPRESSION_SOURCE_UNSUPPORTED` (extraction-detectable,
already landed in `source_evidence.py`), plus elaboration-time `SI_OCCURRENCE_MISSING`,
`SI_OCCURRENCE_AMBIGUOUS`, `OVERRIDE_TARGET_MISSING`. Strict/lenient may change halt-vs-report,
never identity.

**D10 — Rejected alternative.** Consuming `extract_calculation_usages`' expanded population
with remap (the spike shortcut) was rejected for production: it keeps the legacy expansion
alive, which the deletion ledger requires dead, and inherits its def-relative inconsistency.

## Deletion ledger (executed at Item 6; authority for "one owner per responsibility")

From `.project/research/20260807-145336_elaborate-first-instance-graph-architecture.md`:
VBR + specialized-chain rewrite + self-named rescue (`pipeline_builder.py:204-645`),
aggregation scope re-derivation (`:646-877`), virtual calc-usage expansion
(`usage_extractor.py:248-626`), the backtracker resolution ladder (DFS edge discovery
re-sourced; toposort kept), the 21-key-form table (`producer_resolution.py`), the
supplied-value materializer (`supplied_values.py`), the OutputRegistry namespaces, the
group-deriver value backfill (`graph_builder.py:618-632`), and their wrong-oracle tests.

## Bets / risks

- **B1**: EXPRESSION-redefinition folding (D6) covers every corpus aggregation shape — the
  breadth learning tests (Item 5) falsify per shape; term-level evidence is already complete.
- **B2**: `constraint_lowering` adaptation (D7) is a narrowing, not a rewrite — its occurrence
  expansion is already index-based.
- **B3**: Node-ID positional stability (D1) is acceptable for the corpus — Item-6 semantic
  review sees any rename.

## Handoff

Item 5 implements this design breadth-first with per-shape learning tests and the dual-run
diff harness; Item 6 cuts over, executes the ledger, and lands snapshot = serialized instance
graph atomically.
