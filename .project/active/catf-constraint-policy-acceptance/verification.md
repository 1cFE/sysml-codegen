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

**The one failure is environmental, not a regression.**
`tests/execution/test_fusion_tea_real_teax.py::test_the_lane_runs_the_real_simkit` fails with

```
AssertionError: the in-repo stub runner was imported on the real-TEAx lane;
its fake simkit would shadow the installed one
```

That lane must be hosted in the agentic-mbse venv with a `sys.path` insert of
`teax/packages/teax-simkit`; the task venv makes the in-repo stub importable. It is
pre-existing at this HEAD and unrelated to any Item 5 edit (the only tree change at the time
of the run is d5's PROVENANCE prose).

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
