# Constraint Execution: Authoritative Lifecycle Contract

**Status:** Ratified normative authority — 2026-07-19. No certified implementation candidate exists.
**Owner:** Reid W
**Ratified:** 2026-07-19 — [OWNER-VERBATIM] “Ratified.”
**Created:** 2026-07-19
**Scope:** authoring validation, code generation, package integrity, evaluation, and studies
**Requirements:** `.project/active/constraint-execution-lifecycle-contract/spec.md`
**Evidence:** `.project/research/20260719-111228_constraint-execution-lifecycle-evidence-census.md`
**Adversarial review:**
`.project/research/20260719-125806_constraint-execution-lifecycle-contract-adversarial-review.md`
**Correction re-review:**
`.project/research/20260719-134700_constraint-execution-lifecycle-contract-correction-rereview.md`

## Authority and reading rule

After owner ratification, this document is the behavioral authority for modeled constraint
execution across agentic-mbse, sysml-codegen, and TEAx. Earlier concepts, specs, designs, public
docs, and PR bodies remain provenance. They do not override an explicit correction here.

This contract says what the architecture must do. Appendix A reports what current code proves.
An implemented or certified component is not evidence that an untested composition works.

Detailed requirement IDs and provenance grades live in the companion spec. Owner approval of an
agent recommendation does not rewrite its origin.

## Implementation candidate status

No commit-pinned, mutually installable implementation candidate exists as of 2026-07-19. The observed
worktree bases are sysml-codegen `512786c7dfab44fba7a0185d09e845b7494c702d` and agentic-mbse
`4ed2a0728ea49298666415cd389d9a6173a81a3e`; both carry uncommitted lifecycle changes. TEAx's tracked
tree is at `d545701f575133350474108c96202a2ac5244462` with only untracked orchestration logs. These are
observation bases, not a candidate revision set. Profile-v4 ordering and polarity behavior exists
only in the uncommitted agentic-mbse tree;
committed refs remain profile v3, and the committed companion/codegen package versions are not a
mutually satisfiable pair.

Ratifying this contract adopts the target architecture and activates the remediation register; it
certifies no current behavior. Certification and release readiness remain blocked until every
relevant change is committed, the exact cross-repository hashes and locks are recorded (register
row 0), and that one revision set passes the mandatory public-path matrix (register row 17).

## The mental model

There are three jobs:

1. **The model states meaning.** SysML defines the positive predicate, its formal/actual bindings,
   ownership, concrete context, and assertion polarity.
2. **The generated package evaluates meaning.** Codegen turns a supported, successfully bound
   assertion into an ordinary graph module and read-only evidence. A bad verdict is data. Broken
   execution is a failure.
3. **The study decides what to do.** TEAx may classify, reject, or penalize evidence. It cannot
   rewrite what the model asserted or what the evaluator observed.

That separation is the architecture's spine. It prevents hand-coded feasibility rules, parser
semantics inside the runtime, and optimizer policy from becoming competing sources of truth.

## End-to-end lifecycle

```text
SysML source
  │
  ├─ parse + neutral extraction ──> ConstraintFacts + ExpressionIR
  │                                  │
  │                                  ├─ agentic-mbse L4/L6 validation
  │                                  │     (diagnostics only)
  │                                  │
  │                                  └─ sysml-codegen re-evaluates profile
  │                                        │
  │                ┌───────────────────────┼────────────────────────┐
  │                │                       │                        │
  │              ADMIT              NON_NUMERICAL /            BLOCK
  │                │                  UNASSESSED                  │
  │                v                       v                        v
  │       contextual lower/expand  visible exclusion        named model halt
  │       + strict resolution       or contextual exclusion
  │                │
  │                v
  │       inject constraint demand → prune/build base graph
  │                │
  │       constraint graph extension → catalog assembly
  │                │
  │       extension channel validation
  │       + Item 3B coverage-scope decision
  │                │
  │       graph-complete producer validation
  │                │
  │       whole-graph V11 + precomputed generation plan
  │                │
  │       deterministic render + model contract + seal
  │                │
  │       verified TEAx package load
  │                │
  │       ConstraintEvaluation(s) + ConstraintReport
  │                │
  └────────────────v
        read-only study evidence → policy → durable case/query results
```

The profile appears twice because there are two consumers. Authoring validation and codegen make
the same classification from the same neutral facts. Validation does not create executable output
and does not pass mutable decision state to codegen.

Snapshot replay stores neutral facts and occurrence evidence, then reuses the same semantic
profile/lowering/extension/catalog functions through a route-specific `include_all` graph rebuild.
It never stores a finished graph or historical profile decision. The normal product path must
reject grandfathered skip-lowering snapshots; explicit legacy inspection is
non-executable/non-certifying.

## Stage ownership and contracts

