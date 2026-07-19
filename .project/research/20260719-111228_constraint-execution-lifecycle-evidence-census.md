---
date: 2026-07-19T11:12:28-07:00
researcher: Codex with three independent evidence agents
topic: "Constraint execution lifecycle: intent, implemented architecture, remediation history, and end-to-end proof gaps"
tags: [research, constraints, lifecycle, architecture, provenance, end-to-end]
status: complete
last_updated: 2026-07-19
---

# Research: Constraint Execution Lifecycle Evidence Census

## Research question

What architecture is actually intended for modeled constraint execution, what does the current
three-repository implementation prove, which earlier claims have been superseded, and what must be
demonstrated before the project can honestly claim end-to-end functional closure?

## Method

The main review read the two original concepts, the original deep research, the completed epic and
independent audit, the fact/IR/profile/lowering/generation/snapshot/contract artifacts, the current
remediation epic, the Gate B reports, current public docs and code, TEAx study/evaluator evidence,
and the IFE and stellarator consumer records.

Three independent agents then reviewed separate evidence sets:

1. intent and provenance across the original concepts and later corrections;
2. the current live and snapshot implementation, public docs, and tests;
3. remediation history and real consumer integration across sysml-codegen, agentic-mbse, TEAx,
   IFE, and the stellarator demo.

This is an evidence and conflict register. It does not promote an agent recommendation to an owner
requirement. The companion lifecycle spec carries requirement-grade provenance.

## Bottom line

The architecture is recoverable and coherent enough to state definitively. The implementation is
not yet proven end to end across the intended supported surface.

The strongest existing evidence proves several vertical slices and many local invariants. It does
not prove one supported public path from model authoring through sealed-package study execution for
the interaction shapes that have exposed the recent defects.

The most important corrections are:

- The executable profile has **two production consumers**. `agentic-mbse validate` uses it for
  independent authoring validation. sysml-codegen separately evaluates it during lowering and
  consumes its decisions. Authoring validation does not hand decisions to codegen.
- Gate A is a real, unowned contract violation. Literal-valued design attributes are valid
  constraint actuals under the lowering contract, but the stellarator route cannot resolve them
  without calculation passthroughs.
- Gate B is a real, registered contract violation. Constraint extension applies whole-graph V11
  coverage too early. The corrected invariant is differential at extension and whole-graph strict
  at final generation.
- F1 exceptional-arithmetic normalization is implemented in the current local TEAx tree at
  `d545701`. Its audit header incorrectly names `927a9e1`; sysml-codegen records that still call F1
  unimplemented are also stale. Release/remote state was not established here.
- The IFE acceptance is real but bounded. It required consumer adapters for the catalog and
  multi-entry study bridge and did not exercise the stellarator's Gate A/Gate B combination.
- The fusion late-fill bridge is private consumer code, is stale against the current generation
  plan, and is not evidence of a supported codegen API.

## Authority model

No existing document can be copied forward unchanged as the authority.

| Source class | Use in the lifecycle contract | Limitation |
|---|---|---|
| Owner-labeled original concepts | Governing intent and problem framing | Individual bullets are not owner-verbatim and later decisions supersede some details. |
| Owner statements captured in specs | `[NEED]` requirements | Quotes or path-cites must be preserved. |
| Agent recommendations ratified by owner | Adopted design direction, still agent-grade | Ratification does not make the wording owner-originated. |
| Completed specs/designs | Detailed contract and mechanism evidence | Some assertions were later falsified by cross-boundary tests. |
| Audits/tests | Evidence for the exact exercised surface | A certified item does not prove unexercised combinations. |
| Current code | Evidence of actual behavior | It may violate the intended contract. |
| Public docs and PR bodies | Evidence of what users are being told | Several are stale or contradictory. |
| Consumer bridges and probes | Integration evidence and defect discovery | Private helpers are not supported product seams. |

The only owner-verbatim text found in the R-1/R-2 decision chain is preserved in the v4 profile
spec: “ok got it. agreed with both decisions. please capture in the spec/plan and proceed with
orchestration”. It ratifies the agent recommendations; it does not change their provenance grade.

## Reconstructed lifecycle

