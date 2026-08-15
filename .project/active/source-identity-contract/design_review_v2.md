# Design Re-Review v2: Authoritative Source-Identity Contract (SOURCE-IDENTITY Item 3)

**Design:** `.project/active/source-identity-contract/design.md` (rev 2)
**Spec:** `.project/active/source-identity-contract/spec.md`
**Prior Review:** `.project/active/source-identity-contract/design-review.md`
**Review File:** `.project/active/source-identity-contract/design_review_v2.md`
**Date:** 2026-08-05

---

## Fundamental Assessment

**Concerns. Revise, not Rework.** Rev 2 fixes the original architectural failure. It no longer
creates separate normative decision-register and acceptance-matrix documents. Decisions,
corrections, and scenarios now use the lifecycle contract's existing sections, and verification
test state is separated from contract disposition (`design.md:68-81,122-168`). The core amendment
approach is now sound.

The acceptance authority is not deterministic enough to implement. Its row derivation treats four
evidence-gap bullets as four cells even though one gap applies to every supported cell; its status
field mixes semantic disposition with certification state; its representative row changes the
authored form of the evidence it cites; and its expected count is deliberately inexact. The proposed
archive migration also removes the historical spec from the completed-item archive. These are
repairable design defects, but they remain load-bearing because Items 4–6 inherit this matrix and
authority chain.

**Stage 0 recommendation:** retain the rev-2 architecture, revise the scenario schema and migration
mechanics, then re-review. No foundational rework is needed.

---

## V1 Finding Closure Audit

The Resolutions note appended to `design-review.md:278-312` is treated as the design author's
response, not as an owner resolution. Each closure claim was re-derived against rev 2.

| V1 finding | V2 status | Assessment |
|---|---|---|
| DR-C1 — Normative ownership | **Closed with one clarification** | Existing contract sections are now used and Appendix C is the sole scenario home (`design.md:68-81,147-162`). Clarify how substantive `LC-SI-*` wording relates to contract invariants so the one-home check can distinguish checkable projection from restatement. |
| DR-M1 — Verification status | **Partially closed** | `PASS` remains test state and clause-level disposition is orthogonal (`design.md:136-146`). Rev 2 miscounts seven rows as eight and does not assign the spec's exact disposition vocabulary to every clause. See V2-M5. |
| DR-M2 — Matrix schema | **Open** | Sparse derivation is the right direction, but count, deduplication, applicability, and state fields are not reproducible. See V2-M1 and V2-M2. |
| DR-M3 — Checkpoint scope | **Partially closed** | The agenda now includes all gates and names rejected-deferral consequences (`design.md:221-240,300-305`). It asks the owner to ratify a table before that table is drafted. See V2-M4. |
| DR-M4 — Archived companion | **Open** | Owner gating is explicit, but `git mv` plus a stub still removes the archived deliverable from the current archive. See V2-M3. |
| DR-M5 — SI-18 payload | **Closed** | SI-01, SI-15/16, and SI-18 are separated correctly; `quesiton` remains with SI-18 (`design.md:255-258`). |
| DR-N1 — Stale authority status | **Open** | The proposed pointer is incomplete and still requires an owner ruling. See V2-N1. |

---

## Dimensional Review

### 1. Spec Compliance

**Assessment:** Concerns

Rev 2 now covers the spec's authority, disposition, correction, validation, guidance, and
derivability obligations without introducing peer authority documents. It carries the owner payloads
correctly and retains provenance-grade auditing (`design.md:242-258,327-341`). No challengeable
`[INFERRED]` or `[INHERITED]` requirement is visibly upgraded to owner origin.

Two compliance gaps remain:

- The spec requires the affected verification rows to be marked `partial`, `failed`, or
  `superseded` (`spec.md:46-48`). Rev 2 promises family footnotes using “superseded or
  under-proving,” but does not define the exact orthogonal disposition value for every affected
  clause or require a marker on each row (`design.md:136-146`).
- The exact-customer acceptance requires two outcomes under the settled self-binding rule: the
  original self-binding fails and an approved explicit form converges
  (`.project/backlog/epic_semantic_source_identity.md:145-148`). Rev 2 allocates one customer cell
  (`design.md:200-201`) without defining it as a paired scenario. One normalized cell cannot carry
  two authored forms and two diagnostic/topology outcomes under the proposed schema.

The owner-given validation and guidance referents are now preserved at their stated force. The
remaining fidelity problem is evidence transformation, not owner-payload loss: SRC-07 silently
changes a bare-self-named evidence row into a feature-chain target, addressed under Data Structure
Clarity.

**Recommendations:** define exact clause dispositions for all affected rows and represent customer
acceptance as two linked cells or one explicitly paired scenario with two complete coordinates.

### 2. Pattern Consistency

**Assessment:** Concerns

