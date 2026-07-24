# Epic: Constraint PR-Wave Remediation

**Epic ID**: CONSTRAINT-WAVE-REMEDIATION
**Status**: Superseded — partially completed (2026-07-19)
**Priority**: P0 (gates the local CONSTRAINT-EXEC PR wave)
**Created**: 2026-07-18
**Estimated Effort**: 9.5–13 working days
**Superseded by**: `.project/backlog/epic_constraint_execution_lifecycle_remediation.md`

---

## Supersession Notice

**[OWNER-VERBATIM], 2026-07-19:** “Ratified. Please mark the old epic as superceded and write the
new one.” This epic is therefore frozen as partially completed history. No new implementation or
certification work proceeds under it. The ratified lifecycle contract and its replacement epic are
the behavioral and execution authorities.

Completed work remains complete against its recorded scope; supersession does not erase or reopen
its evidence. Newly discovered adjacent gaps receive new items rather than retroactively widening a
completed item.

| Old item | Final state | Replacement treatment |
|---|---|---|
| 1 — Profile semantics | Complete | Inherited baseline; candidate landing/version pin is replacement Item 0. |
| 2 — Name safety | Complete | Inherited baseline and mandatory acceptance evidence; no re-audit. |
| 3 — Occurrence/demand | Open | Replacement Item 1; resolver-unification scope moves to Item 2. |
| 3B — Gate B | Open | Replacement Item 3; first prove whether extension can create V11, then delete or narrow the check. |
| 4 — Snapshot portability/shape | Certified | Preserved; newly discovered whole-tree portability delta is replacement Item 5. |
| 5 — Diagnostics/defaults | Open | Replacement Item 4. |
| 6 — Seal/verify symlinks | Certified | Preserved; newly discovered seal-provenance/bootstrap gaps are replacement Item 7. |
| 7 — Dependency/tail | Open | Documentation/F1 reconciliation moves to replacement Item 6; other tails keep their named backlog homes. |
| 8 — Release evidence | Open | Replaced by Item 13's 41-case, one-artifact-thread composed proof. |

This mapping is historical bookkeeping, not a second active plan.

---

## Executive Summary

This epic remediates the reproduced correctness, crash, portability, and diagnostic-fidelity
defects in the open CONSTRAINT-EXEC wave across agentic-mbse and sysml-codegen. It closes the four
High findings before merge, groups the eight Medium findings by implementation seam, and gives the
Low/latent tail an evidence-backed disposition without pulling unrelated architecture work into the
critical path.

**Critical Success Factor**: [AGENT] R-1 through R-4 and the independently reproduced Gate B
collision are fixed with defect-specific regression evidence before either PR merges. The owner
resolves the R-1/R-2 profile semantics in Item 1; no agent recommendation in this epic is treated as
settled merely because it is written here.

---

## Source Documents

- [Research] `.project/research/20260718-192048_constraint-exec-pr-wave-code-review.md` — primary
  finding register, reproductions, clean-surface checks, recommendations, and open questions.
- [Research] `.project/research/20260719-103419_gate-b-independent-assessment.md` — independent
  current-tree reproduction, contract analysis, repair recommendation, and epic placement for the
  constraint-extension/V11 Gate B collision.
- [Research] `../fusion-tea-stellarator-mbse-demo/.project/research/20260719-082509_gate-b-root-cause-constraint-lowering-vs-v11-bridge.md`
  — original consumer-side root-cause report, real-package evidence, workaround analysis, and
  option-1 design handoff.
- [Project state] `.project/CURRENT_WORK.md` — current PR-wave state, merge order, external F1 hold,
  and prior remediation status.
- [Owner concept] `.project/concepts/constraint-execution-and-design-space-studies.md` — original
  owner framing, including executable-profile and polarity intent.
- [Design] `.project/concepts/constraint-execution-and-design-space-studies-claude.md` — definitive
  concept design, failure taxonomy, and the agent-graded spike results.
- [Spec] `.project/active/numerical-constraint-profile/spec.md` — provenance-graded v3 numerical
  profile contract and the distinction between owner needs and ratified agent recommendations.
- [Design] `.project/active/numerical-constraint-profile/design.md` — implemented v3 decision
  procedure and coordinated-pair rules.
- [Epic] `.project/backlog/epic_gap_close.md` — existing local remediation boundary, wave gates,
  and the external F1 split that this epic must not absorb.
- [Backlog] `.project/backlog/BACKLOG.md` — existing architectural follow-ons and filing homes.

---

## Why This Epic?

**Current State**:
- [INHERITED: `.project/research/20260718-192048_constraint-exec-pr-wave-code-review.md`] Four
  reproduced High defects remain: non-numeric ordering can be admitted, negated assertions can
  execute with inverted meaning, generated formals can shadow framework locals, and a nullable-QN
  filter can crash valid snapshot replay.
- [INHERITED: same research] Eight Medium defects remain at occurrence expansion, path
  portability, demand deduplication, warning rendering, modeled defaults, seal/verify symmetry,
  snapshot shape validation, and explicit TEAx dependency discovery.
- [INHERITED: same research] The Low/latent tail mixes cheap drift corrections, test-quality gaps,
  unreachable or mutation-only claims, and architecture-sized work. It has no single disposition
  record yet.
