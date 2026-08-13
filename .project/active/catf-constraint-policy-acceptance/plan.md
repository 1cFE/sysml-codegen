# Implementation Plan: CATF Derivative and End-to-End Acceptance

**Status:** Draft
**Created:** 2026-08-13
**Last Updated:** 2026-08-13
**Epic:** CONSTRAINT-SEMANTICS, Item 5
**Branch:** `item7-rebuild` (worktree `/home/reid/1cfe/sysml-codegen-item7-rebuild`); coordinated
TEAx work on `/home/reid/1cfe/teax` branch `constraint-semantics-item3` @ `5b70ae9`

## Source Documents

- **Spec:** `spec.md` (SC-1 met; SC-3 twice-amended to the identity `65 = 58 + 7`)
- **Ruled authority:** `owner-disposition.md` — RULED 2026-08-13. Sole source of intent classes,
  tolerance values, deletion authority, and bases. No agent re-derives a number from it.
- **Design:** `design.md` rev 2 (APPROVED at review round 2, commit `1afd83e`) ← component detail,
  D1–D7, the SURFACED/RULED record, invariants
- **Review:** `design-review.md` (round-2 addendum: Approve + four carry-forwards)

Everything about *what* to build lives in `design.md`. This file is *order, proof, and evidence*.

---

## The Point

A design search must be able to tell a candidate that **passed its physics gates** from one
**nobody checked**.

> **[OWNER]** A design search can trust the generated feasibility evidence to represent every
> applicable asserted physics gate, while every other authored constraint remains visibly
> dispositioned.
> (`.project/backlog/epic_constraint_semantics_contract.md`, Critical Success Factor)

Items 1–4 built the machinery — the assert-only rule, a catalog that accounts for every authored
usage, a coverage-truthful report and TEAx policy, two predicate-boundary fixes — each against a
purpose-built fixture. None of it has been driven end to end on the richest model we have, and that
model is the failure case the epic exists to close: `catf_mfe_d5` carries **65 authored constraint
usages, 9 reaching, 0 executed**. Until a real physics mutation travels generated package → TEAx
normalization → policy → durable case record and comes back `reject`, the critical success factor is
an assertion.

Two totals must never be conflated, and this item is where they meet a real model: **inventory
totality** over all 65 authored usages, and **feasibility coverage** over applicable asserted gates
only.

---

## Implementation Strategy

### Phasing rationale

Three things drive the order, and all three are measured facts rather than preferences.

1. **The landing is atomic.** A profile BLOCK on any asserted constraint halts generation of the
   whole model (`elaborate.py:1145-1152`, `SI_CONSTRAINT_BLOCKED`), and a projection collision does
   the same. There is no partial-migration state. So every edit that will ever be in the fixture is
   probed on a scratch copy *before* the fixture exists (Phase 1).
2. **Expectations must precede actuals, by commit.** The owner's sequence, carried as SC-6 and
   invariant 5. Expectation artifacts land in an earlier commit than the fixture that produces the
   outputs they pin (Phase 2 before Phase 3).
3. **The probe shape is not the ruled shape.** P7 admitted with 65 rows because it deleted nothing
   and derived the axis leg the ruling drops. The ruled target is **58 carriers, 2 executing gates**.
   Reconciling those two is a gate on Phase 2, not a footnote.

### Critical path

```
Phase 0  baseline + environment proof (+ d5 PROVENANCE paragraph)
   │
Phase 1  ★ B2 full-scope de-risk probe → ruled-shape reconciliation      ← GATE
   │        (no expectation file may be written before this closes)
Phase 2  expectation artifacts committed                                 ← SC-6 evidence
   │        (deliberate red window opens here — see below)
Phase 3  author the derivative, probe-order, atomic landing              ← red window closes
   │
Phase 4  integrity: check_gated_manifest.py, 65 = 58 + 7
   │
Phase 5  SC-8 golden + deliberate falsification        (independent of 1–4; may run in parallel)
   │
Phase 6  acceptance: three routes + TEAx execution, verification.md
   │
Phase 7  close-out: docs, audit prep
```

