# Design Review: Part-Instance Index — Subtype Closure and Cardinality Expansion

**Design:** `.project/active/part-instance-index/design.md`
**Spec:** `.project/active/part-instance-index/spec.md`
**Review File:** `.project/active/part-instance-index/design-review.md`
**New evidence folded in:** `.project/active/part-instance-index/b1-probe-evidence.md`
**Date:** 2026-07-12

---

## Fundamental Assessment

**Sound.** The approach is right and the design does not over-reach.

The core move — a **second, structure-only enumerator that runs beside calc-driven discovery,
never through it** — is exactly what the spec asks for and what S3 proved live (9/9 with zero
calculations). The three composed facts (subtype closure over a source owner, structured
per-step paths, fail-closed cardinality) each map to a specific spec success criterion, and each
is backed by code I verified, not asserted:

- Subtype closure: `_supertype_closure` (`usage_extractor.py:197`) dedups and terminates on
  diamonds (the `if super_qn not in closure` guard before `stack.append`, line 215). The closure
  direction is correct — `owner ∈ _supertype_closure(candidate)` selects candidates that are
  *subtypes* of the owner, matching the probe (`probe_instance_index.py:96-99`).
- Structured walker over `_build_part_usage_index`: the flat finder keys multiplicity by bare
  leaf name (`probe_instance_index.py:81`), which provably collides — success criterion #2. A
  walker retaining `(owning_def_qn, feature_name)` per step is the minimum that fixes it. It also
  earns its place for intermediate-container multiplicity, which the flat one-path-per-usage
  finder cannot express.
- Additive boundary: the module is imported by nothing this item, reuses helpers read-only. INV-1
  is honestly stated.

The capture-fidelity handling is good: the `[HARD]` "no new SysIDE facts" vs Design Principle 5
tension is **surfaced, not resolved silently** (design Surfacing note), and the B1 probe the
design demanded has now retired that risk in the design's own favor.

So this is not Rework. But the design was written **before** the B1 evidence existed, and the
cardinality gate — the load-bearing core — is specified in terms that **contradict the now-proven
API**. Taken literally, the gate blocks the simplest fixed `[3]`. That plus two under-specified
identity/dedup details are the must-fixes below. The foundation stands; the gate mechanics must be
re-pinned to the evidence table before implementation.

---

## Dimensional Review

### 1. Spec Compliance
**Assessment:** Concerns

Every spec success criterion has a design element, and the provenance is carried faithfully
(the `[HARD]` gate requirement, the `[INHERITED]` closure reuse, the `[INFERRED]` one-entry-per-
occurrence all land in D3/D5/INV-4). But **the gate as written fails the very criterion it
targets** — see Critical #1. And two criteria have **no listed test**:

- Criterion #2 (collision) — covered (Validation #2).
- Criterion #3 (blocking) — covered for the parameterized case (Validation #3), and the design
  correctly defers the ordered/unbounded live-range test to "once B1 is confirmed" (now is).
- **Intermediate / nested-multiplicity (the Cartesian product, `Bank[2]` × `member[3]` = 6)** —
  asserted "handled by construction" (Architecture step 3; Potential Risks) but **absent from the
  Validation Approach list**. "By construction" without a test is exactly where a Cartesian-walk
  off-by-one hides. Must add.

### 2. Pattern Consistency
**Assessment:** Pass

Placement in `analysis/` beside `dependency_backtracker` / `parameter_groups` is correct (derived
analysis over extraction output). The named-`Exception`-at-the-broken-invariant convention
(`MissingCalcDefError`, `CircularDependencyError`) is followed by `NonFiniteCardinalityError` (D4).
Sorting keys by QN string to avoid `heritage`/`types` iteration-order dependence mirrors
`most_specific` (`usage_extractor.py:233-235`). No new pattern invented where an existing one fits.

### 3. Abstraction Quality
**Assessment:** Pass

