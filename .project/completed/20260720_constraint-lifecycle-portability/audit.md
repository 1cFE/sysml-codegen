# Audit: Lifecycle Item 5 — Whole-Tree Snapshot Portability

**Verdict:** Certify (three non-blocking notes)
**Audited:** 2026-07-20
**Branch:** constraint-exec-epic
**Commit:** `4c6223c` (code) / `570ef77` (evidence; code state identical — evidence-only commit)
**Auditor:** independent stage subagent — reproduced, did not trust

---

## Summary

Item 5 delivers what it claims. The three path-normalization schemes collapse to one certified
`root-N/` referent, the loader stops re-absolutizing, the format bumps to v5 with a load-time
shape gate that closes Item 4's N1, and the whole-tree two-root proof holds. I reproduced the
headline proof at two **fresh** roots with two fixtures the proof never used (`solar_battery`,
`fusion_tea`) — byte-identical, zero absolute-`.sysml` leaks. The licensed relocated anonymous
leg (`OccurrenceDemandAnonymous__Admitted`) is GREEN, closing Item 1's named open leg. Every
deletion the design promised is actually gone, not shimmed. The surfaced premise corrections are
honest and the "does not reach output" claim is proven, not assumed.

Three notes, none blocking: a narrow test-coverage gap on the live docstring route, a benign
sentinel-set divergence with a slightly misleading comment, and one imprecise phrasing in the
evidence about which axis gates the design-attribute-key non-portability.

## Findings

### Plan completion (phased plan in spec-design.md)

All five phases verified complete.

