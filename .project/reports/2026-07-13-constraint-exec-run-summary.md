# CONSTRAINT-EXEC Orchestrated Run — Close-Out Summary (2026-07-13)

All 15 items implemented, adversarially reviewed, and audit-certified across four repos in one
orchestrated run (~14h wall-clock). Branches: `constraint-exec-epic` in sysml-codegen,
agentic-mbse, teax; fusion-tea acceptance on `main` there. `/_my_close` and PR creation left
to the owner per the run agreement.

## The headline
Modeled limits now execute. `assert constraint` lowers to Kleene-compiled graph modules feeding
an exact-schema report aggregator; verdicts are data beside ordinary outputs; snapshots carry
constraint facts load-bearing; packages seal with verified-on-load contracts; and a crash-safe
study layer (evaluator → store/runner → policy/query/CLI) runs one point or thousands. The IFE
sweep's hand-coded viability rule is deleted.

## The acceptance (owner's eye requested)
**2294/2301 grid classifications match exactly (99.7%).** The 7 divergent rows are exactly the
`eta*gain == 10.0` boundary: the hand rule used strict `>` while the model says `>=` — the
generated assertion is MORE faithful than the rule it replaced. Recorded as met-with-divergence,
never a bare "100%". If you read the Critical Success Factor strictly, this is the one wording
call that is yours: the divergence is the hand rule's bug, surfaced as data per the design's
pre-decided rule. Prepare-once benchmark: ~168× on the real package; 200/200 verdict parity.

## Reserved gates (all decided by you, recorded [OWNER])
Item 7 identity = class-per-assertion (with measured scale evidence); Item 10 entry API =
Shape A instantiated-models-only; Item 11 attempt history = Option A append-only-per-transition.

## Follow-ons registered (BACKLOG, CE-F1..F3)
The first real multi-channel package through the sealed→study path surfaced three integration
gaps (catalog emission shape; single-channel bridge; a hardcoded fixture class in
PreparedEvaluator), bridged consumer-side and documented — each should become real work.

## Final gates (orchestrator-executed)
sysml-codegen 2330/23 + mypy-76-baseline + ruff clean; agentic-mbse 1401/1; teax green except
the 4 known pre-existing failures. Every item's audit closed with executed probes (mutation
RED/GREEN where guards matter), not recorded claims.

## Post-run ratifications (owner session, 2026-07-13)
- **Boundary wording ratified [OWNER]:** "met with recorded divergence — 99.7% + 7
  model-favoring boundary rows" accepted as satisfying the Critical Success Factor; no
  `>`-matched re-run. Cite `findings.md` for the acceptance statement, not the CSV alone —
  the CSV's `match` column is defined as match-or-boundary and reads as a bare 100% standalone.
- **Epic Success Criteria now 9/9** (this summary previously implied all were checked while
  the contracts/study-layer box was open): the 9th box checked [OWNER] with its narrowing
  note retained. CE-F3 is fixed (teax `0d606a4`); CE-F1/F2 remain registered follow-ons.
- **Independent audit of the run's findings:** every sampled claim reproduced exactly —
  `epic_constraint_execution_audit_independent.md`. teax's 4 known failures also now fixed
  (`1b63272`); its suite is fully green (262 passed).
