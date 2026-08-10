# Spec: Semantic Identity and Occurrence Foundation

**Status:** Superseded (2026-08-07; archived 2026-08-10) — the Item-4 architecture was
stopped after Phases 1–2 and replaced by the elaborate-first front end
(`.project/backlog/epic_elaborate_first_architecture.md`); salvage landed via
ELABORATE-FIRST Item 2. See `plan.md` banner and the supersession record in the archived
SOURCE-IDENTITY epic.
**Owner:** Reid W
**Created:** 2026-08-07
**Complexity:** HIGH
**Branch:** `source-identity-epic`
**Epic Item:** SOURCE-IDENTITY Item 4

---

## Problem

`sysml-codegen` cannot reliably resolve one modeled value to one runtime source until the value has
an exact identity before consumer resolution begins. The ratified source-identity contract defines
that identity as the modeled declaration plus its concrete occurrence. Current extraction and
snapshot data instead move referents through raw strings, written-name hints, definition-relative
records, and consumer-relative scope projections. Item-2 evidence showed that reconstructing an
exact source from those fields fails for 40 of 75 measured model-derived cells where the pipeline
creates a consumer-local public input (a "mint").

The missing occurrence relationship already causes a concrete value-loss defect. A `:>>` override
captured relative to a nested definition does not match the same feature demanded relative to an
instantiated occurrence. The modeled value `80.0` is therefore lost for both calculation and
constraint consumers. A shipped tripwire reports the mismatch but deliberately does not repair it.

Snapshot capture makes the loss durable. It serializes the post-rewrite binding state after source
paths may have been cleared, while replay has no equivalent rewrite stage from which it could
recover the original identity. Current version-5 snapshots do not contain the explicit
declaration-plus-occurrence evidence required by the ratified contract.

This item establishes the identity and occurrence foundation shared by later resolution work. It
must publish exact source identity during extraction, carry it through live and snapshot routes,
and provide one occurrence-to-definition authority. It also owns the author-facing diagnostics and
the concrete fixtures that the contract assigned to this foundation. It does not perform Item 5's
broad resolver/materialization cutover or Item 6's corpus migration and public mutation proof.

## Success Criteria

- [ ] Every supported model-derived binding reaches the pre-resolution boundary with its semantic
  referent preserved and one exact source identity containing declaration identity plus concrete
  occurrence on both live and relocated-snapshot routes.
- [ ] A source identity is produced from extraction evidence rather than reconstructed from a
  consumer's owner, parameter name, written leaf, or current value; missing or ambiguous identity
  fails before a runtime source is selected.
- [ ] The nested-occurrence coordinate C19 applies the modeled `80.0` override to its calculation
  and constraint consumers, emits no unmatched-override tripwire, and preserves the flat sibling's
  established behavior.
- [ ] Two occurrences of one declaration remain distinct under different overrides (C8), while a
  definition-level referent with no uniquely determined occurrence produces the named ambiguity
  outcome in C9 and C10.
- [ ] Every Appendix C coordinate assigned to Item 4 has a concrete fixture or kept diagnostic
  coordinate with the exact referent, occurrence, consumer, value-state, and topology key stated by
  the authority. For C14 and C26, whose downstream topology repair belongs to Item 5, Item 4 proves
  the pre-resolution identity and keeps an explicit current-defect pin that Item 5 must flip; it
  does not assert the corrected public topology early. Foundation evidence does not claim Item 6's
  public mutation certification.
- [ ] Live capture writes an identity-bearing snapshot format, graph rebuild consumes the new
  evidence without semantic reconstruction, and all 37 committed extraction snapshots are
  recaptured atomically with the version change. Unmigrated version-5 snapshots fail closed with
  recapture guidance; in-place versus relocated replay preserves identity exactly.
- [ ] The absorbed nested-override repair shares the existing occurrence-to-definition bridge and
  introduces no parallel part-structure walker, bridge, or consumer-specific identity authority.
- [ ] `agentic-mbse` provides the assigned self-binding and indexed-source diagnostics, while
  codegen independently fails closed for self-binding, indexed-source, and deferred
  expression-source forms; a same-named outer feature never suppresses or changes a diagnostic.
  Existing rescue-aware wrong-oracle tests are replaced with positive and negative oracle tests,
  not deleted, skipped, or marked as expected failures.
- [ ] Item 4 reviews the 37-snapshot recapture for schema and identity correctness, live/relocated
  parity, and unrelated capture drift. Item 6 retains the final per-source semantic-topology review
  after the Item-5 cutover.
- [ ] Focused unit and conformance tests pass on the maintained quality gates, including cycles,
  non-finite cardinality, shadowing, specialization, per-child redefinition, and relocated replay.
  Committed graph baselines, parameter schemas, and generated-package outputs remain unchanged
  unless an explicit foundation change to one of them is separately reviewed.

## Known Requirements

### Identity and referent

- **SIF-01 [NEED]** The foundation must preserve the epic's owner-originated mission invariant: one
  semantic source occurrence can become exactly one public input or one producer channel for every
  and only its consumers. Item 4 must make that outcome derivable without inventing a source at a
  consumer. Source: epic Success Criteria, `[OWNER] Mission invariant`; lifecycle contract
  invariant 56.
