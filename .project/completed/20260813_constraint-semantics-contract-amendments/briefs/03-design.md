# Stage brief — design (Item 1: Contract and Authoring Policy)

Design the execution of the approved Item 1 spec:
`.project/active/constraint-semantics-contract-amendments/spec.md` (revised after review;
read `spec-review.md`'s Resolutions section too — the rulings there are binding).

**Deliverable**: `.project/active/constraint-semantics-contract-amendments/design.md`

This is a documentation/contract item — the "design" is the complete amendment plan: exact
target text per amendment, placement decisions, the sweep design, and the verification plan.
Design quality bar: an implementing agent should be able to execute it without re-deriving any
decision, and an auditor should be able to check each amendment against it.

## What design must decide (from the spec's Open Questions + review resolutions)

1. **Amendment drafting, invariant by invariant.** For each target in the spec's contract and
   companion lists: quote the current text, give the amended text (or the "verified
   already-correct" record for guardrail entries), with `(amended 2026-08-12,
   CONSTRAINT-SEMANTICS Item 1)` convention and provenance grades preserved. This is the bulk
   of the design.
2. **ADR-009 placement** inside codegen `docs/architecture/modeling-assumptions.md` (the
   consolidated-ADR precedent, commit eda48f9): new section vs entry in §8. Read the file and
   follow its actual structure. Also decide the companion-side cite (stub next to
   `docs/patterns/adr002-calculations.md` or a cite-in-place).
3. **Equality-instruction authority home**: `.project/concepts/constraint-execution-and-design-space-studies.md`
   vs the lifecycle contract's supported-boundary section — pick the authority, the other cites it.
   Then the agentic-mbse authoring-guidance rendering of it.
4. **Companion amendment presentation** against its copy-and-freeze header.
5. **The sweep**: named search terms (retired test name, `require constraint` taught as a
   check, plain-constraint-enforces claims), both repos, docs + comments/docstrings, and the
   verification.md disposition format.
6. **Per-file edit plan for D1–D7 + the opened class** (exact files, current defect text,
   replacement approach).
7. **The matrix-row pointer** (dated "re-grade pending, CONSTRAINT-SEMANTICS Item 2" addition
   at REQ-EXT-09 — spec ruled this; design writes the exact line and placement).

## Verified companion-repo facts (orchestrator-read 2026-08-12; your session may be sandboxed from that repo)

Repo `/home/reid/1cfe/agentic-mbse-item7-rebuild`, branch `item7-rebuild`, clean tree.

- **D3** — `docs/subtype-enumeration-decision-table.md:24` (row 1, Rationale column):
  "`assert` (`AssertConstraintUsage`) and `require`/plain are executable constraint usages
  (lowered under the profile); `RequirementUsage` + its `satisfy` subtype are requirement-side
  and excluded". The enumeration decision (include_subtypes=True, EXCLUDE RequirementUsage)
  must survive verbatim; substitute the reason (visibility/totality, not executability).
- **D4** — `docs/patterns/constraints.md:190-199`: "### Wrong: Plain constraint block (no
  prefix)" ... "// WRONG: Not recognized as ConstraintUsage!" ... "**Error:** Parser does not
  create proper AST node without prefix." The stated reason is false (parser produces a
  `ConstraintUsage`, classified `plain_usage`; the form gate is why it never executes).
- **D5** — four sites teach `require constraint` as an equal/valid check form:
  - `claude/agents/sysml-expert.md:124` — `require constraint { system.flowRate >= requiredFlow }`
  - `docs/patterns/semantic-operators.md:~503-512` — section "### Correct: Assert/require prefix"
    with "assert constraint TempLimit {  // Creates ConstraintUsage!"
  - `docs/patterns/semantic-operators.md:520` — "- `require constraint` - Preconditions that
    must be satisfied"
  - `docs/patterns/semantic-operators.md:545` — "-> Use `assert constraint` or `require
    constraint` (with prefix!)"
  - plus `docs/patterns/syntax-reference.md:185` — "- `require constraint` - Precondition"
    (context decides whether this one is defective or a legitimate requirement-side syntax
    listing; design rules it and records the ruling).
- **ADR precedent**: the companion's only ADR file is `docs/patterns/adr002-calculations.md`.
- **Doc-check surface**: the companion has NO dedicated doc-check script — `scripts/` is corpus
  tooling (benchmark_corpus.py, generate_index.py, …). The spec's "equivalent documentation
  checks in the companion" resolves to whatever design specifies (at minimum
  `git diff --check`; say what else, e.g. the docs-referencing tests if any exist).
- Note: `docs/patterns/constraints.md:25-41` carries the CORRECT four-outcome story (research
  register calls it authority-side) — the D4 fix must stay consistent with it.

## Constraints

- Provenance rules from the spec are binding: rulings stay [AGENT] (ratified by owner,
  2026-08-12); amendments never re-grade the statements they amend; corrections delete/rewrite,
  never annotate or add prohibition prose.
- The parked D-2 vs D-4/SRC-01 conflict: no amendment may touch either statement.
- Item 1/Item 3 boundary: no normative token spellings or report field names.
- Work synchronously — never pause for background agents or schedule check-backs; finish
  design.md this turn. End with `ARTIFACT: <path>`.
