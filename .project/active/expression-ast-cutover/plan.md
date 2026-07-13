# Implementation Plan: Calc-Seam Cutover — Retire ExpressionAST

**Status:** Draft
**Created:** 2026-07-13
**Last Updated:** 2026-07-13
**Branch:** constraint-exec-epic

## Source Documents
- **Spec:** `.project/active/expression-ast-cutover/spec.md`
- **Design:** `.project/active/expression-ast-cutover/design.md` ← component details, bets, invariants, staging. This plan does not restate them; it sequences and gates them.
- **Design review:** `.project/active/expression-ast-cutover/design-review.md` (M1–M3, N1–N5 — all folded into design rev 2).

## Sequencing & Baseline (read first)

- **Starts after Item 9's implement finishes.** The orchestrator enforces this; do not begin Phase 0 code until Item 9's implement session has committed and the tree is clean. This session writes **only** this plan — no code — while Item 9 is in flight.
- **Baseline = post-Item-8+9 corpus at current HEAD.** Item 8 Phase 5 (`df5ed97`, Snapshot v3 re-capture) is already committed on this branch, so the corpus is **fixed, not moving** (design R4/N4). The design's `Base commit: 043fdb8` predates this — treat current HEAD after Item 9 as the byte-identity baseline. Do not re-derive against 043fdb8.
- **Commit granularity: one commit per phase** (design "Integration Strategy"). The orchestrator commits; do **not** run `git commit` yourself. Each phase's gate must be green before the orchestrator is told the phase is done.
- **R1 is resolved — no de-risk probe.** agentic-mbse exposes a public `extract_expression_ir` (lazy-exported, landed with a serialization-equality test, commit `3ad890e`). The design's "Open / de-risk first" note on the extractor entry point is **stale**; Phase 0 consumes it directly. B1/B2 (byte-identity with the *landed* extractor) are still proven live by the Phase-0 parity test — that is the real de-risk, and it gates everything downstream.

## Implementation Strategy

**Phasing rationale.** The phases *are* the design's five stages (0–4), because each stage is exactly one commit with its own per-function comparand and byte-identity gate (design `Integration Strategy`). Nothing is gained by re-cutting them:

- **Phase 0 (Stage 0)** lands the renderer + the live parity proof with **no production caller flipped**. This is the first proof point and the whole de-risk: if the landed extractor + renderer can't reproduce `compile_expression` byte-for-byte over the corpus, we find out here, and the fix is a renderer/extractor fix, not a bad cutover.
- **Phase 1 (Stage 1)** flips the seam (`compile_calc_def`) — the higher-value, higher-risk consumer (ref-list ordering, `member_names` composition) — behind the golden captured before the flip.
- **Phase 2 (Stage 2)** flips computed attributes — the simpler consumer (empty `member_names`).
- **Phase 3 (Stage 3)** is verification-only: snapshot-replay byte-identity. No code change.
- **Phase 4 (Stage 4)** deletes the three symbols and migrates the ~240-reference test surface. Last and only hard-to-reverse step; owns the largest mechanical chunk.

**Critical path.** Phase 0 green (landed extractor proves byte-identity) → Phase 1 seam flip → Phase 2 computed-attr flip → Phase 3 replay confirm → Phase 4 delete + test migration + grep gate. Old functions live until Phase 4, so Phases 1–3 roll back by reverting a commit.

**First proof point.** Phase 0's `@requires_license` parity test green over the whole corpus (including N5's integer-literal calc output) — proves B1, B2, B4, and the literal rule before any consumer moves.

**Overall validation.** Every phase runs, in order: (1) the phase's per-function golden/parity comparand (INV-1, the primary gate — a green package diff is necessary but *not* sufficient); (2) corpus byte-identity via `capture_pipeline_baselines` + `test_factory_purity` after the timestamp-churn revert (INV-2); (3) full `uv run pytest`, `mypy src/`, `ruff check src/` clean (SC).

---

## Environment & Commands

**See CLAUDE.md** for install/test/typecheck/lint. Two extra facts this plan needs:

- **License-bearing legs** (live extraction, re-capture, the parity test) need `SYSIDE_LICENSE_KEY`, which lives in agentic-mbse's `.env`. Run them as:
  ```bash
  env $(grep -v '^#' ~/1cfe/agentic-mbse/.env | xargs) uv run pytest -m requires_license tests/...
  ```
  Never a bare `python -c` — the license loads for pytest/scripts but not an ad-hoc `-c` probe (`memory: syside-license-via-scripts-not-dashc`, `syside-license-key-explicit-env-needed`). If a `@requires_license` test *skips* instead of running, the key didn't export — that is a fake green, re-run with the env prefix.
- **Snapshot-replay legs are license-free** (`--from-snapshot`, `test_factory_purity`, `capture_pipeline_baselines`).
- **Timestamp-churn revert** after any re-capture: a full re-capture rewrites every `captured_at` (`memory: byte-identity-captured-at-churn`). Diff, confirm only `captured_at`/timestamp lines changed on already-present fixtures, revert those, and confirm the only real diff is what the phase intended (usually: nothing).

---

## Phase 0 — Land renderer + live parity proof (no behavior change)

### Goal
Add `extraction/calc_compat_renderer.py` and a `@requires_license` parity test that asserts, for every corpus calc output expression, the new path reproduces `compile_expression`'s output byte-for-byte. No production caller flips; baselines untouched. This is the de-risk-first phase (design Stage 0, B1/B2/B4).