- [INHERITED: both Gate B research reports] Constraint extension conditionally runs a whole-graph
  V11 check before generation and rejects three unrelated fusion capital-rollup inputs before the
  consumer's private late-fill bridge can act. The bridge is also stale against the current
  generation-plan and sealing flow.
- [INHERITED: `.project/CURRENT_WORK.md`] agentic-mbse PR #11 must precede sysml-codegen PR #9.
  The separate GAP-CLOSE F1 runtime-normalization leg remains open.

**Future State**:
- [AGENT] Every High and Medium finding has a defect-specific regression that is RED on the reviewed
  state and GREEN on the remediation state, or a narrowed evidence-backed disposition where the
  reported path cannot be implemented as stated.
- [AGENT] The profile consumes operand category and assertion polarity deliberately; generation
  cannot collide with its own local names; occurrence and demand collection use stable identity and
  valid owner kinds.
- [AGENT] Snapshot replay and generated packages are portable and fail with contextual domain
  diagnostics; sealing and verification enforce one symlink policy; an invalid explicit TEAx path
  cannot silently select another installation.
- [AGENT] Constraint extension rejects only coverage violations it introduces; the unchanged final
  generation boundary remains whole-graph strict, and fusion compatibility evidence exercises the
  current generation-plan and sealing flow.
- [AGENT] The tail is closed once: cheap verified defects are corrected, genuinely latent claims are
  pinned or narrowed, and architecture work is linked to its existing backlog home rather than
  folded into this wave.

---

## Success Criteria

- [ ] [AGENT] R-1 and R-2 have an owner-recorded semantics choice, complete decision-matrix rows,
      and live regressions proving non-numeric ordering and negated assertions cannot be silently
      admitted with the wrong meaning.
- [x] [AGENT] R-3 rejects or collision-safely maps `value`, `status`, `verdict`, and `self`.
      Under rejection, each case fails deterministically before target-tree mutation and
      collision-free modules import, execute, and report correct verdict and margin evidence.
      Under mapping, all four mapped modules must import, execute, and report correct evidence.
      **Closed 2026-07-19 by Item 2** (rejection policy chosen; reject-before-mutation and
      collision-free real-simkit execution both proven — see Item 2 below).
- [ ] [AGENT] R-4 uses non-null occurrence-stable identity and an owner-kind guard; valid snapshot
      replay succeeds without spurious synthesized values or transcript-corruption errors.
- [ ] [AGENT] R-5 through R-12 each have a defect-specific regression and a correction or explicit
      evidence-backed disposition.
- [ ] [AGENT] (ratified by owner, 2026-07-19) Constraint extension rejects V11 coverage violations
      it introduces without prematurely rejecting unrelated pre-existing inputs; final generation
      still requires zero whole-graph V11 uncovered inputs.
- [ ] [AGENT] Live capture and snapshot replay agree on decisions, demand, warnings, catalogs,
      fingerprints, and generated output for every changed cross-route surface.
- [ ] [AGENT] Each fact field consumed at the profile, lowering, and generation decision seams is
      mapped to a consumer or documented as decision-irrelevant; the four High captured-but-
      unconsulted classes have a test or static completeness check.
- [ ] [AGENT] Every Low/latent/informational row has one disposition: fixed here, narrowed with
      evidence, or linked to an existing/new backlog home with honest provenance and priority.
- [ ] [AGENT] Focused normal and optimized tests, cross-repo compatibility tests, final licensed
      suites, Ruff/format checks, the recorded mypy baseline, fixture-diff review, and portability
      checks pass at the candidate commits.
- [ ] [AGENT] Release evidence preserves agentic-mbse #11 before sysml-codegen #9. External
      `[GAP-CLOSE-F1-TEAX-NORMALIZATION]` remains separate and is not claimed complete here.

---

## Epic Strategy

**Value delivery path:** Item 1 resolves the only product-semantics gate and fixes the two
companion Highs. Items 2 and 3 close the two codegen Highs. Item 3B corrects the independently
reproduced Gate B ownership collision between constraint extension and the generation-time V11
gate. Items 4–6 harden the Medium seams that can run beside the High path. Item 7 closes test
infrastructure and dispositions the tail after the behavioral fixes are known. Item 8 is the final
evidence and release-readiness gate.

**Decomposition rationale:** findings are grouped by the seam that must be specified and designed
together: profile decisions; generated-name safety; occurrence/demand identity; constraint-
extension coverage ownership; snapshot portability; lowering diagnostics/defaults; package
integrity; test/tail hygiene; and coordinated validation. This keeps each implementation item
within roughly 0.5–2 days and keeps `[CONSTRAINT-ARCH-UNIFY]` and the external F1 leg out of the
wave.

**De-risking:** the primary review already reproduces or concretely traces every High and Medium.
No separate spike is needed. Each item starts by converting that evidence into a kept regression
that fails on the reviewed revision. Item 1 is a decision gate: its spec must obtain the owner
choice before implementation, rather than inferring a settled contract from prior ratification.

**PR sequencing:** implementation may be prepared in parallel, but coordinated compatibility and
release evidence use the companion state first. The merge order remains agentic-mbse #11, then
sysml-codegen #9. This epic authorizes no commit, push, PR comment, or merge action.

