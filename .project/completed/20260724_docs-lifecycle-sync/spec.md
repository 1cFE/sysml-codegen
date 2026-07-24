# Spec — Docs Lifecycle Sync (post-CONSTRAINT-LIFECYCLE documentation reconciliation)

**Status:** Approved (owner, 2026-07-24) — re-verified against merged main before start
**Created:** 2026-07-20 · **Re-reviewed:** 2026-07-24 (all cited facts re-checked at `936315c`;
R6 added — the resolver unification was missing from the original scope)
**Baseline:** merged main — sysml-codegen `936315c`, agentic-mbse `f4ebdce`, teax `fa0e06a`
(no commits landed on any of the three mains since 2026-07-20; baseline unchanged).
**Authority:** the deferred-documentation register from the closed epic
(`.project/completed/20260720_epic_constraint_execution_lifecycle_remediation.md`) and Item 6's
gap register (`.project/completed/20260720_constraint-lifecycle-docs-f1/spec.md` §3c).

This is a light spec: the epic already did the discovery; this item does the owed writing and
one fresh sweep. Requirements inherit their grades from the epic artifacts.

---

## 1. Intent

Make `docs/architecture/` agree with merged main after the epic's late changes, and give the
two known coverage gaps (severity system, portability matrix row) real doc homes. A correction
shrinks or amends the stale claim in place with a code citation; a gap gets new coverage. No
release-readiness claims anywhere — that record is closed and archived.

## 2. Requirements

- **R1 `[INHERITED: Item 6 gap G1]` — Document the diagnostics severity system.** The
  severity contract (constraint-facts/v2 `DiagnosticSeverity`, fail-closed skew in both
  directions, BLOCK/warning ordering) has no public doc coverage beyond one passing
  changelog mention (doc 27:86, "v4 carried the diagnostic-severity field" — verified
  2026-07-24; no doc describes the contract itself). Landed surface:
  `analysis/diagnostic_screen.py`, `_upstream_pins.py:24-27`, `snapshot/loader.py:588-591`.
  Home: `docs/architecture/reference/` near docs 27/28. Item 4's archived artifacts
  (`20260720_constraint-lifecycle-diagnostics-defaults/`) hold the content to project.
- **R2 `[INHERITED: Item 6 gap G2]` — Add the portability verification-matrix row(s).** The
  v5 referent shape gate (`_validate_source_referents` in `snapshot/loader.py`) and the
  whole-tree portability contract have no REQ-SNAP row (family stops at REQ-SNAP-20). Adding
  rows changes matrix index counts — follow the recount discipline (memory
  `verification-matrix-drift-modes`: recount index totals + check for missing REQ families,
  not just the summary block). Wider signal (verified 2026-07-24): the matrix still has its
  pre-epic 274 REQ rows — the whole epic added none — so the sweep should also file GAP rows
  for other new surfaces without matrix coverage (producer resolution/completeness, catalog
  schema 2.0.0, trust manifest); adding those rows is a filing decision at the register, only
  the portability row is required by this item.
- **R3 `[INFERRED]` — Sweep `docs/architecture/` against merged main.** The epic landed large
  changes after docs 27/28 were last re-projected: v5 snapshot format, written-qualifier
  fields (in `usage_extractor.py`, no doc coverage), catalog schema 2.0.0 (docs 28/29 carry
  no version mention — verified 2026-07-24), producer completeness, trust manifest/anchor
  (`contracts/manifest.py`, no doc coverage), plus the resolver unification (carved out as
  R6, the largest family). Item 6's sweep predates Items 7–13's landings, so its ACCURATE
  verdicts for those areas are not current.
  Method is fixed: reuse Item 6's three-sweep inventory (per-claim STALE / ACCURATE /
  AMBIGUOUS / GAP disposition, every STALE verdict carrying the code citation that proves it).
- **R4 `[INHERITED: close handoff]` — Re-anchor `EXPLAINER_PROMPT.md`**
  (`.project/active/EXPLAINER_PROMPT.md`). Last touched pre-epic; the Gen-1 banner and any
  pipeline claims may be stale vs merged main. This item re-anchors the prompt only; the
  `[V2-HTML-BUILD]` HTML build itself stays owner-assigned-elsewhere (Non-Goal).