- **SIF-02 [INHERITED]** Every supported model-derived consumed value carries an extraction-owned
  identity containing declaration identity and concrete occurrence identity before resolution.
  Owner/name reconstruction is diagnostic provenance only and is not an identity authority.
  Source: LC-SI-08; lifecycle contract invariant 55; Item-2 evidence-sufficiency verdict.
- **SIF-03 [HARD]** The semantic referent is the element selected by KerML name resolution and
  exposed by SysIDE. Redefinition replaces the redefined feature in its concrete context. Identity
  must therefore preserve the actual referent and redefinition relationship; it cannot substitute a
  same-named element. Source: KerML 1.0 §8.2.3.5 and §7.4.11; SysML v2 Part 1 §§7.6 and 7.13.4;
  Item-1 licensed referent and `owned_redefinitions` evidence.
- **SIF-04 [INHERITED]** Semantic referent, declaration, concrete occurrence, supplied value, and
  value provenance remain distinguishable. Applying a literal or default does not change a
  reference-derived binding into an independently authored literal and does not erase its identity.
  Source: lifecycle contract definitions and invariants 54–56 and 60; Appendix B corrections for
  VBR stamping and supplied-value synthesis.
- **SIF-05 [INHERITED]** A definition-level referent used in a concrete context maps to the unique
  occurrence established by model structure. Zero or multiple eligible occurrences produce the
  contract's named failure or ambiguity outcome; the foundation never first-picks or leaf-guesses.
  Source: lifecycle contract invariant 55 and Appendix C C9/C10/C18.

### Occurrence authority

- **SIF-06 [INHERITED]** The Item-10 per-child redefinition and transitive instance-routing
  machinery is reused as substrate. The nested-override repair and source-identity work share one
  occurrence-to-definition bridge with the existing occurrence index; no parallel walker or bridge
  may be introduced. Source: lifecycle contract invariant 60; Item-2 adjacent-work register rows
  1–3; `[CONSTRAINT-ARCH-UNIFY]` sub-scope 2 sequencing.
- **SIF-07 [INHERITED]** A definition-relative captured override must match the corresponding
  occurrence-relative demand for calculations and constraints. For C19, both consumers observe
  `80.0`, the tripwire is silent, and the package-level flat control remains unchanged. Source:
  lifecycle contract C19; `[NESTED-OCCURRENCE-OVERRIDE]`; archived tripwire evidence and fixture
  provenance.
- **SIF-08 [INHERITED]** Distinct concrete occurrences remain distinct sources, including equal
  inherited defaults and different occurrence overrides. Recursive containment, non-finite
  multiplicity, malformed cardinality, or non-unique occurrence mapping fails atomically with
  owner/path context rather than publishing a partial occurrence set. Source: lifecycle invariants
  17, 18, 55, and 56; LC-SI-05; Appendix C C7–C10.

### Live and snapshot transport

- **SIF-09 [INHERITED]** The identity-bearing snapshot change advances the snapshot format, updates
  capture and graph rebuild together, rejects older or insufficient formats before semantic use,
  and atomically recaptures all 37 committed extraction snapshots so the maintained snapshot gate
  never depends on a compatibility window. No silent compatibility shim may synthesize missing
  identity. Source: lifecycle contract invariant 58 and snapshot/identity blast-radius obligation;
  LC-SI-13. Atomic Item-4 ownership is an agent recommendation ratified by owner, 2026-08-07,
  because the loader and conformance gate accept exactly one current snapshot version.
- **SIF-10 [INHERITED]** Live extraction, in-place snapshot replay, and relocated replay preserve
  the same source identity and occurrence evidence. Checkout location and route-specific scope
  strings do not become semantic identity. Source: lifecycle contract invariants 34, 35, and 58;
  Item-2 licensed parity evidence.

### Contract coordinates and diagnostics

- **SIF-11 [INHERITED]** Item 4 owns concrete fixtures for every Appendix C cell whose published
  certification state assigns the missing foundation evidence to Item 4: C9–C13, C15, C18–C21,
  C24, and C25. It also owns C8's foundation topology; C14's canonical identity input to the
  existing synthesis route; C17's correct producer-topology control; C26's canonical source
  identities and retained current-defect pin; and kept readiness coordinate 22a. Item 4 does not
  reroute SVM synthesis or assert C26's corrected public topology. Item 5 owns those flips. These
  fixtures inherit their exact evidence coordinates; they do not broaden or parametrize the keys.
  Source: ratified lifecycle contract Appendix C; epic Item 4 scope; Item-4/5 boundary
  interpretation ratified by owner, 2026-08-07.
- **SIF-12 [NEED]** The `agentic-mbse` validation stack covers both a consumed calculation input
  that resolves to itself and a valid indexed value expression used where source feature identity
  is required. Source: owner, 2026-08-05: “agree with classifying that as unsupported. Can we add
  that (and probably the `in.R=R`) pattern in the agentic-mbse validation stack?”
