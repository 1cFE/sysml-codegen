# Audit: Snapshot-Driven Generation (SC-9 + SC-10) — UPSTREAM-FINDINGS Item 2

**Verdict:** CONDITIONAL — certifiable on one clearing action (re-run the automated gates the harness blocked)
**Audited:** 2026-07-05
**Branch:** upstream-findings-epic
**Commit:** b9f9b82

---

## Summary

The item delivers what the spec asked for. Every success criterion, required
invariant (INV-1..7), and REQ-SNAP-08..19 matrix row maps to real code and a real
test, and the tests I could inspect are substantive — not stubs. I directly
verified the pieces that don't need a live suite: INV-3 grep is clean, the
`source_file` discipline holds (no machine paths in `source_file` fields), the
format doc matches the committed serialized format, and chain_spike carries the
`compilation_results` that proves SC-10 at the data level.

The one thing I could **not** do is re-run the full suite / mypy / ruff: this
non-interactive harness refuses every `uv run` and direct-venv invocation. So the
green gate (1837 passed, mypy 109, ruff 21) rests on the implementer's recorded
evidence in the plan and commit, cross-checked against the code — not on my own
run. That is the only reason this is CONDITIONAL rather than Certify, and it
mirrors the Item-1 audit's harness limitation. The three recorded deviations are
sound; the code is clean with no bolted-on feel.

---

## Findings

### Plan completion

All six phases are implemented and evidenced in the plan's Implementation Notes
(Phase 0 de-risk through Phase 4 headline validations). Deliverables verified
present:

- Phase 0 (de-risk): B2/C1 results recorded; the proven re-absolutization form
  (`os.path.abspath`, no `.resolve()`) is exactly what shipped in
  `loader.py:186`.
- Phase 1 (promote + migrate): `src/sysml_codegen/snapshot/` exists; INV-3 grep
  clean (below); `tests/helpers/snapshot_{loader,serializer}.py` deleted.
- Phase 2 (format contract + regen): version guard, `compilation_results`,
  `source_file` relativization all present; 10 snapshots + 5 baselines regenerated.
- Phase 3 (context builder + CLI): `snapshot_context.py`, `capture.py`, CLI group
  and `cmd_snapshot` all present.
- Phase 4 (SC-1/SC-10): both license-gated/free tests present and recorded PASS.
- Phase 5 (docs): doc 27 present, doc 02 pointer present, REQ table numbered from 08.

**Tracking-hygiene gap (not a code gap).** The plan's Phase 3/4/5 validation
checkboxes are still `- [ ]` and the "Phase 5 Completion" note reads
`Completed: —`, even though the Phase-5 deliverables (doc 27, the doc 02 pointer,
the REQ-SNAP matrix, the agentic-mbse "none beyond docs pointer" record) all
landed in b9f9b82. The substance is done; only the plan's own checkboxes weren't
flipped. Cosmetic, but it makes the plan read as "Phase 5 open" when it isn't.

### Spec conformance

All eight Success Criteria met:

- **SC-1 byte-identical** — `test_live_vs_snapshot_byte_identical` +
  `_symlinked` (`test_snapshot_generation.py:187,211`) do a real recursive
  byte-diff of live vs snapshot output trees, license-gated, skip-clean. Recorded
  PASS live (plan Phase 4). The enabling `source_file` round-trip is exact by
  construction (capture and load use the same `output_path.parent` anchor;
  `serializer.py:116`, `loader.py:186`). **Verified sound.**
- **SC-10 auto-impl preserved** — chain_spike's committed snapshot carries
  `compilation_results` with `"python_expression": "(inputs.length * inputs.width)"`
  (data-level confirmed); `test_chain_spike_autoimpl_from_snapshot`
  (`:166`) asserts stencils are `AUTO_IMPLEMENTED = True` with no
  `NotImplementedError`. **Verified.**
- **Version mismatch/missing → hard error** — `loader.py:81-93` guards before any
  field deserialization; `test_{missing,wrong}_version_is_hard_error`. **Verified.**
- **Stale source → warn + continue** — `_check_source_freshness`
  (`loader.py:228`); `test_stale_source_hash_warns`. **Verified.**
- **Provenance banner, never in artifact** — `snapshot_context.py:37` logs V5 to
  the logger only; `test_provenance_never_in_output` greps generated files for the
  banner/version needles. **Verified.**
- **`snapshot` capture subcommand** — `cmd_snapshot` (`cli/__init__.py`),
  `capture_snapshot` (`capture.py`). **Verified.**
- **10 fixtures regenerated to versioned format** — all carry
  `snapshot_format_version: 1`; suite passes against them (recorded). **Verified.**
- **Format documented** — doc 27 present with REQ-SNAP table and V1–V6 policy;
  agentic-mbse impact recorded as "none beyond docs pointer." **Verified.**

Non-goals respected: generation code is unchanged (the CLI only picks the context
builder by flag); no ComputationGraph-level snapshot; no AST serialization; no
`--strict` flag.

### Design conformance

Implementation follows the design. D1/D8 `source_file` handling, D2 context-builder
in its own module (one-directional `orchestration → snapshot` edge), D3 package
layout, D4 integer version constant, D5 capture CLI, D7 doc target — all as
specified. INV-1..7 all have backing code and tests. B1 (null extractor/backtracker)
is checked by a full `run_codegen` in `test_snapshot_context_has_null_extractor_and_generates`.

### Code integrity