- **R5 `[INHERITED: close handoff]` — Override-capture honesty.** Wherever docs describe
  `:>>` override capture, state the def-relative limitation plainly
  (`[NESTED-OCCURRENCE-OVERRIDE]`, BACKLOG P2; probe fixture
  `tests/fixtures/nested_occurrence_override_probe/`). Docs must not imply nested-occurrence
  overrides are captured correctly. Surface is wide: 8+ reference docs mention
  `design_override`/`:>>` capture (verified 2026-07-24) — only claims about *capture
  correctness* need the note, not every mention.
- **R6 `[INFERRED, added at 2026-07-24 re-review]` — Reconcile the resolver-architecture
  docs with the Item-2 unification.** The largest stale family, missed by the original spec:
  lifecycle Item 2 replaced the dual resolver ladders with one registry-owned ordered table
  (`resolution/producer_resolution.py` — `KEY_FORMS:527`, single entry `resolve_producer:616`,
  strict/lenient split only at `TerminalPolicy`) and DELETED `resolution/input_resolver.py`
  (with `resolve_input`/`AGG_STRATEGIES`/`DesignAttributeLookup`). At `936315c`, six doc files
  still describe the old architecture — `04-input-resolver.md` (309 lines, documents the
  deleted module), `24-dual-resolution-architecture.md` (316 lines, pre-unification
  narrative), `03-resolution-overview.md`, `05-module-factory.md`, `overview.md`, and
  `verification-matrix.md` rows — while `producer_resolution`/`producer_completeness` appear
  in NO doc. Default treatment (finalize at implementation against the register): replace
  doc 04 with a producer-resolution reference doc; amend doc 24 to the unified-ladder
  narrative; fix references elsewhere in place. Evidence referent:
  `.project/completed/20260720_constraint-lifecycle-shared-resolution/{design,evidence}.md`.
- **R7 `[INHERITED: BACKLOG P3 filings, absorbed 2026-07-24]` — Fold in the two standing doc
  sweeps.** `[MODULEKIND-DOC-SWEEP]`: the retired `is_computed_attribute`/`is_aggregation`
  bool flags survive as live claims (7 hits in `05-module-factory.md`,
  `22-output-schema-rules.md:179`, matrix REQ-MF-03 — re-verified 2026-07-24); sweep them to
  `module_kind` together so doc 05 and the matrix don't split. `[DOC19-DISPATCH-REAUDIT]`:
  reconcile doc 19's prose dispatch-site table with the authoritative `DUAL_CHECK_SITES`
  inventory it already points to (`19-ast-dispatch-invariant.md:98,132`). Both BACKLOG
  entries get absorbed-markers pointing here.

## 3. Non-Goals

- Out of scope: building `pipeline_explainer_v2.html` (`[V2-HTML-BUILD]`) — owner-assigned to
  another agent; this item only makes its input prompt truthful.
- Out of scope: fixing `[NESTED-OCCURRENCE-OVERRIDE]` itself — R5 documents the limitation;
  the fix is a separate backlog decision.
- Out of scope: teax/agentic-mbse doc trees — this item covers sysml-codegen's `docs/` and
  `EXPLAINER_PROMPT.md`. Cross-repo doc debt, if the sweep surfaces any, gets filed, not fixed.

## 4. Success Criteria

- Every claim in the sweep register has a disposition with a citation; every STALE claim is
  amended in place.
- A severity-system reference doc exists and is linked from the doc index/neighbors.
- The verification matrix has the portability row(s) and its index counts reconcile.
- `EXPLAINER_PROMPT.md` claims match merged main.
- No doc claims nested-occurrence override capture works.
- `grep -r 'input_resolver\|resolve_input\|AGG_STRATEGIES\|DesignAttributeLookup' docs/architecture/`
  returns zero live claims (dated-history mentions allowed if clearly marked), and the
  producer-resolution architecture has a reference-doc home.
- `grep -r 'is_computed_attribute\|is_aggregation' docs/architecture/` returns zero live
  claims; doc 19's prose table matches `DUAL_CHECK_SITES`.
