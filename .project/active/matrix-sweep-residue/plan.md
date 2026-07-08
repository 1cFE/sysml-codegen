# Implementation Plan: Matrix Sweep Residue (TRUTH-DEBT Item 5)

**Status:** Draft
**Created:** 2026-07-07
**Branch:** truth-debt-epic

## Source Documents
- **Spec:** `.project/active/matrix-sweep-residue/spec.md` — the disposition table (§A/B/C) IS the
  contract. This item skips design; do not re-derive judgments already made there.
- **Spec Review:** `.project/active/matrix-sweep-residue/spec-review.md` — Revise verdict, resolved
  in the spec's post-review revision (commit `1eaee41`). No open review items remain.
- **Epic:** `.project/backlog/epic_truth_debt.md` Item 5 (§Item 5, R1–R4).
- **D7 leash + stopping rule:** `.project/active/matrix-truth/design.md:286-296`.
- **Full row list:** `.project/backlog/BACKLOG.md:344-400` (`[ITEM7-MATRIX-SWEEP-RESIDUE]`).

## Implementation Strategy

**Phasing rationale.** Six phases, ordered cheap-and-mechanical → judgment-heavy → open-ended, so
each commit is independently reviewable and a stall in a later phase doesn't block the earlier
wins from landing:

1. High-value strengthen pair (named mutation tests — the spec's headline proof).
2. Remaining 15 strengthens (judgment work, byte-identity gate on 3 of them).
3. 11 reframes — one byte-safe text batch.
4. 5 citations — marker/traceability only.
5. The ~46-row sweep completion (open-ended by nature; the D7 leash bounds it).
6. Recount + gates, last.

Reframes (phase 3) and citations (phase 4) are ordered *after* the strengthens deliberately: they
are byte-safe and mechanical, so if phase 1/2 run long, phases 3–4 are still cheap to land in the
same session, and if phase 5's sweep produces its own reframe/cite findings they fold into the
same batch shape phases 3–4 already established.

**Every row, every phase, opens with R4 reproduction** (`epic_truth_debt.md` R4): re-read the
matrix row + cited test at current HEAD before touching anything. A row whose disposition doesn't
reproduce (text already matches the test, or the test already covers more than the spec's finding
claims) is reclassified in the plan's row log, not force-edited. This is expected to be rare — the
spec's own re-verification and review spot-checks already reproduced ~10 of the 33 rows — but
Items 3/4/6 are moving code concurrently on this branch, so re-check every row's line number and
citation against HEAD before editing.

**Critical path:** Phase 1 (mutation-proof the two named gates) → Phase 2 (judge + strengthen the
other 15) → Phase 6 (final recount). Phases 3/4/5 are independent of 1/2 and of each other; they
can run in any order once phase 1/2's fixture-touching work is known not to collide (checked at
phase 2 close, see below).

**First proof point:** REQ-EC-04's mutation test — delete the internal parse-and-raise gate at
`expression_compiler.py:217-223`, confirm the *new* test goes red, revert, confirm green. This is
the cheapest possible falsification of the spec's whole premise (that these gates are really
unpinned) and should run before any other strengthen, mechanical or not.

**Overall validation:** every phase's changes are verified with the narrowest scoped run first
(the specific test file/class touched), then the full suite once per phase before committing.
Ruff/mypy checked once per phase on the touched files, and again with `src/`-wide scope at
phase 6. No phase commits on a regressed gate.

---

## Phase 1: High-Value Strengthen Pair — REQ-EC-04 + REQ-AS-06 (mutation-proven)

### Goal
Land the two named headline strengthens with deliberate-mutation proof, establishing the mutation
pattern the rest of phase 2 follows.

### Assumption Under Test
That both gates are genuinely unpinned as the spec claims (R4 reproduction) — confirmed already by
spec-review L1-3, but re-verify live at implement since Items 3/4/6 may have touched neighboring
lines.

