# Audit: Snapshot v3 — Constraint Facts Load-Bearing (Item 8)

**Verdict:** Certify
**Audited:** 2026-07-13
**Branch:** constraint-exec-epic
**Commit:** df5ed97 (item span `1a5c591..df5ed97`)

---

## Summary

Item 8 makes the neutral `ConstraintFacts` a load-bearing, versioned snapshot section, re-lowers
from it offline (genuine re-derivation, not carriage), rejects stale/sectionless snapshots loudly,
and flips `lower_constraints_enabled` to default True behind a named grandfather set. The
implementation matches design rev 2 file-for-file, all five spec success criteria are met, and the
5+5 test fixups are legitimate re-anchors, not weakened assertions. Verification combined my static
code/git inspection with an orchestrator-executed probe set (I could not run tests in my own
session; the orchestrator ran them and returned results, cited explicitly below).

## Evidence provenance

Two classes of evidence back this audit:

- **Static (my session):** code reads, git diffs, and fixture-content greps — all read-only, all
  run by me directly.
- **Orchestrator-executed probes:** all test/mypy/ruff execution. My session's permission layer
  denied every code-execution form (`uv run`, bare `pytest`, `python -m pytest`, direct
  `.venv/bin/pytest`), the license `.env` sits outside the sandbox working dir (unreadable), and
  the brief's `env $(…)` license form is statically blocked as command-substitution. The
  orchestrator ran the probe set and returned results verbatim; those are cited as
  **[orchestrator-executed]** wherever relied upon. I did not fabricate or infer any test outcome.

## Findings

### Plan completion

All five phases verified complete against their recorded changes and deviations.

- **Phase 1 (de-risk spike).** `RecordingOccurrenceIndex`/`FrozenOccurrenceIndex`/`OccurrenceIndex`
  Protocol + `deserialize_part_occurrences` in `part_instance_index.py`; recorder wired at
  `pipeline_builder.py:875`; `part_occurrences` on `PipelineContext`. Round-trip+parity test
  present (`test_occurrence_roundtrip_parity.py`). **[orchestrator-executed]** part of the 15-passed
  gate+parity run.
- **Phase 2 (serializer + gate).** `SNAPSHOT_FORMAT_VERSION = 3` and the mode constants
  (`snapshot/__init__.py:19,26-29`); serializer writes the three keys with sorted owner keys;
  loader's eight-step gate (`loader.py:156-210`). Full 8-cell rejection matrix in
  `test_snapshot_v3_gate.py`.
- **Phase 3 (offline re-lowering).** Constraint phase dispatched on the load-validated mode at
  `graph_rebuild.py:189-224`, including the pulled-forward P4 catalog assembly (`:207-213`) so
  from-snapshot artifacts match live. Parity test compares full graph bytes + catalog.
- **Phase 4 (default flip + grandfather).** Defaults True at `pipeline_builder.py:705` and
  `capture.py:24`; `GRANDFATHERED` frozenset at `capture_extraction_snapshots.py:129`, routed
  through the MODELS loop (`:240`). Carve-out test present.
- **Phase 5 (corpus re-capture).** Every committed extraction snapshot re-captured at v3 (37
  fixture files in the item diff); `constraint_inline`/`constraint_multi_instance` added with
  committed snapshots + baselines. Deviations (Layer C yaml, d38_caret drift, self-reverting
  filter test, module-kind test fixups) all logged in the plan and independently checked below.

No placeholder code, TODOs, or partial implementations found in the item's src surface.

### Spec conformance — success-criteria walk

- [x] **SC-1: Both rejection cases fire with re-capture messages.** Old-version snapshot → version
      hard-gate (`loader.py:149-154`); v3 missing the constraint-facts section → the new
      `_require(raise_on_missing=True)` gate (`loader.py:159-167`), raising `SnapshotFormatError`,
      never loading as an empty catalog, never a `KeyError`. Both are pinned by tests
      (`test_snapshot_v3_gate.py` cells a–d). **[orchestrator-executed]** the mode-enum mutation
      probe (delete `loader.py:193-199` → cells h1/h2 FAIL, 2 failed/8 passed; revert → 10 passed)
      empirically proves the gate has teeth — the test is not vacuous.
