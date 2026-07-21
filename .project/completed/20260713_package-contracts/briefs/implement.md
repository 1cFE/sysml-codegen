# Brief: Item 9 implement — Contracts and Sealing

You are the implement stage for Item 9 in the orchestrated CONSTRAINT-EXEC epic run. Repo: sysml-codegen, branch `constraint-exec-epic`.

## Process constraints
- Work synchronously; never pause for background agents or schedule check-backs.
- You ARE allowed to commit in this repo — you are the only session writing code to this tree. Commit at each completed plan phase; check off plan.md checkboxes with implementation notes. End commit messages with: `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`.
- Do NOT touch `.project/` outside `.project/active/package-contracts/`. Never run capture scripts except into temp dirs.
- License env: `env $(grep -v '^#' ~/1cfe/agentic-mbse/.env | xargs) uv run pytest ...`

## Input — execute the plan
`.project/active/package-contracts/plan.md` (Phases 1–4) is authoritative; `design.md` D1–D7 holds the models, seal function, verifier, and seams. **Item 8 is now CERTIFIED** — the SC-4 snapshot-stability leg's preconditions hold; run it live (no deferral needed; update the plan's bolded gating note accordingly).

## Quality bar
- Fingerprint determinism is the item's soul: canonical serialization pinned, tests across independent loads AND live-vs-snapshot.
- The embedded stdlib verifier imports nothing from sysml-codegen — structural test.
- Tamper/extra-file/stale-detection tests must exercise the LOAD path (verify_package), not just seal internals.
- Baseline handling per the plan (contracts/ files are generated-package content; the exact-file-set assertion sweep).
- Final gates: full suite (license env), mypy 76, ruff, corpus byte-identity per the plan's baseline decision.
- If a gate fails and the fix is outside plan scope, STOP and report precisely.
