# Provenance — `catf_mfe_gated`

Forked from `tests/fixtures/catf_mfe_d5` on 2026-08-13 for **CONSTRAINT-SEMANTICS Item 5**
(`.project/completed/20260813_catf-constraint-policy-acceptance/`). This fixture is the **worked example of
the ruled constraint policy**: nothing in it is invented, and every difference from `catf_mfe_d5`
traces to a row in `owner-disposition.md` (RULED 2026-08-13).

**The frozen twins are untouched.** `catf_mfe_model` and `catf_mfe_d5` keep their bytes and their
byte-reversal relationship; the only edit to d5 was its stale acceptance paragraph. This fixture
deliberately differs from d5, so the byte-reversal check does not transfer to it. Its integrity
check is the **accounting identity** instead: `scripts/check_gated_manifest.py --check`, which
joins the ruled table, the population expectation, and this file, and proves

> **65 = 58 carriers + 7 named deletions**

closes with every carrier matched (56 by name, 2 by `renamed_from:`) and every deletion citing an
authorizing table row. Nothing is a carrier and nothing vanishes silently.

**Measured shape** (licensed elaboration, 2026-08-13): **47 modules · 58 usage rows · 2 concrete
entries · dispositions `{eligible: 2, excluded: 3, non_reaching: 53}`**. Coverage account
`58 / 2 / 2 / 0 / 0 / {} / complete`, headline `full_satisfaction` for the authored candidate.

---

## 1. Per-change records

One record per edit, each citing its authorizing row.

### `library/constraints/gate_forms.sysml` — new file (D5)

Package `CATFGateForms`, fixture-local, holding `PositiveQuantity` and `FractionWithinBand`.
Both are declared over bare `Real` formals with predicates written over formals only — the
blessed bindings-only gate shape (`rulings-20260812.md` Q4).

`ProductWithinBand` is **deliberately not authored**. Its only consumer was A9, which the D-S1
ruling parks; authoring it would ship an unused definition. Authority: design D5, open point O7.

**`PositiveQuantity`'s formal is named `quantity`, not `value` — a change from the ruled table's
proposed spelling.** `owner-disposition.md`'s A2 cell proposes
`constraint def PositiveQuantity { in value : Real; value > 0 }`. That spelling **cannot
generate**: `value` is a reserved generated local in predicate scope
(`src/sysml_codegen/generation/constraint_name_safety.py:39`,
`generated_locals=frozenset({"value"})`), so generation refuses the model with

```
Constraint name-safety violation: … scope='predicate', kind='generated_binding_overlap',
final_binding='value' collides with generated binding 'value'
```

Elaboration admits it; the refusal is a **generation preflight**, which is why it surfaced only
at the acceptance run (Item 5 finding **6-B**). The formal is therefore named `quantity`, in the
definition and in its one binding.

**Authority: open point O7**, which records the library's names as **provisional and
design-owned** — this is a formal's spelling, not a disposition, tolerance, intent class, or
count, and none of those moved. The spec independently blesses formal renaming as "a local edit"
for the structurally identical self-named-binding case. The change moves no usage qualified name
and no source line, so every committed expectation still matched with no edit.

### A2 — `designs/catf_mfe/physics.sysml:126`, asserted and renamed

- **`renamed_from:` `CATFMFEPhysics::catf_physics::ViabilityCheck`** (d5 `physics.sysml:134`)
- **now:** `CATFMFEPhysics::catf_physics::net_power_viable`
- Rewritten as `assert constraint net_power_viable : PositiveQuantity { in quantity = p_electric_net_out; }`.
- The intent is unchanged — it was already a one-sided gate and already the only row with a
  measured ADMIT. What changed is the `assert` prefix and the bindings-only shape.
- Authority: `owner-disposition.md` Group A, A2 (`assert-one-sided`).

### A3 — `designs/catf_mfe/physics.sysml:134`, asserted and renamed

- **`renamed_from:` `CATFMFEPhysics::catf_physics::ReasonableParasiticTotal`** (d5 `physics.sysml:142`)
- **now:** `CATFMFEPhysics::catf_physics::parasitic_fraction_ok`
- Rewritten as `assert constraint parasitic_fraction_ok : FractionWithinBand` binding
  `part_power`, `whole_power`, `lower_frac = 0.10`, `upper_frac = 0.90`.
