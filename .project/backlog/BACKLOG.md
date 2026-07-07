# Product Backlog

Prioritized list of epics and features.

**Last Updated**: 2026-07-06

---

## Priority Legend

- **P0**: Critical - Blocking, do immediately
- **P1**: High - Important, do soon
- **P2**: Medium - Valuable, do when possible
- **P3**: Low - Nice to have, do eventually

---

## In Progress

| Item | Priority | Status | Started | Notes |
|------|----------|--------|---------|-------|
| generation-boundary | P1 | In Progress (BUILD phase) | 2026-02-20 | Step 7.6 — enforcing generation/ only consumes ComputationGraph. Phases 1-2-4 done. **FLAG (Item 8, 2026-07-06):** Item 8 deletes generation-layer symbols on a rebase-sensitive surface — `map_sysml_type_to_rootmodel_wrapper` (`generation/type_mapping.py`), `generate_derived_group_json` + its `generation/__init__.py` re-exports (`generation/entry_point.py`), and two dead Jinja templates in `src/sysml_codegen/templates/` (a sibling of `generation/`). Do not resurrect these exports on rebase. |
| hierarchical-output | P2 | Draft (spec only) | 2026-02-22 | Convert flat JSON output to hierarchical structure reflecting SysML part hierarchy. |
| new-pipeline-explainer | P2 | Draft (active) | 2026-02-22 | Interactive HTML explainer for refactored 7-step pipeline architecture. |

---

## P1 - High Priority

