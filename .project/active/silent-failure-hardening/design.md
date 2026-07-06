# Design: Silent-Failure Hardening — Loud Extraction & Resolution

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-06
**Branch:** pipeline-truth-epic
**Commit:** 3314264
**Epic:** PIPELINE-TRUTH · Item 5
**Complexity:** HIGH

## Overview

Make the model shapes the pipeline cannot handle produce a diagnostic at the root, per
family, without adding noise to clean models. Four families, one choke point each, plus the
sanitizer and the non-float entry-point holes.

## Related Artifacts

- **Spec:** `.project/active/silent-failure-hardening/spec.md` (verification table, four
  families, LOUD-REJECT ruling, closed-by-construction criterion, coordination fences).
- **Spec review:** `.project/active/silent-failure-hardening/spec-review.md` (Resolutions).
- **Probes:** `.project/active/silent-failure-hardening/probes/` — all now run live
  (design-open gate satisfied; see below).
- **Doc-19 totality invariant:** `docs/architecture/reference/19-ast-dispatch-invariant.md`
  (REQ-AST-08 — the Family-1 house pattern).
- **Item-4 sentinel house style:** `src/sysml_codegen/**/constraint_report.py:89-141`.
- **Required Reading (background):** epic `epic_pipeline_truth.md` (Item 5, R1–R4);
  `docs/architecture/reference/10-output-registry.md`, `12-virtual-binding-rewrite.md`.

## Design-Open Gate — OUTCOME (mandated by spec, done this session)

All probe fixtures repaired and every probe ran live. Verification table updated in the spec.

| Finding | Before | Live outcome |
|---|---|---|
| D3-1 | trace | **CONFIRMED (live).** `in x = Doubler(v=a)` → `x` in `unbound_params`, zero warnings. Fixture repaired: `max(...)` (does not resolve to a Behavior in this SysIDE build) → calc-def invocation. |
| D3-8 | trace | **CONFIRMED (live).** `sum(cell.total_cost) ^ exponent` → `'(… ^ exponent)'`, `has_unsupported_nodes=False`. |
| D3-10 | trace | **CONFIRMED (live).** Two `Motor` partdefs → fallback returns `100.0` for both. |
| D3-7 | trace | **RECLASSIFIED → closed-by-construction (live).** The two-FORMULA-`Widget.result` shape *raises loudly* — `ValueError: OutputRegistry scoped key collision: 'Widget.result'…` at `core/output_registry.py:72`, **before** the resolution-map merge. The silent-cross-wire claim is refuted for the reachable shape. **Family 3 shrinks** to {D3-10, D3-15, D3-11b}. |

Fixture repairs: added an isolated minimal `NoopCalc` calc def + usage to `d37`/`d38`/`d310`
(so `build_pipeline_context` accepts the model without touching the FORMULA/aggregation/redef
shape each probe exercises); swapped the `d3-1` invocation to `Doubler(v=a)`.

## Core Concept

**Totality at the choke points.** Every dispatch, report, lookup, and exception handler on a
load-bearing extraction/resolution path must be *total and loud*: an input it cannot handle
routes to a **distinct, warned sentinel** — never to a valid-looking category, a discarded
report, a merged bucket, or a swallowed `None`. Clean models are unaffected because the loud
arm fires only on the shape that would otherwise corrupt output.

This is the doc-19 totality invariant (REQ-AST-08 — literals dispatch before the invocation
catch-all in `reconstruct_expression`) generalized from the *display* dispatch to the
*extraction/classification/lookup* dispatches whose silent else-arms corrupt the wired vs
entry-point ledgers. It composes with what already exists:

- The **doc-19 pattern** (distinct sentinel + warn naming param/part/node-type) — extended,
  not reinvented.
- The **Item-4 report house style** (`render_constraint_report`: always-present
  scanned/reported/excluded INFO + per-item INFO + summary WARN only when >0) — reused for
  the gated-report and zero-found sentinels.
- The **OutputRegistry collision guard** (`register_scoped` raises on a duplicate scoped
  key) — the load-bearing closer for D3-7, and the pattern SC-4 A1 copies for key injectivity.
- The `warnings` list `_extract_bindings` already threads and the `ExtractionReport` it
  already builds — Family 1 and Family 2 wire into these, adding no new plumbing.

The fix is per family at its choke point, not per site (R4 step 3 — the anti-whack-a-mole
contract).

## Key Bets

