# Implementation Plan: Derived-Attribute Alias Surfacing (SC-7)

**Status:** Draft
**Created:** 2026-07-06
**Last Updated:** 2026-07-06
**Epic Item:** UPSTREAM-FINDINGS Item 11 (last code item)
**Branch:** upstream-findings-epic

## Source Documents

- **Spec:** `.project/active/alias-surfacing/spec.md`
- **Design:** `.project/active/alias-surfacing/design.md` ← component details, bets, invariants, decisions
- **Design review + resolutions:** `.project/active/alias-surfacing/design-review.md`

Read the design fully before starting. This plan does not restate the mechanism — it
references design sections and adds only phase order, test stencils, and the two
integration facts the design's prose under-specifies (below).

---

## Implementation Strategy

### Phasing Rationale

The item is one derived list plus two small edits (`design.md#core-concept`). The list
(`output_aliases`) is the product and the riskiest piece — its shape-B resolver is the one
thing the review flagged as able to **silently no-op** a whole class of exposures (C1). So
Phase 1 builds and unit-tests the list end-to-end (both sources, the Key_A resolver, the
run-mode-split filter) behind its own unit tests *before* any baseline is captured. Phases
2–3 are the two independent edits (warning reroute, YAML filename override). Phase 4 is the
enumerated regen (the only place the suite is intentionally red mid-phase). Phase 5 is docs.

### Critical Path

`OutputAlias` model + field → `_build_output_aliases` (both sources resolved) → thread the
new param through **both** `build_computation_graph` call sites → unit tests green → warning
reroute → YAML override → regen → docs.

### First Proof Point

Phase 1's `ife_plant` nested-shape-B unit test: it asserts the plant-idiom exposures surface
with a **non-null** `canonical_channel`. That is the exact test that fails if the resolver
regresses to `scoped_lookup`-only (design-review C1) — the fastest signal that the resolver
is correct where the item is meant to be populated.

### Two integration facts the design under-specifies (VERIFY-anchored, plan-time findings)

- **F-A. Two `build_computation_graph` call sites must thread `channel_aliases`, not one.**
  The design's architecture diagram shows only the live path
  (`orchestration/pipeline_builder.py:800`). But the **7 graph baselines are captured
  through the snapshot path** — `scripts/capture_pipeline_baselines.py` →
  `snapshot/graph_rebuild.py:139` `build_full_graph_from_snapshot` → `build_computation_graph`.
  If only the live call is threaded, every shape-B baseline (`attr_expr_probe`, `ife_plant`,
  `catf_mfe`) serializes an **empty** `output_aliases` and the item silently no-ops in the
  committed artifacts. Both call sites must pass the new param. The snapshot registry already
  carries `_scoped_alias` (registered at `graph_rebuild.py:56`) for shape A and
  `snap["channel_aliases"]` (loaded at `:44`) for shape B — both are in scope at the `:139`
  call. Phase 1 threads both.

- **F-B. The YAML capture is live-only (license-gated); the graph capture is not.**
  `scripts/capture_baseline_yaml.py` uses `build_pipeline_context([model_path])` — **live
  syside extraction, needs a license** (valid until 2026-08-06). `capture_pipeline_baselines.py`
  is snapshot-driven and license-free. So Phase 4 splits: graph regen (7, license-free) runs
  anytime; YAML regen (`attr_expr_probe` re-capture + new `wi014_toy`) is grouped as the
  license-gated step. *Recommended optional improvement (noted, not required):* refactor
  `capture_baseline_yaml.py` to render from `build_full_graph_from_snapshot` (both fixtures
  have committed snapshots) — that makes YAML regen license-free and guarantees the YAML is
  rendered from the same graph the baseline captures. If not taken, keep the live path and run
  the two YAML captures under a license.

### Overall Validation Approach

