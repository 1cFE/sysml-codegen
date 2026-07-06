# Epic: Upstream Findings Remediation & Plant-Idiom Support

**Epic ID**: UPSTREAM-FINDINGS
**Status**: Draft
**Priority**: High
**Created**: 2026-07-05
**Estimated Effort**: ~13–16 days (12 items; two parallel tracks)

---

## Executive Summary

The fusion-tea de-risk epic executed the full SysML → codegen → teax pipeline on models outside our fixture corpus for the first time and surfaced 11 findings (SC-1–SC-11). Deep research verified every symptom, corrected three misdiagnosed root causes, and found six additional defects. This epic fixes the verified bugs, adds staged support for the plant idiom that gates fusion-tea's MFE epic, closes the fixture blind spot that let all of this survive 1,500+ conformance tests, and keeps agentic-mbse's guidance and validation in lockstep at every step.

**Critical Success Factor**: The fusion-tea IFE model set generates a valid, correctly-wired package with no hand-built plumbing — and every newly supported (or explicitly rejected) SysML shape is locked in by a conformance fixture and matching agentic-mbse guidance.

---

## Mandatory Reading (every item)

Read these fully before spec'ing any item in this epic:

1. **The findings register** — `~/1cfe/fusion-tea/.project/reports/2026-07-05-upstream-findings-register.md` (what broke, how it manifested, downstream workarounds in place)
2. **The deep-research report** — `.project/research/20260705_upstream-findings-deep-research.md` (claim-by-claim verification against HEAD, corrected root causes, alternatives judged, per-finding fit/lift/risk, six new defects)
3. **The supported-subset contract** — `docs/architecture/modeling-assumptions.md` (what the pipeline promises; several findings are bugs precisely because this document already promises the behavior)

