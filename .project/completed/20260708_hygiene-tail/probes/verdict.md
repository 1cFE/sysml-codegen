# Phase 0 Verdict: D3 Hygiene Tail

**Date:** 2026-07-07
**Method:** per-site reproduce probe (`probes/probe_site*.py`, all offline, no license)
+ corpus-scan gate over the 15-fixture `SNAPSHOT_MODELS` list (`tests/conformance/conftest.py`).

---

## Site 1 — loader `.get` load-bearing fields (`snapshot/loader.py`)

**Reproduce:** confirmed by construction (`probes/probe_site1_loader.py`). Deleting
`python_type`, `binding_type` (from `AttributeInfo`) or `parent_part_path`,
`qualified_name`, `owning_part_def_qn` (from `CalcUsageData`) silently substitutes a
degraded default with no diagnostic today.

**Corpus scan:** 0 hits — no `SNAPSHOT_MODELS` fixture (attribute_info, calc_usage, or
design_attribute dict) is missing any of these fields. **INV-6-safe for all fields as
WARN or raise.**

**Disposition (per field), settled:**
| Field | Kind | Disposition | Reason |
|---|---|---|---|
| `python_type` | type | WARN | benign-leaning type default (`"Any"`), importable-but-flagged |
| `binding_type` | wiring | WARN | drops a binding to `UNBOUND` — flagged, not fatal to load |
| `parent_part_path` | scoping | WARN | scoping degradation, importable |
| `owning_part_def_qn` | scoping | WARN | scoping degradation, importable |
| `qualified_name` (calc_usage, `:327`) | **keying** | **RAISE** | mis-keys the registry — corrupts wiring downstream, not a degraded-but-usable state |
| `qualified_name` (design_attribute, `:343`) | **keying** | **RAISE** | same — feeds `DesignAttributeData.qualified_name`, used as a registry/alias key |

Benign majority (`is_input`, `is_output`, `description`, `unit`, `source_line`,
`is_optional`, `sysml_type`, `default_value`, list fields) is untouched — confirmed by
re-reading `_deserialize_attribute_info`/`_deserialize_calc_usage`/
`_deserialize_design_attribute`; those defaults don't change wiring, keying, or type.

---

## Site 2 — aggregation-compile `.replace()` collision (`resolution/graph_builder.py`)

**Reproduce:** confirmed on a hand-built `ScopedAggregationData` fixture
(`probes/probe_site2_agg_replace.py`) with two `SingletonTerm`s `cost` / `cost_total`.
Compiled output: `'inputs.cost + inputs.inputs.cost_total'` — the exact corruption the
spec describes. **Real bug, not exotic.**

**Corpus scan:** 0 hits — no `SNAPSHOT_MODELS` aggregation expression currently has a
nested-name ref pair. **Fixing the mechanism is byte-identical-safe on the whole
covered corpus** (nothing currently exercises the collision path).

**Disposition:** **FIX** (not reclassify — L2-1's spec-review correction holds: this
reproduces cleanly on a realistic modeling shape, just not yet in the covered corpus).
Mechanism: replace the substring `.replace()` loop with a word-boundary
(`re.sub(r'\bref\b', ...)`) substitution so `cost` cannot match inside the already-
substituted `inputs.cost_total`. No diagnostic needed — this is a correctness fix at
the compile choke, and it doesn't change output for any covered (disjoint-ref) model.

---

## Site 3 — `type_map` "Any" exit-point skip (`generation/registry.py`)

**Reproduce (unit):** confirmed — a constructed single-output module with
`python_type="Any"` is silently skipped by `_collect_exit_point_primitive_types`
(`probes/probe_site3_registry.py`).

**Reproduce (reachability):** 0 hits — every `SNAPSHOT_MODELS` built graph's
single-output (`field_name="root"`) exit point has `python_type` in
`{float,int,str,bool}` today. **Latent-only on the current corpus.**

**Coupling to Site 1:** confirmed independent per spec L1-1 — `"Any"` is also minted
live at `extractor.py:492`/`data_models.py:70`, with no loader involved. The Site-1 fix
(above) only ever touches the *loader's* `.get("python_type", "Any")` fallback — it
does not and cannot make Site 3's live-sourced `"Any"` shape unreachable. Site 3 keeps
its own diagnostic, as the spec predicted.

**Disposition:** **HARDEN as a latent-only tripwire.** Add a `logger.warning` in the
`else` branch of `if wrapper:` for an unmapped `python_type` on a `field_name="root"`
exit point. INV-6-safe (0 real-corpus fires); the fires-on-shape test is pinned with a
constructed fixture (no real fixture currently exercises the shape), consistent with
the plan's fallback.

---

## Site 4 — Phase-4 transitive-alias no-`else` (`orchestration/output_registry_builder.py`)

**Reproduce (unit):** confirmed — a `DesignAttributeData` with a transitive default
(`"nonexistent_module.nonexistent_channel"`) that fails all three lookups produces no
warning today (`probes/probe_site4_output_registry.py`).

