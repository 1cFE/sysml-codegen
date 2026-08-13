# Design Review: CATF Derivative and End-to-End Acceptance

**Design:** `.project/active/catf-constraint-policy-acceptance/design.md` (committed `2821c38`)
**Spec:** `.project/active/catf-constraint-policy-acceptance/spec.md` (SC-3 AMENDED to the accounting identity)
**Ruled authority:** `.project/active/catf-constraint-policy-acceptance/owner-disposition.md` (RULED 2026-08-13)
**Review File:** `.project/active/catf-constraint-policy-acceptance/design-review.md`
**Date:** 2026-08-13
**Epic:** CONSTRAINT-SEMANTICS, Item 5

---

## The Point

A design search must be able to tell a candidate that **passed its physics gates** from one
**nobody checked**.

> **[OWNER]** A design search can trust the generated feasibility evidence to represent every
> applicable asserted physics gate, while every other authored constraint remains visibly
> dispositioned.
> (`.project/backlog/epic_constraint_semantics_contract.md`, Critical Success Factor)

Items 1–4 built the machinery against purpose-built fixtures. The richest model we have,
`catf_mfe_d5`, is still the failure case the epic exists to close: **65 authored constraint usages,
9 reaching, 0 executed**. Until a real physics mutation travels generated package → TEAx
normalization → policy → durable case record and comes back `reject`, the critical success factor
is an assertion.

Two totals must never be conflated: **inventory totality** over all 65 authored usages, and
**feasibility coverage** over applicable asserted gates only.

Note the second half of the owner's sentence, because three of this review's findings turn on it.
"Visibly dispositioned" means visible **in the artifact a design search reads** — the catalog and
the coverage account — not visible in a `.project/` document.

---

## Fundamental Assessment

**Concerns — with one structural smell FIRED and escalated. Verdict: Revise, not Rework.**

The approach is right, and it is right for a reason worth naming: this design was **probe-first**.
Seven licensed probes ran before a single fixture byte was authored, and they came back with a
result the design did not want — two owner-ruled row groups cannot be authored at all. The design
chased that refusal to the producer seam (`elaborate.py:1678-1689` mints unit metadata only for
`CalcNode` consumers; `project.py:394-397` refuses the mismatched `EntryPoint` pair), named the
shim that would have dodged it, and **refused the shim**. It surfaced both refusals as D-S1/D-S2,
parked the dependent conclusions, and explicitly declined to recompute the owner's accounting
identity. That is capture-fidelity §4 executed properly, and it is the hardest thing on this
review's list to do well. The core concept — the ruled table is the compiler input, the fixture is
its output, and the difference is machine-reconcilable — is the right shape for the problem.

Against that, three things are wrong at a level the plan stage would inherit as fact.

**Structural smell (b) FIRED — a solution that changes who owns an invariant without saying so.**
"Every other authored constraint remains visibly dispositioned" is owned by a machine-produced
catalog row over a closed vocabulary. Under the parks, A5, A6 and A9 ship **as authored** — bare
`constraint`, in-predicate `==` — and catalog as `excluded / unassessed form`, byte-identical in
meaning to the row `catf_mfe_d5` shows today. A reader of the shipped artifact cannot distinguish
"the owner ruled this a 1%-band physics gate and a named product defect refuses it" from "nobody
has gotten to this yet." That ownership moved from the catalog to `design.md`, and the design does
not say so: `PROVENANCE.md`'s stated contents (design.md:304-307) list per-change records, the nine
deletion records, two O3 model-debt entries, and the per-gate unit reasoning — **no parked-row
records** — and Non-Goals says only "Resolving D-S1 or D-S2." Contrast D2, which performs the same
kind of ownership move (byte-reversal → bespoke script), says plainly why the old mechanism cannot
transfer, and books it as bet B4. Same shape, said out loud. That contrast is what makes the
silence a finding rather than an oversight.