---

## Backlog Items

### Item 1: Profile Semantics and Wrong-Verdict Closure (R-1, R-2)

**Status (2026-07-19): complete; inherited by the replacement epic.** The fresh audit verified
implementation and spec conformance. The owner subsequently removed agent-authored clean-overlay
and pre-edit-hash gates and requested no re-audit.

**Type**: Code/Integration (agentic-mbse, with codegen compatibility evidence)
**Effort**: 1.5–2 days (spec 2h, design 2h, plan 1h, execute 7–9h)
**Dependencies**: None; decision gate for Items 3 and 8

**Objective**: Obtain the owner semantics ruling and make the executable profile consume operand
category and assertion polarity so neither defect can produce a wrong verdict.

**Decision Required at Spec Stage**:

| Finding | Option | Consequence | Provenance |
|---|---|---|---|
| R-1 | **BLOCK non-numeric ordering (recommended)** | Treat ordering with Boolean/string/enum operands as a malformed numerical claim under v3 default-deny. | [AGENT] Recommendation derived from the owner-stated malformed-numerical rule. |
| R-1 | Extend admission | Define and preserve a SysML ordering meaning for each admitted non-numeric category through generation. | [AGENT] Expands the executable surface and needs new semantics evidence. |
| R-2 | **Carry polarity separately per usage (selected)** | Preserve positive predicate IR, compile one neutral body per true source, and apply expected truth once per usage. | [AGENT] Ratified by owner on 2026-07-19. |
| R-2 | BLOCK negated assertions | Fail safely in v3 and defer executable negation to a separately versioned contract. | [AGENT] Smaller surface, but narrows the prior first-scope intent. |

The owner concept includes negation, while the later spec grades the exact admitted matrix and
polarity mechanics as `[INFERRED]` and owner-ratified. Under capture-fidelity rules, ratification
does not promote that recommendation to owner-originated settled content. The Item 1 spec records
the final owner choice and its reasoning before design or implementation proceeds.

**Scope**:
1. Add the missing category gate for `<`, `<=`, `>`, and `>=`; cover string, Boolean, enumeration,
   integer/real, quantity-compatible, incompatible, and unknown facts in the golden matrix.
2. Apply the owner-selected polarity policy before an ADMIT decision reaches codegen; keep
   `UsageDecision.effective_predicate`, diagnostics, and any polarity field internally coherent.
3. Add live and codec-roundtrip tests for positive and negated inline/definition-typed assertions,
   plus a matrix-driven schema-field consumer completeness check for the profile decision seam.
4. Run the companion suite and codegen's profile-compatibility selection against the exact updated
   companion revision without changing PR state.

**Out of Scope**:
- Non-numerical equality execution, tolerance semantics, or a general generated typed-value path.
- Any profile v4 expansion beyond the owner-selected R-1/R-2 correction.

**Success Criteria**:
- [x] The spec records both owner-ratified choices while preserving their agent-originated grade.
- [x] R-1 and R-2 regressions fail on agentic-mbse `54a95d2` and pass after the correction.
- [x] Every assessed `ConstraintUsageFact` field has a named consumer or an explicit
      decision-irrelevant rationale covered by a test/static check.
- [x] Companion and exact-pair codegen profile tests pass normally and under optimized Python.

**Required Reading**: primary review R-1/R-2 and Open Questions; numerical-profile spec in full;
numerical-profile design D2/I1–I4; both constraint-execution concepts' executable-profile,
negation, and invariants sections; companion executable-profile completed spec/design.

**Deliverables**:
- `../agentic-mbse/.project/active/constraint-wave-profile-semantics/spec.md`
- `../agentic-mbse/.project/active/constraint-wave-profile-semantics/design.md`
- `../agentic-mbse/.project/active/constraint-wave-profile-semantics/plan.md`
- `../agentic-mbse/.project/active/constraint-wave-profile-semantics/evidence.md`

---

### Item 2: Generated Constraint Name-Safety Boundary (R-3) ✅

**Status (2026-07-19): complete.** All three success criteria are met. The 2026-07-18 audit
certified the license-free scope (missing-catalog fail-open now produces one deterministic
structured join violation at every renderer, writer, and orchestration boundary before mutation;
fresh re-audit evidence passed the original probe, all 20 writer/orchestration cases, 16 diagnostic
permutations, and four independent historical-impact nodes). The one criterion the audit left open
— the real execution node, then blocked by unavailable `pandas` — was executed green on 2026-07-19
in the agentic-mbse venv (pandas 2.3.3, teax-simkit on `sys.path`), closing the execution criterion.
Licensed Syside live/snapshot parity (design I11) is out of this item's scope and tracked under
Item 8. See `../active/constraint-wave-name-safety/audit.md` (post-audit addendum) and
`.../evidence/evidence.md`.

**Type**: Implementation (sysml-codegen)
**Effort**: 1 day (spec 1h, design 1.5h, plan 1h, execute 4.5h)
**Dependencies**: None; must complete before Item 8

**Objective**: Prevent model-derived formals from shadowing generated parameters or locals and
silently corrupting evidence or emitted Python.

