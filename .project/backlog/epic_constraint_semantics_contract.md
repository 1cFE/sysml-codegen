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

### Item 1: Contract and Authoring Policy (1.5 days) ✅

**Status (2026-08-13): CLOSED — implemented, audited Certify-with-residuals, archived to
`.project/completed/20260813_constraint-semantics-contract-amendments/`.** All success criteria
met at codegen `76e3ab7` / companion `dcb187b`. Nothing pushed, no `main` touched, TEAx untouched;
`pre_pr` remains with the owner. Nothing executable changed — the Python diff is comment- and
docstring-only, verified by reading.

**What Items 2–7 build against** (published by this item, unchanged by close):

- The lifecycle contract's `### Headline states and coverage truth` subsection — the
  **applicable-asserted-gate** membership test (decided on the form, not the predicate), the
  inventory-versus-feasibility split, the six states, the precedence, and the both-vocabularies
  obligation.
- **Invariant 61** (asserted vacuous gate at warning grade) with its companion mirror **LC-E13**;
  **invariant 28 + LC-E05** (the third disposition kind, non-reaching-with-reason);
  **invariant 48 + LC-G07** (embedded catalog as sole authority for coverage truth).
- **ADR-009** (`docs/architecture/modeling-assumptions.md` §9) — the decision record for the
  coverage-vocabulary change, at `[AGENT] (ratified by owner, 2026-08-12)`, quoting what invariant
  33 and LC-E11 said before.
- The equality-intent taxonomy — authority copy in the contract's supported-boundary section,
  rendered in full in agentic-mbse `docs/patterns/constraints.md` for Item 5's all-65 checkpoint.

**Both deliberate hand-offs are DISCHARGED** (recorded at close, not left open):

- The four `all_satisfied` assertions in `tests/execution/` were corrected by **Item 3**'s token
  migration to `full_satisfaction` (`.project/completed/20260813_constraint-coverage-policy/`).
- REQ-EXT-09's replacement totality proof was landed by **Item 2** —
  `tests/conformance/test_constraint_population_oracle.py` plus 42 reviewed expected-population
  files, with the REQ-EXT-09/REQ-CL-04 re-grade performed there
  (`.project/completed/20260813_constraint-catalog-totality/`). The dated "re-grade pending" pointer
  Item 1 added at `verification-matrix.md:336` has served its window.

**Audit residual M-3 dispositioned at close: the vendored-corpora aggregation is RATIFIED as
final.** The 52 companion hits in `docs/sysmlv2/` and `docs/syside/` stay aggregated into four
rows by term and corpus, each naming every file with its count and one uniform disposition; every
project-authored hit is still one row each. The aggregated class is the OMG specification, the
standard library, and generated SysIDE API docs — text this item has no authority to amend — and
the audit reproduced all five sweep terms independently. Expanding to 52 rows would add rows, not
information. The deviation from the spec's raw-hit-list wording is a recorded decision, not a gap.

**The D5-a deviation was judged sounder than the design's instruction and stands.** At companion
`claude/agents/sysml-expert.md:124` the `require constraint` example was kept inside its
`requirement def` and given a settled-semantics sentence, rather than being swapped to `assert
constraint`. Substituting would have taught invalid requirement modeling and deleted the visible
requirement-side form that ruling Q7 exists to preserve. Recorded with its reasoning before it was
taken; probe P-2 confirmed the landed wording.

**Residuals other items homed against "Item 1's authoring guidance" are NOT Item 1's** — Item 1 is
closed and has no execution vehicle. Item 3's design-F2 (Appendix C vacuous-gate cell), the D9
advisory guidance, and item3-F2 (the unreachable `BLOCK`ed-asserted-usage clause) are re-homed to
**Item 7**, whose scope item 4 executes them.

**The parked D-2 vs D-4/SRC-01 premise conflict stays parked at the umbrella level**
(`.project/active/constraint-semantics-contract/spec.md:325`) and was verified byte-untouched at
close. It needs the owner; no item may resolve it silently.

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

- [x] **[INHERITED: spec.md]** A live ADR records the intended contract change and is cited from
      the product-lens disposition trail.
- [x] **[INHERITED: spec.md]** The lifecycle contract and requirements companion publish the full
      amendment set with their original provenance intact.
- [x] **[INHERITED: research D1–D7]** Codegen and agentic-mbse contain no remaining statement that
      a plain or requirement-side constraint is an enforced gate.
- [x] **[NEED carried from spec.md]** Authoring guidance explains when equality intent should be
      derived, band-checked, one-sided, fixed as input, or closed by construction.
- [x] **[OWNER]** Documentation is correct before confirmation testing begins.
- [x] Documentation checks and `git diff --check` pass in every touched repository.

**Estimated Effort**: 1.5 days (spec 1h, design 2h, plan 1h, execute and review 8h)

