# Implementation Plan: docs/ Full Scrub After UPSTREAM-FINDINGS

**Status:** Complete (audit pending)
**Created:** 2026-07-06
**Last Updated:** 2026-07-06

## Source Documents
- **Spec:** `.project/active/docs-scrub/spec.md` (success criteria + hard constraints live there)
- **Handoff:** `/tmp/handoff-20260706-064033.md` (ten Key Discoveries; the per-item docs map)
- No design doc — docs-only correctness pass, spec → plan → implement → audit.

## Implementation Strategy

**Phasing Rationale:**
Ground truth first (release notes + code symbols at HEAD), because every later phase
verifies docs *against* that truth — verifying docs against each other is the failure
mode the spec forbids. Then the contract docs (modeling-assumptions + matrix), because
every reference doc defers to them; fixing the contract first means reference-doc fixes
have a stable target. Then the epic-touched reference docs (known-thin prose is the
biggest known gap), then the untouched docs (unknown staleness), then mechanical
cross-cutting sweeps that would otherwise be missed doc-by-doc.

**Critical Path:**
Phase 1 fact sheet → Phase 2 contract docs → Phases 3/4 reference docs → Phase 5 sweeps + gate.

**First Proof Point:**
The Phase 1 fact sheet: if the release notes + code symbols can be assembled into an
unambiguous "what is true at HEAD" list, every later phase is mechanical. If they
conflict, that surfaces immediately, before any doc is edited.

**Resumability:**
The Phase 3/4 tables below have one row per doc with a Status cell. Update the cell
(`ok` / `fixed` / `flagged`) as each doc is finished. A fresh session resumes at the
first empty cell.

**Overall Validation Approach:**
- Docs-only: the gate (pytest / ruff / mypy) must be byte-identical to the epic baseline.
- Each phase ends with a named grep or recount that proves its claim.
- Commit per phase so drift is bisectable.

---

## Phase 1: Ground-Truth Fact Sheet

### Goal
Assemble the authoritative "true at HEAD" facts the scrub will verify docs against.
First because it de-risks everything: conflicts between release notes and code surface
here, not mid-edit.

### Assumption Under Test
The epic's release notes, audits, and code at HEAD agree with each other. (If they
don't, that's a finding to report, not silently reconcile.)

### Verification Stencil (run before editing any doc)
```bash
# Terms that must exist in src/ if docs are to use them:
grep -rn "ScopedAliasKey\|reference_chain\|EXPOSE_CHAIN_TENTATIVE\|fallback_entry_points\|output_aliases" src/ | head
# Term that must NOT appear anywhere (renamed during Item 10):
grep -rn "ConsumerScopedKey" src/ docs/
# Capture-script roles, from the docstrings (source of truth per handoff):
head -30 scripts/capture_*.py
```

