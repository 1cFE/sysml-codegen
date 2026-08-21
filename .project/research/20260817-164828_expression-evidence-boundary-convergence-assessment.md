---
date: 2026-08-17T16:48:28-07:00
researcher: Codex
topic: "Whether stop-reinventing-the-parser is converging, and why semantic fallback findings keep recurring"
tags: [research, architecture, syside-authority, semantic-evidence, convergence]
status: complete
last_updated: 2026-08-17
agentic_baseline: 2171016d3e3e0805525aa4cf787c55c6293dd00c
codegen_baseline: 78a9beb956f9b5a517c08836b067f0cb0dc4ccc6
---

# Research: Expression-evidence boundary and convergence

**Date**: 2026-08-17T16:48:28-07:00
**Researcher**: Codex
**Research Type**: Codebase and architecture

## Research Question

**[OWNER-VERBATIM]** “I cannot tell if we are converging or playing whack a mole.”

The concrete question is whether the fresh indexed-reference, B3, B4, and B9 findings are unrelated
implementation misses, evidence of a failed occurrence architecture, or repeated symptoms of one
bounded design problem. The answer must explain what is happening, identify the exact live routes,
and give a stop condition that makes another remediation pass demonstrably finite.

The Agentic PDF suite is outside this research and outside parser-work validation by settled owner
direction. It was not run. The durable disposition is recorded in
`.project/completed/20260819_stop-reinventing-the-parser/plan.md:156-169` and
`.project/completed/20260819_stop-reinventing-the-parser/audit.md:38-49`.

For brevity below, `spec.md`, `design.md`, `design-review.md`, and `audit.md` refer to files in
`.project/completed/20260819_stop-reinventing-the-parser/`. `A_final:` and `C_prod:` refer to the immutable
baselines named in the frontmatter and expanded under Code References.

## Summary

- **[AGENT] The current patching method is not demonstrably converging.** The last remediation
  repaired named helpers and tests, while semantically equivalent public consumers remained legal.
  The latest audit therefore found the same failure class on different routes
  (`.project/completed/20260819_stop-reinventing-the-parser/audit.md:223-234`). Another site-by-site patch pass
  would be whack-a-mole.
- **[AGENT] The findings themselves are converging strongly.** The occurrence core is holding. The
  repeated defect is at the semantic-evidence edges that feed it: a typed owner exists, but another
  consumer can still read raw SysIDE fields, construct partial evidence, or accept a second
  caller-supplied account of an invariant (`audit.md:116-131,135-199`).
- **[AGENT] The indexed-reference result is serious but bounded.** Indexed element evaluation is not
  supported. The correct behavior is the existing named refusal. One computed-attribute route
  misses that refusal, drops the index marker, and resolves the remaining root/chain/leaf as an
  ordinary occurrence (`C_prod:src/sysml_codegen/elaboration/elaborate.py:329-350,2548-2600`). This
  does not show that exact occurrence identity generally selects random occurrences.
- **[AGENT] This is partly a design defect.** D5 and D7 defined one typed error contract and one
  public error-conversion boundary, but did not establish one exclusive evidence-acquisition path.
  D9 explicitly allowed registry generation to assume a caller had already preflighted the graph
  (`design.md:280-321,347-391,409-424`). The approved review treated those weaker properties as
  structural closure (`design-review.md:51-60,86-102`).
- **[AGENT] The repair is bounded.** Revise D5, D7, and D9. Preserve D1-D4 and the existing
  `ExpressionIR`. Add one total Agentic reference-inspection operation, valid-by-construction exact
  path values, graph-derived registry types, and a checked route manifest plus static ownership
  gate. Do that design work before another implementation pass.

## Detailed Findings

### 1. Two different convergence questions have different answers

The implementation has converged on its structural occurrence core:

- The earlier premise audit located the remaining authority breach at the semantic inputs to the
  graph, not in the typed graph, snapshot, or projection architecture
  (`.project/research/20260816-205035_premise-audit-fallback-census.md:42-49,225-243`).
- The fresh audit says the first audit's six occurrence and diagnostic findings remain fixed, and
  D1-D4's occurrence structures remain present (`audit.md:116-131,223-234`).
