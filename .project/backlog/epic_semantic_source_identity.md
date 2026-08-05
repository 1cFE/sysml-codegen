# Epic: One Modeled Value, One Runtime Source

**Epic ID**: SOURCE-IDENTITY
**Status**: Ready
**Priority**: Critical (P0 for study releases)
**Created**: 2026-08-03
**Estimated Effort**: 3–5 weeks (16–26 engineering days; re-estimate after spikes)

---

## Executive Summary

`sysml-codegen` exists to turn one authored SysML model into a faithful executable graph by
backtracking every consumed value to its semantic source: the modeled declaration in its concrete
occurrence. A binding is not an independent runtime knob. When several calculations consume one
externally supplied modeled value, the generated package must expose one public parameter whose value
reaches all of them; when they consume a computed value, they must share its producer channel; and an
unsupported authored form must fail before package generation. This epic restores that contract,
beginning with semantic and pipeline spikes before any fix is designed, then carrying the verified
result through implementation, generated artifacts, studies, documentation, and certification.

**Critical Success Factor**: Every consumed modeled value resolves to exactly one runtime source
across all bound consumers. An externally supplied value has one public input whose mutation reaches
every and only those consumers; a computed value has one producer channel; and an unsupported or
semantically invalid binding fails loudly before package generation.

---

## Source Documents

- **[research]** [How a central backtracking bug survived the refactors and reviews](../research/20260803-202453_backtracking-fanout-forensics.md) — primary forensic report. It establishes that the customer shape never worked, identifies where source identity is destroyed, documents the wrong-oracle test and review failures, and scopes the study blast radius.
- **[research]** [Entry-surface fan-out forensics](../research/20260803-203011_entry-surface-fanout-forensics.md) — complementary mechanism and standards analysis. It identifies the unresolved semantics of bare self-named bindings and the two current fan-out paths.
- **[concept]** [Constraint Execution: Authoritative Lifecycle Contract](../concepts/constraint-execution-authoritative-lifecycle-contract.md) — ratified model/generated-package/study ownership and lifecycle invariants, including shared positive resolution, producer completeness, semantic identity, and complete typed study inputs.
- **[concept]** [Constraint Execution and Design-Space Studies](../concepts/constraint-execution-and-design-space-studies.md) — original product framing for a trustworthy generated forward model and repeatable studies over stable model parameters.

---

## Why This Epic?

**Current State**:

- The library violates its founding purpose on a customer-shaped composition: one `PartDef`
  attribute supplied at a concrete occurrence and consumed by multiple self-named calculation
  bindings becomes multiple independently mutable public inputs. The exact composition never
  worked; it is not a regression from a previously correct implementation
  ([primary research, Executive verdict and history](../research/20260803-202453_backtracking-fanout-forensics.md#executive-verdict)).
- The pipeline loses or obscures source identity before backtracking. Self-named extraction may
  resolve to the calculation formal, and virtual-binding rewrite copies the occurrence value into
  each consumer, changes the binding to a consumer-local literal, and clears its source path. The
  literal backtracking route then mints one entry point per consumer
  ([primary research, Exact failure mechanism](../research/20260803-202453_backtracking-fanout-forensics.md#exact-failure-mechanism)).
- The defect is numerically invisible at the captured design point because all duplicate fields
  start with the same value. It becomes semantically wrong when a study or user changes one copy and
  only some consumers observe the modeled value. Sweeps, optimization, sensitivity analysis, and
  manual input edits are therefore unsafe on affected packages
  ([primary research, Blast radius](../research/20260803-202453_backtracking-fanout-forensics.md#blast-radius)).
- Tests, baselines, plans, and audits institutionalized the wrong oracle. They prove selected routes
  and fixed-point arithmetic while simultaneously preserving per-consumer fan-out as expected
  behavior. The project had the real fixture and the contradiction, but narrowed the acceptance
  meaning instead of escalating it
  ([primary research, How the review pipeline failed](../research/20260803-202453_backtracking-fanout-forensics.md#how-the-review-pipeline-failed)).
- The intended meaning of bare self-named syntax such as `in R = R` is not settled. SysIDE and KerML
  evidence indicate a local self-binding, while existing code paths sometimes reinterpret the form
  as a reference to the outer modeled attribute. Designing a repair before resolving this would
  encode another accidental semantics
  ([complementary research, spec ruling](../research/20260803-203011_entry-surface-fanout-forensics.md#the-spec-ruling-on-in-r--r)).
- The affected boundary is not yet enumerated. Ownership, occurrence expansion, overrides,
  reference spelling, consumer type, consumer count, and live versus snapshot generation can all
  change the route. The verification corpus proves isolated cells, not the governing invariant
  ([primary research, What the refactors did not prove](../research/20260803-202453_backtracking-fanout-forensics.md#what-the-massive-refactors-actually-proved)).
- Occurrence identity is already split across coordinated and uncoordinated work. Lifecycle Item 10
  landed general per-child `:>>` capture and instance-scoped producer routing, while the outstanding
  `[NESTED-OCCURRENCE-OVERRIDE]` fix needs an occurrence→definition bridge in the supplied-value
  materializer and `[CONSTRAINT-ARCH-UNIFY]` sub-scope 2 proposes one shared part-structure index.
  Treating these as sibling fixes would create competing authorities on the same seam
  ([BACKLOG, NESTED-OCCURRENCE-OVERRIDE and CONSTRAINT-ARCH-UNIFY](BACKLOG.md)).

**Future State**:

- The library has one explicit source-identity contract: every model-derived consumed value resolves
  to its intended declaration in its concrete occurrence before a generated input, default, or
  producer channel is chosen. Binding routes cannot silently turn a reference into an unrelated
  consumer-local parameter.
- Evidence-producing spikes establish SysML/SysIDE referent behavior, supported authoring forms,
  current live/snapshot route behavior, and the full affected corpus before the repair is designed.
  The owner then dispositions every authoring-form class in the resulting table, including bare,
  qualified, chained, and occurrence-indexed forms. No agent silently expands or narrows support.
- Those dispositions amend the ratified lifecycle contract, its companion requirements spec, and the
  contract's correction register before fix design is approved. README, architecture, matrix, and
  acceptance claims derive from that authority instead of becoming an independent semantics layer.
- Calculation, constraint, aggregation, occurrence-override, live, and snapshot routes enforce the
  same source identity. Strictness may change the terminal error policy; it does not change which
  modeled value a binding means. Unsupported shapes fail with an actionable diagnostic.
- Generated packages expose stable semantic parameters suitable for single runs and studies. A
  candidate changes one model-owned field and every bound consumer observes the same value, matching
  the model/generated-package/study separation in the ratified lifecycle contract.
- The complete fixture and generated-package corpus is audited by modeled source rather than by
  output bytes. Every forced entry-key, contract, snapshot, package, and study-lineage change is
  reviewed as a semantic migration.
- Customer/demo packages and any affected study evidence are regenerated or corrected. Historical
  acceptance and verification claims state exactly what was and was not proven.
- The README, architecture references, verification matrix, and acceptance tests state the point of
  the library directly and verify it at the public mutation boundary.

---

## Success Criteria

- [ ] **[OWNER] Mission invariant:** For every supported binding, one semantic source occurrence maps
  to exactly one runtime source across all consumers: one public input for an externally supplied
  value or one producer channel for a computed value. A bound calculation parameter is never exposed
  as an independently mutable input merely because it has a different consumer.
- [ ] **[AGENT] (ratified by owner, 2026-08-03) Spike-first gate:** No fix design begins until kept
  spikes establish (a) SysIDE referents for bare, owner-qualified, feature-chain, and bracketed
  occurrence-index forms; (b) the current behavior of both known fan-out paths; (c) a matrix covering
  owner kind, declaration site, occurrence override, written reference form, consumer type, consumer
  count, live and relocated-snapshot routes, and off-default mutation result; (d) whether written
  reference plus occurrence-owner evidence is sufficient to recover exact source identity, or
  extraction must emit an explicit semantic source ID with the resulting snapshot-schema/version and
  corpus-recapture impact; and (e) an owner disposition for every supported or rejected
  authoring-form class found by the matrix.
- [ ] **[AGENT] Authority-chain gate:** Before fix design is approved, the owner dispositions and
  resolved source-identity semantics are recorded in the
  [ratified lifecycle contract](../concepts/constraint-execution-authoritative-lifecycle-contract.md),
  its [companion requirements spec](../completed/20260720_constraint-execution-lifecycle-contract/spec.md),
  and the contract's correction register. Superseded readings of invariants 19, 20, 22, and 26 are
  named explicitly; this epic, downstream docs, and implementation artifacts do not become competing
  semantic authorities.
- [ ] **[AGENT] Seam-ownership gate:** This epic absorbs the remaining
  `[NESTED-OCCURRENCE-OVERRIDE]` fix as a required source-identity cell, reuses and audits the landed
  Lifecycle Item-10 per-child redefinition/producer-routing machinery, and explicitly sequences its
  occurrence work against `[CONSTRAINT-ARCH-UNIFY]` sub-scope 2. Stage 2 may not create a second
  occurrence→definition bridge, concrete-instance walker authority, or supplied-value identity
  policy.
- [ ] Every supported matrix cell proves source identity at the public package boundary: exactly one
  entry field for an externally supplied source or one channel for a computed source, the intended
  modeled default or override, and mutation observed by every bound calculation, constraint, and
  aggregation consumer. Every unsupported cell fails before generation with a stable, actionable
  diagnostic.
- [ ] The pipeline preserves or reconstructs exact modeled-source provenance before any
  consumer-local value materialization. A reference-derived supplied value cannot be silently
  classified as an independently authored usage literal, and a terminal fallback cannot convert a
  model binding into a public input without a named failure or an explicitly supported external-input
  contract.
- [ ] The exact customer composition is a public live-and-relocated-snapshot acceptance fixture. If
  bare self-named syntax is supported, it generates one input whose mutation reaches both consumers.
  If it is rejected, the original form fails loudly and the approved explicit form generates the one
  shared input.
- [ ] A whole-corpus semantic-source audit accounts for every generated entry point. Every modeled
  source that maps to multiple fields is classified, fixed or explicitly rejected; every forced
  baseline, snapshot, contract, parameter-schema, or generated-package change receives semantic
  review rather than automatic byte acceptance.
- [ ] Fusion Tea and Stellarator artifacts are regenerated against the corrected contract. The July
  IFE study is checked for downstream use of frozen-design-point cost outputs; any decision-relevant
  affected results are rerun or explicitly corrected, and incompatible study stores begin a new
  lineage rather than silently reusing old identity.
- [ ] Contradictory tests and certification records are corrected. Route-specific requirements no
  longer imply universal convergence, the Fusion Tea one-copy perturbation is removed or reframed,
  and the verification matrix contains an independently anchored source-identity family with public
  mutation evidence.
- [ ] The README and architecture documentation state the library's governing purpose in plain
  language: translate the SysML model into a faithful executable graph by resolving bound values to
  their modeled sources; never invent independent study variables for parameters the model binds
  together.
- [ ] The repair leaves one semantic authority and one supported resolution path per responsibility.
  Superseded rescue, fan-out, or compatibility behavior is deleted rather than wrapped in another
  route. Full unit, conformance, live/snapshot parity, generated-package, TEAx integration, and
  affected real-model acceptance gates pass, with only reviewed semantic output changes.

---

## Non-Goals

- Redesigning the global review workflow or adding more review stages. This epic makes the
  source-identity evidence standard durable in the authoritative contract and verification matrix;
  broader workflow reform remains outside this defect's scope.
- Treating consumer-side fan-out expansion, aliases, or synchronized duplicate values as closure.
  They may be temporary diagnostics or migration aids, but they do not satisfy source identity.
- Absorbing the two queued `agentic-mbse pm` CLI defects (`update-validation` pipe corruption and
  `close-item` colon parsing). Their batch-filing decision remains tracked in `CURRENT_WORK.md`, but
  they do not affect this epic's semantic contract or critical path.

---

## Epic Strategy

All item boundaries and scopes below are **[AGENT] (ratified by owner, 2026-08-04)** unless an item
records more specific provenance. The epic stays unified despite its size because source identity is
one end-to-end product invariant. Splitting extraction, occurrence mapping, backtracking, generated
packages, and studies into separate epics would allow local completion while the public semantics
remain wrong.

The delivery order is evidence → authority → implementation → migration → certification:

1. Items 1 and 2 measure language behavior, pipeline behavior, evidence sufficiency, and the corpus.
   They may start together, but both must close before semantic decisions.
2. Item 3 records the owner's authoring-form dispositions in the ratified authority. No fix design is
   approved before that gate.
3. Items 4 and 5 establish semantic identity, then cut every consumer route over to it. They absorb
   the outstanding nested-occurrence fix and remove parallel identity behavior.
4. Items 6 and 7 migrate the corpus and downstream consumers using public mutation evidence. Old/new
   byte parity is evidence of stability only where no semantic change is required.
5. Item 8 corrects the certification record and runs one composed source→package→study proof.

Items 4–7 exceed the guide's normal two-day target because each crosses a semantic boundary that must
change atomically. Their internal plans must use independently checkable phases and stop if a phase
reveals a new source-identity authority or an unapproved authoring-form semantics.

---

## Evidence Checkpoint — 2026-08-05

### Confirmed facts

- **[INHERITED: Item 1 findings]** Bare self-named `in R = R` is normatively a legal, silent
  self-binding. KerML nearest-scope resolution reaches the calculation formal; the renamed-formal
  control reaches the outer attribute, proving the name collision is the complete cause. Codegen may
  preserve that meaning or reject the form as unsupported, but may not reinterpret it as an outer
  reference while claiming language fidelity.
- **[INHERITED: Item 1 findings]** The two spec-correct outer-source forms identify different model
  elements. `'Probe Plant'::R` names the definition attribute. `plant.R` names the occurrence-level
  redefining feature, whose SysIDE `owned_redefinitions` edge names both the definition and override
  site. The standards do not choose which one carries this project's concrete-occurrence contract.
- **[INHERITED: Item 1 findings]** `plants#(1).R` is valid value selection whose target referent stays
  definition-level; the occurrence index is not feature identity, and current extraction silently
  drops its index segment. `plants[1].R` is not occurrence indexing and fails to load. Neither form
  appears in the current corpora.
- **[INHERITED: Item 2 learning-test findings]** Snapshot capture serializes bindings after the
  Step-3.5 literal stamp, while snapshot rebuild does not rerun VBR. Correcting captured identity
  therefore requires coordinated capture/rebuild behavior and recapturing all 37 snapshot fixtures.
- **[INHERITED: Item 2 learning-test findings]** Existing written-reference fields survive the stamp
  and reliably distinguish authored literals (`written_reference is None`) from reference-derived
  stamped values. They do not identify the exact source generally: only 35 of 75 model-derived
  per-consumer entry points reconstruct by owner plus leaf; 40 cross-owner/tail cases do not.
- **[INHERITED: Item 2 learning-test findings]** The current 37-fixture corpus exposes 277 public
  entry points. Seventy-five (27%) are model-derived per-consumer mints: 37 silent stamps and 38
  lenient misses. This is a broad semantic class, not one customer-only edge.
- **[INHERITED: Item 2 learning-test findings]** Parameter-group derivation is a fourth value
  authority: it can backfill a definition default onto a consumer-local `USAGE_LITERAL`, masking
  identity loss while preserving the fixed-point value.
- **[INHERITED: Item 2 licensed parity]** Live, committed-snapshot, and relocated-snapshot routes
  produce identical topology and watched binding state for `fusion_tea`, `ife_plant`,
  `shared_producer`, and `solar_battery_model`. The defect is a pipeline semantic preserved across
  routes, not snapshot-only drift.

### Current direction — not yet authoritative

These are **[AGENT]** recommendations. Item 2's technical evidence, licensed parity, and joint
synthesis now support them; the aggregation-family disposition remains owner-held before Item 2 can
close. Item 3 must obtain the remaining semantic dispositions and record them in the ratified
authority.

1. Adopt an extraction-owned semantic source ID built from SysIDE referent/redefinition evidence.
   Written-reference reconstruction remains useful diagnostic provenance, not the identity authority.
2. Treat the source-ID change as a snapshot schema/version migration: update capture and rebuild
   together, fail closed on insufficient historical evidence, and recapture the 37-fixture corpus.
3. Reject bare self-named bindings loudly as unsupported for executable generation rather than
   assigning them a non-normative outer-reference meaning. For a concrete `:>>` value, prefer an
   occurrence-qualified feature chain as the migration target; retain definition-qualified syntax
   only with its distinct, explicitly supported semantics.
4. Defer `#(i)` executable support until index identity is modeled end to end, and reject `[i]` with
   the language/load diagnostic. Both have zero current migration cost.
5. Absorb the queued producer-channel/aggregation-scoping finding into this semantic family unless
   Item 2's live evidence disproves the shared terminal-mint mechanism.
6. Put the parameter-group backfill on Item 5's deletion/consolidation register. One semantic source
   authority must choose both identity and modeled default; a separate value repair may not make a
   wrong identity appear correct.

Primary evidence:

- `.project/active/source-identity-binding-semantics-spike/findings.md`
- `.project/active/source-identity-binding-semantics-spike/authoring-form-table.md`
- `.project/research/20260805-054752_source-identity-route-evidence.md`
- `tests/conformance/test_source_identity_routes.py`

---

## Backlog Items

#### Item 1: Binding Semantics and Authoring-Form Spike (1–2 days)

**Type**: Research / Spike

**Status**: Complete (2026-08-05; executed through the approved spike-shaped evidence path)

**Objective**: Establish what each relevant SysML binding form denotes and what SysIDE actually
reports, without designing or implementing a repair.

**Current State**:
- ✅ The forensic reports and `self_named_binding_trap` record that a bare `in R = R` can resolve to
  the calculation's own formal.
- ⚠️ KerML nearest-scope analysis supports that observation, but the repository has no kept,
  systematic comparison across authoring forms.
- ❌ Owner-qualified, feature-chain, and bracketed occurrence forms do not have one shared evidence
  table or public live probe.
- ❓ The project has not dispositioned which forms it supports, rejects, or migrates.

**Scope**:
1. **Authoring-form fixtures and probes**:
   - Construct minimal, source-faithful cases for bare self-named, owner-qualified, feature-chain,
     and bracketed occurrence-index references.
   - Hold modeled meaning constant where possible so differences arise from syntax and scope, not
     different values or topologies.
2. **Referent evidence**:
   - Record written form, SysIDE AST/referent, resolved QN, owning namespace, occurrence evidence,
     and emitted diagnostic for every form.
   - Run through licensed public loading; retain raw evidence sufficient for independent review.
3. **Language analysis**:
   - Reconcile observed behavior with the exact KerML/SysML scoping and calculation-parameter rules.
   - Separate standards-derived meaning from project convention and from current implementation.
4. **Decision input**:
   - Produce an authoring-form table that names proven meaning, uncertainty, corpus prevalence, and
     migration consequences without silently choosing project support policy.

**Out of Scope**:
- Production code, generated baseline, snapshot-schema, or model-corpus changes.
- Owner dispositions; Item 3 owns the authoritative decision.
- A consumer-side workaround or a proposal to synchronize duplicate fields.

**Success Criteria**:
- [x] Every named authoring form has a repeatable licensed probe and retained raw referent evidence.
- [x] The table distinguishes written reference, resolved referent, intended outer source, and
  concrete occurrence; no field is inferred from the implementation under test.
- [x] Standards conclusions cite primary normative text and identify any remaining ambiguity plainly.
- [x] Corpus prevalence and migration implications are recorded for each form.
- [x] The findings contain no fix design and are sufficient for the Item-3 owner disposition.

**Estimated Effort**: 1–2 days (spec 1h, design 1h, plan 1h, execute/findings 5–12h)

**Spike executed 2026-08-05** (via `/_my_spike`; probes + findings + table, the
spec/design/plan deliverables consciously skipped for the spike shape — rationale in
findings.md). What it resolved: all four forms have repeatable licensed probes with
retained raw referent evidence, reconciled against clause-cited KerML/SysML rulings.
Bare `in R = R` is a normatively *required* self-binding (shadowing is the entire
cause; the renamed control resolves to the outer attribute). The two correct
replacements denote different elements — qualified → def-level attribute, chain →
occurrence-level redefining feature — and the spec does not adjudicate between them
(that choice is an Item-3 disposition). `#(i)` parses with value-only semantics
(referent stays def-level; the current extractor silently drops the index segment —
new identity-loss site for Item 2's matrix); `[i]` is the quantity bracket and fails
to load; both indexed spellings have zero corpus prevalence, while bare self-named is
~47% of usage bindings in both external corpora and the qualified form has zero
external use. Decision table:
`.project/active/source-identity-binding-semantics-spike/authoring-form-table.md`;
findings: `.project/active/source-identity-binding-semantics-spike/findings.md`.

**Location**: `.project/active/source-identity-binding-semantics-spike/`

**Dependencies**: None; licensed SysIDE access is required for the live evidence leg.

**Required Reading**:
- Both forensic reports listed under Source Documents.
- `tests/conformance/test_self_named_binding_trap.py` and its fixture.
- KerML 1.0 §8.2.3.5 and the SysML calculation-usage semantics they govern.

**Deliverables**:
- The listed `spec.md`, `design.md`, and `plan.md` were consciously skipped because the item was
  invoked through `/_my_spike`; the dated deviation and rationale are recorded in `findings.md`.
- `.project/active/source-identity-binding-semantics-spike/authoring-form-table.md`
- `.project/active/source-identity-binding-semantics-spike/findings.md`
- `.project/active/source-identity-binding-semantics-spike/probes/`

---

#### Item 2: Source-Identity Routes and Evidence-Sufficiency Spike (2–3 days)

**Type**: Research / Learning Tests

**Status**: In Progress — technical evidence, joint synthesis, and licensed parity complete; owner
aggregation-family disposition remains

**Objective**: Map where semantic identity survives or is lost, determine the minimum sufficient
source evidence for a correct repair, and enumerate the affected corpus before design.

**Current State**:
- ✅ The forensic reports identify the silent literal-stamp path and the warned lenient-miss path.
- ✅ Lifecycle Item 10 landed per-child redefinition capture and transitive instance routing.
- ✅ **Learning-test leg complete (2026-08-05)**: kept tests in
  `tests/conformance/test_source_identity_routes.py` pin both fan-out paths, the
  authored-vs-reference-derived literal discriminator, and the cross-owner cell where owner-local
  reconstruction fails; findings, identity trace, initial census (277 entry points, 75
  model-derived per-consumer mints), and adjacent-work register in
  `.project/research/20260805-054752_source-identity-route-evidence.md`. Key new facts: snapshot
  capture persists the post-VBR stamp (rebuild has no VBR step), written-form evidence survives
  the stamp, and a fourth value authority (group-deriver backfill,
  `graph_builder.py:620-630`) masks Path-B identity loss.
- ✅ **Joint synthesis and licensed parity complete (2026-08-05)**: Item-1 language evidence rules
  out preserving the self-referential `source_path` as the intended source; an extraction-owned
  semantic source ID is the final evidence-sufficiency verdict. Live, snapshot, and relocated routes
  match on four representative fixtures. Route matrix, identity trace, census, parity scripts, and
  raw results live in `.project/active/source-identity-route-evidence-spike/`.
- ⚠️ Existing tests certify contradictory route-specific outcomes, and the initial corpus findings
  are not a complete semantic-source census (cross-owner duplicates remain an unknown class).
- ⚠️ The remaining close gate is the owner disposition of the queued Fusion Tea
  producer-channel/aggregation-scoping finding. Evidence places its unresolved aggregation terms in
  the same terminal-mint family and supports absorption.

**Scope**:
1. **Full route matrix**:
   - Cover owner kind, declaration site, occurrence override, written reference form, consumer type,
     consumer count, live/relocated-snapshot route, and off-default mutation result.
   - Characterize calculation, constraint, and aggregation consumers without using one route as the
     oracle for another.
2. **Identity trace**:
   - Trace declaration/occurrence identity through extraction, virtual-binding rewrite,
     supplied-value materialization, producer resolution, dependency backtracking, graph assembly,
     generated parameter schemas, and public execution.
   - Pin the first stage at which identity becomes absent, ambiguous, or mislabeled.
3. **Evidence-sufficiency experiment**:
   - Attempt exact reconstruction from written reference plus occurrence-owner/index data across
     positive, ambiguous, nested, specialized, and multi-occurrence cases.
   - Compare that route with an explicit extraction-owned semantic source ID. Name the required
     snapshot-format/version, fixture-recapture, and companion-repository impact of each option.
4. **Initial whole-corpus census**:
   - Map generated inputs and producer channels back to semantic source occurrences where evidence
     permits; list every duplicate, ambiguity, and unknown rather than forcing classification.
5. **Adjacent-work disposition**:
   - Reconcile the landed Item-10 machinery, `[NESTED-OCCURRENCE-OVERRIDE]`,
     `[CONSTRAINT-ARCH-UNIFY]` sub-scope 2, and the queued Fusion Tea
     producer-channel/aggregation-scoping finding.

**Out of Scope**:
- Choosing the supported authoring forms; Item 3 owns the owner decision.
- Production fixes, snapshot migration, or automatic baseline regeneration.
- Treating entry-key equality alone as evidence of semantic identity.

**Success Criteria**:
- [x] Every required matrix cell has a retained observation or is explicitly blocked with the exact
  missing evidence named.
- [x] The identity trace independently records the source occurrence and every derived identity at
  each stage.
- [x] A falsifiable evidence-sufficiency verdict selects reconstruction or explicit source ID and
  states the schema/version blast radius.
- [x] The corpus census accounts for all generated entry points in the selected fixture corpus and
  preserves an explicit unknown class.
- [ ] The adjacent-work register assigns one owner/disposition per overlapping mechanism; no second
  occurrence bridge or part-structure authority is proposed.
- [x] Kept learning tests or probes fail on at least the two known fan-out paths and distinguish
  genuinely independent literals from references sharing a source.

**Estimated Effort**: 2–3 days (spec 1.5h, design 2h, plan 1h, execute/findings 11–19h)

**Location**: `.project/active/source-identity-route-evidence-spike/`

**Dependencies**: May start with Item 1; Item 1 must complete before this item's final semantic
synthesis.

**Required Reading**:
- Both forensic reports and the ratified lifecycle contract.
- `[NESTED-OCCURRENCE-OVERRIDE]` and `[CONSTRAINT-ARCH-UNIFY]` in `BACKLOG.md`.
- `.project/completed/20260720_constraint-lifecycle-producer-completeness/` design, evidence, and
  audit.
- Current extraction, VBR, supplied-value, producer-resolution, backtracking, graph, and snapshot
  architecture references.

**Deliverables**:
- The listed `spec.md`, `design.md`, and `plan.md` were consciously skipped because the item was
  invoked through `/_my_learning_test` (same call as Item 1); the dated deviation and rationale
  are recorded in `findings.md`. Kept tests live in
  `tests/conformance/test_source_identity_routes.py`.
- `.project/active/source-identity-route-evidence-spike/route-matrix.md`
- `.project/active/source-identity-route-evidence-spike/identity-trace.md`
- `.project/active/source-identity-route-evidence-spike/corpus-census.md`
- `.project/active/source-identity-route-evidence-spike/adjacent-work-register.md`
- `.project/active/source-identity-route-evidence-spike/findings.md`
- `.project/active/source-identity-route-evidence-spike/probes/`

---

#### Item 3: Authoritative Source-Identity Contract (1 day)

**Type**: Specification / Decision

**Objective**: Turn the spike evidence and owner dispositions into the one authoritative semantic
contract that all implementation and certification work must follow.

**Current State**:
- ✅ The ratified lifecycle contract already requires shared positive resolution, exact producer
  identity, and complete typed study inputs.
- ⚠️ Its current invariants do not disposition the newly enumerated authoring forms, and existing
  architecture/matrix rows support contradictory readings.
- ❌ No authoritative source-identity acceptance matrix binds syntax, occurrence, consumer, and
  public mutation behavior together.

**Scope**:
1. **Owner decision checkpoint**:
   - Present the complete authoring-form and route evidence without collapsing standards meaning,
     project convention, and migration cost.
   - Record an owner disposition for every supported, rejected, or explicitly deferred class with
     exact provenance.
2. **Normative contract amendment**:
   - Define semantic source occurrence, supplied external input, modeled default, producer channel,
     authored independent literal, and impermissible consumer-local fallback.
   - Amend lifecycle invariants 19, 20, 22, and 26 and the correction register where existing
     readings are superseded or narrowed.
3. **Companion requirements**:
   - Add checkable requirements for source identity, occurrence identity, reference/value
     separation, supported-form diagnostics, live/snapshot parity, and public mutation.
   - Mark contradictory current matrix/acceptance claims partial or failed pending Items 4–8.
4. **Acceptance authority**:
   - Publish the authoritative source-identity matrix and evidence coordinate that downstream item
     specs must inherit rather than restate.

**Out of Scope**:
- Technical fix design, code changes, fixture migration, and downstream package regeneration.
- Rewriting broad public documentation; Item 8 owns that projection.
- Upgrading an agent recommendation to owner-originated provenance merely because it is approved.

**Success Criteria**:
- [ ] Every authoring-form class has an owner disposition or an explicitly owner-approved deferral.
- [ ] The ratified lifecycle contract and companion spec contain the same source-identity semantics
  and preserve the provenance grade of each decision.
- [ ] The correction register identifies every superseded reading relevant to this defect.
- [ ] The acceptance matrix defines topology, value provenance, diagnostic, and mutation outcomes at
  the public boundary for every supported and rejected class.
- [ ] Items 4 and 5 can derive their specs without inventing a semantics decision.

**Estimated Effort**: 1 day (spec 2h, authority design 1.5h, plan 0.5h, owner checkpoint/amendments 4h)

**Location**: `.project/active/source-identity-contract/`

**Dependencies**: Items 1 and 2 complete; owner available for the disposition checkpoint.

**Required Reading**:
- Item 1 authoring-form table and findings.
- Item 2 route matrix, evidence-sufficiency verdict, corpus census, and adjacent-work register.
- Ratified lifecycle contract and `.project/completed/20260720_constraint-execution-lifecycle-contract/spec.md`.
- Current verification-matrix rows REQ-IR-06/07, REQ-SVM-01/02/04, REQ-CL-05, and REQ-VBR-10.

**Deliverables**:
- `.project/active/source-identity-contract/spec.md`
- `.project/active/source-identity-contract/design.md`
- `.project/active/source-identity-contract/plan.md`
- `.project/active/source-identity-contract/decision-register.md`
- `.project/active/source-identity-contract/acceptance-matrix.md`
- Updated ratified lifecycle contract, companion spec, and correction register.

---

#### Item 4: Semantic Identity and Occurrence Foundation (3–4 days)

**Type**: Code / Integration

**Objective**: Give every model-derived consumed value one exact declaration-plus-occurrence identity
that survives live extraction and snapshot replay before consumer resolution begins.

**Current State**:
- ✅ The occurrence index and Lifecycle Item-10 machinery represent several concrete-instance and
  per-child redefinition cases.
- ✅ The nested-occurrence tripwire names one definition-relative capture versus occurrence-relative
  demand mismatch.
- ⚠️ Identity still crosses key seams as raw strings and parallel scope projections.
- ❌ The nested-occurrence override does not resolve, and the self-named fan-out path can lose outer
  source identity before resolution.

**Scope**:
1. **Chosen semantic identity representation**:
   - Implement the Item-2/3 decision: either exact reconstruction through a canonical constructor or
     an extraction-owned explicit source ID.
   - Keep referent identity, supplied value, value provenance, declaration, and concrete occurrence
     separate; do not encode them through binding-type mutation.
2. **Occurrence authority**:
   - Reuse the existing occurrence index and landed Item-10 redefinition machinery.
   - Absorb `[NESTED-OCCURRENCE-OVERRIDE]` so definition-relative captures resolve against
     occurrence-relative demands for both calculations and constraints.
   - Sequence with `[CONSTRAINT-ARCH-UNIFY]` sub-scope 2; consolidate only the portion required to
     prevent a second bridge or walker authority.
3. **Live/snapshot transport**:
   - Carry the chosen identity and occurrence evidence identically through live and relocated
     snapshot routes.
   - If forced by Item 2, bump the snapshot format/version with fail-closed old-version behavior and
     an explicit migration/recapture plan; do not add a silent compatibility shim.
4. **Foundation tests**:
   - Pin nested/flat siblings, multiple occurrences with different supplied values, specialization,
     per-child redefinitions, cycles/cardinality errors, and moved snapshot identity.

**Out of Scope**:
- VBR/materialization/backtracking cutover; Item 5 consumes this foundation.
- Whole-corpus recapture and generated-package migration; Item 6 owns them.
- The remaining `[CONSTRAINT-ARCH-UNIFY]` sub-scopes unrelated to source occurrence identity.

**Success Criteria**:
- [ ] Every supported model-derived binding carries one exact semantic source occurrence into the
  pre-resolution boundary on both live and relocated-snapshot paths.
- [ ] The nested-occurrence fixture applies `80.0` on calculation and constraint paths, its tripwire
  goes silent, and its flat sibling retains the same semantics.
- [ ] Two occurrences of one declaration remain distinct when the model supplies distinct values;
  consumers of one occurrence still converge.
- [ ] No second occurrence→definition bridge, instance walker authority, or consumer-specific source
  identity exists.
- [ ] Snapshot versioning and recapture obligations match the Item-2 verdict and fail closed on
  incompatible evidence.
- [ ] Focused unit/conformance tests and maintained lint/type gates pass with no unreviewed output
  changes.

**Estimated Effort**: 3–4 days (spec 2h, design 4h, plan 2h, execute/validate 16–24h)

**Location**: `.project/active/source-identity-occurrence-foundation/`

**Dependencies**: Item 3 complete.

**Required Reading**:
- Item 2 evidence-sufficiency verdict and adjacent-work register.
- Item 3 contract, requirements, and acceptance matrix.
- `[NESTED-OCCURRENCE-OVERRIDE]`, its archived tripwire evidence, and fixture provenance.
- Lifecycle Item-10 design/evidence/audit and `[CONSTRAINT-ARCH-UNIFY]` sub-scope 2.

**Deliverables**:
- `.project/active/source-identity-occurrence-foundation/spec.md`
- `.project/active/source-identity-occurrence-foundation/design.md`
- `.project/active/source-identity-occurrence-foundation/plan.md`
- `.project/active/source-identity-occurrence-foundation/evidence.md`
- Production identity/occurrence implementation and focused tests.
- Snapshot schema/version and migration artifacts if required by Item 2.

---

#### Item 5: Unified Materialization and Backtracking Cutover (3–5 days)

**Type**: Code / Integration

**Objective**: Make calculation, constraint, and aggregation consumers resolve through the same
semantic source identity and remove consumer-local fan-out behavior.

**Current State**:
- ✅ The unified producer resolver handles several exact-QN and source-QN convergence routes.
- ⚠️ Virtual-binding rewrite can convert a reference into a consumer-local literal and clear its
  source path before the resolver runs.
- ⚠️ Lenient terminal fallback can mint a consumer-local public input for a bound model reference.
- ❌ Path-specific rescues, materialization rules, and literal arms allow one semantic source to
  become several runtime sources.

**Scope**:
1. **Reference/value separation**:
   - Preserve semantic referent identity while applying a supplied literal/default value.
   - Ensure a reference-derived value cannot become `USAGE_LITERAL`; preserve genuinely authored,
     independent literals as distinct sources.
2. **One consumer resolution route**:
   - Route calculation inputs, constraint actuals, and aggregation terms through the Item-4 identity
     and the shared producer/design-input selection contract.
   - Converge consumers on one public input for an externally supplied source or one producer channel
     for a computed source.
3. **Terminal policy and diagnostics**:
   - Allow entry-point minting only for an explicit supported external-input contract.
   - Reject unsupported, ambiguous, or invalid bound references with the Item-3 diagnostic; strict
     versus lenient policy may change failure handling, never semantic identity.
4. **Superseded-route deletion**:
   - Remove or reduce VBR source clearing, self-named rescue, per-consumer minting, and other parallel
     behavior made obsolete by the authoritative path.
   - Replace wrong-oracle tests with independently anchored topology and mutation tests.
5. **Adversarial semantic tests**:
   - Cover both known fan-out paths, distinct literals with equal values, same-leaf ambiguity,
     aggregation asymmetry, multi-consumer mixed types, and off-default mutation.

**Out of Scope**:
- Bulk snapshot/baseline/package migration; Item 6 owns reviewed forced changes.
- Downstream study/store migration; Item 7 owns it.
- A key-dedup pass that does not repair upstream provenance.

**Success Criteria**:
- [ ] The accepted customer form produces one runtime source; public mutation reaches every and only
  its calculation, constraint, and aggregation consumers.
- [ ] Both historical fan-out paths converge or fail according to the Item-3 authoring-form policy;
  neither silently mints consumer-local fields.
- [ ] Equal-valued but independently authored literals remain distinct, and same-source references
  with different consumer names converge.
- [ ] Legitimate explicitly declared external inputs still mint ordinary typed entry points.
- [ ] Superseded path-specific identity/rescue code and wrong-oracle tests are deleted or reduced to
  non-semantic adapters with one authority.
- [ ] Focused and broad unit/conformance suites, lint, and zero-new type gates pass; every output
  change is handed to Item 6's semantic-diff ledger.

**Estimated Effort**: 3–5 days (spec 2h, design 4–6h, plan 2h, execute/validate 16–30h)

**Location**: `.project/active/source-identity-resolution-cutover/`

**Dependencies**: Item 4 complete.

**Required Reading**:
- Item 3 contract/acceptance matrix and Item 4 implementation evidence.
- Both forensic reports' failure mechanisms and wrong-oracle test findings.
- VBR, supplied-value, producer-resolution, backtracking, graph-builder, and snapshot-rebuild
  reference docs and tests.

**Deliverables**:
- `.project/active/source-identity-resolution-cutover/spec.md`
- `.project/active/source-identity-resolution-cutover/design.md`
- `.project/active/source-identity-resolution-cutover/plan.md`
- `.project/active/source-identity-resolution-cutover/evidence.md`
- Unified production resolution/materialization implementation and adversarial tests.
- Deletion register for superseded mechanisms and tests.

---

#### Item 6: Semantic Corpus Migration and Public Acceptance (2–4 days)

**Type**: Testing / Integration

**Objective**: Prove the corrected semantics over the whole codegen corpus and migrate every forced
artifact change under a source-identity review rather than byte-preservation assumptions.

**Current State**:
- ✅ The repository has a large fixture, snapshot, generated-graph, and package test corpus.
- ⚠️ Several baselines encode per-consumer fan-out as ground truth, and some acceptance tests bless
  one-copy mutation.
- ❌ No final census accounts for every entry point by semantic source occurrence.

**Scope**:
1. **Final semantic-source census**:
   - Re-run Item 2's census against the corrected pipeline and account for every entry point and
     producer channel.
   - Classify every former duplicate, legitimate independent source, rejected form, and unresolved
     gap; zero silent unknowns are allowed at certification.
2. **Independent acceptance matrix**:
   - Implement kept source-to-public-boundary tests for every supported/rejected Item-3 matrix cell.
   - Derive expected source topology from fixtures/contract, never from generated key populations or
     the resolver under test.
3. **Reviewed artifact migration**:
   - Recapture snapshots, graph baselines, parameter schemas, contracts, and generated packages only
     after producing a per-source semantic diff ledger.
   - Separate forced semantic changes from unrelated capture drift and stale-baseline debt.
4. **Customer and regression acceptance**:
   - Keep the exact customer composition on live and relocated-snapshot routes with topology plus
     execution mutation proof.
   - Retain nested occurrence, Item-10 rollup, direct PartUsage, dotted cross-part, independent
     literal, ambiguity, and negative unsupported-form cases.
5. **Repository gates**:
   - Run the complete maintained codegen suites and generation checks; record license proof and
     reviewed output changes.

**Out of Scope**:
- Fusion Tea/Stellarator study reruns and store migration; Item 7 owns downstream evidence.
- Treating an old/new byte match as proof for a semantic cell.
- Opportunistic cleanup unrelated to forced identity/schema migration.

**Success Criteria**:
- [ ] The final census accounts for every generated input and producer channel with zero unexplained
  model-derived fan-out or unknown source identities.
- [ ] Every Item-3 matrix cell has independent live and relocated-snapshot topology, value, diagnostic,
  and mutation evidence as applicable.
- [ ] The customer acceptance proves one public input and mutation of every bound consumer, or the
  approved invalid form fails and its supported replacement proves convergence.
- [ ] Every committed snapshot/baseline/contract/package diff appears in the semantic-diff ledger and
  is classified as forced, pre-existing drift, or rejected unrelated change.
- [ ] Existing safe fixed-point calculations and legitimate external inputs retain their documented
  behavior.
- [ ] Full maintained codegen gates pass with exact revisions, pass/skip counts, and license evidence
  recorded.

**Estimated Effort**: 2–4 days (spec 1.5h, design 2h, plan 1.5h, execute/validate 11–27h)

**Location**: `.project/active/source-identity-corpus-acceptance/`

**Dependencies**: Item 5 complete.

**Required Reading**:
- Item 2 corpus census and matrix; Item 3 acceptance authority; Items 4–5 evidence/deletion register.
- Baseline capture rules, `SNAPSHOT_MODELS`, generation/package tests, and stale-baseline backlog
  records.
- Exact customer fixture/provenance and the Fusion Tea acceptance tests that blessed per-consumer
  mutation.

**Deliverables**:
- `.project/active/source-identity-corpus-acceptance/spec.md`
- `.project/active/source-identity-corpus-acceptance/design.md`
- `.project/active/source-identity-corpus-acceptance/plan.md`
- `.project/active/source-identity-corpus-acceptance/final-corpus-census.md`
- `.project/active/source-identity-corpus-acceptance/semantic-diff-ledger.md`
- `.project/active/source-identity-corpus-acceptance/evidence.md`
- Migrated fixtures/snapshots/baselines/contracts/packages and public acceptance tests.

---

#### Item 7: Downstream Study and Consumer Remediation (2–4 days)

**Type**: Integration / Research

**Objective**: Move real consumers and study evidence onto the corrected source-identity contract
without preserving fan-out through adapters or silently reusing incompatible lineages.

**Current State**:
- ✅ Fusion Tea and Stellarator packages run at their pinned design points, and the July IFE verdict
  comparison remains meaningful.
- ⚠️ Their generated packages contain affected duplicate fields, demo Item 5 is gated, and prior
  research proposed consumer-side fan-out expansion.
- ❓ It is not known whether downstream decisions consumed cost outputs that stayed frozen during the
  July IFE sweep.

**Scope**:
1. **Consumer artifact regeneration**:
   - Regenerate Fusion Tea and Stellarator packages/contracts against the corrected codegen pins.
   - Remove duplicate-field synchronization, fan-out expansion, or model reshaping used only to cope
     with upstream identity failure.
2. **Demo Item 5**:
   - Resume it fix-first on the corrected public package and prove the intended study varies one
     semantic parameter per modeled source.
3. **TEAx and lineage compatibility**:
   - Update joins, parameter IDs, package fixtures, or compatibility checks forced by corrected model
     contracts.
   - Start an explicit new study lineage whenever semantic/catalog/executable identity changes; no
     silent rebinding of prior cases.
4. **July IFE impact audit**:
   - Determine whether any downstream artifact or decision consumed LCOE/cost outputs from swept rows
     whose calculation inputs remained at the design point.
   - Rerun decision-relevant outputs or issue an explicit correction; preserve unaffected verdict
     evidence with its bounded claim.
5. **Adjacent real-model finding**:
   - Close or absorb the producer-channel/aggregation-scoping finding according to Item 2's register
     and prove the real model no longer needs value-preserving authoring adaptations for an upstream
     identity defect.

**Out of Scope**:
- New optimization strategies, study features, or model physics/economics changes.
- The two unrelated `agentic-mbse pm` CLI defects.
- Consumer adapters presented as certification evidence.

**Success Criteria**:
- [ ] Fusion Tea and Stellarator regenerate, seal, load, and execute with the corrected parameter
  topology and no identity workaround.
- [ ] Demo Item 5 uses one candidate field per modeled source and completes its public-path acceptance.
- [ ] TEAx accepts the corrected contracts through stock APIs and incompatible studies begin a new,
  explicitly linked lineage.
- [ ] The July IFE impact report names every cost-output consumer and records rerun/correction status;
  no affected decision remains mislabeled.
- [ ] Fixed-point numerical anchors remain unchanged except for separately approved model changes,
  while off-default mutations reach all intended consumers.
- [ ] The adjacent aggregation-scoping finding is closed, absorbed, or explicitly left separate with
  evidence that no competing source-identity mechanism remains.

**Estimated Effort**: 2–4 days (spec 1.5h, design 2h, plan 1.5h, execute/audit 11–27h)

**Location**: `.project/active/source-identity-downstream-remediation/`

**Dependencies**: Item 6 complete; access to the consumer repositories and their pinned environments.

**Required Reading**:
- Item 6 migrated contract, semantic-diff ledger, and acceptance evidence.
- Both forensic reports' blast-radius and IFE sections.
- Fusion Tea/Stellarator study failure research, demo Item-5 work, package pins, and store lineages.
- TEAx model/package compatibility and study-resume contracts.

**Deliverables**:
- `.project/active/source-identity-downstream-remediation/spec.md`
- `.project/active/source-identity-downstream-remediation/design.md`
- `.project/active/source-identity-downstream-remediation/plan.md`
- `.project/active/source-identity-downstream-remediation/ife-impact-report.md`
- `.project/active/source-identity-downstream-remediation/evidence.md`
- Updated consumer packages, contracts, tests, studies, and lineage records in their owning repos.

---

#### Item 8: Certification Repair and Composed Source-Identity Proof (2–3 days)

**Type**: Testing / Documentation

**Objective**: Correct the public and historical assurance record and certify the source-identity
invariant through one composed model-to-study artifact thread.

**Current State**:
- ✅ The two forensic reports name the wrong-oracle requirements, tests, plans, audits, and broad
  claims that require correction.
- ⚠️ README and architecture prose describe route mechanisms more clearly than the library's founding
  product invariant.
- ❌ No composed proof starts from an independently identified semantic source and follows an
  off-default mutation through generated package and study evidence.

**Scope**:
1. **Product and architecture documentation**:
   - State plainly that codegen backtracks each consumed modeled value to one runtime source and never
     invents independent study variables for bound consumer parameters.
   - Document supported/rejected authoring forms, occurrence identity, external inputs, diagnostics,
     snapshot behavior, and migration policy from the ratified contract.
2. **Certification correction**:
   - Correct or supersede the Fusion Tea one-copy perturbation, broad REQ-IR/REQ-SVM readings,
     verification-matrix status, Pipeline Truth conclusions, and other artifacts identified by the
     forensics.
   - Preserve historical provenance while preventing stale artifacts from acting as current authority.
3. **Composed public proof**:
   - Bind exact model/fixture, live and relocated-snapshot generation, graph/package contracts,
     generated parameter topology, TEAx load/evaluation, study candidate, and persisted evidence to
     one revision/artifact thread.
   - Include positive convergence, distinct-source non-collapse, unsupported-form failure, and
     off-default mutations with independently derived expectations.
4. **Release record**:
   - Run cross-repository maintained gates, verify all epic criteria/item evidence, and state the exact
     release/study-readiness boundary. No skipped or blocked mandatory cell is certified.

**Out of Scope**:
- Adding review stages or redesigning the global workflow.
- Unrelated documentation cleanup, code refactors, or consumer features.
- Declaring the epic complete while downstream Item-7 corrections or mandatory proof cells remain open.

**Success Criteria**:
- [ ] README and architecture docs state the governing product invariant and derive supported behavior
  from the ratified source-identity contract.
- [ ] Verification rows and historical certification records no longer present route-specific success
  as universal source-identity proof.
- [ ] One exact artifact thread proves source occurrence→runtime source→all consumers→TEAx candidate
  and persisted evidence on live and relocated-snapshot routes.
- [ ] Negative mutations prove the proof would fail for per-consumer fan-out, wrong occurrence,
  literal over-collapse, unsupported fallback, and stale study lineage.
- [ ] All eight item evidence records, full cross-repository gates, exact pins/locks, and forced semantic
  changes are reconciled in a release-readiness report.
- [ ] The final record says plainly which source-identity forms are certified and which remain
  unsupported or deferred.

**Estimated Effort**: 2–3 days (spec 1.5h, design 2h, plan 1h, execute/proof 11–19h)

**Location**: `.project/active/source-identity-certification/`

**Dependencies**: Items 6 and 7 complete. Documentation preparation may begin after Item 3, but the
composed proof and certification verdict wait for all predecessors.

**Required Reading**:
- Item 3 authority and Items 6–7 evidence.
- Both forensic reports, especially review-pipeline failures, confidence limits, and recommendations.
- Current README, architecture references, verification matrix, Pipeline Truth report, Fusion Tea
  acceptance spec/plan/audit, and lifecycle release records.

**Deliverables**:
- `.project/active/source-identity-certification/spec.md`
- `.project/active/source-identity-certification/design.md`
- `.project/active/source-identity-certification/plan.md`
- `.project/active/source-identity-certification/certification-correction-register.md`
- `.project/active/source-identity-certification/evidence-coordinate-register.md`
- `.project/active/source-identity-certification/release-readiness.md`
- Updated README, architecture, matrix, historical correction pointers, and composed proof tests.

---

## Dependencies

**External**:

- Owner dispositions, after the semantic spikes, for the complete authoring-form table, followed by
  amendment of the ratified lifecycle contract and companion spec.
- Licensed live SysIDE access for referent probes and public live-generation acceptance.
- Demo Item 5 remains gated on this epic's spikes and authority ruling. A consumer workaround cannot
  certify or substitute for the upstream fix.
- If any currently used form is rejected, coordinated migration of both in-house model corpora and
  affected customer models is required before their regenerated packages can certify the change.
- Coordinated artifact and compatibility updates in Fusion Tea, the Stellarator demo, and TEAx if
  generated parameter identities change.
- The queued Fusion Tea producer-channel/aggregation-scoping finding must be dispositioned against
  this epic's source-identity matrix during Stage 2; unlike the two `pm` CLI defects, it may be the
  same semantic family and may need absorption.

**Internal**:

- Existing producer-resolution, occurrence-index, supplied-value, backtracking, snapshot, contract,
  and package-generation surfaces.
- The outstanding `[NESTED-OCCURRENCE-OVERRIDE]` fix is in this epic's scope. Its shipped tripwire and
  fixture are evidence, not a parallel implementation path.
- The completed Lifecycle Item-10 per-child redefinition and transitive instance-routing work is
  substrate to reuse and audit, not an open second fix.
- `[CONSTRAINT-ARCH-UNIFY]` sub-scope 2 must be sequenced explicitly so this epic does not introduce a
  second part-structure index or occurrence→definition authority.
- The current fixture corpus and generated baselines as evidence to audit, not as semantic authority.

**Item Dependency Graph**:

```text
Item 1: Binding semantics spike ───────────────┐
                                               ├─> Item 3: Authoritative contract
Item 2: Route/evidence spike ─────────────────┘             │
                                                            v
                                      Item 4: Identity/occurrence foundation
                                                            │
                                                            v
                                      Item 5: Resolution cutover
                                                            │
                                                            v
                                      Item 6: Corpus/public acceptance
                                                            │
                                                            v
                                      Item 7: Downstream remediation
                                                            │
                                                            v
                                      Item 8: Certification/composed proof
```

Items 1 and 2 can run in parallel, but Item 2 cannot close its semantic synthesis without Item 1.
Item-8 documentation preparation may begin after Item 3. Its correction verdict and composed proof
remain dependent on Items 6 and 7.

---

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Designing against the wrong meaning of `in R = R` | High | Complete referent/language spikes and obtain an owner ruling before design. |
| A downstream key-dedup patch merges fields without repairing provenance | High | Prove source identity before value materialization and test public mutation, not key count alone. |
| Existing byte baselines block required semantic changes | High | Classify every diff by modeled source and require explicit semantic review of forced changes. |
| The known customer shape is only one member of a larger defect class | High | Audit a route matrix and the entire emitted corpus before claiming closure. |
| Existing occurrence-identity work produces a second bridge or index | High | Absorb the nested-override fix, reuse Item-10 machinery, and sequence explicitly against CONSTRAINT-ARCH-UNIFY sub-scope 2. |
| The owner ruling remains in an epic artifact instead of semantic authority | High | Amend the ratified contract, companion spec, and correction register before design approval. |
| Corrected input identities invalidate packages or studies silently | High | Bind migrations to contracts/fingerprints and start new study lineages when identity changes. |
| Another large artifact set creates confidence without proving the mission | High | Anchor acceptance on independently derived source identity and off-default mutation through public paths. |

---

## Timeline

**Total Effort**: 16–26 engineering days (roughly 3–5 weeks; re-estimate after Items 1–2)

| Item | Effort | Dependencies |
|------|--------|--------------|
| 1. Binding Semantics and Authoring-Form Spike | 1–2 days | None |
| 2. Source-Identity Routes and Evidence-Sufficiency Spike | 2–3 days | None to start; Item 1 to close |
| 3. Authoritative Source-Identity Contract | 1 day | Items 1–2 + owner checkpoint |
| 4. Semantic Identity and Occurrence Foundation | 3–4 days | Item 3 |
| 5. Unified Materialization and Backtracking Cutover | 3–5 days | Item 4 |
| 6. Semantic Corpus Migration and Public Acceptance | 2–4 days | Item 5 |
| 7. Downstream Study and Consumer Remediation | 2–4 days | Item 6 |
| 8. Certification Repair and Composed Source-Identity Proof | 2–3 days | Items 6–7 |

---

## Lessons Learned (Post-Completion)

*Fill in after epic is complete*

**What Went Well**:
- TBD

**What Could Improve**:
- TBD

**Surprises**:
- TBD

---

**Last Updated**: 2026-08-05
**Next Action**: Start Items 1 and 2 as parallel evidence work. No fix design begins before both close
and Item 3 records the owner dispositions in the ratified authority.
