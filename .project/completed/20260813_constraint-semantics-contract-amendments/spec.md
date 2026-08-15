# Spec: Constraint Contract and Authoring Policy (CONSTRAINT-SEMANTICS Item 1)

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-08-12
**Complexity:** MEDIUM–HIGH (two repositories, ratified authorities, strict provenance; no
executable code, but dead-citation fixes in comments and docstrings are in scope — see the
code-text boundary under Documentation corrections)
**Estimated effort:** 2.5–3 days, revising the epic's 1.5-day figure (spec 1h, design 3h, plan 1h,
execute and review 14–18h). The epic figure is a guideline, not a cap. The revision is what the
work actually is: one ADR, roughly seventeen amendments across the contract and companion, seven
documentation corrections plus whatever the recorded sweep adds, a six-state vocabulary published
in two dialects, and two policies published in two repositories — half of it in a repository this
worktree cannot read. Under-budgeting Item 1 pushes thin text into four downstream items.
**Branch:** `item7-rebuild` (worktrees `/home/reid/1cfe/sysml-codegen-item7-rebuild` and
`/home/reid/1cfe/agentic-mbse-item7-rebuild`)

---

## Problem

The constraint-semantics contract is settled. Nothing that a modeler or an implementing agent
actually reads says so yet.

The umbrella spec (`.project/active/constraint-semantics-contract/spec.md`, approved) rules
assert-only enforcement, catalog totality with severity by cause, coverage-truthful headlines, and
study defaults. Every durable authority in the two repositories still states the superseded rule:

- **No ADR records the change.** The headline-vocabulary change is an intentional product-contract
  change that contradicts contract invariant 33 and companion LC-E11 as written. The product-lens
  gate dispositioned it INTENDED-CHANGE and requires a filed ADR, cited back into the lens trail,
  **before implementation**
  (`.project/active/constraint-semantics-contract/product-lens.md`, spec-F1).
- **The ratified lifecycle contract still teaches the old behavior.** Invariants 1, 9, 28, 32, 33,
  46/46a, 48 and the Appendix B/C cells that restate them carry pre-amendment semantics
  (`.project/concepts/constraint-execution-authoritative-lifecycle-contract.md`). Invariant 8 is
  in the amendment set as a **guardrail**, not a target: it fixes the profile's four outcomes and
  must survive unchanged, because the new severity is a named contextual failure rather than a
  fifth outcome.
- **The frozen requirements companion has no amendment yet**, though its header makes it the only
  place forward requirement amendments may land; LC-E05/E06/E10/E11/E12 all state behavior this
  contract changes (`.project/concepts/constraint-execution-lifecycle-requirements.md:3-7`).
- **Seven documentation statements actively steer modelers wrong.** D1–D7 in the research register
  (`.project/research/20260812-101200_constraint-semantics-end-to-end.md` §7) teach that a bare
  `constraint` or `require constraint` is an enforced gate, attribute unassessed status to owner
  kind alone, and cite a retired test as living totality evidence. The first of these is the exact
  form that silently does nothing.
- **The blessed authoring pattern is unpublished.** There is nowhere a modeler can read the
  assert-with-bindings gate shape, when an equality should be used at all, or that tolerances are
  theirs to choose.

Two obligations carry decision force into this item:

- **[OWNER, 2026-08-12]** Required sequence: settle semantics → fix documentation and the test
  model to match, capturing expected output → then run tests to confirm
  (`.project/active/constraint-semantics-contract/rulings-20260812.md`). Item 1 is the
  documentation half of that sequence, and Items 2–5 build against what it publishes.
- **[OWNER-VERBATIM, 2026-08-12]** "we know that narrow bands of viability may make design
  exploration really difficult. So I want to call out in our concept WHEN we really think
  equalities SHOULD be used (instructions) in addition to the sysml-codegen support"

Until this lands, every downstream item builds against text that contradicts the contract it is
implementing, and any modeler following current guidance authors constraints that never execute.

## What publishes where

The whole deliverable in one pass. "Decided" means this spec fixes the location; "design" means
the location is an open question below.