**Corpus scan — MATERIAL FINDING, changes the disposition.** Unlike the other three
sites, this one does **not** come back clean. Running the *same* three-lookup
predicate (`instance_attr_to_channel` / `scoped_lookup` / `alias_lookup`) that Phase 4
uses, over every `SNAPSHOT_MODELS` design attribute with `is_transitive_default(...)`
True, finds **5 real, currently-unresolved transitive defaults** on the covered
corpus, generating clean today:

- `solar_battery_model`: `SolarBatteryLibrary__Solar_Array__misc_hardware_cost` → `'allocation_model.total_allocation'`
- `wi014_toy`: `toy_plant__Toy_Plant__total_cost` → `'cost_calc.cost'`
- `ife_plant`: `IfePlantLib__Coil__volume` → `'volume_calc.volume'`
- `ife_plant`: `IfePlantLib__Ife_Power_Plant__lcoe` → `'lcoe_calc.lcoe'`
- `plant_values`: `PlantValuesLib__Power_Plant__plant_cost` → `'cost_calc.plant_cost'`

Root cause: these `default_value`s are written in **short (leaf-instance) dotted
form** (`"cost_calc.cost"`), but the three lookup keys Phase 4 checks are all
**full-path** forms (`instance_attr_to_channel`/alias keyed by the calc usage's full
EQN, e.g. `"toy_plant__demo_plant__cost_calc.cost"`; `scoped_lookup` keyed by
design-prefix-stripped dotted EQN, e.g. `"demo_plant.cost_calc.cost"`). None of the
three ever match a bare `"cost_calc.cost"`. This is a real, live gap — not a synthetic
edge case — confirmed independently against the real `OutputRegistry` built for each
fixture (`registry.scoped_lookup`/`alias_lookup` both return `None`), not just my
scan's re-implementation.

**A mechanical sibling-copy WARN (mirroring Phase 2/3) would fire on these 5 fixtures
today, breaking INV-6 [HARD].** The corpus-scan gate is doing exactly its job here —
this is the site the plan expected to be "clean," and it isn't.

**This exact tension was already discovered and deliberately deferred elsewhere in
the codebase**, for the sibling drop in `analysis/parameter_groups.py`
(`_derive_from_design_attributes`, lines ~672-682): a present-but-unparseable design
attribute default (the same short-dotted-path shape) is silently dropped from the
derived JSON parameter list, with a comment explicitly citing SC-5/D3-12 and stating
that a naive "unparseable default" WARN "over-fires on legitimate chain/reference
defaults... resolved elsewhere, breaking INV-6," and that scoping it correctly "needs
the EP-omission membership check across the full derivation" — deferred, and never
filed in BACKLOG or the discovery register.

**Impact check:** searched every `calc_usage` binding's `source_path` across the
affected fixtures for a reference to any of the 5 orphaned names
(`misc_hardware_cost`, `total_cost`, `volume`, `lcoe`, `plant_cost`) — none found.
Nothing in the current corpus consumes these particular aliases downstream, so the
gap has no observable effect on any covered model's generated output *today*. That is
exactly why it is currently invisible and exactly why a corpus-scan-blind mechanical
fix would have shipped a false-fire.

**Disposition:** **RECLASSIFY.** Per R4 ("a non-reproducing-cleanly-on-corpus site is
not forced"), Site 4's mechanical "add the missing `else`, mirror Phase 2/3" fix is
**not implemented in this item** — it is not INV-6-safe as scoped, and correctly
scoping it (an EP-omission / cross-derivation membership check, per the existing
deferred comment) is design-level work spanning two modules
(`output_registry_builder.py` Phase 4 and `parameter_groups.py`
`_derive_from_design_attributes`), not a single-choke mechanical hygiene fix. Filed to
`BACKLOG.md` as `[D3-HYGIENE-TAIL-SITE4-TRANSITIVE-ALIAS]`, connecting both sites and
this corpus evidence. No code change to `output_registry_builder.py` in this item.

---

## Summary

| Site | Reproduces | Corpus-scan | Disposition |
|---|---|---|---|
| 1 (loader) | Yes, by construction | 0 hits (all fields) | HARDEN — WARN (4 fields), RAISE (`qualified_name`, keying) |
| 2 (`.replace`) | Yes, real shape | 0 hits | FIX (word-boundary substitution) |
| 3 (`type_map`) | Yes (unit); latent on corpus | 0 hits | HARDEN — WARN, latent-only tripwire |
| 4 (Phase 4) | Yes — **on 5/15 real fixtures** | **5 hits** | **RECLASSIFY** — not INV-6-safe as scoped, re-filed |

3 of 4 sites harden/fix in this item. Site 4 reclassifies with a concrete, evidenced
reason and a named BACKLOG pointer — an honest R4 outcome, not a forced fix.