- The two feature chains move into **binding position**, which is supported; chains inside a
  predicate body remain blocked.
- Tolerances are the owner's: **`[OWNER 2026-08-13]` lower `0.10`, upper `0.90`**, the authored
  values, confirmed as a **plausibility envelope**. Recorded promise, carried here so it is not
  lost: **this band does not gate viability — viability is A2's job (`p_net > 0`).**
- Authority: `owner-disposition.md` Group A, A3 (`assert-band`).

### The derivations that replace deleted usages

Each is a computed design attribute replacing a literal in place (design D4), with the unit moved
to a trailing comment to match the fixture's dominant idiom.

| edit | file | derivation |
|---|---|---|
| A7 | `designs/catf_mfe/shield.sysml` | `gamma_shield.fraction_volume := 1.0 - neutron_shield.fraction_volume` |
| A8 | `designs/catf_mfe/vacuum.sysml` | `catf_vacuum_vessel.outer_radius := inner_radius + wall_thickness` |
| C37 | `library/physics/power_balance.sysml` | `p_neutron := p_fusion - p_alpha` |

A1 and A4 are deletions with no new derivation of their own: A1 is the instance-level restatement
of C37's identity, and A4 asserted a literal against itself.

### What was **not** edited

- **A5, A6, A9 are left exactly as `catf_mfe_d5` wrote them.** See §3.
- **B1–B5 are left exactly as `catf_mfe_d5` wrote them**, with no `@inapplicable:` marker. See §3.
- **The axis-region layer is not derived.** Design probe P6 measured it deriving cleanly, and it is
  the one A5/A6 leg that would generate — but deriving it alone leaves the radial build carrying
  two bases at once, which is worse modeling than the constraint it would replace. One consistent
  basis, per the D-S2 ruling.
- No `[unit]` literal appears in either surviving gate's predicate body (D3).
- **No bare self-named binding is authored anywhere.** Every surviving formal is named differently
  from the attribute it binds (`quantity` ← `p_electric_net_out`, `part_power` ←
  `p_parasitic_total`). The parked D-2 versus D-4/SRC-01 conflict is untouched.

---

## 2. The seven named deletions

`65 = 58 carriers + **7 named deletions**`. Five are `derive-instead`; two are the O2 placeholder
deletions. Each names the deleted usage, its d5 `file:line`, its intent class, and its authorizing
row.

**The derivation documentation obligation** (`[OWNER 2026-08-13]`, structural amendment): each
derivation records the **undirected relation** and states that the direction is a **chosen basis,
not physics**. The relation intent must survive the deletion. Those statements are carried in
source beside each derivation and repeated below.

> **Deviation, recorded.** The obligation says "doc comment". These are `//` comments rather than
> `doc /* … */` bodies. Carrying a real `doc` on an attribute-with-initializer needs a trailing
> `{ doc /* … */ }` body, which risks perturbing an atomic landing for no gain — and Item 5 Phase 1
> measured directly that SysIDE's handling of `doc` bodies in unusual positions is unreliable (five
> `@inapplicable:` markers written, zero carried). `//` is also this fixture's dominant
> documentation idiom: every unit in the model lives in one. The verbatim relation and
> chosen-basis statements are mandatory either way and appear in both places.
> Orchestrator-confirmed 2026-08-13.

### D1 — A1 `CATFMFEPhysics::catf_physics::PowerBalanceConsistency`

- **d5 location:** `designs/catf_mfe/physics.sysml:125` · **intent class:** 1 (structural identity)
- **Authorizing row:** `owner-disposition.md` Group A, A1 (`derive-instead`)
- **Relation (undirected):** `alpha_neutron_split.p_alpha + alpha_neutron_split.p_neutron = p_fusion`
- **Chosen basis, not physics:** `p_alpha` is the free branch; `p_neutron` is derived as the
  remainder. The reverse basis is equally valid. The direction is a modeling choice.
