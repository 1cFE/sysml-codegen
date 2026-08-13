# CATF all-65 constraint disposition — RULED

**Status:** RULED — owner ruling 2026-08-13 converted this table to authority. Rows the owner
approved without change are `[AGENT] (ratified by owner, 2026-08-13)`. Owner-originated items are
marked `[OWNER 2026-08-13]` where they appear: the two tolerance rulings (A3, A9), the item5-F1
SC-3 amendment authorization, and the O2/O5 rulings. The owner's structural amendment (basis
cells on A5/A6/A7 + the derivation doc-comment obligation) is applied in place below.
**Item:** CONSTRAINT-SEMANTICS Item 5 (`spec.md`, SC-1)
**Fixture under disposition:** `tests/fixtures/catf_mfe_d5`
**Row authority:** `tests/expectations/constraint_population/catf_mfe_d5.json` — 65 usages, joined 1:1
**Created:** 2026-08-13 (proposal) · **Ruled:** 2026-08-13

---

## The ruling in force

All 65 rows are approved. **Amended by the D-S1/D-S2 ruling (option 3, adopted as recommended —
[AGENT] (ratified by owner, 2026-08-13)):** design-stage probes measured that A9's assert-band
and 26 of 27 A5/A6 radius derivations refuse against the current projection
(`SI_RENDERING_COLLISION`; unit-lane defect, verified in code). Item 5 lands on the landable
shape now: **A5, A6, A9 are retained as visible plain usages, dispositioned blocked-by-defect in
this table and PROVENANCE only — no new catalog reason token; their catalog rows stay within
Item 2's closed vocabulary.** Their ruled basis cells and A9's 1%-relative tolerance remain in
force as recorded intent for the follow-on item that upgrades the derivative once the unit-lane
defect fix lands (filed as its own epic item).

The accounting identity, restated as a mechanical consequence of that ruling (restatement
authorized by the owner, not a re-disposition):

> **65 = 58 carriers + 7 named deletions** (5 derive-instead: A1, A4, A7, A8, C37;
> 2 placeholder deletions under the O2 ruling: C21, C28).

Every deletion is a named record in the derivative's PROVENANCE citing its authorizing table row;
nothing is a carrier or vanishes silently. The frozen-twin half of SC-3 (65 carriers on
`catf_mfe_d5` itself, proved by Item 2) is untouched.

**Derivation documentation obligation [OWNER 2026-08-13, structural amendment]:** each of the
seven derivations carries a doc comment recording the undirected relation and stating that the
direction is a **chosen basis, not physics** — and the PROVENANCE deletion record repeats it. The
relation intent must survive the deletion; a permanently-unassessed catalog row is the wrong home
for it, documentation on the derivation is the right one.

## Unit-check column — status under the ruling

**The toolchain does not check units on constraint bindings.** A unit written on a binding
(`in tol = 0.05 [m];`) contributes the number and nothing else; a bound formal takes its operand
category from the constraint definition's declared type, so the annotation never reaches the
dimension check. A band that compares a length against a time is admitted silently
(`docs/architecture/modeling-assumptions.md` §8; Item 4 measured limit 1).

So the unit-check column is **human-verified, not toolchain-verified**. It has exactly two
checkpoints: the owner's sign-off (given 2026-08-13 with this ruling) and design review
re-checking it against the authored source. A later reader must not read a filled-in unit cell as
evidence that anything machine-checked it.

**Worse in this fixture than usual.** Every CATF attribute is a bare `Real`. Units live in
end-of-line comments (`// MW - Fusion power`) and doc text, never in the model. The units in this
table are read off those comments and off the physics. Treat the column as my claim about intent,
not as a fact recovered from the model.

## Vocabulary

Intent classes are the four-way equality taxonomy (`agentic-mbse docs/patterns/constraints.md`;
authority copy `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md`):

| class | intent | the move |
|---|---|---|
| 1 | structural identity — `b` **is** `a` by construction | derive `b`; do not constrain it |
| 2 | cross-check of two independently computed values | loose, physically motivated band |
| 3 | feasibility gate | one-sided inequality; if it must *equal* a value, fix it as an input |
| 4 | composition closure | derive the last term; else a banded check |

Dispositions used: `derive-instead` (the authored usage is deleted and a derivation replaces it),
`assert-one-sided`, `assert-band`, `inapplicable` (an explicit `@inapplicable:` disposition, no
attachment), `awaits-capability` (Item 6 builds calc-def gate attachment; nothing is built here),
and `delete-placeholder` (**[OWNER 2026-08-13]**, O2 ruling only — not a disposition the proposal
could offer). The D-S1/D-S2 ruling added `blocked-by-defect` (**[AGENT] (ratified by owner,
2026-08-13)**): the usage is retained as a visible plain constraint; the ruled target form stays
recorded intent for the post-fix follow-on; the marking lives in this table and PROVENANCE only —
the catalog row uses Item 2's existing vocabulary.

The same recording mechanism was applied to B1–B5's `inapplicable` rows on 2026-08-13
(**[AGENT]**, orchestrator-applied, flagged for owner review): the disposition is unchanged,
but the `@inapplicable:` marker cannot reach the domain on their inline-predicate shape, so
the disposition is recorded in this table and PROVENANCE rather than in a source marker. See
"B1–B5 recording mechanism" in Group B.

---

# Group A — 9 instance-reaching gates

These nine are owned by part usages in `designs/catf_mfe/`. They reach instances today and catalog
as `excluded, unassessed form`. Eight of the nine BLOCK under an assert probe; only `ViabilityCheck`
ADMITs (research §3).

