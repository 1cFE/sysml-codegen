# Implementation Plan: Self-Referential Test Remediation (PIPELINE-TRUTH Item 6)

**Status:** Draft
**Created:** 2026-07-06
**Last Updated:** 2026-07-06

## Source Documents
- **Spec:** `.project/active/test-truth/spec.md` ← the three disposition tables (HIGH/MEDIUM/LOW) carry the concrete literal + anchor per test; the [HARD] requirements are settled contracts. This plan does not restate them — it references rows by their `#` (H2, M4, L2, …).
- **Spec review:** `.project/active/test-truth/spec-review.md` ← why the [HARD] requirements exist (L3-1 index re-keying, L1-1 doubling note, L3-2 provenance).

---

## READ THIS FIRST — rebase-awareness (coordination constraint)

Items 1 and 4 are implementing in **this same working tree ahead of this item**. The line numbers in the spec's disposition tables were read 2026-07-06 and **may have drifted**. Before touching any file:

1. `git status` and `git log --oneline -10` — see what landed since the spec was written.
2. **If `tests/conformance/test_extractor.py` shows uncommitted changes, DO NOT touch it.** That file holds REQ-EXT-09 (H1), which is Item 4's to re-anchor (spec [HARD]: "do not touch `test_extractor.py`'s EXT-09 test here"). H1 is a **HANDOFF**, not a fix — it stays out of scope regardless.
3. For every flagged test, **locate it by test-function name, not by the spec's line number** — grep the name (e.g. `grep -n "def test_output_channel_name_format" tests/`). The spec review already warns the count-sibling must be keyed on name not line (L1-2). Treat every line number in the spec and in this plan as a starting point to re-confirm.

## LICENSE-FREE — no capture step

Every anchor literal comes from **committed** sources — the two snapshots
(`tests/fixtures/{solar_battery_model,catf_mfe_model}/extraction_snapshot.json`), the
committed `computation_graph.json` baselines, and the committed `*.sysml` design/library
sources. **No syside license, no `--models` capture, no snapshot regeneration is needed at
any point in this item.** The REG-02 on-disk phase (M10) generates *from a committed
snapshot* to `tmp_path` via `generate --from-snapshot` (the harness already used in
`tests/integration/test_full_pipeline.py:228-248`). If you find yourself reaching for a
license, stop — you have taken a wrong turn.

## No production change (NEED)

Re-anchoring reveals current behavior; it does not alter it. §D5 verified current behavior
matches. **If a re-anchor genuinely exposes a production bug, STOP** — file it (absorb into
the matching epic item or a BACKLOG entry) rather than bending the literal to match wrong
output. Do not edit production to make a pin pass. (The only production edits in this whole
item are the *temporary, reverted* mutations in Phase 9.)

## Provenance comment format (applies to every fixed test, all phases)

Every re-anchored literal carries a comment next to it citing its source, in one of these
forms (spec [HARD] / L3-2):

```python
# provenance: tests/fixtures/catf_mfe_model/extraction_snapshot.json:2896 (USAGE_LITERAL binding)
# provenance: models/solar_battery/design.sysml:53 (design attribute)
# provenance: hand-computed from float("0.45")
```

The close-out lists the provenance per fixed test. A literal without a provenance comment is
an incomplete fix.

---

## Implementation Strategy

**Phasing rationale.** One phase per test-file cluster / disposition tier, ordered so the
suite is **green at every phase boundary** and each phase is a standalone commit. Within
that, de-risk the one non-trivial pattern early: the by-`(instance_path, attribute_name)`
aggregation selection (L3-1) lands in Phase 3, before the phases that reuse it. Everything
else is literal transcription.

**Critical path.** Phase 3 is the only phase with real technique (select an aggregation out
of `aggregation_data` by identity, not index, then assert a literal on it, including the
deliberate channel doubling). Prove that pattern in Phase 3; Phase 4 (M4 + factory naming)
leans on it. All other phases are independent and could be reordered.

**First proof point.** Phase 1 — the per-model expected-count dict `{"solar_battery_model":
3, "catf_mfe_model": 8}` replacing `len(files) == len(groups)`. Smallest possible change
that breaks a tautology; proves the "literal from a committed baseline" approach end to end.

**Validation approach.** Each phase: `uv run pytest <touched files>` green. After the last
content phase and again after mutations are reverted: **full suite** green, ruff/mypy not
worse than the **21/109** baseline. Phase 9 proves three of the fixed tests actually go RED
under a named production mutation, then reverts. Count changes are reconciled in the
close-out (no test deleted without a replacement).