**Location**: `.project/completed/20260813_constraint-semantics-contract-amendments/` (archived
2026-08-13; was `.project/active/constraint-semantics-contract-amendments/`)

**Dependencies**: None; the approved umbrella spec is the input.

**Required Reading**:

- `.project/active/constraint-semantics-contract/spec.md`
- `.project/active/constraint-semantics-contract/rulings-20260812.md`
- `.project/research/20260812-101200_constraint-semantics-end-to-end.md` §7 (D1–D7)
- `.project/active/constraint-semantics-contract/product-lens.md`
- `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md`
- `.project/concepts/constraint-execution-lifecycle-requirements.md`

**Deliverables**:

- `.project/completed/20260813_constraint-semantics-contract-amendments/spec.md`
- `.project/completed/20260813_constraint-semantics-contract-amendments/design.md`
- `.project/completed/20260813_constraint-semantics-contract-amendments/plan.md`
- Live ADR plus amended contract, requirements companion, codegen references, and agentic-mbse
  authoring guidance.
- `.project/completed/20260813_constraint-semantics-contract-amendments/verification.md`

---

### Item 2: Canonical Usage Domain and Catalog Totality (2 days) ✅

**Status (2026-08-13): CLOSED — implemented, audited Certify-with-residuals, archived to
`.project/completed/20260813_constraint-catalog-totality/`.** All success criteria met at codegen
`35ee82f` / companion `bc69f04` (65/65 carriers on frozen `catf_mfe_d5` — 9 reaching, 0 eligible,
a measured correction to the item's "9 eligible" premise; full licensed suite 1860/34/0
zero-skip). `pre_pr` remains with the owner; nothing pushed, no `main` touched. One scope note:
the vocabulary below spells the first disposition kind `executable`; the landed contract
vocabulary is `eligible` (contract governs, recorded in the item spec).

**Owner should read this before ratifying downstream items.** The item spec carries an **[AGENT]**
severity exception recorded beside an **[INHERITED]** line
(`.project/completed/20260813_constraint-catalog-totality/spec.md:184-194`): a **malformed
`@inapplicable:` directive** grades `non_reaching` / `classification_incomplete` at **`error`** and
halts by name **whatever the usage's form**, including a plain one. That overrides the inherited
"plain and out-of-scope forms are visible records and never errors" rule for this one cause. The
reasoning: a malformed marker is a defect in an instruction the author wrote *to the tool*, not a
fact about the model, and silently ignoring it would be indistinguishable from never having written
it — the absence-not-disposition failure this item exists to end. The umbrella spec is untouched and
its Q3 form-caused severity rule is unchanged. Accepted at audit (A3 / residual **R2**),
orchestrator-ratified, **not owner-ruled**.

**Traveling residuals from Item 2's audit** (`audit.md` §Residuals; none blocked certification):

- **R1 — the internal bare-`ComputationGraph` seam is seal-only.** A *resealed* removal of a
  non-reaching catalog row still passes silently there, and the reaching-case diagnostic degrades
  from usage-identifying to fingerprint-only. **No production caller reaches it**; the completeness
  guarantee is intact on both public routes (live and `--from-snapshot`). Recorded so the boundary
  is written down. **Owner:** whoever next adds a production caller to that seam — adding one
  reopens the guarantee, so the check must move with it.
- **R3 — the calc-def-only package shape has no pre-item baseline.** The A4 cure's justification
  ("matches what shipped before this item") could not be measured: within the audit window
  `catf_mfe_d5` shipped `schemas/constraint_types.py` at `ba756fb` and does not at HEAD, and no cure
  commit changed baseline bytes, so no byte gate covers the shape. It is pinned only by the two new
  generation-level tests. The change is defensible and probably right; the justification reaches
  back to a state that was not observable. **Owner:** Item 5 (CATF derivative and end-to-end
  acceptance) is the natural place to give this shape a real baseline.
- **R5 — the item's product-lens ledger has no plan-stage or implement-stage entry.** Dispositioned
  at close as a recorded process gap, not backfilled with retroactive entries
  (`20260813_constraint-catalog-totality/product-lens.md`, close block). Process observation about
  how the run was staffed; not an obligation on any later item.

**Recorded deviations from the Item 2 orchestrated run, both judged ACCEPTABLE at audit** (kept
here because they explain why the landed evidence looks the way it does):

- **The "9 eligible" premise was wrong, and the correction is the measured one.** The spec and
  research inherited "65 authored usages produce 9 carriers" reading the 9 as *eligible*. The 9 are
  **reaching** usages carrying visible dispositions; `catf_mfe_d5` has **zero** eligible
  constraints. Confirmed from `.sysml` source without the elaborator: 70 `constraint` lines minus 5
  comments = 65, all bare inline form, zero `assert`. The 65 headline is unaffected.
