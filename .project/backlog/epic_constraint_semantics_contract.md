# Epic: Constraint Semantics and Design-Search Feasibility

**Epic ID**: CONSTRAINT-SEMANTICS
**Status**: Ready (scope and decomposition approved by owner 2026-08-12; product lens CLEAR)
**Priority**: Critical (P0 — owner-directed prerequisite for ELABORATE-FIRST Item 7 steps 4–10)
**Created**: 2026-08-12
**Estimated Effort**: 8.5–9.5 working days over 2–3 weeks, plus owner-checkpoint turnaround

---

## Executive Summary

This epic makes modeled constraint meaning, catalog visibility, generated reports, and TEAx study
policy agree on one design-search feasibility contract. It closes the measured CATF failure in
which 65 authored constraints yield 9 visible dispositions and 0 executed checks, then proves the
contract on a new derivative fixture without changing the two frozen CATF witnesses.

**Critical Success Factor**: **[OWNER]** A design search can trust the generated feasibility
evidence to represent every applicable asserted physics gate, while every other authored
constraint remains visibly dispositioned.

---

## Source Documents

- **[umbrella spec — provided input]**
  [`../active/constraint-semantics-contract/spec.md`](../active/constraint-semantics-contract/spec.md)
  — the behavioral contract, success criteria, non-goals, and required child-item structure.
- **[research]**
  [`../research/20260812-101200_constraint-semantics-end-to-end.md`](../research/20260812-101200_constraint-semantics-end-to-end.md)
  — the 65-usage CATF measurement, working fusion-tea referent, D1–D7 contradiction register,
  and the two reproduced defects.
- **[decision record]**
  [`../active/constraint-semantics-contract/rulings-20260812.md`](../active/constraint-semantics-contract/rulings-20260812.md)
  — the owner-verbatim payloads and agent-proposed rulings ratified by the owner on 2026-08-12.
- **[spec review]**
  [`../active/constraint-semantics-contract/spec-review.md`](../active/constraint-semantics-contract/spec-review.md)
  — the resolved coverage, totality, CATF-denominator, and umbrella-structure findings.
- **[product-lens ledger]**
  [`../active/constraint-semantics-contract/product-lens.md`](../active/constraint-semantics-contract/product-lens.md)
  — the one-authority, contract-amendment, and Item 7 evidence-invalidation obligations.

---

## Why This Epic?

**Current State**:

- CATF authors 65 constraint usages, but only 9 receive catalog dispositions and none execute;
  56 vanish before the catalog because the current authority lacks a complete pre-expansion
  authored-usage domain.
- A report can claim `all_satisfied` over partial assessment, an excluded-only model receives no
  report, and TEAx cannot distinguish that model from a genuinely unconstrained package.
- Product guidance contradicts the SysML/KerML plain-versus-asserted distinction and the shipped
  profile. Two concrete defects also block or obscure correct asserted predicates.
- ELABORATE-FIRST Item 7 steps 4–10 are paused because their catalog, report, fixture, and
  recapture evidence would be invalidated by this contract work.

**Future State**:

- Plain constraints remain visible descriptions; supported asserted constraints are the only
  enforced gates; requirement-side forms remain visible and non-executable.
- One graph-and-embedded-catalog authority accounts for every authored usage and hard-fails on a
  missing disposition without maintaining a parallel inventory.
- Generated reports and TEAx policy distinguish full, partial, unassessed, violated,
  indeterminate, and truly unconstrained states with durable coverage accounting.
- A new CATF derivative carries an owner-reviewed disposition for all 65 usages and proves a real
  unphysical candidate is rejected, while calc-definition gate execution remains a separately
  staged capability with ruled semantics.

---

## Success Criteria

- [ ] **[INHERITED: constraint-semantics-contract/spec.md] One product rule is stated consistently.**
      The lifecycle contract, frozen requirements companion, ADR, codegen references, and
      agentic-mbse authoring guidance agree on assert-only enforcement; D1–D7 are corrected; the
      equality-intent taxonomy and modeler-owned tolerance rule are published.
- [ ] **[INHERITED: constraint-semantics-contract/spec.md] Catalog totality is complete and
      non-circular.** One canonical authority records the full authored-usage domain before
      occurrence expansion, gives every usage exactly one visible disposition, and halts
      generation on any missing disposition. Both the frozen `catf_mfe_d5` and the derivative
      show 65/65 carriers; REQ-EXT-09 and REQ-CL-04 are re-graded and re-anchored.
- [ ] **[INHERITED: constraint-semantics-contract/spec.md] Severity follows the cause.** An
      asserted structurally unattachable usage halts generation; an asserted vacuous usage is
      warning-grade and holds feasibility at partial coverage until fixed or explicitly marked
      inapplicable; plain and out-of-scope forms remain visible without halting generation.
- [ ] **[INHERITED: constraint-semantics-contract/spec.md] Report coverage is truthful.**
      `all_satisfied` requires every applicable asserted gate to be assessed and pass; missing
      assessment produces the new partial state; descriptive-only models emit a zero-input
      `not_assessed` report; constraint-free models remain report-free.
