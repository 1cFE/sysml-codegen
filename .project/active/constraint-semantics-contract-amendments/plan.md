# Implementation Plan: Constraint Contract and Authoring Policy (CONSTRAINT-SEMANTICS Item 1)

**Status:** Draft
**Created:** 2026-08-12
**Last Updated:** 2026-08-12
**Branch:** `item7-rebuild`, in both worktrees
**Base commit (codegen):** `882161e` or later on the same branch

## Source Documents

- **Spec:** `spec.md`
- **Design:** `design.md` ← **all target text lives in its Appendices A–D**. This plan carries no
  amendment text; it carries order, gates, and bookkeeping.
- **Design review:** `design-review.md` §Resolutions (binding; already incorporated into the design)

Naming, used consistently below because "companion" is overloaded in the source documents:

- **contract** = codegen `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md`
- **requirements companion** = codegen `.project/concepts/constraint-execution-lifecycle-requirements.md`
- **companion repo** = `/home/reid/1cfe/agentic-mbse-item7-rebuild` (agentic-mbse, branch `item7-rebuild`)

---

## The Point

Constraint handling exists so a design study can trust a feasibility verdict. The umbrella contract
settled how that works: only the assert family enforces, the catalog accounts for every authored
usage, and the headline never claims full satisfaction while an applicable gate went unassessed.

Nothing a modeler or an implementing agent actually reads says any of that yet. The ratified
lifecycle contract, the frozen requirements companion, and seven documentation statements across two
repositories still teach the superseded rule — including the claim that a bare `constraint` is an
enforced gate, which is the exact form that silently does nothing.

The owner's sequence is binding: **[OWNER, 2026-08-12]** settle semantics → fix documentation and the
test model to match → then run tests to confirm. Item 1 is the documentation half. If it ships thin
text, Items 2–5 write code against a contract that still contradicts itself. Two owner-originated
payloads ride on it and must survive intact: **[OWNER-VERBATIM, 2026-08-12]** *"we know that narrow
bands of viability may make design exploration really difficult. So I want to call out in our concept
WHEN we really think equalities SHOULD be used (instructions) in addition to the sysml-codegen
support"*, and that tolerance values are modeled values the modeler chooses.

## Implementation Strategy

### This is a documentation item. There are no test suites to run.

Stated up front so the implementer does not burn time: **no `pytest` run is required by this plan, at
any phase.** No executable text changes (RI-6). The mechanical surface is exactly:

- codegen: `python scripts/check_doc_distinctness.py`, `git diff --check`
- companion repo: `git diff --check`, relative-link resolution on edited Markdown, and the
  docs-referencing-test grep whose *finding* is recorded either way (design Appendix D, last block)
- both: the S1–S5 sweep, re-run at the end as the proof of the "no remaining statement" criterion
- both: the pairwise precedence-agreement check (design Validation Approach step 2)

The one exception is conditional: if the companion-repo grep of `tests/` finds a test that references
an edited documentation path, run that test. If none does, record the absence as the finding.

**In place of test stencils, each phase below carries a check stencil** — the concrete grep or diff
command that proves the phase landed. Run the check stencil *before* the edits where it is a
pre-condition read (Phases 0 and 1), and after where it is a proof.

### Phasing Rationale

1. **Sweep and re-verify first, edit second.** S4 and S5 were added after design review and were
   never pre-run; S4 is expected to hit living prose around the report template and its tests, and
   that hit set is unsized work. The sweep must also run *before* the edits because the amendment
   notes quote the superseded precedence verbatim, so a post-edit S4 would collide with this item's
   own output. The same phase re-verifies all companion-repo quoted strings (design bet B4), which is
   the only failure mode that would force a second pass.
2. **Definitions before everything that cites them.** A0 is the single home; ADR-009 is written
   second because it must quote the *pre-amendment* invariant 33 and LC-E11 text while that text is
   still on disk.
3. **One repository at a time, contract before mirrors.** Contract → requirements companion →
   codegen docs → companion repo. Each mirror is written against text already on disk, not against
   the design alone, so a drift is caught at the point it is introduced.
