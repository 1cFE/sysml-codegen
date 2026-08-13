# Implementation Plan: CATF Derivative and End-to-End Acceptance

**Status:** Complete
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
- [x] Licensed full suite; record passed/skipped and **grep the output for `no live syside license`
      → expect 0 lines**. Record the count in `verification.md` (create it).
- [x] `ruff check src/` and `mypy src/` → record counts (expect 12 / 55).
- [x] `git -C /home/reid/1cfe/teax rev-parse HEAD` and `--abbrev-ref HEAD` → record; expect
      `5b70ae9` on `constraint-semantics-item3`. If it differs, **stop and surface** — acceptance
      evidence cites that tip.
- [x] Correct the stale acceptance paragraph in `tests/fixtures/catf_mfe_d5/PROVENANCE.md` (it still
      claims the exact route refuses the model with 152× `SI_OCCURRENCE_MISSING`; the model has built
      42 modules since). Nothing else in that fixture changes.
- [x] `python scripts/make_d5_variant.py --check` → passes for all three variants.
- [x] `git diff --stat tests/fixtures/catf_mfe_d5/` → exactly one file, exactly the paragraph.

### Validation
- [x] Full suite green at the recorded baseline; `git diff --check` clean.

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
- [x] Reproduce P7's composite first, unchanged, and confirm it still admits (48 modules, 2 gates,
      65 rows). A drift here means something moved under the design and everything after it is suspect.
- [x] Add the remaining edits **group by group, re-elaborating after each group**. Record each
      group's outcome. A BLOCK or collision names the group that caused it — that is the whole
      reason for the grouping.
- [x] Author the five `@inapplicable:` markers **by copy from the Item 2 fixtures that pin the exact
      form** (`tests/fixtures/constraint_domain_inapplicable/`). A malformed directive halts
      generation at `error` even on a plain usage.
- [x] Drive any rewrite off the **chain name** carried by `block_feature_chain`, never off
      `file:line` — every entry of a multi-chain block renders the same location (Item 4 limit 2).
- [x] Author **no bare self-named binding**. If one becomes unavoidable, **surface and stop**: the
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

- [x] The probe's measured counts equal the reconciliation table's. **Any mismatch stops the phase**
      — triage as fixture-wrong / reconciliation-wrong / B2-false, and surface the third.

### Validation
- [x] Probe ADMITs with 58 usage rows, 2 concrete entries, histogram as above.
- [x] Nothing under `tests/` or `src/` changed; `/tmp/item5probe/*` is throwaway.
- [x] Reconciliation table committed to `verification.md`.

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
- [x] **`tests/expectations/constraint_population/catf_mfe_gated.json`** — the 58 carrier identities
      (`usage_qualified_name`, `source_file`, `source_line`), derived from d5's 65-row expectation
      minus the 7 deletions, with the two renamed gates carrying their **new** names
      (`…::net_power_viable`, `…::parasitic_fraction_ok`) and their new lines.