| # | usage | file:line | current predicate (verbatim, abridged where noted) | class | proposed disposition | target form | tolerance | unit-check (human) | survives? |
|---|---|---|---|---|---|---|---|---|---|
| A1 | `CATFMFEPhysics::catf_physics::PowerBalanceConsistency` | `designs/catf_mfe/physics.sysml:125` | `alpha_neutron_split.p_alpha + alpha_neutron_split.p_neutron > p_fusion * 0.999 and … < p_fusion * 1.001` | 1 | **derive-instead** | Delete. `AlphaNeutronSplit` splits `p_fusion` by `3.52/17.58` and `14.06/17.58`, which sum to exactly 1 — conservation is true by construction, and the band checks arithmetic the generator already guarantees. Derive `p_neutron := p_fusion - p_alpha` in the calc def (same edit as C37) and the check has no work left. | n/a | power, MW both sides | **no** |
| A2 | `CATFMFEPhysics::catf_physics::ViabilityCheck` | `physics.sysml:134` | `p_electric_net_out > 0` | 3 | **assert-one-sided** | `assert constraint net_power_viable : PositiveQuantity { in value = p_electric_net_out; }` over `constraint def PositiveQuantity { in value : Real; value > 0 }`. Already one-sided, already ADMITs, no rewrite of intent — only the `assert` prefix and the bindings-only shape. **Formal renamed `value` → `quantity` as authored** (Item 5 finding 6-B): `value` is a reserved generated local in predicate scope, so this spelling cannot generate. An amendment to an agent-provisional name under **O7** (library names are provisional and design-owned) — not a re-disposition; no ruled content moves. Recorded in `tests/fixtures/catf_mfe_gated/PROVENANCE.md` §1. | none — the `0` floor is the authored physical zero, not a band | power, MW; threshold `0` is dimensionless-safe as a `real`/`real` comparison | **yes** |
| A3 | `CATFMFEPhysics::catf_physics::ReasonableParasiticTotal` | `physics.sysml:142` | `net_electric.p_parasitic_total > gross_electric.p_electric_gross * 0.10 and net_electric.p_parasitic_total < gross_electric.p_electric_gross * 0.90` | 3 | **assert-band** | `assert constraint parasitic_fraction_ok : FractionWithinBand { in part_power = net_electric.p_parasitic_total; in whole_power = gross_electric.p_electric_gross; in lower_frac = …; in upper_frac = …; }`; predicate `part_power > whole_power * lower_frac and part_power < whole_power * upper_frac`. Chains move to binding position, which is supported. | **[OWNER 2026-08-13]** lower `0.10`, upper `0.90` [dimensionless fractions] — the authored values, confirmed as a **plausibility envelope**. Recorded promise: this band does not gate viability; viability is A2's job (`p_net > 0`). | power, MW on both compared sides; the two band edges are dimensionless fractions | **yes** |
| A4 | `CATFMFERadialBuild::catf_radial_build::TotalRadiusConsistency` | `radial_build.sysml:605` | `bioshield.outer_radius == 8.55 [m]` | 3 | **derive-instead** | Delete. Class 3's own rule: a quantity that must equal a value is fixed as an input, not searched for and then constrained. `bioshield.outer_radius` is already the literal `8.55 [m]` (`radial_build.sysml:558`), so the gate asserts a literal against itself. It also carries the `[m]`-literal elaborator defect (research §6). | n/a | length, m | **no** |
| A5 | `CATFMFERadialBuild::catf_radial_build::LayerContinuity` | `radial_build.sysml:612` | 13-term `and`: `plasma_region.inner_radius == axis_region.outer_radius and … and bioshield.inner_radius == lt_shield.outer_radius` | 1 | **blocked-by-defect** (was derive-instead; D-S2 ruling 2026-08-13 — retained as a visible plain usage until the unit-lane fix lands; the derivation below stays recorded intent) | Ruled intent: delete. Each layer's `inner_radius` **is** the previous layer's `outer_radius` — that is the definition of a radial build, not a check on it. Derive each `inner_radius` from the layer below. Design decides the source edit; it touches 13 attribute declarations. **Basis [AGENT] (ratified by owner, 2026-08-13):** free parameters are the axis root radius plus the 14 layer thicknesses; all other radii derived. A parameterization is an engineering decision carrying owner sign-off, never a side effect of classification. | n/a | length, m | **yes** (until fix; then deleted per ruled intent) |
| A6 | `CATFMFERadialBuild::catf_radial_build::RadiusThicknessConsistency` | `radial_build.sysml:630` | 14-term `and`: `axis_region.outer_radius == axis_region.inner_radius + axis_region.thickness and …` | 1 | **blocked-by-defect** (was derive-instead; D-S2 ruling 2026-08-13 — retained as a visible plain usage until the unit-lane fix lands; the derivation stays recorded intent) | Ruled intent: delete. Derive each `outer_radius := inner_radius + thickness`. Same reasoning as A5, one layer at a time; the two together make the whole radial build a chain of derivations from `axis_region.inner_radius` plus 14 thicknesses. Probe P6 measured the axis-region leg deriving cleanly; the other 26 radii collide (D-S2). **Basis [AGENT] (ratified by owner, 2026-08-13):** same basis as A5 — axis root radius + 14 thicknesses free; all radii derived. | n/a | length, m | **yes** (until fix; then deleted per ruled intent) |
| A7 | `CATFMFEShield::catf_shield::CompositionConsistency` | `shield.sysml:171` | `neutron_shield.fraction_volume + gamma_shield.fraction_volume == 1.0` | 4 | **derive-instead** | Delete. Closure over two terms — derive the last: `gamma_shield.fraction_volume := 1.0 - neutron_shield.fraction_volume`. See open point O3: the sum covers 2 of the 4 shield layers, so deriving it encodes a partial closure — ruled: the derivation goes ahead (it encodes exactly what the authored constraint checked, no worse), and the debt gets named model-debt records (O3). **Basis [AGENT] (ratified by owner, 2026-08-13):** `neutron_shield.fraction_volume` free; gamma derived. | n/a | dimensionless volume fractions summing to 1 | **no** |
| A8 | `CATFMFEVacuum::catf_vacuum_vessel::ThicknessConsistency` | `vacuum.sysml:87` | `outer_radius == inner_radius + wall_thickness` | 1 | **derive-instead** | Delete. Derive `outer_radius := inner_radius + wall_thickness`. All three are literals today (`6.3`, `0.2`, `6.5` at `vacuum.sysml:51-53`) and the source comment on line 53 already says the value came from that sum. | n/a | length, m | **no** |
| A9 | `CATFMFEVacuum::catf_vacuum_pumping::PumpingSpeedConsistency` | `vacuum.sysml:169` | `pumping_speed_total == n_pumps * pump_capacity_each` | 2 | **blocked-by-defect** (was assert-band; D-S1 ruling 2026-08-13 — retained as a visible plain usage until the unit-lane fix lands; the band below stays recorded intent) | Ruled intent: `assert constraint pumping_speed_agrees : ProductWithinBand { in observed = pumping_speed_total; in count = n_pumps; in each_capacity = pump_capacity_each; in rel_tol = …; }` in the relative form. Probes P3/P3b measured every assert spelling refusing (`SI_RENDERING_COLLISION` — both attributes are already unit-carrying entry points of `calc pump_load`). Genuine cross-check: `pumping_speed_total` is `volume_to_pump / vacuum_time_constant` = 200, and `n_pumps * pump_capacity_each` = 48 × 4.17 = **200.16**. Two independently authored routes to one number that already disagree by 0.16 — exactly class 2, and exactly why `==` is wrong here. | **[OWNER 2026-08-13]** **1% relative** (band = `count * each_capacity ± 1%`), chosen over absolute so the band scales under design-search resizing; ~12× the authored 0.16 m³/s disagreement. `ProductWithinBand` adjusts to relative form; if the def-shape changes materially, design notes it rather than silently adapting. Band protects: the pump count/capacity sizing still delivers the pumpdown speed the vessel volume needs. | volumetric flow, m^3/s on both sides; `n_pumps` is a dimensionless count, `pump_capacity_each` is m^3/s, product is m^3/s; the relative tolerance is dimensionless | **yes** |