- The exact artifact topology, Fusion pins, both maintained model roots, and every-and-only mutation
  checks still reproduce (`audit.md:26-36,236-254`).

The remediation method has not converged. The repeated sequence is:

1. A requirement names a semantic authority or refusal.
2. Implementation adds a typed helper or makes an argument mandatory.
3. A test calls that helper or proves that exact argument shape.
4. Another live consumer still acquires weaker evidence or supplies a different account of the
   same invariant.
5. A later audit reaches that consumer and reproduces the same semantic failure class.

The second audit's B3/B4/B9 repairs illustrate the pattern. Typed Agentic operand and target
operations exist, and the registry list became mandatory. The fresh audit then found a raw unit
operand read, a separate optional binding-reference constructor, a partial deep-path constructor,
and an accepted empty registry list (`audit.md:148-199,223-234`).

**[AGENT] Verdict:** current local remediation is whack-a-mole; the diagnosis is converging on one
bounded ownership problem.

### 2. The public route set is finite

Live generation and snapshot capture enter raw SysIDE through two public arms:

```text
live model roots ──> elaborate_model_paths ───────┐
                                                  ├─> elaborate_loaded_extractor
admitted snapshot sources ─> elaborate_admitted_sources ─> _build_instance_graph

sealed --from-snapshot input ─> decoded InstanceGraph (no raw SysIDE traversal)
```

The two raw-source arms converge on one bridge
(`C_prod:src/sysml_codegen/orchestration/elaborated_pipeline.py:62-86,108-160`). Snapshot capture
uses the admitted-source arm (`C_prod:src/sysml_codegen/snapshot/capture.py:17-34`). Loading an
already sealed snapshot does not touch raw expression fields
(`C_prod:src/sysml_codegen/orchestration/exact_pipeline_context.py:283-298`).

The reachable consumers are enumerable:

| Consumer | Current semantic route | Status |
|---|---|---|
| Calculation definitions and constraint/math IR | Agentic reconstruction and `extract_expression_ir` | Typed operands and missing-target errors exist; several recursive operations have no shared depth budget (`A_final:src/agentic_mbse/sysml/expression.py:393-439,469-517`; `A_final:src/agentic_mbse/sysml/constraint_extraction.py:570-682`). |
| Indexed-source preflight | Scans input-directed top-level feature chains only | Incomplete category coverage; computed attributes, aliases, predicates, and nested index shapes can bypass it (`C_prod:src/sysml_codegen/elaboration/elaborate.py:301-350`). |
| Unit annotation | Reads raw `operands` before the typed walk | Failing getters can escape as raw exceptions (`C_prod:src/sysml_codegen/extraction/unit_annotation.py:45-58`; `C_prod:src/sysml_codegen/elaboration/elaborate.py:1025-1040`). |
| Alias/computed/predicate dependency walk | Uses typed facts, then recursively walks locally | Ignores `has_index_segment` and has no depth budget (`C_prod:src/sysml_codegen/elaboration/elaborate.py:2370-2404,2448-2600`). |
| Binding evidence | Chains use Agentic facts; bare references use a weaker optional route | A supported reference can carry no exact semantic path (`C_prod:src/sysml_codegen/extraction/binding_evidence.py:171-231`). |
| Deep literal overrides | Builds a path from `chaining_features` | Missing middle elements are filtered out instead of refused (`C_prod:src/sysml_codegen/elaboration/elaborate.py:1082-1149`). |
| Redefinition endpoints and multiplicity | Narrow Codegen-owned contextual operations | These routes are behaviorally fail-closed and have focused coverage (`C_prod:src/sysml_codegen/elaboration/occurrence.py:285-325,572-770`). |
| Enumeration discriminator | Narrow mapped-owner/stable-ID operation | Deliberate exception needed for the hard enumeration `::` behavior (`C_prod:src/sysml_codegen/elaboration/elaborate.py:1043-1058`). |

Three older extraction modules are explicitly off the public route in the active spec:
`usage_extractor.py`, `computed_attribute_extractor.py`, and `hierarchy_resolver.py`
(`.project/completed/20260819_stop-reinventing-the-parser/spec.md:118-119`). They must be deleted, de-exported,
or inventoried separately before anyone makes a repository-wide “no raw reads” claim. They do not
make the live route census unbounded.

