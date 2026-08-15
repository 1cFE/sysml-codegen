# Spec: Authoritative Source-Identity Contract

**Status:** Complete (decision checkpoint resolved 2026-08-05; implementation landed;
2026-08-07 audit certified and owner-ratified)
**Owner:** Reid W
**Created:** 2026-08-05
**Complexity:** HIGH
**Branch:** `source-identity-epic`

---

## Problem

`sysml-codegen` exists to trace each modeled value consumed by calculations, constraints, and
aggregations back to its actual runtime source. A design-space study must vary that source once and
reach every consumer of it. The current pipeline can instead turn one modeled value into several
consumer-local inputs that happen to share the same default value.

The most damaging route starts with `in R = R`. KerML resolves the right-hand `R` to the calculation
usage's own parameter, so the model contains a legal but inert self-binding. Codegen has nevertheless
searched outward for a same-named feature and treated that unrelated feature as the intended source.
The `agentic-mbse` L2 validator encodes the same workaround: it suppresses its self-binding error
when a same-named outer feature exists (`level2_structure.py:309-421`). This reverses the meaning
supplied by SysIDE/KerML and teaches model authors that a modeling error is supported.

The valid alternatives have distinct meanings. A bare renamed parameter whose right-hand name
resolves outward and an owner-qualified reference identify the definition feature; an
occurrence-rooted chain identifies the feature at the named occurrence. Current requirements,
validation, resolution routes, and verification rows do not carry those distinctions consistently
through concrete occurrence identity and the public study boundary.

Item 3 must establish one authoritative behavioral contract before a fix is designed. It must say
which authored forms mean what, which forms the executable subset supports, what constitutes one
semantic source occurrence, and what every consumer and public mutation must observe. It must also
correct the authoring-validation and documentation obligations so a later implementation cannot
restore the same workaround under a different name.

## Success Criteria

- [x] A provenance-graded source-identity disposition table covers every observed authoring form
  and every remaining source class without treating approval of an agent recommendation as owner
  origin.
- [x] The ratified lifecycle contract, its durable companion requirements, and its correction
  register state one consistent source-identity contract and identify every superseded reading
  relevant to this defect.
- [x] An authoritative acceptance matrix and evidence coordinate define source topology,
  occurrence behavior, value provenance, diagnostics, and off-default mutation outcomes for every
  supported, rejected, deferred, and language-rejected class across calculation, constraint, and
  aggregation consumers.
- [x] The current verification rows that certify consumer-local minting, rescue, or route-specific
  convergence are marked partial, failed, or superseded until implementation evidence satisfies the
  new matrix.
- [x] The downstream validation and `agentic-mbse` modeling-guidance obligations are explicit,
  testable, and assigned; neither codegen nor documentation may teach self-binding reinterpretation.
- [x] Items 4 and 5 can derive their specifications without choosing new language semantics, source
  identity, terminal fallback, or consumer-specific behavior.

## Known Requirements

### Language fidelity and authoring forms

- **SI-01 [NEED]** The supported toolchain must never reinterpret a self-binding as an outer
  reference. Source:
  owner, 2026-08-05: “Never reinterpret a self-binding as an outer reference.”
- **SI-02 [HARD]** The semantic referent is the element selected by KerML name resolution and exposed
  by SysIDE. For `in R = R`, that element is the calculation usage's own input parameter; the
  expression is a legal, inert self-binding and supplies no enclosing feature. Source: Item-1
  licensed probes and KerML 1.0 §8.2.3.5 and §7.4.11.
- **SI-03 [INFERRED]** A bare renamed parameter reference such as `in r_in = R`, an owner-qualified
  reference, and an occurrence-rooted feature chain are supported according to the referent SysIDE
  supplies. Binding-owner context is semantic key material: in the observed definition-context
  forms, bare-renamed and definition-qualified references identify the definition feature; in the
  observed concrete-usage context, bare-renamed and usage-qualified references identify the
  occurrence feature. A chain identifies the feature reached through its named occurrence. None of
  these forms is reinterpreted as another. Agent recommendation ratified by owner, 2026-08-05;
  Item-1 referent probes and Item-2 snapshot referent evidence.
- **SI-04 [HARD]** A `:>>` feature is a distinct redefinition that replaces the redefined feature in
  its concrete context. A default on the definition applies when each featuring instance is
  constructed unless that occurrence supplies an override. Source: SysML v2 Part 1 §§7.6 and
  7.13.4; Item-1 `owned_redefinitions` evidence.
- **SI-05 [INFERRED]** When a definition feature is instantiated at more than one concrete
  occurrence and the model does not bind those occurrences to one shared source, each occurrence is
  a distinct semantic source occurrence. If externally supplied, each is a distinct public study
  input even when the occurrences inherit equal defaults. Equal values do not collapse identity;
  an explicit modeled relationship is required to share a source. Agent recommendation ratified by
  owner, 2026-08-05; resolution of spec-review finding L1-2.
- **SI-06 [INFERRED]** `plants#(1).R` is unsupported as a source-bearing calculation binding in this
  epic. It is a legal indexed value expression, not an occurrence feature identity, and must not be
  flattened to `R` or represented as a direct source reference. Agent recommendation ratified by
  owner, 2026-08-05.
