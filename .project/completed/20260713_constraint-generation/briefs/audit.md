# Brief: Item 7 audit — Constraint Generation

You are a fresh audit session in the orchestrated CONSTRAINT-EXEC epic run. Repo: sysml-codegen, branch `constraint-exec-epic`. You did not implement this; audit it.

## Process constraints
- Work synchronously; never pause for background agents.
- Do NOT run `git commit` — the orchestrator commits.
- Artifact: `audit.md` in `.project/active/constraint-generation/`.
- **License incantation that works from any shell here:** `env $(grep -v '^#' ~/1cfe/agentic-mbse/.env | xargs) uv run pytest ...` — the key lives in agentic-mbse/.env, not ambient env. Use it; do not report license failures as findings.
- Never run the snapshot-capture script.

## Audit target
The five Item 7 phase commits against `spec.md` (review-revised), `design.md` (rev 2), `plan.md` (+ notes incl. the teax pin and the three Phase 4 bug fixes).

## What to verify by execution
1. **The Kleene unit suite**: run it; independently spot-derive three cells against the emitted function source (leaf-unknown on NaN, false-and-unknown=false, -0.0→0.0 boundary).
2. **The falsifying exit test**: run it; then mutation probe — remove the report-channel pin from the exit builder → the mechanism leg must go RED; revert.
3. **The three Phase 4 bug fixes** (bracket-unsafe class names, unsanitized aggregator fields, hardcoded-None default): each must have a regression test — find and run them; check the fixes are structural, not string patches.
4. **S4-slice + the five S4-unexercised cases** under real simkit: run the execution-lane tests (zero-assertion aggregator, indeterminate non-finite point, negated + inline at execution, multi-instance, modeled-default EP override changing the verdict). Violated verdicts complete with ordinary outputs intact — assert you saw it.
5. **The same-IR (INV-2) and B5 guards**: mutation probes per the design (mutate one predicate_ir post-lowering → generation fails naming the constraint_id).
6. **D11's one-condition touch**: diff constraint_lowering.py across the item — exactly the one condition; constraint-free corpus byte-identity gate green.
7. **Gates**: full suite (with license env), mypy 76 baseline, ruff. Break-the-YAML test present and RED-capable (S4 carry-forward (2)).
8. **Spec success-criteria walk** with evidence; flag silent scope cuts.

Verdict: Certify / Certify-with-notes / Fail.
