# Stage brief — spec_review (Item 1: Contract and Authoring Policy)

Review target: `.project/active/constraint-semantics-contract-amendments/spec.md` — the item
spec for CONSTRAINT-SEMANTICS epic Item 1 (documentation/contract-amendment item, no code).

## Authorities to review against

- `.project/backlog/epic_constraint_semantics_contract.md` — Item 1 section (scope, out of
  scope, success criteria; boundary is [AGENT] ratified by owner 2026-08-12).
- `.project/active/constraint-semantics-contract/spec.md` — the approved umbrella behavioral
  contract this item operationalizes.
- `.project/active/constraint-semantics-contract/rulings-20260812.md` — Q1–Q8 + refinements
  with provenance grades.
- `.project/research/20260812-101200_constraint-semantics-end-to-end.md` §7 — D1–D7 register.
- `.project/active/constraint-semantics-contract/product-lens.md` — spec-F1/F2/F3 obligations.
- `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md` and
  `.project/concepts/constraint-execution-lifecycle-requirements.md` — the documents the item
  amends; check the spec's amendment list against what those documents actually say (invariant
  numbers, LC-E numbers, Appendix C cell names).

## Review pressure to apply (beyond your command's own checklist)

1. **Amendment-set completeness and accuracy.** Does the spec's invariant-by-invariant list
   match the actual contract text (right invariant numbers, right current claims)? Is anything
   in the umbrella spec's "Contract amendment obligations" missing?
2. **Provenance fidelity.** The rulings are [AGENT] (ratified by owner); only the two verbatim
   quotes + tolerance need + equality-instruction need + doc-before-testing sequence are
   owner-grade. Flag any spot where the spec (or an amendment it mandates) would present an
   agent ruling as owner-originated, or would re-grade an amended statement.
3. **Boundary leaks.** Item 1 owns meaning; Item 3 owns token spellings/schema/code; Item 2
   owns the totality gate and the REQ-EXT-09/REQ-CL-04 re-grade; Item 6 owns calc-def design.
   Flag any requirement that quietly drags implementation into this item.
4. **The parked premise conflict** (contract D-2 acceptance cell vs D-4/SRC-01): the spec must
   not resolve it in either direction. Verify its non-goal actually holds against the amendment
   list (e.g. does any listed invariant amendment touch those statements?).
5. **Testability of "no remaining statement that plain/require is enforced"** — is the success
   criterion checkable (grep-able sweep + the named D1–D7 locations), or vague?

## Verified facts from the orchestrator (your session may be sandboxed from the companion repo)

The orchestrator verified these in `/home/reid/1cfe/agentic-mbse-item7-rebuild` (branch
`item7-rebuild`, clean tree) on 2026-08-12, so do not count their unverifiability against the
spec — but do check the spec records them as design-verify obligations:

- D3: `docs/subtype-enumeration-decision-table.md` line 24 — row 1 rationale says "`assert`
  (`AssertConstraintUsage`) and `require`/plain are executable constraint usages (lowered under
  the profile)".
- D4: `docs/patterns/constraints.md` ~lines 192–199 — "WRONG: Not recognized as
  ConstraintUsage!" / "Error: Parser does not create proper AST node without prefix."
- D5: `claude/agents/sysml-expert.md` line 124 — `require constraint { system.flowRate >=
  requiredFlow }` taught inside a requirement pattern; `docs/patterns/semantic-operators.md`
  ~505 — section "Correct: Assert/require prefix" teaches them as equal alternatives.
- The companion has `docs/patterns/adr002-calculations.md` (ADR-with-file precedent lives in
  the companion, not codegen).

## Process

Work synchronously: never pause for background agents, never schedule a check-back — finish the
review artifact this turn. Write the review to
`.project/active/constraint-semantics-contract-amendments/spec-review.md` with a verdict
(Approve / Revise) and findings ordered by severity, each with the exact spec text it targets.
End with `ARTIFACT: <path>`.
