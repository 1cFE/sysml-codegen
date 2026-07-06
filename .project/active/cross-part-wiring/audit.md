# Audit: Item 10 — Cross-Part Channel Wiring (SC-5 stage 2)

**Verdict:** CONDITIONAL (certify the substance; two test/fixture fixes required before close)
**Audited:** 2026-07-06
**Branch:** upstream-findings-epic
**Commit:** 0c4b921 (range 5ea0a6a^..0c4b921 — four commits)
**Auditor note:** Suite not re-run this session (`uv run` / project-venv commands are approval-gated in
this non-interactive environment, the same limit prior Item-3/5/9 audits recorded). Green rests on the
recorded gate (**1962 passed / 4 skipped / 5 xfailed; ruff src/ 21; mypy src/ 109**) plus direct code,
snapshot, and baseline inspection.

---

## Summary

The production code is sound and complete. All six new resolution mechanisms are real, well-documented
logic — not stubs — and the three required invariants (INV-F no-tentative-escapes, INV-G phase order,
D-C offline reconstruction) are present in code exactly as designed. Five of the six mechanisms are
pinned by a **channel-identity** test (the exact producer channel string), which is the audit's central
guard against silent mis-wiring.

Two gaps, both on the flagship multi-hop-EXPOSE mechanism and both fixable in tests/fixtures only:

1. **ife_plant's direct-calc-output-terminal path has no channel-identity assertion.** Its only
   committed check is `EXPECTED_UNCOVERED == set()` — the exact "it left the uncovered list" signal the
   D-C find (plan Phase 5) proved is *insufficient* to catch a mis-wire. catf's alias-terminal path is
   pinned by a baseline; ife's direct path is not.
2. **The committed ife_plant graph baseline is stale.** It still shows `magnet_volume` as an unwired
   `entry_point`/`producer_channel: null`, inconsistent with the recaptured snapshot (which is
   `expose_pure` and wires to the `tf_coil` channel). No test compares against it, so the staleness is
   invisible to the suite — but the plan's claim "ife baseline needed no regen — its graph structure
   held" is false; the structure did change.

SC-2's honest-caveat framing is truthful and consistent everywhere. No document claims the IFE anchors
reproduce end-to-end. The REQ census, docs, verification matrix, deviation record, and agentic-mbse
impact list are complete.

---

## Findings

### Central Q1 — Silent mis-wiring sweep (channel-identity per mechanism)

For each new mechanism, does a committed test assert the WIRED CHANNEL IDENTITY (not just "resolved")?

| # | Mechanism | Channel-identity test | Verdict |
|---|---|---|---|
| 1 | Transitive confirm walk — catf alias-terminal | `baseline_outputs/catf_mfe/computation_graph.json:2922` (`magnet_volume` → `CATFMFERadialBuild__catf_radial_build__tf_coil__volume_calc__volume`), pinned by `test_pipeline_e2e.py:381 test_baseline_comparison_catf_mfe` (full-JSON equality, offline path) | **STRONG** |
| 1 | Transitive confirm walk — ife direct-calc-output terminal | only `test_ife_plant.py:227 assert actual == EXPECTED_UNCOVERED` (empty set). No producer-channel assertion; committed ife baseline is stale + uncompared | **WEAK — Finding 1** |
| 2 | ScopedAliasKey lookup (part-def EXPOSE, wi014) | `test_wi014_toy.py:127` exact tuple key `("demo_plant","total_cost")` + `:130/:175 channel.endswith("cost_calc__cost")` | STRONG (suffix, minor) |
| 3 | Consumer-scoped CHAIN / sibling disambiguation (D-D) | `test_sibling_channel_ambiguity.py:63` `== chamber_b...power_calc__power`, `:64 != chamber_a` | STRONG |
| 4 | Precedence resolver / specialized `:>>` (gamma→lcoe) | `test_spec_chain_channel.py:65` `== SpecChainDesign__spec_chain_plant__driver__meier_cost__gamma` | STRONG |
| 5 | Instance-aware type-select (two-level, REQ-VBR-11) | `test_spec_chain_twolevel.py:86` `== TwoLevelDesign__hif_plant__driver__meier_cost__gamma`; `:101-104` pins the single new `usage_type_map` entry | STRONG |
| 6 | Self-ref rescue (mechanism D, D-E) | `test_self_named_rescue.py:66` `== RescueDesign__rescue_plant__source_calc__throughput`; negative trap stays self-referential in `test_self_named_binding_trap.py:68` | STRONG |

