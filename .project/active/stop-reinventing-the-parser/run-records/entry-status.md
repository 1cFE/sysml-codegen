# Orchestrated Run — Entry Status Record

**Run started:** 2026-08-17
**Orchestrator:** Claude (Fable), `/_my_orchestrate` session
**Reserved gates (owner-confirmed at Align):** stop-rule trips halt to owner; close/`pre_pr` are
owner's; nothing pushed to any remote. Product-lens append at green `C_prod` is delegated.

## Original user checkouts (must retain these digests at every phase boundary)

| Checkout | Branch | HEAD | `status --porcelain` sha256 |
|---|---|---|---|
| `/home/reid/1cfe/sysml-codegen` | `stop-reinventing-the-parser` | `2f391fe143d4936dbd995346ae2e421362a29154` | `e3b0c442…7852b855` (empty) |
| `/home/reid/1cfe/agentic-mbse` | `self-binding-replacement` | `fcee56d6cee3828b6f3b7f29a9e684aa03b03bbb` | `e3b0c442…7852b855` (empty) |

The docs checkout (`/home/reid/1cfe/sysml-codegen`) receives orchestration commits only: briefs,
run records, and plan.md phase-completion updates. Its working tree must stay clean between them.
HEAD advances with those commits; the digest rule applies to tracked-work status, not HEAD.

## Dedicated implementation worktrees (fresh, this run)

| Worktree | Branch | Rooted at |
|---|---|---|
| `/tmp/stop-parser-rev2/worktrees/sysml-codegen` | `stop-parser-impl-r2` | `C_base` `78a9beb956f9b5a517c08836b067f0cb0dc4ccc6` |
| `/tmp/stop-parser-rev2/worktrees/agentic-mbse` | `stop-parser-evidence-r2` | `A_base` `2171016d3e3e0805525aa4cf787c55c6293dd00c` |

Both verified clean (`status --porcelain` empty) immediately after creation.

## Phase 4 boundary (2026-08-18)

Codegen implementation advanced from the Phase 3 close `1451615` to production candidate
`e5f73e6cff653f5b6a0c3861c0d3d5cd5b2544da`. Agentic stayed read-only at
`3f8bd587af40f05b929dd56645901dada7daea37`. Both dedicated worktrees were clean at the boundary.
The docs checkout advanced only through Phase 4 briefs and project records.

Phase 4's fresh source extraction is `/tmp/stop-parser-rev2/phase4-extraction-r2/`; its declared
source identities and archive hashes live in `artifact-source-inputs.json`. Phase 5 artifact
construction has not started. The parser-work PDF/HTML suite remained retired under the owner's
2026-08-17 instruction.

Prior-attempt worktrees under `/tmp/stop-parser.QVJIIP/` are historical evidence of the failed
candidate. This run never modifies, reuses, or imports from them.

Stage logs: `/tmp/stop-parser-rev2/logs/`.

## Phase 5 pre-work — external pin existence check (2026-08-18, orchestrator)

All three Global Execution Contract external pins verified to exist as commit objects in their
own repositories (handoff open question 4, previously unverified):

| Pin | Commit | Repo | Note |
|---|---|---|---|
| Fusion parent | `824a876e` | `/home/reid/1cfe/fusion-tea` | exists; reachable from `self-binding-replacement` and `stop-parser-verification`; the checkout currently sits on `item8-fusion-embedded-catalog` (a different item) — Phase 5 must build from the pinned commit in a dedicated worktree, never this checkout |
| TEAx | `744745f8` | `/home/reid/1cfe/teax` | exists |
| 1costingfe | `02543850` | `/home/reid/1cfe/1costingfe` | exists |

## Phase 5 checkout-integrity checkpoint (2026-08-18)

The Phase 5 brief asks for before/after status-digest equality across all five source checkouts, but
the original table above recorded entry digests only for Codegen and Agentic. That omission cannot
be repaired retrospectively by treating a final measurement as an entry measurement.

| Checkout | Final branch / HEAD | Final `status --porcelain=v1` SHA-256 | Comparison authority |
|---|---|---|---|
| Codegen docs checkout | `stop-reinventing-the-parser` / docs HEAD before the final Phase 5 record | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | matches recorded empty entry digest before authorized `.project/` edits |
| Agentic user checkout | `self-binding-replacement` / `fcee56d6cee3828b6f3b7f29a9e684aa03b03bbb` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | matches recorded entry digest |
| Fusion user checkout | `item8-fusion-embedded-catalog` / `be1ee7c0c40a092ebe6750f262902501e377bbd0` | `d8a9922b4300ee7bf04f87b8d01fa02846f2253b7ad290ca535b83f3db9bf08a` | no entry digest was recorded; current dirty paths preserved, equality not claimed |
| TEAx user checkout | `main` / `744745f895677f3344b9884627369a6a47ed987f` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | no entry digest was recorded; final tree clean at frozen pin |
| 1costingfe user checkout | `master` / `02543850089be175ea7c28b92a8b2a4184e1637e` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | no entry digest was recorded; final tree clean at frozen pin |

No Phase 5 command wrote, staged, stashed, switched, or reset any of the three external user
checkouts. Fusion work landed only in `/tmp/stop-parser-rev2/worktrees/fusion-tea`; TEAx and
1costingfe were read from dedicated `/tmp/stop-parser-rev2/` sources. The exact equality box stays
open because the missing before-state digests are an evidence gap, not because a final tree was
observed to change.

## Entry-digest residual — Fusion/TEAx/1costingfe (accepted by owner, 2026-08-18)

The table above recorded entry digests only for the two checkouts this run implemented in
(Codegen, Agentic). Phase 5 later consumed three more repositories — `fusion-tea`, `teax`,
`1costingfe` — whose before-state digests were never captured and cannot be reconstructed.
Phase 5's "original checkouts retain their entry digests" validation box is therefore
unsatisfiable for those three, permanently.

**[OWNER] ruling (2026-08-18): accepted as a recorded residual.** Integrity for those three
checkouts rests on run discipline (no stage command wrote to any user checkout; all Phase 5
inputs were `git archive` extractions of the pinned commits `824a876e` / `744745f8` /
`02543850`) and on the committed runner's provenance records, which tie every isolated run to
git objects rather than working trees. `fusion-tea`'s dirty working tree belongs to the owner's
unrelated in-flight item (`item8-fusion-embedded-catalog`) and is outside this run's scope.