**Scope**:
1. Define scope-specific reserved-name checks at the actual final binding boundaries: predicate
   leaf parameters (`value`, `status`) and wrapper module-input parameters (`self`, `verdict`), plus
   a package-level correspondence check between those naming paths.
2. Choose deterministic reject or collision-safe mapping behavior; make compiler, wrapper, and
   package preflight consume one structured policy without pretending the naming paths are the same.
3. Add end-to-end regressions for satisfied and violated predicates under the chosen policy. Under
   rejection, all four names fail before target-tree mutation and collision-free controls import
   and execute with correct verdict, status, and margin. Under mapping, all four mapped modules do.
4. Add a generated-scope completeness guard so a new template local cannot bypass the collision
   policy silently.

**Out of Scope**:
- General ADR-003 identifier refactoring or qualified-name architecture.
- User-facing renaming outside generated constraint module formals.

**Success Criteria**:
- [x] Each R-3 symptom is independently RED on sysml-codegen `512786c` and GREEN after the fix.
- [x] No accepted generated module can contain a duplicate Python parameter or formal/local
      collision; diagnostics name the model formal when generation rejects it.
- [x] Under rejection, collision-free controls import and preserve correct verdict and margin
      evidence for both truth values; under mapping, the four mapped modules do so. **Closed
      2026-07-19**: the pinned execution node ran green in the real environment (agentic-mbse venv,
      pandas 2.3.3, teax-simkit on `sys.path`) — satisfied `(True, 'satisfied', 1.0, {'x': 2.0,
      'limit': 3.0})`, violated `(False, 'violated', -1.0, {'x': 4.0, 'limit': 3.0})`
      (`../active/constraint-wave-name-safety/evidence/collision-free-execution-tuples.txt`).

**Required Reading**: primary review R-3; current predicate compiler and constraint template;
GAP-CLOSE F2 collision strategy and tests; ADR-003 naming documentation.

**Deliverables**:
- `.project/active/constraint-wave-name-safety/spec.md`
- `.project/active/constraint-wave-name-safety/design.md`
- `.project/active/constraint-wave-name-safety/plan.md`
- `.project/active/constraint-wave-name-safety/evidence/evidence.md`

---

### Item 3: Occurrence and Demand Identity Integrity (R-4, R-5, R-7)

**Type**: Code/Integration (sysml-codegen)
**Effort**: 1.5–2 days (spec 1.5h, design 2h, plan 1h, execute 7–9h)
**Dependencies**: Item 1 (final ADMIT semantics); must complete before Item 5 and Item 8

**Objective**: Make occurrence expansion and supplied-value demand collection total, stable, and
deduplicated across live and snapshot routes.

**Scope**:
1. **R-4:** replace nullable-QN membership with occurrence-stable usage identity; filter owner kinds
   before expansion; normalize expected occurrence-index failures without relabeling valid
   snapshots as corrupt.
2. **R-5:** make recursive containment fail with `NonFiniteCardinalityError` and contextual owner/
   path evidence, matching the existing non-finite multiplicity contract.
3. **R-7:** define one demand identity and precedence rule for the calc-usage and constraint routes;
   either constrain the collector to bare actuals or deduplicate by resolved target without
   changing parameter grouping based on assertion source file.
4. Pin stable counts, ordering, warning cardinality, owner-kind behavior, and live/snapshot parity.

**Out of Scope**:
- The canonical resolver/typed-path/one-instance-index redesign in `[CONSTRAINT-ARCH-UNIFY]`.
- Supporting new owner kinds or infinite recursive model expansion.

**Success Criteria**:
- [ ] The valid R-4 snapshot rebuild succeeds and produces no excluded-usage synthesized values.
- [ ] Unsupported owner kinds are excluded before expansion and cannot reach the package fallback.
- [ ] Recursive containment blocks loudly with a domain error; finite sibling occurrence order is
      unchanged.
- [ ] A value demanded by both routes appears once with deterministic source grouping, scan/apply
      counts, and warnings.
- [ ] R-4/R-5/R-7 regressions are RED on the reviewed state and GREEN after the fix in both routes.

**Required Reading**: primary review R-4/R-5/R-7; GAP-CLOSE F5 identity work and
`gap-lowering-integrity` evidence; part-instance index design/audit; supplied-values and parameter-
group contracts; numerical-profile Item 1 outcome chosen above.

**Deliverables**:
- `.project/active/constraint-wave-occurrence-demand/spec.md`
- `.project/active/constraint-wave-occurrence-demand/design.md`
- `.project/active/constraint-wave-occurrence-demand/plan.md`
- `.project/active/constraint-wave-occurrence-demand/evidence.md`

---

### Item 3B: Constraint-Extension V11 Coverage Ownership (Gate B)

**Status (2026-07-19): not started; migrated to replacement Item 3.** The owner agreed with the
independent assessment. The ratified lifecycle later tightened this item to prove the V11 vacuity
question before choosing deletion or differential checking.

**Type**: Code/Integration (sysml-codegen, with fusion-tea compatibility evidence)
**Effort**: 0.5–1 day (spec/design amendment 1.5h, plan 0.5h, execute 3–5h)
**Dependencies**: Item 1; default sequence after Item 3; must complete before Items 5, 7, and 8

