# Spec: Authoritative Constraint Execution Lifecycle Contract

**Durable requirements companion (copy-and-freeze, 2026-08-05).** Copied from
`.project/completed/20260720_constraint-execution-lifecycle-contract/spec.md` at its close state
(SHA-256 `3b7014bfc3973df0031c61a6f836e7a8c1f9b7da7ae5960ffcb37992e5afe56c`). The archived file
stays byte-for-byte intact as the close-state audit trail; forward requirement amendments happen
here only.

**Status:** Ratified target architecture — 2026-07-19. Lifecycle composed proof passed 41/41 and
the candidate merged 2026-07-20 (see Current proof verdict). Source-identity amendment authority
and certification state are inherited from the lifecycle contract's "Current conclusion".
**Owner:** Reid W
**Ratified:** 2026-07-19 — `[OWNER-VERBATIM]` “Ratified.”
**Created:** 2026-07-19
**Complexity:** HIGH
**Scope:** agentic-mbse + sysml-codegen + TEAx + supported consumer integration

## Problem

Constraint execution has accumulated correct pieces without one authoritative contract that says
how they compose. The original concepts describe the intended shape. Later specs, designs,
remediations, and consumer reports refine or correct it. Some public docs still describe superseded
behavior. Several certified components fail when combined in a real whole-plant route.

The result is an architecture that is hard to reason about and impossible to certify as a whole.
Recent defects repeatedly crossed seams that local tests treated independently: captured facts were
not consumed, literal design attributes were not visible to strict lowering, constraint extension
reapplied a final coverage rule too early, and stock study adapters did not accept a real
multi-entry package.

This item creates one lifecycle contract that is authoritative for behavior and proof. It does not
declare the implementation complete. It defines what completion means and records the current proof
status honestly.

The owner's bar for this artifact is preserved verbatim:

> “I need a DEFINITIVE set of requirements and invariants and architectural description that PROVES
> BEYOND A REASONABLE DOUBT that this works from an end-to-end functional perspective.”

## Normative status

The lifecycle contract is the single normative architecture description after owner ratification.
The original concepts, completed specs/designs, public docs, and PR bodies remain provenance and
history. Where they disagree, the lifecycle contract's explicit correction register governs.

This spec governs the lifecycle contract and its acceptance proof. The evidence census is
non-normative support. Neither document upgrades agent-authored decisions to owner-originated
requirements.

Every requirement below becomes normative if the owner ratifies the contract. Its label still
records origin: ratification does not turn an inherited or agent-derived rule into an owner-stated
need.

## Current proof verdict

**Established for the lifecycle scope — 2026-07-20.**
(Reconciled 2026-08-05, SOURCE-IDENTITY Item 3, checkpoint item 7.) The 2026-07-19
"not established" verdict is historical: the composed public proof passed 41/41 at the
commit-pinned candidate set and the wave merged on 2026-07-20 — agentic-mbse `f4ebdce`,
sysml-codegen `936315c`, TEAx `fa0e06a`
(`.project/completed/20260720_constraint-lifecycle-composed-proof/release-readiness.md`, which
alone still says merge pending; the merged state and post-merge smoke are in
`.project/completed/CHANGELOG.md:74-100`). Source-identity amendment authority and certification
state are not restated here; the lifecycle contract's "Current conclusion" is their sole home.

## Success criteria

- [x] The owner ratifies one lifecycle contract as the behavioral authority and resolves every
      item labeled “owner decision required.”
- [ ] Every stage names its owner, inputs, outputs, semantic authority, failure boundary, and
      downstream consumer.
- [ ] Every decision-carrying rule carries correct provenance. Agent recommendations remain
      agent-grade after ratification.
- [ ] The contract explicitly supersedes the old equality matrix, old whole-graph extension-time
      V11 invariant, stale profile-version claims, and “profile is codegen-only” description.
- [ ] Every modeled constraint usage receives one visible profile disposition. A `BLOCK` causes a
      named model-level halt. After generation, every non-blocking usage is represented by concrete
      executable modules or a visible exclusion; after evaluation, each module yields evidence or a
      named execution failure.
- [ ] Profile admission is total over its declared operand/operator/source-form matrix, and every
      fact field has a named consumer or tested decision-irrelevant rationale.
- [ ] `ADMIT` means the canonical predicate belongs to the executable semantic profile. No
      downstream layer invents a second semantic eligibility policy. Named occurrence, binding,
      graph, package, input, and runtime failures remain valid lifecycle outcomes.
- [ ] Direct literal-valued design-attribute actuals satisfy the written strict-resolution
      contract without a calculation passthrough. Calculation and constraint consumers share the
      same exact-QN positive-resolution machinery and differ only at terminal miss policy.
- [ ] Constraint extension never rejects unrelated pre-existing V11 offenders. A constructed Item
      3B case first proves whether extension can introduce an offender; only then is the correct
      behavior selected between differential checking and no extension-time coverage check. Final
      generation always rejects every whole-graph V11 violation.
- [ ] The owner-selected embedded constraint catalog passes from codegen's model contract to TEAx
      without a second schema, consumer materializer, identity substitute, or semantic reconstruction.
- [ ] The supported study bridge builds every required typed entry channel and applies candidate
      overrides to selected fields without consumer wrappers.
- [ ] Public late fill and post-build graph/default mutation are outside the supported lifecycle.
      Every model-derived downstream value has a modeled/codegen producer when the graph is built;
      ordinary declared design inputs enter only through generated typed input schemas.
- [ ] Producer completeness is proven independently from V11: no defaulted fallback, ambiguous
      first-pick, or leaf-name guess can satisfy a model-derived dependency.
- [ ] A package is seal-verified before supported TEAx import or evaluation.
- [ ] The final proof suite runs one public path from model/snapshot to mutation-protected
      authoritative TEAx evidence, with negative mutations proving every load-bearing guard.
- [ ] IFE acceptance remains green and the stellarator five-constraint route completes with no
      hand-coded viability rule, unchanged ordinary numerics, and no private bridge counted as
      upstream product proof.
- [ ] Exact candidate revisions, versions, hashes, route outputs, and remaining external release
      state are recorded. No component audit is substituted for a missing composed proof.

## Requirements

### A. Responsibility and authority

- **LC-A01 [INHERITED]** Calculations compute values. Modeled constraints judge those values and return
  evidence. Study policy decides what to do with the evidence. Study code must not reinterpret the
  modeled predicate. Source: original concept, Design Principles 1 and 4.
- **LC-A02 [INHERITED]** A false supported predicate is successful `violated` evidence, not an
  execution failure. Ordinary outputs remain available. Source: original concept, Design Principle
  4.
- **LC-A03 [INHERITED]** Every modeled constraint usage receives one profile disposition. Any
  `BLOCK` causes a named model-level halt. After generation, every other usage has executable
  concrete representation or remains visibly excluded/unassessed. After evaluation, every module
  yields evidence or a named execution failure. Source: Claude concept variant, Design Principle 5,
  and original concept's settled visibility rule; corrected for fail-fast lowering behavior.
