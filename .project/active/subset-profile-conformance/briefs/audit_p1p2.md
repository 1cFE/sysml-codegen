# Brief: /_my_audit of EXEC-SUBSET-CONTRACT Item 2a, Phases 1–2 (mid-run)

Audit Phases 1 and 2 of `.project/active/subset-profile-conformance/plan.md` against `spec.md` and `design.md` (rev 3). Phases 3–7 are not done; audit only what Phases 1–2 claim. This is a mid-run audit: the point is to catch weak foundations before groups C–E build on them.

Code: sysml-codegen this worktree, branch `subset-conformance` (base `b5663c07`); agentic-mbse `/home/reid/src/subset-conformance/agentic-mbse`, branch `subset-conformance` (rebased onto agentic-mbse `main` with Item 4, PR #31). Diff each against its base.

Look hardest at:
- **Non-circularity in the code, not the docs.** Can any agreement, mutation or citation test pass with the screen checking itself, or with stored answers regenerated from either side? Does the generator half truly run with the screen made to raise?
- **Mutation tests that can't fail.** Pick several site and shape mutations and confirm, by actually running a disabled detector, that a test goes red. Check the 4 unwitnessed sites' "fails if reached" guards are real.
- **Reason carrier through the live route** (the reach test): does it cover every converter branch?
- **Accept/refuse unchanged**: snapshot byte-identity and oracle claims; verify independently.
- **Code quality**: well-factored, idiomatic, no dead code, placeholders or TODOs standing in for work; `GenerationCode` (20 members, mandatory on every `CodeGenerationError`) is a clean change.
- Deleted agentic-mbse tests and fixtures: is the screen still tested on real models in agentic-mbse?

Run the suites yourself (agentic-mbse needs `uv sync --all-extras`; licenses are in each `.env`). Compare failures to `evidence/baseline.md` by test ID. Write the audit artifact; do not fix code. End with `ARTIFACT: <path>`.
