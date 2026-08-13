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
      pinned report outcome **and** an independently pinned canonical TEAx outcome. Six report
      states minus one (state 6 is report-absent by construction) means five report headline values
      and their six runtime dispositions are each proven by a test that no other state satisfies.
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
- [ ] Partial coverage defaults to keep-for-boundary; feed-strategy for partial coverage happens
      only with an explicit config line; both paths persist coverage counts and catalog linkage in
      durable case records.
- [ ] Unknown or unmapped report and runtime headline tokens fail closed with a named error — no
      fallthrough to a satisfied or unconstrained reading, no unnormalized `KeyError`.
- [ ] Cross-repository compatibility tests pass, codegen and TEAx full suites pass, ruff/mypy are
      zero-new against baseline, generated artifacts are reviewed, and `git diff --check` is clean —
      with exact counts recorded in `verification.md`.
- [ ] **[INHERITED: constraint-semantics-contract-amendments/audit.md M-1]** The four
      `all_satisfied` assertions in codegen `tests/execution/` are moved to the new vocabulary and
      each now asserts a coverage claim rather than a not-failed one.

## Known Requirements

Provenance note: behavioral requirements below are **[INHERITED]** from the umbrella contract
(`.project/active/constraint-semantics-contract/spec.md`, its Q5/Q6 rulings and spec-review
resolutions L1-1/L2-1/L2-2) and from Item 1's landed definitions home (the lifecycle contract and
its frozen requirements companion). The umbrella's rulings are agent-grade, owner-ratified
2026-08-12, and challengeable only by re-deriving against their recorded reasoning — not by an
implementing agent's preference. Items marked **[INFERRED]** are this spec's own reading of what
those obligations force here.

### What the report must say

- **[INHERITED: lifecycle contract, "Headline states and coverage truth"; invariant 33; LC-E11]**
  The headline states are violation, indeterminate, full satisfaction, partial coverage, and not
  assessed, with report-absent (`unconstrained`) as the sixth state by construction. Precedence is
  violation → indeterminate → full satisfaction → partial coverage → not assessed. Full
  satisfaction is a coverage claim — every applicable asserted gate assessed and passed — not the
  absence of a failure.
- **[INHERITED: contract, same subsection; umbrella Q5 / spec-review L2-1]** The feasibility
  denominator is applicable asserted gates only, and **the test is on the form, not the
  predicate**: an asserted usage whose predicate is `BLOCK`ed or classified `NON_NUMERICAL` stays in
  the denominator as an unassessed gate. Plain and requirement-side usages are never applicable
  asserted gates; a model whose only constraints are descriptive reads not-assessed, never partial.
- **[INFERRED]** The `BLOCK` half of that clause is testable only where the usage reaches no
  instance. `SI_CONSTRAINT_BLOCKED` is raised inside the scope loop (`elaborate.py:1018-1029`), so an
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
- **[INHERITED: umbrella Q5]** The report embeds *compact* coverage accounting — authored-usage
  total, assessed count, excluded and non-reaching counts with a reason histogram, and the coverage
  state. Per-usage exclusion detail stays in the catalog (invariant 48), joined by the catalog
  fingerprint the report already carries.
- **[INHERITED: umbrella Q5]** Two-tier accounting: coverage counts authored **usages**; the
  results list carries concrete **occurrences**. The two tiers relate through `occurrence_count`
  and are never conflated in one number.
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
  The replacement is the report-required trigger above (any authored constraint usage), and it stays
  in one place, so the three generation seams that read it cannot drift apart again.

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

### Cross-repository and scope

- **[HARD]** (Item 2 hand-off, `constraint-catalog-totality/verification.md` "Cross-repo") TEAx must
  re-vendor `ACCEPTED_CATALOG_SCHEMA_VERSIONS` to include `3.0.0`. TEAx fails closed on every newly
  generated package until it does — the intended direction. **Never bump TEAx first**; the landing
  order is codegen, then TEAx.
- **[HARD]** (owner instruction, align record 2026-08-12) All TEAx work happens on a branch. TEAx
  `main` is never committed to.
- **[INFERRED]** The companion (`agentic-mbse`) is out of scope for this item and is expected
  untouched. Nothing in the report, seam, or policy work names a companion surface; if design finds
  one, that is a surfacing event, not a quiet edit.
- **[INHERITED: Item 2 design, "Item 3 coordination"]** This item adds no usage-tier catalog field
  and renames nothing. Every input the feasibility denominator needs already exists at catalog
  `3.0.0` keyed by `declaration_id`.
- **[INHERITED: epic Item 3 scope 6]** Generated schemas, package contracts, and cross-repository
  pins are versioned or migrated as required, with the landing order specified before code lands.

### Sequencing

- **[NEED]** (owner-directed sequence, handoff 2026-08-12, carried from the umbrella spec) Expected
  outputs are captured from the settled semantics before confirmation tests run. Expectations are
  never reverse-engineered from current behavior — which matters most here, because the current
  behavior is precisely the defect.

## Non-Goals

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
  study stores take.
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
  agent-grade Item 1 text; this spec does not choose between them.
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
  repo's own README/pyproject.

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
- **Design:** `.project/active/constraint-coverage-policy/design.md` (to be created)

---

**Next Steps:** After approval, `/_my_spec_review` in a fresh session, then `/_my_design`.
