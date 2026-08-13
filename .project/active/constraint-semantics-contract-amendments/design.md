# Design: Constraint Contract and Authoring Policy (CONSTRAINT-SEMANTICS Item 1)

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-08-12
**Branch:** `item7-rebuild` (worktrees `/home/reid/1cfe/sysml-codegen-item7-rebuild`,
`/home/reid/1cfe/agentic-mbse-item7-rebuild`)
**Base commit:** `882161e`
**Spec:** `.project/active/constraint-semantics-contract-amendments/spec.md` (revised, with
`spec-review.md` §Resolutions binding)

---

## Overview

The complete amendment plan for Item 1: exact target text for every contract, companion, and
documentation change, the placement decisions the spec deferred, the recorded sweep, and how each
edit is verified. No executable text changes.

## Related Artifacts

- **Spec:** `spec.md` · **Spec review:** `spec-review.md` (verdict Revise, resolutions binding)
- **Epic:** `.project/backlog/epic_constraint_semantics_contract.md`
- **Required reading:** `.project/active/constraint-semantics-contract/spec.md`,
  `…/rulings-20260812.md`, `…/product-lens.md`,
  `.project/research/20260812-101200_constraint-semantics-end-to-end.md` §7
- **Amended authorities:** `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md`,
  `.project/concepts/constraint-execution-lifecycle-requirements.md`
- **Decision records:** no `.project/adr/` exists in this repository and `.project/scripts/` holds
  only `get-metadata.sh`. Codegen decision records are citation identifiers over consolidated prose
  in `docs/architecture/modeling-assumptions.md` (commit `eda48f9`, verified). ADR-009 is
  hand-authored there; no `adr.sh` is invoked because none exists.

## The Point

Constraint handling has to enforce modeled physics so a design study can trust a feasibility
verdict. The umbrella contract settled how that works — assert-only enforcement, a catalog that
accounts for every authored usage, and a headline that never claims full satisfaction while
applicable gates went unassessed. **[INHERITED: constraint-semantics-contract/spec.md]**

Nothing a modeler or an implementing agent reads says any of that yet. Today's durable authorities
teach the superseded rule, and seven documentation statements actively steer a modeler into the
one form that silently does nothing. The owner's sequence is binding and unambiguous:
**[OWNER, 2026-08-12]** settle semantics → fix documentation and the test model to match → then
run tests to confirm. Item 1 is the documentation half. If it ships thin text, Items 2–5 write
code against a contract that still contradicts itself.

Two owner-originated payloads ride on this item and must survive intact:
**[OWNER-VERBATIM, 2026-08-12]** *"we know that narrow bands of viability may make design
exploration really difficult. So I want to call out in our concept WHEN we really think equalities
SHOULD be used (instructions) in addition to the sysml-codegen support"*, and the modeler-owned
tolerance need.

## Research Findings

Everything below was read in this session unless marked otherwise.

**Contract structure** (`constraint-execution-authoritative-lifecycle-contract.md`, 1477 lines).
Invariants are a flat numbered list grouped under topical `###` subsections; the highest live
number is 60 (`:376`), so 61 is free. The `(amended YYYY-MM-DD, EPIC Item N)` convention sits at
the head of the restated statement — invariants 19 (`:172`), 20 (`:179`), 22 (`:186`), 26 (`:198`).
Owner decisions live under `## Supported boundary and owner decisions` (`:406`), which opens with
D-1..D-3 and then hands off to a `### Source-identity dispositions (D-4 onward)` subsection
(`:435`). Appendix B is a three-column correction register (`:639`); Appendix C is a two-column
acceptance matrix (`:669`). The contract's own reading rule (`:19-21`) says earlier concepts,
specs, and designs "remain provenance" and do not override an explicit correction here.

**Companion structure** (`constraint-execution-lifecycle-requirements.md`, 687 lines). The
copy-and-freeze header (`:3-7`) is the licensing text: "forward requirement amendments happen here
only." That is what authorizes this item to change requirement text at all, and it is not limited
to appending.

The file's one prior amendment is **LC-E04B** (`:269-274`; LC-E04 is a different, owner-adjacent
requirement at `:263`). It is a **pure append**: comparing the live body (`:269-271`) against the
archived close-state copy
(`.project/completed/20260720_constraint-execution-lifecycle-contract/spec.md:253-255`), the
requirement text is byte-identical and the 2026-08-05 amendment added only the trailing "Amended
2026-08-05 (SOURCE-IDENTITY Item 3): …" sentence. **So there is no in-place-rewrite precedent in
this file, and this design does not claim one** — see DD4 and B3, which ground the rewrite on the
header rule instead. What LC-E04B *does* establish is the trailing-sentence form of the amendment
note, which this item reuses.

LC-E11 (`:299-301`) carries the direct contradiction verbatim; LC-G07 (`:362-366`) is `[NEED]`
with an owner quote.

**ADR precedent.** `git show --stat eda48f9` confirms the review's account: eight ADR files
deleted, content synthesized into `docs/architecture/modeling-assumptions.md`. ADR identifiers
survive only as citations — 40-plus live ones across `src/`, `tests/`, `docs/`, `CLAUDE.md` — and
`modeling-assumptions.md` contains **no** `ADR-00n` string at all. The mapping from identifier to
section lives in `CLAUDE.md:107,114`. So today an ADR identifier is a bare citation with no
anchor; ADR-009 must not repeat that.

**Correction sites, verified.** D1 = `modeling-assumptions.md:489-492`; D2 = `:468-470`;
D7-docs = `:482-487`, `reference/01-extraction.md:20`, `reference/28-…:100-101`; D6 =
`reference/28-…:44-49`; D7-code = `src/sysml_codegen/extraction/constraint_report.py:6` and
**two** sites in `tests/conformance/test_extractor.py` (`:880` docstring, `:902` comment — the
spec named one). `verification-matrix.md:336` cites two live tests and grades PASS.

**Live evidence that survives.** `01-extraction.md:20`'s evidence cell has **four** clauses: the
retired-test claim, the `wi014_toy` assert landing, the `include_subtypes=False` mutation check,
and a pointer to the companion's subtype-enumeration decision table. Only the first cites the
retired test; the other three stay (`tests/conformance/test_extractor.py:975`, `:1020-1032` are
live). The cell therefore does not become evidence-free — a materially cheaper outcome than the
spec's open question assumed.

**Sweep pre-run (codegen only).** `test_constraint_migration_mapping` → 6 living-surface hits (the
5 above plus `modeling-assumptions.md:484`), the rest in dated records. `require constraint` → 9
living-surface hits, of which 8 are correct-as-written classification statements (fixture and test
text calling it a plain `ConstraintUsage`) and 1 is D1. Plain-constraint-enforces regex → 1
living-surface hit, D1's own heading. The class is small; the value of the sweep is the record.

**Companion repository.** This session is sandboxed from
`/home/reid/1cfe/agentic-mbse-item7-rebuild`. All companion facts below come from the
orchestrator's 2026-08-12 read (stage brief) and are labelled `[INHERITED: orchestrator read]`.
Every companion edit carries a re-verify-before-editing step in the plan.

## Core Concept

**One decision, one authority, cited from everywhere it binds.**

The contract change is a single semantic move: *coverage truth*. A headline may only claim full
satisfaction when every applicable asserted gate was assessed and passed, which forces a new
partial-coverage state, a third disposition kind for usages that reach no instance, and a warning
tier for asserted gates that attach to nothing. Every amendment in this item is that one move
projected onto a different surface — an invariant, a frozen requirement, an acceptance cell, a
modeler-facing paragraph.

So the design does not scatter the semantics. It puts the definitions in exactly one place — a new
**"Headline states and coverage truth"** subsection in the lifecycle contract, carrying the
definition of *applicable asserted gate*, the six state meanings, the precedence order, the
inventory-versus-feasibility split, and new invariant 61 (the vacuous-gate warning tier).

**Stated accurately, because it changes what the audit must do:** the definitions have one *home*,
not one *copy*. Some amendments point at the home and some must restate it, and which is which is
fixed by each document's structure, not by preference. Pointing: invariant 33 (A6), invariant 32
(A5), invariant 46a (A7). Restating in full, because an acceptance cell must state its own
observation, a frozen requirement must carry its own text, and a decision record must record what
changed: Appendix C's mixed-population cell (A10), LC-E11 (B4), and ADR-009 (C1). The five-state
precedence therefore ends up written out in five places and the three disposition kinds in three.
Where an amendment restates, it restates **verbatim in meaning and order** and cites the home. No
checker enforces that — see Non-Goals — so the audit compares the copies pairwise against A0
(Validation Approach step 2).

ADR-009 records *why the change was made*
and what the superseded statements said; the contract records *what is true now*. Those are
different jobs and they get different homes, which is also what keeps capture-fidelity law 3
satisfiable: a corrected statement is rewritten in place with nothing left behind, because the
superseded claim's designated home is the decision record and Appendix B, not a warning label
stapled to the corrected text.

The authoring-facing half follows the same shape. One rewritten paragraph in
`modeling-assumptions.md` §8 discharges D1, publishes the blessed assert-with-bindings gate shape
with its three scope carve-outs, states that tolerances are the modeler's, and cites the equality
instruction. The equality instruction itself is written once in the lifecycle contract's supported
boundary and cited from the companion's authoring guidance.

## Key Bets

- **B1.** The seven-defect register plus a three-term sweep over *living* surfaces really does
  close the class — the defect family is "text written before the semantics were settled," and it
  concentrates in constraint-facing docs. *If false → the "no statement remains" criterion is
  false at close, and a modeler still finds wrong guidance somewhere the sweep did not look. The
  mitigation is that the sweep's raw hit list and its directory scope are recorded, so a later
  reader can see exactly what was and was not searched rather than trusting a summary.*