- **B1.** Every reachable unhandled shape at these choke points is one this item should
  *reject loudly*, not *support* — support is a Non-Goal deferred to the epic. *If false →
  we'd be rejecting models users legitimately expect to work, and the loud arm becomes noise.*
- **B2.** The doc-19 totality pattern generalizes to the extraction/classification dispatches
  without changing ledger semantics for clean models — the loud arm is unreachable on any
  clean corpus fixture. *If false → clean fixtures regress with new WARNINGs and the
  byte-identical / zero-WARNING success criteria break.*
- **B3.** The OutputRegistry scoped-key collision guard closes every reachable D3-7 silent
  cross-wire: any silent merge needs two entries at the same `(bare part_name, python_name)`
  *with a channel*, and every such FORMULA entry registers the colliding `key_f` so the guard
  raises first. *If false → a silent cross-wire survives via a non-FORMULA resolution path and
  D3-7 needs the QN re-key after all.*
- **B4.** "Value present but unparseable" is distinguishable from "genuinely absent" by
  inspecting the raw source string at the shared SC-5/D3-12 omission site. *If false → we
  either warn on legitimately-absent defaults (noise) or miss the real drop.*

## Key Decisions

- **D1 — Family 1 fix = thread `warnings` + total terminal arm.** `_extract_single_binding`
  (`usage_extractor.py:683`) receives the `warnings` list its caller `_extract_bindings`
  already holds (line 650); the terminal arm at 748 warns (naming param + node type) and
  routes to a *distinct* diagnostic disposition, not silent UNBOUND reuse. The legitimately-
  unbound arm at 693 (no `feature_value_expression`) stays silent — that is correct UNBOUND.
  *Rejected: warning at the `_extract_bindings` caller (loses the node-type context the arm
  has).*
- **D2 — D3-2 = hard-diagnose 3+-segment chains (LOUD-REJECT).** `_parse_chain_expression`
  (`usage_extractor.py:756`) counts real segments via the existing
  `extract_feature_chain_segments` (`extraction/expression_utils.py:279`); >2 segments →
  warn + reject (do not truncate to root). 2-segment/V11 path unchanged. *Rejected: full
  multi-hop parse — new capability, Non-Goal; FILED as `[MULTIHOP-CHAIN-PARSE]`.*
- **D3 — D3-8 = use the power-emitting map + set `has_unsupported`.** The aggregation walker
  (`hierarchy_resolver.py:370,382`) maps known operators through the Python-emitting map so
  `^`→`**`; an operator absent from that map sets `ctx.has_unsupported = True` (the pattern
  already used at the unknown-node arm, line 457) instead of the silent `f" {operator} "`
  fallback. *Rejected: leaving the pass-through fallback (silently emits Python XOR).*
- **D4 — SC-5 + D3-12 = warn-on-unparseable-present at the shared omission site, fix both
  roots.** The two roots (`parameter_groups.py:192` eval `except→None`; `:710` `float()→None`)
  both feed `if default_value is None: continue` at the design-attr loop (`:601`). The fix
  warns *only* when the raw source carried a value that parsed to `None` (present-but-
  unparseable), silent when genuinely absent — one predicate at the shared site, both roots
  narrowed. *Rejected: typed pre-fill of a fabricated value (hides the real gap); double-
  patching each root independently (leaves a gap at the shared site).*
- **D5 — Family 3 = require-unique-and-warn at lookup; no follow-on split.** D3-10
  (`graph_builder.py:1349`) and D3-15 (`pipeline_builder.py:597`) get a collision warning at
  the lookup/derivation site (leaf-name match is structurally required in the fallback, so a
  QN re-key is not possible there); D3-11b gets a lookup-time ambiguity warning. Churn is
  small (three collision-warns, no re-key), so the family lands **in-item** — the
  pre-authorized split is **not taken**. D3-7 is closed-by-construction (pin the guard). The
  bare→QN re-key of the D3-7 resolution map is optional defense-in-depth, deferred pending a
  consumer audit. *Rejected: bulk QN re-key (large churn for no reachable silent failure).*
- **D6 — D3-14 stays in Family 4, no split.** Narrow the `except` at `preservation.py:92-95`,
  log at WARNING, and distinguish a *transient* read/parse error (preserve the impl) from a
  *genuinely-absent* impl (regenerate). Blast radius is contained to `preservation.py` + its
  one CLI caller. *Rejected: its own item (over-scoped for a small narrow-and-log + a
  preserve-on-transient branch).*
