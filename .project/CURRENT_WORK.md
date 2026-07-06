# Current Work

**Last Updated**: 2026-07-05

---

## Active Work

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
