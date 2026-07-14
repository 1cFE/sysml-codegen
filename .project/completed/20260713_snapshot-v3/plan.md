# Implementation Plan: Snapshot v3 — Constraint Facts Load-Bearing

**Status:** Complete
**Created:** 2026-07-12
**Last Updated:** 2026-07-13
**Epic:** CONSTRAINT-EXEC — Item 8
**Branch:** constraint-exec-epic

## Source Documents

- **Spec:** `.project/active/snapshot-v3/spec.md`
- **Design:** `.project/active/snapshot-v3/design.md` ← component details, bets, decisions, the
  mode×section matrix, and every file:line anchor live here. This plan does **not** repeat them.
- **Design review:** `.project/active/snapshot-v3/design-review.md` — Approved-with-must-fixes;
  all four must-fixes (MF1 three-key gate, MF2 mode-enum validation, MF3 recorded-transcript table,
  MF4 pinned key order) are already folded into design rev 2 and are what the tests below pin.

## Implementation Strategy

**Phasing rationale.** The whole item rests on one bet: serialized occurrences reload
byte-identical, so offline re-lowering re-derives byte-identical `constraint_id`s
(design.md#key-bets B2, the highest-risk new surface). Everything else — the gates, the mode
enum, the corpus re-capture — is mechanical once that bet holds. So **Phase 1 is a vertical spike
that collapses that one uncertainty on the smallest reproducing fixture** (`constraint_multi_instance`,
the per-occurrence-expansion shape) before any serializer or loader surgery. If it fails, the
frozen-table shape (design.md#key-decisions D1) is what to revisit, and we've spent one phase, not five.

After the bet holds, the work is a straight line:

- **Phase 2** — version bump, serializer writes the three keys, loader gates all three + validates
  the mode enum + the embedded expression-ir version (the full rejection matrix). This closes the
  silence trap.
- **Phase 3** — wire offline lowering into the from-snapshot rebuild, gated on the load-validated
  mode; prove end-to-end live/snapshot parity on all three clean fixtures.
- **Phase 4** — flip the default True on both surfaces together, behind the named grandfather set,
  so the corpus stays coherent through the flip.
- **Phase 5** — re-capture the corpus per-fixture under the timestamp-churn discipline, with the
  expected-diff enumeration as the review checklist.

**Critical path:** Phase 1 proves B2 → Phase 2 makes facts load-bearing (version-gated) → Phase 3
re-lowers offline → Phase 4 flips the default → Phase 5 re-captures. Phases 2–5 are strictly
ordered; Phase 1 is independent and green on its own.

**First proof point:** the `constraint_multi_instance` occurrence round-trip + `constraint_id`
parity test in Phase 1. That single test tells us the occurrence-table bet holds.

### ⚠️ Surfacing: the corpus goes RED between Phase 2 and Phase 5 — this is inherent, not a bug

INV-6 (design.md#required-invariants) forbids v2/v3 coexistence: the loader hard-gates on the
version (`loader.py:127-140`). The moment Phase 2 bumps `SNAPSHOT_FORMAT_VERSION` to 3, **every
committed v2 snapshot fails to load**, so every test that loads a committed snapshot (conformance,
pipeline-baseline) goes RED and stays RED until Phase 5 re-captures the corpus at v3. This is the
"single atomic change" the design calls out (design.md#integration-strategy), split across phases
for reviewability.

Consequence for the phase gates, stated plainly so no one mistakes a red suite for a regression:

- **Phases 2, 3, 4 gate on their own targeted tests** (the new rejection/round-trip/parity/grandfather
  tests, plus non-snapshot-loading unit tests), **not** on full-suite green.
- **Full-suite green is Phase 5's gate**, after re-capture.
- Phase 1 is green on the full suite (it touches no version/serializer/loader code and runs under
  the still-False default).

If the orchestrator's commit policy needs every committed state green, the alternative is to fold
Phase 5's re-capture into Phase 2's commit (version bump + re-capture atomic). The orchestrator's
brief explicitly orders re-capture **last**, so this plan follows that and accepts the mid-epic red.

## Environment Setup

See CLAUDE.md. Key commands for this item:

- Full suite: `uv run pytest tests/`
- Single file/test: `uv run pytest tests/unit/test_hygiene_tail_loader.py -k <name>`
- Type check: `uv run mypy src/` (project baseline is dirty ~77; gate is **no new errors**)
- Lint: `uv run ruff check src/`
- Live capture (stage session has a working license):
  `uv run python scripts/capture_extraction_snapshots.py --fixtures <name>`
  then `uv run python scripts/capture_pipeline_baselines.py --fixtures <name>`
- Timestamp-churn revert discipline: memory `byte-identity-captured_at-churn` (Phase 5).

---

## Phase 1: De-risk spike — occurrence round-trip + `constraint_id` parity (`constraint_multi_instance`)

### Goal
Prove, on the smallest per-occurrence-expansion fixture, that a serialized occurrence table
reloads byte-identical and drives the **real** `lower_constraints()` offline to byte-identical
`constraint_id`s. Land it as a **kept test**, not a throwaway spike. Build only what this proof
needs; defer the full snapshot serializer/loader/gate/mode/flag to later phases.

### Why first
It collapses the one bet everything else rests on (B2 + B1, design.md#key-bets) before any
serializer surgery. A divergence here means the frozen-table shape (D1) is wrong — cheapest to
learn now. The design's own de-risk-first note (design.md#next-stage-handoff) mandates exactly this.

### Assumption Under Test
- **B2** — serialized `InstanceOccurrence`s reload byte-identical (frozen-dataclass equality),
  so re-derived `constraint_id`s are byte-identical.
- **B1** — the only live-model dependency in lowering is `occ_index.occurrences_of`; a frozen
  table replaces the live model with nothing else missing.

### Test Stencil (write first)
```python
# tests/unit/test_occurrence_roundtrip_parity.py  (NEW)
def test_multi_instance_occurrence_roundtrip_and_constraint_id_parity():
    # --- live leg: capture the occurrence table as the lowering transcript (MF3) ---
    ctx = build_pipeline_context([FIXTURES / "constraint_multi_instance"],
                                 lower_constraints_enabled=True)   # opt in explicitly
    live_ids = sorted(c.constraint_id for c in ctx.concrete_constraints)
    table = ctx.part_occurrences            # recorded by RecordingOccurrenceIndex at P1

    # --- round-trip the two identity-bearing inputs ---
    facts_json = json.loads(constraint_facts.serialize(ctx.constraint_facts))
    occ_json = _serialize_value(table)      # dataclasses -> dicts, tuples -> lists
    reloaded_facts = constraint_facts.parse(json.dumps(facts_json))
    reloaded_table = deserialize_part_occurrences(occ_json)
    assert reloaded_table == table          # INV-2 occurrence equality, byte-for-byte

    # --- offline leg: real lower_constraints through the frozen index ---
    frozen = FrozenOccurrenceIndex(reloaded_table)
    concrete = lower_constraints(reloaded_facts, occ_index=frozen,
                                 registry=..., design_attrs=..., calc_usages=...)
    assert sorted(c.constraint_id for c in concrete) == live_ids   # B2 parity
```
(The `registry`/`design_attrs`/`calc_usages` for the offline leg come from the same `ctx`; this
phase reuses the live-derived inputs so the test isolates the occurrence/facts round-trip. Phase 3
re-derives them from a real snapshot — the end-to-end version.)

### Changes Required

**See design.md for:** the occurrence-table concept (design.md#core-concept); the two thin wrappers
(design.md#component-overview); B1/B2 (design.md#key-bets).

- [x] **`analysis/part_instance_index.py`** — add `RecordingOccurrenceIndex` (wraps a live
      `PartInstanceIndex`, delegates `occurrences_of`, records each `owner_eqn → result` into
      `.recorded`) and `FrozenOccurrenceIndex` (holds the table, `occurrences_of(qn)` = dict lookup,
      **raises on a missing key** — corruption, never `[]`, per design.md#key-decisions D2). Added
      the `OccurrenceIndex` Protocol; `constraint_lowering.lower_constraints`/`_expand_owner_instances`
      now type `occ_index` as `OccurrenceIndex` (mypy clarity, duck-typed at runtime).
- [x] **`analysis/part_instance_index.py`** (or a sibling `serialize` helper) — `deserialize_part_occurrences(dict) -> dict[str, list[InstanceOccurrence]]`
      rebuilding `InstanceOccurrence(part_def_qn, steps=tuple(PathStep(...)))` from the serialized
      shape. Serialization is `_serialize_value` (no hand-rolled dicts — `InstanceOccurrence`/`PathStep`
      are plain frozen dataclasses; design.md#implementation-notes).
- [x] **`orchestration/pipeline_builder.py:865`** — inside the existing
      `if lower_constraints_enabled and constraint_facts.usages:` block, wrap the already-built
      `occ_index` in `RecordingOccurrenceIndex(occ_index)` and pass the **wrapper** to
      `lower_constraints(..., occ_index=recorder, ...)`. After the call, `recorder.recorded` is the
      table (MF3 — inherits lowering's exact `part_def`-kind + `ADMIT`-eligible filter, no second
      owner-selection path). A `NonFiniteCardinalityError` still surfaces from the real call and
      halts, same as today.
- [x] **`orchestration/pipeline_context.py`** — added `part_occurrences` field; `constraint_facts` was
      already a field (Item 5) and is now **always** populated (dropped the
      `if constraint_facts.usages else None` guard) so snapshot v3 can serialize an honest facts
      section for every model, constraint-bearing or not (design.md#component-overview D4). No
      downstream reader relied on the old None-when-empty behavior (grepped clean). The
      `constraint_lowering_mode` field lands in Phase 2 with the serializer.
- [x] **Test file** `tests/unit/test_occurrence_roundtrip_parity.py` (NEW) — the stencil above,
      plus one negative assertion that `FrozenOccurrenceIndex.occurrences_of("nonexistent")` raises.

### Validation
**Automated:**
- [x] `uv run pytest tests/unit/test_occurrence_roundtrip_parity.py` → passes (both the round-trip +
      parity test and the missing-owner negative test, on the first run — B1/B2 held with no
      surprises)
- [x] `uv run pytest tests/` → **full suite green**: 2238 passed, 4 skipped (2236 baseline + 2 new)
- [x] `uv run ruff check src/`; `uv run mypy src/` → clean; mypy 76 errors, identical to baseline
      (no new errors)

**Manual:**
- [x] Confirm the recorded table has one entry per queried `part_def`-kind owner and the occurrence
      lists match `occurrences_of` sort order (spot-check against the fixture's two instances).
      Verified indirectly: the round-trip assertion `reloaded_table == table` is frozen-dataclass
      equality over the full table, and the parity assertion proves the recorded occurrences drive
      offline lowering to the same 3 `constraint_id`s as live — a sort or content divergence would
      have failed either assertion.

**What we know works after this phase:** the occurrence-table bet (B2) holds on the multi-instance
shape — offline re-lowering from carried inputs re-derives byte-identical `constraint_id`s. The
frozen-table shape (D1) is validated before we build the format around it.

---

## Phase 2: Serializer writes the three keys; loader gates them + validates the mode enum

### Goal
Make `ConstraintFacts` a load-bearing, versioned snapshot section: bump v2→v3, serialize the three
new keys, and gate all three at load with the full rejection matrix — closing the silence trap
(MF1, MF2). No offline lowering yet; this phase is capture + reject.

### Why now
Phase 1 proved the payload round-trips. Now make it a real snapshot section with a loud boundary,
so Phase 3 has a v3 snapshot to re-lower from.

### Assumption Under Test
The `_require(raise_on_missing=True)` version-gate idiom (design.md#architecture, `loader.py:53-79`)
extends cleanly to a three-key + enum + embedded-version gate, and Item 1's canonical facts JSON
re-dumps deterministically through `snapshot_to_json` (design.md#implementation-notes "Facts embedding").

### Test Stencil (write first — the rejection matrix, mirroring `test_hygiene_tail_loader.py`)
```python
# tests/unit/test_hygiene_tail_loader.py  (EXTEND)
@pytest.mark.parametrize("mutate, match", [
    (drop_key("constraint_facts"),          "constraint_facts"),        # (b) MF1
    (drop_key("part_occurrences"),          "part_occurrences"),        # (c) MF1
    (drop_key("constraint_lowering_mode"),  "constraint_lowering_mode"),# (d) MF1
    (strip_facts_schema_version,            "schema_version"),          # (e) torn facts dict
    (set_facts_version("constraint-facts/v2"), "constraint-facts"),     # (f) data pin
    (set_embedded_ir_version("expression-ir/v2"), "expression-ir"),     # (g) NH5 data pin
    (set_mode("off"),                       "constraint_lowering_mode"),# (h) MF2 unknown enum
    (set_mode(""),                          "constraint_lowering_mode"),# (h) empty
])
def test_v3_corruption_raises_with_recapture_message(v3_snapshot, mutate, match):
    bad = mutate(v3_snapshot)
    with pytest.raises(SnapshotFormatError, match=match):
        load_extraction_snapshot(write_tmp(bad))
    # never a raw KeyError; message ends with a re-capture instruction

def test_v2_snapshot_rejected_by_version_gate(v2_snapshot):   # (a) the bump alone
    with pytest.raises(SnapshotFormatError, match="snapshot_format_version"):
        load_extraction_snapshot(write_tmp(v2_snapshot))

def test_facts_section_roundtrips_byte_identical(v3_snapshot):   # INV-2
    reloaded = load_extraction_snapshot(write_tmp(v3_snapshot))
    assert snapshot_to_json(reserialize(reloaded)) contains the identical facts bytes
    assert reloaded["part_occurrences"] deserialize == captured occurrences
```

### Changes Required

**See design.md for:** the format (design.md#architecture "Snapshot format v3"); the eight-step
load order (design.md#architecture "Load / rejection"); the mode×section matrix
(design.md#architecture); the gate-message idiom and facts-embedding note (design.md#implementation-notes);
D5 (design.md#key-decisions).

- [x] **`snapshot/__init__.py:15`** — `SNAPSHOT_FORMAT_VERSION = 3`; update the version comment.
      Added the mode constants: `CONSTRAINT_LOWERING_MODE_APPLIED = "applied"`,
      `CONSTRAINT_LOWERING_MODE_GRANDFATHERED_OFF = "grandfathered_off"`,
      `VALID_CONSTRAINT_LOWERING_MODES = frozenset({...})`.
- [x] **`orchestration/pipeline_context.py`** — added the `constraint_lowering_mode` field (Phase 1
      added the other two). Populated in `build_pipeline_context`: `"applied"` when
      `lower_constraints_enabled=True`, `"grandfathered_off"` otherwise (Phase 4 routes the flag —
      for now this tracks the same flag that gates lowering itself).
- [x] **`snapshot/serializer.py`** — `serialize_extraction_snapshot` writes the three keys:
      `constraint_facts` = `json.loads(constraint_facts.serialize(facts))` (canonical bytes preserved,
      not re-derived); `part_occurrences` = `_serialize_value(occurrences, output_dir)` per owner with
      **`sorted()` owner keys** (INV-7 / MF4); `constraint_lowering_mode` = the mode string (always
      present, now a required keyword param — no default, since design mandates it's never absent).
- [x] **`snapshot/capture.py:44`** — pass `ctx.constraint_facts`, `ctx.part_occurrences`,
      `ctx.constraint_lowering_mode` into `serialize_extraction_snapshot` (with an `assert
      ctx.constraint_facts is not None` for mypy narrowing — build_pipeline_context always populates it).
- [x] **`snapshot/loader.py`** (after the version gate) — the eight-step order from
      design.md#architecture: (2) all three keys via `_require(raise_on_missing=True)`; (3) facts is
      a dict carrying `schema_version` (torn dict raises here, not downstream); (4) facts
      `schema_version == CONSTRAINT_FACTS_SCHEMA_VERSION`; (5) scan embedded predicate nodes for
      `expression-ir/*` `schema_version` via new `_scan_expression_ir_versions` (NH5 — a shallow
      recursive token scan), any `!= EXPRESSION_IR_SCHEMA_VERSION` raises; (6) `mode ∈
      VALID_CONSTRAINT_LOWERING_MODES` else raise (MF2); (7) code-pin asserts for both version
      constants (mirrors `PROFILE_SEMANTIC_VERSION` at `constraint_lowering.py:463`); (8) deserialize
      facts via `constraint_facts.parse`, occurrences via `deserialize_part_occurrences` (Phase 1),
      mode string — joined into the `snap` dict.
- [x] **Parse-entry decision (design open question) resolved:** `constraint_facts.parse(json.dumps(section))`
      IS byte-exact — `test_facts_and_occurrences_roundtrip_byte_identical` proves it. No dict-taking
      `parse` entry needed.
- [x] **Test file** — new `tests/unit/test_snapshot_v3_gate.py` (not an extension of
      `test_hygiene_tail_loader.py`, which tests individual deserializer helpers on hand-built dicts —
      this needs the full `load_extraction_snapshot` gate on a full snapshot dict, matching
      `test_snapshot_contract.py`'s style instead) with the matrix stencil (cells a–h), the v2-rejection
      test, and the round-trip test. Built the v3 fixture by hand-bumping the still-v2 committed
      `chain_spike_model` snapshot + a locally-constructed `ConstraintFacts` (one package-owned admitted
      assert, license-free, mirrors `test_constraint_lowering.py`'s non-license-gated builders) so cell
      (g)'s embedded expression-ir scan has a real node to corrupt.
- [x] **Deviation (pulled forward from Phase 4):** `scripts/capture_extraction_snapshots.py`'s
      `_capture_extraction_only` now also passes the three new params (facts via
      `extract_constraint_facts`, mode `grandfathered_off`, empty table) — done now rather than in
      Phase 4, because Phase 2's serializer signature change (three new **required** params) breaks
      that call site immediately, not just at Phase 4's flag-flip. Left everything else in
      `capture_extraction_snapshots.py`/`capture_pipeline_baselines.py` for Phase 4/5 as planned.

### Validation
**Automated:**
- [x] `uv run pytest tests/unit/test_snapshot_v3_gate.py` → all 10 tests pass: 8 matrix cells raise
      `SnapshotFormatError` with the right message + "recapture"; v2-rejection; round-trip byte-identical
- [x] `uv run pytest tests/unit/test_occurrence_roundtrip_parity.py` → still green
- [x] `uv run ruff check src/`; `uv run mypy src/` → clean; mypy 76 (baseline, no new errors)
- [x] **Full suite is expected RED here** on snapshot-loading tests: 245 failed, 1315 passed, 692
      errors. Traced every failure/error to the version-gate rejection (`grep`'d the run output for
      non-snapshot causes — every failure/error is downstream of `tests/conformance/conftest.py`'s
      session-scoped `extraction_snapshots` fixture, which loads every committed v2 snapshot and now
      hits the version gate). Nothing else is red.

**Manual:**
- [x] Read a generated v3 snapshot dict in the round-trip test: three new keys present, facts section
      canonical (byte-identical to `constraint_facts.serialize` output), `part_occurrences` owner keys
      sorted (verified by construction — `serializer.py` builds the dict via `sorted(...)`), mode
      `"applied"`.
- [x] Verify every rejection message names the missing/bad section and ends with a re-capture
      instruction — asserted directly in the test (`"recapture" in str(exc_info.value).lower()`) for
      every matrix cell.

**What we know works after this phase:** a v3 snapshot carries honest facts + occurrences + mode;
the load boundary raises loudly on all eight corruption cells and never `KeyError`s. The silence
trap is closed.

---

## Phase 3: Offline re-lowering in `graph_rebuild`; end-to-end live/snapshot parity

### Goal
Wire the constraint phase (P1 lower + P3 extend, P2 inert per B3) into the from-snapshot rebuild,
dispatched on the load-validated mode enum, and prove byte-identical live/snapshot generation on
all three clean fixtures (INV-3).

### Why now
The v3 section exists (Phase 2) and the payload is proven to round-trip (Phase 1). This joins them
into genuine offline re-derivation.

### Assumption Under Test
- **B3** — `include_all=True` offline (`graph_rebuild.py:174`) makes live P2 (roots-before-pruning)
  inert: every producer channel a constraint binds to already exists, so `extend_graph_with_constraints`
  finds no dangling `bound_channel`.
- **B4** — the facts round-trip is lossless enough that `evaluate_profile`/`serialize_expression`
  return byte-identical predicates offline, so catalog **order** matches too.

### Test Stencil (write first)
```python
# tests/conformance/test_snapshot_constraint_parity.py  (NEW)
@pytest.mark.parametrize("fixture", ["wi014_toy", "constraint_multi_instance", "constraint_inline"])
def test_live_snapshot_constraint_parity(fixture, tmp_path):
    live = build_pipeline_context([FIXTURES / fixture], lower_constraints_enabled=True)
    snap_path = capture_snapshot([FIXTURES / fixture], tmp_path / "s.json")   # v3, mode=applied
    offline_graph, _ = build_full_graph_from_snapshot(snap_path)
    assert constraint_ids(offline_graph) == constraint_ids(live.computation_graph)   # INV-3
    assert catalog_order(offline_graph) == catalog_order(live.computation_graph)
    assert graph_structure(offline_graph) == graph_structure(live.computation_graph)

def test_constraint_free_fixture_loads_empty_catalog_graph_unchanged(tmp_path):
    # present-and-empty: empty usages -> no-op, graph byte-identical to today's baseline
```

### Changes Required

**See design.md for:** the offline dispatch block (design.md#architecture "Offline lowering"); B3
(design.md#key-bets); the mode×section matrix (design.md#architecture); the acceptance-is-two-things
note (design.md#validation-approach — the 3 parity fixtures prove byte-identity; the 22 corpus
divergences are eliminated by the suite going green in Phase 5, **not** by these three fixtures).

- [x] **`snapshot/graph_rebuild.py`** (`build_full_graph_from_snapshot`) — after the base graph
      is built, added the constraint phase dispatched on `snap["constraint_lowering_mode"]` (already
      a validated enum at load): `applied` + `facts.usages` → `FrozenOccurrenceIndex(snap["part_occurrences"])`,
      `lower_constraints(...)`, then `extend_graph_with_constraints(...)`, then (pulled forward from
      the epic-context note, not originally in this task list) `assemble_constraint_catalog` — mirrors
      pipeline_builder's live P4 so generated artifacts (which read the catalog from the graph, never
      from a context) stay byte-identical, not just the graph structure; `grandfathered_off` +
      `facts.usages` → skip + loud WARNING naming the ungenerated assertions; empty-usages → no-op.
      The dispatch is total (no third branch — the enum was validated at load).
- [x] Reused `inputs["registry"]`, `inputs["design_attrs"]`, `inputs["group_deriver"]` from
      `build_classifier_inputs_from_snapshot` and `snap["calc_usages"]` — all already re-derived
      offline. No new re-derivation.
- [x] **Deviation (pulled forward from Phase 4):** `snapshot/capture.py`'s `capture_snapshot` gained
      a `lower_constraints_enabled: bool = False` param, threaded to `build_pipeline_context`. Needed
      now because the parity test must capture a **fresh** v3 snapshot with lowering actually applied
      (the committed corpus is still v2/un-recaptured until Phase 5) — Phase 4 only needs to flip the
      *default* to `True` and route the grandfather set through it, not invent the param.
- [x] **Test file** `tests/conformance/test_snapshot_constraint_parity.py` (NEW) — the parity test
      (three fixtures, `model_dump_json()` + catalog `constraint_id`/fingerprint comparison), the
      present-empty test (`sample_model`), and an INV-4 grep-based regression test (no
      `build_part_instance_index` call in `graph_rebuild.py`).

### Validation
**Automated:**
- [x] `uv run pytest tests/conformance/test_snapshot_constraint_parity.py` → all 5 pass on the first
      run: three fixtures byte-identical live-vs-snapshot (graph dump + catalog constraint_ids +
      fingerprint), present-empty unchanged, INV-4 grep clean
- [x] `uv run ruff check src/`; `uv run mypy src/` → clean; mypy 76 (baseline, no new errors)
- [x] Full suite still expected RED on committed-corpus loading: 245 failed, 1320 passed (1315 + 5
      new), 692 errors — identical failure/error counts to Phase 2 plus the 5 new green tests.

**Manual:**
- [x] For `constraint_multi_instance`, the parametrized parity test directly asserts per-occurrence
      `constraint_id`s match one-for-one between live and offline catalogs (the exact path the
      occurrence table exists to serve) — no divergence.
- [x] Confirmed INV-4 via a grep-based regression test: `build_part_instance_index` does not appear
      in `graph_rebuild.py`; `FrozenOccurrenceIndex` is the only occurrence source on the offline path.

**What we know works after this phase:** live and from-snapshot generation produce byte-identical
constraint structure on the clean fixtures. Re-derivation-not-carriage is proven end-to-end.

---

## Phase 4: Flip the default True (both surfaces) behind the named grandfather set

### Goal
Flip `build_pipeline_context`'s `lower_constraints_enabled` default False→True and make the offline
path lower by default, in one change, with `plant_values`/`fusion_tea` grandfathered flag-off behind
a named, visible exclusion set so the corpus stays coherent.

### Why now
Parity is proven (Phase 3), which is the gate the flip is conditioned on (spec Success Criteria).
Both surfaces move together because the mode marker decouples "facts present" from "lower offline"
(design.md#integration-strategy).

### Assumption Under Test
The grandfather marker holds the two `gain`-blocked fixtures un-lowered on **both** paths: their
snapshots capture `mode:"grandfathered_off"` (flag-off at capture) and the offline path skips
lowering on that mode, so their graphs stay byte-identical while the rest flip (design.md#key-decisions D3,
INV-5).

### Test Stencil (write first)
```python
# tests/conformance/test_grandfather_carveout.py  (NEW)
@pytest.mark.parametrize("fixture", ["plant_values", "fusion_tea"])
def test_grandfathered_from_snapshot_generates_no_gain_halt(fixture, caplog):
    # from-snapshot generation succeeds (reads grandfathered_off, skips lowering)
    graph, _ = build_full_graph_from_snapshot(committed_snapshot(fixture))
    assert "grandfather" in caplog.text.lower()          # WARNING names the ungenerated assertion
    assert graph_bytes(graph) == committed_baseline(fixture)   # INV-5 byte-identical

def test_live_generate_grandfathered_still_halts_on_gain(fixture):
    # the CLI does NOT carry the exclusion set: live --models plant_values halts loudly (D3 scope)
    with pytest.raises(...): build_pipeline_context([FIXTURES/"plant_values"])  # unresolved 'gain'
```

### Changes Required

**See design.md for:** D3 scope-of-grandfather = capture scripts not CLI (design.md#key-decisions);
the flip + exclusion component (design.md#component-overview); the intended live-CLI halt
(design.md#key-decisions D3 sub-bullet).

- [x] **`orchestration/pipeline_builder.py`** — default `lower_constraints_enabled=True`; retired
      the transitional comment block, replaced with a Phase-4 note explaining the default and the
      grandfather's scope (CLI unaffected).
- [x] **`snapshot/capture.py`** — `capture_snapshot`'s `lower_constraints_enabled` param (added in
      Phase 3's pull-forward with default `False`) is now default `True`; threaded into
      `build_pipeline_context` (already wired in Phase 3).
- [x] **`scripts/capture_extraction_snapshots.py`** — a named `GRANDFATHERED = frozenset({"plant_values",
      "fusion_tea"})` set; in the `MODELS` loop, `lower_constraints_enabled=(model_name not in GRANDFATHERED)`
      passed to `capture_snapshot`. Named + commented (loud on gap, design principle).
- [x] **`scripts/capture_extraction_snapshots.py`** (`_capture_extraction_only`) — already wrote the
      three keys as of Phase 2's pull-forward (facts via `extract_constraint_facts`, mode
      `grandfathered_off`, empty table) — no further change needed here.
- [x] **`scripts/capture_pipeline_baselines.py`** — confirmed no change needed: it only calls
      `build_full_graph_from_snapshot(snapshot_path)`, which reads `constraint_lowering_mode` from the
      already-captured v3 snapshot (Layer A) and dispatches accordingly — no `GRANDFATHERED` mirror
      required on the Layer-B side.
- [x] **Test file** `tests/conformance/test_grandfather_carveout.py` (NEW).
- [x] **Deviation — 5 pre-existing tests updated for the default flip** (not originally listed, but
      required: these tests asserted the *old* off-by-default behavior as their control/premise, and
      the flip invalidates that premise, not the test's actual intent):
      - `test_constraint_lowering.py::_load` — now passes `lower_constraints_enabled=False` explicitly
        (these tests call `lower_constraints` manually afterward; the shared ctx must stay inert
        regardless of fixture, including `constraint_blocked_owner` which would otherwise halt before
        the test's own call).
      - `test_constraint_lowering.py::test_wired_pipeline_path_lowers_when_enabled` → renamed
        `..._by_default_and_is_inert_when_disabled`; adds a default-True assertion and keeps the
        explicit-False/True cases.
      - `test_constraint_pipeline_threading.py::test_roots_before_pruning_retains_producer_s4_reproduction`
        — the "control" build now passes `lower_constraints_enabled=False` explicitly (it was relying
        on the old implicit default for its control/lowered contrast).
      - `test_constraint_pipeline_threading.py::test_blocked_profile_fixture_generates_when_flag_off`
        → renamed `..._when_lowering_explicitly_disabled`; passes `False` explicitly (its premise —
        "flag off is the default" — no longer holds; the opt-out mechanism itself still does).
      - `test_orchestrator.py::test_computation_graph_identity_is_the_generation_boundary` — passes
        `lower_constraints_enabled=False` explicitly (wi014_toy carries an admitted assertion; P3
        EXTEND reassigns `computation_graph` to a new object, which is orthogonal to what this test
        pins — identity up to the `build_computation_graph` boundary).

### Validation
**Automated:**
- [x] `uv run pytest tests/conformance/test_grandfather_carveout.py` → all 4 pass: from-snapshot
      succeeds + WARNING (both fixtures); live CLI halts on `gain` (both fixtures) — verified the
      exact halt message empirically (`PlantValuesDesign__plant.gain: unresolved actual 'gain'`,
      `hif_plant_pkg__hif_plant.gain: ...`) before writing the assertion
- [x] `uv run ruff check src/`; `uv run mypy src/` → clean; mypy 76 (baseline, no new errors)
- [x] Full suite still expected RED on committed-corpus loading until Phase 5: 245 failed, 1324
      passed (1320 + 4 new), 692 errors — identical failure/error set to Phase 3.

**Manual:**
- [x] Confirmed the `GRANDFATHERED` set is named and commented in
      `scripts/capture_extraction_snapshots.py`; the offline WARNING names the ungenerated-assertion
      count (`caplog.text` assertion in the test). `capture_pipeline_baselines.py` needs no mirror
      (confirmed above — it reads the mode from the already-captured snapshot).

**What we know works after this phase:** the default is True on both surfaces; the two `gain`-blocked
fixtures stay un-lowered and byte-identical behind a visible marker; the live CLI halt on `gain` is
intact and loud (the Item-14 prerequisite hand-off).

---

## Phase 5: Corpus re-capture per-fixture + deliberate diff review

### Goal
Re-capture every committed snapshot at v3 under the timestamp-churn discipline, review each diff
against the expected-diff classes, and turn the full suite green.

### Why last
The version bump + flip + grandfather must all be in place before the corpus captures at v3 under
the new default. This is the phase that closes the mid-epic red.

### Assumption Under Test
The only diffs a re-capture produces are the six expected classes (design.md#integration-strategy
"Expected-diff classes"); anything else is a real change to investigate, not accept.

### Test Stencil (this phase is a procedure + a green suite, not a new unit test)
```
# per fixture, never blanket:
uv run python scripts/capture_extraction_snapshots.py --fixtures <name>
uv run python scripts/capture_pipeline_baselines.py   --fixtures <name>
# then the timestamp-churn check (memory: byte-identity-captured_at-churn):
git diff -- tests/fixtures/<name>   # if ONLY captured_at changed -> git checkout that file
```

### Changes Required

**See design.md for:** the four-step integration sequence (design.md#integration-strategy); the six
expected-diff classes + the grandfathered-pair caveat (classes 1–4 in their snapshots, class 5
excludes them); the two known stale baselines (design.md#potential-risks — `deep_cross_scope`,
`ife_plant`, reviewed not waved through).

- [x] **Add `constraint_inline` + `constraint_multi_instance` to `MODELS`** in both capture scripts
      (design.md#key-decisions D6) so they gain committed v3 snapshots + baselines.
- [x] **Re-capture Layer A** (extraction snapshots, needs license) — ran a full corpus capture (not
      per-fixture, since every fixture needs the version bump + 3 new keys regardless): all 29
      fixtures (23 full-pipeline + 6 extraction-only) → v3 + facts section; clean constraint fixtures
      (`wi014_toy`, `catf_mfe_model`, `constraint_inline`, `constraint_multi_instance`) gain honest
      facts/occurrences/`mode:"applied"`; the grandfathered pair (`plant_values`, `fusion_tea`)
      captured flag-off (`mode:"grandfathered_off"`, honest non-empty facts, empty table — verified
      by direct inspection).
- [x] **Re-capture Layer B** (pipeline baselines, license-free from Layer A): only `catf_mfe` and
      `wi014_toy` baselines changed (constraint structure added — the only two fixtures with
      admitted/unassessed constraint usages among the baseline-tracked set); everything else
      byte-identical, confirmed via `git diff --stat`.
- [x] **Deviation — Layer C discovered mid-phase:** `scripts/capture_baseline_yaml.py` (a third,
      license-free baseline layer the plan's four-step sequence didn't name) also needed re-running —
      `wi014_toy.yaml` was stale (missing the constraint modules), caught by
      `test_yaml_baseline_comparison_wi014_toy`. Re-ran it; only `wi014_toy.yaml` changed, same
      class-5 pattern as Layer B.
- [x] **Timestamp-churn revert:** not applicable this phase — every fixture's extraction snapshot has
      substantive changes (classes 1–4 below), so no file's diff is captured_at-only. The discipline
      applies to a future re-capture where nothing else changes.
- [x] **Deliberate diff review** — walked every extraction-snapshot diff programmatically (top-level
      key-set diff, old vs new, per fixture) against the classes below; one exception found and
      reviewed (`d38_caret`, logged below). The two design-flagged stale baselines (`deep_cross_scope`
      [captured as `deep_cross_scope_probe`], `ife_plant`) show ONLY the three new keys added — no
      other drift, confirmed via the same programmatic diff.
- [x] **Deviation — one out-of-band diff found and reviewed, not one of the six classes:**
      `d38_caret/extraction_snapshot.json` also lost a stale `"unhandled": false` field on one
      `BindingInfo` dict. Traced via `git log -S` to a prior, unrelated commit ("item5 Phase 1: Family
      1 total-and-loud extraction dispatch") that removed the `unhandled` field from `BindingInfo`
      and explicitly noted "the extraction snapshot also drops the stale `unhandled` field
      (serialization catch-up)" — `d38_caret` simply hadn't been re-captured since. Confirmed no other
      fixture shows this diff (grepped the whole corpus). Benign, pre-existing drift unrelated to
      Item 8; surfaced honestly here rather than silently absorbed into the re-capture.
- [x] **Mid-epic red interaction with an existing test, resolved by inspection, not a code change:**
      `test_capture_fixtures_filter.py::test_extraction_filter_touches_only_named` re-captures
      `sample_model` then runs `git checkout --` on it in a `finally` block to stay side-effect-free —
      which reverts it to whatever HEAD holds. Mid-phase (before this commit), HEAD still held the
      pre-Phase-5 v2 bytes, so running the full suite silently reverted `sample_model`'s working-tree
      re-capture back to v2, surfacing as a flaky-looking `test_clean_fixture_zero_warnings[sample_model]`
      failure. Root-caused via `git log -S`/reproduction (not a guess); resolves itself once this
      phase's re-capture is committed (the checkout then restores identical v3 bytes, a no-op). No
      code or test change needed — re-ran the affected fixture's capture once more before committing.

**Expected-diff classes (the review checklist — NH2 extends spec class 2 to all three keys):**
1. `snapshot_format_version: 2 → 3` on every snapshot.
2. `constraint_facts` section added everywhere (empty `usages` for constraint-free; honest non-empty
   for constraint-bearing incl. the grandfathered pair).
3. `part_occurrences` added everywhere (`{}` for constraint-free + grandfathered; the resolved table
   for clean-lowering fixtures).
4. `constraint_lowering_mode` added everywhere (`"applied"`, or `"grandfathered_off"` for the two
   carved-out + all extraction-only fixtures).
5. Constraint structure in the `baseline_outputs/` graphs of clean-lowering fixtures **only** (Layer B;
   excludes the grandfathered pair).
6. `captured_at` churn — reverted before commit.

### Validation
**Automated:**
- [x] `uv run pytest tests/` → **full suite green**: 2256 passed, 4 skipped (2255 + 1 self-resolving
      after commit — see the `test_extraction_filter_touches_only_named` note above), 7 deselected.
      The 22 corpus-wide conformance divergences the flip was blocked on are eliminated (NH3).
- [x] `uv run ruff check src/`; `uv run mypy src/` → clean; mypy 76 (baseline, no new errors)
- [x] `git status` / `git diff --stat -- tests/fixtures` shows only the expected-diff classes (verified
      programmatically per-fixture, see above)

**Manual:**
- [x] Every fixture diff classified into 1–4 (class 6 doesn't apply — no captured_at-only diffs
      existed this phase); the two grandfathered fixtures show classes 1–4 in their snapshots but
      byte-identical Layer-B graphs (confirmed: neither `plant_values` nor `fusion_tea` appears in the
      Layer-B `git diff --stat`).
- [x] `deep_cross_scope_probe` and `ife_plant` stale baselines reviewed: both show ONLY the three new
      keys added, nothing else — the "known stale" risk didn't materialize into an actual extra diff.
- [x] **Test-suite fixups required by the two structurally-changed baselines** (`catf_mfe`,
      `wi014_toy` — not anticipated in the original Phase 5 task list, needed because Phase 5 is the
      first point these fixtures' generated artifacts actually change):
      - `test_gen_registry.py`: `test_module_count_matches_inputs` and
        `test_schema_imports_match_entry_point_groups` didn't account for CONSTRAINT/REPORT_AGGREGATOR
        modules or the `constraint_types` schema import — both formulas extended.
      - `test_gen_schemas.py`: `test_single_output_uses_root_field` and
        `test_output_channels_use_pqn_format` pinned calc-module naming conventions that CONSTRAINT/
        REPORT_AGGREGATOR modules deliberately don't follow (`field_name="evaluation"`/
        `"constraint_report"`, and REPORT_AGGREGATOR's singleton `channel_name="constraint_report"`
        has no `__`) — both now exempt those two module kinds.
      - `test_pipeline_module_expansion.py`: `test_all_modules_have_metadata_fields` required
        `calc_def_name`/`source_file` on every module; CONSTRAINT/REPORT_AGGREGATOR modules carry
        neither (not derived from a calc_def) — exempted.
      - `test_gen_pipeline_yaml.py::test_yaml_baseline_comparison_wi014_toy` — fixed by re-running
        Layer C (`capture_baseline_yaml.py`), not a test-code change.
      - `test_snapshot_generation.py` (SC-1/SC-D parity): `plant_values` removed from
        `_SNAP19_FIXTURES` and `test_fusion_tea_live_vs_snapshot` rewritten (renamed
        `test_fusion_tea_snapshot_generates_grandfathered_and_live_halts_on_gain`) — both fixtures'
        live CLI leg now legitimately halts on `gain` under the Phase 4 default, so a live-vs-snapshot
        byte-diff can no longer run; each test now asserts the real current behavior of both legs.
      - `test_snapshot_v3_gate.py::test_v2_snapshot_rejected_by_version_gate` (my own Phase 2 test) —
        no longer reads a committed snapshot expecting it to still be v2; hand-bumps a v3 snapshot
        down to v2 instead.
      None of these are scope changes — each test's *actual* invariant (module metadata completeness,
      naming conventions, parity where it can still run) is intact; only the CONSTRAINT/
      REPORT_AGGREGATOR module kind's known, designed exceptions needed encoding.

**What we know works after this phase:** the whole corpus is at v3, live/snapshot parity holds across
the conformance suite, and the default flip is landed under a green gate.

---

## Risk Management

**See design.md#potential-risks for the full analysis.** Phase-specific mitigations:

- **Phase 1** — occurrence identity is the top risk (B2). Mitigation: this phase *is* the mitigation
  — the multi-instance round-trip test surfaces any `instance_path` reorder/index-loss on the smallest
  case before anything else is built.
- **Phase 2** — the rejection surface is the spec headline; the parametrized matrix (cells a–h) is
  the guard against a partial gate reopening the silence trap (MF1/MF2).
- **Phase 3** — offline registry/channel divergence could move a `constraint_id`. Mitigation: the
  byte-identity parity test on the exact clean-lowering shapes is the guard (pre-existing offline-parity
  territory narrowed to constraint inputs).
- **Phase 4** — grandfather drift (the exclusion set silently growing). Mitigation: the set is named
  in code + docs; the offline WARNING names ungenerated assertions on every grandfathered load.
- **Phase 5** — `captured_at` churn masking a real diff. Mitigation: the established timestamp-only
  churn check + revert, then per-diff classification against the six expected classes.

**Accepted boundary (NH4, design.md#potential-risks):** offline lowering trusts the frozen occurrence
table with no live model to cross-check — a model edited but not re-captured lowers against stale
occurrences (internally consistent, silently stale). This item does **not** detect that; the loader's
per-file source-hash freshness warning flags the edited source, and fingerprint sealing (Item 9) is
where staleness becomes a hard boundary. Explicit, accepted, not an oversight.

## Implementation Notes

[TO BE FILLED DURING IMPLEMENTATION]

### Phase 1 Completion
**Completed:** 2026-07-13
**Actual Changes:**
- `analysis/part_instance_index.py`: `OccurrenceIndex` Protocol, `RecordingOccurrenceIndex`,
  `FrozenOccurrenceIndex` (+ `FrozenOccurrenceIndexCorruptionError`), `deserialize_part_occurrences`.
- `analysis/constraint_lowering.py`: `occ_index` parameter type widened `PartInstanceIndex` →
  `OccurrenceIndex` on `_expand_owner_instances` and `lower_constraints`.
- `orchestration/pipeline_context.py`: new `part_occurrences` field; `constraint_facts` docstring
  updated (always populated, no behavior change to the field itself here — the None-when-empty
  guard was removed at the call site in `pipeline_builder.py`).
- `orchestration/pipeline_builder.py`: wraps `occ_index` in `RecordingOccurrenceIndex` inside the
  P1 RESOLVE block; `constraint_facts` is now passed to `PipelineContext` unconditionally;
  `part_occurrences=recorder.recorded` (or `{}` when lowering did not run) threaded through.
- `tests/unit/test_occurrence_roundtrip_parity.py` (NEW): the B1/B2 spike, 2 tests.
**Issues:** None — the spike passed on the first run, no `instance_path` reorder or index loss.
**Deviations:** None from the plan's stencil beyond using the real `_serialize_value`/
`constraint_facts.serialize`/`parse` entry points (as the stencil already anticipated) rather than
hand-rolled JSON.

### Phase 2 Completion
**Completed:** 2026-07-13
**Actual Changes:**
- `snapshot/__init__.py`: `SNAPSHOT_FORMAT_VERSION = 3`; `CONSTRAINT_LOWERING_MODE_APPLIED`,
  `CONSTRAINT_LOWERING_MODE_GRANDFATHERED_OFF`, `VALID_CONSTRAINT_LOWERING_MODES`.
- `orchestration/pipeline_context.py`: `constraint_lowering_mode: str = "grandfathered_off"` field.
- `orchestration/pipeline_builder.py`: computes and threads the mode string into `PipelineContext`.
- `snapshot/serializer.py`: `serialize_extraction_snapshot` gains three required keyword params
  (`constraint_facts`, `part_occurrences`, `constraint_lowering_mode`); writes them into the
  returned dict, `part_occurrences` with sorted owner keys.
- `snapshot/capture.py`: threads `ctx.constraint_facts`/`ctx.part_occurrences`/`ctx.constraint_lowering_mode`.
- `snapshot/loader.py`: the eight-step gate (all three keys required, facts well-formed, facts
  version pin, embedded expression-ir version scan, mode enum, code-pin asserts, deserialize);
  new `_scan_expression_ir_versions` helper.
- `scripts/capture_extraction_snapshots.py`: `_capture_extraction_only` now also emits the three
  keys (pulled forward from Phase 4 — see deviation above).
- `tests/unit/test_snapshot_v3_gate.py` (NEW): 10 tests — the 8-cell rejection matrix, v2-rejection,
  round-trip.
**Issues:** None beyond the deviation already logged above (extraction-only capture fix pulled
forward).
**Deviations:** (1) test file is new (`test_snapshot_v3_gate.py`), not an extension of
`test_hygiene_tail_loader.py` — logged above with rationale. (2) `_capture_extraction_only` fixed
now instead of Phase 4 — logged above with rationale. Neither changes scope, only sequencing.

### Phase 3 Completion
**Completed:** 2026-07-13
**Actual Changes:**
- `snapshot/graph_rebuild.py`: constraint-phase dispatch (P1 RESOLVE + P3 EXTEND + P4 CATALOG) in
  `build_full_graph_from_snapshot`, on the validated `constraint_lowering_mode` enum.
- `snapshot/capture.py`: `capture_snapshot` gained `lower_constraints_enabled: bool = False`.
- `tests/conformance/test_snapshot_constraint_parity.py` (NEW): 5 tests.
**Issues:** None — parity held on the first run for all three fixtures, including the
per-occurrence-expansion shape (`constraint_multi_instance`), the highest-risk case per the design's
risk register.
**Deviations:** (1) offline dispatch also assembles the catalog (`assemble_constraint_catalog`),
matching live P4 — logged above, required by the post-Item-7 artifact-level parity criterion the
orchestrator's brief added after this plan was written. (2) `capture_snapshot` gained the
`lower_constraints_enabled` param now instead of Phase 4 — logged above, needed for the parity test
itself to capture a lowering-applied snapshot before the corpus default flips.

### Phase 4 Completion
**Completed:** 2026-07-13
**Actual Changes:**
- `orchestration/pipeline_builder.py`: `lower_constraints_enabled` default → `True`; transitional
  comment replaced with the Phase-4 rationale (default + grandfather scope).
- `snapshot/capture.py`: `capture_snapshot`'s `lower_constraints_enabled` default → `True`.
- `scripts/capture_extraction_snapshots.py`: named `GRANDFATHERED` set; routed through the `MODELS`
  capture loop.
- `tests/conformance/test_grandfather_carveout.py` (NEW): 4 tests.
- 5 pre-existing tests updated for the default flip (logged above): `test_constraint_lowering.py`
  (`_load` helper + 1 renamed test), `test_constraint_pipeline_threading.py` (2 tests, one renamed),
  `test_orchestrator.py` (1 test).
**Issues:** The default flip surfaced 5 tests whose *assertions* encoded the old off-by-default
behavior as their test setup/control, not their actual subject under test. None were spec/design
violations — each was fixed by making the now-necessary `lower_constraints_enabled=False` explicit
where the test's real intent needed lowering disabled, confirmed via a full-suite diff
(`diff` against Phase 3's failure list) showing zero new failures beyond the fixed 5.
**Deviations:** None beyond the test updates above, which are corrective (keeping existing tests'
actual intent valid under the new default), not scope changes.

### Phase 5 Completion
**Completed:** 2026-07-13
**Actual Changes:**
- `scripts/capture_extraction_snapshots.py`, `scripts/capture_pipeline_baselines.py`: added
  `constraint_inline`/`constraint_multi_instance` to `MODELS` (D6).
- Re-captured Layer A (all 29 committed extraction snapshots → v3), Layer B (pipeline baselines —
  only `catf_mfe`, `wi014_toy` changed), Layer C (`baseline_yaml` — only `wi014_toy.yaml` changed,
  the deviation logged above).
- 5 test files updated for the two structurally-changed fixtures' new constraint modules
  (`test_gen_registry.py`, `test_gen_schemas.py`, `test_pipeline_module_expansion.py`,
  `test_snapshot_generation.py`, `test_snapshot_v3_gate.py`) — logged in Validation above.
**Issues:** Two non-obvious ones, both root-caused (not guessed) and logged above as deviations: the
`d38_caret` stale-`unhandled`-field drop (pre-existing, unrelated to Item 8), and the
`test_extraction_filter_touches_only_named` self-revert interaction with an uncommitted mid-phase
state (resolves on commit, no code change).
**Deviations:** All logged above at their point of discovery: Layer C's existence, the `d38_caret`
out-of-band diff, the self-reverting test interaction, and the 5 test-file fixups for the
CONSTRAINT/REPORT_AGGREGATOR module-kind exceptions. None are scope changes — each preserves the
original invariant while encoding the new, designed exception.

**Full suite: 2256 passed, 4 skipped, 7 deselected. mypy 76 (baseline). ruff clean on `src/`.**

---

**Status:** ~~Draft~~ → ~~In Progress~~ → **Complete** (all 5 phases landed 2026-07-13)
