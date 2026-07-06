# Design: Snapshot-Driven Generation (SC-9 + SC-10)

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-05
**Branch:** upstream-findings-epic
**Commit:** 705b99d
**Complexity:** HIGH
**Epic:** UPSTREAM-FINDINGS, Item 2

---

## Overview

Promote the proven test-tree snapshot machinery into a supported `generate
--from-snapshot` path plus a `snapshot` capture command, so generation can run
without the syside license that expires 2026-08-06. Add the format-versioning,
provenance, `source_file` normalization, and `compilation_results` serialization
the snapshot needs to be a real generation contract.

## Related Artifacts

- **Spec (the contract):** `.project/active/snapshot-generation/spec.md`
- **Spec review:** `.project/active/snapshot-generation/spec-review.md`
- **Epic:** `.project/backlog/epic_upstream_findings.md` — Item 2; R1/R2/R3
- **Research:** `.project/research/20260705_upstream-findings-deep-research.md` — SC-9/SC-10
- **Doc:** `docs/architecture/reference/02-orchestration.md` — 7-step sequence, REQ-ORCH-06

## Research Findings

- **Snapshot round-trip already works.** `snapshot_serializer.py` (dataclass →
  JSON-safe dict, nullifying `_AST_FIELDS`, Path→str relative to a passed dir)
  and `snapshot_loader.py` (JSON → typed dataclasses, AST fields stay `None`)
  are exercised by ~900 conformance tests. The loader hard-codes
  `FIXTURES_DIR` and takes a `model_name` (`snapshot_loader.py:39,42`).
- **The graph-rebuild body exists but lives in a test.**
  `build_classifier_inputs_from_snapshot` / `build_full_graph_from_snapshot`
  (`test_entry_point_classifier.py:56,136`) rebuild an OutputRegistry →
  backtracker → `ComputationGraph` from a snapshot, passing
  `compilation_results=None`. They run the snapshot path without ever invoking
  the syside adapter/parser (the whole conformance suite does this license-free).
  Note: `import agentic_mbse.sysml.syside_adapter` is itself license-free
  (verified: `env -u SYSIDE_LICENSE* uv run python -c "import ..."` succeeds) —
  the license is only needed to *invoke* the parser, so "no license" is a
  runtime-behavior property, not an import-graph property.
- **Generation already consumes only the graph.** `run_codegen`
  (`cli/__init__.py:600`) reads `ctx.computation_graph` exclusively; stencil
  auto-impl reads `module.auto_impl_context` (`stencils.py:173`), which
  `build_computation_graph(..., compilation_results=...)` bakes in
  (`graph_builder.py:239`). Nothing in generation dereferences `ctx.extractor`
  or `ctx.backtracker`.
- **`compilation_results` is absent from snapshots today.** It is built at
  Step 6.5 from live ASTs (`pipeline_builder.py:540-580`) and is a
  `dict[str, CalcDefCompilationResult]` — plain dataclasses of pre-lowered
  Python strings (`expression_compiler.py:119-145`), no live AST.
- **`source_file` is the only byte-identity hazard.** Modules, schemas, and
  stencils emit `SysML Source: {module.source_file}:...`
  (`modules.py:78`, `schemas.py:43`, `stencils.py:66`); `module.source_file =
  str(calc_def.source_file)` (`graph_builder.py:1568`). Live sets it to the
  parser's **absolute** document path (`extractor.py:258`, via
  `adapter.get_source_location`); the serializer bakes it **fixtures-relative**
  (`snapshot_serializer.py:102-108`). The conformance baseline test already
  normalizes `source_file` away (`test_graph_assembly.py:536-539`), so **only
  SC-1's live-vs-snapshot diff actually compares it.** Entry-point-group paths
  use `.stem` (`parameter_groups.py:562,683`) — bare filenames, machine-independent.
- **License-skip pattern.** `_load_live_extractor` catches `ImportError` from
  `load_models()` and calls `pytest.skip` (`test_extractor.py:851-864`).

## Core Concept

A snapshot is a **versioned JSON capture of the extraction boundary** — the
typed dataclasses that live extraction produces, with live syside AST objects
nullified and the lowered `compilation_results` strings preserved. Generation
already treats `ComputationGraph` as its sole input (REQ-ORCH-06), so the whole
problem is: rebuild the same `PipelineContext` the live 7-step sequence produces,
but from JSON instead of syside.