Each phase starts with tests. The suite is green at every phase boundary **except** Phase 4
(the enumerated regen), where the field-set conformance test is intentionally red between the
model edit and the test flip. Gate at each boundary: `pytest`, `ruff check src/`, `mypy src/`
(record counts; `uv run` may be approval-gated — if blocked, record the recorded-gate + static
inspection, matching the Item 8–10 audit pattern).

**Current gate (baseline to hold):** 1963 passed / 4 skipped / 5 xfailed; ruff `src/` 21;
mypy `src/` 109.

### Corrected file anchors (design prose vs. verified location)

- `pipeline_builder.py` → `src/sysml_codegen/orchestration/pipeline_builder.py`
  (call site `:800`; `_register_partdef_expose_scoped_aliases` `:463`; `all_channel_aliases`
  `:707`; `include_all` param `:634`).
- `output_registry_builder.py` → `src/sysml_codegen/orchestration/output_registry_builder.py`
  (the two hand-copied leaf splits: `:260-263` and `:308-311`).
- `build_computation_graph` signature: `resolution/graph_builder.py:149` (no `channel_aliases`
  today — genuinely new; `:826`'s `channel_aliases=` is a `PipelineContext(...)` kwarg, not
  this function).
- Snapshot call site: `snapshot/graph_rebuild.py:139`.
- Per-field annotation test lives in **`tests/conformance/test_data_models.py`** (pattern
  `test_req_dm_03_fields_*`), not `tests/unit/`. Add `test_req_dm_09_fields_*` there.
- Exit template line (verified): `templates/pipeline_yaml.jinja2:47` —
  `{{ exit.name }}: {{ exit.type }} {{ exit.name }}.json`.

---

## Phase 1: `output_aliases` field + `_build_output_aliases` builder (the product)

### Goal

Add the `OutputAlias` model and the `ComputationGraph.output_aliases` field, build the derived
list from both sources with the correct resolvers/filters/sort, thread the new param through
**both** call sites, and pin it with unit tests. First and riskiest: the shape-B resolver is
the C1 no-op risk. This phase is green on its own before any baseline capture.

### Assumption Under Test

That shape-B `canonical_name` resolves through the **persisted Key_A path**
(`registry.alias_lookup(ScopedKey(...))` first, `scoped_lookup` fallback — `design.md#key-bets`
B2, C1 resolution) for **nested** part-usage exposures, not just top-level ones. If the resolver
is wrong, `ife_plant`'s nested exposures drop and the item no-ops.

### Test Stencil (write first)

```python
# tests/unit/test_output_aliases.py  (NEW)

def test_shape_a_from_scoped_alias(registry_with_wi014):
    aliases = _build_output_aliases(registry, expose_pure_aliases=[], modules=modules,
                                    include_all=True)
    assert OutputAlias("total_cost", "...demo_plant__cost_calc__cost",
                       "demo_plant", "part_def") in aliases

def test_shape_b_nested_resolves_nonnull(ife_plant_ctx):   # C1 GUARD — first proof point
    aliases = _build_output_aliases(registry, expose_pure_aliases=ep_aliases,
                                    modules=modules, include_all=True)
    nested = [a for a in aliases if a.shape == "part_usage"]
    assert nested and all(a.canonical_channel for a in nested)   # non-null channel

def test_determinism_sorted(mixed_aliases):
    assert aliases == sorted(aliases, key=lambda a: (a.instance_path, a.alias_name))

def test_dangling_filtered_targeted_run_silent(caplog):        # D4 targeted
    # channel absent from modules, include_all=False -> dropped + DEBUG, no raise
def test_dangling_include_all_run_errors():                    # D4 / M3 full run
    # channel absent from modules, include_all=True -> raise (or asserted WARNING)

def test_two_names_one_channel_both_retained(dup_alias_ctx):   # M4 tie-break
    # both entries in output_aliases; filename = first-by-sorted alias_name (Phase 3 asserts file)
```

### Changes Required

