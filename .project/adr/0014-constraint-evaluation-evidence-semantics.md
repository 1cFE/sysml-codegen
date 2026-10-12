---
id: 0014
title: Constraint verdicts are evidence; raised arithmetic is execution failure
date: 2026-10-12
owner: Reid W
status: active
amended_by: []
superseded_by: null
provenance: "[INHERITED: lifecycle evaluation contract and July owner ruling cited below]"
seams: [generation, constraint-evaluation, reporting]
supersedes: null
promoted_to: null
---

## Decision

Generated constraints produce feasibility evidence; a false predicate completes evaluation, and study policy decides what that evidence means for a candidate. Generated arithmetic propagates thrown exceptions instead of converting them into feasibility verdicts; already-produced non-finite operands retain Kleene indeterminate semantics. Compile the positive predicate body once and apply each usage's polarity once during finalization, preserving raw truth and polarity-aware simple margin.

## Why

A divide-by-zero is a failed evaluation, while a correctly evaluated false assertion is evidence about the model. Collapsing those outcomes can make an execution defect look like an infeasible design. Negating the shared body or applying polarity twice also changes raw evidence and can hide which usage failed.

## Authority and provenance

[OWNER, 2026-07-18] The arithmetic ruling is recorded at `aa35f06fb6b3bacfd42c7763a07a4ee4fdaafa57:.project/research/20260718_gap-review-verification.md`, Owner ruling — F1 policy: raised arithmetic is execution failure, never a verdict; generated predicates add no arithmetic guards; a failed constraint yields no completed constraint report. That source records the ruling in paraphrase, not as an owner-verbatim quote. Codegen owns propagation and the emitted contract; runtime normalization remains evaluator-owned.

[AGENT, ratified by owner] Positive-body compilation with separately applied usage polarity is the R-2 decision reconciled in `aa35f06fb6b3bacfd42c7763a07a4ee4fdaafa57:.project/research/20260719-065712_constraint-profile-semantics-and-license-reconciliation.md` and graded by `aa35f06fb6b3bacfd42c7763a07a4ee4fdaafa57:.project/research/20260719-111228_constraint-execution-lifecycle-evidence-census.md`. Ratification does not upgrade its origin. The retained normative authority is `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md`, invariants 6, 29, 43–45, and 52; headline coverage semantics remain `.project/adr/0010-coverage-truth-and-headline-semantics.md`.

## Evidence

`src/sysml_codegen/generation/predicate_compiler.py`; `src/sysml_codegen/templates/constraint_module.py.jinja2`; `tests/unit/test_predicate_compiler.py`; `tests/execution/test_constraint_verdicts_exact_route.py`. This records the emitted evaluation contract, not a new study-policy, compound-margin, or lifecycle-certification promise.