- **LC-A04 [INFERRED]** The authoritative semantic chain is neutral fact → profile decision →
  verified concrete lowering → generated evidence. Source facts carry provenance; the verified
  `UsageDecision` is codegen's eligibility/polarity authority.
- **LC-A05 [INHERITED]** A downstream representation may add execution identity, graph wiring, or
  evidence metadata. It may not rewrite the selected positive predicate or silently change its
  polarity, bindings, or source identity.
- **LC-A06 [INFERRED]** Public documentation, PR prose, and consumer adapters are subordinate to
  the lifecycle contract when they disagree. Contradictions must be corrected, not averaged.

### B. Neutral extraction and expression representation

- **LC-B01 [INHERITED]** agentic-mbse is the only layer that interprets SysIDE constraint syntax.
  `ConstraintFacts` and `ExpressionIR` are library-neutral, serializable semantic facts.
- **LC-B02 [INHERITED]** Facts contain source identity/location, source form, owner/scope, membership,
  polarity, structural actuals/formal targets, omitted defaults, inheritance/retyping, type/unit
  evidence, and predicate structure. They contain no graph roles, Python names, study policy, or
  historical profile decisions.
- **LC-B03 [INHERITED]** The base `ConstraintUsage` subtype sweep is total for the supported
  constraint-fact/catalog boundary. `AssertConstraintUsage`-only enumeration is insufficient
  because it misses satisfy semantics. The retired drop manifest is not an authority.
- **LC-B04 [INHERITED]** Every reference preserves source name, qualified target, and ordered feature
  chain segments. Runtime channel/parameter resolution remains codegen's job.
- **LC-B05 [INHERITED]** One structural `ExpressionIR` serves constraint predicates and calculation
  expressions. Display reconstruction and source-text evaluation are not semantic interfaces.
- **LC-B06 [INHERITED]** Every unrecognized expression node becomes an explicit `UnsupportedNode`.
  Extraction never coerces it into a known kind or drops it.
- **LC-B07 [INHERITED]** Fact and IR codecs are versioned and canonical. Serialize→parse→serialize is
  byte-identical at one pinned schema pair.
- **LC-B08 [INFERRED]** Extraction diagnostics are load-bearing. Each diagnostic has a stable code
  and severity. A trust-affecting diagnostic blocks before lowering; an advisory diagnostic remains
  visible in authoring and codegen output. An unclassified diagnostic fails closed. The current fact
  has no severity field, so closure requires a fact-schema/version bump, companion floor/guard
  update, and two-direction skew tests; a sink alone is insufficient.

### C. Executable profile and validation

- **LC-C01 [NEED]** This executor serves numerical validity evaluation. Valid non-numerical
  statements may remain in the model without stopping code generation. Source: owner statement
  recorded in the numerical-profile spec, 2026-07-18.
- **LC-C02 [NEED]** A numerical claim whose meaning cannot be proven safe under the retained
  runtime is malformed and stops generation rather than degrading to a warning. Source: owner
  statement recorded in the numerical-profile spec review, 2026-07-18.
- **LC-C03 [INFERRED]** The profile returns exactly one of `ADMIT`, `BLOCK`, `NON_NUMERICAL`, or
  `UNASSESSED` for every usage. It is a pure, deterministic facts-to-decision function.
- **LC-C04 [INHERITED]** The profile has two independent production consumers:
  `agentic-mbse validate` for L4/L6 authoring diagnostics and sysml-codegen for load-bearing
  lowering/preflight. Codegen re-evaluates facts; authoring decisions are not passed as mutable
  state.
- **LC-C05 [INFERRED]** The profile-v4 ratification target admits `<`, `<=`, `>`, and `>=` over Integer/Real pairs and
  exact-unit compatible Quantity/Quantity pairs; supported arithmetic and `and`/`or`/`not` may
  compose those predicates. Agent recommendation ratified by owner on 2026-07-18/19.
- **LC-C06 [INFERRED]** No equality or `!=` currently executes. Boolean/string/enum equality is
  `NON_NUMERICAL`; integer/real/quantity equality is `BLOCK`. Agent recommendation ratified by
  owner on 2026-07-18.
- **LC-C07 [INFERRED]** In the profile-v4 ratification target, every non-whitelisted ordering category pair, including Boolean, String,
  enumeration, unknown, unresolved, and mixed numeric/non-numeric pairs, blocks. Agent
  recommendation ratified by owner on 2026-07-19.
- **LC-C08 [INFERRED]** The profile-v4 ratification target supports inline and definition-typed positive and negated assertions.
  The positive predicate bytes remain unchanged; decision-carried `is_negated` and
  `expected_value == not is_negated` carry polarity. Agent recommendation ratified by owner on
  2026-07-19.
- **LC-C09 [INHERITED]** Polarity is applied exactly once, when each concrete assertion derives status
  and simple margin. Raw `actual_value` remains the positive predicate result.
- **LC-C10 [INHERITED]** Every `ConstraintUsageFact` field has a real, code-grounded
  profile/downstream consumer or a tested decision-irrelevant rationale. A static map entry alone
  is not proof. Adding/removing a field without updating the consumer evidence fails a test.
- **LC-C11 [INHERITED]** A profile semantic change bumps `PROFILE_SEMANTIC_VERSION`; companion package
  metadata, codegen dependency floor, runtime guard, and both skew directions fail closed.
- **LC-C12 [INFERRED]** Profile behavior is not called current or certified until exact committed
  agentic-mbse/sysml-codegen hashes and locks form a mutually installable pair. Working-tree tests
  are candidate evidence only.

### D. Concrete lowering and actual resolution

- **LC-D01 [INHERITED]** Owner kind controls expansion cardinality. Source form controls predicate
  selection. These axes are orthogonal and may not be inferred from one another.
- **LC-D02 [INHERITED]** Every finite concrete occurrence receives its own `constraint_id`, catalog
  entry, module instance, and evaluation channel. Structurally identical occurrences may not
  collapse.
- **LC-D03 [INFERRED]** Multiple occurrences may bind the same de-indexed producer when the base
  graph truly has one producer. The shared binding is recorded per entry; execution identities and
  result channels remain distinct.
- **LC-D04 [INHERITED]** Non-finite, recursive, malformed, or unsupported occurrence expansion blocks
  loudly with owner/path context. It never truncates to a partial occurrence set.
- **LC-D05 [INHERITED]** A definition-typed usage resolves formal bindings by formal target identity,
  not by the local spelling of an actual.
