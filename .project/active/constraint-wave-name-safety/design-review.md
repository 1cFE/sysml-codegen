# Design Review: Generated Constraint Name-Safety Boundary

**Design:** `.project/active/constraint-wave-name-safety/design.md`
**Spec:** `.project/active/constraint-wave-name-safety/spec.md`
**Review File:** `.project/active/constraint-wave-name-safety/design-review.md`
**Date:** 2026-07-18

---

## Fundamental Assessment

**Concerns.** The core approach is right: retain the minimal source identity already present,
validate the predicate and wrapper as separate Python scopes, compare them at package preflight,
and reject instead of renaming. This fits the existing graph-first generation shape and avoids
catalog or snapshot schema expansion.

The design is not ready to plan. Its lower-boundary story contradicts the revised spec's
no-mutation rule, its exception-normalization path does not preserve the structured facts it says
it preserves, and its AST completeness algorithm is underspecified enough to miss real Python
bindings. These are repairable design defects rather than a reason to replace the approach.

---

## Dimensional Review

### 1. Spec Compliance

**Assessment:** Fail

- **The direct write path is not preflighted.** The spec requires direct generation APIs to return
  the same rejection before their first write (`spec.md:76-79, 98-103`). The design instead says
  `_generate_modules()` remains a write phase protected by per-compiler and per-wrapper rechecks,
  and limits whole-tree preservation to `run_codegen()` (`design.md:211-223`). Today
  `_generate_modules()` creates the constraint namespace and writes `predicates.py` before it
  renders any wrapper (`src/sysml_codegen/cli/__init__.py:333-395`). A wrapper-only `self`,
  `verdict`, sanitizer-collapse, missing-provenance, or correspondence violation can therefore
  mutate the tree before rejection. Recommendation: run the full graph validator at the start of
  `_generate_modules()` as a defense for that directly called write API, before `mkdir`, package
  init creation, or `predicates.py`; retain the earlier `run_codegen()` call for the whole pipeline.
- **The AST completeness design does not yet meet the semantic coverage criterion.** D6 says to
  subtract injected model bindings from AST-observed bound names, but B3 and the risk note narrow
  observation to arguments and assignment targets (`design.md:100-102, 138-143, 339-342`). Python
  also binds names through annotated/augmented assignment, loop and `with` targets, exception
  handlers, imports, named expressions, and nested function/class definitions; comprehensions add
  a separate scope. A hand-written partial visitor can go green while a new generated local remains
  absent from policy. Recommendation: define a scope-correct semantic extractor, preferably Python's
  symbol-table view over the exact predicate function and wrapper `run` function, or enumerate and
  test every binding form and nested-scope rule. Mutation probes must exercise more than ordinary
  `Assign` and arguments.
- **Collision-free bytes are addressed well.** I9/I10, dump exclusion, the detached baseline/candidate
  package comparison, and fresh-process execution together cover emitted files, contracts,
  fingerprints, seals, signatures, wiring, and behavior (`design.md:256-259, 335-346, 400-433`). Add
  a direct assertion that `ComputationGraph.model_dump()` and the model contract omit the carrier;
  this makes the no-schema/payload-churn claim local rather than relying only on the final byte diff.
- **Capture fidelity needs correction.** Every decision in the revised spec is `[INFERRED]` and the
  spec explicitly calls the contract agent-shaped (`spec.md:25-27, 58-112`). The design may choose
  among those items, but its handoff says D1-D7 and I1-I10 are “fixed” (`design.md:435-438`). That
  silently hardens challengeable agent-grade requirements into settled instructions. Recommendation:
  say the plan should implement the approved design unless new evidence invalidates a bet or
  inferred premise. There is no owner-originated referent in this spec to preserve or flag as
  dropped; the R-3 reproduction is carried as inherited evidence rather than an owner bar.

### 2. Pattern Consistency

**Assessment:** Concerns

- The proposed preflight beside the landed predicate-name, output-path, and coverage checks follows
  the existing safe pattern (`src/sysml_codegen/cli/__init__.py:968-985`). The shared pure validator
  also avoids duplicating deny lists.
