# Design: Expression Reconstruction Fidelity (SC-6)

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-05
**Complexity:** MEDIUM (0.5–1 day)
**Branch:** upstream-findings-epic
**HEAD at design:** 1f1b227
**Epic:** UPSTREAM-FINDINGS — Item 6

---

## Overview

Two small display-path fixes in `expression_utils.py` so generated docstrings and
stencils show real math: dispatch literal nodes before the invocation catch-all,
and parenthesize operator expressions where grouping changes meaning. Then
regenerate the affected baselines through the capture scripts under a review gate
that proves executable content is byte-identical.

## Related Artifacts

- **Spec (contract):** `.project/active/expression-fidelity/spec.md`
- **Spec review + resolutions:** `.project/active/expression-fidelity/spec-review.md`
- **Research (SC-6, authoritative root cause):** `.project/research/20260705_upstream-findings-deep-research.md` (§SC-6, lines 178–186)
- **Epic:** `.project/backlog/epic_upstream_findings.md` (Item 6; R1/R2/R3)
- **Reference doc (owner):** `docs/architecture/reference/19-ast-dispatch-invariant.md` (REQ-AST family)
- **Verification matrix:** `docs/architecture/verification-matrix.md` (REQ-AST rows 82–88)
- **Code:** `src/sysml_codegen/extraction/expression_utils.py`

## Research Findings

**The bug is two independent defects, both confirmed against HEAD.**

1. **Branch ordering** — `reconstruct_expression` (`expression_utils.py:34-79`)
   checks the invocation catch-all (`hasattr(expr_node, "function")`, line 57)
   *before* the literal branches (lines 64-77). Every SysIDE node carries a
   derived KerML `.function`, so every literal hits the catch-all first and
   stringifies to `LiteralRationalEvaluation()` / `LiteralIntegerEvaluation()`.
   The literal branches are dead code as written. They also detect via
   `type(expr_node).__name__` (lines 64, 68, 72, 76) rather than `is_instance`.

2. **No parenthesization** — `reconstruct_operator_expression`
   (`expression_utils.py:82-111`) emits `f"{left}{op_str}{right}"` with no parens
   (line 96), so a meaning-changing group is lost.

**Paren-churn evidence (settles the algorithm choice).** I pulled every
operator `expression_text` from the 11 committed snapshots. The mixed-precedence
ones all follow natural precedence — e.g. `eta_thermal * p_fusion + eta_direct *
p_input`, `r_inner + r_outer / 2.0 - r_major`, `p_fusion * 2.0 / 3.0`
(`attr_expr_probe`), and the additive chains in `solar_battery_model`. **None**
has a grouping that overrides precedence (no `(a + b) * c`, no same-precedence
right-child). So under **precedence-aware** parenthesization, **zero** baseline
expressions gain a paren — only literal substitution churns the text. Under
**always-paren**, every one of the ~30+ multi-operator expressions gains nested
parens (`((a + b) + c)`), churning text with no fidelity gain. Precedence-aware
wins decisively. (Full sample list in Appendix A.)

**The repro needs a genuine grouping.** `capacity * rate + capacity * (rate /
2.0) * 3.0` parses so that `(rate / 2.0)` is the **right** child of a `*` node.
`/` and `*` share precedence and are left-associative, so a right child at equal
precedence *does* require parens (`capacity * rate / 2.0` would mean
`(capacity * rate) / 2.0`). Precedence-aware rules reproduce the group exactly.
No existing fixture exercises this shape — hence a new fixture (see Component 4).

**Aggregation executable path is the real risk, not the calc path.** Confirmed
`_walk_aggregation_ast` (`hierarchy_resolver.py:432-433`) delegates literal
leaves to `reconstruct_expression`, whose return becomes
`transformed_expression` (`:485`) → `compiled_expression`
(`graph_builder.py:1343-1348`) → `auto_impl_context` (`:1358-1361`). Executable
output stays byte-identical only for corpus-scoped reasons (spec Known
Requirements). The regen review is the gate that checks this, not a structural
guarantee.

**License gating pattern exists.** `test_snapshot_generation.py:35-47` defines
`requires_license = pytest.mark.skipif(not _license_available(), ...)` by trying
`SysMLDataExtractor(...).load_models()`. The real-AST test reuses this exactly.

## Core Concept