### 3. What “indexed references can bind to the wrong occurrence” means

The alarming sentence describes one precise failure:

1. The item intentionally does not implement indexed element evaluation. `cells#(2).mass` must
   refuse with `SI_INDEXED_SOURCE_UNSUPPORTED` before graph construction
   (`design.md:263-278,393-407`).
2. The current preflight examines only `direction is In` features and selected top-level chain
   shapes (`C_prod:src/sysml_codegen/elaboration/elaborate.py:329-350`). The kept fixture is exactly
   that input-directed shape
   (`C_prod:tests/fixtures/indexed_expression_source/model.sysml:13-21`).
3. A computed attribute instead reaches `_expression_references`. Agentic returns a chain fact with
   `has_index_segment`, but this consumer does not branch on that field. It passes only the root,
   segments, and leaf into ordinary reference resolution
   (`C_prod:src/sysml_codegen/elaboration/elaborate.py:2142-2162,2548-2577`).
4. The licensed audit probe therefore observed `cells#(2).mass` resolve as `cells[0].mass` with no
   diagnostic (`.project/completed/20260819_stop-reinventing-the-parser/product-lens.md:643-653`).

This is silent wrong meaning, so it blocks certification. Its scope matters:

- It is not evidence that the occurrence graph confuses arbitrary identical names.
- It is not a request to implement indexed evaluation.
- It is an unsupported syntax form entering a resolver after its “unsupported” evidence was
  represented as an ignorable Boolean.

**[AGENT] The structural fix is to make an indexed use a distinct closed variant that an exact
resolver cannot accept.** `ExactReferenceUse | IndexedReferenceUse` is stronger than a resolvable
reference fact carrying `has_index_segment: bool`. The former makes accidental de-indexing a type
and construction error rather than a missed `if` statement.

### 4. The B3, B4, and B9 findings have the same shape

They look unrelated at the line level. They are the same authority defect at the architectural
level.

#### B3: typed operand ownership is optional

Agentic has `materialize_operands`, which converts getter or iteration failure into
`OPERAND_ITERATION_FAILED`, and `traverse_expression`, which has a depth limit
(`A_final:src/agentic_mbse/sysml/expression.py:42-54,57-118`). Codegen's unit helper still reads
`operands` directly before that owner. Its dependency walker recursively calls itself without the
same depth policy (`C_prod:src/sysml_codegen/extraction/unit_annotation.py:45-58`;
`C_prod:src/sysml_codegen/elaboration/elaborate.py:2548-2600`).

The public bridge converts the typed evidence family, not arbitrary `RuntimeError` or
`RecursionError` (`C_prod:src/sysml_codegen/orchestration/elaborated_pipeline.py:153-207`). One
conversion boundary therefore does not imply one evidence-acquisition path.

#### B4: incomplete references are representable

Agentic's total public reference operation refuses a missing resolved target
(`A_final:src/agentic_mbse/sysml/expression.py:645-665`). Bare binding extraction bypasses it. It
uses optional `resolved_target_fact` and constructs a supported reference form even when
`semantic_reference` is `None`
(`C_prod:src/sysml_codegen/extraction/binding_evidence.py:197-231`). The evidence model permits that
state (`C_prod:src/sysml_codegen/extraction/source_evidence.py:69-99`), and resolution later throws a
raw `RuntimeError` (`C_prod:src/sysml_codegen/elaboration/elaborate.py:2610-2620`).

Deep overrides have a parallel representational problem. `_reference_from_elements` discards
elements with missing facts and succeeds if any remain, so valid/missing/valid becomes a shorter
path (`C_prod:src/sysml_codegen/elaboration/elaborate.py:1136-1149`). A target path must be total or
absent; “partly resolved path” cannot be a productive value.

#### B9: a graph invariant has two authorities

The CLI derives and validates exit-point primitive types before output mutation
(`C_prod:src/sysml_codegen/cli/__init__.py:319-338`). The exported registry API separately accepts a
caller-provided list and trusts it (`C_prod:src/sysml_codegen/generation/registry.py:240-258,382-390`).
An empty list is syntactically present but semantically disagrees with the graph.

