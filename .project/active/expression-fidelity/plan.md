# Implementation Plan: Expression Reconstruction Fidelity (SC-6)

**Status:** Draft
**Created:** 2026-07-05
**Last Updated:** 2026-07-05
**Epic:** UPSTREAM-FINDINGS — Item 6
**Complexity:** MEDIUM (0.5–1 day)
**Branch:** upstream-findings-epic

## Source Documents
- **Spec:** `.project/active/expression-fidelity/spec.md`
- **Design:** `.project/active/expression-fidelity/design.md` ← component details, the precedence table, the five hand-traces, the regen checklist, Appendix A
- **Design review (Approve):** `.project/active/expression-fidelity/design-review.md` ← C1–C3 history + the Component-5 stub residual (resolved below)
- **Epic R1/R3:** `.project/backlog/epic_upstream_findings.md`

---

## Implementation Strategy

**Phasing Rationale**

The work splits cleanly along a license boundary, and that boundary sets the order.
The code fix and everything that proves it *offline* (unit tests on the paren
helper, the literal-totality guard, docs) must all land first and independently,
because the live regen (Tier 1) needs a syside license that expires 2026-08-06 and
may be unavailable in the implement window. So:

- **Phase 1** lands the two code fixes plus the cheapest correctness proof — the
  five hand-traces as no-license unit tests. These pin the C2 polarity and C3
  unary bugs the review caught, and they run in any environment. If the helper is
  wrong, this phase catches it before anything expensive.
- **Phase 2** adds the license-gated real-AST test. It is the *only* thing that
  proves dispatch ordering on real `.function`-bearing nodes — the exact class of
  bug mocks masked. It comes after Phase 1 because the helper is already proven by
  then; Phase 2 proves dispatch + parens end-to-end.
- **Phase 3** is the regen. It is mechanical once the code is proven, but it is the
  HARD byte-identity gate — the checked backstop that the display fix did not
  perturb any executable field. It runs last among the code phases because it
  depends on the fix being final.
- **Phase 4** is docs, matrix, BACKLOG, PUSH-DOWN, agentic-mbse. No license, no
  code risk; last because REQ text should describe what actually shipped.

**Critical Path**

Fix `reconstruct_expression` (reorder) + `reconstruct_operator_expression`
(parens) → prove offline with the five hand-traces → prove on real AST (license) →
regen under the byte-identity gate → docs.

**First Proof Point**

The five hand-trace unit tests (Phase 1) pass against the real
`reconstruct_operator_expression`. That is the earliest signal the paren helper's
polarity (C2) and unary handling (C3) are correct, and it needs no license.

**Overall Validation Approach**
- Each phase starts with tests.
- The suite stays green at every phase boundary against the baseline below.
- The regen (Phase 3) is governed by the design's review checklist executed
  verbatim — byte-identity is a hard stop.

**Gate baseline (post-Item-5, current HEAD).** `uv run pytest tests/` →
**1880 passed / 4 skipped / 5 xfailed**. `ruff check src/` → **21**. `mypy src/` →
**109**. These are the numbers to hold or improve; a *drop* in passed or a *rise*
in ruff/mypy that this item introduces is a regression to investigate.

**Plan-time footprint reconciliation (READ — affects Phase 3).** The design's
Tier-1 list names **11** extraction snapshots. A grep at plan time shows **12**
`*/extraction_snapshot.json` files now carry `Literal*Evaluation`: the design's 11
(`alias_agg_probe`, `attr_expr_probe`, `catf_mfe_model`, `chain_override_probe`,
`expression_binding_probe`, `issue22_model`, `return_styles`, `retype_model`,
`sample_model`, `solar_battery_model`, `unresolvable_attr_probe`) **plus
`quoted_owner_formula`**, which Item 5's regen added *after* this design was
written. This is exactly the "counts shift with prior regens" caveat
(`design.md:492`, spec:255). It does **not** change the plan: the review rule
governs, not the count. Phase 3 confirms the exact changed set empirically and
treats `quoted_owner_formula`'s literal→value churn as a legitimate Item-6 change,
while rejecting any identifier-sanitization delta in that file (that is Item 5's,
already committed — regen must not perturb it). See Phase 3, step 0.

