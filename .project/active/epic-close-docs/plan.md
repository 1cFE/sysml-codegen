# Plan: Item 10 — Docs Refresh & Explainer-Prompt Revision (Epic Close)

**Spec**: `.project/active/epic-close-docs/spec.md`. **Status**: ✅ Complete (2026-07-06).
Docs-only. Pathspec commits; decision-leading messages; `Co-Authored-By: Claude Fable 5`.

---

## Phase 1 — Verify reference docs hold at post-epic HEAD (fact-sheet method)

Confirm each item's docs loop actually landed; no edits unless a residual caveat is found.

- [x] Matrix recount from the family index → 253/249/4/0, 30 families. (Done in spec-time
  verification; re-assert row-by-row in close-out.)
- [x] Grep `docs/architecture/` for every retired caveat's distinctive phrase; expect the
  only survivors to be the *truthful* post-decision statements (F4 not-yet-wired, §8
  subtype-aware). Record the grep evidence.
- [x] Spot-check 3 reference docs against HEAD (modeling-assumptions §8, doc-19, doc-03/04
  F4 status) — each claim traces to a code symbol or landed test.

## Phase 2 — Resolve doc-25's Item-10-pending dotted-leaf note

The doc explicitly defers the part-blindness decision to Item 10.

- [x] Decision: keep current leaf-only, part-blind behavior — it is pinned by
  `TestDottedLeafAliasMatch`, and no committed model triggers the edge; tightening is a code
  change out of Item 10's docs-only scope.
- [x] Rewrite doc-25's parenthetical to the resolved state (remove the forward-reference to
  Item 10; state the behavior is intentionally pinned-in-place, tightening filed).
- [x] File the speculative tightening as a P3 BACKLOG breadcrumb (register discipline).

## Phase 3 — Revise EXPLAINER_PROMPT.md

- [x] Branch anchor: `docs-scrub` → merged `main` (PR #4) + this epic's branch
  `pipeline-truth-epic`; note the post-epic docs are current at that HEAD.
- [x] "Honest caveats" section (item 7) rewritten to post-epic truth: V11 10-offender abort
  GONE (fusion-tea generates zero-offender via the SVM); constraints dropped but **loudly and
  subtype-aware** (assert included); cross-part support **broader than four shapes** (four
  wiring shapes + SVM value-fill a/b/c/d); F2 resolved fix-to-code; F4 resolved as
  built-parity-validated-not-yet-wired with the cutover filed (`[ITEM7-F4-CUTOVER]`) — no
  longer framed as an OPEN divergence. Keep the genuinely-still-true caveats
  (`attribute :>> attr = <expr>` silently dropped; EXPOSE_COMPUTED rejected).
- [x] Cross-part story (item 4): add the value-resolution mechanism — the supplied-value
  materializer (`resolution/supplied_values.py`, REQ-SVM), keyed by source QN, fan-out
  collapse.
- [x] Reading list: add the discovery register + this epic's artifacts (release notes /
  close-outs / the epic file).
- [x] Execution gate: cite the GREEN Item-3 fusion-tea acceptance run (run-C lcoe
  $270.1211779380445 bit-exact; zero-offender generation) instead of gating on the old
  open-caveat state.
- [x] Sweep the whole prompt for any other claim contradicted by post-epic HEAD (matrix
  count 248→253, terminology, fixture facts).

## Phase 4 — fact-sheet F6/F10 post-epic update

The fact sheet is explicitly named for caveat retirement. Add a clearly-marked POST-EPIC
UPDATE (do not rewrite the docs-scrub-era facts — mark what the epic changed).

- [x] F6 "Honest caveats": append a POST-EPIC UPDATE marking each caveat retired-by-epic
  with its item pointer.
- [x] F10 gate: note the post-epic gate (2069/4/5, ruff 17, mypy 104) supersedes the
  docs-scrub gate.

## Phase 5 — CURRENT_WORK + BACKLOG + epic file

