# Design Review: Authoritative Source-Identity Contract (SOURCE-IDENTITY Item 3)

**Design:** `.project/active/source-identity-contract/design.md`
**Spec:** `.project/active/source-identity-contract/spec.md`
**Review File:** `.project/active/source-identity-contract/design-review.md`
**Date:** 2026-08-05

---

## Fundamental Assessment

**Concerns.** The core move is right: amend the ratified lifecycle authority before Items 4 and 5
design a fix. The design also correctly keeps implementation out of Item 3 and grounds the contract
in the completed Item-1 and Item-2 evidence.

The authority partition is not sound yet. The lifecycle contract already has an owner-decision
section and a mandatory acceptance matrix (`.project/concepts/constraint-execution-authoritative-lifecycle-contract.md:279-306,410-418`), while its companion spec has a second normative acceptance-scenario table
(`.project/completed/20260720_constraint-execution-lifecycle-contract/spec.md:427-480`). The design
then adds a normative decision register and a third normative acceptance matrix, while also requiring
the contract and companion spec to carry the same SI rules (`design.md:61-83,137-141,149-207`). That
contradicts the design's own "one normative home" rule and creates the parallel-authority risk D1 is
supposed to prevent.

This is repairable without changing the overall approach. Prefer the simpler partition: append
source-identity decisions to the contract's existing decision section, append a normalized
source-identity scenario table to its existing Appendix C, and put provenance-graded `LC-SI-*`
requirements in one durable companion requirements file. If a separate matrix is necessary because
of size, make it the sole normative home for source-identity cells and replace overlapping contract
and companion-spec wording with citations.

**Stage 0 recommendation:** Revise, not Rework. Continue with the amendment approach after the
authority homes, matrix representation, and checkpoint gates are corrected.

---

## Dimensional Review

### 1. Spec Compliance

**Assessment:** Concerns

The design covers all six success-criterion families. It names all observed authoring forms, all
Item-2 source classes, the SI-23 evidence coordinate, validation and guidance obligations, the
verification rows, and the Item-4/5 derivability check (`design.md:164-222,303-315`). It also
preserves the spec's important distinction between observed-at-HEAD evidence and target behavior
(`design.md:133-136`).

Three gaps remain:

- **DR-C1 — Normative ownership is unresolved.** The spec requires one consistent authority chain
  (`spec.md:39-52`). The proposed contract, companion spec, decision register, acceptance matrix,
  existing Appendix C, and existing companion-spec scenarios can all carry overlapping normative
  source-identity statements. Naming the new files from the contract does not by itself establish
  which statement wins if wording diverges.
- **DR-M3 — The checkpoint is wider than B4 admits.** B4 says one open ruling affects only
  library-default cells and REQ-CL-05 (`design.md:102-105`). The agenda also asks the owner to approve
  expression-binding deferral, evidence-gap deferrals, aggregation filing, and the assembled
  register (`design.md:209-222`). D2's artifact-home deviation needs approval too
  (`design.md:112-118`) but is absent from the agenda. Rejecting either deferral can require more
  evidence or new dispositions before the contract is complete.
- **DR-M5 — One owner payload is misidentified.** The design says the SI-15 and SI-16 quotes include
  the preserved `quesiton` typo (`design.md:263-264`). That typo and the "how do you model correctly"
  referent belong to SI-18 (`spec.md:136-140`), not SI-15 or SI-16. The implementation instruction
  can therefore omit or misattribute an owner-given referent. Correct the requirement IDs and state
  where SI-01, SI-15, SI-16, and SI-18 owner wording is preserved verbatim or by path.

The design does not visibly launder an `[INFERRED]` or `[INHERITED]` item into owner origin. It
correctly calls D2 an open deviation from an `[AGENT]` epic path and explicitly requires absorb-grade
auditing (`design.md:112-118,287-289`). The issue is duplicated normative homes, not a detected grade
upgrade.

**Recommendations:** choose one normative home per statement, expand the checkpoint's real gating
scope, and correct the SI-18 payload mapping before planning.

### 2. Pattern Consistency

**Assessment:** Fail

The design reuses the lifecycle contract's invariant numbering, correction-register format,
decision provenance, and evidence-coordinate pattern well (`design.md:28-57,119-145`). Those are
the right existing patterns.