| What | Repository / file | Location |
|---|---|---|
| ADR-009, the coverage-headline change record | codegen `docs/architecture/modeling-assumptions.md` | decided (placement within the file: design) |
| Contract amendments (invariants 1, 9, 28, 32, 33, 46/46a, 48; the warning tier; Appendix B and C cells) | codegen `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md` | decided |
| Companion amendments (LC-E05/E06/E10/E11/E12, LC-G07) | codegen `.project/concepts/constraint-execution-lifecycle-requirements.md` | decided |
| Headline vocabulary meanings, both dialects | with the contract amendments (invariants 32/33) | decided |
| D1, D2, D6, D7 corrections + blessed gate shape | codegen `docs/architecture/modeling-assumptions.md`, `reference/28-constraint-lowering-and-catalog.md`, `reference/01-extraction.md` | decided |
| D3, D4, D5 corrections + authoring policy + equality taxonomy | agentic-mbse `docs/subtype-enumeration-decision-table.md`, `docs/patterns/constraints.md`, `docs/patterns/semantic-operators.md`, `claude/agents/sysml-expert.md` | decided (line positions unverified from this worktree) |
| Equality instruction, concept-layer copy | codegen `.project/concepts/…` | design picks the file; the other copy cites it |
| Dead-citation fixes in comments and docstrings | codegen `src/sysml_codegen/extraction/constraint_report.py`, `tests/conformance/test_extractor.py` | decided |
| Two future-capability candidate lines | codegen `.project/backlog/BACKLOG.md` | decided |
| Recorded sweep output and its hit-list dispositions | `.project/active/constraint-semantics-contract-amendments/verification.md` | decided |

## Success Criteria

- [x] **[INHERITED: constraint-semantics-contract/spec.md]** A live ADR records the intended
      contract change with agent-originated, owner-ratified provenance, and its id is cited from
      the product-lens disposition trail.
- [x] **[INHERITED: constraint-semantics-contract/spec.md]** The lifecycle contract and the frozen
      requirements companion publish the full amendment set, invariant by invariant and
      requirement by requirement, with the original provenance grades of amended statements intact.
- [x] **[INHERITED: research D1–D7]** No statement remains in either repository that a plain or
      requirement-side constraint is an enforced gate, and none cites the retired totality test as
      living evidence. Each defect is corrected at its location by amendment or deletion — not
      annotated, and not answered with compensating prohibition prose.
- [x] The universal claim above is **checked, not asserted**: a recorded sweep runs over both
      repositories' documentation and their comment/docstring text, and every hit is dispositioned
      (corrected, or recorded as correct with the reason) in `verification.md`. D1–D7 plus the
      three locations named in this spec are the floor, not the ceiling.
- [x] **[NEED carried from constraint-semantics-contract/spec.md]** Authoring guidance explains
      when equality intent should be derived, band-checked, one-sided, fixed as an input, or
      closed by construction, and states that tolerance values are modeled values the modeler
      chooses.
- [x] The blessed assert-with-bindings gate shape is published, together with its scope precision:
      the restriction is predicate-body-only, binding-position feature chains stay supported, and
      inline asserted forms stay admitted.
- [x] Both headline vocabularies — the generated report's and TEAx's canonical runtime one — have
      a published **meaning** for every state, including the new partial-coverage state, and the
      precedence order among them. The spec text draws an explicit line: Item 1 owns meaning,
      Item 3 owns token spellings, schema field names, and normalization code.
- [x] **[OWNER]** Documentation is correct before confirmation testing begins. No amendment in
      this item is written to match current behavior.
- [x] `scripts/check_doc_distinctness.py`, the equivalent documentation checks in the companion
      repository, and `git diff --check` pass in both touched repositories.

**All nine were ticked at close (2026-08-13), none on evidence the close pass produced.** The
audit verified seven from the codegen worktree with `file:line` evidence (`audit.md`, spec
conformance table); the two it could not — `check_doc_distinctness.py` and the companion-side
checks — were closed by the orchestrator's probes P-1 (31 documents, 0 identical-content groups)
and P-3 (companion `git diff --check` clean, five documentation files, `src/`+`tests/` diff empty),
recorded in the audit addendum. No suite was re-run at close.

