# Spec: Lowering Outcome Integrity — Warning Order and Excluded Identity

**Status:** Certified in GAP-CLOSE re-audit (2026-07-18)
**Owner:** Reid W
**Created:** 2026-07-18 14:32 PDT
**Complexity:** MEDIUM
**Branch:** constraint-exec-epic
**Epic:** GAP-CLOSE — Item 2

---

## Problem

Constraint lowering loses information in two legal mixed or anonymous cases. It checks for any
blocking decision before it reports non-numerical siblings, so a model that must halt can hide
every warning for valid statements outside the numerical executor. On the exclusion path, lowering
derives a source-location identity for an anonymous statement and then discards it when minting the
record ID. Two anonymous exclusions therefore receive the same ID and turn warn-and-continue or
ordinary cataloging into a generation error whose text wrongly blames a broken model.

F4 is a reporting-order defect, not a partial-generation feature: warnings must remain observable
when a sibling blocks, but that run must still produce no package or catalog. F5 blocks anonymous
excluded statements observed through live SysIDE extraction. Independent verification corrected
F4 to Medium severity and F5 to High-latent: the anonymous shape is absent from the committed
corpus, but it fails in a live legal model. Together they leave the lowering boundary neither
complete nor faithful to the profile decisions it consumes.

## Success Criteria

- [x] A batch containing at least two `NON_NUMERICAL` statements and a sibling `BLOCK` emits each
      statement's one source-specific warning, in profile/source order, before raising the existing
      generation halt. The halt retains every blocking diagnostic and its actionable repair text.
- [x] The mixed batch produces no returned pipeline context, generated package tree, or constraint
      catalog. Warning emission does not weaken or recover from the halt.
- [x] Anonymous excluded identity is observably
      `(<canonical source referent>, <line>, <column>)`. The canonical source referent identifies
      the logical source file, retains enough ancestry to distinguish two files, and contains no
      absolute checkout or capture-machine prefix. Multiple model input roots remain distinct by a
      stable root discriminator that is also independent of their absolute locations. The ID's
      encoding remains a design choice.
- [x] For each exclusion kind, the anonymous-pair regression matrix proves all three legal source
      distinctions independently: different lines in one file, different columns on one line, and
      different files at the same line and column. Every pair receives distinct, deterministic
      IDs. The three kinds are `non_numerical`, `satisfy` / `unassessed_form`, and
      `unsupported_owner`.
- [x] Each `non_numerical` pair emits both warnings and retains both canonical locations. Each
      `satisfy` / `unassessed_form` and `unsupported_owner` pair emits no profile warning. All three
      kinds produce two excluded records with the expected kind and source association.
- [x] For the same anonymous source, repeated live lowering, snapshot replay, and equivalent model
      trees under different absolute checkout roots produce byte-identical constraint IDs,
      applicable warning values, canonical exclusion locations, and serialized excluded records.
      Regression facts preserve the missing name, missing qualified name, and non-null
      `LocationFact` shape observed in the verified live SysIDE reproduction.
- [x] A kept adversarial uniqueness regression injects two genuinely different concrete records
      with the same `constraint_id`. Uniqueness validation still halts, names the duplicate ID, and
      distinguishes both records by their available source and owner identity. The diagnostic does
      not blame a legal anonymous model or describe the duplicate as an unavoidable hash collision.
- [x] Saved pre-fix evidence runs the mixed warning-plus-halt family and all three anonymous-pair
      kinds against the exact coordinated baseline: sysml-codegen
      `6db321225a5c8568db0287b67ed1d04c03079cc2`, agentic-mbse
      `4ed2a0728ea49298666415cd389d9a6173a81a3e`, and
      `PROFILE_SEMANTIC_VERSION == "executable-profile/v3"`. The mixed test is RED because warnings
      are absent before the expected halt. Each anonymous-kind test is independently RED because
      the pair collides. Every record includes both revisions, the profile version, focused
      command, and defect-specific failure output; setup, license, or unrelated failures do not
      count.
- [x] Direct before/after evidence pins one exact named constraint ID for each exclusion kind:
      `non_numerical`, `unassessed_form`, and `unsupported_owner`. Each post-fix ID is byte-identical
      to its value at the coordinated pre-fix baseline; a corpus hash or fixture-wide comparison
      alone does not satisfy this criterion.
- [x] Existing named fixtures and their generated artifacts are byte-identical before and after
      this item. If an anonymous fixture is added, its reviewed fixture changes are limited to that
      new coverage and the migration-mapping anonymous-corpus guard is updated to use the canonical
      source identity rather than silently weakening the guard.

## Known Requirements

- **[NEED]** A halting F4 run reports every `NON_NUMERICAL` sibling before the `BLOCK` raises, while
  producing no package or catalog. Owner-stated for GAP-CLOSE Item 2 in the stage input.
- **[NEED]** F5 preserves location-derived identity for anonymous excluded statements and corrects
  the misleading collision error. Owner-stated for GAP-CLOSE Item 2 in the stage input.
