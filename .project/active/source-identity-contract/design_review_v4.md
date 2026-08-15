# Design Re-Review v4: Authoritative Source-Identity Contract (SOURCE-IDENTITY Item 3)

**Design:** `.project/active/source-identity-contract/design.md` (rev 4)
**Spec:** `.project/active/source-identity-contract/spec.md`
**Prior Review:** `.project/active/source-identity-contract/design_review_v3.md`
**Review File:** `.project/active/source-identity-contract/design_review_v4.md`
**Date:** 2026-08-05

---

## Fundamental Assessment

**Concerns. Revise, not Rework.** Rev 4 keeps the sound authority architecture and fixes the most
important schema error from rev 3. Form support, expected boundary outcome, and certification are
now separate. R5 assigns route and mutation obligations from the boundary outcome, so supported
forms that correctly diagnose no longer inherit impossible runtime proof.

The literal arithmetic also checks: Appendix A contains 21 top-level rows and claims 27 coordinates.
Those 27 are not yet concrete R1/SI-23 coordinates. Supported rows are collapsed under a rule that
only permits rejected-form families; checkpoint rows lack keys and outcomes; several source classes
cannot use the six-value authored-form vocabulary; and the evidence mapping still merges observations
with different semantic referents. RM13 is also assigned two incompatible meanings.

These are matrix defects, not a reason to replace the amendment approach. The contract homes,
copy-and-freeze migration, verification-status separation, and two-checkpoint sequence remain sound.

**Stage 0 recommendation:** keep the rev-4 architecture and route-outcome schema. Rebuild the
coordinate enumeration once more from exact referents and keys, then re-review before the owner
checkpoint and `my-plan`.

---

## V3 Finding Closure Audit

| V3 finding | V4 status | Assessment |
|---|---|---|
| V3-M1 — Cell-key derivation and exact count | **Open** | The arithmetic is explicit, but supported families violate R1/R2 and incomplete rows are counted as concrete. See V4-M1. |
| V3-M2 — Form support versus boundary outcome | **Closed** | Three orthogonal fields and R5 correctly attach routes and mutation to boundary outcome (`design.md:230-264`). |
| V3-M3 — Evidence fidelity | **Partially closed** | Rev-3 SRC-13/SRC-16 are retired and SRC-07 cites exact lines. SRC-07/08 still merge different referent contexts, and RM13 is used for incompatible cells. See V4-M3/V4-M4. |
| V3-M4 — SVM clauses too broad | **Closed with one annotation note** | SVM-01/02/04 now retain only derived value-adapter behavior and supersede independent identity authority (`design.md:166-177`). REQ-VBR-10 still needs an explicit row-level `PARTIAL`; see V4-N1. |
| V3-M5 — Full SI-23 schema | **Partially closed** | A.1 names all 15 fields and their locality. Several enumerated rows cannot supply those fields. See V4-M2. |
| V3-N1 — Six source categories | **Closed** | The inventory and validation both name six categories (`design.md:270-274,479-491,420-423`). |
| V3-N2 — SRC-01 census wording | **Closed** | The 75 mints are labeled as the broader affected population, separate from ~124 + 91 self-bindings (`design.md:518,544`). |
| V3-N3 — Clause-label invariant | **Partially closed** | The invariant now defines row and clause labels, but D4 does not explicitly assign REQ-VBR-10 its row-level value (`design.md:157-181,337-340`). |

---

## Dimensional Review

### 1. Spec Compliance

**Assessment:** Fail

Rev 4 continues to satisfy the authority, provenance, correction, archive, validation, guidance, and
sequencing parts of the spec. Owner-originated payloads remain correctly attributed, and the new
customer-form choice is explicitly `[AGENT]` pending checkpoint item 8 (`design.md:286-294,319-321`).

The acceptance authority remains incomplete:

- The spec requires an evidence coordinate for every supported and rejected form across calculation,
  constraint, and aggregation consumers (`spec.md:43-45,95-98,161-165`). Bare-renamed is supported,
  but its rows cover calculations only. SRC-10's blocked cross-consumer family includes chain and
  owner-qualified forms, not bare-renamed (`design.md:565`).