**Group A totals as ruled (post D-S1/D-S2):** 4 `derive-instead` (A1, A4, A7, A8),
1 `assert-one-sided` (A2), 1 `assert-band` (A3), 3 `blocked-by-defect` (A5, A6, A9 — visible
plain usages, ruled target forms held as recorded intent). 5 of 9 survive as authored usages.

**Self-named bindings:** none required. Every survivor's formal is named differently from the
attribute it binds (`value` ← `p_electric_net_out`, `part_power` ← `p_parasitic_total`, `observed` ←
`pumping_speed_total`). No row needed the `SURFACED` escape, and the parked D-2 / D-4-SRC-01
conflict is untouched.

**Unit-annotated literals:** none of the three survivors carries a `[unit]` literal in its predicate
body, so none trips the `[m]`-literal elaborator failure (research §6) or the
`block_ordering_category_pair` real/quantity refusal.

---

# Group B — 5 part-definition guards

These five are owned by part definitions in `library/components/`. No design part is typed by any of
them (every CATF design part is untyped: `part catf_vacuum_vessel { … }`, never
`part x : 'Vacuum Vessel'`), so they reach zero instances and catalog `non_reaching`.

**The L2-2 consequence, stated plainly.** Attaching one of these by typing a design part is not free.
An asserted gate whose owner has zero occurrences counts as *missing assessment* and holds the whole
model at partial coverage. So attachment is only worth it when the guard is a real gate with real
bound values behind it. **I propose zero attachments.** Four of the five are the same structural
identities Group A derives away, and the fifth has no design part to attach to at all.