---

## Phase 1: Two fixes + offline hand-trace unit tests

### Goal
Land both code fixes in `expression_utils.py` and prove the paren helper correct
offline. First and riskiest: the `needs_parens` polarity (C2) and unary-operand
(C3) bugs are wrong-math, and this is the cheapest place to catch them. License-free,
suite stays green.

### Assumption Under Test
That the precedence-aware helper renders all five hand-traces exactly
(`design.md:334-340`) — i.e. the C2 polarity convention and C3 unary handling as
written in the design are implementable straight from the doc and produce correct
math. Also: that a name-fallback stub actually drives the helper's binary-op check
(the design-review residual, resolved below).

### Component-5 stub residual — RESOLVED (do this before writing the helper)
The design-review verification round left one plan-time confirmation
(`design-review.md:421-428`): do the offline stubs actually exercise the helper's
binary-op detection? Resolution, pinned here:

- Implement `binary_op_of(child)` to treat a child as a binary operator **iff**
  `SysideAdapter.is_instance(child, "OperatorExpression")` **and** it has exactly
  2 operands **and** its `.operator` is a key in `RANK`. The `RANK`-membership
  clause is load-bearing: it makes FCE (operator `"."`, an OE subtype) and
  invocations fall through to atomic — no `KeyError`, no accidental wrap — without
  a separate FCE guard.
- Because detection keys off `is_instance(child, "OperatorExpression")`, the
  offline stub must carry `"OperatorExpression"` in its **class name** so
  `SysideAdapter.is_instance`'s name fallback fires — the exact pattern
  `MockFeatureChainExpressionOperatorExpression` already uses
  (`test_ast_dispatch_invariant.py:112-125`). A stub named e.g.
  `StubOperatorExpression` with `.operator="+"` and two atomic operands must make
  `binary_op_of` return `"+"`.
- **Residual check as the first test (write it first):** assert that this stub
  drives `binary_op_of` to a non-None result. If it returns `None`, the stub is
  not exercising the check and the other four hand-traces would pass vacuously.
  This one assertion closes the residual.

### Test Stencil (Write This First)
```python
# tests/unit/test_expression_paren_helper.py  (NEW, no license)
from types import SimpleNamespace
from sysml_codegen.extraction.expression_utils import reconstruct_operator_expression

class StubOperatorExpression:              # name carries the type -> is_instance name fallback
    def __init__(self, operator, operands):
        self.operator = operator
        self.operands = operands

def atom(name):                            # atomic child: not an OperatorExpression by name
    return SimpleNamespace(referent=SimpleNamespace(name=name))  # renders as its name via FRE? -> see note

def test_residual_stub_drives_binary_op_check():
    # a * (b / c): parent '*', right child a 2-operand '/' OE stub -> must wrap
    child = StubOperatorExpression("/", [atom("b"), atom("c")])
    node  = StubOperatorExpression("*", [atom("a"), child])
    assert reconstruct_operator_expression(node) == "a * (b / c)"  # if this is "a * b / c", the stub isn't seen

# The five hand-traces (design.md:334-340) — each must render exactly:
#   a - (b - c)   -> "a - (b - c)"     equal-prec, left-assoc unfavored=right -> wrap
#   a / (b * c)   -> "a / (b * c)"     equal-prec, left-assoc unfavored=right -> wrap
#   -(a + b)      -> "-(a + b)"        unary(2) over binary(5), looser -> wrap
#   a ** (b ** c) -> "a ** b ** c"     right-assoc, natural nesting -> flat
#   (a ** b) ** c -> "(a ** b) ** c"   right-assoc, forced left nesting -> wrap
```

