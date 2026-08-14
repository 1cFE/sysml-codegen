# Audit: Unit-Lane Port Metadata Defect

**Verdict:** Certify
**Audited:** 2026-08-13
**Branch:** `item7-rebuild`
**Commit:** `62a07e5c870158672eb100f1cba73adfe4c9df28`

---

## The Point

One modeled design attribute can feed a calculation, a constraint formal, and a computed
expression while remaining one public design input. Each consumer port must carry the exact unit
text owned by its semantic source declaration. The tool must neither infer nor convert that text.
Equal complete metadata deduplicates to one public entry point; unequal metadata refuses the whole
projection. The decided graph must preserve that result identically through licensed live
elaboration, in-place v6 snapshot replay, and relocated v6 snapshot replay.

## Summary

The frozen implementation delivers the Item 8 contract without widening it. Declaration identity
owns unit selection, graph-v3 carries the existing unit field, the projector keeps its fail-closed
equality rule, and v6 envelope build and load now own projectability certification before capture
can write. Fresh licensed and static checks reproduce the recorded result: no Item 8 regression,
no stale tracked snapshot, and only the inherited all-marker collection-order failure.

No blocking or minor implementation finding remains. The seven documentation/tracking edits that
were present after the freeze contain no production, test, fixture, or snapshot change and are
consistent with the frozen commit.

## Product Judgment

**This is the right piece of work.** The implementation restores the documented product model:
one design attribute has one public identity, authored unit text is metadata rather than conversion
behavior, and snapshot replay consumes a decided projectable graph. It adds no syntax, unit
semantics, user choice, or competing runtime authority.

The complete item ledger and the parent epic ledger were scanned. The current audit block is
`CLEAR`; the earlier design-review findings are `DISPOSED` by the revised design and final approved
review. No unresolved item or epic `BLOCK` exists. None of the audit product-drift smells fired:
tests do not select among duplicate outputs, no consumer class receives a semantic exemption, no
parallel representation needs manual synchronization, and the known all-marker baseline does not
preserve behavior contrary to the product goal
(`.project/active/unit-lane-port-metadata/product-lens.md`).

## Findings

### Plan completion

All five phases are complete and independently checked against their recorded completion notes
(`plan.md:892`, `plan.md:917`, `plan.md:938`, `plan.md:967`, `plan.md:993`).

1. The untouched-tree baseline and complete 23-path inventory exist, use Git's tracked set as the
   authority, and distinguish the historical 15-path subset.
2. The A9 and radius customer shapes are kept and are red against the parent production tree.
   The final frozen tree admits both with their authored units.
3. One shared extractor and the closed effective-formal selector implement the declaration-owned
   unit law, including redefinition and alias identity.
4. Envelope build/load, capture, and CLI refusal have kept tests for ordered diagnostics and
   no-overwrite behavior.
5. Final inventory, route parity, generated-entry-point evidence, licensed suites, static
   comparisons, freeze commit, and the narrow Item 6 handoff are complete.

No placeholder phase, unchecked plan box, or implementation TODO remains.

### Spec conformance

#### Success criteria