- **Phase 0 (RED harness):** `tests/conformance/test_whole_tree_portability.py` exists; the
  two-root diff + absolute-`.sysml` scan is the completeness gate the plan describes. Mechanism
  is sound (byte diff catches per-file divergence; `_ABSOLUTE_SYSML` regex catches an absolute
  source path while the `root-0/…` referent's inner `/` never matches).
- **Phase 1 (referent at capture):** `serializer.py` threads `model_paths` into every
  `_serialize_value` call and maps `source_file` through `map_live_source_referent`
  (`serializer.py:277`). Phase-1 stop condition honored — an unresolvable path raises
  (`_source_referent`, no silent absolutization).
- **Phase 2 (v5 + shape gate; delete re-absolutization):** `SNAPSHOT_FORMAT_VERSION = 5`
  (`snapshot/__init__.py`); `_reabsolutize_source_file(s)` deleted, replaced by
  `_validate_source_referents` (`loader.py:912`); `os` import removed (no residual usage).
- **Phase 3 (render referent; delete Branch C):** both `"models/"` string strips removed from
  `stencils.py` and `test_gen.py` (only explanatory comments remain).
- **Phase 4 (re-capture + baselines):** 36 committed snapshots all at v5; the
  `capture_pipeline_baselines.py:120` `.replace()` hack is gone.
- **Phase 5 (proof):** reproduced below.

### Spec conformance

All six success criteria met.

1. **No checkout-absolute bytes anywhere** — VERIFIED. Two-root scan returns zero absolute-
   `.sysml` hits; independent `grep` for the checkout root over every non-snapshot fixture and
   both baseline trees (`baseline_outputs`, `baseline_yaml`) returns empty.
2. **Two real roots → byte-identical tree** — VERIFIED independently. `solar_battery` (115
   files) and `fusion_tea` (47 files), each generated at two genuinely different absolute roots
   (different names and lengths), produced zero diffs. This is the falsification attempt the
   task asked for with a non-proof fixture; it holds.
3. **Item 1's relocated anonymous leg** — VERIFIED. `test_anonymous_admitted_relocated_graph_portable`
   ran licensed (passed, not skipped); admitted actual `3.0` preserved, graph+catalog identical
   across two roots + relocated copy, no checkout-absolute path.
4. **Calc-bearing + anonymous fixtures on both routes** — MET (see note N1 for the one narrow
   gap). Snapshot route: whole corpus re-captured v5, focused suites GREEN. Live route:
   constraint-id path pinned at `test_constraint_lowering_integrity.py:170` (`root-0/`), Item 4
   live-A/B/replay tests GREEN.
5. **Obsolete branches deleted, not shimmed** — VERIFIED. `_reabsolutize` absent from `src/`
   and `tests/`; Branch C strips gone; baseline `.replace()` gone; no replacement normalization
   layer added. Three schemes → one `root-N/` authority.
6. **Route-parity not regressed** — MET (transitive). Item 4 portability/identity pins GREEN
   (9 passed); A2 compares graph/catalog wiring across routes, not just absence of absolute bytes.

Non-goals respected — no schema expansion beyond the referent, no Item 4 re-audit (the
`SNAPSHOT_MANIFEST_SHA256` pin is unchanged and GREEN), no historical-snapshot work.

### Design conformance

Implementation follows D1 + v5 as ratified.

- **D1 (generalize `root-N/`):** `map_live_source_referent` applied at capture; the v5 shape
  gate reuses the certified `validate_snapshot_source_referent`. Live route mirrors it in
  `graph_builder` Step 7.5 (`_apply_module_source_referents`) and `pipeline_builder`
  (`source_location_mode="live"`).
- **v5 shape gate closes N1:** both skew directions reject loudly — an absolute `source_file`
  (`test_absolute_source_file_rejected`) and a bare snapshot-dir-relative path
  (`test_snapshot_dir_relative_source_file_rejected`, the exact value a silent v4 edit would
  have passed). Both raise `SnapshotFormatError` matching "portable". Version skew fails both
  directions. Reproduced: focused gate suites 13 passed.
- **Anonymous eligible constraint_id folds the referent** (`constraint_lowering.py`): derived
  once in `prepare_constraint_usages` (I10), carried on the transcript, folded in
  `_source_local_identity`. Verified zero Item-4 impact — `catf_mfe` has 65 constraint usages,
  **0** anonymous-with-location, so no id moves and the Item 4 manifest pin is untouched.
- **Deletion inventory** matches reality item-for-item.

### Code integrity

No correctness or failure-honesty defects. The failure posture is right: on both the live and
snapshot routes an unresolvable/absolute `source_file` **raises** rather than falling back to an
absolute path (the Phase-1 stop condition), pinned at `test_constraint_lowering_integrity.py:195-219`
(three distinct loud-failure paths) and by the shape gate. Freshness went inert on the referent
without a shim.

**N1 — test-coverage (minor).** No test *explicitly* pins the live `--models` module-**docstring**
`source_file` as a `root-N/` referent, nor asserts live==snapshot docstring byte-parity for a
generated tree. The machinery is exercised transitively (licensed integration tests call
`build_pipeline_context` → Step 7.5; they would fail if it raised) and is fail-loud, so it
cannot silently leak — worst case is a crash, not a bad byte. The constraint-*id* live route is
pinned; the module-*docstring* live route is covered only indirectly. Recommend a small licensed
live-vs-snapshot docstring-parity assertion when convenient. Not blocking.

**N2 — maintenance (minor).** `graph_builder._SOURCE_SENTINELS = {"unknown","hierarchy","unknown.sysml"}`
diverges from `loader`/`serializer._SOURCE_SENTINELS = {"unknown","hierarchy"}`, under a comment
saying "kept in sync with loader._SOURCE_SENTINELS." The divergence is deliberate and benign —
`"unknown.sysml"` is a graph-layer-only mint (derived-group/hierarchy modules) that never reaches
the serializer, and both routes render it consistently. The "kept in sync" phrasing could mislead
a future editor into "fixing" the mismatch. Recommend the comment state the extra token is
graph-layer-only.

**N3 — evidence phrasing (minor, record-only).** Surfaced finding #2 says the design-attribute-key
/ `document_path` non-portability is "gated by the two-root diff." Strictly, the diff axis
*cancels* for a snapshot-baked absolute (identical snapshot bytes on both sides), so it cannot
catch such a value reaching output — the absolute-byte *scan* axis is the real gate, and I
confirmed it independently by grepping the committed corpus. Finding #1 shows the implementer
understands this exact masking (the from-snapshot inventory masking the anonymous-id leak), so
this is imprecise wording, not a misunderstanding. The claim "does not reach output" is **proven**
(scan + grep empty), not assumed, for the committed corpus.

---

## Independent reproduction log

| Check | Result |
|---|---|
| Two-root whole-tree, `solar_battery` (fresh roots, not proof fixture) | diff 0/115, abs hits 0 |
| Two-root whole-tree, `fusion_tea` (fresh roots) | diff 0/47, abs hits 0 |
| Shape gate both skews + version gate (`test_source_referent_shape_gate`, `test_snapshot_v5_gate`) | 11 passed |
| Whole-tree A1 (license-free) + A2 relocated anonymous (**licensed, not skipped**) | 2 passed |
| Item 4 pins (`test_constraint_snapshot_portability` + `_identity`) | 9 passed; manifest SHA unchanged |
| Deletion greps (`_reabsolutize`, Branch C, `.replace()`, `os`) | all absent |
| Snapshot census | 36 fixtures, all v5 |
| Recapture field-classification (`wi014_toy` vs parent) | deltas exactly {source_file, captured_at, location.file, version} |
| catf_mfe anonymous-located usages | 0 (confirms zero Item-4 impact) |
| Checkout-root in any non-snapshot fixture/baseline | none |
| design_attr keys / document_path in snapshot | keys still absolute (surfaced, honest); document_path None; neither reaches output |
| Execution lane (`pytest -m execution`, agentic-mbse venv + teax-simkit) | 17 passed |
| `-O` parity on changed surface (8 files) | 58 passed |
| ruff (changed src) | clean |
| mypy `src/` | 72 (matches baseline, zero added) |

## Deferred-item assessment (task priority 7)

- **Execution lane** — run, GREEN (17 passed). The evidence deferred it under budget; it holds.
- **`-O` parity** — run on the Item 5 changed surface, GREEN (58 passed). The orchestrator
  already verified `-O` parity on core files; this confirms the changed test surface too.
- **Full-suite confirming run** — the orchestrator verified the full licensed suite 3063/0 with
  zero license skips at the candidate; not re-derived here (no finding depends on it).
- **D3 (param-group basename → referent)** — deferral is **sound**. `entry_point.py:226` still
  renders the bare basename (`Parameters from <basename>.`), which is already root-independent;
  the two-root scan found zero leaks in `inputs/` and `*_params.py`. D3 is a disambiguation
  nicety, not a portability fix, and folding it would churn baselines for no portability gain.
  Honestly surfaced as a deviation from the phased plan.

## Certification

Marked as verified:
- Spec success criteria 1–6 (`spec-design.md`) — all reproduced first-hand.
- Epic Item 5 success criteria (4) — met; ✅ appended to the Item 5 heading.

**Not checked:**
- The full licensed suite was **not** re-run end-to-end (relied on the orchestrator's 3063/0 at
  the candidate; my independent coverage is the focused portability/gate/Item-4/execution/`-O`
  surface above, ~99 tests).
- Live `--models` whole-tree docstring byte-parity is not independently pinned (see N1); I
  verified the machinery is exercised and fail-loud, not that a licensed live tree is
  byte-identical to its snapshot tree field-by-field.
- The stale-baseline class (`plant_values`, `constraint_inline`) was accepted per the recorded
  pattern from evidence, not re-reproduced on the parent commit this pass.
- agentic-mbse-side state (pin `4c18d61`) unchanged by this item and not re-audited.