- **LC-D06 [INHERITED]** Calculation inputs and constraint actuals share one ordered positive-
  resolution procedure. It checks an existing producer channel first, then a real design attribute
  under its exact qualified identity. An omitted constraint formal may become a modeled-default
  parameter only when the model explicitly supplies that default. Source: completed lowering spec
  lines 145–175. Current code has three drifted ladders (calculation, constraint, aggregation) and
  shares only terminal disposition; resolver unification is an explicit implementation gap.
  Amended 2026-08-05 (SOURCE-IDENTITY Item 3): aggregation terms join the shared procedure and
  resolution keys by semantic source identity — contract invariant 19 (amended) and invariants
  54–56; see LC-SI-09/LC-SI-10.
- **LC-D07 [INHERITED]** Strictness changes only the terminal miss policy. Constraint resolution
  never parses display text, invents an actual, or uses the calculation resolver's synthesized
  fallback. Genuinely unresolved means a generation error naming the usage, formal, actual, and
  attempted resolution classes. Positive resolution may not fork into consumer-specific ladders.
  Amended 2026-08-05 (SOURCE-IDENTITY Item 3): the genuine-terminal-miss policy applies to every
  consumer type, with no same-named candidate and no consumer-local mint for a bound reference —
  contract invariant 20 (amended); see LC-SI-12.
- **LC-D08 [NEED]** Direct literal-valued design attributes are valid constraint actuals and must be
  materialized under their real qualified names, reusing the same typed entry point as calculation
  consumers. The stellarator passthrough-calculation pattern is a workaround, not the required
  representation. Source: owner, 2026-07-19: “100% Option A. I am BLOW AWAY this wasn't already a
  requirement and this is a design gap. That is the whole fucking ethos of the graph-building.”
  This later decision supersedes the same-day owner-ratified WI-027 D7 passthrough design. WI-027
  must point to this supersession and remove those passthroughs before acceptance.
- **LC-D09 [INHERITED]** Modeled defaults remain overridable typed contract parameters. They are not
  baked into predicate code and never become automatic study variables. Amended 2026-08-05
  (SOURCE-IDENTITY Item 3): authored-literal independence and the per-usage `LIBRARY_DEFAULT`
  ruling are contract invariant 22 (amended); see LC-SI-11/LC-SI-11A.
- **LC-D10 [INHERITED]** Constraint input channels join dependency roots before pruning so a producer
  used only by a constraint remains live.
- **LC-D11 [INHERITED]** An eligible executable identity uses `(source-local identity, concrete owner
  occurrence, membership kind, polarity)`. An excluded record instead uses stable source/context
  identity because occurrence or polarity may not exist. The executable fingerprint scopes and
  interprets IDs but is not an ID input; doing so would be circular. Collisions fail before graph/
  output mutation. Resolved (Item 12): `tracking_key` was removed (dead field — no writer, no
  catalog entry, never serialized), so no cross-version correlation mechanism is claimed.

### E. Graph extension, catalog, and generation

- **LC-E01 [INHERITED]** Constraint extension does not mutate its input graph. It returns a new graph
  whose permitted changes are added constraint modules, their required entry points, and the report
  aggregator; unchanged values may be safely shared. Catalog assembly is the following, separate
  stage and embeds one catalog on the returned graph.
- **LC-E02 [INFERRED]** Pre-existing uncovered inputs do not make an unrelated safe constraint fail.
  Constraint extension performs no V11 coverage check; final generation owns coverage. Supersedes
  old lowering INV-6. Settled by constructed proof (Item 3, 2026-07-19): extension is vacuous with
  respect to V11 — it cannot introduce an offender, so a differential would be dead code. Decision
  and enumeration: `.project/active/constraint-lifecycle-gate-b/decision.md`. **Re-open trigger:**
  the result holds only while fallback membership stays restricted to consumer-minted
  `{consumer_eqn}__{key}` strings. Any change letting a design-attribute QN enter
  `fallback_entry_points` makes extension-time V11 non-vacuous again and must re-open this row.
- **LC-E03 [INHERITED]** Whole-graph channel-reference validation still runs on the extended graph.
  Strict actual resolution remains unchanged.
- **LC-E04 [INHERITED]** Final generation requires zero whole-graph V11 uncovered inputs.
- **LC-E04A [NEED]** Codegen exposes no public late-fill or post-build graph/default mutation seam.
  Every model-derived value consumed downstream has a modeled/codegen producer when the graph is
  built. Legitimate external design inputs remain ordinary generated typed entry channels. Source:
  owner, 2026-07-19: “I really don't want to add support for ‘public late-fill’ -- that sounds like
  a great way to allow bugs and enable injecting even more.”
- **LC-E04B [INFERRED]** Producer completeness is checked independently from V11. Every
  model-derived consumed value resolves under exact identity to one intended producer; a defaulted
  fallback, ambiguous first-match, or leaf-name guess is not conformance even when V11 is clean.
  Amended 2026-08-05 (SOURCE-IDENTITY Item 3): "exact identity" means semantic source identity
  (declaration plus concrete occurrence), and owner/name reconstruction is not conformance —
  contract invariant 26 (amended) and invariant 55; see LC-SI-08.
- **LC-E05 [INFERRED]** The canonical catalog must expose definition/source inventory, one visible
  disposition per usage, and one concrete execution entry per admitted occurrence. A visible
  disposition is one of three kinds — eligible, excluded-with-reason, or non-reaching-with-reason —
  and the dispositions cover the complete authored-usage domain. It carries
  source form, usage short name/QN, owner QN, definition QN, and an explicit definition-to-usage join,
  each on the per-eligible concrete entry. `owner_qn` is a real qualified name distinct from
  `owner_instance_path`, and the definition-to-usage join is entry-level. Current code lacks the
  admitted per-usage record and these five TEAx-consumed fields; closing the coverage model is
  additive schema work. Each result joins one concrete entry by `constraint_id`.
  Amended 2026-08-12 (CONSTRAINT-SEMANTICS Item 1), `[AGENT] (ratified by owner, 2026-08-12)`:
  added the three-kinds and complete-authored-domain clauses above; "reaches no instance" is a
  disposition, not an absence. Superseded: the requirement named no
  disposition kinds and left non-reaching usages uncovered. See contract invariant 28 (amended).
  *(This item rewrites requirement text in place under the header's forward-amendment rule; the
  superseded text is quoted in each amendment note.)*
- **LC-E06 [INHERITED]** Excluded, unassessed, and non-reaching usages remain inspectable with
  identity, reason, and portable location. They never masquerade as executed constraints or vanish
  from coverage. Amended 2026-08-12 (CONSTRAINT-SEMANTICS Item 1),
  `[AGENT] (ratified by owner, 2026-08-12)`: the same guarantee now covers non-reaching usages.
  Superseded: "Excluded/unassessed usages remain inspectable…". See contract invariant 28 (amended).
- **LC-E07 [INHERITED]** One reusable polarity-neutral predicate body is compiled per true predicate
  source. One wrapper/module exists per concrete assertion. All same-source entries must agree on
  canonical IR bytes while preserving independent source polarity; mixed polarity may not inherit
  the first entry's value.
