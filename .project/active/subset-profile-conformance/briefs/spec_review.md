# Brief: /_my_spec_review for EXEC-SUBSET-CONTRACT Item 2a

Review `.project/active/subset-profile-conformance/spec.md` (sysml-codegen worktree, branch `subset-conformance`). Source of the work item: agentic-mbse epic at `/home/reid/src/subset-conformance/agentic-mbse/.project/backlog/epic_executable-subset-contract.md` (Items 2, 2a, 2b). Route and owner gates: `briefs/align.md`. Item 1's evidence: `/home/reid/src/subset-conformance/agentic-mbse/.project/completed/20261018_exec-subset-profile/` (especially `evidence/r3-proposal.md`, `evidence/re-estimate.md`). Project rules are in `.claude/rules/`; the product-lens instruction set is at `.claude/scripts/product-lens.md`.

Intent the spec must serve [AGENT] (ratified by owner): prove, independently of the new screen, that the shared subset contract matches what the generator actually does, and make drift fail a test.

Look hardest at:
- Circularity: can any criterion be satisfied by the screen checking itself, or by expectations derived from either side at test time?
- Every R3 row routed to Item 2: is the closing outcome evaluatable, and is anything dropped or quietly widened?
- Gate discipline: does any requirement need a generator behavior change without marking it RG-1? Is the "contract fixes are not RG-1" call sound, given RG-1 covers what the generator accepts/refuses?
- Scope creep into 2b (check CLI, preparation path, snapshots) or Items 3–5; and whether 17–27 days of work is honestly scoped or needs a further cut.
- Provenance grades per capture-fidelity.

Do not edit the spec; write the review artifact. End with `ARTIFACT: <path>`.
