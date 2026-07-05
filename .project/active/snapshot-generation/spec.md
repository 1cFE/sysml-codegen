# Spec: Snapshot-Driven Generation (SC-9 + SC-10)

**Status:** Draft
**Owner:** Reid W
**Created:** 2026-07-05
**Complexity:** HIGH
**Branch:** upstream-findings-epic
**Epic:** UPSTREAM-FINDINGS, Item 2

---

## Problem

Generation requires a live syside license to run. Every `generate` call first
parses SysML through `SysMLDataExtractor` (the JVM/SysIDE bridge) to produce a
`PipelineContext`. That license is single-seat, machine-locked, and **expires
2026-08-06 with no grace period**. After that date, nobody can generate,
regenerate a baseline, debug a generation bug, or run generation in CI —
because all of it is gated on extraction.

The pieces to decouple generation from the license already exist, but only
inside the test tree, unsupported:

- `tests/helpers/snapshot_serializer.py` / `snapshot_loader.py` round-trip a
  full extraction result to/from JSON, nullifying the live syside AST fields.
- The conformance suite already rebuilds a `ComputationGraph` from those
  snapshots — the `build_full_graph_from_snapshot()` helper
  (`tests/conformance/test_entry_point_classifier.py:136`) is exercised by
  900+ tests. Generation already consumes only `ComputationGraph`
  (REQ-ORCH-06), so a snapshot-fed context is a drop-in.
- `scripts/capture_extraction_snapshots.py` (`_capture_full_pipeline`) captures
  the 10 committed fixture snapshots — but it's a dev script, not a supported
  command, and users have no supported way to produce a snapshot.

Two gaps make the existing snapshots unfit as a generation contract:

1. **No format versioning or provenance guard.** The snapshot is a serialized
   view of freshly-refactored dataclasses. If those change, an old snapshot
   deserializes into subtly wrong data with no signal. There is no version
   field, no source-freshness check, and no indication at runtime that a run
   used a snapshot rather than live extraction.

2. **CalcUsage auto-implementation is silently lost (SC-10).** `compilation_results`
   — the lowered Python expression strings that let a CalcUsage's stencil be
   auto-implemented — is rebuilt from live syside ASTs (`pipeline_builder.py`
   Step 6.5) that the snapshot nullifies. FORMULA and aggregation auto-impl
   already survive a snapshot (they carry pre-lowered strings); CalcUsage does
   not. On an expression-bearing model, a snapshot run produces well-formed
   output where stencils regress to `NotImplementedError` and `compilability`
   stays `UNKNOWN` — **silently**, because the output is otherwise valid.

This item promotes the proven snapshot machinery into a supported
`--from-snapshot` generation path plus a capture command, adds the versioning
and provenance the contract needs, and serializes `compilation_results` so
CalcUsage auto-impl survives. It is the mitigation for the license expiry, so
the capture command must be usable **now** to bank snapshots before 2026-08-06.

## Success Criteria

- [ ] `generate --from-snapshot <solar_battery snapshot>` is **byte-identical** to
      live `generate --models <solar_battery>`. This is a **claim to prove, not an
      established fact** — today's evidence is snapshot-vs-committed-baseline
      self-consistency only; no existing test compares live against snapshot. Verify
      with a **live-vs-snapshot full recursive tree diff** (empty diff), as a
      **license-gated** test that skips cleanly when no license is present, and run
      it **at least once during implementation while the license is live**.
      Snapshot-vs-snapshot self-consistency does not count. (Relies on Item 1's
      deterministic entry-point-group sort in `graph_builder`, and on the
      `source_file` normalization below — without it the embedded `SysML Source:`
      headers diverge and the diff fails.)
- [ ] A snapshot of `chain_spike_model` (the SC-10 proving fixture — verified
      expression-bearing: CalcUsages instantiating calc defs with inline output
      expressions) preserves CalcUsage auto-implementation: generated stencils are
      auto-implemented (not `NotImplementedError`) and `compilability` is set (not
      `UNKNOWN`), matching live generation. **No new license-gated fixture capture is
      needed for this item** — the proving fixture already exists in the committed
      corpus.
- [ ] A snapshot whose format version does not match the current version **fails
      loudly** with a clear, actionable error (recapture instruction), not a silent
      wrong deserialization.
- [ ] A snapshot whose recorded source hash no longer matches the on-disk source
      **warns** (stale-source), and the run continues.
