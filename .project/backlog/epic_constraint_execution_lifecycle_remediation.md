# Epic: Constraint Execution Lifecycle Remediation

**Epic ID**: CONSTRAINT-LIFECYCLE-REMEDIATION
**Status**: In progress — Item 0 complete; Item 1 defects reproduced; production remediation not started
**Priority**: P0 (gates the open constraint PR wave)
**Created**: 2026-07-19
**Estimated Effort**: 19–23 working days
**Authority**: `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md`

---

## Executive Summary

This epic implements and proves the ratified constraint-execution lifecycle across agentic-mbse,
sysml-codegen, TEAx, IFE, and the stellarator consumer. It replaces the narrow PR-wave remediation
epic with one dependency-ordered program that fixes the semantic, graph, package, evaluator, and
study seams and then certifies one public artifact thread end to end.

The required delivery vehicles for the existing constraint wave are the open agentic-mbse PR #11
first and the open sysml-codegen PR #9 second. This epic updates those PRs; it does not replace them
with new upstream PRs. TEAx and consumer work remains part of the same lifecycle program but uses
the delivery path authorized for each repository.

**Critical Success Factor**: [INHERITED: ratified lifecycle contract] One commit-pinned compatible
revision set passes all 41 mandatory acceptance cases through public live and relocated-snapshot
routes, using the same sealed artifact thread through load, evaluation, persistence, IFE, and
stellarator, while superseded authorities, routes, bridges, and workarounds are removed.

## Current Execution Status — 2026-07-19

The program is at the start of implementation. Item 0 is complete. Item 1 has an approved contract
and design plus a public failing acceptance surface, but no production code has been changed for
Item 1. Items 2–13 have not started.

| Item | Actual status | Evidence that matters |
|---|---|---|
| 0 — Compatible candidate | **Complete** | Compatible commits, locks, imports, package build, focused 323-test gate, and repository LOC baseline are recorded in `.project/active/constraint-lifecycle-candidate-pin/evidence.md`. |
| 1 — Occurrence/demand | **In progress: RED reproduced, implementation not started** | Six public acceptance nodes and six SysML fixture families now exist. Five nodes reproduce R-4/R-5/R-7 on the pinned predecessor and current production code; the constraint-only provenance control already passes. `src/` is unchanged. |
| 2–12 — Product remediation | **Not started** | No item-owned production implementation or certifying evidence exists yet. Prior inherited work remains valid only within its recorded scope. |
| 13 — Composed proof/release | **Blocked by Items 1–12** | No 41-case composed artifact thread, final release candidate, push, or PR update exists. |

Useful Item 1 work now present:

- `.project/active/constraint-lifecycle-occurrence-demand/spec.md` — independently re-reviewed,
  **Approve**.
- `.project/active/constraint-lifecycle-occurrence-demand/design.md` — independently re-reviewed,
  **Approve**.
- `tests/conformance/test_constraint_occurrence_demand_acceptance.py` and
  `tests/fixtures/constraint_occurrence_demand/` — stable public behavioral surface.

The detailed Item 1 plan and provisional LOC accounting are not completion evidence and do not
gate implementation. The next meaningful action is to change the shared occurrence/demand code
until the five reproduced failures pass without weakening the fixtures, then run the relevant
regression suite. Later work should combine shared root-cause edits across item boundaries instead
of creating an artifact pipeline per item.

---

## Source Documents

- [Ratified authority]
  `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md` — lifecycle stages,
  invariants, owner decisions D-1/D-2/D-3, proof matrix, and ordered register.
- [Requirements]
  `.project/active/constraint-execution-lifecycle-contract/spec.md` — provenance-graded LC-A–LC-I
  requirements and acceptance obligations.
- [Research]
  `.project/research/20260719-111228_constraint-execution-lifecycle-evidence-census.md` — intent,
  current implementation, consumer, and proof ledger.
- [Adversarial review]
  `.project/research/20260719-125806_constraint-execution-lifecycle-contract-adversarial-review.md`
  — six-lane architecture, code, consumer, and acceptance-matrix attack.
- [Correction re-review]
  `.project/research/20260719-134700_constraint-execution-lifecycle-contract-correction-rereview.md`
  — correction traceability, residual proof cases, and architecture-versus-certification gate.
- [PR-wave review]
  `.project/research/20260718-192048_constraint-exec-pr-wave-code-review.md` — R-1 through R-12
  reproductions and captured-but-unconsulted defect family.
- [Gate B independent assessment]
  `.project/research/20260719-103419_gate-b-independent-assessment.md` — reproduced scope defect and
  repair constraints.
- [Gate B consumer root cause]
  `../fusion-tea-stellarator-mbse-demo/.project/research/20260719-082509_gate-b-root-cause-constraint-lowering-vs-v11-bridge.md`
  — original fusion reproduction, limitation, and integration evidence.
- [Superseded epic]
  `.project/backlog/epic_constraint_pr_wave_remediation.md` — completed Items 1/2/4/6 and migration
  map for unfinished work.
- [Project state] `.project/CURRENT_WORK.md` — worktree, evidence, and PR-wave status.

---

## Why This Epic?

**Current State**:
- [INHERITED: Item 0 evidence] A commit-pinned, mutually installable starting set exists. It is a
  baseline for remediation, not a final certifying candidate.
- [INHERITED: adversarial review] Component tests can pass while supported combinations fail at
  actual resolution, occurrence expansion, producer completeness, package trust, catalog joins,
  evaluator routes, or evidence persistence.
- [INHERITED: superseded epic] Profile semantics, generated name safety, bounded snapshot
  portability/shape gates, and seal/verify symlink symmetry are completed or certified. They remain
  valid within their recorded scopes.
- [INHERITED: ratified contract] Three resolver ladders, alternate catalog authorities, consumer
  materializers/wrappers, private graph mutation, and duplicated verifier/runtime rules leave too
  many places for the same meaning to drift.
- [OWNER] All constraint remediation belongs to the same open PR landing unit. Backlog-item
  boundaries organize specification, dependencies, and evidence; they do not require artificial
  branch or PR separation.

