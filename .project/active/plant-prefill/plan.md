# Implementation Plan: Plant-Idiom Literal Pre-Fill (SC-5 stage 1)

**Status:** Draft
**Created:** 2026-07-05
**Last Updated:** 2026-07-05
**Epic Item:** UPSTREAM-FINDINGS Item 9
**Complexity:** MEDIUM (~3–4 phases)
**Branch:** upstream-findings-epic

## Source Documents
- **Spec:** `.project/active/plant-prefill/spec.md`
- **Design:** `.project/active/plant-prefill/design.md` ← component details, decisions (D1–D5), invariants (INV-1..5), B2 sweep, pin-flip checklist
- **Design review + resolutions:** `.project/active/plant-prefill/design-review.md` (C1/M1/M2/m1/m2 resolved)

## Orchestrator sign-offs (baked in — do not reopen)
- **D1:** LIVE re-capture of the four affected snapshots. A license is available at implement time; there is **no** offline-patch path.
- **Shape-5:** `ife_plant` shape 5 is **capture-but-unwired**. `capacity_factor` is consumed by no calc, so the asserted outcome is that `design_overrides` *captures* `baseline_plant.capacity_factor = 0.95`, not that a param value flips. (Design → Shape-5 correction.)

## Implementation Strategy

**The whole fix is three one-function edits** (Design → Architecture). Everything else in this plan is *proving* those three edits are correct and *not-wider-than-promised*:

1. `extract_design_overrides` (`hierarchy_resolver.py:167`) — drop the per-usage `owned_redefinitions` skip; scan every part usage's members; keep a newly-scanned plain-usage override only when its RHS is LITERAL (D3).
2. `_rewrite_virtual_bindings` (`pipeline_builder.py:242`) — replace the bare-name `raise` with skip-with-DEBUG (REQ-VBR-09).
3. `_create_virtual_calc_usage` (`usage_extractor.py:393`) — `list(template.bindings)` → `[copy.copy(b) for b in template.bindings]` (D2 / REQ-VBR-08).

**Phasing rationale:**
- **Phase 0 (tests-first, license-free)** writes the two constructed unit tests that are cleanly red before the code exists — the divergent-sibling rewrite (REQ-VBR-08) and the bare-name skip (REQ-VBR-09). Both run on plain model objects, no SysIDE license. This de-risks the two rewrite-hardening edits independently of any snapshot.
- **Phase 1 (the three edits)** makes Phase 0 green. Full suite still green except the four snapshot-baked pins, which cannot flip until the snapshots are regenerated — those are the *only* allowed reds crossing into Phase 2.
- **Phase 2 (live re-capture + pin-flip + byte-exact sweep)** is the executable gate. Regenerate exactly the four affected snapshots via the capture script, execute every pin-flip checklist row (incl. the three `unresolvable_attr_probe` re-anchors and the V11-proof docstring moves), then prove INV-5: exactly the four snapshot dirs changed, every other committed artifact byte-identical.
- **Phase 3 (docs / matrix / close-out)** moves the REQ IDs, docs, release-notes enumeration, agentic-mbse impact, and the `deep_cross_scope_probe` drift note.

**Critical path:** Phase 0 tests red → three edits → Phase 0 green → live re-capture of four snapshots → pin-flip checklist → byte-exact sweep proves INV-5. The sweep is the single go/no-go gate.

**First proof point:** Phase 0's divergent-sibling test is red on `main` and goes green the moment the shallow-copy edit lands — the fastest independent proof the hardening edits are correct, needing no license and no snapshot.

**Overall validation approach:** suite green at every phase boundary; the *only* documented exception is the window inside Phase 2 between "snapshots regenerated" and "pins flipped." mypy/ruff clean at each boundary.

**Gate now (pre-item):** 1928 passed / 4 skipped / 11 xfailed; ruff 21; mypy 109. **Post-item expectation:** the V11 xfails/aborts tied to `alias_agg_probe` flip to clean; test count shifts are enumerated in Phase 2's checklist. ruff/mypy counts unchanged (three edits + `import copy`).

---

## Phase 0: Constructed unit tests (license-free, red first)

### Goal
Write the two rewrite-hardening tests that can be proven red *before* the code exists, on plain model objects. First proof point for the two edits that don't need a snapshot.

