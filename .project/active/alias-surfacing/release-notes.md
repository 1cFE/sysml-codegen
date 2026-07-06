# Release Notes — Item 11: Derived-Attribute Alias Surfacing (SC-7)

**Epic:** UPSTREAM-FINDINGS Item 11 (last code item) · **Branch:** upstream-findings-epic

## Summary

The name a modeler gives a calc output with an EXPOSE_PURE derived attribute
(`attribute total_cost = cost_calc.cost`) now reaches generated output. Item 10 already
resolved the name→channel mapping for both EXPOSE shapes and stored it with provenance;
Item 11 surfaces that name:

- **On the graph** — a new serialized field `ComputationGraph.output_aliases`
  (`list[OutputAlias]`), each entry carrying the modeler's sanitized name, the canonical
  channel the value flows on, the instance path, and the shape.
- **In the pipeline YAML** — the modeler's instance-qualified name becomes the **output
  filename** on that channel's exit line.
- **Warning retired** — the graph builder's shape-A EXPOSE_PURE branch no longer fires
  Item 1's malformed-refs warning for the resolvable case.

Both shapes surface: **shape A** (part-def EXPOSE, via the `_scoped_alias` registry) and
**shape B** (part-usage EXPOSE, via the `expose_pure` `ChannelAlias`).

## What changed

### `ComputationGraph.output_aliases` (REQ-DM-09)

- New `OutputAlias` BaseModel (`resolution/models.py`): `alias_name`,
  `canonical_channel`, `instance_path`, `shape: Literal["part_def","part_usage"]`, plus
  an `output_filename` property (`{instance_path}__{alias_name}.json`).
- New field `output_aliases: list[OutputAlias]` — serialized (no `exclude`, contrast
  `fallback_entry_points`), stable-sorted by `(instance_path, alias_name)` (INV-5), every
  entry's channel validated to exist (INV-3). Built at the end of `build_computation_graph`
  from the two provenance-carrying sources; threaded through **both** build sites (the
  live `pipeline_builder` path and the snapshot `graph_rebuild` path).
- Schema rev landed per R1: doc 09 field list, REQ tags, verification-matrix rows, and a
  field-set conformance flip (`test_graph_assembly.py`, `test_data_models.py`).

### Exit-point filename override (REQ-PY-08)

- `generate_pipeline_yaml` builds a `canonical_channel → filename` map from
  `graph.output_aliases` (`_build_alias_filename_map`, first-wins over the sorted list)
  and passes it to `_build_exit_points`; the template renders `{{ exit.filename }}`.
- The exit **key** stays the canonical channel and the type token is unchanged, so
  REQ-PY-06 and the existing conformance tests need no change, and simkit's
  key-is-a-channel validation is a consumer-side backstop for INV-3.

### Shape-A reroute + warning retirement (REQ-CA-11)

- `_build_attribute_resolution_map` splits the EXPOSE_PURE branch on
  `is_on_part_definition`. Shape A takes a LITERAL fallback (identical to the old
  post-warning behavior — no in-repo FORMULA consumes a shape-A exposed name) and
  consults `_scoped_alias` for the warning: registered leaf → silent (resolves via Item
  10, surfaces via Item 11), unregistered → warns naming the real cause. Shape B is
  byte-identical; a genuinely unresolvable shape-B EXPOSE still warns at
  `graph_builder.py:796`.

## Output filename MOVE — downstream coordination

This is a **behavioral change, not baseline churn**: aliased channels' output files move
from `{channel}.json` to `{instance_path}__{alias_name}.json`. A consumer (e.g. a
fusion-tea harness) reading generated output by the old `{channel}.json` path sees the
move. The committed YAML baselines that change:

