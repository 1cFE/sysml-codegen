# Brief: Item 14 implement (in-repo phases) — Migration, Docs, and IFE Acceptance

You are the implement stage for Item 14's sysml-codegen phases in the orchestrated CONSTRAINT-EXEC epic run. Repo: sysml-codegen, branch `constraint-exec-epic`.

## Process constraints
- Work synchronously; never pause for background agents or schedule check-backs.
- You ARE allowed to commit in this repo — you are the only session writing to this tree. One commit per phase; check off plan.md checkboxes with implementation notes. End commit messages with: `Co-Authored-By: Claude Fable 5 <noreply@anthropic.com>`.
- Do NOT touch `.project/` outside `.project/active/constraint-migration-acceptance/`. Do NOT touch agentic-mbse/teax/fusion-tea — their work is the appendix briefs, applied by separate sessions.
- License env: `env $(grep -v '^#' ~/1cfe/agentic-mbse/.env | xargs) uv run ...`

## Input — execute Phases 1–5 (+6 partially)
`.project/active/constraint-migration-acceptance/plan.md` is authoritative (design rev 2 for mechanisms).
- Phase 1 (gain fix + re-land grandfathered): the R2 backstop is exactly-two-snapshot change; the byte-identity discipline applies to the re-captures.
- Phase 2 (mapping test FIRST, green before deletions) → Phase 3 (retirement + re-anchors + grep gate) → Phase 4 (docs here) → Phase 5 (W5a seam).
- Phase 6: do the epic-checklist reconcile ONLY for boxes this repo's evidence supports; the acceptance-dependent boxes wait for the fusion-tea session (note them).
- Baseline: current HEAD (post-Item-13; suite 2317/23, mypy 76).

## Quality bar
- Phase 1 is the epic's root de-risk: if the gain fix's blast radius exceeds exactly-two-snapshots, STOP and report (do not absorb).
- The mapping/no-silent-drop test is a KEPT test reading both carriers (concrete_entries + ctx.concrete_constraints).
- Final gates: full suite green (license env), mypy 76, ruff clean, retirement grep-clean, corpus diffs limited to the enumerated classes.
- If a gate fails and the fix is outside plan scope, STOP and report precisely.