- **LC-E08 [INHERITED]** Generated namespaces are collision-checked against model names, generated
  function names, wrapper parameters, locals, module paths, schemas, and output paths before
  mutation. Collision resolution is deterministic reject or a separately specified injective map.
- **LC-E09 [INHERITED]** A precomputed generation plan performs source/catalog/polarity/IR/input/
  name/compile/render consistency checks before clearing or creating the output directory. Writers
  consume it without changing its semantic contents.
- **LC-E10 [INHERITED]** Constraint evidence schemas are exact and registered. The aggregator requires
  one field per eligible concrete assertion with extras forbidden. Missing evidence is failure. The
  aggregator remains an exit ancestor whenever a constraint report is required. A model with
  constraint usages but no applicable asserted gate still requires the zero-input aggregator and a
  report carrying the not-assessed state; a model with no constraint usages remains inert and has no
  aggregator. Amended 2026-08-12 (CONSTRAINT-SEMANTICS Item 1),
  `[AGENT] (ratified by owner, 2026-08-12)`: the trigger is the absence of an applicable asserted
  gate, not the absence of eligible concrete assertions — an applicable gate that produced zero
  eligible entries reads partial coverage. Superseded: "A model with constraint usages but zero
  eligible concrete assertions still requires the zero-input aggregator and a `not_assessed`
  report". See contract invariant 32 (amended).
- **LC-E11 [INHERITED]** Report headline precedence is: violation, then indeterminate, then full
  satisfaction, then partial coverage, then not assessed. Full satisfaction requires every
  applicable asserted gate to have been assessed and passed; an assessed result alone does not earn
  it. Source: original concept and generation spec — which is the source of the requirement's
  subject, not of the precedence below. Amended 2026-08-12 (CONSTRAINT-SEMANTICS Item 1),
  `[AGENT] (ratified by owner, 2026-08-12)`, sourced to
  `.project/active/constraint-semantics-contract/spec.md` and ADR-009: the coverage-truthful
  five-state precedence above **replaces** the inherited rule in full. Superseded: "Report headline
  precedence is: any violation → `violation`; else any indeterminate → `indeterminate`; else any
  assessed result → `all_satisfied`; else `not_assessed`." See contract invariant 33 (amended).
- **LC-E12 [INHERITED]** Constraint-free models remain byte-stable. No constraint usage means no
  constraint catalog or modules. An asserted usage with zero eligible entries still produces visible
  exclusions and puts the report at the partial-coverage state; a constraint-bearing model whose
  usages are all non-asserted reads not assessed. Amended 2026-08-12 (CONSTRAINT-SEMANTICS Item 1),
  `[AGENT] (ratified by owner, 2026-08-12)`, sourced to ADR-009: zero eligible entries under an
  asserted usage is partial coverage, not the not-assessed surface. Superseded: "Constraint usages
  with zero eligible entries still produce visible exclusions and the `not_assessed` report surface."
  See contract invariants 32 and 33 (both amended).
- **LC-E13 [AGENT] (ratified by owner, 2026-08-12)** An asserted usage whose owner has zero
  occurrences — a vacuous gate — is visible at warning grade: the catalog carries a
  non-reaching-with-reason disposition and authoring validation emits an advisory naming the usage
  and its detached owner. It counts as missing assessment for feasibility coverage until it carries
  an explicit inapplicability disposition, at which point it leaves the denominator. It is neither a
  generation halt nor a silent pass. Added 2026-08-12 (CONSTRAINT-SEMANTICS Item 1), mirroring
  contract invariant 61 (minted by the same item); acceptance in contract Appendix C, "Asserted
  vacuous gate".

### F. Snapshot, contracts, and package integrity

- **LC-F01 [INHERITED]** Snapshot is an extraction boundary, not a serialized executable graph. It
  stores neutral facts and the load-bearing occurrence transcript. A supported replay re-runs the
  same semantic profile/lowering/extension/catalog functions through its route-specific
  `include_all` graph rebuild. Grandfathered skip-lowering fails closed on the normal product path;
  any explicit legacy-inspection mode is opt-in, visibly non-executable, and cannot certify/seal.
- **LC-F02 [INHERITED]** Live and supported snapshot routes produce equivalent decisions,
  diagnostics, graph/catalog values, fingerprints, and generated bytes for the same semantic input.
  Because replay uses `include_all=True`, certification explicitly compares the retained producer
  set rather than merely defining it as equivalent.
- **LC-F03 [INHERITED]** Snapshot schema/version/shape errors fail before reconstruction with section and
  field context and recapture guidance. Raw container exceptions do not escape.
- **LC-F04 [INHERITED]** Semantic artifacts contain portable source referents, never checkout-absolute
  paths in IDs, loader-reconstructed fields, generated code/docstrings, catalog/contracts, reports,
  or the full generated tree. Relocation does not change semantic or executable bytes.
- **LC-F05 [INHERITED]** The model contract is a pure projection of final graph/catalog/parameters/
  outputs and records the semantic fingerprint. The sealed package contract records the executable
  fingerprint. Neither identity is substituted for the other.
- **LC-F06 [INHERITED]** Sealing and verification use one path/symlink policy. Anything that seals must
  verify unchanged; every forbidden link fails at the earliest boundary. A generation manifest
  identifies codegen-produced, preserved-handwritten, and runtime artifact classes so re-sealing
  cannot launder arbitrary foreign files into generated provenance.
- **LC-F07 [INHERITED]** The supported TEAx package loader verifies the package contract and seal
  before importing generated model modules or evaluating a case. Direct unverified imports are
  outside the supported lifecycle.
- **LC-F08 [INHERITED]** Every downstream constraint-generation operation consumes the
  `ComputationGraph`, including its embedded catalog, as its constraint authority. It never
  re-profiles or re-lowers stale facts from `PipelineContext`; unrelated calculation generators may
  still consume their own context fields.
- **LC-F09 [INFERRED]** No untrusted package code executes before package verification. The verifier
  is runtime-owned, or a package-carried verifier is authenticated against a runtime-owned digest
  before execution. The current loader's unauthenticated package-local `contracts/verify.py`
  bootstrap does not satisfy this rule. Verifier and runtime-contract versions are single-sourced
  or checked through an explicit compatibility table; skew fails closed before package code runs.

### G. Runtime evidence and study execution

- **LC-G01 [INFERRED]** A completed constraint module emits one authoritative
  `ConstraintEvaluation` with identity, raw three-valued predicate result, status, optional signed
  margin, and bounded observed values. Downstream code cannot change the authoritative value;
  enforce this with deep freezing or defensive isolation of the envelope, generated report, nested
  results, observations, status, and margin. A simple margin respects polarity and is zero at the
  modeled boundary; compound predicates do not invent an aggregate margin.
- **LC-G02 [INHERITED]** An already-produced non-finite operand becomes Kleene unknown. Boolean
  composition follows Kleene truth tables. Overall unknown produces `indeterminate` evidence.
