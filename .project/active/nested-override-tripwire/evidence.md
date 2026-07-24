# Evidence — nested-override-tripwire

**Date:** 2026-07-24. **Branch:** `nested-override-tripwire` (baseline: docs-lifecycle-sync tip,
`80e8939`). **Scope:** a warning for the `[NESTED-OCCURRENCE-OVERRIDE]` silent-value-loss shape.
No resolution behavior change, no new synthesis, no output change.

## Phase 0 — corpus false-fire scan (gate: PASS)

Probe: `probes/unmatched_override_scan.py`. Verdict: `probes/verdict.md`.

Scanned all 19 fixtures in `tests/conformance/conftest.py::SNAPSHOT_MODELS` (150 demands) from
committed snapshots, license-free.

- The name-only candidate **false-fires 4×** — `solar_battery_model` (1), `issue22_model` (1),
  `alias_agg_probe` (2). All four are `::` reference-form demands naming a **library
  definition**, whose value resolves through the aggregation path. Warning there would be the
  site-4 / D3-12 story again.
- The shipped predicate adds a **shape gate** (dotted `part_usage.attr` demands only) and a
  **part-usage gate** (the override must name the demanded part usage via its owning-QN leaf or
  its `target_path`). **Clean-corpus fires: 0.**

To express the shape gate, `_BindingTarget` gained a diagnostics-only
`form: Literal["dotted","reference","bare"]` field set by `_binding_target`'s three branches. No
resolution tier reads it.

The recorded coordinate fixture `tests/fixtures/nested_occurrence_override_probe/` has no
committed snapshot (it is expected to halt), so it cannot be a probe positive control. The
positive case is pinned by unit test instead — see below.

## Phase 1 → 2 — RED → GREEN

Three tests appended to `tests/unit/test_supplied_values.py`:

| test | asserts | RED |
|---|---|---|
| `test_unmatched_nested_override_warns_with_both_scopes` | the BACKLOG coordinate (captured `..._Design__panel` vs demanded `..._the_design__panel`, `target_path=['source','reading']`, LITERAL 80.0) warns, naming both scopes, the target QN, and `[NESTED-OCCURRENCE-OVERRIDE]`; synthesizes nothing | **failed before implementation** (`assert []`) |
| `test_silent_fallthrough_with_no_matching_override_stays_silent` | INV-6: an ordinary silent fall-through with no same-name capture stays silent | passed throughout (guards against over-firing) |
| `test_unmatched_override_on_other_part_usage_stays_silent` | the part-usage gate: a same-named override on a different usage does not fire | passed throughout |

Implementation (`src/sysml_codegen/resolution/supplied_values.py`):

- `_unmatched_override_scopes` — mechanism: the captured scopes of overrides that speak to this
  target but matched no tier. Returns `[]` for every non-dotted shape.
- Policy at the call site, inside the silent fall-through branch of
  `enrich_graph_design_attributes` (the `else` beside `nonliteral` / `malformed_literal`):
  collect `(target, captured_scopes, demanded_scopes)`, drain once after the loop as one
  `logger.warning` per target, following the `collisions` / `malformed_targets` idiom (I7: one
  logical warn per normalized target).

`probes/unmatched_override_scan.py` now delegates its tight variant to the shipped
`_unmatched_override_scopes`, so a later edit to the warning cannot silently invalidate the
verdict. Re-run after implementation: still `tight=0` on the clean corpus.

## Phase 3 — gates

- **Full suite with license** (`set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a; uv run
  --frozen pytest -q -rs tests/`): **3118 passed, 47 skipped, 18 deselected** in 66s. Baseline
  was 3115 / 47; the +3 are the new tests. `grep -ci "no live syside license"` over the `-rs`
  skip report: **0** — the license was live.
- `uv run ruff check src/` — **All checks passed.**
- `uv run mypy src/` — **72 errors**, exactly the accepted pre-existing baseline; none new.
- **No output change:** the conformance suite byte-compares generated output against committed
  baselines, and it is green in the run above. That green IS the no-output-change proof. The
  tripwire only adds a log record on a path that already `continue`d.

## Phase 4 — bookkeeping

- `.project/backlog/BACKLOG.md` — `[NESTED-OCCURRENCE-OVERRIDE]` amended with the tripwire note;
  the occurrence → definition bridge remains the filed work.
- `docs/architecture/modeling-assumptions.md:358` — "falls to a silent manual-required entry
  point" → "falls to a manual-required entry point (value dropped, with a WARN naming both the
  captured and the demanded scope — a tripwire added 2026-07-24, not a fix)". Rest intact.
- `tests/fixtures/nested_occurrence_override_probe/PROVENANCE.md` — **not touched**: it never
  claims the calc path is silent (it says the binding "loses the same value ... falls to a
  manual-required entry point"), which is still exactly true.

## What this is not

Not the occurrence → definition bridge. The modeled value is still dropped on the calc path and
the constraint path still halts under strict INV-2. The only change is that the calc path no
longer drops it in silence.