### First proof point

**Phase 1's composite probe admitting with the ruled counts.** Everything downstream — every
expectation file, the identity, the coverage account — is written against numbers that only mean
something if that probe comes back ADMIT with 58 usage rows and 2 concrete entries. It is also the
cheapest place to discover a second `SI_RENDERING_COLLISION`; discovering one during Phase 3 costs
the whole authoring pass.

### The deliberate red window (read this before Phase 2)

SC-6 requires the expectation artifacts to be committed **before** the fixture. Two tests go red in
that gap, and they are supposed to:

- `tests/conformance/test_constraint_population_oracle.py::test_no_expectation_file_is_stranded` —
  license-free; fails while `catf_mfe_gated.json` exists and the fixture directory does not.
- `tests/unit/test_coverage_ledger_agreement.py::test_derived_account_equals_the_hand_written_account[catf_mfe_gated]`
  — license-gated; fails on a licensed run in the same gap.

**Do not close the gap by reordering, by deleting the expectation, or by landing the fixture first.**
The gap *is* the SC-6 evidence. Phase 2 and Phase 3 are one contiguous work unit: Phase 2 ends in a
committed, knowingly-red state; Phase 3's first commit (the forked fixture directory) closes it.
Both commit hashes go into `verification.md` as the ordering proof. Every other phase ends green.

### Overall validation approach

- Each phase starts by writing or naming the check that would fail if the phase were wrong.
- Each phase ends with the suite command below and an explicit "what we now know" statement.
- Numbers are recorded exactly, never summarized — `verification.md` is the home (SC-7).

---

## Environment (inherited; repeat these, do not re-derive)

- **Test invocation:** `/home/reid/1cfe/item7-rebuild-venv/bin/python -m pytest`. **Never `uv run`**
  — it resolves `agentic_mbse` to the wrong checkout.
- **Licensed runs:** `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a`. There is no `.env`
  in this repo. **Zero `no live syside license` skip lines is the only proof a licensed run really
  ran** — count them, don't assume. The probe wrapper `probes/licensed.sh` does both steps.
- **Frozen twins:** `catf_mfe_model` and `catf_mfe_d5` stay byte-untouched, except d5's stale
  acceptance paragraph in `tests/fixtures/catf_mfe_d5/PROVENANCE.md`.
  `python scripts/make_d5_variant.py --check` must still pass after that edit.
- **Baselines not to regress:** codegen **2050 passed / 34 skipped** (licensed, at Item 3 close);
  `ruff check src/` **12**; `mypy src/` **55**; `git diff --check` clean.
- **TEAx:** `/home/reid/1cfe/teax`, branch `constraint-semantics-item3` @ `5b70ae9`. **The checkout
  stays on that branch for the whole item.** Real-simkit runs: host in the agentic-mbse venv with a
  `sys.path` insert of `teax/packages/teax-simkit`; the teax `.venv`/`uv run` route is broken.
- **Snapshot capture:** capture per fixture through the shipped path (`sysml-codegen snapshot` /
  `capture_instance_graph_snapshot`). **Do not run `scripts/capture_v6_batch.py`** — it rewrites
  every `captured_at` in the 37-fixture corpus, and `tests/conformance/test_v6_recapture_batch.py`
  pins that corpus at exactly 37 records / 15 captured / 22 refused. Neither new snapshot belongs in
  that manifest. If a batch recapture becomes unavoidable, run the byte-identity gate as a
  timestamp-only diff check plus revert so only the new fixture shows.

---

## Phase 0 — Baseline, environment proof, and the d5 paragraph

### Goal
Pin the numbers every later phase claims "no regression" against, prove the licensed environment
actually licenses, and land the one isolated edit that has no dependencies.

### Assumption Under Test
That the recorded baselines (2050/34, ruff 12, mypy 55) still hold at this HEAD, and that the
licensed suite really runs licensed here.

