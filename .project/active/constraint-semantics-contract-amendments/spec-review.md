# Spec Review: Constraint Contract and Authoring Policy (CONSTRAINT-SEMANTICS Item 1)

**Spec:** `.project/active/constraint-semantics-contract-amendments/spec.md`
**Contract:** `claude-pack/commands/_my_spec.md`
**Review File:** `.project/active/constraint-semantics-contract-amendments/spec-review.md`
**Date:** 2026-08-12

---

## Reality Check

**Sound.** The spec is about the right work item, its Problem section is materially accurate, and
its amendment list matches the actual contract text on every invariant number and current claim I
checked. Provenance discipline is the strongest part of the document: the two owner quotes
reproduce `rulings-20260812.md:16-21` exactly, the equality taxonomy is correctly demoted to
`[INFERRED]`, LC-G07 is correctly identified as owner-sourced and explicitly not re-graded, and the
D-2 vs D-4/SRC-01 conflict is parked in both directions without a single amendment touching either
statement.

What is wrong is concentrated in one place: **the spec is confident about facts on disk that it did
not check.** The ADR home decision contradicts a deliberate owner-authored consolidation commit; the
D1–D7 list is stated as the closed corrective set and a two-minute grep finds an eighth location of
the same defect; and one D-row's correction instruction, taken literally, would damage the totality
argument Item 2 depends on. All three are fixable in the spec text. Verdict is **Revise**, not
Rework.

---

## Audit

### Lens 1 — Faithfulness

**L1-1 · Direct claim (highest severity):** The ADR home decision rests on a stale premise. The spec
states as `[INFERRED]` "**Decision recorded here, revisable in design:** the ADR lands in this
repository at `docs/architecture/ADR-009-constraint-coverage-and-headline-semantics.md`," with the
rationale that "`docs/architecture/` is the path CLAUDE.md and code comments already imply for
codegen ADRs" (spec.md:113-119). That path pattern was **deliberately retired**. Commit `eda48f9`
("docs(D3/D5): Consolidate ADRs into modeling-assumptions.md", Reid Westwood, 2026-02-22) deleted
all eight ADR files from `docs/architecture/` and synthesized them into
`docs/architecture/modeling-assumptions.md`, under `.project/active/docs-consolidation/plan.md`.
`docs/architecture/` today contains exactly four entries and no ADR file. So:

- The rationale is inverted. The repo's recorded decision is that codegen ADRs are *not* standalone
  files at that path.
- ADR-009 would be the only ADR file in a repository where ADR-001 through ADR-008 are citation-only
  (25 live citations to ADR-003, 18 to ADR-001, all pointing at deleted files). The spec's own
  requirement — "A decision recorded where no reader will meet it is not filed" (spec.md:111-112) —
  argues against its own placement.
- The orchestrator verified that the ADR-with-a-file precedent lives in the **companion**
  (`docs/patterns/adr002-calculations.md`). The spec knows this file exists — it appears in Open
  Questions as a possible stub-cite location — but reasoned the home to codegen anyway.
- The product lens's spec-F1 disposition names `.project/scripts/adr.sh new` + `amend` as the filing
  route. That script does not exist in this repository. The spec silently substituted a hand-written
  file without recording that the named tool is absent.

Only the *number* survives: 008 is the highest consumed identifier, so 009 is free. Everything else
in that paragraph needs re-deriving, and "revisable in design" is not enough cover — design would
inherit a rationale that is false on its face.

**L1-2 · Direct claim:** The D1–D7 table is presented as the complete corrective set, and it is
incomplete for D7. The spec's D7 row names `docs/architecture/modeling-assumptions.md` and
`docs/architecture/reference/01-extraction.md`. The retired `test_constraint_migration_mapping.py`
(deleted in `82c7951`) is also cited as **living totality evidence** at
`docs/architecture/reference/28-constraint-lowering-and-catalog.md:100-101`: "The migration mapping
test (`test_constraint_migration_mapping.py`, D1/INV-A) proves every swept usage lands in exactly
one catalog outcome." That document is already a named D6 location in the same table, so this is not
a scoping choice — it is a miss, inherited from the research register and never re-checked. Two more
citations sit in code: `src/sysml_codegen/extraction/constraint_report.py:6` and
`tests/conformance/test_extractor.py:880` (see L3-1 for the code-boundary question).