- **The 42 expectation files were scanner-generated, then reviewed** — the design asked for
  hand-authored, source-read files. Accepted: the load-bearing property is independence *from the
  domain*, and it holds completely (the licence-free scanner shares no code, no adapter, and no
  parse with the elaborator). The weaker property — independence between scanner and files — is
  named rather than argued away; the mitigation was a full 42-fixture scanner-vs-domain comparison
  *before* any file was written, which found and fixed two scanner bugs.

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

- [x] **[INHERITED: spec.md]** Frozen `catf_mfe_d5` produces exactly 65 usage carriers with zero
      absence and no change to its authored constraint syntax.
- [x] Removing or duplicating any carrier fails generation with a named, usage-identifying
      completeness diagnostic. *(Met on both public routes; the internal seal-only seam is residual
      R1 above.)*
- [x] An asserted structurally unattachable fixture halts; an asserted vacuous fixture produces
      the visible warning/advisory; a plain constraint with a blocked predicate still generates
      and catalogs as unassessed.
- [x] The inapplicability mechanism is explicit, fingerprinted, and cannot silently change an
      asserted usage's coverage role.
- [x] Live, in-place snapshot, and relocated snapshot routes produce the same authored domain and
      dispositions; old or malformed snapshot shapes fail closed under the selected version rule.
- [x] REQ-EXT-09 and REQ-CL-04 cite non-self-referential tests that fail if a pre-expansion usage
      vanishes.
- [x] Focused tests, full licensed codegen/companion suites, ruff zero-new, mypy zero-new, fixture
      diff review, and `git diff --check` pass with exact counts recorded.

**Estimated Effort**: 2 days (spec 1h, design 3h, plan 1h, execute and validate 11h)

**Location**: `.project/completed/20260813_constraint-catalog-totality/` (archived 2026-08-13; was
`.project/active/constraint-catalog-totality/`)

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

- `.project/completed/20260813_constraint-catalog-totality/spec.md`
- `.project/completed/20260813_constraint-catalog-totality/design.md`
- `.project/completed/20260813_constraint-catalog-totality/plan.md`
- Canonical authored-domain, disposition, codec, catalog, gate, and diagnostic implementation.
- Independent totality and three-route parity tests.
- `.project/completed/20260813_constraint-catalog-totality/verification.md`

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

### Item 3: Coverage Report and TEAx Policy (2 days) ✅

**Status (2026-08-13): CLOSED — implemented, audited Certify-with-residuals, all six residuals
cured, archived to `.project/completed/20260813_constraint-coverage-policy/`.** Audit at codegen
`cb19011` / TEAx `e0c7e48`; cures at codegen `0f6f022`/`3d32ae4` and TEAx `4101325`/`5b70ae9`,
**+29 pinning tests** (+26 TEAx, +3 codegen). All twelve spec success criteria are now verified and
marked: the three the audit left open (A-1 unknown-token fail-closed at all three runtime seams,
A-2 invariant 41 over the nested coverage block, A-3 invariant 50's `evidence_schema_version`
carrier) are each pinned by a named test in the cure addendum
(`.project/completed/20260813_constraint-coverage-policy/verification.md` §Cure addendum). Two
unearned checkboxes were corrected rather than defended: the invariant-50 carrier claim, which
cited a pre-existing test varying `strategy_config`, and Phase 6's over-ticked validation box.

**Final gates:** codegen **2050 passed / 34 skipped / zero licence-skip**, TEAx **337 / 0**, ruff
and mypy counters unchanged in both repos, `git diff --check` clean in both, **zero baseline byte
churn**, companion untouched at `5088b41`. Nothing pushed; no `main` touched anywhere. `pre_pr`
remains with the owner.

**Cross-repo state — the TEAx branch is an unmerged deliverable.** The coordinated TEAx work is
complete on branch `constraint-semantics-item3` at `5b70ae9` in `/home/reid/1cfe/teax`, four
commits off pinned `main` `fa0e06a`. It is **not merged**. Two consequences that outlive this
close:

