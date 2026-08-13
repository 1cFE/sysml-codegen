# Verification — CONSTRAINT-SEMANTICS Item 5

**Item:** CATF Derivative and End-to-End Acceptance
**Plan:** `plan.md` (committed `18f51e1`)
**Started:** 2026-08-13

Numbers here are recorded exactly, never summarized (SC-7). Every licensed run records its
`no live syside license` skip-line count, because zero is the only proof it really ran licensed.

---

## Phase 0 — Baseline and environment proof

### Test invocation

`/home/reid/1cfe/item7-rebuild-venv/bin/python -m pytest tests/`, licensed via
`set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a`.

`pyproject.toml:46` sets `addopts = -v --tb=short -m "not execution"`, so the default
invocation deselects the `execution`-marked tests. Both marker sets are recorded below,
because the plan's inherited floor did not say which one it counted.

| run | invocation | passed | skipped | deselected | failed | `no live syside license` lines |
|---|---|---|---|---|---|---|
| default marker set | `pytest tests/` | **2012** | **34** | 79 | 0 | **0** |
| all markers | `pytest tests/ -m ""` | **2090** | **34** | 0 | **1** | **0** |

**The one failure is pre-existing and already recorded — not re-diagnosed here.**
`test_the_lane_runs_the_real_simkit`, quoting `.project/CURRENT_WORK.md:468-472` verbatim:

> **`tests/runtime/…::test_the_lane_runs_the_real_simkit` fails on a whole-set run and passes in
> isolation** — a collection-order artifact, reproduced at the parent commit and therefore
> pre-existing. Surfaced (and re-confirmed) by CONSTRAINT-SEMANTICS Item 3, which touched neither
> `tests/runtime/` nor the guard; `tests/execution` alone is green. Recorded here so it is not
> rediscovered as a regression. **Still needs an owner** — no item has claimed it.

