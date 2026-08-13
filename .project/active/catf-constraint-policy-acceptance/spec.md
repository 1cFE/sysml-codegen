# Spec: CATF Derivative and End-to-End Acceptance

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-08-13
**Complexity:** HIGH
**Branch:** `item7-rebuild` (worktree `/home/reid/1cfe/sysml-codegen-item7-rebuild`; coordinated
TEAx work on `/home/reid/1cfe/teax` branch `constraint-semantics-item3`)
**Epic:** CONSTRAINT-SEMANTICS, Item 5

---

## Problem

The constraint-semantics contract is now built but never proven on a real model.

Items 1–4 landed the pieces: the assert-only rule and its documentation (Item 1), a catalog that
accounts for every authored usage (Item 2), a coverage-truthful report and TEAx policy (Item 3),
and two predicate-boundary defect fixes (Item 4). Each was verified against purpose-built
fixtures. None of them has been driven end to end on the richest model we have, and the richest
model is still the failure case the epic exists to close.

**The measurement, at Item 2's close.** `catf_mfe_d5` carries **65 authored constraint usages / 9
reaching / 0 eligible**. All 65 are bare `constraint`; there are zero `assert` forms. Nine are
owned by part usages and reach instances (they catalog as excluded, unassessed form); five are
owned by part definitions that no design part is typed by, so they reach nothing; 51 are owned by
calculation definitions, which have no attachment capability yet. The catalog is keyed by
`declaration_id` at `CATALOG_SCHEMA_VERSION` `3.0.0` over an `instance-graph/v3` schema.

Note the corrected premise: older documents say "9 eligible". The 9 are **reaching**, not
eligible, and `catf_mfe_d5` executes zero gates
(`.project/completed/20260813_constraint-catalog-totality/`, recorded deviation).

**What is missing.** There is no all-65 intent/disposition table, no owner-approved tolerance set,
no derivative fixture that carries the policy, and no proof that generated feasibility evidence
rejects an unphysical candidate through the real TEAx route. Without that proof the epic's
critical success factor is an assertion:

> **[OWNER]** A design search can trust the generated feasibility evidence to represent every
> applicable asserted physics gate, while every other authored constraint remains visibly
> dispositioned.
> (`.project/backlog/epic_constraint_semantics_contract.md`, Critical Success Factor)

**The owner's sequence governs how this item runs.**

> **[OWNER, 2026-08-12]** Required sequence: settle the semantics → fix documentation and the test
> model to match (capturing expected output) → then run tests to confirm.
> (`.project/active/constraint-semantics-contract/rulings-20260812.md`)

Semantics are settled. This item does the second and third steps for the CATF model, in that
order, with a hard line between them: expected catalog, report, and study outputs are committed
**before** any confirmation test runs.

**Two measured limits shape the modeling work** (Item 4, `.project/completed/
20260813_constraint-predicate-hardening/`):

