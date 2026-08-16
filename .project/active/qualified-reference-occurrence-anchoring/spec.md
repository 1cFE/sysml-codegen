# Spec: Exact Owner Anchoring for Usage-Owned One-Segment References

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-08-15 14:15 PDT
**Revised:** 2026-08-15 (spec-review incorporation)
**Complexity:** MEDIUM
**Branch:** main (`c615eb4` at revision)

---

## Problem

SysIDE resolves a direct reference to an exact semantic feature. When that feature is a
redefinition owned by a `PartUsage`, its owner identifies the occurrence the author named. The
elaborator preserves the exact feature declaration and its owner, but its one-segment route ignores
the owner. It first reduces the feature to its redefinition slot and then searches for that slot
from the consumer's position. This can select another occurrence, refuse an unambiguous reference,
or report that a named occurrence is missing.

Here, “one segment” describes the semantic reference the elaborator receives: one resolved leaf
with no occurrence root to contextualize first. Source text such as `comp_a::length` still arrives
on this direct-reference route because `::` qualifies the leaf's declaration; it is not the same
shape as a feature chain such as `driver.cost`, whose `driver` root fixes an occurrence before the
leaf is selected.

The sharpest case is `comp_a::length` authored from inside `comp_b`: SysIDE resolves `comp_a`'s
redefining feature, while the current graph silently wires `comp_b.length`. A design mutation can
therefore move the named value without moving its supposed consumer, producing a confident wrong
answer. That contradicts the ELABORATE-FIRST mission and the product's design-search promise.

For usage-qualified references, this is also a conformance defect against D-6. That ratified
disposition says “usage qualifier → occurrence-level feature”; it does not authorize codegen to
replace the exact usage owner with the consumer's position. The qualified half of this item restores
that existing contract rather than inventing new `::` semantics.

`[OWNER, 2026-08-15]` After being presented the qualified-only and broader alternatives, the owner
selected the “broader invariant”: every one-segment reference whose exact resolved leaf is owned by
a real `PartUsage` honors that owner, whether the author wrote a qualified or bare reference. The
outcome applies consistently to calculation bindings, aliases, computed attributes, constraint
bindings and predicates, and the other callers of the shared exact resolver.

`[AGENT]` The completed bare-reference measurement supports that choice but does not certify it. It
found zero edge changes: 91 of the 126 expression- and constraint-side subjects joined to exact
typed edges and compared equal, while the other 35 had named no-edge reasons. Equality was forced
by the corpus topology: every joined bare leaf slot appears on exactly one occurrence. The narrow
alternative would therefore carry authored-spelling evidence through three shared resolver callers
to protect no observed behavior. The measurement is acceptance evidence, not the source of the
owner-grade requirement; it does not silently narrow or reopen that requirement. A discriminating
authored bare regression remains the proof where the two routes can differ, and contrary evidence
must be surfaced for disposition rather than classified away.

`[OWNER-VERBATIM, 2026-08-15]` The work must “also repair the self-biding spec.” That direction is
already substantially discharged: rev 4 of the active self-binding spec names the positional
behavior as codegen defect F-6 and delegates the repair here. What remains is a close-time check
that the landed semantics and that explanation still agree. This item does not change the D-5
local-rename advice, the D-7 dot-path advice, or the chosen fusion-tea migration form.

## Success Criteria

- [ ] A one-segment reference to a `PartUsage`-owned leaf resolves through an occurrence of that
      exact owner before selecting the leaf's feature slot, across every shared resolver consumer.
- [ ] The promoted u4 package-sibling case resolves `shared_component::length` to the
      package-scoped `PartUsage` occurrence `shared_component.length`, with no occurrence
      diagnostic.
- [ ] The promoted u5 named-sibling case resolves `comp_a::length` to `plant.comp_a.length`, rather
      than reporting an ambiguity between the sibling `comp_a` and `comp_b` occurrences.
- [ ] The promoted u6 cross-owner case, authored inside `comp_b`, resolves `comp_a::length` to
      `plant.comp_a.length`, never the competing enclosing `plant.comp_b.length`, with no silent or
      fallback edge.
- [ ] The promoted u7 paired-spelling case resolves its two qualified bindings to the distinct
      `comp_a.length` and `comp_b.length` nodes, and those edges agree with the corresponding
      occurrence-rooted dot-path controls.
- [ ] The u1–u3b cases and definition-owned, package-owned, enumeration, and feature-chain controls
      retain their existing exact edges or named diagnostics. Inherited leaves that resolve to a
      definition-owned declaration do not acquire an occurrence from qualifier text.
- [ ] Kept qualified usage-owned regressions cover an alias, a computed attribute, a typed
      constraint binding, and a constraint predicate. Each places the consumer where exact owner
      selection is load-bearing and pins the typed target edge.
