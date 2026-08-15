# Spec: Unit-Lane Port Metadata Defect

**Status:** Complete
**Owner:** Reid W
**Created:** 2026-08-13
**Complexity:** MEDIUM
**Branch:** `item7-rebuild`
**Epic:** CONSTRAINT-SEMANTICS, Item 8

---

## Problem

One modeled design attribute can supply more than one consumer. Projection correctly treats those
consumers as one public `DESIGN_ATTRIBUTE` entry point only when their projected metadata agrees.
The elaborator currently makes agreement impossible for two supported consumer shapes.

A calculation-usage binding gets unit metadata from its exact calculation-definition formal. A
constraint-formal binding does not: the metadata construction in
`src/sysml_codegen/elaboration/elaborate.py:1670-1698` populates `unit` only for a `CalcNode`. An
input to a computed design attribute likewise gets `unit=None` at
`src/sysml_codegen/elaboration/elaborate.py:2381-2410`. `PortMetadata.unit` already survives the
instance-graph codec (`src/sysml_codegen/snapshot/instance_graph.py:222-289`), so this is a live
elaboration gap, not a missing snapshot field.

Projection compares complete entry-point candidates and refuses unequal metadata at
`src/sysml_codegen/elaboration/project.py:365-399`. That fail-closed behavior is correct. The
defect is that valid inputs reach it with one real unit string and one manufactured `None`.

Item 5 measured both customer-shaped consequences before filing this item:

- A9's relative `ProductWithinBand` form binds `pumping_speed_total` and `n_pumps` to constraint
  formals while those attributes also feed `VacuumPumpPower`. P3/P3b refuse on
  `CATFMFEVacuum__catf_vacuum_pumping__n_pumps` with `SI_RENDERING_COLLISION`.
- A radial-build derivation such as `outer_radius = inner_radius + thickness` reads attributes
  that also feed `TorusMinorRadius`. P4a/P5 refuse on
  `CATFMFERadialBuild__catf_radial_build__plasma_region__inner_radius` with the same code. Removing
  the design attributes' `[m]` literals does not help; the calculation formal still contributes
  `m` while the computed-expression port contributes `None`.

This blocks correct modeling and the already-ruled A5/A6/A9 follow-on. The delivery boundary is
**[INHERITED: `.project/backlog/epic_constraint_semantics_contract.md`, Item 8; source grade
`[AGENT] (ratified by owner, 2026-08-13)`]**: Item 8 fixes the unit lane and lands standalone. It
does not revive joint delivery with Item 6.

## Success Criteria

- [x] **[INHERITED: epic Item 8 scope 1 and SC 1]** Two kept, licensed characterizations land red
      before production code changes: the A9 constraint-formal shape and the radius-derivation
      computed-attribute shape. Each initially refuses for the named `SI_RENDERING_COLLISION`,
      then admits after the fix without changing the model shape being characterized.
- [x] **[INFERRED: Item 5 P3/P3b/P4a/P5 and the exact extracted formal metadata]** The admitted A9
      characterization mints exact unit text `m³/s` for its volumetric-flow ports and
      `Dimensionless` for its count and relative-tolerance ports. The radius characterization
      mints exact unit text `m` for the design-attribute entry points read by the derivation and
      by `TorusMinorRadius`.
- [x] **[INHERITED: epic Item 8 scope 2; Item 6 R5]** Constraint-formal versus calculation-usage
      agreement, constraint-formal versus calculation-usage disagreement, computed-attribute
      versus calculation-usage agreement, and computed-attribute versus calculation-usage
      disagreement each have a kept test. Agreement produces one shared entry point;
      disagreement produces the precise fail-closed behavior in Known Requirements.
- [x] **[INHERITED: epic Item 8 SC 3]** Licensed live elaboration, an in-place v6 snapshot read,
      and a relocated v6 snapshot read carry identical `PortMetadata.unit` values at the exact
      consumer ports and project identical `EntryPoint.unit_text` values.
- [x] **[INFERRED: epic Item 8 scope 3, current tracked tree, and spec-review L3-1]** A
      machine-checked pre-change inventory proves that its assessment rows are exactly equal to
      the version-controlled `tests/fixtures/**/instance_graph_snapshot.json` path set: no
      missing, extra, or duplicate row. That set measures 23 paths on 2026-08-13. The final
      inventory repeats the same set-equality check against the then-current tracked path set and
      records the final count and every path added or removed. The historical accepted-batch
      subset check does not substitute for this gate.
