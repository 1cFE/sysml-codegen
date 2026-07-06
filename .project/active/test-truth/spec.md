# Spec: Self-Referential Test Remediation (PIPELINE-TRUTH Item 6)

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-06
**Complexity:** MEDIUM
**Branch:** pipeline-truth-epic

---

## Problem

A conformance test that computes its own expected value from the same production
call it is checking cannot fail. The value under test and the value it is compared
against come from one code path, so the assertion is `f(x) == f(x)` — true for any
`x`, including a buggy one. The discovery sweep (register §D5, 1,433 tests examined)
flagged 25 such tests: 7 HIGH (structurally unable to fail), 10 MEDIUM (assert a
production identity or re-invoke the gating call), 8 LOW (circular, but the content
is independently pinned by a literal in a sibling test). One of these,
`test_localterm_sibling_agg_output` (REQ-MF-07), is worse than tautological: it can
**pass or skip but never fail** — the most deceptive single finding, because a green
suite hides that it never ran an assertion.

These tests are the verification matrix's own foundation. If they cannot fail, a PASS
row backed by one of them pins nothing. The epic's mission is that the generated
package is the truth and every diagnostic is trustworthy; that collapses if the tests
proving it are self-referential. R1's addition to this epic bans the anti-pattern
going forward (every new/changed diagnostic lands with an independently-anchored
expectation); this item purges the existing instances so the ban starts from a clean
base.

The fix is mechanical and low-risk: every flagged test has a correctly-anchored
sibling in the same suite that hand-transcribes a literal. Replace each computed
expectation with a hand-transcribed literal drawn from a known fixture element (or an
on-disk check where the REQ says "file"), and convert the pass-or-skip test to
pass-or-FAIL.

## Success Criteria

- [ ] All 25 §D5 register entries are dispositioned — fixed, converted, handed off
  (EXT-09 → Item 4), or documented-as-sibling-pinned — with a one-line rationale each
  in the disposition table below.
- [ ] Each **fixed** test demonstrably fails under a deliberate production mutation.
  Spot-check three (one count-tautology, one naming/channel, the MF-07 conversion) by
  perturbing production, confirming red, reverting; record the three in the close-out.
- [ ] `test_localterm_sibling_agg_output` (REQ-MF-07) fails — not skips — when its
  LocalTerm does not resolve to the expected sibling aggregation channel.
- [ ] The mis-anchored REQ-REG-02 test checks import paths against files an actual
  generation run wrote to disk, not against a re-derived path rule.
- [ ] The two SC-6 render-contract pins exist and pass (scientific-notation normalized
  form; one positive `sum(...)` exact render).
- [ ] `tests/conformance/README.md` carries a short "how to anchor a conformance
  expectation" note (the anti-pattern, the fix, the pass-or-skip trap).
- [ ] Full suite green; any test-count change is explained in the close-out (no test
  deleted without a replacement). ruff/mypy not worse than the 21/109 baseline.

## Known Requirements

- **[HARD]** Every fixed test's expected value is a **hand-transcribed literal** (or a
  set membership over hand-transcribed literals, or an on-disk `path.exists()` check),
  never a value produced by calling the same production function the test verifies.
  This is R1's banned anti-pattern; it is the definition of "anchored" for this item.
- **[HARD]** Anchor literals are drawn from **known fixture elements** read from the
  committed snapshots (`tests/fixtures/{solar_battery_model,catf_mfe_model}/extraction_snapshot.json`)
  and design sources — license-free, so the pins run without a syside license. The
  concrete literals are enumerated per test below.
- **[HARD]** REQ-EXT-09 (H1) is **out of scope** — Item 4 (subtype-enumeration) owns
  its re-anchoring as part of the constraint-report fix. Record the handoff; do not
  touch `test_extractor.py`'s EXT-09 test here.
- **[NEED]** No behavior change. Re-anchoring reveals current behavior, it does not
  alter it. §D5 verified current behavior matches; none of these fixes should require a
  production edit. If one genuinely exposes a bug, stop and file it explicitly (absorb
  into the matching epic item or a BACKLOG entry) rather than bending the literal to
  match wrong output.
- **[NEED]** A test that can only pass or skip is not coverage. Every converted
  pass-or-skip test ends on an unconditional `assert found, ...` so a missing fixture
  element is a FAIL, not a silent skip.