### R4 Reproduction (do first, before writing any new assertion)
- [x] Confirm `expression_compiler.py:217-223`'s internal `try/except` → `CompilationError` gate
  still exists at HEAD and is still unreachable from any test in
  `tests/conformance/test_expression_compiler.py` (`TestReqEc04AstParseValidation`).
- [x] Confirm `test_aggregation_scoping.py:479-513`'s `if result is not None: assert resolved_count
  > 0` shape still stands unchanged at HEAD.

### Test Stencil (write first)

**REQ-EC-04** — `tests/conformance/test_expression_compiler.py`:
```python
class TestReqEc04AstParseValidation:
    def test_internal_gate_raises_on_invalid_emitted_python(self):
        # Force the compiler to emit syntactically-invalid Python (e.g. via a
        # crafted expression tree the compiler's templater mishandles), and
        # assert CompilationError propagates from the internal parse-and-raise
        # gate — not from a caller-side ast.parse() call.
        with pytest.raises(CompilationError):
            compile_expression(<crafted-invalid-emit-fixture>)

    # MUTATION SPOT-CHECK (not committed as a test; run once, record result, revert):
    # comment out the raise in expression_compiler.py:217-223 → this test goes RED.
```

**REQ-AS-06** — `tests/conformance/test_aggregation_scoping.py`:
```python
def test_every_registered_redefinition_alias_resolves():
    registered = <enumerate the full registered redefinition-alias set>
    for alias in registered:
        assert resolve(alias) is not None, f"{alias} did not resolve"
    # replaces/augments the resolved_count > 0 floor at :479-513

    # MUTATION SPOT-CHECK: make one alias in the fixture unresolvable
    # (e.g. break its target reference) → this test goes RED; the old
    # `resolved_count > 0` assertion would still pass.
