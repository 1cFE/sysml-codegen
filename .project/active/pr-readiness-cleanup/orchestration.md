# Orchestration: PR-readiness cleanup

**Status:** Implemented and independently audited; ready for human close and pre-PR
**Owner authorization:** 2026-10-08 — “Please $my-orchestrate the rest of the process, starting with a spec-review. use your best judgement to keep this on track and not overdesigned”
**Implementation checkout:** `/tmp/pr-readiness-cleanup-run`, branch `pr-readiness-cleanup`, starting at `6872977541eae935d4be2789f48f723ffea7101b`.

## Routing decisions

- [AGENT] The Codex stage helper failed before creating a stage session: app-server initialization attempted to write read-only state. Logs: `/tmp/pr-readiness-orchestrate-logs/run-spec-review-20261008-075237-3.stderr`. Fresh native agents execute the same skill stages instead.
- [AGENT] Spec review ran fresh and found only SC4b's numerical-channel count. The coordinator corrected it and verified the count; the historical Revise verdict remains with a resolution note.
- [AGENT] A short design records the real evidence-storage, recapture, and immutable-validation choices. Mechanical edits need no architecture expansion. Product/UX shaping is skipped because this is a defined cleanup of existing behavior.
- [AGENT] A persistent phased plan follows design. The owner authorized continuing all phases under coordinator judgment; routine design/plan approval checkpoints are satisfied by that delegation.
- [AGENT] Independent implementation audit is required. Close and post-close pre-PR remain the human boundary under my-orchestrate's default scope.

## Isolation

The original checkout's index and mental-alignment worktree hashes are recorded in `/tmp/pr-readiness-original-state.json`. The isolated clone carries the approved spec/review/research and current tracking inputs, without mental-alignment drafts. Production edits and focused commits happen there; concurrent fusion-tea work remains intact. No source changes precede the durable baseline capture.

## Stage status

- [x] Fresh spec review and localized correction.
- [x] Short design; standalone design review skipped because no architectural/interface change.
- [x] Executable five-phase plan approved under delegated coordinator judgment.
- [x] Baseline and functional regression checks before source changes.
- [x] C1–C10 implementation and final candidate/customer validation.
- [x] Independent audit and correction of material findings; verdict Certify.

## Completion

[AGENT] The independent [audit](audit.md) certifies the bounded cleanup. Archived default tests: 2,207 passed, nine named historical parity gaps, 96 runtime deselections; the separate stock-TEAx lane passes all 96 tests. All 18 current customer generation units are compared, with principal-family runtime, mutation, and handwritten-preservation evidence. Two reproduced consumer-test defects are repaired on the isolated customer branch. The replacement-evidence gate exposed three stale references; their final bounded dispositions preserve the named-proof invariant and pass the unchanged checker policy. Exact candidate identities and evidence bounds remain in [evidence](evidence.md) and the audit.

[AGENT] Local companion/customer branches are preserved in their original repositories without checkout changes. The final codegen branch is imported after this completion record. The original index and all 17 protected mental-alignment draft hashes remain unchanged. Item 8 and the epic retain their own completion authority and open status. Close and post-close pre-PR are the next human-controlled stages.
