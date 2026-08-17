# Spec: Elaborator Downstream Remediation and Certification

**Status:** Draft — spec-review resolutions incorporated; product lens `CLEAR`
**Owner:** Reid W
**Created:** 2026-08-16 18:35 PDT
**Complexity:** HIGH
**Branch:** `main` for specification; implementation branches are governed below

---

## Problem

ELABORATE-FIRST Item 8 cannot close because the customer package, study evidence, and assurance
record do not yet agree with the exact elaborate-then-project architecture. The
`self-binding-replacement` item is closed and independently verified. The active
`stop-reinventing-the-parser` item is now this work's entry gate: occurrence derivation and evidence
integrity must be corrected and certified before downstream regeneration establishes a new
assurance baseline. This item does not absorb either predecessor's remediation.

The committed downstream evidence still describes the pre-retirement Fusion Tea topology. The
post-R-2 shape — the customer model after July's duplicate-field workaround retirement — removes
the standalone `hif_driver_instance`. The sealed graph shows that occurrence feeds no downstream
consumer: deleting it removes two duplicate channels, moving the topology from eleven to nine,
without moving the LCOE calculation. Both the codegen fixture and customer model must now converge
on that one shape before the package and its acceptance pins can be certified.

The July IFE sweep contains decision-relevant outputs whose inputs did not sweep. The 2,294 of
2,301 feasibility-verdict matches remain bounded evidence, but swept-row LCOE and recirculation
values are design-point values. No complete record identifies which repository artifacts,
external reports, or decisions consumed affected outputs.

The assurance record also remains incomplete. There is no independently anchored source-identity
requirements family in the verification matrix. The Item-3 contract's cross-repository guidance
obligation has not been fully reconciled, README commands are stale, fourteen architecture
references need rewrite-or-retire dispositions, and document 25 needs its retained test-only role
stated accurately. Item 8 needs one composed model-to-study proof and one consistent historical
record before it can proceed to independent audit.

**[AGENT] (ratified by owner, 2026-08-16) Scope boundary:** Stellarator migration is not part of
this item. Its completed read-only triage and the separate P2 `[STELLARATOR-D5-MIGRATION]` are the
bounded disposition for Item 8 without reversing the July hold. Ratification is recorded in
`.project/active/elaborator-downstream/spec-review.md`, Resolutions L1-1/L1-2, with the provenance
grade corrected by the owner's subsequent instruction to apply the capture-fidelity rule.

## Success Criteria

- [ ] The migrated Fusion Tea customer model regenerates a package and model contract through the
      exact public route. The physical seal and semantic contract verify without editing generated
      bytes or substituting a hand-built package.
- [ ] The regenerated customer artifacts contain no identity adapter, duplicate-field
      synchronization, readiness-finding bypass, contract bypass, or standalone
      `hif_driver_instance` occurrence.
- [ ] The codegen Fusion Tea fixture deletes its legacy `hif_driver_instance` workaround and
      converges with the customer model on one measured post-R-2 parameter and channel topology.
- [ ] All affected fixture and customer acceptance pins identified by the spec review — projection
      wiring, fail-closed enum literals, and TEAx channel/arithmetic pins — are re-anchored to that
      measured topology.
- [ ] Stock TEAx APIs load and execute the regenerated, verified customer package and reproduce the
      fixed-point LCOE anchor `270.1211779380445` within its existing tolerance.
- [ ] A new composed model → sealed package → stock study proof changes an off-default modeled
      source and observes the change at every intended calculation, constraint, aggregation, and
      study consumer.
- [ ] The composed proof also observes that an independently anchored unrelated consumer does not
      change under that mutation.
- [ ] The new study lineage records an explicit link to its predecessor and binds its new
      eight-field compatibility identity.
- [ ] A compatibility check demonstrates that the prior store refuses the changed identity through
      TEAx's shipped `IncompatibleStore` behavior rather than silently rebinding old cases.
- [ ] A July IFE impact report names its repository and project-artifact census roots, identifies
      every consumer there of a decision-relevant output affected by the frozen design-point
      behavior, including LCOE, cost, and recirculation, and records each consumer as unaffected,
      rerun, corrected, or bounded-unknown.
- [ ] The impact report preserves the 2,294-of-2,301 feasibility-verdict claim at its original
      bound and does not relabel any frozen output as a swept result.