**See `design.md`:** `#component-overview` (`OutputAlias`, `_build_output_aliases`,
`owning_part_leaf`, `scoped_alias_items()`), `#key-decisions` D1/D2/D4/D5, `#required-invariants`
INV-1..5, `#implementation-notes`.

- [ ] **`OutputAlias` model** — `resolution/models.py`. Fields per `design.md#component-overview`
  D2 sketch: `alias_name`, `canonical_channel`, `instance_path`,
  `shape: Literal["part_def","part_usage"]`, `output_filename` property. Plain `BaseModel`.
- [ ] **`ComputationGraph.output_aliases`** — `resolution/models.py` (class at `:192`, field list
  ends at `:213`). `list[OutputAlias] = Field(default_factory=list)`, **no `exclude`** (D1 —
  contrast `fallback_entry_points` which *is* `exclude=True`).
- [ ] **`owning_part_leaf` shared helper** (Dim-4) — extract the `::`/`__` split now duplicated at
  `orchestration/output_registry_builder.py:260-263` and `:308-311`; call it from both those sites
  **and** `_build_output_aliases`. One rule, no drift on a `::`-form `owning_part_qn`.
- [ ] **`scoped_alias_items()` read accessor** — `core/output_registry.py` (near `_scoped_alias`
  at `:49`). Small property returning the `(scope, leaf) → channel` pairs so the builder stays off
  the private attribute.
- [ ] **`_build_output_aliases`** — `resolution/graph_builder.py` (new; Step 8.5). Shape A: iterate
  `scoped_alias_items()`, `instance_path` = key's scope half. Shape B: filter threaded aliases to
  `.source == "expose_pure"`, resolve `canonical_name` via
  `registry.alias_lookup(ScopedKey(canonical_name))` **first**, `scoped_lookup` fallback (C1 — do
  **not** "fix" this back to `scoped_lookup`-only; `design.md#component-overview` states why the
  `alias_lookup` read does not violate INV-1), `instance_path` = `owning_part_leaf(owning_part_qn)`.
  Recompute the declared-channel set locally (M5 — `_validate_channel_references` returns `None`,
  does not hand it over). Filter dangling by run mode (D4/M3). Stable-sort by
  `(instance_path, alias_name)` (INV-5).
- [ ] **New param + call in `build_computation_graph`** — `resolution/graph_builder.py:149`: add
  `channel_aliases: list[ChannelAlias] | None = None`; call `_build_output_aliases` as Step 8.5 and
  pass its result to `ComputationGraph(...)`. Thread `include_all` in from the caller (already a
  `build_pipeline_context` param at `pipeline_builder.py:634`) so the D4 split has the run mode.
- [ ] **Thread the param — LIVE call site** — `orchestration/pipeline_builder.py:800`: pass
  `channel_aliases=all_channel_aliases` (available at `:707`) and `include_all=include_all`.
- [ ] **Thread the param — SNAPSHOT call site (F-A)** — `snapshot/graph_rebuild.py:139`: pass
  `channel_aliases=snap.get("channel_aliases", [])`. `include_all` is effectively True here
  (full snapshot rebuild). Without this the 7 graph baselines serialize empty `output_aliases`.
- [ ] **Deliberate field-test flips (M1):**
  - `tests/conformance/test_graph_assembly.py:365` — the exact-set assertion (currently 4 fields).
    Add `"output_aliases"` to the set. *This red-then-green is the graph-rev discipline working.*
  - `tests/conformance/test_data_models.py` — add `test_req_dm_09_fields_computation_graph` (and an
    `OutputAlias` field case) matching the `test_req_dm_03_fields_*` pattern.
- [ ] **Positive shape test** — assert `output_aliases` is `list[OutputAlias]` with the four fields.

### Validation

**Automated:**
- [ ] `tests/unit/test_output_aliases.py` all pass (shape A, nested shape B, determinism, D4 both
  modes, M4 retention).