The three new types (`PathStep`, `InstanceOccurrence`, `NonFiniteCardinalityError`) each earn
their place: `PathStep` carries the per-segment owner the flat string discards, `InstanceOccurrence`
is the structured identity Item 5 needs to wire siblings, the error is the fail-closed diagnostic.
The classifier-as-pure-function (`(usage_node, owning_def, feature) -> Fixed|NonFinite`) is the
right seam for a directly-unit-testable truth table. Nothing here is speculative generality.

One simplification worth weighing (not a blocker): see Major #2 — the classifier takes
`list[MultiplicityData]` and cross-checks, but B1 proves the live node alone is sufficient *and*
mandatory, so the `MultiplicityData` dependency may be dead weight that also introduces a
missing-data ambiguity.

### 4. Duplication Avoidance
**Assessment:** Concerns

The new walker deliberately duplicates the recursion shape of `_find_instantiation_paths`
(`usage_extractor.py:313-369`) rather than refactoring a shared core — a **conscious** choice (D2,
Implementation Notes) to protect INV-1 byte-identity. That is the right call for this item: a
shared-core refactor would risk perturbing calc discovery. Flagging only so it is a recorded
decision, not accidental drift: the two recursions must be kept in sync by humans, and the walker
must replicate the `_visited` cycle guard (line 335-337) or it infinite-loops on cyclic
containment. Worth an explicit implementation note.

### 5. Data Structure Clarity
**Assessment:** Concerns

`PathStep` / `InstanceOccurrence` are explicit frozen dataclasses — good. But
**`InstanceOccurrence.part_def_qn` is under-specified and collides with the D7 dedup** for
double-keyed retyped usages. See Critical #3. The field is commented "concrete type instantiated
(may be a subtype)" but the data-flow (Architecture step 2, "for each applicable type") does not
say whether the field is set from the *closure-entry* type or the *usage's own* type — and those
differ precisely for the retyped case the item exists to handle.

### 6. Route Safety
**Assessment:** Pass

The gate is fail-closed by construction: expand only on positively-confirmed single literal;
every other shape raises. No catch-all "reduced set" arm (INV-2). The `NonFiniteCardinalityError`
raise-site reasoning (D4: in the index, not extraction, because extraction is shared with corpus
generation and the real corpus has `[module_count]` everywhere) is correct and load-bearing for
INV-1 — raising at extraction would break byte-identity the moment a corpus model has a
parameterized multiplicity.

### 7. Bets & Decisions Integrity
**Assessment:** Pass (with the B1/B2 bets now converted to facts)

B1 and B2 were genuine bets with honest "if false → what fails" clauses, and the design correctly
gated the classifier behind a de-risk spike. The orchestrator's B1 probe has now **confirmed
both**. Post-evidence:

- B1 holds — the live node positively identifies a fixed literal (`upper_bound` = `LiteralInteger`),
  and ordered/nonunique live on the **usage** (`is_ordered` / `is_nonunique`), not the range node.
- B2 holds *stronger* — a parameterized `[n]` resolves its default into `cached_upper_bound`
  (non-`None`), so any gate keyed on cached counts or `MultiplicityData` presence silently expands
  the default. Node-type dispatch on `upper_bound` is mandatory.
