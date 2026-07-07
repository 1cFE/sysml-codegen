# Probe (iii) — F4 module drift: live path vs `input_resolver.py`, both directions

**Threshold (spec HARD-F4 probe iii):** any post-COST-PATTERN (`d6c725f..HEAD`) live-path
fix in graph_builder's aggregation resolution that is **absent** from the module counts as
material drift → a KILL.

## Live path = `_resolve_aggregation_input_channel` (graph_builder.py:1205)

The module (`input_resolver.py`) docstring names its mirror targets:
`_resolve_aggregation_input_channel()` and `_build_aggregation_module()`.

## Commit inventory, `d6c725f..HEAD`, `src/sysml_codegen/resolution/graph_builder.py`

```
21273b5 item5 Phase 3: Family 3 require-unique-or-warn at name-keyed lookups (INV-3)
89e6f80 UPSTREAM-FINDINGS: fix the 11 de-risk findings + staged plant-idiom support (#3)
```

Only two commits touched the file since the module's COST-PATTERN birth.

## Direct function-body diffs (d6c725f vs HEAD)

- `_resolve_aggregation_input_channel`: **byte-identical** (115 lines, `diff` empty).
- `_build_aggregation_module`: **unchanged** since birth.
- `_find_literal_redefinition`: changed by 21273b5 (Item 5) — added INV-3
  require-unique-or-warn on name-keyed LITERAL leaf collisions. This is **literal default-
  value propagation**, a different responsibility than channel resolution; the module never
  mirrored it (Strategy C follows CHAIN redefs to channels, it does not resolve literal
  defaults). Not a live-path resolution fix, so not drift.

## The two epic changes the orchestrator flagged

- **Item 8 reordered `_walk_aggregation_ast`** — that function lives in
  `extraction/hierarchy_resolver.py:386`, the extraction layer. It shapes the
  `aggregation_expressions` data that **both** resolution paths consume equally; it is
  upstream of the resolve split, not part of it. Reordering it changes neither path's
  resolution logic. Not drift between the paths.
- **Item 5 graph_builder family fix** (21273b5) — is `_find_literal_redefinition` (above),
  literal-value propagation, never in the module's mirror scope.

## Both-directions delta (birth-state, not drift)

- **Module → live:** the module carries Strategy B (`SysMLQNLookup` for `::` refs) and
  Strategy D (`DesignAttributeLookup`, no-op). The live path has neither. These are
  birth-state; the parity suite already documents Strategy B as a "known asymmetry" the
  backtracker reaches by a different route. Not a post-COST-PATTERN live-path fix.
- **Live → module:** no post-COST-PATTERN live-path fix exists to be absent.

## Verdict

**No material drift. NO KILL.** The live aggregation-resolution function is byte-identical
to its COST-PATTERN birth; zero live-path fixes have landed since, so none can be missing
from the module. The Item-8 and Item-5 changes the orchestrator named are, respectively,
extraction-layer (upstream of both paths) and literal-default propagation (never mirrored).