- [x] **`tests/unit/data/expected-coverage.md`** — one new prose entry plus one line in the
      ```` ```ledger ```` block, in the existing field order:
      `catf_mfe_gated | 58 | 2 | 2 | 0 | 0 | {} | complete | full_satisfaction | 2`
      The prose entry cites the file and line of every usage it counted and states the
      `inapplicable_gate_count = 0` reasoning explicitly (below).
- [x] **Expected catalog disposition histogram** — `2 eligible / 3 excluded / 53 non_reaching`, with
      the three `excluded` rows named (A5, A6, A9) and stated to be indistinguishable from any other
      plain usage in the catalog.
- [x] **D2's expected identity** — `65 = 58 carriers + 7 named deletions`, with the 7 deletions named
      (A1, A4, A7, A8, C37, C21, C28) and the 2 `renamed_from:` carriers named. Store it as a
      committed data file the script reads (not inline in `check_gated_manifest.py`) so the
      commit-order evidence is content-scoped and unambiguous.
- [x] **Expected report / study outcomes** — valid candidate: headline `full_satisfaction`, both
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
- [x] **New files** (`catf_mfe_gated.json`, the identity data file):
      `git log --diff-filter=A --format=%H -- <path>`
- [x] **Edits to existing files** (the `expected-coverage.md` ledger row — `--diff-filter=A` returns
      Item 3's file-creation commit, which is the wrong answer):
      `git log -S'catf_mfe_gated' --format=%H -- tests/unit/data/expected-coverage.md`
- [x] Both must return commits that **precede** `git log --diff-filter=A --format=%H --
      tests/fixtures/catf_mfe_gated/`. Record all hashes in `verification.md`.
- [x] Do **not** cite the reader tests' dates — they existed at HEAD, so their ordering proves nothing.

### Validation
- [x] `git show --stat HEAD` — the commit touches expectations only, no fixture bytes.
- [x] Suite is red on exactly the two named tests (the deliberate window). Record both names and the
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
- [x] Fork `catf_mfe_d5` → `tests/fixtures/catf_mfe_gated/` (**this commit closes the red window**;
      land it immediately after Phase 2's commit).
- [x] Apply the edits **in Phase 1's proven group order, re-elaborating after each group**:
      library (`library/constraints/gate_forms.sysml`, package `CATFGateForms`:
      `PositiveQuantity`, `FractionWithinBand` — **no `ProductWithinBand`**, its only consumer is
      parked) → A2 → A3 → A7/A8 derivations → A1/C37 derivation → the A4/C21/C28 deletions →
      the five `@inapplicable:` markers. A5, A6, A9 are left exactly as d5 wrote them.
- [x] Each of the 7 derivations carries a **doc comment recording the undirected relation and stating
      that the direction is a chosen basis, not physics** (owner's structural amendment).
- [x] No `[unit]` literal in either surviving gate's predicate body (D3 — both are dimensionless-safe;
      the §8 both-operands spelling stays the supported unit-carrying form, these two just don't use it).
- [x] Capture the fixture's v6 snapshot (`instance_graph_snapshot.json`) through the shipped capture
      path. **Not** via `capture_v6_batch.py`.

### PROVENANCE — five record classes, all of them (`design.md#component-overview`)
- [x] **Per-change records**, one per edit, each citing its authorizing table row. The two asserted
      gates' records carry **`renamed_from:`** holding the d5 qualified name
      (`…::ViabilityCheck` → `…::net_power_viable`; `…::ReasonableParasiticTotal` →
      `…::parasitic_fraction_ok`).
- [x] **Seven named deletion records** — A1, A4, A7, A8, C37 (derive-instead: each carries the
      undirected relation + the chosen-basis statement) and C21, C28 (citing the O2 ruling).
