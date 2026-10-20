The snapshot spike (`spike-snapshot/FINDINGS.md`) fired the spec's split trigger. Orchestrator ruling, 2026-10-20, per the split trigger recorded in the spec and stated to the owner at Align: the snapshot half splits out as backlog row `[SUBSET-SCREEN-SNAPSHOT-CARRIAGE]` (already added to `.project/backlog/BACKLOG.md`). 2b ships the live half with option 3: the snapshot envelope stays v6, and replay reports the screen's findings as not assessed, so replay never reports ready for a model whose screen was not assessed. Generator decisions on replay must still equal live.

Revise `spec.md` for the split (revision 3):
- Rewrite the success criteria that assumed snapshot carriage (live/replay finding parity, snapshot-vs-build profile skew, supported/unsupported snapshot loading) so they state option 3's behavior and are testable now. Keep the generator-decision parity on replay. Drop criteria that only make sense with a new format, and say in one line each where they went (the backlog row).
- Move the "How a snapshot carries the screen" option analysis to a short pointer at the spike and the backlog row. Keep the spike's summary you added, trimmed.
- The website question is no longer on 2b's path, since no new format ships in 2b. Say so in the `[NEED]` line's follow-up, keeping the owner quote.
- Keep the epic link honest: the epic's "supported upgrades" and full snapshot-authority scope are now partly in the backlog row; note that the epic file in agentic-mbse needs updating at close (not now).
- Update the item's effort statement to the spike's live-half guess and say it is a guess.
Report what changed. Do not commit.