This was enabled by D9, which says registry generation may assume preflight passed
(`design.md:409-424`). The defect is therefore not just “the implementation forgot validation.” The
approved API assigns authority for graph-derived data to a caller that can disagree with the graph.

### 5. Design versus implementation accountability

| Finding | Implementation responsibility | Design/review responsibility |
|---|---|---|
| Computed indexed reference | Preflight omitted this consumer; dependency resolution ignored retained index evidence. | A5's intended refusal is correct, but D5/D7 did not make index classification and refusal common to every expression consumer. The proof matrix covered one consumer shape. |
| B3 unit and depth | Codegen retained a raw operand read and an unbounded recursive walker. | D5 required total operations but did not prohibit alternate raw reads or require one depth policy across production expression walks. |
| B4 binding | Binding extraction bypassed the total Agentic operation. | `SourceReferenceEvidence` permits “supported reference with no semantic reference,” so the invalid state is part of the data model. |
| Deep path | The constructor filters missing segments. | The constructor was absent from the design route inventory despite P-002 already warning that deep-override coverage was empirical (`.project/product/P-002-exact-owner-anchoring.md:31-48`). |
| B9 registry | The exported function trusts its list. | D9 explicitly authorizes the unsafe preflight assumption across that seam. |
| Final run record | An external staging script assembled the record instead of the committed runner. | The approved runner design is adequate; this is an execution/evidence-production deviation (`audit.md:201-221`). |

The design review's statement that F4 was resolved is too strong. It proved one public **error
conversion** function, then described that as one public **evidence** boundary
(`design-review.md:51-60`). Its duplication and route-safety passes also did not account for raw
operand reads, optional binding facts, partial deep paths, or the registry's second authority
(`design-review.md:86-102`).

**[AGENT] The requirements are not the problem.** A5, B3, B4, and B9 describe the correct product
behavior. D1-D4 also remain sound. The needed action is a bounded revision to the enforcement part
of D5, D7, and D9, followed by a fresh review of those revised claims.

### 6. Why the tests passed

The kept tests prove selected helpers and selected routes, not exclusive ownership:

- The indexed fixture covers only a top-level calculation input, which matches the current
  preflight filter (`C_prod:tests/fixtures/indexed_expression_source/model.sysml:13-21`).
- The forced B3 operand mock has no `operator = "["`, so the unit helper returns before its raw
  operand access is exercised
  (`C_prod:tests/conformance/test_expression_evidence_integrity.py:57-64,252-338`).
- The forced B3/B4 public test injects a direct call to `_expression_references`. It does not
  populate and resolve the actual binding, deep-override, or natural computed-attribute route
  (`C_prod:tests/conformance/test_expression_evidence_integrity.py:74-85,252-303`).
- The B9 test proves that omitting the list raises `TypeError`. It does not test empty, wrong, or
  duplicate values
  (`C_prod:tests/conformance/test_module_kind_faildloud.py:273-280`).
- Existing static guards ban named string and legacy selection mechanisms. They do not guard raw
  `.operands`, `.referent`, `.target_feature`, `.chaining_features`, or runtime class-name dispatch
  (`C_prod:tests/unit/test_elaboration_import_boundaries.py:12-64,82-173,196-297`).

The spec correctly says green maintained models cannot substitute for forced failure proof
(`spec.md:73-77`). The implementation tests did not yet apply that rule as a complete
consumer-by-failure route matrix.

### 7. Existing code already contains the right enforcement patterns

No new framework is needed:

- Agentic's `ExpressionIR` is a closed tagged union with fail-closed decoding
  (`A_final:src/agentic_mbse/sysml/expression_ir.py:50-133,145-180,226-283`). Reuse this pattern, not
  necessarily its mutability or this exact value. Its reference target is optional and its purpose is neutral
  math/predicate reconstruction, so it is not itself an exact occurrence-authority contract
  (`A_final:src/agentic_mbse/sysml/expression_facts.py:65-77`).
- `ExactPipelineContext` demonstrates builder-created immutable semantic state and receipt checking
  (`C_prod:src/sysml_codegen/orchestration/exact_pipeline_context.py:60-67,100-128,138-205`). A
  sealed context is more machinery than this repair needs; frozen variants plus private factories
  and an ownership guard are sufficient.
