# Design: Derivative Upgrade Under Held Intent (CONSTRAINT-SEMANTICS Item 9)

**Status:** Implemented
**Owner:** Reid W
**Created:** 2026-08-13
**Branch:** `item7-rebuild` @ `0596f5c`
**Complexity:** MEDIUM — mechanical edits, broad blast radius, one prover extension

---

## Overview

Execute the held intent for A5, A6 and A9 on `tests/fixtures/catf_mfe_gated`: delete two radial-build
constraints in favour of 27 derivations, upgrade the vacuum cross-check to a 1%-relative asserted
band, retire the `blocked-by-defect` markings on the live surface, and restate the accounting
identity to `65 = 56 carriers + 9 named deletions`.

## Related Artifacts

- **Spec:** `.project/active/derivative-upgrade-held-intent/spec.md` (the contract)
- **Product lens:** `.project/active/derivative-upgrade-held-intent/product-lens.md`
- **Probe evidence:** `.project/active/derivative-upgrade-held-intent/probes/RESULTS.md` + scripts
- **Ruled table:** `.project/completed/20260813_catf-constraint-policy-acceptance/owner-disposition.md`
- **Item 8 (the unblocker):** `.project/completed/20260813_unit-lane-port-metadata/`, freeze `62a07e5`
- **Live surface:** `tests/fixtures/catf_mfe_gated/PROVENANCE.md`
- **Decision records:** `.project/adr/` does not exist in this tree. No prior entries to check, none filed.

---

## The Point

`catf_mfe_gated` is the **worked example of the ruled constraint policy**. Its whole job is to be
the artifact someone reads to see what the policy actually produces. Three of its rows are not the
shape the owner ruled — they are the shape a defect allowed, parked under Item 5's D-S1/D-S2 ruling
with their target forms held as recorded intent.

Item 8 cured the defect. So the fixture now misrepresents the policy it exists to demonstrate: it
asserts by constraint what the ruled basis says it should compute, it checks two independently
authored numbers with `==` when they already disagree by 0.16 m³/s, and it carries
`blocked-by-defect` markings whose cause is gone.

The obligation is to make the worked example true again, and to do it **without re-deciding
anything**. Every target form is already ruled `[OWNER 2026-08-13]` or `[AGENT] (ratified by owner,
2026-08-13)`. This item executes held intent and restates the arithmetic that follows from it. A
ruled form that cannot be built is a surfacing event for the owner, never a licence to pick a
different form.

That ladders up to the epic's contract: the catalog's dispositions have to mean something, and they
only mean something if the reference fixture is the policy rather than an accident of tooling.

---

## Research Findings

**The fixture and its join.** `catf_mfe_gated` is not consumed by any generation test. Its two live
consumers are `scripts/check_gated_manifest.py` (the accounting identity, license-free, joining four
documents plus the `.sysml` sources) and `tests/unit/test_coverage_ledger_agreement.py:84-95`, which
parses the ledger row out of `tests/unit/data/expected-coverage.md` and elaborates the fixture under
license. Nothing else reads it, so the change surface is exactly the artifacts the spec enumerates.

**The prover's current shape.** `DERIVATIONS` (`scripts/check_gated_manifest.py:99-114`) maps one
deleted usage to at most one `(file, initializer)` pair, and `check_derivations` refuses an
initializer that is not unique in its file (`:219-227`). Documentation is read as the contiguous
`//` block within 12 lines above the matched line (`:189-199`, `COMMENT_WINDOW = 12`), which must
contain both `relation (undirected):` and `chosen basis, not physics` (`:119-120`).

**The existing derivation idiom.** Item 5's A8 derivation is the precedent that already ships:
`vacuum.sysml:53-58` carries a five-line `//` block then
`attribute outer_radius : Real = inner_radius + wall_thickness;  // m`. Unit in a trailing comment,
`//` rather than `doc`, with the deviation recorded and orchestrator-confirmed at
`PROVENANCE.md:122-129`.

**Where a port's unit comes from.** `extract_feature_unit`
(`src/sysml_codegen/extraction/feature_metadata.py:57-65`) resolves a unit from the feature's
**type**, then its **trailing `//` comment**, then its doc description. The comment rule
(`:84-122`) takes the first token after `//` and rejects a stop-word list including `from`. The
`[m]` written on a *value* (`: Real = 0.25 [m]`) never reaches port metadata. Projection mints one
`EntryPoint` per public key and refuses when two consumers render different metadata
(`elaboration/project.py:394-397`).

**What Item 8 actually did.** It gave the constraint and computed-attribute lanes authored unit
text and pinned unequal text as a whole-model refusal — both agreement and disagreement cases are
conformance-pinned (`tests/conformance/test_unit_lane_port_metadata.py:157-203`). Its A9 and radius
customer fixtures (`tests/fixtures/unit_lane_a9/model.sysml`, `unit_lane_radius/`) annotate **every**
formal with a unit comment. That detail is load-bearing and is the thing the probe found.

