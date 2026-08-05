# Initial Whole-Corpus Semantic-Source Census (SOURCE-IDENTITY Item 2)

**Date**: 2026-08-05 · **Branch**: `nested-override-tripwire` @ `fa9e0d0`
**Probe**: `probes/census_probe.py` (license-free; full per-fixture JSON in
`probes/raw/census.json`). This is the *initial* census the epic asks Item 2 for; the
*final* census against the corrected pipeline, with zero silent unknowns, is Item 6's.

## Method

For every fixture with a committed extraction snapshot (37), build the full pipeline
offline, then attribute each public entry point to its minting binding:

- **Path A** — per-consumer EP from a `LITERAL` binding that still names a written
  referent (`source_attribute_name` set): a stamped, reference-derived literal.
- **Path B** — per-consumer EP from a `REFERENCE` binding (lenient terminal miss).
- **authored literal** — `LITERAL` binding with no written referent: a genuine model
  literal, legitimately consumer-local.
- **converged** — EP keyed by a design attribute (captured or SVM-synthesized).
- **library default** — unbound-formal mint (per-usage by ADR-001 design).
- **other** — EXPRESSION bindings and unattributed remainder.

Fan-out grouping keys per-consumer EPs on (consumer-owner path, written leaf).
**Known limitation**: that key cannot see cross-owner duplicates — the solar
`pack_count` cell was found via the forensics pointer, not the sweep. The final census
must key on *recovered source identity*, which requires the Item 4/5 repair.

## Totals

**277 entry points** across 37 fixtures (all build):

| class | count | share |
|---|---|---|
| converged design-attribute | 123 | 44% |
| library default (unbound formal) | 58 | 21% |
| **Path A per-consumer mints (stamped)** | **37** | **13%** |
| **Path B per-consumer mints (lenient miss)** | **38** | **14%** |
| authored usage literal | 14 | 5% |
| expression / other | 7 | 3% |

27% of the corpus's public entry surface is model-derived per-consumer minting.

Reconstruction experiment over the 75 model-derived mints (candidate =
consumer-owner + written leaf, fallback owning-def QN + leaf, against **captured**
attributes — a lower bound, since SVM-synthesized attributes are excluded):
**35 reconstruct** (2 exact-occurrence, 33 def-default), **40 unresolved**, 0 ambiguous.

## Per-fixture census