**Future State**:
- [INHERITED: ratified contract] Model meaning is extracted and classified once per consumer,
  generated packages evaluate it without invented values, and studies consume immutable evidence
  without redefining semantics.
- [INHERITED: owner decisions D-1/D-2] Every model-derived consumed value has a real graph producer;
  direct literal design attributes resolve through shared exact-QN machinery; no public late-fill
  or post-build mutation seam exists.
- [INHERITED: owner decision D-3] Codegen's embedded model-contract catalog is the sole schema
  authority; TEAx consumes it directly and alternate schemas, fixtures, stand-ins, materializers,
  and reconstruction code are deleted.
- [INHERITED: proof standard] One pinned public artifact thread proves live/snapshot generation,
  full-tree portability, sealing, trusted load, evaluation, persistence, query, IFE, and the
  five-constraint stellarator design point.

---

## Success Criteria

- [x] Register row 0 records exact compatible agentic-mbse, sysml-codegen, and TEAx commits,
      versions, dependency locks, current-profile smoke evidence, and the production LOC baseline.
      Later register rows retain their own two-direction schema/runtime skew obligations.
- [ ] All 41 mandatory acceptance cases record their full LC-I09 evidence coordinate, both public
      routes, open predecessor rows, and one sealed artifact identity thread.
- [ ] Occurrence, demand, actual resolution, Gate A, Gate B, diagnostics, defaults, and whole-tree
      portability satisfy contract rows 1–5 without invented values or weaker fixture shapes.
- [ ] Runtime-owned verification, verifier/runtime skew, generation provenance, and re-seal behavior
      satisfy rows 8–9 before any package code executes.
- [ ] The canonical embedded catalog and real semantic/catalog/executable identities pass directly
      into TEAx; alternate schemas, materializers, fixtures, stand-ins, and reconstruction paths are
      removed under row 10.
- [ ] Stock TEAx handles complete zero/one/multiple entry mappings, constraint-free packages,
      immutable nested evidence, exact file-backed reports, crash-safe persistence, and compatible
      resume/query without a consumer adapter.
- [ ] Producer completeness is proved independently from V11. The stellarator model has no D7
      passthroughs, private bridge, placeholder mutation, ambiguous first-pick, or leaf-name guess.
- [ ] Grandfathered skip-lowering snapshots fail closed on the product path; `tracking_key` is either
      implemented/cataloged or removed with every correlation claim corrected.
- [ ] IFE runs all 2,301 points through canonical stock seams and the stellarator produces five
      verdicts with unchanged ordinary numerics and sealed handwritten content.
- [ ] [OWNER] Completed superseded-epic Items 1/2/4/6 are inherited rather than automatically
      re-audited; final composed proof still exercises their relevant behavior on the pinned set.
- [ ] [OWNER] The existing open agentic-mbse PR #11 and sysml-codegen PR #9 are updated with the
      final compatible commits, accurate descriptions, and evidence. PR #11 remains first in the
      merge order, and no replacement upstream PR is opened for this remediation.
- [ ] [OWNER] The remediation strives for simpler code, judged qualitatively: superseded paths
      are deleted rather than shimmed and no parallel authority or route replaces them.
- [ ] Public docs, package/profile/runtime versions, PR descriptions, and evidence reports describe
      the landed candidate without stale or present-tense overclaims.

---

## Simplification and Deletion Mandate

**[OWNER-VERBATIM], 2026-07-19:** “do not mess with item 1. it is already in flight. no saving it
now. but please for the love of god get rid of all the fucking LOC bullshit on ALL OTHER ITEMS.”

For Items 2–13, this amendment retires every numeric LOC gate, baseline, per-file cap, counting
obligation, and code-growth deviation review. Item 1 is already in flight and its artifacts are
untouched. Simplicity for Items 2–13 remains an execution rule, judged qualitatively by review:

1. Prefer one shared mechanism and deletion of superseded paths over another guard, adapter, or
   compatibility shim. Name expected deletions before design and delete what a change obsoletes.
2. Do not collapse intentional boundaries: the two independent profile consumers, halt-before-
   mutation, plan-before-clear, and stdlib-only seal/verify behavior remain distinct invariants.

**[OWNER-VERBATIM], 2026-07-19 (original):** “Remember to mention in the epic document the
importance of SIMPLIFICATION and REDUCING code wherever possible.”

Expected deletion opportunities include the three drifted resolver ladders, legacy polarity-baked
compiler paths, extension-time V11 if proved vacuous, duplicate catalog authorities, fusion
materializers/wrappers, hand-authored contract fixtures, stand-in fingerprints, duplicated
verifier/runtime version rules, and grandfathered fail-open code.

---

## Epic Strategy

**Value delivery path:** Item 0 establishes the only certifiable revision set. Items 1–5 close the
model-to-graph correctness path. Items 6–12 close documentation, package trust, catalog, TEAx, real
producer, evidence, and legacy-state seams. Item 13 certifies the complete public lifecycle and is
strictly last.

**Dependency discipline:** The ratified register order is binding. A later item may be specified or
designed while an earlier item runs, but it cannot be certified around an open predecessor. Every
evidence record names its open predecessor rows. Item 1's anonymous live leg closes before Item 5;
its relocated leg closes with Item 5, exactly as the contract states.

**One landing unit:** [OWNER] This epic fixes and updates the existing open constraint PR wave.
Items are audit and dependency boundaries inside that landing unit, not a requirement for isolated
commits, branches, or PRs. Shared edits should converge directly toward the final architecture.
The upstream delivery order is agentic-mbse PR #11, then sysml-codegen PR #9. Item 0 must keep the
current committed agentic-mbse work intact; the modeling-orchestrator commit may remain in PR #11.

**Decomposition rationale:** Fourteen items are an intentional program-sized exception to the usual
epic size guideline. Splitting them into independent epics would weaken the one-register ordering
rule and the same-artifact proof. Closely coupled rows are grouped only where they share one seam:
docs/F1 (rows 6–7), package trust (rows 8–9), and TEAx evidence durability (rows 13–15).

