# Design Review: Constraint Contract and Authoring Policy (CONSTRAINT-SEMANTICS Item 1)

**Design:** `.project/active/constraint-semantics-contract-amendments/design.md`
**Spec:** `.project/active/constraint-semantics-contract-amendments/spec.md` (+ `spec-review.md` §Resolutions)
**Review File:** `.project/active/constraint-semantics-contract-amendments/design-review.md`
**Date:** 2026-08-12
**Reviewer scope note:** every codegen-side quote in the design was checked against the file on
disk at base commit `882161e`. Companion (agentic-mbse) facts were checked against the
orchestrator-verified block in `briefs/03-design.md:37-67`, not against the companion tree.
The item's product-lens ledger (`product-lens.md`) exists and was not re-run; this stage is
synchronous and spawns no subagents. The two structural smells were checked inline — neither fired
(see Fundamental Assessment).

---

## The Point

A constraint report headline is what a design study reads to decide whether a design point is
feasible. Two rules made that headline unreliable: a plain `constraint` was cataloged but never
executed, and the headline claimed satisfaction whenever *any* assessed result passed — so a model
could read fully satisfied while every gate the modeler wrote went unassessed.

The umbrella contract settled the fix: assert-only enforcement, a catalog that accounts for every
authored usage, and a headline that never claims full satisfaction while applicable gates went
unassessed. Nothing a modeler or an implementing agent reads says any of that yet — the ratified
lifecycle contract, its frozen requirements companion, and seven documentation statements all still
teach the superseded rule, and one of those statements actively steers a modeler into the form that
silently does nothing.

Item 1 is the documentation half of the owner's binding sequence **[OWNER, 2026-08-12]**: settle
semantics → fix documentation and the test model → then run tests. Two owner-originated payloads
ride on it: **[OWNER-VERBATIM, 2026-08-12]** *"we know that narrow bands of viability may make
design exploration really difficult. So I want to call out in our concept WHEN we really think
equalities SHOULD be used (instructions) in addition to the sysml-codegen support"*, and the
modeler-owned tolerance need. If Item 1 ships thin text, Items 2–5 write code against a contract
that still contradicts itself.

## Fundamental Assessment

**Sound.** This is the right piece of work and the approach is right.

The design's organizing claim — that every amendment in the item is one semantic move (*coverage
truth*) projected onto a different surface, so the definitions get exactly one home and everything
else points there — is the correct shape for a multi-document amendment item. It is what makes the
seventeen-odd edits auditable instead of seventeen independent judgment calls.

Three things it got right that a weaker design would have missed:

- It read the repositories' *own* amendment conventions and follows each rather than imposing one
  (DD4), which is what keeps a frozen document's edits legible as native.
- It refused to soften a correction into an annotation, and it named the designated home for the
  superseded claim (the decision record and Appendix B) so capture-fidelity law 3 is actually
  satisfiable rather than nominally cited.
- It explicitly declined to build cross-document consistency tooling (Non-Goals), which is the
  plausible-sounding addition this item did not need.

Neither structural smell fired. Invariant 46a's fail-closed extension puts an obligation on the
consumer, but a fail-closed seam at a vocabulary boundary is the producer's contract stated at the
place it is enforced, not a consumer patching a producer gap. Invariant 48's amendment does move
ownership — the catalog becomes the sole authority for coverage truth — and it says so explicitly
in the amended text and mirrors it into LC-G07, so it is not a silent transfer.

**Verdict is Revise, not Rework.** The findings below are gaps and inconsistencies inside a correct
frame, and every one is fixable without changing the design's shape. Two of them (M1, M2) touch
provenance discipline the spec grades `[HARD]`, so they need to close before the plan.

---

## Dimensional Review

### 1. Spec Compliance
**Assessment:** Concerns