- **[NEED]** Regression evidence must be RED at the pinned pre-fix revision for mixed warning-plus-
  halt behavior and anonymous pairs in all three exclusion kinds: `non_numerical`,
  `satisfy` / `unassessed_form`, and `unsupported_owner`. Owner-stated for GAP-CLOSE Item 2 in the
  stage input.
- **[NEED]** The regression facts retain live extraction shape, and fixture changes follow byte
  discipline. Owner-stated for GAP-CLOSE Item 2 in the stage input.
- **[NEED]** Anonymous IDs remain stable across live lowering, snapshot replay, and different
  checkout roots. Their observable source identity does not depend on an absolute path.
  Owner-stated in the 2026-07-18 spec-review revision request.
- **[NEED]** Named-ID byte stability is proved directly for every exclusion kind, and pre-fix RED
  evidence pins both sysml-codegen and agentic-mbse revisions. Owner-stated in the 2026-07-18
  spec-review revision request.
- **[NEED]** Correcting anonymous identity and collision wording does not weaken uniqueness
  validation; a genuine duplicate-ID regression must still halt with a truthful diagnostic.
  Owner-stated in the 2026-07-18 spec-review revision request.
- **[INHERITED]** A non-numerical statement produces exactly one warning per tool that runs. The
  codegen warning includes statement identity, rendered location, and actionable diagnostics in
  walk order. Sources: `.project/active/numerical-constraint-profile/design.md`, I2 and D5.
- **[INHERITED]** Live and snapshot routes produce identical warning values, exclusions, halts, and
  admitted behavior for the same facts. Source:
  `.project/active/numerical-constraint-profile/design.md`, I5.
- **[INFERRED]** The excluded-ID change is anonymous-only. Anonymous exclusions must include their
  already-derived location component in the stable identity, while named excluded IDs remain
  byte-identical. This is an agent-selected, reviewable scope decision. It follows Item 2's lean
  recommendation and confines the fix to verified F5; changing all excluded IDs would churn valid
  named catalogs without evidence of a named-identity defect. Sources:
  `.project/backlog/epic_gap_close.md`, Item 2; both F5 research records; current lowering and named
  catalog fixtures.
- **[INFERRED]** An anonymous assessed statement without a source location remains a generation
  error for this item because no portable source identity can be established. This preserves the
  current boundary at `src/sysml_codegen/analysis/constraint_lowering.py`,
  `_source_local_identity`; the upstream schema still permits a missing location, so this is an
  agent-grade scope decision rather than a hard interface constraint.
- **[INFERRED]** The pre-fix evidence record and named-fixture byte comparison are PR-gating
  controls inherited from the agent-authored epic, not owner-originated product behavior. Source:
  `.project/backlog/epic_gap_close.md`, Item 2 and wave success criteria.

## Non-Goals

- Supporting or changing compile grouping for eligible anonymous assertions. The pre-existing
  `"<anonymous>"` predicate-definition-key limitation remains booked as `[ANON-ELIGIBLE-KEY]` in
  `.project/backlog/BACKLOG.md` and still requires an owner ruling.
- Changing profile classification, diagnostic force, warning contents, or the v3 admitted matrix.
- Returning a partial catalog, computation graph, or generated package after any `BLOCK` decision.
- Changing IDs for named eligible or named excluded constraints.
- Refactoring lowering into new architectural phases or absorbing `[CONSTRAINT-ARCH-UNIFY]` work.
- Closing any GAP-CLOSE item other than Item 2.

## Open Questions / Deferred to design

- Choose how lowering guarantees warning-before-halt ordering while preserving one warning per
  statement and the current decision order. The contract does not choose between a reporting
  pre-pass and an aggregated preflight result.
- Define the encoding of the canonical source referent, stable multi-root discriminator, anonymous
  ID, and duplicate-error rendering. The design may choose the mechanism but may not omit file,
  line, or column identity, use an absolute-root prefix, or change named IDs.
- Choose the evidence-file format and focused test organization while retaining the pinned
  revision, commands, and failure output required by the success criteria.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_gap_close.md`, Item 2
- **Required Reading:**
  - `.project/research/20260718-123558_constraint-expression-final-gap-review.md`, F4/F5
  - `.project/research/20260718_gap-review-verification.md`, F4/F5 including corrected severity
    and live reproduction
  - `.project/active/numerical-constraint-profile/design.md`, I2/D5
- **Current implementation:**
  - `src/sysml_codegen/analysis/constraint_lowering.py`
  - `tests/conformance/test_constraint_lowering.py`
  - `tests/conformance/test_constraint_non_numerical.py`
  - `tests/conformance/test_constraint_migration_mapping.py`
  - `tests/unit/test_concrete_constraint_model.py`
- **Tracked follow-on:** `[ANON-ELIGIBLE-KEY]` in `.project/backlog/BACKLOG.md`
- **Design:** `.project/active/gap-lowering-integrity/design.md` (to be created)

---

**Next Steps:** Proceed to `my-design`.
