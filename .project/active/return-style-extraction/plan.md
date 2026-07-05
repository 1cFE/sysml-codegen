# Implementation Plan: Return-Style & Bare-Parameter Extraction (SC-2)

**Status:** Draft
**Created:** 2026-07-05
**Last Updated:** 2026-07-05
**Epic Item:** UPSTREAM-FINDINGS Item 3
**Complexity:** MEDIUM (1-day)

## Source Documents
- **Spec:** `.project/active/return-style-extraction/spec.md`
- **Design:** `.project/active/return-style-extraction/design.md` ← component details, bets, invariants, exact wording. This plan does not repeat them; it links.
- **Design review:** `.project/active/return-style-extraction/design-review.md` (resolutions applied in the design)
- **Epic:** `.project/backlog/epic_upstream_findings.md` (Item 3; R1 docs-lockstep, R2 agentic-mbse impact, R3 license window)

## Implementation Strategy

**The fix is small and already proven on paper** (`design.md#research-findings`): one member-filter predicate, applied at two sites, plus a V8 pre-scan and a V7 reword. Everything downstream of the filter already works. The plan's real job is to *de-risk the one unprobed shape* and *prove nothing else moved*.

**Phasing Rationale:**
- **Phase 0 first** because V8's detection rule rests on an unprobed node shape (Bet **B4**, `design.md#key-bets`). Probing the anonymous return live is the cheapest insurance and it *selects* V8's detection key before any V8 code is written. It also settles the two other live unknowns (style-D generation safety, named-return expression presence) that shape the fixture and confirm auto-impl.
- **Phase 1** makes the code change test-first: the predicate + V8 + the extractor-side V7 string, with live extractor tests. These run the live extractor against new fixtures — they need no committed snapshot, so they can be written and run before capture.
- **Phase 2** captures the `return_styles` snapshot and runs the license-free offline assertions on it, then proves I1 (byte-identical existing snapshots + 4 pipeline baselines).
- **Phase 3** closes the R1 docs lockstep and the R2 agentic-mbse A-2 stencil fix, plus the deferred-work backlog note. Docs-only, license-free.

**License grouping (R3, live until 2026-08-06):** all license-gated work — the Phase 0 probes, the Phase 1 live extractor tests, the Phase 2 snapshot capture + baseline re-run — is front-loaded into Phases 0–2 so the licensed session is one continuous stretch. Phase 3 needs no license.

**Critical Path:**
Phase 0 probe (selects V8 key) → Phase 1 predicate + V8 + live tests → Phase 2 capture + baseline-invariance proof → Phase 3 docs + A-2. Phases are strictly ordered; Phase 3 is the only one that could run out of order (docs), but keep it last so REQ tags match the shipped code.

**First Proof Point:**
Phase 0, probe #1 — parse an anonymous `return : Real = expr;` live and read back its `.direction`, `.name`/`sanitize_name`, and result-parameter heritage. This single observation confirms or kills the design's V8 rule (`design.md#key-decisions` D2) before a line of V8 is written.

**Overall Validation Approach:**
- Each phase starts with tests (or, for Phase 0, with recorded probe observations).
- Suite must be **green at every phase boundary** — `uv run pytest tests/`.
- I1 byte-identical proof (`git diff` empty on all existing snapshots + 4 baselines) is the hard gate on Phase 2.

---

## Phase 0: De-Risk Probes (license-gated)

### Goal
Collapse the three live unknowns the research probe never covered, in the order the design's handoff prescribes (`design.md#next-stage-handoff`). Outcomes select V8's detection key and confirm the fixture shape. **No production code in this phase** — throwaway probe scripts only.

### Assumption Under Test
- **B4** (`design.md#key-bets`): an anonymous `return : Real = expr;` surfaces as a member with direction **Out** and an **empty** `sanitize_name`. This is the rule V8 keys off. If false → adopt the B4 fallback (key off result-parameter membership/heritage, e.g. `ReturnParameterMembership`) **before** writing V8.
- **B1**: `return y : Real = expr;` populates `feature_value_expression` on the ReferenceUsage (auto-impl falls out for free).
- **Risk 1** (`design.md#potential-risks`): style D (no-AST output) generates a stencil without breaking `build_pipeline_context` — decides whether style D keeps its design usage.

