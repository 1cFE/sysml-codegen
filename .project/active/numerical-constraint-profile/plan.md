# Implementation Plan: Numerical Constraint Executable Profile

**Status:** Complete
**Created:** 2026-07-18
**Last Updated:** 2026-07-18

## Source Documents
- **Spec:** `.project/active/numerical-constraint-profile/spec.md`
- **Design:** `.project/active/numerical-constraint-profile/design.md` ← component details,
  decisions D1–D10, invariants I1–I6, consumer/fixture censuses
- **Reviews:** `spec-review.md`, `design-review.md` (all findings resolved; M2/M6 owner-ratified)

## Implementation Strategy

**Phasing Rationale:** agentic-mbse lands completely first (Phases 1–2) because codegen's
version pin (`src/sysml_codegen/analysis/constraint_lowering.py:720`) RuntimeErrors the moment
the shared editable install carries a new `PROFILE_SEMANTIC_VERSION` — Phase 3 re-pins codegen
immediately after, before any new codegen behavior. The profile edit and its v3 answer key are
one commit (golden-churn risk, `design.md#potential-risks`). Catalog/fixture churn (Phase 4) is
isolated from new-behavior fixtures (Phase 5) so the re-capture diff stays interpretable.

**Critical Path:** P1 profile v3 → P2 companion consumers + suite → P3 codegen re-pin →
P4 exclusion payload/catalog → P5 end-to-end families + final gates.

**First Proof Point:** Phase 1's v3 answer-key test green over all golden equality/inequality
rows plus the containment cases — proves D2/B1 before any consumer changes.

**Environment notes (see CLAUDE.md + memory):**
- agentic-mbse lives at `/home/reid/1cfe/agentic-mbse` (not `~/agentic-mbse`).
- syside license: `set -a; source /home/reid/1cfe/agentic-mbse/.env` before any live capture;
  needed only for Phase 5's two new fixture captures. agentic-mbse tests may need
  `UV_CACHE_DIR` workaround per its repo conventions.
- Never run `pytest -m ""` or the corpus test in agentic-mbse; default suites only.

---

## Phase 1: Profile v3 Core (agentic-mbse)

### Goal
Land the force axis, `Eligibility.NON_NUMERICAL`, D2 containment classification, `!=` operand
walk (D9), v3 version string, and updated `REASON_CODES` — with the v3 answer key in the same
commit so the suite never sits red across commits.

### Assumption Under Test
**B1/D2:** the landed operand facts give every golden row and every containment shape exactly
one coherent (outcome, force) — no case needs a fact the schema doesn't carry.

### Test Stencil (Write This First)
```python
# tests/test_sysml/test_executable_profile_v3.py
V3_EXPECTED = {  # keyed by frozen golden equality_cases[].name — golden.json is NEVER edited (D8)
    "boolean_equality": (Eligibility.NON_NUMERICAL, "warn_non_numerical_equality"),
    "integer_equality": (Eligibility.BLOCK, "block_integer_equality_unpreservable"),
    "quantity_same_unit": (Eligibility.BLOCK, "block_real_equality_requires_tolerance"),
    ...  # all 14 equality + 2 inequality rows
}
def test_v3_answer_key_over_frozen_golden_operand_facts(): ...
def test_containment_mixed_and_boolean_flag_errors(): ...      # (x > 0) and flag -> BLOCK
def test_containment_xor_of_comparisons_errors(): ...          # (x > 0) xor (y > 0) -> BLOCK
def test_containment_pure_boolean_xor_warns(): ...             # flag xor other -> NON_NUMERICAL
```

### Changes Required

**See `design.md` for:** D1/D2/D8/D9 mechanics, `design.md#implementation-notes` (force field,
`classify_equality` contract change, bare-Boolean split, single-walk containment),
`design.md#required-invariants` I1–I3.

**Specific file changes (all in `/home/reid/1cfe/agentic-mbse`):**

#### 1. Tests (first)
**File:** `tests/test_sysml/test_executable_profile_v3.py` (NEW) + edits to the existing
profile tests that assert v2 codes
- [x] v3 answer key over every frozen-golden operand-fact row (stencil above)
- [x] Containment/force: mixed `and`, `xor`/`implies` over comparisons vs Boolean terms,
      malformed numerical branch under a warn connective → BLOCK, bare-Boolean root warns
      only for `category == "boolean"`, `!=` bucketing mirrors `==`, default-deny unprovables
      (unresolved/unknown/chain operands in `==`) → BLOCK