- **Why deleted:** `AlphaNeutronSplit` splits `p_fusion` by `3.52/17.58` and `14.06/17.58`, which
  sum to exactly 1. Conservation is true by construction, so the band checked arithmetic the
  generator already guarantees. Replaced by the same derivation as C37.

### D2 — A4 `CATFMFERadialBuild::catf_radial_build::TotalRadiusConsistency`

- **d5 location:** `designs/catf_mfe/radial_build.sysml:605` · **intent class:** 3 (feasibility gate)
- **Authorizing row:** `owner-disposition.md` Group A, A4 (`derive-instead`)
- **Why deleted, no derivation needed:** class 3's own rule — a quantity that must *equal* a value
  is fixed as an input, not searched for and then constrained. `bioshield.outer_radius` is already
  the literal `8.55 [m]` (`radial_build.sysml:558` in d5), so the gate asserted a literal against
  itself. It also carried the `[m]`-literal elaborator defect.

### D3 — A7 `CATFMFEShield::catf_shield::CompositionConsistency`

- **d5 location:** `designs/catf_mfe/shield.sysml:171` · **intent class:** 4 (composition closure)
- **Authorizing row:** `owner-disposition.md` Group A, A7 (`derive-instead`)
- **Relation (undirected):** `neutron_shield.fraction_volume + gamma_shield.fraction_volume = 1.0`
- **Chosen basis, not physics:** `neutron_shield.fraction_volume` free; `gamma_shield.fraction_volume`
  derived as `1.0 - neutron_shield.fraction_volume`. Basis ruled at `owner-disposition.md` A7.
- **Carries model debt — see §4.** The sum covers 2 of the 4 shield layers.

### D4 — A8 `CATFMFEVacuum::catf_vacuum_vessel::ThicknessConsistency`

- **d5 location:** `designs/catf_mfe/vacuum.sysml:87` · **intent class:** 1 (structural identity)
- **Authorizing row:** `owner-disposition.md` Group A, A8 (`derive-instead`)
- **Relation (undirected):** `outer_radius = inner_radius + wall_thickness`
- **Chosen basis, not physics:** `inner_radius` and `wall_thickness` free; `outer_radius` derived.
  Solving the same relation for `wall_thickness` would be equally valid.
- **Why deleted:** all three were literals (`6.3`, `0.2`, `6.5`), and d5's own source comment
  already said the value came from that sum.

### D5 — C37 `FusionPhysics_PowerBalance::AlphaNeutronSplit::EnergyConservation`

- **d5 location:** `library/physics/power_balance.sysml:69` · **intent class:** 4
- **Authorizing row:** `owner-disposition.md` Group C, C37 (`derive-instead`) — the only derivable
  row in Group C
- **Relation (undirected):** `p_alpha + p_neutron = p_fusion`
- **Chosen basis, not physics:** `p_alpha` free, `p_neutron` derived as the remainder.
- **Why deleted:** both outputs are `p_fusion` times fixed coefficients summing to exactly 1, so
  the band checked guaranteed arithmetic. Pairs with A1, the same identity re-asserted at instance
  level.

### D6 — C21 `FusionPhysics_Confinement::PlasmaConfinement::Phase2PlasmaParametersPhysical`

- **d5 location:** `library/physics/confinement.sysml:133`
- **Authorizing row:** `owner-disposition.md` open point **O2**, `[OWNER 2026-08-13]`
- **Why deleted:** the predicate body is the literal `true` — a vacuous always-pass gate waiting
  for Item 6's capability. This fixture is the worked example of the policy and does not carry one.
  The frozen twins keep it for history.

### D7 — C28 `FusionPhysics_Neutronics::TritiumBreedingRatio::Phase2SelfSufficiency`

- **d5 location:** `library/physics/neutronics.sysml:138`
- **Authorizing row:** `owner-disposition.md` open point **O2**, `[OWNER 2026-08-13]`
- **Why deleted:** same ruling as C21; body is the literal `true`.

---

## 3. Parked rows — the dispositions that live only here

These usages are **byte-identical to `catf_mfe_d5`**, and their catalog rows are
**indistinguishable from any other plain usage**. Item 2's disposition vocabulary is closed, and
neither ruling added a token to it. **This section is the only place these dispositions are
visible.** That is the point of writing them down here.