**De-risking:** Item 3 proves the Gate B vacuity question before choosing an implementation. Item 8
specifies catalog placement and store transition before deleting any compatibility surface. Item 10
drives the ambiguous/defaulted producer counterexample before the stellarator rollup. No item may
substitute a private bridge, synthetic lower-layer object, same-machine path cancellation, or
hand-authored contract fixture for a required public-path coordinate.

---

## Relationship to the Superseded Epic

| Superseded item | Preserved result | New ownership |
|---|---|---|
| 1 — Profile semantics | Complete working-tree profile-v4 behavior and audit evidence | Item 0 lands/pins it; Item 13 composes it. |
| 2 — Generated name safety | Complete | Item 13 reuses its regressions; no separate re-audit. |
| 3 — Occurrence/demand | Not started | Items 1 and 2. |
| 3B — Gate B | Not started; old differential framing under question | Item 3, with vacuity proof first. |
| 4 — Snapshot portability/shape | Certified for its bounded manifest | Item 5 owns only the newly discovered full-tree delta. |
| 5 — Diagnostics/defaults | Not started | Item 4. |
| 6 — Seal/verify symlink symmetry | Certified | Item 7 owns new trusted-bootstrap/provenance work. |
| 7 — Dependency/tail | Not started | Item 6 owns docs/F1; existing unrelated backlog rows remain separate. |
| 8 — Release readiness | Not started and too narrow | Item 13 replaces it with the composed 41-case proof. |

---

## Backlog Items

### Item 0: Compatible Candidate Landing and Pin

**Register row**: 0
**Type**: Code/Integration
**Effort**: 0.5–1 day (reconciliation 2h, lock/version repair 2–4h, evidence 1h)
**Dependencies**: None; activates all later certification
**Status**: Complete — local compatible pin recorded 2026-07-19

**Objective**: Create one committed, mutually installable agentic-mbse/sysml-codegen/TEAx revision
set on which every later evidence coordinate is based.

**Current State**:
- ✅ sysml-codegen's completed name/portability/symlink work and lifecycle artifacts are preserved
  in local checkpoint `e217119`.
- ✅ agentic-mbse profile v4 is preserved in local checkpoint `205debd` above the committed
  modeling-orchestrator work at `4ed2a07`. The owner does not require those commits to be separated.
- ✅ The stellarator WI-027 Gate-B blocker record is preserved in local checkpoint `bceaf40a`.
- ✅ agentic-mbse `515e08b`, sysml-codegen `ecdc728`, and TEAx `d545701` form the local compatible
  starting set; exact locks and smoke evidence are recorded in Item 0 evidence.

**Scope**:
1. Reconcile intended dirty-tree changes without dropping unrelated user work.
2. Align package versions, dependency floors, runtime/profile/schema guards, and lockfiles.
3. Confirm the current package/profile guards select the intended candidate. Later items retain
   their own two-direction schema/runtime skew matrices.
4. Reconcile the current agentic-mbse branch with the PR #11 remote tip without dropping either
   committed line; then establish the compatible sysml-codegen PR #9 candidate.
5. Record exact commits, locks, dirty-state policy, and PR-wave merge order.

**Out of Scope**:
- Certifying any acceptance cell or claiming release readiness.
- Re-auditing superseded-epic Items 1/2/4/6.
- Push, PR mutation, or merge before the owning item has passed its required gates.

**Success Criteria**:
- [x] Exact hashes and locks install/build together and current guards select the intended profile.
- [x] The evidence record names the revision set inherited by later items until superseded.
- [x] The agentic-mbse candidate contains the current local commits and the PR #11 remote tip; the
      sysml-codegen candidate is based on PR #9.
- [x] Production LOC baseline is recorded by repository and subsystem.

**Deliverables**:
- `.project/active/constraint-lifecycle-candidate-pin/spec.md`
- `.project/active/constraint-lifecycle-candidate-pin/evidence.md`

---

### Item 1: Occurrence and Demand Integrity

**Register row**: 1
**Type**: Code/Integration (sysml-codegen)
**Effort**: 1.5–2 days (spec 1h, design 2h, plan 1h, execute/evidence 8–12h)
**Dependencies**: Item 0
**Status**: In progress — public RED reproduced; no production implementation yet

**Objective**: Close R-4/R-5/R-7 with occurrence-stable identity, loud finite-expansion rules, and
one deterministic demand identity.

**Scope**:
1. Replace nullable-QN membership with occurrence-stable usage identity and filter owner kinds
   before expansion.
2. Make recursive containment fail with a contextual non-finite/cycle error and no partial index.
3. Deduplicate shared calculation/constraint demand without overwriting file grouping or counts.
4. Prove distinct per-occurrence overrides, anonymous admitted/excluded behavior, and shared demand
   on the public live leg; retain the relocated anonymous leg for Item 5.
5. Delete superseded nullable-QN and duplicate-demand branches instead of layering guards.

**Out of Scope**:
- The shared calculation/constraint/aggregation resolver, owned by Item 2.
- Whole-tree location portability, owned by Item 5.

**Success Criteria**:
- [x] Anonymous actual, shared demand, recursive, finite, and distinct-override live cases pass. (Item 1 evidence.md §2-§3, candidate 28bc8b0.)
- [x] Unsupported owners never reach package fallback; no valid replay is mislabeled corrupt. (Explicit part_def/calc_def/package dispatch with no default arm; R-4 replay GREEN. Item 1 evidence.md §2.)
- [x] Counts, ordering, warnings, grouping, and retained producer are deterministic with no overwrite. (One logical operation per target; last-write-wins synthesis deleted. Item 1 evidence.md §2, §4.)
- [~] Production LOC accounting names removed duplicate/nullable paths and any increase. **Retired by owner ruling 2026-07-19 (commit a1435e1)**; deletions and the +266 net are recorded informationally in Item 1 evidence.md §1, not as a gate.

**Deliverables**:
- `.project/active/constraint-lifecycle-occurrence-demand/spec.md`
- `.project/active/constraint-lifecycle-occurrence-demand/design.md`
- `.project/active/constraint-lifecycle-occurrence-demand/plan.md`
- `.project/active/constraint-lifecycle-occurrence-demand/evidence.md`

---

### Item 2: Shared Producer Resolution and Gate A ✅

