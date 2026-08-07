# Design Re-Review v3: Authoritative Source-Identity Contract (SOURCE-IDENTITY Item 3)

**Design:** `.project/active/source-identity-contract/design.md` (rev 3)
**Spec:** `.project/active/source-identity-contract/spec.md`
**Prior Review:** `.project/active/source-identity-contract/design_review_v2.md`
**Review File:** `.project/active/source-identity-contract/design_review_v3.md`
**Date:** 2026-08-05

---

## Fundamental Assessment

**Concerns. Revise, not Rework.** Rev 3 keeps the sound authority architecture from rev 2 and
genuinely fixes the archive migration, projection rule, stale-status scope, and checkpoint order.
It also identifies the correct seven verification rows. No foundational redesign is needed.

The acceptance matrix is still not deterministic under its own rules. R1 makes authored form and
override/default state part of a cell key, but Appendix A merges different values for those axes and
leaves other keys unspecified. The `SUPPORTED` disposition also covers both successful runtime
sources and pre-generation diagnostics, even though R4/R5 assign mutation and replay obligations to
every supported cell. The declared count of 19 and its route obligations therefore cannot be
implemented or audited as written.

The verification-row map has one remaining semantic error. It marks all of REQ-SVM-01 as
`SUPERSEDED`, although the recorded adjacent-work ruling allows supplied-value synthesis to remain
as a value adapter when it derives from the single semantic identity authority. That row needs a
narrowed `PARTIAL` treatment.

**Stage 0 recommendation:** retain the rev-3 authority and sequencing design. Repair the cell key,
outcome, evidence-coordinate, and SVM clause treatments, then re-review. Do not proceed to
`my-plan`; the design also correctly requires the owner decision checkpoint before planning.

---

## V2 Finding Closure Audit

| V2 finding | V3 status | Assessment |
|---|---|---|
| V2-M1 — Deterministic sparse cells | **Open** | R1 is explicit, but several Appendix A rows violate it and the count is not reproducible. See V3-M1. |
| V2-M2 — Evidence-form fidelity | **Partially closed** | SRC-01/SRC-15 are now paired and SRC-06 is faithful. SRC-07 needs exact sub-row evidence; SRC-13 and SRC-16 still change the form or consumer mix of the evidence they cite. See V3-M3. |
| V2-M3 — Archive migration | **Closed** | D6 copies the archived companion, adds provenance at the durable home, and keeps the archive byte-identical (`design.md:160-168,295-297`). |
| V2-M4 — Checkpoint ordering | **Structurally closed; owner action pending** | Decisions happen before `my-plan`; final ratification follows drafting (`design.md:169-175,246-271`). Agenda items 1–7 still require owner answers. |
| V2-M5 — Seven row dispositions | **Partially closed** | The count and vocabulary are fixed, but REQ-SVM-01 and the literal-application part of REQ-SVM-04 are classified too broadly. See V3-M4. |
| V2-N1 — Stale status | **Closed in design; owner approval pending** | Both the 41/41 proof and merged-state changelog are cited, and the full stale sections are in scope (`design.md:49-54,266-268`). |
| V2-N2 — Completed-spec path | **Closed** | D6 uses the exact `.project/completed/...` source path (`design.md:160-162`). |
| V2-N3 — `LC-SI-*` projection | **Closed** | Behavioral wording has one owner and requirement rows carry checkable citations (`design.md:86-89`). |

---

## Dimensional Review

### 1. Spec Compliance

**Assessment:** Fail

Rev 3 covers the authority chain, provenance, corrections, validation, guidance, archive handling,
and owner checkpoints. It preserves the owner payloads at their stated force and does not visibly
upgrade an `[INFERRED]` or `[INHERITED]` item to owner origin.

Two matrix requirements remain unmet:

- SI-23 requires every cell to publish an exact evidence coordinate: authored form, semantic
  referent, declaration and concrete occurrence identity, default/override state, consumer type and
  count, route, public topology, diagnostic, and mutation result (`spec.md:161-165`). Appendix A
  omits or combines several of those coordinates. Its global route/mutation defaults cannot repair a
  row whose expected result is a diagnostic.
- R2 collapses every observed bare-self-named topology into SRC-01 (`design.md:211-213,393`). That is
  useful as a form-disposition family, but it is not one SI-23 evidence coordinate. The concrete
  variants must be subrows or separately enumerated acceptance cells.

The verification requirement also remains partly open because the proposed SVM dispositions do not
match the recorded mechanism boundary. See V3-M4.

**Recommendation:** define the full Appendix C row schema and distinguish a disposition family from
the concrete evidence coordinates it contains.

### 2. Pattern Consistency

**Assessment:** Concerns

The artifact pattern now fits the repository. The lifecycle contract remains the behavioral
authority, Appendix C owns scenarios, Appendix B owns corrections, the durable companion owns graded
IDs, and the completed spec stays frozen (`design.md:71-89,155-168`). This closes the material archive
and parallel-authority concerns.