- **SIF-13 [INHERITED]** Those authoring diagnostics are blocking and actionable. A same-named
  outer attribute or sibling output never suppresses the self-binding diagnostic. The current
  rescue-aware tests are replaced with positive and negative oracle tests; they are not deleted,
  skipped, or marked as expected failures. Source: lifecycle contract invariant 59 and L2
  validation obligation; epic Item 4 scope 5.
- **SIF-14 [INHERITED]** Codegen enforces source-self-binding, indexed-source, and deferred
  expression-source boundaries unconditionally, regardless of whether authoring validation ran.
  Indexed and expression diagnostics say valid SysML but unsupported by this executable subset;
  they never flatten an expression or invent a source. Source: lifecycle contract invariant 59;
  D-4, D-8, D-15; SRC-01, SRC-02, and C22/22a.
- **SIF-15 [INHERITED]** Foundation tests observe identity and topology structurally from the exact
  Appendix C key. Equal values, entry-key counts, agreement between live and replay, or the existing
  producer-completeness diagnostic alone cannot certify correctness. Source: lifecycle contract
  invariant 57 and proof standard; Lifecycle Item-10 audit's channel-tier completeness gap.
- **SIF-16 [INFERRED]** The `agentic-mbse` validation leg may phase independently of the atomic
  codegen snapshot-format/capture/rebuild/37-snapshot unit. Item 4 is complete only after both legs
  satisfy this spec. Source: review recommendation ratified by owner, 2026-08-07.

## Non-Goals

- Cutting calculation, constraint, and aggregation consumers over to one final resolution route;
  deleting VBR stamping, lenient consumer-local minting, parameter-group backfill, or other
  superseded routes. Item 5 owns that cutover and deletion register.
- Performing the final post-cutover semantic-source census or per-source public-topology
  certification; migrating graph baselines, parameter schemas, contracts, generated packages,
  customer artifacts, or authored self-bindings. Item 6 owns those reviewed migrations after Item
  5 repairs resolution topology.
- Certifying off-default behavior through generated packages and studies. Item 6 owns package-level
  mutation; Item 7 owns study lineage and historical-study correction.
- Supporting general expression-source or `#(i)` source identity. Those forms remain deferred or
  unsupported under D-8 and D-15.
- Publishing the cross-repository modeling guide. Item 8 owns documentation; this item implements
  only the assigned validation behavior.
- Completing `[CONSTRAINT-ARCH-UNIFY]` sub-scopes beyond the source-identity seam, including general
  typed-path cleanup, shared orchestrator phases, or graph-extension folding.

## Open Questions / Deferred to design

- The immutable source-ID type, canonical constructor, internal field names, and equality/hash
  representation are deferred to design. The observable identity content and authority are fixed.
- Design must choose the extraction seam that publishes SysIDE referent/redefinition evidence and
  the single mapping from that evidence to the existing occurrence index. It may not create a
  second semantic or structural authority.
- The snapshot serialization layout, next version constant, and capture/rebuild API changes are
  deferred to design. Fail-closed version behavior and the absence of heuristic reconstruction are
  fixed.
- The smallest honest fixture set may extend existing coordinates or add new fixtures. Design must
  prove every SIF-11 key exactly and avoid duplicate fixtures whose only difference is route.
- Diagnostic codes and the non-atomic cross-repository landing order are deferred to design.
  Blocking severity, valid-but-unsupported wording, independent codegen enforcement, and the
  atomic codegen snapshot unit are fixed.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_semantic_source_identity.md` (Item 4)
- **Required Reading:**
  - `.project/active/source-identity-route-evidence-spike/findings.md`
  - `.project/active/source-identity-route-evidence-spike/adjacent-work-register.md`
  - `.project/concepts/constraint-execution-authoritative-lifecycle-contract.md`
  - `.project/concepts/constraint-execution-lifecycle-requirements.md`
  - `.project/backlog/BACKLOG.md` (`[NESTED-OCCURRENCE-OVERRIDE]` and
    `[CONSTRAINT-ARCH-UNIFY]` sub-scope 2)
  - `.project/completed/20260724_nested-override-tripwire/evidence.md`
  - `.project/completed/20260724_nested-override-tripwire/probes/verdict.md`
  - `tests/fixtures/nested_occurrence_override_probe/PROVENANCE.md`
  - `.project/completed/20260720_constraint-lifecycle-producer-completeness/design.md`
  - `.project/completed/20260720_constraint-lifecycle-producer-completeness/evidence.md`
  - `.project/completed/20260720_constraint-lifecycle-producer-completeness/audit.md`
- **Research:** `.project/research/20260805-054752_source-identity-route-evidence.md`
- **Acceptance authority:** lifecycle contract Appendix C, “Source-identity scenarios”
- **Product lens:** `.project/active/source-identity-occurrence-foundation/product-lens.md`
- **Design:** `.project/active/source-identity-occurrence-foundation/design.md` (to be created)

---

**Next Steps:** After the revised-spec recheck clears and the owner approves, proceed to
`my-design`.