- [ ] `test_graph_assembly.py` + `test_data_models.py` field tests green after the flip.
- [ ] Full suite: no regressions beyond the intended field-test updates. `ruff`, `mypy` clean.

**Manual:**
- [ ] Build `ife_plant` graph in a REPL (snapshot path), inspect `graph.output_aliases`: nested
  exposures present with non-null channels.

**What we know works after this phase:** the derived list is correct for both shapes incl. nested,
both call sites populate it, and determinism + dangling-filter + tie-break are pinned — all before
a single baseline is touched.

---

## Phase 2: Shape-A reroute + warning retirement

### Goal

Route `_build_attribute_resolution_map`'s EXPOSE_PURE branch by `ca.is_on_part_definition`
(`extraction/data_models.py:226`) so shape A stops calling the naive refs-parser and stops emitting
the malformed-refs warning for the resolvable case. Flip `test_wi014_toy.py`.

### Assumption Under Test

That nothing in-repo reads the shape-A EXPOSE_PURE entry of the resolution map for wiring
(`design.md#key-bets` B3 — verified: only consumer is `_build_computed_attr_module`, no shape-A
FORMULA-consumes-exposed-name fixture), so setting shape A to LITERAL fallback mis-wires nothing.

### Test Stencil (write first)

```python
# tests/conformance/test_wi014_toy.py  (FLIP :28-40)
def test_shape_a_resolves_silent_and_surfaces(caplog):
    graph = build_full_graph_from_snapshot(wi014_snapshot)[0]
    assert any(a.alias_name == "total_cost" for a in graph.output_aliases)   # surfaced
    assert "could not identify instance/output" not in caplog.text          # :796 silent
    # unresolvable-refs and EXPOSE_COMPUTED warnings still fire (INV-6 matrix)
```

### Changes Required

**See `design.md`:** `#component-overview` "Shape-A reroute", `#implementation-notes` "Reroute
placement" / "Warning retirement diff", `#required-invariants` INV-6.

- [ ] **`_build_attribute_resolution_map`** — `resolution/graph_builder.py`: split the EXPOSE_PURE
  branch on `ca.is_on_part_definition`. Part usage (shape B): unchanged `_resolve_expose_pure` path
  (leave `:796`/`:809` byte-identical — still the shape-B / unresolvable path). Part def (shape A):
  do **not** call the refs-parser; set resolution to LITERAL (B3), and consult `_scoped_alias` to
  decide the warning — resolvable → silent; genuinely unresolvable → a warning naming the real cause,
  not "Item 10/11". Leaf-match `_scoped_alias` on `ca.python_name` (instance-qualified matching is
  available if a shared-sanitized-name case appears — `#implementation-notes`; low stakes).
- [ ] **Flip `test_wi014_toy.py:28-40`** from pinning the malformed-refs warning to asserting shape-A
  resolution + surfaced `total_cost` + no warning for the resolvable case (stencil above). Update the
  `REQ-CA-09 disposition` docstring at the top of the file — the deferral to "Items 10/11" is now
  discharged.

### Validation

**Automated:**
- [ ] `test_wi014_toy.py` green in its flipped form.
- [ ] Full suite green; `ruff`, `mypy` clean. (Graph baselines not yet regenerated — see Phase 4;
  if a wi014/attr_expr baseline-comparison test exists it moves to Phase 4's red window. Verify at
  implement time whether the resolution-map change alone churns any committed graph — it should not,
  since the shape-A map entry is unread for wiring, B3.)

**Manual:**
- [ ] `ife_plant` / `attr_expr_probe` shape-B warnings unchanged; EXPOSE_COMPUTED warning still fires.

**What we know works after this phase:** the resolvable EXPOSE (both shapes) is silent and named;
unresolvable/EXPOSE_COMPUTED warnings still fire (INV-6 matrix holds).

---

## Phase 3: YAML exit-point filename override

### Goal

