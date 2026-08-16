# Brief: Phase 4 — public mutation, strict/lenient, and snapshot routes

Sent to an `implement` stage session by the orchestrator.

## Work item

`plan.md` Phase 4, every checkbox. The plan is the contract.

The repair landed in Phase 3 (`98970c9`). This phase proves the repaired **internal** edge is the
same source that **public generation** and **snapshot round trips** actually see — and exposes any
stale committed snapshot before recapture.

## Intent this serves (provenance marked)

- `[OWNER-VERBATIM, 2026-08-13]` The product seeks a design search where engineering design
  parameters can be freely varied and viability and outcomes such as LCOE can be assessed, without
  embedding engineering logic by predetermining free variables and backing into the rest.
- `[AGENT — orchestrator]` That promise is only kept if a mutation of one modeled source reaches
  **every and only** its bound consumers on the route a real user runs, not merely inside the
  elaborator. A green internal test with a broken public route would fail the owner's promise while
  passing this item's unit oracle. That is what this phase exists to catch.

## What earlier phases established — do not re-derive

**[AGENT — orchestrator, from `85f598a` and `98970c9`]**

- `tests/fixtures/usage_owned_reference_consumers` carries one named source `plant.comp_a.length`
  (3.0) read by **seven** consumers inside the sibling `comp_b` (7.0), across all six lanes. After
  the repair all seven anchor on `comp_a`.
- Occurrence wire IDs and every node ID compare equal for the 13 promoted roots captured with
  identity. The 140 frozen corpus roots omitted identity and therefore do not support the original
  153-root claim. Snapshot inventory at Phase 2: **23 tracked, 0 stale**.
- The corpus changed at exactly 5 sites, all predicted.
- The arrayed-owner negative now refuses with `SI_OCCURRENCE_AMBIGUOUS`.

## Orchestrator decisions for this phase (execution detail — record loudly)

- **[AGENT]** Snapshot recapture is **not** an owner-reserved gate; the owner explicitly declined to
  reserve it. You may recapture, but only under the plan's D9 discipline: run the live-versus-
  committed assessment **first**, retain the exact stale typed-edge comparison as evidence, and then
  recapture **only** the classified fixture. Unconditional or convenience recapture is a defect.
- **[AGENT]** Do not enroll the new fixtures in the committed v6 batch just to make a round-trip
  test pass (D9). Use the temporary capture/relocation route.

## Constraints

- Licensed environment: `set -a; source ../agentic-mbse/.env; set +a`. **No license-related skip is
  acceptable in this phase's results** — the plan says so explicitly.
- **Do not touch `src/`.** The repair is done. If a public or codec route appears to need a
  production change, that is a premise conflict: stop and report it.
- Compare the **full decoded graph and raw alias targets**, not only `semantic_edges()` — the plan
  calls this out because `semantic_edges()` omits raw alias targets (D8).
- Keep the strict/lenient owner-resolution controls free of unrelated readiness findings, and test
  `_finish_readiness`'s earlier strict halt separately.
- Typed identity makes every semantic decision. Projected and generated **names** are checked only
  as public-compatibility output, never as the oracle.
- Ruff and mypy clean on what you touch.

## Quality bar

`[AGENT — orchestrator]` The public-mutation assertion must be *every and only* — a test that proves
the four intended consumers moved but would not notice a fifth unintended one is not the test this
phase needs.

## Deliverable

Phase 4's "Changes Required" and full "Validation" section, results reported exactly, including both
manual checks. Fill in the plan's "Phase 4 Completion" notes. End with `ARTIFACT: <path>`.