### Changes Required
- [x] Read `.project/backlog/epic_upstream_findings.md` (the 12-item map)
- [x] Read the four `release-notes.md` files (Items 7, 9, 10, 11 — Item 9's exists too)
- [x] Confirm code symbols: `snapshot/` package, `--from-snapshot`, `ScopedAliasKey`,
      `output_aliases`/`OutputAlias`, `fallback_entry_points` (exclude=True),
      `reference_chain`, `EXPOSE_CHAIN_TENTATIVE` + Phase 3b confirm pass,
      `sanitize_qualified_name`, exit-point filename override
- [x] Confirm capture-script roles from docstrings
- [x] Write `.project/active/docs-scrub/fact-sheet.md` — one line per fact, with the
      code symbol or release-note section that proves it

### Validation
- [x] Fact sheet exists; every fact has a provenance pointer
- [x] `ConsumerScopedKey` grep over src/ returns nothing (else the spec's rename claim is wrong — stop and report)

**What We Know Works After This Phase:** every later doc edit has a checkable source.

---

## Phase 2: Contract Docs

### Goal
`modeling-assumptions.md` coherent end-to-end; `verification-matrix.md` summary
recounted from actual rows. These are the docs the reference tree defers to.

### Assumption Under Test
Six items' worth of independent edits to modeling-assumptions left seams — especially
the EXPOSE story spanning §3 / §5 / V-table.

### Verification Stencil
```bash
# Recount matrix rows by status column, compare to summary block:
grep -c "^|" docs/architecture/verification-matrix.md   # then count per-status
```

### Changes Required
- [x] Read `modeling-assumptions.md` end-to-end (not per-diff); fix seams; verify the
      EXPOSE story (§3 surfacing / §5 retyping / V7–V11) tells one story
- [x] Verify the V12/V13-reframe note still reads correctly against doc 16 / REQ-CA-03
- [x] Recount verification-matrix rows; correct the summary block from the table, not
      from the previous summary (233/221/12 was already stale once)
- [x] Preserve honest caveats (SC-2 graph-level-only, fusion-tea workarounds) — check
      each caveat sentence survives verbatim or stronger-in-honesty

### Validation
- [x] Matrix summary equals actual row counts (show the arithmetic in the commit message)
- [x] A read of modeling-assumptions top-to-bottom hits no contradiction with the fact sheet

**What We Know Works After This Phase:** the contract the reference docs point at is sound.

---

## Phase 3: Epic-Touched Reference Docs

### Goal
Every doc the epic touched describes HEAD, and the Item-7 thin-prose gap
(07/10/11/17/24) is closed.

### Assumption Under Test
Item-by-item edits were locally correct but the prose around them wasn't rewritten
(known true for 07/10/11/17/24; suspected elsewhere).

### Doc checklist (update Status as you go: `ok` / `fixed` / `flagged`)

| Doc | Known epic exposure | Status |
|-----|--------------------|--------|
| 01-extraction | Items 1, 3 (canonical example), 4 |  ok |
| 02-orchestration | Item 2 pointer |  fixed |
| 07-graph-assembly | Item 7 — **thin prose, rewrite** |  fixed |
| 09-data-models | Item 11 (`output_aliases`/`OutputAlias`) |  fixed |
| 10-output-registry | Items 7, 10 — **thin prose, rewrite** |  fixed + flagged (REQ-OR-05/06/08 vs Key_A/Key_F — BACKLOG F2) |
| 11-analysis-backtracker | Items 7, 10 — **thin prose, rewrite** |  fixed |
| 12-virtual-binding-rewrite | Items 9, 10 |  fixed |
| 15-naming-conventions | Item 5 (`sanitize_qualified_name`, fail-fast) |  fixed |
| 16-computed-attributes | Items 1, 10, 11 |  fixed |
| 17-parameter-group-deriver | Item 7 — **thin prose, rewrite** |  fixed |
| 19-ast-dispatch-invariant | Item 6 (REQ-AST-03/08/09, known-deviation note) |  fixed |
| 20-module-registry-generation | Item 5 |  fixed |
| 21-pipeline-yaml-generation | Item 11 (exit-point filename override, simkit grammar) |  fixed |
| 24-dual-resolution-architecture | Items 7, 10 — **thin prose, rewrite** |  fixed |
| 25-hierarchy-resolver | Items 4, 9, 10 |  fixed |
| 27-snapshot-generation | Item 2 (new) — verify against shipped code + script roles |  ok (matrix gained its REQ-SNAP-08..19 rows) |

### Changes Required
- [x] For each row: read the doc, verify each claim against the fact sheet / code,
      rewrite thin prose to match the REQ rows (matrix + modeling-assumptions carry the
      authoritative text — prose must agree, not diverge)
- [x] Convert `file:line` anchors to symbol anchors in every doc touched
- [x] Release-note behavioral changes (Items 7/10/11) each traceable to a doc statement

### Validation
- [x] Every row has a non-empty Status
- [ ] `grep -rn "ConsumerScopedKey" docs/` → nothing
- [x] Spot-check: each release-note behavioral change has a home in some doc

**What We Know Works After This Phase:** the epic's own docs are self-consistent with HEAD.

---

## Phase 4: Untouched Docs

### Goal
Docs the epic never opened don't contradict the new reality; 22/23/26 get an explicit
liveness verdict.

### Assumption Under Test
At least some of these describe pre-epic behavior as current (highest-risk: overview,
00, 03 — they describe the pipeline shape the epic changed).

### Doc checklist

| Doc | Risk notes | Status |
|-----|-----------|--------|
| overview.md | No snapshot/ package, no `--from-snapshot`? |  fixed |
| 00-pipeline-overview | Capture workflow roles (Discovery 7) |  fixed |
| 03-resolution-overview | Predates `reference_chain`/tentative-confirm terms |  fixed |
| 04-input-resolver | Terminology drift |  fixed + flagged (resolve_input cutover — BACKLOG F4) |
| 05-module-factory | Terminology drift |  fixed |
| 06-entry-point-classifier | Item-7 adjacency (entry-point semantics) |  fixed |
| 08-generation | Dead-template reference? (Discovery 5) |  fixed (dead templates de-listed; 2nd dead template found — BACKLOG F1) |
| 13-aggregation-scoping | Terminology drift |  fixed |
| 14-expression-compiler | Terminology drift |  fixed |
| 18-literal-value-propagation | (not in handoff's touched list — verify) |  fixed (REQ-LVP-08/09 rows added) |
| 22-output-schema-rules | Liveness verdict required |  fixed — verified LIVE, corrected |
| 23-smart-regen-preservation | Liveness verdict required |  fixed — verified LIVE, corrected |
| 26-pipeline-module-migration | Liveness verdict required |  fixed — HISTORICAL banner (end state verified true) |

### Changes Required
- [x] For each row: read against HEAD; fix contradictions; don't polish prose that's
      merely old but true
- [x] 22/23/26: check the subsystem exists and behaves as described; mark
      verified-live, corrected, or add an explicit status header (archived/superseded)
- [x] Any doc referencing `pydantic_schema.py.jinja2`: fix the doc, file the template
      deletion as a follow-up (no code change)

### Validation
- [x] Every row has a non-empty Status; 22/23/26 rows say what the verdict was
- [x] `grep -rn "pydantic_schema.py.jinja2" docs/` → nothing (or only as documented-dead)

**What We Know Works After This Phase:** no silent contradictions left in the tree.

---

## Phase 5: Cross-Cutting Sweeps + Gate

### Goal
Mechanical checks that don't belong to any one doc, plus the unchanged-gate proof.

### Changes Required
- [x] Repo-root `CLAUDE.md`: architecture section mentions `snapshot/` package and
      `--from-snapshot`
- [x] Terminology sweep over all of docs/: old names gone, new terms used consistently
      (`reference_chain`, `EXPOSE_CHAIN_TENTATIVE`/Phase 3b, `ScopedAliasKey`,
      `fallback_entry_points` vs `output_aliases` contrast)
- [x] `file:line` anchor sweep: `grep -rEn '\.py:[0-9]+' docs/` → fix or remove stragglers
- [x] "Doc 27" ambiguity check: links distinguish `reference/27-snapshot-generation.md`
      from the TRR design doc
- [x] Capture-workflow docs (27, 00, 02) state snapshot-driven vs live-license split
- [x] File follow-ups discovered en route (template deletion, any code bugs found) in
      the backlog — not fixed here

### Validation
- [x] All greps above clean
- [x] Gate: `uv run pytest tests/` → 1989 passed / 4 skipped / 5 xfailed;
      `ruff check src/` → 21; `mypy src/` → 109 (byte-identical baselines)
- [x] `git diff --stat upstream-findings-epic...docs-scrub -- . ':!docs' ':!.project' ':!CLAUDE.md'`
      shows nothing (docs-only proof)

**What We Know Works After This Phase:** spec success criteria all checkable-true; ready for `/_my_audit`.

---

## Risk Management

- **Verifying docs against each other** (spec [NEED]): the fact sheet is the only
  allowed truth source; Phase 1 exists to enforce this.
- **Over-cleaning honest caveats** (spec [HARD]): Phase 2 checks caveat sentences
  explicitly; the audit re-checks.
- **Scope creep into code**: any code smell found gets filed, never fixed here.
- **Silent skips across sessions**: the per-doc Status tables are the resume point.

## Implementation Notes

[TO BE FILLED DURING IMPLEMENTATION]

### Phase 1 Completion
**Completed:** 2026-07-06 ~06:55
**Actual Changes:** `fact-sheet.md` written (F1–F12, each fact with a code-symbol or release-note provenance pointer). No doc edits yet.
**Issues:** None. `ConsumerScopedKey` absent from src/ and docs/; all new-term symbols confirmed present in src/.
**Deviations:** Read four release-notes files, not three — Item 9 (plant-prefill) has one the handoff didn't list. Nuance corrected vs. my earlier assumption: Phase 3b (tentative→confirm) is a *registry-build* phase in `output_registry_builder.py`, not a backtracker phase — recorded in F5 so docs get it right.

### Phase 2 Completion
**Completed:** 2026-07-06 ~07:15
**Actual Changes:** modeling-assumptions.md — §3 gained the multi-hop chain row + EXPOSE_CHAIN_TENTATIVE/Phase-3b paragraph and a shape-A (part-def EXPOSE) paragraph; §5 gained the specialization-chain precedence rule (REQ-VBR-10/11) and the bare-`:>>`-form caveat (F6); V-table intro corrected (V1–V10 extraction-time, V11 generation-boundary). verification-matrix.md — summary block verified CORRECT against the table (233 total = 221 PASS + 12 UNTESTED; no drift since Item 11), but 9 Index family counts were stale (AST 7→9, BT 8→11, EXT 9→14, GA 7→8, HR 7→8, LVP 7→9, OR 8→9, PGD 7→8, VBR 7→11) and the test-file metric was wrong (34 → 49 distinct files cited; label clarified since some cited files are unit tests).
**Issues:** The predicted summary-block drift (Discovery 2) did NOT materialize — the drift was in the Index counts instead. Same lesson, different block.
**Deviations:** SC-2/fusion-tea caveat sentences turn out to live in release notes, not docs/ — nothing to preserve-check in the contract docs; the constraint remains "don't strengthen claims" for Phases 3–5.

### Phase 3 Completion
**Completed:** 2026-07-06 ~08:00 (13 parallel agents for Phases 3+4, one truth source)
**Actual Changes:** 14 of 16 docs edited (see table; 01 and 27 verified accurate as-is). The five thin-prose docs (07/10/11/17/24) now describe HEAD: V11 collector + boundary, Phase 3b confirm walk, scoped-alias Step 1b/1c ladder, matcher fixes REQ-BT-09/10, offline-parity corrections. Doc 02's step-ordering table was false (group deriver listed before the registry; it runs at Step 5.7 after) — fixed. Matrix gained REQ-SNAP-08..19 (epic omission found via doc 27) and REQ-GA-05/CA-01/CA-11 rows were revised in place to match deliberate code revs.
**Issues:** One REQ-vs-code disagreement correctly left unedited and filed: REQ-OR-05/06/08 claim Key_A/Key_F are never registered; code registers both (BACKLOG DOCS-SCRUB-F2).
**Deviations:** More matrix edits than planned (SNAP/NC/REG families were missing rows the reference docs define with existing passing tests — added: 233→248 total, 221→236 PASS, 49→54 files; arithmetic re-verified from rows after each edit).

### Phase 4 Completion
**Completed:** 2026-07-06 ~08:00 (same fan-out as Phase 3)
**Actual Changes:** All 13 docs edited. overview + 00 gained the snapshot path (--from-snapshot, capture roles/license split), 4-registry + Phase 3b story, and corrected counts (204→245-era claims; the false "doc 27 merged into doc 10" claim removed). 03/04/05/06: resolution ladders rewritten to the HEAD dispatch (nonexistent strategies/forms removed — Strategy D is a no-op, documented as such); JSON null-key omission corrected in 06. 08: dead templates de-listed (a second one found), nonexistent templates removed, REQ-PIPE-07 gap section rewritten as completed. 13/14/18: anchors + REQ tables brought current. Verdicts: 22 LIVE (corrected), 23 LIVE (corrected), 26 HISTORICAL (banner added; end state verified true at HEAD).
**Issues:** Biggest finding of the scrub: resolve_input()/AGG_STRATEGIES has zero production call sites while REQ-IR-05/07/REQ-RES-02 mark it PASS — filed as BACKLOG DOCS-SCRUB-F4; REQ-mirroring prose deliberately left in docs 03/04/05 pending that reconciliation.
**Deviations:** None beyond the flags filed.

### Phase 5 Completion
**Completed:** 2026-07-06 ~08:30
**Actual Changes:** CLAUDE.md: snapshot package + --from-snapshot (commands + pipeline step 5). Backlog: DOCS-SCRUB-F1 (two dead templates + 4 dead-code candidates), F2 (REQ-OR reconciliation), F3 (stale code docstrings), F4 (resolve_input cutover). Sweeps all clean: ConsumerScopedKey absent from docs/ and CLAUDE.md; zero file:line anchors in docs/; dead templates mentioned only as documented-dead (doc 08); no ambiguous doc-27 links.
**Issues:** None. Gate byte-identical: 1989 passed / 4 skipped / 5 xfailed; ruff src/ 21; mypy src/ 109.
**Deviations:** uv.lock was already modified before this session started — left uncommitted, not part of the scrub.

---

**Status**: Complete (audit pending)
