# Audit: Whole-Plant Cross-Part Value Resolution (PIPELINE-TRUTH Item 2)

**Verdict:** PASS-WITH-NOTES
**Audited:** 2026-07-06
**Branch:** pipeline-truth-epic
**Commit:** 85022dc (Item-2 range 2de8f60..85022dc)

---

## Summary

The mechanism works and the headline claim is real: the committed fusion-tea snapshot goes
from **10 V11 offenders to 0** (verified structurally by toggling the materializer), the full
YAML package emits, and every gate is green (suite 2056/4/5, ruff 17, mypy 104 — all matching
the expected baselines). The supplied-value materializer is a clean, single-responsibility
pre-pass; the SC-3 runner genuinely executes generated modules; INV-2 renamed-consumer
collapse, the 48.5714 anchor, the 0.0 fixes, and the byte-identity gate all hold.

Two notes, neither blocking. **(1)** The close-out's recorded offender-arithmetic *story* is
wrong about the mechanism — it says "most fusion-tea values are real design attributes
(collision guard defers, real wins) and the rest synthesize," but empirically **all 10 clear
by synthesis with zero collision-defers**; the 10→7 reduction is source-QN dedup. The code is
correct; the recorded narrative misattributes the path, which is exactly the precision the
spec's offender table demanded. **(2)** The three-tier precedence proof is a mechanism-level
unit construction, not the captured `plant_value_precedence` fixture the plan/design named
(a documented Phase-5 deviation). The behavioral contract SC-2 asks for is met.

---

## Priority findings (orchestrator's list)

### 1. Offender arithmetic 10→0 — the "real wins" claim is misattributed (NOTE)

Verified structurally on `tests/fixtures/fusion_tea/extraction_snapshot.json` via the
from-snapshot path (`build_full_graph_from_snapshot`):

- Materializer **disabled** → `collect_uncovered_params` = **10** offenders.
- Materializer **enabled** → **0** offenders. The 10→0 trace is real.
- Materializer log on the committed snapshot: *"scanned 15 referenced bindings: **10 literal
  applied, 0 non-literal skipped**."*
- Synthetic attrs emitted: **7** (not 10). Explicit WARNING-level capture over the whole
  from-snapshot run: **0 collision WARNs, 0 non-literal WARNs**.

So the arithmetic is: **all 10 offender references clear by synthesis** (tier-1/2a/2b), and
the 10-applied → 7-emitted gap is **source-QN dedup** (`synth: dict[qn, ...]` collapses
duplicate/renamed consumers of one source — `driver.efficiency` ×2, `chamber.blanket_energy_multiple`
×2, etc.). **None of the 10 cleared via the collision guard ("real wins")** — the guard never
fired on this snapshot.

The close-out (`plan.md` §"Phase 7", ~line 545) records: *"most fusion-tea values are real
design attributes (collision guard defers, real wins) and the rest synthesize."* This is
**inverted** — there were zero real-wins defers. The spec's offender table (`spec.md:60-73`,
the "Cleared by" column) demanded exactly this per-path precision. **Action (doc-only):**
correct the close-out to "all 10 clear by synthesis; 10 literal applied → 7 unique
source-QN entry points via renamed/duplicate-consumer dedup; zero collision-defers, zero
non-literal skips." No code change.

### 2a. Materializer at the caller seam — both call sites identical, ctx stays pure (PASS)

The documented deviation (materializer moved from inside `build_computation_graph` to the
caller seam) is sound and offline-parity holds:

- **Snapshot path** (`snapshot/graph_rebuild.py:75-85`) and **live path**
  (`orchestration/pipeline_builder.py:817-827`) both call `materialize_supplied_values` with
  **identical arguments** (`calc_usages, redefinitions, design_overrides, usage_type_map,
  <real design attrs>`). The `real_design_attrs` passed is the pre-synth map at both sites, so
  the collision guard sees only real attrs identically.
