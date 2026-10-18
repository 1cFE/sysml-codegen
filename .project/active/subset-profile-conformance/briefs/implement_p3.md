# Brief: /_my_implement Phase 3 of EXEC-SUBSET-CONTRACT Item 2a

Implement **Phase 3** of `.project/active/subset-profile-conformance/plan.md`, preceded by the mid-run audit fixes below, then stop and report. Read `audit.md` (mid-run, Phases 1–2), `design.md` (rev 3), `spec.md`; owner gates in `briefs/align.md`.

## First: audit fixes (land and commit before Phase 3 work)

1. **Blocker audit-p12 (B6).** Add a licensed codegen test that the live screen answer equals the stored screen answer for every case, so codegen's suite (the pre-merge gate) catches evaluator/extractor changes. Also compute the screen mutation test's "before" from an unmutated live run, not from `case.json`. Prove it: switch off one screen recognizer (e.g. `part-multiplicity/range`) and show the codegen suite goes red; record the command and result in the plan notes. Then restore.
2. **Reach test advisory.** Give the `ExpressionInventoryError` witness a reason distinct from the catch-all branch, so removing that converter fails the test. Prove it the same way.
3. **Stale text**: `evidence/versioning.md`, the agentic-mbse test docstring and the plan status line the audit names.
4. **Disagreement `owner` field**: name a person/role (the owner) or rename the field to what it holds; pick the honest one and record why.

## Then Phase 3

Also include this orchestrator call ([AGENT], 2026-10-18): fix agentic-mbse's occurrence-extraction copy so the anonymous assert-by-reference (`assert positive;`) matches codegen's occurrence index (no `SI_ID_UNSTABLE`), then package it as a case. No parity exception. This is agentic-mbse's mirror, not the generator, so it is not RG-1. And handle the three disagreeing spellings Phase 2 handed you (`assert constraint bare;`, `Constraints::ConstraintCheck`-typed constraint, mixed-unit sum): decide per Known Requirements → Gates (narrow the contract by default; `kerml-expert` + recorded disagreement + RG-1 candidate if the generator's behavior looks semantically wrong).

Repositories, rules and gate: as in `briefs/implement_p2.md` (subset-conformance branches only; never push/merge; no RG-1 changes; stop and report on a false premise; check off and annotate `plan.md`; agentic-mbse baseline is the 5-ID all-extras set). Before closing, check whether agentic-mbse `main` or sysml-codegen `main` moved and rebase per the phase gate if needed.

End with a short report: commits, phase-gate results, deviations, decisions for me. End with `ARTIFACT: <path>`.
