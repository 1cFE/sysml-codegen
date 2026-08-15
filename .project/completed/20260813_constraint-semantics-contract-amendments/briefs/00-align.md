# Orchestrated run — Align record (Item 1: Contract and Authoring Policy)

**Run**: `/_my_orchestrate .project/backlog/epic_constraint_semantics_contract.md Item 1`
**Date**: 2026-08-12
**Orchestrator**: Claude (fable session), headless stage subagents via `orchestrate-stage.sh`

The owner waived check-ins at invocation ("no need for check-ins"), so this Align is recorded,
not waited on. Anything below that would normally be confirmed live is instead stated as the
reading this run proceeds on; the owner can audit it here.

## Reading of the work

Item 1 publishes one constraint-semantics contract and one authoring rule **before** any
implementation changes the catalog or report. Concretely:

1. A live ADR for the coverage-headline vocabulary change (agent-originated, owner-ratified
   provenance, cited from the product-lens trail).
2. Lifecycle-contract amendments invariant-by-invariant (1, 8/9, 28, 32, 33, 46/46a, 48 +
   affected Appendix C cells), original provenance grades preserved.
3. Frozen requirements companion amendments (LC-E05/E06/E10/E11/E12 at minimum) — forward
   amendments land in the companion per its header.
4. D1–D7 corrections across codegen and agentic-mbse by amendment or deletion; publish the
   blessed assert-with-bindings pattern, the equality-intent taxonomy (R-POL-4), and the
   modeler-owned tolerance rule.
5. Semantic meaning of both report and canonical runtime headline vocabularies — meaning only;
   Item 3 owns concrete schema/code spellings.

The intent this serves (owner-verbatim, rulings-20260812.md): constraints enforce physics so
design search stays viable; sequence is settle semantics → fix docs and model to match → then
test. Item 1 is the "settle semantics + fix docs" leg. Items 2–6 build nothing until this
contract is published.

## Reserved gates

- **Item 5's all-65 disposition table and tolerance sign-off** is the epic's owner checkpoint.
  It is outside Item 1 scope; nothing in this run decides an intent class, tolerance value, or
  inapplicability for any CATF usage.
- Within Item 1 there is no reserved decision. The `[OWNER]` success criterion ("documentation
  is correct before confirmation testing begins") is a sequencing rule this run enforces, not a
  decision to make.
- The surfaced premise conflict in the umbrella spec (lens spec-F6: contract D-2's acceptance
  cell requires a bare self-named actual while D-4/SRC-01 makes that form UNSUPPORTED) stays
  **parked for owner disposition**. Item 1 amendments must not resolve it silently in either
  direction.

## Provenance notes carried into every stage

- The eight rulings Q1–Q8 and four refinements are **[AGENT] (ratified by owner, 2026-08-12)** —
  challengeable by re-deriving, never to be written as owner-originated. Only the two
  owner-verbatim quotes and the two owner-stated needs (modeler-owned tolerances; equality-usage
  instruction) are owner-grade.
- The D1–D7 defective statements are all agent-authored and none owner-corroborated — correction
  is deletion/amendment per capture-fidelity law 3 (no compensating "WE MUST NOT" prose).
- `[HARD]` items checked, none smell inherited: the SysML/KerML plain-vs-asserted semantics are
  clause-cited to the standard, and BLOCK-halts-generation is verified in code
  (`elaborate.py:488`).

## Entry decision

The umbrella spec is reviewed and approved; the epic decomposition is owner-ratified. Problem is
well understood → enter at `spec` for the single item, then spec_review → design →
design_review → plan → implement → audit. Close and pre_pr stay with the owner.