## Known Requirements

Citation key: `(Qn)` and `(Ln-n)` cite
`.project/active/constraint-semantics-contract/rulings-20260812.md`; `(lens spec-Fn)` cites
`.project/active/constraint-semantics-contract/product-lens.md`; `(Dn)` cites the research
register §7; `(umbrella spec-review Ln-n)` cites
`.project/active/constraint-semantics-contract/spec-review.md`, which is a different document from
the ruling record and uses a colliding ID form — always spelled out in full here. Every
requirement text stands alone.

### Provenance discipline (binding on every artifact this item writes)

- **[HARD]** (capture-fidelity law 1) Q1–Q8 and the L2-1 / L2-2 / L3-1 / L3-3 / L2-3 refinements
  are **[AGENT] (ratified by owner, 2026-08-12)**. No artifact this item writes may present them
  as owner-originated or mark them settled/do-not-relitigate. The only owner-grade payloads in
  scope are: the two owner-verbatim quotes in the ruling record, the modeler-owned-tolerance need,
  the equality-usage-instruction need, and the documentation-before-testing sequence.
- **[HARD]** (capture-fidelity law 1) An amendment preserves the original provenance grade of the
  statement it amends. Amending an `[INHERITED]` companion requirement does not promote it; the
  amendment's own new content carries agent-ratified grade and its date.
- **[HARD]** (capture-fidelity law 3) D1–D7 are corrected by deleting or rewriting the defective
  text at its location. A correction may not leave the defective claim in place with a warning
  attached, and may not add prohibition prose that anchors future readers on the rejected form.

### The ADR

- **[INFERRED]** (lens spec-F1) One ADR is filed that records the coverage-headline change as an
  intentional product-contract change: what invariant 33 and LC-E11 said, what they now say, why,
  and that the decision is agent-proposed and owner-ratified on 2026-08-12. It exists before any
  Item 2/3 code lands.
- **[INFERRED]** The ADR's identifier is cited back into
  `.project/active/constraint-semantics-contract/product-lens.md` so spec-F1's INTENDED-CHANGE
  disposition resolves against a live document rather than an intention.
- **[INFERRED]** The ADR is discoverable from the contract and companion amendments it justifies,
  and from this item's ledger. A decision recorded where no reader will meet it is not filed.
- **[INFERRED]** **Decision recorded here, corrected from the first draft:** the ADR is
  **ADR-009**, and it lands as an identified decision entry inside this repository's
  `docs/architecture/modeling-assumptions.md` — not as a standalone file. Rationale, from the
  repository's actual recorded decision: commit `eda48f9` ("docs(D3/D5): Consolidate ADRs into
  modeling-assumptions.md", 2026-02-22) deleted all eight standalone ADR files from
  `docs/architecture/` and folded their content into `modeling-assumptions.md` as numbered topical
  sections. Codegen ADRs are citation-identifiers over consolidated prose, and a revived
  standalone file would reverse an owner-authored consolidation. 009 is the next free identifier:
  ADR-001 through ADR-008 are consumed by live citations. Placement within the file — a new
  numbered section, or an entry inside §8 "Constraints Execute Under a Profile", which is already
  the D1/D2/D7 correction home — is design's call. The single ADR governs both repositories'
  vocabularies; the companion cites it rather than mirroring it, so there is one authority for one
  decision.
- **[INFERRED]** The filing route named in the product-lens disposition (`.project/scripts/adr.sh
  new` + `amend`) does not exist in this repository — `.project/scripts/` holds only
  `get-metadata.sh`. The ADR is hand-authored into the consolidated document. This is recorded so
  a later reader does not go looking for a tool.

### Lifecycle contract amendments

