# Brief — implement: docs-lifecycle-sync, Phases 3 AND 4 (severity doc; portability matrix rows)

**Work item:** `.project/active/docs-lifecycle-sync/`. Read: `spec.md` (R1, R2), `plan.md`
(Phases 3 and 4), `inventory.md` (sweep B GAP rows). Phases 1–2 are committed and audited
(Pass with notes — `audit-midrun.md`); doc 04 is now `04-producer-resolution.md`.

**Scope guard:** Phases 3 and 4 only, ONE COMMIT PER PHASE (severity doc commit, then matrix
commit). Stop after Phase 4's commit; do not start Phase 5.

**Baseline:** merged main `936315c`, branch `docs-lifecycle-sync`. Docs + `.project/` only.

## Phase 3 — Severity-System Reference Doc (spec R1)

New doc in `docs/architecture/reference/`, numbered after the 27/28/29 series (30 unless
taken). Content: the diagnostics severity contract — constraint-facts/v2 severity field, the
`screen_extraction_diagnostics` sink (`analysis/diagnostic_screen.py`), fail-closed skew in
BOTH directions, BLOCK-vs-warning ordering, and where the gate runs on the snapshot path
(`snapshot/loader.py:588-591`; pins at `_upstream_pins.py:24-27`).

Ground truth priority: merged code first; then Item 4's archived artifacts
(`.project/completed/20260720_constraint-lifecycle-diagnostics-defaults/{design,evidence,audit}.md`).
If they disagree, code wins AND you surface the contradiction loudly — never silently pick.

Bar: a reader must be able to answer "what happens on severity skew in each direction" from
the doc alone. Cite merged-main line numbers. Link the new doc from its doc 27/28 neighbors
and any index that lists the reference docs. Also replace the one-line severity mention
context at doc 27:86 with a cross-reference to the new doc if that improves it — judgment
call, record it.

## Phase 4 — Portability Matrix Rows (spec R2)

Add REQ-SNAP row(s) after REQ-SNAP-20 in `docs/architecture/verification-matrix.md` for:
- the v5 referent shape gate — `_validate_source_referents` (`snapshot/loader.py:912`,
  called at `:837`);
- whole-tree snapshot portability — cite the pinning tests in
  `tests/conformance/test_constraint_snapshot_portability.py` (verify which tests actually
  pin which behavior before citing them — no aspirational citations).

Matrix recount discipline (project memory `verification-matrix-drift-modes`): after adding
rows, recount the index totals AND per-family counts — not just the summary block. Matrix
currently has 274 REQ rows; record the new total in inventory.md and update every place the
matrix states its own counts.

Also per spec R2: file GAP register rows in inventory.md (do NOT add matrix rows) for the
other uncovered new surfaces — producer resolution/completeness, catalog schema 2.0.0, trust
manifest — as candidates for a later owner decision.

## Both phases

Update inventory.md dispositions; tick plan.md boxes + Implementation Notes per phase; run
Phase 3/4 validation checks from plan.md and record results. Commit messages:
`docs-lifecycle-sync Phase 3: diagnostics severity reference doc` and
`docs-lifecycle-sync Phase 4: portability matrix rows + recount`
(+ `Co-Authored-By: Claude <noreply@anthropic.com>`).

Finish with `ARTIFACT: <path of the new severity doc>`.
