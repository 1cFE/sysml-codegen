# Spec: Migration, Docs, and IFE Acceptance

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-13
**Complexity:** HIGH
**Branch:** constraint-exec-epic
**Epic:** CONSTRAINT-EXEC — Item 14 (closing item)

---

## Problem

The constraint-execution system is built. Items 1–13 landed the neutral facts, the executable
profile, concrete lowering, constraint generation, snapshot carriage, contracts, and the teax
study layer. But the old world it replaces is still standing next to it, and the loop the epic
opened is not yet closed.

Three concrete gaps remain, and this item is the only place they close:

1. **The drop-manifest era still runs.** Every extracted constraint is still swept into a drop
   manifest and reported as "not executable" — two blanket warnings, a snapshot section, and a
   test family all anchored on dropping (`extraction/constraint_report.py`). The new catalog
   (`generation/constraint_catalog.py`) now carries the same constraints as executable source
   records and concrete entries. Two surfaces describe the same constraints with opposite verdicts.
   Until the manifest retires against a proven 1:1 mapping, a reader can't trust which is true.

2. **The docs still teach the opposite of what the system now does.** Authoring guidance
   (`docs/architecture/modeling-assumptions.md:400`, "Constraints Are Not Executable") tells
   modelers their limits are dropped. That is now false. Architecture docs have no coverage of the
   lowering phase, catalog, contracts, evaluator, or study layer, and the verification matrix has
   no rows for the new REQ families.

3. **The IFE sweep still judges viability by hand.** The fusion-tea sweep harness re-implements the
   viability rule in Python (`~/1cfe/fusion-tea`, the `exploration/ife_e2e` surface), where nothing
   stops it drifting from the model it claims to represent. This is the exact drift the epic named
   in its Problem statement and its Critical Success Factor. The generated assertion now exists;
   the sweep does not yet use it.

Closing the loop has a hard **prerequisite** the run accumulated. fusion_tea's `'Viability
Threshold'` assertion cannot lower today. The constraint def (`fusion_cycle.sysml:29-51`) is
`eta * gain >= threshold` with `threshold` defaulting to `10.0`; the assert usage
(`generic_ife/ife_plant.sysml:155`) binds `in eta = driver.efficiency; in gain = gain;`. That
`in gain = gain` actual traces to a top-level design-instance self-redefinition —
`hif_plant.sysml:87`'s `:>> gain = 80.0` — that `materialize_supplied_values`
(`resolution/supplied_values.py`) does not synthesize a design attribute for, so the strict
resolver raises `unresolved actual 'gain'` — a halt, not a "cataloged unassessed" path. Item 8
grandfathered the two affected fixtures (`plant_values`, `fusion_tea`) flag-off behind a loud,
named exclusion list and handed this item the fix as its **named, first work** (Item 8 spec lines
199–208; Item 5 plan Phase-4 third pass). Without the fix, the acceptance test — "replaced by the
generated assertion" — is unreachable.

This item retires the drop-manifest era against a proven 1:1 migration, flips the docs across all
three repos, fixes the `gain` extraction gap so the two grandfathered fixtures re-land lowered,
sweeps the small recorded seams the run left open, and passes the concept's acceptance test on the
real IFE sweep.

## Success Criteria

Grouped by the four workstreams. Each is an outcome, concrete and checkable.

**Prerequisite — the `gain` gap and the grandfathered pair**

- [ ] `materialize_supplied_values` synthesizes a design attribute for a top-level design-instance
      `:>>` self-redefinition, so `fusion_tea`'s `'Viability Threshold'` assertion resolves its
      `gain` actual and lowers instead of halting.
- [ ] `plant_values` and `fusion_tea` re-land **lowered** under their own byte-identity gates;
      Item 8's named exclusion list (the GRANDFATHERED set) shrinks to **empty**, and the loud
      flag-off carve-out is removed.

**Migration — retire the drop-manifest era**

- [ ] Every constraint in today's drop manifest maps to **exactly one** catalog source record — a
      kept test proves the 1:1 correspondence (not a count match: each manifest entry names its
      source record).
- [ ] Every source record expands to **≥1 concrete entry**, or is explicitly recorded as
      unassessed / inventory (a source with no concrete instance is inventory, never silent).
