# Brief: Item 7 plan — Constraint Generation

You are the plan stage for Item 7 in the orchestrated CONSTRAINT-EXEC epic run. Repo: sysml-codegen, branch `constraint-exec-epic`.

## Process constraints
- Work synchronously; never pause for background agents.
- Do NOT run `git commit` — the orchestrator commits.
- Artifact: `plan.md` in `.project/active/constraint-generation/`.

## Input
Design rev 2 (committed): `.project/active/constraint-generation/design.md` — D1–D11, the constructible exit seam, the offline Kleene unit lane, B5's generation-time assertion, and the de-risk-first list are authoritative.

## Planning guidance (orchestrator, agent-grade)
- Implement runs on sonnet: mechanical phases, exact files/templates, per-phase gates.
- De-risk order per the design: Kleene compiler + offline unit suite first (pure, no generation); then the exit seam + falsifying test; then the five-seam emission (templates + the D11 one-condition Item 5 touch) with the S4-slice reproduction; then the S4-unexercised cases (zero-assertion, indeterminate, negated/inline at execution, multi-instance, modeled-default EP override) under real simkit; final gates (constraint-free corpus byte-identity, full suite, mypy 76 baseline, ruff).
- Execution-lane tests: generation tests run with lower_constraints_enabled=True; the real-simkit runs use the environment recorded in the design's N6/execution lane.
- B4/N5: verify teax scalar-persistence state as the plan's first grounding fact (memory said fixed at teax HEAD; the design review flagged the tension).
- Keep phases resumable from checkboxes.