- [x] Aggregation order: diagnostics in walk order; outcome folds error > warn > admit
- [x] Location fallback (D10): decision with `location=None` still classifies; kept test that
      every live-extracted assessed assertion carries a location
- [x] Import-hygiene test unchanged and still green

#### 2. Profile module
**File:** `src/agentic_mbse/sysml/executable_profile.py`
- [x] `EligibilityDiagnostic.force` field; `Eligibility.NON_NUMERICAL`
- [x] D2 containment in the existing walk (no second traversal); `xor`/`implies` recurse
      (`:565-569` today stop); `!=` walks operands (`:469-480` today unconditional)
- [x] `classify_equality` v3 contract (no `support_*`); integer-equality error code; warn
      codes; `REASON_CODES` updated; messages carry the fix (two-inequality band / float-path
      reason) — exact spellings chosen here, used verbatim by Phase 3's rendering test
- [x] `_evaluate_usage` force-folding; `PreflightResult.non_numerical`;
      `PROFILE_SEMANTIC_VERSION = "executable-profile/v3"`

### Validation
**Automated:**
- [x] `uv run pytest tests/test_sysml/ -q` → green (answer key + containment + hygiene)
- [x] `python -O` run of the same selection → green
**Manual:**
- [x] Confirm `git diff` touches no fixture under `tests/fixtures/constraint_fact_shapes/`

**What We Know Works After This Phase:** D2 is total and coherent over every certified operand
fact; the v3 vocabulary exists; nothing consumes it yet.

---

## Phase 2: Companion Consumers + Suite (agentic-mbse)

### Goal
L4/L6 speak the four-outcome vocabulary (D4); the full companion suite is green; the exact
companion commit for codegen's pin discipline exists.

### Assumption Under Test
**D4:** ERROR-severity issues already fail L6 (`level6_architecture.py:953`), so parity with
the codegen halt needs only the severity split — no new gating machinery.

### Test Stencil (Write This First)
```python
def test_l6_malformed_numerical_is_error_and_fails_level(): ...   # BLOCK -> ERROR, success False
def test_l6_non_numerical_is_warning_level_passes(): ...          # NON_NUMERICAL -> WARNING
def test_l4_executable_share_denominator_includes_non_numerical():
    # 0 admitted, 0 blocked, N non-numerical  ->  0% executable share, not vacuous 100%
```

### Changes Required
**See `design.md#key-decisions` D4 and `design.md#architecture`.**

- [x] `src/agentic_mbse/validation/level6_architecture.py:600-641`: severity by force/outcome;
      new/updated `ValidationCode` entries in `sysml/types.py` as needed
- [x] `src/agentic_mbse/validation/level4_constraints.py:64-76`: per-family counts +
      executable-share rate (admitted / (admitted + blocked + non_numerical))
- [x] Update existing L4/L6 tests asserting v2 counts/severities

### Validation
**Automated:**
- [x] Full agentic-mbse suite (`uv run pytest tests/ -q`) → green; count recorded
- [x] Touched-file ruff/format
**Manual:**
- [x] Commit; record the commit hash — this is the **exact companion commit** for D3(c)

**What We Know Works After This Phase:** the companion half is complete and self-consistent;
codegen can pin one hash.

---

## Phase 3: Codegen v3 Compatibility (smallest possible)

### Goal
Un-break codegen against the upgraded editable companion: re-pin, four-outcome handling at
both consumer sites, message-bearing halt rendering (M1/D5). No new fixtures, no catalog
changes.

### Assumption Under Test
**B2 (census, now executed):** no committed fixture changes family under v3 — the whole
existing codegen suite goes green with only pin/rendering/dispatch edits.

### Test Stencil (Write This First)
```python
# tests/conformance/test_constraint_lowering.py (extend)
def test_blocked_profile_halt_names_the_fix():
    # constraint_blocked_profile (value == 5.0): halt text includes the diagnostic message
    with pytest.raises(CodeGenerationError, match="two.inequalit"):  # exact v3 message from Phase 1
        build_from_fixture("constraint_blocked_profile")
```

### Changes Required
**See `design.md#key-decisions` D3/D5 and `design.md#research-findings` (consumer inventory).**

- [x] `src/sysml_codegen/analysis/constraint_lowering.py:720` → pin `"executable-profile/v3"`
- [x] `:726-742` halt rendering appends `diag.message`; halt filter untouched (BLOCK only)
- [x] `:748-776` non-ADMIT dispatch tolerates `NON_NUMERICAL` (behavioral no-op this phase —
      records stay `eligible=False` as today); `collect_bare_actual_demand` (`:405-440`)
      confirmed ADMIT-filter-safe (test, no code change expected)
