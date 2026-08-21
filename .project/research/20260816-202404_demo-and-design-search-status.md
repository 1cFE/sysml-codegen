---
date: 2026-08-16T20:24:04-07:00
researcher: Claude
topic: "Honest status: compiled+teax-generated CATF/stellarator package, and the design-search demo"
tags: [research, status, catf, stellarator, fusion-tea, design-search, demo]
status: complete
last_updated: 2026-08-16
---

# Research: How close are we to (a) a correctly compiled, teax-generated CATF/stellarator package and (b) a basic design-search demo?

**Date**: 2026-08-16T20:24-07:00
**Researcher**: Claude (four parallel research agents; two demos re-executed live today)
**Research Type**: Status audit / archaeology

## Research Question

Honest assessment, criteria broken down, validation level stated per criterion:
a) How close to a correctly compiled and teax-generated package for the CATF and/or stellarator models?
b) How close to a basic demo of the design search?

## Validation vocabulary used below

- **PINNED-AT-HEAD** — an automated test at current HEAD enforces it (noting which lane it runs in).
- **RUNS-TODAY** — re-executed live during this research (2026-08-16) and passed.
- **ONE-SHOT-RECORDED** — ran once, evidence recorded in docs; nothing fails if it regresses.
- **DOC-ONLY** — a document claims it; no runnable artifact backs it.
- **MISSING** — does not exist.

## Summary

**CORRECTED 2026-08-16 (owner pushback, verified):** the first version of this summary called the
stellarator runner "a working demo." The owner's recollection — "we had like 5 inputs that were the
same variable" — is **confirmed by direct inspection** of its generated inputs
(`stellarator_e2e/generated/inputs/`): `operational_years` is 4 separate input keys, `availability`
4, `interest_rate`/`discount_rate` 5, `project_time`/`construction_years` 5, major radius `R` 3,
and `pi` is an input twice. That package reproduces its pinned numbers but its values are **not
tied together** — mutating one copy leaves the others stale. It demonstrates number-reproduction,
not a usable design surface. The claims below are re-graded accordingly.

