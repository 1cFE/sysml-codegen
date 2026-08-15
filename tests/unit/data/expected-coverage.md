# Expected Coverage Ledger (PD2)

**Epic:** CONSTRAINT-SEMANTICS, Item 3
**Created:** 2026-08-13 (Phase 0), extended Phase 1
**Authority:** the design's D3 bucket table, applied to each fixture's `.sysml` source.

## The expectation rule (PD2, DR-6)

Every account below is derived from **what the author wrote** — the fixture's SysML source read
against D3's bucket table — never transcribed from a catalog dump, a generated report, or Item 2's
disposition table. Each entry cites the file and line of every constraint usage it counted.

Reading the projected catalog to confirm *which usages a model declares* is a legitimate cross-check
of the source reading, and was used that way in the Phase 0 corpus probe. Reading it to obtain *the
counts* is the shortcut this rule forbids, and no entry below does it.

## D3's bucket table, restated for the reader

Two predicates decide the bucket:

- **asserted** ≡ the declaration is `assert constraint …` (source forms `definition_typed`, `inline`,
  `named_usage_reference`). A bare `constraint …`, a `require constraint …` inside a requirement, and
  a `satisfy` reference are **not** asserted.
- **inapplicable** ≡ the usage's doc comment carries an `@inapplicable:` marker.

| # | asserted | inapplicable | reaches an occurrence | bucket | contributes to |
|---|---|---|---|---|---|
| 1 | no | either | either | inventory only | `authored_usage_total` |
| 2 | yes | yes | either | inapplicable gate | `authored_usage_total`, `inapplicable_gate_count` |
| 3 | yes | no | yes (and admitted by the profile) | assessed gate | `authored_usage_total`, `applicable_gate_total`, `assessed_gate_count` |
| 4 | yes | no | no, or blocked by the profile | unassessed gate | `authored_usage_total`, `applicable_gate_total`, `unassessed_gate_count`, `unassessed_reasons[reason] += 1` |

`coverage_state` is `complete` when `applicable_gate_total > 0 and unassessed_gate_count == 0`,
`partial` when `applicable_gate_total > 0 and unassessed_gate_count > 0`, `none` when
`applicable_gate_total == 0`.

Headline (D6, over runtime statuses **and** the account): `violation` → `indeterminate` →
`full_satisfaction` (iff `unassessed_gate_count == 0 and assessed_gate_count > 0`) →
`partial_coverage` (iff `applicable_gate_total > 0`) → `not_assessed`.

---

## Ledger

Field order in every entry: `authored_usage_total` / `applicable_gate_total` / `assessed_gate_count` /
`unassessed_gate_count` / `inapplicable_gate_count` / `unassessed_reasons` / `coverage_state`.

### `fusion_tea` — the whole-dump site (`tests/execution/test_fusion_tea_real_teax.py:245`)

**Source evidence.** One constraint *usage* is declared in the whole fixture tree:

- `designs/generic_ife/ife_plant.sysml:155` — `assert constraint viability : 'Viability Threshold'`,
  inside `part def 'IFE Power Plant'`, which the model instantiates.

The other three grep hits are not usages:
`library/analyses/fusion_cycle.sysml:29` is `constraint def 'Viability Threshold'` — a *definition*;
`designs/generic_ife/ife_plant.sysml:159` and `designs/hif_ife/hif_plant.sysml:223` are prose inside a
doc comment and a `//` comment respectively.

**The open check from the design, resolved.** `hif_plant.sysml:223` reads
`// viability constraint is inherited from IFE Power Plant`. It is a comment; the HIF design declares
no second usage. The account is for **one** usage.

Asserted, not marked inapplicable, owner instantiated → bucket 3.

| field | value |
|---|---|
| `authored_usage_total` | 1 |
| `applicable_gate_total` | 1 |
| `assessed_gate_count` | 1 |
| `unassessed_gate_count` | 0 |
| `inapplicable_gate_count` | 0 |
| `unassessed_reasons` | `{}` |
| `coverage_state` | `"complete"` |