4. **Verification last and whole.** `verification.md` is created in Phase 0 and completed in
   Phase 6; the discharge table is only checkable once every edit has landed.

### Critical Path

Phase 0 (sweep + companion re-verify) → Phase 1 (A0, then C1/ADR-009, then the product-lens cite-back)
→ Phase 2 (contract invariants + appendices + equality subsection) → Phase 3 (requirements companion)
→ Phase 4 (codegen docs, code comments, backlog) → Phase 5 (companion repo) → Phase 6 (re-sweep,
verification.md, all gates).

Phases 2–5 are strictly ordered by citation direction; none can safely be reordered, because each
later phase cites text the earlier one wrote.

### First Proof Point

End of Phase 0: the raw S1–S5 hit lists for both repositories exist in `verification.md`, and all
five companion-repo quoted strings are confirmed present at their stated locations. At that moment
the work is sized and the design's one unmitigated bet (B4) is resolved.

### Commit and Repository Discipline

- **One commit per phase, in the repository that phase touches.** Phase 5 is the only companion-repo
  commit; Phase 6 may produce one commit per repository if the re-sweep forces a correction there.
- Companion-repo git runs as `git -C /home/reid/1cfe/agentic-mbse-item7-rebuild …`. Never `cd`.
- **Stage untracked files before a pathspec commit** — `verification.md` is new and will be silently
  skipped otherwise.
- **Never touch `uv.lock`**, in either repository. If one appears in `git status`, it is a mistake to
  undo, not to commit.
- Commit subject carries the decision, not the file list. Example shapes:
  `docs(Item 1): contract publishes headline states, coverage truth, invariant 61`.
- The companion repo starts clean. Keep its commits scoped to this item's files; if anything
  unrelated is dirty there, stop and record it rather than committing around it.
- Neither repository opens a PR in this item.

### Boundaries — restated so they are not re-derived mid-edit

- **No TEAx repository changes.** Item 1 defines the canonical runtime vocabulary's *meaning*; Item 3
  lands the code.
- **No normative token spellings or report schema field names** (RI-3). Where a current spelling
  appears, it appears only inside a quotation of pre-amendment text.
- **The parked D-2 vs D-4/SRC-01 conflict is untouched, in either direction** (RI-5). Locate both
  bullets by their quoted text, not by line number — A11 inserts between D-3 and D-4.
- **Comment and docstring edits only in Python, with zero behavior change** (RI-6). Executable text —
  code, assertions, values — is out of scope. A correction that cannot avoid it is recorded in
  `verification.md` and handed to the item that owns that code.
- **No re-grade of REQ-EXT-09 or REQ-CL-04**, and no choice of replacement proof — Item 2's.
- **No new consistency tooling.** Declining to build a checker is a design decision, not an omission.

---

## Phase 0: Sweep, Size, and Re-Verify

### Goal

Produce the raw hit lists that size the editing work, and confirm every companion-repo target string
before a single edit is made anywhere.

### Assumption Under Test

Two. (a) Design bet **B4** — the companion-repo facts inherited from the orchestrator's 2026-08-12
read are still accurate. (b) Design bet **B1** — the defect class is small and concentrated. S4 and
S5 are unrun; this phase is where the work either stays the size the design assumed or grows.

### Check Stencil (Run This First)

```bash
# Codegen scope (DD5): docs/ src/ tests/ scripts/ README.md CLAUDE.md .project/concepts/ .project/backlog/
# Excluded and recorded: .project/research/ .project/completed/ .project/active/
SCOPE="docs src tests scripts README.md CLAUDE.md .project/concepts .project/backlog"
grep -rn --include=*.md --include=*.py --include=*.sysml "test_constraint_migration_mapping" $SCOPE   # S1
grep -rn --include=*.md --include=*.py --include=*.sysml "require constraint" $SCOPE                  # S2
# S3, S4, S5: exact patterns in design.md Appendix D, "Terms" table — copy them verbatim

# Companion repo: same five terms, same scope, via -C. Do not cd.
git -C /home/reid/1cfe/agentic-mbse-item7-rebuild status --short   # must be clean before starting
```