- [ ] A kept bare-reference regression uses a discriminating topology where consumer-lineage and
      exact-owner selection can land on different occurrences. It pins the expected typed edge and
      fails if the implementation merely preserves the corpus's accidental fan-out-of-one equality.
- [ ] The broader bare-reference surface is re-derived from the tracked corpus. Every usage-owned
      direct reference has an exact before/after typed-edge comparison or a named structural reason
      why no edge exists. Every change is adjudicated as a fix or a regression with recorded
      reasoning; there are zero unadjudicated semantic differences.
- [ ] At least one public off-default mutation of a named source occurrence reaches every and only
      its calculation, alias/computed, constraint, and aggregation consumers on the live graph and
      snapshot round-trip routes.
- [ ] Strict and lenient elaboration agree on semantic identity. Lenient mode records the exact
      diagnostic multiset; strict mode either produces the same complete graph or rejects those same
      blocking diagnostics.
- [ ] Feature-slot families, occurrence records, and serialized occurrence IDs remain unchanged.
      The repair may change a consumer edge or its resolution diagnostic, never occurrence or wire
      identity.
- [ ] Every live-versus-snapshot and stored-baseline difference is classified. If the implemented
      repair changes an edge stored in a committed snapshot, a typed-edge comparison exposes the
      stale replay before recapture; that snapshot is then recaptured and live/snapshot parity is
      restored. Snapshots with no changed final edge remain byte-unchanged.
- [ ] At close, the active self-binding spec is checked against the landed behavior and still names
      positional selection as defect F-6 rather than the meaning of `::`. Any mismatch is corrected
      there without changing the D-5 local rename advice, D-7 dot-path advice, or fusion-tea
      migration choice.

## Known Requirements

- **[NEED]** Every one-segment reference with an exact `PartUsage`-owned leaf honors that exact
  owner across all resolver consumers, including bare and qualified authored forms. This is the
  owner's selected broader invariant (2026-08-15).
- **[NEED]** Promote u4–u7 and add qualified expression-side regressions. The owner explicitly
  authorized both as scope for this separate item (2026-08-15); the corpus scans supply the
  concrete coverage rationale.
- **[NEED]** The landed behavior remains consistent with the owner's verbatim direction to “also
  repair the self-biding spec.” Rev 4 has already corrected that spec's explanation; this item must
  verify the correction against the implementation without changing the existing modeling advice
  (owner confirmation, 2026-08-15).
- **[INHERITED]** D-6 says a usage-qualified reference is supported at the occurrence-level feature
  SysIDE resolved. A definition-qualified reference remains definition-owned and uses the ordinary
  occurrence bridge; it never guesses an occurrence
  (`.project/concepts/constraint-execution-authoritative-lifecycle-contract.md:618-626`,
  `[AGENT] (ratified by owner, 2026-08-05)`).
- **[INHERITED]** One semantic source occurrence becomes exactly one runtime source across all
  calculation, constraint, and aggregation consumers; a public mutation reaches every and only the
  bound consumers (`.project/backlog/epic_elaborate_first_architecture.md:31-33,84-86`, owner
  grade).
- **[INHERITED]** Exact parser declaration identity and structured occurrence identity are the
  semantic contract. Names, qualified names, rendered paths, source positions, values, and
  enumeration order may not select an occurrence or graph edge
  (`.project/active/elaborator-design/spec.md:38-54`; design invariants 1–11 at
  `.project/active/elaborator-design/design.md:361-376`).