> **Atom-rendering note for the implementer:** the stub's *atomic* children must
> reconstruct to bare names. Pick whichever stub shape makes `reconstruct_expression`
> return the name cleanly (an FRE-named stub, or a plain `str`). The point of these
> tests is the *paren* logic, not dispatch — keep the atoms trivial so only the
> helper's precedence branches are under test.

### Changes Required

**See `design.md` for:**
- The reorder + `is_instance` conversion → `design.md#component-overview` (Component 1)
- The precedence table (RANK, associativity) → `design.md#the-precedence-table-d1`
- The `needs_parens` pseudocode + C2 polarity convention → `design.md:296-318`
- Unary-operand wrapping (C3) → `design.md:320-326`
- The five hand-traces (acceptance test for the helper) → `design.md:334-340`
- D3 renderings (`"null"`, `"*"`) → `design.md:146-155`

**Specific file changes:**

#### 1. Unit test file
**File:** `tests/unit/test_expression_paren_helper.py` (NEW — write first)
- [ ] Residual stub check (`binary_op_of` sees a name-fallback stub)
- [ ] The five hand-traces as five exact-string assertions
- [ ] `-(a + b)` and `not (a and b)` (C3 both operators)
- [ ] `(a + b) * c` and `a * (b + c)` (C2, looser child on each side)
- [ ] `- -a` stays flat (nested unary operand is atomic, `binary_op_of` → None)

#### 2. `reconstruct_expression` reorder + is_instance (Component 1)
**File:** `src/sysml_codegen/extraction/expression_utils.py:34-79`
- [ ] Move the five `Literal*`, `LiteralInfinity`, and `NullExpression` branches
      **above** the invocation catch-all (currently line 57), converting each
      `type(expr_node).__name__` check to `SysideAdapter.is_instance` (D2, HARD)
- [ ] Catch-all (`hasattr(expr_node, "function")`) becomes the last branch before
      `str(node)`
- [ ] Add `LiteralInfinity` → `"*"` (D3); keep `NullExpression` → `"null"` (already
      the string at `:76-77`, just relocated above the catch-all)
- [ ] Keep FCE/OE/FRE branches and their order untouched (INV-4, B1)

#### 3. `reconstruct_operator_expression` parens (Component 2)
**File:** `src/sysml_codegen/extraction/expression_utils.py:82-111`
- [ ] Add `RANK` dict from the precedence table (`design.md:275-285`); smaller =
      tighter (C2 convention — do **not** build a separate tightness number)
- [ ] Add `binary_op_of(child)` + `needs_parens(parent_op, child, side)` per the
      pseudocode (`design.md:311-317`), with the `RANK`-membership guard from the
      residual resolution above
- [ ] Binary branch (2 operands): wrap `left`/`right` when `needs_parens` says so
- [ ] Unary branch (1 operand): run `needs_parens(unary_op, operand, "operand")`
      and wrap when true (C3) — corrects the old `f"-{operand}"` / `f"not {operand}"`
- [ ] n-ary branch (>2 operands): left-fold — same-operator children never wrap; a
      looser-precedence child still does (`design.md:328-330`)

#### 4. `is_literal_expression` alignment (Component 3)
**File:** `src/sysml_codegen/extraction/expression_utils.py:168-180`
- [ ] Add one `is_instance` clause each for `LiteralInfinity` and `NullExpression`
      (HARD — keeps it consistent with the dispatch set)

### Validation (How to Verify This Phase)

**Automated:**
- [ ] `uv run pytest tests/unit/test_expression_paren_helper.py` → all pass
      (the residual check + five hand-traces + C2/C3 cases)
- [ ] `uv run pytest tests/` → **1880 passed** held (existing
      `reconstruct_expression` FCE/invocation tests at
      `tests/unit/test_hierarchy_resolver.py:271-368` stay green — untouched by the
      reorder, per `design.md#integration-strategy`)