- **SI-07 [HARD]** `plants[1].R` is not KerML indexing. It uses the bracket operator and fails to
  resolve in the observed SysML environment; normal language/load diagnostics govern it. Source:
  KerML 1.0 §8.2.5.8.2 and Item-1 licensed probe.
- **SI-07a [INFERRED]** General expression bindings used where execution requires source feature
  identity are deferred in this epic. Authoring validation and codegen must fail closed with a
  distinct codegen-readiness diagnostic; they may not flatten the expression or invent a source.
  Agent recommendation ratified by owner, 2026-08-05; Item-2 census expression class.

### Semantic source and public behavior

- **SI-08 [INHERITED]** Every supported model-derived consumed value carries one extraction-owned
  semantic source identity containing both declaration identity and concrete occurrence identity.
  Reconstruction from current owner/name fields is not an accepted authority. Source: Item-2
  evidence-sufficiency verdict; reconstruction failed 40 of 75 measured model-derived mint cells.
- **SI-09 [NEED]** One semantic source occurrence produces one runtime source. Every and only
  its calculation, constraint, and aggregation consumers resolve to that source. Consumer parameter
  names, count, placement, and strictness do not create new source identity. Source: epic governing
  mission invariant `[OWNER]`; lifecycle invariants 19, 20, and 26.
- **SI-10 [INFERRED]** The queued Fusion Tea producer-channel/aggregation-scoping finding belongs to
  this same contract. Aggregation terms may not use a separate terminal-mint or identity rule.
  Agent recommendation ratified by owner, 2026-08-05.
- **SI-11 [INHERITED]** Independently authored literals remain independent sources even when their
  names or values are equal. A library default is not automatically selected as a study variable.
  Source: Item-2 discriminator evidence and lifecycle invariant 22.
- **SI-11a [INFERRED]** An unbound calculation-definition input default creates one independently
  overridable `LIBRARY_DEFAULT` source per concrete calculation usage; it is not shared without an
  explicit modeled relationship. Agent recommendation ratified by owner, 2026-08-05; Item-2 RM 11
  and ADR-001 behavior.
- **SI-12 [INHERITED]** Strict versus lenient policy changes only the disposition of a genuine
  terminal miss. It cannot change referent identity, select a same-named candidate, or mint a
  consumer-local input for a bound model reference. Source: lifecycle invariants 19, 20, and 26.
- **SI-13 [INHERITED]** Live extraction, in-place snapshot replay, and relocated snapshot replay must
  transport and resolve the same semantic source identity. The new identity evidence requires a
  snapshot format/version bump, fail-closed older versions, coordinated capture/rebuild changes,
  and recapture of the 37-fixture corpus. Source: Item-2 route and parity findings.
- **SI-14 [INHERITED]** Acceptance is established at the public boundary by off-default mutation:
  changing one source changes every intended consumer and no independent source. Fixed-point value
  equality and entry-key counts are insufficient evidence. Source: epic success criteria and both
  forensic reports.

### Authoring validation and modeling guidance

- **SI-15 [NEED]** The `agentic-mbse` validation stack must report a blocking, actionable diagnostic
  when a consumed calculation input's value expression resolves to that same input parameter. A
  same-named outer attribute or sibling output does not suppress the diagnostic. The current
  rescue-aware exemption and its wrong-oracle tests must be corrected. Source: owner, 2026-08-05:
  “Can we add that (and probably the `in.R=R`) pattern in the agentic-mbse validation stack?” Here
  `in.R=R` denotes the discussed `in R = R` self-binding form.
- **SI-16 [NEED]** The `agentic-mbse` codegen-readiness validation must report a distinct blocking
  diagnostic when an indexed value expression is used where the supported executable path requires
  source feature identity. The message states that the SysML expression is valid but unsupported by
  this executable subset; it must not call the expression invalid SysML. Source: owner, 2026-08-05:
  “agree with classifying that as unsupported. Can we add that (and probably the `in.R=R`) pattern
  in the agentic-mbse validation stack?”
- **SI-17 [INHERITED]** Codegen enforces these conditions unconditionally and independently of
  whether authoring validation ran. Validation diagnostics improve author feedback; they are not
  mutable semantic decisions passed into codegen. Source: ratified lifecycle stage-ownership
  contract.
- **SI-18 [NEED]** `agentic-mbse` must document the allowable calculation-binding patterns as a
  modeling question, including what each accepted and rejected form means in KerML/SysML and how
  SysIDE exposes it. Source: owner, 2026-08-05: “we MUST document allowable patterns in our
  `agentic-mbse` docs as well. This is a "how do you model correctly" quesiton, not a "what should
  sysml-codegen do" question...”
- **SI-19 [INFERRED]** The guidance includes positive nested-definition and named-occurrence examples,
  the source-self-binding counterexample, the indexed-value-expression limitation, and the
  definition/redefinition relationship. Examples are labeled by force and do not present one valid
  topology as the universal required model shape.

### Authority, corrections, and simplification