| Stage | Owning repository | Input | Output / authority | Required terminal outcomes |
|---|---|---|---|---|
| Authoring and parse | agentic-mbse / SysIDE | SysML text | Parsed semantic model and diagnostics | Valid structure or named authoring failure. |
| Neutral extraction | agentic-mbse | Parsed model | `ConstraintFacts` + `ExpressionIR` | Every usage represented; no execution policy or graph role. |
| Profile classification | agentic-mbse | Neutral facts | `UsageDecision` per usage | `ADMIT`, `BLOCK`, `NON_NUMERICAL`, or `UNASSESSED`. |
| Authoring validation | agentic-mbse | Fresh profile result | L4 metrics and L6 diagnostics | Diagnostics only; no executable artifacts or state handoff. |
| Codegen preflight/lowering | sysml-codegen | Facts re-profiled by codegen | `ConcreteConstraint` records and exclusions | Execute, visible exclusion, or named halt. |
| Occurrence expansion | sysml-codegen | Owner kind + occurrence index | One concrete identity per finite occurrence | Non-finite or malformed ownership blocks loudly. |
| Actual resolution | sysml-codegen | Structural actual/default facts | Real channel, real design-attribute entry point, or modeled-default parameter | No text fallback or invented value. |
| Demand and base graph | sysml-codegen | Resolved module-output inputs + calculation targets | Pruned live graph or full replay graph with required producers | A resolved constraint channel without a producer halts. |
| Graph extension | sysml-codegen | Base graph + concrete constraints | Constraint nodes, entry points, report aggregator | No newly introduced V11 violation; all channel references valid. |
| Catalog assembly | sysml-codegen | Facts + concrete dispositions + extended graph | Embedded catalog | Every usage remains visible and every runtime entry has join identity. |
| Generation planning | sysml-codegen | Final graph/catalog | Precomputed `ConstraintGenerationPlan` | Semantic/name/IR/input checks before output mutation; writers preserve contents. |
| Final generation | sysml-codegen | Fully covered graph + plan | Runnable package | Zero whole-graph V11 violations, then deterministic render. |
| Contracts and sealing | sysml-codegen | Generated package | Model contract + package seal | Complete, deterministic artifact coverage. |
| Package load/evaluation | TEAx | Verified package + all typed entry channels | Mutation-protected authoritative `ModelEvidence` | Verdict evidence or normalized execution failure. |
| Study lifecycle | TEAx | Study definition + evaluator | Durable proposals/cases/evidence/query results | Crash-safe identity, resume, policy separate from model meaning. |

## Current profile contract

The current candidate is `executable-profile/v4` with four outcomes:

- `ADMIT`: numerical predicate is within the executable subset.
- `BLOCK`: a malformed, unresolved, or unsupported numerical claim; generation fails.
- `NON_NUMERICAL`: a valid statement outside this numerical executor; warning plus visible
  exclusion, generation continues.
- `UNASSESSED`: a valid form outside this executor's assessment scope; visible exclusion.

Current admitted behavior:

- Ordering: Integer/Real pairs and exact-unit compatible Quantity/Quantity pairs only.
- Arithmetic in operand position: the supported numerical operators under the existing unit rules.
- Boolean composition: `and`, `or`, `not` over admitted numerical predicates.
- Inline and definition-typed assertions.
- Positive and negated assertion polarity, with the positive predicate preserved unchanged and
  polarity carried separately.

Current excluded behavior:

- No equality executes. Boolean/string/enum equality is `NON_NUMERICAL`; numerical equality and
  `!=` are `BLOCK` because the float runtime lacks exact/tolerance semantics.
- Boolean/string/enum ordering blocks.
- Invocation, feature-chain execution, unsupported connectives, unresolved operands, unproven
  units, conversion-required quantities, and malformed facts block where they express a numerical
  claim.

This deliberately supersedes the original concept's broader typed-equality admission.

## Corrections and contradictions

### C-1: both profile consumers

Earlier conversation characterized extraction/profile as codegen-only. Current code proves both
uses. The same pure profile is invoked independently by L4/L6 validation and sysml-codegen
lowering. Facts are shared; decisions are recomputed.

Evidence:

- `../agentic-mbse/src/agentic_mbse/validation/level4_constraints.py`
- `../agentic-mbse/src/agentic_mbse/validation/level6_architecture.py`
- `../agentic-mbse/src/agentic_mbse/validation/runner.py`
- `src/sysml_codegen/analysis/constraint_lowering.py`

### C-2: old equality intent

The original concept admitted some typed equality. The owner later selected numerical validity on
the existing IEEE-double path. Profile v3 removed all equality from execution, and v4 retained
that rule. The new lifecycle must state the current rule, not merge the two matrices.

### C-3: Gate A actual resolution

The lowering spec accepts a real design attribute as a constraint actual. The real stellarator
model proves literal-valued design attributes do not reach the strict resolver/materializer. The
consumer's passthrough-calculation rewrite proves a workaround, not upstream conformance.

Gate A has no explicit row in the current remediation epic or backlog. Existing intent strongly
favors fixing direct design-attribute resolution rather than narrowing the model contract.

### C-4: extension-time versus final V11

Completed lowering INV-6 required the whole extended graph to be V11-clean. Gate B proves that
rule rejects unrelated pre-existing deferred inputs before a consumer can complete them. The owner
ratified the replacement direction on 2026-07-19:

> Constraint extension introduces no new V11 uncovered inputs. Final generation requires zero
> whole-graph V11 uncovered inputs.

