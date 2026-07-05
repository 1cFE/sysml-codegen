# Implementation Plan: Return-Style & Bare-Parameter Extraction (SC-2)

**Status:** Complete
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

- [x] Write a throwaway probe script (not committed) covering probes 1, 1b, 2, 3.
- [x] **Record outcomes in this file's Implementation Notes → Phase 0** — the observed direction/name/heritage of the anonymous member is the input to Phase 1's V8 rule.

### Validation
**Automated:** none (exploratory probe).

**Manual:**
- [x] Probe 1 prints the anonymous member's direction + sanitized name + heritage → **V8 key decided** (design rule or B4 fallback).
- [x] Probe 1b prints whether the mixed anonymous+named form parses → I3 behavior confirmed.
- [x] Probe 2 shows non-empty `feature_value_expression` on the named-return member.
- [x] Probe 3 shows style D generates a stencil without a codegen crash → style D keeps its design usage (or, if it breaks, fall back to extraction-only for style D per `design.md#potential-risks`).

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
- [x] `tests/fixtures/return_styles/` — one `.sysml` with 4 calc defs (control `out attribute`, style B named inline `return`, bare `in`, style D `return attribute` + body assignment) **plus a design part with 4 calc usages** binding all inputs (bare `in x` bound as `in x = <literal>`). Style D keeps its usage unless Phase 0 probe 3 said otherwise. *Implementer confirms syside parses the style-D body syntax before proceeding (`design.md#potential-risks`).*
- [x] `tests/fixtures/anonymous_return/` — one calc def with an anonymous `return`. Live-only, no snapshot (extraction raises); mirrors `zero_output_calc`.
- [x] `tests/conformance/test_return_style_extraction.py` — implement the stencil above.

#### 2. Predicate + filter sites
**File:** `src/sysml_codegen/extraction/extractor.py`
- [x] Add `_is_parameter_member(self, member) -> bool` (two-branch body from `design.md#implementation-notes`).
- [x] Replace the gate at `:204` (`if not is_instance(member, "AttributeUsage"): continue`) with `if not self._is_parameter_member(member): continue`.
- [x] Replace the identical gate at `:242` (second `member_expressions` pass) the same way (I4 — both passes MUST use the same predicate).

#### 3. V8 pre-scan
**File:** `src/sysml_codegen/extraction/extractor.py` (insert immediately before the REQ-EXT-08 / V7 guard at `:271`)
- [x] Loop over `elem.owned_members`; on the first member matching the **Phase 0-selected key** (design default: direction Out + empty `sanitize_name`), raise `ValueError` with the V8 message (`design.md#implementation-notes`). Fires regardless of other named outputs (I3).

#### 4. V7 reword (extractor side only; doc side is Phase 3)
**File:** `src/sysml_codegen/extraction/extractor.py:272-278`
- [x] Replace the current string (exact) with the revised V7 string quoted in `design.md#implementation-notes`. The doc-table V7 row (`modeling-assumptions.md:350`) is a **separate** edit deferred to Phase 3 — the two live strings differ.

### Validation
**Automated:**
- [x] `uv run pytest tests/conformance/test_return_style_extraction.py` (license present) → all pass.
- [x] `uv run pytest tests/` → green, no regressions.
- [x] `uv run mypy src/` and `uv run ruff check src/` → pass.

**Manual:**
- [x] Read the two changed filter sites — confirm both call `_is_parameter_member` verbatim (I4).

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

- [x] Register `return_styles` in the capture surface — `scripts/capture_extraction_snapshots.py` `MODELS` map (`:41`; full-pipeline, so **not** `EXTRACTION_ONLY_MODELS`) — or the equivalent registration in the Item-2 `snapshot` package if capture has moved there.
- [x] Capture the `return_styles` snapshot (license) and commit it under `tests/fixtures/return_styles/`.
- [x] Add `return_styles` to `MODELS` in `tests/conformance/test_extraction_snapshots.py:42` so the standard REQ-SNAP-01..07 checks cover it.
- [x] Add the two offline assertions above to `test_return_style_extraction.py`.

### Validation
**Automated:**
- [x] `uv run pytest tests/conformance/test_return_style_extraction.py` → offline + live all pass.
- [x] `uv run pytest tests/` → green.

