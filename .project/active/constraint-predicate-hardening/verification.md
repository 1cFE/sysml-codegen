# Verification: Predicate Defect Hardening (CONSTRAINT-SEMANTICS Item 4)

**Date:** 2026-08-13
**Codegen:** `item7-rebuild`, `3ca94af` → **`3459127`**
**Companion:** `/home/reid/1cfe/agentic-mbse-item7-rebuild`, `item7-rebuild`, `bc69f04` → **`0a52942`**
**TEAx:** untouched, `/home/reid/1cfe/teax` still on `constraint-semantics-item3`, working tree clean.

Every count below is read off a captured run, not remembered. Commands are given so each is
re-runnable.

---

## Commands and exact counts

### Full licensed codegen suite

```
set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a
/home/reid/1cfe/item7-rebuild-venv/bin/python -m pytest 2>&1 | tee /tmp/item4-codegen.log
grep -ci "license" /tmp/item4-codegen.log
```

**2010 passed · 0 failed · 34 skipped · 79 deselected · 0 xfailed · 0 xpassed.**

`grep -ci license` returns **1**, and that one line is a *test name*, not a skip:
`test_exact_route_snapshot_generation.py::test_generation_from_a_v6_snapshot_needs_no_license
PASSED`. Confirmed independently with `pytest -q -rs`: all **34** skips are content-shape skips
from `test_calc_compat_parity.py:63` ("no calc output expressions in the golden") and
`test_computed_attribute_golden.py:48` ("no computed attributes in the golden"). **Zero
license-skip lines. This is a full run.**

Baseline for comparison: the same suite at `3ca94af` **did not run at all** — see "Pre-existing
breakage" below.

### Full companion suite (default selection — never `-m ""`)

```
cd /home/reid/1cfe/agentic-mbse-item7-rebuild
set -a; source /home/reid/1cfe/agentic-mbse/.env; set +a
/home/reid/1cfe/item7-rebuild-venv/bin/python -m pytest -q
```

**1821 passed · 10 failed · 1 skipped · 5 deselected.**

The 10 failures are **pre-existing and unrelated**, verified by `git stash`-ing the Item 4 change
and re-running the same four files at `bc69f04`: **10 failed, 176 passed** — the identical set.
They are `test_cli.py` console-script lookups (`FileNotFoundError`, the prescribed interpreter is
the codegen venv and does not expose the companion's console script), two `test_index.py` script
runs, one quality-check CLI exit-code test, and two validation baseline comparisons. None touches
the executable profile. **The gate is zero-new, and it holds.**

### Lint

| Gate | Baseline | Measured | Verdict |
|---|---|---|---|
| codegen `ruff check src` | 12 | **12** | zero-new |
| codegen `mypy src` | 55 | **55** (in 11 files, 71 checked) | zero-new |
| companion `ruff check src` | 1 | **1** | zero-new |
| companion `mypy src` | 108 | **108** (in 26 files, 59 checked) | zero-new |

### Cleanliness

- `git diff --check` in **both** repos: clean.
- Frozen twins byte-untouched: `git status --short tests/fixtures/catf_mfe_model
  tests/fixtures/catf_mfe_d5` is empty; neither has a commit in this item's range.
- Codegen working tree at the end: only `.project/CURRENT_WORK.md`, modified before this stage
  started.
- Companion working tree: clean.

---

## Success criteria, one by one

### 1. An asserted predicate containing a compatible unit-annotated literal elaborates without `SI_OCCURRENCE_MISSING`, and unit behaviour is unchanged in both directions

**Discharged.** `tests/conformance/test_predicate_unit_annotation.py`:
`test_an_asserted_predicate_carrying_a_unit_annotation_elaborates` passes on the new
`predicate_unit_annotation` fixture, which raised
`SI_OCCURRENCE_MISSING: leaf declaration 146016c8-… has no feature slot` at `3ca94af`
(`probes/red-evidence.md`).

Unchanged in both directions:
- `test_an_incompatible_annotation_still_blocks_on_a_dimension_reason` — the incompatible twin
  still refuses with `block_incompatible_dimensions: ordering '>=' cannot compare different
  dimensions.` (probe P2, run once as designed).
- `test_unit_annotation_values.py` — the two previously cured lanes, 6 tests, unchanged and green.
- `test_the_unit_is_not_resolved_as_a_reference` — no `SI::` element appears as a graph
  dependency, following `test_unit_annotation_values.py:53-60` verbatim.
- `test_the_annotated_and_bare_twins_wire_up_identically` — invariant 7: same wiring shape, and
  `{"gap_width": 0.5}` on both twins, so no dependency edge was lost.

### 2. That predicate's end state is a **working gate**, pinned positively

**Discharged.** `test_the_cured_predicate_is_a_working_gate`: the catalog carries a row for
`gap_guard` with `disposition_kind == "eligible"` and `disposition_reason == "admitted"`, and
`coverage_account` reports `assessed_gate_count == 1`, `unassessed_gate_count == 0`. Probe P1
selected the **primary** branch on the fixture as authored in Phase 1.

The demonstration predicate is an inequality (`gap_width [m] >= 0.25 [m]`), not
`== <literal> [unit]`, as the spec requires.

**One thing the spec's readers should know.** The fixture annotates *both* operands. The spec's
one-sided shape blocks on `block_ordering_category_pair` — a bare `Real` feature reference is
category `real`, an annotated literal is `quantity`, and `(real, quantity)` is not an admitted
ordering pair. The design's stated remedy for that branch (a declared quantity type on the
attribute) is unreachable: codegen refuses `ISQBase::LengthValue` as an unsupported exact type.
Annotating both operands reaches the same designed end — a `quantity`/`quantity` pair the profile
admits — by the one route the product supports. Recorded in the fixture header and in the plan's
Phase 1 notes.