- **D7 — SC-4 = broaden guard + prepend + injective key construction.** `sanitize_name`
  (`core/qualified_names.py:12`) broadens the keyword guard to `keyword.kwlist`, prepends a
  safe prefix when the result starts with a digit or is empty (so `.isidentifier()` always
  holds), and the empty-input early return no longer yields `""`. Channel/EP **key
  construction** gains a collision fail-fast (the `register_scoped` raise pattern). *Rejected:
  post-hoc collision detection downstream (too late — the wrong key is already wired).*

## Architecture

Five edit clusters, each at its family's choke point. Data flow is unchanged for clean
models; the new arms fire only on the trip shapes.

- **Family 1 — extraction dispatch** (`extraction/usage_extractor.py`,
  `extraction/hierarchy_resolver.py`, `extraction/computed_attribute_extractor.py`). The
  binding classifier's terminal arm and the chain parser gain totality; the aggregation
  walker's operator map is corrected; the EXPOSE alias loop (D3-16) gains an `else` that warns
  on the cross-part single-hop shape the Item-10 gate misses. Diagnostics ride the existing
  `warnings` list → `ExtractionReport`.
- **Family 2 — report surfacing** (`orchestration/pipeline_builder.py`,
  `analysis/phantom_detector.py`, `resolution/output_registry_builder.py`). D3-4 renders the
  extraction report (live + from-snapshot, INV parity). D3-5 and D3-13 and the pattern-3 sites
  get the Item-4 scanned/reported/excluded sentinel.
- **Family 3 — lookup uniqueness** (`resolution/graph_builder.py`,
  `orchestration/pipeline_builder.py`, `analysis/dependency_backtracker.py`). Collision-warn
  at the leaf-name / first-wins lookups. D3-7 pins the existing OutputRegistry guard.
- **Family 4 — exception handlers** (`snapshot/loader.py`, `analysis/parameter_groups.py`,
  `generation/preservation.py`). Narrow-and-log; preserve-on-transient for `--smart-regen`.
- **Sanitizer** (`core/qualified_names.py`) + **key construction** (channel/EP key sites).
  Always-legal-identifier + injectivity fail-fast.

## Required Invariants

- **INV-1 (totality).** Every terminal dispatch arm at the Family-1 choke points routes an
  unhandled input to a *distinct* disposition + a WARN naming param/part/node-type; it never
  reuses a valid category (UNBOUND, XOR pass-through) for an unhandled shape.
- **INV-2 (report parity).** The extraction warning report is rendered on **both** the live
  and from-snapshot paths, identically (the Item-4 INV-B property).
- **INV-3 (uniqueness-or-warn).** Every name-keyed lookup either keys by QN or warns when a
  bare-name lookup is ambiguous; no first-wins collision is silent.
- **INV-4 (preserve-on-transient).** `--smart-regen` never overwrites a valid handwritten
  impl to a stub on a transient read/parse error.
- **INV-5 (sanitizer).** For all `x`, `sanitize_name(x)` is a legal Python identifier and not
  a keyword; two sibling names that sanitize to one channel/EP key **fail fast** at key
  construction.
- **INV-6 (silent-on-clean).** Every clean corpus fixture still generates with zero WARNINGs;
  repetitive diagnostic classes use the count-summary style (RN-7).

## Component Overview

- `extraction/usage_extractor.py` — `_extract_single_binding` (D3-1 terminal arm),
  `_parse_chain_expression` (D3-2 hard-diagnose), template-detection sentinel (pattern-3).
- `extraction/hierarchy_resolver.py` — `_walk_aggregation_ast` operator handling (D3-8).
- `extraction/computed_attribute_extractor.py` — EXPOSE alias loop `else` (D3-16); the D3-9
  tripwire guard (non-literal AST root + empty refs).
- `orchestration/pipeline_builder.py` — render the discarded report (D3-4); `design_prefix`
  collision-warn (D3-15); pattern-3 sentinels (scoped-alias, self-named rescue, design-override
  rewrite, empty-render).
- `resolution/output_registry_builder.py` — Phase-1a unknown-calc-def skip warns (D3-5).
- `resolution/graph_builder.py` — `_find_literal_redefinition` fallback collision-warn (D3-10);
  the D3-7 guard pin + invariant (no re-key by default).
- `analysis/dependency_backtracker.py` — `_usage_by_name` lookup ambiguity warn (D3-11b).
- `analysis/parameter_groups.py` — `_parse_default_value` + expr-eval narrowed; warn-on-
  unparseable-present at the shared omission site (SC-5, D3-12).