- [ ] **[INHERITED: constraint-semantics-contract/spec.md] TEAx consumes every report state
      deliberately.** Report and canonical runtime vocabularies are normalized fail-closed;
      partial coverage defaults to keep-for-boundary, feed-strategy requires an explicit study
      opt-in, and coverage is persisted in durable case records.
- [ ] **[INHERITED: constraint-semantics-contract/spec.md] The CATF derivative proves the policy
      end to end.** Its table dispositions all 65 usages; the nine instance-reaching gates carry
      owner-approved intent, target form, and tolerances; the five part-definition guards and 51
      calculation-definition guards have explicit outcomes; all applicable asserted gates are
      covered; a mutation rejects an unphysical candidate through the real TEAx route.
- [ ] **[INHERITED: constraint-semantics-contract/spec.md] Calc-definition gate delivery is
      staged honestly.** One asserted check per calculation occurrence is captured as the ruled
      behavior in its own designed backlog item; until that capability lands, asserted
      calculation-definition constraints fail loudly instead of disappearing.
- [ ] **[INHERITED: constraint-semantics-contract/spec.md] Both named defects are fixed.**
      Unit-annotated literals inside asserted predicates elaborate correctly, and a blocked
      predicate feature chain reports the offending reference plus the bindings rewrite.
- [ ] **[OWNER] Documentation and the derivative's expected outputs are corrected and captured
      before confirmation tests run.** Test expectations are not reverse-engineered from current
      behavior.
- [ ] **[INHERITED: constraint-semantics-contract/product-lens.md] Item 7 resumes from valid
      evidence.** The epic records every invalidated step-4, step-7, step-8, and 37-fixture
      recapture artifact and assigns each rerun or absorption before the paused correction
      continues.

---

## Product-Lens

### epic-plan — 2026-08-12 — rev .project/backlog/epic_constraint_semantics_contract.md

Point (re-derived): Constraint handling must enforce modeled physics and consistency so design
search stays viable, with clear expectations proven against the richest model; documentation and
expected outputs precede confirmation tests. [source:
`.project/active/constraint-semantics-contract/rulings-20260812.md`, grade: owner]

Falsifier: An applicable asserted CATF gate is absent or unassessed while the report claims full
satisfaction and TEAx accepts the design.

Findings:

- None. No item narrows or contradicts the point, and the six-item set plus the epic-owned
  evidence-invalidation register covers the point's obligations.

Gate: CLEAR

---

## Epic Strategy

**Boundary authority**: The six-item slicing is **[AGENT] (ratified by owner, 2026-08-12)**.
Behavioral obligations retain the provenance recorded in the umbrella spec and ruling record.

The epic moves one authority boundary at a time. Item 1 publishes the contract and authoring rule
before implementation. Item 2 then makes the instance graph and embedded catalog own the complete
authored-usage domain. Item 3 derives report and study behavior from that authority instead of
introducing a second coverage inventory. Item 4 fixes the two reproduced predicate-boundary
defects in parallel. Item 5 is the composed proof: the owner dispositions all 65 CATF usages,
expected outputs are captured, and only then do confirmation tests run. Item 6 designs the staged
calculation-definition capability against the representation Item 2 actually lands.

**Critical path**:

```text
Item 1 -> Item 2 -> Item 3 -> Item 5
```

**Parallel path**:

- Item 4 runs after Item 1 alongside Items 2–3 and must finish before Item 5 acceptance.
- Item 5's all-65 owner checkpoint begins after Item 1; model implementation waits for Items 2–4.
- Item 6 begins after Item 2 and can run alongside Items 3–5. It does not block the derivative
  because the 51 calculation-definition guards may be dispositioned `awaits-capability`.

**De-risking**:

- Items 2–4 start from reproduced failures in the research record, so each begins with a kept
  failing characterization rather than a separate discovery item.
- Item 5 places the domain checkpoint before design. No tolerance, intent class, or
  inapplicability decision is inferred by the implementing agent.
- Item 6 opens with a throwaway probe over one calculation-definition constraint and its concrete
  calculation occurrences. If attachment requires a second occurrence authority or rendered-name
  reconstruction, the item parks dependent design conclusions and returns for redesign.

### Item 7 Evidence-Invalidation Register