### Changes Required

**See `design.md#appendix-d--the-recorded-sweep`** for the exact term patterns, the scope decision
(DD5) and its recorded reason, the disposition table format, and the pre-run codegen result.

- [x] Create `verification.md` with the two table stubs from Appendix D (hit dispositions; discharge
      record) plus a header stating the scope, the exclusion, and its reason
- [x] Run S1–S5 over the codegen scope; paste the **raw** output into the hit table, one row per hit
      — 34 hits, all rowed
- [x] Run S1–S5 over the companion-repo scope with `grep -rn` under that path; same treatment.
      **Scope additions recorded:** `claude/` added (D5-a's target lives there, outside every DD5
      directory) and companion `BACKLOG.md` swept at the repository root
- [x] For S4 and S5 specifically: record the hit counts as a finding, since neither was pre-run.
      **S4 codegen: 12** (4 executable test assertions → Item 3; 2 amended here; 6 correct as
      written). **S4 companion: 0.** **S5 codegen: 2**, both correct as written. **S5 companion: 33**,
      of which 27+6 are vendored corpora. The design expected S4 to hit "the report template and its
      tests" — the tests, yes; no report-template prose restates the precedence
- [x] Pre-dispose every hit as `fix-here (C-ref)` / `correct-as-written (reason)` /
      `hand-to-Item-N (reason)`. A hit with no disposition blocks the phase gate
- [x] Explicitly disposition `BACKLOG.md:170-171` either way — dispositioned **correct as written**
      (Table 1 row 16), with the reason: dated historical finding naming retired modules
- [x] Re-verify all five companion-repo sites by reading them — **all five confirmed verbatim**;
      B4 is resolved
- [x] Any quoted string that does not match: none mismatched. **One characterization mismatch**
      recorded instead: D5-a's line is verbatim but sits inside a `requirement def`, so the design's
      "replace the form with `assert constraint`" would teach invalid SysML. Dispositioned against
      the design's stated intent — keep the form, add the settled-semantics sentence
- [x] Apply the DD8 test to `syntax-reference.md:185` and record which branch fires — **no-edit
      branch fired** (the default), framing sentence `**Constraint Prefixes:**` quoted in
      `verification.md`. `:186` ruled the same way

### Validation

- [x] Every raw hit has a row and a disposition — project-authored hits one row each; vendored
      `docs/sysmlv2/` and `docs/syside/` corpora aggregated by directory with counts and file lists,
      and the aggregation flagged with its reason
- [x] Five companion-repo sites confirmed present, or the mismatch recorded
- [x] S4/S5 hit counts recorded as findings, not as "none found" by implication
- [x] `git -C /home/reid/1cfe/agentic-mbse-item7-rebuild status --short` was clean at phase start

**Deviation — three design additions in the companion**, each recorded in `verification.md` with its
reason: D5-b′ (the "Wrong:" half of the pair D5-b corrects carries the identical false claim),
D5-f (`common-mistakes.md` Mistake 8, a third instance of the D4 defect, surfaced by S3), and
`constraints.md:43`'s "unassessed **today**", which reads the assert-only rule as temporary.

**Pre-existing dirt in codegen at phase start**, not this item's and not committed by it:
`.project/CURRENT_WORK.md` (modified), `.project/backlog/BACKLOG.md` (modified), and
`.project/backlog/epic_constraint_semantics_contract.md` (untracked) — all from the earlier
orchestration stages of this same epic. Every codegen commit below is a pathspec commit.

**What We Know After This Phase:** the true size of the correction set, including whatever S4 and S5
surfaced, and whether the companion-repo edits can proceed as designed.

**Commit (codegen):** `docs(Item 1): record pre-edit sweep S1–S5 over both repositories`

---

## Phase 1: Definitions Home and the Decision Record

### Goal

Write the single definitions home (A0) and ADR-009 (C1), in that order, and resolve the product-lens
spec-F1 disposition by citing the identifier back.

### Assumption Under Test

Design bet **B2** — meaning can be published without spellings. If the six states, their precedence,
and the coverage semantics cannot be written using state *names* alone, the Item 1 / Item 3 boundary
is wrong and the rest of the plan is built on it.