### 3. The published promise at `modeling-assumptions.md:535` is true, and any reason that still cannot keep it is named in the record

**Discharged.** The promise sentence is rewritten to state what is now true, and §8 gains a "What
a block tells you" paragraph with the worked message.

The residue is named against the **authoritative** vocabulary, not the published nine:
`reason-codes-reconciliation.md` in this folder covers all **23** `block_*` members of the
companion's closed `REASON_CODES`, read at `0a52942`. Headline: **1 names the fix**
(`block_feature_chain`, cured here), **11 name the shape** with an explicit actionable message,
**10 name the reason only**, **1 mixed**. All 23 gained a location. Three reason-only rows are
named as the cheap follow-on; four more are recorded as adequate, with the reason.

### 4. A blocked feature chain names the offending written reference and states the supported rewrite

**Discharged.** `tests/conformance/test_blocked_chain_diagnostic.py`, on
`constraint_blocked_chain_multi`. Rendered detail, verbatim (one line, wrapped here only):

```
constraint profile blocked execution: block_feature_chain: feature chain
'bioshield.inner_radius' is not executable in a predicate body; bind it to a constraint formal
in the usage (in inner_radius = bioshield.inner_radius;) and use the formal in the predicate
[model.sysml:43]; block_feature_chain: feature chain 'bioshield.outer_radius' is not executable
in a predicate body; bind it to a constraint formal in the usage (in outer_radius =
bioshield.outer_radius;) and use the formal in the predicate [model.sysml:43]
```

At `3ca94af` the same model produced `block_feature_chain: feature_chain: block_feature_chain`
three times.

Probe **P4 confirmed live**, not only statically: `".".join(chain_segments)` reproduces the
authored spelling `bioshield.outer_radius`.

**Limit, stated rather than implied:** the location is the constraint *usage's* line, not the
chain's own. Both entries read `[model.sysml:43]`, which is where the `assert constraint` opens —
the `LocationFact` the companion attaches to a decision is the usage's, and the payload has no
per-node location. Naming the reference is what disambiguates within a predicate. Recorded in the
docs text and in the reconciliation file.

### 5. A multi-chain predicate identifies each **distinct** reference, deterministically

**Discharged.** Three chain occurrences over two distinct references →
`test_three_chain_occurrences_collapse_to_two_distinct_entries` asserts `count == 2`;
`test_two_elaborations_of_one_model_produce_byte_identical_detail` asserts byte identity across
runs; `test_the_detail_is_a_single_line` asserts no newline (invariant 8).

