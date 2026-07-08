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
| [PUSH-DOWN] agentic-mbse Push-Down Design | Design ready | Move reusable SysML semantics (~875 lines) from sysml-codegen extraction/ into agentic-mbse/sysml/. Phase 1 (LOW risk): expression_utils + qualified_names. Phase 2 (MEDIUM risk): hierarchy + aggregation. **Sequencing (updated 2026-07-06): start after TRUTH-DEBT (`epic_truth_debt.md`) lands.** The earlier ruling (after PIPELINE-TRUTH Items 5 & 8) is superseded: TRUTH-DEBT Items 1 (F4 cutover / `input_resolver` consolidation), 2 (multi-hop, touches `expression_utils` chain-follow), and 6 (D3 hygiene tail, touches loader / aggregation-compile / registry extraction) all edit the same extraction/resolution surfaces the push-down would move — so PUSH-DOWN now additionally waits on those three, so the moved code is born correct. See `.project/concepts/agentic-mbse-push-down-design.md`. |

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

### [TRUTH-DEBT] Truth-Debt Retirement — the PIPELINE-TRUTH follow-on ledger

**Filed 2026-07-06** as `epic_truth_debt.md`. **Status: Draft.** Estimated ~7–9.5 days (6
items). Retires the work PIPELINE-TRUTH deliberately filed rather than rush: the F4
aggregation-resolution cutover, resolved multi-hop chain support, the three matrix test-gaps,
the inherited-attr classifier fix, the matrix sweep residue, and the D3 hygiene tail. No
discovery sweep — every item carries implement-time evidence (probes, pins, filings with
file:line). Carries forward R1–R4 verbatim. **Sequencing: lands before PUSH-DOWN** (Items 1/2/6
touch extraction/resolution surfaces PUSH-DOWN moves — moved code is born correct).

Items (each absorbs a filing below):
- [ ] Item 1 — F4 aggregation cutover (+ `[GB-PARAMGROUPS-TYPING]` folded in), lands first
- [ ] Item 2 — resolved multi-hop chain bindings
- [ ] Item 3 — matrix test-gap authoring (DM-08, RES-05, RES-08)
- [ ] Item 4 — inherited-attr classifier fix (flip the 5 xfails)
- [ ] Item 5 — matrix sweep residue
- [ ] Item 6 — D3 hygiene tail

See `.project/backlog/epic_truth_debt.md`.

### [SYNC-F3] Shape-B leaf-collision filename edge (UPSTREAM-FINDINGS Item 12, F3)

**Source**: alias-surfacing (Item 11) audit Obs. 2. Two distinct shape-B owning parts that
share a leaf name and expose the same alias to different channels produce the same output
filename `{instance_path}__{alias}.json` — a collision codegen does not yet disambiguate.
Not triggered by any in-repo fixture. File to disambiguate (e.g. qualify by owning-part
path) before a real model hits it.

**PIPELINE-TRUTH Item 9 disposition (S-F3): KEEP FILED.** No model hits the leaf-collision
edge; nothing to build under Item 9's guard. Revisit when a real model produces two shape-B
owning parts that share a leaf and expose the same alias.

### [SYNC-F4] Redefinition / design_override name surfacing (UPSTREAM-FINDINGS Item 12, F4)

**Source**: alias-surfacing (Item 11) release-notes §impact. `:>>` and design-override names
resolve as channels but are not EXPOSE_PURE-sourced, so they do not surface as named
outputs. Decide whether these names should surface (mirror of D6/EXPOSE surfacing) or stay
internal.

**PIPELINE-TRUTH Item 9 disposition (S-F4): KEEP FILED.** No consumer needs
`:>>`/design-override names surfaced as named outputs today. Revisit if a downstream consumer
(e.g. a report or a cross-part binding) needs them exposed.

### [SYNC-F5] Positive unresolvable-warning test (UPSTREAM-FINDINGS Item 12, F5)

**Source**: alias-surfacing (Item 11) audit Obs. 1. Item 11's INV-6 "unresolvable refs still
warn" leg has no positive live assertion. Add a test that asserts an unresolvable ref emits
its warning. Opportunistic — cheap to add in sysml-codegen's test suite.