- **[INFERRED]** Where a flagged test is parametrized over multiple models/indices, a
  single hardcoded literal cannot ride the parametrization. Add a dedicated,
  non-parametrized assertion on one named fixture element alongside (or replacing) the
  parametrized recompute — see the aggregation/factory rows.
- **[INFERRED]** The matrix rows for these tests are **not** updated here — Item 7 owns
  the matrix. This item changes test bodies only.

## Disposition of the 25 flagged tests

Grounded in the actual test bodies (read 2026-07-06). "Anchor" = the hand-transcribed
literal that replaces the computed expectation. Line numbers are as-read and are a
starting point; re-confirm at implement.

### HIGH (7)

| # | Test / REQ | File:line | Why it can't fail | Fix / anchor |
|---|---|---|---|---|
| H1 | `test_extractor` EXT-09 | test_extractor.py:~895 | `expected` computed by the impl's own constraint query | **HANDOFF → Item 4.** Not touched here. |
| H2 | `test_req_gen_05_one_json_per_group` GEN-05 | test_gen_json_templates.py:115 | `len(json_files) == len(graph.entry_point_groups)` — both sides are `len(groups)` over a 1:1 producer loop | Assert against literal counts: solar_battery **3**, catf_mfe **8**. |
| H3 | `test_req_gen_05_one_schema_per_group` GEN-05 | test_gen_json_templates.py:135 | same `len==len` for schema files | same literals (3, 8). |
| H4 | `test_req_py_07_json_file_count_matches_entry_point_groups` PY-07 | test_gen_json_templates.py:553 | byte-duplicate of H2's assertion; claims a YAML cross-check it never performs | Assert literal counts (3, 8). **Also fix the true PY-07 twin** `test_entry_fusion_json_count` (test_gen_pipeline_yaml.py:402), same `len==len` over the `entry_fusion` block — literal 3/8. |
| H5 | `test_usage_literal_float_conversion` EPC-03 | test_entry_point_classifier.py:289 | `expected = float(source)` (line 309) recomputes production's `float(entry_point_sources.get(qname))` (graph_builder.py:508-511) | Hardcode input→expected pairs from catf_mfe USAGE_LITERALs: `gross_electric`→**1546.72**, `p_neutron`→**2079.41**, `p_thermal_electric`→**1104.22**; add a synthetic unparseable `"3+4"`→**None**. Keep the independent `isinstance(...float)` check. |
| H6 | `test_module_name_format` MF-01 (aggregation) | test_factory_aggregation.py:208 | `expected = get_module_name(agg.module_eqn)` — the exact call production makes (graph_builder.py:1389) | Dedicated assertion on solar_battery agg idx 0: `module.name == "solarbatterydesign__solar_battery_plant__solar_array__capital_cost"` (note the design prefix is **lowercased** — only a literal catches this). |
| H7 | `test_output_channel_name_format` MF-05 (aggregation) | test_factory_aggregation.py:566 | `expected = get_channel_name(agg.module_eqn, attr)` — production's exact call (graph_builder.py:1644-1647) | Literal idx 0: `channel_name == "SolarBatteryDesign__solar_battery_plant__solar_array__capital_cost__capital_cost"` (the trailing attribute is **doubled** — invisible to a helper-derived expected). |

### MEDIUM (10)

