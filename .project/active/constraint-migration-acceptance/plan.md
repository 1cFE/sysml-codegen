# Implementation Plan: Migration, Docs, and IFE Acceptance (CONSTRAINT-EXEC Item 14)

**Status:** Draft
**Created:** 2026-07-13
**Last Updated:** 2026-07-13
**Branch:** constraint-exec-epic
**Epic:** CONSTRAINT-EXEC — Item 14 (closing item)

## Source Documents
- **Spec:** `.project/active/constraint-migration-acceptance/spec.md` — success criteria (four workstreams + seams + epic close), Known Requirements, Non-Goals, Open Questions.
- **Design (rev 2, committed):** `.project/active/constraint-migration-acceptance/design.md` ← **all component details, file:line targets, bets, decisions, invariants live here. Do not restate; link.** Key anchors: five-workstream architecture (`design.md#architecture`), the dual carrier surfaces (`design.md#key-decisions` D1), the gain-fix tier (D2), within-v3 removal (D3), the epsilon boundary rule (`design.md#implementation-notes`), retirement grep targets (Appendix B), per-repo doc set (Appendix A).
- **Design review:** `design-review.md` — Approved-with-must-fixes; all three MF and five NTH incorporated into design rev 2 (verified this session).
- **Reference (fusion-tea harness):** `.project/reference/fusion-tea-ife-sweep/FACTS.md` — deletion target `sweep_ife.py:82`, outputs dir, `>`-vs-`>=` boundary hazard. Carries the paths for Appendix C.
- **Memory:** `item3-fusiontea-acceptance-facts` (per-consumer gain key, abs-path parity), `byte-identity-captured-at-churn` (timestamp-only diff gate), `plant-idiom-fixtures`, `verification-matrix-drift-modes`, `syside-license-key-explicit-env-needed`.

---

## Implementation Strategy

### The shape: four repos, one closing item

