# Design Review: Snapshot v3 — Constraint Facts Load-Bearing

**Design:** `.project/active/snapshot-v3/design.md`
**Spec:** `.project/active/snapshot-v3/spec.md`
**Review File:** `.project/active/snapshot-v3/design-review.md`
**Date:** 2026-07-12
**Reviewer posture:** skeptical; verified every load-bearing claim against `snapshot/`, `analysis/constraint_lowering.py`, `analysis/part_instance_index.py`, `orchestration/pipeline_builder.py`.

---

## Fundamental Assessment

**Sound.** The core shape is right and I could not find a materially simpler design that meets the spec.

- **Re-derivation, not carriage.** The design correctly refuses to carry the `ConcreteConstraint` catalog (the S3 CF(2) trap) and instead carries the two identity-bearing *inputs* — the neutral facts and the resolved occurrence table — then runs the real `lower_constraints()` offline. Verified: the only live-model dependency in lowering is `occ_index.occurrences_of`, called at `constraint_lowering.py:350` inside `_expand_owner_instances`, and only for `part_def` owners. `FrozenOccurrenceIndex` exposing just `occurrences_of` is the minimal offline stand-in. B1 holds.
- **Offline inputs already exist.** `build_classifier_inputs_from_snapshot` (`graph_rebuild.py:26`) already rebuilds `registry`, `design_attrs` as `dict[Path, list[DesignAttributeData]]` (`:100`, the shape `lower_constraints` wants), `group_deriver`, and materializes supplied values — so the constraint phase genuinely joins the end of existing re-derivation, not a new pipeline.
- **Grandfather via a loud marker, not an empty section.** Correctly rejects writing an empty facts section for the `gain`-blocked pair (dishonest, indistinguishable from constraint-free, violates the round-trip `[HARD]`). The marker decouples "facts present" from "lower offline," which is what lets both flip surfaces move in one atomic change.
- **Rejection reuses the version hard-gate idiom** (`loader.py:127-140`, `_require(raise_on_missing=True)`) — the right precedent, and correctly refuses the `compilation_results` degrade-with-warning path.

The approach is not over-engineered: `FrozenOccurrenceIndex` is the only new type, and it earns its place (offline has no live model to answer `occurrences_of`). Proceed to detailed review.

The must-fixes below are **completeness and determinism holes inside a sound design**, not a flawed foundation.

---

## Dimensional Review

### 1. Spec Compliance
**Assessment:** Concerns

Every spec requirement maps to a design element, and provenance is carried faithfully (the `[INFERRED]` occurrence-serialization decision is recorded as a decision with its rejected alternative; the `gain` handoff is a named Item-14 prerequisite, not a silent deferral). Two gaps:

- **The spec's "both rejection cases fire loudly" is only partly met.** The design's new gate (D5) guards `constraint_facts` presence only. But a v3 snapshot carries **three** new load-bearing keys (`constraint_facts`, `part_occurrences`, `constraint_lowering_mode`), and the loader reads all three. A partial/torn v3 snapshot missing `part_occurrences` or `constraint_lowering_mode` passes the gate and then raises a raw `KeyError`, not a `SnapshotFormatError` with a re-capture message. See Must-Fix 1.
- **The expected-diff enumeration (spec [INFERRED] class 2) names only the facts section.** The design adds three sections. If the re-capture review procedure whitelists only "new facts section," `part_occurrences` and `constraint_lowering_mode` show up as diffs "outside the set → investigated." Minor — extend the enumeration (Nice-to-have 2).

### 2. Pattern Consistency
**Assessment:** Pass

Reuses `_serialize_value` for the occurrence table (no hand-rolled dicts — correct, `InstanceOccurrence`/`PathStep` are plain frozen dataclasses), the `_require`/version-gate raise idiom, and mirrors the live P1/P3 threading offline. The `PROFILE_SEMANTIC_VERSION` code-pin assert (`constraint_lowering.py:463`) is the right precedent for the new `EXPRESSION_IR_SCHEMA_VERSION` code-pin — verified both constants exist (`constraint_facts.py:39`, `expression_ir.py:38`).

### 3. Abstraction Quality
**Assessment:** Concerns

`FrozenOccurrenceIndex` is a clean, well-scoped abstraction. The concern is `resolve_owner_occurrence_table`: it is a **second owner-selection path** that must stay in lockstep with what `lower_constraints` actually queries, forever. The design describes it as "iterates the `part_def` owner EQNs" — but lowering queries `occurrences_of` only for owners that are `part_def`-kind **and** `Eligibility.ADMIT` (`constraint_lowering.py:490-545`; the P1 comment at `pipeline_builder.py:854-856` confirms "a non-admitted usage catalogs unassessed, never reaching the strict resolver"). That mismatch is Must-Fix 3, and the cleanest resolution removes the second path entirely.

### 4. Duplication Avoidance
**Assessment:** Concerns