- [x] **SC-2: Constraint-bearing fixture byte-identical live vs from-snapshot.** `wi014_toy`,
      `constraint_multi_instance`, `constraint_inline` proven via `test_snapshot_constraint_parity.py`,
      which compares the full `ComputationGraph.model_dump_json()` (modules, entry points, execution
      order, the CONSTRAINT/REPORT_AGGREGATOR nodes) plus catalog `constraint_id`s, order, and
      fingerprint. This is artifact/graph-level identity (the level the spec scopes; emitted-`.py`
      parity is Item 7's). **[orchestrator-executed]** in the 15-passed gate+parity run.
- [x] **SC-3: Re-captured corpus shows only expected diffs; conformance green.** Constraint-free
      fixtures gain only the three new keys + version (verified: `sample_model` = present-empty
      `"usages": []`, `part_occurrences: {}`, `mode: "applied"`). Clean constraint fixtures gain
      occurrences + `mode: "applied"` (verified: `wi014_toy`/`constraint_multi_instance` have
      non-empty tables). The two grandfathered fixtures stay un-lowered (below). One out-of-band
      diff (`d38_caret`) investigated and cleared as pre-existing drift (see Design conformance).
      **[orchestrator-executed]** full suite 2256 passed / 4 skipped / 7 deselected.
- [x] **SC-4: Default flips under the parity gate.** `lower_constraints_enabled` defaults True on
      both surfaces (`pipeline_builder.py:705`, `capture.py:24`); the from-snapshot path lowers
      from carried facts (`graph_rebuild.py:196`). The transitional comment block retired (the
      `:856-863` region is now the Phase-4 rationale note). The 22 corpus-wide divergences are
      eliminated as the suite's baseline — **[orchestrator-executed]** full suite green confirms.
- [x] **SC-5: The two `gain`-blocked fixtures grandfathered honestly.** `plant_values` and
      `fusion_tea` captured flag-off: both snapshots carry `constraint_lowering_mode:
      "grandfathered_off"` with **honest non-empty facts** (not empty — verified: neither shows
      `"usages": []`) and empty `part_occurrences: {}`. Their `baseline_outputs/` are
      **byte-identical across the entire item** (empty `git diff --stat 1a5c591~1..df5ed97` on both
      dirs). The exclusion set is named and visible (`GRANDFATHERED`, `capture_extraction_snapshots.py:129`).
      The `gain` gap is handed to Item 14 as a named prerequisite (spec Known Requirements, honored
      as a Non-Goal here — `materialize_supplied_values` untouched).

### Spec tagged-requirement conformance

- **[HARD] facts round-trip lossless / byte-stable:** loader embeds via `constraint_facts.parse`,
  serializer via `json.loads(serialize(facts))`; round-trip byte-identity asserted
  (`test_snapshot_v3_gate.py::test_facts_and_occurrences_roundtrip_byte_identical`). Met.
- **[HARD] pin both schema versions:** data-level facts-version check (`loader.py:174`) + embedded
  expression-ir scan (`loader.py:180-192`, `_scan_expression_ir_versions`) + code-pin asserts
  (`:203-210`). Met.
- **[HARD] version bump 2→3, no coexistence:** `SNAPSHOT_FORMAT_VERSION = 3`; every committed
  snapshot re-captured (INV-6). Met.
- **[HARD] two rejection cases raise, not degrade:** the new gate raises `SnapshotFormatError`,
  explicitly not following the `compilation_results` degrade-with-warning precedent. Met.
- **[INFERRED] present-and-empty vs absent distinction:** section always written even when empty;
  absent → raise, present-empty → load. Verified via `sample_model` (present-empty) vs the
  drop-key gate cells. Met.
- **[HARD] lowering wired into `build_full_graph_from_snapshot`, P3 extend runs:**
  `graph_rebuild.py:196-213`. Met.
- **[INHERITED] `constraint_id`/catalog byte-identical across paths:** SC-2 parity test. Met.
- **[NEED] default flip + [INFERRED] carve-out:** SC-4/SC-5 above. Met.
- **[HARD] corpus re-capture discipline:** Phase 5 followed the timestamp-churn discipline
  (n/a this phase — every fixture had substantive class-1–4 changes); the two known stale baselines
  (`deep_cross_scope_probe`, `ife_plant`) reviewed and show only the three new keys. Met.

**Non-goals respected:** no constraint code emission (Item 7), no facts-schema change (Item 1), no
`materialize_supplied_values` touch (Item 14), no fingerprint sealing (Item 9). Confirmed — the
item's src diff touches only the ten design-named files.

### Design conformance

Implementation follows design rev 2. Spot-checked deviations, all sound:

- **d38_caret out-of-band diff (the one non-class diff):** the dropped `"unhandled": false` on a
  `BindingInfo` dict traces to commit `891cf8e` ("item5 Phase 1"), confirmed an **ancestor of the
  Item-8 parent** (`git merge-base --is-ancestor` → true). Item 8's src diff touches no
  binding/extraction serializer (only the ten snapshot/constraint files), and no other fixture
  retains `"unhandled"` (`grep -rl` → empty). Pre-existing re-capture catch-up, reproduces on the
  parent, not Item-8-introduced. Root-cause note verified.
- **P4 catalog pulled forward into the offline path** (`graph_rebuild.py:207-213`): a deviation from
  the original plan task list, logged, and correct — generation reads the catalog from the graph, so
  from-snapshot artifacts diverge from live without it. Mirrors live P4.
- **Offline dispatch is total** (`graph_rebuild.py:196-222`): `applied`/`grandfathered_off` only, no
  third branch — safe because the loader validated the enum. This is exactly what makes the
  mutation probe meaningful (delete the loader guard → an unknown mode silently no-ops here).

All eight INV invariants have a corresponding code + test locus; INV-4 (offline never builds the
live index) is pinned by a grep-based regression test (`test_snapshot_constraint_parity.py:79`).

### Code integrity

No slop or failure-honesty findings.

- The `mode`-keyed dispatch is a clean two-arm total function, not a sentinel-parameter god function.
- The new gate **raises** on every corruption cell — no silent fallback, no broad `except`, no
  compat shim. It deliberately does *not* reuse the `compilation_results` degrade-with-warning path.
- `FrozenOccurrenceIndex` raises on a missing key (corruption), never returns `[]` — the design's D2
  no-silent-`[]` rule, verified in `part_instance_index.py` and by the Phase-1 negative test.
- The 5+5 test fixups are re-anchors, not weakenings (checked each diff):
  - *Phase-4 five* make the previously-implicit off-by-default explicit; one
    (`test_wired_pipeline_path_lowers_by_default_and_is_inert_when_disabled`) **adds** a default-True
    assertion. Assertions unchanged otherwise.
  - *Phase-5 five*: the two count tests keep exact equality with new terms added
    (`+ constraint_count + report_aggregator_count`, `+ constraint_schema_imports`); the three
    exemptions carve out module kinds whose conventions genuinely don't apply (a graph-wide
    singleton channel with no PQN; modules with no source calc_def). The
    `fusion_tea`/`plant_values` parity-leg rewrites assert the now-intended live `gain` halt
    (spec SC-5 / design D3 sub-bullet) instead of an unprovable byte-diff — an honest re-anchor to
    the new, specified behavior, thoroughly annotated and cross-referenced to the carve-out test.