It is **out of this item's floor** by orchestrator ruling (2026-08-13). The observed failure
message on this run was `AssertionError: the in-repo stub runner was imported on the real-TEAx
lane; its fake simkit would shadow the installed one` — consistent with the recorded
collection-order account. No Item 5 edit is involved (the only tree change at the time of the
run was d5's PROVENANCE prose).

### Deviation from the inherited floor — recorded, not absorbed

The plan carries **2050 passed / 34 skipped** as the Item 3 close baseline. Neither measured
number equals it: 2012 (default markers) and 2090 (all markers). Skipped is **34 in both**,
matching exactly.

Account: 2050 sits between the two, so the gap is the marker set plus test churn. Item 4
(`constraint-predicate-hardening`) landed after the 2050 measurement and added tests, which
is consistent with all-markers now reading 2090 ≈ 2050 + 40. **No test was lost** — the
skipped count is identical and no test that passed at Item 3 close is failing here.

**The floor for the rest of this item is the measured HEAD baseline, not the inherited
number:** all markers **2090 passed / 34 skipped / 1 environmental failure**, default markers
**2012 passed / 34 skipped**, zero license-skip lines on both. Surfaced to the orchestrator.

### Lint and type floors

| check | measured | expected |
|---|---|---|
| `ruff check src/` | **12** | 12 ✓ |
| `mypy src/` | **55 errors in 11 files (71 source files)** | 55 ✓ |
| `git diff --check` | clean (exit 0) | clean ✓ |

### TEAx tip

```
git -C /home/reid/1cfe/teax rev-parse --short HEAD   → 5b70ae9
git -C /home/reid/1cfe/teax rev-parse --abbrev-ref HEAD → constraint-semantics-item3
```

Matches the plan. The checkout stays on that branch for the whole item.

### `catf_mfe_d5` measured, for the corrected PROVENANCE paragraph

From the committed `tests/fixtures/catf_mfe_d5/instance_graph_snapshot.json`, projected
license-free:

| quantity | measured |
|---|---|
| modules | **43** |
| `usage_records` | **65** |
| `concrete_entries` | **0** |
| `excluded_records` | **9** |
| disposition histogram | `{non_reaching: 56, excluded: 9}` |

**Deviation:** the plan and spec prose say the model "has built 42 modules". The measured
count is **43**. 43 is the number consistent with every design probe delta (P1 44 = 43+1,
P2 45, P6 46, P7 48), so 42 was the stale figure. No expectation is derived from it; the
corrected d5 paragraph records the measured 43.

### Frozen twins

`python scripts/make_d5_variant.py --check <source> <target>` for all three pairs:

```
catf_mfe_model catf_mfe_d5           → strip check: 0 problems
solar_battery_model solar_battery_d5 → strip check: 0 problems
gate_a gate_a_d5                     → strip check: 0 problems
```

`git diff --stat tests/fixtures/catf_mfe_d5/` → exactly one file,
`PROVENANCE.md`, 11 insertions / 18 deletions — the stale acceptance paragraph and the
superseded "what blocks it" section. No model byte changed. `catf_mfe_model` untouched.

---

## Phase 1 — ★ B2 de-risk at full scope, and the ruled-shape reconciliation

Scratch copy `/tmp/item5probe/p8`, forked from `tests/fixtures/catf_mfe_d5` by
`probes/setup_probe.py`. Nothing under `tests/` or `src/` changed. Every run licensed via
`probes/licensed.sh`.

### Group-by-group ladder — re-elaborated after every group

| step | edits added | result | modules | usage rows | concrete | histogram (eligible/excluded/non_reaching) |
|---|---|---|---|---|---|---|
| P7 reproduction | library + A2 + A3 + A7 + A8 derivations + axis leg | **ADMIT** | 48 | **65** | 2 | 2 / 7 / 56 |
| group 3 | ruled library (no `ProductWithinBand`); A1 usage deleted; C37 usage deleted + `p_neutron := p_fusion - p_alpha` | **ADMIT** | 48 | **63** | 2 | 2 / 6 / 55 |
| group 4 | A4, C21, C28 deletions | **ADMIT** | 48 | **60** | 2 | 2 / 5 / 53 |
| group 4b | A7 and A8 **usage** deletions | **ADMIT** | 48 | **58** | 2 | **2 / 3 / 53** |
| group 5 | five `@inapplicable:` markers on B1–B5 | **ADMIT** | 48 | 58 | 2 | 2 / 3 / 53 |
| group 6 | axis-leg derivation **reversed** | **ADMIT** | **47** | **58** | **2** | **2 / 3 / 53** |

**B2 holds.** Every remaining edit lands with no new `SI_RENDERING_COLLISION`, no
`SI_CONSTRAINT_BLOCKED`, and no readiness refusal. The ruled shape generates.

The two executing gates at the end of the ladder:

```
ELIGIBLE CATFMFEPhysics::catf_physics::net_power_viable        occ=1
ELIGIBLE CATFMFEPhysics::catf_physics::parasitic_fraction_ok   occ=1
source_records: CATFGateForms::FractionWithinBand, CATFGateForms::PositiveQuantity
channel  CATFMFEPhysics__catf_physics__net_power_viable__d8cad14493e47fbd__evaluation
channel  CATFMFEPhysics__catf_physics__parasitic_fraction_ok__280b94b2e8d184f5__evaluation
```

**Module count note.** The ruled shape is **47** modules, not P7's 48. Reversing the axis-leg
derivation returns `axis_region.outer_radius` to a literal, which un-mints the module the
derived attribute created. Expected, and the plan pinned no module count for this phase.

### The reconciliation — P7's 65 to the ruled 58

| from | delta | to | authority |
|---|---|---|---|
| P7 composite | 65 rows, nothing deleted, axis leg derived | 65 | probe evidence only |
| − A1, A4, A7, A8, C37 | 5 derive-instead deletions | 60 | ruled table, Group A (A1/A4/A7/A8) + Group C (C37) |
| − C21, C28 | 2 placeholder deletions | **58** | `[OWNER 2026-08-13]`, O2 |
| axis leg | derivation reversed | 58 | D-S2 ruling (one consistent basis) |
| A5, A6, A9 | retained as plain `blocked-by-defect` | 58 | D-S1/D-S2 ruling |

**Derived disposition histogram, from the ruled table:** `eligible` **2** (A2, A3) ·
`excluded` **3** (A5, A6, A9 — reaching, unassessed form, exactly as in d5 today) ·
`non_reaching` **53** (B1–B5 + the 48 `awaits-capability` Group C rows) = **58**.

**The probe's measured counts equal the reconciliation table's**, row for row:
58 usage rows, 2 concrete entries, `{eligible: 2, excluded: 3, non_reaching: 53}`. No
mismatch, no triage needed.

### Correction to the plan's group list — A7/A8 are two edits each, not one

The plan's Phase 1 stencil grouped "A7, A8 derivations (P6-proven)" as if `derive-instead`
were only the derivation. It is not: `derive-instead` deletes the authored usage *and*
authors the derivation replacing it. The design probes (P6, P7) only ever did the derivation
half, which is why P7 legitimately kept all 65 rows.

Measured consequence: after groups 3 and 4 the probe sat at **60** rows, not 58. The missing
two are the A7 (`CATFMFEShield::catf_shield::CompositionConsistency`) and A8
(`CATFMFEVacuum::catf_vacuum_vessel::ThicknessConsistency`) usage deletions, added as group
4b. With them the count is exactly 58 and the histogram is exactly 2/3/53.

This is a gap in the plan's step list, not in the ruled table — `owner-disposition.md` names
all five derive-instead rows (A1, A4, A7, A8, C37) in the identity, and the arithmetic only
closes if all five usages are deleted. Recorded rather than absorbed.

### FINDING — the five `@inapplicable:` markers do not reach the domain

**Measured, not inferred.** With group 5 applied:

```
markers written in source: 5
  library/components/divertor.sysml:218      (B1 HeatLoadBalance)
  library/components/first_wall.sysml:222    (B2 TotalThicknessConsistency)
  library/components/radial_build.sysml:57   (B3 RadiusConsistency)
  library/components/shield.sysml:162        (B4 TotalThicknessConsistency)
  library/components/vacuum.sysml:157        (B5 ThicknessConsistency)
markers carried on the domain: 0
```

The markers were authored in the exact form the Item 2 fixture pins
(`tests/fixtures/constraint_domain_inapplicable/model.sysml:20`), as the **first** line of
the first `doc` body — the placement `constraint_domain_inapplicable_late_marker` requires.
Elaboration ADMITs; the markers are silently dropped.

**Cause is already documented and is not new.** B1–B5 are **inline-predicate** constraints
(`constraint X { doc /* … */ <predicate> }`), and SysIDE drops a `doc` comment inside an
inline-predicate constraint body. That is rule 3 of the population oracle, written down at
`tests/conformance/test_constraint_population_oracle.py` precisely to make this gap loud:

> An `@inapplicable` marker written in source that produced no `Inapplicability` on the
> record is a failure. … on that one shape the marker never reaches elaboration and the
> strict parse's near-miss halt cannot fire.

The Item 2 fixtures that *do* carry a working marker are all **bindings-form** usages
(`constraint c : Def { doc /* @inapplicable: … */ in v = value; }`). None of them is the
inline-predicate shape B1–B5 have.

**What it costs, exactly.** Authoring the markers as the ruled table calls for would turn
`test_every_authored_inapplicable_marker_reached_the_domain[catf_mfe_gated]` red — written 5,
carried 0 — on a test built to catch this specific silent failure. No workaround inside the
marker's own form exists: placement and spelling are already correct.

**What it does not cost.** The committed coverage account is unchanged either way.
`inapplicable_gate_count` is **0** regardless, because B1–B5 are plain (non-asserted) usages
and bucket row 1 decides "not asserted → inventory only" before the inapplicable predicate is
consulted (`generation/coverage.py:7-27`). The measured histogram with the markers applied is
identical to the histogram without them: 2 / 3 / 53. **Every number the plan commits in Phase
2 survives this finding untouched.**

**Parked, not resolved.** Surfaced to the orchestrator per capture-fidelity §4.

**Scope of the finding, measured.** The five marker lines sit inside `doc` bodies *after*
each constraint's declaration line, and no other constraint usage follows them in those five
files. Scanning both variants:

```
with markers: 58 rows   without markers: 58 rows
rows whose (usage_qualified_name, source_file, source_line) identity differs: 0
```

So **Phase 2's expectation artifacts are independent of how this is resolved** — the
population oracle's 58 identities and the coverage account are byte-identical either way.
The decision changes Phase 3's fixture bytes and the PROVENANCE record for B1–B5, nothing
upstream of them.

---

## Phase 2 — Expectation artifacts (SC-6)

All three landed in **`1247a3b`**, expectations only, no fixture byte.

### Commit-order evidence — the recipe differs by artifact kind (r2-1)

| artifact | command | commit |
|---|---|---|
| `tests/expectations/constraint_population/catf_mfe_gated.json` | `git log --diff-filter=A --format=%H -- <path>` | **`1247a3b`** |
| `tests/expectations/gated_manifest/catf_mfe_gated.json` | `git log --diff-filter=A --format=%H -- <path>` | **`1247a3b`** |
| `tests/unit/data/expected-coverage.md` ledger row | `git log -S'catf_mfe_gated' --format=%H -- <path>` | **`1247a3b`** |
| `tests/fixtures/catf_mfe_gated/` | `git log --diff-filter=A --format=%H -- <path>` | **`7369b3e`** |

`1247a3b` is the parent of `7369b3e`. **Expectation precedes actual.** The reader tests'
dates are not cited — they existed at HEAD, so their ordering proves nothing.

### The deliberate red window, measured

Licensed full suite at `1247a3b`: **2089 passed / 34 skipped / 3 failed**, zero license-skip
lines. The three failures were exactly:

```
FAILED tests/conformance/test_constraint_population_oracle.py::test_no_expectation_file_is_stranded
FAILED tests/unit/test_coverage_ledger_agreement.py::test_derived_account_equals_the_hand_written_account[catf_mfe_gated]
FAILED tests/execution/test_fusion_tea_real_teax.py::test_the_lane_runs_the_real_simkit   (pre-existing, out of floor)
```

The first two are the named window. Nothing else was red.

### How the 58 were derived

`d5's 65 rows − the 7 named deletions + the 2 renames`, then **cross-checked** against a source
scan of what the author would write. The scan supplies line numbers and checks membership; it
does not supply the membership (PD2/DR-6). Output:

```
identity: 65 = 58 carriers + 7 named deletions
cross-check: derivation and source agree on all 58 identities
```

---

## Phase 3 — The derivative lands

Authored in Phase 1's group order, re-elaborating after every group, at fixture scale:

| step | modules | rows | concrete | histogram |
|---|---|---|---|---|
| fork, unedited | 43 | 65 | 0 | 56 non_reaching / 9 excluded |
| + library | 43 | 65 | 0 | 56 / 9 |
| + A2 | 44 | 65 | 1 | 1 eligible / 56 / 8 |
| + A3 | 45 | 65 | 2 | 2 / 56 / 7 |
| + A7, A8 derivations | 47 | 65 | 2 | 2 / 56 / 7 |
| + A1, C37 | 47 | 63 | 2 | 2 / 55 / 6 |
| + A4, C21, C28 | 47 | 60 | 2 | 2 / 53 / 5 |
| + A7, A8 usage deletions | **47** | **58** | **2** | **2 eligible / 3 excluded / 53 non_reaching** |

Read back from the committed snapshot: coverage account
**`58 / 2 / 2 / 0 / 0 / {} / complete`** — equal to the ledger row committed at `1247a3b`,
**with no edit to the expectations**. Source scan vs committed expectation: **MATCH, 58 = 58**.

Full suite at `7369b3e`: **2094 passed / 34 skipped**, zero license-skip lines, red window
closed.

Frozen twins: `git status --short` clean on both `catf_mfe_d5` and `catf_mfe_model`.

---

## Phase 4 — The identity, machine-checked

```
$ python scripts/check_gated_manifest.py --check
identity closes: 65 = 58 carriers + 7 named deletions
  carriers matched by name:         56
  carriers matched by renamed_from: 2
```

License-free. Three falsifications run for real, each against a **temp copy** of PROVENANCE
with the module's path monkeypatched — not against the committed fixture, so no revert is
needed and an interrupted run cannot corrupt the tree (deviation from the plan's
"mutate then revert", same proof):

```
drop a renamed_from:
  FAIL: carriers matching neither by name nor by renamed_from:
        ['CATFMFEPhysics::catf_physics::net_power_viable']; d5 usages that are neither a
        carrier nor a named deletion: ['CATFMFEPhysics::catf_physics::ViabilityCheck']

point renamed_from: at a row a deletion claims
  FAIL: renamed_from: claims a d5 usage a deletion record also claims:
        ['CATFMFEPhysics::catf_physics::PowerBalanceConsistency']

deletion record with no authorizing row
  FAIL: deletion record A4 (CATFMFERadialBuild::catf_radial_build::TotalRadiusConsistency)
        cites no authorizing table row
```

Full suite at `0d9f474`: **2099 passed / 34 skipped**, zero license-skip lines. ruff 12,
mypy 55, `git diff --check` clean.

---

## Phase 5 — SC-8, the first committed-bytes gate

Fixture shape confirmed as the one R3 names: **`usage_records` 2, `concrete_entries` 0**.

Goldens committed at `tests/conformance/golden/zero_entry_package/`:

| file | bytes |
|---|---|
| `schemas/constraint_types.py` | 4664 |
| `modules/constraints/constraintreportaggregatormodule.py` | 3260 |

Registry carries both `ConstraintEvaluation` and `ConstraintReport`.

**Falsification, run once and reverted.** Flipping `ships_constraint_machinery` back to Item
2's concrete-entry bar (`catalog.usage_records` → `catalog.concrete_entries`):

```
FAILED test_the_zero_entry_package_ships_the_bytes_we_committed[schemas/constraint_types.py]
   FileNotFoundError: .../pkg/schemas/constraint_types.py     (the file is not emitted at all)
FAILED test_the_registry_imports_the_constraint_machinery
   AssertionError: assert 'ConstraintEvaluation' in '...'      (both imports gone)
```

**Recorded honestly: only one of the two pinned files moves under that flip.** The aggregator
module is still emitted, so its golden stays green. The gate is real but the two files are not
equally sensitive to this particular bar.

Reverted; `git diff --stat src/sysml_codegen/resolution/models.py` empty; gate green again.
`test_v6_recapture_batch` still green — the snapshot was captured per fixture through the
shipped CLI, so the 37-record manifest is untouched.

Full suite at `1a7328c`: **2103 passed / 34 skipped**, zero license-skip lines.

---

## Phase 6 — Acceptance: three routes, and a STOP

### Three routes, exact counts

| | route 1 — live (`--models`, licensed) | route 2 — in-place snapshot | route 3 — relocated snapshot |
|---|---|---|---|
| files | 101 | 101 | 101 |
| module `.py` files | 36 | 36 | 36 |
| `inputs/*.json` | 9 | 9 | 9 |
| raw tree digest | `1762214feba0de57bcac8522ac709e1657ecaff0034808c5bc91f6917e6a2d3c` | `9586f5d9b5e8ae64ad1b1f1f3e41972641a9caebc6e95a073113a5db55883510` | `9586f5d9b5e8ae64ad1b1f1f3e41972641a9caebc6e95a073113a5db55883510` |
| model contract `semantic_fingerprint` | `03b59be74c9a29bc99e082b208dc1ccbca179ac5b0f40d191e807166440bb535` | `5c65622f11d194a9887aae1002c9a131606ffe36f6392c48fcca42997caa090c` | `5c65622f11d194a9887aae1002c9a131606ffe36f6392c48fcca42997caa090c` |

**Routes 2 and 3 are byte-identical.** The relocated read produces the same package as the
in-place read, which is the portability claim.

The projected graph, from the sealed snapshot, identical across all three:

```
modules 47 | usage_records 58 | concrete_entries 2 | excluded_records 3
histogram {eligible: 2, excluded: 3, non_reaching: 53}
coverage  58 / 2 / 2 / 0 / 0 / {} / complete
entry-point groups 9 | entry points 65
ENTRY CATFMFEPhysics::catf_physics::net_power_viable
      channel CATFMFEPhysics__catf_physics__net_power_viable__d8cad14493e47fbd__evaluation
ENTRY CATFMFEPhysics::catf_physics::parasitic_fraction_ok
      channel CATFMFEPhysics__catf_physics__parasitic_fraction_ok__280b94b2e8d184f5__evaluation
```

`inputs/` and `pipelines/` are byte-identical on all three routes. D6's key is confirmed in
place: `physics_params.json` carries `CATFMFEPhysics__catf_physics__p_fusion: 2600.0`.

### FINDING 6-A — the catalog fingerprint is not portable across routes (pre-existing)

Route 1 differs from routes 2/3 beyond provenance comments. Normalising the source-root prefix
in every provenance comment leaves exactly one substantive difference:

```
modules/constraints/constraintreportaggregatormodule.py
-    CATALOG_FINGERPRINT = "4edaf85e8c6737e5fb55a7c07cf2beabf8a3112ec5539d1267a3648bda7c022c"   (live)
+    CATALOG_FINGERPRINT = "65083fb7e1350f6862974428c7bf1f6b960bc6b76011583b42d62c7848f33b25"   (snapshot)
```

**Cause, chased to source.** `ConstraintCatalog.recomputed_fingerprint`
(`resolution/models.py:597-622`) hashes the full model dump of `usage_records`, and those rows
carry `source_file`. The live route records `tests/fixtures/catf_mfe_gated/…`; the snapshot
route records `root-0/…`. Same graph, same semantics, different paths, different fingerprint —
and the generated aggregator bakes it in as a runtime coherence check.

**Ownership: pre-existing, not this item's.** Reproduced on the untouched frozen twin:

```
catf_mfe_d5 live     CATALOG_FINGERPRINT = 39d02855cd9bfa9adf628af94f6c91d8fddf783d947ad8a6762b5e2aec78027f
catf_mfe_d5 snapshot CATALOG_FINGERPRINT = beaaa339a11dd229462f22e0ae51e41c6922e0aa1abfb5d605d6f495893c91ca
```

It does **not** reproduce on `constraint_domain_satisfy_calc_def`, whose model is a single flat
`model.sysml` — both routes there agree (`9b93a157…`). So the split appears when a model has a
nested source layout, which is why no existing fixture caught it.

Recorded, not fixed: it contradicts the plan's "all three agree on the instance fingerprint",
but it is not against a ruled row and not caused by Item 5.

### FINDING 6-B — `value` is a reserved name, so the ruled A2 spelling cannot generate

Route 1's first run refused at a **generation preflight**, not at elaboration:

```
ERROR: Code generation failed: Constraint name-safety violation:
  constraint_id='CATFMFEPhysics__catf_physics__net_power_viable__d8cad14493e47fbd',
  scope='predicate', kind='generated_binding_overlap',
  final_binding='value' collides with generated binding 'value';
  identities=[raw_name='value', qualified_name='CATFGateForms::PositiveQuantity::value']
```

`value` is a **reserved generated local** in predicate scope
(`generation/constraint_name_safety.py:39`, `generated_locals=frozenset({"value"})`), so a
constraint formal can never be named `value` — and `owner-disposition.md`'s A2 cell proposes
exactly `constraint def PositiveQuantity { in value : Real; value > 0 }`.

**Resolved inside authority, not improvised.** Open point **O7** records the library's names as
**provisional and design-owned**, and the spec already blesses formal renaming as "a local edit"
for the structurally identical self-named-binding case. The formal is renamed
`value` → `quantity` in the definition and its one binding. Nothing ruled changes: no
disposition, tolerance, intent class, or count moves, and the committed expectation still
matches the source (**MATCH, 58 = 58**) because the rename touches no usage name or line.

**What this exposes about Phase 1.** The de-risk probe only **elaborated**; it never
**generated**. A whole class of refusals — the five generation preflights — was untested at the
gate that existed to be the cheap place to find them. B2 was tested for the wrong half of the
landing.

### FINDING 6-C — D6's mutation route is refused by the product

D6 says the mutation "lives in the generated `inputs/*.json`". That route does not exist: the
package contract covers the on-disk bytes, so editing a sealed input breaks the seal, and
`tests/execution/test_fusion_tea_mutation_teax.py::test_editing_a_sealed_input_and_resealing_is_refused`
pins the refusal in code rather than policy.

The supported route, already used by Item 3's mutation lane, is TEAx's typed entry injection:
`CandidateBridge.build(selected_fields)` fills every entry channel from the package's own
modelled defaults and `PreparedEvaluator.evaluate` runs the real executor against that mapping.
**D6's intent is preserved exactly** — one generated package, two input sets, the mutation a
physics input value rather than a model edit or a study-config override — and the seal stays an
active check, because the same loader verifies the package the evaluator runs. Taken, recorded.

### FINDING 6-D — **STOP.** The authored CATF design point is itself infeasible

The lane works. Generate → seal → load → execute → policy runs end to end, and both gates
report. What is false is the **direction** the ruled SC-5 row assumes.

Measured on the sealed package through real TEAx, at the **authored** inputs
(`p_fusion = 2600.0`, no overrides):

```
headline = 'violated'
CATFMFEPhysics__catf_physics__net_power_viable__d8cad14493e47fbd      = 'violated'
CATFMFEPhysics__catf_physics__parasitic_fraction_ok__280b94b2e8d184f5 = 'violated'

CATFMFEPhysics__catf_physics__gross_electric__p_electric_gross =  1546.72 MW
CATFMFEMagnets__catf_tf_system__cryo_load__cooling_power       =  8396.05 MW
```

The magnet cryoplant draws **5.4× the plant's entire gross electric output**, so net power is
negative at the authored design point and A2 correctly reports `violated`.

**Ownership: the model, not the derivative.** Identical numbers from `catf_mfe_d5`, untouched:

```
catf_mfe_d5  cooling_power = 8396.054399837172   p_electric_gross = 1546.723690193402
catf_mfe_gated cooling_power = 8396.054399837172 p_electric_gross = 1546.723690193402
```

Item 5's edits changed no physics. (`catf_mfe_d5` executes no gates, so it reports
`not_assessed` and this was invisible there — which is the whole point of the epic.)