- R6 leaves shadowing and specialization without a concrete key or expected outcome and assigns Item
  4 to create the cells and change the authoritative count (`design.md:266-268,572,576`). Evidence may
  remain blocked, but Item 4 should inherit the target coordinate rather than choose it. Otherwise
  Item 3 has not met the downstream-derivability criterion (`spec.md:51-52`).
- SRC-04 and SRC-05 are called concrete cells in the count, but they do not contain an
  `expected_boundary_outcome` or full evidence coordinate (`design.md:554-555,580-583`). If an owner-
  approved expression deferral is a valid final result, the schema also needs a final `DEFERRED`
  state; `PENDING_CHECKPOINT` is no longer true after that decision.

**Recommendation:** distinguish blocked proof from deferred semantics. Item 3 must publish the
target key/outcome for blocked cells; a genuinely deferred class needs an explicit final disposition
and must not be counted as a concrete coordinate.

### 2. Pattern Consistency

**Assessment:** Concerns

The repository-level patterns now fit. Behavioral wording stays in the lifecycle contract, Appendix
C owns scenarios, Appendix B owns superseded readings, the durable companion owns graded IDs, and
the completed spec remains frozen (`design.md:85-103,186-206`). The verification matrix keeps test
status separate from contract disposition.

D4 almost implements its own exact row-annotation pattern. REQ-VBR-10 is described as a clause split
but is not explicitly assigned row-level `PARTIAL`, despite D4 and the invariant requiring exactly
one row value (`design.md:157-161,180-181,337-340`).

**Recommendation:** label REQ-VBR-10 `PARTIAL` explicitly. Keep the specialized-chain clause as
`stands` and the self-binding rescue clause as `SUPERSEDED`.

### 3. Abstraction Quality

**Assessment:** Concerns

The three named levels are a good abstraction: disposition family, acceptance cell, and evidence
coordinate (`design.md:116-122`). The problem is that the derivation rules do not preserve those
levels:

- R2 permits family collapse only for `UNSUPPORTED` and `LANGUAGE_REJECTED` forms
  (`design.md:247-250`). SRC-09 and SRC-10 nevertheless collapse two supported authored forms into
  one top-level row (`design.md:564-565`). R1 says authored form is part of the key, so these are four
  acceptance cells, not two.
- R6 calls a row with no key or outcome a placeholder family. That can track an evidence gap, but it
  is not an acceptance cell or an evidence coordinate. Counting placeholders alongside concrete
  rows hides that distinction.

**Recommendation:** use families only as non-counted grouping headers. Count each complete R1 key as
one cell and each full SI-23 record as one evidence coordinate.

### 4. Duplication Avoidance

**Assessment:** Pass

No parallel normative document is introduced. The `LC-SI-*` projection rule remains mechanical, and
the archive copy avoids a second mutable authority (`design.md:89-103,191-199`). Appendix A's source
inventory, derivation, and enumeration are different views of one matrix and have a same-edit
invariant; that is useful traceability rather than semantic duplication.

### 5. Data Structure Clarity

**Assessment:** Fail

- **V4-M1 — The 21/27 count is bookkeeping, not the result of R1–R3.** SRC-09 and SRC-10 each merge
  two supported authored forms even though authored form is part of the key and R2 does not apply.
  SRC-02/03 use `× any` without the concrete coordinate subrows R2 requires. SRC-04/05 have neither
  complete keys nor boundary outcomes but are counted among the 16 concrete cells
  (`design.md:242-268,552-565,578-583`). Splitting only SRC-09/10 already changes the top-level count.
- **V4-M2 — The 15-field schema is not total over the row population.** `authored_form` is declared
  as one of the six AFT forms (`design.md:463-465`), but expression bindings, unbound defaults, and
  authored literals are also rows. They need exact values such as expression, unbound/no binding, or
  authored literal. `semantic_referent` cannot always be derived from an AFT form for those classes,
  aggregation terms, or placeholder shapes. Pending and placeholder rows also lack public topology,
  diagnostic, mutation, and route fields (`design.md:471-477,554-555,572,576`).
