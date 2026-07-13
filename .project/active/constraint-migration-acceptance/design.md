# Design: Migration, Docs, and IFE Acceptance

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-13
**Branch:** constraint-exec-epic (head `1706f03` at authoring; Item 13 session committing concurrently)
**Epic:** CONSTRAINT-EXEC — Item 14 (closing item)

## Overview

Retire the drop-manifest era against a proven per-usage manifest→catalog mapping, flip the docs in
all three repos, fix the `gain` extraction gap so the two grandfathered fixtures re-land lowered,
pass the IFE sweep acceptance through the study layer, and sweep three recorded seams.

## Related Artifacts

- **Spec:** `.project/active/constraint-migration-acceptance/spec.md` (read fully)
- **Reference (fusion-tea harness):** `.project/reference/fusion-tea-ife-sweep/FACTS.md` — deletion
  target `sweep_ife.py:82` (`viable = eta_g > ETA_G_MIN`, `ETA_G_MIN = 10`), outputs at
  `exploration/ife_e2e/outputs/`, LCOE overlay stays hand-coded, `>` vs `>=` boundary hazard.
- **Concept (owner-ratified):** `constraint-execution-and-design-space-studies-claude.md` — Migration
  invariant (line 153), block list (188), Acceptance (221), Next-Stage Handoff (238).
- **Landed upstream reference (in-repo mirror):** `.project/reference/agentic-mbse-landed/` —
  `constraint_extraction.py`, `constraint_facts.py` (source-of-truth for the catalog vocabulary).
- **Memory:** `item3-fusiontea-acceptance-facts`, `plant-idiom-fixtures`, `verification-matrix-drift-modes`.

## Research Findings

- **Manifest and catalog sweep the identical population.** `collect_constraint_manifest`
  (`extraction/extractor.py:112`) and `extract_constraint_facts`
  (`reference/agentic-mbse-landed/constraint_extraction.py:118`) both call
  `elements_of_type(model, "ConstraintUsage", include_subtypes=True)`. So every manifest entry has
  exactly one `ConstraintUsageFact` counterpart, joinable by usage identity. This is the fact that
  makes a 1:1 mapping test *possible* — the two surfaces are not disjoint.
- **Three granularities, not two.** The manifest is per source usage. The catalog splits into
  `source_records` (per constraint *definition*, `facts.definitions`, `models.py:325`) and
  `concrete_entries` (per *instance occurrence*, `models.py:338`). One usage on a part_def with N
  instances mints N concrete entries sharing one `usage_qualified_name`. **The per-usage carrier in
  the catalog is the concrete entry (or an unassessed record), not the source record.** Source
  records are the many-to-one vocabulary layer above.
- **Lowering disposition is three-way** (`analysis/constraint_lowering.py:490`): each usage is
  ADMIT → one-or-more eligible concrete entries; not-ADMIT / non-`part_def|calc_def|package` owner →
  one `eligible=False` unassessed record (`:498`); BLOCK → the kept generation halt (`:481`), which
  is loud and out of scope to retire.
- **catf_mfe = 65 plain, 0 assert.** The REQ-EXT-09 anchor fixture (`test_extractor.py:909`,
  `CATF_DROPPABLE = 65`) carries 65 plain inline `constraint {}` usages and no asserts (verified:
  `grep -n '\bassert\b' tests/fixtures/catf_mfe_model` returns nothing). Whether the profile ADMITs
  a non-asserted inline constraint or catalogs it unassessed determines the eligible/unassessed split
  — see Risk R1. Either way each of the 65 has a catalog carrier; none goes silent.
- **The `gain` gap is a tier miss, not a missing capture.** `hif_plant.sysml:87` `:>> gain = 80.0`
  is a *self-redefinition owned by the design instance itself*. The assert binds `in gain = gain`
  (`ife_plant.sysml:167`, bare name). `_binding_target` routes the bare name to
  `qn = f"{instance_scope}__gain"` (`supplied_values.py:96`), then all three precedence tiers miss:
  tier 1's bare-override branch tests `owning_part_qn == f"{instance_scope}__gain"` (`:129`) but the
  redef's owner is `instance_scope` itself; tier 2a needs a `usage_type_map` key; tier 2b needs the
  redef owned by the *consuming part def*. None matches an instance self-redefinition.