| Stage | Owner | Semantic authority | Input → output | Consumer | Failure boundary |
|---|---|---|---|---|---|
| Parse/extract | agentic-mbse | SysML meaning/provenance | Model → neutral facts/IR | Profile | Named diagnostic |
| Profile | agentic-mbse | Predicate eligibility/polarity | Facts → one usage decision | Validation/lowering | Total default-deny decision |
| Authoring validation | agentic-mbse | Diagnostics only | Decisions → L4/L6 issues | Author | `BLOCK` fails L6; warnings visible |
| Lowering | sysml-codegen | Context/binding/occurrence | Facts/decisions → concrete/excluded | Demand/base graph | Named error; no fallback |
| Demand/base graph | sysml-codegen | Producer liveness | Resolved demand → live/full graph | Extension | Missing producer |
| Extension | sysml-codegen | Runtime wiring | Base graph/concrete → extended graph | Catalog | Dangling/newly invalid channel; Item 3B owns coverage scope |
| Catalog | sysml-codegen | Usage/execution disposition | Facts/concrete → embedded catalog | Generation | Missing/inconsistent coverage |
| Generation | sysml-codegen | Validated graph/plan | Graph/catalog → package | Contracts/seal | Preflight before clear; later writes may fail |
| Contracts/seal | sysml-codegen | Semantic/physical identity | Package tree → contracts | TEAx loader | Incomplete/unsafe tree cannot seal |
| Load/evaluate | TEAx | Runtime execution | Verified package/inputs → evidence | Study | Phase-tagged failure |
| Study | TEAx | Explicit policy only | Evidence/policy → durable cases | Query/user | Crash-safe failure/resume |

## Normative invariants

### Meaning and visibility

1. Every usage gets one profile disposition. Any `BLOCK` halts the model. After generation, every
   other usage has executable concrete representation or a visible exclusion. After evaluation,
   every module yields evidence or a named execution failure.
2. Neutral facts contain model semantics and provenance only. They contain no graph roles, Python
   names, generated identity, or study policy.
3. `ExpressionIR` is the structural semantic representation. Reconstructed text is display only.
4. An unknown syntax or IR node becomes explicit unsupported data. It is never coerced or dropped.
5. The selected positive predicate bytes are unchanged from facts through decision, concrete
   record, catalog, generation plan, and compiler input.
6. Assertion polarity is separate from the positive predicate and applied once when each concrete
   assertion derives status and simple margin.

### Profile

7. The profile is pure, deterministic, total, and versioned independently from the fact schema.
8. Outcomes are exactly `ADMIT`, `BLOCK`, `NON_NUMERICAL`, and `UNASSESSED`.
9. `ADMIT` places canonical IR inside the compiler's semantic envelope. Downstream may not
   reclassify it, but named contextual lowering, graph, input, and runtime failures remain.
10. The ratification target is numerical profile v4. Ordering admits Integer/Real pairs and
    compatible exact-unit Quantity pairs. Boolean/String/enum ordering blocks. This is a target
    requirement until a compatible cross-repository revision set is committed and pinned.
11. No equality or `!=` executes. Boolean/String/enum equality is non-numerical; numerical equality
    blocks until a separate exactness/tolerance contract exists.
12. The ratification target admits inline and definition-typed assertions and positive and negated
    membership when polarity is an actual Boolean. This behavior is not a committed current-state
    claim until the revision set above exists.
13. Every fact field has a real code consumer or tested decision-irrelevant explanation. A static
    consumer-map label alone is not proof.
14. A semantic change bumps the profile version and fails both codegen/companion skew directions.
15. Every extraction diagnostic has a stable code/severity. Blocking diagnostics halt before
    lowering; advisory diagnostics remain visible; an unclassified diagnostic fails closed. The
    current fact schema has no severity field, so closure requires a versioned facts-schema change
    and corresponding fail-closed skew tests.

### Concrete lowering and graph construction

16. Owner kind decides occurrence expansion. Source form decides predicate selection. The axes are
    independent.
17. Every finite occurrence gets its own execution ID, catalog entry, module, and result channel.
    A truly shared producer may feed several occurrences, but that sharing is recorded.
18. Recursive, non-finite, or malformed occurrence expansion blocks loudly. Partial expansion is
    forbidden.
19. Calculation inputs and constraint actuals use one shared positive-resolution procedure: first a
    real producer channel, then a real design attribute under its exact qualified identity. An
    omitted constraint formal accepts a modeled default only when the model declares it.
20. Strictness changes only the terminal miss policy. Constraint resolution never invents a value,
    parses display text, or reaches the calculation fallback; a miss is a contextual generation
    error. Positive resolution may not fork into consumer-specific ladders.
21. A direct literal-valued design attribute is a valid design-attribute actual. It must be available
    during graph construction and must reuse the same QN-keyed typed entry point as any calculation
    consumer. Requiring a passthrough calculation is a workaround, not conformance.