**Phase → tests → files:**

| Phase | Rows | Files touched |
|---|---|---|
| 1 · Count-tautologies (HIGH) | H2, H3, H4 + entry_fusion twin | `test_gen_json_templates.py`, `test_gen_pipeline_yaml.py` |
| 2 · Classifier literals | H5, M1 | `test_entry_point_classifier.py` |
| 3 · By-identity aggregation + MF-07 convert | H6, H7, L2, L3 | `test_factory_aggregation.py` |
| 4 · Scoping + factory-naming | M4, M5–M9 | `test_aggregation_scoping.py`, `test_factory_calc_usage.py`, `test_factory_formula.py` |
| 5 · Parameter-group deriver | M2, M3 | `test_parameter_group_deriver.py` |
| 6 · Registry on-disk truth | M10 (REG-02) | `test_gen_registry.py` |
| 7 · LOW document + cheap fixes | L1, L4, L5, L6, L7, L8 | `test_naming_conventions.py`, `test_type_mapping_consolidation.py`, `test_gen_module_wrappers.py`, `test_gen_schemas.py`, `test_gen_stencils.py` |
| 8 · SC-6 render pins + README | 2 NEW pins + note | `tests/unit/test_hierarchy_resolver.py`, `tests/conformance/README.md` |
| 9 · Mutation spot-check + close-out | verify H2, H7, L2 | production (temporary, reverted) |

H1 (EXT-09) appears in no phase — **HANDOFF to Item 4**, recorded in the close-out.

---

## Phase 1: Count-tautologies (HIGH — H2, H3, H4 + entry_fusion twin)

### Goal
Replace `len(files) == len(groups)` (both sides are the same count over a 1:1 loop) with a
hand-transcribed per-model expected-count dict. First and simplest — proves the approach.

### Assumption Under Test
That the committed baselines really do fix the counts at solar=3 / catf=8, so a keyed dict
is complete over `PARAMETRIZED_MODELS` (exactly those two models). If a model produces a
different count, the pin — not the tautology — catches it.

### Test Stencil (write first)
```python
# H2 / H3 — test_gen_json_templates.py
# Keep the parametrization; index a per-model literal count by model_name (L3-3).
EXPECTED_GROUP_COUNTS = {
    # provenance: computation_graph.json baselines — solar has 3 entry_point_groups
    #   (DesignParams, LibraryParams, SystemDesign); catf has 8 (Blanket/Heating/
    #   Magnets/Physics/RadialBuild/System/Tritium/Vacuum). spec-review "Literals verified".
    "solar_battery_model": 3,
    "catf_mfe_model": 8,
}
def test_req_gen_05_one_json_per_group(model_name, ...):
    ...
    assert len(json_files) == EXPECTED_GROUP_COUNTS[model_name]
```

### Changes Required
See `spec.md` rows **H2** (`test_gen_json_templates.py:115`), **H3** (`:135`), **H4**
(`:553`) and the H4 twin **`test_entry_fusion_json_count`** (`test_gen_pipeline_yaml.py:402`).

- [ ] `test_gen_json_templates.py`: H2 (json per group), H3 (schema per group), H4
  (`test_req_py_07_json_file_count_matches_entry_point_groups`) → the `{solar:3, catf:8}`
  dict keyed by `model_name`. **Do not collapse to a scalar; do not drop the
  parametrization** (L3-3). One shared `EXPECTED_GROUP_COUNTS` dict is fine.
- [ ] `test_gen_pipeline_yaml.py`: the `entry_fusion` twin gets the **same** map.
- [ ] Provenance comment on the dict (source: committed `computation_graph.json` baselines).

### Validation
- [ ] `uv run pytest tests/conformance/test_gen_json_templates.py tests/conformance/test_gen_pipeline_yaml.py` → green.
- [ ] `git grep -n "len(.*groups)" <these files>` → no remaining `len==len` self-comparisons in the four touched tests.

**What we know works after:** the count pins now compare to a committed literal, not to
themselves. The keyed-dict pattern is proven for the parametrized phases below.

---

## Phase 2: Classifier literals (H5, M1)

### Goal
Replace `expected = float(source)` (H5) and the re-invoked `_get_library_default` agreement
(M1) with transcribed input→expected pairs from catf USAGE_LITERALs and calc-def defaults.

### Assumption Under Test
That the transcribed literals (1546.72 / 2079.41 / 1104.22; 0.45 / 1.07 / 171.5) match the
committed snapshot bindings and defaults — and that the unparseable cases really yield `None`.