The existing test helpers already do the hard part (rebuild the graph). This
item **promotes them into `src`**, wraps the rebuilt graph in a full
`PipelineContext` (`build_pipeline_context_from_snapshot()`), and threads the
now-serialized `compilation_results` through `build_computation_graph(...)` so
CalcUsage auto-impl survives. Two syside-only context fields — `extractor`,
`backtracker` — are set to `None`, safe because no generation path reads them.
The snapshot path may transitively import syside modules; it must never *invoke*
the adapter or parser — that is what makes it license-free at runtime.

Three additions turn the machinery into a contract:

1. **A version + provenance guard.** A top-level `snapshot_format_version` gates
   loading (any mismatch or absence → hard error, recapture). A provenance
   banner tells the operator the run came from a snapshot, not live extraction.
2. **`source_file` reconstruction.** Capture stores paths relative to the
   snapshot's own directory; the loader re-absolutizes them against that
   directory at load. A snapshot then reproduces the **exact absolute string**
   the live parser emits, on any machine, with nothing machine-specific committed.
3. **`compilation_results` serialization** (SC-10), handled by the existing
   generic serializer since the payload is already plain dataclasses of strings.

The snapshot is at the *extraction* boundary, never the graph — resolution and
generation still run live from it (spec Non-Goals), so a snapshot run tests the
same resolution/generation code the live run does.

## Key Bets

- **B1 — No generation path dereferences `ctx.extractor` or `ctx.backtracker`.**
  *If false → snapshot generation crashes with `AttributeError` on a `None`
  field.* Evidence: `run_codegen` reads only `ctx.computation_graph`; stencils
  read `module.auto_impl_context`; fusion-tea already generates with
  `extractor=None`. Verifying this exhaustively is in scope (grep + a
  null-fields generation test).
- **B2 — The parser's `source_file` for a document equals the lexical absolute
  path of that document beside the snapshot, so a lexical join of
  `snapshot_dir` with the stored relative (no symlink resolution, D8)
  reproduces it byte-for-byte.** *If false → SC-1's tree diff fails on the
  `SysML Source:` header lines and byte-identity is unproven.* This is the
  riskiest bet; de-risk first on a symlinked path (see Handoff).
- **B3 — `compilation_results` is entirely pre-lowered strings and plain
  dataclasses, with no live AST field.** *If false → the serializer nullifies
  real data and SC-10 auto-impl is silently lost.* Evidence:
  `CalcDefCompilationResult` / `CompilationResult` fields are `str`/`list[str]`/
  enums only (`expression_compiler.py:119-145`).

## Key Decisions

- **D1 — `source_file` normalization: relativize at capture, re-absolutize at
  load, both against the snapshot file's own directory (`output_path.parent`).**
  Capture writes each `source_file` relative to `output_path.parent` (the
  directory the snapshot is written into — not the models-root, which may differ
  from `--output`); the loader rebuilds `source_file` by a **lexical** absolute
  join of `snapshot_path.parent` with the stored relative — no `.resolve()`, so
  symlinks are preserved (see M2/D8). Because capture and load use the same
  anchor, the round-trip is exact by construction for any `--output` destination.
  *Rejected:* anchoring on the models-root (diverges from the snapshot location
  when `--output` points elsewhere); storing the absolute path verbatim
  (machine-specific, uncommittable); normalizing live emission to relative
  (forbidden — alters live output, spec Non-Goal); stripping `source_file` from
  output (alters output, loses provenance).
- **D2 — `build_pipeline_context_from_snapshot()` is new assembly in
  `orchestration/snapshot_context.py`, built on the promoted graph-rebuild body.**
  *Rejected:* renaming the helper (it returns a `ComputationGraph` + inputs dict,
  not a `PipelineContext`, and passes `compilation_results=None`); putting it in
  `pipeline_builder.py` (risks an import tangle with the promoted `snapshot/`
  package — a separate module keeps the dependency one-directional).