---

## Core Concept

Nothing here is invented. The design's only real work is **three mechanical shapes**, and one of
them turned out to be a correctness requirement rather than a style choice.

The shapes are: how each of the 27 derivations carries its owner-required documentation so a prover
can gate it per occurrence; how that prover anchors a derivation when 14 of them are byte-identical
lines; and how the unit text is spelled on the new declarations.

The insight that organises all three is that **a unit lives on a declaration, and authoring a
derivation adds a consumer lane to a design attribute.** A derived `outer_radius = inner_radius +
thickness` does not just replace a constraint — it makes `thickness` an input port, and that port
reads its unit from `thickness`'s own declaration. If some other consumer already reads a unit there
and the two disagree, projection refuses the whole model. So "where does the `[m]` go" is not
cosmetics; it decides whether the ruled form builds at all. The same rule governs A9: a constraint
formal's port takes its unit from the formal's declaration, so an unannotated `ProductWithinBand`
projects four `None` ports that collide with the calc lane's real units on the same attributes.

Once that is understood, the rest composes with what already exists: the derivation idiom Item 5
established, the prover's existing comment-window contract, and the disposition vocabulary Item 2
closed. The prover extension is the one piece of new mechanism, and it is small — it swaps "unique
in the file" for "unique inside the owning block", which is the minimum needed to make 14 identical
lines individually gateable.

---

## Key Bets

- **B1. The 27 derivations are semantically inert at the decimal level** — every authored
  `outer_radius` literal already equals `inner_radius + thickness`, and every `inner_radius` already
  equals the layer below's `outer_radius`. *If false → this stops being an execution of held intent
  and becomes a re-baselining exercise, and the spec's whole "no downstream value moves" premise
  collapses.* **Confirmed decimally** by the spec against source and by the probe's clean generation.
  **Qualified at the bit level** — see the float-drift surfacing item under Risks.

- **B2. The three upgraded rows are the only catalog rows that move.** A5/A6 leave by deletion, A9
  leaves the name-matched set by rename; the other 53 usages are untouched. *If false → the restated
  identity `65 = 56 + 9` is wrong and every committed expectation in the change list is wrong with
  it.* **Confirmed**: measured catalog is 56 rows, histogram `{eligible 3, non_reaching 53}`.

- **B3. Annotating the two under-labelled declarations is sufficient to make every lane agree.**
  *If false → more collisions appear later in the pipeline (snapshot certification, or a lane the
  generate path does not exercise) and the landing is not atomic.* **Confirmed for generation**;
  the residual is snapshot capture and re-seal, which the probe did not run (see Handoff).

- **B4. The owner's documentation obligation is satisfied by a compact per-derivation statement.**
  The obligation is that the undirected relation and the chosen-basis claim survive the deletion at
  every derivation. *If false → the documentation is present but the obligation is not met, and the
  prover gates the wrong property.* This is a reading of an owner ruling, not a measurement; it is
  the one item in this design most worth a reviewer's disagreement.

- **B5. Every derivation sits inside exactly one findable owning block.** The prover's per-occurrence
  anchoring (D5) rests on each layer having a `part <name> {` header that appears once and closes by
  brace depth. *If false → the anchor is ambiguous and the gate silently weakens to file scope,
  which is the audit A-1 gap reopening.* **Confirmed** for all 27: the probe's block scanner located
  every layer and asserted exactly one matching declaration inside each. The failure behaviour is
  specified rather than assumed — see Implementation Notes.

---

## Key Decisions

- **D1. Unit text goes in a trailing `//` comment on the derived attribute, not `[m]` on the
  attribute.** *Rejected: `[m]` on the declaration* — the fixture's dominant idiom is the comment,
  Item 5's A8 derivation already ships exactly this spelling (`vacuum.sysml:58`), and the probe
  measured that a value-position `[m]` does not reach port metadata anyway. This answers the spec's
  deferred question 4 with evidence rather than taste.

- **D2. `ProductWithinBand`'s four formals carry unit comments (`// m³/s`, `// Dimensionless`).**
  *Rejected: bare `Real` formals like the other two gate forms* — measured to refuse the model.
  This is a **material change from the ruled row's sketch and is NOTE-ed below**, as row A9 requires.

- **D3. `tf_coil.thickness`'s trailing comment gains a readable unit.** `// From line 83 (= tf_dr)`
  → `// m - from line 83 (= tf_dr)`. *Rejected: leaving it* — measured to refuse. *Rejected:
  annotating all 14 thicknesses* — only `tf_coil.thickness` has a second consumer, and editing 13
  declarations that nothing requires is unauthorised churn. Authority: this is a mechanical
  consequence of A6's ruled derivation in the same sense as O6's 27 edits — without it the ruled
  form does not build. **Flagged for the reviewer as the one edit outside the 27.**