The structural point matters more than the one row. The spec applied the "at minimum … design may
add, may not drop" clause to the *contract amendment* list but left the D-table closed. The D-table
is the list that just failed a grep.

**L1-3 · Direct claim:** D3's correction instruction, followed literally, breaks the totality
argument. The spec says: "Delete or rewrite '`require`/plain are executable constraint usages
(lowered under the profile)'". The orchestrator-verified source sentence is *"`assert`
(`AssertConstraintUsage`) and `require`/plain are executable constraint usages (lowered under the
profile)"* — and it is the **row-1 rationale for enumerating subtypes in the sweep**. That
enumeration is what REQ-EXT-09 rests on: `01-extraction.md:20` states the requirement over
"`ConstraintUsage` — **including** its `assert` … and `require`/plain subtypes", pins it with a
mutation check that "flips `include_subtypes=False` and confirms the assert is then MISSED from the
sweep", and cites that decision table as the per-call-site policy home. An agent that deletes the
clause, or rewrites it to "`require`/plain are not executable," removes the stated reason to
enumerate them — the exact direction that would let 56 usages vanish again.

The correction the contract actually wants is a *substitution of reason*: `require`/plain are
enumerated for **visibility and catalog totality**, not for executability; only the assert family
executes. The spec's row says what to remove and not what must survive. Given Item 2 builds its
totality gate on this enumeration, D3 needs its required correction stated positively.

**L1-4 · Direct claim:** Invariant 8 is listed as a statement of pre-amendment semantics, and it
isn't. The Problem section says "Invariants 1, 8/9, 28, 32, 33, 46/46a, 48 … state pre-amendment
semantics" (spec.md:26-28). Invariant 8 reads "Outcomes are exactly `ADMIT`, `BLOCK`,
`NON_NUMERICAL`, and `UNASSESSED`" — and the spec's own amendment text says the new severity is
"**not** a fifth profile outcome, and does not reclassify `ADMIT`." So invariant 8 is cited to say
what must *not* change; the amendment lands on 9 or on a new statement. Because the amendment list
now carries "may not drop one from this list," a design agent reading it as an amendment target will
either amend a correct invariant or spend the round-trip figuring out that it shouldn't. Say which
of the pair is the target and which is the guardrail.

**L1-5 · If-then tradeoff:** The same overstatement applies to two of the three Appendix C cells.
The spec requires amending "Excluded-only usages", "Zero constraint usages", and "Mixed
satisfied/violated/indeterminate population". Only the third clearly changes — its cell states the
old precedence verbatim. The other two:

- "Zero constraint usages | No constraint catalog/modules; bytes unchanged; … empty constraint
  evidence" is state 6 in the new vocabulary and reads correctly as written.
- "Excluded-only usages | Portable exclusions plus `not_assessed`" is still correct for a
  *plain-only* model (state 5) and wrong only for a model whose exclusions include an **asserted**
  usage (state 4, partial coverage).