- [x] **[INHERITED: epic Item 8 scope 3 and SC 2]** Every tracked snapshot receives a
      fingerprint/churn disposition. A tracked snapshot is stale when final live elaboration
      would change its exact instance-graph payload or any relevant `PortMetadata.unit` value.
      If at least one is stale, exactly one reviewed final-schema recapture covers all stale
      snapshots after implementation and tests are final. If none is stale, no existing snapshot
      is recaptured. Envelope byte movement, including `captured_at`, and projected population
      counts are evidence to record, not the recapture trigger.
- [x] **[INHERITED: epic Item 8 scope 4 and SC 4; Item 6 start gate]** Item 8's final
      `verification.md` first publishes the evidence bundle defined below. After the reviewed
      implementation commit exists, the Item 8 delivery makes a narrow documentation-only
      handoff into the named Item 6 R5/start-gate records. Those records cite the immutable full
      commit SHA, exact kept-test nodes and claims, and Item 8's v3 recapture disposition. The
      handoff does not authorize any Item 6 implementation.
- [x] **[INFERRED: spec re-review L3-1]** The handoff carries Item 8's sorted final tracked-
      snapshot path set and measured count. Item 6's future graph-v4 recapture evidence proves
      exact coverage of its own then-current tracked snapshot path set, not a reused numeric
      count or the historical accepted-batch subset.
- [x] **[INHERITED: epic Item 8 final SC; qualified by the surfaced baseline conflict below]**
      Focused licensed tests and the default maintained `pytest tests/` lane pass. The all-marker
      licensed suite is run before and after the change and has zero new failures. Its
      unconditional-pass conclusion remains parked while the known collection-order failure is
      unresolved. Ruff and mypy are zero-new; the snapshot checks and `git diff --check` pass.
      `verification.md` records every invocation and every exact result count required below.

## Known Requirements

### Delivery and ownership

- **[INHERITED: epic Item 8; source grade `[AGENT] (ratified by owner, 2026-08-13)`]** This is a
  standalone defect fix. Item 8 owns `PortMetadata.unit`, the A9/radius characterizations, the
  four agreement/disagreement cases, three-route unit parity, and the conditional reviewed v3
  recapture.
- **[INHERITED: epic Item 8 delivery ruling; source grade `[AGENT] (ratified by owner,
  2026-08-13)`]** Item 6's production implementation is not authorized by this item. Avoiding a
  possible later graph-v4 recapture is not authority to join deliveries. Only a new owner ruling
  may change that boundary.
- **[INHERITED: `.project/active/calcdef-constraint-gate-design/design.md`, R5]** A later,
  separately authorized Item 6 may add calc-input `formal_provenance`, but it must preserve Item
  8's unit text, deduplication behavior, and disagreement refusal. The instance graph remains the
  single runtime authority for the combined `PortMetadata`.

### Characterizations and unit source

- **[INHERITED: epic Item 8 scope 1 and Item 5 P3/P3b/P4a/P5]** Kept failing
  characterizations come first. Their red evidence records the exact test node, exception type,
  `SI_RENDERING_COLLISION`, and colliding public entry-point name before production code changes.
  A test made green by weakening or replacing the source shape does not discharge this
  requirement.
- **[INFERRED]** The kept characterizations use focused fixture models that preserve the measured
  topology without editing `catf_mfe_gated`. The A9 fixture has one design attribute consumed by a
  calculation input and by a bound constraint formal. The radius fixture has `inner_radius` and
  `thickness` read by a computed `outer_radius` while at least one of those sources also feeds a
  `TorusMinorRadius` calculation. This is the narrowest form that reproduces each defect while
  leaving Item 9's CATF migration untouched.
- **[INFERRED]** Each consumer port carries the unit authored for that lane, using the product's
  existing extraction semantics: a calculation binding uses the exact calculation-definition
  formal; a constraint binding uses the exact effective constraint-definition formal; a computed
  expression input uses the exact referenced design attribute. That exact unit must be present on
  the corresponding port in the sealed `InstanceGraph` consumed by projection and snapshot
  capture. It is not copied from a sibling consumer, inferred from arithmetic, converted, or
  normalized. Design owns helper placement and the order in which elaboration finalizes the
  metadata.
