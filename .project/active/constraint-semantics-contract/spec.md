# Spec: Constraint Semantics and Design-Search Feasibility Contract

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-08-12 14:56 PDT
**Complexity:** HIGH
**Branch:** `item7-rebuild` (worktree `/home/reid/1cfe/sysml-codegen-item7-rebuild`; coordinated
changes in `agentic-mbse-item7-rebuild` and `teax`)

---

## Problem

Constraints are the mechanism by which our models enforce physics and consistency so that
design-space search stays viable. The owner's framing, stated 2026-08-12:

> **[OWNER-VERBATIM]** "when we started this whole cleanup, it was while defining a policy around
> how to use constraints to enforce things like physics in a way that make our overall 'design
> search' viable"

and the directing instruction (handoff, 2026-08-12):

> **[OWNER-VERBATIM]** "We need to get to the bottom of 'how do constraints work', checking
> against our most rich model to make sure we have defined, clear expectations and that that is
> what our code does."

Measured against the richest model (`catf_mfe_d5`, 65 authored constraint usages), the product
today does none of that
(full evidence: `.project/research/20260812-101200_constraint-semantics-end-to-end.md`,
independently reproduced by a second agent the same day):

- **65 authored checks → 9 visible dispositions → 0 executed.** 51 calc-def-owned constraints
  are structurally unreachable (`elaborate.py:522-539` has no CalculationDefinition branch);
  5 part-def-owned ones attach to zero occurrences because every design part is untyped; the
  9 part-usage-owned ones are excluded as `plain_usage`. All 42 generated calculation modules
  instantiate constraint-bearing calc defs — the formulas execute, their validity envelopes do not.
- **56 of the 65 have no catalog record at all** — not eligible, not excluded, absent. The
  contract already promises one visible disposition per usage (invariants 1 and 28); REQ-CL-04 is
  the PARTIAL matrix row for exactly this.
- **The docs contradict the code and the standard.** `modeling-assumptions.md:489-491` tells
  authors a bare `constraint` gives an enforced gate; the profile makes it UNASSESSED before
  reading the predicate; SysML v2 (Part 1 §8.4.16.3) says a plain constraint asserts nothing.
  Seven defective doc statements are cataloged (research doc, D1–D7).
- **The report can misrepresent coverage.** `ConstraintReport` carries only
  `assessed_count`/`headline`/`results`; the aggregator never consults exclusions, so 2-of-9
  assessed can read `all_satisfied`. An excluded-only model generates no aggregator at all.
- **The search sees nothing.** TEAx labels a constraint-bearing-but-unassessed package
  `unconstrained` — the identical disposition to a genuinely constraint-free model. CATF
  candidates receive no physics-based rejection and no signal that 65 authored checks were
  omitted.

This spec captures the product rule — modeling policy, pipeline invariants, report contract, and
study-policy defaults across sysml-codegen, agentic-mbse, and teax — from the eight rulings of
2026-08-12: agent-proposed recommendations the owner ratified in a recorded Q&A (durable record:
`rulings-20260812.md` in this directory), together with the owner-stated needs quoted here. Per
capture-fidelity the rulings remain agent-grade and challengeable; only the quoted owner
statements are owner-originated. The owner's required sequence: settle semantics → fix
documentation and the test model to match (capturing expected output) → then run the tests to
confirm.

## Success Criteria

- [ ] **One product rule, stated once, agreed everywhere.** The lifecycle contract, agentic-mbse
      modeling guidance, and codegen reference docs state the same constraint semantics; the seven
      defective statements (D1–D7 in the research doc) are corrected by amendment/deletion, not
      annotation.
- [ ] **Catalog totality holds and is gated.** Every manifest-swept constraint usage receives
      exactly one catalog disposition (eligible / excluded-with-reason / non-reaching-with-reason);
      a generation-time completeness gate fails on any unaccounted usage. On the migrated CATF
      derivative and on the frozen `catf_mfe_d5`: 65/65 carriers.
- [ ] **Severity by cause is demonstrable.** An asserted, structurally-unattachable constraint
      halts generation with a named diagnostic; an asserted, vacuous constraint (owner has zero
      occurrences) produces a visible warning-grade disposition and an authoring advisory; plain
      forms produce records and never errors.