- [x] Update any codegen tests pinning v2 reason codes/messages or the version string

### Validation
**Automated:**
- [x] Full sysml-codegen suite → green, zero fixture diffs (`git diff -- tests/fixtures` empty)
- [x] `python -O` on the constraint-focused selection
**Manual:**
- [x] Halt text for `constraint_blocked_profile` visually contains statement, location,
      construct, reason, and fix

**What We Know Works After This Phase:** the coordinated pair is re-synced; family stability
of the corpus is proven by the real suite, not just the census.

---

## Phase 4: Exclusion Payload + Catalog Projection + Re-capture (codegen)

### Goal
One tagged, validated exclusion payload on `ConcreteConstraint` (M5/D6); catalog
`excluded_records` projection; unsupported-owner route totalized; constraint-bearing baselines
re-captured.

### Assumption Under Test
**D6's churn containment:** the baseline re-capture diff shows excluded-records additions (and
the consequent fingerprint changes) and *nothing else*.

### Test Stencil (Write This First)
```python
# tests/unit/test_concrete_constraint_model.py (extend)
def test_eligible_record_with_exclusion_rejected(): ...        # eligible=True + exclusion -> ValidationError
def test_ineligible_record_without_exclusion_rejected(): ...   # eligible=False, no exclusion -> ValidationError
def test_catalog_projects_excluded_records_in_id_order(): ...  # kind, ordered reasons, location survive
def test_unsupported_owner_kind_gets_exclusion(): ...          # requirement_def owner -> kind="unsupported_owner"
```

### Changes Required
**See `design.md#key-decisions` D6, `design.md#required-invariants` I2, and
`design.md#implementation-notes` (aggregation, re-capture discipline).**

- [x] `src/sysml_codegen/resolution/models.py`: exclusion payload model; eligible⇔exclusion
      validator (extends existing validators at `:345`/`:424`; honors the remediation's
      `validate_assignment`); `ConstraintCatalog` excluded-record model
- [x] `src/sysml_codegen/analysis/constraint_lowering.py:748-776`: thread
      `{kind, reasons, location}` from the profile decision (and the owner-kind branch) onto
      every `eligible=False` record
- [x] `src/sysml_codegen/generation/constraint_catalog.py:60-129`: project payloads into
      `excluded_records`; fingerprint payload gains the key
- [x] Re-capture/regenerate constraint-bearing baselines (catf_mfe et al. — license-free from
      committed snapshots); verify byte-identity of all non-constraint baselines

### Validation
**Automated:**
- [x] Full suite green; `python -O` on model/catalog selections
- [x] Baseline diff review: selective regeneration was byte-clean for this phase because the
      catalog is deliberately excluded from persisted graph baselines; the only discovered
      baseline change belonged to the parent remediation and was booked there
**Manual:**
- [x] Inspect one catf_mfe excluded record: plain-usage constraint appears with
      `kind="unassessed_form"`, ordered reasons empty-or-form, location present

**What We Know Works After This Phase:** every non-executed usage is visible, validated, and
serialized (SC 5/SC 6); contradictory records are unrepresentable (I2).

---

## Phase 5: Non-Numerical End-to-End + Final Gates (codegen)

### Goal
The two new behavior families exist as fixtures and are proven end-to-end (SC 1/3/4/5, I5);
all combined gates run and the execution record closes with the exact companion commit.

### Assumption Under Test
**I5:** live and from-snapshot generation produce identical warning *values* and excluded-record
*values* — and the totality gate holds over the narrowed matrix (SC 1).

### Test Stencil (Write This First)
```python
# tests/conformance/test_constraint_non_numerical.py (NEW)
def test_non_numerical_fixture_generates_warns_and_catalogs(caplog):
    ctx = build_from_fixture("constraint_non_numerical")           # e.g. assert status == "on" + admitted sibling
    assert [w for w in caplog.records if "not numerical" in ...]   # one warning: identity + file:line + reasons
    rec = ctx.graph.constraint_catalog.excluded_records[0]
    assert rec.exclusion.kind == "non_numerical"
def test_non_numerical_live_snapshot_warning_and_record_parity(): ...
def test_malformed_numerical_fixture_halts_naming_fix(): ...       # mixed (x>0) and flag -> halt, message named
```

### Changes Required
**See `design.md#validation-approach` and `design.md#key-decisions` D5/D7.**

- [x] `constraint_lowering.py`: `logger.warning` per NON_NUMERICAL usage (one line: identity +
      location-or-`<no location>` + ordered reasons)
