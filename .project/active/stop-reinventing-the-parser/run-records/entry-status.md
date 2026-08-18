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