Smell (a), a consumer compensating for a producer guarantee — the one a reviewer should expect to
fire here — **does not fire**, and the design is explicitly clean on it (design.md:154-155,
Non-Goals:321).

The command's default on a fired smell is Rework-and-stop. **I am not calling Rework, and here is
why.** The smell's remedy is additive and named: one record per parked row in the same PROVENANCE
that already carries the nine deletion records. It does not touch D1–D7, the probe-first authoring
order, the fork, or the atomic landing. The product-lens gated **PROCEED** with all findings
disposed and no BLOCK, and the lens's own test — is the next step's question rigged? — comes back
no: three genuine owner options, the measurement behind each, no recommendation smuggled in.
Recommending Rework on a design this carefully measured would be a misjudgment, and stopping the
review here would withhold six further findings the design agent needs. So: escalated, recorded,
and carried into the issues list as Critical.

The other two: **D7 rests on a premise that is false at HEAD** (C1), and the **Validation Approach
and handoff validate the ruled identity as if it held** (C2) — the one thing the SURFACED section
was careful not to do. The thread through all three is one habit: the design reasons carefully and
then states its conclusions one register too confidently downstream.

---

## Dimensional Review

### 1. Spec Compliance
**Assessment:** Concerns

SC-1 through SC-7 each have a design element and SC-8 has D7. Capture-fidelity carried cleanly on
the way in: the ruled table's rows are treated as authority, no tolerance or intent class is
invented, no owner referent is hardened, and the SC-3 amendment is carried as amended rather than
annotated. The three concerns:

- **SC-8's target shape is stale (C1).** The spec's own wording (`spec.md:71-76`) describes the
  calc-def-only shape as one that "correctly ships no `schemas/constraint_types.py`." That was Item
  2's rule. At HEAD, `tests/conformance/test_constraint_catalog_totality.py:109` asserts
  `(output / "schemas/constraint_types.py").exists()` for exactly that fixture, because
  `ships_constraint_machinery` now keys on one authored usage
  (`src/sysml_codegen/resolution/models.py:625-644`). The design records the corrected rule at
  design.md:347 and then contradicts it at D7 — an internal contradiction, not just an inherited one.
- **SC-6's invariant is vacuous for two of three expectation artifacts (M3).**
- **SC-3/SC-4's content is downstream of the parked ruling (C2)**, which the handoff understates.

The unit-check re-check the spec assigns to this stage is performed below (M5) and **passes**.

### 2. Pattern Consistency
**Assessment:** Pass

Every precedent the design cites, I opened, and each holds: the ledger at
`tests/unit/data/expected-coverage.md` is parsed not transcribed
(`test_coverage_ledger_agreement.py:38-70`); the population oracle asserts by identity list and
fails a constraint-bearing fixture with no expectation file by name
(`test_constraint_population_oracle.py:14-25`); `make_d5_variant.py --check` +
`test_d5_variants.py` is the mechanical-reversal precedent; there are 13 baseline directories. D2's
choice to reuse the parsed-ledger and identity-list patterns rather than invent a new one is right.
The one caveat is what a `MODELS` row actually buys — see C1.

### 3. Abstraction Quality
**Assessment:** Pass

One new script, one new fixture, one new library file, three new data files. No new class, no new
layer, no wrapper. D2 is the only genuinely new mechanism and it earns itself: byte-reversal cannot
transfer to a fixture that deliberately differs, and the design says exactly that. D5's library is
two definitions over bare `Real` formals — as small as it can be. I looked for something to call
over-engineered and did not find it.

### 4. Duplication Avoidance
**Assessment:** Pass

The derivative is additive; nothing existing is repointed. The one place duplication could creep in
— a second mutated fixture for SC-5 — is explicitly rejected in D6 for that reason.

### 5. Data Structure Clarity
**Assessment:** Concerns