### Probe Stencil (Write This First)
```python
# throwaway probe — parse each snippet live, print the node shape. Not committed.
from sysml_codegen.extraction.extractor import SysMLDataExtractor  # + live adapter setup

# Probe 1 (B4 — GATES V8): anonymous return
#   calc def Anon { in x : Real; return : Real = x * 2; }
#   → for m in elem.owned_members: print(m.name, sanitize_name(m.name),
#         str(m.direction), <result-parameter heritage/membership>)
#   Record: is direction Out? is sanitize_name empty? is a name synthesized?

# Probe 1b (I3 mixed case): does `return : Real = e; out attribute y : Real = e2;`
#   even PARSE? Record legality — informs whether V8's unconditional raise can mask
#   a usable output (design I3 predicts SysML forbids it).

# Probe 2 (B1): named return  →  calc def Named { in x : Real; return y : Real = x*2; }
#   assert member for `y` has non-empty feature_value_expression.

# Probe 3 (Risk 1): style D  →  return attribute y : Real; ... y = x*2;  bound in a
#   design usage; run build_pipeline_context; confirm it produces a NotImplementedError
#   stencil and does NOT raise during codegen.
```

### Changes Required
**See `design.md` for:** B4 + fallback (`#key-bets`), D2 detection key (`#key-decisions`), Risk 1 mitigation (`#potential-risks`), the four-forms table (`#architecture`).

- [ ] Write a throwaway probe script (not committed) covering probes 1, 1b, 2, 3.
- [ ] **Record outcomes in this file's Implementation Notes → Phase 0** — the observed direction/name/heritage of the anonymous member is the input to Phase 1's V8 rule.

### Validation
**Automated:** none (exploratory probe).

**Manual:**
- [ ] Probe 1 prints the anonymous member's direction + sanitized name + heritage → **V8 key decided** (design rule or B4 fallback).
- [ ] Probe 1b prints whether the mixed anonymous+named form parses → I3 behavior confirmed.
- [ ] Probe 2 shows non-empty `feature_value_expression` on the named-return member.
- [ ] Probe 3 shows style D generates a stencil without a codegen crash → style D keeps its design usage (or, if it breaks, fall back to extraction-only for style D per `design.md#potential-risks`).

**What We Know Works After This Phase:**
V8's detection key is chosen against a real node, not an assumption. The fixture shape (does style D get a design usage?) is settled. Auto-impl presence for named return is confirmed live.

---

## Phase 1: Predicate + V8 + V7 (code, test-first; live tests license-gated)

### Goal
Land the actual fix: the shared `_is_parameter_member` predicate at both filter sites, the V8 pre-scan (using the Phase 0 key), and the extractor-side V7 reword. Prove it with live extractor tests against new fixtures.

### Assumption Under Test
The predicate admits direction-carrying `ReferenceUsage` and excludes direction-None refs, at **both** passes, with zero change to `AttributeUsage` handling (invariants I2, I4, I5; `design.md#required-invariants`). V8 fires before V7 on an anonymous return (I3).

