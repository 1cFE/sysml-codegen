# Spec: Coverage Report and TEAx Policy (CONSTRAINT-SEMANTICS Item 3)

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-08-12
**Complexity:** HIGH
**Branch:** `item7-rebuild` (codegen worktree `/home/reid/1cfe/sysml-codegen-item7-rebuild`);
coordinated change in TEAx (`/home/reid/1cfe/teax`, on a branch off pinned `main` `fa0e06a`)

---

## Problem

A generated package can today report `all_satisfied` while most of the model's authored
feasibility checks were never assessed, and TEAx can label such a package `unconstrained` — the
same disposition a genuinely constraint-free model gets. The design search therefore cannot tell
"this candidate passed its physics gates" from "nobody checked."

The mechanics, reproduced twice on 2026-08-12
(`.project/research/20260812-101200_constraint-semantics-end-to-end.md` §§2, 4–5):

- **The headline is a not-failed claim, not a coverage claim.** `report_aggregator.py.jinja2:44-49`
  reads violation → indeterminate → `all_satisfied` (any non-empty result list) → `not_assessed`.
  It never consults exclusions. `ConstraintReport`
  (`src/sysml_codegen/templates/constraint_types.py.jinja2:24-29`) carries only
  `catalog_fingerprint`, `assessed_count`, `headline`, `results` — no authored population, no
  excluded counts, no coverage state. Two-of-nine assessed reads `all_satisfied`.
- **There is no state between "all good" and "nothing assessed."** Neither vocabulary has a
  partial-coverage value, so partial assessment has nowhere truthful to land.
- **An excluded-only model emits no report at all.** `project.py:893-894` returns before minting
  the aggregator when no constraint produced an executable module, so a constraint-bearing model
  with nothing eligible generates no aggregator — even though the template already supports the
  zero-input shape and contract invariant 32 requires it.
- **TEAx then reads the silence as freedom.** A package with no headline maps to `unconstrained`
  (`packages/teax-simkit/simkit/study/policy.py:65-68, 112-116`, as recorded in the research),
  which is the deliberate contract-46a state for constraint-free models. A CATF-shaped model with
  65 authored, unassessed checks is indistinguishable from a model with none.

Items 1 and 2 have already moved the authority this item needs. Item 1 fixed what each state
*means* (lifecycle contract, "Headline states and coverage truth"; ADR-009; invariants 32, 33,
46/46a, 48, 61; LC-E05/E06/E10/E11/E12/E13) and explicitly left the concrete token spellings,
report schema, and normalization-seam code to this item. Item 2 made the embedded catalog own the
complete authored-usage domain at schema `3.0.0`, with the per-usage fields the feasibility
denominator needs (`declaration_id`, `source_form`, `disposition.kind`/`.severity`,
`inapplicability`, `occurrence_count`). What is missing is the consumer of that authority: a
report whose coverage is derived from the catalog, a vocabulary that can say "partial", and a
study policy that reacts to each state.

The governing obligation carries owner grade at its root:

> **[OWNER-VERBATIM]** (2026-08-12, umbrella spec Problem) "when we started this whole cleanup, it
> was while defining a policy around how to use constraints to enforce things like physics in a way
> that make our overall 'design search' viable"

and the rule that follows from it is **[INHERITED: constraint-semantics-contract/spec.md]** — no
report or study label may claim more coverage than was assessed.

## Success Criteria

Carried from the epic's Item 3 section, all **[INHERITED: epic_constraint_semantics_contract.md
Item 3]** unless marked.

- [ ] Each of the six states — fully-covered satisfaction, partial coverage, violation,
      indeterminate, descriptive-only not-assessed, and truly unconstrained — has an independently
      pinned report outcome **and** an independently pinned canonical TEAx outcome. The matrix is
      five report headline values (the sixth state is report-absent by construction) and six runtime
      dispositions, each pinned by a test that no other state satisfies.
- [ ] **[AGENT] (orchestrator-ratified, 2026-08-12)** The coverage accounting survives a headline
      that outranks it: a report whose headline is `violation` still states how much of the
      applicable asserted population was assessed, and those numbers reach the durable case record.
      Proven on a model with one violated gate and at least one unassessed applicable asserted gate —
      the report reads `violation` **and** carries a non-full coverage account.
