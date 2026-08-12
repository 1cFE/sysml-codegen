# Stage brief — spec (Item 1: Contract and Authoring Policy)

You are writing the item spec for **Item 1 of the CONSTRAINT-SEMANTICS epic**
(`.project/backlog/epic_constraint_semantics_contract.md`, "Item 1: Contract and Authoring
Policy"). Read that item's section in full — its Scope (5 numbered points), Out of Scope,
Success Criteria, and Required Reading are the item definition. The umbrella behavioral spec
already exists and is approved; your spec operationalizes Item 1 only.

**Deliverable**: `.project/active/constraint-semantics-contract-amendments/spec.md`

## Required reading (in this order)

1. `.project/backlog/epic_constraint_semantics_contract.md` — Item 1 section + Epic Strategy.
2. `.project/active/constraint-semantics-contract/spec.md` — the umbrella contract. Item 1
   publishes its "Contract amendment obligations" and "Modeling policy" sections as durable
   documentation.
3. `.project/active/constraint-semantics-contract/rulings-20260812.md` — the Q1–Q8 rulings and
   L2-1/L2-2/L3-1/L2-3 refinements, with provenance grades.
4. `.project/research/20260812-101200_constraint-semantics-end-to-end.md` §7 — the D1–D7
   contradiction register (file:line for every defective statement).
5. `.project/active/constraint-semantics-contract/product-lens.md` — the spec-F1/F2/F3
   contract-amendment obligations.
6. `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md` — the contract
   being amended (read at least invariants 1, 8/9, 12, 28, 32, 33, 40, 46/46a, 48 and
   Appendix C's structure).
7. `.project/concepts/constraint-execution-lifecycle-requirements.md` — the frozen companion;
   its header defines how forward amendments land (LC-E05/E06/E10/E11/E12 at minimum).

## What Item 1 is (scope, from the epic — boundary [AGENT] ratified by owner 2026-08-12)

1. File the coverage-headline ADR with accurate agent-originated, owner-ratified provenance.
2. Amend the lifecycle contract invariant-by-invariant (1, 8/9, 28, 32, 33, 46/46a, 48 +
   affected Appendix C cells).
3. Amend the frozen requirements companion without changing provenance grades of inherited
   statements.
4. Correct D1–D7 across codegen and agentic-mbse by amendment or deletion. Publish the blessed
   assert-with-bindings pattern, the equality-intent taxonomy (umbrella spec R-POL-4), and the
   modeler-owned tolerance rule.
5. Define the **semantic meaning** of both report and canonical runtime headline vocabularies.
   Item 3 owns concrete schema and code spellings — your spec must draw that line explicitly.

**Out of scope**: catalog/report/projection/policy/fixture implementation; calc-def attachment
design (Item 6); resolving the parked D-2 vs D-4/SRC-01 premise conflict (umbrella spec Open
Questions, lens spec-F6) — amendments must not resolve it silently.

## Success criteria to carry (grades matter — preserve them)

- **[INHERITED: constraint-semantics-contract/spec.md]** live ADR cited from the product-lens
  trail; contract + companion publish the full amendment set with original provenance intact.
- **[INHERITED: research D1–D7]** no remaining statement in either repo that a plain or
  requirement-side constraint is an enforced gate.
- **[NEED carried from spec.md]** authoring guidance explains when equality intent should be
  derived, band-checked, one-sided, fixed as input, or closed by construction.
- **[OWNER]** documentation is correct before confirmation testing begins (sequencing rule).
- Documentation checks and `git diff --check` pass in every touched repository.

## Provenance rules (capture-fidelity — binding on your spec text)

- Q1–Q8 and the refinements are **[AGENT] (ratified by owner, 2026-08-12)** — never write them
  as owner-originated. Owner-grade payloads are only: the two owner-verbatim quotes in
  rulings-20260812.md, the modeler-owned-tolerance need, and the equality-usage-instruction need.
- D1–D7 corrections are deletions/amendments at the defect, not annotations and not
  compensating prohibition prose.
- Amendments to the contract and companion preserve the original provenance grades of the
  statements they amend.

## Environment facts

- Two repos are touched: this worktree (`/home/reid/1cfe/sysml-codegen-item7-rebuild`, branch
  `item7-rebuild`) and the companion (`/home/reid/1cfe/agentic-mbse-item7-rebuild`, branch
  `item7-rebuild`). TEAx is NOT touched by Item 1 (vocabulary meaning only; Item 3 lands code).
- Known doc homes: codegen `docs/architecture/modeling-assumptions.md`,
  `docs/architecture/reference/28-constraint-lowering-and-catalog.md`,
  `docs/architecture/reference/01-extraction.md`; agentic-mbse
  `docs/subtype-enumeration-decision-table.md`, `docs/patterns/constraints.md`,
  `docs/patterns/semantic-operators.md`, `claude/agents/sysml-expert.md`.
- There is no ADR directory in codegen docs. ADR-001/ADR-003 are cited from CLAUDE.md and code
  comments but have no dedicated files; the only ADR with a file is agentic-mbse
  `docs/patterns/adr002-calculations.md`. Where the new ADR lives (and its number) is a
  spec/design decision — pick something consistent with that precedent, record it, don't
  agonize.

If something the umbrella spec settles seems ambiguous, decide per its text and record the
decision in your spec's open-questions section rather than asking; this run is autonomous.
End with `ARTIFACT: <path>`.