| Paused evidence | Disposition in this epic | Resume action |
|-----------------|--------------------------|---------------|
| Step 4 zero-input report and REQ-CL-04/REQ-EXT-09 closures | Absorbed by Items 2–3 under the amended contract; the old closures are retired | The revised step-4 brief cites the new tests and grades |
| Step 4 REQ-CL-03 pre-amendment behavior check | Superseded where the new contract changes coverage and disposition semantics | Re-derive the row against the amended contract in Items 1–3, then revise the step-4 brief |
| Step 4 `gain = 100` live, in-place-snapshot, and relocated-snapshot proof | Kept as Item 7 evidence, but any pre-epic run would be stale | Run once after this epic on the final paired codegen/agentic OIDs |
| Item 7's 37-fixture instance-graph recapture | Item 2 decides whether the canonical-domain representation changes the snapshot schema; if so, Item 2 owns one reviewed recapture at its final schema | Item 7 consumes Item 2's final snapshot bytes; another recapture occurs only if later Item 7 code changes them |
| Every paused Item 7 snapshot-route observation taken against `instance-graph/v2` bytes | **Invalid.** Item 2 bumped the instance-graph schema to `v3`; no v2 reader is kept, so any v2-derived observation cannot be reproduced | Re-observe against the recaptured v3 bytes |
| Byte-identity comparisons on the 21 recaptured fixtures | **Invalid.** All 21 snapshot-bearing fixtures were recaptured once at the v3 schema (Item 2, 2026-08-12); every one gained `constraint_usages`, and three also moved `owner_kind` from the ungraded `partusage` to `part_usage` | Re-baseline against the recaptured bytes; the reviewed diff is in Item 2's `verification.md` |
| Any Item 7 evidence citing `collect_constraint_manifest` as the population definition | **Invalid.** The sweep, its two classifiers, `extraction/constraint_report.py`, and all seven test call sites were deleted in Item 2 Phase 7c | Re-cite `tests/conformance/test_constraint_population_oracle.py`, whose expected-population files are the replacement authority |
| Step 7 three complete batteries | Deferred until every substantive epic change has landed | Run once at the final paired OIDs after the epic |
| Step 8 candidate record | Invalid until the final batteries exist | Regenerate once from the post-epic batteries and final paired OIDs |

---

## Backlog Items

### Item 1: Contract and Authoring Policy (1.5 days)

**Type**: Contract / Documentation

**Boundary authority**: **[AGENT] (ratified by owner, 2026-08-12)**. Behavioral requirements are
**[INHERITED: constraint-semantics-contract/spec.md]** unless separately marked.

**Objective**: Publish one constraint-semantics contract and one authoring rule before any
implementation changes the catalog or report.

**Current State**:

- ✅ The umbrella spec, owner ruling record, research, and resolved review define the required
  semantics and amendment set.
- ⚠️ The lifecycle contract and frozen requirements companion still define the old headline and
  disposition behavior.
- ❌ No ADR records the intentional coverage-vocabulary change, and D1–D7 still teach conflicting
  constraint forms or cite retired evidence.

**Scope**:

1. File the coverage-headline ADR with accurate agent-originated, owner-ratified provenance.
2. Amend the lifecycle contract invariant-by-invariant, including invariants 1, 8/9, 28, 32, 33,
   46/46a, 48 and affected Appendix C cells.
3. Amend the frozen requirements companion, including LC-E05/E06/E10/E11/E12, without changing
   the provenance grades of inherited statements.
4. Correct D1–D7 across codegen and agentic-mbse by amendment or deletion. Publish the blessed
   assert-with-bindings pattern, the equality-intent taxonomy, and the rule that tolerances are
   modeled values chosen by the modeler.
5. Define the semantic meaning of both report and canonical runtime headline vocabularies. Item 3
   owns their concrete schema and code spellings.

**Out of Scope**:

- Catalog, report, projection, policy, or fixture implementation.
- Calculation-definition attachment design, owned by Item 6.

**Success Criteria**:

- [ ] **[INHERITED: spec.md]** A live ADR records the intended contract change and is cited from
      the product-lens disposition trail.
- [ ] **[INHERITED: spec.md]** The lifecycle contract and requirements companion publish the full
      amendment set with their original provenance intact.
- [ ] **[INHERITED: research D1–D7]** Codegen and agentic-mbse contain no remaining statement that
      a plain or requirement-side constraint is an enforced gate.
- [ ] **[NEED carried from spec.md]** Authoring guidance explains when equality intent should be
      derived, band-checked, one-sided, fixed as input, or closed by construction.
- [ ] **[OWNER]** Documentation is correct before confirmation testing begins.
- [ ] Documentation checks and `git diff --check` pass in every touched repository.

**Estimated Effort**: 1.5 days (spec 1h, design 2h, plan 1h, execute and review 8h)

**Location**: `.project/active/constraint-semantics-contract-amendments/`

**Dependencies**: None; the approved umbrella spec is the input.

**Required Reading**:

- `.project/active/constraint-semantics-contract/spec.md`
- `.project/active/constraint-semantics-contract/rulings-20260812.md`
- `.project/research/20260812-101200_constraint-semantics-end-to-end.md` §7 (D1–D7)
- `.project/active/constraint-semantics-contract/product-lens.md`
- `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md`
- `.project/concepts/constraint-execution-lifecycle-requirements.md`

**Deliverables**:

- `.project/active/constraint-semantics-contract-amendments/spec.md`
- `.project/active/constraint-semantics-contract-amendments/design.md`
- `.project/active/constraint-semantics-contract-amendments/plan.md`
- Live ADR plus amended contract, requirements companion, codegen references, and agentic-mbse
  authoring guidance.