- **B2.** Meaning can be published without spellings. Item 1 can define six states, their
  precedence, and their coverage semantics using state *names* while Item 3 chooses the report and
  runtime tokens. *If false → Item 3 finds the definitions unimplementable without re-deriving
  semantics, and the Item 1/Item 3 boundary collapses into a round-trip.*
- **B3.** The companion's copy-and-freeze header — "forward requirement amendments happen here
  only" (`:3-7`) — licenses rewriting a requirement's text, not merely appending to it. The bet is
  on the header's plain meaning: a document designated as the only place a forward amendment may
  land must be able to carry an amendment that *contradicts* the frozen text, or LC-E11 has no
  home at all. **No precedent supports this**; the file's one prior amendment (LC-E04B) is a pure
  append, verified against the archived close-state copy, and this item is what establishes the
  rewrite convention the header licenses. *If false → LC-E11's superseded precedence has to stay
  on the page under an amendment note, which capture-fidelity law 3 forbids, and the item needs an
  owner ruling before it can proceed.* Mitigation, and why this does not need to block: every
  rewrite quotes the text it supersedes inside its own amendment note, so nothing is lost from the
  record even if the owner later prefers append-only — the recovery is mechanical.
- **B4.** The companion-repo facts in the stage brief are accurate as of 2026-08-12 and the tree
  is unchanged when the plan executes. *If false → the D3/D4/D5 edits miss or damage their
  targets. Mitigated by a mandatory re-read-then-edit step per site.*

## Key Decisions

- **DD1. ADR-009 lands as a new numbered section `## 9. Coverage Truth and Headline Semantics
  (ADR-009)` in `docs/architecture/modeling-assumptions.md`, between §8 and `## Validation
  Rules`.** *Rejected: an entry inside §8 — §8 is a modeler-prerequisites section that already
  absorbs three corrections in this item, and folding a decision record into it makes ADR-009
  uncitable as a unit and mixes "what you must model" with "why the contract changed". Rejected:
  a revived standalone file — reverses `eda48f9`. Rejected: the companion — the decision governs
  a codegen-owned report contract.* The heading carries the literal string `ADR-009` so the
  identifier greps to exactly one anchor, unlike ADR-001..008 today.
- **DD2. The companion cites ADR-009 in place; no stub file next to
  `docs/patterns/adr002-calculations.md`.** *Rejected: a stub — a second ADR-shaped file in the
  companion would imply a second home for one decision, which is what the "one authority for one
  decision" rule in the spec forbids.* The cite rides the D4/D5 corrections that already touch
  those files.
- **DD3. The equality instruction's authority is the lifecycle contract, in a new
  `### Equality intent and authoring policy` subsection under `## Supported boundary and owner
  decisions`, placed after D-3 and before `### Source-identity dispositions (D-4 onward)`.**
  *Rejected: `.project/concepts/constraint-execution-and-design-space-studies.md` — it is
  `Status: Proposed`, and its own banner (`:9`) says the `-claude.md` design governs where they
  differ; the ratified contract's reading rule demotes both to provenance. Writing a new normative
  instruction into a provenance document would contradict the authority rule this item is
  enforcing.* The lifecycle contract is in `.project/concepts/`, so the owner's "call out in our
  concept" is satisfied. It gets no `D-n` number: the D-register from D-4 onward is
  source-identity scoped, and borrowing a number there would misfile it.
- **DD4. Each file's amendments follow that file's own convention, and the companion's rewrites are
  grounded on its header rule rather than on a precedent.** Contract: `(amended 2026-08-12,
  CONSTRAINT-SEMANTICS Item 1)` at the head of the restated statement — the live convention of
  invariants 19/20/22/26. Companion: the statement is rewritten in place and a trailing
  `Amended 2026-08-12 (CONSTRAINT-SEMANTICS Item 1), [AGENT] (ratified by owner, 2026-08-12): …`
  sentence records what changed, **quotes the text it supersedes**, and cites the governing
  invariant. The license for rewriting is the copy-and-freeze header's "forward requirement
  amendments happen here only" (`:3-7`), not LC-E04B — LC-E04B is a pure append and carries no
  rewrite precedent. This item establishes the rewrite convention the header licenses, and says so
  in its first amendment note. *Rejected: append-only, leaving LC-E11's superseded precedence on
  the page under a note — capture-fidelity law 3 requires the corrected content to be deleted or
  rewritten, and a frozen requirement that still reads "else any assessed result → all_satisfied"
  is exactly the statement Items 2–3 would build against. Rejected: forcing the contract's
  parenthetical convention onto the companion — a foreign convention reads as a foreign edit in a
  frozen document, and LC-E04B's trailing-sentence form is native there.*
- **DD5. The sweep covers living-guidance surfaces only, and records the exclusion.** In scope:
  `docs/`, `src/`, `tests/`, `scripts/`, `README.md`, `CLAUDE.md`, `.project/concepts/`,
  `.project/backlog/` in both repositories. Out of scope: `.project/research/`,
  `.project/completed/`, `.project/active/`. *Rejected: sweeping everything — those are dated
  records of what was believed when, and the contract's reading rule (`:19-21`) already makes them
  provenance; rewriting them would falsify the audit trail. The exclusion and this reason are
  written into `verification.md` so the boundary is auditable rather than silent.*
- **DD6. The matrix pointer lands in REQ-EXT-09's evidence cell, not its Status cell.**
  *Rejected: the Status cell — an annotation there reads as a re-grade, which is Item 2's and is a
  stated non-goal.* Exact line in Appendix D.
- **DD7. `01-extraction.md`'s REQ-EXT-09 evidence cell keeps its other three clauses** (the
  `wi014_toy` landing, the `include_subtypes=False` mutation check, and the decision-table
  pointer — four clauses in total). Only the
  retired-test clause is removed and replaced with a dated pending note. *Rejected: emptying the
  cell — the `wi014_toy` landing and the `include_subtypes=False` mutation check are live and
  unrelated to the retired test; deleting live evidence to signal a gap would be a worse
  distortion than the gap.*
- **DD8. `docs/patterns/syntax-reference.md:185` is ruled by a stated test the implementer
  applies, not by a guess from here.** See Appendix C, D5-e.

## Architecture

Four surfaces, one dependency order.

```text
ADR-009 (modeling-assumptions.md §9)  ── records why + what the old text said
   │ cited by
   ├─> lifecycle contract          ── invariants 1, 9, 28, 32, 33, 46/46a, 48, new 61
   │      │                            + "Headline states and coverage truth" (definitions)
   │      │                            + "Equality intent and authoring policy"
   │      │                            + Appendix B row, Appendix C two cells
   │      │ cited by
   │      ├─> companion requirements  ── LC-E05/E06/E10/E11/E12, LC-G07
   │      └─> agentic-mbse authoring guidance ── D3, D4, D5 + equality-instruction cite
   └─> codegen reference docs       ── D1, D2, D6, D7 + matrix pointer
```

**Write order matters.** The definitions subsection is written first: every other amendment cites
it. ADR-009 is written second, because it must quote the pre-amendment invariant 33 and LC-E11
text, and that text must still be on disk when it is quoted. Then the invariants, then the
appendix cells, then the companion, then documentation, then the sweep, then `verification.md`.

**What is not a data flow here.** There is no tooling seam. No script generates any of this text,
no check validates cross-document consistency, and none is built — `check_doc_distinctness.py`
compares byte-identity between numbered reference documents (`scripts/check_doc_distinctness.py:9-13`)
and would never see a wrong sentence. Consistency is held by the single-definitions-home decision
and checked by the audit against this design.

## Required Invariants

- **RI-1.** Every statement this item writes states the settled semantics. Where current code
  differs, the text says what must be true and names the item that makes it true. No amendment is
  softened to match today's behavior. **[NEED, owner-directed sequence]**
- **RI-2.** No amendment re-grades the statement it amends. `[INHERITED]` companion requirements
  stay `[INHERITED]` with their cited source; LC-G07 stays `[NEED]`; the amendment's own new
  content carries `[AGENT] (ratified by owner, 2026-08-12)` and says so where a grade is visible.
- **RI-3.** No amendment names a headline token spelling or a report schema field name as
  normative. Where a current spelling appears it appears as today's text being amended.
- **RI-4.** Three guardrail statements are byte-identical after this item, **anchored by quoted
  text, not line number** — A0 and A11 insert above all three, so the line numbers move:
  invariant 8 ("Outcomes are exactly `ADMIT`, `BLOCK`, `NON_NUMERICAL`, and `UNASSESSED`.");
  Appendix C's "Zero constraint usages" row; Appendix B's row whose superseded claim reads
  "Catalog is absent when no assertion is admitted".
