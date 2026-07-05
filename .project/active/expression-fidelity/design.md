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

**Paren-churn evidence — read from source, not from buggy output (C1).** The
committed snapshot strings were produced by the no-paren reconstructor
(`expression_utils.py:96`), so a source group like `(a + b) * c` is *already
erased* to `a + b * c` in them. They cannot tell you whether the source had a
meaning-changing group — reading them was my original mistake. Re-deriving from
the `.sysml` **sources**, at least four committed baselines carry real groups the
fix will (correctly) restore:

- `attr_expr_probe/design.sysml:62` — `(r_inner + r_outer) / 2.0 - r_major`
  (a `+` as the left child of `/`, looser → parens).
- `attr_expr_probe/design.sysml:77-78` — `eta_thermal * (f_pump * eta_pump +
  f_subsystem) * (m_neutron * p_fusion)` (two groups: a `+` inside `*`, and a `*`
  right-child of `*` at equal precedence).
- `expression_binding_probe/library.sysml:8` — `combined_input * (1.0 +
  tax_rate)` (a `+` right-child of `*`).
- `catf_mfe_model/library/components/divertor.sysml:222` — constraint
  `... * (target_plates.surface_area_inner + target_plates.surface_area_outer) *
  ...` (a `+` group inside a `*` chain; `reconstruct_expression` serves constraint
  text too).

So under **precedence-aware** parenthesization these ~4 groups reappear exactly —
that is the fix working. Under **always-paren**, every one of the ~30+
multi-operator baseline expressions *also* gains redundant nesting
(`((a + b) + c)`), burying the four real groups in noise with no fidelity gain.
Precedence-aware wins decisively. The exact paren-gainer set is confirmed at
Tier-1 regen; the enumerated four are the floor. (Full source list in Appendix A.)

**The repro needs a genuine grouping.** `capacity * rate + capacity * (rate /
2.0) * 3.0` parses so that `(rate / 2.0)` is the **right** child of a `*` node.
`/` and `*` share precedence and are left-associative, so a right child at equal
precedence *does* require parens (`capacity * rate / 2.0` would mean
`(capacity * rate) / 2.0`). Precedence-aware rules reproduce the group exactly.
The corpus has meaning-changing groups of the *unequal*-precedence kind
(Appendix A), but no fixture exercises this **equal-precedence,
associativity-unfavored** shape — hence a new fixture (see Component 4).

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

- **D1. Precedence-aware parenthesization.** *Rejected: always-paren* — it would
  bury the ~4 real source groups (Appendix A) under ~30+ redundant nestings
  (`((a + b) + c)` on every additive chain), churning text with no fidelity gain.
  Precedence-aware restores exactly the source's meaning-bearing parens and adds
  nothing where precedence already reads correctly. (The earlier "zero baselines
  gain a paren" claim was wrong — it read the paren-erased output strings; the
  corrected evidence *strengthens* D1: it restores real groups the always-paren
  option would drown.)
- **D2. `is_instance` dispatch for all literal/null branches**, replacing
  `type(expr_node).__name__`. *Rejected: keep name-based checks* — inconsistent
  with the rest of the function (FCE/OE/FRE already use `is_instance`) and with
  `is_literal_expression`; the spec mandates `is_instance` (HARD).
- **D3. `NullExpression` → `"null"`; `LiteralInfinity` → `"*"`.** *Rejected for
  infinity: `"inf"`* — `*` is KerML's actual textual notation for an unbounded
  literal; `inf` is invented notation. These strings land in engineer-facing
  docstrings, so textual-notation fidelity wins. `"null"` matches the existing
  branch (`:76-77`) and KerML notation. Neither appears in the current corpus, so
  both are defensive branches with no baseline churn. *Recorded trade (m1):* in a
  rendered docstring `x * *` (multiply-then-infinity) is genuinely ambiguous to
  read; we accept that cost for notation fidelity since the branch is
  defensive-only and never fires on today's corpus. Revisit if a real
  infinity-bearing value expression ever appears.