**Register row**: 2
**Type**: Code/Integration (sysml-codegen)
**Effort**: 2 days (spec 1.5h, design 2.5h, plan 1h, execute/evidence 10–12h)
**Dependencies**: Item 1

**Objective**: Replace the three drifted calculation, constraint, and aggregation ladders with one
producer/exact-QN positive resolver and make direct literal design attributes work without
passthrough calculations.

**Scope**:
1. Define one typed resolution request/result and one ordered positive ladder: real producer channel,
   then real design attribute under exact qualified identity.
2. Preserve strict/lenient differences only at terminal miss; constraints never use a calculation
   fallback or invented value.
3. Drive the real Gate A shape: usage-owned attribute on a concrete `PartUsage`, self-named actual,
   public live and relocated routes.
4. Preserve modeled defaults only when declared by the model.
5. Delete the three consumer-specific ladders and obsolete string surgery (qualitative deletion
   mandate; numeric targets retired by the 2026-07-19 owner amendment).

**Out of Scope**:
- Public late fill, placeholder completion, or post-build graph/default mutation.
- General typed-path/part-index refactors not required to unify this resolver.
- Two-consumer convergence for self-named calc bindings (SR-A02): extraction discards the
  written reference, so the calc consumer structurally cannot feed the exact key form. Referred
  to Item 4's written-reference carry (decision 2026-07-20); `tests/fixtures/shared_producer/`
  pins the current two-entry-point state until then.

**Success Criteria**:
- [x] One production resolver serves calculation, aggregation, and constraint consumers.
- [x] Direct literal design-attribute actuals resolve under real QN with no passthrough.
- [x] Unresolved or ambiguous constraint actuals fail contextually; lenient calc behavior never
      becomes an ambiguous first-pick or leaf-name guess.
- [x] Resolver precedence, source form, live/snapshot parity, and typed entry-point identity pass.
- [x] Old ladders and their duplicate tests/helpers are deleted; no parallel resolver remains.

**Audit**: Pass with notes at `039d66e` (2026-07-19, independent) —
`.project/active/constraint-lifecycle-shared-resolution/audit.md`. Every gate reproduced; all
five criteria verified. Eight findings, all artifact/docstring corrections with no production
change; the D2 residual as recorded names rows that do not conflict (F1).

**Deliverables**:
- `.project/active/constraint-lifecycle-shared-resolution/spec.md`
- `.project/active/constraint-lifecycle-shared-resolution/design.md` (phased plan folded in)
- `.project/active/constraint-lifecycle-shared-resolution/evidence.md`

---

### Item 3: Gate B Coverage-Scope Proof and Correction

**Register row**: 3
**Type**: Code/Integration (sysml-codegen with stellarator evidence)
**Effort**: 0.5–1 day (probe/spec 2h, design/plan 1.5h, execute/evidence 3–5h)
**Dependencies**: Item 2; must complete before Item 4

**Objective**: Determine whether constraint extension can introduce a new V11 violation, then keep
only the coverage check the constructed evidence proves necessary.

**Scope**:
1. Build the exact pre-existing/unrelated, newly consumed, and mixed V11 shapes from both Gate B
   reports.
2. Prove or refute whether append-only extension can create a V11 offender under current semantics.
3. If impossible, delete extension-time coverage validation. If possible, reject only the introduced
   violation by semantic identity. Do not implement a differential check by assumption.
4. Keep whole-graph channel-reference validation and strict final-generation V11 unchanged.
5. File fusion finding #8 upstream and preserve live/snapshot behavior through the shared function.

**Out of Scope**:
- Adding deferred-input annotations, capture hooks, public late fill, or placeholder defaults.
- Solving stellarator producer representation, owned by Item 10.

**Status**: Complete — vacuity proven, delete branch executed 2026-07-19. Awaiting independent audit.

**Success Criteria**:
- [x] The constructed case settles the vacuity question with kept evidence.
      **Vacuous** — closed enumeration in `findings.md`, decision in `decision.md`.
- [x] Unrelated pre-existing V11 never blocks extension; final generation remains whole-graph strict.
      `tests/unit/test_constraint_graph_extension.py`, `tests/conformance/test_gate_b_generation_gate.py`.
- [x] Strict actual resolution and dangling-channel rejection remain unchanged.
- [x] Any vacuous call/helper is deleted; no replacement wrapper preserves the dead path.
      `collect_uncovered_params` retained for its generation-gate caller only.

**Required Reading**:
- `.project/active/constraint-lifecycle-gate-b/decision.md` — the settled outcome and its re-open
  trigger. Read this before either Gate B report; both reports recommend a differential repair that
  the proof superseded.
- Both Gate B reports listed in Source Documents.
- Ratified invariants 24–26 and LC-E02–LC-E04B.

**Deliverables** (`[OWNER]` pace directive 2026-07-19: decision record in place of spec/design/plan):
- `.project/active/constraint-lifecycle-gate-b/decision.md`
- `.project/active/constraint-lifecycle-gate-b/findings.md`
- `.project/active/constraint-lifecycle-gate-b/upstream-filing.md`

**Carried out of scope**: `shared_producer` contradicts Item 2's SR-A02 / I9 convergence claim
(decision.md, "Surfaced"). Parked for Item 2's evidence owner; does not affect Gate B.

---

### Item 4: Diagnostic Severity and Modeled-Default Fidelity

**Register row**: 4
**Type**: Code/Integration (agentic-mbse + sysml-codegen)
**Effort**: 1–1.5 days (spec 1h, design 2h, plan 1h, execute/evidence 6–9h)
**Dependencies**: Item 3

**Objective**: Make extraction diagnostics load-bearing and preserve supported signed/unit defaults
without letting warning rendering hide a later halt.

**Scope**:
1. Add a versioned diagnostic severity field and stable code/sink through facts, codecs, validation,
   and codegen; unclassified trust-affecting diagnostics fail closed.
2. Add companion floor/guard changes and both schema-skew directions.
3. Make out-of-root warning rendering total and preserve warning order before `BLOCK`.
4. Preserve explicit `-0.1` and `[MW]` modeled defaults through typed entry points and generated JSON;
   unsupported wrappers never invent values.