- **RI-5.** No edit touches contract **D-2** (the bullet opening "**D-2 [OWNER-VERBATIM], decided
  2026-07-19:**") or **D-4/SRC-01** (the bullet opening "**D-4 [OWNER-VERBATIM], decided
  2026-08-05:**"), in either direction. Anchored by that quoted text, not by line number — A11
  inserts between D-3 and D-4 and shifts D-4 down. The parked conflict stays parked.
- **RI-6.** No executable text changes. `git diff` over both repositories shows changes only in
  Markdown files and in comment/docstring lines of Python files. A correction that cannot avoid
  executable text is recorded in `verification.md` and handed on, not made.
- **RI-7.** Every entry in the spec's amendment lists is discharged visibly — amended, or recorded
  in `verification.md` as "verified already-correct, no amendment needed" with the verification
  note. Silence discharges nothing.

## Component Overview

| # | Component | Location | Responsibility |
|---|---|---|---|
| C1 | ADR-009 | codegen `docs/architecture/modeling-assumptions.md` §9 (new) | Records the intended change, the superseded text, the reasoning, the grade |
| C2 | Definitions subsection | contract, new `### Headline states and coverage truth` before `## Supported boundary` | Applicable asserted gate; six states; precedence; two totals; invariant 61 |
| C3 | Invariant amendments | contract invariants 1, 9, 28, 32, 33, 46, 46a, 48 | The one move, projected per invariant |
| C4 | Appendix amendments | contract Appendix B (the "Aggregator always exists even with no usage" row), Appendix C (two cells amended, one added for invariant 61) | Register and acceptance consistency |
| C5 | Equality instruction | contract, new `### Equality intent and authoring policy` | Authority copy of the four-class taxonomy + owner reason |
| C6 | Companion amendments | companion LC-E05/E06/E10/E11/E12, LC-G07, new LC-E13 | Frozen-requirement mirror, invariant 61 included |
| C7 | Codegen doc corrections | `modeling-assumptions.md` §8, `reference/01-extraction.md`, `reference/28-…md`, `verification-matrix.md` | D1, D2, D2b, D6, D7-docs, matrix pointer |
| C8 | Code-comment corrections | `extraction/constraint_report.py`, `tests/conformance/test_extractor.py` | D7-code, three sites, zero behavior change |
| C9 | Companion doc corrections | agentic-mbse `docs/subtype-enumeration-decision-table.md`, `docs/patterns/constraints.md`, `docs/patterns/semantic-operators.md`, `docs/patterns/syntax-reference.md`, `claude/agents/sysml-expert.md` | D3, D4, D5 + equality-instruction cite |
| C10 | Backlog filings | codegen `.project/backlog/BACKLOG.md` → "Ideas / Future Considerations" | Two future-capability decision records |
| C11 | Sweep record | `.project/active/constraint-semantics-contract-amendments/verification.md` (new) | Terms, scope, raw hits, per-hit disposition, checks run |

## Non-Goals

Unchanged from the spec, and the ones this design could plausibly drift into are worth restating:
no token spellings or report field names (Item 3); no re-grade of REQ-EXT-09/REQ-CL-04 or choice of
replacement proof (Item 2); no CATF tolerance values or intent classes (Item 5); no TEAx repository
edits; no resolution of the parked D-2 vs D-4/SRC-01 conflict; no executable text.

Also explicitly not in scope, and deliberately: **no new consistency tooling.** A cross-document
checker for constraint semantics would be a plausible-sounding addition and it is not this item's
problem.

## Implementation Notes

- **Re-verify before editing in the companion.** Every companion site's quoted text is
  `[INHERITED: orchestrator read, 2026-08-12]`. The plan reads each site and confirms the quoted
  string before editing; a mismatch stops and is recorded, not guessed around.
- **D3 is a substitution, not a deletion.** The enumeration decision — `include_subtypes=True`,
  `RequirementUsage` excluded — must appear verbatim after the edit. Item 2's totality gate and
  REQ-EXT-09 both rest on it.
- **Dead citations outnumber the filename hits.** `test_extractor.py` has two filename sites
  (`:880`, `:902`) plus a by-description reference at `:881-882`; `constraint_report.py` has one
  filename site (`:6`) plus three by-description references (`:9`, `:10-11`, `:15-16`). The S1 grep
  finds only the filename ones — the rest come from C7a/C7b's explicit lists, not from the sweep.
- **`modeling-assumptions.md` §8 is edited in four places** (D1, D2, D2b, D7-docs). Make them as
  separate edits against separate quoted strings so an auditor can check each against Appendix C.
- **`captured_at` churn does not apply.** No fixture regeneration happens in this item.
- Byte-check after the code-comment edits: `git diff -- '*.py'` must show only comment and
  docstring lines.

## Potential Risks

- **The companion tree moved since 2026-08-12.** Mitigated by re-verify-then-edit; a moved target
  is a recorded stop, not an improvised edit.
- **Amendment text drifts toward Item 3's territory.** Mitigated by RI-3 and by a dedicated audit
  check: grep the diff for report field names and token spellings and confirm each appearance is
  inside a quotation of pre-amendment text.
- **The vacuous-gate warning tier lands as a new invariant (61) rather than in an existing one.**
  A new invariant is a larger contract move than an amendment. It is the honest one: the rule has
  no existing home, invariant 28 supplies only the disposition kind and carries no severity
  vocabulary, and the contract already grew by 54–60 under a prior epic. Because it is a real new
  rule it gets the full treatment every other invariant amendment gets — a companion mirror
  (B7/LC-E13) and an Appendix C acceptance cell (A10b) — by the same symmetry argument this design
  uses for LC-G07. The contract keeps no next-free-number register, so 61 could in principle
  collide with a concurrent epic; A0 records that 61 was minted by this item on 2026-08-12, which
  is the cheap half of the fix. A register is not worth building.
- **Six states, two dialects, and a normalization seam described in prose only.** If Item 3 finds a
  state with no counterpart on one side, that is a defect in this item's output by the spec's own
  criterion — so the definitions subsection states each state's counterpart obligation explicitly
  rather than leaving the bridge implied.

## Integration Strategy

Item 1 publishes; Items 2–5 build against it. Concretely: Item 2 reads invariant 28 + LC-E05 for
the third disposition kind and invariant 48 + LC-G07 for coverage-truth derivation; Item 3 reads
the definitions subsection for state meanings and invariants 46/46a for fail-closed behavior;
Item 5 reads the equality instruction and the blessed gate shape for the all-65 owner checkpoint,
which may begin as soon as those publish. ADR-009's identifier is cited back into
`.project/active/constraint-semantics-contract/product-lens.md`'s spec-F1 finding (`:32-34`,
"cite the id here"), which is what resolves the INTENDED-CHANGE disposition.

## Validation Approach

1. **Per-amendment audit against Appendix A–C of this design.** Each amendment's post-edit text
   matches the target text here, or the deviation is recorded with its reason.
