# Execution-lane run log (Item 7 Phase 4, N6)

Appended, never overwritten — an unrun or failing lane must stay visible, not assumed green.

## 2026-07-13 — first execution-lane run

**Teax state:** `/home/reid/1cfe/teax` checked out at branch `constraint-exec-epic`, HEAD
`4ac920b`. Verified `main` HEAD `7560d65` (the plan's pin) is an ancestor of this HEAD
(`git merge-base --is-ancestor 7560d65 HEAD` → true), and
`packages/teax-simkit/simkit/io/writers.py` carries `write_json_primitive` with
`PRIMITIVE_TYPES` validation at this HEAD. **Decision: persist-and-assert in force** —
matches the orchestrator's 2026-07-12 pin; re-verified independently here rather than
assumed.

**Invocation:**
```
SYSIDE_LICENSE_KEY=<key> UV_CACHE_DIR=/tmp/agentic-mbse-uv-cache \
PYTHONPATH=/home/reid/1cfe/sysml-codegen/src:/home/reid/1cfe/teax/packages/teax-simkit \
uv run --directory /home/reid/1cfe/agentic-mbse python -m pytest \
  -m execution -p no:cacheprovider --override-ini="addopts=" \
  --rootdir /home/reid/1cfe/sysml-codegen \
  /home/reid/1cfe/sysml-codegen/tests/execution -v
```

Note: the syside license loads via an explicit `SYSIDE_LICENSE_KEY` env var (present in this
repo's `.env`, but not sourced by ambient shell env or a bare `uv run python -c ...` probe —
must be passed explicitly per invocation). This corrects prior sandbox assumptions
(`@requires_license` tests were believed unrunnable here); they are not — see the codegen-venv
full-suite run below.

**Results (first pass — 2 failures, both real bugs, both fixed before the passing run below):**

| Test | Result | Notes |
|---|---|---|
| `test_s4_slice_both_truth_values` | FAIL → FIXED → PASS | See Bug 2 below |
| `test_zero_assertion_aggregator_not_assessed` | FAIL → FIXED → PASS | Blocked by Bug 1 (unrelated to this test's own assertions) until the pipeline-yaml entry-point requirement was satisfied in the test fixture itself |
| `test_multi_instance_expansion_n_modules_one_predicate` | FAIL → FIXED → PASS | See Bug 1 below |

**Bugs found and fixed by this lane:**

1. **D9 class-name derivation produced invalid Python identifiers for occurrence-indexed
   part_def owners** (`analysis/constraint_lowering.py::_constraint_module_type`).
   `owner_instance_path` carries `[i]` occurrence brackets (e.g. `cell[0]`) for a part_def
   with multiple occurrences; the class-name derivation passed them through unescaped,
   producing `Cell[0]NonnegConstraintModule` — a `SyntaxError` at import time, not a
   generation-time failure. Fixed: brackets replaced with `_` before Pascal-casing, so three
   occurrences now derive three distinct, valid identifiers (`Cell0`, `Cell1`, `Cell2`).
   Caught by `constraint_multi_instance` (three occurrences) — `wi014_toy` (single instance,
   no brackets) never exercised this path.

2. **Aggregator field names used the raw, sha-suffixed `constraint_id` directly as a Python
   identifier** (`analysis/constraint_lowering.py`'s aggregator-input construction +
   `generation/modules.py::render_report_aggregator`). Same root cause as (1): a
   bracket-bearing `constraint_id` reaching a Pydantic field declaration is a `SyntaxError`.
   Fixed: the aggregator's `ModuleInput.param_name` (and hence its rendered field name) is
   now `sanitize_name(constraint_id)`, not the raw string — the wiring channel and the
   `ConstraintEvaluation.constraint_id` runtime string are untouched, only the
   Python-identifier site changed.

3. **`plant_budget`-shaped constraint-only design attributes minted with `default_value=None`
   always** (`analysis/constraint_lowering.py::extend_graph_with_constraints`'s
   `DESIGN_ATTRIBUTE` mint call hardcoded `None`). This produced a JSON input template
   missing the key entirely, failing pydantic validation on load — a design attribute
   referenced *only* by an assert (never by a calc) never got its real default. Fixed: added
   `ParameterGroupDeriver.design_attribute_default_value(qn)` (mirrors the existing
   `float(attr.default_value)` conversion already used for calc-referenced design
   attributes) and wired it into the mint call. This is the bug that actually blocked SC-1 —
   `wi014_toy`'s `plant_budget` is exactly this shape (asserted against, never calc-consumed).

All three are Item-5-file touches beyond D11's already-surfaced `if eligible:` relaxation.
Surfaced here per capture-fidelity §4 rather than folded silently into the diff: each is a
narrow, load-bearing correction the execution lane exists to catch (fail-loud generation
tests cannot see a `SyntaxError` in an *executed* import, or a JSON schema validation gap
that only bites at simkit load time) — none is a redesign, each is a one-function fix with a
clear before/after.

**Second pass, after fixes — all green:**

| Test | Result |
|---|---|
| `test_s4_slice_both_truth_values` | PASS |
| `test_zero_assertion_aggregator_not_assessed` | PASS |
| `test_multi_instance_expansion_n_modules_one_predicate` | PASS |

**Regression check (codegen venv, license present):** `uv run pytest tests/` → 2231 passed,
4 skipped, 3 deselected (the execution-marked tests) — zero failures, zero errors. This is
the *first* fully-green run of the full suite in this session; every prior "23 failed / 96
errors" baseline reading in this epic's Phases 1-3 was a sandbox license-availability
artifact (`SYSIDE_LICENSE_KEY` not exported to ambient shell env), not a real baseline — see
the memory note filed alongside this run log.

## 2026-07-13 — audit cures (Phase 6)

Same teax state as the entry above (`main` HEAD `7560d65` an ancestor of the checked-out
`constraint-exec-epic` HEAD) — not re-verified independently this run since nothing in
teax/simkit changed between the two runs in the same session.

**New execution-lane tests (invocation identical to the entry above):**

| Test | Result | Criterion |
|---|---|---|
| `test_indeterminate_point_at_execution` | PASS | SC-2: non-finite operand -> `indeterminate`, `actual_value is None`, `margin is None` |
| `test_negated_inline_assertion_at_execution` | PASS | SC-2: negated inline assertion, correct status + sign-flipped margin |
| `test_modeled_default_override_flips_verdict` | PASS | SC-3: unmodified default -> satisfied; overriding the entry parameter -> violated |
| `test_break_the_yaml_surfaces_execution_failure` | PASS (raises as required) | Break-the-YAML: rewiring the aggregator's evaluation-channel reference in the generated YAML surfaces as an execution failure through the executor, not a silent gap |

Full execution lane after the additions: **7/7 pass** (the 3 from the prior run plus these 4).

**New offline CI regression pins** (`tests/unit/test_phase4_bugfix_regressions.py`) —
verified to go RED on revert (each fix was reverted in isolation, the corresponding test
failed with the exact bug's symptom, then the fix was restored via `git checkout`):

| Test | Reverted fix | Failure reproduced |
|---|---|---|
| `test_occurrence_indexed_constraint_modules_have_valid_class_names_and_parse` | bracket-strip in `_constraint_module_type` | `'TheDesignCCell[0]NonnegConstraintModule'.isidentifier()` is `False` |
| `test_occurrence_indexed_aggregator_fields_are_valid_identifiers_and_parse` | `sanitize_name(c.constraint_id)` | raw bracketed `constraint_id` used as a field name fails `.isidentifier()` |
| `test_constraint_only_design_attribute_gets_real_default_not_none` | `design_attribute_default_value` wiring | minted entry point's `default_value` is `None` instead of `5000.0` |

**Full-suite regression check (codegen venv, license present):**
`SYSIDE_LICENSE_KEY=<key> uv run pytest tests/` -> **2236 passed, 4 skipped, 7 deselected
(execution-marked), zero failures, zero errors.** `ruff check src/` clean. `mypy src/` — 76
errors, baseline held exactly. Byte-identity (INV-7) re-confirmed:
`test_graph_assembly.py::TestBaselineComparison`,
`test_pipeline_e2e.py::TestBaselineComparison`,
`test_e2e_output_registry.py::TestYamlDiffValidation` — 11/11 pass.

All four audit cures (SC-2, SC-3, Break-the-YAML, three CI regression pins) are closed.