1. **A unit written on a constraint *binding* is dimensionally inert to the executable profile.**
   `in tol = 0.05 [m];` contributes the number `0.05` and nothing else — a bound formal takes its
   operand category from the constraint definition's declared type, so the annotation never
   reaches `classify_ordering`. A probe binding a length against a time is **admitted**. The band
   recipe this item must author is exactly that shape, so a mis-united tolerance is admitted
   silently by a gate whose whole purpose is catching wrong physics. Unit correctness on bindings
   has to be caught by human review, or by moving the comparison and both annotations into the
   predicate body (`docs/architecture/modeling-assumptions.md` §8, "Authoring a gate that carries
   units").
2. **A blocked chain's diagnostic points at the constraint usage's line, not the offending
   term's.** Every entry of a multi-chain block renders the same `file:line`. What disambiguates
   is the named reference, which `block_feature_chain` now carries. Drive the rewrites off the
   chain name, not the line.

**One traveling residual lands here.** Item 2's audit residual **R3**: the calc-def-only package
shape (a package whose constraint usages all fail to reach, which correctly ships no
`schemas/constraint_types.py`) has no committed byte baseline. It is pinned only by two
generation-level tests, and A4's justification reached back to a pre-Item-2 state the auditor
could not measure. Item 2's close named this item as the natural home
(`.project/completed/20260813_constraint-catalog-totality/audit.md` §Residuals, R3).

## Success Criteria

The seven epic criteria are the floor; all are carried below. SC-1 through SC-7 restate the epic
item's criteria; SC-8 carries the folded-in residual.

- [x] **SC-1 — The owner approves a table covering exactly 65 usages.**
      **[NEED carried from `constraint-semantics-contract/spec.md`, owner-gated]** No usage is
      missing an intent, target-form, attachment, inapplicability, derivation, capability, or
      tolerance disposition. The table lives in `owner-disposition.md` and is approved before
      design begins. *Met 2026-08-13: the owner ruled on all 65 rows, both tolerances, and the
      open points; `owner-disposition.md` is RULED status and design had not started.*
- [ ] **SC-2 — Every derivative change is accounted for.**
      **[INHERITED: epic Item 5]** The derivative's PROVENANCE and a machine-checkable diff
      account for every change from `catf_mfe_d5`, with a reason per change. Both frozen twins
      retain their ratified modeled syntax and their existing byte-reversal relationship.
- [ ] **SC-3 — The derivative accounts for all 65 and shows honest coverage.**
      **AMENDED — authorized by the owner 2026-08-13, adopting the ruled table's option 1; the
      option's content is [AGENT] (ratified by owner, 2026-08-13).** The derivative's catalog
      shows the accounting identity **65 = 56 carriers + 9 named deletions** (7 derive-instead + 2
      O2 placeholder deletions): every surviving authored usage is a carrier, and every deleted
      usage is a named deletion record in PROVENANCE citing its authorizing table row — nothing is
      a carrier or vanishes silently. The report claims full feasibility coverage over the
      derivative's applicable asserted gates without counting descriptive or requirement-side
      usages in the denominator. The frozen-twin half is untouched: `catf_mfe_d5` itself still
      shows 65/65 carriers (Item 2's proof stands).
      *(The pre-amendment wording — "exactly 65 catalog carriers" — and the surfaced item5-F1
      conflict that forced the ruling are preserved in this file's git history at `102ee6a`;
      resolution recorded per capture-fidelity §3: amended, not annotated.)*
- [ ] **SC-4 — Every applicable asserted gate executes, and the rest match their approved
      dispositions.** **[INHERITED: epic Item 5]** The five part-definition and 51
      calculation-definition groups land exactly where `owner-disposition.md` puts them.
- [ ] **SC-5 — A physics rejection is proved through the real TEAx route.**
      **[INHERITED: epic Item 5]** At least one physically valid candidate reaches the configured
      satisfied path, and at least one unphysical mutation of a physics input reaches `reject`
      through generated package → TEAx normalization → policy → durable case storage.
- [ ] **SC-6 — Expected outputs precede confirmation tests.**
      **[OWNER, 2026-08-12 sequence]** Expected catalog, report, and study outputs are committed
      before any confirmation test runs, and match the resulting outputs with no
      reverse-engineering edit. A commit-order argument, not a claim.
- [ ] **SC-7 — All acceptance gates pass with exact numbers recorded.**
      **[INHERITED: epic Item 5]** Licensed live generation, in-place snapshot, relocated
      snapshot, generation, seal, execution, and TEAx acceptance all pass; counts and fingerprints
      are recorded in `verification.md`, not summarized.
- [ ] **SC-8 — The calc-def-only package shape has a committed byte baseline.**
      **[AGENT, announced at the 2026-08-13 Align checkpoint, unobjected]** Item 2's residual R3 is
      discharged: the shape is covered by a real baseline in the byte-identity gate, not by
      generation-level tests alone.

## Known Requirements

### The derivative and the frozen twins

- **[HARD]** Neither `catf_mfe_model` nor `catf_mfe_d5` may have its constraint syntax changed.
  `catf_mfe_model`'s ratified corpus row pins its refused shape and `catf_mfe_d5` is
  byte-reversal-pinned to it (`tests/conformance/test_d5_variants.py:29`; re-runnable without a
  license via `scripts/make_d5_variant.py --check`).
  (`constraint-semantics-contract/spec.md`, Migration/fixtures/defects)
- **[INHERITED: rulings-20260812.md Q8]** **[AGENT] (ratified by owner, 2026-08-12)** The CATF
  migration happens in a **new derivative fixture forked from `catf_mfe_d5`**. The d5 →
  derivative diff is the worked example of the policy; PROVENANCE records every change and why.
- **[AGENT]** This item decides and records the derivative fixture's name (umbrella working name
  `catf_mfe_gated`) and the fixture-check that stands in for byte-reversal on it — the umbrella
  spec left both open (`constraint-semantics-contract/spec.md`, Open Questions). Design chooses;
  the spec does not.
- **[INHERITED: epic Item 5 scope 6]** `tests/fixtures/catf_mfe_d5/PROVENANCE.md`'s acceptance
  paragraph is stale — it still says the exact route refuses the model with 152×
  `SI_OCCURRENCE_MISSING`, which has not been true since the model began building 42 modules. It
  is corrected. The fixture's role and its bytes outside that documentation change are preserved.

### The all-65 disposition table (`owner-disposition.md`)

- **[NEED carried from `constraint-semantics-contract/spec.md`; owner-gated]** The table covers
  all 65 authored usages in three groups, and is the sole source of intent classes and tolerance
  values for everything downstream:
  - **9 instance-reaching gates** — intent class, target form, and **each tolerance value**.
  - **5 part-definition guards** — typed attachment, or an explicit inapplicability disposition.
  - **51 calculation-definition guards** — derive-instead (where the equality taxonomy applies) or
    `awaits-capability`.
- **[INFERRED, from rulings Q2 + Q3]** No calculation-definition guard may be dispositioned as
  asserted-now. Asserted plus structurally unattachable is a **generation-halting error** by
  ruling, and the halt is whole-model, so a single asserted calc-def guard takes SC-3, SC-4, SC-5
  and SC-7 down together. The only two dispositions available to those 51 are derive-instead and
  `awaits-capability`, which the group's scope already says — this states the consequence so the
  draft table cannot offer a third column by accident. (Item 5 product-lens, item5-F2.)
- **[OWNER 2026-08-13, "go"]** The table and every tolerance value are the owner's decision, made
  at a check-in **after the table draft and before design**. `owner-disposition.md` is a distinct
  pre-design artifact; design does not start against a draft.
- **[NEED]** (owner-stated, 2026-08-12) Tolerances are modeled, modeler-chosen values. The
  pipeline never invents one, and neither does this item's agent — a placeholder in the draft
  table is an explicit `TBD-OWNER` marker, never a plausible number.
- **[INHERITED: `constraint-execution-authoritative-lifecycle-contract.md`, "Equality intent and
  authoring policy"; rendered in agentic-mbse `docs/patterns/constraints.md`]** The four-way
  equality intent taxonomy is the table's classification vocabulary: (1) structural identity →
  derive it, don't constrain it; (2) cross-check of independently computed values → loose,
  physically motivated validity band; (3) feasibility gate → one-sided inequality, and if a
  quantity must equal a value, fix it as an input; (4) composition closure → derive the last term
  by construction, else a banded check.
- **[INFERRED]** The draft table carries a **unit-check column** for every band, because the
  profile will not catch a mis-united binding (Problem, limit 1). Unit correctness on bindings has
  a named human owner at two points and nowhere else: the owner check-in signs the column, and
  design review re-checks it against the authored source. Say so in the table's header so a later
  reader does not assume the toolchain checked it.
- **[INFERRED]** The two mitigations do not compose, and design must not assume they do. The
  supported unit-checking spelling annotates **both** operands in the predicate body, which pins
  the dimension into the predicate — so one generic `WithinBand` over `Real` formals cannot be the
  unit-checking form. Either the library stays dimensionless and review carries units, or the
  library grows per-dimension definitions. Design picks; the spec does not.
  (Item 5 product-lens, item5-F3.)

### Authoring the gates

- **[INHERITED: rulings-20260812.md Q4]** **[AGENT] (ratified by owner, 2026-08-12)** The blessed
  gate shape is **bindings-only**: a `constraint def` with formals, asserted as
  `assert constraint g : Def { in formal = <path>; }`, with the predicate written over formals
  only. Feature chains in **binding position** stay supported; feature chains **inside a predicate
  body** remain blocked.
- **[HARD]** Bare self-named bindings are UNSUPPORTED (D-4/SRC-01). Author none. The ordinary way
  to avoid one is to name the constraint definition's formal differently from the attribute it
  binds (`in wall_t = wall_thickness;`), which is a local edit and does not touch the parked
  conflict — take it. Only if renaming the formal still cannot avoid a self-named binding do you
  **surface it and stop**: the D-2 versus D-4/SRC-01 conflict is parked at the umbrella level
  (`constraint-semantics-contract/spec.md`, Open Questions, lens spec-F6) and must not be resolved
  silently inside this item. (Item 5 product-lens, item5-F5.)
- **[INHERITED: epic Item 5 scope 3]** A small reusable **constraint-definition library** is added,
  including a band form such as `WithinBand`, and bindings-only predicates are used where a banded
  cross-check is appropriate. **[AGENT]** This item decides and records the library's home and
  naming, which the umbrella spec left open.
- **[HARD]** A profile BLOCK on an asserted constraint halts generation of the **whole model**
  (`elaborate.py:488`, verified). Migration is therefore atomic per model: there is no
  partial-migration state where some gates are asserted and the model still builds past a block.
  Plan the derivative's authoring as one all-or-nothing landing.
- **[HARD]** A unit-carrying comparison has exactly one supported in-predicate spelling —
  annotate **both** operands (`gap_width [m] >= 0.25 [m]`). Annotating neither is also admitted
  (a `real`/`real` comparison). Annotating one operand is refused
  (`block_ordering_category_pair`), and a declared quantity type on the attribute is refused
  earlier still (`SI_EDGE_DANGLING`). (`docs/architecture/modeling-assumptions.md` §8)

### What the derivative must produce

- **[INHERITED: `constraint-semantics-contract/spec.md`, catalog totality]** Every authored usage
  carries exactly one catalog disposition — `eligible`, `excluded` with reason, or `non_reaching`
  with reason — over the complete pre-expansion authored-usage domain. 65/65 carriers, zero
  absences.
- **[INHERITED: Item 3 as landed, ADR-009 (`modeling-assumptions.md` §9)]** The report's five
  headline tokens are `violation`, `indeterminate`, `full_satisfaction`, `partial_coverage`,
  `not_assessed`, each mapping to exactly one TEAx runtime token; the coverage account beside the
  headline is derived **from the catalog**, one direction, by
  `generation/coverage.py::coverage_account`. Expected outputs are written in this vocabulary —
  `all_satisfied` was renamed, not redefined, and a stale reader refuses it by name.
- **[INHERITED: rulings-20260812.md L2-1]** The feasibility denominator is **applicable asserted
  gates only**. Descriptive (plain) and requirement-side usages appear in the inventory and never
  in the denominator.
- **[INHERITED: rulings-20260812.md L2-2]** A vacuous asserted gate — an asserted usage whose
  owner has zero occurrences — counts as **missing assessment** and holds the model at partial
  coverage until the model is fixed so the gate attaches, or the usage carries an explicit
  inapplicability disposition. The five part-def guards are exactly this case, which is why SC-1
  demands an explicit outcome for each.
- **[INFERRED]** A single `@inapplicable:` directive that is malformed halts generation at
  `error` **whatever the usage's form**, including a plain one — an Item 2 **[AGENT]** severity
  exception recorded beside an `[INHERITED]` line
  (`.project/completed/20260813_constraint-catalog-totality/spec.md:184-194`; accepted at audit as
  A3/R2, orchestrator-ratified, **not owner-ruled**). Any inapplicability marker the table calls
  for must be authored exactly, and a typo is a hard stop rather than a silent no-op.

### Acceptance and evidence

- **[INHERITED: rulings-20260812.md Q6]** Study defaults on the canonical vocabulary: violated →
  reject; indeterminate → keep-for-boundary; not-assessed → keep-for-boundary; partial coverage →
  keep-for-boundary; fully-covered satisfied → feed-strategy/penalize. Feed-strategy for partial
  coverage requires an explicit, auditable per-study opt-in. Coverage lands in durable case
  records regardless.
- **[INHERITED: epic Item 5 scope 5]** Acceptance runs the derivative through the **real TEAx
  route**: generate, seal, execute, persist, query. At least one physics input is mutated across
  the feasibility boundary and the mutation reaches `reject`.
- **[INHERITED: brief, Item 3 close]** The coordinated TEAx work lives on the **unmerged branch
  `constraint-semantics-item3` at `5b70ae9`** in `/home/reid/1cfe/teax`. The checkout stays on
  that branch for the whole item, and acceptance evidence cites that tip. *(Verify the tip at the
  start of design — this session could not read the TEAx repo state.)*
- **[HARD]** Test invocation is `/home/reid/1cfe/item7-rebuild-venv/bin/python -m pytest`, not
  `uv run` — `uv run` resolves `agentic_mbse` to the wrong checkout. Licensed runs need
  `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a`, and **zero `no live syside license`
  skip lines** is the only valid proof a licensed run really ran.
- **[INHERITED: epic Item 5 SC-7]** Three routes are gated, not one: licensed live, in-place
  snapshot, and relocated snapshot. Exact counts and fingerprints go in `verification.md`.

## Non-Goals

- Changing the constraint syntax of `catf_mfe_model` or `catf_mfe_d5`. Only d5's stale PROVENANCE
  paragraph changes, and nothing else about that fixture's bytes.
- Implementing calculation-definition gate attachment. Item 6 designs that capability and has not
  run; it does not block this item. Affected usages are dispositioned `awaits-capability` in the
  table, not built.
- Inventing tolerance values or intent classes during design or implementation. They come from
  `owner-disposition.md` or the work stops.
- Admitting in-predicate feature chains. Filed as a future capability candidate at the umbrella
  level, not built here.
- Resolving the D-2 versus D-4/SRC-01 self-named-binding conflict. Parked at the umbrella level;
  this item surfaces a collision rather than deciding one.
- Changing BLOCK-halts-generation semantics, the report vocabulary, or the coverage contract.
  Those landed in Items 1–3 and this item consumes them.

## Open Questions / Deferred to design

- **The derivative fixture's name and its integrity check.** Working name `catf_mfe_gated`. The
  d5 byte-reversal check does not transfer to a fixture that deliberately differs; design picks
  the replacement (a provenance-diff manifest was flagged in the umbrella spec).
- **The constraint-definition library's home, contents, and naming.** Whether it lives inside the
  derivative's `library/` or in a shared fixture library, and what beyond `WithinBand` it needs.
  Q4 introduced the library to answer the owner's ergonomics worry about narrow viability bands,
  which is an authoring concern and not a fixture concern — so if the library proves out here,
  whether its forms get published into the authoring guidance is a question this item files for
  Item 7's documentation sync rather than answers. (Item 5 product-lens, item5-F4.)
- **How the nine gates are rewritten in detail.** Six of the nine use a real `==` with no
  tolerance band and seven of the nine block on in-predicate feature chains
  (`.project/research/20260812-101200_constraint-semantics-end-to-end.md` §3). Which become
  derivations, which become bands, and which become one-sided gates follows from the owner's
  intent classes — the rewrite mechanics are design's.
- **Whether authoring the derivative requires model changes beyond constraints** — e.g. typing
  design parts so the five part-def guards attach. The table decides attachment-versus-
  inapplicability; design decides what source edits that implies and how PROVENANCE records them.
- **The shape of the R3 baseline (SC-8).** Which fixture carries the calc-def-only baseline
  (`constraint_domain_satisfy_calc_def` is the measured example), and how it enters
  `tests/fixtures/baseline_outputs/` without churning the other baselines.
- **The mutation's mechanics for SC-5.** Which physics input is mutated, by how much, and where
  the mutation lives (a study config, a candidate record, or an input JSON) so the rejection is
  reproducible.
- **How expected outputs are stored so SC-6 is auditable.** Item 3's precedent —
  `expected-coverage.md` committed before any coverage code existed — is the model to follow;
  design fixes the file layout and the commit-order evidence.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_constraint_semantics_contract.md` (Item 5)
- **Umbrella spec:** `.project/active/constraint-semantics-contract/spec.md`
- **Ruling record:** `.project/active/constraint-semantics-contract/rulings-20260812.md`
  (Q4, Q5, Q6, Q8 and the four post-ruling refinements)
- **Research:** `.project/research/20260812-101200_constraint-semantics-end-to-end.md` §§3, 5–7
- **Fixture provenance:** `tests/fixtures/catf_mfe_d5/PROVENANCE.md` (the paragraph SC-2 corrects)
- **Item 4 limits:** `.project/completed/20260813_constraint-predicate-hardening/verification.md`
  ("Surfaced") and `reason-codes-reconciliation.md` ("Also surfaced")
- **Contract as landed:** `docs/architecture/modeling-assumptions.md` §8 and §9 (ADR-009)
- **Items 2–3 close records:** `.project/completed/20260813_constraint-catalog-totality/` and
  `.project/completed/20260813_constraint-coverage-policy/`
- **Owner disposition table:** `.project/active/catf-constraint-policy-acceptance/owner-disposition.md`
  — **RULED 2026-08-13**; the sole source of intent classes, tolerance values, and deletion
  authority for everything downstream.
- **Product-lens ledger:** `.project/active/catf-constraint-policy-acceptance/product-lens.md`
  — spec-stage gate was **BLOCK** on item5-F1; **resolved 2026-08-13 by owner ruling** (SC-3
  amended to the accounting identity, recorded at SC-3 above). item5-F2..F5 folded into the
  requirements above.
- **Design:** `.project/active/catf-constraint-policy-acceptance/design.md` (to be created)

---

**Next Steps:** The owner check-in is complete (2026-08-13): `owner-disposition.md` is RULED, the
SC-3 amendment is recorded, and the three backlog filings from the ruling are made. Next:
`/_my_design` against the ruled table.