Same root as Dimension 3: `resolve_owner_occurrence_table` duplicates the owner-selection logic embedded in `lower_constraints`'s main loop. Two independent implementations of "which owners does lowering query" will drift. Capturing the table as a byproduct of the lowering call (the index records the keys it was asked for) removes the duplication and makes B5 true by construction instead of by matching two code paths.

### 5. Data Structure Clarity
**Assessment:** Concerns

The three-key format is explicit and typed. Two clarity gaps:

- **`part_occurrences` key ordering is unpinned** — a byte-identity hazard, because `snapshot_to_json` does not `sort_keys` (`serializer.py:200`). See Must-Fix 4.
- **The mode × section matrix is left implicit.** The reader must infer behavior for every combination of `mode ∈ {applied, grandfathered_off, <corrupt>}` × facts `{present-nonempty, present-empty, absent}` × occurrence-table `{present, absent}`. The corrupt-mode cell is a live silence-trap bug (Must-Fix 2); pinning the full matrix in the design would have surfaced it.

### 6. Route Safety
**Assessment:** Fail

This is the design's weakest dimension and the source of the two most serious must-fixes.

- **A catch-all fall-through on `constraint_lowering_mode`.** The offline dispatch is `if mode == "applied" and facts.usages: lower`, with the grandfather WARNING gated on `mode == "grandfathered_off"`. Any other string — a hand-edited or torn `"appplied"`, `""`, `"off"` — matches neither branch: lowering is silently skipped and **no** warning fires. An asserting model then generates an assertion-free graph. That is exactly the silence trap the spec forbids (concept line 66). Must-Fix 2.
- **Unguarded key reads** after a gate that checks only one of three keys. Must-Fix 1.

Both are "ambiguous routing masks a corruption" failures — the dimension's core risk.

### 7. Bets & Decisions Integrity
**Assessment:** Concerns

The bets are genuine reality-claims, each with an honest "if false." B1, B3, B4 verified sound against the code. But:

- **B5 is stated imprecisely and is false as written.** "The set of owner QNs lowering queries is exactly the `part_def`-kind owning-definition QNs in the facts." Lowering queries `part_def`-kind **AND `Eligibility.ADMIT`** owners. The gap is not academic: an unassessed (non-`ADMIT`, non-`BLOCK`) `part_def`-owned usage whose owner has non-finite multiplicity would make `resolve_owner_occurrence_table`'s `occurrences_of` raise `NonFiniteCardinalityError` and **halt capture**, where live lowering skips that usage and succeeds. Tighten B5 and the helper (Must-Fix 3).
- **A hidden bet: `part_occurrences` key order is deterministic across captures.** Never stated; it rests on how the helper iterates owners. If it dedups via a `set`, str-hash randomization churns the section every re-capture. Surface and pin it (Must-Fix 4).
- Decisions D1–D6 each name their rejected alternative with a reason — good. D2's reasoning ("a per-owner query raises at capture, so no blocked entry reaches a valid snapshot") is correct *for `occurrences_of`'s non-finite raise*, but note `occurrences_of` returns `[]` (does not raise) for a zero-instance owner; the "no concrete instances" raise lives in `_expand_owner_instances` (`:357`), which the helper bypasses. Harmless for sufficiency (an empty list is just never queried), but the D2 claim is slightly overstated — see Must-Fix 3.

### 8. Reader Comprehension
**Assessment:** Pass

The "Core Concept" section builds the model well: capture the answers, not the capability; re-derive from carried inputs; the marker decouples the two flip surfaces. A tired engineer can get the shape in one read. The one comprehension cost is the implicit mode×section matrix (Dimension 5) — a table would help, and would have caught Must-Fix 2.

---

## Issues by Severity

### Critical (Must address before implementation)

- **MF1 — The missing-section gate guards only `constraint_facts`; `part_occurrences` and `constraint_lowering_mode` are unguarded.** [Route Safety / Spec] A v3 snapshot missing either of the other two keys passes the gate, then raises a raw `KeyError` at `snap["part_occurrences"]`/`snap["constraint_lowering_mode"]` instead of a `SnapshotFormatError` with a re-capture instruction. **Why it matters:** the spec's rejection requirement is that a corrupt v3 snapshot fails *loudly with a re-capture message*; an unhandled `KeyError` is neither. **Fix:** gate all three v3 keys together with the `_require(raise_on_missing=True)` idiom; also read `constraint_facts.get("schema_version")` so a torn facts dict raises `SnapshotFormatError`, not `KeyError`.

- **MF2 — A corrupt/unknown `constraint_lowering_mode` silently skips lowering (reopens the silence trap).** [Route Safety] `if mode == "applied" ... lower` else skip, with the grandfather WARNING only for `mode == "grandfathered_off"`. A hand-edited or torn mode value matches neither branch: no lowering, no warning, an asserting model generates an assertion-free graph. **Why it matters:** this is precisely the silence trap the spec/concept forbid (concept line 66). **Fix:** the loader validates `mode ∈ {"applied","grandfathered_off"}` and raises `SnapshotFormatError` on anything else — treat the marker as a load-bearing enum whose unknown value is corruption.