Render each aliased channel's exit line with the modeler's name as its output **filename**
(`{instance_path}__{alias_name}.json`), keeping the exit **key** as the canonical channel (D3 —
verified against real simkit). Unaliased lines byte-identical to today.

### Assumption Under Test

That the filename-rename form (not a new alias-keyed line) is what simkit's grammar accepts
(`design.md#key-decisions` D3 — discharged against `pipeline_schema.py _parse_exit_outputs`), so
REQ-PY-06 and the existing conformance tests need no change.

### Test Stencil (write first)

```python
# tests/unit/test_exit_point_aliases.py  (NEW)
def test_aliased_channel_gets_alias_filename():
    exits = _build_exit_points(modules, alias_filenames={chan: "demo_plant__total_cost.json"})
    line = next(e for e in exits if e["name"] == chan)
    assert line["name"] == chan and line["filename"] == "demo_plant__total_cost.json"

def test_sibling_channel_ambiguity_distinct_filenames(sibling_ctx):   # D5 collision, shape A
    files = {a.output_filename for a in graph.output_aliases}
    assert files == {"chamber_a__power.json", "chamber_b__power.json"}

def test_nested_shape_b_guard_ife_plant(ife_ctx):                    # C1 at YAML layer
    # ife_plant nested exposures render aliased filenames, no dropped exit

def test_unaliased_channel_keeps_default_filename():
    assert line["filename"] == f"{chan}.json"
```

### Changes Required

**See `design.md`:** `#component-overview` "Exit-point filename override", `#key-decisions` D3, D5,
INV-4.

- [ ] **`_build_exit_points`** — `generation/pipeline.py:202`: accept a `canonical_channel → filename`
  override map (built from `graph.output_aliases`, filename = `OutputAlias.output_filename`). Each
  exit's `filename` = alias filename when present, else `{channel}.json`. One channel, two aliases →
  filename = first by sorted `alias_name` (M4); both entries stay in `output_aliases`.
- [ ] **`generate_pipeline_yaml`** — `generation/pipeline.py:58`: build the override map from
  `graph.output_aliases` and pass it to `_build_exit_points`.
- [ ] **Template** — `templates/pipeline_yaml.jinja2:47`: change `{{ exit.name }}.json` to
  `{{ exit.filename }}`. Key and type tokens unchanged → no conformance-test change (REQ-PY-06).
- [ ] **Collision unit test** (`sibling_channel_ambiguity`, D5) and **nested shape-B guard**
  (`ife_plant`) per stencil.

### Validation

**Automated:**
- [ ] `tests/unit/test_exit_point_aliases.py` all pass.
- [ ] REQ-PY-06 conformance test (`test_gen_pipeline_yaml.py:377`) still green **unchanged** (key +
  type untouched).
- [ ] Full suite green except any committed-YAML baseline comparison (→ Phase 4 red window).
  `ruff`, `mypy` clean.

**What we know works after this phase:** aliased channels render the modeler's filename; siblings get
distinct filenames (INV-4); the exit key stays a channel (simkit backstop for INV-3).

---

## Phase 4: Enumerated regeneration (the only red window)

### Goal

Regenerate committed baselines through the capture scripts with reviewed diffs. This is the only
phase where the suite is intentionally red between the code edit and the baseline/test update.

### Assumption Under Test

That every baseline diff falls in a pre-enumerated review class (field-addition, populated alias
entries, filename moves) — nothing unexpected churns.

### Changes Required — reviewed diff classes

**See `design.md#validation-approach` and `spec.md#baseline-regeneration`.**

- [ ] **7 graph baselines** (`scripts/capture_pipeline_baselines.py`, **license-free**,
  snapshot-driven — F-A applies: this is the path that must carry the threaded param):
  - Field-addition only: `solar_battery`, `sample_model`, `chain_spike` gain `output_aliases: []`;
    everything else byte-identical.
  - Populated: `attr_expr_probe` (3 entries: `scale_result`, `half_vol`, `quarter_vol`), `wi014_toy`
    (`total_cost`), `ife_plant` + `catf_mfe` (nested plant-idiom exposures — verify non-empty).
  - Review each diff against the class; no other field changes.
