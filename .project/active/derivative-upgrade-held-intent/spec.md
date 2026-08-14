# Spec: Derivative Upgrade Under Held Intent (CONSTRAINT-SEMANTICS Item 9)

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-08-13
**Complexity:** MEDIUM (mechanical edits, but broad: ~27 attribute declarations, four committed
expectation artifacts, one prover extension, one licensed re-capture)
**Branch:** `item7-rebuild`

---

## Problem

`tests/fixtures/catf_mfe_gated` is the worked example of the ruled constraint policy. Three of its
rows are not the shape the owner ruled — they are the shape a defect allowed.

Item 5 measured that A9's assert-band and 26 of the 27 A5/A6 radius derivations refused against the
projection with `SI_RENDERING_COLLISION`, so the D-S1/D-S2 ruling landed those three rows as
**visible plain usages marked `blocked-by-defect`**, with their ruled target forms held as recorded
intent. Item 8 cured that defect at `62a07e5c870158672eb100f1cba73adfe4c9df28`: constraint-formal
and computed-attribute ports now carry authored unit text, and a design attribute reached by both a
calc and a constraint no longer refuses the model.

So the held intent is now buildable, and the fixture is out of date with the ruling it exists to
demonstrate. Three things are wrong today:

- The radial build asserts by constraint what the ruled basis says it should compute
  (A5 `LayerContinuity`, A6 `RadiusThicknessConsistency`).
- The vacuum cross-check is an exact `==` between two independently authored routes that already
  disagree by 0.16 m³/s (A9 `PumpingSpeedConsistency`), where the owner ruled a 1% relative band.
- The fixture's live PROVENANCE carries `blocked-by-defect` markings whose cause is gone.

**Authority for this item is closed. [AGENT] (ratified by owner, 2026-08-13)** — filed under Item
5's D-S1/D-S2 ruling, option 3. The target forms are already ruled; **no new disposition is
authorized here**. This item executes held intent and restates the arithmetic that follows from it.

**Held intent, path-cited** —
`.project/completed/20260813_catf-constraint-policy-acceptance/owner-disposition.md`:

- **A5 / A6 basis** — *"the free parameters are the axis root radius plus the 14 layer thicknesses;
  all other radii are derived"*, **[AGENT] (ratified by owner, 2026-08-13)**. Ruled intent for both
  rows: delete the constraint and derive — each layer's `inner_radius` from the layer below, each
  `outer_radius := inner_radius + thickness`. *"A parameterization is an engineering decision
  carrying owner sign-off, never a side effect of classification."*
- **A9 tolerance** — **[OWNER 2026-08-13] 1% relative**, band = `count * each_capacity ± 1%`,
  *"chosen over absolute so the band scales under design-search resizing"*.
- **A9 target form** (same row): `assert constraint pumping_speed_agrees : ProductWithinBand
  { in observed = pumping_speed_total; in count = n_pumps; in each_capacity = pump_capacity_each;
  in rel_tol = …; }` in the relative form. *"if the def-shape changes materially, design notes it
  rather than silently adapting."*
- **O6** — *"A5/A6 imply 27 attribute-declaration edits. Acknowledged, design-owned; the edit is
  authorized by the A5/A6 basis ruling"* — edit shape design-owned.
- **Derivation documentation obligation** (`owner-disposition.md:37-41`, **[OWNER 2026-08-13]**
  structural amendment): every derivation records the undirected relation and states that the
  direction is a **chosen basis, not physics**, and the PROVENANCE deletion record repeats it.

---

## Success Criteria

- [ ] **Three executing gates.** A2 (`net_power_viable`), A3 (`parasitic_fraction_ok`) and A9
      (`pumping_speed_agrees`) are asserted, bindings-form, and eligible in the catalog. A9 asserts
      `ProductWithinBand` in relative form at `rel_tol = 0.01`.