### Test Stencil (write first)
```python
# H5 — test_entry_point_classifier.py; keep the independent isinstance(...float) check.
CASES = [
    ("gross_electric", 1546.72),        # provenance: catf_mfe_model/extraction_snapshot.json:2896
    ("p_neutron", 2079.41),             # provenance: catf_mfe_model/extraction_snapshot.json:<line>
    ("p_thermal_electric", 1104.22),    # provenance: catf_mfe_model/extraction_snapshot.json:<line>
    ("3+4", None),                      # provenance: hand-computed — unparseable literal → None
]
```

### Changes Required
See `spec.md` rows **H5** (`test_entry_point_classifier.py:289`, `expected=float(source)` at
`:309`) and **M1** (`:318`, `_get_library_default` re-invoked at `:353`).

- [ ] H5: hardcode the three USAGE_LITERAL input→expected pairs + a synthetic `"3+4"`→`None`.
  Keep the `isinstance(..., float)` check (independent of the value).
- [ ] M1: transcribe calc-def default→expected — numeric `0.45 / 1.07 / 171.5`; expression
  defaults (`"1.0 / q_eng"`, `"TBD"`)→`None`. **Also anchor the DA (`:339`) and UL (`:359`)
  branches** of the same test — they share the disease in weaker form.
- [ ] Provenance comment per literal (snapshot line for USAGE_LITERALs; calc-def source for
  defaults; "hand-computed" for the unparseable cases).

### Validation
- [ ] `uv run pytest tests/conformance/test_entry_point_classifier.py` → green.

**What we know works after:** the float-conversion and library-default classifier pins fail
if production stops parsing or mis-defaults; they no longer echo the production call.

---

## Phase 3: By-identity aggregation anchors + MF-07 conversion (H6, H7, L2, L3)

### Goal
The de-risking phase. (a) Re-anchor the two aggregation naming pins (H6 module name, H7
output channel) by selecting the aggregation via `(instance_path, attribute_name)` — **not
list index** (L3-1) — then asserting a literal. (b) Convert the two pass-or-skip LocalTerm
tests (L2 MF-07, L3 expose-alias) to pass-or-FAIL.

### Assumption Under Test
That `(instance_path, attribute_name)` uniquely selects the intended aggregation out of
`aggregation_data` (the model has many `idiot_index` aggregations, so index is unsafe), and
that the LocalTerm resolves to the expected sibling / expose channel. This is the one place
the item could *introduce* a wrongly-failing test if the selection is wrong — prove it here.

### Test Stencil (write first)
```python
# H6 module name — select by identity, assert lowercased literal (design prefix lowercased).
agg = next(a for a in agg_data
           if a.instance_path == "SolarBatteryDesign__solar_battery_plant__solar_array"
           and a.expression.attribute_name == "capital_cost")   # NOT agg_data[idx]
# provenance: get_module_name lowercases the whole EQN (core/qualified_names.py:95)
assert module.name == "solarbatterydesign__solar_battery_plant__solar_array__capital_cost"

# H7 output channel — SAME selection; trailing attribute is DOUBLED on purpose.
# The doubling is the ADR-003 aggregation channel-PQN: get_channel_name =
#   usage_qn + "__" + output_name (core/qualified_names.py:98-100), and an aggregation
#   module's EQN already ends in the attr name. This is CORRECT — do NOT de-double.
assert channel_name == \
    "SolarBatteryDesign__solar_battery_plant__solar_array__capital_cost__capital_cost"
```

For L2/L3 use the spec's MF-07 code sketch verbatim (spec.md "The MF-07 pass-or-skip
conversion (detail)"), ending on an **unconditional `assert found, "..."`**.

### Changes Required
See `spec.md` rows **H6** (`test_factory_aggregation.py:208`), **H7** (`:566`), **L2**
(`:724`), **L3** (`:753`) and the "MF-07 conversion (detail)" block.

- [ ] **[HARD] Selection by identity, not index** for H6 and H7. Never `agg_data[0]` /
  `agg_data[15]` — a DFS reorder must not fail these pins.
- [ ] **[HARD] Doubling comment** on the H7 literal (and it stays doubled). Per ADR-003; see
  `core/qualified_names.py:98-100`.
- [ ] H6 literal is fully lowercased incl. the `solarbatterydesign` design prefix — only a
  literal catches the lowercasing.