**Chased to a probable unit error.** `MagnetCryogenicLoad`
(`library/analyses/thermal_loads.sysml:45-66`):

```
heat_leak     = magnet_volume * 0.05                                  // MW
cooling_power = (thermal_load_cryo / operating_temp) * (300.0 / carnot_efficiency)   // MW
```

The Carnot factor is `300/(T·η) = 300/(4.5 × 0.3) ≈ 222`, so the cryogenic-temperature heat
load is `8396/222 ≈ 37.8 MW`, essentially all of it `heat_leak = magnet_volume × 0.05`. **A
static heat leak of ~38 MW into a 4.5 K magnet system is off by three to six orders of
magnitude** — ITER-scale static loads are tens of kilowatts. The coefficient `0.05` reads as
W/m³ or kW/m³ written as MW/m³.

**The gate is working as designed.** It caught an implausible model that was previously
invisible, which is the epic's critical success factor doing its job.

**Both directions demonstrated**, so only the labelling of "valid" is open:

| `p_fusion` (MW) | gross (MW) | A2 | A3 | headline |
|---|---|---|---|---|
| **2600 (authored)** | 1546.7 | violated | violated | **violated** |
| 5000 | 2953.2 | violated | violated | violated |
| 10000 | 5883.5 | violated | violated | violated |
| 14000 | 8227.7 | violated | violated | violated |
| 16000 | 9399.8 | **satisfied** | violated | violated |
| **20000** | 11744.0 | **satisfied** | **satisfied** | **satisfied** |
| 30000 | 17604.4 | satisfied | satisfied | satisfied |
| 60000 | 35185.9 | satisfied | satisfied | satisfied |