- **[HARD]** Unit text is exact metadata. Existing extraction can obtain it from feature typing,
  source syntax, or supported documentation/comment syntax
  (`src/sysml_codegen/extraction/extractor.py:551-712`). This item does not invent a unit, infer
  one from arithmetic, convert one, or silently normalize unequal spellings. The characterization
  models therefore author the exact expected strings: `m³/s`, `Dimensionless`, and `m`.
- **[INFERRED]** The A9 characterization asserts all four formal lanes, not only the first
  collision encountered: `observed` and `each_capacity` carry `m³/s`; `count` and `rel_tol` carry
  `Dimensionless`. The radius characterization asserts `m` on every minted design-attribute
  entry point consumed by the derivation. This prevents a first-collision-only cure.

### Agreement and refusal

- **[HARD]** One semantic design-attribute source projects to one public entry point. If all
  candidate metadata is equal, including equal non-null unit text or `None` on every lane,
  projection deduplicates the candidates and keeps one `DESIGN_ATTRIBUTE` entry point with that
  exact `unit_text` (`src/sysml_codegen/elaboration/project.py:365-399`).
- **[INFERRED]** Unit disagreement means any unequal pair: different non-null strings, or a
  non-null string versus `None`. Projection must not choose first-wins, erase both units, copy the
  calculation unit over the other lane, or mint two public keys.
- **[HARD]** Disagreement refuses the whole projection with `ProjectionError` carrying
  `SI_RENDERING_COLLISION`. The diagnostic names the conflicting public entry point and reports
  conflicting projected metadata. No computation graph or generated package is returned. Through
  public snapshot capture, the same non-projectable graph is refused before a snapshot write and
  an existing destination remains unchanged
  (`docs/architecture/reference/27-snapshot-generation.md`, "Three routes" and atomic capture).
- **[INFERRED]** Agreement/disagreement is pinned in both directions for both repaired lanes. A
  constraint-only or computed-only green case is insufficient because the defect appears when one
  public source is shared with a calculation consumer.

### Snapshot parity and churn control

- **[HARD]** `PortMetadata.unit` is already a required field in the `instance-graph/v3` codec and
  the v6 envelope carries that graph. In-place and relocated reads therefore reproduce the unit
  value rather than re-extracting it from a model tree
  (`src/sysml_codegen/snapshot/instance_graph.py:222-289`; `docs/architecture/reference/27-snapshot-generation.md`).
  This item populates an existing field; it does not authorize a graph-schema or envelope-version
  bump.
- **[INHERITED: epic Item 8 SC 3]** The parity check compares three distinct routes: licensed
  live elaboration; the captured snapshot loaded where it was written; and the same snapshot
  copied to a different directory and loaded without relying on the source tree. It compares the
  exact relevant `PortMetadata` records before projection and the public entry-point unit text
  after projection.
- **[INHERITED: epic Item 8 scope 3; Item 2 recapture precedent]** Before production edits, record
  the complete tracked v6 snapshot inventory. For every existing snapshot record its path,
  envelope SHA-256, instance-graph fingerprint, source-manifest fingerprint, projected counts,
  and relevant non-null/null unit paths. Re-run the same inventory against the final behavior and
  list every changed fixture and field.
- **[HARD]** The tracked repository state on 2026-08-13 contains 23
  `tests/fixtures/**/instance_graph_snapshot.json` paths. The accepted v6 recapture batch covers
  only 15 of them; its 37-row corpus check also includes refused models without committed
  snapshots. The inventory gate therefore compares two complete path sets, not counts alone:
  pre-change assessment rows equal the 23-path tracked set, and final assessment rows equal the
  final tracked set. Both checks fail on any missing, extra, or duplicate path. The final record
  gives the exact count and names every addition or removal with its authority. Item 8 does not
  implicitly authorize deleting an existing snapshot.
- **[INFERRED]** A source-manifest fingerprint change is not expected when only code changes. A
  graph fingerprint, envelope digest/SHA, computation digest, or projected schema byte may move
  when newly populated units are semantic output. The assessment distinguishes those derived
  movements from unrelated module, edge, value, catalog, ordering, or source changes; any
  unrelated movement is surfaced rather than accepted as baseline churn.
