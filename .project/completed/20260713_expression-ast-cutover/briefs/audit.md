# Brief: Item 13 audit — Calc-Seam Cutover

You are a fresh audit session in the orchestrated CONSTRAINT-EXEC epic run. Repo: sysml-codegen, branch `constraint-exec-epic`. You did not implement this; audit it.

## Process constraints
- Work synchronously; never pause for background agents.
- Do NOT run `git commit` — the orchestrator commits.
- Artifact: `audit.md` in `.project/active/expression-ast-cutover/`.
- License env: `env $(grep -v '^#' ~/1cfe/agentic-mbse/.env | xargs) uv run pytest ...`. If execution blocked, full static audit + exact "Requested live probes".

## Audit target
The five Item 13 phase commits (`7dcae90..2b00261`) against `spec.md`, `design.md` (rev 2), `plan.md` (+ the two unplanned fixes in Phases 1 and 4).

## What to verify
1. **The skip-count jump (4 → 23).** The suite went from 2236/4-skipped pre-item to 2317/23-skipped. Account for every new skip: legitimate (license-gated goldens? retired-moved tests?) or masked failures? Run the suite and list skip reasons; any skip that hides a should-run test fails the item.
2. **Byte-identity chain**: the committed golden (D4) — run it; verify Phase 1/2's pre-flip goldens were captured from the exact replaced functions (read the capture code); extraction snapshots + baselines byte-identical across the item (git diff the corpus across 7dcae90^..2b00261).
3. **Deletion completeness**: run the INV-4 grep gate; independently grep for the whole family (ExpressionAST, ExpressionNodeType, build_expression_ast, compile_expression, PYTHON_OPERATOR_MAP, _collect_refs) in src and tests; no silent third representation.
4. **The two unplanned fixes** (Phase 1 literal-rendering gap on mocks; Phase 4's other): each structural with a regression test?
5. **REQ-AST-04 update**: counts 6→5 / 4→3 as designed; the invariant still has teeth (what does it now assert?).
6. **Gates**: full suite (license env; parity tests RAN not skipped — check), mypy 76, ruff.
7. **Spec success-criteria walk** with evidence.

Verdict: Certify / Certify-with-notes / Fail.
