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

- `snapshot_format_version` (int) — gates loading. Current: **5** (`sysml_codegen.snapshot.SNAPSHOT_FORMAT_VERSION`, `snapshot/__init__.py:28`).
- `model_name`, `captured_at` (provenance).
- `constraint_facts` — the neutral `ConstraintFacts` (agentic-mbse Item 1),
  serialized via `agentic_mbse.sysml.constraint_facts.serialize`. Always present
  (v3). The extraction-boundary predicate facts the offline path re-lowers from.
- `part_occurrences` — `{owner_eqn: [occurrences]}`, the resolved per-owner
  occurrence table: the successful capture-time prepared batch's
  `occurrence_transcript`. Only admitted `part_def` owners appear — an excluded or
  unsupported owner is never queried, so its absence is correct rather than
  corruption. `{}` when lowering did not run. Owner keys emitted sorted (INV-7/MF4).
- `constraint_lowering_mode` — `"applied"` or `"grandfathered_off"` (Item 8, D3),
  always present. `"grandfathered_off"` means the snapshot was captured with
  lowering disabled and the offline path must skip re-lowering loudly, never infer
  it from an empty section.
- `compilation_results` — `{calc_def_name: CalcDefCompilationResult}`, the lowered
  Python expression strings that let a CalcUsage stencil auto-implement (SC-10).
- `calc_defs`, `calc_usages`, `design_attributes`, `hierarchy_data`,
  `aggregation_expressions`, `computed_attributes`, `channel_aliases` — the typed
  extraction output (live syside AST fields nullified).

**`source_file` portable referent (v5, byte-identity).** Modules/schemas/stencils
emit a `SysML Source: {source_file}:{line}` header. Capture maps each real
`source_file` to a portable `root-N/<relpath>` referent — the model root it lives
under, indexed by capture order, plus its path within that root
(`serializer.py:277-282` via `map_live_source_referent`, `analysis/source_referent.py`).
The loader validates the referent shape at load and reconstructs **no** absolute
path; the referent string is what generation emits verbatim
(`loader.py` `_validate_source_referents` via `validate_snapshot_source_referent`).
Generated output therefore carries no checkout-absolute bytes and is byte-identical
across checkout roots, without any same-machine cancellation. A field-less,
absolute, or snapshot-relative `source_file` is rejected loudly at load rather than
silently loaded (`SnapshotFormatError`). Sentinels (`unknown`, `hierarchy`) are not
real paths and pass through untouched (`serializer.py:55-56`).

## Version / provenance / freshness policy (V1–V6)

| Case | Behavior |
|---|---|
| **V1** missing `snapshot_format_version` | hard error (`SnapshotFormatError`) — recapture |
| **V2** version ≠ current | hard error — recapture |
| **V3** on-disk source hash ≠ recorded | warn per file + one end-of-run summary; run continues |
| **V4** version-current but no `compilation_results` | warn + degrade (CalcUsage auto-impl lost) |
| **V5** every snapshot run | provenance banner to log/console (never into an artifact) |
| **V6** `generate` extraction input | exactly one of `--models` / `--from-snapshot`; `--from-snapshot` + `--design-path-filter` is a hard error |
| **V7** missing load-bearing field on a deserialized dict | not silently defaulted. A type/wiring/scoping field (`python_type`, `binding_type`, `parent_part_path`, `owning_part_def_qn`) warns and degrades to its default; a **keying** field (`qualified_name` on a calc usage or design attribute) raises `SnapshotFormatError` — a silent default would mis-key the output registry. The benign majority (`is_input`, `unit`, `source_line`, list fields, …) keeps its `.get(default)` untouched. TRUTH-DEBT Item 6, Site 1. |

**Format migrations (v2 → v5).** v3 added the three top-level constraint sections
above (`constraint_facts`, `part_occurrences`, `constraint_lowering_mode`) so the
offline path can re-lower modeled assertions without a license (CONSTRAINT-EXEC
Item 8). The format has since advanced twice: v4 carried the diagnostic-severity
field through the wire shape (constraint-lifecycle Item 4), and v5 replaced the
snapshot-relative `source_file` with the portable `root-N/<relpath>` referent
behind a load-time shape gate (constraint-lifecycle Item 5). The authoritative
history is `snapshot/__init__.py:12-28`. The version gate is a hard cutover, not a
compatibility shim: there is **no cross-version coexistence** (V1/V2 above), so any
snapshot whose version is not the current 5 is a hard error and every committed
snapshot is re-captured at the current version in the same change. The loader never
up-migrates an old snapshot in place.

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
| REQ-SNAP-20 | A missing load-bearing field on a deserialized dict is loud (V7): `python_type`/`binding_type`/`parent_part_path`/`owning_part_def_qn` warn and degrade; `qualified_name` (keying) raises `SnapshotFormatError`; benign fields keep their default silently (TRUTH-DEBT Item 6, Site 1) | `test_hygiene_tail_loader.py` (fires-on-shape/raise + silent-on-clean) |

## agentic-mbse impact

Snapshot generation has a coordinated agentic-mbse boundary. Snapshot re-lowering consumes the
companion's serialized constraint-fact and expression-IR schemas and applies executable-profile
v4 behavior to those facts (`PROFILE_SEMANTIC_VERSION = "executable-profile/v4"`,
`_upstream_pins.py:33`). A snapshot can therefore remain format-current while an incompatible
companion changes the meaning or shape of the data codegen consumes.

The package floor and the runtime/schema guards protect different failure modes. The
`agentic-mbse>=0.1.2` distribution requirement (`pyproject.toml:24`) prevents a resolver from
selecting a companion release predating the pinned profile. Runtime guards still pin
`PROFILE_SEMANTIC_VERSION`,
`CONSTRAINT_FACTS_SCHEMA_VERSION`, and `EXPRESSION_IR_SCHEMA_VERSION` so an installed companion
whose code drifts behind unchanged package metadata fails loudly at the boundary. Snapshot-format
validation remains separate: it protects the captured envelope and required fields, not companion
package selection or executable-profile meaning.
