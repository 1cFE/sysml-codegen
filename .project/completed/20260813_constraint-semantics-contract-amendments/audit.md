# Audit: Constraint Contract and Authoring Policy (CONSTRAINT-SEMANTICS Item 1)

**Verdict:** Certify-with-residuals
**Audited:** 2026-08-12
**Branch:** `item7-rebuild`
**Commit:** `f490a22` (item range `4678cd5..HEAD`)
**Auditor scope:** codegen worktree only. `/home/reid/1cfe/agentic-mbse-item7-rebuild` is
unreadable from this sandbox (both `ls` and `Read` denied), so the companion half is audited
through `verification.md` and `design.md`, with live probes requested at the end.

---

## The Point

A study reads a constraint report headline to decide whether a design point is feasible. Today that
headline can say satisfied when nothing was checked: a plain `constraint` is cataloged and never
executed, and the old precedence claimed satisfaction whenever *any* assessed result passed. The
umbrella contract settled the fix — assert-only enforcement, catalog totality with severity by
cause, coverage-truthful headlines. Item 1 is the documentation half of the owner's required
sequence (settle → fix docs → then test): make every durable authority a modeler or an implementing
agent actually reads say the settled rule, before Items 2–5 write code against it. Nothing here
changes behavior. Getting it wrong means four downstream items build against text that contradicts
the contract they implement, and every modeler following current guidance keeps authoring
constraints that silently do nothing.

## Summary

The work landed and it is good. Every success criterion I could check from this worktree is met with
evidence: ADR-009 is filed and cited back into the umbrella lens trail, the amendment set is
complete with provenance grades preserved and superseded text quoted, the sweep reproduces exactly
as recorded, the five precedence copies agree, and the boundary discipline held — no TEAx edits, no
normative token spellings, the parked D-2/D-4 statements byte-untouched, Python diffs comment- and
docstring-only. I re-ran all five sweep terms independently and got the recorded post-edit result,
term for term.

Four residuals, none of them a wrong rule. The largest is that the contract's own equality-policy
subsection describes an arrangement that is not what shipped: it says the companion cites the
instruction and does not restate it, while the design's M6 resolution renders the whole taxonomy in
the companion. That is the authority document misdescribing its own governance, and it needs one
sentence. The rest are editorial or hand-off placement.

## Product Judgment

**Is this the right piece of work?** Yes, and it is the right *shape* of the work. The owner's
sequence ruling makes documentation-first the precondition for everything downstream, and this item
publishes exactly the things Items 2–5 need to key off: the applicable-asserted-gate membership test
(the term everything turns on, defined where it is first used), the inventory-versus-feasibility
split, the six states with a precedence, and the warning tier that sits between the halt and the
never-errors record. The hardest judgment in the item — that a headline which cannot distinguish
"checked and passed" from "not checked" is not evidence — is stated plainly in ADR-009 and carried
into every copy.

**Ledger gate: DISPOSED, not blocked.** The item's `product-lens.md` holds one spec-stage block
(gate DISPOSED, item1-F1..F6), and every finding has a recorded resolution: F1–F5 resolved in the
spec text, F6 deferred to design and then landed as the dated matrix pointer
(`verification-matrix.md:336`). The umbrella ledger's `spec-F1` INTENDED-CHANGE disposition now
resolves against a live document — `constraint-semantics-contract/product-lens.md:35` carries
`Filed: ADR-009 — docs/architecture/modeling-assumptions.md §9 (2026-08-12)`. The epic gate is
recorded CLEAR. No unresolved `BLOCK` anywhere in the chain.

**Structural smells checked, one fired.** "Two representations must be manually kept synchronized"
fires on the equality instruction, and it fires in a way the item's own text denies — see H-1. It is
escalated here rather than left in the rubric: the failure mode is a future editor amending the
contract copy and reading the contract's own sentence as an assurance that no second copy needs
touching. It is one sentence of repair, not a design problem, so it does not forbid certification —
but it is the finding to fix first. The other four smells did not fire: the amendment set is not a
special-category exemption, correctness does not depend on downstream knowledge of an internal
representation, no test is green by route selection (no tests were changed), and no baseline
preserves contradicted behavior.

