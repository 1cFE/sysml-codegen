# Brief: Phase 2 — durable fixtures, red tests, before-state ledger

Sent to an `implement` stage session by the orchestrator.

## Work item

`plan.md` Phase 2, every checkbox. Read the phase in full — it is the contract, this brief only adds
what Phase 1 settled and what the orchestrator decided.

## Intent this serves (provenance marked)

- `[OWNER-VERBATIM, 2026-08-13]` The product seeks a design search where engineering design
  parameters can be freely varied and viability and outcomes such as LCOE can be assessed, without
  embedding engineering logic by predetermining free variables and backing into the rest. One
  modeled source occurrence must become exactly one runtime source reaching every and only its
  bound consumers.
- `[INHERITED: plan.md Phase 2]` This phase reproduces the defect durably and freezes the
  pre-repair state so no later phase can hide a changed occurrence, node ID, or snapshot identity.

## What Phase 1 settled — treat as established, do not re-derive

**[AGENT — orchestrator, from the two committed learning tests at `d78c42e` and `7673bf9`]**

- **D10: affected shape found.** Route 1 applies on its own terms. SC8 is kept as written and B3 is
  confirmed. No route-2 amendment, no `authored bare discrimination unproven` gap record.
  The promoted bare fixture is
  `spike/bare-discriminator-authorability/c01-alias-parent-scope` — smallest discriminating shape,
  loads with zero errors and zero warnings, keeps the `comp_a`/`comp_b` naming, and its wrong edge
  reads as `14.0` where the model says `6.0`. Promote it under `tests/fixtures/` per the plan's
  "Add the Phase-1 bare/deep fixture only if that phase authorized one" clause — **it is
  authorized.**
- **D11: no affected shape.** The dated `deep override affected-shape coverage unproven` gap is
  already recorded in `spike/deep-override-authorability/findings.md`. **Add no deep-override
  fixture.** Do not re-run that search.

Two retained Phase-1 results you should carry into the test surface:

- `c06` / `c08` are falsified-but-useful **definition-owned guard controls** (owner is a
  `PartDefinition`, so the repaired branch must not activate).
- `c12` (arrayed owner) is a **Phase-3 no-hidden-recovery negative**: exact-owner selection sees two
  occurrences and must raise `SI_OCCURRENCE_AMBIGUOUS` where the shipped resolver silently answers.
  Capture its current silent answer in the before-ledger so Phase 5 can adjudicate the change.

## Orchestrator decisions for this phase (execution detail — record them loudly)

- **[AGENT]** Capture the licensed full-suite baseline **first**, before any fixture is added, and
  keep it in `verification/` as a file — Phase 5 compares against it and must not rely on prose.
  Record exact failures and `-rs` skip reasons verbatim.
- **[AGENT]** The intentional red set is a deliverable, not a failure. Name every red assertion and
  why it is red in your completion notes. A red test that is red for a *fixture syntax* reason is a
  defect in this phase, not evidence — the plan's risk register calls this out.

## Constraints

- Licensed environment: `set -a; source ../agentic-mbse/.env; set +a`. An unlicensed skip is not
  evidence, and a green run with no key is not a full run.
- **Do not touch `src/`.** This phase is tests, fixtures, and verification tooling only. Phase 3
  owns the single production edit.
- Copy the u1–u7 models (including u3b) — copy, never move (D6). Preserve bytes at copy time.
- The corpus verifier must be **self-contained** and must never become a second resolver: it
  captures shipped actuals only. Source text is a site/classification key, never an edge authority.
- Freeze the preexisting tracked-root set so the fixtures you add this phase do not inflate the
  corpus comparison.
- Typed IDs are the assertions everywhere. Never assert on rendered names or display paths.
- Ruff-clean and mypy-clean whatever you add.

## Quality bar

This is not "tests that fail." The conformance file is the durable authority for this item after the
research paths are archived (D6), so it must read as a designed surface: clear case names, one
obligation per test, and the typed oracle visible in the assertion rather than buried in a helper.

## Deliverable

Everything in `plan.md` Phase 2's "Changes Required", with its Validation section run and its results
reported exactly. Fill in the plan's "Phase 2 Completion" notes. End with `ARTIFACT: <path>`.
