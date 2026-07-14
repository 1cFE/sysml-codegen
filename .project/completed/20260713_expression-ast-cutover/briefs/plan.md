# Brief: Item 13 plan — Calc-Seam Cutover

You are the plan stage for Item 13 in the orchestrated CONSTRAINT-EXEC epic run. Repo: sysml-codegen, branch `constraint-exec-epic`.

## Process constraints
- Work synchronously; never pause for background agents.
- Do NOT run `git commit` — the orchestrator commits.
- An Item 9 implement session is committing to this tree — write ONLY plan.md; touch no code.
- Artifact: `plan.md` in `.project/active/expression-ast-cutover/`.

## Input
- Design rev 2 (committed): `.project/active/expression-ast-cutover/design.md` — stages 0–4, the literal rule, member_names composition, Stage-4 test-surface categorization, REQ-AST-04 6→5 are authoritative.
- **R1 / plan-task-0 is ALREADY RESOLVED**: agentic-mbse exposes `extract_expression_ir` (public, lazy-exported, landed with a serialization-equality test — agentic-mbse commit 3ad890e). The design's "still open" note is stale on this point; plan Stage 0 to consume it directly, no de-risk probe needed.

## Planning guidance (orchestrator, agent-grade)
- Implement runs on sonnet: per-stage phases with the design's exact comparands, golden-capture steps, and per-stage byte-identity gates. License env: `env $(grep -v '^#' ~/1cfe/agentic-mbse/.env | xargs) uv run pytest ...`
- Sequencing: implement starts after Item 9's implement finishes (orchestrator enforces; note it). Baseline = post-Item-8+9 corpus at HEAD.
- Stage 4's ~240-reference test migration is the largest mechanical chunk — give it its own phase with the design's re-anchor/retire categorization as the checklist.
- Keep phases resumable from checkboxes.
