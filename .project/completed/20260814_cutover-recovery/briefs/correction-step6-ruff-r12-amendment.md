# Step-6 plan — ruff R12 amendment

**Written 2026-08-14 at `0ded316` (companion `6372ef7`), before any edit.** Ratified
instruction: plan.md step-6 checkbox + `owner-disposition-20260811.md` disposition 2 — amend
spec requirement R12 to a zero-new ruff baseline: no new findings, changed files clean unless a
recorded pre-existing finding is unchanged, totals no worse. Every decision below is `[AGENT]`
under that ratification. This step touches no code, no tests, no fixtures — four project
artifacts only.

## The baselines, measured this session (ruff 0.16.2, the item7-rebuild venv)

The disposition's recorded codegen number, **14**, is stale: `ruff check src` reads **12**
(it improved during the CONSTRAINT-SEMANTICS epic; the step-4 record documents 14 → 12). Per
the standing instruction restated in the step-4 and step-5 records, the amendment records the
**measured** set. Both sets reproduced exactly this session:

- **codegen `src` = 12**, all UP042 (str+Enum), enumerated file by file in the amendment text.
- **agentic-mbse `src` = 1**: `src/agentic_mbse/extraction/index.py:146:5 N806`, measured at
  companion HEAD `6372ef7`, tree clean.

Recording the named finding *sets* (not counts) is what makes "changed files clean unless a
recorded pre-existing finding is unchanged" auditable: the step-5 gate already ran exactly that
comparison (`--output-format concise` set-diff against HEAD) and the amendment encodes it.

## Judgment call 1 — the R12 command list drops `uv run`

R12's command list says `uv run pytest tests/` etc., and names the companion as
`../agentic-mbse`. Both are environment falsehoods in the current topology: `uv run` in this
worktree resolves the **parked** `/home/reid/1cfe/agentic-mbse` checkout, and `../agentic-mbse`
*is* that parked checkout. A literal execution of the requirement would measure the wrong
environment — and R12's command list is precisely what the step 7–8 batteries execute.

**Decision: amend both, dated.** Commands restate against the venv interpreter
(`/home/reid/1cfe/item7-rebuild-venv/bin/python -m …`); the companion pointer moves to the
authoritative worktree (`/home/reid/1cfe/agentic-mbse-item7-rebuild`). The note records that
this form holds until the phase-D merge and worktree cleanup. Historical fidelity lives in git
history; a requirement that mis-measures when followed is worse than an amended one.

## Judgment call 2 — the "coordinated repository gates" SC box stays unticked

The tick-provenance note (spec.md, after the SC list) left the box unticked for one recorded
reason: `ruff check src` reads 14 and R12 wants clean production (owner question 2 unanswered).
Disposition 2 answers that question and this amendment discharges the blocker.

**Decision: do not tick.** The box's substance is "pass the **fresh exact-count**, license,
Ruff, mypy, and diff gates in R12" — and the fresh counts are, by the plan of record, the
single-shot step 7–8 batteries at the final paired OIDs. Step-5 gate numbers are current but
not final-tree numbers (step 6 itself moves the tree). The honest state: blocker discharged,
tick belongs to the steps 7–8 record. The note gains a dated update saying exactly that. The
**mission outcome** half of that note is untouched — its own text already records that probe P1
sits outside the independent audit and the tick is the owner's to make.

## Path set (declared before editing)

- `.project/active/elaborator-cutover/spec.md` — R12 amendment (dated): zero-new baseline
  clause with both enumerated sets; runner + companion-pointer amendment; tick-provenance note
  update for the coordinated-gates box.
- `.project/active/cutover-recovery/plan.md` — step-6 checkbox + completion record.
- `.project/CURRENT_WORK.md` — status update.
- `.project/active/cutover-recovery/briefs/correction-step6-ruff-r12-amendment.md` — this brief.

No code, test, fixture, matrix, or ledger path. Matrix: zero row edits expected (no row cites
R12's ruff clause); no recount.

## Gates

`ruff check src` **12** (codegen) / **1** (companion) — measured before editing, re-checked
identical after (the step edits no Python). `git diff --check` clean. No suite re-run: no code
or test changed; the step-5 gate baselines stand as the current-tree record.

## Path-set delta, recorded at execution

None — the four declared artifacts were the four edited.
