# Brief — stage `spike` (re-establish binding-shape behavior by measurement)

Sent by the orchestrator. Everything the orchestrator states here is `[AGENT]` grade unless it
carries an explicit owner stamp.

## Why you are running

The spec's guidance and migration criteria gate on **measured** behavior of the shipped exact route.
Earlier measurements were taken by work that the owner ordered **REVERTED IN FULL**; the spec's
provenance note rules that those results are *evidence to reproduce*, never settled fact. One
`[HARD]` row is explicitly stamped *measurement pending re-establishment*. Design must not build on
it until you have reproduced it here. Specification text and grammar have already proven
insufficient — the currently published guidance teaches examples the shipped route refuses.

This is a **spike**: throwaway code confirming known assumptions. It settles facts; it ships nothing.

## The question

For each authoring shape below, on the **shipped exact route at codegen HEAD**: which feature does
the bare/authored reference actually land on, and what concrete value or named diagnostic follows?

1. **Self-named** — `in availability = availability`. Expected: refused pre-generation as
   `SI_SELF_BINDING`, as a readiness finding (no output at all), not a warning. Confirm on the
   codegen route **and** confirm what the agentic-mbse validation path does with the same model.
2. **Names differ (D-5)** — `in availability_in = availability`, attribute on the part owning the
   calculation. Expected: the bare reference lands on the outer attribute and its value arrives.
   Prove the value arrives, not merely that generation succeeds.
3. **Path-named (D-7)** — `in driver_cost = driver.cost`, value on a different part. Expected: lands
   on that occurrence's feature.
4. **Owner-qualified (D-6)** — a qualified name landing on the definition-level feature. The
   `[HARD]` row to re-establish: it is refused with `SI_OCCURRENCE_AMBIGUOUS` when the consumer's
   context contains more than one leaf occurrence of the qualifying definition, and it never
   guesses. **Cover the authoring position the earlier probe table did not: inside the part
   definition.** Measure both the one-occurrence and the multi-occurrence case.

## How to work

- Author minimal throwaway fixtures under the scratchpad, not in the tracked fixture tree.
- Use the real shipped entry points (`run_codegen` / the CLI), not internal helpers, so what you
  measure is what the product does.
- The licensed suite needs `SYSIDE_LICENSE_KEY`: `set -a; source /home/reid/1cfe/agentic-mbse/.env;
  set +a`. Without it, license-gated paths skip rather than fail — a green run with no key is not a
  run. Confirm the key loaded before trusting any result.
- Prior evidence you may reproduce against but must not cite as fact:
  `.project/active/source-identity-binding-semantics-spike/authoring-form-table.md` (2026-08-05
  probe table) and the three patches under
  `.project/active/self-binding-replacement/reverted/`.

## What the orchestrator needs back

A table: shape → authored spelling → feature the reference lands on → observed value or named
diagnostic → the exact command and fixture that produced it. Plus, called out separately:

- **Any shape that resolves silently and wrongly.** This is the highest-value finding. Name it
  precisely. Do not fix it and do not expand scope; the spec's disposition rule is that such a form
  is filed unless the repair is small and contained, and that rule is `[AGENT]` grade — so report
  the size of the repair honestly and let the orchestrator make the call.
- **Anything that contradicts the spec's `[HARD]` rows**, especially the `SI_OCCURRENCE_AMBIGUOUS`
  row. Surface it; do not quietly conform your write-up to the spec.

## Hard bounds

- Change **no** tracked source, fixture, model, or document. Findings only.
- Do not migrate fusion-tea and do not touch `/home/reid/1cfe/fusion-tea`.

## Output

Findings under `.project/active/self-binding-replacement/`. End with `ARTIFACT: <path>`.