- **Two runnable artifacts exist, of very different quality:**
  1. **Stellarator single-pass runner** (`run_stellaris_single.py`) — re-executed today, reproduces
     LCOE $275.26/MWh bit-exact vs oracle — **but on the July V11-era package with the fan-out
     defect above**. Historical evidence, not a demo of tied values.
  2. **The Slice-3D execution lane** — `sysml-codegen tests/execution -m execution`: **88 passed
     today** at HEAD `58bc6aa`. This is the one with the fan-out defect actually fixed and proven:
     one `gain` entry feeding exactly its three consumers (two calcs + viability constraint),
     structural and runtime every-and-only mutation proofs
     (`test_fusion_tea_mutation_teax.py:302-345` — the comment names it: "The entry the original
     fan-out forensics was about").
- **HEAD-generated fusion_tea package, scanned the same way (license-free snapshot generation,
  27 input keys):** codegen-level fan-out is gone (`gain`, `availability`, `thermal_efficiency` each
  one key). The residual duplicates are **model-authored**, not wiring failures: the
  `hif_driver_instance` workaround block duplicates 3 driver keys (removal = the elaborator-downstream
  regeneration), and plant `frequency` vs `driver.pulse_rate_ref` are two separately authored
  attributes for one physical quantity (`hif_plant.sysml:33,78`) — a modeling fix, not a codegen fix.
- **(a) is split by model.** The *pipeline* is proven at HEAD. The *models* are each one specific, known distance away: fusion-tea customer repo needs its 15-site migration certified + one regeneration (the two items already in flight); CATF compiles and executes at HEAD but its gated variant's execution evidence is one-shot and stale, it has **no LCOE at all**, and its authored design point is physically infeasible by 5.43× (the P1 cryo bug); the stellarator is refused by the exact route (114 self-bindings) and is parked P2/unowned behind a July hold.
- **(b) is one integration pass away, not an architecture away.** The study layer (grid strategy, policy, crash-safe SQLite store, CLI) is built and pinned; a real 2,301-point IFE viability study ran through the *stock* study layer on 2026-07-20 (2,294/2,301 verdict agreement). The gaps: that study recorded verdicts but not LCOE (data was available, hours to add); the package it ran against is stale (regeneration = the live elaborator-downstream item); nothing is wrapped as a one-command demo.
- **The never-ending-slop feeling has a mechanical explanation**: almost all recent effort went into converting ONE-SHOT-RECORDED claims into PINNED-AT-HEAD proofs and refusing silent wrongness (the exact route now *refuses* models the old route silently glued together). The end-to-end capability didn't regress — the July demos still run — but the certification loop (audit → needs-work → remediate → re-audit) is what the last weeks were spent on.

---

## Part (a) — compiled + teax-generated package, per model

### The pipeline itself (model-independent)

| Criterion | Status | Evidence |
|---|---|---|
| Exact route generates, seals, TEAx-loads, executes a whole plant | **PINNED-AT-HEAD + RUNS-TODAY** | `tests/execution/test_fusion_tea_real_teax.py` (11 channels, LCOE at `fusion_tea_arithmetic.py:148`); 88/88 today |
| Live and snapshot routes byte-identical | **PINNED-AT-HEAD** | step-5 portable provenance, `CURRENT_WORK.md` 2026-08-14 entries |
| Mutation propagation every-and-only, verdict flip | **PINNED-AT-HEAD** | `tests/execution/test_fusion_tea_mutation_teax.py:217-365` |
| Constraint six-state vocabulary, coverage-true headline, fail-closed load | **PINNED-AT-HEAD** | `teax-simkit simkit/evaluation/evidence.py:66-74`, `package_load.py:40` |

Caveat on every row: the execution lane is deselected from the default suite (`pyproject.toml:46`) and needs the agentic-mbse venv + PYTHONPATH incantation (`CURRENT_WORK.md:502-506`). License-gated tests skip silently without `SYSIDE_LICENSE_KEY`.

### fusion-tea IFE/HIF (the closest model — the user didn't name it, but it's the demo model)

| Criterion | Status | Evidence |
|---|---|---|
| Codegen fixture end-to-end | **PINNED-AT-HEAD + RUNS-TODAY** | above |
| Customer repo models accepted by exact route | **NOT YET** — 15 self-binding sites refused | `CURRENT_WORK.md:449-454` |
| Migration of those 15 sites | done on branch, dual trees byte-identical, spine 9 passed — but **re-audit NEEDS WORK, SC1 open** (non-injective cross-tree mapping can false-green; positional fixture mode has an unguarded `rmtree`) | `active/self-binding-replacement/audit.md`; `CURRENT_WORK.md:83-106` |
| Regeneration of customer package on post-R-2 (workaround-free, 9-channel) shape | **NOT DONE** — this is exactly `elaborator-downstream` (Item 8 remainder), spec revised, ready for design, gated on the sibling re-audit certifying | `active/elaborator-downstream/spec.md` |

**Distance: two bounded items, both already specified.** Close SC1's two technical blockers → certify → run elaborator-downstream (regenerate, execute on stock TEAx, new lineage).

### CATF (MFE tokamak; three fixtures in `tests/fixtures/`, no upstream home)

| Criterion | Status | Evidence |
|---|---|---|
| Elaborates with zero readiness diagnostics | **PINNED-AT-HEAD** (license-gated) for `catf_mfe_d5` and `catf_mfe_gated`; original `catf_mfe_model` still refused (1× SI_SELF_BINDING) | `test_coverage_ledger_agreement.py:88`, `test_constraint_population_oracle.py:126` |
| Generates + seals | `catf_mfe_d5`: **PINNED-AT-HEAD** (execution lane). `catf_mfe_gated`: **ONE-SHOT-RECORDED** (2026-08-13); no test at HEAD generates it | `test_constraint_coverage_matrix.py:170-181`; `20260813_catf-constraint-policy-acceptance/verification.md:380-405` |
| Executes under real `execute_pipeline` | `catf_mfe_d5`: **PINNED-AT-HEAD** — full 43-module pipeline runs; but it has **zero asserted gates** and the test asserts only the constraint report, never a physics number. `catf_mfe_gated` (3 gates): **NEVER** run through `execute_pipeline`; its one run used `PreparedEvaluator`, on the superseded 2-gate shape | `test_constraint_coverage_matrix.py:184`; `20260813_derivative-upgrade-held-intent/audit.md:300-305` |
| Gate verdicts + study policy | **ONE-SHOT-RECORDED**, weaker than the doc claims (probe asserts truthiness, not tokens; `/tmp` JSON, not a case store; A-7: only the reject leg is genuine policy output) | `verification.md:582-616`; backlog `[CATF-ACCEPTANCE-LANE-MANUAL]` P3 |
| Any numeric output asserted by any test | **MISSING** | agent sweep of `tests/**` |
| LCOE | **MISSING from the model** — `attribute lcoe : Real` declared, "TO BE CALCULATED in Costing epic"; no CAS cost layer modeled | `catf_mfe_gated/designs/catf_mfe/system.sysml:91` |
| Physically sane authored design point | **NO** — `[CATF-CRYO-HEAT-LEAK-COEFFICIENT]` P1: cryo cooling 8396 MW vs 1547 MW gross (5.43×); net electric negative; unit error in `thermal_loads.sysml:59`. Owner-signed modeling fix required | `BACKLOG.md:171-200` |
| Most constraints executable | **NO** — 48 of 65 are calc-def-owned, `non_reaching`; needs `[CALCDEF-GATE-IMPLEMENTATION]` (P1, 7–9 days, **not authorized**) | `BACKLOG.md`; `20260813_calcdef-constraint-gate-design/implementation-item.md` |

Two staleness discoveries: the recorded blocker for pinning the CATF acceptance lane ("teax branch unmerged") is dead — teax main is `744745f`, the branch merged; and the archived probe hardcodes a deleted worktree path, so re-running it is a reconstruction, not a command.

**Distance: "compiled and teax-generated" is genuinely done for `catf_mfe_d5` at HEAD.** A CATF package you'd *believe* needs: re-execution + pinning of the 3-gate shape (small — the stated blocker is gone), the cryo fix (P1, small, owner sign-off), and — for anything LCOE-like — a costing layer that was never modeled (real modeling work, unsized).

### Stellarator (concept-09 "Stellaris", `fusion-tea-stellarator-mbse-demo`)

| Criterion | Status | Evidence |
|---|---|---|
| End-to-end demo with LCOE + 5 verdicts + oracle parity | **RUNS-TODAY** — but on the *old* route's staged artifacts (V11-era, canonical models untouched), with 3 harness-injected values codegen couldn't wire (`special_materials_capital`, `cas28_capital`, `n_mod`) | `run_stellaris_single.py` (ran 2026-08-16: LCOE $275.264220, all verdicts satisfied, PARITY PASS); `CODEGEN_FINDINGS.md` |
| Canonical models accepted by exact route | **NO** — exit 1, **114× SI_SELF_BINDING**, only class seen (route stops at first class; more may lurk — WI-027 history hit Gate A/B blockers beyond self-binding) | `active/self-binding-replacement/stellarator-triage.md:13-20,45-47` |
| Migration work sized | 99 sites in 2 files (`generic_mfe/mfe_plant.sysml` ×94, `stellarator_plant.sysml` ×5); proven D-5 recipe + customer-mode tool exist | `BACKLOG.md:332-341` |
| Scheduled | **NO** — `[STELLARATOR-D5-MIGRATION]` P2, unowned, July owner hold stands | same |

**Distance: one mechanized migration (tool already proven on fusion-tea) + an unknown tail of post-self-binding diagnostics + the three cross-part wiring gaps.** Nothing moves until the July hold is lifted and it gets an owner.

---

## Part (b) — basic design-search demo

Target (P-001): vary parameters freely, get viability + outcomes (LCOE) per point. Minimal credible demo: 1–2 parameters × N points → LCOE + feasibility verdict per point, table/plot, one command.

| Building block | Status | Evidence |
|---|---|---|
| Study layer (GridStrategy, StudyRunner, policy, crash-safe SQLite store, `teax-study` CLI) | **PINNED-AT-HEAD** (create→run→crash→resume byte-identical; toy package) | `teax-simkit simkit/study/`; `simkit/tests/study/test_cli_end_to_end.py:35-70` |
| Real grid study on a real fusion model through the *stock* study layer | **ONE-SHOT-RECORDED** — 2,301-point (η × gain) IFE viability study, 2,294/2,301 match vs the hand-written classification (7 boundary rows, `>` vs `>=`); ~168× prepare-once speedup | `fusion-tea/exploration/ife_e2e/study/run_viability_study.py`, `findings.md:38-45,88-93`, `acceptance_table.csv` |
| LCOE per swept point | **exists only in the harness that bypasses TEAx** — `sweep_ife.py`, 11,505 points, LCOE+viability per row, committed plots — calls generated impls directly, skips executor/seal/store | `sweep_ife.py:44-56,96-101`; `plot_sweep.py`; `data/ife_sweep/` |
| LCOE and verdict in the SAME harness | **MISSING — smallest real gap.** The study run set `ObjectivePolicy(objectives=())` and wrote no LCOE column; `CaseView.outputs` already carries it. Hours of work | `run_viability_study.py:69,134-142`; `simkit/study/query.py:46-51` |
| Fresh package to run it against | **STALE** — `ife_e2e/generated/` is 2026-07-20, pre-CONSTRAINT-SEMANTICS, pre-R-2. Regeneration = `elaborator-downstream`, gated on self-binding SC1 | `active/elaborator-downstream/spec.md:28-31,61-70` |
| Multiple physics gates bounding the region | **THIN** — IFE package has exactly one eligible gate (the viability knee). CATF has 3 executing gates but no LCOE and the cryo defect | `run_viability_study.py:79-81` |
| One-command demo wrapper / plot off the study store | **MISSING** — reproduction is a multi-venv, multi-repo incantation | `findings.md:118-129` |
| UI (Concept Explorer, tornado charts, sliders) | exists and serves, but over hand-written 1costingFE models — **not wired to generated packages** | `fusion-tea/exploration/concept_explorer/` |

**Distance: after elaborator-downstream lands, the remaining demo work is roughly: (1) add LCOE to the study's objective/outputs and emit it (hours); (2) repoint the plot at the study output (mechanical); (3) wrap as one script (small).** The epic close already anticipated this as the "composed design-search demo item" next-slot competitor (`CURRENT_WORK.md:1660-1662`). A *CATF* design search additionally needs the cryo fix (else it rejects everything near the authored regime) and the calc-def gate item for real multi-gate feasibility.

## Architecture Insights

- The three-layer split (model owns meaning / generated package owns evaluation / study layer owns exploration) is fully built and demonstrated; P-001's second bullet (no predetermined free variables) remains directional — the causal-toolchain reconciliation and `[ACAUSAL-RELATIONS-CAPABILITY]` P3 record the gap honestly.
- The dominant recent cost was converting one-shot claims into pinned proofs and making the route refuse what it used to silently glue (self-bindings, seals, coverage). That is why things "keep breaking": the old demos ran on rescues the new route correctly rejects.
- Chronic evidence hazards to keep in view: license-skip makes green runs lie; the execution lane is off by default; the 17 ordering-dependent full-suite failures at clean HEAD are still unowned (`CURRENT_WORK.md:345-351`).

## Recommendations (order matters)

1. **Close self-binding SC1's two blockers** (injective cross-tree mapping; guard positional-mode `rmtree`) → certify. Everything else queues behind this.
2. **Run elaborator-downstream** — fresh customer package on the 9-channel shape, stock-TEAx execution, lineage.
3. **The composed demo item (small):** LCOE column + plot + one-command wrapper on the 2,301-point study. This is the "basic demo of the design search" — it is days, not refactors, once 1–2 land.
4. In parallel/after, owner decisions: cryo coefficient fix (P1, small, unblocks CATF search), calc-def gate implementation authorization (P1, 7–9 days), stellarator hold + ownership (P2, ~99 sites + unknown tail).
5. Cheap wins surfaced: the CATF acceptance lane can now be pinned (its "unmerged teax branch" blocker is dead); nothing enforces the CATF numbers today.

## Open Questions

- Whether the stellarator July hold lifts, and who owns the migration.
- Whether CATF gets a costing layer (LCOE) or remains a physics-gate testbed — changes what "CATF design search" can mean.
- The 17 unowned ordering-dependent full-suite failures.
- Whether Concept Explorer becomes the demo UI over generated packages, or the demo stays CLI/plot.

## Code References (primary)

- `sysml-codegen/tests/execution/test_fusion_tea_real_teax.py:56-67,182,198` — Slice 3D, 11 channels, LCOE pin
- `sysml-codegen/tests/execution/test_fusion_tea_mutation_teax.py:217-365` — every-and-only mutation + verdict flip
- `sysml-codegen/tests/execution/test_constraint_coverage_matrix.py:170-184` — CATF d5 generate→seal→load→execute at HEAD
- `fusion-tea-stellarator-mbse-demo/exploration/stellarator_e2e/run_stellaris_single.py` — the working stellarator demo (ran today)
- `fusion-tea/exploration/ife_e2e/study/run_viability_study.py:69,79-81,134-142` — the 2,301-point stock-study run and its LCOE omission
- `teax/packages/teax-simkit/simkit/study/` — the study layer; `simkit/tests/study/test_cli_end_to_end.py:35-70`
- `.project/backlog/BACKLOG.md:171-200` (cryo P1), `:332-341` (stellarator P2), `:1333-1343` (CATF lane manual)