2. **Pairwise agreement check (M7 — the price of five copies and no checker).** The five statements
   of the headline precedence (A0, A6, A10's mixed-population cell, B4, C1) are compared against A0
   and must agree in meaning and order. The three statements of the disposition kinds (A0/A4, B1,
   and the catalog text in C5) are compared the same way. A disagreement is a defect, not a
   stylistic variation.
3. **RI-1 disposition check (M4).** Every statement this item publishes as a description of
   behavior carries, in `verification.md`, one of two dispositions: "verified true of current
   behavior, with the evidence" or "target statement — Item N makes it true", with the item named
   in the published text. C2, C3, and C5 are dispositioned in Appendix C; the audit confirms the
   published text matches the disposition.
4. **Discharge check (RI-7).** Every listed entry appears in `verification.md` as amended or as
   verified-already-correct.
5. **Guardrail check (RI-4, RI-5).** `git diff` shows zero changes to the three RI-4 guardrail
   statements and to contract D-2 and D-4, located by their quoted text rather than by line
   number.
6. **Boundary check (RI-3, RI-6).** Diff contains no new normative token spelling or report field
   name; Python diff hunks are comment/docstring only.
7. **The recorded sweep**, run and dispositioned per Appendix D.
8. **Mechanical checks.** Codegen: `python scripts/check_doc_distinctness.py` and
   `git diff --check`. Companion: `git diff --check`, plus relative-link resolution for every
   edited Markdown file, plus — because no doc-check script exists there — a grep of `tests/` for
   the edited documentation paths; if any test references one, run it, and if none does, record
   "no docs-referencing tests in the companion" in `verification.md` as the finding it is.

## Next-Stage Handoff

**Fixed:** the seven decisions DD1–DD8; the target text in Appendices A–C; the sweep design in
Appendix D; the write order in Architecture; RI-1..RI-7.

**Open for the plan:** edit sequencing within a file; how the two repositories' commits are split
(one commit per repository is the expected shape, and neither is a PR in this item).

**De-risk first:** the companion re-verification. Read all five companion sites and confirm every
quoted string before any edit anywhere — a stale quote there is the only failure mode that would
force a second pass.

---
Next Step: after approval → `/_my_plan`.

---

# Appendix A — Contract amendments (target text)

Repository: codegen. File: `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md`.
Convention: `(amended 2026-08-12, CONSTRAINT-SEMANTICS Item 1)` at the head of the restated
statement, matching invariants 19/20/22/26. Statements amended here are agent-authored contract
prose; no provenance grade is attached to individual invariants, so none is changed.

## A0. New subsection: "Headline states and coverage truth"

**Placement:** immediately after the Source-identity subsection ends (after the "Validation and
guidance obligations" block that closes it, i.e. before `## Supported boundary and owner
decisions`, currently `:406`). Numbering stays monotone: invariant 61 follows 60.

**Text to add:**

> ### Headline states and coverage truth
>
> Added 2026-08-12 (CONSTRAINT-SEMANTICS Item 1). The decision record is ADR-009
> (`docs/architecture/modeling-assumptions.md` §9). Invariants 32, 33, 46a, and 48 point here for
> the meanings they use. This subsection fixes what each state *means* and when it may be claimed;
> the concrete report and runtime token spellings, the report schema, and the normalization-seam
> code are CONSTRAINT-SEMANTICS Item 3's.
>
> **Applicable asserted gate.** A usage is an applicable asserted gate when its source form is in
> the assert family and that form is in executable scope. **The test is on the form, not on the
> predicate:** an asserted usage whose predicate the profile `BLOCK`s or classifies
> `NON_NUMERICAL` is still an applicable asserted gate, and it stays in the feasibility
> denominator as an unassessed one. A vacuous gate — one whose owner has zero occurrences — is
> still applicable. A usage stops being applicable only when it carries an explicit
> inapplicability disposition. Plain and requirement-side usages are never applicable asserted
> gates.
>
> **Two totals, kept apart.** *Inventory totality* counts every authored usage of every form.
> *Feasibility coverage* counts applicable asserted gates only. Descriptive and requirement-side
> usages appear in inventory and never in the feasibility denominator.
>
> **The six states.**
>
> 1. **Violation** — at least one applicable asserted gate was assessed and failed.
> 2. **Indeterminate** — no violation, and at least one assessed gate produced Kleene unknown.
> 3. **Full satisfaction** — every applicable asserted gate was assessed and passed. This is a
>    coverage claim, not the absence of a failure.
> 4. **Partial coverage** — at least one applicable asserted gate exists and went unassessed,
>    including an asserted vacuous gate carrying no explicit inapplicability disposition.
> 5. **Not assessed** — the model has constraint usages but no applicable asserted gate at all. A
>    deliberately descriptive model reads here, never partial.
> 6. **Unconstrained (report absent)** — the model authors no constraint usage, so no report is
>    generated and the runtime's unconstrained disposition is true by construction.
>
> **Precedence:** violation → indeterminate → full satisfaction → partial coverage → not assessed.
>
> **Both vocabularies.** Two headline vocabularies exist — the generated report's and TEAx's
> canonical runtime one — bridged by a normalization seam. Every state above has a meaning in both
> and a counterpart across the seam. A state defined on one side with no counterpart on the other
> is a defect, and an unmapped value fails closed (invariant 46a) rather than falling through to a
> satisfied or unconstrained reading.
>
> Invariant 61 below was minted by CONSTRAINT-SEMANTICS Item 1 on 2026-08-12; invariant 60 was the
> highest live number before it. Its companion mirror is LC-E13 (companion requirements) and its
> acceptance cell is Appendix C's "Asserted vacuous gate" (A10b).
>
> 61. (added 2026-08-12, CONSTRAINT-SEMANTICS Item 1) An asserted usage whose owner has zero
>     occurrences — a vacuous gate — is visible at warning grade. The catalog carries a
>     non-reaching-with-reason disposition (invariant 28) and authoring validation emits an
>     advisory naming the usage and its detached owner. A vacuous gate counts as missing assessment
>     for feasibility coverage until it carries an explicit inapplicability disposition; carrying
>     one makes it inapplicable and removes it from the denominator. It is neither a halt nor a
>     silent pass.

## A1. Invariant 1 — target

**Current (`:130-132`):** "Every usage gets one profile disposition. Any `BLOCK` halts the model.
After generation, every other usage has executable concrete representation or a visible exclusion.
After evaluation, every module yields evidence or a named execution failure."

**Amended:**

> 1. (amended 2026-08-12, CONSTRAINT-SEMANTICS Item 1) Every usage gets one profile disposition. A
>    `BLOCK` on an **asserted** usage halts the model. A non-asserted usage never halts generation:
>    the form gate runs before the predicate walk, so an unsupported predicate written inside a
>    plain `constraint` is never reached and the usage catalogs as unassessed. Descriptive
>    constraints are never load-bearing. After generation, every other usage has executable
>    concrete representation or a visible exclusion. After evaluation, every module yields evidence
>    or a named execution failure.

## A2. Invariant 8 — guardrail

**Current (`:145`):** "Outcomes are exactly `ADMIT`, `BLOCK`, `NON_NUMERICAL`, and `UNASSESSED`."
**Disposition:** verified already-correct, no amendment needed. The new severity in A3 is a named
contextual failure, not a fifth outcome, and does not reclassify `ADMIT`. Recorded in
`verification.md`; byte-identity checked by RI-4.

## A3. Invariant 9 — target

**Current (`:146-147`):** "`ADMIT` places canonical IR inside the compiler's semantic envelope.
Downstream may not reclassify it, but named contextual lowering, graph, input, and runtime failures
remain."

**Amended:**

> 9. (amended 2026-08-12, CONSTRAINT-SEMANTICS Item 1) `ADMIT` places canonical IR inside the
>    compiler's semantic envelope. Downstream may not reclassify it, but named contextual lowering,
>    graph, input, and runtime failures remain. One of those named contextual failures halts
>    generation: an asserted usage whose form is in executable scope but which has no attachment
>    capability — structurally unattachable — fails loudly, naming the usage and the missing
>    attachment. It is a contextual failure of the kind this invariant already admits; invariant 8's
>    four outcomes are unchanged and `ADMIT` is not reclassified.

## A4. Invariant 28 — target

**Current (`:213-219`; the quoted first sentence spans `:213-215`):** begins "The canonical catalog exposes definition inventory, one visible
disposition per usage, and one concrete execution entry per admitted occurrence." (Rest of the
invariant — the field list, `owner_qn`, the entry-level join, the additive-schema-work note —
is unchanged.)

**Amended:** prefix the invariant with the convention marker and insert one sentence after the
first:

> 28. (amended 2026-08-12, CONSTRAINT-SEMANTICS Item 1) The canonical catalog exposes definition
>     inventory, one visible disposition per usage, and one concrete execution entry per admitted
>     occurrence. A visible disposition is one of three kinds — eligible, excluded-with-reason, or
>     non-reaching-with-reason — and every authored usage carries exactly one, so the dispositions
>     cover the complete authored-usage domain: "reaches no instance" is a disposition, not an
>     absence. It carries source form, usage name and QN, …*(remainder unchanged)*

## A5. Invariant 32 — target

**Current (`:227-231`), final sentence:** "A model with constraint usages but zero eligible
concrete assertions still requires the zero-input aggregator and a `not_assessed` report; a model
with no constraint usages remains inert and has no aggregator."

**Amended** (prefix the invariant with the marker; replace that final sentence):

> A constraint-bearing model with no applicable asserted gate still requires the zero-input
> aggregator and a report whose headline is the not-assessed state ("Headline states and coverage
> truth"); a model with no constraint usages remains inert and has no aggregator.

*Note for the implementer:* the trigger genuinely changes. A model with an applicable asserted gate
that produced zero eligible entries now reads partial coverage, not not-assessed.

## A6. Invariant 33 — target

**Current (`:232`):** "Headline precedence is violation, then indeterminate, then all satisfied,
then not assessed."

**Amended:**

> 33. (amended 2026-08-12, CONSTRAINT-SEMANTICS Item 1) Headline precedence is violation, then
>     indeterminate, then full satisfaction, then partial coverage, then not assessed. Full
>     satisfaction means every applicable asserted gate was assessed and passed — a coverage claim,
>     not the absence of a failure. The states, the term "applicable asserted gate", and the
>     inventory-versus-feasibility split are defined under "Headline states and coverage truth".
>     Decision record: ADR-009.

## A7. Invariants 46 and 46a — target

**Current 46 (`:262-263`):** "The public file-backed route persists and harvests the exact report
plus package identity with no consumer schema adapter."

**Amended 46:**

> 46. (amended 2026-08-12, CONSTRAINT-SEMANTICS Item 1) The public file-backed route persists and
>     harvests the exact report plus package identity with no consumer schema adapter. The exact
>     report carries compact coverage accounting derived from the catalog (invariant 48), and
>     persistence and harvest carry it through unchanged.

**Current 46a (`:264-266`):** "A constraint-free package is valid input to TEAx. Absence of the
constraint report produces empty constraint evidence rather than a `KeyError`; codegen remains free
to omit constraint-only catalog/modules for byte-stable constraint-free generation."

**Amended 46a:**

> 46a. (amended 2026-08-12, CONSTRAINT-SEMANTICS Item 1) A constraint-free package is valid input
>      to TEAx. Absence of the constraint report produces empty constraint evidence rather than a
>      `KeyError`; codegen remains free to omit constraint-only catalog/modules for byte-stable
>      constraint-free generation. The same fail-closed obligation extends to headline values: an
>      unknown or unmapped headline fails closed with a named error, never a `KeyError` and never a
>      fallthrough to a satisfied or unconstrained reading.

*RI-3 note:* neither amendment names a field. "Compact coverage accounting" is the obligation;
its shape is Item 3's.

## A8. Invariant 48 — target

**Current (`:269-273`), first sentence:** "Codegen's catalog embedded in the model contract is the
sole catalog schema authority."

**Amended** (prefix the marker; extend the first sentence, rest unchanged):

> 48. (amended 2026-08-12, CONSTRAINT-SEMANTICS Item 1) Codegen's catalog embedded in the model
>     contract is the sole catalog schema authority and the sole authority for coverage truth: the
>     report's coverage accounting is derived from it in one direction and is never an
>     independently maintained second inventory. TEAx consumes its source form, …*(remainder
>     unchanged)*

## A9. Appendix B — one row amended, one guarded

**Target row (`:660`).** Current governing correction: "No usages is inert; excluded-only usages
retain `not_assessed` visibility."

**Amended governing correction:**

> No usages is inert. A constraint-bearing model whose usages are all non-asserted reads not
> assessed; an excluded **asserted** usage puts the report at partial coverage. (amended
> 2026-08-12, CONSTRAINT-SEMANTICS Item 1)

**Guardrail row**, located by its superseded-claim text "Catalog is absent when no assertion is
admitted" (governing correction: "It is absent when no usages exist; excluded-only usages retain
catalog/report visibility"). Verified already-correct; no edit. Byte-identity checked by RI-4
against that quoted text — A0/A11 insert above it and move its line number.

## A10. Appendix C — two cells amended, one guarded

**Target 1 (`:708`), "Mixed satisfied/violated/indeterminate population".** Current: "Headline
precedence is violation → indeterminate → satisfied → not assessed with every ordinary output
retained."

**Amended:**

> Headline precedence is violation → indeterminate → full satisfaction → partial coverage → not
> assessed, with every ordinary output retained. (amended 2026-08-12, CONSTRAINT-SEMANTICS Item 1)

**Target 2 (`:682`), "Excluded-only usages" — narrow ask, a form-splitting clause.** Current:
"Portable exclusions plus `not_assessed`; no silent omission; the sealed package evaluates in TEAx
with a `not_assessed` report surface."

**Amended:**

> Portable exclusions with no silent omission; the sealed package evaluates in TEAx with a
> not-assessed report surface when every excluded usage is non-asserted, and a partial-coverage
> surface when any excluded usage is asserted. (amended 2026-08-12, CONSTRAINT-SEMANTICS Item 1)

**Guardrail, the "Zero constraint usages" row** (located by that case name). Reads correctly as
state 6. Verified already-correct; no edit. Byte-identity checked by RI-4 against the quoted row.

## A10b. Appendix C — one cell added, for invariant 61

Invariant 61 introduces observable behavior — a warning-grade disposition, an authoring-time
advisory, and a partial-coverage consequence — and Appendix C is the *mandatory* acceptance matrix,
so a new invariant with no cell would be a rule nothing has to demonstrate. Added under the same
"design may add, may not drop" clause the spec applies to the amendment list; recorded in
`verification.md` as a design addition with this reason.

**New row, placed immediately after the "Excluded-only usages" row:**

> | Asserted vacuous gate | An asserted usage whose owner has zero occurrences catalogs with a non-reaching-with-reason disposition at warning grade, authoring validation emits the advisory naming the usage and its detached owner, generation does not halt, and the report headline reads partial coverage; the same usage carrying an explicit inapplicability disposition drops out of the feasibility denominator and the headline reads full satisfaction when every remaining gate passed. |

## A11. New subsection: "Equality intent and authoring policy"

**Placement:** under `## Supported boundary and owner decisions`, after the D-3 bullet (`:433`) and
before `### Source-identity dispositions (D-4 onward)` (`:435`).

**Text to add:**

> ### Equality intent and authoring policy
>
> Added 2026-08-12 (CONSTRAINT-SEMANTICS Item 1). This is the authority copy; agentic-mbse's
> authoring guidance cites it and does not restate it.
>
> **[NEED]** (owner-stated, 2026-08-12) Narrow bands of viability make design exploration really
> difficult, so the guidance must say *when* an equality should be used at all — not only how the
> pipeline treats one. **[NEED]** (owner-stated, 2026-08-12) Tolerance values are modeled values
> the modeler chooses. The pipeline never invents one.
>
> **[AGENT] (ratified by owner, 2026-08-12)** The intent behind a written `a == b` falls into four
> classes, and each has a different correct authoring move. This taxonomy is agent-originated and
> owner-reviewed; challenge it by re-deriving against the reasoning recorded here.
>
> 1. **Structural identity** — `b` is `a` by construction. Derive it; do not constrain it. A
>    constraint here adds a gate that can only ever pass or reveal a modeling error.
> 2. **Cross-check of independently computed values** — two paths compute the same physical
>    quantity. Use a loose, physically motivated validity band, sized to the disagreement you would
>    actually accept, not to floating-point noise.
> 3. **Feasibility gate** — you want the design to satisfy a limit. Prefer a one-sided inequality.
>    If a quantity genuinely must equal a value, fix it as an input rather than search for it and
>    then constrain it; searching a zero-measure set is why exploration collapses.
> 4. **Composition closure** — terms must sum to a whole. Derive the last term by construction;
>    where that is not possible, use a banded validity check as in class 2.
>
> Behavioral consequence, already stated elsewhere and repeated here only as a pointer: invariant
> 11 governs which equality forms execute, and the profile's real-equality block list is documented
> in `docs/architecture/modeling-assumptions.md` §8.

---

# Appendix B — Companion amendments (target text)

Repository: codegen. File: `.project/concepts/constraint-execution-lifecycle-requirements.md`.
**Convention (DD4).** The license to rewrite is the copy-and-freeze header's "forward requirement
amendments happen here only" (`:3-7`). The *form* of the amendment note follows LC-E04B's
trailing-sentence shape (`:272-274`), which is the file's only precedent and is a pure append —
this item is what establishes the rewrite. Every amendment note therefore does four things:

1. carries its own grade, `[AGENT] (ratified by owner, 2026-08-12)`, so new content never wears the
   amended statement's grade (RI-2, spec `[HARD]` law 1);
2. **quotes the text it supersedes**, so a rewrite loses nothing from the record;
3. cites the governing contract invariant, and ADR-009 where the change is the headline decision;
4. leaves the requirement's own grade marker and `Source:` line untouched.

B1's note additionally carries the one-time convention statement: *"This item rewrites requirement
text in place under the header's forward-amendment rule; the superseded text is quoted in each
amendment note."*

**B1. LC-E05** `[INFERRED]` — insert the disposition-kind clause after "one visible disposition per
usage," and append:

> Amended 2026-08-12 (CONSTRAINT-SEMANTICS Item 1), `[AGENT] (ratified by owner, 2026-08-12)`: a
> visible disposition is one of three kinds — eligible, excluded-with-reason, or
> non-reaching-with-reason — and the dispositions cover the complete authored-usage domain;
> "reaches no instance" is a disposition, not an absence. Superseded: the requirement named no
> disposition kinds and left non-reaching usages uncovered. See contract invariant 28 (amended).
> *(This item rewrites requirement text in place under the header's forward-amendment rule; the
> superseded text is quoted in each amendment note.)*

**B2. LC-E06** `[INHERITED]` — rewrite the first clause to name non-reaching usages, then append:

> Excluded, unassessed, and non-reaching usages remain inspectable with identity, reason, and
> portable location. They never masquerade as executed constraints or vanish from coverage.
> Amended 2026-08-12 (CONSTRAINT-SEMANTICS Item 1), `[AGENT] (ratified by owner, 2026-08-12)`: the
> same guarantee now covers non-reaching usages. Superseded: "Excluded/unassessed usages remain
> inspectable…". See contract invariant 28 (amended).

**B3. LC-E10** `[INHERITED]` — replace the final sentence's trigger, then append:

> …A model with constraint usages but no applicable asserted gate still requires the zero-input
> aggregator and a report carrying the not-assessed state; a model with no constraint usages
> remains inert and has no aggregator. Amended 2026-08-12 (CONSTRAINT-SEMANTICS Item 1),
> `[AGENT] (ratified by owner, 2026-08-12)`: the trigger is the absence of an applicable asserted
> gate, not the absence of eligible concrete assertions — an applicable gate that produced zero
> eligible entries reads partial coverage. Superseded: "A model with constraint usages but zero
> eligible concrete assertions still requires the zero-input aggregator and a `not_assessed`
> report". See contract invariant 32 (amended).

**B4. LC-E11** `[INHERITED]` — the direct contradiction, and the one wholesale replacement. The
requirement keeps its `[INHERITED]` marker and its `Source:` line, because those grade *what the
requirement is about* and where it came from; the replacement body carries its own grade so no
reader mistakes the new precedence for something inherited from the original concept:

> - **LC-E11 [INHERITED]** Report headline precedence is: violation, then indeterminate, then full
>   satisfaction, then partial coverage, then not assessed. Full satisfaction requires every
>   applicable asserted gate to have been assessed and passed; an assessed result alone does not
>   earn it. Source: original concept and generation spec — which is the source of the requirement's
>   subject, not of the precedence below. Amended 2026-08-12 (CONSTRAINT-SEMANTICS Item 1),
>   `[AGENT] (ratified by owner, 2026-08-12)`, sourced to
>   `.project/active/constraint-semantics-contract/spec.md` and ADR-009: the coverage-truthful
>   five-state precedence above **replaces** the inherited rule in full. Superseded: "Report
>   headline precedence is: any violation → `violation`; else any indeterminate → `indeterminate`;
>   else any assessed result → `all_satisfied`; else `not_assessed`." See contract invariant 33
>   (amended).

**B5. LC-E12** `[INHERITED]` — rewrite the final sentence:

> - **LC-E12 [INHERITED]** Constraint-free models remain byte-stable. No constraint usage means no
>   constraint catalog or modules. An asserted usage with zero eligible entries still produces
>   visible exclusions and puts the report at the partial-coverage state; a constraint-bearing model
>   whose usages are all non-asserted reads not assessed. Amended 2026-08-12 (CONSTRAINT-SEMANTICS
>   Item 1), `[AGENT] (ratified by owner, 2026-08-12)`, sourced to ADR-009: zero eligible entries
>   under an asserted usage is partial coverage, not the not-assessed surface. Superseded:
>   "Constraint usages with zero eligible entries still produce visible exclusions and the
>   `not_assessed` report surface." See contract invariants 32 and 33 (both amended).

**B6. LC-G07** `[NEED]`, owner-sourced — the clause is mirrored, and the mirror carries its own
grade so the owner grade is not diluted (RI-2). Append, leaving the existing text and its owner
quote byte-identical:

> Amended 2026-08-12 (CONSTRAINT-SEMANTICS Item 1), `[AGENT] (ratified by owner, 2026-08-12)`: the
> embedded catalog is also the sole authority for coverage truth — the report's coverage accounting
> derives from it in one direction and is never an independently maintained second inventory. See
> contract invariant 48 (amended). The owner-sourced requirement above is unchanged.

**B7. LC-E13 — new requirement, the companion mirror of invariant 61.** Added after LC-E12 in
section E, taking the next free identifier in that block.

> - **LC-E13 [AGENT] (ratified by owner, 2026-08-12)** An asserted usage whose owner has zero
>   occurrences — a vacuous gate — is visible at warning grade: the catalog carries a
>   non-reaching-with-reason disposition and authoring validation emits an advisory naming the usage
>   and its detached owner. It counts as missing assessment for feasibility coverage until it
>   carries an explicit inapplicability disposition, at which point it leaves the denominator. It is
>   neither a generation halt nor a silent pass. Added 2026-08-12 (CONSTRAINT-SEMANTICS Item 1),
>   mirroring contract invariant 61 (minted by the same item); acceptance in contract Appendix C,
>   "Asserted vacuous gate".

*Why the mirror exists:* the same argument the design makes for LC-G07 below, applied
symmetrically. The frozen companion is what Items 2 and 3 read for requirements; an invariant with
no companion requirement means the warning tier — the whole middle tier between the halting error
and the never-errors record — is invisible on the side that implements it.

*Design ruling on the spec's "if design concludes the clause needs no companion mirror":* it needs
one. LC-G07 and invariant 48 are a stated pair; leaving only one of them carrying the coverage-truth
clause is exactly the disagreement the spec asked to prevent.

---

# Appendix C — Documentation corrections (target text)

## C1 — ADR-009 (codegen `docs/architecture/modeling-assumptions.md`, new §9)

Placed between §8's closing `---` and `## Validation Rules`.

> ## 9. Coverage Truth and Headline Semantics (ADR-009)
>
> **Decision record.** Filed 2026-08-12 under CONSTRAINT-SEMANTICS Item 1.
> **Provenance:** `[AGENT] (ratified by owner, 2026-08-12)` — agent-proposed, owner-ratified.
> Ratification does not make it owner-originated, and it is challengeable by re-deriving against
> the reasoning below.
>
> **Context.** A constraint report headline is what a study reads to decide whether a design point
> is feasible. Two rules made that headline unreliable: a plain `constraint` was cataloged but never
> executed, and the headline claimed satisfaction whenever *any* assessed result passed. A model
> could therefore read fully satisfied while every gate a modeler wrote went unassessed.
>
> **What the contract said.** Lifecycle contract invariant 33: "Headline precedence is violation,
> then indeterminate, then all satisfied, then not assessed." Frozen companion LC-E11: "Report
> headline precedence is: any violation → `violation`; else any indeterminate → `indeterminate`;
> else any assessed result → `all_satisfied`; else `not_assessed`."
>
> **What it says now.** Precedence is violation → indeterminate → full satisfaction → partial
> coverage → not assessed. Full satisfaction is a coverage claim: every applicable asserted gate was
> assessed and passed. A new partial-coverage state carries the case where an applicable asserted
> gate exists and went unassessed. The definitions live in the lifecycle contract's "Headline states
> and coverage truth" subsection
> (`.project/concepts/constraint-execution-authoritative-lifecycle-contract.md`), which is the one
> authority for both repositories' vocabularies.
>
> **Why.** A headline that cannot distinguish "checked and passed" from "not checked" is not
> evidence. The change makes the claim honest at the cost of one additional state, and the study
> layer keeps a design point at the boundary rather than accepting it on a coverage gap.
>
> **Scope.** This record governs the headline vocabulary's meaning. The concrete report and runtime
> token spellings, the report schema, and the normalization-seam code are CONSTRAINT-SEMANTICS
> Item 3's.
>
> **Consequences filed:** lifecycle contract invariants 1, 9, 28, 32, 33, 46/46a, 48, new 61, and
> Appendix B/C cells; companion LC-E05/E06/E10/E11/E12 and LC-G07.

**Cite-back:** add the identifier to `.project/active/constraint-semantics-contract/product-lens.md`
spec-F1 (`:32-34`, "cite the id here"), as: `Filed: ADR-009 —
docs/architecture/modeling-assumptions.md §9 (2026-08-12).` No other product-lens text changes.

## C2 — D1 (codegen `modeling-assumptions.md:489-492`)

**Current:** "**What a modeler needing an enforced gate should do.** Author an `assert constraint`
(or bare `constraint`/`require constraint`) against a defined `constraint def`, bind every formal to
a real value in scope, and keep any equality check as an explicit two-inequality tolerance band. If
the profile BLOCKs it, the generation error names the exact construct to fix."

**RI-1 disposition: verified true of current behavior at `882161e`.** The assert-family-only rule
is what the profile does today — `agentic_mbse/sysml/executable_profile.py:949-950` routes
`satisfy`, `requirement_constraint`, and `plain_usage` to UNASSESSED *before predicate inspection*,
and `constraint_extraction.py:726-735`'s `_effective_predicate_source` returns `None` for
`plain_usage`, so an authored bare body is never read as a predicate. Evidence:
`.project/research/20260812-101200_constraint-semantics-end-to-end.md` §2 ("Form classification",
"Profile gate"). The blessed shape's end-to-end behavior is likewise current — the same register
records `fusion_tea`'s `assert constraint x : Def { in formal = child.attr; }` admitting, lowering,
generating a module and aggregator, and driving study dispositions. No pending marker; no item
named.

**Replacement** (discharges D1, publishes the blessed gate shape and its three scope carve-outs,
the modeler-owned-tolerance `[NEED]`, and the equality-instruction cite):

> **What a modeler needing an enforced gate should do.** Use the assert family. It is the only
> enforcement opt-in: a bare `constraint`, a `require constraint`, an `assume constraint`, and a
> `satisfy` are visible, cataloged descriptions that never execute. The blessed shape is a
> `constraint def` with formals, asserted with every formal bound to a real value in scope:
>
> ```sysml
> constraint def MarginOk { in produced : Real; in required : Real; produced >= required }
> // ...
> assert constraint g : MarginOk { in produced = plant.net_power; in required = target_power; }
> ```
>
> Three scope points that are easy to over-read. The restriction on what a predicate body may
> reference is **predicate-body-only**: the body works over formals. Feature chains in *binding*
> position stay supported, as the example shows. Inline asserted forms stay admitted — a definition
> is not required. Admitting feature chains inside the predicate body is a filed future capability
> candidate, not a closed door.
>
> **Tolerances are yours.** Where a check needs a band, the tolerance is a modeled value you choose
> and can override; the pipeline never invents one.
>
> **Before writing an equality at all**, check which of four intents you have. Structural identity:
> derive it, do not constrain it. A cross-check of two independently computed values: use a loose,
> physically motivated validity band. A feasibility gate: prefer a one-sided inequality, and if a
> quantity must equal a value, fix it as an input rather than search for it and then constrain it.
> Composition closure: derive the last term by construction, or fall back to a banded check. The
> reasoning behind these four, and the owner's reason for them, is in the lifecycle contract's
> "Equality intent and authoring policy" (this repository,
> `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md`) — the authority
> copy.
>
> If the profile BLOCKs an asserted constraint, the generation error names the exact construct to
> fix.

## C3 — D2 (codegen `modeling-assumptions.md:468-470`)

**Current, third bullet:** "**unassessed** — a requirement-side usage
(`RequirementUsage`/`SatisfyRequirementUsage`, excluded from execution by design) or an
out-of-profile owner (e.g. a `requirement_def` owner) is cataloged defensively — one record, no
expansion, no formal resolution, no node — never silently absent."

**RI-1 disposition: split — the never-executed half is current, the cataloged half is a target.**

- *Never executed under any non-assert form*: **verified true at `882161e`**, same evidence as C2
  (`executable_profile.py:949-950`; a standalone `require constraint` classifies `plain_usage`, and
  a `require`/`assume` under a `RequirementConstraintMembership` classifies
  `requirement_constraint` — both route to UNASSESSED pre-predicate).
- *Cataloged, one record each, never silently absent*: **target — CONSTRAINT-SEMANTICS Item 2 makes
  it true.** Today only usages that produced instance-graph nodes get carriers; a usage with zero
  scopes appears nowhere (research register §2 "Catalog"; the CATF census shows 56 of 65 usages
  with no carrier). Per RI-1 the published text says what must be true and names the item.

**Replacement:**

> - **unassessed** — every usage outside the assert family is never executed: a plain `constraint`,
>   a `require constraint`, an `assume constraint`, and the requirement-side
>   `RequirementUsage`/`SatisfyRequirementUsage` all land here. So does an out-of-profile owner
>   (e.g. a `requirement_def` owner), which draws a named visible exclusion rather than an
>   unreachable-assert error. Each one gets a catalog record — no expansion, no formal resolution,
>   no node — and none is silently absent. *(Catalog totality is the target state: today a usage
>   that reaches no instance gets no carrier at all. CONSTRAINT-SEMANTICS Item 2 closes that gap.)*

## C4 — D2b (design-added, codegen `modeling-assumptions.md:460`)

**Current:** "**The three outcomes.** `agentic-mbse`'s executable profile (`evaluate_profile`)
classifies every swept `ConstraintUsage` (subtypes included) exactly one way:"

**Defect:** the profile has four outcomes (contract invariant 8, a guardrail this item must not
change; `reference/28-constraint-lowering-and-catalog.md:11`). §8 folds `NON_NUMERICAL` into
unassessed and calls the result three. Leaving it would ship a modeler doc contradicting a guardrail
invariant in the same item that pins the guardrail.

**Replacement:** "**The four outcomes.**" and add a bullet between BLOCK and unassessed:

> - **NON_NUMERICAL** — the predicate is well-formed but not numerically executable (Boolean,
>   string, or enum comparison). It warns with its identity, location, and profile diagnostics, then
>   becomes a visible exclusion.

*Added under the spec's "at minimum … design may add, may not drop" clause. Recorded in
`verification.md` as a design addition with this reason.*

## C5 — D6 (codegen `reference/28-constraint-lowering-and-catalog.md:44-49`)

**Current, step 2:** "**Owner-kind dispatch** (D5): `part_def` owners expand to one concrete
instance per `OccurrenceIndex.occurrences_of()` result; `calc_def` owners expand to one per matching
concrete calc usage; `package` owners are already concrete (one instance, top-level scope). Any
other owner kind (e.g. `requirement_def`) is defensively cataloged **unassessed** — one record,
`eligible=False`, no expansion, no formal resolution, no node (D7)."

**RI-1 disposition: split, the same way as C3.** *Status follows source form*: **verified true at
`882161e`** — the profile gates on form before predicate inspection
(`executable_profile.py:949-950`). *Catalogs unassessed under **any** owner kind*: **target —
CONSTRAINT-SEMANTICS Item 2 makes it true.** `elaboration/elaborate.py:522-539`
(`_scopes_for_owner`) has branches for `PartDefinition`, `PartUsage`, and `Package` and **no
`CalculationDefinition` branch**, so calc-def-owned usages produce zero nodes and no carrier
regardless of form (research register §2 "Instance reach"; 51 of CATF's 65 usages). The published
text names the item.

**Replacement** (the two axes separated, per contract invariant 16):

> 2. **Owner-kind dispatch** (D5) decides *occurrence expansion only*: `part_def` owners expand to
>    one concrete instance per `OccurrenceIndex.occurrences_of()` result; `calc_def` owners expand to
>    one per matching concrete calc usage; `package` owners are already concrete (one instance,
>    top-level scope). An owner kind with no expansion rule (e.g. `requirement_def`) yields no
>    occurrence, and the usage is cataloged with one record, `eligible=False`, no expansion, no
>    formal resolution, no node (D7).
>
>    **Unassessed status follows source form, not owner kind.** The axes are independent (contract
>    invariant 16): only the assert family executes, so a plain, `require`, `assume`, or
>    requirement-side usage catalogs unassessed under *any* owner kind, and an asserted usage under
>    an expandable owner is the only shape that can become eligible. *(Target state for the
>    owner-kind half: today an owner kind with no expansion branch — a `calc def` owner — yields no
>    occurrence and therefore no catalog record at all. CONSTRAINT-SEMANTICS Item 2 closes that.)*

## C6 — D7-docs, three sites

**C6a. `modeling-assumptions.md:482-487`.** Current paragraph opens "**Every manifest entry has a
carrier — the migration invariant.**" and names `test_constraint_migration_mapping.py` as the
license-free proof surface.

**Replacement:**

> **Every manifest entry has a carrier — the migration invariant.**
> `collect_constraint_manifest()` still sweeps the model exactly as before (REQ-EXT-09), and the
> catalog is where every swept usage lands: an eligible concrete entry, an explicit unassessed
> record, or a named, justified requirement/satisfy exclusion — nothing silently absent. The
> license-free totality proof that used to be cited here retired with the legacy stack; the
> independent proof that the invariant holds across every constraint-bearing fixture is pending,
> and CONSTRAINT-SEMANTICS Item 2 re-anchors it. (citation removed 2026-08-12,
> CONSTRAINT-SEMANTICS Item 1)

**C6b. `reference/28-constraint-lowering-and-catalog.md:100-101`.** Current: "The migration mapping
test (`test_constraint_migration_mapping.py`, D1/INV-A) proves every swept usage lands in exactly one
catalog outcome."

**Replacement:**

> Every swept usage lands in exactly one catalog outcome. The test that proved this retired with the
> legacy stack; the replacement totality proof is pending under CONSTRAINT-SEMANTICS Item 2.
> (citation removed 2026-08-12, CONSTRAINT-SEMANTICS Item 1)

**C6c. `reference/01-extraction.md:20`, REQ-EXT-09 evidence cell.** Current cell opens
"`test_constraint_migration_mapping.py` proves this total across every constraint-bearing fixture;"
then carries two further clauses.

**Replacement of that first clause only** (DD7 — the other three clauses stay verbatim):

> Totality across every constraint-bearing fixture has no live proof: the test that carried it
> retired with the legacy stack, and CONSTRAINT-SEMANTICS Item 2 re-anchors the evidence (citation
> removed 2026-08-12, CONSTRAINT-SEMANTICS Item 1);

Requirement text and Status are untouched — choosing the replacement proof is Item 2's.

## C7 — D7-code, three sites (comment/docstring only, zero behavior change)

**C7a. `src/sysml_codegen/extraction/constraint_report.py:5-7`.** Current: "…the manifest side of
the manifest->catalog no-silent-drop mapping test
(`tests/conformance/test_constraint_migration_mapping.py`, D1/INV-A)."

**Replacement:** "…the manifest side of the manifest->catalog no-silent-drop mapping. The test that
proved that mapping retired with the legacy stack; CONSTRAINT-SEMANTICS Item 2 re-anchors the
proof." **Three dangling references in the same docstring go with it** — the S1 grep will not find
them, because they name the test by description rather than by filename:

- `:9` "the catalog is now the **proven** single source of truth" → drop "proven"; the proof it
  referred to is the retired test. (Same word C7b strips from the parallel phrase.)
- `:10-11` "both load-bearing for the mapping test" → "both load-bearing for the mapping".
- `:15-16` "the mapping test's justified carrier-free category" → "the mapping's justified
  carrier-free category".

**C7b. `tests/conformance/test_extractor.py:878-882`** (class docstring). Current: "…(the catalog is
now the proven single source of truth, `test_constraint_migration_mapping.py`); what survives here
is the manifest sweep itself (still live, still load-bearing for the mapping test)…"

**Replacement:** "…(the catalog is now the single source of truth; its totality proof retired with
the legacy stack and is re-anchored by CONSTRAINT-SEMANTICS Item 2); what survives here is the
manifest sweep itself (still live, still load-bearing for the manifest→catalog mapping)…" — the
`:881-882` "the mapping test" reference is corrected in the same edit, for the same reason as
C7a's dangling three.

**C7c. `tests/conformance/test_extractor.py:902`** (inline comment). Current: "# confirmed
empirically — see test_constraint_migration_mapping.py)."