| # | usage | file:line | current predicate | class | proposed disposition | reasoning | unit-check (human) | survives? |
|---|---|---|---|---|---|---|---|---|
| B1 | `FusionComponents::Divertor::HeatLoadBalance` | `library/components/divertor.sysml:216` | `total_heat_load <= n_divertor_modules * (target_plates.surface_area_inner + target_plates.surface_area_outer) * target_plates.heat_flux_capability` | 3 | **inapplicable** — reason: no design part | This is the one genuine one-sided physics gate in Group B, and there is **no divertor part anywhere in `designs/catf_mfe/`** (verified: the design has plasma, blanket, shield, vacuum, magnets, heating, tritium, radial build, system — no divertor). `'Divertor'`'s attributes also carry no default values, so a typed part would bind nothing. Gating divertor physics means adding a divertor to the model, which is a modeling decision, not a constraint disposition. Flagged as O5. | heat load MW vs modules × m^2 × MW/m^2 → MW. Dimensionally consistent as written. | yes (as an authored, dispositioned usage) |
| B2 | `FusionComponents::'First Wall'::TotalThicknessConsistency` | `library/components/first_wall.sysml:220` | `total_thickness == armor_layer.thickness + structural_backing.thickness` | 1 | **inapplicable** — reason: no structurally matching design part | The design's `first_wall` (`radial_build.sysml:150`) is a radial-build *layer* — `inner_radius` / `thickness` / `outer_radius` — with no `armor_layer` or `structural_backing` children. Typing it `: 'First Wall'` would be a false claim about what the part is. The identity it expresses is derived away at A6 for the layer that actually exists. | length, m throughout | yes |
| B3 | `FusionComponents::'Radial Build Layer'::RadiusConsistency` | `library/components/radial_build.sysml:55` | `outer_radius == inner_radius + thickness` | 1 | **inapplicable** — reason: superseded by derivation | Identical to A6, at definition level. Once each layer's `outer_radius` is derived from `inner_radius + thickness`, the guard is structurally vacuous — and an attached vacuous asserted gate is exactly the L2-2 partial-coverage trap. | length, m | yes |
| B4 | `FusionComponents::'Shield Assembly'::TotalThicknessConsistency` | `library/components/shield.sysml:160` | `thickness_total == neutron_shield.thickness + gamma_shield.thickness + thermal_shield.thickness + biological_shield.thickness` | 4 | **inapplicable** — reason: superseded by derivation | Composition closure: derive `thickness_total` from the four layer thicknesses in `catf_shield` instead. Note the design's `thickness_total` is `0.4 [m]` (`shield.sysml:162`, "HT shield + structure layers") while the four layers named here sum to something else — the guard would fail if attached, which is itself worth your eye (O3). | length, m | yes |
| B5 | `FusionComponents::'Vacuum Vessel'::ThicknessConsistency` | `library/components/vacuum.sysml:155` | `outer_radius == inner_radius + wall_thickness` | 1 | **inapplicable** — reason: superseded by derivation | Identical to A8, at definition level. `catf_vacuum_vessel` could be typed by this def, but the value it would gate is derived by construction after A8, so attaching it buys a vacuous gate. | length, m | yes |

**Group B totals as proposed:** 5 `inapplicable`, 0 attachments, 0 usages deleted. All 5 survive as
authored, explicitly dispositioned usages and none enters the feasibility denominator (L2-1).

**Authoring warning carried forward:** a malformed `@inapplicable:` directive halts generation at
`error` whatever the usage's form, including a plain one. These five markers must be authored
exactly; a typo is a hard stop, not a silent no-op.

## B1–B5 recording mechanism — orchestrator-applied owner pattern

**[AGENT] 2026-08-13, orchestrator-applied — flagged for owner review.** Applies the owner's
D-S1/D-S2 pattern (option 3, ratified 2026-08-13) to a new instance of the same defect class.

**The disposition is unchanged.** All five rows stay `inapplicable`, with the reasons above.
What moves is *where the disposition is recorded*, and only that.

**What was measured** (Item 5 Phase 1, `verification.md`): the five `@inapplicable:` markers
were authored in the exact form and first-line placement the Item 2 fixtures pin, and
**5 were written in source while 0 reached the domain**. B1–B5 are inline-predicate
constraints (`constraint X { doc /* … */ <predicate> }`), and SysIDE drops a `doc` comment
inside an inline-predicate constraint body. That is rule 3 of
`tests/conformance/test_constraint_population_oracle.py`, which exists to make this gap loud.
Every Item 2 fixture that carries a working marker is bindings-form. Placement and spelling
are already correct, so there is no dodge inside the marker's own form.

**Ruled.** The five guards land in the derivative as **plain usages carrying no marker**.
Their inapplicability is recorded in this table and in PROVENANCE parked-row-style records
naming the marker-read defect, oracle rule 3, and the held intent — exactly as A5/A6/A9 are
handled. **No catalog vocabulary change**; their rows read `non_reaching` as they do in
`catf_mfe_d5` today. Rewriting the five guards into bindings form was rejected: it is an
unauthorized model rewrite this table never asked for.

**Held intent.** The markers are authored when the marker-read gap closes. Folded into epic
**Item 9**'s scope; the defect itself is filed as backlog `[INLINE-PREDICATE-MARKER-DROP]`.

**Nothing downstream moves.** `inapplicable_gate_count` is **0** either way — B1–B5 are plain
(non-asserted) usages and bucket row 1 decides "not asserted → inventory only" before the
inapplicable predicate is consulted (`generation/coverage.py:7-27`). Measured: the disposition
histogram and all 58 expectation identities are byte-identical with and without the markers.

---

# Group C — 51 calculation-definition guards

Owned by `calc def`s in `library/physics/` and `library/analyses/`. There is no calc-def attachment
branch at all today, so these reach nothing structurally.

**Only two dispositions are available to this group, and this is why.** An asserted constraint whose
owner is structurally unattachable is a generation-halting error by ruling, and the halt is
whole-model. One asserted calc-def guard takes SC-3, SC-4, SC-5 and SC-7 down together. So every row
below is `derive-instead` or `awaits-capability`. There is no third column, and none may be added at
design time.

**What "awaits-capability" means here.** The usage stays authored, stays a plain `constraint`, stays
cataloged `non_reaching`, and nothing is built. Item 6 designs the attachment capability and has not
run. These are not deferred *decisions* — the decision is made: not now.

**Why 50 of 51 are `awaits-capability`.** The equality taxonomy is a tool for equalities. These
guards are overwhelmingly input-domain and output-range assertions (`p_fusion > 0`,
`eta_thermal > 0 and eta_thermal < 1.0`) — already one-sided or two-sided inequalities, with no
equality to derive away and no structural identity hiding in them. They are real guards that simply
have nowhere to attach yet.