Strict constraint-actual resolution and whole-graph channel-reference validation remain unchanged.

### C-5: catalog vocabulary

The concept uses “source record” for an applied usage. The landed class named
`ConstraintCatalogSourceRecord` is per definition. Per-usage identity is represented by eligible
concrete entries or excluded records. The lifecycle must describe semantics, not rely on the
misleading class name.

### C-6: snapshot semantics

Snapshot v3 stores neutral constraint facts and occurrence evidence. It does not store profile
decisions or a finished graph. Replay re-runs the installed profile, lowering, extension, catalog,
and generation. Public docs that still cite profile v3 / agentic-mbse 0.1.1 are stale relative to
the current v4 / 0.1.2 candidate.

### C-7: non-finite values versus arithmetic exceptions

An already-produced non-finite operand becomes Kleene unknown and can produce `indeterminate`.
Division by zero, negative power failure, exponent overflow, or other thrown predicate arithmetic
is execution failure. TEAx now normalizes that failure with the exact module key and preserves the
native exception as cause. These cases must never be collapsed.

### C-8: verification language

The supported TEAx `ProvisionalPackageLoader.load()` verifies the package seal before generated
model imports. Arbitrary direct Python imports do not. It first executes the package's own
unauthenticated `contracts/verify.py`, however, so no evidence proves a trusted verification
bootstrap. The authoritative contract requires a runtime-owned verifier or authentication of the
package-local verifier before execution.

### C-9: constraint diagnostics

`ConstraintFacts.diagnostics` is serialized, but current profile, validation, and lowering do not
consume it as a general diagnostic stream. A lifecycle rule is needed so extraction diagnostics
cannot be captured and then ignored.

## What is proven now

| Proof area | Evidence strength | Honest conclusion |
|---|---|---|
| Neutral fact recovery | Strong live fixture matrix and codec tests | Proven for the recorded source/type/unit shapes. |
| Expression IR | Strong structural, round-trip, and parity spikes | Proven for the admitted operator envelope and explicit unsupported nodes. |
| Profile v4 | Exhaustive category matrix, polarity routes, compatibility evidence | Predicate matrix complete for R-1/R-2; real fact-field consumer proof is open. |
| Lowering | Multiple fixtures and original S4 slice | Proven for selected resolver and occurrence shapes, not Gate A. |
| Generation/runtime | Unit, conformance, and real-simkit execution | Proven for selected truth, polarity, non-finite, default, and failure cases. |
| Snapshot | Multiple parity and portability suites | Proven for selected shapes; admitted locations can remain checkout-absolute and combined cases remain open. |
| Sealing | Package-contract and symlink matrices | Locally complete for current Item 6 policy. |
| TEAx F1 | Current code plus audit | Implemented at `d545701`; audit's `927a9e1` claim and release state need reconciliation. |
| Study lifecycle | Certified toy-package lifecycle and crash/resume | Architecture proven for one-entry fixture; real multi-entry support remains open. |
| IFE consumer | 2,301 real cases and unchanged numeric anchors | Strong bounded vertical slice with three adapters. |
| Stellarator consumer | Gate A facts captured after model workaround | No generated five-constraint package or end-to-end execution yet. |

## Open violations and unsupported seams

| ID | Gap | Current owner | Lifecycle consequence |
|---|---|---|---|
| R-4/R-5/R-7 | Occurrence and demand identity defects | Remediation Item 3 | Concrete expansion/demand integrity is not closed. |
| Gate A | Literal-valued design-attribute actuals fail strict resolution | Unowned | Written resolution contract is violated. |
| Gate B | Extension raises on unrelated pre-existing V11 offenders | Item 3B | Constraint construction and deferred-input graphs cannot compose. |
| R-8/R-9 | Warning render can mask halt; signed/unit defaults can disappear | Item 5 | Diagnostics/default meaning can be lost. |
| CE-F1 | TEAx expects a different standalone catalog schema | Open integration gap | Stock package-to-study catalog join is unsupported. |
| CE-F2 | Stock candidate bridge builds only one entry channel | Open integration gap | Real multi-entry packages need a consumer wrapper. |
| Late-fill | No public seam before final V11/plan/write/seal | Product/API decision | Fusion bridge is private, stale, and non-certifying. |
| Fact diagnostics | Serialized but no general production consumer | New owned item required | Trust-affecting extraction diagnostics can be ignored. |
| Evidence mutability | Generated report/evaluation and nested TEAx containers are mutable | New joint item | Policy can mutate authoritative evidence today. |
| Verifier bootstrap | Loader executes unauthenticated package-local verifier before checking the seal | New joint load item | Malicious verifier code can run before trust is established. |
| File-backed report success | Failure normalization exists; canonical report persistence/harvest is not proven | New TEAx integration item | Public no-adapter evidence path is open. |
| Snapshot locations | Admitted usage locations are not fully canonicalized | Remediation ownership required | Snapshot portability is not complete for all semantic facts. |
| Public docs | Profile/version/subtype/inequality statements are stale | Item 7/tail | Users are being told contradictory behavior. |
| Composed acceptance | No kept public-path generation→seal→verify→TEAx test | Item 8 / new proof gate | End-to-end claim is not established. |

