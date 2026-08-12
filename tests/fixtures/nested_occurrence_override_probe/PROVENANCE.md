# Provenance — the C19 repair case

**Read the route first.** On the exact identity route this fixture is a *passing* case: the
`80.0` reaches both consumers and the package generates, seals, and executes in real TEAx.
`tests/execution/test_c19_nested_occurrence_teax.py` proves that on all three public routes
(live, in-place v6 snapshot, relocated v6 snapshot), and
`tests/fixtures/nested_occurrence_override_probe/instance_graph_snapshot.json` is the
committed envelope the two snapshot routes read.

Everything below the next heading describes the **retiring string-resolution route**, where
the same fixture halts. It is kept as the recorded root cause of what the exact route fixed,
not as a description of what the product does.

## The string route's failure (historical, pin `7526665`)

Permanent reproducible coordinate for a **general supplied-value gap**: a `:>>` override on a
usage nested inside an *instantiated* part def is captured definition-relative and never
expanded to its occurrence path, so its literal is lost on **both** the calc and the
constraint resolution paths. Authored per owner ruling 2026-07-20 (Item 13 composed proof,
case-18 addendum, Option A) — plant-idiom style, so the gap has a standing test coordinate.

On the string route this fixture **halts** at generation. It pinned a filed backlog gap
(Item-10 occurrence-materialization family); see `.project/backlog/BACKLOG.md` for what
remains of that family beyond this shape.

## The shape

`part def Panel` owns `assert constraint within : 'Within Limit' { in v = source.reading; }`
and a calc `noop { in x = source.reading; }`. The redefining usage is nested one level deep:

```
part def Design {
    part panel : Panel {
        :>> source.reading = 80.0;
    }
}
part the_design : Design;
```

This is identical to the canonical `constraint_def_owned_redefining` fixture **except** the
redefining `panel` usage lives inside `part def Design` (instantiated as `part the_design`)
rather than directly at package level.

## Root cause (verbatim coordinates, pin `7526665`, licensed)

- **Override captured definition-relative:**
  `owning_part_qn = 'nested_occurrence_override_probe__Design__panel'`,
  `attribute_name = 'reading'`, `redefinition_type = LITERAL`,
  `target_path = ['source', 'reading']`, `literal_value = 80.0`.
- **Demand resolved occurrence-relative:** constraint owner instance
  `nested_occurrence_override_probe__the_design__panel`;
  `_binding_target('source.reading', '..._the_design__panel')` →
  `qn = '..._the_design__panel__source__reading'`, `part_usage = 'source'`, `attr = 'reading'`.
- `supplied_values._match_override` (tier-1 dotted branch) requires
  `ov.owning_part_qn == instance_scope`; `Design__panel` != `the_design__panel`, so the literal
  is never found. Tier 2a also misses: `usage_type_map` is definition-keyed
  (`('..._Design','panel') -> '..._Panel'`) and carries no entry for the occurrence
  `the_design`, so there is no occurrence -> definition bridge available to the materializer.

Observed at generation:

```
INFO: supplied-value materializer scanned 1 referenced bindings: 0 literal applied, 0 non-literal skipped.
ERROR: Code generation failed: nested_occurrence_override_probe__the_design__panel.v:
  unresolved actual 'source.reading' (strict mode: no fallback, no entry-point synthesis — INV-2).
  Attempted: scoped_prefixed, scoped_deindexed, scoped_bare, alias_prefixed, alias_deindexed,
  scoped_alias_prefixed, scoped_alias_deindexed, structured_alias_unscoped,
  structured_alias_deindexed, alias_bare, sysml_qn, direct_channel, scope_climb,
  occurrence_materialized_qn, target_qn, owner_def_qn
```

The strict resolver is correct — the design attribute it needs is simply absent from the index
because the materializer could not resolve the def-relative override against the occurrence-
relative demand. The calc binding `in x = source.reading` loses the same value (it would fall
to a manual-required entry point were the constraint not halting first); the gap is not
constraint-specific.

## Why the string route did not fix it

The contract row 18 mandates only "definition-owned assert through redefining usage," which the
flat `constraint_def_owned_redefining` fixture satisfies faithfully. The occurrence-expansion
of overrides nested under an instantiated def is a broader capability (calc + constraint) owned
by the Item-10 occurrence-materialization family; forcing it into a byte-clean Item-2 addendum
at the epic's finish line is the blast-radius mistake the stop rule exists to prevent. Filed to
backlog instead.