**PIPELINE-TRUTH Item 9 disposition (S-F5): DISCHARGED.** Verified against Item 5's landed
tests. The old `unresolvable_attr_probe` fixture was *absorbed* by Item 9's plain-usage-override
fix (`:>> local_val = 5.0` is now captured, so it resolves). The positive loud-on-gap proof is
re-anchored on `chain_override_probe`: `tests/unit/test_uncovered_params.py::test_collector_pins_chain_override_probe`
(an unresolved calc-output ref stays LOUD in the uncovered-params result) and
`::test_reconcile_raises_v11_on_wired_gap` (V11 raises on the wired-valueless gap). The INV-6
silent-on-clean leg is covered by `tests/unit/test_silent_failure_family2.py`
(`test_d34_clean_report_no_warn`, `test_d313_all_known_no_warn`). No new test needed.

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

**Absorbed into TRUTH-DEBT (`epic_truth_debt.md`) Item 1, 2026-07-06** — with `[GB-PARAMGROUPS-TYPING]`
folded in (same graph_builder group-assembly region). Lands first among aggregation-resolution items.

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

### [ITEM7-MATRIX-TEST-GAPS] Three REQ rows lack a pinning test — P3, test-coverage

**Absorbed into TRUTH-DEBT (`epic_truth_debt.md`) Item 3, 2026-07-06.**

**Filed by PIPELINE-TRUTH Item 7, 2026-07-06.** The matrix reconciliation dispositioned
most UNTESTED rows by cross-citing an existing component test, but three claims have no
honest test to cite and are left UNTESTED with an argument in the matrix:

- **REQ-DM-08** — "name fields with semantic format constraints SHALL use NewType wrappers,
  not bare `str`." The wrappers exist (`core/identifier_types.py`) but no test asserts the
  relevant model fields are *annotated* with them. Needs a small static test (assert the
  wrappers are `NewType` and the target fields use them).
- **REQ-RES-05** — "the orchestrator SHALL be a linear sequence: classify → build modules →
  rebuild groups → toposort → validate." `test_orchestrator.py::test_step_ordering_call_sequence`
  pins only the OUTER `build_pipeline_context` DAG order (REQ-ORCH-01), a different function.
  No test pins `build_computation_graph`'s internal sequence.
- **REQ-RES-08** — "consumer scope derivation SHALL apply to ALL resolution paths." Per-path
  derivation is verified (aggregation REQ-IR-07, CalcUsage-CHAIN REQ-DRA-04) but no single
  test pins the cross-cutting invariant. Needs a new independently-anchored test enumerating
  the paths (R1 ban: expectation written independently, not computed by the code under test).
  Item 1's cross-part fixtures are substrate.

None is feature work — all three are test-authoring. Kept out of Item 7 (matrix-truth budget;
new-test authoring, not matrix reconciliation).

### [ITEM7-CLASSIFIER-FIX] Inherited-attr EXPOSE_COMPUTED misclassification — RESOLVED (TRUTH-DEBT Item 4)

**✅ LANDED by TRUTH-DEBT Item 4, 2026-07-07.** Step-2b widened to prefix-match any ancestor
PartDef QN (`computed_attribute_extractor._ancestor_part_qns`); snapshot re-captured (5 flips +
a depth-2 case); the xfail site deleted for a positively-asserting 7-row table (REQ-CA-12); D5
graph-builder diagnostic added. **The "loud" framing below was corrected to "silent no-op"** —
the misclassification dropped silently at `graph_builder.py:269-288`, it was never a loud reject.

**Absorbed into TRUTH-DEBT (`epic_truth_debt.md`) Item 4, 2026-07-06.**

**Filed by PIPELINE-TRUTH Item 7, 2026-07-06.** `test_computed_attributes.py::TestInheritedAttrClassification::test_misclassification_documented`
xfails N inherited-attribute patterns classified EXPOSE_COMPUTED where FORMULA is correct: an
inherited attribute's QN resolves to the **supertype** namespace, which defeats the classifier's
Step-2b `owning_part_qn` prefix check (`test_computed_attributes.py::test_inherited_refs_have_supertype_qn`
pins the root cause). **Re-frame chosen over fix in Item 7:** the misclassification is *loud*
(EXPOSE_COMPUTED rejection, not silent wrong output), no fusion-tea model hits it, and the fix
(supertype-namespace QN resolution vs the Step-2b prefix check) is out of proportion to a
matrix-truth item. Fix scope: teach the Step-2b check to accept a supertype-namespace QN for an
inherited attribute. When landed, the xfail cases flip to PASS (xfail strict=False).

### [DM08-MODEL-FIELD-TYPING] NewType-annotate the resolution-model name fields — P3