- [ ] **The headline cannot claim more coverage than exists.** `all_satisfied` requires every
      applicable asserted gate assessed and passed; an unassessed applicable asserted gate
      (including a vacuous one without an inapplicability disposition) forces the
      partial-coverage headline; a constraint-bearing model with zero applicable asserted gates
      emits a `not_assessed` report through a generated zero-input aggregator; a constraint-free
      model remains report-free (`unconstrained` becomes true by construction).
- [ ] **The study reacts correctly to every coverage state.** Default dispositions per the
      ruling (partial → keep-for-boundary); feed-strategy for partial coverage only via an
      explicit, recorded per-study opt-in; coverage lands in durable case records.
- [ ] **The migrated CATF derivative proves the policy end to end** (denominator named per
      spec-review L3-1): every one of the 65 authored usages carries an explicit disposition —
      the nine instance-reaching gates get intent class, target form, and owner-signed
      tolerances; the five part-def guards get typed attachment or an explicit inapplicability
      disposition; the 51 calc-def guards get derive-instead (where the equality taxonomy
      applies) or awaits-capability — zero unaccounted usages, full feasibility coverage over the
      applicable asserted gates, and at least one mutation demonstrates a physics-based `reject`
      of an unphysical candidate through the real TEAx route.
- [ ] **The calc-def gate capability is filed with ruled semantics** (one check per calculation
      occurrence) as a designed backlog item; until it lands, the interim behavior is the
      severity-by-cause error, not silence.
- [ ] **The two named defects are fixed**: unit-annotated literals (`8.55 [m]`) inside asserted
      predicates elaborate correctly, and the feature-chain block diagnostic names the offending
      reference and states the rewrite.
- [ ] **REQ-EXT-09 is re-graded and re-anchored** (lens spec-F7): its PASS currently rests on
      specimen fixtures that each happen to have carriers while 56/65 CATF usages have none; the
      row's grade and proof move to the totality gate in the same landing, alongside the
      REQ-CL-04 correction.
- [ ] **The equality-usage instruction is published** in the concept and agentic-mbse authoring
      guidance: the when-to-use-equality intent taxonomy (derive structural identities; loose
      banded validity cross-checks; one-sided feasibility gates; closure by construction), as
      required by the owner statement recorded in the modeling-policy requirements.

## Known Requirements

All rulings below tagged **[INFERRED]** were agent-proposed and owner-selected in the recorded
2026-08-12 Q&A; per capture-fidelity they remain agent-grade (ratified by owner, 2026-08-12) and
are challengeable by re-deriving against their recorded reasoning. `(Q1)`–`(Q8)` cite the durable
ruling record `rulings-20260812.md` in this directory; `(lens spec-Fn)` cites the product-lens
ledger `product-lens.md`. Requirement text stands alone — the labels are citations, not context a
reader must chase.

### Modeling policy (the language rule)

- **[HARD]** SysML v2 semantics: a plain `constraint` usage is a computed Boolean with no truth
  claim; only the assert family (`assert constraint`, `assert not`, `satisfy`) binds the
  predicate's value (SysML v2 Part 1 §8.4.16.3; KerML §8.4.4.8.2). Any product rule must not
  claim standard authority for enforcing what the model did not assert.
- **[INFERRED]** (Q1) **Assert-only enforcement.** Bare `constraint` = visible, cataloged,
  never-executed description. `assert constraint` (inline or definition-typed) is the sole opt-in
  to enforcement. An evaluated-advisory tier for plain constraints is recorded as a possible
  future extension, not a commitment.
- **[INFERRED]** (consequence of Q1, made explicit per lens spec-F2) **An unsupported predicate
  inside a bare `constraint` never halts generation** — the form gate runs before the predicate
  walk, so a plain constraint can carry a construct that would BLOCK if asserted, and the model
  still generates (the usage catalogs as unassessed). This is intended behavior and a product
  statement: BLOCK protects asserted gates only; descriptive constraints are never load-bearing.
- **[INFERRED]** (Q2) **Calc-def-owned asserted constraints mean one check per calculation
  occurrence and will execute.** Delivery is staged as its own designed capability item; this spec
  rules the semantics, not the build.
