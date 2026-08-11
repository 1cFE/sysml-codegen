# Provenance — `alias_agg_d5`

Authored 2026-08-11 for recovery plan **Gate 4C** (`.project/active/cutover-recovery/plan.md`),
as the exact-route replacement specimen for row **L-099** (alias-aggregation probe generation).

**Not a corpus fixture.** It joins no ledger and no 37-path corpus run.

## Why it exists

`alias_agg_probe` is corpus row 3, a ratified `expected-collapse`: its leaf cost model binds
`in base_cost = base_cost`, which the exact route refuses with `SI_SELF_BINDING`. The probe's
subject — quoted calc-def names surviving identifier derivation all the way to files on disk,
with an aggregation read both directly and through a chain alias — has no other fixture.

## The one difference against `alias_agg_probe`

The leaf's cost model binds `in base_cost_in = base_cost` (D-5 form). Nothing else moved:
the three quoted calc defs, the `[3]` widget array, `:>> total_cost = sum(widget.total_cost)`,
the chain alias `:>> reported_cost = total_cost`, and the two calc usages reading the
aggregation directly and through the alias are the probe's, verbatim.

## Hand-derived values

`base_cost = 50.0`, `markup_in` default `1.5` → each widget's `unit_cost = 75.0`.
Three widgets → `total_cost = 225.0`. `margin_rate = 0.15` → `margin = 33.75`.
`report_value = reported_cost = 225.0`.