**Objective**: Make constraint extension responsible for coverage failures it introduces without
moving the final whole-graph V11 generation gate earlier for unrelated pre-existing inputs.

**Source Evidence**:
- [INHERITED: original fusion-tea Gate B research] A lowering-on fusion snapshot capture fails on
  exactly three pre-existing capital-rollup inputs before the consumer bridge can fill them.
- [INHERITED: independent Gate B assessment] The failure reproduces on the current dirty tree in a
  license-free minimal graph and in the licensed fusion capture; no completed epic item changes the
  collector, extension tail, or either live/snapshot call site.

**Required Invariants**:
1. **Extension ownership.** [AGENT] (ratified by owner, 2026-07-19) Constraint extension introduces
   no new V11 uncovered inputs. It does not reject an unchanged, unrelated violation already present
   in the input graph.
2. **Final coverage.** [AGENT] (ratified by owner, 2026-07-19) Final generation still requires zero
   whole-graph V11 uncovered inputs through the existing always-strict generation boundary.
3. **Strict actual resolution.** [INHERITED: constraint-lowering INV-2] An unresolved constraint
   actual remains a named generation error. This item adds no textual fallback, synthesized actual,
   placeholder default, or fallback entry point.
4. **Channel integrity.** [INHERITED: constraint-lowering INV-6] Constraint extension continues to
   run whole-graph `_validate_channel_references`; the coverage correction does not narrow channel-
   reference validation.
5. **Route symmetry.** [AGENT] The ownership rule is implemented in the shared extension function so
   live construction and snapshot reconstruction cannot diverge. It requires no snapshot schema or
   lowering-mode change.

**Scope**:
1. Amend the old whole-graph wording of constraint-lowering INV-6 honestly. Record the replacement
   contract as: extension introduces no new V11 uncovered inputs; final generation requires zero
   whole-graph V11 uncovered inputs.
2. Compare the input graph's V11 violations with the extended graph's violations and raise only for
   the newly introduced multiset, or use an equally precise appended-module ownership boundary that
   does not depend on module-name filtering.
3. Keep `_reconcile_params_coverage` unchanged as the final whole-graph gate and keep
   `_validate_channel_references` whole-graph during extension.
4. Add the missing regression shape: constraints plus a pre-existing valueless fallback input,
   including a case where the new constraint begins consuming a previously unwired fallback key.
5. Update the fusion-tea bridge compatibility path for the current `ConstraintGenerationPlan`,
   preflight, prewrite, and sealing flow as part of Item 8 evidence, or explicitly disposition a
   separately designed public late-fill seam. Do not claim Gate B alone makes that private bridge
   current.

**Out of Scope**:
- Solving the underlying cross-part capital-rollup wiring limitation.
- Adding a deferred-input snapshot annotation, capture-time consumer hook, or public bridge API
  without a separate design decision.
- Adding placeholder defaults to the SysML model as the permanent correction.
- Relaxing strict constraint-actual resolution or the final whole-graph V11 generation gate.

**Success Criteria**:
- [ ] A pre-existing wired V11 violation plus an unrelated safe constraint extends successfully;
      the unchanged final generation gate still rejects it until the consumer supplies a value.
- [ ] A previously unwired, valueless fallback entry point newly consumed by a constraint fails
      during extension, and a mixed baseline/new case reports only the newly introduced violation.
- [ ] Strict unresolved-actual regressions remain green; no constraint actual or default is invented.
- [ ] Whole-graph channel-reference validation remains unchanged and catches a dangling constraint
      module-output channel.
- [ ] Live construction and snapshot reconstruction produce identical graph/catalog/generated bytes
      for the corrected shape, normally and under optimized Python.
- [ ] Item 8 either proves the updated fusion bridge through the current generation-plan/sealing
      flow or records the remaining private-integration gap without claiming end-to-end closure.

**Required Reading**: both Gate B research reports in Source Documents; current V11 architecture
contract in `docs/architecture/reference/07-graph-assembly.md`; completed constraint-lowering
spec/design INV-2 and INV-6; `collect_uncovered_params`, `extend_graph_with_constraints`, both live/
snapshot call sites, and `_reconcile_params_coverage`; current fusion bridge and two-pass runner.

**Deliverables**:
- `.project/active/constraint-wave-v11-coverage/spec.md`
- `.project/active/constraint-wave-v11-coverage/design.md`
- `.project/active/constraint-wave-v11-coverage/plan.md`
- `.project/active/constraint-wave-v11-coverage/evidence.md`

---

### Item 4: Snapshot Portability and Shape Gates (R-6, R-11) ✅

**Type**: Code/Integration (sysml-codegen)
**Effort**: 1–1.5 days (spec 1h, design 1.5h, plan 1h, execute 5–7h)
**Dependencies**: None; coordinate fixture edits with Item 3; must complete before Item 8
**Status**: Certified

**Objective**: Remove host paths from semantic artifacts and make every malformed v3 section fail
through a contextual snapshot-domain diagnostic.

**Scope**:
1. **R-6:** apply one root-slot-relative location normalization policy to named and anonymous
   excluded usages before IDs, catalogs, fingerprints, contracts, and generated reports consume it.