- **The TEAx checkout must stay on `constraint-semantics-item3` until merge.** codegen's execution
  lane imports simkit from that working tree (D8's checkout inversion), so switching the branch
  breaks codegen's own suite.
- **Publication order is codegen first, TEAx second** (D8 step 4). The reverse makes TEAx accept a
  runtime contract no generator produces.

Item 2's hand-off is **discharged on that branch**: the accepted schema sets were re-vendored —
replaced, not extended — so a pre-item package fails at seal verification before any report is
read. What remains is merge sequencing, owned by `pre_pr` and the owner.

**Traveling residuals and filed corrections** (none blocked certification):

- **design-F2 [FILED — Item 1 territory]** — Appendix C's vacuous-gate cell over-permits in the
  degenerate case; it wants "…and at least one gate remains". Item 3's design D4 published a
  RULING (**not assessed**) with its reasoning against the contract, so behaviour is settled; the
  contract text is not. **Owner: re-homed to Item 7** at Item 1's close (2026-08-13) — Item 1 is
  archived at `.project/completed/20260813_constraint-semantics-contract-amendments/` and has no
  execution vehicle; Item 7's scope item 4 executes this.
- **D9 follow-on [FILED — companion territory]** — the authoring-time advisory for the
  eligible-plus-`@inapplicable:` combination belongs in `agentic-mbse` authoring guidance. D9
  refuses the combination loudly at generation time, so nothing ships wrong; the advisory would
  catch it a step earlier. **Owner: re-homed to Item 7** at Item 1's close (2026-08-13), same
  reason; Item 7's scope items 2 and 4 execute it.
- **item3-F2 [DEFERRED, surfaced not resolved]** — the inherited "a `BLOCK`ed asserted usage stays
  in the denominator" clause is unreachable under invariant 1 as amended (a `BLOCK` on an asserted
  usage halts the model, so no package and no report exist to carry it). Item 3 carried the clause
  as one row of a total map over `DISPOSITION_REASONS` — a totality claim, not a reachability
  claim — and correctly did **not** write the unbuildable "asserted + BLOCKed → partial coverage"
  fixture. **Owner: re-homed to Item 7** at Item 1's close (2026-08-13) — the ruling (dead text, or
  invariant 1 narrower than written) rides Item 7's scope-item-1 owner checkpoint. It stays a
  surfaced premise conflict in both directions until then. Do not let a later agent read the clause
  as a live requirement.
- **audit-F4 [no home available]** — this repo has no `.project/product/` index and no
  `product.sh`, so the coverage-truth promise has no product-promise entry; it exists as a concept
  subsection plus ADR-009 at `[AGENT] (ratified)`. No id was hand-minted. File a first-capture
  entry when the owner next states the promise in their own words.

**Recorded deviations from the Item 3 orchestrated run, all judged ACCEPTABLE at audit** (kept here
because they explain why the landed evidence looks the way it does):

- **PD5 was a probe-and-stop, and the orchestrator ruled replace-and-regenerate.** The design
  parked the fixture-package question rather than guessing it; the probe measured the real blast
  radius and the ruling regenerated all five committed TEAx fixture packages instead of patching
  them by hand.
- **`f1_arithmetic`'s pinned generation script was deleted, not repaired — its premise was false.**
  The script called modules the cutover recovery removed, so it could not run at any current
  revision. It was replaced by `models/toy_plant.sysml` driven through the ordinary public route,
  byte-reproducible, and the audit endorsed the swap on the merits: it removes a bespoke exemption
  rather than creating one, and case values are unchanged.
- **`sealed_package`'s model was regenerated from codegen's `wi014_toy`** (adopted, recorded in
  TEAx `GENERATION.md`).
- **The `Free_Plant → freePlant` entry-key drift is pre-existing** (`fa0e06a`→HEAD, ADR-001),
  surfaced by regeneration rather than caused by it. Accepted and annotated at every site; **not**
  an Item 3 semantic change.
- **`excluded_only` moved `not_assessed` → `partial_coverage`, and that is mandated, not widened.**
  LC-E12's owner-ratified amendment requires it: an excluded asserted gate stays in the
  denominator, so a package with one is partially covered, not unassessed.

**Lesson recorded at close:** two checkboxes in this item were ticked without the evidence they
claimed — one against a test that varied the wrong field, one over an unrun validation step. Both
were found by looking rather than by a failure, because an unearned `[x]` is exactly what stops the
next reader looking. The cure pass corrected both in place and named what they had claimed.

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
  `.project/completed/20260813_constraint-semantics-contract-amendments/verification.md`).
  **Discharged** by this item's token migration; recorded at Item 1's close (2026-08-13).

**Scope**:

1. Derive compact report coverage from Item 2's canonical catalog: authored-usage total, assessed
   count, excluded/non-reaching counts and reason histogram, and coverage state. Keep per-usage
   detail in the catalog and preserve the fingerprint join.
2. Add the partial-coverage report headline and its canonical TEAx runtime counterpart. Extend the
   normalization seam and reject unknown or unmapped tokens.
3. Implement headline precedence over applicable asserted gates: violation, indeterminate, full
   satisfaction, partial coverage, then not assessed.
4. Generate the zero-input aggregator for any model carrying at least one authored constraint
   usage; keep genuinely constraint-free (zero-usage) models report-free. **Corrected at close
   (2026-08-13, design-F3) to match the amended contract:** the trigger for the not-assessed
   headline is the absence of an *applicable asserted gate*, not the absence of executable
   assertions. An applicable gate that produced zero eligible entries reads **partial coverage**,
   not not-assessed (LC-E10). The as-built contract was always right; this wording was looser than
   it, and the item followed the contract.
5. Update TEAx defaults: partial coverage keeps for boundary; feed-strategy requires an explicit,
   auditable per-study opt-in. Persist coverage accounting in durable case records.