- **[INHERITED: epic Item 8 standalone ruling; source grade `[AGENT] (ratified by owner,
  2026-08-13)`]** Decide recapture from semantic snapshot staleness. A path is stale if the final
  live behavior would change the committed snapshot's exact instance-graph payload or any
  relevant `PortMetadata.unit` value. Do not decide from projected computation-graph population,
  projected counts, or whether a committed envelope byte has already moved; a recapture itself
  changes envelope data such as `captured_at`. If no tracked path is stale, do not recapture an
  existing snapshot. If one or more are stale, perform exactly one reviewed final-schema
  recapture after field behavior and tests are final, covering every stale path and no accepted
  interim baseline. The review records per path the old/new SHA and graph fingerprint, exact
  unit paths added or changed, projected-count evidence, three-route parity, and every explained
  envelope or manifest change. Update affected batch-manifest digests/outcomes in that same
  recapture. New characterization fixtures do not turn an intermediate capture into an accepted
  baseline.

### Item 6 evidence handoff

- **[INHERITED: `.project/active/calcdef-constraint-gate-design/implementation-item.md`, Item 8
  ownership gate]** Item 8's final `verification.md` gives Item 6 the exact file path and node ID
  for five kept proofs: constraint/calc agreement; constraint/calc disagreement; computed/calc
  agreement; computed/calc disagreement; and live/in-place/relocated `PortMetadata` parity.
- **[INFERRED]** The citation bundle also names the A9 and radius characterization nodes, their
  before/after result, exact expected unit strings, exact disagreement exception/code and public
  key, the sorted pre-change and final complete snapshot path sets, their measured counts,
  set-equality evidence, and Item 8's v3 recapture decision and manifest when one exists. Item 6
  cites this bundle rather than re-characterizing or reimplementing the unit lane. A count without
  the corresponding exact path set does not satisfy the bundle.
- **[INHERITED: Item 6 start gate]** A branch name is insufficient. The handoff happens in this
  order: Item 8's final `verification.md` publishes the complete evidence bundle; review produces
  an immutable implementation-and-test commit; then a narrow documentation-only edit updates
  `.project/active/calcdef-constraint-gate-design/design.md` section **R5. Item 8 prerequisite and
  ownership** and `.project/active/calcdef-constraint-gate-design/implementation-item.md`
  sections **Start gate and exact dependency pins** and **Item 8 ownership gate**. Those records
  receive the full commit SHA and exact test nodes.
- **[INFERRED: spec re-review L3-1]** The same documentation-only handoff corrects Item 6 design
  R5, R8, and the recapture entry in its component manifest, plus implementation-item Phase 4.
  It must not mechanically replace `21` with `23` or with Item 8's eventual final count. Instead,
  the named records receive the exact unit/refusal claims, Item 8 final tracked-inventory path set
  and measured count, and Item 8's v3 recapture disposition. Those records also require Item 6's
  separately authorized graph-v4 recapture to derive the expected
  path set from the version-controlled `tests/fixtures/**/instance_graph_snapshot.json` inventory
  at Item 6's own immutable pre-recapture baseline. At final verification:

  - the per-path disposition rows equal the union of Item 6's pre-change and final tracked path
    sets, with no missing, extra, or duplicate path;
  - every final tracked snapshot path has one reviewed graph-v4 recapture artifact/evidence row,
    and that row set equals the final tracked path set; and
  - every path addition or removal is named with its authority and explains the set drift.

  The implementation mechanism remains Item 6's design choice. The current
  `tests/conformance/test_v6_recapture_batch.py` and its manifest prove only the 15 captured
  corpus paths and explicitly exclude eight other tracked snapshots. They may remain a subset
  gate, but they cannot satisfy or be cited as proof of the complete-set obligation unless Item 6
  broadens or replaces that coverage and the resulting gate proves the equalities above.
- **[INFERRED]** The handoff treats the dated 23-total/15-subset measurements recorded under
  Snapshot parity and churn control as evidence, not durable scope. Item 8 re-derives its final
  v3 path set at its reviewed commit. Item 6 later re-derives its graph-v4 path set at its own
  baseline; drift from Item 8's set is recorded rather than hidden by reusing either count.
- **[INHERITED: epic Item 8 standalone ruling]** This documentation handoff does not authorize
  Item 6 production code, `formal_provenance`, graph v4, catalog 4, TEAx changes, a v4 recapture,
  Item 7 documentation, or Item 9 migration. Item 6 remains blocked until its own authority and
  the reviewed Item 8 descendant both exist.
- **[INHERITED: epic Item 8 standalone ruling; source grade `[AGENT] (ratified by owner,
  2026-08-13)`]** The recapture duties remain separate. Item 8 assesses final v3 semantic churn
  across its complete tracked inventory and, if stale paths exist, performs its one reviewed v3
  recapture for those paths. A later authorized Item 6 owns the distinct graph-v4 migration. Item
  8 neither performs nor authorizes that future v4 work.