- **[INFERRED]** (lens spec-F2) The amendment set covers at minimum the following, published
  invariant by invariant. Design may add a statement it finds carrying the superseded rule; it may
  not drop one from this list. **The no-drop rule does not force an edit onto correct text**: an
  entry marked here as a guardrail, or one design reads and finds already consistent with the
  ruled semantics, is discharged by recording "verified already-correct, no amendment needed"
  with the verification note. Silently skipping an entry is what the rule forbids.
  - **Invariant 1** — the halt scope narrows from "any `BLOCK` halts the model" to "`BLOCK` on an
    **asserted** constraint halts the model", and the consequence is written down as a product
    statement: an unsupported predicate inside a plain `constraint` never halts generation,
    because the form gate runs before the predicate walk, and the usage catalogs as unassessed.
    Descriptive constraints are never load-bearing.
  - **Invariant 9 (target), invariant 8 (guardrail)** — a new generation-halting severity exists
    for an **asserted, structurally unattachable** usage: an in-scope asserted form with no
    attachment capability. It is a named contextual failure of the kind invariant 9 already
    admits, so the amendment lands on 9. Invariant 8's four profile outcomes must survive
    unchanged — the new severity is not a fifth outcome and does not reclassify `ADMIT`.
  - **Invariant 28** — a third visible disposition kind, non-reaching-with-reason, joins eligible
    and excluded-with-reason. Every authored usage carries exactly one disposition, and "reaches
    no instance" is a disposition rather than an absence.
  - **Invariant 32** — the zero-input aggregator obligation is restated over applicable asserted
    gates: a constraint-bearing model with no applicable asserted gate still requires the
    aggregator and a not-assessed report; a model with no constraint usages remains inert.
  - **Invariant 33** — headline precedence becomes violation → indeterminate → full satisfaction
    → partial coverage → not assessed, and full satisfaction means every applicable asserted gate
    was assessed and passed.
  - **Invariants 46/46a** — the persisted-exact-report contract admits the report's new compact
    coverage accounting, and 46a's fail-closed obligation extends to the new headline state: an
    unknown or unmapped headline token fails closed, never a `KeyError` and never a fallthrough.
  - **Invariant 48** — the embedded catalog remains the sole catalog schema authority and the
    authority for coverage truth; the report's coverage accounting is derived from it in one
    direction and is never an independently maintained second inventory.
  - **Appendix C, three cells, with different asks:**
    - "Mixed satisfied/violated/indeterminate population" (**target**) states the old precedence
      verbatim and is restated to the five-state order.
    - "Excluded-only usages" (**target, narrow ask**) stays true for a plain-only model and is
      wrong only when the exclusions include an asserted usage. The whole ask is a clause that
      splits by form: plain-only reads not-assessed, an excluded asserted usage reads partial
      coverage. Not a rewrite.
    - "Zero constraint usages" (**guardrail**) already reads correctly as the new vocabulary's
      report-absent state. Verify and record; do not amend.
  - **Appendix B** — the correction-register row carrying the same superseded claim as the
    Appendix C excluded-only cell ("excluded-only usages retain `not_assessed` visibility") is
    amended with it, so the two do not disagree. The neighbouring row on catalog/report
    visibility for excluded-only usages stays true and is a **guardrail** — naming it here so it
    does not collect a collateral edit.
  - **The warning tier of severity by cause** — an asserted **vacuous** usage (its owner has zero
    occurrences) is a warning-grade visible disposition plus an authoring-time advisory, and it
    counts as missing assessment until it carries an explicit inapplicability disposition. Design
    names the amendment target that carries the severity and the advisory; invariant 28 supplies
    the disposition kind, not the severity. Without this, Items 2–3 have no published middle tier
    between the halting error and the never-errors record.
- **[INFERRED]** Amendments land in place using the contract's existing convention — the amended
  statement carries `(amended YYYY-MM-DD, CONSTRAINT-SEMANTICS Item 1)`, as invariants 19, 20, 22,
  and 26 already do — so a reader meets the current rule first and its history second.

### Frozen requirements companion amendments