6. Version or migrate generated schemas, package contracts, and cross-repository pins as required,
   with a specified landing order.

**Out of Scope**:

- Recomputing per-usage detail outside the catalog.
- CATF model migration and tolerance decisions, owned by Item 5.
- Calculation-definition gate execution.

**Success Criteria**:

- [x] Fully covered satisfaction, partial coverage, violation, indeterminate, descriptive-only
      `not_assessed`, and truly unconstrained states each have an independently pinned report and
      canonical TEAx outcome.
- [x] `all_satisfied` is impossible when any applicable asserted usage lacks assessment.
- [x] A model containing only plain or requirement-side usages generates a zero-input
      `not_assessed` report; a zero-usage model remains report-free and maps to `unconstrained`.
- [x] Report coverage is derived from the catalog in one direction and cannot diverge from the
      per-usage inventory without a generation or verification failure.
- [x] Partial coverage defaults to keep-for-boundary; feed-strategy occurs only with an explicit
      config line; both paths persist coverage counts and catalog linkage.
- [x] Unknown report and runtime headline tokens fail closed rather than falling through or raising
      an unnormalized key error. *(Met at implementation, pinned by the cure pass: all three runtime
      seams refuse by name against the retired token and an invented one —
      `simkit/tests/evaluation/test_headline_vocabulary.py`, 15 cases.)*
- [x] Cross-repository compatibility tests, codegen and TEAx full suites, ruff/mypy zero-new gates,
      generated-artifact review, and `git diff --check` pass with exact counts recorded.

**Estimated Effort**: 2 days (spec 1h, design 3h, plan 1h, execute and validate 11h)

**Location**: `.project/completed/20260813_constraint-coverage-policy/` (archived 2026-08-13; was
`.project/active/constraint-coverage-policy/`)

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

- `.project/completed/20260813_constraint-coverage-policy/spec.md`
- `.project/completed/20260813_constraint-coverage-policy/design.md` (rev 2)
- `.project/completed/20260813_constraint-coverage-policy/plan.md`
- Codegen report/template/schema and zero-input-aggregator implementation.
- TEAx normalization, policy, configuration, and durable-record implementation.
- Cross-repository state-matrix and compatibility tests.
- `.project/completed/20260813_constraint-coverage-policy/verification.md` (+ cure addendum)
- `.project/completed/20260813_constraint-coverage-policy/expected-coverage.md` — the 13-entry
  expected-account ledger, hand-derived from `.sysml` source before the code existed.
- **TEAx branch `constraint-semantics-item3` at `5b70ae9`** (`/home/reid/1cfe/teax`) — complete,
  **unmerged**, four commits off pinned `main` `fa0e06a`.

---

### Item 4: Predicate Defect Hardening (0.5–1 day) ✅

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

- [x] An asserted predicate containing a compatible unit-annotated literal elaborates without
      `SI_OCCURRENCE_MISSING`; incompatible-unit behavior remains governed by the profile.
- [x] A blocked feature chain names the exact offending written reference and the bindings rewrite;
      a multi-chain predicate identifies each distinct offending reference deterministically.
- [x] Existing quantity, occurrence, profile, and diagnostic tests do not regress.
      *(Audit addendum R1, 2026-08-13: 2010 passed / 34 skipped / 0 failed, zero license skips —
      no longer author-reported.)*
- [x] Focused companion/codegen tests, full maintained suites, ruff/mypy zero-new gates, and
      `git diff --check` pass with exact counts recorded.
      *(Audit addendum R2/R3: codegen ruff 12 / mypy 55; companion baseline established at
      `bc69f04` directly — ruff 1, mypy 108, failing node IDs byte-identical to tip, so zero-new
      holds on membership and not only on count.)*

**Audit (2026-08-13): Certify-with-residuals** — `.project/completed/20260813_constraint-predicate-hardening/audit.md`,
including the orchestrator addendum (probes R1–R7 all PASS). Both blocking residuals are
**discharged**: the two surfaced findings are carried into Item 5's Current State and Required
Reading below (audit F7), and the rewritten red-first assertion is deviation 8 in
`verification.md`, with R5's measurement showing it conceals no edge (audit F1, not promoted).
The record-and-decide residuals F2–F4 and F6 are cured in the same pass; F5 is resolved by
owner decision **[OWNER 2026-08-13]**: the coverage ledger moved to
`tests/unit/data/expected-coverage.md` (bytes unchanged, pointer stub at the archived path),
so suite collection no longer depends on archive layout.

**Estimated Effort**: 0.5–1 day (spec 0.5h, design 1h, plan 0.5h, execute and validate 4–6h)

**Location**: `.project/completed/20260813_constraint-predicate-hardening/`

**Dependencies**: Item 1; runs in parallel with Items 2–3.

**Required Reading**:

