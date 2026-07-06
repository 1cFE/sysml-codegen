# Audit: Item 4 — Subtype-Aware Enumeration & Constraint-Report Truth

**Verdict:** PASS-WITH-NOTES
**Audited:** 2026-07-06
**Branch:** pipeline-truth-epic (codegen); pipeline-truth-item4 (agentic-mbse, unverified — see limit)
**Commit:** HEAD `88a419c` (codegen)
**Epic:** PIPELINE-TRUTH, Item 4

---

## Summary

The codegen side of Item 4 is delivered faithfully and is well-pinned. Every codegen deliverable
I could inspect statically matches the spec's decision table and the design's invariants: the
subtype-aware collect/render split, the REQ-EXT-09 re-anchor with an executable mutation check, the
constraint manifest serialized through the whole snapshot chain, the from-snapshot replay, the
dead-code deletions, the docs rewrite, and the committed v2 snapshots (all 23 at version 2, wi014
carrying the real assert manifest). The from-snapshot report is now genuinely available and pinned
license-free.

Two substantive notes keep this from a clean PASS. **(1)** The Phase-5 reviewed-diff gate — an
explicit `[HARD]` control — under-itemized at least one of the six flagged fixtures: `self_named_rescue`'s
v2 diff carries a semantic binding reclassification (`reference`→`chain`) that the completion note
bucketed as "source_file relativization." The gate's *conclusion* (not an Item-4 behavior change)
holds — Item 4 touches no binding-resolution code — but the disclosure was inaccurate, which weakens
the gate for a truth-item. **(2)** The `wi014_toy AND the committed fusion-tea snapshot` success
criterion is only half-demonstrable here: there is no committed fusion-tea snapshot anywhere in this
repo, and the v2 hard-gate now rejects any external v1 fusion-tea snapshot until Item 2 re-captures it.

A third, non-defect limit dominates the verdict: this non-interactive sandbox blocks all code
execution (every `python`/`pytest`/`uv` call returns "requires approval" with no approver) **and**
blocks all reads/exec of `/home/reid/1cfe/agentic-mbse`. So "both suites green," ruff/mypy counts, a
live mutation run, the SC-D acceptance generations, and the **entire agentic-mbse half** (rows 5–8,
the published decision table, the TYPE_MAP contents, Level-3 circular-FAILS) could not be
independently re-executed. They are certified only as *plan-recorded*, corroborated by source where a
codegen artifact touches them (e.g. the INV-D test imports the adapter policy).

---

## Findings

### Plan completion

All 8 phases are marked complete in `plan.md` with completion notes. Codegen-side phases verified by
artifact:

- **Phase 3 (report + re-anchor):** `extraction/constraint_report.py` (pure module) and
  `extractor.py:98-169` (`report_dropped_constraints` → `collect_constraint_manifest` +
  `_classify_constraint_kind`) present and correct. `constraint_extractor.py` deleted (file absent);
  `_deserialize_constraint_info`/`ConstraintInfo` gone from `loader.py` (0 refs). Verified.
- **Phase 4 (serialization):** full chain wired — `pipeline_builder.py:686,832` → `serializer.py:108` →
  `loader.py:119` → `snapshot_context.py:44-45` (replay). M8 message names
  `scripts/capture_extraction_snapshots.py` (`loader.py:86,93`). Verified.
- **Phase 5 (v2 + recapture):** `SNAPSHOT_FORMAT_VERSION = 2` (`snapshot/__init__.py:15`); all 23
  committed `extraction_snapshot.json` at version 2 (grep: 23/23). Verified.
- **Phases 0–2, 6 (agentic-mbse + adapter docs):** NOT independently verifiable (repo blocked). Marked
  complete per plan/commits `64a097e`/`cc64b1d`/`bc24ae3`/`bc196df`.

No placeholder code or TODOs found in the codegen surface.

### Spec conformance

