# Audit: Lifecycle Item 1 — Occurrence and Demand Integrity

**Verdict:** Needs work
**Audited:** 2026-07-19
**Branch:** `constraint-exec-epic`
**Candidate:** `28bc8b0f` (HEAD `8aac0a4` is code-identical — the follow-on commits touch only `.project/`)
**Coordinated pins:** agentic-mbse `515e08bb`, TEAx `d545701f`

---

## Summary

The lifecycle rebuild is real and the evidence is, with two exceptions, honest and reproducible.
I reran every gate first-hand and all seven invariants hold with traceable code locations. The
RED/GREEN byte-identity question is now closed by an unbroken chain of custody rather than by
trusting the plan's notes.

Two things block a clean certification, both narrow and both fixable without rework:

1. **A silent value-loss regression** that Item 1 introduced in `_resolve_value`. I reproduced it
   on both the predecessor and the candidate: the predecessor returns `42.0`, the candidate
   returns nothing and reports the loss nowhere.
2. **Mandatory acceptance case OD-A10 was not delivered as approved**, and the shortfall is
   undisclosed — the design's fixture spec and the plan's checked box both assert observations no
   test makes.

Everything else in the brief's five priorities reproduced exactly. The item is close.

---

## Findings

### Plan completion

Phases 0–6 are substantively complete. One checkbox is not supported by the code.

**F2 — `plan.md:726` is a checked box the implementation does not support.** The box reads
"Unique targets produce the exact OD-A08/OD-A09 info summaries and OD-A10 warning order/counts."
The OD-A08/A09 half is genuine. The OD-A10 half is not: no test asserts OD-A10's counts or its
warning order. Detail under Spec conformance. The brief's priority 4 names unsupported checkboxes
specifically, so this is called out rather than folded into a note.

### Spec conformance

**Success criteria.** Criteria 1–3 are met and I verified them independently. Criterion 4
(truthful evidence) is *substantially* met — evidence.md is unusually forthcoming, recording eight
deviations, a review-confirmed defect, a digest mis-recording, and an unexecutable-RED caveat — but
F2 and F3 below are deviations from the approved design that the record does not disclose, so I
cannot mark it fully confirmed.

**F2 (blocking) — OD-A10 is not delivered, and the gap is unrecorded.**

The approved design specifies the `order` fixture at `design.md:602`: `a_collision` has a real
`101.0` plus supplied `11.0`, `b_nonliteral` carries a highest-precedence CHAIN, `c_clean` supplies
`33.0`, yielding "counts and exact warnings are OD-A10's 3/2/1 sequence." `design.md:622` states the
proof instrument asserts `scanned=3`, `applied=2`, `non_literal_skips=1` and "both spec warning
bytes once/in order."

The fixture as built (`tests/fixtures/constraint_occurrence_demand/order/model.sysml:40-44`) gives
all three attributes plain literal overrides — `11.0`, `22.0`, `33.0`. There is no real captured
attribute to collide with and no CHAIN. So the observed behaviour is 3/3/0 with no warnings, and
`test_r7_multi_target_order_permutations`
(`tests/conformance/test_constraint_occurrence_demand_acceptance.py:151-155`) accordingly asserts
`_warning_messages(caplog) == []` and `"3 literal applied, 0 non-literal skipped"` — the opposite of
what the design says it asserts.