**Replacement:** "# confirmed empirically against the fixture source, transcribed above)."

No assertion, name, or value changes at any of the three sites.

## C8 — matrix pointer (codegen `docs/architecture/verification-matrix.md:336`)

Appended to the **Test File** cell, after the existing two test citations (DD6). Exact text:

> ; totality-evidence re-grade pending — CONSTRAINT-SEMANTICS Item 2 (noted 2026-08-12)

Requirement text and the `PASS` status are untouched.

## C9 — Companion repository corrections (agentic-mbse)

All current-text quotes are `[INHERITED: orchestrator read, 2026-08-12]`; re-verify each before
editing.

**D3 — `docs/subtype-enumeration-decision-table.md:24`, row 1 Rationale.** Current: "`assert`
(`AssertConstraintUsage`) and `require`/plain are executable constraint usages (lowered under the
profile); `RequirementUsage` + its `satisfy` subtype are requirement-side and excluded".

**Replacement — a substitution of reason. The enumeration decision (`include_subtypes=True`,
`RequirementUsage` EXCLUDED) survives verbatim; only the reason changes:**

> `require`/plain subtypes are enumerated for visibility and catalog totality — every authored usage
> gets a catalog disposition — not because they execute. Only the assert family
> (`AssertConstraintUsage`) executes, lowered under the profile. `RequirementUsage` + its `satisfy`
> subtype are requirement-side and excluded from the sweep.