- **SC — wi014 constraint report incl. `toy_plant.sysml:51` assert:** MET (codegen leg). The committed
  `tests/fixtures/wi014_toy/extraction_snapshot.json:382-390` carries the assert manifest
  (`part_def`, `Toy_Plant`, `affordable`, `assert`, line 51). `test_snapshot_contract.py:92`
  (`test_wi014_manifest_roundtrips_through_committed_snapshot`) pins it license-free: golden == manifest,
  render emits `scanned 1 / 1 assert / affordable ... is not executable`. Live leg
  (`test_extractor.py:949`) also pins it. **fusion-tea leg: NOT MET here** — see Note 2.
- **SC — from-snapshot report available:** MET. Delivered by construction (`snapshot_context.py:45`
  calls the same `render_constraint_report` through the extractor logger); INV-B round-trip pinned in
  `test_snapshot_contract.py` and `test_constraint_report.py:91`.
- **SC — REQ-EXT-09 fails under a broken query (mutation check):** MET structurally.
  `test_extractor.py:969` (`test_mutation_check_discriminates`) calls
  `collect_constraint_manifest(include_subtypes=False)` and asserts the assert is MISSED. The lever is
  real: `extractor.py:135-136` threads `include_subtypes` straight into `elements_of_type`. Independent
  anchor is a grep-transcribed literal `CATF_DROPPABLE = 65` (`test_extractor.py:903-909`), not the
  production query; part-usage leg asserted (`:934`). Could not execute the test (see limit).
- **SC — `require constraint` certified:** MET. `tests/fixtures/item4_require/model.sysml` carries
  `require constraint within_budget` + `requirement demo_req`; pinned by
  `test_extractor.py:990-1004` (require → PLAIN ∈ DROPPABLE_KINDS; requirement → REQUIREMENT ∉).
  Fixture is snapshot-free (out of the recapture set), as designed.
- **SC — `EnumerationUsage` decision (row 3) pinned:** PARTIAL/verified-by-code. `parameter_groups.py:102`
  keeps exact-type `AttributeUsage` (no `include_subtypes`), matching the row-3 opt-OUT. The row-3 pin
  test on solar_battery/catf_mfe was not executed.
- **SC — decision table published (agentic-mbse), pointer here:** pointer verified
  (`01-extraction.md:20` links `../../../../agentic-mbse/docs/subtype-enumeration-decision-table.md`);
  the 8-row table itself is in the blocked repo — not verified.
- **SC — R4 verification table complete:** the R4 table is in `design.md:43-49` (source-read verdicts)
  and `plan.md` Phase-0 records all rows CONFIRMED-live; `_probe.py` committed. Verified as artifact.
- **SC — reviewed-diff gate (byte-identical except version+manifest):** PARTIAL — see Note 1. Two of six
  independently diffed: `attr_expr_probe` CLEAN; `self_named_rescue` carries an undisclosed semantic diff.

Non-goals respected: no constraint execution, no connection/view/case extraction, no enum entry point.

### Design conformance

- **INV-C (full swept subtree in manifest):** followed — `collect_constraint_manifest` keeps every kind,
  tags requirement/satisfy rather than pre-filtering (`extractor.py:134-153`).
- **INV-D (single droppable-policy source):** followed and cross-repo-pinned.
  `test_extractor.py:1029` imports `is_droppable_constraint` from
  `agentic_mbse.sysml.syside_adapter` and asserts `(kind in DROPPABLE_KINDS) == is_droppable_constraint(elem)`
  element-by-element on item4_require. (Not executed; import target in blocked repo.)
- **INV-E (hard gate, no coexistence):** followed — `test_snapshot_contract.py:76`
  (`test_v1_snapshot_is_rejected`).
- **INV-G (stable order):** followed — `extractor.py:152` sorts by
  `(owner_qualified_name, constraint_name)`; `manifest_to_records` preserves order.
- **D8 (stable tokens):** followed — `constraint_report.py:144-176` serialize by `.value`;
  `test_constraint_report.py:116` pins tokens ≠ display wording.
- **D4 (delete row 2):** followed — `constraint_extractor.py` deleted.

