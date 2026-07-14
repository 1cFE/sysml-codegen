# Brief: Item 9 plan — Contracts and Sealing

You are the plan stage for Item 9 in the orchestrated CONSTRAINT-EXEC epic run. Repo: sysml-codegen, branch `constraint-exec-epic`.

## Process constraints
- Work synchronously; never pause for background agents.
- Do NOT run `git commit` — the orchestrator commits.
- An Item 8 implement session may still be committing here — write ONLY plan.md; check git log for Item 8's landed phases (its snapshot-parity artifacts are your SC-4 dependency).
- Artifact: `plan.md` in `.project/active/package-contracts/`.

## Input
Design (committed): `.project/active/package-contracts/design.md` — D1–D7 authoritative.

## Planning guidance (orchestrator, agent-grade)
- Implement runs on sonnet: mechanical phases, exact files, per-phase gates. License env: `env $(grep -v '^#' ~/1cfe/agentic-mbse/.env | xargs) uv run pytest ...`.
- Suggested order: contract models + canonical serialization + fingerprints (offline unit tests) → sealing pass + Step 9 wiring + seal subcommand → verification (tamper/extra-file/stale/env-compat tests) + embedded stdlib verifier → SC-4 stability tests (cross-load; snapshot leg gated on Item 8's landed state — check git log; if Item 8 hasn't finished, mark the snapshot-stability test to run at Item 8's certification and say so loudly).
- Final gates: full suite (license env), mypy 76 baseline, ruff, corpus byte-identity (sealing adds contracts/ files to generated output — that's an expected-diff class for generated packages, NOT the committed baselines unless the baseline capture includes them; plan the baseline handling explicitly).
- Keep phases resumable from checkboxes.
