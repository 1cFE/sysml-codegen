# Orchestrator brief — spec stage, CONSTRAINT-SEMANTICS Item 9

## Work item

Epic CONSTRAINT-SEMANTICS Item 9: **Derivative Upgrade Under Held Intent** (0.5 day, Modeling
follow-on). Full item text: `.project/backlog/epic_constraint_semantics_contract.md` lines
1254–1291. Item home: `.project/active/derivative-upgrade-held-intent/` (this folder).

**Objective (verbatim from the epic):** Once Item 8 lands, upgrade `catf_mfe_gated` under the
already-ruled rows: derive the 26 blocked radii per the ruled A5/A6 basis (axis root radius + 14
thicknesses free), assert A9's `ProductWithinBand` at the ruled 1% relative tolerance, delete the
A5/A6 usages per their ruled intent, and restate the accounting identity to
`65 = 56 carriers + 9 named deletions` (mechanical consequence of executing the held rulings — no
re-disposition).

## Provenance you must preserve

- **Boundary authority: [AGENT] (ratified by owner, 2026-08-13)** — filed under Item 5's D-S1/D-S2
  ruling (option 3). The target forms are already ruled; **no new dispositions are authorized**.
- **Held intent lives at**
  `.project/completed/20260813_catf-constraint-policy-acceptance/owner-disposition.md`, rows A5,
  A6 (basis cell: axis root radius + 14 layer thicknesses free, all other radii derived —
  **[AGENT] ratified by owner 2026-08-13**) and A9 (tolerance cell: **[OWNER 2026-08-13] 1%
  relative**, band = `count * each_capacity ± 1%`, relative form chosen so the band scales under
  design-search resizing). These are in-force intent, not history. The spec's job is faithful
  capture and operationalization, not re-decision.
- A9's ruled target form (from the disposition row): `assert constraint pumping_speed_agrees :
  ProductWithinBand { in observed = pumping_speed_total; in count = n_pumps; in each_capacity =
  pump_capacity_each; in rel_tol = …; }` in the **relative** form. The row also says: if the
  def-shape must change materially, the design **notes it** rather than silently adapting.
- A5/A6 ruled intent: **delete** both usages; each layer's `inner_radius` is the layer below's
  `outer_radius` and each `outer_radius := inner_radius + thickness`. Owner-disposition note O6:
  this implies ~27 attribute-declaration edits, authorized by the basis ruling.

## Success criteria (from the epic, restate with grades)

1. Three executing gates (A2, A3, A9); the `blocked-by-defect` markings retired from table and
   PROVENANCE; expected outputs re-derived from the table **before** confirmation tests (same
   SC-6 discipline as Item 5 — commit expectations first, then run).
2. Integrity manifest re-proves the restated identity (`scripts/check_gated_manifest.py --check`
   is the existing prover; it also ties each `derive-instead` deletion to its in-source
   derivation and chosen-basis statement — A5/A6's deletions must satisfy it). Frozen twins
   (`catf_mfe_model`, `catf_mfe_d5`) byte-untouched.
3. SC-3 (B1–B5 marker retirement) — **ruled at Align, [OWNER 2026-08-13], two-sided recording:**
   - `[INLINE-PREDICATE-MARKER-DROP]` is open and unowned, so SC-3 is a **not-fired conditional**
     in this run. The five `@inapplicable:` markers stay recorded in PROVENANCE.
   - **Record the trigger on both sides:** Item 9's records mark SC-3 as a not-fired conditional,
     AND the `[INLINE-PREDICATE-MARKER-DROP]` entry in `.project/backlog/BACKLOG.md` gains one
     line saying that closing it fires the B1–B5 marker migration (move the five `@inapplicable:`
     markers from PROVENANCE into source, retiring the workaround) — so whoever picks up the
     defect inherits the obligation from the entry itself, not from an archived item's
     conditional. Phrase it as a decision record, not an instruction pile-up.

## Context the spec should absorb (read these)

- `.project/backlog/epic_constraint_semantics_contract.md` — Item 9 section, Item 8's close
  record (the fix that unblocks this: freeze `62a07e5c870158672eb100f1cba73adfe4c9df28`,
  constraint-formal and computed-attribute ports now carry authored unit text), and Item 5's
  section (SC-3 amendment history, B1–B5 deviation, held-intent paragraph).
- `.project/completed/20260813_catf-constraint-policy-acceptance/owner-disposition.md` — rows
  A2/A3 (already executing), A5/A6/A9 (this item), B1–B5, the vocabulary section, and the
  restated-identity arithmetic.
- The derivative fixture itself: `tests/fixtures/catf_mfe_gated/` (PROVENANCE.md, the all-65
  table location, `radial_build.sysml`, `vacuum.sysml`, the constraint library where
  `ProductWithinBand` lives).
- `scripts/check_gated_manifest.py` — what the integrity check currently proves and what the
  restated identity requires of it.
- Item 5's expected-output records (expected catalog/report/study outcomes) — this item
  re-derives them for the new shape: expect three eligible gates (A2, A3, A9), histogram moves
  from `{eligible 2, excluded 3, non_reaching 53}` over 58 carriers to the restated 56-carrier
  account. Derive the exact expected values from the table, don't copy mine.

## Constraints and environment facts

- Frozen twins `catf_mfe_model` and `catf_mfe_d5` must not change by a byte. Only
  `catf_mfe_gated` (and its expectations/PROVENANCE/manifest inputs) moves.
- **Concurrency:** another agent is closing Items 6 and 8 in this same worktree; CURRENT_WORK.md,
  BACKLOG.md, CHANGELOG.md and the calcdef-design archive moves may be uncommitted. Do NOT
  commit, revert, or absorb their changes. Stage and commit only files this item touches. The
  BACKLOG one-liner (SC-3 rider) should be made and committed only after checking `git status`
  shows BACKLOG.md clean of foreign uncommitted edits — if it isn't clean yet, record the
  pending edit in the spec and defer it to a later stage of this item.
- Interpreter: `uv run` is WRONG for this worktree pair (resolves agentic_mbse to the main
  checkout). Use `/home/reid/1cfe/item7-rebuild-venv/bin/python -m pytest`.
- License: `SYSIDE_LICENSE_KEY` lives in `/home/reid/1cfe/agentic-mbse/.env`
  (`set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a`). A green run with zero
  license-skip lines is the only valid licensed proof.
- Nothing is pushed; no `main` is touched; TEAx stays on `constraint-semantics-item3` @ `5b70ae9`;
  `pre_pr` remains with the owner.

## What the spec stage should deliver

`spec.md` in this item folder: graded requirements (the held-intent rows are the [NEED]/[OWNER]
payload — carry quotes or path-cites), the SC-3 two-sided conditional as an explicit requirement,
the restated-identity arithmetic stated precisely (65 = 56 carriers + 9 named deletions; name the
9), out-of-scope (no re-disposition, no marker-gap fix, no TEAx change, no schema change),
and acceptance criteria runnable by a later audit. Keep it proportionate — this is a 0.5-day
mechanical-execution item; the spec's value is exactness, not length.