- [ ] **`attr_expr_probe` YAML** (`scripts/capture_baseline_yaml.py`, **license-gated** — F-B):
  3 exit filenames move to the modeler's names; all other lines byte-identical.
- [ ] **New `wi014_toy` YAML baseline** (F-B, license-gated): register `wi014_toy` in
  `capture_baseline_yaml.py`'s `MODELS` (currently `{solar_battery, attr_expr_probe, chain_spike,
  sample_model}`); new committed artifact showing `...cost_calc__cost` exit line's filename =
  `demo_plant__total_cost.json`.
  - *F-B optional:* if refactoring `capture_baseline_yaml.py` to the snapshot path
    (`build_full_graph_from_snapshot` + `generate_pipeline_yaml`), both YAML captures become
    license-free; otherwise run this step under a valid license (expires 2026-08-06).
- [ ] **No extraction-snapshot change** — snapshots carry no graph (verified).

### Validation

**Automated:**
- [ ] After regen: full suite green (field-set test now names `output_aliases`; baseline comparisons
  match regenerated files). `ruff` 21, `mypy` 109 (unchanged).
- [ ] Baseline comparison tests for `wi014_toy` / `attr_expr_probe` / `ife_plant` green.

**Manual:**
- [ ] Read each of the 7 graph diffs and both YAML diffs; confirm each falls in its enumerated class.

**What we know works after this phase:** committed artifacts carry the surfaced names; the suite is
green again; the schema rev is live and reviewed.

---

## Phase 5: Docs, REQ tags, coordination notes

### Goal

Land the R1 documentation obligations and the downstream-coordination note for the filename move.

### Changes Required

**See `design.md#docs--req-census`.**

- [ ] **REQ tags:** `REQ-DM-09` (the `output_aliases` field: shape, INV-3 existence, INV-5 order),
  `REQ-PY-08` (aliased channel's exit line renders the modeler's name as its filename), `REQ-CA-11`
  (shape-A EXPOSE_PURE routed via `_scoped_alias`; warning retired for resolvable case). Confirm each
  is the next free tag in its family before allocating.
- [ ] **Doc 09** (`reference/09-data-models.md`): add `output_aliases: list[OutputAlias]` to the
  ComputationGraph field list + an `OutputAlias` model entry; note it is present *because* not
  excluded (contrast `fallback_entry_points`). Fix the stale `models.py:174` line ref.
- [ ] **Doc 21** (`reference/21-pipeline-yaml-generation.md`): exit-point filename override; cite the
  simkit `<Type> <filename>` grammar; add the REQ-PY-08 matrix row.
- [ ] **Doc 16** (`reference/16-computed-attributes.md`): EXPOSE_PURE → surfaced-name story end; the
  shape-A warning retirement.
- [ ] **modeling-assumptions §3:** reconcile "consumers bind to `subsystem.exposed_name`" with the
  sanitized `python_name` form (Item 5 / REQ-NC-06).
- [ ] **verification-matrix.md:** rows for REQ-DM-09, REQ-PY-08, REQ-CA-11.
- [ ] **Release notes** — NEW `.project/active/alias-surfacing/release-notes.md` (M2; template:
  `.project/active/cross-part-wiring/release-notes.md`). The filename MOVE
  `{channel}.json → {instance}__{alias}.json` is a real behavioral change, not just churn:
  `attr_expr_probe` moves 3, `wi014_toy` moves 1. Enumerate which baselines' exit filenames change and
  the consumer-visible effect (a harness reading old `{channel}.json` paths sees the move).
- [ ] **agentic-mbse:** record the EXPOSE-pattern docs impact — the exposed name now surfaces as a
  named output capture (documentation-only note; no code).
- [ ] **CURRENT_WORK.md:** update Item 11 status.