- **Graph-only-copy claim verified.** The live/capture path builds
  `graph_design_attrs = {k: list(v) for k, v in design_attrs.items()}`
  (`pipeline_builder.py:815`) and feeds *that* to the deriver, backtracker, and graph builder;
  `design_attrs` — the extraction boundary a captured snapshot serializes — stays pure. So a
  snapshot captured from a live run serializes **only real attributes**, and the from-snapshot
  path reconstructs the synth attrs from raw redefinitions/overrides. The snapshot path mutates
  the in-memory loaded `snap["design_attributes"]` directly, which is safe because that dict is
  never re-serialized (from-snapshot generate loads fresh each time). Both paths produce the
  same synth set — cross-checked by SC-4 (0 offenders) landing identically to the orchestrator's
  independent from-snapshot generate.

### 2b. Precedence-proof placement — mechanism-level, anchors hand-transcribed (NOTE)

`tests/unit/test_supplied_values.py:115` `test_three_tier_precedence_ladder` exercises all
three tiers with **distinct** hand-transcribed values and is **reorder-sensitive**:
`resolve(tier2, tier1) == "0.99"` (tier 1 > tier 2), `resolve(tier2, []) == "0.35"` (tier 2
alone), `resolve([], []) is None` (tier 3, no synthesis). A tier-skip/reorder flips an
assertion. The anchors (0.99, 0.35) are literals in the test, not resolver-read.

**Deviation (documented, `plan.md` Phase 5):** the plan/design specified a dedicated captured
`plant_value_precedence` SysML fixture authoring the usage-override tier; the implementation
proves it at the materializer seam with constructed `RedefinitionData` instead. The behavior
SC-2 requires (three tiers, distinct values, reorder-sensitive, hand-transcribed) is fully
met; only the artifact form differs. Acceptable, noted.

### 3. INV-2 renamed-consumer collapse on fusion-tea (PASS)

`tests/conformance/test_fusion_tea_snapshot.py:48` `test_renamed_consumers_collapse_to_one_source_ep`
passes and observes the real shape: `driver.efficiency` produces **exactly one** source-QN
entry point feeding **both** `lcoe_calc.driver_efficiency` **and** `recirc_calc.eta`
(`{"eta", "driver_efficiency"} <= consumer_names`), and `chamber.blanket_energy_multiple`
collapses to one EP feeding two differently-named consumers. Confirmed independently in the
synth dump (one `...__driver__efficiency = 0.35` QN despite two renamed readers).

### 4. The 48.5714 anchor (PASS)

`tests/conformance/test_plant_values.py:93` `test_plant_cost_anchor_hand_transcribed` asserts
`abs((10.0 + 7.0) / 0.35 - 48.5714285714) < 1e-9` — the constant is **hand-transcribed**, and
the composing inputs 10.0/7.0/0.35 are pinned as carried model literals (INV-5). Note: SC-1's
48.5714 is a **graph-level composition** check (per plan Phase 5), not run through
`run_pipeline`. The SC-3 execution gate is separately satisfied on `spec_chain_twolevel`:
`tests/runtime/test_pipeline_runner.py` executes the generated package (importlib module load
+ `.run()`) to `lcoe == 100.0` (hand-derived, `rel 1e-6`), and an input override doubles it to
200.0 — a genuine executor, not graph re-read.

### 5. Byte-identity gate (PASS)

`git diff --exit-code <pre-Item-2> HEAD -- baseline_outputs/catf_mfe baseline_outputs/ife_plant`
is **empty** (byte-identical) checked both against `2de8f60^` (first Item-2 commit parent) and
against `941aa9b^`. Both baseline dirs are non-empty (computation_graph.json + registry_init.py
each). No collateral drift from the materializer.

### 6. 0.0-truthiness fixes (PASS, sweep clean)

Both named sites use `is not None`:
- `graph_builder.py:486` (`_classify_entry_points`) — the materializer's own classify path.
- `graph_builder.py:1151` (FORMULA/computed-attr input builder).

Pinned by `test_supplied_values.py` (0.0 literal → `"0.0"`) and the unit classify test; suite
green. **INV-6 sweep:** two other `.default_value:` truthiness sites remain —
`graph_builder.py:647` and `parameter_groups.py:647` — but both read **calc-def input library
defaults** which are **string-valued**, so `"0.0"` is a truthy non-empty string and is *not*
dropped. The materializer never routes through either (it emits design attributes classified
at `:486`). No live 0.0-drop; the sweep is clean.

### 7. Vendored fusion_tea fixture (PASS)

- Models committed (`library/`, `designs/`, `concepts/`) + `extraction_snapshot.json` at
  `snapshot_format_version: 2`.
