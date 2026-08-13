# Orchestration brief — spec stage — CONSTRAINT-SEMANTICS Item 5

You are writing the spec for **Item 5: CATF Derivative and End-to-End Acceptance** of the
CONSTRAINT-SEMANTICS epic. Item home: `.project/active/catf-constraint-policy-acceptance/`.
Write `spec.md` there.

## The work item (from `.project/backlog/epic_constraint_semantics_contract.md`, Item 5)

Boundary authority: **[AGENT] (ratified by owner, 2026-08-12)**. The complete disposition and
tolerance checkpoint is **[NEED carried from spec.md]** and must be decided by the owner before
this item's design.

Objective: turn the richest model into a worked, auditable example of the constraint-semantics
contract and prove that generated feasibility evidence rejects an unphysical candidate through
TEAx.

Scope (inherit from the epic item, do not narrow):

1. Fork a new derivative from `catf_mfe_d5`. Preserve both twins' modeled sources unchanged and
   record the exact source diff and reason for every derivative change in PROVENANCE.
2. Before design, present all 65 usages to the owner: nine instance-reaching gates with intent
   class, target form, and each tolerance; five part-definition guards with typed attachment or
   explicit inapplicability; 51 calculation-definition guards with derive-instead or
   awaits-capability.
3. Add the small reusable constraint-definition library selected in design, including a band form
   such as `WithinBand`, and use bindings-only predicates where a banded cross-check is
   appropriate.
4. Author the derivative and capture expected catalog, report, and study outcomes from the
   approved table before running confirmation tests.
5. After Items 2–4 (all landed), generate, seal, execute, persist, and query the derivative
   through the real TEAx route. Mutate at least one physics input across the boundary and prove
   rejection.
6. Correct the stale `tests/fixtures/catf_mfe_d5/PROVENANCE.md` acceptance paragraph while
   preserving the fixture's role and bytes outside that documentation change.

Out of scope: changing either frozen twin's constraint syntax; implementing calc-def gate
attachment (usages may be `awaits-capability` per the approved table); inventing tolerance values
or intent classes during design or implementation.

The epic item's success criteria are the spec's floor — carry all seven, including: exactly 65
catalog carriers on the derivative; full feasibility coverage over applicable asserted gates;
expected outputs saved before confirmation tests with no reverse-engineering edits; licensed
live, in-place snapshot, relocated snapshot, generation, seal, execution, and TEAx acceptance
gates with exact counts and fingerprints recorded.

## Decisions from the Align checkpoint (orchestrator-recorded, 2026-08-13)

- **[OWNER 2026-08-13, "go"]** The run proceeds as aligned. Reserved gate: the all-65 disposition
  table and every tolerance value are the owner's, at a check-in hosted after the table draft and
  before design. Structure the spec so `owner-disposition.md` is a distinct pre-design artifact.
- **[AGENT, announced at Align, unobjected]** Item 2's residual **R3** folds into this item: the
  calc-def-only package shape gets a real committed baseline here (context:
  `.project/completed/20260813_constraint-catalog-totality/` audit residuals, quoted in the
  epic's Item 2 section).
- **[AGENT]** Execution details this item decides and records: derivative fixture name (umbrella
  spec working name `catf_mfe_gated`), constraint-def library home and naming.
- Item 6 has not run and does not block; the 51 calc-def guards are dispositioned in the table,
  not built.

## Facts the spec must build on (measured, not inferred)

- Item 2 measured `catf_mfe_d5` as **65 usage carriers / 9 reaching / 0 eligible** — all 65 are
  bare `constraint`, zero `assert`. The "9 eligible" phrasing in older docs is a corrected
  premise. Catalog is keyed by `declaration_id`; `CATALOG_SCHEMA_VERSION` is `3.0.0`;
  instance-graph schema is `v3`.
- Item 3 landed the six-state coverage vocabulary (`full_satisfaction`, `partial_coverage`,
  `not_assessed`, violation, indeterminate, unconstrained-by-construction), one-direction
  report-from-catalog derivation, keep-for-boundary default, explicit feed-strategy opt-in, and
  durable coverage in case records. The coordinated TEAx work lives on **unmerged branch
  `constraint-semantics-item3` at `5b70ae9`** in `/home/reid/1cfe/teax`; the checkout must stay
  on that branch; acceptance evidence will cite that tip.
- Item 4's two surfaced limits (required reading before specifying the band form):
  1. **A unit written on a constraint binding is dimensionally inert to the executable profile**
     (`in tol = 0.05 [m];` never reaches `classify_ordering`). A mis-united band is admitted
     silently. The table and review must carry the unit check; the one supported unit-carrying
     in-predicate spelling is `docs/architecture/modeling-assumptions.md` §8 "Authoring a gate
     that carries units".
  2. **A blocked chain's diagnostic location is the usage's line, not the term's** — disambiguate
     by the named reference, not the line.
- The blessed gate shape is bindings-only: `assert constraint g : Def { in formal = <path>; }`,
  predicates over formals only; feature chains in *binding position* are supported; bare
  self-named bindings are UNSUPPORTED (do not author any; if a rewrite seems to need one,
  surface it — the D-2 vs D-4/SRC-01 conflict is parked at the umbrella level and must not be
  resolved silently).
- Equality intent taxonomy (authority: lifecycle contract supported-boundary section; rendered in
  agentic-mbse `docs/patterns/constraints.md`): (1) structural identity → derive; (2) cross-check
  → loose banded validity; (3) feasibility → one-sided; fixed value → input; (4) closure → by
  construction, else band.
- A profile BLOCK on an asserted constraint halts the whole model — migration is atomic per
  model.
- Environment: use `/home/reid/1cfe/item7-rebuild-venv/bin/python -m pytest` (NOT `uv run` — it
  resolves agentic_mbse to the wrong checkout). Licensed runs need
  `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a`; zero `no live syside license` skip
  lines is the only valid license proof.

## Required reading (verify pointers before citing)

- `.project/active/constraint-semantics-contract/spec.md` — umbrella: Modeling policy, Migration/
  fixtures/defects, CATF success criterion.
- `.project/active/constraint-semantics-contract/rulings-20260812.md` — Q4, Q5, Q6, Q8 and the
  four post-ruling refinements (esp. L3-1/L3-3 all-65 table).
- `.project/research/20260812-101200_constraint-semantics-end-to-end.md` §§3, 5–7 (the
  nine-constraint table and census).
- `tests/fixtures/catf_mfe_d5/PROVENANCE.md`.
- `.project/completed/20260813_constraint-predicate-hardening/verification.md` ("Surfaced") and
  `reason-codes-reconciliation.md` ("Also surfaced").
- `docs/architecture/modeling-assumptions.md` §8 and §9 (ADR-009).
- Items 2–3 close records in `.project/completed/20260813_constraint-catalog-totality/` and
  `20260813_constraint-coverage-policy/` for the catalog/report contracts as landed.

## Provenance discipline

Grade every requirement you write. Owner-originated payloads keep their quotes; the eight rulings
stay `[AGENT] (ratified by owner, 2026-08-12)`; epic-inherited obligations are
`[INHERITED: epic_constraint_semantics_contract.md Item 5]` or the umbrella spec. Do not promote
this brief's `[AGENT]` items to owner grade. Tolerance values and intent classes must appear in
the spec only as *owner-gated placeholders* — the table supplies them later.

## What good looks like

A tired engineer reads the spec once and knows: what the derivative is, what the owner must
decide and when, what evidence gets captured before tests, what the acceptance gates are, and
what is out of scope. Keep it lean; the epic item already did the shaping. End your final message
with `ARTIFACT: <path>` per the spec command's contract.