The `include_subtypes=True` setting, the EXCLUDE decision, and every other column are unchanged.
REQ-EXT-09 and Item 2's totality gate rest on this enumeration.

**D4 — `docs/patterns/constraints.md:190-199`.** Current: heading "### Wrong: Plain constraint block
(no prefix)", inline comment "// WRONG: Not recognized as ConstraintUsage!", and "**Error:** Parser
does not create proper AST node without prefix."

The stated reason is false — the parser does produce a `ConstraintUsage`, classified `plain_usage`.
**Replacement:**

- Heading → `### Not a check: plain constraint block (no prefix)`
- Inline comment → `// Parses fine — a ConstraintUsage — but never executes`
- Error line → `**Why it never runs:** the parser does create a ConstraintUsage; it is classified
  \`plain_usage\`, and the form gate stops it before the predicate is ever walked. It is cataloged
  and visible, never enforced. Use \`assert constraint\` for a check.`

Must stay consistent with the correct four-outcome story already at `:25-41` — the implementer reads
that block first and matches its vocabulary.

**D5 — four defective sites, one ruled site.**

- **D5-a. `claude/agents/sysml-expert.md:124`** — `require constraint { system.flowRate >=
  requiredFlow }` presented as check guidance. Replace the form with `assert constraint { … }`,
  keeping the predicate and surrounding prose. If the surrounding prose names `require`, it is
  rewritten to say the assert family is the enforcement opt-in.
