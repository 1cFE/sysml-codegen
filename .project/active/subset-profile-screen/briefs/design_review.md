Review the design for EXEC-SUBSET-CONTRACT Item 2b, live half: `.project/active/subset-profile-screen/design.md`, against `spec.md` (revision 3), `briefs/align.md`, `product-lens.md`, and the real code in this repo (sysml-codegen, branch `subset-profile-screen`). Agentic-mbse sibling: `/home/reid/src/subset-conformance/agentic-mbse`.

Intent, graded: [OWNER-ratified] the generator's own route alone decides refusal; the screen only reports. [OWNER] RG-1 (accept/refuse changes), RG-2 (String metadata policy), RG-3 (merges, PRs, ADR filing) stay with the owner. [ORCHESTRATOR] the bar is clean, well-factored code: one read-only preparation path both commands call, writes outside it by structure, one report type.

Beyond your normal checklist, weigh these specifically:
1. `assess_screen` does its own second SysIDE load instead of reusing the model `prepare` already loaded. Is that justified by the code, or is it avoidable coupling-avoidance that costs time and risks the two loads seeing different things (the spike found unnamed-element IDs differ between loads)? What would reusing the load cost?
2. Readiness policy for omitted and excluded findings: the design says they don't block readiness. The epic lists "blocking policy for exclusions/omissions" as an open owner decision (agentic-mbse `.project/backlog/epic_executable-subset-contract.md`, "Owner decisions and remaining questions" item 2), and Item 3 shipped an L6 policy for the `generated` target (agentic-mbse `.project/completed/20261020_l6-subset-profile/`). Check whether `check`'s rule matches what L6 shipped, and whether String omissions reporting "ready" steps on RG-2. If the policy needs an owner decision, say so plainly.
3. The changed first failure for a refused model with a symlinked destination: confirm it is not an accept/refuse change.
4. Moving the writers to `cli/emit.py` and updating ~20 tests that patch private functions: is the factoring right, or is there a smaller cut that keeps quality?
5. Exit codes and the `check` CLI shape: consistent with the repo's other commands?

Write `.project/active/subset-profile-screen/design-review.md` with a verdict and must-fix / should-fix points.