2. Re-capture only fixtures whose semantic payload genuinely changes; review diffs for portable
   path/fingerprint consequences and prove relocated-checkout byte stability.
3. **R-11:** validate mapping/list/item shapes and required keys for all v3 sections before domain
   reconstruction; normalize `AttributeError`, `KeyError`, and `TypeError` into section/path-specific
   recapture guidance.
4. Add a table-driven malformed-section matrix and live/snapshot location parity checks.

**Out of Scope**:
- Snapshot schema v4 or unrelated serializer restructuring.
- Rewriting historical snapshots that contain no affected named excluded record.

**Success Criteria**:
- [x] Generated artifacts and fingerprints contain no absolute checkout path for affected records.
- [x] The same snapshot generates byte-identical semantic artifacts from two checkout roots. The
      moved replay and licensed live A/live B/replay A routes pass the exact manifest.
- [x] Every R-11 malformed shape raises the documented domain exception with section and field
      context; no raw container exception escapes.
- [x] Fixture churn is limited to reviewed, provenance-recorded R-6 consequences.

**Required Reading**: primary review R-6/R-11; snapshot serializer/loader contracts; snapshot v3
active spec/design/audit; GAP-CLOSE anonymous-location normalization and fixture-recapture notes.

**Deliverables**:
- `.project/active/constraint-wave-snapshot-portability/spec.md`
- `.project/active/constraint-wave-snapshot-portability/design.md`
- `.project/active/constraint-wave-snapshot-portability/plan.md`
- `.project/active/constraint-wave-snapshot-portability/evidence.md`

---

### Item 5: Lowering Diagnostic and Modeled-Default Fidelity (R-8, R-9)

**Type**: Implementation (sysml-codegen)
**Effort**: 1 day (spec 1h, design 1.5h, plan 1h, execute 4.5h)
**Dependencies**: Items 3 and 3B (shared lowering/default surfaces); must complete before Item 8

**Objective**: Ensure warning preparation cannot hide the actionable halt and that signed or
unit-annotated modeled defaults reach generated inputs faithfully.

**Scope**:
1. **R-8:** make warning location rendering total; use a deterministic safe fallback when a source
   cannot map to a supplied model root, then continue to the intended warning-before-BLOCK flow.
   First establish live reachability or explicitly narrow the claim to snapshot/mutation coverage.
2. **R-9:** evaluate the supported literal wrapper shapes needed by defaults—unary sign and unit
   annotation—without broadening expression evaluation; preserve unit policy and reject unsupported
   structures loudly or leave them for the existing resolver with named evidence.
3. Test negative/positive signed defaults, unit-annotated defaults, nested unsupported shapes, and
   generated JSON inclusion; assert warning bytes/order and live/snapshot parity where reachable.

**Out of Scope**:
- General constant folding or implicit unit conversion.
- New diagnostic architecture beyond the existing warning and lowering-halt surfaces.

**Success Criteria**:
- [ ] The R-8 pre-pass never replaces a BLOCK diagnostic with a location-mapping exception; the
      regression records whether the live path is reachable.
- [ ] Signed and unit-annotated supported defaults retain their numeric value in synthesized entry
      points and generated JSON.
- [ ] Unsupported default IR does not silently invent a value.
- [ ] R-8/R-9 regressions are RED on the reviewed state and GREEN after the fix.

**Required Reading**: primary review R-8/R-9; numerical-profile warning/location design;
GAP-CLOSE warning-order evidence; entry-point/default resolution documentation and tests.

**Deliverables**:
- `.project/active/constraint-wave-lowering-fidelity/spec.md`
- `.project/active/constraint-wave-lowering-fidelity/design.md`
- `.project/active/constraint-wave-lowering-fidelity/plan.md`
- `.project/active/constraint-wave-lowering-fidelity/evidence.md`

---

### Item 6: Seal and Verify Symlink Symmetry (R-10) ✅

**Type**: Implementation (sysml-codegen)
**Effort**: 0.5–1 day (spec 0.5h, design 1h, plan 0.5h, execute 4h)
**Dependencies**: None; must complete before Item 8

**Objective**: Make sealing and verification enforce the same explicit symlink policy so sealing
cannot produce an immediately unverifiable package and dangling links cannot evade coverage.

**Scope**:
1. Define one shared classification/policy for file, directory, internal, escaping, and dangling
   symlinks without following links outside the package root.
2. Reject unsupported links at seal time with path-specific diagnostics; verify reports the same
   class and cannot skip dangling links.
3. Add a seal→verify case matrix proving every successfully sealed package verifies unchanged and
   every forbidden link fails at the earliest boundary.

**Out of Scope**:
- Archive format changes or broader package-contract redesign.
- The external TEAx evaluator-normalization F1 leg.

**Success Criteria**:
- [x] No symlink tree can seal successfully and immediately fail unchanged verification.
- [x] Dangling, internal, and escaping cases have explicit deterministic outcomes and diagnostics.
- [x] Verifier remains stdlib-only and existing regular-file package fingerprints stay stable.

**Required Reading**: primary review R-10 and verified-clean seal/verify notes; GAP-CLOSE F9 work;
package-contract and sealing reference documentation.