- [x] New fixtures + captures (live, licensed): `constraint_non_numerical` (non-numerical
      assert + one admitted numerical assert), `constraint_malformed_mixed` (source-only —
      halts, so no snapshot baseline; keep as model + halt test)
- [x] Totality gate: extend the parent remediation's differential test
      (`tests/conformance/test_constraint_lowering.py:303` area) to the v3 admitted matrix —
      ADMIT → compile → generated execution; assert `==`/`!=` never reach the compiler (I4)
- [x] Snapshot round-trip: excluded records + warnings byte-equal live vs snapshot

**Final combined gates:**
- [x] Full sysml-codegen suite (licensed if available; else record skips) + `python -O` focused
- [x] Companion suite at the exact Phase-2 commit; hash recorded below and in CURRENT_WORK
- [x] Touched-file ruff/format + targeted mypy (baseline-labeled), `git diff --check`,
      placeholder scan, fixture byte-identity for non-constraint corpus
- [x] `pyproject.toml` companion version floor reviewed; no version was cut, so no floor bump

### Validation
**What We Know Works After This Phase:** every spec success criterion has a passing anchor —
admitted matrix executes unchanged (SC 1/7), split equality outcomes (SC 3), source-specific
warnings both tools (SC 4), catalog visibility (SC 5), force distinguishability (SC 6), v3
boundary + exact-companion evidence (SC 8).

---

## Risk Management

**See `design.md#potential-risks`.** Phase-specific:
- **Phase 1:** golden churn — single commit; never edit `golden.json`.
- **Phase 3:** if any fixture unexpectedly changes family (B2 false), stop and record the
  disposition before adapting tests — never silently re-pin.
- **Phase 4:** re-capture only after the suite is green; diff must be excluded-records-only.
- **Phase 5:** new captures need the license env; run via capture scripts, not `-c` probes.

## Implementation Notes

### Phase 1 Completion
**Completed:** 2026-07-18

**Changes Made:**
- Added the v3 force axis, `NON_NUMERICAL` outcome, four-way preflight partition, and semantic
  version in `agentic_mbse.sysml.executable_profile`.
- Reworked the existing recursive walk to return numerical-claim containment without a second
  traversal. Mixed predicates promote every diagnostic to error force.
- Re-anchored the frozen operand facts through a separate v3 answer key and added containment,
  force-folding, walk-order, `!=`, bare-Boolean, and location-fallback tests.

**Validation:**
- `tests/test_sysml/`: 369 passed, 1 skipped in normal and optimized Python.
- Targeted Ruff check passed; the frozen `constraint_fact_shapes` fixture has no diff.

**Issues Encountered:**
- Repository-local cache directories are read-only in the managed workspace. Validation used
  task-specific cache directories under `/tmp`; behavior and test selection were unchanged.

**Deviations from Plan:**
- The v3 answer key was added to the existing golden-matrix test module, while the new
  `test_executable_profile_v3.py` holds the structural containment cases. This keeps the frozen
  fact loader in one place and preserves the planned independent v3 behavior coverage.
### Phase 2 Completion
**Completed:** 2026-07-18

**Changes Made:**
- Split L6 diagnostics into malformed-numerical errors and one warning per non-numerical
  statement. Existing L6 error aggregation now makes malformed numerical models fail the level.
- Replaced the L4 v2 metric family with admitted numerical, malformed numerical,
  non-numerical, and unassessed counts. Executable share now includes non-numerical assertions
  in its denominator.
- Updated validation codes and focused L4/L6 regression tests.

**Validation:**
- Full agentic-mbse suite: 1511 passed, 1 skipped, 33 deselected.
- Focused L4/L6 suite after formatting: 90 passed.
- Touched production/new-test Ruff passed. `tests/test_sysml_quality_checks.py` retains its
  pre-existing whole-file Ruff findings; only metric-key assertions changed there.

**Issues Encountered:**
- None in the behavior contract.

**Deviations from Plan:**
- None.

**Exact companion commit:** `05cde35` (`Update validation consumers for profile v3`).
### Phase 3 Completion
**Status:** Complete.

**Changes Made:**
- Re-pinned the shared lowering gate to `executable-profile/v3`.
- Added diagnostic messages to generation halts, including the two-inequality rewrite.
- Confirmed `NON_NUMERICAL` reaches the existing ineligible-record path without halting.
- Made the predicate compiler reject every `==`/`!=` defensively and updated the admitted
  totality matrix to the v3 numerical subset.

