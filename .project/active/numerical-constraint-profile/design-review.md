# Design Review: Numerical Constraint Executable Profile

**Design:** `.project/active/numerical-constraint-profile/design.md`
**Spec:** `.project/active/numerical-constraint-profile/spec.md`
**Review File:** `.project/active/numerical-constraint-profile/design-review.md`
**Date:** 2026-07-18

---

## Fundamental Assessment

**Concerns, but fundamentally sound.** Keeping the existing profile walk, adding an explicit
non-numerical outcome, preserving hard failures, and projecting non-executed usages into the
catalog is the right-sized approach. It reuses the existing live/snapshot lowering path and does
not need a new pipeline.

The design needs revision before implementation. Several load-bearing details are either false in
the current codebase or left open where they affect the contract: BLOCK diagnostics do not surface
the required fix, mixed-predicate behavior is not settled by the spec, exclusions are not total
across every lowering route, and the claimed second profile-version pin does not exist. These are
repairable without replacing the core approach.

---

## Dimensional Review

### 1. Spec Compliance

**Assessment: Fail**

- **Malformed-claim errors cannot name the fix as designed.** The spec requires a malformed
  numerical error to name the statement, construct, and fix, and specifically requires numerical
  equality to name its rewrite (`spec.md`, Success Criteria 3 and 5). D5 says the BLOCK halt
  message is unchanged, while the current formatter only emits identity, location, construct, and
  reason. It does not emit `EligibilityDiagnostic.message`, where the design puts rewrite guidance
  (`design.md`, D5 and Implementation Notes;
  `src/sysml_codegen/analysis/constraint_lowering.py:729-742`). Recommendation: change the BLOCK
  rendering contract to include the actionable diagnostic message and test the exact required
  content for equality, unsafe units, unresolved operands, and unsupported constructs.

- **Exact companion-revision compatibility is not durably designed.** The spec requires codegen
  to prove compatibility against the exact companion revision. A v3 semantic string proves only
  that the installed companion claims v3 behavior. The dependency remains a version range/local
  editable source, and the design records an exact-commit test run without defining durable CI,
  lock, or artifact evidence (`design.md`, D3, coordinated-pair order, and Validation Approach;
  `pyproject.toml:23-25,64-65`). Recommendation: define the durable revision evidence and the gate
  that checks it, or explicitly narrow the success criterion with the owner.

- **Mixed predicates silently acquire a semantic rule.** D2 decides that a statement such as
  `(x > 0) and flag` becomes NON_NUMERICAL when the numerical branch is valid, so the numerical
  claim is not executed. The spec settles root ordering/arithmetic and several clearly
  non-numerical families, but it does not settle mixed numerical/non-numerical composition. This is
  a challengeable `[INFERRED]` boundary, not an owner-originated settled item (`spec.md`, Known
  Requirements `[INFERRED]` structural classification; `design.md`, D2). Recommendation: surface
  the premise conflict to the owner and record the chosen outcome with examples before treating it
  as fixed.

- **Source-location availability is an unstated prerequisite.** The spec requires every
  non-numerical warning to name its source location, but both `UsageDecision.location` and
  `EligibilityDiagnostic.location` are optional. The design promises `file:line` without proving
  that every assessed assertion has a location (`design.md`, D5/I2;
  `../agentic-mbse/src/agentic_mbse/sysml/executable_profile.py:101-120`). Recommendation: either
  make location mandatory for assessed assertions and validate it, or take an owner-approved
  fallback back to the spec.

- **Capture fidelity needs correction.** The design says the spec's “all tags” are settled and
  lists the structural classifier as fixed. Ratified `[INFERRED]` items remain challengeable under
  the project's capture-fidelity rule. The mixed-predicate ambiguity shows why that distinction
  matters (`design.md:18-19, Next-Stage Handoff`; `spec.md`, `[INFERRED]` requirements).

### 2. Pattern Consistency

**Assessment: Concerns**