- [ ] The full-satisfaction headline is impossible when any applicable asserted usage lacks
      assessment — proven on a model where some, not all, applicable asserted gates are assessed
      and all assessed ones pass.
- [ ] A model containing only plain or requirement-side usages generates a zero-input not-assessed
      report; a model with zero constraint usages remains report-free and maps to `unconstrained`.
- [ ] **[INHERITED: contract Appendix C "Excluded-only usages" / "Asserted vacuous gate"; LC-E12]**
      A model whose applicable asserted gates all produced zero eligible concrete entries also
      generates the zero-input aggregator, and its report reads **partial coverage** — pinned
      separately from the descriptive-only not-assessed case, since the two share a shape and differ
      in headline.
- [ ] Report coverage is derived from the catalog in one direction and cannot diverge from the
      per-usage inventory without a generation-time or verification-time failure — proven by a
      negative test that perturbs one side and observes the refusal.
- [ ] Partial coverage defaults to keep-for-boundary — the conservative disposition: the candidate
      is retained to inform the feasible boundary, but its results are **not** fed back to steer the
      search. Feeding a partially-covered candidate to the search strategy (feed-strategy, the
      permissive disposition, and what a fully-covered satisfied candidate gets today) happens only
      with an explicit config line. Both paths persist coverage counts and catalog linkage in
      durable case records.
- [ ] **[INFERRED]** (review L3-3a) The new nested coverage block is proven unmutable from
      downstream code, to the same standard invariant 41 sets for the rest of the report.
- [ ] Unknown or unmapped report and runtime headline tokens fail closed with a named error — no
      fallthrough to a satisfied or unconstrained reading, no unnormalized `KeyError`.
- [ ] **[INHERITED: invariant 50]** (review L3-3b) The durable-store transition is proven, not
      assumed: either an equivalence proof over old and new artifacts, or an archived old store with
      a new lineage begun. No stored record is rebound to a new identity silently.
- [ ] Cross-repository compatibility tests pass, codegen and TEAx full suites pass, ruff/mypy are
      zero-new against baseline, generated artifacts are reviewed, and `git diff --check` is clean —
      with exact counts recorded in `verification.md`.
- [ ] **[INHERITED: constraint-semantics-contract-amendments/audit.md M-1]** The four
      `all_satisfied` assertions in codegen `tests/execution/` are moved to the new vocabulary and
      each now asserts a coverage claim rather than a not-failed one. Three
      (`test_constraint_verdicts_exact_route.py:171,416,540`) are bare headline asserts. The fourth
      (`test_fusion_tea_real_teax.py:244-259`) is a **whole-dump equality** on the real-TEAx route —
      its own docstring says a new report field "has to be accounted for here before this passes" —
      so moving it means hand-writing the expected coverage block for that route, from the settled
      semantics, before the test is run. That is the Sequencing `[NEED]` in action, not a token
      swap.

## Known Requirements

Provenance note: behavioral requirements below are **[INHERITED]** from the umbrella contract
(`.project/active/constraint-semantics-contract/spec.md`, its Q5/Q6 rulings and spec-review
resolutions L1-1/L2-1/L2-2) and from Item 1's landed definitions home (the lifecycle contract and
its frozen requirements companion). The umbrella's rulings are agent-grade, owner-ratified
2026-08-12, and challengeable only by re-deriving against their recorded reasoning — not by an
implementing agent's preference. Items marked **[INFERRED]** are this spec's own reading of what
those obligations force here. Items marked **[AGENT] (orchestrator-ratified, 2026-08-12)** are the
review's judgment calls:
they were settled during the spec review because leaving them open would have handed design a coin
flip, and they derive from the recorded rulings rather than restating one — so they are agent-grade
and challengeable by re-deriving against those rulings, not settled.

### What the report must say

- **[INHERITED: lifecycle contract, "Headline states and coverage truth"; invariant 33; LC-E11]**
  The headline states are violation, indeterminate, full satisfaction, partial coverage, and not
  assessed, with report-absent (`unconstrained`) as the sixth state by construction. Precedence is
  violation → indeterminate → full satisfaction → partial coverage → not assessed. Full
  satisfaction is a coverage claim — every applicable asserted gate assessed and passed — not the
  absence of a failure.