5. Consolidate duplicated diagnostic/default parsing paths where one typed representation suffices.
6. Carry the written reference for self-named calc bindings through extraction facts and the
   snapshot format (coordinated agentic-mbse + codegen change under this item's versioned
   schema/skew machinery), completing Item 2's referred SR-A02 convergence on real data with no
   name inference (referral decision 2026-07-20).

**Out of Scope**:
- General constant folding, unit conversion, or a new diagnostics framework beyond the required
  versioned contract.

**Success Criteria**:
- [ ] Severity/code round-trip and both consumer sinks pass with fail-closed skew.
- [ ] Warning preparation cannot replace the actionable `BLOCK` diagnostic.
- [ ] Signed/unit defaults survive; unsupported default IR fails or remains explicitly unresolved.
- [ ] Diagnostic/default parsing is consolidated without a second representation or compatibility shim.

**Deliverables**:
- `.project/active/constraint-lifecycle-diagnostics-defaults/spec.md`
- `.project/active/constraint-lifecycle-diagnostics-defaults/design.md`
- `.project/active/constraint-lifecycle-diagnostics-defaults/plan.md`
- `.project/active/constraint-lifecycle-diagnostics-defaults/evidence.md`

---

### Item 5: Whole-Tree Snapshot Portability

**Register row**: 5
**Type**: Code/Integration (sysml-codegen)
**Effort**: 1–1.5 days (spec 1h, design 1.5h, plan 1h, execute/evidence 6–9h)
**Dependencies**: Item 4; completes Item 1's relocated anonymous leg

**Objective**: Extend the certified Item 4 portability boundary to every semantic and generated
byte, including admitted anonymous identity and calculation docstrings.

**Scope**:
1. Remove checkout-absolute paths from loader-reconstructed fields, eligible/excluded IDs,
   fingerprints, catalogs/contracts/reports, generated code/docstrings, and the full tree.
2. Preserve source referent meaning without same-machine cancellation.
3. Prove live A/live B/relocated replay equivalence for graph, retained producers, catalog,
   fingerprints, and every generated byte.
4. Complete the anonymous-admitted-with-actual relocated case from Item 1.
5. Reuse the certified transaction/shape-gate machinery; do not re-audit old Item 4.

**Out of Scope**:
- Snapshot schema expansion unrelated to portable referents.
- Historical snapshot reproducibility under historical profile semantics.

**Success Criteria**:
- [ ] No checkout-absolute bytes occur anywhere in the generated tree or semantic artifacts.
- [ ] Same semantic input at two checkout roots produces byte-identical output and identity.
- [ ] Anonymous admitted/excluded and calculation-bearing fixtures pass both public routes.
- [ ] Obsolete path-normalization branches are consolidated/deleted; no same-machine workaround remains.

**Deliverables**:
- `.project/active/constraint-lifecycle-portability/spec.md`
- `.project/active/constraint-lifecycle-portability/design.md`
- `.project/active/constraint-lifecycle-portability/plan.md`
- `.project/active/constraint-lifecycle-portability/evidence.md`

---

### Item 6: Public Documentation and F1 Evidence Reconciliation

**Register rows**: 6–7
**Type**: Testing/Validation + Documentation
**Effort**: 1 day (inventory/spec 1h, plan 0.5h, reconciliation/docs/evidence 5–6h)
**Dependencies**: Item 5

**Objective**: Make public claims and F1 evidence agree with the pinned landed candidate without
reimplementing already-landed normalization.

**Scope**:
1. Update profile/package versions, equality/ordering, subtype coverage, snapshot replay, and
   extension/final V11 documentation to the ratified contract and pinned candidate.
2. Record TEAx F1 at `d545701`, correct the stale `927a9e1` audit reference, and compare complete
   report contents across evaluators.
3. Scope invalid `TEAX_SIMKIT_PATH` behavior to codegen test infrastructure and make an explicit
   invalid path fail instead of discovering a sibling.
4. Reconcile PR descriptions/evidence without claiming release readiness.
5. Delete stale comments, duplicate version literals, and obsolete documentation helpers where safe.

**Out of Scope**:
- Reimplementing F1 normalization.
- Final PR update/push, owned by the authorized release workflow after Item 13.

**Success Criteria**:
- [ ] Every correction-register claim agrees with landed code and versions.
- [ ] F1 evidence names the correct commit and compares exact report content.
- [ ] Invalid explicit simkit path never falls through.
- [ ] Stale documentation helpers and duplicate version literals are removed where superseded.

**Deliverables**:
- `.project/active/constraint-lifecycle-docs-f1/spec.md`
- `.project/active/constraint-lifecycle-docs-f1/plan.md`
- `.project/active/constraint-lifecycle-docs-f1/evidence.md`

---

### Item 7: Trusted Package Bootstrap and Seal Provenance

**Register rows**: 8–9
**Type**: Code/Integration (sysml-codegen + TEAx)
**Effort**: 1.5–2 days (spec 1.5h, design 2h, plan 1h, execute/evidence 8–12h)
**Dependencies**: Item 6

**Objective**: Ensure no untrusted package code runs before verification and a re-seal cannot
launder foreign files into generated provenance.

**Scope**:
1. Move verification trust to runtime-owned code or authenticate package-local verifier bytes before
   execution.
2. Single-source verifier/runtime-contract versions or define an explicit fail-closed compatibility
   table with both skew directions.
3. Add a generation manifest distinguishing codegen-produced, preserved-handwritten, and runtime
   artifacts.
4. Preserve the certified stdlib-only symlink/path policy and prove foreign-file re-seal rejection.
5. Consolidate duplicated verifier/version machinery without merging deliberate seal/verify walkers.

**Out of Scope**:
- A second catalog schema authority.
- Re-auditing the certified Item 6 symlink matrix.

**Success Criteria**:
- [ ] An unconditional-success package verifier is rejected before any package code executes.
- [ ] Verifier/runtime-contract skew fails closed in both directions.
- [ ] Re-sealing cannot classify an arbitrary foreign file as codegen-produced.
- [ ] Existing seal→verify regular-file and symlink guarantees remain green.
- [ ] Verification and provenance have one authoritative implementation with no duplicate bypass.