### Verification record

- **[HARD]** Licensed test commands use
  `/home/reid/1cfe/item7-rebuild-venv/bin/python -m pytest` after exporting
  `/home/reid/1cfe/agentic-mbse/.env`. A run with any `no live syside license` skip line is not
  reported as a licensed pass.
- **[INFERRED]** `verification.md` records a pre-change and final baseline. Focused runs include
  both characterization nodes, all four agreement/disagreement nodes, the three-route parity
  node, graph round-trip/codec coverage, and any affected recapture-batch checks. The exact node
  list and exact collected/passed/skipped/deselected/failed/error counts are recorded.
- **[INFERRED]** At both checkpoints, `verification.md` records the complete-inventory gate's
  exact invocation, tracked-path count, assessment-row count, missing/extra/duplicate counts, and
  path additions/removals. It separately records the accepted-batch subset check's exact pytest
  counts. A green subset check cannot stand in for the complete-inventory result.
- **[INHERITED: epic Item 8 final SC]** Run and record both maintained licensed lanes before and
  after the change: the default `pytest tests/` marker set, which must pass, and the all-marker
  `pytest tests/ -m ""` suite. For each invocation record collection total, passed, skipped,
  deselected, xfailed, xpassed, failed, and error counts, plus the license-skip-line count. The
  final all-marker failure node set must contain no node absent from its pre-change baseline.
- **[HARD]** The pre-existing baseline in `.project/CURRENT_WORK.md` and Item 5's
  `verification.md` records one unowned all-marker collection-order failure:
  `tests/execution/test_fusion_tea_real_teax.py::test_the_lane_runs_the_real_simkit`. Reproduce the
  node in the pre-change and final full-suite outputs and run it in isolation at both baselines,
  where the recorded behavior is pass. Record its exact counts. Do not absorb a cure into Item 8
  without separate authority.
- **[INHERITED: epic Item 8 final SC]** Record exact results for changed-file ruff, `ruff check
  src/`, `mypy src/`, the license-free snapshot batch check, and `git diff --check`. Ruff and mypy
  are zero-new against the measured pre-change baseline; touched Python files introduce no new
  finding. For each static/diff command, record its exit code and exact checked-file, diagnostic,
  error, or whitespace-failure count as applicable. If recapture fires, also record the single
  licensed public recapture command and its exact captured/refused/deviation counts.

## Surfaced Premise Conflict

### Full-suite pass versus the current all-marker baseline

- **[INHERITED: epic Item 8 final SC; source grade `[AGENT] (ratified by owner, 2026-08-13)`]**
  Item 8's source success criterion says the full licensed suite passes.
- **[HARD]** The current all-marker licensed suite has the collection-order failure named above.
  It reproduces in the whole set and passes in isolation. The failure predates Item 8 and has no
  owner (`.project/CURRENT_WORK.md`; Item 5 `verification.md`).
- **[INFERRED]** These premises cannot both be reported as satisfied while that failure remains.
  Item 8 therefore requires zero new full-suite failures and preserves exact pre/final evidence,
  but it does not relabel the known failure as a pass. The unconditional full-suite-pass
  conclusion is parked until either a separately authorized change removes the failure or the
  owner explicitly dispositions the source criterion. This authority conflict does not enlarge
  Item 8 into a test-order repair.

## Non-Goals

- **[INHERITED: epic Item 8 standalone ruling]** Implementing Item 6's calculation-definition gate
  capability, calc-input `formal_provenance`, graph-v4 identity, catalog 4, TEAx consumer changes,
  or later v4 recapture.
- **[INHERITED: epic Items 8–9 dependency boundary]** Executing Item 9's held A5/A6/A9 CATF
  migration. This item proves those shapes can be modeled; Item 9 changes `catf_mfe_gated` under
  the recorded disposition.
- **[INFERRED]** Unit conversion, dimensional analysis of constraint bindings, arithmetic unit
  inference, spelling normalization, or changes to executable-profile operand-category decisions.
  Units remain exact documentation metadata on ports.
- **[INFERRED]** Weakening or replacing projection's metadata-collision refusal. Genuine
  disagreement remains a whole-model error.
- **[INHERITED: stage input]** Product or UX design. This is a compiler metadata defect with
  testable public behavior.

## Open Questions / Deferred to design

