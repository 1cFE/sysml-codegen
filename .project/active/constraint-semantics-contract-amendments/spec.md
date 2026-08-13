# Spec: Constraint Contract and Authoring Policy (CONSTRAINT-SEMANTICS Item 1)

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-08-12
**Complexity:** MEDIUM (no code; two repositories, ratified authorities, strict provenance)
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
- **The ratified lifecycle contract still teaches the old behavior.** Invariants 1, 8/9, 28, 32,
  33, 46/46a, 48 and three Appendix C cells state pre-amendment semantics
  (`.project/concepts/constraint-execution-authoritative-lifecycle-contract.md`).
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

## Success Criteria

- [ ] **[INHERITED: constraint-semantics-contract/spec.md]** A live ADR records the intended
      contract change with agent-originated, owner-ratified provenance, and its id is cited from
      the product-lens disposition trail.
- [ ] **[INHERITED: constraint-semantics-contract/spec.md]** The lifecycle contract and the frozen
      requirements companion publish the full amendment set, invariant by invariant and
      requirement by requirement, with the original provenance grades of amended statements intact.
- [ ] **[INHERITED: research D1–D7]** No statement remains in either repository that a plain or
      requirement-side constraint is an enforced gate. Each of D1–D7 is corrected at the defect by
      amendment or deletion — not annotated, and not answered with compensating prohibition prose.
- [ ] **[NEED carried from constraint-semantics-contract/spec.md]** Authoring guidance explains
      when equality intent should be derived, band-checked, one-sided, fixed as an input, or
      closed by construction, and states that tolerance values are modeled values the modeler
      chooses.
- [ ] The blessed assert-with-bindings gate shape is published, together with its scope precision:
      the restriction is predicate-body-only, binding-position feature chains stay supported, and
      inline asserted forms stay admitted.
- [ ] Both headline vocabularies — the generated report's and TEAx's canonical runtime one — have
      a published **meaning** for every state, including the new partial-coverage state, and the
      precedence order among them. The spec text draws an explicit line: Item 1 owns meaning,
      Item 3 owns token spellings, schema field names, and normalization code.
- [ ] **[OWNER]** Documentation is correct before confirmation testing begins. No amendment in
      this item is written to match current behavior.
- [ ] `scripts/check_doc_distinctness.py`, the equivalent documentation checks in the companion
      repository, and `git diff --check` pass in both touched repositories.

## Known Requirements

Citation key: `(Qn)` and `(Ln-n)` cite
`.project/active/constraint-semantics-contract/rulings-20260812.md`; `(lens spec-Fn)` cites
`.project/active/constraint-semantics-contract/product-lens.md`; `(Dn)` cites the research
register §7. Every requirement text stands alone.

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
- **[INFERRED]** **Decision recorded here, revisable in design:** the ADR lands in this repository
  at `docs/architecture/ADR-009-constraint-coverage-and-headline-semantics.md`. Rationale:
  ADR-001 through ADR-008 are already-consumed identifiers in this repository's citations, so 009
  is the next free number; `docs/architecture/` is the path CLAUDE.md and code comments already
  imply for codegen ADRs; and the report whose vocabulary changes is generated here. The single
  ADR governs both repositories' vocabularies — the companion repository cites it rather than
  mirroring it, so there is one authority for one decision.

### Lifecycle contract amendments

- **[INFERRED]** (lens spec-F2) The amendment set covers at minimum the following, published
  invariant by invariant. Design may add a statement it finds carrying the superseded rule; it may
  not drop one from this list.
  - **Invariant 1** — the halt scope narrows from "any `BLOCK` halts the model" to "`BLOCK` on an
    **asserted** constraint halts the model", and the consequence is written down as a product
    statement: an unsupported predicate inside a plain `constraint` never halts generation,
    because the form gate runs before the predicate walk, and the usage catalogs as unassessed.
    Descriptive constraints are never load-bearing.
  - **Invariants 8/9** — a new generation-halting severity exists for an **asserted, structurally
    unattachable** usage: an in-scope asserted form with no attachment capability. It is a named
    contextual failure, not a fifth profile outcome, and does not reclassify `ADMIT`.
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
  - **Appendix C** — the "Excluded-only usages", "Zero constraint usages", and "Mixed
    satisfied/violated/indeterminate population" cells are amended to the new headline and
    disposition semantics.
  - **Appendix B** — the correction-register row carrying the same superseded claim as the
    Appendix C excluded-only cell ("excluded-only usages retain `not_assessed` visibility") is
    amended with it, so the two do not disagree.
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
  dispatch on the canonical tokens. No amendment in this item names a token spelling as normative;
  where a current spelling is quoted it is quoted as today's text being amended.