The SVM clause map does not fit the existing mechanism split. REQ-SVM-01 describes creating a
synthetic design attribute after resolving a demand (`docs/architecture/verification-matrix.md:566`;
`src/sysml_codegen/resolution/supplied_values.py:639-660`). The reference-to-literal stamp is a
different earlier mutation (`src/sysml_codegen/orchestration/pipeline_builder.py:363-369`). The
adjacent-work register explicitly permits synthesis to remain if it derives from the single identity
authority (`.project/active/source-identity-route-evidence-spike/adjacent-work-register.md:16`).

**Recommendation:** treat SVM synthesis as `PARTIAL`: supersede its independent identity authority,
not the whole value-adapter behavior.

### 3. Abstraction Quality

**Assessment:** Concerns

The semantic spine and artifact ownership are small and clear. The scenario abstraction still asks
one field to answer two questions:

- Is this authored form supported by the executable subset?
- What happens at the boundary for this topology: a runtime source, an authoring diagnostic, a
  capture refusal, a generation diagnostic, or a load error?

SRC-09 exposes the mismatch. It is `SUPPORTED`, but its required result is an ambiguity diagnostic
before a runtime source exists (`design.md:401`). SRC-17 similarly includes a terminal-miss diagnostic
inside a `SUPPORTED` row (`design.md:409`). R4/R5 then require mutation and full replay parity from
both (`design.md:215-222,387-389`).

**Recommendation:** use separate `form_disposition`, `expected_boundary_outcome`, and
`certification_state` fields. Derive route and mutation applicability from the boundary outcome.

### 4. Duplication Avoidance

**Assessment:** Pass

Rev 3 creates no new normative decision or scenario document. The projection rule gives behavioral
wording one home, and the companion requirements add IDs, grades, sources, and citations without
restatement (`design.md:75-89`). The copy-and-freeze migration also avoids using the archive as a
second mutable authority.

### 5. Data Structure Clarity

**Assessment:** Fail

- **V3-M1 — The exact 19-cell count contradicts R1.** R1 includes authored form and
  override/default state in the cell key; R3 only merges identical keys, and R2 only collapses
  unsupported or language-rejected forms (`design.md:208-218`). Appendix A nevertheless:
  - combines default and override states in SRC-08 (`design.md:400`);
  - combines qualified and renamed forms in SRC-09 (`design.md:401`);
  - combines chain and qualified forms in SRC-13 (`design.md:405`);
  - leaves SRC-15's authored form as “approved explicit form” (`design.md:407`); and
  - omits authored form from SRC-16, SRC-18, and SRC-19 (`design.md:408-411`).
  SRC-19 also combines shadowing and specialization topology shapes without a supported-cell
  collapse rule. Applying R1 as written creates more cells than Appendix A, so 19 is not the output
  of the declared derivation.
- **V3-M2 — Disposition does not determine applicability.** `SUPPORTED` currently means both “the
  form is accepted” and “this cell produces a runtime source.” SRC-09 and SRC-17 disprove that
  equivalence, so the global mutation/parity rules are not total.
- **V3-M3 — Evidence coordinates are not faithful enough.** SRC-13 cites RM7, which is bare
  self-named, while the target row changes the form to chain/qualified and calls it
  `CONTRADICTED_AT_HEAD` (`route-matrix.md:24`; `design.md:405`). Qualified/chain cross-owner behavior
  is unobserved and belongs in `BLOCKED` or `UNPROVEN`. SRC-16 combines RM5's bare-self-named
  calc+constraint control with RM6's dotted two-calc control into a supported calc+constraint row
  that neither source observed (`route-matrix.md:22-23`; `design.md:408`). SRC-07 is supportable from
  RM12, but RM12 is mixed-form evidence; cite its two exact bare-renamed bindings rather than the
  whole row (`route-matrix.md:29`; `tests/fixtures/deep_cross_scope_probe/design.sysml:69-93`).
- **V3-M5 — The final SI-23 row shape is not specified.** The two orthogonal fields are useful, but
  the design never says how each Appendix C row carries all SI-23 coordinates. “Any topology/
  consumers” and inherited global obligations are insufficient when a concrete coordinate is the
  certification unit.

The validation section also says “four source sets” although the derivation names six categories
(`design.md:224-226,360-362`). That wording is minor, but it confirms that the source-to-cell mapping
is not yet mechanical.

**Recommendation:** publish a source-to-cell derivation table. Each output row must contain exactly
one R1 key, or be named as a family with explicit coordinate subrows. Recompute the count from that
table rather than holding 19 fixed.

### 6. Route Safety

**Assessment:** Fail

R5 safely terminates unsupported and language-rejected routes at their required failure boundaries.
It is unsafe for supported forms used in a topology that must diagnose. SRC-09 has no snapshot or
mutation route, and SRC-17's terminal-miss branch cannot satisfy the global supported-cell
obligations. A downstream test plan following R5 literally would either invent replay behavior after
a required failure or silently exempt cells.