- [ ] L2 (`test_localterm_sibling_agg_output`): convert pass-or-skip → pass-or-FAIL. Anchor
  the `idiot_index` aggregation at `solar_array` (`local_terms = [capital_cost,
  raw_material_cost]`); assert `capital_cost`'s `producer_channel` equals the doubled literal
  `...__solar_array__capital_cost__capital_cost`; end on `assert found, ...`.
- [ ] L3 (`test_localterm_expose_alias`): same conversion. The `capital_cost` aggregation on
  `solar_array` has `local_terms = ["misc_hardware_cost"]`, an EXPOSE_PURE alias resolving to
  `...__solar_array__allocation_model__total_allocation`. End on `assert found`.
- [ ] Model the already-correct sibling `test_localterm_entry_point_fallback` (`:781`), which
  already ends on `assert found`.
- [ ] Provenance comments (library.sysml lines for the aggregation definitions —
  `library.sysml:637` idiot_index, `:615` capital_cost sibling, `:612` misc_hardware_cost
  expose, per spec-review).

### Validation
- [ ] `uv run pytest tests/conformance/test_factory_aggregation.py` → green.
- [ ] Confirm **no** `agg_data[<int>]` index access remains in the four touched tests
  (`git grep -nE "aggregation_data\[[0-9]" tests/conformance/test_factory_aggregation.py`).
- [ ] Confirm neither converted test ends on `pytest.skip(...)` any more.

**What we know works after:** the identity-selection pattern is proven; the two MF-07-shape
tests now FAIL (not skip) on a missing/mis-resolved LocalTerm; the deliberate doubling is
documented in-code so it survives future readers.

---

## Phase 4: Scoping + factory-naming (M4, M5–M9)

### Goal
Apply the Phase-3 identity-selection to M4 (aggregation `module_eqn`) and add dedicated
non-parametrized literal pins for the six factory-naming tests (M5–M9), including the
deliberate FORMULA-channel doubling.

### Assumption Under Test
That the factory naming helpers produce the exact transcribed names for the named
solar_battery modules — and that the parametrized recompute can be replaced by a single
literal on one named element without losing the parametrized coverage.

### Test Stencil (write first)
```python
# M5–M9 — dedicated non-parametrized literals (alongside/replacing the recompute).
# calc_usage module name:
assert name == "solarbatterydesign__solar_battery_plant__energy_production"
# calc_usage channel:
assert ch == "SolarBatteryDesign__solar_battery_plant__energy_production__annual_energy_mwh"
# formula name:
assert name == "solarbatterydesign__solar_battery_plant__p_net_kw"
# formula channel — DOUBLED on purpose (same ADR-003 PQN as H7; do NOT de-double):
assert ch == "SolarBatteryDesign__solar_battery_plant__p_net_kw__p_net_kw"
# module types:
assert mt == "solarbatterylibrary.EnergyProductionCalcModule"
assert mt == "solarbatterydesign.solar_battery_plant.p_net_kwModule"
```

### Changes Required
See `spec.md` rows **M4** (`test_aggregation_scoping.py:511`, plus the identical AS-03
recompute at `:311`) and **M5–M9** (`test_factory_calc_usage.py:206,:522`;
`test_factory_formula.py:216,:647`; module_type twins `:218,:234`).

- [ ] M4: **select by `(instance_path, attribute_name)`, not the parametrized index** (L3-1).
  `solar_array`/`capital_cost` → `module_eqn == "SolarBatteryDesign__solar_battery_plant__solar_array__capital_cost"`;
  plant-root/`capital_cost` → `"SolarBatteryDesign__solar_battery_plant__capital_cost"`.
  Fold in the identical AS-03 recompute at `:311` with the same fix. Model
  `test_module_eqn_issue22` (`:521`, already literal).
- [ ] M5–M9: add a **dedicated non-parametrized** literal assertion on the named module
  (INFERRED: a single literal cannot ride the parametrization). **Disposition all six** of
  this shape — the register said five, the sweep found six; the extra `module_type` recompute
  is coverage gained, note it, not scope creep.
- [ ] **[HARD] Doubling comment** on the formula-channel literal (same ADR-003 PQN as H7).
- [ ] Provenance comments per literal.

### Validation
- [ ] `uv run pytest tests/conformance/test_aggregation_scoping.py tests/unit/test_factory_calc_usage.py tests/unit/test_factory_formula.py` → green (confirm the real paths of the factory test files at implement).
- [ ] No `[<int>]` index selection remains in the M4 tests; no `expected = get_*_name(...)`
  or `expected = derive_module_type(...)` recompute remains in the six factory tests.

