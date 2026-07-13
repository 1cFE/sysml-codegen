# Spec: Concrete Constraint Lowering — New Phase, Strict Resolution, Execution IDs

**Status:** Draft
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

From the epic. These are the acceptance bar for the item.

- [ ] **S4 behavior reproduced by production code.** With pruning enabled and a minimal exit
      selection, the control run (no lowering) prunes `cost_calc`; the lowered run retains it
      — and *only* via the resolved constraint input channel joined as a backtracking root,
      not because every output feeds the exit.
- [ ] **Strict resolution has no fallback.** V11 coverage and channel-reference validation
      pass on the extended graph; no fallback path executes for a constraint actual. Probe:
      an unresolvable actual produces a generation error that names the actual — never a
      synthesized entry point.
- [ ] **Deterministic identity.** `constraint_id`s and catalog ordering are byte-identical
      across repeated live loads. Fixed-multiplicity siblings are independently wired — three
      occurrences are three wired nodes with three distinct channels, not copies.
- [ ] **Corpus byte-identity.** The existing fixture corpus (no constraints admitted to the
      executable profile) regenerates byte-identically (timestamps excepted). The new phase
      is inert when nothing is lowered.

## Known Requirements

### Phase placement

- **[INHERITED: concept "Concrete Lowering"; epic §1]** Lowering is a **new pipeline phase**
  that runs after aliases, the output registry, and supplied-value materialization are final,
  and before dependency backtracking — actual resolution needs the finished registry. It
  reuses the virtual-usage expansion idiom but at a later seam than template-calc expansion.