```

### Changes Required

**File:** `tests/conformance/test_expression_compiler.py` (~217-223 region's test class)
- [x] Add a fixture/case that forces invalid *emitted* Python through the compiler's own code
  path (not a caller-side `ast.parse()` on the return value).
- [x] Assert `CompilationError` (or the gate's actual exception type — confirm at
  `expression_compiler.py:217-223`) is raised by the internal gate.
- [x] Mutation spot-check: comment out the gate's `raise`, run the new test → confirm RED, revert,
  confirm GREEN.

**File:** `tests/conformance/test_aggregation_scoping.py` (~479-513 region)
- [x] Enumerate the full registered redefinition-alias set (independently — not derived from the
  resolver's own internal state beyond what's needed to enumerate registrations; R1 anti-vacuity).
- [x] Assert each one resolves; replace or augment the `if result is not None: resolved_count > 0`
  shape so a gap in the middle of the set can't hide behind the floor.
- [x] **Byte-identity gate (⚠BI, spec flag):** this touches the aggregation-scoping surface. Run
  the full baseline comparison (`test_baselines.py`, `test_graph_assembly.py::TestBaselineComparison`)
  before and after — expect **zero** baseline diff (the test change adds coverage, not production
  behavior). If any baseline moves, stop and diagnose before continuing — that would mean the new
  assertion exposed a real behavior gap, which is out of this item's scope (file it, per Non-Goals).
- [x] Mutation spot-check: make one aliased target unresolvable in the fixture (or monkeypatch the
  resolver to skip one), run the new test → confirm RED, revert, confirm GREEN.

### Validation
**Automated:**
- [x] `uv run pytest tests/conformance/test_expression_compiler.py tests/conformance/test_aggregation_scoping.py -v` → new tests pass.
- [x] Full suite → no regressions.
- [x] Byte-identity check on aggregation-scoping baselines → clean (per above).
- [x] `uv run ruff check src/`, `uv run mypy src/` → not worse than current gates.

**Manual:**
- [x] Both mutation spot-checks run, RED confirmed, reverted, GREEN confirmed. Record the exact
  mutation (line + change) in this plan's Implementation Notes for audit traceability.

**What We Know Works After This Phase:** The two headline gates are mutation-proven — the spec's
central success criterion is met independent of everything else in this item.

**Commit:** pathspec-limited to the two test files (+ any minimal fixture file if a new one is
needed for EC-04's invalid-emit case). Message: `test(item5): mutation-prove REQ-EC-04 + REQ-AS-06`.

---

## Phase 2: Remaining 15 Strengthens

### Goal
Judge and strengthen the rest of spec table A (17 total, minus the 2 done in phase 1 = 15), per
row, per the spec's per-row "Action (contract)" column.

### Assumption Under Test
That every row's judgment (STR, none flip to pure reframe per the spec's own note) still holds at
HEAD, and that the byte-identity-flagged rows (CA-07, CA-11, SR-05 — AS-06 already done in phase 1)
land without baseline churn.

### Rows (grouped by risk, not by table order — no-fixture rows first, fixture-touching last)

**No new fixture, no baseline risk (do first):**
- [ ] REQ-EPC-07 (`:211`) — deep-compare all 5 purity inputs against fresh copies.
- [ ] REQ-ORCH-05 (`:368`) — set-membership over count floor (`test_orchestrator.py`).
- [ ] REQ-ORCH-02 (`:365`) — observe the `binding_type` mutation, not just call order.
- [ ] REQ-ORCH-06 (`:369`) — STR + CITE: re-cite REQ-PIPE-07 **and** assert `ctx.computation_graph`
  identity in the ORCH-06 test body (spec's judgment: STR alone via re-cite would leave the row's
  own text unpinned).
- [ ] REQ-OR-02 (`:349`, `test_output_registry.py`) — add `not hasattr(registry, "resolve")`
  negative assertion + cover the 4th lookup (`scoped_alias_lookup`).
- [ ] REQ-OR-03 (`:350`, `test_output_registry.py`) — assert the `caplog` WARNING record is
  actually emitted for the first-wins alias collision (R1 fires-on-shape).
- [ ] REQ-PGD-03 (`:394`, `test_parameter_group_deriver.py`) — tighten `>=` to `==` distinct
  source-file count.
- [ ] REQ-REG-06 (`:453`, `test_gen_registry.py:539-579`) — de-circularize: derive the expected
  primitive-type set independently from the graph, not from `_collect_exit_point_primitive_types`
  (R1 anti-vacuity — the named offender).
- [ ] REQ-EPC-05 (`:209`) — add cross-group ParameterGroup uniqueness assertion.
- [ ] REQ-BASE-04 (`:110`, `test_baselines.py`) — glob all 10 baseline dirs instead of the
  4-model `MODELS` parametrize list (read-only widening; spec flags "no churn").
- [ ] REQ-DM-09 (`:169`, `test_data_models.py` + `test_graph_assembly.py`) — strengthen to pin
  INV-5 stable-sort + INV-3 channel-existence validation + serialization-non-exclusion (not just
  the 4 field names); **and** add the `# REQ-DM-09` / `@pytest.mark.req` marker so tooling binds
  it (one row, two defects — do not double-count against the citation phase, per spec's
  INFERRED note).
- [ ] REQ-PMM-02 (`:422`) — add the `ModuleOutput.default_value` field assertion.

**Byte-identity-flagged (⚠BI — new fixture or drives regen):**
- [ ] REQ-CA-07 (`:149`, `test_computed_attributes.py`) — add an `x = x + 1` self-referencing
  fixture; assert on `input_names` directly (not a downstream string). Byte-identity check on any
  conformance baseline touched by the new fixture.
- [ ] REQ-CA-11 (`:152`, `test_computed_attributes.py`) — add the unregistered shape-A case;
  assert the warning names the real cause (R1 fires-on-shape). Byte-identity check as above.
- [ ] REQ-SR-05 (`:508`) — drive the actual regen path (not isolated backup-mechanism test);
  assert backup-before-regen ordering. This one is expected to *invoke* `scripts/capture_*.py`
  machinery in the test — confirm it does not itself mutate committed baselines (use a temp
  output dir); if it must touch a real baseline path, land under the byte-identity gate as a
  reviewed capture diff (R3).