- **V4-M3 — The key omits a semantic distinction exposed by the evidence.** AFT 1c/2 are authored in
  a PartDef and resolve to the definition feature
  (`authoring-form-table.md:17-19,24-25,35-36`). DCS lines 71/83/92 are authored inside the concrete
  `analyzer` PartUsage; the extracted QN names
  `DeepCrossScopeDesign::measurement_system::analyzer::baseline_value`, not the Analyzer PartDef
  declaration (`tests/fixtures/deep_cross_scope_probe/design.sysml:61-93`;
  `tests/fixtures/deep_cross_scope_probe/extraction_snapshot.json:404,448,478`). The design merges
  those observations into SRC-07/08 and says the semantic referent derives from form. It does not:
  qualifier kind and binding-owner context change the referent. R1 needs that context in the topology
  key, or semantic referent itself must be key material. SRC-08 also calls one qualified DCS binding a
  multi-calc observation; the other two bindings use the bare-renamed form (`design.md:508,563`).
- **V4-M4 — RM13 is assigned incompatible semantic states.** The derivation maps one unresolved
  aggregation observation to both resolved SRC-17 and “genuine terminal miss” SRC-22
  (`design.md:509,570,575`; `route-matrix.md:30`). The solar model contains the `permitting` child and
  the referenced cost features (`tests/fixtures/solar_battery_model/library.sysml:697-721`), so RM13
  is evidence that a modeled reference fails positive resolution. It contradicts SRC-17. It is not
  evidence of genuine absence and cannot certify SRC-22 as `CONTRADICTED_AT_HEAD`. SRC-22 needs an
  independently constructed terminal-miss coordinate or must remain blocked/unproven.
- **V4-M5 — Coverage changes under checkpoint item 8 are incomplete.** If the owner selects the
  owner-qualified customer form, the design merges SRC-15 into SRC-08
  (`design.md:286-294,319-321`). AFT form 3 remains an observed, supported chain form, but A.3 maps its
  two-calc coordinate only to SRC-15; SRC-10a is a different mixed-consumer key
  (`design.md:513,565`). The alternate checkpoint branch must re-home the AFT-3 cell and recompute the
  derivation/count. The missing bare-renamed mixed-consumer coordinate changes the count as well.

The source-to-row table also names the converged census class in A.2 but does not map that class in
A.3 (`design.md:484-486,493-528`). That is a smaller completeness defect in the promised inventory
audit.

**Recommendation:** make the derivation table operate on full keys, including semantic referent or
binding-owner context. Give every source exactly one evidence role: direct observation, topology
referent, principle-derived target, or blocked obligation. Recompute row and coordinate counts only
after all keys are explicit.

### 6. Route Safety

**Assessment:** Concerns

R5 itself is now sound. Runtime-source rows require full parity and mutation; authoring, ambiguity,
policy, and load failures end at explicit boundaries (`design.md:256-264`). This closes the rev-3
route defect.

Several rows cannot use R5 yet because they have no boundary outcome. The `POLICY_DIAGNOSTIC` row
also says “per strict/lenient” without publishing the exact diagnostic disposition for each policy
(`design.md:263,575`). The spec allows policy to change only the disposition of a genuine miss, so
the matrix must state those two results rather than leave them to Items 4/5.

**Recommendation:** retain R5 and complete each row's boundary outcome. Add strict and lenient
subcoordinates if their observable diagnostics differ.

### 7. Bets & Decisions Integrity

**Assessment:** Concerns

B2–B4 are genuine bets with named failure outcomes. D1–D7 continue to name the relevant rejected
alternatives. Checkpoint item 8 correctly preserves the chain recommendation as `[AGENT]`; owner
approval must not upgrade its provenance (`design.md:286-294,319-321`).

B1 is not supported by the current mapping. RM13 has not been classified as positive-resolution
failure versus genuine terminal miss before being used for both. Bare-renamed cross-consumer
coverage is absent, and the DCS/AFT merge shows that written spelling alone is insufficient to derive
the semantic referent. These gaps can change dispositions, keys, and counts, which is B1's stated
failure mode (`design.md:126-130`).