- B3 (closure finds every constraint-only instance) — S3 confirmed 9/9.
- B4 (retyped double-keying is the only duplicate source; canonical-path dedup is complete) — this
  is the one bet the evidence does **not** fully settle. It is correct that double-keying reaches
  the same occurrence twice, but B4 is entangled with the unspecified `part_def_qn` (Critical #3):
  dedup is only complete if the dedup key is entry-independent. Pin #3 and B4 becomes true; leave
  it and B4 can drop the correct concrete-type record.

Hidden bet surfaced: the design assumes the D6 sort key `(tuple(segment_names), tuple(indices))`
is a total order over Python's mixed `None`/`int` `occurrence_index`. It is safe *only because*
equal `segment_names` imply the same feature and therefore aligned `None`/`int` at each index
position — so `None < int` (a `TypeError` in Python 3) never actually gets compared. That is a
real, unstated invariant the sort rests on. See Minor.

### 8. Reader Comprehension
**Assessment:** Pass

The Core Concept gives the mental model first (structure-only enumerator; three composed facts)
before mechanism, and "silence is never an outcome" anchors the fail-closed principle plainly. The
Surfacing note states the tension in the reader's terms. A tired engineer can skim this and know
what the system is and why. The one comprehension gap is that the gate's prose ("bounds present,
lower == upper") now describes an API that the B1 table contradicts — a reader trusting the design
text would build the wrong gate. That is Critical #1, not a style nit.

---

## Issues by Severity

### Critical (must address before implementation)

- **C1 — The D3 cardinality gate is specified against an API the B1 evidence disproves; taken
  literally it blocks fixed `[3]`.** D3 says expand iff "bounds present, lower == upper, bound is a
  literal, not ordered/nonunique." The B1 table shows fixed `Leaf[3]` presents as **`lower_bound`
  node `None`, `upper_bound` node `LiteralInteger(3)`, cached `3 / 4`** (upper exclusive). So:
  "bounds present" (both nodes) is false — `lower_bound` is `None`; and "lower == upper" on cached
  values is `3 == 4` → false. Either literal reading **blocks `[3]`**, breaking success criterion #1.
  *Why load-bearing:* the gate is the item's entire guarantee, and its written mechanics contradict
  the proven surface. **Fix:** re-pin to the node-type dispatch the evidence mandates (evidence
  consequence 1–2):
  - `upper_bound` node is `LiteralInfinity` → **block** (`[*]`).
  - `upper_bound` node is `FeatureReferenceExpression` (referent an attribute) → **block**
    (parameterized `[n]`; `count_attribute_name` non-`None`).
  - `upper_bound` node is `LiteralInteger(u)`:
    - `lower_bound` node `None` → **admit**, count = `u` (bare `[u]`).
    - `lower_bound` node `LiteralInteger(l)` with `l == u` → decide per C2 (`[u..u]`).
    - `lower_bound` node `LiteralInteger(l)` with `l != u` → **block** (`[0..5]`).
  - `usage.is_ordered` or `usage.is_nonunique` → **block** (read off the **usage**, not the range
    node — the design text that says the gate "reads the live multiplicity range node" for ordered
    is wrong; the classifier signature already takes `usage_node`, so this is a text/logic fix, not
    a signature change).

- **C2 — `[3..3]` is not pinned.** The brief explicitly requires an admit-or-block decision, and
  the B1 table flags it as a new edge (`range33`: `lower_bound` `LiteralInteger(3)`, `upper_bound`
  `LiteralInteger(3)`). The design never mentions it. *Why load-bearing:* it is a live shape the
  gate will hit, and an unpinned branch is exactly a silent-behavior risk. **Fix:** record the
  decision (evidence recommends **admit as fixed-3**, since it is semantically identical to `[3]`)
  and add a test.

- **C3 — `InstanceOccurrence.part_def_qn` derivation and its interaction with D7 dedup is
  unspecified for double-keyed retyped usages, and can drop the correct concrete type.** The
  retyped `part :>> leaf : SpecializedLeaf` is keyed in `_build_part_usage_index` under **both**
  `SpecializedLeaf` (owned typing) and its preserved supertype `ConstrainedLeaf` (`.types`;
  `usage_extractor.py:283-289`). The walker therefore reaches the same `leaf` usage from **two**
  closure-entry types. If `part_def_qn` is set to the closure-entry type and the D7 dedup key is
  "steps only," the two records have identical steps but `part_def_qn ∈ {ConstrainedLeaf,
  SpecializedLeaf}`; whichever survives dedup is arbitrary, and `ConstrainedLeaf` (sorts first) can
  win — recording the **supertype as the concrete type instantiated** and dropping the correct
  `SpecializedLeaf`. *Why load-bearing:* it makes B4's "dedup is complete" false and hands Item 5 a
  wrong occurrence type. **Fix:** define `part_def_qn` as the **most-specific user type of the
  usage node itself** (via `most_specific`, `usage_extractor.py:221`), entry-independent; keep the
  dedup key entry-independent (steps, or steps + that usage-derived `part_def_qn`). Then both hits
  produce an identical record and collapse cleanly. Note: the plain `plain_subtype : SpecializedLeaf`
  is *not* double-keyed (single owned typing, no preserved supertype), so it is unaffected — the
  bug is specific to retyped/redefined usages.

### Major (should address)

- **M1 — Intermediate / nested-multiplicity (Cartesian) has no test.** Architecture step 3 claims
  `Bank[2]` × `member[3]` = 6 "by construction," and Potential Risks says "the fixture must cover
  it," but the Validation Approach list (#1–#6) never enumerates it. Add a multiplicity-on-an-
  intermediate-container case and a multiplicity-under-a-subtype case to the promoted fixture, and
  assert the exact product and per-member indices.

- **M2 — Reconsider whether the classifier needs `MultiplicityData` at all.** B1 proves the live
  `upper_bound` node yields both the finiteness verdict *and* the count directly. B2 proves
  extraction *omits* non-fixed shapes, so a `MultiplicityData` cross-check is absent exactly for the
  shapes we most want to pin (and may be absent for `[3..3]`). As written, "cross-checks the literal
  count against the matching `MultiplicityData` for consistency" is ambiguous about the
  missing-data case: if a missing match is treated as an inconsistency, it wrongly blocks. Cleaner:
  make the **live node authoritative and sole**, drop `MultiplicityData` from the classifier, and
  if you keep it, state explicitly that a missing `MultiplicityData` is **not** a block.

### Minor (consider addressing)

- **m1 — D6 sort-key mixed `None`/`int` is safe only by an unstated invariant.** `(tuple(segment_names),
  tuple(indices))` compares `indices` only when `segment_names` are equal, which guarantees aligned
  `None`/`int` positions, so `None < int` never triggers. True, but fragile — add a one-line note,
  or normalize `occurrence_index` to a sortable sentinel, so a future edit that changes the key
  order can't introduce a `TypeError`.

- **m2 — Walker must replicate the `_visited` cycle guard.** "Copy the recursion shape" (D2) should
  call out the `_visited` set (`usage_extractor.py:335-337`) explicitly; omitting it infinite-loops
  on cyclic part containment.

- **m3 — Text fix:** the design says ordered is read from "the live multiplicity range node"; the
  B1 evidence places `is_ordered`/`is_nonunique` on the **usage**. Correct the prose (mechanics are
  fine — the classifier already receives `usage_node`).

---

## Recommendations

1. **Rewrite D3 to the node-type-dispatch gate the B1 table proves (C1)** — this is the one change
   without which the module ships broken. Fold the `[3..3]` decision (C2) into the same rewrite.
2. **Pin `part_def_qn` to the usage's own most-specific type and make the dedup key
   entry-independent (C3)** — closes the only real gap in B4.
3. **Add the Cartesian / intermediate-multiplicity test and the `[3..3]` test (M1, C2)** to the
   promoted fixture; they cover the two behaviors currently asserted-not-tested.
4. **Decide the `MultiplicityData` dependency (M2)** — prefer dropping it for a live-node-only
   classifier; if kept, specify missing-data is not a block.
5. Minor: sort-key note (m1), `_visited` guard note (m2), ordered-marker prose (m3).

The de-risk spike the design's Handoff demands is **already done** (B1 evidence). The plan should
cite that evidence and skip re-spiking; the classifier can be written directly against the table.

---

## Resolutions

_Filled in during Stage 4 — the design agent reads this section to incorporate the review._

---

**Overall:** Approved-with-must-fixes

The approach, module boundary, closure reuse, fail-closed principle, and additive guarantee are
all correct and evidence-backed — not Rework. But three must-fixes gate implementation: the D3
gate must be re-pinned to the confirmed B1 API (C1) and `[3..3]` decided (C2), and `part_def_qn` /
D7 dedup must be specified so a double-keyed retyped usage yields one correct record (C3). M1's
missing Cartesian test and M2's `MultiplicityData` question should be resolved in the same pass.

**Next Steps:** Record resolutions above, then re-run `/_my_design` (or return to the design-agent
session) and point it at this review to incorporate. The reviewer does not edit the design. Because
the B1 de-risk is already complete, the corrected design can proceed straight to `/_my_plan` /
`/_my_implement` after the must-fixes land — no further spike.