- [ ] **Guard-count check (m3, assert not assume):** `REQ-AST-04` exact counts stay
      green (`test_ast_dispatch_invariant.py:252-276` — 5 dual-check / 8 multi-type)
      and `test_canonical_ordering_fce_oe_fre` stays green (it asserts only relative
      FCE<OE<FRE, `:220`; literal position is not checked). Also confirm no
      `is_literal_expression` caller misbehaves now that `LiteralInfinity` /
      `NullExpression` return `True`.
- [ ] `ruff check src/` → **≤ 21** (no new lint from the change)
- [ ] `mypy src/` → **≤ 109** (no new type errors)

**Manual:**
- [ ] Read the diff of `expression_utils.py`: the five literal/null branches sit
      above the catch-all, all via `is_instance`; the helper reads the RANK table
      directly with no inverted-tightness number.

**What We Know Works After This Phase:**
The paren helper is correct on all five hand-traces and both C2 sides and both C3
operators, offline. The literal branches are reachable. The suite is green. The
dispatch guards did not move. The only thing not yet proven is dispatch ordering on
real `.function`-bearing nodes — that is Phase 2.

---

## Phase 2: Live real-AST regression test

### Goal
Prove dispatch + parens end-to-end on a real parsed AST — the one thing mocks
cannot do, because mock nodes lack the derived `.function` that caused the bug
(spec HARD, `design.md#component-overview` Component 4).

### Assumption Under Test
That on real SysIDE nodes the reorder actually reaches the literal branches (no
`Literal*Evaluation` leaks) **and** the helper's parens survive a live AST for all
four branch shapes — not just the equal-precedence repro (M2 from the review).

### Test Stencil (Write This First)
```python
# tests/conformance/test_expression_reconstruction_fidelity.py  (NEW, license-gated)
from tests.conftest import requires_license          # factored out — see step 1

@requires_license
def test_repro_and_all_branch_shapes_render_exactly():
    graph = extract(REPO_ROOT / "tests/fixtures/expr_paren_probe")   # live parse
    got = calc_expressions_of(graph)                  # the reconstruct_expression output
    # INV-3 repro (equal-prec, assoc-unfavored):
    assert "capacity * rate + capacity * (rate / 2.0) * 3.0" in got
    # unequal-prec, each side (C2):
    assert "(a + b) * c" in got
    assert "a * (b + c)" in got
    # unary over binary (C3):
    assert "-(a + b)" in got
    assert "not (a and b)" in got
    # power right-associativity:
    assert "a ** b ** c" in got          # natural nesting flat
    assert "(a ** b) ** c" in got        # forced left nesting wrapped
    # literal totality on a live AST:
    assert "Evaluation()" not in "".join(got)
```

### Changes Required

**See `design.md` for:** the fixture's required branch coverage →
`design.md#component-overview` (Component 4); the license marker factoring →
`design.md#validation-approach` (m2).

**Specific file changes:**

#### 1. Factor the license marker (m2 — do first, shared by both tests)
**File:** `tests/conftest.py`
- [ ] Move `_license_available` + `requires_license` out of
      `test_snapshot_generation.py:35-47` into `conftest.py` (keep the
      `@functools.lru_cache` so it probes once per run), and import it from both
      `test_snapshot_generation.py` and the new test. **Do not copy**
      `_license_available` — a second copy runs a second live `load_models()` probe.

#### 2. New source-only fixture (D4)
**Directory:** `tests/fixtures/expr_paren_probe/` (NEW — source `.sysml` only, no
committed snapshot)
- [ ] A calc def whose output expressions cover **all four helper branches**
      (`design.md:240-249`): the equal-precedence repro
      `capacity * rate + capacity * (rate / 2.0) * 3.0`; an unequal-precedence gain
      on each side (`(a + b) * c`, `a * (b + c)`); a unary-over-binary case
      (`-(a + b)`, `not (a and b)`); and power right-associativity
      (`a ** b ** c` flat, `(a ** b) ** c` wrapped)
- [ ] No `extraction_snapshot.json` for this fixture — it is parsed live (a stored
      snapshot is text, not an AST; it cannot exercise the `.function`-bearing node)