### Check Stencil

```bash
# Before editing: the pre-amendment text ADR-009 must quote is still on disk.
grep -n "Headline precedence is violation, then indeterminate, then all satisfied" \
  .project/concepts/constraint-execution-authoritative-lifecycle-contract.md
grep -n "else any assessed result" .project/concepts/constraint-execution-lifecycle-requirements.md
# After editing: the ADR identifier greps to exactly one anchor.
grep -rn "ADR-009" docs/ .project/active/constraint-semantics-contract/product-lens.md
```

### Changes Required

**See `design.md#a0-new-subsection-headline-states-and-coverage-truth`** (target text, placement) and
**`design.md#c1--adr-009-codegen-docsarchitecturemodeling-assumptionsmd-new-9`**.

- [x] Contract: add `### Headline states and coverage truth` immediately before
      `## Supported boundary and owner decisions`, with A0's text verbatim — including the
      form-level applicability test (a `BLOCK`ed or `NON_NUMERICAL` asserted usage stays applicable),
      the two totals, the six states, the precedence, the both-vocabularies paragraph, the
      minting note for invariant 61, and invariant 61 itself
- [x] `docs/architecture/modeling-assumptions.md`: add `## 9. Coverage Truth and Headline Semantics
      (ADR-009)` between §8's closing `---` and `## Validation Rules` (DD1) — landed at `:496`
- [x] Confirm the two superseded quotations inside ADR-009 are byte-accurate against the still-unedited
      contract and requirements companion — invariant 33 (`:232`) and LC-E11 (`:299-301`) were both
      still pre-amendment on disk when ADR-009 was written, and both quotes were taken from them
- [x] `.project/active/constraint-semantics-contract/product-lens.md` spec-F1: add
      `Filed: ADR-009 — …` — landed at `:35`. **No other product-lens text changed**

### Validation

- [x] A0 names no token spelling and no report field name (RI-3) — the six states are named in
      prose ("full satisfaction", "partial coverage"), never as tokens; the only backticked
      identifiers are `BLOCK` and `NON_NUMERICAL`, which are invariant 8's existing profile outcomes,
      not headline tokens
- [x] ADR-009's quoted "what the contract said" block matches the on-disk pre-amendment text exactly
- [x] `grep -rn "ADR-009" docs/` returns exactly one heading anchor (`modeling-assumptions.md:496`)
- [x] `python3 scripts/check_doc_distinctness.py` passes (31 documents, 0 identical groups);
      `git diff --check` clean. **Note:** the interpreter is `python3`; bare `python` is not on PATH
      in this environment

**What We Know After This Phase:** the definitions exist in one place, and every later amendment has
something to cite.

**Commit (codegen):** `docs(Item 1): publish headline-state definitions and file ADR-009`

---

## Phase 2: Contract Amendments

### Goal

Land every invariant, appendix, and boundary amendment in the lifecycle contract.

### Assumption Under Test

That the guardrails survive an edit pass that inserts two subsections above them. RI-4 and RI-5 are
anchored on quoted text precisely because A0 and A11 move every line number in the design's citations.

### Check Stencil

```bash
# Guardrails must be byte-identical after this phase (RI-4), located by text not line.
git diff -- .project/concepts/constraint-execution-authoritative-lifecycle-contract.md \
  | grep -nE "^-.*(Outcomes are exactly|Zero constraint usages|Catalog is absent when no assertion)"
# Expect: no output. Any hit is a guardrail violation.
git diff -- .project/concepts/... | grep -nE "^[-+].*D-2 \[OWNER-VERBATIM\]|D-4 \[OWNER-VERBATIM\]"
# Expect: no output (RI-5).
```

### Changes Required

**See `design.md` Appendix A, sections A1–A11** for every target text. Edit order within the file,
fixed here (design left this open):

