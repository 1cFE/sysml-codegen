# Release Notes — Item 10: Cross-Part Channel Wiring (SC-5 stage 2)

**Epic:** UPSTREAM-FINDINGS Item 10 · **Branch:** upstream-findings-epic

## Summary

Cross-part calc channels now wire from generated code alone. A calc in one part
that reads an output produced in another part — the plant idiom — previously fell
through resolution and either dropped the input or aborted generation at the V11
params-coverage check. Item 10 wires four cross-part shapes end to end:

- **Multi-hop EXPOSE** (`magnet_volume_total = tf_coil.volume_calc.volume`) — the
  catf_mfe and ife_plant `cryo_load.magnet_volume` pins now resolve to the real
  `tf_coil` volume channel (stage a).
- **Part-def EXPOSE / shape A** (`total_cost = cost_calc.cost` on a part def) — the
  consumer resolves per instance via a structured scoped alias (stage a, #4/#1).
- **Specialized-def `:>>` chain** (`gamma → lcoe`) — a nested calc output reached
  through a retyped part's redefinition chain (stage b, single- AND two-level).
- **Sibling disambiguation** and **self-named-binding rescue** (stage b).

## What changed

### Stage (a) — multi-hop EXPOSE and part-def scoped aliases

- **`reference_chain` capture (REQ-CA-10).** A pure `FeatureChainExpression` derived
  attribute now carries its full dotted segments (`["tf_coil","volume_calc","volume"]`).
  Additive snapshot field, no `SNAPSHOT_FORMAT_VERSION` bump — old snapshots degrade
  to `None` → FORMULA (today's behavior).
- **Tentative-then-confirm classification (REQ-CA-10).** A multi-hop chain is tagged
  `EXPOSE_CHAIN_TENTATIVE`, then a Phase-3b transitive walk over `reference_chain`
  finalizes it to EXPOSE_PURE (registering the real transitive channel) or reverts it
  to FORMULA. No tentative survives to a reader (INV-F raises).
- **Part-def EXPOSE scoped aliases (REQ-CA-03 revised, REQ-BT-11).** A part-def-level
  EXPOSE (shape A) expands per design instance into a structured `_scoped_alias`
  namespace, and the backtracker reads it by splitting the consumer `source_path` at
  the last dot. This discharges the Item-1 REQ-CA-09 malformed-refs deferral.
- **Offline == live (D-C).** The confirm walk is reconstructed on snapshot load, so a
  multi-hop pin wires to the SAME channel offline and live (a prior gap resolved the
  offline pin to a first-wins collision — a lying sim — now fixed).

### Stage (b) — precedence resolver and companion mechanisms

- **Specialized-def `:>>` precedence resolver (REQ-VBR-10).** `_rewrite_specialized_chain`
  rewrites a `part_usage.attr` CHAIN binding through the retyped part's specialized-def
  `:>>` chain (three-tier merge: usage override > specialized-def `:>>` > base def). This
  is the `gamma → lcoe` edge.
- **Sibling disambiguation (REQ-BT-11 / D-D).** A consumer binding `chamber_b.power` with
  two same-type siblings now resolves to the correct instance-scoped channel via a
  consumer-scope prepend, never first-wins-colliding on `chamber_a`.
- **Self-named-binding rescue (REQ-VBR-10 / D-E).** A self-named `in x = x` whose outer
  same-named EXPOSE resolves is rewritten to the upstream channel; with no resolvable
  upstream it is left as-is (the `self_named_binding_trap` negative — still a modeling
  error, and now the sole home for the mechanism-D FAIL check).

### Two-level specialization (Phase 8 — the real fusion-tea shape)

The single-level `spec_chain_channel` fixture puts the consumer calc AND the `:>>` retype
on one def. The real fusion-tea `hif_plant` is **two-level**: the consumer `lcoe_calc` is
declared on the base def `'IFE Power Plant'`, while the retype `part :>> driver : 'HIF
Driver'` lives on a part USAGE (`part hif_plant : 'IFE Power Plant' { part :>> driver :
'HIF Driver' }`). Two changes wire it:

- **Usage-level retype indexing (REQ-LVP-09).** `_index_usage_level_retypes` indexes the
  usage-level retype into `usage_type_map` keyed by the container instance QN
  (`('...hif_plant','driver') -> 'HIF Driver'`). Limited to GENUINE retypes (target
  differs from the base-declared type), so value-only `:>>` overrides are excluded and
  every non-two-level snapshot stays byte-identical.
- **Instance-aware type-select (REQ-VBR-11).** `_rewrite_specialized_chain` tries the
  consumer INSTANCE's path key before the declaring-def key, so it reaches `'HIF Driver'`
  where the declaring base def sees only `'IFE Driver'`.

## Channel / EQN changes

- **catf_mfe:** `cryo_load.magnet_volume` now wires to
  `CATFMFERadialBuild__catf_radial_build__tf_coil__volume_calc__volume`
  (was a dangling fallback entry point). catf pipeline baseline regenerated (one wiring
  flip + execution reindex).
- **ife_plant:** the shape-4 `cryo_load.magnet_volume` pin leaves `EXPECTED_UNCOVERED`
  (now empty).
- **fusion-tea `gamma → lcoe`:** `hif_plant__lcoe_calc` input `driver_cost_constant` moves
  from an unwired library-default entry point to a `module_output` producing channel
  **`hif_plant_pkg__hif_plant__driver__meier_cost__gamma`**. Downstream coordination: the
  lcoe driver-cost input is now fed by the Meier `gamma` output channel, not a JSON param.

## fusion-tea coordination (truthful status)

- **SC-2 met at the graph level.** On `generate --models ~/1cfe/fusion-tea/models`, the
  `gamma → lcoe` edge is present in the ComputationGraph from generated wiring alone
  (`driver_cost_constant` left the V11 offender list; count 11 → 10). Confirmed by direct
  graph inspection, not by a written YAML — see below.
- **The full fusion-tea YAML does NOT yet emit.** Generation still aborts at V11 on **10
  other** unresolved cross-part bindings on `lcoe_calc`/`recirc_calc` (`driver.efficiency`,
  `driver.energy`, `driver.lifetime_shots`, `chamber.blanket_energy_multiple`,
  `chamber.yield_cost_constant`, `target_factory.cost_per_target`, plus the separate
  `hif_driver_instance` driver). These are broader plant-wiring gaps beyond Item 10's
  SC-2 scope; they are pre-existing and untouched by this change (INV-A additive).
- **Workarounds STAY upstream for now.** Because the whole-model YAML does not yet
  generate, the fusion-tea `hif_driver_instance` scaffold and the two-pass gamma feedback
  in `run_anchors.py` are NOT yet deletable. The `gamma → lcoe` edge that those
  workarounds stood in for is now wired, but the remaining 10 cross-part inputs must
  resolve before the generated pipeline can replace the hand-plumbing. Tracked as a
  BACKLOG follow-up.
- **Run-C anchor** ($270.12/MWh lcoe, rel-1e-6, γ=$68.247/J) stays **recorded, not
  reproduced** in-repo: it is a fusion-tea-harness computation (teax simkit + hand-built
  input JSONs + two-pass gamma feedback), never an in-repo gate. The in-repo SC-2 gate is
  the graph edge plus the `spec_chain_twolevel` pin flip.

## agentic-mbse impact (recorded for Item 12; not built here)

- **Reference shapes** for the MODELING_GUIDE: the five Item-10 fixtures are the canonical
  cross-part references — `wi014_toy` (part-def EXPOSE / shape A), `spec_chain_channel`
  (single-level specialized `:>>` chain), `spec_chain_twolevel` (two-level: retype on a
  part usage, consumer on the base def), `sibling_channel_ambiguity` (same-type siblings),
  `self_named_rescue` (positive mechanism D) with its `self_named_binding_trap` negative.
- **Supported cross-part shapes** to document: multi-hop EXPOSE; part-def EXPOSE expanded
  per instance; specialized-def `:>>` chain (single- and two-level); sibling
  disambiguation by instance scope.
- **The redefinition-precedence rule:** usage override > specialized-def `:>>` > base def.
- **The value-carrying redefinition idiom is the BARE `:>> attr = value` form** (parses as
  ReferenceUsage, captured). `attribute :>> attr = <expression>` is a **known-unsupported**
  shape (the AttributeUsage redefinition is silently dropped at extraction,
  `hierarchy_resolver` `_extract_single_redefinition`). Item-12 guidance should teach the
  bare form and add a validation warning when an `attribute :>>` carries an expression RHS
  (D-F). fusion-tea uses only the bare form (the real gamma edge is
  `hif_driver.sysml:82 :>> cost_per_joule = meier_cost.gamma`), so no extraction relaxation
  was needed in this item.
- **The self-named-binding FAIL check** (mechanism D) with the `self_named_binding_trap`
  negative fixture.