- The design must extend that same pattern to `_generate_modules()`. Existing tests call this writer
  directly (`tests/execution/test_constraint_execution.py:65` and
  `tests/conformance/test_constraint_generation_integration.py:148`), so treating it as protected
  merely because its renderers validate piecemeal is inconsistent with the spec and with package
  preflight semantics.
- Dependency direction is viable if kept explicit: `resolution.models` owns the data-only identity;
  `generation.constraint_name_safety` may import resolution and companion IR types; compiler,
  modules, and CLI may import the validator. The new module must not import the `generation` package
  facade or CLI to construct public errors, because that facade imports `generation.modules` and
  would risk a cycle. Boundary adapters should construct public exceptions.

### 3. Abstraction Quality

**Assessment:** Concerns

- One small policy/validator module earns its existence. The same collision vocabulary and ordering
  must serve compiler, renderer, `_generate_modules()`, and orchestration, while the two name
  derivations remain separate.
- The ownership text conflicts. D3 places `ConstraintFormalIdentity` in `resolution/models.py`, while
  the component list says `constraint_name_safety.py` owns “formal identity” records
  (`design.md:116-123, 264-270`). Keep the carrier in resolution and keep policy binding/violation
  records in generation. Naming those responsibilities precisely will prevent duplicate record
  types.
- The graph validator is doing useful integrity work when it rejects duplicate or missing module
  joins before comparison (`design.md:326-327`). That turns B2 from an unsafe assumption into a
  checked invariant and should be stated that way.

### 4. Duplication Avoidance

**Assessment:** Pass

The design centralizes inventories, validation, deterministic selection, and formatting while
leaving final-name derivation at the existing predicate and lowering boundaries. It avoids a
catalog-side copy and an orchestration side map. Repeating the pure full-graph preflight at two
write entry points is intentional boundary defense, not duplicated policy.

### 5. Data Structure Clarity

**Assessment:** Concerns

- The two-field immutable carrier is minimal and compatible with the actual structures.
  `FeatureReferenceFact` already serializes `source_name` and target identity in predicate IR;
  `ConcreteConstraintInput` is the pre-graph carrier; `ModuleInput` is copied into the final graph
  (`constraint_lowering.py:970-1049, 1205-1238`; `resolution/models.py:141-156, 268-308`). No
  catalog field is needed.
- The design names the broad construction routes, including definition formals, inline leaves,
  legacy actuals, and omitted defaults (`design.md:153-167, 271-273`). It should add a constructor
  matrix that states the exact identity on both sides for each route. In particular, the legacy
  non-definition path currently starts from an `ActualFact.name` dictionary while the predicate
  side starts from `FeatureReferenceFact.source_name`/target (`constraint_lowering.py:971-1018`).
  “Use the single formal target when extraction supplies it” is not precise enough to prove those
  keys match. Define the source field and fallback for each route, then test the matrix on live and
  snapshot graph rebuilds.
- `Field(exclude=True)` is appropriate for payload stability and `model_copy(deep=True)` should
  retain it. The design correctly fails closed when provenance is absent. Add checks for
  `model_dump(mode="python")`, `model_dump(mode="json")`, the graph dump, and model-contract bytes;
  `exclude=True` affects dumps but should not be described as preventing every possible Pydantic
  JSON-schema change unless that surface is also tested.

### 6. Route Safety

**Assessment:** Fail

There are no HTTP routes. The relevant routes are live orchestration, snapshot orchestration,
direct compilation, direct rendering, and direct module generation.

- Live and snapshot builds both reconstruct constraint inputs and converge on a `ComputationGraph`
  before `run_codegen()` preflights, so the proposed graph check covers both orchestration routes.
- Direct compiler and direct renderer checks occur before source is returned and are correctly
  scoped to their final bindings.
- Direct `_generate_modules()` is unsafe as designed because it writes shared predicates and can
  write earlier modules before a later wrapper/correspondence rejection. It needs full-graph
  preflight at function entry.

### 7. Bets & Decisions Integrity

**Assessment:** Concerns

- B1 is supported for definition and inline paths by current `FormalFact` and
  `FeatureReferenceFact` data. Its unresolved raw-name fallback is honest about information the
  extractor did not provide.