22. Modeled defaults remain overridable typed parameters and never become study variables
    automatically.
23. Constraint input channels join dependency roots before live pruning. Supported snapshot replay
    retains the equivalent producers through its full-graph rebuild.
24. Constraint extension does not reject unrelated pre-existing uncovered inputs. Item 3B must
    first construct a case that proves or refutes whether extension can introduce a new V11
    uncovered input. If it can, extension rejects only the introduced violation. If it cannot,
    extension performs channel validation only and final generation alone owns V11 coverage.
25. Whole-graph channel-reference validation still runs after extension.
26. Final generation requires zero whole-graph V11 uncovered inputs. A separate producer-
    completeness check proves that every model-derived consumed value resolves to one intended
    producer under exact identity, while legitimate external design inputs remain ordinary typed
    entry channels. V11 is not a substitute: a defaulted fallback or ambiguous first-match binding
    can pass it. No late-fill, leaf-name guess, ambiguous first-pick, or post-build graph/default
    mutation seam is supported.
27. Eligible execution IDs use source-local identity, concrete occurrence, membership, and
    polarity. Excluded IDs use stable source/context identity because occurrence or polarity may
    not exist. The executable fingerprint scopes IDs but is not an ID input. Cross-version
    correlation is supported only through an explicit author key that is populated and cataloged;
    otherwise the system makes no correlation claim.

### Catalog, generation, and package

28. The canonical catalog exposes definition inventory, one visible disposition per usage, and one
    concrete execution entry per admitted occurrence. It carries source form, usage name and QN,
    owner QN, definition QN, an explicit definition-to-usage join, and per-occurrence identity. The
    five TEAx-consumed fields live on each per-eligible concrete entry; `owner_qn` is a real qualified
    name distinct from `owner_instance_path`, and the definition-to-usage join is entry-level.
    Current code lacks the admitted per-usage record and five TEAx-consumed fields, so this invariant
    carries additive schema work.
29. One polarity-neutral predicate body is compiled per true source. One wrapper is generated per
    concrete assertion. Entries sharing a predicate source must agree on the neutral source/IR while
    preserving their independently sourced polarity; mixed polarity may not be taken from whichever
    entry sorts first.
30. Names and paths are proven collision-free against generated scopes before output mutation.
31. The precomputed generation plan validates catalog/source/polarity/IR/input/name/compile/render
    agreement before clearing the target; writers do not change its semantic contents.
32. The report aggregator has one required exact-schema input per eligible concrete assertion.
    Missing or extra evidence fails, and the aggregator is structurally retained as an exit ancestor
    whenever a constraint report is required. A model with constraint usages but zero eligible
    concrete assertions still requires the zero-input aggregator and a `not_assessed` report; a model
    with no constraint usages remains inert and has no aggregator.
33. Headline precedence is violation, then indeterminate, then all satisfied, then not assessed.
34. Semantic source referents are portable. Checkout-absolute paths never enter IDs, fingerprints,
    contracts, generated code or docstrings, reports, catalogs, or reconstructed snapshot fields.
35. Live and supported snapshot routes agree on decisions, diagnostics, retained producers,
    graph/catalog values, fingerprints, and generated bytes.
36. The model contract owns semantic identity; the package contract owns executable identity.
37. Anything that seals verifies unchanged. Sealing and verification apply one symlink/path policy.
    A seal proves integrity, not generation provenance: re-sealing records and validates the
    generation manifest and may not relabel arbitrary foreign files as codegen-produced artifacts.
38. The supported TEAx loader verifies before model imports. Arbitrary direct imports are unsupported.
39. No untrusted package code runs before verification. Use a runtime-owned verifier or authenticate
    package-local verifier bytes before execution; the current loader violates this bootstrap rule.
    Verifier and runtime-contract versions have one source or an explicit compatibility table, and
    skew fails closed before package code executes.
40. Every downstream constraint-generation seam consumes the graph and embedded catalog. It never
    re-profiles/re-lowers stale context; unrelated calculation generators may use their own fields.

### Runtime and studies

41. A completed constraint module returns authoritative evaluation evidence. Downstream code cannot
    change the envelope, generated report, nested results, observations, status, or margin; enforce
    this by deep freeze or defensive isolation. Current nested models violate it.
42. A violated result never raises and never removes ordinary outputs.
43. An already-produced non-finite comparison operand becomes Kleene unknown; overall unknown is
    `indeterminate`.
44. Thrown arithmetic, missing input, schema failure, or missing aggregate result is execution
    failure, never a verdict.
45. Prepared and file-backed evaluators normalize a module failure identically, name the exact
    phase/module, preserve the original exception as cause, and return equal report content for
    equivalent completed executions.
46. The public file-backed route persists and harvests the exact report plus package identity with no
    consumer schema adapter.
