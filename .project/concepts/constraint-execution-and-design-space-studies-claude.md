# Design: Constraint Execution and Design-Space Studies

**Status:** Proposed
**Owner:** Reid W
**Created:** 2026-07-11

---

## Overview

Engineers already model physical limits next to the calculations they constrain. Today those limits stop at a warning: the generated model computes values but never judges them, so every study re-implements the judgment by hand. This design makes modeled limits execute inside the generated forward model, exposes their verdicts as data, and adds a study layer that runs one point or thousands against the same evidence.

The core commitment is a three-way separation of responsibility. Calculations compute a candidate design state. Constraints observe that state and report whether it holds. A study decides what a verdict means for the exploration at hand — reject the point, penalize it, keep it for a boundary plot, or feed it back to a search strategy. Keeping the three apart lets one generated model serve manual runs, dense sweeps, uncertainty studies, and optimization without re-deriving anything.

---

## Problem

The authoring workflow captures three kinds of engineering knowledge: hardware structure, forward calculations, and physical limits. The first two survive generation — calculations become a typed executable graph, proven bit-exact against hand-verified anchors on a real fusion cost model. The third does not. A modeled limit is recognized, classified, and then reported as dropped; its predicate, its bindings, its concrete design context, and its truth value never reach generated code. The one demonstrated design-space sweep re-implements the viability rule by hand in its harness, where nothing stops it drifting from the model it claims to represent.

The execution framework compounds this. It runs one pipeline at a time, reading inputs from files, with no way to hand it in-memory values and no notion of a candidate or a study. Worse, its only vocabulary for "something is wrong" is an exception — which conflates an infeasible design with broken code. An infeasible design is a successful, informative evaluation; broken code is not. Today's sweeps escape the framework entirely by calling generated functions directly, giving up its validation and provenance to get throughput.

The missing system is not a solver. The forward model already knows how to compute its outputs. What it lacks is a trustworthy way to evaluate the modeled predicates over those outputs, keep the evidence alongside the ordinary results, and let an outer layer own the interpretation. History here argues for one more requirement: this system has repeatedly been bitten by things vanishing quietly. Whatever shape execution takes, silence must stop being a possible outcome for a modeled limit.

---

## Goals

- Execute every supported modeled assertion for each concrete design state, both live and from a captured snapshot.
- Preserve normal outputs and diagnostic evidence when an assertion is violated.
- Keep violation, indeterminacy, and execution failure as three distinct, queryable outcomes at every layer.
- Let people and agents define study variables, objectives, policies, and search methods without copying model equations.
- Serve auditable single runs and high-throughput studies from one sealed model contract.

## Non-Goals

- Solve algebraic equations, infer missing values, or add implicit loops to the forward graph.
- Prove temporal invariants or monitor time-series behavior.
- Assign hard, soft, advisory, objective, or penalty roles from names or assertion syntax.
- Execute requirement satisfaction, assumptions, or preconditions in the first scope; they stay visible but unassessed.
- Invent floating-point equality tolerances, universal margins, or normalized penalties.
- Ship optimizers in the first scope; the strategy interface is pluggable, and the first strategies are prepared lists and grids.

---

## Design Principles

### 1. Compute, Judge, and Decide Are Different Operations

Calculations produce a design state. Constraints observe that state and return evidence. Study policy decides what the evidence means for the current exploration. A relation that determines a value belongs in a calculation; a relation that limits or checks values belongs in a constraint; a rule about what to do with a violation belongs only in a study.

### 2. The Unit of Evaluation Is a Predicate in a Concrete Context

An assertion may own its predicate inline or select a reusable one and supply bindings. Neither means anything at runtime without its owning design instance, and inheritance or templates may turn one source assertion into several executions. Every result therefore belongs to exactly one effective predicate in exactly one concrete context, and carries an identity that says which.

### 3. Structure Survives; Reconstructed Text Does Not

Predicates, bindings, identities, and source facts travel as typed structural data through extraction, snapshots, and graph construction, and code is generated from that structure. Reconstructed expression text, name-matching, and dynamic evaluation are display and debugging aids, never semantic interfaces. This project has already paid for violating this once.

### 4. Violations Are Evidence; Exceptions Are Breakage

A false supported predicate is a successful evaluation that returned an important answer. Exceptions are reserved for evaluations that could not complete. The two never share a representation, at module, report, or study level.

### 5. Silence Is Never an Outcome

Every modeled limit ends in exactly one of three visible places: it executes and produces a verdict; it is cataloged as present-but-unassessed with its kind stated; or it blocks generation with its identity and the exact unsupported construct named. There is no path on which a limit simply disappears — including the offline path, where a stale snapshot without constraint facts must be rejected, not quietly generated without assertions.