**Manual — the I1 hard gate:**
- [x] Re-run the full capture surface for **all existing** models + the 4 pipeline baselines (`scripts/capture_extraction_snapshots.py`, `scripts/capture_pipeline_baselines.py`).
- [x] `git diff` on every existing `extraction_snapshot.json` and every `tests/fixtures/baseline_outputs/**` → **empty**. Only the new `return_styles` files are added. Any other diff → STOP and investigate (`design.md#validation-approach`).

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
- [x] `docs/architecture/reference/01-extraction.md` — add REQ-EXT-10 / 11 / 12 rows to the Requirements table. The existing `return total_cost : Real = capacity * unit_cost;` canonical example (`:27-32`) is now true as documented — no example change, only rows.
- [x] `docs/architecture/modeling-assumptions.md` — replace the V7 row at `:350` with the exact doc-side revised string (`design.md#implementation-notes`; backtick quoting, distinct from the code string edited in Phase 1); **add the V8 row**.
- [x] `docs/architecture/verification-matrix.md` — add REQ-EXT-10 / 11 / 12 rows in the EXT section (after `:204`).
- [x] Confirm the `@pytest.mark.req(id=...)` tags on the Phase 1/2 tests match REQ-EXT-10/11/12 so the matrix traces to real tests.

#### 2. Backlog note
- [x] File the body-assignment-capture follow-up (wire `member_expressions[y]` → `output_expression_asts[y]`; M-lift, low priority) in the sysml-codegen backlog per `spec.md#agentic-mbse-impact`.

#### 3. A-2 stencil fix (R2 — cross-repo, needs filesystem access to `~/1cfe/agentic-mbse`)
- [x] Open `~/1cfe/agentic-mbse` sysml-conventions skill `references/stencils.md`; **verify the live line range** (research cites ~39-41).
- [x] Replace the expression-losing body-assignment stencil with the inline `return <result> : Real = <expr>;` form (`design.md#implementation-notes`). Do **not** teach `return attribute <result> : Real;` + a separate body assignment.

