# Brief: /_my_implement Phase 5 of EXEC-SUBSET-CONTRACT Item 2a

Implement **Phase 5** (group E head: R3-row site reasons and head E4) of `.project/active/subset-profile-conformance/plan.md`, including the orchestrator calls already recorded in the plan notes (attempt shared rules for anonymous declarations codegen must index and for ES-002's broad shape; else reproduced gaps with exact boundaries in `r3-closure.md`). Then evaluate the **group E split trigger** at P5's close exactly as the plan states it, record the count and the verdict in the plan, and stop and report. Do not start Phase 6. Read `design.md` (rev 3), `spec.md`, `evidence/r3-closure.md`, `rg1-recommendations.md`; owner gates in `briefs/align.md`.

## Also in this phase (commit separately)

- **File two sysml-codegen backlog rows** in `.project/backlog/BACKLOG.md`, owner Reid Westwood, each citing its pinning case:
  1. The calc usage with its own result expression also loses its input binding (`in v = x`); suspected lazy-iterator exhaustion in `_collect_bound_members` (`elaboration/elaborate.py`). State it as unconfirmed. Make sure a case pins today's output so a fix is visible.
  2. RG1-8: a member named with a Python keyword becomes a manual stub because two name-cleaning functions disagree.
  Write them as decision records, not instructions (capture-fidelity law 3).
- The `.claude/agents` kerml-expert link in this worktree is broken; leave it (it is tracked repo content), but note it in the plan for the owner.

Repositories, rules and gate: as in `briefs/implement_p2.md` (subset-conformance branches only; never push/merge; no RG-1 changes; stop and report on a false premise; check off and annotate `plan.md`; agentic-mbse baseline is the 5-ID all-extras set; check whether either `main` moved and rebase per the gate).

End with a short report: commits, phase-gate results, split-trigger count and verdict, deviations, decisions for me. End with `ARTIFACT: <path>`.
