# Current Work

**Last Updated**: 2026-07-06

---

## Active Work

### UPSTREAM-FINDINGS Item 12: agentic-mbse Sync — Guidance & Validation

**Status**: **COMPLETE** (2026-07-06). Close-out: `.project/active/validation-sync/close-out.md`
(two traceability tables — every impact row and every fusion-tea trap dispositioned).
Executed in `~/1cfe/agentic-mbse` (branch `upstream-findings-sync`), four commits
`9db5ede`→`08cd595`. This is the epic's final item — the validated-subset contract is
enforceable again.

**What landed (agentic-mbse):**
- **Checks (BUILT):** C1 self-named-binding FAIL (L2), C2a anonymous-return FAIL (L6), C2b
  body-assignment WARN (L6), C3 constraint WARN (L6), C4 calc-bearing-no-instantiation FAIL
  (L6), C5 operator-set correction (`^` dropped) + function-invocation WARN, C6 L6
  false-positive corrections (calc-def-internal derived expr + quoted names). Each with a
  negative fixture + negative-of-the-negative under `tests/fixtures/item12/`.
- **Checks (FILED):** C7 (attribute-`:>>`-expr WARN), C8 (two-names-one-identifier WARN) —
  agentic-mbse backlog `ITEM-SYNC-C7/C8`, reasons logged (guard).
- **Docs (BUILT):** D1–D8 — new `docs/patterns/plant-idiom.md` (plant idiom, retyping,
  def-owned attrs), quoted-names, no-loops, bare-`:>>`, EXPOSE surfacing, constraint pointer.
  V1 confirmed (A-2 stencil), V2 sweep found nothing else stale.
- **Filings:** F1 (syside vendor note — evaluation-time-not-extraction-time — + draft),
  F2 agentic-mbse; F3/F4/F5 in this repo's `.project/backlog/BACKLOG.md` (`SYNC-F3/4/5`).

**Acceptance gates (both green):** agentic-mbse suite 1218 passed / 1 skipped (ruff clean,
mypy 0 new); run_all_checks over the sysml-codegen corpus — three plant fixtures PASS L1–L5
(no regression), the real `self_named_binding_trap` L6 now PASSES (C6), all Item-12 L6
changes are the designed ones.

**Key deviation (C1 reframed per orchestrator ruling):** C1 FAILs only a *dead-end*
self-named binding (owner carries no covering feature, owned or inherited). The old
`self_named_binding_trap` fixture — which carries a covering attribute — is now the SUPPORTED
plant idiom (Items 9/10) and became C1's negative-of-the-negative; the new negative is
`item12/self_named_deadend`. One-line codegen-spec amendment recorded in close-out.md.

**Nothing committed in sysml-codegen** (per orchestration): F3/F4/F5, close-out, plan/spec
status, and this note are written here, not committed.

### UPSTREAM-FINDINGS Item 11: Derived-Attribute Alias Surfacing (SC-7)

**Status**: **AUDITED — PASS/Certify** (2026-07-06, commits `4f6ba40`+`0672cae`;
audit: `.project/active/alias-surfacing/audit.md`). All 5 phases landed and certified;
all 10 spec success criteria verified against committed baselines/YAML/tests (no mocks).
Three non-blocking observations (INV-6 positive-warning coverage gap; documented shape-B
leaf-collision edge; inherited catf first-wins collapse) — none gate close. Gate
1989/4/5, ruff 21, mypy 109 rests on the recorded value + static inspection (`uv run`
approval-gated this session). Ready for `/_my_pre_pr` → `/_my_close`. Surfaces
Item 10's typed EXPOSE_PURE alias registrations into a new serialized `output_aliases`
ComputationGraph field + named exit-point captures in pipeline YAML, both shapes
(wi014_toy shape A `total_cost`, attr_expr_probe shape B `scale_result`/`half_vol`/
`quarter_vol`). Retires Item 1's shape-A malformed-refs warning for resolvable cases.
Scope pinned: EXPOSE_PURE only (redefinition-name surfacing is a BACKLOG non-goal).
- **5 populated graph baselines:** attr_expr_probe (3), solar_battery (1, shape-A
  `misc_hardware_cost` — the spec's "no EXPOSE_PURE" §1 label was wrong; snapshot
  recaptured under the approved SC-1 reconciliation), wi014_toy (1), ife_plant (2),
  catf_mfe (44 entries / 19 channels, first-wins collapse).
- **Filename MOVE (downstream coordination):** aliased channels' output files move
  `{channel}.json → {instance}__{alias}.json` — committed YAML: attr_expr_probe ×3,
  solar_battery ×1, new wi014_toy baseline ×1. See
  `.project/active/alias-surfacing/release-notes.md`.
- **Gate:** 1989 passed / 4 skipped / 5 xfailed; ruff src/ 21; mypy src/ 109.
- **Docs:** REQ-DM-09 / REQ-PY-08 / REQ-CA-11 (docs 09/16/21, modeling-assumptions §3,
  verification-matrix). Ready for `/_my_audit` → `/_my_pre_pr`.

### UPSTREAM-FINDINGS Item 10: Cross-Part Channel Wiring (SC-5 stage 2)

