Audit EXEC-SUBSET-CONTRACT Item 2b, live half (`subset-profile-screen`, sysml-codegen, branch `subset-profile-screen`, base `556cbedf`). Agentic-mbse sibling: `/home/reid/src/subset-conformance/agentic-mbse` (should be unchanged at `e268357f`).

Read `spec.md` (revision 3), `design.md`, `plan.md` with its implementation notes, `briefs/` (what each stage was told) and `evidence/`. Phases 0-9 are implemented. Phase 10 (the readiness rule, D8) is intentionally open, gated on the owner; audit the interim rule (plan A1) as shipped and treat Phase 10 as out of scope, but say what the audit can't certify until it lands.

Intent, graded: [OWNER-ratified] the generator's own route alone decides refusal; the screen only reports. [OWNER] RG-1 (accept/refuse changes), RG-2, RG-3. [ORCHESTRATOR] the bar is clean, well-factored code, not "it runs".

Beyond your normal checks, I want independent verification of:
1. That `generate` accepts and refuses exactly what it did at base: re-run the Phase 0 package-byte and refusal-record comparisons yourself, and confirm the one expected record change (refused model with symlinked destination).
2. That `check` cannot write: by structure (imports) and by the sentinel tests.
3. That nothing after the seal can change `generate`'s exit code.
4. Code quality of `cli/prepare.py`, `cli/emit.py`, `cli/readiness.py`, `subset_screen.py` and the `elaborated_pipeline.py` changes: placeholder code, dead code, leftover aliases, duplicated logic, tests that test mocks rather than behaviour.
5. That each spec success criterion's checked box is actually proven by the named test.
Run the licensed suites (license in `.env`). Write `.project/active/subset-profile-screen/audit.md` with a verdict and findings.
