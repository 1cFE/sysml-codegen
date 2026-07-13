# Spec: Concrete Constraint Lowering — New Phase, Strict Resolution, Execution IDs

**Status:** Draft (revised after spec-review — must-fixes discharged)
**Owner:** Reid W
**Created:** 2026-07-12
**Complexity:** HIGH
**Branch:** constraint-exec-epic
**Epic:** CONSTRAINT-EXEC — Item 5

---

## Problem

Modeled assertions (`assert constraint`) are extracted and classified, then die at a
drop-report warning. Their predicates, bindings, and concrete design context never reach
generated code. Upstream epic items have now built everything lowering needs: the neutral
constraint facts (Item 1), the expression tree (Item 2), the part-instance index (Item 4),
and `module_kind` (Item 6). What is still missing is the sysml-codegen phase that turns
those facts into graph structure: expand each assertion into its concrete design instances,
resolve every actual to a real producer channel or a real design attribute, keep the
producer alive against pruning, and give each concrete assertion a stable execution
identity.

The S4 vertical-slice spike proved this whole seam works on one real model with test-only
code (`.project/active/spike-vertical-slice-constraint-execution/s4_lib.py`). This item
productionizes that proven shape. It stops at graph structure and catalog identity; emitting
the constraint modules, the Kleene predicate compiler, and the aggregator is Item 7.

Two known traps shape the work:

- **The strict-resolution trap.** Entry-point resolution today lives inside the backtracker
  and falls through to *synthesizing* an entry point when it can't resolve an input, caught
  only by a late boundary check. Assertion actuals must never take that path — an unresolved
  actual is a generation error, never a synthesized value. The backtracker's fallback is not
  a drop-in: it collapses distinct entry-point keys (the F4-cutover lesson, memory:
  `f4-cutover-fallback-divergence`).
- **The silence trap.** This project has repeatedly been bitten by things vanishing quietly.
  Every assertion must end in a visible place: a lowered graph node, or a named generation
  error. No path may drop one.

## Success Criteria

The first four are the epic's acceptance bar. The last two were surfaced by spec review as
new surfaces S4 never exercised — they are stated as their own criteria so they can't be
mistaken for already-proven.

- [ ] **S4 behavior reproduced by production code.** With pruning enabled and a minimal exit
      selection, the control run (no lowering) prunes `cost_calc`; the lowered run retains it
      — and *only* via the resolved constraint input channel joined as a backtracking root,
      not because every output feeds the exit.
- [ ] **Strict resolution has no fallback.** V11 coverage and channel-reference validation
      pass on the extended graph; no fallback path executes for a constraint actual. Probe:
      an unresolvable actual produces a generation error that names the actual — never a
      synthesized entry point.
- [ ] **Deterministic identity.** `constraint_id`s and catalog ordering are byte-identical
      across repeated live loads.
- [ ] **Corpus byte-identity.** The existing fixture corpus (no constraints admitted to the
      executable profile) regenerates byte-identically (timestamps excepted). The new phase
      is inert when nothing is lowered.