- **[INFERRED]** (Q4) **Bindings-only predicates.** The blessed gate shape is a `constraint def`
  with formals, asserted via `assert constraint g : Def { in formal = <path>; }`, predicates over
  formals only. In-predicate feature chains remain blocked; chain admission is filed as an
  explicit future capability candidate, not a closed door. Equality intent is expressed as
  two-inequality tolerance bands, made ergonomic by a small reusable constraint-def library
  (e.g. `WithinBand`). **Scope precision (lens spec-F6):** the restriction is
  *predicate-body-only* — feature chains in binding position (`in formal = child.attr`) stay
  supported per contract D-7 and invariant 20, and inline asserted forms (predicate over local
  names) remain admitted per invariant 12; nothing here narrows inline admission or calculation
  binding resolution.
- **[NEED]** (owner-stated, 2026-08-12) Tolerances are modeled, modeler-chosen values; the
  pipeline never invents one.
- **[NEED]** (owner-stated, 2026-08-12) **The concept must instruct WHEN equalities should be
  used at all** — authoring policy in agentic-mbse guidance scope, beyond what sysml-codegen
  supports:
  > **[OWNER-VERBATIM]** "we know that narrow bands of viability may make design exploration
  > really difficult. So I want to call out in our concept WHEN we really think equalities SHOULD
  > be used (instructions) in addition to the sysml-codegen support"

  **R-POL-4, the instruction content (agent-drafted, owner-reviewed in session):** intent
  taxonomy for `a == b` — (1) structural identity → derive it, don't constrain it; (2)
  cross-check of independently computed values → loose, physically motivated validity band;
  (3) feasibility gates → prefer one-sided inequalities; if a quantity must equal a value,
  fix it as an input rather than search-and-constrain; (4) composition closure → derive the
  last term by construction, else a banded validity check.
- **[INFERRED]** (Q7) **Requirements-side forms stay non-executable and visible.**
  `require`/`assume` are conjuncts of their requirement's implication; `satisfy` IS an assertion
  per the standard but requirement evaluation is a declared out-of-scope capability — an
  out-of-scope *form* gets a named visible exclusion, never the unreachable-assert error.

### Pipeline invariants (sysml-codegen + agentic-mbse)

- **[INHERITED]** (contract invariants 1, 28 —
  `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md`) Every usage gets
  one profile disposition and one visible catalog disposition. This spec operationalizes what the
  contract already promises; the exact route currently violates it for 56/65 CATF usages.
- **[INFERRED]** (Q3) **Totality is hard-gated.** A generation-time completeness check fails
  generation on any authored constraint usage without a catalog disposition. "Reaches no
  instance" is itself a visible exclusion reason, never an absence.
- **[INFERRED]** (spec-review L3-2) **The gate must not be circular.** Today constraint records
  exist only downstream of owner-to-scope expansion, so comparing the graph with its own catalog
  cannot detect usages that vanished before either existed (the 56). The canonical authority must
  therefore record the **complete authored-usage domain before occurrence expansion**, and the
  gate compares dispositions against that domain — never two projections of the same
  already-truncated set.
- **[INHERITED]** (contract invariants 40, 48; D-3 owner-verbatim "no second catalog authority";
  lens spec-F4) **One authority owns totality.** The authored-usage domain and its dispositions
  live in the graph/embedded-catalog authority — no parallel constraint inventory kept in sync by
  hand. This must be reconciled with ELABORATE-FIRST Item 7's deletion of the dual
  constraint-fact extraction pass; design names the single owning representation.
- **[INFERRED]** (Q3) **Severity by cause.** Asserted + structurally unattachable (in-scope form,
  no attachment capability — e.g. calc-def pre-capability) = generation-halting error. Asserted +
  vacuous (owner has zero occurrences) = warning-grade visible disposition plus an authoring-time
  advisory ("part def with asserted constraint has no typed occurrences") — and, per the coverage
  ruling below (spec-review L2-2), it counts as missing assessment until dispositioned
  inapplicable. Plain and out-of-scope forms = visible records, never errors.
- **[INHERITED]** (contract invariant 32) A model with constraint usages but zero eligible
  assertions still requires the zero-input aggregator and a `not_assessed` report; a model with no
  constraint usages remains inert. The current projector early-return
  (`project.py:895`) violates this; the fix lands as part of this contract, not as an isolated
  patch (owner sequencing, handoff 2026-08-12).