- `.project/active/constraint-semantics-contract-amendments/verification.md`

---

### Item 2: Canonical Usage Domain and Catalog Totality (2 days)

**Type**: Code / Integration

**Boundary authority**: **[AGENT] (ratified by owner, 2026-08-12)**. Behavioral requirements are
**[INHERITED: constraint-semantics-contract/spec.md]** unless separately marked.

**Objective**: Make the graph and embedded catalog account for every authored constraint usage
before occurrence expansion can erase it.

**Current State**:

- ✅ The exact route already owns resolved constraint nodes, catalog generation, sealed snapshots,
  and generation preflights.
- ⚠️ Constraint records begin after owner-to-scope expansion, so 56 of CATF's 65 usages disappear
  before either the instance graph or catalog can see them.
- ❌ There is no canonical pre-expansion usage domain, non-reaching disposition, inapplicability
  mechanism, or non-circular totality gate.

**Scope**:

1. Add the complete authored-usage domain to the same instance-graph/catalog authority used by
   live and snapshot generation. Preserve exact declaration identity and form classification.
2. Project exactly one disposition per usage: executable, excluded with reason, or non-reaching
   with reason. Keep per-occurrence executable entries separate from usage-level inventory.
3. Apply severity by cause: asserted structurally unattachable is an error; asserted vacuous is a
   warning and authoring advisory; plain and out-of-scope forms are visible records.
4. Design and implement the explicit vacuous-inapplicability mechanism without adding a second
   hand-maintained inventory.
5. Add a generation-time completeness gate over the canonical authored domain and catalog
   dispositions. Mutations that remove, duplicate, or misjoin a disposition must fail.
6. Carry the authority through the instance-graph codec, snapshot path, and sealing fingerprints.
   If the schema changes, perform one reviewed final-schema fixture recapture in this item.
7. Re-grade and re-anchor REQ-EXT-09 and REQ-CL-04 against independent totality evidence.

**Out of Scope**:

- Report headline, coverage schema, TEAx projection, and policy changes, owned by Item 3.
- Executing calculation-definition-owned gates, owned by the follow-on designed in Item 6.
- A parallel manifest or catalog inventory kept in sync with the graph.

**Success Criteria**:

- [ ] **[INHERITED: spec.md]** Frozen `catf_mfe_d5` produces exactly 65 usage carriers with zero
      absence and no change to its authored constraint syntax.
- [ ] Removing or duplicating any carrier fails generation with a named, usage-identifying
      completeness diagnostic.
- [ ] An asserted structurally unattachable fixture halts; an asserted vacuous fixture produces
      the visible warning/advisory; a plain constraint with a blocked predicate still generates
      and catalogs as unassessed.
- [ ] The inapplicability mechanism is explicit, fingerprinted, and cannot silently change an
      asserted usage's coverage role.
- [ ] Live, in-place snapshot, and relocated snapshot routes produce the same authored domain and
      dispositions; old or malformed snapshot shapes fail closed under the selected version rule.
- [ ] REQ-EXT-09 and REQ-CL-04 cite non-self-referential tests that fail if a pre-expansion usage
      vanishes.
- [ ] Focused tests, full licensed codegen/companion suites, ruff zero-new, mypy zero-new, fixture
      diff review, and `git diff --check` pass with exact counts recorded.

**Estimated Effort**: 2 days (spec 1h, design 3h, plan 1h, execute and validate 11h)

**Location**: `.project/active/constraint-catalog-totality/`

**Dependencies**: Item 1.

**Required Reading**:

- `.project/active/constraint-semantics-contract/spec.md` — Pipeline invariants and report/coverage
  denominator distinction.
- `.project/research/20260812-101200_constraint-semantics-end-to-end.md` §§2–4.
- `.project/active/constraint-semantics-contract/product-lens.md` — spec-F4, spec-F7, spec-F8.
- `.project/backlog/epic_elaborate_first_architecture.md` — Item 7 single-authority and recapture
  obligations.
- `.project/active/cutover-recovery/plan.md` — paused step-4 evidence.

**Deliverables**:

- `.project/active/constraint-catalog-totality/spec.md`
- `.project/active/constraint-catalog-totality/design.md`
- `.project/active/constraint-catalog-totality/plan.md`
- Canonical authored-domain, disposition, codec, catalog, gate, and diagnostic implementation.
- Independent totality and three-route parity tests.
- `.project/active/constraint-catalog-totality/verification.md`

---

#### Cross-repo hand-off from Item 2 (not work Item 2 performs)

**TEAx must re-vendor `ACCEPTED_CATALOG_SCHEMA_VERSIONS` to include `3.0.0`, after this repo
lands.** B3 forbids TEAx importing sysml-codegen, so nothing here can enforce it. While it is
pending, **TEAx fails closed on every newly generated package** — loudly, which is the intended
direction. Do not bump TEAx first: that makes TEAx accept a schema no generator produces.