| fixture | EPs | Path A | Path B | authored lit | converged | lib default | other | fan-out groups |
|---|---|---|---|---|---|---|---|---|
| agg_literal_probe | 0 | 0 | 0 | 0 | 0 | 0 | 0 | — |
| agg_localterm_probe | 2 | 0 | 1 | 0 | 1 | 0 | 0 | — |
| alias_agg_probe | 3 | 1 | 0 | 1 | 0 | 1 | 0 | — |
| attr_expr_probe | 16 | 0 | 0 | 0 | 16 | 0 | 0 | — |
| catf_mfe_model | 60 | 0 | 0 | 3 | 46 | 11 | 0 | — |
| chain_override_probe | 3 | 1 | 1 | 1 | 0 | 0 | 0 | — |
| chain_spike_model | 3 | 0 | 0 | 0 | 3 | 0 | 0 | — |
| constraint_inline | 1 | 0 | 0 | 0 | 1 | 0 | 0 | — |
| constraint_multi_instance | 1 | 0 | 0 | 0 | 1 | 0 | 0 | — |
| constraint_non_numerical | 1 | 0 | 0 | 0 | 1 | 0 | 0 | — |
| crosspart_rollup_twolevel | 2 | 0 | 2 | 0 | 0 | 0 | 0 | — |
| d38_caret | 1 | 0 | 0 | 1 | 0 | 0 | 0 | — |
| deep_cross_scope_probe | 7 | 4 | 0 | 0 | 1 | 2 | 0 | analyzer.baseline_value×3 |
| expression_binding_probe | 7 | 0 | 0 | 0 | 1 | 0 | 6 | — |
| fusion_tea | 31 | 16 | 0 | 2 | 10 | 3 | 0 | hif_plant.availability×2; hif_plant.gain×2 (+converged sibling); hif_plant.thermal_efficiency×2 |
| gate_a | 3 | 0 | 1 | 0 | 1 | 1 | 0 | — |
| gate_a_package_owner | 3 | 0 | 1 | 0 | 1 | 1 | 0 | — |
| ife_plant | 25 | 0 | 25 | 0 | 0 | 0 | 0 | driver.bank_energy×2 |
| invocation_binding_probe | 1 | 0 | 0 | 0 | 0 | 1 | 0 | — |
| issue22_model | 3 | 1 | 0 | 1 | 0 | 1 | 0 | — |
| modeled_default_fidelity | 6 | 0 | 0 | 0 | 3 | 3 | 0 | — |
| plant_value_shapes | 7 | 0 | 2 | 3 | 1 | 0 | 1 | — |
| plant_values | 5 | 0 | 0 | 0 | 4 | 1 | 0 | — |
| quoted_owner_formula | 2 | 0 | 0 | 0 | 2 | 0 | 0 | — |
| return_styles | 4 | 0 | 0 | 0 | 4 | 0 | 0 | — |
| retype_model | 4 | 0 | 0 | 0 | 2 | 2 | 0 | — |
| sample_model | 0 | 0 | 0 | 0 | 0 | 0 | 0 | — |
| self_named_binding_trap | 1 | 0 | 1 | 0 | 0 | 0 | 0 | — |
| self_named_rescue | 1 | 0 | 0 | 0 | 1 | 0 | 0 | — |
| shadowed_reference | 1 | 0 | 0 | 0 | 1 | 0 | 0 | — |
| shared_producer | 2 | 0 | 0 | 0 | 1 | 1 | 0 | — |
| sibling_channel_ambiguity | 2 | 0 | 2 | 0 | 0 | 0 | 0 | — |
| solar_battery_model | 60 | 13 | 0 | 2 | 15 | 30 | 0 | (cross-owner: battery_system.pack_count → +battery_bos.cost_model copy) |
| spec_chain_channel | 1 | 0 | 1 | 0 | 0 | 0 | 0 | — |
| spec_chain_twolevel | 3 | 0 | 1 | 0 | 2 | 0 | 0 | — |
| unresolvable_attr_probe | 1 | 1 | 0 | 0 | 0 | 0 | 0 | — |
| wi014_toy | 4 | 0 | 0 | 0 | 4 | 0 | 0 | — |

## Duplicate / fan-out register

One modeled source demonstrably mapped to multiple public fields at HEAD:

| source (owner.leaf) | fields | kind | fixture |
|---|---|---|---|
| hif_plant.gain | 3 (1 converged + 2 stamped) | Path A + constraint | fusion_tea |
| hif_plant.thermal_efficiency | 2 | Path A | fusion_tea |
| hif_plant.availability | 2 | Path A | fusion_tea |
| hif_plant.driver bank_energy | 2 | Path B | ife_plant |
| analyzer.baseline_value | 3 (incl. renamed `data_point`) | Path A | deep_cross_scope_probe |
| battery_system.pack_count | 2 (1 converged + 1 stamped, cross-owner) | Path A | solar_battery_model |

## Explicit unknown classes (preserved, not forced)

- **Cross-owner duplicates beyond `pack_count`** — the sweep's (owner, leaf) key cannot
  enumerate them; needs source-keyed re-sweep (Item 6, post-repair).
- **catf_mfe's 13 per-occurrence `inner_radius` attributes** — 13 distinct layer
  occurrences, *not* per-consumer mints (contra a loose reading of the forensics'
  "minted 13×"); whether the model chains them (producer channels) or intends 13
  independent inputs is unread.
- **EXPRESSION-binding EPs** (6 in expression_binding_probe, 1 in plant_value_shapes) —
  no dispatch path today; source identity of their operand references unexamined.
- **The 40 reconstruction-unresolved rows** (see `probes/raw/census.json` per-fixture
  `recon`) — cross-owner, consumer-relative dotted tails, and no-captured-attr cases.
- **Multi-occurrence def-default sharing** (ife chambers, fusion_tea driver pair) —
  per-occurrence fields observed; whether an un-overridden def default is one source or
  one per occurrence is an Item-3 ruling, not a census fact.