| # | usage (QN tail) | owner calc def | file:line | current predicate | disposition | reasoning |
|---|---|---|---|---|---|---|
| C01 | `PositiveInputs` | `MagnetCryogenicLoad` | `library/analyses/thermal_loads.sysml:69` | `magnet_volume > 0 and magnet_surface_area > 0 and first_wall_area > 0 and p_neutron > 0 and b_field > 0 and operating_temp > 0` | awaits-capability | Input-domain guard; no equality, nothing to derive. |
| C02 | `ReasonableCryoTemp` | `MagnetCryogenicLoad` | `thermal_loads.sysml:76` | `operating_temp > 1.0 and operating_temp < 80.0` | awaits-capability | Plausibility band on an input; already a band. |
| C03 | `CarnotEfficiencyPhysical` | `MagnetCryogenicLoad` | `thermal_loads.sysml:81` | `carnot_efficiency > 0 and carnot_efficiency < 1.0` | awaits-capability | Physical-range guard on a derived efficiency. |
| C04 | `PositiveInput` | `CoolantPumpPower` | `thermal_loads.sysml:122` | `p_thermal_electric > 0` | awaits-capability | Input-domain guard. |
| C05 | `ReasonableFraction` | `CoolantPumpPower` | `thermal_loads.sysml:127` | `f_pcppf > 0.02 and f_pcppf < 0.10` | awaits-capability | Plausibility band on an input fraction. |
| C06 | `PumpEfficiencyPhysical` | `CoolantPumpPower` | `thermal_loads.sysml:132` | `pump_efficiency > 0 and pump_efficiency <= 1.0` | awaits-capability | Physical-range guard. |
| C07 | `PositiveDelivered` | `HeatingWallPlugPower` | `thermal_loads.sysml:171` | `delivered_power > 0` | awaits-capability | Input-domain guard. |
| C08 | `EfficiencyPhysical` | `HeatingWallPlugPower` | `thermal_loads.sysml:176` | `heating_efficiency > 0 and heating_efficiency < 1.0` | awaits-capability | Physical-range guard. |
| C09 | `ReasonableEfficiency` | `HeatingWallPlugPower` | `thermal_loads.sysml:181` | `heating_efficiency > 0.20 and heating_efficiency < 0.80` | awaits-capability | Plausibility band narrower than C08; both are bands already. |
| C10 | `PositiveInputs` | `VacuumPumpPower` | `thermal_loads.sysml:224` | `pumping_speed_total_in > 0 and base_pressure > 0 and pump_count > 0` | awaits-capability | Input-domain guard. |
| C11 | `VacuumPressure` | `VacuumPumpPower` | `thermal_loads.sysml:229` | `base_pressure > 1.0e-6 and base_pressure < 100.0` | awaits-capability | Plausibility band on an input pressure. |
| C12 | `EfficiencyPhysical` | `VacuumPumpPower` | `thermal_loads.sysml:234` | `pump_efficiency > 0 and pump_efficiency <= 1.0` | awaits-capability | Physical-range guard. |
| C13 | `PositiveInputs` | `CryoPumpRefrigeration` | `thermal_loads.sysml:282` | `cryo_pump_count > 0 and pump_capacity > 0` | awaits-capability | Input-domain guard. |
| C14 | `CryogenicTemp` | `CryoPumpRefrigeration` | `thermal_loads.sysml:287` | `operating_temp > 4.0 and operating_temp < 80.0` | awaits-capability | Plausibility band on an input temperature. |
| C15 | `CarnotPhysical` | `CryoPumpRefrigeration` | `thermal_loads.sysml:292` | `carnot_efficiency > 0 and carnot_efficiency < 1.0` | awaits-capability | Physical-range guard. |
| C16 | `PositiveFusion` | `TritiumProcessingPower` | `thermal_loads.sysml:332` | `fusion_power > 0` | awaits-capability | Input-domain guard. |
| C17 | `ReasonableFactor` | `TritiumProcessingPower` | `thermal_loads.sysml:337` | `processing_factor > 0.001 and processing_factor < 0.01` | awaits-capability | Plausibility band on an input factor. |
| C18 | `PositiveGross` | `AuxiliarySystemsPower` | `thermal_loads.sysml:376` | `gross_electric > 0` | awaits-capability | Input-domain guard. |
| C19 | `ReasonableFraction` | `AuxiliarySystemsPower` | `thermal_loads.sysml:381` | `auxiliary_fraction > 0.003 and auxiliary_fraction < 0.02` | awaits-capability | Plausibility band on an input fraction. |
| C20 | `Phase1PositivePower` | `PlasmaConfinement` | `library/physics/confinement.sysml:127` | `p_fusion_input > 0` | awaits-capability | Input-domain guard. |
| C21 | `Phase2PlasmaParametersPhysical` | `PlasmaConfinement` | `confinement.sysml:133` | `true  // Placeholder - implement in Phase 2` | **delete-placeholder [OWNER 2026-08-13, O2]** | Deleted in the derivative as a named deletion record citing O2. A body-`true` constraint is a vacuous always-pass gate waiting for Item 6's capability; the derivative is the worked example of the policy and does not carry it. The frozen twins keep it for history. |
| C22 | `PositiveRadii` | `TorusMinorRadius` | `library/physics/geometry.sysml:59` | `r_inner >= 0 and r_outer > r_inner and r_major > 0` | awaits-capability | Input-domain and ordering guard. |
| C23 | `PositiveInputs` | `TorusVolume` | `geometry.sysml:101` | `r_major > 0 and a > 0 and kappa > 0` | awaits-capability | Input-domain guard. |
| C24 | `ReasonableElongation` | `TorusVolume` | `geometry.sysml:106` | `kappa >= 1.0 and kappa <= 5.0` | awaits-capability | Plausibility band on an input. |
| C25 | `PositiveInputs` | `TorusSurfaceArea` | `geometry.sysml:146` | `r_major > 0 and a > 0 and kappa > 0` | awaits-capability | Input-domain guard. |
| C26 | `PositiveInputs` | `MagnetSurfaceArea` | `geometry.sysml:185` | `r_inner > 0 and thickness > 0 and kappa > 0 and f_exposed > 0 and f_exposed <= 1.0` | awaits-capability | Input-domain guard. |
| C27 | `Phase1ReasonableTBR` | `TritiumBreedingRatio` | `library/physics/neutronics.sysml:132` | `tbr_assumed > 0.9 and tbr_assumed < 1.3` | awaits-capability | Plausibility band on an assumed input. |
| C28 | `Phase2SelfSufficiency` | `TritiumBreedingRatio` | `neutronics.sysml:138` | `true  // Placeholder - implement in Phase 2` | **delete-placeholder [OWNER 2026-08-13, O2]** | Deleted in the derivative as a named deletion record citing O2. Same ruling as C21. |
| C29 | `PositivePowers` | `ScientificQFactor` | `library/physics/performance_metrics.sysml:80` | `p_fusion > 0 and p_input > 0` | awaits-capability | Input-domain guard. |
| C30 | `ReasonableRange` | `ScientificQFactor` | `performance_metrics.sysml:85` | `q_sci > 0.01 and q_sci < 1000` | awaits-capability | Plausibility band on a derived output. |
| C31 | `PositivePowers` | `EngineeringQFactor` | `performance_metrics.sysml:150` | `p_electric_gross > 0 and p_auxiliary_total > 0` | awaits-capability | Input-domain guard. |
| C32 | `ViabilityCheck` | `EngineeringQFactor` | `performance_metrics.sysml:155` | `q_eng > 1.0` | awaits-capability | A real one-sided feasibility gate — the strongest candidate in Group C — but calc-def-owned, so it cannot be asserted now. Its intent is already covered at instance level by A2, which gates the same viability through `p_net > 0`. |
| C33 | `ReasonableRange` | `EngineeringQFactor` | `performance_metrics.sysml:160` | `q_eng < 50` | awaits-capability | One-sided plausibility bound on a derived output. |
| C34 | `PositivePowers` | `PlantEfficiency` | `performance_metrics.sysml:212` | `p_fusion > 0 and p_net > 0` | awaits-capability | Input-domain guard. |
| C35 | `EfficiencyPhysical` | `PlantEfficiency` | `performance_metrics.sysml:217` | `eta_plant > 0 and eta_plant < 1.0` | awaits-capability | Physical-range guard. |
| C36 | `ReasonableEfficiency` | `PlantEfficiency` | `performance_metrics.sysml:222` | `eta_plant > 0.15 and eta_plant < 0.50` | awaits-capability | Plausibility band narrower than C35. |
| C37 | `EnergyConservation` | `AlphaNeutronSplit` | `library/physics/power_balance.sysml:69` | `p_alpha + p_neutron > p_fusion * 0.99999 and p_alpha + p_neutron < p_fusion * 1.00001` | **derive-instead** | The only derivable row in Group C. Both outputs are `p_fusion` times fixed coefficients that sum to exactly 1 (`3.52/17.58` + `14.06/17.58`), so the band checks arithmetic the generator already guarantees. Derive `p_neutron := p_fusion - p_alpha` and delete the usage. Pairs with A1, which is the same identity re-asserted at instance level. |
| C38 | `PositivePower` | `AlphaNeutronSplit` | `power_balance.sysml:75` | `p_fusion > 0` | awaits-capability | Input-domain guard. |
| C39 | `PositiveInputs` | `BlanketThermalPower` | `power_balance.sysml:130` | `p_neutron > 0 and p_input >= 0` | awaits-capability | Input-domain guard. |
| C40 | `ReasonableMultiplication` | `BlanketThermalPower` | `power_balance.sysml:135` | `m_neutron >= 1.0 and m_neutron <= 1.5` | awaits-capability | Plausibility band on an input. |
| C41 | `ReasonableEfficiencies` | `BlanketThermalPower` | `power_balance.sysml:140` | `eta_thermal > 0 and eta_thermal <= 1.0 and f_pump >= 0 and f_pump <= 1.0 and eta_pump > 0 and eta_pump <= 1.0 and f_subsystem >= 0 and f_subsystem <= 1.0` | awaits-capability | Four physical-range guards in one usage. |
| C42 | `PositivePowers` | `GrossElectricPower` | `power_balance.sysml:193` | `p_thermal > 0 and p_alpha >= 0` | awaits-capability | Input-domain guard. |
| C43 | `ThermalEfficiencyPhysical` | `GrossElectricPower` | `power_balance.sysml:198` | `eta_thermal > 0 and eta_thermal < 0.5` | awaits-capability | Physical-range guard against an approximate Carnot ceiling. |
| C44 | `DirectConversionRange` | `GrossElectricPower` | `power_balance.sysml:203` | `eta_direct >= 0 and eta_direct <= 0.9` | awaits-capability | Physical-range guard. |
| C45 | `PositiveGrossElectric` | `NetElectricPower` | `power_balance.sysml:260` | `p_electric_gross > 0` | awaits-capability | Input-domain guard. |
| C46 | `NonNegativeParasitics` | `NetElectricPower` | `power_balance.sysml:265` | `p_coils >= 0 and p_heating >= 0 and p_pumps >= 0 and p_cryo >= 0 and p_vacuum >= 0 and p_tritium >= 0 and p_auxiliary >= 0` | awaits-capability | Seven input-domain guards in one usage. |
| C47 | `ReasonableParasiticFraction` | `NetElectricPower` | `power_balance.sysml:272` | `p_parasitic_total < p_electric_gross` | awaits-capability | A real one-sided gate, calc-def-owned. Its intent is covered at instance level by A3's upper band edge. |
| C48 | `TemperaturePhysical` | `ThermalCycleEfficiency` | `library/physics/thermal.sysml:125` | `t_hot > t_cold and t_cold > 273.0` | awaits-capability | Ordering and input-domain guard. |
| C49 | `ReasonableTemperatures` | `ThermalCycleEfficiency` | `thermal.sysml:130` | `t_hot > 500.0 and t_hot < 1200.0 and t_cold > 273.0 and t_cold < 350.0` | awaits-capability | Plausibility bands on inputs. |
| C50 | `RealEfficiencyRange` | `ThermalCycleEfficiency` | `thermal.sysml:136` | `eta_real > 0.4 and eta_real < 0.95` | awaits-capability | Plausibility band on an input. |
| C51 | `ThermalEfficiencyPhysical` | `ThermalCycleEfficiency` | `thermal.sysml:141` | `eta_thermal > 0 and eta_thermal < eta_carnot and eta_thermal < 1.0` | awaits-capability | Physical-range guard against the computed Carnot limit. |