- B2 is mislabeled as a bet. The design already requires the graph validator to reject missing or
  duplicate module/catalog joins. Make one-wrapper/one-entry a checked invariant, not a belief that
  could let a wrapper bypass validation.
- B3 is too weak. “Syntactically visible” does not prove the proposed AST collector recognizes every
  binding or assigns it to the correct Python scope. The hidden bet is that the collector implements
  Python symbol binding completely. State that bet and remove it by using a scope-aware semantic
  source or comprehensive binding-form tests.
- D5 does not describe a realizable structured-fact path. `PredicateCompileError` is currently an
  empty exception subclass carrying only the message supplied at construction
  (`predicate_compiler.py:99-100`). D5 first converts the internal violation to that public error,
  then says `compile_shared_predicates()` converts it to `CodeGenerationError` “with the structured
  facts intact” (`design.md:130-136`). Define one mechanism: attach the immutable violation as a
  typed attribute/cause on `PredicateCompileError`, or have `compile_shared_predicates()` run the
  shared inventory validator itself and adapt the internal violation directly. Also define whether
  non-name compiler failures are normalized; the spec asks package generation to expose
  `CodeGenerationError`, while current `compile_shared_predicates()` lets all
  `PredicateCompileError`s escape (`generation/modules.py:131-174`).

### 8. Reader Comprehension

**Assessment:** Pass

The document gives a usable mental model before implementation detail, distinguishes identity from
final binding, and traces package and direct-call flows. The problems above are technical omissions,
not voice failures.

---

## Issues by Severity

### Critical

- None.

### Major

- **M1 — Direct module generation mutates before wrapper rejection.** `_generate_modules()` writes
  shared predicates and possibly earlier modules before its per-wrapper checks, contrary to the
  direct-API no-write success criterion. — Spec Compliance / Route Safety
- **M2 — Structured collision facts have no defined path through public exceptions.** The current
  compiler exception is message-only, so D5 cannot both normalize early and retain the structured
  record without an explicit carrier or a second direct validation. — Bets & Decisions Integrity
- **M3 — Completeness checking does not define complete Python binding semantics.** Arguments plus
  assignment targets can miss generated locals or misattribute nested-scope bindings. — Spec
  Compliance / Bets & Decisions Integrity
- **M4 — Raw identity threading lacks an exact route matrix.** The legacy non-definition route does
  not name the precise field used on each side, so predicate/wrapper equality is not proven for all
  current lowering paths. — Data Structure Clarity

### Minor

- **m1 — Agent-grade decisions are called fixed.** This loses the revised spec's `[INFERRED]`
  provenance and makes challengeable design choices look settled. — Spec Compliance
- **m2 — Identity-record ownership is inconsistent.** Resolution should own the carrier; generation
  should own policy binding and violation records. — Abstraction Quality
- **m3 — The no-schema-churn proof should name dump and schema surfaces separately.** Dump exclusion
  is well chosen, but Pydantic schema visibility is a different property. — Data Structure Clarity
- **m4 — The dependency constraint is incomplete.** The pure validator must avoid importing the
  generation facade/public error types to keep the proposed edge acyclic. — Pattern Consistency

---

## Recommendations

1. Add `validate_constraint_graph_name_safety(graph)` at the start of `_generate_modules()` before
   any filesystem operation, while retaining the earlier `run_codegen()` preflight.
2. Specify the exception carrier and normalization table, including name-safety versus unrelated
   compiler failures at direct compiler, shared compile, renderer, module writer, and orchestration
   boundaries.
3. Replace the partial AST-binding description with a scope-aware symbol-table algorithm or an
   explicitly exhaustive binding collector and mutation matrix.
4. Add a four-route identity matrix for definition-bound, inline, legacy non-definition, and
   omitted-default inputs, naming predicate identity, wrapper identity, final names, and fallback.
5. Clarify record ownership and import direction, and preserve `[INFERRED]` provenance in the
   next-stage handoff.
6. Keep the full baseline/candidate byte comparison, plus targeted dump/contract assertions for the
   excluded carrier fields.

---

## Resolutions

No resolutions recorded. This autonomous stage produced the draft review for the design agent.

---

**Overall:** Revise
**Next Steps:** Return to `my-design` and point it at this review. Resolve M1-M4 before planning;
the reviewer does not edit the design.