### 3a. A5, A6, A9 — `blocked-by-defect` (D-S1 / D-S2)

| | A5 | A6 | A9 |
|---|---|---|---|
| usage | `CATFMFERadialBuild::catf_radial_build::LayerContinuity` | `CATFMFERadialBuild::catf_radial_build::RadiusThicknessConsistency` | `CATFMFEVacuum::catf_vacuum_pumping::PumpingSpeedConsistency` |
| d5 `file:line` | `radial_build.sysml:612` | `radial_build.sysml:630` | `vacuum.sysml:169` |
| here | `radial_build.sysml:604` | `radial_build.sysml:622` | `vacuum.sysml:169` |
| disposition | `blocked-by-defect` | `blocked-by-defect` | `blocked-by-defect` |
| surfacing finding | **D-S2** | **D-S2** | **D-S1** |
| catalog row reads | `excluded` / unassessed form | `excluded` / unassessed form | `excluded` / unassessed form |

**The measured refusal.** All three refuse against the current projection with
`SI_RENDERING_COLLISION`:

- **A5/A6** — the ruled basis needs a computed design attribute on every layer radius. **26 of the
  27 refuse.** Each layer's `inner_radius` and `outer_radius` are already unit-carrying entry
  points of that layer's `calc minor_calc : TorusMinorRadius`. The colliding entry point measured
  at probe P4a/P5 was `CATFMFERadialBuild__catf_radial_build__plasma_region__inner_radius`. Only
  `axis_region.outer_radius`, the one layer with no geometry calc on it, derives cleanly — and it
  is deliberately left underived so the radial build keeps one basis.
- **A9** — every assert spelling refuses. Both `n_pumps` and `pumping_speed_total` are already
  unit-carrying entry points of `calc pump_load : VacuumPumpPower`. The colliding entry point
  measured at probe P3/P3b was `CATFMFEVacuum__catf_vacuum_pumping__n_pumps`. No formal naming,
  unit comment, or tolerance form changes it.

**There is no authoring dodge, and none was attempted.** A shim attribute introduced solely to
dodge the collision would have been the silent workaround the item forbids.

**Who fixes it, and who upgrades this row.** The unit-lane port-metadata defect is **epic Item 8**.
The upgrade of this fixture under the already-ruled rows is **epic Item 9**.

**The held intent, so it survives the parking:**

- **A5 / A6 basis** (`[AGENT]`, ratified by owner 2026-08-13): the free parameters are the **axis
  root radius plus the 14 layer thicknesses**; all other radii are derived. Both rows' ruled intent
  is *delete the constraint and derive* — `inner_radius` from the layer below (A5) and
  `outer_radius := inner_radius + thickness` (A6). Together they make the whole radial build a
  chain of derivations. A parameterization is an engineering decision carrying owner sign-off,
  never a side effect of classification.
- **A9 target form** (`[OWNER 2026-08-13]`): `assert-band` at **1% relative** —
  `band = count * each_capacity ± 1%` — chosen over an absolute tolerance so the band scales under
  design-search resizing. It is ~12× the authored disagreement. This is a genuine class-2
  cross-check: `pumping_speed_total` is `volume_to_pump / vacuum_time_constant` = 200, while
  `n_pumps * pump_capacity_each` = 48 × 4.17 = **200.16**. Two independently authored routes to one
  number that already disagree by 0.16 m³/s — which is exactly why `==` was wrong here. The band
  protects the claim that pump count and capacity sizing still deliver the pumpdown speed the
  vessel volume needs.

### 3b. B1–B5 — `inapplicable`, recorded here because the marker cannot reach the domain

The five part-definition guards are dispositioned **`inapplicable`** by the owner's ruling, with
zero attachments. That disposition is unchanged. What is unusual is *where* it is recorded.

**Measured** (Item 5 Phase 1): the five `@inapplicable:` markers were authored in the exact form
the Item 2 fixtures pin (`tests/fixtures/constraint_domain_inapplicable/model.sysml:20`), as the
first line of the first `doc` body — the placement `constraint_domain_inapplicable_late_marker`
requires. Result: **5 markers written in source, 0 carried on the domain.** Elaboration ADMITs and
the markers are silently dropped.

