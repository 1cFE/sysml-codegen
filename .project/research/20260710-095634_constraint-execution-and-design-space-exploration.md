# Constraint Execution and Design-Space Exploration

**Date:** 2026-07-10  
**Status:** Research complete  
**Scope:** How SysML constraints should become executable pipeline artifacts, who should evaluate them, and how their results should support design-space exploration (DSE).

## Executive Summary

Constraint execution should be split into evaluation and policy.

- **agentic-mbse owns SysML meaning.** It should expose neutral facts about constraint definitions, usages, parameters, predicates, membership kind, and negation. It should validate which shapes codegen supports.
- **sysml-codegen owns executable lowering.** It should instantiate each relevant constraint in a concrete model context, resolve its runtime inputs, compile its predicate, and add it to the computation graph.
- **TEAx owns ordinary execution.** It should run generated constraint modules and persist a typed result. A false constraint is data, not an execution failure.
- **The DSE driver owns study policy.** It decides whether a result excludes a point, incurs a penalty, raises a warning, contributes to probability of feasibility, or is displayed as a boundary.

The recommended first implementation is:

1. Lower each supported, concrete `assert constraint` usage to an ordinary graph module.
2. Have each module return a structured constraint result, or a Boolean plus metadata that is immediately collected into one structured report.
3. Add a generated `FeasibilityReport` aggregator and expose that report through the pipeline exit point.
4. Keep the pipeline successful when a predicate is false. Distinguish `completed_feasible`, `completed_infeasible`, and `execution_failed` at the study layer.

This fits the existing graph and TEAx scheduler. It also preserves the information needed for sweeps, optimization, uncertainty propagation, and visualization.

The hard part is not emitting `>=` in Python. The hard part is producing the correct concrete execution from SysML semantics. A predicate is defined on a reusable `ConstraintDefinition`; its actual bindings and execution context come from a `ConstraintUsage`. Constraints may also be inherited from a part definition or instantiated once per calculation usage. The current manifest does not represent any of that.

## Mental Model

There are three distinct layers.

### 1. A constraint is a model statement

A SysML `ConstraintDefinition` defines a Boolean predicate. A typed `ConstraintUsage` supplies the context and parameter bindings. An `assert constraint` says that predicate is expected to hold in that context.

The SysML v2 specification describes a constraint definition as a predicate with input parameters and an implicit Boolean result. It also permits intermediate calculation steps before the final expression. A constraint usage is satisfied when the predicate evaluates true and violated when it evaluates false (`agentic-mbse/docs/sysmlv2/SysML_Spec_v2_Part1/full_document.md:8052`, `:8058`, `:8069`, `:8135`).

An asserted constraint has stronger semantics than an ordinary predicate usage. SysML says it is asserted to be true and may be negated (`agentic-mbse/docs/sysmlv2/SysML_Spec_v2_Part1/full_document.md:8087`, `:8178`). That distinction must survive extraction.

### 2. Constraint execution evaluates one design state

For a concrete set of model inputs, codegen must:

- determine which concrete constraint instances exist;
- resolve every formal parameter to an entry point, attribute, or upstream calculation output;
- evaluate upstream calculations in dependency order;
- evaluate the predicate;
- record satisfied, violated, or indeterminate with source identity and diagnostics.

This is a forward-model operation. It answers: "For this design point, what happened?"

### 3. DSE interprets many evaluations

A sweep, optimizer, or uncertainty study asks different questions:

- Which points are feasible?
- How close is a point to a boundary?
- Which constraint is active or violated?
- What fraction of uncertain samples are feasible?
- Should a violation exclude a point, add a penalty, or only warn?

Those are study-policy decisions. They do not belong in the predicate compiler or the TEAx scheduler.

## What Exists Today

### Detection and reporting only

The live pipeline detects constraints after calculation definitions and before calculation usages. It only reports them (`src/sysml_codegen/orchestration/pipeline_builder.py:741`).

The subtype-aware collector classifies usages as assert, satisfy, requirement, or plain (`src/sysml_codegen/extraction/extractor.py:112`). Its manifest stores only:

- owner kind;
- owner name and qualified name;
- constraint name and kind;
- source line.