**Deliverables**:
- `.project/active/constraint-lifecycle-package-trust/spec.md`
- `.project/active/constraint-lifecycle-package-trust/design.md`
- `.project/active/constraint-lifecycle-package-trust/plan.md`
- `.project/active/constraint-lifecycle-package-trust/evidence.md`

---

### Item 8: Canonical Embedded Catalog and Store Transition

**Register row**: 10
**Type**: Code/Integration (sysml-codegen + TEAx + fusion consumer cleanup)
**Effort**: 2 days (spec 1.5h, design 2.5h, plan 1h, execute/evidence 10–12h)
**Dependencies**: Item 7

**Objective**: Make codegen's embedded model-contract catalog the only schema authority and move
TEAx/store identity to real semantic/catalog/executable fingerprints.

**Scope**:
1. Add the admitted per-usage record and five TEAx-consumed fields on each eligible concrete entry:
   source form, usage short name/QN, real `owner_qn`, `definition_qn`, and entry-level
   definition-to-usage join.
2. Make TEAx config/query/CLI/fixtures consume real codegen model contracts directly.
3. Replace the stand-in catalog-byte hash with real semantic/catalog/executable identity.
4. Migrate an old store only with artifact-equivalence proof; otherwise preserve it as archived
   lineage and start a new store.
5. Delete the alternate TEAx catalog schema, fusion materializer, hand-authored schema fixture,
   stand-in fingerprint, QN splitting, predicate-text search, hardcoded source form, and semantic
   reconstruction.

**Out of Scope**:
- A differently shaped standalone canonical catalog. Any later export must be mechanically identical
  to the embedded schema and independently justified.

**Success Criteria**:
- [ ] Catalog coverage is total across definition, usage, concrete occurrence, exclusion, and result.
- [ ] TEAx uses no alternate schema or reconstruction path and consumes codegen's real identity.
- [ ] Store migration proves equivalence or old stores remain explicitly archived; no silent rebind.
- [ ] Catalog/schema skew fails closed before semantic use.
- [ ] The named alternate catalog/materializer/fixture/stand-in system is removed; the embedded
      model-contract catalog is the sole authority.

**Deliverables**:
- `.project/active/constraint-lifecycle-catalog-store/spec.md`
- `.project/active/constraint-lifecycle-catalog-store/design.md`
- `.project/active/constraint-lifecycle-catalog-store/plan.md`
- `.project/active/constraint-lifecycle-catalog-store/evidence.md`

---

### Item 9: Multi-Entry Candidate Bridge

**Register row**: 11
**Type**: Code/Integration (TEAx)
**Effort**: 1–1.5 days (spec 1h, design 1.5h, plan 1h, execute/evidence 6–9h)
**Dependencies**: Item 8

**Objective**: Make the stock TEAx bridge construct complete typed mappings for zero, one, or many
generated entry channels without a consumer wrapper.

**Scope**:
1. Represent baseline typed models for every entry channel and overrides for selected fields.
2. Validate missing, extra, malformed, and wrong-typed channel mappings before evaluation.
3. Preserve ordinary declared design inputs without treating them as missing graph producers.
4. Delete fusion's `MultiChannelEvaluator` and any single-entry assumptions duplicated across
   config, definition, and bridge layers.

**Out of Scope**:
- Model-derived late fill or graph mutation.
- Constraint-free report semantics, owned by Item 11.

**Success Criteria**:
- [ ] Zero/one/multiple mappings validate completely and no unrelated channel is omitted.
- [ ] Candidate overrides change only selected typed fields.
- [ ] Stock TEAx replaces the fusion wrapper through public APIs.
- [ ] Single-entry duplicate paths are consolidated/deleted; stock TEAx owns the public route.

**Deliverables**:
- `../teax/.project/active/constraint-lifecycle-multi-entry/spec.md`
- `../teax/.project/active/constraint-lifecycle-multi-entry/design.md`
- `../teax/.project/active/constraint-lifecycle-multi-entry/plan.md`
- `../teax/.project/active/constraint-lifecycle-multi-entry/evidence.md`

---

### Item 10: Producer Completeness and Stellarator Rollup

**Register row**: 12
**Type**: Code/Integration + Modeling (sysml-codegen + stellarator)
**Effort**: 2 days (spec 1.5h, design 2.5h, plan 1h, execute/evidence 10–12h)
**Dependencies**: Item 9

**Objective**: Prove every model-derived consumed value resolves to one intended producer independent
of V11, then represent the stellarator capital rollup in the ordinary graph.

**Scope**:
1. Add the ambiguous/defaulted producer acceptance: two same-leaf candidates and a fallback/default
   shape must fail contextually or resolve only under exact QN; no guessed verdict is produced.
2. Define/enforce producer completeness separately from V11 while preserving legitimate external
   typed design inputs.
3. Teach codegen to compile the modeled cross-part capital aggregation using the same graph machinery
   as calculations/aggregations, not consumer mutation.
4. Amend WI-027 D7 to point at the later owner decision and remove all passthrough calculations.
5. Remove the stellarator private bridge/placeholders and generate publicly with unchanged ordinary
   numerics.
6. Delete now-obsolete aggregation/resolver workarounds; do not retain a compatibility wrapper.

**Out of Scope**:
- Public late fill or a permanent model placeholder.
- Weakening exact-QN resolution, final V11, or declared external-input semantics.

**Success Criteria**:
- [ ] Ambiguous/defaulted resolution cannot produce a verdict while V11 is clean.
- [ ] Intended producer completeness is explicit, deterministic, and independent of V11.
- [ ] WI-027 contains the supersession pointer; D7 passthroughs and private bridge/mutation are gone.
- [ ] Public generation builds a fully representable stellarator graph with unchanged ordinary
      numerical anchors.
- [ ] Named aggregation/resolver workarounds are deleted and no parallel producer mechanism remains.

**Required Reading**:
- Ratified D-1/D-2 and invariants 19–26.
- WI-027 spec/design/plan and both Gate B reports.