- **[INFERRED]** (lens spec-F3) The companion is amended in place, per its header's
  "forward requirement amendments happen here only", covering at minimum:
  - **LC-E05** — the third disposition kind and the obligation that dispositions cover the
    complete authored-usage domain.
  - **LC-E06** — excluded and unassessed usages never vanish from coverage, restated so
    non-reaching usages are covered by the same guarantee.
  - **LC-E10** — the zero-input aggregator requirement restated against applicable asserted gates.
  - **LC-E11** — the direct contradiction: "else any assessed result → `all_satisfied`" becomes
    the coverage-truthful precedence with the partial state.
  - **LC-E12** — an asserted usage with zero eligible entries yields the partial-coverage state,
    not the not-assessed surface; constraint-free models stay byte-stable and report-free.
  - **LC-G07** — the companion's sole-catalog-authority requirement gains the coverage-truth
    clause that invariant 48 gains, so the two authorities do not disagree. LC-G07 is
    owner-sourced; the amendment adds to it and does not re-grade it. If design concludes the
    clause needs no companion mirror, it says why in the amendment record.
- **[INFERRED]** Amending an `[INHERITED]`-graded requirement leaves its grade and cited source
  intact; the amendment records its own date and this item as the amending authority.

### Headline vocabulary semantics (meaning only)

- **[INFERRED]** (L2-1, L2-2) **"Applicable asserted gate" is defined where it is first used**, because
  every state meaning, the precedence order, and the inventory-versus-feasibility split turn on it,
  and no later item has the mandate to define it. The published rule: a usage is an applicable
  asserted gate when its source form is in the assert family and the form is in executable scope —
  including a vacuous one whose owner has zero occurrences — and it stops being applicable only
  when it carries an explicit inapplicability disposition. Plain and requirement-side usages are
  never applicable asserted gates.
- **[INFERRED]** (Q5, refined L2-1) Item 1 publishes the **meaning** of each state in both
  vocabularies. Six states exist:
  1. **Violation** — at least one applicable asserted gate was assessed and failed.
  2. **Indeterminate** — no violation, and at least one assessed gate produced Kleene unknown.
  3. **Full satisfaction** — every applicable asserted gate was assessed and passed. This is a
     coverage claim, not merely the absence of a failure.
  4. **Partial coverage (new)** — at least one applicable asserted gate exists and went
     unassessed, including an asserted vacuous gate carrying no explicit inapplicability
     disposition.
  5. **Not assessed** — the model has constraint usages but no applicable asserted gate at all;
     a deliberately descriptive model reads here, never partial.
  6. **Unconstrained (report absent)** — the model authors no constraint usage, so no report is
     generated and the runtime's unconstrained disposition is true by construction.
- **[INFERRED]** The two-total distinction is published with the vocabulary: *inventory totality*
  counts every authored usage of every form; *feasibility coverage* counts applicable **asserted**
  gates only. Descriptive and requirement-side usages appear in inventory and never in the
  feasibility denominator.
- **[INFERRED]** Precedence among the states is violation → indeterminate → full satisfaction →
  partial coverage → not assessed.
- **[HARD]** (existing interface, spec-review L1-1) Two vocabularies exist and are bridged by a
  normalization seam. Item 1's definitions cover **both** the generated report's states and TEAx's
  canonical runtime states, so a state defined on one side without a counterpart on the other is a
  defect in this item's output.
- **[INFERRED]** **Boundary, stated explicitly:** Item 1 fixes what each state means and when it
  is claimed. Item 3 owns the concrete token spellings, report schema field names and shapes, the
  normalization-seam mapping code, generated-schema migration, and the TEAx policy defaults that
  dispatch on the canonical tokens. **No amendment in this item names a token spelling or a report
  schema field name as normative**; where a current spelling is quoted it is quoted as today's
  text being amended. The invariant 46/46a amendment in particular says that the report carries
  compact coverage accounting and that unknown headline tokens fail closed — it does not say what
  the fields are called or shaped.

### Documentation corrections (D1–D7) and published authoring policy

- **[INHERITED: research §7]** Each defect is corrected at its location. All are agent-authored
  text with no OWNER/HARD/ADR marker, so correction by deletion or rewrite is the
  capture-fidelity-correct move (lens ledger, "Not findings" note).