- **LC-G03 [INHERITED]** An adverse verdict never raises. A violated case completes with ordinary
  outputs and report evidence. Source: original concept; later TEAx F1 work preserves the rule.
- **LC-G04 [INHERITED]** Thrown arithmetic, missing inputs, schema failure, or missing aggregate
  evidence is execution failure, never `violated` or `indeterminate`. Source: TEAx F1 design/audit;
  it refines the owner-originated violation-versus-failure distinction.
- **LC-G05 [INHERITED]** Prepared and file-backed evaluators normalize module failure identically with
  phase, exact module key, non-retryable status, no partial artifacts, and the original exception as
  direct cause. Equivalent completed executions also produce equal full report content.
- **LC-G06 [INHERITED]** Candidate validation rejects malformed/missing/wrong-typed inputs. It does not
  reject an otherwise typed non-finite value merely because the model may return `indeterminate`.
- **LC-G07 [NEED]** Codegen's catalog embedded in the model contract is the sole catalog schema
  authority and TEAx consumes source form, usage identity, owner QN, definition QN, explicit join,
  and occurrence data directly. TEAx binds compatibility to the real semantic/catalog identity,
  not a standalone-byte stand-in. Source: owner, 2026-07-19: “100% Option A. We need to purge this
  mess.”
  Amended 2026-08-12 (CONSTRAINT-SEMANTICS Item 1), `[AGENT] (ratified by owner, 2026-08-12)`: the
  embedded catalog is also the sole authority for coverage truth — the report's coverage accounting
  derives from it in one direction and is never an independently maintained second inventory. See
  contract invariant 48 (amended). The owner-sourced requirement above is unchanged.
- **LC-G07A [INFERRED]** The catalog-identity transition either proves an old store artifact-
  equivalent and migrates it, or preserves it as an archived lineage and starts a new store;
  identity is never silently reassigned.
- **LC-G08 [INFERRED]** A study definition supplies baseline typed models for every required entry
  channel and candidate overrides for selected channel fields. The supported bridge validates and
  returns the complete channel mapping.
- **LC-G09 [INHERITED]** Study policy may classify, reject, or penalize read-only evidence but may not
  rewrite modeled status, margin, observed values, or catalog identity. Source: original concept,
  Study Layer.
- **LC-G10 [INHERITED]** Study identity distinguishes proposal, candidate, case, attempt, and artifact.
  Commit is crash-safe, append-only where required, idempotent on resume, and compatibility-bound
  to the exact package and real semantic/catalog/executable fingerprints. Resume/query across a
  mismatch fails or starts an explicit new lineage.
- **LC-G11 [INFERRED]** The public file-backed evaluator registers and routes the constraint report,
  persists its exact JSON form with package identity, and harvests it into study evidence without a
  consumer-specific schema adapter. This machinery does not exist today and is implementation work,
  not merely missing audit evidence.
- **LC-G12 [INFERRED]** A constraint-free generated package loads and evaluates successfully in TEAx.
  An absent constraint report yields empty constraint evidence, not a `KeyError`.
- **LC-G13 [INHERITED]** `assessment_failed` is a distinct evidence-preserving case state. Policy
  failure does not erase completed model evidence or masquerade as execution failure.

### H. Supported integration seams

- **LC-H01 [INFERRED]** Normal public codegen/CLI generation, final V11, precomputed planning,
  rendering, contracts, sealing, TEAx prepared/file-backed evaluation, and study runner/store/query
  APIs are supported lifecycle surfaces.
- **LC-H02 [INFERRED]** Private `_generate_*` imports, direct graph/default mutation, consumer
  catalog materializers, and consumer evaluator wrappers are integration probes, not supported
  product seams.
- **LC-H02A [NEED]** CE-F1 closure deletes the fusion catalog materializer and TEAx's independently
  shaped catalog contract, hand-authored schema fixture, and stand-in fingerprint. TEAx config,
  query, CLI, and fixtures consume real codegen model-contract artifacts. No supported code splits
  qualified-name strings, searches serialized predicate text, hardcodes source form, or invents
  missing fields. Source: Owner Decision 3, 2026-07-19.
- **LC-H03 [NEED]** The supported lifecycle does not expose a hook that supplies missing model
  computations after graph construction. Direct graph/default mutation and the current fusion
  bridge cannot certify upstream behavior. Source: Owner Decision 1, 2026-07-19.
- **LC-H04 [INFERRED]** Graph completeness does not eliminate declared external design inputs. It
  requires every modeled/computed dependency to have a producer; consumers supply only the ordinary
  typed entry channels declared by the generated package.
- **LC-H05 [NEED]** The remediation simplifies the architecture by consolidating shared machinery
  and deleting superseded hacks, bridges, adapters, and duplicated validation/resolution paths.
  For Items 2–13, line counts are not requirements or gates; necessary code growth does not require
  a deviation when the result is structurally simpler and satisfies the lifecycle invariants.
  Item 1's in-flight artifacts are unchanged. Source: owner correction, 2026-07-19.

### I. Proof obligations

- **LC-I01 [NEED]** The proof target is one composed public path, not the sum of component audits.
  Source: owner's “beyond a reasonable doubt” end-to-end proof requirement above.
- **LC-I02 [INFERRED]** Every load-bearing invariant has a positive case and a mutation/negative case
  that fails for the intended reason before later boundaries.
- **LC-I03 [INFERRED]** The matrix covers, at minimum: inline/definition-typed; positive/negated;
  admitted/non-numerical/unassessed/blocked; producer/design-attribute/modeled-default actuals;
  single/multiple/non-finite occurrence; clean/pre-existing/new V11 states; live/snapshot;
  zero/one/multiple entry channels; satisfied/violated/indeterminate/execution-failed.
- **LC-I04 [INFERRED]** Combined cases exercise interactions, not only one axis at a time. The
  mandatory interaction case is the real multi-constraint, multi-entry stellarator route on a fully
  representable graph. The cost-rollup representation gap has an owned prerequisite item; the proof
  uses no private bridge or post-build graph/default mutation.
- **LC-I05 [INFERRED]** Final evidence records exact revisions, package/profile/schema versions, lock
  resolution, artifact hashes, fixture manifests, commands, and public/private seam classification.
- **LC-I06 [INFERRED]** IFE remains the bounded single-constraint acceptance. Stellarator WI-027 is the
  mandatory multi-constraint interaction acceptance. Neither substitutes for the other.
- **LC-I07 [INFERRED]** Release readiness remains false while a mandatory proof cell is blocked,
  skipped, served only by a private workaround, or run against a different candidate revision.
- **LC-I08 [NEED]** Items 2–13 name and remove the superseded duplicate/workaround paths they own.
  Review verifies the structural result: one authority, no parallel implementation, and no shim
  preserving an obsolete route. Do not create or require LOC baselines, budgets, per-file caps,
  net-negative targets, counting tools, or code-growth deviation reviews. Source: owner correction,
  2026-07-19. Item 1's in-flight artifacts are unchanged.