**Deliverables**:
- `.project/active/constraint-lifecycle-producer-completeness/spec.md`
- `.project/active/constraint-lifecycle-producer-completeness/design.md`
- `.project/active/constraint-lifecycle-producer-completeness/plan.md`
- `.project/active/constraint-lifecycle-producer-completeness/evidence.md`
- Updated `../fusion-tea-stellarator-mbse-demo/work/active/WI-027_demo-constraint-execution/`

---

### Item 11: TEAx Constraint Evidence Durability

**Register rows**: 13–15
**Type**: Code/Integration (TEAx, with generated-package fixtures from codegen)
**Effort**: 2 days (spec 1.5h, design 2h, plan 1h, execute/evidence 10–12h)
**Dependencies**: Item 10

**Objective**: Make constraint-free and completed constraint evidence work identically through
prepared and file-backed evaluators, remain immutable, and persist/query without an adapter.

**Scope**:
1. Treat absence of a constraint report as empty constraint evidence through both evaluator routes;
   eliminate every unconditional report read.
2. Deep-freeze or defensively isolate the envelope, generated report, nested results, observations,
   status, and margin before policy can access them.
3. Register, route, persist, and harvest exact completed report JSON for satisfied, violated,
   indeterminate, and `assessment_failed` outcomes with package identity.
4. Pin expected failure phase per arithmetic shape; do not establish phase truth by evaluator
   agreement alone. Emit `OUTPUT_WRITE` honestly or collapse the unused phase.
5. Prove excluded-only zero-eligible packages evaluate to `not_assessed` while zero-usage packages
   yield empty evidence.
6. Remove generic/duplicate report adapters and incidental encode-before-policy protection once the
   explicit mechanism owns durability.

**Out of Scope**:
- Reinterpreting verdicts as study policy.
- Recreating a consumer-specific catalog/report schema.

**Success Criteria**:
- [ ] Constraint-free packages pass prepared and file-backed evaluation with empty evidence.
- [ ] Excluded-only packages produce the exact `not_assessed` surface.
- [ ] Nested mutation attempts cannot change authoritative or persisted evidence.
- [ ] Exact reports persist/harvest for every completed status and remain compatibility-bound.
- [ ] Phase/module/cause/report parity uses fixture-pinned expected phases.
- [ ] Duplicate report adapters and unconditional reads are deleted; one durability mechanism remains.

**Deliverables**:
- `../teax/.project/active/constraint-lifecycle-evidence-durability/spec.md`
- `../teax/.project/active/constraint-lifecycle-evidence-durability/design.md`
- `../teax/.project/active/constraint-lifecycle-evidence-durability/plan.md`
- `../teax/.project/active/constraint-lifecycle-evidence-durability/evidence.md`

---

### Item 12: Legacy Snapshot and Tracking Identity Closure

**Register row**: 16
**Type**: Code/Integration (sysml-codegen)
**Effort**: 1–1.5 days (spec 1h, design 1.5h, plan 1h, execute/evidence 6–9h)
**Dependencies**: Item 11

**Objective**: Remove the silent constraint-drop path for grandfathered snapshots and make the
cross-version correlation story real or delete it.

**Scope**:
1. Fail closed on `grandfathered_off` in normal generation before a certifying seal can exist.
2. If retained, expose legacy inspection only through an explicit opt-in, visibly non-executable
   and non-certifying mode.
3. Either populate/catalog/test `tracking_key` as the author correlation key or delete the field and
   every cross-version correlation claim.
4. Preserve the distinction between semantic, catalog, executable, proposal, case, attempt, and
   artifact identities.
5. Delete the fail-open branch and dead identity surface not selected by design.

**Out of Scope**:
- Claiming anonymous identities are stable across versions without an explicit author key.

**Success Criteria**:
- [ ] Normal product generation cannot silently drop constraints from a grandfathered snapshot.
- [ ] Legacy inspection cannot execute or produce a certifying package.
- [ ] `tracking_key` is fully implemented/cataloged or absent with documentation corrected.
- [ ] Resume/query mismatch behavior remains fail-closed or starts explicit new lineage.
- [ ] The rejected legacy/identity path is deleted rather than hidden behind another default route.

**Deliverables**:
- `.project/active/constraint-lifecycle-legacy-identity/spec.md`
- `.project/active/constraint-lifecycle-legacy-identity/design.md`
- `.project/active/constraint-lifecycle-legacy-identity/plan.md`
- `.project/active/constraint-lifecycle-legacy-identity/evidence.md`

---

### Item 13: Composed Public Lifecycle Proof and Release Readiness

**Register row**: 17
**Type**: Testing/Validation (all repositories and consumers)
**Effort**: 2 days (spec/manifest 1h, plan 1h, execution 10–12h, report 2h)
**Dependencies**: Items 0–12; strictly last

**Objective**: Certify every mandatory acceptance case and the two real consumers on one pinned,
public, sealed artifact thread.

**Scope**:
1. Run all 41 acceptance cases with the complete LC-I09 coordinate: exact commits/locks, fixture
   shape, source-originated semantics, open predecessors, both public routes, and artifact identity.
2. Run live A/live B/relocated replay, full-tree byte checks, generation, seal, runtime-trusted load,
   prepared/file-backed evaluation, persistence, resume/query, and negative mutations.
3. Run exact IFE 2,301-point acceptance through stock seams with unchanged anchors.
4. Run the stellarator five-constraint, multi-entry acceptance with no D7 passthrough, bridge,
   placeholder, mutation, alternate catalog, or consumer wrapper.
5. Run focused/optimized, compatible full suites, lint/format/type baselines, fixture diff review,
   and licensed live routes at the final revisions.
6. Confirm superseded paths named by Items 1–12 are deleted, not shimmed, and no parallel authority
   or route replaces them.
7. Produce the release-readiness report and only then update existing agentic-mbse PR #11 first and
   sysml-codegen PR #9 second with the final commits, accurate descriptions, and evidence. Do not
   open replacement upstream PRs for this remediation.

**Out of Scope**:
- Fixing a failure discovered here without returning it to its owning predecessor item.
- Counting a private seam, stale revision, skipped cell, or lower-layer synthetic fixture as proof.

**Success Criteria**:
- [ ] Every mandatory matrix cell is certified at the same pinned revision set; none is skipped,
      blocked, or served by a private workaround.
