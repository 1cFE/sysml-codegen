# Audit: Calc-Seam Cutover — Retire ExpressionAST (Item 13)

**Verdict:** Certify-with-notes
**Audited:** 2026-07-13
**Branch:** constraint-exec-epic
**Commit range:** `7dcae90^..2b00261` (Phases 0–4)

---

## Summary

The item does what it set out to do: the two production calc consumers (`compile_calc_def`,
`computed_attribute_extractor`) now render Python expression strings from `ExpressionIR` via a
new compat renderer, `ExpressionAST` + its two compile functions are deleted, and a grep gate
locks the door. The migration is byte-identity-clean by the strongest static evidence
available: **git shows zero changes to any existing fixture, baseline, or snapshot across the
whole item** — the only corpus additions are the three new golden files. Deletion is complete,
the skip-count jump is fully accounted for by content-gated golden tests (not masked failures),
and both unplanned fixes are structural with genuine regression coverage.

The one limit on the verdict is environmental, not substantive: this sandboxed non-interactive
session cannot execute pytest/mypy/ruff (approval-gated and denied, even with the sandbox
disabled). So the live green suite, the `mypy 76` baseline, ruff, and the actual pass of the
`@requires_license` goldens are **plan-claimed and statically corroborated, not
audit-reproduced.** The Requested Live Probes section lists exactly what a licensed run must
confirm to convert this to an unconditional Certify.

## Findings

### Plan completion

All five phases (0–4) are present in the commit chain and each phase's completion note in
`plan.md` matches the committed code. Verified statically:

- **Phase 0** — `calc_compat_renderer.py` + `test_calc_compat_parity.py` present; parity test
  is `@requires_license`, parametrized over the capture-script corpus (reused, not re-listed —
  can't drift). ✓
- **Phase 1** — seam swap at `expression_compiler.py:294–319`; golden test present. ✓
- **Phase 2** — computed-attr FORMULA branch swapped at `computed_attribute_extractor.py:296–307`
  with empty `member_names`; golden test present. ✓
- **Phase 3** — verification-only, no code change (git confirms no src change in `1bf77e2`). ✓
- **Phase 4** — deletion + test-surface migration + grep gate. ✓

No placeholder code, no TODOs, no partial implementation found in the changed source.

### Spec conformance

- **SC1 — seam renders through IR + compat renderer; `build_expression_ast`/`compile_expression`
  no longer compile calc outputs.** ✓ `compile_calc_def` (`expression_compiler.py:298–319`)
  calls `extract_expression_ir → render_calc_expression → collect_calc_refs`;
  `computed_attribute_extractor.py:298–303` does the same. Both old functions are deleted.
- **SC2 — every corpus calc expr renders byte-identically before each flip; S2 proof kept as a
  test until deletion.** ✓ The Phase-0→3 live parity test asserted `render_calc_expression(...)
  == compile_expression(build_expression_ast(...))` with both paths present; at Phase 4 it froze
  the old-path strings + ref lists into `calc_compat_parity_golden.json` (D4) and now asserts
  the renderer against that golden. Spot-checked the golden: it preserves the int/float
  distinction (`(inputs.a * 2)` vs `(inputs.base * 2.0)`) — the actual byte-identity failure mode.
- **SC3 — packages byte-identical after each staged step.** ✓ (static) Git diff `7dcae90^..2b00261`
  shows **no** change to any pipeline baseline or generated-package fixture; per-phase notes
  report `capture_pipeline_baselines` zero-diff + `test_factory_purity` green. Live re-run not
  reproducible here (Probe P3).
- **SC4 — `ExpressionAST`, `build_expression_ast`, `compile_expression` deleted + grep gate.** ✓
  Independently grepped: none of the three (nor `ExpressionNodeType`, `PYTHON_OPERATOR_MAP`)
  appear as code in `src/`. The one `_collect_refs` hit is prose in a docstring
  (`calc_compat_renderer.py:145`), out of the gate's 3-symbol scope. Grep gate
  `test_no_expression_ast.py` scans all of `src/sysml_codegen` line-by-line for the three
  substrings.
- **SC5 — serialized calc-compilation section round-trips byte-identically; `--from-snapshot`
  packages byte-identical; re-capture only if shape changes.** ✓ (static) No snapshot corpus
  bytes changed across the item; INV-3 shape frozen (below). Live `--from-snapshot` diff not
  reproducible here (Probe P3).
- **SC6 — full suite green; mypy clean; ruff clean.** Partially verifiable. See Gates + Note 1
  (mypy is a 76-error *baseline*, not literally clean; the item adds zero new errors by
  intent — the `if ir is None: raise` guard at `:300` exists to avoid one). Live run required
  (Probes P1–P2).

**Non-goals respected.** No new operators/invocation/feature-chains (renderer *rejects* chains
and invocations with `CompilationError`, `calc_compat_renderer.py:80,109`); predicate compiler
untouched; `shared_aggregation` untouched. The spec's surfaced scope correction (aggregation
walking is out of scope) is honored — nothing there was modified.

