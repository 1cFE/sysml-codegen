# Implementation Plan: Derivative Upgrade Under Held Intent (CONSTRAINT-SEMANTICS Item 9)

**Status:** Draft
**Created:** 2026-08-13
**Last Updated:** 2026-08-13
**Branch:** `item7-rebuild`

## Source Documents

- **Spec:** `.project/active/derivative-upgrade-held-intent/spec.md`
- **Design:** `.project/active/derivative-upgrade-held-intent/design.md` ← component detail,
  decisions D1–D7, the concrete derivation shape, A9's authored form, the full PROVENANCE edit
  list, and the SC-6 expectation table. This plan sequences that material; it does not restate it.
- **Ruled table:** `.project/completed/20260813_catf-constraint-policy-acceptance/owner-disposition.md`
  (archive is frozen — read only)
- **Probe evidence:** `probes/RESULTS.md` beside this file

---

## The Point

`tests/fixtures/catf_mfe_gated` is the worked example of the ruled constraint policy — the artifact
someone opens to see what the policy actually produces. Three of its rows are not the shape the
owner ruled. They are the shape a defect allowed: Item 5 measured that A9's assert-band and 26 of
the 27 A5/A6 radius derivations refused with `SI_RENDERING_COLLISION`, so those rows landed as plain
usages marked `blocked-by-defect` with their ruled forms held as recorded intent.

Item 8 cured the defect at `62a07e5`. So today the fixture asserts by constraint what the ruled
basis says it should compute, checks two independently authored numbers with `==` when they already
disagree by 0.16 m³/s, and carries `blocked-by-defect` markings whose cause is gone.

The obligation is to make the worked example true again **without re-deciding anything**. Every
target form is already ruled. This item executes held intent and restates the arithmetic that
follows: `65 = 56 carriers + 9 named deletions`. A ruled form that cannot be built is a surfacing
event for the owner, never a licence to pick a different form.

That ladders to the epic's contract: the catalog's dispositions only mean something if the reference
fixture is the policy rather than an accident of tooling.

---

## Implementation Strategy

**Phasing rationale.** Two hard orderings drive everything.

1. **The unproven lane goes first.** The design probe drove `generate --models`. It never ran
   `snapshot` + `generate --from-snapshot`, and Item 8 routed projectability certification through
   `snapshot/envelope.py`, so a lane disagreement would surface there as `SnapshotCertifiabilityError`.
   Phase 1 edits the sources and immediately proves capture and re-seal. A refusal there is cheap;
   a refusal after five committed expectation documents is not.
2. **SC-6: expectations before the confirmation run.** The commit order is the evidence. Sources are
   not expectations, and the population expectation needs A9's new `source_line`, which is a property
   of authored source. So the order is: edit sources → read line numbers **from source** → write and
   commit every expectation → only then run anything that could confirm them.

The prover extension follows the expectations because it is mechanism, not an expectation, and
because nothing can pass `--check` until both the expectations and the extension are in.

**Critical path.**

```
sources + snapshot capture proof  →  read source line numbers  →  commit ALL expectations
        (Phase 1, commit C1)                                          (Phase 2, commit C2)
   →  prover per-occurrence anchoring + falsification cases  →  first confirmation run
                                 (Phase 3, commit C3)
   →  BACKLOG both-sides records  →  full gates + verification.md
          (Phase 4, commit C4)          (Phase 5, commit C5)
```

**First proof point.** `sysml-codegen snapshot` over the edited fixture completes and the resulting
v6 envelope loads and projects. That single command collapses the largest remaining uncertainty in
the item.

**Overall validation approach.** Each phase has an automated check that can fail. No phase's
verification is "it looks right." The final phase records exact counts in `verification.md` rather
than adjectives.

---

## Environment (every phase)

**See CLAUDE.md.** Two rules are non-negotiable here and both come from the spec:

```bash
set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a     # license
/home/reid/1cfe/item7-rebuild-venv/bin/python -m pytest ...   # NOT uv run
```