- **D3 — New package `sysml_codegen/snapshot/` owns loader, serializer, capture,
  and the promoted graph-rebuild helpers; it never invokes syside on the load
  path.** (It may transitively import syside modules — that import is
  license-free; the constraint is behavioral, not import-graph.) The public API
  re-exports every promoted name so each test migrates with a one-line import
  swap. *Rejected:* leaving a re-export shim in `tests/helpers/` (spec HARD: no
  two copies).
- **D4 — `snapshot_format_version` is an integer, `SNAPSHOT_FORMAT_VERSION = 1`,
  top-level alongside `model_name` / `captured_at`; the constant lives in
  `snapshot/__init__.py`.** *Rejected:* a semantic string (there is no
  partial-compat semantics — any mismatch is a hard error, so an integer counter
  is exactly enough).
- **D5 — Capture CLI: `sysml-codegen snapshot --models <path>
  [--output <file>] [--design-path-filter S]`; default output
  `<models-root>/extraction_snapshot.json`.** `source_file` is relativized
  against the chosen `--output` location (D1), so the default and any custom
  `--output` both round-trip exactly. *Rejected:* a per-model directory layout
  (models are already directories; a single file beside the sources matches the
  committed layout and keeps the default re-absolutization anchor next to the
  source files).
- **D6 — Source-freshness is warn-and-continue only; no `--strict` flag this
  item.** *Rejected:* adding `--strict` now (YAGNI — add it when a concrete CI
  consumer needs a stale snapshot to fail the build).
- **D7 — New reference doc `27-snapshot-generation.md`, plus a pointer from
  doc 02's PipelineContext section.** *Rejected:* extending doc 02 (a different
  concern — doc 02 is the live 7-step sequence; the snapshot format is its own
  schema/versioning/provenance story).
- **D8 — Re-absolutize by a lexical join, not `.resolve()`.** The loader builds
  `source_file = Path(os.path.abspath(snapshot_path.parent / stored))` — lexical
  normalization of `.`/`..`, made absolute — and does **not** resolve symlinks.
  *Rejected:* `Path.resolve()` (it canonicalizes symlinks — if the parser reports
  the symlinked path but `.resolve()` returns the real path, SC-1's header diff
  fails). B2's de-risk probe must run on a **symlinked** source path specifically,
  since that is where the two forms diverge.

## Architecture

Two entry paths converge on one `PipelineContext`, after which generation is
identical:

```
                            live:  --models  ─► build_pipeline_context()  ┐
                                                (syside, Steps 1–7)        │
                                                                           ├─► PipelineContext ─► run_codegen()
  snapshot: --from-snapshot ─► build_pipeline_context_from_snapshot()  ────┘        (unchanged generation)
                                └─ snapshot.load_extraction_snapshot(path)
                                   snapshot.build_full_graph_from_snapshot(...)
                                   (+ compilation_results, extractor/backtracker=None)
```

- **Capture (write path):** `snapshot.capture_snapshot()` runs the live
  `build_pipeline_context()` once, then `serialize_extraction_snapshot()` with
  `compilation_results` added and `source_file` relativized to `output_path.parent`.
  This is the only license-requiring code in the new package; it is lifted from
  `scripts/capture_extraction_snapshots.py:_capture_full_pipeline`.
- **Load (read path):** `load_extraction_snapshot(snapshot_path)` — version
  guard first, then deserialize, re-absolutize `source_file`, deserialize or
  degrade `compilation_results`, emit per-file freshness warnings and record how
  many files were stale (so the caller can log one end-of-run summary).
- **Assemble:** `build_pipeline_context_from_snapshot()` rebuilds the graph from
  the loaded snapshot (promoted helper), threads `compilation_results` into
  `build_computation_graph`, wraps a `PipelineContext` with `extractor=None`,
  `backtracker=None`, logs the provenance banner once, and — if the loader
  flagged any stale-source files — logs one end-of-run freshness summary
  ("N of M source files no longer match; recapture to refresh") in addition to
  the per-file warnings.
- **Generate:** `run_codegen` is unchanged; the CLI picks the builder by which
  flag was supplied.

## Required Invariants