- **[INFERRED]** The phase must be a no-op on models with no profile-admitted assertions, so
  the corpus byte-identity gate holds. (Forced by the corpus success criterion; the
  mechanism — early-out vs. empty-result — is design's.)

### `ConcreteConstraint` — one predicate in one concrete context

- **[INHERITED: concept; epic §2]** Produce a `ConcreteConstraint` per concrete expansion,
  carrying: its source facts, resolved actuals, expected Boolean value (a negated assertion
  expects false), a deterministic `constraint_id`, and optional simple-inequality response
  metadata (margin sign).
- **[INHERITED: concept; epic §2]** Expansion has three sources, one per ownership kind:
  - Part-definition-owned and inherited assertions expand **once per concrete part
    instance**, via Item 4's index (`PartInstanceIndex.occurrences_of`).
  - Calc-definition-owned assertions expand **once per concrete calc usage** (existing
    calc-usage discovery, not the part index).
  - Direct-usage-owned assertions expand **once** (Item 1's tagged owner semantics).
  - *Only part-def-owned was exercised by S4; calc-def-owned and direct-usage-owned are new
    paths this item builds.*
- **[INHERITED: concept Required Invariant "Semantics and Identity"; epic §2]** An expected
  concrete instance that cannot be formed is a **validation error**, not a warn-and-drop.
- **[HARD]** A constraint-owning part definition whose instance expansion hits a non-finite
  multiplicity must surface as a generation error, never a silent omission. Item 4's bulk API
  reports these in `AllOccurrencesResult.blocked` / `SourceOwnersResult.blocked`; the
  per-owner `occurrences_of` raises `NonFiniteCardinalityError`. Whichever entry point
  lowering uses, a blocked constraint owner must not vanish (Design Principle 5; the Item 4
  audit cure exists precisely so this cannot be swallowed).

### Strict resolution through one shared seam

- **[INHERITED: concept Architectural Bets "Strict resolution"; epic §3]** Resolve every
  actual through **one shared resolver seam with an explicit strict mode**. Legal outcomes,
  and only these:
  - A **chain actual** (e.g. `cost_calc.cost`) resolves via `OutputRegistry.scoped_lookup`
    in the owner-instance scope to a producer channel.
  - A **reference actual** resolves against design attributes, minting a `DESIGN_ATTRIBUTE`
    entry point in its derived parameter group.
  - A **defaulted formal** with no actual becomes an overridable contract parameter that
    retains the modeled default — eligible for explicit study selection, never an automatic
    study variable.
- **[HARD]** **Unresolved is a generation error — never synthesis.** No textual fallback, no
  entry-point synthesis for a constraint actual. This is forced by the existing backtracker
  fallback being unsafe here: it emits a bare `{module_eqn}__{leaf}` entry point that
  collapses distinct params and churns baselines (memory: `f4-cutover-fallback-divergence`,
  verified against `dependency_backtracker.py` / `graph_builder.py`). The strict seam must
  not reuse that fallback as a drop-in.
- **[INFERRED]** The shared seam should be structured so the strict (constraint) mode and the
  lenient (calc) mode are one code path with an explicit switch, so the two cannot silently
  diverge again. (The concept calls for "one shared resolver seam"; the exact factoring —
  extract into a shared function vs. a mode flag on the existing resolver — is design's.)
- **[INHERITED: concept; epic §3]** A formal that has neither an actual nor a modeled default
  is a generation error.

### Roots before pruning

- **[INHERITED: concept; epic §4; S4-proven]** Each resolved constraint **input channel**
  joins the backtracking roots via the production `_find_usage_for_channel` seam
  (`dependency_backtracker.py:466`) **before pruning**, so a calculation whose only consumer
  is an assertion stays in a targeted graph. S4 proved this exact seam.

### Extended graph and validation

- **[INFERRED]** Lowering produces the **extended `ComputationGraph`**: constraint module
  nodes (`module_kind=CONSTRAINT`, one per concrete assertion, each with its own evaluation
  channel) and one report-aggregator node (`module_kind=REPORT_AGGREGATOR`), plus the minted
  entry points joined into their groups. This is the graph *structure* only — Item 7 emits
  the module Python, the Kleene compiler, the aggregator schema, and the catalog runtime from
  it. (Reasoning: the epic requires "V11 coverage and channel-reference validation pass on
  extended graphs," which needs the constraint consumers present to cover the minted entry
  points; S4's `extend_graph` — the productionized shape — builds exactly these nodes and
  runs exactly these validations. See the Open Question on the Item 5 / Item 7 line.)
- **[HARD]** `PipelineModule.module_kind` is a required field (Item 6, `models.py:193`).
  Constraint and report-aggregator nodes must set it; they carry no
  `calc_def_qualified_name`, so any seam that assumes one must already dispatch on
  `module_kind` (Item 6 made the four calc-shaped seams do so).
- **[INHERITED: concept; epic success criteria]** The extended graph passes
  `_validate_channel_references` (`graph_builder.py:641`) and has zero V11 uncovered
  parameters (`collect_uncovered_params`, `graph_builder.py:800`).

### Identity

- **[INHERITED: concept "Concrete Lowering"; epic §5]** `constraint_id` is the **execution
  identity**: source-local identity + concrete owner-instance identity + membership kind +
  polarity, all scoped to one executable fingerprint. It is deterministic; catalog ordering
  is deterministic by ID.
- **[INHERITED: concept; epic §5]** A `constraint_id` **collision is a generation error**.
- **[INHERITED: S3 carry-forward (3); epic §5]** Fixed-multiplicity siblings each get their
  **own channels** — structurally identical siblings must not share an evaluation channel, or
  their verdicts become copies. Item 4's index already gives each occurrence its own identity
  (`InstanceOccurrence.instance_path` with per-step `occurrence_index`).
- **[INHERITED: concept; epic §5]** Support an optional author-controlled **`tracking_key`**
  for cross-version correlation. Names enable correlation, not equivalence; anonymous
  assertions have identity only within a fingerprint. (The fingerprint *namespaces* IDs and
  is never an input to them — no circularity. Fingerprint construction itself is Item 9.)
- **[INFERRED]** The fingerprint that scopes IDs is not sealed until Item 9. Lowering needs a
  determinism boundary it can compute now (stable across repeated live loads) without the
  package seal. (The exact scoping token for this item is design's; the invariant is
  repeated-live-load byte-identity, which S3 proved is the achievable determinism here.)

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
  item assumes every fact it receives is profile-admitted and does not re-check eligibility.
- **Fingerprint sealing and contracts** — Item 9.

## Open Questions / Deferred to design

- **The Item 5 / Item 7 line.** This spec reads Item 5 as producing the extended
  `ComputationGraph` (constraint + report-aggregator *nodes*, minted entry points, joined
  roots) plus `ConcreteConstraint` data, with Item 7 emitting all code from it — because the
  epic's V11-on-extended-graph criterion needs the consumer nodes present and S4's productionized
  `extend_graph` builds them. Design should confirm this boundary against Item 7's spec and
  decide precisely which fields of the constraint `PipelineModule` nodes Item 5 sets versus
  leaves for Item 7 (the node's `module_type`/`name` sit near Item 7's generated-class
  identity decision).
- **The shared resolver seam's factoring.** Extract entry-point resolution out of the
  backtracker into a shared function taking a `strict` flag, versus add a strict mode in
  place. Either satisfies "one shared seam"; the choice interacts with the F4 EP-key-collapse
  risk and the calc-side lenient path, which design must keep byte-identical.
- **`constraint_id` string encoding.** The components are fixed (source-local + owner-instance
  + membership kind + polarity); the exact serialization, and the anonymous-assertion ordinal
  scheme within a source-local part, are design's — with the constraint that no scheme is
  advertised as cross-version-stable (that is `tracking_key`'s job).
- **`tracking_key` authoring surface.** The concept fixes that it exists and is
  author-controlled and optional. Where the author declares it, and whether it arrives on the
  Item 1 fact or is read at lowering, is a design + Item 1 coordination question. Low leverage
  for the core lowering path.
- **Modeled-default contract-parameter representation.** S4 explicitly did not exercise
  modeled-default formals ("refusing to guess"). The concept fixes the outcome (an overridable
  contract parameter retaining the default, not an automatic study variable); the graph/entry-
  point representation is design's.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_constraint_execution.md` (Item 5)
- **Concept (owner-ratified):**
  `.project/concepts/constraint-execution-and-design-space-studies-claude.md` — "Concrete
  Lowering"; Required Invariants (Semantics and Identity; Graph and Evaluation); Architectural
  Bets (strict resolution); Appendix B S3/S4 results and carry-forwards.
- **Required Reading (from the epic):** concept "Concrete Lowering" + Required Invariants +
  S3/S4 results and carry-forwards; memory `f4-cutover-fallback-divergence` (EP-key collapse).
- **Proven shape:** `.project/active/spike-vertical-slice-constraint-execution/s4_lib.py` and
  its `findings.md`.
- **Upstream landed types (design must read the real shapes):**
  - agentic-mbse (`~/1cfe/agentic-mbse`, outside this sandbox): `ConstraintUsageFact`,
    `ConstraintSource`, `ConstraintDefinitionFact` (Item 1, CERTIFIED); `ExpressionIR` /
    `expression_ir.py` (Item 2, audit in flight).
  - this repo: `sysml_codegen/analysis/part_instance_index.py` (Item 4, CERTIFIED —
    `PartInstanceIndex`, `occurrences_of`, `AllOccurrencesResult.blocked`);
    `sysml_codegen/resolution/models.py:161` (`ModuleKind`, Item 6);
    `dependency_backtracker.py:466` (`_find_usage_for_channel`),
    `graph_builder.py:641,800` (`_validate_channel_references`, `collect_uncovered_params`),
    `core/output_registry.py:186` (`scoped_lookup`).
- **Design:** `.project/active/constraint-lowering/design.md` (to be created)

---

**Next Steps:** After approval, `/_my_spec_review` (fresh session), then `/_my_design`.