**Documented deviations (all sound):**
1. `collect_constraint_manifest` has no `excluded_types` param (design signature listed one). Correct
   call — INV-C needs the full subtree, so a pre-filter constant would be unused. Droppability derives
   from kind via `DROPPABLE_KINDS`, pinned equal to the adapter policy by INV-D. `plan.md` Phase-3
   deviation #1.
2. New live-only fixture `item4_require` for the exclusion/sentinel path. `plan.md` Phase-3 deviation #2.
3. Row-5 (agentic-mbse) needed a graph re-key beyond `include_subtypes` — recorded in `plan.md` Phase-2.
   Not verifiable here.

### Code integrity

No slop or failure-honesty problems in the codegen surface:

- `render_constraint_report` (`constraint_report.py:89`) is a clean pure function — sentinel always
  emitted (observable empty vs blind), per-item INFO, WARN only if `reported>0`. No swallowed
  exceptions, no silent fallback.
- The D6 hard-error stance (unknown type name raises) is the opposite of a silent fallback — good.
- `collect_constraint_manifest` has one injectable keyword (`include_subtypes`), summarizable in one
  sentence — no god-function / mode-sentinel smell.
- `loader.py:120` reads `dropped_constraints` with `.get(..., [])` — additive, but the version
  hard-gate makes the default unreachable for real snapshots, so it is not a compatibility shim papering
  over missing data.

---

## Notes (the "-WITH-NOTES")

### Note 1 — the reviewed-diff gate under-itemized `self_named_rescue` (disclosure, not correctness)

The Phase-5 completion note (`plan.md:487-498`) lists six fixtures with diffs beyond version+manifest
and buckets them into three benign causes. I independently diffed the committed v2 against its v1
predecessor (`git diff 89e6f80 5d77856`) for two:

- **`attr_expr_probe` — CLEAN.** Every extra change traces to `reference_chain` (null or a populated
  list) + `dropped_constraints: []` + version/timestamp. `reference_chain` entered `src/` in `89e6f80`
  (UPSTREAM-FINDINGS, Item 10) — a landed extraction feature, not Item-4. Confirmed benign.
- **`self_named_rescue` — under-disclosed.** Beyond the claimed `source_file` relativization, the v2
  snapshot reclassifies the `sink_calc` `throughput` binding: `binding_type: "reference" → "chain"` and
  `source_path: "RescueLib::'Rescue Plant'::sink_calc::throughput" → "rescue_plant.throughput"` (the
  `raw_expression` is unchanged). This is a **semantic extraction diff** — exactly what the gate's
  `[HARD]` rule says to "stop and investigate" — and it was filed under "relativization." It is **not
  Item-4-caused**: Item 4's code touches only `constraint_report.py`, `extractor.py` (manifest),
  the snapshot chain, and the dead `LiteralReal` branches (`git show --stat 501968f a627f0a`) — no
  binding resolver. So the gate's core conclusion holds, but its itemization is wrong, and the value's
  correctness is not proven by the audit (the fixture's test `test_self_named_rescue.py:56` asserts the
  downstream *resolved channel*, not the `binding_type` field; its docstring still describes the old
  full-QN `reference` form).

**Also checked and cleared:** the absolute `/home/reid/...` `document_path` in all 23 v2 snapshots is
**pre-existing** repo convention, present in the pre-epic COST-PATTERN snapshot at `d6c725f` — not an
Item-4 regression. (`self_named_rescue`'s v1 happened to hold a relative form; the recapture normalized
it to the repo-standard absolute form.)

**What this means:** the net tree is plausibly correct and the full suite is reported green on it, but
the gate's evidentiary value is diminished for a truth-item. Recommendation: re-run the six-fixture
diff and record the actual per-fixture change set (including the `self_named_rescue` binding
reclassification), and confirm that reclassification against a test that pins the field, or state
plainly it is unpinned. Two of six were independently checked; the other four were not.

### Note 2 — the fusion-tea leg of the wi014-and-fusion-tea criterion is not demonstrable here