The reconstructor is a recursive AST-to-text function whose dispatch order and
operator rendering are both slightly wrong. The fix is **local and structural**:
put the literal/null checks where the recursion can actually reach them (before
the catch-all), and teach the operator renderer one rule — *wrap a child in
parens iff its operator binds looser than the parent, or equal-and-on-the-
associativity-unfavored side*. That single rule, driven by the KerML precedence
table, both preserves real groups and adds nothing where precedence already
reads correctly. Everything else — FCE, FRE, invocation, chains — is untouched.

The change reaches executable fields on exactly one path (aggregation), and there
only inertly for today's corpus. So the design's second half is not code but a
**review gate**: regenerate baselines through the capture scripts and diff
`compiled_expression` / `auto_impl_context` for byte-identity. That gate is what
converts "empirically safe" into "checked safe."

## Key Bets

- **B1.** Every literal `is_instance` check (`LiteralInteger/Rational/Real/
  Boolean/String`, `LiteralInfinity`, `NullExpression`) is `False` for
  `OperatorExpression`, `FeatureReferenceExpression`, and
  `FeatureChainExpression` nodes. *If false → moving literals above the catch-all
  could capture an operator/FRE/FCE node and corrupt a currently-correct
  expression.* (Spec L3-2 reassurance confirms this; verified by the reorder
  carrying no opposite-bug risk.)
- **B2.** For the current corpus, no `Literal*Evaluation` string lives in any
  executable field — every occurrence is in `expression_text` /
  `raw_expression_text` / `calc_expressions`. *If false → the display fix would
  change executable output and the byte-identity gate would (correctly) hard-stop
  the regen.*
- **B3.** SysIDE literal nodes expose numeric/boolean/string `.value` on live
  parsed nodes (already assumed by the existing dead literal branches). *If false
  → the reached literal branch returns the fallback `str(node)` and text is still
  wrong, just differently.*

## Key Decisions

- **D1. Precedence-aware parenthesization.** *Rejected: always-paren* — churns
  every multi-operator baseline expression for zero fidelity gain (evidence
  above; Appendix A). Precedence-aware adds parens only where a group overrides
  natural precedence, which is zero existing baselines and exactly the repro.
- **D2. `is_instance` dispatch for all literal/null branches**, replacing
  `type(expr_node).__name__`. *Rejected: keep name-based checks* — inconsistent
  with the rest of the function (FCE/OE/FRE already use `is_instance`) and with
  `is_literal_expression`; the spec mandates `is_instance` (HARD).
- **D3. `NullExpression` → `"null"`; `LiteralInfinity` → `"*"`.** *Rejected for
  infinity: `"inf"`* — `*` is KerML's actual textual notation for an unbounded
  literal; `inf` is invented notation. These strings land in engineer-facing
  docstrings, so textual-notation fidelity wins. `"null"` matches the existing
  branch (`:76-77`) and KerML notation. Neither appears in the current corpus, so
  both are defensive branches with no baseline churn.
- **D4. New source-only fixture for the real-AST test**, parsed live, no
  committed snapshot. *Rejected: extend `attr_expr_probe`* — would couple the
  regression proof to that fixture's snapshot regen and add grouping churn to an
  unrelated fixture. A dedicated fixture isolates the repro and adds zero regen
  burden. *Rejected: drive the assertion from a committed snapshot* — a snapshot
  is stored text, not an AST; it cannot exercise the `.function`-bearing node
  that caused the bug.
- **D5. Revise REQ-AST-03 in place AND add new IDs (REQ-AST-08, -09).**
  *Rejected: supersede REQ-AST-03 with a new ID* — its FCE<OE<FRE ordering is
  still canonical and correct; only its "...Literal" tail (implying literal-last,
  after invocation) is part of the defect. Fix the tail, keep the ID, add IDs for
  the two genuinely new behaviors.

## Architecture

Two functions change; nothing else in the call graph moves.

```
reconstruct_expression(node)            # dispatch — reorder + is_instance
  ├─ str / None            → passthrough        (unchanged)
  ├─ FCE                   → extract_feature_chain_name   (unchanged)
  ├─ OE                    → reconstruct_operator_expression  (now parenthesizes)
  ├─ FRE                   → extract_feature_reference_name   (unchanged)
  ├─ LITERALS + NULL       → value text          ← MOVED above the catch-all
  └─ invocation catch-all  → "func(args)"         (unchanged, now last)

reconstruct_operator_expression(node)   # rendering — precedence-aware parens
  └─ wrap child iff _needs_parens(parent_op, child_node, side)
```

`is_literal_expression` (`:168`) gains `LiteralInfinity` and `NullExpression` so
it stays consistent with the dispatch set (spec HARD).

