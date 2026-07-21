# Brief: Item 13 implement — Calc-Seam Cutover

You are the implement stage for Item 13 in the orchestrated CONSTRAINT-EXEC epic run. Repo: sysml-codegen, branch `constraint-exec-epic`.

## Process constraints
- Work synchronously; never pause for background agents or schedule check-backs.
- You ARE allowed to commit in this repo — you are the only session writing to this tree. One commit per stage/phase; check off plan.md checkboxes with implementation notes. End commit messages with: `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`.
- Do NOT touch `.project/` outside `.project/active/expression-ast-cutover/`. Do NOT modify agentic-mbse (extract_expression_ir is landed there — consume it).
- License env: `env $(grep -v '^#' ~/1cfe/agentic-mbse/.env | xargs) uv run pytest ...` (skip-is-fake-green caveat: license-gated parity tests MUST run, not skip — check the pass count).

## Input — execute the plan
`.project/active/expression-ast-cutover/plan.md` (Phases 0–4) is authoritative; `design.md` rev 2 holds the renderer spec (literal rule, member_names composition, dialect rules), stage comparands, and the Stage-4 re-anchor/retire checklist with pinned REQ-AST-04 edits. Baseline = current HEAD (post-Items 8+9).

## Quality bar
- Phase 0's corpus-wide parity proof gates everything: every corpus calc expression through (extract_expression_ir → calc-compat renderer) byte-equal to the exact replaced function's output. If ANY expression diverges, STOP and report the divergence precisely (do not patch around it).
- Per-stage byte-identity for generated packages; the comparand is the replaced function, never a downstream proxy.
- Stage 4: the deletion + grep gate (ExpressionAST, build_expression_ast, compile_expression gone) + the ~240-reference migration per the checklist. No silent third representation.
- Final gates: full suite green (license env; verify parity tests RAN), mypy 76 baseline, ruff clean, corpus byte-identical or reviewed-diff per plan.
- If a gate fails and the fix is outside plan scope, STOP and report precisely.
