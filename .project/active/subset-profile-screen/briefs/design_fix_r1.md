Design review (`design-review.md`) is Revise. Apply every must-fix and should-fix point EXCEPT the readiness rule D8, which is parked for the owner (RG-2 plus the epic's open omission/exclusion decision); the orchestrator is asking the owner now. Leave D8 as is but mark it "PARKED: owner decision pending" with a one-line pointer to the review point, and make sure nothing else in the design depends on which way it goes (readiness should be one pure function whose rule can change without touching anything else).

Orchestrator rulings on the review's points:
- Share one SysIDE load between `prepare` and `assess_screen` (review Q1). The design-review's reason is the deciding one: in `generate` a second load after writing can read files saved in between. Use the existing seam (`elaborated_pipeline.py:159-173` and `:267`). A model that loads with parse errors gives "screen not assessed".
- Nothing after the seal may raise because of the screen or the report: make the mapping and report code total, and test it.
- Pin what each command logs on destination problems, so the 2a harness's exactly-one-refusal-record rule holds and `check` never logs a refusal record on a "builds, not ready" run.
- The changed first failure for a refused model with a symlinked destination is confirmed not RG-1 by the review. Record it as a stated behaviour change, not parked.
- Apply the seven minor points unless one conflicts with the above; say which if so.
Report what changed. Do not commit.