#### 3. The regression test
**File:** `tests/conformance/test_expression_reconstruction_fidelity.py` (NEW)
- [ ] `@requires_license`; parse the fixture live; assert each reconstructed string
      exactly; assert no `Literal*Evaluation`

### Validation

**Automated:**
- [ ] With a live license: `uv run pytest tests/conformance/test_expression_reconstruction_fidelity.py`
      → passes (all four shapes + totality)
- [ ] Without a license: same test **skips** cleanly (marker works), and the
      Phase-1 offline unit tests still carry C2/C3 coverage
- [ ] `uv run pytest tests/` → still **1880 passed** (+1 passed or +1 skipped for
      the new test depending on license), no regressions
- [ ] Confirm `test_snapshot_generation.py` still imports the marker post-factoring
      and its two `@requires_license` tests (`:185`, `:209`) behave unchanged

**Manual:**
- [ ] Confirm the fixture actually parses (license present) — a syntax error in the
      fixture would skip-mask as "no license"; eyeball the parse or run the
      extractor once directly on the fixture dir.

**What We Know Works After This Phase:**
Dispatch ordering is correct on real nodes (no literal leaks), and the parens
survive a live AST for every branch shape. The code fix is fully proven. Regen is
now mechanical.

---

## Phase 3: Regen under the byte-identity gate

### Goal
Regenerate the affected baselines through the capture scripts and prove, via the
design's review checklist executed **verbatim**, that executable content is
byte-identical (INV-1) and that the four enumerated paren-restorers actually
appeared (M1). This is the HARD gate that converts "empirically safe" into "checked
safe."

### Assumption Under Test
That the display fix changes **only** display fields — `compiled_expression`,
`compilation_results`, `auto_impl_context`, `compilability`, pipeline YAML wiring,
and channel names stay byte-identical across all baselines (B2, INV-1). A single
executable-field diff falsifies it and is a hard stop.

### License dependency (READ FIRST)
Tier 1 needs a **live syside license** (expires 2026-08-06). If none is available
in the implement window: land Phases 1, 2, 4; **flag regen as blocked to the
orchestrator**; the item is **not done** until Tier 1/2 run. Never hand-edit
snapshots (R3, `design.md#license-window-fallback`).

### Test Stencil (the guard, write first — no license)
```python
# tests/conformance/test_literal_totality.py  (NEW, offline; INV-2 + M1)
def test_no_literal_evaluation_in_committed_baselines():
    for f in committed_snapshots_and_baselines():        # *.json under tests/fixtures + baseline_outputs
        assert "Evaluation()" not in f.read_text(), f        # INV-2: zero Literal*Evaluation

def test_enumerated_paren_restorers_present():
    # M1: the four Appendix-A groups must appear post-regen (a C2 bug would drop them)
    assert "(r_inner + r_outer)"            # attr_expr_probe/design.sysml:62
    assert "(f_pump * eta_pump + f_subsystem)"  # attr_expr_probe:77-78
    assert "(1.0 + tax_rate)"               # expression_binding_probe/library.sysml:8
    assert "(target_plates.surface_area_inner + target_plates.surface_area_outer)"  # catf_mfe divertor.sysml:222
```

### Procedure