---

## Architectural Bets

- **One ordinary graph module per concrete assertion, plus one report aggregator.** Constraints ride the existing DAG scheduling, provenance, and validation instead of a parallel engine. The aggregator gives every assertion a guaranteed execution path (only ancestors of the pipeline's exit are guaranteed to run) and one stable report artifact. Rejected alternatives: post-run harness evaluation (the drift we are retiring), producer-embedded assertions (no natural owner for cross-module predicates, and exceptions destroy infeasible points), a runtime constraint engine (couples a generic executor to one modeling language).
- **Predicates get a structural, serializable expression representation owned by the semantics library; codegen compiles it.** A permanently separate semantic representation is rejected — the long-term direction is one tree serving calculations and predicates, and the display-text reconstruction never grows into a compiler. Whether that tree extends an existing representation, becomes the shared tree immediately, or begins predicate-focused with an explicit convergence path is S2's decision, on evidence.
- **The graph owns the catalog and the semantic contract; packaging seals them.** Everything generation needs is serializable graph data; after artifacts are written, a sealing pass hashes them into an executable fingerprint. Study tooling consumes the sealed contract, never module filenames or YAML internals.
- **Repeated-evaluation machinery is generic and lives in the runtime; SysML meaning stays upstream.** The runtime gains typed in-memory input injection, an evaluator protocol, and a study layer that work for any conforming model package. It never parses model semantics.
- **Strict resolution for assertion inputs: fail, never synthesize.** Calculation inputs historically fell through to synthesized entry points, caught only by a boundary check. Assertion actuals do not inherit that leniency — an unresolved actual is a generation error, and a missing actual is legal only when the formal has a modeled default: the default applies, and the formal is exposed as an overridable contract parameter retaining that default — eligible for explicit study selection, never a study variable automatically. This is the same rule today's library-default entry points already follow.

---

## Core Model

*Register shift: from here on, identifiers and file-level mechanisms are intentional.*

### Neutral Constraint Facts — agentic-mbse

`ExpressionIR` names the structural, serializable predicate representation — its relationship to the two existing expression representations is S2's decision, not this document's. Its required node algebra: literal, feature reference, unary/binary/n-ary operator, invocation, unit annotation, and an explicit unsupported node carrying a structural diagnostic. References keep source name, qualified target, and feature-chain segments; they do not pre-classify a value as channel, parameter, or intermediate — that is codegen's job.

`ConstraintDefinitionFact` carries a reusable predicate, formal parameters with defaults, and source identity. `ConstraintUsageFact` records exactly one `ConstraintSource` — an inline predicate, a constraint-definition reference, a named constraint-usage reference (the spec's assert-by-reference form, bound by reference subsetting), or a requirement-usage reference (satisfy) — and preserves actual expressions, owner, scope, membership kind, assertion polarity, and inheritance facts. Inline and reusable sources put the effective predicate in different places (on the usage itself versus on the definition, evaluated in usage scope), so extraction treats them as two distinct lookups. Membership kind must be read from the owning membership (require/assume live on `RequirementConstraintMembership`, not on a usage subtype), which today's type-level classification collapses to "plain" — a known limitation these facts exist to fix.

The **executable profile** defines what may run: static scalar `AssertConstraintUsage` in the inline and definition-typed source forms, with owner-scope references or formals bound by explicit actuals or modeled defaults; comparisons, arithmetic, `and`/`or`/`not`, and negated assertion polarity. Assert-by-reference to a named usage blocks generation in the first scope with a named diagnostic; satisfy stays cataloged, unassessed. Equality is admitted by proof, never by guess. Boolean, enum, integer, and string equality are supported only when both operand types are recovered from the neutral facts and their compatibility is proven — an enum comparison is understood as enum equality against the right enumeration, catching invalid literals before execution, not as arbitrary string matching. Real-valued equality stays unsupported unless the model supplies explicit comparison semantics such as a tolerance (no such convention exists yet, and implying one would smuggle in exactly the invented tolerance the non-goals forbid); unknown, partially typed, or incompatible operands block generation; the compiler never guesses an operand category. An author who needs a numeric band writes it explicitly as two inequalities. Unit policy, first scope: comparison and arithmetic operands must be dimensionless or carry identical units; anything requiring conversion — including same-dimension different units — blocks generation with a named diagnostic, because runtime values are bare floats and units never convert silently. The profile replaces the current placeholder coverage check and the blanket "constraints are dropped" warning with per-construct eligibility diagnostics, and runs both at design review and at codegen preflight.

### Concrete Lowering — sysml-codegen

`ConcreteConstraint` is one effective predicate in one owner instance: source facts, resolved actuals, expected Boolean value, deterministic ID, and optional simple-inequality response metadata. Lowering is a **new pipeline phase** that reuses the virtual-usage expansion idiom but runs at a later seam than template-calc expansion does today: after aliases, the output registry, and supplied-value materialization are final, and before dependency backtracking — because actual resolution needs the finished registry. Part-definition-owned and inherited assertions expand once per concrete part instance; calculation-definition-owned assertions expand once per concrete calculation usage; an expected instance that cannot be formed is a validation error, not a warn-and-drop.

Actual resolution reuses the `OutputRegistry` and `BindingResolution` shape for channels — but entry-point resolution today lives inside the backtracker and includes fallback behavior, so lowering needs one shared resolver seam with an explicit strict mode; the fallback path is not a drop-in (a known entry-point-key collapse risk). Resolved constraint input channels join the backtracking roots before pruning, so a calculation whose only consumer is an assertion stays in a targeted graph. Lowering also needs a complete concrete part-instance index that does not derive from calc templates: today's instance discovery is driven by virtual calculation expansion, so a constraint-only part definition may have no discovered instances at all. Covering constraint-only definitions, nesting, inheritance and redefinition, multiplicity, and snapshot replay is a named implementation risk, gated by its own spike. Identity splits in two. The `constraint_id` is the **execution identity**: source-local identity plus concrete owner-instance identity plus membership kind plus polarity, all scoped to one executable fingerprint; a collision is a generation error and catalog ordering is deterministic by ID. Anonymous assertions may use an ordinal inside the source-local part, but that ordinal is never advertised as cross-version stability — no automatic scheme survives arbitrary source edits (ordinals move on insertion, locations move on edits, content hashes change with semantics). Cross-version correlation is a separate, optional, author-controlled **`tracking_key`**: name any constraint whose results must be compared across model versions. Names enable correlation, not equivalence — a named constraint whose predicate changes remains the same tracking subject, but its evidence spans different executable fingerprints and tools must show that boundary. Anonymous assertions have identity only within a fingerprint. The fingerprint *namespaces* IDs — it is never an input to them: artifacts contain the IDs, and the artifact hashes then form the fingerprint, so there is no circularity.

`PipelineModule` gains a real `module_kind` (calculation, formula, aggregation, constraint, report aggregator) replacing the accreted Boolean flags, and structured output schema identity becomes graph data — retiring the float-specialized wrapper assumption for these modules.

### Catalog, Evaluation, and Report

The graph embeds one `ConstraintCatalog` at two levels: a **source record** per asserted or applied constraint *usage* (source identity and form, membership kind, polarity, scope, source location, display expression, referenced-definition metadata when one exists) and a **concrete entry** per executable expansion, keyed by `constraint_id`, referencing its source record and adding concrete owner, execution eligibility, and optional response metadata. An unused `ConstraintDefinition` is authoring inventory, not execution coverage — it never appears as unassessed. Reporting can then group failures by modeled constraint while naming the failing instance. Every constraint that today lands in the drop-report manifest lands here instead — executable and explicitly-unassessed alike — and the manifest plus its blanket warning retire.

Each constraint module emits a compact `ConstraintEvaluation`: ID, actual value, `satisfied | violated | indeterminate`, optional signed margin, bounded diagnostic. Status compares the actual value against the assertion's expected value — a negated assertion expects false, so a false predicate there is satisfied. Generated predicate code evaluates under three-valued (Kleene) semantics: a non-finite operand makes its own leaf comparison unknown, and unknown propagates only where a connective needs it — `true or unknown` is true, `false and unknown` is false — so an assertion is indeterminate only when its overall value is unknown. This is a deliberate divergence from raw IEEE evaluation, which would return a confident `false` from a broken value. The module never raises because the verdict went against the assertion. A margin exists only for simple inequalities where structure fixes its sign, and the sign respects polarity (a negated inequality's margin is negated); compound predicates report status only. Each evaluation also carries bounded explanatory evidence — the observed operand values needed to explain this case, such as response and bound for a simple inequality — keyed against the catalog's statics; the exact schema is design detail, but "violated" without the values that violated it is not acceptable evidence.

`ConstraintReport` carries the catalog fingerprint, assessed coverage, ordered results, and a headline that resolves by precedence: any violation, else any indeterminate, else all-satisfied, else not-assessed for zero assertions. The aggregator has a generated exact input schema — one required field per concrete assertion, so a missing result is a schema failure, not a silent gap — exists even for zero assertions, and is an ancestor of the exit point.

### Contracts and the Evaluator

`ModelContract` derives solely from graph fields: stable parameter and output IDs, the constraint catalog, required evaluation semantics, and a semantic fingerprint; *provided* capabilities — available backends, in-memory entry support, persistence modes — are package and runtime facts and live in `PackageContract`, not the graph. `PackageContract` seals it after artifact generation: content hashes over the generated and preserved (handwritten) artifact set, excluding the seal itself and runtime outputs, plus generator and runtime versions — verified on package load, not just at packaging. The generated package ships a `ModelEvaluator` adapter returning immutable `ModelEvidence` — a runtime-owned generic envelope: response entries keyed by stable IDs (constraint verdicts project onto generic response keys), selected outputs, provenance, and the full generated report attached as an opaque model artifact, so runtime types never depend on generated classes. Every evaluation failure surfaces as one normalized outcome: phase, module or channel when known, cause, retryability, and partial-artifact status. The first backend is a prepared pipeline — validate and build topology once, fresh execution context per case — fed by a typed in-memory entry source; the file-backed path remains for auditable runs, with finishing, auditing, and merging the runtime's in-flight scalar-persistence work as a prerequisite, alongside a direct producer-to-consumer type-continuity test. Faster backends are admitted only on case-level parity.

### Study Layer — TEAx

`StudyDefinition` selects variables and domains by parameter ID, observables by output ID, objectives, response roles, failure policy, strategy, budget, and retention; it cannot redefine a predicate. `CandidateStrategy` implements propose/observe for lists, grids, samplers, and later optimizers. `StudyRunner` follows one order: validate and canonicalize the proposal, evaluate, assess immutable evidence, atomically commit the `CaseRecord`, then advance strategy feedback. Identity has three layers — `proposal_id` (raw strategy output), `candidate_id` (the validated logical evaluation; deliberate replicates get distinct candidate IDs even with identical inputs), and `attempt_id` (one execution try) — with idempotency scoped to (`study_id`, `candidate_id`), so failed attempts are preserved without ever committing two case results for one logical candidate.

An invalid proposal never becomes a candidate: it persists as an append-only `ProposalRecord` keyed by `proposal_id`, so "candidate" always means a canonical evaluation that reached the evaluator. `CaseRecord` keeps `completed`, `execution_failed`, and `assessment_failed` distinct. `StudyStore` (SQLite first — atomicity and idempotency are required behavior, not scale features) is append-only for committed case evidence and attempt history, with controlled mutable operational state such as cursors kept separate. Database and filesystem writes cannot share a transaction, so artifacts follow a staging protocol: write to staging or content-addressed storage, make durable, then commit the case record and artifact references in one transaction — unreferenced staged artifacts are collectable garbage, and a reader never sees a committed case pointing at half-written artifacts. At creation the store binds immutable compatibility fields (executable, model-contract, and study-definition fingerprints; input and evidence schema versions; strategy identity and configuration); opening it with incompatible values fails explicitly, and any change starts a new study lineage. First delivery is candidate source → validation → evaluator → atomic store; adaptive checkpointing, replayable feedback, parallel workers, and optimizer state restoration are deferred until crash-resume semantics are proven — an adaptive strategy must then be replayable from ordered feedback plus a seed, checkpointed atomically with its cursor, or declared non-resumable up front.

---

## Diagram

```mermaid
flowchart LR
    A[SysML calculations + assertions] --> B[Neutral facts + executable profile] --> C[Concrete lowering: expand, resolve, root] --> D[Computation graph + catalog + contract]
    D --> E[Generated calc modules] & F[Generated constraint modules]
    E --> F --> G[Report aggregator]
    E --> H[Ordinary outputs]
    G & H --> I[Model evaluator → immutable evidence]
    J[Strategy] --> K[Study runner] --> I
    I --> L[Study policy] --> M[Atomic case record] --> J
```

---

## Required Invariants

### Semantics and Identity

- One `constraint_id` maps to exactly one effective predicate source, usage, concrete owner instance, membership kind, and polarity within an executable fingerprint; IDs and catalog ordering are identical across live and snapshot generation.
- Membership kind, polarity, ownership, and inheritance facts survive extraction, snapshot round-trip, and generation unchanged.
- Every asserted predicate either lowers to a module or blocks generation naming its identity, the unsupported construct, and its source location; non-assert kinds appear in the catalog as unassessed.
- A snapshot predating the constraint-facts format version is rejected by the existing version hard-gate, and a current-version snapshot missing the constraint-facts section fails rather than loading as an empty catalog; a model that asserts something never quietly generates an assertion-free package.
- An expected concrete instance that cannot be formed fails validation.

### Graph and Evaluation

- Predicate, catalog, schema, and contract data are serializable graph fields; generation reads only the graph.
- Constraint actual resolution has no textual fallback and no entry-point synthesis; unresolved means generation error.
- Every concrete assertion and its transitive producers are ancestors of the report aggregator and the exit point.
- An assertion whose actual value differs from its expected value returns `violated` — never raising or suppressing ordinary outputs; a non-finite operand makes its leaf comparison unknown under three-valued propagation, and only an overall-unknown assertion is `indeterminate`; missing inputs, schema failures, thrown predicate code, or a missing aggregator field are execution failures.
- Margins exist only where predicate structure fixes their sign, and the sign respects assertion polarity; no aggregate margin for compound predicates.
- Generated modules validate values inside `run()`; producer and consumer channel types match exactly; every constraint and report schema is registered.
- Migration: every constraint in today's drop manifest maps to exactly one source record in the new catalog, and every source record expands to one or more concrete entries; the blanket warnings retire with the manifest.

### Study Execution

- Proposal records and the three case states never merge; policy assessment never mutates stored evidence.
- Auditable and fast evaluators return equivalent selected outputs and constraint results for the same canonical inputs.
- Atomic case commit precedes strategy feedback; a persistence or infrastructure failure never yields a completed case, and a committed case never references half-written artifacts (artifacts are staged durably before the commit).
- Resume joins on study lineage, executable and study fingerprints, and candidate identity — never on constraint IDs alone; that combination makes resume idempotent and prevents mixed-model datasets.

---

## How It Works

### Author and Generate

An engineer models limits as inline or typed assertions — the live-validated toy is the shape: a reusable `'Cost Within Budget'` definition owning `cost <= budget`, and an `affordable` usage binding `cost` to a calc output and `budget` to a design attribute. The executable profile judges every assertion during prototyping and again at preflight. Lowering expands assertions per concrete instance, resolves `cost` to its producer channel and `budget` to an entry point, adds both as backtracking roots, and generation emits the constraint module, the aggregator, the catalog, and the sealed contracts.

### Evaluate One Design Point

The evaluator takes typed values keyed by contract parameter IDs, validates them against the prepared pipeline, and runs a fresh context. Constraint modules consume entry values and upstream outputs like any module; the aggregator emits one report beside the ordinary outputs; the evaluator returns both as immutable evidence. A file-backed run produces the same evidence plus auditable artifacts.

### Run a Study

The runner asks the strategy for candidates. Invalid proposals persist as proposal records and never touch the model. Valid points evaluate; policy classifies the evidence; evidence and assessment commit atomically; only then does the strategy see feedback. A rejected point keeps its outputs and violations for boundary plots. Model, assessment, and persistence failures stay phase-distinct.

### Inspect and Resume

Results query by parameter, output, constraint ID, status, and assessment, joining static source detail through the catalog. Resume refuses a changed executable or study fingerprint and restores strategy state by replay or checkpoint; a non-resumable strategy declares itself before the first case.

---

## Edge Cases and Failure Modes

- An assertion is the only consumer of a calculation: root status keeps the producer in targeted graphs.
- An inherited assertion lands on several instances: one deterministic ID and result per instance.
- An assertion uses an unsupported construct (invocation, conditional, temporal, unit conversion, real equality): generation blocks, naming construct and location; the authoring fix for real equality is an explicit two-inequality band.
- A module raises or the aggregator misses an input: execution failure; partial channels make no assertion claims. An operand that is NaN or infinite is different: that assertion is indeterminate, and policy decides the point's fate.
- A model has no assertions: the report says not-assessed; documented-only constraints can never yield a false all-satisfied.
- An old snapshot is loaded, or a current one lacks the constraint-facts section: both fail with a re-capture instruction; neither loads as an empty catalog.
- A part definition owns constraints but no calculations: instance discovery must still find its concrete instances; calc-template-derived discovery would find none — the instance-index spike gates this.
- Runtime scalar handling: constraint modules bind whole channels and emit structured models, avoiding the known field-reference gap on scalar channels; the larger unproven risk — ordinary producer-to-consumer scalar type continuity — gets a direct test.
- Scale (thousands of cases; very large assertion fan-in): values live in case records with source metadata once in the catalog and per-case files off; module fusion is revisited only past a measured aggregator-schema limit.
- Objective extraction or policy fails: evidence is preserved in an assessment-failed record, never relabeled model failure.
- Persistence fails: no completed case, a retryable phase-tagged event, replay from the last commit.
- Anything in the model, generator, or runtime changes mid-study: fingerprint mismatch starts a new lineage.

---

## Vocabulary

- `forward model`: directed computation from fully supplied inputs to outputs; solves nothing.
- `constraint definition` / `constraint usage`: reusable Boolean predicate with formals / its application in context, owning or selecting the effective predicate.
- `concrete constraint`: one executable usage in one concrete owner instance.
- `executable profile`: the published decision procedure for whether an assertion may run.
- `model contract` / `package contract`: graph-derived semantic catalog / its artifact-hash seal.
- `constraint report`: assertion evidence and coverage for one design point; never a feasibility decision.
- `tracking_key`: optional author-controlled name correlating a logical constraint across model versions.
- `study policy`: user-selected interpretation of evidence for one exploration.
- `proposal` / `candidate` / `attempt` / `case` / `lineage`: raw strategy output, persisted even when invalid / validated logical evaluation (replicates distinct) / one execution try / a candidate's committed record / all cases sharing one compatibility binding.

---

## Validation Strategy

- Live-probe learning tests freeze the modeling-tool fact shapes (ownership, membership, negation, inheritance, bindings, compound ASTs) before any schema commits — and gate equality: for an equality expression the facts must classify both operands and prove compatibility, covering enum against its own enumeration, incompatible enums, integer/real promotion, quantities with the same unit, same-dimension different units, and incompatible dimensions, unit-bearing arithmetic, unitless versus dimensioned values, unresolved operands, and inherited or aliased types.
- Expression parity runs the live oracle in both source forms — typed usages via the proven two-step (evaluate the definition's predicate expression with the usage as scope), inline usages via their own result expression — against compiled Python over satisfied, violated, boundary, and non-finite points, with non-finite values in every Boolean position and the oracle asserting the documented three-valued truth table there rather than raw SysIDE equality (that divergence is by design), plus byte-stable serialization round-trips. The same spike decides the shared tree's relationship to the two existing expression representations — extend, extract-and-migrate, or predicate-focused with an explicit convergence path — never a silent third IR or a forced calculation rewrite; until it runs, this concept states the required properties of the neutral facts and deliberately leaves the canonical tree undeclared.
- Codegen: expansion (including a constraint-only part definition with multiple instances and inheritance), strict resolution, ID determinism, module-kind and schema generation, live/snapshot parity, and snapshot-rejection tests. Reachability is proved with pruning enabled and a minimal exit selection, so liveness comes from the constraint dependency rather than from every output already feeding the exit.
- Runtime: in-memory versus file-path parity, report precedence, phase-distinct failures, atomic commit with crash-resume, scalar-persistence regression pin.
- Acceptance: the IFE sweep's hand-coded viability rule is replaced by the generated assertion and every existing grid classification matches.

---

## Next-Stage Handoff

**Settled here:**
- Calculations compute, constraints judge, studies decide; silence is never an outcome.
- Per-assertion modules plus an exact-schema report aggregator, on the ordinary graph, are the execution shape.
- The graph owns one catalog and semantic contract; packaging seals them; study assessment never touches stored evidence.
- First scope: static scalar assertions (inline and definition-typed) with negation, owner-scope references or explicit actuals, Boolean composition; real-valued equality blocked pending a modeled-tolerance convention, other equality gated on proven type recovery.
- Strict actual resolution; defaulted formals keep their modeled defaults as overridable contract parameters, varied only by explicit study selection.

**Spec/design detail still needed next:**
- Exact fact/graph/report schemas, ID encoding, snapshot version, diagnostic taxonomy, package and evaluator APIs.
- Study, policy, store, and CLI contracts; failure-event and provenance shapes.
- The shared strict-resolution seam, the complete part-instance index, the normalized failure outcome, and the seal's full integrity protocol (coverage set, stale-file detection, environment compatibility).
- Migration of the drop manifest, both blanket warnings, existing tests, and the authoring guidance that currently teaches "constraints are not executable."

**First risk to de-risk:**
- Spikes S1 (fact shapes, all four source forms, equality typing matrix) and S5 (TEAx typed entry + scalar continuity) start immediately and in parallel — S1 blocks every schema, S5 depends on nothing upstream. Full scope, intent, and pass criteria for all six spikes: Appendix B.

---

## Summary

Modeled limits become traceable responses of the generated forward model — never exceptions, never solver hints, and never silent. A graph-owned, package-sealed contract lets the runtime evaluate one point or a whole study while violation evidence, feasibility policy, invalid candidates, and genuine breakage stay permanently distinct.

---

## Appendix A: Verification Verdict Summary

Three read-only sweeps, 2026-07-11, against sysml-codegen `main`, agentic-mbse HEAD (`d340c8e`), teax HEAD.

- **sysml-codegen** — confirmed: manifest-only constraint path (`constraint_report.py:62-75`); `constraints = []` stub (`extractor.py:197-198`); snapshot strips ASTs, serializes `dropped_constraints` (`serializer.py:35-43,108`); compiler is arithmetic-only with no Boolean node, and its `[` entry is a unit-annotation strip, not indexing (`expression_compiler.py:151-159,347-350`); Boolean flags not `module_kind` (`models.py:181-182`); graph seeded only from backtracked calc usages (`graph_builder.py:161,214`); `OutputRegistry`/`BindingResolution` exist as described (`core/output_registry.py:26`, `core/models.py:13-68`); templates/stencils float-specialized (`teax_module.py.jinja2:36,79,122`; `stencils.py:86-115`); fall-through entry synthesis with V11 at boundary (`dependency_backtracker.py:542-598`, `cli/__init__.py:228-270`); none of the proposed types exist; `constraint_extractor.py` deleted.
- **agentic-mbse** — confirmed: expression reconstruction handles comparison/logical/Boolean as display text only (`expression.py:377-448`); L4 placeholder reports 0% by design (`level4_constraints.py:57-69`); L6 blanket per-constraint warning (`level6_architecture.py:622-631`); adapter subtype sweep + droppability single-sourced (`syside_adapter.py:43,270,410-425`); no structural predicate, membership-kind, or negation capture anywhere; PUSH-DOWN shared modules establish the neutral-semantics-live-here pattern.
- **teax** — confirmed: validate → DAG → topological execution (`pipeline_validator.py:65`, `pipeline_graph.py:29-89`, `pipeline_executor.py:126`); executor breaks at the exit module so only exit ancestors are guaranteed (`pipeline_executor.py:131-139`); module exceptions escape, only validation errors caught (`pipeline.py:181-202`); inputs are file-only, no in-memory injection API; `RunResult` carries outputs/manifest/versions/metadata/provenance (`pipeline_executor.py:57-64`); zero study/sweep/constraint machinery repo-wide. Scalar-persistence caveat: an early read of the dirty working tree found scalar and `RootModel[scalar]` handlers in `output_router.py`, but those are uncommitted — HEAD `c9e1e85` still lacks them, and teax's `CURRENT_WORK.md` records the work as "Implementation Complete — audit and pre-PR verification pending." The prerequisite therefore stands: finish, audit, and merge that in-flight work before relying on it.

## Appendix B: De-risking Spikes — Scope, Intent, Pass Criteria

Six spikes (S1–S6) plus a deferred seventh (S7). Each names the assumption it tests; a spike that cannot fail is not run.

### S1 — Constraint fact-shape learning test (`agentic-mbse`, live SysIDE) — START FIRST

**Intent:** freeze the neutral fact schema against modeling-tool reality before any cross-repo schema commitment. Every schema in this design hangs on what S1 finds.
**Scope:** a committed fixture matrix and kept tests covering all four `ConstraintSource` forms (inline; definition-typed; assert-by-reference to a named usage with `:>>` rebinding; satisfy), membership kind read from the owning membership (require/assume), negation polarity, ownership (part-definition, calc-definition, direct usage), inheritance and retyping, anonymous assertions, actuals (owner-scope references, feature chains, literals, omitted defaulted formals), compound Booleans — and the type/unit matrix: enum against its own enumeration, incompatible enums, integer/real promotion, quantities with the same unit, same-dimension different units (detected, and blocked in first scope), incompatible dimensions, unit-bearing arithmetic, unitless versus dimensioned values, unresolved operands, inherited and aliased types. Emit golden JSON facts plus diagnostics.
**Pass/decision:** every field the design needs is recoverable without invoking the evaluator; any unrecoverable field is cut from the schema or becomes an explicit profile restriction. The equality gate (which operand categories are admitted) is decided by this evidence, not by assumption.

### S2 — Expression-tree parity and the IR relationship decision (`agentic-mbse` + `sysml-codegen`)

**Intent:** prove one neutral tree serializes byte-stably and compiles to Python that matches live semantics; decide, on evidence, how it relates to the two existing expression representations.
**Scope:** compile the WI-014 predicate, the IFE viability predicate, an inline owner-reference predicate, a negated assertion, and a compound Boolean. Run the live oracle in both source forms — typed usages via the proven two-step (definition's predicate expression, usage as scope), inline usages via their own result expression — over satisfied, violated, boundary, and non-finite points, including margin sign under negation and non-finite values in every Boolean position. At non-finite points the oracle asserts the documented three-valued (Kleene) truth table, not raw SysIDE equality — the IEEE divergence is by design. JSON round-trip every tree.
**Pass/decision:** Python and SysIDE agree on every supported point; disagreeing nodes are excluded from profile v1. Chooses extend / extract-and-migrate / predicate-focused-with-convergence, and fixes the operator/type matrix. Consumes S1's shapes.

### S3 — Concrete expansion and the instance index (`sysml-codegen`)

**Intent:** prove instance discovery independent of calc templates — the named risk that a constraint-only part definition currently has no discovered instances — and prove ID determinism through snapshot replay.
**Scope:** a constraint-only part definition with multiple instances; nesting; inheritance and retyping; multiplicity. Expand per instance, generate execution IDs, round-trip the snapshot, and prove rejection of both an old-version snapshot and a current-version snapshot missing the constraint-facts section.
**Pass/decision:** a complete part-instance index exists or the gap is named and becomes an explicit profile restriction; IDs and catalog ordering are byte-identical live and from snapshot. Can start once S1's fixtures exist, in parallel with S2.

### S4 — Vertical slice: lowering, liveness, generation, execution (`sysml-codegen` + TEAx)

**Intent:** prove the whole cross-repo seam on one real model — and make the liveness claim falsifiable.
**Scope:** feed S1's captured facts for WI-014's `affordable` through a test-only lowering path: strict resolution of `cost_calc.cost` and `plant_budget`, roots before pruning, one structured constraint module plus the exact-schema aggregator, schemas/registry/YAML/contracts. Run **with pruning enabled and a minimal exit selection**, so the cost calculation survives only via the constraint dependency — not because every output feeds the exit. Execute true and false points; compare live and snapshot artifacts.
**Pass/decision:** both truth values complete with identical ordinary outputs and the expected report; targeted generation retains the producer; live/snapshot artifacts match. Failure selects the exact graph or schema seam to redesign before production work. Consumes S1–S3.

### S5 — TEAx typed entry and scalar continuity (`teax`) — START IN PARALLEL WITH S1

**Intent:** prove prepare-once/fresh-context evaluation parity, and close the scalar story properly — finish rather than rediscover it.
**Scope:** prototype the typed in-memory entry source against an existing constraint-free generated graph: ~100 candidates, fresh contexts, `persist_outputs` off, compared with file-backed execution; missing, extra, wrong-type, and consecutive state-leak cases. Finish, audit, and merge the in-flight scalar ExitPoint persistence work, and add the direct ordinary producer-to-consumer scalar type-continuity test.
**Pass/decision:** mapping and file outputs match exactly; invalid mappings fail before any module runs; no state crosses cases; no files in no-persist mode. Measure preparation vs evaluation cost separately — if caching is not materially faster, keep the semantic API and drop the throughput claim. Depends on nothing upstream.

### S6 — Crash-safe study lifecycle, first-delivery scope (`teax`)

**Intent:** freeze the three-layer identity, atomic case commit, artifact staging, and the store's compatibility binding for list/grid studies. S6 deliberately does **not** claim to prove feedback crash semantics — a prepared-candidates strategy ignores feedback, so that claim would be unfalsifiable here.
**Scope:** prepared-candidates strategy, deterministic policy, SQLite store bound to its compatibility fields at creation, and a tiny evaluator covering all-satisfied, violation, indeterminate, invalid proposal (a `ProposalRecord`, never a case), execution failure, assessment failure, and zero assertions. Exercise the artifact staging protocol. Inject crashes before commit and mid-artifact-staging, then resume. Include deliberate replicates (distinct `candidate_id`, identical inputs) and a retry (same `candidate_id`, new `attempt_id`).
**Pass/decision:** resumed and uninterrupted runs produce identical ordered cases; no logical candidate commits twice under (`study_id`, `candidate_id`); no committed case references missing artifacts; invalid proposals persist as proposal records; opening the store with incompatible fingerprints fails. May run first against a fake evaluator, then repeat against S4's generated package.

### S7 — Adaptive-resume (`teax`, deferred; gates adaptive strategies)

**Intent:** settle general feedback transaction order — the part S6 cannot falsify.
**Scope:** a minimal stateful strategy whose next proposal depends on `observe()`; crash injected after case commit and before feedback delivery, then resume.
**Pass/decision:** feedback is delivered exactly once across the crash, and the resumed proposal sequence matches an uninterrupted run. No adaptive strategy ships before this passes.

### Order

S1 and S5 start immediately, in parallel. S2 and S3 follow S1 (S3 needs only its fixtures; S2 and S3 can run concurrently). S4 consumes S1–S3. S6 follows S5's evaluator protocol and finishes against S4's package. S7 is deferred with the adaptive work it gates. No production schema in any repo is committed before S1 and S2 conclude.