**Filed by TRUTH-DEBT Item 3 (Route A ruling), 2026-07-07.** REQ-DM-08's original text
claimed the *model fields* use NewType wrappers; at HEAD they are deliberately bare `str`
(`resolution/models.py`: `EntryPoint.qualified_name`, `InputSource.qualified_name` /
`producer_channel`, `ModuleOutput.channel_name`), and `09-data-models.md` documents the
field↔format table with this deferral. Item 3 pinned the *enforced surface* (OutputRegistry
dicts + `make_*` constructors, `test_dm08_enforced_surface.py`) and reframed the REQ text to
match (INV-B). **Scope**: annotate the documented model fields with their NewTypes
(field↔format table in doc 09 is the target list), update the DM-08 row + doc 09 note, and
extend the AST-scan test to cover the widened surface. Pure typing churn — zero runtime
change (NewType is erased), but touches many models; mypy must not regress.

### [TRUTH-DEBT-INHERITED-FORMULA-COMPILE] Compile inherited-attr FORMULAs into real modules — P3

**Filed by TRUTH-DEBT Item 4, 2026-07-07.** Item 4 fixed *classification* — an attribute
referencing only inherited/local attrs now classifies FORMULA. But these stay
`MANUAL_REQUIRED` and produce **no pipeline module**: the compiler's `input_names` is built
from `owned_members` (`computed_attribute_extractor.py:188-191,247-249`), which per SysML v2
excludes inherited attrs, so an inherited ref compiles to `UNSUPPORTED` →
`compilability=MANUAL_REQUIRED`, `compiled_expression=None`. The D5 graph-builder diagnostic
now makes that no-module outcome **loud** at generation, but it does not build the module.
**Scope**: thread the ancestor PartDefs' attribute names into the FORMULA compiler's
`input_names` (mirroring the ancestor-QN walk already added for classification) so an
inherited-attr FORMULA compiles to a real module. Out of scope for Item 4 (classification-only,
D1). No corpus model hits the shape today, so no baseline moves.

### [TRUTH-DEBT-IFE-PLANT-CHAIN-STALE] `ife_plant` snapshot latently stale (pre-existing classifier drift) — P3

**Filed by TRUTH-DEBT Item 4 B3 check, 2026-07-07; attribution corrected by Item 2's audit
(multihop-chain/audit.md).** While reproducing B3 for Item 4, one **orthogonal** drift
surfaced: `ife_plant` `radial_build.magnet_volume_total` is committed as `expose_pure` but
live extraction now classifies it `expose_chain_tentative`. Confirmed pre-existing on the
pre-Item-4 classifier (`0f75062`). The original filing attributed it to Item-2 multi-hop
machinery; **Item 2's audit refuted that** — Item 2's entire source diff is
`usage_extractor.py` + `dependency_backtracker.py`, neither on the attribute/classifier
path, and it provably cannot produce the `expose_pure → expose_chain_tentative` transition.
The drift is prior-epoch classifier staleness (pre-Item-2, from `891cf8e`), latent until
`ife_plant` is re-captured. NOT an Item-4 effect either. Latent: the conformance suite reads the committed snapshot, so it is green
today; it would surface on a future `ife_plant` re-capture. **Scope**: re-capture `ife_plant`
and review the resulting diff (expect the one chain-classification flip and its downstream
effects), landing it as a reviewed R3 diff. Deliberately not done in Item 4 (mixing Item-2
drift into the Item-4 change would break the byte-identity carve-out).

### [ITEM7-MATRIX-SWEEP-RESIDUE] Deep-read sweep findings — P3, test-coverage / matrix-honesty

**Absorbed into TRUTH-DEBT (`epic_truth_debt.md`) Item 5, 2026-07-06.**

**Filed by PIPELINE-TRUTH Item 7, 2026-07-06.** The leashed ~175-row deep-read sweep (Phase 8)
ran to substantial completion via delegated per-family readers (~167 qualifying strong-word PASS
rows examined). Every finding is a **PASS-but-pins-narrower** row — the cited test passes and the
behavior is real, but the test pins less than the full requirement text (INV-B). **None is a
correctness lie**; none is feature work. Three were reframed in-matrix already (SR-03 6-case,
EXT-07, EXT-14). The rest are filed here rather than reframed/strengthened in-item (matrix-truth
budget; test-authoring, not reconciliation). Each carries its disposition; fix per row when the
owning component is next touched.