`headline = "full_satisfaction"`, `assessed_entry_count = 1`.

### `gate_a_d5` — bare-assert site (`test_constraint_verdicts_exact_route.py:171`)

**Source evidence.** `model.sysml:57` — `assert constraint viability : 'Viability Threshold'` inside
`part def Host`; `model.sysml:54` instantiates `part the_host : Host`. `model.sysml:21` is a
`constraint def`, not a usage. One usage, bucket 3.

**1 / 1 / 1 / 0 / 0 / `{}` / `complete`** → `headline = "full_satisfaction"`, `assessed_entry_count = 1`.

### `constraint_multi_instance` — bare-assert site (`:416`), and the two-tier asymmetry (DR-12)

**Source evidence.** `model.sysml:24` — `assert constraint nonneg : 'Nonneg Power'` inside
`part def Cell`; `model.sysml:30` declares `part cell : Cell [3]`, so the one authored usage expands to
three occurrences. `model.sysml:9` is a `constraint def`. One usage, bucket 3.

**1 / 1 / 1 / 0 / 0 / `{}` / `complete`** → `headline = "full_satisfaction"`,
**`assessed_entry_count = 3`**.

This is the deliberate asymmetry: `assessed_gate_count = 1` (usage tier) beside
`assessed_entry_count = 3` (occurrence tier). It is the two-tier rule working, not a defect.

### `constraint_def_owned_redefining` — bare-assert site (`:540`)

**Source evidence.** `model.sysml:27` — `assert constraint within : 'Within Limit'` inside
`part def Panel`; `model.sysml:39` instantiates `part panel : Panel`. `model.sysml:14` is a
`constraint def`. One usage, bucket 3.

**1 / 1 / 1 / 0 / 0 / `{}` / `complete`** → `headline = "full_satisfaction"`, `assessed_entry_count = 1`.

### `catf_mfe_d5` — descriptive-only (frozen twin, not edited)

**Source evidence — the two documented greps, re-run 2026-08-13** over
`tests/fixtures/catf_mfe_d5/**/*.sysml`:

- `assert constraint` → **0**
- `^\s*constraint def ` → **0**
- bare `^\s*constraint <name>` declarations → **65**

(70 source lines mention the word `constraint`; the other 5 are prose.) All 65 are bare `constraint`
usages — not asserted — so all 65 land in bucket 1 and nothing reaches the denominator.

**65 / 0 / 0 / 0 / 0 / `{}` / `none`** → `headline = "not_assessed"`, `assessed_entry_count = 0`.

This is the shape that motivates the item: 65 authored checks, none assessed, and today the package
emits no report at all.

### `catf_mfe_gated` — the CATF derivative, three executing gates

**Derived from the ruled disposition table, not from a run** (CONSTRAINT-SEMANTICS Item 5;
`.project/completed/20260813_catf-constraint-policy-acceptance/owner-disposition.md`, RULED 2026-08-13).
Committed before the fixture that produces it existed — that commit order is SC-6's evidence.
Restated by Item 9, which executed the held intent for A5, A6 and A9 once Item 8 (`62a07e5`)
cured the unit-lane defect that had parked them. Every number below is re-derived from the same
ruled table and committed before the run that confirms it.

**The population: 56 carriers.** `65 = 56 carriers + 9 named deletions` (7 derive-instead —
A1, A4, A5, A6, A7, A8, C37; 2 O2 placeholder deletions — C21, C28). Every counted usage, by
`file:line` in the derivative:

- **3 asserted, executing** — `designs/catf_mfe/physics.sysml:126`
  (`catf_physics::net_power_viable`, A2, renamed from `ViabilityCheck`),
  `physics.sysml:134` (`catf_physics::parasitic_fraction_ok`, A3, renamed from
  `ReasonableParasiticTotal`), and `designs/catf_mfe/vacuum.sysml:171`
  (`catf_vacuum_pumping::pumping_speed_agrees`, A9, renamed from `PumpingSpeedConsistency`).
  All three are `assert constraint … : <def>` over `library/constraints/gate_forms.sysml`,
  bindings-only, chains in binding position.
- **0 plain, reaching** — A5 and A6 left the population by deletion, their ruled derivations now
  authored in `radial_build.sysml`, and A9 moved from this bucket to the asserted one. The
  D-S1/D-S2 parking is retired.
- **5 plain, part-definition-owned** — `library/components/divertor.sysml:216`,
  `first_wall.sysml:220`, `radial_build.sysml:55`, `shield.sysml:160`, `vacuum.sysml:155`
  (B1–B5). No design part is typed by any of these definitions, so they reach zero instances.
- **48 plain, calculation-definition-owned** — Group C minus C37, C21, C28, spread across
  `library/analyses/thermal_loads.sysml` and `library/physics/{confinement,geometry,
  neutronics,performance_metrics,power_balance,thermal}.sysml`. No calc-def attachment
  capability exists (Item 6), so they reach nothing structurally.

**Why `applicable_gate_total` is 3 and not 56.** The feasibility denominator is applicable
asserted gates only (rulings-20260812 L2-1). The 53 plain usages are bucket 1 — "not asserted
→ inventory only" — so they appear in `authored_usage_total` and never in the denominator.

**Why `inapplicable_gate_count` is 0 and not 5.** This is the trap in this entry, and the
number is 0 for a structural reason rather than an authoring accident. B1–B5 carry an
inapplicability *disposition*, but they are **plain** usages, and bucket row 1 is decided
before the inapplicable predicate is ever consulted (`generation/coverage.py:7-27`). A usage
only reaches bucket 2 by being asserted *and* marked. None of the five is asserted, so all
five land in bucket 1 and the inapplicable count stays 0. (Measured separately in Item 5
Phase 1: the marker cannot even reach the domain on their inline-predicate shape, so the
disposition is recorded in PROVENANCE. That finding does not change this number — the count
is 0 with or without a marker.)

**Why `assessed_entry_count` is 3.** A2 and A3 hang off `catf_physics` and A9 off
`catf_vacuum_pumping`; each of those parts has one occurrence, so each eligible usage mints
exactly one concrete entry: 1 + 1 + 1 = 3.

**56 / 3 / 3 / 0 / 0 / `{}` / `complete`** → `headline = "violation"`,
`assessed_entry_count = 3`.

**A9 does not move the headline.** Its band is satisfied at the authored design point —
`pumping_speed_total = 200` against `n_pumps * pump_capacity_each = 48 × 4.17 = 200.16`, a
0.08% disagreement inside the ruled 1% relative band — so it adds a satisfied gate. The
`violation` headline stays A2's.

**Amended 2026-08-13 under finding 6-D** (`[AGENT]`, ratified by owner). The headline cell was
`full_satisfaction` when this entry was first committed, on the assumption that the model's own
authored design point satisfies its gates. It does not, and the coverage numbers are untouched
by the correction — only the headline moves, because coverage is about the denominator and the
headline is about the outcome.

**The basis is a source-derived computation, not an observed run.**
`.project/completed/20260813_catf-constraint-policy-acceptance/cryo_derivation.py` re-derives
`MagnetCryogenicLoad.cooling_power` from the model's own constants and formulas
(`library/analyses/thermal_loads.sysml:55-66`, `designs/catf_mfe/magnets.sysml:86-94`):

```
nuclear_heating   = 0.05 * 2079.41 * (15.31526418625125 / 31.101767270540993) =   51.197595 MW
heat_leak         = 2334.4698659954747 * 0.05                                 =  116.723493 MW
thermal_load_cryo =                                                              167.921088 MW  at 20 K
amplification     = 300 / (20 * 0.3)                                          =        50.0x
cooling_power     = 167.921088 * 50                                           = 8396.054399837172 MW
```