The carrier is `ConstraintManifestEntry` (`src/sysml_codegen/extraction/constraint_report.py:62`). It does not contain the predicate, constraint-definition identity, parameters, bindings, negation, instance identity, or a result channel.

Part-definition extraction still sets `constraints = []` (`src/sysml_codegen/extraction/extractor.py:197`). The older extraction path recognized a result expression, but it was reporting-oriented and used textual reference matching rather than the runtime resolver.

Snapshot v2 serializes this reporting manifest as `dropped_constraints` (`src/sysml_codegen/snapshot/serializer.py:83`). Raw AST references are deliberately removed during serialization (`src/sysml_codegen/snapshot/serializer.py:35`). Executable constraint facts therefore require a snapshot schema change, not an interpretation of the current warning record.

### No executable Boolean compiler path

The executable expression IR currently supports arithmetic operators and indexing (`src/sysml_codegen/extraction/expression_compiler.py:151`). Its builder accepts numeric literals and calculation-local references, and rejects comparison and logical operators (`src/sysml_codegen/extraction/expression_compiler.py:294`). It has no Boolean literal node.

agentic-mbse's shared expression reconstruction already understands comparisons, logical operators, and Boolean literals (`agentic_mbse/src/agentic_mbse/sysml/expression.py:377`, `:420`). That code is useful for neutral semantic facts and display. It is not an executable compiler and should not be converted to Python through reconstructed text or `eval`.

The graph model can describe a Boolean output (`src/sysml_codegen/resolution/models.py:141`), and pipeline YAML can render generic root-model output types (`src/sysml_codegen/generation/pipeline.py:186`). The generated TEAx module wrapper and stencils are still specialized to `Float` and `float` (`src/sysml_codegen/templates/teax_module.py.jinja2:33`, `src/sysml_codegen/generation/stencils.py:80`). Boolean support therefore crosses extraction, resolution, generation, and snapshot boundaries.

### Constraints do not participate in reachability

The computation graph is built from calculation usages selected by dependency backtracking (`src/sysml_codegen/resolution/graph_builder.py:237`). If a constraint is the only consumer of a calculation output, adding it after backtracking can leave its producer out of a targeted graph.

Enabled constraints must be graph roots, or their dependencies must be incorporated into backtracking before pruning. Input resolution should reuse the output registry and structured binding-resolution machinery. A second leaf-name or regular-expression resolver would recreate bugs that the recent pipeline epics removed.

### TEAx can schedule this, but does not know constraints

TEAx validates typed module inputs and outputs, builds a DAG, and executes modules in topological order (`teax/packages/teax-simkit/simkit/core/pipeline_validator.py:330`, `teax/packages/teax-simkit/simkit/core/pipeline_graph.py:29`, `teax/packages/teax-simkit/simkit/core/pipeline_executor.py:181`). It does not need SysML-specific constraint semantics to evaluate a generated module.

There is one important graph contract: the executor stops after the exit point. A constraint node must be an ancestor of that exit point to be guaranteed to run (`teax/packages/teax-simkit/simkit/core/pipeline_executor.py:125`). A generated feasibility aggregator gives every constraint an explicit path to one exit artifact.

Module exceptions are not an appropriate representation of violation. Exceptions escape module execution, and the public pipeline catches only pipeline-validation errors (`teax/packages/teax-simkit/simkit/core/pipeline.py:180`). An exception can prevent final output persistence and makes an infeasible design indistinguishable from broken code or invalid input.

### The current DSE already demonstrates the desired behavior

The IFE sweep evaluates 11,505 points by calling generated implementation functions directly (`fusion-tea/exploration/ife_e2e/sweep_ife.py:59`). It records raw outputs and separate classifications for positive power, the SysML viability relation, and economic attractiveness (`fusion-tea/exploration/ife_e2e/sweep_ife.py:77`).

That organization is correct in principle:

- physical outputs remain observable;
- a false constraint does not erase the point;
- multiple policies can classify the same output;
- plotting can show boundaries and tradeoffs (`fusion-tea/exploration/ife_e2e/plot_sweep.py:33`).