- [ ] **A5 and A6 are deleted and replaced by derivations** on the ruled basis: `axis_region`'s
      root radius and the 14 layer thicknesses stay free; the other 27 radii (13 `inner_radius`,
      14 `outer_radius`) are computed attributes.
- [ ] **The `blocked-by-defect` markings are retired on the live surface** — the fixture's
      `PROVENANCE.md` §3a and its disposition row — with the retirement citing Item 8's fix commit,
      and the archived `owner-disposition.md` verified byte-untouched (requirement P-1).
- [ ] **Expectations are re-derived from the ruled table and committed before any confirmation run**
      (Item 5's SC-6 discipline: expectations first, then run — the commit order is the evidence).
- [ ] **The integrity manifest re-proves the restated identity.**
      `scripts/check_gated_manifest.py --check` reports `65 = 56 carriers + 9 named deletions`, and
      ties each of the A5/A6 derivations to its in-source initializer and its relation +
      chosen-basis statements.
- [ ] **Frozen twins and the archived ruling are byte-untouched.** `git diff --stat` names no file
      under `tests/fixtures/catf_mfe_model/`, `tests/fixtures/catf_mfe_d5/`, or
      `.project/completed/20260813_catf-constraint-policy-acceptance/`.
- [ ] **The licensed suite is green with zero license-skip lines**, run on the correct interpreter
      (see Known Requirements, environment).
- [ ] **SC-3 is recorded on both sides as a not-fired conditional** (see requirement N-4).

---

## Known Requirements

### The restated accounting identity

- **[NEED]** The derivative's identity is restated to **`65 = 56 carriers + 9 named deletions`**,
  as the mechanical consequence of executing A5/A6 — not a re-disposition. The 9, by name:

  | # | table row | usage | class |
  |---|---|---|---|
  | D1 | A1 | `CATFMFEPhysics::catf_physics::PowerBalanceConsistency` | derive-instead |
  | D2 | A4 | `CATFMFERadialBuild::catf_radial_build::TotalRadiusConsistency` | derive-instead |
  | D3 | A7 | `CATFMFEShield::catf_shield::CompositionConsistency` | derive-instead |
  | D4 | A8 | `CATFMFEVacuum::catf_vacuum_vessel::ThicknessConsistency` | derive-instead |
  | D5 | C37 | `FusionPhysics_PowerBalance::AlphaNeutronSplit::EnergyConservation` | derive-instead |
  | D6 | C21 | `FusionPhysics_Confinement::PlasmaConfinement::Phase2PlasmaParametersPhysical` | delete-placeholder (O2) |
  | D7 | C28 | `FusionPhysics_Neutronics::TritiumBreedingRatio::Phase2SelfSufficiency` | delete-placeholder (O2) |
  | **new** | **A5** | `CATFMFERadialBuild::catf_radial_build::LayerContinuity` | derive-instead |
  | **new** | **A6** | `CATFMFERadialBuild::catf_radial_build::RadiusThicknessConsistency` | derive-instead |

  Seven `derive-instead` plus two `delete-placeholder`. Record numbering is design's call; the
  membership is not.

- **[INFERRED]** The carrier match splits **53 by name + 3 by `renamed_from:`** (was 56 + 2). A5 and
  A6 leave the name-matched set by deletion; A9 leaves it by rename
  (`…::PumpingSpeedConsistency` → `…::pumping_speed_agrees`), the same bridge A2 and A3 already use.
  `tests/expectations/gated_manifest/catf_mfe_gated.json` carries `matched_by_name` and
  `matched_by_renamed_from` as committed fields, so both must move.

### The A5/A6 derivations

- **[NEED]** The free parameters are `axis_region.inner_radius` and the 14 layer thicknesses.
  Every other radius is derived (`owner-disposition.md` A5/A6 basis cells).
- **[HARD]** The 14 layers in `designs/catf_mfe/radial_build.sysml`, in order: `axis_region`,
  `plasma_region`, `vacuum_gap`, `first_wall`, `blanket`, `reflector`, `ht_shield`, `structure`,
  `gap1`, `vessel`, `tf_coil`, `gap2`, `lt_shield`, `bioshield`. That gives 27 derived declarations
  — 14 `outer_radius := inner_radius + thickness`, and 13 `inner_radius := <layer below>.outer_radius`
  (`axis_region.inner_radius = 0.0 [m]` is the free root). That is exactly O6's 27 edits.
- **[HARD]** The derivations must reproduce the authored literals exactly. Checked against source:
  every layer's `outer_radius` literal already equals its `inner_radius + thickness` literal to the
  digit, and every layer's `inner_radius` already equals the layer below's `outer_radius`
  (`0.0+3.0=3.0`, `3.0+1.1=4.1`, … `7.55+1.0=8.55`). So no downstream value moves. If a run shows
  any downstream number moving, that is a surfacing event (capture-fidelity law 4), not something to
  absorb into a re-baselined expectation.
- **[NEED]** Each derivation carries, in source, the **undirected relation** and an explicit
  statement that the direction is a **chosen basis, not physics**
  (`owner-disposition.md:37-41`, **[OWNER 2026-08-13]**), and the PROVENANCE deletion record repeats
  it. The existing fixture deviation stands: `//` comments rather than `doc /* … */` bodies, already
  recorded and orchestrator-confirmed in `PROVENANCE.md:122-129`.
- **[INHERITED]** The axis-region leg is no longer a special case. Item 5 left
  `axis_region.outer_radius` underived only so the radial build would not carry two bases at once
  (`PROVENANCE.md:100-103`); under the full derivation there is one basis and the leg derives with
  the rest.

### The A9 gate

- **[NEED]** A9 becomes an asserted band over a product, at **1% relative** — band =
  `count * each_capacity ± 1%` (**[OWNER 2026-08-13]**). The tolerance value is `0.01`; the ruling
  fixes the relative form, not a spelling.
- **[NEED]** `ProductWithinBand` is authored in `library/constraints/gate_forms.sysml`, which
  deliberately omits it today because A9 was parked (`PROVENANCE.md:33-36`).
- **[NEED]** If the definition's shape has to change materially from the ruled row's sketch, the
  **design notes the change**; it does not silently adapt (A9 row).
- **[HARD]** No formal may be named `value` — it is a reserved generated local in predicate scope
  and generation refuses the model (`src/sysml_codegen/generation/constraint_name_safety.py:39`;
  the A2 finding recorded at `PROVENANCE.md:38-52`). None of `observed`/`count`/`each_capacity`/
  `rel_tol` collides, but the preflight is the authority, not this note.
- **[HARD]** Predicates stay bindings-only, written over formals; feature chains are allowed in
  binding position only (`rulings-20260812.md` Q4). No `[unit]` literal in a predicate body.
- **[INFERRED]** The band is satisfied at the authored design point: `pumping_speed_total = 200`
  against `n_pumps * pump_capacity_each = 48 × 4.17 = 200.16`, a 0.08% disagreement inside a 1%
  band. So A9 adds a satisfied gate and does not move the fixture's `violation` headline, which A2
  owns.

### Retiring the `blocked-by-defect` records

- **P-1. Freeze the archive. [AGENT] (orchestrator ruling, 2026-08-13)**
  `.project/completed/20260813_catf-constraint-policy-acceptance/owner-disposition.md` stays
  **byte-untouched**, and Item 9's verification includes a byte-untouched check on it. The
  retirement lands on the **live surface only**: the fixture's `PROVENANCE.md` (§3a and its
  disposition row) plus this item's own records, citing Item 8's fix commit `62a07e5`.

  Three reasons, recorded so a later reader does not re-open it:
  1. The archived A5/A6/A9 rows already carry their own conditional dating — *"retained as a visible
     plain usage until the unit-lane fix lands"*, *"then deleted per ruled intent"*. Once Item 9
     executes, the archive reads as a correctly dated record of the ruling, not a stale claim about
     the present.
  2. The epic criterion ("retired from table and PROVENANCE") is satisfied on the live surface: the
     only live `blocked-by-defect` carrier is the fixture's PROVENANCE, which **is** the table's
     live projection.
  3. Precedent — this epic's closes treat archived owner-ruled artifacts as byte-frozen and verify
     them untouched.