- Registered in `scripts/capture_extraction_snapshots.py:110` (`"fusion_tea": FIXTURES_DIR / "fusion_tea"`).
- Loads under the v2 hard-gate (`snapshot/loader.py:81-87`, `SNAPSHOT_FORMAT_VERSION = 2`) —
  its conformance tests pass, which requires passing the gate.
- R3-clean: single commit (`47f5165`, Phase 7), fresh `captured_at` (2026-07-07T00:32:56Z), no
  hand-edit history. All fixtures uniformly at v2 (Item-4 format bump held).

### 8. Gates (PASS)

- Suite: **2056 passed, 4 skipped, 5 xfailed** (matches 2056/4/5).
- ruff: **17 errors** (matches expected baseline — pre-existing, not Item-2-introduced).
- mypy: **104 errors** (matches expected baseline).
- Matrix `### SVM` block present (`verification-matrix.md:502-505`), REQ-SVM-01..04 all PASS,
  each citing a green test file. Doc 25 §Supplied-Value Materializer, docs 11/12 cross-refs,
  modeling-assumptions §5, and the Item-9 impact block all present (SC-6).

---

## Findings

### Plan completion
All 8 phases landed and verified. Two structural deviations, both documented in `plan.md`
Implementation Notes and both sound: (i) materializer relocated to the caller seam with a
graph-only `design_attrs` copy so the extraction boundary stays pure (verified §2a); (ii)
precedence proven at the mechanism seam rather than a captured fixture (§2b). One deviation is
*mis-recorded*: the Phase-7 close-out's offender-arithmetic narrative (§1).

### Spec conformance
- **SC-1** (headline flip): met — `plant_values` resolves a/b/c to 0.35/10.0/7.0 on source-QN
  EPs, offender set empty, behavior-observing pins.
- **SC-1d** (in-part flip): met — `test_shape4_in_part_inherited_redefine_resolves_to_8` (d)
  flips to 8.0 via the tier-2b direct-owner leg.
- **SC-2** (precedence): met behaviorally; artifact-form deviation noted (§2b).
- **SC-3** (executor gate): met — genuine execution of the generated package via `run_pipeline`.
- **SC-4** (license-free proxy): met — true zero offenders on the committed fusion-tea snapshot,
  full YAML emits.
- **SC-5** (baseline discipline + raise-proof): met — four cross-part baselines byte-identical;
  V11 raise-proof re-anchored to Shape 1 (`rated_cost.rate`), `test_shape1_still_trips_v11_after_item2`
  green.
- **SC-6** (docs + Item-9 impact): met — doc 25 section, matrix SVM block, Item-9 block present.
- **Non-goals** respected: no fusion-tea repo changes; the materializer applies LITERAL only
  (non-literal falls to V11 loudly per REQ-SVM-04).

### Design conformance
Implementation follows the design (value-fill D1, materialize-into-`design_attributes` D2,
REQ-SVM family D3, no split D4, Shape-1 raise-proof D5). INV-1..7 hold. The one substantive
departure from the design's stated placement (materializer inside `build_computation_graph`)
is the caller-seam relocation — a correct adaptation to where the backtracker is actually
constructed, documented and verified for offline parity.

### Code integrity
`resolution/supplied_values.py` is a clean single-responsibility module: no god functions, no
silent fallbacks (non-literal and collision both WARN loudly; INV-7/REQ-SVM-03), precedence is
total and loud. The collision guard and source-QN dedup are correctly separated. No slop or
failure-honesty issues found.

---

## Certification

Verified and marked: SC-1, SC-1d, SC-2, SC-3, SC-4, SC-5, SC-6 in the spec; all 8 plan phases.
The item delivers the epic CSF (zero V11 offenders on the fusion-tea snapshot) and every
success criterion.

**One documentation correction is owed before close** (non-blocking): the Phase-7 close-out
in `plan.md` misattributes the 10→0 clearing path as "collision guard defers, real wins" when
all 10 clear by synthesis (10 applied → 7 source-QN EPs via dedup, zero collision-defers).
Correct the narrative to match the verified arithmetic; the spec's offender table asked for
exactly this precision. No code change is required.

ARTIFACT: .project/active/whole-plant-resolution/audit.md