- `AutoImplContext` validates redundant derived fields at construction, while
  `ships_constraint_machinery` derives one graph predicate for every generation seam
  (`C_prod:src/sysml_codegen/core/models.py:140-177`;
  `C_prod:src/sysml_codegen/resolution/models.py:625-644`). B9 should use the cheaper second pattern:
  derive from the graph.
- The existing elaboration import-boundary scanner and Agentic adapter-only identity test show how
  to enforce a reviewed ownership manifest mechanically
  (`C_prod:tests/unit/test_elaboration_import_boundaries.py:82-173`;
  `A_final:tests/test_sysml/test_constraint_facts_banned_heuristics.py:46-58`).

## Code References

`A_final:` means Agentic commit `2171016d3e3e0805525aa4cf787c55c6293dd00c`.
`C_prod:` means codegen commit `78a9beb956f9b5a517c08836b067f0cb0dc4ccc6`.

- `A_final:src/agentic_mbse/sysml/expression.py:42-118,645-784` — typed operand, depth, and exact
  reference operations.
- `A_final:src/agentic_mbse/sysml/expression_ir.py:50-133,226-283` — existing closed-union pattern.
- `C_prod:src/sysml_codegen/orchestration/elaborated_pipeline.py:62-86,108-207` — shared public raw
  source bridge and its caught error families.
- `C_prod:src/sysml_codegen/elaboration/elaborate.py:301-350,1082-1149,2370-2600` — category-limited
  indexed preflight, partial deep path, and alternate expression walk.
- `C_prod:src/sysml_codegen/extraction/unit_annotation.py:45-58` — raw operand bypass.
- `C_prod:src/sysml_codegen/extraction/binding_evidence.py:171-231,255-270` — dual reference
  acquisition and runtime-name index classification.
- `C_prod:src/sysml_codegen/extraction/source_evidence.py:69-99` — representable invalid reference
  state.
- `C_prod:src/sysml_codegen/generation/registry.py:240-258,382-413` — caller-supplied graph invariant
  and exported aliases.
- `C_prod:tests/conformance/test_expression_evidence_integrity.py:57-85,252-379` — current forced
  helper coverage and indexed route coverage.
- `.project/completed/20260819_stop-reinventing-the-parser/audit.md:135-221` — reproduced CI-1 through CI-6.

## Architecture Insights

### The missing invariant is exclusivity

The approved design established named owners but did not establish that every public consumer must
use them. These are different claims:

```text
Current claim
    many evidence-acquisition paths
              ↓
    one public exception converter

Required claim
    one reviewed evidence-acquisition owner per semantic fact
              ↓
    closed, valid-by-construction evidence
              ↓
    one public exception converter
```

One catch point can standardize errors only after upstream code raises the owned error. It cannot
repair evidence that another consumer silently shortened or prevent raw exceptions from a direct
parser-property read.

### “Typed” is necessary but insufficient

A permissive typed record can encode the same ambiguity as an untyped structure. A resolvable
reference plus `has_index_segment: bool`, or a supported reference plus
`semantic_reference: None`, leaves the correctness obligation at every use site. Closed variants
move that obligation to one constructor.

### Not every raw read must move to Agentic

Enumeration discrimination, redefinition-slot construction, and multiplicity contextualization
have narrow Codegen responsibilities and already fail closed. The goal is not a cosmetic ban on all
SysIDE access. The goal is a reviewed ownership manifest: each reachable raw read belongs to one
named semantic operation, and every unowned read fails a static test.

## Feasibility Assessment

The repair is feasible without replacing the exact graph, snapshot model, TEAx projection, or
general `ExpressionIR`.

The shipped raw-source route set is finite. Existing code already supplies mapped metatype checks,
typed operand errors, exact target facts, a depth-bounded traversal, closed unions, graph-derived
invariant helpers, and static AST guards. The main work is to compose those patterns into exclusive
boundaries and migrate the enumerated consumers.

The principal risk is choosing a universal expression tree because it sounds clean. That would
duplicate or distort `ExpressionIR`, conflate math reconstruction with occurrence-reference
authority, and still leave deep relationship paths and registry invariants outside the tree. Three
small boundaries are both shorter and stronger.

