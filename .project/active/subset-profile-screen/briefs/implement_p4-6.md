Good work on Phases 0-3; the structure reads well. Continue with Phases 4, 5 and 6 of the plan, same rules: commit per phase with plan notes, exit check per phase, stop and report after Phase 6.

Phases 4 and 5 are the first behaviour changes. Keep them reviewable alone: the commit for each should contain only that phase's change and its tests. For Phase 4, the refusal-record comparison should differ from the Phase 0 baseline only where the design says (the refused-model-with-symlinked-destination case reporting the model's refusal); list every differing record in the notes and confirm each is expected. Any other difference is a stop-and-report. Same for Phase 5: no record or package byte may change.

Set up the TEAx execution-lane provenance manifest only if it is cheap and documented in the repo; otherwise leave it for Phase 9 and say what it needs.