**Data flow, display path (calc modules):** node → `reconstruct_expression` →
`calc_expressions` (`extractor.py:231-233`) / `expression_text` → docstrings,
stencils. Executable text for calc modules comes from a *different* function
(`expression_compiler.build_expression_ast`) this item does not touch.

**Data flow, executable path (aggregation modules):** node →
`_walk_aggregation_ast` → `reconstruct_expression` (literal leaves only) →
`transformed_expression` → `compiled_expression` → `auto_impl_context`. Inert
today because the aggregation walker has the *same* literal-after-invocation
ordering (a literal is marked unsupported before delegation), so
`compiled_expression` is never built from a literal. **Not fixed here** (Non-Goal;
touches an executable path) — documented as a REQ-AST-03 known deviation and
filed to BACKLOG.

## Required Invariants

- **INV-1 (executable byte-identity).** After regen, `compiled_expression`,
  `compilation_results`, `auto_impl_context`, `compilability`, pipeline YAML
  wiring, and channel names are byte-identical to HEAD across all baselines. Any
  diff is a hard stop. This is the checked gate; it is corpus-scoped, not
  structural.
- **INV-2 (literal totality).** After the fix, no `Literal*Evaluation` string
  appears in any regenerated snapshot or baseline. Enforced offline by a
  conformance guard (no license needed).
- **INV-3 (repro fidelity).** `capacity * rate + capacity * (rate / 2.0) * 3.0`
  reconstructs to itself from a real parsed AST — every literal as its value,
  the meaning-changing group preserved. Proven by the license-gated real-AST
  test.
- **INV-4 (dispatch safety).** Literal/null `is_instance` checks never match
  OE/FRE/FCE, so the reorder cannot capture a non-literal node (B1).

## Component Overview

1. **`reconstruct_expression` reorder** (`expression_utils.py:34-79`). Move the
   five `Literal*`, `LiteralInfinity`, and `NullExpression` branches above the
   invocation catch-all (line 57), converting each to `SysideAdapter.is_instance`.
   The catch-all becomes the last branch before `str(node)`.

2. **`reconstruct_operator_expression` parenthesization**
   (`expression_utils.py:82-111`). Add a precedence table and a `_needs_parens`
   helper; wrap each reconstructed operand when the helper says so. Covers
   binary, unary, and n-ary operand counts.

3. **`is_literal_expression` alignment** (`expression_utils.py:168-180`). Add
   `LiteralInfinity` and `NullExpression` (one `is_instance` clause each).

4. **Real-AST regression fixture + test.** New `tests/fixtures/expr_paren_probe/`
   (source only) with a calc def whose output expression is the repro shape. New
   license-gated test parses it live, asserts the reconstructed text and absence
   of `Literal*Evaluation`.

5. **Offline literal-totality guard.** New conformance test greps committed
   snapshots + baselines for `Literal*Evaluation` and asserts zero. Runs without a
   license; guards INV-2 continuously after regen.

6. **Doc + matrix updates.** Revise REQ-AST-03; add REQ-AST-08/-09; note
   `_walk_aggregation_ast` deviation in doc 19; add matrix rows; BACKLOG entry;
   PUSH-DOWN note.

## The Precedence Table (D1)

From KerML Table 6 (§8.2.5.8.1), authoritative over the grammar. Rank 1 = tightest.

| Rank | Operators (in `OPERATOR_MAP`) | Assoc |
|------|-------------------------------|-------|
| 2 | unary `-`, `not` | prefix (tighter than all binary, incl. power) |
| 3 | `**`, `^` | **right** |
| 4 | `*`, `/` | left |
| 5 | `+`, `-` (binary) | left |
| 7 | `<`, `>`, `<=`, `>=` | left |
| 9 | `==`, `!=` | left |
| 10 | `and` | left |
| 12 | `or` | left |
| 13 | `implies` | left |

Two KerML-specific facts the reconstructor must honor:

- **`**`/`^` are right-associative** — `a ** b ** c` = `a ** (b ** c)`. The
  *left* child at equal precedence needs parens for power (the mirror of the
  left-associative rule).
- **Unary `-`/`not` bind tighter than `**`** — differs from Python/math. `-a **
  b` = `(-a) ** b`. (No current corpus expression exercises this; the table is
  pinned so a future one renders right.)

**Paren rule (pseudocode, ≤10 lines):**

```
def needs_parens(parent_op, child_node, side):   # side ∈ {"left","right"}
    if child_node is not an OperatorExpression with a binary operator: return False
    cp, pp = prec(child_op), prec(parent_op)
    if cp < pp:  return True          # child binds looser → must group
    if cp > pp:  return False         # child binds tighter → safe
    # equal precedence: group the associativity-unfavored side
    return side == ("left" if right_assoc(parent_op) else "right")
```