### Test Stencil (Write This First)
```python
# tests/conformance/test_return_style_extraction.py  (NEW) — live extractor tests,
# skip without license via the existing _load_live_extractor fixture.

def test_named_return_autoimpls(live_extractor):           # I5, REQ-EXT-10
    cd = extract_calc_def(live_extractor, "return_styles", "<style-B def>")
    assert "y" in {a.name for a in cd.output_attributes}
    assert cd.output_expression_asts.get("y")              # non-empty AST → auto-impl

def test_bare_in_extracted(live_extractor):                # REQ-EXT-10
    cd = extract_calc_def(live_extractor, "return_styles", "<bare-in def>")
    assert "x" in {a.name for a in cd.input_attributes}

def test_body_assignment_no_double_ingestion(live_extractor):  # I2, REQ-EXT-12
    cd = extract_calc_def(live_extractor, "return_styles", "<style-D def>")
    assert [a.name for a in cd.output_attributes].count("y") == 1
    assert "y" not in cd.member_expressions               # no phantom member

def test_anonymous_return_raises_v8(live_extractor):       # I3, REQ-EXT-11
    with pytest.raises(ValueError, match="anonymous"):     # V8 text; NOT "zero output"
        extract_calc_def(live_extractor, "anonymous_return", "<anon def>")

def test_v7_reworded(live_extractor):                      # revised V7
    with pytest.raises(ValueError, match="zero output attributes") as e:
        extract_calc_def(live_extractor, "zero_output_calc", "<def>")
    assert "not yet extracted" not in str(e.value)
```

### Changes Required
**See `design.md` for:** predicate body (`#implementation-notes`), V8 wording + V8 placement (`#component-overview`, D2), exact V7 replacement strings (`#implementation-notes`), the four-forms table (`#architecture`).

#### 1. Fixtures (NEW — write before code)
- [ ] `tests/fixtures/return_styles/` — one `.sysml` with 4 calc defs (control `out attribute`, style B named inline `return`, bare `in`, style D `return attribute` + body assignment) **plus a design part with 4 calc usages** binding all inputs (bare `in x` bound as `in x = <literal>`). Style D keeps its usage unless Phase 0 probe 3 said otherwise. *Implementer confirms syside parses the style-D body syntax before proceeding (`design.md#potential-risks`).*
- [ ] `tests/fixtures/anonymous_return/` — one calc def with an anonymous `return`. Live-only, no snapshot (extraction raises); mirrors `zero_output_calc`.
- [ ] `tests/conformance/test_return_style_extraction.py` — implement the stencil above.

#### 2. Predicate + filter sites
**File:** `src/sysml_codegen/extraction/extractor.py`
- [ ] Add `_is_parameter_member(self, member) -> bool` (two-branch body from `design.md#implementation-notes`).
- [ ] Replace the gate at `:204` (`if not is_instance(member, "AttributeUsage"): continue`) with `if not self._is_parameter_member(member): continue`.
- [ ] Replace the identical gate at `:242` (second `member_expressions` pass) the same way (I4 — both passes MUST use the same predicate).

#### 3. V8 pre-scan
**File:** `src/sysml_codegen/extraction/extractor.py` (insert immediately before the REQ-EXT-08 / V7 guard at `:271`)
- [ ] Loop over `elem.owned_members`; on the first member matching the **Phase 0-selected key** (design default: direction Out + empty `sanitize_name`), raise `ValueError` with the V8 message (`design.md#implementation-notes`). Fires regardless of other named outputs (I3).

#### 4. V7 reword (extractor side only; doc side is Phase 3)
**File:** `src/sysml_codegen/extraction/extractor.py:272-278`
- [ ] Replace the current string (exact) with the revised V7 string quoted in `design.md#implementation-notes`. The doc-table V7 row (`modeling-assumptions.md:350`) is a **separate** edit deferred to Phase 3 — the two live strings differ.

### Validation
**Automated:**
- [ ] `uv run pytest tests/conformance/test_return_style_extraction.py` (license present) → all pass.
- [ ] `uv run pytest tests/` → green, no regressions.
- [ ] `uv run mypy src/` and `uv run ruff check src/` → pass.

**Manual:**
- [ ] Read the two changed filter sites — confirm both call `_is_parameter_member` verbatim (I4).

**What We Know Works After This Phase:**
Named `return` extracts + auto-impls, bare `in` lands as input, style D extracts `y` once with no phantom, anonymous `return` raises V8 before V7, and the V7 code string no longer says "not yet extracted." Existing suite still green.

---

## Phase 2: Snapshot Capture + Baseline Invariance (license-gated)

### Goal
Capture the committed `return_styles` snapshot through whatever surface is current, add the license-free offline assertions on it (including `compilation_results`, D4/M2), and prove I1 — all existing snapshots and the 4 pipeline baselines are byte-identical.