D2's three-way join is the item's load-bearing data structure and its **join key is
under-specified**. The join is by "usage identity," but all three surviving gates are **renamed** by
the ruled target forms: `ViabilityCheck` → `net_power_viable`, `ReasonableParasiticTotal` →
`parasitic_fraction_ok`, `PumpingSpeedConsistency` → `pumping_speed_agrees`. Under a naive identity
join those read as three unauthorized deletions plus three unauthorized additions (M1).

The one-direction rule itself is sound and **not circular**: the derivative's population expectation
is scanned from `.sysml` source, and the oracle enforces that independently
(`test_constraint_population_oracle.py`, rule 2), so the manifest's inputs do not descend from the
catalog it cross-checks.

### 6. Route Safety
**Assessment:** Pass

Three gated routes, one sealed graph, no fallback and no wildcard. Invariant 7 (zero license-skip
lines) is the right guard on the licensed claims.

### 7. Bets & Decisions Integrity
**Assessment:** Concerns

B1–B4 are genuine claims about reality, each with a real "if false" — not mechanism choices dressed
as bets. D1–D7 each name their rejected alternative with a reason. That is better than most designs
get. Three problems:

- **B2's named de-risk step does not cover B2 (M2).** B2's own scope is the markers, the C21/C28
  deletions, **and the A1/C37 calc-def derivation**; the handoff's de-risk step names only the first
  two. A4's deletion is in neither. The A1/C37 edit changes what a calc def outputs — the same lane
  the collision lives in — so it is the item on that list most likely to falsify B2.