### Assumption Under Test
The **landed** `extract_expression_ir` (not the spike's `s2_ir.extract_ir`), fed a calc output expression, produces an `ExpressionIR` that renders byte-identically through the productionized renderer — including the integer-vs-float literal distinction (B4/M2). If false, it's a renderer or extractor gap caught here, before any flip.

### Test Stencil (write this first)
```python
# tests/conformance/test_calc_compat_parity.py  (NEW)
@pytest.mark.requires_license
@pytest.mark.parametrize("fixture", CALC_CORPUS_FIXTURES)  # includes return_styles (N5: out y = a*2)
def test_calc_compat_parity(fixture):
    for calc_def in extract_calc_defs(fixture):
        # N1: name sets MUST be the sets compile_calc_def derives, not probe4-style
        #     owned_elements-by-direction re-derivation.
        input_names = {a.name for a in calc_def.input_attributes}
        output_names = {a.name for a in calc_def.output_attributes}
        member_names = output_names | (calc_def.all_member_names or set())
        for name, node in calc_def.output_expression_nodes():
            old = compile_expression(build_expression_ast(node, input_names, output_names,
                                                          all_member_names=calc_def.all_member_names))
            ir = extract_expression_ir(node)                       # landed agentic-mbse extractor
            new = render_calc_expression(ir, input_names, member_names)
            assert new == old                                     # byte-identity (INV-1)
            # and the ref lists (B3/R3):
            assert collect_calc_refs(ir, input_names, member_names) == _collect_refs(...old ir...)
```

### Changes Required

**See `design.md` for:** renderer surface → `design.md#component-overview`; the exact dialect the renderer must reproduce → `design.md#implementation-notes` ("Renderer must match `compile_expression` exactly"); the classification model → `design.md#architecture` (seam name sets, M3); why a separate module → `design.md` D1.

**Skeleton to copy from:** `generation/predicate_compiler.py:103-128` (`_compile_numeric`) is the near-twin walk over the same IR node algebra (`ExpressionIR, FeatureReferenceNode, LiteralNode, OperatorNode, UnitAnnotationNode` from `agentic_mbse.sysml.expression_ir`). The calc renderer diverges from it in exactly three places (design research table): `str(value)` **not** `repr`; `inputs.{name}`/bare classification **not** bare `source_name`; arithmetic-only top layer (no Kleene).

#### 1. Renderer module
**File:** `src/sysml_codegen/extraction/calc_compat_renderer.py` (NEW)
- [x] `render_calc_expression(ir, input_names, member_names) -> str` — pure IR→Python walk.
  - [x] **Literals (M2):** render keyed on IR literal type — `LiteralInteger` → `str(int(value))`, `LiteralRational` → `str(float(value))`. Reproduces the raw syside value the old path passed through `str()` (`4`→`"4"`, `4.0`→`"4.0"`). B4 confirms the landed extractor preserves the int/float type; this rule is the actual byte-identity failure mode and is gated by N5 in this phase.
  - [x] **Operators/structure:** `PYTHON_OPERATOR_MAP` spacing (`" + "`), `^`→`" ** "`, unary→`(-x)`, n-ary left-fold with parens at every step, unit-strip to the value operand.
  - [x] **Feature refs:** `inputs.{name}` when name ∈ `input_names`; bare `{name}` when name ∈ `member_names`; else raise `CompilationError` (D3 — the kept symbol, so caller `except CompilationError` → `MANUAL_REQUIRED` is unchanged).
  - [x] Call **this module's** `_sanitize_name` (import from `expression_compiler`), not the shared sanitizer — its divergence is load-bearing (`expression_compiler.py:167`).
  - [x] Final `python_ast.parse(result, mode="eval")` validation; raise `CompilationError` on unparseable output (D3).
- [x] `collect_calc_refs(ir, input_names, member_names) -> (input_refs, intermediate_refs)` — walk `FeatureReferenceNode` leaves, classify against the *same* sets, preserve **pre-order first-occurrence dedup** so ref lists stay byte-identical (B3/R3).

#### 2. Parity test
**File:** `tests/conformance/test_calc_compat_parity.py` (NEW — write first)
- [x] Implement the stencil. Iterate the calc corpus **fixture-only** (design "Implementation Notes": committed fixtures subsume probe4's synthetic SCRATCH shapes — `-(a+b)`, `a**b**c`, 7-ary sums, nested parens).
- [x] **N5:** confirm the iterator includes `return_styles`' integer-literal outputs (`out y = a * 2`, `out y = x * 4`) so the literal rule is gated here.
- [x] **N1:** name sets derived exactly as `compile_calc_def` does (`input_attributes`, `output_attributes ∪ all_member_names`), not re-derived by walking `owned_elements`.
- [x] Assert both the expression **string** and the `(input_refs, intermediate_refs)` tuple (INV-1 comparand is the full result, not just the string — R3).

### Validation
**Automated:**
- [x] `env $(grep -v '^#' ~/1cfe/agentic-mbse/.env | xargs) uv run pytest tests/conformance/test_calc_compat_parity.py` → all pass (not skip — see env note).
- [x] `uv run pytest` (full suite), `mypy src/`, `ruff check src/` → clean.
- [x] `test_factory_purity` + `capture_pipeline_baselines` unchanged (no production path flipped, so no baseline movement expected).

**What we know works after this phase:** the landed extractor + renderer reproduce `compile_expression` byte-for-byte (strings + ref lists) over the whole corpus, including int/float literals. B1, B2, B4, M2 proven. No consumer has moved yet.

---

## Phase 1 — Flip the seam (`compile_calc_def`)

### Goal
Swap the per-output `build_expression_ast` + `compile_expression` + `_collect_refs` triple inside `compile_calc_def`'s loop for `extract_expression_ir` + `render_calc_expression` + `collect_calc_refs`. The orchestration (dependency graph, undeclared-intermediate discovery, topological sort) does **not** move (design `Architecture`).

### Assumption Under Test
`compile_calc_def`'s `CalcDefCompilationResult` — strings **and** `input_refs`/`intermediate_refs` ordering **and** `compilability` — is invariant under the swap (B3). The `member_names = output_names ∪ all_member_names` composition (M3) reproduces the serialized `intermediate_refs` exactly.

### Test Stencil (write this first)
```python
# Golden captured BEFORE the flip, asserted after (INV-1 primary gate).
# scripts/ or a committed golden fixture holds the pre-flip CalcDefCompilationResult per calc def.
def test_compile_calc_def_golden():
    for calc_def in CALC_CORPUS:
        result = compile_calc_def(calc_def, ...)        # now on the IR path
        assert result == GOLDEN[calc_def.qualified_name] # full result: strings + ref lists + compilability
```

### Changes Required

**See `design.md` for:** the exact swap site and what stays → `design.md#architecture` (`compile_calc_def` bullet); seam name sets (M3) → `design.md#architecture` ("Seam name sets"); ref-collection dedup → `design.md#architecture` ("Ref collection moves onto the IR").

**Specific changes:**
- [x] **Golden capture (before touching the loop):** capture each corpus calc def's current `CalcDefCompilationResult` into a committed golden. This is the comparand `compile_calc_def` produced *today* (F4 lesson: the exact replaced function's output, not a downstream proxy).
- [x] `src/sysml_codegen/extraction/expression_compiler.py:580-602` — replace the `build_expression_ast` → `compile_expression` → `_collect_refs` triple with `extract_expression_ir(ast_node)` → `render_calc_expression(ir, input_names, member_names)` → `collect_calc_refs(ir, input_names, member_names)`, keeping the `try/except CompilationError` → `MANUAL_REQUIRED` structure exactly.
- [x] **M3 seam sets:** `input_names = {a.name for a in calc_def.input_attributes}`; `member_names = output_names ∪ all_member_names`. Do **not** pass only `all_member_names` trusting it to contain declared outputs — the union is what reproduces serialized `intermediate_refs`.
- [x] Old symbols (`build_expression_ast`, `compile_expression`, `_collect_refs`, `ExpressionAST`) **stay** — deleted in Phase 4. Only the call site moves.

### Validation
**Automated:**
- [x] Golden test green: post-flip `CalcDefCompilationResult` == pre-flip golden (INV-1).
- [x] Phase-0 parity test still green (both paths still exist).
- [x] **Snapshot re-capture gate (license):** `env $(...) uv run python scripts/capture_extraction_snapshots.py` → run timestamp-churn revert → `compilation_results` section byte-identical (INV-2/INV-3).
- [x] **License-free:** `capture_pipeline_baselines` + `test_factory_purity` green; generated packages byte-identical.
- [x] Full `uv run pytest`, `mypy src/`, `ruff check src/` clean.

**What we know works after this phase:** the primary calc seam produces its strings and ref lists through the IR path with zero byte movement in the snapshot's `compilation_results` and in generated packages.

---

## Phase 2 — Flip computed attributes

### Goal
Swap the single `build_expression_ast` + `compile_expression` call at `computed_attribute_extractor.py:300-306` for the same renderer, passing `input_names = siblings − self` (already sanitized at `:296-298`) and an **empty** `member_names` (so any non-input ref errors → `MANUAL_REQUIRED`, matching today's `output_names=set()`, `all_member_names=None` behavior).

### Assumption Under Test
The computed-attr path is the *same* dialect with an empty member set, so `render_calc_expression(ir, input_names, member_names=∅)` reproduces its `compiled_expression` string exactly (design review Probe Finding 2).

### Test Stencil (write this first)
```python
def test_computed_attr_golden():
    for part, attr in COMPUTED_ATTR_CORPUS:
        result = extract_computed_attribute(part, attr, ...)   # now on the IR path
        assert result.compiled_expression == GOLDEN[(part, attr)]  # exact pre-flip string
        assert result.compilability == GOLDEN_COMPILABILITY[(part, attr)]
```

### Changes Required

**See `design.md` for:** the empty-`member_names` rationale → `design.md#architecture` (`computed_attribute_extractor` bullet).

**Specific changes:**
- [x] **Golden capture (before the flip):** capture each computed attribute's current `compiled_expression` + `compilability`.
- [x] `src/sysml_codegen/extraction/computed_attribute_extractor.py:300-306` — replace `build_expression_ast(...)` + `compile_expression(ast_ir)` with `extract_expression_ir(expr)` + `render_calc_expression(ir, input_names, member_names=set())`, keeping the `try/except CompilationError` → `MANUAL_REQUIRED` + `logger.warning` structure at `:308-316` unchanged.
- [x] The `Compilability` import stays (kept symbol); `build_expression_ast`/`compile_expression` imports here go dead but the symbols still exist until Phase 4 (leave the import until Phase 4's sweep, or drop it now if lint flags unused — either is fine as long as the symbols aren't deleted).

### Validation
**Automated:**
- [x] Computed-attr golden green (INV-1).
- [x] Snapshot re-capture + timestamp-churn revert → byte-identical; `capture_pipeline_baselines` + `test_factory_purity` green.
- [x] Full `uv run pytest`, `mypy src/`, `ruff check src/` clean.

**What we know works after this phase:** both production consumers render from `ExpressionIR`. The old functions are now called only by tests and the still-live parity test.

---

## Phase 3 — Snapshot-replay verification (no code change)

### Goal
Confirm `generate --from-snapshot` packages stay byte-identical over the committed snapshots and the serialized `compilation_results` round-trips byte-identically. License-free. No production edit (design Stage 3, review Probe Finding 3: "no new test needed").

### Assumption Under Test
Because `compilation_results` carry compiled *strings* (not the tree) and Phases 1–2 proved those strings are byte-identical, `--from-snapshot` replays identical strings → identical packages. This phase just proves the premise holds end-to-end.

### Test Stencil
```python
# Existing gates — run, don't write new:
#   test_factory_purity (round-trip byte-identity)
#   generate --from-snapshot <committed snapshot> --output /tmp/out  →  diff against baseline package
```

### Changes Required
- [ ] No source change. If any is needed here, a Phase-1/2 gate was wrong — stop and fix upstream.
- [ ] `test_factory_purity` green over committed snapshots.
- [ ] `generate --from-snapshot` over each committed snapshot → package byte-identical to baseline (timestamps excepted).
- [ ] Re-capture snapshots **only** if the capture *shape* changed (it must not) — and only as a reviewed diff. Expectation: no re-capture.

### Validation
**Automated:**
- [ ] `uv run pytest tests/conformance/test_factory_purity.py tests/conformance/test_snapshot_generation.py` → green.
- [ ] `--from-snapshot` package diff empty (timestamp-churn reverted).

**What we know works after this phase:** the whole snapshot→package replay path is byte-identical on the IR producer. Safe to delete the old path.

---

## Phase 4 — Retire test surface + delete + grep gate

### Goal
Delete the three symbols (plus `ExpressionNodeType`, `PYTHON_OPERATOR_MAP`, `_collect_refs`), migrate the ~240-reference test surface, and lock the door with a grep gate (INV-4). This phase is **not** "delete symbols + grep gate" — it owns the largest mechanical chunk (M1). Last and only hard-to-reverse step; rollback = revert this commit (Phases 1–2 still green on it).

### Assumption Under Test
The renderer has inherited equivalent unit coverage, so retiring the old-tree tests loses no real coverage; and no `src/` **or test** reference to the three symbols survives (INV-4, "full suite green at each stage").

### Test Stencil (the grep gate — write first)
```python
# tests/conformance/test_no_expression_ast.py  (NEW)
def test_expression_ast_symbols_deleted():
    banned = ("ExpressionAST", "build_expression_ast", "compile_expression")
    hits = grep_symbols("src/sysml_codegen", banned)
    assert hits == [], f"ExpressionAST not fully retired: {hits}"   # INV-4, scoped to src/
```

### Changes Required — ordered (design Stage 4 order is authoritative)

**See `design.md#component-overview`** for the full deletion list and the test-surface categorization (re-anchor vs retire).

- [ ] **(1) Convert parity test to a committed golden (D4).** `test_calc_compat_parity.py` compares live `compile_expression` vs the renderer — it cannot survive deleting `compile_expression`. Its last act: freeze the old strings (+ ref lists) into a committed golden file, then assert the renderer against that golden forever. Capture the golden **before** deleting anything.
- [ ] **(2) Re-anchor the renderer's inherited dialect tests** onto `render_calc_expression` (fed IR):
  - [ ] `tests/unit/test_expression_compiler.py` — the ~237 dialect cases ("expression → expected Python string": `inputs.x`, `^`→`**`, unit-strip, n-ary fold, int/float literals, unresolved-ref → `CompilationError`) become `render_calc_expression` tests fed IR.
  - [ ] `tests/conformance/test_expression_compiler.py` — the corpus/conformance dialect cases, same re-anchor.
- [ ] **(3) Retire the old-tree-shape tests** (subject deleted):
  - [ ] The `ExpressionAST`-construction / `ExpressionNodeType` cases in `tests/unit/test_expression_compiler.py`.
  - [ ] The `ExpressionNodeType` data-model inventory rows in `tests/conformance/test_data_models.py:223-225,692`.
  - [ ] The two `build_expression_ast`-FCE-dispatch unit tests in `tests/conformance/test_ast_dispatch_invariant.py:399-426` (raw-node dispatch now lives in agentic-mbse's extractor).
- [ ] **(4) Update REQ-AST-04's two counts** (`tests/conformance/test_ast_dispatch_invariant.py`):
  - [ ] `test_total_dispatch_function_count`: `assert len(multi_type) == 6` → `== 5` (line ~326) + docstring "Exactly 6" → "Exactly 5" (line ~295). Multi-type audited functions **6 → 5**.
  - [ ] `test_total_dual_check_site_count`: `assert len(dual_check) == 4` → `== 3` (line ~289) + docstring "Exactly 4" → "Exactly 3" (line ~268). FCE+OE-ordered sites **4 → 3**.
  - [ ] Add a comment on both: the raw-node FCE-before-OE dispatch responsibility for calc expressions moved cross-repo to the reused `extract_expression_ir` extractor (out of this repo's invariant scope). The renderer consumes `ExpressionIR` (isinstance on IR node classes), **not** raw-syside `is_instance()`, so it adds **no** dispatch site — do **not** add the renderer to the audited set.
- [ ] **(5) Scrub comment-only mentions:**
  - [ ] `tests/integration/test_hierarchy_e2e.py:418` and `tests/helpers/impl_execution.py:3` — stale symbol name in a docstring only.
  - [ ] `src/sysml_codegen/extraction/hierarchy_resolver.py:54` — stale `PYTHON_OPERATOR_MAP` comment (N3; survives the grep gate's 3-symbol scope but scrub it when the symbol goes).
  - [ ] `tests/unit/test_computed_attribute_extraction.py` — keep its `Compilability` import (kept symbol); its compiled-string assertions were re-anchored in Phase 2.
- [ ] **(6) Confirm no `src/` or test reference to the three symbols remains** (grep both trees before deleting).
- [ ] **(7) Delete** from `expression_compiler.py`: `ExpressionAST`, `ExpressionNodeType`, `PYTHON_OPERATOR_MAP`, `build_expression_ast`, `compile_expression`, `_collect_refs`. Keep `Compilability`, `CompilationResult`, `CalcDefCompilationResult`, `classify_compilability`, `compile_calc_def`, `_topological_sort`, `_sanitize_name`, `CompilationError`.
- [ ] **(8) Add the grep gate** (`test_no_expression_ast.py`, INV-4).

### Validation
**Automated:**
- [ ] Grep gate green: three symbols absent from `src/` (INV-4).
- [ ] Manual grep of `tests/` for the three symbols → only the golden fixture's captured strings remain (no live import/call).
- [ ] Golden-file parity test green (renderer vs frozen goldens).
- [ ] REQ-AST-04 both counts green at 5 and 3.
- [ ] Full `uv run pytest` green (this is the phase the spec's "full suite green" hinges on — M1), `mypy src/`, `ruff check src/` clean.
- [ ] Snapshot/package byte-identity unchanged (deletion is producer-internal; no string moves).

**What we know works after this phase:** `ExpressionAST` and its two compile functions are gone, the renderer owns the dialect contract with permanent golden coverage, the dispatch-invariant guardrail is re-derived, and no silent replacement remains.

---

## Risk Management

**See `design.md#potential-risks`** for R1–R4. Phase-specific posture:

- **R1 (extractor entry point) — RESOLVED.** `extract_expression_ir` is public (commit `3ad890e`). No probe; Phase 0 consumes it. The design's "de-risk first / open" note on this is stale.
- **R2 (landed ≠ spike extractor), B1/B2 — Phase 0.** Proven live by the parity test before any flip; a divergence is a renderer fix, not a cutover failure. The int/float literal sub-case (B4/M2) is settled by evidence (`production_facts.json`) and additionally gated by N5 in Phase 0.
- **R3 (ref-list ordering drift) — Phases 0–1.** Comparand is the full `CalcDefCompilationResult` (strings **and** ref lists), never just the string. Pre-order first-occurrence dedup in `collect_calc_refs`.
- **R4 (Item 8 coupling) — de-risked.** Post-Item-8 corpus is fixed at HEAD. Still run the timestamp-churn revert on every re-capture.
- **N2 (error branch is dead for the corpus).** Byte-identity does **not** hinge on renderer error-string parity — the only serialized `unsupported_reason` is the orchestration-level `"no expression AST"` (from `compile_calc_def:573`, untouched). The renderer's `CompilationError` route is safe but effectively unexercised by the gate. Do not over-invest in matching old error text.

## Implementation Notes

[TO BE FILLED DURING IMPLEMENTATION — leave empty now]

### Phase 0 Completion
**Completed:** 2026-07-13
**Actual changes:**
- Added `src/sysml_codegen/extraction/calc_compat_renderer.py` (`render_calc_expression`,
  `collect_calc_refs`) — self-contained, own operator-map copy, imports only the kept
  `CompilationError`/`_sanitize_name` from `expression_compiler` (both survive Stage 4).
- Added `tests/conformance/test_calc_compat_parity.py`, `@requires_license`, parametrized
  over the union of `capture_extraction_snapshots.py`'s `MODELS` + `EXTRACTION_ONLY_MODELS`
  (29 fixtures, reused rather than re-listed so the corpus can't drift from the capture
  script's). For every calc def with `output_expression_asts`, compiles each output through
  both the old (`build_expression_ast`→`compile_expression`/`_collect_refs`) and new
  (`extract_expression_ir`→`render_calc_expression`/`collect_calc_refs`) paths and asserts
  byte-identical strings and ref-list tuples. Name sets derived exactly as `compile_calc_def`
  derives them (N1).
- Result: 28 fixtures with calc output expressions all byte-identical (strings + refs);
  `agg_literal_probe` has none, skips cleanly. `return_styles`' two integer-literal outputs
  (N5) passed — B1/B2/B4/M2 confirmed live with the landed extractor, not just by evidence.
**Deviations:** None from the plan's stencil. `_ARITHMETIC_OPERATOR_MAP` is a private copy
of `PYTHON_OPERATOR_MAP`'s arithmetic subset rather than an import — `PYTHON_OPERATOR_MAP` is
one of the Stage-4 deletions, so importing it would have made the renderer's survival
dependent on a symbol scheduled to disappear.
**Validation:** parity test 28 passed/1 skipped (license env); full suite 2310 passed/5
skipped (license env, no license-gated test skipped); mypy 76 errors (baseline, unchanged);
ruff clean.

### Phase 1 Completion
**Completed:** 2026-07-13
**Actual changes:**
- Captured `tests/fixtures/golden/calc_def_compilation_golden.json` (pre-flip, live, 104 calc
  defs across 28 fixtures) via a one-off capture run before touching the seam.
- Added `tests/conformance/test_compile_calc_def_golden.py` (`@requires_license`), asserting
  post-flip `compile_calc_def` output equals the golden field-for-field per fixture.
- `expression_compiler.py`: `compile_calc_def`'s per-output triple now calls
  `extract_expression_ir` → `render_calc_expression`/`collect_calc_refs` (imported locally
  inside `compile_calc_def`, not at module level — `calc_compat_renderer` imports
  `CompilationError`/`_sanitize_name` back from this module, so a top-level import would be
  circular). M3 seam set: `member_names = output_names | (all_member_names or set())`.
  `build_expression_ast`/`compile_expression`/`_collect_refs`/`ExpressionAST` untouched, still
  present, still used by their own unit tests.
- Renderer fix found by this flip (not by Phase 0, which only exercised real syside data):
  `_render_literal` keyed on `operand_type.category`, which is `"unresolved"` whenever
  `cached_result_type` isn't available (real syside calc literals always resolve it, but a
  hand-built mock node in the existing unit-test surface doesn't). Re-keyed on
  `literal.kind` (the syside class name) instead, using the exact substring-fallback
  convention `SysideAdapter.is_instance` already uses for mocks
  (`"LiteralInteger" in kind`) — matches real data exactly (`kind` is already
  `"LiteralInteger"`/`"LiteralRational"` there) and fixes the mock case without touching
  category/resolution at all.
- Two pre-existing `tests/unit/test_expression_compiler.py` `TestCompileCalcDef` mock-based
  tests broke on the flip and needed narrow fixes (not deferred to Phase 4, since Phase 4
  only owns the *build_expression_ast-level* dialect/dispatch test migration — these are
  *compile_calc_def*-level orchestration tests, which now exercise the new seam directly):
  `test_edge5_feature_chain_returns_manual`'s `MockFeatureChainExpression()` was an empty
  class with no operands, so agentic-mbse's chain-segment extraction found nothing and the
  renderer's `chain_segments`-based rejection (mirroring `predicate_compiler.py`'s identical
  check) never fired; gave it one operand so it behaves like a real FCE node. mypy also
  flagged `extract_expression_ir`'s `ExpressionIR | None` return type at the two new call
  sites; added an explicit `if ir is None: raise CompilationError(...)` guard (ast_node was
  already checked non-None, so this is an invariant guard, not new production behavior).
**Deviations:** None from the plan's staging/comparand. The renderer literal-keying change is
an amendment to Phase 0's `calc_compat_renderer.py`, not a Phase 1 file, but landed in this
commit since Phase 1's flip is what exposed the gap (Phase 0's corpus has no unresolved-type
literals to catch it).
**Validation:** golden test 28 passed/1 skipped; parity test still 28 passed/1 skipped; full
suite 2338 passed/6 skipped (license env); mypy 76 (baseline, unchanged); ruff clean;
extraction-snapshot re-capture — 29 `captured_at`-only diffs, reverted, `compilation_results`
byte-identical; `capture_pipeline_baselines` — zero diff; `test_factory_purity` +
`test_baselines` 26 passed/1 skipped.

### Phase 2 Completion
**Completed:** 2026-07-13
**Actual changes:**
- Captured `tests/fixtures/golden/computed_attribute_golden.json` (pre-flip, live, 87
  computed attrs across 12 fixtures).
- Added `tests/conformance/test_computed_attribute_golden.py` (`@requires_license`),
  per-fixture comparison of `classification`/`compilability`/`compiled_expression` against
  the golden.
- `computed_attribute_extractor.py`'s FORMULA branch (`:300-306`) now calls
  `extract_expression_ir` + `render_calc_expression(ir, input_names, member_names=set())` —
  the empty `member_names` reproduces today's `output_names=set()`/`all_member_names=None`
  behavior (any non-input ref -> `CompilationError` -> `MANUAL_REQUIRED`, unchanged
  `try/except`+`logger.warning` structure). No circular-import issue here (this module
  doesn't import back from `calc_compat_renderer`, unlike `expression_compiler.py`), so the
  import is at module level. `build_expression_ast`/`compile_expression` imports dropped
  (only this one call site used them here); the symbols themselves stay in
  `expression_compiler.py` until Phase 4.
**Deviations:** None.
**Validation:** computed-attribute golden 12 passed/17 skipped (fixtures with no computed
attrs); Phase 0/1 goldens+parity still green; full suite 2350 passed/23 skipped (license
env, all skips accounted for — no computed attrs / no baseline / no matching scenario, none
license-related); mypy 76 (baseline, unchanged); ruff clean; extraction-snapshot re-capture —
`captured_at`-only diffs, reverted; `capture_pipeline_baselines` — zero diff;
`test_factory_purity` + `test_baselines` 26 passed/1 skipped.

### Phase 3 Completion
### Phase 4 Completion

---

**Status:** Draft → In Progress → Complete
