# Spec: Constraint Module, Kleene Compiler, Aggregator, and Catalog Generation

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-12
**Complexity:** HIGH
**Branch:** constraint-exec-epic
**Epic:** CONSTRAINT-EXEC, Item 7

---

## Problem

A modeled assertion still cannot execute, even though everything upstream of code
generation is now in place on this branch:

- Item 1/2 extract constraint facts and compile predicates to a neutral `ExpressionIR`.
- Item 3 gates which assertions are eligible to run (the executable profile).
- Item 5 lowers eligible assertions to `ConcreteConstraint` records — resolved actuals,
  a deterministic `constraint_id`, an `evaluation_channel`, and a serialized `predicate_ir`
  — and extends the `ComputationGraph` with `CONSTRAINT` and `REPORT_AGGREGATOR`
  `PipelineModule`s.
- Item 6 gave `PipelineModule` a `module_kind` and left the generation seams failing loud
  on `CONSTRAINT` / `REPORT_AGGREGATOR` with "wired in Item 7." S4 named **four** calc-shaped
  seams it had to route around (python-path/duplicate-check, registry class naming,
  module-wrapper rendering, stencil rendering); Item 6 realized the fail-loud refusal at
  **five** generation entry points — module-wrapper (`modules.py`), pipeline-yaml, registry,
  test-gen, and stencil/backlog-report (`generation/errors.py` `unrenderable_module_kind_error`).
  Same surface, finer granularity: Item 7 fills all of them.

What is missing is the emission itself. Nothing generates the predicate code, the
constraint-module class, the aggregator, the runtime `ConstraintEvaluation` /
`ConstraintReport` types, or the embedded catalog. So a modeled physical limit still
dies before it reaches runnable code.

The S4 vertical-slice spike proved this whole surface end-to-end under the real TEAx
runtime, with zero production-code changes, using test-only emitters
(`.project/active/spike-vertical-slice-constraint-execution/s4_lib.py`). Item 7
productionizes those proven shapes: it fills those seams so a modeled assertion runs
as an ordinary graph module and its verdict (`satisfied | violated | indeterminate`) is
data beside the ordinary outputs, never an exception.

## Success Criteria

- [ ] **S4 slice reproduced by production generation, end-to-end under real simkit.** Both
      truth values complete with identical ordinary outputs (area 12.0, cost 3000.0),
      correct verdicts and margins (satisfied +2000 / violated −500, the violated run
      completing as evidence rather than raising), and the report persisted beside the
      ordinary outputs.
- [ ] **The cases S4 did not exercise all execute correctly:** the zero-assertion
      aggregator; an indeterminate (non-finite) point; negated and inline assertions at
      execution; and multi-instance expansion (N instances → N wired modules, N aggregator
      fields).
- [ ] **Modeled-default formals are overridable contract parameters at runtime.** The
      generated package exposes the defaulted formal as an input parameter; not overriding
      it uses the modeled default and the verdict matches; overriding it to a different
      value changes the verdict. The default is wired through the entry point, not baked
      into the predicate.
- [ ] **Exit-ancestry holds under a deliberately narrowed exit, proven falsifiably.** A
      control leg first shows the incidental path alone would DROP the report: with the
      guaranteed-ancestry mechanism disabled or mocked and the exit narrowed, the report
      channel is absent from execution. The mechanism leg then shows the report present
      under the same narrowed exit. A test that passes under incidental capture-everything
      is not acceptance.
- [ ] **Break-the-YAML** — a kept test that removes/rewires an upstream evaluation and
      confirms the missing result surfaces as an execution failure *through the executor*,
      not a silent gap.
- [ ] **Suite green; constraint-free corpus regenerates byte-identically** (timestamps
      excepted). Emitting constraint code must not disturb calc-driven generation.
- [ ] **Handoff gate to Item 8 — not an Item 7 exit gate.** Live/snapshot byte-identity
      for a constraint-bearing fixture is only meetable once Item 8 makes constraint facts
      load-bearing in the snapshot; a current snapshot cannot carry the facts yet. Item 7's
      obligation is to deliver deterministic `constraint_id`s and deterministic catalog
      ordering across repeated live loads, so Item 8 can prove the parity. This sequencing
      is recorded honestly here rather than asserted as met. See Open Questions.

## Known Requirements

### Kleene predicate compiler (codegen-owned, from S2)