### Assumption Under Test
That the shared-`BindingInfo` hazard (REQ-VBR-08) and the bare-name raise (REQ-VBR-09) are real and that the designed edits (shallow copy, skip-with-DEBUG) fix them — proven without a license.

### Test Stencils (Write These First)

**Divergent-sibling regression (REQ-VBR-08)** — Design → "Divergent-sibling regression". Precedent for building real Pydantic/dataclass objects (not mocks): `test_unwired_fallthrough_partition` (`test_uncovered_params.py:194`).
```python
# tests/unit/test_virtual_binding_rewrite.py (NEW)
def test_rewrite_respects_instance_boundary_for_divergent_siblings():
    # template CalcUsage with one `base_cost` REFERENCE binding (is_template=True)
    template = _make_template_calc_usage(param="base_cost",
                                         source_path="Lib::Widget::cost_model::base_cost")
    iA = _create_virtual_calc_usage(template, "Design__plant__widgetA")
    iB = _create_virtual_calc_usage(template, "Design__plant__widgetB")
    hier = HierarchyExtractionResult(
        redefinitions=[], design_overrides=[
            _deep_literal_override("Design__plant__widgetA", ["cost_model", "base_cost"], 50.0),
            _deep_literal_override("Design__plant__widgetB", ["cost_model", "base_cost"], 100.0),
        ], multiplicities=[], aggregation_expressions=[], warnings=[])
    _rewrite_virtual_bindings([iA, iB], hier)
    assert _binding(iA, "base_cost").literal_value == 50.0    # fails pre-copy: iB skipped as already-LITERAL
    assert _binding(iB, "base_cost").literal_value == 100.0   # ...and reads 50.0
```

**Bare-name crash-safety (REQ-VBR-09)** — Design → "Bare-name crash-safety".
```python
def test_rewrite_skips_bare_name_source_path_without_raising(caplog):
    usage = _make_virtual_calc_usage(param="availability", source_path="availability")  # bare name
    hier = _hier_with_one_override(...)  # non-empty index — the empty-index shield no longer applies
    with caplog.at_level(logging.DEBUG):
        _rewrite_virtual_bindings([usage], hier)          # must NOT raise (was ValueError at :242)
    assert _binding(usage, "availability").source_path == "availability"  # unchanged
    assert any("bare-name" in r.message for r in caplog.records)
```

**Literal filter (REQ-HR-08, D3) — where provable.** The filter lives inside `extract_design_overrides`, which consumes real SysIDE elements, so a faithful end-to-end unit test needs a license. Its license-free proof is the Phase-2 `catf_mfe` guarantee (CHAIN override stays out → byte-identical → stays V11-pinned). **Planning call:** factor the keep/drop decision into a tiny pure predicate (e.g. `_keep_plain_usage_override(redef_data) -> bool`, returns `redef_data.redefinition_type is RedefinitionType.LITERAL`) so it *can* carry a direct license-free unit test:
```python
def test_plain_usage_override_filter_keeps_only_literal():
    assert _keep_plain_usage_override(_redef(RedefinitionType.LITERAL))
    assert not _keep_plain_usage_override(_redef(RedefinitionType.CHAIN))
    assert not _keep_plain_usage_override(_redef(RedefinitionType.EXPRESSION))
```

### Changes Required
**See `design.md` for:** Test Design (divergent-sibling, bare-name); D2/D3; INV-1/2/3.

- [ ] `tests/unit/test_virtual_binding_rewrite.py` (NEW) — divergent-sibling + bare-name tests, real objects; small builder helpers (`_make_template_calc_usage`, `_deep_literal_override`, `_binding`).
- [ ] Literal-filter predicate test — either alongside the above (if the predicate is factored in Phase 1) or noted as Phase-2-proven.

### Validation
**Automated:**
- [ ] `uv run pytest tests/unit/test_virtual_binding_rewrite.py` → divergent-sibling **RED** (shared object), bare-name **RED** (`ValueError` at `pipeline_builder.py:242`).

**What We Know Works After This Phase:** The two hardening edits have a failing executable spec, license-free — Phase 1 flips them green.

---

## Phase 1: The three one-function edits

### Goal
Land the three edits (Design → Architecture). Turn Phase 0 red → green. Leave the snapshot-baked pins as the only remaining reds (they need Phase 2).

### Assumption Under Test
That the guard relaxation + LITERAL filter + shallow copy + bare-name skip are self-contained: no new abstraction, no schema/template change, and no *code*-driven regression (only snapshot-baked tests move).