- `.project/active/constraint-semantics-contract/spec.md` — Migration, fixtures, and defects.
- `.project/research/20260812-101200_constraint-semantics-end-to-end.md` §6.
- `.project/active/constraint-semantics-contract/rulings-20260812.md` Q4 and Q8.

**Deliverables**:

- `.project/completed/20260813_constraint-predicate-hardening/spec.md`
- `.project/completed/20260813_constraint-predicate-hardening/design.md`
- `.project/completed/20260813_constraint-predicate-hardening/plan.md`
- Literal-elaboration and diagnostic implementation with kept regression tests.
- `.project/completed/20260813_constraint-predicate-hardening/verification.md`

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
- ⚠️ **A unit written on a constraint *binding* is dimensionally inert to the executable profile.**
  `in tol = 0.05 [m];` carries its unit for a human reader and not for the gate: a bound formal
  takes its operand category from the definition's declared type (`Real` → category `real`), so
  the binding's annotation never reaches `classify_ordering`. Measured, not inferred — a probe
  binding a length against a time (`in measured = width [m]; in tol = 0.05 [s];`) is **admitted**.
  True before and after Item 4, which neither widened nor narrowed the profile. **Consequence for
  this item:** the band recipe in scope item 3 is exactly this shape, so a mis-united tolerance
  band is admitted silently by a gate whose purpose is catching wrong physics. The all-65 table
  cannot rely on the profile to catch unit mistakes in bindings; a wrong unit there has to be
  caught by review or by an explicit in-predicate comparison.
  *(Item 4 probe P3; `.project/completed/20260813_constraint-predicate-hardening/verification.md` "Surfaced",
  `reason-codes-reconciliation.md`.)*
