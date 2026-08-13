# Design: CATF Derivative and End-to-End Acceptance

**Status:** Draft — **D-S1/D-S2 RULED 2026-08-13 (option 3, [AGENT] ratified): land the landable
shape now; A5/A6/A9 blocked-by-defect as visible plain usages; identity restated 65 = 58 + 7;
unit-lane defect filed as its own epic item**
**Owner:** Reid W
**Created:** 2026-08-13 · **Branch:** `item7-rebuild` @ `488747b`
**Epic:** CONSTRAINT-SEMANTICS, Item 5

---

## Overview

Fork `catf_mfe_gated` from `catf_mfe_d5`, author the owner-ruled dispositions into it, and prove a
physics rejection through the real TEAx route. Design-stage probes found that three of the ruled
rows (A5, A6, A9) cannot be authored at all against the current projection. That was surfaced
rather than worked around, and it is now **ruled**: land the landable shape, retain the three as
visible plain usages with their intent held, and file the defect as its own epic item.

## Related Artifacts

- **Spec:** `spec.md` (SC-1 met, SC-3 amended to the accounting identity)
- **Ruled table:** `owner-disposition.md` — RULED 2026-08-13, sole authority for intent classes,
  tolerances, deletion authority, and bases
- **Product-lens:** `product-lens.md` (item5-F1 resolved; F2–F5 folded into the spec)
- **Contract as landed:** `docs/architecture/modeling-assumptions.md` §8, §9
- **Items 2–3 close records:** `.project/completed/20260813_constraint-catalog-totality/`,
  `.project/completed/20260813_constraint-coverage-policy/`
- **Probes (throwaway):** `probes/` in this item home
- **TEAx:** `/home/reid/1cfe/teax`, branch `constraint-semantics-item3` @ `5b70ae9`
  — *verified by the orchestrator 2026-08-13, not first-hand in this session*

---

## The Point

A design search must be able to tell a candidate that **passed its physics gates** from one
**nobody checked**. That is the obligation, and it is owner-grade:

> **[OWNER]** A design search can trust the generated feasibility evidence to represent every
> applicable asserted physics gate, while every other authored constraint remains visibly
> dispositioned.
> (`.project/backlog/epic_constraint_semantics_contract.md`, Critical Success Factor)

Items 1–4 built the machinery against purpose-built fixtures. Nothing has driven it end to end on
the richest model we have — and that model, `catf_mfe_d5`, is the failure case the epic exists to
close: 65 authored constraint usages, 9 reaching, **0 executed**. Until a real physics mutation
travels generated package → TEAx normalization → policy → durable case record and comes back
`reject`, the critical success factor is an assertion.

Two totals must never be conflated, and this item is where they meet a real model: **inventory
totality** over all 65 authored usages, and **feasibility coverage** over applicable asserted gates
only.

---

## Research Findings

### The probes (all run this session, licensed, throwaway)

Scratch copies of `catf_mfe_d5` under `/tmp/item5probe/`, elaborated through
`build_elaborated_pipeline`. Harness in `probes/`. Nothing committed; both frozen twins untouched.

| probe | shape | result |
|---|---|---|
| **P1** | A2 asserted via fixture-local `PositiveQuantity` | **ADMIT** — 44 modules, 1 concrete entry, 8 excluded, 65 usage rows |
| **P2** | P1 + A3 asserted via `FractionWithinBand`, both chains in **binding** position | **ADMIT** — 45 modules, 2 concrete entries |
| **P3 / P3b** | A9 asserted via relative-form `ProductWithinBand` | **REFUSED** — `SI_RENDERING_COLLISION` on `CATFMFEVacuum__catf_vacuum_pumping__n_pumps` |
| **P4a / P5** | One radial-build layer derived (`outer_radius = inner_radius + thickness`), with and without the `[m]` literal | **REFUSED** — `SI_RENDERING_COLLISION` on `…plasma_region__inner_radius` |
| **P6** | A7 (gamma fraction), A8 (vessel outer radius), A6's axis-region layer | **ADMIT** — 46 modules |
| **P7** | Composite landable set: library + A2 + A3 + A7 + A8 + axis leg | **ADMIT** — **48 modules, 2 executing gates**, 65 usage rows, 7 excluded |

### The one defect behind both refusals

Chased to source, not inferred. A single design attribute reached by two consumers refuses the
whole model when the consumers disagree about **unit text**:

- A calc-usage binding takes its port unit from the **calc def formal's trailing comment**
  (`in attribute pump_count : Real;  // Dimensionless`), so the entry point is minted carrying a
  unit.
