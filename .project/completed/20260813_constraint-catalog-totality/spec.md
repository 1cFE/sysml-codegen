# Spec: Canonical Usage Domain and Catalog Totality

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-08-12
**Complexity:** HIGH
**Branch:** `item7-rebuild` (worktree `/home/reid/1cfe/sysml-codegen-item7-rebuild`; companion
worktree `/home/reid/1cfe/agentic-mbse-item7-rebuild`)
**Epic:** CONSTRAINT-SEMANTICS, Item 2 (`.project/backlog/epic_constraint_semantics_contract.md`)

---

## Problem

The contract already promises that every authored constraint usage stays visible with exactly one
disposition (lifecycle contract invariants 1 and 28). The exact route does not keep that promise,
and it cannot currently be made to keep it by any check written against today's data.

Measured on `catf_mfe_d5`, the richest model
(`.project/research/20260812-101200_constraint-semantics-end-to-end.md` §§2–4, reproduced by a
second agent the same day):

- **65 authored constraint usages produce 9 catalog carriers.** The other 56 are absent — not
  eligible, not excluded, nothing. 51 are owned by a `calc def` and are structurally unreachable
  because `_scopes_for_owner` has no `CalculationDefinition` branch (`elaboration/elaborate.py:522`);
  5 are owned by a `part def` whose design parts are all untyped, so they attach to zero
  occurrences.
- **Records only begin after owner-to-scope expansion.** `_build_constraint_nodes`
  (`elaboration/elaborate.py:997`) enumerates every `ConstraintUsage` in the model, then emits one
  node per scope returned by `_scopes_for_owner`. A usage with zero scopes emits nothing. Every
  downstream artifact — instance graph, embedded catalog, snapshot payload, report — descends from
  that post-expansion set.
- **So a totality gate written against today's data would be circular** (umbrella spec-review
  L3-2). Comparing the graph with its own catalog compares two projections of an
  already-truncated set; the 56 vanished before either existed, so neither can miss them.
- **There is no third disposition kind, no inapplicability mechanism, and no gate.** Invariant 28
  now names `non-reaching-with-reason` and invariant 61 rules the vacuous case at warning grade
  (both landed by Item 1), but nothing in code produces them.
- **The totality requirement rows are green on selection bias.** REQ-EXT-09 reads PASS
  (`docs/architecture/verification-matrix.md:336`) because each specimen fixture happens to have a
  carrier while 56/65 CATF usages have none — the exact shape of a test that passes only because
  it selects one interpretation (lens spec-F7). REQ-CL-04 is PARTIAL for the same obligation
  (`verification-matrix.md:214`).

**[INHERITED: `.project/active/constraint-semantics-contract/spec.md`, Problem]** The product
consequence, and the reason this is worth doing now: constraints are how these models enforce
physics so design search stays viable. Until the graph accounts for every authored usage, every
downstream coverage claim (Item 3), every disposition table (Item 5), and every capability
decision about calc-def gates (Item 6) rests on a population that silently lost 86% of its
members.

## Success Criteria

Carried from the epic's Item 2 section; every entry is
**[INHERITED: `epic_constraint_semantics_contract.md` Item 2 / `constraint-semantics-contract/spec.md`]**
unless marked otherwise. The two sources state the same criteria — the epic's Item 2 success list
is itself marked `[INHERITED: spec.md]` — so the blanket citation names both rather than splitting
per entry. Two additions are marked where they occur.

**Carrier** = one usage-tier record in the canonical authored domain, together with the single
visible disposition attached to it. One carrier per authored constraint usage; a usage with a
record but no disposition, or a disposition with no record, is not a carrier. Per-occurrence
execution entries are a separate tier and are never counted as carriers. This spec uses "carrier"
for that pair throughout.

- [ ] Frozen `catf_mfe_d5` produces exactly **65** usage carriers with zero absence, and its
      authored constraint syntax is unchanged (both twins stay byte-pinned).
- [ ] Removing or duplicating any carrier fails generation with a named, usage-identifying
      completeness diagnostic.
- [ ] An asserted, structurally unattachable fixture halts generation; an asserted, vacuous fixture
      produces the visible warning-grade disposition plus the authoring advisory; a plain
      constraint carrying a predicate that would BLOCK if asserted still generates and catalogs as
      unassessed.
- [ ] The inapplicability mechanism is explicit, fingerprinted, and cannot silently change an
      asserted usage's coverage role.
- [ ] Live, in-place snapshot, and relocated snapshot routes produce the same authored domain and
      the same dispositions; old or malformed snapshot shapes fail closed under the selected
      version rule.