**Recommendation:** assign route obligations by `expected_boundary_outcome`, including explicit N/A
boundaries for ambiguity and policy diagnostics.

### 7. Bets & Decisions Integrity

**Assessment:** Concerns

B1–B4 are genuine bets with stated failure consequences, and the design follows through on the
selected artifact homes. D6 and D7 now name and reject the right alternatives.

B3 rests on an unstated equivalence: every `SUPPORTED` cell is assumed to produce a runtime source.
The Appendix itself disproves that assumption. B1 also calls the evidence sufficient while SRC-13
and SRC-16 label derived supported-form cells as contradicted by observations made with different
forms or consumer mixes.

The decision checkpoint is now sequenced correctly. It is still pending owner action. Agenda items
1–7 must be answered and recorded with their original provenance before `my-plan`; final table
ratification remains a separate later interaction (`design.md:246-271`).

**Recommendation:** correct the matrix abstraction first, then hold the decision checkpoint against
the revised cells. Do not treat an owner approval as owner-originated provenance.

### 8. Reader Comprehension

**Assessment:** Concerns

The ownership table, semantic spine, and architecture diagram are clear. A reader can understand the
authority model in one pass.

The Appendix undercuts that clarity. “Supported” appears to promise runtime parity in the schema but
means “supported form with a diagnostic outcome” in some rows. The text calls 19 mechanically
derived while rows visibly combine values from the declared key. A reader cannot tell whether a row
is a form family, a test case, or one certifiable evidence coordinate.

**Recommendation:** name those three levels explicitly and use one term for each.

---

## Issues by Severity

### Critical

- None. The authority architecture is sound.

### Major

- **V3-M1 — Appendix A does not follow its cell-key rules:** supported rows merge or omit key values,
  so the exact count of 19 is not reproducible. — Data Structure Clarity / Spec Compliance
- **V3-M2 — Form support is conflated with boundary outcome:** diagnostic cells are marked
  `SUPPORTED` and inherit impossible mutation/replay obligations. — Abstraction Quality / Route
  Safety
- **V3-M3 — Several target cells change or overstate their cited evidence:** SRC-13 and SRC-16 use
  bare or different-consumer observations to certify unobserved supported-form cells; SRC-07 needs an
  exact sub-row citation. — Capture Fidelity / Data Structure Clarity
- **V3-M4 — SVM clauses are superseded too broadly:** REQ-SVM-01 and part of REQ-SVM-04 may remain as
  derived value adapters; only independent identity authority is superseded. — Pattern Consistency /
  Spec Compliance
- **V3-M5 — The full SI-23 evidence-coordinate schema is still absent:** Appendix A cannot yet become
  a certifiable Appendix C table without downstream schema invention. — Spec Compliance / Data
  Structure Clarity

### Minor

- **V3-N1 — Source-set count is inconsistent:** validation says four source sets while the derivation
  names six categories (`design.md:224-226,360-362`). — Reader Comprehension
- **V3-N2 — SRC-01 overstates the self-binding census:** the 75 model-derived mints include mixed,
  dotted, and aggregation routes, not only bare self-bindings
  (`corpus-census.md:31-45`; `route-matrix.md:29-30`; `design.md:393`). Keep the ~124 external + 91
  fixture self-binding count; label 75 as the broader affected mint population. — Evidence Fidelity
- **V3-N3 — The clause invariant is broader than the clause map:** “every affected clause” must carry
  one of three disposition values, while several surviving clauses are described only as “stands”
  (`design.md:139-150,284-285`). State whether the row-level `PARTIAL` value covers standing clauses
  or label every clause mechanically. — Data Structure Clarity

---

## Recommendations

1. Re-derive Appendix A from an explicit source-to-key table. Give every cell one authored form,
   topology, consumer mix, and value state, or model it as a family with explicit coordinate subrows.
   Recompute the count.
2. Split form support, expected boundary outcome, and certification state. Make route and mutation
   obligations follow the boundary outcome.
3. Specify every SI-23 field in the final Appendix C schema, including which fields may be inherited
   and which must be row-local.
4. Correct SRC-13 and SRC-16 to preserve evidence form and consumer mix. Narrow SRC-07 to its exact
   two bare-renamed bindings; choose or enumerate the explicit customer form in SRC-15.
5. Change REQ-SVM-01 to `PARTIAL` and split REQ-SVM-04 at the independent-authority boundary rather
   than treating value materialization itself as superseded.
6. After those revisions, hold the owner decision checkpoint and record agenda items 1–7 before
   planning.

---

## Resolutions

No v3 owner resolutions are recorded yet. The design's notes are evaluated as proposed closures,
not as owner decisions.

---

**Overall:** Revise

**Next Steps:** Return to the design-authoring session or re-run `my-design` with this review. Repair
V3-M1 through V3-M5, then re-review. Once the matrix is coherent, hold the decision checkpoint and
record the owner's answers before `my-plan`. The reviewer does not edit the design.