### Major (Should address)

- **MF3 — `resolve_owner_occurrence_table` re-derives the owner set independently of lowering's actual queries, and B5 is imprecise.** [Abstraction / Duplication / Bets] Lowering queries `occurrences_of` for `part_def` **AND `Eligibility.ADMIT`** owners only; the helper as described omits the ADMIT filter. Consequence: capture can halt on a non-finite owner of an unassessed usage that live lowering never queries — a capture-vs-live divergence — and the table's sufficiency rests on two code paths staying matched forever. **Fix (preferred):** capture the table as a byproduct of the `lower_constraints` call itself (record the keys `occurrences_of` was actually asked for), so the serialized table is exactly sufficient by construction and B5 becomes true-by-construction. **Fix (minimum):** apply the identical profile+kind filter and restate B5 as "`part_def`-kind, `ADMIT`-eligible owners."

- **MF4 — `part_occurrences` key ordering is unpinned; byte-identity churns on re-capture.** [Data Structure / hidden bet] `snapshot_to_json` does not `sort_keys` (`serializer.py:200`), so dict order is insertion order. The facts section stays deterministic because Item 1's `serialize()` emits canonical sorted JSON; `part_occurrences` has no such canonicalization. If the helper dedups owners via a `set`, key order varies run-to-run and the section churns every capture, defeating the corpus byte-identity gate. **Fix:** pin the key order deterministically — iterate `facts.usages` in order with dict-dedup, or sort the keys — and state it in the design. (Occurrence *list* order within a key is already safe: `occurrences_of` returns sorted via `_occurrence_sort_key`, preserved by `_serialize_value`.)

### Minor (Consider addressing)

- **NH1 — Pin the full mode × section matrix in the design.** A short table (every cell → defined behavior, including the corrupt-mode and missing-key cells) would make MF1/MF2 obvious and give the plan a spec to test against.
- **NH2 — Extend the expected-diff enumeration to all three new keys.** Spec class 2 names only the facts section; the re-capture review must also expect `part_occurrences` and `constraint_lowering_mode` on every snapshot, or they read as unexpected diffs.
- **NH3 — "22 divergences become this test's baseline" conflates two things.** The 3 byte-identity parity fixtures do not cover all 22 corpus-wide conformance divergences; those are eliminated by the full conformance suite going green. Reword so the acceptance story is precise.
- **NH4 — Note the staleness boundary explicitly.** Offline lowering trusts the frozen occurrence table with no live model to cross-check; a model-edited-but-not-recaptured v3 snapshot lowers against stale occurrences (internally consistent, silently stale). The design correctly defers detection to Item 9 (fingerprint) in Non-Goals — one sentence making that boundary explicit closes the probe.
- **NH5 — Embedded `expression-ir` version is guarded only at the code level, not the data level.** The loader validates the top-level facts `schema_version` (data) but pins `expression-ir/v1` only via a code assert. A torn snapshot embedding an `expression-ir/v2` predicate node relies on `constraint_facts.parse` to reject it (Item 1's concern). Confirm `parse` validates embedded node versions, or add a data-level check.

---

## Recommendations

1. **Close the rejection surface (MF1 + MF2).** Gate all three v3 keys and validate the mode enum, both raising `SnapshotFormatError` with a re-capture message. This is the spec's headline requirement (loud rejection, no silent assertion-free generation) and the design currently leaves two holes in it.
2. **Remove the second owner-selection path (MF3).** Capture the occurrence table as a byproduct of the real `lower_constraints` call so sufficiency is structural, not a two-path match. Restate B5 precisely regardless.
3. **Pin `part_occurrences` determinism (MF4).** One sentence in the design fixing key order; without it the corpus byte-identity gate is unreliable.
4. **Add the mode×section matrix and extend the expected-diff list (NH1, NH2).** Cheap, and they make the plan and the re-capture review mechanical.

---

## Resolutions

_(Filled in during Stage 4 as the owner resolves each issue. This is what the design agent reads to incorporate the review.)_

---

**Overall:** Approved-with-must-fixes

The foundation is sound — re-derivation over carriage, frozen occurrence table, loud-marker grandfather, version-gate reuse are all the right calls and verify against the code. The four must-fixes are completeness/determinism holes, not a rework: two rejection-surface holes (MF1, MF2) that reopen the silence trap the spec exists to close, one owner-selection drift (MF3) that falsifies stated bet B5 and can halt capture, and one unpinned ordering (MF4) that undermines the byte-identity gate. All four are local fixes to an otherwise-correct design.

**Next Steps:** Record resolutions above, then re-run `/_my_design` (or return to the design-agent session) pointed at this review to incorporate. The reviewer does not edit the design.

ARTIFACT: .project/active/snapshot-v3/design-review.md
