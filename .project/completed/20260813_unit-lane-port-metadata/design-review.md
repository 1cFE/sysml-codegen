# Design Review: Unit-Lane Port Metadata — Final Independent Rerun

**Design:** `.project/active/unit-lane-port-metadata/design.md`
**Spec:** `.project/active/unit-lane-port-metadata/spec.md`
**Prior Rerun Review:** this file before replacement (`Rework`, blocking `RDR-1`)
**Review File:** `.project/active/unit-lane-port-metadata/design-review.md`
**Date:** 2026-08-13

---

## The Point

One modeled design attribute must remain one public entry source when calculations, constraint
formals, and computed design attributes consume it. Each consumer must carry the exact unit authored
for its own semantic declaration. Equal metadata must converge. Unequal metadata must refuse under
the existing exact-text, no-conversion policy. The decided instance graph must preserve the result
through live, in-place snapshot, and relocated snapshot routes. Item 8 must publish exact churn and
downstream-output evidence for Item 6 without implementing Item 6 or broadening Item 8's recapture
trigger.

## Fundamental Assessment

**Assessment: Sound. The design is the right piece of work and the approach is ready for planning.**

The revision repairs the one remaining load-bearing identity defect without reopening the accepted
architecture. It reuses the existing slot/effective selector, projector, graph-v3 unit field, v6
envelope, and generation seams. The shared extraction helper and the small elaboration selector earn
their boundaries; no graph post-pass, duplicate equality policy, schema bump, or Item 6 production
work is introduced.

The existing product-lens verdict remains applicable. The envelope now owns its projectability
guarantee, so the consumer-compensates-for-producer smell does not fire. Constraint identity,
computed-alias metadata identity, and later calc-provenance ownership are explicit, so invariant
ownership does not move silently.

---

## Blocking Finding Verification

### RDR-1 — Wrong SysIDE collection for effective formals

**Disposition: Resolved.**

- The design now pins the observed SysIDE fact: ordinary `BandGuard` constraint inputs are absent
  from `definition.features` and present in `definition.usages`
  (`design.md:82-87`). B1 carries that fact as a falsifiable bet (`design.md:137-142`).
- The selection law enumerates the selected definition's `definition.usages`, retains only exact
  IDs in a precomputed loaded-user input-declaration index, groups them by `FeatureSlotId`, and calls
  `FeatureSlotIndex.effective_declaration()` (`design.md:218-228,232-236`). This matches the existing
  loaded-user filter and slot/effective pattern in
  `src/sysml_codegen/elaboration/occurrence.py:453-502`; it does not fall back to the slot root.
- The existing `BandGuard` fixture gets a direct pre-projection selector proof. The node requires a
  non-empty map with the exact `ref_value` and `tol` slot/declaration IDs, proves both objects came
  from `BandGuard.usages`, proves both are loaded-user `in` declarations, and matches both bound
  member slots (`design.md:481-495`). An empty candidate view cannot pass accidentally.
- The base/redefined calculation and constraint cases still use distinguishable `cm`/`m` units and
  record the binding member, slot root, selected definition, effective formal, port, metadata, and
  public key. The computed-alias case still separates referenced declaration `a` from resolved data
  source `x` and proves metadata comes from `a` (`design.md:497-513`). These proofs remain coherent
  with `FeatureSlotIndex.effective_declaration()`, `ExpressionPortId.referenced_declaration`, and
  `_follow_alias()` in the current code.

RDR-1 changes only candidate enumeration. The unit source, port identity, data edge, extraction, and
projection responsibilities remain distinct.

## Accepted Decision Regression Check

### DR-1 — Envelope-owned projectability

**Disposition: Preserved.**