- [ ] Every snapshot run prints a **provenance banner** (which snapshot, when
      captured, from what source) to the log/console — and this banner never
      appears inside any generated artifact.
- [ ] A `snapshot` capture subcommand produces a versioned snapshot from live
      models through the supported CLI (no dev script required).
- [ ] The 10 committed fixture snapshots are regenerated to the versioned format;
      the full conformance suite passes against them.
- [ ] The snapshot format is documented as a reference doc (new doc or an
      extension of doc 02), with REQ-* tags and verification-matrix rows.
- [ ] agentic-mbse impact recorded (expected: none, or a docs pointer).

## Known Requirements

### Boundary & structure

- **[HARD]** `ComputationGraph` remains the sole input to generation (REQ-ORCH-06 /
  REQ-PIPE-07). The snapshot feeds `build_pipeline_context_from_snapshot()`, which
  produces the same `PipelineContext` the live path produces; generation is not
  changed and does not learn about snapshots. (R1)
- **[HARD]** The snapshot loader/serializer move from `tests/helpers/` to
  `src/sysml_codegen/snapshot/`, and the conformance-helper graph-assembly body
  (`build_full_graph_from_snapshot` and its `build_classifier_inputs_from_snapshot`
  precursor, `test_entry_point_classifier.py`) is **promoted, not copied**. The move
  must not introduce a syside runtime import into the `src` package (the whole point
  is a syside-free path).
- **[HARD]** The hard-coded `FIXTURES_DIR` in the loader (`snapshot_loader.py:39`)
  becomes a parameter — the loader must load from an arbitrary snapshot path, not a
  fixtures-relative model name.
- **[HARD]** No two copies. All ~26 test files that import the promoted helpers
  migrate to the `src` module, and the `tests/helpers/` copies are **deleted in the
  same change**. No transitional re-export shim is left behind — a lingering second
  copy is exactly the drift the promotion exists to prevent.
- **[HARD]** `build_pipeline_context_from_snapshot()` lives in `orchestration/` and
  is **new assembly, not a rename**. The promoted helper returns a `ComputationGraph`
  + inputs dict and passes `compilation_results=None`; this function must build a
  full `PipelineContext` (`pipeline_context.py:78-104`, which also requires
  `backtracker`, `backtracking_result`, `channel_aliases`, `output_registry`, and
  `extractor`) and thread the deserialized `compilation_results` into
  `build_computation_graph(...)`. It is **built on** the helper's proven
  graph-rebuild body; size it as real assembly work, not a one-line reuse. The
  extraction-only fields (`extractor`, `backtracker`) are set to null-equivalents —
  safe only because no generation path dereferences them (the fusion-tea harness
  already runs generation with `extractor=None`). Verifying that no generation site
  reads `ctx.extractor` / `ctx.backtracker` is in scope.

### CLI surface

- **[HARD]** `generate` requires **exactly one** of `--models` / `--from-snapshot`
  — supplying both, or neither, is a hard CLI error. `--models` is currently
  `required=True` (`cli/__init__.py:513`); that changes. The clean mechanism is an
  argparse mutually-exclusive group marked required, which gives both-forbidden,
  neither-forbidden, and exactly-one-required in one construct.
- **[HARD]** `--design-path-filter` combined with `--from-snapshot` is a hard CLI
  error — the filter is applied at capture time and baked into the snapshot, so
  applying it again at generation is meaningless and must not silently no-op.
- **[HARD]** All other generation config (`--output`, `--package-name`,
  `--schema-class`, `--pipeline-name`, `--overwrite`, `--preserve-handwritten`,
  `--smart-regen`) applies unchanged on a snapshot run — the snapshot replaces only
  the extraction input, not the generation configuration.
- **[HARD]** A `snapshot` capture subcommand takes live models (and may accept
  `--design-path-filter`, recording it in the snapshot provenance) and writes a
  versioned snapshot. It lifts `_capture_full_pipeline` from
  `scripts/capture_extraction_snapshots.py` into the supported CLI.

### Format versioning & provenance

- **[HARD]** The snapshot carries a `snapshot_format_version` field. On load, a
  version that does not match the tool's current version — **including a missing
  version field** (a legacy/pre-versioning snapshot) — is a **hard error** with a
  message naming the fix (recapture with current tooling). (V1–V6 diagnostic
  pattern.)