**Deliverables**:
- `.project/active/constraint-wave-seal-symmetry/spec.md`
- `.project/active/constraint-wave-seal-symmetry/design.md`
- `.project/active/constraint-wave-seal-symmetry/plan.md`
- `.project/active/constraint-wave-seal-symmetry/evidence.md`

---

### Item 7: Dependency Discovery and Review-Tail Disposition (R-12 + Low/latent tail)

**Type**: Testing/Validation (both repositories; production edits only for verified cheap defects)
**Effort**: 1–1.5 days (spec 1h, design 0.5h, plan 0.5h, execute 6–8h)
**Dependencies**: Items 1–6, including Item 3B

**Objective**: Make explicit TEAx dependency selection strict and give every remaining review row
one evidence-backed home without expanding the remediation into architecture work.

**Scope**:
1. **R-12:** if `TEAX_SIMKIT_PATH` is set, validate exactly that path and fail loudly when invalid;
   never fall through to sibling discovery. Add the missing invalid-explicit/valid-sibling cell.
2. Build a disposition register covering every Low/latent/informational row in the primary review,
   with reproduction status, reachability, action, owner repo, provenance, and priority.
3. Fix only objective, local rows that remain small after a RED regression—for example comment/
   docstring drift, portable exception-text tests, missing relative-import scan, and trivial test
   cleanup. Keep unrelated behavior changes out unless separately spec'd.
4. Link architecture-sized or capability-expanding rows to `[CONSTRAINT-ARCH-UNIFY]`,
   `[EXIT-PIN-SEAM]`, `[ANON-ELIGIBLE-KEY]`, or one new non-duplicative backlog row. Narrow
   unreachable/mutation-only claims with evidence instead of pretending they were fixed.
5. Confirm the PR #11 tail separately: xor wire-invariant drift, equality docstring drift, L6
   UNASSESSED visibility, duplicate-QN precedence, and cosmetic diagnostic reuse.

**Out of Scope**:
- Implementing the unified resolver/path/instance architecture, new anonymous executable support,
  or dormant exit-selection capability.
- Treating a latent claim as merge-critical without new reachability evidence.

**Success Criteria**:
- [ ] Invalid explicit TEAx paths fail deterministically and never select a sibling install.
- [ ] The disposition register accounts for every primary-review tail row exactly once.
- [ ] Each fixed row has a defect-specific RED/GREEN regression; each deferred row has evidence,
      provenance, priority, and a non-duplicative backlog link.
- [ ] No architecture-sized implementation is added to Items 1–6, Item 3B, or the wave critical
      path.

**Required Reading**: primary review R-12 and full Low/latent/informational section; BACKLOG rows
`[CONSTRAINT-ARCH-UNIFY]`, `[EXIT-PIN-SEAM]`, and `[ANON-ELIGIBLE-KEY]`; current test helpers and
package-verifier import-scan tests; companion executable-profile docs/tests for PR #11 rows.

**Deliverables**:
- `.project/active/constraint-wave-tail-disposition/spec.md`
- `.project/active/constraint-wave-tail-disposition/plan.md`
- `.project/active/constraint-wave-tail-disposition/disposition-register.md`
- `.project/active/constraint-wave-tail-disposition/evidence.md`

---

### Item 8: Cross-Repo Compatibility and Release-Readiness Evidence

**Type**: Testing/Validation (agentic-mbse then sysml-codegen)
**Effort**: 1 day (spec 0.5h, design 0.5h, plan 0.5h, execute 5h)
**Dependencies**: Items 1–7, including Item 3B

**Objective**: Prove the complete remediation pair is compatible, portable, regression-clean, and
ready for the existing PRs without changing external PR state.

**Scope**:
1. Validate the exact agentic-mbse candidate first, then sysml-codegen against that candidate;
   record revisions and preserve the #11-before-#9 release order.
2. Run defect-focused tests normally and with optimized Python; cross-route live/snapshot parity;
   companion and licensed codegen full suites; Ruff/format/diff checks; recorded mypy baseline;
   fixture and generated-package diff review; relocated-package/snapshot portability checks.
3. Re-run each kept regression against its reviewed baseline or an isolated pre-fix overlay and
   record RED provenance, then GREEN at the candidate state.
4. Produce a release-readiness report that names remaining external blockers. Keep
   `[GAP-CLOSE-F1-TEAX-NORMALIZATION]` separate and do not claim the epic or PR wave fully complete
   while it remains open.
5. Run the fusion Gate B route through the current generation-plan, preflight, output-mutation, and
   sealing sequence. Distinguish an updated private bridge from any future public late-fill API.

**Out of Scope**:
- Commit, push, PR comment, merge, branch rewrite, or external F1 implementation.
- Closing or archiving the prior GAP-CLOSE epic.

**Success Criteria**:
- [ ] All preceding item criteria, including Item 3B, are traced to code/tests/evidence with no
      placeholder or skipped claim.
- [ ] Exact-pair focused, optimized, compatibility, lint/format, fixture, and portability gates pass.
- [ ] Licensed full-suite results are recorded at the final candidate revisions, or accurately
      named as an external execution blocker without substituting narrower evidence.
- [ ] The release-readiness report states #11 before #9 and lists external F1 separately.
- [ ] No PR or remote state was changed by this item.