### R4 reproduction gate (before any edit in this phase)
- [ ] Re-check each row's cited test still has the exact shape the spec table describes (line
  numbers may have drifted from Items 3/4/6 landing concurrently on this branch). Log any drift in
  Implementation Notes; if a row's finding no longer reproduces, reclassify it (do not force-edit)
  and note why in the recount phase.

### Validation
**Automated:**
- [ ] Run each touched test file individually as it's edited.
- [ ] Full suite after all 15 land → no regressions, 0 new xfail.
- [ ] Byte-identity check specifically on: `test_computed_attributes.py` fixtures (CA-07, CA-11),
  any baseline SR-05's regen-drive touches. Expect clean; if not, stop and diagnose (R3) before
  committing — a real baseline move here is out of this item's scope.
- [ ] `ruff check src/`, `mypy src/` → not worse than current gates (tests dir isn't gated but
  keep it clean).

**Manual:**
- [ ] Mutation spot-check at least the two R1-flagged rows: REQ-REG-06 (break the independent
  derivation so it would trivially pass if still circular — confirm the new test relies on the
  graph, not the SUT helper) and one diagnostic row (OR-03 or CA-11: suppress the warning emission
  → confirm RED).

**What We Know Works After This Phase:** All 17 strengthens (2 from phase 1 + 15 here) are landed,
each pinning its row's full text, byte-identity holds except where explicitly reviewed.

**Commit:** pathspec-limited to the touched test files (+ any new fixture files for CA-07/CA-11 +
any regen-drive scaffolding for SR-05). Message: `test(item5): strengthen remaining 15 matrix rows`.
Consider splitting into two commits (no-fixture batch, then the 3 ⚠BI rows) if the byte-identity
diffs need isolated review — judgment call at implement, not mandated.

---

## Phase 3: The 11 Reframes — One Byte-Safe Text Batch

### Goal
Land all 11 reframes from spec table B as pure REQ-text edits to `docs/architecture/verification-matrix.md`. No code, no fixtures, no baseline touch.