### Design conformance

- **D1 (one renderer module in `extraction/`, self-contained, not shared-dual-mode).** ✓
  `calc_compat_renderer.py` imports only the kept `CompilationError`/`_sanitize_name` from
  `expression_compiler`; own operator map (deliberately not importing the to-be-deleted
  `PYTHON_OPERATOR_MAP`).
- **D3 (renderer reproduces validation + error path).** ✓ `render_calc_expression` runs
  `python_ast.parse(mode="eval")` and raises the kept `CompilationError` on unresolved refs /
  unparseable output, so caller `except CompilationError → MANUAL_REQUIRED` is unchanged.
- **D4 (parity test → committed golden at deletion).** ✓ As above.
- **M3 (seam name sets).** ✓ `member_names = output_names | (all_member_names or set())`
  (`:297`) — the union, not `all_member_names` alone.
- **M2 (literal rule keyed on IR literal type).** ✓ `_render_literal` keys on `literal.kind`
  substring, deliberately *not* `operand_type.category` (see unplanned fix 1).
- **INV-1 (per-function comparand).** ✓ Stage 1 golden is the full `CalcDefCompilationResult`
  (strings + ref lists + compilability + execution_order); Stage 2 golden is
  `compiled_expression` + `compilability`; parity golden is strings + ref-list tuples.
- **INV-3 (shape frozen).** ✓ No field line of `CompilationResult` / `CalcDefCompilationResult`
  changed in the diff (the only removed lines in that file are the deleted `_collect_refs` body).
- **INV-4 (no silent replacement).** ✓ Verified above.
- **Symbol inventory** exactly matches design Component Overview: kept `Compilability`,
  `CompilationError`, `CompilationResult`, `CalcDefCompilationResult`, `_sanitize_name`,
  `classify_compilability`, `_topological_sort`, `compile_calc_def`; deleted the six retired
  symbols. `compile_calc_def`'s orchestration (undeclared-intermediate discovery, topological
  sort) stayed in place (`:223–297`) — not moved, as designed.

### The skip-count jump (4 → 23) — fully accounted for

Every one of the +19 new skips comes from the three new golden/parity test files, each
`@requires_license` **and** parametrized over the 29-fixture corpus with a per-fixture
`pytest.skip` when that fixture carries no applicable construct:

| test | pass | skip | skip reason |
|---|---|---|---|
| `test_calc_compat_parity` | 28 | 1 | `agg_literal_probe`: no calc output expressions |
| `test_compile_calc_def_golden` | 28 | 1 | `agg_literal_probe`: no calc defs with outputs |
| `test_computed_attribute_golden` | 12 | 17 | 17 fixtures have no computed attributes |

1 + 1 + 17 = **19**; 4 (pre-existing) + 19 = **23**. A `git diff` of the test tree for added
`mark.skip`/`mark.xfail`/`pytest.skip`/`requires_license` shows these three files are the
**only** new skip sources; no existing test was newly skipped or xfailed to hide a failure
(the removed-marker grep is empty). **No skip masks a should-run test.**

**Critical cross-check on the "fake green" risk** (`memory: syside-license-key-explicit-env-needed`):
`requires_license` is `skipif(not _license_available())` (`conftest.py:40`). If the license had
**not** loaded, all 3 golden tests skip *every* parametrization (~87 skips, ~68 fewer passes) —
the count would be ≈2249/91, not the reported 2317/23. The observed 23 is arithmetically
consistent **only** with a license-present run in which the goldens actually executed. This is
the internal-consistency evidence that the parity/golden gates ran and did not silently skip.
(Direct re-execution: Probe P1.)

