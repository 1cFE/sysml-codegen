# Implementation Plan: Snapshot v3 — Constraint Facts Load-Bearing

**Status:** Draft
**Created:** 2026-07-12
**Last Updated:** 2026-07-12
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

- [ ] **`analysis/part_instance_index.py`** — add `RecordingOccurrenceIndex` (wraps a live
      `PartInstanceIndex`, delegates `occurrences_of`, records each `owner_eqn → result` into
      `.recorded`) and `FrozenOccurrenceIndex` (holds the table, `occurrences_of(qn)` = dict lookup,
      **raises on a missing key** — corruption, never `[]`, per design.md#key-decisions D2). Optional
      but recommended: a `typing.Protocol` `OccurrenceIndex` with just `occurrences_of` that both
      wrappers and `PartInstanceIndex` satisfy structurally (design's open question — lower only
      calls `occurrences_of`; the Protocol is for mypy clarity, not runtime).
- [ ] **`analysis/part_instance_index.py`** (or a sibling `serialize` helper) — `deserialize_part_occurrences(dict) -> dict[str, list[InstanceOccurrence]]`
      rebuilding `InstanceOccurrence(part_def_qn, steps=tuple(PathStep(...)))` from the serialized
      shape. Serialization is `_serialize_value` (no hand-rolled dicts — `InstanceOccurrence`/`PathStep`
      are plain frozen dataclasses; design.md#implementation-notes).
- [ ] **`orchestration/pipeline_builder.py:865`** — inside the existing
      `if lower_constraints_enabled and constraint_facts.usages:` block, wrap the already-built
      `occ_index` in `RecordingOccurrenceIndex(occ_index)` and pass the **wrapper** to
      `lower_constraints(..., occ_index=recorder, ...)`. After the call, `recorder.recorded` is the
      table (MF3 — inherits lowering's exact `part_def`-kind + `ADMIT`-eligible filter, no second
      owner-selection path). A `NonFiniteCardinalityError` still surfaces from the real call and
      halts, same as today.
- [ ] **`orchestration/pipeline_context.py`** — add fields `constraint_facts` and `part_occurrences`
      (design.md#component-overview D4); populate both in `build_pipeline_context`. (The
      `constraint_lowering_mode` field lands in Phase 2 with the serializer.)
- [ ] **Test file** `tests/unit/test_occurrence_roundtrip_parity.py` (NEW) — the stencil above,
      plus one negative assertion that `FrozenOccurrenceIndex.occurrences_of("nonexistent")` raises.

### Validation
**Automated:**
- [ ] `uv run pytest tests/unit/test_occurrence_roundtrip_parity.py` → passes
- [ ] `uv run pytest tests/` → **full suite green** (Phase 1 changes nothing that loads snapshots;
      the default stays False, so existing capture/generation is unaffected)
- [ ] `uv run ruff check src/`; `uv run mypy src/` → no new errors

**Manual:**
- [ ] Confirm the recorded table has one entry per queried `part_def`-kind owner and the occurrence
      lists match `occurrences_of` sort order (spot-check against the fixture's two instances).

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

- [ ] **`snapshot/__init__.py:15`** — `SNAPSHOT_FORMAT_VERSION = 3`; update the version comment.
      Add the mode constants: `CONSTRAINT_LOWERING_MODE_APPLIED = "applied"`,
      `CONSTRAINT_LOWERING_MODE_GRANDFATHERED_OFF = "grandfathered_off"`,
      `VALID_CONSTRAINT_LOWERING_MODES = frozenset({...})`.
- [ ] **`orchestration/pipeline_context.py`** — add the `constraint_lowering_mode` field (Phase 1
      added the other two). Populate in `build_pipeline_context`: `"applied"` when lowering ran,
      `"grandfathered_off"` when `lower_constraints_enabled=False` (Phase 4 routes the flag).
- [ ] **`snapshot/serializer.py`** — `serialize_extraction_snapshot` writes the three keys:
      `constraint_facts` = `json.loads(constraint_facts.serialize(facts))` (canonical bytes preserved,
      not re-derived); `part_occurrences` = `_serialize_value(table)` with **`sorted()` owner keys**
      (INV-7 / MF4 — `snapshot_to_json` does not `sort_keys`); `constraint_lowering_mode` = the mode
      string (always present). Thread the three new params through from `capture.py`.
- [ ] **`snapshot/capture.py:44`** — pass `ctx.constraint_facts`, `ctx.part_occurrences`,
      `ctx.constraint_lowering_mode` into `serialize_extraction_snapshot`.
- [ ] **`snapshot/loader.py`** (after the version gate at `:140`) — the eight-step order from
      design.md#architecture: (2) all three keys via `_require(raise_on_missing=True)`; (3) facts is
      a dict carrying `schema_version` (torn dict raises here, not downstream); (4) facts
      `schema_version == CONSTRAINT_FACTS_SCHEMA_VERSION`; (5) scan embedded predicate nodes for
      `expression-ir/*` `schema_version`, any `!= EXPRESSION_IR_SCHEMA_VERSION` raises (NH5 — a
      shallow recursive token scan over the facts dict collecting `schema_version` values that start
      `"expression-ir/"`); (6) `mode ∈ VALID_CONSTRAINT_LOWERING_MODES` else raise (MF2); (7) code-pin
      asserts for both version constants (mirrors `PROFILE_SEMANTIC_VERSION` at
      `constraint_lowering.py:463`); (8) deserialize facts via `constraint_facts.parse`, occurrences
      via `deserialize_part_occurrences` (Phase 1), mode string — join the `snap` dict.
- [ ] **Parse-entry decision (design open question):** try `constraint_facts.parse(json.dumps(section))`
      first; if the round-trip test proves it not byte-exact, add a dict-taking `parse` entry. The
      **round-trip test is the arbiter** — keep whichever passes `test_facts_section_roundtrips_byte_identical`.
- [ ] **Test file** — extend `tests/unit/test_hygiene_tail_loader.py` with the matrix stencil above
      (cells a–h) + the round-trip test. Build the v3/v2 fixture snapshots in a `tmp_path` (capture
      `constraint_multi_instance` live, or hand-assemble a minimal v3 dict).

### Validation
**Automated:**
- [ ] `uv run pytest tests/unit/test_hygiene_tail_loader.py` → all matrix cells raise
      `SnapshotFormatError` with the right message; round-trip byte-identical
- [ ] `uv run pytest tests/unit/test_occurrence_roundtrip_parity.py` → still green
- [ ] `uv run ruff check src/`; `uv run mypy src/` → no new errors
- [ ] **Full suite is expected RED here** on snapshot-loading tests (committed v2 corpus no longer
      loads — see the surfacing note above). Record which tests are red and confirm they are all
      and only snapshot-loading tests; anything else red is a real regression.

**Manual:**
- [ ] Read one generated v3 snapshot: three new keys present, facts section canonical/sorted,
      `part_occurrences` owner keys sorted, mode `"applied"`.
- [ ] Verify every rejection message names the missing/bad section and ends with a re-capture
      instruction (grep the messages).

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

- [ ] **`snapshot/graph_rebuild.py:144`** (`build_full_graph_from_snapshot`) — after the base graph
      is built, add the constraint phase dispatched on `snap["constraint_lowering_mode"]` (already a
      validated enum at load): `applied` + `facts.usages` → `FrozenOccurrenceIndex(snap["part_occurrences"])`,
      `lower_constraints(...)`, then `extend_graph_with_constraints(graph, concrete, inputs["group_deriver"])`;
      `grandfathered_off` + `facts.usages` → skip + loud WARNING naming the ungenerated assertions;
      empty-usages → no-op. The dispatch is total (no third branch — the enum was validated at load).
- [ ] Reuse `inputs["registry"]`, `inputs["design_attrs"]`, `inputs["group_deriver"]` from
      `build_classifier_inputs_from_snapshot` (`graph_rebuild.py:26`) and `snap["calc_usages"]` — all
      already re-derived offline (design.md#research-findings). No new re-derivation.
- [ ] **Test file** `tests/conformance/test_snapshot_constraint_parity.py` (NEW) — the parity stencil
      (three fixtures) + the present-empty test.

### Validation
**Automated:**
- [ ] `uv run pytest tests/conformance/test_snapshot_constraint_parity.py` → all three fixtures
      byte-identical live-vs-snapshot; present-empty unchanged
- [ ] `uv run ruff check src/`; `uv run mypy src/` → no new errors
- [ ] Full suite still expected RED on committed-corpus loading (unchanged from Phase 2 until Phase 5).

**Manual:**
- [ ] For `constraint_multi_instance`, diff the offline vs live catalog and confirm per-occurrence
      `constraint_id`s match one-for-one (the exact path the occurrence table exists to serve).
- [ ] Confirm INV-4: offline path never calls `build_part_instance_index` (grep the offline call
      graph; `FrozenOccurrenceIndex` is the only occurrence source).

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

- [ ] **`orchestration/pipeline_builder.py:697`** — default `lower_constraints_enabled=True`; retire
      the transitional comment block at `:856-863`.
- [ ] **`snapshot/capture.py:20`** — add a `lower_constraints_enabled: bool = True` param to
      `capture_snapshot`; thread it into `build_pipeline_context`. When False, the context stamps
      `constraint_lowering_mode="grandfathered_off"`, keeps honest non-empty facts, empty occurrence
      table (design.md#architecture "Capture data flow").
- [ ] **`scripts/capture_extraction_snapshots.py`** — a named `GRANDFATHERED = {"plant_values",
      "fusion_tea"}` set; in the MODELS loop, pass `lower_constraints_enabled=(name not in GRANDFATHERED)`
      to `capture_snapshot`. Keep the set named + commented (loud on gap, design principle).
- [ ] **`scripts/capture_extraction_snapshots.py:135`** (`_capture_extraction_only`) — also write the
      three keys: `constraint_facts = extract_constraint_facts(extractor.model)`, mode
      `grandfathered_off` (no pipeline → no lowering), empty table. Otherwise those v3 snapshots fail
      INV-1 (design.md#implementation-notes "Extraction-only capture").
- [ ] **`scripts/capture_pipeline_baselines.py`** — mirror the `GRANDFATHERED` set if/where the
      baseline rebuild needs the mode (the offline path reads the mode from the snapshot, so the
      baseline script may need no change beyond loading v3 — confirm during implementation).
- [ ] **Test file** `tests/conformance/test_grandfather_carveout.py` (NEW).

### Validation
**Automated:**
- [ ] `uv run pytest tests/conformance/test_grandfather_carveout.py` → from-snapshot succeeds +
      WARNING; live CLI halts on `gain`
- [ ] `uv run ruff check src/`; `uv run mypy src/` → no new errors
- [ ] Full suite still expected RED on committed-corpus loading until Phase 5.

**Manual:**
- [ ] Confirm the `GRANDFATHERED` set is named and commented in both scripts, and the offline
      WARNING names the specific ungenerated assertion.

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

- [ ] **Add `constraint_inline` + `constraint_multi_instance` to `MODELS`** in both capture scripts
      (design.md#key-decisions D6) so they gain committed v3 snapshots + baselines.
- [ ] **Re-capture Layer A** (extraction snapshots, needs license) per-fixture: every fixture → v3 +
      facts section; clean constraint fixtures gain occurrences + `mode:"applied"`; the grandfathered
      pair captures flag-off (`mode:"grandfathered_off"`, honest non-empty facts, empty table).
- [ ] **Re-capture Layer B** (pipeline baselines, license-free from Layer A) per-fixture: clean
      constraint fixtures gain constraint structure; constraint-free unchanged; grandfathered unchanged.
- [ ] **Timestamp-churn revert** across the corpus (memory `byte-identity-captured_at-churn`): diff,
      revert any file whose only change is `captured_at`.
- [ ] **Deliberate diff review** — walk each remaining diff against the six classes below; investigate
      anything outside. Re-examine the two known stale baselines explicitly.

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
- [ ] `uv run pytest tests/` → **full suite green** (this is the phase gate; the 22 corpus-wide
      conformance divergences are eliminated here, distinct from the 3 parity fixtures — NH3)
- [ ] `uv run ruff check src/`; `uv run mypy src/` → no new errors
- [ ] `git status` / `git diff --stat -- tests/fixtures` shows only the expected-diff classes

**Manual:**
- [ ] Every remaining fixture diff is classified into 1–5 (6 reverted); the two grandfathered fixtures
      show classes 1–4 in their snapshots but byte-identical Layer-B graphs.
- [ ] `deep_cross_scope` and `ife_plant` stale baselines reviewed and their diffs explained, not waved.

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
**Completed:** —
**Actual Changes:** —
**Issues:** —
**Deviations:** —

### Phase 2 Completion
—

### Phase 3 Completion
—

### Phase 4 Completion
—

### Phase 5 Completion
—

---

**Status:** Draft → In Progress → Complete