### Assumption Under Test
That DM-03 and AS-02 (the two reframe-or-strengthen judgment calls) stay reframes — the spec's
default — unless the stronger assertion trivially falls out of an *existing* fixture with no new
fixture authored (spec's explicit rule: do not manufacture a fixture to upgrade these two).

### R4 Reproduction (do first)
- [ ] Re-verify all 11 rows' current matrix text against HEAD (line numbers may have shifted —
  the spec's line refs are `:142, :148, :92, :163, :164, :380, :509, :495, :424, :425, :76`).
- [ ] Re-confirm CA-01 specifically: per the spec's revision (post spec-review), the INV-F clause
  is still live at HEAD and the reframe is a real edit, not a no-op. One grep check:
  `grep -n "EXPOSE_CHAIN_TENTATIVE" docs/architecture/verification-matrix.md tests/conformance/test_computed_attributes.py` —
  confirm the row still asserts INV-F and the test still treats the value as a valid member.
- [ ] For DM-03 and AS-02: check whether an existing fixture already supports the stronger
  assertion (dual-match partdef for AS-02; type/optionality comparison for DM-03) without new
  authoring. If yes, note it — but default to reframe per spec's rule unless it's truly free.

### Changes Required
**File:** `docs/architecture/verification-matrix.md` — 11 row-text edits, one per spec table B row:
- [ ] REQ-CA-01 (`:142`) → "assign each attr exactly one enum member" (drop INV-F clause).
- [ ] REQ-CA-06 (`:148`) → scope to FORMULA/EXPOSE_ALIAS; note LITERAL is the design-attr/entry-point path.
- [ ] REQ-AST-03 (`:92`) → scope to the FCE<OE<FRE ordering clause.
- [ ] REQ-DM-03 (`:163`) → "field name lists" (unless free strengthen found above).
- [ ] REQ-DM-04 (`:164`) → "importable from documented source file."
- [ ] REQ-OSR-03 (`:380`) → template-fidelity scope (or add the output-registry PQN citation — spec
  leaves this open; default to the cheaper reframe unless the citation add is trivial).
- [ ] REQ-SR-06 (`:509`) → "all module types route through the single `_generate_stencils()`."
- [ ] REQ-SNAP-18 (`:495`) → regression-guard framing; per spec-review L4-1, use the corrected
  rationale ("no production render site under `src/sysml_codegen` still passes
  `generation_timestamp`; the carrying template `pydantic_schema.py.jinja2` is deleted") — not
  "the token exists nowhere in the repo" (it still appears in the test itself and `.project/` docs).
- [ ] REQ-PMM-04 (`:424`) → the testable property (valid non-empty Python), drop the
  byte-identity-vs-pre-migration-baseline claim.
- [ ] REQ-PMM-05 (`:425`) → importable-variants + unchanged-fields, drop the phased-sequence claim.
- [ ] REQ-AS-02 (`:76`) → scope to the observed precedence (unless a dual-match fixture already
  exists — else reframe).

### Validation
**Automated:**
- [ ] `git diff docs/architecture/verification-matrix.md` — confirm this commit touches *only* the
  11 rows' text (no accidental line drift elsewhere).
- [ ] Full suite → unaffected (doc-only change; suite should be a no-op run, but run it anyway to
  confirm no accidental co-edit).
- [ ] Byte-identity check on all baselines → must show **zero** diff (this phase is doc-only).

**Manual:**
- [ ] Spot-read all 11 edited rows once more against their cited tests post-edit — confirm INV-B
  (no PASS row pins less than its now-reframed text).

**What We Know Works After This Phase:** 11 rows no longer over-claim; baselines untouched.

**Commit:** pathspec-limited to `docs/architecture/verification-matrix.md`. Message:
`docs(item5): reframe 11 matrix rows to what their tests check`.

---

## Phase 4: The 5 Citation Fixes

### Goal
Land the 5 marker/traceability-only fixes from spec table C.

### Changes Required
- [ ] REQ-BASE-01 (`:107`) — re-cite / add `# REQ-BASE-01` marker to
  `test_graph_assembly.py::TestBaselineComparison` (currently marked REQ-GA-01; confirm dual-marking
  convention used elsewhere in the file, or add a second marker line per existing pattern).
- [ ] REQ-NC-08 (`:339`) — add `test_formula_quoted_owner.py` to the citation (FORMULA
  module_eqn/channel leg).
- [ ] REQ-VBR-10 (`:538`) — add `test_self_named_binding_trap.py::test_self_named_binding_resolves_to_own_param`
  to the citation.
- [ ] REQ-HR-08 (`:277`) — add a `# REQ-HR-08` marker at
  `test_virtual_binding_rewrite.py::TestChainOverrideFixtureCoverage` (currently marked REQ-VBR-04).
- [ ] REQ-PY-08 (`:440`) — add `@pytest.mark.req("REQ-PY-08")` (or the project's actual marker
  convention — check an existing marked test for the exact decorator/pattern) to the cited method
  in `test_gen_pipeline_yaml.py`; currently docstring-only.

### R4 Reproduction
- [ ] Confirm each "claim IS pinned by" test still exists and still pins the claim at HEAD (grep
  each cited test name).

### Validation
**Automated:**
- [ ] Full suite → unaffected (markers/citations don't change test behavior).
- [ ] If the project's matrix-tooling validates markers (check for a script/CI step that binds
  `# REQ-*` markers to matrix rows), run it and confirm the 5 rows now bind correctly.
- [ ] Byte-identity check → zero diff (no production code touched).

**Manual:**
- [ ] Confirm REQ-DM-09's docstring-only marker was fixed in phase 2 (its STR row), not
  re-touched here — avoid double-editing the same test file's marker in two phases.

**What We Know Works After This Phase:** All 5 citation gaps closed; matrix tooling (if any) binds
every row to its real pinning test.

**Commit:** pathspec-limited to the touched test files. Message:
`test(item5): fix 5 matrix row citations/markers`.

---

## Phase 5: The ~46-Row Sweep Completion (D7 leash)

### Goal
Produce the exact qualifying-residue list, deep-read it under the D7 stopping rule, land cheap
dispositions inline, and re-file only genuine budget-exceeding strengthens with a **named count**.

### Step 5.0 — Produce the exact qualifying list (spec's mandated first sweep step)
- [ ] Run the D7 qualifier grep across all 256 matrix rows: text contains
  `SHALL|ALL|every|never|exactly` (case-sensitive on the strong words as written), OR the row
  asserts a diagnostic/warning fires, OR the row asserts a numeric/structural count.
- [ ] Subtract the ~167 rows the Item-7 register already swept (`.project/backlog/BACKLOG.md:344-400`
  names the register; if a discrete list file exists, diff against it — otherwise reconstruct from
  the "reframed already" + "filed here" rows named in that BACKLOG entry).
- [ ] Subtract the 33 rows already dispositioned in phases 1–4 of this plan.
- [ ] The remainder is the concrete residue set. Record its exact count in this plan's
  Implementation Notes (expected ~46; the spec's own anchor computation: EPC 8 + LVP 9 + GA 8 = 25
  known, + ~21 spread across other families — confirm both numbers match your grep output, or
  record the delta and why).

### Step 5.1 — Sweep under the leash
- [ ] Deep-read each qualifying row: cited test vs. row text, same method as phases 1–4 (R4:
  re-read doc intent, reproduce against the test, disposition).
- [ ] **Stopping rule** (`matrix-truth/design.md:294`): stop the deep-read when EITHER the
  qualifying list is exhausted OR 0 new findings occur in 40 consecutive rows after the first 60
  are examined. Log the row count actually read and the point (if any) the stopping rule triggered.
- [ ] Every row read gets one of: **adequate as-is** (no finding), **reframe** (byte-safe, fold
  into an addendum to phase 3's batch — a second small commit, since phase 3 already landed), **cite**
  (fold into an addendum to phase 4's batch), or **strengthen** (judge: land now if cheap/no-fixture,
  same as phase 2's no-fixture rows; re-file with a named count + matrix pointer if it needs a new
  fixture/production-adjacent assertion beyond this item's remaining budget).

### Step 5.2 — Land the cheap dispositions
- [ ] Reframes found: one more `docs/architecture/verification-matrix.md` text-only commit,
  same shape as phase 3.
- [ ] Citations found: one more test-marker commit, same shape as phase 4.
- [ ] Cheap strengthens found (no new fixture, mirrors phase 2's no-fixture rows): land in their
  own commit, same validation discipline as phase 2 (mutation spot-check at least one).

### Step 5.3 — Re-file the overflow
- [ ] For every row whose only faithful fix exceeds this item's remaining budget: file it in
  `.project/backlog/BACKLOG.md` as `[ITEM5-SWEEP-RESIDUE-OVERFLOW]` (or fold as a dated addendum to
  the existing `[ITEM7-MATRIX-SWEEP-RESIDUE]` entry — reader's call at implement, whichever reads
  as one continuous ledger rather than a duplicate), with:
  - The exact REQ id, matrix line, and disposition (same format as spec table A).
  - **A named count** in the entry's own heading (e.g. "N rows re-filed") — never "the remainder"
    or an unstated tail.
  - A one-line reason it exceeded budget (new fixture required / production behavior gap / etc).
- [ ] Cross-check: this re-file's count + phase-5's landed-count + the 33 already-dispositioned
  must reconcile against the exact residue-set count from step 5.0. No row silently dropped.

### Validation
**Automated:**
- [ ] Full suite after step 5.2's commits → no regressions.
- [ ] Byte-identity check on anything step 5.2 touched.
**Manual:**
- [ ] Read back the re-file entry (if any) — confirm it names an exact count, not an estimate,
  and points at the matrix rows by REQ id.

**What We Know Works After This Phase:** The sweep's *read* obligation is fully discharged — no
row is "not asserted swept." The fix obligation is honestly split between landed-now and
named-overflow.

**Commit:** one or more commits per step 5.2's disposition type (reframe / cite / strengthen),
pathspec-limited as in phases 2–4; plus one commit for the BACKLOG.md re-file entry if step 5.3
produces one. Messages: `docs(item5): sweep-residue reframes batch 2`,
`test(item5): sweep-residue citations/strengthens batch 2`,
`docs(item5): re-file N sweep-residue overflow rows`.

---

## Phase 6: Final Recount + Gates

### Goal
Recount the matrix from rows (not the summary block) and confirm the epic's gates haven't
regressed, closing the item.

### Steps
- [ ] Recompute row counts directly from the matrix: `grep -c "^| REQ-" verification-matrix.md`
  (total), and STATUS-column counts anchored on the status column specifically, not a loose
  substring match (memory `verification-matrix-drift-modes`: many rows mention other REQ ids or
  the word "UNTESTED" in prose — count the trailing `| PASS |` / `| UNTESTED |` / `| DEFERRED |`
  cell, not a whole-line grep).
- [ ] Confirm total = PASS + UNTESTED + DEFERRED, no discrepancy. Expected: 256 rows, 255 PASS + 1
  UNTESTED (REQ-PGD-06, unchanged — Non-Goals) + 0 DEFERRED, **unless** phase 5's sweep flipped any
  row's status (it shouldn't — sweep dispositions are text/citation/assertion changes on already-PASS
  rows, not status flips) or Item 6 (running in parallel) added rows. If the count differs from
  256/255/1, diagnose before closing — do not force it to match the spec's expected number.
- [ ] Update the matrix's summary/index/footer counts to match the row-by-row recount.
- [ ] Confirm no PASS row pins less than its text (INV-B) for the specific rows this item touched
  — spot-check by re-reading each of the 17+11+5+phase-5-landed rows' final text against its
  (possibly new) test one more time.
- [ ] Run the full suite fresh (Item 6 may have landed tests in parallel — take current numbers,
  don't assume the spec's 2094+/0 xfailed baseline still holds exactly).
- [ ] `uv run ruff check src/` → confirm ≤ 17 (current gate) or record the new number if it moved
  and why.
- [ ] `uv run mypy src/` → confirm ≤ 97 (current gate) or record the new number if it moved and why.
- [ ] Byte-identity check across all baselines one final time (full `scripts/capture_*.py --check`
  or equivalent diff-and-revert per R3) — expect clean given every phase already gated its own
  fixture-touching rows.

### Validation
**Automated:**
- [ ] Suite green, gate numbers recorded (fresh, not assumed).
- [ ] Recount script/grep output pasted into Implementation Notes below.

**Manual:**
- [ ] Read the final matrix summary block once — confirm it states the recounted numbers, not a
  stale carry-forward.

**What We Know Works After This Phase:** The item's whole charter (INV-B: no PASS row pins less
than its text) holds across all 256(+) rows that were in scope, and the ledger's row-by-row total
reconciles with its own summary — closing the debt PIPELINE-TRUTH Item 7 opened.

**Commit:** pathspec-limited to `docs/architecture/verification-matrix.md` (summary/footer counts
only, if they need updating — the row edits themselves already landed in earlier phases). Message:
`docs(item5): recount matrix from rows, close out sweep residue`.

---

## Risk Management

- **Concurrent branch motion (Items 3/4/6 landing in parallel).** Every phase opens with an R4
  re-read against current HEAD before editing — this is the main defense. If a row's line number
  or test shape has moved since the spec was written, re-locate it by REQ id (matrix rows are
  keyed by REQ id, not line number) before editing.
- **Byte-identity risk concentrated in 4 rows** (AS-06 phase 1; CA-07, CA-11, SR-05 phase 2). Each
  has its own gate check in its phase — do not batch all 4 into one un-reviewed capture diff.
- **Sweep phase (5) is open-ended by construction.** The D7 stopping rule is the hard bound — do
  not extend the read past it "just to be thorough." If the stopping rule triggers before the
  qualifying list is exhausted, the plan still requires it: log what's left unread as a *named*
  gap in the re-file entry (this is different from the "budget overflow" re-file — an unread
  residual and a read-but-too-big-to-fix residual are both named, separately, if both occur).
- **Double-editing the same file across phases.** REQ-DM-09 (phase 2) and REQ-PY-08/others (phase
  4) may touch the same test file's marker region if the sweep (phase 5) later finds another
  finding in the same file — check `git diff` scope per commit to avoid silently re-touching a
  file two phases already closed out.

## Environment Setup

See `CLAUDE.md` for install/test/lint commands. No new dependencies expected.

## Implementation Notes

_(TO BE FILLED DURING IMPLEMENTATION)_

### Phase 1 Completion
**Completed:** 2026-07-08. Commit `4039b47`.
**Changes Made:**
- `tests/conformance/test_expression_compiler.py`: added
  `TestReqEc04AstParseValidation.test_internal_gate_raises_on_invalid_emitted_python`. Constructs
  a `BINARY_OP` `ExpressionAST` with operator `"~~"` (absent from `PYTHON_OPERATOR_MAP`), which
  falls through to the raw-operator-string emission (`f" {ast.operator} "` at
  `expression_compiler.py:198`), producing `(a ~~ b)` — invalid Python. Calls `compile_expression`
  directly (no caller-side `ast.parse`), asserting `CompilationError` from the internal gate at
  `:217-223`.
- `tests/conformance/test_aggregation_scoping.py`: rewrote
  `TestReqAS06Phase2AliasResolution.test_phase_2_alias_resolution`. Replaced the
  `resolved_count > 0` floor with a loop over all 41 registered redefinition aliases (solar_battery
  fixture), collecting any that fail `alias_lookup` into `unresolved`, then
  `assert not unresolved`. Each resolved alias's `canonical_name` is still checked via
  `scoped_lookup` as before.

**Mutation spot-checks (both run live, not just described):**
- EC-04: commented out the `except SyntaxError` gate's `raise` in
  `expression_compiler.py:217-223` (kept `python_ast.parse` call, replaced the raise with `pass`)
  → new test FAILED (`DID NOT RAISE CompilationError`). Reverted from `/tmp` backup → PASSED.
- AS-06: patched the test loop so index 0's `alias_lookup` result is forced to `None` regardless
  of registry state → new test FAILED with `AssertionError: 1/41 registered redefinition aliases
  did not resolve: ['solar_battery_plant.solar_array.pv_module.capital_cost']`. Reverted from
  `/tmp` backup → PASSED. (Confirms 41 is the real registered count in this fixture, matching the
  spec's "40 of 41" framing.)

**Issues Encountered:** None — both gates reproduced exactly as the spec described (R4 confirmed
live, no drift from spec-review's original read).

**Validation:** `test_expression_compiler.py` + `test_aggregation_scoping.py` targeted runs green;
full suite 2108 passed / 4 skipped (was 2107/4 — +1 from the new EC-04 test; AS-06 replaced an
existing test in place); `test_baselines.py` + `test_graph_assembly.py` (byte-identity proxy)
55/55 green, no baseline file diff. `ruff check src/` 17 (unchanged), `mypy src/` 97 (unchanged).

### Phase 2 Completion
### Phase 3 Completion
### Phase 4 Completion
### Phase 5 Completion
(residue exact count from step 5.0, rows landed vs. re-filed, stopping-rule trigger point)
### Phase 6 Completion
(final recount numbers, fresh gate numbers)

---

**Status**: Draft → In Progress → Complete