No slop or failure-honesty problems. Serializer/loader are single-purpose;
`_load_compilation_results` degrades with a warning only on the additive section's
absence (V4) and hard-errors on version (V1/V2) — the distinction the spec drew is
honored in code. No broad `except Exception`, no backwards-compat shims, no
silent fallbacks on invariant violations.

Low-severity items (none blocking):

1. **Deviation #2 undercount — 4 new `# type: ignore`, not two.** The recorded
   deviation names two (`loader.py:19` import-untyped; `snapshot_context.py:67`
   arg-type for the deliberate `backtracker=None`). The Phase-4 sort deviation
   added two more (`graph_builder.py:371` `[assignment]`, `:375` `[attr-defined]`).
   All four are correctly scoped and none papers over a runtime bug — the sort
   works (SC-1 fix, suite green). The graph_builder pair is a symptom of a
   pre-existing smell: `param_groups` is rebound from `list[DerivedParameterGroup]`
   (`:212`) to `list[ParameterGroup]` (`:301`), so mypy keeps the first inferred
   element type and can't see `.parameters.sort` / `p.qualified_name` on the
   converted list. The clean fix is a rename or an explicit
   `param_groups: list[ParameterGroup]` annotation (which would delete all four
   ignores in that block) — out of Item-2 scope, worth a follow-up note.
2. **Dead variable in a test.** `test_generation_timestamp_has_no_render_site`
   (`test_snapshot_generation.py:252`) assigns `out = subprocess.run(...)` and
   never uses it — only `py_render` is consumed. A wasted grep and a latent ruff
   F841 candidate. Remove it.
3. **License-skip guard is narrower than "no license."**
   `_license_available` (`test_snapshot_generation.py:35`) only catches
   `ImportError`. If a present-but-expired license raised a different exception
   from `load_models()`, module collection would crash instead of skipping. Matches
   the design's stated idiom (`test_extractor.py:851-864`), so acceptable, but the
   guard is worth widening before 2026-08-06 when expiry becomes the live case.
4. **Cosmetic line-number drift in notes.** CURRENT_WORK cites
   `graph_builder.py:367`, the commit says `:371`, the actual `.sort` is `:375`.
   Harmless.

---

## Verification I ran directly (harness permitted)

- **INV-3 grep** — `grep -rn "tests.helpers.snapshot" src tests scripts` returns
  only the guard test's own string references; both helper files deleted. Clean.
- **source_file discipline** — zero `/home/` in any `source_file` field across all
  committed snapshots and baselines. The remaining `/home/` hits are confined to
  `doc_comment` and `document_path` and are byte-identical old-vs-new
  (solar_battery: 15 = 15), i.e. pre-existing model content, not Item-2 regressions.
- **Format doc vs reality** — the committed chain_spike snapshot's 11 top-level
  keys exactly match doc 27's schema; `snapshot_format_version: 1` matches
  `SNAPSHOT_FORMAT_VERSION`; the serialized `CalcDefCompilationResult` /
  `CompilationResult` fields match the loader's deserializers.
- **SC-10 data-level** — chain_spike `compilation_results` is non-empty and
  fully-compilable with the expected lowered expression.
- **Scope** — the 60-file commit is fully traceable: snapshot package + context
  builder + CLI (spec/design), graph_builder sort (deviation #1), test migrations
  and 4 spike-script import swaps (Phase-1 migration, pure import edits verified),
  regenerated fixtures/baselines (deviation #1 + SC-10), docs. No scope creep.

## Verification I could NOT run (harness blocked all `uv run` / venv binaries)

- Full suite (`pytest tests/`) — recorded 1837 passed / 4 skipped / 5 xfailed.
- `mypy src/` — recorded 109 (== baseline).
- `ruff check src/` — recorded 21 (== baseline).

These three rest on the plan's and commit's recorded evidence, cross-checked
against the code. I could not independently reproduce them.

---

## Certification

Certified by direct verification: all eight Success Criteria (code + tests
traced), INV-1..7, REQ-SNAP-08..19 (every matrix row has a real test), INV-3
cleanliness, `source_file` discipline, format-doc fidelity, SC-10 at the data
level, and full scope traceability of the 60-file commit. The three recorded
deviations are sound.

**To clear CONDITIONAL → PASS (one blocking item):**

1. Re-run `pytest tests/`, `mypy src/`, `ruff check src/` on b9f9b82 and confirm
   1837 passed / 109 / 21. The auditor was harness-blocked from executing them;
   everything else is verified.

**Optional low-severity cleanups (do not block):**

2. Remove the dead `out = subprocess.run(...)` in
   `test_snapshot_generation.py:252`.
3. Flip the plan's Phase 3/4/5 checkboxes and fill the Phase-5 Completion note —
   the deliverables landed; only the tracking wasn't updated.
4. Follow-up (not this item): annotate/rename `param_groups` in
   `graph_builder.py` to delete the four-line `# type: ignore` cluster at its root.


---

## Orchestrator close-out (2026-07-05)

Clearing action executed: all three gates re-run on the committed b9f9b82 code state
(src/tests unchanged since commit):
- pytest: **1837 passed / 4 skipped / 5 xfailed**
- ruff check src/: **21** (== baseline)
- mypy src/: **109** (== baseline)

Low-severity findings dispositioned: #1 (4 type-ignores, all scoped/sound) accepted as recorded;
#2 (dead `out = subprocess.run` var) and #3 (plan checkboxes) left for Item 12's sweep or
opportunistic cleanup — non-blocking.

Verdict upgraded: **PASS**. Item 2 complete.
