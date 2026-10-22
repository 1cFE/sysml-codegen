Implement EXEC-SUBSET-CONTRACT Item 2b, live half, Phases 0 through 3 of `.project/active/subset-profile-screen/plan.md` (sysml-codegen, branch `subset-profile-screen`). Stop after Phase 3 and report. Agentic-mbse sibling: `/home/reid/src/subset-conformance/agentic-mbse` — do not change it.

Read the plan, `design.md` and `briefs/align.md` first. The SysIDE license key is in `.env`; run licensed suites with it loaded. For CLI commands that call the Claude CLI, redirect output to a file and read it back.

Intent, graded: [OWNER-ratified] the generator's own route alone decides refusal. [OWNER] RG-1/RG-2/RG-3 stay with the owner: if anything you find would change what the generator accepts or refuses, stop and report rather than deciding. [ORCHESTRATOR] Engineering bar: Phases 1-3 are pure moves. Prove each against the Phase 0 byte-identity manifest and refusal records before moving on. Clean modules with clear typed boundaries; no compatibility aliases for moved private functions (tests are updated, as the design says); no dead code left behind.

Commit after each phase, subject leading with what the phase decided or proved, and end each commit message with:
Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Check off the phase in `plan.md` with implementation notes (what changed, deviations, surprises) in the same commit.

Phase 0's two probes check design premises (which sites the writers reach; the real `unresolved_default_kind` value for the String-default case). If either premise is wrong, record it in the plan notes and in your report, and keep going only if Phases 1-3 don't depend on it.
