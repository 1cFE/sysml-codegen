# Brief — implement: docs-lifecycle-sync, Phase 5 ONLY (EXPLAINER_PROMPT re-anchor)

**Work item:** `.project/active/docs-lifecycle-sync/`. Read: `spec.md` (R4), `plan.md`
(Phase 5), `inventory.md`. Phases 1–4 committed; docs now reconciled to merged main.

**Scope guard:** Phase 5 only. Re-anchor `.project/active/EXPLAINER_PROMPT.md` — do NOT
build the HTML (that is `[V2-HTML-BUILD]`, owner-assigned to another agent; spec Non-Goal).
Stop after the phase commit.

**Baseline:** merged main `936315c`, branch `docs-lifecycle-sync` — the corrected docs on
this branch are the anchor, not the pre-epic docs.

**Known-stale anchors in the prompt (orchestrator-verified):**
- Banner says "post-CONSTRAINT-EXEC" and targets branch `constraint-exec-epic` — the wave is
  MERGED to main; the CONSTRAINT-LIFECYCLE epic landed after the prompt was last touched
  ("two epics since Gen-1" is now three).
- Matrix counts cited as 274/32 — now **276 rows** (73→77 files; recount in Phase 4 commit
  `d4051ee`).
- The reading list / responsibility map predates: `04-input-resolver.md` →
  `04-producer-resolution.md` (unified ladder), new `30-diagnostic-severity.md`, doc 24's
  rewrite, v5 snapshot format, catalog schema 2.0.0, trust manifest, producer completeness.

**Method:** sweep every checkable claim in the prompt against the branch (file names, doc
numbers, counts, epic narrative, branch/commit instructions); amend in place at the prompt's
own emphasis. Keep its structure and buildability apparatus (responsibility-map rows,
reading-list data sources, reuse guidance) — re-point, don't redesign. The eight
constraint-exec content areas stay; add lifecycle-epic deltas where the prompt's narrative
requires them (resolver unification, severity system, sealed-thread/trust story) rather than
as a bolted-on section.

Update inventory.md + plan.md Phase 5 boxes/notes. Commit:
`docs-lifecycle-sync Phase 5: EXPLAINER_PROMPT re-anchored to merged main`
(+ `Co-Authored-By: Claude <noreply@anthropic.com>`).

Finish with `ARTIFACT: .project/active/EXPLAINER_PROMPT.md`.