| Criterion | Result | Independent evidence |
|---|---|---|
| SC1: two red-first customer shapes | **Met.** | Both kept nodes fail against parent production with `ProjectionError` / `SI_RENDERING_COLLISION` and pass at the freeze. The radius key is `CATFMFERadialBuild__catf_radial_build__plasma_region__inner_radius`; the final A9 fixture reaches `...__pumping_speed_total` first against the parent, while the recorded earlier formal ordering reached `...__n_pumps` (`tests/conformance/test_unit_lane_port_metadata.py:109`, `:136`; `verification.md`, “Phase 2 red characterizations”). |
| SC2: exact A9/radius unit text | **Met.** | A9 asserts `m³/s` and `Dimensionless` on all four formal lanes and the public entries; radius asserts `m` on derivation and TorusMinorRadius inputs (`test_unit_lane_port_metadata.py:109-154`). |
| SC3: four agreement/disagreement cases | **Met.** | Constraint/calc and computed/calc agreement each produce one entry; both disagreement directions refuse with the exact code, key, and detail (`test_unit_lane_port_metadata.py:157-203`). |
| SC4: three-route parity | **Met.** | Licensed live, in-place v6, and source-independent relocated v6 routes compare exact port records, projected units, and cardinality (`test_unit_lane_port_metadata.py:387-445`). |
| SC5: exact complete inventory | **Met.** | Fresh assessment is 23 tracked / 23 assessed / 0 missing / 0 extra / 0 duplicate; pre and final committed path sets are equal (`test_v6_snapshot_inventory.py:28-108`). |
| SC6: semantic recapture decision | **Met.** | All 23 rows have exact graph/unit dispositions and zero stale rows. Therefore no recapture was allowed or performed. Computation/generated output remains evidence only (`assess_v6_snapshot_churn.py:291-375`). |
| SC7: immutable Item 6 handoff | **Met.** | The Item 6 design and implementation item cite the full freeze SHA, exact kept nodes and claims, complete final path set, and zero-v3-recapture result. The edits are documentation-only. |
| SC8: future complete-set proof | **Met.** | Item 6's future graph-v4 record must derive and prove equality against its own then-current tracked set; it cannot reuse 23 or the 15-path subset (`.project/active/calcdef-constraint-gate-design/design.md:193-220`, `:309-311`; `implementation-item.md:50-79`, `:389-391`). |
| SC9: final gates and baseline comparison | **Met as qualified by the spec's surfaced premise conflict.** | Focused and default licensed lanes pass; all-marker has exactly the one inherited failing node and that node passes alone; ruff and mypy are zero-new; inventory and diff checks pass. The audit does not relabel the inherited all-marker failure as a pass. |

#### Tagged requirements

Every approved tagged requirement was traced. The grouped results below preserve each requirement's
distinct acceptance condition.

**Delivery and ownership (`spec.md:98-111`)**

- **Met:** Item 8 alone owns the two unit lanes, their customer shapes, four collision proofs,
  three-route parity, and the conditional v3 recapture.
- **Met:** no Item 6 production, calc-input `formal_provenance`, graph-v4, or catalog-4 work exists
  in the freeze.
- **Met:** the Item 6 handoff preserves Item 8's exact unit, deduplication, refusal, and one-graph
  authority while leaving later implementation separately authorized.

**Characterizations and unit source (`spec.md:113-142`)**

- **Met:** both final kept customer nodes are red against the parent implementation and green at
  the freeze; neither edits `catf_mfe_gated`.
- **Met:** the A9 fixture retains one source shared by calculation and constraint consumers; the
  radius fixture retains computed derivation plus a TorusMinorRadius consumer.
- **Met:** calc ports use the exact selected calculation formal, constraint ports use the selected
  effective constraint formal from `definition.usages`, and computed ports use the exact referenced
  declaration (`elaborate.py:375-418`, `:1728-1845`, `:1932-1975`, `:2494-2510`).
- **Met:** the shared extractor returns exact authored text with the existing precedence and no
  inference, conversion, or normalization (`feature_metadata.py:57-68`; `extractor.py:553-558`).
- **Met:** the tests assert all four A9 lanes and every minted radius entry, so the cure is not
  limited to the first collision.

**Agreement and refusal (`spec.md:144-161`)**

- **Met:** equal complete candidates deduplicate to exactly one `DESIGN_ATTRIBUTE` with unchanged
  `unit_text`; non-null/non-null and non-null/`None` disagreement are both pinned
  (`project.py:365-399`; `test_elaboration_projection.py:159-181`).
- **Met:** projection remains whole-model fail-closed with `SI_RENDERING_COLLISION`; it neither
  chooses first-wins, erases units, nor mints a second key.
- **Met:** constraint/calc and computed/calc proofs cover agreement and disagreement, not
  single-consumer green cases.
- **Met:** non-projectability returns no computation graph/package and public capture refuses before
  a missing or sentinel destination can change (`test_unit_lane_port_metadata.py:350-384`).

**Snapshot parity and churn (`spec.md:163-206`)**