- A **constraint formal** binding carries `unit=None` **by construction** — the metadata builder
  only consults the attribute lane for a `CalcNode`
  (`src/sysml_codegen/elaboration/elaborate.py:1678-1689`).
- A **computed design attribute** expression (`= inner_radius + thickness`) reaches the same code
  path with `formal_provenance=None` and likewise no unit.

Projection then compares the two `EntryPoint` candidates field by field and fails
(`src/sysml_codegen/elaboration/project.py:394-397`).

**There is no authoring dodge.** P3b gave the constraint-def formals matching unit comments — the
comment is not read for a constraint formal, so `unit` stayed `None`. P5 stripped the `[m]`
literals from the attribute declarations — the surviving `'m'` came from the *calc def's* comment,
not the attribute's, so the collision stood. The only remaining lever is editing the shared library
calc defs' unit comments, which changes semantics for every model that imports them.

**Blast radius, measured.** All 13 non-axis radial-build layers bind **both** `inner_radius` and
`outer_radius` into `calc minor_calc : TorusMinorRadius`
(`designs/catf_mfe/radial_build.sysml:96-565`). So 26 of A5/A6's 27 derived radii are exactly the
colliding case. `catf_vacuum_pumping`'s `n_pumps` and `pumping_speed_total` both feed
`calc pump_load : VacuumPumpPower`, which is A9's case.

### Codebase pattern reuse

- **Expected-output precedent (SC-6):** Item 3's ledger lives at `tests/unit/data/expected-coverage.md`,
  parsed (not transcribed) by `tests/unit/test_coverage_ledger_agreement.py`. The `[OWNER 2026-08-13]`
  ruling moved it beside its test so suite collection never depends on archive layout.
- **Population oracle:** `tests/expectations/constraint_population/<fixture>.json`, asserted by
  identity list in `tests/conformance/test_constraint_population_oracle.py`. A constraint-bearing
  fixture with no expectation file fails that suite by name.
- **Variant integrity precedent:** `scripts/make_d5_variant.py --check` + `tests/conformance/test_d5_variants.py`
  — a mechanical, license-free, reversible proof rather than a diff review.
- **"Byte baselines" are not byte gates.** `tests/fixtures/baseline_outputs/` (13 directories) has
  exactly one reader, `tests/conformance/test_baselines.py`, which never regenerates anything — its
  `model_dir` parameter is accepted and unused, and the widening test only checks each committed JSON
  against itself. `tests/fixtures/baseline_yaml/` has no reader at all. Every real byte gate at HEAD
  compares **two runs of the same route**, not a run against committed bytes. This drives D7.

---

## Core Concept

The derivative is a **worked example of the ruled policy, authored in one atomic landing, whose
every difference from `catf_mfe_d5` is a named record that a script can reconcile against the ruled
table.**

Three ideas carry it.

**The table is the compiler input; the fixture is its output.** Nothing in the derivative is
invented. Every asserted gate, every deletion, every derivation traces to a row in
`owner-disposition.md`. That is what makes the integrity check possible at all: byte-reversal cannot
transfer to a fixture that deliberately differs, but the **accounting identity** can — a script
joins the derivative's catalog against the ruled table and proves `65 = carriers + named deletions`,
row by row.

**Expected before actual, proved by commit order.** The catalog, coverage, and study outcomes are
derived from the ruled table and committed *before the derivative exists to produce them*. This is
the owner's sequence, and it is the only thing that stops an expectation from being
reverse-engineered out of a dump.

**Landing is all-or-nothing, so authoring is probe-first.** A profile BLOCK on any asserted
constraint halts the whole model (`elaborate.py:488`), and — as the probes found — so does a
projection collision. There is no partial state. So the design's job is to establish, *before* the
fixture exists, exactly which edits generate. That job ran, and it came back with two refusals.

---

## SURFACED — two ruled rows cannot be authored (capture-fidelity §4)