46a. A constraint-free package is valid input to TEAx. Absence of the constraint report produces
    empty constraint evidence rather than a `KeyError`; codegen remains free to omit constraint-only
    catalog/modules for byte-stable constraint-free generation.
47. The study bridge supplies every typed entry channel. A candidate changes selected fields in a
    complete typed baseline; it does not omit unrelated channels.
48. Codegen's catalog embedded in the model contract is the sole catalog schema authority. TEAx
    consumes its source form, usage identity, owner QN, definition QN, explicit join, and occurrence
    data directly. The alternate TEAx schema, hand-authored schema fixture, stand-in fingerprint,
    and consumer materializer are retired. A separately serialized catalog, if independently
    justified later, contains the same schema/fingerprint and performs no reconstruction.
49. Study policy cannot mutate authoritative status, margin, observations,
    identity, or catalog linkage.
50. Proposal, candidate, case, attempt, and artifact identities remain distinct. Commit/resume is
    crash-safe and compatibility-bound to the exact package and real semantic/catalog/executable
    fingerprints. Rebinding from the catalog-byte stand-in requires an explicit transition: a
    migration proves old and new artifact equivalence, or the old store remains an archived lineage
    and a new store begins. Identity is never silently reassigned.
51. `assessment_failed` remains a distinct evidence-preserving study state. A policy failure does
    not erase successful model evidence or masquerade as model execution failure.
52. Simple-margin sign respects assertion polarity and is zero at the modeled boundary. Compound
    predicates do not invent an aggregate margin.
53. Grandfathered skip-lowering snapshots fail closed on the normal product path. Any explicit
    legacy-inspection mode is opt-in, visibly non-executable, and cannot produce a certifying seal.

## Supported boundary and owner decisions

The supported core is public codegen generation, final V11 and planning, render/seal, verified TEAx
load/evaluation, and study APIs. Private mutation, conversion, and wrappers do not certify it.

- **D-1 [OWNER-VERBATIM], decided 2026-07-19:** “I really don't want to add support for
  ‘public late-fill’ -- that sounds like a great way to allow bugs and enable injecting even more.”
  Supported codegen therefore requires a fully representable graph and exposes no late-fill or
  post-build graph/default mutation seam. The fusion bridge is private workaround evidence only.
  **Option referent [AGENT]:** A, selected: graph-complete modeled producers plus ordinary declared
  external typed inputs. B, rejected: a public post-build completion/mutation seam.
- **D-2 [OWNER-VERBATIM], decided 2026-07-19:** “100% Option A. I am BLOW AWAY this wasn't
  already a requirement and this is a design gap. That is the whole fucking ethos of the
  graph-building.” Direct literal design-attribute actuals are valid; Gate A is an implementation
  defect. Calculations and constraints share positive resolution, with strictness only at the
  terminal miss. **Option referent [AGENT]:** A, selected: direct resolution through the shared
  producer/exact-QN design-attribute path. B, rejected: require model-authored passthrough
  calculations. This later owner decision supersedes WI-027 D7's same-day owner ruling in
  `../fusion-tea-stellarator-mbse-demo/work/active/WI-027_demo-constraint-execution/design.md`;
  that artifact must point here and its passthroughs must be removed before stellarator acceptance.
- **D-3 [OWNER-VERBATIM], decided 2026-07-19:** “100% Option A. We need to purge this mess.”
  Codegen's embedded model-contract catalog is canonical and TEAx consumes it directly. Closure
  deletes the fusion catalog materializer, the independently shaped TEAx catalog contract, and all
  qualified-name or predicate-text reconstruction used to bridge them. TEAx compatibility binds to
  the real model-contract/catalog identity, and catalog fixtures originate from codegen artifacts.
  **Option referent [AGENT]:** A, selected: the embedded codegen catalog is canonical and TEAx reads
  it directly; any later standalone export is mechanically identical. B, rejected: a codegen-owned
  standalone catalog is canonical and the model contract references its fingerprint.

### Simplification constraint

**[OWNER-VERBATIM]** “I would REALLY LIKE for us to REDUCE the total number of lines of code when
we fix all this shit. I have to believe there are opportunities for simplification and removing
hacky code.” The intended outcome is simpler architecture: shared resolution, one catalog schema,
and removal of superseded bridges, adapters, and duplicated validation paths. **[OWNER], 2026-07-19
correction:** For lifecycle Items 2–13, line counts are not requirements, evidence obligations,
budgets, caps, gates, or deviation triggers. Correct code may grow when explicit types, diagnostics,
or invariants require it. Review simplicity structurally: one authority, no duplicate route, and no
new shim around a superseded mechanism. Item 1 is already in flight and its artifacts are untouched.

## Proof standard

“Beyond a reasonable doubt” means one composed, falsifiable, public-path proof:

- both live and relocated-snapshot entry routes;
- exact candidate versions, locks, hashes, and fail-closed skew;
- positive and mutation evidence at every terminal boundary;
- interaction coverage across source form, polarity, profile outcome, actual source, occurrence,
  V11 state, route, entry-channel shape, and evaluator outcome;
- a real bounded single-constraint acceptance (IFE);
- a real five-constraint, multi-entry stellarator acceptance on a fully representable graph: every
  modeled/computed dependency has a graph producer, and ordinary declared design inputs enter only
  through the generated typed input boundary;
- no private adapter counted as proof of a supported upstream seam.

Every matrix cell is bound to an evidence coordinate, not merely an expected observation. Its
certification records: exact cross-repository revisions and locks; a fixture ID; owner kind; source
form; source-originated polarity; anonymity; actual presence/source; occurrence/override shape;
open predecessor register rows; live and relocated-snapshot routes through public seams; and the
generated, sealed, loaded, and persisted artifact identities. A lower-layer synthetic object cannot
certify a source-to-runtime cell. Both routes use the same semantic candidate, and all
post-generation observations follow one sealed artifact thread. Private adapters, filtered
offenders, hand-authored contract fixtures, and same-machine path cancellation are non-certifying.

Release readiness is false if a mandatory cell is skipped, blocked, uses a different revision, or
works only through a private bridge.

## Current conclusion

The architecture above is coherent and ratified as the normative target architecture. Ratification
certifies no implementation: no matrix cell may be certified and no release claim made until
register row 0 pins a compatible candidate and row 17's composed proof passes on it. Open work
includes resolver unification/Gate A;
occurrence/demand; the Gate B scope probe; diagnostic schema/defaults; whole-tree portability;
producer completeness; catalog/store migration; multi-entry and constraint-free TEAx paths; seal
provenance and trusted bootstrap; evidence immutability; report persistence machinery; grandfather
fail-closed and tracking-key lifecycle; and final IFE/stellarator proof on one artifact thread.

Next: execute `.project/backlog/epic_constraint_execution_lifecycle_remediation.md` from register
row 0; certification follows the register order and row 17 runs last.

## Appendix A: Current proof matrix

| Boundary | Current evidence | Verdict |
|---|---|---|
| SysML → neutral facts | S1 live matrix, production facts/codec tests | Proven for recorded shapes |
| Facts → profile v4 | Exhaustive working-tree category/polarity tests | Not commit-pinned; committed refs are v3 and the package pair is incompatible |
| Extraction diagnostics → consumers | Diagnostics serialized without severity | Schema and production sink absent; build work open |
| Independent authoring validation | Working-tree L4/L6 consumers and tests | Implemented only in an unpinned candidate |
| Profile → concrete lowering | Original lowering fixtures + current route tests | Bounded; Gate A open |
| Occurrence/demand | Original finite fixtures | R-4/R-5/R-7 open |
| Base graph → constraint extension | S4 and graph-extension fixtures | Gate B scope/vacuity question open |
| Concrete/catalog → generated modules | Generation tests and real-simkit lane | Strong for selected cases |
| Generation → untouched target on failure | v4 plan/name-safety tests | Locally complete for covered guards |
| Live → snapshot | Snapshot v3/parity/portability suites | Full-tree parity contradicted by absolute calc-docstring/ID paths |
| Seal → verify | Package-contract and Item 6 matrices | Locally complete |
| Seal → supported TEAx load | Loader verifies before model import | Bootstrap and seal provenance open |
| Generated module → TEAx failure/evidence | Evaluation suites + F1 audit | F1 at `d545701`; audit mismatch and mutation protection open |
| Successful file-backed report persistence | No report registration/persist/harvest machinery | Build work absent |
| Evaluator → crash-safe study | TEAx study suite and integration spike | Proven for one-entry fixture |
| Catalog → TEAx study | TEAx hashes a standalone catalog; codegen semantic fingerprint has zero consumers; IFE used a materializer | CE-F1 open |
| Multi-entry candidate → evaluator | Stock TEAx structures are single-entry; IFE used a wrapper | CE-F2 open |
| Constraint-free package → TEAx | No accepting path; evaluator indexes missing report | Contradicted; bare `KeyError` today |
| IFE real acceptance | 2,294 matches + 7 boundary differences through private adapters | Bounded consumer evidence, not supported public-path proof |
| Stellarator real acceptance | Five facts after now-superseded passthrough workaround | Blocked before generation; D7 artifact stale |
| Public path generation→seal→verify→TEAx | No single kept test | Not proven |

## Appendix B: Explicit correction register

