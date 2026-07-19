# Epic: Constraint-Expression Gap Closure (PR-Gating Fix Wave)

**Epic ID**: GAP-CLOSE
**Status**: Local Scope Certified — external F1 normalization remains open
**Priority**: P0 (gates the CONSTRAINT-EXEC PR wave merge)
**Created**: 2026-07-18
**Estimated Effort**: 4–5 days

---

## Executive Summary

Close all ten verified findings and the hygiene tail from the final constraint-expression gap
review on the open PR branches (sysml-codegen #9, agentic-mbse #11) before the wave merges.
Every finding was independently confirmed with reproductions; the fixes are localized boundary
and totality corrections — no architecture change. The owner's F1 ruling is settled: a raised
exception in constraint arithmetic is an execution failure, never a verdict; keep everything
small and clean.

**Critical Success Factor**: Every High finding (F1, F2, F3, F5) is closed by a fix whose
regression test fails at current HEAD, and both PRs are re-pushed with green full suites — the
wave merges without known crash, wrong-verdict, install, or silent-loss defects.

---

## Why This Epic?

**Current State**:
- The CONSTRAINT-EXEC wave (PR #9 / #11) is certified for its item contracts, but an
  independent gap review found — and verification confirmed — ten boundary defects: admitted
  arithmetic can crash the evaluator (F1); sanitized predicate names can collide and silently
  execute the wrong predicate (F2); package metadata cannot express the v3 lockstep (F3);
  mixed BLOCK+NON_NUMERICAL batches suppress warnings (F4); anonymous excluded statements
  collide with a misleading error (F5); transactional assignment skips defaulted fields (F6);
  malformed xor/implies arities warn instead of default-denying (F7); contradictory quantity
  facts silently admit (F8); the package verifier ignores unrecorded directory symlinks (F9);
  and wheel-shipped docs still teach v2 semantics (F10), plus nine confirmed hygiene items.
- Merge is held on the High findings.

**Future State**:
- All ten findings fixed on the PR branches with adversarial regression tests; profile
  default-deny is total over malformed shapes; the exceptional-arithmetic policy is
  implemented per the owner ruling; docs and package metadata match v3 reality; the wave
  merges clean.

---

## Source Documents

- `.project/research/20260718-123558_constraint-expression-final-gap-review.md` (research —
  the gap review, findings F1–F10 + hygiene)
- `.project/research/20260718_gap-review-verification.md` (research — independent
  verification: all findings confirmed, corrected severities, **owner's F1 ruling recorded**)
- `.project/active/numerical-constraint-profile/{spec,design}.md` (contract context for the
  v3 three-way rule the fixes must preserve)
- `.project/concepts/constraint-execution-and-design-space-studies-claude.md` (Design
  Principle 4 and the failure-taxonomy invariants the F1 ruling anchors to)

---

## Success Criteria

- [ ] F1: an exception raised in generated constraint arithmetic surfaces as the normalized,
      phase-tagged execution failure naming the constraint — never a raw traceback, never a
      verdict; no arithmetic guards added to generated predicates; existing Kleene value
      behavior byte-stable; divide-by-zero and overflow tests assert **failure**.
- [x] F2: a post-sanitization predicate-name collision is impossible to ship — generation
      either fails deterministically naming both raw keys or emits collision-free names; a
      two-predicate collision fixture proves the wrong-predicate execution can no longer occur.
- [x] F3: agentic-mbse's package version is bumped and codegen's floor raised so metadata-only
      resolution cannot pair codegen with a pre-v3 companion; recorded evidence of the pairing
      check.
- [x] F4/F5: a mixed BLOCK+NON_NUMERICAL batch emits every non-numerical warning before
      halting; two anonymous statements produce distinct excluded records for each exclusion
      kind; the ID-collision error no longer misdiagnoses legal models.
- [x] F6/F9: a rejected assignment leaves a defaulted-field model unchanged; an unrecorded
      directory symlink is a fatal, path-specific verification diagnostic.
- [x] F7/F8: malformed xor/implies arities and contradictory quantity unit facts BLOCK
      (default-deny), with codec-roundtrip regressions.
- [x] F10 + hygiene: the three durable doc surfaces teach v3; exports, docstrings, the loader
      comment, and the D5 warning message are corrected; promoted diagnostics no longer carry
      "is not executed" prose in halt messages; artifact whitespace is clean.
- [ ] Wave gates: both full suites green (licensed codegen + companion), fixture byte-identity
      preserved except justified diffs, both PRs re-pushed with updated comments, and every
      fix's regression test demonstrably fails at pre-fix HEAD.

---

## Epic Strategy

**Value delivery path:** unblock the CONSTRAINT-EXEC wave merge. Items 1–4 are independent
behavior fixes (Item 4 in the companion repo, parallel-safe); Item 5 is the strictly-last
closeout that makes docs/metadata describe the final behavior and re-runs the wave gates.

**Decomposition rationale:** grouped by defect surface, not by finding number — runtime
generation (Item 1), lowering (Item 2), model/seal boundaries (Item 3), profile (Item 4),
docs/metadata (Item 5) — so each item's spec/design reasons about one seam. Every fix is
test-first with a regression that fails at pre-fix HEAD (the verification record's probes are
the test recipes).

**De-risking:** none of the items rests on an unverified bet — every defect already has an
independent reproduction with exact mechanics (`20260718_gap-review-verification.md`). The two
spec-stage decisions are named inside Items 2 and 4.

---

## Backlog Items

### Item 1: Runtime Evaluation Contract — Exceptional Arithmetic and Predicate Naming (F1, F2)

**Implementation status (2026-07-18):** sysml-codegen leg complete. F2 is closed; F1 codegen
propagation is characterized. End-to-end F1 remains open on external
`[GAP-CLOSE-F1-TEAX-NORMALIZATION]`.

**Type**: Implementation (sysml-codegen)
**Effort**: 1 day (spec 1h, design 1.5h, plan 1h, execute 5h)
**Dependencies**: None

**Objective**: A raised exception in generated constraint arithmetic surfaces as the
normalized execution failure per the owner's F1 ruling, and a post-sanitization predicate-name
collision can never silently execute the wrong predicate.

**Scope**:
1. **F1 (owner ruling — settled, do not relitigate):** no arithmetic guards in generated
   predicates; the raise propagates and is normalized at the evaluation-failure seam into a
   phase-tagged outcome naming the constraint and cause — never a raw traceback. Kleene value
   behavior byte-stable. Narrow the template docstring
   (`templates/constraint_module.py.jinja2:1-5`) to the DP4 promise: never raises *because the
   verdict went against the assertion*.
2. **F2:** post-sanitization/case-fold uniqueness enforcement at `compile_shared_predicates`
   (`generation/modules.py:117-131`) — deterministic generation error naming both raw keys, or
   a stable hash suffix (design decides; reject-on-collision keeps existing baselines
   byte-identical, hash-suffix churns them — weigh in design).
3. Tests: divide-by-zero, `0 ** negative`, exponent overflow → **failure** (not indeterminate,
   not verdict); nested-connective variant; a two-predicate collision fixture (opposite
   verdicts) proving wrong-predicate execution is impossible; Kleene non-finite-value suite
   unchanged.

**Out of Scope**:
- Value-domain reasoning in the profile; any change to indeterminate semantics.
- C901 refactors (`[CONSTRAINT-ARCH-UNIFY]`).

**Success Criteria**:
- [ ] Div-zero/overflow tests assert a normalized execution failure naming the constraint;
      each is RED at pre-fix HEAD.
- [x] Collision test RED at pre-fix HEAD; post-fix either fails generation naming both raw
      keys or emits collision-free names, per the design decision.
- [x] Existing Kleene/value tests and (if reject-on-collision) generated baselines
      byte-identical.

**Required Reading**: both research docs (F1/F2 sections + the owner ruling);
`docs/architecture` evaluator-failure seam docs as located during design.

**Location**: `.project/active/gap-runtime-contract/`

---

### Item 2: Lowering Outcome Integrity — Warning Order and Excluded Identity (F4, F5) ✅

**Type**: Implementation (sysml-codegen)
**Effort**: 1 day (spec 1h, design 1.5h, plan 1h, execute 5h)
**Dependencies**: None

**Objective**: A halting run still reports every non-numerical statement, and excluded
records mint collision-free identities for legal models.

**Scope**:
1. **F4:** emit the per-statement non-numerical warnings before the blocking raise in
   `lower_constraints` (`analysis/constraint_lowering.py:752-786`); a halting run still
   produces no package/catalog.
2. **F5:** the excluded-record mint keeps the location-derived `id_component`
   (`:791-798` currently discards it). Spec decision: anonymous-only (named excluded IDs
   stay stable — no fixture churn; the lean) vs all-excluded (churns catf_mfe catalogs
   again). Fix the collision error text that misdiagnoses legal models
   (`assert_unique_constraint_ids`).
3. Tests: mixed BLOCK+NON_NUMERICAL batch (warnings then halt); two anonymous statements per
   exclusion kind (non_numerical, satisfy/unassessed_form, unsupported_owner) → distinct
   records; facts shaped like live extraction output. Update the migration-mapping
   anonymous-corpus guard if a fixture is added.

**Out of Scope**:
- The eligible-anonymous catalog compile-key limitation (pre-existing; `[ANON-ELIGIBLE-KEY]`
  follow-on row, needs an owner ruling on anonymous executable assertions).

**Success Criteria**:
- [x] Mixed-batch test RED at pre-fix HEAD; post-fix every non-numerical warning emitted
      before the halt.
- [x] Anonymous-pair tests RED at pre-fix HEAD (ID collision); post-fix distinct records for
      all three kinds.
- [x] Existing corpus byte-identical if anonymous-only minting is chosen; any churn justified
      in the item record.

**Required Reading**: both research docs (F4/F5 sections incl. the I2-drafting nuance and the
live end-to-end reproduction); `numerical-constraint-profile/design.md` I2/D5.

**Location**: `.project/active/gap-lowering-integrity/`

---

### Item 3: Model and Seal Boundary Guards (F6, F9) ✅

**Type**: Implementation (sysml-codegen)
**Effort**: 0.5–1 day (spec 0.5h, design 1h, plan 0.5h, execute 4h)
**Dependencies**: None

**Objective**: Rejected assignments never leave a model mutated, and the package verifier has
an explicit, enforced symlink policy.

**Scope**:
1. **F6:** replace the `__pydantic_fields_set__` membership condition in
   `_TransactionalAssignmentModel` (`resolution/models.py:16-39`) with an
   initialization-state guard so every post-init assignment prevalidates; mutation tests for
   defaulted-construction objects in both directions (eligible flip, exclusion install),
   asserting unchanged + serializable state after rejection.
2. **F9:** explicit directory-symlink policy in `contracts/verify.py:263-298` — lean: reject
   any directory symlink under the package root outright with a path-specific fatal
   diagnostic (simplest honest integrity rule); tests for escaping and internal directory
   symlinks, stdlib-only.

**Out of Scope**:
- Freezing the models (existing generation guards mutate deliberately).
- Archive/packaging format changes.

**Success Criteria**:
- [x] F6 default-omission probes RED at pre-fix HEAD; post-fix objects unchanged after every
      rejected assignment; `ConstraintCatalogEntry` regression pinned (already-safe).
- [x] F9 dir-symlink probes RED at pre-fix HEAD (ok=True today); post-fix fatal diagnostics
      for both escaping and internal cases.

**Required Reading**: both research docs (F6/F9 sections — the F6 production-exposure
sharpening and F9 case table).

**Location**: `.project/active/gap-boundary-guards/`

---

### Item 4: Profile Default-Deny Totalization (F7, F8, promoted diagnostics) ✅

**Type**: Implementation (agentic-mbse, + codegen test sync)
**Effort**: 0.5–1 day (spec 0.5h, design 1h, plan 0.5h, execute 4h)
**Dependencies**: None (parallel-safe); must land before Item 5.

**Objective**: The v3 profile default-denies malformed shapes totally, and promoted
diagnostics describe what actually happens.

**Scope**:
1. **F7:** arity gate for `xor`/`implies` (exactly two operands) in
   `sysml/executable_profile.py:604-620`, mirroring the adjacent connective gate;
   0/1/3-operand codec-roundtrip regressions.
2. **F8:** `_quantity_ratio_fact` checks dimension consistency before the equal-unit admit
   (`:293-309`), matching `unit_compatibility`'s documented guard order; serialized
   malformed-fact regression.
3. **Promoted diagnostics (hygiene 9):** when containment promotes a warn diagnostic to
   error force, the reason/message must describe a halt with repair guidance, not "is not
   executed"; sync the codegen conformance test pinning the old text
   (`tests/conformance/test_constraint_non_numerical.py:76-87`).
4. **Version ruling:** treat all three as defect fixes *within* v3's documented default-deny
   contract — no v4 bump; record the rationale in the item spec. If design finds a consumer
   whose decisions legitimately change on well-formed input, escalate to the owner before
   proceeding.

**Out of Scope**:
- Any change to well-formed-shape decisions; the admitted matrix is untouched.

**Success Criteria**:
- [x] Malformed-arity and contradictory-ratio tests RED at pre-fix HEAD; post-fix BLOCK with
      named diagnostics.
- [x] Promotion tests assert error-appropriate reason/message; codegen halt test synced.
- [x] Companion suite green; codegen suite green against the updated companion.

**Required Reading**: both research docs (F7/F8 sections incl. reachability analysis and the
D-R3 responsibility argument).

**Location**: `../agentic-mbse/.project/active/gap-profile-totalization/` (companion-side
artifacts), codegen test sync recorded in the same item.

---

### Item 5: Packaging, Docs, and Hygiene Closeout + Wave Gates (F3, F10, hygiene 2/4–8)

**Type**: Docs/metadata + validation
**Effort**: 1 day (spec 0.5h, design 0.5h, plan 0.5h, execute 5h)
**Dependencies**: Items 1–4

**Objective**: Metadata and durable docs describe the shipped v3 behavior, the hygiene tail
is clean, and the wave gates re-run green with both PRs updated.

**Scope**:
1. **F3:** bump agentic-mbse to a real new version (pyproject + `__version__`); raise
   codegen's floor to it; add a metadata-pairing check (declared-metadata smoke test or
   recorded probe) so a resolver cannot legally pair codegen with pre-v3.
2. **F10:** update the three durable surfaces — companion `docs/patterns/constraints.md`
   (wheel-shipped; four outcomes, v3 equality policy, xor/implies behavior), codegen doc 28
   (four outcomes + `excluded_records`), doc 27 (correct the "no lockstep surface" claim).
3. **Hygiene:** export `ConstraintExclusion`/`ConstraintCatalogExcludedRecord` (or mark
   private); fix the `ConstraintCatalog` fingerprint docstring and the loader comment's stale
   line cite; D5 warning carries the diagnostic *messages*, not just reason codes;
   execution-lane conftest discovers the teax sibling relative/env-var with validation;
   artifact trailing-whitespace cleanup (`git diff --check` clean).
4. **Wave gates:** full licensed codegen suite + companion suite at the final commits;
   fixture discipline (byte-identity except justified diffs); push both branches (companion
   by ref if unrelated commits are present); update both PR comments with the fix-wave
   summary and gate evidence.

**Out of Scope**:
- CI infrastructure (follow-on decision for the owner).
- C901 refactors (`[CONSTRAINT-ARCH-UNIFY]`, evidence pointer recorded there).

**Success Criteria**:
- [x] A metadata-only resolution cannot pair codegen with a pre-v3 companion; evidence
      recorded.
- [x] All cited doc lines teach v3 (spot-grep assertions in the item record).
- [x] Codegen non-numerical warnings include the actionable message text (D5 satisfied).
- [x] `git diff --check` clean on both repos' branch ranges.
- [ ] Both full suites green; both PRs re-pushed and commented; merge-order note intact.

**Required Reading**: both research docs (F3 correction — runtime-incompatibility not
import-failure — and OQ3 evidence; F10 citations; hygiene items 2/4–8).

**Location**: `.project/active/gap-closeout/`

---

## Dependencies

**External**: syside license only for any new live captures (none expected).

**Internal**: the open PR wave (#9, #11); merge order #11-first remains load-bearing.

**Item Dependency Graph**:
```
Item 1 (codegen: runtime)      ─┐
Item 2 (codegen: lowering)     ─┤
Item 3 (codegen: boundaries)   ─┼─> Item 5 (closeout + wave gates)
Item 4 (companion: profile)    ─┘
(Items 1–4 mutually independent; 1–3 sequential-on-branch by convenience)
```

---

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| F1's failure-normalization seam is in the runtime/evaluator layer, possibly touching teax | Med | Design locates the existing normalized-failure outcome first; if the seam is teax-side, scope stops at "raise propagates un-mangled + codegen tests assert the raw behavior" and books the teax leg |
| F5/F2 fixes churn generated baselines | Med | Prefer the no-churn variants (anonymous-only mint, reject-on-collision); any churn is diff-reviewed excluded-records/naming-only |
| Item 4's promoted-message change breaks codegen tests mid-wave | Low | The codegen test sync is in Item 4's own scope (coordinated-pair discipline) |
| Version bump (F3) interacts with other agentic-mbse consumers | Low | Floor bump is codegen-side only; companion bump is additive |

---

## Timeline

**Total Effort**: 4–5 days

| Item | Effort | Dependencies |
|------|--------|--------------|
| 1 Runtime contract | 1 d | None |
| 2 Lowering integrity | 1 d | None |
| 3 Boundary guards | 0.5–1 d | None |
| 4 Profile totalization | 0.5–1 d | None (before Item 5) |
| 5 Closeout + gates | 1 d | Items 1–4 |

---

## Lessons Learned (Post-Completion)

*Fill in after epic is complete*

---

**Last Updated**: 2026-07-18
**Next Action**: Run `my-pre-pr` as an explicitly partial wave. Keep F1 and epic completion open.