- **[INFERRED]** The focused fixture and test file names. Design may use one fixture with both
  consumer lanes or two small fixtures, but the five Item 6-consumed proof nodes and two
  customer-shaped characterizations must remain individually addressable.
- **[INFERRED]** The smallest code owner for applying the existing unit-extraction rule to
  arbitrary live features. The spec fixes the semantic source and result; design chooses whether
  to reuse an extractor helper, introduce an elaboration-local adapter, or take another equally
  narrow route.
- **[INFERRED]** The final recapture set. It is determined mechanically from the complete pre/post
  snapshot inventory, not chosen in advance or limited to the historical 15-fixture accepted
  batch.

**[INFERRED]** No open item requires owner authority before technical design. If the known
all-marker failure remains, owner disposition or a separately authorized cure is required before
Item 8 can claim the inherited unconditional full-suite-pass criterion and close.

## Spec Review Disposition

| Finding | Disposition | Auditable requirement |
|---|---|---|
| L1-1: recapture trigger was narrowed to projected graph/byte movement | **Resolved.** Staleness now depends on the exact instance-graph payload and relevant unit fields. Envelope bytes and projected counts are evidence only. | Success Criteria, churn criterion; Snapshot parity and churn control |
| L1-2: unconditional full-suite pass conflicts with the known baseline | **Surfaced; dependent conclusion parked.** Default tests must pass and the all-marker suite must be zero-new. The inherited unconditional-pass claim awaits owner disposition or a separately authorized cure. | Verification record; Surfaced Premise Conflict |
| L2-1: the spec froze elaboration timing and repair placement | **Resolved.** The contract names the sealed-graph observable boundary and defers helper placement and finalization order to design. | Characterizations and unit source |
| L3-1: no complete gate covered every tracked snapshot | **Resolved.** Pre-change and final path-set equality are mandatory. The current 23-path baseline, final count, additions, removals, and per-path dispositions are recorded. | Success Criteria, inventory criterion; Snapshot parity and churn control |
| L3-2 / re-review L3-1: Item 6 handoff lacked complete future recapture coverage | **Resolved.** The handoff transfers sorted paths plus measured counts, forbids count-only substitution, and requires Item 6's future v4 evidence to equal its own then-current tracked snapshot set. The 23 tracked and 15 batch-covered paths are 2026-08-13 measurements; Item 8's v3 and Item 6's v4 recapture duties are separate. | Item 6 evidence handoff |

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_constraint_semantics_contract.md` — Item 8
- **Stage-required reading:**
  - `.project/CURRENT_WORK.md` — accepted whole-set collection-order baseline and active item state
  - `.project/completed/20260813_catf-constraint-policy-acceptance/design.md` — P3/P3b/P4a/P5,
    D-S1/D-S2, route and recapture precedents
  - `.project/completed/20260813_catf-constraint-policy-acceptance/owner-disposition.md` — ruled
    A5/A6/A9 intent and source grades
  - `.project/completed/20260813_catf-constraint-policy-acceptance/verification.md` — default and
    all-marker licensed counts and the known isolated-pass/whole-set-failure evidence
  - `.project/active/calcdef-constraint-gate-design/design.md` — R5 ownership and dependency
  - `.project/active/calcdef-constraint-gate-design/implementation-item.md` — start gate and exact
    Item 8 evidence consumers
  - `.project/research/20260812-101200_constraint-semantics-end-to-end.md`
  - `docs/architecture/modeling-assumptions.md` §§3, 8
  - `docs/architecture/reference/16-computed-attributes.md`
  - `docs/architecture/reference/27-snapshot-generation.md`
- **Current code:** `src/sysml_codegen/elaboration/elaborate.py`,
  `src/sysml_codegen/elaboration/project.py`,
  `src/sysml_codegen/snapshot/instance_graph.py`
- **Test patterns:** `tests/conformance/test_snapshot_v6_routes.py`,
  `tests/conformance/test_constraint_usage_domain_parity.py`,
  `tests/conformance/test_exact_projection_aggregation.py`,
  `tests/conformance/test_v6_recapture_batch.py` (15-snapshot corpus subset only)
- **Product lens:** `.project/active/unit-lane-port-metadata/product-lens.md`
- **Spec review:** `.project/active/unit-lane-port-metadata/spec-review.md`
- **Design:** `.project/active/unit-lane-port-metadata/design.md` (to be created)

---

**Next Steps:** Re-run `my-spec-review` against this revision. Do not begin design until the review
accepts the five dispositions above. Product design is unnecessary for this defect.