- **[AGENT] (orchestrator-ratified, 2026-08-12)** **Coverage is a second axis, not a slot in the
  headline.** The two published obligations pull apart unless this is said out loud: precedence
  makes the headline a single summary token, so a model with one violated gate and sixty unassessed
  ones reads `violation` and its coverage gap would vanish; but the compact-accounting requirement
  and Q6's "coverage numbers land in durable case records **regardless**" both describe a coverage
  fact that exists independently. The ruling: the **headline** is the one precedence-ordered summary
  token, and the **coverage account** is an orthogonal embedded fact that is always present and
  always reaches the case record, whatever the headline says. The partial-coverage headline value is
  the *summary projection* of the coverage axis, emitted when nothing above it in precedence fires —
  it is not the only place coverage is visible. Concretely: TEAx can tell "rejected on physics,
  fully covered" from "rejected on physics, and sixty gates were never checked." Derived from the
  recorded rulings (Q5 compact accounting + Q6 "regardless") rather than restating one of them, so
  it is agent-grade and challengeable by re-deriving against them.
- **[INHERITED: contract, same subsection; umbrella Q5 / spec-review L2-1]** The feasibility
  denominator is applicable asserted gates only, and **the test is on the form, not the
  predicate**: an asserted usage whose predicate is `BLOCK`ed or classified `NON_NUMERICAL` stays in
  the denominator as an unassessed gate. Plain and requirement-side usages are never applicable
  asserted gates; a model whose only constraints are descriptive reads not-assessed, never partial.
- **[INFERRED]** The `BLOCK` half of that clause is testable only where the usage reaches no
  instance. `SI_CONSTRAINT_BLOCKED` is raised at `elaborate.py:1103`, inside the `for scope in
  scopes:` loop that opens at `:1083` (cite corrected 2026-08-12, review L1-1), so an
  asserted `BLOCK`ed usage that *does* expand halts the whole model (invariant 1) and never produces
  a report, while one that expands to nothing catalogs `non_reaching` and stays in the denominator
  (Item 2 design, "A non-reaching BLOCK usage emits no halt"). A fixture for "asserted + `BLOCK`ed
  predicate + reaches an instance → partial coverage" cannot be generated; design pins the
  `NON_NUMERICAL` and non-reaching cases instead.
- **[INHERITED: spec-review L2-2; invariant 61; LC-E13]** A vacuous asserted gate — owner with zero
  occurrences — counts as missing assessment and holds the model at partial coverage until it
  carries an explicit inapplicability disposition, at which point it leaves the denominator. Item 2
  landed the mechanism (`inapplicability` on the usage record); this item consumes its coverage
  consequence by reading `inapplicability is not None`.
- **[INHERITED: umbrella Q5; LC-E06]** The report embeds *compact* coverage accounting —
  authored-usage total, assessed count, excluded and non-reaching counts with a reason histogram,
  and the coverage state. Per-usage exclusion detail stays in the catalog (invariant 48), joined by
  the catalog fingerprint the report already carries. LC-E06 is the obligation the excluded and
  non-reaching counts discharge: those usages "never masquerade as executed constraints **or vanish
  from coverage**."
- **[INHERITED: umbrella Q5]** Two-tier accounting: coverage counts authored **usages**; the
  results list carries concrete **occurrences**. The two tiers relate through `occurrence_count`
  and are never conflated in one number.
- **[INFERRED]** (from the two-tier rule; review L3-2) **The tiers must be distinct in the field
  names, not only in the prose.** `ConstraintReport.assessed_count` today is `len(results)` — an
  occurrence-tier count. The compact block's assessed count is usage-tier. So the new usage-tier
  count carries a new, distinct field name; the existing occurrence-tier field keeps its meaning or
  is renamed with the schema bump this item already pays. Exact spellings are design's; shipping two
  fields that both read `assessed_count`, or one field serving both tiers, is not.
- **[INHERITED: invariant 48; product-lens spec-F5]** Coverage truth is derived from the embedded
  catalog in one direction. The report is never a second inventory kept in agreement by hand, and
  a divergence between the two is a generation or verification failure, not a tolerated skew.