Against `p_electric_gross = 1546.723690193402 MW`, the magnet cryoplant draws **5.43× the whole
plant's gross electric output**, so `p_electric_net_out` is negative at the authored inputs and
**A2 reports `violated`**. A3's parasitic band is violated for the same reason. The derivation
reproduces the executed value bit-exactly, which is what licenses it as the basis.

The authored candidate is therefore **gate-infeasible under the model as authored**, and it is
the *rejected* candidate for SC-5. A raised-`p_fusion` candidate (≥ 20000 MW satisfies both
gates) carries the satisfied path as a **machinery exemplar, not a recommended design**.

The cryogenic heat-leak coefficient itself is a model defect, filed as backlog
`[CATF-CRYO-HEAT-LEAK-COEFFICIENT]`; correcting it is a separately-authorized follow-on. It reproduces on
the untouched `catf_mfe_d5`, so it is not this derivative's doing — d5 simply executes no gates,
which is why it went unseen.

### `constraint_domain_plain_forms` — non-asserted inventory

**Source evidence.** `model.sysml:15` — `constraint blocked_if_asserted` (bare, inside
`part def Host`, instantiated at `:27`); `model.sysml:22` — `constraint unreached_plain` (bare, inside
the never-instantiated `part def Detached`). Neither is asserted → both bucket 1.

**2 / 0 / 0 / 0 / 0 / `{}` / `none`** → `headline = "not_assessed"`, `assessed_entry_count = 0`.

Note the contrast with `catf_mfe_d5`: whether the owner is instantiated does not matter for a
non-asserted form. Bucket 1 is decided by the form alone.

### `constraint_domain_satisfy` — requirement-side inventory

**Source evidence.** `model.sysml:16` — `require constraint within` inside a requirement definition
(`requirement_constraint`); `model.sysml:25` — a `satisfy` reference on `part the_rig`
(`satisfy_reference`). Neither form asserts → both bucket 1.

**2 / 0 / 0 / 0 / 0 / `{}` / `none`** → `headline = "not_assessed"`, `assessed_entry_count = 0`.

### `constraint_domain_detached_owner` — mixed partial (reused for the `partial_mixed` shape, PD4)

**Source evidence.** `model.sysml:14` — `assert constraint vacuous_gate` inside `part def Detached`,
which nothing instantiates → asserted, not marked, reaches nothing → bucket 4, reason
`owner_has_no_occurrences`. `model.sysml:21` — `assert constraint reached_gate` inside `part def Live`,
instantiated at `:26` → bucket 3.

**2 / 2 / 1 / 1 / 0 / `{"owner_has_no_occurrences": 1}` / `partial`**
→ `headline = "partial_coverage"`, `assessed_entry_count = 1`.

The assessed gate passes, and full satisfaction is still unclaimable. That is spec success criterion 3.

### `constraint_non_numerical` — partial by profile exclusion

**Source evidence.** Both usages are asserted and both owners are instantiated
(`part the_host : MixedPurposeHost`, `model.sysml:22`). `model.sysml:13` —
`assert constraint status_annotation`, whose predicate is a non-numerical equality the executable
profile does not admit → bucket 4, reason `non_numerical`. `model.sysml:17` —
`assert constraint positive_value` → bucket 3.

**2 / 2 / 1 / 1 / 0 / `{"non_numerical": 1}` / `partial`**
→ `headline = "partial_coverage"`, `assessed_entry_count = 1`.

This is the row-4 case that is *not* about reachability: an asserted gate the profile excluded stays in
the denominator as an unassessed one.

### `constraint_domain_inapplicable` — Appendix C's vacuous-gate cell, non-degenerate