`uv run` resolves `agentic_mbse` to the main checkout and is wrong for this worktree pair. A run
with license-skip lines is not a licensed proof.

**Known pre-existing failure, not this item's:**
`tests/execution/...::test_the_lane_runs_the_real_simkit` fails on whole-set runs and passes in
isolation (collection-order artifact, unowned). Do not chase it. Record it in `verification.md` if
hit.

**Do not touch:** `tests/fixtures/catf_mfe_model/`, `tests/fixtures/catf_mfe_d5/`,
`.project/completed/20260813_catf-constraint-policy-acceptance/`. Keep the concurrent agent's files
(`CURRENT_WORK.md`, `CHANGELOG.md`, calcdef-design archive moves) out of every commit.

---

## Phase 1 — Source edits, then prove snapshot capture and re-seal

### Goal

Author the three source files exactly as the design fixes them, and prove the one lane the probe did
not exercise: v6 capture + re-seal + license-free projection off the captured envelope.

### Assumption Under Test

Design bet **B3** — annotating the two under-labelled declarations (D2, D3) is sufficient to make
every lane agree. Confirmed for generation; **unconfirmed for snapshot certification**. This phase
either confirms it or produces a `SnapshotCertifiabilityError` while the cost of stopping is one
reverted working tree.

### Test Stencil (write/run this first, before the expectations exist)

```bash
# Phase 1 proof — runs before any expectation is written.
set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a
V=/home/reid/1cfe/item7-rebuild-venv/bin
$V/sysml-codegen snapshot --models tests/fixtures/catf_mfe_gated \
    --output /tmp/item9_probe/snap.json                      # must not refuse
$V/sysml-codegen generate --from-snapshot /tmp/item9_probe/snap.json \
    --output /tmp/item9_probe/pkg --package-name item9_probe # must seal
# record: module count, stencil count, parameter-group count, preflight outcomes
```

### Changes Required

**See `design.md` for the authored text:** the 27 derivations' concrete shape (`design.md#the-27-derivations--concrete-shape`),
A9's definition and usage (`design.md#a9s-authored-form`), and decisions D1–D7.

- [x] `tests/fixtures/catf_mfe_gated/designs/catf_mfe/radial_build.sysml` — delete
      `LayerContinuity` (A5) and `RadiusThicknessConsistency` (A6); author 27 derivations in place,
      in authored order, in the same declaration slots (D6); one full basis paragraph at the
      `catf_radial_build` level; each derivation carries its two statements in a `//` block within
      the 12-line comment window (D4); unit in a trailing `//` comment (D1); bare sibling spelling
      (D7).
- [x] Same file — **D3**, the one edit outside the 27: `tf_coil.thickness`'s trailing comment
      becomes `// m - from line 83 (= tf_dr)`. Original provenance text preserved inside it.
- [x] `tests/fixtures/catf_mfe_gated/library/constraints/gate_forms.sysml` — add
      `ProductWithinBand` with all four formals unit-annotated (D2).
- [x] `tests/fixtures/catf_mfe_gated/designs/catf_mfe/vacuum.sysml` — replace
      `PumpingSpeedConsistency` in place with `assert constraint pumping_speed_agrees :
      ProductWithinBand { … rel_tol = 0.01; }`; add
      `private import CATFGateForms::ProductWithinBand;`.
- [x] `tests/fixtures/catf_mfe_gated/instance_graph_snapshot.json` — re-capture in place from the
      edited sources.

`probes/apply_item9_edits.py` already performs a version of these edits against a throwaway copy.
Reuse it as a reference for the exact text; do not run it blind against the live fixture.

### Validation

