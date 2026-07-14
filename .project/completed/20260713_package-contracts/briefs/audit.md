# Brief: Item 9 audit — Contracts and Sealing

You are a fresh audit session in the orchestrated CONSTRAINT-EXEC epic run. Repo: sysml-codegen, branch `constraint-exec-epic`. You did not implement this; audit it.

## Process constraints
- Work synchronously; never pause for background agents.
- Do NOT run `git commit` — the orchestrator commits.
- Artifact: `audit.md` in `.project/active/package-contracts/`.
- If execution is blocked, do the full static audit and list exact "Requested live probes" — the orchestrator runs them (this has worked all epic).

## Audit target
The four Item 9 phase commits (`fba7ddd..8c82b9b`) against `spec.md`, `design.md` (D1–D7), `plan.md` (+ completion notes incl. the two flagged items).

## What to verify (by execution where possible; else static + probe list)
1. **Tamper/extra/stale through the LOAD path**: the tests must call verify_package on a real sealed package — tamper one artifact byte → named TAMPER diagnostic; add an unhashed file → EXTRA; remove a hashed file → MISSING. Run them; mutation probe one (disable the extra-file sweep in verify.py → EXTRA test RED; revert).
2. **SC-4 both legs**: run the offline cross-session and live-vs-snapshot fingerprint tests.
3. **Graph-only ModelContract**: the structural test (no filesystem/YAML introspection) — verify it would catch a violation (what does it actually assert?).
4. **The stdlib-only verifier**: import scan; the `**`-glob matcher duplication — check both copies are byte-identical (a drift test exists? if not, flag).
5. **The two flagged items**: (a) GENERATOR_MISMATCH unreachable — adjudicate: acceptable-and-recorded (the enum documents intent; wiring it needs a second env axis — is that Item 14 integration or a dead field to remove?); (b) the glob matcher — correct on the plan's cases?
6. **Re-seal subcommand**: test exists (modify a stencil → verify fails → re-seal → verify passes; ModelContract unchanged by re-seal)?
7. **Gates**: full suite (license env), mypy 76, ruff, no baseline churn.
8. **Spec success-criteria walk** with evidence.

Verdict: Certify / Certify-with-notes / Fail.