- **LC-I09 [INFERRED]** Every acceptance cell records one evidence coordinate: committed revision/
  lock set, fixture ID, owner kind, source form, source-originated polarity, anonymity, actual
  presence/source, occurrence/override shape, open predecessor register rows, both public
  live/relocated routes, and one sealed artifact identity thread through load/evaluation/persistence.
  Synthetic lower-layer construction, private adapters, filtered offenders, hand-authored contract
  fixtures, and same-machine path cancellation cannot certify a cell.

### SI. Source identity (projections; added 2026-08-05)

Projection rule: the lifecycle contract owns all behavioral wording. Each row carries its ID,
provenance grade, a one-line checkable summary that cites the governing contract statement by
number, and its source; it never restates the normative wording. Grades follow the source spec
(`.project/active/source-identity-contract/spec.md`) and the resolved 2026-08-05 owner
checkpoint; ratification does not upgrade agent-originated provenance.

- **LC-SI-01 [NEED]** Self-binding reinterpretation prohibition — contract D-4 and invariant 54;
  acceptance family SRC-01. Source: owner ruling 2026-08-05 (quote preserved at D-4).
- **LC-SI-02 [HARD]** KerML/SysIDE referent authority for written bindings — contract "Source
  identity" definitions and invariant 54. Source: Item-1 licensed probes; KerML 1.0 §8.2.3.5 and
  §7.4.11.
- **LC-SI-03 [INFERRED]** Supported forms resolve at their context-dependent referents — contract
  referent table, D-5/D-6/D-7; cells C1–C6 and C25. Source: agent recommendation ratified by owner,
  2026-08-05; Item-1/Item-2 referent evidence.
- **LC-SI-04 [HARD]** Redefinition replaces the redefined feature in its concrete context —
  contract "Source identity" definitions; cells C7/C8/C19/C21. Source: SysML v2 Part 1 §7.6 and
  §7.13.4; Item-1 `owned_redefinitions` evidence.
- **LC-SI-05 [INFERRED]** Distinct concrete occurrences are distinct sources absent an explicit
  modeled relationship — contract invariant 56 and D-13; cells C7–C10. Source: agent
  recommendation ratified by owner, 2026-08-05.
- **LC-SI-06 [INFERRED]** `#(i)` unsupported as a source-bearing binding; never flattened —
  contract D-8; family SRC-02. Source: agent recommendation ratified by owner, 2026-08-05.
- **LC-SI-07 [HARD]** `[i]` is language-rejected; load diagnostics govern — contract D-9; family
  SRC-03. Source: KerML 1.0 §8.2.5.8.2; Item-1 licensed probe.
- **LC-SI-07A [INFERRED]** Expression-binding sources deferred; fail-closed readiness diagnostic
  — contract D-15; cell C22. Source: agent recommendation ratified by owner, 2026-08-05.
- **LC-SI-08 [INHERITED]** One extraction-owned semantic source identity (declaration plus
  concrete occurrence); reconstruction is not an authority — contract invariant 55 and invariant
  26 (amended). Source: Item-2 evidence-sufficiency verdict (40 of 75 mint cells
  unreconstructable).
- **LC-SI-09 [NEED]** One occurrence, one runtime source, every and only its consumers, across
  forms — contract invariant 56 and invariant 19 (amended). Source: epic governing mission
  invariant (owner); lifecycle invariants 19/20/26.
- **LC-SI-10 [INFERRED]** Aggregation consumers share the same identity contract — contract D-14;
  cells C17/C18/C26. Source: agent recommendation ratified by owner, 2026-08-05.
- **LC-SI-11 [INHERITED]** Authored-literal independence — contract invariant 22 (amended) and
  D-11; cell C16. Source: Item-2 discriminator evidence; lifecycle invariant 22.
- **LC-SI-11A [INFERRED]** One independently overridable `LIBRARY_DEFAULT` per concrete
  calculation usage — contract invariant 22 (amended) and D-12; cell C23. Source: agent
  recommendation ratified by owner, 2026-08-05; RM 11 and ADR-001.
- **LC-SI-12 [INHERITED]** Strict/lenient policy changes only the genuine-terminal-miss
  disposition — contract invariant 20 (amended); cell C18. Source: lifecycle invariants
  19/20/26.
- **LC-SI-13 [INHERITED]** Live/snapshot/relocated routes transport one semantic source identity;
  versioned, fail-closed evidence — contract invariant 58 and the blast-radius obligation.
  Source: Item-2 route and parity findings.
- **LC-SI-14 [INHERITED]** Acceptance by off-default public mutation — contract invariant 57 and
  the Appendix C route/mutation derivation table. Source: epic success criteria; both forensic
  reports.
- **LC-SI-15 [NEED]** Blocking self-binding diagnostic, unsuppressed by same-named features —
  contract invariant 59 and the L2-correction obligation; family SRC-01. Source: owner request
  2026-08-05 (quote preserved at the contract obligation).
- **LC-SI-16 [NEED]** Distinct readiness diagnostic with valid-but-unsupported wording — contract
  invariant 59 and D-8; family SRC-02. Source: owner request 2026-08-05 (same preserved quote).
- **LC-SI-17 [INHERITED]** Codegen enforces the boundary independently of authoring validation —
  contract invariant 59. Source: ratified lifecycle stage-ownership contract.
- **LC-SI-18 [NEED]** Modeling-guidance publication as a modeling question — contract guidance
  obligation (→ Item 8). Source: owner request 2026-08-05 (quote preserved verbatim, including
  "quesiton", at the contract obligation).
- **LC-SI-19 [INFERRED]** Guidance content and example force labeling — contract guidance
  obligation (required-content list). Source: agent inference from the owner request.
- **LC-SI-20 [INHERITED]** Contract and companion carry one amended source-identity contract —
  contract invariants 19/20/22/26 (amended) and 54–60; the Appendix B correction rows; this
  companion's LC-D06/D07/D09/E04B amendments. Source: epic Item 3.
- **LC-SI-21 [INHERITED]** The acceptance authority supersedes contradictory verification-row
  readings — contract Appendix B rows; the verification-matrix row annotations for REQ-BT-13,
  REQ-CL-05, REQ-IR-01/06/07, REQ-PGD-06, REQ-SVM-01/02/04, and REQ-VBR-03/10. Source: epic
  Item 3; forensic correction registers.
- **LC-SI-22 [INHERITED]** One identity authority; superseded mechanisms derive or die — contract
  invariant 60 and D-16/D-17/D-18. Source: Item-2 adjacent-work register; ratified
  simplification constraint.
- **LC-SI-23 [INHERITED]** Complete published evidence coordinate per acceptance cell — contract
  Appendix C "Source-identity scenarios" schema and counting rules (29 cells / 35 coordinates
  after the 2026-08-07 audit-correction reopening). Source: epic Item 3 acceptance authority; lifecycle
  proof standard.