**Group C totals as ruled:** 48 `awaits-capability`, 1 `derive-instead` (C37), 2
`delete-placeholder` (C21, C28 — **[OWNER 2026-08-13]**, O2; a ruling this table could not
propose, since deletion was outside its two available dispositions). No row is asserted-now, and
none may become so at design time.

**Unit-check for Group C:** not applicable while these await capability. Nothing is authored, so
there is no binding to mis-unit. When Item 6 lands, every one of these rows needs the same
human unit check Group A got.

---

# item5-F1 account — RULED: the accounting identity

**[OWNER 2026-08-13] Option 1 is ruled.** SC-3 is amended to the accounting identity; the
option's content stays `[AGENT] (ratified by owner, 2026-08-13)`. The spec carries the amendment
text; this section records the arithmetic in force.

**The arithmetic, as ruled and restated under the D-S1/D-S2 ruling** (restatement authorized —
a mechanical consequence, not a re-disposition):

| line | count |
|---|---|
| authored usages in `catf_mfe_d5` | 65 |
| `derive-instead` (usage deleted, derivation replaces it) | **5** — A1, A4, A7, A8, C37 |
| `delete-placeholder` (**[OWNER 2026-08-13]**, O2) | **2** — C21, C28 |
| **surviving authored usages in the derivative (carriers)** | **58** |