- **The two-pin model does not match the code.** The snapshot loader does not import or check
  `PROFILE_SEMANTIC_VERSION`; its guard checks constraint-facts and expression-IR schema versions.
  Offline rebuild already reaches the real profile pin through shared lowering
  (`design.md:55-57,125-127,202-203,222`; `src/sysml_codegen/snapshot/loader.py:199-213`;
  `src/sysml_codegen/analysis/constraint_lowering.py:720-725`). Recommendation: keep one
  centralized runtime compatibility check in shared lowering and correct D3/I6, unless snapshots
  will record the capture-time profile version. Adding a duplicate loader literal would add drift
  without proving capture-time semantics.

- **The consumer inventory is incomplete.** The design says codegen consumes the profile only in
  `lower_constraints`, but `collect_bare_actual_demand` also calls `evaluate_profile` and filters
  ADMIT decisions (`design.md:37-42,99-102`;
  `src/sysml_codegen/analysis/constraint_lowering.py:405-440`). That helper is safe under the
  proposed fourth outcome, but it belongs in the inventory and validation plan. The version pin
  also cannot protect unknown consumers inside agentic-mbse or third-party users of the public
  profile API.

- The positive pattern match is real: live and snapshot builds share lowering and catalog
  assembly, and the model contract embeds the catalog. A single warning site and a catalog
  projection can therefore satisfy parity and downstream visibility without a new route.

### 3. Abstraction Quality

**Assessment: Concerns**

- `NON_NUMERICAL` earns its place. It keeps warning-only statements distinct from BLOCK and from
  form-gated UNASSESSED, so consumers do not infer force from reason strings.

- **The exclusion abstraction is under-specified and creates parallel state.** D6 proposes
  optional exclusion fields on `ConcreteConstraint` and a second excluded-record model, but does
  not state the invariant tying those fields to `eligible=False` or preventing incompatible
  combinations. Recommendation: use one typed nested exclusion payload with a kind tag, reasons,
  and location, required exactly when `eligible=False`, then project or reuse that payload in the
  catalog. Keep the existing full source-record rework out of scope.

- Adding a duplicate profile literal to the snapshot loader would be unnecessary indirection. The
  shared lowering seam already provides the behavior gate for both routes.

### 4. Duplication Avoidance

**Assessment: Concerns**

- Optional exclusion fields plus a separately shaped excluded-record model would duplicate the
  same classification and invite drift. A single validated exclusion payload should be the source
  of the catalog projection.

- A second hard-coded profile-version comparison in the snapshot loader would duplicate the
  lowering check without adding protection. If capture-time semantics matter, store the profile
  version in the snapshot instead of comparing two installed-code literals.

- The rest of the design reuses existing walks, warnings, lowering, graph, and contract paths well.

### 5. Data Structure Clarity

**Assessment: Fail**

- **Not every current non-execution route has an exclusion kind.** Lowering creates
  `eligible=False` when either the profile rejects a usage or its owner kind is outside
  `part_def`/`calc_def`/`package`. A profile-ADMIT usage with an unsupported owner kind therefore
  has neither `unassessed_kind` nor diagnostics. D6 promises a reasoned excluded record for every
  non-executed usage but names only NON_NUMERICAL and form-UNASSESSED
  (`design.md`, D6/I2; `src/sysml_codegen/analysis/constraint_lowering.py:748-776`). Recommendation:
  define an owner-kind exclusion outcome/reason, or split the lowering condition so every
  `eligible=False` record has one total, validated cause.

- The exact excluded-record schema is deferred to plan stage even though identity, reason
  cardinality, and invariants determine whether the design is sound. Specify the tag and required
  fields in the design. In particular, define ordered reason aggregation for the spec's one warning
  per statement.

- L4 metric semantics are open, not merely its label. The current admission-rate denominator is
  ADMIT + BLOCK. Adding NON_NUMERICAL only as a count can display 100% for a model with many
  excluded statements and no executable numerical assertions. Define and name the denominator in
  the design (`../agentic-mbse/src/agentic_mbse/validation/level4_constraints.py:67-76`).

### 6. Route Safety

**Assessment: Pass**

No network or application routes are introduced. The relevant execution routes are explicit:
live and snapshot generation converge on shared lowering, and the catalog reaches the generated
model contract. The validation plan should continue to compare warning values and excluded-record
values across both routes, not only eligible IDs and fingerprints.