**Source evidence.** `model.sysml:19-20` — `assert constraint marked_vacuous : Positive` whose doc
comment carries `@inapplicable: no build of this variant is planned`, inside the never-instantiated
`part def Detached` → asserted **and** marked → bucket 2. `model.sysml:27` —
`assert constraint reached_gate` inside `part def Live`, instantiated at `:32` → bucket 3.

**2 / 1 / 1 / 0 / 1 / `{}` / `complete`** → `headline = "full_satisfaction"`,
`assessed_entry_count = 1`.

The marked gate drops out of the denominator and one gate remains, so full satisfaction is claimable —
Appendix C's cell read with its antecedent satisfied. D4 rules only the degenerate case, below.

---

## New fixtures authored for this item (Phase 1)

Named `constraint_coverage_*`. One shape per fixture (PD4).

**A parser constraint the authoring had to work around.** The `@inapplicable:` marker is read off
the usage's owned `Comment` members, and SysIDE drops a `doc` comment written inside an
*inline-predicate* constraint body — the gap `test_constraint_population_oracle.py`'s rule 3 exists
to make loud. Measured again here: the marker did not reach the domain on the inline form and did on
the definition-typed form. So both marked fixtures below are authored as
`assert constraint <name> : Positive { doc /* @inapplicable: … */ in v = <attr>; }`. That changes
`source_form` from `inline` to `definition_typed`; both are in `ASSERTED_SOURCE_FORMS`, so no bucket
and no account field moves.

### `constraint_coverage_zero_eligible` — asserted gates, zero eligible entries

**Source.** `model.sysml:18` — `assert constraint unreached_gate` (inline) inside `part def Detached`,
which nothing instantiates. The only other content is a live part with a calc and no gate. Asserted,
unmarked, reaches nothing → bucket 4.

**1 / 1 / 0 / 1 / 0 / `{"owner_has_no_occurrences": 1}` / `partial`**
→ `headline = "partial_coverage"`, `assessed_entry_count = 0`.

The zero-input aggregator's *partial* branch: a report with an empty input set that still says the
model has an unchecked gate. Today this model emits no report at all.

### `constraint_coverage_all_inapplicable` — D4's ruling

**Source.** `model.sysml:28` — `assert constraint waived_gate : Positive` whose doc comment carries
`@inapplicable: this variant is documentation only`, inside the never-instantiated `part def
Detached`. No other constraint usage. Asserted and marked → bucket 2, and nothing lands in bucket 3
or 4.

**1 / 0 / 0 / 0 / 1 / `{}` / `none`** → `headline = "not_assessed"`, `assessed_entry_count = 0`.

D4: the full-satisfaction arm requires `assessed_gate_count > 0`, so zero assessments cannot claim it.
`inapplicable_gate_count = 1` is what distinguishes this from a descriptive-only model, whose
`inapplicable_gate_count` is `0`.

### `constraint_coverage_violation_partial` — spec success criterion 2

**Source.** `model.sysml:21` — `assert constraint failing_gate { reading > 10.0 }` inside
`part def Live`, instantiated at `:33`, with `reading` modelled `3.0` at `:20`. `3.0 > 10.0` is
false, margin `-7.0` — derived here, not read back. `model.sysml:30` — `assert constraint
unreached_gate` inside the never-instantiated `part def Detached`.

**2 / 2 / 1 / 1 / 0 / `{"owner_has_no_occurrences": 1}` / `partial`**
→ `headline = "violation"` (the top precedence arm), `coverage_state = "partial"`,
`assessed_entry_count = 1`.

Coverage survives a higher-precedence headline: the report says "rejected on physics, *and* one gate
was never checked", which is the distinction the study policy needs.

### `constraint_coverage_eligible_inapplicable` — D9's refusal (generation must fail)

