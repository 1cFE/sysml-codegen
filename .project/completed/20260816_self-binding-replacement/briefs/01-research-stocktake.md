# Brief — stage `research` (bounded Item-8 stocktake)

Sent by the orchestrator. Everything the orchestrator states here is `[AGENT]` grade unless it
carries an explicit owner stamp.

## Why you are running

The self-binding-replacement spec (`.project/active/self-binding-replacement/spec.md`, rev 3,
`[OWNER 2026-08-15]` approved) depends on two scope calls it made without full verification, and the
owner ruled the full Item-8 stocktake runs **after** spec approval as a research report that checks
those rows — not before, and not as a repair pass.

## Scope — bounded, ~half a day of work, ZERO repairs

Three deliverables, nothing else:

1. **Scope table.** Each ELABORATE-FIRST epic §C sub-item vs what Items 1 and 7 already delivered.
   Split the result into "test now" and "repair later" halves. Source:
   `.project/backlog/epic_elaborate_first_architecture.md`.
2. **Reconciled document-repair list.** Epic §C item 3 names docs 11/12/13/16/24/25 (six).
   `CLAUDE.md`'s retiring banner names 03/04/05/07/10/11/12/13/17/24/25/28 (twelve). Five overlap
   (11, 12, 13, 24, 25) — a prior note said four and was wrong; verify the overlap yourself rather
   than inheriting either count. Produce one reconciled list with each document's actual state.
3. **Validate the spec's two dependent scope calls:**
   - the restated documentation obligation (`[OWNER 2026-08-15]`: know the right patterns / document
     them / fix the models / detect the wrong one) — confirm the epic was amended at `:70-77` and
     `:495-503` and that nothing else in the tree still governs by the retracted "two valid
     replacement forms" wording;
   - the declared home for the leftover regeneration work,
     `.project/active/elaborator-downstream/` — confirm whether it exists, and if not, say so
     plainly. Do not create it.

## Hard bounds

- **Perform zero repairs.** No document rewrites, no epic edits, no code. You produce a report.
- Do not re-open D-4 through D-7, and do not restate the spec.
- If you find that a premise the spec rests on is false, **surface it loudly in the report** with
  the dependent conclusions named and parked. Do not resolve it in either direction.

## Output

A research report under `.project/research/` per `/_my_research`. End with `ARTIFACT: <path>`.
