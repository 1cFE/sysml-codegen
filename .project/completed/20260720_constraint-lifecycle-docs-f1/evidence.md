# Evidence — Lifecycle Item 6: Public Documentation and F1 Evidence Reconciliation

Pinned chain: sysml-codegen through Item 5 (`4c6223c`), agentic-mbse `4c18d61`, TEAx
`d545701`. Open predecessors: none (Item 5 landed). This item touches docs, one test
helper, two single-sourced error strings, and one TEAx audit reference. No landed
behavior beyond the sanctioned `TEAX_SIMKIT_PATH` change; no release-readiness claim.

Footprint (codegen): 6 files, +81 / −53. Footprint (teax): 1 line.

---

## 1. RED-first production change — explicit invalid `TEAX_SIMKIT_PATH` fails

The one production-behavior change. Before, `tests/helpers/teax_discovery.py` appended an
explicit path and the checkout-relative sibling to one candidate list and returned the
first valid one — so an **invalid explicit path silently fell through to the sibling**,
hiding the operator's misconfiguration.

**RED.** New test `test_explicit_invalid_path_fails_instead_of_discovering_the_sibling`
(`tests/unit/test_teax_discovery.py:41`) sets `TEAX_SIMKIT_PATH` to an invalid path *with a
valid sibling present* and expects a `RuntimeError`. Against the pre-fix helper:

```
FAILED test_explicit_invalid_path_fails_instead_of_discovering_the_sibling
  - Failed: DID NOT RAISE <class 'RuntimeError'>   (1 failed, 5 passed)
```

**Fix.** An explicitly-set `TEAX_SIMKIT_PATH` is authoritative: it is validated-or-fails,
and the sibling is tried only when no explicit path is set. Policy (explicit is
authoritative) lives at the call site `discover_teax_simkit`; the mechanical
resolve-and-check lives in `_require_simkit_root`. Behavior scoped to codegen test
infrastructure — `discover_teax_simkit` has no `src/` callers (grep: only `tests/`).

**GREEN.** `tests/unit/test_teax_discovery.py` — **6 passed**. The pre-existing
symlink-loop and expanduser-failure tests still pass: the actionable message carries both
`TEAX_SIMKIT_PATH` and the "checkout-relative sibling" remedy.

## 2. F1 evidence at TEAx `d545701`

Environment (per Item 1 evidence §3, teax-simkit needs pandas — its own venv carries it):

```bash
cd /home/reid/1cfe/teax/packages/teax-simkit
../../.venv/bin/python -m pytest \
  simkit/tests/evaluation/test_f1_arithmetic_normalization.py \
  simkit/tests/evaluation/test_f1_arithmetic_fixture.py \
  simkit/tests/evaluation/test_failure_normalization.py \
  simkit/tests/core/test_pipeline_executor_failure_context.py -v
```

Result at HEAD `d545701`: **15 passed**.

**Commit reconciliation.** `git show --stat d545701` carries the F1 code
(`simkit/core/pipeline_executor.py`, `simkit/evaluation/evaluator.py`), the F1 tests, and
`gap-close-f1-normalization/audit.md`. `git show --stat 927a9e1` touches only
`docs/teax-study-explainer.html`. So `927a9e1` provably lacks the change; the audit
header's `927a9e1` was the parent HEAD when the audit was written, corrected to `d545701`.

**Complete report-content comparison across both evaluators**
(`test_f1_arithmetic_normalization.py`, `PreparedEvaluator` vs `FileBackedEvaluator`):

- **Safe cases** (`safe_satisfied`, `safe_violated`, `nonfinite_indeterminate`): full report
  parity — `prepared.responses == file.responses == expected` **and** `prepared.outputs ==
  file.outputs` (test lines 230-231). This is the exact complete-report comparison.
- **Arithmetic-failure cases** (`division_by_zero`, `zero_negative_power`,
  `exponent_overflow`, `nested_division`): both backends raise `EvaluationFailed` with an
  **identical normalized failure record** (`phase`, `module_or_channel`, `cause`) and an
  identical chained `__cause__` (original exception type, message, traceback through
  `predicates.py` and the constraint module), test lines 159-169. On failure no report is
  persisted — the file-backed output tree is asserted **absent** (line 171); earlier
  channel work stays internal (`test_later_failure_keeps_earlier_work_internal_without_aggregate`).

**Surfaced limitation (not reimplemented — out of Item 6 scope).** The shared normalizer
hardcodes `phase=EvaluationPhase.MODULE_EXECUTION` (`evaluator.py:62`); `OUTPUT_WRITE` is
defined (`failure.py:23`) but never emitted anywhere in `evaluator.py` (only
`MODULE_EXECUTION` and `PREPARATION` are set). So the cross-backend failure-record parity
is over a single always-`MODULE_EXECUTION` phase, and the failure path writes no report
JSON to compare. This is epic Item 11's obligation ("Emit `OUTPUT_WRITE` honestly or
collapse the unused phase"), recorded here, not fixed here.

## 3. Repository gates (codegen)

| Gate | Result |
|---|---|
| Full suite (license sourced) | **3,064 passed, 44 skipped, 17 deselected, 0 failed** (62.8s) |
| Skips (`-rs`) | all conditional/no-scenario/license-gated with stated reasons; **no bare license skips** |
| Affected units (teax_discovery, predicate_compiler, package_metadata, graph_extension) | 67 passed |
| Mypy `src/` | **72 errors in 17 files** — equal to the Item 4/5 baseline (zero added) |
| Ruff `check src/` | clean |
| Ruff `format --check` (touched files) | 5 files already formatted |
| Remaining `executable-profile/v3` in `src`/`docs`/`tests` | none (grep empty) |
| Baselines baking the v3 error string | none |

License sourced via `set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a`
(per the `syside license key explicit env needed` note).

## 4. Doc/code corrections (see spec.md §3 for per-claim citations)

- `docs/architecture/reference/27-snapshot-generation.md` — S1 (version 3→5), S2
  (`source_file` re-absolutize → v5 `root-N/` referent), S3 (v2→v5 migration record), S4
  (profile v3→v4), S5 (floor 0.1.1→0.1.2). Amendments in place; no "used to say" prose.
- `docs/architecture/verification-matrix.md:531` — S6 (current 3→5; cross-version).
- `src/sysml_codegen/generation/predicate_compiler.py:150,201` — S7/S8, duplicate version
  literals single-sourced from `PROFILE_SEMANTIC_VERSION`; test re-matched on
  `executable-profile/v\d` so it cannot re-drift.
- `teax/.project/active/gap-close-f1-normalization/audit.md:6` — `927a9e1` → `d545701`
  (committed in the teax repo, no push).

## 5. PR-description drafts (no push, no PR edit)

- `PR_DRAFT_agentic_mbse_11.md` and `PR_DRAFT_codegen_9.md` in this directory reconcile the
  open PR descriptions to Items 1–5 landed locally + Item 6, with **no release-readiness
  claim** and the machine-enforced merge order noted (agentic-mbse #11 first — codegen pins
  `constraint-facts/v2` and `executable-profile/v4` via `_upstream_pins.py`, so merging #9
  first breaks its `main`). The final PR update/push is Item 13's, after certification.

## 6. Preservation

- `.claude/projects/` untracked, never staged.
- No fixture/`baseline_outputs` bytes changed (docs, one test helper, two error strings,
  one teax doc line).
- Snapshot format v5, profile `executable-profile/v4`, package 0.1.0 — unchanged; this item
  documents them, it does not move them.