- **INV-1** `generate --from-snapshot` completes with **no license available at
  runtime** — verified by an env-scrubbed subprocess conformance test (scrub
  `SYSIDE_LICENSE_KEY` and siblings before invoking generation). The package may
  transitively import syside modules; it must never invoke the adapter/parser on
  the snapshot path. (Not a static import-grep — module import is license-free.)
- **INV-2** A snapshot with a `snapshot_format_version` that is missing or ≠
  `SNAPSHOT_FORMAT_VERSION` raises `SnapshotFormatError` **before** any
  field deserialization.
- **INV-3** No two copies: `tests/helpers/snapshot_loader.py` and
  `snapshot_serializer.py` are deleted; `grep -r "tests.helpers.snapshot"`
  returns zero; the promoted helpers exist only in `sysml_codegen/snapshot/`.
- **INV-4** A `PipelineContext` from a snapshot has `extractor is None` and
  `backtracker is None`, and `run_codegen` still succeeds on it.
- **INV-5** For a re-captured `chain_spike_model` snapshot,
  the loaded `compilation_results` is non-empty and the generated CalcUsage
  stencils are auto-implemented (no `NotImplementedError`, `compilability` set).
- **INV-6** No provenance/version/freshness text ever reaches a generated
  artifact — it goes to the log/console only.
- **INV-7** `generate` accepts exactly one of `--models` / `--from-snapshot`;
  neither or both is a hard CLI error, and `--design-path-filter` +
  `--from-snapshot` is a hard CLI error.

## Component Overview

- **`sysml_codegen/snapshot/__init__.py`** — public API re-exports;
  `SNAPSHOT_FORMAT_VERSION = 1`; `SnapshotFormatError`.
- **`snapshot/serializer.py`** — moved `snapshot_serializer.py`. Adds:
  `snapshot_format_version` + provenance fields to the top-level dict; a
  `compilation_results` block; `source_file` relativization to a passed
  `output_dir` = `output_path.parent` (replacing the fixtures-dir assumption).
- **`snapshot/loader.py`** — moved `snapshot_loader.py`, signature changed to
  `load_extraction_snapshot(snapshot_path: Path)`. Adds: version guard,
  `source_file` re-absolutization, `compilation_results` deserialize-or-degrade,
  freshness warning. Adds deserializers `_deserialize_compilation_result` /
  `_deserialize_calc_def_compilation_result`.
- **`snapshot/graph_rebuild.py`** — promoted `build_classifier_inputs_from_snapshot`
  and `build_full_graph_from_snapshot`, taking a loaded snapshot dict (or a
  `snapshot_path`). Never invokes syside (transitive imports are fine).
- **`snapshot/capture.py`** — `capture_snapshot(model_paths, output_path,
  design_path_filter)` lifted from `_capture_full_pipeline`.
- **`orchestration/snapshot_context.py`** — `build_pipeline_context_from_snapshot(
  snapshot_path) -> PipelineContext`; provenance banner.
- **`cli/__init__.py`** — required mutually-exclusive `--models`/`--from-snapshot`
  group; `--from-snapshot` guard against `--design-path-filter`; `cmd_snapshot`
  subcommand; `GenerationConfig` gains `from_snapshot: Path | None`.
- **`docs/architecture/reference/27-snapshot-generation.md`** — format schema,
  REQ-SNAP-* table (numbering starts at **REQ-SNAP-08** — 01–07 are taken),
  version/provenance/freshness policy.
- **Deleted:** `tests/helpers/snapshot_loader.py`,
  `tests/helpers/snapshot_serializer.py`. `scripts/capture_extraction_snapshots.py`
  is rewritten to call `snapshot.capture_snapshot` (or removed in favor of the CLI).

## Non-Goals

- Snapshotting at the `ComputationGraph` level (spec Non-Goal — would freeze
  resolution).
- Serializing syside ASTs (impossible; SC-10 serializes lowered strings).
- Changing what live generation emits — byte-identical is the bar.
- A `--strict` freshness flag (D6), or new fixtures for un-snapshotted shapes.
- Re-capturing the 10 snapshots as an Item-2 license operation beyond the
  format migration — SC-10's proof rides `chain_spike_model`, already committed.

## Implementation Notes