What broke for a consumer at `3.0.0`, both at once: `usage_records` widened from admitted-only to
every authored constraint usage, and every catalog row is now keyed by `declaration_id` instead of
the `(usage_qualified_name, source_local_identity)` string pair. A consumer that wanted the old,
narrower set recovers it exactly by filtering `disposition_kind == "eligible"`.

**Also landed in the companion, and already merged into this epic's paired worktrees:**
`CONSTRAINT_FACTS_SCHEMA_VERSION` moved `constraint-facts/v2` → `v3` for the new
`vacuous_asserted_gate` ADVISORY kind (agentic-mbse `bc69f04`), with codegen's
`_upstream_pins.py` moved in the same window.

### Item 3: Coverage Report and TEAx Policy (2 days)

**Type**: Code / Integration

**Boundary authority**: **[AGENT] (ratified by owner, 2026-08-12)**. Behavioral requirements are
**[INHERITED: constraint-semantics-contract/spec.md]** unless separately marked.

**Objective**: Make generated reports and TEAx study policy state exactly how much applicable
asserted feasibility was assessed.

**Current State**:

- ✅ Generated packages already emit reports for executed constraints, and TEAx normalizes report
  headlines into study-policy dispositions and durable case records.
- ⚠️ The report has no authored or excluded population, and `all_satisfied` means only that some
  result exists and none failed.
- ❌ Excluded-only models emit no report; the report and runtime vocabularies have no partial state;
  TEAx labels such packages `unconstrained`.
- ⚠️ Hand-off from Item 1 (audit M-1): four `all_satisfied` assertions in codegen
  `tests/execution/` embody the superseded any-assessed-result headline meaning and move with
  this item's vocabulary change (sweep record:
  `.project/active/constraint-semantics-contract-amendments/verification.md`).

**Scope**:

1. Derive compact report coverage from Item 2's canonical catalog: authored-usage total, assessed
   count, excluded/non-reaching counts and reason histogram, and coverage state. Keep per-usage
   detail in the catalog and preserve the fingerprint join.
2. Add the partial-coverage report headline and its canonical TEAx runtime counterpart. Extend the
   normalization seam and reject unknown or unmapped tokens.
3. Implement headline precedence over applicable asserted gates: violation, indeterminate, full
   satisfaction, partial coverage, then not assessed.
4. Generate the zero-input aggregator for constraint-bearing models with no executable assertions;
   keep genuinely constraint-free models report-free.
5. Update TEAx defaults: partial coverage keeps for boundary; feed-strategy requires an explicit,
   auditable per-study opt-in. Persist coverage accounting in durable case records.
6. Version or migrate generated schemas, package contracts, and cross-repository pins as required,
   with a specified landing order.

**Out of Scope**:

- Recomputing per-usage detail outside the catalog.
- CATF model migration and tolerance decisions, owned by Item 5.
- Calculation-definition gate execution.

**Success Criteria**:

- [ ] Fully covered satisfaction, partial coverage, violation, indeterminate, descriptive-only
      `not_assessed`, and truly unconstrained states each have an independently pinned report and
      canonical TEAx outcome.
- [ ] `all_satisfied` is impossible when any applicable asserted usage lacks assessment.
- [ ] A model containing only plain or requirement-side usages generates a zero-input
      `not_assessed` report; a zero-usage model remains report-free and maps to `unconstrained`.
- [ ] Report coverage is derived from the catalog in one direction and cannot diverge from the
      per-usage inventory without a generation or verification failure.
- [ ] Partial coverage defaults to keep-for-boundary; feed-strategy occurs only with an explicit
      config line; both paths persist coverage counts and catalog linkage.
- [ ] Unknown report and runtime headline tokens fail closed rather than falling through or raising
      an unnormalized key error.
- [ ] Cross-repository compatibility tests, codegen and TEAx full suites, ruff/mypy zero-new gates,
      generated-artifact review, and `git diff --check` pass with exact counts recorded.

**Estimated Effort**: 2 days (spec 1h, design 3h, plan 1h, execute and validate 11h)

**Location**: `.project/active/constraint-coverage-policy/`

**Dependencies**: Items 1–2.

**Required Reading**:

- `.project/active/constraint-semantics-contract/spec.md` — Report/coverage and Study policy.
- `.project/research/20260812-101200_constraint-semantics-end-to-end.md` §§2, 4–5.
- `.project/active/constraint-semantics-contract/product-lens.md` — spec-F1, spec-F2, spec-F3,
  spec-F5.
- `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md` — invariants 32,
  33, 41, 46/46a, 48, 49.
- `.project/concepts/constraint-execution-lifecycle-requirements.md` — LC-E05/E06/E10/E11/E12.

**Deliverables**:

- `.project/active/constraint-coverage-policy/spec.md`
- `.project/active/constraint-coverage-policy/design.md`
- `.project/active/constraint-coverage-policy/plan.md`
- Codegen report/template/schema and zero-input-aggregator implementation.
- TEAx normalization, policy, configuration, and durable-record implementation.
- Cross-repository state-matrix and compatibility tests.
- `.project/active/constraint-coverage-policy/verification.md`