Of the 58 survivors: 2 asserted gates (A2, A3), 3 `blocked-by-defect` plain usages (A5, A6, A9 —
ruled target forms held as recorded intent for the post-fix follow-on), 5 explicitly
inapplicable part-def guards (B1–B5), 48 plain `awaits-capability` calc-def guards (Group C
minus C37, C21, C28).

**How PROVENANCE reconciles it.** The derivative's PROVENANCE records the identity
`65 = 58 carriers + 7 named deletions`. Each of the 7 gets a deletion record naming: the deleted
usage's qualified name and d5 file:line, its intent class (or O2 for the placeholders), the
derivation that replaces it (for the 7) with the undirected relation and chosen-basis statement,
and the row in this table that authorized it. The machine-checkable diff (SC-2) then accounts for
every change with a reason, and no usage vanishes silently — it is either a carrier or a named
deletion. The three `blocked-by-defect` usages additionally carry PROVENANCE records naming
D-S1/D-S2, the defect item, and the held intent. The frozen-twin half of SC-3 (65 carriers on
`catf_mfe_d5` itself) is untouched — Item 2 proved it and it stays.

The two rejected alternatives (keep the equalities as descriptive usages beside the derivations;
reclassify class-1 rows as bands) are recorded in this file's git history at the proposal
revision; the second was named only to be rejected as the steering the spec's Non-Goals forbid.

---

# SC-5 — executable-gate candidates

SC-5 needs at least one physically valid candidate reaching the satisfied path and one unphysical
mutation reaching `reject`, through generated package → TEAx normalization → policy → durable case
storage.

**Research §3 suggested `ViabilityCheck` might be the only clear one-sided gate. Under this
classification there are three.** That is more headroom than expected, and it means SC-5 does not
rest on a single row.