- [x] A1 — invariant 1 (asserted-only halt scope)
- [x] A3 — invariant 9 (structurally-unattachable asserted usage halts)
- [x] A4 — invariant 28 (third disposition kind; remainder unchanged)
- [x] A5 — invariant 32 (applicable-asserted-gate trigger)
- [x] A6 — invariant 33 (five-state precedence, pointing at A0)
- [x] A7 — invariants 46 and 46a (compact coverage accounting; fail-closed extends to headlines)
- [x] A8 — invariant 48 (sole authority for coverage truth)
- [x] A9 — Appendix B, the one target row (`:737`). The neighbouring "Catalog is absent when no
      assertion is admitted" row (`:725`) is untouched — RI-4 diff check returns no output
- [x] A10 — Appendix C, two cells: mixed-population precedence (`:785`), and the excluded-only
      form-splitting clause (`:759`)
- [x] A10b — Appendix C, new "Asserted vacuous gate" row, immediately after excluded-only
- [x] A11 — new `### Equality intent and authoring policy` under `## Supported boundary and owner
      decisions`, after D-3 and before `### Source-identity dispositions (D-4 onward)`. No `D-n`
      number. Its pointer to invariant 11 is verified: invariant 11 (`:159`) does govern which
      equality forms execute
- [x] A2 — invariant 8 is a **guardrail**: no edit made. "Verified already-correct" recorded in the
      discharge table with the reason

Every amended statement carries `(amended 2026-08-12, CONSTRAINT-SEMANTICS Item 1)` at the head, per
the live convention of invariants 19/20/22/26 (DD4).

### Validation

- [x] Guardrail check stencil above returns no output — both the RI-4 grep and the RI-5 D-2/D-4 grep
      are empty
- [x] A11's two `[NEED]` markers and the `[AGENT] (ratified by owner, 2026-08-12)` grade on the
      four-class taxonomy are present and correctly attached — the taxonomy is agent-grade, the
      *need* is owner-grade (RI-2)
- [x] No amendment names a token spelling except inside a quotation (RI-3) — the states are named in
      prose throughout; `ADMIT`/`BLOCK`/`NON_NUMERICAL`/`UNASSESSED` are invariant 8's profile
      outcomes, which are not headline tokens and are unchanged
