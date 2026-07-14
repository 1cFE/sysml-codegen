# Brief: Item 4 plan — Part-Instance Index

You are the plan stage for Item 4 in the orchestrated CONSTRAINT-EXEC epic run. Repo: sysml-codegen, branch `constraint-exec-epic`.

## Process constraints
- Work synchronously; never pause for background agents.
- Do NOT run `git commit` — the orchestrator commits.
- Artifact: `plan.md` in `.project/active/part-instance-index/`.

## Input
- Design rev 2 (committed, review-revised, orchestrator-accepted): `.project/active/part-instance-index/design.md` — the node-type-dispatch gate, entry-independent typing, and eight named validation tests are authoritative.
- B1/B2 probe evidence: `b1-probe-evidence.md` (confirmed facts; the reproduction command shows the licensed-env invocation for any live test).
- S3 fixture: `.project/active/spike-concrete-expansion-instance-index/model.sysml` (promotable; nine-instance oracle).

## Planning guidance (orchestrator, agent-grade)
- Implement runs on sonnet: phases must be mechanical — exact files, function signatures from the design, the test list (the design's Validation #1–8 including [3..3], Cartesian, and the same-name-different-owner collision case), and per-phase verification commands.
- Live tests need the licensed sibling env (see b1-probe-evidence.md reproduction command; also memory: license loads via script runs, not bare -c). Say exactly how each test phase runs.
- Final phase gates: new tests green, full suite green, mypy/ruff clean, and the byte-identity check for the existing corpus (index is additive; expected diff = none).
- Keep phases resumable from checkboxes.