**Recommendation:** either narrow B1 to the evidence actually classified or close these evidence
classification gaps before treating the matrix as binding.

### 8. Reader Comprehension

**Assessment:** Concerns

The authority model, semantic spine, three matrix levels, and route table are clear. Rev 4 is easier
to follow than rev 3.

The exact-count presentation gives a false sense of completion. “Concrete cell” includes pending
classes with no outcome, while supported-form families combine several R1 keys. A reader also cannot
tell that `owner-qualified` covers a PartDef qualifier in AFT but a PartUsage qualifier in DCS, even
though those names reach different semantic elements.

**Recommendation:** show each actual coordinate as one row with all key fields visible. Use grouping
headers for readability, but do not count the headers as cells or let them hide differing referents.

---

## Issues by Severity

### Critical

- None. The authority and route architecture remain sound.

### Major

- **V4-M1 — The 21-row/27-coordinate count is not produced by R1–R3:** supported families merge form
  keys, rejected rows omit required subcoordinates, and pending rows are counted as concrete. — Data
  Structure Clarity / Abstraction Quality
- **V4-M2 — The SI-23 schema is not total over the enumerated rows:** several source classes have no
  value in the six-form vocabulary, and pending/placeholder rows cannot publish all required fields.
  — Spec Compliance / Data Structure Clarity
- **V4-M3 — AFT and DCS evidence with different semantic referents is merged:** form spelling alone
  cannot derive referent identity, and SRC-08 overstates one qualified binding as multi-calc route
  evidence. — Capture Fidelity / Data Structure Clarity
- **V4-M4 — RM13 is used as both a broken positive reference and a genuine terminal miss:** SRC-22
  needs independent evidence or a blocked/unproven state. — Capture Fidelity / Bets
- **V4-M5 — Required supported-form coverage is incomplete and checkpoint-dependent:** bare-renamed
  has no cross-consumer coordinate, and the owner-qualified checkpoint branch drops the AFT-3
  two-calc chain coordinate. — Spec Compliance / Data Structure Clarity

### Minor

- **V4-N1 — REQ-VBR-10 lacks an explicit row-level `PARTIAL` label:** its clause labels are correct,
  but D4's declared row vocabulary is not applied (`design.md:180-181`). — Pattern Consistency
- **V4-N2 — The converged census class has no A.3 mapping:** A.2 includes it, but the source-to-row
  table does not (`design.md:484-486,493-528`). — Data Structure Clarity
- **V4-N3 — `POLICY_DIAGNOSTIC` is not exact by policy:** “per strict/lenient” does not state each
  expected observable disposition (`design.md:263,575`). — Route Safety

---

## Recommendations

1. Expand supported-family rows into one row per authored form and full R1 key. Add the missing
   bare-renamed mixed-consumer cell and exact subrows for the rejected forms.
2. Extend the authored-form vocabulary to all matrix classes and add binding-owner/qualifier context
   or semantic referent to the key. Re-derive AFT and DCS cells separately.
3. Treat pending decisions and R6 placeholders as non-concrete until every SI-23 field and boundary
   outcome is fixed. Record an explicit final deferral state when the owner defers a class.
4. Use RM13 only for the broken modeled aggregation reference. Add separate genuine-terminal-miss
   evidence for SRC-22 or mark it blocked/unproven.
5. Make checkpoint item 8's two branches total: preserve a chain two-calc coordinate under either
   decision, update the source table, and recompute all counts.
6. Apply the remaining mechanical annotation and inventory fixes, then re-run design review before
   the owner checkpoint and `my-plan`.

---

## Resolutions

No v4 owner resolutions are recorded yet. Rev 4's `[AGENT]` customer-form recommendation and other
design notes remain proposed closure, not owner-originated decisions.

---

**Overall:** Revise

**Next Steps:** Return to the design-authoring session or re-run `my-design` with this review. Repair
V4-M1 through V4-M5 and the three minor consistency issues, then re-review. Once the matrix is
coherent, hold the owner decision checkpoint and record agenda items 1–8 before `my-plan`. The
reviewer does not edit the design.