Two proposed extensions do not fit current repository contracts:

- **DR-M1 — Verification status is being used for a second meaning.** The verification matrix is a
  test-traceability table. Its current statuses answer whether a dedicated test exists and passes
  (`docs/architecture/verification-matrix.md:1-23`). `SUPERSEDED` and `PARTIAL`, as proposed in D4,
  answer whether requirement text remains contractually valid. Replacing `PASS` would conflate proof
  execution with contract disposition even though the historical tests still pass.
- **DR-M4 — The archived companion is treated as a mutable current authority.** Project convention
  makes `.project/completed/` an archive and audit trail (`.project/completed/README.md:1-27`). The
  close record says the ratified authority remains the concepts contract and lists the archived spec
  among completed item deliverables (`.project/completed/CHANGELOG.md:74-100`). The design's pointer
  fix redirects the contract to that archived spec and then plans to amend it
  (`design.md:39-41,137-141,240-246`). That needs an explicit durable-companion migration or an owner-
  approved archive exception; it should not be an unstated pattern change.

D2's move of the two new deliverables to `.project/concepts/` is plausible because the contract is a
deliberate durable exception. It is not the repository default: the epic names active-item paths
(`.project/backlog/epic_semantic_source_identity.md:561-567`) and the active-work convention places
deliverables in the item folder (`.project/active/README.md:8-15,31-37`). The design surfaces the
deviation correctly, so this is an owner decision rather than an automatic review rejection.

**Recommendations:** keep test status and contract disposition as separate columns or annotations;
split or migrate the durable companion requirements file instead of silently editing an archive;
record the D2 resolution before changing the epic paths.

### 3. Abstraction Quality

**Assessment:** Concerns

The semantic spine is clear and appropriately small: referent fidelity, declaration plus concrete
occurrence identity, and one runtime source per occurrence (`design.md:59-77`). That is a good mental
model for downstream design.

The artifact abstractions have not earned their separation. A decision register of roughly the
listed form/source/mechanism rows can fit the contract's existing decision/correction structures.
The existing contract already provides Appendix C for mandatory acceptance scenarios. The design
does not explain why extending those structures is worse than maintaining two additional normative
files; D2 just explains why the active item folder is a poor durable home (`design.md:109-118`).

**Recommendation:** remove the extra documents unless size or independent lifecycle requires them.
If retained, define one owner for each statement category: decisions/provenance, behavioral
invariants, graded requirements, scenario cells, and current proof status.

### 4. Duplication Avoidance

**Assessment:** Fail

The design knowingly introduces overlapping representations:

- lifecycle-contract decisions versus the new decision register;
- lifecycle-contract Appendix C versus the new acceptance matrix;
- companion-spec required scenarios versus the new acceptance matrix; and
- contract invariants versus a full `LC-SI-*` projection of SI-01 through SI-23.

The claim that every other appearance will be a citation (`design.md:79-83,224-227`) is incompatible
with D6 and the contract-amendment plan, both of which require source-identity rules to be written in
multiple artifacts (`design.md:137-141,195-207`). Existing contract text gives a workable split:
behavioral authority lives in the contract, while detailed requirement IDs and provenance grades
live in the companion spec (`.project/concepts/constraint-execution-authoritative-lifecycle-contract.md:15-25`).

**Recommendation:** preserve that split and make scenario ownership singular. A traceability table
may map one requirement to several edits, but it must not turn those edits into several independent
normative restatements.

### 5. Data Structure Clarity

**Assessment:** Fail

- **DR-M2 — The acceptance matrix is not implementable as specified.** The listed axes imply six
  authored forms × seven topologies × four consumer sets × three routes: 504 raw combinations before
  the other SI-23 fields (`design.md:179-193`). Many combinations are meaningless. The design gives
  no applicability rules, stable cell ID, normalized row shape, expected row count, or rule for when
  a combined-consumer row substitutes for individual consumer rows. Its completeness rule only says
  each source artifact maps to at least one cell; it does not prove that the necessary interactions
  were selected.
- The proposed verification status change also mixes two data dimensions: test execution state and
  contractual disposition. These need separate fields.