Reuse of the contract's D-section, Appendix B, Appendix C, invariant numbering, and proof coordinate
now follows established patterns (`design.md:30-42,68-81`). Keeping verification `Status` as test
state also matches the matrix's schema.

- **V2-M3 — The companion migration damages the archive.** Moving
  `.project/completed/20260720_constraint-execution-lifecycle-contract/spec.md` and replacing it with
  a stub removes the completed item's actual spec from the current archive (`design.md:154-162,264-266`).
  That conflicts with the archive's institutional-memory, reuse, and audit-trail purposes
  (`.project/completed/README.md:49-54`) and the changelog's record that the spec is an archived
  deliverable (`.project/completed/CHANGELOG.md:92-100`). Git history does not preserve current
  path-and-line citations.

Copy the frozen archived spec to the durable concepts home with a provenance header. Leave the
archived file byte-for-byte intact. Amend only the durable copy and update forward-looking authority
pointers. Historical citations then keep resolving to the historical text.

### 3. Abstraction Quality

**Assessment:** Concerns

The authority abstractions are now appropriately small. No new decision or scenario subsystem is
introduced. The remaining problem is inside the scenario cell: one `status` field is being asked to
represent two independent facts.

`TARGET`, `UNSUPPORTED`, and `LANGUAGE-REJECTED` are contract dispositions. `BLOCKED` is a proof or
certification state (`design.md:215-219`). A supported target whose mutation evidence is missing is
both `TARGET` and `BLOCKED`; the current model cannot express that. Use separate fields such as:

- `expected_disposition`: `SUPPORTED | UNSUPPORTED | LANGUAGE_REJECTED`
- `certification_state`: `UNPROVEN | BLOCKED | CONTRADICTED_AT_HEAD | CERTIFIED`

The second field should name missing evidence and the owning item when blocked.

### 4. Duplication Avoidance

**Assessment:** Pass with note

The separate register and matrix files are gone. Appendix C is singular, and the companion's
scenario table becomes a citation (`design.md:147-162`). This closes the material v1 duplication
finding.

The plan should state one projection rule for `LC-SI-*`: either the contract owns behavioral wording
and `LC-SI-*` rows cite it while adding IDs/grades/checkability, or the requirements own detailed
wording and contract invariants cite those IDs. Without that rule, the grep-based one-home check
cannot distinguish an allowed projection from a duplicated rule (`design.md:244-245,329-335`).

### 5. Data Structure Clarity

**Assessment:** Fail

- **V2-M1 — Sparse-cell derivation is not reproducible.** The categories listed at
  `design.md:195-202` sum to 26 exactly, yet the expected count is “26 ± a few.” Validation later
  calls them four row sources although seven additive categories are listed
  (`design.md:331-333`). More importantly, the route matrix's four blocked bullets are not four
  cells: off-default mutation applies to every supported cell, while shadowing/specialization and
  qualified/chain cross-consumer gaps can each require several cells
  (`.project/active/source-identity-route-evidence-spike/route-matrix.md:43-57`). Route-matrix row 11 also already
  covers unbound formals, so adding a separate unbound-formal cell needs a merge or distinction rule.
  Define a set-union/deduplication rule, exact source-to-cell mapping, exact expected count, and N/A
  rules. Evidence gaps belong on affected cells rather than becoming one cell per bullet.
- **V2-M2 — SRC-07 changes the evidence's authored form.** The example claims feature-chain
  `plant.R` while citing Item-2 route-matrix row 1 as the contradictory HEAD observation
  (`design.md:208-213`). Route-matrix row 1 is bare self-named
  (`.project/active/source-identity-route-evidence-spike/route-matrix.md:18`), and qualified/chain
  cross-consumer behavior is explicitly unobserved
  (`.project/active/source-identity-route-evidence-spike/route-matrix.md:55-57`). Preserve the evidence coordinate
  exactly. A feature-chain mixed-consumer target may be derived from SI semantics plus the customer
  topology, but it must cite both sources and carry the missing cross-consumer fixture as blocked
  evidence. The bare-self-named row remains a separate unsupported diagnostic cell.
- Language-rejected models cannot exercise snapshot or relocated replay. The rule that every cell
  carries `live = snapshot = relocated` therefore needs applicability exceptions
  (`design.md:203-204`). A load-rejected cell should state route obligations that end at load and mark
  downstream replay as N/A.

**Recommendations:** separate disposition from evidence state, derive cells by set union rather than
additive bullet counts, define exact N/A rules, and replace SRC-07 with evidence-faithful cells.

### 6. Route Safety

**Assessment:** Concerns

There are no runtime endpoints in Item 3, and the artifact authority route is explicit. Acceptance
routes are not fully safe because rev 2 applies replay parity to cells that cannot reach capture or
replay. Define per-disposition route applicability and the exact boundary at which unsupported and
language-rejected forms must stop.