**If** these two cells need only a disambiguating clause that splits by form, the spec should say so,
because "amend to the new headline and disposition semantics" plus a no-drop rule invites a rewrite
of text that is already true. **If** the intent is a fuller restatement, say what the cells must
newly assert. Same question for the Appendix B row, which the spec identifies precisely and
correctly (`:660`, "excluded-only usages retain `not_assessed` visibility") — note there is a
*second* Appendix B row on the neighboring claim ("excluded-only usages retain catalog/report
visibility") that stays true and should be left alone; naming that explicitly would prevent a
collateral edit.

**Checked clean, for the record.** Every invariant number and current claim in the amendment list
matches the contract text: invariant 1's "Any `BLOCK` halts the model"; 28's one-visible-disposition;
32's zero-input aggregator; 33's exact precedence; 46/46a including the `KeyError` clause; 48's
sole-catalog-schema-authority. Every companion requirement checks out too: LC-E11 quotes verbatim
("else any assessed result → `all_satisfied`"), LC-E12's "zero eligible entries … `not_assessed`
report surface" is correctly narrowed to *asserted* usages in the amendment, and LC-G07 is genuinely
`[NEED]` with an owner quote ("100% Option A. We need to purge this mess.") — the spec's
don't-re-grade instruction is exactly right. The `(amended YYYY-MM-DD, ITEM)` convention claim holds:
invariants 19, 20, 22, and 26 all carry it. D1, D2, and D6 reproduce at their named codegen
locations. `scripts/check_doc_distinctness.py` exists. The two owner-grade quotes are verbatim.

### Lens 2 — Problem & Approach

**L2-1 · Question to the user:** Is 1.5 days real for this? The epic budgets spec 1h / design 2h /
plan 1h / execute-and-review 8h. What the item actually has to produce: one ADR, eleven contract
amendments (eight invariants plus Appendix B and C cells plus the warning tier), six companion
requirement amendments, seven documentation corrections across two repositories, a six-state
vocabulary published in two dialects with a precedence order, the blessed gate shape with three
scope carve-outs, and a four-class equality taxonomy published in two places with grades preserved
through every hop. Each amendment has to be drafted so it states settled semantics rather than
current behavior, and half of them land in a repository this worktree cannot read. I'd expect the
execute phase alone to exceed 8h. This isn't a spec defect — the estimate is the epic's — but the
sequencing bet ("Items 2–5 build against what it publishes") means an over-tight Item 1 pushes
underspecified text downstream into code. Worth re-checking before the design stage commits.

**L2-2 · Question to the user:** Two "filed as a future capability" obligations have no filing home
and no deliverable. The spec publishes that "in-predicate chain admission is a filed future
capability candidate, not a closed door," and the umbrella carries the parallel commitment for the
plain-constraint advisory tier. "Filed" names an artifact — a backlog entry, a candidate list — and
this item's Deliverables (in the epic) list only the ADR, the amended contract/companion, the
codegen references, and the agentic-mbse guidance. Should Item 1 create those filings, or is
"recorded in the contract's prose" the whole obligation? Either answer is fine; the spec currently
implies the stronger one and provisions the weaker one.

### Lens 3 — Pipeline Risk

**L3-1 · Question to the user:** The D7 correction crosses the item's own "no code" line, and the
non-goal boundary is drawn by file rather than by requirement. Two collisions:

1. The retired-test citation also lives in a source docstring
   (`extraction/constraint_report.py:6`) and a test docstring (`test_extractor.py:880`). The spec's
   header says "no code" (Complexity, spec.md:6). Does Item 1 correct those, or do they ride with
   Item 2's totality work? A reader who greps the retired test name after Item 1 lands will still
   find it if the answer is "docs only."
2. The non-goal reads "Re-grading or re-anchoring REQ-EXT-09 and REQ-CL-04 **in
   `docs/architecture/verification-matrix.md`** — Item 2." But D7's correction edits
   `01-extraction.md:20`, where the retired test is REQ-EXT-09's **verification-evidence cell**.
   Removing it there is a re-anchor of the same requirement's proof, in a different file. Worth
   noting that the matrix row itself has already moved on — `verification-matrix.md:336` cites
   `test_extractor.py` and `test_exact_route_constraint_portability.py`, not the retired test — so
   the two files currently disagree with each other. Does Item 1 fix `01-extraction.md`'s evidence
   cell, or is the whole REQ-EXT-09 evidence surface Item 2's?

**L3-2 · Direct claim:** The success criterion "No statement remains in either repository that a
plain or requirement-side constraint is an enforced gate" is not checkable as written, and L1-2 is
the proof. The criterion is universally quantified over two repositories; the only enumerated work
is the closed D1–D7 table; and the only named mechanical gate is
`scripts/check_doc_distinctness.py`, which compares byte-identity between numbered reference
documents (`scripts/check_doc_distinctness.py:9-13`) and would never see a wrong sentence. Nothing
in the item verifies the universal claim. It needs one of: a named sweep (search terms plus the
directories covered, run in both repositories, with its output recorded in `verification.md`), or a
scope reduction to "D1–D7 plus whatever the sweep finds," with the sweep as the deliverable. A grep
for `test_constraint_migration_mapping` took under a minute and found the eighth location — a
recorded sweep is cheap and it is the only thing that makes this criterion mean anything.

**L3-3 · Rewrite request:** The invariant 46/46a amendment risks pulling Item 3's schema decisions
into Item 1's text. The amendment must make "the persisted-exact-report contract admit the report's
new compact coverage accounting" while the boundary section reserves "report schema field names and
shapes" to Item 3. Those are compatible only if the amendment is written field-name-free. The spec
states the token-spelling half of this rule explicitly ("No amendment in this item names a token
spelling as normative") but not the field-name half. Extend that sentence to cover report field
names, so the design agent has the rule in the same place as the obligation.

**L3-4 · Rewrite request:** The citation key doesn't cover one of its own citations. The key defines
`(Qn)`, `(Ln-n)`, `(lens spec-Fn)`, and `(Dn)`, and says `(Ln-n)` cites `rulings-20260812.md`. The
two-vocabulary `[HARD]` requirement is cited "(existing interface, spec-review L1-1)" — which is the
*umbrella's* `spec-review.md`, a document not in the key, using an ID form that collides with the
rulings key (the rulings record has no L1-1). One line in the key, or a path in the citation.

### Lens 4 — Hygiene

None material.

### Lens 5 — Reader Comprehension

**L5-1 · Rewrite request:** There is no single place that says what will exist when this item is
done. The deliverables are spread across six sections — an ADR (Known Requirements), amended
contract invariants (one section), amended companion requirements (another), corrected D1–D7 (a
table), a published vocabulary (a fourth section), and an equality instruction whose *home is an
open question*. A reader deciding whether to approve this has to assemble the artifact list
themselves, and the assembled list has a hole in it (which file hosts the equality instruction is
deferred). A short "what publishes where" list near the top — artifact, repository, and whether its
location is decided or deferred — would let the human check the shape in one pass. This is the
comprehension cost, not the prose, which is clear throughout.

---

## Engagement Summary

**Overall take:** The provenance work here is genuinely good — the grades survive every hop, the
owner quotes are verbatim, LC-G07's owner grade is protected, and the parked D-2/D-4 conflict is
untouched in both directions. The problem is that the spec is most confident exactly where it
checked least: three of its concrete, on-disk claims are wrong or incomplete, and one of them
(the D3 correction) would push a downstream agent toward an edit that undermines Item 2. Fix those
in the spec text and this is a strong contract for design.

**Here's what I need you to weigh in on:**

1. **[L1-1]** The ADR home is wrong on its stated rationale. You deleted all eight ADR files in
   `eda48f9` and consolidated them into `modeling-assumptions.md`; the spec cites that same
   directory as the implied precedent. Where should ADR-009 live — a new section in
   `modeling-assumptions.md` (matching your consolidation), a revived standalone file (reversing
   it), or the companion, where `docs/patterns/adr002-calculations.md` is the only ADR-with-a-file
   left standing? Also: the lens names `.project/scripts/adr.sh` as the filing tool and it doesn't
   exist here.
2. **[L1-3]** D3's row says "delete or rewrite" a sentence that is the stated reason the sweep
   enumerates `require`/plain subtypes — the enumeration REQ-EXT-09 and Item 2's totality gate both
   depend on. Confirm the correction is a *substitution of reason* (enumerated for visibility, not
   executability) and have the spec say that positively.
3. **[L1-2, L3-2]** The D1–D7 table is closed and already incomplete: `reference/28-*.md:100-101`
   cites the retired totality test as living evidence, and two code docstrings do too. Apply the
   same "at minimum … may not drop" clause the contract list got, and name the sweep that makes the
   "no remaining statement in either repository" criterion checkable.
4. **[L3-1]** Two boundary calls, both cheap to make now and expensive to discover in design: does
   this item touch the two code docstrings carrying the dead-evidence citation, and does D7's edit
   to REQ-EXT-09's evidence cell in `01-extraction.md` belong to Item 1 or to Item 2's re-anchor?
5. **[L1-4, L1-5]** Invariant 8 and two of the three Appendix C cells are listed as amendment
   targets but read correctly today. Under a no-drop rule, that pushes design to amend correct text.
   Mark which entries are guardrails ("must not change") versus targets, and for the two cells say
   whether a form-splitting clause is the whole ask.
6. **[L2-1]** Is 1.5 days honest for one ADR, seventeen amendments, seven cross-repository doc
   corrections, and two published policies? An over-tight Item 1 ships thin text into four
   downstream items.

---

## Resolutions

*To be filled in as findings are resolved. One entry per finding, keyed by ID — this is what the
spec agent reads to incorporate the review.*

---

**Verdict:** Revise
**Next Steps:** Record resolutions above, then re-run `/_my_spec` (or return to the spec-agent
session) pointed at this review to incorporate. The reviewer does not edit the spec. L1-1, L1-2,
and L1-3 are spec-text fixes and should land before design starts; L3-1 and L1-5 are boundary calls
that design will otherwise have to guess.
