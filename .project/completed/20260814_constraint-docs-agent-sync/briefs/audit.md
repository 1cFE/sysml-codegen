# Audit-stage brief — Item 7 (constraint-docs-agent-sync)

**From:** orchestrating session, 2026-08-14.

## The work item

Audit Item 7's implementation against the spec. Item home
`.project/active/constraint-docs-agent-sync/`: `spec.md` (the contract), `plan.md` (with
per-phase notes), `verification.md` (sweep record + per-criterion evidence),
`owner-checkpoint-20260813.md` (verbatim payload). The epic's audit discipline applies:
**probe, don't trust** — reproduce claims with live checks; certify-with-residuals is the
referent shape (Item 9's audit, `completed/20260813_derivative-upgrade-held-intent/`).
Protocol per project memory `verify-then-fix-protocol`: doc-intent check → reproduce →
family-level fix → docs loop. Write `audit.md` in the item home.

## Claims to reproduce (not exhaustive — sample beyond these)

1. **Verbatim payload:** P-001's two owner bullets are byte-identical to
   `owner-checkpoint-20260813.md:9-13` (the plan's diff check). The tension paragraph exists
   and resolves nothing; every gleaned paragraph carries `[INHERITED: <source>]`.
2. **Licensed run:** the claim is `2070 passed`, zero `no live syside license` lines. Re-run it
   yourself — `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a;
   /home/reid/1cfe/item7-rebuild-venv/bin/python -m pytest tests/` — never `uv run`; zero skip
   lines is the only proof. Also reproduce the elaborate-cleanly check on the corrected
   agent-facing examples (SKILL.md example, any authored `@inapplicable:` snippet).
3. **Post-edit sweep:** re-run S1–S5 in all three repos per the scopes recorded in
   `verification.md`; every hit must match a Table 2 row or aggregation. Spot-check ~10
   dispositions for honesty, including the "correct as written" class.
4. **Amendments:** each amended clause carries its original text; the three parked item3-F2
   records read RESOLVED-with-citation; no live site still parks the conflict; no archived file
   under `.project/completed/` was edited (check `git log --stat` for the item's commits).
5. **Matrix recount:** reproduce the recount from the tables (totals, per-status, families);
   confirm both corrected count blocks now agree with the tables; every newly cited test file
   exists and passes.
6. **Boundaries:** item commits touch only docs/skills/prompts/`.project/` (no code, fixture,
   or schema paths); TEAx commits on `constraint-semantics-item3` only; agentic-mbse commits on
   worktree branch `item7-rebuild` only; `/home/reid/1cfe/agentic-mbse` (out-of-bounds,
   `elaborate-first-salvage`) is clean; nothing pushed anywhere.

## Orchestrator rulings on the two implement-stage flags (audit verifies recording, not the calls)

Both are `[AGENT, orchestrator 2026-08-14]`, surfaced to the owner in the run summary:

- **Symlink residual (SC2/SC3):** codegen's `.claude/` agent surfaces symlink into the
  out-of-bounds checkout; the fix is committed on the authorized worktree; the residual
  resolves when the owner merges. The out-of-bounds checkout is NOT edited. Verify the
  residual is loudly recorded (verification.md + the SC tick state) and the stray-edit
  revert is documented.
- **Untagged-gates residual (SC5):** REQ tags for Items 3/5/8/9 gates are not minted by this
  item (requirements authority, not documentation sync); the parked half must have a named
  vehicle — a BACKLOG entry or an explicit close-stage obligation. If it has none, that is a
  finding.

## Cure rules

Minor, objectively verifiable fixes: reproduce first, fix at family level, record the cure in
audit.md and verification.md. Anything touching owner-verbatim text, the amendments' meaning,
or the residual rulings: finding only, no fix. End with the verdict
(CERTIFY / CERTIFY-WITH-RESIDUALS / REVISE), the findings list, and `ARTIFACT: <audit path>`.
