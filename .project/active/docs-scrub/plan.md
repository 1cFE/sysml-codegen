# Implementation Plan: docs/ Full Scrub After UPSTREAM-FINDINGS

**Status:** Draft
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
- [ ] Read `modeling-assumptions.md` end-to-end (not per-diff); fix seams; verify the
      EXPOSE story (§3 surfacing / §5 retyping / V7–V11) tells one story
- [ ] Verify the V12/V13-reframe note still reads correctly against doc 16 / REQ-CA-03
- [ ] Recount verification-matrix rows; correct the summary block from the table, not
      from the previous summary (233/221/12 was already stale once)
- [ ] Preserve honest caveats (SC-2 graph-level-only, fusion-tea workarounds) — check
      each caveat sentence survives verbatim or stronger-in-honesty

### Validation
- [ ] Matrix summary equals actual row counts (show the arithmetic in the commit message)
- [ ] A read of modeling-assumptions top-to-bottom hits no contradiction with the fact sheet

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
| 01-extraction | Items 1, 3 (canonical example), 4 | |
| 02-orchestration | Item 2 pointer | |
| 07-graph-assembly | Item 7 — **thin prose, rewrite** | |
| 09-data-models | Item 11 (`output_aliases`/`OutputAlias`) | |
| 10-output-registry | Items 7, 10 — **thin prose, rewrite** | |
| 11-analysis-backtracker | Items 7, 10 — **thin prose, rewrite** | |
| 12-virtual-binding-rewrite | Items 9, 10 | |
| 15-naming-conventions | Item 5 (`sanitize_qualified_name`, fail-fast) | |
| 16-computed-attributes | Items 1, 10, 11 | |
| 17-parameter-group-deriver | Item 7 — **thin prose, rewrite** | |
| 19-ast-dispatch-invariant | Item 6 (REQ-AST-03/08/09, known-deviation note) | |
| 20-module-registry-generation | Item 5 | |
| 21-pipeline-yaml-generation | Item 11 (exit-point filename override, simkit grammar) | |
| 24-dual-resolution-architecture | Items 7, 10 — **thin prose, rewrite** | |
| 25-hierarchy-resolver | Items 4, 9, 10 | |
| 27-snapshot-generation | Item 2 (new) — verify against shipped code + script roles | |

### Changes Required
- [ ] For each row: read the doc, verify each claim against the fact sheet / code,
      rewrite thin prose to match the REQ rows (matrix + modeling-assumptions carry the
      authoritative text — prose must agree, not diverge)
- [ ] Convert `file:line` anchors to symbol anchors in every doc touched
- [ ] Release-note behavioral changes (Items 7/10/11) each traceable to a doc statement

### Validation
- [ ] Every row has a non-empty Status
- [ ] `grep -rn "ConsumerScopedKey" docs/` → nothing
- [ ] Spot-check: each release-note behavioral change has a home in some doc

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
| overview.md | No snapshot/ package, no `--from-snapshot`? | |
| 00-pipeline-overview | Capture workflow roles (Discovery 7) | |
| 03-resolution-overview | Predates `reference_chain`/tentative-confirm terms | |
| 04-input-resolver | Terminology drift | |
| 05-module-factory | Terminology drift | |
| 06-entry-point-classifier | Item-7 adjacency (entry-point semantics) | |
| 08-generation | Dead-template reference? (Discovery 5) | |
| 13-aggregation-scoping | Terminology drift | |
| 14-expression-compiler | Terminology drift | |
| 18-literal-value-propagation | (not in handoff's touched list — verify) | |
| 22-output-schema-rules | Liveness verdict required | |
| 23-smart-regen-preservation | Liveness verdict required | |
| 26-pipeline-module-migration | Liveness verdict required | |

### Changes Required
- [ ] For each row: read against HEAD; fix contradictions; don't polish prose that's
      merely old but true
- [ ] 22/23/26: check the subsystem exists and behaves as described; mark
      verified-live, corrected, or add an explicit status header (archived/superseded)
- [ ] Any doc referencing `pydantic_schema.py.jinja2`: fix the doc, file the template
      deletion as a follow-up (no code change)

### Validation
- [ ] Every row has a non-empty Status; 22/23/26 rows say what the verdict was
- [ ] `grep -rn "pydantic_schema.py.jinja2" docs/` → nothing (or only as documented-dead)

**What We Know Works After This Phase:** no silent contradictions left in the tree.

---

## Phase 5: Cross-Cutting Sweeps + Gate

### Goal
Mechanical checks that don't belong to any one doc, plus the unchanged-gate proof.

### Changes Required
- [ ] Repo-root `CLAUDE.md`: architecture section mentions `snapshot/` package and
      `--from-snapshot`
- [ ] Terminology sweep over all of docs/: old names gone, new terms used consistently
      (`reference_chain`, `EXPOSE_CHAIN_TENTATIVE`/Phase 3b, `ScopedAliasKey`,
      `fallback_entry_points` vs `output_aliases` contrast)
- [ ] `file:line` anchor sweep: `grep -rEn '\.py:[0-9]+' docs/` → fix or remove stragglers
- [ ] "Doc 27" ambiguity check: links distinguish `reference/27-snapshot-generation.md`
      from the TRR design doc
- [ ] Capture-workflow docs (27, 00, 02) state snapshot-driven vs live-license split
- [ ] File follow-ups discovered en route (template deletion, any code bugs found) in
      the backlog — not fixed here

### Validation
- [ ] All greps above clean
- [ ] Gate: `uv run pytest tests/` → 1989 passed / 4 skipped / 5 xfailed;
      `ruff check src/` → 21; `mypy src/` → 109 (byte-identical baselines)
- [ ] `git diff --stat upstream-findings-epic...docs-scrub -- . ':!docs' ':!.project' ':!CLAUDE.md'`
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
**Completed:**
**Actual Changes:**
**Issues:**
**Deviations:**

### Phase 3 Completion
**Completed:**
**Actual Changes:**
**Issues:**
**Deviations:**

### Phase 4 Completion
**Completed:**
**Actual Changes:**
**Issues:**
**Deviations:**

### Phase 5 Completion
**Completed:**
**Actual Changes:**
**Issues:**
**Deviations:**

---

**Status**: Draft → In Progress → Complete