### Assumption Under Test
- **B3 / I1** (`design.md#required-invariants`): the relaxation adds zero members to existing models → snapshots and baselines unchanged. The byte-identical re-run is the *proof*; a diff is a real signal to investigate, not to re-baseline.
- **D4 / M2**: the committed snapshot's `compilation_results` block pins auto-impl — style B's def name is a key, style D's is absent.

### Test Stencil (Write This First)
```python
# offline snapshot assertions in test_return_style_extraction.py — license-FREE,
# run on the committed return_styles snapshot via load_extraction_snapshot.

def test_return_styles_io_offline():                       # REQ-EXT-10/12, I2
    snap = load_extraction_snapshot(snapshot_fixture("return_styles"))
    # each of the 4 defs has expected input_attributes / output_attributes names+counts
    # style D's `y` appears exactly once

def test_return_styles_compilation_results_offline():      # I5 offline, D4/M2
    snap = load_extraction_snapshot(snapshot_fixture("return_styles"))
    keys = snap["compilation_results"].keys()
    assert "<style-B def name>" in keys      # inline return compiled → auto-impl
    assert "<style-D def name>" not in keys  # EXPECTED degraded — see backlog note
    # assert on key presence/absence, NOT "snapshot carries no compilation data"
    # (that phrasing breaks under Item 2 — design.md#validation-approach)
```

### Changes Required
**See `design.md` for:** `compilation_results` threading + loader exposure (D4/M2, `#key-decisions`), the offline-vs-live split (`#validation-approach`), Item-2 sequencing note (`#potential-risks` Risk 4).

Item 2 has landed: `src/sysml_codegen/snapshot/` package, versioned format with `compilation_results`, and a `snapshot` CLI subcommand (`cmd_snapshot` → `capture_snapshot`, `cli/__init__.py:474`). Loader exposes `snapshot["compilation_results"]` (`loader.py:115`). Capture through this current surface — do not pin a format.

- [ ] Register `return_styles` in the capture surface — `scripts/capture_extraction_snapshots.py` `MODELS` map (`:41`; full-pipeline, so **not** `EXTRACTION_ONLY_MODELS`) — or the equivalent registration in the Item-2 `snapshot` package if capture has moved there.
- [ ] Capture the `return_styles` snapshot (license) and commit it under `tests/fixtures/return_styles/`.
- [ ] Add `return_styles` to `MODELS` in `tests/conformance/test_extraction_snapshots.py:42` so the standard REQ-SNAP-01..07 checks cover it.
- [ ] Add the two offline assertions above to `test_return_style_extraction.py`.

### Validation
**Automated:**
- [ ] `uv run pytest tests/conformance/test_return_style_extraction.py` → offline + live all pass.
- [ ] `uv run pytest tests/` → green.

**Manual — the I1 hard gate:**
- [ ] Re-run the full capture surface for **all existing** models + the 4 pipeline baselines (`scripts/capture_extraction_snapshots.py`, `scripts/capture_pipeline_baselines.py`).
- [ ] `git diff` on every existing `extraction_snapshot.json` and every `tests/fixtures/baseline_outputs/**` → **empty**. Only the new `return_styles` files are added. Any other diff → STOP and investigate (`design.md#validation-approach`).

**What We Know Works After This Phase:**
The four styles flow through backtracker → graph → generation without downstream break, auto-impl is pinned offline, and the change is proven to move nothing else (I1).

---

## Phase 3: Docs Lockstep + A-2 Stencil Fix (license-free)

### Goal
Close R1 (docs and code in lockstep) and R2 (agentic-mbse A-2 stencil fix), and file the deferred body-assignment-capture backlog note.

### Assumption Under Test
None — mechanical documentation and a cross-repo one-liner. The only live check is the A-2 stencil line range.

### Changes Required
**See `design.md` for:** the docs list (`#integration-strategy`), REQ numbering (D5), exact doc-side V7 replacement + V8 row (`#implementation-notes`), A-2 stencil content (`#implementation-notes`), deferred scope (`#non-goals`).

