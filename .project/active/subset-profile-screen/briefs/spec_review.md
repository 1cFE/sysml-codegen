Work item: EXEC-SUBSET-CONTRACT Item 2b, `subset-profile-screen`, in sysml-codegen (this repo, branch `subset-profile-screen`).
Spec to review: `.project/active/subset-profile-screen/spec.md`. Product-lens ledger: `.project/active/subset-profile-screen/product-lens.md`. Owner answers at Align: `.project/active/subset-profile-screen/briefs/align.md`.
Epic: the agentic-mbse sibling worktree `/home/reid/src/subset-conformance/agentic-mbse`, `.project/backlog/epic_executable-subset-contract.md`, section "Item 2b" plus Design principles, Success Criteria, Epic Strategy and Risks. Item 2a's archived artifacts: `git show c381fb00:.project/active/subset-profile-conformance/<file>` in this repo.

Intent (what this item is for), grades marked:
- [OWNER, ratified 2026-10-20] The generator's own route stays the only thing that decides whether `generate` and `check` refuse. The shared screen only reports findings. This resolves a tension in the epic: its text (2a scope 1, principle 3, the Epic Strategy line "keep temporary skew fail-closed") reads as though the screen would decide in `generate`, but the owner's RG-1 gate reserves any accept/refuse change. Check the spec is consistent with this everywhere, including the epic's "fail-closed" skew wording.
- [OWNER, 2026-10-20] Snapshots saved before 2b don't need to keep loading; only the artifacts on the owner's website need checking, and they "should be stand-alone". The epic's "supported historical snapshots" / "supported upgrades" criteria must be reconciled with this. Check the spec says what "supported" now means.
- [ORCHESTRATOR inference] The modeler's goal: learn, before anything is written, every reason the model won't generate, from a live model or a snapshot, with no change to what the generator accepts.
- Owner gates RG-1/RG-2/RG-3 [OWNER 2026-10-18] stand.

Specific things I want the review to weigh, beyond your normal checklist:
1. The spec-F1 BLOCK in the product-lens ledger was cleared by the spec's own author. Confirm independently whether the rescoping actually clears it.
2. Are the success criteria testable as written, and are any of them really design decisions in disguise, or vice versa?
3. Scope size: the epic estimates 6–10 engineer-days and calls it the least certain number. Is the spec's scope (shared preparation refactor, render-before-write, `check` CLI, snapshot authority, skew in two directions) one item, or should snapshot authority be split?
4. Is "a refused `generate` leaves its destination as it found it" a change to what `generate` refuses (RG-1) or only to when? Judge it.

Write your review to `.project/active/subset-profile-screen/spec-review.md`. Do not edit the spec yourself; list must-fix and should-fix points.