## Required acceptance scenarios

Owner Decisions 1, 2, and 3 are settled.

Source-identity acceptance scenarios are not mirrored here: the sole scenario authority is the
contract's Appendix C "Source-identity scenarios" subsection
(`.project/concepts/constraint-execution-authoritative-lifecycle-contract.md`).

Every row inherits LC-I09. “Live” means source extraction through public seams, not a prebuilt
concrete object; snapshot means relocated replay; runtime observations use the exact sealed package
from that generation. Certification records the fixture and its full evidence coordinate.
Every cell certifies on both routes; a route named in a cell title pins the historically failing
coordinates and exempts nothing.

| Scenario | Purpose |
|---|---|
| Zero constraints | Prove inert codegen bytes and successful TEAx evaluation through both the prepared and file-backed evaluators with empty constraint evidence. |
| Excluded-only usages | Prove portable exclusions and the `not_assessed` report surface through sealed-package TEAx evaluation, with no silent omission. |
| Valid non-numerical + admitted sibling | Prove warning/exclusion without blocking execution. |
| Malformed numerical + prior warnings | Prove warnings surface, then one deterministic halt before mutation. |
| Positive/negated × inline/definition-typed | Prove source-authored forms, including live `assert not constraint`, preserve IR and exact-once polarity/margin. |
| Shared definition × mixed polarity | One neutral compiled body; per-usage polarity is independent of entry order. |
| Multi-occurrence + recursive owner | Prove distinct concrete identities, a legitimate shared producer recorded in the catalog, and loud non-finite blocking. |
| Recursive containment distinct from non-finite multiplicity | Prove a named cycle path and no partial instance index. |
| Per-occurrence distinct overrides | Distinct values/verdicts prove occurrences did not collapse. |
| Anonymous admitted + anonymous excluded | Preserve both dispositions and introduce no spurious demand. |
| Anonymous admitted with actual × snapshot | Prove public live/relocated lowering without nullable-QN crash or identity drift. |
| Shared calc/constraint target across files | One retained producer and deterministic grouping/count/warning with no overwrite. |
| Producer-channel actual | Prove the producer is retained through the constraint root before pruning. |
| Literal design-attribute actual (D-2) | Prove direct exact-QN resolution with a usage-owned attribute on a concrete `PartUsage` and a self-named actual; no passthrough is required. |
| Modeled-default formal | Prove the default applies and an override changes the verdict. |
| Ambiguous/defaulted producer resolution | A model with two same-leaf candidate design attributes and a defaulted-fallback shape fails generation with a named ambiguity/producer error, or resolves only under exact QN; no verdict is ever produced from a guessed or defaulted binding while V11 is clean. |
| Definition-owned assert through redefining usage | Preserve definition source, redefining occurrence, and actual identity. |
| Signed/unit default + unsupported wrapper | Preserve explicit `-0.1` and `[MW]`; unsupported wrappers never invent values. |
| Pre-existing V11 + unrelated constraint | Extension succeeds; strict final coverage still fails until the base graph is complete. |
| Potential extension-introduced V11 (Item 3B) | Prove the shape and differential failure, or prove it impossible and remove extension-time coverage validation. |
| Live + relocated snapshot | Prove retained-producer and full-tree byte parity with no checkout-absolute bytes. |
| Malformed snapshot sections | Fail before reconstruction with section/field context and recapture guidance. |
| Name/path/schema collisions | Prove pre-output rejection and target preservation. |
| Missing catalog with constraint modules | Named pre-output failure; no renderer, writer, or target mutation. |
| Catalog/profile/runtime skew both directions | Fail closed before semantic use. |
| Generation-plan nested mutation | Written semantic contents remain equal to the validated plan. |
| Out-of-root warning followed by BLOCK | Portable warning location remains visible; `BLOCK` still halts. |
| Mixed satisfied/violated/indeterminate population | Prove headline precedence and retained ordinary outputs. |
| Non-finite value + four arithmetic exceptions | Prove phase/module/cause and full-report parity across both evaluators, with the expected phase for each shape pinned by the fixture rather than established by mutual agreement. |
| File-backed completed reports | Persist/harvest exact satisfied, violated, and indeterminate JSON with package identity. |
| Trusted verifier bootstrap | Reject an unconditional-success verifier and verifier/runtime version skew before package code. |
| Seal/verify symlink and provenance | Reject forbidden links symmetrically and prevent foreign-file re-seal laundering. |
| Nested evidence mutation attempt | Generated report/results/status/margin/observations remain authoritative and persisted unchanged. |
| Multi-entry study + canonical embedded catalog (D-3) | Prove CE-F1/CE-F2 closure without an alternate schema, materializer, or consumer adapter. |
| Resume/query across incompatible fingerprints | Reject mismatch or start an explicit new lineage; never rebind silently. |
| Zero-entry and excluded-only entry-channel shapes | Prove complete zero/one/multiple mappings with no invented inputs. |
| Fact-consumer mutation | A behavioral test fails when a load-bearing consumer is removed; static map edits do not satisfy it. |
| Remediation simplification | Verify named superseded paths are absent and no parallel authority or route replaced them; line counts are not proof. |
| Invalid explicit `TEAX_SIMKIT_PATH` (test helper) | Fail on the explicit invalid path; never fall through to sibling discovery. |
| IFE 2,301-point acceptance | Rerun exact final candidates through canonical stock seams; preserve semantics and anchors. |
| Stellarator five-constraint acceptance (D-1/D-2) | Remove WI-027 D7 passthroughs; prove a fully representable graph, no bridge/mutation, five verdicts, and sealed handwritten code. |

## Open implementation and proof register

The owner ratified this dependency order on 2026-07-19. Execution ownership is defined in
`.project/backlog/epic_constraint_execution_lifecycle_remediation.md`.