Where the register and the research report disagree, the research report wins — it was verified against current HEAD (e.g., SC-1's "Phase 6" was never a sysml-codegen plan; SC-6's root cause is branch ordering, not node-type naming; SC-4's fix belongs in the derivation layer, not templates).

---

## Cross-Cutting Requirements (apply to every item)

### R1 — Design-pattern consistency

This epic lands on top of a freshly refactored codebase with strong conventions. Every item MUST follow them rather than invent local solutions:

- **ComputationGraph is the sole input to generation** (REQ-PIPE-07 / REQ-ORCH-06). Any schema change to it is a deliberate, reviewed rev — never a drive-by field.
- **Typed registries and NewType identifier keys** (doc 10, doc 15). New lookups go through the typed dispatch; new keys are unique by construction and consumer-scope-prefixed. Do not reintroduce ambiguous string keys.
- **"Compute once, look up thereafter"** (modeling-assumptions §7). Identifiers are derived at extraction and looked up downstream — sanitization fixes follow this principle (fix at the source, not per-consumer).
- **Diagnostics follow the V1–V6 pattern** (modeling-assumptions "Validation Rules"): a rejected shape gets a clear, actionable error naming the fix; nothing is dropped silently.
- **Conformance tests use real SysML fixtures, never mocks** — mocks masked SC-6 (mock nodes lack SysIDE's derived `.function`) and SC-3 (mock `types` lists had one element). New behavior lands with a real fixture + snapshot.
- **Requirement IDs + docs move with code**: new/changed behavior gets REQ-* tags, verification-matrix rows, and updates to the relevant `docs/architecture/reference/` doc.

### R2 — agentic-mbse matching updates

sysml-codegen defines the executable subset; agentic-mbse teaches and audits it. **Every item MUST end by recording (and where trivial, implementing) the matching agentic-mbse changes**, so the two never drift:

- **Correct patterns to teach**: updates to MODELING_GUIDE / the sysml-conventions skill stencils when an item changes what models should look like.
- **Checking-script updates**: new or corrected validation checks (Level 2 / Level 6 / adr002 operator set) with a negative fixture for each, when an item changes what the auditor should catch.
- Each item's close-out notes carry an explicit "agentic-mbse impact" list (possibly "none"). Item 12 executes the accumulated list; genuinely urgent one-liners (e.g., the A-2 stencil fix) are done inline in the item that motivates them.

### R3 — Baseline and license discipline

- Baseline/snapshot regeneration goes through the capture scripts (`scripts/capture_*.py`) with reviewed diffs — never hand-edited baselines.
- The syside license (single-seat, machine-locked) **expires 2026-08-06** with no grace period. Items needing live extraction (fixture capture, baseline regen) must not be scheduled into that window unprotected; Item 2 (snapshot CLI) is itself the mitigation.

---

## Why This Epic?

**Current State**:
- One test fails on `main` (solar_battery YAML baseline, ordering-only diff), muddying every future change's signal.
- Legal SysML crashes generation (SC-2), silently drops modules (SC-3), or emits non-importable Python (SC-4).
- Constraints, derived-attribute names, and cross-part references vanish silently (SC-1, SC-7, SC-5); warning noise makes real failures look like noise and vice versa (SC-8) — the committed catf_mfe fixture ships a dangling input that fails at runtime.
- Generation requires a live syside license (SC-9/10) that expires 2026-08-06.
- fusion-tea works around all of this with post-processors, hand-fed inputs, and harness-side physics — and their MFE epic (all cross-part wiring) is gated on SC-5.
- The fixture corpus exercises none of the failing shapes, which is why 1,500+ tests caught none of this.

**Future State**:
- Test suite green; every finding either fixed, loudly diagnosed, or explicitly closed.
- The IFE model set generates correctly end-to-end: wired cross-part channels, pre-filled input JSONs, importable package — fusion-tea deletes `sanitize_names.py`, the two-pass gamma feedback, and the `hif_driver_instance` workaround.
- `--from-snapshot` decouples generation from the license.
- New fixtures (return-style, retyping, quoted names, plant idiom) lock every shape in.
- agentic-mbse teaches the correct patterns and its validators catch the traps before execution does.

---

## Success Criteria

- [ ] Full test suite passes on `main`, including the re-captured solar_battery YAML baseline
- [ ] fusion-tea IFE models generate an importable package with correct cross-part wiring (gamma → lcoe edge present in pipeline YAML) and pre-filled input JSONs — verified against the WI-015 anchor values
- [ ] No silent drops remain: constraints, derived-attribute names, dropped calc templates, and unresolved bindings all produce clear warnings or hard errors
- [ ] `sysml-codegen generate --from-snapshot` produces output matching live generation (byte-identical for solar_battery), including CalcUsage auto-implementation
- [ ] New conformance fixtures cover: return-style calc defs, bare `in` params, retyped part usages, quoted calc defs through full generation, the WI-014 toy, and an ife_plant-shaped model
- [ ] Every touched component's reference doc and verification-matrix rows are updated (R1)
- [ ] The accumulated agentic-mbse impact list is implemented or filed as agentic-mbse backlog items (R2), including the A-2 stencil fix
- [ ] SC-11 formally closed as "confirmed intended, documented, tested"

---

## Backlog Items

### Item 1: Baseline Repair & Silent-Failure Diagnostics [0.5–1 day]

**Type**: Implementation
**Effort**: 0.5–1 day (spec 1h, design 1h, plan 1h, execute 3–5h)
**Dependencies**: None — do first

**Objective**: Make the test suite green and convert the three worst silent failures into loud diagnostics, without changing generated output for valid models.

**Scope**:
1. **solar_battery YAML baseline repair**: re-capture via `scripts/capture_baseline_yaml.py` (requires live license); decide in spec whether to also order-normalize the comparison (or the generator's input ordering) so filesystem/discovery-order shifts can't redden the suite again. Research finding: the diff is a two-line ordering swap in `entry_fusion` inputs; content is identical; failure is deterministic and not hash-seed-dependent.
2. **SC-1 interim warning**: extraction/orchestration-time warning when constraint usages are found and dropped (summary WARN + per-item INFO — catf_mfe has dozens of benign inline constraints). Add a "constraints are not executable" section to `modeling-assumptions.md`.
3. **SC-7 warning upgrade**: reword the EXPOSE_PURE warnings (`graph_builder.py` and the Phase-3 registration site) to state plainly that the derived-attribute *name* is dropped and name the canonical channel where the value went.
4. **SC-2 zero-output fail-fast**: hard diagnostic when a calc def extracts with zero outputs, so no extraction gap can ever again crash inside a Jinja template.

**Out of Scope**:
- Constraint execution (future epic — see Deferred section)
- Actually extracting return-style outputs (Item 3) or surfacing aliases (Item 11)

**Success Criteria**:
- [ ] Full suite green on `main`
- [ ] Generating the WI-014 toy and IFE models emits the new constraint / EXPOSE_PURE / zero-output diagnostics
- [ ] No baseline changes beyond the re-captured YAML (valid models' output unchanged)
- [ ] agentic-mbse impact recorded (expected: endorse the A-1 constraint-WARN check)

**Deliverables**: `.project/active/baseline-diagnostics/{spec,design,plan}.md`, re-captured baseline, modeling-assumptions section

---

### Item 2: Snapshot-Driven Generation (SC-9 + SC-10) [1.5–2 days]

**Type**: Code/Integration
**Effort**: 1.5–2 days (spec 2h, design 2h, plan 1h, execute 8–11h)
**Dependencies**: None — parallel track; **schedule early: this is the mitigation for the 2026-08-06 license expiry**

**Objective**: A supported `--from-snapshot` generation path (plus snapshot capture command) so generation, debugging, and CI are decoupled from the syside license — with CalcUsage auto-implementation preserved.

**Scope**:
1. Promote `tests/helpers/snapshot_{loader,serializer}.py` to `src/sysml_codegen/snapshot/`; parameterize the fixtures-dir assumption.
2. `build_pipeline_context_from_snapshot()` in `orchestration/` (the proven conformance-helper body); `--from-snapshot` on `generate`, mutually exclusive with `--models`; reject `--design-path-filter` combined with it.
3. A `snapshot` capture subcommand (lifting `_capture_full_pipeline` from the script).
4. **Format versioning + provenance**: `snapshot_format_version` field with hard error on mismatch; source-hash freshness warning (hashes already in the snapshot); provenance banner on snapshot runs.
5. **SC-10**: serialize `compilation_results` (plain dataclasses of lowered Python expression strings) into the snapshot and thread them through the snapshot context builder. Never attempt syside AST serialization (live bridge objects). Old snapshots degrade to today's behavior with a warning.
6. Regenerate the 10 committed fixture snapshots to the versioned format.

**Out of Scope**:
- Snapshotting at the ComputationGraph level (rejected in research — freezes resolution logic)
- Any remote/licensing workaround beyond the snapshot path

**Success Criteria**:
- [x] `generate --from-snapshot` on the solar_battery snapshot is byte-identical to live generation
- [x] A snapshot of an expression-bearing model preserves CalcUsage auto-impl (stencils not NotImplementedError; `compilability` set)
- [x] Version-mismatched snapshot fails loudly; stale-source snapshot warns
- [x] Snapshot format documented (new reference doc or extension of doc 02)
- [x] agentic-mbse impact recorded (expected: none, or docs pointer)

**Deliverables**: `.project/active/snapshot-generation/{spec,design,plan}.md`, new `snapshot/` package, CLI additions, regenerated fixture snapshots

---

### Item 3: Return-Style & Bare-Parameter Extraction (SC-2) [1 day] ✅

**Type**: Implementation
**Effort**: 1 day (spec 1.5h, design 1.5h, plan 1h, execute 4–6h)
**Dependencies**: Item 1 (zero-output guard in place)

**Objective**: Legal calc-def parameter styles (`return x : Real = expr`, bare `in x : Real`) extract correctly instead of vanishing; the one genuinely unsupportable form (anonymous `return`) is rejected with a clear diagnostic.

**Scope**:
1. Relax the member-type filter (`extractor.py`, both passes) to accept direction-carrying ReferenceUsage members; verify no double-ingestion for the `return attribute` + body-assignment form (two members share a name; direction-None ReferenceUsages stay excluded from attribute lists).
2. Diagnostic for anonymous `return : Real = expr` (no name → no PQN channel; V1–V6-style message naming the fix).
3. New fixture (all four parameter styles) + extraction snapshot + conformance tests.
4. Reconcile the docs the code contradicted: `docs/architecture/reference/01-extraction.md` (its canonical example is currently false).
5. **agentic-mbse inline**: fix the sysml-conventions skill calc-def stencil (A-2 — currently teaches the degraded form); record the Level-6 output-style check for Item 12.
6. Spec-time decision (do not pre-commit): whether body-assignment expression capture (restores auto-impl for the stencil form) is in scope here or recorded as a follow-up.

**Out of Scope**:
- Multi-output `return` (not legal SysML — one result parameter max)

**Success Criteria**:
- [x] All named parameter styles extract with correct inputs/outputs; existing baselines unchanged
- [x] Anonymous return produces the diagnostic, not a crash
- [x] The six converted IFE calc defs work in original `return` form (verify against fusion-tea models) — satisfied by design: the four-styles fixture covers the same inline-return shape; spec-review established all six were inline `return` (fusion-tea `8852afcf`). Live IFE re-run demoted to opportunistic (D6).
- [x] Skill stencil fixed; agentic-mbse impact recorded — impact recorded in spec; A-2 edit committed at agentic-mbse 6dbdf1b per plan, **not read directly (sandbox-blocked); Item 12 re-verifies.**

**Deliverables**: `.project/active/return-style-extraction/{spec,design,plan}.md`, new fixture + snapshot, doc fix, stencil fix

**Audit (2026-07-05, commit 559a0bb):** PASS / Certify — `.project/active/return-style-extraction/audit.md`. Two non-blocking verification limits: tests not re-run (harness approval unavailable; green rests on recorded gate + direct snapshot/code inspection); A-2 not read directly (agentic-mbse outside session sandbox), re-verified by Item 12.

---

### Item 4: Part-Usage Type Indexing (SC-3) [1 day] ✅

**Type**: Implementation
**Effort**: 1 day (spec 1.5h, design 1.5h, plan 1h, execute 4–6h)
**Dependencies**: None (parallel with Items 3, 5, 6)

**Objective**: Retyped part usages (`part :>> x : Subtype`) instantiate their subtype's template calcs instead of silently dropping them — fixing both occurrences of the first-type bug.

**Scope**:
1. Fix `_build_part_usage_index` (`usage_extractor.py`): index each usage under its **owned FeatureTyping target plus every user-model PartDefinition in `usage.types`** (preserves accidental supertype-template flow while adding the subtype's), filtered to user packages. Mechanism precedent: `_get_calc_def_name`'s heritage walk.
2. Fix the same pattern in `extract_hierarchy_data` (`hierarchy_resolver.py:526-533`) — prefer the FeatureTyping target for `usage_type_map`.
3. Virtual-QN collision tiebreak (most-specific owner) or at minimum a warning, for the inherited-template-with-redefined-calc case.
4. Retyping fixture + snapshot + conformance tests; confirm the 4 pipeline baselines unchanged.
5. agentic-mbse impact: document retyping as a supported pattern (MODELING_GUIDE); record the "part def with calcs but no instantiation" Level-6 check (A-1 row 4) for Item 12.

**Out of Scope**:
- Inherited templates reaching *plain* subtype-typed usages (needs a supertype-chain walk; record as a note for the MFE epic, not this item)

**Success Criteria**:
- [x] `part :>> driver : 'HIF Driver'` instantiates HIF-owned template calcs (verified on fusion-tea models or the new fixture)
- [x] Existing baselines byte-identical
- [x] Collision case covered by a test (warning or deterministic tiebreak)
- [x] agentic-mbse impact recorded

**Deliverables**: `.project/active/type-indexing/{spec,design,plan}.md`, retyping fixture, doc updates (doc 25, modeling-assumptions §5)

---

### Item 5: Identifier Sanitization (SC-4, + SC-11 riders) [1 day] ✅

**Type**: Implementation
**Effort**: 1 day (spec 1.5h, design 1.5h, plan 1h, execute 4–6h)
**Dependencies**: None (parallel with Items 3, 4, 6)

**Objective**: Quoted SysML names produce valid, internally consistent Python everywhere — closing the gap between the documented naming contract (REQ-NC-06) and the derivation layer that skips it.

**Scope**:
1. Apply `sanitize_name` at the source (`extractor.py` qualified-name capture and `owning_part_qualified_name` producers) — spec-time fallback: the derivation layer (`identifier_types.py`) if source-sanitization hits a raw-QN comparison (one known site to check: `dependency_backtracker.py:663`). Either way, the FORMULA `module_eqn` path (`sysml_to_python_qualified_name`) must be covered.
2. Fail-fast duplicate-output-path check (two names sanitizing to the same filename currently overwrite silently).
3. Conformance test: full registry/module generation from `alias_agg_probe` (fixture exists, never flowed through generation tests); assert `ast.parse` passes and imported names match declared classes.
4. SC-11 riders (optional, spec-time call): post-alias uniqueness re-check and AST-based import rewrite in `_resolve_class_name_collisions`. **SC-11 itself is closed by this epic as intended/tested — record that in the close-out.**
5. agentic-mbse impact: naming guidance ("quoted names are fine; identifiers are derived"), plus a validation warning candidate for two names sanitizing to one identifier. Note for fusion-tea: `sanitize_names.py` becomes dead — flag for coordinated retirement (their names may shift subtly).

**Out of Scope**:
- Banning quoted names (contradicts fixtures, docs, and REQ-NC-06)
- Channel-name changes (PQN path is already sanitized — verify, don't touch)

**Success Criteria**:
- [x] `alias_agg_probe` generates an importable package; quoted-name leak reproduction from the research is gone
- [x] All existing baselines byte-identical (no baseline model has a quoted calc def)
- [x] Duplicate-path collision fails fast with a clear message
- [x] agentic-mbse impact + fusion-tea coordination note recorded

**Audited PASS / Certify** (2026-07-05, commit 4b19e4d) — see `.project/active/identifier-sanitization/audit.md`. Suite gate (1880/21/109) rests on recorded evidence; auditor harness-blocked from re-running `uv run`.

**Deliverables**: `.project/active/identifier-sanitization/{spec,design,plan}.md`, conformance tests, doc 15/20 updates

---

### Item 6: Expression Reconstruction Fidelity (SC-6) [0.5–1 day]

**Type**: Implementation
**Effort**: 0.5–1 day (spec 1h, design 1h, plan 0.5h, execute 3–5h)
**Dependencies**: None — **must land before the PUSH-DOWN epic moves `expression_utils.py`** so the pushed-down code is born correct

**Objective**: Docstrings and stencil expression text show faithful math — literals render as values, parenthesization is preserved.

**Scope**:
1. Reorder `reconstruct_expression`: literal branches (incl. LiteralBoolean/LiteralString/NullExpression) above the invocation catch-all; switch literal detection to `SysideAdapter.is_instance` (consistent with `is_literal_expression`).
2. Precedence-aware parenthesization in `reconstruct_operator_expression` (chosen over always-paren to minimize baseline text churn — confirm at design).
3. Regression test against a *real* parsed fixture AST (mocks masked this bug).
4. Regenerate baselines (173 `LiteralRationalEvaluation` occurrences across 12 files; capture scripts; requires license — mind R3).
5. agentic-mbse impact: note in the PUSH-DOWN design that the fix travels with the move.

**Out of Scope**:
- Replacing the reconstructor with the expression compiler's renderer (rejected in research: compiler is Python-flavored and deliberately narrower; the reconstructor also serves constraint text and aggregation fallback)

**Success Criteria**:
- [ ] The research repro (`capacity * rate + capacity * (rate / 2.0) * 3.0`) renders faithfully in docstrings/stencils
- [ ] Zero `LiteralRationalEvaluation` strings in regenerated snapshots/baselines
- [ ] Executable bodies unchanged (they were always correct)

**Deliverables**: `.project/active/expression-fidelity/{spec,design,plan}.md`, regenerated baselines, real-AST regression test

---

### Item 7: Resolution Matcher Fixes & Warning Reconciliation (SC-8) [1.5–2 days]

**Type**: Implementation
**Effort**: 1.5–2 days (spec 2h, design 2h, plan 1h, execute 8–11h)
**Dependencies**: Item 5 (shared sanitized-QN matching helper), Item 1 (diagnostic wording conventions)

**Objective**: Warnings mean something — benign first-pass misses resolve correctly at the right stage, and genuinely unresolved-and-uncovered inputs fail loudly and precisely.

**Scope**:
1. Fix the two matcher bugs behind the benign "Registry unresolved" noise: per-segment-sanitizing QN conversion (REFERENCE path — reuse Item 5's helper), and usage-name-aware / QN-suffix matching for part-def-owned design attributes (empty `parent_part`). **This is behavioral**: entry points reclassify (USAGE_LITERAL → DESIGN_ATTRIBUTE) and Step-3 dedup returns (shared keys collapse) — baselines and params-JSON key sets will churn; review deliberately, note in release notes.
2. Demote per-binding Step-4 fallback warnings to DEBUG; add a post-assembly reconciliation summary of entry points that fell through AND still lack a value.
3. **Params-coverage hard check**: any module input referencing `*_params.X` with no matching key in any parameter group is an error (precedent: `_validate_channel_references`). This must catch the committed catf_mfe dangling `magnet_volume` input — fix or explicitly xfail that fixture as part of this item.
4. Count-summary treatment for the repetitive alias-collision warnings (25 of catf_mfe's 29 warning lines).
5. agentic-mbse impact recorded (expected: minor or none).

**Out of Scope**:
- Resolving the *cross-part* unresolved cases (Items 9–10 — the coverage check keeps them loud in the meantime)

**Success Criteria**:
- [ ] Clean fixture models generate with zero WARNING lines; the catf_mfe dangling input is a hard, precise error (then fixed/xfailed)
- [ ] Reclassification/dedup changes reviewed and captured in regenerated baselines
- [ ] A seeded unresolved-binding fixture proves the coverage check fires

**Deliverables**: `.project/active/warning-reconciliation/{spec,design,plan}.md`, matcher fixes, coverage check, regenerated baselines

---

### Item 8: Plant-Idiom Conformance Fixtures [0.5–1 day]

**Type**: Modeling / Testing
**Effort**: 0.5–1 day (spec 1h, design 0.5h, plan 0.5h, execute 3–5h)
**Dependencies**: None hard; **requires live license (R3)** — schedule before 2026-08-06 or after renewal

**Objective**: Close the fixture blind spot for the plant idiom before SC-5 work begins — the "0 cross-part refs found in fixtures" evidence base must never justify a deferral again.

**Scope**:
1. Import the fusion-tea WI-014 toy (`exploration/construct_validation/`) as a conformance fixture (covers part-def EXPOSE_PURE and REFERENCE-binding warning paths).
2. Author an ife_plant-shaped fixture: generic plant part def with def-declared attributes, `:>>`-valued specialized subsystem defs, retyped nested parts, cross-part calc-chain bindings, plain-usage `:>>` overrides, and one self-named-binding trap (as a negative/diagnostic case).
3. Capture extraction snapshots; capture *current* (known-incomplete) pipeline baselines so Items 9–10 show their progress as reviewed baseline diffs.
4. agentic-mbse impact: the fixture shapes become the reference examples for MODELING_GUIDE plant-idiom guidance (executed in Item 12, once Items 9–10 define what's supported).

**Out of Scope**:
- Any production-code change (fixtures and captures only)

**Success Criteria**:
- [ ] Both fixtures load, snapshot, and run through the pipeline without crashing (incomplete output is expected and captured)
- [ ] Fixture models pass agentic-mbse validation (or failures are understood and recorded)

**Deliverables**: `.project/active/plant-fixtures/{spec,plan}.md`, two fixtures + snapshots + baselines

---

### Item 9: Plant-Idiom Literal Pre-Fill (SC-5 stage 1) [1–1.5 days]

**Type**: Implementation
**Effort**: 1–1.5 days (spec 1.5h, design 2h, plan 1h, execute 5–8h)
**Dependencies**: Item 8 (fixtures)

**Objective**: Literal values reach the generated input JSONs for plant-idiom models — `:>>` overrides on plain part usages are captured, and def-attribute literals pre-fill CalcUsage entry points.

**Scope**:
1. Capture `:>>` overrides on plain part usages (the `owned_redefinitions` guard in `hierarchy_resolver.py`) — also rescues self-named bindings via the leaf-match rewrite.
2. Propagate `RedefinitionData` literals to CalcUsage entry-point defaults (mirror of REQ-LVP, which exists for aggregations only).
3. **Fix the shared-mutable-`BindingInfo` latent bug** (`usage_extractor.py` — virtual instances share binding objects; deep-copy) — a hard precondition for Item 10's per-instance rewriting; safe and cheap to land here.
4. Regenerate plant-fixture baselines; verify IFE input JSONs pre-fill (availability, efficiency, etc. — the ~14 Hawker parameters).
5. agentic-mbse impact recorded.

**Out of Scope**:
- Channel wiring across parts (Item 10)

**Success Criteria**:
- [ ] Fresh IFE generation pre-fills the plant/driver input JSONs (against WI-015 evidence: previously 2/16 and 0 keys)
- [ ] Existing 4 baselines unchanged; plant-fixture baseline diffs reviewed
- [ ] BindingInfo aliasing covered by a regression test

**Deliverables**: `.project/active/plant-prefill/{spec,design,plan}.md`

---

### Item 10: Cross-Part Channel Wiring (SC-5 stage 2) [2 days — may split at design]

**Type**: Implementation
**Effort**: 2 days (spec 2h, design 3h, plan 1h, execute 10–12h) — **the riskiest item; the design phase should explicitly decide whether to split**
**Dependencies**: Items 4 (retype indexing), 8, 9

**Objective**: Cross-part calc-output bindings become real channel wiring — the gamma → lcoe edge appears in generated pipeline YAML, ending fusion-tea's two-pass harness feedback.

**Scope**:
1. Consumer-scoped alias lookup step in the backtracker's CHAIN dispatch (additive; ordered before the existing unscoped step; update REQ-BT-08 and docs 11/24).
2. Per-instance binding rewrite through the specialization chain (usage override > specialized-def `:>>` > base def), building on Items 4 and 9 — the genuinely novel machinery; keep every new registry key consumer-scope-prefixed and unique by construction.
3. PartDef-level EXPOSE_PURE with instance-scoped alias keys (revises REQ-CA-03; also fixes SC-7's shape-A resolution path).
4. Verify against WI-015 anchors: run C's lcoe from generated wiring alone matches the harness-fed result.
5. agentic-mbse impact: this item defines the supported plant-idiom shapes — record the MODELING_GUIDE content and any new validation checks for Item 12. Coordination note for fusion-tea: channel names move (e.g., gamma's EQN); `hif_driver_instance` workaround becomes deletable.

**Out of Scope**:
- Alias *emission* into generated output (Item 11)
- Supertype-chain template inheritance (MFE-epic note from Item 4)

**Success Criteria** (audited 2026-07-06, commit `0c4b921` — verdict CONDITIONAL, see `active/cross-part-wiring/audit.md`):
- [~] gamma → lcoe edge present in generated YAML; IFE anchors reproduce end-to-end without harness wiring
  — **AUDIT: met at the GRAPH level only.** The gamma→lcoe edge is present in the fusion-tea
  ComputationGraph from generated wiring alone (`hif_plant__lcoe_calc` input `driver_cost_constant` →
  `hif_plant_pkg__hif_plant__driver__meier_cost__gamma`; left the V11 offender list 11→10). The full YAML
  does NOT emit (aborts at V11 on 10 other cross-part bindings — `driver.efficiency`, `chamber.*`,
  `target_factory.*`, `hif_driver_instance` — pre-existing, out of Item 10 scope), and run-C $270.12/MWh
  stays recorded-not-reproduced (fusion-tea harness only). fusion-tea workarounds stay upstream. Tracked as
  BACKLOG P1 (`BACKLOG.md:104`).
- [~] Existing 4 baselines unchanged (or diffs reviewed and justified) — catf regenerated + reviewed; the
  **ife_plant graph baseline is stale/unreviewed** (audit Finding 2 — regen or remove before close).
- [x] Instance-ambiguity case (two same-type sibling parts) covered by a test —
  `test_sibling_channel_ambiguity.py` pins the consumer to `...chamber_b__power_calc__power` (≠ chamber_a).

**Deliverables**: `.project/active/cross-part-wiring/{spec,design,plan}.md`, docs 10/11/24/25 updates

---

### Item 11: Derived-Attribute Alias Surfacing (SC-7) [1–1.5 days] ✅

**Type**: Implementation
**Effort**: 1–1.5 days (spec 1.5h, design 2h, plan 1h, execute 5–7h)
**Dependencies**: Item 10 (shape-A resolution machinery; ComputationGraph rev discipline)

**Objective**: The modeler's chosen name (`total_cost`) appears in generated output as a named alias of the canonical channel, for both part-usage and part-def shapes.

**Scope**:
1. Graph-level alias field (`output_aliases` or equivalent) populated from the typed alias registrations — **a deliberate ComputationGraph schema rev** (R1).
2. Exit-point rendering of alias captures in pipeline YAML, with instance qualification to avoid collisions.
3. Conformance coverage for both shapes (the WI-014 toy from Item 8 covers shape A).
4. agentic-mbse impact: EXPOSE-pattern docs updated to describe what the name now does downstream.

**Out of Scope**:
- EXPOSE_COMPUTED (calc output + arithmetic — remains rejected per modeling-assumptions §3)

**Success Criteria** (audited 2026-07-06, commit `4f6ba40`+`0672cae` — verdict PASS/Certify, see `active/alias-surfacing/audit.md`):
- [x] `total_cost`-style names appear in generated YAML/outputs wired to the correct channel, both shapes
  — verified in committed baselines: wi014_toy shape A (`total_cost`), attr_expr_probe shape B
  (`scale_result`/`half_vol`/`quarter_vol`), solar_battery shape A (`misc_hardware_cost`).
- [x] Schema rev documented (doc 09) with REQ tags and verification-matrix rows
  — REQ-DM-09/PY-08/CA-11 in doc 09/16/21 + matrix (counts reconciled 233/221/12).

**Deliverables**: `.project/active/alias-surfacing/{spec,design,plan}.md`

---

### Item 12: agentic-mbse Sync — Guidance & Validation [1–1.5 days, in agentic-mbse]

**Type**: Code/Integration + Documentation (agentic-mbse repo)
**Effort**: 1–1.5 days (spec 1.5h, plan 1h, execute 5–8h)
**Dependencies**: All prior items' recorded impact lists (final item)

**Objective**: agentic-mbse's teaching and checking surfaces match what sysml-codegen now supports — the validated-subset contract is enforceable again.

**Scope**:
1. Execute the accumulated per-item impact lists (R2). Expected floor, from the register's A-1 gap matrix plus this epic's outcomes:
   - Level 2: self-named-binding check (FAIL)
   - Level 6: return-style vs out-attribute output check (updated for Item 3's newly legal forms); constraint non-executability WARN; calc-bearing part def with no instantiation (FAIL, updated for Item 4's retyping support)
   - adr002 operator set corrections (`**` status; function-invocation detection → WARN)
   - Negative fixture for every new check
2. MODELING_GUIDE / sysml-conventions updates: plant-idiom patterns (from Items 9–10), retyping (Item 4), quoted-name guidance (Item 5), the no-loops rule (register A-3 — pure documentation).
3. Verify the A-2 stencil fix landed (Item 3) and nothing else in the skill teaches a broken pattern.
4. File anything out of scope as agentic-mbse backlog items rather than dropping it.

**Out of Scope**:
- The syside vendor report for self-named-binding recursion (register A-1 vendor note — file separately with Sensmetry if desired)

**Success Criteria**:
- [ ] Every impact list item implemented or filed; none silently dropped
- [ ] Each new validation check has a negative fixture and catches its trap on the WI-014 toy / plant fixture shapes
- [ ] fusion-tea's RAW_LEARNINGS traps are covered by checks or documented rules (traceability table in the close-out)

**Deliverables**: agentic-mbse `.project/active/validation-sync/{spec,plan}.md`, checks + fixtures, guide updates

---

## Deferred (explicitly not in this epic)

- **SC-1 full constraint execution** — its own future epic: part-level `assert constraint` typed by constraint defs, compiled to boolean-output modules, annotate-don't-halt (needs an ADR). Item 1's warning removes the silence; demand should be re-weighed after the MFE epic. Delete `constraints.py` / `constraint_validator.py.jinja2` as dead code when that epic starts (or opportunistically in Item 1).
- **Supertype-chain template inheritance** for plain subtype usages — note carried to the MFE epic (Item 4).
- **EXPOSE_COMPUTED**, non-uniform arrays, function-call/conditional support — pre-existing backlog ideas, unchanged by this epic.

---

## Dependencies

**External**:
- syside license (expires **2026-08-06**; single-seat, machine-locked) — gates Items 1, 6, 8 capture work and all baseline regens; Item 2 is the mitigation
- fusion-tea coordination: channel renames (Item 10), `sanitize_names.py` retirement (Item 5), `hif_driver_instance` deletion (Item 10), harness two-pass removal (Item 10)
- PUSH-DOWN epic (P1, design ready): Item 6 must land first

**Internal**: none beyond item ordering below.

**Item Dependency Graph**:
```
Track A (hardening)                       Track B (parallel)
Item 1 (baseline + diagnostics)           Item 2 (snapshot CLI — early, license deadline)
  ├─> Item 3 (SC-2 return-style)          Item 8 (plant fixtures — needs license)
  ├─> Item 4 (SC-3 type indexing) ────┐     └─> Item 9 (SC-5 pre-fill)
  ├─> Item 5 (SC-4 sanitization)      │           └─> Item 10 (SC-5 wiring) ←─ also needs Item 4
  │     └─> Item 7 (SC-8 matchers)    │                 └─> Item 11 (SC-7 surfacing)
  └─> Item 6 (SC-6 reconstruction)    │
                                      │
Item 12 (agentic-mbse sync) ← accumulates from ALL items; executes last
```

---

## Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| syside license expires 2026-08-06 mid-epic | High | Item 2 early; front-load all capture/regen work (Items 1, 6, 8); renewal request to Sensmetry now |
| Item 10 (specialization-chain rewrite) exceeds 2 days | Med | Design phase explicitly decides split; Items 8–9 land value independently; staged baselines show progress |
| Behavioral changes (Item 7 dedup/reclassification, Item 5 names for quoted models) surprise downstream consumers | Med | Release notes per item; fusion-tea coordination notes are success criteria, not afterthoughts |
| ComputationGraph schema revs (Item 11) erode the generation boundary | Med | R1: deliberate rev process, REQ tags, doc 09 update, conformance field-set tests |
| Baseline churn masks a real regression during mass regen (Items 6, 7) | Med | One item's regen at a time; reviewed diffs; capture scripts only (R3) |
| Fixture blind spot recurs for newly supported shapes | Med | R1: no new behavior without a real fixture; Item 8 before Items 9–11 |
| agentic-mbse drift (checks lag what codegen accepts) | Med | R2 per-item impact lists; Item 12 gate at epic close; traceability table |

---

## Timeline

**Total Effort**: ~13–16 days

| Item | Effort | Dependencies |
|------|--------|--------------|
| 1. Baseline repair & diagnostics | 0.5–1 d | None (first) |
| 2. Snapshot-driven generation | 1.5–2 d | None (parallel, early) |
| 3. Return-style extraction | 1 d | Item 1 |
| 4. Type indexing | 1 d | None |
| 5. Identifier sanitization | 1 d | None |
| 6. Expression reconstruction | 0.5–1 d | None (before PUSH-DOWN) |
| 7. Matcher fixes & reconciliation | 1.5–2 d | Items 1, 5 |
| 8. Plant-idiom fixtures | 0.5–1 d | None (license window) |
| 9. Plant literal pre-fill | 1–1.5 d | Item 8 |
| 10. Cross-part wiring | 2 d | Items 4, 8, 9 |
| 11. Alias surfacing | 1–1.5 d | Item 10 |
| 12. agentic-mbse sync | 1–1.5 d | All (last) |

---

## Source Documents

- `~/1cfe/fusion-tea/.project/reports/2026-07-05-upstream-findings-register.md` (findings register — evidence, manifestation, workarounds)
- `.project/research/20260705_upstream-findings-deep-research.md` (deep research — verification, corrected root causes, fit/lift/risk)
- `docs/architecture/modeling-assumptions.md` (supported-subset contract)
- `docs/architecture/overview.md` + `docs/architecture/reference/` (design patterns to maintain — R1)

---

## Lessons Learned (Post-Completion)

*Fill in after epic is complete*

**What Went Well**: TBD
**What Could Improve**: TBD
**Surprises**: TBD

---

**Last Updated**: 2026-07-05
**Next Action**: User review of scope and decomposition; then spec Item 1
