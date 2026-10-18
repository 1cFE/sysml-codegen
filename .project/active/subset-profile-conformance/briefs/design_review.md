# Brief: /_my_design_review for EXEC-SUBSET-CONTRACT Item 2a

Review `.project/active/subset-profile-conformance/design.md` against `spec.md` (with `spec-review.md` Resolutions), `briefs/align.md` (owner gates RG-1..3) and `.claude/rules/`. Sibling agentic-mbse worktree: `/home/reid/src/subset-conformance/agentic-mbse` (Item 1 merged at `ccd57d83`).

Intent [AGENT] (ratified by owner): prove, independently of the new screen, that the shared contract matches what the generator actually does, and make drift fail a test.

Orchestrator decision already taken ([AGENT], 2026-10-18): the design's replacement for spec A2 (no agentic-mbse version bump; `SUBSET_PROFILE_VERSION` pinned via `_upstream_pins.py` per ADR 0016) is accepted, because a bump refuses all 22 committed snapshots and that is 2b's work. Challenge it only if you find concrete harm.

Look hardest at:
- **The moves out of agentic-mbse.** Probe models, the parity seed/normalizer and 441 site-account rows move to codegen and agentic-mbse's copies are deleted, retiring its probe-evidence and parity tests. Does agentic-mbse keep enough test coverage of its own contract code after this? Is the cross-repo citation check (`case:<id>` form-checked in agentic-mbse, existence-checked in codegen) sound, or does it leave a window where agentic-mbse can change a record with nothing failing?
- **Non-circularity in practice**, not just in the spec's words: stored answers, who can rewrite them, and whether the agreement test can be satisfied by regenerating both sides.
- **Code quality and fit**: does it reuse codegen's existing conformance tree and idioms, or invent parallel machinery? Is `SiteReason` plus `extra={"refusal": error}` a clean extension of existing error types?
- **Gate discipline**: anything that changes generator accept/refuse (RG-1) or decides String policy (RG-2).
- **Phasing and the group-E split point.**

Do not edit the design; write the review artifact. End with `ARTIFACT: <path>`.
