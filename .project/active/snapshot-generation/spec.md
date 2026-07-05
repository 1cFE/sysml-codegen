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

- [ ] `generate --from-snapshot <solar_battery snapshot>` produces output that is
      **byte-identical** to live `generate --models <solar_battery>` — verified by
      generating both into separate directories and diffing the trees recursively
      (empty diff). (Relies on Item 1's deterministic entry-point-group sort in
      `graph_builder`, which makes the `ComputationGraph` order-stable; spec
      against Item 1 landing first.)
- [ ] A snapshot of an **expression-bearing** model preserves CalcUsage
      auto-implementation: generated stencils are auto-implemented (not
      `NotImplementedError`), and `compilability` is set (not `UNKNOWN`) — matching
      what live generation of the same model produces.
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
  `src/sysml_codegen/snapshot/`. The move must not introduce a syside runtime
  import into the `src` package (the whole point is a syside-free path). The
  hard-coded `FIXTURES_DIR` in the loader (`snapshot_loader.py:39`) becomes a
  parameter — the loader must load from an arbitrary snapshot path, not a
  fixtures-relative model name.
- **[HARD]** `build_pipeline_context_from_snapshot()` lives in `orchestration/`
  and returns a `PipelineContext` equivalent to `build_pipeline_context()`, minus
  the live extractor. It reuses the proven conformance-helper body
  (`build_full_graph_from_snapshot` and its `build_classifier_inputs_from_snapshot`
  precursor), not a reimplementation.

### CLI surface

- **[HARD]** `--from-snapshot <path>` on `generate` is mutually exclusive with
  `--models`; supplying both is a usage error.
- **[HARD]** `--design-path-filter` combined with `--from-snapshot` is rejected —
  the filter is applied at capture time and baked into the snapshot, so applying
  it again at generation is meaningless and must not silently no-op.
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
  version that does not match the tool's current version is a **hard error** with a
  message naming the fix (recapture with current tooling). (V1–V6 diagnostic
  pattern.)
- **[NEED]** A snapshot whose recorded source hash no longer matches the current
  source produces a **freshness warning** and continues. The hashes
  (`source_hash` / `source_file` / `captured_at`) already exist on the extracted
  data; this check reads them.
- **[NEED]** A snapshot run emits a provenance banner identifying the snapshot,
  its capture time, and its source — so a reader of the console/log always knows
  the output did not come from live extraction.
- **[HARD]** The provenance banner and any freshness/version diagnostics go to the
  log/console only. **No generated artifact may embed capture-time or run-time
  provenance** (banner text, `captured_at`, a "generated at" timestamp). This is a
  precondition of the byte-identical criterion — live and snapshot runs must
  produce identical files. (Verify current generation already embeds no such
  timestamp; if it does, that is in scope to remove or normalize.)

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
  snapshots degrade with a warning" behavior from the research; see the version
  policy in Open Questions for how it interacts with the hard version check.

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

## Open Questions / Deferred to design

- **Version-mismatch vs legacy-degrade policy (the crux — confirm the split).**
  Two requirements sit close together: a version mismatch is a *hard error*, but an
  old snapshot without `compilation_results` should *degrade with a warning*. The
  coherent reconciliation, proposed here as [INFERRED] for the reviewer to confirm:
  a snapshot whose `snapshot_format_version` is **present but different** from the
  current version is a hard error (structural incompatibility we can't reason
  about); a snapshot **missing `compilation_results`** (an additive section)
  degrades with a warning. The genuinely undecided sub-case is a snapshot with
  **no version field at all** (every currently-committed one, pre-regen) — treat
  missing-version as legacy/degrade, or as a hard error demanding recapture? Since
  all 10 committed snapshots are regenerated by this item and the capture command
  doesn't exist yet, there are effectively no un-versioned snapshots in the wild;
  the safe default is to treat missing-version as a hard error ("recapture with
  current tooling"). Confirm at design / spec-review.
- **Source-freshness strictness.** Warn-and-continue by default is specified. Whether
  to add a `--strict` flag that promotes the freshness warning to a hard failure
  (useful in CI to catch stale snapshots) is a mechanism choice — defer to design.
- **Capture output path / naming convention.** Where the `snapshot` subcommand
  writes by default, and whether it targets a single file or a per-model directory
  layout, is a mechanism choice — defer to design.
- **Which expression-bearing fixture proves SC-10.** The auto-impl-preservation
  criterion needs a fixture whose CalcUsage carries an inline output expression
  (solar_battery has none, which is why it is already byte-identical). Candidate
  from the committed corpus is `attr_expr_probe` or `chain_spike_model` — confirm at
  design which committed snapshot actually exercises the CalcUsage `compilation_results`
  path, or whether a minimal expression-bearing fixture must be added.
- **Version field format.** Integer vs semantic string for `snapshot_format_version`,
  and where it sits in the JSON (top-level alongside `model_name`/`captured_at`) —
  mechanism, defer to design.

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
  - `tests/conformance/test_entry_point_classifier.py:136` — `build_full_graph_from_snapshot()` (the proven context-builder body)
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