### The two unplanned fixes

Both are structural and regression-covered:

1. **Phase 1 — literal keying on mocks.** `_render_literal` was re-keyed from
   `operand_type.category` (which is `"unresolved"` whenever `cached_result_type` is absent —
   real syside resolves it, a hand-built mock doesn't) onto `literal.kind`
   (`calc_compat_renderer.py:98–100`), using the same substring convention `SysideAdapter.is_instance`
   uses. **Regression test:** `_ir_literal` builds `LiteralFact(kind=..., result_type=None)`
   and `TestRenderCalcExpression` asserts int `42→"42"` and float `3.14→"3.14"`
   (`test_expression_compiler.py:113,119`). Under the old category-keying these fail
   (`result_type=None → unresolved → CompilationError`), so they genuinely pin the fix.
2. **Phase 4 — `mock_syside_adapter` fixture redirect.** Four fixtures patched
   `expression_compiler.SysideAdapter.is_instance`, an attribute path that vanished when
   `expression_compiler` stopped importing `SysideAdapter`. Two dropped the now-redundant line;
   two redirected to the canonical `agentic_mbse.sysml.syside_adapter.SysideAdapter.is_instance`
   (`test_expression_compiler.py:470`). This is test-infra repair (no production behavior
   change); its coverage is the `TestCompileCalcDef` suite that uses the fixture and still
   exercises the new seam. Correctly scoped — not deferred, since these are
   `compile_calc_def`-level tests, not the `build_expression_ast`-dialect tests Phase 4 owns.

### REQ-AST-04 update — invariant still has teeth

`test_ast_dispatch_invariant.py` counts were dropped 4→3 (dual-check FCE+OE sites) and 6→5
(multi-type dispatch functions) with an explaining comment (`:270–271,300–301`). The invariant
is **not** a hardcoded literal: both tests call `find_all_dispatch_functions(SRC_ROOT, ...)`,
which live-scans source for functions doing `is_instance()` dispatch on the expression type
names, then assert the count. The drop is real — `build_expression_ast` was the deleted
FCE+OE-dispatch site; the renderer dispatches with `isinstance` on IR node classes, **not**
raw-syside `is_instance()`, so the scanner correctly sees no new site. Plan reports both counts
verified red-before / green-after deletion (non-vacuous). (Direct re-run: Probe P1.)

### Byte-identity chain

- **Corpus (static, strong).** `git diff 7dcae90^..2b00261 -- tests/fixtures/` returns **only
  three additions** (`calc_compat_parity_golden.json`, `calc_def_compilation_golden.json`,
  `computed_attribute_golden.json`). No existing snapshot, baseline, or model fixture changed a
  byte. The per-phase timestamp-churn reverts (`memory: byte-identity-captured-at-churn`) left
  a clean tree — exactly the intended end state.
- **Golden provenance (partial).** Phases 1/2/4 captured goldens via **one-off scripts that were
  not committed** (plan: "a one-off capture run before touching the seam"). So the capture code
  the brief asked me to read does not exist in the repo — provenance cannot be re-read directly.
  It rests instead on the Phase-0→3 **live** old-vs-new parity/golden tests, which compared the
  genuine old functions against the new path with both present and passed under license (the
  skip arithmetic above shows they ran). Probe P4 re-establishes provenance independently by
  checking out the Phase-0 commit (both paths present) and re-running the live parity.

### Code integrity

- **Minor (latent, non-blocking): unary-operator assumption.** `_render_operator` treats *any*
  single-operand `OperatorNode` as unary minus — `return f"(-{operand})"`
  (`calc_compat_renderer.py:129–131`) — without checking `node.operator == "-"`. A single-operand
  `+` would render as `(-x)`. Harmless under the corpus byte-identity gate (no such node in the
  corpus, and it matched the old path over every corpus expression), but it's an undefensive
  spot worth a guard if the renderer ever sees non-corpus input. Not a certification blocker for
  a representation migration gated on the existing corpus.
- No god-functions, no policy-in-utility, no broad `except`, no back-compat shim. The
  `if ir is None: raise CompilationError` guards (`:300`, computed-attr `:300`) are invariant
  guards on an already-non-None input, added for mypy — honest, not silent fallbacks.

---

## Certification

**Checked (static):** all five phases present and matching their notes; symbol deletion
inventory; grep gate + independent whole-family grep in src and tests (no live banned ref
survives); INV-1/INV-3/INV-4 conformance; M2/M3 seam correctness; REQ-AST-04 invariant is
dynamic (has teeth); the +19 skip accounting and the license-present consistency check; both
unplanned fixes structural + regression-tested; corpus byte-identity via git across the item;
N5 int/float distinction frozen correctly in the golden.

**Not checked (execution blocked in this sandbox — pytest/mypy/ruff are approval-denied here):**
- The full suite actually running green at 2317/23 (I verified the *composition* of the skips
  statically, not the live run).
- `mypy src/` actually at 76 with no new error, and `ruff check src/` clean.
- The `@requires_license` goldens actually passing live (only their necessary presence and the
  skip-count consistency are static evidence).
- Live `capture_pipeline_baselines` / `test_factory_purity` / `--from-snapshot` byte-identity
  (git shows the committed corpus is unchanged, but I did not regenerate).
- Golden capture-script provenance (scripts not committed; see Probe P4).

### Requested Live Probes (run with the license env; converts this to unconditional Certify)

Env prefix: `env $(grep -v '^#' ~/1cfe/agentic-mbse/.env | xargs) uv run pytest ...`

- **P1 — full suite + invariant, license-present.**
  `env $(...) uv run pytest -q -rs` → confirm **2317 passed / 23 skipped**, and that every skip
  reason is one of the three content-gated messages above (no `no live syside license` skip on a
  golden/parity case). Include `tests/conformance/test_ast_dispatch_invariant.py` — REQ-AST-04
  both counts green at 3 and 5.
- **P2 — types + lint.** `uv run mypy src/` → **76** (baseline, no new error);
  `uv run ruff check src/` → clean.
- **P3 — package/snapshot byte-identity.** `uv run pytest tests/conformance/test_factory_purity.py
  tests/conformance/test_snapshot_generation.py`; then re-run `scripts/capture_extraction_snapshots.py`
  + `capture_pipeline_baselines.py` under the license, run the timestamp-only churn revert, and
  confirm the only diff is `captured_at` (i.e., zero real diff).
- **P4 — golden provenance (independent).** `git checkout 9a02f24` (Phase 0, both paths present),
  run `env $(...) uv run pytest tests/conformance/test_calc_compat_parity.py` in its pre-D4
  old-vs-new live form → green proves the frozen golden equals genuine old-path output, closing
  the un-committed-capture-script gap.

**Note 1 (SC6 wording):** "mypy `src/` clean" is not literally true — the project carries a
76-error mypy baseline unrelated to this item; the item adds zero. Read SC6 as "no new
mypy/ruff regression," which the static evidence supports and P2 confirms.

---

**Verdict rationale:** Substantively the item is complete and correct by every static measure,
with unusually strong byte-identity evidence (git-clean corpus) and a clean internal-consistency
proof that the license-gated gates actually ran. It is **Certify-with-notes** rather than
unconditional Certify solely because this session cannot execute the test/type/lint gates
itself; P1–P4 are the exact, low-effort confirmations. No finding requires code change to
certify (the unary-minus note is a latent hardening, not a defect against the corpus).

ARTIFACT: .project/active/expression-ast-cutover/audit.md

---

## Addendum: P1–P4 executed by orchestrator (2026-07-13)

- **P1:** full suite **2317 passed / 23 skipped**; zero `no live syside license` skips (grep count 0) — every skip content-gated as accounted. REQ-AST-04 green at the updated counts.
- **P2:** mypy **76 = baseline**; ruff clean.
- **P3:** dispatch invariant + factory purity + snapshot generation → 42 passed / 1 pre-existing skip.
- **P4:** at commit `9a02f24` (old and new paths both live), `test_calc_compat_parity.py` → **28 passed** — the frozen golden equals genuine old-path output, closing the capture-provenance gap independently.

**Final verdict: Certify** (upgraded; all probes executed).