**Finding 1 (test coverage — the flagship mechanism's direct-terminal shape).** The design (C1/B6)
establishes the two V11 pins are *different* chain shapes exercising *different* code in
`_resolve_reference_chain`: catf is an alias-terminal hop, ife is a direct calc-output terminal. catf's
channel identity is locked by its regenerated baseline + comparison test. ife's is not — only its
uncovered-set membership. The mechanism demonstrably works (the ife snapshot carries
`magnet_volume_total = expose_pure` with `reference_chain [tf_coil, volume_calc, volume]`,
`extraction_snapshot.json:1569,1575`; the identical-code catf path is pinned to `tf_coil`), so this is a
coverage gap, not a demonstrated bug. But it is the exact insufficient-assertion pattern D-C was created
to fix, on the one mechanism most exposed to the documented first-wins collision (`test_backtracker.py`
shows a sibling alias first-winning to a `plasma_region` channel). **Fix (no production change):** add one
license-free assertion via `offline_input_sources("ife_plant")` — the consumer `magnet_volume` input's
`producer_channel == "...radial_build__tf_coil__volume_calc__volume"`. `conftest.py:31 offline_input_sources`
already exists and is the seam the stage-(b) tests use.

### Central Q2 — Honest-caveat framing (SC-2)

Verified truthful and consistent. SC-2 is met at the **graph level only** (the gamma → lcoe edge is present
in the fusion-tea ComputationGraph from generated wiring alone; `driver_cost_constant` left the V11
offender list, 11 → 10). The full fusion-tea YAML does **not** emit — it aborts at V11 on 10 other
cross-part bindings (`driver.efficiency`, `chamber.*`, `target_factory.*`, `hif_driver_instance`),
pre-existing and out of Item 10's scope. The run-C $270.12/MWh anchor stays recorded-not-reproduced
(fusion-tea harness only). Workarounds stay upstream until the other 10 resolve.

This is stated the same way in `release-notes.md:87-106`, `CURRENT_WORK.md:27-36`,
`modeling-assumptions.md:393-400` (V12/V13 deliberately not minted — positive resolution, not new abort
diagnostics), and the `BACKLOG.md:104-128` P1 follow-up. A grep for unqualified "reproduce end-to-end"
claims found hits only in the spec/design procedure text (framing, not a completion claim) — **no
deliverable doc asserts "IFE anchors reproduce end-to-end."** Passes.

### Central Q3 — INV-F, INV-G, D-C

- **INV-F (no tentative escapes — raises are real): VERIFIED.** Three `else/elif ... raise` on a surviving
  `EXPOSE_CHAIN_TENTATIVE` at `graph_builder.py:263` (module build), `:285` (aggregation alias map),
  `:878` (attribute resolution map), plus the confirm-loop terminal raise at
  `output_registry_builder.py:333`. The Phase-1c non-raise is correct (it runs at
  `output_registry_builder.py:203`, before the Phase-3b confirm at `:296`; a pre-confirm tentative is
  legitimate). Note: the design/plan pointer "~:120" for Phase 1c is mislabeled (line 120 is the
  offline-parity comment block) — substance correct, pointer off. Non-blocking.
- **INV-G (finalize before consumers): VERIFIED.** In `pipeline_builder.py`: first
  `_remove_formula_from_design_attrs` at :135 (pre-confirm), `build_output_registry` (Phase 3b confirm)
  at :713, second removal at :739, `ParameterGroupDeriver` at :743 — group_deriver after the second
  removal, as required. Registry-internal: Phase 3b (:296) after Phase 3 (:254), before Phase 4 (:346).
- **D-C (offline == live reconstruction): VERIFIED.** `output_registry_builder.py:139-147` re-tags an
  already-`EXPOSE_PURE` CA back to tentative when `reference_chain` is present, `>= 2` segments, and
  `reference_chain[0]` is not a calc-usage short name — before Phase 1, so the confirm walk runs
  identically offline. The "short name vs full QN" gotcha is handled (`calc_usage_names` derived from
  `qualified_name.rsplit("__",1)[-1]`, not `instance_name`). The offline channel identity — the path that
  carried the mis-wire — is pinned exactly by `test_baseline_comparison_catf_mfe` + baseline line 2922.
  Minor: there is no single test asserting live == offline *channel string* for the catf pin (live is
  covered by success + no-V11; the byte-identity test is solar_battery-only). Since the offline path is
  the risk path and it is pinned, this is low-severity — noted, not required.

### Central Q4 — Fixture pins + blast radius

- **Five stage-(b)/fixture pins:** all STRONG channel-identity (see Q1 table rows 2–6). The two flipped
  V11 pins: catf STRONG (baseline), ife WEAK (Finding 1).
- **Blast radius — usage-level retype indexing changes exactly one fixture: VERIFIED.**
  `_index_usage_level_retypes` (`hierarchy_resolver.py:516-571`) gates on
  `:566 winner != base_type_map.get((container_def, name))` — only a genuine retype (target type differs
  from base-declared) is indexed. Value-only `:>>` overrides are filtered four ways (PartUsage gate :551,
  `owned_redefinitions` :553, `winner` non-empty :564, type-difference :566), so solar_battery's
  `:>> solar_array {...}` and chain_override's sensor are excluded. `test_spec_chain_twolevel.py:101-104`
  pins the single new entry. Claim credible. *Theoretical edge (not a corpus gap):* a missing
  `base_type_map` entry reads as "different" (`None != winner`); an inherited member owned by a supertype
  and retyped to the same type could be spuriously indexed — exotic, absent from the corpus. Note only.
- **No mocks: VERIFIED.** Clean grep for `Mock`/`MagicMock` across the five new conformance files; they
  load real committed snapshots and build real registries/graphs.

### Central Q5 — Deviations, REQ census, docs

- **Deviations D-A…D-F + C-then-B all recorded with evidence.** D-A/D-B/D-C in `plan.md` "Deviations
  absorbed" + design Round-3; D-D/D-E/D-F in design Round-4 amendments + Phase-7 notes; the C-then-B
  ruling and its STEP 1/2 in the Phase-8 notes. Each carries a code pointer and a reason.
- **REQ census complete.** REQ-BT-11, REQ-CA-10, REQ-VBR-10, REQ-VBR-11, REQ-LVP-09 present in the
  verification matrix with test pointers; REQ-CA-03 revised in place; REQ-CA-09 discharged
  (`verification-matrix.md:19,138`); REQ-HR-09 formally released (`25-hierarchy-resolver.md:30`).
  Reference docs 11/12/16/24/25 + modeling-assumptions updated and consistent with the REQ text.
- **agentic-mbse impact carries D-F.** `release-notes.md:119-126` records the bare `:>> attr = value`
  idiom as supported and `attribute :>> attr = <expr>` as known-unsupported (dropped at
  `hierarchy_resolver._extract_single_redefinition`), flagged as Item-12 guidance/validation. Matches D-F.

### Central Q6 — Scope check

Change scope across the four commits is exactly the enumerated set: 9 src files touched additively
(extraction/expression_utils, data_models, computed_attribute_extractor, hierarchy_resolver;
orchestration/output_registry_builder, pipeline_builder; analysis/dependency_backtracker;
resolution/graph_builder; core/output_registry, identifier_types; snapshot/loader, graph_rebuild), the
five fixtures + snapshots, the catf snapshot+baseline regen, the ife snapshot regen, and the matching
test flips. No ComputationGraph schema field added (Item 11's rev preserved — spec HARD constraint held).
Working tree clean but for `uv.lock`.

### Code integrity

No slop or failure-honesty problems. The three novel functions read cleanly, one job each:
`_rewrite_specialized_chain` (`pipeline_builder.py:192`) does instance-first then declaring-def
type-select with early returns; `_rescue_self_named_bindings` (`:516`) gates the rescue on a real
`scoped_alias_lookup` hit (the trap correctly falls through to "left as-is"); `_index_usage_level_retypes`
(`hierarchy_resolver.py:516`) is guarded, not a catch-all. `register_scoped_alias` raises on collision
(unique by construction — no first-wins fallback), satisfying the spec's "unique by construction" HARD
requirement. The `else/elif: raise` INV-F guards are genuine fail-loud, not silent defaults.

---

## Certification

**Marked as verified:**

- **Spec SC-1** — both V11 pins flip; catf channel identity pinned to `tf_coil` (baseline + comparison
  test), ife wiring confirmed via `expose_pure` snapshot + identical mechanism. Marked, with Finding 1
  (ife channel-identity test) recorded as the residual.
- **Spec SC-3, SC-4, SC-5** — STRONG channel-identity pins verified.
- **Spec "every new registry key unique by construction"** — `register_scoped_alias` raise-on-collision.
- **Spec "docs and matrix move with the code"** — verified across docs 11/12/16/24/25 + matrix.

**Left unchecked (with reason):**

- **Spec SC-2** — met at the graph level only; the full YAML does not emit and the end-to-end anchor is
  recorded-not-reproduced. The honest caveat is correctly documented everywhere; the criterion as
  *written* ("present in generated YAML" + "reproduce end-to-end") is not fully met, so it stays `[ ]`
  with the caveat, not checked.
- **Spec "existing 4 baselines unchanged / diffs reviewed"** — catf regenerated and reviewed; the ife
  baseline is stale and unreviewed (Finding 2). Left unchecked pending the regen/removal.

**Required before `/_my_close` (test/fixture only, no production change):**

1. **Finding 1** — add a channel-identity assertion for ife_plant shape-4 via
   `offline_input_sources("ife_plant")`, pinning `magnet_volume` → the `tf_coil__volume_calc__volume`
   producer channel (license-free; mirrors the catf baseline guard).
2. **Finding 2** — regenerate `baseline_outputs/ife_plant/computation_graph.json` (it now wires
   `magnet_volume` to `tf_coil`, no longer an `entry_point`/null) and add a `test_baseline_comparison_ife_plant`
   so the wiring is pinned and the artifact cannot drift; OR remove the stale unreferenced baseline.
   Correct the plan's "ife baseline needed no regen" note.

**Minor / non-blocking (record, optional):** wi014 uses `.endswith(...)` not full-string `==` (unambiguous
in that fixture); no catf live==offline channel-string test (offline is pinned, live is success+no-V11);
`_index_usage_level_retypes` missing-key-reads-as-different theoretical edge; `CURRENT_WORK.md:12` says
"Not committed / no commits" but the work is committed across four commits (stale note).

The substance ships correctly. The verdict is CONDITIONAL only on the two test/fixture fixes above —
both close the flagship mechanism's channel-identity gap the audit was chartered to catch.


---

## Orchestrator close-out (2026-07-06)

Both conditions cleared by the orchestrator:
1. **Channel-identity pin added** for ife_plant's direct-calc-output-terminal path:
   `test_shape4_wires_to_exact_channel` asserts `cryo_load.magnet_volume` wires to
   `IfePlantSubsystems__radial_build__tf_coil__volume_calc__volume` exactly (not a
   first-wins sibling) — the same assertion class that caught D-C.
2. **Stale ife_plant baseline regenerated** via the capture script; reviewed diff shows
   magnet_volume moving entry_point/null → wired module_output with the correct channel.
   wi014_toy's baseline picked up a 2-line source_file canonicalization riding its Item-10
   snapshot recapture (accepted per the standing canonical-form ruling).
3. Gate re-run: **1963 passed / 4 skipped / 5 xfailed; ruff 21; mypy 109** (== baseline).

Verdict upgraded: **PASS** (with the recorded SC-2 graph-level caveat and the BACKLOG P1
follow-up for the remaining 10 fusion-tea cross-part bindings). Item 10 complete.