The amendment set is complete against the spec's floor. Every contract entry is present —
invariants 1, 9, 28, 32, 33, 46/46a, 48, the warning tier, the three Appendix C cells with their
distinct asks, the Appendix B row plus its named guardrail — and invariant 8 and the two guardrail
cells are discharged as verified-already-correct rather than skipped, which is exactly what the
no-drop rule asks. The companion set covers LC-E05/E06/E10/E11/E12 and LC-G07, and the design
answers the spec's open "if design concludes the clause needs no companion mirror" question with a
reasoned yes-it-needs-one (Appendix B, closing note). D1–D7, D7-code, the matrix pointer, the two
backlog filings, the ADR, and the cite-back are all placed.

**Semantic accuracy of the amended text — checked statement by statement, meaning only:**

- Invariant 33 precedence (A6) states the spec's five-state order verbatim in meaning, and adds the
  coverage-claim gloss the spec requires. **Correct.**
- The applicable-asserted-gate definition (A0) matches the spec's published rule clause for clause,
  including "a vacuous gate … is still applicable" and "stops being applicable only when it carries
  an explicit inapplicability disposition." **Correct.**
- Invariant 32's restatement (A5) moves the trigger to "no applicable asserted gate," and the
  implementer note correctly flags that the trigger genuinely changes. **Correct.**
- Invariant 46a's fail-closed extension (A7) covers unknown *and* unmapped headlines, names the
  error, and rules out both the `KeyError` and the satisfied/unconstrained fallthrough. **Correct.**
- Invariant 61 (A0) states the warning grade, the disposition kind, the advisory, and the
  counts-as-missing-until-explicit-inapplicability rule. **Correct.**
- Invariants 1, 9, 28, 48 each match their spec entry. **Correct.**

**RI-3 (no token spellings) holds in the drafted text.** State names appear as meanings
("Full satisfaction", "Partial coverage"), and every backticked token (`not_assessed`,
`all_satisfied`) appears only inside a quotation of pre-amendment text — A10's amended Appendix C
cells correctly drop the backticks the current cells carry. No report field name is named
anywhere; A7's "compact coverage accounting" is the obligation without the shape.

**Where compliance is short:** RI-1's second half is undischarged (M4), the sweep's terms do not
cover the item's own corrected vocabulary (M5), and the owner-verbatim equality payload is
satisfied on the concept side but not on the agentic-mbse side (M6). Details below.

**Capture-fidelity carry:** the design correctly keeps the R-POL-4 taxonomy agent-grade with the
*need* owner-grade (A11), and correctly refuses to mark ratified rulings settled. It carries the
owner-verbatim quote into A11 as a paraphrased `[NEED]` rather than quoting it — acceptable, since
the quote itself lives in the spec's Problem and the design's The Point, and A11 preserves the
owner's stated reason ("narrow bands of viability make design exploration really difficult").

### 2. Pattern Consistency
**Assessment:** Pass

DD4 is the right call and it is grounded in a read of both files rather than a preference. The
contract's `(amended YYYY-MM-DD, EPIC Item N)` head-of-statement convention is real — invariants
19 (`:172`), 20 (`:177`), 22 (`:186`), 26 (`:198`) all carry it, verified. The ADR precedent is
also real: `eda48f9` consolidated eight standalone ADR files into `modeling-assumptions.md`, and
DD1's refusal to revive a standalone file follows the repository's own recorded decision. The
detail that DD1 puts the literal string `ADR-009` in the heading so the identifier greps to one
anchor is a genuine improvement on ADR-001..008, which today grep to citations and no home.

The one convention claim that does not survive verification is the companion's — see M1.

### 3. Abstraction Quality
**Assessment:** Concerns

The single-definitions-home decision is the design's main abstraction and it is the right one. The
concern is that the design overstates how well it holds: "Every other amendment states its local
rule and points there" (Core Concept) is not what Appendices A–C actually do. See M7.

Invariant 61 as a *new* invariant rather than a clause on an existing one is the right call, and
the design was right to self-flag it. Invariant 28 supplies the disposition kind and carries no
severity vocabulary; bolting a warning tier onto it would have made 28 do two jobs. The contract
already grew by 54–60 under a prior epic, so a new number is a native move here, not an escalation.
But a new invariant in a ratified contract needs more than a free number — see M3.