The workaround is that the viability predicate is reimplemented in the sweep rather than generated from SysML. Constraint execution should remove that duplication while preserving the data-first behavior.

## Semantic and Engineering Challenges

### Definition versus usage

The predicate normally lives on the `ConstraintDefinition`. Actual parameter bindings live on the typed usage. The committed WI-014 evaluation found that asking SysIDE to evaluate the usage returned the usage object; evaluating the definition predicate in the usage scope produced the Boolean result (`fusion-tea/work/completed/20260705_WI-014_sysml-wiring-construct-validation/findings.md:33`).

The implementation must explicitly lower the pair. It cannot assume that `ConstraintUsage.result_expression` always contains the executable body.

### Concrete instantiation

A definition is reusable and is not itself one execution.

- A constraint owned by a calculation definition may need one execution per calculation usage, using that usage's inputs and outputs.
- A constraint owned by a part definition may need one execution per concrete part usage, including inherited constraints.
- A constraint owned directly by a part usage executes in that instance.

The current owner-level manifest cannot identify these instances. The IFE model demonstrates the issue: the predicate is defined in the analysis library, bound in the generic IFE plant, and inherited by HIF (`fusion-tea/exploration/ife_e2e/models/analyses/fusion_cycle.sysml:29`, `fusion-tea/exploration/ife_e2e/models/designs/generic_ife/ife_plant.sysml:153`, `fusion-tea/exploration/ife_e2e/models/designs/hif/hif_plant.sysml:221`).

### Membership semantics and negation

The current `PLAIN` classification loses the distinction between `require` and `assume`; that distinction is carried by the membership, not necessarily the usage (`agentic-mbse/docs/subtype-enumeration-decision-table.md:33`). `assert not` also changes the expected truth value.

Execution must preserve semantic kind and polarity. Policy should not silently treat ordinary constraints, asserted invariants, assumptions, and requirement satisfaction as identical hard feasibility checks.

### Static versus temporal semantics

SysML describes an asserted invariant as holding throughout its context. Evaluating a generated static forward model checks one design state. It does not prove a temporal invariant over a dynamic simulation.

The first epic should explicitly implement **static point evaluation**. Time-series monitoring, event semantics, and temporal coverage need a separate design.

### Boolean result versus useful response

A Boolean partitions a sweep into feasible and infeasible regions. It is insufficient for many optimizers, which need a residual or margin to choose a direction and identify active constraints.

For a simple inequality, codegen can preserve an optional signed margin:

- `lhs >= rhs`: `lhs - rhs`;
- `lhs <= rhs`: `rhs - lhs`;
- satisfied when margin is non-negative.

That rule does not generalize cleanly to compound logic, strings, equality without a tolerance, or arbitrary predicates. The compiler should never invent a universal normalized penalty. It should retain a numeric response where the source structure supports one and otherwise report Boolean status only.

## Design Alternatives

### Alternative A: Evaluate through live SysIDE

**Shape:** Load the SysML model and ask SysIDE to evaluate each predicate in the usage scope.

**Benefits**

- Closest available executable reference for SysML semantics.
- Useful as a development oracle and acceptance comparison.
- Avoids implementing the predicate compiler initially.

**Costs**

- Requires a live licensed modeling environment.
- Cannot execute from the committed snapshot representation.
- Bypasses the generated computation graph and TEAx runtime.
- Does not establish deployable generated artifacts.
- Makes DSE throughput and reproducibility dependent on the modeling tool.

**Assessment:** Use for spikes and conformance tests, not production execution.

### Alternative B: Evaluate after the run in a harness

**Shape:** Read generated result files and reimplement predicates in a sweep or reporting script.

**Benefits**

- Lowest initial implementation cost.
- Mirrors the current IFE sweep.
- Keeps violation from aborting the pipeline.

**Costs**

- Duplicates model logic and can drift from SysML.
- Cannot reliably access internal or pruned values.
- Recreates name-resolution and ordering logic outside the graph.
- Weak provenance and poor support for reusable generated models.

**Assessment:** A temporary reference path only. This is the workaround the epic should retire.

### Alternative C: Embed assertions in producer modules

**Shape:** Add Python assertions or Pydantic validators to modules that produce constrained values.