- **Met:** `PortMetadata.unit` remains the existing required graph-v3 field and v6 payload member;
  the graph, envelope, and projector markers remain `instance-graph/v3`, v6, and
  `instance-projector/v1` (`instance_graph.py:71`, `:228`; `envelope.py:104`; `project.py:87`).
- **Met:** in-place and relocated loads reproduce graph metadata without model re-extraction, and
  the three-route test compares port metadata before projection and public units after it.
- **Met:** pre and final inventories record all required hashes, fingerprints, units, projected
  counts, computation evidence, and generated-entry-point evidence for all 23 tracked paths.
- **Met:** exact tracked-path/row equality, uniqueness, additions, and removals are checked. Both
  sets are the same 23 paths; additions and removals are empty. The 15-path batch remains only a
  subset proof.
- **Met:** unrelated source, module, edge, value, catalog, ordering, and manifest movement is zero.
- **Met:** staleness is triggered only by exact live graph payload or relevant unit movement. It is
  not broadened by envelope, computation, generated-output, or projected-count evidence. The empty
  stale set correctly caused zero capture/recapture and zero tracked snapshot or manifest diff.

**Item 6 handoff (`spec.md:208-259`)**

- **Met:** all five required proof-node IDs and their exact claims are named.
- **Met:** A9/radius before-and-after behavior, exact unit strings, refusal evidence, both complete
  path sets, counts, equality result, and zero-recapture disposition are carried.
- **Met:** the evidence bundle precedes the immutable freeze; only then do the named Item 6 records
  receive the full SHA and node IDs.
- **Met:** R5, R8, the component manifest recapture row, and implementation Phase 4 require Item
  6's future per-path rows and graph-v4 evidence to equal its own baseline/final tracked sets.
- **Met:** 23-total and 15-subset are dated evidence, not durable future scope.
- **Met:** the handoff contains no authority or implementation for Item 6, Item 7, Item 9, TEAx,
  graph v4, catalog 4, or a future recapture.
- **Met:** Item 8's v3 zero-recapture disposition and Item 6's possible future graph-v4 migration
  remain separate duties.

**Verification record and surfaced premise (`spec.md:261-308`)**

- **Met:** licensed commands used the pinned environment and have zero license-skip lines.
- **Met:** focused coverage contains both customer nodes, all four collision cases, route parity,
  graph codec/round-trip, envelope/capture/CLI, inventory/subset, and generated-entry-point nodes,
  with exact outcomes recorded.
- **Met:** pre and final complete inventories record exact commands and all set cardinalities;
  subset results are reported separately.
- **Met:** default and all-marker lanes are recorded before and after with exact outcome counts.
  The final all-marker failure set adds no node.
- **Met:** the inherited failing node appears in both full outputs and passes in isolated all-marker
  runs; no cure was absorbed into Item 8.
- **Met:** changed-file ruff is clean; full ruff is the same 12 `UP042` findings; mypy improves from
  55 to 52 errors in the same 11 files; `git diff --check` is clean.
- **Met:** the premise conflict is reported honestly. Default must pass, all-marker must be
  zero-new, and unconditional all-marker pass remains parked.

**Non-goals and design deferrals (`spec.md:309-342`)**

- **Met:** no Item 6 implementation, Item 9 migration, unit conversion/dimensional inference,
  collision weakening, or product/UX work landed.
- **Met:** the approved design resolved the deferred fixture split, helper placement, and
  mechanically determined recapture set without changing their specified semantic outcomes.

### Design conformance

Implementation follows all nine decisions and all twenty required invariants
(`design.md:154-194`, `design.md:323-350`). In particular:

- The effective-formal selector builds a closed map from the selected definition's native
  `usages`, filters it through loaded-user identities, and uses the slot index. It does not fall
  back to a slot root (`elaborate.py:375-418`).
- Redefined calculation and constraint formals use the selected declaration. The alias proof keeps
  the referenced declaration as metadata owner while its edge resolves to the source
  (`test_unit_lane_port_metadata.py:258-348`).
- Exact unit extraction is shared once; elaboration selects identity and the helper extracts text.
  There is no sibling lookup or graph repair pass (`feature_metadata.py:57-68`).