- [ ] The impact report records the owner's attestation about external reports and decisions.
      Unconfirmed external use remains an explicit bounded unknown rather than an inferred absence.
- [ ] The verification matrix gains an independently anchored `REQ-SI` requirements family derived
      from the durable `LC-SI-*` authority and Item-3 acceptance matrix. Its evidence includes the
      public every-and-only mutation behavior and the composed customer proof.
- [ ] The repaired assurance record preserves P-002's deep-override evidence bound and the separate
      `[ANCHORING-ARRAYED-DIAGNOSTIC]` follow-up rather than broadening either into a certified
      guarantee. Contradictory or overbroad claims are amended at their existing homes.
- [ ] A reconciliation record accounts for every certification and guidance obligation inherited
      from the Item-3 source-identity contract, citing certified predecessor evidence where it
      exists and assigning any remaining work here.
- [ ] The published `agentic-mbse` calculation-binding guidance covers the remaining Item-3
      projection: positive nested-definition and named-occurrence forms, the source-self-binding
      counterexample, the valid-but-unsupported indexed-expression limitation, and the
      definition/redefinition relationship, with example and referent force labeled accurately.
- [ ] README states the library's current purpose and gives working install, development, live
      generation, snapshot, and from-snapshot commands.
- [ ] Each of the fourteen historical or mixed reference documents identified by the Item 8
      stocktake is rewritten or formally retired with one current authority for shared claims.
- [ ] Reference document 25 accurately describes `extraction/hierarchy_resolver.py` as a retained,
      test-only, off-shipped-route legacy extractor. Neither the document nor its matrix rows imply
      that it governs public generation.
- [ ] A pre-work regression baseline records exact repository commits, commands, environment, and
      known failures. Final maintained and licensed results introduce no unexplained difference
      from that named baseline.
- [ ] Final evidence records exact commits and distinguishes newly run results from inherited
      evidence, leaving ELABORATE-FIRST Item 8 ready for independent audit and epic close.

## Known Requirements

The first requirement is the governing product outcome. The remaining rows bound the work and the
evidence needed to establish it.

- **[NEED]** One modeled source occurrence becomes exactly one runtime source across every bound
  calculation, constraint, and aggregation consumer. A public mutation reaches every consumer
  bound to that source and no others, and unsupported forms fail before generation. Absorbed from
  the parent epic's `[OWNER]` mission invariant in
  `.project/backlog/epic_elaborate_first_architecture.md`, “Success Criteria.”
- **[NEED]** Regeneration and proof, the July impact audit, and certification/documentation repair
  remain one Item 8 work item. The internal plan may phase them, but it does not split their
  completion authority. Source: `.project/active/elaborator-downstream/spec-review.md`, Resolution
  L2-1.
- **[INFERRED]** Stellarator receives no edits in this item. The completed triage plus the separate
  `[STELLARATOR-D5-MIGRATION]` P2 is the boundary disposition. This was an agent recommendation
  ratified by the owner on 2026-08-16; the review records that ratification at Resolutions
  L1-1/L1-2.
- **[INFERRED]** The July impact claim is bounded by an explicit repository/project-artifact census
  of every affected decision-relevant output and consumer, plus owner attestation for external
  consumers. Unknown external use remains named. This was an agent recommendation ratified by the
  owner on 2026-08-16; see the review's Resolutions L1-1/L1-2 and the first product-lens finding.
- **[NEED]** This item performs none of the `self-binding-replacement` audit remediation. Its
  implementation starts from that sibling's independently certified head; a later audit finding
  can block any dependent evidence without moving the repair into this item. Source:
  `.project/active/elaborator-downstream/spec-review.md`, Resolution L3-1.
- **[INFERRED]** (agent recommendation ratified by owner, 2026-08-16) Design and implementation wait
  for `stop-reinventing-the-parser` to close. Downstream evidence must certify the final
  occurrence-derivation and extraction-integrity rules, not the behavior this predecessor is
  replacing. Source: `.project/active/stop-reinventing-the-parser/spec-review.md` L4-1 and the
  owner's direction to apply the resulting spec fixes; the dependency remains agent-grade.
