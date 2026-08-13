# Constraint Execution: Authoritative Lifecycle Contract

**Status:** Ratified normative authority — 2026-07-19. Remediation complete: the composed public
proof passed 41/41 and the pinned candidate merged 2026-07-20 (see "Implementation candidate
status"). Source-identity amendment state: see "Current conclusion" (sole authority-state home).
**Owner:** Reid W
**Ratified:** 2026-07-19 — [OWNER-VERBATIM] “Ratified.”
**Created:** 2026-07-19
**Scope:** authoring validation, code generation, package integrity, evaluation, and studies
**Requirements:** `.project/concepts/constraint-execution-lifecycle-requirements.md`
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

Reconciled 2026-08-05 (SOURCE-IDENTITY Item 3, checkpoint item 7). The 2026-07-19 statement that
no commit-pinned, mutually installable candidate existed is historical: the lifecycle remediation
epic pinned a candidate, passed the composed public-path proof 41/41 at the pinned set
(`.project/completed/20260720_constraint-lifecycle-composed-proof/release-readiness.md` — the
release record alone still says merge pending), and merged on 2026-07-20 in the test-enforced
order: agentic-mbse `f4ebdce`, sysml-codegen `936315c`, TEAx `fa0e06a`. The merged state and
post-merge smoke are recorded in `.project/completed/CHANGELOG.md:74-100`.

This reconciliation certifies nothing beyond that record. Source-identity amendment authority and
certification state are stated only in "Current conclusion" below; Items 4–8's work is tracked in
`.project/backlog/epic_semantic_source_identity.md`.

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

1. (amended 2026-08-12, CONSTRAINT-SEMANTICS Item 1) Every usage gets one profile disposition. A
   `BLOCK` on an **asserted** usage halts the model. A non-asserted usage never halts generation:
   the form gate runs before the predicate walk, so an unsupported predicate written inside a plain
   `constraint` is never reached and the usage catalogs as unassessed. Descriptive constraints are
   never load-bearing. After generation, every other usage has executable concrete representation or
   a visible exclusion. After evaluation, every module yields evidence or a named execution failure.
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
9. (amended 2026-08-12, CONSTRAINT-SEMANTICS Item 1) `ADMIT` places canonical IR inside the
   compiler's semantic envelope. Downstream may not reclassify it, but named contextual lowering,
   graph, input, and runtime failures remain. One of those named contextual failures halts
   generation: an asserted usage whose form is in executable scope but which has no attachment
   capability — structurally unattachable — fails loudly, naming the usage and the missing
   attachment. It is a contextual failure of the kind this invariant already admits; invariant 8's
   four outcomes are unchanged and `ADMIT` is not reclassified.
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
19. (amended 2026-08-05, SOURCE-IDENTITY Item 3) Calculation inputs, constraint actuals, and
    aggregation terms use one shared positive-resolution procedure: first a real producer channel,
    then a real design attribute — keyed by the consumed value's semantic source identity
    (invariants 54–56), never by name coincidence. An omitted constraint formal accepts a modeled
    default only when the model declares it.
20. (amended 2026-08-09, ELABORATE-FIRST Item 5) Resolution never invents a value, parses display
    text, selects a same-named candidate, or mints a consumer-local input for a bound model
    reference. A genuinely nonexistent authored feature is rejected during language loading
    (Appendix C, C18); codegen does not repeat language name resolution. A loaded supported
    reference that cannot be projected fails with a named diagnostic. Positive resolution may not
    fork into consumer-specific ladders.
21. A direct literal-valued design attribute is a valid design-attribute actual. It must be available
    during graph construction and must reuse the same QN-keyed typed entry point as any calculation
    consumer. Requiring a passthrough calculation is a workaround, not conformance.
22. (amended 2026-08-05, SOURCE-IDENTITY Item 3) Modeled defaults remain overridable typed
    parameters and never become study variables automatically. An independently authored literal
    remains an independent source even when names or values are equal (D-11). An unbound
    calculation-definition input default is one independently overridable `LIBRARY_DEFAULT` source
    per concrete calculation usage; sharing requires an explicit modeled relationship (D-12).
23. Constraint input channels join dependency roots before live pruning. Supported snapshot replay
    retains the equivalent producers through its full-graph rebuild.
24. Constraint extension does not reject unrelated pre-existing uncovered inputs. Item 3B must
    first construct a case that proves or refutes whether extension can introduce a new V11
    uncovered input. If it can, extension rejects only the introduced violation. If it cannot,
    extension performs channel validation only and final generation alone owns V11 coverage.
25. Whole-graph channel-reference validation still runs after extension.
26. (amended 2026-08-05, SOURCE-IDENTITY Item 3) Final generation requires zero whole-graph V11
    uncovered inputs. A separate producer-completeness check proves that every model-derived
    consumed value resolves to one intended producer under its exact semantic source identity
    (declaration plus concrete occurrence, invariant 55), while legitimate external design inputs
    remain ordinary typed entry channels. V11 is not a substitute: a defaulted fallback or
    ambiguous first-match binding can pass it. No late-fill, leaf-name guess, owner/name
    reconstruction, ambiguous first-pick, or post-build graph/default mutation seam is supported.
27. Eligible execution IDs use source-local identity, concrete occurrence, membership, and
    polarity. Excluded IDs use stable source/context identity because occurrence or polarity may
    not exist. The executable fingerprint scopes IDs but is not an ID input. Cross-version
    correlation is supported only through an explicit author key that is populated and cataloged;
    otherwise the system makes no correlation claim.

### Catalog, generation, and package

28. (amended 2026-08-12, CONSTRAINT-SEMANTICS Item 1) The canonical catalog exposes definition
    inventory, one visible disposition per usage, and one concrete execution entry per admitted
    occurrence. A visible disposition is one of three kinds — eligible, excluded-with-reason, or
    non-reaching-with-reason — and every authored usage carries exactly one, so the dispositions
    cover the complete authored-usage domain: "reaches no instance" is a disposition, not an
    absence. It carries source form, usage name and QN,
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
32. (amended 2026-08-12, CONSTRAINT-SEMANTICS Item 1) The report aggregator has one required
    exact-schema input per eligible concrete assertion. Missing or extra evidence fails, and the
    aggregator is structurally retained as an exit ancestor whenever a constraint report is required.
    A constraint-bearing model with no applicable asserted gate still requires the zero-input
    aggregator and a report whose headline is the not-assessed state ("Headline states and coverage
    truth"); a model with no constraint usages remains inert and has no aggregator.
33. (amended 2026-08-12, CONSTRAINT-SEMANTICS Item 1) Headline precedence is violation, then
    indeterminate, then full satisfaction, then partial coverage, then not assessed. Full
    satisfaction means every applicable asserted gate was assessed and passed — a coverage claim, not
    the absence of a failure. The states, the term "applicable asserted gate", and the
    inventory-versus-feasibility split are defined under "Headline states and coverage truth".
    Decision record: ADR-009.
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
46. (amended 2026-08-12, CONSTRAINT-SEMANTICS Item 1) The public file-backed route persists and
    harvests the exact report plus package identity with no consumer schema adapter. The exact
    report carries compact coverage accounting derived from the catalog (invariant 48), and
    persistence and harvest carry it through unchanged.
46a. (amended 2026-08-12, CONSTRAINT-SEMANTICS Item 1) A constraint-free package is valid input to
    TEAx. Absence of the constraint report produces empty constraint evidence rather than a
    `KeyError`; codegen remains free to omit constraint-only catalog/modules for byte-stable
    constraint-free generation. The same fail-closed obligation extends to headline values: an
    unknown or unmapped headline fails closed with a named error, never a `KeyError` and never a
    fallthrough to a satisfied or unconstrained reading.
47. The study bridge supplies every typed entry channel. A candidate changes selected fields in a
    complete typed baseline; it does not omit unrelated channels.
48. (amended 2026-08-12, CONSTRAINT-SEMANTICS Item 1) Codegen's catalog embedded in the model
    contract is the sole catalog schema authority and the sole authority for coverage truth: the
    report's coverage accounting is derived from it in one direction and is never an independently
    maintained second inventory. TEAx consumes its source form, usage identity, owner QN, definition QN, explicit join, and occurrence
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

### Source identity

Added by SOURCE-IDENTITY Item 3 (`.project/backlog/epic_semantic_source_identity.md`). The
definitions, referent table, invariants 54–60, and obligations here serve the source-identity
dispositions (D-4 onward) and Appendix C's "Source-identity scenarios" subsection.

- **Semantic referent.** The element KerML name resolution selects for a written binding
  expression, as SysIDE exposes it. The referent depends on the written form and the binding-owner
  context together; neither alone determines it.
- **Binding-owner context.** The authoring location of the calculation that owns the binding:
  inside a definition body (def context) or inside a concrete part usage (usage context). Context
  is key material: the same written spelling resolves to a def-level feature in def context and to
  an occurrence-level feature in usage context (referent table below).
- **Declaration identity.** The declared feature that anchors a source: its owner kind and
  declaration site.
- **Concrete occurrence.** The concrete featuring context in which a referent applies — which real
  occurrence of the declared feature the consumer observes.
- **Semantic source occurrence.** Declaration identity plus concrete occurrence identity: the unit
  that owns one runtime source.
- **Runtime source.** The one public input or producer channel that carries a semantic source
  occurrence's value at the executable boundary.
- **Redefinition (`:>>`).** A distinct feature that replaces the redefined feature in its concrete
  context; a definition default applies at each featuring instance unless that occurrence supplies
  an override (SysML v2 Part 1 §7.6, §7.13.4).

**Referent table** (written form × binding-owner context → semantic referent). Verified against
the Item-1 def-context probes (AFT), the deep_cross_scope usage-context snapshot QNs
(`tests/fixtures/deep_cross_scope_probe/extraction_snapshot.json:404,448,478`), and RM 9's
def-context binding (`tests/fixtures/fusion_tea/designs/hif_ife/hif_driver.sysml:6,76,118`).

| Form | Authored inside the definition | Authored inside a concrete usage |
|---|---|---|
| bare self-named | own formal (context-invariant — nearest scope is the calculation's own parameter) | own formal (context-invariant) |
| bare renamed | def-level feature (AFT 1c) | occurrence-level feature (DCS:71,83) |
| owner-qualified | def-level feature — definition qualifier (AFT 2) | occurrence-level feature — usage qualifier (DCS:92) |
| feature chain | occurrence-level: the redefining feature at the named occurrence (AFT 3) | same, rooted at the named nested occurrence (NOP:22,25) |
| `#(i)` / `[i]` | value expression / unresolvable (context-invariant) | same |

**[AGENT] (ratified by owner, 2026-08-09) Deep-cross-scope evidence boundary.** The DCS:71,83
and DCS:92 citations prove the semantic referents of those individual supported bindings. Public
runtime acceptance for C4 and C5 comes from their focused matrix fixtures. DCS:82 is also a
supported producer-output reference: with explicit `:>>` redefinitions on `array` and `sensor`,
the valid witness has one concrete `sensor.core` producer and exact projection wires the consumer
to its `metric_value` output. The former plain same-name part declarations were an invalid SysML
namespace shape, not three legitimate producer occurrences; the exact route rejects that shape as
`SYSML_NAMESPACE_NOT_DISTINGUISHABLE` before occurrence expansion. No name or authored qualifier
selects the supported edge.

Abbreviations used by all source-identity material: AFT n = Item-1 authoring-form-table form n
(`.project/active/source-identity-binding-semantics-spike/authoring-form-table.md`); RM n = Item-2
route-matrix row n (`.project/active/source-identity-route-evidence-spike/route-matrix.md`); DCS =
`tests/fixtures/deep_cross_scope_probe/design.sysml`; NOP =
`tests/fixtures/nested_occurrence_override_probe/model.sysml`; HIF =
`tests/fixtures/fusion_tea/designs/hif_ife/`.

The invariant family continues the contract's numbering; invariants 1–53 are unrenumbered.

54. Referent fidelity: every supported model-derived consumed value binds at the semantic referent
    KerML name resolution supplies, fixed by the written form and binding-owner context together
    (referent table). The toolchain may support or reject a written form; it never treats a
    binding as denoting a different element than its referent — a self-binding, in particular, is
    never read as an outer reference (D-4), and no supported form is reinterpreted as another
    (D-5..D-7).
55. Semantic source identity: every supported model-derived consumed value carries one
    extraction-owned semantic source identity containing both declaration identity and concrete
    occurrence identity. Reconstruction from owner/name fields is not an accepted authority. When
    no unique concrete occurrence exists in the consumer's context, the outcome is a named
    ambiguity diagnostic, never a guess (cells C9/C10).
56. One occurrence, one runtime source: one semantic source occurrence produces one runtime
    source, and every and only its calculation, constraint, and aggregation consumers resolve to
    that source. Convergence is per source occurrence, across every supported written form its
    bindings use (RM 12 is the concrete case). Consumer parameter names, count, placement, and
    strictness never create source identity. Distinct concrete occurrences remain distinct
    sources even under equal inherited defaults (D-13).
57. Public mutation acceptance: source-identity acceptance is established at the public boundary
    by off-default mutation — changing one source changes every intended consumer and no
    independent source. Fixed-point value equality and entry-key counts are insufficient
    evidence.
58. Route identity parity: live extraction, in-place snapshot replay, and relocated snapshot
    replay transport and resolve the same semantic source identity. Identity evidence is
    versioned; an older snapshot format without it fails closed.
59. Diagnostic boundary: unsupported and deferred forms fail at authoring validation with
    blocking diagnostics — the self-binding diagnostic is not suppressed by any same-named outer
    attribute or sibling output, and the indexed/expression readiness diagnostics state that the
    expression is valid SysML, unsupported by this executable subset, never "invalid SysML".
    Codegen enforces the same conditions unconditionally and independently of whether authoring
    validation ran; validation diagnostics are author feedback, never mutable semantic decisions
    passed into codegen.
60. One identity authority: exactly one authority decides semantic identity and exactly one
    occurrence-to-definition bridge exists. VBR rescue/stamping, supplied-value synthesis,
    backtracking fallback, aggregation fallback, and parameter-group value repair either derive
    from that authority as non-semantic value adapters or are deleted (D-16..D-18).

**Validation and guidance obligations (owners assigned by the epic):**

- L2 self-binding correction (→ Item 4): the `agentic-mbse` validation stack reports a blocking,
  actionable diagnostic when a consumed calculation input's value expression resolves to that
  same input parameter; the current rescue-aware exemption
  (`../agentic-mbse/src/agentic_mbse/validation/level2_structure.py:309-355`) and its
  wrong-oracle tests are corrected. Indexed value expressions used where the supported executable
  path requires source feature identity get the distinct codegen-readiness diagnostic of
  invariant 59 (→ Item 4). Owner request, 2026-08-05:
  **[OWNER-VERBATIM]** “agree with classifying that as unsupported. Can we add that (and probably the `in.R=R`) pattern in the agentic-mbse validation stack?”
  — here `in.R=R` denotes the discussed `in R = R` self-binding form.
- Modeling guidance (→ Item 8): `agentic-mbse` documentation defines the allowable
  calculation-binding patterns as a modeling question — what each accepted and rejected form
  means in KerML/SysML and how SysIDE exposes it. Owner request, 2026-08-05:
  **[OWNER-VERBATIM]** “we MUST document allowable patterns in our `agentic-mbse` docs as well. This is a "how do you model correctly" quesiton, not a "what should sysml-codegen do" question...”
  Required content: positive nested-definition and named-occurrence examples, the
  source-self-binding counterexample, the indexed-value-expression limitation, and the
  definition/redefinition relationship. Examples are labeled by force — an example illustrates
  the kind; a referent is the bar to match — and no single valid topology is presented as the
  universal required model shape.
- Snapshot/identity blast radius (→ Items 4/6): the new identity evidence requires a snapshot
  format-version bump with fail-closed older versions, coordinated capture/rebuild changes,
  recapture of the 37-fixture snapshot corpus, and companion-repo regeneration (Item-2 route
  findings; scope neither softened nor restated).

### Headline states and coverage truth

Added 2026-08-12 (CONSTRAINT-SEMANTICS Item 1). The decision record is ADR-009
(`docs/architecture/modeling-assumptions.md` §9). Invariants 32, 33, 46a, and 48 point here for the
meanings they use. This subsection fixes what each state *means* and when it may be claimed; the
concrete report and runtime token spellings, the report schema, and the normalization-seam code are
CONSTRAINT-SEMANTICS Item 3's.

**Applicable asserted gate.** A usage is an applicable asserted gate when its source form is in the
assert family and that form is in executable scope. **The test is on the form, not on the
predicate:** an asserted usage whose predicate the profile `BLOCK`s or classifies `NON_NUMERICAL` is
still an applicable asserted gate, and it stays in the feasibility denominator as an unassessed one.
A vacuous gate — one whose owner has zero occurrences — is still applicable. A usage stops being
applicable only when it carries an explicit inapplicability disposition. Plain and requirement-side
usages are never applicable asserted gates.

**Two totals, kept apart.** *Inventory totality* counts every authored usage of every form.
*Feasibility coverage* counts applicable asserted gates only. Descriptive and requirement-side usages
appear in inventory and never in the feasibility denominator.

**The six states.**

1. **Violation** — at least one applicable asserted gate was assessed and failed.
2. **Indeterminate** — no violation, and at least one assessed gate produced Kleene unknown.
3. **Full satisfaction** — every applicable asserted gate was assessed and passed. This is a
   coverage claim, not the absence of a failure.
4. **Partial coverage** — at least one applicable asserted gate exists and went unassessed,
   including an asserted vacuous gate carrying no explicit inapplicability disposition.
5. **Not assessed** — the model has constraint usages but no applicable asserted gate at all. A
   deliberately descriptive model reads here, never partial.
6. **Unconstrained (report absent)** — the model authors no constraint usage, so no report is
   generated and the runtime's unconstrained disposition is true by construction.

**Precedence:** violation → indeterminate → full satisfaction → partial coverage → not assessed.

**Both vocabularies.** Two headline vocabularies exist — the generated report's and TEAx's canonical
runtime one — bridged by a normalization seam. Every state above has a meaning in both and a
counterpart across the seam. A state defined on one side with no counterpart on the other is a
defect, and an unmapped value fails closed (invariant 46a) rather than falling through to a satisfied
or unconstrained reading.

Invariant 61 below was minted by CONSTRAINT-SEMANTICS Item 1 on 2026-08-12; invariant 60 was the
highest live number before it. Its companion mirror is LC-E13 (companion requirements) and its
acceptance cell is Appendix C's "Asserted vacuous gate".

61. (added 2026-08-12, CONSTRAINT-SEMANTICS Item 1) An asserted usage whose owner has zero
    occurrences — a vacuous gate — is visible at warning grade. The catalog carries a
    non-reaching-with-reason disposition (invariant 28) and authoring validation emits an advisory
    naming the usage and its detached owner. A vacuous gate counts as missing assessment for
    feasibility coverage until it carries an explicit inapplicability disposition; carrying one makes
    it inapplicable and removes it from the denominator. It is neither a halt nor a silent pass.

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

### Equality intent and authoring policy

Added 2026-08-12 (CONSTRAINT-SEMANTICS Item 1). This is the authority copy; agentic-mbse's authoring
guidance renders the same instruction in full where its readers are and cites this section as the
authority. The rendering is not a second authority — if the two disagree, the contract governs, and
an edit here obligates a matching edit there. (Corrected 2026-08-12, Item 1 audit H-1: the first
published sentence said the guidance "cites it and does not restate it", which misdescribed the
rendering the design review required.)

**[NEED]** (owner-stated, 2026-08-12) Narrow bands of viability make design exploration really
difficult, so the guidance must say *when* an equality should be used at all — not only how the
pipeline treats one. **[NEED]** (owner-stated, 2026-08-12) Tolerance values are modeled values the
modeler chooses. The pipeline never invents one.

**[AGENT] (ratified by owner, 2026-08-12)** The intent behind a written `a == b` falls into four
classes, and each has a different correct authoring move. This taxonomy is agent-originated and
owner-reviewed; challenge it by re-deriving against the reasoning recorded here.

1. **Structural identity** — `b` is `a` by construction. Derive it; do not constrain it. A constraint
   here adds a gate that can only ever pass or reveal a modeling error.
2. **Cross-check of independently computed values** — two paths compute the same physical quantity.
   Use a loose, physically motivated validity band, sized to the disagreement you would actually
   accept, not to floating-point noise.
3. **Feasibility gate** — you want the design to satisfy a limit. Prefer a one-sided inequality. If a
   quantity genuinely must equal a value, fix it as an input rather than search for it and then
   constrain it; searching a zero-measure set is why exploration collapses.
4. **Composition closure** — terms must sum to a whole. Derive the last term by construction; where
   that is not possible, use a banded validity check as in class 2.

Behavioral consequence, already stated elsewhere and repeated here only as a pointer: invariant 11
governs which equality forms execute, and the profile's real-equality block list is documented in
`docs/architecture/modeling-assumptions.md` §8.

### Source-identity dispositions (D-4 onward)

Added by SOURCE-IDENTITY Item 3. Definitions, the referent table, and invariants 54–60 live in
the "Source identity" subsection; acceptance cells live in Appendix C's "Source-identity
scenarios" subsection. Evidence exhibits are frozen: Item-1
(`.project/active/source-identity-binding-semantics-spike/`) and Item-2
(`.project/active/source-identity-route-evidence-spike/`, including its adjacent-work register).

**Resolved decision checkpoint — 2026-08-05.** Eight agent recommendations were presented
individually with their tradeoffs; the owner replied:
**[OWNER-VERBATIM]** “ok agreed with each one”.
Every ratified recommendation below remains `[AGENT] (ratified by owner, 2026-08-05)`;
ratification does not upgrade provenance. The eight: (1) decisions and the acceptance matrix stay
in this contract; (2) the companion requirements copy-and-freeze to
`.project/concepts/constraint-execution-lifecycle-requirements.md` with the archived companion
untouched; (3) one independently overridable `LIBRARY_DEFAULT` source per concrete calculation
usage (D-12); (4) expression-binding sources deferred with a fail-closed readiness diagnostic
(D-15); (5) Item 4 owns fixtures for every published `BLOCKED` target key and chooses no
semantics; (6) the aggregation finding is absorbed into this contract (D-14); (7)
contract/companion status reconciled against the 41/41 release record and the merged-state
changelog; (8) the customer migration is bare-renamed in place. The checkpoint's agent-authored
C4 placement assumed all customer bindings were usage-authored. The audit disproved that premise;
the exact mixed-context target is now C25, with C2 owning the def-only thermal-efficiency shape.
This evidence correction does not change the ratified bare-renamed-form recommendation.

Each row states: ruling · provenance · evidence · migration consequence.

**Authored written forms**

- **D-4 [OWNER-VERBATIM], decided 2026-08-05:** “Never reinterpret a self-binding as an outer
  reference.” The bare self-named form (`in R = R`) is UNSUPPORTED as a source-bearing calculation
  binding: its referent is the calculation's own formal (context-invariant), the binding is legal
  and inert, and no enclosing feature is implied. Target behavior is a blocking authoring
  diagnostic with independently fail-closed codegen (family SRC-01). Evidence: AFT 1 with the
  clause-cited KerML ruling (normatively required self-binding); RM 1–4, 7, 10, 12. Migration:
  ~124 external + 91 fixture occurrences rewritten under the Item-6 ledger; the replacement form
  follows D-5/D-6/D-7 referent semantics for the model's intended topology.
- **D-5 [AGENT] (ratified by owner, 2026-08-05):** bare renamed references are SUPPORTED at the
  referent SysIDE supplies — def-level feature in def context (AFT 1c), occurrence-level feature
  in usage context (DCS:71,83). Neither reading is reinterpreted as the other. Evidence: referent
  table; RM 9, RM 12. Migration: the customer migration uses this form in place (checkpoint item
  8; exact mixed-context acceptance in C25 and def-only acceptance in C2).
- **D-6 [AGENT] (ratified by owner, 2026-08-05):** owner-qualified references are SUPPORTED at
  their resolved referent — definition qualifier → def-level feature (AFT 2); usage qualifier →
  occurrence-level feature (DCS:92). A def-level referent consumed at a concrete occurrence
  resolves through the occurrence bridge; no unique occurrence in context is an ambiguity
  diagnostic, never a guess (cells C9/C12). Evidence: referent table. Migration: none externally —
  the form exists only in the in-repo fixture corpus (85 bindings).
- **D-7 [AGENT] (ratified by owner, 2026-08-05):** occurrence-rooted feature chains are SUPPORTED;
  the referent is the redefining feature at the named occurrence (AFT 3; NOP:22,25). Evidence:
  referent table. Migration: none — the form resolves occurrence-relative today.
- **D-8 [AGENT] (ratified by owner, 2026-08-05):** `#(i)` indexed value expressions are
  UNSUPPORTED as source-bearing calculation bindings in this epic. The expression is legal SysML
  carrying value semantics only — no occurrence feature identity — and is never flattened to its
  leaf name or represented as a direct source reference; the index segment is never silently
  dropped (D-19). Target behavior is a distinct codegen-readiness diagnostic (family SRC-02).
  Evidence: AFT 4a; zero corpus prevalence. Migration: zero-cost; no authored instance exists.
- **D-9 [INHERITED: KerML 1.0 §8.2.5.8.2], recorded 2026-08-05:** `[i]` bracketed expressions are
  LANGUAGE_REJECTED: the square bracket is the quantity/unit operator, not indexing; the model
  fails to load and normal language diagnostics govern (family SRC-03). Evidence: AFT 4b (four
  load errors observed). Migration: zero-cost; zero corpus prevalence.

**Source classes**

- **D-10 [INHERITED: epic mission invariant (owner); invariants 19/20/26]:** a supported modeled
  source has one of two runtime-source topologies: an externally supplied design attribute has one
  public input, while a computed value has one producer channel. Appendix C states the exact
  topology per cell, including computed mixed-consumer C24 and aggregation's producer-backed C17 /
  literal-backed C26 split. Behavioral wording lives in invariants 54–56. Evidence: census
  converged class (123 EPs) for the expected public-input topology; the mission invariant and
  producer-channel controls for C24; RM 5/6 convergence controls; and the committed solar graph's
  C17 producer channel. Migration: Items 4–6
  implement and prove; no model migration.
- **D-11 [INHERITED: invariant 22 (amended); Item-2 discriminator evidence]:** authored-literal
  independence — behavioral wording in invariant 22; the extraction discriminator
  (`written_reference is None` ⇔ authored) and cell C16 carry the acceptance. Evidence: RM 8.
  Migration: none.
- **D-12 [AGENT] (ratified by owner, 2026-08-05):** per-usage `LIBRARY_DEFAULT` for unbound
  calculation-definition input defaults — behavioral wording in invariant 22 (amended);
  acceptance in cell C23. Evidence: RM 11; ADR-001; census library-default class (58 EPs).
  Migration: none — matches ADR-001 behavior; sharing intent must be modeled.
- **D-13 [AGENT] (ratified by owner, 2026-08-05):** per-occurrence distinctness of
  multi-occurrence definition defaults — behavioral wording in invariant 56; acceptance in cells
  C7/C8. Evidence: RM 10; census multi-occurrence sharing note. Migration: catf_mfe's 13×
  `inner_radius` intent is resolved by the final census → Item 6.
- **D-14 [AGENT] (ratified by owner, 2026-08-05; amended and ratified 2026-08-09):** aggregation
  term references belong to this same identity contract — no separate terminal-mint or identity
  rule for aggregation consumers. Valid positive resolutions are covered by C17/C26. A genuinely
  absent authored target is rejected during language loading under C18. Evidence: the committed
  solar graph directly shows C17's producer-backed target;
  RM 13 and its parity evidence expose C26's broken literal-valued positive resolutions
  (`tests/fixtures/solar_battery_model/library.sysml:569-578,697-721`). RM 13's frozen
  `permitting.*` summary is overbroad and is not evidence for C17. See adjacent-work register row 4.
  Migration: the queued fusion-tea aggregation finding files into this epic.
- **D-15 [AGENT] (ratified by owner, 2026-08-05):** expression bindings as sources are
  `DEFERRED(owner, 2026-08-05)` in this epic. Where execution requires source feature identity,
  the boundary fails closed with a distinct codegen-readiness diagnostic; no flattening; no
  invented source (cell C22). Evidence: census expression class (7 EPs);
  `expression_binding_probe`, `plant_value_shapes` fixtures. Migration: the deferral is terminal
  for this epic; later support reopens this contract explicitly.

**Impermissible mechanisms**

- **D-16 [INHERITED: invariants 19/20/26]:** the VBR reference→literal stamp
  (`src/sysml_codegen/orchestration/pipeline_builder.py:363-369`) and the self-named binding rescue
  (`_rescue_self_named_bindings`) are impermissible as identity mechanisms — governing wording in
  invariants 54/60; Appendix B records both superseded readings. Evidence: RM 1/2/9/12 stamped
  copies; DCS per-consumer stamps. Migration: Item 5 deletes them or derives any surviving
  value-adapter behavior from the single identity authority (adjacent-work register rows 1, 6).
- **D-17 [INHERITED: invariants 19/20/26]:** the lenient consumer-local mint for bound model
  references is impermissible — governing wording in invariant 20 (amended); Appendix B records
  the superseded REQ-IR-06 reading. Evidence: RM 3/4 Path B; census 75 model-derived per-consumer
  mints. Migration: Item 5.
- **D-18 [INHERITED: ratified simplification constraint; adjacent-work register row 5]:** the
  parameter-group deriver's value backfill (`graph_builder.py:620-630`) is a superseded fourth
  value authority — governing wording in invariant 60; Appendix B records the superseded reading.
  Evidence: Item-2 findings (it masks Path-B identity loss). Migration: Item 5 deletion register.
- **D-19 [AGENT] (ratified by owner, 2026-08-05):** the extractor's silent `#(i)` index drop
  (`_parse_chain_expression` skips non-feature-reference first operands; AFT 4a extractor view) is
  a defect class, not a supported flattening: extraction never emits a leaf-only `source_path` for
  an indexed expression; it surfaces the index or fails closed. Evidence: AFT 4a; adjacent-work
  register row 7. Migration: corrected by the Item-4/5 identity work; the authoring-side outcome
  is D-8's readiness diagnostic.

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

Authority state (one statement; every other appearance cites it):

- The lifecycle architecture was ratified 2026-07-19; its remediation register closed with the
  41/41 composed proof and the 2026-07-20 merge ("Implementation candidate status" above).
- The source-identity additions (the "Source identity" subsection, dispositions D-4 onward, the
  new Appendix B rows, and Appendix C's "Source-identity scenarios") were drafted under
  SOURCE-IDENTITY Item 3 on the resolved 2026-08-05 decision checkpoint, audit-certified on
  2026-08-07, and ratified when the owner declared the audited item finished on 2026-08-07. They
  are the behavioral authority for Items 4–8. Ratification does not certify runtime cells; each
  cell retains the certification state and evidence owner recorded in Appendix C.

Next: execute `.project/backlog/epic_semantic_source_identity.md` Items 4–8, which derive from this
contract chain.

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
| Aggregator always exists even with no usage | Original concept | No usages is inert. A constraint-bearing model whose usages are all non-asserted reads not assessed; an excluded **asserted** usage puts the report at partial coverage. (amended 2026-08-12, CONSTRAINT-SEMANTICS Item 1) |
| Snapshot replay is the live route after extraction | Conversational supersession (no documentary source); historical architecture prose | Replay uses route-specific `include_all`; grandfathered skip-lowering fails closed for certification. |
| A consumed input whose value expression resolves to its own parameter is rescued by binding to a same-named outer feature | L2 rescue-aware exemption (`../agentic-mbse/src/agentic_mbse/validation/level2_structure.py:309-355`); `_rescue_self_named_bindings`; wrong-oracle acceptance tests | D-4 and family SRC-01: the self-binding is legal and inert; the outcome is a blocking diagnostic (invariant 59), and the rescue is an impermissible identity mechanism (D-16). |
| A bound model reference that fails resolution may lenient-mint a per-consumer entry point | REQ-IR-06 reading; Path B behavior; 75 measured model-derived mints | D-17: never a mint for a bound reference; an absent authored target fails language loading under invariant 20 and C18; external inputs enter only through the explicit external-input contract. |
| Stamping an occurrence override literal onto same-named consumer inputs preserves the modeled source | VBR tier 1 (`src/sysml_codegen/orchestration/pipeline_builder.py:363-369`); RM 1/2/9/12 stamped copies | D-16: the reference→literal stamp is impermissible as an identity mechanism; a reference-derived value never becomes `USAGE_LITERAL` (cell C16's discriminator stays authored-only). |
| The parameter-group deriver's default backfill is a benign value repair | `graph_builder.py:620-630`; Item-2 findings | D-18: a superseded fourth value authority that masks Path-B identity loss; it derives from the single identity authority or is deleted (Item 5). |
| Route-specific convergence evidence certifies source convergence generally | REQ-IR-07 / REQ-SVM route-specific evidence readings | Invariants 56/58: convergence is per semantic source occurrence with full route identity parity; route-specific evidence certifies only its own route. |
| Supplied-value synthesis may decide source identity on its own authority | `resolution/supplied_values.py:646-660`; REQ-SVM-01/02/04 readings | Invariant 60: synthesis may remain only as a value adapter derived from the single identity authority (adjacent-work register row 6); as an identity authority it is superseded. |

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
| Excluded-only usages | Portable exclusions with no silent omission; the sealed package evaluates in TEAx with a not-assessed report surface when every excluded usage is non-asserted, and a partial-coverage surface when any excluded usage is asserted. (amended 2026-08-12, CONSTRAINT-SEMANTICS Item 1) |
| Asserted vacuous gate | An asserted usage whose owner has zero occurrences catalogs with a non-reaching-with-reason disposition at warning grade, authoring validation emits the advisory naming the usage and its detached owner, generation does not halt, and the report headline reads partial coverage; the same usage carrying an explicit inapplicability disposition drops out of the feasibility denominator and the headline reads full satisfaction when every remaining gate passed. |
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
| Mixed satisfied/violated/indeterminate population | Headline precedence is violation → indeterminate → full satisfaction → partial coverage → not assessed, with every ordinary output retained. (amended 2026-08-12, CONSTRAINT-SEMANTICS Item 1) |
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

### Source-identity scenarios (SOURCE-IDENTITY Item 3)

The sole acceptance authority for source-identity behavior across calculation, constraint, and
aggregation consumers. Dispositions D-4..D-19 govern each ruling; definitions, the referent table,
invariants 54–60, and the AFT/RM/DCS/NOP/HIF abbreviations live in the "Source identity"
subsection. Derivation provenance — the closed source inventory mapping every source to exactly one
evidence role — is `.project/active/source-identity-contract/design.md` Appendix A; this
subsection publishes the complete result and is the only normative home for the cells.

**Schema.** Every cell carries three orthogonal ruling fields:

- `disposition` — the ruling on the authored form or source class: `SUPPORTED | UNSUPPORTED |
  LANGUAGE_REJECTED | DEFERRED(owner, date)`.
- `outcome` — what the executable boundary must do for the cell's topology: `RUNTIME_SOURCE |
  AUTHORING_DIAGNOSTIC | AMBIGUITY_DIAGNOSTIC | POLICY_DIAGNOSTIC | LOAD_ERROR`.
- `certification` — proof status: `UNPROVEN | CONTRADICTED_AT_HEAD | BLOCKED(<missing evidence> →
  <owning item>) | CERTIFIED`. At Item-3 close no cell is `CERTIFIED`.

**Keys and counting.** A cell is one complete key: (authored form, semantic referent — fixed by
form and binding-owner context per the referent table; an exact per-binding referent/context tuple
when one source is consumed across contexts, source-topology class, consumer-mix class, value
state). Cells exist only where the derivation inventory produces the key; there is no
Cartesian enumeration. A family (SRC-01, SRC-02, SRC-03, C22) is one cell covering all variants of
a form whose outcome ends before a runtime source exists and cannot be changed by topology; its
observed variants are coordinate subrows. Two sources producing one key merge into one cell
carrying all citations. Missing evidence is a `certification` value, never a missing cell.
**29 cells; 35 evidence coordinates** (9 family subrows, C22's kept readiness coordinate, and 25
individual cells). The population is closed: a genuinely new shape reopens this contract
explicitly — derivation, enumeration, and counts change together — and Items 4–6 realize fixtures
and evidence for the published keys without choosing semantics. The 2026-08-07 audit-correction
reopening added C24 for the computed-source producer-channel topology and C25 for the exact
mixed-context customer topology, then split aggregation's producer-backed C17 from literal-backed
C26; 26/32 → 28/34 → 29/35, changed together with the design's derivation table and enumeration.
Where one source's consumers bind it through different written forms or
binding-owner contexts (RM 12; the customer availability pair), each binding observation is cited
at its own form's cell; convergence is per source occurrence, across forms and contexts.

**Route and mutation obligations derive from `outcome` alone** and are not restated per row:

| `outcome` | live route | snapshot/replay | off-default mutation |
|---|---|---|---|
| `RUNTIME_SOURCE` | one public source | full `live = snapshot = relocated` parity | required — owed by every such cell (Item 6) |
| `AUTHORING_DIAGNOSTIC` | blocking diagnostic before generation; codegen independently fail-closed | capture refuses | N/A |
| `AMBIGUITY_DIAGNOSTIC` | named diagnostic before a source exists; never a guess | same diagnostic on any route that reaches resolution; no route yields a source | N/A |
| `POLICY_DIAGNOSTIC` | exact per-policy outcomes stated in the cell; never a mint or a same-named candidate | same disposition on any route that reaches resolution | N/A |
| `LOAD_ERROR` | load fails | N/A — everything downstream ends at load | N/A |

**Coordinate fields.** Every counted row publishes the key fields (referent, declaration,
occurrence, value_state, consumers), the outcome detail (topology, diagnostic, and mutation where
owed), certification with the owed evidence and owning item, and citations. Family-level fields
are stated once at the family row and inherited by its subrows; route obligations derive from the
table above.

**Unsupported and language-rejected forms**

**SRC-01 — bare self-named `in R = R` × any topology (family; D-4)**

- disposition: UNSUPPORTED (D-4)
- referent: own formal — context-invariant; the binding is legal, inert, and supplies no enclosing
  feature
- outcome: AUTHORING_DIAGNOSTIC — blocking authoring diagnostic on the self-binding; a same-named
  outer attribute or sibling output does not suppress it; codegen independently fail-closed
- topology: none — no runtime source exists on any route
- diagnostic: blocking L2 self-binding diagnostic; the current rescue-aware exemption
  (`../agentic-mbse/src/agentic_mbse/validation/level2_structure.py:309-355`) is the correction
  point
- citations: D-4; AFT 1; clause-cited KerML ruling; corpus population ~124 external + 91 fixture
  occurrences; the 75 model-derived mints are the broader affected population

**01a — occurrence `:>>` override × 2 calculations + 1 constraint**

- declaration: PartDef attribute
- occurrence: single concrete usage; binding authored in usage context
- value_state: occurrence `:>>` override literal
- consumers: 2 calculations + 1 constraint
- certification: CONTRADICTED_AT_HEAD — 3 public fields (1 converged DESIGN_ATTRIBUTE + 2 stamped
  USAGE_LITERAL copies); the constraint converges while the calculations fan out
- citations: RM 1 (fusion_tea `gain`, parity-starred)

**01b — occurrence `:>>` override × 2 calculations (customer pair; mixed binding contexts)**

- declaration: PartDef attribute on `part def 'IFE Power Plant'`
  (`tests/fixtures/fusion_tea/designs/generic_ife/ife_plant.sysml:7`)
- occurrence: single concrete usage `hif_plant` (`HIF hif_plant.sysml:8`) with `:>>` overrides
  (`:69` availability, `:100` thermal_efficiency). Binding-owner contexts are **mixed**:
  `availability` has one usage-authored consumer binding (`meier_coe_calc`,
  `HIF hif_plant.sysml:205,215`) and one def-authored consumer binding (`lcoe_calc`,
  `ife_plant.sysml:98,114`); `thermal_efficiency` has two def-authored consumer bindings
  (`lcoe_calc` `:126`, `recirc_calc` `:134,148`)
- value_state: occurrence `:>>` override literal
- consumers: 2 calculations per source occurrence
- certification: CONTRADICTED_AT_HEAD — 2 per-consumer fields per source, no converged sibling
- citations: RM 2 (`thermal_efficiency`, `availability`); paired customer acceptance
  (epic `:147-150`) — the migrated composition realizes C25 for availability's mixed
  usage/definition-authored legs and C2 for thermal_efficiency's two definition-authored legs

**01c — definition default × 2 calculations, one occurrence**

- declaration: PartDef attribute
- occurrence: single concrete occurrence
- value_state: definition default, no override
- consumers: 2 calculations
- certification: CONTRADICTED_AT_HEAD — 2 fields; the def-declared source is never public
- citations: RM 3 (ife_plant `bank_energy`)

**01d — definition default × 1 calculation**

- declaration: PartDef attribute
- occurrence: single concrete occurrence
- value_state: definition default, no override
- consumers: 1 calculation
- certification: CONTRADICTED_AT_HEAD — per-consumer field with the definition default backfilled
  into it
- citations: RM 4 (ife_plant `gain`; `self_named_binding_trap`)

**01e — usage literal × calculation + constraint (control)**

- declaration: PartUsage-owned attribute
- occurrence: single concrete usage
- value_state: authored usage literal
- consumers: 1 calculation + 1 constraint
- certification: CONTRADICTED_AT_HEAD — no diagnostic today; the binding converges silently
  (named convergence control for C11)
- citations: RM 5 (`shared_producer`)

**01f — cross-owner parent attribute × aggregation/constraint + child calculation**

- declaration: parent-part attribute, consumed cross-owner
- occurrence: single concrete parent occurrence; child-part consumer
- value_state: occurrence override literal
- consumers: aggregation/constraint + child-part calculation
- certification: CONTRADICTED_AT_HEAD — 2 fields; consumer-owner + leaf reconstruction names
  nothing
- citations: RM 7 (solar_battery `pack_count`); topology referent for C15

**01g — two occurrences, definition defaults × 1 calculation per occurrence (2 calculations)**

- declaration: PartDef attribute; two concrete occurrences of one definition
- occurrence: two concrete occurrences
- value_state: definition defaults, no overrides
- consumers: 1 calculation per occurrence (2 calculations)
- certification: CONTRADICTED_AT_HEAD — no diagnostic today; per-occurrence fields minted from
  the self-bindings
- citations: RM 10 (ife_plant `chamber_a`/`chamber_b`; fusion_tea driver pair); topology referent
  for C7

**SRC-02 — `#(i)` indexed value expression as source binding (family; D-8)**

- disposition: UNSUPPORTED (D-8)
- referent: value expression — context-invariant; no occurrence feature identity exists for the
  trailing segment to anchor to
- outcome: AUTHORING_DIAGNOSTIC — distinct codegen-readiness diagnostic; the index segment is
  never silently dropped
- topology: none
- diagnostic: readiness diagnostic whose wording states the expression is valid SysML, unsupported
  by this executable subset — never "invalid SysML"
- citations: D-8, D-19; AFT 4a; zero corpus prevalence

**02a — def-context binding, occurrence override × 2 calculations**

- declaration: PartDef attribute
- occurrence: single concrete occurrence; def-context binding
- value_state: occurrence `:>>` override
- consumers: 2 calculations
- certification: CONTRADICTED_AT_HEAD — the extractor silently drops the index segment
  (`source_path='R'`)
- citations: AFT 4a (`form_bracket_hash.sysml`)

**SRC-03 — `[i]` bracketed expression (family; D-9)**

- disposition: LANGUAGE_REJECTED (D-9)
- referent: none — unresolvable; `[...]` is the quantity/unit bracket operator, not indexing
- outcome: LOAD_ERROR — the model fails to load; nothing exists downstream
- topology: none
- diagnostic: language load diagnostics govern; no codegen diagnostic exists or is owed
- citations: D-9; AFT 4b; KerML 1.0 §8.2.5.8.2

**03a — def-context binding, occurrence override × 2 calculations**

- declaration: PartDef attribute
- occurrence: single concrete occurrence; def-context binding
- value_state: occurrence `:>>` override
- consumers: 2 calculations
- certification: UNPROVEN — kept negative cell pinning the load failure (→ Item 6); HEAD already
  behaves correctly
- citations: AFT 4b (`form_bracket_sq.sysml`)

**Supported forms — def context (referent: def-level feature; occurrence bridge required)**

**C1 — bare renamed × def context × single-occurrence `:>>` override × 1 calculation**

- disposition: SUPPORTED (D-5)
- referent: def-level feature (referent table: bare renamed / def context)
- declaration: PartDef attribute; binding authored inside `part def 'HIF Driver'`
  (`HIF hif_driver.sysml:6,76`)
- occurrence: single concrete usage; override on the usage (`hif_driver.sysml:118`); occurrence
  identity via the bridge
- value_state: occurrence `:>>` override
- consumers: 1 calculation
- outcome: RUNTIME_SOURCE — one public source; the occurrence's override value observed
- topology: one public input keyed by the design attribute at its concrete occurrence
- diagnostic: none
- mutation: an off-default change of the source reaches the calculation (→ Item 6)
- certification: CONTRADICTED_AT_HEAD — the referent is literal-stamped per consumer
  (`rep_rate` ← `pulse_rate_ref`)
- citations: RM 9; customer migration target for the def-authored `availability` leg
  (`lcoe_calc`, `ife_plant.sysml:114` — today a 01b self-binding; bare-renamed in place lands on
  this key)

**C2 — bare renamed × def context × single-occurrence `:>>` override × 2 calculations**

- disposition: SUPPORTED (D-5)
- referent: def-level feature
- declaration: PartDef attribute (`'Probe Plant'::R`)
- occurrence: single concrete occurrence with `:>> R = 12.7`; occurrence identity via the bridge
- value_state: occurrence `:>>` override
- consumers: 2 calculations
- outcome: RUNTIME_SOURCE — both consumers converge on the one source
- topology: one public input; two consumer edges
- diagnostic: none
- mutation: one change reaches both calculations (→ Item 6)
- certification: UNPROVEN — pipeline + mutation legs owed (→ Item 6)
- citations: AFT 1c (`form_control_renamed.sysml`); customer migration target for the
  def-authored `thermal_efficiency` legs (`lcoe_calc` `ife_plant.sysml:126`, `recirc_calc`
  `:148` — today 01b self-bindings; bare-renamed in place lands on this key)

**C3 — owner-qualified (definition qualifier) × def context × single-occurrence `:>>` override × 2 calculations**

- disposition: SUPPORTED (D-6)
- referent: def-level feature via definition qualifier
- declaration: PartDef attribute (`'Probe Plant'::R`)
- occurrence: single concrete occurrence; occurrence bridge required
- value_state: occurrence `:>>` override
- consumers: 2 calculations
- outcome: RUNTIME_SOURCE — def referent + occurrence bridge → the one occurrence's value
- topology: one public input at the bridged occurrence
- diagnostic: none
- mutation: one change reaches both calculations (→ Item 6)
- certification: UNPROVEN — pipeline + mutation legs owed (→ Item 6); population: 85
  fixture-corpus qualified bindings (contexts and value states unenumerated)
- citations: AFT 2 (`form_owner_qualified.sysml`)

**Supported forms — usage context (referent: occurrence-level feature)**

**C4 — bare renamed × usage context × single-occurrence `:>>` override × 2 calculations**

- disposition: SUPPORTED (D-5)
- referent: occurrence-level feature (referent table: bare renamed / usage context;
  snapshot-verified referent QNs)
- declaration: PartDef attribute overridden at the concrete usage
- occurrence: single concrete usage; bindings authored inside it
- value_state: occurrence `:>>` override
- consumers: 2 calculations
- outcome: RUNTIME_SOURCE — one public input under occurrence identity
- topology: one public input; both consumers wired to it
- diagnostic: none
- mutation: an off-default change reaches both consumers and nothing else (→ Item 6)
- certification: VERIFIED — DCS:71,83 supplies the parser-resolved referent evidence
  (`extraction_snapshot.json:404,448`); `elab_matrix_c4` supplies generated public topology and
  isolated off-default mutation evidence
- citations: RM 12; DCS:71,83; `tests/conformance/test_elaboration_contract_matrix.py` C4. This
  cell supplies referent evidence for C25 but is not itself the customer coordinate: the customer
  has only one usage-authored availability consumer

**C5 — owner-qualified (usage qualifier) × usage context × single-occurrence `:>>` override × 1 calculation**

- disposition: SUPPORTED (D-6)
- referent: occurrence-level feature via usage qualifier
- declaration: PartDef attribute overridden at the concrete usage
- occurrence: single concrete usage (`DeepCrossScopeDesign::measurement_system::analyzer`)
- value_state: occurrence `:>>` override
- consumers: 1 calculation
- outcome: RUNTIME_SOURCE — one source; the occurrence referent is direct
- topology: one public input at the named occurrence
- diagnostic: none
- mutation: an off-default change reaches the calculation (→ Item 6)
- certification: VERIFIED — DCS:92 supplies the parser-resolved referent evidence (snapshot
  `:478`); `elab_matrix_c5` supplies generated public topology and isolated off-default mutation
  evidence. DCS:82 separately proves a supported deep producer-output reference on the repaired
  valid DCS witness; it is not C5 acceptance evidence.
- citations: RM 12; DCS:92; `tests/conformance/test_elaboration_contract_matrix.py` C5

**C6 — feature chain (sibling context, occurrence-rooted) × single-occurrence `:>>` override × 2 calculations**

- disposition: SUPPORTED (D-7)
- referent: occurrence-level — the redefining feature at the named occurrence
- declaration: PartDef attribute redefined at the usage (`'Design Ctx'::plant::R`)
- occurrence: single named occurrence (`plant`)
- value_state: occurrence `:>>` override
- consumers: 2 calculations
- outcome: RUNTIME_SOURCE — one source at the redefining feature
- topology: one public input at the redefining feature
- diagnostic: none
- mutation: one change reaches both calculations (→ Item 6)
- certification: UNPROVEN — mutation leg owed (→ Item 6)
- citations: AFT 3 (`form_chain.sysml`)

**Multi-occurrence (D-13)**

**C7 — chain per occurrence × two occurrences, equal defaults × 1 calculation per occurrence**

- disposition: SUPPORTED (D-7, D-13)
- referent: occurrence-level feature, one per named occurrence
- declaration: PartDef attribute, one definition
- occurrence: two concrete occurrences, one consumer chain per occurrence
- value_state: equal inherited definition defaults, no overrides
- consumers: 1 calculation per occurrence (2 calculations)
- outcome: RUNTIME_SOURCE — distinct sources per occurrence; equal values never collapse
  identity; mutating one leaves the others
- topology: one public input per occurrence
- diagnostic: none
- mutation: mutating one occurrence's source changes only that occurrence's consumers (→ Item 6)
- certification: UNPROVEN — per-occurrence mutation legs owed (→ Item 6); catf_mfe's 13×
  `inner_radius` intent resolved by the final census (→ Item 6)
- citations: D-13; RM 10 (topology referent); census multi-occurrence sharing note

**C8 — chain per occurrence × two occurrences, distinct overrides × 1 calculation per occurrence**

- disposition: SUPPORTED (D-7, D-13)
- referent: occurrence-level feature, one per named occurrence
- declaration: PartDef attribute, one definition
- occurrence: two concrete occurrences
- value_state: distinct occurrence `:>>` overrides
- consumers: 1 calculation per occurrence (2 calculations)
- outcome: RUNTIME_SOURCE — each occurrence's value observed by its consumers only
- topology: one public input per occurrence carrying its own override
- diagnostic: none
- mutation: per-occurrence isolation — each override reaches only its occurrence's consumers
  (→ Item 6)
- certification: UNPROVEN — Item-4 foundation topology; pipeline + mutation legs owed (→ Items
  4/6)
- citations: kin: the "Per-occurrence distinct overrides" constraint row above

**Ambiguity (def-level referent, no unique occurrence in context)**

**C9 — owner-qualified (definition qualifier) × multi-occurrence context × calculation**

- disposition: SUPPORTED (D-6)
- referent: def-level feature via definition qualifier
- declaration: PartDef attribute
- occurrence: two concrete occurrences in the consumer's context; neither uniquely selected
- value_state: definition default, no overrides
- consumers: 1 calculation
- outcome: AMBIGUITY_DIAGNOSTIC — named diagnostic before any source exists; never a guess
- topology: none — no route yields a source
- diagnostic: named ambiguity diagnostic identifying the def-level referent and the candidate
  occurrences
- certification: BLOCKED(two-occurrence def-referent fixture realizing this key → Item 4)
- citations: AFT uncertainty register; `standards/sysml_ruling.md` residual ambiguity

**C10 — bare renamed × def context × multi-occurrence context × calculation**

- disposition: SUPPORTED (D-5)
- referent: def-level feature (referent table: bare renamed / def context)
- declaration: PartDef attribute
- occurrence: two concrete occurrences in the consumer's context; neither uniquely selected
- value_state: definition default, no overrides
- consumers: 1 calculation
- outcome: AMBIGUITY_DIAGNOSTIC — same named diagnostic; never a guess
- topology: none — no route yields a source
- diagnostic: named ambiguity diagnostic identifying the def-level referent and the candidate
  occurrences
- certification: BLOCKED(two-occurrence def-referent fixture realizing this key → Item 4)
- citations: AFT 1c referent class

**Cross-consumer (single-occurrence override; calculation + constraint + aggregation)**

**C11 — feature chain × mixed consumers**

- disposition: SUPPORTED (D-7)
- referent: occurrence-level — the redefining feature at the named occurrence
- declaration: PartDef attribute redefined at the usage
- occurrence: single concrete occurrence
- value_state: occurrence `:>>` override
- consumers: 1 calculation + 1 constraint + 1 aggregation (3 consumers)
- outcome: RUNTIME_SOURCE — one source; all consumer types converge on it
- topology: one public input; consumer edges for all three consumer types
- diagnostic: none
- mutation: one change reaches all three consumers (→ Item 6)
- certification: BLOCKED(cross-consumer fixture realizing this key → Item 4)
- citations: nearest controls RM 5/6 (convergence controls, not observations of this key)

**C12 — owner-qualified (definition qualifier) × mixed consumers**

- disposition: SUPPORTED (D-6)
- referent: def-level feature via definition qualifier
- declaration: PartDef attribute
- occurrence: single concrete occurrence; occurrence bridge required
- value_state: occurrence `:>>` override
- consumers: 1 calculation + 1 constraint + 1 aggregation (3 consumers)
- outcome: RUNTIME_SOURCE — the same convergence via the occurrence bridge
- topology: one public input at the bridged occurrence; edges for all three consumer types
- diagnostic: none
- mutation: one change reaches all three consumers (→ Item 6)
- certification: BLOCKED(cross-consumer fixture realizing this key → Item 4)
- citations: AFT 2 referent class

**C13 — bare renamed (usage context) × mixed consumers**

- disposition: SUPPORTED (D-5)
- referent: occurrence-level feature (referent table: bare renamed / usage context)
- declaration: PartDef attribute overridden at the concrete usage
- occurrence: single concrete usage; bindings authored inside it
- value_state: occurrence `:>>` override
- consumers: 1 calculation + 1 constraint + 1 aggregation (3 consumers)
- outcome: RUNTIME_SOURCE — the same convergence via the occurrence referent
- topology: one public input; edges for all three consumer types
- diagnostic: none
- mutation: one change reaches all three consumers (→ Item 6)
- certification: BLOCKED(cross-consumer fixture realizing this key → Item 4)
- citations: AFT 1c referent class; DCS referent evidence

**Cross-part / cross-owner**

**C14 — dotted chain × cross-part, value at source × 2 calculations (renamed formals)**

- disposition: SUPPORTED (D-7)
- referent: occurrence-level feature reached through the cross-part chain
- declaration: attribute on another part, value declared at the source
- occurrence: single concrete source occurrence, consumed cross-part
- value_state: value at source
- consumers: 2 calculations with renamed formals
- outcome: RUNTIME_SOURCE — one converged public field whose identity derives from the one
  authority, not from parallel synthesis
- topology: one converged public field (design-attribute-keyed)
- diagnostic: none
- mutation: one change reaches both calculations (→ Item 6)
- certification: UNPROVEN — authority derivation owed (→ Items 4/5); convergence is carried today
  by SVM synthesis (adjacent-work register row 6)
- citations: RM 6 (fusion_tea `driver.efficiency`, convergence topology observed)

**C15 — chain × cross-owner (parent attribute; parent-owned aggregation + constraint + child calculation)**

- disposition: SUPPORTED (D-7)
- referent: occurrence-level feature at the parent occurrence
- declaration: parent-part attribute
- occurrence: single concrete parent occurrence; consumers span owners
- value_state: occurrence `:>>` override
- consumers: 1 parent-owned aggregation + 1 parent-owned constraint + 1 child-part calculation
  (3 consumers)
- outcome: RUNTIME_SOURCE — one source across owners; mutation reaches all consumers
- topology: one public input; cross-owner consumer edges
- diagnostic: none
- mutation: one change reaches every consumer in both owners (→ Item 6)
- certification: BLOCKED(cross-owner supported-form fixture realizing this key → Item 4); census
  cross-owner unknown class (40 unresolved rows)
- citations: topology kin RM 7 (observed only in the unsupported form → 01f)

**Computed source (producer channel) — added 2026-08-07 by the audit-F1 reopening**

**C24 — feature chain to a computed value × single occurrence × mixed consumers (producer channel)**

- disposition: SUPPORTED (D-7, D-10)
- referent: concrete output feature `producer_calc.result`; the authored feature chain terminates
  directly at that calculation output
- declaration: output attribute `'Source Identity Producer'::result`, declared by calc def
  `'Source Identity Producer'` in the blocked Item-4 fixture
- occurrence: output feature `result` on concrete calc usage
  `source_identity_computed.producer_calc`
- value_state: value at source — computed at runtime; no authored literal and no public input
  exists for this source
- consumers: 1 calculation + 1 constraint + 1 aggregation (3 consumers)
- outcome: RUNTIME_SOURCE — one producer channel; every consumer wires to that channel; no public
  input is minted for a computed value
- topology: one producer channel (module output); zero public inputs for this source
- diagnostic: none
- mutation: mutating the producer's upstream public input changes the computed value once and
  reaches all three consumers through the one channel; no consumer holds an independent copy
  (→ Item 6)
- certification: BLOCKED(computed-source mixed-consumer fixture realizing this key → Item 4);
  route-specific controls exist but do not certify this key
- citations: epic mission invariant (owner) — one producer channel for a computed value; the
  "Producer-channel actual" constraint row above (single-consumer kin); invariant 19
  producer-first resolution; REQ-IR-07/REQ-CL-05 producer-wiring clauses (route-specific
  controls)

**Mixed binding-owner contexts — added 2026-08-07 by the customer-evidence correction**

**C25 — bare renamed × mixed definition/usage binding contexts × single-occurrence `:>>` override × 2 calculations**

- disposition: SUPPORTED (D-5)
- referent: the usage-authored binding resolves to the occurrence-level feature; the
  definition-authored binding resolves to the def-level feature and reaches the same concrete
  occurrence through the occurrence bridge
- declaration: PartDef attribute `IFE Power Plant::availability`
- occurrence: single concrete usage `hif_plant`; one binding authored inside that usage and one
  inside `part def 'IFE Power Plant'`
- value_state: occurrence `:>>` override (`hif_plant.sysml:69`)
- consumers: 2 calculations — usage-authored `meier_coe_calc` (`hif_plant.sysml:205,215`) and
  definition-authored `lcoe_calc` (`ife_plant.sysml:98,114`)
- outcome: RUNTIME_SOURCE — both referent paths converge on the one semantic source occurrence
- topology: one public input at `hif_plant.availability`; two consumer edges across the two
  binding-owner contexts
- diagnostic: none
- mutation: one off-default availability change reaches both calculations and nothing else
  (→ Item 6)
- certification: BLOCKED(mixed-context bare-renamed fixture → Item 4; customer migration plus
  live/relocated public mutation acceptance → Item 6)
- citations: epic customer criterion `:147-150`; the fixture lines above establish the exact
  owner contexts and consumer count; DCS:71,83 and AFT 1c establish the two referent classes;
  invariant 56 requires their convergence per source occurrence. This is a principle-derived
  target, not a claim that the current self-bound customer fixture already uses the supported form

**Literals and aggregation**

**C16 — authored usage literals (no written reference), equal values × 1 consumer each**

- disposition: SUPPORTED (D-11)
- referent: none — no written reference; each literal is its own source
- declaration: usage-owned authored literal attributes (two literals)
- occurrence: one concrete usage each
- value_state: authored literals with equal values
- consumers: 1 calculation each (2 calculations total)
- outcome: RUNTIME_SOURCE — distinct independent sources; mutating one leaves the other
- topology: distinct public inputs, one per authored literal
- diagnostic: none
- mutation: independent — changing one literal's input leaves the other's consumers unchanged
  (→ Item 6)
- certification: UNPROVEN — mutation leg owed (→ Item 6)
- citations: RM 8 (fusion_tea `num_units`, `target_factory_cost`); discriminator
  `written_reference is None` ⇔ authored

**C17 — aggregation-term dotted reference to producer-backed child attribute `permitting.capital_cost` × one concrete child occurrence × 1 aggregation**

- disposition: SUPPORTED (D-7, D-10, D-14)
- referent: occurrence-level feature `permitting.capital_cost` reached through the aggregation
  term's chain; its value is backed by `permitting.cost_model.total_cost`
- declaration: PartDef attribute redefinition
  `'Permitting & Interconnect'::capital_cost` and producer output
  `PermittingCostCalc::total_cost`
  (`tests/fixtures/solar_battery_model/library.sysml:210,227,571-575`)
- occurrence: child occurrence
  `SolarBatteryDesign::solar_battery_plant::site_infra::permitting`, owned by
  `'Site Infrastructure'` (`tests/fixtures/solar_battery_model/library.sysml:682,697-700`)
- value_state: value at source — computed at runtime by `permitting.cost_model`
- consumers: 1 aggregation
- outcome: RUNTIME_SOURCE — aggregation terms resolve through the same identity; no per-term mint
- topology: one producer channel feeding the aggregation; zero public inputs for this source; no
  minted per-term entry
- diagnostic: none
- mutation: changing the producer's upstream `system_capacity_kw` input changes
  `permitting.capital_cost` once and reaches the aggregate through that channel (→ Item 6)
- certification: UNPROVEN — HEAD's committed computation graph wires the term to producer channel
  `...permitting__cost_model__total_cost`; full live/relocated route and mutation evidence remains
  owed (→ Item 6)
- citations: `tests/fixtures/solar_battery_model/library.sysml:569-575,697-706`;
  `tests/fixtures/baseline_outputs/solar_battery/computation_graph.json:2695-2702`

**C26 — aggregation-term dotted references to literal-valued child attributes × one concrete child occurrence × 1 aggregation per source**

- disposition: SUPPORTED (D-7, D-10, D-14)
- referent: occurrence-level features `permitting.raw_material_cost`,
  `permitting.fabrication_cost`, and `permitting.installation_cost` reached through their
  aggregation-term chains
- declaration: three PartDef attribute redefinitions owned by
  `'Permitting & Interconnect'`
  (`tests/fixtures/solar_battery_model/library.sysml:576-578`)
- occurrence: child occurrence
  `SolarBatteryDesign::solar_battery_plant::site_infra::permitting`, owned by
  `'Site Infrastructure'` (`tests/fixtures/solar_battery_model/library.sysml:682,697-700`)
- value_state: definition-authored literal default `0.0`, with no occurrence override
- consumers: 1 aggregation per source (3 aggregation terms total)
- outcome: RUNTIME_SOURCE — each aggregation term resolves to its modeled source identity; no
  per-term source is minted
- topology: three distinct public inputs, one per literal-valued modeled-feature source; zero producer channels
  for these sources
- diagnostic: none
- mutation: changing one source input reaches its corresponding aggregate and leaves the other two
  source occurrences independent (→ Item 6)
- certification: CONTRADICTED_AT_HEAD — resolution fails at HEAD and per-term entry points are
  minted (I7 warnings)
- citations: RM 13 (broken positive resolution, literal-backed coordinate; not a genuine
  terminal miss); `tests/fixtures/solar_battery_model/library.sysml:576-578,697-721`;
  `tests/fixtures/baseline_outputs/solar_battery/computation_graph.json:2467-2473,2543-2549,2619-2625`;
  `.project/active/source-identity-route-evidence-spike/probes/raw/parity_solar_battery_model.json:194-216`

**C18 — aggregation-term reference, target genuinely absent × aggregation consumer**

- provenance: **[AGENT] (ratified by owner, 2026-08-09)** — corrected from an executable-policy
  premise after the licensed fixture proved that SysIDE rejects the absent feature during loading
- disposition: LANGUAGE_REJECTED (D-14)
- referent: none — language name resolution cannot resolve the term reference
- declaration: none — the target is genuinely absent from the model
- occurrence: none
- value_state: absent
- consumers: none — the syntactic aggregation never becomes a loaded model element
- outcome: LOAD_ERROR — processing stops before extraction or code generation
- topology: none
- diagnostic: the language diagnostic preserves the missing feature name (`ghost_cost`)
- certification: CERTIFIED — `source_identity_absent_referent` and the executable C18 matrix cell
- citations: D-14; `tests/fixtures/source_identity_absent_referent/PROVENANCE.md`

**Nested, shadowing, specialization (published target keys; Item 4 realizes fixtures)**

**C19 — chain `source.reading` × nested-occurrence `:>>` override × calculation + constraint**

- disposition: SUPPORTED (D-7)
- referent: occurrence-level — the redefining feature at the named nested occurrence (NOP:22,25)
- declaration: PartDef attribute redefined at a nested occurrence (NOP:37)
- occurrence: nested concrete occurrence
- value_state: nested-occurrence `:>>` override (80.0)
- consumers: 1 calculation + 1 constraint
- outcome: RUNTIME_SOURCE — the override (80.0) applies on both consumer paths
- topology: one public input at the nested occurrence
- diagnostic: none owed at the boundary; the current calc-path tripwire is silent for this shape
- mutation: a change reaches calculation and constraint together (→ Item 6)
- certification: BLOCKED(live leg → Item 4); snapshot capture halts by design for this fixture
- citations: NOP:22,25,37; adjacent-work register row 2

**C20 — shadowing: bare renamed × intervening same-named declaration**

- disposition: SUPPORTED (D-5)
- referent: the KerML nearest-scope referent — the shadowing declaration, not the shadowed
  attribute
- declaration: the intervening same-named declaration between the consumer scope and the intended
  attribute
- occurrence: the concrete occurrence of the nearest-scope referent
- value_state: value at the nearest-scope referent
- consumers: 1 calculation
- outcome: RUNTIME_SOURCE — at the KerML nearest-scope referent; no name-coincidence capture
  across the shadow
- topology: one public input at the nearest-scope referent
- diagnostic: none
- mutation: a change at the nearest-scope referent reaches the consumer; the shadowed attribute's
  value does not (→ Items 4/6)
- certification: BLOCKED(shadowing fixture realizing this key → Item 4); the census ambiguity
  count of zero is not proof of none
- citations: AFT 1c referent class; census

**C21 — specialization: chain through a retyped usage whose specialized definition carries `:>>`**

- disposition: SUPPORTED (D-7)
- referent: the redefining (specialized) feature at that occurrence
- declaration: the specialized definition's `:>>` redefinition
- occurrence: the retyped concrete usage
- value_state: specialized `:>>` value
- consumers: 1 calculation
- outcome: RUNTIME_SOURCE — the redefining value at that occurrence; the general feature is not a
  separate source
- topology: one public input at the specialized redefinition
- diagnostic: none
- mutation: a change at the specialized value reaches the consumer (→ Items 4/6)
- certification: BLOCKED(specialization fixture realizing this key → Item 4)
- citations: kin: REQ-VBR-10 `stands` clause (`spec_chain_channel` family)

**Checkpoint-resolved classes**

**C22 — expression binding × value-expression referent × any operand/topology variant (family; D-15)**

- disposition: DEFERRED(owner, 2026-08-05) (D-15)
- referent: value expression — the class always stops at readiness validation, before operand
  topology or consumer mix can affect source behavior (family collapse legitimate)
- outcome: AUTHORING_DIAGNOSTIC — fail-closed codegen-readiness diagnostic; no flattening; no
  invented source
- topology: none
- diagnostic: distinct readiness diagnostic; wording states valid SysML, unsupported by this
  executable subset
- citations: D-15; census expression class (7-EP population — population evidence, not the proof
  coordinate)

**22a — kept readiness coordinate**

- declaration: calculation-usage input binding
  `ExpressionBindingDesign::expr_probe::cost_calc::combined_input`, owned by calculation usage
  `cost_calc` (`tests/fixtures/expression_binding_probe/design.sysml:18-20`)
- occurrence: single concrete calculation usage `expr_probe.cost_calc` inside the concrete
  `PartUsage` `expr_probe`
- value_state: expression-computed
- consumers: 1 calculation (`cost_calc`)
- certification: UNPROVEN — one kept readiness-diagnostic coordinate owed (→ Items 4/6)
- citations: `expression_binding_probe`, `plant_value_shapes`; checkpoint item 4

**C23 — none (unbound formal) × calculation-definition default × one concrete calculation usage**

- disposition: SUPPORTED (D-12)
- referent: none — no written reference; the calculation definition's declared input default
- declaration: calculation-definition input parameter carrying a default
- occurrence: one concrete calculation usage
- value_state: library default
- consumers: 1 calculation (the one usage)
- outcome: RUNTIME_SOURCE — one independently overridable `LIBRARY_DEFAULT` source per concrete
  usage; no sharing without an explicit modeled relationship
- topology: one per-usage public `LIBRARY_DEFAULT` input
- diagnostic: none
- mutation: overriding one usage's default leaves sibling usages unchanged (→ Item 6)
- certification: UNPROVEN — mutation leg owed (→ Item 6)
- citations: D-12; RM 11 (solar_battery `fab_factor`: 8 usages → 8 per-usage fields by ADR-001
  design); census library-default class (58 EPs)

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
