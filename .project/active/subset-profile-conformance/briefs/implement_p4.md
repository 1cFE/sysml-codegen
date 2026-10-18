# Brief: /_my_implement Phase 4 of EXEC-SUBSET-CONTRACT Item 2a

Implement **Phase 4** (group D: silent losses, String, stubs, docs) of `.project/active/subset-profile-conformance/plan.md`, preceded by the items below, then stop and report. Read `design.md` (rev 3), `spec.md`, `audit.md`, `evidence/r3-closure.md`; owner gates in `briefs/align.md`.

## First (commit separately)

1. **agentic-mbse unit test for the occurrence fix.** Phase 3 changed agentic-mbse's occurrence extraction for anonymous assert-by-reference with no agentic-mbse test; only codegen's parity test covers it. With no CI, agentic-mbse's own suite must guard its own code. Add a focused agentic-mbse test (it must fail on the pre-fix code; show that).
2. **Correct the agentic-mbse backlog row** for ambiguous inherited typing (PUSH-DOWN-HIER-PROFILE-AMBIG-INHERITED-ATTR or wherever the "sorted-first" claim lives): codegen refuses the model. Cite the case. One-line amendment, per capture-fidelity (amend, don't accrete).

## Phase 4 notes

- ES-010's unbound String library default generates as an entry point with a null default, so the value never reaches the output. Include it as a silent-loss family with presence/absence evidence and put it in the RG-2 String recommendation. Do not decide the policy.
- G1/G2: run the `kerml-expert` check as the plan places it (two questions, both case models attached) and record the findings and an RG-1 recommendation. No generator change.
- Any omission or stub that looks like it should block is an RG-1 candidate with a recommendation; pin current behavior.

## Orchestrator calls for Phase 5 (record in plan notes now so P5 picks them up)

[AGENT] 2026-10-18: Phase 5 attempts shared rules for (a) anonymous declarations codegen must index (`SI_ID_UNSTABLE`) and (b) ES-002's broad shape (reference into a feature of a calc/item/attribute usage other than a calc output). Each becomes a rule if it can be stated from shared agentic-mbse facts with codegen's indexed-declaration set pinned by cases; otherwise it stays a reproduced gap with its exact boundary written in `r3-closure.md` for Item 5's guidance.

Repositories, rules and gate: as in `briefs/implement_p2.md` (subset-conformance branches only; never push/merge; no RG-1 changes; stop and report on a false premise; check off and annotate `plan.md`; agentic-mbse baseline is the 5-ID all-extras set; check whether either `main` moved and rebase per the gate).

End with a short report: commits, phase-gate results, deviations, decisions for me. End with `ARTIFACT: <path>`.
