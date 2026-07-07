# Spec: Item 10 — Docs Refresh & Explainer-Prompt Revision (Epic Close)

**Epic**: PIPELINE-TRUTH (`.project/backlog/epic_pipeline_truth.md`), Item 10 — the last item.
**Type**: Documentation. **Stage**: combined spec+plan+implement (0.5–1 day, low risk).
**Status**: Complete (2026-07-06).

---

## Why

Items 1–9 are landed and audited PASS. Each item closed its own docs loop (R4 step 4), so
the reference docs under `docs/architecture/` are already reconciled to post-epic HEAD.
Item 10's job is the closing verification pass: confirm that reconciliation holds at
post-epic HEAD, retire the epic's caveats in the **aggregating** documents that still carry
the pre-epic story (the explainer prompt, the docs-scrub fact sheet, BACKLOG, CURRENT_WORK),
resolve the one doc that explicitly deferred a decision to Item 10, and move the epic to
Completed with its lessons-learned block filled.

## The truth to certify against

Post-epic HEAD facts (audited, per each item's close-out):

- **Verification matrix**: 253 = 249 PASS + 4 UNTESTED + 0 DEFERRED, 30 families
  (Item 7). Recount from the family index, not the summary block (memory:
  `verification-matrix-drift-modes`).
- **SC-A/B/C**: fusion-tea generates at TRUE ZERO V11 offenders; run-C lcoe bit-exact
  ($270.1211779380445); every workaround deleted upstream (Items 2/3).
- **Cross-part value resolution**: the supplied-value materializer
  (`resolution/supplied_values.py`, REQ-SVM-01..04) resolves cross-part/in-part supplied
  values by source QN. Cross-part support is now **broader than the pre-epic "four
  shapes"**: the UPSTREAM-FINDINGS four wiring shapes (multi-hop EXPOSE, part-def scoped
  aliases, specialized-def `:>>` chains, sibling disambiguation) PLUS the SVM value-fill
  mechanisms a/b/c/d (Item 2).
- **Constraint report**: subtype-aware (`include_subtypes=True`), fires on `assert
  constraint`, available on the `--from-snapshot` path (Item 4). modeling-assumptions §8
  rewritten — no "scans the whole model" overclaim.
- **F2**: resolved fix-text-to-code; REQ-OR-05/06/08 + doc 10 describe the actual Key_A/Key_F
  registrations; DOCS-SCRUB-F2 retired (Item 7).
- **F4**: resolved land-with-split; docs 03/04/05 + matrix honestly state `resolve_input()`
  is parity-validated-but-not-yet-wired, the executable rewire filed as `[ITEM7-F4-CUTOVER]`;
  DOCS-SCRUB-F4 retired (Item 7). The "not-yet-wired" language is **truth, not a caveat**.
- **doc-19 known-deviation**: retired — `_walk_aggregation_ast` now conforms (REQ-AST-10, Item 8).
- **doc-25 dotted-leaf hedge**: unit-pinned (`TestDottedLeafAliasMatch`, Item 8), with an
  explicit "PIPELINE-TRUTH Item 10 decides part-blindness tightening" note this item resolves.
- **Gate (audited HEAD)**: suite 2069 passed / 4 skipped / 5 xfailed; ruff src 17; mypy src 104.

## Caveats to retire (and where they legitimately remain)

Retire in **live/aggregating docs**; leave verbatim in **historical documents** (work
reports, release notes, PR bodies, `completed/`, the discovery register, prior-epic files —
these are the record of what was true then):

| Caveat | Live docs to fix | Already retired in reference docs? |
|---|---|---|
| V11 10-offender abort | EXPLAINER_PROMPT, fact-sheet F6 | Never in `docs/architecture/` |
| assert-constraint silence | (aggregating docs) | Yes — 01 + §8 (Item 4) |
| "four specific cross-part shapes" | EXPLAINER_PROMPT, fact-sheet F6 | Never in `docs/architecture/` |
| F2/F4 open divergences | EXPLAINER_PROMPT (as *open*); BACKLOG entries | Yes — reframed to truth (Item 7) |
| doc-19 known-deviation | — | Yes — "now conforms" (Item 8) |
| doc-25 dotted-leaf hedge | doc-25 (resolve Item-10 note) | Item-8 pin landed; Item-10 note pending |
| §8 "scans whole model" overclaim | — | Yes — §8 rewritten (Item 4) |

## Success Criteria

- [x] A docs-scrub-style spot-check (3 reference docs + matrix recount) passes at post-epic HEAD.
- [x] Zero occurrences of the retired caveats outside historical documents (grep evidence).
- [x] EXPLAINER_PROMPT.md contains no claim contradicted by post-epic HEAD; branch anchor →
  merged main + this epic's branch; Honest-caveats section rewritten to post-epic truth;
  cross-part story gains the SVM/materializer value-resolution mechanism; reading list gains
  the discovery register + this epic's artifacts; execution gate cites the GREEN Item-3
  acceptance run.
- [x] doc-25's Item-10-pending dotted-leaf note resolved (behavior kept + pinned; speculative
  tightening filed; forward-reference removed).
- [x] CURRENT_WORK.md carries the epic close-out summary (pending human actions: agentic-mbse
  companion PR from COMPANION_PR_BODY.md; PR #7 merge; fusion-tea workaround-retirement PR).
- [x] BACKLOG.md: absorbed PIPELINE-TRUTH entries retired; epic moved to Completed.
- [x] epic file: Status → Completed, SC checkboxes reconciled, Lessons Learned filled.

## Out of Scope

- Building the explainer HTML (its own prompt, its own session — this item only makes the
  prompt true).
- Any code/test/fixture change (docs-only working tree). The doc-25 part-blindness *tightening*
  is a code change → filed, not done.
- Re-litigating any Item 1–9 decision (all audited PASS).

## Required Reading

`.project/active/docs-scrub/{fact-sheet,audit}.md` (method); `EXPLAINER_PROMPT.md`;
`epic_pipeline_truth.md` Item 10; memory `verification-matrix-drift-modes`.