- **[HARD]** PROVENANCE records that go false when this lands are broader than §3a. At minimum:
  §1's "`ProductWithinBand` is deliberately not authored", §1's "A5, A6, A9 are left exactly as
  `catf_mfe_d5` wrote them", §1's "the axis-region layer is not derived", §2's heading and identity
  (`65 = 58 + 7`), the measured-shape paragraph at the top, and the §3a parked-row block. Every one
  of them moves in the same edit — under capture-fidelity law 3 the corrected content is amended or
  deleted, not annotated with a note about what used to be true.
- **[INFERRED]** Record that A9 re-enters the SC-5 candidate set. D-S1 removed it *because of* the
  defect Item 8 cured (`owner-disposition.md`, "Post-probe status"), so that exclusion lapses with
  its cause. This is a record, not a re-disposition: SC-5's anchor stays A2, and nothing about
  Item 5's closed SC-5 evidence is reopened.

### Expected outputs — re-derived from the table, committed before the run

- **[NEED]** SC-6 discipline: expectations are derived from the ruled table and **committed before**
  the confirmation run, exactly as Item 5 did. A number read off a run and then written down as an
  expectation is not evidence.
- **[INFERRED]** Derived from the table, the expected values are:
  - disposition histogram `{eligible: 3, excluded: 0, non_reaching: 53}` over **56** carriers
    (was `{2, 3, 53}` over 58). A5/A6 leave by deletion; A9 moves `excluded → eligible`.
  - coverage account `56 / 3 / 3 / 0 / 0 / {} / complete`; `assessed_entry_count = 3` — A9 hangs off
    `catf_vacuum_pumping`, which has one occurrence, so it mints one concrete entry.
  - `tests/unit/data/expected-coverage.md` ledger row `catf_mfe_gated | 56 | 3 | 3 | 0 | 0 | {} |
    complete | violation | 3` (nine columns, as the committed block writes them), with the prose
    section re-derived to match.
  - `expected_study_outcomes`: the feasible candidate satisfies three gates (A9 added); the
    infeasible candidate still reports A2 as the violation. The pumping attributes are untouched by
    the `p_fusion` mutation, so A9 is satisfied on both legs.
  - the module count is **not** predictable from the table (27 new computed attributes may change
    it) and is therefore measured, not pre-committed. Say so where it is recorded.
