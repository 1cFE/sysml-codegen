# Spec: Exact Owner Anchoring for One-Segment References

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-08-15 14:15 PDT
**Complexity:** MEDIUM
**Branch:** main (`c599cfb` at drafting)

---

## Problem

SysIDE resolves a direct reference to an exact semantic feature. When that feature is a
redefinition owned by a `PartUsage`, its owner identifies the occurrence the author named. The
elaborator preserves the exact feature declaration and its owner, but its one-segment route ignores
the owner. It first reduces the feature to its redefinition slot and then searches for that slot
from the consumer's position. This can select another occurrence, refuse an unambiguous reference,
or report that a named occurrence is missing.

The sharpest case is `comp_a::length` authored from inside `comp_b`: SysIDE resolves `comp_a`'s
redefining feature, while the current graph silently wires `comp_b.length`. A design mutation can
therefore move the named value without moving its supposed consumer, producing a confident wrong
answer. That contradicts the ELABORATE-FIRST mission and the product's design-search promise.

`[OWNER, 2026-08-15]` After being presented the qualified-only and broader alternatives, the owner
selected the “broader invariant”: every one-segment reference whose exact resolved leaf is owned by
a real `PartUsage` honors that owner, whether the author wrote a qualified or bare reference. The
outcome applies consistently to calculation bindings, aliases, computed attributes, constraint
bindings and predicates, and the other callers of the shared exact resolver.

The active self-binding spec currently describes the defective positional behavior as the meaning
of `::`. That explanation will become false when this repair lands. `[OWNER-VERBATIM, 2026-08-15]`
The work must “also repair the self-biding spec.” This is a correction to the explanation, not a
change to its modeling advice or the chosen fusion-tea migration form.

## Success Criteria

- [ ] A one-segment reference to a `PartUsage`-owned leaf resolves through an occurrence of that
      exact owner before selecting the leaf's feature slot, across every shared resolver consumer.
- [ ] The promoted u4 case resolves `shared_component::length` to the named package-level
      `shared_component.length` with no occurrence diagnostic.
- [ ] The promoted u5 case resolves `comp_a::length` to `plant.comp_a.length`, rather than reporting
      an ambiguity between `comp_a` and `comp_b`.
- [ ] The promoted u6 case resolves `comp_a::length` to `plant.comp_a.length`, never the competing
      enclosing `plant.comp_b.length`, with no silent or fallback edge.
- [ ] The promoted u7 case resolves its two qualified bindings to the distinct `comp_a.length` and
      `comp_b.length` nodes, and those edges agree with the two dot-path controls.
- [ ] The u1–u3b cases and definition-owned, package-owned, enumeration, and feature-chain controls
      retain their existing exact edges or named diagnostics. Inherited leaves that resolve to a
      definition-owned declaration do not acquire an occurrence from qualifier text.
- [ ] Kept qualified usage-owned regressions cover an alias, a computed attribute, a typed
      constraint binding, and a constraint predicate. Each places the consumer where exact owner
      selection is load-bearing and pins the typed target edge.
- [ ] The broader bare-reference surface is classified and verified. Every usage-owned direct
      expression has an exact before/after edge or diagnostic record, and every change is explained
      by the exact owner invariant; there are zero unclassified semantic differences.
- [ ] At least one public off-default mutation of a named source occurrence reaches every and only
      its calculation, computed, and constraint consumers on the live graph and snapshot round-trip
      routes.
- [ ] Strict and lenient elaboration agree on semantic identity. Lenient mode records the exact
      diagnostic multiset; strict mode either produces the same complete graph or rejects those same
      blocking diagnostics.
- [ ] Feature-slot families, occurrence records, and serialized occurrence IDs remain unchanged.
      The repair may change a consumer edge or its resolution diagnostic, never occurrence or wire
      identity.
- [ ] Every live-versus-snapshot and stored-baseline difference is classified. Existing committed
      snapshots are recaptured only if the implemented repair changes a stored final edge.
