# Brief: /_my_implement Phase 6 of EXEC-SUBSET-CONTRACT Item 2a

**Split-trigger ruling** ([AGENT] orchestrator, 2026-10-19; record it in the plan at the P5 split verdict): the split is **not** taken. The trigger was designed as a proxy for group E overrunning its effort. The whole L < H gap (46 vs 53) is 7 head rows no valid model reaches, each recorded as unwitnessed with a fails-if-reached guard. That is a completed disposition, so those rows count toward L: L = H = 53, the tail (94) is under 1.25 × T, and Phase 6 runs as planned.

Implement **Phase 6** (group E tail) of `.project/active/subset-profile-conformance/plan.md`, then stop and report. Do not start Phase 7. Read `design.md` (rev 3), `spec.md`, `evidence/r3-closure.md`; owner gates in `briefs/align.md`.

Repositories, rules and gate: as in `briefs/implement_p2.md` (subset-conformance branches only; never push/merge; no RG-1 changes; stop and report on a false premise; check off and annotate `plan.md`; agentic-mbse baseline is the 5-ID all-extras set; check whether either `main` moved and rebase per the gate). The tail is the least examined part of the estimate: if it grows past the plan's 1.25 × T bound mid-phase, stop and report rather than pushing through.

End with a short report: commits, phase-gate results, deviations, decisions for me. End with `ARTIFACT: <path>`.
