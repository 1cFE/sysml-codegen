# Phase 0 verdict — unmatched-override predicate false-fire scan

**Date:** 2026-07-24. **Probe:** `unmatched_override_scan.py` (this directory).
**Corpus:** every fixture in `tests/conformance/conftest.py::SNAPSHOT_MODELS` (19 fixtures),
read from committed extraction snapshots (license-free).

**Gate:** every currently-clean fixture must produce ZERO fires. **Result: PASS** for the
shipped predicate (0 fires across all 19). The first candidate did not pass and was narrowed.

## The two candidates scanned

Both start from the same trigger: a demand whose `resolve_logical_demand` returns
`value is None` with `nonliteral=False` and `malformed_literal=False` — the silent
fall-through at `supplied_values.py:563-573`.

- **wide** — some entry in `design_overrides ∪ redefinitions` shares the demand's leaf
  attribute name.
- **tight (shipped)** — same, plus two narrowings:
  1. **shape gate:** the demand must be dotted `part_usage.attr` form (`_BindingTarget.form
     == "dotted"`). Only an instance-relative dotted demand can suffer the
     occurrence-vs-definition scope mismatch.
  2. **part-usage gate:** the override must also name the demanded part usage — either its
     `owning_part_qn` leaf equals the part usage, or its `target_path` contains it.

## Per-fixture fire counts

| fixture | demands | wide | tight (shipped) |
|---|---:|---:|---:|
| sample_model | 0 | 0 | 0 |
| solar_battery_model | 16 | 1 | 0 |
| catf_mfe_model | 76 | 0 | 0 |
| attr_expr_probe | 3 | 0 | 0 |
| chain_spike_model | 5 | 0 | 0 |
| issue22_model | 1 | 1 | 0 |
| expression_binding_probe | 3 | 0 | 0 |
| chain_override_probe | 1 | 0 | 0 |
| unresolvable_attr_probe | 0 | 0 | 0 |
| alias_agg_probe | 2 | 2 | 0 |
| wi014_toy | 6 | 0 | 0 |
| ife_plant | 22 | 0 | 0 |
| self_named_binding_trap | 1 | 0 | 0 |
| plant_values | 4 | 0 | 0 |
| plant_value_shapes | 4 | 0 | 0 |
| gate_a | 2 | 0 | 0 |
| gate_a_package_owner | 2 | 0 | 0 |
| agg_localterm_probe | 1 | 0 | 0 |
| shared_producer | 2 | 0 | 0 |
| **total** | **150** | **4** | **0** |

## What the 4 wide false fires were, and why the narrowing is honest

All four were `::` REFERENCE-form demands naming a **library definition**, not an instance:

- `solar_battery_model`: `SolarBatteryLibrary::'Solar Battery Plant'::capital_cost`
- `issue22_model`: `Issue22Library::WidgetAssembly::total_cost`
- `alias_agg_probe`: `AliasAggProbeLibrary::'Widget Assembly'::{total_cost, reported_cost}`

Each is an aggregation rollup target: the library def carries same-named `capital_cost` /
`total_cost` redefinitions on its sub-part defs, and the target itself resolves through the
aggregation path, not the supplied-value materializer. Nothing is lost, so warning here would
be the site-4 / D3-12 false-fire story again.

The shape gate alone (dotted-only) clears all four. The part-usage gate is kept as well: it is
what the BACKLOG root-cause coordinate actually exhibits (`target_path=['source','reading']`
against a demanded `part_usage='source'`), and it holds the predicate to "an override for
*this* attribute of *this* part usage exists but matched at no tier" rather than the looser
"some override anywhere shares the name."

## Positive control

`tests/fixtures/nested_occurrence_override_probe/` — the recorded coordinate — has **no
committed extraction snapshot** (it is expected to halt, so it was never captured), so it
cannot be scanned by this probe. The positive case is pinned instead by the Phase-1 unit test,
which constructs the coordinate verbatim from the BACKLOG `[NESTED-OCCURRENCE-OVERRIDE]` entry
(`owning_part_qn='nested_occurrence_override_probe__Design__panel'`, `attribute_name='reading'`,
`target_path=['source','reading']`, LITERAL 80.0, demanded scope `..._the_design__panel`).

## Supporting change

`_BindingTarget` gained a `form: Literal["dotted","reference","bare"]` field, set by
`_binding_target`'s three branches. Diagnostics only — no resolution tier reads it. Without it
the dotted and reference forms are indistinguishable at the warning site, and the predicate
cannot reach zero false fires.