### Validation

- [ ] Every new REQ tag appears in both its owner doc and the verification matrix.
- [ ] Release notes enumerate all 4 filename moves and the consumer effect.
- [ ] Final gate recorded: `pytest` / `ruff check src/` / `mypy src/`.

**What we know works after this phase:** the schema rev is documented per R1; the filename move is a
coordination note, not a surprise.

---

## Environment Setup

See `CLAUDE.md`. Tests: `uv run pytest tests/`. Type: `uv run mypy src/`. Lint:
`uv run ruff check src/`. `uv run` may be approval-gated this session — if blocked, record the
recorded-gate + static inspection (Item 8–10 audit pattern) rather than claiming a fresh green.

## Risk Management

**See `design.md#potential-risks`.** Phase-specific:

- **Phase 1 (C1 no-op):** the `ife_plant` nested-shape-B unit test is the guard — it fails if the
  resolver regresses to `scoped_lookup`-only. Written first.
- **Phase 1 (F-A):** if only the live call site is threaded, shape-B baselines serialize empty. The
  manual REPL check on the *snapshot* path catches it before Phase 4.
- **Phase 4 (F-B license):** the YAML captures need a live license or the optional snapshot refactor.
  Confirm license validity (or take the refactor) before starting Phase 4.
- **Phase 4 (misread churn):** every diff reviewed against its enumerated class; regen only via the
  capture scripts.

## Implementation Notes

### Phase 1 Completion — DONE (green)
- `OutputAlias` model + `ComputationGraph.output_aliases` field (serialized, no `exclude`), `resolution/models.py`.
- `owning_part_leaf` shared helper (`core/qualified_names.py`); the two `output_registry_builder`
  sites (`:260-263`, `:308-311`) refactored to call it.
- `scoped_alias_items()` read accessor (`core/output_registry.py`).
- `_build_output_aliases` (`resolution/graph_builder.py`): shape A from `scoped_alias_items()`;
  shape B `alias_lookup`-first then `scoped_lookup` (C1 — verified: shape-B aliases resolve ONLY
  via `alias_lookup`; `scoped_lookup` alone drops all of them, so the C1 guard has teeth on
  attr_expr_probe AND catf_mfe); D4 run-mode dangling filter (raise on `include_all`, debug-drop on
  targeted); INV-5 sort.
- `channel_aliases` + `include_all` threaded through BOTH `build_computation_graph` call sites
  (live `pipeline_builder.py:800`, snapshot `graph_rebuild.py:139`) AND the `test_factory_purity`
  build helper (a third, test call site — needed to match the snapshot-captured baseline).
- Field-test flips: GA-05 exact-set + DM-03 (4→5 fields) name `output_aliases`; new
  `test_req_dm_09_fields_output_alias`. New `tests/unit/test_output_aliases.py` (12 tests).
- **Fixture-shape correction (verified at implement time):** ife_plant's nested exposure is
  **shape A** (`_scoped_alias`, scope `radial_build.tf_coil`), NOT shape B as the design's C1 prose
  labels it. The genuine nested shape-B fixture is catf_mfe. C1 guard placed on attr_expr_probe +
  catf_mfe accordingly.
- **catf_mfe first-wins collapse (documented, invariant-compliant):** catf surfaces 44 shape-B
  entries; 28 (13 `minor_radius` + 13 `volume` + 2 `pump_power`) share a bare `canonical_name` and
  resolve to a single first-wins `_alias` channel each — a pre-existing Item-10 characteristic
  (design C1 note acknowledges it). INV-2/3/4 hold as defined against the registry; distinct
  instance_paths → distinct filenames. Release-notes coordination item.

### Phase 2 Completion — DONE (green)
- `_build_attribute_resolution_map` EXPOSE_PURE split on `is_on_part_definition`: shape A → LITERAL
  (identical to prior post-warning behavior, B3) + `_scoped_alias`-leaf-gated warning
  (resolvable → silent; unresolvable → names the real cause); shape B unchanged `_resolve_expose_pure`
  path (`:796` unresolvable warning intact). Verified: wi014 shape A now silent + surfaces.