---

### Item 4: Predicate Defect Hardening (0.5–1 day)

**Type**: Implementation

**Boundary authority**: **[AGENT] (ratified by owner, 2026-08-12)**. The must-fix disposition is
**[INHERITED: rulings-20260812.md Q8]**.

**Objective**: Remove the two reproduced predicate-boundary defects that block or obscure correct
asserted-constraint authoring.

**Current State**:

- ❌ A unit-annotated literal such as `8.55 [m]` in an asserted predicate triggers
  `SI_OCCURRENCE_MISSING` even when the literal is not a missing feature occurrence.
- ❌ The feature-chain block diagnostic repeats `feature_chain: block_feature_chain` without the
  offending reference or a usable rewrite.
- ✅ Both failures have isolated research reproductions and known neighboring positive behavior.

**Scope**:

1. Add kept failing characterizations for unit-annotated predicate literals and repeated blocked
   feature-chain references.
2. Correct literal elaboration so quantity syntax retains its value/unit semantics without being
   resolved as a feature occurrence.
3. Carry the blocked chain's written reference and location into the diagnostic and state the
   supported rewrite: bind the chain to a formal and use the formal in the predicate body.
4. Pin singular and repeated-chain diagnostics so messages remain actionable and deterministic.

**Out of Scope**:

- Admitting feature chains inside predicate bodies.
- First-class tolerance semantics for `==` or other executable-profile expansion.

**Success Criteria**:

- [ ] An asserted predicate containing a compatible unit-annotated literal elaborates without
      `SI_OCCURRENCE_MISSING`; incompatible-unit behavior remains governed by the profile.
- [ ] A blocked feature chain names the exact offending written reference and the bindings rewrite;
      a multi-chain predicate identifies each distinct offending reference deterministically.
- [ ] Existing quantity, occurrence, profile, and diagnostic tests do not regress.
- [ ] Focused companion/codegen tests, full maintained suites, ruff/mypy zero-new gates, and
      `git diff --check` pass with exact counts recorded.

**Estimated Effort**: 0.5–1 day (spec 0.5h, design 1h, plan 0.5h, execute and validate 4–6h)

**Location**: `.project/active/constraint-predicate-hardening/`

**Dependencies**: Item 1; runs in parallel with Items 2–3.

**Required Reading**:

- `.project/active/constraint-semantics-contract/spec.md` — Migration, fixtures, and defects.
- `.project/research/20260812-101200_constraint-semantics-end-to-end.md` §6.
- `.project/active/constraint-semantics-contract/rulings-20260812.md` Q4 and Q8.

**Deliverables**:

- `.project/active/constraint-predicate-hardening/spec.md`
- `.project/active/constraint-predicate-hardening/design.md`
- `.project/active/constraint-predicate-hardening/plan.md`
- Literal-elaboration and diagnostic implementation with kept regression tests.
- `.project/active/constraint-predicate-hardening/verification.md`

---

### Item 5: CATF Derivative and End-to-End Acceptance (1.5–2 days)

**Type**: Modeling / Acceptance

**Boundary authority**: **[AGENT] (ratified by owner, 2026-08-12)**. The complete disposition and
tolerance checkpoint is **[NEED carried from spec.md]** and must be decided by the owner before
this item's design.

**Objective**: Turn the richest model into a worked, auditable example of the contract and prove
that generated feasibility evidence rejects an unphysical candidate through TEAx.

**Current State**:

- ✅ `catf_mfe_model` and `catf_mfe_d5` are frozen refusal/rename witnesses, and CATF supplies a
  measured census of all 65 authored usages.
- ⚠️ Nine instance-reaching constraints express physics intent in the plain form; five
  part-definition guards are vacuous; 51 calculation-definition guards are unreachable.
- ❌ There is no all-65 intent/disposition table, owner-approved tolerance set, derivative fixture,
  or CATF rejection proof.

**Scope**:

1. Fork a new derivative from `catf_mfe_d5`. Preserve both twins' modeled sources unchanged and
   record the exact source diff and reason for every derivative change in PROVENANCE.
2. Before design, present all 65 usages to the owner: nine instance-reaching gates with intent
   class, target form, and each tolerance; five part-definition guards with typed attachment or
   explicit inapplicability; 51 calculation-definition guards with derive-instead or
   awaits-capability.
3. Add the small reusable constraint-definition library selected in design, including a band form
   such as `WithinBand`, and use bindings-only predicates where a banded cross-check is appropriate.
4. Author the derivative and capture expected catalog, report, and study outcomes from the approved
   table before running confirmation tests.
5. After Items 2–4 land, generate, seal, execute, persist, and query the derivative through the
   real TEAx route. Mutate at least one physics input across the boundary and prove rejection.
6. Correct the stale `catf_mfe_d5/PROVENANCE.md` acceptance paragraph while preserving the
   fixture's role and bytes outside that documentation change.