**Required Reading**: every prior item evidence file; primary review Verified Clean section;
GAP-CLOSE Item 5 and independent audit; current project release/test commands in `CLAUDE.md`.

**Deliverables**:
- `.project/active/constraint-wave-release-readiness/spec.md`
- `.project/active/constraint-wave-release-readiness/plan.md`
- `.project/active/constraint-wave-release-readiness/report.md`

---

## Dependencies

**External**:
- A syside license is required for live reproductions, fixture captures, and the licensed full
  suite. Snapshot/unit work can proceed without it.
- `[GAP-CLOSE-F1-TEAX-NORMALIZATION]` remains a separate TEAx P0. It may still block release after
  this epic's local work is green.
- Open PRs #11 and #9 are context only. This epic does not authorize interaction with them.

**Internal**:
- Item 1 settles the profile contract used by Item 3 and final compatibility evidence.
- Item 3B is captured now. The default sequence places it after Item 3 and before Item 5; it has no
  correctness dependency on Item 3 and may move ahead when the fusion blocker is the immediate
  priority. Item 5 waits for both because it changes the default-value surface V11 classifies.
- Item 7 runs after behavioral fixes so tail rows are not duplicated or dispositioned against stale
  code. Item 8 is strictly last.

**Item Dependency Graph**:
```text
Item 1 Profile semantics ─> Item 3 Occurrence/demand ─> Item 3B Gate B ─> Item 5 Fidelity ─┐
        │                                                                                  │
        └──────────────────────────────────────────────────────────────────────────────────┤
Item 2 Name safety ────────────────────────────────────────────────────────────────────────┤
Item 4 Snapshot portability ────────────────────────────────────────────────────────────────┤
Item 6 Seal symmetry ───────────────────────────────────────────────────────────────────────┤
                                                                                            v
                                                                                  Item 7 Tail disposition
                                                                                            │
                                                                                            v
                                                                                  Item 8 Release evidence
```

Items 2, 4, and 6 can run in parallel with the Item 1→3 path, subject to normal same-branch edit
coordination. Item 4 coordinates fixture changes with Item 3. The default critical path is
Item 1 → Item 3 → Item 3B → Item 5 → Item 7 → Item 8. Item 3B may move before Item 3 without
changing the one-landing-unit rule when fusion integration is the immediate blocker.

---

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| R-1/R-2 recommendations are mistaken for settled owner requirements | High | Item 1 is an explicit decision gate; preserve provenance and stop before implementation until the owner records the choice. |
| High fixes wait behind Medium work | High | Items 1–3 own all Highs; Medium items run in parallel and Item 8 cannot certify release until the High path is green. |
| Shared lowering/snapshot fixtures create conflicting edits | Med | Default to Item 3 → Item 3B → Item 5 and coordinate Item 4 fixture changes through reviewed, provenance-recorded diffs. |
| Gate B is treated as a complete fusion fix | High | Item 3B narrows only extension-time ownership; Item 8 separately updates and proves the private bridge against generation planning, preflight, mutation, and sealing. |
| Narrowing extension coverage silently weakens strict resolution | High | Preserve INV-2 and the final whole-graph V11 gate; add a negative constraint-consumes-fallback regression and a mixed baseline/new case. |
| Broad tail becomes an architecture refactor | High | Item 7 requires one-row dispositions and links existing architecture homes; it fixes only local evidence-backed rows. |
| Live reachability or licensed evidence is unavailable | Med | Preserve unit/snapshot progress, name the missing live leg explicitly, and do not substitute it for the required final evidence. |
| Cross-repo editable installs validate the wrong companion | High | Item 1 and Item 8 record exact revisions and validate companion first; R-12 makes explicit TEAx selection strict. |
| External F1 is accidentally claimed closed | High | Keep it out of every item scope and name it as a separate blocker in Item 8's report. |

---

## Timeline

**Total Effort**: 9.5–13 working days

| Item | Effort | Dependencies |
|---|---:|---|
| 1. Profile semantics and wrong-verdict closure | 1.5–2 d | None |
| 2. Generated constraint name safety | 1 d | None |
| 3. Occurrence and demand identity integrity | 1.5–2 d | Item 1 |
| 3B. Constraint-extension V11 coverage ownership | 0.5–1 d | Item 1; default after Item 3; before Item 5 |
| 4. Snapshot portability and shape gates | 1–1.5 d | None; coordinate with Item 3 |
| 5. Lowering diagnostic/default fidelity | 1 d | Items 3 and 3B |
| 6. Seal/verify symlink symmetry | 0.5–1 d | None |
| 7. Dependency discovery and tail disposition | 1–1.5 d | Items 1–6, including Item 3B |
| 8. Compatibility and release-readiness evidence | 1 d | Items 1–7, including Item 3B |

With Items 2, 4, and 6 parallelized, elapsed time is expected to be 7.5–10 working days. The effort
range is person-days and remains 9.5–13 days.

---

## Lessons Learned (Post-Completion)

*Fill in after epic completion.*

**What Went Well**:
- TBD

**What Could Improve**:
- TBD

**Surprises**:
- TBD

---

**Last Updated**: 2026-07-19
**Next Action**: None. Execute
`.project/backlog/epic_constraint_execution_lifecycle_remediation.md` instead.
