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
unless marked otherwise.

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
      vanishes, and each row's grade matches its evidence.
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
- **[INHERITED: contract invariants 40, 48; D-3 owner-verbatim "no second catalog authority"; lens
  spec-F4]** One authority owns totality: the instance graph and its embedded catalog, the same
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
- **[HARD]** Exact declaration identity is preserved. Constraint identity in this codebase is
  `DeclarationId` / `NodeId` plus the qualified names already carried on `ConstraintNode`
  (`elaboration/graph.py:194-219`), and the snapshot codec already refuses a record whose identity
  fields disagree (`snapshot/instance_graph.py:776`). The domain uses that identity vocabulary; it
  does not introduce qualified-name string matching.
- **[INHERITED: umbrella spec, Modeling policy (Q1, Q7)]** Form classification is preserved on
  every domain member: the five source forms produced by
  `agentic_mbse/sysml/constraint_extraction.py:703-723` (`inline`, `definition_typed`,
  `named_usage_reference`, `requirement_constraint`, `satisfy`, and the `plain_usage`
  fall-through), together with owner kind and owner qualified name, source file, and source line.
- **[INHERITED: contract invariant 28 + LC-E05]** Each usage-tier record also carries the
  definition qualified name and the explicit definition-to-usage join. The per-occurrence tier
  already carries both (`resolution/models.py:397-401, 492-497`); without them on the usage tier,
  a definition-typed asserted gate that never reaches an instance loses the name of the
  `constraint def` that went unassessed.
- **[INFERRED]** The domain's membership boundary is stated explicitly, in the requirement rows and
  in the code that builds it. Today's REQ-EXT-09 wording sweeps `ConstraintUsage` including
  subtypes but excludes `RequirementUsage` and its `satisfy` subtype
  (`docs/architecture/reference/01-extraction.md:20`), while the umbrella spec's Q7 ruling requires
  out-of-scope *forms* — including `satisfy` — to carry a named visible exclusion. The domain
  boundary this item lands must cover every form the umbrella spec requires to be visible, and the
  re-anchored rows must say so in words rather than leaving the difference implicit.

### Dispositions

- **[INHERITED: contract invariant 28 + LC-E05]** Exactly one visible disposition per authored
  usage, of exactly three kinds: eligible, excluded-with-reason, or non-reaching-with-reason. Zero
  dispositions is a failure; two dispositions for one usage is a failure.
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
  say "37 fixtures". At HEAD this tree holds **21** `instance_graph_snapshot.json` fixtures
  (`tests/fixtures/*/instance_graph_snapshot.json`). The obligation is one reviewed recapture
  covering every snapshot fixture in the tree; the exact count is recorded in `verification.md` at
  execution, and the 37 figure is not treated as a target to hit.
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
- **Where the authoring advisory surfaces** for the vacuous case (elaboration diagnostic stream
  versus authoring validation in the companion repo), and at what grade it is recorded.
- **Whether the re-anchored REQ-EXT-09 row keeps its current membership boundary or adopts the
  umbrella spec's wider one** (see the domain-boundary requirement above) — the decision belongs
  to design; leaving it implicit does not.

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
