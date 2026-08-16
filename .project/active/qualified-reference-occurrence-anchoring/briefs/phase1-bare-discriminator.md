# Brief: Phase 1 / D10 — bare-discriminator authorability learning test

Sent to a `learning_test` stage session by the orchestrator.

## Work item

Plan: `.project/active/qualified-reference-occurrence-anchoring/plan.md`, Phase 1, first checkbox.

Extend `.project/active/qualified-reference-occurrence-anchoring/spike/bare-discriminator-authorability/`
into a bounded learning test over the legal SysML scoping/redefinition candidates it names.

**Question:** does a legal authored SysML model exist in which a *bare* (one-segment, unqualified)
reference to a `PartUsage`-owned leaf makes consumer-lineage selection and exact-owner selection land
on **different** occurrences?

## Intent this serves (provenance marked)

- `[OWNER-VERBATIM, 2026-08-13]` The product seeks a design search where engineering design
  parameters can be freely varied and viability and outcomes such as LCOE can be assessed, without
  embedding engineering logic by predetermining free variables and backing into the rest. One
  modeled source occurrence must become exactly one runtime source reaching every and only its
  bound consumers.
- `[INHERITED: design.md D10 / B3]` Approved spec criterion SC8 (`spec.md:128-130`) assumes such a
  topology is authorable. The retained probe falsified the one named candidate. B3 is the design's
  own open bet.
- `[AGENT — orchestrator operationalization]` This is a bounded search, not an impossibility proof.

## Owner-reserved gate — do not decide

`[OWNER, 2026-08-15]` If this search finds no discriminating authored topology, the run **halts for
the owner's ruling**. You must not choose D10 route 2, amend `spec.md` or `design.md`, or write a
gap record. Report the null result with its evidence and stop.

## Constraints

- Zero edits under `src/` or `tests/`. `git diff -- src/ tests/` must be empty when you finish.
- Preserve the existing retained probe (models, `probe.py`, `findings.md`) — extend, don't rewrite.
- Licensed environment: `set -a; source ../agentic-mbse/.env; set +a`. An unlicensed skip is not
  evidence.
- Ruff-clean any retained Python.

## Required evidence shape

For every candidate: the model source text, the exact command, whether it loaded, the exact leaf
element ID, the live owner element ID and metatype, and a conclusion labelled with exactly one of
`candidate falsified` / `affected shape found` / `authorability unproven`.

## Deliverable

Updated `findings.md` under the existing spike directory, plus retained candidate models and driver.
End your final message with `ARTIFACT: <path>`.