- **D4. Each derivation carries a short `//` block holding exactly two statements — the undirected
  relation and the chosen-basis claim — wrapped across two or three lines as the text needs; the
  full basis statement is written once at the `catf_radial_build` level.** The count that matters is
  two *statements*, not two lines; both derivations in the concrete shape below run to three lines.
  *Rejected: repeating a full paragraph 27 times* — heavy and unreadable. *Rejected: a single file-level statement with no per-derivation text* — the prover
  could then only gate a citation, which is precisely the gap audit finding A-1 closed. The two
  lines carry the relation and the chosen-basis claim verbatim, so the per-occurrence gate is real.

- **D5. The prover anchors each derivation to its owning block.** `DERIVATIONS` becomes
  usage → tuple of `(file, owning-block name, initializer)`. The block is found by its declaration
  header line and closed by brace depth; the initializer must appear **exactly once inside that
  block**. *Rejected: line ranges* — brittle against any edit above. *Rejected: matching the
  initializer plus its adjacent comment text* — couples the anchor to the documentation, so
  stripping the documentation would report "not found" instead of "missing its statements" and one
  of the two pinned failure modes would stop being distinguishable.

- **D6. Derivations are authored in place, in authored order, in the same declaration slots.** The
  layer's `inner_radius` and `outer_radius` keep their positions; only the initializer and the
  comment block above change. *Rejected: grouping the derivations into a new block* — would move
  every layer's source line and churn the population expectation for no gain.

- **D7. The bare sibling spelling (`axis_region.outer_radius`) is used, not a package-qualified
  one.** *Rejected: `catf_radial_build::axis_region.outer_radius`* — the bare form is what the
  deleted `LayerContinuity` used and the probe measured it resolving with no channel collapse.

---

## A9's authored form

Spec deferred question 3. The definition, in `gate_forms.sysml`:

```
constraint def ProductWithinBand {
    in observed : Real;        // m³/s
    in count : Real;           // Dimensionless
    in each_capacity : Real;   // m³/s
    in rel_tol : Real;         // Dimensionless
    observed > count * each_capacity * (1.0 - rel_tol) and
    observed < count * each_capacity * (1.0 + rel_tol)
}
```

And the usage, in `vacuum.sysml`, replacing `PumpingSpeedConsistency` in place:

```
assert constraint pumping_speed_agrees : ProductWithinBand {
    in observed = pumping_speed_total;
    in count = n_pumps;
    in each_capacity = pump_capacity_each;
    in rel_tol = 0.01;
}
```

**Checked against the ruled row** (`owner-disposition.md:106`), because "1% relative" is easy to
write and easy to get wrong:

- **Relative, not absolute.** The tolerance multiplies `count * each_capacity`, so the band is
  `count * each_capacity ± 1%` and it **scales under design-search resizing** — the owner's stated
  reason for choosing relative over absolute. An absolute band (`± rel_tol`) would read identically
  in a change list and still generate; this predicate is what makes the claim checkable.
- **Two-sided**, matching a class-2 cross-check between two independently authored routes.
- **`rel_tol = 0.01`** is the ruled 1%, dimensionless.
- **Bindings-only over formals**, no feature chain in the body, no `[unit]` literal in the body
  (spec `[HARD]`, `rulings-20260812.md` Q4). Verified: the body names only the four formals.
- Satisfied at the authored design point — `200` against `48 × 4.17 = 200.16`, a 0.08%
  disagreement inside a 1% band — so A9 adds a satisfied gate and does not move the `violation`
  headline, which A2 owns.

## NOTE — A9's def-shape changed materially from the ruled sketch

Row A9 requires that *"if the def-shape changes materially, design notes it rather than silently
adapting."* It did. Recorded here rather than absorbed:

**The ruled sketch** implies `ProductWithinBand` is a generic form over bare `Real` formals, like
its two siblings in `gate_forms.sysml`. **It cannot be.** A constraint formal's port takes its unit
from the formal's own declaration, so bare formals project `unit_text=None` and collide with the
calc lane's authored `m³/s` / `Dimensionless` on `pumping_speed_total` and `n_pumps`. Measured:
refusal, both keys (`probes/RESULTS.md`, Result 1).

The consequence: **`ProductWithinBand` is dimension-specific**, not reusable across dimensions the
way `PositiveQuantity` and `FractionWithinBand` are. A second product band over, say, powers would
need its own definition. `PROVENANCE.md:345-348` already predicted this cost — *"the per-dimension
in-predicate spelling is the only unit-carrying option and it costs one definition per dimension"* —
but recorded it as a cost the fixture avoids. After Item 8, constraint formals **do** carry unit
text via comments, so that paragraph is now false in its premise and true in its prediction. The
implementation corrects it.