- [x] Each of A5, A6, A7 **points at** A0 rather than restating it (A5 and A6 name "Headline states
      and coverage truth"; A7 names invariant 48 and the fail-closed obligation); A10's
      mixed-population cell restates the precedence in full, per the design's Core Concept
- [x] `git diff --check` clean

**What We Know After This Phase:** the ratified contract teaches the settled semantics, and the
equality instruction has an authority copy.

**Commit (codegen):** `docs(Item 1): contract amendments — coverage truth, invariant 61, equality policy`

---

## Phase 3: Frozen Requirements Companion

### Goal

Mirror the contract into the frozen requirements companion, establishing the in-place-rewrite
convention its header licenses.

### Assumption Under Test

Design bet **B3** — the copy-and-freeze header's "forward requirement amendments happen here only"
licenses rewriting requirement text, not merely appending to it. **No precedent supports this**;
LC-E04B is a pure append. The mitigation is structural: every rewrite quotes the text it supersedes
inside its own amendment note, so an owner who later prefers append-only can recover mechanically.

### Check Stencil

```bash
# Every amendment note carries its own grade and quotes what it supersedes.
grep -n "Amended 2026-08-12 (CONSTRAINT-SEMANTICS Item 1)" \
  .project/concepts/constraint-execution-lifecycle-requirements.md
grep -c "Superseded:" .project/concepts/constraint-execution-lifecycle-requirements.md
# Existing grade markers must be untouched (RI-2).
git diff -- .project/concepts/constraint-execution-lifecycle-requirements.md | grep -E "^-.*\[INHERITED\]|^-.*\[NEED\]"
```

### Changes Required

**See `design.md` Appendix B, B1–B7**, including the four things every amendment note does and the
one-time convention statement B1 carries.

- [x] B1 — LC-E05, plus the one-time convention statement
- [x] B2 — LC-E06
- [x] B3 — LC-E10
- [x] B4 — LC-E11, the wholesale replacement. `[INHERITED]` marker and `Source:` line stay, with the
      clarifying clause; the replacement body is sourced to the umbrella spec and ADR-009 at
      agent-ratified grade
- [x] B5 — LC-E12 (cites invariants **32 and 33**)
- [x] B6 — LC-G07, append-only. The owner quote and existing text stay **byte-identical**
- [x] B7 — new LC-E13, the companion mirror of invariant 61, after LC-E12

### Validation

- [x] Every one of B1–B5 and B7 carries `[AGENT] (ratified by owner, 2026-08-12)` on its **new**
      content, and no requirement's own grade marker changed (RI-2). Six `Amended 2026-08-12
      (CONSTRAINT-SEMANTICS Item 1)` notes (B1–B6); B7 is an addition and carries `Added`
- [x] Every rewrite quotes its superseded text — five `Superseded:` clauses (B1–B5). B6 is
      append-only and B7 supersedes nothing
- [x] LC-G07's owner quote is unchanged in the diff — `git diff | grep "^-.*100% Option A"` is empty
- [x] `git diff --check` clean

**Note on the grade-marker check stencil.** `git diff | grep -E "^-.*\[INHERITED\]"` returns two
lines, for LC-E06 and LC-E11. Both are rewrites of the marker's own line, and both `+` sides carry
the identical `[INHERITED]` marker. RI-2 holds: the check's raw form cannot tell a rewritten line
from a removed grade, and the grades were read on both sides to confirm.

**What We Know After This Phase:** the side Items 2 and 3 read for requirements states the same rule
as the contract, including the warning tier.

**Commit (codegen):** `docs(Item 1): requirements companion amendments incl. LC-E13 vacuous-gate mirror`

---

## Phase 4: Codegen Documentation, Code Comments, and Backlog

### Goal

Correct D1, D2, D2b, D6, D7-docs and D7-code at their locations, add the matrix pointer, and file the
two future-capability lines.

### Assumption Under Test

That the code-text boundary holds: every dead-citation fix in Python is achievable in comment and
docstring lines alone, with zero behavior change (RI-6).

### Check Stencil

```bash
# The whole Python diff must be comment/docstring lines only.
git diff -- '*.py'
# Every remaining living-surface mention of the retired test is gone.
grep -rn "test_constraint_migration_mapping" docs src tests scripts README.md CLAUDE.md \
  .project/concepts .project/backlog
```

### Changes Required

**See `design.md` Appendix C, C2–C8 and C10.**

- [ ] C2 — D1, `modeling-assumptions.md` §8: the replacement paragraph, carrying the blessed gate
      shape, the three scope carve-outs, the modeler-owned-tolerance `[NEED]`, and the four equality
      moves stated inline with the contract cited for the reasoning
- [ ] C3 — D2, unassessed enumeration, with the Item 2 target marker in the parenthetical
- [ ] C4 — D2b, "three outcomes" → four, plus the `NON_NUMERICAL` bullet. **Design addition** —
      record it in the discharge table with its reason
- [ ] C5 — D6, `reference/28-…md`: the two axes separated per invariant 16, with the Item 2 target
      marker
- [ ] C6a/b/c — D7-docs at three sites. C6c removes **only** the first clause of `01-extraction.md:20`;
      the other three clauses stay verbatim (DD7)
- [ ] C7a — `constraint_report.py`: the filename site **plus** the three by-description references at
      `:9`, `:10-11`, `:15-16`. The S1 grep does not find these
- [ ] C7b — `test_extractor.py` class docstring, including the `:881-882` by-description reference
- [ ] C7c — `test_extractor.py:902` inline comment
- [ ] C8 — matrix pointer appended to REQ-EXT-09's **Test File** cell, never the Status cell (DD6)
- [ ] C10 — two bullets under `## Ideas / Future Considerations` in `.project/backlog/BACKLOG.md`,
      phrased as decision records
- [ ] Make the four `modeling-assumptions.md` §8 edits as **separate edits against separate quoted
      strings**, so an auditor can check each independently

### Validation

- [ ] `git diff -- '*.py'` shows only comment and docstring lines — no assertion, name, or value
      changed at any of the three sites (RI-6)
- [ ] The S1 grep over the codegen living scope returns zero hits
- [ ] Both C10 bullets exist — without them, the word "filed" in the published contract is false
- [ ] Every RI-1 target statement (C3, C5) names CONSTRAINT-SEMANTICS Item 2 in the published text
- [ ] `python scripts/check_doc_distinctness.py` passes; `git diff --check` clean

**What We Know After This Phase:** the codegen repository contains no statement that a plain or
requirement-side constraint enforces, and no citation of the retired test.

**Commit (codegen):** `docs(Item 1): correct D1/D2/D2b/D6/D7, add matrix pointer and backlog filings`

---

## Phase 5: Companion Repository (agentic-mbse)

### Goal

Land D3, D4, D5, the full equality instruction, and the ADR-009 cite in
`/home/reid/1cfe/agentic-mbse-item7-rebuild`.

### Assumption Under Test

Already collapsed in Phase 0 — the quoted strings were confirmed there. This phase tests only that
D3's substitution preserves the enumeration decision that Item 2's totality gate rests on.

### Check Stencil

```bash
CO=/home/reid/1cfe/agentic-mbse-item7-rebuild
# D3's enumeration decision must survive the substitution verbatim.
grep -n "include_subtypes=True" $CO/docs/subtype-enumeration-decision-table.md
grep -n "RequirementUsage" $CO/docs/subtype-enumeration-decision-table.md
git -C $CO diff --check
git -C $CO status --short   # nothing outside this item's files; no uv.lock
```

### Changes Required

**See `design.md#c9--companion-repository-corrections-agentic-mbse`** for every target text, and the
equality-instruction block rendered in full (M6).

- [ ] D3 — `docs/subtype-enumeration-decision-table.md` row 1 Rationale. **Substitution of reason
      only.** `include_subtypes=True`, the `RequirementUsage` EXCLUDE decision, and every other column
      are unchanged
- [ ] D4 — `docs/patterns/constraints.md`: heading, inline comment, and error line. Match the
      vocabulary of the correct four-outcome block already at `:25-41`
- [ ] D5-a — `claude/agents/sysml-expert.md:124`
- [ ] D5-b/c/d — `docs/patterns/semantic-operators.md`, three sites
- [ ] D5-e — `docs/patterns/syntax-reference.md:185`: apply the Phase 0 branch ruling. If the no-edit
      branch fired, make no edit and confirm the disposition is already in `verification.md`
- [ ] Equality instruction — the full block (intent → move table, the owner's reason, the
      modeler-owned-tolerance statement, the `[AGENT] (ratified by owner, 2026-08-12)` grade, and the
      "if the two disagree, the contract governs" line) into `docs/patterns/constraints.md`, adjacent
      to the four-outcome block. **Rendered in full, not as a pointer** — a companion reader may not
      have the codegen tree
- [ ] ADR-009 cite — one line in `docs/patterns/constraints.md`. No stub file (DD2)

### Validation

- [ ] D3's enumeration decision greps intact
- [ ] Relative links in every edited Markdown file resolve
- [ ] `git -C $CO diff --check` clean
- [ ] `git -C $CO status --short` shows only this item's files, and no `uv.lock`
- [ ] Grep the companion's `tests/` for the edited documentation paths. If a test references one, run
      it. If none does, record the absence in `verification.md` as the finding it is

**What We Know After This Phase:** a modeler reading agentic-mbse authoring guidance is taught the
assert family as the sole enforcement opt-in, and can act on the equality instruction without a
second checkout.

**Commit (companion repo):**
`git -C /home/reid/1cfe/agentic-mbse-item7-rebuild commit` —
`docs(Item 1): assert-only enforcement in authoring guidance, equality intent policy, ADR-009 cite`

---

## Phase 6: Re-Sweep, Discharge, and Gates

### Goal

Prove the universal claim rather than assert it, and close every RI-7 discharge.

### Assumption Under Test

Design bet **B1** — that the seven-defect register plus a five-term sweep really closes the class.
The re-run is the evidence.

### Check Stencil

```bash
# Re-run S1–S5 over both repositories, same scope as Phase 0.
# Expected residue and how to read it:
#   S1 → zero hits on living surfaces.
#   S4 → hits inside this item's own amendment notes are "quoted supersession, correct as written".
#   S2/S3/S5 → only classification statements, each already dispositioned.
python scripts/check_doc_distinctness.py
git diff --check
git -C /home/reid/1cfe/agentic-mbse-item7-rebuild diff --check
```

### Changes Required

- [ ] Re-run S1–S5 in both repositories; append the post-edit raw output to `verification.md`
- [ ] Disposition every post-edit hit. Any S4 hit inside an amendment note is "quoted supersession,
      correct as written" — pre-resolved, but it must still appear as a row
- [ ] **Pairwise precedence-agreement check** (design Validation Approach step 2): compare the five
      statements of the headline precedence — A0, A6, A10's mixed-population cell, B4, C1 — against
      A0. They must agree in meaning and order. Compare the three disposition-kind statements —
      A0/A4, B1, and the catalog text in C5 — the same way. A disagreement is a defect, not a
      stylistic variation. Record the comparison, not just its verdict
- [ ] Complete the discharge table: invariant 8, Appendix C "Zero constraint usages", Appendix B
      "Catalog is absent…", the three design additions (C4/D2b, A10b, B7), the C2/C3/C5 RI-1
      dispositions, the D5-e branch, and anything handed on for touching executable text
- [ ] Record the DD5 scope exclusion and its reason, the companion doc-check finding, and the B1
      convention statement
- [ ] Run the RI-4/RI-5 guardrail diff checks and the RI-3/RI-6 boundary checks; record the results
- [ ] Update `.project/CURRENT_WORK.md` with Item 1 status and what Items 2–5 may now build against

### Validation

- [ ] Every listed spec and design entry appears in `verification.md` as amended or as
      verified-already-correct. **Silence discharges nothing** (RI-7)
- [ ] Every post-edit sweep hit has a disposition
- [ ] The pairwise check is recorded with its comparisons
- [ ] `check_doc_distinctness.py` passes; `git diff --check` clean in both repositories
- [ ] No `pytest` run was needed, and the plan says so — do not add one to feel complete

**What We Know After This Phase:** the "no remaining statement" criterion is checked, not asserted,
and Items 2–5 have a published contract to build against.

**Commit (codegen):** `docs(Item 1): complete verification record — post-edit sweep and discharges`

---

## Environment Setup

**See CLAUDE.md for full environment rules.** Item-specific notes:

- No `SYSIDE_LICENSE_KEY` is needed. Nothing in this item extracts, elaborates, or generates.
- No `uv` invocation is needed except `python scripts/check_doc_distinctness.py`, which is
  dependency-free.
- `captured_at` churn does not apply — no fixture regeneration happens here.

## Risk Management

**See `design.md#potential-risks`.** Phase-specific mitigations:

- **Phase 0** — the companion tree moved since 2026-08-12: re-verify-then-edit, and a mismatch is a
  recorded stop, not an improvised edit.
- **Phase 0** — S4/S5 are unsized: they are dispositioned before any editing begins, so a large hit
  set changes the plan rather than being discovered mid-Phase-4.
- **Phase 2** — guardrail collateral damage from two inserted subsections: RI-4/RI-5 are anchored on
  quoted text, never line numbers.
- **Phase 3** — no rewrite precedent exists in the frozen companion: every rewrite quotes what it
  supersedes, so an owner reversal is mechanical.
- **Phase 4** — amendment text drifting into Item 3's territory: grep the diff for token spellings
  and report field names and confirm each appearance sits inside a quotation.
- **Phase 6** — five copies of the precedence and no checker: the pairwise agreement check is the
  price, and it is a required gate, not an optional read-through.

## Implementation Notes

[TO BE FILLED DURING IMPLEMENTATION — record deviations in the phase checkboxes as they happen]

### Phase 0 Completion
**Completed:**
**Actual Changes:**
**Issues:**
**Deviations:**

### Phase 1 Completion

### Phase 2 Completion

### Phase 3 Completion

### Phase 4 Completion

### Phase 5 Completion

### Phase 6 Completion

---

**Status**: Draft → In Progress → Complete