### Changes Required
**See `design.md` for:** Architecture (the three edits); Implementation Notes (guard shape `is_part_redefines = bool(usage.owned_redefinitions)` + always-scan + `continue`-on-non-LITERAL; deep-copy site; bare-name skip wording; `import copy` at module top; performance note); D2/D3; INV-1/2/3/4.

- [ ] **`hierarchy_resolver.py:186–197`** — drop the `if not owned_redefinitions: continue` skip; compute `is_part_redefines` once; always scan `owned_members`; for a plain-usage (`not is_part_redefines`) override, `continue` unless `redefinition_type is RedefinitionType.LITERAL`. Factor the keep/drop into the pure predicate from Phase 0. (~6 changed lines.)
- [ ] **`pipeline_builder.py:242`** — replace `raise ValueError(...)` with `logger.debug("bare-name source_path %r on %s; skipping override match", source, usage.qualified_name)` then `continue`.
- [ ] **`usage_extractor.py:393`** — `bindings=list(template.bindings)` → `bindings=[copy.copy(b) for b in template.bindings]`; add `import copy` at module top. Leave `unbound_params=list(...)` (strings) as-is.

### Validation
**Automated:**
- [ ] `uv run pytest tests/unit/test_virtual_binding_rewrite.py` → **all green** (both edits proven).
- [ ] `uv run pytest tests/` → green **except** the four snapshot-baked pins that cannot flip until Phase 2 re-capture: `test_collector_pins_alias_agg_probe`, `test_collector_pins_issue22_model`, `test_collector_pins_unresolvable_attr_probe`, and the `alias_agg_probe`/`ife_plant` fixture tests. Confirm **no other** test moved (a code-only regression here would be a real defect — the deep-copy and guard relax must churn nothing beyond the enumerated snapshot readers).
- [ ] `uv run mypy src/` → 109 (unchanged). `uv run ruff check src/` → 21 (unchanged).

**What We Know Works After This Phase:** The rewrite is per-instance-safe and crash-safe; the guard captures plain-usage LITERAL overrides. Remaining reds are exactly the snapshot-baked pins, quarantined to Phase 2.

---

## Phase 2: Live re-capture + pin-flip + byte-exact sweep (the executable gate)

### Goal
Regenerate the four affected snapshots from live extraction (D1), execute every pin-flip checklist row, and prove INV-5: exactly the four snapshot dirs changed, everything else byte-identical.

### Assumption Under Test
- **B1:** live extraction yields the deep-path `base_cost` override and the rewrite plants the literal (the probe was faithful).
- **B2 / INV-5:** exactly four fixtures change — `ife_plant`, `alias_agg_probe`, `issue22_model`, `unresolvable_attr_probe` — every other committed snapshot byte-identical.
- **D5 re-anchor:** `unresolvable_attr_probe`'s `my_calc.x` fills to `[]` (clean strict generation), and the V11 raise proof survives on `catf_mfe` (strict raise) + `ife_plant` shape-4 (strict abort).

### Regeneration mechanism (grounded)
- **Extraction snapshots:** `uv run python scripts/capture_extraction_snapshots.py` (needs license). It re-runs live extraction for every fixture; the extraction-only path calls `_extract_hierarchy_and_rewrite_bindings` (`scripts/capture_extraction_snapshots.py:96`), so `unresolvable_attr_probe`'s `my_calc.x` **does** get rewritten to LITERAL 5.0 on re-capture. `unresolvable_attr_probe` is in `EXTRACTION_ONLY_MODELS` (`:65`); the other three are in `MODELS`.
- **Pipeline baselines:** `uv run python scripts/capture_pipeline_baselines.py` (license-free, reads snapshots) — regenerates `baseline_outputs/ife_plant/…`. Design expects these **byte-identical** (`capacity_factor` never enters the graph), so this run should churn nothing; run it to confirm.