### Steps
- [ ] Licensed full suite; record passed/skipped and **grep the output for `no live syside license`
      → expect 0 lines**. Record the count in `verification.md` (create it).
- [ ] `ruff check src/` and `mypy src/` → record counts (expect 12 / 55).
- [ ] `git -C /home/reid/1cfe/teax rev-parse HEAD` and `--abbrev-ref HEAD` → record; expect
      `5b70ae9` on `constraint-semantics-item3`. If it differs, **stop and surface** — acceptance
      evidence cites that tip.
- [ ] Correct the stale acceptance paragraph in `tests/fixtures/catf_mfe_d5/PROVENANCE.md` (it still
      claims the exact route refuses the model with 152× `SI_OCCURRENCE_MISSING`; the model has built
      42 modules since). Nothing else in that fixture changes.
- [ ] `python scripts/make_d5_variant.py --check` → passes for all three variants.
- [ ] `git diff --stat tests/fixtures/catf_mfe_d5/` → exactly one file, exactly the paragraph.

### Validation
- [ ] Full suite green at the recorded baseline; `git diff --check` clean.

**What we know after this phase:** the environment is real, the baseline is measured at this HEAD,
and the frozen-twin obligation is discharged and still checkable.

---

## Phase 1 — ★ B2 de-risk at full scope, then reconcile to the ruled shape

### Goal
Establish, on a throwaway scratch copy, that **the ruled shape generates** — not the probe shape.
P7 tested the library, A2, A3, A7, A8 and the axis leg. It tested **none** of: the A1/C37 calc-def
derivation, the A4 deletion, the C21/C28 placeholder deletions, the axis-leg *reversal* the ruling
introduced, or the five `@inapplicable:` markers.

### Assumption Under Test
**B2** (`design.md#key-bets`): the landable set is stable under every remaining edit, with no new
collision. If false, the atomic landing fails on the first authoring pass and the shape has to be
re-scoped before any expectation exists.

### Probe stencil (scratch, throwaway, nothing committed to `tests/`)
```
probes/setup_probe.py p8                      # fresh copy of catf_mfe_d5 under /tmp/item5probe/p8
# group 1: library + A2 + A3            (P7's proven core)         → re-elaborate
# group 2: A7, A8 derivations           (P6-proven)                → re-elaborate
# group 3: A1 + C37 derivation in AlphaNeutronSplit                → re-elaborate
# group 4: deletions A4, C21, C28                                  → re-elaborate
# group 5: five @inapplicable: markers on B1–B5                    → re-elaborate
# group 6: axis-leg REVERSAL (the ruling drops it; P7 had it)      → re-elaborate
probes/licensed.sh probes/run_probe.py /tmp/item5probe/p8
# expect: ADMITTED, usage_records == 58, concrete_entries == 2,
#         dispositions == {eligible: 2, excluded: 3, non_reaching: 53}
```

### Steps
- [ ] Reproduce P7's composite first, unchanged, and confirm it still admits (48 modules, 2 gates,
      65 rows). A drift here means something moved under the design and everything after it is suspect.
- [ ] Add the remaining edits **group by group, re-elaborating after each group**. Record each
      group's outcome. A BLOCK or collision names the group that caused it — that is the whole
      reason for the grouping.
- [ ] Author the five `@inapplicable:` markers **by copy from the Item 2 fixtures that pin the exact
      form** (`tests/fixtures/constraint_domain_inapplicable/`). A malformed directive halts
      generation at `error` even on a plain usage.
- [ ] Drive any rewrite off the **chain name** carried by `block_feature_chain`, never off
      `file:line` — every entry of a multi-chain block renders the same location (Item 4 limit 2).
- [ ] Author **no bare self-named binding**. If one becomes unavoidable, **surface and stop**: the
      D-2 vs D-4/SRC-01 conflict is parked at the umbrella level and is not resolved inside this item.

### Reconciliation (the gate — write this down before Phase 2 starts)
Record in `verification.md` a table with one row per delta from P7's 65 to the ruled 58, each row
citing the authorizing table row:

| from | delta | to | authority |
|---|---|---|---|
| P7 composite | 65 rows, nothing deleted, axis leg derived | — | probe evidence only |
| − A1, A4, A7, A8, C37 | 5 derive-instead deletions | 60 | ruled table, Group A / C37 |
| − C21, C28 | 2 placeholder deletions | **58** | `[OWNER 2026-08-13]`, O2 |
| axis leg | derivation reversed | 58 | D-S2 ruling (one consistent basis) |
| A5, A6, A9 | retained as plain `blocked-by-defect` | 58 | D-S1/D-S2 ruling |

And the derived disposition histogram, from the ruled table (not from a dump):
**`eligible` 2** (A2, A3) · **`excluded` 3** (A5, A6, A9 — reaching, unassessed form, exactly as in
d5 today) · **`non_reaching` 53** (B1–B5 + the 48 `awaits-capability` Group C rows) = **58**.

- [ ] The probe's measured counts equal the reconciliation table's. **Any mismatch stops the phase**
      — triage as fixture-wrong / reconciliation-wrong / B2-false, and surface the third.

### Validation
- [ ] Probe ADMITs with 58 usage rows, 2 concrete entries, histogram as above.
- [ ] Nothing under `tests/` or `src/` changed; `/tmp/item5probe/*` is throwaway.
- [ ] Reconciliation table committed to `verification.md`.

**What we know after this phase:** the ruled shape generates, the atomic landing is safe to attempt,
and every expectation number now has a measured referent. **No expectation file may be written before
this checkbox set is complete.**

---

## Phase 2 — Expectation artifacts, committed before the fixture (SC-6)

### Goal
Commit every expected output, derived from the ruled table and Phase 1's reconciliation, while the
derivative does not yet exist to produce them.

### Assumption Under Test
That the expectations are derivable from **what the author will write** rather than from a dump —
Item 3's PD2/DR-6 rule. An expectation transcribed from a run inherits exactly the error it exists to
falsify.

### Test stencil (the checks these files feed already exist at HEAD — name them, don't rewrite them)
```
tests/conformance/test_constraint_population_oracle.py   # identity list, by name+file+line
tests/unit/test_coverage_ledger_agreement.py             # parses the ```ledger``` block
```

### Files to commit (one commit, before any fixture byte)
- [ ] **`tests/expectations/constraint_population/catf_mfe_gated.json`** — the 58 carrier identities
      (`usage_qualified_name`, `source_file`, `source_line`), derived from d5's 65-row expectation
      minus the 7 deletions, with the two renamed gates carrying their **new** names
      (`…::net_power_viable`, `…::parasitic_fraction_ok`) and their new lines.
