# Stage brief — Phase 4, Gate 4D: documentation repair by subject

**You are executing the documentation gate** of the recovery plan:
`/home/reid/1cfe/sysml-codegen-item7-rebuild/.project/active/cutover-recovery/plan.md` — Gate 4D.
Read first: Gate 4D's plan text, the ledger's 23 doc rows, the Gate 4A measured finding (the 22
architecture docs are byte-identical to Item 6 at rebuild HEAD — the restore step is already
satisfied; only the rewrite remains), the Phase 2 CLAUDE.md disposition and the 3E/4C mechanism
records, and the S4 ruling's documentation obligation.

## The situation the docs must describe (be exact about this)

Since 3E, the exact route (source admission → strict elaboration → InstanceGraph → one-way
projection → generation; v6 instance-graph snapshots) is the ONLY public authority. The legacy
string-resolution machinery (`analysis/`, `resolution/`, `pipeline_builder`, v5 snapshots) is
present but publicly unreachable, with its retirement fully prepared and gated on owner
acceptance (the runbook). Do not document the legacy route as live; do not document it as
deleted. Document what is true, including the pending-retirement state where a subject requires
it.

## Scope

1. **Subject-by-subject update list first** (committed as part of the first subject commit):
   for each of the 34 architecture docs + CLAUDE.md, state which claims became stale and which
   public behavior replaces them — or "no stale claims" with a one-line basis. The 3E/4C
   mechanism records (consumer collapse, declaration-site groups, per-occurrence expansion,
   zero-constraint early return, units annotation rule, envelope identity model) are the
   authoritative content sources.
2. **One coherent subject per commit**, per the plan. Priority order: pipeline overview (00) +
   `docs/architecture/overview.md`; snapshot/v6 subject (27 + envelope semantics incl. the 3A
   identity model and its documented offline limit); orchestration/public-surface subject (02
   incl. the single-authority state); the S4/Gate-4D modeling-requirement subject (cross-part
   aggregation → named per-child intermediates, `costed_cart_d5` as the worked example, Item 10
   cross-reference); entry-point/group-identity subject (06/17 — the option-C rule);
   verification-matrix pointers ONLY where rows reference now-false claims (no wholesale
   rewrite; the matrix is subject-specific by rule 8). Docs whose sole subject is a
   retiring-legacy component get a status banner (retiring, runbook pointer) — not a stub, not
   deletion; their full disposition ships with the retirement/Item 8.
3. **CLAUDE.md — own disposition, own commit** (rule 8): narrow update to the true current
   state (exact route commands/architecture, v6 snapshot flag semantics, the pending-retirement
   note). The Phase 2 "restore" verdict is already satisfied at rebuild HEAD; what lands now
   must match the code at HEAD — verify each claim against the tree before writing it.
4. **The identical-content check** (plan 4D): add the check rejecting identical full-file
   content across distinct numbered reference docs (allowlist empty), wired so the suite runs
   it.

## Rules

- Working-voice: plain, subject-specific, no generic text. Every claim verified against code at
  HEAD (cite file paths in the docs where the doc genre does that already; match each doc's
  existing conventions).
- No production or test changes beyond the identical-content check + its test. Batteries per
  commit (suite delta = the check's nodes only; corpus/execution unchanged; ruff/mypy; checker
  modes; `git diff --check`).
- Read every changed doc in full before committing it (manual review is the plan's own
  requirement; record that it happened per subject).
- Rule-10: a doc claim you cannot verify true or false against the tree → surface it in the
  update list rather than guessing.

## Report back

The update list summary (per-doc verdict), subjects committed with OIDs, the CLAUDE.md
disposition record, the identical-content check state, batteries. `ARTIFACT:` the updated plan.