The determinism is by construction, not by luck: `tests/unit/test_render_block_reasons.py` (8
tests, no license needed) pins the key over hand-built diagnostics — a `None` `line`/`column`
raises no `TypeError`, two entries differing only in `construct` render identically under input
permutation, thirteen identical diagnostics collapse to one, an absent location renders no suffix
at all in each of its three forms.

### 6. Kept failing characterizations committed **before** the fixes, each demonstrated red first

**Discharged, and falsifiably.** Phase 1 (`f3b3131`) landed 26 characterizations, 20 of them
`@pytest.mark.xfail(strict=True)`, before any fix code. `probes/red-evidence.md` holds the
marker-stripped run **verbatim**: **20 failed, 6 passed** — the same 20/6 split as the marked run,
so every marker carried a real failure and none masked a pass. The 6 green rows are named there
with what each guards.

`strict=True` did its job twice without being asked: the two rows the companion message alone
satisfies XPASSed and failed the suite until their markers came off (`284f716`), and the
population oracle's rule 4 failed until `predicate_unit_annotation` left `REFUSED_BY_DESIGN` when
D1 landed.

### 7. Existing quantity, occurrence, profile, and diagnostic tests do not regress

**Discharged.** 2010 passed, zero failed. Specifically:
- `test_unit_annotation_values.py` — 6 passed.
- `test_elaboration_payload_identity.py` — 13 passed, and the file is **unedited** (D7), confirmed
  by `git status`. Its regex depends on the detail staying one line, which invariant 8 and its own
  test now pin.
- `tests/unit/test_constraint_usage_record_mint.py` — 8 passed; the `SI_CONSTRAINT_BLOCKED` row
  count did not move (invariant 4).
- constraint catalog, coverage, and population-oracle suites — green.

### 8. Focused tests, full suites, `ruff check src` = 12, `mypy src` = 55 (zero-new), `git diff --check`, with exact counts recorded

**Discharged.** See "Commands and exact counts" above. All four lint gates at baseline, both
`git diff --check` clean.

---

## Probe verdicts

| Probe | Verdict | Branch selected |
|---|---|---|
| **P1** — is the demonstration predicate admitted after D1? | `disposition_kind == "eligible"`, reason `admitted`, severity `info`; `assessed_gate_count = 1`, `unassessed_gate_count = 0`, `applicable_gate_total = 1` | **Primary.** Fixture stands as authored in Phase 1. B4 holds for the both-operands-annotated shape and fails for the one-sided one — see criterion 2. |
| **P2** — regression guard (gates nothing, A1) | `predicate_unit_annotation_incompatible` still refuses: `block_incompatible_dimensions: ordering '>=' cannot compare different dimensions.` | As expected. The companion path is intact; the unit is still a unit after codegen stops reading it as a reference. |
| **P3** — does the fourth-lane cure keep the binding's unit visible to the profile? | Value is `0.05`, no readiness finding — **and** the profile's verdict is identical for `in tol = 0.05;`, `in tol = 0.05 [m];`, and a deliberately mismatched `in measured = width [m]; in tol = 0.05 [s];`: all three `eligible`/`admitted`. | **Invariant 6 does not fire** — nothing was lost, because the profile never read a unit off a *binding*. See "Surfaced" below. |
| **P4** — is the chain reconstructible from `chain_segments`? | Confirmed live on `constraint_blocked_chain_multi`: the rendered detail reads `feature chain 'bioshield.outer_radius'`. | **Primary.** B3 holds, no companion CST read needed. |

---

## Surfaced (capture-fidelity §4) — not resolved here

**B2 is false for the binding lane.** The design's B2 says the unit text reaches the profile
through the companion's own extraction. That holds for a unit written *inside a predicate body* —
P2 proves it. It does **not** hold for a unit written on a constraint usage binding:
`in tol = 0.05 [m];` is dimensionally inert to the profile, because a bound formal takes its
operand category from the definition's declared type (`Real` → `real`) and the binding's
annotation never reaches `classify_ordering`. Measured, `p3c` binds a length against a time and
the profile admits it. True before and after this item; nothing here widened or narrowed the
profile (invariant 3).