- **[HARD]** A non-finite operand makes its own leaf comparison `unknown`; three-valued
  (Kleene) propagation carries it (`true or unknown` is true, `false and unknown` is
  false, `not unknown` is unknown); an assertion is `indeterminate` only when its overall
  value is unknown. Forced by reality: raw IEEE evaluation returns a confident,
  diagnostic-free `False` from a `1.0/0.0` operand — S2 verified this live in SysIDE. The
  Kleene divergence exists so a broken value never reads as a confident verdict.
  *(Concept "Catalog, Evaluation, and Report"; S2 Appendix B, verified live.)*
- **[HARD]** The predicate compiles **once at the definition level** with formal-named
  arguments; usage-level wiring decides only what the YAML feeds into those arguments —
  no per-instance predicate rewriting. The compiler's input is
  `ConcreteConstraint.predicate_ir`, a serialized IR string re-parsed at compile time via
  `agentic_mbse.sysml.expression_ir.parse_expression`.
  **Identity bridges the two levels:** one compiled predicate function per *definition*
  (compile-once), and N generated classes per concrete assertion — each embedding its own
  `constraint_id` and wiring its resolved actuals into the shared function. This is
  consistent with class-per-concrete-assertion module identity: the classes multiply,
  the compiled predicate does not. *(S2/S4; wiring note in agentic-mbse
  `sysml-codegen-wiring.md`; Item 3 design D7.)*
- **[HARD]** The serialization-equality **same-IR arm** is enforced at generation, not
  assumed: each generated constraint class's compiled predicate must serialization-equal
  its catalog concrete-entry `predicate_ir` — asserted at generation time (the compiler is
  deterministic on identical IR, so a mismatch means the class and its catalog record
  disagree). A predicate/catalog divergence is a loud generation error naming the
  `constraint_id`, never a silent mismatch. *Catching criterion:* mutate one `predicate_ir`
  after lowering → generation fails, naming that `constraint_id`. *(S2 serialization
  round-trip; Item 3 design D7 same-IR arm.)*
- **[HARD]** The profile gate strictly precedes compilation. The compiler strip-renders
  unit annotations and is **not** a unit safety net — a unit-mismatched comparison would
  otherwise compile to a bare-float comparison. Item 7 relies on Item 3 having already
  gated units, arithmetic, equality, and blocked constructs; it must not re-implement that
  check in the compiler, and it must not compile anything the profile did not admit.
  *(S2 carry-forward (2).)*
- **[NEED]** Status compares the actual value against the assertion's **expected value**:
  a negated assertion expects `false`, so a `false` predicate there is `satisfied`. Margin
  sign respects polarity — a negated inequality's margin is negated.
  *(Concept; S2 verified verdict/margin flip under `is_negated`.)*
- **[NEED]** A margin exists only for simple inequalities where predicate structure fixes
  its sign. Compound predicates report status only — no aggregate margin.
- **[HARD]** Boundary margin is zero with **no meaningful sign**. At an exact boundary a
  negated inequality yields `-0.0`; the emitted margin must normalize so a boundary reads
  as zero, not as a signed near-miss. *(S2 carry-forward (3).)*

### Constraint modules

- **[NEED — settled, do not relitigate]** Module identity is
  **class-per-concrete-assertion**: one generated class per `constraint_id`, with the ID
  embedded as a class constant. Decided by the owner (Reid, 2026-07-12) *together with*
  the measured scale evidence in this directory (`identity-gate-evidence.md`,
  `bench_aggregator_scale.py`) — there is no practical scale limit at plausible model sizes
  (IFE-class models are tens of assertions; even 10,000 assertions build the aggregator
  schema in ~450 ms and the class source in ~700 ms). Id-injection is rejected: it would
  require new teax runtime machinery, because a YAML module instance cannot learn its own
  key at run time, and would re-open the executed slice. Module fusion is a documented
  far-future revisit past a *measured* aggregator-schema limit — never first scope.
  *(S4 carry-forward (4) resolved; benchmark in this directory.)*
- **[INHERITED]** Each constraint module emits a compact `ConstraintEvaluation` on **one
  structured channel** — a single-field `MultiOutput` puts the whole struct on one channel,
  avoiding the scalar-field-reference gap. The evaluation carries: the `constraint_id`, the
  actual value, the status (`satisfied | violated | indeterminate`), a signed margin where
  structure fixes it, and the bounded observed operand values needed to explain the case
  ("violated" without the values that violated it is not acceptable evidence). Exact field
  schema is design detail; the proven S4 shape is the starting point.
  *(Concept "Catalog, Evaluation, and Report"; S4 `ConstraintEvaluation`.)*