Spec SC-1 and epic Item-4 SC-1 both read "Generating wi014_toy **and** the committed fusion-tea
snapshot emits the constraint drop report." There is **no committed fusion-tea snapshot anywhere in
this repo** (no fixture dir; the only "fusion" hits are provenance comments in
`plant_values/design.sysml:7` and `ife_plant/library.sysml:228`). fusion-tea's models live in the
separate `~/1cfe/fusion-tea` checkout and its pipeline is generated by **Item 2** (`generate --models
~/1cfe/fusion-tea/models`), which runs *after* Item 4. Consequences:

- Item 4's repo-wide recapture (23 in-repo snapshots) did not and structurally could not include
  fusion-tea. The wi014 leg is fully met; the fusion-tea leg is out of Item 4's committed scope.
- The v2 hard-gate (INV-E) now **rejects any existing v1 fusion-tea snapshot** until it is re-captured
  at v2. Item 2's SC-A/SC-4 depend on generating fusion-tea; that regen must happen on v2.

This is a cross-item dependency to flag for Item 2, not a codegen defect — but the criterion as worded
is not satisfiable in this repo today.

### Note 3 — execution + agentic-mbse verification limit (environmental)

Non-interactive sandbox: all `python`/`pytest`/`uv`/`ruff`/`mypy` invocations return "requires
approval" with no approver, and `/home/reid/1cfe/agentic-mbse` is read- and exec-blocked. Therefore
**not** independently re-verified (certified as plan-recorded only):

- both suites green (plan: codegen 2031 passed; agentic-mbse 1238);
- ruff/mypy ≤ 21/109 (plan: 20/105);
- a live run of the REQ-EXT-09 mutation check / SC acceptance generations;
- the entire agentic-mbse half: adapter TYPE_MAP contents (the "zero unmapped names" map side — the
  *used* side is verified: 22 names in codegen `src/`, `LiteralReal` correctly gone, the three new
  constraint names + OwningMembership/Subclassification/NullExpression present), rows 5–8, D6/D7,
  Level-3 circular-FAILS, and the published 8-row decision table.

Decision-table rows spot-checked against **codegen** code: row 1 (report `include_subtypes=True` +
exclude via `DROPPABLE_KINDS`) ✓; row 3 (`parameter_groups.py:102` exact-type) ✓. Row 5 (agentic-mbse
level3) not verifiable.

---

## Certification

**Verified by static inspection + git (in-sandbox):** snapshot v2 across all 23 fixtures; REQ-EXT-09
re-anchor (independent literal, part-usage leg, wi014 assert pin, executable mutation lever, require +
exclusion pins, zero-found sentinel); `collect_constraint_manifest` kind-ladder + INV-G sort + INV-C
subtree; full serialize→load→replay chain (SC "from-snapshot report available"); INV-B committed-snapshot
leg and INV-E v1-rejection tests present and license-free; INV-D cross-repo policy pin present; dead code
(constraint_extractor.py, _deserialize_constraint_info) deleted; docs (§8 rewrite, REQ-EXT-09 row with the
anti-pattern text removed, decision-table pointer, BACKLOG [CONSTRAINT-SILENCE] retired); reviewed-diff
gate independently spot-checked on 2 of 6 fixtures.

**Not verified (environmental — Note 3):** suite green, ruff/mypy, any live/dynamic run, and the entire
agentic-mbse companion branch.

**Open items for follow-up:** (1) re-itemize the six-fixture recapture diff and pin/justify the
`self_named_rescue` binding reclassification (Note 1); (2) carry the fusion-tea recapture dependency to
Item 2 (Note 2); (3) have a licensed/unsandboxed run confirm both suites green + ruff/mypy + the
agentic-mbse half before epic close.

Checkboxes: spec success criteria for the wi014/from-snapshot/REQ-EXT-09/require/enum-decision legs are
verified-by-artifact and marked; the fusion-tea leg and the agentic-mbse Level-3 leg are left unchecked
(unverified here). Plan phases left as-is (already marked complete by the implementer; codegen phases
corroborated, agentic-mbse phases not).

ARTIFACT: .project/active/subtype-enumeration/audit.md