- **B1 is not falsifiable inside this item.** Its falsifier ("fixing the named seam does not unblock
  A5/A6/A9") is only testable after a fix that is explicitly out of scope. Fine as a recorded belief;
  nothing in-item should be load-bearing on it, and today nothing is. Noted so it stays that way.
- **Hidden bet, unstated (M4).** All seven probes stop at elaboration/projection. D6 and B3 rest on
  `p_fusion` being a mutable key in the generated `inputs/*.json` and on TEAx consuming a mutated
  inputs JSON without a study-config override. Neither is measured. For a design whose whole premise
  is "measure before authoring," the execution lane — the item's headline claim — is the one lane
  with no measurement.

### 8. Reader Comprehension
**Assessment:** Pass

A tired engineer can skim this once and come away with the model: fork d5, author the ruled table
into it, prove a rejection, and two ruled rows turned out unauthorable. The SURFACED section leads
with the conclusion, gives the mechanism only as far as needed, and states the blast radius as a
measured number (26 of 27) rather than an estimate. "The table is the compiler input; the fixture is
its output" is a real mental model, not a coined label. No finding here.

---

## Issues by Severity

### Critical

- **C1 — D7's stated reason is false at HEAD, and a `MODELS` row does not put anything in a
  byte-identity gate.** Two separate defects in one decision.
  *(a)* D7 picks `constraint_domain_satisfy_calc_def` because its package "correctly ships no
  `schemas/constraint_types.py`" and rejects `catf_mfe_gated` as unable to "pin the absent-machinery
  shape." At HEAD that package **does** ship it —
  `test_constraint_catalog_totality.py:109` asserts `.exists()`, and its docstring
  (`:78-92`) exists specifically to warn that Item 3 moved this bar. The design states the corrected
  rule itself at design.md:347.
  *(b)* `tests/conformance/test_baselines.py` never regenerates and never diffs. It asserts
  round-trip, key presence, `execution_order` length, and that `registry_init.py` parses — over
  committed bytes only. The `model_dir` half of every `MODELS` tuple is unused in all four test
  bodies, and `test_execution_order_matches_modules_all_baseline_dirs` already globs every
  directory. So a new directory plus a `MODELS` row buys three structural assertions and no byte
  comparison, which is not what R3 asked for ("no byte gate covers the shape").
  *Suggested resolution:* keep the fixture, restate what it pins — the **"declares constraints,
  assesses none"** shape, which is the more valuable one — and say concretely what mechanism makes
  SC-8 a byte gate rather than a third structural assertion. The committed `registry_init.py` does
  carry the machinery signal (`ConstraintEvaluation` / `ConstraintReport` imports), so the shape is
  representable; what is missing is a test that regenerates and compares. — Dimensions 1, 2, 7
  *(independently found by the product-lens as item5d-F2)*

- **C2 — The Validation Approach and the handoff validate an identity the SURFACED section has
  already shown cannot close.** D2's script proves `65 = carriers + named deletions` against the
  ruled table. Under the parks, A5/A6 are not deleted and A9 is not asserted, so the join cannot
  close by construction. Validation items 1 and 3 list the check as passing unconditionally
  (design.md:370-374), Potential Risks has no row for it, and the handoff calls the parked group
  "**blocking their own rows only** … not a blocker on the item" (design.md:390-392). But the parked
  ruling determines the *content* of the derivative's population expectation, the new
  `expected-coverage.md` row, D2's expected identity, and `verification.md`'s counts — that is
  SC-2, SC-3, SC-4 and SC-6, which are **item** criteria. And because SC-6 requires expectations be
  committed **before** outputs, the ruling gates the item's first real commit, not a trailing one.
  The design was right not to restate the identity; the error is downstream, where the unrestated
  identity is validated as if it held.
  *Suggested resolution:* state the landable identity as an explicit conditional (ruled number in
  force; landable-set number stated as consequence, not as a re-disposition), add the risk row, and
  correct the handoff to say which expectation artifacts are ruling-gated. — Dimensions 1, 7
  *(independently found by the product-lens as item5d-F3)*

- **C3 — SMELL (b) FIRED, ESCALATED: the parked rows are dispositioned in `design.md` and
  undispositioned in the artifact a design search reads.** Under the parks, A5, A6 and A9 ship as
  authored and catalog as `excluded / unassessed form` — the identical row d5 shows today. The
  owner's CSF says every other authored constraint stays **visibly** dispositioned; for these three
  the visibility exists only in `.project/`. PROVENANCE's stated contents carry no parked-row record.
  *Suggested resolution:* whatever the owner rules on D-S1/D-S2, the derivative carries a named
  record per parked row in the same PROVENANCE that carries the nine deletion records — qualified
  name, ruled disposition, refusing reason code plus the measured probe, and the authorizing table
  row. This is additive and does not touch D1–D7. — Stage 0 / Dimension 1
  *(product-lens item5d-F1; smell (b) fired on it)*

### Major

- **M1 — D2's identity join breaks on the three renamed carriers.** All three survivors are renamed
  by their ruled target forms (`ViabilityCheck` → `net_power_viable`, `ReasonableParasiticTotal` →
  `parasitic_fraction_ok`, `PumpingSpeedConsistency` → `pumping_speed_agrees`). The ruled table keys
  by the d5 name; the derivative's population expectation, scanned from source, will carry the new
  name. Under an identity join, three carriers read as unauthorized deletions plus unauthorized
  additions — and B4 ("the rows join 1:1") is false as written.
  *Suggested resolution:* name a fourth join input — a rename record in PROVENANCE, or parse the
  ruled table's target-form cell — and say which. — Dimension 5

- **M2 — B2's de-risk step under-covers B2.** B2 names the `@inapplicable:` markers, the C21/C28
  deletions, **and the A1/C37 calc-def derivation**; the handoff's de-risk step names only the first
  two, and A4's deletion appears in neither. Sequencing is otherwise correct — de-risk before
  authoring, which is the right place — so this is a scope gap, not an ordering error.
  *Suggested resolution:* add A1/C37 and A4 to the composite de-risk probe. Given the collision lives
  in unit metadata on non-`CalcNode` consumers, a calc-def output change is the highest-prior edit on
  that list. — Dimension 7

- **M3 — SC-6's invariant 5 is vacuous for two of the three expectation artifacts.** Invariant 5
  says expected outputs are committed in an earlier commit than "the confirmation tests that read
  them." But `test_coverage_ledger_agreement.py` is parametrized off the ledger file
  (`:84-86`) and `test_constraint_population_oracle.py` globs fixture directories — both exist at
  HEAD, so a new row and a new expectation file add cases with **no new test code**. The reader
  necessarily predates the expectation, and `git log` shows the reverse of what SC-6 wants to prove.
  Same for `test_baselines.py`.
  *Suggested resolution:* restate the order that carries meaning — the expectation commit precedes
  the commit that first **generates or captures** the derivative's outputs (the snapshot capture and
  `verification.md`). That is Item 3's precedent in substance, and it is checkable in `git log`. —
  Dimension 1

