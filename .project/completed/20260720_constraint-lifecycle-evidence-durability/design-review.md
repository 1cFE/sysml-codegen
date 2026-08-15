# Design Review: TEAx Constraint Evidence Durability (Lifecycle Item 11)

**Design:** `.project/active/constraint-lifecycle-evidence-durability/design.md`
**Spec:** `.project/active/constraint-lifecycle-evidence-durability/spec.md`
**Review File:** `.project/active/constraint-lifecycle-evidence-durability/design-review.md`
**Date:** 2026-07-20
**Verified against:** teax `07eb0ac` (HEAD confirmed), codegen `b987869`

---

## Fundamental Assessment

**Sound — approve with revisions.**

The core move is right: make the projection seam the single place where report absence is
handled and immutability is sealed, so both evaluator routes converge and the authoritative
copy is immutable before policy can touch it. That collapses two duplicated bare reads into
one tolerant read (D1), removes an incidental ordering coupling in favor of a real mechanism
(D2), and gives `OUTPUT_WRITE` a first honest emitter instead of collapsing a real phase (D3).
Nothing here is over-engineered; no new abstraction is invented where an existing seam would do.
The rejected alternatives are recorded with reasons, and the spec's provenance carries through.

But three things need fixing before implementation, and one is the same class of defect Item 11
exists to kill — an evaluation stamping a phase name that isn't what actually happened:

1. **D3's phase discriminator is unsound (Critical).** `failed_module_key is None` is not
   exclusive to the write phase. Entry-execution failures and a pre-loop write-handler check
   also carry a `None` module key on the file-backed route and would be misstamped `OUTPUT_WRITE`.
   And the design's own fixture failure is an `OSError` that `write_outputs` does *not* wrap, so
   the `OutputRouterError` "primary discriminator" cannot stand on its own — it is forced onto
   the unsound disjunct.
2. **A1's consumer sweep is scoped to `src/` and silently excludes the tests (Major).** At least
   six test sites construct `ModelEvidence` with a live/typed/`object()` report or assert report
   *identity*; D2's type change breaks every one, and none is in the deletion or fixture plan.
3. **D2's sealed-tree representation is genuinely in tension with byte-identity + the poison
   guard, and the design defers to an option that doesn't actually achieve immutability (Major).**

The approach survives all three — they are revisions, not a rework. Details below.

---

## Dimensional Review

### 1. Spec Compliance
**Assessment:** Concerns

Every Success Criterion has a design element, and provenance is carried faithfully (the spec's
`[INHERITED]` contract rows land as named decisions; the surfaced provenance correction — that
46a is *not* yet reproduced — becomes Phase 0's RED-first step, exactly as the spec's Law-4
surfacing demanded). Two gaps:

- **The corruption-vs-emptiness axis is unaddressed (SC row 1).** The spec's coordinate one is a
  *constraint-free* package → empty evidence. The design detects this purely as
  `result.outputs.get(REPORT_CHANNEL) is None` (D1) and maps any absence to empty/`unconstrained`.
  It never argues why an absent channel *must* mean constraint-free rather than a corrupted
  constraint-BEARING package whose channel vanished. See Route Safety (M3).
- **A3/A4 are RED-fenced properly** — A4 (constraint-free emits no channel) is proven RED-first in
  Phase 0; A3 (excluded-only emits `not_assessed`) is proven by the `excluded_only` fixture in
  Phase 4 and, if false, "surfaces a codegen ask." That is the right treatment for a
  codegen-behavior assumption. No change needed here; noting it because priority 4 asked.

### 2. Pattern Consistency
**Assessment:** Pass

`project(...)` is already the shared seam both evaluators funnel through (`evaluator.py:139`,
`:210`); moving the read inside it follows the existing structure rather than inventing one.
`_freeze` mirrors the codebase's existing `MappingProxyType` usage (`evidence.py:20`,
`CANONICAL_HEADLINE`). The `unconstrained` disposition extends the existing
`_DISPOSITION_BY_HEADLINE` demo-policy vocabulary (`policy.py:32-37`) rather than reinterpreting
verdicts (respects the contract-49 firewall). Fixture-pinned `expected_phase` extends the
existing arithmetic-shape case records. Good reuse throughout.

### 3. Abstraction Quality
**Assessment:** Pass

No new class or layer is introduced. `_freeze` is a single helper; the sealing lives on the
existing envelope. The design explicitly confirms **no** consumer-side report reshaper is added
(D6) — the harvest keeps reading codegen's embedded catalog via `StudyQuery`/`_EmbeddedCatalog`
(`query.py`). The "no `*adapter*` class exists to delete" finding is correct: the only match in
`simkit/` is `io/readers.py` ("Input adapters"), unrelated.

