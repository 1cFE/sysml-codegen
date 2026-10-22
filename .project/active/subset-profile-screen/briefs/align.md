# Orchestration Align — 2026-10-20

Orchestrator: Claude (Opus 5.5) via `/_my_orchestrate`, entering at spec-review.

## Owner answers

- Q1, which is the authority in `generate`: the generator's own route or the shared contract? Owner: "agreed" to the recommendation that the generator's own route stays the authority and the screen only reports. The spec's `[INFERRED]` line is marked ratified.
- Q2, does anyone need snapshots saved before 2b to keep loading afterwards? Owner: "the only thing to check is the artifacts on our website. but those should be stand-alone". Recorded in the spec as a `[NEED]`.

## Reserved gates (owner decides; the orchestrator parks dependent work)

- RG-1: any change to what the generator accepts or refuses, including making a profile mismatch or a screen refusal stop `generate`.
- RG-2: String metadata policy.
- RG-3: merges, PRs and ADR filing.

Not reserved, because the owner's Q2 answer removed the reason to reserve them: the snapshot format choice and an agentic-mbse version bump. Design decides and records them.

## Assumptions stated to the owner, not objected to

- Moving the three late refusals so they fire before the first write changes when they fire, not what is refused. Not RG-1.
- `check` never calls a model clean while it has a `candidate_refusal` finding.
- If the spikes show snapshot carriage is large, the orchestrator splits it into its own item and reports it.

## Open, not blocking

- Where the "website" lives. No repo under `~/src` was found to hold it. Design must confirm that its artifacts do not load snapshots.