### 4. Duplication Avoidance
**Assessment:** Concerns

The five-state precedence is written out in full in at least five places after this item: A0's
definitions subsection, A6 (invariant 33), A10 (Appendix C's mixed-population cell), B4 (LC-E11),
and C1 (ADR-009's "What it says now"). Each duplication is individually defensible — a matrix cell
must state its observation, a frozen companion must carry its own requirement, an ADR must record
what changed — but the design claims a single home it does not have, and it explicitly builds no
consistency check. See M7.

### 5. Data Structure Clarity
**Assessment:** Pass

Not a data-structure item. The nearest analogue — the six-state vocabulary and its two dialects —
is stated as an enumerated list with a precedence order and an explicit counterpart obligation
across the normalization seam, which is the right level of precision for a meaning-only item. The
Component Overview table (C1–C11) maps every deliverable to a file and a responsibility with no
gaps I could find against Appendices A–D.

One imprecision: A0's applicability test says "its source form is in the assert family and that
form is in executable scope." Read as a form-level test this is consistent with A9's claim that an
excluded asserted usage reads partial coverage. Read as a predicate-level test it contradicts it,
because a `BLOCK`ed or `NON_NUMERICAL` asserted usage would drop out of the denominator and the
model would read not-assessed instead. The form-level reading is clearly intended; the sentence
should say so. (Minor n8.)

### 6. Route Safety
**Assessment:** Pass

The relevant analogue is fail-closed behavior, and A7's 46a amendment closes the fallthrough
explicitly in both directions (never a `KeyError`, never a satisfied-or-unconstrained default).
RI-5's parked-conflict guard was verified against the actual target list: contract D-2 lives at
`:417-425` and D-4/SRC-01 at `:464-471`; A11's new subsection inserts between D-3's close (`:433`)
and the source-identity heading (`:435`), so it is an insertion above D-4 and below D-2 that edits
neither. Appendix B's amended row is `:660`, not the D-2 supersession row at `:646`. Appendix C's
D-2 cell (`:694`) is untouched. **The parked conflict stays parked.** Confirmed.

### 7. Bets & Decisions Integrity
**Assessment:** Concerns

B1, B2, and B4 are genuine bets with honest if-false consequences. B1 in particular resists the
temptation to claim the sweep is exhaustive and instead bets on the defect family's shape while
mitigating with a recorded raw hit list — that is the right posture.

**B3 is a bet whose supporting evidence does not survive checking (M1), and it is load-bearing.**

**Hidden bet, surfaced:** the design bets that the target-semantics statements it writes into
`modeling-assumptions.md` §8 and `reference/28-…md` are *already true of today's code*, and so need
no pending marker. That bet is never stated, never checked, and RI-1 explicitly requires the
opposite handling if it is false. See M4.

The eight decisions each name a rejected alternative with a reason, and the reasons are specific
rather than ceremonial — DD3's rejection of the design-space-studies concept cites the file's actual
`Status: Proposed` (`:3`) and its own governance banner (`:9`), both verified. DD7 is the kind of
call a weaker design gets wrong: it keeps live evidence in place rather than emptying a cell to
dramatize a gap.

### 8. Reader Comprehension
**Assessment:** Pass

The Core Concept gives the reader one sentence to hang everything on ("One decision, one authority,
cited from everywhere it binds") and then names the one semantic move before any mechanism. The
Architecture block's dependency arrows plus the explicit write order ("the definitions subsection is
written first: every other amendment cites it… ADR-009 second, because it must quote the
pre-amendment text while that text is still on disk") is the kind of ordering rationale an
implementer would otherwise have to rediscover.

Appendices A–D are dense, but that density is the deliverable — they are target text, not
explanation. No finding.

---

## Issues by Severity

### Critical

None. No finding blocks the design's approach.

### Major

**M1. The companion amendment convention (DD4/B3) rests on a precedent that does not say what the
design says it says — and it is the wrong requirement ID.**
*Targets:* Key Bets B3; Research Findings "Companion structure"; Appendix B preamble.

The design cites "LC-E04 (`:272-274`)" as the precedent that "rewrote the meaning of a term in place
and recorded the amendment in a trailing sentence." Two problems, both verified:

1. **Wrong ID.** `:272-274` is the amendment sentence on **LC-E04B** (`:269-274`). LC-E04 is a
   different, owner-sourced requirement at `:263-268`.
2. **The precedent is a pure append, not an in-place rewrite.** Comparing the live LC-E04B
   (`:269-271`) against the archived close-state copy
   (`.project/completed/20260720_constraint-execution-lifecycle-contract/spec.md:253-255`), the
   requirement body is **byte-identical**. The 2026-08-05 amendment added a trailing sentence and
   changed nothing above it.

This matters because B3 is the bet that licenses B4's *full rewrite* of LC-E11's precedence and
B5's rewrite of LC-E12's final sentence. The only verified companion precedent supports appending.
The design's own if-false clause says that in this case "the item needs an owner ruling before it
can proceed."

*Suggested resolution:* the header's "forward requirement amendments happen here only" (`:3-7`) is
the actual licensing text and it is stronger than the LC-E04B precedent — re-ground DD4 on the
header rather than on a precedent that does not carry the weight. Then either (a) keep the in-place
rewrites and state plainly that this item establishes the rewrite convention the header licenses,
or (b) surface it to the owner per capture-fidelity law 4. Do not leave B3 asserting a precedent
that is not there.

**M2. B1–B5's drafted amendment texts carry no grade on their new content, contradicting the
design's own RI-2 and the spec's `[HARD]` provenance rule.**
*Targets:* RI-2; Appendix B, B1–B5 (contrast B6).

RI-2 says "the amendment's own new content carries `[AGENT] (ratified by owner, 2026-08-12)` and
says so where a grade is visible." B6 (LC-G07) does exactly that. B1–B5 do not — they attach a
bare `Amended 2026-08-12 (CONSTRAINT-SEMANTICS Item 1): …` sentence with no grade.

The sharpest case is B4. LC-E11 is `[INHERITED]` with "Source: original concept and generation
spec." B4 replaces the requirement body wholesale with the new coverage-truthful precedence while
keeping the `[INHERITED]` marker and the source line. The result is agent-ratified new content
wearing an inherited grade sourced to a document that says the opposite. B5 has the same shape.

This is the spec's `[HARD]` law-1 item, and the review brief asked specifically that the drafted
texts be checked rather than the preamble. The preamble is right; the drafts do not implement it.

*Suggested resolution:* give every amendment sentence in B1–B5 the B6 treatment —
`Amended 2026-08-12 (CONSTRAINT-SEMANTICS Item 1), [AGENT] (ratified by owner, 2026-08-12): …`.
For B4 and B5, where the body is rewritten rather than extended, also state in the amendment
sentence what the inherited source now covers, so a reader does not read the new precedence as
inherited from the original concept.

**M3. New invariant 61 gets no companion mirror and no Appendix C acceptance cell, while every
other invariant amendment gets a mirror.**
*Targets:* Appendix A, A0 (invariant 61); Appendix B (B1–B6); Potential Risks, the self-flagged
invariant-61 risk.

The design's own reasoning against a one-sided clause is stated at Appendix B's closing note on
LC-G07: "leaving only one of them carrying the coverage-truth clause is exactly the disagreement
the spec asked to prevent." That reasoning applies to invariant 61 and is not applied to it.
Invariants 28, 32, 33, and 48 each get a companion mirror; 61 gets none, so the frozen requirements
document — which Items 2 and 3 read — has no requirement for the warning tier at all.

Separately, the contract's Appendix C is titled "Mandatory acceptance matrix," and invariant 61
introduces a new observable behavior (a warning-grade disposition plus an authoring-time advisory,
and the partial-coverage consequence). It gets no acceptance row. The spec's Appendix C list names
three cells, but that list is a floor under the same "design may add, may not drop" rule the design
invoked to add C4/D2b.

The numbering-collision question the brief raised is real but smaller: 61 is verifiably free
(invariant 60 at `:376` is the highest live number), and the contract keeps no next-free register,
so a concurrent epic could collide. Worth one line in the definitions subsection recording that 61
was minted by this item on 2026-08-12; not worth a mechanism.

*Suggested resolution:* add a companion requirement for the warning tier (LC-E13, or an addition to
LC-E05 which already carries the disposition kinds), and add one Appendix C cell — "Asserted
vacuous gate" → required observation covering the warning-grade disposition, the advisory, and the
partial-coverage headline. Record the 61-minting date.

**M4. RI-1's "names the item that makes it true" is undischarged for C2, C3, and C5, and the
design never records whether those statements describe today's code.**
*Targets:* RI-1; Appendix C, C2 (D1), C3 (D2), C5 (D6).

RI-1 says: "Where current code differs, the text says what must be true and names the item that
makes it true." C6a/C6b/C6c and C8 do this correctly — each names CONSTRAINT-SEMANTICS Item 2 and
marks the evidence pending. C2, C3, and C5 name no item and carry no pending marker.

That is correct **if and only if** those statements are true of today's behavior. The design never
says. C3's replacement asserts that "every usage outside the assert family is cataloged and never
executed," naming `assume constraint` explicitly; C5's replacement asserts that unassessed status
follows source form under *any* owner kind. Both land in documents a modeler reads as descriptions
of what the pipeline does. If either is a target rather than a current-state claim, the item ships
a modeler doc asserting behavior that does not exist, with nothing marking it pending — which is
the exact defect class D7 exists to correct, inverted.

*Suggested resolution:* for each of C2, C3, C5, record in the design (and then in
`verification.md`) one of two dispositions: "verified true of current behavior at `<commit>`, with
the evidence," or "target statement — Item N makes it true," with the item named in the published
text per RI-1. This is a small addition and it closes the design's one hidden bet.

**M5. The sweep's three terms do not cover the item's own corrected vocabulary — no term finds the
superseded headline precedence, and none finds `assume`/`satisfy` taught as a check.**
*Targets:* Appendix D, terms S1–S3; DD5; success criterion "no statement remains."

Two gaps, both inside the class the item is closing:

- **No precedence term.** The item's central semantic move is the headline precedence, and the
  design amends five places that state it. Nothing in S1–S3 would find a *sixth* — a living
  `docs/`, `src/`, or `tests/` statement of "all satisfied", `all_satisfied`, or "else any assessed
  result". Given that the report code and its tests exist today under the old vocabulary, living
  surfaces almost certainly carry the superseded precedence in prose.
- **No `assume`/`satisfy` term.** S2 greps the literal string `require constraint`. The design's own
  corrected text (C2, C3) widens the never-executes set to include `assume constraint` and
  `satisfy` — so guidance teaching `assume constraint` as an enforcement form is inside the defect
  class and outside the sweep.

S3's regex is also narrow in a way worth noting: it will not match "constraints are evaluated",
"the constraint is verified", or "the constraint blocks generation."

The `.project/` exclusion (DD5) is **defensible and I would keep it.** Dated records under
`research/`, `completed/`, and `active/` are provenance under the contract's own reading rule
(`:19-21`), and rewriting them falsifies the audit trail. Keeping `.project/concepts/` and
`.project/backlog/` in scope is the right line, since those are living authorities. The design
already writes the exclusion and its reason into `verification.md`, which is what makes it auditable
rather than silent.

*Suggested resolution:* add S4 (`grep -rniE "all[_ ]satisfied|else any assessed"`) and S5
(`grep -rn "assume constraint\|satisfy requirement"`) to Appendix D, with the same
disposition-per-hit rule. Widen S3's verb alternation. The "adding a term is allowed, dropping one
is not" rule already in Appendix D covers this cleanly.

**M6. The agentic-mbse equality rendering cites the authority instead of instructing the modeler,
and it points across repositories into a `.project/` directory.**
*Targets:* Appendix C, C9's "Equality-instruction cite (DD2/DD3)"; DD3.

DD3's choice of home is right: the lifecycle contract sits in `.project/concepts/`, so the owner's
"call out in our concept" is satisfied literally, and the rejection of the `Status: Proposed`
design-space-studies concept is correct and well-evidenced (verified: `Status: Proposed` at `:3`,
governance banner at `:9`).

The problem is the other half of the owner's sentence — "**in addition to** the sysml-codegen
support." The companion rendering is three sentences: a question, a pointer to a file in another
repository's `.project/concepts/`, and the tolerance statement. A modeler reading
`docs/patterns/constraints.md` gets told the guidance exists somewhere else. The four intent
classes — which are the actual instruction, and which are what the owner asked to be called out —
never reach the surface a modeler reads.

The cross-repository reachability compounds it. `.project/` is working-artifact space, not published
documentation; a companion reader may not have the codegen checkout at all.

*Suggested resolution:* render the four classes in the companion as a short table (class → the
authoring move, one line each), with the contract cited as the authority for the reasoning and the
`[AGENT] (ratified by owner, 2026-08-12)` grade carried. That is not a second authority — the
rationale, the owner's reason, and the challenge instruction stay in the contract — it is the
instruction actually landing where the instructed reader is. The same reachability point applies to
C2's blessed-gate paragraph, which also sends a modeler from `docs/architecture/` into
`.project/concepts/`.

**M7. The single-definitions-home claim is stated more strongly than the appendices deliver, and
the design builds no check.**
*Targets:* Core Concept ("Every other amendment states its local rule and points there"); Validation
Approach item 1; Non-Goals ("no new consistency tooling").

Of the five places that will state the five-state precedence after this item, two point at the
definitions subsection (A6 does, by name; A0 is the home) and three restate it in full without
pointing (A10's Appendix C cell, B4's LC-E11, C1's ADR-009). The same is true of the disposition
kinds: A4 and B1 both spell out all three.

Most of that is unavoidable and correct — a matrix cell must state its observation, a frozen
companion must carry its own requirement text, a decision record must record what changed. The
finding is not "remove the duplication." It is that the design's stated invariant is false as
written, and the honest version changes what the audit must do: with five copies and no checker,
the audit has to compare them pairwise against the definitions subsection, and Validation Approach
item 1 ("each amendment's post-edit text matches the target text here") does not ask for that.

Declining to build consistency tooling remains right — a checker for this would be a bad trade.

*Suggested resolution:* restate the Core Concept claim accurately ("the definitions have one home;
where an amendment must restate them for its own document's structure, it restates them verbatim
and cites the home"), and add one audit step: the five precedence statements and the three
disposition-kind statements are compared against A0 and must agree in meaning and order.

### Minor

- **n1. Invariant 28's line cite is off.** A4 gives `:216-219`; invariant 28 begins at `:213`. The
  quoted first sentence spans `:213-215`. The quote itself is exact.
- **n2. `01-extraction.md:20` clause count.** Research Findings says the evidence cell "has three
  clauses"; DD7 says it "keeps its two live clauses." The cell has four: the retired-test clause,
  the `wi014_toy` landing, the `include_subtypes=False` mutation check, and a pointer to the
  subtype-enumeration decision table. C6c's replacement scope (first clause only) is correct, so
  this is a description error, not an edit error — but fix it so the implementer does not delete a
  clause looking for the count to match.
- **n3. `constraint_report.py:9` keeps "the catalog is now the *proven* single source of truth"
  after C7a.** C7b strips exactly that word from the parallel phrase in `test_extractor.py`, and the
  proof it refers to is the retired test. Same correction, same file, missed site.
- **n4. `test_extractor.py:881-882` keeps "still load-bearing for the mapping test" after C7b.**
  C7a handles the equivalent dangling references in `constraint_report.py` (`:11`, `:16`) and C7b
  does not handle this one. The S1 grep will not catch it — it names the test by description, not
  by filename.
- **n5. RI-4 and RI-5 guardrails are pinned by line number in files this item edits above those
  lines.** A0 and A11 both insert text upstream of the Appendix B/C rows and D-4. Anchor the
  guardrail checks on quoted text, not `:648` / `:464-471`.
- **n6. The ADR-009 companion cite lands in `docs/subtype-enumeration-decision-table.md`.** A
  coverage-and-headline decision cited from a subtype-enumeration table is an odd meeting place;
  `docs/patterns/constraints.md` — which already receives the equality cite and carries the correct
  four-outcome story at `:25-41` — is where a reader of constraint semantics actually is. DD2's
  "the cite rides the D4/D5 corrections that already touch those files" applies to either file.
- **n7. B5 cites the wrong governing invariant.** LC-E12's amendment says "See contract invariant 33
  (amended)"; the zero-eligible-entries / aggregator trigger is invariant 32's. Cite both, or 32.
- **n8. A0's "that form is in executable scope" is ambiguous** between a form-level and a
  predicate-level test, and A9's excluded-asserted-usage → partial-coverage claim only holds under
  the form-level reading. One clarifying clause fixes it.
- **n9. `verification.md`'s format is specified for the sweep table only.** Appendix D gives an
  exact per-hit table with example rows — good. The RI-7 discharge record, the C4/D2b addition note,
  the D5-e branch record, and the mechanical-check results are described in prose with no shape. One
  more table stub (entry | disposition | verification note) would make the discharge check
  mechanical instead of interpretive.

---

## Recommendations

1. **Close M2 and M1 first — they are the `[HARD]` provenance items.** Give B1–B5's amendment
   sentences the B6 grade treatment, and re-ground DD4 on the companion header's
   "forward requirement amendments happen here only" rather than on the LC-E04B precedent, which
   verifies as an append and not an in-place rewrite.
2. **Give invariant 61 the same treatment every other invariant amendment gets (M3):** a companion
   mirror and an Appendix C acceptance cell. Record that 61 was minted 2026-08-12 by this item.
3. **Discharge RI-1 for C2/C3/C5 (M4)** — for each, either record the current-behavior verification
   or name the item that makes it true, in the published text.
4. **Add S4/S5 to the sweep and widen S3 (M5).** The superseded precedence and the
   `assume`/`satisfy` forms are inside the item's own corrected vocabulary and outside its search.
5. **Render the four equality-intent classes in the companion, not just a pointer (M6).** The owner
   asked for the instruction in the concept *in addition to* the codegen support; a cross-repo
   pointer into `.project/` is the concept half twice.
6. **Say the single-home claim accurately and add the pairwise audit step (M7).**
7. **Sweep the minors in one pass** — n3 and n4 in particular are the same defect class this item
   exists to close, sitting in files it is already editing.

**Implementability, for the record:** with M1–M7 closed, an implementing agent could execute this
without re-deriving a decision. The target text is exact, the write order is stated with its reason,
the re-verify-before-editing step is mandatory per companion site, the D5-e ruling is a stated test
with a named default branch and a record of which branch fired, and DD1–DD8 leave no placement
open. The Next-Stage Handoff correctly scopes what remains to the plan (edit sequencing within a
file, commit split). That is a high bar and the design clears it.

---

## Resolutions

*(Stage 4 — filled in as the owner resolves each finding. Empty at write time.)*

---

**Overall:** Revise
**Next Steps:** Record resolutions above, then re-run `/_my_design` (or return to the design-agent
session) and point it at this review to incorporate. The reviewer does not edit the design.
