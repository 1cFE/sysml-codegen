---
date: 2026-08-15T14:06:30-07:00
researcher: Codex
topic: "Semantic corpus scan for the qualified-binding defect"
tags: [research, elaboration, source-identity, qualified-reference, corpus]
status: complete
last_updated: 2026-08-15
measured_commit: c599cfb
---

# Research: Qualified-binding corpus scan

**Date:** 2026-08-15
**Researcher:** Codex
**Research Type:** Licensed semantic corpus / prospective behavior comparison

## Research Question

`[OWNER-VERBATIM]` “ok please execute the corpus scan”

`[INHERITED: .project/reports/20260815-1338_qualified-binding-defect-attribution.md]`
For every authored `usage::feature` binding, record the exact referent owner, the consumer's
position relative to it, the current edge or diagnostic, the expected owner-aware edge or
diagnostic, and affected snapshots or baselines.

## Verdict

- `[AGENT]` **The qualified-reference blast radius is smaller than the textual count suggests.**
  The tracked codegen corpus has 256 authored qualified references whose exact leaf owner is a
  `PartUsage`. Of those, 251 are consumed inside that usage and produce the same exact wire edge
  under current and owner-aware resolution. The other five are the deliberately authored `u4`–`u7`
  spike cases. All five change in the intended direction.
- `[AGENT]` **No currently green kept fixture depends on the wrong positional result.** The kept
  fixture corpus contributes 249 concrete usage-owned qualified calc-input edges. Current and
  owner-aware edge wires match for all 249. After collapsing the three CATF variants, that is 85
  independent authored sites.
- `[AGENT]` **No committed snapshot or computation-graph baseline needs recapture for the qualified
  repair on the present corpus.** Four snapshots and three stored computation-graph baseline
  families contain relevant qualified feature references. None of their final edges changes.
- `[AGENT]` **This clears the report's qualified-reference behavior-change gate. It does not, by
  itself, authorize the report's broader owner-only implementation predicate.** The proposed shared
  branch says “one-segment leaf owned by `PartUsage`,” without checking authored form. The corpus
  also contains 189 bare, direct, usage-owned reference expressions. Sixty-three are calc bindings
  and compare unchanged; 126 are expression-side consumers that were inventoried but not joined to
  prospective graph edges in this scan.

## Scope and Method

Measured at codegen `c599cfb` with the SysIDE license loaded from the companion checkout.

The tracked inventory contains 304 SysML files:

- 255 files in 119 `tests/fixtures/<family>` roots;
- 49 files under `.project/`;
- 23 committed v6 instance-graph snapshots;
- 13 computation-graph baseline families; and
- 5 YAML baseline families.

The semantic pass did the following:

1. Loaded every one of the 119 fixture roots separately, matching normal fixture admission.
2. Loaded all 20 self-binding spike fixture groups separately.
3. Loaded the source-identity qualified-form probe separately because its sibling bracket probes
   are intentionally parser-invalid.
4. Enumerated subtype-aware `FeatureReferenceExpression` elements and recovered exact authored text
   from CST byte spans. No loaded expression had unknown written form.
5. Recorded the resolved leaf UUID, leaf metatype and qualified name, semantic owner UUID,
   owner metatype and qualified name, and consumer owner chain.
6. For calculation-input bindings, joined each source fact to its concrete calc node, typed consumer
   port, current input edge, and current diagnostic under `strict=False` elaboration.
7. Simulated the proposed owner-aware route only when the resolved owner is a real `PartUsage`:
   select the exact owner's occurrence using the existing occurrence-selection policy, transition
   to the exact leaf slot inside that occurrence, then follow typed aliases exactly as the binding
   resolver does. Exact typed wire edges, not display names, were compared.

Two fixture roots fail model admission by design and contain no textual qualified direct-reference
candidate: `source_identity_absent_referent` and `two_same_leaf_producers`. Two more stop during
calculation extraction and eight stop during graph construction, also with zero qualified
calc-binding facts. No candidate-bearing group failed semantic classification or graph joining.

The scanner initially reported 13 apparent CATF changes. They were false positives: CATF's local
`inner_radius` attributes are typed aliases. The live binding resolver follows each alias to the
previous layer's `outer_radius`; the prospective route must do the same. After applying the same
alias-following step, all 246 CATF variant edges compare equal.

## Semantic Census

The table counts distinct authored expression sites. Extraction emits 278 qualified calc-binding
records because three authored declarations expand twice; those duplicates are not counted as new
source sites.

| Consumer form | PartUsage owner | Other semantic owner | Total sites |
|---|---:|---:|---:|
| Calculation input | 256 | 19 | 275 |
| Constraint input | 0 | 1 `PartDefinition` | 1 |
| Computed attribute | 0 | 1 `PartDefinition` | 1 |
| Enumeration literal | 0 | 33 `EnumerationDefinition` | 33 |
| **Total** | **256** | **54** | **310** |

The 21 non-enumeration “other owner” sites comprise 20 `PartDefinition`-owned leaves and one
`CalculationDefinition`-owned leaf. They retain today's route under the proposed owner-kind guard.