- **D4. New source-only fixture for the real-AST test**, parsed live, no
  committed snapshot. *Rejected: extend `attr_expr_probe`* — would couple the
  regression proof to that fixture's snapshot regen and add grouping churn to an
  unrelated fixture. A dedicated fixture isolates the repro and adds zero regen
  burden. It earns its place because no existing fixture exercises the
  **equal-precedence, associativity-unfavored** shape (a same-precedence operator
  as the unfavored child, e.g. `a * (b / c)`) — the corpus *does* contain
  meaning-changing groups of the unequal-precedence kind (Appendix A), so the
  claim is "no fixture covers the equal-precedence case," not "no fixture has
  groups" (m4). *Rejected: drive the assertion from a committed snapshot* — a
  snapshot is stored text, not an AST; it cannot exercise the `.function`-bearing
  node that caused the bug.
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

4. **Real-AST regression fixture + test (license-gated).** New
   `tests/fixtures/expr_paren_probe/` (source only) with calc-def output
   expressions covering **all four helper branches**, so a C2/C3-class bug cannot
   ship silently (M2): the equal-precedence repro (`capacity * rate + capacity *
   (rate / 2.0) * 3.0`); an unequal-precedence gain on **each** side
   (`(a + b) * c` and `a * (b + c)`); a unary-over-binary case (`-(a + b)` and
   `not (a and b)`); and power right-associativity (`a ** b ** c` renders flat,
   `(a ** b) ** c` gains parens). The test parses live, asserts each reconstructed
   string exactly, and asserts no `Literal*Evaluation`. This is the spec's HARD
   real-parsed-AST proof (mocks masked the dispatch bug).