D5 and the envelope section retain one certifier owned by `snapshot/envelope.py`, used by both
`build_envelope()` and decoded-graph load. Capture consumes `build_envelope()` before its existing
atomic write and adds no projector policy. Structured `SI_RENDERING_COLLISION` diagnostics, a
coherently re-sealed loader refusal, and missing/sentinel destination proofs remain required
(`design.md:173-181,283-306,515-528`). This strengthens the existing boundary call sites without a
graph, envelope, or projector marker change.

### DR-2 — Identity ownership and Item 6 boundary

**Disposition: Preserved.**

Constraint ports use the selected effective formal for both structural formal identity and existing
formal provenance. Calculation ports retain their current usage-member identity while using the
selected effective formal only for payload and unit lookup. Computed inputs retain the exact
referenced alias for metadata while the edge follows the alias target. Calc-input
`formal_provenance`, graph v4, catalog 4, TEAx work, and the later v4 recapture remain Item 6 scope
(`design.md:242-257,420-438,657-684`).

### DR-3 — Downstream evidence and recapture trigger

**Disposition: Preserved.**

Every projectable census arm still records both a computation-graph digest and a deterministic
digest over production-generated entry-point schema/JSON bytes. Refusal arms record typed
inapplicability. A kept differential generation test pins the current non-consumption of
`unit_text` (`design.md:538-568`). Exact instance-graph payload or relevant unit-map movement remains
the only staleness trigger; envelope SHA, projected counts, computation digest, and generated digest
remain evidence or review stops (`design.md:546-587`). The graph/unit-only recapture law has not
regressed.

---

## Dimensional Review

### 1. Spec Compliance
**Assessment: Pass.** RDR-1 now reaches ordinary constraint formals, while the exact-unit,
agreement/refusal, three-route, complete-inventory, Item 6 handoff, and verification requirements
remain mapped to named mechanisms and tests.

### 2. Pattern Consistency
**Assessment: Pass.** The formal selector now follows the proven native-`usages`, loaded-user,
slot/effective pattern. Existing projection, codec, envelope, and generation owners remain in use.

### 3. Abstraction Quality
**Assessment: Pass.** Semantic declaration selection stays in elaboration; exact unit extraction
stays in one small extraction helper. No wider registry or repair pass is introduced.

### 4. Duplication Avoidance
**Assessment: Pass.** One unit extractor, one effective-formal map, one envelope certifier, and one
projector equality policy prevent parallel rules.

### 5. Data Structure Clarity
**Assessment: Pass.** Slot-to-effective-formal mappings, structural port IDs, metadata source IDs,
ordered diagnostics, and census rows are explicit and independently asserted.

### 6. Route Safety
**Assessment: Pass.** Live, in-place, and relocated routes consume sealed graph metadata. Envelope
build/load certification and atomic capture refusal cover both admission and replay boundaries.

### 7. Bets & Decisions Integrity
**Assessment: Pass.** B1 now states the corrected pinned-SysIDE premise and its failure consequence.
The riskiest selection bet has a direct base-formal assertion plus derived-definition falsifiers.
Decisions continue to name rejected alternatives.

### 8. Reader Comprehension
**Assessment: Pass.** The design states the declaration-owned metadata model before its mechanics and
keeps slot identity, effective declaration, referenced alias, resolved source, and downstream scope
separate.

---

## Issues by Severity

### Critical

- None.

### Major

- None.

### Minor

- None.

## Recommendations

1. Proceed to `my-plan`. Preserve the named direct selector, redefinition, alias, envelope, route,
   generated-output, and inventory proof nodes as implementation gates.

## Resolutions

- **RDR-1:** Resolved by the design revision. The effective-formal candidates now come from filtered
  `definition.usages`, and the direct `BandGuard` assertion prevents an empty-view false pass.
- **DR-1 through DR-3:** Their accepted dispositions were rechecked and remain resolved. No owner
  decision or further design edit is required.

---

**Overall: Approve**
**Next Steps:** Run `my-plan` against the approved design. Implementation must retain the exact proof
interfaces and stop if the pinned SysIDE or inventory premises are falsified.
