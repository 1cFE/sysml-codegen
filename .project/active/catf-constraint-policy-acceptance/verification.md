# Verification — CONSTRAINT-SEMANTICS Item 5

**Item:** CATF Derivative and End-to-End Acceptance
**Plan:** `plan.md` (committed `18f51e1`)
**Started:** 2026-08-13

Numbers here are recorded exactly, never summarized (SC-7). Every licensed run records its
`no live syside license` skip-line count, because zero is the only proof it really ran licensed.

---

## Phase 0 — Baseline and environment proof

### Test invocation

`/home/reid/1cfe/item7-rebuild-venv/bin/python -m pytest tests/`, licensed via
`set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a`.

`pyproject.toml:46` sets `addopts = -v --tb=short -m "not execution"`, so the default
invocation deselects the `execution`-marked tests. Both marker sets are recorded below,
because the plan's inherited floor did not say which one it counted.

| run | invocation | passed | skipped | deselected | failed | `no live syside license` lines |
|---|---|---|---|---|---|---|
| default marker set | `pytest tests/` | **2012** | **34** | 79 | 0 | **0** |
| all markers | `pytest tests/ -m ""` | **2090** | **34** | 0 | **1** | **0** |

**The one failure is environmental, not a regression.**
`tests/execution/test_fusion_tea_real_teax.py::test_the_lane_runs_the_real_simkit` fails with

```
AssertionError: the in-repo stub runner was imported on the real-TEAx lane;
its fake simkit would shadow the installed one
```

That lane must be hosted in the agentic-mbse venv with a `sys.path` insert of
`teax/packages/teax-simkit`; the task venv makes the in-repo stub importable. It is
pre-existing at this HEAD and unrelated to any Item 5 edit (the only tree change at the time
of the run is d5's PROVENANCE prose).

### Deviation from the inherited floor — recorded, not absorbed

The plan carries **2050 passed / 34 skipped** as the Item 3 close baseline. Neither measured
number equals it: 2012 (default markers) and 2090 (all markers). Skipped is **34 in both**,
matching exactly.

Account: 2050 sits between the two, so the gap is the marker set plus test churn. Item 4
(`constraint-predicate-hardening`) landed after the 2050 measurement and added tests, which
is consistent with all-markers now reading 2090 ≈ 2050 + 40. **No test was lost** — the
skipped count is identical and no test that passed at Item 3 close is failing here.

**The floor for the rest of this item is the measured HEAD baseline, not the inherited
number:** all markers **2090 passed / 34 skipped / 1 environmental failure**, default markers
**2012 passed / 34 skipped**, zero license-skip lines on both. Surfaced to the orchestrator.

### Lint and type floors

| check | measured | expected |
|---|---|---|
| `ruff check src/` | **12** | 12 ✓ |
| `mypy src/` | **55 errors in 11 files (71 source files)** | 55 ✓ |
| `git diff --check` | clean (exit 0) | clean ✓ |

### TEAx tip

```
git -C /home/reid/1cfe/teax rev-parse --short HEAD   → 5b70ae9
git -C /home/reid/1cfe/teax rev-parse --abbrev-ref HEAD → constraint-semantics-item3
```

Matches the plan. The checkout stays on that branch for the whole item.

### `catf_mfe_d5` measured, for the corrected PROVENANCE paragraph

From the committed `tests/fixtures/catf_mfe_d5/instance_graph_snapshot.json`, projected
license-free:

| quantity | measured |
|---|---|
| modules | **43** |
| `usage_records` | **65** |
| `concrete_entries` | **0** |
| `excluded_records` | **9** |
| disposition histogram | `{non_reaching: 56, excluded: 9}` |

**Deviation:** the plan and spec prose say the model "has built 42 modules". The measured
count is **43**. 43 is the number consistent with every design probe delta (P1 44 = 43+1,
P2 45, P6 46, P7 48), so 42 was the stale figure. No expectation is derived from it; the
corrected d5 paragraph records the measured 43.

### Frozen twins

`python scripts/make_d5_variant.py --check <source> <target>` for all three pairs:

```
catf_mfe_model catf_mfe_d5           → strip check: 0 problems
solar_battery_model solar_battery_d5 → strip check: 0 problems
gate_a gate_a_d5                     → strip check: 0 problems
```

`git diff --stat tests/fixtures/catf_mfe_d5/` → exactly one file,
`PROVENANCE.md`, 11 insertions / 18 deletions — the stale acceptance paragraph and the
superseded "what blocks it" section. No model byte changed. `catf_mfe_model` untouched.