- **[HARD]** The loader's hard error on unversioned/mismatched snapshots and the
  regeneration of all 10 committed fixture snapshots land **atomically in one
  change** — the suite is never red between them. All 10 committed snapshots are
  unversioned today, so a loader change that landed first would hard-error every
  snapshot-loading conformance test. **Item 1 coordination**: Item 1 is concurrently
  regenerating baselines/snapshots and — because the capture command does not exist
  yet — emits **unversioned** snapshots; sequence so Item 2's loader does not reject
  Item 1's fresh captures mid-epic.
- **[NEED]** A snapshot whose recorded source hash no longer matches the current
  source produces a **freshness warning** and continues. The hashes
  (`source_hash` / `source_file` / `captured_at`) already exist on the extracted
  data; this check reads them.
- **[NEED]** A snapshot run emits a provenance banner identifying the snapshot,
  its capture time, and its source — so a reader of the console/log always knows
  the output did not come from live extraction.
- **[HARD]** The byte-identity hazard is the embedded **source path**, not a
  timestamp. Generated modules, schemas, and stencils each emit a
  `SysML Source: {module.source_file}:{module.source_line}` header
  (`modules.py:78`, `schemas.py:43`, `stencils.py:66`), and `computation_graph.json`
  serializes `source_file` per module. Live extraction sets `source_file` from the
  parser's document path (`extractor.py:113`); the serializer bakes it **relative to
  the fixtures dir** at capture (`snapshot_serializer.py:102-108` — the committed
  solar_battery snapshot stores `solar_battery_model/design.sysml`). The two paths
  embed different strings unless normalized. Requirement: the snapshot must preserve
  or reproduce the **exact** `source_file` strings live generation would emit, with
  the normalization defined at **capture time** (what the serializer writes), not
  patched at emission time. Live and snapshot generation of the same model must then
  embed identical `SysML Source:` headers.
- **[HARD]** The provenance banner and freshness/version diagnostics go to the
  log/console only — never into a generated artifact.
- **[INFERRED]** The only generation-time timestamp (`generation_timestamp` in
  `templates/pydantic_schema.py.jinja2`) sits in a **dead template** — zero render
  sites across `src/` or `tests/`, so nothing reaches output today. It is a latent
  byte-identity trap: wired in, it would break live-vs-snapshot equality. Note it as
  such — remove it or leave it provably unwired; it is **not** the provenance the
  guard above polices.

### SC-10 — compilation_results

- **[HARD]** `compilation_results` (a `dict[str, CalcDefCompilationResult]`) is
  serialized into the snapshot and threaded through
  `build_pipeline_context_from_snapshot()` into `build_computation_graph(...,
  compilation_results=...)` and onto the returned `PipelineContext`. These are
  plain dataclasses of already-lowered Python expression strings
  (`CalcDefCompilationResult` → `CompilationResult`, `expression_compiler.py:132`);
  the generic serializer handles them with the existing `_AST_FIELDS` nullification.
- **[HARD]** syside AST fields are never serialized — they are live py4j bridge
  objects (that is what `_AST_FIELDS` and the `None`-on-load convention exist for).
  SC-10 serializes the *lowered strings*, not the ASTs.
- **[INFERRED]** A snapshot lacking a `compilation_results` section (a legacy
  snapshot captured before this item) **degrades to today's behavior** — CalcUsage
  auto-impl is lost — with a warning, rather than crashing. This is the "old
  snapshots degrade with a warning" behavior from the research, scoped to the
  `compilation_results` section only. It is kept distinct from version handling: a
  wrong/missing version is a hard error (see the resolved version policy in Open
  Questions), whereas a version-current snapshot missing this additive section
  degrades.

### Fixtures, tests, docs (R1/R2)

- **[HARD]** Conformance tests use real fixtures, never mocks. The byte-identical
  and auto-impl-preservation criteria are verified against real fixture models and
  their regenerated snapshots.
- **[HARD]** New/changed behavior carries REQ-* tags, verification-matrix rows, and
  a reference-doc update (new snapshot-format doc or an extension of doc 02).
- **[HARD]** The 10 committed fixture snapshots are regenerated to the versioned
  format via the capture path (not hand-edited). (R3 — reviewed diffs, capture
  scripts only.)
- **[NEED]** The spec/design ends with an explicit "agentic-mbse impact" section.

## Non-Goals