- **[INFERRED]** The table below is the **floor, not the closed set** — the same "at minimum …
  design may add, may not drop" rule the contract amendment set carries. The register was
  inherited from the research doc and a one-minute grep found three further instances of the same
  defects, named in the table. The recorded sweep below is what makes the set complete.

  | # | Location | Required correction |
  |---|---|---|
  | D1 | codegen `docs/architecture/modeling-assumptions.md` (the "what a modeler needing an enforced gate should do" paragraph) | Remove the claim that a bare `constraint` or `require constraint` gives an enforced gate; state assert-only enforcement |
  | D2 | codegen `docs/architecture/modeling-assumptions.md` (unassessed enumeration) | Include `plain_usage`, `require`, and `assume` in the unassessed set, not requirement-side and bad-owner only |
  | D3 | agentic-mbse `docs/subtype-enumeration-decision-table.md` | **Substitute the reason, stated positively — do not delete the enumeration.** The sentence is the row-1 rationale for sweeping `require`/plain subtypes, and that enumeration (`include_subtypes=True`, `RequirementUsage` excluded) is what REQ-EXT-09 and Item 2's totality gate rest on; it must survive verbatim. Corrected reason: `require` and plain subtypes are enumerated for **visibility and catalog totality** — every authored usage gets a catalog disposition — not because those forms execute. Only the assert family executes |
  | D4 | agentic-mbse `docs/patterns/constraints.md` | Replace the false reason for bare `constraint` being wrong; the parser does produce a `ConstraintUsage`, classified `plain_usage` — the form gate is why it does not execute |
  | D5 | agentic-mbse `claude/agents/sysml-expert.md`, `docs/patterns/semantic-operators.md` | Stop teaching `require constraint` as an equal alternative for a check |
  | D6 | codegen `docs/architecture/reference/28-constraint-lowering-and-catalog.md` | Unassessed status follows source form; owner kind decides occurrence expansion. The axes are independent (contract invariant 16) |
  | D7 | codegen `docs/architecture/modeling-assumptions.md`, `docs/architecture/reference/01-extraction.md`, **and** `docs/architecture/reference/28-constraint-lowering-and-catalog.md` (the "migration mapping test … proves every swept usage lands in exactly one catalog outcome" sentence) | Remove the citation of the retired `test_constraint_migration_mapping.py` as living totality evidence |
  | D7-code | codegen `src/sysml_codegen/extraction/constraint_report.py` (module docstring), `tests/conformance/test_extractor.py` (test docstring) | Same dead citation, in comment text — see the code-text boundary below |

- **[INFERRED]** (D7 boundary, stated by requirement rather than by file) **Item 1 removes
  dead-evidence citations wherever they appear** and states plainly that the totality proof is
  pending — including `01-extraction.md`'s REQ-EXT-09 evidence cell, which cites only the retired
  test, and any verification-matrix-adjacent prose carrying the same citation. **Item 2 owns the
  re-grade and re-anchor** of the REQ-EXT-09 and REQ-CL-04 rows themselves: their grade, their new
  proof, and the independent totality evidence behind it (lens spec-F7). Removing a citation to a
  deleted file is not a re-anchor; choosing the replacement proof is.
- **[INFERRED]** (the matrix-row window, decided) `docs/architecture/verification-matrix.md`
  already cites live tests for REQ-EXT-09 rather than the retired one, so no dead citation sits
  there — only the PASS grade, which the totality evidence does not yet support. Item 1 adds a
  dated "re-grade pending, CONSTRAINT-SEMANTICS Item 2" pointer at the row. That is an addition,
  not a re-grade, so it stays inside the non-goal, and a reader who meets the green row meets the
  pointer with it.
- **[INFERRED]** (code-text boundary, ruled for this item) **A comment or docstring edit that
  fixes a dead citation is in scope**, recorded per file, with zero behavior change — the
  criterion is "no remaining statement in either repository", and a docstring is a statement a
  reader meets. **Executable text stays out**: no code, no test assertions, no behavior. If a
  correction cannot be made without touching executable text, it is recorded in `verification.md`
  and handed to the item that owns that code.