**Out of Scope**:

- Changing the constraint syntax of `catf_mfe_model` or `catf_mfe_d5`.
- Implementing calculation-definition gate attachment; affected usages may be explicitly marked
  `awaits-capability` under the approved table.
- Inventing tolerance values or intent classes during design or implementation.

**Success Criteria**:

- [ ] **[NEED carried from spec.md]** The owner approves a table with exactly 65 usages and no
      missing intent, target-form, attachment, inapplicability, derivation, capability, or
      tolerance disposition.
- [ ] The derivative's PROVENANCE and machine-checkable diff account for every change from
      `catf_mfe_d5`; both frozen twins retain their ratified modeled syntax and existing reversal
      relationship.
- [ ] The derivative generates exactly 65 catalog carriers and reports full feasibility coverage
      over its applicable asserted gates without counting descriptive or requirement-side usages.
- [ ] Every applicable asserted gate executes; the five part-definition and 51
      calculation-definition groups match their approved dispositions.
- [ ] At least one physically valid candidate reaches the configured satisfied path and one
      unphysical mutation reaches `reject` through generated package, TEAx normalization, policy,
      and durable case storage.
- [ ] Expected catalog/report/study outputs are saved before confirmation tests and match the
      resulting outputs without reverse-engineering edits.
- [ ] Licensed live, in-place snapshot, relocated snapshot, generation, seal, execution, and TEAx
      acceptance gates pass with exact counts and fingerprints recorded.

**Estimated Effort**: 1.5–2 days after owner checkpoint (spec 1h, design 2h, plan 1h, execute and
validate 8–12h)

**Location**: `.project/active/catf-constraint-policy-acceptance/`

**Dependencies**: Item 1 for the owner checkpoint; Items 2–4 for implementation and acceptance.

**Required Reading**:

- `.project/active/constraint-semantics-contract/spec.md` — Modeling policy, migration, and CATF
  success criterion.
- `.project/active/constraint-semantics-contract/rulings-20260812.md` Q4, Q5, Q6, Q8 and
  post-ruling refinements.
- `.project/research/20260812-101200_constraint-semantics-end-to-end.md` §§3, 5–7.
- `tests/fixtures/catf_mfe_d5/PROVENANCE.md`
- Item 1's amended authoring guidance and Items 2–3's catalog/report contracts.

**Deliverables**:

- `.project/active/catf-constraint-policy-acceptance/spec.md`
- `.project/active/catf-constraint-policy-acceptance/owner-disposition.md`
- `.project/active/catf-constraint-policy-acceptance/design.md`
- `.project/active/catf-constraint-policy-acceptance/plan.md`
- New CATF derivative fixture, PROVENANCE, reusable constraint-definition library, and expected
  outputs.
- End-to-end mutation, policy, persistence, and three-route evidence.
- `.project/active/catf-constraint-policy-acceptance/verification.md`

---

### Item 6: Calculation-Definition Gate Capability Design (1 day)

**Type**: Design / Planning

**Boundary authority**: **[AGENT] (ratified by owner, 2026-08-12)**. The one-check-per-occurrence
semantics are **[INHERITED: rulings-20260812.md Q2]**.

**Objective**: Produce an implementation-ready design for asserted constraints owned by
calculation definitions without building the capability inside this epic.

**Current State**:

- ✅ The owner-ratified ruling defines one asserted check per concrete calculation occurrence.
- ⚠️ Calculation usages and exact calculation-definition identity already exist in the instance
  graph, but constraint scope expansion has no CalculationDefinition branch.
- ❌ There is no proved attachment rule, report-volume design, or implementation backlog item for
  the 51 CATF guards in this class.

**Scope**:

1. Run a throwaway probe that attaches one calculation-definition constraint to zero, one, and
   multiple calculation occurrences using exact identities and resolved actuals. Record whether
   the current graph carries enough context.
2. Specify eligibility, attachment, polarity, formal binding, occurrence identity, diagnostic,
   catalog, snapshot, and report behavior for one check per calculation occurrence.
3. Design the capability as an extension of Item 2's canonical authored domain and occurrence
   authority. No rendered-name reconstruction, post-build fill, or second constraint inventory.
4. Define result-volume behavior: usage-level coverage, occurrence-level results, stable drill-down
   identity, and aggregation without losing failed occurrences.
5. Produce the file-level implementation plan, dependency/pin order, public acceptance tests, and
   an effort estimate for the follow-on implementation item.

**Out of Scope**:

- Production implementation, CATF conversion of the 51 guards, or report-schema changes already
  owned by Item 3.
- Requirement-side evaluation or in-predicate feature-chain support.

**Success Criteria**:

- [ ] The probe confirms exact attachment without a second authority, or records the conflicting
      premise and parks dependent design conclusions for owner-visible redesign.
- [ ] The design covers zero, one, and multiple calculation occurrences; repeated calculation
      definitions; defaults and explicit actuals; snapshot round-trip; and per-occurrence failures.