**What this contradicts.** `owner-disposition.md`'s SC-5 table gives A2's rejecting mutation as
"Drop `p_fusion` … far enough that `p_net` goes negative", which presupposes `p_net > 0` at the
authored point. Measured false. The committed expectations name the authored candidate as the
valid one (`expected-coverage.md` headline `full_satisfaction`;
`gated_manifest`'s `expected_study_outcomes.valid_candidate`).

**What this does not touch.** The coverage account is about the denominator, not the outcome:
`58 / 2 / 2 / 0 / 0 / {} / complete` is unchanged and still correct at every probed point. The
ledger's parametrized test asserts only `coverage_account`, so the committed row's numbers all
stand; the one wrong cell is the **headline**.

**Vocabulary note.** TEAx's runtime tokens are `satisfied` / `violated`; the report vocabulary
is `full_satisfaction` / `violation` (ADR-009, one-to-one). No contradiction — but the
expectation files use the report vocabulary and the runtime evidence uses the runtime tokens.

**RULED 2026-08-13 — option (a), `[AGENT]` ratified by owner.** Candidates are labeled
**gate-feasible / gate-infeasible under the model as authored**. The authored CATF design point
is the **rejected** candidate. The raised-`p_fusion` candidate carries the satisfied path as a
**machinery exemplar, not a recommended design**. The coefficient defect is filed as
`[CATF-CRYO-HEATLEAK]`; correcting it is a separately-authorized follow-on. Acceptance completed
below.

**Correction to the diagnosis above, from the source-derived re-computation.** The ruling
required the amended expectations to rest on a computation re-derived from model source rather
than transcribed from output, and doing that caught an error in my own first estimate. The
figures in the STOP report assumed a 4.5 K system and a ~220× amplification, giving ~38 MW.
The model says `operating_temp = 20 [K]` (`magnets.sysml:66`), so:

| term | source | value |
|---|---|---|
| `nuclear_heating` | `0.05 * 2079.41 * (15.31526418625125 / 31.101767270540993)` | 51.197595 MW |
| `ac_losses` | authored `0.0` | 0.0 MW |
| **`heat_leak`** | **`magnet_volume * 0.05` = `2334.4698659954747 * 0.05`** | **116.723493 MW** |
| `thermal_load_cryo` | sum, at **20 K** | 167.921088 MW |
| amplification | `300 / (20 * 0.3)` | **50.0×** |
| `cooling_power` | `167.921088 * 50` | **8396.054399837172 MW** |

The derivation reproduces the executed value **bit-exactly**, which is what licenses it as the
basis for the amended cells. `heat_leak` is **69.5%** of the cryogenic load, and
`cooling_power / p_electric_gross = 5.43×`. Runnable and self-checking at
`cryo_derivation.py` in this item home.

---

## Phase 6 (continued) — acceptance completed under the 6-D ruling

### Both candidates, through generate → seal → load → execute → policy → durable record

One generated package (`route2_inplace`), two candidates, injected through TEAx's typed entry
route (`CandidateBridge` + `PreparedEvaluator`) — see finding 6-C for why not `inputs/*.json`.

| | **gate-infeasible (authored)** | **gate-feasible (exemplar)** |
|---|---|---|
| overrides | *none* — `p_fusion = 2600.0` as authored | `CATFMFEPhysics__catf_physics__p_fusion = 20000.0` |
| A2 `net_power_viable` | **`violated`** | `satisfied` |
| A3 `parasitic_fraction_ok` | **`violated`** | `satisfied` |
| report headline | **`violation`** | `full_satisfaction` |
| TEAx runtime headline | `violated` | `satisfied` |
| canonical token | `violated` | `satisfied` |
| **policy disposition** | **`reject`** | `feed-strategy` |
| `p_electric_gross` | 1546.723690193402 MW | 11743.95146302617 MW |
| `cryo_load.cooling_power` | 8396.054399837172 MW | 8396.054399837172 MW |
| `executable_fingerprint` | `cb61b0ec67fc9d9a037820a6fc605bcf4cc09bcff968454a34caf0cef5fded2f` | *same* |
| `catalog_fingerprint` | `65083fb7e1350f6862974428c7bf1f6b960bc6b76011583b42d62c7848f33b25` | *same* |

The cryo load is identical across both because it depends on magnet geometry, not `p_fusion`.
That is the whole mechanism: raising fusion power outruns a fixed parasitic load rather than
fixing it, which is why the exemplar is explicitly **not** a design.

### The durable case record carries verdict **and** coverage, for both candidates

Both records assert non-null. Coverage account persisted on each row, identical:

```
authored_usage_total 58 | applicable_gate_total 2 | assessed_gate_count 2
unassessed_gate_count 0 | inapplicable_gate_count 0 | unassessed_reasons {}
coverage_state "complete"
```

Equal to the pre-committed ledger row, **at both candidates** — coverage is about the
denominator, so the rejection does not move it. Each record also carries its
`catalog_fingerprint`, which is what lets a study query answer "how covered was this candidate"
off the row without opening evidence artifacts (Item 3 / D7).

Records written to `/tmp/item5acc/acceptance/case_records.json`; the run is reproducible from
`probes/acceptance_run.py`, which asserts every claim above rather than printing it.

**SC-5 is met.** A candidate reaches the configured satisfied path, and a physics input value
takes a candidate to **`reject`** through generated package → TEAx normalization → policy →
durable case storage. Under the ruling, the rejected one is the model's own authored design
point.

### What this item actually caught

The first execution of these gates found a model defect that had been invisible for the model's
entire life. `catf_mfe_d5` carries the same 65 authored checks and executes **zero** of them, so
it reports `not_assessed` and nothing ever contradicted the design point. The moment two of
those checks became executable gates, the authored candidate was rejected on physics.

That is the epic's founding failure mode — a design search cannot tell a candidate that passed
its gates from one nobody checked — **demonstrated and closed by the same item**.