- `analysis/phantom_detector.py` — zero-found sentinel (D3-13).
- `snapshot/loader.py` — `usage_type_map` `except…pass` narrowed + logged (D3-6).
- `generation/preservation.py` — narrow `except` + preserve-on-transient (D3-14).
- `core/qualified_names.py` — `sanitize_name` always-legal-identifier (SC-4 A2); key
  construction collision fail-fast (SC-4 A1).

## Non-Goals

- Implementing support for the rejected shapes (InvocationExpression execution, multi-hop
  chains, non-uniform arrays) — loud rejection only.
- Item 2's sites (the two `0.0`-truthiness classifiers, `design_overrides` threading) and
  Item 4's landed fixes — coordination fences, do not touch.
- The bulk QN re-key of the D3-7 resolution map (optional defense-in-depth, deferred).
- The `[MULTIHOP-CHAIN-PARSE]` follow-on and the `[D3-HYGIENE-TAIL]` consolidated entry —
  FILED at item close, not implemented here.

## Implementation Notes

- **Thread the existing `warnings` list; do not add plumbing.** `_extract_bindings` already
  has it (line 650) and `extract_calculation_usages` already builds the `ExtractionReport`
  (line 557). Family 1 diagnostics append to that list; Family 2's D3-4 renders it.
- **D3-2 segment count.** Use `extract_feature_chain_segments` for the *count* only — do not
  build the resolved path from it (that is the deferred multi-hop feature).
- **D3-8 map choice (confirmed).** Swap `OPERATOR_MAP` (`expression_utils.py:13`, `^`→` ^ `
  XOR) for `PYTHON_OPERATOR_MAP` (`expression_compiler.py:151`, `^`→` ** ` at `:157`) at the
  walker's two operator sites (`hierarchy_resolver.py:370,382`). That map's values are
  `str | None`; a `None` value (or an absent operator) is the `ctx.has_unsupported = True`
  trigger, mirroring the unknown-node arm at line 457.
- **SC-5/D3-12 predicate.** At `parameter_groups.py:601`, warn when `attr.default_value` is
  truthy but `_parse_default_value(...)` returned `None`; silent when `attr.default_value` is
  absent. Apply the mirror predicate at the expr-eval root so both roots share one site.
- **Sentinel verbosity (RN-7).** Repetitive classes (phantom scan, scoped-alias registration,
  self-named rescue) use a build-level count-summary INFO + WARN-only-when-`>0`, not a WARN
  per site. Follow `render_constraint_report`'s three-part shape exactly.
- **Byte-identical carve-outs.** Only D3-2 (`deep_cross_scope_probe` Pattern-A pin flips
  truncation→diagnostic; one scoped snapshot re-capture) and D3-8 (`^` corpus has none, so
  still byte-identical on the committed corpus). Every clean fixture holds INV-6.

## Potential Risks

- **Clean-fixture WARNING regression (INV-6).** A totality arm mis-fires on a legitimate
  clean shape → byte/zero-WARNING break. *Mitigation:* every new diagnostic lands with a
  silent-on-clean test over the corpus; run the full baseline diff before commit.
- **B3 over-claim (D3-7).** A non-FORMULA resolution path reaches the bare-name map and
  cross-wires silently despite the guard. *Mitigation:* the D3-7 test asserts the guard
  *raises* on the FORMULA shape; the plan does the consumer audit before deciding to skip the
  QN re-key. If the audit finds a silent path, D3-7 re-enters the re-key set.
- **D3-14 transient/permanent boundary.** Misclassifying a genuinely-broken impl as transient
  → a broken impl is preserved instead of regenerated. *Mitigation:* the transient set is
  read/IO errors and parse failures on a non-empty file; a genuinely-empty impl stays the
  regenerate case.
- **Register write fence.** The discovery register (`.project/research/…`) is outside this
  session's write scope (Item-6 audit reads it concurrently). The D3-7 reclassification is
  recorded in the spec now; the register row travels with the implement change (see Handoff).

## Integration Strategy

Diagnostics reuse the existing `warnings`/`ExtractionReport`/logger channels and the Item-4
report renderer, so they surface through the same CLI path users already see. No new
subsystem, no new config. The trip fixtures under `probes/fixtures/` graduate to permanent
`tests/fixtures/` entries with their diagnostic (or raises-loudly, for D3-7) pinned.

## Validation Approach