- **Snapshotting at the `ComputationGraph` level.** Rejected in research — it would
  freeze the resolution logic (backtracker, graph builder) behind a frozen graph,
  defeating the point of testing resolution changes. The snapshot is at the
  *extraction* boundary; resolution and generation still run live from it.
- **Any remote or licensing workaround** beyond the snapshot path (no license
  proxy, no vendored parser).
- **Serializing syside ASTs.** Impossible (live bridge objects) and explicitly out
  of scope — SC-10 serializes lowered strings only.
- **Changing what generation emits.** Byte-identical is the bar; this item must not
  alter generated output for the live path.
- **New fixtures for un-snapshotted shapes.** The 10 existing snapshots are the
  corpus for this item; return-style / retyping / plant fixtures belong to Items
  3/4/8.

**Resolved at spec-review** (recorded here so design inherits the ruling, not the debate):

- **Version-mismatch vs legacy-degrade policy — RESOLVED.** Spec-review confirmed
  the split coherent with the epic. Three cases, now settled and captured as HARD /
  INFERRED requirements above: a `snapshot_format_version` that is **present but
  different**, or **missing entirely**, is a **hard error** (recapture); a snapshot
  that is version-current but **missing the additive `compilation_results` section**
  **degrades with a warning** (CalcUsage auto-impl lost — today's behavior). The
  epic's "old snapshots degrade with a warning" is scoped to the `compilation_results`
  absence, kept distinct from version handling.
- **SC-10 proving fixture — RESOLVED: `chain_spike_model`.** Verified
  expression-bearing — its CalcUsages instantiate calc defs with inline output
  expressions (`chain_spike_model/library.sysml:8` `out area : Real = length * width`
  via `design.sysml:12` `calc area_calc : AreaCalc { ... }`), which is exactly the
  CalcUsage auto-impl path (not FORMULA, not aggregation). No new fixture and **no
  new license-gated capture** are required. Design confirms only that its regenerated
  snapshot produces a non-empty `compilation_results` once the serializer is extended.

**Still deferred to design (mechanism choices):**

- **Source-freshness strictness.** Warn-and-continue by default is specified. Whether
  to add a `--strict` flag that promotes the freshness warning to a hard failure
  (useful in CI to catch stale snapshots) is a mechanism choice — defer.
- **Capture output path / naming convention.** Where the `snapshot` subcommand
  writes by default, and whether it targets a single file or a per-model directory
  layout — mechanism, defer.
- **Version field format.** Integer vs semantic string for `snapshot_format_version`,
  and where it sits in the JSON (top-level alongside `model_name`/`captured_at`) —
  mechanism, defer.

---

## Related Artifacts

- **Epic:** `.project/backlog/epic_upstream_findings.md` — Item 2; Cross-Cutting R1/R2/R3
- **Required Reading:**
  - `.project/research/20260705_upstream-findings-deep-research.md` — SC-9 / SC-10 sections (authoritative over the register)
  - `~/1cfe/fusion-tea/.project/reports/2026-07-05-upstream-findings-register.md` — findings register (SC-9/SC-10 as "enhancement")
  - `docs/architecture/modeling-assumptions.md` — supported-subset contract
  - `docs/architecture/reference/02-orchestration.md` — the `build_pipeline_context()` 7-step sequence and REQ-ORCH-06 boundary
- **Code to promote:**
  - `tests/helpers/snapshot_loader.py`, `tests/helpers/snapshot_serializer.py`
  - `tests/conformance/test_entry_point_classifier.py:136` — `build_full_graph_from_snapshot()` / `build_classifier_inputs_from_snapshot()` (the proven graph-rebuild body to promote and wrap in a `PipelineContext`)
  - `scripts/capture_extraction_snapshots.py` — `_capture_full_pipeline()`
- **Design:** `.project/active/snapshot-generation/design.md` (to be created)

---

## agentic-mbse impact

Expected: **none**. This item adds a generation *input path* and does not change
what SysML models should look like or what the auditor should catch — the executable
subset is unchanged. The one plausible artifact is a **docs pointer**: if the new
snapshot-format reference doc is useful to agentic-mbse consumers (e.g., for CI that
runs generation from snapshots), note it in the close-out. Confirm "none vs docs
pointer" at design and record it explicitly per R2.

---

**Next Steps:** After approval, proceed to `/_my_spec_review`, then `/_my_design`.
