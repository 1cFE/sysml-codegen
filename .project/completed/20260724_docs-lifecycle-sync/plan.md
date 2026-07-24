# Implementation Plan: Docs Lifecycle Sync

**Status:** Approved (owner, 2026-07-24)
**Created:** 2026-07-20
**Last Updated:** 2026-07-24 — re-reviewed against merged main `936315c`; added the
resolver-architecture phase (spec R6) and the absorbed P3 sweeps (spec R7); 4 phases → 5

## Source Documents
- **Spec:** `.project/active/docs-lifecycle-sync/spec.md` (light spec; no separate design —
  the "design" is Item 6's proven method, cited below)
- **Method referent:** `.project/completed/20260720_constraint-lifecycle-docs-f1/spec.md` §2–§3
  `[REFERENT]` — the three-sweep inventory with per-claim disposition and citations is the bar
  to match, not just an illustration.

## Implementation Strategy

**Phasing Rationale:** Inventory first — every downstream fix depends on the claim register,
and the sweep is where unknown stale claims hide (Items 7–13 landed after Item 6's sweep).
Then the resolver-architecture family (R6) as its own phase: it is the largest stale mass
(two whole docs plus four files of references) and other docs cross-reference the resolver
story, so fixing it early keeps later phases from citing docs about to be rewritten. Then the
two known gaps (G1 doc, G2 matrix row). EXPLAINER_PROMPT last: it summarizes the docs, so it
re-anchors against corrected docs, not stale ones.

**Critical Path:** sweep register → resolver-family rewrite (R6) → remaining STALE fixes →
G1 severity doc → G2 matrix row → EXPLAINER re-anchor.

**First Proof Point:** the Phase 1 register — if the sweep returns dispositions with citations
for the six late-change areas (resolver unification, v5 snapshot, written qualifiers, catalog
2.0.0, producer completeness, trust manifest), the method transferred and the rest is writing.

**Validation Approach:** docs work has no test-first stencil; the equivalent gate is: every
claim written carries a code citation checked against merged main `936315c`, and the matrix
recount reconciles. Grep-based checks pin the mechanical invariants.

---

## Phase 1: Inventory Sweep (R3)

### Goal
A per-claim disposition register for `docs/architecture/` vs merged main, covering at minimum:
snapshot format v5 + written-qualifier fields, catalog schema 2.0.0, producer completeness,
trust manifest/anchor, and re-checking Item 6's ACCURATE verdicts for areas Items 7–13 touched.

### Assumption Under Test
That Item 6's sweep verdicts survived Items 7–13's landings. Expectation: some did not.

### Register Stencil (write this first)
```markdown
| # | Claim (file:line) | Disposition | Citation proving it | Fix |
|---|---|---|---|---|
| S1 | 28-…:74 "catalog schema 1.x" | STALE | catalog_store.py:NN (2.0.0) | amend in place |
```

### Changes Required
- [x] Four sweeps per the method referent: (A) version/format literals, (B) snapshot/catalog/
      trust surfaces, (C) semantics claims (completeness, qualifiers, severity mentions,
      module_kind vs retired bool flags, doc-19 dispatch table — spec R7), (D)
      resolver-architecture claims (`input_resolver`, `resolve_input`, `AGG_STRATEGIES`,
      `DesignAttributeLookup`, dual-resolution narrative — spec R6; known files: docs 03, 04,
      05, 24, overview, verification-matrix).
- [x] Write the register to `.project/active/docs-lifecycle-sync/inventory.md`.
- [x] Apply small STALE fixes in place (shrink/amend, citation per fix, no "used to say X"
      prose). Whole-doc R6 work is Phase 2, not here — register it, don't fix it inline.
- [x] R5 lands here: grep docs for override-capture *correctness* claims; add the
      def-relative limitation note where capture is described (8+ docs mention `:>>`; only
      correctness claims need the note).

### Validation
- [x] Every register row has a disposition + citation.
- [x] `grep -rn 'snapshot_format_version\|executable-profile/v\|schema.*2\.0\.0' docs/` —
      every live literal matches the pinned constant in `src/` (catalog `2.0.0` has no doc
      mention → B1 GAP, not a stale literal).
- [x] No doc claims nested-occurrence override capture works.

**What We Know Works After This Phase:** the full claim surface is enumerated; remaining
phases are additive writing, not discovery.

---

## Phase 2: Resolver-Architecture Reconciliation (R6 + the R7 module_kind sweep)

### Goal
No doc describes the deleted resolver architecture; the unified producer-resolution ladder
has a reference-doc home; the retired bool-flag claims are swept to `module_kind`.

### Assumption Under Test
That Item 2's design/evidence docs
(`.project/completed/20260720_constraint-lifecycle-shared-resolution/`) contain enough to
project a public reference doc without re-deriving the ladder from code. If projection
contradicts merged code, surface it loudly — don't silently harmonize.

### Changes Required
- [x] Replace `04-input-resolver.md` with a producer-resolution reference doc (`KEY_FORMS`
      table, `resolve_producer` entry point, Tier/`TerminalPolicy` split, the three consumer
      paths, `producer_completeness` check) — default treatment per spec R6; finalize
      replace-vs-retire against the Phase 1 register.
- [x] Amend `24-dual-resolution-architecture.md` to the unified-ladder narrative (its
      dual-resolution framing is now dated history — mark or rewrite, per register).
- [x] Fix in-place references in docs 03, 05, `overview.md`, and matrix rows.
- [x] R7 module_kind sweep in the same pass: doc 05's 7 bool-flag claims,
      `22-output-schema-rules.md:179`, matrix REQ-MF-03 text (together, so doc 05 and the
      matrix don't split).
- [x] Doc 19 prose table reconciled to `DUAL_CHECK_SITES` (R7's second half).

### Validation
- [x] `grep -r 'input_resolver\|resolve_input\|AGG_STRATEGIES\|DesignAttributeLookup' docs/architecture/`
      → zero live claims.
- [x] `grep -r 'is_computed_attribute\|is_aggregation' docs/architecture/` → zero live claims.
- [x] Every behavioral claim in the new/amended docs carries a merged-main citation.

**What We Know Works After This Phase:** the largest stale family is gone; later phases cite
stable resolver docs.

---

## Phase 3: Severity-System Reference Doc (R1 / gap G1)

### Goal
A public home for the diagnostics severity contract in `docs/architecture/reference/`
(number it after the existing 27/28/29 series).

### Assumption Under Test
That Item 4's archived artifacts contain everything the doc needs (they were audit-certified;
if projection surfaces a contradiction with merged code, surface it — don't silently pick).

### Changes Required
- [x] New doc: constraint-facts/v2 `DiagnosticSeverity`, the `screen_extraction_diagnostics`
      sink, fail-closed skew both directions, BLOCK/warning ordering. Project from
      `20260720_constraint-lifecycle-diagnostics-defaults/` artifacts; cite
      `analysis/diagnostic_screen.py`, `_upstream_pins.py:24-27`, `snapshot/loader.py:588-591`
      at their merged-main line numbers.
- [x] Link from doc 27/28 neighbors and any doc index.

### Validation
- [x] Every behavioral claim in the new doc carries a merged-main citation.
- [x] A reader can answer "what happens on severity skew in each direction" from the doc alone.

**What We Know Works After This Phase:** G1 closed — the severity system is publicly documented.

---

## Phase 4: Portability Matrix Rows (R2 / gap G2)

### Goal
REQ-SNAP row(s) for the v5 referent shape gate and whole-tree portability, with reconciled
index counts.

### Assumption Under Test
That the matrix recount discipline (memory `verification-matrix-drift-modes`) catches the
index-count changes the row addition causes.

### Changes Required
- [x] Add row(s) after REQ-SNAP-20 citing `_validate_source_referents` (`snapshot/loader.py`)
      and the portability tests. (Brief's suggested test file was corrected — see notes.)
- [x] Recount: index totals + per-family counts, not just the summary block.

### Validation
- [x] Matrix index counts reconcile after the recount pattern.
- [x] Row citations point at merged-main lines that exist.

**What We Know Works After This Phase:** G2 closed — portability is matrix-tracked.

---

## Phase 5: EXPLAINER_PROMPT Re-Anchor (R4)

### Goal
`.project/active/EXPLAINER_PROMPT.md` claims match merged main, feeding `[V2-HTML-BUILD]`
(which stays with its assigned owner — Non-Goal here).

### Assumption Under Test
That the Gen-1 banner / pipeline claims drifted during the epic (carried, unverified — the
sweep register from Phase 1 tells us exactly which claims to re-anchor).

### Changes Required
- [x] Re-anchor stale claims against the Phase 1 register and merged main; amend in place.

### Validation
- [x] Spot-check the prompt's pipeline/version claims against the register — zero contradictions.

**What We Know Works After This Phase:** the V2 HTML build has a truthful input.

---

## Risk Management

- **Sweep breadth underestimate** (Items 7–13 touched more docs than listed): the register is
  the containment — file GAP rows rather than expanding fix scope mid-phase.
- **Matrix recount errors**: known drift modes are documented in memory
  (`verification-matrix-drift-modes`); follow the recount pattern exactly.
- **Severity doc contradicts merged code**: surface loudly per the spec's projection rule;
  don't silently harmonize.

## Implementation Notes

### Phase 1 Completion
**Completed:** 2026-07-24 · **Baseline:** merged main `936315c`

**Register produced:** `.project/active/docs-lifecycle-sync/inventory.md` — 4 sweeps, every row
carries disposition + citation re-verified at `936315c`.

**Sweep findings (headline):**
- Sweep A (version literals): doc 27/matrix already at v5/v4 (Item 6 held through Items 7–13).
  Only residue: one citation line-drift (A1).
- Sweep B: catalog schema `2.0.0`, `written_qualifier`, trust manifest, severity contract, and
  portability all confirmed as **GAPs** (no stale claim; owed writing) → Phase 3/4/GAP-filed.
- Sweep C: retired `is_computed_attribute`/`is_aggregation` survive as 8 live claims (doc 05,
  22:179, matrix REQ-MF-03); doc 09 narrative is accurate. Deferred to Phase 2 (see below).
- Sweep D: `input_resolver.py` deleted, zero live `resolve_input`/`AGG_STRATEGIES` surface in
  `src/`; 6 doc files still describe it. `producer_resolution`/`producer_completeness` appear in
  no doc. Whole family → Phase 2.

**Changes made (in-place, this commit):**
- `docs/architecture/reference/27-snapshot-generation.md:37` — citation `snapshot/__init__.py:28`
  → `:30` (constant moved since Item 6; value `5` was already correct).
- `docs/architecture/modeling-assumptions.md` (Cross-Part Supplied Values §) — added the
  nested-occurrence def-relative limitation note (R5), citing `[NESTED-OCCURRENCE-OVERRIDE]`
  (BACKLOG.md:168) and the probe fixture.

**Deviation from plan (surfaced, not silently resolved):** the brief lists "sweeps A–C class"
small fixes as Phase-1 work, but plan Phase 2 explicitly bundles the `module_kind` sweep (doc
05 + matrix REQ-MF-03, "so they don't split"). Followed the plan's specific assignment: sweep-C
bool-flag rows are registered STALE with fix = Phase-2, not fixed here. Rationale and full
citations in `inventory.md` (⚠ surfaced note). The rows are mechanical if the owner wants them
pulled forward.

**Validation:** register rows all carry citations; version-literal grep clean (catalog `2.0.0`
is a GAP, not a stale literal); no doc implies nested-occurrence override capture works. The
`is_computed_attribute`/`resolve_input` greps are **not** yet zero — those are Phase 2's exit
gates (plan.md:106,108), deferred by design.

---


### Phase 2 Completion
**Completed:** 2026-07-24 · **Baseline:** merged main `936315c`

**Changes made:**
- Renamed `04-input-resolver.md` → `04-producer-resolution.md` (rename chosen per spec R6
  default; all inbound `04-input-resolver` links across `docs/` repointed). Rewrote it as the
  producer-resolution reference: KEY_FORMS ladder (21 rows, tier/lenient-only), `resolve_producer`
  as sole entry, TerminalPolicy strict-vs-lenient fork, the three consumer paths, and
  `check_producer_completeness`. Cited merged-main lines throughout.
- Rewrote `24-dual-resolution-architecture.md` to "one authority, two pipeline stages"; the
  pre-unification dual-path story kept only under a clearly-marked "Dated history" block.
- In-place: `03-resolution-overview.md`, `05-module-factory.md`, `overview.md` reframed to the
  unified resolver; `22-output-schema-rules.md:179` and doc-05 `module_kind` sweep (C1–C9);
  matrix REQ-MF-03 (C8). Doc 19 dual-check table reconciled to `DUAL_CHECK_SITES` (R7 second half).
- Matrix (D6): DRA/IR banners + rows re-projected onto `resolve_producer()`; dead-test citation
  `test_input_resolver.py` (deleted with the module) replaced by the live producer tests.

**Deviation surfaced (capture-fidelity rule 4):** the matrix REQ-IR family documented the deleted
`resolve_input()` and cited a deleted test as PASS. Register D6 disposition is "in-place rows," so I
kept the REQ-IR/REQ-DRA IDs and re-projected each row onto the shared table's successor guarantee
with its live test (no recount; counts stay 274/32). A dedicated `REQ-PR-*` family for the shared
table is a filed matrix GAP (spec R2), not required by this item — noted in both banners so the gap
is surfaced, not hidden. No merged-code contradiction found against Item 2's design/evidence.

**Validation (exit greps at `936315c`):** both Phase-2 greps return zero LIVE claims —
`input_resolver|resolve_input|AGG_STRATEGIES|DesignAttributeLookup` and
`is_computed_attribute|is_aggregation`. Residual hits are all clearly-marked dated history: doc 24's
history block, the matrix DRA deletion note, and doc 09's accurate retirement narrative (register C9).

**Status**: Draft → In Progress → Complete

---

### Phase 3 Completion
**Completed:** 2026-07-24 · **Baseline:** merged main `936315c` (codegen), `f4ebdce` (agentic-mbse)

**Changes made:**
- New doc `docs/architecture/reference/30-diagnostic-severity.md` — the extraction-diagnostic
  severity contract: `DiagnosticSeverity` (BLOCKING|ADVISORY), severity set by the writer at
  construction from the closed `EXTRACTION_DIAGNOSTIC_SEVERITY` table (no reader-side lookup), the
  `screen_extraction_diagnostics` sink at both routes, advisory-before-block ordering, and the
  three stacked fail-closed guards for skew in both directions. Cited merged-main lines throughout
  (codegen `diagnostic_screen.py`, `pipeline_builder.py:898`, `snapshot_context.py:48`,
  `snapshot/loader.py`, `_upstream_pins.py:24-27`; agentic-mbse `constraint_facts.py`).
- Linked from doc 27:86 (severity-field changelog mention → cross-ref to doc 30 — the judgment-call
  edit the brief flagged; taken, it improves discoverability without disrupting the migration
  narrative), doc 28's opening (extraction diagnostics screened before lowering), and the nav index
  in `00-pipeline-overview.md`. Added rows 28/29/30 to that index's Deep-dive table — 28/29 were
  absent (pre-existing index gap); completing the trio while adding 30 keeps the index honest.

**Deviation surfaced (brief vs code — resolved by documenting both, not silently picking):** the
brief pins "where the gate runs on the snapshot path" to `snapshot/loader.py:588-591`. Code shows
that range is the severity-field **shape** validation (`_validate_diagnostic`), a complementary
mechanism; the actual **screen gate** on the snapshot path is `orchestration/snapshot_context.py:48`
(before `build_full_graph_from_snapshot`). Doc 30 documents both accurately and distinguishes them.

**Fuller-than-brief finding (code wins, recorded):** the design's I2 framed fail-closed skew as the
version gate alone. Merged code also carries a per-diagnostic **severity cross-check** at
reconstruction (`agentic-mbse constraint_facts.py:374-385`): severity is re-derived from the
reader's writer-table and refused if it disagrees with the stored value, in either direction. This
catches a reclassification that skipped a version bump. Doc 30 documents all three guards (version
gate → severity cross-check → unknown-kind refusal), which is what lets a reader answer the
skew question from the doc alone. Writer table currently has one kind (`non_finite_literal` →
BLOCKING) — documented as-is.

**Validation:** every behavioral claim in doc 30 carries a merged-main citation; the "what happens
on severity skew in each direction" question is answerable from the doc's dedicated section. G1 closed.

---

### Phase 4 Completion
**Completed:** 2026-07-24 · **Baseline:** merged main `936315c`

**Changes made:**
- `verification-matrix.md`: added `REQ-SNAP-21` (v5 referent shape gate —
  `_validate_source_referents`, `snapshot/loader.py:912`, called `:837`; rejects absolute /
  snapshot-dir-relative / stale, sentinels pass) and `REQ-SNAP-22` (whole-tree portability, Item 5
  Axis 1: two roots → byte-identical output, no checkout-absolute path). Both PASS.
- Recounted per memory `verification-matrix-drift-modes` (index totals + per-family, not just the
  summary): Total 274→276, PASS 273→275, UNTESTED 1, families 32, distinct test files 73→77; SNAP
  index `(20/20)`→`(22/22)`. Reconciliation verified: Σ index total = 276, Σ index pass = 275.
- Filed three matrix-GAP-row candidates in `inventory.md` (MG1 producer resolution/completeness,
  MG2 catalog 2.0.0, MG3 trust manifest) — recorded, not added to the matrix (spec R2: a later
  owner filing decision, not required by this item).

**Deviation surfaced (brief citation corrected — verified, no aspirational citation):** the brief
told me to cite `test_constraint_snapshot_portability.py` for whole-tree portability. That file
actually pins the exclusion-**relocation manifest** (3 tests: replay-manifest equality,
distinct-route collectors, live-capture relocation). The real pins are
`test_source_referent_shape_gate.py` + `test_snapshot_v5_gate.py` (the gate) and
`test_whole_tree_portability.py` (whole-tree). Cited the verified files.

**Pre-existing drift surfaced and corrected during the mandated recount (capture-fidelity rule 4):**
the index annotations for DM `(8/9 pass, 1 untested)` and RES `(6/8 pass, 2 untested)` were stale —
the actual table rows are all PASS (DM 9/9, RES 8/8); the only real UNTESTED row is REQ-PGD-06.
Three rows had flipped to PASS without the index following. Corrected DM→`(9/9)` and RES→`(8/8)` so
the index reconciles with the summary; this predates and is independent of the two new rows.
Recorded in `inventory.md` Phase 4 dispositions. G2 closed.

---

### Phase 5 Completion
**Completed:** 2026-07-24 · **Baseline:** merged main `936315c`

**Changes made** (`.project/active/EXPLAINER_PROMPT.md`, re-anchored in place; 19-row register
E1–E19 in `inventory.md`):
- Title/banner: "post-CONSTRAINT-EXEC" → "post-CONSTRAINT-LIFECYCLE, merged main"; branch
  `constraint-exec-epic` → `main` (`936315c`/`f4ebdce`/`fa0e06a`); "two epics" → three, with
  the six lifecycle deltas (resolver unification, severity contract, snapshot v5, package
  trust, sole-authority catalog 2.0.0, multi-entry bridge) named. Build para → merged main +
  the composed-proof anchor (41/41, stellarator 5 verdicts/6 anchors, IFE 2,301).
- Snapshot claims v3 → v5 (L1, responsibility row, retired list, prior-art); doc-27 changelog
  cited. Added a producer-resolution/completeness responsibility row (doc 04) and the
  generation-manifest/trusted-bootstrap surface to the contracts row.
- §2 gained the extraction-diagnostic severity contract (doc 30). §4 gained the
  `[NESTED-OCCURRENCE-OVERRIDE]` exception clause; §7 gained it as a live caveat and reframed
  the catalog/bridge caveat (CE-F2 landed, CE-F1 out-of-scope-by-design D-3). §8 anchored
  lowering to `resolve_producer` and corrected the CE-F1/CE-F2 history.
- Reading list: header → docs-lifecycle-sync; added docs 04/30; counts 274/273 → 276/275;
  epic paths backlog → completed; added the lifecycle epic as the newest authority.

**Deviation surfaced:** none material. The prompt's run-C `$270.12/MWh` anchor and all §3/§4
symbol/fixture citations were re-verified live against `src/` and `936315c` and kept (still
true — the lifecycle epic did not disturb them). No brief citation needed correcting this phase.

**Scope guard held:** no HTML build (`[V2-HTML-BUILD]` stays owner-assigned; spec Non-Goal);
docs-only, no code/test/fixture edits.

**Validation:** exit greps clean — no `constraint-exec-epic` / `post-CONSTRAINT-EXEC` /
`docs-explainer-refresh` / `backlog/epic_` / `04-input-resolver` / `format v3` / bare `274`
remain; the only `resolve_input`/`AGG_STRATEGIES`/`input_resolver` mentions are the
deleted/retired-history ones that name them as gone. Every re-anchored claim carries a
merged-main citation. R4 complete; all five phases done.
