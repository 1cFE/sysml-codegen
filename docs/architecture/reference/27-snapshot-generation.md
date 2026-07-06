# 27 — Snapshot-Driven Generation

**Status:** Active · **Epic:** UPSTREAM-FINDINGS Item 2 (SC-9 + SC-10)

## Why

Generation is gated on a live syside license that expires 2026-08-06. A
**snapshot** is a versioned JSON capture of the extraction boundary — the typed
dataclasses live extraction produces, with live syside ASTs nullified and the
lowered `compilation_results` strings preserved. `generate --from-snapshot` rebuilds
the same [`PipelineContext`](02-orchestration.md#pipelinecontext) the live 7-step
sequence produces, but from JSON, so generation runs with **no license at runtime**.
The snapshot is at the *extraction* boundary, never the graph — resolution and
generation still run live from it, so a snapshot run tests the same
resolution/generation code the live run does.

## Two paths, one context

```
live:      --models         ─► build_pipeline_context()            ┐
snapshot:  --from-snapshot  ─► build_pipeline_context_from_snapshot() ├─► PipelineContext ─► run_codegen()
                                └─ snapshot.load_extraction_snapshot(path)
                                   snapshot.build_full_graph_from_snapshot(...)
```

The two syside-only context fields — `extractor`, `backtracker` — are `None` on
the snapshot path (no generation site reads them). The `sysml_codegen.snapshot`
package owns the loader, serializer, capture, and graph-rebuild helpers; only
`capture_snapshot` invokes the parser (needs a license). Module import is
license-free; the constraint is behavioral (never *invoke* the parser on the load
path).

## Format schema

Top-level keys of `extraction_snapshot.json`:

- `snapshot_format_version` (int) — gates loading. Current: **1** (`sysml_codegen.snapshot.SNAPSHOT_FORMAT_VERSION`).
- `model_name`, `captured_at` (provenance).
- `compilation_results` — `{calc_def_name: CalcDefCompilationResult}`, the lowered
  Python expression strings that let a CalcUsage stencil auto-implement (SC-10).
- `calc_defs`, `calc_usages`, `design_attributes`, `hierarchy_data`,
  `aggregation_expressions`, `computed_attributes`, `channel_aliases` — the typed
  extraction output (live syside AST fields nullified).

**`source_file` normalization (byte-identity).** Modules/schemas/stencils emit a
`SysML Source: {source_file}:{line}` header. Capture relativizes each `source_file`
against the snapshot's own directory (`output_path.parent`); the loader
re-absolutizes by a **lexical** join `Path(os.path.abspath(snapshot_dir / stored))`
— **no `.resolve()`**, so a symlinked path is reproduced exactly as the parser
reports it. Same anchor at capture and load → the round-trip reproduces the exact
absolute string live generation emits, on any machine, with nothing machine-specific
committed. Sentinels (`unknown`, `hierarchy`) pass through untouched.

## Version / provenance / freshness policy (V1–V6)

| Case | Behavior |
|---|---|
| **V1** missing `snapshot_format_version` | hard error (`SnapshotFormatError`) — recapture |
| **V2** version ≠ current | hard error — recapture |
| **V3** on-disk source hash ≠ recorded | warn per file + one end-of-run summary; run continues |
| **V4** version-current but no `compilation_results` | warn + degrade (CalcUsage auto-impl lost) |
| **V5** every snapshot run | provenance banner to log/console (never into an artifact) |
| **V6** `generate` extraction input | exactly one of `--models` / `--from-snapshot`; `--from-snapshot` + `--design-path-filter` is a hard error |

## CLI

- `sysml-codegen snapshot --models <path> [--output <file>] [--design-path-filter S]`
  — capture a versioned snapshot. Default output `<models-root>/extraction_snapshot.json`.
- `sysml-codegen generate --from-snapshot <file> [all other generate flags]` —
  license-free generation. `--models` and `--from-snapshot` are mutually exclusive
  and exactly one is required.

**Capture scripts.** Only `scripts/capture_extraction_snapshots.py` runs live
extraction (needs the syside license). `scripts/capture_pipeline_baselines.py`
and `scripts/capture_baseline_yaml.py` regenerate the graph/registry and YAML
baselines **from the committed snapshots** — license-free; the YAML script moved
off the live path in Item 11, so the YAML and graph baselines are rendered from
the same graph and can never disagree. The script docstrings are the source of
truth for this split.

## Requirements & verification matrix

REQ-SNAP-01..07 (round-trip / typed-fields / AST-None) are the prior family; this
item adds REQ-SNAP-08+.

| REQ | Requirement | Test |
|---|---|---|
| REQ-SNAP-08 | Promoted helpers live only in `src`; no second copy (INV-3) | `test_snapshot_contract::test_no_tests_helpers_snapshot_copies` |
| REQ-SNAP-09 | Missing/mismatched version is a hard error before deserialization (INV-2, V1/V2) | `test_snapshot_contract::test_{missing,wrong}_version_is_hard_error` |
| REQ-SNAP-10 | Re-captured expression-bearing snapshot carries `compilation_results` (INV-5) | `test_snapshot_contract::test_chain_spike_compilation_results_nonempty` |
| REQ-SNAP-11 | Version-current snapshot missing the section degrades with a warning (V4) | `test_snapshot_contract::test_missing_compilation_results_degrades` |
| REQ-SNAP-12 | Stale source hash warns; run continues (V3) | `test_snapshot_contract::test_stale_source_hash_warns` |
| REQ-SNAP-13 | Snapshot context has null extractor/backtracker and still generates (INV-4/B1) | `test_snapshot_generation::test_snapshot_context_has_null_extractor_and_generates` |
| REQ-SNAP-14 | `generate --from-snapshot` completes with no license at runtime (INV-1) | `test_snapshot_generation::test_generate_from_snapshot_no_license` |
| REQ-SNAP-15 | No provenance/version text in a generated artifact (INV-6) | `test_snapshot_generation::test_provenance_never_in_output` |
| REQ-SNAP-16 | CLI accepts exactly one extraction input; rejects filter + snapshot (INV-7/V6) | `test_snapshot_generation::test_generate_{neither,both}_input*`, `test_from_snapshot_rejects_design_path_filter` |
| REQ-SNAP-17 | CalcUsage auto-implements from a snapshot (SC-10) | `test_snapshot_generation::test_chain_spike_autoimpl_from_snapshot` |
| REQ-SNAP-18 | The lone `generation_timestamp` template var has zero render sites | `test_snapshot_generation::test_generation_timestamp_has_no_render_site` |
| REQ-SNAP-19 | Live generation is byte-identical to snapshot generation, incl. symlinked (SC-1) | `test_snapshot_generation::test_live_vs_snapshot_byte_identical[_symlinked]` (license-gated) |

## agentic-mbse impact

**None** beyond this docs pointer. The item adds a generation input path; the
executable SysML subset and the auditor are unchanged. This doc is the pointer
noted for agentic-mbse consumers running generation from snapshots in CI (R2).