- **[INHERITED: invariants 32 and 46; LC-E10/E12; contract Appendix C]** **A report is required
  whenever the model authors any constraint usage at all.** Stated positively because it has two
  zero-input branches and the epic text names only one: a constraint-bearing model with no
  applicable asserted gate gets the zero-input aggregator and a *not-assessed* report, and a model
  whose applicable asserted gates all produced zero eligible concrete entries gets the same
  zero-input aggregator with a *partial-coverage* report. A model with no constraint usages remains
  inert — no aggregator, no catalog, no constraint modules (LC-E12 byte stability). The file-backed
  persist/harvest route carries the coverage accounting through unchanged, with no consumer-side
  schema adapter.
- **[INHERITED: invariant 32; LC-E10]** The aggregator is structurally retained as an exit ancestor
  whenever a report is required. This is the load-bearing half for the zero-input case: a node with
  no inputs is exactly what ordinary reachability pruning drops, so "generate it" without "retain
  it" is half the obligation.
- **[INFERRED]** The zero-input aggregator changes which packages must ship constraint machinery,
  so Item 2's `ships_constraint_machinery` rule (`resolution/models.py:598-654`: machinery ships iff
  at least one concrete entry exists) is superseded here — deliberately, as its docstring records.
  The replacement is the report-required trigger above: any authored constraint usage.