**On the missing implementation-stage lens block.** The command's audit flow calls for spawning a
product-lens run and appending its verdict to the ledger. The stage brief makes this pass read-only
and forbids background agents, so no block was appended and none was spawned. The judgment above is
mine, derived against the repo's durable product statements (contract, companion, ADR-009,
`modeling-assumptions.md` §8/§9) rather than inherited from the spec's framing. Recorded as a
limit, not as a pass.

---

## Findings

Severity key: **H** = fix before close; **M** = fix or file; **L** = record.

### H-1 (High-of-the-set; Design conformance) — the contract denies a restatement that exists

`.project/concepts/constraint-execution-authoritative-lifecycle-contract.md:514-515`:

> "This is the authority copy; agentic-mbse's authoring guidance cites it and does not restate it."

That is not what shipped. Design-review finding **M6** ("the agentic-mbse equality rendering cites
the authority instead of instructing the modeler", `design-review.md:348`) was resolved by rendering
the four-class taxonomy in full in the companion — `design.md:1135-1164` specifies the whole table,
the why-it-matters line, the tolerance line, and the grade stamp, landing in agentic-mbse
`docs/patterns/constraints.md`. The companion copy itself says the right thing ("**This is not a
second authority** … If the two ever disagree, the contract governs"), so the precedence is sound.
The contract's sentence is the stale half: it was written for the pre-M6 pointer design and was not
revised when M6 landed.

Why it matters beyond tidiness: the sentence is the only place the contract tells a future editor
what maintenance obligation the arrangement carries. As written it says "none." The two copies must
in fact be kept in agreement, and the contract is where that obligation belongs.

**What should change:** replace the clause with one that states the actual arrangement — the
companion renders the instruction in full for the reader who is there, cites this as the authority,
and this copy governs on disagreement. Same sentence position; no grade change.

### M-1 (Spec conformance) — the four-assertion hand-off is not recorded where Item 3 meets it

The four `all_satisfied` assertions are correctly *not* corrected (RI-6; executable text; Item 3
owns the token): `tests/execution/test_fusion_tea_real_teax.py:245`,
`tests/execution/test_constraint_verdicts_exact_route.py:171,416,540`. I re-ran S4 and confirm all
four still stand and that nothing else in `tests/` was touched.

The hand-off is recorded in `verification.md:322` (Table 2) and `.project/CURRENT_WORK.md:38-41`.
Neither is where Item 3's implementer will meet it: `verification.md` archives to
`.project/completed/` at `/_my_close`, and `CURRENT_WORK.md` is rewritten every session. The durable
document Item 3 reads is
`.project/backlog/epic_constraint_semantics_contract.md:352-400`, and it names no test file or line.

The spec's own code-text boundary requirement asks only that such a case be "recorded in
`verification.md` and handed to the item that owns that code," so this is **spec-literal-compliant**
and graded M rather than H. Item 3's scope items 2–3 will break those assertions on contact, so the
residue is self-revealing. But "handed to the item" reads as a pointer the receiving item can find.

**What should change:** one line under Item 3's Scope in the epic file naming the four sites.

### M-2 (Code integrity, documentation) — LC-E05 states the same clause twice

`.project/concepts/constraint-execution-lifecycle-requirements.md:276-278` and `:284-287`. The
requirement body was rewritten in place to carry the three-kinds clause, *and* the appended
amendment note states the same clause again:

- `:276-278` — "A visible disposition is one of three kinds — eligible, excluded-with-reason, or
  non-reaching-with-reason — and the dispositions cover the complete authored-usage domain."
- `:284-287` — "a visible disposition is one of three kinds — eligible, excluded-with-reason, or
  non-reaching-with-reason — and the dispositions cover the complete authored-usage domain; 'reaches
  no instance' is a disposition, not an absence."

Every sibling amendment (LC-E06, LC-E10, LC-E11, LC-E12, LC-G07) has the correct shape: amended body,
then a note stating only what changed plus the superseded quote. LC-E05 is the one that duplicates.
It is also the one whose "Superseded:" line paraphrases rather than quotes ("the requirement named no
disposition kinds and left non-reaching usages uncovered") — defensible, since the supersession here
is an absence and there is no prior sentence to quote, but worth naming since the design requires a
quote.

**What should change:** cut the duplicated clause from the amendment note at `:284-287`, keeping
"reaches no instance is a disposition, not an absence" and the cross-reference.

### M-3 (Spec conformance) — the vendored-corpora hits are summarized, and the spec asked for the list

Spec success criterion: "The named search terms, the directories covered, and the raw hit list are
part of the record; a summary is not." `verification.md:114-121` aggregates 52 companion hits
(S2×15, S3×4, S5×27, S5×6) by directory with counts and file lists, rather than one row per line.

The reasoning is stated, the exclusion is flagged for an auditor, and it is right on the merits —
`docs/sysmlv2/` and `docs/syside/` are the OMG specification, the standard library, and generated
SysIDE API docs, which this item has no authority to amend and would corrupt by editing. The
disposition is correct; the *form* deviates from a criterion the spec wrote in the imperative. It is
recorded here so the deviation is a decision rather than a gap.

**What should change:** nothing in the tree, if the owner accepts the aggregation. If not, the file
lists are already there and expanding them to line rows is mechanical.

### L-1 (Plan completion) — a stale locator in the plan's validation record

`plan.md:260` records "`grep -rn "ADR-009" docs/` returns exactly one heading anchor
(`modeling-assumptions.md:496`)". The heading is now at `:531` — later phases inserted the §8 D1/D2
corrections above it. The claim's substance still holds (I ran the grep: exactly one heading anchor,
`docs/architecture/modeling-assumptions.md:531`); only the line number drifted. Same class at
`plan.md:246`. No action needed beyond knowing the plan's line cites are phase-time, not final.

---

## Findings by area

### Plan completion

All 91 checkboxes in `plan.md` are `[x]`; zero unchecked. Spot-verified rather than trusted:

- Phase 1 (A0 + ADR-009 + lens cite-back) — `modeling-assumptions.md:531` §9 exists;
  `constraint-semantics-contract/product-lens.md:35` carries the `Filed: ADR-009` line, and the
  full-file diff shows that is the **only** changed line in the umbrella lens (`+1/-0` in the
  diffstat), so the cite-back did not disturb the ledger.
- ADR-009's "What the contract said" block (`:544-546`) quotes invariant 33 and LC-E11
  byte-accurately against the pre-amendment text — checked against `git show 4678cd5:` for both
  files.
- Phase 4 Python-diff claim — verified independently below.

One residual: L-1.

### Spec conformance — success criteria, one by one

| Criterion | Verdict | Evidence |
|---|---|---|
| ADR records the change, agent-originated/owner-ratified, id cited in the lens trail | **Met** | `modeling-assumptions.md:531-568`; provenance line reads `[AGENT] (ratified by owner, 2026-08-12)` and adds "Ratification does not make it owner-originated, and it is challengeable by re-deriving against the reasoning below." Cite-back at `constraint-semantics-contract/product-lens.md:35` |
| Contract + companion publish the full amendment set, grades intact | **Met** | Contract: invariants 1, 9, 28, 32, 33, 46, 46a, 48 all carry `(amended 2026-08-12, CONSTRAINT-SEMANTICS Item 1)`; new 61 at `:476`; Appendix B row and both Appendix C target cells amended; new "Asserted vacuous gate" cell added. Companion: LC-E05/E06/E10/E11/E12 amended, LC-E13 added, LC-G07 amended with "The owner-sourced requirement above is unchanged." Grades: every `[INHERITED]` stays `[INHERITED]`; every amendment note carries `[AGENT] (ratified by owner, 2026-08-12)` |
| No statement anywhere says a plain/require constraint is an enforced gate; no live citation of the retired test | **Met** | S1 re-run: **zero hits** across `docs/ src/ tests/ scripts/ README.md CLAUDE.md .project/concepts/ .project/backlog/`. S3 re-run: 5 hits, each either this item's own corrected text (`modeling-assumptions.md:498` — "Use the assert family. It is the only enforcement opt-in") or epic/backlog prose stating the settled semantics or quoting the defect under correction |
| The universal claim is checked, not asserted; every hit dispositioned | **Met, with M-3** | Tables 1/1b in `verification.md` disposition every project-authored hit individually with a reason. I re-ran all five terms and reproduce the post-edit table exactly (S1 zero; S2 12; S3 5; S4 13; S5 4 in codegen). Vendored hits aggregated — M-3 |
| Equality guidance: when to derive / band-check / one-side / fix as input / close by construction, and modeler-chosen tolerances | **Met** | Contract `:511-539` (authority copy) + `modeling-assumptions.md:517-527` (modeler-facing rendering) + companion rendering per `design.md:1135-1164` (**probe P-2**) |
| Blessed gate shape published with its scope precision | **Met** | `modeling-assumptions.md:498-515`: the `constraint def` + `assert constraint … { in formal = <path>; }` example, then all three carve-outs named — predicate-body-only, binding-position feature chains supported, inline asserted forms admitted, in-predicate chains a filed candidate |
| Both vocabularies have a published meaning for every state incl. partial coverage, and the precedence; Item 1 owns meaning, Item 3 owns spellings | **Met** | Contract "Headline states and coverage truth" (`:431-475`): membership test, two-totals split, six states, precedence, and an explicit both-vocabularies paragraph making a one-sided state a defect. Boundary stated in the subsection head and again in ADR-009's Scope |
| Documentation is correct before confirmation testing; no amendment written to match current behavior | **Met** | Where the published text describes a target rather than today's code it says so and names the owning item, in the published text rather than only in the record: `modeling-assumptions.md:476-477`, `28-constraint-lowering-and-catalog.md:52-58`, `:110-112`. `verification.md:317-319` splits C2/C3/C5 into current-vs-target halves against `882161e` |
| `check_doc_distinctness.py`, companion doc checks, `git diff --check` pass in both repos | **Partial — probe** | `git diff --check 4678cd5..HEAD` → clean (run by me, no output). `check_doc_distinctness.py` needs approval in this sandbox — **probe P-1**. Companion side — **probe P-3** |

**Non-goals respected.** Nothing implemented. No token spelling or report field name published as
normative (RI-3 re-verified: the only headline tokens in the whole diff are inside ADR-009's "What
the contract said" block at `:544-546` and LC-E11's superseded quote at `:326`, both explicitly
framed as pre-amendment text being replaced; `ADMIT`/`BLOCK`/`NON_NUMERICAL`/`UNASSESSED` are
invariant 8's profile outcomes, not headline tokens). REQ-EXT-09/REQ-CL-04 not re-graded — the
matrix row keeps `PASS` and gains only the dated pointer (`verification-matrix.md:336`). No TEAx
path in the diff (`git diff --name-only 4678cd5..HEAD | grep -i teax` → empty).

### Design conformance

Follows the design. DD1 (ADR as a numbered section in `modeling-assumptions.md`, identifier literal
in the heading so it greps to one anchor) — confirmed, one anchor. DD3 (contract's supported-boundary
section as the equality authority) — confirmed at `:511`. The `(amended YYYY-MM-DD, …)` convention
sits at the head of each restated statement, matching invariants 19/20/22/26. The three design
additions (invariant 61 + Appendix C cell, LC-E13, D2b's "three outcomes" → four) each have a
recorded reason in Table 2 and each closes a real self-contradiction — D2b in particular was catching
`modeling-assumptions.md` calling the profile's four outcomes three, inside the same item that pins
invariant 8 as a guardrail.

Deviation: H-1, the contract sentence not revised when M6 changed the companion rendering.

**The D5-a deviation, judged (audit focus 4).** The implementer kept `require constraint` at
`sysml-expert.md:124` because it sits inside a `requirement def`, and added a settled-semantics
sentence instead of swapping the form. **The reasoning is right, and it is more right than the
design's instruction.** Umbrella Q7 rules that requirements-side forms stay **non-executable and
visible**. A `require constraint` nested in a `requirement def` is the SysML v2 idiom that makes a
constraint requirement-side at all; substituting `assert constraint` there would have (a) taught
invalid requirement modeling, and (b) deleted the visible requirement-side form that Q7 exists to
preserve, in an agent-guidance file. The published rule does not say "don't write `require
constraint`" — it says the form never executes and the assert family is the sole enforcement opt-in.
An example that keeps the form and states that rule *is* the rule, rendered. The D5 defect as
written in the register ("stop teaching `require constraint` as an equal alternative for a check")
does not describe this site: the section is headed "Example Pattern: Requirement with Constraint,"
which is requirement modeling, not check guidance. The deviation was recorded with its reasoning
before being taken (`verification.md:178-195`), which is the correct handling.

**One thing I could not verify:** the exact text of the added sentence, and that no surrounding
prose in that section still frames the example as a check. That is **probe P-2**. The judgment above
is on the reasoning and the design's stated intent; the wording needs the companion read.

**Capture-fidelity law 3 (audit focus 7) — clean.** I read every correction in the diff looking for
the accretion pattern (suggestion → rejection → "WE MUST NOT ⟨suggestion⟩"). None of them does it.
The D1 correction states the rule positively and enumerates the never-executing forms as a
classification, not as a prohibition: "Use the assert family. It is the only enforcement opt-in: a
bare `constraint`, a `require constraint`, an `assume constraint`, and a `satisfy` are visible,
cataloged descriptions that never execute" (`modeling-assumptions.md:498-500`). The D6 correction at
`28-…:49-58` replaces the conflated claim rather than annotating it. The two BACKLOG filings
(`:717-726`) are phrased as decision records ("was left open as a candidate; this is the filing"),
not as instructions to a future agent. The defective text is gone in every case, not warned about.

**Provenance audit of the amendment texts (audit focus 2) — clean.** I sampled every companion
amendment and every contract amendment carrying new content:

- No agent ruling is presented as owner-originated. The equality taxonomy carries "**[AGENT]
  (ratified by owner, 2026-08-12)** … This taxonomy is agent-originated and owner-reviewed;
  challenge it by re-deriving against the reasoning recorded here" (contract `:521-523`) — the
  exact split item1-F3 required, and the challenge route is stated rather than implied. The two
  owner `[NEED]`s above it (`:516-520`) carry the owner's narrow-bands reason and the
  modeler-chosen-tolerance rule, at owner grade.
- No amended statement is re-graded. LC-E05/E06/E10/E11/E12 keep `[INFERRED]`/`[INHERITED]`;
  LC-G07 keeps its owner-sourced quote and adds "The owner-sourced requirement above is unchanged."
- Nothing is marked settled or do-not-relitigate. ADR-009 says the opposite in its provenance line.
- Superseded text is quoted in each companion amendment note: LC-E06, LC-E10, LC-E11, LC-E12 each
  carry a `Superseded: "…"` quotation. LC-E05 paraphrases (M-2) because the supersession is an
  absence.
- One judgment call worth naming, not a finding: LC-E13 and invariant 61 were minted by the
  implementer and stamped `(ratified by owner, 2026-08-12)`. The owner did not see these texts. The
  stamp is defensible because their substance is the umbrella's Q3 warning tier, which *was*
  ratified that day, and the grade is agent-with-ratification rather than owner — so a challenger
  re-derives against Q3's reasoning, which is the correct route. Recorded so a later reader knows
  the stamp is inherited from the ruling, not from a review of this wording.

**Contradiction sweep (audit focus 6) — clean.** I re-ran the pairwise check rather than trusting
the record. The five precedence copies (contract A0 `:461`, invariant 33 `:245`, Appendix C cell
`:815`, companion LC-E11 `:315-317`, ADR-009 `:548`) state the same five terms in the same order;
the only variation is arrow-versus-"then". Four of the five restate full satisfaction as a coverage
claim and read identically. The three disposition-kind copies agree the same way. No document in
either sweep scope says a plain or `require` constraint executes.

### Code integrity

**Python diff is comment- and docstring-only — verified by reading, not by trusting the claim.**
`git diff 4678cd5..HEAD -- 'src/*' 'tests/*'` is two files:

- `src/sysml_codegen/extraction/constraint_report.py:3-15` — module docstring; the dead citation
  becomes "The test that proved that mapping retired with the legacy stack; CONSTRAINT-SEMANTICS
  Item 2 re-anchors the proof."
- `tests/conformance/test_extractor.py:876-886` (class docstring) and `:902` (inline comment) — same
  substitution; `:902` swaps the citation for "confirmed empirically against the fixture source,
  transcribed above."

No assertion, name, value, import, or signature moved in either file. This is the boundary the item
staked itself on (RI-6) and it held.

**Slop and failure-honesty checks: not applicable.** No executable text was written. The one
correction that could not be made without touching executable text — the four `all_satisfied`
assertions — was handed on rather than forced through, which is the honest call and the reason M-1
is about placement rather than about the decision.

**Boundary diffs re-run, all clean.** D-2 and D-4/SRC-01 byte-untouched:
`git diff 4678cd5..HEAD -- <contract> | grep -E "^[-+].*(D-2|D-4|SRC-01)"` → empty. Invariant 8
guardrail: `grep -E "^-.*Outcomes are exactly"` → empty. `git diff --check` → clean. No TEAx path in
the diffstat.

---

## Requested live probes

The orchestrator runs these and appends an addendum. Each names its expected outcome so a deviation
is visible.

**P-1 — codegen, blocked on approval in this sandbox**

```bash
cd /home/reid/1cfe/sysml-codegen-item7-rebuild
python3 scripts/check_doc_distinctness.py
```

Expected: `31 numbered reference documents checked, 0 identical-content groups` (matching
`verification.md:335-337`). Note `python3`, not `python` — bare `python` is not on PATH here.

**P-2 — companion, the D5-a and equality-rendering texts**

```bash
cd /home/reid/1cfe/agentic-mbse-item7-rebuild
sed -n '110,140p' claude/agents/sysml-expert.md
sed -n '20,60p'  docs/patterns/constraints.md
grep -n "ADR-009" docs/patterns/constraints.md
grep -n "When should you write an equality at all" -A 30 docs/patterns/constraints.md
```

Expected: (a) `sysml-expert.md:124` still holds `require constraint { system.flowRate >=
requiredFlow }` inside a `requirement def`, with an added sentence near `:132` stating the
requirement-side form is cataloged and visible, never executed, and that `assert constraint` is the
sole enforcement opt-in — **and no surrounding prose still frames the example as a check**; (b)
`constraints.md:43` no longer says "unassessed **today**"; (c) exactly one ADR-009 cite line; (d) the
four-class equality table rendered as `design.md:1141-1164` specifies, carrying the `[AGENT]
(ratified by owner, 2026-08-12)` stamp, the "not a second authority / the contract governs" clause,
and the owner's narrow-bands reason.

**P-3 — companion, the mechanical checks and the boundary**

```bash
cd /home/reid/1cfe/agentic-mbse-item7-rebuild
git diff --check dcb187b^..dcb187b
git show --stat dcb187b
git diff dcb187b^..dcb187b -- 'src/*' 'tests/*'
grep -rn "test_constraint_migration_mapping" docs/ src/ tests/ claude/ 2>/dev/null
grep -rniE "constraint[s]? (are |is )?(enforced|checked|verified|evaluated|a gate|gates|blocks)|enforced (gate|constraint)|plain constraint.*(execut|enforc|gate|check|verif|evaluat|block)" \
  docs/patterns/ docs/subtype-enumeration-decision-table.md claude/ --include=*.md
```

Expected: `--check` clean; five files in the commit, all documentation/guidance, none under `src/`
or `tests/`, no `uv.lock`; the `src/`+`tests/` diff **empty**; S1 zero hits; S3 hits only in this
item's own corrected headings (`common-mistakes.md:244,246`, `semantic-operators.md:493`,
`constraints.md:221`), each of which says the plain form is *not* a check.

**P-4 — companion, the subtype enumeration must have survived**

```bash
cd /home/reid/1cfe/agentic-mbse-item7-rebuild
sed -n '18,32p' docs/subtype-enumeration-decision-table.md
```

Expected: the row-1 enumeration (`include_subtypes=True`, `RequirementUsage` excluded) is intact
**verbatim** — REQ-EXT-09 and Item 2's totality gate rest on it — with only the *reason* substituted
to the positive form ("enumerated for visibility and catalog totality … only the assert family
executes"). The spec is explicit that D3 substitutes the reason and does not delete the enumeration;
this probe is the one that would catch an over-correction.

**P-5 — companion, the referencing test still passes**

```bash
cd /home/reid/1cfe/agentic-mbse-item7-rebuild
set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a
uv run --extra dev pytest tests/test_validation/test_item9_checks.py
```

Expected: **2 passed**. Without `SYSIDE_LICENSE_KEY` this reports 2 failed on an ImportError, which
is not a real result — see `verification.md:353-362`.

---

## Certification

**Certify-with-residuals.** The item delivers what it specified. Every success criterion verifiable
from this worktree is met with `file:line` evidence, the provenance discipline held under sampling,
the boundary discipline held under diff, and the sweep reproduces independently. The product-lens
gate is DISPOSED with all six findings resolved, the umbrella `spec-F1` INTENDED-CHANGE now resolves
against a live ADR, and the epic gate is CLEAR — nothing blocks certification.

The residuals are H-1 (the contract's one stale sentence about the companion rendering — fix this
one before close; it is the finding that would mislead a future editor), M-1 (put the four-assertion
hand-off where Item 3 reads it), M-2 (cut LC-E05's duplicated clause), and M-3 (the vendored-corpora
aggregation, which needs an owner's acceptance rather than an edit). None of them states a wrong
rule, and none of them blocks Items 2–5 from starting: the contract they build against is correct.

Per the stage brief this pass is read-only, so **no checkbox was marked** in `plan.md`, `spec.md`, or
the epic file, and no product-lens block was appended. On the evidence above, the plan's 91 checked
boxes are supported, and every spec success criterion except the mechanical-checks one (pending P-1
and P-3) is verified met.

**Not checked:**

- **The entire companion repository.** `/home/reid/1cfe/agentic-mbse-item7-rebuild` is unreadable
  from this sandbox — both `ls` and `Read` were denied. Every claim about D3, D4, D5-a through D5-f,
  the equality rendering, the ADR-009 cite, and commit `dcb187b`'s contents rests on
  `verification.md` and `design.md`, not on a read. Probes P-2 through P-5 exist to close this, and
  it is the largest unverified surface in this audit. In particular I could not confirm the D5-a
  added sentence's wording, only the soundness of the decision to keep the form.
- `scripts/check_doc_distinctness.py` was not run (approval denied) — P-1.
- **No test suite was run in either repository.** This is a documentation item that changes no
  executable text, and I verified that claim by reading the Python diff; but I did not confirm the
  suite is green at `f490a22`, so this audit says nothing about the repository's test state.
- **The amended rules' correctness against code.** I checked that the amendments say what the
  umbrella contract ruled and that the target-versus-current split is marked in the published text.
  I did not independently verify the `882161e` behavioral claims in `verification.md:317-319`
  (`executable_profile.py:949-950`, `constraint_extraction.py:726-735`, `elaborate.py:522-539`)
  against the code.
- **Documents outside the DD5 sweep scope** — `.project/research/`, `.project/completed/`,
  `.project/active/`. The exclusion is reasoned and recorded; I accepted it rather than re-derived
  it, and did not sweep those trees.
- **The upstream artifacts' own correctness.** I audited conformance to the spec, design, and
  umbrella rulings. Whether the umbrella contract rules the right semantics was settled upstream and
  is not re-opened here.

---

ARTIFACT: .project/active/constraint-semantics-contract-amendments/audit.md

---

## Orchestrator addendum — live probes executed + residual cures (2026-08-12)

Probes P-1 through P-5 were executed by the orchestrator exactly as specified above.
**All five match their expected outcomes:**

- **P-1** — `python3 scripts/check_doc_distinctness.py` → "31 numbered reference documents
  checked, 0 identical-content groups", exit 0.
- **P-2** — (a) `sysml-expert.md:124` keeps `require constraint` inside the `requirement def`
  with the settled-semantics paragraph following the example ("cataloged and visible … never
  executes … assert family is the sole enforcement opt-in"); no surrounding prose frames the
  example as a check. (b) `constraints.md` states the rule as settled, no "today" framing.
  (c) exactly one ADR-009 cite (`constraints.md:71`). (d) the four-class equality table renders
  in full with the `[AGENT] (ratified by owner, 2026-08-12)` stamp, the not-a-second-authority
  clause ("if the two ever disagree, the contract governs"), and the owner's narrow-bands
  reason.
- **P-3** — `git diff --check dcb187b^..dcb187b` clean; five files, all documentation/guidance,
  none under `src/` or `tests/`, no `uv.lock`; `src/`+`tests/` diff empty; S1 zero hits; S3
  hits only the item's own corrected not-a-check headings
  (`semantic-operators.md:493`, `constraints.md:221`, `common-mistakes.md:244,246`).
- **P-4** — row-1 enumeration intact verbatim (`include_subtypes=True`, EXCLUDE
  `RequirementUsage`) with the reason substituted to the positive visibility/totality form.
- **P-5** — licensed run: `tests/test_validation/test_item9_checks.py` → **2 passed** (0.37s),
  with `SYSIDE_LICENSE_KEY` sourced from the companion primary checkout's `.env`.

### Residual dispositions

- **H-1 — FIXED** (this commit): contract "Equality intent and authoring policy" preamble now
  states the real governance — the companion renders the instruction in full and cites the
  contract as authority; contract governs on disagreement; an edit here obligates a matching
  edit there. The correction note quotes the misdescribing sentence it replaced.
- **M-1 — FIXED** (this commit): the four `all_satisfied` `tests/execution/` assertions are now
  recorded as an explicit hand-off bullet in the epic's Item 3 Current State — the section
  Item 3's stages read — pointing at the verification.md sweep record.
- **M-2 — FIXED** (this commit): LC-E05's amendment note no longer restates the three-kinds
  clause verbatim; it records what was added and quotes what was superseded, matching the
  sibling amendment shape.
- **M-3 — ACCEPTED as a recorded deviation** (orchestrator execution-detail call, owner can
  reverse at close): the S2 vendored-corpora hits stay aggregated per corpus with file names
  and counts (`verification.md:118`) rather than expanded to 52 identical rows. The disposition
  is uniform ("out of class — vendored upstream reference corpus"), the files are named, and
  this audit reproduced the sweep independently; expansion would add rows, not information.
  The spec's raw-hit-list wording was not honored literally for this one class.

Post-cure gates, re-run by the orchestrator: `check_doc_distinctness.py` → 31/0;
`git diff --check` clean in both repositories.

With P-1–P-5 confirmed and H-1/M-1/M-2 cured, the audit's own conditional resolves:
**Certify-with-residuals stands, residual set now = M-3 acceptance record only.**