- Per CONFIRMED finding: a **fires-on-shape** test (expectation independently anchored, never
  computed by the code under test) + a **silent-on-clean** test. D3-7 and D3-3 are
  closed-by-construction: D3-7 pins the OutputRegistry `ValueError`; D3-3 gets a debug-guard +
  the stated SysIDE invariant, no silent-drop test.
- SC-4: a unit pin over leading-digit / keyword (all `keyword.kwlist`) / empty / all-symbol
  inputs; a collision fail-fast pin at key construction.
- Full baseline diff byte-identical except the two named carve-outs; zero-WARNING sweep over
  clean corpus (INV-6).
- Touched components' reference docs + matrix rows move in the same change (R4 step 4).

## Next-Stage Handoff

**Fixed (do not reopen):** the four-family choke-point map; the LOUD-REJECT ruling for D3-2;
D3-7 is closed-by-construction (Family 3 re-key set is {D3-10, D3-15}); D3-11b and D3-14 fixes
land in-item (no split); the design-open probe gate is satisfied and the spec table finalized.

**Open (plan decides):** the D3-7 consumer audit (whether the optional QN re-key is worth
doing); the precise sentinel-verbosity split across pattern-3 sites (bounded by RN-7); the
D3-14 transient/permanent error boundary set.

**Risk to de-risk first:** INV-6 (clean-fixture zero-WARNING) — write the silent-on-clean
tests and run the baseline diff *before* landing any diagnostic, so a mis-firing totality arm
is caught immediately rather than at audit.

**Register carry (must travel with implement).** The discovery register §D3 row for **D3-7**
still reads CONFIRMED-latent "silent cross-wire" and must be reclassified to
closed-by-construction (guard already loud) in the implement change — the same edit that
updates the register's per-row Disposition at item close. Recorded here because the register
is outside this session's write fence.

## Appendix — Per-finding fix map (file:line → change)

| Finding | Site | Change |
|---|---|---|
| D3-1 | `usage_extractor.py:748` | Thread `warnings` into `_extract_single_binding`; terminal arm warns (param + node type), distinct disposition. |
| D3-2 | `usage_extractor.py:756-779` | Count segments via `extract_feature_chain_segments`; >2 → warn + reject, no root-truncation. |
| D3-3 | `usage_extractor.py:789-796` | Debug-guard/assert on `(None,None)` return + stated SysIDE invariant (closed-by-construction). |
| D3-4 | `pipeline_builder.py:689` | Render the `_report` (Item-4 shape), live + from-snapshot. |
| D3-5 | `output_registry_builder.py:167` | Phase-1a `if not calc_def:` skip warns. |
| D3-6 | `loader.py:423-424` | Narrow `except`; log the dropped `usage_type_map` key (offline-parity guard). |
| D3-7 | `output_registry.py:72` / `graph_builder.py:984` | Pin the guard raises + state invariant; QN re-key optional (audit first). |
| D3-8 | `hierarchy_resolver.py:370,382` | Power-emitting map; unknown op → `has_unsupported`. |
| D3-9 | `computed_attribute_extractor.py:92` | Tripwire: non-literal AST root + empty refs warns; `not refs → LITERAL` stays. |
| D3-10 | `graph_builder.py:1349-1350` | Fallback leaf match: warn on ambiguous same-leaf collision. |
| D3-11b | `dependency_backtracker.py:247` | Track collisions at index build; warn when a bare-name target lookup is ambiguous. |
| D3-12 | `parameter_groups.py:192` + `:601` | Narrow eval `except`; warn-on-unparseable-present at shared omission site. |
| D3-13 | `phantom_detector.py:165-173` | Zero-found scanned/reported sentinel. |
| D3-14 | `preservation.py:92-95` | Narrow `except`, log WARNING, preserve-on-transient. |
| D3-15 | `pipeline_builder.py:597` | Collision-warn on >1 distinct `design_prefix`. |
| D3-16 | `computed_attribute_extractor.py:315` | `else` arm warns on cross-part single-hop EXPOSE_PURE the Item-10 gate misses. |
| SC-4 A1 | channel/EP key construction | Collision fail-fast (`register_scoped` pattern). |
| SC-4 A2 | `qualified_names.py:12-37` | `keyword.kwlist` guard; prepend prefix on digit/empty; empty-input no longer `""`. |
| SC-5 | `parameter_groups.py:710` + `:601` | Narrow `float()`; warn-on-unparseable-present at shared site. |

---
Next Step: After approval → `/_my_plan` (family-by-family, INV-6 tests first).

ARTIFACT: .project/active/silent-failure-hardening/design.md