**Benefits**

- Simple for a local range check.
- Can fail early on invalid numerical domains.

**Costs**

- Cross-module predicates have no single natural producer.
- Exceptions erase useful infeasible points and downstream outputs.
- Constraint policy becomes mixed into calculation implementation.
- Inheritance, binding identity, and source reporting remain unsolved.

**Assessment:** Wrong default for DSE. Reserve explicit failure for invalid execution domains, not ordinary infeasibility.

### Alternative D: Ordinary constraint modules with Boolean outputs

**Shape:** Each concrete constraint usage becomes a graph module that consumes resolved values and emits `bool`.

**Benefits**

- Reuses the current graph, scheduler, dependency resolution, and provenance model.
- Makes constraints work in live and snapshot generation.
- Gives DSE a direct generated result.
- Keeps TEAx independent of SysML.

**Costs**

- Requires concrete usage instantiation and reachability changes.
- Requires Boolean expression and wrapper generation.
- A bare Boolean lacks source metadata, diagnostics, and margin.
- Every result must feed the exit point or it may not run.

**Assessment:** Correct evaluation mechanism, but not a complete output contract by itself.

### Alternative E: Constraint modules plus a feasibility-report aggregator

**Shape:** Generate ordinary constraint modules and one aggregator that collects their results into a typed `FeasibilityReport` exposed at the exit point.

**Benefits**

- Keeps execution on the normal graph.
- Guarantees all enabled constraints are ancestors of the exit point.
- Avoids a primitive-output routing contract for many Boolean files.
- Provides one stable artifact for CLI runs, sweeps, provenance, and UIs.
- Can represent violated and indeterminate states without throwing.

**Costs**

- Introduces a generated report schema and deterministic aggregation contract.
- Needs stable constraint IDs and result ordering.
- The report must avoid carrying values that are expensive or unsafe to serialize.

**Assessment:** Recommended first production architecture.

### Alternative F: Add a first-class TEAx constraint engine

**Shape:** Teach TEAx about constraints, violation policy, severity, and possibly penalties.

**Benefits**

- A generic runtime could standardize reporting across non-SysML producers.
- Later study tooling could consume a common response protocol.

**Costs**

- Couples a generic executor to modeling-language semantics prematurely.
- Does not remove the need for SysML instantiation, binding, and compilation.
- Encourages execution failure to become mixed with infeasibility.
- Places optimizer-specific policy in the single-run runtime.

**Assessment:** Do not put SysML evaluation in TEAx. TEAx may later define a language-neutral constraint-result protocol after multiple producers need it.

### Alternative G: Generate an in-memory DSE evaluator

**Shape:** Alongside the TEAx pipeline, generate a callable `evaluate_design_point()` facade that uses the same compiled calculation and constraint functions but avoids per-point file I/O.

**Benefits**

- Suitable for thousands of sweep points.
- Supports vectorization, parallel workers, and later JAX backends.
- Keeps single-run TEAx artifacts and high-throughput studies semantically aligned.

**Costs**

- Creates a second orchestration adapter that must share, not duplicate, graph semantics.
- Needs explicit parity tests with the TEAx execution path.
- Does not solve extraction or constraint lowering by itself.

**Assessment:** A complementary second phase. TEAx remains the auditable single-run executor; the generated facade becomes the high-throughput study interface.

## Recommended Architecture

### agentic-mbse: neutral SysML facts and validation

Add shared representations or helpers for:

- constraint definition identity and qualified name;
- formal parameters and defaults;
- structural predicate IR or neutral expression facts;
- usage-to-definition relation;
- owned bindings;
- containing membership kind (`assert`, `require`, `assume`, `satisfy`, ordinary);
- negation;
- source location and documentation;
- inherited ownership facts.

Add a codegen-compatible constraint profile. It should report the exact unsupported construct instead of warning that every constraint is dropped. The current L4 check does not populate constrained attributes (`agentic-mbse/src/agentic_mbse/validation/level4_constraints.py:44`), and L6 emits the blanket dropped-predicate warning (`agentic-mbse/src/agentic_mbse/validation/level6_architecture.py:595`).

### sysml-codegen: instantiation, resolution, and compilation