- **Version guard runs first.** In `load_extraction_snapshot`, read
  `raw.get("snapshot_format_version")` and raise `SnapshotFormatError` before
  touching any other key. This and the 10-snapshot regeneration land in **one
  change** (INV-2 would redden every snapshot test otherwise) — this landing
  stands on its own; Item 1 committed no extraction snapshots (see Integration
  Strategy).
- **`compilation_results` shape.** Serialize under a top-level
  `"compilation_results"` key as `{calc_def_name: <CalcDefCompilationResult
  dict>}`. The generic `_serialize_value` already handles the nested dataclasses.
  Loader: if the key is absent → `logger.warning(...)` + `{}` (degrade, SC-10
  lost, today's behavior); if present → deserialize to
  `dict[str, CalcDefCompilationResult]`.
- **`source_file` re-absolutization (D1, D8).** Loader converts each deserialized
  `source_file` via a lexical join `Path(os.path.abspath(snapshot_path.parent /
  stored))` — **no `.resolve()`** (symlinks stay as the parser reports them).
  Keep the `"unknown"` / `"hierarchy"` sentinels untouched (they are not real
  paths). Capture relativizes against `output_path.parent`, not `FIXTURES_DIR` —
  the same anchor the loader re-absolutizes against, so the round-trip is exact
  by construction.
- **Signature change fan-out.** `load_extraction_snapshot(model_name)` →
  `load_extraction_snapshot(snapshot_path)`. Test call sites pass a fixtures
  path via a single conftest helper (see Appendix B) — mechanical, regex-able.
- **CLI mechanism.** Replace `--models required=True` (`cli/__init__.py:513`)
  with `gen_parser.add_mutually_exclusive_group(required=True)` holding
  `--models` and `--from-snapshot`; both-forbidden / neither-forbidden /
  exactly-one-required come free. Reject `--from-snapshot` + `--design-path-filter`
  explicitly in `cmd_generate`.
- **Dead-template trap.** `generation_timestamp` in
  `templates/pydantic_schema.py.jinja2:8` has zero render sites. Leave it
  provably unwired (or delete it) and add a guard test asserting no render site
  — wiring it would break byte-identity.

Interface sketches (design-level, not implementation):

```python
# sysml_codegen/snapshot/__init__.py
SNAPSHOT_FORMAT_VERSION = 1
class SnapshotFormatError(Exception): ...
def load_extraction_snapshot(snapshot_path: Path) -> dict[str, Any]: ...
def serialize_extraction_snapshot(*, models_root: Path, compilation_results, ...) -> dict: ...
def capture_snapshot(model_paths, output_path: Path, design_path_filter="") -> Path: ...
def build_full_graph_from_snapshot(snapshot_path: Path) -> tuple[ComputationGraph, dict]: ...

# orchestration/snapshot_context.py
def build_pipeline_context_from_snapshot(snapshot_path: Path) -> PipelineContext: ...
```

## Potential Risks

- **B2 wrong (highest).** If the lexical join does not reproduce the parser's
  exact string (`file://` URI, case, trailing form, or a symlink the parser
  canonicalizes differently), SC-1 fails. Mitigation: de-risk first — capture
  solar_battery **on a symlinked source path**, run one live-vs-snapshot diff
  while the license is live, and adjust the re-absolutization to match the
  parser's exact rendering before building the rest.
- **Pipeline-baseline regeneration.** Item 1 rewrote
  `scripts/capture_pipeline_baselines.py` to rebuild graphs from committed
  snapshots via `build_full_graph_from_snapshot`. When Item 2 promotes that
  helper body and adds `compilation_results`, the pipeline baselines regenerate
  deliberately (the script docstring already flags this). Mitigation: migrate
  the baseline-capture script to the promoted `sysml_codegen.snapshot` module and
  re-run it as part of this item; expect and review the baseline diff.
- **Import cycle.** `snapshot/graph_rebuild.py` imports `orchestration/
  output_registry_builder`; `orchestration/snapshot_context.py` imports
  `snapshot/`. Keep the context builder in its own module (D2) so the edge is
  one-directional (`orchestration → snapshot`, never back).
- **Hidden `ctx.extractor` reader (B1).** A generation site that reads a null
  field would only fail at runtime on a snapshot run. Mitigation: grep +
  null-fields generation test as an explicit acceptance check.

## Integration Strategy

The live path is untouched: `build_pipeline_context()` and `run_codegen` keep
their signatures and behavior. `--from-snapshot` is purely additive — it swaps
the *extraction input*, not the generation configuration, so `--output`,
`--package-name`, `--overwrite`, `--preserve-handwritten`, `--smart-regen`, etc.
all apply unchanged. The ~900 conformance tests keep loading snapshots through
the same functions, now imported from `src` (INV-3). The capture command
supersedes `scripts/capture_extraction_snapshots.py`, which becomes a thin
wrapper or is retired.

**Item 1 interaction.** Item 1 committed **no extraction snapshots** (its landed
commit added only `baseline_yaml`, `baseline_outputs`, and the `zero_output_calc`
fixture sources) — so there is no concurrent-unversioned-capture hazard, and the
loader-guard + 10-snapshot regeneration land on their own. The one real coupling
is `scripts/capture_pipeline_baselines.py`, which Item 1 rewrote to rebuild
graphs from committed snapshots via `build_full_graph_from_snapshot`; when Item 2
promotes that helper and adds `compilation_results`, the pipeline baselines
regenerate deliberately (Potential Risks), and the script migrates to the
promoted module.

## Validation Approach

- **SC-1 (byte-identical), license-gated.** A test that runs live
  `generate --models <abs solar_battery>` and `generate --from-snapshot`,
  then does a recursive tree diff of the two output dirs (empty diff).
  Skips cleanly on `ImportError` from `load_models` (no license). Run it at
  least once while the license is live, **including once on a symlinked source
  path** (D8/B2). Feed live an **absolute** `--models` path so the parser emits
  the absolute form D1 reconstructs.
- **SC-10 (auto-impl preserved).** Against a re-captured `chain_spike_model`
  snapshot: assert `compilation_results` non-empty (INV-5), stencils
  auto-implemented, `compilability` set — matching live. License-free once the
  snapshot is committed.
- **Version guard (INV-2).** Unit tests: missing-version → `SnapshotFormatError`;
  wrong-version → `SnapshotFormatError`; message names the recapture fix.
- **Freshness / degrade.** Mutated-source-hash snapshot → warning, run continues;
  a version-current snapshot lacking `compilation_results` → warning + degrade.
- **CLI (INV-7).** Both flags → error; neither → error; `--from-snapshot` +
  `--design-path-filter` → error.
- **No-two-copies (INV-3).** `grep -r "tests.helpers.snapshot"` returns zero.
- **License-free runtime (INV-1).** An env-scrubbed subprocess test runs
  `generate --from-snapshot` with `SYSIDE_LICENSE_KEY` et al. unset and asserts
  success — proving the snapshot path never invokes the parser.
- **Provenance never in output (INV-6).** Assert generated files contain no
  banner/`captured_at`/version text.
- **Full suite green** against the 10 regenerated versioned snapshots.

## Next-Stage Handoff

- **Fixed:** the package layout (D3), the context-builder location and null
  extractor/backtracker (D2, B1), the version policy (D4 + spec), the CLI
  mechanism (INV-7), the doc target (D7).
- **Open (plan decides ordering):** exact conftest helper name for fixtures-path
  resolution; whether `scripts/capture_extraction_snapshots.py` is retired or
  wrapped; error-text wording (Appendix A is the starting catalog).
- **De-risk first (do before anything else):** B2 — capture solar_battery **on a
  symlinked source path** and run the live-vs-snapshot diff on the `SysML Source:`
  headers while the license is live. If the lexical join doesn't match, fix the
  re-absolutization before building capture/CLI/migration on top of it. Everything
  else is mechanical once `source_file` reconstruction is proven.
- **Atomicity constraint:** loader version-guard + 10-snapshot regeneration in
  one change (no external sequencing dependency — Item 1 shipped no snapshots).

## agentic-mbse impact

**None** (beyond a possible docs pointer). This item adds a generation input
path; the executable SysML subset, the auditor, and what models should look like
are unchanged. If `27-snapshot-generation.md` is useful to agentic-mbse
consumers running generation from snapshots in CI, note it as a docs pointer at
close-out (R2). Confirm "none vs docs pointer" then.

## Design-Review Resolutions

Applied from `design-review.md` (verdict: Revise):

- **C1 (critical) — accepted, empirically settled.** `import
  agentic_mbse.sysml.syside_adapter` is license-free; only invoking the parser
  needs a license. Dropped the "syside-free imports" claim and the static-grep
  INV-1. INV-1 is now behavioral: `generate --from-snapshot` completes with no
  license at runtime, verified by an env-scrubbed subprocess test. The package
  may transitively import syside; it must never *invoke* the adapter/parser on
  the load path.
- **M1 — accepted.** `source_file` relativizes against the snapshot's own output
  location (`output_path.parent`), not the models-root — exact by construction
  for any `--output` (D1, D5).
- **M2 — accepted.** Re-absolutization is a lexical absolute join, no symlink
  resolution (new **D8**); B2's de-risk probe must run on a symlinked path.
- **M3 — accepted.** Deleted the "Item 1 emits unversioned snapshots" premise
  (Item 1 committed no extraction snapshots). Recorded the real coupling: Item 1's
  `scripts/capture_pipeline_baselines.py` rebuilds graphs from committed snapshots
  via the promoted helper, so pipeline baselines regenerate deliberately and the
  script migrates to `sysml_codegen.snapshot`.
- **M4 — accepted.** Conftest fixtures helper kept (Appendix B).
- **M5 — accepted.** REQ-SNAP numbering starts at **08** (01–07 taken).
- **M6 — accepted.** Freshness warnings also summarized once at end of run
  (V3, Architecture Assemble step).

---

## Appendix A — Error / warning text catalog (V1–V6 style)

- **V1 (hard, missing version).** `SnapshotFormatError`: "Snapshot <path> has no
  snapshot_format_version — it predates versioned snapshots. Recapture with
  `sysml-codegen snapshot --models <sources>` (current tooling writes version
  {SNAPSHOT_FORMAT_VERSION})."
- **V2 (hard, wrong version).** `SnapshotFormatError`: "Snapshot <path> is format
  version {found}, tool expects {SNAPSHOT_FORMAT_VERSION}. Recapture with
  `sysml-codegen snapshot`."
- **V3 (warn, stale source).** Per file: "Snapshot <path> source hash for <file>
  no longer matches on-disk source — snapshot may be stale. Continuing; recapture
  to refresh." Plus one end-of-run summary: "N of M snapshot source files no
  longer match on-disk source; recapture to refresh."
- **V4 (warn, degrade).** "Snapshot <path> has no compilation_results section
  (captured before SC-10). CalcUsage auto-implementation will be lost; stencils
  fall back to NotImplementedError. Recapture to restore."
- **V5 (info, provenance banner).** "Generating from snapshot <path> (model
  <name>, captured <captured_at>, source <models_root>). This run did NOT use
  live extraction."
