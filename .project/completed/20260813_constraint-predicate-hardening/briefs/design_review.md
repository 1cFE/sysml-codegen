# Brief: design_review stage — CONSTRAINT-SEMANTICS Item 4 (Predicate Defect Hardening)

Orchestrated run (owner-invoked `/_my_orchestrate`, check-ins waived). You are a FRESH
design-review session — you did not write this design. Work synchronously: never pause for
background agents or schedule check-backs; finish the artifact this turn and end with
`ARTIFACT: <path>`.

## Review target

`.project/active/constraint-predicate-hardening/design.md`, against:

- Spec (requirements authority): `.project/active/constraint-predicate-hardening/spec.md`
- Epic scope: `.project/backlog/epic_constraint_semantics_contract.md` Item 4
- Companion-side evidence (your sandbox cannot read the companion repo; the orchestrator
  verified these citations directly):
  `.project/active/constraint-predicate-hardening/probes/companion-evidence.md` — includes
  the P4 verdict (chain segments include the root).
- Rulings: `.project/active/constraint-semantics-contract/rulings-20260812.md` Q4, Q8.

Codegen source under this working directory is readable — check the design's codegen-side
citations against the actual code where a claim is load-bearing.

## What to press on (orchestrator's concerns, not conclusions)

1. **The D1 seam.** Cure at the head of `_expression_references` — is the claim "the
   annotation is nested under the comparison operator, so an entry-level unwrap is a no-op"
   true in the code? Does a head-of-walk unwrap using `_without_unit_annotation` change any
   *other* expression lane's behavior (calc bindings, aggregation terms) beyond the predicate
   lanes — i.e., what else calls `_expression_references`, and is widening the rule's reach
   there safe or a behavior change that needs a stated bound?
2. **The invariant that units survive.** A cure that strips the annotation from the walk must
   not strip it from the profile's dimension checking (spec [HARD]). Is the design's invariant
   2 + probe P2 actually discriminating — would the planned incompatible-unit test fail if the
   unit were silently lost?
3. **The fourth-lane cure (D2).** In-scope by the orchestrator's recorded rule iff it is the
   same rule reaching one more lane. Verify from the code that `_collect_bound_members`
   (`elaborate.py` around 1651) reading the binding un-unwrapped is genuinely the whole
   mechanism, and that curing it cannot change the classification of bindings that are NOT
   unit-annotated literals (e.g. genuine expression sources must stay refused).
4. **Defect B's row-count stability.** One diagnostic per constraint with per-reference
   entries inside — confirm no consumer counts diagnostic rows or parses the detail string in
   a way the new message breaks (`test_elaboration_payload_identity.py:236-266` is claimed to
   need no edit — check that claim).
5. **Determinism.** Dedup key `(reason, construct, message, file, line, column)` and order key
   `(file, line, column, reason, message)` — is anything in those tuples run-dependent
   (absolute paths? column availability when LocationFact is None?), and is the None-location
   case ordered deterministically?
6. **Red-first via strict xfail (D8).** Does this satisfy the spec's "kept failing
   characterizations landed before fixes, demonstrated red first," and does the landing order
   keep both trees green at every commit given the editable-install coupling?

Also apply your own judgment beyond this list. Classify findings must-fix vs advisory.

## Deliverable

`.project/active/constraint-predicate-hardening/design-review.md` with a verdict
(Approve / Revise) in the header. End with `ARTIFACT: <path>`.