### 7. Bets & Decisions Integrity

**Assessment: Concerns**

- B1 is a genuine bet, but its riskiest edge is hidden in D2: the design assumes local diagnostic
  force can express whole-statement intent for nested and mixed predicates. `xor`/`implies`
  currently stop without walking their operands, while error-dominates-warn requires enough
  traversal to discover malformed numerical branches (`design.md`, B1/D2;
  `../agentic-mbse/src/agentic_mbse/sysml/executable_profile.py:565-569`). State the recursion and
  context rules explicitly, including `(x > 0) xor (y > 0)`, `(x > 0) and flag`, and malformed
  numerical branches under a warning-family connective.

- B2 is cheap to test and should not remain unevidenced through design review. Committed fixtures
  contain equality expressions, even if several are blocked or form-UNASSESSED today. Run the
  disposition census before planning and record which usages actually change family.

- B3's “pin makes unknown consumers fail loudly” consequence is false outside the one codegen
  gate. Scope the bet to searched in-repo consumers and require a consumer census; do not claim
  protection for public or third-party consumers.

- D1, D5, D7, D8, and D9 name real alternatives and give sound rejection reasons. D3 and D6 need
  the revisions above before their alternatives can be evaluated honestly.

### 8. Reader Comprehension

**Assessment: Concerns**

The core concept is clear and the design gives a usable mental model. Comprehension breaks where
the model disagrees with the code: the “four consumers” diagram shows only three named consumers,
omits the bare-actual demand helper, and presents two semantic-version pin sites that do not exist.
The excluded-record flow also hides the unsupported-owner route. Correcting those points will make
the diagram trustworthy.

The L6 ERROR-gating question need not remain deferred. The validator already sets success false
when any issue has ERROR severity
(`../agentic-mbse/src/agentic_mbse/validation/level6_architecture.py:953`). Record that evidence in
the design and keep only the behavior test as plan work.

---

## Issues by Severity

### Critical

- None.

### Major

- **M1 — BLOCK output omits required fix guidance:** unchanged codegen formatting cannot satisfy
  the malformed-claim and equality-rewrite success criteria. — Spec Compliance
- **M2 — Mixed-predicate semantics are silently fixed:** D2 chooses whole-statement warning for a
  valid numerical branch combined with a non-numerical branch, although the spec does not settle
  that behavior. — Spec Compliance / Bets & Decisions Integrity
- **M3 — Exact companion revision is not durably proven:** a semantic-version string plus a
  one-time exact-commit test does not identify the tested dependency revision. — Spec Compliance
- **M4 — The two-pin architecture is factually wrong:** the snapshot loader has schema pins, not a
  profile-semantic pin; duplicating the lowering literal would add drift. — Pattern Consistency
- **M5 — Exclusion state is neither total nor structurally valid:** unsupported owner kinds have no
  exclusion reason, and optional parallel fields allow contradictory records. — Data Structure
  Clarity / Abstraction Quality
- **M6 — Source-location availability is a hidden contract bet:** optional locations cannot
  guarantee the required `file:line` warning. — Spec Compliance / Bets & Decisions Integrity

### Minor

- **m1 — Consumer inventory and B3 protection are overstated:** include the bare-actual demand
  helper and scope compatibility protection to actual guarded consumers. — Pattern Consistency
- **m2 — Warning aggregation is incomplete:** define stable aggregation of multiple warning
  diagnostics into one warning and one excluded record per statement. — Data Structure Clarity
- **m3 — L4 denominator semantics are deferred:** define what the admission percentage measures
  after NON_NUMERICAL is added. — Data Structure Clarity
- **m4 — B2 remains an avoidable bet:** run and record the committed-fixture disposition census
  before plan stage. — Bets & Decisions Integrity
- **m5 — L6 ERROR gating is already known:** replace the open verification question with the
  existing code evidence and retain a regression test. — Reader Comprehension
- **m6 — Capture wording overstates authority:** ratified `[INFERRED]` requirements are
  challengeable, not owner-settled. — Spec Compliance

---

## Recommendations