All 256 qualified `PartUsage`-owned sites are calculation-input bindings in the present corpus.
There is no qualified usage-owned alias, computed attribute, constraint binding, or constraint
predicate. That absence is a coverage gap, not evidence that those shared resolver callers are
correct.

### Source/occurrence relation

| Relation to exact `PartUsage` owner | Raw authored sites | CATF-collapsed sites | Outcome |
|---|---:|---:|---|
| Consumer inside owner usage | 251 | 87 | Exact current/expected edge match |
| Consumer outside owner usage | 5 | 5 | All five intentionally change |
| **Total** | **256** | **92** | |

CATF contributes 246 raw sites: the same 82 authored line shapes in `catf_mfe_model`,
`catf_mfe_d5`, and `catf_mfe_gated`. Their candidate-line multisets are identical. Raw counts are
kept above so snapshot-bearing variants remain visible; the collapsed count avoids treating copies
as independent modeling patterns.

The route-neutral 37-family corpus contains 105 qualified reference expressions: 84 usage-owned
calc bindings, one calculation-definition-owned calc binding, and 20 enumeration literals. The
adjunct exact-route fixtures and spike groups provide the remaining cases.

## The Five Changed Sites

These are all under `.project/active/self-binding-replacement/spike/fixtures/`; none is a kept test
fixture today.

| Site | Exact owner UUID | Current | Owner-aware result |
|---|---|---|---|
| `u4_usage_qual_pkg_sibling/model.sysml:23`, `shared_component::length` | `ae393bfa-ea4e-5606-bf4a-1e6fcd266492` | `SI_OCCURRENCE_MISSING`, no edge | `shared_component.length` |
| `u5_usage_qual_named_sibling/model.sysml:23`, `comp_a::length` | `eecdcddf-fa9c-5f4a-9006-3d4a3958f123` | `SI_OCCURRENCE_AMBIGUOUS`, no edge | `plant.comp_a.length` |
| `u6_usage_qual_crossnamed/model.sysml:26`, `comp_a::length` | `dd373162-bf97-5062-ada3-07d5f3244ba4` | `plant.comp_b.length`, no diagnostic | `plant.comp_a.length` |
| `u7_both_spellings/model.sysml:26`, `comp_a::length` | `95d32d62-574d-55ec-9515-4a8ee144a508` | `SI_OCCURRENCE_AMBIGUOUS`, no edge | `plant.comp_a.length` |
| `u7_both_spellings/model.sysml:27`, `comp_b::length` | `869ecad0-edef-5fe4-ae9e-441aa5e724fb` | `SI_OCCURRENCE_AMBIGUOUS`, no edge | `plant.comp_b.length` |

The exact leaf declaration IDs remain distinct from the owner IDs and were also recorded. The
u6 leaf is `7114fafa-d5dc-58cf-879a-2f84cbc6bd73`; the u7 leaves are the report's previously
measured `936d7879-82e1-5bcf-92b8-773d6f67b37d` and
`d7d38390-79be-56a3-876f-3c1a7f4d41e7`. In every row, the expected edge keeps the existing slot
root and changes only the selected occurrence.

Expected diagnostic delta across the five sites:

- one `SI_OCCURRENCE_MISSING` is removed;
- three `SI_OCCURRENCE_AMBIGUOUS` diagnostics are removed;
- four previously absent inputs gain exact typed edges; and
- one silently wrong input edge is rewired from `comp_b` to `comp_a`.

## Kept Fixtures, Snapshots, and Baselines

Kept fixtures contain 249 raw usage-owned qualified sites. All 249:

- select the exact owner from the consumer lineage;
- resolve to one expected edge;
- have no current/expected wire difference; and
- preserve the current diagnostic result.

After collapsing the three CATF copies, they represent 85 authored sites: 82 CATF sites plus one
each in `deep_cross_scope_probe`, `elab_matrix_c5`, and `shadowed_reference`.

Four committed snapshots contain qualified feature-reference candidates:

| Snapshot fixture | Qualified feature sites | Owner-aware edge changes |
|---|---:|---:|
| `catf_mfe_d5` | 82 | 0 |
| `catf_mfe_gated` | 82 | 0 |
| `deep_cross_scope_probe` | 2 | 0 |
| `shadowed_reference` | 1 | 0 |

Three stored computation-graph baseline families contain corresponding qualified feature edges:
`catf_mfe`, `deep_cross_scope_probe`, and `shadowed_reference`. Their candidate edges also compare
unchanged. The solar-battery and fusion-tea `::` sites are enumeration literals and do not traverse
graph reference resolution.

`[AGENT]` **Disposition:** no committed snapshot, computation graph, YAML baseline, or generated
package needs recapture for the qualified behavior measured here. Snapshot replay still cannot
repair a stale edge: if a future kept fixture contains one of the changed topologies, its snapshot
must be recaptured because snapshots serialize final input edges rather than semantic reference
evidence (`src/sysml_codegen/snapshot/instance_graph.py:340-377,523-533`).

## Adjacent Model Trees

The canonical customer roots were loaded semantically, not only searched as text:

| Root | Qualified FREs | Feature-reference candidates |
|---|---:|---:|
| `../fusion-tea/models` | 6 | 0; all 6 are enumeration literals |
| `../fusion-tea-stellarator-mbse-demo/models` | 19 | 0; all 19 are enumeration literals |

The tracked `agentic-mbse` test fixtures have zero textual direct-reference candidates. Six textual
candidates exist only in the vendored SysML standard-library documents
`StateSpaceRepresentation.sysml` and `MeasurementReferences.sysml`; they are outside codegen's
fixture/customer execution corpus and were not used to authorize a codegen behavior change.

## The Broader Implementation Gap

The report's scan request and defect example are authored qualified references. Its preferred repair
condition is broader: any one-segment leaf whose resolved owner is a `PartUsage` would take the new
route. A second census measured that actual predicate:

- 445 direct `FeatureReferenceExpression` sites resolve to a `PartUsage`-owned leaf;
- 256 are the qualified sites assessed above;
- 189 are bare direct references;
- all 189 bare sites are consumed lexically inside their exact owning usage;
- 63 bare sites are calculation inputs and their current/owner-aware final edge wires compare equal;
- 126 bare sites are expression-side consumers, including computed attributes, constraints,
  predicates, and expression terms. Their source/owner relation was recorded, but this scan did not
  join each expression ordinal or alias target to a prospective graph edge.

`[AGENT]` This is not evidence of a likely regression: every bare site is owner-local. It is a
completeness boundary. A shared owner-only branch changes the resolver invariant for those 126
sites, so the qualified-only graph comparison cannot certify it.

Two safe ways forward:

1. Define the product change narrowly as “honor an authored qualified usage-owned direct
   reference.” Carry authored-form evidence into every shared resolver caller, then keep bare forms
   on today's route.
2. Define the invariant broadly as “an exact usage-owned one-segment leaf always anchors its owner.”
   Finish graph joining for the 126 expression-side bare sites and add alias, computed-attribute,
   constraint-binding, and predicate regressions before implementation.

The second option is architecturally cleaner. It requires the broader evidence because the present
corpus has no qualified usage-owned expression-side example to exercise the claimed shared fix.

## Recommendation After the Scan

- `[AGENT]` **Proceed with a separate bounded repair.** The scan found no qualified-reference
  compatibility dependency in kept codegen or customer models. It reproduced exactly the five
  intended changes and no others.
- `[AGENT]` **Keep the repair at elaboration, not extraction.** The report's corrected architectural
  recommendation still stands. Before writing code, decide and state whether the invariant covers
  qualified references only or all usage-owned one-segment leaves.
- `[AGENT]` **Turn `u4`–`u7` into kept regressions.** At minimum, pin exact typed edges plus strict
  and lenient diagnostic multisets. Keep u1–u3b and the definition-qualified controls unchanged.
- `[AGENT]` **Add expression-side regressions even though the corpus contains no affected qualified
  example.** One alias/computed-attribute case and one constraint-side case are required to prove
  that the shared-boundary implementation actually covers the callers used to justify it.
- `[AGENT]` **Do not recapture existing snapshots preemptively.** Recapture only if the implemented
  diff changes a final stored edge; this scan predicts zero such changes in current committed
  snapshots.

## Code and Test References

- `src/sysml_codegen/extraction/binding_evidence.py:59-129,197-231` — exact authored spelling and
  qualified calc-binding evidence.
- `src/sysml_codegen/elaboration/elaborate.py:2062-2083` — one-segment shortcut versus contextual
  path.
- `src/sysml_codegen/elaboration/elaborate.py:2119-2219` — exact root occurrence selection.
- `src/sysml_codegen/elaboration/elaborate.py:2278-2348` — transition and positional leaf lookup.
- `src/sysml_codegen/elaboration/elaborate.py:2417-2433,2575-2602` — alias following and final
  binding-edge assignment.
- `src/sysml_codegen/elaboration/elaborate.py:2435-2554` — independent expression-side caller.
- `tests/helpers/corpus.py:1-26` and `tests/fixtures/v6_recapture_batch/batch.json:2-56` — canonical
  37-family corpus.
- `tests/conformance/test_elaboration_contract_matrix.py:108-160,422-434,812-821` — existing exact
  edge and ambiguity controls.
- `tests/conformance/test_elaboration_shadowing.py:91-102` — qualified shadow edge and diagnostics.
- `tests/conformance/test_elaboration_fail_closed.py:70-92` — definition-qualified ambiguity.

## Limitations

- This was a prospective route composition at `c599cfb`, not an implementation diff. It reused the
  live owner identity, occurrence-selection rules, slot transition, and alias-following semantics,
  but there is no patched before/after full-graph fingerprint yet.
- The exact edge comparison is complete for qualified calculation-input bindings. Constraint and
  computed-attribute qualified sites in the current corpus are definition-owned and therefore
  branch controls, not usage-owned repair cases.
- The 126 bare expression-side usage-owned sites are the remaining evidence task only if the chosen
  implementation changes all usage-owned one-segment references.
- The six vendored-standard-library candidates in `agentic-mbse` were inventoried textually but not
  admitted as codegen execution roots.