- Projector equality/refusal and all schema markers remain unchanged. Envelope build and decoded
  load call one certifier which preserves ordered diagnostics (`envelope.py:156-167`, `:184-224`,
  `:291-316`). Capture only consumes the certified envelope, and CLI renders the public error
  without a traceback (`capture.py:17-37`; `cli/__init__.py:884-935`).
- Computation and generated-entry-point digests are recorded for every projectable inventory arm,
  but `is_stale` still depends only on graph/unit movement
  (`assess_v6_snapshot_churn.py:291-375`).

No undocumented design deviation was found.

### Code integrity

No issue found.

- The new helpers have narrow, single-purpose interfaces. There is no sentinel-selected mode,
  parameter sprawl, consumer policy hidden in a utility, duplicate selection rule, or deep nested
  repair path.
- Missing declaration identity fails through the existing invariant errors; a real declaration
  without authored unit is the only legitimate `None`. No defensive default hides an identity
  failure.
- The inventory script's broad evidence-capture handler records the exception type, message, and
  ordered diagnostics rather than returning a false projectable default
  (`assess_v6_snapshot_churn.py:135-148`). All 46 committed/live projection arms were independently
  projectable in the final inventory.
- Search of the frozen diff found no placeholder, TODO, FIXME, xfail, weakened assertion,
  compatibility shim, or production `pass`. New tests pin exact strings, IDs, cardinalities,
  bytes, ordered diagnostics, and destination state.
- The commit has no production surface outside the declared extraction, elaboration,
  orchestration, envelope, and CLI owners. It contains no Item 6 implementation and no Item 7,
  Item 9, TEAx, main, push, close, or pre-PR work.

---

## Certification

Fresh audit checks at `62a07e5c870158672eb100f1cba73adfe4c9df28`:

- Freeze: `HEAD` equals the required commit. The seven intended post-freeze edits listed in
  `verification.md` were documentation/tracking only; no production, test, fixture, snapshot, or
  capture artifact drifted after the freeze.
- Focused licensed gate: **244 passed**, 0 other outcomes.
- Default licensed lane: **2066 passed / 34 skipped / 79 deselected**, 0 failed/errors.
- All-marker licensed lane: **2144 passed / 34 skipped / 1 failed**, with the failure set exactly
  `tests/execution/test_fusion_tea_real_teax.py::test_the_lane_runs_the_real_simkit`.
- Known node isolated with all markers: **1 passed**.
- Complete inventory: **23 tracked / 23 assessed / 0 stale / 0 missing / 0 extra / 0 duplicate / 0
  added / 0 removed**. The fresh and committed final canonical records have the same digest after
  excluding only run-specific baseline/status fields:
  `f82fc863908d369a60257832b451c30e6288c51fe3cde9336f8faf381f3e6222`.
- Static comparison: touched Python ruff **0**; full ruff **12 before / 12 after**; mypy **55 before
  / 52 after**, same 11 files; `git diff --check` **0**.
- Licensed execution was real: no `no live syside license` line appeared. The 34 maintained skips
  are not license skips.
- Historical red diagnostic: parent production plus the final kept tests yields **2 failed / 0
  passed** for the two customer nodes, both `SI_RENDERING_COLLISION`; the freeze yields both green.

The spec and plan success checkboxes were already complete and were independently verified, so no
box was reopened. This audit marks the parent epic's Item 8 heading certified and updates
`CURRENT_WORK.md` to “certified, awaiting close.”

**Not checked:** The exact command-execution provenance of the pre-production phase log cannot be
recreated from the squashed freeze alone. The parent implementation independently proves both final
kept customer nodes are red, but the final A9 fixture's later slot-alignment ordering reaches
`pumping_speed_total` before `n_pumps`; the contemporaneous `n_pumps`-first observation remains a
recorded phase artifact. A non-empty recapture branch was not executed because the authoritative
stale set is empty. This audit does not repair the inherited all-marker collection-order failure,
certify Item 6 implementation, certify the whole epic, inspect external TEAx repository state, or
run close/pre-PR/push/main operations.
