# Design: Calc-Seam Cutover — Retire ExpressionAST

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-13
**Branch:** constraint-exec-epic
**Base commit:** 043fdb8

---

## Overview

Move the three calc-side consumers of `ExpressionAST` onto the neutral `ExpressionIR` tree
plus a productionized compat renderer, one byte-identity-gated step at a time, then delete
`ExpressionAST` and its two compile functions. No expression semantics change — this is a
representation migration under a per-function byte-identity gate.

## Related Artifacts

- **Spec:** `.project/active/expression-ast-cutover/spec.md` (Option A; three real consumers)
- **Epic:** `.project/backlog/epic_constraint_execution.md` (Item 13)
- **S2 spike:** `.project/active/spike-expression-tree-parity/` — `findings.md`,
  `probe4_calc_compat.py` (byte-identical calc render over the corpus), `s2_ir.py`
  (provisional extractor+renderer, the reference shape)
- **Item 7 precedent:** `src/sysml_codegen/generation/predicate_compiler.py` — the landed
  IR→Python compiler, same node algebra this design renders
- **Memory:** `f4-cutover-fallback-divergence` (comparand = the exact replaced function),
  `byte-identity-captured-at-churn` (timestamp-only churn check),
  `syside-license-key-explicit-env-needed`, `syside-license-via-scripts-not-dashc`

## Research Findings

**The two calc consumers both funnel through one pair of functions.** Both
`compile_calc_def` (`extraction/expression_compiler.py:458`, called at
`orchestration/pipeline_builder.py:931`, "Step 6.5") and
`computed_attribute_extractor.py:300-306` call `build_expression_ast` then
`compile_expression`. Migrating that pair migrates both consumers.

**The third "consumer" is a verification point, not a code change.** The snapshot carries
`CalcDefCompilationResult` / `CompilationResult` — Python strings plus ref lists
(`snapshot/serializer.py:112`, `snapshot/loader.py:278-315`). Those dataclasses live in
`expression_compiler.py` and **stay**; only `ExpressionAST`, `build_expression_ast`,
`compile_expression` are deleted. Once the producer emits byte-identical strings, the
serialized section and every downstream consumer see the same bytes. So this consumer needs a
gate, not an edit.

**`compile_expression` and `predicate_compiler._compile_numeric` are near-twins over the same
IR, but not mergeable.** Both left-fold n-ary arithmetic with parens at every step, map
`^`→`**`, and strip units. They diverge exactly where it matters:

| | calc (`compile_expression`) | predicate (`_compile_numeric`) |
|---|---|---|
| feature ref | `inputs.{name}` if input, bare if intermediate, else error | bare `source_name` |
| literal | `str(value)` | `repr(value)` |
| top layer | arithmetic only | Kleene 3-valued boolean + margin |

`str` vs `repr` and `inputs.` vs bare are load-bearing for byte-identity; a shared dual-mode
function would be a `if calc_mode:` fork through every branch. They also sit in different
layers (`extraction/` vs `generation/`, different pipeline stages). Two thin renderers over
**one** tree is what the concept endorses; a shared renderer is not.

**Reference classification moves from build time to render time.** Today
`build_expression_ast` bakes INPUT_REF vs INTERMEDIATE_REF into the tree from the name sets
(`expression_compiler.py:385-396`). `ExpressionIR`'s `FeatureReferenceNode` carries only
`source_name` (unclassified — the concept requires this). So classification happens in the
renderer from the supplied name sets, exactly as `probe4.compat_render` did.

**License:** live extraction needs `SYSIDE_LICENSE_KEY`, which sits unexported in repo `.env`
(`memory: syside-license-key-explicit-env-needed`). Parity/re-capture run via a committed
`@requires_license` test or a capture script, never a bare `python -c`
(`memory: syside-license-via-scripts-not-dashc`). Snapshot-replay gates are license-free.

## Core Concept

`ExpressionIR` is already the one neutral, serializable semantic tree; predicates render from
it (Item 7). The calc side is the last holdout on its own private tree. This item makes the
calc side render from `ExpressionIR` too, through a **calc-compat renderer** — the
productionized form of S2's `probe4.compat_render`: a pure `IR → Python-string` walk that
classifies each feature reference as `inputs.x` or bare `x` at render time from the caller's
name sets, and reproduces today's `compile_expression` dialect byte-for-byte (n-ary left-fold,
`^`→`**`, unit-strip, `str()` literals, and the `python_ast.parse` validation).