**Cause.** B1–B5 are **inline-predicate** constraints (`constraint X { doc /* … */ <predicate> }`),
and SysIDE drops a `doc` comment inside an inline-predicate constraint body. This is **rule 3** of
`tests/conformance/test_constraint_population_oracle.py`, written down precisely to make the gap
loud. Every Item 2 fixture that carries a working marker is bindings-form; the inline-predicate
shape was never exercised. Placement and spelling are already correct, so no dodge exists inside
the marker's own form.

**Ruled** (`[AGENT]` 2026-08-13, orchestrator-applied as an instance of the owner's D-S1/D-S2
pattern, flagged for owner review): the five guards land as **plain usages carrying no marker**,
with the disposition recorded in `owner-disposition.md` and here. Rewriting them into bindings form
was rejected as an unauthorized model rewrite. **No catalog vocabulary change** — their rows read
`non_reaching`, as in `catf_mfe_d5`.

**Nothing downstream moves.** `inapplicable_gate_count` is **0 either way**: B1–B5 are plain
(non-asserted) usages, and bucket row 1 decides "not asserted → inventory only" before the
inapplicable predicate is consulted (`generation/coverage.py:7-27`). Measured: the disposition
histogram and all 58 expectation identities are byte-identical with and without the markers.

**Who fixes it, and who upgrades these rows.** The parser gap is backlog
`[INLINE-PREDICATE-MARKER-DROP]` (P3, unowned). Authoring the five markers once it closes is in
**epic Item 9**'s scope.

**The held intent — each row's ruled reason for being inapplicable:**

| row | usage | `file:line` here | reason |
|---|---|---|---|
| B1 | `FusionComponents::Divertor::HeatLoadBalance` | `library/components/divertor.sysml:216` | **No design part.** There is no divertor anywhere in `designs/catf_mfe/`, and `'Divertor'`'s attributes carry no defaults, so a typed part would bind nothing. Gating divertor power exhaust means adding a divertor — a modeling decision made in daylight, not smuggled in as a disposition. Open point **O5**; the option is filed as a backlog entry. |
| B2 | `FusionComponents::'First Wall'::TotalThicknessConsistency` | `library/components/first_wall.sysml:220` | **No structurally matching design part.** The design's `first_wall` is a radial-build *layer* — `inner_radius`/`thickness`/`outer_radius` — with no `armor_layer` or `structural_backing` children. Typing it `: 'First Wall'` would be a false claim about what the part is. |
| B3 | `FusionComponents::'Radial Build Layer'::RadiusConsistency` | `library/components/radial_build.sysml:55` | **Superseded by derivation.** Identical to A6 at definition level. Once each layer's `outer_radius` is derived, the guard is structurally vacuous — and an attached vacuous asserted gate is exactly the L2-2 partial-coverage trap. |
| B4 | `FusionComponents::'Shield Assembly'::TotalThicknessConsistency` | `library/components/shield.sysml:160` | **Superseded by derivation.** Composition closure; `thickness_total` is derived from the layer thicknesses instead. **Carries model debt — see §4.** |
| B5 | `FusionComponents::'Vacuum Vessel'::ThicknessConsistency` | `library/components/vacuum.sysml:155` | **Superseded by derivation.** Identical to A8 at definition level. `catf_vacuum_vessel` *could* be typed by this def, but the value it would gate is derived by construction after A8, so attaching it buys a vacuous gate. |

**Why zero attachments, stated once.** An asserted gate whose owner has zero occurrences counts as
*missing assessment* and holds the whole model at partial coverage (`rulings-20260812.md` L2-2).
Attachment is only worth it when the guard is a real gate with real bound values behind it. Four of
the five are structural identities Group A derives away, and the fifth has no design part to attach
to at all.

---

## 4. Model debt (open point O3)

Ruled `[OWNER 2026-08-13]`: **record the debt, don't bake it silently.** Both entries are real
model problems that this item does not fix. They must be findable, not embedded.

### O3-a — A7's shield closure covers 2 of 4 layers