- [ ] REQ-EXT-09 and REQ-CL-04 cite non-self-referential tests that fail if a pre-expansion usage
      vanishes; **[INFERRED]** each row's grade matches that evidence, and REQ-EXT-09's
      domain-versus-carrier self-contradiction is gone.
- [ ] **[INFERRED, from the [NEED] doc-correction obligation and lens spec-F2]** No shipped
      documentation still describes pre-landing behavior: the two Item 1 forward pointers
      (`docs/architecture/modeling-assumptions.md:476-477` and `:489-496`) are corrected before
      confirmation tests run.
- [ ] **[INFERRED, from the manifest-fate requirement and lens spec-F4]** The manifest sweep's fate
      is recorded and executed — retired, or demoted to a test-side oracle with no `src/` caller —
      and the independent totality oracle is named. Neither is left unowned.
- [ ] Focused tests, full licensed codegen and companion suites, `ruff` zero-new, `mypy` zero-new,
      fixture diff review, and `git diff --check` pass, with exact counts recorded in
      `verification.md`.
- [ ] **[AGENT]** If the instance-graph schema changes, exactly one reviewed final-schema fixture
      recapture happens in this item, reviewed under the timestamp-churn diff protocol, and the
      Item 7 evidence-invalidation register still describes what this landing invalidated.

## Known Requirements

### The canonical authored-usage domain

- **[INHERITED: umbrella spec, Pipeline invariants (Q3, spec-review L3-2)]** The authority records
  the **complete authored-usage domain before occurrence expansion**. Every constraint usage the
  model authors is in the domain whether or not it reaches an instance; "reaches no instance" is a
  recorded disposition, never an absence.
- **[INHERITED: contract invariants 40, 48; owner decision D-3, whose verbatim text is “100% Option
  A. We need to purge this mess.” (`contract:503`) and whose recorded consequence is that codegen's
  embedded catalog is canonical with no second catalog authority; lens spec-F4]** One authority owns
  totality: the instance graph and its embedded catalog, the same
  authority live generation and snapshot generation already read. No parallel constraint inventory
  is created or kept in sync by hand, and the completeness gate reads the graph plus the embedded
  catalog rather than a separate sweep.
- **[INHERITED: contract invariants 40, 48; lens spec-F4]** The existing manifest sweep
  (`collect_constraint_manifest`, `extraction/extractor.py:98`) gets an explicit fate in this item.
  It currently defines the population both requirement rows cite, and ELABORATE-FIRST Item 7 is
  deleting the dual constraint-fact extraction pass. After this landing it is either retired, or
  kept solely as a test-side independent oracle that no generation path consults — never a second
  representation the graph must be kept in sync with. Which of the two is design's call; leaving it
  unowned is not.
- **[INFERRED]** Whichever fate design picks, **an independent totality oracle must exist** — some
  enumeration of the authored population that is not derived from the domain it checks (see the
  non-self-referential evidence requirement under *The completeness gate*). Today
  `collect_constraint_manifest` is the only such enumeration, it has no caller in `src/`, and both
  requirement rows plus `docs/architecture/modeling-assumptions.md:489-492` define the population
  by it. So "retire the sweep" and "prove totality independently" are coupled: design resolves the
  fate and names the oracle together, and may not close the first while leaving the second open.
- **[HARD]** Exact declaration identity is preserved. Constraint identity in this codebase is
  `DeclarationId` / `NodeId` plus the qualified names already carried on `ConstraintNode`
  (`elaboration/graph.py:194-219`), and the snapshot codec already refuses a record whose identity
  fields disagree (`snapshot/instance_graph.py:776`). The domain uses that identity vocabulary; it
  does not introduce qualified-name string matching.