- `test_wi014_toy.py`: disposition docstring flipped (deferral discharged by Item 11); new offline
  `test_wi014_toy_shape_a_silent_and_surfaces` pins name-emitted + malformed-refs-gone.

### Phase 3 Completion — DONE (green)
- `_build_alias_filename_map` (first-wins over INV-5-sorted aliases, M4) +
  `_build_exit_points(modules, alias_filenames)` (required param, no papering default) +
  `generate_pipeline_yaml` builds the map; template `pipeline_yaml.jinja2:47` → `{{ exit.filename }}`
  (key + type unchanged, REQ-PY-06 green). New `tests/unit/test_exit_point_aliases.py` (10 tests).

### Phase 4 Completion — PARTIAL (blocked on solar_battery recapture)
- 6/7 graph baselines regenerated + reviewed clean (field-addition + alias entries only, nothing
  else churns): solar_battery(+empty→see below), catf_mfe(+44), attr_expr_probe(+3), chain_spike(+[]),
  sample_model(+[]), wi014_toy(+1), ife_plant(+2). `registry_init.py` unchanged for all.
- `capture_baseline_yaml.py` refactored to the snapshot path (F-B optional; license-free), verified
  byte-identical to prior live baselines for unaffected models. attr_expr_probe YAML: 3 renames only.
  New `wi014_toy.yaml` committed + `test_yaml_baseline_comparison_wi014_toy`.
- **BLOCKED — solar_battery SC-1 reconciliation (approved option 1, not executed this session):**
  solar_battery carries a shape-A EXPOSE `misc_hardware_cost = allocation_model.total_allocation`
  (the spec's Baseline Regen §1 "no EXPOSE_PURE" classification is FALSE). The committed snapshot is
  stale (`misc_hardware_cost.reference_chain = None`, pre-Item-10 format), so the snapshot path
  under-surfaces vs live → SC-1 byte-identity breaks. Fix = recapture solar_battery's snapshot under
  license (same reference_chain class Item 10 recaptured wi014/catf/ife for). **The recapture is
  blocked in this sandbox** (reading `~/1cfe/agentic-mbse/.env` outside the working dir + network
  license validation require an interactive approval). Residual failures (2):
  `test_snapshot_generation.py::test_live_vs_snapshot_byte_identical`,
  `test_e2e_output_registry.py::TestYamlDiffValidation::test_yaml_matches_baseline[solar_battery]`.
  **Resume steps:** (1) recapture `tests/fixtures/solar_battery_model/extraction_snapshot.json`;
  (2) verify its diff is limited to `reference_chain` (+ `captured_at` + any canonical-path fields);
  (3) re-run `capture_pipeline_baselines.py` (solar graph baseline gains 1 alias) +
  `capture_baseline_yaml.py` (solar YAML gains the `misc_hardware_cost` rename); (4) re-run
  `test_live_vs_snapshot_byte_identical` explicitly.
- **Gate at partial state:** 1987 passed / 4 skipped / 5 xfailed / **2 failed** (both solar SC-1);
  ruff src/ 21; mypy src/ 109.

### Phase 5 Completion — NOT STARTED (gated on the recapture + final baseline set)
- Pending: REQ-DM-09 / REQ-PY-08 / REQ-CA-11 tags; docs 09/21/16; modeling-assumptions §3;
  verification-matrix rows; `release-notes.md` (filename moves: attr_expr ×3, wi014 ×1, **solar ×1**,
  + catf first-wins-collapse note); agentic-mbse impact note; CURRENT_WORK. Also: spec Baseline
  Regen §1 one-line amendment (solar_battery DOES carry shape-A EXPOSE misc_hardware_cost).

---

**Status:** Draft → In Progress → Complete