- [ ] **`tests/unit/data/expected-coverage.md`** — one new prose entry plus one line in the
      ```` ```ledger ```` block, in the existing field order:
      `catf_mfe_gated | 58 | 2 | 2 | 0 | 0 | {} | complete | full_satisfaction | 2`
      The prose entry cites the file and line of every usage it counted and states the
      `inapplicable_gate_count = 0` reasoning explicitly (below).
- [ ] **Expected catalog disposition histogram** — `2 eligible / 3 excluded / 53 non_reaching`, with
      the three `excluded` rows named (A5, A6, A9) and stated to be indistinguishable from any other
      plain usage in the catalog.
- [ ] **D2's expected identity** — `65 = 58 carriers + 7 named deletions`, with the 7 deletions named
      (A1, A4, A7, A8, C37, C21, C28) and the 2 `renamed_from:` carriers named. Store it as a
      committed data file the script reads (not inline in `check_gated_manifest.py`) so the
      commit-order evidence is content-scoped and unambiguous.
- [ ] **Expected report / study outcomes** — valid candidate: headline `full_satisfaction`, both
      gates satisfied, study default feed-strategy/penalize. Mutated candidate: headline `violation`
      via **A2**, study default `reject`. A3 is reported either way and is not asked to carry the
      rejection.

### Two facts to write down correctly (both are traps)
- **`inapplicable_gate_count` is 0, not 5.** The five `@inapplicable:` markers sit on *plain* usages,
  and bucket row 1 ("not asserted → inventory only") is decided before the inapplicable predicate is
  consulted (`generation/coverage.py:7-27`). Write 0, and write the reason beside it.
- **`assessed_entry_count` is 2** — the tenth ledger cell the design left unstated. Each of A2 and A3
  hangs off `catf_physics`, which has one occurrence. Derive it that way; if a later run disagrees,
  that is a triage (fixture wrong / ledger wrong / bet false), never a quiet edit.

### Commit-order evidence (r2-1 — the recipe differs by artifact kind)
- [ ] **New files** (`catf_mfe_gated.json`, the identity data file):
      `git log --diff-filter=A --format=%H -- <path>`
- [ ] **Edits to existing files** (the `expected-coverage.md` ledger row — `--diff-filter=A` returns
      Item 3's file-creation commit, which is the wrong answer):
      `git log -S'catf_mfe_gated' --format=%H -- tests/unit/data/expected-coverage.md`
- [ ] Both must return commits that **precede** `git log --diff-filter=A --format=%H --
      tests/fixtures/catf_mfe_gated/`. Record all hashes in `verification.md`.
- [ ] Do **not** cite the reader tests' dates — they existed at HEAD, so their ordering proves nothing.

### Validation
- [ ] `git show --stat HEAD` — the commit touches expectations only, no fixture bytes.
- [ ] Suite is red on exactly the two named tests (the deliberate window). Record both names and the
      commit hash. Anything else red is a real failure — stop.

**What we know after this phase:** every number the derivative must reproduce is committed, derived
from the ruled table, and provably older than the thing that will produce it.

---

## Phase 3 — Author the derivative, probe-first, atomic

### Goal
Land `tests/fixtures/catf_mfe_gated/` in the exact shape Phase 1 proved, with a PROVENANCE that
accounts for every difference from `catf_mfe_d5`.

### Assumption Under Test
That the probe's scratch edits transfer to a committed fixture unchanged — same edits, same order,
same result at fixture scale.

### Steps
- [ ] Fork `catf_mfe_d5` → `tests/fixtures/catf_mfe_gated/` (**this commit closes the red window**;
      land it immediately after Phase 2's commit).
- [ ] Apply the edits **in Phase 1's proven group order, re-elaborating after each group**:
      library (`library/constraints/gate_forms.sysml`, package `CATFGateForms`:
      `PositiveQuantity`, `FractionWithinBand` — **no `ProductWithinBand`**, its only consumer is
      parked) → A2 → A3 → A7/A8 derivations → A1/C37 derivation → the A4/C21/C28 deletions →
      the five `@inapplicable:` markers. A5, A6, A9 are left exactly as d5 wrote them.
- [ ] Each of the 7 derivations carries a **doc comment recording the undirected relation and stating
      that the direction is a chosen basis, not physics** (owner's structural amendment).
- [ ] No `[unit]` literal in either surviving gate's predicate body (D3 — both are dimensionless-safe;
      the §8 both-operands spelling stays the supported unit-carrying form, these two just don't use it).
- [ ] Capture the fixture's v6 snapshot (`instance_graph_snapshot.json`) through the shipped capture
      path. **Not** via `capture_v6_batch.py`.

### PROVENANCE — five record classes, all of them (`design.md#component-overview`)
- [ ] **Per-change records**, one per edit, each citing its authorizing table row. The two asserted
      gates' records carry **`renamed_from:`** holding the d5 qualified name
      (`…::ViabilityCheck` → `…::net_power_viable`; `…::ReasonableParasiticTotal` →
      `…::parasitic_fraction_ok`).
- [ ] **Seven named deletion records** — A1, A4, A7, A8, C37 (derive-instead: each carries the
      undirected relation + the chosen-basis statement) and C21, C28 (citing the O2 ruling).