The design splits into five workstreams across four repos (`design.md#architecture`). This plan groups them into **one in-repo implement session** (sysml-codegen) plus **three cross-repo sessions** the orchestrator sequences. The cross-repo sessions are written as ready-to-apply briefs in Appendices A–C (the Item 3 pattern — those repos are outside this session's sandbox).

**Cross-repo sequencing (the orchestrator's map):**

| Session | Repo | Workstreams | Runs | Depends on |
|---|---|---|---|---|
| **S-CODEGEN** (this plan, Phases 1–5) | sysml-codegen | W1 gain fix, W2 retirement + mapping test, W3a docs, W5a seam | first | Item 13 not mid-commit (write-order only) |
| **S-MBSE** (Appendix A) | agentic-mbse | W3b facts/profile docs | parallel to S-CODEGEN | none |
| **S-TEAX** (Appendix B) | teax | W3c docs, W5b loader seal wiring, W5c tracking-key note | parallel to S-CODEGEN | Items 10–12 landed |
| **S-FUSION** (Appendix C) | fusion-tea | W4 IFE acceptance + prepare-once benchmark | **last** | W1 landed **and** W5b landed **and** Item 13 certified **and** Items 10–12 green |

**Why W1 is first and W4 is last.** The gain fix (W1) is the single precondition for everything downstream: without it `'Viability Threshold'` cannot lower, so the fusion fixtures have no populated catalog for W2's mapping test to read and no executing assertion for W4's acceptance (`design.md` Core Concept; spec Prerequisite). W4 is last because acceptance loads a *sealed* IFE package through teax (W5b must land first, NTH2), reads verdicts through the study layer (Items 10–12 must be green, R3), and the acceptance numbers must sit on a coherent baseline (Item 13's calc cutover certified). Everything between is parallelizable.

### Critical path
`W1 gain fix + re-capture` → `W2 mapping test green` → `W2 retirement + grep-clean` → (cross-repo: `W5b teax seal`) → `W4 acceptance 100% grid match` → `epic reconcile`.
W3 (docs, all repos) and W5a (GENERATOR_MISMATCH) hang off the side — they gate nothing but the epic-close checklist.

### First proof point
**Phase 1's `test_gain_self_redef_materializes`** — a license-free unit test that `materialize_supplied_values` synthesizes a design attribute keyed `hif_plant_pkg__hif_plant__gain = 80.0` from the instance self-redefinition, so the bare `in gain = gain` actual resolves. If that tier match doesn't fire, W1 is wrong and the whole item is blocked at its root (B2). This is the earliest, cheapest test that de-risks the epic's closing dependency.

### Overall validation approach
- Each phase starts test-first. The two migration-critical phases (mapping test, retirement) are ordered so the **kept** mapping test is green *before* any deletion — the proof precedes the retirement it authorizes.
- License-gated legs (`@requires_license`) skip cleanly without the syside license; the live legs run under `env $(grep -v '^#' ~/1cfe/agentic-mbse/.env | xargs) uv run …` with `SYSIDE_LICENSE_KEY` exported (memory `syside-license-key-explicit-env-needed` — an unexported key reads as a fake skip baseline).
- Byte-identity is the backstop for the one production change (W1): exactly `plant_values` and `fusion_tea` change; any third is a regression (R2).

---

## Phase 1: W1 — the `gain` fix + grandfather re-land (de-risk first)

### Goal
Add the instance-self-redefinition precedence tier to the materializer (`design.md#key-decisions` D2) so `fusion_tea` and `plant_values` lower `'Viability Threshold'` instead of halting; re-capture the two snapshots lowered; empty Item 8's grandfather list. This is the precondition for W2 (populated fusion catalog) and W4 (executing assertion).

### Assumption Under Test
A `design_overrides` entry whose `owning_part_qn == instance_scope` with empty `target_path` and `attribute_name == target.attr` exists for `hif_plant.sysml:87`'s `:>> gain = 80.0` (design D2 verified this in the snapshot), and matching it in `_match_override` synthesizes the right `{instance_scope}__{attr}` key **without** shadowing an existing tier-1 match (R2 blast radius).

### Test Stencil (Write This First)
```python
# tests/conformance/test_supplied_values_self_redef.py  (NEW — license-free, snapshot-driven)
def test_gain_self_redef_materializes(fusion_tea_snapshot):
    # design_overrides carries owning_part_qn == instance QN, attr "gain", literal 80.0, target_path []
    supplied = materialize_supplied_values(
        entry_point_qns=[...],            # includes the bare-name gain target's instance scope
        redefinitions=..., design_overrides=...,
        usage_type_map=...,
    )
    assert supplied["hif_plant_pkg__hif_plant__gain"] == 80.0   # instance-self-redef tier fires

# tests/conformance/test_grandfather_carveout.py  (INVERT the existing carve-out)
@requires_license
@pytest.mark.parametrize("fixture", ["plant_values", "fusion_tea"])
def test_grandfathered_fixture_now_lowers(fixture, tmp_path):
    # was: captures grandfathered_off + halts on gain. Now: lowers, catalog assembled.
    graph, _ = build_full_graph_from_snapshot(_recapture(fixture, tmp_path))
    assert graph.constraint_catalog is not None
    assert any(e.constraint_id for e in graph.constraint_catalog.concrete_entries)
```

### Changes Required
**See `design.md#component-overview` (materializer tier) and D2 for the exact match condition and the `design_overrides` bucket (NTH5).**

- [ ] **Add the instance-self-redef tier** in `_match_override` (`resolution/supplied_values.py:102`), scanning `design_overrides` for `owning_part_qn == instance_scope`, empty `target_path`, `attribute_name == target.attr`, bare-name binding only. Insert at the correct precedence — **below** a genuine usage-level override (`:129`), so it never shadows tier 1 (`design.md#implementation-notes`, "Gain fix precedence"). Demand-scoped + literal-only like the existing tiers.
- [ ] **Re-capture** `plant_values` and `fusion_tea` snapshots **lowered** (license; capture-script path per memory `syside-license-via-scripts-not-dashc`). D3 lands here too: the re-captured snapshots omit `dropped_constraints` (Phase 3 removes the emitter; if Phase 3 runs after, re-capture again — or sequence Phase 3 deletion before the final re-capture so the two files are captured once, clean).
- [ ] **Retire the grandfather carve-out** (INV-D): invert `test_grandfather_carveout.py` (both parametrized fixtures now lower, not halt); the named exclusion list `["plant_values", "fusion_tea"]` (`test_grandfather_carveout.py:29`) shrinks to **empty**; remove the loud flag-off carve-out. Confirm `test_snapshot_generation.py:224` (`test_fusion_tea_snapshot_generates_grandfathered_and_live_halts_on_gain`) is retired/inverted with it.

### Validation
**Automated:**
- [ ] `uv run pytest tests/conformance/test_supplied_values_self_redef.py` → passes (license-free first proof point).
- [ ] With license: the inverted grandfather tests → both fixtures lower, catalog non-None.
- [ ] **Byte-identity gate (INV-C, R2):** re-generate all 29 snapshots; the timestamp-only diff gate (memory `byte-identity-captured-at-churn`) shows **exactly** `plant_values` and `fusion_tea` changed. Any third change → stop and investigate (regression).
- [ ] **Confirm the other 5 `grandfathered_off` fixtures are unaffected** — `agg_literal_probe`, `unresolvable_attr_probe`, `chain_override_probe`, `self_named_binding_trap`, `invocation_binding_probe` are grandfathered for non-gain reasons (profile/resolution blocks). They must **not** newly lower and must **not** newly halt differently. If any changes disposition, that is a finding to surface (their blocks are unrelated to the gain tier; a change means the tier over-matched — R2).
- [ ] `uv run pytest tests/` → no regressions; `uv run ruff check src/`, `uv run mypy src/` clean.

**What We Know Works After This Phase:**
The gain gap is closed, the two grandfathered fixtures lower under their own byte-identity gates, and the blast radius is exactly two snapshots. W2's fusion catalog and W4's assertion are unblocked.

---

## Phase 2: W2 — the manifest→catalog 1:1 mapping test (test-first, kept)

### Goal
Author the kept test that proves the migration invariant: every constraint usage the manifest reports is carried by a per-usage catalog carrier, with nothing silently absent (`design.md#core-concept`, D1, INV-A). This is the epic's most load-bearing migration outcome and it lands **before** any deletion — the proof precedes the retirement it authorizes.

### Assumption Under Test
The manifest sweep and the lowering sweep cover the identical population (B1: both call `elements_of_type("ConstraintUsage", include_subtypes=True)`), so a total per-usage function exists from each manifest droppable entry to either (a) ≥1 eligible concrete entry grouped by `usage_qualified_name`, or (b) one `eligible=False` unassessed record — with the residual carrier-free set being a **named, justified** category, not a catch-all (design-review hidden bet; `design.md#key-bets` B1).

### Test Stencil (Write This First)
```python
# tests/conformance/test_constraint_migration_mapping.py  (NEW — re-anchors REQ-EXT-09 family)
@pytest.mark.req("REQ-EXT-09")   # re-anchored: manifest→catalog, not drop-diagnostic
def test_every_manifest_usage_has_a_catalog_carrier(constraint_bearing_ctx):
    ctx = constraint_bearing_ctx
    manifest = ctx.extractor.collect_constraint_manifest()          # the retiring surface
    eligible_by_usage = group_by(                                    # surface (a): catalog
        ctx.graph.constraint_catalog.concrete_entries, key="usage_qualified_name")
    unassessed = {c.usage_qualified_name for c in ctx.concrete_constraints
                  if not c.eligible}                                 # surface (b): NOT the catalog (MF2)
    for entry in manifest:
        usage_qn = _usage_identity(entry)          # QN + source-location tiebreak (Impl Notes)
        carried = usage_qn in eligible_by_usage or usage_qn in unassessed
        assert carried or _is_justified_carrier_free(entry), (      # named category, no catch-all
            f"silent drop: {usage_qn} has no catalog carrier and is not justified inventory")
    # D1b (inverted, safe direction): every concrete entry's definition appears in source_records;
    # unused inventory definitions are allowed (concept line 102 — never counted unassessed).
    src_defs = {r.definition_qualified_name for r in ctx.graph.constraint_catalog.source_records}
    for e in ctx.graph.constraint_catalog.concrete_entries:
        assert e.definition_qualified_name in src_defs   # no dangling reference; inventory OK
```

### Changes Required
**See `design.md#key-decisions` D1 (the two carrier surfaces), D1b (inverted inventory arm), and `design.md#implementation-notes` ("Mapping-test join key").**

- [ ] **Pin the three data surfaces** (MF2): manifest from `extractor.collect_constraint_manifest()` (`extraction/extractor.py:112`); eligible carriers from `graph.constraint_catalog.concrete_entries` grouped by `usage_qualified_name`; unassessed carriers from `ctx.concrete_constraints` where `eligible=False` (`pipeline_context.py:119`) — **not** the catalog (`assemble_constraint_catalog` filters eligible-only, `constraint_catalog.py:76`). *Equivalent cleaner home:* join against the full `lower_constraints` output (`constraint_lowering.py:436`), which carries both dispositions in one list.
- [ ] **Join key:** usage qualified name, with source location as the anonymous-assertion tiebreak — the same identity `_source_local_identity` uses (`constraint_lowering.py:379`). **Confirm the two identity renderings agree on the anonymous case before locking** (`design.md#implementation-notes`).
- [ ] **Name the justified carrier-free category** (design-review B1 hidden bet): requirement-side excluded usages that map to unassessed, plus the tightly-justified set the lowering explicitly skips (e.g. `requirement_def` owners). Do **not** let it absorb surprises — an unrecognized carrier-free usage fails loudly.
- [ ] **catf_mfe counts (R1):** the 65 plain `constraint {}` usages land eligible or unassessed depending on how `evaluate_profile` treats a non-asserted inline constraint. Run extraction (license) to fix the expected split; this sets the test's *counts*, not its *structure*. If any of the 65 come back BLOCK, that is a real finding (catf_mfe would be halting today) — surface it (R1).
- [ ] **Optionally** the D1b inventory-visibility assertion (inverted, safe direction only — unused defs stay legitimate).

### Validation
**Automated:**
- [ ] `uv run pytest tests/conformance/test_constraint_migration_mapping.py` → passes as a **kept** test (not a one-time check).
- [ ] Runs over the constraint-bearing fixture set (derive at implement; includes `catf_mfe`, `fusion_tea`, `plant_values`).
- [ ] License leg (if the mapping test needs live extraction for any fixture) skips cleanly without a license.

**What We Know Works After This Phase:**
The migration invariant is proven as a kept guard. Every manifest usage is demonstrably carried, INV-A holds, and the retirement in Phase 3 is now authorized by a green proof.

---

## Phase 3: W2 — retirement + REQ-EXT-09 re-anchor + grep-clean

### Goal
Delete the drop-manifest era against the Phase-2 proof: the report, both blanket warnings, the snapshot section, the replay, the ctx field and its pass-through. Re-anchor the surviving REQ-EXT-09 assertions onto the catalog. Prove grep-clean (INV-B).

### Assumption Under Test
Every retirement target in Appendix B deletes cleanly with the mapping test (Phase 2) and the catalog (Items 5–9) covering what the manifest reported; the loader's `.get("dropped_constraints", [])` tolerance (`loader.py:239`) and the three-key gate (which excludes `dropped_constraints`, verified in design review) make D3's within-v3 removal safe.

### Test Stencil (Write This First)
```bash
# The grep-clean gate is the test (INV-B). Run after deletion; must return zero.
grep -rn "collect_constraint_manifest\|render_constraint_report\|report_dropped_constraints" src/
grep -rn "not executable" src/         # no blanket warning (the kept halt at constraint_lowering.py:481 is distinct)
grep -rn "dropped_constraints" src/    # snapshot section gone from serializer/loader/capture
```

### Changes Required
**See `design.md` Appendix B (retirement grep targets) and D3 (within-v3 removal). Do NOT touch the kept generation-halt at `constraint_lowering.py:481` (explicit non-goal).**

- [ ] **Delete** (Appendix B, grep-verifiable): `constraint_report.py` (render + `manifest_to_records`/`manifest_from_records`), `extractor.py:98,112`, `pipeline_builder.py:760`, `snapshot_context.py:45` (replay), `serializer.py:133`, `loader.py:238-239`, `capture.py:67`, the two blanket warnings (`constraint_report.py:125-141`), **plus NTH1:** the `constraint_manifest` ctx field (`pipeline_context.py:110`) and its snapshot-context pass-through (`snapshot_context.py:86`).
- [ ] **Re-anchor REQ-EXT-09 tests** (not merely delete): `TestReqExt09ConstraintDropDiagnostic`, `TestConstraintRequireAndExclusion`, `TestConstraintDroppablePolicyParity` (`test_extractor.py:893-1044`) and the wi014 manifest round-trip (`test_snapshot_contract.py:91`) re-anchor onto the mapping test + catalog contents. Map each retained assertion from "manifest reported it dropped" → "catalog carries it as concrete entry / unassessed / inventory."
- [ ] **D3 heterogeneous corpus (NTH3):** the serializer stops emitting `dropped_constraints`; the two re-captured fixtures (Phase 1) omit the key, the other 27 retain it as an ignored vestige. **Sequence the final `plant_values`/`fusion_tea` re-capture after this deletion** so those two files are captured once, clean (avoids a double re-capture). The INV-C timestamp reviewer expects those two to change for **two** reasons (gain fix + key removal).

### Validation
**Automated:**
- [ ] The three grep-clean commands return **zero** (INV-B).
- [ ] `uv run pytest tests/conformance/test_extractor.py tests/conformance/test_snapshot_contract.py` → re-anchored family green.
- [ ] `uv run pytest tests/` → no regressions; old snapshots still load (loader `.get()` tolerance).
- [ ] Byte-identity gate re-run: still exactly `plant_values` + `fusion_tea` changed (now for gain + key-removal reasons).

**What We Know Works After This Phase:**
The rival surface is gone, grep-clean holds, and the REQ-EXT-09 family reads the catalog. The migration (spec workstream 2) is complete in-repo.

---

## Phase 4: W3a — sysml-codegen docs flip + verification matrix

### Goal
Flip this repo's authoring guidance from "constraints are not executable" to teaching the executable profile + block list; add architecture coverage for the new phases; add verification-matrix rows under the register discipline (`design.md` Appendix A).

### Assumption Under Test
The doc surfaces in Appendix A are the complete in-repo set (verified surfaces), and the register-discipline recount (anchor the STATUS column, don't substring-match) reconciles the matrix against `grep -o 'REQ-[A-Z]*-[0-9]*'` over the reference docs.

### Changes Required
**See `design.md` Appendix A (sysml-codegen verified surfaces) and spec Docs requirements.**
- [ ] Flip `docs/architecture/modeling-assumptions.md:400` §8 → teach the executable profile + block list (invocation, conditional, temporal, unit conversion, real-valued equality) and the real-equality → **explicit two-inequality-band** idiom.
- [ ] Update cross-refs: `reference/01-extraction.md:20`, `reference/02-orchestration.md:40`, `verification-matrix.md:228`.
- [ ] Add/extend architecture reference docs: lowering phase, catalog, contracts, evaluator, study layer.
- [ ] `verification-matrix.md`: add rows for the new REQ families (constraint lowering, generation, catalog, contracts, study); **recount index family counts + STATUS from actual table rows** (memory `verification-matrix-drift-modes` — the index counts and missing REQ families are the real drift, not the summary block).

### Validation
- [ ] `grep -rn "not executable" docs/` → only historical/decision-record mentions remain; no authoring guidance still teaches the retired behavior.
- [ ] `grep -o 'REQ-[A-Z]*-[0-9]*' docs/architecture/reference/*.md | sort -u` cross-checks the matrix; every new REQ family has a row.
- [ ] Index family counts + STATUS recounted and consistent (not just the summary block).

**What We Know Works After This Phase:**
This repo's docs teach the built system. (agentic-mbse and teax docs land in S-MBSE / S-TEAX — Appendices A/B.)

---

## Phase 5: W5a — GENERATOR_MISMATCH seam disposition

### Goal
Dispose of the reserved-but-unreachable `GENERATOR_MISMATCH` diagnostic (`contracts/verify.py:24`): either wire a `generator_version` axis so a generator-version mismatch is detectable, or document it as an intentional reserved seam and remove the dead reachability expectation. Record the disposition either way (spec Small Seams).

### Changes Required
**See spec Known Requirements → Small recorded seams (GENERATOR_MISMATCH).**
- [ ] Inspect `contracts/verify.py:24` and its reachability expectation. Decide wire-vs-document.
- [ ] If document-and-remove: remove the dead expectation, add a one-line reserved-seam note (decision-record phrasing, not an instruction to future agents — capture-fidelity Law 3).
- [ ] Record the disposition in the run report.

### Validation
- [ ] The chosen disposition is recorded; if wired, a test exercises the new axis; if documented, the dead expectation is gone and no test asserts unreachable reachability.

**What We Know Works After This Phase:**
The in-repo seam (W5a) is swept. The teax seams (W5b loader seal, W5c tracking-key note) land in S-TEAX (Appendix B).

---

## Phase 6: Epic Success Criteria reconcile (final, after cross-repo sessions)

### Goal
Once S-CODEGEN, S-MBSE, S-TEAX, and S-FUSION have all landed, check the epic's top-level Success Criteria and Item 14's boxes with evidence links, and write the Item 14 close-out report. This phase is resumable — it collects evidence from the four sessions' reports.

### Changes Required
- [ ] Reconcile the **epic** Success Criteria (`epic_constraint_execution.md:39-47`) — Acceptance, migration mapping, byte-identity, docs — each box traceable to a landed item or this item's evidence.
- [ ] Reconcile **Item 14's** boxes (`epic_constraint_execution.md`, Item 14 entry): migration mapping green + grep-clean; IFE grid 100% match + hand rule deleted; docs in all three repos.
- [ ] Write the close-out report `.project/active/constraint-migration-acceptance/run-report.md`: W1 byte-identity result, W2 mapping-test + grep-clean, W3 per-repo doc deltas, **W4 acceptance table** (see Appendix C — committed under fusion-tea's harness dir; link it here), W5 seam dispositions, the prepare-once benchmark, and the recorded **naming-divergence note** (concept "source record" per-usage vs landed `ConstraintCatalogSourceRecord` per-definition — `design.md#core-concept`, the boxed decision: invariant **met as written**, no amendment).

### Validation
- [ ] Every epic + Item 14 box is checked with an evidence link (no self-certification — numbers pasted from real runs).
- [ ] Suggest `/_my_audit` before PR (workflow-accountability).

**What We Know Works After This Phase:**
The epic closes where it started — the IFE sweep's hand-coded rule is dead, replaced by the generated assertion, with 100% grid agreement (or a surfaced boundary row).

---

## Environment Setup
**See CLAUDE.md.** Tests: `uv run pytest tests/`. Type: `uv run mypy src/`. Lint: `uv run ruff check src/`.
- **License env (live legs):** `env $(grep -v '^#' ~/1cfe/agentic-mbse/.env | xargs) uv run …`. `SYSIDE_LICENSE_KEY` must be **exported** or `@requires_license` tests silently skip and read as a fake baseline (memory `syside-license-key-explicit-env-needed`). License loads for capture scripts / full pytest, not a bare `-c` probe (memory `syside-license-via-scripts-not-dashc`).
- **Byte-identity gate:** timestamp-only diff check + revert (memory `byte-identity-captured-at-churn`) — a full re-capture rewrites every `captured_at`; only the intended structural change should survive the gate.
- **Cross-repo:** `~/1cfe/agentic-mbse`, `~/1cfe/teax`, `~/1cfe/fusion-tea` are outside this session's sandbox (R4). Appendices A–C are the ready-to-apply briefs; the orchestrator grants those sessions their repo access.

## Risk Management
**See `design.md#potential-risks` (R1–R4).** Phase-specific:
- **Phase 1 (R2 blast radius):** the byte-identity gate across all 29 snapshots is the backstop — exactly two change; the 5 non-gain `grandfathered_off` fixtures are explicitly re-verified unaffected.
- **Phase 2 (R1 catf_mfe disposition):** the test handles both eligible/unassessed splits; the *counts* are fixed empirically at implement with license; a BLOCK among the 65 is a surfaced finding.
- **Phase 2 (B1 hidden bet):** the carrier-free category is named and justified, never a catch-all.
- **W4/S-FUSION (R3 sequencing):** acceptance depends on Items 10–12 green **and** W5b landed **and** W1 landed **and** Item 13 certified. Flagged to the orchestrator so it is not discovered late (NTH2).
- **W4 (epsilon boundary):** boundary detection uses `abs(eta*G - 10.0) <= eps`, not `== 10.0` (float grid arithmetic; NTH4). A flagged row is a real semantic difference to report, not a mismatch to reconcile away.

---

## Appendix A — S-MBSE brief: agentic-mbse docs (W3b)

**Repo:** `~/1cfe/agentic-mbse` · **Runs:** parallel to S-CODEGEN · **License:** not needed (docs only).

**Task:** Flip the facts/profile authoring-surface docs and add any L4/L6 verification-matrix rows so no agentic-mbse doc still describes the retired "constraints are not executable" behavior.

**Scope (design-best-guess — confirm the exact file set with repo access; `design.md` Appendix A marks these pending access):**
- [ ] The `constraint_extraction` / `constraint_facts` / executable-profile doc(s) — the neutral-facts + profile authoring surface (source of truth mirrored in-repo at `.project/reference/agentic-mbse-landed/`).
- [ ] Any L4/L6 verification-matrix rows for the neutral-facts and profile REQ families, under the register discipline (recount index counts + STATUS from table rows; memory `verification-matrix-drift-modes`).
- [ ] Teach the executable profile + block list (invocation, conditional, temporal, unit conversion, real equality → two-inequality band) where the authoring surface lives.

**Validation:** `grep -rn "not executable" <docs>` → only historical/decision-record mentions; new REQ families cross-check against the matrix.

**Report back:** the exact files touched + matrix deltas, for the Phase-6 reconcile.

---

## Appendix B — S-TEAX brief: teax docs + loader seal wiring + tracking-key note (W3c/W5b/W5c)

**Repo:** `~/1cfe/teax` · **Runs:** parallel to S-CODEGEN, but **W5b must land before S-FUSION (W4)** · **License:** not needed for docs; W5b wiring exercised for real in S-FUSION.

**W5b — teax loader seal-verification wiring (precondition of W4, NTH2):**
- [ ] Wire the loader to `verify_package(dir, name, runtime_version, strict)` (signature fixed by Item 9): load-by-declared-name, inject the runtime marker, choose strict. This is the mechanical Item 10/14 change Item 9 named.
- [ ] It is exercised for real when S-FUSION's acceptance loads the sealed IFE package through teax — so it **must land before W4 runs**.
- [ ] Validation: a sealed IFE package loads through teax with seal verification on; a tampered artifact / unhashed extra file fails with a named diagnostic (Item 9 behavior).

**W3c — teax evaluator + study-layer docs (design-best-guess — confirm file set with access):**
- [ ] Document the evaluator and study-layer surfaces Items 10–12 added.
- [ ] No teax doc still describes the retired behavior.

**W5c — tracking-key correlation note:**
- [ ] Document that a `tracking_key` correlates a logical constraint across model versions by **name only** — names correlate, never equate across fingerprint boundaries (concept Vocabulary, line 209).

**Report back:** files touched, W5b wiring confirmation, for the Phase-6 reconcile.

---

## Appendix C — S-FUSION brief: IFE acceptance + prepare-once benchmark (W4)

**Repo:** `~/1cfe/fusion-tea` · **Runs:** LAST — after W1 landed, W5b landed, Item 13 certified, Items 10–12 green (R3) · **License + teax venv (epic branch) for the study CLI.**

**Reference:** `.project/reference/fusion-tea-ife-sweep/FACTS.md` carries the paths — harness `exploration/ife_e2e/sweep_ife.py`, deletion target `:82` (`viable = eta_g > ETA_G_MIN`, `ETA_G_MIN = 10`), LCOE overlay `:84` (stays hand-coded — policy), outputs `exploration/ife_e2e/outputs/`.

**Task (D4/D5 one-run replay):**
- [ ] **Regenerate the fusion-tea IFE package lowered** (the viability assertion `eta * gain >= threshold` now executes, thanks to W1). Live-vs-snapshot byte-diff of `fusion_tea` needs an **absolute** `--models` path (memory `item3-fusiontea-acceptance-facts`, abs-path parity gotcha).
- [ ] **Route the sweep through the study layer** (teax study CLI/API, Items 10–12), **not** direct generated-impl calls — today `sweep_ife.py` calls impls directly (memory `item3-fusiontea-acceptance-facts`). CLI-vs-API is the implement session's choice; either satisfies the requirement (verdict from the generated assertion via the study layer). Map the sweep grid onto a `StudyDefinition` (list vs grid strategy).
- [ ] **Replay the grid once through both rules** (the about-to-be-deleted hand rule + the generated verdict) to build the comparison, **then delete the hand rule at `:82`** (D4 — the one-run replay makes it self-evidently apples-to-apples; no separate golden to keep honest).
- [ ] **Boundary detection (epsilon window, NTH4):** compute `eta*G` per point; flag any row within `abs(eta*G - 10.0) <= eps`. That window is where hand `>` and modeled `>=` diverge; a flagged row is a **real** semantic difference to report, not to reconcile away.
- [ ] **Record the prepare-once benchmark** (S5 carry-forward (2)) on the real IFE package: prepare-once vs rebuild. A recorded measurement, not a tuning target (Non-Goals).

**The committed acceptance artifact (D5):** a table `grid point (eta, G) → old viable → new verdict → match`, boundary rows flagged, committed under fusion-tea's harness dir as the acceptance evidence. **100% agreement modulo a surfaced boundary row is the epic's Critical Success Factor** — link it into the Phase-6 close-out report.

**Validation:**
- [ ] Package regenerates lowered (viability assertion executing).
- [ ] Hand rule deleted (`grep -n "ETA_G_MIN\|eta_g >" sweep_ife.py` → zero at `:82`); LCOE overlay at `:84` intact.
- [ ] Acceptance table shows 100% match (or a surfaced, flagged boundary row).
- [ ] Prepare-once benchmark recorded.

**Report back:** the acceptance table path, match result, boundary-row disposition, and benchmark, for the Phase-6 reconcile.

---

## Implementation Notes
[TO BE FILLED DURING IMPLEMENTATION — leave empty now]

### Phase 1 Completion
### Phase 2 Completion
### Phase 3 Completion
### Phase 4 Completion
### Phase 5 Completion
### Phase 6 Completion

---

**Status:** Draft → In Progress → Complete