- [ ] The drop manifest and **both** blanket warnings are deleted; `grep` finds no drop-manifest
      emission and no blanket "not executable" warning in `src/`.
- [ ] The REQ-EXT-09 test family and its constraint-adjacent kin re-anchor on the catalog (the
      1:1 mapping and catalog contents), not on the manifest.

**Docs — across all three repos**

- [ ] Authoring guidance flips from "constraints are not executable" to teaching the **executable
      profile and its block list**, including the real-equality → explicit two-inequality-band idiom.
- [ ] Architecture docs cover the new lowering phase, the catalog, the contracts, the evaluator,
      and the study layer.
- [ ] The verification matrix gains rows for the new REQ families under the register discipline
      (index family counts and STATUS recounted, not just the summary block).
- [ ] Docs are updated in **all three repos** (agentic-mbse, sysml-codegen, teax).

**Acceptance — the IFE sweep**

- [ ] The fusion-tea IFE package regenerates **lowered** (with the viability assertion executing).
- [ ] The sweep harness's hand-coded viability rule is **deleted** and replaced by the generated
      assertion, consumed through the study layer (teax study CLI/API, Items 10–12).
- [ ] **Every existing grid classification matches** — 100% agreement between the pre-migration
      hand-coded classifications and the generated-assertion verdicts across the full grid.
- [ ] The cross-model prepare-once benchmark is recorded (the S5 carry-forward measurement, on the
      real IFE package).

**Small recorded seams — swept, not left open**

- [ ] The three seams the run flagged (GENERATOR_MISMATCH second env axis; teax loader seal
      verification wiring; tracking-key correlation docs note) are each either wired or documented,
      with the disposition recorded.

**Epic close**

- [ ] The epic's top-level Success Criteria checklist is fully checkable (every box traceable to a
      landed item or this item's evidence).

## Known Requirements

### Prerequisite: the `gain` extraction-gap fix

- **[HARD]** fusion_tea's `'Viability Threshold'` must lower for acceptance to be possible. Its
  `in gain = gain` actual (assert usage `generic_ife/ife_plant.sysml:167-168`) is unresolved today
  because `materialize_supplied_values` (`resolution/supplied_values.py`) does not synthesize a
  design attribute for a **top-level design-instance `:>>` self-redefinition** (`hif_plant.sysml:87`
  `:>> gain = 80.0`); the strict resolver then raises `unresolved actual 'gain'` (INV-2 halt).
  Acceptance ("replaced by the generated assertion") forces this fix — it is not optional cleanup.
  (Verified in-repo: constraint `eta * gain >= threshold`, `threshold` default `10.0`, at
  `fusion_cycle.sysml:46-50`.)
- **[INHERITED: Item 8 spec lines 184–208; Item 5 plan Phase-4 third pass]** The fix is the
  materializer synthesizing the missing self-redefinition design attribute; then the two
  grandfathered fixtures (`plant_values`, `fusion_tea`) re-land **lowered** under their own
  byte-identity gates, and Item 8's named exclusion list shrinks to empty. Item 8 recorded and
  declined two alternatives — (b) convert the pair to expected-halt rejection fixtures; (c)
  pre-filter the constraint via Item 3's profile — for this fix path. Do not re-litigate; they are
  decision records.

### Migration: the manifest→catalog 1:1 mapping and the deletions

- **[INHERITED: concept Migration invariant, line 153; epic Item 14 §1]** Every constraint in
  today's drop manifest maps to **exactly one** source record in the new catalog, and every source
  record expands to **one or more** concrete entries (or is explicitly unassessed/inventory). The
  blanket warnings retire **with** the manifest. This 1:1 mapping is a **kept test**, not a
  one-time check.
- **[HARD]** The migration reconciles two concrete surfaces:
  - **Retire:** the drop report (`extraction/constraint_report.py` — `render_constraint_report`,
    `collect_constraint_manifest`), its two blanket warnings (the per-predicate INFO at
    `constraint_report.py:125-132` and the summary WARN at `:135-141`), and the
    `dropped_constraints` snapshot section (writer `snapshot/serializer.py:133`, reader
    `snapshot/loader.py:238`, capture feed `snapshot/capture.py:67`).
  - **Anchor onto:** the catalog — `ConstraintCatalogSourceRecord` (`resolution/models.py:325`),
    `ConstraintCatalogEntry` (`:338`), `ConstraintCatalog` (`:357`), assembled by
    `assemble_constraint_catalog` (`generation/constraint_catalog.py:60`).