#### 1. sysml-codegen docs (R1)
- [ ] `docs/architecture/reference/01-extraction.md` — add REQ-EXT-10 / 11 / 12 rows to the Requirements table. The existing `return total_cost : Real = capacity * unit_cost;` canonical example (`:27-32`) is now true as documented — no example change, only rows.
- [ ] `docs/architecture/modeling-assumptions.md` — replace the V7 row at `:350` with the exact doc-side revised string (`design.md#implementation-notes`; backtick quoting, distinct from the code string edited in Phase 1); **add the V8 row**.
- [ ] `docs/architecture/verification-matrix.md` — add REQ-EXT-10 / 11 / 12 rows in the EXT section (after `:204`).
- [ ] Confirm the `@pytest.mark.req(id=...)` tags on the Phase 1/2 tests match REQ-EXT-10/11/12 so the matrix traces to real tests.

#### 2. Backlog note
- [ ] File the body-assignment-capture follow-up (wire `member_expressions[y]` → `output_expression_asts[y]`; M-lift, low priority) in the sysml-codegen backlog per `spec.md#agentic-mbse-impact`.

#### 3. A-2 stencil fix (R2 — cross-repo, needs filesystem access to `~/1cfe/agentic-mbse`)
- [ ] Open `~/1cfe/agentic-mbse` sysml-conventions skill `references/stencils.md`; **verify the live line range** (research cites ~39-41).
- [ ] Replace the expression-losing body-assignment stencil with the inline `return <result> : Real = <expr>;` form (`design.md#implementation-notes`). Do **not** teach `return attribute <result> : Real;` + a separate body assignment.

### Validation
**Automated:**
- [ ] `uv run pytest tests/` → green (docs changes don't affect tests, but confirm REQ tags resolve).

**Manual:**
- [ ] Grep `docs/` for the old "not yet extracted (Item 3)" phrasing → zero hits in both the code and the modeling-assumptions row.
- [ ] Confirm the A-2 stencil edit landed in the live `references/stencils.md` and no longer teaches the body-assignment form.
- [ ] Verification matrix REQ-EXT-10/11/12 rows each point at a real test id.

**What We Know Works After This Phase:**
Docs and code are in lockstep, the repo no longer teaches the SC-2-broken stencil, and deferred work is recorded — Item 3 is close-ready.

---

## Environment Setup

**See CLAUDE.md.** Key commands: `uv run pytest tests/`, `uv run mypy src/`, `uv run ruff check src/`. Capture + live tests require the syside license (live until 2026-08-06, R3). The A-2 fix requires filesystem access to `~/1cfe/agentic-mbse`.

## Risk Management

**See `design.md#potential-risks` for the full analysis.** Phase-specific mitigations:
- **Phase 0:** the whole phase *is* the mitigation for B4 (the one unprobed shape) and Risk 1 (style-D capture safety). Record outcomes before writing V8.
- **Phase 1:** style-D fixture syntax may not parse — confirm live before capturing; the expected extracted shape (output `y`, empty AST) is the assertion target regardless of exact body syntax.
- **Phase 2:** Item-2 format sequencing — capture through the current surface, don't pin a format (Risk 4). I1 diff is a STOP-and-investigate signal, never an auto-rebaseline.
- **Phase 3:** A-2 line range may have drifted — verify against the live file before editing.

## Implementation Notes

[TO BE FILLED DURING IMPLEMENTATION]

### Phase 0 Completion
**Completed:**
**Probe outcomes (V8 key decision):**
**Issues:**
**Deviations:**

### Phase 1 Completion
**Completed:**
**Actual Changes:**
**Issues:**
**Deviations:**

### Phase 2 Completion
**Completed:**
**I1 diff result:**
**Issues:**
**Deviations:**

### Phase 3 Completion
**Completed:**
**A-2 live line range:**
**Issues:**
**Deviations:**

---

**Status:** Draft → In Progress → Complete
</content>
</invoke>
