# Brief: /_my_plan for EXEC-SUBSET-CONTRACT Item 2a

Plan from `.project/active/subset-profile-conformance/design.md` (revision 3, approved for planning after two review rounds) and `spec.md`. Also `spikes/s1/findings.md`, `briefs/align.md` (owner gates RG-1..3). Rules: `.claude/rules/`.

Work spans two repositories:
- sysml-codegen: this worktree, branch `subset-conformance`.
- agentic-mbse: sibling worktree `/home/reid/src/subset-conformance/agentic-mbse`, branch `subset-conformance` (base `ccd57d83`, plus epic commits). A concurrent session works epic Item 4 in `/home/reid/src/agentic-mbse` on branch `positional-binding-check`; never touch that checkout.

What I need from the plan:
- The design's phases (P0 is done: spike S1) as checkbox phases, each independently auditable, with the exact test/command that proves it done, and which repo(s) each step touches.
- Phase ordering that respects the design's dependencies: reasons before the mutation tests that compare them; group E's tail behind the split point with the countable trigger at P5's close.
- Commit points per phase in each repo, so the trail is readable.
- Owner-gate stops: where an RG-1 candidate, RG-2 recommendation or RG-3 staged amendment is produced, the phase records it and continues; nothing in the plan changes generator accept/refuse or decides String policy.
- P1 records the licensed-suite baseline in both repos (the 10 known failures) and determines whether each is pre-existing.
- The G1/G2 `kerml-expert` check and G2 probe placed where they are cheapest.

Decide and record anything open. Do not commit. End with `ARTIFACT: <path>`.