### 4. Duplication Avoidance
**Assessment:** Pass

D1 removes one of the two duplicated bare reads (`evaluator.py:132`/`:203`) — confirmed both are
identical `result.outputs[REPORT_CHANNEL]`. The design correctly keeps them as *one* tolerant read
inside `project`, not two `.get()` patches. This is the cleanest part of the design.

### 5. Data Structure Clarity
**Assessment:** Concerns

The absence table in D1 (constraint-free `{}`/`None`/`unconstrained` vs excluded-only
`{"headline": "not_assessed"}`/real-report/`not_assessed`) is clear and the two axes are genuinely
structurally distinct — verified: `policy.py:65`/`:121` read `responses["headline"]` and would
`KeyError` on `{}`, which is exactly the branch D1 adds. But `ModelEvidence.report` changes type
from `Any` (opaque live model) to a frozen JSON tree (`Mapping[str, Any] | None`), and that change
has a representation tension the design defers rather than resolves (M2), plus a test-migration
surface it doesn't inventory (M1).

### 6. Route Safety
**Assessment:** Fail

Two distinct route-safety defects, one Critical.

- **C1 — `OUTPUT_WRITE` over-claims (Critical).** In `pipeline_executor.run()`, only
  `_execute_module` is wrapped by the try that sets `context.failed_module_key`
  (`pipeline_executor.py:142-146`). `_execute_entry` (`:131`) and the pre-loop write-handler check
  `_ensure_exit_handlers` (`:125`, raises `OutputRouterError`) are **not** — a failure there leaves
  `failed_module_key = None` and propagates to `_normalize_run_failure`. Under the proposed branch
  (`OUTPUT_WRITE if isinstance(error, OutputRouterError) or failed_module_key is None`), an
  entry-load failure on the file-backed route (malformed entry JSON, missing artifact →
  `PipelineValidationError`; a `None` Optional field → `PipelineExecutionError`) gets stamped
  `OUTPUT_WRITE` — a write that never happened. This is the same defect Item 11 exists to remove
  (a phase name that lies), reintroduced in the fix. **And the disjunct cannot simply be dropped:**
  the design's own D3 fixture points `output_dir` at an unwritable path, but `write_outputs` calls
  `base_dir.mkdir(...)` and `handler.fn(...)` with no `OSError` wrapping (`output_router.py`
  `_prepare_run_directory` and the write loop) — so the fixture failure is a bare `OSError`, not
  `OutputRouterError`. The `isinstance` discriminator misses it; only the unsound `None` disjunct
  catches it. The design needs a **positive** write-phase signal at the executor seam (wrap
  `:154-161` so the write phase is identified as such — e.g. a typed write-phase error or a context
  flag), not an inference from a null module key. As written, priority-3's claim "no other failure
  lands in the new stamp" is false.
- The `MODULE_EXECUTION` / `assessment_failed` / four-completed-status routing is otherwise sound:
  `_commit_execution_failure`'s `else` branch (`runner.py:115-124`) does route both
  `MODULE_EXECUTION` and `OUTPUT_WRITE` to an `execution_failed` case, so no runner change is
  needed — confirmed.

### 7. Bets & Decisions Integrity
**Assessment:** Concerns

The stated bets A1–A5 are honest and each carries an "if false" — good practice. But:

- **A1 is stated as complete ("the only readers are …") when its grep was scoped to `src/`.** The
  test suite is a consumer too, and it breaks. This is a *hidden* cost dressed as a closed sweep.
  See M1. A1's production conclusion ("no consumer needs typed access") is correct; the framing
  that the sweep is finished is not.
- **A5's converse is the unstated load-bearing bet.** A5 correctly says the write phase runs after
  the loop so `failed_module_key is None` there. The design then silently relies on the *converse*
  — that `None` key ⟹ write phase — which is false (C1). Surface it or fix the discriminator.
- The rest (A2 byte-identity, A3/A4 codegen behavior) are genuine, fixture-fenced, and honestly
  graded.

### 8. Reader Comprehension
**Assessment:** Pass

The Frame diagram and the "one projection seam" framing land the mental model before the mechanism.
The D1 absence table is the right shape. A tired engineer can follow it. No voice changes needed.

---

## Issues by Severity