- ⚠️ **A blocked chain's location is the constraint usage's line, not the offending term's.** The
  `LocationFact` the companion attaches to a decision belongs to the usage; the payload has no
  per-node location, so every entry of a multi-chain block renders the same `file:line`. What
  disambiguates within a predicate is the named reference, which `block_feature_chain` now
  carries. **Consequence for this item:** on a long predicate the diagnostic points at the gate,
  not at the term — read the chain name, not the line, when driving the 65 rewrites.
  *(`.project/completed/20260813_constraint-predicate-hardening/reason-codes-reconciliation.md` "Also
  surfaced".)*

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
- **Item 4's two surfaced limits**, both summarized in Current State above with their measurements:
  `.project/completed/20260813_constraint-predicate-hardening/verification.md` ("Surfaced") and
  `reason-codes-reconciliation.md` ("Also surfaced"). Read them before fixing the tolerance-band
  form — the first one decides how much the profile can be trusted to check a band.
- `docs/architecture/modeling-assumptions.md` §8, "Authoring a gate that carries units" — the one
  supported spelling for a unit-carrying comparison, which the 65 rewrites will need.

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
- ✅ **[AGENT — executable spike evidence, 2026-08-13]** Exact attachment is feasible inside the
  canonical elaborator: match the constraint owner's `DeclarationId` to
  `CalcNode.calculation_definition_id`, and identify each result by the constraint usage ID plus
  the full calculation `NodeId`. The zero/one/two-occurrence probe recovered resolved attribute,
  literal, and modeled-default inputs without name lookup. It also proved scope alone collides for
  two sibling uses of one definition, so the concrete constraint identity must carry the
  calculation node and attachment must precede serialization. See
  `.project/active/calcdef-constraint-gate-design/probes/findings.md`.
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

### Item 7: ADR, Product Promise, and Agent-Facing Documentation Sync (0.5–1 day)

**Type**: Documentation / Contract

**Boundary authority**: **[OWNER 2026-08-13]** "the ADR + documentation is critical. Including:
cross-repo, agent prompts." Item slicing and scope below are **[AGENT]** (filed same day at the
owner's direction).

**Objective**: Give the landed constraint-semantics contract its durable decision record and
propagate the landed concrete semantics into every surface humans and agents read — cross-repo
documentation and agent prompts/skills — so the next authoring session teaches the new policy
instead of the superseded one.

**Current State** (verified 2026-08-13, post Items 1–3):

- ✅ Item 1 landed the contract-level docs: ADR-009, contract amendments, D1–D7 corrections,
  the equality-intent taxonomy in agentic-mbse `docs/patterns/constraints.md`.
- ✅ Items 2–3 corrected every doc their changes falsified (modeling-assumptions pointers,
  REQ-EXT-09/REQ-CL-04 rows, docs 28/30, four TEAx-side stale sites).
- ❌ No product-promise/ADR home exists for the coverage-truth promise (Item 3 audit-F4); the
  repo has no `.project/product/` ledger and no ADR registry beyond modeling-assumptions.md
  sections. Filing one needs an owner-originated promise statement.
- ❌ agentic-mbse `docs/patterns/constraints.md` has zero mention of `@inapplicable:` authoring
  or the eligible+inapplicable contradiction refusal; TEAx docs have zero mention of
  `partial_coverage`/`full_satisfaction`, the keep-for-boundary default, or the feed-strategy
  opt-in config; nothing documents the disposition vocabulary or carrier concepts as shipped.
- ❌ Agent prompts are stale against the policy: the codegen `sysml-conventions` skill's
  constraint example (`SKILL.md:136`) is an inline assert with a unit literal — the shape the
  blessed bindings-only pattern supersedes; no CLAUDE.md or expert-agent reference teaches the
  new authoring rules.
- ❌ Two Item 3 close residuals were homed to "Item 1's companion-side authoring guidance,"
  which has no future execution vehicle — they re-home here.

**Scope**:

1. **Owner checkpoint (first):** capture the owner-originated coverage-truth product-promise
   statement; decide the promise/ADR home (`.project/product/` first-capture ledger per the
   global convention, plus per-repo ADR convention) and file it with correct provenance.
   Includes the owner disposition for the parked item3-F2 premise conflict (the unreachable
   BLOCK clause) if the owner chooses to rule it here.
2. **Cross-repo doc sweep for the landed surfaces:** `@inapplicable:` authoring, the
   eligible+inapplicable refusal, and the D9 advisory guidance → agentic-mbse
   `docs/patterns/constraints.md`; disposition vocabulary, carriers, totality gate, severity
   by cause → codegen reference docs; six states, coverage block, policy defaults, opt-in
   config, durable-record fields → TEAx docs.
3. **Agent prompts and skills:** update the `sysml-conventions` skill (bindings-only blessed
   pattern, equality-intent taxonomy pointer, `@inapplicable:` usage, corrected example);
   sweep CLAUDE.md in all three repos and the expert-agent definitions for superseded
   constraint teaching; verify agent-facing examples elaborate cleanly under the current
   profile.
4. **Re-home the close-time orphans:** design-F2's Appendix C cell and the D9 advisory
   guidance obligations move from "Item 1" to this item and are executed here.

**Out of Scope**:

- Any code, fixture, or schema change; the derivative fixture docs (Item 5 owns its
  PROVENANCE and worked example).
- Re-litigating the contract; this item documents what landed.

**Success Criteria**:

- [ ] **[OWNER]** The coverage-truth promise is owner-stated, filed in a named home, and cited
      from the product-lens trail (closes Item 3 audit-F4).
- [ ] No shipped doc, skill, or agent prompt in the three repos teaches the superseded
      constraint semantics; the sweep record lists every hit and disposition (Item 1's
      three-sweep method).
- [ ] `@inapplicable:`, the disposition vocabulary, the six states, and the TEAx opt-in are
      documented where their users (human and agent) will find them.
- [ ] Documentation checks and `git diff --check` pass in every touched repository.

**Estimated Effort**: 0.5–1 day (owner checkpoint 0.5h, sweep + edits 3–5h, verification 1h)

**Location**: `.project/active/constraint-docs-agent-sync/`

**Dependencies**: Items 4–6, 8, and 9 landed (documents the final state — Item 8 changes the
unit-on-binding behavior `modeling-assumptions.md` §8 currently documents, and Item 9 changes
the derivative this item's worked-example references describe); before epic close/pre_pr.
(Edges amended 2026-08-13 when Items 8–9 were filed; numbering deliberately unchanged — item
numbers are already cited by close records and rulings.)

---

### Item 8: Unit-Lane Port Metadata Defect (0.5–1 day)

**Type**: Implementation (defect fix)

**Boundary authority**: **[AGENT] (ratified by owner, 2026-08-13)** — filed under the Item 5
D-S1/D-S2 ruling (option 3). Scope content below is owner-directed in that ruling.

**Objective**: Make constraint-formal and computed-design-attribute entry-point ports carry the
same unit lane calc-usage bindings already carry, so a design attribute reached by a calc and a
constraint (or a derivation) no longer refuses the model.

**Current State** (measured by Item 5 design probes P3/P3b/P4a/P5, verified in code):

- ❌ `elaborate.py:1679-1689` mints port unit metadata only for `CalcNode` consumers; constraint
  formals and computed-attribute expressions carry `unit=None` by construction.
- ❌ Projection refuses the whole model at `project.py:394-397` (`SI_RENDERING_COLLISION`) when
  the same attribute is also a unit-carrying calc entry point. Measured blast radius on CATF:
  A9's assert-band and 26 of 27 radial-build radius derivations.
- ✅ The trap's shape is recorded: correct modeling plus correct policy, refused by the
  toolchain. Item 5 landed around it with A5/A6/A9 `blocked-by-defect` (held intent).

**Scope** (owner-directed at the D-S1/D-S2 ruling):

1. Probe-characterized fix with kept failing characterizations first.
2. Its own tests (constraint-formal lane, computed-attribute lane, agreement/disagreement cases).
3. Fingerprint/churn assessment: whether minted units move on existing fixtures — and the
   one-reviewed-recapture obligation if they do (Item 2 precedent: one recapture at final schema).
4. **Item 6 is a named consumer**: constraint formals are the seam its calc-def gate capability
   binds on, so this item's characterization feeds that design.

**Success Criteria**:

- [ ] The two kept characterizations (A9 shape, radius-derivation shape) flip from REFUSE to
      ADMIT with correct unit text on the minted ports.
- [ ] No existing fixture's behavior changes silently: churn assessed, recapture (if any)
      reviewed once, byte gates re-baselined knowingly.
- [ ] Live, in-place snapshot, and relocated snapshot routes mint identical port unit metadata
      (three-route parity — minted units travel in the v3 graph).
- [ ] Item 6's design cites this item's characterization of the constraint-formal unit lane.
- [ ] Focused tests, full licensed suite, ruff zero-new, mypy zero-new, and `git diff --check`
      pass with exact counts recorded in `verification.md`.

**Estimated Effort**: 0.5–1 day, **plus** the one reviewed fixture recapture if the churn
assessment shows minted units move on existing fixtures (Item 2 precedent: 21 fixtures).

**Location**: `.project/active/unit-lane-port-metadata/` (to be created)

**Dependencies**: Item 5's probe evidence (landed). Runs independently; Item 9 consumes it;
Item 7's documentation sweep depends on it (this item changes the behavior
`modeling-assumptions.md` §8 documents).

---

### Item 9: Derivative Upgrade Under Held Intent (0.5 day)

**Type**: Modeling (follow-on)

**Boundary authority**: **[AGENT] (ratified by owner, 2026-08-13)** — filed under the Item 5
D-S1/D-S2 ruling (option 3). The target forms are already ruled; no new dispositions.

**Objective**: Once Item 8 lands, upgrade `catf_mfe_gated` under the already-ruled rows: derive
the 26 blocked radii per the ruled A5/A6 basis (axis root radius + 14 thicknesses free), assert
A9's `ProductWithinBand` at the ruled 1% relative tolerance, delete the A5/A6 usages per their
ruled intent, and restate the accounting identity to `65 = 56 carriers + 9 named deletions`
(mechanical consequence of executing the held rulings — no re-disposition).

**Success Criteria**:

- [ ] Three executing gates (A2, A3, A9); the `blocked-by-defect` markings retired from table
      and PROVENANCE; expected outputs re-derived from the table before confirmation tests
      (same SC-6 discipline as Item 5).
- [ ] Integrity manifest re-proves the restated identity; frozen twins untouched.
- [ ] Retire the B1–B5 PROVENANCE workaround — author the five `@inapplicable:` markers — when
      the marker-read gap closes (backlog `[INLINE-PREDICATE-MARKER-DROP]`).

**Location**: follows Item 5's item home conventions (new item folder at execution time)

**Dependencies**: Items 5 and 8.

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
                                                           ├─> Item 8: Unit-lane defect fix
                                                           │     └─> Item 9: Derivative upgrade
                                                           └─────────────┐
Items 4–6, 8, 9 ──> Item 7: ADR + docs + agent-prompt sync ──> epic close/pre_pr
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

**Total Effort**: 10–12 working days over 2–3 weeks, plus owner-checkpoint turnaround
(Item 7 added 2026-08-13 at owner direction; Items 8–9 filed 2026-08-13 under the D-S1/D-S2
ruling; Item 8 may add one reviewed fixture recapture if churn fires)

| Item | Effort | Dependencies |
|------|--------|--------------|
| Item 1: Contract and Authoring Policy | 1.5 days | None |
| Item 2: Canonical Usage Domain and Catalog Totality | 2 days | Item 1 |
| Item 3: Coverage Report and TEAx Policy | 2 days | Items 1–2 |
| Item 4: Predicate Defect Hardening | 0.5–1 day | Item 1 |
| Item 5: CATF Derivative and End-to-End Acceptance | 1.5–2 days | Item 1 for checkpoint; Items 2–4 for implementation |
| Item 6: Calculation-Definition Gate Capability Design | 1 day | Items 1–2 |
| Item 7: ADR, Product Promise, and Agent-Facing Documentation Sync | 0.5–1 day | Items 4–6, 8, 9 landed; before epic close/pre_pr |
| Item 8: Unit-Lane Port Metadata Defect | 0.5–1 day (+recapture if churn fires) | Item 5 probe evidence (filed 2026-08-13, D-S1/D-S2 ruling) |
| Item 9: Derivative Upgrade Under Held Intent | 0.5 day | Items 5 and 8 |

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
**Next Action**: Item 1 is CLOSED (2026-08-13) alongside Items 2 and 3, so the authoring policy is
published and Item 5's all-65 owner checkpoint is unblocked. Next: Item 5's owner checkpoint and
Item 6's design; Item 7 runs last, before epic close/pre_pr.
