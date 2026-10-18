# Brief: /_my_implement Phase 1 of EXEC-SUBSET-CONTRACT Item 2a

Implement **Phase 1 only** (steps 1.1–1.6) of `.project/active/subset-profile-conformance/plan.md`, then stop and report. Read `design.md` (rev 3) and `spec.md` for the why. Owner gates in `briefs/align.md`.

Repositories:
- sysml-codegen: this worktree, branch `subset-conformance`.
- agentic-mbse: `/home/reid/src/subset-conformance/agentic-mbse`, branch `subset-conformance`. Never touch `/home/reid/src/agentic-mbse` or `/home/reid/src/sysml-codegen` (a concurrent session uses the former; the latter is the owner's main checkout).

Rules for this run:
- Commit at the plan's commit points, on the `subset-conformance` branches only. Never push, never merge, never open PRs. End commit messages with `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`.
- Engineering bar: clean, well-factored code that matches each repo's idioms and a maintainer would keep. No placeholder code, no TODOs standing in for work, no tests that check the screen against itself.
- Never change what the generator accepts or refuses (RG-1); the phase gate's snapshot/oracle checks enforce it. If a step seems to need it, record an RG-1 candidate and continue.
- If a premise of the plan proves false (e.g., a baseline failure is caused by this branch, a carrier can't reach the harness), stop at that point and report rather than working around it.
- Check off plan steps and add implementation notes in `plan.md` as you go.
- Use `uv run` for everything. The SysIDE license key is in each worktree's `.env`.

End with a short report: what landed (commits), the phase-gate results, deviations, and anything for me to decide. End with `ARTIFACT: <path>`.