| # | Test / REQ | File:line | Why it can't fail | Fix / anchor |
|---|---|---|---|---|
| M1 | `test_unparseable_default_is_none` (LIBRARY_DEFAULT branch) EPC-03 | test_entry_point_classifier.py:318 | branch gated on `default_value is None` (itself produced by `_get_library_default`) then re-invokes `_get_library_default` (line 353) and asserts it agrees | Transcribe calc-def default → expected: numeric `"0.45"`→0.45, `"1.07"`→1.07, `"171.5"`→171.5; expression default (e.g. `"1.0 / q_eng"`, `"TBD"`)→None. The DA (339) and UL (359) branches of the same test share the disease in weaker form — anchor them too. |
| M2 | `test_req_pgd_05_classify_precedence_matches_index` PGD-05 | test_parameter_group_deriver.py:411 | `expected_group = deriver._generate_group_names(file_path.stem)` — the same method `classify()` calls internally | Hardcode: `classify("SolarBatteryDesign__solar_battery_plant__p_net_mw") == "design_params"`. Also harden the four `classify_returns_group_for_*_index` tests (365-402): they draw `qname` from the index and assert only non-None — replace with named qname → named group (attr→design_params; unbound/literal → library_params). Keep `classify_unknown_returns_none` (404, already a literal negative). |
| M3 | `test_req_pgd_06_default_value_literal` PGD-06 | test_parameter_group_deriver.py:476 | reads `_literal_index[qname][1]` then asserts `get_default_value(qname)` returns that same dict value | Hardcode the two real literal-index entries: `child_count`→**25.0**, `total_child_mass`→**50.0**. Also fix the binding-resolution twin (459): it asserts only `None or isinstance float` — replace with `get_default_value(".._energy_production__p_net_mw") == 0.008` (exercises the real binding→attr resolution). Model: `test_req_pgd_06_default_value_direct_attr` (451, already literal 0.008). |
| M4 | `test_module_eqn_format_solar_battery` AS-07 | test_aggregation_scoping.py:511 | `expected = f"{agg.instance_path}__{agg.expression.attribute_name}"` duplicates the `module_eqn` property's own f-string | Literal per idx: idx 0 `"SolarBatteryDesign__solar_battery_plant__solar_array__capital_cost"`; …; idx 15 `"SolarBatteryDesign__solar_battery_plant__capital_cost"`. Model: `test_module_eqn_issue22` (521, literal). Fold in the identical REQ-AS-03 recompute at line 311 (`expected_eqn = f"..."`). |
| M5–M9 | Five factory-naming tests (composition unverified) | test_factory_calc_usage.py:206, :522; test_factory_formula.py:216, :647; (+ module_type twins :218, :234) | each builds `expected` by calling the production naming helper (`get_module_name` / `get_channel_name` / `derive_module_type`) the factory used | Dedicated non-parametrized literal on a named solar_battery module: calc_usage name `"solarbatterydesign__solar_battery_plant__energy_production"`; calc_usage channel `"SolarBatteryDesign__solar_battery_plant__energy_production__annual_energy_mwh"`; formula name `"solarbatterydesign__solar_battery_plant__p_net_kw"`; formula channel (doubled) `"SolarBatteryDesign__solar_battery_plant__p_net_kw__p_net_kw"`; module_type `"solarbatterylibrary.EnergyProductionCalcModule"` / `"solarbatterydesign.solar_battery_plant.p_net_kwModule"`. **Count note:** the register said "five"; the sweep found six of this exact shape (the two `module_type` recomputes are the likely extras). Disposition all six; the extra is coverage gained, not scope creep. |
| M10 | `test_req_reg_02_import_paths_match_filesystem` REG-02 | test_gen_registry.py:279 | asserts only that each dotted segment is alphanumeric (valid Python path); never compares to `PythonModulePath.from_sysml()` or the filesystem; the sibling `test_module_count_matches_inputs` (320) re-derives the count from the same graph rule | Re-anchor to on-disk truth: generate solar_battery + catf_mfe to `tmp_path` (the integration harness path already used in `tests/integration/test_full_pipeline.py:228-248`), then for each `from pkg.modules.A.B.C import Name` assert `output/modules/A/B/C.py` exists. Example: `…solarbatterylibrary.allocationcostcalc import AllocationCostCalcModule` → assert `output/modules/solarbatterylibrary/allocationcostcalc.py` exists. Note REQ-REG-02's stated behavior currently lives under REQ-REG-05's test (463) — the mis-anchoring is that REG-02 points at a weak syntactic check; do **not** duplicate REG-05, just make REG-02 assert the on-disk match. (Matrix re-mapping is Item 7's.) |

### LOW (8) — per-test judgment (fix if one-line, else document sibling-pin)

The authoritative LOW enumeration lived only in the discovery session transcript; the
list below is reconstructed by re-applying the §D5 LOW heuristic (circular expectation,
content pinned by a literal sibling). **First implement step: reconcile this list
against the transcript's D5 agent output if recoverable; otherwise this reconstructed
set stands.** MF-07 (L2/L3) is named explicitly by the register and is not optional.

| # | Test / REQ | File:line | Judgment |
|---|---|---|---|
| L1 | `test_module_name_parametrized` NC-03 | test_naming_conventions.py:266 | **Fix (one-line-per-row):** replace `assert result == eqn.lower()` with hand-transcribed lowercased literals for the 3 `REAL_EQNS` rows; sibling `test_module_name_is_lowered_eqn` (259) already models it. |
| L2 | `test_localterm_sibling_agg_output` MF-07 | test_factory_aggregation.py:724 | **Convert (rework).** Pass-or-skip → pass-or-FAIL. See detail below. |
| L3 | `test_localterm_expose_alias` MF-07 | test_factory_aggregation.py:753 | **Convert (rework).** Same pass-or-skip shape (a bonus finding beyond the register's named MF-07). See detail below. |
| L4 | `test_all_generators_use_shared_function` GEN-06 | test_type_mapping_consolidation.py:177 | **Document.** Iterates every module/attr; `expected = map_sysml_type_to_python(...)` recomputes the graph's own value. Content pinned by literal type-map siblings (`test_gen_schemas.py:359-381`, `test_gen_module_wrappers.py:488`). Residual value (all generators call the shared fn) is real but weak — record the sibling-pin reliance. |
| L5 | `test_input_types_match_module` GEN-02 | test_gen_module_wrappers.py:306 | **Document.** Template-fidelity vs the graph; pinned by the literal type-map sibling. |
| L6 | `test_input_type_cross_reference_with_graph` GEN-02 | test_gen_module_wrappers.py:444 | **Document** (near-duplicate of L5; note the dedup opportunity). |
| L7 | `test_field_names_match_pipeline_module_outputs` | test_gen_schemas.py:311 | **Document.** Field-name content pinned by the output-registry PQN tests; this only checks the template renders them. |
| L8 | `test_req_gen_04_multi_output_return_type` GEN-04 | test_gen_stencils.py:315 | **Fix if cheap.** `expected = f"tuple[{', '.join(['float']*n)}]"` is self-shaped on `n`, but `"float"` is a literal assumption. Pin one known multi-output module's exact return string; lowest-priority row. |

### Cleared non-findings — DO NOT re-flag

Recorded so the boundary is explicit (register §D5 cleared list):

- **BT-04** `test_every_binding_resolved_solar` (test_backtracker.py:326): `expected =
  total_bindings + total_unbound` counted from **input** snapshot data, not from
  re-running resolution — a real conservation check.
- **dual_resolution parity** (test_dual_resolution.py:118, 187): cross-checks two
  independently-coded paths (backtracker vs `resolve_input`); a divergence fails it.
  (That `resolve_input` is dead is Item 7's axis, not self-reference.)
- **baselines-as-regression-pins** (test_baselines.py): validate against frozen
  committed artifacts, changed only on deliberate regeneration.

## New work beyond the 25 (same style)

### SC-6 render-contract pins (2 NEW tests to ADD)

The adversarial pass named two unpinned render behaviors. Add them as license-free
unit pins in `tests/unit/test_hierarchy_resolver.py` (it already imports
`reconstruct_expression` and defines the `MockLiteralReal` / `MockInvocationExpression`
/ `MockFeatureChainExpression` stubs; the name-fallback `is_instance` pattern is
proven). `reconstruct_expression` has no dedicated float formatter — numeric literals
render via `str(value)`.

- **Pin 1 — scientific-notation normalized form:**
  `reconstruct_expression(MockLiteralReal(1e-06)) == "1e-06"` (Python `str(1e-06)`;
  **not** `"1.0e-6"` or `"0.000001"`). Currently uncovered anywhere.
- **Pin 2 — positive `sum(...)` exact render:**
  `reconstruct_expression(MockInvocationExpression("sum", [MockFeatureChainExpression(["pv_module","capital_cost"])])) == "sum(pv_module.capital_cost)"`.
  Existing coverage only asserts the substring `"sum("` (test_hierarchy_resolver.py:283) —
  an exact-string pin is new; optionally strengthen line 283 in place.

### tests/conformance/README.md — anchoring note (NEW)

No testing-methodology doc exists (`find tests -iname '*.md'` → only a fixture
PROVENANCE). Add `tests/conformance/README.md` with a short "how to anchor a
conformance expectation" note:

- The anti-pattern: `expected = production_fn(...)` then `assert actual == expected`.
- The fix: transcribe the literal from a known fixture element; compare against it.
- The pass-or-skip trap: a test that can only pass or skip is not coverage — end on an
  unconditional `assert found`.
- Point at the existing conventions rather than restating them: the `req(id)` marker
  (`tests/conformance/conftest.py:56`), the snapshot-fixture pattern
  (`conftest.py:17-35`), and the exemplar literal tables in
  `test_naming_conventions.py:82-149` and `test_gen_schemas.py:359-381`.

## The MF-07 pass-or-skip conversion (detail)

`test_localterm_sibling_agg_output` (test_factory_aggregation.py:724) has two defects:
it sets `found_sibling` only inside nested `if`s (no assert; a miss flips nothing) and
ends on `pytest.skip(...)` — so it is pass-or-skip. Worse, its inner comparison rebuilds
the channel with the exact two lines production runs (`sibling_eqn = f"..."`;
`get_channel_name(...)`), so even a match proves nothing.

Convert to an unconditional assertion on a **known** solar_battery LocalTerm. The
`idiot_index` aggregation at scope `SolarBatteryDesign__solar_battery_plant__solar_array`
has `local_terms = ["capital_cost", "raw_material_cost"]`, both themselves aggregations
at that scope, so both resolve via the sibling strategy:

```python
found = False
for agg in solar_battery_agg["aggregation_data"]:
    if (agg.expression.attribute_name == "idiot_index"
            and agg.instance_path == "SolarBatteryDesign__solar_battery_plant__solar_array"):
        module, _ = _build_aggregation_module(agg=agg, ...)  # same kwargs as the current body
        cap = next(i for i in module.inputs if i.param_name == "capital_cost")
        assert cap.source.source_type == "module_output"
        assert cap.source.producer_channel == \
            "SolarBatteryDesign__solar_battery_plant__solar_array__capital_cost__capital_cost"
        found = True
assert found, "idiot_index/solar_array aggregation with capital_cost LocalTerm not found"
```

The literal is hardcoded (breaks the tautology); `assert found` makes a missing fixture
a FAIL. Model the correctly-anchored sibling `test_localterm_entry_point_fallback`
(781), which already ends on `assert found`. For the L3 expose-alias twin: the
`capital_cost` aggregation on `solar_array` has `local_terms = ["misc_hardware_cost"]`,
an EXPOSE_PURE alias resolving to
`"SolarBatteryDesign__solar_battery_plant__solar_array__allocation_model__total_allocation"`.

## Non-Goals

- Re-anchoring REQ-EXT-09 — Item 4 owns it (handoff recorded).
- Any production-code change. A re-anchor that exposes a real bug is filed/absorbed
  explicitly, not fixed here (§D5 expects none).
- Verification-matrix row/count/marker updates — Item 7 owns the matrix.
- Re-flagging the cleared non-findings (BT-04, dual_resolution parity, baselines).

## Open Questions / Deferred to design

- **The authoritative LOW-8 list.** The register enumerated LOW only in the session
  transcript. The reconstructed set above stands unless the transcript's D5 agent
  output is recovered at implement — the first plan step reconciles them. If the
  transcript names a LOW test not in the reconstruction, disposition it by the same
  fix-if-one-line-else-document rule.
- **The "five vs six" factory-naming count.** The register said five; the sweep found
  six of the identical recompute shape. All six are dispositioned (M5–M9 row); no
  decision needed, but the count divergence is flagged for Item 7's matrix recount.
- Whether L4–L7 (the generation-vs-graph consistency family) warrant a shared helper
  assertion instead of per-test documentation — a design nicety, deferable.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_pipeline_truth.md` (Item 6; R1 addition banning the
  anti-pattern; SC-E)
- **Required Reading:** `.project/research/20260706_pipeline-truth-discovery.md` §D5
  (the 25 flagged + cleared non-findings); `docs/architecture/verification-matrix.md`
  (PASS definition)
- **Handoff:** REQ-EXT-09 re-anchoring → `.project/active/subtype-enumeration/` (Item 4)
- **Plan:** `.project/active/test-truth/plan.md` (to be created)

---

**Next Steps:** Item 6 is low-risk and mechanical — proceed to `/_my_plan` (the epic
routes this item spec → plan → implement, skipping design).