**RULED 2026-08-13 — option 3, adopted as recommended, [AGENT] (ratified by owner, 2026-08-13):**
Item 5 lands on the landable shape now. A5/A6/A9 are retained as visible plain usages,
dispositioned `blocked-by-defect` in the ruled table and PROVENANCE only (no new catalog reason
token — catalog rows stay within Item 2's closed vocabulary). Their ruled basis cells and A9's
1%-relative tolerance remain in force as recorded intent. The identity restates to
**65 = 58 carriers + 7 named deletions** (restatement owner-authorized as mechanical
consequence). The unit-lane defect is filed as its own small epic item (probe-characterized fix,
own tests, fingerprint/churn assessment + one-reviewed-recapture obligation if minted units move
on existing fixtures, Item 6 named as consumer); a follow-on item upgrades the derivative under
the already-ruled rows once it lands. SC-5 proceeds with A2 as anchor and A3 as the second
executing gate. At plan stage, the probe's 65-row composite is reconciled explicitly against the
ruled 58-carrier target so expected outputs pin the ruled shape.

The original surfacing record follows, kept as the evidence trail for the two findings.

### D-S1 — A9 cannot be asserted in any spelling

The ruled row makes A9 an `assert-band` at 1% relative tolerance. Binding `n_pumps` (or
`pumping_speed_total`) into any constraint formal refuses the model with `SI_RENDERING_COLLISION`,
because both attributes are already unit-carrying entry points of `calc pump_load`. Measured at
P3 and P3b. No formal naming, unit comment, or tolerance form changes it.

**Was parked, not worked around.** A shim attribute introduced solely to dodge the collision would
have been exactly the silent workaround the brief forbids. **Ruled:** A9 stays a plain usage,
`blocked-by-defect` in the table and PROVENANCE; its 1%-relative tolerance and cross-check intent
are held as recorded intent for the epic Item 9 upgrade.

### D-S2 — A5/A6 cannot be derived for 26 of 27 radii

The ruled basis (axis root radius + 14 thicknesses free, all radii derived) requires a computed
design attribute on every layer radius. 26 of the 27 refuse for the same reason: each layer's
`inner_radius` and `outer_radius` are already unit-carrying entry points of that layer's
`minor_calc`. Measured at P4a and P5. Only `axis_region.outer_radius` — the one layer with no
geometry calc on it — derives cleanly (P6).

**Ruled.** A5/A6 stay plain usages, `blocked-by-defect`; the axis-region leg is *not* derived either,
so the radial build keeps one consistent basis rather than a half-migrated one. The ruled basis
(axis root radius + 14 thicknesses free) is held as recorded intent. Note the shape of the trap: the
derivation is *correct modeling* and the constraint it replaces is *correct policy*; the toolchain
refuses the combination.

### The accounting identity in force

**65 = 58 carriers + 7 named deletions** (`[OWNER 2026-08-13]` restatement, mechanical consequence
of the option-3 ruling). The 7 deletions: **A1, A4, A7, A8, C37** (derive-instead) + **C21, C28**
(O2 placeholders). A5, A6 and A9 move out of the deletion column and into the carrier column.

The 58 carriers break down as:

| carrier class | count | rows |
|---|---|---|
| asserted, executing | **2** | A2, A3 |
| plain, `blocked-by-defect` (intent held) | **3** | A5, A6, A9 |
| plain, `@inapplicable:`-marked part-def guards | **5** | B1–B5 |
| plain, `awaits-capability` calc-def guards | **48** | Group C minus C37, C21, C28 |

This is the shape every expected output pins.

### The expected coverage account, derived from the ruled shape

Derived from the ruled table against `coverage.py`'s bucket rule, before any run. **The five
`@inapplicable:` markers sit on *plain* usages, and bucket row 1 ("not asserted → inventory only")
is decided before the inapplicable predicate is consulted** (`generation/coverage.py:7-27`). So
`inapplicable_gate_count` is **0, not 5** — this is the single most likely place for an expectation
to be written wrong, and the plan inherits it as a fact, not a guess.

| field | value |
|---|---|
| `authored_usage_total` | 58 |
| `applicable_gate_total` | 2 |
| `assessed_gate_count` | 2 |
| `unassessed_gate_count` | 0 |
| `inapplicable_gate_count` | **0** |
| `unassessed_reasons` | `{}` |
| `coverage_state` | `complete` |

Headline `full_satisfaction` for the valid candidate; `violation` for the SC-5 mutation.

The three `blocked-by-defect` carriers catalog exactly as they do in `catf_mfe_d5` today —
`excluded`, `unassessed form` — because they are still plain usages and Item 2's disposition
vocabulary is closed. Nothing in the catalog distinguishes them from any other plain usage. **What
distinguishes them is their PROVENANCE record** (C3 below); that is where "visibly dispositioned"
actually lives for these three.

---

## Key Bets

- **B1.** The two refusals are one defect with one cause — port metadata for non-calc consumers
  carries no unit — and not three coincidences. *If false → fixing the named seam does not unblock
  A5/A6/A9, and the parked threads need separate diagnosis before any of them lands.*
- **B2.** The landable set (P7: 48 modules, 2 executing gates) is stable under **every** remaining
  edit — the A1 and C37 calc-def derivation, the A4 deletion, the C21/C28 placeholder deletions, the
  A7/A8 derivations, and the five `@inapplicable:` markers — with no new collision. *If false → the
  atomic landing fails on the first real authoring pass and the probe-first premise has to be re-run
  at fixture scale.* **P7 covered only part of this**: it deleted nothing and left A1/C37 alone, so
  the de-risk re-probe below must carry the full edit set, not just markers and deletions.
- **B3.** A2 carries SC-5: mutating `p_fusion` propagates through seven calc modules into
  `p_electric_net_out` and crosses zero. *If false → SC-5 falls back to A3 alone, whose band the
  owner explicitly recorded as a plausibility envelope that does not gate viability — a weaker
  proof of the same criterion.*
- **B4.** The accounting identity is machine-checkable from committed artifacts alone — the ruled
  table's rows join 1:1 against the derivative's catalog plus PROVENANCE records, **including across
  the two renamed carriers**. *If false → SC-2's "machine-checkable diff" degrades to a human diff
  review, which is what byte-reversal existed to avoid.*

## Key Decisions

- **D1. Fixture name `catf_mfe_gated`**, forked from `catf_mfe_d5`, sibling directory under
  `tests/fixtures/`. *Rejected: `catf_mfe_d5_gated` (reads as a d5 variant, and `make_d5_variant.py`
  owns that suffix family — a name collision with a mechanical check that does not apply).*
- **D2. Integrity check is an accounting-identity manifest, not a byte reversal.**
  `scripts/check_gated_manifest.py --check` joins three committed sources by usage identity: the
  ruled table's rows, `tests/expectations/constraint_population/catf_mfe_gated.json`, and the
  derivative's `PROVENANCE.md` records. It proves every d5 usage is either a carrier or a
  named deletion citing an authorizing row, and that `65 = 58 + 7` closes. License-free by
  construction.
  **The join key, including the renamed carriers.** Usage qualified name joins 56 of the 58 carriers
  directly. The two asserted gates are *renamed* by the rewrite — `…::ViabilityCheck` →
  `…::net_power_viable`, `…::ReasonableParasiticTotal` → `…::parasitic_fraction_ok` — so a name join
  would read them as one deletion plus one addition. Their PROVENANCE per-change record therefore
  carries an explicit `renamed_from:` field holding the d5 qualified name alongside the table row
  cite, and the script consults it before declaring an unmatched row. A carrier that matches neither
  by name nor by `renamed_from:` fails the check; a `renamed_from:` naming a d5 row that is also
  claimed by a deletion record fails it too. Mechanical in both directions.
  *Rejected: a raw provenance-diff manifest of changed lines (proves what changed, not that what
  changed was authorized — the authorization is the whole point here). Rejected: joining by
  `declaration_id` (it is content-derived, so a rewritten usage does not keep it — the rename is
  exactly the case it cannot bridge).*
- **D3. Unit approach, per gate (O4): both surviving gates take the dimensionless, unit-blind
  library band under human review.** The probes settled item5-F3 harder than the spec expected —
  a constraint formal *cannot* carry unit text at all, so the per-dimension in-predicate spelling is
  not merely incompatible with a shared library def, it is the only unit-carrying option and it
  costs one definition per dimension. A2 compares a power against the authored physical zero
  (`real`/`real`, nothing to mis-unit). A3's two edges are genuinely dimensionless fractions. Neither
  gate has a tolerance whose dimension could be wrong. The reasoning lands in the derivative's
  PROVENANCE per gate, citing the table row — not only in review conversation.
  *Rejected: per-dimension defs (`PowerWithinBand` etc.) — buys nothing for these two gates and
  multiplies the library by dimension count.*
- **D4. Derivation edit shape (O6) is a computed design attribute** — `attribute outer_radius : Real
  = inner_radius + thickness;` — replacing the literal in place. Measured working for A7, A8, and
  the axis leg (P6). The `[m]` literal is dropped and the unit moves to a trailing comment, matching
  the fixture's dominant idiom. *Rejected: `:>>` redefinition and calc-usage-plus-EXPOSE — both are
  heavier spellings of the same value flow, and the plain computed attribute is what the model
  already uses everywhere else.*
- **D5. Constraint-def library home (O7): `library/constraints/gate_forms.sysml`, package
  `CATFGateForms`, fixture-local.** Contents as landed: `PositiveQuantity`, `FractionWithinBand`.
  `ProductWithinBand` is **not authored** — its only consumer (A9) is parked. Graduation into
  published authoring guidance stays filed for Item 7 (item5-F4).
  *Rejected: a shared cross-fixture library (nothing else consumes it yet; premature).*
- **D6. SC-5 mutation lives in the generated `inputs/*.json`, not in the model.** The valid
  candidate is the authored `p_fusion = 2600.0`; the rejected one drops it until `p_electric_net_out`
  goes negative. One generated package, two input sets, two TEAx runs. *Rejected: a mutated fixture
  (a second model to keep in sync) and a study-config override (hides the mutation in harness
  config, which is precisely what the acausal-relations filing warns against).*
- **D7. SC-8's R3 baseline is a committed golden of the constraint-machinery files that
  `constraint_domain_satisfy_calc_def` generates, diffed byte-for-byte from its (new) committed v6
  snapshot.** Reworked from scratch after design review found the first version's premise false; the
  verification is below under "SC-8 — what R3 actually needs, verified at HEAD".
  *Rejected: a `tests/fixtures/baseline_outputs/` directory plus a `test_baselines.py::MODELS` row —
  measured at HEAD, that file never regenerates anything (`model_dir` is accepted and unused, and the
  glob test only checks each committed JSON against itself), and it is the sole reader of that
  directory. A row there would have added a self-consistency check and pinned no bytes.
  Rejected: putting the baseline on `catf_mfe_gated` — it ships two executing gates, so it is not the
  zero-entry shape R3 names.*

---

## SC-8 — what R3 actually needs, verified at HEAD

The first draft of D7 repeated R3's own wording — "a package whose constraint usages all fail to
reach, which correctly ships no `schemas/constraint_types.py`". **That wording is stale, and the
design review was right to reject it.** Three things checked at HEAD:

1. **The shape survived; its expected bytes inverted.** R3 was written inside Item 2's window, when
   the machinery bar was one *concrete entry*. Item 3 moved the bar to one *authored usage*
   (`resolution/models.py::ships_constraint_machinery`), so a zero-entry constraint-declaring package
   now **does** ship `schemas/constraint_types.py` and the registry's `ConstraintEvaluation` /
   `ConstraintReport` imports — and the aggregator it ships bakes an empty denominator
   (`applicable_gate_total: 0`, `authored_usage_total: 2`, `coverage_state: 'none'`). All four
   assertions are live at `tests/conformance/test_constraint_catalog_totality.py:109-120`.
2. **The fixture is still the right one.** `constraint_domain_satisfy_calc_def` genuinely has the
   shape — non-empty `usage_records`, empty `concrete_entries`. It carries only `model.sysml`, so it
   has no committed v6 snapshot yet.
3. **No committed-bytes gate exists anywhere in the tree.** Every byte gate at HEAD is a *two-run
   self-consistency* check (`test_exact_route_generated_package.py`, `test_public_route_baselines.py:125`,
   `test_exact_route_whole_tree_portability.py`, `test_v6_recapture_batch.py:76`) — they prove
   determinism, not that the bytes are the *right* bytes. `tests/fixtures/baseline_yaml/` is
   orphaned; `tests/fixtures/baseline_outputs/` has one reader that never regenerates.

So R3's residual is real and still open, and closing it needs a genuinely new mechanism rather than
a row in an existing table. **The minimal one:** capture a v6 snapshot for the fixture, commit a
golden of the two files that *are* the shape — `schemas/constraint_types.py` and
`modules/constraints/constraintreportaggregatormodule.py` — and add one conformance test that
regenerates from the committed snapshot and compares those files byte for byte, plus asserts the two
registry import lines. License-free, because the snapshot is committed.

Scoped to two files deliberately: a whole-tree golden would churn on every unrelated generator
change and would be abandoned within an item, which is how `baseline_yaml/` got orphaned. Two files
is the smallest set that actually pins "what a zero-entry package ships".

---

## Architecture

**Four artifacts, one direction of authority.**

```
owner-disposition.md  (RULED, authority)
        │
        ├──► tests/fixtures/catf_mfe_gated/           the worked example
        │        ├── designs/, library/               forked from catf_mfe_d5
        │        ├── library/constraints/gate_forms.sysml   (D5)
        │        ├── PROVENANCE.md                    per-change + 7 deletion + 3 parked records
        │        └── instance_graph_snapshot.json     sealed v6, for the license-free routes
        │
        ├──► tests/expectations/constraint_population/catf_mfe_gated.json   (population oracle)
        ├──► tests/unit/data/expected-coverage.md     one new ledger row (Item 3's home)
        └──► scripts/check_gated_manifest.py          joins all three, proves 65 = 58 + 7 (D2)

separately, SC-8:
     tests/fixtures/constraint_domain_satisfy_calc_def/instance_graph_snapshot.json  (new)
     tests/conformance/<golden>.py + committed golden of the two machinery files      (D7)
```

**Nothing flows backwards.** The catalog is read to cross-check *which usages exist*, never to
obtain counts — Item 3's PD2/DR-6 rule, carried verbatim. An expectation transcribed from a dump
would inherit exactly the error it is supposed to falsify.

**Three gated routes, one graph.** Licensed live (`--models`), in-place snapshot, and relocated
snapshot all read the same sealed instance graph; the snapshot is what makes the last two
license-free. The derivative carries its own `instance_graph_snapshot.json` for the same reason
`catf_mfe_d5` does.

**The execution lane.** Generated package → TEAx normalization → policy → durable case storage, with
simkit imported from `/home/reid/1cfe/teax` on `constraint-semantics-item3` @ `5b70ae9`.

---

## Required Invariants

1. **Both frozen twins are byte-untouched** except d5's stale acceptance paragraph in
   `tests/fixtures/catf_mfe_d5/PROVENANCE.md`. `make_d5_variant.py --check` still passes.
2. **Every d5 authored usage is either a carrier in the derivative (by name or by `renamed_from:`)
   or a named deletion record** citing its authorizing table row, and `65 = 58 + 7` closes. Checked
   by D2's script, not by reading.
2b. **Each of the three `blocked-by-defect` carriers has a PROVENANCE record** naming its surfacing
   finding, the epic item that unblocks it, and its held intent. Their catalog rows are
   indistinguishable from any other plain usage, so this record is the only place the disposition is
   visible.
3. **No calc-def-owned guard is asserted.** Asserted-plus-unattachable is a generation-halting
   error, and the halt is whole-model.
4. **Every `@inapplicable:` marker is authored exactly.** A malformed directive halts generation at
   `error` whatever the usage's form — including a plain one.
5. **Every expectation artifact is committed in an earlier commit than the derivative fixture whose
   outputs it pins.** The reader tests already exist at HEAD, so "expectations before the tests"
   would be vacuous — the ordering that carries meaning is expectation-before-*actual*.
6. **The feasibility denominator counts applicable asserted gates only.** Descriptive and
   requirement-side usages appear in the inventory and never in the denominator.
7. **Zero `no live syside license` skip lines** on every claimed licensed run.

---

## Component Overview

- **`tests/fixtures/catf_mfe_gated/`** — the derivative. Diff from d5: two asserted gates rewritten
  bindings-only (and renamed); one new library file; the A7/A8 derivations replacing literals and the
  A1/C37 derivation inside `AlphaNeutronSplit`; the seven authorized deletions removed; five
  `@inapplicable:` markers on the part-def guards; A5/A6/A9 left exactly as d5 wrote them; PROVENANCE.
- **`library/constraints/gate_forms.sysml`** — `CATFGateForms::{PositiveQuantity, FractionWithinBand}`.
  Two definitions, both over bare `Real` formals, predicates over formals only.
- **`PROVENANCE.md`** — five kinds of record:
  1. **Per-change records**, one per edit, each citing its authorizing table row. The two asserted
     gates' records carry `renamed_from:` (D2).
  2. **Seven named deletion records** (A1, A4, A7, A8, C37, C21, C28). The five derive-instead ones
     carry the undirected relation and the ruled "direction is a chosen basis, not physics"
     statement; the two placeholder ones cite O2.
  3. **Three parked-row records** — A5, A6, A9. See below; this is C3's remedy.
  4. **Two O3 model-debt entries** — A7's partial 2-of-4 shield closure; B4's mismatched thickness
     sets.
  5. **Per-gate unit reasoning** for A2 and A3 (D3), so the human-owned invariant has a committed
     home rather than a review conversation.

  **The three parked-row records, specified.** Each of A5, A6 and A9 gets a record naming, in this
  order: the usage's qualified name and d5 file:line; **`blocked-by-defect`**, with the surfacing
  finding (**D-S1** for A9, **D-S2** for A5/A6) and the measured refusal
  (`SI_RENDERING_COLLISION`, with the colliding entry point); **epic Item 8** as the item that fixes
  the unit-lane defect and **epic Item 9** as the item that upgrades this row once it lands; and the
  **held intent** — A5/A6's ruled basis (axis root radius + 14 thicknesses free, all radii derived)
  and A9's ruled target form (`assert-band`, 1% relative). It states explicitly that the usage's
  catalog row reads `excluded` / unassessed form, exactly as it does in `catf_mfe_d5`, and that this
  record is what distinguishes a blocked row from an ordinary plain one.
- **`scripts/check_gated_manifest.py`** — the integrity check (D2). License-free.
- **`tests/expectations/constraint_population/catf_mfe_gated.json`** — the population oracle's
  identity list, derived from the derivative's source.
- **`tests/unit/data/expected-coverage.md`** — one new ledger row for the derivative, in the
  existing parsed-block format, carrying the account above (note `inapplicable_gate_count = 0`).
- **SC-8's three pieces** — a committed v6 snapshot for `constraint_domain_satisfy_calc_def`, a
  committed golden of its two constraint-machinery files, and the conformance test that regenerates
  and diffs them (D7).
- **`verification.md`** — exact counts and fingerprints for all three routes (SC-7).

---

## Non-Goals

- Fixing the unit-lane defect behind D-S1/D-S2. Ruled out of this item and filed as epic Item 8;
  the derivative's upgrade under the already-ruled A5/A6/A9 rows is epic Item 9.
- Editing the shared library calc defs' unit comments to dodge the collision.
- Deriving the axis-region layer on its own. It is the one A5/A6 leg that generates, but a
  half-migrated radial build carries two bases at once, which is worse modeling than the constraint
  it would replace.
- Implementing calc-def gate attachment (Item 6).
- Inventing a tolerance or an intent class. The accounting identity is the owner's restatement
  (`65 = 58 + 7`); no agent re-derives it.
- Graduating the constraint-def library into published authoring guidance (filed for Item 7).
- Changing BLOCK-halts-generation semantics, the report vocabulary, or the coverage contract.

---

## Implementation Notes

- **Author probe-first, in the probe order that worked.** `probes/` at
  `/tmp/item5probe/p7` is the exact composite that generates: library, then A2, then A3, then the
  A7/A8 derivations. **P7 is not the ruled shape** — it deleted nothing, kept all 65 rows, and
  derived the axis leg the ruling drops. Reproduce it, then add the remaining edits group by group,
  re-elaborating after each: A1/C37's calc-def derivation, the A4/C21/C28 deletions, the axis-leg
  reversal, and the five markers.
- **`inapplicable_gate_count` is 0, not 5.** The five `@inapplicable:` markers sit on plain usages,
  and the bucket rule decides "not asserted → inventory only" before it consults the inapplicable
  predicate (`generation/coverage.py:7-27`). Write the expectation with 0.
- **Drive rewrites off the chain name, not the file:line.** Every entry of a multi-chain block
  renders the same location; `block_feature_chain` carries the offending reference (Item 4 limit 2).
- **Never author a bare self-named binding.** None is required — every surviving formal is named off
  its attribute (`value` ← `p_electric_net_out`, `part_power` ← `p_parasitic_total`). If one becomes
  unavoidable, surface and stop; the D-2 vs D-4/SRC-01 conflict is parked at the umbrella level.
- **A `[unit]` literal must not appear in a predicate body.** Neither surviving gate carries one.
- **Test invocation** is `/home/reid/1cfe/item7-rebuild-venv/bin/python -m pytest`, never `uv run`.
  Licensed env: `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a` (the `probes/licensed.sh`
  wrapper does both).
- **Snapshot recapture rewrites every `captured_at`.** Run the byte-identity gate as a
  timestamp-only diff check plus revert, so only the new fixture shows.
- **`ships_constraint_machinery` now keys on one authored usage, not one concrete entry** — the
  derivative ships a report either way.

---

## Potential Risks

| risk | mitigation |
|---|---|
| Epic Item 8's unit-lane fix lands mid-item and moves minted units on existing fixtures | Ruled out of scope here. Item 8 carries its own fingerprint/churn assessment and the one-reviewed-recapture obligation; this item's derivative is additive to whatever it lands. |
| B2 is false — one of the untested edits introduces a new collision | Re-elaborate after each authoring group, not once at the end. The atomic landing means a late discovery costs the whole pass. |
| The `renamed_from:` field is written wrong or omitted, and the identity check passes vacuously | The check fails closed both ways: an unmatched carrier fails, and a `renamed_from:` pointing at a row a deletion record also claims fails. |
| A malformed `@inapplicable:` typo halts generation | Five markers, authored by copy from the Item 2 fixtures that pin the exact form, then re-elaborated. |
| SC-5's mutation crosses no gate because A2's chain is shorter than assumed | B3 is checked before the acceptance run, by evaluating the projected chain on mutated inputs offline. |
| Expected outputs drift from the ruled table | D2's script joins them; a drift fails the check rather than passing quietly. |

## Integration Strategy

The derivative is **additive**: a new fixture directory, one new script, one new expectations file,
one new ledger row, plus SC-8's three pieces on a different fixture. Nothing existing is repointed.
`catf_mfe_d5` keeps its role, its bytes, and its 65/65 carrier proof; the only edit to it is the
stale acceptance paragraph SC-2 requires. `catf_mfe_model` is untouched.

## Validation Approach

Every number below is the **ruled** shape, not the probe shape.

1. **Integrity (SC-2, SC-3):** `check_gated_manifest.py --check` closes `65 = 58 + 7`, matching all
   58 carriers (56 by name, 2 by `renamed_from:`) and all 7 deletion records to authorizing table
   rows; `make_d5_variant.py --check` still passes for all three existing variants; d5's bytes differ
   only in the PROVENANCE paragraph.
2. **Dispositions (SC-4):** the population oracle lists exactly the 58 carriers; the catalog's
   disposition histogram matches the pre-committed expectation — **2 `eligible`** (A2, A3) and 56
   split between `excluded` and `non_reaching`, with the three parked rows reading `excluded` /
   unassessed form exactly as they do in d5.
3. **Coverage (SC-3):** the new ledger row agrees with `coverage_account` field for field —
   `58 / 2 / 2 / 0 / 0 / {} / complete`, headline `full_satisfaction`.
4. **Commit order (SC-6):** `git log --diff-filter=A --format=%H` for each expectation artifact (the
   population JSON, the ledger row's commit, the manifest's expected identity) returns a commit that
   precedes `git log --diff-filter=A` on `tests/fixtures/catf_mfe_gated/`. Expectation before actual;
   the reader tests already existed, so their dates prove nothing and are not cited.
5. **Acceptance (SC-5):** two TEAx runs from one generated package — the authored candidate reaches
   the satisfied path with both gates satisfied, the mutated `p_fusion` drives `p_electric_net_out`
   negative so **A2** reports `violation` and the candidate reaches `reject`, and coverage lands in
   durable case records in both runs. A3 is the second executing gate and is reported either way;
   the ruling does not ask it to carry the rejection.
6. **Gates (SC-7):** licensed live, in-place snapshot, and relocated snapshot, with exact counts and
   fingerprints recorded in `verification.md` and zero license-skip lines.
7. **Residual (SC-8):** regenerating `constraint_domain_satisfy_calc_def` from its committed v6
   snapshot reproduces the committed golden of `schemas/constraint_types.py` and
   `modules/constraints/constraintreportaggregatormodule.py` byte for byte, and the registry carries
   both import lines. Deliberately falsified once during implementation — flip the machinery bar and
   confirm the gate goes red — because a golden nobody has seen fail is not yet a gate.

## Next-Stage Handoff

**Fixed.** D1–D7. The measured landable set (P7). The ruled table as sole authority. The atomic,
probe-first authoring order. Both frozen twins' byte-untouched status.

**Resolved since drafting.** D-S1/D-S2 are ruled (see the SURFACED section header): the landable
shape is the ruled shape, identity `65 = 58 + 7`, A5/A6/A9 `blocked-by-defect` as plain usages with
held intent, the defect filed as epic Item 8 and the derivative's upgrade as Item 9.

**Nothing is open that blocks starting.** The identity is not a side note — it is the first thing
the plan commits, because SC-6 requires the expectation artifacts to land *before* the fixture
generates. Concretely, the plan's first commits pin: **58 carriers** in the population oracle, the
coverage account **`58 / 2 / 2 / 0 / 0 / {} / complete`** with `inapplicable_gate_count = 0`, and the
manifest's expected `65 = 58 + 7` with its 7 named deletions and 2 `renamed_from:` carriers. Those
numbers come from the ruled table, not from a run. The plan must therefore reconcile the P7 probe
composite (65 rows, nothing deleted, axis leg derived) against the ruled 58-carrier target *before*
writing a single expectation file — P7 is evidence that the shape generates, not a description of
the shape.

**De-risk first.** B2, at full scope. Before authoring the real fixture, re-run the composite probe
carrying **every** remaining edit: A1 and C37's calc-def derivation, the A4 deletion, the C21/C28
placeholder deletions, the axis-leg reversal, and the five `@inapplicable:` markers. P7 tested none
of these. The atomic landing makes this the only cheap place to find a second collision.

---
**Next Step:** D-S1/D-S2 ruled (2026-08-13). `/_my_design_review`, then `/_my_plan` with the
ruled-shape reconciliation.