### Validation
**Automated:**
- [x] `uv run pytest tests/` → green (docs changes don't affect tests, but confirm REQ tags resolve).

**Manual:**
- [x] Grep `docs/` for the old "not yet extracted (Item 3)" phrasing → zero hits in both the code and the modeling-assumptions row.
- [x] Confirm the A-2 stencil edit landed in the live `references/stencils.md` and no longer teaches the body-assignment form.
- [x] Verification matrix REQ-EXT-10/11/12 rows each point at a real test id.

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
**Completed:** 2026-07-05

**Probe scripts:** `.project/active/return-style-extraction/probe/` (probe.py, probe2.py,
probe3.py + model fixtures — throwaway, not committed to production; run under the
license env).

**Probe outcomes (V8 key decision):**

- **Probe 1 (B4 — GATES V8): design's PRIMARY rule REFUTED; fallback refined and
  probe-evidenced.** An anonymous `return : Real = expr;` surfaces as a
  `ReferenceUsage` with direction **Out** but its name is **NOT empty** — syside
  synthesizes `name='result'` (inherited from the redefined base
  `Calculation::result`). So the design's "direction-Out + empty `sanitize_name`"
  rule never fires, and worse, the relaxed predicate would ADMIT this member as a
  garbage output named `result`. The distinguishing property is **`declared_name`**:
  `None` for the anonymous return, `'y'` for a named `return y`. The anonymous
  result's `owning_membership` is `ReturnParameterMembership`.
  - **V8 DETECTION KEY (adopted):** a raw owned member whose `owning_membership`
    type is `ReturnParameterMembership` **and** whose `declared_name` is empty after
    `sanitize_name`. This is the design's named B4 fallback ("key off result-parameter
    membership/heritage — `ReturnParameterMembership`"), refined by the probe:
    membership *alone* is too broad (a named `return y` shares it), so it is combined
    with the empty-`declared_name` anonymity signal the probe surfaced.
- **Probe 1d (I1-CRITICAL, probe3.py): V8 is baseline-safe.** A plain `out attribute`
  calc def (no `return` clause — the shape EVERY existing fixture uses) carries **no**
  owned `ReturnParameterMembership` member; both `x` and `y` are `FeatureMembership`.
  So V8's scan is negative on all existing fixtures → byte-identity (I1) protected.
  `out attribute` is NOT modeled as the calc's return parameter.
- **Probe 1b (I3): mixed anonymous + named `out attribute` PARSES.** `return : Real =
  e; out attribute z : Real = e2;` loads fine and produces both a `result`
  (ReturnParameterMembership, `declared_name=None`) and `z` (FeatureMembership, Out).
  V8's key catches the anonymous `result` regardless of the sibling `z` output —
  satisfies I3 (V8 fires whenever an anonymous member is present, not masked by other
  outputs). NOTE: with the relaxed predicate the anonymous `result` is admitted as an
  output (name non-empty), so `output_attributes` is non-empty and V7 would NOT fire —
  V8 is the ONLY guard catching the anonymous form. This strengthens (not just
  reorders) the case for V8.
- **Probe 2 (B1/I5): CONFIRMED.** Named `return y : Real = x*2;` carries a non-empty
  `feature_value_expression` on the ReferenceUsage → auto-impl falls out for free once
  the filter admits it.
- **Probe 3 (Risk 1 / style D): CONFIRMED SAFE — style D keeps its design usage.**
  `return attribute y : Real; y = x*2;` extracts as: an `AttributeUsage(Out)` `y`
  (owning_membership `ReturnParameterMembership`, `declared_name='y'`, no fve) PLUS a
  direction-**None** `ReferenceUsage` `y` (fve=YES, the body assignment).
  `build_pipeline_context` runs with **no crash**; `output_attributes=['y']` (single,
  no double-ingestion), `output_expression_asts` empty (degraded/no auto-impl as
  designed), style D absent from `compilation_results`. V8 does not fire on it
  (`declared_name='y'` non-empty).

**Issues:** none — probes were decisive.

**Deviations:** V8 detection key changed from the design's stated primary rule
("direction-Out + empty `sanitize_name`") to the probe-evidenced B4 fallback
("`ReturnParameterMembership` owned member with empty `declared_name`"). This is the
fallback the design explicitly authorized for exactly this outcome (B4:
"if the probe shows syside synthesizes a name … V8 keys off … its result-parameter
membership or heritage (`ReturnParameterMembership`)"), tightened with the
`declared_name` signal so it does not also reject valid named returns.

### Phase 1 Completion
**Completed:** 2026-07-05

**Actual Changes:**
- `src/sysml_codegen/extraction/extractor.py`:
  - Added `_is_parameter_member(self, member) -> bool` (two-branch predicate:
    AttributeUsage → True; ReferenceUsage → True iff direction In/Out).
  - Replaced the `is_instance(member, "AttributeUsage")` gate at both member
    passes (primary + `member_expressions` second pass) with
    `self._is_parameter_member(member)` (I4 — both sites use the identical
    predicate).
  - Inserted the V8 pre-scan immediately before the V7 guard: scans raw
    `owned_members` for a `ReturnParameterMembership` whose `declared_name` is
    empty (the Phase-0 key), raises the name-the-result `ValueError`.
  - Reworded the V7 (REQ-EXT-08) zero-output message to the design's revised
    code string (no longer "not yet extracted (Item 3)").
- `tests/fixtures/return_styles/{library,design}.sysml` — 4 calc defs (ControlA
  style-A control; NamedReturnB style-B inline return; BareInC bare `in`; StyleD
  return-attribute + body assignment) + `rs_design` part binding every input.
- `tests/fixtures/anonymous_return/library.sysml` — `AnonReturn` calc def with an
  anonymous `return` (live-only, extraction raises → no snapshot).
- `tests/conformance/test_return_style_extraction.py` — live tests (REQ-EXT-10/11/12,
  V7 reword) + offline snapshot tests (pass after Phase 2 capture).

**Live-test result:** the 6 license-gated live tests all pass — named return
auto-impls (non-empty `output_expression_asts["y"]`), bare `in x` lands in
`input_attributes`, control style unchanged, style D extracts `y` once with no
phantom and no auto-impl, anonymous return raises V8 (not V7), V7 no longer says
"not yet extracted". The 4 offline snapshot tests fail pending Phase 2 capture
(expected — they read the not-yet-captured `return_styles` snapshot).

**Issues:** none.

**Deviations:** V8 key is the Phase-0 probe-evidenced form (ReturnParameterMembership
+ empty `declared_name`), not the design's stated "direction-Out + empty
sanitize_name" — see the Phase 0 deviation note.

### Phase 2 Completion
**Completed:** 2026-07-05

**Actual Changes:**
- Registered `return_styles` in `scripts/capture_extraction_snapshots.py` `MODELS`
  (full-pipeline).
- Captured `tests/fixtures/return_styles/extraction_snapshot.json` (committed).
  4 calc defs; `compilation_results` keys = ControlA, NamedReturnB, BareInC
  (auto-impl), StyleD **absent** (degraded) — pins D4/M2 offline.
- Added `return_styles` to `MODELS` in `tests/conformance/test_extraction_snapshots.py`
  (standard REQ-SNAP-01..07 now cover it).
- Offline assertions in `test_return_style_extraction.py` pass against the committed
  snapshot (I/O + compilation_results keys).
- Annotated `_is_parameter_member(self, member: Any)` to hold mypy at 109 (the new
  method would otherwise add one `no-untyped-def`).

**I1 diff result: PASS (in substance).** Re-ran the full extraction capture (all
existing models) + `capture_pipeline_baselines.py`. Every existing
`extraction_snapshot.json` differed **only** in the `captured_at` provenance
timestamp (Item-2 format field) — verified zero non-timestamp line changes across
all 10 modified snapshots; the 4 pipeline baselines (`baseline_outputs/`) were
byte-identical (no diff at all). The filter relaxation added zero members to
existing models. Restored the timestamp-only rewrites (`git checkout`) so the
commit adds only the new `return_styles` + `anonymous_return` fixtures and touches
no existing snapshot/baseline.

**Full gate:** `uv run pytest tests/` → 1857 passed, 4 skipped, 5 xfailed (+20 new:
11 in `test_return_style_extraction.py` + 9 from `return_styles` in the snapshot
round-trip parametrize). mypy 109, ruff 21 (== baseline).

**Issues:** the design's "byte-identical" I1 criterion predates Item 2's
`captured_at` field; a clean re-capture necessarily rewrites that one line. Resolved
by verifying the diff is timestamp-only and reverting it — the substantive content
is byte-identical, which is what I1 protects.

**Deviations:** none beyond the timestamp handling above.

### Phase 3 Completion
**Completed:** 2026-07-05

**Actual Changes:**
- `docs/architecture/reference/01-extraction.md` — added REQ-EXT-10/11/12 rows to the
  Requirements table (canonical `return total_cost` example unchanged — now true as
  documented).
- `docs/architecture/modeling-assumptions.md` — replaced the V7 row with the revised
  doc-side string (backtick quoting); added the V8 row.
- `docs/architecture/verification-matrix.md` — added REQ-EXT-10/11/12 rows (EXT
  section) pointing at `test_return_style_extraction.py`, all PASS.
- `.project/backlog/BACKLOG.md` — filed the body-assignment-capture follow-up (P3,
  M-lift) under Ideas / Future Considerations.
- **A-2 stencil fix (cross-repo, NOT committed here — report to orchestrator):**
  `~/1cfe/agentic-mbse/claude/skills/sysml-conventions/references/stencils.md`, Calc
  Definition stencil. Replaced the expression-losing body-assignment form
  (`return attribute result : Real;` + a separate `result = input_a * input_b;`,
  live lines 39-41) with the inline form
  `return result : Real = input_a * input_b;   // inline expression -> auto-implemented`.
  Minimal edit; the two input-attribute lines above are unchanged.

**A-2 live line range:** 39-41 (matched research's ~39-41 exactly).

**Validation:** stale "not yet extracted" phrasing → zero hits in `docs/` and `src/`;
REQ tags REQ-EXT-10/11/12 resolve to `test_return_style_extraction.py`; the A-2
stencil no longer teaches the body-assignment form. Full suite 1857 passed / 4
skipped / 5 xfailed; mypy 109, ruff 21 (== baseline).

**Issues:** none.

**Deviations:** none.

---

**Status:** Complete
</content>
</invoke>