- **[HARD]** **[item3-F2 — RESOLVED 2026-08-13, amended 2026-08-14 by CONSTRAINT-SEMANTICS Item 7.
  Not a live blanket requirement; read the scoped form.]** A profile BLOCK on an asserted constraint
  **that reaches occurrences** halts generation of the whole model (existing ratified fail-closed
  behavior; verified `elaborate.py:488`). An asserted usage that reaches no occurrence never halts:
  it is governed by severity-by-cause and the coverage rules (`non_reaching`, missing assessment,
  partial coverage). Model migration is therefore atomic per model for reaching gates — plan
  accordingly; this spec does not change BLOCK semantics.
  **Resolution:** ruling `[AGENT] (ratified by owner, 2026-08-13)`, recorded at
  `.project/completed/20260814_constraint-docs-agent-sync/owner-checkpoint-20260813.md:38-53`. The contract
  amendment lives at
  `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md` invariant 1, with its
  amendment note.
- **[NEED]** (owner-directed sequence, handoff 2026-08-12) Documentation and the test model are
  fixed to match the settled semantics — including capturing expected outputs — *before* tests
  are run to confirm; expectations are never reverse-engineered from current behavior.

### Report and coverage contract (codegen templates + teax)

- **[INFERRED]** (Q5, refined per spec-review L2-1) **Coverage lives in the headline, and its
  denominator is applicable asserted gates.** Two totals exist and must not be conflated:
  *inventory totality* (the catalog: every authored usage of every form, zero absences — the Q3
  gate) and *feasibility coverage* (the headline's claim, counted over applicable **asserted**
  gates only). `all_satisfied` means every applicable asserted gate was assessed and passed. A
  new partial-coverage headline value (token spelling deferred to design) means an applicable
  asserted gate went unassessed. Deliberately descriptive (plain) and requirement-side usages
  appear in inventory, never in the feasibility denominator — a model whose only constraints are
  descriptive reads `not_assessed`, not partial. Precedence remains violation > indeterminate >
  satisfied tier > not_assessed.
- **[INFERRED]** (Q5) The report embeds compact coverage accounting — authored-usage total,
  assessed count, excluded count with reason histogram, coverage state — while per-usage exclusion
  detail stays in the catalog (schema authority, contract invariant 48), joined by the catalog
  fingerprint the report already carries.
- **[INFERRED]** (Q5) **Two-tier accounting:** coverage counts authored usages; results list
  concrete occurrences.