- **[INHERITED: Item 2 audit cure A4]** The rule stays in one place, so the three generation seams
  that read it cannot drift apart again. This is Item 2's landed constraint (`constraint_catalog is
  not None` had already meant three different things across those seams, which is why A4 collapsed
  them into one rule); superseding what the rule *says* does not reopen where it *lives*.

### What both vocabularies must do

- **[HARD]** (existing interface, umbrella spec-review L1-1) Two headline vocabularies exist and are
  bridged by a normalization seam: the generated report emits report tokens
  (`constraint_types.py.jinja2:28`) and TEAx projection maps them to the canonical runtime tokens
  policy dispatches on (`evaluation/projection.py` `CANONICAL_HEADLINE`, `study/policy.py`). The new
  partial-coverage state must be defined in **both** vocabularies with a counterpart across the
  seam. A state defined on one side only is a defect.
- **[INHERITED: invariant 46a]** An unknown or unmapped headline value fails closed with a named
  error. Never a `KeyError`, never a fallthrough to a satisfied or unconstrained reading. This
  applies to the report side and the runtime side alike.

### What the study must do

- **[INHERITED: umbrella Q6]** Default dispositions on the canonical vocabulary: violated → reject;
  indeterminate → keep-for-boundary; not-assessed → keep-for-boundary; **partial coverage →
  keep-for-boundary**; fully-covered satisfaction → feed-strategy/penalize as today; `unconstrained`
  unchanged and now honest by construction.
- **[INHERITED: umbrella Q6]** A study may configure partial coverage → feed-strategy, and only
  through an explicit, auditable per-study config line. Coverage numbers and catalog linkage land in
  durable case records on both paths, opt-in or not.
- **[INHERITED: invariants 41 and 49]** Policy consumes evidence read-only. It cannot mutate status,
  margin, observations, identity, or catalog linkage.
- **[INFERRED]** (from invariant 41's enforcement clause, which the contract records as currently
  violated by nested models) The new nested coverage block is frozen or defensively isolated to the
  same standard as the rest of the report. This item does not inherit the pre-existing nested-model
  violation into its own new fields; fixing that pre-existing violation elsewhere is out of scope.
- **[INHERITED: invariant 50; LC-G07A]** Existing durable study stores were written against catalog
  `2.x` and a report with no coverage block. Crossing that boundary takes one of invariant 50's two
  routes — a migration that proves old and new artifact equivalence, or the old store archived as
  lineage with a new store begun. Identity is never silently reassigned.
- **[AGENT] (orchestrator-ratified, 2026-08-12)** Whichever route design takes must be **additive or
  versioned**: a behavior-changing rewrite of existing durable records is not in this item's silent
  scope. If design finds that neither route can be additive or versioned — that landing coverage
  accounting forces a destructive or lossy transition of stored results — that is an **owner-visible
  decision to surface at close**, not a design call. The reviewer flagged this as an owner
  disposition wearing a design label (review L2-1) and it is treated as one.

### Cross-repository and scope

- **[HARD]** (Item 2 hand-off, `constraint-catalog-totality/verification.md` "Cross-repo") TEAx must
  re-vendor `ACCEPTED_CATALOG_SCHEMA_VERSIONS` to include `3.0.0`. TEAx fails closed on every newly
  generated package until it does — the intended direction. **Never bump TEAx first**; the landing
  order is codegen, then TEAx.
- **[NEED]** (owner instruction, align record 2026-08-12; regraded from `[HARD]` per review L1-3)
  All TEAx work happens on a branch. TEAx `main` is never committed to. The grade table reserves
  `[HARD]` for what an interface, physics, or an existing system forces; a working agreement the
  owner stated is `[NEED]`. Both are settled-eligible, so nothing downstream weakens.
- **[INHERITED: Item 2 design, "Item 3 coordination"; LC-E05]** This item adds no usage-tier catalog
  field and renames nothing. Every input the feasibility denominator needs already exists at catalog
  `3.0.0` keyed by `declaration_id` — LC-E05 is the obligation that put them there (one visible
  disposition per usage over the complete authored-usage domain, with source form, identity, owner
  QN, definition QN, and the explicit join), and this item is its consumer, not a second author.
- **[INHERITED: epic Item 3 scope 6]** Generated schemas, package contracts, and cross-repository
  pins are versioned or migrated as required, with the landing order specified before code lands.

### Sequencing

- **[NEED]** (owner-directed sequence, handoff 2026-08-12, carried from the umbrella spec) Expected
  outputs are captured from the settled semantics before confirmation tests run. Expectations are
  never reverse-engineered from current behavior — which matters most here, because the current
  behavior is precisely the defect. The concrete instance is
  `test_fusion_tea_real_teax.py:244-259`: its expected coverage block is hand-captured from the
  settled semantics first, then the real-TEAx route is run against it.

## Non-Goals

- **Touching the companion (`agentic-mbse`).** It is expected untouched: nothing in the report,
  seam, or policy work names a companion surface. If design finds one, that is a surfacing event,
  not a quiet edit.
- Recomputing or duplicating per-usage constraint detail outside the catalog.
- Changing Item 2's disposition vocabulary, usage-tier schema, or totality gate.
- CATF model migration, intent classes, and tolerance decisions — Item 5.
- Calculation-definition gate execution and its per-occurrence guard volume — Item 6.
- Changing BLOCK-halts-generation semantics, or admitting in-predicate feature chains.
- Executing requirement satisfaction (`satisfy`, `require`/`assume`).
- An evaluated-advisory tier for plain constraints.

## Open Questions / Deferred to design

All of these are deferred by the umbrella spec or by Item 1, not decided here.

- **Token spelling.** The umbrella defers `satisfied_partial` vs `partially_satisfied`, and the
  canonical runtime counterpart's spelling with it.
- **Report field names and shapes** for the compact coverage block, including how the reason
  histogram is keyed (Item 2's closed reason-token set is the natural key) and whether the coverage
  block is a nested model or flat fields on `ConstraintReport`.
- **Where the derivation runs.** Report-from-catalog is fixed (spec-F5); whether the counts are
  computed at projection and baked into the aggregator template, or computed in the aggregator from
  embedded catalog data, is design's call — as is the negative test that proves divergence fails.
- **Schema migration path** for `ConstraintReport` and the package contract: version bump, what
  happens to already-generated packages and captured baselines, and — named explicitly because the
  TEAx `3.0.0` re-vendor lands in this item — which of invariant 50's two routes existing durable
  study stores take, inside the additive-or-versioned constraint stated in Known Requirements.
- **Does a durable study store with results worth keeping exist yet?** Design's first act on the
  TEAx side is to check. If the answer is no, the invariant-50 question collapses to "start clean"
  and this item is sized as the epic estimated. If the answer is yes, the transition is real work
  and the 2-day estimate is undersized — flag it then rather than absorbing it (review L2-2). The
  question is recorded here because it cannot be answered from the codegen repo.
- **Config opt-in spelling** for the partial-coverage → feed-strategy per-study override, and the
  durable case-record shape that carries coverage counts and catalog linkage.
- **Landing order**, including where the TEAx `ACCEPTED_CATALOG_SCHEMA_VERSIONS` re-vendor sits and
  how long the fail-closed window stays open.
- **Aggregation-by-definition with drill-down** once the calc-def capability lands (umbrella open
  question, restated here only as the thing design must not foreclose).

### Surfaced, not resolved

- **Two published rules cross when every asserted gate is dispositioned inapplicable.** Appendix C's
  "Asserted vacuous gate" cell says a usage carrying an explicit inapplicability disposition "drops
  out of the feasibility denominator and the headline reads full satisfaction when every remaining
  gate passed." State 5 says a model with "no applicable asserted gate at all" reads not assessed. A
  model whose only asserted gates are all dispositioned inapplicable satisfies both readings: zero
  remaining gates, all vacuously passed, and zero applicable asserted gates. Item 3 writes the
  precedence function, so it will pick one by accident unless design rules it. Both readings are
  agent-grade Item 1 text; this spec does not choose between them. Design must treat this as a
  **ruling to publish** — written down with its reasoning, against the contract — not a coin flip
  settled inside the precedence function (review L3-5).
- **The epic's scope-4 wording is looser than the amended contract.** Epic Item 3 scope 4 says
  "constraint-bearing models with no executable assertions"; the amended LC-E10 says explicitly that
  the trigger is the absence of an **applicable asserted gate**, not the absence of eligible
  concrete assertions — an applicable gate that produced zero eligible entries reads *partial
  coverage*, not not-assessed. This spec follows the contract, which is the later and more specific
  authority and was amended by Item 1 for exactly this distinction. Flagged rather than silently
  reconciled (capture-fidelity law 4); the epic text may want the same correction at close.
- **TEAx surfaces are cited second-hand.** The TEAx tree at `/home/reid/1cfe/teax` is outside this
  session's sandbox, so `evaluation/projection.py`, `study/policy.py`, the durable case-record
  layer, and `ACCEPTED_CATALOG_SCHEMA_VERSIONS` are cited here from the research record and Item 2's
  hand-off, at line numbers captured 2026-08-12. Design must re-grep them in a session with TEAx
  access before relying on any line number, and must confirm the TEAx suite's runner from that
  repo's own README/pyproject. The independent spec review hit the same sandbox boundary and reached
  the same disposition (review L1-2), and noted what caps the exposure: the load-bearing
  two-vocabulary requirement rests on contract authority, not on those line numbers, so a wrong cite
  costs design a re-grep rather than a requirement.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_constraint_semantics_contract.md` (Item 3)