The two warning bytes are pinned separately at unit level, each at `scanned=1` and with different
QNs: the collision warning at `tests/unit/test_logical_demand_resolution.py:369` and `:494`, the
deferred-summary byte at `:420-423`. **No test pins the two warnings' relative order within one
batch**, which is precisely the observation OD-A10 exists to make ("Exactly two warnings occur in
order: X then Y").

The fixture's own `PROVENANCE.md:5-6` discloses the split honestly. The evidence record does not —
§6 lists eight deviations and this is not among them. What OD-A10 *does* prove publicly is the
demand-ordering half: three-target order, defaults, and live/replay parity under permutation. That
part is solid.

*What should change:* either build the fixture the design specifies, or record this as a deviation
in evidence §6 with the unit-level substitute named, and correct `plan.md:726`. If the split stands,
add one test that pins both warnings in a single batch so the ordering claim has a home.

**F3 (note) — the cycle fixture also deviates from the approved design, and deviation 6
mis-attributes the source.** `design.md:598` specifies an `A → B → A` variant, declaration-reversed
variants, and a pre-existing output target holding `b"sentinel\n"` that must stay byte-identical on
failure. None of these exists: the fixture models only the self-cycle
(`tests/fixtures/constraint_occurrence_demand/cycle/model.sysml:21`), and `grep` finds no
`OccurrenceDemandCycle__A`/`__B` and no sentinel byte-preservation test anywhere.

Evidence §6 deviation 6 calls this "a plan-drafting discrepancy, not an implementation gap" and
cites only the plan's Phase 2 validation line. That attribution is wrong — the approved design
specifies the same fixture content. The substance is largely fine: I verified the unit-level
substitute exists and asserts exactly what evidence claims
(`tests/unit/test_part_instance_index.py:237-244`, `cycle_path == ("A","B","A")`, edge
`("A","b","B")`). But OD-A05's "no target bytes are produced or changed" half is proven nowhere and
disclosed nowhere.

*What should change:* correct deviation 6 to name the design as a source, and either prove or
explicitly defer the output-bytes-on-failure observation.

**Non-goals respected.** Verified. No Item 2 resolver symbol or import appears in the diff, and no
new target-equivalence rule was introduced. Items 4/5/13 are left open with their ownership intact.

### Design conformance

All seven required invariants verified against the implementation, not against names or docstrings:

- **No re-query from lowering (I10).** `lower_constraints(facts, *, prepared, registry,
  design_attrs)` at `constraint_lowering.py:1070` takes no index and no source-location route. The
  only `occurrences_of` call is `_expand_part_owner` (`:416`) and the only `evaluate_profile` call is
  `associate_usage_decisions` (`:534`), both inside preparation.
- **All-or-nothing prepared batch.** `staged` is a function-local at `constraint_lowering.py:748`,
  frozen once at `:787`; no module- or index-held journal survives a raise.
- **Structural cycle error intact.** All five cause fields set at `part_instance_index.py:81-94`,
  re-raised `from error` at `constraint_lowering.py:423-428`; nothing re-wraps in between.
  Independently confirmed by the passing acceptance node.
- **Copy-on-write enrichment (I9).** Fresh dict at `supplied_values.py:509`, per-key new lists at
  `:512`; the input mapping is never touched.
- **Deterministic ordering.** No bare set iteration reaches ordered output; sort points at
  `supplied_values.py:478-484`, `constraint_lowering.py:787`, `part_instance_index.py:357/371/404`.
- **No package fallback for unsupported owners.** Explicit dispatch with a raising `else` at
  `constraint_lowering.py:761-773`.
- **Excluded/unsupported owners issue zero occurrence queries.** The sole query site is gated behind
  the `is_excluded_usage` branch; preflight runs before `staged` exists.

Recorded deviations 1, 2, 4, 5, 7, 8 are consistent with the code as built. Deviation 3 is
incomplete — see F5. Deviation 6 is mis-attributed — see F3.

### Code integrity

**F1 (blocking) — silent value-loss regression in `_resolve_value`,
`src/sysml_codegen/resolution/supplied_values.py:268-281.**

Item 1 merged the predecessor's separate tier 2a and tier 2b blocks into one loop over
`(type_qn, owning_part_def_qn)`. Inside it, a `literal_value` that will not parse as a float does
`return None, False, None` — which now exits the **whole loop**, not just the current tier. A
malformed literal on the specialized/type def therefore suppresses a perfectly good literal on the
consuming part def.

Reproduced on both trees with the same inputs (a `LITERAL` redef `"true"` owned by the type def,
plus a valid `"42.0"` owned by the consuming part def):

| Tree | `_resolve_value(...)` |
|---|---|
| Predecessor `ecdc7285` | `(42.0, False)` — falls through to tier 2b and recovers the value |
| Candidate `28bc8b0` | `(None, False, None)` — value lost |

The predecessor's tier 2a routed through `_find_literal_redefinition`
(`resolution/graph_builder.py:1195`), which returns `None` on a malformed literal and lets control
fall through. That fall-through is gone.

The loss is **silent**. Running the full seam end to end on that input logs exactly:

```
supplied-value materializer scanned 1 referenced bindings: 0 literal applied, 0 non-literal skipped.
```

Nothing applied, nothing skipped, no warning — the demand vanishes. The cause is a disposition
asymmetry: tier 1 sets `saw_non_literal = True` on the identical malformed input
(`supplied_values.py:229-230`), so the caller counts and reports it (`:533-534`); tier 2 returns
`False`, so it is never counted, never warned, never deferred. Same data defect, two opposite
dispositions in one function.

The tier-2 swallow itself is pre-existing (the predecessor had the same `except: return None, False`).
What Item 1 introduced is the early exit that makes it eat a *valid* lower-tier literal. No test
covers this shape, which is why the 3,009-test suite is green.

*What should change:* the malformed-literal branch should not terminate the tier loop, and it should
report the defect the way tier 1 does — flag it as non-literal or raise. A resolvable value must not
disappear without a diagnostic.

**F4 (note) — ambiguous owner provenance silently downgrades a tier,
`supplied_values.py:319`.** `_owner_source` returns `sources.pop() if len(sources) == 1 else None`,
so "no source" and "two or more conflicting sources" are reported identically. That `None` reaches
`select_group_source:345-347`, where `any(_usable_source(...))` is false and control drops to the
constraint-usage tier. The sibling helper `_unique_source:295-304` raises loudly on exactly this
ambiguity. This sits adjacent to accepted deviation 4 (how tier 3 reads its source), but the
deviation covers *which* data is read, not *silently downgrading on conflict*.

**F5 (note) — `source_location_mode=None` has two consumers that disagree,
`constraint_lowering.py:567` vs `:684`.** `_project_excluded_location` raises "excluded assertion
requires an explicit source-location route" on `None`; `_verified_predicate_source_key`'s `else`
branch silently falls back to `Path(raw_file).name`, an unvalidated non-portable basename that feeds
the minted predicate-source key. Both production callers pass explicit values
(`pipeline_builder.py:839` `"live"`, `graph_rebuild.py:96` `"snapshot"`), so `None` is reachable only
from unit tests — which therefore exercise a key-derivation path production never takes. Evidence
deviation 3 claims the nullable was kept so "route-absence still fails at the same place with the
same message"; that holds for the excluded-location path and not for the source-key path.

**F6 (note) — the operator-facing count noun is now wrong, `supplied_values.py:570` and `:579`.**
Both log lines read `"scanned %d referenced bindings"` but pass `len(demands)` — the count of
normalized targets, not bindings. Collapsing many bindings into one logical demand is the entire
point of this change, so the number an operator reads is systematically smaller than the word says.
The `shared` fixture is the live example: a calc binding and a constraint assertion reference one
target, and the pinned byte reads `scanned 1 referenced bindings`. Relatedly, `applied` is
incremented at `:536` before the collision check at `:539`, so it counts targets whose synthesis was
skipped — that one is at least documented in the adjacent comment.

**F7 (minor) — `_usable_source` reads process state, `supplied_values.py:292.** The predicate
includes `path != Path.cwd()`, making a pure resolution helper depend on the directory the generator
was invoked from. Two runs over identical inputs from different working directories could classify
the same path differently. It appears unreachable in practice, but it does not belong in this
helper.

**Clean.** No load-bearing `assert` survives in the changed files, which matters because the focused
gate runs under `python -O`. No dead branches remain from the deletions. No broad
`except Exception` was introduced on the demand path.

---

## Certification

### Reproduced first-hand

Every gate below I ran myself at HEAD, having first confirmed
`git diff --name-only 28bc8b0 HEAD -- src tests` is empty.

| Gate | Evidence claim | Reproduced |
|---|---|---|
| Full suite | 3,009 passed, 26 skipped, 16 deselected | **3,009 / 26 / 16, 0 failed** ✓ |
| Acceptance file | 6 passed | **6 passed, no skips** ✓ |
| Focused optimized (`python -O`) | 63 passed | **63 passed, no skips** ✓ |
| TEAx execution | 2 passed | **2 passed** ✓ |
| Mypy | 76 errors in 17 files (= Phase 0) | **76 in 17** ✓ (Phase 0 baseline confirmed at `plan.md:341`) |
| Ruff `check src/` | clean | **All checks passed** ✓ |
| Ruff `format --check` | 19 would reformat | **19** ✓ |
| Deletion absence grep | no matches | **no matches** ✓ |
| `pyproject.toml` / `uv.lock` drift | empty | **empty** ✓ |

**RED/GREEN byte identity — chain of custody closed.** The brief asked me to reconstruct the
overlay hash from git; git alone cannot do it, because the acceptance file was first committed in
`cfeb7ee` and does not exist at the RED predecessor. I closed it with the independently recorded
Phase 0 manifests instead:

- `sha256sum /tmp/item1-red.yslzRA/overlay.sha256` = `8a5758fa9bf892…cca2897`, which **exactly
  matches** the "complete overlay-manifest SHA-256" recorded at `plan.md:319-321`. The manifest is
  therefore the one Phase 0 wrote, not a later reconstruction.
- `sha256sum -c` of that manifest against the candidate tree: **all 14 files OK** — the acceptance
  file and all thirteen fixture/PROVENANCE files are byte-identical to RED.
- `sha256sum -c unchanged-tests.sha256`: **OK**, overlay at
  `aea7c8219d716f4ca1ecb154ca6ed8a13e0c15b1184fdcfe2d92b556eacb624b`.

**Licensed nodes genuinely ran.** Verified two ways: `-rs` reported no skip and 6 passed, and a
control run confirmed the nodes execute rather than skip. Note for the record: the six nodes pass
identically with and without the `.env` loaded, because `_license_available()`
(`tests/conftest.py:24-42`) probes a live model load that succeeds in this environment regardless of
that file. Evidence §2's framing of the `.env` load as a precondition is imprecise, but it
overstates no result — the nodes ran, and the fake-baseline risk did not materialize.

**Preservation, proven more strongly than the aggregates.** Rather than recompute the §5 aggregate
digests, I used git directly: `git diff ecdc7285 HEAD --name-only -- tests/fixtures
tests/baseline_outputs`, excluding the new `constraint_occurrence_demand/` tree, returns **nothing**.
No tracked fixture or baseline byte changed. This makes the Phase 0 digest-correction narrative in
§5 consistent, and the decision to preserve the wrong original alongside the correction is the right
call.

**TEAx node is genuine, not a stub.** `_run` (`tests/execution/test_constraint_execution.py:87-101`)
imports `simkit.core.pipeline.execute_pipeline` and runs the generated package's real pipeline YAML.
The test asserts distinct evaluation channels, generated inputs `4.0`/`6.0`, verdicts
`("violated", False)` / `("satisfied", True)`, `assessed_count == 2`, `headline == "violation"`, and a
persisted report carrying both statuses. Evidence §3 matches it exactly.

**The §7 defect fix is real.** `select_group_source` is a separate call-site step invoked only after
the collision guard (`supplied_values.py:539-543`), and the regression test
(`tests/unit/test_logical_demand_resolution.py:440-478+`) pins both halves as described, including
the first-half `pytest.raises(... "calc-origin provenance is ambiguous")`. The evidence's plainly
stated caveat — that the test could not be run RED because it imports a symbol that did not then
exist — is accurate and appropriately labelled.

### Tracking artifacts

No checkboxes marked. The verdict is Needs work, so no epic heading was given ✅ and no spec success
criterion was newly checked. `plan.md:726` is flagged as unsupported (F2) but left as-is rather than
silently rewritten — correcting the record belongs to the implementing session.

### Not checked

- **Snapshot/replay beyond same-checkout.** I inherited the item's own subset label. Relocated-tree
  and full-tree generation (Item 5) and composed-artifact proof (Item 13) were not exercised, and
  nothing here substitutes for them.
- **R-8 unmappable warning locations.** Left open under Item 4 per evidence §8; I did not probe the
  warning-location projector's failure behaviour.
- **The remaining 75 mypy errors.** I confirmed the count equals the Phase 0 baseline; I did not
  audit whether any individual error masks a real defect.
- **The 19 format-check files.** Confirmed as count-only against the recorded baseline; contents not
  reviewed.
- **Reachability of F1 in real SysML models.** I proved the regression at the function and seam level
  with constructed inputs. I did not author a `.sysml` model that produces a `LITERAL`-typed
  redefinition with an unparseable value, so how often this shape occurs in practice is unquantified.
  The tier-1 code path handles the same case explicitly, which is evidence the authors considered it
  reachable.
- **Item 1's diff outside the demand/occurrence seams.** `snapshot/serializer.py` and
  `snapshot/graph_rebuild.py` were checked for the seven invariants and for ordering, not
  line-by-line for unrelated behaviour change.
- **Performance.** No timing or scaling characteristic was measured.
- **Metrics JSON.** The two `evidence/item1-candidate-metrics*.json` files were not recomputed; per
  the owner's 2026-07-19 ruling those numbers are informational and carry no gate.

---

## What would move this to Certify

1. Fix F1 — the malformed-literal branch must not terminate the tier loop, and the loss must be
   reported rather than silent. Add the missing test.
2. Resolve F2 — either build the `order` fixture as the design specifies, or record the deviation in
   evidence §6 and correct `plan.md:726`, plus one test pinning the two warnings' order in a single
   batch.
3. Correct deviation 6's attribution and disclose the OD-A05 output-bytes gap (F3).

F4–F7 are notes. They can be folded into this item or tracked forward; none blocks certification on
its own.