Unary operands and function-call/FCE/FRE children never need wrapping (they bind
tighter than any binary or are atomic). For n-ary operator nodes (>2 operands),
treat as a left fold of the same operator: same-operator children never need
parens; a looser-precedence child still does.

## Regen Procedure (R1/R2/R3)

Two tiers, in order. The review checklist implements the spec's HARD gates.

**Tier 1 — extraction snapshots (live, needs license).** Run
`scripts/capture_extraction_snapshots.py`. The display fix manifests in
`expression_text` / `raw_expression_text` / `calc_expressions`. Affects the 11
snapshots carrying `Literal*Evaluation` (confirm the exact set at plan time —
`alias_agg_probe`, `attr_expr_probe`, `catf_mfe_model`, `chain_override_probe`,
`expression_binding_probe`, `issue22_model`, `return_styles`, `retype_model`,
`sample_model`, `solar_battery_model`, `unresolvable_attr_probe`).

**Tier 2 — pipeline baselines (offline).** Run
`scripts/capture_pipeline_baselines.py` — rebuilds
`baseline_outputs/{solar_battery,catf_mfe,attr_expr_probe}/computation_graph.json`
from the committed snapshots. Corrected display text flows into `calc_expressions`.

**Review checklist (every regenerated file):**

1. **Byte-identity gate (INV-1, HARD).** Diff `compiled_expression`,
   `compilation_results`, `auto_impl_context`, `compilability`, YAML wiring,
   channel names. Any change → **hard stop**, investigate, report. No commit.
2. **Expected display classes only.** Accept: `Literal*Evaluation()` → value;
   added parens (expected: none, per Appendix A). Fields:
   `expression_text`, `raw_expression_text`, `calc_expressions`, derived
   docstrings.
3. **Unexpected-class rule (HARD).** Any diff that is neither an expected display
   class nor in the executable set → **hard stop**. If found benign, add it to
   the expected classes (with a note) before committing; never wave through.
4. **`captured_at` discipline (Item 3, HARD).** Commit only snapshots whose
   `expression_text` actually changed; revert timestamp-only rewrites (the 1
   committed extraction snapshot with no `Literal*Evaluation` restamps but must
   not be committed).
5. **One item's regen only (R3).** Do not fold in Item 5's churn (e.g.
   `quoted_owner_formula`) or any other item's baselines.

**License-window fallback.** Both live-dependent success criteria (zero
`Literal*Evaluation`; docstring render) block on Tier 1, which needs a live
license (expires 2026-08-06). If no license is available in the implement window:
land the code fix + the license-gated real-AST test + the offline totality guard,
and **flag regen as blocked to the orchestrator** — the item is not "done" until
Tier 1/2 run. Never hand-edit snapshots (R3).

## Non-Goals

- Fixing `_walk_aggregation_ast`'s twin ordering bug (executable path; Non-Goal,
  filed to BACKLOG).
- Replacing the reconstructor with `build_expression_ast` (Python-flavored,
  narrower; rejected in research).
- Any change to executable/compiled expressions or pipeline YAML wiring.
- FCE reconstruction (already correct, REQ-AST-07).
- Moving `expression_utils.py` to agentic-mbse (PUSH-DOWN epic — this item lands
  first so the moved code is born correct).

## Doc 19 & Matrix Changes

**Revise REQ-AST-03** (`19-ast-dispatch-invariant.md:36`, and matrix line 84):
change "FCE, OE, FRE, Literal" to state the ordering that literal/null branches
dispatch **before** the invocation catch-all, and that FCE<OE<FRE holds among the
reference/operator branches. Keep the existing `test_canonical_ordering_fce_oe_fre`
assertion green (it only checks FCE<OE<FRE; unaffected).

**Add REQ-AST-08** — `reconstruct_expression` SHALL dispatch all literal and
`NullExpression` branches (via `is_instance`) before the invocation catch-all.
*Verified by:* the license-gated real-AST test + offline totality guard.

**Add REQ-AST-09** — `reconstruct_operator_expression` SHALL parenthesize a child
operand iff it binds looser than its parent, or equal and on the associativity-
unfavored side (precedence-aware). *Verified by:* real-AST repro test (INV-3).