The migration swaps `build_expression_ast` + `compile_expression` for `extract IR` + `render`
inside each consumer, one at a time. Each swap is gated by comparing the **exact string the
replaced function produced**, captured before the flip, over the whole corpus (the F4 rule).
When the last production caller is off the old path, delete the three symbols and lock the door
with a grep gate. The whole game is byte-identity; every stage proves it before advancing.

The extractor is reused, not rebuilt: `ExpressionIR` is agentic-mbse-owned and there is already
a landed syside→IR extractor feeding the predicate path. Re-deriving one codegen-side would
reintroduce a second extraction path — a smaller version of the exact drift this epic exists to
remove.

## Key Bets

- **B1. The landed agentic-mbse extractor, fed a calc output expression, produces an
  `ExpressionIR` that renders byte-identically through the productionized renderer.** The S2
  proof used the *spike's* `s2_ir.extract_ir`, not the landed extractor — so byte-identity must
  be *re-proven* with the real extractor, not inherited. *If false → the renderer or the
  extractor has a gap; caught by the Stage-0 parity test before any consumer flips, so it costs
  a fix, not a bad cutover.*
- **B2. Calc output expressions and constraint predicates are the same syside node kinds**
  (OperatorExpression, FeatureReferenceExpression, LiteralRational/Integer, unit `[`) — so the
  predicate extractor already covers every construct the calc corpus contains. *If false → a
  calc-only node kind (e.g. a construct `build_expression_ast` marked UNSUPPORTED) extracts to
  an `UnsupportedNode` the renderer must reject the same way; caught by the parity test as a
  diverging error path.*
- **B3. `CompilationResult` shape is invariant under this migration** — same
  `python_expression`, same `input_refs`/`intermediate_refs` ordering, same `compilability`.
  *If false → the serialized snapshot section churns and downstream graphs shift; caught by the
  snapshot round-trip + `test_factory_purity` gates.*

## Key Decisions

- **D1. One new calc-compat renderer module in `extraction/`, sibling-in-role to
  `generation/predicate_compiler.py` — not a shared dual-mode module.**
  New file `extraction/calc_compat_renderer.py` exports the render and ref-collect functions
  over `ExpressionIR`. *Rejected: one `ir_python.py` with calc+predicate modes — the `str`/`repr`
  and `inputs.`/bare divergences make it a fork-through-every-branch, it would force a cross-layer
  import (renderer used at extraction Step 6.5, predicates at generation), and it fuses Kleene
  semantics with plain arithmetic behind a mode flag.* *Rejected: inline the renderer into
  `expression_compiler.py` — that module's identity ("build the ExpressionAST tree") is exactly
  what retires; a separate module gives the deletion a clean boundary and a stable home for the
  parity test.*

- **D2. Reuse the landed agentic-mbse syside→`ExpressionIR` extractor; confirm its single-node
  entry point as plan task 0.** The predicate path already extracts IR via
  `agentic_mbse.sysml.constraint_extraction`. *Rejected: a codegen-side extractor (the spike's
  `s2_ir.extract_ir` shape) — it works and keeps the change in-repo, but it is a second
  syside→IR path that can drift from the predicate path, the precise smell this epic removes.*
  **Open, de-risk first:** whether agentic-mbse exposes a public `syside_node → ExpressionIR`
  for a single expression, or only whole-facts extraction. If only the latter, exposing a thin
  wrapper is a small agentic-mbse (cross-repo) touch — **surfaced here, not resolved silently**:
  the spec scoped this item to sysml-codegen, so a required agentic-mbse change is a scope note
  the plan must carry. (See Potential Risks.)

- **D3. The renderer reproduces `compile_expression`'s validation and error path, not just its
  happy-path string.** It runs `python_ast.parse(mode="eval")` on its output and raises
  `CompilationError` (the existing symbol, kept) on an unresolved reference or unparseable
  result — so callers' existing `except CompilationError` → `MANUAL_REQUIRED` fallback behaves
  identically. *Rejected: a fresh exception type — would silently change which except-clauses
  catch, a behavior change hiding inside a "representation-only" migration.*

- **D4. At deletion, convert the live old-vs-new parity test into a committed golden.** The
  Stage-0 parity test compares `compile_expression(...)` against the renderer live; it cannot
  survive deleting `compile_expression`. Its last act before deletion is to freeze the old
  strings into a committed golden file, which the renderer is then asserted against forever.
  *Rejected: just delete the parity test at cutover — loses the permanent byte-identity guard
  the spec wants kept.*

## Architecture

Producer side only changes; everything downstream of the compiled string is untouched.