| Epic | Status | Notes |
|------|--------|-------|
| [PIPELINE-TRUTH] The Generated Package Is the Truth | Draft | Finish what UPSTREAM-FINDINGS staged: fusion-tea's models generate/wire/execute end-to-end with zero bridges (the 10 V11 offenders — promoted from Ideas), every diagnostic fires on the shape it claims (assert-constraint silence + the subtype-blind enumeration pattern), zero self-referential tests, REQ/matrix truth (F2/F4), silent-failure hardening (16 sites), cleanup debt, agentic-mbse lockstep, closing docs+explainer-prompt pass. 10 items, ~10.5–13.5 days. Evidence: `.project/research/20260706_pipeline-truth-discovery.md`. See `epic_pipeline_truth.md`. Items: [ ] 1 plant-value fixtures [ ] 2 whole-plant resolution [ ] 3 fusion-tea acceptance+retirement [ ] 4 subtype enumeration [ ] 5 silent-failure hardening [ ] 6 self-referential tests [ ] 7 matrix reconciliation [ ] 8 cleanup debt [ ] 9 agentic-mbse sync [ ] 10 docs+explainer close |
| [PUSH-DOWN] agentic-mbse Push-Down Design | Design ready | Move reusable SysML semantics (~875 lines) from sysml-codegen extraction/ into agentic-mbse/sysml/. Phase 1 (LOW risk): expression_utils + qualified_names. Phase 2 (MEDIUM risk): hierarchy + aggregation. **Sequencing: the UPSTREAM-FINDINGS Item 6 prerequisite has landed (PR #3); new ruling — start after PIPELINE-TRUTH Items 5 (silent-failure hardening) and 8 (cleanup debt) land, since both modify the same extraction/ surfaces the push-down would move.** See `.project/concepts/agentic-mbse-push-down-design.md`. |

---

### [CONSTRAINT-SILENCE] `assert constraint` invisible to the drop report — RESOLVED (PIPELINE-TRUTH Item 4)

**RESOLVED by PIPELINE-TRUTH Item 4** (`epic_pipeline_truth.md`), 2026-07-06. The drop report now
sweeps `ConstraintUsage` subtype-aware (`include_subtypes=True`), so `assert constraint`
(`AssertConstraintUsage`) is reported; the summary is a scanned/reported/excluded sentinel that never
goes fully silent. Pinned by the re-anchored REQ-EXT-09 (`tests/conformance/test_extractor.py`, wi014
assert + mutation check) and available on the `--from-snapshot` path too. Retained below for
provenance.

**Source**: fusion-tea upstream-fix verification, 2026-07-06
(`~/1cfe/fusion-tea/work/active/20260706_upstream-fix-verification/report.md`); verified
in-repo 2026-07-06. `report_dropped_constraints` (`extraction/extractor.py:92`) enumerates
`elements_of_type("ConstraintUsage")`; syside's `model.elements()` is exact-type, so
`assert constraint` (`AssertConstraintUsage`, a subtype) is invisible. Both the per-item
INFO loop and the summary WARN gate on a non-empty list (`extractor.py:123`), so the report
is **completely silent** for exactly the shape fusion-tea uses (`ife_plant.sysml:155`
`assert constraint viability`) — live probe: 0 ConstraintUsage, 1 AssertConstraintUsage.
Compounding factors the fix must address, not just the query:
- The REQ-EXT-09 test (`tests/conformance/test_extractor.py::TestReqExt09`, line 895)
  computes its expected count **with the same query the implementation uses** —
  self-referential, structurally unable to catch this. Re-anchor independently.
- Its fixture (catf_mfe) has only plain constraints; `tests/fixtures/wi014_toy/toy_plant.sysml:51`
  already carries an `assert constraint` but nothing asserts the report against it —
  Item 1's "WI-014 toy emits the constraint diagnostics" criterion was never true for it.
- `extraction/constraint_extractor.py:4` docstring claims "constraint, assert constraint,
  and require constraint" support while using the same blind query (line 50) — check
  `require constraint` (`RequireConstraintUsage`?) too.
- Snapshot-path split (corrects the fusion-tea report's line-74 observation): `snapshot`
  *capture* DOES run the report (`capture.py:42` → `build_pipeline_context` →
  `pipeline_builder.py:685`) — it was silent there only because of this very bug — but
  `generate --from-snapshot` (`snapshot_context.py:24`) does NOT, and cannot: constraint
  data is **never serialized** (serializer writes no constraint fields;
  `_deserialize_constraint_info`, `loader.py:275`, has zero callers — dead code). A
  snapshot-first workflow loses constraint info permanently — decide whether to serialize
  constraints (prerequisite for any from-snapshot report AND for the deferred
  constraint-execution epic).
- Docs impact: modeling-assumptions §8 ("scans the whole model for constraint usages and
  reports them") overclaims until the fix lands.
- Owner split: the exact-type behavior lives in agentic-mbse's `SysideAdapter.elements_of_type`
  / syside `model.elements()`; the consumers are in this repo. Meta-item: audit every
  `elements_of_type` call site for the same subtype-blindness pattern.

## P2 - Medium Priority

### [SYNC-F3] Shape-B leaf-collision filename edge (UPSTREAM-FINDINGS Item 12, F3)

**Source**: alias-surfacing (Item 11) audit Obs. 2. Two distinct shape-B owning parts that
share a leaf name and expose the same alias to different channels produce the same output
filename `{instance_path}__{alias}.json` — a collision codegen does not yet disambiguate.
Not triggered by any in-repo fixture. File to disambiguate (e.g. qualify by owning-part
path) before a real model hits it.

### [SYNC-F4] Redefinition / design_override name surfacing (UPSTREAM-FINDINGS Item 12, F4)

**Source**: alias-surfacing (Item 11) release-notes §impact. `:>>` and design-override names
resolve as channels but are not EXPOSE_PURE-sourced, so they do not surface as named
outputs. Decide whether these names should surface (mirror of D6/EXPOSE surfacing) or stay
internal.

### [SYNC-F5] Positive unresolvable-warning test (UPSTREAM-FINDINGS Item 12, F5)

**Source**: alias-surfacing (Item 11) audit Obs. 1. Item 11's INV-6 "unresolvable refs still
warn" leg has no positive live assertion. Add a test that asserts an unresolvable ref emits
its warning. Opportunistic — cheap to add in sysml-codegen's test suite.

---

## P3 - Low Priority

### [DOCS-SCRUB-F1] Delete the two dead templates (+ dead-code candidates nearby)

**Absorbed into PIPELINE-TRUTH Item 8** (`.project/active/cleanup-debt/`), 2026-07-06. Both dead
templates deleted; `map_sysml_type_to_rootmodel_wrapper` (+ its now-orphaned
`PYTHON_TO_ROOTMODEL_WRAPPER` dict) and `binding_to_entry_point` dual-write deleted in Phase 1;
`get_default_value` / `generate_derived_group_json` resolved in Phase 2 (see close-out).

**Source**: docs-scrub (post-UPSTREAM-FINDINGS docs pass), 2026-07-06. Zero render sites
each (re-confirm with grep before deleting):
- `src/sysml_codegen/templates/pydantic_schema.py.jinja2` (carries `generation_timestamp`;
  originally verified dead during Item 2)
- `src/sysml_codegen/templates/entry_point_schema.py.jinja2` (only
  `parameter_group_schema.py.jinja2` is rendered by `generation/entry_point.py`)

Same-cleanup candidates found during the scrub (verify, then delete or wire up):
- `map_sysml_type_to_rootmodel_wrapper()` in `generation/type_mapping.py` — no external
  callers; `modules.py` imports `map_sysml_type_to_python` without calling it (dead import).
- `get_default_value()` on the ParameterGroupDeriver — only its conformance test calls it
  (REQ-PGD-06 would need re-framing if removed).
- `generate_derived_group_json()` in `generation/entry_point.py` still emits null-default
  keys, unlike `generate_all_derived_jsons()` which omits them (Item 7's corrected shape) —
  check reachability; it reintroduces the null-key shape if still live.
- `BacktrackingResult.binding_to_entry_point` — marked DEPRECATED "will be removed after
  all consumers updated" since long before the epic.

### [DOCS-SCRUB-F2] Reconcile REQ-OR-05/06/08 with the Key_A/Key_F registrations at HEAD — RETIRED (Item 7)

**Retired 2026-07-06 by Item 7.** Design check confirmed the construction-time
`instance_attr_to_channel` dict does NOT bypass the typed-registry contract (it feeds
only guarded `register_alias` calls), so F2 landed as **fix-text-to-code**: REQ-OR-05/06/08
text + doc 10's key-format section now describe the actual registrations (Key_A guarded
alias, Key_F scoped), REQ-ORCH-04's real phase-order contract is restored via a
fixture-anchored presence assertion (red-mutation-gated), and the two lying docstrings
(`test_output_registry.py`, `test_orchestrator.py`) are corrected. Superseded.

**Absorbed into PIPELINE-TRUTH Item 7** (with D7 refinements: REQ-ORCH-04's test was
weakened to fit the divergence; two test docstrings misstate their own bodies).

**Source**: docs-scrub doc-10 pass, 2026-07-06. The REQ text and doc 10's "Eliminated Key
Formats" section say Key_A and Key_F are not registered at all, but `build_output_registry()`
Phase 1a registers Key_A via `register_alias()` (cross-scope CHAIN, first-wins) and Phase 1c
registers Key_F via `register_scoped()` (REFERENCE secondary, spike Q5); Phases 3–4 also
consult a construction-time Key_A-format dict (`instance_attr_to_channel`) before typed
lookups (vs REQ-OR-06's "through typed lookup"). `test_output_registry.py::TestReqOR08` has
already narrowed its own reading. Decide the intended contract, then fix REQ text + doc 10 +
(possibly) code together — not a docs-only fix.

### [DOCS-SCRUB-F4] `resolve_input()` cutover divergence — RETIRED (PIPELINE-TRUTH Item 7)

**Retired 2026-07-06 by Item 7.** The three F4 kill probes ran and fired no kill
(`.project/active/matrix-truth/probes/`), so the reconciliation direction resolved to
**LAND-with-split**: Item 7 reframed the matrix rows + docs 03/04/05 to the true state
(`resolve_input` is a parity-validated, not-yet-wired consolidation; the live path is
`_resolve_aggregation_input_channel`), and the executable cutover is filed below as
**[ITEM7-F4-CUTOVER]**. This filing is superseded by that one.

### [ITEM7-F4-CUTOVER] Wire aggregation resolution through `resolve_input()` — P2, executable follow-on

**Filed by PIPELINE-TRUTH Item 7, 2026-07-06.** Item 7's F4 reconciliation reframed the
matrix/docs to the honest state but deliberately **split out the code cutover** (fallback
refactor + baseline re-capture exceeds Item 7's 1.5–2 day budget; spec Open Question
authorizes the split). This item carries the executable change, pickable cold.

**Goal.** Make the live aggregation path call `resolve_input(AGG_STRATEGIES)` instead of
the inline `_resolve_aggregation_input_channel` (`graph_builder.py:1212`), so the whole IR
family finally pins live code.

**The correct comparand (design-review M3 — DO NOT skip).** The cutover's safety-net
parity suite MUST compare `resolve_input(AGG_STRATEGIES)` against
**`_resolve_aggregation_input_channel`** — the function it replaces — not only the
backtracker DFS. Probe (i) and Item 7's committed `TestResolveInputParityExtended` prove
parity against the *backtracker*, which is general-correctness evidence, NOT
parity-with-the-replaced-function. Add the `_resolve_aggregation_input_channel` comparand
as this item's own gate before rewiring.

**The EP-key reconciliation (design-review M4 — the load-bearing blocker).** See
`.project/active/matrix-truth/probes/probe_iv_ep_key_divergence.md`. The live path builds
the SumTerm entry-point QN as `{module_eqn}__{part_usage}_{attr}` (e.g.
`…site_infra__raw_material_cost__permitting_raw_material_cost`); `resolve_input`'s leaf-only
fallback builds `…site_infra__raw_material_cost__raw_material_cost` — which **already
coexists in the same graph as the module's own output channel** (concrete baseline lines:
`tests/fixtures/baseline_outputs/solar_battery/computation_graph.json:2472/2483/3270/3486`).
A naive drop-in collides an input EP with an output-channel name and drops the part-usage
disambiguator. Reconcile `resolve_input`'s fallback to the live richer EP construction
(part_usage-prefixed QN, `_find_literal_redefinition` defaults, param-groups, multiplicity
EPs, SingletonTerm "Try 2" direct-channel construction) BEFORE rewiring.

**Scope.**
1. Reconcile `resolve_input`'s fallback to the live path's richer EP construction (above).
2. Rewire the 3 aggregation resolution call sites: `graph_builder.py:1444, 1539, 1640`
   (`_resolve_aggregation_input_channel` calls in SumTerm / SingletonTerm / LocalTerm-EXPOSE
   handling). Line numbers as of Item 7; re-verify at pickup.
3. Re-capture baselines byte-identically, or land as a reviewed `scripts/capture_*.py`
   diff (R3 / SC-G).
4. **Delete Strategy D** — `DesignAttributeLookup` (`input_resolver.py:200`) is a
   documented no-op (`return None`, zero live surface: probe ii → 0 key churn on
   catf_mfe/solar_battery). Remove it from `AGG_STRATEGIES` and **fix its lying docstring**
   ("included in AGG_STRATEGIES for future extensibility") — the residual ghost Item 7 left
   noted, not fixed.

**Safety-net evidence (probe pointers).** `.project/active/matrix-truth/probes/`:
`probe_i_extended_parity.py` (+ run log, now committed as `TestResolveInputParityExtended`),
`probe_ii_strategy_d_dedup.py` (+ run log — Strategy D delete justification),
`probe_iii_module_drift.md` (byte-identical since COST-PATTERN birth),
`probe_iv_ep_key_divergence.md` (the EP-key blocker above).

**Done when:** IR rows re-pin the live path (drop the "not-yet-wired" family note),
`_resolve_aggregation_input_channel` is deleted, Strategy D is gone, baselines are
byte-identical or reviewed, and the parity gate runs against the replaced function.

### [DOCS-SCRUB-F3] Stale code docstrings found while verifying docs (one-line fixes)

**Source**: docs-scrub, 2026-07-06. Code changes, out of scope for the docs-only pass:
- `_resolve_binding_via_registry` docstring (`analysis/dependency_backtracker.py`): lists a
  REFERENCE "Step 1b: Normalize :: to dotted -> scoped_lookup" that doesn't exist in
  `_resolve_reference_dispatch`, and its CHAIN summary omits Step 1c.
- `OutputRegistry` class docstring (`core/output_registry.py`): says "Three typed
  registries" (there are four) and its phase list omits Phase 3b; `__repr__` omits the
  `_scoped_alias` count.
- `build_pipeline_context` docstring (`orchestration/pipeline_builder.py`): old 7-step
  summary with the group deriver ahead of the registry (it runs at Step 5.7, after).
- `tests/conformance/test_graph_assembly.py` section header/class docstring still say
  "exactly 3 fields" (the test body pins 5).

### [SANITIZER-MERGE] Two-sanitizer consolidation (D1-F2) — P3, load-bearing divergence

**Filed by PIPELINE-TRUTH Item 8 (D1-F2), 2026-07-06.** `core.sanitize_name`
(`core/qualified_names.py:13`) vs `expression_compiler._sanitize_name`
(`extraction/expression_compiler.py:167`) diverge deliberately: the compiler drops the
reserved-word suffix `core.sanitize_name` applies, and the FORMULA REFERENCE wire matches *by
construction* on that difference. **Assessed → FILE (not merged):** a naive shared core risks
breaking the FORMULA REFERENCE match, and the byte-identity discipline makes a speculative merge
high-risk for near-zero gain. Implement a shared core only if it falls out safely with the
byte-identity gate green. Not forced in a cleanup pass.

### [SC11-IMPORT-REWRITE] AST-based import rewrite (D1-F1 / SC-11) — P3, not small

**Filed by PIPELINE-TRUTH Item 8 (§G), 2026-07-06.** `identifier-sanitization/close-out.md:31`
claimed the AST-based import rewrite (substring, first-match) was a "filed follow-up" — it was
filed **nowhere**; the false claim is now corrected in that close-out. **Assessed → FILE:** the
size judgment is *not small*. Compared against the registry alias-rewrite's no-not-found branch (a
D3 hygiene site, a 1–2-site local change), a correct substring/first-match import rewrite is a
cross-module AST rework. Build it as its own scoped change, not opportunistically. This entry is
the SC-11 assessment-verdict artifact.

### [GB-PARAMGROUPS-TYPING] graph_builder `param_groups` type-ignore cluster (D1-F4) — P3

**Filed by PIPELINE-TRUTH Item 8 (D1-F4), 2026-07-06.** The 2-ignore cluster
(`resolution/graph_builder.py:408/412`, `[assignment]` + `[attr-defined]`) guards a genuine mypy
narrowing: `param_groups` is bound twice (Step-5 `_group_entry_points_via_deriver`, then the
Step-6.6 rebuild via `_convert_derived_groups`) and mypy keeps a `DerivedParameterGroup` typing at
the sort site. **Assessed at implement:** removing the ignores raised mypy 104→106 (real errors,
not stale); a root annotation at the first binding did **not** clear it — the fix needs splitting
the double-binding into two distinctly-named variables (the Step-5 result is discarded by the
Step-6.6 rebuild anyway, so it is likely a removable dead computation). Deferred rather than churn
graph_builder's group-assembly flow in a cleanup pass. **Constraint honored: mypy stayed at 104
(ignores retained).**

### [ITEM7-PGD06] Re-frame REQ-PGD-06's matrix PASS row — CONDITIONAL, Item 7 consumes

**Source**: PIPELINE-TRUTH Item 8 (`.project/active/cleanup-debt/spec.md`, row B), filed
2026-07-06. **FIRED (2026-07-06) — Item 8 confirmed `get_default_value` DEAD and deleted it**
(zero production callers; the live default path resolves inline via `_parse_default_value` in
`_derive_from_*`). Item 8 landed the doc-17 re-frame (rows `:26`/`:28`/`:143`) and the matrix
breadcrumb (`verification-matrix.md:379` now `PENDING-ITEM7 · [ITEM7-PGD06]`). **Item 7's remaining
job:** reconcile/retire the `verification-matrix.md:379` REQ-PGD-06 PASS row (its pinning tests are
gone) and confirm REQ-PGD-08's `:28` mention was cleared (it was). Item 8's
fork-B deletes `ParameterGroupDeriver.get_default_value()` when the method is confirmed
dead (only its own conformance tests call it). When that happens, Item 8 updates the
reference doc in the same change (doc-17 rows `:26`/`:28` + prose `:143`, per R1) and
leaves a breadcrumb on the matrix, but the **matrix PASS-row re-frame is Item 7's** (it
owns the verification matrix). Item 7 must, at its spec: check whether Item 8 deleted the
method (read `cleanup-debt/` close-out); if so, re-frame or retire `verification-matrix.md:379`
(REQ-PGD-06, currently PASS verified-by `test_parameter_group_deriver.py` — those tests are
gone) and reconcile REQ-PGD-08's `get_default_value` mention (`:28`). If Item 8 kept the
method, this entry is a no-op — retire it. **Item 7 required reading must include this
entry.**

**Also for Item 7's matrix sweep (Item 8, Row D):** Item 8 added a new PASS row
**REQ-AST-10** to `verification-matrix.md` (`_walk_aggregation_ast` dispatches literals
before the invocation catch-all, verified by `test_agg_literal_dispatch.py`). Matrix
*additions* are in-item per R1; this is flagged only so Item 7's reconciliation sweep sees
the new row and does not treat it as an orphan.

---

## Completed

| Epic | Completed | Duration | Notes |
|------|-----------|----------|-------|
| [UPSTREAM-FINDINGS] Upstream Findings Remediation & Plant-Idiom Support | 2026-07-06 | ~2 days (orchestrated) | All 12 items landed and audited PASS; merged as PR #3. Fixed SC-1–SC-11 + 6 research defects; staged cross-part wiring; snapshot CLI; agentic-mbse sync. Residue (10 V11 offenders, assert-constraint silence, F2/F4) shaped into PIPELINE-TRUTH. See `epic_upstream_findings.md`. |
| [COST-PATTERN] Costed Component Pattern Support | 2026-02-22 | ~12 days | 41 items completed: full conformance test suite (C01-C27, X01-X02), Phase 7 structural refactors, bug fixes (7, 11), docs consolidation. |
| [ATTR-EXPR] Attribute Expression Capture | 2026-02-09 | ~2 days (Items 1-5) | FORMULA computed attributes generate synthetic pipeline modules. 5-way classification scheme. ADR-004/005 formalized. 285 tests, 0 failures. |
| [EXPR-CODEGEN] Expression-Aware Code Generation | 2026-02-08 | ~8.5 days | 15/15 solar_battery, 19/21 CATF auto-implemented. 167 tests, 0 xfail. |

---

## Ideas / Future Considerations

- ~~**Aggregation-literal dispatch bug (from UPSTREAM-FINDINGS Item 6, SC-6).**~~
  **✅ RESOLVED by PIPELINE-TRUTH Item 8 (Row D), 2026-07-06.** `_walk_aggregation_ast`'s
  literal branch was hoisted above the invocation catch-all (the executable-path twin of the
  Item-6 `reconstruct_expression` fix). Reproduced RED first on a new literal-bearing fixture
  (`agg_literal_probe`: `sum(module.cost) + 5.0`), GREEN after; all 23 existing v2 corpora
  byte-identical (only `captured_at` timestamps moved, reverted). Governed by **REQ-AST-10**
  (doc-19 + `verification-matrix.md`), verified by `test_agg_literal_dispatch.py`. The doc-19
  known-deviation note is re-framed to "conforms" and handed to Item 10's caveat sweep for
  final removal.
- **Constraint-reconstruction coverage (from UPSTREAM-FINDINGS Item 6, SC-6).**
  `reconstruct_expression` also serves constraint text, but constraint expressions are not
  captured in extraction snapshots (the Item-6 design's Appendix-A #4 wrongly assumed the
  catf_mfe divertor constraint `(surface_area_inner + surface_area_outer)` would appear in
  the snapshot; it does not — 0 occurrences). The paren/literal fix applies to constraint
  text too but has no snapshot-level regression coverage. Add a test that exercises
  constraint reconstruction directly if that coverage is wanted.
- **Stale-fixture snapshot refresh (from UPSTREAM-FINDINGS Item 9).**
  *→ Candidate rider for PIPELINE-TRUTH Item 1 (same live-capture session); decide at its spec.* Three committed
  extraction snapshots drift from current live output but were left untouched by Item 9
  (its live re-capture reverted them to keep INV-5's "exactly four fixtures change"). They
  must be refreshed so the committed corpus ends the epic script-reproducible — deferred,
  not dropped. Run as one stale-fixture-refresh chore in the Item 6 Step-1 style: own
  commit, reviewed diff, and any test updates that assert the stale form. Execute at
  epic close-out.
  - (`ife_plant` was migrated to the canonical form in Item 9's re-capture — no longer
    in this chore's scope.)
  - `wi014_toy`, `self_named_binding_trap` — **path canonicalization only.** Last captured
    at Item 8 (`84ae948`) under the old convention; re-capture normalizes `source_file`
    (repo-relative → model-relative), `design_attributes` keys (repo-relative → absolute),
    and `document_path` (`file:…` → `file:///home/…`). No `design_overrides` / binding
    change — provably orthogonal to Item 9 (0 diff lines on those surfaces).
  - `quoted_owner_formula` — **path canonicalization + a classification shift.** Re-capture
    also drops two `design_attributes` (`net_margin`, `total_payout`), which now classify as
    computed attributes instead. Likely cause: post-Item-7 computed-attribute classification
    behavior reaching this Item-6-vintage snapshot (`346cf47`). The refresher should review
    this reclassification deliberately — confirm `net_margin`/`total_payout` SHOULD be
    computed, not design attributes — rather than wave the diff through. The repo already
    flags this fixture's path drift in `scripts/capture_extraction_snapshots.py:56-60`.
- InvocationExpression / function call support (sqrt, min, max whitelist)
- SelectExpression / if-then-else support (piecewise functions)
- EXPOSE_COMPUTED decomposition (calc output + arithmetic, deferred from ATTR-EXPR)
- Non-uniform array instances (flat expansion strategy for arrays with per-element parameters)
- Body-assignment expression capture (P3, M-lift; deferred from UPSTREAM-FINDINGS Item 3 / SC-2). For the `return attribute y : Real; y = expr;` form, wire the direction-None `member_expressions[y]` (the body assignment) into `output_expression_asts[y]` so `y` auto-implements instead of degrading to a `NotImplementedError` stencil. Inline `return y : Real = expr` already auto-implements, and the A-2 stencil fix steers modelers to the inline form, so this is low value — it restores auto-impl only for the deprecated body-assignment pattern.
- **fusion-tea whole-plant cross-part wiring — PROMOTED (2026-07-06).** This P1 item was
  mis-shelved under Ideas; it is now **PIPELINE-TRUTH Items 1–3** (`epic_pipeline_truth.md`):
  the 10 remaining V11 offenders, the extended `spec_chain_twolevel` acceptance fixture,
  zero-offender fusion-tea generation, and the run-C ($270.12/MWh) reproduction + workaround
  retirement. Mechanism evidence (offenders reconciled 1:1, bridge reproduction bit-exact):
  `~/1cfe/fusion-tea/work/active/20260706_upstream-fix-verification/report.md` and
  `.project/research/20260706_pipeline-truth-discovery.md` §D6.
- **Two-level specialization — `attribute :>>` extraction gap (P3; from UPSTREAM-FINDINGS Item 10,
  D-F).** *→ The validation WARNING half is built by PIPELINE-TRUTH Item 9; the extraction
  relaxation itself stays deferred.* A value-carrying redefinition authored as `attribute :>> attr = <expression>` (an
  AttributeUsage) is silently dropped at extraction — `_extract_single_redefinition`
  (`hierarchy_resolver.py`) only scans ReferenceUsage members — so `hierarchy_data.redefinitions`
  comes back empty and the specialized-def resolver has nothing to read. Item 10 did NOT relax
  this: fusion-tea uses only the bare `:>> attr = value` form (86 occurrences, zero
  `attribute :>>`; the real gamma edge is `hif_driver.sysml:82 :>> cost_per_joule = meier_cost.gamma`).
  Recorded as an agentic-mbse guidance/validation candidate for Item 12 (teach the bare form; warn
  when an `attribute :>>` carries an expression RHS), not a codegen change.

### PIPELINE-TRUTH Item 5 — Silent-Failure Hardening close-out filings (2026-07-06)

- **[D3-HYGIENE-TAIL]** — consolidated hygiene entry (pointer: `.project/research/20260706_pipeline-truth-discovery.md` §D3). The benign-leaning silent sites not folded into a family fix: loader `.get` defaults on load-bearing fields, naive substring `.replace()` in aggregation compile, `type_map` "Any" exit-point skip, registry alias-rewrite no-not-found branch. Each is low blast-radius; batch them into one hardening pass. (Dead `_check_semantic_match` is Item 8's dead-code sweep — cross-referenced, not filed twice.)
- **[MULTIHOP-CHAIN-PARSE]** — full multi-hop chain parsing follow-on (from D3-2). `extract_feature_chain_segments` (`expression_utils.py`) already yields all segments; Item 5 uses it for the COUNT only (loud-reject 3+-seg chains). Building the resolved multi-hop path is new capability — cheap (helper exists), unblocks deep cross-scope chains, and would let `deep_cross_scope_probe`'s Pattern-A pin assert a *resolved* chain instead of a loud rejection. Argued at Item 5 design; deferred as new-capability, not this item.
- **Item-9 (agentic-mbse lockstep) impact accumulation from Item 5.** New diagnostics that agentic-mbse guidance/validation should teach & check: (1) the totality/uniqueness/exception invariants (INV-1..INV-5) as new-dispatch/lookup-site review rules; (2) `extract_feature_refs` under-report (D3-9 tripwire) — a non-literal AST root yielding zero refs is a traversal gap in agentic-mbse; (3) `str(direction)` repr and the non-float entry-point (SC-5) shape as modeling-guide anti-patterns. Recorded for Item 9 per R2; not implemented here.