- [ ] Usage-level coverage and occurrence-level results remain distinguishable and join through
      stable exact identity.
- [ ] Unsupported or unattachable asserted definitions fail with the Item 2 cause-based severity;
      none disappear or downgrade to a plain exclusion.
- [ ] A follow-on implementation backlog item is filed with file-level scope, dependencies,
      estimates, and customer-shaped acceptance tests.
- [ ] `my-design-review` finds no unresolved owner/`[HARD]` contradiction or ownership ambiguity.

**Estimated Effort**: 1 day (probe 2h, spec 1h, design and review 4h, follow-on plan 1h)

**Location**: `.project/active/calcdef-constraint-gate-design/`

**Dependencies**: Items 1–2; can run alongside Items 3–5.

**Required Reading**:

- `.project/active/constraint-semantics-contract/spec.md` — Q2 semantics and coverage-volume open
  question.
- `.project/active/constraint-semantics-contract/rulings-20260812.md` Q2, Q3, Q5.
- `.project/research/20260812-101200_constraint-semantics-end-to-end.md` §§2–4.
- Item 2's final spec/design and canonical authored-domain representation.
- `.project/backlog/epic_elaborate_first_architecture.md` — exact-identity and no-second-authority
  constraints.

**Deliverables**:

- `.project/active/calcdef-constraint-gate-design/probes/findings.md`
- `.project/active/calcdef-constraint-gate-design/spec.md`
- `.project/active/calcdef-constraint-gate-design/design.md`
- `.project/active/calcdef-constraint-gate-design/design-review.md`
- `.project/active/calcdef-constraint-gate-design/implementation-item.md`

---

## Dependencies

**External**:

- Coordinated changes and compatible landing order in `agentic-mbse`, sysml-codegen, and TEAx.
- SysIDE-licensed live-model and snapshot verification for the final cross-route gates.
- Owner sign-off on the CATF all-65 disposition table and per-gate tolerance values before the
  CATF child item's design.

**Internal**:

- The approved umbrella spec and its resolved review, ruling, and product-lens records.
- The lifecycle contract and frozen requirements companion amended by Item 1.
- Item 2's canonical authored domain is the sole inventory source for Items 3, 5, and 6.
- ELABORATE-FIRST Item 7 narrow-correction steps 4–10 remain paused until this epic lands and its
  evidence-invalidation register is discharged.

**Item Dependency Graph**:

```text
Item 1: Contract and authoring policy
  ├─> Item 2: Canonical usage domain and catalog totality
  │     ├─> Item 3: Coverage report and TEAx policy ──┐
  │     └─> Item 6: Calc-definition capability design│
  ├─> Item 4: Predicate defect hardening ────────────┤
  └─> Item 5: Owner checkpoint ──────────────────────┤
                                                     └─> Item 5 implementation and acceptance
```

---

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| A second usage inventory recreates the authority split this work must remove | High | Design one pre-expansion authored domain inside the graph/catalog authority and derive every downstream count from it |
| The generated report and TEAx normalize different headline vocabularies | High | Amend both vocabularies and the normalization seam together; fail closed on unknown tokens |
| CATF migration invents domain tolerances or silently narrows the 65-usage denominator | High | Put the complete disposition table and owner tolerance checkpoint before the CATF child design |
| Contract changes invalidate paused Item 7 evidence or force duplicate recaptures | High | Maintain the epic-owned invalidation register and sequence reruns after the final landing |
| Snapshot schema changes force repeated 37-fixture churn | High | Item 2 decides the final representation and owns at most one final-schema recapture; downstream items consume it |
| Cross-repository schema changes land out of order | Medium | Item 3 designs the compatibility and pin sequence before implementation and validates the composed route |
| Calculation-definition design assumes occurrence context the graph does not carry | Medium | Item 6 probes one exact constraint across zero/one/many occurrences before committing to the design |

---

## Timeline

**Total Effort**: 8.5–9.5 working days over 2–3 weeks, plus owner-checkpoint turnaround

| Item | Effort | Dependencies |
|------|--------|--------------|
| Item 1: Contract and Authoring Policy | 1.5 days | None |
| Item 2: Canonical Usage Domain and Catalog Totality | 2 days | Item 1 |
| Item 3: Coverage Report and TEAx Policy | 2 days | Items 1–2 |
| Item 4: Predicate Defect Hardening | 0.5–1 day | Item 1 |
| Item 5: CATF Derivative and End-to-End Acceptance | 1.5–2 days | Item 1 for checkpoint; Items 2–4 for implementation |
| Item 6: Calculation-Definition Gate Capability Design | 1 day | Items 1–2 |

---

## Lessons Learned (Post-Completion)

*Fill in after epic is complete*

**What Went Well**:

- TBD

**What Could Improve**:

- TBD

**Surprises**:

- TBD

---

**Last Updated**: 2026-08-12
**Next Action**: Start Item 1; begin Item 5's all-65 owner checkpoint as soon as Item 1 publishes
the authoring policy.