- **Snapshot removal can stay within v3.** `SNAPSHOT_FORMAT_VERSION = 3` (`snapshot/__init__.py:19`);
  the loader already reads `raw.get("dropped_constraints", [])` (`loader.py:239`) — tolerant of
  absence. The catalog is already the load-bearing v3 section.

## Core Concept

The old world and the new world describe the *same set of constraint usages* with opposite
verdicts. The migration does not delete one surface and hope the other covers it — it **proves, as a
kept test, that every usage the manifest reported is carried by the catalog**, then deletes the
manifest. The proof is a per-usage join: sweep the manifest, sweep the catalog, and show a total
function from each manifest droppable entry to its catalog carrier — an eligible concrete entry (≥1,
grouped by `usage_qualified_name`) or an explicit unassessed record — with nothing silently absent.
Requirement-side entries (the manifest's *excluded* set) map to unassessed or are legitimately
carrier-free, and the test records that distinction rather than hiding it.

Once the catalog is the proven single source of truth for "what constraints exist and what happens
to them," the manifest, its two blanket warnings, the snapshot section, and the report replay are
dead weight — deleted. The docs then flip to teach the executable profile instead of "constraints
are not executable," and the IFE sweep swaps its hand-coded rule for the generated assertion, read
through the study layer. The gain fix is the enabling precondition: without it the one real
executable assertion in the corpus (`'Viability Threshold'`) cannot lower, so acceptance is
unreachable.

The design's load-bearing insight: **the correspondence is manifest-usage ↔ catalog-usage-carrier,
not manifest ↔ source-record.** The spec and concept say "source record," but source records are
per-definition and cannot carry an inline constraint (which has no definition) or distinguish N
instances of one usage. Reading it as the per-usage carrier is what makes the invariant both
satisfiable and honest.

> **Surfaced premise conflict (capture-fidelity Law 4).** The spec/concept say each manifest entry
> "maps to exactly one *source record*." Taken literally against the built catalog, that is
> unsatisfiable: source records are per-definition, an inline constraint has no definition, and one
> usage fans out to N instance occurrences. This design reinterprets the invariant as manifest-usage
> → per-usage carrier (concrete entries / unassessed record), with a separate arm asserting every
> source record is referenced. Spec line 159 ("the catalog carries it as source record + concrete
> entry / inventory") supports this reading. **Flagged for the design_review / owner to confirm** —
> not resolved silently. See D1.

## Key Bets

- **B1. The manifest and catalog sweep the same population, so a total per-usage mapping exists.**
  *If false → the 1:1 test cannot be authored; some manifest entries have no catalog counterpart and
  the migration cannot retire the manifest without going silent on them.* (Strongly evidenced: both
  call the identical `elements_of_type` sweep; the residual risk is an ordering/identity-key
  mismatch, not a population gap.)
- **B2. The `gain` gap is the *only* blocker to lowering `'Viability Threshold'`.** *If false → the
  fixtures still don't re-land lowered after the materializer fix; acceptance stays blocked on a
  second, unnamed extraction gap.* (Evidenced: the constraint def, predicate, and both actuals
  resolve; only `gain` traces to the unmaterialized self-redefinition.)
- **B3. The pre-migration grid classifications and the generated-assertion verdicts agree except at
  the `>`/`>=` boundary.** *If false → acceptance fails and either the model, the profile, or the
  study wiring is wrong — a real defect, not a harness artifact.* The boundary point (`eta*G == 10`)
  is a *known, expected* single-row divergence to surface, not a failure.
- **B4. The study layer (Items 10–12) can drive the generated viability assertion over the grid and
  return per-point verdicts.** *If false → acceptance has no execution home and the sweep cannot be
  re-pointed at the model.* (Depends on 10–12 being green on the branch — sequencing risk, not a
  design risk.)

## Key Decisions

- **D1. The 1:1 mapping test joins manifest-usage → catalog-usage-carrier, keyed by usage identity.**
  *Rejected: manifest → `source_records` (definitions) — the spec's literal wording — because it is
  many-to-one, cannot carry inline constraints, and erases the instance fan-out. Rejected: a count
  match — the spec explicitly forbids it.* The carrier is the set of concrete entries sharing the
  usage's `usage_qualified_name`, or its unassessed record. The test additionally asserts every
  `source_record` (definition) is referenced by ≥1 usage — the vocabulary-coverage arm.
- **D2. Fix the `gain` gap by adding an instance-self-redefinition tier to the materializer.** The
  new case matches a redef/override whose `owning_part_qn == instance_scope` and
  `attribute_name == target.attr` with no `target_path`, for a bare-name binding target — synthesizing
  one design attribute keyed `{instance_scope}__{attr}`. *Rejected (Item 8 decision records, do not
  relitigate): (b) convert the pair to expected-halt fixtures; (c) pre-filter via the Item 3 profile.*
- **D3. Remove `dropped_constraints` within format v3, no version bump.** Serializer stops emitting
  the key (`serializer.py:133`); loader stops reading it (`loader.py:238-239`). *Rejected: a v3→v4
  bump — it would force re-capture of all 29 golden snapshots (pure churn) when the catalog is
  already the load-bearing v3 section and old snapshots' vestigial key loads harmlessly.*
- **D4. The acceptance comparison is built by replaying the grid through both rules once, in the same
  run, then deleting the hand rule.** *Rejected: capture a golden of the old classifications first,
  compare against it later — it adds a golden-provenance question (FACTS.md notes the ground truth's
  existence/shape is only confirmable with harness access) and a second artifact to keep honest.*
  The one-run replay makes the comparison self-evidently apples-to-apples.
- **D5. The acceptance report is a committed table** — `grid point (eta, G) → old viable → new verdict
  → match` — with the boundary row flagged. Committed under fusion-tea's harness dir as the
  acceptance evidence.

## Architecture

Five workstreams, sequenced by the orchestrator across four repos. Dependencies flow left to right:
the gain fix unblocks lowering; lowering unblocks both the mapping test (catalog is populated for
the fusion fixtures) and acceptance (assertion executes).

```
(1) gain fix ─┬─→ (2) manifest retirement + 1:1 test + REQ-EXT-09 re-anchor   [sysml-codegen]
              └─→ (4) IFE acceptance: regen lowered → study-layer verdict      [fusion-tea]
                        → row-by-row compare → prepare-once benchmark
(3) docs flip across agentic-mbse / sysml-codegen / teax   [3 repos, parallel to 2/4]
(5) three seams: GENERATOR_MISMATCH · teax loader seal · tracking-key note   [sysml-codegen/teax]
```

**Repo split** (orchestrator sequences the sessions):
- **sysml-codegen:** gain fix (W1), manifest retirement + mapping test + REQ-EXT-09 re-anchor (W2),
  this repo's docs (W3a), GENERATOR_MISMATCH seam disposition (W5a).
- **agentic-mbse:** facts/profile authoring-surface docs + any L4/L6 verification-matrix rows (W3b).
- **teax:** evaluator + study-layer docs (W3c), loader seal-verification wiring (W5b),
  tracking-key correlation note (W5c).
- **fusion-tea:** sweep replacement + acceptance report + prepare-once benchmark (W4).

**Retire (W2), grep-verifiable:** `render_constraint_report`, `collect_constraint_manifest`,
`report_dropped_constraints` (`extraction/extractor.py:98,112`), the whole `constraint_report.py`
render/serialize helpers, the two blanket warnings (`constraint_report.py:125-141`), the
`dropped_constraints` snapshot section (`serializer.py:133`, `loader.py:238`, `capture.py:67`), the
call site (`pipeline_builder.py:760`), and the from-snapshot replay (`snapshot_context.py:45`).
**Keep (explicit non-goal):** the generation-halt at `constraint_lowering.py:481`.

## Required Invariants

- **INV-A (no silent drop).** After retirement, every constraint usage that the manifest would have
  reported has a catalog carrier or an explicitly recorded disposition. The 1:1 test is the guard;
  it fails loudly if a usage falls through.
- **INV-B (grep-clean).** No drop-manifest emission and no blanket "not executable" warning remains
  in `src/` (spec `[HARD]`). The kept generation-halt diagnostic is distinct and stays.
- **INV-C (byte-identity holds for unchanged fixtures).** Only `plant_values` and `fusion_tea`
  re-capture (the gain fix); the other 27 snapshots do not churn. Run the timestamp-only diff gate
  (memory `byte-identity-captured-at-churn`).
- **INV-D (GRANDFATHERED → empty).** Item 8's named exclusion list shrinks to empty and the loud
  flag-off carve-out is removed; the two fixtures lower under their own byte-identity gates.
- **INV-E (100% grid agreement modulo the boundary).** Every existing grid classification matches the
  generated verdict, except a surfaced boundary row if one exists.

## Component Overview

- **Materializer instance-self-redefinition tier** (`resolution/supplied_values.py`) — W1. Adds the
  one new precedence case (D2). Demand-scoped and literal-only like the existing tiers, so it fires
  only for a referenced bare-name binding whose attribute has a top-level instance `:>>` literal.
- **Manifest→catalog mapping test** (`tests/conformance/`, re-anchoring the REQ-EXT-09 family) — W2.
  A kept test asserting the total per-usage function (D1) and the vocabulary-coverage arm. Replaces
  `TestReqExt09ConstraintDropDiagnostic`, `TestConstraintRequireAndExclusion`,
  `TestConstraintDroppablePolicyParity` (`test_extractor.py:893-1044`) and the wi014 manifest
  round-trip (`test_snapshot_contract.py:91`).
- **Doc surfaces** — W3. See Appendix A for the per-repo file list.
- **IFE acceptance harness** (fusion-tea `exploration/ife_e2e/`) — W4. Re-points `sweep_ife.py` from
  the hand rule at `:82` to a study-layer verdict; emits the D5 comparison table; records the
  prepare-once benchmark. LCOE overlay at `:84` stays hand-coded (study policy).
- **Seam dispositions** — W5. GENERATOR_MISMATCH (`contracts/verify.py:24`): wire a
  `generator_version` axis or document-and-remove the dead reachability expectation. teax loader
  seal wiring: load-by-declared-name + runtime marker + strict choice (exercised for real by the
  acceptance load). tracking-key note: names correlate, never equate across fingerprint boundaries.

## Non-Goals

- New IFE modeling; the executable profile, catalog schema, contracts, or study layer reshaped (the
  gain materializer fix is the one deliberate production change). Performance tuning past recording
  the benchmark. Retiring the generation-halt diagnostic. (Per spec Non-Goals.)

## Implementation Notes

- **Mapping-test join key.** Manifest entries carry `(owner_qualified_name, constraint_name,
  source_line)`; concrete entries carry `usage_qualified_name` + `source_local_identity`. The stable
  join is the usage's qualified name (with source location as the anonymous-assertion tiebreak, the
  same identity `_source_local_identity` uses at `constraint_lowering.py:379`). Confirm the two
  identity renderings agree on the anonymous case before locking the test.
- **Gain fix precedence.** Insert the instance-self-redef case at the correct precedence — below a
  genuine usage-level override, above nothing — so it never shadows an existing tier-1 match. The
  bare-name target already computes the right synthetic QN; the fix is the *match*, not the key.
- **Acceptance license/path.** Live legs need `env $(grep -v '^#' ~/1cfe/agentic-mbse/.env | xargs)
  uv run …`; the live-vs-snapshot byte-diff of `fusion_tea` needs an **absolute** `--models` path
  (memory `item3-fusiontea-acceptance-facts`). The sweep must route through the study layer, not call
  generated impls directly (today's `sweep_ife.py` does the latter).
- **Boundary detection.** The comparison must compute `eta*G` per point and flag any row where
  `eta*G == threshold` (10.0) — that is where hand `>` and modeled `>=` diverge. One such row is a
  real semantic difference to report in the acceptance table, not a mismatch to reconcile away.

## Potential Risks

- **R1 (profile disposition of non-asserted plain constraints — confirm empirically).** catf_mfe's
  65 plain constraints will land as *eligible* or *unassessed* depending on how `evaluate_profile`
  treats a non-asserted inline `constraint`. The mapping test must handle both dispositions; the
  implement session confirms the split by running extraction (needs license). This changes the test's
  *expected counts*, not its *structure*. If any of the 65 come back BLOCK, that is a real finding
  (catf_mfe would already be halting today) — surface it, don't absorb it.
- **R2 (gain-fix blast radius).** The new tier could over-match an instance `:>>` self-redef that
  should *not* become an entry point, churning an unrelated fixture's bytes. Mitigation: it is
  demand-scoped (only referenced bare-name bindings) and literal-only; the full byte-identity gate
  across all 29 snapshots is the backstop. Expect exactly two snapshots to change (`plant_values`,
  `fusion_tea`); any third change is a regression to investigate.
- **R3 (study-layer sequencing).** Acceptance depends on Items 10–12 being green on the branch. If
  they are not when W4 starts, acceptance is blocked on them — an orchestrator sequencing dependency,
  flagged here so it is not discovered late.
- **R4 (cross-repo access).** fusion-tea, agentic-mbse, and teax are outside this session's sandbox.
  The design specifies the model side fully; W3b/W3c/W4/W5b need the access the orchestrator grants
  to the implement sessions (spec Open Questions — environment prerequisite, not scope).

## Integration Strategy

The catalog already exists and is load-bearing (Items 5–9); this item removes its rival, not adds a
mechanism. The mapping test slots into the existing REQ-EXT-09 conformance family, re-anchored rather
than newly created. The acceptance re-points an existing harness through the already-certified study
layer. No new subsystem is introduced.

## Validation Approach

- **W1:** `plant_values` and `fusion_tea` re-capture and lower; GRANDFATHERED set empty; byte-identity
  gate shows exactly those two snapshots changed (timestamp-only check on the rest).
- **W2:** the 1:1 mapping test passes as a kept test; `grep` proves no manifest emission / blanket
  warning in `src/`; the retired REQ-EXT-09 tests are replaced, not merely deleted.
- **W3:** `grep -o 'REQ-[A-Z]*-[0-9]*' docs/architecture/reference/*.md` cross-checks the matrix;
  index family counts and STATUS recounted from table rows (memory `verification-matrix-drift-modes`);
  no repo's docs still say "constraints are not executable."
- **W4:** the committed acceptance table shows 100% agreement modulo a surfaced boundary row; the
  prepare-once benchmark is recorded.
- **W5:** each seam's disposition (wired or documented) is recorded.

## Next-Stage Handoff

- **Fixed:** the per-usage mapping join (D1); the gain-fix mechanism and its precedence (D2); the
  within-v3 snapshot removal (D3); the one-run acceptance-comparison method (D4/D5); the repo split.
- **Open for the plan/implement session:** the eligible/unassessed *counts* for catf_mfe (R1, needs
  license); the exact agentic-mbse/teax doc file set (Appendix A marks these design-best-guess pending
  access); CLI-vs-API choice for driving the study layer (either satisfies the requirement — verdict
  from the generated assertion via the study layer).
- **De-risk first:** the gain fix (W1). It is the precondition for both the populated catalog (W2's
  fusion fixtures) and acceptance (W4). Land it and re-capture before anything downstream.

## Appendix A — Per-repo doc file set (W3)

**sysml-codegen (verified surfaces):**
- `docs/architecture/modeling-assumptions.md:400` — flip section 8 ("Constraints Are Not Executable")
  to teach the executable profile + block list (invocation, conditional, temporal, unit conversion,
  real-valued equality) and the real-equality → explicit two-inequality-band idiom.
- Cross-refs to update: `reference/01-extraction.md:20`, `reference/02-orchestration.md:40`,
  `verification-matrix.md:228`.
- Architecture coverage (new or extended reference docs) for: lowering phase, catalog, contracts,
  evaluator, study layer.
- `verification-matrix.md` — add rows for the new REQ families (constraint lowering, generation,
  catalog, contracts, study) under the register discipline; recount index family counts + STATUS.

**agentic-mbse (design-best-guess, confirm with access):** the facts/profile authoring surface —
the `constraint_extraction` / `constraint_facts` / executable-profile doc(s) and any L4/L6
verification-matrix rows for the neutral-facts and profile REQ families.

**teax (design-best-guess, confirm with access):** the evaluator and study-layer docs (the surfaces
Items 10–12 added); the tracking-key correlation note (W5c) lands here.

## Appendix B — Retirement grep targets (W2)

Retire: `constraint_report.py` (render + `manifest_to_records`/`manifest_from_records`),
`extractor.py:98,112` (`report_dropped_constraints`, `collect_constraint_manifest`),
`pipeline_builder.py:760`, `snapshot_context.py:45`, `serializer.py:133`, `loader.py:238-239`,
`capture.py:67`. Keep: `constraint_lowering.py:481`. Re-anchor tests: `test_extractor.py:893-1044`,
`test_snapshot_contract.py:91`.

---
Next Step: `/_my_design_review` (fresh session), then `/_my_plan` or `/_my_implement`.