**Status**: **AUDITED — CONDITIONAL** (2026-07-06, commit `0c4b921`; audit:
`.project/active/cross-part-wiring/audit.md`). All phases landed and green (Phase 8 C-then-B STEP 1+2
succeeded), committed across four commits (`5ea0a6a`→`0c4b921`). **Gate: 1962 passed / 4 skipped / 5
xfailed; ruff src/ 21; mypy src/ 109** (recorded; `uv run` approval-gated this session, so green rests on
the recorded gate + static code/snapshot/baseline inspection). Substance certified; production code sound
for all six mechanisms; INV-F/INV-G/D-C verified; 5 of 6 mechanisms channel-identity-pinned.

**Two test/fixture fixes required before `/_my_close` (no production change):**
1. **ife_plant channel-identity gap (Finding 1)** — the flagship multi-hop-EXPOSE mechanism's
   direct-calc-output shape is only pinned by `EXPECTED_UNCOVERED == set()`, the exact insufficient signal
   the D-C find flagged. Add an `offline_input_sources("ife_plant")` assertion pinning `magnet_volume` →
   `...tf_coil__volume_calc__volume` (license-free; catf's alias-terminal shape is already baseline-pinned).
2. **Stale ife baseline (Finding 2)** — `baseline_outputs/ife_plant/computation_graph.json` still shows
   `magnet_volume` as `entry_point`/null (not regenerated), inconsistent with the recaptured snapshot;
   regenerate + add `test_baseline_comparison_ife_plant`, or remove it. The plan's "ife baseline needed no
   regen" note is false — its structure did change.

**SC-2 honest status (unchanged, truthful in all docs):** gamma→lcoe edge present in the fusion-tea
ComputationGraph from generated wiring alone; the full YAML still aborts at V11 on 10 OTHER cross-part
bindings (Items 9-11 scope, pre-existing); run-C $270.12/MWh recorded-not-reproduced. BACKLOG P1 filed.

**Phase 8 STEP 1+2 done (2026-07-06, the ruling's (B) branch):** authored the two-level fixture
`spec_chain_twolevel` matching the REAL fusion-tea `hif_plant` shape — consumer `lcoe_calc` on the
BASE def, `part :>> driver : 'HIF Driver'` retype on a part USAGE (the prior session's fixture
wrongly used a `'HIF Plant'` DEF, masking the gap). Two-seam fix under the cap:
- **Extraction (REQ-LVP-09):** `_index_usage_level_retypes` (`hierarchy_resolver.py`) indexes the
  usage-level retype into `usage_type_map` keyed by the container instance QN, filtered to genuine
  retypes (target ≠ base-declared type) — verified blast radius = exactly `spec_chain_twolevel`,
  every other snapshot byte-identical.
- **Resolver (REQ-VBR-11):** instance-aware type-select in `_rewrite_specialized_chain`
  (`pipeline_builder.py`) tries the consumer instance-path key before the declaring-def key.

**SC-2 confirmed on the REAL fusion-tea model:** `generate --models ~/1cfe/fusion-tea/models` now
wires `hif_plant__lcoe_calc` input `driver_cost_constant` = `module_output` →
`hif_plant_pkg__hif_plant__driver__meier_cost__gamma` (the gamma → lcoe edge). `driver_cost_constant`
LEFT the V11 offender list (count 11 → 10, no regression). YAML gating (honest): the full model still
aborts at V11 on 10 OTHER cross-part bindings (`driver.efficiency`, `chamber.*`, `target_factory.*`,
`hif_driver_instance`) — broader Items 9-11 scope, pre-existing, out of Item 10. So the gamma edge is
confirmed in the ComputationGraph (the YAML's source of truth), not a written YAML. Run-C lcoe
$270.12/MWh stays recorded-not-reproduced (fusion-tea harness only). fusion-tea workarounds
(`hif_driver_instance` + two-pass gamma feedback) STAY upstream until the other 10 resolve
(BACKLOG P1 follow-up).

**Note on the "V12/V13" from the design:** reframed as REQ coverage (REQ-CA-10 multi-hop EXPOSE;
REQ-LVP-09/REQ-VBR-11 specialization chain) rather than new diagnostic V-codes — the mechanisms are
positive resolution, not new abort diagnostics, so inventing V-codes would be fictional.

**Phases 0–7 (prior sessions, all green):** Phase 0 probe battery (2 absorbable deviations D-A/D-B);
Phase 1 (D9 `reference_chain` capture); Phase 2 (`EXPOSE_CHAIN_TENTATIVE` tag, INV-E); Phase 3
(confirm pass — both V11 pins flip live; INV-F/INV-G); Phase 4 (part-def EXPOSE `_scoped_alias`
#4/#1, wi014 shape-A, REQ-CA-09 discharged); Phase 5 (recapture catf+ife + D-C offline==live parity
fix); Phase 6 (3 stage-(b) fixtures captured incomplete-first); Phase 7 (3 stage-(b) mechanisms:
D-D backtracker prepend, D-E self-named rescue, b1 specialized-def resolver).

**Deliverables (Phase 8):** `spec_chain_twolevel` fixture + snapshot + `test_spec_chain_twolevel.py`
(6 pins); `_index_usage_level_retypes` + instance-aware type-select; verification-matrix rows
(REQ-BT-11, REQ-CA-10, REQ-VBR-10/11, REQ-LVP-09; REQ-CA-03/09 revised); release notes
(`.project/active/cross-part-wiring/release-notes.md`); BACKLOG P1 follow-up; reference docs
11/24/25/16/12 updated. Real fixtures, no mocks; no commits.

### UPSTREAM-FINDINGS Item 9: Plant-Idiom Literal Pre-Fill (SC-5 stage 1)

**Status**: **Audited CONDITIONAL** (2026-07-05, commit `5140432`) — substance fully
verified by static trace against the commit; clears to PASS on two items. **Audit:**
`.project/active/plant-prefill/audit.md`.

Verified static: the three one-function edits match the design exactly (guard relax +
`_keep_plain_usage_override` LITERAL filter; bare-name raise → DEBUG-skip; `copy.copy` per
`BindingInfo`); the CHAIN/EXPRESSION exclusion (catf_mfe counter-case → byte-identical,
stays V11-pinned); the four snapshot deltas' semantic content; file-level INV-5 (exactly
four snapshots changed, no `baseline_outputs/` churn); every pin flip + the two V11
re-anchors (catf_mfe strict raise, ife_plant shape-4 strict abort); the divergent-sibling
regression test genuinely catches the shared-object bug (traced the key match — without
`copy.copy` iB reads 50.0 and `==100.0` fails); docs 12/25, matrix +3 rows, BACKLOG chore
(names the quoted_owner_formula reclassification question), release-notes, agentic-mbse
impact.

**Two conditions to clear to PASS:**
1. **Gate re-run** — `uv run pytest tests/` / `mypy` / `ruff` (expect 1932/4/11; 109; 21).
   Auditor was `uv run`-blocked (same block as Items 1/2/6/7/8). Two re-anchors are
   static-only: ife_plant must trip **strict** V11 at generation, and ife_plant
   `baseline_outputs` byte-identity — both confirmed by the run.
2. **ife_plant snapshot path-drift** — the committed ife_plant snapshot absorbed ~90 lines
   of environmental path canonicalization (source_file relativized on calc_defs AND
   calc_usages, design_attributes keys → absolute, document_path → `file:///`), the same
   drift class *reverted* on three other fixtures. Breaks no test, but makes the
   release-notes "calc_usages unchanged / every other snapshot byte-identical" claim
   inaccurate for ife_plant. Strip it, or amend release-notes + BACKLOG to record the
   migration. Depends on Item 8 fixtures.

### UPSTREAM-FINDINGS Item 8: Plant-Idiom Conformance Fixtures

**Status**: **Audited CONDITIONAL** (2026-07-05, commit `84ae948`) — substance fully
verified by static trace against the committed snapshots/baselines; clears to PASS on
one environmental item: **re-run the suite gate** (`uv run pytest tests/`), auditor was
harness-blocked from `uv run` (same block as Items 1/2/6/7). The one HARD assertion not
statically traceable is the collector pin `test_cross_part_inputs_pinned_or_baseline`
(rebuilds the graph at runtime; `fallback_entry_points` is not serialized into the
committed baseline) — only execution confirms it returns exactly `EXPECTED_UNCOVERED`.
Verified static: all 7 consumer shapes present + each pinned; shape-3 retype / shape-7
siblings correct in snapshot; shape-2 captured / shape-5 dropped; ≥14-literal floor (=16);
collector pin against ife_plant's OWN names (deliberate catf mirror, not conflation);
trap self-reference source_path; no `src/` changes; additive registration; 16 real-fixture
no-mock tests; snapshots v1. Recorded-not-re-executed: agentic-mbse run (repo outside
sandbox), WI-014 verbatim diff (fusion-tea sandbox-blocked). One non-blocking note: the
REQ-CA-09 malformed-refs pin is `@requires_license`, so it does not run in license-free CI
— an offline caplog pin was feasible. **Audit**: `.project/active/plant-fixtures/audit.md`.
Fixtures, captures, conformance tests, and agentic-mbse validation all landed. No `src/`
changes (spec Non-Goal). **Not committed** per orchestration.

**Gate**: 1928 passed / 4 skipped / 11 xfailed (was 1912 + 16 new); ruff src/ 21; mypy
src/ 109 (both unchanged). New fixtures reddened no existing test.

**Deliverables**: three fixtures under `tests/fixtures/` — `wi014_toy` (imported
verbatim from fusion-tea `964d3ae4`), `ife_plant` (authored, 6 shapes + 16 def
literals), `self_named_binding_trap` (isolated mechanism-D). Extraction snapshots for
all three; pipeline baselines for wi014_toy + ife_plant. Conformance tests:
`test_{wi014_toy,ife_plant,self_named_binding_trap}.py` (16 tests).

**Three live-probe outcomes**:
1. **WI-014 EXPOSE_PURE warning** = **malformed-refs** (`graph_builder.py:783`), not the
   reworded name-drop. → REQ-CA-09 discharged as a **recorded deferral** to Items 10/11.
2. **Mechanism-B surface** = **pipeline baseline** — ife_plant's graph builds (8 modules);
   shape-4 cross-part input falls to a Step-4 fallback, like catf's dangling input.
3. **Self-named trap** = **finite degenerate resolution** — extracts cleanly (no
   recursion); self-named binding resolves to the calc's own param. No register-A-1
   recursion note triggered (recursion is evaluation-time, not extraction-time).

**Per-shape labels**: correct = 3 (retype), 7 (siblings); known-incomplete = 2 (mech A,
`:>>`-valued def, captured-but-unwired), 4 (mech B, cross-part chain, collector pins
`cryo_load.magnet_volume`), 5 (mech C, plain-usage `:>>` override, dropped at extraction).

**Item 7 status at implement time**: LANDED — collector pin uses the definitive
exact-set assertion (Items 9-10 flip it).

**agentic-mbse impact (recorded for Item 12, not built here)**:
- **Reference examples**: the three fixtures are the canonical reference shapes for
  Item 12's MODELING_GUIDE plant-idiom guidance.
- **Validation run**: executed in-session via
  `agentic_mbse.validation.runner.run_all_checks`. **Well-formedness (L1-L5): all three
  PASS.** L6 architecture flags (recorded, not fixed): derived-expression-in-calc-def
  (all 3, incl. verbatim toy) + quoted-name EQN-derivation (toy + trap). The
  mechanism-specific negative checks (self-named-binding Level-2, mech A/C/D) do not yet
  exist in agentic-mbse — Item 12 builds them against these fixtures.

**Spec / Plan**: `.project/active/plant-fixtures/{spec,plan}.md` (no design — epic budgets
none). **Epic**: `.project/backlog/epic_upstream_findings.md` (Item 8 + consumers 9/10/11).

### UPSTREAM-FINDINGS Item 7: Resolution Matcher Fixes & Warning Reconciliation (SC-8)

**Status**: **Audited CONDITIONAL** (2026-07-05, commit `7aec029`) — implementation
sound and faithful to design; clears to PASS on two items:
1. **Add a retype_model reclassification pin** — the item's central behavioral churn
   (3 EPs USAGE_LITERAL → DESIGN_ATTRIBUTE, values 10.0/20.0/20.0 via Bug A) is the only
   real reclassification in the corpus, is enumerated in release notes but asserted by
   no test and has no committed baseline, and its values are Phase-0-computed /
   gate-unconfirmed. The mechanism is unit-tested (synthetic); the corpus instance is
   not. Fix: a snapshot-driven test asserting retype_model's 3 EPs' kind+values, or
   commit its pipeline baseline.
2. **Re-run the suite gate** — auditor was harness-blocked from `uv run` (same block as
   Items 1/2/6). Recorded gate: 1909 passed / 4 skipped / 11 xfailed; ruff 21; mypy 109.
**Verified static**: six-site flip clean (INV-1); V11 collector pure + predicated
fell-through ∩ valueless ∩ wired; catf_mfe pinned exact; five-fixture V11 surface;
warning demotions + count-summary + zero-WARNING (scoped per DEV-3); DEV-4 --from-snapshot
parity tested; docs/matrix/README/release-notes complete; no mocks.
**Epic**: `.project/backlog/epic_upstream_findings.md`
**Spec / Design / Plan**: `.project/active/warning-reconciliation/{spec,design,plan}.md`
**Audit**: `.project/active/warning-reconciliation/audit.md`

### UPSTREAM-FINDINGS Item 6: Expression Reconstruction Fidelity (SC-6)

**Status**: **Audited CONDITIONAL** (2026-07-05, commits `346cf47` feat + `77fc46c` chore) —
substance certified; clears to PASS on one item: re-run the suite gate (auditor was
harness-blocked from `uv run`). Same block as Items 1/2.
**Epic**: `.project/backlog/epic_upstream_findings.md`
**Spec / Design / Plan**: `.project/active/expression-fidelity/{spec,design,plan}.md`
**Audit**: `.project/active/expression-fidelity/audit.md`

Two display-path fixes in `expression_utils.py`: literal/null branches dispatch before the
invocation catch-all (via `is_instance`, REQ-AST-08), and operator expressions parenthesize
precedence-aware per the KerML table (REQ-AST-09). Verified statically: five hand-traces match
the design table exactly; zero `Literal*Evaluation` in the corpus; three snapshot restorers
present; **executable byte-identity holds across both regen commits by direct diff** (0 exec-field
changes). Regen ran as a two-commit split (chore = non-Item-6 staleness with the pre-Item-6
reconstructor; feat = display-only regen). All four recorded deviations sound. Doc 19 + matrix +
BACKLOG (aggregation-literal + constraint coverage) + PUSH-DOWN note landed.

**To clear CONDITIONAL → PASS:** re-run `uv run pytest tests/` (expect 1894 passed,
`test_live_vs_snapshot_byte_identical` green post-regen), `ruff check src/` (21), `mypy src/` (109)
in a Python-enabled env. No code change expected.

### UPSTREAM-FINDINGS Item 1: Baseline Repair & Silent-Failure Diagnostics

**Status**: **Audited CONDITIONAL** (2026-07-05, commit 3c42dd1) — implementation certifiable; clears
to PASS on a 3-item fix list (see `audit.md`). All five phases complete and committed.
**Epic**: `.project/backlog/epic_upstream_findings.md`
**Audit**: `.project/active/baseline-diagnostics/audit.md`
**Plan**: `.project/active/baseline-diagnostics/plan.md`

Done: D1 sort (`entry_point_groups` name-sorted) + I1 test; D2 constraint-drop diagnostic
(`report_dropped_constraints`, REQ-EXT-09); D3 zero-output fail-fast (REQ-EXT-08); D4 EXPOSE_PURE
wording reword (REQ-CA-09 test deferred to Item 8 — shape-A fires malformed-refs, not the reworded
warnings); dead-code deletion; Phase 3 re-capture (solar_battery ×3 + catf_mfe ×2, ordering-only) +
two stale-registry corrections; Phase 4 docs + verification matrix.

**To clear CONDITIONAL → PASS:** (1) reconfirm suite/ruff/mypy green on 3c42dd1 — auditor was
harness-blocked from running them; (2) flip verification-matrix REQ-BASE-05 from "PENDING RE-CAPTURE"
to PASS (the re-capture is already committed); (3) optional — the Item-2 `snapshot-generation/design-review.md`
was bundled into the Item-1 commit (harmless doc, scope-hygiene note).

### UPSTREAM-FINDINGS Item 2: Snapshot-Driven Generation (SC-9 + SC-10)

**Status**: **Audited CONDITIONAL** (2026-07-05, commit b9f9b82) — substance certified;
clears to PASS on one item: re-run suite/mypy/ruff (auditor was harness-blocked from `uv run`).
**Epic**: `.project/backlog/epic_upstream_findings.md`
**Spec / Design / Plan**: `.project/active/snapshot-generation/{spec,design,plan}.md`
**Audit**: `.project/active/snapshot-generation/audit.md`

Supported `--from-snapshot` generation path + `snapshot` capture command, so
generation/debug/CI decouple from the syside license (expires 2026-08-06).
Delivered: promoted `sysml_codegen.snapshot` package; format versioning +
provenance/freshness guards; `compilation_results` serialized (SC-10 — CalcUsage
auto-impl survives); `source_file` relativize-at-capture / lexical-re-absolutize-at-load.
**SC-1 proven live**: `generate --from-snapshot` byte-identical to
`generate --models` incl. a symlinked run (empty tree diff). **SC-10 proven**:
chain_spike stencils auto-implement from the committed snapshot. Reference doc:
`docs/architecture/reference/27-snapshot-generation.md` (REQ-SNAP-08..19).
One deviation: completed Item 1's deterministic entry-point sort by also sorting
parameters within each group (`graph_builder.py:375`) — required for SC-1 byte-identity.
Suite 1837 passed; mypy 109 / ruff 21 (== baseline, recorded — not re-run by auditor).
**Audit findings (all low-severity, non-blocking):** deviation #2 undercount (4 new
`# type: ignore`, not two — all scoped/sound); dead `out` var in a test; plan Phase 3/4/5
checkboxes unfilled though deliverables landed. See `audit.md`.

### UPSTREAM-FINDINGS Item 3: Return-Style & Bare-Parameter Extraction (SC-2)

**Status**: **Audited PASS / Certify** (2026-07-05, commit 559a0bb). All 4 plan
phases verified; spec criteria met on committed evidence. Two non-blocking
verification limits (see audit): tests not re-run (harness-blocked) — green rests on
recorded gate + direct snapshot/code inspection; A-2 stencil fix not read directly
(agentic-mbse outside session sandbox) — verified against plan/commit evidence, and
Item 12 re-verifies it as an explicit gate.
**Epic**: `.project/backlog/epic_upstream_findings.md`
**Spec / Design / Plan**: `.project/active/return-style-extraction/{spec,design,plan}.md`
**Audit**: `.project/active/return-style-extraction/audit.md`

Relaxed the calc-def member filter to a shared `_is_parameter_member` predicate at
both passes (`extractor.py`): named `return` and bare `in` (direction-carrying
ReferenceUsage) now extract; named inline `return` auto-implements. Anonymous
`return` raises the new V8 diagnostic before V7 (V7 reworded — no more "not yet
extracted (Item 3)"). New `return_styles` fixture (4 styles + design part) +
committed snapshot + `anonymous_return` live fixture; `test_return_style_extraction.py`
(11 tests, live + offline). Docs lockstep: REQ-EXT-10/11/12 in 01-extraction +
verification-matrix, V7/V8 rows in modeling-assumptions. Body-assignment capture
deferred (BACKLOG.md, P3). **A-2 stencil fix applied in `~/1cfe/agentic-mbse`
(uncommitted — report to orchestrator).**

**Phase 0 deviation (key finding):** the design's primary V8 rule ("direction-Out +
empty `sanitize_name`") was REFUTED live — an anonymous `return` gets a
syside-synthesized name `result` (non-empty), so V8 keys off the probe-evidenced B4
fallback instead: an owned `ReturnParameterMembership` whose `declared_name` is empty.
Plain `out attribute` calc defs carry no such membership → existing fixtures safe.

**I1 gate:** re-capture diff was `captured_at`-timestamp-only across all 10 existing
snapshots (zero semantic change); baselines byte-identical. Reverted the
timestamp-only rewrites — only `return_styles` + `anonymous_return` added.
Suite 1857 passed / 4 skipped / 5 xfailed; mypy 109, ruff 21 (== baseline).

### UPSTREAM-FINDINGS Item 4: Part-Usage Type Indexing (SC-3)

**Status**: **Audited PASS / Certify** (2026-07-05, commit 82b70b8). All 3 plan phases verified;
all 9 spec success criteria met on committed evidence. FIX 2 fallback deviation verified sound
(fires only when owned FeatureTyping is absent → cannot reach retyped usages). Two verification
limits: suite/mypy/ruff not re-run (sandbox blocked `uv run`) — green rests on recorded gate
(1870/4/5; ruff 21; mypy 109 == baseline) + direct snapshot inspection; live-layer tests skip
without a license (offline mirrors all verified against the committed snapshot).
**Epic**: `.project/backlog/epic_upstream_findings.md`
**Spec / Design / Plan / Audit**: `.project/active/type-indexing/{spec,design,plan,audit}.md`

Retyped part usages (`part :>> x : Subtype`) now instantiate their subtype's template
calcs instead of silently dropping them. Fixed the first-type bug in two places
(`usage_extractor.py` `_build_part_usage_index`, `hierarchy_resolver.py` `usage_type_map`):
index/resolve by **owned FeatureTyping target(s)** plus every user-model PartDef in
`usage.types`, never by list position. Shared helpers in `usage_extractor.py`
(`owned_feature_typing_targets`, `user_partdef_types`, `user_partdef_lookup`,
`most_specific`). Virtual-QN collision tiebreak (most-specific owner + **V9**) at the
`seen_qns` dedup; incomparable multi-typing → sorted-first + **V10**.

**Probe (Phase 0):** B1 (heritage owned-only) and B2-plain (plain `.types` excludes user
supertype) both CONFIRMED; Q4 (`elements_of_type(PartDefinition)` excludes `Part`) confirmed
→ intersection is the whole user filter. No hard stops.

**Delivered:** 3 shared helpers + `most_specific` (unit test, 6 cases); 6-shape `retype_model`
fixture + committed snapshot; `test_type_indexing.py` (7 tests, offline+live), tagged
REQ-EXT-13/14 + REQ-LVP-08. Docs: modeling-assumptions §5 + V9/V10; ref 01/25; verification
matrix. Suite **1870 passed** / 4 skipped / 5 xfailed; mypy 109 / ruff 21 (== baseline).

**Key deviation (baseline invariance):** the Phase-3 re-run caught that FIX 2's most-specific
pick dropped dead `Parts__Part` `usage_type_map` entries for **untyped** inline parts
(`part x {}`) in catf_mfe. Added a fallback: no owned FeatureTyping → keep position-0 `.types`
(nothing to compare). Baseline **content zero-diff** confirmed (excl. `captured_at`);
`test_factory_purity` green. `agentic_mbse` untouched (Item 12 executes the recorded impact).

### UPSTREAM-FINDINGS Item 5: Identifier Sanitization (SC-4, + SC-11 riders)

**Status**: **Audited PASS / Certify** (2026-07-05, commit 4b19e4d, 18 files). All 5 plan
phases verified; all 6 spec success criteria met on committed evidence; both recorded
deviations (INV-1 corpus-honest reformulation; FORMULA fixture consumer = computed attribute
on the resolution_map path) verified sound. INV-3 match sites + `:130` confirmed untouched
by diff-scope; schema key-space check verified against the real `_generate_schemas`
condition. One verification limit (same as Items 1–4): suite not re-run — harness-blocked
from `uv run`; 1880/21/109 gate rests on recorded evidence + direct inspection.
**Epic**: `.project/backlog/epic_upstream_findings.md`
**Audit**: `.project/active/identifier-sanitization/audit.md`
**Spec / Design / Plan / Close-out**: `.project/active/identifier-sanitization/{spec,design,plan,close-out}.md`

Quoted SysML calc-def names produce non-importable Python (`class 'Margin
Calc'Input`, `'margin calc'.py`). Fix at the **derivation layer** — framed as
item-boundary discipline (name-emission slice now; the both-sides FORMULA registry-key
sanitization at `output_registry_builder.py:130`/`:595` deferred to Item 7, which owns
the match sites and must flip `:130` in lockstep). New `sanitize_qualified_name` helper
at `identifier_types.py` `from_sysml` + FORMULA channel/module_eqn emission sites
(`output_registry_builder.py:124`, `graph_builder.py:745/789/818`); match sites
(`dependency_backtracker.py:660`, `parameter_groups.py:439`, `pipeline_builder.py:70`)
untouched. Duplicate-path fail-fast covers all three write key spaces (modules/stencils
share filename key; schemas separate `calc_def_name.lower()`). Conformance: `alias_agg_probe`
full-generation (`ast.parse` + import-name) **plus a new live-captured quoted-owner
FORMULA fixture** proving the wire resolves (existing 11 snapshots + 4 baselines stay
byte-identical; new fixture additive). SC-11 closed; post-alias uniqueness re-check IN
pending a plan-phase static check (WARN-first if a baseline hits the grandparent case),
AST import-rewrite deferred.

### UPSTREAM-FINDINGS Item 6: Expression Reconstruction Fidelity (SC-6)

**Status**: Spec in progress
**Epic**: `.project/backlog/epic_upstream_findings.md`
**Spec**: `.project/active/expression-fidelity/spec.md`

Docstrings/stencils show corrupted math (`LiteralRationalEvaluation()` for
literals, dropped parens) while executable bodies are correct. Root cause
(research-corrected): branch ordering in `reconstruct_expression`
(`expression_utils.py`) — the invocation catch-all precedes the literal branches,
and every SysIDE node carries a derived `.function`, so literals never reach their
branch; plus no parenthesization in `reconstruct_operator_expression`. Fix is
display-path-only (executable text comes from a separate compiler path). Must land
before the PUSH-DOWN epic moves `expression_utils.py`. Owner doc: 19
(ast-dispatch-invariant, REQ-AST family — revises REQ-AST-03's ordering). Baseline
regen is two-tier: extraction snapshots need live license, pipeline baselines
rebuild offline.

### UPSTREAM-FINDINGS Item 7: Resolution Matcher Fixes & Warning Reconciliation (SC-8)

**Status**: Spec in progress
**Epic**: `.project/backlog/epic_upstream_findings.md`
**Spec**: `.project/active/warning-reconciliation/spec.md`

Two matcher bugs behind the benign "Registry unresolved" noise (per-segment
sanitizing QN conversion on the REFERENCE path — executes Item 5's `:130`
lockstep flip; and usage-name-aware / QN-suffix matching for part-def-owned
design attributes with empty `parent_part`). Behavioral: entry points
reclassify (`USAGE_LITERAL` → `DESIGN_ATTRIBUTE`), Step-3 dedup returns —
baselines and params-JSON keys churn and are reviewed deliberately. Step-4
fallback warnings demote to DEBUG + a post-assembly reconciliation summary;
new V11 params-coverage hard error (sibling to `_validate_channel_references`)
catches the catf_mfe dangling `magnet_volume`. **Decision:** xfail catf_mfe's
E2E generation (do not alter the fixture — `magnet_volume_total = tf_coil.volume`
is a real cross-part EXPOSE for Items 9–11); prove the check with a seeded
fixture. Baseline sequencing runs against whatever Item 6 has committed.

### UPSTREAM-FINDINGS Item 8: Plant-Idiom Conformance Fixtures

**Status**: Spec revised (post spec-review; verdict was Revise, six rulings applied)
**Epic**: `.project/backlog/epic_upstream_findings.md`
**Spec**: `.project/active/plant-fixtures/spec.md`
**Review**: `.project/active/plant-fixtures/spec-review.md`

Closes the fixture blind spot for the plant idiom before SC-5 (Items 9–11)
begins. Fixtures/captures only — no `src/` production code. Three fixtures:
`wi014_toy` (imported from fusion-tea; part-def EXPOSE_PURE / shape A +
REFERENCE-binding warning paths; carries the REQ-CA-09 shape-A test Item 1
deferred); an authored `ife_plant` (def-declared attribute literals with a ≥14
richness floor, `:>>`-valued specialized subsystem defs, retyped nested parts,
cross-part calc chains, plain-usage `:>>` overrides, **two same-type sibling
parts** for Item 10's instance-ambiguity SC); and an **isolated**
`self_named_binding_trap` (mechanism D, own dir + timeout guard so a possible
syside recursion can't poison ife_plant). Captures extraction snapshots + CURRENT
known-incomplete pipeline baselines via the graph-build path (order-independent;
strict-generate V11 is expected/xfailed, not the bar). **Decoupled from Item 7:**
the collector-pin conformance assertion is conditional, no HARD requirement
depends on unlanded Item 7 code. Needs live syside license (R3 — before
2026-08-06). Source dirs sandbox-blocked from spec session → import procedure
specified.

### REFACTOR: Incremental Pipeline Refactor

**Status**: In Progress (Phases 0–4 complete)
**Plan**: `.project/concepts/refactor-design-intent/IMPLEMENTATION_PLAN.md`
**Checklist**: `.project/concepts/refactor-design-intent/COMPONENT_CHECKLIST.md`
**Branch**: `cost-pattern-refactor`

**Objective**: Bottom-up, test-first refactor of the pipeline. Lock down every component with conformance tests using real data, then restructure the codebase to match target architecture.

**Completed Phases**:
- [x] Phase 0: Test Infrastructure & Baselines (70 tests, 6 extraction snapshots, 4 pipeline baselines)
- [x] Phase 1: Foundation & Extraction Components (C01-C07, 311 conformance tests)
- [x] Phase TRR: Typed Registry Refactor design doc updates (8 docs updated)
- [x] Phase 2: Core Infrastructure Spikes (C08-C10, 117 conformance tests)
- [x] Phase 3: Analysis Components (C11a/b, C12, C13, X02, 136 conformance tests)
- [x] Phase 4: Module Factory + Graph Assembly (C14-C18, 183 conformance tests, Checkpoint 4 passed)
- [x] Phase 5: Orchestrator Integration (C19 + 5.2, 55 conformance tests, Checkpoint 5 passed)

**Current Phase**: Phase 6 — Generation Layer Validation (C20-C25, X01)

**Test Suite**: 1587 tests passing (920 conformance + 667 existing), 5 xfailed

**Key Decisions**:
- Typed Registry Refactor complete — 3 typed registries, zero `_compat`, zero `resolve()`
- Backtracker typed dispatch (C11b) migrated all 14 compat-only resolutions to typed lookups
- Input Resolver (C12) proven equivalent to old function; graph_builder integration deferred to C16

**Blockers**: None

**Audit**: Phase 3 audit complete — see `.project/concepts/refactor-design-intent/PHASE3_AUDIT_ACTIONS.md`

---

## Recently Completed

### 2026-02-17: Phase 5 — E2E Pipeline Validation (5.2) — Checkpoint 5
- 16 conformance tests in `tests/conformance/test_pipeline_e2e.py`
- catf_mfe baseline generated: 42 modules (all CalcUsage), 8 EP groups
- Baseline comparison for all 4 models (solar_battery, catf_mfe, chain_spike, attr_expr_probe)
- REQ-PIPE-01 through REQ-PIPE-06 validated end-to-end
- Checkpoint 5: All 4 models match baselines — refactored pipeline composes correctly
- No production code changes — conformance-only

### 2026-02-17: Phase 5 (partial) — Orchestrator Step Ordering (C19)
- 39 conformance tests in `tests/conformance/test_orchestrator.py`
- Static analysis: `build_pipeline_context()` 10-step DAG ordering verified
- FORMULA removal safety net verified (zero natural overlap in fixtures; constructed overlap exercises logic)
- Registry 4-phase ordering: all aliases target Phase 1 canonical channels (solar_battery + catf_mfe)
- Pipeline invariants (PIPE-01–06) verified across 4 models (solar_battery, catf_mfe, chain_spike, attr_expr_probe)
- REQ-PIPE-07 baseline: 9 generation/ files import from extraction/analysis (Phase 7.6 target)
- No production code changes — conformance-only

### 2026-02-17: Phase 4 — Module Factory + Graph Assembly
- C14 CalcUsage Factory (48 tests), C15 FORMULA Factory (34 tests), C16 Aggregation Factory (32 tests)
- C17 Entry Point Classification (35 tests), C18 Graph Assembly (34 tests)
- Checkpoint 4 baseline comparison: solar_battery, chain_spike, attr_expr_probe match Phase 0 baselines
- All 3 module types verified (CalcUsage + FORMULA + Aggregation)
- Baseline normalization documented: CalcUsage compilability (snapshot serialization boundary), parameter ordering (dict iteration order)
- All design doc amendments applied (06-entry-point-classifier.md, 11-analysis-backtracker.md)

### 2026-02-17: Phase 3 — Analysis Components
- C11a Backtracker Conformance (43 tests), C11b Typed Dispatch Migration (17 tests)
- C12 Input Resolver (26 tests), C13 ParameterGroupDeriver (30 tests), X02 Dual Resolution (20 tests)
- Backtracker fully migrated to typed dispatch: scoped_lookup/sysml_qn_lookup/alias_lookup
- `_compat` dict, `resolve()`, `register()` removed from OutputRegistry
- 14 previously compat-only resolutions (12 catf_mfe + 2 solar_battery) now typed
- D3: Static analysis helpers extracted to `tests/helpers/static_analysis.py`

### 2026-02-17: Phase 2 — Core Infrastructure Spikes
- C08 Output Registry (32 tests), C09 Virtual Binding Rewrite (38 tests), C10 Aggregation Scoping (47 tests)
- 5 NewType wrappers + 3 typed registries implemented
- Phase 2 audit: 6 fixture coverage gaps investigated (C1-C6), 4 closed, 1 partially closed, 1 pending

### 2026-02-17: Phase TRR — Typed Registry Refactor (Design Docs)
- All 8 TRR design doc updates applied (docs 03, 04, 09, 10, 11, 15, 24, 27)
- New design intent doc: `27-typed-registry-refactor.md`

### 2026-02-17: Phase 1 — Foundation & Extraction Components
- C01-C07, all 49 requirement IDs verified

### 2026-02-17: Phase 0 — Test Infrastructure & Baselines
- Extraction snapshots for 6 models, pipeline baselines for 4 models

### 2026-02-10: COST-PATTERN Items 1-4
- Hierarchy-aware codegen: templates, redefinitions, aggregation, pipeline integration

---

## Up Next

1. Phase 6: Generation Layer Validation (C20-C25, X01)
2. Phase 7: Structural Refactoring & Dead Code Removal

---