**Source.** `model.sysml:25` — `assert constraint live_but_marked : Positive` whose doc comment
carries `@inapplicable: this gate is not part of the feasible set`, inside `part def Live`,
instantiated at `:29`. Asserted, marked, and it expands → `disposition_kind == "eligible"` beside
`inapplicability_reason is not None`, which `tests/unit/test_coverage_fixture_shapes.py` pins as the
combination on a single record.

**No account.** Generation refuses by name at the coverage preflight, before any output is written:
*"`<usage QN>` (`<declaration_id>`) is marked inapplicable but produced `<n>` executable entries…"*.
This fixture is registered wherever a corpus sweep enumerates fixtures, so a sweep expects the refusal.

---

---

## Ledger index — the machine-readable form

One line per fixture, in the field order used throughout: `authored_usage_total /
applicable_gate_total / assessed_gate_count / unassessed_gate_count / inapplicable_gate_count /
unassessed_reasons / coverage_state / headline / assessed_entry_count`.

`tests/unit/test_coverage_ledger_agreement.py` parses this block and asserts
`coverage_account()` reproduces every line. The prose entries above are the derivation and the
evidence; these lines are the same numbers in a form a test can read, so the two cannot drift apart
silently. `constraint_coverage_eligible_inapplicable` has no line: generation refuses it.

```ledger
fusion_tea                            | 1 | 1 | 1 | 0 | 0 | {} | complete | full_satisfaction | 1
gate_a_d5                             | 1 | 1 | 1 | 0 | 0 | {} | complete | full_satisfaction | 1
constraint_multi_instance             | 1 | 1 | 1 | 0 | 0 | {} | complete | full_satisfaction | 3
constraint_def_owned_redefining       | 1 | 1 | 1 | 0 | 0 | {} | complete | full_satisfaction | 1
constraint_domain_inapplicable        | 2 | 1 | 1 | 0 | 1 | {} | complete | full_satisfaction | 1
catf_mfe_gated                        | 56 | 3 | 3 | 0 | 0 | {} | complete | violation | 3
catf_mfe_d5                           | 65 | 0 | 0 | 0 | 0 | {} | none | not_assessed | 0
constraint_domain_plain_forms         | 2 | 0 | 0 | 0 | 0 | {} | none | not_assessed | 0
constraint_domain_satisfy             | 2 | 0 | 0 | 0 | 0 | {} | none | not_assessed | 0
constraint_coverage_all_inapplicable  | 1 | 0 | 0 | 0 | 1 | {} | none | not_assessed | 0
constraint_domain_detached_owner      | 2 | 2 | 1 | 1 | 0 | {owner_has_no_occurrences: 1} | partial | partial_coverage | 1
constraint_non_numerical              | 2 | 2 | 1 | 1 | 0 | {non_numerical: 1} | partial | partial_coverage | 1
constraint_coverage_zero_eligible     | 1 | 1 | 0 | 1 | 0 | {owner_has_no_occurrences: 1} | partial | partial_coverage | 0
constraint_coverage_violation_partial | 2 | 2 | 1 | 1 | 0 | {owner_has_no_occurrences: 1} | partial | violation | 1
```

## Corpus probe cross-check (Phase 0, read-only)

The Phase 0 probe elaborated and projected every fixture directory that elaborates standalone (57 of
104) and scanned all 105 resulting usage records. It was used to confirm *which usages each model
declares*, never to obtain a count. Two results:

- **B3 holds.** `catf_mfe_d5`, `constraint_domain_plain_forms`, `constraint_domain_satisfy`, and
  `constraint_domain_satisfy_calc_def` all project a non-`None` `constraint_catalog` with non-empty
  `usage_records` and zero `eligible` rows. D5's trigger is readable from the catalog.
- **D9 breaks nothing that exists.** Zero of the 105 records are both `eligible` and carry an
  `inapplicability_reason`. The marker appears in five fixtures; four of them refuse elaboration
  already (they are negative fixtures), and in `constraint_domain_inapplicable` the marker sits on a
  `non_reaching` record.
