# Stage brief — audit (Item 1: Contract and Authoring Policy)

Audit the implemented CONSTRAINT-SEMANTICS Item 1 against its own artifacts. Item home:
`.project/active/constraint-semantics-contract-amendments/` (spec.md, design.md, plan.md,
verification.md, both review files with Resolutions).

## What landed (claimed)

Codegen commits `5612ef4` (pre-edit sweep), `90041b7` (definitions home + ADR-009), `8d6d2f3`
(contract amendments incl. invariant 61), `0e98fcc` (companion requirements amendments incl.
LC-E13), `dffc71e` (D1/D2/D2b/D6/D7 + matrix pointer + backlog), `2c9665f` (verification
record). Companion repo `/home/reid/1cfe/agentic-mbse-item7-rebuild` commit `dcb187b`
(authoring guidance + equality policy + ADR-009 cite) — if your sandbox can't read that repo,
audit its half via the verification.md record and write a "Requested live probes" section with
exact commands for the orchestrator to run there.

## Audit focus (beyond your command's checklist)

1. **Success criteria, one by one, against the spec** — including: ADR-009 exists and is cited
   from `.project/active/constraint-semantics-contract/product-lens.md`; the full amendment set
   landed with original provenance grades intact; the sweep discharge in verification.md is
   complete (every S1–S5 hit dispositioned, not just counted); the equality taxonomy published
   at agent grade with the owner NEED at owner grade.
2. **Provenance audit of the amendment texts themselves.** Sample the amended contract
   invariants and companion requirements: does any present an agent ruling as owner-originated,
   re-grade an amended statement, or mark a ruling settled/do-not-relitigate? Is the superseded
   text quoted in each companion amendment note as the design requires?
3. **Boundary compliance**: no TEAx edits; no normative token spellings or report field names
   in any amendment (Item 3's); the parked D-2 vs D-4/SRC-01 statements byte-untouched
   (`git diff 4678cd5..HEAD` over the contract file, checked against those statement spans);
   Python diffs comment/docstring-only (`git show dffc71e -- 'src/*' 'tests/*'` has no
   non-comment changes).
4. **The D5-a deviation** (verification.md): the implementer kept `require constraint` at
   `sysml-expert.md:124` because it sits inside a `requirement def`, adding a semantics
   sentence instead of swapping the form. Judge that reasoning against the umbrella spec's Q7
   (requirements-side forms stay non-executable and visible) — is the kept text now consistent
   with the published rule?
5. **The handed-on residue** (four `all_satisfied` assertions in `tests/execution/`): is the
   hand-off recorded somewhere Item 3 will actually meet it, or only in this item's
   verification.md?
6. **Contradiction sweep**: do the five precedence copies agree (the recorded pairwise check)?
   Does any doc still say plain/require constraints execute (re-run S-greps yourself — they're
   recorded in verification.md)?
7. **Capture-fidelity law 3**: check corrections did not add prohibition prose anchoring future
   readers on the rejected forms.

## Ground rules

- Read-only: git/grep/reads. Do not edit any file; findings go in the audit document.
- `check_doc_distinctness.py` and any command you cannot run: list under "Requested live
  probes" with expected outcomes; the orchestrator executes and appends an addendum.
- Work synchronously — no background agents, no check-backs; finish this turn.

Write `.project/active/constraint-semantics-contract-amendments/audit.md` with a verdict
(Certify / Certify-with-residuals / Needs-work), findings by severity with file:line evidence,
and the verdict in the header. End with `ARTIFACT: <path>`.