| Fixture | Alias (name) | Channel | Old filename → New filename |
|---------|--------------|---------|------------------------------|
| `attr_expr_probe` | `scale_result` | `…probe_design__scale_calc__result` | `…scale_calc__result.json` → `probe_design__scale_result.json` |
| `attr_expr_probe` | `half_vol` | `…probe_design__split__half` | `…split__half.json` → `probe_design__half_vol.json` |
| `attr_expr_probe` | `quarter_vol` | `…probe_design__split__quarter` | `…split__quarter.json` → `probe_design__quarter_vol.json` |
| `solar_battery` | `misc_hardware_cost` | `…solar_array__allocation_model__total_allocation` | `…total_allocation.json` → `solar_battery_plant.solar_array__misc_hardware_cost.json` |
| `wi014_toy` (new baseline) | `total_cost` | `toy_plant__demo_plant__cost_calc__cost` | (no prior YAML) → `demo_plant__total_cost.json` |

So **four exit filenames move in existing committed YAML** (`attr_expr_probe` ×3,
`solar_battery` ×1) and **one new committed YAML** (`wi014_toy`) shows the alias filename
from the start.

At the **graph** level (`output_aliases`), five committed fixtures now carry populated
entries: `attr_expr_probe` (3), `solar_battery` (1), `wi014_toy` (1), `ife_plant` (2),
`catf_mfe` (44). `ife_plant` and `catf_mfe` have no committed YAML baseline, so their
filename moves are not committed — but a live YAML render of those models would move the
aliased channels' filenames the same way.

### `solar_battery` correction (was mislabeled "no EXPOSE_PURE")

`solar_battery` carries a shape-A EXPOSE `misc_hardware_cost = allocation_model.total_allocation`
on `solar_array`. The spec's Baseline Regeneration §1 originally listed it among the
no-EXPOSE fixtures; that was wrong. Its stale pre-Item-10 snapshot was recaptured (the
approved SC-1 reconciliation) so the snapshot path surfaces the alias and stays
byte-identical to the live path.

### `catf_mfe` first-wins nested-collapse note

`catf_mfe` surfaces **44** shape-B `output_aliases` entries across **19** distinct
canonical channels. Three channels each carry more than one alias entry — `minor_radius`
(13 instances), `volume` (13), `pump_power` (2) — a pre-existing Item-10 characteristic
of the nested plant idiom (same bare `canonical_name` across sibling instances). All 44
entries stay in `output_aliases` for programmatic consumers; the exit-filename map is
first-wins per channel (`_build_alias_filename_map` over the INV-5-sorted list), so a
rendered YAML would show one deterministic filename per shared channel. Distinct
instance_paths give distinct filenames where the channels differ; INV-2/3/4 hold as
defined against the registry.

## agentic-mbse impact (recorded for Item 12; not built here)

- **What the EXPOSE name now does downstream.** The MODELING_GUIDE's EXPOSE-pattern docs
  should state that a modeler's EXPOSE_PURE name is no longer internal wiring convenience
  only — it **surfaces as a named output capture**: it lands on the graph
  (`output_aliases`) and becomes the output filename `{instance_path}__{alias_name}.json`
  on the exposed channel's pipeline-YAML exit line. This closes the modeling-assumptions
  §3 promise that "consumers bind to `subsystem.exposed_name`."
- **The name that surfaces is the sanitized `python_name`** (Item 5 / REQ-NC-06), not the
  raw SysML name — e.g. `'total cost'` surfaces as `total_cost`. Guidance should teach the
  sanitized form as the bound/observed name.
- **Both shapes are supported and self-documenting.** `output_aliases` tags each entry's
  provenance via `shape` — `part_def` (shape A) from the `_scoped_alias` registry,
  `part_usage` (shape B) from an `expose_pure` `ChannelAlias`. Canonical reference
  fixtures: `wi014_toy` (shape A, `total_cost`), `attr_expr_probe` (shape B,
  `scale_result`/`half_vol`/`quarter_vol`), `sibling_channel_ambiguity` (same-name
  collision → distinct instance-qualified filenames), `catf_mfe` (nested shape B at scale).
- **EXPOSE_COMPUTED still does NOT surface** and stays rejected (calc output + arithmetic).
  Redefinition (`:>>`) and design_override name surfacing are a BACKLOG follow-up (they
  resolve as channels but their names are not EXPOSE_PURE-sourced).