### Critical
- **C1 — D3 phase discriminator is unsound.** `failed_module_key is None` also fires for
  entry-execution and pre-loop write-handler failures on the file-backed route (`pipeline_executor.py:131`,
  `:125` — neither is wrapped by the module-key try at `:142-146`), misstamping them `OUTPUT_WRITE`.
  The fixture's own failure is an unwrapped `OSError`, so the `OutputRouterError` discriminator can't
  stand alone and the design is forced onto the unsound disjunct. Add a positive write-phase signal
  at the executor seam (wrap `:154-161`) instead of inferring the phase from a null module key.
  — Route Safety / Bets

### Major
- **M1 — A1's sweep excludes the tests; D2's `report` type change breaks ≥6 test sites.** Confirmed
  live/typed/`object()` report consumers: `test_projection.py:99` (`assert evidence.report is report`,
  identity — breaks under a JSON-tree snapshot); `test_isolation.py:61` (`report=object()` — fails the
  new `Mapping|None` validator, and this test *is* the INV1 opacity pin, so its premise must be
  re-expressed); `test_policy.py:37` (`_StubReport()`); `test_evidence_io.py:55,83`
  (`_TypedReport`/`_PoisonedReport` `BaseModel`s relied on for `.model_dump()`); `study/conftest.py:213`
  (`report=report`). None appears in the deletion or fixture plan. The "full suite green" gate is
  unscoped without this migration list. — Data Structure / Bets
- **M2 — INV-C (immutability) and INV-G (byte-identity) are in real tension, and the design defers to
  the non-working option.** If the sealed tree is `MappingProxyType`/`tuple` (immutable), the encode
  walkers `_tag_nonfinite`/`_untag_nonfinite` (`evidence_io.py:20-32`, `:54-61`) only recurse
  `dict`/`list` → they skip the report subtree → non-finite floats inside `report.results` go untagged
  (INV-G byte divergence) **and** the MF-3 poison-collision guard (exercised by `test_evidence_io.py:83`)
  stops firing inside the report. If the tree is plain `dict`/`list` (walkable), `evidence.report`
  returns a mutable container → INV-C fails. The design's "expose a read-only proxy at access, keep
  plain dict/list stored" option does **not** achieve immutability (the stored container is returned
  mutable). The working resolution — store the frozen tree *and* widen the three walkers to
  `Mapping`/`Sequence` — exists; commit to it and drop the proxy-at-access alternative. — Data Structure