---

## Certification

**Checked and verified:**
- The eight-step load gate and its full 8-cell rejection matrix (code + test), with the mode-enum
  cell empirically proven load-bearing by the **[orchestrator-executed]** mutation probe.
- Live/snapshot artifact parity (full graph bytes + catalog id/order/fingerprint) on the three
  clean fixtures — **[orchestrator-executed]** 15-passed gate+parity run.
- The default flip on both surfaces; the named grandfather set; the two grandfathered snapshots'
  markers + honest non-empty facts + empty tables; their baselines byte-identical across the item.
- Per-fixture corpus shape (constraint-free present-empty, clean fixtures gained occurrences,
  grandfathered flag-off) via fixture-content greps.
- The d38_caret out-of-band diff as pre-existing, parent-reproducing drift (git ancestry + no
  Item-8 serializer touch + corpus-wide isolation).
- The 5+5 test fixups, each read as a legitimate re-anchor.
- Gates: **[orchestrator-executed]** full suite 2256 passed / 4 skipped / 7 deselected; mypy 76
  (= baseline, no new errors); ruff clean.

**SC-4 handoff to Item 9 (fingerprint-stability canary):** Item 9's canary depends on this item's
parity holding. It now does — live and from-snapshot generation produce byte-identical graph
structure and an identical catalog fingerprint on the clean fixtures (SC-2, executed green), and the
corpus is coherent at v3 under the flipped default (SC-3/SC-4, full suite green). **Item 9's
fingerprint-stability preconditions are satisfied.** One boundary to carry forward, already stated
in the design (NH4): offline lowering trusts the frozen occurrence table with no live cross-check, so
a model edited-but-not-recaptured lowers against stale occurrences — Item 9's sealing is where that
staleness becomes a hard boundary, not this item's concern.

**Not checked:**
- **Emitted-artifact (`.py`/YAML) live-vs-snapshot parity** — out of scope for Item 8, which proves
  parity at graph/catalog identity; Item 7's own success criterion re-proves it at the emitted level.
- **The `gain` hierarchy-extraction gap itself** — deliberately untouched (Item 14 prerequisite); I
  confirmed only that it is *not* touched and that the grandfather correctly routes around it.
- **The 22 divergences enumerated individually** — I confirmed they are eliminated as a class via the
  full-suite green result (the spec's own framing: parity fixtures ≠ the 22; the suite carries them),
  not by walking each of the 22 divergence sites.
- **I did not re-run any probe in my own session** — all execution results are orchestrator-supplied
  and cited as such; my independent contribution is the static code/git/fixture verification that
  corroborates them and the reasoning that makes the executed results interpretable (e.g. why the
  mutation probe cell is the right one, why the parity comparison is byte-level).
