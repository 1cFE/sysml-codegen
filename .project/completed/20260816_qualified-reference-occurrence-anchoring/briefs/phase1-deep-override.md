# Brief: Phase 1 / D11 — deep-literal-override authorability learning test

Sent to a `learning_test` stage session by the orchestrator.

## Work item

Plan: `.project/completed/20260816_qualified-reference-occurrence-anchoring/plan.md`, Phase 1, second checkbox.

Create `.project/completed/20260816_qualified-reference-occurrence-anchoring/spike/deep-override-authorability/`
with the same evidence shape as the retained sibling probe at
`spike/bare-discriminator-authorability/`.

**Question:** can a legal authored SysML model produce a **one-segment, `PartUsage`-owned deep
literal redefinition** target — the shape the deep-override lane would need as a kept fixture?

Include the resolver's `plural=True` call in what you exercise, but judge the direct reference
against the scalar policy (design D4 keeps one-segment owner anchoring singular regardless of what
the caller passes).

## Intent this serves (provenance marked)

- `[OWNER-VERBATIM, 2026-08-13]` One modeled source occurrence must become exactly one runtime
  source reaching every and only its bound consumers.
- `[INHERITED: design.md D11]` A corpus census cannot prove this shape impossible. The lane needs
  either a kept affected-shape fixture or a named, dated coverage gap.
- `[AGENT — orchestrator operationalization]` Bounded search. Record the search surface you covered.

## Disposition on a null result — decided, record it

`[OWNER, 2026-08-15]` If no authorable shape is found, **record the gap and stop cleanly** — a
dated `deep override affected-shape coverage unproven` record naming the exact search surface and
result. Do not halt the pipeline; do not edit `spec.md` or `design.md`. The close disposition stays
with the owner.

If you *do* find an authorable affected shape, retain that exact model for promotion to a Phase-2
fixture and say so explicitly.

## Constraints

- Zero edits under `src/` or `tests/`. `git diff -- src/ tests/` must be empty when you finish.
- Licensed environment: `set -a; source ../agentic-mbse/.env; set +a`. An unlicensed skip is not
  evidence.
- Ruff-clean any retained Python.

## Required evidence shape

For every candidate: model source text, exact command, load result, exact leaf element ID, live
owner element ID and metatype, and a conclusion labelled with exactly one of
`candidate falsified` / `affected shape found` / `authorability unproven`.

## Deliverable

`spike/deep-override-authorability/findings.md` plus retained models and driver.
End your final message with `ARTIFACT: <path>`.