- **[HARD]** Deletion is grep-verifiable: no drop-manifest emission and no blanket "not
  executable" warning remains in `src/`. (Distinct from the *generation-halt* diagnostic at
  `analysis/constraint_lowering.py:481` — that is the loud out-of-profile block the epic **keeps**,
  not a blanket drop warning; do not delete it.)
- **[INHERITED: epic Item 14 §1]** The REQ-EXT-09 family re-anchors on the catalog. Concretely the
  known anchors are `tests/conformance/test_extractor.py` (`TestReqExt09ConstraintDropDiagnostic`
  at `:892`, `CATF_DROPPABLE = 65`; `TestConstraintRequireAndExclusion`;
  `TestConstraintDroppablePolicyParity`) and `tests/conformance/test_snapshot_contract.py:91`
  (the wi014 manifest round-trip). Design maps each retained assertion from "the manifest
  reported it dropped" to "the catalog carries it as source record + concrete entry / inventory."
- **[INFERRED]** The from-snapshot replay of the drop report (`snapshot_context.py:45`) retires
  with the manifest; the offline path already assembles the catalog
  (`snapshot/graph_rebuild.py:211`). The snapshot format's `dropped_constraints` section is removed
  or emptied — design decides whether this is a further format-version bump or a within-v3 section
  removal (the catalog is already the load-bearing v3 section).

### Docs: flip the authoring guidance and cover the new architecture

- **[INHERITED: concept Next-Stage Handoff, line 238; epic Item 14 §2]** Authoring guidance flips
  from teaching "constraints are not executable" to teaching the **executable profile and its block
  list**. The block list (concept line 188): invocation, conditional, temporal, unit conversion,
  and real-valued equality are blocked; the authoring fix for real equality is an **explicit
  two-inequality band**. In-repo anchor: `docs/architecture/modeling-assumptions.md:400` (section
  8) and its cross-references (`reference/01-extraction.md:20`, `reference/02-orchestration.md:40`,
  `verification-matrix.md:228`).
- **[INHERITED: epic Item 14 §2; concept]** Architecture docs cover the new **lowering phase**,
  **catalog**, **contracts**, **evaluator**, and **study layer**.