- **V6 (hard, CLI).** "generate requires exactly one of --models / --from-snapshot"
  and "--design-path-filter cannot be combined with --from-snapshot (the filter
  is baked into the snapshot at capture)."

## Appendix B — Test migration surface

Two mechanical edits per file (regex-able), import surface is one line:

- `from tests.helpers.snapshot_loader import load_extraction_snapshot`
  → `from sysml_codegen.snapshot import load_extraction_snapshot` (~15 files)
- `from tests.conformance.test_entry_point_classifier import
  (build_full_graph_from_snapshot, build_classifier_inputs_from_snapshot)`
  → `from sysml_codegen.snapshot import (...)` (~11 files)
- Call-site: `load_extraction_snapshot("solar_battery_model")`
  → `load_extraction_snapshot(snapshot_fixture("solar_battery_model"))`, where
  `snapshot_fixture(name)` is a single conftest helper returning
  `FIXTURES_DIR / name / "extraction_snapshot.json"`. Same shape for the two
  promoted graph helpers.
- `test_entry_point_classifier.py`: delete the two helper defs (now in
  `snapshot/graph_rebuild.py`); import them from `sysml_codegen.snapshot`.
- Capture scripts / spikes under `scripts/` update their imports the same way.

---

**Next Step:** After approval → `/_my_plan` (multi-phase; de-risk B2 first).