**What we know works after:** all aggregation/factory naming pins compare to literals; the
count divergence (five-vs-six) is dispositioned and flagged for Item 7's matrix recount.

---

## Phase 5: Parameter-group deriver (M2, M3)

### Goal
Replace the deriver's re-invocation of its own internals (`_generate_group_names`,
`_literal_index[qname]`) with named-qname→named-group and named-literal assertions.

### Assumption Under Test
That the transcribed classifications and literal-index values (`child_count`→25.0,
`total_child_mass`→50.0, `p_net_mw`→0.008) match the committed snapshot and design sources.

### Test Stencil (write first)
```python
# M2 — named qname → named group (not index-drawn, not recomputed):
assert deriver.classify("SolarBatteryDesign__solar_battery_plant__p_net_mw") == "design_params"
# M3 — real literal-index entries:
assert deriver.get_default_value("...__child_count") == 25.0      # provenance: solar snapshot:3555
assert deriver.get_default_value("...__total_child_mass") == 50.0 # provenance: solar snapshot:3568
assert deriver.get_default_value("...__energy_production__p_net_mw") == 0.008  # provenance: design.sysml:53
```

### Changes Required
See `spec.md` rows **M2** (`test_parameter_group_deriver.py:411`, plus the four
`classify_returns_group_for_*_index` tests `:365-402`) and **M3** (`:476`, plus the
binding-resolution twin `:459`).

- [ ] M2: hardcode `classify(...p_net_mw) == "design_params"`. Harden the four
  `classify_returns_group_for_*_index` tests (draw a **named** qname, assert a **named**
  group: attr→`design_params`; unbound/literal→`library_params`) instead of asserting only
  non-None. **Keep** `classify_unknown_returns_none` (`:404`, already a literal negative).
- [ ] M3: hardcode `child_count`→25.0, `total_child_mass`→50.0. Replace the binding-resolution
  twin (`:459`, currently only `None or isinstance float`) with
  `get_default_value(...__energy_production__p_net_mw) == 0.008` (exercises real binding→attr
  resolution). Model `test_req_pgd_06_default_value_direct_attr` (`:451`, already literal 0.008).
- [ ] Provenance comments (solar snapshot lines 3555/3568; `design.sysml:53`).

### Validation
- [ ] `uv run pytest tests/conformance/test_parameter_group_deriver.py` → green (confirm path).

**What we know works after:** the deriver pins fail if classification precedence or the
literal index regresses; they no longer agree with the method they call.

---

## Phase 6: Registry on-disk truth (M10 — REG-02)

### Goal
Re-anchor REQ-REG-02 from a weak "each dotted segment is alphanumeric" syntactic check to an
**on-disk** check: generate the two models to `tmp_path`, then for each registry import
`from pkg.modules.A.B.C import Name` assert `output/modules/A/B/C.py` exists.

### Assumption Under Test
That `generate --from-snapshot` writes module files at paths matching the registry's import
lines — i.e. the registry import paths correspond to files a real generation run produced,
not to a re-derived path rule. License-free: generation runs from the committed snapshot.

### Test Stencil (write first)
```python
# M10 — REG-02 on-disk. Reuse the from-snapshot harness (test_full_pipeline.py:228-248).
output = generate_to_tmp(snapshot=".../solar_battery_model", tmp_path=tmp_path)  # + catf_mfe
for imp in registry_imports:            # from pkg.modules.A.B.C import Name
    rel = imp.module_path.replace(".", "/") + ".py"   # A/B/C.py
    assert (output / "modules" / rel).exists(), f"{imp} has no file on disk"
# Example: ...solarbatterylibrary.allocationcostcalc import AllocationCostCalcModule
#   → assert output/modules/solarbatterylibrary/allocationcostcalc.py exists.
```

### Changes Required
See `spec.md` row **M10** (`test_gen_registry.py:279`; the weak alnum check at `:312`; the
count sibling `test_module_count_matches_inputs` at `:323` — **key on the name, not the
line**, L1-2).

- [ ] Generate solar_battery + catf_mfe from their committed snapshots to `tmp_path` using
  the `generate --from-snapshot` harness pattern from `test_full_pipeline.py:228-248`.