- Several D4 rows are compound. REQ-VBR-10 contains both the still-required specialized-chain
  rewrite and the impermissible self-binding rescue
  (`docs/architecture/verification-matrix.md:586`). REQ-SVM-01/04 may remain as adapters derived from
  the new authority under SI-22 (`spec.md:156-160`), and D4 itself admits the convergence direction of
  REQ-SVM-02 remains useful (`design.md:268-271`). Whole-row supersession loses valid clauses.

**Recommendations:** define a sparse normalized scenario table with stable cell IDs, explicit N/A
constraints, an expected row count, and coverage rules for required interactions. Split compound
verification requirements or attach clause-level dispositions. Keep the existing test status
unchanged until tests themselves stop passing or are replaced.

### 6. Route Safety

**Assessment:** Pass (not applicable to executable routes)

Item 3 adds no runtime routes or endpoints. Its artifact flow is explicit and has no wildcard or
fallback path (`design.md:147-162`). The authority-routing and archived-pointer concerns are covered
under Pattern Consistency and Duplication Avoidance.

### 7. Bets & Decisions Integrity

**Assessment:** Fail

B1 and B3 are genuine, falsifiable bets. They name what fails if evidence or target derivability is
wrong (`design.md:88-101`). B2 is also testable, but the design does not follow through: it says the
existing structures can host the semantics, then creates parallel normative structures without
showing why the existing decision and Appendix C homes are insufficient.

B4 is false as written. Expression-binding and evidence-gap decisions can reopen evidence and
disposition work; D2 can change artifact topology. The drafting order depends on a hidden bet that
the owner will approve all requested deferrals and the new homes. Another hidden bet is that an
archived completed spec can serve as a mutable durable companion without weakening the audit trail.

Most key decisions name rejected alternatives. D5 does not consider the simplest alternative:
extend the lifecycle contract's existing Appendix C. It only rejects editing Item 2's observed route
matrix (`design.md:133-136`). D2 similarly does not consider moving the existing companion
requirements out of the archive while fixing the stale pointer.

**Recommendations:** rewrite B4 to name every checkpoint-dependent artifact and failure outcome;
add the existing-Appendix-C alternative to D5; resolve D2 and the archive-companion choice before
calling artifact homes fixed.

### 8. Reader Comprehension

**Assessment:** Concerns

The Overview and Core Concept give a strong one-pass mental model. The authority diagram is useful,
and the document consistently points readers to evidence.

Understanding breaks at the artifact model. "No new authority document," "two normative
companions," "one normative home," and repeated contract/spec/matrix projections cannot all be true
without a precise ownership rule (`design.md:61-83,149-162`). The acceptance-matrix paragraph also
asks the reader to infer a large multidimensional schema without showing one representative row or
the sparse-selection rule.

**Recommendation:** show one concrete scenario row and one authority-ownership table. State which
artifact is authoritative for each kind of statement and which artifacts contain links only.

---

## Issues by Severity

### Critical

- **DR-C1 — Normative ownership is unresolved:** the design creates overlapping decision,
  requirement, and acceptance authorities while claiming one normative home. Choose one home per
  statement category before implementation. — Spec Compliance / Abstraction / Duplication

### Major

- **DR-M1 — Verification status conflates proof with contract disposition:** retain `PASS`/`UNTESTED`/
  `DEFERRED` as test state and add a separate contract-disposition field; split compound rows before
  superseding clauses. — Pattern Consistency / Data Structure Clarity
- **DR-M2 — Acceptance matrix has no bounded schema:** replace the implicit 504-cell Cartesian
  product with stable sparse cells, explicit applicability rules, an expected row count, and required
  interaction coverage. — Data Structure Clarity
- **DR-M3 — B4 and the checkpoint omit real gates:** include expression-binding and evidence-gap
  outcomes, D2 artifact homes, and their rework consequences; do not call drafting non-blocking until
  those choices are resolved or honestly parameterized. — Spec Compliance / Bets
- **DR-M4 — Archived companion mutability is an unstated architecture choice:** migrate the durable
  requirements companion or obtain an explicit archive exception before editing a completed work
  artifact as current authority. — Pattern Consistency
- **DR-M5 — SI-18 owner payload is misidentified:** preserve and correctly attribute the modeling-
  guidance quote and referent, including the `quesiton` typo. — Spec Compliance / Capture Fidelity

### Minor