### Pin-flip checklist (execute every row — Design → Test Design)
- [ ] `test_uncovered_params.py::test_collector_pins_alias_agg_probe` — `[("base_cost","cost_model")]` → `[]`
- [ ] `test_uncovered_params.py::test_collector_pins_issue22_model` — `[("base_cost","cost_model")]` → `[]`
- [ ] `test_uncovered_params.py::test_collector_pins_unresolvable_attr_probe` (`:104`) — `[("x","my_calc")]` → `[]` (`local_val=5.0` fills `x`; violation list traced to `[]` in Design → Test Design)
- [ ] `test_uncovered_params.py::test_reconcile_raises_v11_on_wired_gap` (`:129`) — **re-anchor** its `_graph(...)` from `unresolvable_attr_probe` to `catf_mfe_model` (still wired-valueless → still raises V11)
- [ ] `test_uncovered_params.py::test_seeded_strict_generation_aborts_independently_of_catf_mfe` (`:139`) — **re-anchor** from `unresolvable_attr_probe` to `ife_plant` (non-catf_mfe fixture that still trips strict V11 on shape-4 `magnet_volume`, preserving the "independent of catf_mfe" purpose). **Verify at implement** that `ife_plant` trips V11 at *strict generation*, not just the in-memory collector; if it does not, author a minimal genuinely-unbound seeded fixture (Design → Potential Risks, V11 proof re-anchor).
- [ ] `test_uncovered_params.py` module docstring (`:9–19`) + `test_collector_pins_unresolvable_attr_probe` docstring — drop "the dedicated V11 proof" / "the only committed real-fixture" wording; that title moves to catf_mfe + ife_plant shape-4 (D5). Update the V11 corpus-surface comment block (`:13–18`).
- [ ] `test_alias_agg_probe_generation.py::test_alias_agg_probe_aborts_with_v11_but_identifiers_are_clean` — rewrite raises-V11 → clean generation: `run_codegen` returns True, every `.py` `ast.parse`-valid, registry imports resolve (restores REQ-NC-08 file-parse coverage). Rename to drop "aborts_with_v11".
- [ ] `test_ife_plant.py::test_shape5_plain_usage_override_dropped` — rewrite from "asserts `design_attributes` absence" to "asserts `hierarchy_data.design_overrides` **captures** `baseline_plant.capacity_factor = 0.95` (bare-name LITERAL)"; the def-level 0.90 default stays. Rename to `test_shape5_plain_usage_override_captured`.
- [ ] **new** `test_issue22_generates_clean` (D4) — issue22 generates a clean, `ast.parse`-valid, importable package; author as a shared body / second parametrization of the rewritten `alias_agg_probe` generation test, not a fork.
- [ ] optional: add an `unresolvable_attr_probe` clean-generation assertion (`run_codegen` now returns True — x filled), restoring its file-parse coverage.

### Snapshot diffs expected (Design → Baseline regen)
- [ ] `ife_plant/extraction_snapshot.json` — `design_overrides` gains `baseline_plant.capacity_factor = 0.95`; `calc_usages` unchanged. `baseline_outputs/ife_plant/*` byte-identical.
- [ ] `alias_agg_probe/extraction_snapshot.json` — `design_overrides` gains deep-path `base_cost`; each virtual `cost_model.base_cost` binding → `LITERAL 50.0`, `source_path: null`.
- [ ] `issue22_model/extraction_snapshot.json` — same with `100.0`.
- [ ] `unresolvable_attr_probe/extraction_snapshot.json` — `design_overrides` gains ≥6 entries; `my_calc.x` binding → `LITERAL 5.0`, `source_path: null`. **Must be regenerated** (D1 caveat — omitting it leaves offline pins passing on stale bindings).

### Byte-exact sweep — the INV-5 gate
- [ ] After the two capture-script runs, `git status --short tests/fixtures` shows changes confined to the four `extraction_snapshot.json` files above (plus, if the baseline run churned anything, that is a defect to investigate — design says it should not). The four byte-exact baselines (`solar_battery`, `attr_expr_probe`, `chain_spike`, `sample_model`), `catf_mfe`, `wi014_toy`, and every other snapshot are **byte-identical**.
- [ ] Full suite green: `uv run pytest tests/`. Expected test-count shift: the `alias_agg_probe` V11 xfail/abort flips to a clean-generation pass; enumerate the exact before/after counts against the 1928/4/11 gate in the Phase-2 completion notes.

### Validation
**Automated:**
- [ ] `uv run python scripts/capture_extraction_snapshots.py` → four snapshots change, rest byte-identical.
- [ ] `uv run python scripts/capture_pipeline_baselines.py` → no churn (confirms `capacity_factor` unwired).
- [ ] `uv run pytest tests/` → green.
- [ ] `uv run mypy src/`; `uv run ruff check src/`.