- **M4 — Nothing has been measured past projection, and SC-5's lane is where the item's claim
  lives.** All seven probes stop at `build_elaborated_pipeline`. D6's mutation design and B3 both
  assume `p_fusion` surfaces as a mutable key in the generated `inputs/*.json` and that TEAx consumes
  a mutated inputs JSON without a study-config override. Neither is probed, and the design's own
  premise is that authoring against an unmeasured assumption is what probe-first exists to prevent.
  D6's shape is otherwise the faithful reading of SC-5 — one generated package, two input sets, both
  reaching durable case records, the mutation on a physics input rather than a constraint edit, and
  both rejected alternatives correctly rejected.
  *Suggested resolution:* one generation probe on the P7 composite before authoring: generate the
  package, confirm `p_fusion` is an inputs-JSON key, and confirm A2's evaluation appears in the
  report. Cheap, and it converts D6 from a plan into a measurement. — Dimension 7

- **M5 — D3's argument is narrower than the claim it supports, and the vacuity is contingent on
  A9's park.** "Neither gate has a tolerance whose dimension could be wrong" is true and is not the
  same as "dimensionless-safe." The uncheckable surface the spec's item5-F3 names is the **operand
  pair**: binding a non-power into `whole_power` would also be admitted silently.
  **Review checkpoint performed** (the spec's `[INFERRED]` two-checkpoint rule designates this stage
  as the second): A2 binds `p_electric_net_out` (MW) against the authored literal `0` — a
  `real`/`real` comparison, nothing to mis-unit. A3 binds `net_electric.p_parasitic_total` and
  `gross_electric.p_electric_gross`, both MW per the ruled table's unit-check cells, with `0.10` /
  `0.90` as dimensionless fractions. **Both gates check out against the authored source.**
  *Suggested resolution:* have the per-gate PROVENANCE record state the operand-pair obligation, not
  only the tolerance dimension, and note that D3's vacuity is contingent — A9 is the one ruled band
  with a real dimension (`m^3/s`), so a "fix the defect" ruling reopens D3. — Dimension 1

- **M6 — The predicted coverage-account numbers are unstated, and the one most likely to be wrong is
  `inapplicable_gate_count`.** The bucket table (`src/sysml_codegen/generation/coverage.py:7-27`) puts
  a **non-asserted** usage in row 1, "inventory only," *regardless of its inapplicability marker*;
  row 2 requires `asserted = yes`. B1–B5 stay plain `constraint`, so the five `@inapplicable:` markers
  produce `inapplicable_gate_count = 0`, not 5 — those guards are already out of the denominator by
  form. The markers still earn their place (they make the catalog disposition explicit, which SC-1
  and SC-4 want, and they move the graph fingerprint), but they buy nothing for the coverage account.
  Under SC-6 a wrong pre-committed number cannot be quietly edited, so getting this right before the
  expectation commit matters more here than it normally would.
  *Suggested resolution:* state the predicted `expected-coverage.md` row explicitly in the design,
  derived cell by cell from the bucket table. — Dimensions 1, 5

### Minor

- **m1 — `elaborate.py:488` is the wrong citation** for the whole-model BLOCK halt (design.md:135,
  inherited from `spec.md:206-207` where it is marked "verified"). That line raises
  `SI_EDGE_DANGLING` for an unrecognized constraint-definition UUID; the halt is around
  `elaborate.py:1145-1152`. Premise correct, pointer wrong. Repoint here and in the spec.
  *(product-lens item5d-F4)*