- **[NEED]** Fusion Tea implementation uses a new `elaborator-downstream` branch created from the
  certified head of its `self-binding-replacement` branch. The current candidate is `7703ba1e`; if
  re-audit changes the head, the certified head replaces that candidate. Source: spec-review
  Resolution L2-3, with the base made exact from the inspected branch topology.
- **[NEED]** The codegen fixture and customer model converge on the one measured post-R-2 topology.
  The fixture's legacy standalone `hif_driver_instance` is deleted rather than preserved as a
  second acceptance surface. Source: spec-review Resolution L2-2.
- **[INFERRED]** Certification mints an independently anchored `REQ-SI` family derived from the
  durable `LC-SI-*` requirements and Item-3 acceptance authority. This agent recommendation was
  ratified by the owner on 2026-08-16 after the review identified the requirements-stage decision.
- **[INFERRED]** `extraction/hierarchy_resolver.py` and reference document 25 remain as a test-only,
  off-shipped-route legacy surface in this item. Deletion requires a later equivalence-backed
  retirement decision. This agent recommendation was ratified by the owner on 2026-08-16.
- **[INHERITED]** This item absorbs the still-open downstream and certification work from the
  SOURCE-IDENTITY remainder: Fusion Tea regeneration, stock-API TEAx execution and lineage, July
  impact audit, assurance correction, documentation repair, and the composed proof. Sources:
  `.project/completed/20260810_epic_semantic_source_identity.md`, downstream remediation and
  certification items, and `.project/research/20260815-103905_item8-bounded-stocktake.md`.
- **[HARD]** The exact `InstanceGraph` route is the only public generation authority. Live models
  and v6 snapshots are two sources for that authority; v5 and the deleted string-resolution stack
  cannot be used as compatibility routes. Source: `CLAUDE.md`, “Processing Pipeline” and
  “Retired — read before trusting a document.”
- **[HARD]** TEAx binds a study store to eight values: study ID, executable fingerprint,
  model-contract fingerprint, study-definition fingerprint, input-schema version, evidence-schema
  version, strategy identity, and strategy configuration. Reopening with any differing bound value
  raises `IncompatibleStore` and requires a new store path. Source:
  `/home/reid/1cfe/teax/packages/teax-simkit/simkit/study/compatibility.py` and `study/cli.py`.
- **[HARD]** A generated package is consumed only after its physical seal and semantic model
  contract verify. The proof may not edit generated bytes or substitute a hand-built package
  between generation and TEAx loading. Source: `CLAUDE.md`, pipeline steps 4–5, and
  `/home/reid/1cfe/teax/packages/teax-simkit/simkit/evaluation/package_load.py`.
- **[HARD]** Licensed SysIDE-dependent results count as evidence only when the repository's license
  environment is loaded. An unlicensed skip, collection failure, or false baseline is not a pass.
  Source: project test configuration and the pre-existing licensed-test instructions recorded in
  `.project/CURRENT_WORK.md`.
- **[INHERITED]** R-2 retired the customer model's duplicate `hif_driver_instance` workaround. The
  sealed graph now proves that occurrence is inert and its two channels duplicate the canonical
  plant-driver channels. Sources: `.project/active/fusiontea-acceptance/{spec,plan,audit}.md`,
  `.project/active/self-binding-replacement/design.md` decision D8, and spec-review L1-5/L2-2.
- **[INHERITED]** The July feasibility claim is 2,294 of 2,301 exact verdict matches, with seven
  model-favoring boundary corrections. That claim is about verdicts; it does not validate LCOE or
  recirculation as swept outputs. Sources:
  `.project/completed/20260713_epic_constraint_execution.md` and the two 2026-08-03 forensic
  reports.
- **[INHERITED]** Documentation repair covers reference documents 03, 04, 05, 07, 09, 10, 11, 12,
  13, 16, 17, 18, 24, and 28. Source:
  `.project/research/20260815-103905_item8-bounded-stocktake.md`, “Reconciled document-repair
  list.” Document 25 is a separate retained-surface disposition, not a fifteenth rewrite.
- **[INHERITED]** Item 3 assigns Item 8 the cross-repository guidance projection, including the
  indexed-expression limitation and accurate example force, and requires certification to inherit
  its acceptance authority. Source:
  `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md`, “Validation and
  guidance obligations,” and
  `.project/concepts/constraint-execution-lifecycle-requirements.md`, `LC-SI-15` through
  `LC-SI-23`.