## Required proof standard

“Beyond a reasonable doubt” must mean an executable proof obligation, not a larger collection of
component claims. The final gate needs:

1. one supported public path from live model to sealed/verified TEAx evidence;
2. the same path from snapshot replay with byte- and value-equivalent outputs;
3. exact candidate versions and fail-closed skew checks;
4. a composed fixture matrix spanning actual source, source form, occurrence, profile outcome,
   base-graph V11 state, route, entry-channel shape, and evaluator outcome;
5. negative mutations at every terminal boundary so a removed guard makes the proof fail;
6. a real single-constraint consumer acceptance (IFE) and a real multi-constraint/multi-entry
   stellarator acceptance: deferred inputs through a public finalization seam if late fill is
   supported, otherwise a fully representable graph with zero deferred inputs;
7. no private bridge or hand-authored catalog counted as proof of a supported upstream API.

## Primary source ledger

### Governing intent

- `.project/concepts/constraint-execution-and-design-space-studies.md`
- `.project/concepts/constraint-execution-and-design-space-studies-claude.md`
- `.project/research/20260710-095634_constraint-execution-and-design-space-exploration.md`
- `.project/completed/20260713_epic_constraint_execution.md`
- `.project/completed/20260713_epic_constraint_execution_audit_independent.md`

### Facts, IR, profile, lowering, generation

- `../agentic-mbse/.project/completed/20260713_constraint-facts/{spec,design,audit}.md`
- `../agentic-mbse/.project/completed/20260713_expression-ir/{spec,design,audit}.md`
- `../agentic-mbse/.project/completed/20260713_executable-profile/{spec,design,audit}.md`
- `.project/active/numerical-constraint-profile/{spec,design,audit}.md`
- `../agentic-mbse/.project/active/constraint-wave-profile-semantics/{spec,design,audit,evidence}.md`
- `.project/completed/20260713_constraint-lowering/{spec,design,audit}.md`
- `.project/completed/20260713_constraint-generation/{spec,design,audit}.md`
- `.project/completed/20260713_snapshot-v3/{spec,design,audit}.md`
- `.project/completed/20260713_package-contracts/{spec,design,audit}.md`

### Remediation and consumer evidence

- `.project/research/20260713-213722_constraint-exec-pr-code-quality.md`
- `.project/research/20260718-192048_constraint-exec-pr-wave-code-review.md`
- `.project/backlog/epic_constraint_pr_wave_remediation.md`
- `.project/research/20260719-065712_constraint-profile-semantics-and-license-reconciliation.md`
- `.project/research/20260719-103419_gate-b-independent-assessment.md`
- `../fusion-tea-stellarator-mbse-demo/.project/research/20260719-082509_gate-b-root-cause-constraint-lowering-vs-v11-bridge.md`
- `../fusion-tea-stellarator-mbse-demo/work/active/WI-027_demo-constraint-execution/{spec,design,plan}.md`
- `/home/reid/1cfe/fusion-tea/exploration/ife_e2e/study/findings.md`

### Runtime and study evidence

- `../teax/docs/evaluation-and-study.md`
- `../teax/.project/completed/20260713_constraint-study-integration-spike/findings.md`
- `../teax/.project/completed/20260713_model-evaluator/audit.md`
- `../teax/.project/completed/20260713_study-store-runner/audit.md`
- `../teax/.project/completed/20260713_study-policy-cli/audit.md`
- `../teax/.project/active/gap-close-f1-normalization/audit.md`

### Current public and code truth

- `../agentic-mbse/docs/constraint-facts-and-expression-ir.md`
- `../agentic-mbse/docs/patterns/constraints.md`
- `../agentic-mbse/src/agentic_mbse/sysml/executable_profile.py`
- `docs/architecture/reference/07-graph-assembly.md`
- `docs/architecture/reference/27-snapshot-generation.md`
- `docs/architecture/reference/28-constraint-lowering-and-catalog.md`
- `docs/architecture/reference/29-contracts-and-sealing.md`
- `src/sysml_codegen/analysis/constraint_lowering.py`
- `src/sysml_codegen/generation/constraint_plan.py`
- `src/sysml_codegen/cli/__init__.py`

## Conclusion

The recovered design is strong enough to serve as a normative lifecycle contract. The current
evidence is not strong enough to certify that contract. The next artifact must therefore define
the architecture and its proof obligations together, and must label current implementation gaps
without treating them as design ambiguity.