Introduce explicit data models for:

- `ConstraintDefinitionData`: definition, parameters, predicate IR, source;
- `ConstraintUsageData`: concrete owner instance, definition, binding actuals, semantic kind, polarity;
- `ConstraintResultDescriptor`: stable ID, result channel, metadata required by the report.

Then:

1. Expand inherited and definition-owned constraints into concrete usages.
2. Resolve bindings through the existing output registry and qualified-name mechanisms.
3. Add enabled constraints as dependency roots before pruning.
4. Compile predicates structurally. Add comparison, Boolean literal, `and`, `or`, and `not` support. Reject unsupported nodes explicitly.
5. Add a real module kind rather than a third classification Boolean beside `is_computed_attribute` and `is_aggregation` (`src/sysml_codegen/resolution/models.py:141`, `src/sysml_codegen/generation/registry.py:220`).
6. Generate typed modules and a deterministic feasibility-report aggregator.
7. Serialize the executable semantic facts in a new snapshot version and test live/snapshot parity.

### TEAx: generic execution and persistence

TEAx should:

- validate and schedule the generated modules normally;
- persist the feasibility report as a regular typed exit artifact;
- report calculation exceptions as execution failures;
- leave false predicates as successful module results.

TEAx should not:

- parse SysML expressions;
- infer assert, require, or assume policy;
- assign optimizer penalties;
- terminate a run solely because a supported predicate returned false.

### DSE and optimization: study policy

The study layer consumes outputs plus the feasibility report. It may:

- filter hard-infeasible points;
- retain them for boundary plots and diagnostics;
- apply study-specific penalties;
- treat advisory checks as annotations;
- aggregate per-sample results into probability of feasibility;
- expose numeric margins as optimizer constraint responses;
- distinguish model-domain failures from constraint violations.