- **SI-20 [INHERITED]** The ratified lifecycle contract and durable companion requirements must
  amend invariants 19, 20, 22, and 26 with the same definitions and provenance grades used here.
  Their correction register must identify the superseded self-binding rescue, consumer-local
  lenient mint, literal stamp, group-deriver value backfill, and route-specific convergence
  readings. Source: epic Item 3.
- **SI-21 [INHERITED]** The authoritative acceptance matrix supersedes contradictory broad readings
  of REQ-BT-13, REQ-CL-05, REQ-IR-01/06/07, REQ-PGD-06, REQ-SVM-01/02/04, and
  REQ-VBR-03/10. Historical tests remain evidence of old behavior, not certification of the new
  contract. Source: epic Item 3 and forensic correction registers.
- **SI-22 [INHERITED]** Downstream design must leave one authority for semantic identity and one
  occurrence-to-definition bridge. Parallel VBR rescue, supplied-value synthesis, backtracking
  fallback, aggregation fallback, and parameter-group value repair may only remain as non-semantic
  adapters derived from that authority or be deleted. Source: Item-2 adjacent-work register and the
  ratified simplification constraint.
- **SI-23 [INHERITED]** The authoritative acceptance matrix must publish a complete evidence
  coordinate for every cell: cell ID; authored form; semantic referent; declaration identity;
  concrete occurrence; override/default state; consumer type and count; form disposition; expected
  boundary outcome; expected public-source topology; diagnostic disposition; execution routes;
  off-default mutation result; certification state and owed-evidence owner; and citations.
  Downstream item specs inherit these coordinates rather than inventing narrower proof standards.
  Source: epic Item 3 acceptance authority and the lifecycle contract proof standard.

## Non-Goals

- Implementing the `agentic-mbse` validators, codegen source identity, snapshot migration, resolver
  cutover, or corpus regeneration in Item 3.
- Rewriting the approximately 124 external and 91 fixture self-binding occurrences before the
  contract and migration ledger exist.
- Adding general indexed-expression execution or inventing occurrence feature identity for a value
  expression.
- Choosing source-ID field names, serialization layout, diagnostic enum names, or the internal
  occurrence-index API.
- Redesigning the global validation pipeline or adding review stages.
- Publishing all public documentation in Item 3; Item 8 owns the required cross-repository
  projection from this contract.

## Resolved decisions and downstream deferrals

- `[AGENT]` (ratified by owner, 2026-08-05): an unbound calculation-definition input default creates
  one independently overridable `LIBRARY_DEFAULT` source per concrete calculation usage.
- `[AGENT]` (ratified by owner, 2026-08-05): general expression-source support is deferred in this
  epic. The supported executable boundary fails closed with a distinct readiness diagnostic.
- `[AGENT]` (ratified by owner, 2026-08-05): the customer migration uses bare-renamed bindings in
  place. Audit evidence corrected the context premise: C25 owns availability's exact mixed
  usage/definition-authored outcome, C2 owns the definition-authored thermal-efficiency outcome,
  and C4 remains usage-context referent evidence. The corrected cell placement remains agent-grade;
  the assembled table was owner-ratified on 2026-08-07 without changing provenance grades.
- The concrete source-ID type, canonical constructor, and snapshot representation are deferred to
  Item 4 design. The identity must still carry declaration plus concrete occurrence.
- Machine-readable diagnostic codes are deferred to downstream implementation design. The existing
  L2 self-binding check is the correction point; indexed and general expression-source rejection
  belong to codegen-readiness validation. Severity and fail-closed outcomes are not deferred.
- The exact `agentic-mbse` documentation file and navigation placement are deferred to Item 8. The
  required semantic content and examples are not deferred.
- The mechanical migration for each affected corpus occurrence is deferred to Item 6. Migration may
  choose either supported form only when that form expresses the model's intended topology and
  referent.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_semantic_source_identity.md`
- **Required Reading:**
  - `.project/active/source-identity-binding-semantics-spike/authoring-form-table.md`
  - `.project/active/source-identity-binding-semantics-spike/findings.md`
  - `.project/active/source-identity-route-evidence-spike/route-matrix.md`
  - `.project/active/source-identity-route-evidence-spike/findings.md`
  - `.project/active/source-identity-route-evidence-spike/corpus-census.md`
  - `.project/active/source-identity-route-evidence-spike/adjacent-work-register.md`
  - `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md`
  - `.project/completed/20260720_constraint-execution-lifecycle-contract/spec.md`
  - `docs/architecture/verification-matrix.md`
- **Research:** `.project/research/20260805-054752_source-identity-route-evidence.md`
- **Standards evidence:**
  - `.project/active/source-identity-binding-semantics-spike/standards/kerml_ruling.md`
  - `.project/active/source-identity-binding-semantics-spike/standards/sysml_ruling.md`
- **Existing validation seam:**
  `../agentic-mbse/src/agentic_mbse/validation/level2_structure.py`
- **Design:** `.project/active/source-identity-contract/design.md`

---

**Next Steps:** Item 3 is complete. Item 4 specifies and implements the semantic-identity and
occurrence foundation against this contract.