**Validation:**
- Focused Phase 3 suite: 67 passed, 13 license skips.
- Optimized focused suite: 66 passed, 5 skipped.
- Licensed blocked-profile message test passes; touched-file Ruff passes; fixture diff is empty.
- The licensed full suite initially failed in
  `test_inheritance_cross_check_instance_index_probe_oracle_unchanged`. R4 proved the invalid
  empty-design-attributes harness predated v3; after its parent-ledger correction, the suite
  passed 2433 tests with 23 skips and 8 deselections.

**Issues Encountered:**
- The licensed gate exposed a pre-existing parent-remediation regression-test defect. It was
  classified by R4 and cured in its own ledger before Phase 3 closed.

**Deviations from Plan:**
- None in the numerical-profile implementation.

**Parent-remediation cross-reference:** R4 reproduced the failure with Phase 3 removed and the
pre-v3 companion loaded, proving pre-existence. The parent D2 ledger records the corrected family
regression at commit `096c29f`; the licensed full suite then passed 2433 tests with 23 skips and 8
deselections. No numerical-profile behavior or B2 fixture-family claim changed.
### Phase 4 Completion
**Completed:** 2026-07-18

**Changes Made:**
- Added the validated `ConstraintExclusion` tagged payload and enforced the eligible/exclusion
  equivalence during construction and assignment.
- Totalized all three non-execution routes as `non_numerical`, `unassessed_form`, or
  `unsupported_owner`, preserving diagnostic reason order and explicit location fallback.
- Added sorted catalog `excluded_records` and included them in the catalog fingerprint input.
- Extended model, lowering, migration, catalog, and live/snapshot parity tests, including the
  `catf_mfe` constraint-bearing family.

**Validation:**
- Focused Phase 4 selections: 98 passed with the license enabled.
- Snapshot parity: 6 passed. Optimized selection: 76 passed, 10 skipped.
- Licensed full suite: 2437 passed, 23 skipped, 8 deselected.
- Selective regeneration of `catf_mfe`, `constraint_inline`, and
  `constraint_multi_instance` was byte-clean after the parent-remediation baseline correction.
- Touched-file Ruff passed after formatting.

**Issues Encountered:**
- Selective regeneration exposed a stale `constraint_inline` graph baseline from the parent D2
  inline-reference cure. That correction is recorded in the parent remediation at commit
  `aaa579e`; it is not numerical-profile churn.

**Deviations from Plan:**
- The design expected persisted catalog/fingerprint diffs. The current pipeline intentionally
  excludes the catalog from committed graph baselines, so Phase 4 produced no persisted fixture
  changes. Live and snapshot tests compare the complete catalog values directly instead.

### Phase 5 Completion
**Completed:** 2026-07-18

**Changes Made:**
- Added one codegen warning per `NON_NUMERICAL` usage at shared lowering. The line carries
  statement identity, full location or `<no location>`, and reason codes in profile walk order.
- Added the licensed `constraint_non_numerical` fixture and committed extraction snapshot. Its
  string equality warns and becomes an excluded catalog record while its numerical sibling
  remains eligible.
- Added the source-only `constraint_malformed_mixed` family. Its numerical comparison plus bare
  Boolean branch halts generation and renders the profile's corrective message.
- Extended the v3 totality boundary: admitted numerical cases compile and execute, while every
  tested `==`/`!=` category is non-admitted and the compiler rejects it defensively.
- Added exact live/offline warning, graph, and complete catalog parity for the new family.

**Validation:**
- Phase 5 focused suite: 83 passed. Optimized combined Phase 4/5 selection: 125 passed.
- Licensed full sysml-codegen suite: 2450 passed, 26 skipped, 8 deselected.
- Exact companion archive at commit `05cde35`: 1491 passed, 1 skipped, 5 deselected. The archive
  used the established companion environment with its source path pinned to that commit.
- Targeted mypy passed on all four changed production files. Touched-file Ruff and formatting,
  `git diff --check`, and the changed-production placeholder scan passed.
- Non-constraint fixtures are unchanged by this item. The pre-existing dirty
  `sample_model/extraction_snapshot.json` remains untouched.

**Issues Encountered:**
- The companion branch advanced to unrelated workflow commit `4ed2a07` after Phase 2. Final
  evidence therefore ran from an isolated archive of the recorded exact commit instead of moving
  or resetting the shared working tree.

**Deviations from Plan:**
- No agentic-mbse release version was cut, so `pyproject.toml` retains its existing version floor.
  Exact compatibility is evidenced by the v3 runtime gate, commit `05cde35`, and its archive suite.

---

**Status**: Complete