- **[INHERITED: epic Item 2 scope 1; contract invariant 28's carried-field list]** Form
  classification is preserved on every domain member, anchored on **the exact route's own
  classifier** — `_constraint_metadata` (`elaboration/elaborate.py:1119-1137`), which emits exactly
  five source forms: `requirement_constraint`, `named_usage_reference`, `definition_typed`,
  `inline`, and the `plain_usage` fall-through. Owner kind, owner qualified name, source file, and
  source line are preserved alongside it. The legacy constraint-fact pass in the companion repo
  (`agentic_mbse/sysml/constraint_extraction.py`) is not the anchor: ELABORATE-FIRST Item 7 scope 2
  is deleting it (`epic_elaborate_first_architecture.md:444`), and building this domain against a
  module scheduled for deletion is the failure mode this item exists to prevent.
- **[INHERITED: umbrella spec, Modeling policy (Q7)]** The named `satisfy` exclusion is **new
  classification work this item adds**, not preserved behavior. There is no `satisfy` source form
  in the exact route today: a `SatisfyRequirementUsage` reaching `_constraint_metadata` falls
  through to `plain_usage` and is indistinguishable from a bare `constraint`. Q7 requires an
  out-of-scope form to carry a *named* visible exclusion, so satisfy must be newly distinguished
  before that exclusion can be named.
- **[INHERITED: contract invariant 28 + LC-E05]** Each usage-tier record also carries the
  definition qualified name and the explicit definition-to-usage join. The per-occurrence tier
  already carries both (`resolution/models.py:397-401, 492-497`); without them on the usage tier,
  a definition-typed asserted gate that never reaches an instance loses the name of the
  `constraint def` that went unassessed.
- **[INFERRED]** The domain's membership boundary is stated explicitly, in the requirement rows and
  in the code that builds it. **REQ-EXT-09 contradicts itself today**
  (`docs/architecture/reference/01-extraction.md:20`): the row excludes `RequirementUsage` and its
  `satisfy` subtype from the swept *domain*, then lists "a named requirement/satisfy exclusion" as
  an admissible *carrier* — a form cannot be outside the domain and carry a disposition inside it.
  The umbrella spec's Q7 ruling requires out-of-scope forms, `satisfy` included, to be visible. So
  the conflict design resolves is internal to the row, and a row rewrite is the likelier fix than a
  domain-boundary change. Parked here in full, not decided.

  This parked question **cannot move the headline 65**: `catf_mfe_d5` authors no `satisfy` and no
  requirement usage (verified in this item's product-lens ledger). Either resolution leaves the
  fixture's authored population at 65.

### Dispositions

- **[INHERITED: contract invariant 28 + LC-E05]** Exactly one visible disposition per authored
  usage, of exactly three kinds: eligible, excluded-with-reason, or non-reaching-with-reason. Zero
  dispositions is a failure; two dispositions for one usage is a failure. **Vocabulary note:** epic
  Item 2 scope 2 spells the first kind `executable` (`epic:289-290`) where contract invariant 28
  and the umbrella spec spell it `eligible` (`contract:223-224`). They name the same kind; the
  contract governs, and `eligible` also matches the existing `Eligibility` field on `ConstraintNode`
  (`elaboration/graph.py:201`). Exact token spellings remain design's, within that vocabulary.
- **[INHERITED: umbrella spec, Report and coverage contract (Q5, two-tier accounting)]** Usage-level
  inventory and per-occurrence execution entries stay separate records. One usage may own many
  concrete entries; the inventory counts usages, the results list occurrences.
- **[INHERITED: umbrella spec (Q3); contract invariants 9, 61]** Severity by cause:
  - asserted **and** structurally unattachable (in-scope form, no attachment capability) is a
    generation-halting error whose diagnostic names both the usage and the missing attachment, per
    invariant 9;
  - asserted **and** vacuous (owner has zero occurrences) is a warning-grade disposition plus an
    authoring advisory naming the usage and its detached owner — not a halt, not a silent pass.
    Per invariant 61 and LC-E13 that advisory is emitted by authoring validation at warning grade;
    this item implements that, it does not reopen it;
  - plain and out-of-scope forms are visible records and never errors.
    - **[AGENT]** (audit-accepted 2026-08-12, orchestrator-ratified; `audit.md` A3 / R2) —
      **one named exception, recorded beside the inherited line rather than reworded into it.**
      The inherited sentence above grades severity by **form**, and it stands for every cause the
      umbrella Q3 line was reasoning about. A **malformed `@inapplicable:` directive** is a
      distinct cause: not a fact about the model, but a defect in an instruction the author wrote
      to the tool. Such a usage grades `non_reaching` / `classification_incomplete` at `error` and
      halts by name **whatever its form**, including a plain one. Silently ignoring it would be
      indistinguishable from never having written it — the absence-not-disposition failure this
      item exists to end. **This overrides an `[INHERITED]` line and the owner should see that**:
      the umbrella spec itself is not touched, and its Q3 rule is unchanged for form-caused
      severity.
- **[INFERRED]** The severity rule keys on **form and cause together**, so `catf_mfe_d5` still
  generates after this item: its 51 calc-def-owned and 5 part-def-owned usages are all bare
  `constraint`, so they become visible records, not halts. The halting path is reachable only once
  a usage is asserted.
- **[INHERITED: contract invariant 61; umbrella spec-review L2-2]** A vacuous asserted gate counts
  as missing assessment until it carries an **explicit inapplicability disposition**. This item
  owns the mechanism; the coverage consequence of carrying one belongs to Item 3.
- **[INHERITED: umbrella spec, scope item 4 / L2-2]** The inapplicability mechanism must be:
  explicit (a recorded decision, never inferred from absence), carried by the single authority
  above with no second hand-maintained inventory, covered by the sealing fingerprints so a change
  to it is visible, and incapable of silently changing an asserted usage's coverage role. The
  mechanism *choice* — model annotation versus reviewed catalog-level acceptance — is deferred to
  this item's design.

### The completeness gate

- **[INHERITED: umbrella spec (Q3)]** A generation-time completeness gate fails generation on any
  authored usage without a disposition.
- **[INHERITED: umbrella spec-review L3-2]** The gate is non-circular: it compares dispositions
  against the pre-expansion authored domain, never two projections of the same already-truncated
  set.
- **[INHERITED: epic Item 2 scope 5]** Mutations that **remove**, **duplicate**, or **misjoin** a
  disposition fail generation. The diagnostic names the offending usage well enough to find it in
  the source — identity plus qualified name, not a bare count mismatch.
- **[INFERRED]** The gate's own evidence is independent of the gate. A test that only asserts the
  gate agrees with itself does not discharge the totality requirement; the totality tests assert an
  expected authored population that fails if a pre-expansion usage vanishes.

### Carriage: codec, snapshot, and sealing

- **[HARD]** The authored domain and its dispositions travel through the instance-graph codec
  (`snapshot/instance_graph.py`), the snapshot envelope, and the sealing fingerprints. The codec
  fingerprints the whole graph document and refuses a schema it does not know
  (`instance_graph.py:88, 907, 927`), so any added field is a schema change, not an additive
  free ride.
- **[INHERITED: epic Item 2 success criteria]** Live, in-place snapshot, and relocated snapshot
  routes produce the same authored domain and the same dispositions. Old or malformed snapshot
  shapes fail closed under the selected version rule (the current constant is
  `instance-graph/v2`); the version rule for this change is design's call, the fail-closed
  behavior is not.
- **[INHERITED: `epic_elaborate_first_architecture.md` Item 7 scope 3; epic Item 2 scope 6]** If the
  representation changes the snapshot schema, this item performs **one** reviewed final-schema
  recapture, under the timestamp-churn diff protocol (a full recapture rewrites every
  `captured_at`, so the review is a timestamp-only diff check followed by reverting untouched
  fixtures). Item 7 then consumes these bytes.
- **[INFERRED — count discrepancy, surfaced not resolved]** The epic and the Item 7 register both
  say "37 fixtures"; at HEAD this tree holds **21** `instance_graph_snapshot.json` fixtures across
  **96** fixture directories. The likely explanation, visible in the source: 37 is the **corpus row
  count** (`epic_elaborate_first_architecture.md:302` "All 37 fixtures have live-checked route
  outcomes"; `:378` "corpus 37/37"), while 21 is the snapshot-bearing subset. If the Item 7
  obligation means "recapture every snapshot that exists," 21 is right; if it means "the 37-row
  corpus must be snapshot-covered," then 16 corpus fixtures lack snapshots and this item's
  recapture scope grows — a real scope change, not a counting detail. **The requirement, stated so
  neither reading is picked silently:** the recapture covers every snapshot-bearing fixture in the
  tree, counted at execution and recorded in `verification.md`; whether the corpus reading adds the
  16 is design's call, made explicitly. The 37 figure is not a target to hit.
- **[INHERITED: `.project/active/cutover-recovery/plan.md`, PAUSED at step 4; lens spec-F8]** This
  landing must not silently invalidate more paused Item 7 evidence than the epic's
  evidence-invalidation register already records. Anything newly invalidated is added to that
  register in this item, not discovered later.

### Requirement rows and evidence

- **[INHERITED: lens spec-F7]** REQ-EXT-09 is re-graded and its proof re-anchored in this landing;
  its current PASS rests on specimen fixtures that each happen to have a carrier.
- **[INHERITED: epic Item 2 scope 7]** REQ-CL-04 is re-anchored to the same independent totality
  evidence and its PARTIAL note is replaced by what the new tests actually prove.
- **[HARD]** `catf_mfe_model`'s ratified corpus row pins its refused shape and `catf_mfe_d5` is
  byte-reversal-pinned to it (`tests/.../test_d5_variants.py:29`). Neither twin's constraint syntax
  changes in this item — the 65 carriers must appear with the fixture exactly as authored.
- **[NEED: owner-directed sequence, umbrella spec]** Documentation is corrected and expected
  outputs are captured **before** confirmation tests run; test expectations are never
  reverse-engineered from current behavior. Item 1 deliberately left two forward pointers naming
  this item — `docs/architecture/modeling-assumptions.md:476-477` ("today a usage that reaches no
  instance gets no carrier at all") and `:489-496` (the pending totality proof) — and this landing
  falsifies both. They are corrected here, alongside the requirement rows.
- **[INHERITED: epic Item 2 success criteria]** Verification records exact counts: focused tests,
  full licensed codegen and companion suites (licensed means `SYSIDE_LICENSE_KEY` sourced from
  `/home/reid/1cfe/agentic-mbse/.env` and zero license-skip lines), `ruff` zero-new, `mypy`
  zero-new, fixture diff review, `git diff --check`.

## Non-Goals

- Report headline vocabulary, coverage schema, TEAx projection, and study policy — Item 3. This
  item provides the inventory; Item 3 owns the feasibility denominator and everything the report
  says about it.
- Executing calculation-definition-owned gates — the capability Item 6 designs. Here those usages
  receive dispositions, not execution.
- Any parallel manifest or catalog inventory kept in sync with the graph.
- The four `all_satisfied` assertions in codegen `tests/execution/` — handed to Item 3 by Item 1's
  audit; not touched here.
- The CATF derivative migration and the all-65 owner disposition table — Item 5.
- The `[m]`-unit-literal elaboration defect and the tautological feature-chain diagnostic —
  Item 4.
- Changing BLOCK-halts-generation semantics, or migrating the frozen CATF twins in place.
- Re-planning ELABORATE-FIRST Item 7; its narrow-correction steps remain the plan of record.

## Open Questions / Deferred to design

- **Vacuous-inapplicability mechanism** (umbrella L2-2): model annotation versus reviewed
  catalog-level acceptance. The requirements it must meet are stated above; the choice is design's.
- **The gate's mechanical home** — extraction-time versus generation-preflight — and how it
  composes with the four existing generation preflights and the ledger checks.
- **The domain's representation**: a new node/record kind in the instance graph versus a
  usage-level record alongside the existing per-occurrence `ConstraintNode`s. Design names the
  single owning representation and shows the join to per-occurrence entries.
- **Snapshot version rule**: whether `instance-graph/v2` bumps, and what the fail-closed rule is
  for the in-between shapes.
- **Disposition-kind and reason token spellings**, and how they align with the schema names Item 3
  will read. Item 3 consumes these; a spelling chosen here without that coordination costs a second
  schema change.
- **How REQ-EXT-09's internal contradiction is fixed** — a row rewrite that reconciles its excluded
  domain with the requirement/satisfy carrier it already admits, or a domain-boundary change (see
  the domain-boundary requirement above). The decision belongs to design; leaving it implicit does
  not. Either way it cannot move the 65.
- **The manifest sweep's fate and the independent totality oracle, decided together** — retire or
  demote, and what enumerates the authored population independently of the domain under test.
  Design may not close one and leave the other open.
- **Whether the recapture covers the 16 corpus fixtures that carry no snapshot** (see the count
  requirement above) — a scope decision, made explicitly and recorded.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_constraint_semantics_contract.md` (Item 2)
- **Required Reading:**
  - `.project/active/constraint-semantics-contract/spec.md` — umbrella behavioral contract
  - `.project/research/20260812-101200_constraint-semantics-end-to-end.md` §§2–4
  - `.project/active/constraint-semantics-contract/product-lens.md` — spec-F4, spec-F7, spec-F8
  - `.project/backlog/epic_elaborate_first_architecture.md` — Item 7 single-authority and recapture
    obligations
  - `.project/active/cutover-recovery/plan.md` — paused step-4 evidence
- **Item 1 landed authority:**
  `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md` (invariants 28, 48,
  61 and Appendix C's "Asserted vacuous gate" cell), its frozen companion
  `.project/concepts/constraint-execution-lifecycle-requirements.md` (LC-E05, LC-G07, LC-E13), and
  ADR-009 in `docs/architecture/modeling-assumptions.md` §9
- **Product-lens ledger:** `.project/active/constraint-catalog-totality/product-lens.md` — spec
  stage, Gate DISPOSED (spec-F1..spec-F5, none blocking); dispositions recorded there and applied
  above. Epic gate: CONSTRAINT-SEMANTICS, CLEAR (epic-plan stage, grade preserved).
- **Design:** `.project/active/constraint-catalog-totality/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_design`.