```
            live syside nodes (calc output expressions)
                         │
   OLD:  build_expression_ast ─► ExpressionAST ─► compile_expression ─► "python str"
                         │
   NEW:  extract_ir (agentic-mbse) ─► ExpressionIR ─► calc_compat_renderer ─► "python str"
                         │
              CompilationResult (str + input_refs + intermediate_refs + compilability)
                         │
            ┌────────────┴─────────────┐
     snapshot compilation_results   ComputationGraph ─► generated package
        (strings, unchanged)          (unchanged if strings + refs match)
```

- **`compile_calc_def`** keeps its whole orchestration — dependency graph, undeclared-
  intermediate discovery, topological sort (`expression_compiler.py:486-533`). Only the
  per-output `build_expression_ast`+`compile_expression`+`_collect_refs` triple inside the loop
  (`:580-602`) swaps to `extract_ir`+`render`+IR-ref-collect. The orchestration does not move.
- **`computed_attribute_extractor`** swaps its one `build_expression_ast`+`compile_expression`
  call (`:300-306`) for the same renderer, passing `input_names = siblings − self`, empty
  member set (so any non-input ref errors → `MANUAL_REQUIRED`, as today via UNSUPPORTED).
- **Ref collection moves onto the IR.** `_collect_refs` walks ExpressionAST INPUT_REF/
  INTERMEDIATE_REF nodes; the replacement walks `FeatureReferenceNode` leaves and classifies
  against the same name sets, preserving pre-order first-occurrence dedup so
  `input_refs`/`intermediate_refs` stay byte-identical (B3).

## Required Invariants

- **INV-1 (per-function comparand).** Each stage's gate compares the output of the *exact
  function it replaces*, captured before the flip, over the whole corpus — never a downstream
  proxy. A green package diff is necessary but not sufficient.
- **INV-2 (byte-identity per stage).** After each staged commit, generated packages, pipeline
  baselines, and the snapshot `compilation_results` section are byte-identical to the
  post-Item-8 baseline, timestamps excepted (run the timestamp-only churn revert).
- **INV-3 (shape frozen).** `CompilationResult` / `CalcDefCompilationResult` fields and the
  serialized snapshot layout do not change.
- **INV-4 (no silent replacement).** After deletion, `ExpressionAST`, `build_expression_ast`,
  `compile_expression` appear nowhere in `sysml-codegen/src`.

## Component Overview

- **`extraction/calc_compat_renderer.py`** (new) — `render_calc_expression(ir, input_names,
  member_names) -> str` and `collect_calc_refs(ir, input_names, member_names) ->
  (input_refs, intermediate_refs)`. Pure IR→Python; raises `CompilationError` on unresolved
  refs / unparseable output. The productionized `probe4.compat_render`.
- **`extraction/expression_compiler.py`** (shrinks) — keeps `Compilability`,
  `CompilationResult`, `CalcDefCompilationResult`, `classify_compilability`, `compile_calc_def`,
  `_topological_sort`, `_sanitize_name`. Loses `ExpressionAST`, `ExpressionNodeType`,
  `PYTHON_OPERATOR_MAP`, `build_expression_ast`, `compile_expression`, `_collect_refs`.
- **`extraction/computed_attribute_extractor.py`** (one call site) — flips to the renderer.
- **`tests/.../test_calc_compat_parity.py`** (new) — the S2 proof, productionized: old-vs-new
  over the corpus while both paths exist; converts to a golden-file test at deletion (D4).
- **Grep gate** — a test (or CI check) asserting INV-4 over `src/`.

## Non-Goals

Unchanged from spec: no new expression capability; predicate compilation untouched;
aggregation-walking (`shared_aggregation`, agentic-mbse-owned) is out of scope and its
convergence onto `ExpressionIR` is a named future coordinated-pair item.

## Implementation Notes

- **Corpus = the `tests/fixtures/*` models that carry calc output expressions**, the same set
  probe4/probe5 and the pipeline baselines already cover (`scripts/capture_pipeline_baselines.py`,
  `test_factory_purity`). The parity test iterates them the way probe4 does.
- **Renderer must match `compile_expression` exactly:** `str(value)` literals (not `repr`),
  `PYTHON_OPERATOR_MAP` spacing (`" + "`, `^`→`" ** "`), unary as `(-x)`, unit-strip to the
  value operand, `inputs.{name}` for inputs and bare name for intermediates, then
  `python_ast.parse` validation (D3).
- **License incantation for the plan:** export the key from `.env` before the live legs, e.g.
  `set -a; source .env; set +a` then `uv run pytest -m requires_license` / the capture script.
  Snapshot-replay legs need no license.

## Potential Risks