### 7. Bets & Decisions Integrity

**Assessment:** Concerns

B1–B4 are now genuine, falsifiable bets with named failure outcomes (`design.md:100-118`). B2 follows
through by choosing the existing Appendix C home and stating what happens if it becomes too large.
B4 honestly says rejected deferrals can add evidence work.

- **V2-M4 — The checkpoint sequence is internally impossible.** Agenda item 7 asks the owner to
  ratify the assembled disposition table (`design.md:221-240`), but D7 and the implementation
  sequence say checkpoint first, then disposition-table drafting (`design.md:163-168,282-286`).
  Either prepare the full provenance-graded table as the checkpoint packet, or split the interaction:
  decide homes/semantics first, draft the table, then ratify the assembled table. Because homes and
  semantic rulings determine the file-level plan, hold the first checkpoint during review
  finalization, before `my-plan`, rather than calling it an implementation step.

Most key decisions now name the simpler rejected alternative. D6's `git mv` choice needs the safer
copy-and-freeze alternative above.

### 8. Reader Comprehension

**Assessment:** Concerns

The ownership table and authority diagram make the system understandable in one pass. This is a
substantial improvement over rev 1.

The representative cell currently teaches the wrong evidence model by merging a bare-self-named
observation, a feature-chain referent probe, and a mixed-consumer target without labeling that
derivation. The “26 ± a few” count also undercuts the claim that the schema is bounded. Fixing
V2-M1/V2-M2 will close the comprehension concern.

---

## Issues by Severity

### Critical

- None. The fundamental architecture is now sound.

### Major

- **V2-M1 — Sparse scenario derivation is not deterministic:** blocked bullets are treated as cells,
  overlapping sources lack a deduplication rule, semantic disposition is mixed with proof state, and
  the count is inexact. — Data Structure Clarity / Spec Compliance
- **V2-M2 — SRC-07 changes the authored form of its cited evidence:** separate the unsupported bare
  self-binding cell from the derived feature-chain target and carry the missing cross-consumer proof
  explicitly. — Data Structure Clarity / Capture Fidelity
- **V2-M3 — `git mv` plus stub removes the historical companion spec from the archive:** copy the
  frozen artifact to its durable home and leave the archive intact. — Pattern Consistency
- **V2-M4 — The checkpoint ratifies an artifact before it exists:** prepare the disposition table as
  checkpoint input or use a decision checkpoint followed by final ratification. — Bets & Decisions
- **V2-M5 — Verification-row disposition is incomplete:** there are seven affected rows, not eight;
  give every affected clause an exact row-local `PARTIAL`, `FAILED`, or `SUPERSEDED` annotation while
  preserving test `Status`. — Spec Compliance / Data Structure Clarity

### Minor

- **V2-N1 — Stale-status correction is incomplete:** cite both the 41/41 composed-proof record and the
  changelog's merged state, and replace or label the full stale proof sections rather than adding one
  header pointer. The release record itself still says merge pending. — Pattern Consistency
- **V2-N2 — D6 uses an incomplete source path:** `design.md:155-156,266` omits the `.project/`
  prefix from the completed-spec path. Use the exact repository path in design and plan. — Reader
  Comprehension
- **V2-N3 — LC-SI projection rule is implicit:** define which layer owns behavioral wording and how
  the other cites it so the one-home validation is mechanically meaningful. — Duplication Avoidance

---

## Recommendations

1. Redefine the Appendix C scenario schema with separate disposition and certification fields,
   exact route applicability, an exact deduplicated cell count, and a source-to-cell mapping.
2. Replace SRC-07 with evidence-faithful source and target cells; represent exact-customer acceptance
   as two linked cells or an explicitly paired scenario.
3. Copy the archived companion into its durable concepts home; do not move or stub the frozen
   archived deliverable.
4. Prepare the provenance-graded disposition table before the owner checkpoint, or split decision
   and ratification checkpoints. Resolve homes and semantic rulings before `my-plan`.
5. Correct “eight rows” to seven and define clause-level `PARTIAL`/`FAILED`/`SUPERSEDED` annotations
   for CL-05, IR-06/07, SVM-01/02/04, and VBR-10.
6. Reconcile complete stale-status sections against both the proof record and the merged-state
   changelog; state the LC-SI projection rule explicitly.

---

## Resolutions

No v2 owner resolutions are recorded yet. The design-author note in the prior review was evaluated
as proposed closure and is reflected in the V1 Finding Closure Audit above.

---

**Overall:** Revise

**Next Steps:** Incorporate V2-M1 through V2-M5, then re-run `my-design` (or return to the design-agent
session) with this review. Resolve the artifact-home and checkpoint decisions before `my-plan`. The
reviewer does not edit the design.