- [x] **Three parked-row records** — A5, A6, A9. Field spec in `design.md#component-overview`: usage
      QN + d5 `file:line`; `blocked-by-defect` with its surfacing finding (**D-S2** for A5/A6, **D-S1**
      for A9) and the measured `SI_RENDERING_COLLISION` including the colliding entry point; **epic
      Item 8** as the fix and **Item 9** as the upgrade; the held intent (A5/A6's basis — axis root
      radius + 14 thicknesses free, all radii derived; A9's `assert-band` at 1% relative). Each states
      that its catalog row reads `excluded` / unassessed form exactly as in d5, and that **this record
      is the only place the disposition is visible**.
- [x] **Two O3 model-debt entries** — A7's partial 2-of-4 shield closure; B4's mismatched thickness
      sets (guard sums four layers; the design's `thickness_total` is `0.4 [m]`).
- [x] **Per-gate unit reasoning** for A2 and A3 (D3), naming what the human is on the hook for:
      **the operand pair as well as the tolerance dimension** (r2-2) — binding a non-power into
      `whole_power` would be admitted silently, and no toolchain check catches it.

### Validation
- [x] Licensed elaboration of the committed fixture: 58 usage rows, 2 concrete entries, histogram
      `2/3/53` — equal to Phase 2's committed expectations, **with no edit to the expectations**.
- [x] `test_no_expectation_file_is_stranded` and the ledger param are green again; full suite back at
      baseline plus the new rows.
- [x] `git diff` shows no change to `catf_mfe_d5` or `catf_mfe_model` beyond Phase 0's paragraph;
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
- [x] `scripts/check_gated_manifest.py --check` — joins the ruled table's rows, the population JSON,
      and the derivative's PROVENANCE by usage identity; consults `renamed_from:` before declaring an
      unmatched row. **License-free by construction.**
- [x] Conformance test wrapping it, plus the two fail-closed cases above (run them once for real,
      then revert the mutation — a check nobody has seen fail is not yet a check).

### Validation
- [x] `--check` closes `65 = 58 + 7`; 56 matched by name, 2 by `renamed_from:`; all 7 deletions cite
      an authorizing table row.
- [x] Both fail-closed mutations were observed red, then reverted; recorded in `verification.md`.
- [x] `ruff check src/` and `mypy src/` at baseline (12 / 55).

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
- [x] Capture the v6 snapshot for `constraint_domain_satisfy_calc_def` (it carries only `model.sysml`
      today). Single-fixture capture path; **not** the batch script, and not into its manifest.
- [x] Commit the two-file golden — `schemas/constraint_types.py` and
      `modules/constraints/constraintreportaggregatormodule.py`. Two files deliberately: a whole-tree
      golden churns on every unrelated generator change and gets abandoned, which is how
      `tests/fixtures/baseline_yaml/` died.
- [x] Add the regenerate-and-diff conformance test (license-free — the snapshot is committed).
- [x] **Deliberate falsification, once, recorded:** flip the machinery bar
      (`resolution/models.py::ships_constraint_machinery`, which now keys on one *authored usage*,
      not one *concrete entry*), confirm the gate goes red, then revert. Record the red output in
      `verification.md`. A golden nobody has seen fail is not yet a gate.

### Validation
- [x] Test green from the committed snapshot; goldens are generator-owned bytes and stay
      **format-exempt** (never `ruff format` them).
- [x] Falsification observed red and reverted; tree clean afterwards.
- [x] `test_v6_recapture_batch.py` still green (37 / 15 / 22 untouched).

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
- [x] Offline B3 check: mutated inputs drive `p_electric_net_out` negative. If not, fall back to A3's
      parasitic-contributor mutation (named in the ruled table) and record the fallback.
- [x] **Route 1 — licensed live** (`--models`): generate, seal. Record module count, entry-point
      count, catalog counts, package fingerprint. Grep for license-skip lines → 0.
- [x] **Route 2 — in-place snapshot** (`--from-snapshot` at the fixture): same, license-free.
- [x] **Route 3 — relocated snapshot** (copy the snapshot elsewhere, generate from there): same.
- [x] All three agree on the instance fingerprint and the projected graph. Record **exact** counts and
      fingerprints per route in `verification.md` — not a summary.
- [x] Execute both candidates through TEAx (`/home/reid/1cfe/teax` @ `5b70ae9`, branch unchanged).
      Host in the agentic-mbse venv with a `sys.path` insert of `teax/packages/teax-simkit`; the teax
      `.venv` / `uv run` route is broken.
- [x] **Valid candidate:** headline `full_satisfaction`, both gates satisfied, study default
      feed-strategy/penalize.
- [x] **Mutated candidate:** A2 reports `violation`, the candidate reaches **`reject`**.
- [x] **Both runs:** coverage lands in the durable case records; query them back and record the
      coverage fields.
- [x] All observed outcomes equal Phase 2's committed expectations, with no edit to those expectations.

### Validation
- [x] Licensed full suite green at baseline + the new rows; zero license-skip lines.
- [x] `verification.md` carries: three route blocks with exact counts and fingerprints, both TEAx run
      outcomes, the durable-record coverage fields, the SC-6 commit hashes from Phase 2, Phase 1's
      reconciliation table, Phase 4's and Phase 5's falsification records, and the TEAx tip.

**What we know after this phase:** the epic's critical success factor is measured, not asserted.

---

## Phase 7 — Close-out

### Goal
Leave the item auditable.

### Steps
- [x] `verification.md` complete against SC-1…SC-8, one section per criterion, numbers not prose.
- [x] Re-check the two round-1 minors are still closed at HEAD (they were fixed in design rev 2):
      the whole-model BLOCK cite reads `elaborate.py:1145-1152`, and the `[unit]`-literal note is
      scoped rather than stated as a flat rule. Correct anything that drifted, in both `design.md`
      and `spec.md`.
- [x] Backlog filings from the ruling are present: epic Item 8 (unit-lane defect), Item 9 (derivative
      upgrade), the divertor option (O5), the acausal-relations capability question, and the O3 debt note.
- [x] `git diff --check` clean; ruff 12; mypy 55; licensed suite at baseline + new rows.
- [x] Suggest `/_my_audit`.

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

**Completed:** 2026-08-13. Full numbers in `verification.md` §Phase 0.

**Changes made:**
- `tests/fixtures/catf_mfe_d5/PROVENANCE.md` — the stale acceptance paragraph replaced with
  the measured state (43 modules, 65 usages / 0 concrete / 9 excluded / 56 non-reaching), and
  the superseded "What blocks it — 152× `SI_OCCURRENCE_MISSING`" section shrunk to a one-line
  closed record pointing at git history (capture-fidelity §3: amend, don't accrete). Only file
  touched in either frozen twin.
- `verification.md` created.

**What we now know:** the licensed environment really licenses (0 skip lines on both runs),
lint/type floors hold exactly (ruff 12, mypy 55), the TEAx tip is `5b70ae9` on
`constraint-semantics-item3`, and the frozen-twin obligation is discharged and still checkable
(all three `make_d5_variant.py --check` pairs pass).

**Issues / deviations — two count surprises, both recorded rather than absorbed:**

1. **Suite baseline does not equal the inherited 2050/34.** Measured at this HEAD:
   **2012 passed / 34 skipped / 79 deselected** under the default marker set
   (`pyproject.toml:46` sets `-m "not execution"`), and **2090 passed / 34 skipped / 1 failed**
   under `-m ""`. Skipped is 34 in both, matching exactly, and no previously-passing test
   fails — 2050 sits between the two numbers, so the gap is the marker set plus Item 4's
   added tests. No test was lost. The floor for the rest of the item is the measured HEAD
   baseline, stated in `verification.md`. Surfaced to the orchestrator.
2. **The one failing test is environmental.**
   `tests/execution/test_fusion_tea_real_teax.py::test_the_lane_runs_the_real_simkit` refuses
   because the in-repo stub runner is importable in the task venv; that lane must be hosted in
   the agentic-mbse venv with a `sys.path` insert of `teax/packages/teax-simkit`. Pre-existing,
   not caused by any Item 5 edit.
3. **d5 builds 43 modules, not the 42 the plan's prose says.** 43 is the number consistent with
   every design probe delta (P1 44, P2 45, P6 46, P7 48). No expectation derives from it; the
   corrected paragraph records 43.

### Phase 1 Completion

**Completed:** 2026-08-13. Full ladder, counts, and reconciliation table in
`verification.md` §Phase 1.

**Changes made (all throwaway, nothing under `tests/` or `src/`):**
- `probes/edits3.py` — the edits P7 never tested: the ruled library (no `ProductWithinBand`),
  the A1/C37 group, the A4/C21/C28 deletions, the A7/A8 usage deletions, the five
  `@inapplicable:` markers, the axis-leg reversal.
- `probes/apply3.py`, `probes/check_markers.py` — group runner and a marker-carriage probe.
- Scratch copy at `/tmp/item5probe/p8`; both frozen twins untouched.

**Result — B2 holds.** The ruled shape generates: **ADMIT, 47 modules, 58 usage rows, 2
concrete entries, `{eligible: 2, excluded: 3, non_reaching: 53}`** — equal to the
reconciliation table derived from the ruled table, row for row. No new
`SI_RENDERING_COLLISION`, no `SI_CONSTRAINT_BLOCKED`, no readiness refusal at any of the six
re-elaborations. No bare self-named binding was needed or authored.

**Issues / deviations:**

1. **The plan's group list undercounted `derive-instead` by two edits.** It treated "A7, A8
   derivations" as the whole of those rows; `derive-instead` also deletes the authored usage
   the derivation replaces. Measured: after groups 3 and 4 the probe sat at **60** rows, not
   58. Added as group 4b (the A7 and A8 usage deletions), which lands it at exactly 58 and the
   histogram at exactly 2/3/53. The ruled table is not wrong — its identity names all five
   derive-instead rows, and the arithmetic only closes if all five usages go.
2. **Module count is 47, not P7's 48.** The axis-leg reversal returns
   `axis_region.outer_radius` to a literal and un-mints its module. Expected.
3. **Derivation basis statements are `//` comments, not `doc` bodies.** The owner's structural
   amendment asks for a doc comment recording the undirected relation and the chosen-basis
   statement. An attribute with an initializer would need a trailing `{ doc /* … */ }` body to
   carry a real doc, which risks perturbing an atomic landing for no gain — and SysIDE's
   handling of doc bodies in this position is the very thing finding 4 below shows to be
   unreliable. The relation and the chosen-basis statement are carried verbatim in source
   comments beside each derivation and repeated in PROVENANCE, which is where the ruling puts
   the durable record. Flagged for the owner.

**FINDING (surfaced, not resolved) — the five `@inapplicable:` markers cannot reach the
domain on B1–B5's shape.** Measured: **5 written in source, 0 carried on the domain**, with
the markers in the exact form and first-line placement the Item 2 fixtures pin. B1–B5 are
inline-predicate constraints, and SysIDE drops a `doc` comment inside an inline-predicate
constraint body — rule 3 of `test_constraint_population_oracle.py`, written down to make
exactly this gap loud. Every Item 2 fixture that carries a working marker is bindings-form.

Consequence: authoring the markers as the ruled table calls for turns
`test_every_authored_inapplicable_marker_reached_the_domain[catf_mfe_gated]` red. **No
committed number changes either way** — `inapplicable_gate_count` is 0 regardless (bucket row
1 decides before the inapplicable predicate is consulted), and the measured histogram is
identical with and without the markers. Phase 2's expectations are unaffected.

**Phase 2 is not started.** The finding touches an owner-ruled disposition (Group B: "an
explicit `@inapplicable:` disposition"), so it is surfaced rather than absorbed.

### Phase 2 Completion

**Completed:** 2026-08-13, commit **`1247a3b`**. Numbers in `verification.md` §Phase 2.

**Changes:** `tests/expectations/constraint_population/catf_mfe_gated.json` (58 carriers),
`tests/expectations/gated_manifest/catf_mfe_gated.json` (the identity `65 = 58 + 7`, its 7
deletions with authorizing rows, both `renamed_from:` carriers, the 2/3/53 histogram, expected
study outcomes), and one ledger row plus its prose entry in `tests/unit/data/expected-coverage.md`.

**Derivation, not transcription.** Built as `d5's 65 − the 7 deletions + the 2 renames`, then
cross-checked against a source scan: `derivation and source agree on all 58 identities`. The
scan supplies line numbers and checks membership; it does not supply it (PD2/DR-6).

**Red window opened as designed.** Suite red on exactly the two named tests and nothing else.

**Deviations:** none.

### Phase 3 Completion

**Completed:** 2026-08-13, commit **`7369b3e`** — this closes the red window.

**Result:** 47 modules, 58 usage rows, 2 concrete entries, `{eligible 2, excluded 3,
non_reaching 53}`. Coverage read back from the committed snapshot is
`58 / 2 / 2 / 0 / 0 / {} / complete`, equal to the pre-committed ledger row **with no edit to
the expectations**. Source scan vs committed expectation: MATCH, 58 = 58. Every intermediate
group ADMITs (ladder in `verification.md`). Frozen twins clean.

**SC-6 proved:** all three expectation artifacts at `1247a3b`, fixture at `7369b3e`, parent to
child.

**Deviations:**
1. **Derivation basis statements are `//` comments, not `doc` bodies** — orchestrator-confirmed
   2026-08-13. Verbatim relation + chosen-basis statements are carried in source and repeated
   in PROVENANCE, as required.
2. **B1–B5 carry no `@inapplicable:` marker**, per the ruling recorded at `99700ac`.

### Phase 4 Completion

**Completed:** 2026-08-13, commit **`0d9f474`**.

`check_gated_manifest.py --check` closes `65 = 58 + 7`, 56 matched by name and 2 by
`renamed_from:`, license-free. Conformance test plus **three** falsifications run for real
(the plan asked for two; a deletion record with no authorizing row was added as the other
direction an unauthorized change could slip through). Outputs recorded in `verification.md`.

**Deviation:** the falsifications rewrite a **temp copy** of PROVENANCE and monkeypatch the
module's path, rather than mutating the committed fixture and reverting. Same proof, and a
mutation of a committed artifact is one interrupted run away from corrupting the tree.

### Phase 5 Completion

**Completed:** 2026-08-13, commit **`1a7328c`**.

Committed v6 snapshot for `constraint_domain_satisfy_calc_def` (shape confirmed: `usage_records`
2, `concrete_entries` 0), a two-file golden, and a license-free regenerate-and-diff test. The
tree's first committed-bytes gate. Falsification run and reverted: flipping the machinery bar
back to Item 2's concrete-entry rule stops `schemas/constraint_types.py` being emitted at all
and strips both registry imports.

**Recorded honestly:** only **one** of the two pinned files moves under that flip — the
aggregator is still emitted, so its golden stays green. The gate is real; the two files are not
equally sensitive to that particular bar.

`test_v6_recapture_batch` still green; the 37-record manifest is untouched.

### Phase 6 Completion — **STOPPED at the acceptance run**

**Three routes: done.** Exact counts and fingerprints in `verification.md` §Phase 6. Routes 2
and 3 are byte-identical; the projected graph is identical on all three
(47 / 58 / 2 / `{2,3,53}`, coverage `58/2/2/0/0/{}/complete`, 9 groups / 65 entry points).

**Three findings recorded, two resolved inside authority:**

- **6-A — the catalog fingerprint is not portable across routes.** Live and snapshot bake
  different `CATALOG_FINGERPRINT`s because the fingerprint hashes `usage_records`, whose
  `source_file` paths are route-relative (`resolution/models.py:597-622`). **Pre-existing** —
  reproduces on the untouched `catf_mfe_d5`, and does not reproduce on a flat single-file
  fixture. Contradicts the plan's "all three agree on the instance fingerprint"; not against a
  ruled row, not caused by this item. Recorded, not fixed.
- **6-B — `value` is a reserved generated local, so the ruled A2 spelling cannot generate.**
  Generation's name-safety preflight refused what elaboration admitted
  (`generated_binding_overlap`). Resolved by renaming the formal `value` → `quantity`, which
  **O7** authorises (library names provisional, design-owned) and which the spec already
  blesses as a local edit. Nothing ruled moved; the committed expectation still matches.
  **This exposes a real gap in Phase 1:** the de-risk probe only elaborated, never generated,
  so the five generation preflights were untested at the gate meant to be the cheap place to
  find exactly this.
- **6-C — D6's mutation route does not exist.** Editing a sealed `inputs/*.json` breaks the
  package contract, and the refusal is pinned in code. Took TEAx's typed entry injection
  (`CandidateBridge` + `PreparedEvaluator`), the route Item 3's mutation lane already uses.
  D6's intent — one package, two input sets, mutation as a physics input value — is preserved.

**6-D — the STOP.** The lane works end to end and both gates report. What is false is the
direction the ruled SC-5 row assumes: **at the authored inputs, both gates report `violated`**.
The magnet cryoplant draws 8396 MW against 1547 MW gross, so net power is negative at the
authored design point.

Ownership is the model, not the derivative — `catf_mfe_d5` produces the identical
`cooling_power = 8396.054399837172`. Chased to a probable unit error:
`heat_leak = magnet_volume * 0.05  // MW` implies ~38 MW of static heat leak into a 4.5 K
system, three to six orders of magnitude high.

Both directions are demonstrated (`p_fusion = 20000` → both gates `satisfied`), so only the
labelling of "valid candidate" is open — and that is a modeling decision, as is the heat-leak
coefficient. Parked for a ruling rather than resolved. The coverage account is unaffected at
every probed point; the one wrong cell in the committed expectations is the **headline**.

### Phase 6 Completion (continued) — closed under the 6-D ruling

**Completed:** 2026-08-13, commits **`e01c3b4`** (the standalone 6-D amendment), **`609c777`**
(acceptance evidence), **`2872ca6`** (backlog filings).

**The ruling, applied.** Candidates are labeled **gate-feasible / gate-infeasible under the
model as authored**. The authored CATF design point is the **rejected** candidate; the
raised-`p_fusion` candidate carries the satisfied path as a **machinery exemplar, not a
recommended design**, and is recorded that way in every artifact that mentions it.

**SC-5 met**, full route, both candidates, verdict **and** coverage persisted on each:

| | gate-infeasible (authored) | gate-feasible (exemplar) |
|---|---|---|
| A2 / A3 | `violated` / `violated` | `satisfied` / `satisfied` |
| report headline | `violation` | `full_satisfaction` |
| policy disposition | **`reject`** | `feed-strategy` |
| coverage on the record | `58/2/2/0/0/{}/complete` | *identical* |

**The amendment's basis is a source-derived computation**, per the ruling — `cryo_derivation.py`
re-derives `cooling_power` from model source and asserts it reproduces the executed value
bit-exactly. Doing that **corrected my own STOP-report figures**: the model runs at **20 K**, not
the 4.5 K I had assumed, so the amplification is **50×** and the cryogenic load **167.92 MW**, of
which `heat_leak` is **116.72 MW** (69.5%).

**Deviation:** the coverage *numbers* were never wrong and were not touched. One cell moved —
the headline — in a commit that names the finding.

### Phase 7 Completion

**Completed:** 2026-08-13, this commit.

**`verification.md` is complete against SC-1 … SC-8**, one section per criterion, numbers not
prose. All eight are **MET**.

**Round-1 minors re-checked at HEAD:** the whole-model BLOCK cite reads `elaborate.py:1145-1152`
in both `spec.md:209` and `design.md:141`, and line 1145 is in fact the `Eligibility.BLOCK`
branch; the `[unit]`-literal note at `design.md:492-495` is scoped rather than stated as a flat
rule. Neither drifted; nothing to correct.

**Backlog filings all present:** epic Item 8, epic Item 9 (plus the B1–B5 marker retirement),
the divertor option (O5), the acausal-relations capability question, the O3 model-debt note, and
this item's three new filings — `[INLINE-PREDICATE-MARKER-DROP]`, `[CATF-CRYO-HEAT-LEAK-COEFFICIENT]`, and
`[CATALOG-FINGERPRINT-ROUTE-PORTABILITY]`.

**Final gates:** licensed full suite **2103 passed / 34 skipped**, **zero** `no live syside
license` lines; `ruff check src/` **12**; `mypy src/` **55**; `git diff --check` clean. The one
failure is `test_the_lane_runs_the_real_simkit`, pre-existing and quoted verbatim from
`CURRENT_WORK.md:468-472` in `verification.md`, ruled out of this item's floor.

**The Phase-1 gap is recorded** in `verification.md` and carried into the epic's Lessons
Learned: the de-risk probe elaborated but never generated, so the five generation preflights
went untested at the gate built to catch exactly that class of refusal.

**Next:** `/_my_audit`.

---

**Status:** Complete (2026-08-13)
