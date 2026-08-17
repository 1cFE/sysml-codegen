# Brief — measure the 126 bare expression-side usage-owned references

Sent by the orchestrator. `[AGENT]` grade unless stamped otherwise.

## Why this runs, and why now

The qualified-binding corpus scan
(`.project/research/20260815-140630_qualified-binding-corpus-scan.md`) certified the *qualified*
sites: 256 found, 251 unchanged under owner-aware resolution, 5 changed and all 5 are the intentional
u4–u7 probes. No kept fixture, snapshot, or baseline is affected.

It left one completeness boundary. The agreed repair condition is broader than the defect: **any
one-segment leaf whose resolved owner is a real `PartUsage`** takes the new route. That predicate also
covers **189 bare** direct references. Sixty-three are calculation inputs and already compare equal.
**126 are expression-side consumers — computed attributes, constraints, predicates, expression terms —
whose source/owner relation was recorded but which were never joined to a prospective graph edge.**

Those 126 are your subject. The sequencing matters: this measurement must land **before** the repair
is written, not alongside it. If an edge changes, we need to judge whether that change is a fix or a
regression, and that judgment gets much harder once there is a diff to defend.

## The task

For each of the 126 bare expression-side usage-owned sites, join it to a prospective graph edge and
compare current versus owner-aware, at the level of **exact typed wire edges, not display names**.

Reuse the scan's harness and method so the numbers are directly comparable. In particular keep:

- separate loading per fixture root, matching normal fixture admission;
- exact authored text recovered from CST byte spans;
- the owner-aware simulation only where the resolved owner is a real `PartUsage` — select the exact
  owner's occurrence with the existing occurrence-selection policy, transition to the exact leaf slot
  inside that occurrence, then **follow typed aliases exactly as the binding resolver does**. That
  alias step is not optional: it is what turned 13 apparent CATF changes into 13 false positives in
  the qualified pass, and the same trap is live here.

## What the report must contain

1. **The headline count**: of 126, how many compare equal, how many change, how many could not be
   joined. Unjoinable sites are a result, not an omission — report them with the reason.
2. **Every changed site individually**: file and line, authored text, consumer kind (computed
   attribute / constraint / predicate / expression term), current edge, prospective edge, and your
   judgment of **fix or regression**, with the reasoning. This is the part the decision rests on.
3. **A per-consumer-kind breakdown.** The four kinds have different blast radii and the aggregate
   hides that.
4. **Affected snapshots and baselines**, by name, or an explicit statement that none are.
5. **Which sites should become kept regressions.** The scan already recommends adding alias,
   computed-attribute, constraint-binding and predicate regressions; name the specific sites that
   would carry them, and say plainly if the corpus has no example of some kind — an absence is a
   finding, since the corpus has no qualified usage-owned expression-side example at all.

## Two things to weigh, not to assume

- **The scan offered a narrow alternative** — define the change as "honor an authored qualified
  usage-owned direct reference," carrying authored-form evidence into every shared resolver caller,
  leaving bare forms on today's route. I previously argued that was impossible because the
  qualification part is absent from the abstract syntax (KerML §8.2.3.4). **The scan itself falsifies
  my claim**: it recovered exact authored text from CST byte spans. So the narrow option is available,
  just more plumbing. Your measurement decides which option is worth its cost — say so explicitly.
- **The bare case may be the same defect, not scope creep.** If a bare name resolves to a usage-owned
  redefinition, it denotes that usage's feature by the same KerML §7.3.4.5 argument that settled the
  qualified case. That is an argument, not a measurement. Your edges are the measurement. If they
  contradict it, say so.

## Bounds

- **Measure and report. Change no tracked source, test, fixture, model, or baseline.** Implement no
  repair and propose no patch. The disposition is the owner's.
- Scratch harnesses go in the scratchpad or under `spike/`, and `spike/out/` is gitignored — do not
  commit generated output.
- The license lives in the companion checkout: `set -a; source /home/reid/1cfe/agentic-mbse/.env;
  set +a`. Without it licensed paths **skip rather than fail**, so a green run with no key is not a
  run. Confirm the key is loaded before trusting any number.
- If a result contradicts the corpus scan or anything in this brief, **say so directly**. Several
  conclusions in this item have already been falsified by measurement; another would be useful.

## Output

A research report under `.project/research/`, same shape as the corpus scan so the two read as a
pair. End with `ARTIFACT: <path>`.