- **D5-b. `docs/patterns/semantic-operators.md:~503-512`**, section "### Correct: Assert/require
  prefix" with "assert constraint TempLimit {  // Creates ConstraintUsage!". Heading →
  `### Correct: assert prefix`. The inline comment's claim is the D4 defect again — replace with
  `// Executes: the assert family is the enforcement opt-in`. Remove `require` from the section's
  "correct check form" framing.
- **D5-c. `docs/patterns/semantic-operators.md:520`** — "- `require constraint` - Preconditions that
  must be satisfied". Replace with: "- `require constraint` — a requirement-side precondition. It is
  cataloged and visible; it is not executed and does not gate generation."
- **D5-d. `docs/patterns/semantic-operators.md:545`** — "-> Use `assert constraint` or `require
  constraint` (with prefix!)". Replace with: "-> Use `assert constraint` (with prefix!)".
- **D5-e. `docs/patterns/syntax-reference.md:185`** — "- `require constraint` - Precondition".
  **Ruling (DD8), applied by the implementer against the file as read:** if the surrounding list is
  a syntax inventory and the entry describes `require constraint` as a requirement-side precondition
  without claiming it is checked, enforced, or gates anything, it is **correct as written** — under
  the ruled semantics a `require` *is* a precondition conjunct in its owning requirement's
  implication. No edit; the disposition and the quoted framing sentence go in `verification.md`.
  If instead the list is framed as forms for authoring checks, apply the D5-c replacement text. The
  implementer records which branch fired and quotes the sentence that decided it. Default
  expectation, stated so a deviation is visible: the no-edit branch.

**Equality instruction, rendered in full (DD2/DD3, revised per review M6).** The owner asked for
this "in our concept **in addition to** the sysml-codegen support," so the companion gets the
instruction, not a pointer to it. A modeler reading `docs/patterns/constraints.md` must be able to
act on it without a second checkout — `.project/` is working-artifact space and a companion reader
may not have the codegen tree at all. Added to `docs/patterns/constraints.md`, adjacent to the
four-outcome block at `:25-41`:

> ### When should you write an equality at all?
>
> A numerical `==` does not execute as a check (see the outcomes above), and even where it could, an
> exact equality is usually not what you mean. Find your intent, then use the move next to it.
>
> | Your intent | The move |
> |---|---|
> | `b` **is** `a` by construction — structural identity | Derive `b`. Do not constrain it. |
> | Two independently computed values should agree — a cross-check | A loose, physically motivated validity band, sized to the disagreement you would accept. |
> | The design must meet a limit — a feasibility gate | A one-sided inequality. If a quantity must *equal* a value, fix it as an input rather than searching for it and constraining it. |
> | Terms must sum to a whole — composition closure | Derive the last term by construction; where you cannot, use a banded check as above. |
>
> **Why it matters:** narrow bands of viability make design exploration really difficult — searching
> a zero-measure set is why a study stops finding feasible points.
>
> **Tolerances are yours.** A band's tolerance is a modeled value you choose and can override. The
> pipeline never invents one.
>
> `[AGENT] (ratified by owner, 2026-08-12)` — the four classes are agent-originated and
> owner-reviewed; the *need* for this guidance is owner-stated. The reasoning behind each class,
> and the record you would challenge it against, is the authority copy: sysml-codegen
> `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md`, "Equality intent and
> authoring policy". **This is not a second authority** — it is the same instruction, rendered where
> the instructed reader is. If the two ever disagree, the contract governs.

**ADR-009 cite (DD2, home revised per review n6).** One line in `docs/patterns/constraints.md` — the
document a reader of constraint semantics is actually in, and the one that already carries the
correct four-outcome story at `:25-41` and now the equality instruction: `Coverage and headline
semantics are recorded in ADR-009 (sysml-codegen docs/architecture/modeling-assumptions.md §9).`
*Rejected: `docs/subtype-enumeration-decision-table.md` — a coverage-and-headline decision cited
from a subtype-enumeration table is an odd meeting place.* No stub file.

## C10 — Backlog filings (codegen `.project/backlog/BACKLOG.md`)

Two bullets appended under `## Ideas / Future Considerations` (`:715`), phrased as decision records
and not as instructions to a future agent:

> - **In-predicate feature-chain admission (CONSTRAINT-SEMANTICS Item 1, filed 2026-08-12).** The
>   blessed gate shape restricts predicate bodies to formals; feature chains stay supported in
>   binding position. Admitting them inside the predicate body was left open as a candidate rather
>   than decided against — the published contract calls it a filed future capability, and this is
>   the filing.
> - **Evaluated advisory tier for plain constraints (CONSTRAINT-SEMANTICS Item 1, filed
>   2026-08-12).** A plain `constraint` is a visible, cataloged, never-executed description. Whether
>   a plain constraint could additionally be *evaluated* and surfaced as a non-gating advisory was
>   left open as a candidate; this is the filing.

---

# Appendix D — The recorded sweep

**Deliverable:** `.project/active/constraint-semantics-contract-amendments/verification.md`, created
by this item. D1–D7 plus the sites named in the spec are the floor.

**Scope (DD5).** In both repositories: `docs/`, `src/`, `tests/`, `scripts/`, `README.md`,
`CLAUDE.md`, `.project/concepts/`, `.project/backlog/`. Excluded: `.project/research/`,
`.project/completed/`, `.project/active/` — dated records, provenance under the contract's reading
rule (`:19-21`). The exclusion and this reason are written into `verification.md`; the boundary is
recorded, not silent.

**Terms.** Five, run over documentation *and* comment/docstring text (the `--include` set covers
`.md`, `.py`, and `.sysml`):

| # | Term | Command shape |
|---|---|---|
| S1 | retired test name | `grep -rn "test_constraint_migration_mapping" <scope>` |
| S2 | `require constraint` taught as a check | `grep -rn "require constraint" <scope>` |
| S3 | plain-constraint-enforces claims (verb alternation widened per review M5) | `grep -rniE "constraint[s]? (are \|is )?(enforced\|checked\|verified\|evaluated\|a gate\|gates\|blocks)\|enforced (gate\|constraint)\|plain constraint.*(execut\|enforc\|gate\|check\|verif\|evaluat\|block)" <scope>` |
| S4 | the superseded headline precedence | `grep -rniE "all[_ ]satisfied\|else any assessed\|any assessed result" <scope>` |
| S5 | `assume`/`satisfy` taught as a check | `grep -rn "assume constraint\|satisfy requirement" <scope>` |

**Why S4 and S5 exist.** They cover the item's *own* corrected vocabulary, which the first three
terms miss. S4 catches a sixth living statement of the superseded precedence — the report template
and its tests run on the old vocabulary today, so living prose almost certainly restates it, and a
statement of the old precedence surviving this item would contradict the five places the item
amends. S5 catches guidance teaching `assume constraint` or `satisfy` as an enforcement form: C2 and
C3 widen the never-executes set to include both, which puts them inside the defect class.

*Expected S4 collision, resolved in advance:* S4 will hit the amended text this item writes, since
the amendment notes quote the superseded precedence verbatim (M2). Run S4 **before** the edits, and
disposition any post-edit hit inside an amendment note as "quoted supersession, correct as written".

Run S1–S5 in the companion repository with the same scope. Add a term there if the D4/D5 reads
surface a local idiom these five miss; adding a term is allowed, dropping one is not.

**Disposition format.** One row per raw hit. A summary does not discharge the criterion.

```markdown
| # | Term | Repo | File:line | Quoted hit | Disposition | Note |
|---|------|------|-----------|------------|-------------|------|
| 1 | S1 | codegen | docs/architecture/modeling-assumptions.md:484 | "…kept conformance test (`test_…`) reads directly…" | corrected (C6a) | dead citation to a deleted file |
| 2 | S2 | codegen | src/sysml_codegen/extraction/constraint_report.py:35 | "# constraint / require constraint -> ConstraintUsage" | correct as written | a classification statement, not check guidance |
```

**Pre-run result, codegen only, 2026-08-12** (recorded here so the plan can size the work; the
implementer re-runs and records the raw output, and does not copy this):

- S1 → 6 living-surface hits: `modeling-assumptions.md:484`, `reference/01-extraction.md:20`,
  `reference/28-…:100`, `constraint_report.py:6`, `test_extractor.py:880`, `test_extractor.py:902`.
  All six are corrected by C6/C7.
- S2 → 9 living-surface hits. One (`modeling-assumptions.md:490`) is D1, corrected by C2. Eight are
  correct as written — `constraint_report.py:35`, `tests/fixtures/item4_require/model.sysml:5,17,19`,
  `test_extractor.py:983,987,995,1008` — each states that `require constraint` *is* a plain
  `ConstraintUsage`, which is true and is not check guidance. `BACKLOG.md:170-171` sits in an
  excluded-by-content historical finding block; the implementer dispositions it explicitly either
  way rather than skipping it.
- S3 → 1 living-surface hit under the *narrow* regex, `modeling-assumptions.md:489`, D1's own
  heading, corrected by C2. The widened alternation was not pre-run; expect more.
- **S4 and S5 were not pre-run.** They were added after the design review and their hit sets are
  unknown. Treat that as unsized work in the plan, not as an empty result — S4 in particular is
  expected to hit living prose around the report template and its tests.

**Checks recorded in `verification.md` alongside the sweep.** Codegen:
`python scripts/check_doc_distinctness.py`, `git diff --check`. Companion: `git diff --check`;
relative-link resolution for each edited Markdown file; and the docs-referencing-test finding —
grep `tests/` for the edited documentation paths, run any test that references one, and if none
does, record "the companion has no doc-check script and no docs-referencing tests; `git diff --check`
plus link resolution is the whole mechanical surface" as the finding rather than as a pass.

**Second table: the discharge record.** Everything that is not a sweep hit gets the same treatment —
one row, not prose, so the RI-7 check is mechanical rather than interpretive:

```markdown
| Entry | Disposition | Verification note |
|-------|-------------|-------------------|
| contract invariant 8 | verified already-correct | four outcomes unchanged; new severity is a contextual failure (A3), not a fifth outcome |
| Appendix C "Zero constraint usages" | verified already-correct | reads as state 6 (unconstrained, report absent) |
| Appendix B "Catalog is absent when no assertion is admitted" | verified already-correct | catalog/report visibility claim is unaffected by the coverage change |
| C4 / D2b ("three outcomes" → four) | design addition | §8 contradicted invariant 8, the guardrail this item pins |
| A10b (Appendix C "Asserted vacuous gate") | design addition | invariant 61 is a mandatory-matrix behavior with no cell |
| B7 (LC-E13) | design addition | companion mirror for invariant 61, per the LC-G07 symmetry argument |
| C2 / C3 / C5 RI-1 dispositions | current-behavior or target | one row each, evidence or the item named (see Appendix C) |
| D5-e (`syntax-reference.md:185`) | branch fired: … | the quoted framing sentence that decided it |
| <any correction blocked by executable text> | handed on | the item that owns that code, by name |
```

Also recorded: the DD5 scope exclusion and its reason; the companion doc-check finding; and the
convention statement B1 carries (this item establishes in-place rewriting under the companion
header's forward-amendment rule).