- [ ] The active self-binding spec and every in-scope guidance statement describe the corrected
      semantics. They no longer teach positional selection as the meaning of `::`; the D-5 local
      rename advice, D-7 dot-path advice, and fusion-tea migration choice remain unchanged.

## Known Requirements

- **[NEED]** Every one-segment reference with an exact `PartUsage`-owned leaf honors that exact
  owner across all resolver consumers, including bare and qualified authored forms. This is the
  owner's selected broader invariant (2026-08-15).
- **[INFERRED]** Promote u4–u7 and add qualified expression-side regressions. The owner explicitly
  authorized both as scope for this separate item (2026-08-15); the corpus scan supplies the
  concrete coverage rationale.
- **[NEED]** The work corrects `.project/active/self-binding-replacement/spec.md` and the narrow
  guidance explanation made stale by the repair, without changing the existing modeling advice
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
- **[INHERITED]** Snapshots contain resolved final graph edges and do not retain enough live semantic
  evidence to rerun owner selection. A changed live edge requires recapture; replay cannot repair an
  old edge (`src/sysml_codegen/snapshot/instance_graph.py:340-377,523-533`).
- **[INFERRED]** The implementation is accepted against typed graph edges, exact diagnostics, and
  public mutation behavior. Display paths and generated names are diagnostic output, not semantic
  oracles.
- **[INFERRED]** The corpus comparison is re-derived from tracked model groups at implementation
  time. The 2026-08-15 scan is the baseline and predicts five qualified changes, zero kept-fixture
  changes, and no existing snapshot recapture; new evidence may correct those predictions but may
  not be left unclassified.

## Non-Goals

- Reinterpreting `in R = R` as an outer reference or weakening `SI_SELF_BINDING`.
- Changing the D-5 rename-in-place migration for fusion-tea, migrating customer models, or
  reopening the broader self-binding documentation/model-migration item.
- Reconstructing occurrence identity from authored qualifier text. The repair uses the exact live
  owner of the resolved referent; a definition-owned inherited leaf stays definition-owned.
- Changing feature-slot construction, occurrence expansion, occurrence wire encoding, snapshot
  schema version, projection naming, or generated public identifiers.
- Changing feature-chain (`.`) meaning, plural cardinality policy, enumeration-literal handling, or
  package-owner semantics. Exact owner anchoring still applies when those callers resolve a
  one-segment usage-owned reference.
- Adding name, qualified-name, display-path, source-text, or candidate-order fallbacks.
- Recapturing snapshots or baselines that have no classified semantic edge change.
- Revising historical research reports to make past observations read as though the repaired code
  already existed. Active requirements and current guidance are corrected; measured history stays
  dated evidence.

## Open Questions / Deferred to design

- Where the shared exact-owner contextualization lives inside elaboration, provided every
  one-segment semantic-reference caller receives the same behavior.
- How the kept regression fixtures are organized and whether u4–u7 are copied into a dedicated
  fixture family or promoted under their existing names.
- How the 126 already-inventoried bare expression-side consumers are joined to stable before/after
  edge records without making display metadata an oracle.
- Whether the qualified constraint regression uses one fixture for typed actuals and predicates or
  separate minimal fixtures. Both consumer lanes must be covered.
- Which current guidance surfaces contain the stale positional explanation beyond the active
  self-binding spec. Design owns the inventory; this spec fixes the outcome.

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
- **Related active spec:** `.project/active/self-binding-replacement/spec.md`
- **Product promise:** `.project/product/P-001-design-search-free-variation.md`
- **Product lens:** `.project/active/qualified-reference-occurrence-anchoring/product-lens.md`
  — latest verdict `Gate: CLEAR`; resolves `spec-F1` after provenance regrading.
- **Design:** `.project/active/qualified-reference-occurrence-anchoring/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `$my-design`.