**Known deviation note (HARD).** In doc 19, note `_walk_aggregation_ast`
(`hierarchy_resolver.py:372,431`) as a documented deviation from revised
REQ-AST-03: it keeps literal-after-invocation ordering and carries the latent
literal-in-aggregation bug. Not fixed here (executable path).

**BACKLOG entry.** File the latent aggregation-literal bug: a literal operand in
an aggregation expression is mis-dispatched to the invocation catch-all
(`hierarchy_resolver.py:372`), marked `has_unsupported`, and its
`reconstruct_expression` delegation (`:433`) is dead. Fixing it touches an
executable path and needs its own item.

**PUSH-DOWN note.** Record in the P1 PUSH-DOWN design that this fix travels with
the `expression_utils.py` move; landing Item 6 first means the pushed-down
`reconstruct_expression` is already correct and the baseline churn was reviewed
once, here.

**agentic-mbse impact:** none (Item 12 accumulated list, R2). Internal display
fix; no MODELING_GUIDE / sysml-conventions / validator change.

## Potential Risks

- **Live license unavailable → regen blocks.** Mitigation: code fix + real-AST
  test + offline guard land independently; regen flagged to orchestrator, never
  hand-edited (see fallback).
- **A future literal-bearing aggregation fixture breaks INV-1.** Mitigation: the
  byte-identity gate catches it as a hard stop; the BACKLOG item removes the
  latent cause.
- **n-ary / power-associativity edge cases in the paren helper.** Mitigation:
  the real-AST test covers the multiplicative/additive repro; the precedence
  table pins power right-associativity and unary-tighter-than-power so the helper
  is correct even for shapes absent from today's corpus.

## Integration Strategy

Purely additive to the display path. No caller changes: `extractor.py` and
`hierarchy_resolver.py` call `reconstruct_expression` unchanged; only its output
text improves. Existing `reconstruct_expression` FCE/invocation unit tests
(`tests/unit/test_hierarchy_resolver.py:271-368`) stay green — those cases are
untouched by the reorder.

## Validation Approach

- **INV-3 (license-gated):** real-AST repro test → exact string + no
  `Literal*Evaluation`.
- **INV-2 (offline):** totality guard over committed snapshots/baselines → zero
  occurrences.
- **INV-1 (review gate):** byte-identity diff on executable fields during regen.
- **INV-4 / dispatch:** existing `test_ast_dispatch_invariant.py` REQ-AST-03
  suite stays green; new REQ-AST-08/-09 rows added.
- **Regression safety:** full `uv run pytest tests/` green pre-commit.

## Next-Stage Handoff

**Fixed:** precedence-aware (D1); `is_instance` dispatch (D2); `"null"` / `"*"`
renderings (D3); new source-only fixture (D4); REQ-AST-03 revised in place +
REQ-AST-08/-09 added (D5). The precedence table is pinned from KerML Table 6.

**Open (plan-time):** exact per-file occurrence counts (shift with prior regens);
final fixture directory name; whether the offline guard lives in a new test file
or an existing conformance module.

**De-risk first:** write the paren helper + real-AST test *before* touching
snapshots — the test is the cheapest proof the two fixes are correct, and it needs
only the new fixture (license-gated), not the full regen. Regen is mechanical once
the code is proven.

---

## Appendix A — Paren-Churn Evidence (Baseline Operator Expressions)

Distinct multi-operator `expression_text` values pulled from committed snapshots.
None has a meaning-changing group; under precedence-aware rules none gains a
paren. Under always-paren all would.

From `attr_expr_probe`:
- `eta_thermal * p_fusion + eta_direct * p_input`
- `m_neutron * p_fusion + p_input + eta_thermal * f_pump * eta_pump + f_subsystem * m_neutron * p_fusion`
- `p_fusion * <lit> / <lit>`  ( `*`/`/` same precedence, left-assoc → flat)
- `r_inner + r_outer / <lit> - r_major`  ( `/` binds tighter → flat)
- `<lit> * length + <lit> * width`
- `length * width * height`, `length + width`, `area * rate`, `cost * markup`

From `solar_battery_model` (representative): additive chains only, e.g.
`racking.capital_cost + electrical_panel.capital_cost + permitting.capital_cost`,
`sum(pv_module.capital_cost) + sum(inverter.capital_cost) + array_bos.capital_cost + misc_hardware_cost`.

**Repro (new fixture) — the one shape that legitimately needs a paren:**
`capacity * rate + capacity * (rate / 2.0) * 3.0` — `(rate / 2.0)` is the right
child of a `*` at equal precedence, left-associative → parens required.

---

**Next Step:** After approval → `/_my_plan`.