- **[INFERRED]** The generated public surface moves, and that is expected. Each derived radius stops
  being a `DESIGN_ATTRIBUTE` entry point, so up to 27 public input keys leave the generated schemas
  and JSON input templates (ADR-001; `CLAUDE.md`, entry-point classification). The free parameters —
  `axis_region.inner_radius` and the 14 thicknesses — stay keys. Record the before/after key set;
  a key moving that is **not** one of the 27 derived radii is a surfacing event, not a re-baseline.
- **[INFERRED]** Stale citations in the artifacts this item rewrites get corrected in the same pass,
  since they are already being touched: the manifest expectation's `_comment` and `_basis` cite
  `.project/active/catf-constraint-policy-acceptance/…` (the item archived to `completed/`); the
  prover's module docstring states `65 = 58 carriers + 7 deletions`; `histogram_rows` still
  describes A5/A6/A9 as excluded.
- **[HARD]** Artifacts that must move together: the population expectation
  (`tests/expectations/constraint_population/catf_mfe_gated.json`), the manifest expectation
  (`tests/expectations/gated_manifest/catf_mfe_gated.json`), the coverage ledger
  (`tests/unit/data/expected-coverage.md`), the fixture's `PROVENANCE.md`, and the fixture's
  committed `instance_graph_snapshot.json` (re-captured under license, since the sources change).