| Superseded claim | Source/provenance | Governing correction |
|---|---|---|
| Profile classification is invoked only by codegen | Prior conversational description; census C-1 | Both agentic-mbse validation and codegen independently invoke it. |
| Typed Boolean/string/integer/enum equality executes | Original concept matrix | Target profile v4 executes no equality; candidate revisions remain unpinned. |
| Whole extended graph must be V11-clean during extension | Completed lowering INV-6 | Extension never rejects unrelated pre-existing offenders; Item 3B first proves whether a differential V11 check is meaningful. |
| Constraint actuals need calculation passthroughs | WI-027 D7, owner-ruled 2026-07-19 | Later owner D-2 supersedes D7: direct literal attributes are valid. Shared resolver implementation is required but does not exist today. |
| Catalog “source record” means the same thing everywhere | Original concept vs landed class; census C-5 | Landed source records are definition inventory; canonical coverage also needs an explicit per-usage disposition/join. |
| Catalog is absent when no assertion is admitted | Completed generation assumptions | It is absent when no usages exist; excluded-only usages retain catalog/report visibility. |
| Snapshot stores or freezes eligibility decisions | Conversational supersession (no documentary source); historical snapshot prose | Snapshot stores neutral facts; installed pinned semantics re-profile on replay. |
| Non-finite and thrown arithmetic both become indeterminate | Early concept/runtime prose | Produced non-finite values may be indeterminate; thrown arithmetic is normalized failure. |
| Fusion late-fill bridge is a sanctioned codegen seam | Gate B consumer report | Late fill is unsupported; bridge evidence cannot certify upstream behavior. |
| F1 remains unimplemented | Stale TEAx audit header | F1 is implemented at `d545701`; release/evidence state still needs reconciliation. |
| IFE acceptance proves arbitrary whole-plant integration | IFE consumer findings | It proves a bounded constraint through private adapters, not the public Gate A/Gate B/multi-entry cross-product. |
| Every arbitrary import/load verifies automatically | Historical loader prose | Only the supported loader may verify; arbitrary imports are unsupported. |
| Verification runs before any package code | Loader claim | Current loader executes unauthenticated package-local verifier code first; trusted bootstrap and version-skew closure are required. |
| L6 `BLOCK` is a non-failing warning | Profile-v3 documentation | Target profile v4 makes `BLOCK` an L6 error; this is not committed/pinned yet. |
| Snapshot docs' profile v3 / package 0.1.1 claims are current | Public snapshot docs | Target is profile v4 / package 0.1.2; landing must pin compatible commits and update docs. |
| “No equality or inequality enters execution” | Historical public docs | No equality executes; target profile admits numerical ordering inequalities. |
| The retired manifest defines subtype coverage | Migration-era tests/docs | Base constraint-usage facts plus explicit per-usage catalog disposition are authoritative. |
| Aggregator always exists even with no usage | Original concept | No usages is inert; excluded-only usages retain `not_assessed` visibility. |
| Snapshot replay is the live route after extraction | Conversational supersession (no documentary source); historical architecture prose | Replay uses route-specific `include_all`; grandfathered skip-lowering fails closed for certification. |

## Appendix C: Mandatory acceptance matrix

D-1, D-2, and D-3 are owner-decided.

Every row inherits the proof-standard evidence coordinate. “Live” means source extraction through
the public CLI, not a prebuilt `ConcreteConstraint`; “snapshot” means relocated replay; and runtime
rows follow the exact package sealed by that generation. Certification names the fixture and shape.
Every cell certifies on both routes; a route named in a cell title pins the historically failing
coordinates and exempts nothing.

