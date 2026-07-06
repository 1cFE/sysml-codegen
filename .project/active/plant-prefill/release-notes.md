# Release Notes — Item 9: Plant-Idiom Literal Pre-Fill (SC-5 stage 1)

**Epic:** UPSTREAM-FINDINGS Item 9
**Branch:** upstream-findings-epic
**Date:** 2026-07-05

## What changed (three one-function edits)

1. **`extraction/hierarchy_resolver.py` — `extract_design_overrides`** (REQ-HR-08).
   Dropped the per-usage `owned_redefinitions` skip so plain typed usages' member
   `:>>` overrides are scanned too. A newly-scanned **plain**-usage override is kept
   only when its RHS is LITERAL (`_keep_plain_usage_override`, D3); the `part
   redefines` path is unchanged (all RHS types). CHAIN/EXPRESSION plain overrides
   (Item 10's job) never enter `design_overrides`.
2. **`orchestration/pipeline_builder.py` — `_rewrite_virtual_bindings`** (REQ-VBR-09).
   The bare-name `source_path` `raise ValueError` became a skip-with-DEBUG. Crash-safe
   now that the relaxed capture guard can make the override index non-empty.
3. **`extraction/usage_extractor.py` — `_create_virtual_calc_usage`** (REQ-VBR-08).
   `bindings=list(template.bindings)` → `[copy.copy(b) for b in template.bindings]`
   (+ `import copy`), so sibling virtual instances never share a `BindingInfo`.

## Pin-flip enumeration (every checklist row)

| Test | From → To |
|---|---|
| `test_uncovered_params.py::test_collector_pins_alias_agg_probe` | `[("base_cost","cost_model")]` → `[]` |
| `test_uncovered_params.py::test_collector_pins_issue22_model` | `[("base_cost","cost_model")]` → `[]` |
| `test_uncovered_params.py::test_collector_pins_unresolvable_attr_probe` | `[("x","my_calc")]` → `[]` (`local_val=5.0` fills `x`) |
| `test_uncovered_params.py::test_reconcile_raises_v11_on_wired_gap` | re-anchored `unresolvable_attr_probe` → **`catf_mfe_model`** (still wired-valueless CHAIN → still raises V11) |
| `test_uncovered_params.py::test_seeded_strict_generation_aborts_independently_of_catf_mfe` | re-anchored `unresolvable_attr_probe` → **`ife_plant`** (shape-4 `magnet_volume`, non-catf_mfe strict-V11 abort) |
| `test_uncovered_params.py` module docstring + `test_collector_pins_unresolvable_attr_probe` docstring | dropped the "dedicated V11 proof" wording; the committed V11-proof title moved to catf_mfe + ife_plant shape-4 (D5) |
| `test_alias_agg_probe_generation.py` | raises-V11 → clean generation, parametrized over `alias_agg_probe` + `issue22_model` (D4); renamed `test_plain_usage_literal_fixture_generates_clean`; restores REQ-NC-08 file-parse coverage |
| `test_ife_plant.py::test_shape5_plain_usage_override_dropped` | "asserts absence" → "asserts capture" of `baseline_plant.capacity_factor = 0.95` in `design_overrides`; renamed `test_shape5_plain_usage_override_captured`; per-shape label updated to "captured (Item 9)" |

New test file: `tests/unit/test_virtual_binding_rewrite.py` — divergent-sibling
(REQ-VBR-08), bare-name skip (REQ-VBR-09), LITERAL-filter predicate (REQ-HR-08).

## Snapshot regen — exactly four fixtures (INV-5)

Live re-capture (`scripts/capture_extraction_snapshots.py`, license) changed exactly:
- `ife_plant` — `design_overrides` gains `baseline_plant.capacity_factor = 0.95`
  (bare-name LITERAL); `calc_usages` unchanged (unconsumed).
- `alias_agg_probe` — deep-path `base_cost` override captured; virtual `cost_model.base_cost`
  binding → LITERAL 50.0, `source_path: null`.
- `issue22_model` — same, 100.0.
- `unresolvable_attr_probe` — 6 `design_overrides`; `my_calc.x` → LITERAL 5.0, null.

Every other committed snapshot reverted to byte-identical (per the approved
timestamp-only + orthogonal-drift revert; see the deferred stale-fixture-refresh chore
in `BACKLOG.md`). `baseline_outputs/` untouched (capacity_factor never enters the graph).

## Test-count shift vs. the 1928/4/11 gate

Pre-item gate: 1928 passed / 4 skipped / 11 xfailed. Item 9 adds
`tests/unit/test_virtual_binding_rewrite.py` (3 tests) and the parametrized
generation test gains a second case (issue22). Skips and xfails are unchanged —
Item 9 adds no V-rule and no xfail; it *satisfies* V11 for the plain-usage LITERAL
class (three collector pins flip to `[]`) while re-anchoring the committed V11 raise
proof onto catf_mfe + ife_plant shape-4.

> **Gate status caveat:** the full `uv run pytest tests/` / `mypy` / `ruff` re-run
> could not be executed in the implementing session — the permission sandbox blocked
> all command execution after the snapshot capture. Phase-0/1 ran green before the
> block (unit tests 3/3; suite 1931/4/11; mypy 109; ruff 21). The pin-flip edits and
> re-captured snapshot data were verified by direct git/JSON inspection. **The final
> gate re-run remains to be executed** — see `plan.md` Phase-2/3 notes.

## agentic-mbse impact (R2 — for close-out)

- **New supported shape to teach:** plain-usage `:>>` **literal** overrides are now
  honored — MODELING_GUIDE / sysml-conventions should present
  `part x : Type { :>> nested.attr = <literal>; }` as supported. Execute in Item 12,
  once Item 10 lands. No checker script lands here.
- **Self-named-binding check** stays a FAIL/advisory against `self_named_binding_trap`
  until Item 10 (the rescue is deferred; this item only made the path crash-safe).

## modeling-assumptions §5

No change. Item 9 adds no V-rule; it satisfies V11 for the plain-usage LITERAL class.
The V11 raise proof survives, re-anchored (catf_mfe strict raise; ife_plant shape-4
strict abort).

## deep_cross_scope_probe drift note (m2)

`deep_cross_scope_probe` has plain-usage LITERAL `:>>` (`reading = 10.0`,
`baseline_value = 2.0`) but **no committed snapshot and no test reference**, so its
live extraction now changes silently with nothing asserting it. Flagged here so a
future snapshot capture of it is not a surprise. (Distinct from the stale-fixture
refresh chore, which covers fixtures that *do* have committed snapshots.)