- [x] CURRENT_WORK.md: epic close-out summary; the pending human actions (agentic-mbse
  companion PR from COMPANION_PR_BODY.md; PR #7 merge; fusion-tea retirement PR).
- [x] BACKLOG.md: mark the PIPELINE-TRUTH P1 row Completed with item checkboxes; move the
  epic to the Completed table with a one-line lessons pointer; leave the follow-on filings
  ([ITEM7-F4-CUTOVER], SYNC/SC11/etc.) in place (they outlive the epic).
- [x] epic_pipeline_truth.md: Status Draft → Completed; reconcile SC checkboxes to landed
  reality; fill the Lessons Learned block.

## Phase 6 — Self-check + close-out

- [x] Docs-scrub-style spot-check recorded (3 docs + matrix recount).
- [x] Caveat-retirement grep evidence recorded (live docs clean; historical retained).
- [x] EXPLAINER_PROMPT diff summary recorded.
- [x] Commits listed (pathspec, decision-leading).

## Implementation Notes

### All phases complete — 2026-07-06

**Phase 1 (verify reference docs).** Matrix recount from the family index = 253 = 249 PASS
+ 4 UNTESTED + 0 DEFERRED, 30 families (untested: DM 1, PGD 1, RES 2) — matches the header.
Caveat grep across `docs/architecture/` returned the retired caveats as **absent** and only
the truthful survivors present (F4 not-yet-wired in 03/04/05/matrix; §8 subtype-aware). Items
4/7/8 had already closed their doc loops — no reference-doc edits needed except doc-25.

**Phase 2 (doc-25).** Resolved the Item-10-pending dotted-leaf note: keep the current
part-blind behavior (pinned by `TestDottedLeafAliasMatch`; no model triggers it); rewrote the
parenthetical to the resolved state; filed the speculative tightening as
BACKLOG `[DOTTED-LEAF-PART-BLIND]` (P3).

**Phase 3 (EXPLAINER_PROMPT.md).** Diff summary:
- Branch anchor `docs-scrub` → `pipeline-truth-epic` (merged `main`/PR #4 noted); added the
  GREEN Item-3 acceptance-run certification line as the facts' grounding.
- §7 "Honest caveats" fully rewritten: kept the still-true limits (constraints dropped but
  loud+subtype-aware; `attribute :>> attr = <expr>` dropped; EXPOSE_COMPUTED rejected;
  `resolve_input` built-but-not-yet-wired, framed as truth not a divergence) and added an
  explicit **"Retired by PIPELINE-TRUTH — do NOT present as open"** list (V11 10-offender
  abort, assert-constraint silence, four-shapes limit, F2/F4 "open" divergences, run-C
  recorded-not-reproduced).
- §4 cross-part story split into channel-wiring + value-resolution; added the supplied-value
  materializer (`resolution/supplied_values.py`, REQ-SVM, source-QN keying, a/b/c/d shapes,
  fan-out collapse).
- §1 responsibility map gained an SVM row.
- Reading list: matrix count 248/236/12 → 253/249/4 + recount-from-index note; added the
  discovery register, the epic file, and the PIPELINE-TRUTH item close-outs; pointed at the
  fact-sheet F6/F10 POST-EPIC UPDATE.

**Phase 4 (fact-sheet).** Added POST-EPIC UPDATE blocks to F6 (caveats retired-by-epic, with
item pointers; `attribute :>>` noted as the one that stands) and F10 (gate 2069/4/5, ruff 17,
mypy 104 supersedes the docs-scrub gate). Historical docs-scrub-era facts left intact.

**Phase 5 (CURRENT_WORK / BACKLOG / epic file).** CURRENT_WORK gained an epic-complete summary
+ the 3 human actions (agentic-mbse companion PR, PR #7 merge, fusion-tea retirement PR).
BACKLOG: P1 PIPELINE-TRUTH row retired → Completed table (with per-item recap + kept follow-on
filings); `[DOTTED-LEAF-PART-BLIND]` filed. Epic file: Status → ✅ Completed; SC-A..H checkboxes
reconciled to landed reality; Lessons Learned block filled (7 lessons + human actions).

**Phase 6 (self-check).** Spot-check of 3 reference-doc claims against source — all pass:
1. modeling-assumptions §8 subtype-aware report → `include_subtypes=True` at
   `extraction/extractor.py:113`, applied at `:136`.
2. doc-19 REQ-AST-10 → `tests/conformance/test_agg_literal_dispatch.py` exists.
3. doc-03/04 F4 → zero `resolve_input` production callers in `src/` (grep empty outside
   `input_resolver.py`); live path `_resolve_aggregation_input_channel` at
   `graph_builder.py:1212`, called `:1282`.
Matrix recount re-asserted from the family index (253/249/4/0, 30 families).

**Caveat-retirement grep evidence.** Live docs (`docs/architecture/`, EXPLAINER_PROMPT,
fact-sheet F6/F10, BACKLOG P1/Completed, CURRENT_WORK) carry no retired caveat as a live
claim. Historical documents (work reports under `.project/active/{cross-part-wiring,
whole-plant-resolution,fusiontea-acceptance,plant-value-fixtures}/`, `EPIC_PR_BODY.md`,
`NEXT_EPIC_PROMPT.md`, the discovery register, `epic_upstream_findings.md`) retain the
pre-epic phrasing as the record of what was true then — deliberately left.

**Gate:** docs-only change; suite untouched. `ruff check src/` = 17, `mypy src/` = 104
(re-run this session, confirming the cited numbers).
