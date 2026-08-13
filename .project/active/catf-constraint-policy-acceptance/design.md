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
physics rejection through the real TEAx route. Design-stage probes found that two of the ruled
rows cannot be authored at all against the current projection — that finding is the headline, and
it is surfaced rather than worked around.

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
- **Byte baselines:** `tests/fixtures/baseline_outputs/<name>/{computation_graph.json,registry_init.py}`,
  read by `tests/conformance/test_baselines.py`; 13 directories today.

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
derived from the ruled table and committed *before* any confirmation test runs. This is the owner's
sequence, and it is the only thing that stops an expectation from being reverse-engineered out of a
dump.

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

**Parked, not worked around.** A shim attribute introduced solely to dodge the collision would be
exactly the silent workaround the brief forbids. The owner's options are: fix the defect in the
product (constraint/computed port metadata inherits the bound attribute's unit), re-disposition A9,
or accept it as `awaits-capability`. That is an owner decision.

### D-S2 — A5/A6 cannot be derived for 26 of 27 radii

The ruled basis (axis root radius + 14 thicknesses free, all radii derived) requires a computed
design attribute on every layer radius. 26 of the 27 refuse for the same reason: each layer's
`inner_radius` and `outer_radius` are already unit-carrying entry points of that layer's
`minor_calc`. Measured at P4a and P5. Only `axis_region.outer_radius` — the one layer with no
geometry calc on it — derives cleanly (P6).

**Parked.** Same three owner options. Note the shape of the trap: the derivation is *correct
modeling* and the constraint it replaces is *correct policy*; the toolchain refuses the combination.

### What this does to the ruled accounting identity

The identity **65 = 56 carriers + 9 named deletions** was ruled on the assumption that all seven
derive-instead rows and all three asserted gates could be authored. Under the probes, the landable
set is **A2 + A3 asserted; A4, A7, A8 (and A1/C37, unprobed) deleted-with-derivation; A5, A6, A9
not landable as ruled**.

**The design does not restate the identity.** Recomputing it would be an agent silently
re-dispositioning owner-ruled rows. The arithmetic consequence is stated so the owner can rule; the
number in force stays the ruled one until they do.

---

## Key Bets

- **B1.** The two refusals are one defect with one cause — port metadata for non-calc consumers
  carries no unit — and not three coincidences. *If false → fixing the named seam does not unblock
  A5/A6/A9, and the parked threads need separate diagnosis before any of them lands.*
- **B2.** The landable set (P7: 48 modules, 2 executing gates) is stable under the remaining
  authoring work — the `@inapplicable:` markers, the C21/C28 deletions, and the A1/C37 calc-def
  derivation do not introduce a new collision. *If false → the atomic landing fails on the first
  real authoring pass and the whole probe-first premise has to be re-run at fixture scale.*
- **B3.** A2 alone carries SC-5: mutating `p_fusion` propagates through seven calc modules into
  `p_electric_net_out` and crosses zero. *If false → SC-5 has no surviving gate to cross, because
  A3's band is a plausibility envelope the owner explicitly said does not gate viability, and A9 is
  parked.*
- **B4.** The accounting identity is machine-checkable from committed artifacts alone — the ruled
  table's rows join 1:1 against the derivative's catalog plus PROVENANCE deletion records. *If
  false → SC-2's "machine-checkable diff" degrades to a human diff review, which is what
  byte-reversal existed to avoid.*

## Key Decisions

- **D1. Fixture name `catf_mfe_gated`**, forked from `catf_mfe_d5`, sibling directory under
  `tests/fixtures/`. *Rejected: `catf_mfe_d5_gated` (reads as a d5 variant, and `make_d5_variant.py`
  owns that suffix family — a name collision with a mechanical check that does not apply).*
- **D2. Integrity check is an accounting-identity manifest, not a byte reversal.**
  `scripts/check_gated_manifest.py --check` joins three committed sources by usage identity: the
  ruled table's rows, `tests/expectations/constraint_population/catf_mfe_gated.json`, and the
  derivative's `PROVENANCE.md` deletion records. It proves every d5 usage is either a carrier or a
  named deletion citing an authorizing row, and that the counts close. License-free by construction.
  *Rejected: a raw provenance-diff manifest of changed lines (proves what changed, not that what
  changed was authorized — the authorization is the whole point here).*
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
- **D7. SC-8's R3 baseline is `constraint_domain_satisfy_calc_def`** — the measured calc-def-only
  example, whose package correctly ships no `schemas/constraint_types.py`. It enters as a new
  `tests/fixtures/baseline_outputs/constraint_domain_satisfy_calc_def/` directory and a new row in
  `test_baselines.py::MODELS`. No existing baseline directory is touched, so no other fixture churns.
  *Rejected: putting the baseline on `catf_mfe_gated` (it is not a calc-def-only package — it ships
  two executing gates, so it cannot pin the absent-machinery shape).*

---

## Architecture

**Four artifacts, one direction of authority.**

```
owner-disposition.md  (RULED, authority)
        │
        ├──► tests/fixtures/catf_mfe_gated/           the worked example
        │        ├── designs/, library/               forked from catf_mfe_d5
        │        ├── library/constraints/gate_forms.sysml   (D5)
        │        ├── PROVENANCE.md                    per-change + 9 deletion records
        │        └── instance_graph_snapshot.json     sealed v6, for the license-free routes
        │
        ├──► tests/expectations/constraint_population/catf_mfe_gated.json   (population oracle)
        ├──► tests/unit/data/expected-coverage.md     one new ledger row (Item 3's home)
        └──► scripts/check_gated_manifest.py          joins all three, proves the identity (D2)
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
2. **Every d5 authored usage is either a carrier in the derivative or a named deletion record**
   citing its authorizing table row. Checked by D2's script, not by reading.
3. **No calc-def-owned guard is asserted.** Asserted-plus-unattachable is a generation-halting
   error, and the halt is whole-model.
4. **Every `@inapplicable:` marker is authored exactly.** A malformed directive halts generation at
   `error` whatever the usage's form — including a plain one.
5. **Expected outputs are committed in an earlier commit than the confirmation tests that read
   them.** SC-6 is a commit-order argument, and `git log` is the evidence.
6. **The feasibility denominator counts applicable asserted gates only.** Descriptive and
   requirement-side usages appear in the inventory and never in the denominator.
7. **Zero `no live syside license` skip lines** on every claimed licensed run.

---

## Component Overview

- **`tests/fixtures/catf_mfe_gated/`** — the derivative. Diff from d5: two asserted gates rewritten
  bindings-only; one new library file; the landable derivations replacing literals; the authorized
  deletions removed; five `@inapplicable:` markers on the part-def guards; PROVENANCE.
- **`library/constraints/gate_forms.sysml`** — `CATFGateForms::{PositiveQuantity, FractionWithinBand}`.
  Two definitions, both over bare `Real` formals, predicates over formals only.
- **`PROVENANCE.md`** — per-change records; the named deletion records (each carrying the undirected
  relation and the "direction is a chosen basis, not physics" statement for the derivations); the two
  O3 model-debt entries (A7's partial 2-of-4 shield closure; B4's mismatched thickness sets); the
  per-gate unit reasoning (D3).
- **`scripts/check_gated_manifest.py`** — the integrity check (D2). License-free.
- **`tests/expectations/constraint_population/catf_mfe_gated.json`** — the population oracle's
  identity list, derived from the derivative's source.
- **`tests/unit/data/expected-coverage.md`** — one new ledger row for the derivative, in the
  existing parsed-block format.
- **`verification.md`** — exact counts and fingerprints for all three routes (SC-7).

---

## Non-Goals

- Resolving D-S1 or D-S2. Both are surfaced for owner ruling; this design lands what is landable and
  parks what is not.
- Editing the shared library calc defs' unit comments to dodge the collision.
- Implementing calc-def gate attachment (Item 6).
- Inventing a tolerance, an intent class, or a re-derived accounting identity.
- Graduating the constraint-def library into published authoring guidance (filed for Item 7).
- Changing BLOCK-halts-generation semantics, the report vocabulary, or the coverage contract.

---

## Implementation Notes

- **Author probe-first, in the probe order that worked.** `probes/` at
  `/tmp/item5probe/p7` is the exact composite that generates: library, then A2, then A3, then the
  three landable derivations. Reproduce that state in the real fixture before adding the markers and
  deletions, and re-elaborate after each group.
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
| The owner rules "fix the defect" on D-S1/D-S2, and the fix reaches elaboration's metadata seam mid-item | Land the landable set first as its own commit; the fix is a separate item with its own probes. The derivative is additive to it. |
| B2 is false — the markers or deletions introduce a new collision | Re-elaborate after each authoring group, not once at the end. The atomic landing means a late discovery costs the whole pass. |
| A malformed `@inapplicable:` typo halts generation | Five markers, authored by copy from the Item 2 fixtures that pin the exact form, then re-elaborated. |
| SC-5's mutation crosses no gate because A2's chain is shorter than assumed | B3 is checked before the acceptance run, by evaluating the projected chain on mutated inputs offline. |
| Expected outputs drift from the ruled table | D2's script joins them; a drift fails the check rather than passing quietly. |

## Integration Strategy

The derivative is **additive**: a new fixture directory, one new script, one new baseline directory,
one new expectations file, one new ledger row. Nothing existing is repointed. `catf_mfe_d5` keeps
its role, its bytes, and its 65/65 carrier proof; the only edit to it is the stale acceptance
paragraph SC-2 requires. `catf_mfe_model` is untouched.

## Validation Approach

1. **Integrity (SC-2, SC-3):** `check_gated_manifest.py --check` passes; `make_d5_variant.py --check`
   still passes for all three existing variants.
2. **Dispositions (SC-4):** the population oracle's identity list matches; the catalog's disposition
   histogram matches the pre-committed expectation.
3. **Coverage (SC-3):** the new `expected-coverage.md` row agrees with `coverage_account`.
4. **Commit order (SC-6):** `git log --oneline` shows expectations committed before the confirmation
   tests that read them.
5. **Acceptance (SC-5):** two TEAx runs from one generated package — the authored candidate reaches
   the satisfied path, the mutated `p_fusion` reaches `reject`, and both land coverage in durable
   case records.
6. **Gates (SC-7):** licensed live, in-place snapshot, and relocated snapshot, with exact counts and
   fingerprints recorded in `verification.md` and zero license-skip lines.
7. **Residual (SC-8):** the new calc-def-only baseline directory is read by `test_baselines.py` and
   no other baseline's bytes change.

## Next-Stage Handoff

**Fixed.** D1–D7. The measured landable set (P7). The ruled table as sole authority. The atomic,
probe-first authoring order. Both frozen twins' byte-untouched status.

**Resolved since drafting.** D-S1/D-S2 are ruled (see the SURFACED section header): the landable
shape is the ruled shape, identity `65 = 58 + 7`, A5/A6/A9 blocked-by-defect as plain usages with
held intent. The plan must reconcile the P7 probe composite (which deleted nothing and asserted
nothing on A5/A6/A9's rows — 65 usage rows) against the ruled 58-carrier target explicitly, so
expected outputs pin the ruled shape, not the probe shape.

**De-risk first.** B2. Before authoring the real fixture, re-run the composite probe with the five
`@inapplicable:` markers and the C21/C28 deletions added. That is the cheapest place to discover a
second collision, and the atomic landing makes it the only cheap place.

---
**Next Step:** D-S1/D-S2 ruled (2026-08-13). `/_my_design_review`, then `/_my_plan` with the
ruled-shape reconciliation.