The bindings, the tolerance, the relative form and the 1% value are all exactly as ruled. What
changed is the definition's genericity, which the ruled row did not fix.

---

## Architecture

Five artifacts move together, joined by one prover.

**Source of truth** is `tests/fixtures/catf_mfe_gated/**/*.sysml` — the fixture's authored model.
Three files change: `radial_build.sysml` (27 derivations + 2 constraint deletions + D3's comment),
`gate_forms.sysml` (add `ProductWithinBand`), `vacuum.sysml` (A9's assert + one import).

**The live record** is `PROVENANCE.md`. It carries the per-change records, the named deletions with
their authorizing rows, and the parked-row dispositions. It is the only place the `blocked-by-defect`
disposition is visible, so retiring it is an edit here.

**The committed expectations** are three documents derived from the ruled table, never from a run:
the population expectation (which usages exist, by `file:line`), the manifest expectation (the ruled
table's counts), and the coverage ledger row.

**The prover** (`scripts/check_gated_manifest.py`) joins all of the above and closes the identity.
Its deletion side is the only part that opens a `.sysml`: for each `derive-instead` row it must find
the replacing derivation in source and confirm it carries the owner's two statements. That is where
the per-occurrence extension lands.

**Data flow at check time**, unchanged in shape: d5 population (65 authored) ∪ gated population (56
carriers) ∪ PROVENANCE renames/deletions (9) → identity closes → cross-checked field by field
against the manifest expectation → then `check_derivations` opens the sources and gates all 30
derivations per occurrence.

---

## Required Invariants

1. Every d5 usage is **either** a carrier (by name or by `renamed_from:`) **or** a named deletion.
   Never both, never neither. `65 = 56 + 9`, with `53` by name and `3` by `renamed_from:`.
2. Every `derive-instead` row's derivations exist in source, **each located uniquely inside its
   owning block**, each carrying the undirected relation and the chosen-basis statement within the
   12-line comment window.
3. Both pinned failure modes still fail closed **per occurrence**: documentation stripped from one
   layer names that layer; the initializer removed from one layer names that layer.
4. `catf_mfe_model`, `catf_mfe_d5`, and `.project/completed/20260813_catf-constraint-policy-acceptance/`
   are byte-untouched. `git diff --stat` names no file under any of them.
5. Expectations are committed **before** the confirmation run. The commit order is the evidence.
6. **Every attribute reached by more than one consumer lane carries unit text those lanes agree
   on.** This is a build requirement, not a documentation preference. Note the scope carefully: an
   attribute with a single consumer needs no readable unit text, which is why 13 layer thicknesses
   and `axis_region.inner_radius` are correctly left unannotated (D3). The invariant is about
   agreement between lanes, not about universal annotation.
7. SC-3 is recorded as a not-fired conditional **on both sides** — the fixture's live record and
   the `[INLINE-PREDICATE-MARKER-DROP]` backlog entry — each naming the open defect as the trigger.

---

## Component Overview

| component | location | responsibility |
|---|---|---|
| Radial-build derivations | `tests/fixtures/catf_mfe_gated/designs/catf_mfe/radial_build.sysml` | 27 computed attributes on the ruled basis; the two constraints deleted |
| `ProductWithinBand` | `tests/fixtures/catf_mfe_gated/library/constraints/gate_forms.sysml` | the relative product band, formals unit-annotated |
| A9's gate | `tests/fixtures/catf_mfe_gated/designs/catf_mfe/vacuum.sysml` | `assert constraint pumping_speed_agrees : ProductWithinBand`, `rel_tol = 0.01` |
| Live record | `tests/fixtures/catf_mfe_gated/PROVENANCE.md` | retires `blocked-by-defect`; adds D8/D9; restates the identity |
| Per-occurrence prover | `scripts/check_gated_manifest.py` | `DERIVATIONS` anchored by owning block; 30 derivations gated |
| Falsification suite | `tests/conformance/test_gated_manifest_identity.py` | restated literals; per-occurrence failure modes |

---

## Non-Goals

- **No re-disposition.** Dispositions, bases and the tolerance are ruled. Only shapes are design's.
- **Not fixing `[INLINE-PREDICATE-MARKER-DROP]`.** SC-3 is a conditional that does not fire; only
  its trigger is recorded, on both sides.
- **No TEAx change, no schema change, no catalog-vocabulary change.**
- **Not touching the frozen twins**, and not re-opening O3-a/O3-b or `[CATF-CRYO-HEAT-LEAK-COEFFICIENT]`.
- **Not deriving anything outside the radial build** — `catf_radial_build.major_radius` stays a literal.
- **Not annotating the 13 thicknesses that need no annotation** (see D3).

---

## Implementation Notes

**Sequence matters, and it is not the obvious one.** SC-6 forbids reading a number off a run and
writing it down as an expectation, but the population expectation needs A9's new `source_line`,
which is a property of the authored source. So: **edit the sources first, read the line numbers from
the source, then derive and commit every expectation, then run.** Source is not an expectation; the
ordering that matters is expectations-before-confirmation-run.

**Where the SC-3 BACKLOG amendment lands.** As its own step, after the fixture edits and before the
confirmation run, so a `git status` re-check for foreign edits is fresh. It was clean at design time
(2026-08-13, verified). It is an **amendment**: `BACKLOG.md:1158-1159`'s closing clause *"(the Item 5
workaround that epic Item 9 retires)"* is now wrong and becomes a decision record that closing the
defect fires the B1–B5 marker migration. One line replaced, not a line added.

**The `value` trap did not fire.** None of `observed`/`count`/`each_capacity`/`rel_tol` collides with
the reserved generated local (`generation/constraint_name_safety.py:39`). Verified by a passing
generation, not by inspection.

**Expect a registry warning, not a failure.** 15 modules mint `outer_radiusModule` and are aliased.
This is the registry preflight doing its job. Do not "fix" it.

**A9's import.** `private import CATFGateForms::ProductWithinBand;` in `CATFMFEVacuum`, matching the
idiom at `physics.sysml:17-18`.

**Prover shape** (design sketch, not implementation):

```python
@dataclass(frozen=True)
class Derivation:
    relative: str      # "designs/catf_mfe/radial_build.sysml"
    owner: str         # "plasma_region" — the declaration block that owns it
    initializer: str   # "attribute outer_radius : Real = inner_radius + thickness;"

DERIVATIONS: dict[str, tuple[Derivation, ...] | None]
```

The owner anchor generalises the three existing entries too (`gamma_shield`, `catf_vacuum_vessel`,
`AlphaNeutronSplit`), so there is one matching rule rather than two.

**Anchor failures are reported problems, never skips.** The fail-closed property must not rest on an
unstated default. Three cases, each appending a problem naming the usage and the owner:

- the owning block's header is **not found** → *"owner block `<name>` not found in `<file>`"*;
- the header matches **more than once** → *"owner block `<name>` is ambiguous in `<file>`"*;
- the initializer appears **zero or more than once inside the block** → the existing not-found and
  not-unique messages, now scoped to the block rather than the file.

No file-wide fallback. A derivation the prover cannot anchor is a failure, not an unchecked row.

---

## The 27 derivations — concrete shape

Per layer, in place, keeping declaration order. Free root is `axis_region.inner_radius`.

```
    // Relation (undirected): plasma_region.inner_radius = axis_region.outer_radius (adjacent layers abut).
    // CHOSEN BASIS, not physics: the axis root radius and the 14 layer thicknesses are free; radii
    // derive outward. Authority: owner-disposition.md Group A, A5 (derive-instead).
    attribute inner_radius : Real = axis_region.outer_radius;  // m
    attribute thickness : Real = 1.1 [m];  // From line 74
    // Relation (undirected): plasma_region.outer_radius = plasma_region.inner_radius + plasma_region.thickness.
    // CHOSEN BASIS, not physics: inner_radius and thickness are free; outer_radius derives.
    // Authority: owner-disposition.md Group A, A6 (derive-instead).
    attribute outer_radius : Real = inner_radius + thickness;  // m
```

14 `outer_radius` derivations (every layer, including `axis_region` — the leg Item 5 left underived
is no longer a special case, per the spec's `[INHERITED]` item) and 13 `inner_radius` derivations.
The layer order is the spec's `[HARD]` list. One full basis paragraph is added once at the
`catf_radial_build` level stating the parameterization and citing the A5/A6 ruling.

---

## Expected-output derivation plan (SC-6)

Every value below is derived from the ruled table or read from authored source. Committed **before**
the confirmation run.

| # | artifact | change | derived from |
|---|---|---|---|
| 1 | `tests/expectations/constraint_population/catf_mfe_gated.json` | drop the `LayerContinuity` and `RadiusThicknessConsistency` rows; rename `PumpingSpeedConsistency` → `pumping_speed_agrees` and set its `source_line` | the ruled table (A5/A6 deleted, A9 renamed); the line number read from the edited source |
| 2 | `tests/expectations/gated_manifest/catf_mfe_gated.json` | `carrier_total` 58→**56**, `deletion_total` 7→**9**, `matched_by_name` 56→**53**, `matched_by_renamed_from` 2→**3**, `assessed_entry_count` 2→**3**; add A5/A6 deletion records (d5 lines 612, 630 per `PROVENANCE.md:209`); add A9 to `renamed_carriers`; histogram → `{eligible 3, excluded 0, non_reaching 53}`; coverage account → `56/3/3/0/0/{}`; `gates_satisfied` gains A9 **and its `_note`**, which says *"both gates satisfy at 20000"* and is stale at three; rewrite `histogram_rows`; correct the `.project/active/…` citations in `_comment` and `_basis` to `completed/` | the ruled table's arithmetic, restated in the spec |
| 3 | `tests/unit/data/expected-coverage.md` | ledger row → `catf_mfe_gated \| 56 \| 3 \| 3 \| 0 \| 0 \| {} \| complete \| violation \| 3`; prose section re-derived (3 asserted executing + 5 B-guards + 48 Group C = 56); "Why `assessed_entry_count` is 2" → 3 | the ruled table; the 3+5+48 split |
| 4 | `scripts/check_gated_manifest.py` | module docstring `65 = 58 + 7` → `65 = 56 + 9`; `DERIVATIONS` extended per D5 | the restated identity |
| 5 | `tests/conformance/test_gated_manifest_identity.py` | `58/7/56/2` → `56/9/53/3`; deletion-row set gains `A5`, `A6`; add per-occurrence falsification cases | the restated identity |
| 6 | `tests/fixtures/catf_mfe_gated/PROVENANCE.md` | retire `blocked-by-defect` (§3a); add D8/D9; restate the identity; three §5 edits incl. an A9 subsection and this design's D3 record; the float-drift record; **SC-3 side 1 in §3b** — full list below | the ruled table + Item 8's fix commit + the owner's SC-3 ruling |
| 7 | `tests/fixtures/catf_mfe_gated/instance_graph_snapshot.json` | re-captured under license | the edited sources — a **capture, not an expectation** (see below) |
| 8 | `.project/backlog/BACKLOG.md` | one-line amendment to `[INLINE-PREDICATE-MARKER-DROP]` (N-4 **side 2**) | the owner's SC-3 ruling |
| 9 | `.project/backlog/BACKLOG.md` | **new** unowned entry recording `ProductWithinBand`'s per-dimension cost | this design's NOTE |

**Row 7 is a capture, not an expectation.** The snapshot is bytes read out of the edited sources by
`sysml-codegen snapshot`, not a number derived from the ruled table. Committing it in the same pass
as the expectations does not violate SC-6, and this sentence exists so a later auditor reading the
commit order does not mistake it for a run feeding an expectation.

**Row 9, phrased as a decision record** (capture-fidelity law 3 — not an instruction to future
agents): a constraint port takes its unit from the formal's own declaration, so a unit-carrying
constraint form is authored per dimension. `ProductWithinBand` is therefore m³/s-specific, and a
product band over a different dimension needs its own definition. Recorded as a platform gap the
fixture absorbs, unowned. Without this line the cost lives only in this design, which archives.

**`assessed_entry_count = 3`** because each of A2, A3 and A9 hangs off a part with one occurrence
(`catf_physics` ×2, `catf_vacuum_pumping` ×1), so each eligible usage mints one concrete entry.

**Module count is measured, not pre-committed.** Recorded where it appears (PROVENANCE's measured-shape
paragraph). The probe measured **62**; the implement stage re-measures and records what it gets.

**PROVENANCE edits, all in one pass** (capture-fidelity law 3 — amend, do not annotate).

> **Naming caution.** `PROVENANCE.md` §5 is headed *"Per-gate unit reasoning (D3)"*, where `D3` is
> **Item 5's** design decision. It is unrelated to **this** design's D3 (`tf_coil.thickness`'s
> comment). Both appear below; do not conflate them.

*Amend what has gone false:* the measured-shape paragraph; §1's *"`ProductWithinBand` is
deliberately not authored"*; §1's *"A5, A6, A9 are left exactly as `catf_mfe_d5` wrote them"*; §1's
*"the axis-region layer is not derived"*; §2's heading and identity (`65 = 58 + 7` → `65 = 56 + 9`);
§3a's parked-row block, retired with a citation to Item 8's fix commit `62a07e5`; and the Authority
block's *"SC-3's identity is `65 = 58 + 7`"* — note that this `SC-3` is **Item 5's** third success
criterion, not the epic's SC-3 that N-4 parks, so amend the number and leave the reference alone.

*Add:* deletion records **D8 (A5)** and **D9 (A6)**, each carrying the relation, the chosen basis,
and the authorizing row. A record that A9 re-enters the SC-5 candidate set — a record, not a
re-disposition; SC-5's anchor stays A2.

*§5, the fixture's live home for the human unit claim* — three edits, not one:

- **(a)** `:345`'s *"Both gates take the dimensionless, unit-blind library band"* goes stale. There
  are three gates after A9, and A9's band is **not** unit-blind — its formals carry unit text.
- **(b)** A new **A9 subsection**, matching the shape of A2's (`:350`) and A3's (`:359`), carrying
  the ruled unit-check cells: m³/s on both compared sides, `count` dimensionless, `rel_tol`
  dimensionless (`owner-disposition.md` A9 unit-check column). This is the human checkpoint the
  ruled table assigns to design review; it was met in this item's review against authored source and
  needs a live home.
- **(c)** `:345-348`'s claim that *a constraint formal cannot carry unit text at all* is now false in
  its premise — Item 8 made formals carry unit text via comments — while its prediction (one
  definition per dimension) came true. Amend accordingly, and record **this design's D3**: the
  `tf_coil.thickness` comment edit, what changed, that the original provenance text (`from line 83
  (= tf_dr)`) was preserved inside the amended comment, and why it was necessary — the
  computed-attribute lane reads the consumed attribute's own declaration, so an unreadable unit
  there refuses the model. This is the item's only source edit outside the ruled 27; §5 is where a
  unit-annotation edit belongs, and it must not live only in this design, which archives.

*§2 or §5, wherever the deletion records sit best — the float-drift record* (Major 5, capture-fidelity
law 4). Written where a later reader looks, not only in this design: the derived chain reproduces the
authored literals decimally but not bit-exactly; `vacuum_gap`, `first_wall`, `blanket` and
`reflector` outer radii drift by −8.88e-16 m and the inner radii that read them follow; the chain
re-converges at `ht_shield.outer_radius`; `bioshield.outer_radius` is exactly `8.55` and the
`tf_coil` legs are exact, so the 16-digit `cooling_power` figure is untouched; **no generated byte
changes**, so this can only appear at execution. State plainly that an execution expectation moving
is **the surfacing event, not a number to absorb**.

*§3b — SC-3's first side* (N-4.1). §3b already holds the B1–B5 markers and their held intent, so it
is the natural home. Record that the epic's third success criterion is a **conditional that does not
fire in this run**, naming `[INLINE-PREDICATE-MARKER-DROP]` as the trigger and stating that the five
markers stay recorded here until it closes. Side 2 is the backlog amendment (row 8); this is side 1,
and without it a stated success criterion ships half-met.

**Before/after public key set — derived from source, then confirmed by the probe.** Both numbers
read off the authored model, so they belong in this section rather than beside the measured module
count:

- **26 leave.** A radius is a `DESIGN_ATTRIBUTE` key today only if some calc consumes it. 13 of the
  14 layers carry `calc minor_calc : TorusMinorRadius` binding both radii; `axis_region` carries no
  geometry calc at all (`radial_build.sysml:57-75`). So 13 × 2 = 26 radius keys exist, and all 26
  become channels. The 27th derived radius, `axis_region.outer_radius`, was never a key — which is
  the same 26/27 split Item 5 measured when it found 26 of 27 refusing.
- **16 arrive.** The derived `outer_radius` consumes its layer's `thickness`, minting 14 thickness
  keys of which `tf_coil.thickness` was already one (via `magnet_surface_calc`) → 13 new; plus
  `axis_region.inner_radius`, the free root, now consumed by its own derived `outer_radius`; plus
  A9's `pump_capacity_each` and `pumping_speed_agrees__rel_tol`. 13 + 1 + 2 = 16.

There are **15 free radial parameters** (the axis root radius plus 14 thicknesses); 14 of them
arrive as new keys and `tf_coil.thickness` was already one. Correct the spec's phrasing that the
free parameters "stay keys" — they overwhelmingly *arrive*. Direction of the movement is as ruled.

---

## Probe result

Full detail and scripts: `probes/RESULTS.md`. Run licensed, on the correct interpreter, through
the public generate route, on throwaway copies. Summary:

- **First attempt refused.** Ruled forms authored without unit annotation →
  `SI_RENDERING_COLLISION` on exactly three keys, `unit_text` the only differing field:
  `tf_coil__thickness` (`None` vs `'m'`), `n_pumps` (`'Dimensionless'` vs `None`),
  `pumping_speed_total` (`'m³/s'` vs `None`). Each ruled form refuses independently; the unedited
  fixture generates cleanly, so the authoring introduced them.
- **Cause measured, and it is the reverse of the natural guess.** The calc lane reads units
  correctly; the lanes I authored read `None`. A port's unit comes from the formal's own
  declaration. Item 8 is not incomplete — its refusal caught two genuinely unlabelled declarations.
- **After D2 and D3, full generation completes**: 62 modules, 58 stencils, 9 parameter groups, all
  five preflights pass, package sealed. `constraint_name_safety` did not fire. Minted ports carry
  the authored text (`m³/s`, `Dimensionless`, `m`). **No cross-part collapse** — all 13
  sibling-reaching initializers wire correctly on the bare spelling.
- **Measured shape confirms the spec's pre-committed numbers exactly**: coverage
  `56/3/3/0/0/{}/complete`, histogram `{eligible 3, non_reaching 53}`, 56 catalog rows.
- **Per-occurrence anchoring validated** — locating each layer by its `part` header and requiring
  exactly one matching declaration inside succeeded for all 27.

---

## Potential Risks

- **Float drift — surfaced, not absorbed.** The spec's `[HARD]` claim that the derivations reproduce
  the authored literals "exactly" holds decimally but **not** in IEEE-754. Four layers drift by one
  ULP (−8.88e-16 m): `vacuum_gap`, `first_wall`, `blanket`, `reflector` outer radii and the inner
  radii that read them. The chain re-converges at `ht_shield.outer_radius`; `bioshield.outer_radius` is exactly
  `8.55`; the `tf_coil` legs are exact, so the manifest's 16-digit `cooling_power` figure is
  untouched. No generated byte changes — this can only appear at execution, in volumes downstream of
  those five layers. **Recorded for the owner under capture-fidelity law 4, in the fixture's
  `PROVENANCE.md`** — not only here, because this document archives with the item and the later
  reader opens PROVENANCE. Mitigation: do not re-baseline anything on it; if an execution
  expectation moves, that is the surfacing event the spec describes, not a number to absorb.
- **Snapshot re-capture is unproven.** The probe drove `generate --models`; it did not run
  `snapshot` + `generate --from-snapshot`. Item 8 routed projectability certification through
  `snapshot/envelope.py`, so a lane disagreement would surface there as
  `SnapshotCertifiabilityError`. Mitigation: re-capture early in implement, before the expectations
  are committed, so a refusal is cheap. Also expect `captured_at` churn on re-capture.
- **The `expected-coverage.md` ledger is parsed, not transcribed.** A malformed row fails the whole
  suite loudly (`test_coverage_ledger_agreement.py:47-51`). Nine columns exactly.
- **D3 is an edit outside the 27.** It is required for A6 to build, and it is flagged rather than
  buried: reviewed and ratified at design review, and recorded in the fixture's `PROVENANCE.md` §5
  so the record outlives this document. If the owner reads it as unauthorised, the alternative is to
  surface the refusal instead — but the ruled form then cannot land.
- **Concurrency on `BACKLOG.md`.** Clean at design time; re-check immediately before the edit and
  defer the line if a foreign edit appeared.

## Integration Strategy

This replaces nothing structural. It brings one fixture into line with a ruling already made, and
extends one prover so the strongest of its claims is gated per occurrence rather than per file. The
disposition vocabulary, the catalog schema, the coverage machinery and TEAx are all untouched.

## Validation Approach

1. `scripts/check_gated_manifest.py --check` reports `65 = 56 carriers + 9 named deletions`, with
   `53` by name and `3` by `renamed_from:`.
2. `tests/conformance/test_gated_manifest_identity.py` green, including new **occurrence-scoped**
   falsification cases. Both must name the occurrence, and both must mutate one block only:
   - strip **`blanket`'s `outer_radius`** comment block → exactly **one** problem, naming that
     derivation and both missing statements. Each layer now carries *two* comment blocks, one per
     derivation, so the case has to say which.
   - remove **`blanket`'s `outer_radius`** initializer → exactly **one** problem, "not found".

   The existing missing-derivation case uses an unbounded `str.replace`
   (`test_gated_manifest_identity.py:143-147`). Against `radial_build.sysml` that would delete all
   14 identical A6 lines and yield 14 problems, not one. The new cases must replace **within the
   owning block's line range**, or pass `count=1` against a block-unique anchor.
3. Licensed suite green with **zero license-skip lines**, on
   `/home/reid/1cfe/item7-rebuild-venv/bin/python -m pytest`.
4. `git diff --stat` names no file under the two frozen twins or the archived acceptance item.
5. The generated package builds and seals; the recorded key movement is exactly the 26/16 sets
   derived above.
6. **SC-3 is recorded on both sides.** `PROVENANCE.md` §3b names the epic's third criterion a
   not-fired conditional with `[INLINE-PREDICATE-MARKER-DROP]` as its trigger, and the backlog
   entry's closing sentence says that closing the defect fires the B1–B5 marker migration. Grep both
   for the defect name and read them; neither side may be missing.
7. `PROVENANCE.md` §5 carries an A9 subsection, and the float-drift record is present and findable.

## Next-Stage Handoff

**Fixed** — A9's authored predicate and bindings, verbatim above; the 27 derivations' shape and
order (D4, D6, D7); the unit spelling (D1, D2, D3); the prover's owning-block anchoring and its
three anchor-failure cases (D5); the expectation table above, including the PROVENANCE edit list and
both sides of SC-3; the sequence (source → read line numbers → commit expectations → run).

**Open** — the exact `DERIVATIONS` literal and the prover's block-scanner implementation; the final
module count (re-measure, do not copy 62); whether snapshot re-capture perturbs anything beyond
`captured_at`.

**De-risk first** — snapshot capture and re-seal, before any expectation is committed. It is the one
lane the probe did not exercise, and it is the cheapest place left for a refusal to hide.

---

**Next Step:** fresh-session `/_my_design_review`, then `/_my_plan`.