- [ ] One artifact thread passes public live/relocated generation, seal/load/evaluate/persist/query.
- [ ] IFE and stellarator acceptances pass with the required public shapes and unchanged numerics.
- [ ] Every negative mutation fails at its intended boundary before a later failure can mask it.
- [ ] Final evidence names exact hashes, locks, manifests, commands, artifacts, and remaining
      external state.
- [ ] Existing PR #11 and PR #9 point at the certified commits and accurately state the final
      lifecycle scope, evidence, remaining external state, and required merge order.
- [ ] Superseded paths named by Items 1–12 are verified deleted with no replacement shim or
      duplicate authority.

**Deliverables**:
- `.project/active/constraint-lifecycle-composed-proof/spec.md`
- `.project/active/constraint-lifecycle-composed-proof/plan.md`
- `.project/active/constraint-lifecycle-composed-proof/evidence-coordinate-register.md`
- `.project/active/constraint-lifecycle-composed-proof/release-readiness.md`

---

## Dependencies

**External**:
- A working SysIDE license is required only for live extraction/capture and licensed full-suite
  evidence. Snapshot/unit, package, and TEAx work proceeds independently; pandas is an ordinary
  runtime dependency, not a licensed gate.
- The existing agentic-mbse PR #11 and sysml-codegen PR #9 are required delivery vehicles. The
  owner authorized local checkpoint commits on 2026-07-19. Item 13 owns the final push and PR
  updates after certification; merge remains a separate human action.
- IFE and stellarator repositories must be available at their pinned consumer revisions for Items
  10 and 13.

**Internal**:
- The ratified lifecycle contract and companion spec are the behavioral authority.
- Superseded-epic Items 1/2/4/6 are inherited evidence, not prerequisites to re-audit.
- `[CONSTRAINT-ARCH-UNIFY]` resolver scope is absorbed by Item 2; CE-F1 by Item 8; CE-F2 by Item 9.
- GAP-CLOSE F1 implementation is not redone. Item 6 reconciles its evidence and exact revision.

**Item Dependency Graph**:

```text
Item 0  Candidate pin
  └─> Item 1  Occurrence/demand
        └─> Item 2  Shared resolver + Gate A
              └─> Item 3  Gate B scope proof
                    └─> Item 4  Diagnostics/defaults
                          └─> Item 5  Whole-tree portability
                                └─> Item 6  Docs/F1 reconciliation
                                      └─> Item 7  Package trust/provenance
                                            └─> Item 8  Canonical catalog/store
                                                  └─> Item 9  Multi-entry bridge
                                                        └─> Item 10 Producer completeness/stellarator
                                                              └─> Item 11 TEAx evidence durability
                                                                    └─> Item 12 Legacy/tracking identity
                                                                          └─> Item 13 Composed proof
```

Specification and design work may overlap where file ownership permits. Certification remains
ordered, and all implementation lands in the same constraint PR unit.

---

## Risks

| Risk | Impact | Mitigation |
|---|---|---|
| A later item certifies on a different revision or around an open predecessor | High | LC-I09 coordinate records commits, artifact identity, and open predecessor rows; Item 13 rejects mixed-revision evidence. |
| Simplification becomes another layer of guards/adapters | High | Review named superseded paths for absence and reject any new parallel authority, route, or compatibility shim. |
| Catalog schema growth hides an overall expansion | High | Book Item 8 schema additions separately and require deletion of alternate schema/materializer/fixture/stand-in machinery. |
| Resolver consolidation changes precedence or invents values | High | Drive exact-QN and ambiguous/defaulted counterexamples first; strictness changes only terminal miss. |
| Gate B implements a differential check that can never fire | High | Item 3 proves/refutes extension-created V11 before implementation; delete the call if vacuous. |
| Completed Item 4/6 scopes are accidentally reopened | Medium | Treat their audits as inherited; new Items 5/7 name only adversarially discovered adjacent gaps. |
| Consumer workaround is counted as product proof | High | Public-seam classification is part of every coordinate; private bridges/materializers/wrappers are deletion targets. |
| Store identity cutover strands historical results silently | High | Migration requires equivalence proof; otherwise archive the old lineage and start a new one. |
| Full-tree parity passes by same-machine cancellation | High | Two checkout roots plus an absolute-byte scan over the entire generated tree are mandatory. |
| Live licensed evidence is unavailable at final candidate | Medium | Continue license-free work, record the exact missing live cell, and do not substitute snapshot evidence or claim release readiness. |
| Program-sized epic loses the thread | High | Each item maps to explicit register rows; no later certification while a predecessor is open; CURRENT_WORK and this epic are updated at every item boundary. |

---

## Timeline

**Total Effort**: 19–23 working days. This is person-time. Planning/design may overlap, but the
certification critical path remains ordered.

| Item | Effort | Register rows | Dependencies |
|---|---:|---:|---|
| 0. Compatible candidate landing and pin | 0.5–1 d | 0 | None |
| 1. Occurrence and demand integrity | 1.5–2 d | 1 | Item 0 |
| 2. Shared producer resolution and Gate A | 2 d | 2 | Item 1 |
| 3. Gate B scope proof and correction | 0.5–1 d | 3 | Item 2 |
| 4. Diagnostic severity and defaults | 1–1.5 d | 4 | Item 3 |
| 5. Whole-tree snapshot portability | 1–1.5 d | 5 | Item 4 |
| 6. Public docs and F1 reconciliation | 1 d | 6–7 | Item 5 |
| 7. Trusted bootstrap and seal provenance | 1.5–2 d | 8–9 | Item 6 |
| 8. Canonical catalog and store transition | 2 d | 10 | Item 7 |
| 9. Multi-entry candidate bridge | 1–1.5 d | 11 | Item 8 |
| 10. Producer completeness and stellarator | 2 d | 12 | Item 9 |
| 11. TEAx constraint evidence durability | 2 d | 13–15 | Item 10 |
| 12. Legacy snapshot and tracking identity | 1–1.5 d | 16 | Item 11 |
| 13. Composed proof and release readiness | 2 d | 17 | Item 12 |

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
**Next Action**: Complete Item 1, then begin Item 2 from the compatible candidate pin.