**Consequence for Item 5**, which is why it is written down: the blessed tolerance-band recipe is
exactly this shape. A band binding can carry a unit for a human reader, and the gate will not
check it. Carried into `reason-codes-reconciliation.md` and the plan's Phase 3 notes for the close
record.

---

## Pre-existing breakage repaired, so the suite could run

**The full licensed codegen suite did not run at `3ca94af`.**
`tests/unit/test_coverage_ledger_agreement.py:25` pointed at
`.project/active/constraint-coverage-policy/expected-coverage.md`, which Item 3's close (`cec3f03`)
moved to `.project/completed/20260813_constraint-coverage-policy/`. Collecting that module raised
`FileNotFoundError` and interrupted collection for the whole suite —
`79 deselected, 1 error in 0.83s`, nothing executed. The path is corrected to the archived
artifact; nothing about the ledger's content changed. Recorded here because it means no full-suite
count from before this item is comparable.

`tests/conformance/test_constraint_population_oracle.py` also gained the five expectation files its
rule 1 requires for new constraint-bearing fixtures, plus three permanent `REFUSED_BY_DESIGN`
entries. A fourth, temporary entry for `predicate_unit_annotation` was removed when D1 landed, as
its own rule-4 test forced.

---

## Deviations from the plan

All are recorded in `plan.md`'s Implementation Notes at their phase. In one place:

1. **The demonstration fixture annotates both operands** (Phase 1). The plan's shape reproduces
   the defect but cannot pin a working gate, and the design's fallback is unreachable. Criterion 2
   above states the measurement.
2. **The Defect B fixture is asserted, not plain** (Phase 1). A plain constraint never consults
   the profile — it grades `excluded`/`unassessed_form` and emits no block reasons, so there would
   be no detail to read. The characterizations use the non-strict elaboration idiom from
   `test_elaboration_payload_identity.py:246-253`, and the same fixture pins that the strict path
   still halts.
3. **`_render_block_reasons` takes the diagnostics sequence, not the decision** (Phase 5). It
   reads nothing else, and the signature says so.
4. **Landing order steps 4 and 5 are one landing** (Phase 4). The design's "the companion change
   is safe alone" note was about pre-existing codegen tests; this item's own characterizations
   assert the cure by construction, so two `xfail(strict=True)` rows XPASSed the instant the
   companion committed. The companion commit and the codegen commit that unmarks them land back to
   back, and no commit in between was reported green.
5. **Two green-before-the-fix rows** (Phase 1): the single-line and byte-identity assertions. The
   plan's verify step allows this explicitly.
6. **`ref` is a SysML keyword** (Phase 1), so the fourth-lane binding is `ref_value`.
7. **The design's residue table understated the companion** (Phase 6). Most of the eight published
   "residue" reasons already carry explicit, actionable messages; only their construct-naming is
   coarse. `reason-codes-reconciliation.md` states what is actually there.

---

## Commit trail

Codegen (`item7-rebuild`):

| SHA | Phase | |
|---|---|---|
| `f3b3131` | 1 | red-first characterizations land xfail-strict, red captured as output |
| `acfba0b` | 2 | unit annotation unwraps at the reference-walk head (D1) |
| `098ea65` | 3 | the fourth lane — unit-annotated constraint bindings (D2) |
| `284f716` | 4b | unmark the two Defect B rows the companion message alone satisfies |
| `1b94c4b` | 5 | block reasons de-duplicate, order, and name where (D4/D5/D6) |
| `3459127` | 6 | make the block promise true, and reconcile all 23 block reasons |

Companion (`item7-rebuild`): `0a52942` — a blocked feature chain names the chain and the rewrite.

`4e5bc71` also sits in the codegen range; it is the orchestrator's own epic-file commit
(`.project/backlog/epic_constraint_semantics_contract.md` only) and touches nothing here.

**Red evidence:** `.project/active/constraint-predicate-hardening/probes/red-evidence.md`
**Reason-code reconciliation (for the close record):**
`.project/active/constraint-predicate-hardening/reason-codes-reconciliation.md`