1. Resolve mixed-predicate behavior with the owner, then specify recursive force/context rules with
   concrete examples and tests.
2. Make BLOCK rendering include actionable diagnostic messages so every malformed claim names its
   fix or rewrite.
3. Replace optional exclusion fields with one tagged, validated exclusion payload and totalize all
   non-execution routes, including unsupported owner kinds.
4. Correct the version model: keep the shared lowering profile gate, and separately define durable
   exact-companion evidence. Add a snapshot field only if capture-time profile semantics must be
   proven.
5. Decide how missing locations are handled, define one-warning aggregation and L4 denominator
   semantics, and record the in-repo consumer/fixture censuses before planning.

---

## Resolutions

*Recorded by the design agent, 2026-07-18; design.md revised in the same pass. The owner
ratified the M2 containment rule and the M6 location fallback on 2026-07-18 — all findings are
resolved and the design is Approved.*

- **M1 (accepted):** D5 now extends the BLOCK halt rendering to include
  `EligibilityDiagnostic.message`; validation pins the rewrite guidance in the halt text.
- **M2 (accepted, recommendation revised — owner ratification pending):** the design agent
  agrees the mixed-predicate rule was silently decided, and on re-derivation *reverses* the
  draft rule: D2 now classifies by numerical-claim containment — any numerical claim anywhere
  makes the statement numerical, so `(x > 0) and flag` and `(x > 0) xor (y > 0)` error rather
  than warn; only statements with no numerical claim warn. Flagged inline in D2; plan blocked
  until ratified.
- **M3 (partially accepted / pushback):** accepted that the design must state what the
  durable evidence is; D3 now defines it as runtime v3 assert + companion version-floor bump +
  exact companion commit recorded in the execution record with the companion suite run at that
  commit (the established `82fef09` discipline). Pushback: CI/lockfile infrastructure is not
  demanded — it does not exist in this repo and exceeds this correction's scope; SC 8 has
  always been discharged by this discipline in this project.
- **M4 (accepted):** the second pin claim was factually wrong (`snapshot/loader.py:199-212`
  pins schema versions only). D3/I6 corrected to the single shared-lowering gate; no loader
  literal added; rationale recorded (decisions are recomputed at load, so capture-time profile
  semantics don't exist to prove).
- **M5 (accepted):** D6 replaced optional parallel fields with one tagged exclusion payload
  (`non_numerical` / `unassessed_form` / `unsupported_owner`), required iff `eligible=False`
  (model validator), projected into the catalog; the unsupported-owner route is totalized.
- **M6 (accepted as a surfaced decision — owner blessing pending):** D10 proposes
  location-when-present with the existing `<no location>` fallback plus a kept test that live
  extraction supplies locations for all assessed assertions; mandatory schema locations
  rejected as an Item-1 schema change. Flagged inline; plan blocked until blessed.
- **m1 (accepted):** `collect_bare_actual_demand` added to the consumer inventory and
  diagram; B3 rescoped to in-repo consumers with no protection claim beyond the guarded gate.
- **m2 (accepted):** aggregation pinned — one warning per statement, reasons in walk order,
  excluded-record reasons ordered identically, deterministic across routes.
- **m3 (accepted):** L4 rate redefined as executable share = admitted / (admitted + blocked +
  non_numerical), with per-family count lines (D4).
- **m4 (accepted):** census run and recorded in Research Findings — no committed fixture
  changes family; catf_mfe's equality constraints are plain non-asserted usages
  (form-UNASSESSED); the only walked equality is `constraint_blocked_profile` (blocked →
  blocked). B2 narrowed to census completeness with the baseline gates as tripwire.
- **m5 (accepted):** L6 ERROR gating recorded as evidence (`level6_architecture.py:953`);
  open question removed; regression test kept in the plan.
- **m6 (accepted):** capture wording corrected — ratified `[INFERRED]` items are recorded as
  challengeable; M2 is cited as the live example.

---

**Overall:** Revise

**Next Steps:** Resolve the major findings here. Then re-run `my-design` (or return to the design
agent session) and point it at this review to incorporate the resolutions. The reviewer does not
edit `design.md`.