The A7 derivation encodes `neutron_shield.fraction_volume + gamma_shield.fraction_volume = 1.0`.
The shield has **four** layers; `thermal_shield` and `biological_shield` have no `fraction_volume`
attribute at all. So the closure is partial, and deriving it makes the partial closure structural
rather than merely asserted.

The derivation went ahead by ruling — **it encodes exactly what the authored constraint checked,
no worse.** But a two-term closure over a four-layer assembly is a modeling claim nobody has
signed. If the two missing layers should hold volume fractions, this derivation is wrong in a way
no test here will catch.

### O3-b — B4's mismatched thickness sets

B4's guard sums **four** layer thicknesses (`neutron_shield` + `gamma_shield` + `thermal_shield` +
`biological_shield`). The design's `catf_shield.thickness_total` is `0.4 [m]`, labelled *"HT shield
+ structure layers"* — a different set. The two do not describe the same quantity, so **the guard
would fail if it were attached**. That is worth an owner's eye independently of the disposition:
B4 is inapplicable here for a structural reason, but the mismatch it exposes is a live modeling
question.

---

## 5. Per-gate unit reasoning (D3) — what the human is on the hook for

**The toolchain does not check units on constraint bindings.** A unit written on a binding
(`in tol = 0.05 [m];`) contributes the number and nothing else: a bound formal takes its operand
category from the constraint definition's declared type, so the annotation never reaches the
dimension check. A band comparing a length against a time is **admitted silently**
(`docs/architecture/modeling-assumptions.md` §8; Item 4 measured limit 1).

Worse in this model than usual: **every CATF attribute is a bare `Real`.** Units live only in
end-of-line comments and doc text. So the unit correctness of both gates below is a **human claim
about intent**, verified at exactly two checkpoints — the owner's sign-off (2026-08-13) and design
review against the authored source — and **nowhere else**. A later reader must not read these
paragraphs as evidence that anything machine-checked them.

Both gates take the dimensionless, unit-blind library band under human review (design D3). A
constraint formal cannot carry unit text at all, so the per-dimension in-predicate spelling is the
only unit-carrying option and it costs one definition per dimension — which buys nothing for these
two.

### A2 `net_power_viable` — `quantity > 0`

- **Operands:** `quantity` ← `p_electric_net_out`, a **power in MW**. The threshold `0` is the
  authored physical zero.
- **Why it is dimensionless-safe:** a `real`/`real` comparison against zero. Zero has no dimension,
  so there is no tolerance whose dimension could be wrong, and nothing to mis-unit.
- **What the human is on the hook for:** that `quantity` is bound to a **power**. Binding a
  non-power into `quantity` would be admitted silently.

### A3 `parasitic_fraction_ok` — `part_power > whole_power * lower_frac and part_power < whole_power * upper_frac`

- **Operands:** `part_power` ← `net_electric.p_parasitic_total` and `whole_power` ←
  `gross_electric.p_electric_gross`, **both powers in MW**. `lower_frac = 0.10` and
  `upper_frac = 0.90` are **dimensionless fractions**.
- **Why it is dimensionless-safe:** the comparison is power against power-times-fraction, so both
  sides carry the same dimension and the band edges are genuinely dimensionless. No tolerance here
  has a dimension that could be wrong.
- **What the human is on the hook for — the operand pair as well as the tolerance dimension.**
  This is the sharper obligation. Binding a **non-power into `whole_power`** would be admitted
  silently and would produce a gate that compares incommensurable quantities while reporting
  cleanly. No toolchain check catches it. The pairing of `part_power` and `whole_power` as *the
  same kind of quantity* is a human guarantee, not a checked one.

---

## Authority

- **Ruled disposition table:** `.project/completed/20260813_catf-constraint-policy-acceptance/owner-disposition.md`
  (RULED 2026-08-13) — sole source of intent classes, tolerance values, deletion authority, and bases.
- **Spec / design / plan:** the same item home. SC-3's identity is `65 = 58 + 7`.
- **Integrity check:** `scripts/check_gated_manifest.py --check`, license-free.
- **Population expectation:** `tests/expectations/constraint_population/catf_mfe_gated.json`,
  committed **before** this fixture existed (SC-6).
- **Coverage expectation:** `tests/unit/data/expected-coverage.md`, ledger row `catf_mfe_gated`.