- [ ] **Multi-instance expansion (new — not proven by S4).** A committed multi-occurrence
      fixture (Item 4's promoted S3 `[3]`-expansion shape, or equivalent) expands to three
      concrete constraints with three distinct `constraint_id`s, three distinct evaluation
      channels, **and** each sibling's actuals resolved in its *own* occurrence scope — three
      wired nodes, not copies of one. S4 ran on a single-instance model (`wi014_toy`,
      `demo_plant`); this whole path is new.
- [ ] **Inline source form lowers (new — S4 did only definition-typed).** A committed fixture
      whose assertion owns its predicate inline (`ConstraintSource.form == "inline"`) lowers
      correctly, selecting the effective predicate from the usage rather than a definition.

## Known Requirements

### The two orthogonal classification axes

The landed facts (`constraint_facts.py`) classify every usage on **two independent axes**.
Keeping them separate is the spine of this spec — conflating them is what the spec review
caught, and what a design agent will slip on if the axes aren't named up front.

- **[HARD]** **Owner-kind axis** — `ConstraintUsageFact.owner.owning_definition.kind`
  (`OwningDefinitionFact.kind`, `constraint_facts.py:52-63`). One of four values, resolved by
  walking `owner` up to the first enclosing definition/package. This axis drives **expansion
  cardinality** (how many concrete instances one source assertion becomes).
- **[HARD]** **Source-form axis** — `ConstraintUsageFact.source.form` (`ConstraintSource`,
  `constraint_facts.py:73-91`). This axis drives **which predicate is effective and where it
  lives** — read the `source.effective_predicate_source` pointer, never inferred from the
  owner axis.

The two are orthogonal: a `part_def`-owned assertion may be `inline` or `definition_typed`;
so may a `calc_def`-owned one. Every rule below dispatches on exactly one axis; the spec says
which.

### Expansion — dispatch on the owner-kind axis (four values)

- **[HARD]** Expansion dispatches on `owning_definition.kind` and handles **all four** landed
  values — no prose category may stand in for the real field. The dispositions:
  - **[INFERRED]** `part_def` → expand **once per concrete part instance**, via Item 4's
    index (`PartInstanceIndex.occurrences_of`). Inherited assertions land here too (the fact
    carries `inherited_into`).
  - **[INFERRED]** `calc_def` → expand **once per concrete calc usage** (existing calc-usage
    discovery, not the part index).
  - **[INFERRED]** `package` → the assertion is directly owned at package/top level and is
    **already concrete**: expand **once**. (This is what the review brief called
    "direct-usage-owned"; the landed field spells it `package`, because a top-level usage's
    owner-walk terminates at its enclosing `Package`.)
  - **[INFERRED]** `requirement_def` → **catalog-unassessed territory**, never an execution.
    Requirement-owned constraints (require/assume) and satisfy usages live here. Expected
    disposition: Item 3's profile filters these out upstream, so in the normal path lowering
    never sees one. If one nonetheless reaches lowering, it is cataloged **unassessed** (its
    kind stated), **not** expanded to an executable node and **not** silently dropped
    (Design Principle 5). The design must state which — filter-assumed vs. defensively
    cataloged — and, if defensive, where the unassessed record goes.

  *(Provenance note: the concept's expansion prose (line 94) and epic §2 name only `part_def`
  and `calc_def`. The four-value dispatch is forced by the landed fact, so the requirement to
  enumerate all four is `[HARD]`; the per-kind disposition is `[INFERRED]` from the concept's
  ownership taxonomy (concept line 268) and this revision's brief — not `[INHERITED]`.)*

- **[INHERITED: concept Required Invariant "Semantics and Identity"; epic §2]** An expected
  concrete instance that cannot be formed is a **validation error**, not a warn-and-drop.
- **[HARD]** A constraint-owning part definition whose instance expansion hits a non-finite
  multiplicity must surface as a generation error, never a silent omission. Item 4's per-owner
  `occurrences_of` raises `NonFiniteCardinalityError`; its bulk API reports these in
  `AllOccurrencesResult.blocked` / `SourceOwnersResult.blocked`. Whichever entry point
  lowering uses, a blocked constraint owner must not vanish (the Item 4 audit cure exists
  precisely so this cannot be swallowed).

### Effective predicate — dispatch on the source-form axis

- **[HARD]** Select the effective predicate per `source.form` via
  `source.effective_predicate_source`, not by guessing from the owner axis:
  - `inline` → predicate on the **usage** (`ConstraintUsageFact.predicate`).
  - `definition_typed` → predicate on the **definition**
    (`ConstraintDefinitionFact.predicate`), evaluated in usage scope with the usage's actuals
    bound to the definition's formals.
- **[INHERITED: concept "executable profile", line 90]** **Both** `inline` and
  `definition_typed` are in the first-scope executable profile. S4 hard-coded
  `source_form="definition_typed"` and never exercised inline; this item must lower both.
  (Fixture required — see Success Criteria.)
- **[INFERRED]** Other forms (`named_usage_reference`, `satisfy`, `plain_usage`,
  `requirement_constraint`) are out of the first-scope executable profile and are Item 3's to
  block/catalog upstream; lowering treats them as it treats `requirement_def`-owned kinds —
  never a silent drop if one arrives.

### Strict resolution — one ordered decision procedure per formal

- **[INFERRED]** Resolve each formal through **one shared resolver seam with an explicit
  strict mode**, as a single ordered decision — *not* a chain-vs-reference split (a "chain" is
  just a multi-segment `FeatureReferenceFact` with non-empty `chain_segments`; a plain
  owner-scope reference is the single-segment case, and the concept admits owner-scope
  references, line 90/96). The order, per formal:
  1. **The formal has an actual** (an `ActualFact` in `usage.actuals` whose `formal_targets`
     name it, carrying a `FeatureReferenceNode` value):
     a. **Output registry, owner-instance scope** — `OutputRegistry.scoped_lookup`
        (`output_registry.py:186`) keyed by the reference in the owning instance's scope.
        This handles **both** single-segment references and `chain_segments` chains. Resolves
        to a producer channel.
     b. **Else design attributes** — match the reference target QN against design attributes;
        on a hit, mint a `DESIGN_ATTRIBUTE` entry point (see minting discipline below).
     c. **Else generation error** naming the actual.
  2. **The formal has no actual** and is in `usage.omitted_default_formals`
     (`constraint_facts.py:135`) with a modeled default (`FormalFact.has_default`,
     `FormalFact.default`): it becomes an **overridable contract parameter** retaining the
     modeled default — eligible for explicit study selection, never an automatic study
     variable.
  3. **Else** (no actual, no default): generation error.
- **[INFERRED]** Registry-scope-before-design-attribute is a **deliberate** order, not S4's
  incidental one. S4's `_resolve_actual_strict` tried design-attribute first for plain
  references and channel-only for dotted chains (`s4_lib.py:288-326`); this revision pins the
  unified order above so an in-profile owner-scope reference to a sibling calc output is not
  mis-routed to a design attribute. Design owns confirming this precedence against the corpus.
- **[HARD]** **Unresolved is a generation error — never synthesis.** No textual fallback, no
  entry-point synthesis for a constraint actual. Forced by the existing backtracker fallback
  being unsafe here: it emits a bare `{module_eqn}__{leaf}` entry point that collapses
  distinct params and churns baselines (memory: `f4-cutover-fallback-divergence`). The strict
  seam must not reuse that fallback as a drop-in; the strict and lenient (calc) modes should
  be one code path with an explicit switch so they cannot silently diverge again.

### Minted entry-point discipline (the F4-safe positive rule)

- **[INFERRED]** A minted `DESIGN_ATTRIBUTE` entry point is keyed by the **design attribute's
  real qualified name**, and deduplicated against existing group parameters **by QN**: an
  already-present QN is **reused, not re-minted and not a collision** (S4 `s4_lib.py:496,504`).
  This is exactly why minting is F4-safe — the key is a globally-unique attribute QN, and an
  attribute already exposed as an entry point (because a calc also consumes it) is the *same*
  parameter, not a clash. The EP lands in the attribute's derived parameter group
  (`group_deriver`).

### Nullable-fact handling

- **[HARD]** `ConstraintUsageFact.is_negated` and `.membership_kind` are both nullable
  (`bool | None`, `str | None` — `constraint_facts.py:132-133`). Lowering derives
  `expected_value` from negation and folds membership kind + polarity into `constraint_id`, so
  a `None` in either would silently poison both the expected value and ID determinism. The
  executable profile is expected to guarantee an asserted, polarity-known usage; if a `None`
  nonetheless reaches lowering, it is a **generation error** naming the field and the usage —
  never a defaulted guess.

### Roots before pruning

- **[INHERITED: concept; epic §4; S4-proven]** Each resolved constraint **input channel**
  joins the backtracking roots via the production `_find_usage_for_channel` seam
  (`dependency_backtracker.py:466`) **before pruning**, so a calculation whose only consumer
  is an assertion stays in a targeted graph. S4 proved this exact seam.

### Phase placement — the call-site and its three threading points

- **[HARD]** Lowering integrates into `build_pipeline_context`
  (`orchestration/pipeline_builder.py:685`), **not** as a single opaque "phase before
  backtracking." It threads through three points, in order:
  1. **Resolve** actuals after **Step 5.65** `materialize_supplied_values` (~line 808) and
     **Step 5.7** `group_deriver` (~line 831) — the output registry and the graph-only
     `design_attrs` copy are final here, and the deriver is needed to place minted EPs in
     their derived groups.
  2. **Inject** the resolved constraint input channels as roots into the **Step 6**
     `backtracker.find_required_modules(...)` target list (~line 841), before pruning.
  3. **Extend** the graph after **Step 7** `build_computation_graph` (~line 889) with the
     constraint + report-aggregator nodes and the minted entry points.
  S4's `generate_s4_package` demonstrates exactly this three-point threading.

### Extended graph and validation

- **[INFERRED]** Lowering produces the **extended `ComputationGraph`**: constraint module
  nodes (`module_kind=CONSTRAINT`, one per concrete assertion, each with its own evaluation
  channel) and one report-aggregator node (`module_kind=REPORT_AGGREGATOR`), plus the minted
  entry points joined into their groups. This is graph *structure* only — Item 7 emits the
  module Python, the Kleene compiler, the aggregator schema, and the catalog runtime from it.
  (Reasoning: the epic's "V11 coverage and channel-reference validation pass on extended
  graphs" needs the constraint consumers present to cover the minted entry points; S4's
  `extend_graph` — the productionized shape — builds exactly these nodes and runs exactly
  these validations. See the Open Question on the Item 5 / Item 7 line.)
- **[HARD]** `PipelineModule.module_kind` is required (Item 6, `models.py:193`). Constraint
  and report-aggregator nodes set it; they carry no `calc_def_qualified_name`, so any seam
  assuming one must already dispatch on `module_kind` (Item 6 made the four calc-shaped seams
  do so).
- **[INHERITED: concept; epic success criteria]** The extended graph passes
  `_validate_channel_references` (`graph_builder.py:641`) and has zero V11 uncovered
  parameters (`collect_uncovered_params`, `graph_builder.py:800`).

### Identity

- **[INHERITED: concept "Concrete Lowering"; epic §5]** `constraint_id` is the **execution
  identity**: source-local identity + concrete owner-instance identity + membership kind +
  polarity, scoped to one executable fingerprint. Deterministic; catalog ordering
  deterministic by ID.
- **[HARD]** **Source-local identity uses the landed `LocationFact`, not a de-novo ordinal.**
  Item 1 shipped `LocationFact` (`file`, `line`, `column` — `constraint_facts.py:42-49`)
  documented `[HARD]` as "an anonymous assertion's only identity," carried on every
  `ConstraintUsageFact.location`. Source-local identity is the usage's name
  (`identity.name` / `qualified_name`) when named, and `LocationFact` when anonymous. Location
  is stable across repeated live loads of the same source (satisfies the determinism
  criterion) and moves on edits (satisfies the no-cross-version-stability caveat below) — it
  *is* the source-local identity, so lowering must not invent an ordinal scheme while a
  certified `[HARD]` field already fills the role.
- **[INHERITED: concept; epic §5]** A `constraint_id` **collision is a generation error**.
- **[INHERITED: S3 carry-forward (3); epic §5]** Fixed-multiplicity siblings each get their
  **own channels** — structurally identical siblings must not share an evaluation channel, or
  their verdicts become copies. Item 4's index already gives each occurrence its own identity
  (`InstanceOccurrence.instance_path` with per-step `occurrence_index`).
- **[INHERITED: concept; epic §5]** Support an optional author-controlled **`tracking_key`**
  for cross-version correlation. Names enable correlation, not equivalence; anonymous
  assertions have identity only within a fingerprint. No `constraint_id` scheme (nor the
  `LocationFact` it uses) is advertised as cross-version-stable — that is `tracking_key`'s
  job. (Fingerprint construction itself is Item 9.)

### Byte-identity discipline

- **[HARD]** Parity gates compare against the exact function being replaced or extended, not a
  downstream proxy (the F4-cutover comparand lesson). The corpus regenerates byte-identically
  under the established timestamp-only-diff-check + revert discipline (memory:
  `byte-identity-captured_at-churn`).

## Non-Goals

- **Module and aggregator emission** — the Kleene predicate compiler, the constraint module
  `.py`, the aggregator schema, the catalog runtime assembly, and the registry wiring are
  Item 7. This item stops at graph structure + `ConcreteConstraint` data + identity.
- **The generated-class identity mechanism** (class-per-concrete-assertion vs. id-injection)
  is Item 7's design decision, taken together with the measured aggregator-schema scale limit
  (S4 carry-forward (4)). This item wires one *graph node* per concrete assertion; how those
  nodes render to Python classes is Item 7.
- **Snapshot round-trip** of constraint facts and live/snapshot ID parity — Item 8. This item
  proves determinism across repeated *live* loads only (S3's boundary; snapshot re-derivation
  parity is Item 8's burden).
- **Profile eligibility decisions** — Item 3 has already gated what reaches lowering. This
  item assumes every fact it receives is profile-admitted and does not re-check eligibility;
  its only obligation toward out-of-profile kinds/forms is to never silently drop one.
- **Fingerprint sealing and contracts** — Item 9.

## Open Questions / Deferred to design

- **The Item 5 / Item 7 line.** This spec reads Item 5 as producing the extended
  `ComputationGraph` (constraint + report-aggregator *nodes*, minted entry points, joined
  roots) plus `ConcreteConstraint` data, with Item 7 emitting all code from it — because the
  epic's V11-on-extended-graph criterion needs the consumer nodes present and S4's
  productionized `extend_graph` builds them. Design should confirm this boundary against Item
  7's spec and decide which fields of the constraint `PipelineModule` nodes Item 5 sets versus
  leaves for Item 7 (the node's `module_type`/`name` sit near Item 7's generated-class
  identity decision).
- **Per-occurrence input-channel resolution.** For multi-instance part expansion, distinct
  evaluation channels are necessary but not sufficient. Design must pin that each sibling's
  actuals resolve to a **distinct producer channel in that sibling's own occurrence scope**
  (via `scoped_lookup` keyed by the occurrence's `instance_path`), not one shared input
  channel with only the evaluation channels differing. This is the highest-risk new surface
  and its correctness is what the multi-occurrence fixture must catch.
- **`requirement_def` / out-of-profile disposition.** Whether lowering *assumes* Item 3
  filtered these upstream (and errors if surprised) or *defensively catalogs* them unassessed
  — and, if defensive, where that unassessed record lives before Item 7's catalog exists.
- **`constraint_id` string encoding.** The components are fixed (source-local identity —
  name or `LocationFact` — + owner-instance identity + membership kind + polarity); the exact
  serialization is design's, with the constraint that it stays byte-stable across repeated
  live loads and is never advertised as cross-version-stable.
- **`tracking_key` authoring surface.** The landed `ConstraintUsageFact`
  (`constraint_facts.py:124-138`) has **no** `tracking_key` field, and Item 1 is CERTIFIED. So
  "arrives on the Item 1 fact" is not a free option — the realistic space is (a) read at
  lowering from some other authoring surface, or (b) a scoped Item 1 extension with its own
  re-certification cost. Design should name which, not assume the fact carries it. Low
  leverage for the core lowering path.
- **Modeled-default contract-parameter representation.** S4 explicitly did not exercise
  modeled-default formals ("refusing to guess", `s4_lib.py:542`). The coverage rule reads
  `omitted_default_formals` + `FormalFact.has_default`/`FormalFact.default`; the concept fixes
  the outcome (an overridable contract parameter retaining the default, not an automatic study
  variable); the graph/entry-point representation of that parameter is design's.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_constraint_execution.md` (Item 5)
- **Spec review:** `.project/active/constraint-lowering/spec-review.md`
  (Approved-with-must-fixes; this revision discharges L1-1, L1-2, L1-3, L1-4, L1-5, L1-6,
  L2-1, L3-1, L3-2, L3-3, L3-4, L5-1).
- **Concept (owner-ratified):**
  `.project/concepts/constraint-execution-and-design-space-studies-claude.md` — "Concrete
  Lowering"; Required Invariants (Semantics and Identity; Graph and Evaluation); Architectural
  Bets (strict resolution); Appendix B S3/S4 results and carry-forwards.
- **Required Reading (from the epic):** concept "Concrete Lowering" + Required Invariants +
  S3/S4 results and carry-forwards; memory `f4-cutover-fallback-divergence` (EP-key collapse).
- **Proven shape:** `.project/active/spike-vertical-slice-constraint-execution/s4_lib.py` and
  its `findings.md`.
- **Landed upstream types (read directly for design):**
  - `.project/reference/agentic-mbse-landed/constraint_facts.py` (Item 1) —
    `ConstraintUsageFact`, `ConstraintSource`, `OwningDefinitionFact`, `FormalFact`,
    `ActualFact`, `LocationFact`, `ConstraintDefinitionFact`.
  - `.project/reference/agentic-mbse-landed/expression_ir.py` and `expression_facts.py`
    (Item 2) — `FeatureReferenceNode` / `FeatureReferenceFact` (`source_name`, `target`,
    `chain_segments`), node algebra.
  - this repo: `sysml_codegen/analysis/part_instance_index.py` (Item 4 —
    `PartInstanceIndex.occurrences_of`, `AllOccurrencesResult.blocked`);
    `resolution/models.py:161` (`ModuleKind`, Item 6);
    `analysis/dependency_backtracker.py:466` (`_find_usage_for_channel`);
    `resolution/graph_builder.py:641,800` (`_validate_channel_references`,
    `collect_uncovered_params`); `core/output_registry.py:186` (`scoped_lookup`);
    `orchestration/pipeline_builder.py:685` (`build_pipeline_context`, the insertion seam).
- **Design:** `.project/active/constraint-lowering/design.md` (to be created)

---

**Next Steps:** After approval, `/_my_design`.