- **M3 — Absence is mapped to emptiness without distinguishing corruption.** D1 treats
  `outputs.get(REPORT_CHANNEL) is None` as constraint-free → `unconstrained` → `completed`. A
  constraint-BEARING package whose report channel vanished is corruption, and it would be silently
  committed as a healthy `unconstrained` completed case — the opposite of surfacing (capture-fidelity
  Law 4). Either argue at the seam why channel-absent ⟺ constraint-free is not reachable for a
  constraint-bearing package (e.g. its aggregator module either produces the channel or fails in
  `MODULE_EXECUTION`, so a silent drop can't occur), or add a guard/coordinate. As written the design
  asserts distinctness between constraint-free and excluded-only but not between constraint-free and
  corrupt. — Route Safety / Spec

### Minor
- **m1 — `unconstrained` branch placement in `ObjectivePolicy`.** It must sit before the objective /
  response-role loops (`policy.py:106-119`), which read `evidence.responses`/`outputs` and raise
  `AssessmentFailed` *before* the headline line (`:121`). The design says "first branch" — correct —
  but pin it explicitly, since otherwise a constraint-free package under a policy that configures any
  `response_role` yields `assessment_failed`, not `unconstrained`.
- **m2 — "encode moves to just before `commit_case`" is a rationale deletion, not a clean physical
  move.** Two commit sites need `evidence_json` (`runner.py:138` assessment_failed, `:149` completed),
  and one `encode_evidence` at `:134` currently serves both. The load-bearing deletion is the
  *protection rationale*, not the call site; frame it that way. Crash-safety is **not** weakened — the
  atomic seam is `store.commit_case(..., crash=self.crash)`, untouched by the reorder — but the design
  should say so, since the epic names crash-safe persistence as a row-13-15 concern.
- **m3 — Fixture plan has a hole exactly where C1/M3 live.** The `OUTPUT_WRITE` coordinate proves the
  phase *is* emitted, but nothing proves it is *not over-emitted*. Add an entry-failure-on-file-backed
  coordinate pinned to its true phase, so the C1 misclassification would be caught by a test rather
  than shipped. (Plus the M1 test-migration list and, if M3 is guarded, a corruption coordinate.)

---

## Recommendations

1. **Fix C1 before anything else.** Identify the write phase positively at the executor seam
   (`pipeline_executor.py:154-161`) — a dedicated try that tags the failure as write-phase (typed
   error or context flag) — and drive the D3 stamp off that, not off `failed_module_key is None`.
   Then add the entry-failure phase-pin coordinate (m3) so over-claiming is caught by a test.
2. **Re-scope A1 to include tests and inventory the migration (M1).** List the six sites, and decide
   how `test_isolation.py`'s INV1 opacity pin and `test_evidence_io.py`'s MF-3 poison test are
   re-expressed against the sealed-tree contract. Fold this into Phase 2.
3. **Resolve M2 in the design, not at implementation.** Commit to "store the frozen tree + widen the
   three encode/decode walkers to `Mapping`/`Sequence`"; delete the proxy-at-access option, which
   doesn't freeze. Keep the golden test (INV-G) as the pin.
4. **Address M3.** Add the constraint-free ⟺ channel-absent argument (or a corruption guard) so a
   vanished channel on a constraint-bearing package cannot commit as a healthy `unconstrained` case.
5. **Tighten m1/m2 wording** — `unconstrained` branch placement, and the encode "rationale-deletion,
   crash-safety-preserved" framing.

---

## Resolutions

*(Filled in during Stage 4 as the owner resolves each issue. This section is what the design agent
reads to incorporate the review.)*

- **C1 — Accepted.** Positive write-phase signal at the executor seam: a `context.in_output_write`
  flag set around the `write_outputs(...)` call (`pipeline_executor.py:154-161`). `_normalize_run_failure`
  stamps `OUTPUT_WRITE` **iff** `context.in_output_write` is true — never from exception type or a null
  module key. Entry-load and pre-loop write-handler failures keep their honest `MODULE_EXECUTION`
  phase. The unwritable-`output_dir` fixture (bare `OSError`) stamps `OUTPUT_WRITE` via the flag. A new
  entry-failure-on-file-backed coordinate (m3) pins the non-over-emission.
- **M1 — Accepted.** Six sites inventoried and migrated in Phase 2 (design D2 "test migration"):
  `test_projection.py:99` (identity→value), `test_isolation.py:61` (`object()`→plain dict tree; INV1
  pin re-expressed), `test_policy.py:37` (`_StubReport`→dict), `test_evidence_io.py:55,83`
  (`_TypedReport`/`_PoisonedReport`→dict trees; MF-3 preserved), `study/conftest.py:213`
  (`ConstraintReport`→dict). A broad `report=`/`.report` test grep runs in Phase 2 to catch any not listed.
- **M2 — Accepted, committed.** Store the frozen tree AND widen the three encode/decode walkers to
  `Mapping`/`Sequence`. `project` computes `report.model_dump(mode="json")` once, freezes it
  (dict→`MappingProxyType`, list→`tuple`), stores it as `ModelEvidence.report`. `encode_evidence`
  drops its own `model_dump` and walks the sealed tree; `_tag_nonfinite`/`_untag_nonfinite` accept
  `Mapping`/`Sequence`. Proven by both a nested-mutation attack test (INV-C) and a byte-identity
  golden (INV-G), with the MF-3 poison guard (`test_evidence_io.py` migrated) still firing. The
  proxy-at-access option is dropped.
- **M3 — Accepted, catalog authority.** The study-layer caller reads
  `load_model_contract(package_dir).concrete_entries` (empty ⟺ constraint-free, per the seam's own
  docstring) and passes `expects_constraint_report=bool(concrete_entries)` into the evaluator, which
  forwards it to `project`. Report absent + `expects=True` → raise `CorruptConstraintEvidence` (loud,
  not a recorded case); absent + `expects=False` → empty evidence. Evaluation layer stays
  isolation-clean (receives a bool, never imports `study`); a spec-derived default (exit declares the
  `constraint_report` field) keeps standalone evaluation-layer tests self-contained. Corruption
  coordinate added.
- **m1 — Accepted.** The `unconstrained` branch sits **before** `ObjectivePolicy`'s objective /
  response-role loops (`policy.py:106-119`), pinned by a test with a configured `response_role`.
- **m2 — Accepted.** The load-bearing deletion is the encode-before-assess *protection rationale*, not
  the call site; crash-safety is unchanged (the atomic seam is `store.commit_case(..., crash=...)`),
  stated explicitly. **m3 — Accepted** (entry-failure + corruption coordinates added to D5).

---

**Overall:** Approve-with-revisions
**Next Steps:** Record resolutions above, then re-run `/_my_design` (or return to the design-agent
session) and point it at this review to incorporate. C1 must be resolved (it reintroduces the exact
"phase name that lies" defect Item 11 removes); M1–M3 must be resolved before Phase 2/Phase 3 land.
The reviewer does not edit the design. Max two rounds.