- **[INHERITED]** P-002 does not evidence the deep-literal-override lane, and its arrayed-owner
  spelling inconsistency remains under `[ANCHORING-ARRAYED-DIAGNOSTIC]`. This item preserves both
  bounds. Source: `.project/product/P-002-exact-owner-anchoring.md`, “The bound” and “Known
  inconsistency, dispositioned.”
- **[INFERRED]** The source-identity matrix family and every-and-only proof must be anchored
  independently of the implementation they certify. Implementation discovery or expected output
  cannot serve as both oracle and evidence.
- **[INFERRED]** Regression claims compare the same maintained and licensed commands, environment,
  and repository set before and after this item. The baseline records existing failures, including
  ordering-dependent failures, rather than silently treating them as new or green.

## Non-Goals

- Migrating or repairing the Stellarator demo; that remains `[STELLARATOR-D5-MIGRATION]`, P2 and
  separately authorized.
- Repairing, extending, or re-auditing `self-binding-replacement` or
  `stop-reinventing-the-parser`; this item starts only after both predecessors close and performs no
  remediation on their behalf.
- Restoring `hif_driver_instance`, reintroducing duplicate-field synchronization, reviving a legacy
  resolver route, or adding a consumer adapter to make old evidence pass.
- Changing model physics, economics, fixed design inputs, constraint policy, search strategy, or
  optimization capability. Any numerical change beyond corrected propagation or required lineage
  separation needs its own authorized item.
- Implementing calculation-definition gates, acausal relation solving, the CATF cryogenic fix, or
  the arrayed-owner diagnostic follow-up.
- Deleting `extraction/hierarchy_resolver.py` or presenting its test-only requirements as shipped
  public behavior.
- Pushing branches, opening or merging pull requests, closing Item 8, or closing ELABORATE-FIRST.
  Those actions follow this item's audit through the normal close and branch-gate stages.

## Open Questions / Deferred to design

- Enumerate the exact repository branches, study stores, reports, handoffs, and project-artifact
  roots that form the July IFE census before the audit runs. The census and owner-attestation
  outcomes are fixed; the mechanically searchable root list is design work.
- Map the approved `REQ-SI` family onto the durable `LC-SI-*` requirements and Item-3 acceptance
  coordinates without duplicating or weakening either authority.
- Choose rewrite versus formal retirement for each of the fourteen reference documents. Shared
  live explanations should have one authority rather than fourteen synchronized copies.
- Choose the owning locations and naming for regenerated Fusion Tea package/contracts, the linked
  study lineage, the impact report, the Item-3 reconciliation record, and composed proof evidence.
  Existing user worktrees and historical stores must remain untouched.
- Phase the single work item so regeneration/proof, impact auditing, and documentation/certification
  can receive focused validation without splitting Item 8's completion authority.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_elaborate_first_architecture.md` — ELABORATE-FIRST Item 8
- **Required Reading:** Item 8 lists none explicitly. Its inherited source documents are the parent
  epic's “Source Documents,” especially the SOURCE-IDENTITY contract and the two 2026-08-03
  forensic reports.
- **Scope stocktake:** `.project/research/20260815-103905_item8-bounded-stocktake.md`
- **Spec review:** `.project/active/elaborator-downstream/spec-review.md`
- **Predecessors:** `.project/completed/20260816_self-binding-replacement/` and
  `.project/active/stop-reinventing-the-parser/spec.md`
- **Absorbed ancestor:** `.project/completed/20260810_epic_semantic_source_identity.md`, downstream
  remediation and certification items
- **Item-3 authority:** `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md`
  and `.project/concepts/constraint-execution-lifecycle-requirements.md`
- **Forensics:** `.project/research/20260803-203011_entry-surface-fanout-forensics.md` and
  `.project/research/20260803-202453_backtracking-fanout-forensics.md`
- **Prior composed proof:** `.project/completed/20260814_cutover-recovery/plan.md`, Slice 3D
- **Product promises:** `.project/product/P-001-design-search-free-variation.md` and
  `.project/product/P-002-exact-owner-anchoring.md`
- **Product lens:** `.project/active/elaborator-downstream/product-lens.md`
- **Design:** `.project/active/elaborator-downstream/design.md` (to be created)

---

**Next Steps:** After `stop-reinventing-the-parser` closes, proceed to `$my-design`.