- **[HARD]** The module never raises because a verdict went against the assertion. A
  violation completes with ordinary outputs intact and is returned as evidence. Only
  missing inputs, schema failures, thrown predicate code, or a missing aggregator field are
  execution failures. *(Concept Required Invariants, Graph and Evaluation.)*
- **[HARD]** The generated module validates its inputs inside `run()`; producer and
  consumer channel types match exactly; every constraint and report schema is registered.
  *(Concept Required Invariants.)*
- **[INHERITED]** A formal with no supplied actual is legal only when it has a **modeled
  default**: the default applies, and the formal is exposed as an **overridable contract
  parameter** retaining that default — eligible for explicit study selection, never
  automatically a study variable. Item 5 already mints this as a `LIBRARY_DEFAULT` entry
  point in the `constraint_defaults` group (`constraint_lowering.py:602`, `731-736`) and
  sources the module input from it. Item 7's obligation is to render that entry-point-sourced
  input as an ordinary contract parameter — it must **not** bake the default into the
  compiled predicate as a constant, or the parameter stops being overridable. *(Concept
  Architectural Bets: "a missing actual is legal only when the formal has a modeled default:
  the default applies, and the formal is exposed as an overridable contract parameter
  retaining that default — eligible for explicit study selection, never a study variable
  automatically.")*

### Aggregator

- **[HARD]** The aggregator has a **generated exact input schema**: one *required* field
  per concrete assertion, keyed by `constraint_id`, with `extra="forbid"`. A missing result
  is a schema failure, not a silent gap. *(Concept Required Invariants; S4.)*
- **[HARD]** The aggregator **exists even for zero assertions** — a model that asserts
  nothing still generates the report surface (headline `not_assessed`).
- **[NEED]** Headline resolves by precedence: any violation → `violation`; else any
  indeterminate → `indeterminate`; else if any results → `all_satisfied`; else (zero
  assertions) → `not_assessed`.
- **[INHERITED]** Emitted headline literals are the underscore forms that conform to the
  runtime evidence vocabulary: `violation`, `indeterminate`, `all_satisfied`,
  `not_assessed`. teax Item 10 pinned the runtime vocabulary; the generated side conforms
  to the runtime. The *ownership direction* of that vocabulary (who defines it) is decided
  in Item 10's spec, not here — Item 7 only aligns the emitted literals and records the
  dependency. *(Brief vocabulary note; S4 already emits underscore forms.)*
- **[HARD]** The aggregator is a **guaranteed exit ancestor** — reached by explicit exit
  membership or a generation-time ancestry assertion, never incidentally by riding the
  capture-everything exit. In the S4 slice the report channel reached the exit only because
  the generated exit captured every surviving module output; that breaks the moment the
  exit is narrowed. Production must make the ancestry non-incidental, and the narrowed-exit
  test proves it *falsifiably* (control leg drops the report without the mechanism; see
  Success Criteria). Which of the two mechanisms is a design decision (see Open Questions).
  *(S4 carry-forward (1).)*
- **[INHERITED]** `ConstraintReport` carries the catalog fingerprint, the assessed count,
  the ordered results, and the headline. *(Concept; S4 `ConstraintReport`.)*

### Catalog

- **[INHERITED]** The graph embeds one two-level `ConstraintCatalog`:
  - a **source record** per asserted or applied constraint *usage* — source identity and
    form, membership kind, polarity, scope, source location, display expression, and
    referenced-definition metadata when one exists;
  - a **concrete entry** per executable expansion, keyed by `constraint_id`, referencing
    its source record and adding concrete owner, execution eligibility, *optional* response
    metadata, and the recorded producer binding (`ConcreteConstraintInput.bound_channel` —
    Item 5's B1 adjudication; recorded, never hidden).
  Response metadata is **derived at generation** from predicate structure (the
  simple-inequality shape that fixes a margin's sign), not carried from upstream, and is
  optional — absent for a compound predicate that reports status only.
  *(Concept "Catalog, Evaluation, and Report"; Item 5 `ConcreteConstraint` / `...Input`.)*
- **[INHERITED]** An unused `ConstraintDefinition` is authoring inventory, never unassessed
  coverage — it never appears as unassessed. Non-assert kinds appear in the catalog as
  unassessed. Catalog ordering is deterministic by `constraint_id`. *(Concept.)*
- **[INFERRED]** Item 7 assembles the catalog from Item 5's `ConcreteConstraint` records
  (concrete entries) and Item 1's constraint facts (source records), and embeds it in the
  graph as serializable fields — generation reads only the graph. The catalog fingerprint
  flows into every `ConstraintReport.catalog_fingerprint`.

### Runtime-facing tests

- **[NEED]** A kept **break-the-YAML** test: break the upstream wiring for one evaluation
  and assert the missing result surfaces as an execution failure through the executor. S4
  proved the mechanism only at the constructor level (the aggregator's exact-schema
  `ValidationError`); production must close it with an end-to-end test.
  *(S4 carry-forward (2).)*
- **[HARD]** Execution-level criteria are exercised under the **real simkit** runtime
  (teax's venv on the epic branch, provisioned by Items 10–12; Item 0/S4 findings hold the
  incantations), not only through offline graph construction.

## Non-Goals

- Contracts and package sealing — Item 9.
- Making constraint facts load-bearing in the snapshot, and flipping the
  `lower_constraints_enabled` default — Item 8. Item 7's generation tests run with
  `lower_constraints_enabled=True` (the flag defaults `False` on the shared path until
  Item 8).
- Calc-side IR rendering and `ExpressionAST` retirement — Item 13.
- Drop-manifest retirement, blanket-warning removal, and IFE acceptance — Item 14.
- New expression capability: blocked operators (`xor`/`implies`, invocation, feature
  chains, unit conversion, real equality) stay blocked; Item 3 owns the profile and Item 7
  compiles only what it admitted.
- Deciding who *owns* the runtime evidence vocabulary — Item 10's spec. Item 7 only
  conforms the emitted literals.

## Open Questions / Deferred to design

- **Exit-ancestry mechanism.** Explicit exit membership vs a generation-time ancestry
  assertion — both satisfy the invariant. Design picks one and builds the narrowed-exit
  kept test against it.
- **Exact `ConstraintEvaluation` / `ConstraintReport` field schema and where the runtime
  types live.** S4 put them in `schemas/constraint_types.py`. Design pins the schema; it
  must carry the required semantic content above and register every schema.
- **What "actual value" is in `ConstraintEvaluation`.** S4 used the boolean predicate
  result (`Optional[bool]`, `None` when indeterminate) and put the numeric operands in a
  separate `observed` map. Confirm at design whether that split is the production shape.
- **Template structure for the five seams** — module-wrapper, pipeline-yaml, registry,
  test-gen, and stencil/backlog-report. How much reuses the existing calc templates versus
  new constraint templates, and where the constraint/aggregator buckets slot into
  `generate_registry`'s calcusage/formula/aggregation partition.
- **Class and channel naming for class-per-concrete-assertion.** S4 used
  `_pascal(instance_local + usage_name) + "ConstraintModule"`, `constraint_id.lower()` as
  the YAML key, and `constraint_id + "__evaluation"` as the channel. Pin the production
  scheme at design (Item 5 sets `evaluation_channel`; the `module_type` on the graph today
  is an explicit placeholder Item 7 owns).

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_constraint_execution.md` (Item 7)
- **Required Reading:**
  - `.project/concepts/constraint-execution-and-design-space-studies-claude.md` —
    "Catalog, Evaluation, and Report", Required Invariants, Appendix B (S2/S4 results and
    all carry-forwards)
  - S2 findings: `.project/active/spike-expression-tree-parity/findings.md`
  - S4 findings + emitters: `.project/active/spike-vertical-slice-constraint-execution/`
    (`findings.md`, `s4_lib.py`)
- **Owner-gate evidence:** `identity-gate-evidence.md`, `bench_aggregator_scale.py`
  (this directory)
- **Upstream code (this branch):**
  - Item 5 — `src/sysml_codegen/resolution/models.py` (`ConcreteConstraint`,
    `ConcreteConstraintInput`, `ConstraintInputResolution`, `ModuleKind`, `PipelineModule`);
    `src/sysml_codegen/analysis/constraint_lowering.py`
    (`lower_constraints`, `extend_graph_with_constraints`)
  - Item 6 seams — `src/sysml_codegen/generation/` (`modules.py`, `pipeline.py`,
    `registry.py`, `test_gen.py`, `stencils.py`, shared `errors.py`)
  - Item 2 — `agentic_mbse.sysml.expression_ir` (`parse_expression`, node algebra);
    reference copy `.project/reference/agentic-mbse-landed/expression_ir.py`
- **Test surface to flip:** `tests/conformance/test_module_kind_faildloud.py` (asserts the
  five seams refuse today — Item 7 inverts these); `test_constraint_lowering.py`,
  `test_constraint_graph_extension.py`, `test_concrete_constraint_model.py`
- **Design:** `.project/active/constraint-generation/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_design`.