- [ ] **Three parked-row records** — A5, A6, A9. Field spec in `design.md#component-overview`: usage
      QN + d5 `file:line`; `blocked-by-defect` with its surfacing finding (**D-S2** for A5/A6, **D-S1**
      for A9) and the measured `SI_RENDERING_COLLISION` including the colliding entry point; **epic
      Item 8** as the fix and **Item 9** as the upgrade; the held intent (A5/A6's basis — axis root
      radius + 14 thicknesses free, all radii derived; A9's `assert-band` at 1% relative). Each states
      that its catalog row reads `excluded` / unassessed form exactly as in d5, and that **this record
      is the only place the disposition is visible**.
- [ ] **Two O3 model-debt entries** — A7's partial 2-of-4 shield closure; B4's mismatched thickness
      sets (guard sums four layers; the design's `thickness_total` is `0.4 [m]`).
- [ ] **Per-gate unit reasoning** for A2 and A3 (D3), naming what the human is on the hook for:
      **the operand pair as well as the tolerance dimension** (r2-2) — binding a non-power into
      `whole_power` would be admitted silently, and no toolchain check catches it.

### Validation
- [ ] Licensed elaboration of the committed fixture: 58 usage rows, 2 concrete entries, histogram
      `2/3/53` — equal to Phase 2's committed expectations, **with no edit to the expectations**.
- [ ] `test_no_expectation_file_is_stranded` and the ledger param are green again; full suite back at
      baseline plus the new rows.
- [ ] `git diff` shows no change to `catf_mfe_d5` or `catf_mfe_model` beyond Phase 0's paragraph;
      `make_d5_variant.py --check` still passes.

**What we know after this phase:** the ruled policy is authored, it generates, and it reproduces
pre-committed expectations without reverse-engineering.

---

## Phase 4 — The integrity check (D2): `65 = 58 + 7`, machine-checked

### Goal
Replace byte-reversal (which cannot transfer to a fixture that deliberately differs) with an
accounting-identity check that a script closes from committed artifacts alone.

### Assumption Under Test
**B4** — the ruled table's rows join 1:1 against the derivative's catalog plus PROVENANCE records,
**including across the two renamed carriers**. If false, SC-2's machine-checkable diff degrades to a
human diff review.

### Test stencil (write first)
```
def test_the_identity_closes():
    result = check_gated_manifest.run()
    assert result.carriers == 58 and result.deletions == 7
    assert result.matched_by_name == 56 and result.matched_by_renamed_from == 2

def test_an_unmatched_carrier_fails_closed():        # falsification, both directions
    # drop a renamed_from: → the carrier is unmatched → check fails
def test_a_renamed_from_claimed_by_a_deletion_fails():
    # point renamed_from: at a row a deletion record also claims → check fails
```

### Steps
- [ ] `scripts/check_gated_manifest.py --check` — joins the ruled table's rows, the population JSON,
      and the derivative's PROVENANCE by usage identity; consults `renamed_from:` before declaring an
      unmatched row. **License-free by construction.**
- [ ] Conformance test wrapping it, plus the two fail-closed cases above (run them once for real,
      then revert the mutation — a check nobody has seen fail is not yet a check).

### Validation
- [ ] `--check` closes `65 = 58 + 7`; 56 matched by name, 2 by `renamed_from:`; all 7 deletions cite
      an authorizing table row.
- [ ] Both fail-closed mutations were observed red, then reverted; recorded in `verification.md`.
- [ ] `ruff check src/` and `mypy src/` at baseline (12 / 55).

**What we know after this phase:** nothing in the derivative is unauthorized, and no usage vanished
silently — proved by a script, not by reading.

---

## Phase 5 — SC-8: the calc-def-only byte baseline (D7) — independent, may run any time after Phase 0

### Goal
Discharge Item 2's residual R3 with the tree's **first committed-bytes gate**, on
`constraint_domain_satisfy_calc_def`.

### Assumption Under Test
That a zero-entry, constraint-declaring package's shipped bytes are stable and worth pinning — and
that the new gate actually fails when the bytes move. Every existing byte gate in the tree compares
**two runs of the same route**; none compares a run against committed bytes.

### Test stencil (write first)
```
def test_the_zero_entry_package_ships_the_bytes_we_committed():
    out = generate_from_snapshot(FIXTURES/"constraint_domain_satisfy_calc_def"/"instance_graph_snapshot.json")
    assert (out/"schemas/constraint_types.py").read_bytes() == GOLDEN_A.read_bytes()
    assert (out/"modules/constraints/constraintreportaggregatormodule.py").read_bytes() == GOLDEN_B.read_bytes()
    assert "ConstraintEvaluation" in registry_text and "ConstraintReport" in registry_text
```

### Steps
- [ ] Capture the v6 snapshot for `constraint_domain_satisfy_calc_def` (it carries only `model.sysml`
      today). Single-fixture capture path; **not** the batch script, and not into its manifest.
- [ ] Commit the two-file golden — `schemas/constraint_types.py` and
      `modules/constraints/constraintreportaggregatormodule.py`. Two files deliberately: a whole-tree
      golden churns on every unrelated generator change and gets abandoned, which is how
      `tests/fixtures/baseline_yaml/` died.
- [ ] Add the regenerate-and-diff conformance test (license-free — the snapshot is committed).
- [ ] **Deliberate falsification, once, recorded:** flip the machinery bar
      (`resolution/models.py::ships_constraint_machinery`, which now keys on one *authored usage*,
      not one *concrete entry*), confirm the gate goes red, then revert. Record the red output in
      `verification.md`. A golden nobody has seen fail is not yet a gate.

### Validation
- [ ] Test green from the committed snapshot; goldens are generator-owned bytes and stay
      **format-exempt** (never `ruff format` them).
- [ ] Falsification observed red and reverted; tree clean afterwards.
- [ ] `test_v6_recapture_batch.py` still green (37 / 15 / 22 untouched).

**What we know after this phase:** R3 is closed by a real gate, and the gate has been seen to fail.

---

## Phase 6 — Acceptance: three routes and a real physics rejection (SC-5, SC-7)

### Goal
Prove the whole lane: generate → seal → execute → persist → query, through TEAx, with one valid
candidate satisfied and one unphysical mutation rejected.

### Assumption Under Test
**B3** — mutating `p_fusion` propagates through seven calc modules into `p_electric_net_out` and
crosses zero. **D6's mechanics are already measured** (M4, closed by the orchestrator probe
`probes/review_r2_inputs_key.py`, license-free): `p_fusion` surfaces as the mutable key
`CATFMFEPhysics__catf_physics__p_fusion: 2600.0` in `physics_params.json`.

### The mutation, stated exactly
- One generated package, **two input sets**, two TEAx runs. The mutation lives in the generated
  `inputs/*.json` — not in the model, not in a study-config override.
- **Mutate `CATFMFEPhysics__catf_physics__p_fusion` only.** `tritium_params.json` carries an
  independent `CATFMFETritium__catf_tritium__fusion_power: 2600.0` — a **separate modeled attribute,
  not a fan-out**. Leaving it alone is deliberate: an unphysical candidate is the point, and A2's
  gate hangs off the physics chain. Record this choice in `verification.md`.
- Drop `p_fusion` until `p_electric_net_out` goes negative. Check the projected chain offline on
  mutated inputs **before** the acceptance run (B3's mitigation).

### Steps
- [ ] Offline B3 check: mutated inputs drive `p_electric_net_out` negative. If not, fall back to A3's
      parasitic-contributor mutation (named in the ruled table) and record the fallback.
- [ ] **Route 1 — licensed live** (`--models`): generate, seal. Record module count, entry-point
      count, catalog counts, package fingerprint. Grep for license-skip lines → 0.
- [ ] **Route 2 — in-place snapshot** (`--from-snapshot` at the fixture): same, license-free.
- [ ] **Route 3 — relocated snapshot** (copy the snapshot elsewhere, generate from there): same.
- [ ] All three agree on the instance fingerprint and the projected graph. Record **exact** counts and
      fingerprints per route in `verification.md` — not a summary.
- [ ] Execute both candidates through TEAx (`/home/reid/1cfe/teax` @ `5b70ae9`, branch unchanged).
      Host in the agentic-mbse venv with a `sys.path` insert of `teax/packages/teax-simkit`; the teax
      `.venv` / `uv run` route is broken.
- [ ] **Valid candidate:** headline `full_satisfaction`, both gates satisfied, study default
      feed-strategy/penalize.
- [ ] **Mutated candidate:** A2 reports `violation`, the candidate reaches **`reject`**.
- [ ] **Both runs:** coverage lands in the durable case records; query them back and record the
      coverage fields.
- [ ] All observed outcomes equal Phase 2's committed expectations, with no edit to those expectations.

### Validation
- [ ] Licensed full suite green at baseline + the new rows; zero license-skip lines.
- [ ] `verification.md` carries: three route blocks with exact counts and fingerprints, both TEAx run
      outcomes, the durable-record coverage fields, the SC-6 commit hashes from Phase 2, Phase 1's
      reconciliation table, Phase 4's and Phase 5's falsification records, and the TEAx tip.

**What we know after this phase:** the epic's critical success factor is measured, not asserted.

---

## Phase 7 — Close-out

### Goal
Leave the item auditable.

### Steps
- [ ] `verification.md` complete against SC-1…SC-8, one section per criterion, numbers not prose.
- [ ] Re-check the two round-1 minors are still closed at HEAD (they were fixed in design rev 2):
      the whole-model BLOCK cite reads `elaborate.py:1145-1152`, and the `[unit]`-literal note is
      scoped rather than stated as a flat rule. Correct anything that drifted, in both `design.md`
      and `spec.md`.
- [ ] Backlog filings from the ruling are present: epic Item 8 (unit-lane defect), Item 9 (derivative
      upgrade), the divertor option (O5), the acausal-relations capability question, and the O3 debt note.
- [ ] `git diff --check` clean; ruff 12; mypy 55; licensed suite at baseline + new rows.
- [ ] Suggest `/_my_audit`.

**What we know after this phase:** every criterion has a recorded, re-runnable proof.

---

## Risk Management

**See `design.md#potential-risks` for the full table.** Phase-specific mitigations:

- **Phase 1 — B2 false (a new collision in the untested edits).** This is why Phase 1 exists and why
  it re-elaborates after every group: a late discovery costs the whole atomic pass. A collision here
  is a surface-and-stop, not a shim — the shim is exactly what D-S1/D-S2 refused.
- **Phase 2 — an expectation quietly transcribed from a dump.** Every entry cites the source
  file:line it was derived from; the `inapplicable_gate_count = 0` and `assessed_entry_count = 2`
  reasoning is written beside the number, not just the number.
- **Phase 3 — a malformed `@inapplicable:` typo halts generation at `error`.** Copy the exact form
  from the Item 2 fixtures, then re-elaborate.
- **Phase 3 — `renamed_from:` written wrong or omitted, so the identity passes vacuously.** Phase 4's
  two fail-closed mutations are run for real, then reverted.
- **Phase 5 — a golden that churns or that nobody has seen fail.** Two files only, and one deliberate
  falsification, recorded.
- **Phase 6 — the mutation crosses no gate.** Checked offline before the acceptance run; A3's
  parasitic mutation is the recorded fallback.
- **Cross-cutting — epic Item 8 lands mid-item and moves minted units.** Ruled out of scope here;
  this item's derivative is additive to whatever Item 8 lands.

---

## Implementation Notes

[TO BE FILLED DURING IMPLEMENTATION]

### Phase 0 Completion
**Completed:** · **Actual Changes:** · **Issues:** · **Deviations:**

### Phase 1 Completion
### Phase 2 Completion
### Phase 3 Completion
### Phase 4 Completion
### Phase 5 Completion
### Phase 6 Completion
### Phase 7 Completion

---

**Status:** Draft → In Progress → Complete