- **[INFERRED]** (spec-review L2-2, superseding the earlier "vacuous doesn't block full" ruling)
  **A vacuous asserted gate counts as missing assessment by default.** An asserted usage whose
  owner has zero occurrences holds the model at partial coverage (boundary-kept) until either the
  model is fixed so the gate attaches, or the usage carries an explicit inapplicability
  disposition (mechanism deferred to design: a model annotation or a reviewed catalog-level
  acceptance). Rationale: every observed vacuous case (CATF's five part-def guards) is an
  accidental detachment, not a deliberate one. The Q3 warning + advisory remain; this adds the
  coverage consequence.

### Study policy (teax)

- **[HARD]** (existing interface, spec-review L1-1) Two headline vocabularies exist and are
  bridged by a normalization seam: the generated report emits report tokens (`violation`,
  `all_satisfied`, `not_assessed`, …) and TEAx projection maps them to the canonical
  runtime tokens policy dispatches on (`violated`, `satisfied`, `not_assessed`;
  `evaluation/projection.py` `CANONICAL_HEADLINE`, `study/policy.py`). The contract must define
  the new partial-coverage value in **both** vocabularies and extend the normalization seam;
  a report-side-only token that projection cannot map is a failure, not a fallthrough.
- **[INFERRED]** (Q6) Default dispositions on the canonical vocabulary: violated → reject;
  indeterminate → keep-for-boundary; not-assessed → keep-for-boundary; **the partial-coverage
  state → keep-for-boundary**; fully-covered satisfied → feed-strategy/penalize as today;
  `unconstrained` unchanged and now honest by construction. A study may explicitly configure the
  partial-coverage state → feed-strategy; the opt-in is a visible, auditable config line, and
  coverage numbers land in durable case records regardless.
- **[INHERITED]** (contract invariants 41, 49) Policy consumes evidence read-only; it cannot
  mutate status, margin, observations, identity, or catalog linkage.

### Contract amendment obligations (lens spec-F1/F2/F3)

- **[INFERRED]** (agent-originated process obligation from the product-lens gate, spec-F1) The
  headline-vocabulary change is an intentional product-contract change and is filed as an ADR
  (owner-ratified provenance) before implementation; the ADR id is cited back into the
  product-lens ledger.
- **[INFERRED]** Design publishes the complete amendment set invariant-by-invariant before code
  lands — at minimum contract invariants 1 (asserted-only BLOCK scope), 8/9 (new severity for the
  asserted-unattachable cause), 28 (third disposition kind), 32, 33 (headline precedence), 46/46a
  (report field additions + fail-closed handling of the new headline token on the TEAx side), 48,
  and the affected Appendix C cells — **and the frozen requirements companion**
  (`constraint-execution-lifecycle-requirements.md`, whose header requires forward amendments to
  land there: LC-E05/E06/E10/E11/E12 at minimum). Amendments preserve original provenance grades.

### Migration, fixtures, and defects

- **[INFERRED]** (Q8) **CATF migration happens in a new derivative fixture** forked from
  `catf_mfe_d5`; the twins stay frozen as ratified refusal/rename witnesses. The derivative's
  PROVENANCE records every change and why — the d5→derivative diff is the worked example of the
  policy.
- **[HARD]** `catf_mfe_model`'s ratified corpus row pins its refused shape, and `catf_mfe_d5` is
  byte-reversal-pinned to it (`test_d5_variants.py:29`); neither twin's constraint syntax may
  change.
- **[NEED]** (owner-gated; scope set by spec-review L3-1/L3-3 resolution) The migration carries a
  disposition table covering **all 65 authored usages**: the nine instance-reaching constraints
  get intent class, target form, and each tolerance value signed off by the owner
  (equality-class-1 constraints dispositioned as derivations, not banded constraints, where the
  taxonomy applies); the five part-def guards get typed attachment or explicit inapplicability;
  the 51 calc-def guards get derive-instead or awaits-capability. The owner checkpoint for this
  table lives in the CATF child item (see Structure below), before that item's design.
- **[INFERRED]** (Q8) Two named defects are in-scope must-fixes: the `[m]`-unit-literal
  elaboration crash (`SI_OCCURRENCE_MISSING` on unit-annotated literals in asserted predicates)
  and the tautological `feature_chain: block_feature_chain` diagnostic (must name the offending
  reference and state the bindings rewrite).
- **[INFERRED]** `tests/fixtures/catf_mfe_d5/PROVENANCE.md`'s stale acceptance paragraph (still
  claims the exact route refuses the model) is amended when the fixture's role is recorded.

## Non-Goals

- Executing requirement satisfaction (`satisfy`, `require`/`assume` evaluation) — declared out of
  executable scope; revisiting it is a new capability decision.
- Building the calc-def gate capability in this item — semantics ruled here, delivery staged as
  its own designed item.
- Admitting in-predicate feature chains — filed as a future capability candidate, not built here.
- First-class tolerance semantics for `==` — deferred; the two-inequality band plus library defs
  covers the need until proven insufficient.