- **[INHERITED: memory verification-matrix-drift-modes; epic Item 14 §2]** Verification-matrix rows
  are added under the **register discipline**: recount index family counts and STATUS from the
  actual table rows (anchor the status column, don't substring-match), and cross-check
  `grep -o 'REQ-[A-Z]*-[0-9]*' docs/architecture/reference/*.md` against the matrix so new REQ
  families (constraint lowering, generation, catalog, contracts, study) get rows.
- **[NEED]** *(brief; epic success criteria)* Docs are updated in **all three repos** —
  agentic-mbse (facts/profile authoring surface), sysml-codegen (this repo's authoring +
  architecture docs), teax (evaluator + study-layer docs). The exact file set per repo is design's
  to enumerate; the outcome is that no repo's docs still describe the retired behavior.

### Acceptance: the IFE sweep migration

- **[INHERITED: concept Validation Strategy — Acceptance, line 221; epic Critical Success Factor]**
  The IFE sweep's hand-coded viability rule is **replaced by the generated assertion** and **every
  existing grid classification matches**. This is the epic's Critical Success Factor and the single
  most load-bearing outcome of the item. The generated assertion is the in-repo-verified viability
  constraint: `eta * gain >= threshold` (`fusion_cycle.sysml:50`, `threshold` default `10.0`),
  asserted at `generic_ife/ife_plant.sysml:155` binding `eta = driver.efficiency`, `gain = gain`.
  The sweep grid varies `eta` (driver efficiency) and `gain`; a point is viable when the assertion
  is `satisfied`.
- **[HARD]** The fusion-tea IFE package must be regenerated **lowered** (viability assertion
  executing) — which is why the `gain` fix is a prerequisite. The generated verdict is consumed
  through the **study layer** (teax study CLI/API, Items 10–12), not by calling generated impls
  directly. (Memory `item3-fusiontea-acceptance-facts`: today `sweep_ife.py` calls generated impls
  directly and never used the instance channel — the migration routes it through the study layer
  instead.)
- **[NEED]** *(brief; S5 carry-forward (2))* Record the **cross-model prepare-once benchmark** on
  the real IFE package (prepare-once vs rebuild). This is a recorded measurement, not a tuning
  target (see Non-Goals).
- **[HARD]** The live legs of acceptance (regenerating fusion-tea, running the sweep) need the
  license env and fusion-tea access. License env: `env $(grep -v '^#' ~/1cfe/agentic-mbse/.env |
  xargs) uv run ...`. Live-vs-snapshot byte-diff of fusion_tea needs an **absolute `--models`
  path** (memory `item3-fusiontea-acceptance-facts` — the abs-path parity gotcha). **Access
  caveat: fusion-tea is outside this session's sandbox** — see Open Questions.

### Small recorded seams — sweep each

- **[INHERITED: Item 9 audit note 2, CURRENT_WORK]** **GENERATOR_MISMATCH second env axis.** The
  `GENERATOR_MISMATCH` diagnostic kind (`contracts/verify.py:24`) is reserved but unreachable — no
  `generator_version` axis feeds it. Wire the axis (so a generator-version mismatch is detectable)
  or document it as an intentional reserved seam and remove the dead reachability expectation.
  Disposition is recorded either way.
- **[INHERITED: Item 9 design D7 seam, CURRENT_WORK]** **teax loader seal verification wiring.**
  The `verify_package(dir, name, runtime_version, strict)` signature and the self-describing seal
  are fixed by Item 9; the teax loader wiring (load-by-declared-name, inject the runtime marker,
  choose strict) was named a mechanical Item 10/14 change. Wire it (the acceptance run loads a
  sealed IFE package through teax, so this seam is exercised for real here).
- **[INHERITED: Item 12 spec]** **Tracking-key correlation docs note.** Document that a
  `tracking_key` correlates a logical constraint across model versions by **name only** — names
  correlate, never equate across fingerprint boundaries (concept Vocabulary, line 209).

## Non-Goals

- **New IFE modeling.** Acceptance runs the existing IFE model and grid; it does not add or change
  modeled physics.
- **Performance tuning beyond recording the benchmark.** The prepare-once benchmark is measured and
  recorded; no optimization work is in scope.
- **Changing the executable profile, the catalog schema, the contracts, or the study layer.** Those
  are Items 3, 7, 9, 10–12. This item migrates onto them, documents them, and accepts against them;
  it does not reshape them. (The `gain` materializer fix is the one deliberate production change,
  scoped to the extraction gap the run named — not a profile or schema change.)
- **Retiring the generation-halt diagnostic** (`constraint_lowering.py:481`). That loud
  out-of-profile block is kept; only the *blanket drop* warnings retire.

## Open Questions / Deferred to design

- **fusion-tea harness access boundary (surfaced — parked, not resolved).** The **model side** of
  acceptance is now pinned (verified in-repo against the `fusion_tea` fixture: the constraint def,
  predicate, assert usage, and `gain` redefinition, cited above). What remains **unreadable** is the
  fusion-tea **harness** itself: the verbatim hand-coded Python viability rule the migration
  deletes, and the location/shape of the existing grid-classification ground truth (a saved golden
  CSV/JSON vs computed-each-run) — the `~1/100` comparison target. Those live only in
  `~/1cfe/fusion-tea`, which is **outside this session's allowed working directories**: I attempted
  direct access this turn — `Bash find` is hard-blocked at the directory boundary (even with the
  sandbox override), and the `Read` tool is permission-gated with no way to grant it in a headless
  session. Before implement can run, the session (and the orchestrated implement session) must be
  granted access to `~/1cfe/fusion-tea` (and `~/1cfe/agentic-mbse`, `~/1cfe/teax` for the cross-repo
  legs). **This is an environment prerequisite for implement, flagged to the orchestrator, not a
  scope question** — the outcome is fully specified from the model side; only the deletion target
  and golden location await access.
- **Study-layer consumption mechanism — CLI vs API.** Whether the sweep drives the generated
  assertion through the teax study CLI or its API, and how the sweep's grid maps onto a
  `StudyDefinition` (list vs grid strategy), is design's. The requirement is that the verdict comes
  from the generated assertion via the study layer, not from a hand-coded rule.
- **The classification-match harness.** How the 100%-match check is structured — replay the grid
  through both the (about-to-be-deleted) hand rule and the generated verdict once to build the
  comparison, then delete the hand rule; or compare the generated verdicts against a captured golden
  of the old classifications. Design picks; the golden's existence/location is part of the
  fusion-tea investigation gated on access above.
- **Snapshot `dropped_constraints` removal shape.** Whether removing the retired section is a
  format-version bump or a within-v3 removal (the catalog is already the load-bearing v3 section).
- **Exact per-repo docs file set.** Which files in agentic-mbse and teax carry the flipped authoring
  guidance and the new architecture coverage.
- **Sequencing against teax Items 10–12.** Acceptance depends on the study layer (Items 10–12) being
  landed. If they are not yet green on the branch when implement starts, acceptance is blocked on
  them — a dependency the orchestrator sequences, noted here so it is not discovered late.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_constraint_execution.md` (Item 14)
- **Required Reading (from the epic):** concept **Problem** (line 19) + **Migration invariant**
  (line 153, Required Invariant) + **Validation Strategy — Acceptance** (line 221); memory:
  `item3-fusiontea-acceptance-facts` (retirement grep scope, per-consumer gain key, abs-path parity
  gotcha); memory: `plant-idiom-fixtures`.
- **Concept (owner-ratified):**
  `.project/concepts/constraint-execution-and-design-space-studies-claude.md` — Problem; Required
  Invariants (Migration, line 153); block list (line 188); Validation Strategy (Acceptance, line
  221); Next-Stage Handoff (migration of manifest/warnings/tests/authoring guidance, line 238).
- **Discharged handoff ledger (recorded in the named items' artifacts):**
  - The `gain` gap prerequisite — `.project/active/snapshot-v3/spec.md` (lines 184–208);
    `.project/active/constraint-lowering/plan.md` (Phase-4 third pass); Item 8 audit.
  - The grandfather carve-out — `.project/active/snapshot-v3/spec.md`; `test_grandfather_carveout.py`.
  - GENERATOR_MISMATCH + teax-loader-seal seams — Item 9 audit / design (CURRENT_WORK Item 9 entry).
  - Tracking-key correlation note — Item 12 spec.
- **In-repo surfaces (read directly for design):**
  - Drop report: `src/sysml_codegen/extraction/constraint_report.py`;
    `src/sysml_codegen/extraction/extractor.py:98,112`;
    `src/sysml_codegen/orchestration/pipeline_builder.py:760`;
    `src/sysml_codegen/orchestration/snapshot_context.py:45`.
  - Snapshot manifest: `snapshot/serializer.py:133`, `snapshot/loader.py:238`, `snapshot/capture.py:67`.
  - Catalog: `resolution/models.py:325,338,357`; `generation/constraint_catalog.py:60`.
  - Materializer gap: `resolution/supplied_values.py`.
  - IFE model (in-repo fixture mirror): `tests/fixtures/fusion_tea/library/analyses/fusion_cycle.sysml:29-51`
    (constraint def); `.../designs/generic_ife/ife_plant.sysml:155-169` (assert usage);
    `.../designs/hif_ife/hif_plant.sysml:87` (`:>> gain = 80.0`).
  - Seams: `contracts/verify.py:24`; `analysis/constraint_lowering.py:481` (the kept halt).
  - Docs: `docs/architecture/modeling-assumptions.md:400`; `docs/architecture/verification-matrix.md`.
- **Environment:** fusion-tea checkout `~/1cfe/fusion-tea` (owner-authorized modification, but
  outside the session sandbox — see Open Questions); license env
  `env $(grep -v '^#' ~/1cfe/agentic-mbse/.env | xargs) uv run ...`.
- **Design:** `.project/active/constraint-migration-acceptance/design.md` (to be created)

---

**Next Steps:** After approval, proceed to `/_my_design`. Before implement, the fusion-tea /
agentic-mbse / teax access boundary (Open Questions) must be resolved by the orchestrator.