- **[HARD]** `tests/conformance/test_gated_manifest_identity.py` asserts `58 / 7 / 56 / 2`
  literally (`test_the_identity_closes`) and pins the deletion-row set
  `{A1, A4, A7, A8, C37, C21, C28}`. Both must move to the restated shape, and its falsification
  cases must still fail closed.
- **[HARD]** `scripts/check_gated_manifest.py`'s `DERIVATIONS` map takes **one** initializer per
  deleted usage and refuses any initializer that is not unique in its file
  (`scripts/check_gated_manifest.py:99-114`, `:219-227`). Both halves break here: A5 and A6 each
  replace one usage with many derivations, and A6's 14 derivations are **byte-identical lines**
  (`attribute outer_radius : Real = inner_radius + thickness;`), so a set of initializers still
  trips the uniqueness refusal. The prover must match **per occurrence** — each derivation located
  by its owning layer, each carrying its own relation and chosen-basis statements. Anything less
  accepts the two biggest deletions on the strength of a citation alone, which is precisely the gap
  audit finding A-1 closed.

### SC-3 — the not-fired conditional

- **N-4. [OWNER 2026-08-13, ruled at Align]** The epic's third success criterion (author the five
  B1–B5 `@inapplicable:` markers) is a **conditional that does not fire in this run**, because
  `[INLINE-PREDICATE-MARKER-DROP]` is open and unowned. The five markers stay recorded in
  PROVENANCE §3b. The trigger is recorded **on both sides**:
  1. This item's records mark SC-3 as a not-fired conditional, naming the open defect as the
     trigger.
  2. The `[INLINE-PREDICATE-MARKER-DROP]` entry in `.project/backlog/BACKLOG.md`
     (`BACKLOG.md:1148-1159`) says that closing the defect fires the B1–B5 marker migration — move
     the five `@inapplicable:` markers from PROVENANCE into source and retire the workaround.
     Phrased as a decision record, not an instruction.

  The point of the second side: whoever picks the defect up inherits the obligation from the entry
  itself, not from an archived item's conditional.

- **[INFERRED]** Execute side 2 as an **amendment, not an added line**. The entry's closing sentence
  already reads *"the Item 5 workaround that epic Item 9 retires"* (`BACKLOG.md:1158-1159`), and
  that sentence is now wrong: Item 9 does not retire the workaround — closing this defect does.
  Amending it in place carries the owner's intent and avoids stacking a second, contradicting
  sentence beside a stale one (capture-fidelity law 3).

- **[HARD]** Concurrency guard for that edit. Another agent is closing Items 6 and 8 in this
  worktree. The BACKLOG line is written and committed **only** when `git status` shows
  `.project/backlog/BACKLOG.md` free of foreign uncommitted edits. It was clean at spec time
  (2026-08-13); re-check at edit time and defer the line to a later stage of this item if it is not.

### Environment and process

- **[HARD]** Interpreter: `/home/reid/1cfe/item7-rebuild-venv/bin/python -m pytest`. `uv run`
  resolves `agentic_mbse` to the main checkout and is wrong for this worktree pair.
- **[HARD]** License: `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a`. A run with
  license-skip lines is not a licensed proof.
- **[HARD]** Frozen twins `catf_mfe_model` and `catf_mfe_d5` do not change by a byte, and neither
  does the archived Item 5 record (P-1). Only `catf_mfe_gated` and its
  expectation/PROVENANCE/manifest inputs move.
- **[AGENT]** `spec_review` is **skipped for this item** as proportionate (orchestrator decision,
  2026-08-13). The orchestrator independently re-verified the restated-identity arithmetic against
  Item 5's close record — 58 − 2 = 56 carriers; 7 `derive-instead` + 2 `delete-placeholder` = 9;
  histogram `{eligible 3, excluded 0, non_reaching 53}` — and the design stage runs a fresh-session
  `design_review` against this spec.