- An evaluated-advisory tier for plain constraints — recorded as a possible future extension only.
- Migrating the frozen CATF twins in place, or changing BLOCK-halts-generation semantics. *(item3-F2
  — RESOLVED 2026-08-13. This Non-Goal held for this spec's own work and still does. The blanket
  clause it referred to was separately amended to reaching-gates scope on 2026-08-14 by
  CONSTRAINT-SEMANTICS Item 7, under the ruling at
  `.project/completed/20260814_constraint-docs-agent-sync/owner-checkpoint-20260813.md:38-53`. Read the amended
  form in the contract's invariant 1, not the blanket one.)*
- Re-planning ELABORATE-FIRST Item 7 — its narrow-correction steps 4–10 remain the plan of
  record and resume after this contract work per the owner's sequencing.

## Open Questions / Deferred to design

- Exact headline token (`satisfied_partial` vs `partially_satisfied`), report field names/shapes,
  and the generated-schema migration path for the vocabulary change.
- Name of the new derivative fixture (working name `catf_mfe_gated`) and the exact fixture-check
  that replaces byte-reversal for it (e.g. a provenance-diff manifest).
- The reusable constraint-def library's home, contents, and naming (`WithinBand` et al.).
- How coverage accounting and the report handle per-occurrence guard volume once the calc-def
  capability lands (aggregation-by-definition with drill-down was flagged in session; design
  decides).
- The completeness gate's mechanical home (extraction-time vs generation-preflight) and how it
  composes with the existing ledger checks.
- Amendment drafting (in-place vs added, per invariant) for the full set now listed under
  Contract amendment obligations — drafting belongs to design/close with provenance preserved.
- Per-constraint tolerance values for the CATF derivative — owner sign-off during migration
  (recorded above as owner-gated; values not yet chosen).
- **Coverage derivation direction (lens spec-F5):** the report's embedded coverage counts and the
  catalog state the same facts; design must fix which is computed from which (expected: report
  derived from catalog at generation time) so the pair cannot diverge.
- **Item 7 evidence invalidation register (lens spec-F8):** the epic plan records which paused
  Item 7 evidence this contract work invalidates — step 4's REQ-CL-03 pre-amendment check and the
  three-route `gain = 100` proof, step 7's three batteries at one paired OID, step 8's candidate
  record, and the ELABORATE-FIRST epic's single 37-fixture recapture (a second recapture is now
  likely) — and whether each is re-run after landing or absorbed into a child item.
- **Vacuous-inapplicability mechanism (L2-2):** model annotation vs reviewed catalog-level
  acceptance — design of the totality/catalog child decides.
- **Surfaced premise conflict, owner to disposition (lens spec-F6, pre-existing, NOT resolved
  here):** contract D-2's acceptance cell requires "a usage-owned attribute on a concrete
  `PartUsage` and a self-named actual" while D-4/SRC-01 makes bare self-named bindings
  UNSUPPORTED. This spec's blessed-shape ruling sits on top of that conflict without resolving
  it; per capture-fidelity law 4 it is surfaced here and parked.

---

## Structure (spec-review L2-3 resolution)

This spec is the **umbrella behavioral contract**, not one implementation item. Decomposition
happens via `/_my_epic_plan` into auditable child items, expected roughly as: (1) contract/
companion amendments + ADR + doc corrections D1–D7; (2) totality domain + catalog + completeness
gate; (3) report/coverage vocabulary + TEAx projection and policy; (4) the CATF derivative
migration (hosts the all-65 disposition table and the owner tolerance checkpoint); (5) the two
named defects. The epic also owns the Item 7 evidence-invalidation register and sequencing
against the paused narrow correction. Child items cite this spec as their required reading; the
epic plan may adjust the cut lines, not the behavioral rulings.

---

## Related Artifacts

- **Research:** `.project/research/20260812-101200_constraint-semantics-end-to-end.md` (this
  session; includes the nine-constraint table, assert-conversion probe, doc-contradiction register
  D1–D7, and spec-semantics citations)
- **Owner direction:** `/tmp/handoff-20260812-095207.md` (subjects 1–4 and required order;
  quoted verbatim above) — durable copies of its rulings live in this spec
- **Ratified authorities being amended:**
  `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md` and its frozen
  requirements companion `.project/concepts/constraint-execution-lifecycle-requirements.md`
  (forward amendments land in the companion per its header)
- **Adjacent plan of record:** `.project/active/cutover-recovery/plan.md` (Item 7 narrow
  correction, steps 4–10 paused behind this item)
- **Durable ruling record:** `.project/active/constraint-semantics-contract/rulings-20260812.md`
  (the eight Q1–Q8 rulings, alternatives, and owner-verbatim payloads)
- **Spec review:** `.project/active/constraint-semantics-contract/spec-review.md` (verdict
  Revise; resolutions recorded there by finding ID)
- **Product-lens ledger:** `.project/active/constraint-semantics-contract/product-lens.md`
- **Design:** `.project/active/constraint-semantics-contract/design.md` (to be created)

---

**Next Steps:** Spec review completed 2026-08-12 (verdict Revise; all findings resolved in
`spec-review.md` and incorporated). Next: `/_my_epic_plan` to decompose per the Structure
section; child items then run spec/design/implement per pipeline, with the CATF child carrying
the owner tolerance checkpoint.