**Manual:**
- [ ] Confirm the re-anchored V11 proof fires: `catf_mfe` strict raise (`test_reconcile_raises_v11_on_wired_gap`) and `ife_plant` strict abort (`test_seeded_strict_generation_aborts_independently_of_catf_mfe`).
- [ ] Inspect the four snapshot diffs match the "expected" list — especially the `widget [3]` expansion in `alias_agg_probe` (how many virtual `cost_model` instances carry a rewritten `base_cost`; Design → Potential Risks, snapshot faithfulness).

**What We Know Works After This Phase:** Plain-usage literals reach params (base_cost consumed → V11 clean); INV-5 proven (exactly four changed); the committed V11 raise proof survives, re-anchored.

---

## Phase 3: Docs / matrix / close-out

### Goal
Move the REQ IDs, reference docs, and close-out notes with the code (R1/R2).

### Changes Required
**See `design.md` for:** Docs / Matrix; agentic-mbse impact.

- [ ] **`reference/25-hierarchy-resolver.md`** — guard relaxation + LITERAL filter + performance note (REQ-HR-08).
- [ ] **`reference/12-virtual-binding-rewrite.md`** — `BindingInfo` shallow-copy (REQ-VBR-08) + bare-name skip-with-DEBUG (REQ-VBR-09); correct the "no committed fixture triggers the bare-name raise" rationale to the by-branch reason (m1: `unresolvable_attr_probe` produces a non-empty index; its reachable source_paths are `::`-qualified so they take the `::` branch, never the bare-name `else`).
- [ ] **`docs/architecture/verification-matrix.md`** — rows for REQ-HR-08, REQ-VBR-08, REQ-VBR-09; `modeling-assumptions.md` §5 as applicable. **Doc 18 (LVP) untouched** (scope 2 cut).
- [ ] **Release-notes-style pin-flip enumeration** — list every checklist row flipped and the test-count shift vs. the 1928/4/11 gate (mirrors Item 7's `release-notes.md` form).
- [ ] **agentic-mbse impact (R2), recorded for close-out** — plain-usage `:>>` **literal** overrides now honored; teach `part x : Type { :>> nested.attr = <literal>; }` as supported (executed in Item 12, once Item 10 lands). Self-named check stays a FAIL against `self_named_binding_trap` (rescue → Item 10). No checker script lands here.
- [ ] **`deep_cross_scope_probe` drift note (m2)** — filed: it has plain-usage LITERAL `:>>` but no committed snapshot and no test reference, so its live extraction changes silently; note it so a future capture is not a surprise.

### Validation
- [ ] Matrix rows resolve to real tests; docs reference correct `file:line`.
- [ ] `uv run pytest tests/`; `uv run mypy src/`; `uv run ruff check src/` — all at their post-item baselines.

**What We Know Works After This Phase:** Requirements traceable; downstream impact (agentic-mbse, Item 10 handoff, deep_cross_scope drift) recorded.

---

## Environment Setup
See CLAUDE.md. Key commands: `uv run pytest tests/`, `uv run mypy src/`, `uv run ruff check src/`. Snapshot regen: `scripts/capture_extraction_snapshots.py` (license), `scripts/capture_pipeline_baselines.py` (license-free).

## Risk Management
**See `design.md#potential-risks`.** Phase-specific mitigations:
- **Phase 2 (highest — snapshot faithfulness):** live re-capture (D1, signed off) eliminates the offline-patch faithfulness risk; the Phase-0 constructed tests already prove the code independent of the snapshot. Inspect the `widget [3]` expansion in the `alias_agg_probe` diff.
- **Phase 2 (V11 re-anchor):** verify `ife_plant` shape-4 trips *strict* V11 (not just the in-memory collector) before relying on it for the "independent of catf_mfe" role; fallback is a minimal genuinely-unbound seeded fixture.
- **Phase 1 (unintended capture):** the LITERAL filter (D3, INV-1) keeps CHAIN/EXPRESSION out of `design_overrides`; the Phase-2 byte-exact sweep is the deterministic guard against a grep-missed fixture.

## Implementation Notes
[TO BE FILLED DURING IMPLEMENTATION]

### Phase 0 Completion
### Phase 1 Completion
### Phase 2 Completion
### Phase 3 Completion

---
**Status:** Draft → In Progress → Complete