**Automated:**
- [x] `snapshot` completes without refusal → envelope written
- [x] `generate --from-snapshot` seals the package
- [x] `generate --models tests/fixtures/catf_mfe_gated` also seals (re-confirm the probe's lane)
- [x] All five preflights pass on both routes

**Manual:**
- [x] Record the **measured** module/stencil/parameter-group counts. The probe saw 62 modules —
      re-measure, do not copy it (`design.md#next-stage-handoff`).
- [x] Confirm the expected registry alias warning for the 15 `outer_radiusModule` collisions
      appears and is **not** "fixed" (`design.md#implementation-notes`).
- [x] Diff the re-captured snapshot against the committed one and note whether anything beyond
      `captured_at` moved. Anything else is a finding, not churn.
- [x] Record the before/after public key movement and check it against the derived **26 leave /
      16 arrive** sets (`design.md#expected-output-derivation-plan-sc-6`). A key moving that is not
      in those sets is a surfacing event.

**What we know works after this phase:** the ruled forms build, certify through the snapshot
envelope, and generate from it license-free. Every remaining phase is bookkeeping over a proven
model.

### Commit point C1

Sources + re-captured snapshot. Commit message must say the snapshot is a **capture, not an
expectation** (`design.md#expected-output-derivation-plan-sc-6`, row 7 note), so a later auditor
reading the commit order does not mistake it for a run feeding an expectation. No expectation
document is in this commit.

### Rollback (fixture edits)

Everything here is reversible by Git and nothing outside the working tree is written.

- Before C1: `git checkout -- tests/fixtures/catf_mfe_gated/` restores the fixture whole.
- After C1: `git revert <C1>` — the snapshot rides in the same commit, so sources and capture revert
  together and cannot desynchronize.
- If Phase 1 refuses: **stop and surface**. A ruled form that will not build is an owner surfacing
  event (spec Non-Goals). Do not adapt the form, and do not proceed to Phase 2 — no expectation
  should exist for a model that does not certify.

---

## Phase 2 — Derive and commit every expectation (SC-6)

### Goal

Write all five committed expectation documents from the ruled table and from authored source, and
commit them **before** anything confirms them.

### Assumption Under Test

Design bet **B2** — the three upgraded rows are the only catalog rows that move, so the restated
identity `65 = 56 + 9` and every number under it is right. This phase writes those numbers down
where a later run can falsify them.

### Test Stencil (this phase writes expectations; it runs nothing that confirms them)

```
# The only reads permitted in this phase:
#   - the ruled table (owner-disposition.md)     → all counts
#   - the edited .sysml sources                  → A9's new source_line, layer line numbers
# Explicitly NOT permitted: reading a count off check_gated_manifest.py or pytest.
grep -n "pumping_speed_agrees" tests/fixtures/catf_mfe_gated/designs/catf_mfe/vacuum.sysml
```

### Changes Required

**See `design.md#expected-output-derivation-plan-sc-6` for the per-artifact change list (rows 1–6)
and `design.md#potential-risks` for the ledger-format trap.**

- [x] `tests/expectations/constraint_population/catf_mfe_gated.json` — drop the A5/A6 rows; rename
      A9 and set its `source_line` **read from the edited source** (row 1)
- [x] `tests/expectations/gated_manifest/catf_mfe_gated.json` — full field list in row 2:
      `56/9/53/3/3`, A5/A6 deletion records (d5 lines 612, 630), A9 into `renamed_carriers`,
      histogram `{eligible 3, excluded 0, non_reaching 53}`, coverage `56/3/3/0/0/{}`,
      `gates_satisfied` **and its stale `_note`**, rewritten `histogram_rows`, and the
      `.project/active/…` → `completed/` citation corrections
- [x] `tests/unit/data/expected-coverage.md` — ledger row
      `catf_mfe_gated | 56 | 3 | 3 | 0 | 0 | {} | complete | violation | 3` (**nine columns
      exactly** — a malformed row fails the whole suite loudly) plus the re-derived prose section
      (3 asserted executing + 5 B-guards + 48 Group C = 56; "why `assessed_entry_count` is 2" → 3)
- [x] `tests/conformance/test_gated_manifest_identity.py` — literals `58/7/56/2` → `56/9/53/3`;
      deletion-row set gains `A5`, `A6`. (The new per-occurrence falsification cases land in
      Phase 3 with the mechanism they exercise.)
- [x] `scripts/check_gated_manifest.py` — module docstring `65 = 58 + 7` → `65 = 56 + 9` only. The
      `DERIVATIONS` extension is Phase 3.
- [x] `tests/fixtures/catf_mfe_gated/PROVENANCE.md` — **all of `design.md`'s PROVENANCE edit list in
      one pass**, amending rather than annotating (capture-fidelity law 3). Do not skip these three,
      which are easy to lose:
      - **§5(b)** the new A9 subsection carrying the ruled unit-check cells, matching A2's and A3's
        shape — the live home for the human unit claim
      - **§5(c)** this design's **D3** record, plus the correction to `:345-348`'s now-false premise
      - **the float-drift record** (§2 or §5): four layers drift −8.88e-16 m, chain re-converges at
        `ht_shield.outer_radius`, no generated byte changes, and an execution expectation moving is
        **the surfacing event, not a number to absorb**
      - **§3b — SC-3 side 1**: the epic's third criterion is a not-fired conditional naming
        `[INLINE-PREDICATE-MARKER-DROP]` as its trigger; the B1–B5 markers stay recorded here
      - Watch the naming trap: PROVENANCE §5's "D3" is **Item 5's** decision, unrelated to this
        design's D3 (`design.md#expected-output-derivation-plan-sc-6`, naming caution).

### Validation

**Automated:** none by design. Running a confirmation here would defeat the phase.

**Manual:**
- [x] Re-derive `65 = 56 + 9` and `53 + 3 = 56` by hand against the spec's nine-row deletion table
- [x] Count the ledger row's columns: nine
- [x] Grep PROVENANCE for `blocked-by-defect` → only historical/retired framing remains, with the
      retirement citing `62a07e5`
- [x] Grep PROVENANCE for `65 = 58 + 7` → zero hits (including the Authority block, where the
      `SC-3` reference is **Item 5's** SC-3 and stays as-is; only the number changes)

**What we know works after this phase:** nothing yet — and that is the point. What we have is a
falsifiable, timestamped claim.

### Commit point C2 — the SC-6 evidence

All five expectation documents in one commit, **before** any confirmation run. This commit's
position in history is the evidence that the numbers came from the ruled table and not from a run.

---

## Phase 3 — Per-occurrence prover, then the first confirmation run

### Goal

Extend `check_gated_manifest.py` so each of the 30 derivations is anchored to its owning block and
gated individually, add the occurrence-scoped falsification cases, and run the first confirmation.

### Assumption Under Test

Design bet **B5** — every derivation sits inside exactly one findable owning block, so the gate is
per occurrence and not a file-scope citation check (the audit A-1 gap). The probe's block scanner
confirmed all 27; this phase pins it in shipped code with failure cases.

### Test Stencil (write these before the prover change)

```python
def test_stripping_one_layers_documentation_names_that_layer(tmp_path):
    root = _fixture_copy(tmp_path)
    # Replace WITHIN blanket's block line range, or with count=1 against a block-unique
    # anchor. An unbounded str.replace deletes all 14 identical A6 lines and yields 14
    # problems, not one (test_gated_manifest_identity.py:143-147).
    _strip_comment_block(root, layer="blanket", attr="outer_radius")
    problems = check(root)
    assert len(problems) == 1
    assert "blanket" in problems[0] and "outer_radius" in problems[0]

def test_removing_one_layers_initializer_names_that_layer(tmp_path): ...   # exactly one, "not found"
def test_an_unfindable_owner_block_is_a_problem_not_a_skip(tmp_path): ...  # not found
def test_an_ambiguous_owner_block_is_a_problem_not_a_skip(tmp_path): ...   # ambiguous
```

Each layer now carries **two** comment blocks, one per derivation, so every case must say which
derivation it mutated.

### Changes Required

**See `design.md#implementation-notes` for the `Derivation` dataclass sketch and the three
anchor-failure messages; `design.md` D5 for why line ranges and comment-coupled anchors were
rejected.**

- [ ] `tests/conformance/test_gated_manifest_identity.py` — the four cases above, occurrence-scoped
- [ ] `scripts/check_gated_manifest.py` — `DERIVATIONS` becomes
      `dict[str, tuple[Derivation, ...] | None]` keyed by usage, each `Derivation` carrying
      `(relative, owner, initializer)`; populate all 27 new entries plus the three existing ones
      (`gamma_shield`, `catf_vacuum_vessel`, `AlphaNeutronSplit`) on the same rule
- [ ] Same file — block scanner: locate the owning block by its declaration header, close it by
      brace depth, require the initializer **exactly once inside that block**
- [ ] Same file — **no file-wide fallback**. All three anchor failures append a problem naming the
      usage and the owner. A derivation the prover cannot anchor is a failure, never an unchecked
      row.

### Validation

**Automated:**
- [ ] `python scripts/check_gated_manifest.py --check` → reports `65 = 56 carriers + 9 named
      deletions`, `53` by name, `3` by `renamed_from:`, and gates all **30** derivations
- [ ] `pytest tests/conformance/test_gated_manifest_identity.py` → green, all falsification cases
      included
- [ ] `pytest tests/conformance/test_constraint_population_oracle.py -k catf_mfe_gated` → green
      (licensed; this is what confirms the population `source_line`)
- [ ] `pytest tests/unit/test_coverage_ledger_agreement.py` → green (licensed; parses the ledger row)

**Manual:**
- [ ] Confirm the failure messages name the layer, not just the file — read one of them

**What we know works after this phase:** the restated identity closes against a prover whose
strongest claim is gated per occurrence, and the committed expectations are confirmed by a run that
happened after they were committed.

### Commit point C3

Prover + conformance cases. If any expectation from C2 is found wrong here, **fix it in its own
commit with a message saying which number was wrong and why** — do not amend C2. The commit order is
load-bearing evidence and rewriting it destroys the evidence.

---

## Phase 4 — BACKLOG: SC-3 side 2 and the `ProductWithinBand` cost

### Goal

Record the two backlog obligations that outlive this item, both phrased as decision records.

### Assumption Under Test

That `.project/backlog/BACKLOG.md` is still free of foreign uncommitted edits. Another agent is
closing Items 6 and 8 in this worktree. It was clean at spec and design time; it is re-checked here.

### Test Stencil

```bash
git status --porcelain .project/backlog/BACKLOG.md   # must be clean or ours-only before editing
```

### Changes Required

- [ ] **Concurrency guard first.** If a foreign edit is present, defer both lines to Phase 5 and
      re-check; if still foreign at the end, record the deferral in `verification.md` rather than
      editing over another agent.
- [ ] `.project/backlog/BACKLOG.md` `[INLINE-PREDICATE-MARKER-DROP]` (`:1148-1159`) — **amend**, do
      not add. The closing clause *"(the Item 5 workaround that epic Item 9 retires)"* is wrong;
      Item 9 does not retire the workaround — closing the defect does. One line replaced, saying
      that closing the defect fires the B1–B5 marker migration (spec N-4.2; design change-list row 8).
- [ ] Same file — **new unowned entry** recording `ProductWithinBand`'s per-dimension cost: a
      constraint port takes its unit from the formal's own declaration, so a unit-carrying
      constraint form is authored per dimension; `ProductWithinBand` is m³/s-specific and a product
      band over another dimension needs its own definition. Decision-record phrasing, never an
      instruction to future agents (design change-list row 9).

### Validation

**Automated:**
- [ ] `grep -n "INLINE-PREDICATE-MARKER-DROP" .project/backlog/BACKLOG.md tests/fixtures/catf_mfe_gated/PROVENANCE.md`
      → **both** sides hit, and reading them shows a not-fired conditional on one side and the
      firing trigger on the other

**Manual:**
- [ ] Read both new/amended paragraphs for capture-fidelity law 3: no stacked contradicting sentence
      beside a stale one, no "WE MUST NOT" phrasing

**What we know works after this phase:** whoever picks up the defect inherits the obligation from
the entry itself, not from an archived item's conditional. SC-3 no longer ships half-met.

### Commit point C4

BACKLOG only. Nothing else in this commit.

---

## Phase 5 — Full gates and `verification.md`

### Goal

Prove no regression anywhere, prove the freezes held, and record exact counts.

### Assumption Under Test

That the blast radius really was the five artifacts the spec enumerates — nothing else in the suite
reads this fixture.

### Test Stencil

```bash
set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a
/home/reid/1cfe/item7-rebuild-venv/bin/python -m pytest tests/ 2>&1 | tee /tmp/item9_full.log
grep -c "SKIPPED.*license" /tmp/item9_full.log    # must be 0 — the only licensed proof
```

### Changes Required

- [ ] Create `.project/active/derivative-upgrade-held-intent/verification.md` with **exact counts**,
      not adjectives: pass/fail/skip totals, the license-skip count (0), ruff and mypy counts against
      their baselines, the measured module/stencil/parameter-group counts, and the recorded 26/16 key
      movement.

### Validation

**Automated:**
- [ ] Full licensed suite green, **zero license-skip lines**, on the item7-rebuild venv
- [ ] `ruff check src/ scripts/ tests/` → **zero new** against baseline **12**
- [ ] `mypy src/` → **zero new** against baseline **52**
- [ ] `git diff --check` → clean (no whitespace errors)
- [ ] `git diff --stat main...HEAD` names **no** file under `tests/fixtures/catf_mfe_model/`,
      `tests/fixtures/catf_mfe_d5/`, or
      `.project/completed/20260813_catf-constraint-policy-acceptance/`
- [ ] `git status --porcelain` shows no staged file belonging to the concurrent agent

**Manual:**
- [ ] Walk design.md's Validation Approach items 1–7 and tick each in `verification.md`, including
      item 6 (SC-3 grepped on both sides) and item 7 (§5 A9 subsection + float-drift record present
      and findable)
- [ ] If `test_the_lane_runs_the_real_simkit` fails on the whole-set run, re-run it in isolation,
      confirm it passes, and record it as the known pre-existing artifact. Do not chase it.

**What we know works after this phase:** the item is complete and auditable — every claim in the
spec's success criteria has a recorded count behind it.

### Commit point C5

`verification.md`. Then the item is ready for `/_my_audit` and `/_my_close`.

---

## Risk Management

**See `design.md#potential-risks` for the full analysis.** Phase-specific mitigations:

- **Phase 1 — snapshot re-capture unproven.** Mitigated by making it the first thing that runs,
  before any expectation exists. `captured_at` churn on the one re-captured file is expected; a diff
  beyond it is a finding.
- **Phase 1 — float drift.** Four layers drift one ULP. No generated byte changes, so it can only
  appear at execution. If an execution expectation moves, that is the surfacing event — record it,
  do not re-baseline it.
- **Phase 2 — the ledger is parsed, not transcribed.** Nine columns exactly, or the whole suite
  fails loudly.
- **Phase 2 — the PROVENANCE list is long and easy to half-do.** Mitigated by the explicit callouts
  above for §5(b), §5(c), the float-drift record, and §3b.
- **Phase 3 — unbounded `str.replace` in the existing falsification idiom** would hit all 14
  identical A6 lines. Mitigated by the block-scoped replacement rule stated in the stencil.
- **Phase 4 — BACKLOG concurrency.** Mitigated by the re-check-then-defer guard.
- **Whole item — D3 is an edit outside the ruled 27.** Ratified at design review and recorded in the
  fixture's PROVENANCE §5 so the record outlives the archived design.

---

## Implementation Notes

[TO BE FILLED DURING IMPLEMENTATION]

### Phase 1 Completion
**Completed:** 2026-08-13

**Actual Changes:**
- `designs/catf_mfe/radial_build.sysml` — 27 derivations authored in place (14 `outer_radius`,
  13 `inner_radius`), each with the design's three-line `//` block; the `catf_radial_build`-level
  basis paragraph added above `attribute elongation`; `LayerContinuity` and
  `RadiusThicknessConsistency` deleted; D3's `tf_coil.thickness` comment amended to
  `// m - from line 83 (= tf_dr)`.
- `library/constraints/gate_forms.sysml` — `ProductWithinBand` added, four formals unit-annotated,
  with a block comment recording why the form is dimension-specific.
- `designs/catf_mfe/vacuum.sysml` — `PumpingSpeedConsistency` replaced in place by
  `assert constraint pumping_speed_agrees : ProductWithinBand` at `rel_tol = 0.01`; the
  `private import CATFGateForms::ProductWithinBand;` added. **A9 now sits at
  `designs/catf_mfe/vacuum.sysml:171`** (read from source; this is Phase 2's `source_line`).
- `instance_graph_snapshot.json` — re-captured in place under license.

**Measured (Phase 1 proof, both lanes, licensed):**
- `sysml-codegen snapshot --models tests/fixtures/catf_mfe_gated` — completed, no refusal. **B3
  holds through snapshot certification**; no `SnapshotCertifiabilityError`.
- `generate --from-snapshot` — sealed. **62 modules, 58 stencils, 9 parameter-group schemas,
  9 JSON templates.** All five preflights passed.
- `generate --models` — sealed, same shape.
- Registry alias warning present on both routes and left alone:
  `Module class name collisions detected: ['outer_radiusModule']. Generating aliased imports for
  15 modules.`
- Public key movement: **65 → 55, 26 leave / 16 arrive**, matching the derived sets exactly.
  The 26 leaving are the 13 layers' `inner_radius`+`outer_radius` pairs; the 16 arriving are 13
  layer thicknesses + `axis_region.thickness`… measured precisely as 13 thickness keys +
  `axis_region.inner_radius` + `pump_capacity_each` + `pumping_speed_agrees__rel_tol`. No key
  moved that is outside those sets.

**Issues:**
- **Snapshot re-capture diff — the v6 envelope has no `captured_at` field at all.** The plan's
  "anything beyond `captured_at`" test therefore reads differently than written: there is no
  timestamp churn to filter. Every field that moved traces to the edited sources —
  `sources.files` (exactly the three edited paths, by sha256 and size), `sources.fingerprint`,
  `integrity.digest`, `instance_graph.fingerprint`, and the graph itself
  (`attrs` 374→360, `calcs` 44→58, `constraint_usages` 58→56, `constraints` 5→3). Nothing
  spurious moved. `constraints` 5→3 is the ruled movement, not a loss: the three inline
  definition-less nodes (`LayerContinuity`, `RadiusThicknessConsistency`,
  `PumpingSpeedConsistency`) are gone and `CATFGateForms::ProductWithinBand` has joined
  `PositiveQuantity` and `FractionWithinBand` as a def-typed constraint.

**Deviations:**
- The derivation comment blocks use design.md's three-line concrete shape (D4), not the probe
  script's two long lines. Same two statements, same authority citation.
- `probes/apply_item9_edits.py` was used as reference text only, not run against the live
  fixture, per the plan.

### Phase 2 Completion
**Completed:** 2026-08-13. **No confirmation run happened before this commit.**

**Actual Changes:**
- `tests/expectations/constraint_population/catf_mfe_gated.json` — 58 → 56 rows: A5's and A6's rows
  dropped; A9 renamed to `…::pumping_speed_agrees` with `source_line` **171**, read from the edited
  `vacuum.sysml`, not from any run.
- `tests/expectations/gated_manifest/catf_mfe_gated.json` — `carrier_total` 56, `deletion_total` 9,
  `matched_by_name` 53, `matched_by_renamed_from` 3, `assessed_entry_count` 3; A5/A6 deletion
  records added at d5 lines 612 and 630; A9 added to `renamed_carriers`; histogram
  `{eligible 3, excluded 0, non_reaching 53}`; coverage account `56/3/3/0/0/{}/complete`;
  `gates_satisfied` gains A9 **and its `_note` rewritten** ("both gates satisfy at 20000" was stale
  at three); `histogram_rows` rewritten on all three keys; `_comment` and `_basis` citations moved
  from `.project/active/…` to `.project/completed/20260813_…`.
- `tests/unit/data/expected-coverage.md` — ledger row
  `catf_mfe_gated | 56 | 3 | 3 | 0 | 0 | {} | complete | violation | 3` (**nine columns, counted**);
  prose section re-derived (3 asserted executing + 0 plain reaching + 5 B-guards + 48 Group C = 56),
  "why `applicable_gate_total` is 2" → 3, "why `assessed_entry_count` is 2" → 3, plus a paragraph
  recording that A9 is satisfied at the design point and does not move the headline.
- `tests/conformance/test_gated_manifest_identity.py` — `58/7/56/2` → `56/9/53/3`; deletion-row set
  gains `A5` and `A6`; module docstring identity restated.
- `scripts/check_gated_manifest.py` — module docstring `65 = 58 + 7` → `65 = 56 + 9` and the source
  table's "58 carriers" → "56 carriers". No `DERIVATIONS` change (that is Phase 3).
- `tests/fixtures/catf_mfe_gated/PROVENANCE.md` — the whole edit list in one pass: header identity
  and carrier split; measured-shape paragraph (62 modules, measured in Phase 1); §1's gate_forms
  record; a new **A9 per-change record** carrying the third `renamed_from:`/`now:` pair the prover
  joins on; the derivations table gains A5 and A6; "what was not edited" amended; §2 heading and
  identity; **D8 (A5)** and **D9 (A6)** deletion records; the **float-drift record**; §3a rewritten
  as a retirement citing `62a07e5`, with A9's SC-5 re-entry recorded and the archive's byte-freeze
  stated; §3b's **SC-3 side 1** as a not-fired conditional naming `[INLINE-PREDICATE-MARKER-DROP]`;
  B3's row tense; §5's three edits — the stale "both gates take the unit-blind band", the corrected
  premise about constraint formals carrying unit text, **Item 9's D3 record**, and a new **A9
  unit-check subsection** matching A2's and A3's shape; the Authority block's identity.

**Manual checks:**
- `65 = 56 + 9` and `53 + 3 = 56` re-derived by hand against the spec's nine-row deletion table.
- Ledger row column count: nine.
- `grep blocked-by-defect PROVENANCE.md` → 2 hits, both retirement framing; `62a07e5` cited 4×.
- `grep "65 = 58 + 7"` / `"58 carriers"` in PROVENANCE → zero hits.
- Deletion headings D1–D9 all match the prover's `### D\d+ — <row> \`<qn>\`` form; three
  `renamed_from:` bullets, each with its `**now:**` partner.

**Issues:**
- The `_note` on the feasible candidate and the measured-shape paragraph's `full_satisfaction`
  headline were **already stale before this item** (corrected under Item 5 finding 6-D in the ledger
  and manifest but not in PROVENANCE). Both were amended in this pass rather than left, since the
  paragraphs were being rewritten anyway.

**Deviations:**
- The new §5 subsection is headed *"Item 9's decision D3"*, not *"D3"*, so it cannot be confused
  with §2's deletion record D3 or with §5's own heading, which carries **Item 5's** D3. It also
  keeps the prover's deletion-heading regex from matching it.

### Phase 3 Completion

### Phase 4 Completion

### Phase 5 Completion

---

**Status:** Draft → In Progress → Complete