### Documentation corrections (D1–D7) and published authoring policy

- **[INHERITED: research §7]** Each defect is corrected at its location. All seven are
  agent-authored text with no OWNER/HARD/ADR marker, so correction by deletion or rewrite is the
  capture-fidelity-correct move (lens ledger, "Not findings" note).

  | # | Location | Required correction |
  |---|---|---|
  | D1 | codegen `docs/architecture/modeling-assumptions.md` (the "what a modeler needing an enforced gate should do" paragraph) | Remove the claim that a bare `constraint` or `require constraint` gives an enforced gate; state assert-only enforcement |
  | D2 | codegen `docs/architecture/modeling-assumptions.md` (unassessed enumeration) | Include `plain_usage`, `require`, and `assume` in the unassessed set, not requirement-side and bad-owner only |
  | D3 | agentic-mbse `docs/subtype-enumeration-decision-table.md` | Delete or rewrite "require/plain are executable constraint usages (lowered under the profile)" |
  | D4 | agentic-mbse `docs/patterns/constraints.md` | Replace the false reason for bare `constraint` being wrong; the parser does produce a `ConstraintUsage`, classified `plain_usage` — the form gate is why it does not execute |
  | D5 | agentic-mbse `claude/agents/sysml-expert.md`, `docs/patterns/semantic-operators.md` | Stop teaching `require constraint` as an equal alternative for a check |
  | D6 | codegen `docs/architecture/reference/28-constraint-lowering-and-catalog.md` | Unassessed status follows source form; owner kind decides occurrence expansion. The axes are independent (contract invariant 16) |
  | D7 | codegen `docs/architecture/modeling-assumptions.md`, `docs/architecture/reference/01-extraction.md` | Remove the citation of the retired `test_constraint_migration_mapping.py` as living totality evidence |

- **[INFERRED]** (D7 boundary) Item 1 removes the dead-evidence citation and states plainly that
  the totality proof is pending. It does **not** re-grade or re-anchor REQ-EXT-09 or REQ-CL-04 in
  `docs/architecture/verification-matrix.md` — those move with the totality gate in Item 2 (lens
  spec-F7).
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
  projection and policy, fixtures, and the predicate defect fixes belong to Items 2–5.
- Choosing the concrete headline token spellings, report schema field names, or the normalization
  seam's code shape — Item 3.
- Designing calculation-definition constraint attachment — Item 6.
- Re-grading or re-anchoring REQ-EXT-09 and REQ-CL-04 in the verification matrix — Item 2.
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

- **ADR home and number.** Decided above as
  `docs/architecture/ADR-009-constraint-coverage-and-headline-semantics.md` on the next-free-number
  and implied-path rationale. Design may relocate it if a better precedent surfaces; it may not
  leave it unfiled. Related unknown: whether the companion repository wants a stub cite next to
  `docs/patterns/adr002-calculations.md`.
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
- **The REQ-EXT-09 window** (lens item1-F6). Item 1 writes "totality proof pending" while
  `docs/architecture/verification-matrix.md` still reads PASS for that row, and the re-grade is
  Item 2's. Design decides between a dated "re-grade pending, CONSTRAINT-SEMANTICS Item 2" pointer
  at the row — an addition, not a re-grade, so it stays inside the non-goal — and accepting the
  window explicitly.

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
- **Design:** `.project/active/constraint-semantics-contract-amendments/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_design`.
