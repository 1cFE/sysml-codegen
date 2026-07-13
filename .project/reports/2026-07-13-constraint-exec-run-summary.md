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