- **[INHERITED]** The exact leaf's live semantic owner is available before graph sealing. The
  resolver can rely on the owner's exact declaration ID only when `SysideAdapter.is_instance(owner,
  "PartUsage")`; `owner_is_definition == false` is insufficient because package and other owners
  also satisfy it (`../agentic-mbse/src/agentic_mbse/sysml/data_models.py:55-74`,
  `../agentic-mbse/src/agentic_mbse/sysml/expression.py:639-678`).
- **[INHERITED]** Slot normalization remains the authority for redefinition families after an
  occurrence is fixed. A base feature and every materialized redefinition still share one
  `FeatureSlotId`, and unrelated same-named declarations do not
  (`src/sysml_codegen/elaboration/occurrence.py:58-133`).
- **[INHERITED]** Missing or multiple occurrences of the exact owner fail with the existing named
  occurrence diagnostics. Resolution never falls back to consumer position, qualifier strings,
  owner names, qualified names, or first-match selection
  (`.project/active/elaborator-design/design.md:345-355,361-376`).
- **[INHERITED]** Extraction is not the sole reference authority. Aliases, computed attributes,
  constraints, and other expression-side consumers independently construct one-segment semantic
  facts, so every such consumer must exhibit the same owner-aware outcome
  (`src/sysml_codegen/elaboration/elaborate.py:1032-1059,2370-2602`).
- **[INHERITED]** Strict and lenient elaboration may differ only in halt-versus-report behavior,
  never in semantic identity. A graph with a blocking identity diagnostic cannot project
  (`.project/active/elaborator-design/design.md:320-324,374-376`).
- **[INHERITED]** Snapshots contain resolved final graph edges and do not retain enough live semantic
  evidence to rerun owner selection. A changed live edge requires recapture; replay cannot repair an
  old edge (`src/sysml_codegen/snapshot/instance_graph.py:340-377,523-533`).
- **[INFERRED]** The implementation is accepted against typed graph edges, exact diagnostics, and
  public mutation behavior. Display paths and generated names are diagnostic output, not semantic
  oracles.
- **[INFERRED]** The corpus comparison is re-derived from tracked model groups at implementation
  time. The two 2026-08-15 scans predict five qualified changes, zero bare changes, zero current
  kept-fixture changes, and no existing snapshot recapture. New evidence may correct those
  predictions, but every difference must be adjudicated as a fix or regression rather than merely
  attributed to the invariant.
- **[INFERRED]** The bare corpus's zero-change result is compatibility evidence, not proof of the
  broader predicate. A kept discriminating bare topology is required because every currently joined
  bare leaf slot has occurrence fan-out one, and the corpus has no usage-owned direct typed-alias or
  inline-predicate example
  (`.project/research/20260815-142743_bare-expression-side-measurement.md:157-259`).
- **[INFERRED]** When a changed live edge is present in a committed snapshot, acceptance must expose
  the stale replay through an exact typed-edge live/snapshot comparison before recapture. Snapshot
  loading itself cannot re-resolve the semantic owner.

## Non-Goals

- Reinterpreting `in R = R` as an outer reference or weakening `SI_SELF_BINDING`.
- Changing the D-5 rename-in-place migration for fusion-tea, migrating customer models, or
  reopening the broader self-binding documentation/model-migration item.
- Reconstructing occurrence identity from authored qualifier text. The repair uses the exact live
  owner of the resolved referent; a definition-owned inherited leaf stays definition-owned.
- Changing feature-slot construction, occurrence expansion, occurrence wire encoding, snapshot
  schema version, projection naming, or generated public identifiers.
- Changing feature-chain (`.`) meaning, plural cardinality policy, enumeration-literal handling, or
  the semantics of a leaf whose semantic owner is a package. A `PartUsage` declared at package scope
  is still usage-owned and remains in scope; this is the u4 shape.
- Adding name, qualified-name, display-path, source-text, or candidate-order fallbacks.
- Recapturing snapshots or baselines that have no classified semantic edge change.
- Revising historical research reports to make past observations read as though the repaired code
  already existed. Active requirements and the related self-binding explanation are corrected;
  measured history stays dated evidence.

## Open Questions / Deferred to design

- Where the shared exact-owner contextualization lives inside elaboration, provided every
  one-segment semantic-reference caller receives the same behavior.
- How the kept regression fixtures are organized and whether u4–u7 are copied into a dedicated
  fixture family or promoted under their existing names.
- Whether the qualified constraint regression uses one fixture for typed actuals and predicates or
  separate minimal fixtures. Both consumer lanes must be covered.
- How exact-owner selection preserves the existing singular/plural policy when the shared resolver
  is called with `plural=True`. The measured corpus has no bare usage-owned reference under `sum()`,
  and this item does not choose a new cardinality policy.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_elaborate_first_architecture.md` — ELABORATE-FIRST. Placement as
  a separate bounded child of Item 8 is `[INFERRED]`; the repair was previously unowned and is not
  folded into `self-binding-replacement`.
- **Required Reading:** Item 8 lists none. Relevant occurrence-authority inputs inherited from the
  closed Item-6 implementation are:
  - `.project/research/20260809-153245_item6-identity-completion-and-cutover-census.md`
  - `.project/active/spike-syside-occurrence-authority/findings.md`
  - `.project/active/elaborator-design/spec.md`
  - `.project/active/elaborator-design/design.md`
- **Research:** `.project/reports/20260815-1338_qualified-binding-defect-attribution.md`
- **Independent assessment:**
  `.project/research/20260815-134615_qualified-binding-defect-assessment.md`
- **Corpus scan:** `.project/research/20260815-140630_qualified-binding-corpus-scan.md`
- **Bare expression-side measurement:**
  `.project/research/20260815-142743_bare-expression-side-measurement.md`
- **Spec review:**
  `.project/active/qualified-reference-occurrence-anchoring/spec-review.md` — `Revise`; findings
  substantively incorporated in this revision.
- **Related active spec:** `.project/active/self-binding-replacement/spec.md`
- **Product promise:** `.project/product/P-001-design-search-free-variation.md`
- **Product lens:** `.project/active/qualified-reference-occurrence-anchoring/product-lens.md`
  — latest revision verdict `Gate: CLEAR` with no findings; the earlier `spec-F1` provenance
  finding remains explicitly resolved.
- **Design:** `.project/active/qualified-reference-occurrence-anchoring/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `$my-design`.
