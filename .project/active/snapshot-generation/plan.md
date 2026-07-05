# Implementation Plan: Snapshot-Driven Generation (SC-9 + SC-10)

**Status:** Draft
**Created:** 2026-07-05
**Last Updated:** 2026-07-05
**Epic:** UPSTREAM-FINDINGS, Item 2
**Branch:** upstream-findings-epic
**Complexity:** HIGH (1.5–2 day item)

## Source Documents
- **Spec:** `.project/active/snapshot-generation/spec.md`
- **Design (authoritative, review resolutions applied):** `.project/active/snapshot-generation/design.md` ← component details, D1–D8 decisions, B1–B3 bets, INV-1..7, V1–V6 error catalog, Appendix A/B
- **Design review:** `.project/active/snapshot-generation/design-review.md` (C1/M1–M6 — all resolved in the design)
- **Epic:** `.project/backlog/epic_upstream_findings.md` — Item 2; R1/R2/R3

---

## Implementation Strategy

### Phasing Rationale

The design promotes machinery that already works (~900 conformance tests exercise
the snapshot round-trip and graph rebuild) and adds three things on top: a
version/provenance contract, `source_file` reconstruction, and
`compilation_results` serialization. The phasing is built around two constraints:

1. **De-risk the two load-bearing bets before writing any real code.** B2
   (`source_file` lexical re-absolutization reproduces the parser's path) and C1
   (the promoted package imports license-free) are the only things that can
   invalidate the whole approach. Both need the **live license** and must be
   proven first (Phase 0). If either fails, the design changes — better to know
   on day one.

2. **Keep the suite green at every phase boundary.** Two changes force a
   coordinated landing:
   - The version guard hard-errors on unversioned snapshots → all 10 committed
     (unversioned) snapshots must regenerate in the **same change** (INV-2, spec
     atomic requirement).
   - `source_file` re-absolutization and `compilation_results` both change
     snapshot-derived output → the committed extraction snapshots **and** the
     pipeline baselines regenerate with them.

   So the mechanical promotion (Phase 1) lands first as a pure refactor with
   **no behavior change**, and the entire format contract lands **atomically** in
   Phase 2 with the regeneration.

### Critical Path

Phase 0 (de-risk, license) → Phase 1 (promote + migrate, green refactor) →
Phase 2 (format contract + regen, atomic, license) → Phase 3 (generation surface
+ CLI) → Phase 4 (headline validations SC-1/SC-10, license) → Phase 5 (docs +
close-out).

### First Proof Point

**Phase 0.** A live-vs-snapshot diff of the `SysML Source:` header lines for
solar_battery captured **on a symlinked source path**, plus a license-absent
import of the promoted-chain modules. These two collapse the design's biggest
uncertainties before anything is built on them.

### License-Required Phases (front-load — license expires 2026-08-06)

- **Phase 0** — B2/C1 de-risk (live capture + diff).
- **Phase 2** — re-capture the 10 extraction snapshots; regenerate pipeline baselines.
- **Phase 4** — SC-1 live-vs-snapshot byte-identical; SC-10 chain_spike re-capture if not already done in Phase 2.

Phases 1, 3, 5 are license-free. If the license is at risk, run 0/2/4's capture
steps in one live session and let the license-free phases follow.

### Overall Validation Approach

- Each phase starts with a test (or, for Phase 0, an executable probe).
- Every phase has an explicit green gate; Phase 1 and Phase 2 gate on the **full
  suite** because they touch the shared snapshot loader.
- Phase 2 is a **single atomic landing** (one commit): the suite is never red
  between the version guard and the regeneration.

---

## Known Facts (verified against HEAD, 2026-07-05)

- **10 committed extraction snapshots**, all unversioned:
  `tests/fixtures/{alias_agg_probe, attr_expr_probe, unresolvable_attr_probe,
  chain_spike_model, chain_override_probe, catf_mfe_model, solar_battery_model,
  sample_model, expression_binding_probe, issue22_model}/extraction_snapshot.json`.
- **Migration surface:** 19 files import `tests.helpers.snapshot*`; 14 import
  `build_full_graph_from_snapshot` / `build_classifier_inputs_from_snapshot`
  (overlap → ~26 unique files, matching design Appendix B).
- **Current loader** hard-codes `FIXTURES_DIR` and takes a `model_name`
  (`tests/helpers/snapshot_loader.py:39,42,58`); it leaves `source_file` as the
  **stored relative string** (`Path(d["source_file"])`, e.g. lines 124/157/173) —
  no re-absolutization today.
- **`source_file` reconciliation gotcha (Phase 2, load-bearing):** committed
  pipeline baselines store `source_file` **fixtures-relative**
  (`tests/fixtures/baseline_outputs/chain_spike/computation_graph.json:54` →
  `"chain_spike_model/library.sysml"`), and `test_factory_purity.py:508` compares
  with full `graph_dict == baseline` equality — **no `source_file` normalization**.
  Design D1/D8 re-absolutizes `source_file` at load to a **machine-specific
  absolute path**. If that reaches the pipeline-baseline path unchanged, the
  equality breaks — and regenerating the baseline would commit a
  `/home/reid/...` path that fails on any other machine/CI. Phase 2 must resolve
  this (normalize `source_file` away in the pipeline-baseline comparison, mirroring
  `test_graph_assembly.py:536-539` which already does). See Phase 2.
- **`test_factory_purity.py:486` already reads `inp["snap"].get("compilation_results")`**
  — the conformance infra is already wired for the SC-10 field; Phase 2 fills it.
- **`scripts/capture_pipeline_baselines.py`** already rebuilds from committed
  snapshots via `build_full_graph_from_snapshot(snapshot_name)` (line 70) and its
  docstring flags the deliberate Item-2 regen. It imports the helper from
  `tests.conformance.test_entry_point_classifier` — migrates in Phase 2.

---

## Phase 0: De-Risk B2 + C1 (License Live)

### Goal
Prove the two bets that can invalidate the approach, before building on them.
Everything else is mechanical once these hold.

### Assumption Under Test
- **B2** (design Key Bets, D8): a **lexical** absolute join of `snapshot_dir`
  with the stored relative `source_file` — `os.path.abspath(snapshot_path.parent
  / stored)`, **no `.resolve()`** — reproduces the parser's emitted `source_file`
  **byte-for-byte, on a symlinked path**.
- **C1** (design Design-Review Resolutions, INV-1 reworded): `import
  sysml_codegen.snapshot` and its transitive agentic-mbse imports
  (`parameter_groups`, `usage_extractor`, `dependency_backtracker`) **succeed with
  no syside license / JVM available** — module import is license-free; only
  *invoking* the parser needs a license.

### Probes (Write/Run These First)

**B2 — symlinked-path source diff (license required):**
```bash
# Create a symlinked view of the solar_battery sources, capture from it, diff headers.
ln -s "$(pwd)/tests/fixtures/solar_battery_model" /tmp/sb_symlink
# 1. Live generate from the SYMLINKED absolute --models path → capture SysML Source: headers
# 2. Capture a snapshot from the same symlinked path (serializer relativizes to output_dir)
# 3. Re-absolutize with the lexical join (NO .resolve()) and compare the
#    `SysML Source:` header strings byte-for-byte.
# PASS = identical. FAIL = adjust re-absolutization to match the parser's exact
#        rendering (file:// URI? trailing form? case?) BEFORE Phase 1.
```

**C1 — license-absent import (license-free, run in a scrubbed env):**
```bash
env -u SYSIDE_LICENSE_KEY -u SYSIDE_LICENSE -u SYSIDE_LICENSE_FILE \
  uv run python -c "
import analysis.parameter_groups, extraction.usage_extractor, \
       analysis.dependency_backtracker, agentic_mbse.sysml.syside_adapter
print('IMPORT OK license-absent')"
# PASS = prints OK. FAIL = imports pull in the JVM eagerly → design change
#        (lazy/deferred agentic-mbse imports in the rebuild chain). Surface now.
```

### Changes Required
- [ ] Scratch probe scripts under `scripts/` or `/tmp` (not committed) — or a
      throwaway `tests/` spike deleted after.
- [ ] Record the **exact** re-absolutization form B2 proves correct (lexical
      `os.path.abspath`, no `.resolve()`) — this is the spec for Phase 2's loader.
- [ ] Record the C1 result. If it fails, STOP and revise the design's import
      strategy before Phase 1.

### Validation
**Manual (license live):**
- [ ] B2 symlink diff → `SysML Source:` headers byte-identical.
- [ ] C1 scrubbed-env import → succeeds.

**What We Know Works After This Phase:**
The `source_file` reconstruction primitive reproduces the parser's path on a
symlinked path, and the promoted package imports without a license. The two
things that could sink the item are settled.

---

## Phase 1: Promote Package + Migrate Tests (Green Refactor)

### Goal
Move the loader/serializer and the two graph-rebuild helpers into
`src/sysml_codegen/snapshot/`, change the loader to a path-based signature,
migrate all ~26 call sites, and delete the `tests/helpers/` copies — with **zero
behavior change**. This is a pure refactor that must leave the full suite green.

### Assumption Under Test
The promotion is behavior-preserving: loading a committed (unversioned,
fixtures-relative) snapshot through the new `src` module produces exactly the same
data as today (INV-3, no output change). No version guard, no re-absolutization,
no `compilation_results` yet — those all land in Phase 2.

### Test Stencil (Write This First)
```python
# The migration is proven by the EXISTING suite passing unchanged after the import
# swap. Add one guard test for the no-two-copies invariant (INV-3):
def test_no_tests_helpers_snapshot_copies():
    # grep the tree; the promoted helpers exist only in src/sysml_codegen/snapshot/
    out = subprocess.run(["grep", "-r", "tests.helpers.snapshot", "tests", "scripts", "src"],
                         capture_output=True, text=True)
    assert out.stdout.strip() == "", f"stale tests.helpers.snapshot refs: {out.stdout}"
    assert not Path("tests/helpers/snapshot_loader.py").exists()
    assert not Path("tests/helpers/snapshot_serializer.py").exists()
```

### Changes Required

**See `design.md` for:** Component Overview (package layout D3), Appendix B
(migration surface), M4 (conftest helper is legitimate, not a shim).

- [ ] Create `src/sysml_codegen/snapshot/__init__.py` — public API re-exports;
      define `SNAPSHOT_FORMAT_VERSION = 1` and `class SnapshotFormatError(Exception)`
      (constant + exception **defined**, guard **not yet enforced** — Phase 2).
- [ ] `snapshot/serializer.py` — moved from `tests/helpers/snapshot_serializer.py`.
      (Format additions deferred to Phase 2; this is a straight move.)
- [ ] `snapshot/loader.py` — moved from `tests/helpers/snapshot_loader.py`;
      signature `load_extraction_snapshot(snapshot_path: Path)` (was
      `model_name: str`). **Behavior otherwise identical** — `source_file` stays
      the stored relative string; no version guard; `compilation_results` absent →
      today's behavior. Deserializers unchanged.
- [ ] `snapshot/graph_rebuild.py` — promoted `build_full_graph_from_snapshot` and
      `build_classifier_inputs_from_snapshot` from
      `tests/conformance/test_entry_point_classifier.py:56,136`. Keep them
      path/dict-based to match the new loader signature.
- [ ] `tests/conftest.py` — add `snapshot_fixture(name)` returning
      `FIXTURES_DIR / name / "extraction_snapshot.json"` (design M4 / Appendix B).
      **Decision:** helper name is `snapshot_fixture` (plan's call — design left it open).
- [ ] Migrate the ~26 files (Appendix B mechanical edits): swap
      `from tests.helpers.snapshot_loader import ...` →
      `from sysml_codegen.snapshot import ...`; swap the two-helper import from
      `test_entry_point_classifier` → `sysml_codegen.snapshot`; rewrite call sites
      `load_extraction_snapshot("solar_battery_model")` →
      `load_extraction_snapshot(snapshot_fixture("solar_battery_model"))`.
- [ ] Delete the two helper defs from `test_entry_point_classifier.py`; import from
      the promoted module.
- [ ] Migrate `scripts/capture_extraction_snapshots.py` and any `scripts/` spikes'
      imports (the deep `capture_pipeline_baselines.py` migration is Phase 2).
- [ ] **Delete** `tests/helpers/snapshot_loader.py` and
      `tests/helpers/snapshot_serializer.py` (INV-3, no shim).

### Validation
**Automated:**
- [ ] `uv run pytest tests/` → full suite green (same count as before, refactor-only).
- [ ] `grep -r "tests.helpers.snapshot" src tests scripts` → empty (INV-3).
- [ ] `uv run mypy src/` and `uv run ruff check src/` → pass.

**What We Know Works After This Phase:**
The snapshot machinery lives in `src`, loads from an arbitrary path, and every
test + the pipeline-baseline path imports it from `src` — with identical behavior.
No output changed; no snapshot regenerated.

---

## Phase 2: Format Contract + Regeneration (Atomic, License Live)

### Goal
Land the whole format contract — version guard, `compilation_results`,
`source_file` re-absolutization — **and** regenerate the 10 extraction snapshots
and the pipeline baselines, **in one atomic change**. The suite is never red
between the guard and the regeneration.

### Assumption Under Test
The three format additions round-trip correctly, and the regenerated snapshots +
baselines make the full suite green in a single landing (INV-2, INV-5, SC-10,
spec atomic requirement).

### Test Stencil (Write This First)
```python
def test_missing_version_is_hard_error(tmp_path):
    snap = tmp_path / "extraction_snapshot.json"
    snap.write_text(json.dumps({"model_name": "x", "calc_definitions": []}))  # no version
    with pytest.raises(SnapshotFormatError, match="no snapshot_format_version"):
        load_extraction_snapshot(snap)

def test_wrong_version_is_hard_error(tmp_path):
    snap = tmp_path / "extraction_snapshot.json"
    snap.write_text(json.dumps({"snapshot_format_version": 999, "model_name": "x"}))
    with pytest.raises(SnapshotFormatError, match="format version 999"):
        load_extraction_snapshot(snap)

def test_chain_spike_compilation_results_nonempty():
    snap = load_extraction_snapshot(snapshot_fixture("chain_spike_model"))
    assert snap["compilation_results"]  # non-empty dict[str, CalcDefCompilationResult] (INV-5)
```

### Changes Required

**See `design.md` for:** D1/D8 (`source_file` relativize-at-capture /
re-absolutize-at-load, lexical), D4 (integer version constant), Implementation
Notes (version guard runs first; `compilation_results` shape; sentinel carve-out),
Appendix A (V1/V2/V4 wording).

- [ ] **Version guard (INV-2, V1/V2).** In `load_extraction_snapshot`, read
      `raw.get("snapshot_format_version")` **before any other key**; raise
      `SnapshotFormatError` on missing or `!= SNAPSHOT_FORMAT_VERSION`. Messages
      per Appendix A V1/V2 (name the recapture fix).
- [ ] **`compilation_results` (SC-10, INV-5, V4).** Serializer: add a top-level
      `"compilation_results"` block as `{calc_def_name: <CalcDefCompilationResult
      dict>}` via the existing generic `_serialize_value`. Loader: absent →
      `logger.warning` (V4) + `{}` (degrade); present → deserialize to
      `dict[str, CalcDefCompilationResult]` (add
      `_deserialize_compilation_result` / `_deserialize_calc_def_compilation_result`).
- [ ] **`source_file` capture-time relativization (D1, M1).** Serializer
      relativizes each `source_file` against **`output_path.parent`** (the snapshot's
      own directory), not `FIXTURES_DIR`. Keep `"unknown"` / `"hierarchy"`
      sentinels untouched.
- [ ] **`source_file` load-time re-absolutization (D1, D8).** Loader converts each
      real `source_file` via the **exact form Phase 0 proved** —
      `Path(os.path.abspath(snapshot_path.parent / stored))`, **no `.resolve()`**.
      Sentinels pass through untouched.
- [ ] **RESOLVE THE PIPELINE-BASELINE `source_file` GOTCHA (load-bearing).**
      Re-absolutization makes `source_file` machine-specific, but the pipeline
      baseline stores it and `test_factory_purity.py:508` compares by full equality.
      Fix: **normalize `source_file` away in the pipeline-baseline comparison**
      (and in `capture_pipeline_baselines.py` before writing), mirroring
      `test_graph_assembly.py:536-539`. This keeps committed baselines portable
      (no `/home/reid/...` paths) while re-absolutization stays correct for the
      generation path (Phase 3/4). Verify no committed baseline embeds an absolute
      path after regen.
- [ ] **Migrate `scripts/capture_pipeline_baselines.py`** to import
      `build_full_graph_from_snapshot` from `sysml_codegen.snapshot` and take the
      snapshot path via `snapshot_fixture` (or an equivalent path map).
- [ ] **Re-capture the 10 extraction snapshots** via the promoted capture (versioned,
      `output_path.parent`-relative `source_file`, `compilation_results` present).
      (Capture command may not exist until Phase 3 — use the promoted
      `capture_snapshot` function or the migrated `capture_extraction_snapshots.py`
      wrapper; either is fine, the CLI is a thin shell over it.)
- [ ] **Regenerate the pipeline baselines** from the re-captured snapshots. Expect
      and **review** the diff: `compilability` flips from `"unknown"` and
      `auto_impl_context` becomes non-null for expression-bearing models
      (chain_spike especially) — this is the **EXPECTED, deliberate** SC-10 effect,
      documented in the capture script docstring. `source_file` stays
      normalized/relative (previous item).

### Validation
**Automated:**
- [ ] New guard tests (stencil) → pass; error messages name the recapture fix.
- [ ] `chain_spike` snapshot `compilation_results` non-empty (INV-5).
- [ ] Freshness/degrade unit tests: mutated source-hash → warning, run continues
      (V3); version-current snapshot with no `compilation_results` → warning +
      degrade (V4).
- [ ] `uv run pytest tests/` → **full suite green** against regenerated snapshots
      + baselines (the atomic gate).

**Manual (license live):**
- [ ] Review the pipeline-baseline diff: only `compilability` / `auto_impl_context`
      changes (SC-10), no `source_file` absolute-path leakage, no unexpected churn.

**What We Know Works After This Phase:**
The versioned format round-trips; unversioned/mismatched snapshots hard-error;
`compilation_results` survives; `source_file` reconstructs; the whole suite is
green against the regenerated corpus. This is a single atomic commit.

---

## Phase 3: Generation Surface — Context Builder + CLI (License-Free)

### Goal
Wire the loaded snapshot into a full `PipelineContext` and expose
`generate --from-snapshot` + the `snapshot` capture subcommand. Generation code is
unchanged; the CLI picks the builder by flag.

### Assumption Under Test
**B1** end-to-end: no generation path dereferences `ctx.extractor` /
`ctx.backtracker`, so a snapshot context with those `None` generates successfully
(INV-4). And the snapshot path never invokes the parser (INV-1, behavioral).

### Test Stencil (Write This First)
```python
def test_snapshot_context_has_null_extractor_and_generates():
    ctx = build_pipeline_context_from_snapshot(snapshot_fixture("solar_battery_model"))
    assert ctx.extractor is None and ctx.backtracker is None  # INV-4
    run_codegen(ctx, config)  # must not raise AttributeError on a None field (B1)

def test_generate_requires_exactly_one_input(capsys):
    # neither --models nor --from-snapshot → error; both → error (INV-7, V6)
    ...

def test_from_snapshot_rejects_design_path_filter():
    # --from-snapshot + --design-path-filter → hard CLI error (INV-7, V6)
    ...
```

### Changes Required

**See `design.md` for:** Architecture (two-path convergence), D2 (context-builder
location keeps `orchestration → snapshot` one-directional), Implementation Notes
(CLI mechanism), Appendix A (V5 banner, V6 CLI errors), dead-template trap.

- [ ] `src/sysml_codegen/orchestration/snapshot_context.py` —
      `build_pipeline_context_from_snapshot(snapshot_path) -> PipelineContext`:
      rebuild the graph (promoted helper), thread `compilation_results` into
      `build_computation_graph(...)`, wrap a `PipelineContext` with
      `extractor=None`, `backtracker=None` (+ the other required fields per
      `pipeline_context.py:78-104`), log the provenance banner **once** (V5), and —
      if the loader flagged stale sources — log the **one end-of-run freshness
      summary** (V3, design M6).
- [ ] `src/sysml_codegen/snapshot/capture.py` — `capture_snapshot(model_paths,
      output_path, design_path_filter="")` lifted from
      `_capture_full_pipeline` (the only license-requiring code in the package).
      Default output `<models-root>/extraction_snapshot.json` (D5).
- [ ] `cli/__init__.py`: replace `--models required=True` (`cli/__init__.py:513`)
      with `add_mutually_exclusive_group(required=True)` holding `--models` /
      `--from-snapshot` (INV-7); reject `--from-snapshot` + `--design-path-filter`
      in `cmd_generate` (V6); add `cmd_snapshot` subcommand; `GenerationConfig`
      gains `from_snapshot: Path | None`.
- [ ] **Decision (design left open):** retire vs wrap
      `scripts/capture_extraction_snapshots.py`. **Plan's call:** keep it as a thin
      wrapper that loops the 10 fixtures calling `capture_snapshot` (convenient for
      bulk fixture regen), delegating all logic to the promoted module — no second
      copy of capture logic (INV-3 spirit). The supported user path is the CLI.
- [ ] **Dead-template guard (spec INFERRED).** Add a test asserting
      `generation_timestamp` in `templates/pydantic_schema.py.jinja2:8` has **zero
      render sites** (leave unwired or delete) — wiring it would break byte-identity.

### Validation
**Automated:**
- [ ] Null-fields generation test (INV-4, B1) → generates, no `AttributeError`.
- [ ] CLI route tests (INV-7, V6): both flags → error; neither → error;
      `--from-snapshot` + `--design-path-filter` → error.
- [ ] **INV-1 env-scrubbed subprocess:** run `generate --from-snapshot` with
      `SYSIDE_LICENSE_KEY` et al. **unset** → success (proves the path never invokes
      the parser).
- [ ] **INV-6 provenance-never-in-output:** generated files contain no
      banner / `captured_at` / version text.
- [ ] Dead-template guard test → passes.
- [ ] `uv run pytest tests/` → full suite green.

**Manual:**
- [ ] `uv run sysml-codegen snapshot --models <fixture>` writes a versioned snapshot.
- [ ] `uv run sysml-codegen generate --from-snapshot <snapshot> --output /tmp/out`
      prints the V5 provenance banner and generates.

**What We Know Works After This Phase:**
`--from-snapshot` generates a full package license-free; the CLI decision surface
is exhaustive; provenance stays out of artifacts; capture is a supported command.

---

## Phase 4: Headline Validations — SC-1 + SC-10 (License Live, Evidence Captured)

### Goal
Prove the two success criteria that only a live license can establish:
byte-identical live-vs-snapshot generation (SC-1) and preserved CalcUsage
auto-implementation (SC-10). Capture explicit evidence while the license is live.

### Assumption Under Test
SC-1: a snapshot run is byte-identical to live generation (including the
`SysML Source:` headers, on a symlinked path — the full-integration version of
Phase 0's primitive). SC-10: `chain_spike` auto-impl matches live.

### Test Stencil (Write This First)
```python
@skip_if_no_license  # skips cleanly on ImportError from load_models
def test_live_vs_snapshot_byte_identical(tmp_path):
    live_out, snap_out = tmp_path / "live", tmp_path / "snap"
    # Feed live an ABSOLUTE --models path (parser emits the absolute form D1 rebuilds).
    # Run at least once on a SYMLINKED source path (D8/B2).
    run_generate(models=abs_symlinked_solar_battery, output=live_out)
    run_generate(from_snapshot=captured_snapshot, output=snap_out)
    assert recursive_tree_diff(live_out, snap_out) == []   # empty diff (SC-1)

def test_chain_spike_autoimpl_matches_live():
    ctx = build_pipeline_context_from_snapshot(snapshot_fixture("chain_spike_model"))
    stencils = generate_stencils(ctx)
    assert "NotImplementedError" not in calc_usage_stencils(stencils)  # auto-impl (SC-10)
    assert all(m.compilability != "unknown" for m in calc_usage_modules(ctx))  # INV-5
```

### Changes Required

**See `design.md` for:** Validation Approach (SC-1 license-gated, absolute path,
symlinked run; SC-10 license-free once committed).

- [ ] License-gated `test_live_vs_snapshot_byte_identical` — skips cleanly on
      `ImportError` from `load_models` (reuse `test_extractor.py:851-864` idiom).
      Feed an **absolute** `--models` path; run **once on a symlinked source path**.
- [ ] SC-10 `chain_spike` auto-impl test (license-free — rides the Phase-2
      re-captured snapshot).

### Validation
**Manual (license live — capture evidence into the plan's Implementation Notes):**
- [ ] Run SC-1 with the license live → **empty tree diff**. Record the command and
      the empty-diff output.
- [ ] Run SC-1 once on a **symlinked** source path → empty diff (D8/B2 at
      integration scale). Record it.
- [ ] SC-10 chain_spike → stencils auto-implemented, `compilability` set, matches
      live. Record it.

**Automated (license-free thereafter):**
- [ ] SC-10 test passes in CI (no license).
- [ ] SC-1 test **skips** cleanly when no license present.

**What We Know Works After This Phase:**
Snapshot generation is byte-identical to live (the headline SC-9 claim, proven —
not self-consistency), and CalcUsage auto-impl survives a snapshot (SC-10).

---

## Phase 5: Docs, Tags, Close-Out (License-Free)

### Goal
Document the format as a reference doc, tag the requirements, complete the
verification matrix, record the agentic-mbse impact, and update CURRENT_WORK.

### Assumption Under Test
None — this is documentation and traceability closing out the item.

### Changes Required

**See `design.md` for:** D7 (new doc 27 + pointer from doc 02), M5 (REQ-SNAP
numbering starts at **08** — 01–07 exist), agentic-mbse impact section.

- [ ] `docs/architecture/reference/27-snapshot-generation.md` — format schema
      (top-level `snapshot_format_version`, `compilation_results` block,
      relativized `source_file`), the version/provenance/freshness policy (V1–V6),
      and the `REQ-SNAP-08+` requirement table. Reconcile with the **existing**
      `REQ-SNAP-01..07` family (round-trip / typed-fields / AST-None) — doc 27 is a
      new reference doc for an existing family, not a new namespace.
- [ ] Pointer from `docs/architecture/reference/02-orchestration.md`
      (PipelineContext section) to doc 27.
- [ ] Add `REQ-SNAP-08+` tags to the new behavior and **verification-matrix rows**
      mapping each REQ to its test (INV-1..7 → the tests written above).
- [ ] **agentic-mbse impact:** record explicitly — expected **none** beyond a
      possible docs pointer (design "agentic-mbse impact"; R2). Confirm "none vs
      docs pointer" and note it in the close-out.
- [ ] Update `.project/CURRENT_WORK.md` Item 2 status → complete, with the SC-1/SC-10
      evidence pointer.

### Validation
- [ ] Doc 27 present; doc 02 pointer resolves; REQ table numbered from 08.
- [ ] Verification matrix: every new REQ-SNAP has a row and a passing test.
- [ ] `uv run pytest tests/` → full suite green (final gate).

**What We Know Works After This Phase:**
The snapshot format is documented and traceable; the item is closeable
(`/_my_audit` → `/_my_pre_pr`).

---

## Environment Setup

**See CLAUDE.md** for install / test / lint commands. Key ones:
- Tests: `uv run pytest tests/`
- Single: `uv run pytest tests/unit/test_x.py -k name`
- Types/lint: `uv run mypy src/` / `uv run ruff check src/`
- License-absent probe: `env -u SYSIDE_LICENSE_KEY -u SYSIDE_LICENSE ... uv run ...`

**Orchestrator note:** the current harness gates `uv run` and file writes for the
license-dependent capture steps (Phases 0, 2, 4). Front-load those into a single
live-license session; Phases 1, 3, 5 are license-free.

---

## Risk Management

**See `design.md#potential-risks` for the full analysis.** Phase-specific:

- **Phase 0 (B2 highest risk).** If the lexical join doesn't reproduce the
  parser's path, fix re-absolutization before Phase 1. If C1's import pulls in the
  JVM, the rebuild chain needs lazy imports — surface immediately, don't proceed.
- **Phase 2 (atomicity + `source_file` gotcha).** The version guard reddens every
  snapshot test until the 10 regenerate — land them together, one commit. The
  `source_file` machine-specific-path trap (normalize in the pipeline-baseline
  comparison) is the subtle one; verify no committed baseline embeds an absolute
  path.
- **Phase 2 (baseline churn masking a regression).** The pipeline-baseline diff
  should be **only** `compilability` / `auto_impl_context` (SC-10). Any other field
  changing means an unintended output shift — investigate before committing.
- **Phase 3 (B1 hidden reader).** A generation site reading a null field fails only
  at runtime on a snapshot run. The INV-4 null-fields test + INV-1 scrubbed
  subprocess are the explicit acceptance checks; B1 is already grep-confirmed in
  the design review (only a function-local import at `pipeline_builder.py:469`).

---

## Implementation Notes

[TO BE FILLED DURING IMPLEMENTATION]

### Phase 0 Completion
**Completed:** —
**B2 result (exact re-absolutization form proven):** —
**C1 result (license-absent import):** —

### Phase 1 Completion
**Completed:** —
**Actual Changes / Issues / Deviations:** —

### Phase 2 Completion
**Completed:** —
**Pipeline-baseline diff review (SC-10 effect):** —
**source_file gotcha resolution:** —

### Phase 3 Completion
**Completed:** —

### Phase 4 Completion
**Completed:** —
**SC-1 evidence (empty diff, incl. symlinked run):** —
**SC-10 evidence (chain_spike auto-impl):** —

### Phase 5 Completion
**Completed:** —
**agentic-mbse impact (none vs docs pointer):** —

---

**Status:** Draft → In Progress → Complete
