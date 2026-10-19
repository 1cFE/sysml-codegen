# Brief: /_my_implement Phase 7 of EXEC-SUBSET-CONTRACT Item 2a

Implement **Phase 7** (group F, rescan, receipt, final checks) of `.project/active/subset-profile-conformance/plan.md`, then stop and report. This is the last implementation phase. Read `design.md` (rev 3), `spec.md`, `evidence/r3-closure.md`, `rg1-recommendations.md`, `rg2-string-policy.md`; owner gates in `briefs/align.md`.

## Orchestrator rulings on Phase 6's questions ([AGENT], 2026-10-19; record in the plan)

1. The completeness test accepting a public row with either a witness or an "unwitnessed" record (with its fails-if-reached guard) is accepted; it matches the design.
2. File a sysml-codegen backlog row, owner Reid Westwood, marked unconfirmed: the registry may deduplicate calc modules by bare calc def name (`generation/registry.py`, `_registry_class_entries`), so two same-named calc defs in different packages may register one class. Phrase it as a decision record. Probing it is not in scope.
3. File a backlog row for the `SI_TYPE_INVALID` message printing `syside.core.QualifiedName([...])`. Not fixed in 2a.

## Notes

- dc3 is at `/home/reid/src/dc3` and is **read-only**: export the pinned revisions (`808464df…`, `60b44d53…`) into isolated temp trees per the epic's evidence rules; never modify or check out in the dc3 checkout.
- The receipt (`codegen_gate.json`) and its test land here, from a gate run at the final revisions of both repos. Before that run, check whether either `main` moved and rebase per the phase gate, so the receipt is taken on the tree that will merge.
- Final checks: compare both licensed suites by test ID with `evidence/baseline.md`; `evidence/repository-checks.md` names every skip and every check not run.
- Update each repo's `.project/CURRENT_WORK.md` to state where 2a stands: implemented, awaiting audit; owner gates RG-1 (11 candidates), RG-2 (String policy) and RG-3 (staged ADR 0001 / ADR 0012 / ADR 0016 / P-0001 amendments) pending.

Repositories and rules: as in `briefs/implement_p2.md` (subset-conformance branches only; never push/merge; no RG-1 changes; stop and report on a false premise; check off and annotate `plan.md`; agentic-mbse baseline is the 5-ID all-extras set).

End with a short report: commits, final-check results, the dc3 rerun outcome against the matrix, deviations, decisions for me. End with `ARTIFACT: <path>`.
