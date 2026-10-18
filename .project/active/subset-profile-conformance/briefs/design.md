# Brief: /_my_design for EXEC-SUBSET-CONTRACT Item 2a

Design from `.project/active/subset-profile-conformance/spec.md` (sysml-codegen worktree, branch `subset-conformance`; sibling agentic-mbse worktree at `/home/reid/src/subset-conformance/agentic-mbse`, branch `subset-conformance`, base = Item 1 merge `ccd57d83`). Also read `spec-review.md` (with its Resolutions), `product-lens.md`, `briefs/align.md` (owner gates RG-1..3). Rules: `.claude/rules/`.

Intent [AGENT] (ratified by owner): prove, independently of the new screen, that the shared contract matches what the generator actually does, and make drift fail a test.

What I expect the design to settle well:
- **Every "Deferred to design" question in the spec**, each with a decision and its reasoning: the disagreement-record form, expectation-file form, how agentic-mbse records cite sysml-codegen cases (the loader can't check a cross-repo citation), the agentic-mbse version bump/publish, `run_codegen` vs direct stage calls, mutation mechanics.
- **One source of truth.** The product-lens warned about hand-synced duplicates (Item 1's 80 probes vs the new corpus; a frozen copy of the site account). Design so each fact lives once and the others derive or check against it.
- **Fit the codebase.** Read the existing `tests/conformance/` tree and the elaboration/projection entry points before inventing harness code; reuse what is there. Match codegen's test idioms. The bar is clean, well-factored code a maintainer would keep, not a pile of one-off scripts.
- **Phaseable.** Groups A–F should map to design sections the plan can turn into independently auditable phases, with group E's tail behind an explicit split point.
- **Gate discipline.** Anything that needs a generator accept/refuse change is RG-1: design the pin-current-behavior test and the candidate record, not the fix. String policy is RG-2: design the fixtures and where the recommendation lands.

If a key assumption about generator or SysIDE behavior is unverified and expensive to get wrong, say so and propose a spike instead of building on it. Decide and record anything open; ask me only what genuinely blocks. Do not commit. End with `ARTIFACT: <path>`.