- **[HARD]** Stage and commit only files this item touches. Do not commit, revert, or absorb the
  concurrent agent's changes to `CURRENT_WORK.md`, `BACKLOG.md`, `CHANGELOG.md`, or the
  calcdef-design archive moves.
- **[INHERITED]** Nothing is pushed; `main` is untouched; TEAx stays on
  `constraint-semantics-item3` @ `5b70ae9`; `pre_pr` remains with the owner.

---

## Non-Goals

- **No re-disposition.** A5, A6 and A9's dispositions, bases, and tolerance are ruled. This item
  executes them. Any evidence that a ruled form cannot be built is a surfacing event for the owner,
  not a licence to choose a different form.
- **Not fixing `[INLINE-PREDICATE-MARKER-DROP]`.** The marker-read gap stays open and unowned; only
  its trigger is recorded (N-4).
- **No TEAx change.** TEAx stays where it is.
- **No schema or catalog-vocabulary change.** Item 2's disposition vocabulary is closed; the three
  upgraded rows use existing tokens.
- **Not touching the frozen twins**, and not re-opening B4/A7's model debt (O3-a/O3-b) or
  `[CATF-CRYO-HEAT-LEAK-COEFFICIENT]`. Those stay recorded where they are.
- **Not deriving anything outside the radial build.** The A5/A6 basis covers layer radii; other
  literals (for example `catf_radial_build.major_radius`, which duplicates
  `axis_region.outer_radius`) are out of scope.

---

## Open Questions / Deferred to design

- **How the 27 derivations carry their documentation.** The obligation is per-derivation, and the
  manifest prover reads a `//` block within 12 lines above the initializer
  (`scripts/check_gated_manifest.py:119-124`). Repeating a full relation + basis paragraph 27 times
  is heavy; a per-layer one-liner plus one block statement may satisfy the obligation better. The
  obligation itself is not negotiable — only its shape is design's.
- **The shape of the per-occurrence `DERIVATIONS` extension** in the prover — how a derivation is
  anchored to its layer given 14 byte-identical initializer lines (owning `part` block, line range,
  or a scoped search). Whatever it is, both failure modes the conformance test already exercises
  (documentation stripped, initializer gone) must still fail closed for every A5/A6 derivation.
- **`ProductWithinBand`'s exact declaration** — formal spelling and how the ±1% band is written over
  the formals. Ruled: relative form, 1%. If the shape must change materially from the row's sketch,
  design notes it.
- **Whether the `[m]` unit lives on the derived attribute or in a trailing comment.** The fixture's
  dominant idiom is the comment; Item 8 changed what ports can carry. Design decides and records.
- **Whether the fixture's `instance_graph_snapshot.json` re-capture perturbs anything else**
  (timestamps, ordering). Measured at implement, not assumed.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_constraint_semantics_contract.md` (Item 9, lines 1254–1291)
- **Required Reading:**
  - `.project/completed/20260813_catf-constraint-policy-acceptance/owner-disposition.md` — the ruled
    table; rows A2/A3/A5/A6/A9, B1–B5, the vocabulary section, the accounting arithmetic, O2/O6/O7
  - `tests/fixtures/catf_mfe_gated/PROVENANCE.md` — §2 deletion records, §3a parked rows and held
    intent, §3b B1–B5, §5 unit reasoning
  - `scripts/check_gated_manifest.py` and `tests/conformance/test_gated_manifest_identity.py` — the
    existing prover and its falsification cases
  - `tests/unit/data/expected-coverage.md` — the `catf_mfe_gated` ledger row and its derivation
- **Design:** `.project/active/derivative-upgrade-held-intent/design.md` (to be created)
- **Product lens:** `.project/active/derivative-upgrade-held-intent/product-lens.md`

---

**Next Steps:** After approval, proceed to `/_my_design`.