- **[INFERRED]** (lens item1 review L1-2/L3-2) **A recorded sweep closes the class.** Before the
  item closes, a search runs over both repositories' documentation **and** their comment and
  docstring text for at least: the retired test name `test_constraint_migration_mapping`;
  `require constraint` presented as check guidance; and claims that a plain or bare `constraint`
  enforces, gates, or is checked. Every hit is listed in `verification.md` with its disposition —
  corrected, or correct-as-written with the reason. The named search terms, the directories
  covered, and the raw hit list are part of the record; a summary is not.
  `scripts/check_doc_distinctness.py` does not substitute: it compares byte-identity between
  numbered reference documents and would never see a wrong sentence.
- **[INFERRED]** (Q4, scope precision lens spec-F6) The blessed gate shape is published: a
  `constraint def` with formals, asserted as `assert constraint g : Def { in formal = <path>; }`,
  with the predicate body over formals only. Published with it: the restriction is
  **predicate-body-only**; feature chains in binding position stay supported (contract D-7,
  invariant 20); inline asserted forms stay admitted (invariant 12); in-predicate chain admission
  is a filed future capability candidate, not a closed door.
- **[NEED]** (owner-stated, 2026-08-12) Tolerances are modeled values chosen by the modeler. The
  published guidance says so, and says the pipeline never invents one.
- **[NEED]** (owner-stated, 2026-08-12, quoted verbatim in Problem) The guidance instructs **when**
  equalities should be used at all, and it states the owner's reason: narrow bands of viability
  make design exploration difficult.
- **[INFERRED]** (umbrella spec R-POL-4, agent-drafted and owner-reviewed in session 2026-08-12)
  The instruction's content is the four-class intent taxonomy for `a == b`: (1) structural
  identity → derive it, do not constrain it; (2) cross-check of independently computed values → a
  loose, physically motivated validity band; (3) feasibility gate → prefer a one-sided inequality,
  and if a quantity must equal a value, fix it as an input rather than search-and-constrain; (4)
  composition closure → derive the last term by construction, otherwise a banded validity check.
  The taxonomy is published carrying that grade, so a later reader can challenge it by re-deriving
  against its recorded reasoning; the *need* for the instruction above is what is owner-originated.
- **[INFERRED]** The equality instruction is published in the concept layer **and** in
  agentic-mbse authoring guidance, per the owner's "call out in our concept … in addition to the
  sysml-codegen support". One is the authority and the other cites it; which is which is a design
  choice recorded in Open Questions.
- **[INFERRED]** (lens item1 review L2-2) **"Filed as a future capability" names an artifact.** The
  two commitments the published text makes — in-predicate feature-chain admission (Q4) and the
  evaluated-advisory tier for plain constraints (Q1) — each get one line in
  `.project/backlog/BACKLOG.md`, phrased as a decision record rather than an instruction to a
  future agent. Without those two lines, the word "filed" in the published contract is false.
- **[INFERRED]** (Q1, Q7) The published rule states that bare `constraint` is a visible, cataloged,
  never-executed description; that the assert family is the sole enforcement opt-in; and that
  `require`/`assume`/`satisfy` stay non-executable and visible, with an out-of-scope form drawing
  a named visible exclusion rather than the unreachable-assert error.

### Sequencing

- **[NEED]** (owner-directed sequence, 2026-08-12) Every artifact in this item states the settled
  semantics, never observed current behavior. Where current behavior differs from the amended
  rule, the amendment says what must be true and names the item that makes it true; it does not
  soften the rule to match today's code.
- **[INHERITED: epic]** Item 1 completes before Items 2–5 implement, and Item 5's all-65 owner
  checkpoint may begin as soon as the authoring policy publishes.

## Non-Goals

- Implementing anything. Catalog totality, the completeness gate, report coverage, TEAx
  projection and policy, fixtures, and the predicate defect fixes belong to Items 2–5. Executable
  text is untouched; only comment and docstring citations are corrected.