- **Required Reading:**
  - `.project/active/constraint-semantics-contract/spec.md` — "Report and coverage contract",
    "Study policy"
  - `.project/research/20260812-101200_constraint-semantics-end-to-end.md` §§2, 4–5
  - `.project/active/constraint-semantics-contract/product-lens.md` — spec-F1 (ADR-009, filed by
    Item 1 — cite, do not re-file), spec-F2, spec-F3, spec-F5
  - `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md` — "Headline states
    and coverage truth"; invariants 32, 33, 41, 46/46a, 48, 49, 61
  - `.project/concepts/constraint-execution-lifecycle-requirements.md` — LC-E05/E06/E10/E11/E12/E13
- **Upstream item consumed:** `.project/active/constraint-catalog-totality/design.md` ("Token
  Vocabulary (Item 3 cites this section)", "Item 3 coordination") and its `verification.md`
  "Cross-repo" hand-off
- **Decision record:** ADR-009 (`docs/architecture/modeling-assumptions.md` §9)
- **Orchestration:** `.project/active/constraint-coverage-policy/briefs/align.md`,
  `briefs/spec.md`
- **Product lens:** `.project/active/constraint-coverage-policy/product-lens.md`
- **Spec review:** `.project/active/constraint-coverage-policy/spec-review.md` (verdict Revise,
  2026-08-12; all nine findings resolved, resolutions recorded there by ID)
- **Design:** `.project/active/constraint-coverage-policy/design.md` (to be created)

---

**Next Steps:** Spec review completed 2026-08-12 (verdict Revise; L1-1..L5-2 resolved and
incorporated, with L3-1/L3-2/L2-1/L1-5 settled by orchestrator ruling). Next: `/_my_design`.
