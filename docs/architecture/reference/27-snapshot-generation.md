# 27 — Snapshot-Driven Generation

**Status:** Active · **Format:** v6 instance-graph snapshot · **Supersedes:** the v5
extraction snapshot, whose code and fixtures were deleted by the Item 7 retirement (see
[The v5 extraction snapshot](#the-v5-extraction-snapshot-historical) below)

## Why

Generation must be able to run without a live syside license. A **snapshot** is a
self-contained, license-free capture of one elaborated `InstanceGraph`, sealed into an
envelope. `generate --from-snapshot` loads it and projects it; nothing about the loaded graph
needs the model tree, a parser, or a licence.

The snapshot is at the **instance-graph** boundary, not the extraction boundary. That is the
load-bearing change from v5: the semantics are already resolved when the file is written, so
what the offline run reproduces is a decided graph rather than a re-derivation from strings.
Capture is the only step that can establish that the sealed graph came from the sealed sources,
so capture elaborates and seals in one step (`snapshot/capture.py:93`).

## Three routes, one authority

```
live:      --models         ─► elaborate_model_paths()          ┐
                                                                 ├─► InstanceGraph ─► seal ─►
snapshot:  --from-snapshot  ─► load_instance_graph_snapshot()   ┘   ExactPipelineContext
                                                                            │
capture:   sysml-codegen snapshot ─► admit_sources()                        ▼
                                     ─► elaborate_admitted_sources()     project() ─► generate
                                     ─► build_envelope() ─► atomic write
```

`build_exact_pipeline_context` and `build_exact_pipeline_context_from_snapshot`
(`orchestration/exact_pipeline_context.py`) are the two builders, and they differ only in where
the graph comes from. Both seal it, and every read re-decodes and re-projects the sealed bytes
and refuses anything the receipt disagrees with. See [02-orchestration](02-orchestration.md).

Capture writes atomically: on any refusal — an unadmissible source tree, a model that does not
elaborate cleanly, a graph that is not projectable — nothing is written and an existing file at
the output path is left untouched.

**Capture is deterministic.** The same model in the same environment produces byte-identical
snapshot files.

**The routes agree byte-for-byte.** Every graph node's `source_file` is the portable
`root-N/<relpath>` referent on both routes: capture rewrites it against the sealed admission
manifest, and the live route rewrites it against the caller's model roots
(`orchestration/elaborated_pipeline.py`, via `analysis/source_referent.py`) — same shape, each
route deriving it from the evidence it has. Generation from a model tree and generation from a
snapshot of that tree therefore write identical bytes, `SysML Source:` comments included
(lifecycle-contract invariants 34–35; pinned by
`test_exact_route_generated_package.py::test_the_two_packages_are_byte_identical` and
`test_exact_route_fingerprint_stability.py`).

## What a sealed snapshot may claim

This is the part to read before relying on a snapshot for anything but structure.
`integrity.digest` is an **unkeyed** SHA-256. Anyone who edits the file recomputes it, so the
digest proves the document is *coherent* — nobody changed one part and left the rest stale —
and never that it is *authentic*. Every refusal in the envelope is written to survive a forger
who re-seals properly (`snapshot/envelope.py:1-53`).

**Anchored** — a forger cannot make these say something false and get past the loader:

| Kind | Fields | Checked against |
|---|---|---|
| Constants this build defines | `format`, `version`, the profile markers (`certifiability_profile`, `instance_graph_schema`, `expression_ir_schema`, `executable_profile`, `projector_semantics`) | the constants |
| Environment facts | SysIDE version, `sysml_codegen` and `agentic_mbse` versions, the pinned standard-library digest and count | the process doing the loading |
| The graph | the whole `instance_graph` section | re-derived by the codec; must be projectable and diagnostic-free |

**Not anchored** — `sources` is a self-declared manifest: a referent, size, and SHA-256 per
file, checked for canonical form but never against the files themselves. Offline, the loader
only cross-checks that every graph row's `source_file` appears in it. So a re-sealed snapshot
can be re-labelled — the sealed referents renamed consistently across the manifest and every
graph row, a fabricated row appended, or a real row's digest restated — and it will load.
**Those three shapes are pinned as accepted behaviour in the conformance matrix**
(`tests/conformance/test_snapshot_v6_envelope.py`) so the limit is stated rather than implied
away.

**Passing `source_roots` is what closes them.** The admission is then recomputed from the model
tree on disk and must reproduce the sealed manifest exactly, which catches all three. A caller
that needs provenance, rather than only structure, must supply `source_roots`
(`build_exact_pipeline_context_from_snapshot(..., source_roots=...)`).

**What no amount of checking can prove offline.** That the sealed graph really *is* the
elaboration of the sealed sources means elaborating them again, which needs the parser and a
licence. Even `source_roots` only proves the sources are the ones named. That proof belongs to
capture, which elaborates and seals in one step.

The receipt on `ExactPipelineContext` is a self-consistency check on the same footing: it
catches a context whose authority moved underneath it — an in-place edit, a partially
constructed object, a projector whose semantics changed between reads. It cannot make a
snapshot's own claims about its sources true, and that limit is recorded at
`orchestration/exact_pipeline_context.py:23-28` rather than left to be discovered.

## The v5 refusal

A v5 extraction snapshot carries no `version` key, so it is refused at load by name rather
than by a confusing `None`: *"this is a v5 extraction snapshot, but the instance-graph route
requires snapshot v6. Recapture with `sysml-codegen snapshot`."* There is no cross-version
coexistence and no in-place up-migration.

## CLI

- `sysml-codegen snapshot --models <path> [--output <file>]` — capture one v6 instance-graph
  snapshot. Default output `<models-root>/instance_graph_snapshot.json`. Needs the live
  licence.
- `sysml-codegen generate --from-snapshot <file> [all other generate flags]` — license-free
  generation. `--models` and `--from-snapshot` are mutually exclusive and exactly one is
  required (a required argparse group, so both-forbidden and neither-forbidden come free).

`scripts/capture_v6_batch.py` produces the proposed v6 recapture batch for the 37-fixture
corpus through that same `capture_instance_graph_snapshot` entry point, so the batch cannot
drift from the product. A fixture the exact route refuses gets a typed refusal record in the
batch manifest rather than a snapshot. **The owner accepted that batch** (disposition of 2026-08-11, step 1); the script produces
readiness, not authority, and `--verify` re-derives it byte for byte on demand.

## The v5 extraction snapshot (historical)

Everything below describes the **v5 extraction snapshot**. Its code — `snapshot/loader.py`,
`serializer.py`, `graph_rebuild.py`, `capture_snapshot` — and every committed
`extraction_snapshot.json` fixture were **deleted** by the Item 7 retirement (2026-08-12,
`19072ad` / `82c7951` / `882fc8d` / `3071fba`). Nothing in the tree reads or writes the format,
and `generate --from-snapshot` refuses a v5 document by name. This section is retained as the
record of what that format was, so a v5 file found outside the tree can still be read. It is
not a description of anything the product does.

### Format schema (v5)

Top-level keys of `extraction_snapshot.json`:

- `snapshot_format_version` (int) — gates loading. Current: **5** (`sysml_codegen.snapshot.SNAPSHOT_FORMAT_VERSION`, `snapshot/__init__.py:30`).
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

### Version / provenance / freshness policy, v5 (V1–V7)

| Case | Behavior |
|---|---|
| **V1** missing `snapshot_format_version` | hard error (`SnapshotFormatError`) — recapture |
| **V2** version ≠ current | hard error — recapture |
| **V3** on-disk source hash ≠ recorded | warn per file + one end-of-run summary; run continues |
| **V4** version-current but no `compilation_results` | warn + degrade (CalcUsage auto-impl lost) |
| **V5** every snapshot run | provenance banner to log/console (never into an artifact) |
| **V6** `generate` extraction input | exactly one of `--models` / `--from-snapshot`. The paired `--design-path-filter` refusal is now argparse's: Gate 4B-G0 removed the flag, so it is rejected before a snapshot is opened. Still a hard error, never a silent no-op |
| **V7** missing load-bearing field on a deserialized dict | not silently defaulted. A type/wiring/scoping field (`python_type`, `binding_type`, `parent_part_path`, `owning_part_def_qn`) warns and degrades to its default; a **keying** field (`qualified_name` on a calc usage or design attribute) raises `SnapshotFormatError` — a silent default would mis-key the output registry. The benign majority (`is_input`, `unit`, `source_line`, list fields, …) keeps its `.get(default)` untouched. TRUTH-DEBT Item 6, Site 1. |

**Format migrations (v2 → v5).** v3 added the three top-level constraint sections
above (`constraint_facts`, `part_occurrences`, `constraint_lowering_mode`) so the
offline path can re-lower modeled assertions without a license (CONSTRAINT-EXEC
Item 8). The format has since advanced twice: v4 carried the diagnostic-severity
field through the wire shape (constraint-lifecycle Item 4; the severity contract
that field carries is [30-diagnostic-severity](30-diagnostic-severity.md)), and v5
replaced the
snapshot-relative `source_file` with the portable `root-N/<relpath>` referent
behind a load-time shape gate (constraint-lifecycle Item 5). The authoritative
history is `snapshot/__init__.py:12-28`. The version gate is a hard cutover, not a
compatibility shim: there is **no cross-version coexistence** (V1/V2 above), so any
snapshot whose version is not the current 5 is a hard error and every committed
snapshot is re-captured at the current version in the same change. The loader never
up-migrates an old snapshot in place.

### Capture scripts (v5)

Only `scripts/capture_extraction_snapshots.py` runs live
extraction (needs the syside license). `scripts/capture_pipeline_baselines.py`
and `scripts/capture_baseline_yaml.py` regenerate the graph/registry and YAML
baselines **from the committed snapshots** — license-free; the YAML script moved
off the live path in Item 11, so the YAML and graph baselines are rendered from
the same graph and can never disagree. The script docstrings are the source of
truth for this split.

### Requirements & verification matrix (v5)

REQ-SNAP-01..07 (round-trip / typed-fields / AST-None) are the prior family; this
item adds REQ-SNAP-08+. Every row below is verified against the **v5** machinery. The v6
envelope's own matrix lives in `tests/conformance/test_snapshot_v6_{envelope,capture,routes}.py`
and `tests/conformance/test_source_admission_routes.py`.

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

Snapshot generation has a coordinated agentic-mbse boundary, and it applies to **both** formats:
the v6 envelope anchors the companion's version and the executable-profile marker as
environment facts, and v5 re-lowering consumes the companion's serialized schemas directly.
Snapshot re-lowering consumes the
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