No implementation should begin until the design identifies the full consumer manifest and the
proof matrix. Otherwise the next pass can again repair a helper without eliminating its alternate
route.

## Recommendations

### 1. Return to design now

**[AGENT] Revise D5, D7, D9, their test matrix, and the corresponding design-review claims before
another implementation pass.** Preserve the approved requirements and D1-D4. This is a bounded
design correction, not a restart of the feature.

### 2. Add one total Agentic reference-inspection operation

It should walk an expression once and return a materialized sequence of closed values such as:

```text
ReferenceUse = ExactReferenceUse | IndexedReferenceUse
```

It must own:

- mapped `IndexExpression` recognition through `SysideAdapter`, never runtime class-name text;
- typed operand materialization;
- one explicit depth budget shared by every recursive production consumer;
- structural unit handling;
- exact root, every segment, and leaf target construction;
- typed failure at the first missing target, operand failure, or depth exhaustion.

Use it for pre-graph scan, aliases, computed attributes, predicates, and calc/constraint bindings.
An exact resolver must accept only `ExactReferenceUse`; an `IndexedReferenceUse` must produce the
existing refusal before graph allocation. Keep a defensive refusal at consumption so an omitted
preflight category cannot silently resolve.

### 3. Make exact paths valid by construction

- Replace tag-plus-optional-field binding evidence with closed variants or private factories.
- Reference and chain forms require a complete exact path.
- Indexed forms cannot masquerade as resolvable references.
- Literal and general expression forms cannot carry a partial semantic reference.
- Give deep relationship paths a separate total `exact_path_from_elements` factory. It must map one
  fact for every supplied element or raise on the first missing segment.

Deep paths are not expression trees. Keeping this factory separate avoids forcing unlike evidence
through one abstraction.

### 4. Make the graph the sole B9 authority

Remove `exit_point_primitive_types` from `generate_registry`. Derive the sorted unique type set
inside the function from `graph.modules` using the existing collector. The CLI may call the same
validator before any write, but exported registry seams must not accept a second account of the
graph.

### 5. Replace spot checks with a closure proof

Create a checked route manifest with one row for every reachable raw selector. Each row names its
owner and a public failure test. Then enforce these mechanical conditions:

1. A static AST gate scans public-generation-reachable modules for raw `.operands`, `.referent`,
   `.target_feature`, `.chaining_features`, and runtime metatype-name dispatch.
2. The discovered inventory equals the reviewed manifest exactly. There are zero unowned reads.
3. Every expression-bearing consumer is covered across live and admitted/snapshot capture.
4. The matrix includes plain reference, chain, indexed chain, unit wrapper, depth exhaustion,
   missing referent/target/leaf/middle, plus strict and lenient modes where applicable.
5. Every failure proves the exact diagnostic, reference, root-relative location, cause chain, and
   no graph, snapshot, or output mutation.
6. Off-route exported modules are deleted/de-exported or separately inventoried and guarded.

The pass condition is:

> reachable raw-selector inventory equals the reviewed ownership manifest, with zero unowned
> reads, and every manifest row has a green public failure proof.

That is the point at which this work is demonstrably converged rather than merely green on the last
reported examples.

### 6. Repair final evidence through the existing runner

Rebuild the final execution record with the committed immutable runner. Do not invent a new
historical-measurement protocol during this semantic repair. The runner already executes commands,
retains output, hashes it, probes imports, and writes the evidence files
(`C_prod:verification/run_independent_green.py:270-355,383-450`).

## Open Questions

There is one implementation-shape choice for the revised design:

- add strict reference-use variants beside the general `ExpressionIR`; or
- add a strict evidence aggregate that contains the existing IR plus total exact reference uses.

**[AGENT] Recommendation:** use the first, smaller option unless the design can show that consumers
need the reconstructed math and exact reference uses atomically. Do not weaken or repurpose the
general IR's optional states merely to make it serve a second job.

No owner product decision is needed to choose the overall direction. The existing requirements
already settle unsupported-index refusal, exact evidence, and fail-before-write behavior. The next
stage is a focused technical-design revision and adversarial review, not further implementation.