| candidate | why it can carry SC-5 | mutation that should reject |
|---|---|---|
| **A2 `catf_physics::ViabilityCheck`** (strongest) | Already ADMITs today under an assert probe — measured, not predicted. A second research probe asserting only this constraint built cleanly: 44 modules, `concrete_entries=1`, `excluded_records=8`, well-formed IR. It sits at the end of the real power chain, so a physics input mutation propagates into it through seven calc modules. | Drop `p_fusion` (`physics.sysml:53`, 2600 MW) far enough that `p_net` goes negative, or raise a parasitic load past gross electric. Either is a physics input, not a constraint edit. |
| **A3 `catf_physics::ReasonableParasiticTotal`** | Two-sided band with a physically meaningful upper edge; the same power-chain inputs drive it, so one mutation can be checked against two gates. | Raise a parasitic contributor (e.g. `catf_heating.wall_plug_power`) until the parasitic share crosses the upper band edge. |
| **A9 `catf_vacuum_pumping::PumpingSpeedConsistency`** | A genuine cross-check band with a real, already-nonzero disagreement (200 vs 200.16 m^3/s), which makes the boundary easy to sit near and easy to cross deliberately. | Change `n_pumps` or `pump_capacity_each` so the product leaves the approved band. |

**Caveat, stated so design does not inherit it as a promise.** Only A2 has a measured ADMIT. A3 and
A9 are predicted to admit from the profile rules (inequality comparisons, `real`/`real` operands,
chains in binding position only) and have not been probed. If either fails to admit, A2 alone still
satisfies SC-5 — but the resulting coverage denominator changes, so design should probe all three
before committing.

**[OWNER 2026-08-13] Endorsed as laid out:** design probes all three candidates (A2/A3/A9) before
committing. A2 is the anchor — the only measured ADMIT, and now also the only gate whose
threshold needed no tolerance ruling.

**Post-probe status (D-S1 ruling, 2026-08-13):** A9 is `blocked-by-defect` and out of the SC-5
candidate set. **SC-5 proceeds with A2 as anchor and A3 as the second executing gate** — both
measured ADMIT at design probes P1/P2 (the P2 composite: 45 modules, 2 concrete entries).

---

# Open points — dispositions under the 2026-08-13 ruling

- **O1 — SC-3 versus the derive count. RULED [OWNER 2026-08-13]:** option 1, the accounting
  identity. See "item5-F1 account" above; the spec carries the SC-3 amendment.

- **O2 — Two placeholder predicates whose body is the literal `true`. RULED [OWNER 2026-08-13]:
  delete both in the derivative**, each as a named deletion record citing O2. The derivative is
  the worked example of the policy; a body-`true` constraint is a vacuous always-pass gate waiting
  for Item 6's capability. The frozen twins keep them for history. (C21, C28 rows updated above;
  this is the +2 in the accounting identity.)

- **O3 — Partial shield closure and the mismatched thickness sets. RULED [OWNER 2026-08-13]:
  record the debt, don't bake it silently.** A7's 2-of-4 closure (`thermal_shield` and
  `biological_shield` have no `fraction_volume` attribute) and B4's mismatched sets (the guard
  sums four layer thicknesses while the design's `thickness_total` is `0.4 [m]` labelled "HT
  shield + structure layers") get **named model-debt entries in the derivative's PROVENANCE plus
  one backlog note**. The A7 derivation goes ahead — it encodes exactly what the authored
  constraint checked, no worse — but the debt must be findable, not embedded.

- **O4 — Units exist only in comments. Acknowledged, design-owned as stated.** Every CATF
  attribute is a bare `Real`; units live in end-of-line comments. The unit-check column is a claim
  about intent, not a fact read from the model. The generic-band-versus-dimension-pinned choice is
  design's.

- **O5 — Divertor gate. RULED [OWNER 2026-08-13]: B1 stays inapplicable as proposed.** Gating
  divertor power exhaust would mean adding a divertor — a modeling-scope decision made in
  daylight, not smuggled in as a disposition. A follow-on backlog entry ("divertor addition +
  HeatLoadBalance gating, CATF derivative") records the option, unowned, priority owner's-later.

- **O6 — A5/A6 imply 27 attribute-declaration edits. Acknowledged, design-owned; the edit is
  authorized by the A5/A6 basis ruling** (axis root radius + 14 thicknesses free, radii derived).
  Design decides the edit shape and PROVENANCE records it.

- **O7 — Constraint-definition library home. Acknowledged, design-owned as stated.** Three
  survivors need three definition shapes (`PositiveQuantity`, `FractionWithinBand`,
  `ProductWithinBand`, names provisional; A9's ruling makes the product band relative-form).
  Guidance graduation stays filed for Item 7.

- **New filing from the ruling [OWNER 2026-08-13] — acausal-relations capability question.**
  Relation-style parametrics with study-selectable causality ("don't force independent vs
  dependent") is a capability bet this toolchain cannot currently express; the derive rulings
  above choose visible in-model bases precisely because the alternative hides causality in study
  harness config. Filed as one unowned backlog line citing this ruling.

---

## Provenance

Rows the owner approved without change are `[AGENT] (ratified by owner, 2026-08-13)` — settled by
owner ratification of agent-originated content, challengeable by re-deriving against the recorded
reasoning. Owner-originated items are `[OWNER 2026-08-13]`: the A3 tolerance values and their
recorded promise, the A9 relative-tolerance ruling, the item5-F1 SC-3 amendment authorization,
and the O2/O5 rulings. The A5/A6/A7 basis cells and the derivation doc-comment obligation are the
owner's structural amendment, content `[AGENT] (ratified by owner, 2026-08-13)`. The intent
taxonomy is `[INHERITED]` from the lifecycle contract (itself `[AGENT] (ratified by owner,
2026-08-12)`). The 65-row domain is `[INHERITED]` from
`tests/expectations/constraint_population/catf_mfe_d5.json`. All predicates are transcribed from
the `.sysml` sources named in each row, verified against source at the proposal revision, not
from the research doc's transcription. The proposal form of this table is preserved in git
history (`0f90e20`).