**Step 0 — confirm the changed set (reconciles the 12-vs-11 footprint).**
- [ ] Grep committed extraction snapshots for `Literal*Evaluation`; confirm the set
      (plan-time: the design's 11 **plus** `quoted_owner_formula`). For each,
      decide: does its `expression_text` / `calc_expressions` actually change under
      the fix? If yes → Tier-1 target. If a snapshot restamps `captured_at` only
      with no content change → revert it (checklist item 4).

**Step 1 — Tier 1: extraction snapshots (live, license).**
- [ ] Run `scripts/capture_extraction_snapshots.py`
- [ ] Apply the review checklist (below) to each regenerated `extraction_snapshot.json`

**Step 2 — Tier 2: pipeline baselines (offline).**
- [ ] Run `scripts/capture_pipeline_baselines.py` — rebuilds the 3
      `baseline_outputs/{solar_battery,catf_mfe,attr_expr_probe}/computation_graph.json`
      from the committed snapshots
- [ ] Apply the review checklist to each

**The review checklist (`design.md:362-384`) — execute verbatim, per file:**
- [ ] **1. Byte-identity gate (INV-1, HARD).** Diff `compiled_expression`,
      `compilation_results`, `auto_impl_context`, `compilability`, YAML wiring,
      channel names. Any change → **hard stop**, investigate, report, no commit.
- [ ] **2. Expected display classes only, AND positively confirm each paren.**
      Accept `Literal*Evaluation()` → value, and the **four** enumerated
      paren-restorers (Appendix A: `attr_expr_probe` ×2, `expression_binding_probe`,
      `catf_mfe_model`) plus any others Tier-1 surfaces. **The reviewer must
      positively confirm each of the four appears** — a missing one is a hard stop,
      same as a surprise one (M1; a C2 polarity bug would silently drop exactly
      these).
- [ ] **3. Unexpected-class rule (HARD).** Any diff that is neither an expected
      display class nor executable → **hard stop**. If benign, add to expected
      classes with a note before committing; never wave through.
- [ ] **4. `captured_at` discipline (Item 3, HARD).** Commit only snapshots whose
      `expression_text` actually changed; revert timestamp-only rewrites.
- [ ] **5. One item's regen only (R3).** Do not fold in Item 5's
      `quoted_owner_formula` identifier-sanitization churn or any other item's
      baselines. `quoted_owner_formula`'s *literal→value* change is Item 6's and is
      kept; any *identifier* delta in it is Item 5's (already committed) and must
      not reappear — if the regen reintroduces one, hard stop.

### Validation

**Automated:**
- [ ] `tests/conformance/test_literal_totality.py` → both tests pass (INV-2 zero
      `Literal*Evaluation`; four paren-restorers present)
- [ ] `uv run pytest tests/` → green; snapshot/baseline conformance tests pass
      against the regenerated files
- [ ] `git diff` on executable fields shows **zero** change (the byte-identity gate,
      done as an explicit diff, not just test-green)

**Manual:**
- [ ] Positively confirm each of the four Appendix-A parens in the regenerated
      snapshots (checklist item 2)
- [ ] Confirm no timestamp-only snapshot is staged (checklist item 4)

**What We Know Works After This Phase:**
The display fix is live in the baselines, executable content is provably unchanged,
and the four real groups are restored. The offline totality guard now protects
INV-2 continuously.

---

## Phase 4: Docs, matrix, BACKLOG, PUSH-DOWN, agentic-mbse

### Goal
Make the reference doc describe what shipped: revise REQ-AST-03, add REQ-AST-08/-09,
note the aggregation-walker deviation, add matrix rows, file the latent bug, record
the PUSH-DOWN and agentic-mbse notes.

### Assumption Under Test
None (documentation). The only check is that existing conformance
(`test_canonical_ordering_fce_oe_fre`) stays green after the REQ-AST-03 text edit —
it asserts only FCE<OE<FRE, so it is unaffected.

### Changes Required

**See `design.md#doc-19--matrix-changes` for the exact wording of each item.**

- [ ] **Revise REQ-AST-03** (`docs/architecture/reference/19-ast-dispatch-invariant.md:36`
      and verification-matrix line 84): change "FCE, OE, FRE, Literal" to state that
      literal/null branches dispatch **before** the invocation catch-all, and
      FCE<OE<FRE holds among the reference/operator branches. Keep
      `test_canonical_ordering_fce_oe_fre` green.
- [ ] **Add REQ-AST-08** — `reconstruct_expression` SHALL dispatch all literal and
      `NullExpression` branches (via `is_instance`) before the invocation catch-all.
      *Verified by:* the license-gated real-AST test + offline totality guard.
- [ ] **Add REQ-AST-09** — `reconstruct_operator_expression` SHALL parenthesize a
      child operand (binary or unary) iff it binds looser than its parent, or equal
      and on the associativity-unfavored side (precedence-aware; C2 polarity; C3
      unary). *Verified by:* real-AST repro + branch fixture + offline hand-trace
      unit tests.
- [ ] **Known-deviation note (HARD)** in doc 19: `_walk_aggregation_ast`
      (`hierarchy_resolver.py:372,431`) keeps literal-after-invocation ordering and
      carries the latent literal-in-aggregation bug — a documented deviation from
      revised REQ-AST-03, not fixed here (executable path).
- [ ] **Matrix rows** in `docs/architecture/verification-matrix.md` (REQ-AST rows,
      near 82–88) for REQ-AST-08 and -09, pointing at their verifying tests.
- [ ] **BACKLOG entry** (`BACKLOG.md`): the latent aggregation-literal bug — a
      literal operand in an aggregation expression is mis-dispatched to the
      invocation catch-all (`hierarchy_resolver.py:372`), marked `has_unsupported`,
      its `reconstruct_expression` delegation (`:433`) dead. Fixing it touches an
      executable path; needs its own item.
- [ ] **PUSH-DOWN note** in the P1 PUSH-DOWN design: this fix travels with the
      `expression_utils.py` move; landing Item 6 first means the pushed-down
      `reconstruct_expression` is born correct and the baseline churn was reviewed
      once, here.
- [ ] **agentic-mbse impact: none** — record "none" for Item 12's accumulated list
      (R2). Internal display fix; no MODELING_GUIDE / sysml-conventions / validator
      change.

### Validation

**Automated:**
- [ ] `uv run pytest tests/conformance/test_ast_dispatch_invariant.py` → green
      (REQ-AST-03 text edit does not touch the relative-ordering assertion)
- [ ] Any matrix-consistency / REQ-tag conformance test (if present) → green with
      the new rows
- [ ] `uv run pytest tests/` → **1880+** passed, no regressions

**Manual:**
- [ ] Doc 19 reads correctly: REQ-AST-03 revised, -08/-09 added, deviation noted
- [ ] Matrix rows point at real, passing tests
- [ ] BACKLOG, PUSH-DOWN, agentic-mbse notes present

**What We Know Works After This Phase:**
The reference doc and matrix describe the shipped behavior; the latent aggregation
bug is filed, not lost; the PUSH-DOWN move inherits correct code.

---

## Environment Setup

**See CLAUDE.md.** Key commands: `uv run pytest tests/`, `uv run mypy src/`,
`uv run ruff check src/`. Regen: `uv run python scripts/capture_extraction_snapshots.py`
(license) and `scripts/capture_pipeline_baselines.py` (offline).

---

## Risk Management

**See `design.md#potential-risks` for the full analysis.**

**Phase-specific mitigations:**
- **Phase 1** — the C2/C3 wrong-math risk is retired by the five hand-traces as the
  *first* tests written, before the helper. The residual stub check ensures the
  tests are not vacuous.
- **Phase 2** — license expiry: the offline unit tests (Phase 1) already carry
  C2/C3 coverage, so the item is provable even if Phase 2 skips. Fixture syntax
  error masquerading as "no license" is caught by the manual parse check.
- **Phase 3** — a future literal-bearing aggregation fixture would break INV-1; the
  byte-identity gate catches it as a hard stop, and the BACKLOG item removes the
  latent cause. License unavailable → regen blocks, flagged to orchestrator, never
  hand-edited.
- **Phase 4** — none beyond keeping the conformance suite green.

---

## Implementation Notes

[TO BE FILLED DURING IMPLEMENTATION — leave empty now]

### Phase 1 Completion
**Completed:**
**Actual Changes:**
**Issues:**
**Deviations:**

### Phase 2 Completion

### Phase 3 Completion

### Phase 4 Completion

---

**Status:** Draft → In Progress → Complete