**Reframe REQ text to what the test checks (cheap, byte-safe):**
- **REQ-CA-01** — test uses the 6-member enum set (incl. transient `EXPOSE_CHAIN_TENTATIVE`); INV-F/no-tentative-survives is REQ-CA-10's job, not pinned here. Reframe: "assign each attr exactly one enum member."
- **REQ-CA-06** — LITERAL assignment path never exercised (only FORMULA/EXPOSE_ALIAS). Reframe to those two, note LITERAL is design-attr/entry-point path.
- **REQ-AST-03** — cited test pins only the FCE<OE<FRE ordering clause, not literal-before-catch-all (that's REQ-AST-08). Reframe to the ordering clause.
- **REQ-DM-03** — compares field-NAME sets only (not type/optionality). Reframe "field name lists," or strengthen.
- **REQ-DM-04** — checks source file only, not parent class. Reframe "importable from documented source file," or strengthen.
- **REQ-OSR-03** — template-fidelity only (both sides from same graph), not SysML-source match. Reframe or add the output-registry PQN test to the citation.
- **REQ-SR-06** — grep-only static, no behavioral regen. Reframe to "all module types route through the single `_generate_stencils()`."
- **REQ-SNAP-18** — vacuous grep: `generation_timestamp` token exists nowhere in repo; the template-var premise is stale (var removed). Reframe to a regression guard.
- **REQ-PMM-04** — asserts valid non-empty Python, not byte-identity vs pre-migration baseline (the doc's `diff -r` gate ran once at cutover). Reframe to the testable property.
- **REQ-PMM-05** — phased-sequence (add/create/deprecate/remove) is process, not a testable module property; test pins coexistence only. Reframe to importable-variants + unchanged-fields.
- **REQ-AS-02** — Strategy-1-before-2 short-circuit shown only via a disjoint fixture (no dual-match partdef); precedence inferred. Reframe or add a dual-match case.

**Strengthen test (needs a new/expanded assertion; risks touching baselines — do under byte-identity gate):**
- **REQ-EC-04** — tests call `python_ast.parse` themselves on the compiler's output; the compiler's internal parse-and-raise gate (`expression_compiler.py:217-223`) is unpinned (delete it and every EC-04 test still passes). Add a case that forces invalid emitted Python and asserts `CompilationError`.
- **REQ-AS-06** — resolve-before-register gate wrapped in `if result is not None:` + `resolved_count>0` floor; 40 of 41 aliases could be unresolvable and pass. Assert every registered redefinition alias resolves.
- **REQ-EPC-07** — purity test deep-compares only 2 of 5 inputs. Deep-compare all five against fresh copies.
- **REQ-ORCH-05** — `len(scoped)>=len(expr)` aggregate count; one over-producing expr masks another scoping to zero. Assert every expression id appears in the scoped output.
- **REQ-ORCH-02** — source call-order only; the in-place binding_type mutation-visible-to-backtracker half is unpinned. Assert a virtual binding's `binding_type` is actually mutated.
- **REQ-ORCH-06** — source-order proof only; the "computation_graph is SSOT / generation boundary" half is really pinned under REQ-PIPE-07's `TestGenerationBoundary`. Re-cite or assert `ctx.computation_graph` identity.
- **REQ-OR-02** — despite its name (`test_no_single_resolve_method`) never asserts `not hasattr(registry, "resolve")`; omits the 4th lookup `scoped_alias_lookup`. Add the negative assertion.
- **REQ-OR-03** — wraps `caplog.at_level(WARNING)` but never asserts a warning record for the first-wins alias collision. Assert the record.
- **REQ-PGD-03** — "one group per file" pinned only as `>=` lower bound; over-grouping passes. Assert `== distinct source-file count`.
- **REQ-REG-06** — circular expected-set: derives expected types from the SUT helper `_collect_exit_point_primitive_types`. Derive the expected set independently from the graph.
- **REQ-CA-07** — self-reference exclusion vacuous (no self-referencing fixture; checks a downstream string). Add an `x = x + 1` fixture and assert on `input_names` directly.
- **REQ-CA-11** — pins only the registered→silent case, not unregistered→warns-naming-real-cause. Add the unregistered shape-A case.
- **REQ-EPC-05** — "exactly one ParameterGroup" — no cross-group uniqueness check. Add it.
- **REQ-BASE-04** — parametrizes 4 models but 10 baseline dirs have `computation_graph.json`. Glob all.
- **REQ-DM-09** — pins the 4 field names, not serialization-non-exclusion / INV-5 sort / INV-3 validation. Strengthen; also its `test_graph_assembly.py` citation has no REQ-DM-09-marked method (docstring only).
- **REQ-SR-05** — backup mechanism tested in isolation, not the "before every regen/upgrade" ordering. Drive the regen path.
- **REQ-PMM-02** — pins ModuleInput desc/default + ModuleOutput desc/unit, but not `ModuleOutput.default_value` (a real field). Add it.

**Fix citation only (traceability — behavior IS pinned, under a different REQ/test):**
- **REQ-BASE-01** — the real full-JSON baseline compare lives in `test_graph_assembly.py::TestBaselineComparison` (marked REQ-GA-01); the cited `test_baselines.py` only checks 3 keys exist. Re-cite/mark.
- **REQ-NC-08** — FORMULA module_eqn/channel leg pinned by `test_formula_quoted_owner.py` (not cited). Add it.
- **REQ-VBR-10** — the "else leave it as-is" clause is pinned by `test_self_named_binding_trap.py::test_self_named_binding_resolves_to_own_param` (not cited). Add it.
- **REQ-HR-08** — the "`part redefines` keeps all RHS types" leg is pinned by `test_virtual_binding_rewrite.py::TestChainOverrideFixtureCoverage` (marked REQ-VBR-04). Add a `# REQ-HR-08` marker there.
- **REQ-PY-08 / REQ-DM-09** — cited methods carry the REQ only in a docstring, no `@pytest.mark.req`; matrix tooling may not bind them.

**Residue (register discipline — NOT swept, named with count):** the sweep examined ~167 of the
~213 qualifying strong-word/diagnostic/count rows. ~46 qualifying rows were not independently
deep-read this pass (primarily the EPC diagnostics, LVP literal-propagation, and GA topo-sort
internals judged adequate on their family reader's spot-check but not line-by-line). These are
**not** asserted swept — a future pass completes them. No silent truncation.

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

**Absorbed into TRUTH-DEBT (`epic_truth_debt.md`) Item 1, 2026-07-06** — folded into the F4
cutover (same graph_builder group-assembly region).

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

### [DOTTED-LEAF-PART-BLIND] Tighten the dotted-leaf alias match to be part-aware (D6 edge) — P3

**Filed by PIPELINE-TRUTH Item 10, 2026-07-06.** The `.`-suffix branch of
`_chain_sibling_aliases_aggregation` (`extraction/hierarchy_resolver.py`) matches any dotted
`source_path` whose leaf equals the aggregation attribute, **regardless of which part it
references** — so `parent.capital_cost` matches `attribute_name="capital_cost"` on an unrelated
part. It could produce a spurious alias for a hierarchical CHAIN redefinition. **Item 10
disposition: keep the current behavior.** No supported model triggers the edge; the behavior is
pinned by `tests/unit/test_hierarchy_resolver.py::TestDottedLeafAliasMatch` (doc-25's dotted-leaf
section), so any tightening is a red-then-green change. Tightening (make the match part-aware) is a
code change, deliberately left un-done at epic close — pick it up if a real model produces the
spurious-alias collision.

### [ITEM7-PGD06] Re-frame REQ-PGD-06's matrix PASS row — RETIRED (Item 7 consumed)

**Retired 2026-07-06 by Item 7.** Confirmed `get_default_value` is deleted (0 hits in `src/`
and `tests/`). REQ-PGD-06 re-framed in the matrix from the PENDING-ITEM7 row to an
UNTESTED row with its argument: the numeric default now resolves inline via
`_parse_default_value` in `_derive_from_*` (live), but it is a side-output of grouping
(pinned by REQ-PGD-01/08) and not independently asserted — the standalone accessor that
pinned it is gone. REQ-PGD-08's `get_default_value` mention in doc-17 was already cleared by
Item 8. Superseded.



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
| [PIPELINE-TRUTH] The Generated Package Is the Truth | 2026-07-06 | ~2 days (orchestrated) | All 10 items landed and audited PASS. **The generated package is the truth**: fusion-tea generates/wires/executes end-to-end at TRUE ZERO V11 offenders (SVM value-fill, Item 2); run-C lcoe reproduces bit-exact ($270.1211779380445) and every workaround deleted upstream (Item 3); constraint drop report subtype-aware incl. `assert` (Item 4); 13 silent-failure findings fixed by family (Item 5); 25 self-referential tests re-anchored (Item 6); matrix 253 = 249 PASS + 4 UNTESTED-argued + 0 DEFERRED, F2/F4 resolved by decision (Item 7); dead code cleared + REQ-AST-10 (Item 8); agentic-mbse taught+checked (Item 9); docs+explainer refreshed (Item 10). Follow-on filings kept below (outlive the epic): `[ITEM7-F4-CUTOVER]`, `[ITEM7-MATRIX-TEST-GAPS]`, `[ITEM7-CLASSIFIER-FIX]`, `[ITEM7-MATRIX-SWEEP-RESIDUE]`, `[SANITIZER-MERGE]`, `[SC11-IMPORT-REWRITE]`, `[GB-PARAMGROUPS-TYPING]`, `[DOTTED-LEAF-PART-BLIND]`, SYNC-F3/F4. See `epic_pipeline_truth.md` (Lessons Learned). |
| [UPSTREAM-FINDINGS] Upstream Findings Remediation & Plant-Idiom Support | 2026-07-06 | ~2 days (orchestrated) | All 12 items landed and audited PASS; merged as PR #3. Fixed SC-1–SC-11 + 6 research defects; staged cross-part wiring; snapshot CLI; agentic-mbse sync. Residue (10 V11 offenders, assert-constraint silence, F2/F4) shaped into — and now closed by — PIPELINE-TRUTH. See `epic_upstream_findings.md`. |
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

- **[D3-HYGIENE-TAIL]** — **absorbed into TRUTH-DEBT (`epic_truth_debt.md`) Item 6, 2026-07-06.** Consolidated hygiene entry (pointer: `.project/research/20260706_pipeline-truth-discovery.md` §D3). The benign-leaning silent sites not folded into a family fix: loader `.get` defaults on load-bearing fields, naive substring `.replace()` in aggregation compile, `type_map` "Any" exit-point skip, registry alias-rewrite no-not-found branch. Each is low blast-radius; batch them into one hardening pass. (Dead `_check_semantic_match` is Item 8's dead-code sweep — cross-referenced, not filed twice.)
- **[MULTIHOP-CHAIN-PARSE]** — **absorbed into TRUTH-DEBT (`epic_truth_debt.md`) Item 2, 2026-07-06.** Full multi-hop chain parsing follow-on (from D3-2). `extract_feature_chain_segments` (`expression_utils.py`) already yields all segments; Item 5 uses it for the COUNT only (loud-reject 3+-seg chains). Building the resolved multi-hop path is new capability — cheap (helper exists), unblocks deep cross-scope chains, and would let `deep_cross_scope_probe`'s Pattern-A pin assert a *resolved* chain instead of a loud rejection. Argued at Item 5 design; deferred as new-capability, not this item.
- **Item-9 (agentic-mbse lockstep) impact accumulation from Item 5.** New diagnostics that agentic-mbse guidance/validation should teach & check: (1) the totality/uniqueness/exception invariants (INV-1..INV-5) as new-dispatch/lookup-site review rules; (2) `extract_feature_refs` under-report (D3-9 tripwire) — a non-literal AST root yielding zero refs is a traversal gap in agentic-mbse; (3) `str(direction)` repr and the non-float entry-point (SC-5) shape as modeling-guide anti-patterns. Recorded for Item 9 per R2; not implemented here.

### TRUTH-DEBT Item 6 — D3 Hygiene Tail Phase 0 filings (2026-07-07)

- **[D3-HYGIENE-TAIL-SITE4-TRANSITIVE-ALIAS]** — **reclassified, not fixed, at Item 6 Phase 0.**
  Site 4 (`orchestration/output_registry_builder.py:353-367`, Phase 4 transitive design-attribute
  alias resolution) was expected to reproduce only synthetically ("reproduces cleanly" per the
  plan) and get a mechanical sibling-copy `logger.warning` mirroring Phases 2/3. The Phase-0
  corpus-scan gate found instead that the identical unresolved-lookup shape already fires on
  **5 of 15 `SNAPSHOT_MODELS` fixtures today**: `solar_battery_model`
  (`misc_hardware_cost` → `'allocation_model.total_allocation'`), `wi014_toy`
  (`total_cost` → `'cost_calc.cost'`), `ife_plant` (`volume` → `'volume_calc.volume'`,
  `lcoe` → `'lcoe_calc.lcoe'`), `plant_values` (`plant_cost` → `'cost_calc.plant_cost'`). Root
  cause: these `default_value`s use a short leaf-instance dotted form (`"cost_calc.cost"`) but
  all three of Phase 4's lookup keys are full-EQN forms — none ever match. A mechanical WARN
  here would fire on all 5 currently-clean fixtures, breaking INV-6 [HARD]. No downstream binding
  in the corpus references any of the 5 orphaned names, so the gap has no observable effect on
  current generated output — which is exactly why the mechanical fix would have been a false-fire,
  not a true one.

  **This is the same underlying gap already discovered and deliberately deferred** at
  `analysis/parameter_groups.py:672-682` (`_derive_from_design_attributes`), where a
  present-but-unparseable design-attribute default is silently dropped from the derived JSON
  parameter list. That code's own comment (citing SC-5/D3-12) states a naive WARN there
  "over-fires on legitimate chain/reference defaults... resolved elsewhere, breaking INV-6," and
  that the correct fix "needs the EP-omission membership check across the full derivation" —
  deferred, and never filed until now.

  **Filing:** a correct fix spans both sites (an EP-omission / cross-derivation membership check
  that only warns when a transitive default resolves in *neither* Phase 4 *nor* the parameter-group
  JSON path) — design-level work, not a single-choke mechanical hygiene fix. Out of Item 6's scope.
  Evidence: `.project/active/hygiene-tail/probes/probe_site4_output_registry.py`,
  `.project/active/hygiene-tail/probes/verdict.md`.

### [ITEM5-SWEEP-RESIDUE-OVERFLOW] D7 sweep completion — 21 rows read-spot-checked, not line-by-line deep-read — P3, test-coverage / matrix-honesty

**Filed by TRUTH-DEBT Item 5 (matrix-sweep-residue), 2026-07-08.**

Step 5.0's D7 qualifier grep (`SHALL|ALL|every|never|exactly|warn|fire|count`, case-insensitive)
across all 259 current matrix rows returns 232 qualifying rows. Subtracting the ~167 the
Item-7 register already swept and the 33 rows this item dispositioned in Phases 1-4 (17
strengthen + 11 reframe + 5 cite) leaves **32 rows** as the concrete residue (the spec's ~46
estimate included rows this item's own Phase 2 work re-verified/absorbed).

Of those 32, the 23 in the three named families (EPC 8, GA 8, LVP 9, minus REQ-EPC-05/07
already strengthened in Phase 2 = 21 unread here) were spot-checked (not individually
line-by-line deep-read): REQ-GA-04's `TestNoSelfDependency` and REQ-LVP-04's LocalTerm-fallback
assertions both read as real, non-vacuous checks matching their row text on inspection. No
correctness lie or feature gap was found in the spot-check, consistent with the Item-7 register's
finding that every prior deep-read row was PASS-pins-narrower, never a lie.

**Stopping rule invoked:** the D7 stopping rule (0 new findings in 40 consecutive rows after the
first 60) was not reached on row-count grounds — this pass stopped short of it, at the item's
remaining implementation budget, having read 2 of 21 representative rows in the named families
(GA-04, LVP-04) plus the row-text/citation check for all 21 during Step 5.0's grep pass. This is
an **honest budget-bound stop**, not a claim the D7 heuristic's row-count threshold was hit --
named separately per the plan's risk-management section (an unread residual vs. a
read-but-too-big-to-fix residual are both named, separately).

**Residue, named exactly:**
- **21 rows** in EPC/GA/LVP families not individually deep-read beyond the spot-check above:
  REQ-EPC-01, -02, -03, -04, -06, -08; REQ-GA-01, -02, -03, -05, -06, -07, -08; REQ-LVP-01, -02,
  -03, -05, -06, -07, -08, -09.
- **11 rows** elsewhere in the qualifying set (the "~21 spread across other families" the spec
  named) not enumerated by REQ id in this filing -- reconstructing the exact list requires
  re-running the Step 5.0 grep minus the 167+33+21 already accounted for; left as a precise
  follow-on rather than guessed here.

**Scope for the follow-on:** re-run the Step 5.0 grep, subtract this item's full disposition
(33 dispositioned + 21 spot-checked here), deep-read the remainder under a fresh D7 budget, land
cheap dispositions (reframe/cite) inline, re-file only genuine budget-exceeding strengthens.