This follows the design used by established multidisciplinary optimization tools. OpenMDAO models expose constraint response variables and bounds, while the driver retrieves values and computes violations. The DOE driver runs and records many cases. Evaluation remains in the model; study policy remains in the driver. See [OpenMDAO constraint responses](https://openmdao.org/newdocs/versions/latest/features/core_features/adding_desvars_cons_objs/adding_constraint.html), [driver violation handling](https://openmdao.org/newdocs/versions/latest/_modules/openmdao/core/driver.html), and [DOE driver](https://openmdao.org/newdocs/versions/latest/features/building_blocks/drivers/doe_driver.html).

## Proposed Result Contract

The exact schema belongs in design, but the research indicates this minimum shape:

```text
FeasibilityReport
  evaluation_status: completed_feasible | completed_infeasible | indeterminate
  results: ConstraintEvaluation[]

ConstraintEvaluation
  constraint_id: stable generated identity
  source_qualified_name: source definition or usage
  owner_instance_qualified_name: concrete execution context
  semantic_kind: assert | require | assume | satisfy | predicate
  expected_value: true | false
  actual_value: true | false | unknown
  status: satisfied | violated | indeterminate
  margin: optional numeric value
  message: optional bounded diagnostic
  source_location: file and line when available
```

The report should not decide hard versus soft feasibility unless that policy is explicitly modeled or supplied by the study. Existing examples do not establish a reliable severity convention.

For optimization, preserve a numeric response and bound where possible instead of reducing every inequality to Boolean. For example, retain `eta * gain` with a lower bound of `threshold`, or retain a signed residual. The Boolean result is still useful for reporting and arbitrary predicates.

## Fit With the Larger DSE Vision

### Dense sweeps

The first payoff is replacing hand-coded classifications in the IFE and MFE sweeps. A false point completes, records its outputs and violated constraints, and remains available for plots. This directly supports the stated workflow of varying inputs, observing outputs, and checking constraints (`fusion-tea/modeling_project/HYPOTHESIS_DOSSIER.md:74`).

### Higher-dimensional optimization

Dense grids become expensive as dimensions increase. An optimizer needs objective values and smooth or at least informative constraint responses. The inverse-solving backlog already considers sweep/interpolation and JAX-based engines (`fusion-tea/work/backlog/epic-inverse-solving.md:17`).

The initial IR should therefore avoid a Boolean-only dead end. Preserve expression structure and optional margins so a later backend can lower supported numerical predicates to NumPy or JAX without re-extracting SysML.

### Uncertainty propagation

Monte Carlo and range studies evaluate the same design many times. A violation is an outcome, not an exception. The study can calculate:

- probability that each constraint is satisfied;
- probability that all hard constraints are satisfied;
- distributions of margins;
- sensitivity of feasibility to uncertain inputs.

This aligns with the uncertainty-propagation backlog (`fusion-tea/work/backlog/epic-uncertainty-propagation.md:13`). Collapsing a run to pass/fail inside TEAx would discard the evidence these studies need.

### Discrete and qualitative design spaces

The existing ATMS spike represents logical propagation and contradictions over partial architecture choices (`fusion-tea/exploration/spike_constraint_atms.py:1`). That is a different execution problem from evaluating a numerical predicate at a complete design point.

The two systems may eventually publish results into a common design-state record, but they should not share an evaluator prematurely:

- generated numerical constraints evaluate concrete values;
- an ATMS or solver propagates propositions over incomplete or discrete choices.

### Preconditions and numerical-domain guards

Some checks protect a calculation from invalid inputs, such as division by zero or an invalid physical domain. These may need staged execution or early gating. They should be distinguished from ordinary feasibility constraints because downstream calculations may be undefined.

The first constraint-execution epic should not silently use exceptions for both. A later policy can define `not_evaluated` or `indeterminate` results for constraints whose prerequisites failed.

## Recommended First-Epic Scope

Support static, scalar, typed part-level `assert constraint` usages with:

- one `ConstraintDefinition` predicate;
- explicit parameter bindings and definition defaults;
- local attributes, entry-point values, and calculation outputs;
- inherited part-definition constraints instantiated on concrete part usages;
- comparison operators and basic Boolean composition;
- `assert not` polarity;
- structured report output;
- live and snapshot generation parity;
- annotate-don't-halt behavior.

Explicitly defer:

- temporal invariants and time-series monitoring;
- `satisfy requirement` execution;
- policy for `require` versus `assume`;
- arbitrary function invocation and conditionals until the expression compiler supports them;
- universal margin or penalty synthesis;
- JAX/autodiff lowering;
- qualitative/discrete ATMS reasoning;
- hard/soft severity unless a source-of-truth convention is approved.

## Required Discovery Spike

Before the detailed design, run a live SysIDE probe against committed fixtures and record:

1. Inline constraint usage versus typed-definition predicate ownership.
2. Parameter binding representation and inherited default behavior.
3. Membership representation for `require` and `assume`.
4. `AssertConstraintUsage.is_negated` behavior.
5. Inherited part-definition constraint enumeration and owner context.
6. Constraint definitions nested in calculations and their per-usage scope.
7. Compound Boolean expression AST shapes and operator precedence.

The existing snapshot cannot answer these questions because it stores only dropped-constraint manifest rows.

## Acceptance Tests for the Epic

- The committed IFE viability constraint is generated from SysML and replaces the sweep's hand-coded formula.
- Changing `eta` or `gain` changes the constraint result through resolved runtime inputs.
- A false constraint completes the pipeline and produces `completed_infeasible` with normal calculation outputs intact.
- A calculation exception produces `execution_failed`, not `completed_infeasible`.
- A constraint that is the only consumer of a calculation output still pulls that calculation into a targeted graph.
- Definition defaults, usage bindings, inherited constraints, and negated assertions each have focused tests.
- Cross-part qualified bindings do not use leaf-name fallback.
- Unsupported predicate constructs fail generation with the constraint identity and exact unsupported AST shape.
- Live and snapshot generation produce equivalent constraint modules and report descriptors.
- TEAx executes every enabled constraint because the report aggregator is an ancestor of the exit point.
- A high-throughput evaluator, when added, matches TEAx results for the same design point.

## Risks and Design Decisions Still Needed

1. **Stable identity:** Define how a reusable definition plus concrete owner instance maps to a deterministic constraint ID.
2. **Report payload:** Decide whether parameter actuals and margins are included directly or referenced through provenance to control artifact size.
3. **Module granularity:** One module per constraint gives clear provenance. A fused evaluator reduces module count. The first design should measure the number of asserted concrete constraints in target models before choosing.
4. **Numeric types and units:** Define whether comparison operands are normalized before evaluation and how margin units are recorded.
5. **Equality tolerance:** Exact floating-point equality is rarely a useful feasibility rule. Tolerance must be modeled or configured explicitly.
6. **Indeterminate state:** Define behavior when a prerequisite calculation fails or a value is missing.
7. **Policy source:** Decide where a study declares hard, soft, advisory, or objective roles. Do not infer these roles from names.
8. **Snapshot versioning:** Executable semantic facts require a version bump and migration/error policy.
9. **Throughput boundary:** Decide when the generated in-memory evaluator becomes part of the epic versus a follow-on DSE integration item.

## Recommendation

Proceed with a constraint-execution epic whose architectural center is **concrete constraint modules plus a typed feasibility-report aggregator**.

Do not frame the epic as "make SysML constraints throw errors." That behavior conflicts with design-space exploration. Frame it as "make modeled predicates observable, traceable responses of the generated forward model."

Start with the SysIDE semantic spike. Then design the executable constraint data model and snapshot representation before extending the compiler. That sequence forces the project to solve definition/usage identity, bindings, inheritance, and policy boundaries before code generation makes those assumptions difficult to change.

## Source Index

### sysml-codegen

- Detection stage: `src/sysml_codegen/orchestration/pipeline_builder.py:741`
- Constraint enumeration/classification: `src/sysml_codegen/extraction/extractor.py:112`
- Reporting manifest: `src/sysml_codegen/extraction/constraint_report.py:62`
- Part-definition constraint stub: `src/sysml_codegen/extraction/extractor.py:197`
- Snapshot serialization: `src/sysml_codegen/snapshot/serializer.py:35`, `:83`
- Arithmetic-only expression compiler: `src/sysml_codegen/extraction/expression_compiler.py:151`, `:294`
- Graph construction and reachability: `src/sysml_codegen/resolution/graph_builder.py:237`
- Module representation: `src/sysml_codegen/resolution/models.py:141`
- Generation registry partitioning: `src/sysml_codegen/generation/registry.py:220`
- Float-specialized wrapper/stencils: `src/sysml_codegen/templates/teax_module.py.jinja2:33`; `src/sysml_codegen/generation/stencils.py:80`
- Current documented deferral: `docs/architecture/modeling-assumptions.md:400`

### agentic-mbse and SysML

- Expression reconstruction: `agentic-mbse/src/agentic_mbse/sysml/expression.py:377`, `:420`
- Constraint validation gaps: `agentic-mbse/src/agentic_mbse/validation/level4_constraints.py:44`; `agentic-mbse/src/agentic_mbse/validation/level6_architecture.py:595`
- Membership subtype distinction: `agentic-mbse/docs/subtype-enumeration-decision-table.md:33`
- SysML constraint semantics: `agentic-mbse/docs/sysmlv2/SysML_Spec_v2_Part1/full_document.md:8052`, `:8069`, `:8087`, `:8135`, `:8178`

### TEAx and DSE

- TEAx DAG validation and execution: `teax/packages/teax-simkit/simkit/core/pipeline_validator.py:330`; `teax/packages/teax-simkit/simkit/core/pipeline_graph.py:29`; `teax/packages/teax-simkit/simkit/core/pipeline_executor.py:125`, `:181`
- TEAx public error handling: `teax/packages/teax-simkit/simkit/core/pipeline.py:180`
- Current IFE sweep classification: `fusion-tea/exploration/ife_e2e/sweep_ife.py:59`, `:77`
- WI-014 evaluation finding: `fusion-tea/work/completed/20260705_WI-014_sysml-wiring-construct-validation/findings.md:33`
- DSE hypothesis: `fusion-tea/modeling_project/HYPOTHESIS_DOSSIER.md:74`
- Inverse solving: `fusion-tea/work/backlog/epic-inverse-solving.md:17`
- Uncertainty propagation: `fusion-tea/work/backlog/epic-uncertainty-propagation.md:13`