| Case | Required observation |
|---|---|
| Zero constraint usages | No constraint catalog/modules; bytes unchanged; the sealed package loads/evaluates in TEAx through both the prepared and file-backed evaluators with empty constraint evidence. |
| Excluded-only usages | Portable exclusions plus `not_assessed`; no silent omission; the sealed package evaluates in TEAx with a `not_assessed` report surface. |
| ADMIT + NON_NUMERICAL + BLOCK mix | Warnings in order, then one halt before mutation; no compiler call. |
| Positive/negated × inline/definition-typed | Source-authored forms, including live `assert not constraint`, preserve positive IR/raw value and complementary truth/status/margin. |
| Shared definition × mixed polarity | One neutral compiled body; each source-authored usage retains its own polarity and margin sign independent of ordering. |
| One definition × multiple occurrences | Distinct IDs/modules/results; legitimate shared producer recorded in the catalog. |
| Per-occurrence distinct overrides | Every occurrence resolves its own value and yields the expected distinct verdict; no collapse is observationally hidden. |
| Anonymous admitted + anonymous excluded | Both dispositions visible; no spurious actual demand. |
| Anonymous admitted with actual × snapshot | Public live and relocated replay both lower the actual without a nullable-QN crash or identity drift. |
| Shared calc/constraint demand across files | One intended producer retained; the exact parameter group survives deterministically with no overwrite. |
| Recursive containment | Named cycle error with full owner path; no partial instance index. |
| Non-finite multiplicity | Named cardinality error; no partial occurrence expansion. |
| Producer-channel actual | Producer retained through constraint root before pruning. |
| Literal design-attribute actual (D-2) | Direct resolution under real QN with a usage-owned attribute on a concrete `PartUsage` and a self-named actual; no passthrough required. |
| Modeled-default formal | Default applies and an override changes verdict. |
| Ambiguous/defaulted producer resolution | A model with two same-leaf candidate design attributes and a defaulted-fallback shape fails generation with a named ambiguity/producer error, or resolves only under exact QN; no verdict is ever produced from a guessed or defaulted binding while V11 is clean. |
| Signed/unit default + unsupported wrapper | Explicit `-0.1` and `[MW]` defaults survive; an unsupported wrapper never invents a value. |
| Definition-owned assert through redefining usage | Definition source and redefining occurrence/actual identity remain distinct and produce the expected verdict. |
| Pre-existing V11 + unrelated constraint | Extension succeeds; final generation remains strict. |
| Potential extension-introduced V11 (Item 3B) | Constructed case proves the shape exists and fails by introduced identity, or proves it impossible and removes extension-time coverage validation. |
| Relocated snapshot | Same decisions, retained producers, graph/catalog, fingerprints, and full generated tree; no checkout-absolute bytes anywhere. |
| Malformed snapshot sections | Each malformed required shape fails before reconstruction with section/field context and recapture guidance. |
| Reserved/model/generated name collisions | Deterministic pre-output failure and untouched target. |
| Missing catalog with constraint modules | Named pre-output failure; no renderer/writer/orchestration mutation. |
| Catalog/profile/runtime schema skew | Older/newer combinations fail closed in both directions before semantic use. |
| Generation-plan nested mutation | Written semantic contents equal the preflight-validated plan. |
| Out-of-root warning then `BLOCK` | Portable warning renders and does not mask the later halt. |
| Mixed satisfied/violated/indeterminate population | Headline precedence is violation → indeterminate → satisfied → not assessed with every ordinary output retained. |
| Four exceptional-arithmetic shapes | Both evaluators agree on phase/module/cause and complete report content, not merely on one shared failure wrapper, with the expected phase for each shape pinned by the fixture rather than established by mutual agreement. |
| Successful/violated/indeterminate file-backed reports | Verified identity, exact JSON persistence, routing, and harvest with no adapter for every completed status. |
| Trusted verifier bootstrap | A verifier modified to return unconditional success is rejected before any package code runs; verifier-version skew also fails closed. |
| Seal/verify symlink and provenance | Every forbidden link fails symmetrically; adding a foreign file then re-sealing cannot make it codegen-originated. |
| Nested evidence mutation attempt | Mutation of generated report/results/status/margin/observations cannot change authoritative or persisted evidence. |
| Canonical embedded catalog + multi-entry package (D-3) | Stock codegen/TEAx path, no alternate catalog schema, materializer, or wrapper. |
| Resume/query across incompatible fingerprints | Executable or semantic/catalog mismatch rejects resume/query or starts an explicit new lineage; no silent reassignment. |
| Zero-entry and excluded-only entry-channel shapes | Zero/one/multiple typed channel mappings validate completely; excluded-only constraints do not invent inputs. |
| Fact-consumer mutation | Removing or changing each load-bearing fact consumer fails a behavioral test; a static map edit cannot satisfy it. |
| Remediation simplification | Named superseded mechanisms are removed rather than shimmed; no duplicate authority or parallel route remains. Line counts are not proof. |
| Invalid explicit simkit path (test infrastructure) | The codegen test helper fails rather than falling through to sibling discovery. |
| IFE grid | Exact final candidates, stock seams, 2,301 points, modeled `>=`, unchanged anchors. |
| Stellarator design point (D-1/D-2) | Fully representable graph with WI-027 D7 passthroughs removed, no post-build mutation/private bridge, five verdicts, unchanged numerics, handwritten code sealed. |

## Appendix D: Provenance and primary evidence

### Original shaping intent

- `.project/concepts/constraint-execution-and-design-space-studies.md`
- `.project/concepts/constraint-execution-and-design-space-studies-claude.md`

### Agent-authored and owner-ratified decisions

- `.project/active/numerical-constraint-profile/spec.md`
- `../agentic-mbse/.project/active/constraint-wave-profile-semantics/spec.md`

### Architecture and implementation

- `../agentic-mbse/docs/constraint-facts-and-expression-ir.md`
- `../agentic-mbse/src/agentic_mbse/sysml/executable_profile.py`
- `.project/completed/20260713_constraint-lowering/{spec,design,audit}.md`
- `.project/completed/20260713_constraint-generation/{spec,design,audit}.md`
- `docs/architecture/reference/27-snapshot-generation.md`
- `docs/architecture/reference/28-constraint-lowering-and-catalog.md`
- `docs/architecture/reference/29-contracts-and-sealing.md`
- `src/sysml_codegen/analysis/constraint_lowering.py`
- `src/sysml_codegen/generation/constraint_plan.py`
- `src/sysml_codegen/cli/__init__.py`

