# Brief: Item 14 plan — Migration, Docs, and IFE Acceptance

You are the plan stage for Item 14 in the orchestrated CONSTRAINT-EXEC epic run. Repo: sysml-codegen, branch `constraint-exec-epic`.

## Process constraints
- Work synchronously; never pause for background agents.
- Do NOT run `git commit` — the orchestrator commits.
- An Item 13 implement session may be committing — write ONLY plan.md; touch no code.
- Artifact: `plan.md` in `.project/active/constraint-migration-acceptance/`.

## Input
Design rev 2 (committed): `.project/active/constraint-migration-acceptance/design.md` — five workstreams (W1 gain fix + grandfather re-land; W2 manifest retirement + mapping test; W3 docs ×3 repos; W4 IFE acceptance; W5 seams, with W5b as W4's precondition), the dual carriers, the epsilon boundary rule.

## Planning guidance (orchestrator, agent-grade)
- Phase the CROSS-REPO work explicitly for the orchestrator to sequence: sysml-codegen phases (W1, W2, docs-here, W5a) run in this repo's implement session; agentic-mbse docs and teax docs+W5b are SEPARATE small sessions in those repos (write their ready-to-apply briefs as plan appendices, like Item 3 did); fusion-tea W4 is its own session rooted there (write its brief too — the reference facts at .project/reference/fusion-tea-ife-sweep/ carry the paths).
- W1 lands first (everything depends on the lowered fusion_tea); W4 last, after W5b and Item 13's certification (baseline coherence).
- License env: `env $(grep -v '^#' ~/1cfe/agentic-mbse/.env | xargs) uv run ...`. The acceptance run needs the teax venv (epic branch) for the study CLI.
- The acceptance report is a committed artifact: grid point → old classification → new verdict → match, with the epsilon-boundary rows flagged; 100% match (or surfaced boundary divergence) is the epic's Critical Success Factor.
- Keep phases resumable; the epic Success Criteria checklist reconcile is the plan's final phase (the epic file's boxes get checked with evidence links).