5. **Branch-coverage unit tests (no license).** Because the fixture test skips
   without a license (expiry risk), add no-license unit tests on
   `reconstruct_operator_expression` using the existing named-type stub pattern
   (`test_ast_dispatch_invariant.py:106-125` — class names carry the type so
   `is_instance`'s name fallback fires). These do not need `.function` because the
   parens logic is precedence-only, not dispatch. They pin the same five
   hand-traces (a-(b-c), a/(b*c), -(a+b), a**(b**c), (a**b)**c) so C2/C3 stay
   caught even offline. (Dispatch-ordering correctness still needs the real-AST
   test — that is the part mocks cannot cover.)

6. **Offline literal-totality guard.** New conformance test greps committed
   snapshots + baselines for `Literal*Evaluation` and asserts zero, **and**
   asserts the four enumerated paren-restorers (Appendix A) are present in the
   regenerated snapshots. Runs without a license; guards INV-2 and the M1 paren
   expectation continuously after regen.

7. **Doc + matrix updates.** Revise REQ-AST-03; add REQ-AST-08/-09; note
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

**Polarity convention (C2), stated once and explicitly.** `RANK[op]` is the rank
number straight from the table above: **smaller = binds tighter**. Do *not* build
a separate "tightness" number — all comparisons below are written against the
rank directly, so "child binds looser than parent" is `RANK[child] > RANK[parent]`.
(The earlier draft's `prec()` silently required the *inverse* of the rank column,
which would invert every unequal-precedence decision — exactly the `(a + b) * c`
category the fix targets. This convention removes that trap.)

**Paren rule (pseudocode):**

```
def binary_op_of(child):        # None unless child is a 2-operand OperatorExpression
    return child.operator if is_binary_operator_expr(child) else None
    # → None for literals, FRE, FCE, invocations, AND unary operator expressions

def needs_parens(parent_op, child, side):   # side ∈ {"left","right"}
    cop = binary_op_of(child)
    if cop is None: return False            # atomic / unary child → never wrap
    cr, pr = RANK[cop], RANK[parent_op]
    if cr > pr: return True                 # child binds looser → must group
    if cr < pr: return False                # child binds tighter → safe
    return side == ("left" if right_assoc(parent_op) else "right")  # equal → unfavored side
```

**Unary operands DO need wrapping (C3).** KerML puts unary `-`/`not` at rank 2,
tighter than *every* binary (including power). So the unary branch runs the *same*
helper on its operand with the unary op as parent: `needs_parens(unary_op,
operand, side="operand")`. Any binary operand (rank ≥3 > 2) wraps; a nested unary
operand is atomic (`binary_op_of` → None) so it doesn't — `- -a` stays flat.
Result: `-(a + b)` renders with parens, not the wrong `-a + b`. This corrects the
prior draft's false "unary operands never need wrapping."

Function-call/FCE/FRE children are atomic (`binary_op_of` → None). For n-ary
operator nodes (>2 operands of the *same* operator), treat as a left fold: same-
operator children never wrap; a looser-precedence child still does.

**Hand-traces (part of the artifact — these five must render exactly):**

| Input (source group) | Parent / child / side | `cr` vs `pr` | Decision | Renders |
|---|---|---|---|---|
| `a - (b - c)` | `-`(5) L / `-`(5) / right | `cr==pr`, L→unfavored=right | wrap | `a - (b - c)` |
| `a / (b * c)` | `/`(4) L / `*`(4) / right | `cr==pr`, L→unfavored=right | wrap | `a / (b * c)` |
| `-(a + b)` | unary `-`(2) / `+`(5) / operand | `cr=5 > pr=2` | wrap | `-(a + b)` |
| `a ** (b ** c)` | `**`(3) R / `**`(3) / right | `cr==pr`, R→unfavored=left | no wrap | `a ** b ** c` |
| `(a ** b) ** c` | `**`(3) R / `**`(3) / left | `cr==pr`, R→unfavored=left | wrap | `(a ** b) ** c` |

The last two prove right-associativity is handled: natural right-nesting stays
flat, forced left-nesting gets parens.

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
2. **Expected display classes only.** Accept: `Literal*Evaluation()` → value; and
   **added parens on the enumerated group-restorers** — at minimum the four in
   Appendix A (`attr_expr_probe` ×2, `expression_binding_probe`, `catf_mfe_model`),
   plus any others Tier-1 surfaces. These parens are the fix working, *not* churn
   to reject. Fields: `expression_text`, `raw_expression_text`,
   `calc_expressions`, derived docstrings. **The reviewer must positively confirm
   each enumerated paren appears** — because a C2-class polarity bug would drop
   exactly these parens, and a reviewer primed to "expect none" could wave the bug
   through. Missing an expected paren is a hard stop, same as a surprise one.
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
operand (binary or unary) iff it binds looser than its parent, or equal and on the
associativity-unfavored side (precedence-aware; polarity per the C2 convention;
unary operands per C3). *Verified by:* real-AST repro + branch fixture (INV-3,
license-gated) and the offline branch-coverage unit tests (the five hand-traces).

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

- **INV-3 (license-gated, real AST):** repro + all four branch shapes render
  exactly; no `Literal*Evaluation` (Component 4).
- **Helper branches (offline unit tests):** the five hand-traces pinned without a
  license (Component 5) so C2/C3 stay caught when the fixture test skips.
- **INV-2 (offline):** totality guard → zero `Literal*Evaluation` **and** the four
  enumerated paren-restorers present in regenerated snapshots (Component 6).
- **INV-1 (review gate):** byte-identity diff on executable fields during regen.
- **INV-4 / dispatch:** existing `test_ast_dispatch_invariant.py` REQ-AST-03
  suite stays green; new REQ-AST-08/-09 rows added.
- **Guard-count check (m3):** the plan asserts (not assumes) that `REQ-AST-04`'s
  exact dispatch-function counts (`test_ast_dispatch_invariant.py:252-276`) stay
  green after literals switch to `is_instance`, and that no `is_literal_expression`
  caller misbehaves when `LiteralInfinity`/`NullExpression` now return `True`.
- **License marker (m2):** factor `requires_license` / `_license_available` out of
  `test_snapshot_generation.py:35-47` into `tests/conftest.py` (or a shared
  helper) and import it from both tests — do not copy `_license_available`, which
  would run a second live `load_models()` probe per run.
- **Regression safety:** full `uv run pytest tests/` green pre-commit.

## Next-Stage Handoff

**Fixed:** precedence-aware (D1); `is_instance` dispatch (D2); `"null"` / `"*"`
renderings (D3); new source-only fixture (D4); REQ-AST-03 revised in place +
REQ-AST-08/-09 added (D5). The precedence table is pinned from KerML Table 6, and
the `needs_parens` polarity + unary-operand handling are pinned by the five
hand-traces (implement them exactly — those traces are the acceptance test for
the helper).

**Open (plan-time):** exact per-file occurrence counts (shift with prior regens);
final fixture directory name; whether the offline guard lives in a new test file
or an existing conformance module.

**De-risk first:** write the paren helper + the offline branch-coverage unit tests
(the five hand-traces) *before* touching snapshots — those unit tests are the
cheapest proof the helper is correct and run without a license, so they de-risk
C2/C3 immediately. The license-gated real-AST fixture test then proves dispatch +
parens end-to-end on `.function`-bearing nodes. Regen is mechanical once the code
is proven.

---

## Appendix A — Paren-Restorers, Read From Source Models (C1)

**Why this appendix was rewritten.** The first draft read the committed snapshot
strings and concluded "no baseline has a meaning-changing group." That inference
is unsound: those strings were produced by the no-paren reconstructor
(`expression_utils.py:96`), which *structurally erases* source groups — a source
`(a + b) * c` is already stored as `a + b * c`. So the buggy output cannot be a
census of source groups. The evidence must come from the `.sysml` **sources** (or
re-parsed ASTs), enumerated below. The exact set is confirmed at Tier-1 regen;
these are the verified floor.

**Groups the fix will restore (verified against source + committed snapshot):**

| Source | Expression (source form) | Group that reappears | Why |
|---|---|---|---|
| `attr_expr_probe/design.sysml:62` | `(r_inner + r_outer) / 2.0 - r_major` | `(r_inner + r_outer)` | `+` is the left child of `/`; looser → wrap |
| `attr_expr_probe/design.sysml:77-78` | `eta_thermal * (f_pump * eta_pump + f_subsystem) * (m_neutron * p_fusion)` | `(f_pump * eta_pump + f_subsystem)` and `(m_neutron * p_fusion)` | a `+` inside `*` (looser); and a `*` right-child of `*` (equal-prec, unfavored) |
| `expression_binding_probe/library.sysml:8` | `combined_input * (1.0 + tax_rate)` | `(1.0 + tax_rate)` | `+` right-child of `*`; looser → wrap |
| `catf_mfe_model/library/components/divertor.sysml:222` | `... * (surface_area_inner + surface_area_outer) * ...` (constraint) | `(surface_area_inner + surface_area_outer)` | `+` group inside a `*` chain; `reconstruct_expression` serves constraint text |

Committed snapshots currently store all of these *flattened* (the group gone),
which is the visible display defect. After the fix they render with the group
restored — that churn is the fix working (regen checklist item 2, M1).

**By contrast, most baseline expressions have no group** and stay flat under
precedence-aware rules — e.g. `attr_expr_probe`'s `eta_thermal * p_fusion +
eta_direct * p_input`, `p_fusion * 2.0 / 3.0`, and `solar_battery_model`'s
additive chains (`racking.capital_cost + electrical_panel.capital_cost + ...`).
Under **always-paren** all ~30+ of these would gain redundant nesting, which is
why D1 rejects it.

**Repro (new fixture) — the equal-precedence shape the corpus lacks:**
`capacity * rate + capacity * (rate / 2.0) * 3.0` — `(rate / 2.0)` is the right
child of a `*` at equal precedence, left-associative → parens required.

---

**Next Step:** After approval → `/_my_plan`.