- [ ] For each `from pkg.modules.A.B.C import Name`, assert `output/modules/A/B/C.py` exists.
- [ ] **Do not duplicate REG-05.** REG-02's stated behavior currently lives under REG-05's
  test (`:463`); the mis-anchoring is that REG-02 points at a weak syntactic check. Just make
  REG-02 assert the on-disk match; leave REG-05 alone. (Matrix re-mapping is Item 7's.)
- [ ] Provenance: the on-disk files ARE the anchor; comment cites the generation harness.

### Validation
- [ ] `uv run pytest tests/conformance/test_gen_registry.py` → green.
- [ ] Confirm the test performs real filesystem `exists()` checks against generated output,
  not a `.isalnum()` syntactic pass.

**What we know works after:** REG-02 fails if a registry import points at a module file that
generation did not write — a real path/filesystem contract, license-free.

---

## Phase 7: LOW tier — document + cheap fixes (L1, L4, L5, L6, L7, L8)

### Goal
Fix the one-line LOW rows (L1, L8), and for the generation-vs-graph consistency family
(L4–L7) record the sibling-pin reliance in a code comment (they stay, but their weakness is
made explicit). Per the spec's LOW preamble, each candidate stands on its own inspection —
**if inspection finds a listed candidate is NOT actually self-referential, strike it with
evidence and note the count change in the close-out.**

### Assumption Under Test
That the reconstructed 7 LOW identities (all but L2/MF-07) really are self-referential on
inspection. No transcript archaeology (Q-1: transcript not recoverable; reconstructed set is
authoritative).

### Test Stencil (write first)
```python
# L1 — test_naming_conventions.py: replace `assert result == eqn.lower()` with
# hand-transcribed lowercased literals for the 3 REAL_EQNS rows. Sibling
# test_module_name_is_lowered_eqn (:259) models it.
assert result == "solarbatterydesign__solar_battery_plant__energy_production"  # provenance: ...

# L4–L7 — leave the consistency check; add a comment noting the literal sibling that pins
# the content, e.g.:
# NOTE: content pinned by the literal type-map sibling test_gen_schemas.py:359-381;
#   this test only checks all generators call the shared fn (weak residual — sibling-pinned).
```

### Changes Required
See `spec.md` LOW table rows **L1** (`test_naming_conventions.py:266`), **L4**
(`test_type_mapping_consolidation.py:177`), **L5** (`test_gen_module_wrappers.py:306`), **L6**
(`:444`), **L7** (`test_gen_schemas.py:311`), **L8** (`test_gen_stencils.py:315`).

- [ ] **L1 (fix):** transcribe lowercased literals for the 3 `REAL_EQNS` rows.
- [ ] **L8 (fix if cheap):** `expected = f"tuple[{', '.join(['float']*n)}]"` is self-shaped —
  pin one known multi-output module's exact return string as a literal. Lowest priority; if it
  is not genuinely cheap, document it as sibling-pinned instead and note that in the close-out.
- [ ] **L4 (document):** iterates every module/attr recomputing `map_sysml_type_to_python`;
  content pinned by literal type-map siblings (`test_gen_schemas.py:359-381`,
  `test_gen_module_wrappers.py:488`). Add a comment recording the sibling-pin reliance.
- [ ] **L5, L6 (document):** template-fidelity vs the graph, pinned by the literal type-map
  sibling. L6 is a near-duplicate of L5 — **note the dedup opportunity** in the comment (do
  not delete; dedup is not this item's call).
- [ ] **L7 (document):** field-name content pinned by the output-registry PQN tests; comment
  it.
- [ ] Provenance/sibling-pin comment on every touched row.

### Validation
- [ ] `uv run pytest tests/unit/test_naming_conventions.py tests/conformance/test_type_mapping_consolidation.py tests/conformance/test_gen_module_wrappers.py tests/conformance/test_gen_schemas.py tests/conformance/test_gen_stencils.py` → green (confirm real paths).
- [ ] Every L-row either has a hand-literal (L1, L8) or a sibling-pin comment (L4–L7).

**What we know works after:** the two fixable LOW rows are anchored; the four documented rows
carry an explicit, reviewable record of why they are kept and what pins them.

---

## Phase 8: SC-6 render-contract pins + conformance README (NEW work)

### Goal
Add the two license-free render pins the adversarial pass named, and the
`tests/conformance/README.md` anchoring note.

### Assumption Under Test
That `reconstruct_expression` renders `1e-06` via `str(value)` → `"1e-06"` (not `"1.0e-6"` /
`"0.000001"`), and renders a positive `sum(...)` exactly as `"sum(pv_module.capital_cost)"`.

### Test Stencil (write first)
```python
# tests/unit/test_hierarchy_resolver.py — reuse the existing Mock* stubs + name-fallback pattern.
# Pin 1 — scientific-notation normalized form (str(1e-06) == "1e-06"):
assert reconstruct_expression(MockLiteralReal(1e-06)) == "1e-06"   # provenance: hand-computed, Python str(1e-06)
# Pin 2 — positive sum(...) exact render (existing coverage only asserts substring "sum(", :283):
assert reconstruct_expression(
    MockInvocationExpression("sum", [MockFeatureChainExpression(["pv_module", "capital_cost"])])
) == "sum(pv_module.capital_cost)"                                  # provenance: hand-computed
```

### Changes Required
See `spec.md` "SC-6 render-contract pins" and "tests/conformance/README.md — anchoring note".

- [ ] Add Pin 1 and Pin 2 in `tests/unit/test_hierarchy_resolver.py` (it already imports
  `reconstruct_expression` and defines `MockLiteralReal` / `MockInvocationExpression` /
  `MockFeatureChainExpression`; name-fallback `is_instance` pattern is proven). Optionally
  strengthen the substring-only line (`:283`) to the exact-string form in place.
- [ ] Create `tests/conformance/README.md` with the "how to anchor a conformance expectation"
  note: the anti-pattern (`expected = production_fn(...)` then `assert actual == expected`);
  the fix (transcribe a literal from a known fixture element); the pass-or-skip trap (end on
  an unconditional `assert found`). Point at the existing conventions rather than restating:
  the `req(id)` marker (`tests/conformance/conftest.py:56`), the snapshot-fixture pattern
  (`conftest.py:17-35`), and the exemplar literal tables (`test_naming_conventions.py:82-149`,
  `test_gen_schemas.py:359-381`).

### Validation
- [ ] `uv run pytest tests/unit/test_hierarchy_resolver.py` → green (both new pins).
- [ ] `tests/conformance/README.md` exists and covers the three points.

**What we know works after:** the two previously-uncovered render behaviors are pinned; the
suite has a written methodology so the R1 ban has a doc to point at.

---

## Phase 9: Mutation spot-check + close-out

### Goal
Prove three of the fixed tests actually go RED under a deliberate production mutation (SC-2),
then revert every mutation. Record results in the close-out. **This phase makes no permanent
production or test change** — the mutations are temporary and reverted; the tests were already
finalized in Phases 1–8.

### Assumption Under Test
That the re-anchored literals genuinely diverge from a mutated production value — i.e. the
tests can now fail. One per category: a count-tautology, a naming/channel, and the MF-07
conversion.

### The three named mutations (break → observe RED → revert)

Confirm exact production lines at implement (they may have drifted); the function targets are
stable.

1. **Count-tautology — verify H2** (`test_req_gen_05_one_json_per_group`).
   - **Mutation:** in the JSON-template generator's loop that writes one file per
     `entry_point_group`, drop a group — iterate `groups[:-1]` instead of `groups`.
   - **Expected failure:** solar_battery writes **2** JSON files; the literal
     `EXPECTED_GROUP_COUNTS["solar_battery_model"] == 3` → **RED**. (Under the old tautology,
     `len(files) == len(groups[:-1])` would still have passed — that contrast is the point.)

2. **Naming/channel — verify H7** (`test_output_channel_name_format`, aggregation).
   - **Mutation:** in `get_channel_name` (`core/qualified_names.py:98-100`), change the
     composition to strip a duplicated trailing segment (de-double), or change the `"__"`
     separator.
   - **Expected failure:** the aggregation channel becomes `...__solar_array__capital_cost`
     (single) or uses the wrong separator; the doubled literal
     `...__capital_cost__capital_cost` → **RED**. This directly proves the doubling pin catches
     a de-doubling — the exact future mistake the [HARD] note guards against.

3. **MF-07 conversion — verify L2** (`test_localterm_sibling_agg_output`).
   - **Mutation:** in the aggregation LocalTerm sibling-resolution (graph_builder — the code
     that sets `producer_channel` for a sibling-resolved LocalTerm; near the
     `get_channel_name` call at `graph_builder.py:1644-1647`), perturb the resolved channel
     (e.g. point `capital_cost` at `raw_material_cost`'s channel).
   - **Expected failure:** `cap.source.producer_channel` ≠ the literal → **RED**, and because
     the converted test ends on `assert found`, it FAILS rather than skips — proving the
     pass-or-skip trap is closed.

For each: run only that test file, capture the RED output line, `git checkout` the production
file to revert, re-run to confirm GREEN.

### Validation
- [ ] Each of the three mutations produces the expected RED; captured in the close-out.
- [ ] All three mutations reverted (`git diff` on production is clean).
- [ ] **Full suite** green: `uv run pytest tests/`.
- [ ] `uv run ruff check src/` and `uv run mypy src/` → not worse than **21/109** baseline.
- [ ] Test-count reconciliation written in the close-out.

**What we know works after:** three representative fixed tests demonstrably fail under a real
production regression; the suite is green with mutations reverted; the item is auditable.

---

## Close-out (fill during implement)

- [ ] **Disposition table** — all 25 dispositioned: 17 register-named (H1–H7, M1–M10) + 8 LOW
  (1 register-named MF-07 + 7 reconstructed). One-line rationale each. Any struck reconstructed
  LOW recorded with evidence.
- [ ] **H1 (EXT-09) handoff** to Item 4 recorded (untouched here).
- [ ] **Per-fixed-test provenance list** — the `file:line` / snapshot / hand-computed source of
  each re-anchored literal (SC / L3-2). ~24 fixed tests.
- [ ] **Mutation spot-check results** — the three named mutations, the RED observed, revert
  confirmed.
- [ ] **Test-count reconciliation** — before/after counts; every delta explained (M5–M9 adds
  dedicated assertions; SC-6 adds 2 pins; no test deleted without a replacement). If any LOW
  candidate was struck, note the count change and the SC-1 arithmetic (17 + 8).
- [ ] **Gate** — full suite green; ruff/mypy vs the 21/109 baseline.
- [ ] **Five-vs-six factory count** flagged for Item 7's matrix recount (no decision here).

---

## Risk Management

- **Index drift (L3-1) — highest risk.** H6/H7/M4 must select by `(instance_path,
  attribute_name)`, never by list index. Mitigation: Phase 3 proves the selection pattern
  first; each phase's validation greps for residual `[<int>]` index access.
- **A literal lifted from production output (L3-2).** Mitigation: every literal carries a
  provenance comment (all phases); the close-out lists provenance per fixed test; Phase 9
  mutation-checks three. Reviewer can confirm each literal traces to a committed source.
- **De-doubling a deliberate PQN (L1-1).** Mitigation: [HARD] doubling comment on every doubled
  literal (H7, M5–M9); Phase 9's H7 mutation is specifically a de-double, proving the pin.
- **Line-number drift from Items 1/4 (coordination).** Mitigation: rebase-awareness note at
  top; locate every test by name; do not touch `test_extractor.py` if it has uncommitted
  changes.
- **A re-anchor exposes a real bug (NEED).** Mitigation: STOP and file it; do not bend the
  literal or edit production. §D5 expects none.

## Environment Setup

See CLAUDE.md. Tests: `uv run pytest tests/`. Type: `uv run mypy src/`. Lint:
`uv run ruff check src/`. **No `generate --models` / license anywhere** — REG-02 uses
`generate --from-snapshot` from committed snapshots.

## Implementation Notes

[TO BE FILLED DURING IMPLEMENTATION]

### Phase 1 Completion
**Completed:** 2026-07-06
**Baseline (current, post-Item-4):** 2031 passed / 4 skipped / 5 xfailed; ruff 20, mypy 105.
(The plan's earlier 21/109 predates Item 4's landing; current is 20/105 — this is the
no-regress bar for this item.)
**Changes:**
- `test_gen_json_templates.py`: added `EXPECTED_GROUP_COUNTS = {solar:3, catf:8}` with
  provenance to the committed `computation_graph.json` baselines; H2/H3/H4 now assert
  `len(files) == EXPECTED_GROUP_COUNTS[model_name]` (dropped the `all_graphs` arg where no
  longer needed). Parametrization kept (L3-3).
- `test_gen_pipeline_yaml.py`: same dict (keys solar+catf; twin runs over `[:2]`);
  `test_entry_fusion_json_count` now pins to the literal.
**Verification of literals against committed snapshots (v2):** solar `computation_graph.json`
has exactly 3 entry_point_groups (design_params, library_params, system_design); catf has 8
(blanket/heating/magnets/physics/radial_build/system/tritium/vacuum)_params. No v2 discrepancy.
**Validation:** 56 passed; no residual `len(x) == len(y)` self-comparison in the 4 touched tests.

### Phase 2 Completion
### Phase 3 Completion
### Phase 4 Completion
### Phase 5 Completion
### Phase 6 Completion
### Phase 7 Completion
### Phase 8 Completion
### Phase 9 Completion (mutation spot-check + close-out)

---

**Status:** Draft → In Progress → Complete