- Choosing the concrete headline token spellings, report schema field names, or the normalization
  seam's code shape — Item 3.
- Designing calculation-definition constraint attachment — Item 6.
- Re-grading REQ-EXT-09 or REQ-CL-04, and choosing the proof that re-anchors them — Item 2,
  wherever those rows and their evidence cells live. Item 1 removes citations to a deleted test
  and adds the dated pending pointer; it picks no replacement evidence.
- Choosing CATF tolerance values or intent classes — Item 5, behind the owner checkpoint.
- **Resolving the parked D-2 vs D-4/SRC-01 premise conflict** (umbrella spec Open Questions, lens
  spec-F6). Contract D-2's acceptance cell requires "a usage-owned attribute on a concrete
  `PartUsage` and a self-named actual" while D-4/SRC-01 makes bare self-named bindings
  UNSUPPORTED. No amendment in this item may touch either statement, in either direction; the
  conflict stays surfaced and parked for the owner (capture-fidelity law 4).
- Changing BLOCK-halts-generation semantics for asserted constraints, or the profile's four
  outcomes.
- Touching the TEAx repository. Item 1 defines the canonical runtime vocabulary's meaning; Item 3
  lands the code.

## Open Questions / Deferred to design

- **ADR placement within `modeling-assumptions.md`.** The file and the identifier are decided
  above (ADR-009, consolidated into `docs/architecture/modeling-assumptions.md`, per commit
  `eda48f9`). Open: whether it reads better as a new numbered section or as an entry inside §8,
  which is already the D1/D2/D7 correction home. Also open: whether the companion repository wants
  a stub cite next to `docs/patterns/adr002-calculations.md`, the one ADR-with-a-file left
  standing across the pair.
- **Which concept file hosts the equality instruction.** Candidates are
  `.project/concepts/constraint-execution-and-design-space-studies.md` (the ratified concept the
  owner's word "concept" most likely names) and the lifecycle contract's supported-boundary
  section. Design picks one as authority and makes the other cite it.
- **Amendment presentation in the companion.** In-place amendment matching the contract's
  `(amended …)` convention is the recorded default; design confirms it reads correctly against the
  companion's copy-and-freeze header.
- **Companion-repository documentation checks.** This worktree is sandboxed away from
  `/home/reid/1cfe/agentic-mbse-item7-rebuild`, so the companion's doc-check surface and the
  current line positions of D3/D4/D5 are unverified here. Design confirms both before editing;
  the D3–D5 defect descriptions come from the research register, not from a read in this session.
- Whether the published vocabulary meanings live in one place both repositories cite, or in the
  contract with the ADR as the change record. Related to the ADR-discoverability requirement.
- **The `01-extraction.md` evidence gap.** Item 1 removes the retired test from REQ-EXT-09's
  evidence cell there and leaves the cell citing no proof until Item 2 re-anchors it. Design
  decides the interim wording so the gap reads as pending rather than as an omission.
  (The matrix-row window itself is no longer open — the dated pending pointer is decided above.)

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_constraint_semantics_contract.md` (CONSTRAINT-SEMANTICS, Item 1)
- **Required Reading:**
  - `.project/active/constraint-semantics-contract/spec.md` (umbrella behavioral contract)
  - `.project/active/constraint-semantics-contract/rulings-20260812.md` (Q1–Q8 + refinements)
  - `.project/research/20260812-101200_constraint-semantics-end-to-end.md` §7 (D1–D7 register)
  - `.project/active/constraint-semantics-contract/product-lens.md` (spec-F1/F2/F3 obligations)
  - `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md` (amended here)
  - `.project/concepts/constraint-execution-lifecycle-requirements.md` (frozen companion)
- **Product-lens ledger:**
  `.project/active/constraint-semantics-contract-amendments/product-lens.md`
- **Spec review:** `.project/active/constraint-semantics-contract-amendments/spec-review.md`
  (verdict Revise, 2026-08-12; resolutions recorded there by finding ID and incorporated here)
- **Design:** `.project/active/constraint-semantics-contract-amendments/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_design`.
