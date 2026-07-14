# Brief: Item 5 plan — Concrete Lowering

You are the plan stage for Item 5 in the orchestrated CONSTRAINT-EXEC epic run. Repo: sysml-codegen, branch `constraint-exec-epic`.

## Process constraints
- Work synchronously; never pause for background agents.
- Do NOT run `git commit` — the orchestrator commits.
- Artifact: `plan.md` in `.project/active/constraint-lowering/`.

## Input
Design rev 2 (committed, probe-settled): `.project/active/constraint-lowering/design.md` — the B1 adjudication, D5-IR carriage, strict ladder (scoped→alias→design-attr), Step 5.65→7 threading, and the Appendix A/B decisions and fixtures are authoritative. `b1-probe-evidence.md` holds the working model-shape skeleton for the multi-instance fixture (package-level design instance required).

## Planning guidance (orchestrator, agent-grade)
- Implement runs on sonnet: mechanical phases, exact files, signatures from the design, per-phase gates.
- Suggested de-risk order: ConcreteConstraint model + ID minting + serialization first (offline unit tests); then the strict resolver seam (with the fallback-unreachable + ladder tests); then expansion (four-kind dispatch, blocked-owner error, multi-instance); then Step 5.65→7 threading + roots-before-pruning; then the four success-criteria fixtures + corpus byte-identity gate.
- Fixtures: `constraint_multi_instance`, `constraint_inline`, `constraint_blocked_owner` are new (skeletons per design/evidence); wi014_toy reproduces S4's control-prune/retain criterion with include_all=False.
- Live tests run in this repo's venv (licensed — verified this run). Corpus byte-identity: regenerate, timestamp-only diff check, revert (never run the snapshot-capture script for this item).
- Keep phases resumable from checkboxes.