| Order | Gap | Proposed owner | Required closure |
|---:|---|---|---|
| 0 | Commit-pinned compatible candidate | Lifecycle Item 0 | Exact codegen/agentic-mbse/TEAx hashes and locks install together; semantic/runtime skew tests pass. |
| 1 | R-4/R-5/R-7 occurrence and demand | Lifecycle Item 1 | Anonymous-actual, shared-demand, recursive, finite, and per-occurrence-override cells pass on the live leg; the anonymous cell's relocated leg completes with row 5. |
| 2 | Resolver unification + Gate A | Lifecycle Item 2 | One producer/exact-QN resolver serves calc, aggregation, and constraint; direct literal works; duplicate ladders are deleted. |
| 3 | Gate B capture-time check scope | Lifecycle Item 3 | Constructed case proves/refutes new V11 creation; delete the call if vacuous or differential-check it; file fusion finding #8. |
| 4 | Diagnostics and defaults | Lifecycle Item 4 | Versioned severity schema/sink/skew gates, warning order, and `-0.1`/`[MW]` defaults pass. |
| 5 | Whole-tree portability | Lifecycle Item 5 | Docstrings, loader paths, anonymous IDs, catalog/contracts, and full generated bytes are checkout-independent. |
| 6 | Public/version documentation | Lifecycle Item 6 | Correction-register claims agree with pinned landed candidates. |
| 7 | F1/environment evidence | Lifecycle Item 6 | Record `d545701`, repair `927a9e1`, compare reports, and scope invalid-path test infrastructure. |
| 8 | Trusted verifier/bootstrap skew | Lifecycle Item 7 | Runtime-trusted verifier rejects bypass; verifier/runtime-contract skew fails closed. |
| 9 | Seal provenance | Lifecycle Item 7 | Generation manifest distinguishes artifact origins; re-seal cannot launder foreign content. |
| 10 | Catalog/CE-F1 + store transition | Lifecycle Item 8 | Five fields + admitted usage record land; alternate schema/materializer/fixture/stand-in deleted; stores migrate by proof or archive. |
| 11 | Multi-entry CE-F2 | Lifecycle Item 9 | Stock bridge supplies complete zero/one/multiple typed channel mappings. |
| 12 | Producer completeness + stellarator rollup | Lifecycle Item 10 | Exact producers are proven independently of V11 through the ambiguous/defaulted acceptance cell; WI-027 D7 is amended/removed; public generation succeeds without bridge/mutation. |
| 13 | Constraint-free TEAx | Lifecycle Item 11 | Constraint-free package loads/evaluates with empty constraint evidence. |
| 14 | Evidence mutation protection | Lifecycle Item 11 | Freeze/isolate nested report/results; policy/store mutation tests pass. |
| 15 | File-backed report machinery | Lifecycle Item 11 | Register/persist/harvest exact completed reports with package identity and no adapter. |
| 16 | Grandfather/tracking-key lifecycle | Lifecycle Item 12 | Normal path fails closed on skip-lowering; tracking key is implemented/cataloged or removed with claims corrected. |
| 17 | Composed public proof | Lifecycle Item 13 | One pinned artifact thread passes public live/relocated generation, seal/load/evaluate/persist/query, IFE, and stellarator, and every mandatory matrix cell is certified at the pinned revision set. |

No later row may certify around an earlier open dependency. LC-I09 enforces this by binding every
status to the same committed revision/artifact thread and naming open predecessors. F1 reconciles
evidence/release/environment behavior; it does not redo the landed normalization implementation.

## Owner decisions

1. **Resolved 2026-07-19.** `[OWNER-VERBATIM]` “I really don't want to add support for ‘public
   late-fill’ -- that sounds like a great way to allow bugs and enable injecting even more.” The
   supported lifecycle requires a fully representable graph and excludes late fill and post-build
   graph/default mutation. **Option referent `[AGENT]`:** A, selected: graph-complete modeled
   producers plus ordinary declared external inputs. B, rejected: public post-build completion.
2. **Resolved 2026-07-19.** `[OWNER-VERBATIM]` “100% Option A. I am BLOW AWAY this wasn't
   already a requirement and this is a design gap. That is the whole fucking ethos of the
   graph-building.” Direct literal-valued design attributes are valid constraint actuals. Gate A is
   an implementation/conformance defect; passthrough calculations are not the intended pattern.
   **Option referent `[AGENT]`:** A, selected: direct shared producer/exact-QN resolution. B,
   rejected: model-authored passthrough calculations. This supersedes owner-ratified WI-027 D7;
   its design must be amended and the passthroughs removed before acceptance.
3. **Resolved 2026-07-19.** `[OWNER-VERBATIM]` “100% Option A. We need to purge this mess.”
   Codegen's embedded model-contract catalog is the sole schema authority. TEAx consumes it
   directly; the alternate TEAx schema, fusion materializer, identity stand-in, and semantic
   reconstruction are deleted. **Option referent `[AGENT]`:** A, selected: embedded codegen schema
   consumed directly, with only a mechanically identical optional export. B, rejected: a
   codegen-owned standalone catalog is canonical and the model contract references its fingerprint.

## Non-goals

- Adding new executable expression capability beyond profile v4.
- Defining real/quantity equality without a separately modeled tolerance contract.
- Executing requirement satisfaction, temporal constraints, or non-numerical statements.
- Treating study penalties or feasibility policy as modeled constraint semantics.
- Claiming historical snapshots reproduce historical profile decisions; replay uses the installed
  pinned profile.
- Making anonymous identity cross-version stable. Resolved (Item 12): the `tracking_key` field was
  removed, so no cross-version correlation is claimed.
- Treating a private consumer bridge as a supported upstream API merely because it works.
- Re-auditing completed remediation items before the lifecycle contract is ratified.

## Provenance map

| Requirement range | Primary design/evidence source |
|---|---|
| LC-A | Original concepts and `20260710-095634_constraint-execution-and-design-space-exploration.md` |
| LC-B | agentic-mbse completed `constraint-facts` and `expression-ir` spec/design/audit sets |
| LC-C | numerical-profile spec/design and agentic-mbse `constraint-wave-profile-semantics` artifacts |
| LC-D–E | completed sysml-codegen constraint-lowering/generation spec/design/audits plus current remediation research |
| LC-F | completed snapshot-v3/package-contracts artifacts and current contract/seal code |
| LC-G | TEAx evaluator/study audits, F1 design/audit, and the IFE findings |
| LC-H–I | current public APIs, Gate A/Gate B reports, WI-027, IFE adapters, and this owner's proof bar |

The evidence census gives the full path ledger and records where current code contradicts these
requirements. `[INHERITED]` and `[INFERRED]` rules remain challengeable by re-deriving them against
those sources.

## Related artifacts

- **Authoritative lifecycle design:**
  `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md`
- **Evidence census:**
  `.project/research/20260719-111228_constraint-execution-lifecycle-evidence-census.md`
- **Adversarial review:**
  `.project/research/20260719-125806_constraint-execution-lifecycle-contract-adversarial-review.md`
- **Correction re-review:**
  `.project/research/20260719-134700_constraint-execution-lifecycle-contract-correction-rereview.md`
- **Original concepts:**
  `.project/concepts/constraint-execution-and-design-space-studies.md` and
  `.project/concepts/constraint-execution-and-design-space-studies-claude.md`
- **Completed epic:** `.project/completed/20260713_epic_constraint_execution.md`
- **Current remediation:**
  `.project/backlog/epic_constraint_execution_lifecycle_remediation.md`
- **Superseded remediation history:**
  `.project/backlog/epic_constraint_pr_wave_remediation.md`
- **Gate B reports:**
  `.project/research/20260719-103419_gate-b-independent-assessment.md` and
  `../fusion-tea-stellarator-mbse-demo/.project/research/20260719-082509_gate-b-root-cause-constraint-lowering-vs-v11-bridge.md`

## Next step

Execute `.project/backlog/epic_constraint_execution_lifecycle_remediation.md` from register row 0.
Certification follows the register order and row 17 runs last.