### Corrections and consumer proof

- `.project/research/20260719-125806_constraint-execution-lifecycle-contract-adversarial-review.md`
- `.project/research/20260718-192048_constraint-exec-pr-wave-code-review.md`
- `.project/research/20260719-065712_constraint-profile-semantics-and-license-reconciliation.md`
- `.project/research/20260719-103419_gate-b-independent-assessment.md`
- `../fusion-tea-stellarator-mbse-demo/.project/research/20260719-082509_gate-b-root-cause-constraint-lowering-vs-v11-bridge.md`
- `/home/reid/1cfe/fusion-tea/exploration/ife_e2e/study/findings.md`
- `../fusion-tea-stellarator-mbse-demo/work/active/WI-027_demo-constraint-execution/{spec,design,plan}.md`
- `../teax/.project/active/gap-close-f1-normalization/audit.md`
- `../teax/.project/completed/20260713_constraint-study-integration-spike/findings.md`

## Appendix E: Ordered remediation register

The owner ratified this order on 2026-07-19. The execution owners below are defined in
`.project/backlog/epic_constraint_execution_lifecycle_remediation.md`.

| Order | Gap | Proposed owner | Exit condition |
|---:|---|---|---|
| 0 | Commit-pinned compatible candidate | Lifecycle Item 0 | Exact codegen/agentic-mbse/TEAx hashes and locks install together; profile/runtime skew tests pass. |
| 1 | Occurrence/demand R-4/R-5/R-7 | Lifecycle Item 1 | Exact anonymous-actual, shared-demand, recursive, finite, and per-occurrence-override cells pass on the live leg; the anonymous cell's relocated leg completes with row 5. |
| 2 | Resolver unification + Gate A | Lifecycle Item 2 | One producer/exact-QN resolver serves calc, aggregation, and constraint consumers; direct literal works; three ladders are deleted. |
| 3 | Gate B capture-time check scope | Lifecycle Item 3 | Constructed case proves or refutes new V11 creation; delete the call if vacuous, otherwise differential-check it; file fusion finding #8. |
| 4 | Diagnostics/defaults | Lifecycle Item 4 | Versioned severity schema/sink and skew gates land; warning order and `-0.1`/`[MW]` defaults pass. |
| 5 | Whole-tree portability | Lifecycle Item 5 | Docstrings, loader paths, anonymous IDs, catalog/contracts, and full generated bytes contain no checkout-absolute path. |
| 6 | Public/version docs | Lifecycle Item 6 | All correction-register claims agree with landed candidates. |
| 7 | F1/environment evidence | Lifecycle Item 6 | Record `d545701`, repair `927a9e1`, compare report contents, and scope the invalid-path helper correctly. |
| 8 | Trusted verifier/bootstrap skew | Lifecycle Item 7 | Runtime-trusted verifier rejects the bypass; verifier/runtime-contract skew fails closed. |
| 9 | Seal provenance | Lifecycle Item 7 | Generation manifest distinguishes codegen/preserved/runtime files; re-seal cannot launder foreign content. |
| 10 | Catalog/CE-F1 + store transition | Lifecycle Item 8 | Five missing fields + admitted usage record land; alternate schema/materializer/fixture/stand-in are deleted; old stores migrate by proof or remain archived. |
| 11 | Multi-entry CE-F2 | Lifecycle Item 9 | Stock bridge supplies zero/one/multiple complete typed channel mappings. |
| 12 | Producer completeness + stellarator rollup | Lifecycle Item 10 | Exact intended producers are proven independently of V11 through the ambiguous/defaulted acceptance cell; WI-027 D7 is amended/removed; public generation succeeds with no bridge/mutation. |
| 13 | Constraint-free TEAx | Lifecycle Item 11 | Constraint-free package loads/evaluates with empty constraint evidence. |
| 14 | Evidence mutation protection | Lifecycle Item 11 | Freeze/isolate nested report/results; policy/store mutation tests pass. |
| 15 | File-backed report machinery | Lifecycle Item 11 | Register, persist exact completed reports for all statuses, bind package identity, and harvest without adapter. |
| 16 | Grandfather/tracking-key lifecycle | Lifecycle Item 12 | Normal path fails closed on skip-lowering; tracking key is implemented/cataloged or removed with correlation claims corrected. |
| 17 | Composed proof | Lifecycle Item 13 | One pinned artifact thread passes public live/relocated generation, seal/load/evaluate/persist/query, IFE, and stellarator, and every mandatory matrix cell is certified at the pinned revision set. |

No later row may certify around an earlier open dependency. The evidence-coordinate record enforces
this by binding each status to the same committed revision/artifact thread and naming every open
predecessor. F1 is evidence/release/environment reconciliation, not reimplementation.