- **R1 — extractor entry point (highest).** If agentic-mbse exposes no single-node
  `syside → ExpressionIR`, D2 needs either a small cross-repo wrapper (scope note) or the
  rejected codegen-side extractor. *Mitigation:* plan task 0 is a license-free `dir()` probe of
  `agentic_mbse.sysml.constraint_extraction` / `expression_ir`; resolve before writing any
  renderer wiring. This is the de-risk-first item.
- **R2 — landed extractor ≠ spike extractor (B1).** The real tree shape may differ from
  `s2_ir`'s (n-ary normalization, unit node shape). *Mitigation:* the Stage-0 parity test proves
  byte-identity with the *landed* extractor before any flip; a divergence is a renderer fix, not
  a cutover failure.
- **R3 — ref-list ordering drift.** IR ref collection must reproduce `_collect_refs` pre-order
  dedup exactly, or the serialized section churns. *Mitigation:* INV-1 comparand is the full
  `CalcDefCompilationResult` (strings **and** ref lists), not just the expression string.
- **R4 — Item 8 concurrency.** Baseline is the post-Item-8 corpus; Item 8 re-captures snapshots
  concurrently. *Mitigation:* orchestrator sequences implement after Item 8 certifies; rebaseline
  against the certified corpus and run the timestamp-churn check.

## Integration Strategy — Staging and Comparands

Each stage is one commit. Old functions live until Stage 4, so any stage rolls back by reverting
its commit. Deletion is last and is the only hard-to-reverse step.

- **Stage 0 — land renderer + parity proof (no behavior change).** Add
  `calc_compat_renderer.py` and the `@requires_license` parity test asserting, for every corpus
  calc output expression, `render_calc_expression(extract_ir(node), in, mem) ==
  compile_expression(build_expression_ast(node, in, out, mem))`. No production caller flips;
  baselines untouched. *Comparand: `compile_expression` output string, live, both paths present.*
- **Stage 1 — flip the seam (`compile_calc_def`).** Swap the per-output triple for
  extract+render+IR-ref-collect. *Comparand: `compile_calc_def`'s `CalcDefCompilationResult`
  (strings + ref lists + compilability), golden-captured before the flip.* *Gate:* re-capture
  extraction snapshots (license) → `compilation_results` section byte-identical after
  timestamp-churn revert; then license-free `capture_pipeline_baselines` + `test_factory_purity`
  green.
- **Stage 2 — flip computed attributes.** Swap the `:300-306` call. *Comparand: the exact
  `compiled_expression` string that path produces today, golden-captured per computed attribute
  before the flip.* *Gate:* same snapshot + package byte-identity.
- **Stage 3 — snapshot-replay verification (no code change).** Confirm `generate --from-snapshot`
  packages stay byte-identical over committed snapshots (license-free) and the serialized
  `compilation_results` round-trips byte-identically. Re-capture only if the capture *shape*
  changed (it must not), as a reviewed diff.
- **Stage 4 — delete + grep gate.** Convert the parity test to a committed golden (D4); delete
  `ExpressionAST`, `ExpressionNodeType`, `PYTHON_OPERATOR_MAP`, `build_expression_ast`,
  `compile_expression`, `_collect_refs`; add the grep gate (INV-4). *Order:* convert test →
  confirm no `src/` reference remains → delete symbols → add grep gate. *Rollback:* revert this
  commit to restore the old path (Stages 1–2 still green on it).

## Validation Approach

- **Per-function golden (primary).** Stages 1–2 capture the replaced function's output over the
  corpus into a golden before the flip and assert equality after (INV-1). This is the gate that
  the F4 lesson makes primary; the package diff is the secondary confirmation.
- **Corpus byte-identity (secondary).** `capture_pipeline_baselines` + `test_factory_purity`
  (license-free) after every stage; `--from-snapshot` package diff at Stage 3.
- **Live parity (Stage 0, kept to Stage 4).** The productionized probe4/probe5, `@requires_license`.
- **Suite + types + lint.** Full `uv run pytest`, `mypy src/`, `ruff check src/` clean at each
  stage (SC).

## Next-Stage Handoff

- **Fixed:** the four-stage order and per-stage comparands (INV-1); one renderer module in
  `extraction/` (D1); reuse-not-rebuild the extractor (D2); shape frozen (INV-3); grep-gate
  scope (INV-4); deletion last.
- **Open:** the extractor's public single-node entry point (R1) — **resolve first**, license-free.
- **De-risk first:** R1, then B1 via the Stage-0 parity test. Do not wire any consumer until the
  Stage-0 test is green with the landed extractor.

---
Next Step: after approval → `/_my_plan`.