- **m2 — The Implementation Note "A `[unit]` literal must not appear in a predicate body"
  (design.md:340) is stated as a flat rule** and contradicts `modeling-assumptions.md` §8, carried
  as `[HARD]` at `spec.md:209-213`: annotating **both** operands is the supported unit-carrying
  spelling; only the one-operand form is refused. Harmless in practice (neither survivor carries
  one), but a plan would inherit it as a rule. Scope it to this item, or — if the probes measured a
  contradiction with §8 — that is a §4 surfacing obligation, not an implementation note.
  *(product-lens item5d-F5)*
- **m3 — D5's contents depend on a parked row.** Dropping `ProductWithinBand` follows from A9's
  park and is stated openly, so this is not a silent re-disposition. Flagging only that a "fix the
  defect" ruling reopens D5 as well as D3 and the identity.
- **m4 — B1 is unfalsifiable within this item** (its falsifier is only testable after an
  out-of-scope fix). Fine as a recorded belief; noted so nothing in-item becomes load-bearing on it.

---

## Recommendations

1. **Correct C1's premise before anything else.** It is a one-paragraph fix to D7 and a restatement
   of what SC-8 pins, but left alone the plan inherits a false fact about the product and builds a
   baseline that discharges R3 in name only.
2. **Add the parked-row PROVENANCE records (C3).** Additive, touches no decision, and it is what
   closes the fired smell. The owner's ruling determines the record's content, not whether one is
   needed — so this can be specified now.
3. **Make the parked-row dependency explicit in the validation plan and the handoff (C2).** State
   the landable identity as a conditional, add the risk row, and say plainly which expectation
   artifacts cannot be authored before the ruling. The plan's sequencing depends on this being right.
4. **Extend the de-risk probe to cover all of B2 (M2), and add a generation probe for the execution
   lane (M4).** Both are cheap, both are in the spirit the design already established, and M4 covers
   the one lane with no measurement behind it.
5. **Name D2's rename join input (M1) and state the predicted coverage row (M6).** Two small
   specifications that stop a pre-committed expectation from being wrong in a way SC-6 will not let
   you quietly fix.
6. Fold in the minors (m1, m2) as one-line corrections.

**Not findings — checked and clean, recorded so they are not re-litigated:** the SURFACED handling
meets every axis capture-fidelity §4 asks for (named against owner-graded content, both conclusions
parked, the arithmetic consequence stated *without* restating the identity, three owner options with
no recommendation smuggled in, blast radius measured rather than estimated); D2's one-direction rule
is genuinely non-circular, because the population expectation is scanned from `.sysml` source and
the oracle enforces that independently; the derivative's five `@inapplicable:` markers do **not**
risk the `marked_but_unattachable` halt, which fires on *asserted* unattachable gates
(`tests/fixtures/constraint_domain_inapplicable_unattachable/model.sysml`) and not on the plain
part-def form these five take; provenance grades survive the spec → design hop; rejected alternatives
read as decision records rather than prohibitions.

---

## Resolutions

*(Stage 4 — filled in as the owner resolves each issue. One entry per resolution; this section is
what the design agent reads to incorporate the review.)*

---

**Overall:** **Revise**

Six of the ten findings are one-sentence or one-paragraph corrections; three (C1, C2, C3) are
substantive but additive. No decision D1–D7 is overturned, and the probe-first method, the fork, the
ruled-table-as-authority stance, and the atomic landing all stand. The structural smell fired and is
escalated into the judgment above rather than left in the rubric; the reason it does not force
Rework is stated there.

**Next Steps:** Record resolutions in the section above, then re-run `/_my_design` (or return to the
design-agent session) and point it at this review to incorporate. The reviewer does not edit the
design. C1, C2 and C3 should land **before** `/_my_plan`, independently of the owner's D-S1/D-S2
ruling — the ruling determines the parked rows' content, not whether these three corrections are
needed.