- **DR-N1 — Existing authority status is stale:** the contract still says no certified candidate
  exists (`.project/concepts/constraint-execution-authoritative-lifecycle-contract.md:3,27-30`), and
  the archived companion says proof is not established
  (`.project/completed/20260720_constraint-execution-lifecycle-contract/spec.md:47-56`), while the
  release record reports 41/41 completion and the changelog records the merge
  (`.project/completed/20260720_constraint-lifecycle-composed-proof/release-readiness.md:1-8`;
  `.project/completed/CHANGELOG.md:74-100`). If Item 3 keeps these artifacts as current authority,
  either reconcile those status statements or record one precise current-status pointer.

---

## Recommendations

1. Use the existing lifecycle contract decision section and Appendix C unless a measured size or
   lifecycle constraint justifies separate normative companions. If a separate matrix remains, make
   it the sole source-identity scenario authority and convert overlapping sections to citations.
2. Define a durable home for the graded companion requirements. Do not silently turn an archived
   completed-item spec into a mutable current artifact.
3. Specify a sparse acceptance-cell schema with stable IDs, N/A rules, an expected row count, and
   explicit interaction coverage.
4. Keep verification test state separate from contract disposition. Split REQ-VBR-10 and apply
   clause-level treatment to the IR/SVM rows so valid behavior and passing historical tests remain
   visible.
5. Expand and move forward the owner checkpoint: decide D2, unbound defaults, expression-binding
   disposition, and evidence-gap deferrals before final artifact drafting, or state the full
   parameterized rework cost.
6. Correct the SI-18 quote mapping and include a provenance/payload check in the plan traceability
   table.

---

## Resolutions

Recorded by the design agent on 2026-08-05 against design.md rev 2. Items marked **(owner)** are
proposed resolutions that still require the owner's ruling at the Item-3 checkpoint; the rest are
incorporated.

- **DR-C1 — Resolved by ownership table.** Rev 2 removes both proposed companion files. Every
  statement kind has one named home inside the existing structures: dispositions in the contract's
  owner-decision section (D-4+), scenarios in Appendix C, superseded readings in Appendix B,
  graded requirement IDs in the companion spec, test state in the verification matrix. The Core
  Concept carries the explicit ownership table; the one-home rule is a Required Invariant checked
  at audit.
- **DR-M1 — Resolved.** Verification Status stays test-state and is byte-identical before/after;
  contract disposition becomes clause-level footnotes under the affected family tables (REQ-VBR-10
  and REQ-SVM-02 explicitly split by clause). Row restructuring deferred to Item 6.
- **DR-M2 — Resolved.** The scenario schema is sparse and derived, not Cartesian: four named row
  sources, stable `SRC-nn` IDs, an expected count (~26, re-derived at audit), route parity as a
  per-cell obligation rather than a row multiplier, interaction coverage pinned to the six census
  duplicate groups and mixed-consumer cells, and one representative row shown in the design.
- **DR-M3 — Resolved by checkpoint-first (D7).** The checkpoint moves before drafting and its
  agenda now includes the artifact-home decisions (D2/D5/D6) and names the rework consequence of a
  rejected deferral. B4 is rewritten as the honest bet ("decidable in one sitting from evidence in
  hand").
- **DR-M4 — Proposed resolution (owner).** Migrate the companion spec to
  `.project/concepts/constraint-execution-lifecycle-requirements.md` via `git mv` + archived stub,
  fixing the contract's stale `:8` pointer to the new home; no in-place amendment of the archive.
  Checkpoint agenda item 1.
- **DR-M5 — Resolved.** The "quesiton" payload is re-attributed to SI-18; the SI-01, SI-15/16, and
  SI-18 quotes each have a named verbatim landing spot (Required Invariants), and the plan's
  traceability table carries a payload-placement check.
- **DR-N1 — Proposed resolution (owner).** One-line status corrections in contract and companion
  pointing at the 41/41 release record; checkpoint agenda item 6.
- **Bets/decisions dimension** — B2 is now followed through (existing structures actually used,
  with its failure branch defined: split Appendix C subsection out only as an explicit surfaced
  change); D5 names the Appendix C alternative as the selected option; B4 rewritten as above.

---

**Overall:** Revise

**Next Steps:** Resolve DR-C1 and the owner decisions in DR-M3/DR-M4 first. Then re-run `my-design`
(or return to the design-agent session) and point it at this review. The reviewer does not edit the
design.
